"""
# [INPUT]: 依赖 engine.impact_analyzer.ImpactAnalyzer、llm.client.HarneticsLLM、graph.store (impact_reports 表)
# [OUTPUT]: 对外提供 router: POST /api/impact/analyze、GET /api/impact、GET /api/impact/{id}、GET /api/impact/{id}/export
# [POS]: api/routes 的影响分析域端点，US3 影响分析的 HTTP 入口，注入 embedding_store + llm
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md
"""
from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from harnetics.engine.impact_analyzer import ImpactAnalyzer
from harnetics.graph import store
from harnetics.llm.client import HarneticsLLM

router = APIRouter(prefix="/api/impact", tags=["impact"])


class ImpactAnalyzeRequest(BaseModel):
    doc_id: str
    old_version: str = ""
    new_version: str = ""
    changed_section_ids: list[str] = []


@router.get("")
def list_impact_reports() -> list[dict]:
    """列出所有影响分析报告（摘要）。"""
    with store.get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM impact_reports ORDER BY created_at DESC"
        ).fetchall()
    return [
        {
            "report_id": r["report_id"],
            "trigger_doc_id": r["trigger_doc_id"],
            "old_version": r["old_version"],
            "new_version": r["new_version"],
            "summary": r["summary"],
            "changed_sections": json.loads(r["changed_sections_json"] or "[]"),
            "impacted_docs": json.loads(r["impacted_docs_json"] or "[]"),
            "created_at": r["created_at"],
        }
        for r in rows
    ]


@router.post("/analyze")
def analyze_impact(req: ImpactAnalyzeRequest, request: Request) -> dict:
    """触发变更影响分析，返回完整 ImpactReport。注入 embedding_store + llm 启用 AI 向量分析。"""
    try:
        settings = request.app.state.settings
        embedding_store = getattr(request.app.state, "embedding_store", None)

        llm = None
        if settings.llm_model:
            llm = HarneticsLLM(
                model=settings.llm_model,
                api_base=settings.llm_base_url,
                api_key=settings.llm_api_key,
            )

        analyzer = ImpactAnalyzer(embedding_store=embedding_store, llm=llm)
        report = analyzer.analyze(
            doc_id=req.doc_id,
            old_version=req.old_version,
            new_version=req.new_version,
            changed_section_ids=req.changed_section_ids or None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return _serialize_report(report)


@router.get("/{report_id}")
def get_impact_report(report_id: str) -> dict:
    """获取已存储的影响分析报告。"""
    with store.get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM impact_reports WHERE report_id = ?", (report_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="impact report not found")
    return {
        "report_id": row["report_id"],
        "trigger_doc_id": row["trigger_doc_id"],
        "old_version": row["old_version"],
        "new_version": row["new_version"],
        "summary": row["summary"],
        "changed_sections": json.loads(row["changed_sections_json"] or "[]"),
        "impacted_docs": json.loads(row["impacted_docs_json"] or "[]"),
        "created_at": row["created_at"],
    }


@router.get("/{report_id}/export", response_class=PlainTextResponse)
def export_impact_report(report_id: str) -> str:
    """以 Markdown 表格形式导出影响分析报告。"""
    with store.get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM impact_reports WHERE report_id = ?", (report_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="impact report not found")

    impacted = json.loads(row["impacted_docs_json"] or "[]")
    lines = [
        f"# 影响分析报告 {row['report_id']}",
        f"**触发文档：** {row['trigger_doc_id']}",
        f"**版本变更：** {row['old_version']} → {row['new_version']}",
        "",
        row["summary"],
        "",
        "## 影响文档清单",
        "",
        "| 文档 ID | 标题 | 关系 | 危险等级 |",
        "|---------|------|------|----------|",
    ]
    for d in impacted:
        lines.append(
            f"| {d.get('doc_id','')} | {d.get('title','')} | {d.get('relation','')} | {d.get('severity','')} |"
        )
    return "\n".join(lines)


# ================================================================
# 序列化
# ================================================================

def _serialize_report(report) -> dict:
    return {
        "report_id": report.report_id,
        "trigger_doc_id": report.trigger_doc_id,
        "old_version": report.old_version,
        "new_version": report.new_version,
        "summary": report.summary,
        "analysis_mode": report.analysis_mode,
        "changed_sections": [
            {
                "section_id": s.section_id,
                "heading": s.heading,
                "change_type": s.change_type,
                "summary": s.summary,
            }
            for s in report.changed_sections
        ],
        "impacted_docs": [
            {
                "doc_id": d.doc_id,
                "title": d.title,
                "relation": d.relation,
                "severity": d.severity,
                "analysis_mode": d.analysis_mode,
                "affected_sections": [
                    {"section_id": a.section_id, "heading": a.heading, "reason": a.reason}
                    for a in d.affected_sections
                ],
            }
            for d in report.impacted_docs
        ],
        "created_at": report.created_at,
    }
