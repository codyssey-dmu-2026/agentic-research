"""Build the RiskTag file consumed by the RL engine and the API.

    python -m agentic_research.risk            # price + earnings + text tags
    python -m agentic_research.risk --no-text  # skip LLM/keyword text tagging

Rebuilds `AGENT_RISK_TAGS_PATH` from scratch; tag ids are stable across runs.
"""

import argparse
import logging
from collections import Counter
from datetime import UTC, datetime

from ..config import get_settings
from ..wiring import build_llm, build_news_source
from .provider import write_jsonl
from .taggers import (
    deduplicate,
    earnings_shock_tags,
    load_returns,
    price_shock_tags,
    tagger_version,
    text_tags,
)

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--no-text", action="store_true", help="skip text tagging")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    settings = get_settings()
    llm = build_llm(settings)
    common = {
        "ttl_days": settings.risk_ttl_days,
        "generated_at": datetime.now(UTC),
        "version": tagger_version(llm.name),
    }
    records = build_news_source(settings).load()
    tags = []
    if settings.returns_path.is_file():
        returns = load_returns(settings.returns_path)
        shock = {"lookback": settings.shock_lookback_days}
        tags += price_shock_tags(
            returns, z_threshold=settings.price_shock_z, **shock, **common
        )
        tags += earnings_shock_tags(
            records, returns, z_threshold=settings.earnings_shock_z, **shock, **common
        )
    else:
        logger.warning(
            "%s not found: price and earnings tags skipped", settings.returns_path
        )
    if not args.no_text:
        tags += text_tags(records, llm, **common)

    tags = deduplicate(tags)
    count = write_jsonl(tags, settings.risk_tags_path)
    by_type = Counter(tag.risk_type for tag in tags)
    print(f"wrote {count} tags to {settings.risk_tags_path} ({common['version']})")
    print(f"by type {dict(sorted(by_type.items()))}")
    if tags:
        print(f"available {tags[0].available_at} .. {tags[-1].available_at}")


if __name__ == "__main__":
    main()
