"""The 12-asset universe shared with data-pipeline, and market-time helpers."""

import re
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")
NEW_YORK = ZoneInfo("America/New_York")

ASSET_NAMES: dict[str, str] = {
    "SPY": "S&P500 ETF",
    "QQQ": "나스닥100 ETF",
    "AAPL": "애플",
    "MSFT": "마이크로소프트",
    "NVDA": "엔비디아",
    "TLT": "미국 장기채 ETF",
    "GLD": "금 ETF",
    "VNQ": "미국 리츠 ETF",
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "069500": "KODEX 200",
    "148070": "국고채10년 ETF",
}

# Lower-case aliases used to find assets mentioned in a free-text question.
# Ambiguous short forms ("MS") are deliberately absent (0929 feedback).
ASSET_ALIASES: dict[str, str] = {
    **{ticker.lower(): ticker for ticker in ASSET_NAMES},
    "삼성전자": "005930",
    "하이닉스": "000660",
    "apple": "AAPL",
    "애플": "AAPL",
    "microsoft": "MSFT",
    "마이크로소프트": "MSFT",
    "nvidia": "NVDA",
    "엔비디아": "NVDA",
    "코스피200": "069500",
    "kodex 200": "069500",
}


def is_korean(asset_id: str) -> bool:
    return asset_id.isdigit()


def market_close(asset_id: str, day: date) -> datetime:
    """Close of the regular session on `day` (KRX 15:30 KST, US 16:00 ET)."""
    if is_korean(asset_id):
        return datetime.combine(day, time(15, 30), tzinfo=KST)
    return datetime.combine(day, time(16, 0), tzinfo=NEW_YORK)


def price_source_url(asset_id: str) -> str:
    """Public page of the price series a price-based tag was computed from."""
    if is_korean(asset_id):
        return f"https://finance.naver.com/item/sise_day.naver?code={asset_id}"
    return f"https://finance.yahoo.com/quote/{asset_id}/history/"


# A Korean alias counts only as a whole word, optionally followed by a particle,
# so "애플리케이션" does not match "애플" (0929 feedback) but "삼성전자의" matches.
_PARTICLES = "의|은|는|이|가|을|를|과|와|에|도|로|으로|에서"


def _alias_pattern(alias: str) -> re.Pattern[str]:
    if alias.isascii():
        return re.compile(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])")
    return re.compile(rf"(?<![가-힣]){re.escape(alias)}(?:{_PARTICLES})?(?![가-힣])")


_PATTERNS = tuple(
    (_alias_pattern(alias), asset) for alias, asset in ASSET_ALIASES.items()
)


def assets_in_text(text: str) -> list[str]:
    """Assets mentioned in free text, in universe order."""
    lowered = text.lower()
    found = {asset for pattern, asset in _PATTERNS if pattern.search(lowered)}
    return [asset for asset in ASSET_NAMES if asset in found]
