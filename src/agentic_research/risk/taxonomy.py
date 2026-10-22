"""Risk types, lifetimes, ETF macro mapping and keyword rules (Notion D4, D8).

`risk_type` is free text in the evaluation-xai contract; this module is the
agreed vocabulary on our side.
"""

from typing import Literal

RiskType = Literal[
    "earnings_shock",
    "regulation",
    "geopolitical",
    "price_shock",
    "litigation",
    "macro_rate",
]

DEFAULT_TTL_DAYS: dict[RiskType, int] = {
    "earnings_shock": 10,
    "regulation": 30,
    "litigation": 30,
    "geopolitical": 10,
    "macro_rate": 20,
    "price_shock": 5,
}

# ETFs have no news file of their own; macro risks found in stock news are
# propagated to the ETFs that carry that exposure.
MACRO_ASSET_MAP: dict[RiskType, tuple[str, ...]] = {
    "macro_rate": ("TLT", "148070", "VNQ"),
    "geopolitical": ("SPY", "QQQ", "069500"),
}

# (risk_type, severity, keywords). Matching is case-insensitive substring.
KEYWORD_RULES: tuple[tuple[RiskType, float, tuple[str, ...]], ...] = (
    (
        "earnings_shock",
        0.6,
        (
            "어닝쇼크",
            "어닝 쇼크",
            "실적 쇼크",
            "실적쇼크",
            "적자 전환",
            "적자전환",
            "영업손실",
            "실적 부진",
            "earnings miss",
            "profit warning",
            "guidance cut",
        ),
    ),
    (
        "regulation",
        0.5,
        (
            "규제",
            "제재",
            "과징금",
            "수출 통제",
            "수출통제",
            "반독점",
            "공정위",
            "antitrust",
            "sanction",
            "export control",
        ),
    ),
    (
        "litigation",
        0.5,
        ("소송", "피소", "특허 침해", "lawsuit", "litigation"),
    ),
    (
        "geopolitical",
        0.5,
        ("전쟁", "관세", "지정학", "분쟁", "tariff", "geopolitic"),
    ),
    (
        "macro_rate",
        0.4,
        ("금리 인상", "기준금리", "긴축", "국채 금리", "rate hike", "inflation"),
    ),
)

# Disclosures whose price reaction is classified as an earnings event.
EARNINGS_FILING_PREFIXES = ("10-K", "10-Q")
EARNINGS_DART_KEYWORDS = (
    "영업(잠정)실적",
    "매출액또는손익구조",
    "사업보고서",
    "반기보고서",
    "분기보고서",
)


def match_keywords(text: str) -> list[tuple[RiskType, float]]:
    """Return each risk type whose keywords appear in `text`, once per type."""
    lowered = text.lower()
    return [
        (risk_type, severity)
        for risk_type, severity, keywords in KEYWORD_RULES
        if any(keyword.lower() in lowered for keyword in keywords)
    ]
