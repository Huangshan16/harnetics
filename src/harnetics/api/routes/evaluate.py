"""
# [INPUT]: 依赖 graph.store (drafts 表)、evaluators.build_default_bus
# [OUTPUT]: 对外提供 router: POST /api/evaluate/{draft_id}、GET /api/evaluate/results/{draft_id}
# [POS]: api/routes 的评估域端点，US6 Evaluator 的 HTTP 接口
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md
"""
from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException

from harnetics.evaluators import build_default_bus
from harnetics.graph import store

router = APIRouter(prefix="/api/evaluate", tags=["evaluate"])


@router.post("/{draft_id}")
def run_evaluation(draft_id: str) -> dict:
    """对指定草稿运行全量 Evaluator Bus，更新 eval_results_json。"""
    with store.get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="draft not found")

    draft_dict = {
        "draft_id": row["draft_id"],
        "content_md": row["content_md"],
        "citations": json.loads(row["citations_json"] or "[]"),
        "conflicts": json.loads(row["conflicts_json"] or "[]"),
        "request": json.loads(row["request_json"] or "{}"),
    }

    bus = build_default_bus()
    results = bus.run_all(draft_dict)
    has_blocking = bus.has_blocking_failures(results)

    results_payload = [
        {
            "evaluator_id": r.evaluator_id,
            "name": r.name,
            "status": r.status.value,
            "level": r.level.value,
            "detail": r.detail,
            "locations": r.locations,
        }
        for r in results
    ]

    new_status = "blocked" if has_blocking else "eval_pass"
    with store.get_connection() as conn:
        conn.execute(
            "UPDATE drafts SET eval_results_json = ?, status = ? WHERE draft_id = ?",
            (json.dumps(results_payload, ensure_ascii=False), new_status, draft_id),
        )

    return {
        "draft_id": draft_id,
        "status": new_status,
        "has_blocking_failures": has_blocking,
        "results": results_payload,
    }


@router.get("/results/{draft_id}")
def get_eval_results(draft_id: str) -> dict:
    """获取草稿的已存储评估结果。"""
    with store.get_connection() as conn:
        row = conn.execute(
            "SELECT draft_id, status, eval_results_json FROM drafts WHERE draft_id = ?",
            (draft_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="draft not found")

    return {
        "draft_id": row["draft_id"],
        "status": row["status"],
        "results": json.loads(row["eval_results_json"] or "[]"),
    }
