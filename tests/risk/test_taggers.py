from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd

from agentic_research.contracts import NewsRecord, RiskAssessment
from agentic_research.llm.rule import RuleBasedLLM
from agentic_research.risk.taggers import (
    earnings_shock_tags,
    load_returns,
    price_shock_tags,
    text_tags,
)
from agentic_research.risk.taxonomy import DEFAULT_TTL_DAYS

GENERATED = datetime(2026, 10, 22, tzinfo=UTC)
COMMON = {"ttl_days": DEFAULT_TTL_DAYS, "generated_at": GENERATED, "version": "t"}


def returns_with_shock(asset, shock_day, shock=-0.12, days=120):
    index = pd.bdate_range("2024-06-03", periods=days)
    noise = np.random.default_rng(0).normal(0, 0.01, days)
    series = pd.Series(noise, index=index, name=asset)
    series[pd.Timestamp(shock_day)] = shock
    return series.to_frame()


def test_price_shock_tag_is_available_at_that_days_close():
    returns = returns_with_shock("005930", "2024-10-08")

    tags = price_shock_tags(returns, z_threshold=3.0, lookback=60, **COMMON)

    assert [t.available_at for t in tags] == [
        datetime.fromisoformat("2024-10-08T15:30:00+09:00")
    ]
    assert tags[0].risk_type == "price_shock"
    assert tags[0].mode == "historical_replay"
    assert tags[0].expires_at - tags[0].available_at == timedelta(days=5)


def test_price_shock_uses_us_close_for_us_assets():
    returns = returns_with_shock("SPY", "2024-10-08")

    tags = price_shock_tags(returns, z_threshold=3.0, lookback=60, **COMMON)

    assert tags[0].available_at == datetime.fromisoformat("2024-10-08T16:00:00-04:00")


def test_price_shock_does_not_depend_on_future_returns():
    returns = returns_with_shock("SPY", "2024-10-08")
    cutoff = pd.Timestamp("2024-10-10")
    future_changed = returns.copy()
    future_changed.loc[future_changed.index > cutoff, "SPY"] *= 5

    def up_to_cutoff(frame):
        tags = price_shock_tags(frame, z_threshold=3.0, lookback=60, **COMMON)
        return [t for t in tags if t.available_at.date() <= cutoff.date()]

    assert up_to_cutoff(returns) == up_to_cutoff(future_changed)


def test_forward_filled_holidays_do_not_change_tags():
    # data-pipeline fills a closed market with the previous price: a 0 return.
    sessions = returns_with_shock("069500", "2024-10-08")
    holidays = pd.DataFrame(
        {"069500": 0.0},
        index=pd.to_datetime(["2024-09-16", "2024-09-17", "2024-10-03"]),
    )
    with_holidays = pd.concat(
        [sessions.drop(holidays.index, errors="ignore"), holidays]
    )
    without = sessions.drop(holidays.index, errors="ignore")

    def tags(frame):
        return price_shock_tags(
            frame.sort_index(), z_threshold=3.0, lookback=60, **COMMON
        )

    assert tags(with_holidays) == tags(without)
    assert len(tags(without)) == 1


def _dart(title, day):
    published = datetime.fromisoformat(f"{day}T00:00:00+09:00")
    return NewsRecord(
        asset_id="005930",
        title=title,
        published_at=published,
        available_at=published + timedelta(days=1),
        source_url=f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={day}",
        source_type="dart",
    )


def test_earnings_shock_counts_only_the_first_session_after_availability():
    filing = _dart("영업(잠정)실적(공정공시)", "2024-10-08")
    same_day = returns_with_shock("005930", "2024-10-08")
    next_day = returns_with_shock("005930", "2024-10-09")

    before = earnings_shock_tags(
        [filing], same_day, z_threshold=2.0, lookback=60, **COMMON
    )
    after = earnings_shock_tags(
        [filing], next_day, z_threshold=2.0, lookback=60, **COMMON
    )

    assert before == []
    assert [t.available_at for t in after] == [
        datetime.fromisoformat("2024-10-09T15:30:00+09:00")
    ]
    assert after[0].risk_type == "earnings_shock"
    assert after[0].source_url == filing.source_url


def test_non_earnings_disclosures_do_not_create_earnings_tags():
    filing = _dart("최대주주등소유주식변동신고서", "2024-10-08")
    returns = returns_with_shock("005930", "2024-10-09")

    assert (
        earnings_shock_tags([filing], returns, z_threshold=2.0, lookback=60, **COMMON)
        == []
    )


class MacroLLM(RuleBasedLLM):
    def assess_risk(self, record):
        return [RiskAssessment(risk_type="macro_rate", severity=0.6, confidence=0.7)]


def test_macro_risks_propagate_to_mapped_etfs_and_sec_is_skipped(records):
    tags = text_tags(records, MacroLLM(), **COMMON)

    hynix_url = next(
        r.source_url for r in records if r.title.startswith("SK하이닉스, HBM")
    )
    assets = {t.asset_id for t in tags if t.source_url == hynix_url}
    assert assets == {"000660", "TLT", "148070", "VNQ"}
    assert not any("sec.gov" in t.source_url for t in tags)


def test_rebuilding_gives_the_same_tag_ids(records):
    first = text_tags(records, RuleBasedLLM(), **COMMON)
    later = {**COMMON, "generated_at": GENERATED + timedelta(days=7)}
    second = text_tags(records, RuleBasedLLM(), **later)

    assert first and [t.tag_id for t in first] == [t.tag_id for t in second]


def test_keyword_rules_classify_fixture_events(records):
    tags = text_tags(records, RuleBasedLLM(), **COMMON)

    found = {(t.asset_id, t.risk_type) for t in tags}
    assert ("005930", "earnings_shock") in found  # 어닝쇼크
    assert ("AAPL", "litigation") in found  # 반독점 소송
    assert ("000660", "litigation") in found  # DART 소송등의제기


def test_load_returns_strips_suffix_and_parses_dates(tmp_path):
    frame = pd.DataFrame(
        {"SPY_return": [0.01, -0.02]},
        index=pd.Index(["2024-01-02", "2024-01-03"], name="Date"),
    )
    path = tmp_path / "returns.parquet"
    frame.to_parquet(path)

    loaded = load_returns(path)

    assert list(loaded.columns) == ["SPY"]
    assert isinstance(loaded.index, pd.DatetimeIndex)
