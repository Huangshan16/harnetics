# Quickstart: Verify Legacy Removal

**Feature**: 007-remove-legacy-workflow  
**Date**: 2026-04-19

## 移除后验证步骤

### 1. 检查零引用

```bash
# 源码中不应有 repository.py 引用
grep -r "from.*repository import\|import.*repository" src/ && echo "FAIL: legacy import found" || echo "PASS"

# 源码中不应有 harnetics.db 引用（Python 代码内）
grep -r "harnetics\.db" src/ --include="*.py" && echo "FAIL: legacy DB reference" || echo "PASS"

# 源码中不应有 Jinja2Templates
grep -r "Jinja2Templates" src/ && echo "FAIL: Jinja2 reference" || echo "PASS"
```

### 2. 运行测试

```bash
uv run pytest tests/ -q --tb=short
```

### 3. 前端构建

```bash
cd frontend && npm run build
```

### 4. 冒烟测试

```bash
uv run python -m harnetics.cli.main serve &
sleep 3
curl -s http://localhost:8000/health | python -m json.tool
curl -s http://localhost:8000/api/documents | python -m json.tool | head -20
kill %1
```

### 5. 依赖检查

```bash
# pyproject.toml 不应包含 jinja2
grep "jinja2" pyproject.toml && echo "FAIL" || echo "PASS: jinja2 removed"

# python-frontmatter 应保留
grep "python-frontmatter" pyproject.toml && echo "PASS: frontmatter kept" || echo "FAIL"
```

### 6. 文档一致性

```bash
# README 不应包含"旧版"双工作流叙事
grep -c "旧版\|兼容保留\|不要混用" README.md && echo "FAIL: legacy narrative remains" || echo "PASS"
```
