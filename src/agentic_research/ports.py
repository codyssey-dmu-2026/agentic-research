"""Boundaries between this service, teammates' modules and external providers.

Every implementation is chosen by `.env` in `wiring.py`. A replacement is
accepted when it passes the shared contract tests in `tests/contracts/`.
All point-in-time methods take a timezone-aware moment and must never return
anything that was not available at that moment.
"""

from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

import numpy as np

from .contracts import Draft, Hit, NewsRecord, RiskAssessment, RiskTag


class NewsSource(Protocol):
    """data-pipeline news and disclosures (`data/raw/news/*.csv`)."""

    def load(self, as_of: datetime | None = None) -> list[NewsRecord]: ...


class EmbeddingPort(Protocol):
    # Identifies the vector space; stores keep one collection per name.
    name: str

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class VectorStorePort(Protocol):
    def upsert(self, records: Sequence[NewsRecord]) -> None: ...

    def count(self) -> int: ...

    def search(
        self,
        queries: Sequence[str],
        as_of: datetime,
        assets: Sequence[str] | None = None,
        k: int = 6,
    ) -> list[Hit]:
        """Top `k` per query with `available_at <= as_of`, one hit per URL,
        best first."""
        ...


class LLMPort(Protocol):
    """Every reasoning step the agent delegates to a language model."""

    name: str

    def plan(self, question: str, assets: Sequence[str]) -> list[str]:
        """Break a question into 1-4 search queries."""
        ...

    def rewrite(self, query: str, feedback: str) -> str:
        """A different query for the same information need."""
        ...

    def analyze(
        self, question: str, evidence: Sequence[Hit], feedback: str | None
    ) -> Draft:
        """Opinion whose claims cite evidence by 1-based index."""
        ...

    def check_support(self, pairs: Sequence[tuple[str, str]]) -> list[bool]:
        """For each (claim, cited evidence text): does the evidence support it?"""
        ...

    def assess_risk(self, record: NewsRecord) -> list[RiskAssessment]: ...


class RiskTagProvider(Protocol):
    """What the RL engine and Safe-Guard consume (issue #7)."""

    def tags(
        self, decision_at: datetime, assets: Sequence[str] | None = None
    ) -> list[RiskTag]:
        """Tags with `available_at <= decision_at < expires_at`."""
        ...

    def vector(self, decision_at: datetime, asset_order: Sequence[str]) -> np.ndarray:
        """Per asset max(severity * confidence) of usable tags, 0 if none.

        Shape `(len(asset_order),)`, in exactly the given order.
        """
        ...

    def __len__(self) -> int: ...
