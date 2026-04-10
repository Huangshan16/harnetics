/**
 * [INPUT]: 依赖 vis-network 全局变量（由模板内联加载）
 * [OUTPUT]: 导出图谱初始化辅助函数（供模板页调用）
 * [POS]: web/static/js 的图谱工具模块，为 graph/view.html 提供渐进增强
 * [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md
 */

// graph.js — vis-network 渐进增强工具
// 核心渲染逻辑已内联于 graph/view.html（避免模板与脚本频繁切换）
// 本文件提供导出供未来模块化使用

window.HarneticsGraph = {
  /**
   * 根据部门名称返回色值
   * @param {string} dept
   * @returns {string} hex color
   */
  deptColor(dept) {
    const palette = {
      '推进': '#6366f1',
      '结构': '#f59e0b',
      '电气': '#10b981',
      '热控': '#ef4444',
      'GNC': '#3b82f6',
      '系统': '#8b5cf6',
      '质量': '#ec4899',
    };
    for (const [key, color] of Object.entries(palette)) {
      if (dept && dept.includes(key)) return color;
    }
    return '#94a3b8';
  },

  /**
   * 高亮指定节点及其一跳邻居
   * @param {vis.Network} network
   * @param {vis.DataSet} nodes
   * @param {vis.DataSet} edges
   * @param {string} nodeId
   */
  highlightNeighbors(network, nodes, edges, nodeId) {
    const connectedNodes = network.getConnectedNodes(nodeId);
    const connectedEdges = network.getConnectedEdges(nodeId);
    const allNodes = nodes.getIds();
    const allEdges = edges.getIds();

    const nodeUpdates = allNodes.map(id => ({
      id,
      opacity: (id === nodeId || connectedNodes.includes(id)) ? 1.0 : 0.15,
    }));
    const edgeUpdates = allEdges.map(id => ({
      id,
      opacity: connectedEdges.includes(id) ? 1.0 : 0.05,
    }));

    nodes.update(nodeUpdates);
    edges.update(edgeUpdates);
  },

  /**
   * 重置所有节点/边不透明度
   */
  resetHighlight(nodes, edges) {
    nodes.update(nodes.getIds().map(id => ({ id, opacity: 1.0 })));
    edges.update(edges.getIds().map(id => ({ id, opacity: 1.0 })));
  },
};
