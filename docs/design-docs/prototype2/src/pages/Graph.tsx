import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { documents, graphEdges } from '@/data/mock'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

// ─── Node layout ─────────────────────────────────────────────────────────────
const nodePositions: Record<string, { x: number; y: number; r: number }> = {
  'DOC-ICD-001': { x: 420, y: 260, r: 36 },   // center — hub node
  'DOC-SYS-001': { x: 200, y: 130, r: 28 },   // top-left
  'DOC-OVR-001': { x: 420, y:  75, r: 26 },   // top-center
  'DOC-DES-001': { x: 640, y: 130, r: 28 },   // top-right
  'DOC-TST-002': { x: 155, y: 285, r: 26 },   // mid-left
  'DOC-FMA-001': { x: 680, y: 285, r: 26 },   // mid-right
  'DOC-QAP-001': { x: 245, y: 420, r: 24 },   // bottom-left
  'DOC-TPL-001': { x: 590, y: 420, r: 24 },   // bottom-right
}

const deptColor: Record<string, string> = {
  '技术负责人': '#7c3aed',
  '系统工程部': '#2563eb',
  '动力系统部': '#059669',
  '质量与可靠性部': '#d97706',
  '试验与验证部': '#7c3aed',
  '总体设计部': '#db2777',
}

const relationColors: Record<string, string> = {
  derived_from: '#7c3aed',
  references: '#2563eb',
  constrained_by: '#d97706',
  traces_to: '#059669',
}

const relationLabels: Record<string, string> = {
  derived_from: '派生自',
  references: '引用',
  constrained_by: '约束于',
  traces_to: '追溯至',
}

const departments = ['全部', ...Array.from(new Set(documents.map((d) => d.department)))]

// Compute arrow head angle
function arrowAngle(sx: number, sy: number, tx: number, ty: number) {
  return Math.atan2(ty - sy, tx - sx) * (180 / Math.PI)
}

// Trim edge endpoints to node radii
function trimEdge(
  sx: number, sy: number, sr: number,
  tx: number, ty: number, tr: number
) {
  const dx = tx - sx; const dy = ty - sy
  const len = Math.sqrt(dx * dx + dy * dy)
  const ux = dx / len; const uy = dy / len
  return {
    x1: sx + ux * (sr + 2), y1: sy + uy * (sr + 2),
    x2: tx - ux * (tr + 6), y2: ty - uy * (tr + 6),
  }
}

export default function Graph() {
  const navigate = useNavigate()
  const [hovered, setHovered] = useState<string | null>(null)
  const [deptFilter, setDeptFilter] = useState('全部')

  const visibleDocs = deptFilter === '全部'
    ? documents
    : documents.filter((d) => d.department === deptFilter)
  const visibleIds = new Set(visibleDocs.map((d) => d.doc_id))

  const visibleEdges = graphEdges.filter(
    (e) => visibleIds.has(e.source) && visibleIds.has(e.target)
  )

  const hoveredDoc = hovered ? documents.find((d) => d.doc_id === hovered) : null

  return (
    <div className="container mx-auto max-w-screen-xl px-4 py-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">文档图谱</h1>
        <p className="mt-1 text-muted-foreground">可视化文档间的派生、引用与约束关系</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
        {/* Graph canvas */}
        <Card className="lg:col-span-3 overflow-hidden">
          <CardContent className="p-0">
            <svg
              viewBox="0 0 840 520"
              width="100%"
              className="block"
              style={{ minHeight: 360 }}
            >
              {/* Arrow markers */}
              <defs>
                {Object.entries(relationColors).map(([rel, color]) => (
                  <marker
                    key={rel}
                    id={`arrow-${rel}`}
                    markerWidth="8" markerHeight="8"
                    refX="6" refY="3"
                    orient="auto"
                  >
                    <path d="M0,0 L0,6 L8,3 z" fill={color} />
                  </marker>
                ))}
              </defs>

              {/* Edges */}
              {visibleEdges.map((e, i) => {
                const sp = nodePositions[e.source]
                const tp = nodePositions[e.target]
                if (!sp || !tp) return null
                const { x1, y1, x2, y2 } = trimEdge(sp.x, sp.y, sp.r, tp.x, tp.y, tp.r)
                const color = relationColors[e.relation] ?? '#888'
                return (
                  <line
                    key={i}
                    x1={x1} y1={y1} x2={x2} y2={y2}
                    stroke={color}
                    strokeWidth={hovered === e.source || hovered === e.target ? 2.5 : 1.5}
                    strokeOpacity={hovered && hovered !== e.source && hovered !== e.target ? 0.2 : 0.75}
                    markerEnd={`url(#arrow-${e.relation})`}
                  />
                )
              })}

              {/* Nodes */}
              {documents.map((doc) => {
                const pos = nodePositions[doc.doc_id]
                if (!pos || !visibleIds.has(doc.doc_id)) return null
                const color = deptColor[doc.department] ?? '#6b7280'
                const isHub = doc.doc_id === 'DOC-ICD-001'
                const isHovered = hovered === doc.doc_id
                const isGhosted = hovered !== null && !isHovered
                return (
                  <g
                    key={doc.doc_id}
                    style={{ cursor: 'pointer', opacity: isGhosted ? 0.3 : 1, transition: 'opacity 0.15s' }}
                    onClick={() => navigate(`/documents/${doc.id}`)}
                    onMouseEnter={() => setHovered(doc.doc_id)}
                    onMouseLeave={() => setHovered(null)}
                  >
                    {/* Glow for hub or hovered */}
                    {(isHub || isHovered) && (
                      <circle cx={pos.x} cy={pos.y} r={pos.r + 8} fill={color} opacity={0.12} />
                    )}
                    <circle
                      cx={pos.x} cy={pos.y} r={pos.r}
                      fill={isHub ? color : 'white'}
                      stroke={color}
                      strokeWidth={isHub ? 0 : 2.5}
                      filter={isHovered ? 'drop-shadow(0 2px 6px rgba(0,0,0,0.25))' : undefined}
                    />
                    {/* Label inside hub node */}
                    {isHub && (
                      <text x={pos.x} y={pos.y - 4} textAnchor="middle" fill="white" fontSize={9} fontWeight="bold">
                        ICD
                      </text>
                    )}
                    {isHub && (
                      <text x={pos.x} y={pos.y + 7} textAnchor="middle" fill="white" fontSize={8}>
                        001
                      </text>
                    )}
                    {/* Label below non-hub nodes */}
                    {!isHub && (
                      <text x={pos.x} y={pos.y + pos.r + 14} textAnchor="middle" fill={color} fontSize={9} fontWeight="600">
                        {doc.doc_id.replace('DOC-', '')}
                      </text>
                    )}
                  </g>
                )
              })}
            </svg>
          </CardContent>
        </Card>

        {/* Sidebar: filters + legend + tooltip */}
        <div className="space-y-4">
          {/* Dept filter */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">按部门筛选</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {departments.map((d) => (
                <button
                  key={d}
                  onClick={() => setDeptFilter(d)}
                  className={`px-2.5 py-1 rounded-full text-xs font-medium transition-colors border ${
                    deptFilter === d
                      ? 'bg-primary text-primary-foreground border-primary'
                      : 'border-border text-muted-foreground hover:bg-accent'
                  }`}
                >
                  {d === '全部' ? `全部 (${documents.length})` : d}
                </button>
              ))}
            </CardContent>
          </Card>

          {/* Legend */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">关系类型图例</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {Object.entries(relationColors).map(([rel, color]) => (
                <div key={rel} className="flex items-center gap-2 text-sm">
                  <div className="h-0.5 w-8 rounded" style={{ backgroundColor: color }} />
                  <span className="text-muted-foreground">{relationLabels[rel]}</span>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Node tooltip */}
          {hoveredDoc && (
            <Card className="border-primary/50">
              <CardHeader className="pb-1">
                <CardTitle className="text-xs flex items-center gap-2">
                  <code className="text-primary">{hoveredDoc.doc_id}</code>
                  <Badge variant="secondary" className="text-[10px]">{hoveredDoc.version}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="text-xs space-y-1">
                <p className="font-medium text-sm">{hoveredDoc.title}</p>
                <p className="text-muted-foreground">{hoveredDoc.department}</p>
                <p className="text-muted-foreground">{hoveredDoc.doc_type} · {hoveredDoc.system_level}</p>
                <Button
                  size="sm"
                  variant="outline"
                  className="mt-2 w-full text-xs h-7"
                  onClick={() => navigate(`/documents/${hoveredDoc.id}`)}
                >
                  查看文档详情
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Stats row */}
      <div className="flex gap-4 flex-wrap text-sm text-muted-foreground">
        <span>可见节点：<strong className="text-foreground">{visibleDocs.length}</strong></span>
        <span>可见关系：<strong className="text-foreground">{visibleEdges.length}</strong></span>
        <span>点击节点可查看文档详情</span>
      </div>
    </div>
  )
}
