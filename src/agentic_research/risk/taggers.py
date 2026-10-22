"""Turn prices, disclosures and news into evaluation-xai RiskTags (issue #7).

Three sources, because RSS news only exists for recent weeks while the RL
training windows start in 2018:

* price_shock: abnormal daily move vs the trailing volatility (all 12 assets,
  full history).
* earnings_shock: abnormal move on the first session after an earnings filing
  (SEC 10-K/10-Q, DART earnings reports) became available.
* text: risk events the LLM (or keyword rules) finds in news and DART titles,
  propagated to ETFs for macro risk types.

All z-scores use only returns strictly before the day being scored.
"""

import hashlib
from bisect import bisect_right
from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd

from .. import __version__
from ..assets import market_close, price_source_url
from ..contracts import NewsRecord, RiskTag
from ..ports import LLMPort
from .taxonomy import (
    EARNINGS_DART_KEYWORDS,
    EARNINGS_FILING_PREFIXES,
    MACRO_ASSET_MAP,
    RiskType,
)

PRICE_CONFIDENCE = 0.9
EARNINGS_CONFIDENCE = 0.8


def tagger_version(llm_name: str) -> str:
    return f"agentic-research/{__version__}+{llm_name}"


def make_tag(
    *,
    asset_id: str,
    risk_type: RiskType,
    severity: float,
    confidence: float,
    published_at: datetime,
    available_at: datetime,
    source_url: str,
    generated_at: datetime,
    ttl_days: Mapping[RiskType, int],
    version: str,
) -> RiskTag:
    # Same evidence, asset and type always yield the same id (idempotent rebuild).
    key = "|".join(
        (asset_id, risk_type, source_url, published_at.astimezone(UTC).isoformat())
    )
    return RiskTag(
        tag_id="rt_" + hashlib.sha1(key.encode()).hexdigest()[:16],
        asset_id=asset_id,
        risk_type=risk_type,
        severity=round(severity, 4),
        confidence=round(confidence, 4),
        published_at=published_at,
        available_at=available_at,
        generated_at=generated_at,
        expires_at=available_at + timedelta(days=ttl_days[risk_type]),
        source_url=source_url,
        tagger_version=version,
        # Tags built after the fact must say so (evaluation-xai contract).
        mode="live" if generated_at <= available_at else "historical_replay",
    )


def load_returns(path: Path) -> pd.DataFrame:
    """data-pipeline `returns.parquet`: unnormalized log returns, `{asset}_return`."""
    frame = pd.read_parquet(path)
    if not isinstance(frame.index, pd.DatetimeIndex):
        date_columns = [c for c in frame.columns if str(c).lower() == "date"]
        if date_columns:
            frame = frame.set_index(date_columns[0])
    frame.index = pd.to_datetime(frame.index)
    frame.columns = [str(c).removesuffix("_return") for c in frame.columns]
    return frame.sort_index()


def zscores(returns: pd.Series, lookback: int) -> pd.Series:
    """Return divided by the trailing std of the previous `lookback` sessions."""
    # data-pipeline fills holidays with the previous price, i.e. a 0 return.
    sessions = returns[returns != 0].dropna()
    scale = sessions.shift(1).rolling(lookback, min_periods=lookback // 2).std()
    return (sessions / scale).dropna()


def _severity(z: float, threshold: float) -> float:
    # |z| at the threshold maps to 0.5, twice the threshold or more to 1.0.
    return min(1.0, abs(z) / (2 * threshold))


def price_shock_tags(
    returns: pd.DataFrame,
    *,
    z_threshold: float,
    lookback: int,
    ttl_days: Mapping[RiskType, int],
    generated_at: datetime,
    version: str,
) -> list[RiskTag]:
    tags = []
    for asset in returns.columns:
        scores = zscores(returns[asset], lookback)
        for day, z in scores[scores.abs() >= z_threshold].items():
            close = market_close(asset, day.date())
            tags.append(
                make_tag(
                    asset_id=asset,
                    risk_type="price_shock",
                    severity=_severity(z, z_threshold),
                    confidence=PRICE_CONFIDENCE,
                    published_at=close,
                    available_at=close,
                    source_url=price_source_url(asset),
                    generated_at=generated_at,
                    ttl_days=ttl_days,
                    version=version,
                )
            )
    return tags


def is_earnings_filing(record: NewsRecord) -> bool:
    if record.source_type == "sec":
        return record.title.startswith(EARNINGS_FILING_PREFIXES)
    if record.source_type == "dart":
        return any(keyword in record.title for keyword in EARNINGS_DART_KEYWORDS)
    return False


def earnings_shock_tags(
    records: Iterable[NewsRecord],
    returns: pd.DataFrame,
    *,
    z_threshold: float,
    lookback: int,
    ttl_days: Mapping[RiskType, int],
    generated_at: datetime,
    version: str,
) -> list[RiskTag]:
    sessions: dict[str, tuple[list[datetime], list[float]]] = {}
    tags = []
    for record in records:
        asset = record.asset_id
        if not is_earnings_filing(record) or asset not in returns.columns:
            continue
        if asset not in sessions:
            scores = zscores(returns[asset], lookback)
            closes = [market_close(asset, day.date()) for day in scores.index]
            sessions[asset] = (closes, scores.tolist())
        closes, scores = sessions[asset]
        # First session that closed after the filing became usable.
        index = bisect_right(closes, record.available_at)
        if index == len(closes) or abs(scores[index]) < z_threshold:
            continue
        tags.append(
            make_tag(
                asset_id=asset,
                risk_type="earnings_shock",
                severity=_severity(scores[index], z_threshold),
                confidence=EARNINGS_CONFIDENCE,
                published_at=record.published_at,
                available_at=closes[index],
                source_url=record.source_url,
                generated_at=generated_at,
                ttl_days=ttl_days,
                version=version,
            )
        )
    return tags


def text_tags(
    records: Iterable[NewsRecord],
    llm: LLMPort,
    *,
    ttl_days: Mapping[RiskType, int],
    generated_at: datetime,
    version: str,
) -> list[RiskTag]:
    tags = []
    for record in records:
        # SEC titles are only "{form} ({period})"; there is no text to read.
        if record.source_type == "sec":
            continue
        for found in llm.assess_risk(record):
            assets = (record.asset_id, *MACRO_ASSET_MAP.get(found.risk_type, ()))
            for asset in dict.fromkeys(assets):
                tags.append(
                    make_tag(
                        asset_id=asset,
                        risk_type=found.risk_type,
                        severity=found.severity,
                        confidence=found.confidence,
                        published_at=record.published_at,
                        available_at=record.available_at,
                        source_url=record.source_url,
                        generated_at=generated_at,
                        ttl_days=ttl_days,
                        version=version,
                    )
                )
    return tags


def deduplicate(tags: Sequence[RiskTag]) -> list[RiskTag]:
    """One tag per id, keeping the strongest signal."""
    best: dict[str, RiskTag] = {}
    for tag in tags:
        current = best.get(tag.tag_id)
        if current is None or (
            tag.severity * tag.confidence > current.severity * current.confidence
        ):
            best[tag.tag_id] = tag
    return sorted(best.values(), key=lambda tag: (tag.available_at, tag.tag_id))
