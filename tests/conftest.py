# [INPUT]: 依赖 pytest 的 tmp_path fixture、FastAPI app 工厂与导入/仓储边界
# [OUTPUT]: 提供 temp_db_path、fixture_root、temp_app 与 imported_fixture_app 夹具
# [POS]: tests 目录的共享测试支架，供 catalog 路由与导入场景复用
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from pathlib import Path
from types import SimpleNamespace

import pytest

from harnetics.app import create_app
from harnetics.importer import ImportService
from harnetics.repository import Repository


@pytest.fixture()
def temp_db_path(tmp_path: Path) -> Path:
    return tmp_path / "test.db"


@pytest.fixture()
def fixture_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture()
def temp_app(temp_db_path: Path, tmp_path: Path):
    app = create_app()
    repository = Repository(temp_db_path)
    app.state.repository = repository
    app.state.import_service = ImportService(repository)
    app.state.settings = SimpleNamespace(raw_upload_dir=tmp_path / "uploads")
    return app


@pytest.fixture()
def imported_fixture_app(temp_app):
    root = Path(__file__).resolve().parents[1]
    importer = temp_app.state.import_service
    importer.import_file(root / "fixtures" / "requirements" / "DOC-SYS-001.md")
    importer.import_file(root / "fixtures" / "design" / "DOC-DES-001.md")
    return temp_app
