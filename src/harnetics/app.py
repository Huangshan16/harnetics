# [INPUT]: 依赖 FastAPI、本地配置工厂 get_settings、Repository、ImportService 与 web.router
# [OUTPUT]: 提供 create_app()、模块级 app 实例，以及 /health 和 catalog 路由挂载
# [POS]: harnetics 的应用装配层，负责把配置、仓储与导入服务挂到 app.state 上并组装 HTTP 入口
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from fastapi import FastAPI

from .config import get_settings
from .importer import ImportService
from .repository import Repository
from .web.routes import router


def create_app() -> FastAPI:
    app = FastAPI(title="Harnetics")
    settings = get_settings()
    repository = Repository(settings.database_path)
    app.state.settings = settings
    app.state.repository = repository
    app.state.import_service = ImportService(repository)
    app.include_router(router)

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
