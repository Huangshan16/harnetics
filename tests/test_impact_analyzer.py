# [INPUT]: 依赖 pytest、graph.store、engine.impact_analyzer 与文档模型
# [OUTPUT]: 提供 ImpactAnalyzer 的批量 LLM 精判与缓存行为回归测试
# [POS]: tests 目录中的影响分析单元测试，锁定 AI 精判不会按候选章节重复调用外部 LLM
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from __future__ import annotations

from harnetics.engine.impact_analyzer import ImpactAnalyzer
from harnetics.graph import store
from harnetics.models.document import DocumentEdge, DocumentNode, Section


class _FakeEmbeddingStore:
    def __init__(self, hits: list[dict]) -> None:
        self._hits = hits

    def search_similar(self, query: str, top_k: int = 10, filters: dict | None = None) -> list[dict]:
        assert query
        assert filters == {"doc_id": "DOC-DEP-001"}
        return list(self._hits)


class _CountingLLM:
    def __init__(self) -> None:
        self.calls = 0

    def generate_draft(self, system_prompt: str, context: str, user_request: str) -> str:
        self.calls += 1
        assert "候选章节(JSON)" in user_request
        assert "SEC-DEP-001" in user_request
        assert "SEC-DEP-002" in user_request
        return (
            '{"results": ['
            '{"section_id": "SEC-DEP-001", "affected": true, "reason": "引用了变更需求"}, '
            '{"section_id": "SEC-DEP-002", "affected": true, "reason": "参数说明需要同步更新"}'
            ']}'
        )


def test_impact_analyzer_batches_llm_judgement_per_document(graph_db_path) -> None:
    store.insert_document(
        DocumentNode(
            doc_id="DOC-SRC-001",
            title="上游需求",
            doc_type="Requirement",
            department="系统工程部",
            system_level="System",
            engineering_phase="Requirement",
            version="v1.0",
            status="Approved",
        )
    )
    store.insert_sections(
        [
            Section(
                section_id="SEC-SRC-001",
                doc_id="DOC-SRC-001",
                heading="1. 动力需求",
                content="REQ-SYS-001 发动机入口压力不低于 10 MPa。",
                level=2,
                order_index=1,
            )
        ]
    )

    store.insert_document(
        DocumentNode(
            doc_id="DOC-DEP-001",
            title="下游设计",
            doc_type="Design",
            department="动力系统部",
            system_level="Subsystem",
            engineering_phase="Design",
            version="v1.0",
            status="Approved",
        )
    )
    store.insert_sections(
        [
            Section(
                section_id="SEC-DEP-001",
                doc_id="DOC-DEP-001",
                heading="1. 设计约束",
                content="本节引用 REQ-SYS-001。",
                level=2,
                order_index=1,
            ),
            Section(
                section_id="SEC-DEP-002",
                doc_id="DOC-DEP-001",
                heading="2. 参数说明",
                content="入口压力设计值与上游需求保持一致。",
                level=2,
                order_index=2,
            ),
        ]
    )
    store.insert_edges(
        [
            DocumentEdge(
                source_doc_id="DOC-DEP-001",
                source_section_id="SEC-DEP-001",
                target_doc_id="DOC-SRC-001",
                target_section_id="SEC-SRC-001",
                relation="references",
            )
        ]
    )

    llm = _CountingLLM()
    analyzer = ImpactAnalyzer(
        embedding_store=_FakeEmbeddingStore(
            [
                {
                    "section_id": "SEC-DEP-001",
                    "doc_id": "DOC-DEP-001",
                    "heading": "1. 设计约束",
                    "text": "本节引用 REQ-SYS-001。",
                    "distance": 0.05,
                },
                {
                    "section_id": "SEC-DEP-002",
                    "doc_id": "DOC-DEP-001",
                    "heading": "2. 参数说明",
                    "text": "入口压力设计值与上游需求保持一致。",
                    "distance": 0.08,
                },
            ]
        ),
        llm=llm,
    )

    report = analyzer.analyze(
        doc_id="DOC-SRC-001",
        old_version="v1.0",
        new_version="v1.1",
        changed_section_ids=["SEC-SRC-001"],
    )

    assert llm.calls == 1
    assert len(report.impacted_docs) == 1
    impacted = report.impacted_docs[0]
    assert impacted.doc_id == "DOC-DEP-001"
    assert impacted.analysis_mode == "ai_vector"
    assert [section.section_id for section in impacted.affected_sections] == [
        "SEC-DEP-001",
        "SEC-DEP-002",
    ]
