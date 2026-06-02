---
tags: [ax, case-study, playbook, finance]
created: 2026-06-02
company: DBS Bank
category: 금융 · 장기 체계 구축
valid_until: 2027-Q2
---

# DBS Bank AX Playbook — 5년 체계로 SGD 1B를 만든 은행

> 📅 작성일 2026-06-02 · 측정치·동향은 시점 의존적, 6~12개월 후 재검토 권장
> 🔖 AX 실천 Playbook 시리즈 · [[00-ax-practice-guide]]

---

## 0. Executive Summary

DBS Bank는 2014년 디지털 전환을 시작으로, 2019년 PURE 윤리 프레임워크 수립, 2021년 9,000명+ AI 업스킬링, 2023년 700명 규모 Data Chapter 조직화라는 단계적 체계를 쌓았다. 이 기반 위에서 2022년 공식 선언한 "5년 내 SGD 1B" 목표를 2025년에 조기 달성했으며 `[Self-Reported]`, Harvard Business School은 아시아 은행 최초의 AI 케이스스터디로, Global Finance는 세계 최고 AI 은행(2025)으로 선정했다 `[Independently-Audited]`. 핵심 교훈은 기술보다 먼저 데이터 거버넌스·윤리 기반을 다지고, 중앙 지식 공유와 현장 임베딩을 동시에 달성하는 조직 구조를 만든 것이다.

---

## 1. 출발점 — 왜 AX를 시작했나

### 1-1. 출발 시점의 문제 인식 (2014년 전후)

- CEO 피유시 굽타(Piyush Gupta)는 2014년을 전후해 "전통 은행보다 기술 스타트업처럼 운영해야 한다"는 방향을 제시했다 `[Self-Reported]`.
- 싱가포르 최대 은행으로서 데이터는 풍부했지만, 사일로화된 시스템과 레거시 인프라로 인해 데이터 활용이 단절되어 있었다.
- 규제 압박(싱가포르 MAS 지도), 핀테크·빅테크의 금융 진입, 동남아시아 고성장 시장에서의 경쟁 격화가 변화의 외부 촉발 요인이었다.

### 1-2. 전략 선택의 근거

| 선택지 | DBS가 선택한 이유 |
|--------|-----------------|
| 외부 AI 솔루션 구매 | ❌ 도메인 맥락 없는 블랙박스로 현장 적용 어려움 |
| 내부 역량 자체 구축 | ✅ 컨텍스트·문화·규제 이해 내재화 |
| PoC 중심 실험 | ❌ 개별 성공이 전사 스케일로 이어지지 않음 |
| 산업화(Industrialisation) | ✅ 반복 가능한 AI 배포 파이프라인 표준화 |

> Nimish Panchmatia(최고 데이터 전환 책임자, CDTO): "PhD 데이터 과학자를 영입해도 우리의 맥락과 문화를 이해하지 못하면 AI를 적용하기 어렵다." `[Self-Reported]`

---

## 2. 타임라인 — 어떻게 수행했나

### 연도별 단계표

| 연도 | 단계 | 주요 이벤트 |
|------|------|------------|
| **2014** | 기반 구축 | 디지털 전환 선언, 기술 인프라 현대화 착수 (레거시 → 오픈소스·클라우드) |
| **2017** | 인재 전환 선제 | 싱가포르 최초 은행 전문직 전환 프로그램(데이터·AI) 도입 `[Self-Reported]` |
| **2018–2019** | 거버넌스 확립 | PURE 윤리 프레임워크 수립 (DBS 공식 페이지: "2019년부터 사용") `[Self-Reported]` |
| **2021** | 전사 업스킬링 | 9,000명+ 임직원 데이터·AI 업스킬링 시작 (이후 누적) `[Self-Reported]` |
| **2022** | 목표 공식화 + 가치 측정 시작 | CIO 지미 응(Jimmy Ng): "5년 내 SGD 1B" 목표 공개 선언; 해당 연도 SGD 1억 8,000만 달성 (매출 SGD 1억 5,000만 + 비용 절감 SGD 3,000만) `[Self-Reported]` |
| **2022** | GenAI 실험 착수 | 생성형 AI 실험 시작, 거버넌스 프레임워크 확장 검토 |
| **2023** | 조직 재편 | Data Chapter 공식 출범 (700명 데이터 전문가 통합), DBS-GPT 내부 도구 출시 `[Self-Reported]` |
| **2023** | 외부 검증 시작 | Global Evident AI Index: AI 전략 리더십 세계 1위, 종합 10위 (아시아 은행 유일 Top 10) `[Independently-Audited]` |
| **FY2023 말** | 누적 가치 공개 | 경제가치 SGD 3억 7,000만 달성 `[Self-Reported]` |
| **2024** | 스케일 가속 | 1,500개+ AI 모델, 370개+ 유스케이스 배포; SGD 7억 5,000만~7억 8,000만 달성 `[Self-Reported]` |
| **2024** | 학술 인정 | Harvard Business School: 아시아 은행 최초 AI 케이스스터디 "DBS' AI Journey" 발간 (저자: Feng Zhu 교수) `[Independently-Audited]` |
| **2024~25** | CEO 승계 | 탄 수 샨(Tan Su Shan) 2024-08 Deputy CEO → 2025-03 CEO 취임 (굽타 2025-03-28 퇴임), AI 전략 연속성 유지 |
| **2025** | 목표 조기 달성 | SGD 1B 달성 (2년 조기 달성), Global Finance: 세계 최고 AI 은행 선정 `[Independently-Audited]` |

### 경제가치 누적 성장 추이

```
SGD (단위: 억)
10 ┤                                    ★ 10B (2025)
 9 ┤
 8 ┤
 7 ┤                           ■ 7.5–7.8B (2024)
 6 ┤
 5 ┤
 4 ┤                  ◆ 3.7B (FY2023)
 3 ┤
 2 ┤         ● 1.8B (2022)
 1 ┤
 0 ┤────────────────────────────────────
    2022     2023      2024      2025
```

---

## 3. 조직 변화 — 신설 부서·역할·보고체계

### 3-1. Data Chapter (2023년 출범)

| 항목 | 내용 |
|------|------|
| **규모** | 700명 데이터 전문가 (데이터 과학자 약 200명 + 번역가·엔지니어 등) |
| **구조** | 하이브리드 임베딩: 각자의 사업·지원 부서에 소속되어 일상 업무 수행 + 중앙 Data Chapter에 소속되어 스킬링·리소싱 관리 |
| **목적** | 지식 공유, AI 산업화 촉진, 도메인 전문성과 데이터 역량의 융합 |
| **보고체계** | 현장 업무는 각 사업부 보고 / 스킬링·리소싱은 중앙 CDTO(최고 데이터 전환 책임자) 산하 |

> [Self-Reported] — DBS Bank 공식 발표 및 EDB Singapore 인터뷰 종합

### 3-2. 핵심 리더십

| 역할 | 인물 | 역할 핵심 |
|------|------|----------|
| CEO (전임) | 피유시 굽타 (2009–2024) | AX 비전 제시, "기술 스타트업처럼 운영" 문화 정착 |
| CEO (현) | 탄 수 샨 (2024–) | GenAI 시대 전략 계승, "AI with a heart" 철학 강조 |
| CDTO | Nimish Panchmatia | AI·데이터 전략 실행, SGD 1B 달성 주도 |
| CIO (전) | 지미 응(Jimmy Ng) | 2022년 SGD 1B 목표 공개 선언 |

### 3-3. 조직 구조 변화 핵심

```
[기존 구조]                      [AX 이후 구조]
─────────────────                ──────────────────────────────
각 사업부별 분산된                CDTO (Nimish Panchmatia)
데이터 팀 (사일로)    →              │
                                 ├── Data Chapter (700명, 중앙 스킬링)
                                 │    └── 각 사업부 임베딩 데이터 전문가
                                 ├── ADA 플랫폼 팀 (데이터 거버넌스)
                                 └── Responsible AI Taskforce (GenAI 거버넌스)
```

---

## 4. 의사결정·거버넌스 — 어떤 프로세스로 결정했나

### 4-1. PURE 윤리 프레임워크

DBS가 2019년부터 시행한 AI·데이터 사용의 윤리 기준으로, "법적으로 허용되는가"가 아니라 "사용해야 하는가"를 판별하는 도구다 `[Self-Reported]`.

| 원칙 | 내용 |
|------|------|
| **P**urposeful (목적성) | 데이터 사용에 명확하고 정당한 목적이 있어야 한다 |
| **U**nsurprising (예측 가능성) | 데이터 사용이 개인·법인의 합리적 기대에 부합해야 한다 |
| **R**espectful (존중) | 사회 규범을 준수하고 개인 프라이버시·존엄성을 존중해야 한다 |
| **E**xplainable (설명 가능성) | 데이터 사용이 투명하고 모델 근거를 명확히 설명할 수 있어야 한다 |

**운영 방식**: 각 AI 유스케이스 오너가 PURE 체크리스트를 적용해 자기 평가 수행 → 리스크 레벨에 따라 상위 거버넌스 검토 (3단계 거버넌스: 데이터 기반 → PURE 적용 → 모델 거버넌스).

**GenAI 확장**: 2022년 생성형 AI 실험 착수 시, 크로스펑셔널 Responsible AI Taskforce를 구성해 GenAI 유스케이스 평가 및 리스크 완화 지침 수립 `[Self-Reported]`.

### 4-2. AI 모델 거버넌스 3단계

```
1단계: 데이터 거버넌스 기반
  ├── 보안, 프라이버시, 접근 제어, 데이터 품질
  └── ADA 플랫폼으로 단일 진실 공급원(Single Source of Truth) 확보

2단계: PURE 프레임워크 적용
  ├── 유스케이스별 PURE 자기 평가
  └── 규제 변화에 따른 정기 업데이트

3단계: 모델 거버넌스
  ├── 중요도 평가(Materiality Assessment)
  ├── 의무 거버넌스 요건
  ├── ALAN 프로토콜 등록 (AI 모델 레지스트리)
  └── 시니어 경영진 책임 체계
```

### 4-3. 리스크 기반 접근

- 고객 대면 애플리케이션: 보수적 배포 (95%+ 정확도 요건 필수)
- 내부 직원 대면 도구: 더 빠른 반복 허용
- 금융거래·투자 어드바이저리: 엄격한 Human-in-the-loop 요건

---

## 5. 실행 디테일 — 기술 스택·데이터 플랫폼·롤아웃

### 5-1. 핵심 기술 인프라

| 플랫폼/도구 | 역할 | 주요 특징 |
|------------|------|----------|
| **ADA** (Advancing DBS with AI) | 데이터 거버넌스 플랫폼 | 5.3PB 데이터 보유; 데이터 검색성·품질·보안의 단일 진실 공급원; 셀프서비스 UI |
| **ALAN** (Alan Turing 이름에서 유래) | AI 프로토콜·지식 저장소 | 과거 유스케이스 탐색, 사용 데이터·ML 기법·최종 모델·정확도를 표준화 형태로 보존; 반복 배포 가속 |
| **Vertex AI** (Google Cloud) | 모델 서빙·API | 플랫폼 중립적 API 레이어; 모델 버전 유연성 확보 |

> ADA + ALAN 조합으로 AI 유스케이스 배포 기간이 12–15개월 → 2–3개월으로 단축됨 `[Self-Reported]`.

### 5-2. 인프라 현대화 경로

```
레거시 시스템
    │
    ▼  (2014~2017)
오픈소스 기술 스택 전환 + 하이브리드 멀티클라우드 도입
    │
    ▼  (2019~2021)
ADA 플랫폼 구축 (데이터 거버넌스 + 피처 마트)
    │
    ▼  (2021~2022)
ALAN 프로토콜 완성 (AI 모델 레지스트리 + 재사용 파이프라인)
    │
    ▼  (2022~2024)
GenAI 레이어 추가 (Vertex AI + LLM + RAG)
    │
    ▼  (2024~)
에이전틱(Agentic) AI 워크플로우 통합 실험
```

### 5-3. 주요 유스케이스 롤아웃

| 유스케이스 | 적용 영역 | 성과 |
|-----------|----------|------|
| **NAV Planner AI 넛지** | 소비자 금융 | 30M건/월 초개인화 인사이트 발송 (싱가포르 3.5M 고객) |
| **CSO 어시스턴트** (고객 서비스) | 콜센터 | 통화 처리 시간 20% 단축, 솔루션 추천 정확도 95%+ |
| **세일즈 퍼슨 증강** | 기업금융 | 통화 준비 시간 30–40% 절감 → 영업 기회 30–40% 증가 |
| **중소기업 융자** | SME 뱅킹 | 즉시 융자 최대 SGD 30만, 부실채권 3개월+ 조기 식별 95% |
| **부실 차주 감지** | 리스크 관리 | 리스크 차주 80% 사전 아웃리치 성공 |
| **GenAI 고객서비스** | 콜센터 자동화 | 월 25만 건 루틴 쿼리 자동화 (RAG 기반), 루틴 업무 80% 처리 |
| **iGrow / iCoach** | 인사·채용 | AI 기반 커리어 어드바이저; 내부 공석의 30% 내부 충원 기여 |

### 5-4. 소프트웨어 개발 가속

- DBS-GPT: 5,000명+ 싱가포르 직원 사용
- 개발자 코드 지원 도구: 시장 출시 속도 향상, 버그 감지, 소프트웨어 품질 개선 (엔지니어 대체가 아닌 증강)

---

## 6. 측정 결과 — 어떻게 성공을 측정했나

### 6-1. 경제가치 측정 방법론

DBS는 AI 경제가치를 **3가지 범주의 합산**으로 산출한다 `[Self-Reported]`:

| 범주 | 내용 |
|------|------|
| **매출 증대** | 소비자·기업금융 이자수익, 수수료, 커미션 증가분 |
| **비용 절감** | 운영 효율화로 인한 비용 절감액 |
| **리스크 회피** | 리스크 가중 손실 감소분 |

**컨트롤 그룹 비교법**: AI 솔루션 적용 고객군 vs. 비적용 고객군(컨트롤 그룹)의 행동·결과 차이를 측정해, 이론적 추정이 아닌 실측 효과만을 반영한다 `[Self-Reported]`.

**연간 보고서 공시**: DBS는 전 세계 소수의 금융기관 중 하나로, 감사받은 연간 보고서에 AI 경제가치를 공개적으로 공시한다 `[Independently-Audited — 회계감사를 받은 연간보고서 기재]`.

> Nimish Panchmatia: "지난해(2024년) SGD 7억 5,000만, 2025년에는 10억 달러를 넘을 것으로 예상한다." `[Self-Reported]`

### 6-2. Forrester 독립 검증

- Tom Mouhsian(Forrester 애널리스트)이 DBS AI 여정 케이스스터디 보고서 발간 `[Independently-Audited]`
- 보고서 제목: "DBS Bank's Billion-Dollar AI Dream — Realized" (2026년 1월 발간)
- 검증 내용: Forrester는 DBS의 AI 역량 구축 방식, 고객·사업·임직원·주주에 대한 혜택을 분석; DBS의 **방법론** (컨트롤 그룹 비교, 3범주 가치 산출)을 케이스로 기술했으나, Forrester 자체의 독립 재계산은 공개 문서에서 확인되지 않음 `[Uncertain — 방법론 설명 vs 독립 재산 여부 불명확]`.

### 6-3. 정량 성과 (주요 수치)

| 지표 | 수치 | 라벨 |
|------|------|------|
| AI 경제가치 (2022) | SGD 1억 8,000만 | `[Self-Reported]` |
| AI 경제가치 (FY2023) | SGD 3억 7,000만 | `[Self-Reported]` |
| AI 경제가치 (2024) | SGD 7억 5,000만~7억 8,000만 | `[Self-Reported]` |
| AI 경제가치 (2025) | SGD 약 10억 | `[Self-Reported]` |
| 배포 AI 모델 수 (2025년 초) | 1,500개+ | `[Self-Reported]` |
| AI 유스케이스 수 (2025년 초) | 370개+ | `[Self-Reported]` |
| AI 배포 기간 단축 | 12–15개월 → 2–3개월 | `[Self-Reported]` |
| 업스킬링 임직원 수 (2021~) | 9,000명+ | `[Self-Reported]` |
| 디지털 고객 서비스 비용 | 전통 채널 대비 50% 절감 | `[Self-Reported]` |

### 6-4. 고객 행동 변화 (NAV Planner AI 넛지)

| 지표 | 수치 | 비교 기준 | 라벨 |
|------|------|----------|------|
| 저축 증가율 | 83% | AI 넛지 수신 vs. 비수신 고객 | `[Self-Reported]` |
| 투자 증가 | 4.3배 | 동일 비교 | `[Self-Reported]` |
| 보험 가입 증가 | 2.3배 | 동일 비교 | `[Self-Reported]` |
| NAV Planner 설문 완료 후 투자 시작 | 3배 가능성 | 설문 완료 vs. 미완료 고객 | `[Self-Reported]` |
| 월간 발송 넛지 수 (싱가포르) | 3,000만 건 | 3.5M 고객 대상 | `[Self-Reported]` |
| 분석 고객 데이터 포인트 | 1만 5,000개/고객 | 100개 이상 AI/ML 알고리즘 활용 | `[Self-Reported]` |

> **측정 방법**: A/B 테스트(AI 처리군 vs. 컨트롤군) + 고객 행동 종단 추적. 다만 실험 설계 세부(무작위 배정 방법, 추적 기간, 혼재 변수 통제)는 공개 문서에서 확인 불가 `[Uncertain]`.

### 6-5. 외부 인정 (독립 검증 성격)

| 기관 | 수상/인정 | 연도 |
|------|----------|------|
| Global Evident AI Index | AI 전략 리더십 세계 1위; 종합 Top 10 (아시아 은행 유일) | 2023 |
| Celent | Global Model Bank Award — AI Industrialisation | 2024 |
| Harvard Business School | 아시아 은행 최초 AI 케이스스터디 ("DBS' AI Journey") | 2024 |
| Global Finance | 세계 최고 AI 은행 (Best Corporate/Institutional AI Bank, Best Enhanced Customer Experience 포함) | 2025 |
| Euromoney | World's Best Bank (2019, 2022, 2025 — AI 포함 전반적 탁월성) | 2025 |
| The Banker | Global Bank of the Year | 2025 |

---

## 7. 핵심 실천 교훈 — 따라 할 수 있는 것

### 7-1. 기술보다 데이터 기반을 먼저 다진다

ADA 플랫폼(5.3PB 데이터, 단일 진실 공급원)을 AI 배포보다 먼저 완성했다. 데이터 거버넌스·품질·접근 제어가 없으면 모델 수가 늘어도 가치 산출이 어렵다.

- **실천**: 첫 AI 유스케이스 전에 데이터 플랫폼 로드맵을 수립하라. "데이터가 준비되면 AI를 한다"는 순서를 지켜라.

### 7-2. 윤리 프레임워크를 성과 측정 이전에 내재화한다

PURE는 2019년에 수립됐고, 경제가치 측정이 공식화된 것은 2022년이다. 거버넌스가 스케일보다 앞섰기 때문에 빠른 배포에도 규제 문제가 없었다.

- **실천**: "법적으로 가능한가"가 아니라 "해야 하는가"를 묻는 윤리 체크리스트를 AI 유스케이스 승인 게이트에 삽입하라.

### 7-3. 중앙화와 분산화를 동시에 설계한다 (Data Chapter 모델)

Data Chapter는 중앙에서 스킬링·리소싱을 관리하면서도, 구성원은 현장 사업부에 임베딩된다. 순수 중앙화(사일로 재형성)도, 순수 분산화(지식 단절)도 피한다.

- **실천**: 데이터 전문가 조직을 설계할 때 "중앙 CoE + 현장 임베딩" 이중 소속 구조를 검토하라.

### 7-4. 재사용 가능한 AI 파이프라인(ALAN)으로 배포 속도를 표준화한다

ALAN은 과거 유스케이스의 데이터, 기법, 모델, 정확도를 검색 가능하게 보존한다. 새 유스케이스 팀이 처음부터 시작하지 않고 기존 지식을 재활용하면서 배포 기간이 12~15개월에서 2~3개월로 단축됐다.

- **실천**: AI 모델 레지스트리(사용 데이터, ML 기법, 배포 결과 포함)를 초기부터 구축하라. "발견 가능성"이 재사용의 전제조건이다.

### 7-5. 경제가치를 3범주(매출·비용·리스크)로 구조화하고 연간 보고서에 공시한다

DBS는 전 세계 소수 은행 중 하나로 AI 경제가치를 감사받은 연간 보고서에 공개 기재한다. 이 투명성이 이사회·투자자 신뢰를 높이고, 내부 AI 투자 지속의 근거가 된다.

- **실천**: AI ROI 산출 기준을 매출·비용·리스크 3범주로 표준화하고, 컨트롤 그룹과 비교하는 A/B 방식을 초기부터 설계하라.

### 7-6. 목표를 공개 선언하고 리더십 연속성을 유지한다

2022년 CIO 지미 응의 "5년 내 SGD 1B" 공개 선언은 내부 우선순위를 고정했다. 2025년 3월 CEO 승계(탄 수 샨, 굽타 2025-03-28 퇴임) 이후에도 AI 전략을 계승했으며, "AI with a heart" 철학으로 GenAI 시대의 연속성을 확보했다.

- **실천**: AI 목표를 정량화해 외부에 공개 선언하라. 리더십 변화 시 AI 전략 인수인계를 공식화하라.

### 7-7. 스킬링을 기술 도입과 동시에, 전 계층에 걸쳐 설계한다

9,000명+ 임직원 업스킬링, iGrow AI 커리어 어드바이저, DBS-GPT 내부 도구는 AI를 두려워하지 않는 문화 기반을 만들었다. 내부 공석의 30%를 내부 충원으로 채운 것은 이 문화의 결과다.

- **실천**: AI 도입 로드맵에 임직원 스킬링 계획을 동시에 포함하라. "기술 우선, 교육 나중"은 저항과 공백을 낳는다.

---

## 출처 (Sources)

| # | 출처 | URL | 유형 | 검증 수준 |
|---|------|-----|------|----------|
| 1 | Forrester: "DBS Bank's Billion-Dollar AI Dream — Realized" (Tom Mouhsian, 2026-01) | https://www.forrester.com/blogs/dbs-banks-billion-dollar-ai-dream-realized/ | 독립 애널리스트 보고서 | `[Independently-Audited]` |
| 2 | Singapore EDB: "How DBS is capturing the full value of AI and ML" | https://www.edb.gov.sg/en/business-insights/insights/how-dbs-southeast-asias-largest-bank-is-capturing-the-full-value-of-ai-and-machine-learning-in-singapore.html | 정부기관 인터뷰 | `[Self-Reported]` |
| 3 | McKinsey: "DBS CEO Tan Su Shan on building a gen AI-enabled bank" | https://www.mckinsey.com/featured-insights/future-of-asia/dbs-ceo-tan-su-shan-on-building-a-gen-ai-enabled-bank-with-a-heart | 컨설팅 공저 인터뷰 | `[Self-Reported]` |
| 4 | DBS 공식: "Ethical & Responsible AI in Banking" (PURE 프레임워크) | https://www.dbs.com/artificial-intelligence-machine-learning/artificial-intelligence/ethical-and-responsible-ai-in-banking.html | 기업 공식 | `[Self-Reported]` |
| 5 | DBS 공식: "DBS' AI-Powered Digital Transformation" (ADA·ALAN) | https://www.dbs.com/artificial-intelligence-machine-learning/artificial-intelligence/dbs-ai-powered-digital-transformation.html | 기업 공식 | `[Self-Reported]` |
| 6 | Google Cloud: "How DBS builds AI with confidence" (Nimish Panchmatia 인터뷰) | https://cloud.google.com/transform/how-dbs-singapores-largest-bank-builds-ai-with-confidence | 벤더 케이스 + 임원 인터뷰 | `[Self-Reported]` |
| 7 | HBS 케이스 발표 (PR Newswire, 2024-09) | https://www.prnewswire.com/news-releases/harvard-business-school-examines-dbs-ai-strategy-and-implementation-in-its-first-case-study-focusing-on-ai-in-an-asian-bank-302248738.html | 학술기관 발표 | `[Independently-Audited]` |
| 8 | DBS 뉴스룸: "DBS named World's Best AI Bank" (Global Finance, 2025) | https://www.dbs.com/newsroom/DBS_named_Worlds_Best_AI_Bank_2025 | 기업 공식 (수상 발표) | `[Independently-Audited]` |
| 9 | Global Finance Magazine: Nimish Panchmatia 인터뷰 "AI With A Heart" | https://gfmag.com/award/winner-insights/dbs-nimish-panchmatia-ai-banking/ | 전문지 인터뷰 | `[Self-Reported]` |
| 10 | Computer Weekly: "How DBS is industrialising AI across its business" | https://www.computerweekly.com/news/366569993/How-DBS-is-industrialising-AI-across-its-business | 독립 기술 미디어 | `[Self-Reported]` |

---

> **회색지대 참고**: Forrester가 검증한 것은 DBS의 방법론(컨트롤 그룹 비교·3범주 산출) 프레임이며, SGD 수치 자체를 Forrester가 독립 재계산한 증거는 공개 문서에서 확인되지 않는다 `[Uncertain]`. DBS는 감사받은 연간 보고서에 수치를 공시하므로 회계 감사 수준의 검증은 이루어진 것으로 볼 수 있다.
