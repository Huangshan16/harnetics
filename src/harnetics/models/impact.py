# [INPUT]: 依赖 dataclasses
# [OUTPUT]: 对外提供 ImpactReport, ImpactedDoc, SectionDiff, AffectedSection
# [POS]: models 包的变更影响子域，描述变更波及报告，支持 AI 分析模式
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SectionDiff:
    section_id: str
    heading: str
    change_type: str
    summary: str = ""


@dataclass(slots=True)
class AffectedSection:
    """AI 分析产出的受影响章节，含影响理由。"""
    section_id: str
    heading: str = ""
    reason: str = ""


@dataclass(slots=True)
class ImpactedDoc:
    doc_id: str
    title: str
    relation: str
    affected_sections: list[AffectedSection] = field(default_factory=list)
    severity: str = "info"
    analysis_mode: str = "heuristic"


@dataclass(slots=True)
class ImpactReport:
    report_id: str
    trigger_doc_id: str
    old_version: str
    new_version: str
    changed_sections: list[SectionDiff] = field(default_factory=list)
    impacted_docs: list[ImpactedDoc] = field(default_factory=list)
    summary: str = ""
    created_at: str = ""
    analysis_mode: str = "heuristic"
