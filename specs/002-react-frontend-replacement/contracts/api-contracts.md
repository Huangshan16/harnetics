# API Contracts: Frontend ↔ Backend

## 已有端点（无需修改）

| Method | Path | 用途 |
|--------|------|------|
| GET | /api/documents | 文档列表（支持 department/doc_type/system_level/status/q 筛选） |
| GET | /api/documents/{doc_id} | 文档详情（含 sections/upstream/downstream/icd_parameters） |
| POST | /api/documents/upload | 上传文档 |
| DELETE | /api/documents/{doc_id} | 删除文档 |
| POST | /api/draft/generate | 生成草稿 |
| GET | /api/draft/{draft_id} | 草稿详情 |
| GET | /api/drafts | 草稿列表 |
| GET | /api/draft/{draft_id}/export | 导出草稿 Markdown |
| POST | /api/impact/analyze | 触发影响分析 |
| GET | /api/impact/{report_id} | 影响报告详情 |
| GET | /api/graph | 全量图谱 (vis-network 格式) |
| GET | /api/graph/upstream/{doc_id} | 上游文档 |
| GET | /api/graph/downstream/{doc_id} | 下游文档 |
| GET | /api/graph/stale | 陈旧引用 |
| POST | /api/evaluate/{draft_id} | 运行评估 |
| GET | /api/evaluate/results/{draft_id} | 评估结果 |
| GET | /health | 健康检查 |

## 需新增端点

### GET /api/graph/edges

返回原始边列表，供前端 SVG 图谱渲染。

```json
{
  "edges": [
    { "edge_id": 1, "source_doc_id": "DOC-SYS-001", "target_doc_id": "DOC-ICD-001", "relation": "derived_from", "confidence": 1.0 }
  ]
}
```

### GET /api/impact

列出所有影响分析报告摘要。

```json
{
  "reports": [
    { "report_id": "rpt-xxx", "trigger_doc_id": "DOC-SYS-001", "old_version": "v3.0", "new_version": "v3.1", "summary": "...", "created_at": "..." }
  ]
}
```

### GET /api/dashboard/stats

返回仪表盘统计数据。

```json
{
  "total_documents": 10,
  "total_edges": 27,
  "stale_references": 3
}
```

## SPA Fallback

`create_api_app()` 需在所有 API 路由之后添加 catch-all 路由：
- 非 `/api/*` 且非静态文件的 GET 请求 → 返回 `frontend/dist/index.html`
- 仅在 `frontend/dist/index.html` 存在时启用
