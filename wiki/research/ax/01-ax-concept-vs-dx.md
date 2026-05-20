# AX(AI Transformation) 개념과 DX와의 관계

> 📅 작성일: 2026-05-20 · 정책·시장 통계는 시점 의존적이므로 6~12개월 후 재검토 권장
> 🔖 시리즈: AX 리서치 1/3 — `[[02-ax-success-cases]]` · `[[03-ax-process-framework]]`

## Executive Summary

**"AX(AI Transformation)"** 는 2023~2024년 한국·일본 SI 업계에서 본격 통용된 조어로, **영문권 컨설팅·학계는 "AI Transformation" 풀네임**을 사용한다. 본 노트는 AX의 정의·DX와의 관계·배경 맥락을 5개 권위 출처 + 4개 학계·독립 회의 출처로 교차검증한다.

핵심 결론은 **양론 병기**다 — falsification gate 평가에서 "AX = DX의 marketing 리브랜딩"이라는 단정도, "AX는 DX와 구분되는 독립 패러다임"이라는 단정도 모두 출처 우세를 확보하지 못했다. 그 대신:
- **지지측**: McKinsey "Rewired", BCG, Deloitte, 한국 SI 3사(LG CNS, 삼성SDS, SK AX)는 AX가 자율 의사결정·에이전틱 AI 차원에서 DX와 질적 차이를 가진다고 주장 (회색지대 부록표 기준 대부분 `[Self-Reported]`)
- **회의측**: Acemoglu(NBER w32487, 2024), Benedict Evans, Gary Marcus, RAND 2024 보고서는 AI 효과의 과장과 채택 격차를 지적하며 transformation 내러티브 규모를 비판 (`[Independently-Audited]`)

본 노트는 어느 한쪽으로 단정하지 않고 **양쪽 근거를 모두 명시**한다. 독자(사용자)는 후속 사례 노트와 프레임워크 노트를 종합하며 자기 입장을 형성하면 된다.

---

## 1. AX란 무엇인가?

### 1.1 영문권 권위 출처의 정의

**McKinsey — "Rewired" 6 역량 프레임워크** `[Self-Reported]`
> "기업이 디지털·AI 기술로 경쟁우위를 창출하도록 근본적으로 재배선(rewire)하는 과정. 단순 AI 도입이 아닌 value roadmapping, talent, operating model, data, technology, adoption & scaling 6 가지 엔터프라이즈 역량의 동시 구축."

- 출처: McKinsey "Rewired: The McKinsey Guide to Outcompeting in the Age of Digital and AI" (초판 2023-06)
  - URL: https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/leadership-and-digital-transformation
- 핵심 수치(2025 State of AI): 88% 조직이 AI를 1개+ 기능에 사용하나, "AI 전략이 충분히 성숙해 실질 가치를 창출한다"고 답한 조직은 **1%에 불과**

**BCG — "AI Transformation = Workforce Transformation"** `[Self-Reported]`
> "AI의 진정한 가치는 알고리즘 자체(~10%)와 기술 구현(~20%)이 아닌, 인적 역량과 업무 방식의 재설계(~70%)에서 비롯됨."

- 출처: BCG, "AI Transformation Is a Workforce Transformation" (2026)
  - URL: https://www.bcg.com/publications/2026/ai-transformation-is-a-workforce-transformation
- 추가 수치: 조직의 **5%만이 매출·현금흐름 양면에서 실질적 재무성과** 달성 (BCG, "Are You Generating Value from AI? The Widening Gap" 2025)

**Deloitte — "AI-fueled organization"** `[Self-Reported]`
> "AI가 업무 수행 방식과 필요 스킬을 근본적으로 바꾸는 과정에서 Trust · Data Fluency · Agility 3 가지 문화 요소를 내재화한 'AI-fueled entity'로 거듭나는 것."

- 출처: Deloitte, *State of AI in the Enterprise, 4th Edition*
  - URL: https://www.deloitte.com/us/en/what-we-do/capabilities/applied-artificial-intelligence/articles/build-ai-ready-culture.html
- 성숙도 3단계 — ① 새 제품·BM 창출(1/3) ② 핵심 프로세스 재설계(1/3) ③ 표면 AI 활용(1/3). Change management 투자 조직이 AI 이니셔티브 기대 초과 확률 **1.6배**.

**MIT Sloan + BCG — "10% 조직만 상당한 재무 이익 달성"** `[Independently-Audited]`
> 핵심 차별 요인은 machine learning이 아닌 **organizational learning**에 의도적 투자.

- 출처: MIT Sloan Management Review, "Winning With AI" 시리즈
  - URL: https://sloanreview.mit.edu/projects/winning-with-ai/

### 1.2 Korean·Japanese 발신 정의

"AX"라는 약어 자체는 **한국·일본 SI 업계에서 통용되는 조어**다. 영문 컨설팅·학계는 "AI Transformation" 또는 "AI-powered transformation" 풀네임을 사용하며, "AX" 약어 단독 사용은 거의 없다.

| 한국 SI 3사 | AX 정의 | 비고 |
|------------|---------|------|
| **LG CNS** | "Application with AI" — 기존 엔터프라이즈 애플리케이션에 GenAI 접목하는 응용계층 통합 | "DX 선도 기업"에서 AX로 진화 포지셔닝 |
| **삼성SDS** | "AX Full-Stack Partner" — 자체·외부 GenAI 모델 + 에이전틱 AI 결합, 클라우드·ERP·물류 전 스택 | 전 스택 AI 전환 지원 |
| **SK AX** (구 SK C&C) | "AI eXcellence" — DX 이후 AI 네이티브 운영으로의 전환 | 2024년 사명 변경 |

- 출처: nextplatform.net, "SI/SM 산업의 AX 전략" (2026-01-08); https://nextplatform.net/si-ax-strategy-samsung-sds-lg-cns-hyundai-autoever-sk-ax/ `[Self-Reported]`

> 💡 **공통 특징**: 한국 SI 3사 모두 AX를 **DX의 상위 레이어**(응용 통합)로 규정. 단순 인프라 공급이 아닌 business workflow AI 통합이 핵심.

### 1.3 등장 배경

- **2022-11**: ChatGPT 출시 → "DX는 이미 완료된 과제, 다음 단계가 AI" 내러티브 확산
- **2023~2024**: 한국·일본 SI 업계 중심 "AX" 용어 본격 통용. 영문권은 동일 개념을 다른 어휘로 표현
  - "AI-powered transformation"
  - "AI-first strategy"
  - "Enterprise AI adoption"
  - "Generative AI strategy"
- **2024~2025**: 에이전틱 AI(Agentic AI) 등장으로 **자율 의사결정** 차원이 새로 부각 — 이 지점이 양론 분기의 핵심

> ⚠️ **검색 시 주의**: 본 노트가 후속 작업의 출발점이라면, 영문 1차 자료 검색에는 **"AI Transformation"** 풀네임 사용. "AX" 약어는 한국·일본 코퍼스 검색에서만 보조적으로 활용.

---

## 2. DX(Digital Transformation)와의 관계

### 2.1 DX 표준 정의

| 출처 | 정의 |
|------|------|
| **McKinsey** | "디지털 기술을 채택해 조직의 운영 방식을 현대화하는 것." 디지털화된 워크플로우도 매 단계 인간 의사결정이 필요하며, 기술이 더 빠르게 실행할 뿐 스스로 학습·예측·최적화하지 않음. |
| **MIT Sloan** | "디지털 기술의 전략적 통합으로 사업 모델·고객 경험·운영 방식을 재정의하는 것." |

### 2.2 AX vs DX 비교 — 5축

| 축 | DX (Digital Transformation) | AX (AI Transformation) |
|----|-----------------------------|------------------------|
| **데이터** | 데이터 수집·저장·보고 (record-of-truth) | 데이터 **학습·추론·예측** 피드백 루프 |
| **기술** | ERP, 클라우드, SaaS 도입 | LLM, **에이전틱 AI**, ML 파이프라인 |
| **조직** | 디지털 부서 신설, IT 현대화 | AI 역량 **전사 내재화**, 워크플로우 재설계 |
| **문화** | 디지털 리터러시, 애자일 전환 | **Data Fluency**, 실험·실패 내성, AI Trust |
| **측정** | 프로세스 속도·비용 절감 | **자율 최적화 성과**, 예측 정확도, 새 BM 수익 |

> 💡 핵심 차이는 **"인간이 더 빠르게 실행하는 기술"(DX) vs "기술이 학습·예측·자율 결정하는 시스템"(AX)** 이라는 컨설팅 진영의 표현이다. 회의측은 이 차이가 마케팅 어휘 수준이라고 본다 — 다음 절 참고.

### 2.3 6대 축의 출처

**"6대 축(전략·데이터·기술·프로세스·인재·문화)" 형태의 단일 권위 출처는 확인되지 않음** — 복수 컨설팅 프레임워크의 합성이다. 가장 근접한 원형:

| 프레임워크 | 6개 구성요소 | 출처 |
|-----------|--------------|------|
| McKinsey "Rewired" 6역량 | Value Roadmap / Talent / Operating Model / Technology / Data / Adoption & Scaling | McKinsey (2023-06) `[Self-Reported]` |
| Deloitte 3 문화 요소 | Trust / Data Fluency / Agility (+ Change Management) | Deloitte *State of AI 4th Ed* `[Self-Reported]` |
| BCG 인재 중심 모델 | Algorithm(10%) / Technology(20%) / People(70%) | BCG (2025) `[Self-Reported]` |

본 노트의 6대 축(전략·데이터·기술·프로세스·인재·문화)은 McKinsey Rewired를 기준으로 재구성한 합성이다 `[Synthesized]`.

| 축 | 설명 | 권위 출처 |
|----|------|----------|
| **전략** | AI 전환 로드맵 — 실질 가치 창출 영역 식별 및 우선순위 | McKinsey "Rewired" `[Self-Reported]` |
| **데이터** | 학습·추론·피드백 루프 가능한 데이터 인프라 | McKinsey + Deloitte `[Self-Reported]` |
| **기술** | 유연한 분산 기술 환경 — LLM·에이전틱 AI 통합 가능 | McKinsey "Rewired" `[Self-Reported]` |
| **프로세스** | AI 기반 워크플로우 재설계 — 의사결정 흐름 재구성 | BCG (2025) `[Self-Reported]` |
| **인재** | AI 고숙련 전문가 벤치 + 전사 AI 리터러시 | McKinsey + MIT Sloan `[Independently-Audited]` |
| **문화** | 실험 내성·학습 조직화 — Trust, Agility, organizational learning | Deloitte + MIT Sloan `[Independently-Audited]` |

---

## 3. AX vs DX — Falsification Gate 양론 병기

본 노트의 핵심 분기 결정 섹션. plan v3의 falsification gate 규칙에 따라 **양 진영의 출처와 근거를 모두 명시**한 후 분기 결정을 사용자에게 위임한다.

### 3.1 분기 B 지지측 — "AX는 DX와 구분되는 독립 패러다임"

**근거 1: McKinsey "Rewired" — 통합 단일 여정 프레임이지만 자율 학습·예측·에이전틱 실행이 신규 차원**
- 6역량 중 4개(전략 로드맵, 인재, 운영 모델, 기술)는 기존 DX 프레임워크와 상당 부분 중복하지만, **"자율 학습·예측·에이전틱 실행" 차원은 DX 어휘에 없는 신규 요소**
- 출처: McKinsey "Rewired" `[Self-Reported]`

**근거 2: BCG — 70% 가치가 워크포스 재설계에서 발생**
- DX 시대에는 디지털 도구가 인간 의사결정의 보조 도구였으나, AX 시대에는 워크플로우 자체가 AI 의사결정 흐름으로 재설계
- 출처: BCG "AI Transformation Is a Workforce Transformation" (2026) `[Self-Reported]`

**근거 3: Deloitte — Trust, Data Fluency, Agility는 DX 문화 요건과 다른 차원**
- "디지털 리터러시"(DX)와 "Data Fluency + AI Trust"(AX)는 요구 역량의 깊이가 다름
- 출처: Deloitte *State of AI 4th Ed* `[Self-Reported]`

**근거 4: 한국 SI 3사 + CIO.com — "Goodbye digital transformation, hello AI-first"**
- LG CNS·삼성SDS·SK AX 모두 AX를 DX 위에 쌓는 상위 레이어로 정의
- CIO.com 2024 기사는 "AI-first" 전환을 DX의 종결과 AX의 시작으로 프레임
- 출처: nextplatform.net (2026-01-08) `[Self-Reported]` · CIO.com (2024) `[Self-Reported]`

### 3.2 분기 A 지지측 — "AX = DX의 AI 강조 marketing 리브랜딩"

**근거 1: Daron Acemoglu — AI productivity 효과는 0.53~0.66%에 그침** `[Independently-Audited]`
- 논문: "The Simple Macroeconomics of AI," NBER Working Paper 32487 (2024-04). *Economic Policy* 40(121), 2025에 게재
  - URL: https://www.nber.org/papers/w32487
- 핵심: Task-based 모델 적용 시 AI의 10년 TFP(전요소생산성) 증가 효과는 **최대 0.66%, 보수 추정 0.53% 이하**
- McKinsey·Goldman Sachs의 연 1.5~3.4% 전망 대비 **현저히 낮음**
- 주장의 의미: AX 시대를 "DX와 질적으로 다른 패러다임"이라 부르기에는 거시경제 효과가 부족 — 어휘 인플레이션 가능성

**근거 2: Benedict Evans — "GenAI's adoption puzzle"** `[Independently-Audited]`
- 출처: ben-evans.com, "GenAI's adoption puzzle" (2025-05-25)
  - URL: https://www.ben-evans.com/benedictevans/2025/5/25/genais-adoption-puzzle
- 핵심: ChatGPT 채택 속도(2년 내 30%)는 PC·웹·스마트폰 대비 빠르나, **DAU/WAU 비율이 매우 낮음** — 일상 활용자 5~15%, 주간 활용자 ~30%
- 인용 표현: "이것이 진정 life-changing transformation이라면 왜 DAU/WAU 비율이 이렇게 나쁜가?"
- 함의: 채택 패턴이 혁명적 전환 내러티브를 지지하지 않음

**근거 3: Gary Marcus — "The bad news: AI is going pretty much as I expected"** `[Independently-Audited]`
- 출처: garymarcus.substack.com (2025-09-05)
  - URL: https://garymarcus.substack.com/p/the-bad-news-ai-is-going-pretty-much
- 핵심:
  - LLM 스케일링이 AGI로 이어지지 않는다는 한계를 2024년 말 업계 주류도 인정
  - AI 에이전트는 2025년 내내 **하이프 대비 실제 배포 성과 미달**
  - 기업 채택이 "예상보다 훨씬 제한적이며 총 수익은 미미"
- 함의: "AX 패러다임"이라는 어휘가 실제 비즈니스 효과보다 앞서 있음

**근거 4: RAND 2024 — AI 프로젝트 80%+ 실패율** `[Independently-Audited]`
- 출처: James Ryseff 외, "The Root Causes of Failure for Artificial Intelligence Projects and How They Can Succeed: Avoiding the Anti-Patterns of AI," RAND Research Report RRA2680-1 (2024)
  - URL: https://www.rand.org/pubs/research_reports/RRA2680-1.html
- 방법론: 5년+ 경력 데이터 과학자·엔지니어 65명 인터뷰
- 핵심 수치: "일부 추산에 따르면 AI 프로젝트 **80% 이상 실패** — AI 미포함 IT 프로젝트 실패율의 약 **2배**"
- ⚠️ 주의: RAND 보고서 자체는 "by some estimates"로 기술 — 자체 측정 수치가 아닌 업계 추산 인용
- 함의: AX 추진의 현실 성과가 컨설팅 내러티브와 큰 격차

> 🔁 **자주 인용되는 오류**: "McKinsey 2024 State of AI에서 보고된 AI 프로젝트 70~80% 실패율" — McKinsey 원문에 없는 인용. 실제 출처는 **RAND 2024**이며, McKinsey 2024의 핵심 수치는 별도로 "65% 조직이 GenAI 정기 사용 / EBIT 5%+ 기여 조직은 응답자 17%"이다.

### 3.3 Falsification Gate 평가 결과

plan v3 규칙에 따른 임계 평가:

| 조건 | 충족 여부 | 비고 |
|------|----------|------|
| (i) 학계·규제·독립 저널리즘 3+개 중 2+개가 **"AX≠DX 구분 불가"를 명시** | ❌ 불충족 | Acemoglu·Evans·Marcus·RAND 모두 "AX 효과 과장" 또는 "채택 격차" 비판이지, "AX와 DX가 개념적으로 동일하다"고 **명시하지 않음** |
| (ii) 컨설팅·Vendor의 AX 정의가 기존 DX 정의와 **90%+ 중복** | ⚠️ 모호 | McKinsey "Rewired" 6역량 중 4개는 기존 DX와 상당 중복, 단 "자율 학습·예측·에이전틱 실행" 차원은 신규 요소 |

**최종 분기**: **양론 병기** (분기 A·B 어느 쪽도 단정하지 않음)

### 3.4 현재 사용자 입장 (vault 학습 노트 코멘트)

> 💭 사용자 코멘트 (백엔드 엔지니어, 2026-05-20)
> - AX는 vendor·SI 업계의 마케팅 어휘이지만, **에이전틱 AI 흐름은 DX 어휘로 잘 잡히지 않는 새로운 기술적 실체**다.
> - 즉 "AX라는 단어는 marketing 색채가 있다"는 회의측의 지적은 일리 있고, "에이전틱 AI 차원의 자율 의사결정은 새로운 패러다임"이라는 지지측의 지적도 일리 있다.
> - 본인의 적용 관점에서는 "AX vs DX" 단정 분기보다 **각 사례에서 어떤 기술적·조직적 결정이 실제 성과를 냈는가**가 더 중요한 질문이다. → 다음 노트 `[[02-ax-success-cases]]` 로 이동.

---

## 4. 배경·맥락 (Industry & Policy)

이 섹션은 v2 → v3 변경에서 "산업 동향·정책 노트"를 본 노트로 흡수한 결과다. 시점 의존적 통계가 다수이므로 **2024~2025년 기준**임을 명기하고 압축 형식으로 보존한다.

### 4.1 시장 규모·성장률 (분석사 데이터 — 회색지대 부록표 케이스 2 적용)

| 출처 | 기준 연도 | 시장 규모 | 2028/2030 전망 | CAGR |
|------|----------|----------|----------------|------|
| IDC (2025) | 2025 | $307B (AI 솔루션 지출) | $632B (2028) | ~20% |
| Gartner AI Software | 2025 | 미공개 | $297.9B (2027, SW만) | ~19% |
| Fortune Business Insights | 2024 | $224B | $1,236B (2030) | 32.9% |

- 출처: IDC, "AI Solutions & Services Global Impact" (2025); https://my.idc.com/getdoc.jsp?containerId=prUS53290725 `[Self-Reported]`
- ⚠️ IDC·Gartner 수치는 **vendor-funded 분석사** 데이터 → 회색지대 케이스 2에 해당 → `[Self-Reported]`. Fortune Business Insights는 광범위 정의 포함 → 과대 추산 가능성

### 4.2 국가별 AI 정책 비교 (2024~2025 기준)

| 국가 | 정책명 | 접근 방식 | 발효 시점 |
|------|--------|----------|----------|
| **EU** | AI Act (Reg. 2024/1689) | 위험 기반 4단계 규제 (금지~저위험). 고위험 시스템 엄격 준수 요건 | 2024년 채택, 단계적 시행 |
| **미국** | AI Executive Order (Trump) | 2025-01 이전 EO 폐지. 연방 종합 입법 없음, 섹터별 기관 가이드라인 의존 | 2025-01 |
| **한국** | 인공지능 기본법 | AI 개발·이용 촉진 + 신뢰성 확보 종합 기본법 | 2024-12-26 제정, 2025-01-21 공포 |
| **일본** | AI 촉진법 | 경량 규제, 형사처벌·행정과징금 없음. 자율규제 우선, 혁신 저해 최소화 | 2025-09 전면 시행 |
| **중국** | 알고리즘 규정 + GenAI 조치 | "강하게 개발, 강하게 통제." 알고리즘 등록제, AI 생성 콘텐츠 라벨링 의무 | 2025-09 (최신 조치) |

- 출처: IAPP Global AI Law and Policy Tracker; https://iapp.org/news/a/global-ai-law-and-policy-tracker-highlights-and-takeaways `[Independently-Audited]` (규제자 1차 출처 기반)
- 보조: anecdotes.ai, "AI Regulations in 2025"; https://www.anecdotes.ai/learn/ai-regulations-in-2025-us-eu-uk-japan-china-and-more `[Self-Reported]`

### 4.3 산업별 AI 도입률 (2024~2025 기준)

| 산업 | 지표 | 출처 | 시점 |
|------|------|------|------|
| **금융** | 업무 관련 GenAI 채택률 63% (Real-Time Population Survey 최고치) | Stanford HAI AI Index 2025 `[Independently-Audited]` | 2024 기준 |
| **제조** | AI 활용 기업 51% (NAM 조사) | Stanford HAI AI Index 2025 `[Independently-Audited]` | 2025 기준 |
| **헬스케어** | GenAI 도입 65% (McKinsey); FDA 승인 AI 의료기기 223건 | McKinsey 2024 `[Self-Reported]` / Stanford HAI `[Independently-Audited]` | 2023~2024 |
| **전체 기업** | 78% 조직이 AI 1개+ 기능 활용 (2024, ↑55% from 2023) | Stanford HAI AI Index 2025 `[Independently-Audited]` | 2024 기준 |

- 출처: Stanford HAI, *AI Index Report 2025* (2025-04 발간), Chapter 4 Economy; https://hai.stanford.edu/ai-index/2025-ai-index-report `[Independently-Audited]`

---

## 5. Pitfalls & Anti-Patterns (AX 추진 시 함정)

본 노트 다음 단계인 `[[03-ax-process-framework]]` 의 Anti-Pattern 섹션과 연결되는 함정 목록.

| # | 함정 | 권위 출처 |
|---|------|----------|
| 1 | **"파일럿 환상"** — AI 파일럿이 성공해도 스케일 시 80%+ 실패 | RAND 2024 `[Independently-Audited]` |
| 2 | **"기술 우선" 오류** — 알고리즘·기술에 70% 투자, 인적·문화 변화에 30% 투자 → BCG 70/20/10 원칙 위반 | BCG 2026 `[Self-Reported]` |
| 3 | **"DX 미완성 위 AX"** — DX 기초(데이터 인프라, 디지털 워크플로우) 부재 상태에서 AX 추진 | 한국 SI 3사 공통 입장 `[Self-Reported]` |
| 4 | **"organizational learning 부재"** — machine learning만 투자하고 조직 학습 메커니즘 미구축 | MIT Sloan "Winning With AI" `[Independently-Audited]` |
| 5 | **"AX = ChatGPT 라이선스 구매"** — 단순 도구 도입을 transformation으로 동일시. AX는 조직·프로세스·문화 변경 동반 | (본 노트 정의 종합) `[Synthesized]` |
| 6 | **"vendor 데이터 맹신"** — IDC/Gartner/vendor 케이스 스터디만으로 의사결정. 회색지대 부록표 적용 X | (rl-verify 2026-05-20) `[Synthesized]` |

---

## 6. 회색지대 분류 부록표 (8 케이스 — 모든 AX 노트 공통)

본 표는 `[Independently-Audited]` vs `[Self-Reported]` 분류 시 운영 규칙. AX 시리즈 노트 3개 모두 본 표 참조.

| # | 회색 케이스 | 분류 |
|---|------------|------|
| 1 | 컨설팅펌+기업 공저 case study (예: McKinsey + Microsoft 공저) | `[Self-Reported]` (공저자 중 1개가 수익 이해관계자면 자동 Self) |
| 2 | 분석가(Forrester, IDC)가 vendor 비공개 데이터를 인용한 리포트 | `[Self-Reported]` |
| 3 | 학회 발표 case study가 vendor 직원에 의해 진행됨 | `[Self-Reported]` |
| 4 | 매체 보도가 IR 자료를 paraphrase한 기사 | `[Self-Reported]` |
| 5 | 학계 논문이 vendor 제공 데이터에 기반 (예: Microsoft Research) | `[Self-Reported]` (학계 형식이라도 데이터 출처가 vendor면 Self) |
| 6 | 학계 논문이 vendor와 독립적 데이터에 기반 (예: SEC 공시 분석) | `[Independently-Audited]` |
| 7 | 규제자(FTC, EU Commission) 공식 발표 | `[Independently-Audited]` |
| 8 | 저널리즘 (FT, Bloomberg) 자체 취재 (소스 다수) | `[Independently-Audited]` |

---

## 7. 학습 리소스 — 다음 단계

| 단계 | 리소스 |
|------|--------|
| 본 노트 다음 | `[[02-ax-success-cases]]` — 3~4개 기업 사례 분석 (카테고리 (b) 외부 도입 + (c) 인하우스) |
| 그 다음 | `[[03-ax-process-framework]]` — 6단계 프레임워크 + 백엔드 엔지니어 관점 횡단 부록 |
| 외부 1차 학습 | Acemoglu NBER w32487 / RAND RRA2680-1 / Stanford HAI AI Index 2025 — 회의측 학계·독립 출처 우선 |
| 컨설팅 입장 | McKinsey "Rewired" / BCG 2026 Workforce Transformation / Deloitte *State of AI 4th* — 회색지대 케이스 적용 후 `[Self-Reported]` |
| 백엔드 엔지니어 적용 | `[[03-ax-process-framework]]` ⑦ 횡단 부록 — MLOps·RAG infra·evals 스택 변화 |

---

## 8. 교차검증 기록

본 노트 작성 시 양 진영 출처 교차검증 결과:

| 주장 | 지지측 출처 | 회의측 출처 | 결론 |
|------|------------|------------|------|
| "AX는 DX 위의 신규 패러다임" | McKinsey, BCG, Deloitte, LG/삼성/SK AX | Acemoglu, Evans, Marcus, RAND | **양론 병기** — falsification gate 조건 (i) 불충족 + (ii) 모호 |
| "AI 효과는 0.5~0.7% TFP" (회의측) | — | Acemoglu NBER w32487 (2024) | `[Independently-Audited]` 단일 학계 출처 — 강한 근거 |
| "AI 프로젝트 80%+ 실패율" | (없음 — 컨설팅 측은 성공 강조) | RAND RRA2680-1 (2024) | RAND가 "by some estimates"로 기술 — 자체 측정 아님, 업계 추산 인용. 정정 인용 시 출처 명시 필수 |
| "78% 조직이 AI 1+ 기능 활용" | Stanford HAI AI Index 2025 | (회의측 부재) | `[Independently-Audited]` — 학계 메타 분석, 채택률 자체는 일치 |

---

## 출처 (Sources)

| 라벨 | 출처 |
|------|------|
| `[Independently-Audited]` | Acemoglu, "The Simple Macroeconomics of AI," NBER w32487 (2024-04). https://www.nber.org/papers/w32487 |
| `[Independently-Audited]` | RAND, "Root Causes of Failure for AI Projects" RRA2680-1 (2024). https://www.rand.org/pubs/research_reports/RRA2680-1.html |
| `[Independently-Audited]` | Benedict Evans, "GenAI's adoption puzzle" (2025-05-25). https://www.ben-evans.com/benedictevans/2025/5/25/genais-adoption-puzzle |
| `[Independently-Audited]` | Gary Marcus, "The bad news: AI is going pretty much as I expected" (2025-09-05). https://garymarcus.substack.com/p/the-bad-news-ai-is-going-pretty-much |
| `[Independently-Audited]` | Stanford HAI, *AI Index Report 2025* (2025-04). https://hai.stanford.edu/ai-index/2025-ai-index-report |
| `[Independently-Audited]` | MIT Sloan, "Winning With AI" 시리즈. https://sloanreview.mit.edu/projects/winning-with-ai/ |
| `[Independently-Audited]` | IAPP, Global AI Law and Policy Tracker. https://iapp.org/news/a/global-ai-law-and-policy-tracker-highlights-and-takeaways |
| `[Self-Reported]` | McKinsey, "Rewiring for digital and AI" (Rewired 2023-06). https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/leadership-and-digital-transformation |
| `[Self-Reported]` | McKinsey, State of AI 2025. https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai |
| `[Self-Reported]` | BCG, "AI Transformation Is a Workforce Transformation" (2026). https://www.bcg.com/publications/2026/ai-transformation-is-a-workforce-transformation |
| `[Self-Reported]` | BCG, "Are You Generating Value from AI? The Widening Gap" (2025). https://www.bcg.com/publications/2025/are-you-generating-value-from-ai-the-widening-gap |
| `[Self-Reported]` | Deloitte, *State of AI in the Enterprise, 4th Ed*. https://www.deloitte.com/us/en/what-we-do/capabilities/applied-artificial-intelligence/articles/build-ai-ready-culture.html |
| `[Self-Reported]` | nextplatform.net, "SI/SM 산업의 AX 전략" (2026-01-08). https://nextplatform.net/si-ax-strategy-samsung-sds-lg-cns-hyundai-autoever-sk-ax/ |
| `[Self-Reported]` | CIO.com, "Goodbye digital transformation, hello AI-first" (2024). https://www.cio.com/article/3816862/goodbye-digital-transformation-hello-ai-first-business-transformation.html |
| `[Self-Reported]` | IDC, "AI Solutions & Services Global Impact" (2025). https://my.idc.com/getdoc.jsp?containerId=prUS53290725 |
| `[Self-Reported]` | anecdotes.ai, "AI Regulations in 2025". https://www.anecdotes.ai/learn/ai-regulations-in-2025-us-eu-uk-japan-china-and-more |

**구조적 적대적 출처(수익 이해관계 없는 학계·저널리즘·규제자) 충족 여부**: ✅ 총 7건 (`[Independently-Audited]` 라벨) — 노트당 1건+ 의무 충족.

---

> 🔖 다음 노트: `[[02-ax-success-cases]]` — 3~4개 기업 사례를 (b) 외부 AI 도입 + (c) 인하우스 AI 역량 구축 카테고리로 분리하여 분석. 본 노트의 양론 병기 결과를 받아 사례 패턴이 "AX 고유 차원"인지 "DX 연장선"인지 추가 평가.
