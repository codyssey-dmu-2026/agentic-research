# 진행 현황과 남은 일

미션 요구사항 중 에이전트 담당 범위를 기준으로 정리했다(2026-10-30). 이슈는 GitHub [Issues](../../../issues)에, 팀 결정은 Notion「Agentic Research 구현 계획 · 의사결정」에 있다.

## 요구사항 대비

| 요구사항 (미션 4-9, 4-10) | 상태 | 근거 |
| --- | --- | --- |
| LangGraph 계획-수행-검증 다단계 워크플로우 | 완료 | `agent/workflow.py`, #5 |
| 금융 뉴스를 ChromaDB에 벡터화, 원문 URL 메타데이터 | 완료 | `ingest.py`, `corpus/vectorstore.py`, #4 |
| Self-Correction (검색 결과가 부적절하면 쿼리 수정 후 재검색) | 구현 완료, **실데이터에서 발동 0회** | `agent/workflow.py:121-168`, README 측정 결과 |
| 모든 결과에 원문 출처 | 완료 (검증 실패 주장은 삭제) | `agent/verifier.py`, #6 |
| 에이전트 "현재 생각" 로그 | 완료 (`trace`) | `agent/workflow.py:66`, 대시보드 탭 4에서 표시 |
| 위험 이벤트 → RiskTag → RL 관측 또는 리스크 모니터링 | **에이전트 쪽만 완료**, RL·Safe-Guard 쪽 미연동 | `risk/`, #7 (open) |
| `POST /research`, `GET /health`, Pydantic, Swagger | 완료 | `api.py`, #8 |
| 요청당 5초 이내 | p95 4.17초, **최대 5.18초** (20건 중 1건 초과) | `agent/bench.py`, README |
| 결과물 하단 면책 조항 | API 응답에는 있음, **README에는 없음** | `contracts.py` `DISCLAIMER` |

## 남은 일 (우선순위 순)

### 1. RiskTag → RL 연동 합의 (경진)

RL 관측 차원이 바뀌면 모델을 전부 재학습해야 하므로, **실데이터 학습 전에** 정해야 한다.

- [ ] **결정 시각 규칙**: RL 환경의 날짜(시간대 없음)를 `vector(decision_at, …)`에 넣을 시각으로 바꾸는 규칙. 미래 정보 누수 여부가 여기서 정해진다.
- [ ] **관측 위치**: rl-engine `environment.py:146` (`obs_dim`, 288 → 300), `:230` (concat). 호출부 `train.py:55`, `rollout.py:18`, `data_loader.WindowData`.
- [ ] **Safe-Guard 규칙**: `severity × confidence ≥ θ`인 자산의 비중 상한 축소. 훅 위치는 `environment.py:181`과 `:184` 사이. 적용 전후 비중과 `tag_id`를 기록한다.
- [ ] **"자료 없음 ≠ 위험 없음"**: 지금 `vector()`는 태그가 없는 경우와 뉴스 소스가 없는 경우 모두 0을 돌려준다. evaluation-xai 스펙(§8.1 `coverage_missing`)은 둘을 구분하라고 한다. 커버리지 마스크를 따로 줄지 정한다.

### 2. evaluation-xai 스펙이 요구하는 산출물 (재왕)

- [ ] `risk_rule_config`: 임계값, 유효기간, 비중 축소 방식. 평가 담당이 테스트 전에 고정한다.
- [ ] 예시 태그 3개: 활성, 만료, 무관.
- [ ] 뉴스 커버리지 보고: 자산별, 기간별 문서 수.
- [ ] **end-to-end 사례 1건**: 같은 `tag_id`로 원문 URL → 관측값 → PPO 제안 비중 → Safe-Guard 적용 비중이 이어지는 기록. 1번이 끝나야 만들 수 있다.

### 3. 플랫폼 연동 (현호)

- [x] 플랫폼 compose의 데이터 경로: 플랫폼 #4(2026-10-30)에서 `AGENT_NEWS_DIR` 등 `AGENT_*` 환경변수로 맞췄고, `env_file` 필수 지정도 없어졌다. 이 레포는 커밋 `bdd5b84`로 고정돼 있다.
- [ ] 게이트웨이 `ResearchRequest`의 기본값 `tickers=["NVDA"]`, `as_of=2024-12-31`을 없앤다. 질문에서 자산을 찾는 기능과 `as_of` 기본값(현재 시각)을 덮어쓴다.
- [ ] 게이트웨이 타임아웃 4.8초 vs 이 서비스 최대 5.18초. 이 서비스의 최대 응답을 4.5초 아래로 낮추는 것이 우선이다.
- [ ] 대시보드는 `/health`의 `status`만 보고 "온라인"을 표시한다. 벡터 저장소가 비어 있으면 `ready=false`가 이미 응답에 있으므로 그 값을 쓰게 한다.

### 4. 이 레포에서 혼자 할 수 있는 것

- [ ] Self-Correction 시연: OpenAI 임베딩 기준으로 관련성 기준(0.3)을 다시 잡거나, 재작성이 발동하는 시연 질문을 정해 README에 남긴다. 동료 평가 항목이다.
- [ ] 최대 응답 시간 줄이기: `AGENT_TOP_K`, analyst 프롬프트 길이, `check_support` 일괄 호출 시간을 측정한다.
- [ ] README 하단에 면책 조항을 다시 넣는다.
- [ ] PDF 리포트의 에이전트 부분: 아키텍처, Self-Correction 평가표, RiskTag 시점 정책, 한계점. README 내용을 옮기면 된다.

### 5. 데이터 (예종)

- [ ] 팀 공용 데이터 스냅샷: `data/`가 어느 레포에도 커밋돼 있지 않고, 한경 RSS는 실행 시점마다 결과가 달라 재현되지 않는다. ingest와 risk 생성도 이 데이터가 있어야 돌아간다.
- [ ] DART API 키: 없으면 DART 공시가 0건이다.
- [ ] 뉴스 커버리지: 12개 자산 중 5개만 뉴스 파일이 있고, 본문 요약 대부분이 placeholder다. 과거 구간(2022~2025)에는 DART·SEC 제목만 있다.
