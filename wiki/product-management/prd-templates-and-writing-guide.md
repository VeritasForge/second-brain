---
tags: [product-management, prd, requirements-document, templates, best-practices]
created: 2026-07-15
updated: 2026-07-23
---

# 📖 PRD (Product Requirements Document) — Concept Deep Dive

> 💡 **한줄 요약**: PRD는 "무엇을(What), 왜(Why), 누구를 위해(Who)" 만드는지를 제품·디자인·개발·비즈니스 팀이 공유하는 **단일 진실 공급원(Single Source of Truth)** 문서다.

> 🔗 실제 PRD를 리뷰·재작성하며 도출한 실전 체크리스트는 [[prd-writing-checklist]] 참고 (컴포넌트 명칭 사용 기준, 엔지니어링 용어 순화, recall/precision/accuracy 선택 기준, G/W/T 작성 기준 등).

### 📚 용어 범례 (Glossary) — 아래 약어는 문서 전체에서 반복 사용됩니다

| 약어 | 풀네임 | 의미 |
| --- | --- | --- |
| **PRD** | Product Requirements Document | 제품 요구사항 문서 |
| **PR/FAQ** | Press Release / Frequently Asked Questions | 아마존식 "가상 보도자료+예상질문" 문서 |
| **BRD** | Business Requirements Document | 비즈니스 요구사항 문서 (경영진·이해관계자 대상) |
| **FRD/FSD** | Functional Requirements/Specification Document | 기능 요구사항·명세 문서 (엔지니어 대상, 상세 로직) |
| **ERD** | Engineering Requirements Document | 기술 설계·아키텍처·구현을 다루는 문서 (FRD/FSD와 실질적으로 같은 역할군) |
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

아래 5가지는 서로 배타적인 "등급"이 아니라, **문서의 무게(얼마나 자세히 쓰는가)**와 **작성 시점(아이디어 단계 vs 실행 단계)**이라는 두 축으로 나뉜 스타일이다. 실무에서는 작은 기능은 원페이저로, 큰 기능은 표준 PRD로 섞어서 쓰는 경우가 많다.

| 유형 | 핵심 특징 | 적합한 상황 | 대표 출처 |
| --- | --- | --- | --- |
| **Amazon PR/FAQ** (Press Release/FAQ) | 아이디어를 "출시된 것처럼" 가상 보도자료+예상질문으로 먼저 쓴다. 고객 관점 강제. | 신제품/신사업처럼 **불확실성이 큰 초기 아이디어 검증** | [Working Backwards 공식 템플릿](https://workingbackwards.com/resources/working-backwards-pr-faq/) |
| **표준 멀티섹션 PRD** (Atlassian/Aha/Google식) | Overview·목표·요구사항·디자인·범위 등 9~13개 섹션을 갖춘 정형 문서 | 이미 승인된 기능을 **개발팀에 넘길 만큼 구체화**할 때 | [Atlassian Confluence](https://www.atlassian.com/software/confluence/templates/product-requirements), [Aha.io](https://www.aha.io/roadmapping/guide/requirements-management/what-is-a-good-product-requirements-document-template) |
| **Lean 원페이저 (Lean/One-Pager PRD)** | 문제정의·가치제안·**MVP** 범위·지표만 담은 1페이지 경량 문서 | 스타트업, 빠른 실험이 필요한 **작은 기능/가설 검증** | [Planio](https://plan.io/blog/one-pager-prd-product-requirements-document/), [IntelliSoft](https://intellisoft.io/product-requirements-document-prd-why-make-it-lean/) |
| **AI-네이티브 PRD** | ChatPRD 등 AI 도구가 초안을 자동 생성, 인간이 다듬는 방식. 2026년 기준 "고객 근거(customer evidence) 통합"이 핵심 차별점 | AI 코드 생성 도구에 바로 넘길 명세가 필요할 때 | [ChatPRD 2026 가이드](https://www.chatprd.ai/learn/prd-template) |
| **Figma식 3-섹션 (Problem/Solution Alignment)** | 자사의 Product Review 회의 3단계(문제→솔루션→출시준비)와 1:1로 대응하는 경량 구조. 문제 정의에 솔루션만큼 시간 투자 강조 | 애자일/디자인 중심 조직에서 **회의 프로세스와 문서를 결합**하고 싶을 때 | Figma PM 실무 사례 ([Coda/Superhuman](https://docs.superhuman.com/@yuhki/figmas-approach-to-product-requirement-docs)) |

### 🌡️ 템플릿 스펙트럼 (경량 ↔ 상세)

```
[Figma 3-섹션]   [Amazon PR/FAQ]   [Notion 5-속성]   [Atlassian 5-섹션]   [Aha.io 9-섹션]   [Product School 13-섹션]
   경량 ◄─────────────────────────────────────────────────────────────────────────────► 상세
 애자일/빠른     아이디어 검증        범용 최소       Jira 연동형          중견 조직 표준       엔터프라이즈/
 이터레이션       (초기 불확실성)      공통분모        (팀 협업 중심)       (성과지표 강조)       다부서 조율용
```

> 📌 섹션 수가 적다고 "가볍게 쓰라"는 뜻은 아니다 — Figma의 3섹션은 각각 별도 승인 회의와 결합되어 있어, 섹션 수와 실제 검토 강도는 별개다.

### 📋 목차 항목별 상세 가이드 — 무엇을, 얼마나 깊이 쓸 것인가

목차 항목 "이름"만 봐서는 실제로 뭘 써야 할지 판단하기 어렵다. 아래는 대표 템플릿 5종의 항목별로 **담을 내용 · 깊이 기준 · 필수/선택 여부 · 흔한 실수**를 정리한 것이다. 깊이 기준을 문장·단어 수까지 명시하는 곳은 Amazon PR/FAQ가 유일하며, 나머지는 "팀 성숙도에 맞게 유연하게"라는 정성적 가이드만 제공한다.

#### ① Amazon PR/FAQ

| 목차 항목 | 담을 내용 | 깊이 기준 | 필수/선택 | 흔한 실수 |
| --- | --- | --- | --- | --- |
| Heading | 고객이 이해할 제품명 | 정확히 1문장 | 필수 | 사내 용어로 작성해 고객이 못 알아봄 |
| Subheading | 고객이 얻을 편익 | 정확히 1문장 | 필수 | 기능 나열(구현 관점)로 써버림 |
| Summary | 발행 도시·언론사·출시일 + 제품 요약 | 1개 단락 | 필수 | 너무 길게 써서 "보도자료" 톤을 잃음 |
| Problem | 고객 관점의 문제, **TAM** 근거 | 1개 단락 | 필수 | "우리가 만들고 싶은 것"으로 문제를 왜곡 |
| Solution | 해결책, 경쟁사 대비 차별점 | 복잡한 제품일수록 1개 이상 단락 허용 | 필수 | 기술 구현 세부사항까지 침투 |
| Quotes & Getting Started | 회사 대변인 인용 1개 + 가상 고객 인용 1개 + 시작 방법 | 각 인용 1개씩 | 필수 | 인용문이 마케팅 카피처럼 공허함 |
| External FAQ | 기자·고객이 물을 질문(가격, 작동방식, 구매처) | 질문당 상세 답변 | 필수 | 답변을 얼버무려 실제 의사결정에 못 씀 |
| Internal FAQ | 재무/법무/운영 관점 리스크, **TAM**, 손익분기점 | "낙관적이지만 현실적" 톤 유지 | 필수 | 낙관 편향으로 리스크를 축소 서술 |

> ⏱️ 원문에 따르면 첫 초안은 "몇 시간" 안에 쓰지만, 최종 승인까지는 "수개월"이 걸린다 — 초안의 빠른 속도가 승인의 빠른 속도를 뜻하지 않는다. ([Working Backwards](https://workingbackwards.com/resources/working-backwards-pr-faq/))

#### ② Atlassian Confluence 5-섹션

| 목차 항목 | 담을 내용 | 깊이 기준 | 필수/선택 | 흔한 실수 |
| --- | --- | --- | --- | --- |
| Project Details | 출시일, 현재 상태, 핵심 팀원 | 표 1개 | 필수 | 담당자 불명확 → 책임소재 실종 |
| Objectives & Success Metrics | 조직 목표와의 연결 + 구체적 지표(예: "고객 만족도 15%↑") | 목표 문장 + 정량 지표 병기 | 필수 | 목표만 쓰고 측정 방법은 생략 |
| Assumptions & Options | 사용자/기술/비즈니스 가정 + 요구사항 표(User Story·중요도·Jira 이슈·노트) | 요구사항은 표 형식, 항목당 1행 | 필수 | 가정을 검증 계획 없이 "사실"처럼 서술 |
| Supporting Documentation | 목업, 다이어그램, 시각 설계 | 링크/임베드로 통합 (본문 장황화 지양) | 선택 | 텍스트로 UI를 장황하게 서술 |
| Open Questions & Out of Scope | 미해결 질문(질문+답변일자 추적) + 범위 외 명시적 나열 | 질문 목록형, Out of Scope는 불릿 | 필수 | Out of Scope를 아예 안 씀 → 스코프 크립 |

#### ③ Aha.io 9-섹션

Aha.io는 각 섹션을 정확히 한 문장으로 정의해두고 있어, 목차 항목별 담을 내용을 가장 명료하게 확인할 수 있다.

| 목차 항목 | 원문 정의 | 깊이 기준 | 필수/선택 | 흔한 실수 |
| --- | --- | --- | --- | --- |
| Overview | "기본 정보: 상태, 팀원, 출시일" | 짧게, 표 형태 권장 | 필수 | 목표까지 섞어 장황해짐 |
| Objective | "조직 목표·이니셔티브와의 전략적 정렬" | 1~2문장 | 필수 | 회사 전략 문구를 그대로 복붙 |
| Context | "고객 페르소나, 유스케이스, 경쟁 환경 등 팀의 깊은 이해를 돕는 보조 자료" | 팀 이해도에 맞게 가변적 | 선택 (신규 합류자 많을수록 비중↑) | 경쟁 분석을 생략해 "왜 지금"이 안 보임 |
| Assumptions | "긍정/부정 영향을 줄 수 있는 모든 것 + 검증 방법 + 알려진 의존성" | 가정마다 검증 계획 병기 | 필수 | 가정을 나열만 하고 검증 방법 누락 |
| Requirements | "무엇을 만들지의 세부사항 — 유저 스토리나 와이어프레임" | 요구사항 근거("왜") 병기 | 필수 | 근거 없는 기능 체크리스트로 전락 |
| Design | "제품의 룩앤필, 사용자 상호작용 방식" | 시각자료 위주, 텍스트 최소화 | 상황에 따라 선택 (UI 변경 없으면 생략 가능) | 디자인 결정을 텍스트로 장황 서술 |
| Performance | "성공 지표, 추적할 KPI" | 정량 지표 필수 명시 | 필수 | 정성적 목표("더 좋게")만 쓰고 수치 없음 |
| Scope | "이번 릴리스에 포함되지 않는 것" | 명시적 리스트 | 필수 | 암묵적으로 생략 → 스코프 크립 |
| Open Questions | "팀이 아직 답을 모르는 것" | 질문 형태로 나열 | 필수 | 질문을 숨기고 다 결정된 것처럼 포장 |

> 📌 Aha.io는 "구체적 분량보다 팀의 맥락과 조직 성숙도에 따라 유연하게 조정"할 것을 권장 — Amazon PR/FAQ의 엄격한 분량 규정과 정반대 철학이다. ([Aha.io](https://www.aha.io/roadmapping/guide/requirements-management/what-is-a-good-product-requirements-document-template))

#### ④ Product School/Google식 13-섹션

| 목차 항목 | 원문 정의 | 깊이 기준 | 필수/선택 | 흔한 실수 |
| --- | --- | --- | --- | --- |
| Title / Change History | 프로젝트명 + "누가/언제/무엇을 바꿨는지" | 변경 이력은 표로 누적 | 필수 | 변경 이력 누락 → 결정 배경 추적 불가 |
| Overview | "이 프로젝트는 무엇이고 왜 하는가" | 2~3문장 | 필수 | 목표·지표까지 섞어 서술 |
| Success Metrics | "내부 목표 달성을 나타내는 성공 지표" | 정량 KPI 목록 | 필수 | 섹션을 비워두고 "나중에" 처리 |
| Messaging | 마케팅이 고객에게 쓸 제품 메시징 | 문구 초안 수준 | 선택(내부 기능이면 생략) | PM이 마케팅 영역까지 확정해버림 |
| Timeline | 전체 일정 | 마일스톤 목록 | 필수 | 버퍼 없는 낙관적 일정만 기재 |
| Personas | 타깃 페르소나, 그중 핵심 페르소나 | **1~3개 권장** — "3개 넘으면 문제를 너무 많이 풀려는 것" | 필수 | 페르소나 4개 이상 → 초점 상실 |
| User Scenarios | 페르소나가 맥락 속에서 제품을 쓰는 전체 스토리 | 스토리텔링 형식(불릿 아님) | 필수 | 기능 나열을 스토리처럼 위장 |
| User Stories/Features | 우선순위화된 개별 기능 + "왜 중요한지" | 기능당 1줄 설명 + 근거 | 필수 | 근거 없이 기능만 나열 |
| Features Out | "명시적으로 하지 않기로 결정한 것과 이유" | 불릿 리스트 | 필수 | 이 섹션 자체를 생략 |
| Designs | 시각 자료(와이어프레임/목업) | 임베드/링크 | 상황에 따라 선택 | 디자인 없이 텍스트만으로 UI 설명 |
| Open Issues | "아직 답을 못 찾은 요인" | 질문 목록 | 필수 | 이슈를 숨기고 완성된 것처럼 포장 |
| Q&A | 자주 나오는 질문 + 결정된 답 | Q-A 페어 | 선택(리뷰 중 자연 축적) | 리뷰 중 질문 기록 안 해 같은 질문 반복 |
| Other Considerations | 위 항목에 안 들어가는 기타 사항 | 자유 형식 | 선택 | 핵심 요구사항을 몰래 여기에 숨김 |

> 📌 원문은 **"미확정 항목은 TBD(추후 결정) 플레이스홀더로 남겨도 된다"**고 명시 — 가장 상세한 템플릿조차 초안 단계의 불완전함을 공식 허용한다. 완벽주의로 초안을 미루는 실수를 막기 위한 장치다. ([Product School](https://productschool.com/blog/product-strategy/product-template-requirements-document-prd))

#### ⑤ Figma 3-섹션 (가장 애자일한 최신 구조)

Figma는 자사의 3단계 Product Review 회의와 1:1로 대응하는 3섹션 구조를 쓴다.

| 목차 항목 | 담을 내용 | 깊이 기준 | 필수/선택 | 흔한 실수 |
| --- | --- | --- | --- | --- |
| Problem Alignment | 문제 진술 + High-level Approach(범위·솔루션 개요) + 사용자가 "생각·느끼길·행동하길" 바라는 것 | "솔루션 정의만큼 문제 정의에도 시간을 써라" — 원문 강조 | 필수 | 문제 정의를 대충 쓰고 바로 솔루션으로 직행 |
| Solution Alignment | 핵심 기능 + 사용자 플로우(User Flow), Figma 파일 임베드로 최신 디자인 유지 | "User Flow가 독자가 프로젝트를 이해하는 가장 쉬운 방법" | 필수 | 기능 목록만 나열, 플로우(맥락) 생략 |
| Launch Readiness | 법무/마케팅 등 전 부서가 출시 전 확인할 체크리스트 | 체크리스트 형식 | 필수 | 출시 직전에야 타부서 이슈 발견 |

> 📌 섹션이 3개뿐이라 가벼워 보이지만, 각 섹션이 Product Review라는 조직 프로세스와 결합되어 하나의 승인 게이트 역할을 한다. ([Coda/Superhuman, Figma PM 실무 블로그](https://docs.superhuman.com/@yuhki/figmas-approach-to-product-requirement-docs))

### 🔗 템플릿 간 공통 요소 매핑 (Notion 5-속성 기준)

Notion 공식 가이드는 특정 템플릿이 아니라, **모든 PRD가 공유하는 5가지 속성**을 정의한다.

> 원문: *"Typically, all PRDs will share the same 5 attributes: 1. Context 2. Goals or Requirements 3. Constraints 4. Assumptions 5. Dependencies"* ([Notion 공식 가이드](https://www.notion.com/help/guides/building-a-product-requirement-document-in-notion))

이 5개는 위 템플릿들에 **다른 이름으로** 흩어져 있다 — 아래는 이름이 달라도 실제로는 같은 개념임을 보여주는 매핑이다.

| 공통 요소 (Notion 기준) | Amazon PR/FAQ | Atlassian | Aha.io | Product School | Figma |
| --- | --- | --- | --- | --- | --- |
| Context(배경) | Problem 단락 | Project Details | Context | Overview | Problem Alignment |
| Goals/Requirements | Solution 단락 | Requirements | Requirements | User Stories/Features | Solution Alignment |
| Constraints | Internal FAQ | Assumptions 표 | Assumptions | Features Out | Launch Readiness |
| Assumptions | Internal FAQ | Assumptions | Assumptions | (암묵적, Open Issues에 흡수) | Problem Alignment |
| Dependencies | Internal FAQ | Open Questions | Open Questions | Open Issues | Launch Readiness |

> 📌 "Assumptions/Dependencies/Open Questions"는 사실상 하나의 **리스크 관리 축**을 템플릿마다 다른 이름으로 쪼개놓은 것이다. 이름이 다르다고 다른 개념이 아니라는 점을 알아두면 템플릿 간 전환 시 혼동이 줄어든다.

### 💡 실무자 버전: 섹션마다 깊이를 다르게 (Alex Debecker 사례)

벤더 템플릿이 아닌 현직 PM의 실제 운영 사례. 핵심은 **섹션마다 상세도를 의도적으로 다르게** 가져간다는 것이다.

```
요약(1단락)  <  릴리스 계획(3개 하위섹션)  <  기회/피치(5개 하위섹션)  <  솔루션(6개 하위섹션, 최상세)
```

- **가장 얕게**: 요약(리소스·상태·출시목표만)
- **가장 깊게**: 솔루션 섹션 — Proposed solution/Key features/Complexity/Assumptions/Budget/Out-of-scope 6개 하위 항목
- **조건부 생략**: 경쟁사 리서치는 "내부 기능이면 비워둘 수 있다"고 원문에 명시
- **사후 작성 전용**: 회고 섹션은 "프로젝트 완료 후에만" 작성 ([Alex Debecker, Substack](https://alexdebecker.substack.com/p/how-i-organise-my-prds))

> 💡 이 사례가 주는 시사점: **"모든 섹션을 균등한 깊이로 쓰지 마라"** — 벤더 템플릿에는 없는, 실무에서만 확인되는 암묵적 규칙이다.

### ✅ PRD 잘 쓰는 법 — 단계별 실전 가이드

1. **문제부터 써라 (Problem-first)**: 해결책이 아니라 문제를 먼저 정의한다.
   - ❌ 나쁜 예: "사용자에게 대량 내보내기(bulk export) 버튼이 필요하다" (이미 해결책)
   - ✅ 좋은 예: "사용자는 매주 20분씩 데이터를 리포트에 수동으로 복사하며 실수를 유발한다" (문제) → 이래야 "버튼"이 최선인지 다른 대안(자동 리포트 등)인지 팀이 판단할 수 있다.
2. **측정 가능한 성공 지표(KPI)를 반드시 정의하라** — "무엇을 성공으로 볼 것인가"가 없으면 출시 후 평가가 불가능하다.
3. **범위 외(Out-of-Scope)를 명시적으로 적어라** — 암묵적으로 남겨두면 스코프 크립(scope creep, 범위가 계속 늘어나는 현상)이 발생한다.
4. **How가 아닌 What에 집중하라** — 기술 구현 방법을 PRD에 못박으면 엔지니어의 창의성을 제한하고, PRD와 기술 명세서(**FRD**) 간 소유권 혼란이 생긴다.
5. **이해관계자와 함께 써라** — PM 혼자 완성해서 "던지는" 문서가 아니라, 디자인·개발·비즈니스와 공동 작성해야 일정 충돌을 예방한다.
6. **적정 무게의 템플릿을 골라라** — 작은 기능에 13-섹션 풀 PRD를 쓰면 과잉, 큰 신사업에 원페이저만 쓰면 부족하다. 위 표의 5유형 중 상황에 맞는 것을 선택한다.
7. **Living Document로 유지하라** — 개발 중 발견한 사실을 반영해 지속 갱신한다. 갱신을 멈추면 "PRD와 실제 제품이 다른" 상태가 된다.
8. **섹션마다 깊이를 균등하게 배분하지 마라** — 핵심 섹션(문제 정의, 솔루션)에 더 많은 시간과 분량을 쓰고, 부차적 섹션(경쟁사 리서치, 메시징 등)은 상황에 따라 가볍게 쓰거나 생략한다. Figma는 "솔루션 정의만큼 문제 정의에도 시간을 써라"고 강조하며, 실무 PM들은 섹션별 하위 항목 개수를 의도적으로 차등화한다.

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

### 🤖 AI/Agent 제품 특수 원칙 — 성능 임계치·Guardrail은 예외적으로 What

전통적인 What/How 경계(PRD=What, FRD/**ERD**=How)는 AI·Agent 제품에서 한 가지 예외를 가진다. **AI는 확률적(probabilistic)이라 "입력 A → 항상 출력 B"가 성립하지 않으므로, "얼마나 정확해야 성공인가"라는 성능 임계치 자체가 구현 디테일이 아니라 제품 결정이 된다.**

> *"The eval framework **becomes** your acceptance criteria — it defines the target, measures pass or fail, tracks improvement, and prevents regression."*
> *"Guardrails are not a post-launch safety patch; they belong in the PRD from day one."*
> — [Ainna AI PRD Guide](https://ainna.ai/resources/faq/ai-prd-guide-faq)

#### 🧭 경계 재설정 — 무엇이 What으로 남고, 무엇이 How로 옮겨가는가

| 항목 | PRD (What) | 기술 설계 문서 / **ERD** (How) |
| --- | --- | --- |
| 성능 임계치 (예: "분류 정확도 90% 이상이어야 파일럿 통과") | ✅ 남음 | |
| 에스컬레이션 트리거 (예: "모호한 입력이 감지되면 사람에게 확인받는다") | ✅ 남음 | |
| 그 임계치를 계산하는 라벨링 스키마·평가 파이프라인 단계 | | ✅ 이동 |
| 에스컬레이션 판단을 위한 내부 상태 추적·데이터 모델 로직 | | ✅ 이동 |

- **왜 임계치는 What인가**: 전통 소프트웨어는 QA가 "버그냐 아니냐"를 기술적으로 판정하면 되지만, AI는 애초에 "정답의 범위"가 확률적이라 그 범위(임계치)를 정하는 것 자체가 제품이 감수할 리스크 수준을 결정하는 행위다.
- **왜 트리거는 What인가**: "언제 시스템이 자동으로 처리하고, 언제 사람에게 넘기는지"는 사용자가 체감하는 경험을 직접 좌우하는 결정이라 Guardrail(가드레일 — AI가 하면 안 되는 행동의 경계 및 에스컬레이션 조건)로 분류되며, 구현 디테일이 아니다.
- **판단 기준 한 줄**: *숫자나 조건이 등장해도, 그것이 "제품의 성공/실패 기준"이거나 "사용자 경험 결정"이면 PRD, 그걸 만족시키는 내부 메커니즘이면 ERD.*

> 💡 **ERD**는 위 비교 매트릭스의 **FRD/FSD**와 실질적으로 같은 역할군이다 — 회사마다 Design Doc·Tech Spec·TCD(Technical Coordination Document) 등 다른 이름으로 부를 뿐, "PRD가 확정한 What을 어떻게 구현할지"를 다룬다는 본질은 동일하다.

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
| 7 | 타부서 영향(의존성) 누락 | 전통적 제품개발 관점에만 매몰되어 다른 부서·시스템에 미치는 파급효과를 놓침 | Launch Readiness 체크리스트나 Internal FAQ처럼 타부서 확인을 강제하는 섹션을 별도로 둘 것 |

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
16. [Product Requirements Document: What Is It & How To Write It — Reforge Blog](https://www.reforge.com/blog/product-requirement-document-prd-templates) — 실무 교육기관 블로그
17. [Building a product requirement document in Notion — Notion 공식 가이드](https://www.notion.com/help/guides/building-a-product-requirement-document-in-notion) — 공식 벤더 가이드
18. [Figma's approach to modern PRDs — Coda/Superhuman](https://docs.superhuman.com/@yuhki/figmas-approach-to-product-requirement-docs) — Figma PM 실무 블로그
19. [3 Most Common Mistakes in PRDs — twocentspm, Substack](https://twocentspm.substack.com/p/3-most-common-mistakes-in-product) — 실무 PM 블로그
20. [How I Organise My PRDs — Alex Debecker, Substack](https://alexdebecker.substack.com/p/how-i-organise-my-prds) — 실무 PM 블로그 (단일 출처, 참고용)
21. [How to write a PRD that engineers actually read — Plane Blog](https://plane.so/blog/how-to-write-a-prd-that-engineers-actually-read) — PRD/ERD(기술 설계 문서) 경계, 리스크 기반 문서 크기 결정 원칙
22. [How Do You Write a PRD for AI Products? — Ainna](https://ainna.ai/resources/faq/ai-prd-guide-faq) — AI/Agent 제품의 성능 임계치·Guardrail이 예외적으로 PRD의 What에 속하는 이유

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 21 (WebSearch, 최초 12 + 2차 조사 7 + 3차 조사 2), 심화 조사: 15건 (WebFetch/Playwright, 최초 4 + 2차 9 + 3차 2, 1건은 Cloudflare 403 → Playwright MCP로 우회)
> - 수집 출처 수: 22개 이상, 교차 검증됨
> - 출처 유형: 공식/벤더 가이드 8, 실무 교육기관 블로그 9, 개인 실무 블로그 4, 백과사전 1
> - 2차 조사(2026-07-22): Aha.io/Atlassian/Product School/Working Backwards 원문 섹션별 정의 재확인 + Reforge/Notion/Figma(Coda)/실무자 블로그 2건 신규 발굴
> - 3차 조사(2026-07-22): 실제 사내 PRD 리뷰 과정에서 도출된 "AI/Agent 제품의 PRD-ERD 경계" 질문을 계기로 Plane Blog/Ainna 가이드 검증 — 성능 임계치·Guardrail 트리거가 What에 속하는 예외 원칙 확인

---

## 🤝 추가로 확인하면 좋은 부분

- **회사 내부 표준이 이미 있다면 그것을 우선하세요** — 위 템플릿들은 일반화된 형식이며, 조직마다 관행(예: Jira 필드 연동 방식)이 다를 수 있습니다.
- **AI PRD 도구 도입을 고려 중이라면**, 단순 산문 생성이 아니라 실제 사용자 인터뷰·티켓 데이터를 근거로 통합하는지부터 확인하는 것을 권장합니다 — 이 부분이 2026년 기준 도구 간 품질 격차의 핵심입니다.
- 혹시 **특정 팀/제품(예: 사내 AI 기능, 신규 API 등)에 맞는 PRD 초안**이 필요하시면, 위 템플릿 중 어떤 것을 베이스로 실제로 작성해볼지 말씀해 주시면 구체적인 초안을 함께 잡아드릴 수 있습니다.
