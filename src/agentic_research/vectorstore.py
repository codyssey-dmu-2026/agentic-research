"""ChromaDB vector store with point-in-time filtering.

Embeddings are computed by our `EmbeddingPort` and passed explicitly, so Chroma
never downloads its default model. Each embedding space gets its own collection
because vectors of different models are not comparable.
"""

import re
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

import chromadb

from .contracts import Hit, NewsRecord, merge_hits, require_aware
from .ports import EmbeddingPort

_BATCH = 256


def _metadata(record: NewsRecord) -> dict[str, str | int]:
    return {
        "asset_id": record.asset_id,
        "title": record.title,
        "summary": record.summary or "",
        "published_at": record.published_at.isoformat(),
        "available_at": record.available_at.isoformat(),
        # Chroma filters on numbers only; whole seconds suffice (inputs have no
        # sub-second precision).
        "available_ts": int(record.available_at.timestamp()),
        "source_url": record.source_url,
        "source_type": record.source_type,
    }


def _record(metadata: dict) -> NewsRecord:
    return NewsRecord(
        asset_id=metadata["asset_id"],
        title=metadata["title"],
        summary=metadata["summary"] or None,
        published_at=datetime.fromisoformat(metadata["published_at"]),
        available_at=datetime.fromisoformat(metadata["available_at"]),
        source_url=metadata["source_url"],
        source_type=metadata["source_type"],
    )


class ChromaVectorStore:
    def __init__(self, path: Path, embedding: EmbeddingPort) -> None:
        self._embedding = embedding
        client = chromadb.PersistentClient(
            path=str(path),
            settings=chromadb.Settings(anonymized_telemetry=False),
        )
        name = re.sub(r"[^a-zA-Z0-9._-]", "-", f"news-{embedding.name}")
        self._collection = client.get_or_create_collection(
            name,
            embedding_function=None,
            configuration={"hnsw": {"space": "cosine"}},
        )

    def upsert(self, records: Sequence[NewsRecord]) -> None:
        # Ids derive from (asset, URL), so re-ingesting never duplicates.
        for start in range(0, len(records), _BATCH):
            batch = records[start : start + _BATCH]
            self._collection.upsert(
                ids=[record.doc_id for record in batch],
                embeddings=self._embedding.embed(
                    [record.search_text for record in batch]
                ),
                documents=[record.search_text for record in batch],
                metadatas=[_metadata(record) for record in batch],
            )

    def count(self) -> int:
        return self._collection.count()

    def search(
        self,
        queries: Sequence[str],
        as_of: datetime,
        assets: Sequence[str] | None = None,
        k: int = 6,
    ) -> list[Hit]:
        require_aware(as_of)
        if not queries:
            return []
        conditions: list[dict] = [{"available_ts": {"$lte": int(as_of.timestamp())}}]
        if assets:
            conditions.append({"asset_id": {"$in": list(assets)}})
        where = conditions[0] if len(conditions) == 1 else {"$and": conditions}
        # One embedding call and one query for all queries (latency budget).
        result = self._collection.query(
            query_embeddings=self._embedding.embed(list(queries)),
            n_results=k,
            where=where,
            include=["metadatas", "distances"],
        )
        return merge_hits(
            # Cosine distance is in [0, 2]; report similarity clipped to [0, 1].
            Hit(record=_record(metadata), score=max(0.0, min(1.0, 1.0 - distance)))
            for metadatas, distances in zip(
                result["metadatas"], result["distances"], strict=True
            )
            for metadata, distance in zip(metadatas, distances, strict=True)
        )
