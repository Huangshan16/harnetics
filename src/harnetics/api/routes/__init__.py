# [INPUT]: 聚合 api/routes 子模块的路由
# [OUTPUT]: 对外提供 documents_router
# [POS]: api/routes 包入口，按领域拆分的 API 路由模块
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from .documents import router as documents_router

__all__ = ["documents_router"]
