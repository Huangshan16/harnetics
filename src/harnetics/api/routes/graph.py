"""
# [INPUT]: 依赖 graph.query.DocumentGraph、graph.store (get_document/get_connection)
# [OUTPUT]: 对外提供 router: GET /api/graph、/edges、/upstream、/downstream、/stale、/related
# [POS]: api/routes 的图谱域端点，US4 文档关系图谱的 HTTP 接口
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from harnetics.graph.query import get_graph
from harnetics.graph import store

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("")
def full_graph(
    department: str | None = None,
    system_level: str | None = None,
) -> dict:
    """返回 vis-network 格式的全量图谱。"""
    return get_graph().get_full_graph(
        department=department or None,
        system_level=system_level or None,
    )


@router.get("/edges")
def list_edges() -> list[dict]:
    """返回所有边的 JSON 列表（前端图谱 / 关系面板使用）。"""
    with store.get_connection() as conn:
        rows = conn.execute(
            "SELECT edge_id, source_doc_id, target_doc_id, relation, confidence FROM document_edges"
        ).fetchall()
    return [
        {
            "edge_id": r["edge_id"],
            "source_doc_id": r["source_doc_id"],
            "target_doc_id": r["target_doc_id"],
            "relation": r["relation"],
            "confidence": r["confidence"],
        }
        for r in rows
    ]


@router.get("/upstream/{doc_id}")
def upstream(doc_id: str, depth: int = 3) -> list[dict]:
    """返回 doc_id 的上游文档节点列表（最大深度 depth）。"""
    _require_doc(doc_id)
    return get_graph().get_upstream(doc_id, depth=depth)


@router.get("/downstream/{doc_id}")
def downstream(doc_id: str, depth: int = 3) -> list[dict]:
    """返回 doc_id 的下游文档节点列表（最大深度 depth）。"""
    _require_doc(doc_id)
    return get_graph().get_downstream(doc_id, depth=depth)


@router.get("/stale")
def stale_references() -> list[dict]:
    """返回所有指向 Superseded 文档的陈旧引用边。"""
    return get_graph().get_stale_references()


@router.get("/related/{doc_id}")
def related(doc_id: str) -> list[dict]:
    """返回与 doc_id 直接相连的所有文档节点。"""
    _require_doc(doc_id)
    return get_graph().get_related(doc_id)


def _require_doc(doc_id: str) -> None:
    if store.get_document(doc_id) is None:
        raise HTTPException(status_code=404, detail=f"document not found: {doc_id}")
