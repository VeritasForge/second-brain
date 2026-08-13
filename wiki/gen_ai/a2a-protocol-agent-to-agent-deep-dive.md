# 📖 A2A Protocol (Agent2Agent Protocol) — Concept Deep Dive

> 💡 **한줄 요약**: A2A (Agent2Agent) Protocol은 Google이 주도해 만들고 현재 Linux Foundation 산하 LF AI & Data의 Agentic AI Foundation이 관리하는 개방형 표준으로, **서로 다른 벤더·프레임워크로 만들어진 AI 에이전트들이 서로를 발견하고, 인증하고, 작업을 위임·협업할 수 있게 해주는 "에이전트 간(agent-to-agent) 통신 규격"**입니다.

---

## 1️⃣ 무엇인가? (What is it?)

**A2A**는 서로 다른 회사·프레임워크로 만들어진 자율 AI 에이전트가 내부 구현을 공개하지 않고도 서로 발견(discover)·인증(authenticate)·협업(interact)할 수 있게 하는 개방형 통신 표준입니다.

- **탄생 배경**: 2025년 4월 9일 Google이 발표. 기업들이 자율 AI 에이전트를 실제 배포하면서 "서로 다른 벤더와 프레임워크로 만들어진 에이전트들이 서로 협력할 방법이 없다"는 문제에 직면했고, 이를 해결하기 위해 만들어졌습니다. [Google Developers Blog](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
- **거버넌스 변화**: 2025년 6월 23일 Google이 A2A를 **Linux Foundation**에 기증(donate)했고, Amazon Web Services (AWS), Cisco, Microsoft, Salesforce, SAP, ServiceNow 등이 참여하는 벤더 중립 프로젝트로 전환됐습니다. [Linux Foundation 발표](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents), [Forbes](https://www.forbes.com/sites/janakirammsv/2025/06/25/key-tech-firms-unite-as-google-donates-a2a-to-linux-foundation/)
- **최신 현황(2026년 8월 기준)**: 2026년 4월 **v1.0 정식 버전**이 나왔고, 150개 이상 조직이 지원, GitHub 스타 2만 2천 개 이상, 5개 언어 SDK 제공. 서명된 Agent Card와 결제 확장인 **Agent Payments Protocol (AP2)**도 함께 발표됐습니다. [Google Open Source Blog](https://opensource.googleblog.com/2026/04/a-year-of-open-collaboration-celebrating-the-anniversary-of-a2a.html)

> 📌 **핵심 키워드**: `Agent Card`, `Task 상태 머신`, `JSON-RPC 2.0`, `Server-Sent Events (SSE)`, `벤더 중립 (vendor-neutral)`

---

## 2️⃣ 핵심 개념 (Core Concepts)

```
┌───────────────────────────────────────────────────────────┐
│                A2A 핵심 구성 요소 관계                        │
├───────────────────────────────────────────────────────────┤
│                                                             │
│   Client Agent                       Remote Agent          │
│  (작업을 요청하는 쪽)                  (작업을 수행하는 쪽)     │
│        │                                    │              │
│        │  1. Agent Card 조회 (능력 발견)      │              │
│        │ ───────────────────────────────────▶│              │
│        │                                    │              │
│        │  2. Task 생성 요청 (Message 전송)    │              │
│        │ ───────────────────────────────────▶│              │
│        │                                    │              │
│        │  3. Task 상태 업데이트 (SSE 스트리밍) │              │
│        │ ◀───────────────────────────────────│              │
│        │                                    │              │
│        │  4. Artifact(결과물) 수신             │              │
│        │ ◀───────────────────────────────────│              │
│                                                             │
└───────────────────────────────────────────────────────────┘
```

| 구성 요소 | 역할 | 설명 |
|-----------|------|------|
| **Agent Card** | 능력 광고 | 에이전트가 스스로 게시하는 메타데이터(JSON) 문서. 무엇을 할 수 있고, 어떻게 접근하며, 어떤 인증이 필요한지 기술 |
| **Task** | 협업의 상태 단위 | 고유 ID를 가진 상태 기반(stateful) 작업 단위. 여러 번의 메시지 교환을 거쳐 진행 |
| **Message** | 대화 단위 | `role`(ROLE_USER/ROLE_AGENT)과 `parts`(텍스트/파일/구조화 데이터)로 구성 |
| **Artifact** | 결과물 | 에이전트가 작업 완료 시 생성하는 출력물 |
| **Skill** | 세부 기능 | Agent Card 내부에 배열로 선언되는, 에이전트가 실제 수행 가능한 개별 기능 단위 |

- Agent Card 안의 `securitySchemes` 필드로 API Key, OAuth 2.0 (Open Authorization 2.0), OpenID Connect (OIDC), mTLS (mutual Transport Layer Security) 등 인증 방식을 명시합니다.
- Task는 "제출됨 → 처리 중 → (필요시 중단) → 종료" 흐름의 **상태 머신**으로 설계되어, 수 시간~수일이 걸리는 장기 작업의 진행 상황을 클라이언트가 항상 추적할 수 있게 합니다.

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

```
┌─────────────────────────────────────────────────────────────┐
│                     A2A 프로토콜 스택                          │
├─────────────────────────────────────────────────────────────┤
│  전송 계층(Transport)                                         │
│   ├─ HTTP(S) + JSON-RPC 2.0  (단일 엔드포인트, 메서드 호출)      │
│   ├─ HTTP(S) + REST/JSON     (RESTful 엔드포인트)               │
│   ├─ gRPC (Protocol Buffers) (HTTP/2, 양방향 스트리밍)          │
│   └─ SSE (Server-Sent Events) (실시간 진행 상태 스트리밍)        │
├─────────────────────────────────────────────────────────────┤
│  발견/신뢰 계층                                                │
│   └─ Agent Card (+ v1.0부터 암호서명(cryptographic signing) 지원)│
├─────────────────────────────────────────────────────────────┤
│  작업 계층                                                     │
│   └─ Task 상태 머신 + Message + Artifact                       │
└─────────────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (Step by Step)

1. **Discovery(발견)**: Client Agent가 Remote Agent의 Agent Card를 조회해 어떤 Skill을 제공하는지, 어떤 입출력 형식(`inputModes`/`outputModes`)을 지원하는지, 어떤 인증이 필요한지 확인합니다.
2. **Task 생성**: Client가 Message를 담아 Task 생성을 요청합니다. 서버가 고유 `id`와 `contextId`(관련 상호작용 그룹 식별자)를 부여합니다.
3. **상태 전이**: Task는 아래 표의 상태값을 오가며 진행됩니다.
4. **스트리밍 업데이트**: 장기 작업의 경우 SSE로 진행 상황을 실시간 push.
5. **완료/결과 수신**: 종료 상태에 도달하면 Artifact(결과물)를 Client가 수신합니다.

### 🔍 Discovery 상세 메커니즘

Client Agent가 Remote Agent의 Agent Card를 **처음** 조회하는 방법은 스펙이 정의한 3가지 중 하나입니다.

| 방식 | 어떻게 동작하는가 | 언제 쓰나 |
|---|---|---|
| **① Well-Known URI (기본/권장)** | 정해진 경로로 그냥 GET 요청 | 공개 에이전트, 넓은 범위의 자동 발견이 필요할 때 |
| **② 레지스트리(Registry) 기반** | 중앙 저장소에 등록된 카드들을 "이런 스킬을 가진 에이전트" 같은 조건으로 검색 | 엔터프라이즈 내부망, 공개 마켓플레이스처럼 여러 에이전트를 검색·비교해야 할 때 |
| **③ 직접 설정(하드코딩)** | URL을 코드나 설정 파일·환경변수에 미리 박아둠 | 이미 관계가 정해진 밀결합(tightly-coupled) 시스템, 개발/테스트 단계 |

#### ① Well-Known URI 방식 — 가장 기본이 되는 첫 조회 절차

표준 경로:
```
https://{에이전트-서버-도메인}/.well-known/agent-card.json
```

이 경로는 **RFC 8615**(Request for Comments 8615 — IETF가 정한 "특정 목적의 메타데이터를 도메인의 `/.well-known/` 하위 표준 위치에 공개하자"는 규약, `/.well-known/security.txt` 등과 같은 계열)의 원칙을 따릅니다.

```
┌───────────────────────────────────────────────────────────┐
│              Well-Known URI 방식 첫 조회 흐름                │
├───────────────────────────────────────────────────────────┤
│  Client Agent                    Remote Agent 서버          │
│  (도메인만 알고 있음)                                        │
│       │                                                     │
│       │ 1. GET https://weather-agent.example.com/           │
│       │        .well-known/agent-card.json                  │
│       │ ──────────────────────────────────────────▶         │
│       │                                                     │
│       │ 2. 200 OK + Agent Card(JSON) 응답                    │
│       │        (인증 불필요 — 공개 카드)                       │
│       │ ◀──────────────────────────────────────────         │
│       │                                                     │
│       │ 3. Card 안의 skills / inputModes / outputModes /     │
│       │    securitySchemes 확인 → 이후 통신 방식 결정          │
└───────────────────────────────────────────────────────────┘
```

요청 예시:
```bash
curl https://weather-agent.example.com/.well-known/agent-card.json
```

핵심은 **클라이언트가 알아야 하는 건 도메인 하나뿐**이라는 점입니다. 경로가 표준으로 고정돼 있으니 별도 협의 없이 바로 조회가 가능합니다.

#### 공개 카드로 끝나지 않는 경우 — 인증된 확장 카드(Authenticated Extended Card)

공개 Agent Card에 `capabilities.extended_agent_card: true`가 있으면, 그 카드는 "일부만 보여주는 축약판"이고 더 상세한(민감한 스킬·내부 엔드포인트 포함) 버전이 따로 있다는 신호입니다.

1. 공개 카드 조회(위 GET 요청) → `extended_agent_card: true` 확인
2. Out-of-band로 자격증명 획득(예: OAuth 2.0 흐름으로 access token 발급)
3. 확장 카드 조회 메서드 호출 시 `Authorization` 헤더에 토큰 포함 → 더 상세한(비공개 스킬 포함) Agent Card 수신

> v1.0부터 이 메서드 이름이 `agent/getAuthenticatedExtendedCard` → **`GetExtendedAgentCard`**로 변경됐습니다(하위 호환이 깨지는 변경).

#### Discovery를 건너뛰어도 되는가? — 2계층 구조로 보는 답

A2A는 **"발견(Discovery) 계층"과 "실행(Invocation) 계층"을 분리**해 설계했습니다.

```
┌─────────────────────────────────────────────────────────┐
│  계층 1: Discovery (선택적 — 정보를 "어떻게 얻는가"의 문제)   │
│   ├─ Well-Known URI (매번 동적으로 카드 GET)                │
│   ├─ Registry 검색                                        │
│   └─ 직접 설정(하드코딩)                                     │
├─────────────────────────────────────────────────────────┤
│  계층 2: Invocation (필수 — 실제 작업 실행)                  │
│   └─ HTTP+JSON-RPC 2.0 / REST / gRPC 중 하나로              │
│       실제 message/send, tasks/get 같은 호출 수행            │
└─────────────────────────────────────────────────────────┘
```

즉 Agent Card 조회는 실행에 필요한 정보(URL, 호출 방식, 인증)를 **"얻는 방법" 중 하나**일 뿐이고, 그 정보를 다른 경로로 이미 갖고 있다면 건너뛰어도 프로토콜 관점에서 문제없습니다. GitHub 공식 문서(`docs/topics/agent-discovery.md`)의 Direct Configuration 정의 원문:

> "Client applications utilize hardcoded details, configuration files, environment variables, or proprietary APIs for discovery." — "This method is straightforward for establishing connections within known, static relationships."

다만 "URL만" 있으면 충분한 건 아니고, 최소 4가지가 필요합니다(원래 Agent Card가 이 4가지를 한 번에 알려주는 역할을 합니다).

| 필요 정보 | Discovery를 거치면 | 직접 설정으로 건너뛰면 |
|---|---|---|
| 엔드포인트 URL | Agent Card의 `url`/`AgentInterface` 필드에서 얻음 | 코드/설정 파일에 하드코딩 |
| 전송 방식(JSON-RPC/REST/gRPC) | Agent Card가 선언 | 미리 알고 맞춰서 클라이언트 구현 |
| 호출할 메서드/스킬과 입력 형식 | Agent Card의 `skills`, `inputModes`/`outputModes` | 문서·계약(contract)으로 사전 합의 |
| 인증 방식 | Agent Card의 `securitySchemes` | 미리 알고 자격증명 준비 |

**Discovery를 굳이 두는 이유**:
- **동적 변경 대응**: 리모트 에이전트의 스킬·인증 방식·버전이 바뀌면 discovery를 매번 하는 클라이언트는 즉시 반영되지만, 하드코딩한 클라이언트는 변경을 감지 못하고 실패하거나 구버전 방식으로 계속 호출합니다.
- **신뢰 확인**: v1.0부터의 서명된 Agent Card처럼, discovery 단계는 "이 카드가 진짜 그 도메인 소유자가 발행한 것"임을 검증하는 지점이기도 합니다. 직접 설정 방식은 이 검증을 건너뛰는 대신, 애초에 "정적이고 신뢰된 관계"임을 배포 시점에 인간이 보증한다는 전제를 깝니다.

#### Task 상태값 (Task Lifecycle States)

> 범례: **터미널(terminal)** = 더 이상 메시지를 받을 수 없는 최종 상태 / **중단(interrupted)** = 클라이언트 응답 후 재개 가능한 임시 정지 상태

| 상태값 | 분류 | 설명 |
|--------|------|------|
| `submitted` | 진행 중 | 작업 제출 완료, 아직 처리 시작 전 |
| `working` | 진행 중 | 처리 중 |
| `input-required` | 중단 | 에이전트가 추가 입력을 요구해 일시 정지 |
| `auth-required` | 중단 | 인증 정보가 부족해 일시 정지 |
| `completed` | 터미널 | 성공적으로 완료 |
| `failed` | 터미널 | 실패 |
| `canceled` | 터미널 | 취소됨 |
| `rejected` | 터미널 | 거부됨 |

### 버전 관리

- 버전 형식은 `Major.Minor`(예: `1.0`)이며, 클라이언트는 모든 요청에 `A2A-Version` 헤더를 포함해야 합니다.
- 2026년 4월 기준 **v1.0이 정식(stable) 릴리스**이며, 서명된 Agent Card·엔터프라이즈 멀티테넌시·마이그레이션 경로가 이 버전에서 확정됐습니다. [towardsai.net](https://pub.towardsai.net/a2a-protocol-v1-2026-how-ai-agents-actually-talk-to-each-other-c500079bca73)

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| # | 유즈 케이스 | 설명 | 적합한 이유 |
|---|------------|------|------------|
| 1 | 공급망(Supply Chain) 자동화 | 주문→배송 전 과정에서 여러 벤더의 에이전트가 협업 | 벤더마다 다른 시스템을 하나의 통신 규격으로 연결 |
| 2 | IT 운영(ITOps) 워크플로우 | 서로 다른 시스템의 에이전트가 인시던트 대응을 자동 협업 | 장기 실행·비동기 작업 추적에 적합 |
| 3 | 엔터프라이즈 내부 에이전트 네트워크 | 한 회사 안의 여러 부서 에이전트(재무, HR, 영업 등)를 연결 | "공개 에이전트 마켓플레이스"보다 훨씬 현실적인 근시일 사용처로 평가됨 [glukhov.org](https://www.glukhov.org/ai-systems/comparisons/a2a-protocol-2026-adoption/) |

### ✅ 베스트 프랙티스

1. **A2A는 MCP와 함께 쓴다**: A2A는 "에이전트-에이전트" 조율(가로 방향), MCP (Model Context Protocol)는 "에이전트-도구/데이터" 연결(세로 방향)을 담당하므로 상호 보완적으로 조합합니다.
2. **Agent Card 서명 검증을 반드시 한다**: v1.0부터 지원되는 서명된 Agent Card로 가짜 에이전트(카드 위조) 공격을 막습니다.
3. **독립 배포되는 다중 에이전트 시스템에만 도입한다**: 단일 애플리케이션 내부 구조나 소규모 팀에는 불필요한 복잡성을 추가한다는 것이 실무자 공통 의견입니다.

### 🏢 실제 적용 사례

- **Microsoft, AWS, Salesforce, SAP, ServiceNow, Workday, IBM 등 150개 이상 조직**이 A2A를 지지·구현하며, 주요 클라우드 플랫폼에 통합됐습니다. [Linux Foundation 보도자료](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year)

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ 장점 | 벤더 중립성 | 특정 프레임워크·모델에 종속되지 않고 서로 다른 회사의 에이전트를 연결 |
| ✅ 장점 | 기존 웹 표준 재사용 | HTTP, JSON-RPC, SSE 등 이미 검증된 인프라·인증·관측성 도구를 그대로 활용 가능 |
| ✅ 장점 | 장기 비동기 작업 지원 | Task 상태 머신 설계로 수 시간~수일 걸리는 작업의 진행 상황을 표준적으로 추적 |
| ❌ 단점 | N² 확장성 문제 | 점대점(peer-to-peer) HTTP 연결 방식이라 에이전트 수가 늘어나면 연결 수가 제곱으로 증가 [Medium 비판글](https://medium.com/@ckekula/everything-wrong-with-agent2agent-a2a-protocol-7e5ae8d4ab2b) |
| ❌ 단점 | 신뢰 메커니즘 미흡 | 프로토콜 자체에는 "상대 에이전트가 정말 신뢰할 만한가"를 검증하는 장치가 약함(서명 카드로 일부 보완 중) |
| ❌ 단점 | 통합 관측성 도구 부재 | 다중 에이전트 워크플로우 실패 시 원인 추적(A2A 통신 vs MCP 도구 vs LLM 프롬프트)이 어려움 |

### ⚖️ Trade-off 분석

```
표준화·상호운용성   ◄──────── Trade-off ────────►   운영 복잡성·디버깅 난이도
느슨한 결합(에이전트 독립성) ◄─────────────────►   신뢰·보안 검증 부담 증가
```

---

## 6️⃣ 차이점 비교 (Comparison: A2A vs MCP vs ACP)

> 범례: **MCP** = Model Context Protocol (Anthropic, 2024년 11월 발표) / **A2A** = Agent2Agent Protocol (Google, 2025년 4월 발표) / **ACP** = Agent Communication Protocol (IBM 주도, 2025년 8월 A2A 프로젝트에 합류) [LF AI & Data](https://lfaidata.foundation/communityblog/2025/08/29/acp-joins-forces-with-a2a-under-the-linux-foundations-lf-ai-data/)

### 📊 비교 매트릭스

| 비교 기준 | MCP | A2A | ACP |
|-----------|-----|-----|-----|
| 핵심 목적 | 단일 에이전트 ↔ 도구/데이터 연결(수직) | 에이전트 ↔ 에이전트 협업(수평) | 거버넌스 프레임워크(현재 A2A 프로젝트에 흡수) |
| 통신 방식 | JSON-RPC 2.0 (stdio/SSE) | HTTP(S) + JSON-RPC/REST/gRPC + SSE | A2A 프로젝트 편입 후 A2A 스택에 정렬 중 |
| 만든 곳 | Anthropic | Google → Linux Foundation | IBM → Linux Foundation |
| 발표 시점 | 2024년 11월 | 2025년 4월 | 2025년 초 (2025년 8월 A2A와 통합) |
| 적합한 경우 | 에이전트가 파일·DB·API 같은 "도구"를 써야 할 때 | 서로 다른 조직의 에이전트가 "작업"을 주고받아야 할 때 | (독립 표준으로서는 사실상 종료, A2A로 수렴) |

### 🔍 핵심 차이 요약

```
MCP                              A2A
──────────────────    vs    ──────────────────
수직 통합(agent→tool)          수평 통합(agent↔agent)
"내가 뭘 쓸 수 있나"            "네가 뭘 할 수 있나"
단일 에이전트 관점              멀티 에이전트 조율 관점
```

### 🤔 언제 무엇을 선택?

- **MCP를 선택하세요** → 에이전트 하나가 검색, 파일 시스템, 사내 DB 같은 도구/데이터에 접근해야 할 때
- **A2A를 선택하세요** → 서로 독립적으로 배포된, 다른 회사·팀이 만든 에이전트 여러 개가 작업을 위임·협업해야 할 때
- **실무에서는 대개 둘 다 필요**합니다 — "MCP로 개별 에이전트에 도구를 붙이고, A2A로 그 에이전트들을 조율"하는 조합이 표준 패턴으로 자리잡고 있습니다.

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|------|-----------|------------|
| 1 | 모든 멀티 에이전트 시스템에 A2A를 기본값으로 도입 | 단일 앱 내부 구조에서는 불필요한 통신 오버헤드·운영 복잡성만 증가 | 독립적으로 배포되는 에이전트 간 협업이 실제로 필요한지부터 확인 |
| 2 | Agent Card 서명 검증을 생략 | 가짜 Agent Card로 위장한 악성 에이전트에 작업을 위임할 위험(Agent Impersonation) | v1.0의 서명된 Agent Card 기능을 반드시 적용 |
| 3 | OAuth 토큰 만료 시간을 느슨하게 설정 | 토큰 탈취 시 장시간(수 시간~수일) 재사용 가능 | 짧은 토큰 수명 + 강력한 고객 인증(Strong Customer Authentication) 적용 |

### 🚫 Anti-Patterns

1. **점대점 연결만으로 대규모 에이전트 네트워크 구성**: 에이전트 수가 늘어날수록 N² 연결 문제가 발생하므로, 대규모에서는 Apache Kafka 같은 메시지 브로커를 앞단에 두는 구조를 고려해야 합니다.
2. **광범위한 접근 범위(overbroad access scopes)를 기본으로 부여**: 필요한 최소 권한만 부여하는 원칙 없이 에이전트에 넓은 권한을 주면, 하나의 에이전트가 침해당했을 때 피해 범위가 커집니다.

### 🔒 보안/성능 고려사항

- **Tool Squatting(도구 스쿼팅)**: 악의적 행위자가 가짜 도구/에이전트를 등록해 A2A의 발견(discovery) 메커니즘을 악용할 수 있습니다.
- **Context Poisoning**: Agent Card 메타데이터에 악성 지시문을 심어 다른 에이전트의 행동을 조작하는 공격이 보고되고 있습니다.
- **공개 카드 자체의 노출 위험**: `/.well-known/agent-card.json`은 인증 없이 누구나 조회 가능하므로, 내부 URL이나 민감한 스킬 설명을 여기에 그대로 넣으면 그 자체로 정보 노출입니다. 민감한 내용은 인증된 확장 카드(Authenticated Extended Card)로만 노출하는 것이 스펙이 권장하는 설계 원칙입니다.
- **관측성(observability) 선투자 필수**: 통합 모니터링 도구가 아직 부족한 상태이므로, 도입 전에 자체 트레이싱·로깅 체계를 먼저 마련해야 운영 중 장애 원인 파악이 가능합니다.

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|------|------|----------|
| 📖 공식 스펙 | A2A Protocol Specification | [a2a-protocol.org/latest/specification](https://a2a-protocol.org/latest/specification/) |
| 📖 공식 발표 글 | Google Developers Blog | [A2A: A New Era of Agent Interoperability](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) |
| 📘 학술 서베이 | arXiv 2505.02279 | MCP·ACP·A2A·ANP(Agent Network Protocol) 4개 프로토콜 비교 서베이 |
| 📘 보안 분석 | arXiv 2602.11327 | MCP, A2A, Agora, ANP에 대한 위협 모델링 비교 논문 |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리 | 언어/플랫폼 | 용도 |
|---------------|-----------|------|
| a2aproject/A2A (GitHub) | Python 등 5개 언어 SDK | 공식 SDK 및 레퍼런스 구현 |
| AP2 (Agent Payments Protocol) | A2A 확장 | 에이전트 간 결제 트랜잭션을 표준화하는 companion 프로토콜 |

### 🔮 트렌드 & 전망

- **v1.0(2026년 4월) 안정화 이후 엔터프라이즈 내부 네트워크 중심으로 확산**: "공개 에이전트 마켓플레이스"보다 "한 회사 안의 여러 부서 에이전트를 연결"하는 시나리오가 훨씬 현실적인 근시일 활용처로 평가됩니다.
- **MCP·A2A·ACP 3자 구도 → A2A로 수렴**: ACP가 2025년 8월 A2A 프로젝트에 합류하며, "에이전트 통신 표준" 경쟁이 A2A(협업) + MCP(도구 연결) 2개 축으로 정리되는 흐름입니다.
- **결제·거버넌스 확장 진행 중**: AP2(결제) 외에도 거버넌스 공백(governance gap)을 지적하는 논문들이 나오고 있어, 향후 버전에서 감사(audit)·정책 준수 관련 표준화가 추가될 가능성이 있습니다.

### 💬 커뮤니티 인사이트

- 실무자들 사이에서 "150개 조직 지지"라는 숫자와 "실제 90일 이상 운영 중인 프로덕션 사례" 사이에는 차이가 있다는 신중론이 존재합니다. 로고 지지 표명과 심층 운영 경험을 구분해서 봐야 한다는 지적입니다. [glukhov.org](https://www.glukhov.org/ai-systems/comparisons/a2a-protocol-2026-adoption/)

---

## 📎 Sources

1. [Announcing the Agent2Agent Protocol (A2A) - Google Developers Blog](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) — 공식 발표
2. [Agent2Agent Protocol (A2A) Specification](https://a2a-protocol.org/latest/specification/) — 공식 스펙
3. [Linux Foundation Launches the Agent2Agent Protocol Project](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents) — 거버넌스 발표
4. [A year of open collaboration: Celebrating the anniversary of A2A - Google Open Source Blog](https://opensource.googleblog.com/2026/04/a-year-of-open-collaboration-celebrating-the-anniversary-of-a2a.html) — v1.0/현황
5. [A2A Protocol Surpasses 150 Organizations - Linux Foundation](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year) — 채택 현황
6. [Google A2A Protocol in 2026: Adoption, Hype, and Reality - glukhov.org](https://www.glukhov.org/ai-systems/comparisons/a2a-protocol-2026-adoption/) — 비판적 현황 분석
7. [Everything wrong with Agent2Agent (A2A) Protocol - Medium](https://medium.com/@ckekula/everything-wrong-with-agent2agent-a2a-protocol-7e5ae8d4ab2b) — 한계·안티패턴
8. [MCP vs A2A: how they overlap and differ - Merge.dev](https://www.merge.dev/blog/mcp-vs-a2a) — MCP 비교
9. [ACP Joins Forces with A2A - LFAI & Data](https://lfaidata.foundation/communityblog/2025/08/29/acp-joins-forces-with-a2a-under-the-linux-foundations-lf-ai-data/) — ACP 통합
10. [Key Tech Firms Unite As Google Donates A2A To Linux Foundation - Forbes](https://www.forbes.com/sites/janakirammsv/2025/06/25/key-tech-firms-unite-as-google-donates-a2a-to-linux-foundation/) — 기증 배경
11. [Agent Discovery - A2A Protocol](https://a2a-protocol.org/latest/topics/agent-discovery/) — Discovery 3가지 전략(Well-Known URI/Registry/Direct Configuration) 공식 원문
12. [A2A/docs/topics/agent-discovery.md - GitHub](https://github.com/a2aproject/A2A/blob/main/docs/topics/agent-discovery.md) — Direct Configuration 전략 정의 원문
13. [A2A Common Workflows & Examples - a2aprotocol.ai](https://a2aprotocol.ai/docs/guide/a2a-sample-methods-and-json-responses) — GetExtendedAgentCard(구 agent/getAuthenticatedExtendedCard) 인증 확장 카드 흐름

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 11 (WebSearch 10 + 후속 확인 1)
> - 심화 조사(WebFetch) 수: 8
> - 출처 유형: 공식 5(Google/Linux Foundation/A2A 공식 스펙·GitHub), 기술 블로그 5, 학술(arXiv) 2, 비판적 분석 2
