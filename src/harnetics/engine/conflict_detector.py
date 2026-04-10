# [INPUT]: 依赖 graph.store (icd_parameters)、models.draft.Conflict
# [OUTPUT]: 对外提供 ConflictDetector
# [POS]: engine 包的冲突检测器，比对文档间参数差异
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from __future__ import annotations

from harnetics.graph import store
from harnetics.models.draft import Conflict


class ConflictDetector:
    """跨文档 ICD 参数冲突检测。"""

    def detect(self, doc_ids: list[str], icd_params: list[dict] | None = None) -> list[Conflict]:
        # 收集所有相关文档的 ICD 参数
        all_params: dict[str, list[tuple[str, str, str]]] = {}  # name → [(doc_id, value, version)]
        for doc_id in doc_ids:
            doc = store.get_document(doc_id)
            if not doc:
                continue
            params = store.get_icd_parameters(doc_id)
            for p in params:
                all_params.setdefault(p.name, []).append((doc_id, p.value or "", p.version or ""))
        
        # 也检查明确传入的 ICD 参数（来自 LLM 上下文）
        if icd_params:
            pass  # 已通过 store.get_icd_parameters 获取

        conflicts: list[Conflict] = []
        for name, entries in all_params.items():
            if len(entries) < 2:
                continue
            # 比对所有文档对的值
            for i in range(len(entries)):
                for j in range(i + 1, len(entries)):
                    doc_a, val_a, ver_a = entries[i]
                    doc_b, val_b, ver_b = entries[j]
                    if val_a and val_b and val_a.strip() != val_b.strip():
                        conflicts.append(Conflict(
                            doc_a_id=doc_a,
                            doc_b_id=doc_b,
                            section_a_id="",
                            section_b_id="",
                            description=f"「{name}」: {doc_a}={val_a} vs {doc_b}={val_b}",
                            severity="warning",
                        ))
        return conflicts
