# [INPUT]: 依赖 evaluators 子模块
# [OUTPUT]: 对外提供 build_default_bus() 快捷工厂
# [POS]: evaluators 包入口，组装默认评估器总线
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from __future__ import annotations

from harnetics.evaluators.base import EvaluatorBus
from harnetics.evaluators.citation import (
    EA1_CitationCompleteness, EA2_CitationReality,
    EA3_VersionFreshness, EA4_NoCyclicReferences, EA5_CoverageRate,
)
from harnetics.evaluators.icd import EB1_ICDConsistency
from harnetics.evaluators.ai_quality import ED1_NoFabrication, ED3_ConflictMarked


def build_default_bus() -> EvaluatorBus:
    bus = EvaluatorBus()
    for ev in [
        EA1_CitationCompleteness(),
        EA2_CitationReality(),
        EA3_VersionFreshness(),
        EA4_NoCyclicReferences(),
        EA5_CoverageRate(),
        EB1_ICDConsistency(),
        ED1_NoFabrication(),
        ED3_ConflictMarked(),
    ]:
        bus.register(ev)
    return bus
