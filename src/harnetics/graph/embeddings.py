# [INPUT]: 依赖 chromadb、sentence-transformers、litellm 与 models.document.Section
# [OUTPUT]: 对外提供 EmbeddingStore 类（本地/云端 embedding 双模式）
# [POS]: graph 包的向量检索层，负责章节级语义索引、相似性搜索与文档级聚合检索
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from __future__ import annotations

from harnetics.models.document import Section

_COLLECTION_NAME = "harnetics_sections"


# ================================================================
# 云端 embedding function — 包装 litellm.embedding()
# ================================================================

class _LitellmEmbeddingFunction:
    """ChromaDB 自定义 EmbeddingFunction，路由到 litellm.embedding()。"""

    def __init__(self, model: str, api_key: str = "", base_url: str = "") -> None:
        self._model = model
        self._api_key = api_key or None
        self._base_url = base_url or None

    def __call__(self, input: list[str]) -> list[list[float]]:  # noqa: A002
        import litellm
        resp = litellm.embedding(
            model=self._model,
            input=input,
            api_key=self._api_key,
            api_base=self._base_url,
        )
        return [item["embedding"] for item in resp.data]


def _is_cloud_model(model_name: str) -> bool:
    """model_name 含 '/' 视为云端路由（如 openai/text-embedding-3-small）。"""
    return "/" in model_name


class EmbeddingStore:
    """ChromaDB 向量存储，承载章节级语义检索。支持本地 sentence-transformers 与云端 litellm embedding。"""

    def __init__(
        self,
        persist_path: str,
        model_name: str,
        api_key: str = "",
        base_url: str = "",
    ) -> None:
        import chromadb

        self._client = chromadb.PersistentClient(path=persist_path)
        self._model_name = model_name
        self._ef = self._build_ef(model_name, api_key=api_key, base_url=base_url)
        self._collection = self._client.get_or_create_collection(
            name=_COLLECTION_NAME,
            embedding_function=self._ef,
        )

    @staticmethod
    def _build_ef(model_name: str, api_key: str = "", base_url: str = ""):
        if _is_cloud_model(model_name):
            return _LitellmEmbeddingFunction(model=model_name, api_key=api_key, base_url=base_url)
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        return SentenceTransformerEmbeddingFunction(model_name=model_name)

    # ---- 索引 --------------------------------------------------------

    def index_sections(self, doc_id: str, sections: list[Section]) -> None:
        if not sections:
            return
        ids = [s.section_id for s in sections]
        documents = [f"{s.heading}\n{s.content}" for s in sections]
        metadatas = [
            {"doc_id": s.doc_id, "heading": s.heading,
             "level": s.level, "order_index": s.order_index}
            for s in sections
        ]
        self._collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    # ---- 章节级检索 ---------------------------------------------------

    def search_similar(
        self, query: str, top_k: int = 10, filters: dict | None = None
    ) -> list[dict]:
        where = filters if filters else None
        results = self._collection.query(
            query_texts=[query], n_results=top_k, where=where,
        )
        hits: list[dict] = []
        if not results["ids"] or not results["ids"][0]:
            return hits
        for i, sid in enumerate(results["ids"][0]):
            hit: dict = {"section_id": sid}
            if results["metadatas"]:
                hit.update(results["metadatas"][0][i])
            if results["documents"]:
                hit["text"] = results["documents"][0][i]
            if results["distances"]:
                hit["distance"] = results["distances"][0][i]
            hits.append(hit)
        return hits

    # ---- 文档级聚合检索 -----------------------------------------------

    def search_documents(self, query: str, top_k: int = 10) -> list[dict]:
        """按 query 检索章节后按 doc_id 聚合，取每个文档下最高相关度。"""
        section_hits = self.search_similar(query, top_k=top_k * 3)
        doc_best: dict[str, dict] = {}
        for hit in section_hits:
            doc_id = hit.get("doc_id", "")
            if not doc_id:
                continue
            distance = hit.get("distance", 999.0)
            score = max(0.0, 1.0 - distance)
            if doc_id not in doc_best or score > doc_best[doc_id]["relevance_score"]:
                doc_best[doc_id] = {"doc_id": doc_id, "relevance_score": round(score, 4)}
        ranked = sorted(doc_best.values(), key=lambda d: d["relevance_score"], reverse=True)
        return ranked[:top_k]

    # ---- 状态查询 -----------------------------------------------------

    def section_count(self) -> int:
        return self._collection.count()
