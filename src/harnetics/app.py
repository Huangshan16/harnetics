# [INPUT]: 依赖 FastAPI、本地配置工厂 get_settings 与 web.router
# [OUTPUT]: 提供 create_app()、模块级 app 实例，以及 /health 和 catalog 路由挂载
# [POS]: harnetics 的应用装配层，负责把配置挂到 app.state 上并组装 HTTP 入口
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from fastapi import FastAPI

from .config import get_settings
from .web.routes import router


def create_app() -> FastAPI:
    app = FastAPI(title="Harnetics")
    app.state.settings = get_settings()
    app.include_router(router)

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
