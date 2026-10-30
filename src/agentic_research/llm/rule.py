"""Keyless `LLMPort` (Notion D1): deterministic keyword heuristics.

Used by CI and offline demos. Its output is labelled with `llm_provider="rule"`
in every response so it is never mistaken for model reasoning.
"""

import re
from collections.abc import Sequence
from statistics import fmean

from ..assets import ASSET_NAMES
from ..contracts import Draft, Hit, NewsRecord, RiskAssessment
from ..risk.taxonomy import match_keywords

_TOKEN = re.compile(r"[0-9a-z가-힣]+")
_STOPWORDS = {
    "어때",
    "어떤가",
    "어떤가요",
    "어떻게",
    "무엇",
    "뭐야",
    "알려줘",
    "알려주세요",
    "최근",
    "관련",
    "대한",
    "있나",
    "있어",
    "the",
    "what",
    "is",
    "are",
    "of",
    "about",
}
_POSITIVE = ("호실적", "사상 최대", "최대 실적", "상향", "흑자", "beat", "record high")
# Query expansion used by the rule-based rewrite (Korean news + English filings).
_EXPANSIONS = {
    "실적": ("영업이익", "잠정실적", "분기보고서"),
    "리스크": ("규제", "소송", "위험"),
    "위험": ("규제", "소송"),
    "규제": ("제재", "수출", "통제"),
    "반독점": ("과징금", "소송"),
    "전망": ("실적", "가이던스"),
    "earnings": ("10-q", "10-k"),
}


def _tokens(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


def _strip_particle(token: str) -> str:
    for particle in ("은", "는", "이", "가", "을", "를", "의", "와", "과", "에"):
        if token.endswith(particle) and token[: -len(particle)] in _EXPANSIONS:
            return token[: -len(particle)]
    return token


class RuleBasedLLM:
    name = "rule"

    def plan(self, question: str, assets: Sequence[str]) -> list[str]:
        queries = [question]
        for asset in assets[:3]:
            queries.append(f"{ASSET_NAMES.get(asset, asset)} {asset} 실적 리스크 공시")
        return list(dict.fromkeys(queries))

    def rewrite(self, query: str, feedback: str) -> str:
        keywords = [
            _strip_particle(token)
            for token in _tokens(query)
            if token not in _STOPWORDS
        ]
        extra = [term for token in keywords for term in _EXPANSIONS.get(token, ())]
        rewritten = " ".join(dict.fromkeys(keywords + extra))
        return rewritten if rewritten and rewritten != query else f"{query} 공시"

    def analyze(
        self, question: str, evidence: Sequence[Hit], feedback: str | None
    ) -> Draft:
        used = list(evidence[:3])
        titles = " ".join(hit.record.text for hit in used)
        negative = len(match_keywords(titles))
        positive = sum(word.lower() in titles.lower() for word in _POSITIVE)
        if negative > positive:
            opinion = "비중 축소"
        elif positive > negative:
            opinion = "비중 확대"
        else:
            opinion = "유지"
        return Draft(
            opinion=opinion,
            confidence=round(min(1.0, fmean(hit.score for hit in used)), 2),
            summary=(
                f"근거 {len(used)}건 기준 의견: {opinion} "
                f"(위험 신호 {negative}건, 긍정 신호 {positive}건, 규칙 기반 분석)"
            ),
            claims=[
                {"text": hit.record.title, "citations": [index]}
                for index, hit in enumerate(used, start=1)
            ],
        )

    def check_support(self, pairs: Sequence[tuple[str, str]]) -> list[bool]:
        results = []
        for claim, evidence in pairs:
            claim_tokens = set(_tokens(claim))
            overlap = len(claim_tokens & set(_tokens(evidence)))
            results.append(bool(claim_tokens) and overlap / len(claim_tokens) >= 0.5)
        return results

    def assess_risk(self, record: NewsRecord) -> list[RiskAssessment]:
        return [
            RiskAssessment(
                risk_type=risk_type,
                severity=severity,
                confidence=0.5,
                rationale="키워드 규칙 일치",
            )
            for risk_type, severity in match_keywords(record.text)
        ]
