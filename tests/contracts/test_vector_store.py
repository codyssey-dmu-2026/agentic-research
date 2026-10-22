"""VectorStorePort contract: any replacement store must pass these."""

from datetime import datetime, timedelta

import pytest

from agentic_research.embeddings import HashEmbedding
from agentic_research.vectorstore import ChromaVectorStore

AS_OF_CASES = [
    "2024-09-01T00:00:00+09:00",
    "2024-10-08T12:00:00+09:00",
    "2024-12-31T00:00:00+09:00",
]


@pytest.mark.parametrize("as_of", AS_OF_CASES)
def test_search_never_returns_records_unavailable_at_as_of(store, as_of):
    moment = datetime.fromisoformat(as_of)

    hits = store.search(["삼성전자 애플 SK하이닉스 실적 규제 소송"], moment, k=20)

    assert hits
    assert all(hit.record.available_at <= moment for hit in hits)


def test_record_is_usable_exactly_at_its_available_at(store, records):
    dart = next(r for r in records if r.title.startswith("영업(잠정)실적"))

    before = store.search([dart.title], dart.available_at - timedelta(seconds=1))
    at = store.search([dart.title], dart.available_at)

    assert dart.source_url not in {h.record.source_url for h in before}
    assert dart.source_url in {h.record.source_url for h in at}


def test_asset_filter_limits_results(store):
    as_of = datetime.fromisoformat("2024-12-31T00:00:00+09:00")

    hits = store.search(["실적 규제 소송"], as_of, assets=["AAPL"], k=20)

    assert hits
    assert {hit.record.asset_id for hit in hits} == {"AAPL"}


def test_results_are_best_first_with_scores_in_unit_range(store):
    as_of = datetime.fromisoformat("2024-12-31T00:00:00+09:00")

    hits = store.search(["삼성전자 3분기 영업이익 어닝쇼크"], as_of, k=10)

    scores = [hit.score for hit in hits]
    assert scores == sorted(scores, reverse=True)
    assert all(0 <= score <= 1 for score in scores)
    assert hits[0].record.title.startswith("삼성전자 3분기 영업이익")


def test_multiple_queries_return_one_hit_per_url(store):
    as_of = datetime.fromisoformat("2024-12-31T00:00:00+09:00")

    hits = store.search(["삼성전자 실적", "삼성전자 어닝쇼크", "반도체"], as_of, k=5)

    urls = [hit.record.source_url for hit in hits]
    assert len(urls) == len(set(urls))


def test_reingesting_the_same_records_does_not_duplicate(store, records):
    before = store.count()

    store.upsert(records)

    assert store.count() == before == len(records)


def test_store_persists_across_instances(tmp_path, store):
    reopened = ChromaVectorStore(tmp_path / "chroma", HashEmbedding())

    assert reopened.count() == store.count()


def test_naive_as_of_is_rejected(store):
    with pytest.raises(ValueError, match="timezone"):
        store.search(["실적"], datetime(2024, 12, 31))
