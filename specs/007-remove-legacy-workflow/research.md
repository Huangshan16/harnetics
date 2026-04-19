# Research: Remove Legacy Repository Workflow

**Feature**: 007-remove-legacy-workflow  
**Date**: 2026-04-19

## 审计方法

通过全量代码搜索、import 图谱追踪和测试覆盖分析，完成旧版工作流的边界识别。

## Decision 1: python-frontmatter 依赖是否移除

- **Decision**: 保留 `python-frontmatter>=1.1.0`
- **Rationale**: `graph/indexer.py`（新工作流核心）在 L208 使用 `frontmatter.loads()` 解析 Markdown frontmatter 元数据。移除将直接打断文档入库流程。
- **Alternatives considered**: 用 PyYAML 手动解析 frontmatter — 引入不必要的复杂度，python-frontmatter 本身体积极小。

## Decision 2: python-multipart 是否被新工作流使用

- **Decision**: 移除 `python-multipart>=0.0.12`
- **Rationale**: 搜索全部 `src/harnetics/api/` 路由，文件上传端点使用 `UploadFile` 但 FastAPI 自身内联了 multipart 处理（通过 `python-multipart` 或 `starlette` 的内置支持）。进一步验证：`pip show python-multipart` 显示它是 FastAPI 的 optional dependency，如果有 `UploadFile` 用法则实际上需要保留。
- **Risk**: 需要运行测试确认。如果上传端点 break，则回退保留此依赖。
- **Update after testing**: 如果测试失败，保留 `python-multipart`。

## Decision 3: jinja2 是否被新工作流使用

- **Decision**: 移除 `jinja2>=3.1.4`
- **Rationale**: 仅在 `web/routes.py` 中通过 `Jinja2Templates` 使用。新工作流的 API 路由纯 JSON，前端由 React SPA 处理。

## Decision 4: test_graph_store.py 中 Repository 引用处理

- **Decision**: 重写 `test_init_db_rejects_legacy_repository_schema` 为不依赖 Repository 的独立测试
- **Rationale**: 该测试的意图是"graph store 不应操作旧版 schema"。可以直接用 raw SQL 创建旧版表结构来验证，无需导入 Repository 类。
- **Alternatives considered**: 删除该测试 — 拒绝，因为 schema 隔离验证仍有价值。

## Decision 5: models.py vs models/ 目录

- **Decision**: 需要确认 `src/harnetics/models.py`（根级）和 `src/harnetics/models/`（目录）的关系
- **Rationale**: 如果 `models.py` 是旧版残留文件而 `models/` 是新版包，则删除 `models.py`。如果 `models.py` 不存在（被 `models/` 替代），则只需清理 `models/records.py`。
- **Resolution**: 需在实施阶段确认文件系统实际状态。

## 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| python-multipart 实际被 FastAPI UploadFile 需要 | 中 | 上传端点 break | 测试验证后决定；如 break 则回退保留 |
| 旧版代码中有新工作流的间接依赖 | 低 | 运行时 ImportError | 全量 import 图谱已确认隔离性 |
| AGENTS.md 更新遗漏 | 低 | 文档不一致 | GEB 回环强制检查 |
