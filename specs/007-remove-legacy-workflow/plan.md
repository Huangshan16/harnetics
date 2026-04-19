# Implementation Plan: Remove Legacy Repository Workflow

**Branch**: `007-remove-legacy-workflow` | **Date**: 2026-04-19 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/007-remove-legacy-workflow/spec.md`

## Summary

系统化移除旧版 Repository 工作流——包括 Jinja2/HTMX Web 层、Repository CRUD 层、旧版服务（ImportService/RetrievalPlanner/DraftService/DraftValidator）、旧版 app factory、对应测试和依赖——为开源发布呈现清晰的单一架构（FastAPI + React SPA + SQLite graph store）。

本质上这是一次减法手术：删除 ~15 个文件，修改 ~8 个文件，移除 2 个 pyproject 依赖。零新功能，零新模块。

## Technical Context

**Language/Version**: Python 3.13 + TypeScript 5.7  
**Primary Dependencies**: FastAPI, React 18, Vite 6, shadcn/ui, Tailwind v4  
**Storage**: SQLite (`var/harnetics-graph.db`) + ChromaDB  
**Testing**: pytest  
**Target Platform**: Linux/macOS/Windows (cross-platform)  
**Project Type**: web-service (FastAPI backend + React SPA)  
**Performance Goals**: N/A（纯减法，不影响性能）  
**Constraints**: 移除后全部现有测试必须通过  
**Scale/Scope**: 删除 ~15 文件、修改 ~8 文件、移除 2 个依赖

## Constitution Check

*Constitution 未初始化（空模板）— 无 gates 需要检查。*

## Project Structure

### Documentation (this feature)

```text
specs/007-remove-legacy-workflow/
├── plan.md              # 本文件
├── research.md          # Phase 0: 旧版代码审计报告
├── data-model.md        # Phase 1: 被移除实体清单
├── quickstart.md        # Phase 1: 移除验证快速指南
└── tasks.md             # Phase 2: 实施任务列表
```

### Source Code — 移除前后对比

```text
# 移除前
src/harnetics/
├── __init__.py
├── AGENTS.md
├── app.py                 ← DELETE (旧版 app factory)
├── config.py              ← EDIT (移除 legacy DB 配置)
├── drafts.py              ← DELETE (旧版草稿服务)
├── importer.py            ← DELETE (旧版导入服务)
├── models.py              ← CHECK (可能是旧版模型)
├── repository.py          ← DELETE (旧版 CRUD 层)
├── retrieval.py           ← DELETE (旧版检索服务)
├── validation.py          ← DELETE (旧版校验器)
├── web/
│   ├── AGENTS.md          ← DELETE
│   ├── routes.py          ← DELETE (Jinja2 路由)
│   └── templates/         ← DELETE (全目录)
├── api/                   ✅ KEEP
├── cli/                   ✅ KEEP
├── engine/                ✅ KEEP
├── graph/                 ✅ KEEP
├── llm/                   ✅ KEEP
└── models/                ← EDIT (移除 records.py)

# 移除后
src/harnetics/
├── __init__.py
├── AGENTS.md              ← UPDATE
├── config.py              ← CLEANED
├── api/                   ✅ UNCHANGED
├── cli/                   ✅ UNCHANGED
├── engine/                ✅ UNCHANGED
├── graph/                 ✅ UNCHANGED
├── llm/                   ✅ UNCHANGED
└── models/                ← CLEANED

tests/
├── conftest.py            ← EDIT (移除旧版 fixtures)
├── test_app.py            ← EDIT (移除旧版 app 测试)
├── test_graph_store.py    ← EDIT (重写 Repository 依赖测试)
├── test_catalog_routes.py ← DELETE
├── test_drafts.py         ← DELETE
├── test_importer.py       ← DELETE
├── test_repository.py     ← DELETE
└── test_retrieval.py      ← DELETE
```

**Structure Decision**: Web application structure (backend/ Python + frontend/ React)。移除后源码树只保留 api/cli/engine/graph/llm/models 六个子包——每个包都服务于图谱工作流。

## Complexity Tracking

无 constitution 违规需要记录。本特性是纯减法，不增加任何复杂度。
