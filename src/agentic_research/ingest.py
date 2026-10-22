"""Load data-pipeline news CSVs into ChromaDB.

    python -m agentic_research.ingest

Idempotent: document ids derive from (asset, URL), so re-running after
data-pipeline appends new rows only adds the new ones.
"""

import logging
from collections import Counter

from .config import get_settings
from .wiring import build_news_source, build_vector_store


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()
    records = build_news_source(settings).load()
    if not records:
        raise SystemExit(f"no news records under {settings.news_dir}")
    store = build_vector_store(settings)
    store.upsert(records)
    by_type = Counter(record.source_type for record in records)
    by_asset = Counter(record.asset_id for record in records)
    first = min(record.published_at for record in records)
    last = max(record.published_at for record in records)
    print(f"loaded {len(records)} records {dict(by_type)} from {settings.news_dir}")
    print(f"assets {dict(sorted(by_asset.items()))}")
    print(f"published {first.isoformat()} .. {last.isoformat()}")
    print(f"vector store now holds {store.count()} documents in {settings.chroma_dir}")


if __name__ == "__main__":
    main()
