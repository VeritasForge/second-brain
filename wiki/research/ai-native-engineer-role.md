---
tags: [ai-native-engineer, career, job-role, claude-code, ai-agent, hiring-trends]
created: 2026-05-26
---

# AI Native Engineer 직군 완전 해부

## 📋 Executive Summary

**AI Native Engineer**는 코드를 직접 타이핑하는 사람이 아니라, **AI 코딩 에이전트(Claude Code, Cursor, Codex 등)를 핵심 인프라로 오케스트레이션하여 소프트웨어를 빌드하는 엔지니어**입니다. 모델을 만드는 ML Engineer도, 모델을 호출해서 앱을 만드는 AI Engineer도 아닌, **"에이전트 부대를 지휘하는 설계자/편집자(architect & editor)"** 역할입니다. 2025년 후반~2026년 초부터 무신사·그루우·Sionic AI 같은 한국 기업도 공식 채용을 시작했고, 글로벌 시장에서는 일반 AI Engineer보다 20~30% 더 높은 연봉을 받는 추세입니다 🟡.

---

## 🔍 Findings

### 1️⃣ 정의: "AI를 만드는 사람"이 아니라 "AI로 만드는 사람"

> 12살 비유 🧒
> - **ML Engineer** = 자동차 공장에서 **엔진을 설계하는 사람** (모델을 만듦)
> - **AI Engineer** = 그 엔진을 **차에 장착해서 자동차를 조립하는 사람** (모델을 호출해서 앱 빌드)
> - **AI Native Engineer** = **로봇 부대에게 "이런 차를 만들어줘"라고 지시하고, 로봇이 만든 차를 검수하는 감독** (에이전트를 오케스트레이션해서 빌드 자체를 자동화)

원문 인용 (Howdy, 2026):

> *"AI-native engineering is an operating model where AI agents participate across the full software development lifecycle (SDLC) with standardized inputs (specs + context), scoped permissions, and verification gates."*

원문 인용 (Agentic Engineering Jobs):

> *"AI-native engineering is the practice of building software by orchestrating AI coding agents as primary development infrastructure — not optional tooling."*

- ✅ **확신도**: [Confirmed] — 3개 독립 출처(Howdy, Augment Code, Agentic Engineering Jobs)에서 원문 일치
- **핵심 통찰**: 병목이 역전되었습니다 — 과거에는 "코드 작성"이 느리고 "리뷰"가 빨랐지만, AI Native 환경에서는 **"코드 생성은 순식간, 인간의 판단이 새 병목"**

---

### 2️⃣ 기존 직군과의 차이 — 한눈에 보는 비교표

| 차원                | ML Engineer            | AI Engineer                       | AI Native Engineer                                  |
| ------------------- | ---------------------- | --------------------------------- | --------------------------------------------------- |
| **무엇을 만드는가** | 모델 자체              | 모델을 쓰는 앱                    | **소프트웨어 (모든 것)**                            |
| **핵심 활동**       | 데이터 전처리, 학습, 튜닝 | API 호출, RAG, 프롬프트 엔지니어링 | **에이전트 오케스트레이션, 검증**                   |
| **주요 도구**       | PyTorch, TensorFlow, MLflow | OpenAI/Anthropic API, LangChain   | **Claude Code, Cursor, Codex**                      |
| **수학/통계 요구도**| 높음                   | 중간                              | **낮음 (대신 시스템 설계 요구도 매우 높음)**        |
| **진입 학습 기간**  | 6~12개월+ (PhD 선호)   | 3~6개월                           | **소프트웨어 엔지니어가 빠르게 전환 가능**          |
| **메인 산출물**     | `model.pkl`            | `app.py` (API call)               | `CLAUDE.md`, 시스템 프롬프트, 검증 파이프라인       |
| **멘탈 모델**       | 연구자                 | 통합자                            | **장인(craftsperson) → 설계자(architect)**          |

- ✅ **확신도**: [Confirmed] — IIT Kharagpur, Towards Data Science, Second Talent, Augment Code에서 일치
- **출처**: Augment Code 블로그 명시 표현 *"from craftsperson to architect — from typing to thinking"*

---

### 3️⃣ 6가지 핵심 역량 (Augment Code 채용 프레임워크)

Augment Code가 공개한 **AI-Native 엔지니어 6대 평가 차원** (원문 직접 확인 완료):

> 💡 **Augment Code란 어떤 회사인가?** (이 프레임워크의 출처)
>
> 이 6대 역량을 만든 **Augment Code**는 **대규모·복잡한 코드베이스에 특화된 AI 코딩 에이전트** 제품/회사입니다 (Cursor·Claude Code와 같은 카테고리).
>
> - **핵심 기술 — Context Engine**: 키워드/정적 검색을 넘어선 **시맨틱(의미 기반) 코드 검색**. 🧒 일반 AI 도구가 "포스트잇 한 장 보고 답하는 친구"라면, Augment는 **"도서관 전체를 외운 사서"** — 함수 하나를 고쳐도 코드베이스 전체의 연관성을 파악해 "여기 고치면 저기서 터진다"까지 알려줌.
> - **타겟 시장**: 200~500명 규모 개발 조직의 문제 (아키텍처 추론, 에이전트 간 공유 메모리).
> - **2026 신제품**: ① **Intent** (macOS 멀티 에이전트 오케스트레이션 앱 — Coordinator가 작업을 쪼개 병렬 전문 에이전트에 위임) ② **Context Engine MCP** (Cursor·Claude Code 등 모든 MCP 클라이언트에서 사용 가능하게 개방).
> - **차별점**: **ISO/IEC 42001 인증을 받은 최초의 AI 코딩 어시스턴트** + SOC 2 Type II.
>
> **왜 이 출처가 신뢰할 만한가**: "AI 에이전트로 코드를 다루는 도구"를 파는 회사라, 스스로가 "에이전트를 잘 부리는 엔지니어"를 가장 절박하게 뽑아야 하는 입장 — *칼 만드는 대장장이가 쓴 검술 채용 기준*인 셈. **단, 자사 제품 홍보 맥락**이 깔려 있어 정의 인용 시 마케팅 편향 가능성은 감안해야 함.

```
┌──────────────────────────────────────────────────────────┐
│   AI-Native Engineer Competency Dimensions                │
├──────────────────────────────────────────────────────────┤
│                                                            │
│   ┌─────────────────────┐   ┌──────────────────────┐     │
│   │ 1. Product Taste    │   │ 2. System Judgment   │     │
│   │  "올바른 걸 만드나?" │   │  "프로덕션 견디나?"  │     │
│   └─────────────────────┘   └──────────────────────┘     │
│                                                            │
│   ┌─────────────────────┐   ┌──────────────────────┐     │
│   │ 3. Agent Leverage   │   │ 4. Communication     │     │
│   │  "AI → 처리량 변환" │   │  "의도 전달 능력"    │     │
│   └─────────────────────┘   └──────────────────────┘     │
│                                                            │
│   ┌─────────────────────┐   ┌──────────────────────┐     │
│   │ 5. Ownership        │   │ 6. Learning Velocity │     │
│   │  "결과를 주도하나?" │   │  "도구만큼 빨리 진화"│     │
│   └─────────────────────┘   └──────────────────────┘     │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

위 다이어그램은 한눈 요약이고, 각 역량을 원문 기준으로 풀어보면 다음과 같습니다.

#### 역량별 상세

**1. Product & Outcome Taste (제품 감각·결과 지향)** — *"올바른 걸 만드나?"*

- **의미**: 코드 생산 비용이 싸질수록 가장 비싼 실수는 **잘못된 것을 만드는 것**. 구현 전에 사용자 문제를 조사하고, 모호함을 해결하며, 명확한 결과를 먼저 정의해야 함.
- 💬 *"가장 영향력 있는 엔지니어는 가장 많은 코드를 작성하는 사람이 아니다. 팀이 올바른 문제를 풀게 하는 사람이다."*
- ✅ 구현 전 문제의 경계를 명확히 함 ❌ 무작정 코딩부터 시작

**2. System & Architectural Judgment (시스템·아키텍처 판단)** — *"프로덕션에서 견디나?"*

- **의미**: 에이전트는 "작동하는 코드"는 잘 만들지만, **주변 시스템이 건전한지** 판단하는 데는 덜 신뢰할 수 있음. 장기 트레이드오프, 운영 현실, 규모 확대 시 드러나는 숨은 위험을 이해해야 함.
- 💬 *""작동한다"는 쉽다. "프로덕션에서 계속 작동할 것이다"는 훨씬 어렵다."*
- ✅ 단기 해결책의 장기 비용을 우려 ❌ "일단 작동하면 충분" 태도

**3. Agent Leverage (에이전트 활용)** — *"AI를 처리량으로 전환하나?"*

- **의미**: 에이전트를 단순 보조 도구로 쓰는 게 아니라, **에이전트가 잘 실행하도록 문제를 구조화**하고, 이탈하면 가이드하며, 산출물을 검증하는 능력.
- 💬 *"Like delegation — except the reports are very fast and sometimes confidently wrong."* (위임과 같다 — 다만 보고서가 엄청 빠르고 때론 자신감 있게 틀린다)
- ✅ AI 결과를 비판적으로 검토 ❌ AI 출력을 무조건 수용

**4. Communication & Collaboration (소통·협업)** — *"의도를 명확히 전달하나?"*

- **의미**: 구현 속도가 빨라질수록 **문제 명확화·트레이드오프 제시·팀 피드백 통합**의 비중이 커짐. 명확히 말하고, 잘 듣고, 공유 이해를 빠르게 구축해야 함.
- 💬 *"가장 빠른 팀은 가장 빠르게 코딩하는 팀이 아니다 — 가장 빠르게 명확성에 도달하는 팀이다."*
- ✅ 복잡한 설계 결정을 간단히 설명 ❌ 모호한 요구사항을 명확히 하지 않음

**5. Ownership & Leadership (소유권·리더십)** — *"결과를 주도하나?"*

- **의미**: 자기 코드 조각만이 아니라 **전체 결과를 소유**함. 진행을 막는 것(느린 빌드, 불명확한 워크플로, 시스템 간 갭)이 있으면 **범위 밖이라도 개입**해 제거함.
- 💬 *"소유권은 팀과 결과 사이의 모든 장애물을 제거하는 것을 의미한다."*
- ✅ "이건 내 일이 아니야"라고 하지 않음 ❌ 책임을 외부에 돌림

**6. Learning Velocity & Experimental Mindset (학습 속도·실험 정신)** — *"도구만큼 빨리 진화하나?"*

- **의미**: 오늘 쓰는 도구가 3개월 뒤엔 달라짐. 끊임없이 실험하고, 워크플로를 빠르게 바꾸고, 더 나은 방법이 나오면 **기존 방식을 미련 없이 버림**.
- 💬 *"실험은 한 단계가 아니다. 지금이 곧 일이다(Experimentation isn't a phase. It's the job now)."*
- ✅ 새 도구 채택을 주도 ❌ "우리는 항상 이렇게 해왔다"

#### 🎤 어떻게 평가하나 (면접 신호)

원문이 밝힌 핵심 평가 질문 3가지 — 코드를 빨리 짜는지가 아니라 **판단력**을 본다:

1. "후보자가 **모호한 문제를 빠르게 명확히** 할 수 있는가?"
2. "**아키텍처 위험**을 프로덕션에 드러나기 전에 인식하는가?"
3. "**AI 생성 작업을 효과적으로 지시·검증**할 수 있는가?"

#### 🧭 4가지 채용 프로필 (역량 가중치가 다름)

원문은 *"각 프로필이 6가지 역량을 다르게 가중치하며, 가장 중요한 신호를 중심으로 면접 루프를 구성한다"*고 명시합니다.

| 프로필                            | 가장 중요한 역량                | 원문 설명                                                                            |
| --------------------------------- | ------------------------------- | ------------------------------------------------------------------------------------ |
| **AI-Native Systems Engineer**    | System & Architectural Judgment | "강력한 아키텍처 판단과 깊은 인프라 직관. 에이전트가 위에서 더 빠르게 구축해도 기초를 건전하게 유지" |
| **AI-Native Product Engineer**    | Product & Outcome Taste         | "강력한 제품 감각과 사용자 공감. 올바른 문제를 정의하고 중요한 결과를 향해 반복"      |
| **AI-Native Applied AI Engineer** | (모델 이해 + Agent Leverage)    | "모델의 깊은 이해와 그 위에 효과적으로 구축하는 법. 에이전트·워크플로 역량 개선 책임" |
| **AI-Native Early Professional**  | Learning Velocity               | "학습 속도가 무엇보다 중요. 에이전트-우선으로 성장하고 도구·워크플로 변화에 빠르게 적응" |

> 💡 **백엔드 배경(Python/FastAPI/Celery)이라면**: 시스템 사고가 강점이므로 **AI-Native Systems Engineer** 프로필에 가장 자연스럽게 들어맞습니다. 면접 루프도 "아키텍처 위험을 프로덕션 전에 짚어내는가(2번 역량)"에 무게가 실릴 가능성이 높습니다.

- ✅ **확신도**: [Confirmed] — Augment Code 공식 채용 블로그 원문 (6대 역량 정의·인용구·평가 신호·4프로필 모두 WebFetch로 원문 직접 확인)

---

### 4️⃣ 구체적 일상 업무 (Howdy 정의의 "Agent Wrangler" 역할)

| 업무 카테고리             | 구체 활동                                                       | 산출물                              |
| ------------------------- | -------------------------------------------------------------- | ----------------------------------- |
| **🧩 Task Decomposition** | 사람이 작성할 작업 → 에이전트가 한 번에 처리 가능한 단위로 쪼개기 | 작업 그래프, 계획 문서              |
| **📝 Context Curation**   | 어떤 파일/문서/예시를 에이전트 컨텍스트에 넣을지 결정           | `CLAUDE.md`, 시스템 프롬프트, ADR   |
| **🛡️ Harness Design**     | 에이전트 출력을 검증하는 CI 게이트, 타입체크, 테스트 자동화     | 검증 파이프라인, 가드레일           |
| **🔍 Verification Ownership** | 라인별 코드리뷰가 아닌 **동작 의도 일치도** 평가             | 통과/탈락 기준                      |
| **⚠️ Intervention**       | "그럴듯하지만 틀린(plausible-but-wrong)" 출력 감지하고 개입     | 수정 지시, 재실행                   |

- ✅ **확신도**: [Confirmed] — Howdy, Augment Code, Agentic Engineering Jobs 모두 동일 활동 명시

---

### 5️⃣ 한국 시장 현황 (2026년 5월 기준) 🇰🇷

| 회사               | 발표/공고 시점         | 채용 방식                                              | 명시된 자격요건 (원문)                                                                                                       |
| ------------------ | ---------------------- | ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| **무신사**         | 2026-01-16             | 6개월 인턴 → 정규직 전환, "이력서 없는 간편 지원"        | "AI 기술로 핵심 업무를 해결하고 시스템 효율화를 주도할 AI 네이티브 인재"                                                    |
| **그루우 (Greum)** | 상시채용 (경력 1-7년)  | 3개월 수습 (신입 6개월)                                 | **"Claude Code, Codex, opencode 등 AI 코딩 도구로 실제 결과물을 만들어본 경험"**, **"컨텍스트 엔지니어링과 하네스 엔지니어링의 경계를 이해"** |
| **GroupBy**        | 경력 채용              |  \-                                                     | "Software Engineer (AI Native)" 명시                                                                                        |
| **Sionic AI**      | 상시                   |  \-                                                     | AI Native 직군 채용 (그리팅 채용 페이지)                                                                                    |

> 💡 **주목할 점**: 그루우의 자격요건은 **"AI Native"의 정의를 가장 구체적으로 명문화**한 한국 사례입니다. 단순히 "AI 도구를 잘 쓴다"가 아니라 **"컨텍스트 엔지니어링과 하네스 엔지니어링의 경계를 이해한다"**고 적시한 것은, Augment Code/Agentic Engineering Jobs의 글로벌 정의와 거의 동일한 표현입니다.

> 🏢 **무신사 맥락**: CTO 전준희가 직접 발표한 4년 만의 주니어 대규모 공채입니다. "AI를 도구로 활용해 패션 생태계 혁신을 이끌 주니어 개발자"가 핵심 메시지.

- ✅ **확신도**: [Confirmed] — 무신사 뉴스룸 원문 + 원티드 채용공고 원문 직접 확인

---

### 6️⃣ 연봉 수준

| 시장                  | 직군                              | 연봉 (2026)                                  |
| --------------------- | --------------------------------- | -------------------------------------------- |
| 🇺🇸 미국 (글로벌)      | AI Engineer 중위값                | $150K~$165K base                             |
| 🇺🇸 미국 (글로벌)      | AI Engineer Senior 총보상         | $200K~$312K+                                 |
| 🇺🇸 미국 (글로벌)      | **AI Native Engineer 프리미엄**   | **일반 AI Engineer 대비 +20~30%** 🟡         |
| 🇮🇳 인도               | AI Native 신입                    | ₹10~18 LPA (약 1.6~3억 원 환산 가치)         |
| 🇰🇷 한국               |  \-                                | **개별 공고에 미공개**, 일반 시니어 SWE 시장가 + AI 프리미엄 추정 |

- 🟡 **확신도**: [Likely] — 20~30% 프리미엄 수치는 IIT Kharagpur 단일 출처. 그러나 KORE1/Built In 등에서 "AI Native 스킬은 시장에서 supply 대비 demand가 높다"는 정성적 진술은 다수 확인됨
- **출처**: KORE1 AI Engineer Salary 2026, Built In, IIT Kharagpur

---

## 📊 어떤 사람이 AI Native Engineer로 적합한가?

```
              [ 적합도 매트릭스 ]

  높은 시스템 사고  ┃              ⭐ AI Native Engineer
                    ┃          (백엔드 SWE + 아키텍처 + 에이전트 활용)
                    ┃
                    ┃    ⚪ AI Engineer
                    ┃   (API 호출, RAG)
                    ┃
                    ┃   🔵 ML Engineer
                    ┃   (수학/통계 강점)
                    ┃
  낮은 시스템 사고  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    낮은 에이전트 활용   →    높은 에이전트 활용
```

**Python/FastAPI/Celery 백엔드 배경에서 유리한 포인트** 🎯:

- ✅ 백엔드 시스템 사고력은 이미 강점 → "System & Architectural Judgment" 차원 충족
- ✅ Celery 같은 비동기/오케스트레이션 경험 → 에이전트 워크플로우 설계로 자연스럽게 확장
- ⚡ 추가로 필요한 것: **CLAUDE.md/시스템 프롬프트 포트폴리오**, **에이전트로 빌드한 프로덕션 사례**

---

## ⚠️ Edge Cases & Caveats

| 상황                            | 영향                                                                                                                                                                          |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **"AI Native"가 마케팅 용어인가?** | 일부 채용 시장에서는 기존 SWE에 AI 도구 사용 경험만 더한 포지션에도 "AI Native"를 붙이는 경향. 실제 정의는 **에이전트 오케스트레이션 + 검증 인프라 구축**까지 포함하는지로 판단 |
| **신입의 진입 방식 변화**       | Howdy에 따르면 신입 온보딩이 "보일러플레이트 작성 → **에이전트 생성 코드 읽고 평가하기**"로 전환. 무신사 6개월 인턴 전환형도 같은 맥락                                          |
| **AI 도구 의존 리스크**         | Augment Code 표현대로 "보고서가 매우 빠르고 자신감 있게 틀림" → **자신의 판단력을 잃지 않는 것**이 핵심 역량. 검증 능력 없으면 위험                                              |
| **연봉 프리미엄의 지속성**      | 현재는 supply < demand 상태라 프리미엄 존재. 1~2년 내 대부분의 SWE가 AI Native 역량을 갖추게 되면 프리미엄 소멸 가능 ❓ [Uncertain]                                              |
| **포트폴리오 부재 시 평가법**   | Augment Code/Agentic Engineering Jobs 모두 "**프로덕션 배포 증거, 컨텍스트 파일 예시, 프로세스 변화 경험**" 3가지를 강조. GitHub 커밋 그래프만으로는 부족                       |

---

## ⚔️ Contradictions Found

발견된 모순 없음. 글로벌 정의와 한국 채용공고 표현이 거의 일치합니다 (그루우 "컨텍스트 엔지니어링과 하네스 엔지니어링의 경계" ≈ Agentic Engineering Jobs "Context Engineering + Harness Design").

---

## 🎯 권장: 이직/커리어 관점에서 어떻게 접근할까?

1. **단기 (1~2개월)**: Claude Code로 본인 사이드 프로젝트 1개를 처음부터 끝까지 빌드하고, `CLAUDE.md`/시스템 프롬프트를 공개 포트폴리오로 정리
2. **중기 (3~6개월)**: 현 직장에서 **팀 단위 워크플로우 개선** 사례 만들기 (Augment Code가 강조하는 "프로세스 변화 경험"). 이게 개인 GitHub보다 훨씬 강력한 시그널
3. **장기**: Den vault에 이미 축적 중인 Claude Code 4-scope 모델, Trivy auto-patch 같은 노트들이 **컨텍스트/하네스 엔지니어링 역량의 직접 증거**입니다. 면접 시 활용 가능

> 💡 **다음에 확인해야 할 것**:
>
> - 한국 시장의 AI Native 연봉 데이터 (잡코리아/원티드 공개 데이터 분석 필요)
> - 무신사 채용 결과 발표 (전환 비율, 평가 기준 사례)
> - 1년 후 직군 정착 여부 — 마케팅 용어로 사라질지, 표준 직군으로 자리잡을지

---

## 📎 Sources

1. [AI-Native Engineering: Definition, Roles, Workflow, and Operating Model (2026)](https://www.howdy.com/blog/ai-native-engineering-definition-roles-workflow-operating-model) — 1차 자료 (정의 및 워크플로우)
2. [How we hire AI-native engineers now: our criteria — Augment Code](https://www.augmentcode.com/blog/how-we-hire-ai-native-engineers-now) — 1차 자료 (채용 기준 6대 역량)
3. [What is AI-Native Engineering? — Agentic Engineering Jobs](https://agentic-engineering-jobs.com/what-is-ai-native-engineering) — 1차 자료 (도구 및 채용 방식)
4. [무신사, 'AI 네이티브' 신입 개발자 공개 채용 실시 — 무신사 뉴스룸 (2026-01-16)](https://newsroom.musinsa.com/newsroom-menu/2026-0116) — 1차 자료 (한국 시장)
5. [그루우 AI Native Engineer 채용공고 — 원티드](https://www.wanted.co.kr/wd/343535) — 1차 자료 (한국 자격요건)
6. [How to Choose Between AI, ML & AI-Native Engineering Courses — IIT Kharagpur](https://online.iitkgp.ac.in/blog/ai-vs-ml-vs-ai-engineering-course) — 기술 블로그 (직군 비교)
7. [AI-Native Software Engineer Skills to Learn in 2026 — IIT Kharagpur](https://online.iitkgp.ac.in/blog/ai-native-engineer-skills) — 기술 블로그 (역량)
8. [AI Engineer vs AI-Native Engineer Salary 2026 — IIT Kharagpur](https://online.iitkgp.ac.in/blog/ai-engineer-vs-ai-native-salary-comparison) — 기술 블로그 (연봉)
9. [AI Engineer Salary 2026: $145K–$310K — KORE1](https://www.kore1.com/ai-engineer-salary-guide/) — 기술 블로그 (연봉)
10. [AI Engineer vs ML Engineer vs Data Scientist (2026) — Second Talent](https://www.secondtalent.com/resources/ai-engineer-vs-ml-engineer-vs-data-scientist/) — 기술 블로그 (직군 비교)
11. [Generative AI Engineer vs ML Engineer: 2026 Role Comparison — Zen Van Riel](https://zenvanriel.com/job/generative-ai-engineer-vs-ml-engineer/) — 기술 블로그 (직군 비교)
12. [Augment Code 공식 사이트](https://www.augmentcode.com/) — 1차 자료 (회사/제품 개요)
13. [Augment Code, 시맨틱 코딩 역량을 모든 AI 에이전트에 개방 — SiliconANGLE (2026-02-06)](https://siliconangle.com/2026/02/06/augment-code-makes-semantic-coding-capability-available-ai-agent/) — 뉴스 (Context Engine MCP 개방)
14. [Augment: 대규모·복잡 코드베이스용 코딩 에이전트 — VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=augment.vscode-augment) — 마켓플레이스 (제품 설명)

---

## 📊 Research Metadata

- 검색 쿼리 수: 7 (일반 6 + SNS 1)
- 수집 출처 수: 14 (원문 확인 4건)
- 출처 유형 분포: 1차 자료 6, 기술 블로그 6, 뉴스 1, 마켓플레이스 1 (커뮤니티/SNS 0)
- 확신도 분포: ✅ Confirmed 5, 🟡 Likely 1, ❓ Uncertain 1, ⚪ Unverified 0
- 원문 직접 인용: 18건+ (6대 역량 보충 시 각 역량 인용구·평가 신호·4프로필 추가 확인)
- 보충 이력: 2026-05-26 Augment Code 회사 설명 추가 (Quick Research, WebSearch 1회 — 회사 개요용이므로 [QuickResearch] 수준) / 2026-05-26 3️⃣ 6대 역량 상세 보충 (WebFetch 1회로 Augment Code 원문 재확인 — 역량별 정의·인용구·좋은/나쁜 신호·면접 신호·4프로필)
- SNS 접근 방법: WebSearch site: operator (Reddit 결과 부실 — 직군명이 아직 커뮤니티에서 표준화되지 않음)
