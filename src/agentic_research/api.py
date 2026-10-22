"""FastAPI service for the agentic research part."""

from functools import lru_cache

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from . import DISCLAIMER, __version__
from .config import Settings, get_settings
from .contracts import ProviderError, ResearchRequest, ResearchResponse
from .research import ResearchService
from .wiring import (
    MissingAPIKeyError,
    build_llm,
    build_risk_provider,
    build_vector_store,
)

app = FastAPI(
    title="Codyssey Agentic Research API",
    version=__version__,
    description=DISCLAIMER,
)


@lru_cache
def _build_service() -> ResearchService:
    settings = get_settings()
    return ResearchService(
        build_vector_store(settings),
        build_llm(settings),
        build_risk_provider(settings),
        settings,
    )


def get_service() -> ResearchService | None:
    """None when a configured provider cannot start (e.g. missing API key)."""
    try:
        return _build_service()
    except MissingAPIKeyError:
        return None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    ready: bool
    llm_provider: str | None
    llm_api_key_configured: bool
    news_csv_count: int
    vector_store_documents: int
    risk_tag_count: int
    disclaimer: str


@app.get("/health", response_model=HealthResponse)
def health(
    settings: Settings = Depends(get_settings),
    service: ResearchService | None = Depends(get_service),
) -> HealthResponse:
    news_dir = settings.news_dir
    news_csv_count = len(list(news_dir.glob("*.csv"))) if news_dir.is_dir() else 0
    documents = service.store.count() if service else 0
    return HealthResponse(
        status="ok",
        service="agentic-research",
        version=__version__,
        ready=documents > 0,
        llm_provider=service.llm.name if service else None,
        llm_api_key_configured=settings.openai_api_key is not None,
        news_csv_count=news_csv_count,
        vector_store_documents=documents,
        risk_tag_count=len(service.risk_provider) if service else 0,
        disclaimer=DISCLAIMER,
    )


@app.post(
    "/research",
    response_model=ResearchResponse,
    responses={
        502: {"description": "LLM·임베딩 제공자 호출 실패"},
        503: {"description": "LLM 미설정 또는 벡터 저장소가 비어 있음"},
    },
)
def research(
    request: ResearchRequest,
    service: ResearchService | None = Depends(get_service),
) -> ResearchResponse:
    if service is None:
        raise HTTPException(503, "LLM/embedding provider is not configured")
    if service.store.count() == 0:
        raise HTTPException(
            503, "vector store is empty: run `python -m agentic_research.ingest`"
        )
    try:
        return service.run(request)
    except ProviderError as error:
        raise HTTPException(502, str(error)) from error
