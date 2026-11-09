from datetime import datetime

import pytest

from agentic_research.corpus.news import CsvNewsSource, NewsSchemaError
from conftest import FIXTURE_NEWS


def by_title(records, prefix):
    return next(r for r in records if r.title.startswith(prefix))


def test_asset_id_comes_from_file_name_not_company_column(records):
    hynix = by_title(records, "SK하이닉스, HBM")

    assert hynix.asset_id == "000660"


def test_placeholder_summaries_are_dropped_and_sec_forms_described(records):
    paywalled = by_title(records, "삼성전자, 美 반도체")
    dart = by_title(records, "분기보고서")
    ten_q = by_title(records, "10-Q")

    assert paywalled.summary is None
    assert dart.summary is None
    assert "분기보고서" in ten_q.summary


def test_timestamped_news_and_sec_acceptance_are_usable_when_published(records):
    news = by_title(records, "삼성전자 3분기 영업이익")
    ten_q = by_title(records, "10-Q")

    assert news.available_at == news.published_at
    assert ten_q.available_at == ten_q.published_at


def test_date_only_dart_is_usable_from_next_midnight_kst(records):
    dart = by_title(records, "영업(잠정)실적")

    assert dart.available_at == datetime.fromisoformat("2024-10-09T00:00:00+09:00")


def test_date_only_sec_filing_is_usable_from_next_midnight_new_york(records):
    # filingDate 2024-11-01 could be accepted as late as 22:00 ET that day.
    ten_k = by_title(records, "10-K")

    assert ten_k.available_at == datetime.fromisoformat("2024-11-02T00:00:00-04:00")
    assert ten_k.available_at > datetime.fromisoformat("2024-11-01T22:00:00-04:00")


def test_invalid_rows_are_skipped_without_dropping_the_file(records):
    samsung = [r for r in records if r.asset_id == "005930"]

    assert len(samsung) == 5
    assert all(r.source_url.startswith("https://") for r in samsung)


def test_as_of_filters_on_availability_not_publication():
    source = CsvNewsSource(FIXTURE_NEWS)
    noon = datetime.fromisoformat("2024-10-08T12:00:00+09:00")

    titles = {r.title for r in source.load(as_of=noon)}

    assert any(t.startswith("삼성전자 3분기 영업이익") for t in titles)
    # Published (date-only) on 10-08 but not usable until 10-09.
    assert not any(t.startswith("영업(잠정)실적") for t in titles)


def test_missing_column_is_a_schema_error(tmp_path):
    (tmp_path / "SPY.csv").write_text("종목명,제목,게시일\nSPY,x,2024\n", "utf-8-sig")

    with pytest.raises(NewsSchemaError, match="본문요약"):
        CsvNewsSource(tmp_path).load()


def test_naive_as_of_is_rejected():
    with pytest.raises(ValueError, match="timezone"):
        CsvNewsSource(FIXTURE_NEWS).load(as_of=datetime(2024, 10, 8))
