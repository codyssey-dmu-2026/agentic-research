"""OpenAI chat model behind `LLMPort` (Notion D1), with strict structured output."""

from collections.abc import Sequence
from typing import get_args

from pydantic import BaseModel, Field, SecretStr

from ..assets import ASSET_NAMES
from ..contracts import Draft, Hit, NewsRecord, ProviderError, RiskAssessment
from ..risk.taxonomy import RiskType

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
