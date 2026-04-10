"""
# [INPUT]: 依赖 graph.store (get_document, get_sections, get_edges_for_doc)、models.impact
# [OUTPUT]: 对外提供 ImpactAnalyzer 类，analyze() 返回 ImpactReport
# [POS]: engine 包的影响分析器，BFS 遍历下游依赖图，按深度/关系类型评定危险等级
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md
"""
from __future__ import annotations

import json
import uuid
from collections import deque
from datetime import datetime, timezone

from harnetics.graph import store
from harnetics.models.impact import ImpactReport, ImpactedDoc, SectionDiff

# ---- 关系类型 → 影响传播权重 ----------------------------------------
_HIGH_RISK_RELATIONS = {"constrained_by", "traces_to", "implements", "derived_from"}
_MEDIUM_RISK_RELATIONS = {"references", "supersedes", "allocated_to"}


def _severity(depth: int, relation: str | None) -> str:
    """根据 BFS 深度和关系类型返回危险等级。"""
    if depth == 1 and (relation in _HIGH_RISK_RELATIONS):
        return "critical"
    if depth == 1:
        return "major"
    if depth == 2:
        return "major"
    return "minor"


class ImpactAnalyzer:
    """BFS 遍历下游依赖，评估文档变更波及范围。"""

    # ----------------------------------------------------------------
    # 公共接口
    # ----------------------------------------------------------------

    def analyze(
        self,
        doc_id: str,
        old_version: str = "",
        new_version: str = "",
        changed_section_ids: list[str] | None = None,
    ) -> ImpactReport:
        """
        分析 doc_id 的一次版本变更会影响哪些下游文档。

        Parameters
        ----------
        doc_id:               触发文档 ID
        old_version:          变更前版本号（记录用，不影响计算）
        new_version:          变更后版本号
        changed_section_ids:  明确变更的章节 ID 列表；为空则默认全量章节
        """
        doc = store.get_document(doc_id)
        if doc is None:
            raise ValueError(f"document not found: {doc_id}")

        sections = store.get_sections(doc_id)
        changed_ids = set(changed_section_ids or [s.section_id for s in sections])

        changed_sections = [
            SectionDiff(
                section_id=s.section_id,
                heading=s.heading,
                change_type="modified",
                summary=f"章节 '{s.heading}' 发生变更",
            )
            for s in sections
            if s.section_id in changed_ids
        ]

        impacted_docs = self._bfs_downstream(doc_id, changed_ids)

        summary_lines = [
            f"文档 {doc_id}（{doc.title}）从版本 {old_version} → {new_version}",
            f"变更章节：{len(changed_sections)} 个，影响下游文档：{len(impacted_docs)} 个",
        ]
        critical = [d for d in impacted_docs if d.severity == "critical"]
        major = [d for d in impacted_docs if d.severity == "major"]
        minor = [d for d in impacted_docs if d.severity == "minor"]
        if impacted_docs:
            summary_lines.append(
                f"影响等级分布：critical {len(critical)} / major {len(major)} / minor {len(minor)}"
            )
        else:
            summary_lines.append(
                "未发现依赖该文档的下游文档；当前图谱中没有任何文档把它作为引用目标。"
            )
        if critical:
            summary_lines.append(
                "高危影响：" + "、".join(d.doc_id for d in critical)
            )

        report_id = str(uuid.uuid4())
        report = ImpactReport(
            report_id=report_id,
            trigger_doc_id=doc_id,
            old_version=old_version,
            new_version=new_version,
            changed_sections=changed_sections,
            impacted_docs=impacted_docs,
            summary="\n".join(summary_lines),
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        self._persist(report)
        return report

    # ----------------------------------------------------------------
    # 内部方法
    # ----------------------------------------------------------------

    def _bfs_downstream(
        self, start_doc_id: str, changed_section_ids: set[str]
    ) -> list[ImpactedDoc]:
        """BFS 遍历所有依赖 start_doc_id 的下游文档（最大深度 6）。"""
        visited: dict[str, ImpactedDoc] = {}
        # queue items: (doc_id, depth, relation)
        queue: deque[tuple[str, int, str]] = deque()

        # 入队首层下游：谁引用了 start_doc_id，谁就会被它影响。
        upstream, _ = store.get_edges_for_doc(start_doc_id)
        for edge in upstream:
            if edge.source_doc_id == start_doc_id:
                continue
            queue.append((edge.source_doc_id, 1, edge.relation or "references"))

        while queue:
            current_doc_id, depth, relation = queue.popleft()

            if depth > 6:
                continue
            if current_doc_id in visited:
                # 保留危险等级较高的条目
                existing = visited[current_doc_id]
                new_sev = _severity(depth, relation)
                if _sev_rank(new_sev) > _sev_rank(existing.severity):
                    existing.severity = new_sev
                continue

            current_doc = store.get_document(current_doc_id)
            if current_doc is None:
                continue

            severity = _severity(depth, relation)
            affected_sections = self._find_affected_sections(
                current_doc_id, changed_section_ids
            )

            impacted = ImpactedDoc(
                doc_id=current_doc_id,
                title=current_doc.title,
                relation=relation,
                affected_sections=affected_sections,
                severity=severity,
            )
            visited[current_doc_id] = impacted

            # 继续向下游传播
            if depth < 6:
                next_upstream, _ = store.get_edges_for_doc(current_doc_id)
                for edge in next_upstream:
                    if edge.source_doc_id not in visited:
                        queue.append(
                            (edge.source_doc_id, depth + 1, edge.relation or "references")
                        )

        # 按危险等级降序排列
        return sorted(
            visited.values(),
            key=lambda d: _sev_rank(d.severity),
            reverse=True,
        )

    def _find_affected_sections(
        self, doc_id: str, upstream_changed_ids: set[str]
    ) -> list[str]:
        """返回被上游变更章节引用的当前文档章节列表（简化：内容含上游 section_id 关键词）。"""
        sections = store.get_sections(doc_id)
        affected: list[str] = []
        for s in sections:
            for uid in upstream_changed_ids:
                if uid in (s.content or ""):
                    affected.append(s.section_id)
                    break
        return affected

    def _persist(self, report: ImpactReport) -> None:
        """将影响分析报告序列化后写入 impact_reports 表。"""
        changed_json = json.dumps(
            [
                {
                    "section_id": s.section_id,
                    "heading": s.heading,
                    "change_type": s.change_type,
                    "summary": s.summary,
                }
                for s in report.changed_sections
            ],
            ensure_ascii=False,
        )
        impacted_json = json.dumps(
            [
                {
                    "doc_id": d.doc_id,
                    "title": d.title,
                    "relation": d.relation,
                    "affected_sections": d.affected_sections,
                    "severity": d.severity,
                }
                for d in report.impacted_docs
            ],
            ensure_ascii=False,
        )
        try:
            with store.get_connection() as conn:
                conn.execute(
                    """INSERT OR REPLACE INTO impact_reports
                       (report_id, trigger_doc_id, old_version, new_version,
                        changed_sections_json, impacted_docs_json, summary, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        report.report_id,
                        report.trigger_doc_id,
                        report.old_version,
                        report.new_version,
                        changed_json,
                        impacted_json,
                        report.summary,
                        report.created_at,
                    ),
                )
        except Exception:
            # 持久化失败不阻断主流程；日志由调用方负责
            pass


def _sev_rank(severity: str) -> int:
    return {"critical": 3, "major": 2, "minor": 1, "info": 0}.get(severity, 0)
