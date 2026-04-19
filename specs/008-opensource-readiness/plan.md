# Implementation Plan: Open-Source Readiness

**Branch**: `008-opensource-readiness` | **Date**: 2026-04-19 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/008-opensource-readiness/spec.md`

## Summary

将 Harnetics 从内部原型项目重构为专业 GitHub 开源项目。核心交付：根目录法律/社区文件（LICENSE、CONTRIBUTING、CODE_OF_CONDUCT）、GitHub Actions CI pipeline、Issue/PR 模板、面向国际社区的 README 重写、CHANGELOG v0.1.0、pyproject.toml 元数据补全、开源运营最佳实践文档。

## Technical Context

**Language/Version**: Python 3.13 + TypeScript 5.7 (existing)
**Primary Dependencies**: FastAPI, React 18, Vite 6, pytest, shadcn/ui (existing, no new runtime deps)
**Storage**: SQLite + ChromaDB (existing, no change)
**Testing**: pytest (backend) + Vite build (frontend) — CI 需覆盖两者
**Target Platform**: GitHub (hosting) + GitHub Actions (CI)
**Project Type**: web-service (Python backend + React SPA)
**Performance Goals**: CI pipeline < 5 min
**Constraints**: GitHub Actions free tier, no secrets required for basic CI
**Scale/Scope**: ~50 files to create/modify, 0 runtime code changes

## Constitution Check

*GATE: Pass — 本特性纯文档与配置变更，不触及核心代码架构。*

- ✅ 无新运行时依赖
- ✅ 不改变模块边界
- ✅ 文件数变更在 GEB 协议约束内（每目录 ≤8 文件）
- ✅ 所有新目录附带 AGENTS.md

## Project Structure

### Documentation (this feature)

```text
specs/008-opensource-readiness/
├── spec.md
├── plan.md              # This file
├── tasks.md             # Task breakdown
└── checklists/
    └── requirements.md
```

### Source Code (repository root) — 新增/变更文件

```text
# Root-level files (新增)
LICENSE                        # Apache 2.0
CONTRIBUTING.md                # 贡献者指南
CODE_OF_CONDUCT.md             # Contributor Covenant v2.1
CHANGELOG.md                   # v0.1.0 release notes

# .github/ directory (新增)
.github/
├── SECURITY.md                # 安全漏洞报告流程
├── PULL_REQUEST_TEMPLATE.md   # PR 模板
├── ISSUE_TEMPLATE/
│   ├── bug_report.yml         # Bug 报告模板 (YAML forms)
│   └── feature_request.yml    # 功能请求模板 (YAML forms)
└── workflows/
    └── ci.yml                 # GitHub Actions CI pipeline

# Existing files (修改)
README.md                      # 重写为开源社区标准格式
pyproject.toml                 # 补全元数据，清理死依赖
AGENTS.md                      # 更新变更日志

# Documentation (新增)
docs/opensource-playbook.md    # 开源运营最佳实践指南
```

**Structure Decision**: 遵循 GitHub Community Standards 推荐结构。所有社区文件放根目录，GitHub 特定文件放 `.github/`。不创建新的代码目录。

## Complexity Tracking

> 无违规项——本特性不引入架构复杂度。
