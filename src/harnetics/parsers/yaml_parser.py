# [INPUT]: 依赖 PyYAML
# [OUTPUT]: 对外提供 parse_yaml()
# [POS]: parsers 包的 YAML 安全加载包装器
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from __future__ import annotations

import yaml


def parse_yaml(content: str) -> dict:
    """安全加载 YAML 内容，解析失败时返回 error 字典。"""
    try:
        data = yaml.safe_load(content)
        if data is None:
            return {}
        if not isinstance(data, dict):
            return {"_raw": data}
        return data
    except yaml.YAMLError as exc:
        return {"_error": str(exc)}
