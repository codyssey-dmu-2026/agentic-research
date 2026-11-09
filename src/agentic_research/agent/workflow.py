"""LangGraph plan → retrieve → grade → (rewrite) → analyst → verifier → finalize.

Self-Correction happens twice, both bounded by settings:
* retrieval: too few relevant documents → rewrite the queries and search again;
* generation: citation verification fails → the analyst revises the draft.
Every node appends a TraceEvent; the API returns them as the agent's
"current thinking" log for the dashboard.
"""

import operator
from dataclasses import dataclass
from datetime import datetime
from time import perf_counter
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph

from ..config import Settings
from ..contracts import Draft, Hit, TraceEvent, merge_hits
from ..llm.rule import RuleBasedLLM
from ..ports import LLMPort, VectorStorePort
from .verifier import Verification, verify


@dataclass(frozen=True)
class WorkflowConfig:
    """Loop bounds and thresholds; defaults live in `Settings` only."""

    top_k: int
    relevance_threshold: float
    min_relevant_docs: int
    max_rewrites: int
    max_revisions: int
    llm_planner: bool

    @classmethod
    def from_settings(cls, settings: Settings) -> "WorkflowConfig":
        return cls(
            top_k=settings.top_k,
            relevance_threshold=settings.relevance_threshold,
            min_relevant_docs=settings.min_relevant_docs,
            max_rewrites=settings.max_rewrites,
            max_revisions=settings.max_revisions,
            llm_planner=settings.llm_planner,
        )


class ResearchState(TypedDict, total=False):
    question: str
    as_of: datetime
    assets: list[str]
    queries: list[str]
    hits: list[Hit]
    evidence: list[Hit]
    relevance_passed: bool
    retrieval_feedback: str
    rewrites: int
    draft: Draft
    verification: Verification
    verification_feedback: str | None
    revisions: int
    revise: bool
    trace: Annotated[list[TraceEvent], operator.add]


def _event(node: str, started: float, message: str, **data: Any) -> dict:
    elapsed = int((perf_counter() - started) * 1000)
    return {
        "trace": [TraceEvent(node=node, message=message, data=data, elapsed_ms=elapsed)]
    }


INSUFFICIENT_SUMMARY = (
    "근거 부족: 기준 시점 이전에 공개된 관련 뉴스·공시가 충분하지 않다."
)


def build_workflow(store: VectorStorePort, llm: LLMPort, config: WorkflowConfig):
    # Deterministic planning saves one LLM round trip (~1 s) of the 5 s budget.
    plan = llm.plan if config.llm_planner else RuleBasedLLM().plan

    def planner(state: ResearchState) -> dict:
        started = perf_counter()
        queries = plan(state["question"], state["assets"])[:4]
        kind = "LLM" if config.llm_planner else "규칙"
        return {
            "queries": queries,
            "hits": [],
            "rewrites": 0,
            "revisions": 0,
            "verification_feedback": None,
            **_event(
                "planner",
                started,
                f"질문을 검색어 {len(queries)}개로 분해 ({kind} 기반 계획)",
                queries=queries,
                assets=state["assets"],
            ),
        }

    def retrieve(state: ResearchState) -> dict:
        started = perf_counter()
        found = store.search(
            state["queries"], state["as_of"], state["assets"] or None, config.top_k
        )
        hits = merge_hits([*state["hits"], *found])
        return {
            "hits": hits,
            **_event(
                "retrieve",
                started,
                f"as_of 이전 문서 검색: {len(found)}건 (중복 제거 누적 {len(hits)}건)",
                queries=state["queries"],
                top=[
                    {"title": hit.record.title, "score": round(hit.score, 3)}
                    for hit in hits[:5]
                ],
            ),
        }

    def grade(state: ResearchState) -> dict:
        started = perf_counter()
        hits = state["hits"]
        relevant = [h for h in hits if h.score >= config.relevance_threshold]
        evidence = relevant[: config.top_k]
        best = hits[0].score if hits else 0.0
        passed = len(evidence) >= config.min_relevant_docs
        feedback = (
            f"관련성 {config.relevance_threshold:.2f} 이상 문서가 {len(evidence)}건 "
            f"(필요 {config.min_relevant_docs}건, 최고 관련성 {best:.2f})"
        )
        return {
            "evidence": evidence,
            "relevance_passed": passed,
            "retrieval_feedback": feedback,
            **_event(
                "grade",
                started,
                ("통과: " if passed else "기준 미달: ") + feedback,
                relevant=len(evidence),
                best_score=round(best, 3),
                threshold=config.relevance_threshold,
            ),
        }

    def after_grade(state: ResearchState) -> str:
        # No document passes the as_of/asset filter: rewriting cannot help.
        if not state["hits"]:
            return "analyst"
        if state["relevance_passed"] or state["rewrites"] >= config.max_rewrites:
            return "analyst"
        return "rewrite"

    def rewrite(state: ResearchState) -> dict:
        started = perf_counter()
        before = state["queries"]
        after = [llm.rewrite(query, state["retrieval_feedback"]) for query in before]
        return {
            "queries": after,
            "rewrites": state["rewrites"] + 1,
            **_event(
                "rewrite",
                started,
                f"Self-Correction {state['rewrites'] + 1}회: 검색어 수정",
                before=before,
                after=after,
            ),
        }

    def analyst(state: ResearchState) -> dict:
        started = perf_counter()
        evidence = state["evidence"]
        if not evidence:
            draft = Draft(opinion="유지", confidence=0.0, summary=INSUFFICIENT_SUMMARY)
        else:
            draft = llm.analyze(
                state["question"], evidence, state["verification_feedback"]
            )
        return {
            "draft": draft,
            **_event(
                "analyst",
                started,
                f"초안 작성: 의견 {draft.opinion}, 주장 {len(draft.claims)}개",
                evidence=len(evidence),
                revision=state["revisions"],
            ),
        }

    def verifier(state: ResearchState) -> dict:
        started = perf_counter()
        draft = state["draft"]
        result = verify(draft, state["evidence"], llm)
        revise = not result.ok and state["revisions"] < config.max_revisions
        if result.ok:
            message = "인용 검증 통과"
        elif revise:
            message = f"인용 검증 실패 {len(result.issues)}건 → 재작성 요청"
        else:
            message = f"인용 검증 실패 {len(result.issues)}건 → 검증된 주장만 유지"
        return {
            "verification": result,
            "revise": revise,
            "revisions": state["revisions"] + int(revise),
            "verification_feedback": "\n".join(result.issues) or None,
            **_event(
                "verifier",
                started,
                message,
                issues=result.issues,
                **result.stats(len(draft.claims)),
            ),
        }

    def after_verify(state: ResearchState) -> str:
        return "analyst" if state["revise"] else "finalize"

    def finalize(state: ResearchState) -> dict:
        started = perf_counter()
        kept = state["verification"].supported
        cited = {number for claim in kept for number in claim.citations}
        return _event(
            "finalize",
            started,
            f"최종 리포트: 검증된 주장 {len(kept)}개, 인용 문서 {len(cited)}건",
            rewrites=state["rewrites"],
            revisions=state["revisions"],
        )

    graph = StateGraph(ResearchState)
    for name, node in [
        ("planner", planner),
        ("retrieve", retrieve),
        ("grade", grade),
        ("rewrite", rewrite),
        ("analyst", analyst),
        ("verifier", verifier),
        ("finalize", finalize),
    ]:
        graph.add_node(name, node)
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "retrieve")
    graph.add_edge("retrieve", "grade")
    graph.add_conditional_edges("grade", after_grade, ["rewrite", "analyst"])
    graph.add_edge("rewrite", "retrieve")
    graph.add_edge("analyst", "verifier")
    graph.add_conditional_edges("verifier", after_verify, ["analyst", "finalize"])
    graph.add_edge("finalize", END)
    return graph.compile()
