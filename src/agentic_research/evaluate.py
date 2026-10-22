"""Measure what Self-Correction and citation verification change (#6).

    python -m agentic_research.evaluate [--questions evaluation/questions.json]

Runs the fixed question set three times against the ingested store:
* baseline: no query rewrite, no draft revision
* retrieval_correction: query rewrite up to AGENT_MAX_REWRITES, no revision
* full_correction: query rewrite plus at least one analyst revision
"Draft" metrics come from the first verification of each run (what the analyst
wrote before any correction); "final" metrics describe the returned report.
"""

import argparse
import json
from pathlib import Path
from statistics import fmean, median

from .config import Settings, get_settings
from .contracts import ResearchRequest, ResearchResponse
from .research import ResearchService
from .wiring import build_llm, build_risk_provider, build_vector_store


def _ratio(part: int, whole: int) -> float:
    return part / whole if whole else 0.0


def percentile95(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, round(0.95 * (len(ordered) - 1)))]


def summarize(responses: list[ResearchResponse]) -> dict[str, float]:
    first = [next(e for e in r.trace if e.node == "verifier").data for r in responses]
    last = [[e for e in r.trace if e.node == "verifier"][-1].data for r in responses]
    draft_claims = sum(d["claims"] for d in first)
    latencies = [r.elapsed_ms for r in responses]
    return {
        "questions": len(responses),
        "draft_claims": draft_claims,
        "draft_citation_coverage": _ratio(
            draft_claims - sum(d["no_citation"] for d in first), draft_claims
        ),
        "draft_invalid_citation_rate": _ratio(
            sum(d["invalid_citation"] for d in first), draft_claims
        ),
        "draft_unsupported_rate": _ratio(
            sum(d["unsupported"] for d in first), draft_claims
        ),
        "final_verified_rate": _ratio(
            sum(d["supported"] for d in last), sum(d["claims"] for d in last)
        ),
        "final_claims_per_answer": fmean(len(r.claims) for r in responses),
        "insufficient_rate": fmean(r.insufficient_evidence for r in responses),
        "mean_rewrites": fmean(r.rewrites for r in responses),
        "latency_p50_ms": median(latencies),
        "latency_p95_ms": percentile95(latencies),
    }


def run(settings: Settings, questions: list[dict]) -> dict[str, dict[str, float]]:
    store = build_vector_store(settings)
    if store.count() == 0:
        raise SystemExit(
            "vector store is empty: run `python -m agentic_research.ingest`"
        )
    llm = build_llm(settings)
    risk = build_risk_provider(settings)
    revisions = max(1, settings.max_revisions)
    variants = {
        "baseline": {"max_rewrites": 0, "max_revisions": 0},
        "retrieval_correction": {"max_revisions": 0},
        "full_correction": {"max_revisions": revisions},
    }
    report: dict[str, dict] = {}
    for name, update in variants.items():
        service = ResearchService(store, llm, risk, settings.model_copy(update=update))
        responses = [service.run(ResearchRequest(**q)) for q in questions]
        report[name] = summarize(responses)
    report["meta"] = {
        "llm_provider": llm.name,
        "embedding_provider": settings.embedding_provider,
        "relevance_threshold": settings.relevance_threshold,
        "llm_planner": settings.llm_planner,
        "max_rewrites": settings.max_rewrites,
        "full_correction_revisions": revisions,
    }
    return report


VARIANTS = ("baseline", "retrieval_correction", "full_correction")


def to_markdown(report: dict[str, dict[str, float]]) -> str:
    metrics = [key for key in report["baseline"] if key != "questions"]
    lines = [f"| metric | {' | '.join(VARIANTS)} |", "| --- |" + " --- |" * 3]
    for key in metrics:
        values = " | ".join(f"{report[v][key]:.3g}" for v in VARIANTS)
        lines.append(f"| {key} | {values} |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--questions", type=Path, default=Path("evaluation/questions.json")
    )
    parser.add_argument(
        "--out", type=Path, default=Path("artifacts/evaluation_report.json")
    )
    args = parser.parse_args(argv)
    questions = json.loads(args.questions.read_text(encoding="utf-8"))
    report = run(get_settings(), questions)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), "utf-8")
    print(json.dumps(report["meta"], ensure_ascii=False))
    print(to_markdown(report))
    print(f"saved {args.out}")


if __name__ == "__main__":
    main()
