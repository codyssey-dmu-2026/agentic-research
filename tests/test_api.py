import pytest
from fastapi.testclient import TestClient

from agentic_research.agent.service import ResearchService
from agentic_research.api import app, get_service
from agentic_research.config import Settings, get_settings
from agentic_research.corpus.embeddings import HashEmbedding
from agentic_research.corpus.vectorstore import ChromaVectorStore
from agentic_research.llm.rule import RuleBasedLLM
from agentic_research.risk.provider import StoredRiskTagProvider
from conftest import make_settings

QUESTION = {
    "question": "삼성전자 3분기 실적 어때?",
    "as_of": "2024-12-31T00:00:00+09:00",
}


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def client(settings: Settings, service: ResearchService | None) -> TestClient:
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_service] = lambda: service
    return TestClient(app)


def research_service(store, settings):
    return ResearchService(store, RuleBasedLLM(), StoredRiskTagProvider([]), settings)


def test_research_returns_cited_report(tmp_path, store, records):
    settings = make_settings(tmp_path)

    response = client(settings, research_service(store, settings)).post(
        "/research", json=QUESTION
    )

    body = response.json()
    assert response.status_code == 200
    assert body["citations"]
    assert {c["source_url"] for c in body["citations"]} <= {
        r.source_url for r in records
    }
    assert [e["node"] for e in body["trace"]][0] == "planner"
    assert "투자 조언" in body["disclaimer"]


def test_research_is_503_when_vector_store_is_empty(tmp_path):
    settings = make_settings(tmp_path)
    empty = ChromaVectorStore(tmp_path / "empty", HashEmbedding())

    response = client(settings, research_service(empty, settings)).post(
        "/research", json=QUESTION
    )

    assert response.status_code == 503
    assert "ingest" in response.json()["detail"]


def test_research_is_503_when_provider_is_not_configured(tmp_path):
    response = client(make_settings(tmp_path), None).post("/research", json=QUESTION)

    assert response.status_code == 503


def test_research_rejects_naive_as_of(tmp_path, store):
    settings = make_settings(tmp_path)

    response = client(settings, research_service(store, settings)).post(
        "/research", json={**QUESTION, "as_of": "2024-12-31T00:00:00"}
    )

    assert response.status_code == 422


def test_health_reports_store_readiness_without_leaking_secret(tmp_path, store):
    secret = "sk-test-should-never-appear"
    settings = make_settings(tmp_path, OPENAI_API_KEY=secret)

    response = client(settings, research_service(store, settings)).get("/health")

    body = response.json()
    assert response.status_code == 200
    assert secret not in response.text
    assert body["llm_api_key_configured"] is True
    assert body["ready"] is True
    assert body["vector_store_documents"] == store.count()
    assert body["news_csv_count"] == 3
    assert body["llm_provider"] == "rule"


def test_health_is_not_ready_without_documents_or_provider(tmp_path):
    settings = make_settings(tmp_path, news_dir=tmp_path / "absent")

    body = client(settings, None).get("/health").json()

    assert body["status"] == "ok"
    assert body["ready"] is False
    assert body["news_csv_count"] == 0
    assert body["llm_provider"] is None
