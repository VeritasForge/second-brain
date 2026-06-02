---
tags: [ax, case-study, playbook, manufacturing]
created: 2026-06-02
company: John Deere
category: 전통 제조 · 비즈니스 모델 전환
valid_until: 2027-Q2
---

# John Deere AX Playbook — 트랙터 제조사가 플랫폼 기업이 되기까지

> 📅 작성일 2026-06-02 · 측정치·동향은 시점 의존적, 6~12개월 후 재검토 권장
> 🔖 AX 실천 Playbook 시리즈 · [[00-ax-practice-guide]]

---

## 0. Executive Summary

John Deere는 188년 역사의 농기계 제조사에서 데이터·자율주행 플랫폼 기업으로 전환하는 과정에 있다. 핵심 전환점은 2017년 AI 스타트업 Blue River Technology($305M 인수)와 2021년 자율주행 스타트업 Bear Flag Robotics($250M 인수)다. 이 두 건의 인수는 단순한 기술 확보가 아니라 **비즈니스 모델 전환의 전략적 내기**였다.

결과: See&Spray 기술은 2024년 시즌 100만 에이커에서 제초제 800만 갤런을 절감했으며 평균 59% 비용 절감을 달성했다 [Self-Reported]. 2025년에는 500만 에이커로 확대되고 제초제 절감은 3,100만 갤런에 달했다 [Self-Reported]. Autonomy Ready 트랙터는 2024년부터 공장 출하 중이며, 기존 8R/9R 기종에는 retrofit 키트가 판매되고 있다.

**BM 전환 핵심**: 일회성 하드웨어 판매 → 에이커당 소프트웨어 라이선스 + 구독 수익. Deere의 Leap Ambitions 전략에서 명시한 목표는 **2030년까지 전체 매출의 10%를 구독·라이선스 형태의 반복 수익(Recurring Revenue)으로 전환**하는 것이다 [Self-Reported].

전통 제조업이 AI 전환(AX)을 추진할 때 Deere는 세 가지를 보여준다: (1) 인수로 기술 속도를 확보하고, (2) 기존 장비 인프라에 소프트웨어 레이어를 올려 해자를 구축하며, (3) 농민이 실제로 얻는 가치(절감액)를 수익 단위로 삼는다.

---

## 1. 출발점 — 왜 AX를 시작했나

### 1-1. 농업 노동력 위기

미국 농가의 평균 연령은 58세를 넘었다 [Self-Reported, Deere CTO Jahmy Hindman 인터뷰]. 수확 시즌에는 하루 12~18시간 노동이 일상이지만 젊은 농업 인력 유입은 정체되고 있다. CTO Hindman은 이를 "더 적은 사람으로 더 많은 일을 해야 하는" 구조적 문제로 규정했다. 자율화는 선택지가 아닌 생존 조건이다.

### 1-2. 화학 비용·환경 규제 압박

비선택적 제초제 살포는 작물 피해와 화학 낭비를 동시에 유발한다. EU 및 미국의 농약 사용 규제가 강화되면서 정밀 살포에 대한 시장 수요가 증가했다. 제초제 가격 상승은 농가의 화학 비용을 압박하고, 절감 기술의 ROI(투자수익률)를 즉각적으로 만든다.

### 1-3. 농기계 하드웨어 시장의 한계

전통 농기계는 7~10년 교체 주기의 일회성 판매 구조다. 마진 개선 여지가 제한적이며, 대형 경쟁사(CNH Industrial, AGCO)와 가격 경쟁이 심화되었다. Deere는 하드웨어에서 소프트웨어·데이터 플랫폼으로 수익 중심을 이동하지 않으면 장기 성장이 어렵다는 내부 판단을 내렸다.

### 1-4. 기술 기회창

2015~2017년 컴퓨터 비전(Computer Vision)과 엣지 AI의 실용화 속도가 가속되었다. 특히 NVIDIA Jetson Xavier 계열 Edge Processing Unit이 고속·고해상도 이미지 처리를 현장 장비에서 가능하게 만들었다. Deere는 이 기술 창이 스타트업 생태계에 먼저 열렸음을 인지하고 인수 전략을 택했다.

---

## 2. 타임라인 — 어떻게 수행했나

| 연도 | 이벤트 | 의미 |
|------|--------|------|
| 2011 | Blue River Technology 창업 (Stanford 출신, Sunnyvale) | 컴퓨터 비전 농업 적용 연구 |
| 2017 | Deere, Blue River Technology 인수 ($305M) | AI 기술 확보; 60명 팀 Sunnyvale 독립 운영 유지 |
| 2019 | Deere, Bear Flag Robotics와 Startup Collaborator 파트너십 시작 | 자율주행 파이프라인 사전 검증 |
| 2021 | Deere, Bear Flag Robotics 인수 ($250M) | 자율주행 트랙터 기술 확보 |
| 2021 Q2 | See&Spray 상업 판매 계획 발표 | 필드 테스트 종료, 상용화 전환 |
| 2022 | See&Spray Ultimate 상용 출하 시작 | 현장 적용 및 데이터 수집 본격화 |
| 2022 Q1 | Leap Ambitions 공식화 — 2030년 10% 반복 수익 목표 | 구독 BM 전환 전략 공표 |
| 2023 말 | Blue River 공동창업자 Jorge Heraud 퇴임; Sunnyvale 랩 Deere 전사 통합 | 독립 스타트업 단계 종료 |
| 2024 | Model Year 2024부터 8R/9R "Autonomy Ready" 패키지 공장 출하 | 자율화 하드웨어 표준화 |
| 2024 | See&Spray 2024 시즌 — 100만 에이커, 800만 갤런 절감, 59% 평균 절감 [Self-Reported] | 상용 규모 검증 |
| 2024 | 기존 2020년 이후 8R/8RX, 2022년 이후 9R/9RX용 retrofit 자율화 키트 출시 | 설치 기반(installed base) 확장 |
| 2025 Q3 | Operations Center PRO 구독 서비스 출시 (기계당 $195/년~) | 소프트웨어 구독 수익 공식화 |
| 2025 | See&Spray 2025 시즌 — 500만 에이커, 3,100만 갤런 절감, 평균 50% 절감 [Self-Reported] | 전년 대비 5배 규모 성장 |
| 2025 | Application Savings Guarantee 도입 — 절감 없으면 무료 | 성과 기반 가격 모델 공식화 |
| 2026~ | Unlimited Annual License 옵션 도입 예정 | 고사용량 농가 대상 구독 전환 |
| 2030 (목표) | 전체 곡물·대두 농가 대상 완전 자율 생산 주기 달성 목표 [Self-Reported] | |

---

## 3. 조직 변화 — 신설 부서·역할·소프트웨어 인력

### 3-1. Intelligent Solutions Group (ISG)

ISG는 Deere 내부의 기술·AI 전담 부서로 25년 이상 운영되어 왔다. 2024년 기준 아이오와주 Urbandale에 $33M 규모의 134,000 sq ft 전용 시설을 운영하며 약 800명의 엔지니어를 수용한다. 데이터 과학자, 소프트웨어 엔지니어, 컴퓨터 비전 연구자로 구성되며, 센서 기술·머신러닝·연결 시스템·로보틱스가 핵심 역량이다.

ISG는 독립적인 P&L(손익 책임) 구조를 가지며 Deere 전사 평균보다 높은 R&D 지출 비율을 유지한다.

**핵심 리더십**: CTO Jahmy Hindman (ISG 총괄, 기술 스택 전반 책임), Senior VP John Stone (ISG 운영 총괄), Senior Group PM Mike Moeller (연결성·자율 시스템·가이던스 기술).

### 3-2. Blue River Technology 통합 경로

인수 직후(2017): Sunnyvale 독립 운영. 60명 팀 유지, 스타트업 문화 보존.
통합 가속기(2022~2023): See&Spray 상용화에 따라 Deere 전사 제품 라인과 통합 심화. 기술 인력이 Deere 글로벌 기술 조직에 흡수.
통합 완료(2023 말): 공동창업자 Jorge Heraud 퇴임, Sunnyvale 랩이 Deere 공식 기술 조직으로 편입. 독립 스타트업 단계 공식 종료.

**시사점**: 인수 후 6년간 독립성을 유지하며 상용화 검증을 완료한 뒤 전사 통합. "인수 후 즉시 흡수" 모델이 아닌 단계적 통합으로 스타트업 혁신 속도를 보존했다.

### 3-3. 소프트웨어 인력 전환

Deere는 General Assembly와 파트너십을 통해 부트캠프 졸업생을 소프트웨어 엔지니어로 채용했으며, 100명 이상의 기존 임직원을 소프트웨어 엔지니어로 재훈련하는 업스킬링 프로그램을 운영했다. 구체적인 총 소프트웨어 엔지니어 수는 공개 자료에서 확인되지 않는다 [Uncertain].

**주의**: Deere는 2024년 전체 인력 2,000명을 감축하면서 동시에 AI·소프트웨어 인력을 채용하는 구조 전환을 병행했다. 전통 제조직 감소와 기술직 증가가 동시에 일어난 전형적인 AX 인력 재구성 패턴이다.

---

## 4. 의사결정·거버넌스 — 인수·BM 전환 의사결정

### 4-1. 인수 의사결정 로직

**Blue River ($305M, 2017)**
- 판단 근거: 자체 컴퓨터 비전 개발 vs. 6년 선행 투자를 가진 스타트업 인수. 스탠퍼드 기원의 기술 깊이와 농업 도메인 특화 데이터셋을 높이 평가.
- 인수 조건 설계: 팀 독립성 보장, Sunnyvale 유지 → 혁신 속도 보존 우선.
- 리스크: $305M은 당시 Deere의 단일 기술 인수로서 이례적 규모. 농업 AI 시장 자체가 검증 전 단계.

**Bear Flag Robotics ($250M, 2021)**
- 판단 근거: 2019년 Startup Collaborator 프로그램을 통한 2년 선행 파트너십으로 기술 검증 완료. 완전 자율 주행이 Blue River의 정밀 살포와 시너지를 낸다는 판단.
- 인수 조건: 역시 Silicon Valley 독립 운영 유지.

**핵심 의사결정 원칙**: Deere는 핵심 AI 역량을 외부 파트너십으로 해결하지 않고 인수(소유)를 택했다. 이유는 데이터 주권 — 농가 데이터가 Operations Center로 독점 유입되어야 AI 플라이휠이 작동하기 때문이다.

### 4-2. BM 전환 거버넌스

Leap Ambitions 프레임워크(2021~ 공식화)는 전략 목표를 두 가지로 수렴한다:
1. 영업이익률 20% (미드사이클 기준)
2. 반복 수익(Recurring Revenue) 10% (2030년 목표)

2022년 Q1 투자자 컨퍼런스콜에서 CFO Ryan Campbell은 "자율 주행이 반복 수익 목표 달성에 중요한 역할을 할 것"이라고 명시했다. 이는 자율화 투자를 단순 R&D가 아닌 **BM 전환 수단**으로 공식 정의한 것이다 [Self-Reported].

---

## 5. 실행 디테일 — See&Spray 기술·Operations Center·구독 모델

### 5-1. See&Spray 기술 스택

**컴퓨터 비전 레이어**
붐(boom)에 장착된 고속 카메라가 초당 2,500 sq ft 이상 (2025년 기준)의 작물 구역을 스캔한다. 각 이미지는 작물·잡초 DB를 학습한 심층 신경망(Deep Neural Network, DNN)을 통해 픽셀 단위로 분류된다. 처리 결과는 밀리초(ms) 단위로 노즐 액추에이터에 전달된다.

**엣지 컴퓨팅 구현**
클라우드 연결 없이 장비 탑재 컴퓨터가 실시간 처리를 수행한다. 야외 농업 환경(조도 변화, 먼지, 진동)을 견디는 엣지 처리 설계. NVIDIA Jetson Xavier 계열 VPU(Vision Processing Unit)가 핵심 처리 칩셋이다.

**모델 학습 데이터**
Operations Center에 축적된 누적 현장 데이터가 모델 재훈련에 사용된다. 330만 이상의 "engaged acres"(연결 에이커)에서 수집된 실제 현장 데이터가 데이터셋의 근간이다 [Self-Reported].

**제품 라인업 (2024~2025)**
- See&Spray Select: 기본 타겟 살포
- See&Spray Premium: 고급 분류 + 비용 절감 최적화
- See&Spray Ultimate: 최고 정밀도 + 작물별 최적화

### 5-2. Operations Center 데이터 플랫폼

Operations Center는 John Deere의 클라우드 기반 농장 관리 플랫폼으로, AX 전환의 데이터 기반 인프라다.

**핵심 기능**:
- 330만 이상 engaged acres의 실시간 데이터 수집 [Self-Reported]
- 수확량 지도, 살포 지도(정확한 잡초 위치 포함), 토양 조건, 장비 성능 데이터 통합
- Digital Farm Twin(디지털 농장 쌍둥이)으로 작업 사전 계획 수립 가능
- 기계 상태(DTC), 소프트웨어 업데이트, 유지보수 계획 통합 관리

**Operations Center PRO (2025년 7월 출시)**
- 연간 구독: 기계당 $195~
- 제공 기능: 기계 건강 인사이트, 진단 코드(DTC), 부품별 콘텐츠, ECU 소프트웨어 리프로그래밍, 인터랙티브 진단 테스트
- 딜러 및 농가 모두 대상 (사업체용 별도 라이선스 존재)

**전략적 의미**: Operations Center는 Deere 장비에서만 발생하는 독점 데이터셋을 구축한다. 이 데이터는 AI 모델 개선에 재투입되고, 개선된 모델은 더 높은 절감 효과를 내며, 이는 더 많은 농가를 유인하는 **AI 플라이휠(Flywheel)**을 형성한다.

### 5-3. 구독·라이선스 수익 모델

**See&Spray 과금 구조 (2025 기준)**
- 휴경지(Fallow) 살포: 에이커당 $1
- 재배 중(In-Crop) 살포: 에이커당 $5 (절감이 발생한 경우에만 과금)
- Application Savings Guarantee: 절감이 발생하지 않으면 무료
- 2026 신규: Unlimited Annual License (고사용 농가 대상, 정액 연간 구독)

**하드웨어 진입 비용**
- See&Spray Premium 업그레이드: 약 $25,000~$100,000 (기존 분무기 종류에 따라 차이)
- 고정 라이선스 옵션: $28,000 USD (Premium 시스템)
- Autonomy retrofit 키트: 기존 8R/9R에 장착 가능 (가격 미공개 [Uncertain])

**전략**: CTO Hindman은 "업프론트 비용을 낮추고 사용량에 비례한 라이선스 모델로 배분한다"고 설명했다. 농가는 절감 가치를 먼저 경험하고, Deere는 성과 기반으로 과금하는 구조다.

**Operations Center PRO 구독**: 기계당 연간 $195~. 반복 수익의 첫 번째 공식 레이어.

---

## 6. 측정 결과 — 어떻게 성공을 측정했나

### 6-1. See&Spray 2024 시즌 성과

| 지표 | 수치 | 출처 라벨 | 측정 방법 |
|------|------|----------|----------|
| 적용 면적 | 100만 에이커 이상 | [Self-Reported] | Deere 2024 Impact Report 집계 |
| 제초제 절감 (갤런) | 800만 갤런 (혼합액 기준) | [Self-Reported] | 에이커당 평균 15갤런 비선택 제초제 기준 전통 광역살포 대비 계산 |
| 평균 비용 절감 | 59% | [Self-Reported] | 옥수수·대두·목화 밭 평균; Premium 및 Ultimate 모델 기준; 광역살포 대비 |
| 독립 연구 절감율 | 76% 평균 (415에이커, 5개 대두밭) | [Sponsored-Study · Deere 후원] | Iowa State University 현장 연구, 제3자 진행이나 Deere 후원 |
| 경제적 절감 | 에이커당 $15.7 | [Sponsored-Study · Deere 후원] | Iowa State University 동일 연구 |
| 필드별 절감 범위 | 43.9%~90.6% | [Sponsored-Study · Deere 후원] | Iowa State 5개 밭 각각 측정 |

**측정 방법 세부 주의사항**:
- "800만 갤런" 산정: 에이커당 15갤런 광역살포를 기준으로 절감 비율 적용. 실제 농가별 살포량이 다를 경우 수치가 달라진다.
- 59% 수치는 Premium·Ultimate 모델에 한정되며, 잡초 밀도·밭 조건에 따라 개별 편차가 크다 (일부 35~40%, 일부 73%+).
- Iowa State 연구는 John Deere가 후원했으나 제3자가 진행했다. 완전 독립 감사가 아닌 "스폰서드 독립 연구"에 해당한다.

### 6-2. See&Spray 2025 시즌 성과 (초기 데이터)

| 지표 | 수치 | 출처 라벨 |
|------|------|----------|
| 적용 면적 | 500만 에이커 이상 | [Self-Reported] |
| 제초제 절감 (갤런) | 3,100만 갤런 (혼합액 기준) | [Self-Reported] |
| 평균 절감율 | 약 50% | [Self-Reported] |
| 수확량 효과 | 대두 평균 +2부셸/에이커 (최대 4.8) | [Self-Reported, 제3자 연구 기반] |
| 스캔 속도 | 초당 2,500 sq ft 이상 | [Self-Reported] |

**2024→2025 성장**: 적용 면적 5배 증가. 절감율은 59%→50%로 소폭 하락 (잡초 조건·적용 지역 확대에 따른 자연스러운 평균 하락으로 해석 가능).

### 6-3. 자율주행 트랙터 성과

| 지표 | 수치 | 출처 라벨 |
|------|------|----------|
| 파일럿 자율 경작 면적 | 50,000에이커 이상 | [Self-Reported] |
| 생산성 향상 | 15~20% | [Self-Reported] |
| 연료·노동 절감 | 6% | [Self-Reported] |
| 카메라 수 (9RX) | 16개 스테레오 카메라 배열 | [Self-Reported] |
| GPS 정밀도 | 1인치 미만 | [Self-Reported] |

### 6-4. Operations Center 플랫폼 규모

| 지표 | 수치 | 출처 라벨 |
|------|------|----------|
| 연결된 총 에이커 | 3억 3천만 에이커 이상 | [Self-Reported] |

**주의**: 3억 3천만 "engaged acres"는 Deere가 공개한 수치로, 어떤 기준으로 "연결됨"을 정의하는지(장비 연결 기준인지, 데이터 전송 기준인지)는 공개 자료에서 명확하지 않다 [Uncertain].

---

## 7. 핵심 실천 교훈 — 전통 산업이 따라 할 수 있는 것

### 교훈 1. "인수 vs. 자체 개발"의 판단 기준

**Deere의 선택**: 컴퓨터 비전(Blue River, 6년 선행) + 자율주행(Bear Flag, 검증 완료) → 인수. 연결 플랫폼(Operations Center) → 내부 구축.

**원칙**: 핵심 AI 알고리즘은 스타트업에서 이미 6년 이상 검증된 경우 인수가 빠르다. 그러나 데이터 플랫폼(경쟁 해자의 원천)은 내부 구축으로 소유권을 확보한다. 양쪽을 혼동하면 핵심 데이터를 외부 플랫폼에 의존하게 된다.

**따라 할 것**: 자체 기술 로드맵에서 5년 이상 걸릴 역량은 스타트업 파트너십 → 검증 → 인수 경로를 미리 설계한다. 데이터가 모이는 플랫폼 레이어는 직접 소유한다.

### 교훈 2. 인수 후 통합은 단계적으로

Blue River는 인수 후 6년간 Sunnyvale 독립 운영을 유지하며 상용화를 달성했고, 공동창업자 퇴임 후에야 전사 통합이 이루어졌다. 즉각적인 통합이 아닌 **단계적 통합**이 혁신 속도를 보존했다.

**따라 할 것**: 인수한 AI 팀을 본사 문화와 프로세스에 즉시 흡수하지 않는다. 독립 P&L과 물리적 독립성을 유지하되, 데이터·인프라 레이어는 초기부터 연결한다.

### 교훈 3. 고객 가치를 수익 단위로 삼는다

See&Spray의 과금 단위는 에이커당 $1/$5다. 이는 "농가가 절감한 제초제 비용"이 직접 수익 단위로 변환된 것이다. Application Savings Guarantee("절감 없으면 무료")는 공급사와 고객의 인센티브를 정렬한다.

**따라 할 것**: AI가 만들어내는 고객 절감액 또는 생산 증가분을 특정하고, 그 가치의 일부를 에이커·거래·시간 등 측정 가능한 단위로 과금 구조화한다. "기술 구독"이 아닌 "성과 구독"으로 포지셔닝한다.

### 교훈 4. 기존 설치 기반(Installed Base)을 플랫폼 진입로로 활용

Deere의 최대 자산은 전 세계 농가에 이미 설치된 수십만 대의 장비다. Retrofit 키트 전략은 신규 판매 없이도 이 기반을 구독 수익 기반으로 전환한다. "새 장비를 사지 않아도 새 소프트웨어가 가치를 열어준다" (CTO Hindman 발언).

**따라 할 것**: 이미 현장에 배포된 제품·설비를 소프트웨어 업그레이드 또는 센서 추가로 AI화한다. 신제품 판매와 기존 기반 전환을 병렬로 추진하면 전환 속도가 빠르다.

### 교훈 5. 데이터 플라이휠을 의도적으로 설계한다

Operations Center → 현장 데이터 수집 → AI 모델 개선 → 더 나은 절감 성과 → 더 많은 농가 유입 → 더 많은 데이터. 이 플라이휠은 의도적으로 설계된 것이다. Deere는 Operations Center를 무료로 제공하면서 데이터 유입을 극대화했다.

**따라 할 것**: AI 서비스의 첫 레이어는 낮은 진입 장벽(무료 또는 저가)으로 설계하여 데이터를 먼저 축적한다. 데이터가 쌓이면 프리미엄 레이어의 정확도가 올라가고, 그것이 구독 전환을 이끈다.

### 교훈 6. "2030년 완전 자율화"라는 내부 강제 함수(Forcing Function)

Deere는 2030년까지 옥수수·대두 농가의 완전 자율 생산 주기를 목표로 공개 선언했다. 이 목표는 내부적으로 R&D, 엔지니어링, 제품 팀의 방향을 하나로 수렴하는 역할을 한다.

**따라 할 것**: 외부에 공개 가능한 기술 마일스톤 목표를 설정하고, 그것을 내부 로드맵의 수렴점으로 삼는다. 목표가 없으면 조직 내 우선순위 충돌이 지속된다.

### 교훈 7. 전통 인력 재훈련을 병행한다

General Assembly 파트너십, 100명 이상 임직원 소프트웨어 재훈련 프로그램은 외부 채용만으로 기술 인력을 확보하는 전략의 한계를 보완한다. 농업 도메인 지식을 가진 기존 인력에 소프트웨어 역량을 추가하는 것이 순수 소프트웨어 엔지니어를 농업에 적응시키는 것보다 빠를 수 있다.

**따라 할 것**: 기술 채용과 내부 재훈련을 이중 트랙으로 운영한다. 도메인 지식은 훈련하기 어렵고, 코딩은 훈련 가능하다.

---

## 출처 (Sources)

1. **Deere & Company — Blue River Technology 인수 발표 (PR Newswire, 2017-09-06)**: 인수 금액, 통합 계획 공식 발표
   https://www.prnewswire.com/news-releases/deere--company-completes-blue-river-technology-acquisition-300518014.html

2. **John Deere — See&Spray Herbicide Savings 공식 페이지 (deere.com, 2024)**: 2024 시즌 100만 에이커, 800만 갤런, 59% 절감 수치 원본 [Self-Reported]
   https://www.deere.com/en/news/all-news/see-spray-herbicide-savings/

3. **Iowa State University / Precision Farming Dealer — ISU Precision Spraying Study: $15.7 Herbicide Savings Per Acre**: 76% 절감율, 에이커당 $15.7 경제적 절감 (John Deere 후원 연구, 제3자 진행) [Sponsored-Study · Deere 후원]
   https://www.precisionfarmingdealer.com/articles/6098-isu-precision-spraying-study-157-herbicide-savings-per-acre

4. **Emerj Artificial Intelligence Research — AI at John Deere**: 기술 스택(NVIDIA Jetson Xavier), 에이커당 구독 BM, CTO 발언, Operations Center 플라이휠 분석
   https://emerj.com/artificial-intelligence-at-john-deere/

5. **DTN Progressive Farmer — John Deere CTO Hindman Talks Pricing at CES 2024**: CTO의 구독 모델·Solutions-as-a-Service 발언 원문
   https://www.dtnpf.com/agriculture/web/ag/equipment/article/2024/01/11/john-deere-cto-hindman-talks-pricing

6. **Global Ag Tech Initiative — John Deere Customers Use See&Spray Technology Across Five Million Acres in 2025**: 2025 시즌 500만 에이커, 3,100만 갤런 절감, Application Savings Guarantee [Self-Reported]
   https://www.globalagtechinitiative.com/in-field-technologies/robotics-automation/john-deere-customers-use-see-spray-technology-across-five-million-acres-in-2025/

7. **Precision Farming Dealer — Autonomy to Play Significant Role in Deere's Recurring Revenue Goal**: Leap Ambitions 2030년 10% 반복 수익 목표, CFO Ryan Campbell 발언
   https://www.precisionfarmingdealer.com/articles/5056-technology-corner-autonomy-to-play-significant-role-in-deeres-target-recurring-revenue-goal

8. **Robotics and Automation News — Exclusive Interview: John Deere Deepens Its Automation Strategy (2025-07-03)**: 9RX 자율 트랙터, 스테레오 카메라 배열, Autonomy Ready 전략, Mike Moeller 발언
   https://roboticsandautomationnews.com/2025/07/03/exclusive-interview-john-deere-deepens-its-automation-strategy/92870/

9. **AgFunderNews — John Deere Acquires Bear Flag Robotics $250M (2021)**: Bear Flag 인수 배경, Startup Collaborator 사전 파트너십, 기술 통합 전략
   https://agfundernews.com/bear-flag-robotics-john-deere-acquires-agfunder-portfolio-company-for-250m

10. **AgUpdate — John Deere Autonomous Technology Introduces Retrofit Kit**: Autonomy Ready 패키지 세부 구성요소, Retrofit 키트 적용 모델 범위(2020년 이후 8R 등)
    https://agupdate.com/farmandranchguide/news/technology/article_973e8902-d6ae-11ef-8383-cf7544d0b11e.html

11. **John Deere Operations Center PRO Service 공식 페이지**: 구독 가격($195~/기계), 제공 기능 상세 [Self-Reported]
    https://www.deere.com/en/technology-products/operations-center-pro-service/

12. **General Assembly Blog — From Ag to AI: Reimagining Tech Talent at John Deere**: 부트캠프 채용, 내부 재훈련 100명+ 프로그램
    https://generalassemb.ly/blog/from-ag-to-ai-reimagining-tech-talent-at-john-deere/
