# [INPUT]: 依赖 dataclasses, abc
# [OUTPUT]: 对外提供 EvalLevel, EvalStatus, EvalResult, BaseEvaluator, EvaluatorBus
# [POS]: evaluators 包的基础框架，定义评估器接口与批量运行器
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class EvalLevel(str, Enum):
    BLOCK = "block"
    WARN = "warn"


class EvalStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"


@dataclass
class EvalResult:
    evaluator_id: str
    name: str
    status: EvalStatus
    level: EvalLevel
    detail: str
    locations: list[str] = field(default_factory=list)


class BaseEvaluator(ABC):
    evaluator_id: str
    name: str
    level: EvalLevel

    @abstractmethod
    def evaluate(self, draft: "dict", graph_conn=None) -> EvalResult: ...


class EvaluatorBus:
    def __init__(self) -> None:
        self._evaluators: list[BaseEvaluator] = []

    def register(self, ev: BaseEvaluator) -> None:
        self._evaluators.append(ev)

    def run_all(self, draft: "dict", graph_conn=None) -> list[EvalResult]:
        return [ev.evaluate(draft, graph_conn) for ev in self._evaluators]

    @staticmethod
    def has_blocking_failures(results: list[EvalResult]) -> bool:
        return any(
            r.status == EvalStatus.FAIL and r.level == EvalLevel.BLOCK
            for r in results
        )
