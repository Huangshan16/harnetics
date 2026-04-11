# [INPUT]: 依赖 fastapi.testclient 的 TestClient，依赖 harnetics.app 的 create_app
# [OUTPUT]: 提供根路径、healthcheck 与 app.state.settings 装配行为的回归测试
# [POS]: tests 目录中的首个冒烟测试，验证应用骨架可被导入、首页入口、响应 /health，并挂载默认 settings
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from pathlib import Path

from fastapi.testclient import TestClient

from harnetics.app import create_app
from harnetics.config import Settings, get_settings


def test_healthcheck_returns_ok() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_redirects_to_documents() -> None:
    client = TestClient(create_app())

    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] in ("/documents", "/dashboard")


def test_app_state_settings_matches_defaults() -> None:
    app = create_app()

    assert isinstance(app.state.settings, Settings)
    assert app.state.settings == get_settings()


def test_settings_separate_legacy_and_graph_databases() -> None:
    settings = Settings()

    assert settings.database_path != settings.graph_db_path


def test_get_settings_loads_dotenv(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("HARNETICS_LLM_MODEL", raising=False)
    monkeypatch.delenv("HARNETICS_LLM_API_KEY", raising=False)
    monkeypatch.delenv("HARNETICS_EMBEDDING_MODEL", raising=False)
    monkeypatch.delenv("HARNETICS_EMBEDDING_API_KEY", raising=False)
    (tmp_path / ".env").write_text(
        "\n".join(
            [
                "HARNETICS_LLM_MODEL=deepseek/deepseek-chat",
                "HARNETICS_LLM_API_KEY=sk-llm",
                "HARNETICS_EMBEDDING_MODEL=text-embedding-3-small",
                "HARNETICS_EMBEDDING_API_KEY=sk-emb",
            ]
        ),
        encoding="utf-8",
    )

    settings = get_settings()

    assert settings.llm_model == "deepseek/deepseek-chat"
    assert settings.llm_api_key == "sk-llm"
    assert settings.embedding_model == "text-embedding-3-small"
    assert settings.embedding_api_key == "sk-emb"
