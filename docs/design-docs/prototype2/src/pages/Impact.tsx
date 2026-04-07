import { useNavigate } from 'react-router-dom'
import { Upload, ArrowRight, AlertTriangle, ChevronRight } from 'lucide-react'
import { impactReport } from '@/data/mock'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'

const impactReports = [impactReport]

export default function Impact() {
  const navigate = useNavigate()

  return (
    <div className="container mx-auto max-w-screen-xl px-4 py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">变更影响分析</h1>
        <p className="mt-1 text-muted-foreground">上传文档新版本，自动分析对下游文档的级联影响</p>
      </div>

      {/* Upload form */}
      <Card className="border-dashed border-2">
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Upload className="h-4 w-4 text-primary" />
            发起新的影响分析
          </CardTitle>
          <CardDescription>选择触发文档并上传新版本，系统将自动扫描全部下游关联文档</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3 items-end">
            <div className="space-y-1.5">
              <Label>触发文档</Label>
              <select
                defaultValue="DOC-SYS-001"
                className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="DOC-SYS-001">DOC-SYS-001 动力系统总体需求</option>
                <option value="DOC-ICD-001">DOC-ICD-001 全局接口控制文档</option>
                <option value="DOC-DES-001">DOC-DES-001 动力系统详细设计</option>
              </select>
            </div>
            <div className="space-y-1.5">
              <Label>新版本号</Label>
              <Input placeholder="例如 v3.2" defaultValue="v3.2" />
            </div>
            <Button className="gap-2 w-full md:w-auto">
              <Upload className="h-4 w-4" />
              上传并分析
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Reports list */}
      <div className="space-y-3">
        <h2 className="text-base font-semibold">历史分析报告</h2>
        {impactReports.map((rpt) => (
          <Card
            key={rpt.id}
            className="cursor-pointer hover:border-primary/50 transition-colors"
            onClick={() => navigate(`/impact/${rpt.id}`)}
          >
            <CardContent className="py-4 px-5">
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-2 flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <code className="text-sm font-mono font-bold text-primary">{rpt.trigger_doc_id}</code>
                    <span className="flex items-center gap-1 text-sm text-muted-foreground">
                      <code className="bg-muted px-1 rounded text-xs">{rpt.old_version}</code>
                      <ArrowRight className="h-3.5 w-3.5" />
                      <code className="bg-primary/10 text-primary px-1 rounded text-xs font-semibold">{rpt.new_version}</code>
                    </span>
                    <Badge variant="secondary" className="text-xs">{rpt.date}</Badge>
                  </div>
                  <p className="text-sm font-medium truncate">{rpt.trigger_title}</p>

                  <Separator />

                  <div className="flex items-center gap-3 flex-wrap">
                    <span className="text-sm text-muted-foreground flex items-center gap-1">
                      <AlertTriangle className="h-4 w-4" />
                      影响 <strong>{rpt.impacted.length}</strong> 份文档
                    </span>
                    {rpt.critical > 0 && (
                      <Badge variant="destructive">{rpt.critical} Critical</Badge>
                    )}
                    {rpt.major > 0 && (
                      <Badge variant="warning">{rpt.major} Major</Badge>
                    )}
                    {rpt.minor > 0 && (
                      <Badge variant="secondary">{rpt.minor} Minor</Badge>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-1 text-muted-foreground shrink-0">
                  <span className="text-sm">查看报告</span>
                  <ChevronRight className="h-4 w-4" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
