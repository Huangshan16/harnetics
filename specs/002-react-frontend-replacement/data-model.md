# Data Model: React Frontend Replacement

**Branch**: `002-react-frontend-replacement` | **Date**: 2026-04-11

## TypeScript 接口定义

前端 TypeScript 接口需与后端 API JSON 响应结构对齐。

### Document

```typescript
interface Document {
  doc_id: string
  title: string
  doc_type: string
  department: string
  system_level: string
  engineering_phase: string
  version: string
  status: 'Draft' | 'UnderReview' | 'Approved' | 'Superseded'
  created_at: string
  updated_at: string
}
```

后端端点: `GET /api/documents` → `{ total, page, per_page, documents: Document[] }`

### Section

```typescript
interface Section {
  section_id: string
  doc_id: string
  heading: string
  content: string
  level: number
  order_index: number
}
```

后端端点: `GET /api/documents/{doc_id}` → 含 `sections: Section[]`

### DocumentEdge

```typescript
interface DocumentEdge {
  edge_id: number
  source_doc_id: string
  target_doc_id: string
  relation: 'traces_to' | 'references' | 'derived_from' | 'constrained_by' | 'supersedes' | 'impacts'
  confidence: number
}
```

后端端点: `GET /api/graph` → vis-network 格式; 需补充 `GET /api/graph/edges` → `DocumentEdge[]`

### Draft

```typescript
interface Draft {
  draft_id: string
  status: string
  content_md: string
  citations: Citation[]
  conflicts: Conflict[]
  eval_results: EvalResult[]
  generated_by: string
  created_at: string
}

interface Citation {
  source_doc_id: string
  source_section_id: string
  quote: string
  confidence: number
}

interface Conflict {
  doc_a_id: string
  doc_b_id: string
  description: string
  severity: string
}

interface EvalResult {
  evaluator_id: string
  name: string
  status: string
  level: string
  detail: string
  locations: string[]
}
```

后端端点: `POST /api/draft/generate`, `GET /api/draft/{id}`, `GET /api/drafts`

### ImpactReport

```typescript
interface ImpactReport {
  report_id: string
  trigger_doc_id: string
  old_version: string
  new_version: string
  summary: string
  changed_sections: ChangedSection[]
  impacted_docs: ImpactedDoc[]
  created_at: string
}

interface ChangedSection {
  section_id: string
  heading: string
  change_type: string
  summary: string
}

interface ImpactedDoc {
  doc_id: string
  title: string
  relation: string
  affected_sections: string[]
  severity: string
}
```

后端端点: `POST /api/impact/analyze`, `GET /api/impact/{id}`

### DashboardStats (需新增后端端点)

```typescript
interface DashboardStats {
  total_documents: number
  total_edges: number
  stale_references: number
}
```

后端端点: `GET /api/dashboard/stats` (待新增)
