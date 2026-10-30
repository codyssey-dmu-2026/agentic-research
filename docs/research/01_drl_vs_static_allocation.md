# DRL 동적 자산배분은 1/N·MVO보다 나은가?

질문은 **국내 ETF의 미래 구간에서**, 거래비용을 제하고 위험조정 수익률을 높이면서 손실도 줄일 수 있는지이다.
표본 외(out-of-sample, OOS)는 학습·모델 선택에 사용하지 않은 뒤의 기간이다.
심층강화학습(deep reinforcement learning, DRL)은 신경망으로 관측한 상황에서 취할 행동을 배우는 방법이다.
PPO(Proximal Policy Optimization)는 정책 갱신법, SAC(Soft Actor-Critic)는 별개의 학습법이다.
[Schulman et al.](https://arxiv.org/abs/1707.06347) · [Lu](https://arxiv.org/pdf/2307.07694)
회전율(turnover)은 자산을 바꾸기 위해 거래한 정도, 확실성등가수익(certainty-equivalent return)은
위험을 고려한 투자 성과를 확실한 수익으로 환산한 지표다.
[DeMiguel et al.](https://www.london.edu/faculty-and-research/academic-research/o/optimal-versus-naive-diversification-how-inefficient-is-the-1n-portfolio-strategy-p7805)
위험조정 수익의 대표 지표인 샤프비율(Sharpe ratio)은 초과수익을 수익률 변동성으로 나눈 값이며,
최대낙폭(maximum drawdown, MDD)은 이전 최고 자산가치에서 이후 최저점까지의 최대 하락률이다.
[Jiang et al., §6](https://arxiv.org/html/1706.10059)

## 핵심 결론

- **일반적인 우월성은 입증되지 않았다.** 일곱 주식 데이터셋의 표본 외 성과를 합쳐 300년 이상 비교한 연구에서
  SAC 강화학습은 거래비용이 없을 때도 동일가중 1/N을 일관되게 이기지 못했고, 거래비용 0.1% 적용 시
  높은 회전율 때문에 순수익이 음수가 되었다. 이는 **SAC·주식 데이터**의 결과이지 PPO·국내 ETF 전체에
  대한 판정은 아니다. [Kruthof & Müller, 2025](https://portal.fis.tum.de/en/publications/can-deep-reinforcement-learning-beat-formula-presented/)
- **PPO와 MVO를 직접 비교한 긍정 사례는 있다.** 미국 S&P 500 업종지수의 2012~2021년
  10개 연간 표본 외 시험에서 PPO의 샤프비율은 1.17, MVO는 0.68이었다. 다만 일일 거래의
  거래비용은 0으로 가정했고 두 방법의 관측된 최대낙폭은 모두 약 33%여서, 비용 공제 후
  우위나 MDD 15% 준수를 입증하지 않는다.
  [Sood et al., §5–6·표 2](https://arxiv.org/html/2602.17098v1)
- **이길 수 있다는 실험 근거도 있다.** Jiang 등의 암호화폐 EIIE는 매수·매도 각각 0.25% 수수료를
  반영하고도 세 번의 약 50일 표본 외 실험에서 비교 전략보다 높은 샤프비율·최종자산을 보였다.
  그러나 세 실험의 CNN 최대낙폭은 22.4%, 21.6%, 40.6%로, 높은 수익이 15% 낙폭 제한을
  입증하지 않는다. [Jiang et al., 표 1·2](https://arxiv.org/html/1706.10059)
- **1/N은 꼭 넘어야 할 기준선이다.** 일곱 실증 데이터셋에서 14가지 추정·최적화 전략 중
  샤프비율·확실성등가수익·회전율 기준으로 1/N보다 *일관되게* 나은 전략이 없었다.
  MVO(평균·분산 최적화)는 과거 평균수익과 공분산을 추정해 비중을 고르므로 추정오차에 취약하다.
  [DeMiguel et al., 2009](https://www.london.edu/faculty-and-research/academic-research/o/optimal-versus-naive-diversification-how-inefficient-is-the-1n-portfolio-strategy-p7805) · [Michaud, 1989](https://rpc.cfainstitute.org/research/financial-analysts-journal/1989/the-markowitz-optimization-enigma-is-optimized-optimal)
- **동적·비용 반영 연구의 성과를 과대일반화하면 안 된다.** 미국 ETF의 딥러닝 직접 비중 최적화는
  2011~2020년 4월 OOS에서 고정 비중·MVO보다 높은 샤프비율을 보고했지만 **PPO나 DRL이 아니다**.
  선물 DRL 연구에서도 전체 계약 성과는 좋아도 주가지수군에서는 단순 롱온리가 더 나았다.
  [Zhang et al., *Portfolio Optimization*, §3–4](https://arxiv.org/pdf/2005.13665) · [Zhang et al., *Trading*, §4](https://arxiv.org/html/1911.10107)
- **유리한 백테스트와 확증은 다르다.** 여러 보상함수·시드·가중치 한도·재조정 주기를 시험해 최상 결과만
  고르면 선택 편향이 생긴다. 선택 횟수를 고려한 Deflated Sharpe Ratio와 전략 선택 과정의 과적합 확률(PBO)을
  별도 검토하고, 마지막 시간순 테스트는 선택에 다시 쓰지 않아야 한다.
  [Bailey & López de Prado, 2014](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf) · [Bailey et al., 2015 원고](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf)

## 근거

### 고정 배분의 기준선과 최적화의 추정오차

1. **DeMiguel, Garlappi & Uppal (2009), “Optimal Versus Naive Diversification”.**
   주장 → 최적화된 배분의 *표본 내* 이론적 우위가 표본 외 우위와 같지는 않다. 일곱 실증 데이터셋에
   14개 모형을 대조해 1/N을 샤프비율·확실성등가수익·회전율에서 일관되게 이긴 모형을 찾지 못했다.
   미국 주식시장 모수로 보정한 분석에서는 25개 자산에 약 3,000개월의 추정 표본이 필요하다고
   계산했으나, **그 수치는 국내 ETF 11개에 필요한 데이터 길이가 아니다**.
   자료의 개별 시작·종료연도와 실제 거래비용 공제 방식은 접근 가능한 저자 소속기관의 초록에 없어
   **[미확인]**; 회전율은 매매비용과 관련된 *대리 지표*이지 순수익이 아니다.
   [런던비즈니스스쿨의 저자 논문 초록](https://www.london.edu/faculty-and-research/academic-research/o/optimal-versus-naive-diversification-how-inefficient-is-the-1n-portfolio-strategy-p7805)

2. **Michaud (1989), “The Markowitz Optimization Enigma”.**
   주장 → 제약 없는 MVO가 예상수익·공분산 입력오차를 증폭해 동일가중보다 나쁠 수 있다.
   반대로 저자는 믿을 만한 사전 정보와 투자자 제약을 넣은 최적화의 가치는 인정한다.
   접근 가능한 발행기관 초록에는 실증 데이터·실험기간·거래비용 가정이 없어 모두 **[미확인]**;
   여기서 특정 초과수익률이나 승률을 도출하지 않는다.
   [CFA Institute 원문 초록](https://rpc.cfainstitute.org/research/financial-analysts-journal/1989/the-markowitz-optimization-enigma-is-optimized-optimal)

### 동적 배분: 긍정 사례, 직접 반증, 적용 범위

3. **Jiang, Xu & Liang (2017), “A Deep Reinforcement Learning Framework for the Financial Portfolio Management Problem”.**
   주장 → 시장정보·직전 비중으로 새 비중을 정하는 EIIE(CNN·RNN·LSTM)는 단순 보유·정기 동일가중
   리밸런싱 등보다 세 암호화폐 실험의 샤프비율과 최종 자산가치에서 앞섰다.
   Poloniex 30분봉, 훈련 자료는 실험별 2014~2017년, 표본 외 구간은 2016-09-07~10-28,
   2016-12-08~2017-01-28, 2017-03-07~04-27; 현금은 비트코인이며 매수·매도 수수료 각 0.25%를 반영한다.
   **그러나 MVO를 기준선으로 실험하지 않았고**, 가장 수익성 높은 CNN조차 세 구간 모두 MDD 15%를 넘는다.
   [§2.3, 표 1·2](https://arxiv.org/html/1706.10059)

4. **Zhang, Zohren & Roberts (2019), “Deep Reinforcement Learning for Trading”.**
   주장 → DRL이 국면에 따라 포지션을 조절할 가능성은 있지만, 본 논문은 **ETF 11개의 배분이 아닌
   개별 선물의 매수·매도·공매도 신호**를 학습한다. 상품·주가지수·채권·FX 50개 연속선물의 2005~2019년
   자료로 5년 간격 재학습, 2011~2019년 표본 외 테스트를 했고, 포지션 변화에 비례한 거래비용을
   수익에 차감했으며 25bp(베이시스포인트, 0.25%) 비용에서도 일부 RL 모델의 수익이 양수라고 보고했다.
   선물 수익을 동일 비중으로 합쳐 비교했으나 주가지수군에서는 롱온리 기준선이 RL보다 우세했다.
   [§3 보상식·§4 표 2와 비용 민감도](https://arxiv.org/html/1911.10107)

5. **Zhang, Zohren & Roberts (2020/2021), “Deep Learning for Portfolio Optimization”.**
   주장 → VTI·AGG·DBC·논문상 ‘VIX’로 표기한 미국 자산 네 종류의 2006~2020년 일별 자료에서,
   과거 가용 데이터로 2년마다 재학습한 LSTM의 2011~2020년 4월 테스트 샤프비율이 연간 재조정
   고정비중(25%씩 포함)·MVO보다 높았다. MVO는 과거 50일 평균·공분산으로 매일 갱신하며,
   순수익에는 거래대금 변화당 0.01% 기본 비용과 0.1% 민감도 비용을 각각 적용한다.
   **이 모델은 미분 가능한 샤프비율을 직접 최적화하는 딥러닝 구조이지 PPO/DRL이 아니다**;
   비용 0.1%에서는 고정 배분 일부가 근접하고 잦은 일별 거래의 비용 부담도 인정한다.
   [§2–4, 표 1](https://arxiv.org/pdf/2005.13665)

6. **Liu et al. (2020, arXiv v1), “FinRL: A Deep Reinforcement Learning Library for Automated Stock Trading in Quantitative Finance”.**
   주장 → 금융환경에서 PPO·DDPG·TD3 등을 재현 가능한 방식으로 구현하고, 거래비용·호가 스프레드를
   설정하며, 학습→검증→테스트와 동일가중·MVO·최소분산 기준선을 제공한다.
   시연의 DJIA 종목 배분/매매는 2019-01-01~2020-09-23 테스트에서 TD3·DDPG를 최소분산과
   비교하지만 **동일가중의 해당 시연 성과는 제시하지 않으며**, 시연 표에 실제 적용 비용 수치는
   **[미확인]**이다; 단순한 라이브러리 기능 목록을 DRL의 1/N 승리 증거로 읽으면 안 된다.
   [§3–4, 표 2](https://arxiv.org/html/2011.09607v1)

7. **Kruthof & Müller (2025), “Can deep reinforcement learning beat 1/N?”.**
   주장 → 앞선 긍정 결과에 대한 더 직접적인 반대 증거다. 일곱 주식 데이터셋의 **합산 300년 이상**
   표본 외 비교에서 SAC의 시장 타이밍 가능성에도 1/N 대비 일관된 비용 전 우위가 없었고,
   0.1% 거래비용 반영 시 높은 회전율로 순수익이 음수였으며 꼬리위험 지표도 일관된 우위를 보이지 않았다.
   개별 데이터셋의 달력상 시작·종료연도는 접근 가능한 대학 소속기관 초록에 없어 **[미확인]**;
   서로 다른 주식시장의 OOS 연수를 더한 것이지 단일 300년 시계열이 아니다.
   [TUM 저자 논문 기록 및 초록](https://portal.fis.tum.de/en/publications/can-deep-reinforcement-learning-beat-formula-presented/) · [저자 공개 요약](https://kruthof.github.io/publications/)

8. **Lu (2025, arXiv v3), “Evaluation of Deep Reinforcement Learning Algorithms for Portfolio Optimisation”.**
   주장 → *실제 자산의 OOS 성과가 아니라* 인공 시장에서 PPO의 학습 가능성과 데이터 요구량을 점검했다.
   VUG·VTV·GLD의 2018~2023년 가격에서 추정한 모수로 상관된 가격변동·매매 시장충격을 합성했고,
   PPO·A2C는 단순 환경에서 이론적 목표에 접근했지만 DDPG·TD3·SAC는 어려움을 겪었다.
   Bertsimas–Lo 시장충격으로 거래 부담을 모사하되 국내 ETF 고정 0.065% 비용을 사용하지 않았고,
   저자는 가장 단순한 과제도 200만 번 이상 단계가 필요하다고 지적한다(실제 OOS 기간 **해당 없음**).
   [§3·6 및 초록](https://arxiv.org/pdf/2307.07694)

9. **Moody & Saffell (2001), “Learning to Trade via Direct Reinforcement”.**
   주장 → 예측값을 먼저 만드는 대신 매매 정책을 직접 개선하고 거래비용을 반영해
   차등 샤프비율(differential Sharpe ratio: 한 거래가 누적 수익/위험 비율에 미치는 변화)을
   최적화할 수 있음을 보였다. 실제 금융자료에 대해 일중 외환 거래와 **S&P 500 지수·미국 단기국채
   (T-Bills) 월간 자산배분**을 다루지만, 공개된 발행기관 초록에는 각 실험의 날짜·비용률·
   동일가중/MVO와의 직접 승부가 없어 **[미확인]**이다; 현대 PPO의 ETF 우월성 근거는 아니다.
   [IEEE 논문 초록](https://ieeexplore.ieee.org/document/935097)

10. **Schulman et al. (2017), “Proximal Policy Optimization Algorithms”.**
    주장 → PPO는 새 환경 경험을 모은 뒤 잘린 정책 갱신 목적함수로 여러 미니배치 학습을 하는
    강화학습 방법이다. 원 실험은 Atari 게임·모의 로봇이며 금융 가격자료·투자기간·수수료가
    **해당 없음**; PPO를 선택할 구현상 근거일 뿐 수익률 증거가 아니다.
    [arXiv 원 논문](https://arxiv.org/abs/1707.06347)

11. **Sood, Papasotiriou, Vaiciulis & Balch (2023 워크숍; 2026 arXiv 공개), “Deep Reinforcement Learning for Optimal Portfolio Allocation: A Comparative Study with Mean-Variance Optimization”.**
    주장 → 미국 S&P 500 업종지수 11개의 2006~2021년 일별 가격에서 앞선 기간으로 학습하고
    2012~2021년 연간 OOS 10회(일일 리밸런싱)에 PPO를 시험했다. 과거 60일 자료로
    매일 갱신하는 MVO와 비교해 샤프비율 1.1662 대 0.6776으로 우세했지만,
    수수료·슬리피지는 반영하지 않았다. 표 2의 전체 시험 중 최대 MDD는
    PPO 32.96%, MVO 33.03%이며, 1/N 기준선·ETF 실거래·15% MDD 제한은
    시험하지 않았다. [§4.5, §5.1·5.4, §6 표 2](https://arxiv.org/html/2602.17098v1)

### 연구 품질과 백테스트 선택 오류

12. **Felizardo et al. (2022), “Reinforcement Learning Applied to Trading Systems: A Survey”.**
    주장 → 서로 다른 기간·시장·학습·평가 설정을 가진 논문의 성과를 그냥 합쳐 ‘RL이 우월하다’고
    말할 수 없다. 2014~2020년에 발표된 거래/자산배분 논문 29편을 분류했는데 검증 구간 사용의
    불일치, 기준선·시장·기간의 이질성, 거래비용 미반영 5편과 비용 수치 미기재 3편을 확인했다.
    이는 새 가격자료의 투자 백테스트가 아닌 **문헌 분석**이므로 자체 OOS 기간·직접 거래비용률은
    해당 없음이다. [§3–5](https://arxiv.org/pdf/2212.06064)

13. **Bailey, Borwein, López de Prado & Zhu (2015 원고/2016 온라인), “The Probability of Backtest Overfitting”.**
    주장 → PBO는 여러 설정 가운데 *훈련구간 최상위*로 뽑은 설정이 다른 구간에서 후보들의
    중앙값보다 못할 확률이다. 논문은 전략별 동일 시점 수익률을 여러 덩어리로 나누어 훈련/검증
    조합을 바꾸는 조합형 대칭 교차검증(combinatorially symmetric cross-validation, CSCV)을
    제안하고 모의 예제와 한 실제 전략 예제를 다룬다; 실제 전략의 개별
    시장·기간·비용률은 공개 원고에서 확인하기 어려워 **[미확인]**, 방법 자체에는 고정 비용률이 없다.
    [저자 원고 §1–3·5](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf) · [저널 게재 초록](https://www.risk.net/journal-of-computational-finance/2471206/the-probability-of-backtest-overfitting)

14. **Bailey & López de Prado (2014), “The Deflated Sharpe Ratio”.**
    주장 → DSR(조정 샤프의 통계적 유의확률)는 **여러 전략 중 최고를 고른 효과와 수익률의
    비정규성(정규분포와 다른 모양)**을 고려해 샤프비율의 신뢰도를 판단한다. 원고의 미국 국채 전략 예시는 *가상 사례*의
    일별 5년·약 1,250관측치이며 실거래 전략 OOS 결과가 아니고 수수료도 별도로 제시하지 않는다.
    따라서 DSR을 계산할 때는 선정된 한 모델뿐 아니라 시험한 전략 수·각 샤프비율의 퍼짐·
    최종 수익열의 왜도(비대칭)·첨도(꼬리의 두께)를 기록해야 한다.
    [저자 원고 §Multiple Testing–Numerical Example](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)

## 반대 증거와 한계

- **직접 반증:** 2025년의 대규모 주식 OOS 실험에서 SAC는 거래비용 전에도 1/N을 꾸준히 이기지
  못했으며 0.1% 비용에 순성과가 무너졌다. 연구 대상은 SAC와 주식이므로 이를 PPO·한국 ETF의
  확정적 실패라고 말할 수는 없다. [Kruthof & Müller](https://portal.fis.tum.de/en/publications/can-deep-reinforcement-learning-beat-formula-presented/)
- **직접 우위도 비용·낙폭 조건을 통과해야 한다:** 업종지수 PPO의 MVO 대비 샤프 우위는
  비용 0·일일 즉시 재배분의 실험이며, 관측 최대 MDD 32.96%는 목표인 15%를 넘는다.
  더 낮은 회전율이라는 관찰만으로 국내 ETF의 비용 공제 후 우위를 단정할 수 없다.
  [Sood et al., §4.5·§6·§7](https://arxiv.org/html/2602.17098v1)
- **수익과 낙폭은 별개:** EIIE의 높은 샤프와 최종자산 뒤에 21.6~48.7% 범위의 EIIE
  최대낙폭이 있었고, 최고 수익 모델의 세 낙폭도 모두 15%를 넘었다.
  그 논문으로 ‘DRL이면 15% MDD가 보장된다’고 주장할 수 없다.
  [Jiang et al., 표 2](https://arxiv.org/html/1706.10059)
- **비교 대상 차이:** 선물 개별 포지션 연구의 전체 50종 계약 평균 성과는 국내 11종 ETF 간
  비중 학습의 증거가 아니며, 그 연구에서도 주가지수군은 단순 롱온리가 낫다.
  ETF 딥러닝 샤프 최적화의 우위 역시 PPO/DRL에 귀속할 수 없다.
  [Zhang et al., *Trading* §4](https://arxiv.org/html/1911.10107) · [Zhang et al., *Portfolio Optimization* §3](https://arxiv.org/pdf/2005.13665)
- **데이터·시장 제약:** 2018~2025년의 일별 ETF 자료에서 4년 학습·1년 시험 3구간은 실험
  가능한 설계지만, 30분봉 암호화폐의 수백~수천 거래사례나 반복 생성 인공시장과 관측량·거래
  구조가 다르다. 인공시장 PPO 연구는 가장 단순한 설정에 200만 학습 단계 이상이 들었다고 보고한다.
  [Jiang et al., 표 1](https://arxiv.org/html/1706.10059) · [Lu, 2025](https://arxiv.org/pdf/2307.07694)
- **기준선도 공정해야 한다:** 동일가중 ‘매수 후 보유’와 ‘매달 1/N 복귀’는 다른 정책이며,
  MVO는 과거 창을 이동시키면 엄밀히 고정 비중이 아니다. Jiang은 두 동일가중형 기준선을
  별도 보고했고, Zhang은 연간 고정비중 재조정과 일일 MVO를 구분했다.
  [Jiang et al., §6.3](https://arxiv.org/html/1706.10059) · [Zhang et al., *Portfolio Optimization* §4.2](https://arxiv.org/pdf/2005.13665)
- **통계적 확증의 한계:** 보상함수 세 개, 여러 λ·시드·학습 에포크·비용·MDD 문턱을 뒤져
  최상의 전략을 고르면 한 번의 OOS도 ‘새 데이터’가 아니게 된다. PBO용 CSCV는 시간 덩어리의
  조합을 바꾸므로 3년의 진짜 미래형 워크포워드 테스트를 대체해서는 안 된다.
  [Bailey et al., §2·5](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf) · [Bailey & López de Prado, 2014](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)

## 우리 프로젝트에 대한 시사점

1. **판정문을 미리 정하기:** 기본 검증은 3개 연도 OOS를 시간 순서로 연결한 **비용 차감 후
   샤프비율: PPO > 월간 1/N과 월간 MVO**, 동시에 **실현 MDD ≤15%**인지이다.
   위험조정 성과·최대낙폭·연도별 결과를 각각 보여주고 ‘둘 중 하나만 이김’을 성공이라 하지 않는다.
   정적 기준선의 어려움과 MDD/샤프의 차이는
   [DeMiguel et al.](https://www.london.edu/faculty-and-research/academic-research/o/optimal-versus-naive-diversification-how-inefficient-is-the-1n-portfolio-strategy-p7805)과 [Jiang et al. 표 2](https://arxiv.org/html/1706.10059)에서 확인된다.
2. **완전히 같은 거래 환경:** 같은 ETF 11종·거래일·비중 한도 0~40%·현금 허용 규칙·가격 시점·
   수수료/슬리피지·포트폴리오 초기 금액을 1/N/MVO/PPO에 적용한다. 월간 1/N 재조정과
   1/N 매수 후 보유는 구분해 보고, MVO는 동일한 재조정일에 *그 전 252거래일*의 통계만 사용한다.
   모든 매매의 한 방향 거래대금에 프로젝트 가정인 0.015% 수수료+0.05% 슬리피지=0.065%를
   공통 차감하고 비용 전·후와 회전율을 함께 보고한다.
   [Zhang et al., *Portfolio Optimization* §4](https://arxiv.org/pdf/2005.13665) · [Kruthof & Müller](https://portal.fis.tum.de/en/publications/can-deep-reinforcement-learning-beat-formula-presented/)
3. **비용·재조정 빈도에 대한 반증 실험:** 기본 비용 0.065%와 0% 및 더 높은 비용,
   PPO의 일일/월간 행동 제한을 사전에 정해 성과와 매매량을 비교한다. 가격은 의사결정 시점에
   알 수 있었던 정보만 사용하고 주문은 그 *다음* 체결 가능 시점에 반영한다.
   작은 비용에도 순성과 역전이 가능한지는
   [Kruthof & Müller](https://portal.fis.tum.de/en/publications/can-deep-reinforcement-learning-beat-formula-presented/)와 [Zhang et al. 비용 민감도](https://arxiv.org/pdf/2005.13665)가 보여준다.
4. **보상과 15% 차단 장치를 분리 검증:** 수익·변동성 보정·MDD 벌점 세 보상을 같은 예산/시드로
   비교하되, 학습 중 보상 개선과 **사후 전체 경로의 실현 MDD**를 혼동하지 않는다.
   MDD 15%에서 에피소드를 종료하는 백테스트는 종료 뒤의 운용 성적을 가리지 말고,
   종료 시점·청산비용·이후 현금/단기채 가치도 끝까지 기록한다. 원 연구에서도 높은 수익과
   높은 MDD가 동반되었다. [Jiang et al., 표 2](https://arxiv.org/html/1706.10059)
5. **시간 순서·재현성:** 각 4년 학습 구간 내부에서만 검증 구간을 떼어 파라미터·보상 계수·
   중단 시점·시드를 고르고, 해당 1년 OOS로는 **재선택하지 않는다**.
   보상 3종만이 아니라 실제로 돌린 모든 후보/시드를 실험대장에 기록해 DSR/PBO의 선택 횟수
   입력으로 남긴다. 논문 간 검증 관행이 제각각이었던 문제와 다중 시도 편향은
   [Felizardo et al.](https://arxiv.org/pdf/2212.06064) · [Bailey & López de Prado](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf) · [Bailey et al.](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf)에서 다룬다.
6. **설명은 수익의 별도 성과 조건:** 매 결정에 ‘그날 이용 가능한 상태변수 → 비중 변화 →
   예상/실현 비용 → 실제 사후 손익·낙폭’을 기록한다. 설명의 그럴듯함만으로 초과수익이나
   위험제한의 증거로 대체하지 않는다; 직접 비중을 산출하는 모델의 연구 성과도 투입 특성
   민감도 분석과 별도 거래성과로 평가했다.
   [Zhang et al., *Portfolio Optimization* §4](https://arxiv.org/pdf/2005.13665)

## 참고문헌

- Bailey, D. H., Borwein, J. M., López de Prado, M., & Zhu, Q. J. (2016 온라인; 2017 권호). “The Probability of Backtest Overfitting.” *The Journal of Computational Finance*, 20(4). [저자 원고(2015)](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf) · [게재 초록](https://www.risk.net/journal-of-computational-finance/2471206/the-probability-of-backtest-overfitting).
- Bailey, D. H., & López de Prado, M. (2014). “The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality.” *The Journal of Portfolio Management*, 40(5), 94–107. [저자 원고](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf).
- DeMiguel, V., Garlappi, L., & Uppal, R. (2009). “Optimal Versus Naive Diversification: How Inefficient is the 1/N Portfolio Strategy?” *The Review of Financial Studies*, 22(5), 1915–1953. [저자 소속기관 원문 초록](https://www.london.edu/faculty-and-research/academic-research/o/optimal-versus-naive-diversification-how-inefficient-is-the-1n-portfolio-strategy-p7805).
- Felizardo, L. K., Paiva, F. C. L., Costa, A. H. R., & Del-Moral-Hernandez, E. (2022). “Reinforcement Learning Applied to Trading Systems: A Survey.” *arXiv:2212.06064*. [원고](https://arxiv.org/pdf/2212.06064).
- Jiang, Z., Xu, D., & Liang, J. (2017). “A Deep Reinforcement Learning Framework for the Financial Portfolio Management Problem.” *arXiv:1706.10059v2*. [원고](https://arxiv.org/html/1706.10059).
- Kruthof, G., & Müller, S. (2025). “Can deep reinforcement learning beat 1/N?” *Finance Research Letters*, 75, 106866. [저자 소속기관 논문 기록](https://portal.fis.tum.de/en/publications/can-deep-reinforcement-learning-beat-formula-presented/).
- Liu, X.-Y., Yang, H., Chen, Q., Zhang, R., Yang, L., Xiao, B., & Wang, C. D. (2020, v1). “FinRL: A Deep Reinforcement Learning Library for Automated Stock Trading in Quantitative Finance.” *arXiv:2011.09607v1*. [원고](https://arxiv.org/html/2011.09607v1).
- Lu, C. I. (2025, v3). “Evaluation of Deep Reinforcement Learning Algorithms for Portfolio Optimisation.” *arXiv:2307.07694v3*. [원고](https://arxiv.org/pdf/2307.07694).
- Michaud, R. O. (1989). “The Markowitz Optimization Enigma: Is ‘Optimized’ Optimal?” *Financial Analysts Journal*, 45(1), 31–42. [발행기관 논문 초록](https://rpc.cfainstitute.org/research/financial-analysts-journal/1989/the-markowitz-optimization-enigma-is-optimized-optimal).
- Moody, J., & Saffell, M. (2001). “Learning to Trade via Direct Reinforcement.” *IEEE Transactions on Neural Networks*, 12(4), 875–889. [발행기관 논문 초록](https://ieeexplore.ieee.org/document/935097).
- Schulman, J., Wolski, F., Dhariwal, P., Radford, A., & Klimov, O. (2017). “Proximal Policy Optimization Algorithms.” *arXiv:1707.06347*. [원고](https://arxiv.org/abs/1707.06347).
- Sood, S., Papasotiriou, K., Vaiciulis, M., & Balch, T. (2023 워크숍 발표; 2026 arXiv 공개). “Deep Reinforcement Learning for Optimal Portfolio Allocation: A Comparative Study with Mean-Variance Optimization.” *FinPlan’23 Workshop at ICAPS 2023*, arXiv:2602.17098v1. [원고](https://arxiv.org/html/2602.17098v1).
- Zhang, Z., Zohren, S., & Roberts, S. (2019). “Deep Reinforcement Learning for Trading.” *arXiv:1911.10107*. [원고](https://arxiv.org/html/1911.10107).
- Zhang, Z., Zohren, S., & Roberts, S. (2020 원고; 2021 v3). “Deep Learning for Portfolio Optimization.” *arXiv:2005.13665v3*. [원고](https://arxiv.org/pdf/2005.13665).
