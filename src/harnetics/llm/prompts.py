# [INPUT]: 无外部依赖（纯文本常量）
# [OUTPUT]: 对外提供 DRAFT_SYSTEM_PROMPT 与 build_context()
# [POS]: llm 包的 prompt 模块，封装 LLM 调用所需的 system prompt 与上下文组装
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from __future__ import annotations

DRAFT_SYSTEM_PROMPT = """\
你是一名专业的航天系统工程文档助手。你的任务是根据用户提供的参考文档，
生成一份结构化的技术文档草稿。

## 严格规则

1. **每个技术指标必须标注来源**：使用格式 [📎 DOC-XXX-XXX §X.X] 标注
2. **不允许捏造数字**：所有数值参数必须来自参考文档，不可自行编造
3. **发现冲突必须标记**：如果两份参考文档对同一参数给出不同值，
   用 ⚠️ 标记冲突，列出两个来源和各自的值
4. **遵循模板格式**：如果提供了文档模板，严格按模板的章节结构生成
5. **使用中文**：正文使用中文，技术术语可保留英文缩写
6. **ICD 参数引用**：涉及接口参数时，标注 ICD 参数编号

## 输出格式

使用 Markdown 格式，章节使用 ## 和 ### 标题层级。
每个段落末尾标注引用来源。
冲突使用引用块标注：
> ⚠️ 冲突：[参数名]
> - DOC-XXX §X.X: [值A]
> - DOC-YYY §Y.Y: [值B]
"""


def build_context(sections: list[dict], icd_params: list[dict], template_content: str = "") -> str:
    """将检索的章节和 ICD 参数组装为 LLM 可读的上下文字符串。"""
    parts: list[str] = []
    if template_content:
        parts.append(f"## 文档模板\n\n{template_content}\n")
    if sections:
        parts.append("## 参考文档章节\n")
        for sec in sections:
            doc_id = sec.get("doc_id", "")
            heading = sec.get("heading", "")
            text = sec.get("text", "")
            section_id = sec.get("section_id", "")
            parts.append(f"### [{doc_id} §{section_id}] {heading}\n\n{text}\n")
    if icd_params:
        parts.append("## ICD 接口参数\n")
        for p in icd_params:
            parts.append(
                f"- **{p.get('name', '')}** (ID: {p.get('param_id', '')}): "
                f"{p.get('value', '')} {p.get('unit', '')} "
                f"[{p.get('subsystem_a', '')} ↔ {p.get('subsystem_b', '')}]"
            )
    return "\n".join(parts)
