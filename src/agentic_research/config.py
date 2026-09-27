"""Environment-driven settings. Secrets come from `.env`, never from code."""

from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AGENT_", env_file=".env", extra="ignore"
    )

    news_dir: Path = Path("data/raw/news")
    chroma_dir: Path = Path("artifacts/chroma")
    openai_api_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENAI_API_KEY", "AGENT_OPENAI_API_KEY"),
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
