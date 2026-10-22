"""Run the workflow for one request and shape the API response."""

from datetime import UTC, datetime
from time import perf_counter

from .assets import assets_in_text
from .config import Settings
from .contracts import Citation, ResearchRequest, ResearchResponse
from .ports import LLMPort, RiskTagProvider, VectorStorePort
from .workflow import INSUFFICIENT_SUMMARY, WorkflowConfig, build_workflow


class ResearchService:
    def __init__(
        self,
        store: VectorStorePort,
        llm: LLMPort,
        risk_provider: RiskTagProvider,
        settings: Settings,
    ) -> None:
        self.store = store
        self.llm = llm
        self.risk_provider = risk_provider
        self._graph = build_workflow(store, llm, WorkflowConfig.from_settings(settings))

    def run(self, request: ResearchRequest) -> ResearchResponse:
        started = perf_counter()
        as_of = request.as_of or datetime.now(UTC)
        assets = request.tickers or assets_in_text(request.question)
        state = self._graph.invoke(
            {"question": request.question, "as_of": as_of, "assets": assets}
        )

        evidence = state["evidence"]
        claims = state["verification"].supported
        cited = sorted({number for claim in claims for number in claim.citations})
        citations = [
            Citation(
                id=number,
                title=evidence[number - 1].record.title,
                asset_id=evidence[number - 1].record.asset_id,
                source_type=evidence[number - 1].record.source_type,
                published_at=evidence[number - 1].record.published_at,
                source_url=evidence[number - 1].record.source_url,
            )
            for number in cited
        ]
        tag_assets = assets or sorted({c.asset_id for c in citations})
        risk_tags = (
            sorted(
                self.risk_provider.tags(as_of, tag_assets),
                key=lambda tag: tag.severity * tag.confidence,
                reverse=True,
            )
            if tag_assets
            else []
        )
        # Without a single verified claim there is no evidence-backed opinion.
        insufficient = not claims
        draft = state["draft"]
        return ResearchResponse(
            question=request.question,
            as_of=as_of,
            tickers=assets,
            answer=INSUFFICIENT_SUMMARY if insufficient else draft.summary,
            opinion="유지" if insufficient else draft.opinion,
            confidence=0.0 if insufficient else draft.confidence,
            insufficient_evidence=insufficient,
            claims=claims,
            citations=citations,
            risk_tags=risk_tags,
            trace=state["trace"],
            rewrites=state["rewrites"],
            revisions=state["revisions"],
            llm_provider=self.llm.name,
            elapsed_ms=int((perf_counter() - started) * 1000),
        )
