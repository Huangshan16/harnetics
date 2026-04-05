<!--
[INPUT]: 依赖 docs/product-specs/mvp-prd.md、ARCHITECTURE.md 与本轮 brainstorming 确认的范围决策
[OUTPUT]: 对外提供 Harnetics v1 最小可交付闭环的正式设计 spec
[POS]: docs/superpowers/specs 的设计基线文档，作为后续 writing-plans 的直接输入
[PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md
-->

# Harnetics v1 最小可交付闭环设计 Spec

日期：2026-04-05
来源：基于 `docs/product-specs/mvp-prd.md` 的 brainstorming 收敛结果

## 1. 设计目标

本 spec 定义 Harnetics 第一阶段的最小可交付闭环：

1. 导入受控文档
2. 浏览与检索文档库
3. 基于候选来源和模板生成带引注草稿
4. 在 Web 内进行轻编辑
5. 导出 Markdown 交付工程师继续修改

该阶段目标是 `可交付`，不是仅做演示。系统必须优先保证草稿结构稳定、引用可核对、冲突可见、导出可用。

## 2. 已确认决策

### 2.1 范围

纳入：
- 文档导入
- 文档库浏览与搜索
- 混合式候选选择
- 带引注草稿生成
- Web 内轻编辑
- Markdown 导出
- 生成前后校验

排除：
- 自动影响分析
- 文档图谱
- 仪表盘
- 自由格式文档理解
- 完整富文本编辑器
- 多用户协作和权限系统

### 2.2 交互和风险策略

- 草稿修改位置：Web 内轻编辑
- 生成入口：混合式，先给候选来源与模板，再由用户确认后生成
- 冲突策略：继续生成，但用强警告显式标记冲突段落和过期引用
- 输入策略：受控输入，仅接受带明确元数据的 Markdown/YAML；格式不合格直接拒绝导入

## 3. 系统边界与组件

`v1` 只围绕一条数据闭环设计，不把影响分析和图谱预埋进主流程。

### 3.1 Import Service

职责：
- 接收 Markdown/YAML
- 校验必填元数据和结构
- 解析为 `Document` 与 `Section`
- 将模板文档识别并入 `Template`

不负责：
- 草稿生成
- UI 级编辑
- 模型提示词拼装之外的业务决策

### 3.2 Document Catalog

职责：
- 文档列表展示
- 元数据筛选
- 标题与正文搜索
- 文档详情与 section 查看

不负责：
- 草稿状态管理
- 原始文件解析

### 3.3 Retrieval Planner

职责：
- 接收主题、部门、文档类型、系统层级
- 返回候选上游文档和模板
- 在生成前暴露选择面，而不是直接替用户决定来源

### 3.4 Draft Workspace

职责：
- 发起草稿生成
- 展示正文、引用和告警
- 支持轻编辑
- 导出 Markdown

不负责：
- 原始文档入库
- 文档解析和目录治理

### 3.5 Validation Layer

职责：
- 导入前校验输入
- 生成后校验引用完整性、模板覆盖和版本冲突
- 统一输出 `通过 / 告警 / 阻断`

## 4. 数据模型

`v1` 只保留支撑闭环所需的核心对象。

### 4.1 Document

字段：
- `doc_id`
- `title`
- `department`
- `doc_type`
- `system_level`
- `engineering_phase`
- `version`
- `status`
- `source_path`
- `imported_at`

职责：承载文档级元数据，是列表、筛选和版本识别的基本单位。

### 4.2 Section

字段：
- `section_id`
- `document_id`
- `heading`
- `level`
- `sequence`
- `content`
- `trace_refs`

职责：作为最小检索和引用单元。

### 4.3 Template

字段：
- `template_id`
- `document_id`
- `name`
- `required_sections`
- `structure`

职责：提供草稿骨架。模板单独建模，不与普通文档混放。

### 4.4 Draft

字段：
- `draft_id`
- `topic`
- `department`
- `target_doc_type`
- `target_system_level`
- `status`
- `content_markdown`
- `exported_at`

职责：表示一次生成任务当前可编辑的结果。

### 4.5 Citation

字段：
- `citation_id`
- `draft_id`
- `draft_anchor`
- `section_id`
- `quote_excerpt`

职责：将草稿片段和源 `Section` 连接起来。`Citation` 是一等对象，不能只靠正文内嵌标记替代。

### 4.6 ValidationIssue

字段：
- `issue_id`
- `owner_type`
- `owner_id`
- `severity`
- `message`
- `source_refs`

职责：记录导入或生成后的问题，用于驱动告警和阻断。

### 4.7 GenerationRun

字段：
- `run_id`
- `draft_id`
- `selected_document_ids`
- `selected_template_id`
- `status`
- `duration_ms`
- `input_summary`

职责：保存一次生成过程的执行上下文，服务复现和排错。

## 5. 主数据流

### 5.1 导入流

1. 用户上传 Markdown/YAML
2. `Import Service` 校验元数据和结构
3. 通过则写入 `Document + Section`
4. 若文档为模板，则同时写入 `Template`
5. 失败则返回拒绝原因，不入库

### 5.2 浏览流

1. `Document Catalog` 基于 `Document` 提供筛选和搜索
2. 文档详情页显示元数据和 section 列表；`v1` 不要求展示完整文档关系
3. 文档库只消费结构化数据，不再碰原始文件解析

### 5.3 生成流

1. 用户输入主题、部门、目标文档类型、系统层级
2. `Retrieval Planner` 返回候选文档和模板
3. 用户确认候选后发起 `GenerationRun`
4. 系统基于模板骨架和候选 `Section` 生成 `Draft`
5. `Validation Layer` 生成 `Citation + ValidationIssue`
6. 草稿进入可编辑状态

### 5.4 导出流

1. 用户在 `Draft Workspace` 内轻编辑
2. 系统保留引用和告警信息
3. 导出当前 `Draft` 版本为 Markdown
4. 导出不回写来源文档

## 6. 页面与交互状态

### 6.1 文档库页

用途：
- 上传文档
- 过滤、搜索和查看详情

必须具备：
- 上传入口
- 部门/类型/层级筛选
- 文档列表
- 文档详情查看

### 6.2 草稿创建页

用途：
- 输入目标主题
- 选择部门、文档类型、系统层级
- 查看并确认候选来源和模板

关键约束：
- 必须是“两步式”：先检索候选，再确认生成
- 不允许“一提交就生成”

### 6.3 草稿工作台

用途：
- 查看生成草稿
- 轻编辑标题、段落和列表
- 查看引用来源和告警
- 导出 Markdown

关键布局：
- 正文区
- 引用与告警侧栏
- 导出入口

### 6.4 状态机

导入：
- `待上传 -> 校验中 -> 已入库 / 被拒绝`

候选检索：
- `待输入 -> 检索中 -> 候选已就绪 / 无结果`

草稿生成：
- `生成中 -> 校验中 -> 可编辑 / 失败`

草稿编辑：
- `只读初稿 -> 已编辑 -> 已导出`

## 7. 错误处理与校验规则

### 7.1 导入校验

阻断条件：
- 缺少必填元数据
- `doc_id + version` 冲突
- Markdown/YAML 结构不符合受控格式
- 模板文档缺少可识别的必填章节

策略：直接拒绝导入，不进行自动猜测或模糊修复。

### 7.2 生成后校验

规则：
- 每个生成段落或列表项必须至少挂一个 `Citation`
- 引用了旧版本来源时，标为 `告警`
- 同一关键参数在候选来源中出现冲突时，标为 `告警`
- 模板必填章节缺失时，标为 `阻断`

### 7.3 告警呈现

要求：
- 冲突段落在正文内高亮
- 侧栏同步列出原因和来源
- 不允许只在页面底部给摘要

### 7.4 失败恢复

要求：
- 候选为空时，不生成草稿，提示改主题或放宽筛选
- 生成失败时，保留用户输入和候选选择，支持重试
- 导出失败时，不丢失已编辑正文

## 8. 测试策略

### 8.1 解析测试

使用 `fixtures/` 验证：
- Markdown 文档可稳定解析为 `Document + Section`
- YAML ICD 可稳定解析为 `Document + Section`
- 模板可识别为 `Template`

### 8.2 检索测试

验证：
- 给定主题和筛选条件，能返回合理候选集合
- 候选结果包含模板和来源文档两类对象

### 8.3 生成契约测试

验证：
- 草稿遵守模板骨架
- 每个生成段落带引用
- 导出结果为有效 Markdown

### 8.4 校验测试

验证：
- `fixtures/test_plans/DOC-TST-003.md` 这类过期引用样本能打出强告警
- 冲突参数能被定位到具体来源 section

### 8.5 端到端测试

验证：
- 从导入样本到导出草稿的 happy path 完整打通
- 失败路径可恢复：坏元数据、无候选、模板缺章节、生成异常

## 9. 明确不做

`v1` 不做以下内容：

- PDF、DOCX 等非受控格式导入
- 自动猜元数据
- 完整富文本编辑器
- 自动影响分析
- 文档图谱
- 仪表盘
- 多用户协作
- 权限系统
- 审计后台
- 让模型自动决定冲突的最终版本

## 10. 验收标准

只有满足以下条件，`v1` 才算达到“可交付”目标：

1. 受控 Markdown/YAML 能稳定入库
2. 用户能在文档库中查到来源文档和 section
3. 系统能先返回候选来源和模板，再执行生成
4. 生成的草稿遵守模板骨架
5. 草稿每个生成段落或列表项都可追溯到至少一个来源 `Section`
6. 版本冲突和过期引用会以强告警形式显式展示
7. 用户可在 Web 内进行轻编辑
8. 用户可导出 Markdown 并继续在外部工具中修改

## 11. 实现假设

为避免计划阶段再次发散，本 spec 固定以下假设：

- 系统部署形态仍为本地 Web 应用
- 原始导入文件保留在本地文件系统
- 草稿导出格式仅为 Markdown
- `v1` 的“关系”只要求能支持引用回跳和告警定位，不要求完整知识图谱

这份 spec 是后续 `writing-plans` 的输入基线；后续计划若要偏离这里的边界，必须先回改本文件。
