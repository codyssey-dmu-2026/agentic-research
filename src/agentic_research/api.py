"""FastAPI service for the agentic research part."""

from fastapi import Depends, FastAPI
from pydantic import BaseModel

from . import DISCLAIMER, __version__
from .config import Settings, get_settings

app = FastAPI(
    title="Codyssey Agentic Research API",
    version=__version__,
    description=DISCLAIMER,
)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    llm_api_key_configured: bool
    news_csv_count: int
    disclaimer: str


@app.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    news_dir = settings.news_dir
    news_csv_count = len(list(news_dir.glob("*.csv"))) if news_dir.is_dir() else 0
    return HealthResponse(
        status="ok",
        service="agentic-research",
        version=__version__,
        llm_api_key_configured=settings.openai_api_key is not None,
        news_csv_count=news_csv_count,
        disclaimer=DISCLAIMER,
    )
