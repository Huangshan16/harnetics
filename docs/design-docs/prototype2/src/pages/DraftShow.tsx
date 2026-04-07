import { useState } from 'react'
import { Download, CheckCircle, AlertTriangle, XCircle, BookOpen, ChevronDown, ChevronUp } from 'lucide-react'
import { evalResults, draftCitations, draftMarkdown } from '@/data/mock'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import type { EvalLevel } from '@/data/mock'

const evalIcon: Record<EvalLevel, React.ReactNode> = {
  Pass: <CheckCircle className="h-4 w-4 text-green-500 shrink-0" />,
  Warning: <AlertTriangle className="h-4 w-4 text-amber-500 shrink-0" />,
  Blocker: <XCircle className="h-4 w-4 text-destructive shrink-0" />,
}

const evalBadge: Record<EvalLevel, 'success' | 'warning' | 'destructive'> = {
  Pass: 'success',
  Warning: 'warning',
  Blocker: 'destructive',
}

const passCount = evalResults.filter((r) => r.level === 'Pass').length
const warnCount = evalResults.filter((r) => r.level === 'Warning').length
const blockCount = evalResults.filter((r) => r.level === 'Blocker').length

export default function DraftShow() {
  const [activeTab, setActiveTab] = useState<'overview' | 'detail'>('overview')
  const [citExpanded, setCitExpanded] = useState(true)

  return (
    <div className="container mx-auto max-w-screen-xl px-4 py-6 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold">草稿工作台</h1>
            <Badge variant="success">Ready</Badge>
            <code className="text-xs text-muted-foreground bg-muted px-1.5 py-0.5 rounded">draft-001</code>
          </div>
          <p className="text-sm text-muted-foreground">
            TQ-12 发动机地面试车测试大纲 · 动力系统部 · 分系统层
          </p>
        </div>
        <Button variant="outline" size="sm" className="gap-2 shrink-0">
          <Download className="h-4 w-4" />
          导出草稿
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Draft content — 2/3 */}
        <div className="lg:col-span-2 space-y-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground font-semibold uppercase tracking-wide">
                草稿内容（只读预览）
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-xs font-mono leading-relaxed whitespace-pre-wrap text-foreground max-h-[65vh] overflow-y-auto p-3 bg-muted/40 rounded-lg">
                {draftMarkdown}
              </pre>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar — 1/3 */}
        <div className="space-y-4">
          {/* Evaluator results */}
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm">评估结果</CardTitle>
                <div className="flex gap-1.5">
                  <Badge variant="success" className="text-xs">{passCount}✓</Badge>
                  {warnCount > 0 && <Badge variant="warning" className="text-xs">{warnCount}⚠</Badge>}
                  {blockCount > 0 && <Badge variant="destructive" className="text-xs">{blockCount}✗</Badge>}
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <Tabs defaultValue="overview">
                <div className="px-4 pt-2">
                  <TabsList className="w-full">
                    <TabsTrigger value="overview" className="flex-1">概览</TabsTrigger>
                    <TabsTrigger value="detail" className="flex-1">详情</TabsTrigger>
                  </TabsList>
                </div>
                <TabsContent value="overview">
                  <div className="p-4 space-y-3">
                    <div className="grid grid-cols-3 gap-2 text-center text-sm">
                      <div className="rounded-lg bg-green-50 dark:bg-green-950/30 p-2">
                        <p className="text-xl font-bold text-green-600">{passCount}</p>
                        <p className="text-xs text-muted-foreground">通过</p>
                      </div>
                      <div className="rounded-lg bg-amber-50 dark:bg-amber-950/30 p-2">
                        <p className="text-xl font-bold text-amber-500">{warnCount}</p>
                        <p className="text-xs text-muted-foreground">告警</p>
                      </div>
                      <div className="rounded-lg bg-red-50 dark:bg-red-950/30 p-2">
                        <p className="text-xl font-bold text-destructive">{blockCount}</p>
                        <p className="text-xs text-muted-foreground">阻断</p>
                      </div>
                    </div>
                    {evalResults
                      .filter((r) => r.level !== 'Pass')
                      .map((r) => (
                        <div key={r.id} className="flex items-start gap-2 text-xs">
                          {evalIcon[r.level]}
                          <div>
                            <span className="font-medium">{r.label}</span>
                            <p className="text-muted-foreground mt-0.5">{r.message}</p>
                          </div>
                        </div>
                      ))}
                  </div>
                </TabsContent>
                <TabsContent value="detail">
                  <div className="p-3 space-y-1.5 max-h-64 overflow-y-auto">
                    {evalResults.map((r) => (
                      <div key={r.id} className="flex items-start gap-2 py-1.5 border-b border-border/50 last:border-0">
                        {evalIcon[r.level]}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-1.5">
                            <span className="text-xs font-mono font-medium">{r.id}</span>
                            <Badge variant={evalBadge[r.level]} className="text-[10px]">{r.level}</Badge>
                          </div>
                          <p className="text-xs text-muted-foreground mt-0.5">{r.message}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Citations */}
          <Card>
            <CardHeader
              className="pb-2 cursor-pointer select-none"
              onClick={() => setCitExpanded((v) => !v)}
            >
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm flex items-center gap-2">
                  <BookOpen className="h-4 w-4 text-primary" />
                  引用来源
                  <Badge variant="secondary" className="text-xs">{draftCitations.length}</Badge>
                </CardTitle>
                {citExpanded ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
              </div>
            </CardHeader>
            {citExpanded && (
              <CardContent className="space-y-3 pt-0">
                {draftCitations.map((c, i) => (
                  <div key={i} className="text-xs space-y-0.5">
                    <p className="font-medium">{c.anchor}</p>
                    <p className="text-muted-foreground">
                      <code className="bg-muted px-1 rounded">{c.source_doc_id}</code> {c.source_section}
                    </p>
                    <p className="text-muted-foreground italic">"{c.snippet}"</p>
                    {i < draftCitations.length - 1 && <Separator className="mt-2" />}
                  </div>
                ))}
              </CardContent>
            )}
          </Card>
        </div>
      </div>
    </div>
  )
}
