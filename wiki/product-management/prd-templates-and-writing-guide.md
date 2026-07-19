---
tags: [product-management, prd, requirements-document, templates, best-practices]
created: 2026-07-15
---

# 📖 PRD (Product Requirements Document) — Concept Deep Dive

> 💡 **한줄 요약**: PRD는 "무엇을(What), 왜(Why), 누구를 위해(Who)" 만드는지를 제품·디자인·개발·비즈니스 팀이 공유하는 **단일 진실 공급원(Single Source of Truth)** 문서다.

### 📚 용어 범례 (Glossary) — 아래 약어는 문서 전체에서 반복 사용됩니다

| 약어 | 풀네임 | 의미 |
| --- | --- | --- |
| **PRD** | Product Requirements Document | 제품 요구사항 문서 |
| **PR/FAQ** | Press Release / Frequently Asked Questions | 아마존식 "가상 보도자료+예상질문" 문서 |
| **BRD** | Business Requirements Document | 비즈니스 요구사항 문서 (경영진·이해관계자 대상) |
| **FRD/FSD** | Functional Requirements/Specification Document | 기능 요구사항·명세 문서 (엔지니어 대상, 상세 로직) |
| **SRS** | Software Requirements Specification | 소프트웨어 요구사항 명세서 (BRD보다 상세, FRD보다 상위) |
| **MVP** | Minimum Viable Product | 최소 기능 제품 |
| **KPI** | Key Performance Indicator | 핵심 성과 지표 |
| **TAM** | Total Addressable Market | 전체 유효 시장 규모 |
| **PM** | Product Manager | 프로덕트 매니저 |
| **UX** | User Experience | 사용자 경험 |

---

## 1️⃣ 무엇인가? (What is it?)

**PRD**는 제품 또는 기능의 목적·기능·동작을 상세히 기술하여, 이를 만드는 모든 팀(제품, 디자인, 개발, 마케팅)이 **"무엇이 왜 만들어지는지"에 대한 공통 이해**를 갖도록 하는 문서다. 일반적으로 **PM**이 작성을 주도하지만, 실제로는 이해관계자와의 협업 산출물이다.

- **탄생 배경**: 1990~2000년대 워터폴(Waterfall) 소프트웨어 개발 문화에서, 요구사항을 사전에 문서화해 개발 착수 전 합의를 확정하려는 목적으로 정착했다.
- **애자일 시대의 변화**: 애자일/린 방법론이 확산되며 PRD는 "한 번 쓰고 끝"이 아닌 **살아있는 문서(Living Document)**로 성격이 바뀌었다 — 개발이 진행되며 지속적으로 갱신된다.
- **핵심 원칙**: PRD는 "**무엇을(What)** 해결해야 하는가"를 정의하되, "**어떻게(How)** 구현할지"는 의도적으로 비워둔다 — 이는 디자이너·엔지니어가 최적의 해결책을 찾을 창의적 여지를 남기기 위함이다. ([Wikipedia](https://en.wikipedia.org/wiki/Product_requirements_document), [Atlassian](https://www.atlassian.com/agile/product-management/requirements))

> 📌 **핵심 키워드**: `Single Source of Truth`, `Living Document`, `What not How`, `이해관계자 정렬(Alignment)`

---

## 2️⃣ 핵심 개념 (Core Concepts)

모든 PRD 형식(뒤에서 다룰 Amazon PR/FAQ든, 경량 원페이저든)이 공유하는 **뼈대**는 다음과 같다.

```
┌───────────────────────────────────────────────────────────┐
│                 PRD 핵심 구성요소 관계도                      │
├───────────────────────────────────────────────────────────┤
│                                                             │
│   [문제 & 맥락 Problem/Context]                              │
│              │                                             │
│              ▼                                             │
│   [목표 & 성공 지표 Goals/KPI]  ◄── 비즈니스 목표와 정렬        │
│              │                                             │
│              ▼                                             │
│   [요구사항 Requirements] ◄────── [사용자 스토리/페르소나]      │
│   (What을 정의, How는 비워둠)                                 │
│              │                                             │
│      ┌───────┴───────┐                                     │
│      ▼               ▼                                     │
│  [범위 내 Scope]   [범위 외 Out-of-Scope]                     │
│              │                                             │
│              ▼                                             │
│   [디자인/기술 고려사항]                                       │
│              │                                             │
│              ▼                                             │
│   [미해결 질문 Open Questions] ◄──► [가정 Assumptions/리스크]  │
│                                                             │
└───────────────────────────────────────────────────────────┘
```

| 구성 요소 | 역할 | 설명 |
| --- | --- | --- |
| **문제/맥락(Problem & Context)** | 출발점 | 왜 이 문제가 중요한지, 고객 페르소나와 경쟁 환경을 제공 |
| **목표/성공 지표(Goals & KPI)** | 방향 설정 | 무엇을 달성하려는지와 측정 가능한 기준(**KPI**) |
| **요구사항(Requirements)** | 본체 | 해결해야 할 문제와 필요한 기능 (구현 방법은 제외) |
| **범위/범위 외(Scope/Out-of-Scope)** | 경계 설정 | 이번 릴리즈에 포함/제외되는 것을 명시 |
| **가정(Assumptions)** | 리스크 관리 | 검증되지 않은 전제를 드러내고 검증 계획 제시 |
| **미해결 질문(Open Questions)** | 투명성 | 아직 결정되지 않은 사항을 숨기지 않고 기록 |

- 각 요소는 **위에서 아래로 좁혀지는 깔때기** 구조다 — "왜(문제)" → "무엇을 위해(목표)" → "무엇을(요구사항)" → "어디까지(범위)" 순으로 구체화된다.
- **가정과 미해결 질문**은 별도 섹션이지만 서로 얽혀있다 — 검증되지 않은 가정이 바로 리스크의 원천이기 때문이다. ([ProductPlan](https://www.productplan.com/glossary/product-requirements-document), [Aha.io](https://www.aha.io/roadmapping/guide/requirements-management/what-is-a-good-product-requirements-document-template))

---

## 3️⃣ 작성 프로세스와 라이프사이클 (Process & Lifecycle)

PRD는 한 번 쓰고 서랍에 넣는 문서가 아니라, 제품이 출시될 때까지(그리고 그 이후에도) **계속 갱신되는 참조 문서**로 동작한다.

```
┌────────────────────────────────────────────────────────────────┐
│               PRD 라이프사이클 (Living Document)                  │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ① Discovery        ② Draft PRD        ③ Align & Review          │
│  고객인터뷰/데이터  ──► PM이 초안 작성 ──► 디자인·개발·비즈           │
│  → 문제 정의              (Problem→Goal→Req)   이해관계자와 합의     │
│                                              │                   │
│                                              ▼                   │
│  ⑥ Update & Close   ◄── ⑤ Build          ④ Approve               │
│  성공지표 검증/          개발팀 참조 문서로   Jira/Linear 등          │
│  최종 업데이트           지속 사용, Open       작업 티켓으로 분해     │
│                        Questions 갱신                            │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

### 🔄 단계별 흐름

1. **Discovery(발견)**: 고객 인터뷰·데이터 분석을 통해 "진짜 문제"를 먼저 검증한다. 이 단계 없이 바로 PRD를 쓰면 "해결책을 문제처럼 포장"하는 안티패턴에 빠진다.
2. **Draft(초안)**: PM이 문제→목표→요구사항 순으로 초안을 작성한다. 이 시점에는 `TBD`(추후 결정) 플레이스홀더를 남겨도 무방하다.
3. **Align & Review(정렬/리뷰)**: 디자인·개발·비즈니스 이해관계자와 함께 가정을 검증하고 기술적 제약을 반영한다. 이 단계를 건너뛰면 "PRD는 완성했는데 개발팀이 일정을 맞출 수 없다"는 상황이 재발한다.
4. **Approve(승인)**: 합의된 요구사항이 Jira/Linear 같은 작업 티켓으로 분해된다.
5. **Build(개발)**: 개발 기간 동안에도 PRD는 참조 문서로 계속 쓰이며, 미해결 질문이 해소되는 대로 갱신된다.
6. **Update & Close(갱신/종료)**: 출시 후 성공 지표를 검증하고 문서를 최종 업데이트해 보관한다.

> 📌 이 흐름 자체가 "PRD = 정적 산출물이 아니라 프로세스"라는 핵심 통찰이다. ([Product School](https://productschool.com/blog/product-strategy/product-template-requirements-document-prd), [Reforge](https://www.reforge.com/blog/evolving-product-requirement-documents))

---

## 4️⃣ 형식/템플릿 종류 & 잘 쓰는 법 (Formats, Templates & Best Practices)

### 🗂️ 템플릿 분류 기준 (먼저 읽어주세요)

아래 4가지는 서로 배타적인 "등급"이 아니라, **문서의 무게(얼마나 자세히 쓰는가)**와 **작성 시점(아이디어 단계 vs 실행 단계)**이라는 두 축으로 나뉜 스타일이다. 실무에서는 작은 기능은 원페이저로, 큰 기능은 표준 PRD로 섞어서 쓰는 경우가 많다.

| 유형 | 핵심 특징 | 적합한 상황 | 대표 출처 |
| --- | --- | --- | --- |
| **Amazon PR/FAQ** (Press Release/FAQ) | 아이디어를 "출시된 것처럼" 가상 보도자료+예상질문으로 먼저 쓴다. 고객 관점 강제. | 신제품/신사업처럼 **불확실성이 큰 초기 아이디어 검증** | [Working Backwards 공식 템플릿](https://workingbackwards.com/resources/working-backwards-pr-faq/) |
| **표준 멀티섹션 PRD** (Atlassian/Aha/Google식) | Overview·목표·요구사항·디자인·범위 등 9~13개 섹션을 갖춘 정형 문서 | 이미 승인된 기능을 **개발팀에 넘길 만큼 구체화**할 때 | [Atlassian Confluence](https://www.atlassian.com/software/confluence/templates/product-requirements), [Aha.io](https://www.aha.io/roadmapping/guide/requirements-management/what-is-a-good-product-requirements-document-template) |
| **Lean 원페이저 (Lean/One-Pager PRD)** | 문제정의·가치제안·**MVP** 범위·지표만 담은 1페이지 경량 문서 | 스타트업, 빠른 실험이 필요한 **작은 기능/가설 검증** | [Planio](https://plan.io/blog/one-pager-prd-product-requirements-document/), [IntelliSoft](https://intellisoft.io/product-requirements-document-prd-why-make-it-lean/) |
| **AI-네이티브 PRD** | ChatPRD 등 AI 도구가 초안을 자동 생성, 인간이 다듬는 방식. 2026년 기준 "고객 근거(customer evidence) 통합"이 핵심 차별점 | AI 코드 생성 도구에 바로 넘길 명세가 필요할 때 | [ChatPRD 2026 가이드](https://www.chatprd.ai/learn/prd-template) |

### 📋 대표 템플릿 3종 실제 구조 비교

**① Amazon PR/FAQ** — 두 파트로 구성:

| 파트 | 세부 항목 |
| --- | --- |
| **Press Release** | Heading(제품명) → Subheading(고객 편익) → Summary(요약) → Problem(문제, **TAM** 검증 포함) → Solution(해결책, 경쟁 차별점) → Quotes(회사·가상고객 인용) |
| **FAQ** | *External*: 가격/작동방식/구매처 등 고객 질문 / *Internal*: 경쟁 분석, **TAM**, 기술·법규 리스크, 단위경제성, 손익분기점 |

**② Atlassian Confluence PRD** — Project Overview(팀/일정/상태) → Objectives(조직 목표 연계) → Assumptions → Product Requirements(User Story + 우선순위 + Jira 연동) → Out of Scope

**③ Aha.io 9-섹션 표준형** — Overview → Objective → Context → Assumptions → Requirements → Design → Performance(성과지표) → Scope → Open Questions

**④ Product School/"Google식" 13-섹션형** (가장 상세) — Title/Change History → Overview → Success Metrics → Messaging → Timeline → Personas → User Scenarios → User Stories/Features → Features Out → Designs → Open Issues → Q&A → Other Considerations

### ✅ PRD 잘 쓰는 법 — 단계별 실전 가이드

1. **문제부터 써라 (Problem-first)**: 해결책이 아니라 문제를 먼저 정의한다.
   - ❌ 나쁜 예: "사용자에게 대량 내보내기(bulk export) 버튼이 필요하다" (이미 해결책)
   - ✅ 좋은 예: "사용자는 매주 20분씩 데이터를 리포트에 수동으로 복사하며 실수를 유발한다" (문제) → 이래야 "버튼"이 최선인지 다른 대안(자동 리포트 등)인지 팀이 판단할 수 있다.
2. **측정 가능한 성공 지표(KPI)를 반드시 정의하라** — "무엇을 성공으로 볼 것인가"가 없으면 출시 후 평가가 불가능하다.
3. **범위 외(Out-of-Scope)를 명시적으로 적어라** — 암묵적으로 남겨두면 스코프 크립(scope creep, 범위가 계속 늘어나는 현상)이 발생한다.
4. **How가 아닌 What에 집중하라** — 기술 구현 방법을 PRD에 못박으면 엔지니어의 창의성을 제한하고, PRD와 기술 명세서(**FRD**) 간 소유권 혼란이 생긴다.
5. **이해관계자와 함께 써라** — PM 혼자 완성해서 "던지는" 문서가 아니라, 디자인·개발·비즈니스와 공동 작성해야 일정 충돌을 예방한다.
6. **적정 무게의 템플릿을 골라라** — 작은 기능에 13-섹션 풀 PRD를 쓰면 과잉, 큰 신사업에 원페이저만 쓰면 부족하다. 위 표의 4유형 중 상황에 맞는 것을 선택한다.
7. **Living Document로 유지하라** — 개발 중 발견한 사실을 반영해 지속 갱신한다. 갱신을 멈추면 "PRD와 실제 제품이 다른" 상태가 된다.

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
| --- | --- | --- |
| ✅ 장점 | 단일 진실 공급원 | 제품/디자인/개발/마케팅이 "왜, 무엇을" 만드는지 하나의 문서로 정렬 |
| ✅ 장점 | 사후 분쟁 감소 | 범위·의사결정 기록(Q&A)이 있어 "누가 뭘 합의했는지" 추적 가능 |
| ✅ 장점 | 온보딩 자료화 | 신규 합류자가 제품 맥락을 빠르게 파악하는 참고 문서가 됨 |
| ❌ 단점 | 형식주의 위험 | 체크박스 채우듯 작성하면 "쓰는 행위" 자체가 목적이 되어버림 |
| ❌ 단점 | 유지보수 부담 | 갱신을 안 하면 곧 "오래된 거짓말" 문서가 되어 신뢰를 잃음 |
| ❌ 단점 | 검증 대체 오용 | "문서화 = 검증 완료"로 착각해 실제 고객 검증(discovery)을 생략하게 됨 |

### ⚖️ Trade-off 분석

```
경량(Lean 원페이저)   ◄──────── Trade-off ────────►   상세(표준 멀티섹션)
빠른 작성/낮은 오버헤드                    풍부한 컨텍스트/낮은 재작업 리스크
작은 기능/불확실성 높은 초기 아이디어 적합      큰 기능/여러 팀 조율 필요 시 적합
```

---

## 6️⃣ 인접 문서와의 차이 (Comparison with BRD/FRD/SRS)

PRD는 종종 **BRD**, **FRD**(또는 **FSD**), **SRS**와 혼동된다. 이들은 "같은 프로젝트의 다른 상세도/다른 독자층"을 겨냥한 문서다.

### 📊 비교 매트릭스

*(범례: BRD=Business Requirements Document / PRD=Product Requirements Document / FRD·FSD=Functional Requirements(Specification) Document / SRS=Software Requirements Specification)*

| 비교 기준 | BRD | PRD | FRD/FSD |
| --- | --- | --- | --- |
| 핵심 질문 | 왜(비즈니스 관점) | 무엇을(제품/사용자 관점) | 어떻게(시스템 동작 관점) |
| 주 작성자 | 비즈니스 분석가/경영진 | **PM** | 엔지니어/시스템 분석가 |
| 상세도 | 상위 수준 | 중간 | 매우 상세(로직·데이터 흐름·UI 동작 조건까지) |
| 작성 시점 | 프로젝트 승인 단계 | 제품 정의 단계 | 설계·구현 단계 |
| 주 독자 | 경영진, 이해관계자 | 디자인/개발/마케팅 팀 | 개발팀 |

### 🔍 핵심 차이 요약

```
BRD                       PRD                        FRD/FSD
──────────────    vs    ──────────────      vs    ──────────────────
"왜 이 사업을?"            "무엇을 만드나?"              "정확히 어떻게 동작하나?"
비즈니스 목표/ROI          기능·사용자 요구사항           로직 규칙, 검증 조건, UI 상태값
```

### 🤔 언제 무엇을 선택?

- **BRD**를 먼저 쓰세요 → 아직 "이 프로젝트를 할지 말지" 경영진 승인이 필요한 단계
- **PRD**를 쓰세요 → 프로젝트는 승인됐고, 제품/디자인/개발이 "무엇을 만들지" 정렬해야 하는 단계
- **FRD/FSD**를 쓰세요 → PRD가 확정됐고, 엔지니어가 상세 로직·API·화면 상태를 명세해야 하는 단계
- 참고로 대형 프로젝트는 **BRD→PRD→FRD** 세 문서를 순차적으로 다 쓰는 경우가 흔하다. ([dplooy 가이드](https://www.dplooy.com/blog/prd-vs-frd-vs-brd-complete-guide-2025-documents-templates-real-world-examples), [Plane Blog](https://plane.so/blog/brd-vs-prd-whats-the-difference-and-when-should-teams-use-each))

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| # | 실수 | 왜 문제인가 | 올바른 접근 |
| --- | --- | --- | --- |
| 1 | 해결책을 문제처럼 서술 | "대시보드가 필요하다"로 시작하면 그 해결책 하나로 팀 사고가 갇힘 | "CSM이 매주 리포트 취합에 4시간 쓴다"처럼 문제로 시작 |
| 2 | 체크박스 나열 | 모든 항목이 근거 없는 기능 목록이면 PRD가 아니라 로드맵 한 줄에 불과 | 각 요구사항에 "왜"라는 근거를 함께 적기 |
| 3 | 범위 외 미명시 | 암묵적으로 남겨두면 스코프 크립 발생 | Out-of-Scope 섹션을 명시적으로 채우기 |
| 4 | 성공 지표 부재 | 출시 후 무엇으로 성과를 판단할지 불명확 | 정량적 **KPI**를 목표 단계에서 미리 정의 |
| 5 | 문서 방치 | 개발 중 바뀐 내용을 반영 안 하면 실제 제품과 문서가 어긋남 | Living Document로 지속 갱신 |
| 6 | How를 PRD에 못박음 | 엔지니어의 최적 해법 탐색을 제한, FRD와 소유권 충돌 | "무엇을" 수준까지만 기술 |

### 🚫 Anti-Patterns

1. **문서로 검증을 대체하기**: PRD를 다 채웠다고 해서 고객 검증이 끝난 게 아니다. PRD는 "검증된 결정을 기록"하는 것이지, 검증 자체를 대신하지 않는다.
2. **승인용 세일즈 문서화**: "진실 추구(truth-seeking)"가 아니라 "승인 받기 위한 설득 문서"로 PRD를 쓰면, 나중에 잘못된 전제가 드러나도 고치기 어렵다 (아마존 PR/FAQ 철학이 강조하는 부분).

### 🔒 조직적 고려사항

- 이해관계자(디자인·마케팅·개발)와 사전 협의 없이 PRD를 완성하면, "일정을 맞출 수 없다"는 반발이 뒤늦게 나온다 — 초안 단계부터 리뷰를 끼워 넣을 것.
- ([Carlin Yuen, Medium](https://carlinyuen.medium.com/writing-prds-and-product-requirements-2effdb9c6def), [Product School](https://productschool.com/blog/product-strategy/product-template-requirements-document-prd))

---

## 8️⃣ PM이 알아둬야 할 것들 (Toolkit & Trends)

### 📚 학습 리소스

| 유형 | 이름 | 설명 |
| --- | --- | --- |
| 📖 공식 자료 | Working Backwards (Amazon 전 임원 저술) | PR/FAQ 프로세스의 원저작 가이드 |
| 📘 실무 가이드 | Atlassian Agile Coach | PRD 정의와 Confluence 템플릿 무료 제공 |
| 📘 블로그 | Reforge, Aha.io 로드맵 가이드 | 실무형 PRD 진화 사례 |
| 💬 뉴스레터 | Lenny's Newsletter | 실제 기업(Uber, Airbnb 등) PRD/원페이저 사례집(유료) |

### 🛠️ 관련 도구

| 도구 | 유형 | 용도 |
| --- | --- | --- |
| Confluence / Notion | 협업 문서 | 표준 멀티섹션 PRD 작성·공유 |
| Aha.io / Productboard | 제품관리 플랫폼 | 로드맵과 PRD 연동 |
| Jira / Linear | 이슈 트래커 | 승인된 요구사항을 티켓으로 분해 |
| **ChatPRD** 등 AI PRD 도구 | AI 코파일럿 | 최소 입력으로 초안 자동 생성, Notion/Slack/Linear 연동 |

### 🔮 트렌드 & 전망 (2026년 기준)

- **AI-네이티브 PRD 확산**: 2026년 기준 PM의 상당수가 AI 도구로 PRD 초안을 생성하지만, 단순 AI 산문이 아니라 **고객 통화·티켓 등 실제 근거(customer evidence)를 통합**할 수 있는지가 도구 선택의 핵심 기준이 되고 있다.
- **AI 코드 생성 도구용 PRD**: PRD가 사람뿐 아니라 AI 코딩 어시스턴트에게 바로 넘겨지는 명세로도 쓰이기 시작하면서, 모호성을 줄이는 정밀한 서술이 더 중요해지고 있다.
- ([ChatPRD 2026 가이드](https://www.chatprd.ai/learn/ai-for-product-managers))

### 💬 실무자 인사이트

- "PRD는 체크박스 가방이 아니다 — 모든 불릿포인트가 근거 없는 기능 목록이면, 그건 PRD가 아니라 로드맵 한 줄일 뿐이다" — 실무 PM 블로그 공통 지적
- "PRD는 검증된 결정을 담는 것이지, 발견(discovery) 과정을 대체하는 것이 아니다"

---

## 📎 Sources

1. [What is a Product Requirements Document (PRD)? — Atlassian](https://www.atlassian.com/agile/product-management/requirements) — 공식 벤더 가이드
2. [Product Requirements Document — ProductPlan Glossary](https://www.productplan.com/glossary/product-requirements-document) — 공식 벤더 가이드
3. [Product requirements document — Wikipedia](https://en.wikipedia.org/wiki/Product_requirements_document) — 백과사전
4. [PRD Templates: What To Include for Success — Aha.io](https://www.aha.io/roadmapping/guide/requirements-management/what-is-a-good-product-requirements-document-template) — 공식 벤더 가이드
5. [Working Backwards PR/FAQ Instructions & Template](https://workingbackwards.com/resources/working-backwards-pr-faq/) — 원저작 공식 자료
6. [Free PRD Template — Atlassian Confluence](https://www.atlassian.com/software/confluence/templates/product-requirements) — 공식 벤더 템플릿
7. [The Only PRD Template You Need — Product School](https://productschool.com/blog/product-strategy/product-template-requirements-document-prd) — 실무 교육기관 블로그
8. [PRD Template: Complete Guide for 2026 — ChatPRD](https://www.chatprd.ai/learn/prd-template) — AI 도구 벤더 블로그
9. [AI for Product Managers 2026 Guide — ChatPRD](https://www.chatprd.ai/learn/ai-for-product-managers) — AI 도구 벤더 블로그
10. [PRD vs FRD vs BRD Complete Guide — dplooy](https://www.dplooy.com/blog/prd-vs-frd-vs-brd-complete-guide-2025-documents-templates-real-world-examples) — 비교 가이드 블로그
11. [BRD vs PRD — Plane Blog](https://plane.so/blog/brd-vs-prd-whats-the-difference-and-when-should-teams-use-each) — 비교 가이드 블로그
12. [How to write a lean PRD — Planio](https://plan.io/blog/one-pager-prd-product-requirements-document/) — 실무 블로그
13. [How to Write a Lean PRD — IntelliSoft](https://intellisoft.io/product-requirements-document-prd-why-make-it-lean/) — 실무 블로그
14. [Writing PRDs and product requirements — Carlin Yuen, Medium](https://carlinyuen.medium.com/writing-prds-and-product-requirements-2effdb9c6def) — 개인 실무 블로그
15. [13x PRD Examples — Hustle Badger](https://www.hustlebadger.com/what-do-product-teams-do/prd-template-examples/) — 실무 사례 모음(내용 확인은 접근 제한으로 제목/스니펫만 참조)

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 12 (WebSearch), 심화 조사: 4 (WebFetch, 2건은 접근 제한으로 스니펫만 활용)
> - 수집 출처 수: 15개 이상, 교차 검증됨
> - 출처 유형: 공식/벤더 가이드 6, 실무 블로그 5, 비교 가이드 2, 백과사전 1, AI 도구사 블로그 2

---

## 🤝 추가로 확인하면 좋은 부분

- **회사 내부 표준이 이미 있다면 그것을 우선하세요** — 위 템플릿들은 일반화된 형식이며, 조직마다 관행(예: Jira 필드 연동 방식)이 다를 수 있습니다.
- **AI PRD 도구 도입을 고려 중이라면**, 단순 산문 생성이 아니라 실제 사용자 인터뷰·티켓 데이터를 근거로 통합하는지부터 확인하는 것을 권장합니다 — 이 부분이 2026년 기준 도구 간 품질 격차의 핵심입니다.
- 혹시 **특정 팀/제품(예: 사내 AI 기능, 신규 API 등)에 맞는 PRD 초안**이 필요하시면, 위 템플릿 중 어떤 것을 베이스로 실제로 작성해볼지 말씀해 주시면 구체적인 초안을 함께 잡아드릴 수 있습니다.
