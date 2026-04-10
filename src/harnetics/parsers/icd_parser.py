# [INPUT]: 依赖 parsers.yaml_parser 与 models.icd.ICDParameter
# [OUTPUT]: 对外提供 parse_icd_yaml()
# [POS]: parsers 包的 ICD 专用解析器，从 YAML interfaces 列表提取参数
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from __future__ import annotations

from harnetics.models.icd import ICDParameter
from harnetics.parsers.yaml_parser import parse_yaml


def parse_icd_yaml(content: str, doc_id: str) -> list[ICDParameter]:
    """解析 ICD YAML，提取 interfaces 列表为 ICDParameter。"""
    data = parse_yaml(content)
    if "_error" in data:
        return []

    # ICD 文档使用 `interfaces` 键存放参数列表
    raw_params = data.get("interfaces") or data.get("parameters") or []
    if not isinstance(raw_params, list):
        return []

    params: list[ICDParameter] = []
    for item in raw_params:
        if not isinstance(item, dict):
            continue
        pid = item.get("param_id")
        if not pid:
            continue
        params.append(
            ICDParameter(
                param_id=str(pid),
                doc_id=doc_id,
                name=str(item.get("name", "")),
                interface_type=str(item.get("interface_type", "")),
                subsystem_a=str(item.get("subsystem_a", "")),
                subsystem_b=str(item.get("subsystem_b") or ""),
                value=str(item.get("value", "")),
                unit=str(item.get("unit") or ""),
                range_=str(item.get("range") or ""),
                owner_department=str(item.get("owner_department", "")),
                version=str(data.get("metadata", {}).get("version", "")),
            )
        )
    return params
