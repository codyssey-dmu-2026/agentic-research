# Agentic Research

에이전틱 RAG + 강화학습 기반 로보어드바이저 프로젝트의 **Agentic Research** 파트다.
LangGraph 기반 계획-수행-검증 워크플로우로 금융 뉴스·공시를 교차 분석하고, 인용이 포함된
리서치 리포트와 강화학습 엔진·Safe-Guard가 소비하는 **리스크 태그(RiskTag)**를 생성한다.

구현 계획과 진행 상황은 이 레포의 [Issues](../../issues)에서 관리한다.

## 팀 레포와의 관계

| 레포 | 이 레포와의 연결 |
| --- | --- |
| [data-pipeline](https://github.com/codyssey-dmu-2026/data-pipeline) | `data/raw/news/{ticker}.csv`(종목명, 제목, 본문요약, 게시일, 원문URL)를 읽어 ChromaDB에 적재한다. 수집은 data-pipeline이 담당한다. |
| [evaluation-xai](https://github.com/codyssey-dmu-2026/evaluation-xai) | `evaluation_xai.contracts.RiskTag` 스키마를 그대로 따르는 리스크 태그를 공급한다. |
| RL 엔진 / 프론트 | 리스크 태그를 관측 공간·Safe-Guard에 전달하고, `/research` 결과와 추론 로그를 대시보드에 제공한다. |

## 구조

```
src/agentic_research/
├── __init__.py   # 버전, 금융 면책 문구
├── config.py     # 환경 변수 기반 설정 (AGENT_* / OPENAI_API_KEY)
└── api.py        # FastAPI 앱 (현재 GET /health)
tests/            # pytest
```

## 실행

### 로컬 (Python 3.12 또는 3.13)

```bash
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e . --no-deps
cp .env.example .env            # OPENAI_API_KEY 등 입력, 커밋 금지
python -m uvicorn agentic_research.api:app --port 8001
```

### Docker

```bash
# NEWS_DIR: data-pipeline의 뉴스 CSV 경로 (기본 ./data/raw/news), 읽기 전용 마운트
NEWS_DIR=../data-pipeline/data/raw/news docker compose up --build
```

- Health: <http://127.0.0.1:8001/health>
- Swagger UI: <http://127.0.0.1:8001/docs>
- 포트 8001은 evaluation-xai API(8000)와의 충돌을 피하기 위한 값이다.

### 검사

```bash
python -m black --check src tests
python -m flake8 src tests
python -m pytest --cov=agentic_research
```

## 설정

| 변수 | 기본값 | 설명 |
| --- | --- | --- |
| `OPENAI_API_KEY` | 없음 | LLM API 키. `/health`는 설정 여부만 노출하고 값은 노출하지 않는다. |
| `AGENT_NEWS_DIR` | `data/raw/news` | data-pipeline 뉴스·공시 CSV 디렉터리 |
| `AGENT_CHROMA_DIR` | `artifacts/chroma` | ChromaDB 영속 저장 경로 |
