"""
# [INPUT]: 依赖 graph.store (counts)、graph.query (stale_references)、llm.client (check_availability)
# [OUTPUT]: 对外提供 router: GET /api/status
# [POS]: api/routes 的健康看板端点，US5 仪表盘数据源
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md
"""
from __future__ import annotations

import json

from fastapi import APIRouter

from harnetics.graph import store
from harnetics.graph.query import get_graph

router = APIRouter(prefix="/api", tags=["status"])


@router.get("/status")
def system_status() -> dict:
    """返回系统健康指标：文档数、草稿数、陈旧引用数、LLM 可用性、Evaluator 通过率。"""
    with store.get_connection() as conn:
        doc_count: int = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        draft_count: int = conn.execute("SELECT COUNT(*) FROM drafts").fetchone()[0]
        eval_pass: int = conn.execute(
            "SELECT COUNT(*) FROM drafts WHERE status = 'eval_pass'"
        ).fetchone()[0]
        eval_blocked: int = conn.execute(
            "SELECT COUNT(*) FROM drafts WHERE status = 'blocked'"
        ).fetchone()[0]
        icd_count: int = conn.execute("SELECT COUNT(*) FROM icd_parameters").fetchone()[0]
        impact_count: int = conn.execute("SELECT COUNT(*) FROM impact_reports").fetchone()[0]

    stale = get_graph().get_stale_references()

    # LLM 可用性（不抛异常）
    llm_ok = False
    try:
        from harnetics.llm.client import HarneticsLLM
        llm_ok = HarneticsLLM().check_availability()
    except Exception:
        pass

    eval_total = eval_pass + eval_blocked
    eval_pass_rate = round(eval_pass / eval_total, 2) if eval_total > 0 else None

    return {
        "documents": doc_count,
        "drafts": draft_count,
        "icd_parameters": icd_count,
        "impact_reports": impact_count,
        "stale_references": len(stale),
        "llm_available": llm_ok,
        "eval_pass_rate": eval_pass_rate,
        "eval_pass": eval_pass,
        "eval_blocked": eval_blocked,
    }
