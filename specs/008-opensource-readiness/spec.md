# Feature Specification: Open-Source Readiness

**Feature Branch**: `008-opensource-readiness`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: 基于 MVP 文档与现有开发进度，将项目梳理为专业 GitHub 开源项目架构，补全文档，输出开源最佳实践指南

## User Scenarios & Testing

### User Story 1 - 项目第一印象与可贡献性 (Priority: P1)

一个开发者在 GitHub 上发现 Harnetics，进入仓库首页。他需要在 30 秒内理解项目做什么、为什么有价值、如何快速上手。他点进 README，看到清晰的项目定位、功能截图/示意、安装步骤、许可证和贡献入口。

**Why this priority**: 开源项目的第一次接触决定 90% 的留存。README 是门面，LICENSE 是法律基础，CONTRIBUTING 是参与入口——三者缺一则项目不可贡献。

**Independent Test**: 一个从未见过本项目的开发者，仅凭 README 内容能在 10 分钟内完成安装并看到运行画面。

**Acceptance Scenarios**:

1. **Given** 开发者访问 GitHub 仓库, **When** 查看 README, **Then** 能在 30 秒内理解项目定位与核心价值
2. **Given** 开发者想贡献代码, **When** 查看根目录, **Then** 找到 LICENSE、CONTRIBUTING.md、CODE_OF_CONDUCT.md
3. **Given** 开发者 clone 项目, **When** 按 README 步骤操作, **Then** 10 分钟内完成环境搭建并通过冒烟测试

---

### User Story 2 - CI/CD 自动化质量门禁 (Priority: P2)

维护者收到一个 Pull Request，GitHub Actions 自动运行 pytest 后端测试和 npm build 前端构建。CI 绿灯后维护者才开始 review。

**Why this priority**: 没有 CI 的开源项目无法规模化接受贡献——每个 PR 都需要人工跑测试，效率极低且不可信。

**Independent Test**: 推送任意分支触发 CI pipeline，pytest 和 frontend build 均自动运行并报告状态。

**Acceptance Scenarios**:

1. **Given** 贡献者提交 PR, **When** GitHub Actions 触发, **Then** 自动运行 pytest 并报告 pass/fail
2. **Given** PR 涉及前端改动, **When** CI 运行, **Then** 自动执行 npm run build 验证编译通过
3. **Given** CI 失败, **When** 维护者查看, **Then** 能从日志快速定位失败原因

---

### User Story 3 - 规范化的社区协作流程 (Priority: P3)

一个贡献者想报告 bug 或提出新功能。他在 Issues 页面看到结构化的 issue 模板（Bug Report / Feature Request），填写后自动打上标签。维护者通过 PR 模板确保每个贡献都有上下文。

**Why this priority**: 模板化的 issue/PR 流程降低沟通成本，但依赖 P1/P2 先就位。

**Independent Test**: 创建 issue 时自动弹出模板选择器，Bug Report 和 Feature Request 各有结构化表单。

**Acceptance Scenarios**:

1. **Given** 用户点击 New Issue, **When** 选择模板, **Then** 看到 Bug Report / Feature Request 两种模板
2. **Given** 贡献者提交 PR, **When** 创建 PR, **Then** 看到包含 checklist 的 PR 模板
3. **Given** 维护者管理项目, **When** 查看 SECURITY.md, **Then** 找到漏洞报告流程

---

### Edge Cases

- 贡献者在 Windows/macOS/Linux 不同平台上 clone 并构建项目——README 需覆盖跨平台差异
- 贡献者不熟悉 uv 包管理器——需提供 pip fallback 说明
- 贡献者只想改前端不碰后端——CONTRIBUTING 需说明独立开发路径

## Requirements

### Functional Requirements

- **FR-001**: 项目根目录 MUST 包含 LICENSE 文件（Apache 2.0）
- **FR-002**: 项目根目录 MUST 包含 CONTRIBUTING.md，说明分支策略、代码规范、PR 流程、开发环境搭建
- **FR-003**: 项目根目录 MUST 包含 CODE_OF_CONDUCT.md（Contributor Covenant v2.1）
- **FR-004**: .github/ 目录 MUST 包含 SECURITY.md，说明安全漏洞报告流程
- **FR-005**: .github/workflows/ MUST 包含 CI workflow，覆盖 pytest + frontend build
- **FR-006**: .github/ISSUE_TEMPLATE/ MUST 包含 Bug Report 和 Feature Request 模板
- **FR-007**: .github/ MUST 包含 PULL_REQUEST_TEMPLATE.md
- **FR-008**: README.md MUST 重写为面向开源社区的专业格式（英文为主、中文补充），包含 badges、架构图、快速上手、API 概览
- **FR-009**: 项目根目录 MUST 包含 CHANGELOG.md，记录 v0.1.0 首次发布的变更
- **FR-010**: pyproject.toml MUST 清理死依赖（jinja2），补全项目元数据（description、authors、urls、classifiers）
- **FR-011**: 项目 MUST 输出一份 docs/opensource-playbook.md 开源运营最佳实践文档

### Key Entities

- **Repository Metadata**: LICENSE、README、CONTRIBUTING、CODE_OF_CONDUCT、SECURITY——构成项目的"法律与社区契约层"
- **CI Pipeline**: GitHub Actions workflow 定义自动化质量保障
- **Issue/PR Templates**: 标准化社区交互的入口模板
- **Changelog**: 版本发布历史的权威记录

## Success Criteria

### Measurable Outcomes

- **SC-001**: 新开发者仅凭 README 能在 10 分钟内完成项目安装与冒烟测试
- **SC-002**: 每次 PR 自动触发 CI 并在 5 分钟内返回测试结果
- **SC-003**: 项目通过 GitHub Community Standards 检查（https://github.com/{owner}/{repo}/community）100% 绿灯
- **SC-004**: CONTRIBUTING.md 覆盖 clone → 分支 → 开发 → 测试 → PR 全流程
- **SC-005**: 开源最佳实践文档覆盖从 v0.1.0 发布到社区运营的完整路径

## Assumptions

- 项目采用 Apache 2.0 许可证（适合商业友好的开源项目，允许专利授权）
- 英文为项目主语言（国际化开源社区标准），中文作为补充说明
- GitHub 作为唯一代码托管平台
- CI 使用 GitHub Actions（免费 tier 足够覆盖当前规模）
- v0.1.0 作为首次公开发布版本号
