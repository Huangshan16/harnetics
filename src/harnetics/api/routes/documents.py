# [INPUT]: 依赖 FastAPI、graph.store CRUD、graph.indexer、graph.embeddings.EmbeddingStore、models (DocumentNode/Section/ICDParameter)
# [OUTPUT]: 对外提供 documents_router (文档上传/列表/详情/删除/章节/向量搜索) 与 ICD 参数路由
# [POS]: api/routes 的文档域 REST 端点，被 api/app.py 注册
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from harnetics.graph import store
from harnetics.graph.indexer import DocumentIndexer

router = APIRouter(prefix="/api")


# ================================================================
# 文档端点
# ================================================================

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_id: str = Form(""),
    title: str = Form(""),
    doc_type: str = Form(""),
    department: str = Form(""),
    system_level: str = Form(""),
    engineering_phase: str = Form(""),
    version: str = Form(""),
):
    filename = file.filename or ""
    if not filename:
        raise HTTPException(400, "missing filename")
    safe_name = Path(filename).name
    if safe_name != filename or safe_name in {"", ".", ".."}:
        raise HTTPException(400, "invalid filename")

    suffix = Path(safe_name).suffix.lower()
    if suffix not in (".md", ".yaml", ".yml"):
        raise HTTPException(400, "unsupported file type, expected .md / .yaml / .yml")

    content = await file.read()
    tmp = Path(tempfile.mkdtemp()) / safe_name
    tmp.write_bytes(content)

    meta = {}
    if doc_id:
        meta["doc_id"] = doc_id
    if title:
        meta["title"] = title
    if doc_type:
        meta["doc_type"] = doc_type
    if department:
        meta["department"] = department
    if system_level:
        meta["system_level"] = system_level
    if engineering_phase:
        meta["engineering_phase"] = engineering_phase
    if version:
        meta["version"] = version

    indexer = DocumentIndexer()
    try:
        doc = indexer.ingest_document(str(tmp), meta)
    except Exception as exc:
        raise HTTPException(400, f"import failed: {exc}") from exc
    finally:
        tmp.unlink(missing_ok=True)

    return {"status": "ok", "doc_id": doc.doc_id, "title": doc.title}


@router.get("/documents")
def list_documents(
    department: str | None = None,
    doc_type: str | None = None,
    system_level: str | None = None,
    status: str | None = None,
    q: str | None = None,
    page: int = 1,
    per_page: int = 50,
):
    docs = store.get_documents(
        department=department, doc_type=doc_type,
        system_level=system_level, status=status, q=q,
    )
    total = len(docs)
    start = (page - 1) * per_page
    page_docs = docs[start : start + per_page]
    return {
        "total": total, "page": page, "per_page": per_page,
        "documents": [_doc_dict(d) for d in page_docs],
    }


@router.get("/documents/search")
def search_documents(q: str, top_k: int = 10, request: Request = None):
    """向量语义检索：按 query 检索相似文档，返回排序结果列表。"""
    embedding_store = getattr(request.app.state, "embedding_store", None) if request else None
    if embedding_store is None:
        raise HTTPException(503, "embedding store not available")

    hits = embedding_store.search_documents(query=q, top_k=top_k)
    results = []
    for hit in hits:
        doc = store.get_document(hit["doc_id"])
        if doc is None:
            continue
        results.append({
            **_doc_dict(doc),
            "relevance_score": hit.get("relevance_score", 0),
        })
    return {"results": results}


@router.get("/documents/{doc_id}")
def document_detail(doc_id: str):
    doc = store.get_document(doc_id)
    if not doc:
        raise HTTPException(404, "document not found")
    sections = store.get_sections(doc_id)
    upstream, downstream = store.get_edges_for_doc(doc_id)
    icd_params = store.get_icd_parameters(doc_id)
    return {
        "document": _doc_dict(doc),
        "sections": [_sec_dict(s) for s in sections],
        "upstream": [_edge_dict(e) for e in upstream],
        "downstream": [_edge_dict(e) for e in downstream],
        "icd_parameters": [_icd_dict(p) for p in icd_params],
    }


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    doc = store.get_document(doc_id)
    if not doc:
        raise HTTPException(404, "document not found")
    store.delete_document(doc_id)
    return {"status": "deleted", "doc_id": doc_id}


@router.get("/documents/{doc_id}/sections")
def document_sections(doc_id: str):
    doc = store.get_document(doc_id)
    if not doc:
        raise HTTPException(404, "document not found")
    return {"doc_id": doc_id, "sections": [_sec_dict(s) for s in store.get_sections(doc_id)]}


# ================================================================
# ICD 参数端点
# ================================================================

@router.get("/icd/parameters")
def list_icd_parameters(doc_id: str | None = None):
    params = store.get_icd_parameters(doc_id)
    return {"parameters": [_icd_dict(p) for p in params]}


@router.get("/icd/parameters/{param_id}")
def icd_parameter_detail(param_id: str):
    p = store.get_icd_parameter(param_id)
    if not p:
        raise HTTPException(404, "ICD parameter not found")
    return _icd_dict(p)


# ================================================================
# 序列化辅助
# ================================================================

def _doc_dict(d) -> dict:
    return {
        "doc_id": d.doc_id, "title": d.title, "doc_type": d.doc_type,
        "department": d.department, "system_level": d.system_level,
        "engineering_phase": d.engineering_phase, "version": d.version,
        "status": d.status, "created_at": d.created_at, "updated_at": d.updated_at,
    }


def _sec_dict(s) -> dict:
    return {
        "section_id": s.section_id, "doc_id": s.doc_id, "heading": s.heading,
        "content": s.content, "level": s.level, "order_index": s.order_index,
    }


def _edge_dict(e) -> dict:
    return {
        "edge_id": e.edge_id, "source_doc_id": e.source_doc_id,
        "target_doc_id": e.target_doc_id, "relation": e.relation,
        "confidence": e.confidence,
    }


def _icd_dict(p) -> dict:
    return {
        "param_id": p.param_id, "doc_id": p.doc_id, "name": p.name,
        "interface_type": p.interface_type, "subsystem_a": p.subsystem_a,
        "subsystem_b": p.subsystem_b, "value": p.value, "unit": p.unit,
        "range": p.range_, "owner_department": p.owner_department,
        "version": p.version,
    }
