# harnetics/web/
> L2 | 父级: src/harnetics/AGENTS.md

成员清单
routes.py: FastAPI `APIRouter` 挂载点，承载文档导入、列表筛选与详情路由。
templates/: Jinja2 模板目录，承载 `documents.html`、`document_detail.html` 与页面母版。

法则: 只放与页面渲染有关的静态和模板资源，不混入业务逻辑。

[PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md
