from datetime import datetime

from agentic_research.agent.service import ResearchService
from agentic_research.contracts import Claim, Draft, ResearchRequest
from agentic_research.llm.rule import RuleBasedLLM
from agentic_research.risk.provider import StoredRiskTagProvider
from conftest import make_settings

AS_OF = "2024-12-31T00:00:00+09:00"


def service(store, tmp_path, llm=None, **overrides):
    settings = make_settings(tmp_path, **overrides)
    return ResearchService(
        store, llm or RuleBasedLLM(), StoredRiskTagProvider([]), settings
    )


def ask(svc, question="삼성전자 3분기 실적 어때?", as_of=AS_OF, **kwargs):
    return svc.run(ResearchRequest(question=question, as_of=as_of, **kwargs))


def nodes(response):
    return [event.node for event in response.trace]


def test_low_relevance_rewrites_queries_until_the_limit(store, tmp_path):
    svc = service(store, tmp_path, relevance_threshold=0.99, max_rewrites=2)

    response = ask(svc)

    assert response.rewrites == 2
    assert nodes(response) == [
        "planner",
        *["retrieve", "grade", "rewrite"] * 2,
        "retrieve",
        "grade",
        "analyst",
        "verifier",
        "finalize",
    ]
    rewrite = next(e for e in response.trace if e.node == "rewrite")
    assert rewrite.data["before"] != rewrite.data["after"]


def test_relevant_results_skip_rewriting(store, tmp_path):
    svc = service(store, tmp_path, relevance_threshold=0.0, min_relevant_docs=1)

    response = ask(svc)

    assert response.rewrites == 0
    assert nodes(response) == [
        "planner",
        "retrieve",
        "grade",
        "analyst",
        "verifier",
        "finalize",
    ]


def test_nothing_available_before_as_of_gives_insufficient_evidence(store, tmp_path):
    response = ask(service(store, tmp_path), as_of="2024-01-01T00:00:00+09:00")

    assert response.insufficient_evidence
    assert response.opinion == "유지" and response.confidence == 0
    assert response.citations == [] and response.claims == []
    # Rewriting cannot help when no document passes the time filter.
    assert response.rewrites == 0


def test_future_articles_are_never_cited(store, tmp_path):
    svc = service(store, tmp_path, relevance_threshold=0.0, min_relevant_docs=1)

    response = ask(svc, question="삼성전자 수출 통제", tickers=["005930"])

    as_of = datetime.fromisoformat(AS_OF)
    assert response.citations
    assert all(c.published_at <= as_of for c in response.citations)


class CitesMissingDocuments(RuleBasedLLM):
    def analyze(self, question, evidence, feedback):
        return Draft(
            opinion="비중 확대",
            confidence=0.9,
            summary="근거 없는 낙관",
            claims=[
                {"text": "HBM 매출이 두 배가 된다", "citations": [99]},
                {"text": "주가가 반드시 오른다", "citations": []},
            ],
        )


def test_unverifiable_claims_are_removed_after_bounded_revisions(store, tmp_path):
    svc = service(store, tmp_path, CitesMissingDocuments(), max_revisions=1)

    response = ask(svc)

    verifier_events = [e for e in response.trace if e.node == "verifier"]
    assert len(verifier_events) == 2 and response.revisions == 1
    assert verifier_events[0].data["invalid_citation"] == 1
    assert verifier_events[0].data["no_citation"] == 1
    assert response.claims == [] and response.citations == []
    assert response.insufficient_evidence and response.opinion == "유지"


class FixesOnRevision(RuleBasedLLM):
    def analyze(self, question, evidence, feedback):
        draft = super().analyze(question, evidence, feedback)
        if feedback is None:
            # First draft: one claim the evidence does not support.
            unsupported = Claim(text="애플 아이폰 판매 급증", citations=[1])
            return draft.model_copy(update={"claims": [unsupported]})
        return draft


def test_failed_verification_feeds_back_into_a_revised_draft(store, tmp_path):
    svc = service(store, tmp_path, FixesOnRevision(), max_revisions=1)

    response = ask(svc)

    assert response.revisions == 1
    assert response.claims and not response.insufficient_evidence
    first = next(e for e in response.trace if e.node == "verifier")
    assert first.data["unsupported"] == 1


def test_citations_point_only_at_retrieved_documents(store, tmp_path, records):
    response = ask(service(store, tmp_path))

    stored_urls = {r.source_url for r in records}
    assert response.citations
    assert {c.source_url for c in response.citations} <= stored_urls
    cited_ids = {n for claim in response.claims for n in claim.citations}
    assert cited_ids == {c.id for c in response.citations}
