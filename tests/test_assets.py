import pytest

from agentic_research.assets import assets_in_text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("삼성전자의 3분기 실적은?", ["005930"]),
        ("AAPL? 그리고 엔비디아는", ["AAPL", "NVDA"]),
        ("SK하이닉스 HBM 전망", ["000660"]),
        # 0929 feedback: these must not match AAPL / MSFT.
        ("애플리케이션 시장 성장", []),
        ("모건스탠리(MS) 보고서", []),
    ],
)
def test_assets_in_text(text, expected):
    assert assets_in_text(text) == expected
