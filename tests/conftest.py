# [INPUT]: 依赖 pytest 的 tmp_path fixture、graph store 初始化
# [OUTPUT]: 提供 graph_db_path、graph_conn、fixture_root、fixture_doc_paths 夹具
# [POS]: tests 目录的共享测试支架，供图谱/API/E2E 测试复用
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from pathlib import Path

import pytest

from harnetics.graph.store import init_db, get_connection


@pytest.fixture()
def fixture_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture()
def graph_db_path(tmp_path: Path) -> Path:
    """初始化图谱 SQLite 数据库并返回路径。"""
    db_path = tmp_path / "graph_test.db"
    init_db(db_path)
    return db_path


@pytest.fixture()
def graph_conn(graph_db_path: Path):
    """获取图谱数据库连接，测试结束后关闭。"""
    with get_connection(graph_db_path) as conn:
        yield conn


@pytest.fixture()
def fixture_doc_paths(fixture_root: Path) -> dict[str, Path]:
    """常用 fixture 文档路径映射。"""
    base = fixture_root / "fixtures"
    return {
        "sys_req": base / "requirements" / "DOC-SYS-001.md",
        "design": base / "design" / "DOC-DES-001.md",
        "template": base / "templates" / "DOC-TPL-001.md",
        "test_plan": base / "test_plans" / "DOC-TST-003.md",
        "icd": base / "icd" / "DOC-ICD-001.yaml",
    }
