# Data Model: Remove Legacy Repository Workflow

**Feature**: 007-remove-legacy-workflow  
**Date**: 2026-04-19

## 概述

本特性不引入新的数据模型。以下记录被移除的旧版实体和保留的新版实体，确保边界清晰。

## 被移除的实体（旧版 Repository schema — harnetics.db）

| 实体 | 表名 | 描述 | 移除原因 |
|------|------|------|----------|
| DocumentRecord | documents | 文档元数据（doc_id, title, doc_type, version, status） | 被 graph store 的 documents 表替代 |
| SectionRecord | sections | 文档章节（section_id, doc_id, heading, content, level） | 被 graph store 的 sections 表替代 |
| TemplateRecord | templates | 文档模板（template_id, name, structure） | 新工作流不使用模板概念 |
| DraftRecord | drafts | 草稿（draft_id, template_id, title, content, status） | 被 graph store 的 drafts 表替代 |
| CitationRecord | citations | 引注（citation_id, draft_id, source_doc_id, quote） | 被 graph store 的 draft_citations 表替代 |
| ValidationIssueRecord | validation_issues | 校验问题（issue_id, draft_id, severity, message） | 被 evaluator bus + eval_results 替代 |
| GenerationRunRecord | generation_runs | 生成运行记录（run_id, draft_id, model, prompt） | 新工作流内嵌于 draft 生成流程 |

## 保留的实体（新版 Graph Store schema — harnetics-graph.db）

| 实体 | 表名 | 状态 |
|------|------|------|
| Document | documents | ✅ 不受影响 |
| Section | sections | ✅ 不受影响 |
| Edge | edges | ✅ 不受影响 |
| ICDParameter | icd_parameters | ✅ 不受影响 |
| Draft | drafts | ✅ 不受影响 |
| DraftCitation | draft_citations | ✅ 不受影响 |
| EvalResult | eval_results | ✅ 不受影响 |
| ImpactReport | impact_reports | ✅ 不受影响 |

## 被移除的 Python 类

| 类名 | 文件 | 依赖 |
|------|------|------|
| Repository | repository.py | sqlite3 |
| ImportService | importer.py | Repository, frontmatter |
| RetrievalPlanner | retrieval.py | Repository |
| DraftService | drafts.py | Repository, LocalLlmClient |
| DraftValidator | validation.py | Repository |
| DocumentRecord, SectionRecord, etc. | models/records.py | dataclasses |
