from pathlib import Path

import pytest

from agentic_research.config import Settings
from agentic_research.corpus.embeddings import HashEmbedding
from agentic_research.corpus.news import CsvNewsSource
from agentic_research.corpus.vectorstore import ChromaVectorStore

FIXTURE_NEWS = Path(__file__).parent / "fixtures" / "news"


def make_settings(tmp_path: Path, **overrides) -> Settings:
    values = {
        "news_dir": FIXTURE_NEWS,
        "chroma_dir": tmp_path / "chroma",
        "risk_tags_path": tmp_path / "risk_tags.jsonl",
        "returns_path": tmp_path / "returns.parquet",
        "_env_file": None,
    }
    values.update(overrides)
    return Settings(**values)


@pytest.fixture
def records():
    return CsvNewsSource(FIXTURE_NEWS).load()


@pytest.fixture
def store(tmp_path, records):
    vector_store = ChromaVectorStore(tmp_path / "chroma", HashEmbedding())
    vector_store.upsert(records)
    return vector_store
