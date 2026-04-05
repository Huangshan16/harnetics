# harnetics/
> L2 | 父级: /AGENTS.md

成员清单
__init__.py: 包级入口，导出最小公共 API。
app.py: FastAPI 应用工厂，挂载健康检查、仓储/导入服务与 web 路由。
config.py: 运行时设置对象与默认路径来源。
models.py: 领域记录 dataclass，供仓储与服务层共享。
importer.py: 受控 Markdown/YAML 导入服务，负责解析、校验与入库。
repository.py: SQLite schema 初始化与唯一持久化边界。
web/: 文档目录 HTTP 路由与页面渲染子模块。

法则: 只保留最小可运行骨架，避免把业务逻辑塞进包根。

[PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md
