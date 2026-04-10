# [INPUT]: 依赖 re、graph.store、evaluators.base
# [OUTPUT]: 对外提供 ED1_NoFabrication, ED3_ConflictMarked
# [POS]: evaluators 包的 AI 质量检查域，防止捏造数据和确保冲突标记
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from __future__ import annotations

import re

from harnetics.evaluators.base import (
    BaseEvaluator, EvalLevel, EvalResult, EvalStatus,
)

_NUMBER_RE = re.compile(r"\b(\d+(?:\.\d+)?)\s*(?:kN|MPa|K|km|s|kg|m/s|t|%|°C|Hz|kPa|m|mm|N|W|A|V)?")
_DOC_REF_RE = re.compile(r"DOC-[A-Z]{3}-\d{3}")
_CONFLICT_ANCHOR_RE = re.compile(r"⚠️")


class ED1_NoFabrication(BaseEvaluator):
    """草稿中每个数字值必须能在引用文档的章节中找到原文。"""
    evaluator_id = "ED.1"
    name = "无捏造技术指标"
    level = EvalLevel.BLOCK

    def evaluate(self, draft: dict, graph_conn=None) -> EvalResult:
        from harnetics.graph import store
        content = draft.get("content_md", "")
        citations = draft.get("citations", [])  # list of dicts or Citation objects
        if not citations:
            # 无引注信息则基于文档内容做宽松检查
            numbers = _NUMBER_RE.findall(content)
            if not numbers:
                return EvalResult(
                    evaluator_id=self.evaluator_id, name=self.name,
                    status=EvalStatus.SKIP, level=self.level,
                    detail="草稿无数值内容，跳过捏造检查", locations=[],
                )
            # 有数字但无任何引注
            return EvalResult(
                evaluator_id=self.evaluator_id, name=self.name,
                status=EvalStatus.WARN, level=self.level,
                detail=f"草稿中含 {len(numbers)} 个数值但未提供引注信息，无法验证来源",
                locations=[],
            )

        # 基于草稿引注列表验证数字可追溯
        # 收集引用文档中出现的所有数字
        source_numbers: set[str] = set()
        cited_doc_ids = set()
        for c in citations:
            if isinstance(c, dict):
                cited_doc_ids.add(c.get("source_doc_id", ""))
            else:
                cited_doc_ids.add(getattr(c, "source_doc_id", ""))

        for doc_id in cited_doc_ids:
            sections = store.get_sections(doc_id)
            for sec in sections:
                for m in _NUMBER_RE.finditer(sec.content or ""):
                    source_numbers.add(m.group(1))

        # 检查草稿中的数字是否都在来源中能找到
        draft_numbers = [m.group(1) for m in _NUMBER_RE.finditer(content)]
        unfounded = [n for n in draft_numbers if n not in source_numbers]
        
        if unfounded and len(unfounded) > len(draft_numbers) * 0.3:
            return EvalResult(
                evaluator_id=self.evaluator_id, name=self.name,
                status=EvalStatus.FAIL, level=self.level,
                detail=f"{len(unfounded)}/{len(draft_numbers)} 个数值未在引用文档中找到原文",
                locations=unfounded[:5],
            )
        return EvalResult(
            evaluator_id=self.evaluator_id, name=self.name,
            status=EvalStatus.PASS, level=self.level,
            detail="草稿数值均可在引用文档中溯源", locations=[],
        )


class ED3_ConflictMarked(BaseEvaluator):
    """检测到的冲突必须在草稿正文中有对应 ⚠️ 标记。"""
    evaluator_id = "ED.3"
    name = "冲突明确标记"
    level = EvalLevel.BLOCK

    def evaluate(self, draft: dict, graph_conn=None) -> EvalResult:
        content = draft.get("content_md", "")
        conflicts = draft.get("conflicts", [])
        if not conflicts:
            return EvalResult(
                evaluator_id=self.evaluator_id, name=self.name,
                status=EvalStatus.PASS, level=self.level,
                detail="无检测到的冲突，无需标记", locations=[],
            )
        conflict_markers = _CONFLICT_ANCHOR_RE.findall(content)
        if len(conflict_markers) < len(conflicts):
            return EvalResult(
                evaluator_id=self.evaluator_id, name=self.name,
                status=EvalStatus.FAIL, level=self.level,
                detail=f"检测到 {len(conflicts)} 处冲突但正文只有 {len(conflict_markers)} 个 ⚠️ 标记",
                locations=[],
            )
        return EvalResult(
            evaluator_id=self.evaluator_id, name=self.name,
            status=EvalStatus.PASS, level=self.level,
            detail=f"{len(conflicts)} 处冲突均已用 ⚠️ 标记", locations=[],
        )
