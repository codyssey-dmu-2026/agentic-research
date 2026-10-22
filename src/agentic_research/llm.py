"""LLM implementations (Notion D1).

`RuleBasedLLM` is the keyless implementation: deterministic heuristics used by
CI and offline demos. Its output is labelled with `llm_provider="rule"` in every
response so it is never mistaken for model reasoning.
"""

import re
from collections.abc import Sequence
from statistics import fmean
from typing import get_args

from pydantic import BaseModel, Field, SecretStr

from .assets import ASSET_NAMES
from .contracts import Draft, Hit, NewsRecord, ProviderError, RiskAssessment
from .risk.taxonomy import RiskType, match_keywords

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


_SYSTEM = (
    "너는 금융 리서치 에이전트다. 제공된 문서만 근거로 사용하고, 사전 지식이나 "
    "기준 시점 이후의 정보를 사용하지 마라. 교육 목적이며 투자 조언이 아니다."
)


class _Plan(BaseModel):
    queries: list[str] = Field(min_length=1, max_length=4)


class _Rewrite(BaseModel):
    query: str


class _Support(BaseModel):
    supported: list[bool]


class _Risks(BaseModel):
    risks: list[RiskAssessment]


def _evidence_block(evidence: Sequence[Hit]) -> str:
    lines = []
    for index, hit in enumerate(evidence, start=1):
        record = hit.record
        lines.append(
            f"[{index}] ({record.asset_id}, {record.source_type}, "
            f"{record.published_at.date()}) {record.text}"
        )
    return "\n".join(lines)


class OpenAILLM:
    def __init__(self, model: str, api_key: SecretStr, timeout_s: float) -> None:
        from langchain_openai import ChatOpenAI

        self.name = f"openai-{model}"
        self._chat = ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=0,
            timeout=timeout_s,
            max_retries=1,
        )

    def _ask(self, schema: type[BaseModel], instruction: str, content: str):
        # Strict JSON schema: function calling returned a bare bool for a list.
        structured = self._chat.with_structured_output(
            schema, method="json_schema", strict=True
        )
        try:
            return structured.invoke(
                [("system", f"{_SYSTEM}\n{instruction}"), ("human", content)]
            )
        except Exception as error:  # provider, network, or schema failure
            raise ProviderError(f"{self.name}: {error}") from error

    def plan(self, question: str, assets: Sequence[str]) -> list[str]:
        names = ", ".join(f"{a}({ASSET_NAMES.get(a, a)})" for a in assets) or "없음"
        result = self._ask(
            _Plan,
            "질문을 뉴스·공시 벡터 검색용 검색어 1~3개로 분해하라. "
            "한국어 기사와 영어 공시가 섞여 있으니 필요하면 두 언어를 모두 써라.",
            f"질문: {question}\n대상 자산: {names}",
        )
        return result.queries

    def rewrite(self, query: str, feedback: str) -> str:
        result = self._ask(
            _Rewrite,
            "검색 결과가 부적절했다. 같은 정보를 찾되 다른 표현의 검색어 하나를 만들어라.",
            f"기존 검색어: {query}\n문제: {feedback}",
        )
        return result.query

    def analyze(
        self, question: str, evidence: Sequence[Hit], feedback: str | None
    ) -> Draft:
        instruction = (
            "문서를 근거로 투자 의견 초안을 작성하라. opinion은 '비중 확대', '유지', "
            "'비중 축소' 중 하나다. 모든 claim은 근거 문서 번호를 citations에 "
            "하나 이상 넣어야 하며, 문서에 없는 내용은 주장하지 마라. "
            "claim은 최대 4개, 각 한 문장. summary는 두 문장 이내."
        )
        if feedback:
            instruction += f"\n이전 초안의 문제를 반드시 고쳐라:\n{feedback}"
        return self._ask(
            Draft, instruction, f"질문: {question}\n문서:\n{_evidence_block(evidence)}"
        )

    def check_support(self, pairs: Sequence[tuple[str, str]]) -> list[bool]:
        if not pairs:
            return []
        items = "\n\n".join(
            f"#{i} 주장: {claim}\n근거: {evidence}"
            for i, (claim, evidence) in enumerate(pairs, start=1)
        )
        result = self._ask(
            _Support,
            f"각 항목의 근거가 주장을 직접 뒷받침하면 true, 아니면 false. "
            f"정확히 {len(pairs)}개를 순서대로 답하라.",
            items,
        )
        # A missing verdict is treated as unsupported.
        verdicts = list(result.supported[: len(pairs)])
        return verdicts + [False] * (len(pairs) - len(verdicts))

    def assess_risk(self, record: NewsRecord) -> list[RiskAssessment]:
        types = ", ".join(get_args(RiskType))
        result = self._ask(
            _Risks,
            f"기사·공시에서 해당 자산의 투자 위험 이벤트를 찾아라. risk_type은 {types} "
            "중 하나다. 위험이 없으면 빈 목록. 정기보고서(사업·분기·반기) 제출 "
            "자체는 위험 이벤트가 아니다. severity는 0~1(1=치명적), "
            "confidence는 판단 확신도다.",
            f"자산: {record.asset_id}\n{record.text}",
        )
        return result.risks
