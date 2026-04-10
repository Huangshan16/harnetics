# [INPUT]: 依赖 re、graph.store (icd_parameters)、evaluators.base
# [OUTPUT]: 对外提供 EB1_ICDConsistency
# [POS]: evaluators 包的 ICD 一致性检查器，验证草稿参数值与 ICD 表对齐
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from __future__ import annotations

import re

from harnetics.evaluators.base import (
    BaseEvaluator, EvalLevel, EvalResult, EvalStatus,
)

# 匹配 "参数名...数字单位" 模式
_PARAM_PATTERN = re.compile(
    r"([\u4e00-\u9fa5a-zA-Z][^\n，,。.：:]*?)"  # 参数名（中/英文）
    r"[\s：:为是]*"
    r"(\d+(?:\.\d+)?)\s*(kN|MPa|K|km|s|kg|m/s|t|%|°C|Hz|kPa|m|mm|N|W|A|V|Hz)?",
    re.MULTILINE,
)


class EB1_ICDConsistency(BaseEvaluator):
    """草稿中出现的参数名+值必须与 ICD 表一致。"""
    evaluator_id = "EB.1"
    name = "接口参数与 ICD 一致"
    level = EvalLevel.BLOCK

    def evaluate(self, draft: dict, graph_conn=None) -> EvalResult:
        from harnetics.graph import store
        content = draft.get("content_md", "")
        icd_params = store.get_icd_parameters()
        if not icd_params:
            return EvalResult(
                evaluator_id=self.evaluator_id, name=self.name,
                status=EvalStatus.SKIP, level=self.level,
                detail="图谱中无 ICD 参数，跳过一致性检查", locations=[],
            )
        # 构建 ICD 参数名 → 值的映射
        icd_map = {p.name: (p.value, p.unit) for p in icd_params}
        conflicts: list[str] = []
        for m in _PARAM_PATTERN.finditer(content):
            name_candidate = m.group(1).strip()
            val_str = m.group(2)
            unit_str = m.group(3) or ""
            # 精确匹配 ICD 参数名
            if name_candidate in icd_map:
                icd_val, icd_unit = icd_map[name_candidate]
                if icd_val and icd_val.strip() != val_str:
                    conflicts.append(
                        f"「{name_candidate}」草稿值={val_str}{unit_str}，ICD值={icd_val}{icd_unit}"
                    )
        if conflicts:
            return EvalResult(
                evaluator_id=self.evaluator_id, name=self.name,
                status=EvalStatus.FAIL, level=self.level,
                detail=f"发现 {len(conflicts)} 处参数与 ICD 不一致",
                locations=conflicts[:5],
            )
        return EvalResult(
            evaluator_id=self.evaluator_id, name=self.name,
            status=EvalStatus.PASS, level=self.level,
            detail="草稿参数与 ICD 一致", locations=[],
        )
