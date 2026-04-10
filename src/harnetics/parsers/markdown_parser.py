# [INPUT]: 依赖 re 正则与 models.document.Section
# [OUTPUT]: 对外提供 parse_markdown()
# [POS]: parsers 包的 Markdown 解析器，按标题拆分章节
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from __future__ import annotations

import re
from harnetics.models.document import Section

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)", re.MULTILINE)


def parse_markdown(content: str, doc_id: str) -> list[Section]:
    """按 Markdown 标题拆分内容，返回 Section 列表。"""
    matches = list(_HEADING_RE.finditer(content))
    if not matches:
        return [
            Section(
                section_id=f"{doc_id}-sec-0",
                doc_id=doc_id,
                heading="(untitled)",
                content=content.strip(),
                level=0,
                order_index=0,
            )
        ]

    sections: list[Section] = []

    # ---- 标题前的前导内容 ----
    preamble = content[: matches[0].start()].strip()
    if preamble:
        sections.append(
            Section(
                section_id=f"{doc_id}-sec-0",
                doc_id=doc_id,
                heading="(preamble)",
                content=preamble,
                level=0,
                order_index=0,
            )
        )

    for idx, m in enumerate(matches):
        level = len(m.group(1))
        heading = m.group(2).strip()
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        body = content[start:end].strip()
        order = len(sections)
        sections.append(
            Section(
                section_id=f"{doc_id}-sec-{order}",
                doc_id=doc_id,
                heading=heading,
                content=body,
                level=level,
                order_index=order,
            )
        )

    return sections
