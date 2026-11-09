# Agentic Research 작업 규칙

이 저장소는 팀의 리서치 에이전트 서비스다. 뉴스·공시 수집은 data-pipeline, RiskTag 스키마는 evaluation-xai(커밋 고정 의존성)가 담당한다. 코드 구조는 [docs/code-guide.md](docs/code-guide.md), 남은 일은 [docs/status.md](docs/status.md)에 있다.

- **시점 규칙**: 검색·태그·provider의 시각 인자는 모두 시간대가 있어야 한다. `available_at <= as_of`(또는 `decision_at`)인 것만 반환한다. 이 규칙을 건드리면 `tests/contracts/`를 먼저 확인한다.
- **출처**: 원문 URL로 되짚을 수 없는 주장이나 RiskTag는 만들지 않는다. 인용 검증에 실패한 주장은 고치거나 지우며, 그대로 내보내지 않는다.
- **RiskTag 스키마**: evaluation-xai의 `RiskTag`를 import해서 쓴다. 필드를 복사하거나 덧붙이지 않는다. `tag_id`는 같은 입력이면 같은 값이 나와야 한다.
- **구현 교체**: LLM·임베딩·저장소 구현은 `wiring.py`에서만 고른다. 팀 결정 항목은 `config.py`의 설정값이며 기본값은 그곳에만 둔다.
- **응답 시간**: `/research`는 5초 이내여야 한다. LLM 호출을 늘리는 변경은 `python -m agentic_research.bench`로 측정한 뒤 README 측정 결과를 갱신한다.
- **문서**: 기능이나 연동 상태가 바뀌면 `docs/status.md`를 함께 고친다. 구현되지 않은 연동을 완료로 쓰지 않는다.
- **검사**: `black --check src tests`, `flake8 src tests`, `pytest`를 통과시킨다.
