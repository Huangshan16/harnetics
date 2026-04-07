import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Download, ArrowRight, ChevronRight } from 'lucide-react'
import { impactReport, type ImpactLevel } from '@/data/mock'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

const impactBadge: Record<ImpactLevel, 'destructive' | 'warning' | 'secondary'> = {
  Critical: 'destructive',
  Major: 'warning',
  Minor: 'secondary',
}

export default function ImpactReport() {
  const navigate = useNavigate()
  const rpt = impactReport  // single report for this prototype

  return (
    <div className="container mx-auto max-w-screen-xl px-4 py-6 space-y-6">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-1 text-sm text-muted-foreground">
        <Link to="/impact" className="hover:text-foreground transition-colors">变更影响</Link>
        <ChevronRight className="h-4 w-4" />
        <span className="text-foreground font-medium">{rpt.id}</span>
      </nav>

      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-2">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-xl font-bold">影响分析报告</h1>
            <code className="text-xs bg-muted px-2 py-0.5 rounded font-mono">{rpt.id}</code>
          </div>
          <div className="flex items-center gap-2 text-sm flex-wrap">
            <code className="font-mono text-primary font-semibold">{rpt.trigger_doc_id}</code>
            <span className="text-muted-foreground">{rpt.trigger_title}</span>
            <span className="flex items-center gap-1 text-muted-foreground">
              <code className="bg-muted px-1 rounded text-xs">{rpt.old_version}</code>
              <ArrowRight className="h-3.5 w-3.5" />
              <code className="bg-primary/10 text-primary px-1 rounded text-xs font-semibold">{rpt.new_version}</code>
            </span>
            <Badge variant="secondary">{rpt.date}</Badge>
          </div>
        </div>
        <div className="flex gap-2 shrink-0">
          <Button variant="outline" size="sm" className="gap-1.5" onClick={() => navigate('/impact')}>
            <ArrowLeft className="h-4 w-4" />
            返回
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5">
            <Download className="h-4 w-4" />
            导出报告
          </Button>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Card>
          <CardContent className="pt-4 pb-4 text-center">
            <p className="text-2xl font-bold">{rpt.impacted.length}</p>
            <p className="text-xs text-muted-foreground mt-1">受影响文档</p>
          </CardContent>
        </Card>
        <Card className="border-destructive/40">
          <CardContent className="pt-4 pb-4 text-center">
            <p className="text-2xl font-bold text-destructive">{rpt.critical}</p>
            <p className="text-xs text-muted-foreground mt-1">Critical</p>
          </CardContent>
        </Card>
        <Card className="border-amber-400/40">
          <CardContent className="pt-4 pb-4 text-center">
            <p className="text-2xl font-bold text-amber-500">{rpt.major}</p>
            <p className="text-xs text-muted-foreground mt-1">Major</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 pb-4 text-center">
            <p className="text-2xl font-bold text-muted-foreground">{rpt.minor}</p>
            <p className="text-xs text-muted-foreground mt-1">Minor</p>
          </CardContent>
        </Card>
      </div>

      {/* Impacted docs table */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">受影响文档清单</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/50">
                <TableHead className="w-[130px]">文档编号</TableHead>
                <TableHead>文档标题</TableHead>
                <TableHead className="hidden md:table-cell">部门</TableHead>
                <TableHead className="w-[90px]">影响等级</TableHead>
                <TableHead className="hidden lg:table-cell">受影响章节</TableHead>
                <TableHead className="hidden xl:table-cell">影响原因摘要</TableHead>
                <TableHead className="hidden lg:table-cell w-[100px]">当前引用版本</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rpt.impacted.map((d, i) => (
                <TableRow key={i} className="hover:bg-muted/30">
                  <TableCell>
                    <code className="text-xs bg-muted px-1.5 py-0.5 rounded font-mono">{d.doc_id}</code>
                  </TableCell>
                  <TableCell>
                    <span className="font-medium text-sm">{d.title}</span>
                  </TableCell>
                  <TableCell className="hidden md:table-cell text-sm text-muted-foreground">
                    {d.department}
                  </TableCell>
                  <TableCell>
                    <Badge variant={impactBadge[d.impact_level]}>{d.impact_level}</Badge>
                  </TableCell>
                  <TableCell className="hidden lg:table-cell">
                    <div className="flex flex-wrap gap-1">
                      {d.affected_sections.map((s, j) => (
                        <code key={j} className="text-xs bg-muted px-1 rounded">{s}</code>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell className="hidden xl:table-cell text-xs text-muted-foreground max-w-xs">
                    <span className="line-clamp-2">{d.reason}</span>
                  </TableCell>
                  <TableCell className="hidden lg:table-cell">
                    <code className="text-xs text-muted-foreground">{d.current_ref_version}</code>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Detail cards for each impacted doc */}
      <div className="space-y-3">
        <h2 className="text-base font-semibold">影响详情</h2>
        {rpt.impacted.map((d, i) => (
          <Card key={i} className={d.impact_level === 'Critical' ? 'border-destructive/40' : d.impact_level === 'Major' ? 'border-amber-400/40' : ''}>
            <CardContent className="py-4 px-5">
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <code className="font-mono text-sm font-bold text-primary">{d.doc_id}</code>
                    <Badge variant={impactBadge[d.impact_level]}>{d.impact_level}</Badge>
                    <code className="text-xs text-muted-foreground bg-muted px-1 rounded">引用：{d.current_ref_version}</code>
                  </div>
                  <p className="text-sm font-medium">{d.title}</p>
                  <p className="text-sm text-muted-foreground">{d.reason}</p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    <span className="text-xs text-muted-foreground">受影响章节：</span>
                    {d.affected_sections.map((s, j) => (
                      <code key={j} className="text-xs bg-muted px-1 rounded">{s}</code>
                    ))}
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="gap-1 shrink-0 text-primary"
                  onClick={() => navigate('/draft')}
                >
                  生成对齐草稿
                  <ChevronRight className="h-3.5 w-3.5" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
