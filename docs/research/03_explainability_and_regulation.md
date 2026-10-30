# 강화학습 로보어드바이저: 설명가능성과 규제의 실제 범위

> 조사 기준: 2026-10-13. 논문은 포트폴리오 성과의 실증근거가 아니라 **결정 설명 방법의 근거**로 읽는다. 법령의 적용은 서비스의 실제 용도·사업자 지위·관할권에 따라 달라진다.

## 핵심 결론

- **설명은 가능하지만, 무엇을 설명했는지 한정해야 한다.**
  SHAP(SHapley Additive exPlanations, 개별 출력과 기준 출력의 차이를 입력 변수들에 나눠 주는 방법)은
  특정 시점의 **정책 출력**을 설명한다. 포트폴리오의 미래 수익, 하락 방어 성공,
  강화학습의 장기 목표 달성 원인을 입증하지는 않는다.
  [Lundberg & Lee (2017)](https://proceedings.neurips.cc/paper/2017/file/8a20a8621978632d76c43dfd28b67767-Paper.pdf), [Milani et al. (2022)](https://arxiv.org/abs/2202.08434).
- **PPO의 연속형 ETF 비중에는 KernelExplainer를 우선 검토할 수 있다.**
  입력은 한 시점의 관측값, 출력은 재현 가능한 `관측값 → 결정론적 11차원 비중` 함수로 정한다.
  각 ETF 비중에 대한 SHAP은 별도로 해석하고, 신경망 구조·연산이 호환될 때에만 DeepExplainer를 대안으로 쓴다.
  이는 공식 API를 활용한 **우리 설계안**이지 PPO 자체의 설명가능성 검증 결과가 아니다.
  [SHAP KernelExplainer](https://shap.readthedocs.io/en/latest/generated/shap.KernelExplainer.html), [SHAP DeepExplainer](https://shap.readthedocs.io/en/latest/generated/shap.DeepExplainer.html), [SB3 PPO](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html).
- **상관성과 시간 의존성이 핵심 반증이다.**
  한국·미국 주가지수, ETF 수익률·변동성·이동평균처럼 겹치는 입력을 독립적으로 가리면
  실제로 불가능한 시장 상태가 생길 수 있다. SHAP 순위는 배경 데이터 표본에도 흔들릴 수 있으며,
  높은 중요도가 인과관계나 실행 가능한 대응책을 뜻하지 않는다.
  [Kumar et al. (2020)](https://proceedings.mlr.press/v119/kumar20e/kumar20e.pdf), [Yuan et al. (2022)](https://arxiv.org/abs/2204.11351).
- **한국의 ‘금융 XAI 의무화’라는 포괄적 표현은 부정확하다.**
  2026년 개정 금융위 가이드라인은 명시적으로 **자율규제**이지만, 별도 법령에 해당하면 법적 의무가 생긴다.
  특히 「인공지능기본법」의 **고영향 AI**에는 기술적으로 가능한 범위에서 주요 기준 등을 설명할
  **방안의 수립·시행** 의무가 있다. 모든 ETF 투자추천·모든 RL 정책에 SHAP을 의무화한 법은 확인되지 않는다.
  [금융위원회 (2026)](https://www.fsc.go.kr/po010103/87142), [인공지능기본법 제2조](https://www.law.go.kr/LSW/lsLinkCommonInfo.do?lsJoLnkSeq=1031810747), [제34조](https://law.go.kr/lsLinkCommonInfo.do?chrClsCd=010202&lsJoLnkSeq=1031810845).
- **로보어드바이저 상용화 심사는 따로 존재한다.**
  자본시장법 시행령은 전자적 투자조언장치의 투자자 성향 분석·보안 등을 규정하며,
  코스콤 테스트베드는 ‘투자자들에게 설명 가능한 알고리즘’과 성향별 포트폴리오·리밸런싱을 본다.
  **백테스트 통과, 테스트베드 통과, 법적 영업자격은 서로 다르다.**
  [시행령 제2조](https://www.law.go.kr/lsLinkCommonInfo.do?lsJoLnkSeq=1029500643), [제99조](https://www.law.go.kr/LSW//lsLawLinkInfo.do?chrClsCd=010202&lsId=010817&lsJoLnkSeq=1000930618&print=print), [코스콤 심사프로세스](https://www.ratestbed.kr:7443/portal/main/contents.do?menuNo=200080), [코스콤 참여요건](https://www.ratestbed.kr:7443/portal/main/contents.do?menuNo=200070).

## 근거

### 1. 어떤 출력을 설명할 것인가

- **Lundberg & Lee (2017), _A Unified Approach to Interpreting Model Predictions_.**
  단일 예측을 `기준 출력 + 변수별 기여도`로 분해하는 부가적 설명 틀과
  공리(국소 정확성·결측성·일관성)를 제시했다. 결정트리 예제, 사용자 설명 비교,
  MNIST 숫자영상 분류를 사용했으며 **금융 ETF나 PPO 시계열 성과는 실험하지 않았다**.
  [원 논문](https://proceedings.neurips.cc/paper/2017/file/8a20a8621978632d76c43dfd28b67767-Paper.pdf).

- **국소(local) 설명:** ‘이 날짜·이 관측값에서 이 모델이 왜 이 값을 출력했는가’에 한정된다.
  식으로는 특정 ETF `k`의 `w_k(s_t) ≈ E[w_k(S)] + Σ_i φ_{i,k}`이며 `φ`는 입력 변수의 기여도다.
  여기서 기준인 `E[w_k(S)]`는 **선택한 배경 표본**의 평균 정책 출력이다.
  이 식은 포트폴리오 최종 비중을 함수의 출력으로 선택한 경우에만 그 비중을 설명한다.
  [원 논문 §2–4](https://proceedings.neurips.cc/paper/2017/file/8a20a8621978632d76c43dfd28b67767-Paper.pdf), [KernelExplainer 문서](https://shap.readthedocs.io/en/latest/generated/shap.KernelExplainer.html).

- **KernelExplainer (공식 SHAP 문서):** 표본 행렬을 받아 하나의 출력 또는 여러 출력의 행렬을
  돌려주는 **임의 함수**에 적용한다. 배경 데이터의 값으로 ‘없는 변수’를 대체하며
  `identity` 링크를 쓰면 기여도의 단위는 함수 출력의 단위(여기서는 비중)이다.
  출력이 11개라면 결과를 ETF별로 분리해야 한다. [API](https://shap.readthedocs.io/en/latest/generated/shap.KernelExplainer.html).

- **DeepExplainer (공식 SHAP 문서):** TensorFlow/PyTorch의 미분 가능한 모델을 위한
  Deep SHAP 근사이며 배경 표본에 대한 기대 출력과 현 출력의 차이를 배분한다.
  문서는 한 출력에 대한 기여도와 다중 출력의 반환 형태를 설명하고,
  배경 표본 수에 비례하여 계산비용이 커진다고 명시한다. Stable-Baselines3 `PPO` 객체 자체가
  이 API에 곧바로 호환된다는 주장은 **[미확인]**이며, 실제 정책 네트워크·출력·전처리·비중 변환을
  모두 감싼 후 호환성을 확인해야 한다. [API](https://shap.readthedocs.io/en/latest/generated/shap.DeepExplainer.html).

- **SB3 PPO 공식 문서:** 연속 행동공간 `Box`를 지원하고, 연속 제어의 평가 시
  `predict(..., deterministic=True)`를 권장한다. 따라서 실제 투자 배분에 쓰는
  **동일한 관측 전처리와 최종 비중 변환**을 설명 함수 안에 포함시키는 것이 정책값과
  설명값을 일치시키는 설계다. 정책의 내부 평균행동 또는 로그잇만 설명하면
  최종 ETF 비중을 설명했다고 말할 수 없다. [SB3 PPO](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html), [KernelExplainer API](https://shap.readthedocs.io/en/latest/generated/shap.KernelExplainer.html).

### 2. 강화학습과 시간의 추가 문제

- **Milani et al. (2022), _A Survey of Explainable Reinforcement Learning_.** XRL(eXplainable Reinforcement Learning, 순차적인 **상태 → 행동 → 후속 결과**를 이해시키는 연구)을 RL 설정별로 분류하고 연구의 공백을 제시한 문헌조사다. 새 투자 실험이나 수익률 표본을 제시한 논문은 아니다. 단일 시점 입력 기여도와 장기 전략의 설명을 동일시하지 말아야 한다는 **설계상 해석**의 출발점이다. [원 서베이](https://arxiv.org/abs/2202.08434).

- **Puiutta & Veith (2020), _Explainable Reinforcement Learning: A Survey_.** XRL 방법을 분류하면서 복잡한 모델을 사후에 모방·단순화하는 방법이 많고, 비전문 사용자가 설명을 어떻게 이해하는지는 자주 간과한다고 정리한다. 별도의 금융 투자기간 실험이나 ‘SHAP 사용 시 소비자가 결정을 이해했다’는 증거는 아니다. [원 서베이](https://arxiv.org/abs/2005.06247).

- **Bento et al. (2020), _TimeSHAP: Explaining Recurrent Models through Sequence Perturbations_.**
  KernelSHAP을 **순서가 있는 입력**에 확장하여 변수·시점·시점×변수 기여도를 계산한다.
  은행 계좌 탈취 탐지 RNN 사례에서 입력 순서 분석과 오래된 이벤트 가지치기
  (pruning, 기여도가 작은 앞부분을 생략)를 실험했다. 그러나 기본 SB3 PPO의 `MlpPolicy`에
  TimeSHAP을 그대로 쓰는 근거는 아니다. [원 논문 arXiv](https://arxiv.org/abs/2012.00073), [SB3 PPO의 순환정책 안내](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html).

### 3. 한국 규제: 의무·자율규제·테스트베드를 분리

| 구분 | 1차 자료에서 실제로 확인한 내용 | 프로젝트에 대한 해석 |
|---|---|---|
| **자율규제** | 금융위는 2021년 「금융분야 AI 가이드라인」을 **모범규준**으로 발표하며 AI 활용 고지, 이해 가능한 설명, 권리구제 안내를 제시했다. 2022년 「AI 개발·활용 안내서」는 로보어드바이저 등 5개 서비스용 단계별 **체크리스트**다. [금융위 2021](https://www.fsc.go.kr/no010101/76206), [금융위 2022](https://www.fsc.go.kr/no010101/78235). | 발표문 속 ‘설명’ 표현만으로 **SHAP 구현 법적 의무**라고 할 수 없다. |
| **최신 자율규제** | 금융위는 2026-06-22 시행 「금융분야 인공지능 가이드라인」 개정안을 **모든 금융회사 등이 준수하는 자율규제**로 명시하고 적용 수준을 위험·규모에 맞춰 자율 결정하도록 했다. 7대 원칙에는 임직원의 최종책임·인적 개입 및 소비자 이익이 포함된다. 단, 법률에 별도 의무가 있으면 따라야 한다. [금융위 2026](https://www.fsc.go.kr/po010103/87142). | 2021년 발표만 현재 단독 법적 근거로 인용하지 말 것; 사람의 조직적 책임과 매 거래마다 수동 투자결정을 혼동하지 말 것. |
| **조건부 법적 의무** | 「인공지능기본법」 제2조제4호사목은 개인의 권리·의무에 중대한 영향을 미치는 ‘채용, **대출 심사** 등’의 판단·평가를 고영향 AI의 범위로 규정한다. 제31조는 고영향 AI 서비스의 사전 AI 고지를, 제34조는 위험관리·사람의 감독·문서화와 **기술적으로 가능한 범위에서 결과·주요기준·학습데이터 개요 등에 대한 설명 방안 수립·시행**을 요구한다. [제2조](https://www.law.go.kr/LSW/lsLinkCommonInfo.do?lsJoLnkSeq=1031810747), [제31조](https://www.law.go.kr/lsLinkCommonInfo.do?chrClsCd=010202&lsJoLnkSeq=1031810721), [제34조](https://law.go.kr/lsLinkCommonInfo.do?chrClsCd=010202&lsJoLnkSeq=1031810845). | **투자자문이 일률적으로 고영향 AI인지는 [미확인].** 대출심사와 ETF 추천을 동일시하거나 제34조가 SHAP 라이브러리를 지정한다고 쓰지 말 것. |
| **분야별 법규** | 자본시장법 시행령 제2조제6호는 전자적 투자조언장치가 자문·일임 시 **투자목적·재산상황·투자경험을 고려해 투자성향을 분석**하고 사고 예방·복구 체계 등을 갖추도록 한다. 제99조제1항제1호의2는 적법한 전자적 장치를 이용한 **일반투자자 자문·일임의 예외**를 규정한다. [제2조](https://www.law.go.kr/lsLinkCommonInfo.do?lsJoLnkSeq=1029500643), [제99조](https://www.law.go.kr/LSW//lsLawLinkInfo.do?chrClsCd=010202&lsId=010817&lsJoLnkSeq=1000930618&print=print). | 개인 입력이 전혀 없는 ETF 배분 백테스트는 **개인별 자문 적합성의 근거가 아니다**. 연구와 상용 자문은 구분. |
| **테스트베드 심사기준** | 코스콤은 사전심사에서 ‘투자자들에게 설명 가능한 알고리즘’ 및 투자성향별 **구분된 포트폴리오**를 보며, 본심사에서는 최대 6개월 실제 자금 운용·리밸런싱 원칙·시스템 안정성 등을 본다. 통과 심사는 **수익률 평가나 품질 보증이 아니다**. [심사프로세스](https://www.ratestbed.kr:7443/portal/main/contents.do?menuNo=200080), [유의사항](https://www.ratestbed.kr:7443/portal/main/contents.do?menuNo=200223). | ‘설명 가능’은 심사표의 실제 항목이지만 **SHAP 필수라는 뜻은 아니다**. 학생 팀 실험이 심사에 통과한 것으로 홍보하지 말 것. |
| **별개의 법적 권리** | 「신용정보법」 제36조의2는 일정 개인신용평가회사·금융회사 등의 **자동화평가**에 대해 결과·주요 기준·기초정보 개요의 설명을 요구하고 오류 정정·재산출을 청구할 수 있게 한다. [법 제36조의2](https://law.go.kr/LSW/lsLinkCommonInfo.do?lsJoLnkSeq=1025127741). | 개인신용 자동화평가 관련 권리를 **모든 ETF 주문의 일률적 설명청구권**으로 넓혀 인용하지 말 것. |


### 4. 해외 범위: EU와 미국

- **EU 「AI Act」 Annex III 제5호:** 개인 **신용도 평가·신용점수**(사기탐지 목적 예외), 개인의 **생명·건강보험 위험평가와 보험료 책정**을 고위험으로 열거하지만, **투자자문·포트폴리오 관리 자체는 이 목록에 명시되어 있지 않다**. 따라서 투자추천이라는 이유만으로 고위험이라고 단정할 수 없으며, 다른 기능이 결합되면 다시 검토해야 한다. EU 집행위도 금융 분야의 대표적 두 고위험 용도를 위와 같이 소개한다. [EU 집행위 AI Act Annex III](https://ai-act-service-desk.ec.europa.eu/en/ai-act/annex-3), [EU 집행위 금융분야 설명](https://finance.ec.europa.eu/news/ai-finance-2024-06-19_en).

- **EU에서의 ‘설명’의 수준:** 고위험 AI에 해당하면 법 제13조는 **사용 주체가 출력을 해석·적절히 사용**할 정도의 투명성과 사용지침을 요구한다. 이것도 ‘모든 투자자에게 SHAP 차트를 제공하라’는 규정이 아니다. 집행위의 2026-10-06 시행 안내에 따르면 Annex III 고위험 규정의 적용 예정일은 **2027-12-02**이다. [AI Act 제13조](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-13), [EU 집행위 시행 일정](https://digital-strategy.ec.europa.eu/en/policies/enforcement-ai-act).

- **미국 SEC, 2017:** SEC 발표문은 투자자문업자로 등록한 robo-adviser에 기존 Investment Advisers Act의 **신인의무**가 적용되며, 2017년 IM Guidance Update가 **정보공개·적합성·준법** 이행에 관한 직원의 제안을 제시했다고 설명한다. 같은 날 SEC 투자자 안내문은 투자자의 목표·기간·재산·위험수용도를 질문으로 파악하고, 추천에 쓴 정보·비용·인적 상담의 정도를 확인하라고 안내한다. **2017 IM Guidance Update 본문 자체는 SEC 원문 URL 접근 제한으로 [미확인]**이므로 그 문구·‘SHAP 의무’ 여부를 원문 확인한 사실처럼 인용하지 않는다. [SEC 보도자료 (실제 열람)](https://www.sec.gov/newsroom/press-releases/2017-52), [SEC 투자자 안내문](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-45), [미확인 원문 URL](https://www.sec.gov/investment/im-guidance-2017-02.pdf).

## 반대 증거와 한계

- **상관 피처:** Kumar et al. (2020)은 독립적으로 가린 입력의 조합이 학습 분포 밖
  (out-of-distribution, **실제 데이터에서 거의 나타나지 않는 조합**)으로 나가는 반례와,
  의존성을 보존하면 모델이 직접 쓰지 않은 상관 피처에도 기여도가 배분될 수 있음을 보였다.
  입력 변수의 선택·중복 여부만 바뀌어도 설명량이 달라질 수 있다.
  이 반례는 금융시장 실측 데이터 실험이 아니라 **수학·모형 반례**다.
  [원 논문 §§3–4](https://proceedings.mlr.press/v119/kumar20e/kumar20e.pdf).

- **설명 안정성:** Yuan et al. (2022)은 MIMIC-III 의료 데이터의 심층모형을 대상으로
  서로 다른 무작위 배경 표본에서 SHAP 값과 순위가 변하고, 배경 표본 수가 커지면
  흔들림이 줄어드는 것을 관찰했다. 따라서 프로젝트의 금융 데이터에서 같은 현상이
  **이미 확인됐다**고 주장할 수는 없고, 직접 반복 측정해야 한다.
  [원 논문 초록](https://arxiv.org/abs/2204.11351).

- **시계열 관계 파괴:** 시계열의 ‘오늘 변동성’과 ‘최근 20일 수익률’을 서로 다른 날짜에서
  합성하면 경제적·시간적 관계가 깨질 수 있다. TimeSHAP은 순차 입력에 대해 시점 단위
  기여도를 별도로 정의하므로, 단순 평탄화된 입력의 SHAP을 ‘시간상 원인’으로
  읽지 않도록 경고하는 **프로젝트 적용 해석**이다.
  [TimeSHAP](https://arxiv.org/abs/2012.00073), [KernelExplainer의 배경 대체 방식](https://shap.readthedocs.io/en/latest/generated/shap.KernelExplainer.html).

- **사후 기여도 ≠ 원인·행동 제안:** Kumar et al. (2020)은 ‘중요도가 큰 변수’가
  사용자가 수정할 수 있는 조치인지 또는 그 변수를 바꾸면 원하는 결과가 나오는지를
  SHAP만으로 알 수 없다고 지적한다. 투자자에게 ‘변동성이 높아져 채권 비중 증가에 기여했다’는
  모델의 국소 설명과 ‘변동성이 높으면 채권이 손실을 반드시 막는다’는 투자 조언을 분리해야 한다.
  [원 논문 §4](https://proceedings.mlr.press/v119/kumar20e/kumar20e.pdf).

- **시장 충격의 결과는 SHAP 바깥에 있다:** 사후 분석에서 ETF 비중을 설명하더라도
  이후 가격 경로에 따른 MDD(최대낙폭, 이전 고점 대비 최대 하락폭)와 실제 수익률의
  인과적 기여는 별도 검증 문제다. ‘모형이 그렇게 결정했다’와
  ‘그래서 시장에서 손실이 줄었다’를 혼동하지 않는다.
  [Lundberg & Lee (2017)의 단일 예측 설명 범위](https://proceedings.neurips.cc/paper/2017/file/8a20a8621978632d76c43dfd28b67767-Paper.pdf), [Milani et al. (2022)의 순차적 설명 범위](https://arxiv.org/abs/2202.08434).

- **규제의 역방향 한계:** 자율규제라는 사실은 아무 설명도 필요 없다는 뜻이 아니다.
  코스콤의 실제 심사표에는 투자자에게 설명 가능한 알고리즘이 있고,
  고영향 AI로 분류되는 **다른 용도**에는 설명 방안 관련 법적 의무가 있다.
  반대로 테스트베드 통과가 수익률 보증인 것도 아니다.
  [코스콤 심사](https://www.ratestbed.kr:7443/portal/main/contents.do?menuNo=200080), [인공지능기본법 제34조](https://law.go.kr/lsLinkCommonInfo.do?chrClsCd=010202&lsJoLnkSeq=1031810845), [코스콤 유의사항](https://www.ratestbed.kr:7443/portal/main/contents.do?menuNo=200223).

## 우리 프로젝트에 대한 시사점

1. **설명 대상을 고정:** 각 Walk-Forward 테스트 날짜에
   `(관측 상태, 모델 버전, 보상함수 유형, 결정론적 원행동, 비중 변환 후 11개 ETF 비중,
   실제 매매 비중, Safe-Guard 발동 여부)`를 저장한다.
   SHAP은 우선 **비중 변환 후 투자결정 함수**의 11개 출력을 ETF별로 설명한다.
   Safe-Guard가 덮어쓴 비중은 ‘PPO가 선택했다’고 표기하지 말고
   **안전규칙의 발동과 변경 전·후 비중을 별도 설명**한다.
   [KernelExplainer의 함수 출력 정의](https://shap.readthedocs.io/en/latest/generated/shap.KernelExplainer.html), [SB3 PPO의 행동 예측](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html).

2. **정확히 무엇을 말하는지 표기:** 예를 들어 ‘해당 거래일의 변동성 입력이 **이 모델의** 국고채 ETF 목표 비중을 학습기간의 기준값 대비 +3%p 높이는 방향으로 기여’라고 쓰고, ‘변동성 때문에 국고채가 향후 수익을 보장’이라고 쓰지 않는다. 설명마다 배경 표본 기간, 모델·윈도우, 기준 비중, 변수별 기여도, 최종 비중을 함께 적는다. [SHAP 원 논문](https://proceedings.neurips.cc/paper/2017/file/8a20a8621978632d76c43dfd28b67767-Paper.pdf), [SHAP 비판](https://proceedings.mlr.press/v119/kumar20e/kumar20e.pdf).

3. **시간 누수 없이 배경 선택:** 각 테스트 윈도우의 SHAP 배경은
   **해당 학습구간에서만** 고르고 보유 날짜를 기록한다.
   상승·급락·회복 등 학습 데이터 내 국면을 고르게 뽑거나 국면별로 별도 기준을 만드는 경우에도,
   기준이 달라지면 설명이 달라진다고 적는다. 다른 날짜 피처를 마구 섞는 마스킹과
   검증 윈도우 이후의 배경 선택을 피한다.
   [KernelExplainer 배경 데이터 정의](https://shap.readthedocs.io/en/latest/generated/shap.KernelExplainer.html), [Kumar et al. (2020)](https://proceedings.mlr.press/v119/kumar20e/kumar20e.pdf).

4. **안정성을 실제로 측정:** 동일 모델·동일 날짜에 대해 배경 표본을 여러 번
   다시 추출하여 상위 변수의 부호·순위 일치율을 보고한다.
   상관 입력은 그룹(예: 한국 주식, 미국 주식, 위험지표)별 결과도 비교하고,
   변수 중복 제거·그룹 마스킹 전후에 설명이 유지되는지 본다.
   KernelExplainer의 추정 표본 수(`nsamples`) 변경에도 민감한지 검사한다.
   이는 권장 실험이며 **연구 결과를 이 데이터에 적용했다고 주장하는 것이 아니다**.
   [Yuan et al. (2022)](https://arxiv.org/abs/2204.11351), [Kumar et al. (2020)](https://proceedings.mlr.press/v119/kumar20e/kumar20e.pdf), [KernelExplainer API](https://shap.readthedocs.io/en/latest/generated/shap.KernelExplainer.html).

5. **SHAP 이외의 설명을 병기:** 시점별 SHAP은 ‘입력 → 비중’을 보여주고, 투자자에게는 ‘이전 비중 → 현재 비중’, 리밸런싱 기준, 수수료·슬리피지, Safe-Guard와 MDD 이력, 동일가중·MVO 대비 실제 성과를 분리하여 보여준다. 그와 함께 사용자가 ‘왜 주식보다 채권인가’를 읽고 잘못된 결론을 내리지 않는지 **간단한 사용자 이해도 점검**을 설계한다. XRL 서베이는 사람을 위한 설명을 별도의 문제로 지적하고, 코스콤은 알고리즘의 설명 가능성과 합리적인 리밸런싱을 확인한다. [Puiutta & Veith (2020)](https://arxiv.org/abs/2005.06247), [코스콤 심사](https://www.ratestbed.kr:7443/portal/main/contents.do?menuNo=200080).

6. **상용화 표현을 엄격히 제한:** 현재 프로젝트에 투자자별 투자목적·재산·경험 입력이 없다면
   ‘**시세를 이용한 가상 자산배분 연구**’이지 ‘개인별 적합성을 검증한 로보어드바이저’가 아니다.
   국내 상용 자문 구상 시 자본시장법상 업자 지위·투자자 성향·테스트베드·AI기본법
   고영향 해당 여부를 별도로 검토한다. 2017년 SEC 가이던스 본문 상세를 근거로
   미국에서의 특정 XAI 기술 의무를 단정하지 않는다.
   [시행령 제2조](https://www.law.go.kr/lsLinkCommonInfo.do?lsJoLnkSeq=1029500643), [코스콤 참여요건](https://www.ratestbed.kr:7443/portal/main/contents.do?menuNo=200070), [인공지능기본법 제2조](https://www.law.go.kr/LSW/lsLinkCommonInfo.do?lsJoLnkSeq=1031810747), [SEC 2017 발표](https://www.sec.gov/newsroom/press-releases/2017-52).

## 참고문헌

- Lundberg, S. M., & Lee, S.-I. (2017). “A Unified Approach to Interpreting Model Predictions.” *Advances in Neural Information Processing Systems* 30. https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html
- Kumar, I. E., Venkatasubramanian, S., Scheidegger, C., & Friedler, S. A. (2020). “Problems with Shapley-value-based explanations as feature importance measures.” *Proceedings of the 37th International Conference on Machine Learning*, PMLR 119, 5491–5500. https://proceedings.mlr.press/v119/kumar20e.html
- Milani, S., Topin, N., Veloso, M., & Fang, F. (2022). “A Survey of Explainable Reinforcement Learning.” *arXiv:2202.08434*. https://arxiv.org/abs/2202.08434
- Puiutta, E., & Veith, E. M. S. P. (2020). “Explainable Reinforcement Learning: A Survey.” *arXiv:2005.06247*. https://arxiv.org/abs/2005.06247
- Bento, J., Saleiro, P., Cruz, A. F., Figueiredo, M. A. T., & Bizarro, P. (2020). “TimeSHAP: Explaining Recurrent Models through Sequence Perturbations.” *arXiv:2012.00073*. https://arxiv.org/abs/2012.00073
- Yuan, H., Liu, M., Kang, L., Miao, C., & Wu, Y. (2022). “An empirical study of the effect of background data size on the stability of SHapley Additive exPlanations (SHAP) for deep learning models.” *arXiv:2204.11351*. https://arxiv.org/abs/2204.11351
- SHAP 개발팀 (접속일 2026-10-13). “shap.KernelExplainer”; “shap.DeepExplainer.” *SHAP 공식 API 문서*. https://shap.readthedocs.io/en/latest/generated/shap.KernelExplainer.html ; https://shap.readthedocs.io/en/latest/generated/shap.DeepExplainer.html
- Stable-Baselines3 개발팀 (접속일 2026-10-13). “PPO.” *Stable-Baselines3 공식 문서*. https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html
- 금융위원회 (2021). 「금융분야 인공지능(AI) 가이드라인이 시행됩니다」. https://www.fsc.go.kr/no010101/76206
- 금융위원회 (2022). 「금융분야 인공지능 활용 활성화 및 신뢰확보 방안」, 「금융분야 AI 개발·활용 안내서」 발표. https://www.fsc.go.kr/no010101/78235
- 금융위원회 (2026). 「금융분야 인공지능 가이드라인」 개정안 발표·시행 안내. https://www.fsc.go.kr/po010103/87142
- 대한민국 법제처 (2026 시행본). 「인공지능 발전과 신뢰 기반 조성 등에 관한 기본법」 제2조·제31조·제34조. https://www.law.go.kr/LSW/lsLinkCommonInfo.do?lsJoLnkSeq=1031810747 ; https://www.law.go.kr/lsLinkCommonInfo.do?chrClsCd=010202&lsJoLnkSeq=1031810721 ; https://law.go.kr/lsLinkCommonInfo.do?chrClsCd=010202&lsJoLnkSeq=1031810845
- 대한민국 법제처 (2026 시행본). 「자본시장과 금융투자업에 관한 법률 시행령」 제2조·제99조, 「신용정보의 이용 및 보호에 관한 법률」 제36조의2. https://www.law.go.kr/lsLinkCommonInfo.do?lsJoLnkSeq=1029500643 ; https://www.law.go.kr/LSW//lsLawLinkInfo.do?chrClsCd=010202&lsId=010817&lsJoLnkSeq=1000930618&print=print ; https://law.go.kr/LSW/lsLinkCommonInfo.do?lsJoLnkSeq=1025127741
- 코스콤 로보어드바이저 테스트베드센터 (접속일 2026-10-13). 「심사프로세스 소개」, 「참여 기본 요건」, 「유의사항」. https://www.ratestbed.kr:7443/portal/main/contents.do?menuNo=200080 ; https://www.ratestbed.kr:7443/portal/main/contents.do?menuNo=200070 ; https://www.ratestbed.kr:7443/portal/main/contents.do?menuNo=200223
- European Union / European Commission (2024; 2026-07-27 통합 표시본). *Regulation (EU) 2024/1689 (AI Act)*, Annex III 및 Article 13. https://ai-act-service-desk.ec.europa.eu/en/ai-act/annex-3 ; https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-13
- European Commission, DG FISMA (2024). “AI in finance.” https://finance.ec.europa.eu/news/ai-finance-2024-06-19_en
- European Commission (2026). “The enforcement framework of the AI Act.” https://digital-strategy.ec.europa.eu/en/policies/enforcement-ai-act
- U.S. Securities and Exchange Commission (2017). “SEC Staff Issues Guidance Update and Investor Bulletin on Robo-Advisers.” https://www.sec.gov/newsroom/press-releases/2017-52
- U.S. Securities and Exchange Commission, Office of Investor Education and Advocacy (2017). “Investor Bulletin: Robo-Advisers.” https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-45
- U.S. Securities and Exchange Commission, Division of Investment Management (2017). “Robo-Advisers,” *IM Guidance Update No. 2017-02*. **본문 [미확인]:** SEC PDF 직접 열람 제한. https://www.sec.gov/investment/im-guidance-2017-02.pdf
