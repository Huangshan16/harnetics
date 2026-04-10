"""
# [INPUT]: 依赖 graph.store (get_documents, get_document, get_edges_for_doc, get_sections)
# [OUTPUT]: 对外提供 DocumentGraph 类，返回 vis-network 格式图谱数据及关系查询
# [POS]: graph 包的高阶查询层，US4 图谱浏览功能的数据源
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md
"""
from __future__ import annotations

from harnetics.graph import store
from harnetics.models.document import DocumentEdge, DocumentNode

# ---- 部门 → 颜色组 （vis-network group 对应主题色）----
_DEPT_COLORS: dict[str, str] = {
    "推进": "#6366f1",
    "结构": "#f59e0b",
    "电气": "#10b981",
    "热控": "#ef4444",
    "GNC": "#3b82f6",
    "系统": "#8b5cf6",
    "质量": "#ec4899",
}
_DEFAULT_COLOR = "#94a3b8"


def _dept_color(department: str | None) -> str:
    if not department:
        return _DEFAULT_COLOR
    for key, color in _DEPT_COLORS.items():
        if key in department:
            return color
    return _DEFAULT_COLOR


def _node_shape(doc_type: str | None) -> str:
    mapping = {
        "ICD": "diamond",
        "系统需求": "box",
        "设计": "ellipse",
        "质量": "triangle",
        "测试": "triangleDown",
        "模板": "star",
    }
    if not doc_type:
        return "ellipse"
    for key, shape in mapping.items():
        if key in doc_type:
            return shape
    return "ellipse"


class DocumentGraph:
    """US4 图谱浏览：节点/边生成、上下游查询、陈旧引用检测。"""

    # ----------------------------------------------------------------
    # 全量图谱
    # ----------------------------------------------------------------

    def get_full_graph(
        self,
        department: str | None = None,
        system_level: str | None = None,
    ) -> dict:
        """
        返回 vis-network 可直接消费的 {nodes, edges} 字典。

        Parameters
        ----------
        department:    筛选部门（模糊匹配）
        system_level:  筛选层级（模糊匹配）
        """
        docs = store.get_documents(department=department, system_level=system_level)
        doc_ids = {d.doc_id for d in docs}

        nodes = [self._doc_to_node(d) for d in docs]

        # 只返回两端都在筛选结果内的边
        edges: list[dict] = []
        seen_edges: set[tuple[str, str]] = set()
        for doc_id in doc_ids:
            _, downstream = store.get_edges_for_doc(doc_id)
            for edge in downstream:
                key = (edge.source_doc_id, edge.target_doc_id)
                if key in seen_edges:
                    continue
                if edge.target_doc_id in doc_ids:
                    seen_edges.add(key)
                    edges.append(self._edge_to_vis(edge))

        return {"nodes": nodes, "edges": edges}

    # ----------------------------------------------------------------
    # 上游 / 下游查询
    # ----------------------------------------------------------------

    def get_upstream(self, doc_id: str, depth: int = 3) -> list[dict]:
        """返回 doc_id 的上游文档（被 doc_id 依赖的文档）节点列表。"""
        return self._traverse(doc_id, direction="upstream", max_depth=depth)

    def get_downstream(self, doc_id: str, depth: int = 3) -> list[dict]:
        """返回 doc_id 的下游文档（依赖 doc_id 的文档）节点列表。"""
        return self._traverse(doc_id, direction="downstream", max_depth=depth)

    def _traverse(
        self, start: str, direction: str, max_depth: int
    ) -> list[dict]:
        from collections import deque

        visited: dict[str, dict] = {}
        queue: deque[tuple[str, int]] = deque([(start, 0)])
        while queue:
            doc_id, depth = queue.popleft()
            if depth > max_depth or doc_id in visited:
                continue
            doc = store.get_document(doc_id)
            if doc is None:
                continue
            if doc_id != start:
                visited[doc_id] = self._doc_to_node(doc)
            upstream, downstream = store.get_edges_for_doc(doc_id)
            neighbors = upstream if direction == "upstream" else downstream
            for edge in neighbors:
                next_id = edge.source_doc_id if direction == "upstream" else edge.target_doc_id
                if next_id not in visited and next_id != start:
                    queue.append((next_id, depth + 1))
        return list(visited.values())

    # ----------------------------------------------------------------
    # 陈旧引用检测
    # ----------------------------------------------------------------

    def get_stale_references(self) -> list[dict]:
        """返回目标文档状态为 Superseded 的所有边（陈旧引用）。"""
        docs = store.get_documents()
        superseded = {d.doc_id for d in docs if (d.status or "").lower() == "superseded"}
        result: list[dict] = []
        for doc in docs:
            _, downstream = store.get_edges_for_doc(doc.doc_id)
            for edge in downstream:
                if edge.target_doc_id in superseded:
                    result.append(
                        {
                            "source_doc_id": edge.source_doc_id,
                            "target_doc_id": edge.target_doc_id,
                            "relation": edge.relation,
                            "target_status": "Superseded",
                        }
                    )
        return result

    # ----------------------------------------------------------------
    # 关联文档
    # ----------------------------------------------------------------

    def get_related(self, doc_id: str) -> list[dict]:
        """返回与 doc_id 直接相连的所有文档节点。"""
        upstream, downstream = store.get_edges_for_doc(doc_id)
        seen: set[str] = set()
        result: list[dict] = []
        for edge in upstream + downstream:
            other = edge.source_doc_id if edge.target_doc_id == doc_id else edge.target_doc_id
            if other in seen or other == doc_id:
                continue
            seen.add(other)
            doc = store.get_document(other)
            if doc:
                result.append(self._doc_to_node(doc))
        return result

    # ----------------------------------------------------------------
    # 格式转换
    # ----------------------------------------------------------------

    def _doc_to_node(self, doc: DocumentNode) -> dict:
        section_count = len(store.get_sections(doc.doc_id))
        return {
            "id": doc.doc_id,
            "label": doc.doc_id,
            "title": f"{doc.title}\n{doc.department or ''} / {doc.doc_type or ''}\nv{doc.version or '?'} | {doc.status or 'Active'}",
            "group": doc.department or "未分类",
            "color": _dept_color(doc.department),
            "shape": _node_shape(doc.doc_type),
            "size": max(20, min(50, 20 + section_count * 2)),
            "meta": {
                "doc_type": doc.doc_type,
                "department": doc.department,
                "system_level": doc.system_level,
                "version": doc.version,
                "status": doc.status,
            },
        }

    def _edge_to_vis(self, edge: DocumentEdge) -> dict:
        return {
            "from": edge.source_doc_id,
            "to": edge.target_doc_id,
            "label": edge.relation or "",
            "dashes": edge.relation in _MEDIUM_RISK_RELATIONS if edge.relation else False,
            "arrows": "to",
            "title": f"{edge.relation} (confidence={edge.confidence:.2f})" if edge.confidence else edge.relation,
        }


# ---- 全局单例（lazy init）-----------------------------------------
_graph: DocumentGraph | None = None


def get_graph() -> DocumentGraph:
    global _graph
    if _graph is None:
        _graph = DocumentGraph()
    return _graph


_MEDIUM_RISK_RELATIONS = {"references", "supersedes", "allocated_to"}
