from fastapi.testclient import TestClient

from agentic_research.api import app
from agentic_research.config import Settings, get_settings


def _client(settings: Settings) -> TestClient:
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app)


def teardown_function():
    app.dependency_overrides.clear()


def test_health_reports_key_presence_without_leaking_secret(tmp_path):
    secret = "sk-test-should-never-appear"
    settings = Settings(news_dir=tmp_path, OPENAI_API_KEY=secret, _env_file=None)

    response = _client(settings).get("/health")

    assert response.status_code == 200
    assert response.json()["llm_api_key_configured"] is True
    assert secret not in response.text


def test_health_counts_only_news_csv_files(tmp_path):
    (tmp_path / "005930.csv").write_text("종목명,제목\n", encoding="utf-8")
    (tmp_path / "AAPL.csv").write_text("종목명,제목\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignored", encoding="utf-8")
    settings = Settings(news_dir=tmp_path, _env_file=None)

    body = _client(settings).get("/health").json()

    assert body["news_csv_count"] == 2
    assert body["llm_api_key_configured"] is False


def test_health_tolerates_missing_news_dir(tmp_path):
    settings = Settings(news_dir=tmp_path / "absent", _env_file=None)

    body = _client(settings).get("/health").json()

    assert body["status"] == "ok"
    assert body["news_csv_count"] == 0
