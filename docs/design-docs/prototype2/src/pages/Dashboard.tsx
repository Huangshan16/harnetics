import { Link } from 'react-router-dom'
import { FileText, Link2, AlertTriangle, FileEdit, GitMerge, CheckCircle, Clock, Upload, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'

const stats = [
  { label: '文档总数', value: 10, sub: '8 已收录 · 2 待上传', icon: FileText, color: 'text-primary' },
  { label: '跨文档关系', value: 23, sub: '10 条已建立', icon: Link2, color: 'text-blue-600' },
  { label: '过期引用/告警', value: 3, sub: '需人工审核', icon: AlertTriangle, color: 'text-amber-500' },
]

const healthMetrics = [
  { label: '引用最新版本率', value: 78, hint: '5 处引用落后 1 个版本' },
  { label: 'ICD 参数一致性', value: 100, hint: '所有接口参数均已对齐' },
  { label: '引注覆盖率', value: 72, hint: '技术段落缺引注比例 28%' },
]

const recentActivity = [
  { time: '今天 14:32', action: '上传新版本', target: 'DOC-SYS-001 v3.1', type: 'upload', color: 'bg-primary' },
  { time: '今天 13:15', action: '生成草稿', target: 'TQ-12 测试大纲 (draft-001)', type: 'draft', color: 'bg-blue-500' },
  { time: '今天 11:48', action: '影响分析完成', target: 'rpt-001: SYS-001 v3.0→v3.1', type: 'impact', color: 'bg-amber-500' },
  { time: '昨天 17:22', action: '文档审批通过', target: 'DOC-DES-001 v2.0', type: 'approval', color: 'bg-green-500' },
  { time: '昨天 15:00', action: '上传新版本', target: 'DOC-ICD-001 v2.3', type: 'upload', color: 'bg-primary' },
]

export default function Dashboard() {
  return (
    <div className="container mx-auto max-w-screen-xl px-4 py-8 space-y-8">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">系统仪表盘</h1>
        <p className="mt-1 text-muted-foreground">实时掌握文档对齐状态 · 驱动工程决策</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {stats.map((s) => (
          <Card key={s.label}>
            <CardHeader className="pb-2 flex flex-row items-center justify-between">
              <CardDescription>{s.label}</CardDescription>
              <s.icon className={`h-5 w-5 ${s.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{s.value}</div>
              <p className="mt-1 text-xs text-muted-foreground">{s.sub}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Health metrics */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-primary" />
              文档健康度
            </CardTitle>
            <CardDescription>基于文档图谱自动计算</CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            {healthMetrics.map((m) => (
              <div key={m.label} className="space-y-1.5">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">{m.label}</span>
                  <span className={m.value >= 90 ? 'text-green-600' : m.value >= 75 ? 'text-amber-500' : 'text-destructive'}>
                    {m.value}%
                  </span>
                </div>
                <Progress value={m.value} />
                <p className="text-xs text-muted-foreground">{m.hint}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Quick actions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">快捷操作</CardTitle>
            <CardDescription>核心工作流入口</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link to="/draft" className="block">
              <Button className="w-full justify-start gap-2" size="lg">
                <FileEdit className="h-4 w-4" />
                生成对齐草稿
              </Button>
            </Link>
            <Link to="/impact" className="block">
              <Button variant="outline" className="w-full justify-start gap-2" size="lg">
                <GitMerge className="h-4 w-4" />
                变更影响分析
              </Button>
            </Link>
            <Link to="/documents" className="block">
              <Button variant="outline" className="w-full justify-start gap-2" size="lg">
                <Upload className="h-4 w-4" />
                上传新文档
              </Button>
            </Link>
            <Link to="/graph" className="block">
              <Button variant="ghost" className="w-full justify-start gap-2" size="lg">
                <Link2 className="h-4 w-4" />
                查看文档图谱
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Recent activity */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Clock className="h-4 w-4 text-primary" />
            最近操作
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative space-y-0">
            {recentActivity.map((a, i) => (
              <div key={i} className="flex items-start gap-4 pb-4 last:pb-0">
                <div className="flex flex-col items-center">
                  <div className={`h-2 w-2 rounded-full mt-1.5 ${a.color}`} />
                  {i < recentActivity.length - 1 && <div className="w-px flex-1 bg-border mt-1 min-h-[24px]" />}
                </div>
                <div className="flex flex-col gap-0.5 min-w-0">
                  <p className="text-sm">
                    <span className="text-muted-foreground">{a.action}：</span>
                    <span className="font-medium">{a.target}</span>
                  </p>
                  <p className="text-xs text-muted-foreground">{a.time}</p>
                </div>
                {a.type === 'impact' && (
                  <Badge variant="warning" className="ml-auto shrink-0">影响</Badge>
                )}
                {a.type === 'approval' && (
                  <Badge variant="success" className="ml-auto shrink-0 flex items-center gap-1">
                    <CheckCircle className="h-3 w-3" /> 通过
                  </Badge>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
