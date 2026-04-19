# [INPUT]: 依赖 pytest、graph.store 与 raw SQL 构造旧版 schema
# [OUTPUT]: 提供 graph store 初始化与兼容性保护的回归测试
# [POS]: tests 目录中的图谱存储层测试，锁定新 graph schema 不再误踩旧 repository DB
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

import sqlite3
from pathlib import Path

import pytest

from harnetics.graph.embeddings import _normalize_embedding_model, _uses_remote_embeddings
from harnetics.graph.indexer import DocumentIndexer
from harnetics.graph.store import init_db
from harnetics.graph import store
from harnetics.models.document import DocumentEdge


def test_init_db_creates_graph_schema(tmp_path: Path) -> None:
    db_path = tmp_path / "graph.db"

    init_db(db_path)

    import sqlite3

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("PRAGMA table_info(documents)").fetchall()

    columns = {row[1] for row in rows}
    assert {"doc_id", "content_hash", "file_path", "created_at", "updated_at"} <= columns


def test_init_db_rejects_legacy_repository_schema(tmp_path: Path) -> None:
    """graph store 必须拒绝包含旧版 Repository schema 的数据库文件。"""
    db_path = tmp_path / "legacy.db"
    # ---- 用 raw SQL 创建旧版 documents 表（缺少 content_hash 等列） ----
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE documents ("
            "  doc_id TEXT PRIMARY KEY,"
            "  title TEXT NOT NULL,"
            "  doc_type TEXT NOT NULL,"
            "  version TEXT DEFAULT 'v1.0',"
            "  status TEXT DEFAULT 'draft'"
            ")"
        )

    with pytest.raises(RuntimeError, match="legacy repository database"):
        init_db(db_path)


def test_document_indexer_indexes_sections_when_embedding_store_present(tmp_path: Path) -> None:
    db_path = tmp_path / "graph.db"
    init_db(db_path)

    md_path = tmp_path / "DOC-SYS-001.md"
    md_path.write_text(
        """---
title: 系统级需求
doc_type: Requirement
department: 系统工程部
system_level: System
engineering_phase: Requirement
version: v1.0
status: Approved
---
# 1. 文档说明
本文档定义系统级需求。
""",
        encoding="utf-8",
    )

    class FakeEmbeddingStore:
        def __init__(self) -> None:
            self.calls: list[tuple[str, list[str]]] = []

        def index_sections(self, doc_id: str, sections: list) -> None:
            self.calls.append((doc_id, [section.section_id for section in sections]))

    emb_store = FakeEmbeddingStore()
    indexer = DocumentIndexer(embedding_store=emb_store)

    doc = indexer.ingest_document(str(md_path))

    stored_sections = store.get_sections(doc.doc_id)
    assert len(stored_sections) == 1
    assert emb_store.calls == [(doc.doc_id, [stored_sections[0].section_id])]


def test_ingest_directory_skips_agents_markdown(tmp_path: Path) -> None:
    db_path = tmp_path / "graph.db"
    init_db(db_path)

    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    (fixture_dir / "AGENTS.md").write_text("# internal", encoding="utf-8")
    (fixture_dir / "DOC-SYS-001.md").write_text(
        """---
title: 系统级需求
doc_type: Requirement
department: 系统工程部
system_level: System
engineering_phase: Requirement
version: v1.0
status: Approved
---
# 1. 文档说明
本文档定义系统级需求。
""",
        encoding="utf-8",
    )

    docs = DocumentIndexer().ingest_directory(str(fixture_dir))

    assert [doc.doc_id for doc in docs] == ["DOC-SYS-001"]


def test_ingest_markdown_preserves_frontmatter_after_leading_comment(tmp_path: Path) -> None:
    db_path = tmp_path / "graph.db"
    init_db(db_path)

    md_path = tmp_path / "DOC-SYS-001.md"
    md_path.write_text(
        """<!-- contract comment -->
---
doc_id: DOC-SYS-001
title: 天行一号运载火箭系统级需求文档
doc_type: Requirement
department: 系统工程部
system_level: System
engineering_phase: Requirement
version: v3.1
status: Approved
---
# 1. 文档说明
本文档定义系统级需求。
""",
        encoding="utf-8",
    )

    doc = DocumentIndexer().ingest_document(str(md_path))

    assert doc.title == "天行一号运载火箭系统级需求文档"
    assert doc.doc_type == "Requirement"
    assert doc.department == "系统工程部"
    assert doc.system_level == "System"


def test_embedding_model_normalizes_bare_openai_name_for_cloud_routing() -> None:
    assert _normalize_embedding_model("text-embedding-3-small") == "openai/text-embedding-3-small"
    assert _uses_remote_embeddings("text-embedding-3-small") is True


def test_embedding_model_keeps_local_sentence_transformer_route() -> None:
    model_name = "paraphrase-multilingual-MiniLM-L12-v2"

    assert _normalize_embedding_model(model_name) == model_name
    assert _uses_remote_embeddings(model_name) is False


def test_embedding_model_normalizes_bare_remote_name_for_openai_compatible_gateway() -> None:
    model_name = "jina-embeddings-v5-text-small"

    assert _normalize_embedding_model(
        model_name,
        api_key="sk-test",
        base_url="https://aihubmix.com/v1",
    ) == "openai/jina-embeddings-v5-text-small"
    assert _uses_remote_embeddings(
        model_name,
        api_key="sk-test",
        base_url="https://aihubmix.com/v1",
    ) is True


def test_document_indexer_reingest_replaces_outgoing_edges_instead_of_accumulating(tmp_path: Path) -> None:
    db_path = tmp_path / "graph.db"
    init_db(db_path)

    target_path = tmp_path / "DOC-TGT-001.md"
    target_path.write_text(
        """---
title: 目标文档
doc_type: Design
department: 动力系统部
system_level: Subsystem
engineering_phase: Design
version: v1.0
status: Approved
---
# 1. 目标文档
无引用。
""",
        encoding="utf-8",
    )

    source_path = tmp_path / "DOC-SRC-001.md"
    source_path.write_text(
        """---
title: 源文档
doc_type: Design
department: 动力系统部
system_level: Subsystem
engineering_phase: Design
version: v1.0
status: Approved
---
# 1. 总述
引用 DOC-TGT-001。
""",
        encoding="utf-8",
    )

    indexer = DocumentIndexer()
    indexer.ingest_document(str(target_path))
    indexer.ingest_document(str(source_path))
    indexer.ingest_document(str(source_path))

    upstream, _ = store.get_edges_for_doc("DOC-SRC-001")

    assert len(upstream) == 1
    assert upstream[0].target_doc_id == "DOC-TGT-001"


def test_collapse_doc_edges_dedupes_multiple_section_level_references() -> None:
    edges = [
        DocumentEdge(
            source_doc_id="DOC-A",
            source_section_id="DOC-A-sec-1",
            target_doc_id="DOC-B",
            target_section_id="",
            relation="references",
            confidence=0.8,
        ),
        DocumentEdge(
            source_doc_id="DOC-A",
            source_section_id="DOC-A-sec-2",
            target_doc_id="DOC-B",
            target_section_id="",
            relation="references",
            confidence=1.0,
        ),
        DocumentEdge(
            source_doc_id="DOC-A",
            source_section_id="DOC-A-sec-3",
            target_doc_id="DOC-B",
            target_section_id="",
            relation="constrained_by",
            confidence=0.7,
        ),
        DocumentEdge(
            source_doc_id="DOC-A",
            source_section_id="DOC-A-sec-4",
            target_doc_id="DOC-C",
            target_section_id="",
            relation="references",
            confidence=0.9,
        ),
    ]

    collapsed = store.collapse_doc_edges("DOC-A", edges)

    assert [(edge.target_doc_id, edge.relation) for edge in collapsed] == [
        ("DOC-B", "constrained_by"),
        ("DOC-B", "references"),
        ("DOC-C", "references"),
    ]
    assert next(edge for edge in collapsed if edge.target_doc_id == "DOC-B" and edge.relation == "references").confidence == 1.0