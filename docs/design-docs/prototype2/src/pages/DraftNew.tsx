import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Check, ChevronRight, FileText, Sparkles } from 'lucide-react'
import { documents } from '@/data/mock'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'

const departments = ['系统工程部', '动力系统部', '质量与可靠性部', '试验与验证部', '总体设计部', '技术负责人']
const docTypes = ['测试大纲', '需求文档', '设计文档', 'ICD', '分析报告', '管理文档']
const levels = ['系统层', '分系统层', '零部件层', '全层级']

// Candidate docs that are usually surfaced for a draft about TQ-12 testing
const candidateDocs = documents.filter((d) =>
  ['DOC-ICD-001', 'DOC-SYS-001', 'DOC-DES-001', 'DOC-QAP-001', 'DOC-TPL-001'].includes(d.doc_id)
)

export default function DraftNew() {
  const navigate = useNavigate()
  const [step, setStep] = useState<1 | 2>(1)
  const [topic, setTopic] = useState(
    '为 TQ-12 型发动机编写地面热试车测试大纲，需引用 ICD 接口参数和 SYS-001 性能指标。'
  )
  const [dept, setDept] = useState(departments[1])
  const [type, setType] = useState(docTypes[0])
  const [level, setLevel] = useState(levels[1])
  const [selected, setSelected] = useState<Set<string>>(new Set(['DOC-ICD-001', 'DOC-SYS-001', 'DOC-DES-001']))
  const [generating, setGenerating] = useState(false)

  function toggleDoc(docId: string) {
    setSelected((prev) => {
      const next = new Set(prev)
      next.has(docId) ? next.delete(docId) : next.add(docId)
      return next
    })
  }

  function handleSearch() {
    setStep(2)
  }

  function handleGenerate() {
    setGenerating(true)
    setTimeout(() => navigate('/draft/draft-001'), 1400)
  }

  return (
    <div className="container mx-auto max-w-screen-xl px-4 py-8 space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">草稿工作台</h1>
        <p className="mt-1 text-muted-foreground">填写草稿参数，检索候选来源，一键生成对齐草稿</p>
      </div>

      {/* Stepper indicator */}
      <div className="flex items-center gap-2 text-sm">
        <span className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold ${step >= 1 ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'}`}>1</span>
        <span className={step >= 1 ? 'font-medium' : 'text-muted-foreground'}>填写草稿参数</span>
        <ChevronRight className="h-4 w-4 text-muted-foreground" />
        <span className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold ${step >= 2 ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'}`}>2</span>
        <span className={step >= 2 ? 'font-medium' : 'text-muted-foreground'}>确认来源文档</span>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Step 1 — Form */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <FileText className="h-4 w-4 text-primary" />
              步骤一：草稿参数
            </CardTitle>
            <CardDescription>描述草稿主题并设定文档类型信息</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="topic">草稿主题描述</Label>
              <Textarea
                id="topic"
                rows={4}
                placeholder="请描述需要生成的文档内容，越详细越准确…"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label>负责部门</Label>
                <select
                  value={dept}
                  onChange={(e) => setDept(e.target.value)}
                  className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  {departments.map((d) => <option key={d}>{d}</option>)}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label>文档类型</Label>
                <select
                  value={type}
                  onChange={(e) => setType(e.target.value)}
                  className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  {docTypes.map((t) => <option key={t}>{t}</option>)}
                </select>
              </div>
            </div>

            <div className="space-y-1.5">
              <Label>系统层级</Label>
              <select
                value={level}
                onChange={(e) => setLevel(e.target.value)}
                className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                {levels.map((l) => <option key={l}>{l}</option>)}
              </select>
            </div>

            <Separator />

            <Button className="w-full gap-2" onClick={handleSearch} disabled={!topic.trim()}>
              <Search className="h-4 w-4" />
              检索候选来源文档
            </Button>
          </CardContent>
        </Card>

        {/* Step 2 — Candidate sources */}
        <Card className={step < 2 ? 'opacity-50 pointer-events-none' : ''}>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Search className="h-4 w-4 text-primary" />
              步骤二：候选来源文档
            </CardTitle>
            <CardDescription>
              AI 已检索到 {candidateDocs.length} 份相关文档，勾选要引用的来源
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {step < 2 ? (
              <p className="text-sm text-muted-foreground text-center py-8">请先完成步骤一</p>
            ) : (
              <>
                {candidateDocs.map((doc) => {
                  const checked = selected.has(doc.doc_id)
                  return (
                    <label
                      key={doc.doc_id}
                      className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                        checked ? 'border-primary bg-primary/5' : 'border-border hover:bg-muted/40'
                      }`}
                    >
                      <div
                        className={`mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded border ${
                          checked ? 'bg-primary border-primary' : 'border-input'
                        }`}
                        onClick={() => toggleDoc(doc.doc_id)}
                      >
                        {checked && <Check className="h-3 w-3 text-primary-foreground" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <code className="text-xs font-mono text-primary">{doc.doc_id}</code>
                          <Badge variant="secondary" className="text-xs">{doc.version}</Badge>
                          <Badge variant="outline" className="text-xs">{doc.doc_type}</Badge>
                        </div>
                        <p className="text-sm font-medium mt-0.5 truncate">{doc.title}</p>
                        <p className="text-xs text-muted-foreground">{doc.department}</p>
                      </div>
                    </label>
                  )
                })}

                <Separator />

                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    已选 <strong>{selected.size}</strong> 份来源文档
                  </p>
                  <Button
                    className="w-full gap-2"
                    disabled={selected.size === 0 || generating}
                    onClick={handleGenerate}
                  >
                    {generating ? (
                      <>
                        <div className="h-4 w-4 rounded-full border-2 border-primary-foreground/30 border-t-primary-foreground animate-spin" />
                        AI 生成中…
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-4 w-4" />
                        生成对齐草稿
                      </>
                    )}
                  </Button>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
