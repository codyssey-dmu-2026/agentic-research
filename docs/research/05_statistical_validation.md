# 전략 성과의 통계 검증: ANOVA 요구사항과 금융 시계열의 함정

## 핵심 결론

- 미션의 One-way ANOVA 2개, Two-way ANOVA 1개, Tukey HSD와 η²는 **요구 산출물로 수행**하되, 같은 날짜의 전략 수익률을 서로 독립된 표본처럼 취급한 *p*값을 우월성의 최종 증거로 쓰면 안 된다. ANOVA의 독립·정규·등분산 가정과 Tukey의 등분산 가정은 공식 문서에도 명시되어 있다. [SciPy `f_oneway`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html), [statsmodels `pairwise_tukeyhsd`](https://www.statsmodels.org/stable/generated/statsmodels.stats.multicomp.pairwise_tukeyhsd.html)

- 금융 수익률은 두꺼운 꼬리와 변동성 군집을 보인다. 원자산 수익률의 **선형** 자기상관이 종종 작더라도 독립성이 성립하는 것은 아니며, 전략의 같은 날짜 수익률은 공통 시장 충격도 공유한다. 따라서 날짜가 정렬된 **짝별 성과 차이**와 시간 블록 신뢰구간을 주된 보완 증거로 제시한다. [Cont (2001)](http://rama.cont.perso.math.cnrs.fr/pdf/empirical.pdf), [Ledoit & Wolf (2008)](http://www.ledoit.net/jef_2008pdf.pdf)

- 위험조정수익률(Sharpe)의 차이는 평균 일수익률에 대한 ANOVA와 **다른 귀무가설**이다. Jobson–Korkie/Memmel의 고전적 Sharpe 검정은 비정규·시계열 자료에 취약하며, Ledoit–Wolf의 *studentized time-series block bootstrap*이 직접적인 보완책이다. [Ledoit & Wolf (2008), 원문 §2–5](http://www.ledoit.net/jef_2008pdf.pdf)

- PPO 학습 시드가 달라지면 성과도 달라진다. 시드 ≥10개를 **프로젝트의 사전 계획값**으로 권고하되 이것이 어떤 보편적 통계 기준이라는 뜻은 아니다. 같은 시장을 10회 재사용했다고 독립적인 시장 10개가 생기는 것은 아니며, 세 테스트 연도만으로 국면 일반화를 입증하기 어렵다. [Henderson et al. (2018)](https://cdn.aaai.org/ojs/11694/11694-13-15222-1-2-20201228.pdf), [Agarwal et al. (2021)](https://proceedings.neurips.cc/paper_files/paper/2021/file/f514cec81cb148559cf475e7426eed5e-Paper.pdf)

- 보상함수·시드·윈도우·하이퍼파라미터 중 최고 결과만 고르면 데이터 스누핑이 발생한다. Tukey는 **주어진 그룹들의 쌍별 비교**를 조정할 뿐 탐색 전체를 지우지 못한다. 사전 지정한 비교, 별도 테스트 자료, 탐색 전체를 포함하는 White Reality Check/Hansen SPA를 구분한다. [White (2000)](https://www.econometricsociety.org/publications/econometrica/2000/09/01/reality-check-data-snooping), [Hansen (2005)](https://cdr.lib.unc.edu/downloads/zp38wf793?locale=en), [statsmodels Tukey 문서](https://www.statsmodels.org/stable/generated/statsmodels.stats.multicomp.pairwise_tukeyhsd.html)

## 근거

### 먼저 읽는 용어

- **표본 밖 검증(OOS, out-of-sample):** 학습·후보 선정에 쓰지 않은 날짜로 고정된 전략을 평가한다. 테스트 자료를 보고 다시 고르면 ‘처음 보는 데이터’가 아니다. [White (2000), §1](https://users.ssc.wisc.edu/~behansen/718/White2000.pdf)

- **위험조정수익률(Sharpe ratio):** 동일 기간의 평균 초과수익률(수익률−무위험수익률)을 그 수익률의 변동성(표준편차)으로 나눈 값이다. 값의 **차이**는 평균 수익률의 차이와 다른 질문이다. [Ledoit & Wolf (2008), §2](http://www.ledoit.net/jef_2008pdf.pdf)

- **신뢰구간:** 성과 차이의 추정 불확실성을 일정 범위로 표시한다. 95% 구간은 같은 절차를 반복할 때 구성한 구간이 참값을 덮는 장기 비율의 뜻이며, ‘이 전략이 95% 확률로 이긴다’는 뜻이 아니다. [Agarwal et al. (2021), §2](https://proceedings.neurips.cc/paper_files/paper/2021/file/f514cec81cb148559cf475e7426eed5e-Paper.pdf)

- **블록·시드:** 블록은 이웃한 날짜를 묶어 재표집하는 단위, 시드는 PPO 재학습의 난수 출발점이다. 날짜 블록의 수와 학습 시드의 수는 서로 다른 불확실성을 가리킨다. [Ledoit & Wolf (2008), §3.2](http://www.ledoit.net/jef_2008pdf.pdf), [Henderson et al. (2018)](https://cdn.aaai.org/ojs/11694/11694-13-15222-1-2-20201228.pdf)

- **귀무가설과 *p*값:** 귀무가설은 ‘전략 간 차이가 없다’와 같은 기준 주장이고, *p*값은 해당 가정들이 맞을 때 지금만큼 극단적인 통계량이 관측될 확률이다. 가정이 틀리면 작은 *p*도 차이에 대한 안전한 증거가 아니다. [SciPy `f_oneway`, Notes](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html)

### 무엇을 검정하는가

- **ANOVA**(분산분석): 여러 그룹의 평균이 같은지 검정한다. One-way는 요인 하나(예: 전략), Two-way는 두 요인(예: 전략 × 사전에 정한 시장 국면)과 두 요인의 **상호작용**(한 요인의 효과가 다른 요인에 따라 달라지는가)을 분리한다. 기본 F검정에는 독립 관측, 각 그룹의 정규분포, 집단 간 동일 분산이 필요하다. 엄밀히는 그룹·셀 내부 **모형 오차**의 분포와 관측 설계가 중요하다. [SciPy `f_oneway`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html), [statsmodels `anova_lm`](https://www.statsmodels.org/stable/generated/statsmodels.stats.anova.anova_lm.html)

- 동일가중, MVO, PPO는 같은 날짜에 같은 시장의 충격을 겪는다. 전략별 일별 수익률을 세 개의 독립 그룹으로 늘어놓으면 **횡단면 짝짓기**를 놓치고, 인접 날짜가 연관되면 **시계열 독립성**도 잃는다. 이는 같은 날짜 관측끼리 짝지어 분석해야 한다는 연구 설계상의 추론이다. 일반 ANOVA의 독립성 요건과 수익률의 시계열 의존성에 근거한다. [SciPy `f_oneway`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html), [Cont (2001)](http://rama.cont.perso.math.cnrs.fr/pdf/empirical.pdf)

- **Cont (2001)**는 주식·상품·지수·환율 등 여러 금융 시계열의 실증적 공통 속성을 정리하고 BMW 주식의 **1992–1998년 일별 수익률** 등 사례로 두꺼운 꼬리, 절댓값·제곱수익률의 자기상관, 변동성 군집을 보였다. 단, 원수익률의 선형 자기상관은 유동 시장에서 흔히 작다고도 명시한다. 이 논문의 사례가 국내 ETF 11개의 2018–2025년 자료에서 동일한 정도의 위반을 **실증했다는 뜻은 아니다**. [원문 §2, §3, §5](http://rama.cont.perso.math.cnrs.fr/pdf/empirical.pdf)

- **Lo (2002)**는 독립동분포·정상 시계열·시간 집계 조건별 Sharpe 추정의 불확실성을 유도하고, 뮤추얼펀드·헤지펀드 사례에서 자기상관이 Sharpe 연율화와 순위를 바꿀 수 있음을 보였다. 월 Sharpe에 기계적으로 √12를 곱하는 것은 특별한 조건에서만 맞는다. [CFA Institute 원문 소개](https://rpc.cfainstitute.org/research/financial-analysts-journal/2002/the-statistics-of-sharpe-ratios)

### 관측 단위: 늘어난 표본수가 늘어난 독립 실험은 아니다

| 단위 | 장점 및 적합한 질문 | 독립성·해석상 제약 |
| --- | --- | --- |
| **일별 순수익률** `r_{전략,t}` | 같은 날짜의 `PPO − 동일가중`처럼 **짝별 일간 차이** 계산; 비용 포함 시뮬레이션의 기본 기록. | 같은 날짜 전략끼리 상관되고, 날짜 간 수익률·변동성의 의존성 가능. 일별 F검정의 표본수를 독립 시행 횟수로 읽지 말 것. [Cont (2001)](http://rama.cont.perso.math.cnrs.fr/pdf/empirical.pdf), [SciPy ANOVA](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html) |
| **비중첩 월별 순수익률** | 일정한 월별 리밸런싱과 비교하기 쉽고 연속 21거래일 *rolling* 수익률의 인위적 중첩을 피한다. | 세 개의 1년 테스트라면 월 관측치는 대략 36개에 불과하고, 같은 달의 전략들은 여전히 짝이며 국면에 따라 분산이 다를 수 있다. [Lo (2002)](https://rpc.cfainstitute.org/research/financial-analysts-journal/2002/the-statistics-of-sharpe-ratios), [Cont (2001)](http://rama.cont.perso.math.cnrs.fr/pdf/empirical.pdf) |
| **윈도우별 Sharpe/MDD** | 1년짜리 OOS(표본 밖) 윈도우의 위험조정수익·전체 경로 낙폭을 그대로 평가한다. | 이 프로젝트는 세 개의 테스트 윈도우뿐이다. 학습 기간이 겹치고 시장이 연속되어 독립적인 ‘시장 3번의 무작위 추출’로 가정하기도 어렵다. **MDD는 경로상 최고점 대비 최대 하락률**이므로 일별 독립 성과 행으로 만들지 않는다. [Ledoit & Wolf (2008)](http://www.ledoit.net/jef_2008pdf.pdf), [Cont (2001)](http://rama.cont.perso.math.cnrs.fr/pdf/empirical.pdf) |
| **시드별 PPO 재학습** | 같은 설정에서 초기화·학습 난수에 따른 **알고리즘 변동성**을 측정한다. | 10시드 × 3년 = 30개 성과값을 독립적인 시장 30개로 해석하면 의사반복이다. 동일가중·MVO를 시드별로 복제해 표본수를 늘려서도 안 된다. [Henderson et al. (2018)](https://cdn.aaai.org/ojs/11694/11694-13-15222-1-2-20201228.pdf), [Agarwal et al. (2021)](https://proceedings.neurips.cc/paper_files/paper/2021/file/f514cec81cb148559cf475e7426eed5e-Paper.pdf) |

- **반복측정 ANOVA/블록 설계**: 동일한 날짜(또는 월)를 *블록*으로 놓고 각 블록 안에서 모든 전략을 평가한다. statsmodels의 `AnovaRM`은 완전 균형 **within-subject** 설계만 지원하고 구형성(*sphericity*: 반복 측정 간 차이의 분산이 쌍마다 같아야 함) 위반 보정과 between-subject 효과는 구현하지 않는다. ‘날짜 블록’을 써도 서로 이웃한 블록의 시간 의존성이 사라지는 것은 아니므로 별도 블록 부트스트랩이 필요하다. [statsmodels `AnovaRM`](https://www.statsmodels.org/stable/generated/statsmodels.stats.anova.AnovaRM.html), [Ledoit & Wolf (2008)](http://www.ledoit.net/jef_2008pdf.pdf)

- **Friedman 검정**은 동일 블록에 여러 처리(전략)를 반복 측정한 경우의 순위 기반 대안이지만, 세 전략·세 테스트 연도만을 ‘독립 블록 세 개’로 쓰면 근사 *p*값이 불안정하다. SciPy 문서에는 카이제곱 근사가 `n > 10`과 반복 표본이 6개보다 많을 때 신뢰 가능하다는 주의가 있다. 월별 블록을 써도 달 사이 의존은 따로 다뤄야 한다. [SciPy `friedmanchisquare`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.friedmanchisquare.html), [Cont (2001)](http://rama.cont.perso.math.cnrs.fr/pdf/empirical.pdf)

### 요구 검정과 그 대안의 정확한 범위

- **Welch ANOVA**는 집단 분산이 달라도 되는 One-way 평균검정이다. SciPy `f_oneway(equal_var=False)`는 **1.16.0부터** 이를 지원하고, statsmodels `anova_oneway(use_var='unequal')`도 제공한다. 그러나 둘 다 **독립 표본** 방법이므로 같은 날의 전략 상관이나 시간 의존은 해결하지 못한다. 심하게 비대칭인 표본에서는 Welch도 유의수준을 벗어날 수 있다고 statsmodels가 경고한다. [SciPy `f_oneway`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html), [statsmodels `anova_oneway`](https://www.statsmodels.org/stable/generated/statsmodels.stats.oneway.anova_oneway.html)

- **Kruskal–Wallis**는 정규 가정에 덜 의존하는 순위 기반 **독립 그룹** 검정이지, 같은 날의 짝을 보존하는 검정이 아니다. 검정 대상도 평균수익률·Sharpe가 아니다. 따라서 일별 수익률을 전략별 독립 열로 전달하는 것은 ‘비모수니까 안전’하지 않다. [SciPy `kruskal`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html)

- **Tukey HSD**는 모든 쌍의 평균 차이를 검사하고 쌍별 다중비교를 조정하지만, 기본적으로 집단 내 분산 동일과 독립 표본을 전제한다. 분산이 다르면 **Games–Howell**로 쌍별 후속검정을 바꿀 수 있으나 역시 날짜 짝짓기·시간 의존을 고치지는 않는다. statsmodels **0.15**부터 `pairwise_tukeyhsd(..., use_var='unequal')`이 Games–Howell이며, SciPy `tukey_hsd(..., equal_var=False)`도 이를 명시한다. [statsmodels `pairwise_tukeyhsd`](https://www.statsmodels.org/stable/generated/statsmodels.stats.multicomp.pairwise_tukeyhsd.html), [SciPy `tukey_hsd`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.tukey_hsd.html)

- **Jobson & Korkie (1981)**는 두 투자전략의 Sharpe/Treynor 성과 비교 검정을 제시했고 **Memmel (2003)**은 Sharpe 검정식을 수정했다. [원문 미확인: 두 원문의 본문은 직접 열람되지 않았음; 출판 서지는 원 논문 DOI와 저자 기관 목록, 수정 사실과 적용 가정은 직접 읽은 Ledoit–Wolf 원문 §1–2에서 확인.] [Jobson–Korkie 원문 DOI 서지](https://doi.org/10.1111/j.1540-6261.1981.tb04891.x), [Memmel 저자 기관 목록](https://www.bundesbank.de/en/christoph-memmel), [Ledoit & Wolf (2008)](http://www.ledoit.net/jef_2008pdf.pdf)

- **Ledoit & Wolf (2008)**는 위 고전적 Sharpe 차이 검정이 **정규·독립동분포(i.i.d.) 쌍별 수익률**에 의존한다는 점을 보이고, Student화한 **시간 블록 부트스트랩 신뢰구간**(원래의 통계량 차이를 표준오차로 나눠 재표집하는 방법)을 제안했다. 120개월 길이의 정규·t₆ 두꺼운 꼬리·GARCH 변동성 군집·VAR 자기상관 모의실험에서 고전 검정은 명목 5%의 영가설을 t₆ i.i.d. 경우 **10.7%** 기각했고 시간 블록 방법은 **5.0%**였다. 실제 두 펀드 쌍의 1994.01–2003.12 월별 초과수익률에서도 검정별 결론이 달랐다. [원문 표 1–3, §4–6](http://www.ledoit.net/jef_2008pdf.pdf)

- **블록 부트스트랩**(붙어 있는 관측일을 묶어 재표집)은 시간 의존을 보존한다. 전략 비교에서는 *동일한 날짜 인덱스의 모든 전략 수익률을 함께* 재표집하여 짝별 상관을 보존한다. Ledoit–Wolf는 **전략 쌍**을 묶는 circular block bootstrap을 사용했고, White와 Hansen은 다수 대안의 성과차 벡터를 위한 stationary bootstrap을 사용했다. 블록 길이와 시계열 정상성·구조 변화의 민감도는 여전히 남는다. [Ledoit & Wolf (2008), §3.2](http://www.ledoit.net/jef_2008pdf.pdf), [White (2000), §2](https://users.ssc.wisc.edu/~behansen/718/White2000.pdf), [Hansen (2005), §3](https://cdr.lib.unc.edu/downloads/zp38wf793?locale=en)

- **Diebold–Mariano (1995)**는 *같은 대상*을 예측한 두 모델의 시점별 **손실 차이**의 기대값이 0인지 비교하며 손실 차이의 자기상관을 고려한다. 이는 **예측오차·사전 정의한 시점별 의사결정 손실**에 쓸 때 적합하고, ‘PPO의 Sharpe가 높다’ 또는 ‘연간 MDD가 낮다’의 자동 대체 검정은 아니다. statsmodels `diebold_mariano_test`는 관측 목표 `y`와 두 예측치, 손실 함수(`criterion`)를 요구한다. 투자전략 의사결정의 손실 비교는 White/Hansen이 제시한 전략·거래규칙 성과차 틀과 혼동하지 말 것. [Diebold–Mariano 원논문 서지](https://doi.org/10.1080/07350015.1995.10524599), [statsmodels DM 문서](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.diebold_mariano_test.html), [Hansen (2005), 원문 Example 3](https://cdr.lib.unc.edu/downloads/zp38wf793?locale=en)

### 강화학습의 반복과 다중검정

- **Henderson et al. (2018)**은 MuJoCo의 Hopper-v1·HalfCheetah-v1 연속제어에서 PPO 등 정책경사 알고리즘을 실험했다. 같은 설정의 **10번 실행을 서로 다른 5개 시드 그룹으로 나눌 때** 학습곡선이 크게 달라질 수 있었고 구현·하이퍼파라미터도 결과에 영향을 주었다. 금융 ETF에서 확인한 수치가 아니라 **시드 실험을 설계할 근거**다. [AAAI 원문 Experimental Analysis, Random Seeds](https://cdn.aaai.org/ojs/11694/11694-13-15222-1-2-20201228.pdf)

- **Agarwal et al. (2021)**은 Atari 100k의 **26게임** 등에 대한 3–10개 실행의 비교가 점추정만으로 뒤바뀔 수 있음을 보이고, 다양한 실행의 분포·사분위 평균·신뢰구간을 권장했다. 게임별 실행을 계층적으로 재표집한 신뢰구간을 국내 주식의 **시간 순서 없는 일별 재표집**으로 그대로 이식해서는 안 된다. [NeurIPS 원문 §1–4](https://proceedings.neurips.cc/paper_files/paper/2021/file/f514cec81cb148559cf475e7426eed5e-Paper.pdf)

- **White (2000)**는 같은 자료에서 많은 후보를 고르면 최고의 후보가 운으로 나타날 수 있음을 정식화하고, 기준 전략 대비 여러 후보 중 최선의 우월성을 공동 검정하는 Reality Check를 제시했다. 실제 예로 **1988.03–1994.05 S&P 500 일별 자료** 중 **1991.06–1994.05**를 예측 평가에 썼다. [Econometrica 원문 §1–4](https://users.ssc.wisc.edu/~behansen/718/White2000.pdf)

- **Hansen (2005)**은 White 검정이 형편없는 후보가 추가될수록 검정력이 약해질 수 있다고 지적하고 Student화와 표본에 따른 귀무분포를 쓰는 **SPA**(Superior Predictive Ability)를 제안했다. 미국 연간 인플레이션 예측을 다수 회귀 예측 대 random walk로 비교한 실증·모의실험으로 설명했고, 원문 §2는 **거래규칙**도 손실함수로 표현한다. 단, 그의 검정은 성과차 시계열의 정상성 등 조건이 있으며 윈도우마다 정책이 바뀌는 본 실험에 자동 보증이 아니다. [Journal of Business & Economic Statistics 원문](https://cdr.lib.unc.edu/downloads/zp38wf793?locale=en)

- **Harvey, Liu & Zhu (2016)**는 **313편의 연구, 316개 후보 요인**을 모아 반복적인 요인 발견으로 평범한 `|t| ≈ 2`가 부족하다고 논하고, **새 주식 수익률 횡단면 요인**에 `t > 3`의 더 높은 문턱을 제안했다. 이는 한국 ETF 전략의 ANOVA에서 `t > 3`을 기계적 합격선으로 쓰라는 주장이 **아니다**. 여러 보상·비용·윈도우 설정을 살핀 뒤 발견만 보고하면 탐색을 반영해야 한다는 경고다. [Review of Financial Studies 원문 §1, §3](https://people.duke.edu/~charvey/Research/Published_Papers/P118_and_the_cross.PDF)

### 효과크기는 *p*값과 별도로 읽는다

- **효과크기 η²**(에타 제곱)는 표본에서 관측된 총 변동 가운데 ANOVA 요인과 연결된 비율이다. 일반 One-way에서는 `η² = SS_between / SS_total`, 여기서 `SS`는 **제곱합**(평균에서의 편차 제곱을 합한 값)이다. Two-way에서는 요인마다 `SS_요인 / SS_total`을 표시하고, **부분 η²**는 `SS_요인 / (SS_요인 + SS_error)`로 분모가 다르다. 불균형 자료의 Type II/III 제곱합은 요인끼리 단순히 더해 총제곱합이 된다고 가정하지 않는다. ANOVA 표의 `sum_sq`와 분모 정의를 함께 제시한다. [Lakens (2013), Eta-squared 절](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2013.00863/full), [statsmodels `anova_lm`의 Type별 설명](https://www.statsmodels.org/stable/generated/statsmodels.stats.anova.anova_lm.html)

- **ω²**(오메가 제곱)는 η²의 작은 표본 낙관 편향을 완화하려는 효과크기다. 일반 One-way 예시는 `(SS_between − (k−1)·MS_error) / (SS_total + MS_error)`, `MS_error = SS_error/(N−k)`; 이는 **독립 그룹을 가정한 기존 ANOVA**의 해석으로, 잘못된 독립성을 ω²가 고쳐주지는 않는다. 작은 표본에서는 ω²도 완벽히 불편(편향 없음)이라고 단언하지 않는다. [Lakens (2013), Omega-squared 절](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2013.00863/full)

- **Cohen의 관례적 η² 크기** 0.01/0.06/0.14(작음/중간/큼)는 원래 행동과학의 대략적 비교치다. 짝·반복측정 설계와 총변동의 정의가 달라지면 비교 자체가 어려워서 ETF 전략의 ‘투자 가치’ 기준으로 기계적으로 쓰지 않는다. **연율화 Sharpe 차이, 순수익률 차이, 거래비용, MDD 차이(퍼센트포인트)**를 신뢰구간과 함께 보고한다. [Cohen (1988), 출판사 서지](https://www.routledge.com/Statistical-Power-Analysis-for-the-Behavioral-Sciences/Cohen/p/book/9780805802832), [Lakens (2013), 적용 범위 주의](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2013.00863/full)

## 반대 증거와 한계

- **주요 가설에 불리한 예:** Ledoit–Wolf의 1994–2003년 120개월 펀드 두 쌍 비교에서는 고전 검정 *p*가 **3.9%/1.0%**여서 5%에서 차이가 있다고 읽히지만, 시간 블록 방법은 **9.2%/29.4%**여서 그렇게 결론 내리지 못한다. 동일한 성과차라도 금융 시계열의 가정을 무시하면 ‘유의한 개선’이 가짜일 수 있다. **해당 펀드에서의 결과이지 우리 PPO가 실패했다는 실험 결과는 아니다.** [Ledoit & Wolf (2008), 표 2–3](http://www.ledoit.net/jef_2008pdf.pdf)

- **일별 표본이 많아도 실질 검증 기간은 짧다:** 서로 다른 씨드로 같은 3년의 OOS 일별 자료를 반복 측정해도 다른 금리·위기·시장 국면이 생기지 않는다. 월별 집계는 겹침을 줄이지만 세 연도를 넘는 시장 일반화나 드문 15% MDD 초과 확률의 정밀 추정까지 제공하지 않는다. [Agarwal et al. (2021), 소수 실행 불확실성](https://proceedings.neurips.cc/paper_files/paper/2021/file/f514cec81cb148559cf475e7426eed5e-Paper.pdf), [Cont (2001), 정적성·꼬리 위험 논의](http://rama.cont.perso.math.cnrs.fr/pdf/empirical.pdf)

- **Welch·Games–Howell·Kruskal–Wallis도 만능이 아니다:** 각각 이분산 또는 분포 가정을 일부 완화하지만 같은 날짜의 전략 상관, 시계열 의존, 정책 교체에 따른 분포 이동은 해결하지 않는다. 반복측정 ANOVA 역시 독립적인 날짜 블록이라는 근사와 구현상의 구형성 제약이 남는다. [SciPy ANOVA](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html), [SciPy Kruskal](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html), [statsmodels `AnovaRM`](https://www.statsmodels.org/stable/generated/statsmodels.stats.anova.AnovaRM.html)

- **부트스트랩도 완전한 안전망은 아니다:** White/Hansen의 성과차 정상성, Ledoit–Wolf의 규칙성·시간 의존 조건이 급격한 국면 교체에서 깨질 수 있다. 15% MDD Safe-Guard로 백테스트를 중단하고 이후 데이터를 버리면 전략별 관측 기간마저 달라진다. 드문 하락이 관측되지 않았다면 어느 재표집도 이를 만들어 확실한 손실 상한을 증명할 수 없다. [Hansen (2005), Assumption 1·정책 교체 제약](https://cdr.lib.unc.edu/downloads/zp38wf793?locale=en), [Ledoit & Wolf (2008), §3–4](http://www.ledoit.net/jef_2008pdf.pdf), [Cont (2001), 극단값·비정상성](http://rama.cont.perso.math.cnrs.fr/pdf/empirical.pdf)

- **유의하지 않음 ≠ 동일 성과:** 시드·윈도우가 적어 신뢰구간이 넓으면 효과가 없어도, 커도, 둘 다 자료와 양립할 수 있다. Agarwal 등은 단일 *p*값에 따른 이분법 대신 **성과 차이의 구간과 분포** 보고를 강조한다. [Agarwal et al. (2021), §2 Remark·§4](https://proceedings.neurips.cc/paper_files/paper/2021/file/f514cec81cb148559cf475e7426eed5e-Paper.pdf)

## 우리 프로젝트에 대한 시사점

### 미션 요구를 지키면서 타당성을 높이는 검증 설계

1. **비교 대상·평가 규칙을 OOS 성과 확인 전에 고정**한다. 세 보상함수 PPO와 동일가중·MVO를 동일 날짜·동일 ETF 데이터와 동일 비용률(수수료 0.015% + 슬리피지 0.05%) 아래 기록하되, 리밸런싱 주기는 전략별로 **사전에** 명시한다(동일가중·MVO의 월간 주기와 PPO의 예정 주기를 억지로 같게 바꾸지 않는다). 세 1년 테스트 윈도우의 일별 순수익률을 `날짜 × 전략 × 보상 × 학습시드 × 테스트윈도우`로 정렬해 결측·중단일을 기록한다. 최초 사전 주요 비교는 예를 들어 `PPO(사전 고정한 보상·시드 집계) − 동일가중`, `PPO − MVO`로 명시한다. **설계 제안**이며 결과의 근거는 시간 정렬·여러 후보를 고려한 원 논문들이다. [Ledoit & Wolf (2008)](http://www.ledoit.net/jef_2008pdf.pdf), [White (2000)](https://users.ssc.wisc.edu/~behansen/718/White2000.pdf)

2. **학습 난수 ≥10개**를 보상함수마다 **미리 고정해 전부** 학습·평가하고 각 윈도우에서 시드별 Sharpe·MDD·순수익률, 중앙값·분산·최악값을 공개한다. 비용상 10개가 어렵다면 5개도 기술하고 시드 효과의 구간 불확실성을 명시하되 5개를 검정력 보장으로 포장하지 않는다. 동일가중/MVO는 시드가 없고 10번 복사한다고 비교군의 독립 실험이 되지 않는다. ≥10은 본 프로젝트 권고값이지 두 RL 논문이 정한 보편 하한이 아니다. [Henderson et al. (2018)](https://cdn.aaai.org/ojs/11694/11694-13-15222-1-2-20201228.pdf), [Agarwal et al. (2021)](https://proceedings.neurips.cc/paper_files/paper/2021/file/f514cec81cb148559cf475e7426eed5e-Paper.pdf)

3. **요구 One-way ANOVA #1:** 전략을 요인으로 하고 **비중첩 월별 순수익률**(공통 3개 OOS 윈도우에서 동일한 달)을 반응으로 표준 F, Tukey 쌍별 결과, `η² = SS_전략/SS_total`을 표에 낸다. **One-way ANOVA #2:** PPO 보상함수 3개를 요인으로 하고 **시드 × 테스트윈도우별 Sharpe**를 반응으로 같은 표를 낸다. 두 검정은 미션 요구를 충족하지만 월간 날짜 공유·시드별 같은 시장 경로 때문에 **F/Tukey의 명목 *p*값은 탐색적 기술치**로 표기한다. Sharpe를 월간 순수익 ANOVA 결과라고 잘못 부르지 않는다. [SciPy `f_oneway`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html), [Ledoit & Wolf (2008)](http://www.ledoit.net/jef_2008pdf.pdf)

4. **요구 Two-way ANOVA:** 모든 전략을 같은 월에 놓고 `전략 × 사전에 정의한 국면`(예: 그 달이 시작되기 **전에 관찰 가능한** 시장변동성 기준; 기준값은 학습 구간만으로 정함)의 월별 순수익률에 `anova_lm(..., typ=2/3)`의 주효과·상호작용 F, 각 요인 `η² = SS_요인/SS_total`을 보고한다. 결측으로 셀별 수가 다르면 Type I 제곱합은 입력 순서에 영향받고, Type III는 대비 코딩과 상호작용 해석에 주의한다. **날짜 고정효과**를 넣으면 모두에게 공통인 ‘국면 주효과’는 날짜 효과와 겹쳐 별도 추정 불가하다. 상호작용 보완은 **같은 월 PPO−동일가중 차이**가 사전 정의 국면에 따라 바뀌는지를 시간 블록으로 평가한다. 세 테스트 연도의 국면 수가 적으면 검정력 제약도 공개한다. [statsmodels `anova_lm` Type I/II/III 설명](https://www.statsmodels.org/stable/generated/statsmodels.stats.anova.anova_lm.html), [Cont (2001)](http://rama.cont.perso.math.cnrs.fr/pdf/empirical.pdf)

5. **가정 점검과 보조 표:** 전략·국면별 분포/극단치, 분산, 같은 날 전략간 상관, 차이 수익률 및 그 제곱의 자기상관을 확인한다. `scipy.stats.levene(center='median')`와 `statsmodels.stats.diagnostic.acorr_ljungbox`의 사용 목적은 각각 분산 동일성·자기상관 **진단**이지 통과를 강제해 가정 위반을 없애는 것이 아니다. One-way 참고표에 Welch F와 Games–Howell, 순위 검정 Kruskal–Wallis의 결과를 함께 싣고 **이들 역시 독립성 미해결**이라고 명시한다. [SciPy `levene`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.levene.html), [statsmodels Ljung–Box](https://www.statsmodels.org/stable/generated/statsmodels.stats.diagnostic.acorr_ljungbox.html), [SciPy `f_oneway`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html), [statsmodels Tukey/Games–Howell](https://www.statsmodels.org/stable/generated/statsmodels.stats.multicomp.pairwise_tukeyhsd.html)

6. **최종 비교는 짝별 시간 블록 분석:** 각 날짜에 `PPO−동일가중`, `PPO−MVO` 순수익 차이를 만들고, 각 OOS 테스트 윈도우 **내에서만** 같은 블록 인덱스를 모든 전략·시드에 적용해 전체 성과를 다시 계산한다. 블록 길이는 여러 사전 지정 값으로 민감도 검사하고 기간 전후·윈도우 경계를 섞지 않는다. Sharpe는 **같은 일별 무위험수익률을 뺀 초과수익** 기준으로 전략별 재계산해 차이의 95% 구간에 0이 드는지 제시하고, 연율화·위험자산 혼합 기준을 통일한다. 경로 전체 누적액에서 MDD와 15% 초과 여부도 **재계산**하고, ANOVA/Sharpe만으로 손실 한도를 입증했다고 하지 않는다. 시드는 학습 불확실성, 날짜 블록은 시장경로 불확실성을 다루며 이를 분리 보고한다. [Ledoit & Wolf (2008), §3.2](http://www.ledoit.net/jef_2008pdf.pdf), [Lo (2002)](https://rpc.cfainstitute.org/research/financial-analysts-journal/2002/the-statistics-of-sharpe-ratios), [Agarwal et al. (2021)](https://proceedings.neurips.cc/paper_files/paper/2021/file/f514cec81cb148559cf475e7426eed5e-Paper.pdf)

7. **Safe-Guard와 판정:** MDD 15% 초과로 포지션을 청산하면 청산 거래비용과 **남은 테스트 기간의 현금 보유 수익률** 등을 사전에 정해 모두 같은 종료일로 평가한다. 중단 이후 날짜를 제거해 성과가 좋은 날만 남기는 방식은 금지한다. 주 평가표에 전략별 윈도우/시드 Sharpe 차이와 95% 구간, 순수익, MDD, **15% 위반 횟수**를 나란히 제시한다. ‘우월’은 사전에 정한 PPO-vs-기준 Sharpe 차이의 구간이 0보다 높고 비용·낙폭도 목표를 충족할 때의 **해당 OOS 기간에 조건부인 결론**으로 한정한다. [White (2000), 후보 선택과 평가 분리](https://users.ssc.wisc.edu/~behansen/718/White2000.pdf), [Ledoit & Wolf (2008)](http://www.ledoit.net/jef_2008pdf.pdf)

8. **다중검정과 선택 편향:** ANOVA 2개·Two-way·Tukey 각 쌍·보상 3종·시드·비용·블록길이·국면 구분을 모두 뒤져 나온 최소 *p*값을 결과로 고르지 않는다. 사전 핵심 PPO-vs-EW/MVO 비교 *p*값에는 Holm 등 추가 조정(단, 원 검정의 독립성 위반부터 해결), 탐색적 후속 분석에는 **실제로 살핀 후보들의 공동 성과차**를 이용한 White Reality Check 또는 Hansen SPA를 별도 민감도 분석으로 붙인다. 동일 테스트 창에서 정책·국면 정의를 바꾸면 그 창은 더 이상 미사용 OOS가 아니며, Reality Check/SPA도 **미기록 후보나 구조 변화까지** 수선하지는 못한다. [White (2000)](https://users.ssc.wisc.edu/~behansen/718/White2000.pdf), [Hansen (2005)](https://cdr.lib.unc.edu/downloads/zp38wf793?locale=en), [statsmodels `multipletests`](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html), [Harvey, Liu & Zhu (2016)](https://people.duke.edu/~charvey/Research/Published_Papers/P118_and_the_cross.PDF)

9. **도구·해석 구분:** `scipy.stats.f_oneway`는 One-way F/Welch, `statsmodels.stats.anova.anova_lm`는 적합 선형모형의 Two-way 표(`sum_sq`, `df`, F, *p*), `statsmodels.stats.multicomp.pairwise_tukeyhsd`는 Tukey 또는 Games–Howell을 제공한다. statsmodels `anova_lm(robust='hc3')`는 **이분산 보정**일 뿐 시계열·공통 날짜 상관의 만능 보정이 아니다. ANOVA를 구현하는 evaluation-xai는 `requirements.txt`에서 statsmodels 0.15.0, SciPy 1.18.1을 고정하므로 **SciPy `equal_var=False` 사용 가능 버전(≥1.16)** 조건을 충족한다(2026-10-30 확인). 효과크기표는 η²와 One-way ω² 외에 전략 간 **실제 Sharpe/MDD 차이의 크기**를 병기한다. [statsmodels `anova_lm`](https://www.statsmodels.org/stable/generated/statsmodels.stats.anova.anova_lm.html), [statsmodels `pairwise_tukeyhsd`](https://www.statsmodels.org/stable/generated/statsmodels.stats.multicomp.pairwise_tukeyhsd.html), [SciPy `f_oneway`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html), [Lakens (2013)](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2013.00863/full)

## 참고문헌

- Agarwal, R., Schwarzer, M., Castro, P. S., Courville, A. C. & Bellemare, M. G. (2021). “Deep Reinforcement Learning at the Edge of the Statistical Precipice.” *Advances in Neural Information Processing Systems 34*. [원문](https://proceedings.neurips.cc/paper_files/paper/2021/file/f514cec81cb148559cf475e7426eed5e-Paper.pdf).

- Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences*, 2nd ed. Lawrence Erlbaum Associates/Routledge. [출판사 서지](https://www.routledge.com/Statistical-Power-Analysis-for-the-Behavioral-Sciences/Cohen/p/book/9780805802832); [원문 본문 미확인: 0.01/0.06/0.14의 적용 범위는 아래 Lakens 원문에서 확인].

- Cont, R. (2001). “Empirical properties of asset returns: stylized facts and statistical issues.” *Quantitative Finance* 1: 223–236. [저자 제공 원문](http://rama.cont.perso.math.cnrs.fr/pdf/empirical.pdf).

- Diebold, F. X. & Mariano, R. S. (1995). “Comparing Predictive Accuracy.” *Journal of Business & Economic Statistics* 13(3): 253–263. [원문 DOI 서지](https://doi.org/10.1080/07350015.1995.10524599), [검정의 직접 확인 가능한 공식 구현 설명](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.diebold_mariano_test.html). [원문 PDF 텍스트 미확인: NBER 복사본 텍스트 추출 실패.]

- Hansen, P. R. (2005). “A Test for Superior Predictive Ability.” *Journal of Business & Economic Statistics* 23(4): 365–380. [학술기관 소장 원문](https://cdr.lib.unc.edu/downloads/zp38wf793?locale=en).

- Harvey, C. R., Liu, Y. & Zhu, H. (2016). “… and the Cross-Section of Expected Returns.” *The Review of Financial Studies* 29(1): 5–68. [저자 제공 원문](https://people.duke.edu/~charvey/Research/Published_Papers/P118_and_the_cross.PDF).

- Henderson, P., Islam, R., Bachman, P., Pineau, J., Precup, D. & Meger, D. (2018). “Deep Reinforcement Learning that Matters.” *Proceedings of the AAAI Conference on Artificial Intelligence* 32. [AAAI 원문](https://cdn.aaai.org/ojs/11694/11694-13-15222-1-2-20201228.pdf).

- Jobson, J. D. & Korkie, B. M. (1981). “Performance Hypothesis Testing with the Sharpe and Treynor Measures.” *The Journal of Finance* 36: 889–908. [DOI 서지](https://doi.org/10.1111/j.1540-6261.1981.tb04891.x). [원문 본문 미확인; 적용 가정의 1차 확인 자료는 Ledoit & Wolf (2008).]

- Lakens, D. (2013). “Calculating and reporting effect sizes to facilitate cumulative science: a practical primer for t-tests and ANOVAs.” *Frontiers in Psychology* 4: 863. [원문](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2013.00863/full).

- Ledoit, O. & Wolf, M. (2008). “Robust performance hypothesis testing with the Sharpe ratio.” *Journal of Empirical Finance* 15(5): 850–859. [저자 제공 원문](http://www.ledoit.net/jef_2008pdf.pdf).

- Lo, A. W. (2002). “The Statistics of Sharpe Ratios.” *Financial Analysts Journal* 58(4): 36–52. [학회 발행 원문 소개](https://rpc.cfainstitute.org/research/financial-analysts-journal/2002/the-statistics-of-sharpe-ratios). [원문 본문 미확인; 저자 초록 확인].

- Memmel, C. (2003). “Performance Hypothesis Testing with the Sharpe Ratio.” *Finance Letters* 1: 21–23. [저자 소속 기관 서지](https://www.bundesbank.de/en/christoph-memmel). [원문 본문 미확인; 교정 내용은 Ledoit & Wolf (2008)에서 확인].

- White, H. (2000). “A Reality Check for Data Snooping.” *Econometrica* 68(5): 1097–1126. [학술기관 소장 원문](https://users.ssc.wisc.edu/~behansen/718/White2000.pdf).

- SciPy 개발팀. *공식 API 문서*: [`f_oneway`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html), [`kruskal`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html), [`friedmanchisquare`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.friedmanchisquare.html), [`levene`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.levene.html), [`tukey_hsd`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.tukey_hsd.html) (열람된 v1.18.0 문서).

- statsmodels 개발팀. *공식 API 문서*: [`anova_lm`](https://www.statsmodels.org/stable/generated/statsmodels.stats.anova.anova_lm.html), [`AnovaRM`](https://www.statsmodels.org/stable/generated/statsmodels.stats.anova.AnovaRM.html), [`anova_oneway`](https://www.statsmodels.org/stable/generated/statsmodels.stats.oneway.anova_oneway.html), [`pairwise_tukeyhsd`](https://www.statsmodels.org/stable/generated/statsmodels.stats.multicomp.pairwise_tukeyhsd.html), [`diebold_mariano_test`](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.diebold_mariano_test.html), [`multipletests`](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html), [`acorr_ljungbox`](https://www.statsmodels.org/stable/generated/statsmodels.stats.diagnostic.acorr_ljungbox.html) (열람된 v0.15.0 문서).
