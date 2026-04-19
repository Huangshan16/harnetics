# [INPUT]: 聚合 document/icd/draft/impact 子模块的公共类型
# [OUTPUT]: 对外提供全部领域 dataclass 的统一导入入口
# [POS]: models 包的门面，让消费者写 `from harnetics.models import X` 即可
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

# ---- 领域模型 ----
from .document import DocumentEdge, DocumentNode, Section
from .draft import AlignedDraft, Citation, Conflict, DraftRequest
from .icd import ICDParameter
from .impact import ImpactedDoc, ImpactReport, SectionDiff

__all__ = [
    "AlignedDraft",
    "Citation",
    "Conflict",
    "DocumentEdge",
    "DocumentNode",
    "DraftRequest",
    "ICDParameter",
    "ImpactedDoc",
    "ImpactReport",
    "Section",
    "SectionDiff",
]
