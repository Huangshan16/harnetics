# [INPUT]: 依赖 chromadb、sentence-transformers 与 models.document.Section
# [OUTPUT]: 对外提供 EmbeddingStore 类
# [POS]: graph 包的向量检索层，负责章节级语义索引与相似性搜索
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from __future__ import annotations

from harnetics.models.document import Section

_COLLECTION_NAME = "harnetics_sections"


class EmbeddingStore:
    """ChromaDB 向量存储，承载章节级语义检索。"""

    def __init__(self, persist_path: str, model_name: str) -> None:
        import chromadb

        self._client = chromadb.PersistentClient(path=persist_path)
        self._model_name = model_name
        self._ef = self._build_ef(model_name)
        self._collection = self._client.get_or_create_collection(
            name=_COLLECTION_NAME,
            embedding_function=self._ef,
        )

    @staticmethod
    def _build_ef(model_name: str):
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        return SentenceTransformerEmbeddingFunction(model_name=model_name)

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
