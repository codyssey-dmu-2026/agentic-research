# 한국 개인투자자의 자산배분 문제와 로보어드바이저의 실제 효과

## 핵심 결론

- **문제는 투자상품 부족만이 아니라 사용 방식이다.** 2020년 3~10월 국내 개인 약 20만 명의 거래자료에서 잦은 매매, 수익 종목의 조기 매도, 투기적 종목 선호가 저조한 성과와 연결되었다. 이는 자동화의 비교 대상이 ‘아무것도 하지 않는 투자자’만은 아니라는 배경 근거다. 다만 관찰된 것은 주식 직접투자자의 행동이지 PPO 자산배분 전략의 효과가 아니다. [김민기·김준석, 2022](https://www.kcmi.re.kr/report/report_view?report_no=1481)
- **해외자산 접근성과 분산투자 실천은 다르다.** 국내 투자자의 모국편향은 2018년 집계에서 컸지만, 2020~2022년 계좌자료에서는 해외투자가 일부 투자자의 위험조정 성과를 개선하기도 했다. 동시에 특정 미국 종목·고위험 ETP 집중도 관찰되어 ‘국내 대 해외’의 이분법보다 실제 기초자산 노출을 볼 필요가 있다. [김한수, 2020](https://www.kcmi.re.kr/report/report_view?report_no=1194) · [강소현·김민기, 2026](https://www.kcmi.re.kr/report/report_view?report_no=2254)
- **자동 조언의 효과는 조건부다.** 인도 증권사 계좌를 조사한 D’Acunto 외(2019)는 기존 보유종목이 적은 투자자의 분산·성과 개선과 행동 편향 감소를 보고했지만, 이미 분산한 투자자는 거래비용이 늘고 평균 성과 개선은 없었다. 더 엄격한 비교에서는 변동성 감소의 통계적 근거도 뚜렷하지 않았다. [원문 공개본](https://www.fdic.gov/promises-and-pitfalls-robo-advising.pdf)
- **국내 시장의 성장·심사통과는 수익률 우위의 증거가 아니다.** 2025년 12월 말 코스콤 집계의 테스트베드 통과 업체 고객은 374,853명, 가입금액은 11,742억 원이다. 심사 목적은 최소 운용·보안 요건 확인이며 수익률은 심사 대상이 아니고 자문 품질도 보장하지 않는다. [코스콤 2025년 12월 공시](https://www.ratestbed.kr/portal/bbs/B0000006/view.do?nttId=34709&menuNo=200241) · [유의사항](https://www.ratestbed.kr/portal/main/contents.do?menuNo=200223)
- **국내 상장 ETF는 실행 가능한 실험 도구이지만 ETF를 산다는 것 자체로 성과가 좋아지지 않는다.** 코스콤 ETF CHECK의 2025년 12월 말 ETF 순자산총액은 297조 1,401억 원이다. 그러나 2020년 국내 개인 ETF 계좌자료에서는 특히 인버스 ETF 보유·거래가 수익률과 샤프비율 저하와 관련되었다. [코스콤 ETF CHECK](https://www.koscom.co.kr/portal/bbs/B0000066/view.do?nttId=30496&menuNo=200562) · [김준석·김민기, 2024](https://www.kcmi.re.kr/report/report_view?report_no=1776)

## 근거

**먼저 읽을 개념.** *자산배분*은 여러 자산군에 투자금의 비율을 정하는 일, *위험조정 수익률*은 수익과 그 과정의 위험을 함께 보는 성과다. *샤프비율(Sharpe ratio)*은 무위험 수익을 뺀 수익을 변동성으로 나눈 값이다. *최대낙폭(MDD, maximum drawdown)*은 관찰 기간 중 직전 최고 평가액부터 이후 최저 평가액까지의 최대 하락률이다. 코스콤은 샤프지수와 최대손실률을 함께 공시하며 같은 측정기간·전략의 비교가 중요하다고 명시한다. [코스콤 공시의 용어설명](https://www.ratestbed.kr/portal/pblntf/listProgrsInfo2.do?menuNo=200238)

### 1. 개인투자자에게 무엇이 어려운가

- **과잉매매 → 거래비용을 제하고 나면 성과가 악화된다.** Barber와 Odean(2000)은 미국 할인증권사 가계 66,465곳의 1991~1996년 주식 계좌를 조사했다. 거래 최상위 그룹의 연평균 순수익률은 11.4%, 동기간 시장은 17.9%였으며, 평균 가계 포트폴리오의 연간 회전율은 75%를 넘었다. *회전율*은 일정 기간 포트폴리오가 매매로 교체된 정도다. 연구는 과잉확신을 가능한 설명으로 제시하지, 모든 거래의 심리적 원인을 실험으로 입증한 것은 아니다. [원 논문](https://faculty.haas.berkeley.edu/odean/papers/returns/individual_investor_performance_final.pdf)

- **처분효과(disposition effect) → 손실을 확정하기 꺼리고 이익은 빨리 실현한다.** Odean(1998)은 미국 할인증권사 10,000개 계좌의 1987~1993년 거래를 조사했다. 전체 연도에 걸친 이익 실현 비율(PGR) 0.148은 손실 실현 비율(PLR) 0.098보다 컸다. 다만 미국의 12월에는 절세 목적의 손실 매도가 강해졌으므로, 동일 패턴을 모든 세제·시점에 그대로 대입하면 안 된다. [원 논문](https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/areinvestorsreluctant.pdf)

- **한국의 과잉매매·처분효과 → 국내 표본에서도 발견된다.** 김민기·김준석(2022)은 국내 대형 증권사 4곳의 개인 204,004명 자료를 사용했다. 증권사 3곳은 2020년 3~10월, 나머지 1곳은 3~6월의 일별 주식 거래다. 매수가격보다 오른 주식을 팔 확률은 내린 주식을 팔 확률의 2배 이상이었고, 잦은 거래 유형에서는 매수 후 성과가 매도 후 성과보다 낮았다. 복권형 주식 선호와 군집거래도 관찰됐다. [원 보고서](https://www.kcmi.re.kr/report/report_view?report_no=1481)

- **모국편향(home bias) → 세계시장 비중에 비해 자국 시장에 쏠리는 현상.** French와 Poterba(1991)는 미국·일본·영국 투자자의 국제 주식 보유액을 추정했고 당시 자국주식 비중이 각각 94%·98% 초과·82%라고 보고했다. 이는 역사적인 국가 전체 집계이지 2020년대 한국 개인계좌 통계는 아니다. [NBER 원 논문](https://www.nber.org/papers/w3609)

- **국내 모국편향과 새로운 해외 집중이 공존한다.** 김한수(2020)는 한국은행·IMF·예탁결제원 등의 투자주체별 주식 보유 집계를 통해, 2018년 국내 투자자 전체의 해외주식 비중 약 21%와 정규화된 모국편향 지표 0.79를 제시했다. 여기의 ‘개인·기타’에는 개인 외 증권사 거래도 섞여 있으므로 이 숫자를 순수 개인 계좌 수치로 쓰면 안 된다. [원 보고서](https://www.kcmi.re.kr/report/report_view?report_no=1194)

- **해외 분산의 실제 효과 → 개선 사례와 실패 사례 모두 있다.** 강소현·김민기(2026)는 국내 대형 증권사의 2020~2022년 개인 102,380명 계좌에서 국내·해외 상장 주식·ETP 보유와 거래를 분석했다. 해외 참여자 다수는 수익률·위험조정 성과가 개선됐지만 그중 약 절반은 여전히 만족스럽지 않은 성과였고, 소액투자자의 고배율 ETP 빈번 매매와 미국 특정 상품 편중도 나타났다. 따라서 ‘해외 ETF 보유 = 충분한 국가·자산군 분산’이 아니다. [원 보고서](https://www.kcmi.re.kr/report/report_view?report_no=2254)

### 2. 자동 자문은 투자자 행동을 바꿨는가

- **효과가 난 경우 → 원래 분산이 부족한 고객.** D’Acunto·Prabhala·Rossi(2019)는 인도 증권사가 2015년 7월 도입한 주식 포트폴리오 최적화 도구와 2015~2017년 거래·접속 자료를 분석했다. 이 도구는 과거 자료와 평균-분산 최적화(MVO, 수익과 변동성을 고려해 비중을 고르는 방법)로 비중을 제안하고 일괄 주문 버튼을 제공했다. 사전 보유 5종목 미만 고객에게는 보유종목 증가와 성과 개선이 관찰됐다. **이 연구의 도구는 개별주식 MVO이지 ETF PPO나 국면전환 전략이 아니다.** [저자 공개 원문](https://www.fdic.gov/promises-and-pitfalls-robo-advising.pdf)

- **편향 감소는 부분적이다.** 같은 연구에서 이용 전후 처분효과·과거 상승 추종·보유종목 수익률 순위에 따른 매도 편향은 완화되었으나 없어지지 않았다. 처분효과 지표의 이용 전후 단순 비교에서는 PGR−PLR 격차가 약 30% 감소했다. 연구는 실제 접촉에 성공한 고객과 같은 날 연락을 받지 않은 고객을 비교하는 차분의 차분 분석도 수행했다. [저자 공개 원문](https://www.fdic.gov/promises-and-pitfalls-robo-advising.pdf)

- **설명 제공만으로 실행되지는 않는다.** Bhattacharya 외(2012)는 독일 대형 증권사의 적극적 개인 고객 약 8,000명에게 편향되지 않은 자문을 무작위로 제안한 현장연구를 했다. 실제 자문을 받은 사람은 약 5%이고 조언을 받은 사람도 거의 따르지 않아 포트폴리오 효율성 개선이 작았다. 이는 사람이 제공한 투자자문에 관한 연구이며 SHAP 설명의 효능을 직접 검증한 결과는 아니다. [저자 소속대학의 원 논문 초록](https://researchportal.hkust.edu.hk/en/publications/is-unbiased-financial-advice-to-retail-investors-sufficient-answe/)

### 3. 한국의 실제 로보어드바이저와 ETF 시장

- **규제의 목적 → 소비자 보호와 안전성, 초과수익 인증은 아님.** 금융위원회의 2016년 테스트베드 운영방안은 투자자 성향별 포트폴리오, 실제 자금 운용, 시스템 안정·보안 심사를 설명했다. 2019년에는 로보어드바이저 업체에 펀드·일임재산 운용 위탁을 허용하고 개인 개발자의 테스트베드 참가 경로를 마련했다. [금융위 2016](https://www.fsc.go.kr/po010101/72307) · [금융위 2019](https://www.fsc.go.kr/no010101/73686)

- **제도 확대 → 실제 서비스 적용 범위가 늘었다.** 금융위원회는 2023년 테스트베드 공시 수익률을 일정 요건하에 광고에 사용하도록 하고 비대면 일임계약의 사전공시 기간을 1년 6개월에서 1년으로 줄였다. 2025년 3월에는 테스트베드 통과 알고리즘을 이용한 개인형퇴직연금(IRP) 일임서비스의 순차 출시를 발표했다. 이는 제도·출시 사실이지 투자자 수익률 향상 관찰이 아니다. [금융위 2023](https://www.fsc.go.kr/no010101/80133) · [금융위 2025](https://www.fsc.go.kr/no010101/84247)

- **시장규모 → 집계 범위와 시점을 구분한다.** 코스콤의 *2025년 12월 말 기준*, 테스트베드 통과 업체 고객수는 전체 374,853명·퇴직연금 12,121명, 가입금액은 전체 11,742억 원·퇴직연금 436.6억 원이다. *2026년 9월 말 기준* 전체 219,337명·6,413억 원, 퇴직연금 19,629명·828억 원이다. 이는 코스콤의 **테스트베드 통과 회사만** 조사한 고객·가입금액으로 국내 전체 로보업계 운용자산(AUM)이 아니다. 코스콤은 2026년 4월 대비 감소에 무료추천 서비스를 중단한 알고리즘이 영향을 주었다고 적어, 이를 곧바로 고객 투자손실로 읽으면 안 된다. [2025년 12월 공시](https://www.ratestbed.kr/portal/bbs/B0000006/view.do?nttId=34709&menuNo=200241) · [2026년 9월 공시](https://www.ratestbed.kr/portal/bbs/B0000006/view.do?nttId=38805&menuNo=200241)

- **수익률 공시 → 있는 수치와 비교 불가능한 수치를 구분한다.** 코스콤 대시보드의 *2026년 10월 12일 기준* 공개 화면은 구성 포트폴리오 1,081개의 ‘운용실적 전 체’ 연환산 7.20%, 최근 3개월 −5.47%를 표시했다. 그 화면은 동일 기간·동일 위험 수준의 수동 ETF 전략, 거래비용·보수 조정 조건 또는 개인별 실제 수익률 비교를 제공하지 않는다. 코스콤 자신도 공시는 자문 품질 보증이나 미래 실적 예측이 아니라고 경고한다. [대시보드](https://www.ratestbed.kr/portal/pblntf/boardA.do?menuNo=200242) · [운용정보 유의사항](https://www.ratestbed.kr/portal/pblntf/listProgrsInfo2.do?menuNo=200238)

- **ETF 실물 시장 → 국내 상장만으로 여러 자산군에 접근할 수 있다.** 코스콤 ETF CHECK의 *2025년 12월 말 기준* 국내 ETF 순자산총액은 297조 1,401억 원이며, 그중 주식형 190조 1,880억 원, 채권형 40조 4,282억 원, 단기자금형 48조 4,346억 원이다. 크기가 크다는 것은 접근 가능한 상장상품이 있다는 근거이지, 모든 ETF의 호가·유동성이 충분하다는 보장은 아니다. [코스콤 ETF CHECK 원 통계](https://www.koscom.co.kr/portal/bbs/B0000066/view.do?nttId=30496&menuNo=200562)

- **ETF 이용 실태 → 장기 분산투자와 단기 투기는 구분된다.** 김준석·김민기(2024)는 국내 대형 증권사 3곳의 투자자 136,426명, *2020년 1월 2일~10월 28일* 보유·거래를 연구했다. ETF 이용자는 약 16.8%; 당시 개인 ETF 거래대금의 60~70%는 레버리지·인버스 상품에서 발생했고, 인버스 ETF 비중·회전율 증가가 수익률과 샤프비율 하락에 연관된 반면 다른 ETF 유형의 보유 비중은 샤프비율 개선과 연관되었다. [원 보고서](https://www.kcmi.re.kr/report/report_view?report_no=1776)

## 반대 증거와 한계

- **로보어드바이저가 일률적으로 변동성을 낮춘다는 주장은 성립하지 않는다.** D’Acunto 외의 이용자 전후 비교에서는 시장조정 포트폴리오 변동성이 연율 약 2.07%포인트 감소했지만, 연락 성공/미성공 고객을 비교한 차분의 차분 표본에서는 그 감소가 통계적으로 유의하지 않았다. 또 사전 10종목 초과 보유자는 더 거래하고도 평균 성과 개선이 없었다. [원문 6·7장](https://www.fdic.gov/promises-and-pitfalls-robo-advising.pdf)

- **상품의 ‘분산 가능성’은 사용자의 실제 분산을 보장하지 않는다.** 국내 개인 ETF 연구는 관찰기간 전체 포트폴리오에서 ETF 보유·거래를 제거하면 월간 수익률과 샤프비율이 *상승*했다고 보고한다. 주로 인버스 ETF 영향이고, 2020년 한 시기의 관찰자료이므로 이를 ‘모든 ETF가 해롭다’는 인과적 결론으로 바꾸면 안 된다. 독일 계좌자료에서도 ETF 사용만으로는 거래비용 전 성과 개선이 없고 매수·매도 시점 및 ETF 선택의 문제가 제시되었다. [국내 원 보고서](https://www.kcmi.re.kr/report/report_view?report_no=1776) · [Bhattacharya 외(2017) 저자 소속대학 원 논문 초록](https://researchportal.hkust.edu.hk/en/publications/abusing-etfs/)

- **모국편향만을 전제로 설계하면 최신 행태를 놓친다.** 2018년 전체 투자자 보유액에 관한 국내 모국편향 연구와 2020~2022년 개인계좌의 해외 편중 연구는 표본과 시점이 다르다. 후자는 국내상장 해외지수 ETP를 보유한 사람을 분석상 ‘해외시장 투자자’로 분류하지 않기도 한다. 따라서 거래소 소재지만으로 해외노출을 계산하거나 2018년 집계의 0.79를 현 개인의 편향 정도라고 주장할 수 없다. [김한수, 2020](https://www.kcmi.re.kr/report/report_view?report_no=1194) · [강소현·김민기, 2026](https://www.kcmi.re.kr/report/report_view?report_no=2254)

- **국내 테스트베드 수익률은 ‘우리 PPO가 동일가중·MVO보다 낫다’는 직접 실증이 아니다.** 테스트베드의 통과 요건은 기본 자문·일임 가능성 검증이고, 운용성과 공시는 투자자를 위한 비교정보다. 대시보드의 포트폴리오 가입 시점·투자성향·비용·위험 수준이 프로젝트의 11개 ETF 및 동일한 2018~2025 구간과 일치하지 않으므로 나란히 놓고 승패를 판정할 수 없다. [심사 유의사항](https://www.ratestbed.kr/portal/main/contents.do?menuNo=200223) · [대시보드](https://www.ratestbed.kr/portal/pblntf/boardA.do?menuNo=200242)

- **연구대상과 목표변수가 다르다.** Barber·Odean의 미국 계좌는 개별주식과 오래된 수수료 체계, D’Acunto 외의 인도 도구는 MVO 주식 일괄매매, 국내 계좌연구는 주로 2020년 또는 2020~2022년이다. 이들 연구는 한국 상장 ETF 11개의 2018~2025년 PPO 전략이 MDD 15% 이내에서 동일가중/MVO보다 높은 위험조정 성과를 낸다는 증거도, SHAP 설명이 인간의 편향을 줄인다는 증거도 아니다. [Barber·Odean, 2000](https://faculty.haas.berkeley.edu/odean/papers/returns/individual_investor_performance_final.pdf) · [D’Acunto 외, 2019](https://www.fdic.gov/promises-and-pitfalls-robo-advising.pdf) · [김준석·김민기, 2024](https://www.kcmi.re.kr/report/report_view?report_no=1776)

## 우리 프로젝트에 대한 시사점

1. **문제 정의를 분리한다.** ‘개인이 집중·과잉거래하기 쉽다’는 관찰, ‘ETF로 저비용 분산이 가능하다’는 상품 특성, ‘PPO가 단순 전략보다 낫다’는 미검증 가설을 각각 구분해 쓴다. 위 세 문장은 서로를 자동으로 입증하지 않는다. [김민기·김준석, 2022](https://www.kcmi.re.kr/report/report_view?report_no=1481) · [김준석·김민기, 2024](https://www.kcmi.re.kr/report/report_view?report_no=1776)

2. **투자자 위험성향을 먼저 정한다.** 코스콤이 ‘안정추구·위험중립·적극투자’ 포트폴리오를 구분하듯, 팀의 MDD 15% 목표가 누구의 감내 수준을 나타내는지와 적합하지 않은 투자자를 명시한다. 모든 개인에게 한 전략이 더 낫다는 표현은 피한다. [코스콤 공시기준](https://www.ratestbed.kr/portal/main/contents.do?menuNo=200239) · [투자자 유의사항](https://www.ratestbed.kr/portal/main/contents.do?menuNo=200223)

3. **기초자산 노출을 확인한다.** 국내 상장 여부가 아니라 한국주식·미국주식·기타 국가·국고채·금·원유·현금성 자산별 비중을 따로 계산한다. 나스닥100과 S&P500 등의 중복 주식노출도 보여준다. 해외에 투자했다는 이유만으로 실제 분산을 얻었다고 가정하지 않는다. [강소현·김민기, 2026](https://www.kcmi.re.kr/report/report_view?report_no=2254) · [김준석·김민기, 2024](https://www.kcmi.re.kr/report/report_view?report_no=1776)

4. **2018~2025의 실제 투자 가능성을 복원한다.** ETF 11개의 상장·상장폐지 날짜와 매일 이용 가능한 가격·거래량을 확인한 뒤, 해당 날짜에 없는 종목은 미래에 존재할 것을 아는 상태로 이전 구간에 넣지 않는다. 가격과 순자산가치(NAV, ETF 보유자산 순가치)의 차이인 괴리율을 확인하고, 저유동성 ETF의 슬리피지를 기본 0.05%보다 높게 둔 민감도 분석도 보여준다. [한국거래소 NAV·괴리율 설명](https://open.krx.co.kr/contents/OPN/01/01030203/OPN01030203T1.jsp)

5. **동일 위험·동일 비용으로 비교한다.** 동일가중·월간 MVO·PPO에 같은 ETF 투자 가능 기간, 주문 시점, 비용과 제약을 적용한다. 기존 0.015% 수수료+0.05% 슬리피지를 각 *실제 매매 대금*에 적용하고 총수익 및 비용 차감 수익, 회전율, 위험조정 수익률과 MDD를 나란히 발표한다. ‘거래를 많이 해도 수익은 늘지 않는’ 사례가 비교의 핵심 반증이다. [Barber·Odean, 2000](https://faculty.haas.berkeley.edu/odean/papers/returns/individual_investor_performance_final.pdf) · [D’Acunto 외, 2019](https://www.fdic.gov/promises-and-pitfalls-robo-advising.pdf)

6. **시장 국면과 기본 포트폴리오의 차이를 함께 본다.** 3개 Walk-Forward 테스트 연도별로 ‘평소 정기 리밸런싱만 하는 ETF 배분’ 대비 PPO의 추가 성과·거래횟수·MDD를 공개한다. KOSPI는 참고 시장지표로 남기되 글로벌 주식·국고채·금·원유가 섞인 전략의 단독 성과판정 기준으로 쓰지 않는다. [코스콤의 동일 기간·전략 비교 주의](https://www.ratestbed.kr/portal/pblntf/listProgrsInfo2.do?menuNo=200238) · [김한수, 2020](https://www.kcmi.re.kr/report/report_view?report_no=1194)

7. **조기종료 규칙의 표현을 엄밀히 한다.** ‘MDD 15% 이하 보장’ 대신 ‘과거 상태에서 MDD가 15%를 넘으면 학습 에피소드를 종료하는 규칙’이라고 적고, 별도 테스트에서 *실제* MDD 위반 횟수와 위반폭을 집계한다. 종료·현금화는 이미 일어난 하락을 되돌리지 못한다. [코스콤의 최대손실률 정의](https://www.ratestbed.kr/portal/pblntf/listProgrsInfo2.do?menuNo=200238)

8. **설명가능성과 권고 준수는 따로 검증한다.** SHAP 그림을 제시하더라도 ‘왜 이런 비중인가’를 기초자산 노출, 기대 위험, 최근 리밸런싱, 투자자 성향으로 번역하고, 초보자가 설명을 이해·수용할지 별도 질문으로 다룬다. 무작위 자문 제안 실험에서 약 5%만 조언을 받고 그마저 거의 따르지 않았다는 결과는 ‘설명을 제공하면 행동이 개선된다’는 주장을 경계하게 한다. [Bhattacharya 외, 2012](https://researchportal.hkust.edu.hk/en/publications/is-unbiased-financial-advice-to-retail-investors-sufficient-answe/) · [코스콤 투자자 유의사항](https://www.ratestbed.kr/portal/main/contents.do?menuNo=200223)

## 참고문헌

- Barber, Brad M. & Terrance Odean (2000). “Trading Is Hazardous to Your Wealth: The Common Stock Investment Performance of Individual Investors.” *The Journal of Finance* 55(2), 773–806. [저자 공개 원문](https://faculty.haas.berkeley.edu/odean/papers/returns/individual_investor_performance_final.pdf).
- Odean, Terrance (1998). “Are Investors Reluctant to Realize Their Losses?” *The Journal of Finance* 53(5), 1775–1798. [저자 공개 원문](https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/areinvestorsreluctant.pdf).
- French, Kenneth R. & James M. Poterba (1991). “Investor Diversification and International Equity Markets.” *American Economic Review* 81(2), 222–226; [NBER Working Paper 3609 원문·초록](https://www.nber.org/papers/w3609).
- 김민기·김준석 (2022). 『국내 개인투자자의 행태적 편의와 거래행태』. 자본시장연구원 연구보고서 22-02. [원문](https://www.kcmi.re.kr/report/report_view?report_no=1481).
- 김한수 (2020). 『국내투자자의 지역별 해외주식투자 현황 및 특성 분석』. 자본시장연구원 이슈보고서 20-02. [원문](https://www.kcmi.re.kr/report/report_view?report_no=1194).
- 강소현·김민기 (2026). 『개인투자자의 해외투자 특징 및 성과 분석』. 자본시장연구원 연구보고서 26-04. [원문](https://www.kcmi.re.kr/report/report_view?report_no=2254).
- 김준석·김민기 (2024). 『ETF 시장의 개인투자자』. 자본시장연구원 연구보고서 24-02. [원문](https://www.kcmi.re.kr/report/report_view?report_no=1776).
- D’Acunto, Francesco, Nagpurnanand Prabhala & Alberto G. Rossi (2019). “The Promises and Pitfalls of Robo-Advising.” *The Review of Financial Studies* 32(5), 1983–2020. [저자 공개 원문](https://www.fdic.gov/promises-and-pitfalls-robo-advising.pdf); [게재정보](https://api.crossref.org/works/10.1093/rfs/hhz014).
- Bhattacharya, Utpal, Andreas Hackethal, Simon Kaesler, Benjamin Loos & Steffen Meyer (2012). “Is Unbiased Financial Advice to Retail Investors Sufficient? Answers from a Large Field Study.” *The Review of Financial Studies* 25(4), 975–1032. [저자 소속대학의 원 논문 초록](https://researchportal.hkust.edu.hk/en/publications/is-unbiased-financial-advice-to-retail-investors-sufficient-answe/).
- Bhattacharya, Utpal, Benjamin Loos, Steffen Meyer & Andreas Hackethal (2017). “Abusing ETFs.” *Review of Finance* 21(3), 1217–1250. [저자 소속대학의 원 논문 초록](https://researchportal.hkust.edu.hk/en/publications/abusing-etfs/).
- 금융위원회 (2016). 「로보어드바이저 테스트베드 기본 운영방안」. [원문](https://www.fsc.go.kr/po010101/72307).
- 금융위원회 (2019). 「로보어드바이저 활성화를 위한 제도개선」. [원문](https://www.fsc.go.kr/no010101/73686).
- 금융위원회 (2023). 「금융투자업규정 일부개정고시안 금융위원회 의결·시행」. [원문](https://www.fsc.go.kr/no010101/80133).
- 금융위원회 (2025). 「로보어드바이저가 퇴직연금을 자동으로 운용해주는 새로운 연금투자 방식이 시행됩니다」. [원문](https://www.fsc.go.kr/no010101/84247).
- 코스콤 로보어드바이저 테스트베드센터 (2025~2026). 「공시기준」, 「RA 시장규모 추이 자료: 2025년 12월 말·2026년 9월 말」, 「RATB Dashboard: 2026년 10월 12일 조회」, 「유의사항」. [공시기준](https://www.ratestbed.kr/portal/main/contents.do?menuNo=200239) · [2025년 12월](https://www.ratestbed.kr/portal/bbs/B0000006/view.do?nttId=34709&menuNo=200241) · [2026년 9월](https://www.ratestbed.kr/portal/bbs/B0000006/view.do?nttId=38805&menuNo=200241) · [대시보드](https://www.ratestbed.kr/portal/pblntf/boardA.do?menuNo=200242) · [유의사항](https://www.ratestbed.kr/portal/main/contents.do?menuNo=200223).
- 코스콤 ETF CHECK (2026). 「국내 ETF 시장 2025년 12월 결산」, *2025년 12월 말 기준*. [원문](https://www.koscom.co.kr/portal/bbs/B0000066/view.do?nttId=30496&menuNo=200562).
- 한국거래소 (연도 미기재). 「순자산가치와 괴리율」, *Market: ETF*. [원문](https://open.krx.co.kr/contents/OPN/01/01030203/OPN01030203T1.jsp).
