"""Load data-pipeline news and disclosure CSVs as point-in-time `NewsRecord`s.

Input contract (data-pipeline `0bbd15f`): `data/raw/news/{asset_id}.csv`,
utf-8-sig, columns `종목명, 제목, 본문요약, 게시일, 원문URL`, where `게시일` is a
timezone-aware ISO timestamp. The file name is the asset id because `종목명`
differs by market (ticker for US, Korean name for KR).
"""

import logging
from datetime import datetime, time, timedelta
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from pydantic import ValidationError

from .assets import KST, NEW_YORK
from .contracts import NewsRecord, SourceType, require_aware

logger = logging.getLogger(__name__)

COLUMNS = ("종목명", "제목", "본문요약", "게시일", "원문URL")
# data-pipeline writes these instead of a body; they carry no information.
PLACEHOLDER_SUMMARIES = frozenset(
    {"요약 없음(원문URL 참고)", "유료/비공개 기사(원문URL 참고)"}
)
# SEC rows are titled "{form} ({period})" with no body. Saying what the form is
# makes them retrievable for questions about results or events.
SEC_FORM_DESCRIPTIONS = {
    "10-K": "미국 SEC 연간보고서(annual report): 연간 실적과 재무제표",
    "10-Q": "미국 SEC 분기보고서(quarterly report): 분기 실적과 재무제표",
    "8-K": "미국 SEC 수시공시(current report): 실적 발표 등 주요 경영 사건",
}


class NewsSchemaError(ValueError):
    pass


def source_type_of(url: str) -> SourceType:
    host = urlparse(url).hostname or ""
    if host.endswith("dart.fss.or.kr"):
        return "dart"
    if host.endswith("sec.gov"):
        return "sec"
    return "news"


def available_at(published_at: datetime, source_type: SourceType) -> datetime:
    """Earliest moment the record may be used (Notion D6).

    DART receipts and the SEC `filingDate` fallback carry only a date, stored as
    midnight KST. The real filing time that day is unknown, so the record is
    usable from midnight after that date in the filer's market time zone.
    Everything else has a real timestamp and is usable when published.
    """
    local = published_at.astimezone(KST)
    if source_type in ("dart", "sec") and local.time() == time(0, 0):
        market_tz = NEW_YORK if source_type == "sec" else KST
        return datetime.combine(local.date() + timedelta(days=1), time(0), market_tz)
    return published_at


def _parse_row(asset_id: str, row: dict[str, str]) -> NewsRecord:
    published = require_aware(datetime.fromisoformat(row["게시일"]), "게시일")
    url = row["원문URL"].strip()
    kind = source_type_of(url)
    summary: str | None = row["본문요약"].strip()
    if not summary or summary in PLACEHOLDER_SUMMARIES:
        form = row["제목"].strip().split(" ", 1)[0]
        summary = SEC_FORM_DESCRIPTIONS.get(form) if kind == "sec" else None
    return NewsRecord(
        asset_id=asset_id,
        title=row["제목"].strip(),
        summary=summary,
        published_at=published,
        available_at=available_at(published, kind),
        source_url=url,
        source_type=kind,
    )


def load_file(path: Path) -> list[NewsRecord]:
    frame = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    missing = [column for column in COLUMNS if column not in frame.columns]
    if missing:
        raise NewsSchemaError(f"{path.name}: missing columns {missing}")
    records: dict[str, NewsRecord] = {}
    for line, row in enumerate(frame.to_dict("records"), start=2):
        try:
            record = _parse_row(path.stem, row)
        except (ValueError, ValidationError) as error:
            logger.warning("%s:%d skipped: %s", path.name, line, error)
            continue
        records[record.source_url] = record
    return list(records.values())


class CsvNewsSource:
    def __init__(self, news_dir: Path) -> None:
        self.news_dir = news_dir

    def load(self, as_of: datetime | None = None) -> list[NewsRecord]:
        if as_of is not None:
            require_aware(as_of)
        if not self.news_dir.is_dir():
            return []
        records = [
            record
            for path in sorted(self.news_dir.glob("*.csv"))
            for record in load_file(path)
        ]
        if as_of is None:
            return records
        return [record for record in records if record.available_at <= as_of]
