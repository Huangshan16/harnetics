# Feature Specification: Remove Legacy Repository Workflow

**Feature Branch**: `007-remove-legacy-workflow`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: User description: "将旧版 Repository 工作流以及相关代码从本项目进行系统化移除，为开源发布做准备"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 开源贡献者首次 clone 并启动项目 (Priority: P1)

一位新的开源贡献者 clone 仓库，执行 `uv sync && npm install`，然后 `uv run python -m harnetics.cli.main serve`，打开浏览器访问 React SPA。整个过程中不会遇到任何旧版模块的导入错误、废弃配置项、或 Jinja2/HTMX 路由残留。

**Why this priority**: 开源项目的第一印象决定贡献者留存率。如果 clone 后遇到死代码、废弃依赖或令人困惑的双工作流，贡献者会直接离开。

**Independent Test**: 全新环境下 `uv sync --dev && cd frontend && npm install && cd .. && uv run pytest tests/ -q` 全部通过，且不存在任何对 `repository.py` 或 `harnetics.db` 的引用。

**Acceptance Scenarios**:

1. **Given** 全新 clone 的仓库, **When** 执行 `uv sync --dev`, **Then** 不安装 `jinja2` 或 `python-multipart` 依赖
2. **Given** 全新 clone 的仓库, **When** 执行 `uv run pytest tests/ -q`, **Then** 所有测试通过，无废弃模块导入错误
3. **Given** 全新 clone 的仓库, **When** 在源码树中搜索 `harnetics.db`, **Then** 仅在 var/ .gitignore 或迁移说明中出现，不在任何 Python 代码中出现

---

### User Story 2 - 维护者确认新工作流完整性不受影响 (Priority: P1)

项目维护者在移除旧版代码后运行完整测试套件和前端构建，确认图谱 API、React SPA、CLI ingest/serve 命令、影响分析、草稿生成等全部正常工作。

**Why this priority**: 移除代码是减法手术——必须保证切除的是死组织而非活组织。

**Independent Test**: `uv run pytest tests/ -q` 通过全部现有的图谱/API/E2E 测试，`cd frontend && npm run build` 成功。

**Acceptance Scenarios**:

1. **Given** 旧版代码已移除, **When** 运行 `uv run pytest tests/ -q`, **Then** 所有图谱、API、E2E 测试通过
2. **Given** 旧版代码已移除, **When** 启动后端并访问 `/api/documents`, **Then** 返回正常的文档列表 JSON
3. **Given** 旧版代码已移除, **When** 执行 `uv run python -m harnetics.cli.main ingest fixtures/`, **Then** 文档正常入库至 graph DB

---

### User Story 3 - 开发者理解清晰的单一架构 (Priority: P2)

开发者阅读 README、ARCHITECTURE.md 和 AGENTS.md 时，看到的是一套清晰、统一的架构描述（FastAPI + React SPA + SQLite graph store），不再有"旧版 vs 新版"的二元叙事和双数据库警告。

**Why this priority**: 文档即架构的镜像。清除代码但保留双重叙事，等于手术成功但伤口没缝合。

**Independent Test**: README.md 中不包含"旧版"、"兼容保留"、"不要混用"等措辞；AGENTS.md 和 ARCHITECTURE.md 反映单一工作流。

**Acceptance Scenarios**:

1. **Given** 旧版代码和文档已清理, **When** 阅读 README.md, **Then** 只描述一套工作流（FastAPI + React + graph DB）
2. **Given** 旧版代码和文档已清理, **When** 阅读 ARCHITECTURE.md, **Then** 不包含 Repository 模式或 Jinja2/HTMX 的描述

---

### Edge Cases

- 如果某个新工作流文件意外 import 了旧版模块 → 必须在移除前修复引用
- `tests/test_graph_store.py` 中的 `test_init_db_rejects_legacy_repository_schema` 测试引用了 `Repository` 类 → 需重写为不依赖 Repository 的独立 schema 验证
- `python-frontmatter` 被新工作流的 `graph/indexer.py` 使用 → 不能移除此依赖
- `var/harnetics.db` 文件本身只是运行时产物，不在 git 中 → 无需删除，但 .gitignore 条目可保留

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系统 MUST 删除所有纯旧版 Python 源文件：`repository.py`, `importer.py`, `retrieval.py`, `drafts.py`, `validation.py`, `app.py`
- **FR-002**: 系统 MUST 删除旧版 Web 层：`web/routes.py`, `web/templates/` 全目录, `web/AGENTS.md`
- **FR-003**: 系统 MUST 删除旧版模型记录：`models/records.py` 及其在 `models/__init__.py` 中的导出
- **FR-004**: 系统 MUST 删除纯旧版测试文件：`test_repository.py`, `test_importer.py`, `test_retrieval.py`, `test_drafts.py`, `test_catalog_routes.py`
- **FR-005**: 系统 MUST 清理 `tests/conftest.py` 中的旧版 fixtures（`temp_db_path`, `temp_app`, `imported_fixture_app` 等）
- **FR-006**: 系统 MUST 清理 `tests/test_app.py` 中对旧版 `create_app()` 的测试
- **FR-007**: 系统 MUST 从 `pyproject.toml` 中移除 `jinja2>=3.1.4` 和 `python-multipart>=0.0.12`
- **FR-008**: 系统 MUST 保留 `python-frontmatter>=1.1.0`（被 `graph/indexer.py` 使用）
- **FR-009**: 系统 MUST 清理 `config.py` 中的 `DEFAULT_REPOSITORY_DB_PATH` 和 `database_path` 配置项
- **FR-010**: 系统 MUST 重写 `tests/test_graph_store.py` 中依赖 `Repository` 类的测试，改为独立的 schema 验证
- **FR-011**: 系统 MUST 更新 README.md 移除双工作流叙事，呈现单一架构
- **FR-012**: 系统 MUST 更新 ARCHITECTURE.md 移除旧版组件描述
- **FR-013**: 系统 MUST 更新根 AGENTS.md 和受影响的 L2 AGENTS.md 文件
- **FR-014**: 所有现存的图谱/API/E2E 测试 MUST 在移除后全部通过

### Key Entities

- **Repository** (被移除): 旧版 SQLite CRUD 层，操作 `harnetics.db`，提供文档/章节/草稿/模板的增删改查
- **Graph Store** (保留): 新版 SQLite CRUD 层，操作 `harnetics-graph.db`，提供文档/章节/边/ICD 参数的增删改查
- **Legacy Services** (被移除): `ImportService`, `RetrievalPlanner`, `DraftService`, `DraftValidator` — 全部依赖 Repository
- **New Services** (保留): `DocumentIndexer`, `ImpactAnalyzer`, `DraftGenerator`, `EvaluatorBus` — 全部依赖 Graph Store

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 移除后源码树中零引用 `repository.py`、`harnetics.db`（Python 代码内）、`Jinja2Templates`、`litellm`
- **SC-002**: `uv run pytest tests/ -q` 全部通过，测试数量 ≥ 移除前的图谱/API 测试数
- **SC-003**: `cd frontend && npm run build` 成功
- **SC-004**: `pyproject.toml` 中不包含 `jinja2` 或 `python-multipart`
- **SC-005**: README.md 中不包含"旧版"、"兼容保留"、"不要混用同一 SQLite 文件"等措辞
- **SC-006**: 所有受影响的 AGENTS.md 文件已同步更新

## Assumptions

- 新工作流（api/app.py + graph store + React SPA）已完全覆盖旧版的所有核心功能
- `var/harnetics.db` 是运行时产物不在 git 中，无需物理删除
- `python-frontmatter` 是新旧工作流共享的唯一依赖，必须保留
- CLI 命令（`init`, `ingest`, `serve`）全部走新工作流，不依赖旧版代码
- 开源发布不需要向后兼容旧版数据库的迁移工具
