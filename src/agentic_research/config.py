"""Environment-driven settings. Secrets come from `.env`, never from code.

Pending team decisions (Notion "Agentic Research 구현 계획 · 의사결정", D1~D12) are
settings with conservative defaults so a decision only changes `.env`.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from .risk.taxonomy import DEFAULT_TTL_DAYS, RiskType


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AGENT_", env_file=".env", extra="ignore"
    )

    # Inputs produced by data-pipeline and artifacts produced here.
    news_dir: Path = Path("data/raw/news")
    returns_path: Path = Path("data/processed/returns.parquet")
    chroma_dir: Path = Path("artifacts/chroma")
    risk_tags_path: Path = Path("artifacts/risk_tags.jsonl")

    openai_api_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENAI_API_KEY", "AGENT_OPENAI_API_KEY"),
    )
    # D1, D2: "rule"/"hash" run without any API key (CI, offline demo).
    llm_provider: Literal["rule", "openai"] = "rule"
    llm_model: str = "gpt-4o-mini"
    llm_timeout_s: float = Field(default=20.0, gt=0)
    embedding_provider: Literal["hash", "openai"] = "hash"
    embedding_model: str = "text-embedding-3-small"

    # Retrieval and Self-Correction loop bounds (prevent infinite loops).
    top_k: int = Field(default=6, ge=1, le=20)
    # Cosine similarity scale depends on the embedding; tune together with D2.
    relevance_threshold: float = Field(default=0.3, ge=0, le=1)
    min_relevant_docs: int = Field(default=2, ge=1)
    max_rewrites: int = Field(default=2, ge=0, le=5)
    # Latency budget is 5 s per request (Notion D13). Measured with gpt-4o-mini:
    # LLM planner ~1.0 s, one analyst revision ~3-4 s. Both off by default;
    # the verifier still drops every unsupported claim.
    llm_planner: bool = False
    max_revisions: int = Field(default=0, ge=0, le=5)

    # D4, D7: risk tag thresholds and lifetimes.
    price_shock_z: float = Field(default=3.0, gt=0)
    earnings_shock_z: float = Field(default=2.0, gt=0)
    shock_lookback_days: int = Field(default=60, ge=10)
    risk_ttl_days: dict[RiskType, int] = Field(
        default_factory=lambda: dict(DEFAULT_TTL_DAYS)
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
