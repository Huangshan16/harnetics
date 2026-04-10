# [INPUT]: 依赖 FastAPI、pathlib、graph.store、config 与所有 api.routes.*
# [OUTPUT]: 对外提供 create_api_app() 工厂函数
# [POS]: api 包的应用装配层，注册全量 API 路由 + SPA 前端托管，支持 lifespan 启动 init_db
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from harnetics.config import get_settings
from harnetics.graph.store import init_db
from harnetics.api.routes.documents import router as documents_api_router
from harnetics.api.routes.evaluate import router as evaluate_router
from harnetics.api.routes.draft import router as draft_router
from harnetics.api.routes.impact import router as impact_router
from harnetics.api.routes.graph import router as graph_router
from harnetics.api.routes.status import router as status_router


@asynccontextmanager
async def _lifespan(app: FastAPI):
    """应用启动时初始化图谱数据库。"""
    settings = get_settings()
    init_db(settings.graph_db_path)
    yield


def create_api_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Harnetics", lifespan=_lifespan)

    app.state.settings = settings

    # ---- API 路由 ----
    app.include_router(documents_api_router)
    app.include_router(evaluate_router)
    app.include_router(draft_router)
    app.include_router(impact_router)
    app.include_router(graph_router)
    app.include_router(status_router)

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    # ---- SPA 前端托管 (production build) ----
    dist_dir = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "dist"
    if dist_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(dist_dir / "assets")), name="spa-assets")

        @app.get("/{full_path:path}")
        async def spa_fallback(request: Request, full_path: str):
            """SPA fallback: 非 API 路由一律返回 index.html。"""
            file_path = dist_dir / full_path
            if file_path.is_file():
                return FileResponse(str(file_path))
            return FileResponse(str(dist_dir / "index.html"))

    return app
