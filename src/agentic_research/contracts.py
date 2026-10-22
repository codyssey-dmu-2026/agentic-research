"""Data shapes exchanged between ports, the workflow, and the API.

`RiskTag` is re-exported from evaluation-xai so there is exactly one schema
(Epic #1: no fork). Everything else here is owned by this service.
"""

import hashlib
from collections.abc import Iterable
from datetime import datetime
from typing import Any, Literal

from evaluation_xai.contracts import RiskTag
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from . import DISCLAIMER
from .assets import ASSET_NAMES
from .risk.taxonomy import RiskType

__all__ = [
    "Citation",
    "Claim",
    "Draft",
    "Hit",
    "NewsRecord",
    "Opinion",
    "ResearchRequest",
    "ResearchResponse",
    "ProviderError",
    "RiskAssessment",
    "RiskTag",
    "SourceType",
    "TraceEvent",
    "merge_hits",
    "require_aware",
]

SourceType = Literal["news", "dart", "sec"]
Opinion = Literal["비중 확대", "유지", "비중 축소"]


class ProviderError(RuntimeError):
    """An external model call failed or returned output outside its schema."""


def require_aware(moment: datetime, name: str = "as_of") -> datetime:
    """Point-in-time queries are meaningless without a timezone."""
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError(f"{name} must include a timezone")
    return moment


class NewsRecord(BaseModel):
    """One news article or disclosure for one asset."""

    model_config = ConfigDict(frozen=True)

    asset_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    summary: str | None = None
    published_at: AwareDatetime
    # When the agent may first use the record. Never earlier than published_at.
    available_at: AwareDatetime
    source_url: str = Field(pattern=r"^https?://")
    source_type: SourceType

    @property
    def doc_id(self) -> str:
        # The same article can be filed under several assets; keep one per asset.
        key = f"{self.asset_id}|{self.source_url}".encode()
        return hashlib.sha1(key).hexdigest()[:20]

    @property
    def text(self) -> str:
        return f"{self.title}\n{self.summary}" if self.summary else self.title

    @property
    def search_text(self) -> str:
        # Titles rarely repeat the company name (DART report names never do).
        return f"{ASSET_NAMES.get(self.asset_id, self.asset_id)} {self.text}"


class Hit(BaseModel):
    record: NewsRecord
    score: float = Field(ge=0, le=1)


def merge_hits(hits: Iterable[Hit]) -> list[Hit]:
    """One hit per source URL with its best score, best first."""
    best: dict[str, Hit] = {}
    for hit in hits:
        url = hit.record.source_url
        if url not in best or hit.score > best[url].score:
            best[url] = hit
    return sorted(best.values(), key=lambda hit: hit.score, reverse=True)


class RiskAssessment(BaseModel):
    """A risk event the LLM (or keyword rules) found in one record."""

    risk_type: RiskType
    severity: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    rationale: str = ""


class Claim(BaseModel):
    text: str = Field(min_length=1)
    # 1-based indices into the evidence list shown to the analyst.
    citations: list[int] = Field(default_factory=list)


class Draft(BaseModel):
    opinion: Opinion
    confidence: float = Field(ge=0, le=1)
    summary: str
    claims: list[Claim] = Field(default_factory=list)


class TraceEvent(BaseModel):
    node: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    elapsed_ms: int = Field(ge=0)


class ResearchRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "question": "삼성전자 최근 실적과 리스크는?",
                    "tickers": ["005930"],
                    "as_of": "2026-10-20T09:00:00+09:00",
                }
            ]
        },
    )

    question: str = Field(min_length=2, max_length=500)
    tickers: list[str] | None = Field(default=None, max_length=12)
    # Defaults to the request time. Only records available by then are used.
    as_of: AwareDatetime | None = None


class Citation(BaseModel):
    id: int
    title: str
    asset_id: str
    source_type: SourceType
    published_at: AwareDatetime
    source_url: str


class ResearchResponse(BaseModel):
    question: str
    as_of: AwareDatetime
    tickers: list[str]
    answer: str
    opinion: Opinion
    confidence: float = Field(ge=0, le=1)
    insufficient_evidence: bool
    claims: list[Claim]
    citations: list[Citation]
    risk_tags: list[RiskTag]
    trace: list[TraceEvent]
    rewrites: int
    revisions: int
    llm_provider: str
    elapsed_ms: int
    disclaimer: str = DISCLAIMER
