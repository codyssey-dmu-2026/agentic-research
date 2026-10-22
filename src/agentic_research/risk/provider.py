"""RiskTagProvider backed by a JSONL file of evaluation-xai RiskTags.

The RL engine calls `vector()` once per step, so lookups are bounded by a
binary search on `available_at` instead of scanning every tag.
"""

import os
import tempfile
from bisect import bisect_right
from collections.abc import Iterable, Sequence
from datetime import datetime
from pathlib import Path

import numpy as np

from ..contracts import RiskTag, require_aware


class StoredRiskTagProvider:
    def __init__(self, tags: Iterable[RiskTag]) -> None:
        self._tags = sorted(tags, key=lambda tag: tag.available_at)
        self._available = [tag.available_at for tag in self._tags]
        self._max_lifetime = max(
            (tag.expires_at - tag.available_at for tag in self._tags), default=None
        )

    @classmethod
    def from_jsonl(cls, path: Path) -> "StoredRiskTagProvider":
        if not path.is_file():
            return cls([])
        with path.open(encoding="utf-8") as handle:
            return cls(
                RiskTag.model_validate_json(line) for line in handle if line.strip()
            )

    def __len__(self) -> int:
        return len(self._tags)

    def tags(
        self, decision_at: datetime, assets: Sequence[str] | None = None
    ) -> list[RiskTag]:
        require_aware(decision_at, "decision_at")
        if self._max_lifetime is None:
            return []
        # Usable tags became available within the longest lifetime before now.
        end = bisect_right(self._available, decision_at)
        start = bisect_right(self._available, decision_at - self._max_lifetime)
        wanted = None if assets is None else set(assets)
        return [
            tag
            for tag in self._tags[start:end]
            if tag.usable_at(decision_at) and (wanted is None or tag.asset_id in wanted)
        ]

    def vector(self, decision_at: datetime, asset_order: Sequence[str]) -> np.ndarray:
        position = {asset: index for index, asset in enumerate(asset_order)}
        values = np.zeros(len(asset_order), dtype=np.float64)
        for tag in self.tags(decision_at, asset_order):
            index = position[tag.asset_id]
            values[index] = max(values[index], tag.severity * tag.confidence)
        return values


def write_jsonl(tags: Iterable[RiskTag], path: Path) -> int:
    """Replace `path` atomically so readers never see a half-written file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, suffix=".tmp"
    ) as handle:
        for tag in tags:
            handle.write(tag.model_dump_json() + "\n")
            count += 1
    os.replace(handle.name, path)
    return count
