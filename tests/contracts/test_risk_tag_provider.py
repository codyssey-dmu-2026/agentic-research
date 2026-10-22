"""RiskTagProvider contract shared with the RL engine (issue #7)."""

from datetime import datetime, timedelta

import numpy as np
import pytest

from agentic_research.contracts import RiskTag
from agentic_research.risk.provider import StoredRiskTagProvider, write_jsonl

T0 = datetime.fromisoformat("2024-10-08T15:30:00+09:00")


def tag(tag_id, asset, severity, confidence, available_at=T0, days=5):
    return RiskTag(
        tag_id=tag_id,
        asset_id=asset,
        risk_type="price_shock",
        severity=severity,
        confidence=confidence,
        published_at=available_at,
        available_at=available_at,
        generated_at=available_at + timedelta(days=400),
        expires_at=available_at + timedelta(days=days),
        source_url="https://example.com/x",
        tagger_version="test",
        mode="historical_replay",
    )


def test_tag_is_usable_only_inside_its_half_open_window():
    provider = StoredRiskTagProvider([tag("a", "005930", 0.8, 1.0)])

    assert provider.tags(T0 - timedelta(seconds=1)) == []
    assert [t.tag_id for t in provider.tags(T0)] == ["a"]
    assert [t.tag_id for t in provider.tags(T0 + timedelta(days=4))] == ["a"]
    assert provider.tags(T0 + timedelta(days=5)) == []


def test_long_lived_tags_are_found_after_newer_short_ones():
    # Guards the binary-search window: an old long-lived tag is still usable.
    old = tag("old", "TLT", 0.5, 1.0, available_at=T0, days=30)
    new = tag("new", "SPY", 0.5, 1.0, available_at=T0 + timedelta(days=20), days=1)
    provider = StoredRiskTagProvider([new, old])

    usable = provider.tags(T0 + timedelta(days=20, hours=1))

    assert {t.tag_id for t in usable} == {"old", "new"}


def test_vector_follows_asset_order_with_max_signal_and_zero_default():
    provider = StoredRiskTagProvider(
        [
            tag("a", "005930", 0.8, 0.5),
            tag("b", "005930", 0.6, 1.0),
            tag("c", "AAPL", 0.2, 1.0),
        ]
    )

    vector = provider.vector(T0, ["AAPL", "SPY", "005930"])

    assert vector.shape == (3,)
    np.testing.assert_allclose(vector, [0.2, 0.0, 0.6])


def test_assets_filter():
    provider = StoredRiskTagProvider(
        [tag("a", "005930", 0.8, 1.0), tag("b", "AAPL", 0.8, 1.0)]
    )

    assert [t.asset_id for t in provider.tags(T0, ["AAPL"])] == ["AAPL"]


def test_naive_decision_time_is_rejected():
    provider = StoredRiskTagProvider([tag("a", "005930", 0.8, 1.0)])

    with pytest.raises(ValueError, match="timezone"):
        provider.vector(datetime(2024, 10, 8), ["005930"])


def test_jsonl_round_trip_preserves_tags(tmp_path):
    tags = [tag("a", "005930", 0.8, 1.0), tag("b", "AAPL", 0.3, 0.9)]
    path = tmp_path / "tags.jsonl"

    write_jsonl(tags, path)
    loaded = StoredRiskTagProvider.from_jsonl(path)

    assert loaded.tags(T0) == tags


def test_missing_file_means_no_tags(tmp_path):
    provider = StoredRiskTagProvider.from_jsonl(tmp_path / "absent.jsonl")

    assert len(provider) == 0
    np.testing.assert_array_equal(provider.vector(T0, ["SPY"]), [0.0])
