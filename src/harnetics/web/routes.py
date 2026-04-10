# [INPUT]: 依赖 FastAPI、Jinja2 模板、graph.store CRUD、旧版 Repository/ImportService/DraftService
# [OUTPUT]: 对外提供根路径跳转、文档列表/详情/上传页面与草稿工作流路由，以及图谱/影响/仪表盘页面
# [POS]: harnetics/web 的 HTTP 入口，负责文档库浏览（graph store 驱动）与草稿生成/编辑/导出闭环
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from pathlib import Path
from datetime import datetime
from datetime import timezone

from fastapi import APIRouter
from fastapi import File
from fastapi import Form
from fastapi import HTTPException
from fastapi import Request
from fastapi import UploadFile
from fastapi.responses import HTMLResponse
from fastapi.responses import PlainTextResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import yaml

from harnetics.graph import store as graph_store

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))


def _normalize_filter(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    return value


@router.get("/")
def root():
    return RedirectResponse("/dashboard")


@router.get("/documents", response_class=HTMLResponse)
def list_documents(
    request: Request,
    department: str | None = None,
    doc_type: str | None = None,
    system_level: str | None = None,
    q: str | None = None,
    query: str | None = None,
):
    department = _normalize_filter(department)
    doc_type = _normalize_filter(doc_type)
    system_level = _normalize_filter(system_level)
    # 兼容旧版 query 参数名
    search = _normalize_filter(q) or _normalize_filter(query)

    # ---- 旧版仓储路径（旧 create_app 填充了 repository） ----
    if hasattr(request.app.state, "repository"):
        documents = request.app.state.repository.list_documents(
            department=department, doc_type=doc_type,
            system_level=system_level, query=search,
        )
        return templates.TemplateResponse(
            request, "documents/list.html",
            {
                "documents": documents,
                "departments": [], "doc_types": [], "system_levels": [],
                "filters": {
                    "department": department or "", "doc_type": doc_type or "",
                    "system_level": system_level or "", "q": search or "",
                },
            },
        )

    # ---- 新版 graph store 路径 ----
    documents = graph_store.get_documents(
        department=department, doc_type=doc_type,
        system_level=system_level, q=search,
    )
    all_docs = graph_store.get_documents()
    departments = sorted({d.department for d in all_docs if d.department})
    doc_types = sorted({d.doc_type for d in all_docs if d.doc_type})
    system_levels = sorted({d.system_level for d in all_docs if d.system_level})
    return templates.TemplateResponse(
        request,
        "documents/list.html",
        {
            "documents": documents,
            "departments": departments,
            "doc_types": doc_types,
            "system_levels": system_levels,
            "filters": {
                "department": department or "",
                "doc_type": doc_type or "",
                "system_level": system_level or "",
                "q": search or "",
            },
        },
    )


@router.get("/documents/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    return templates.TemplateResponse(request, "documents/upload.html", {})


# ---- 旧版导入端点（被 test_catalog_routes 依赖，保留兼容） ----
@router.post("/documents/import")
async def import_document(request: Request, file: UploadFile = File(...)):
    filename = file.filename or ""
    if not filename:
        raise HTTPException(status_code=400, detail="missing filename")
    if "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="invalid filename")
    safe_name = Path(filename).name
    if safe_name != filename or safe_name in {"", ".", ".."}:
        raise HTTPException(status_code=400, detail="invalid filename")
    target_path = Path(request.app.state.settings.raw_upload_dir) / safe_name
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists():
        raise HTTPException(status_code=400, detail="file already exists")
    target_path.write_bytes(await file.read())
    try:
        request.app.state.import_service.import_file(target_path)
    except yaml.YAMLError as exc:
        try:
            target_path.unlink()
        except FileNotFoundError:
            pass
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        try:
            target_path.unlink()
        except FileNotFoundError:
            pass
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "imported"}


@router.get("/documents/{doc_id}", response_class=HTMLResponse)
def graph_document_detail(request: Request, doc_id: str):
    # 旧版 integer ID 使用旧仓储
    if doc_id.isdigit() and hasattr(request.app.state, "repository"):
        try:
            detail = request.app.state.repository.get_document_detail(int(doc_id))
        except LookupError as exc:
            raise HTTPException(status_code=404, detail="document not found") from exc
        return templates.TemplateResponse(
            request, "document_detail.html", {"request": request, "detail": detail},
        )
    # 新版 string doc_id 使用 graph store
    document = graph_store.get_document(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="document not found")
    sections = graph_store.get_sections(doc_id)
    upstream, downstream = graph_store.get_edges_for_doc(doc_id)
    icd_params = graph_store.get_icd_parameters(doc_id)
    return templates.TemplateResponse(
        request,
        "documents/detail.html",
        {
            "document": document,
            "sections": sections,
            "upstream": upstream,
            "downstream": downstream,
            "icd_params": icd_params,
        },
    )


@router.get("/drafts/new", response_class=HTMLResponse)
def new_draft(request: Request):
    return templates.TemplateResponse(
        request,
        "draft_new.html",
        {
            "request": request,
            "plan": None,
            "topic": "",
            "department": "",
            "target_doc_type": "",
            "target_system_level": "",
        },
    )


@router.post("/drafts/plan", response_class=HTMLResponse)
def plan_draft(
    request: Request,
    topic: str = Form(...),
    department: str = Form(...),
    target_doc_type: str = Form(...),
    target_system_level: str = Form(...),
):
    try:
        plan = request.app.state.retrieval_planner.plan(
            topic=topic,
            department=department,
            target_doc_type=target_doc_type,
            target_system_level=target_system_level,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=400,
            detail="no template available for draft planning",
        ) from exc
    return templates.TemplateResponse(
        request,
        "draft_new.html",
        {
            "request": request,
            "plan": plan,
            "topic": topic,
            "department": department,
            "target_doc_type": target_doc_type,
            "target_system_level": target_system_level,
        },
    )


@router.post("/drafts")
def create_draft(
    request: Request,
    topic: str = Form(...),
    department: str = Form(...),
    target_doc_type: str = Form(...),
    target_system_level: str = Form(...),
    selected_document_ids: list[int] = Form(...),
    template_id: int = Form(...),
):
    draft = request.app.state.draft_service.generate(
        topic=topic,
        department=department,
        target_doc_type=target_doc_type,
        target_system_level=target_system_level,
        selected_document_ids=selected_document_ids,
        template_id=template_id,
    )
    return RedirectResponse(f"/drafts/{draft.id}", status_code=303)


@router.get("/drafts/{draft_id}", response_class=HTMLResponse)
def show_draft(request: Request, draft_id: int):
    try:
        draft = request.app.state.repository.get_draft_detail(draft_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="draft not found") from exc
    return templates.TemplateResponse(
        request,
        "draft_show.html",
        {
            "request": request,
            "draft": draft,
            "issues": draft.issues,
            "citations": draft.citations,
        },
    )


@router.post("/drafts/{draft_id}/edit")
def update_draft(request: Request, draft_id: int, content: str = Form(...)):
    try:
        request.app.state.repository.get_draft_detail(draft_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="draft not found") from exc
    request.app.state.draft_service.update_content(draft_id=draft_id, content=content)
    return RedirectResponse(f"/drafts/{draft_id}", status_code=303)


@router.get("/drafts/{draft_id}/export")
def export_draft(request: Request, draft_id: int):
    try:
        draft = request.app.state.repository.get_draft_detail(draft_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="draft not found") from exc
    request.app.state.repository.mark_draft_exported(
        draft_id,
        datetime.now(timezone.utc),
    )
    return PlainTextResponse(
        draft.content_markdown,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="draft-{draft_id}.md"'},
    )


# ================================================================
# 新版页面路由（US2/US3/US4/US5）
# ================================================================

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@router.get("/drafts/workspace", response_class=HTMLResponse)
def draft_workspace(request: Request):
    docs = graph_store.get_documents()
    return templates.TemplateResponse(request, "draft/workspace.html", {"documents": docs})


@router.get("/drafts/{draft_id_str}", response_class=HTMLResponse)
def draft_result_page(request: Request, draft_id_str: str):
    """草稿详情页：兼容新版字符串 draft_id 与旧版数字 id。"""
    # 旧版整数 id 走旧路径
    if draft_id_str.isdigit() and hasattr(request.app.state, "repository"):
        try:
            draft = request.app.state.repository.get_draft_detail(int(draft_id_str))
        except LookupError as exc:
            raise HTTPException(status_code=404, detail="draft not found") from exc
        return templates.TemplateResponse(
            request, "draft_show.html",
            {"request": request, "draft": draft, "issues": draft.issues, "citations": draft.citations},
        )
    # 新版字符串 DRAFT-* id
    import json as _json
    from harnetics.graph import store as _store
    with _store.get_connection() as conn:
        row = conn.execute("SELECT * FROM drafts WHERE draft_id = ?", (draft_id_str,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="draft not found")

    draft_obj = {
        "draft_id": row["draft_id"],
        "status": row["status"],
        "content_md": row["content_md"],
        "citations": _json.loads(row["citations_json"] or "[]"),
        "conflicts": _json.loads(row["conflicts_json"] or "[]"),
        "eval_results": _json.loads(row["eval_results_json"] or "[]"),
        "generated_by": row["generated_by"],
        "created_at": row["created_at"],
    }
    return templates.TemplateResponse(request, "draft/result.html", {"draft": draft_obj})


@router.get("/impact", response_class=HTMLResponse)
def impact_page(request: Request, doc_id: str | None = None):
    docs = graph_store.get_documents()
    return templates.TemplateResponse(request, "impact/analyze.html", {"documents": docs, "selected_doc_id": doc_id or ""})


@router.get("/graph", response_class=HTMLResponse)
def graph_page(request: Request):
    all_docs = graph_store.get_documents()
    departments = sorted({d.department for d in all_docs if d.department})
    system_levels = sorted({d.system_level for d in all_docs if d.system_level})
    return templates.TemplateResponse(
        request, "graph/view.html",
        {"departments": departments, "system_levels": system_levels},
    )
