---
tags: [temporal, saga-pattern, workflow-orchestration, msa, distributed-transaction, python]
created: 2026-07-12
---

# 📖 Temporal (워크플로우 오케스트레이션 엔진) 완전 정리

> 💡 **한줄 요약**: Temporal은 서버가 죽거나 네트워크가 끊겨도 "어디까지 진행했는지"를 자동으로 기억하고 이어서 실행해주는 오픈소스 워크플로우 실행 엔진으로, 여러 서비스에 걸친 여러 단계의 작업(=분산 트랜잭션)을 안전하게 끝까지 완료시키는 데 쓰인다.

---

## 1️⃣ Temporal이란 무엇인가

**Temporal**은 "듀어러블 실행 (Durable Execution, 실패해도 진행 상태가 유실되지 않는 실행 방식)"을 제공하는 오픈소스 워크플로우 오케스트레이션(orchestration, 여러 작업 단계를 순서대로 지휘하는 것) 플랫폼이다.

- **탄생 배경**: Uber 내부의 Cadence 프로젝트에서 파생되어, 분산 시스템에 깊은 경험을 가진 엔지니어들이 만들었다.
- **해결하려는 문제**: 여러 서비스를 거치는 긴 비즈니스 로직(예: "주문 생성 → 결제 → 재고 차감 → 배송 요청")을 실행하는 도중 서버가 죽거나 특정 단계가 실패하면, 기존에는 "어디까지 진행됐는지"를 개발자가 직접 DB나 상태 플래그로 추적해야 했다. Temporal은 이걸 엔진이 자동으로 보장해준다.

> 📌 **핵심 키워드**: `Durable Execution (듀어러블 실행)`, `Workflow (워크플로우)`, `Event History (이벤트 히스토리)`, `SAGA 패턴`

---

## 2️⃣ 핵심 구성요소 — Workflow / Activity / Worker

```
┌─────────────────────────────────────────────┐
│         Temporal의 3가지 핵심 구성요소          │
├─────────────────────────────────────────────┤
│  Workflow (오케스트레이션 코드)                 │
│      ↓ 호출                                   │
│  Activity (실제 side effect: API 호출/DB 쓰기)  │
│      ↓ 실행                                    │
│  Worker (내 애플리케이션 프로세스, 실제 실행자)   │
└─────────────────────────────────────────────┘
```

| 구성 요소 | 역할 | 설명 |
| --- | --- | --- |
| **Workflow** | 순서/로직 정의 | "무엇을 어떤 순서로 할지"를 정의하는 결정적(deterministic) 함수. Go, Java, Python, TypeScript 등으로 작성 |
| **Activity** | 실제 작업 수행 | 실제 API 호출, DB 쓰기 같은 부수효과(side effect)가 일어나는 단위. 실패 시 재시도 정책 적용 |
| **Worker** | 실행 프로세스 | 사용자가 직접 배포·운영하는 프로세스. Task Queue를 폴링(polling)하며 Workflow/Activity를 실제로 실행 |
| **Temporal Server (Cluster)** | 상태 관리 서버 | Workflow를 직접 실행하지 않고, 일정/상태 관리와 Task 분배만 담당 |
| **Event History** | 진행 상태 기록 | 모든 단계를 이벤트로 영속 저장 → Worker가 죽으면 새 Worker가 이 히스토리를 재생(replay)해서 중단 지점부터 이어감 |

### 동작 흐름

```
┌───────────────────────────────────────────────────────────┐
│                    Temporal 동작 흐름                       │
├───────────────────────────────────────────────────────────┤
│  [내 애플리케이션]                  [Temporal Server]         │
│   Worker ──(poll: "할 일 있어?")──▶  Task Queue               │
│   Worker ◀──(Task 전달)───────────  Task Queue               │
│   Worker ──(실행 결과 보고)───────▶  Event History에 기록       │
│                                                             │
│  ※ Temporal Server는 "무엇을, 언제, 누구에게" 시킬지만 관리      │
│    실제 코드 실행은 항상 내가 배포한 Worker 안에서 일어남         │
└───────────────────────────────────────────────────────────┘
```

1. **Workflow 시작**: 클라이언트가 "주문 처리 워크플로우"를 시작시키면, Temporal Server가 이를 Task Queue에 등록.
2. **Worker가 Task 수령**: 내가 배포한 Worker 프로세스가 Task Queue를 폴링(long-poll)해서 "할 일"을 가져옴.
3. **Activity 실행**: Worker가 실제 Activity(결제 서비스 호출 등)를 실행. 성공하면 결과를, 실패하면 에러를 Server에 보고.
4. **상태 영속화**: Server는 매 단계를 Event History에 기록 → Worker가 중간에 죽어도 새 Worker가 히스토리를 재생해 정확히 그 지점부터 재개.
5. **재시도/보정**: 특정 단계가 실패하면 정의된 재시도 정책에 따라 자동 재시도하거나, SAGA 패턴처럼 이전 단계를 되돌리는 보정 트랜잭션(compensating transaction)을 실행.

---

## 3️⃣ 왜 Temporal을 쓰는가 — SAGA 패턴과의 관계

### 3.1 MSA의 분산 트랜잭션 문제와 SAGA

**SAGA**는 분산 트랜잭션을 여러 개의 로컬 트랜잭션으로 나누고, 실패 시 보상 트랜잭션(Compensating Transaction)으로 되돌리는 패턴이다. SAGA에는 2가지 구현 방식이 있다.

```
[Choreography 방식]                    [Orchestration 방식] ← Temporal이 여기
서비스 A ──이벤트 발행──▶ 서비스 B          중앙 오케스트레이터
서비스 B ──이벤트 발행──▶ 서비스 C            │
서비스 C ──이벤트 발행──▶ 서비스 A               ├──▶ 서비스 A 호출
  (누가 전체 흐름을 아는지 불분명)                ├──▶ 서비스 B 호출
                                              └──▶ 서비스 C 호출
                                        (오케스트레이터가 전체 흐름을 알고 지휘)
```

| 구분 | Choreography (안무형) | Orchestration (지휘형) |
| --- | --- | --- |
| 흐름 제어 | 각 서비스가 이벤트를 주고받으며 자율적으로 진행 | 중앙의 오케스트레이터가 순서를 지시 |
| 전체 흐름 가시성 | 낮음 (누구도 전체를 안 봄) | 높음 (오케스트레이터가 전체를 추적) |
| Temporal의 역할 | 해당 없음 | 바로 이 "중앙 오케스트레이터" 로직을 실행하는 런타임 |

Temporal은 SAGA의 두 방식 중 **오케스트레이션(지휘형) 방식**을 구현할 때 쓰인다. 다만 "중앙화된 오케스트레이터"의 실제 로직(어떤 순서로 어떤 서비스를 호출하고, 실패 시 무엇을 보정할지)은 개발자가 Workflow 코드로 직접 작성한다. Temporal은 그 코드가 서버가 죽어도 진행 상태를 잃지 않고, 각 단계 실패 시 정의한 재시도/보정 로직을 정확히 실행하도록 **보장해주는 실행 엔진(런타임)**일 뿐이다.

정식 명칭으로는 소프트웨어 아키텍처 문헌에서 이 역할을 **"Process Manager"**라고 부른다. Orchestration 기반 SAGA의 오케스트레이터는 본질적으로 **비즈니스 프로세스 하나의 진행 상태를 관리하는 상태 머신**이다.

### 3.2 왜 중앙화가 필요한가

- Choreography 방식은 서비스가 늘어날수록(예: 10개 이상) "지금 전체 트랜잭션이 어디까지 진행됐는지" 추적하기가 매우 어려워진다.
- 중앙 오케스트레이터가 있으면 실패 지점 파악, 재시도, 보정 트랜잭션 처리가 한 곳(Workflow 코드)에 모여있어 디버깅과 가시성이 좋아진다 — 이게 Temporal을 도입하는 핵심 이유다.

### 3.3 "직접 배포"란 무엇을 의미하는가 — Self-hosted vs Temporal Cloud

| 비교 기준 | Temporal 자체 배포 (Self-hosted) | Temporal Cloud |
| --- | --- | --- |
| 핵심 목적 | 완전한 제어권 확보 | 운영 부담 없이 Temporal 사용 |
| 운영 주체 | 내 팀이 서버·DB까지 직접 운영 | Temporal 사가 서버 운영 |
| 비용 구조 | 인프라비 $2,500~4,500/월 + 인건비 | 사용량 기반, 소규모는 월 $200부터 |
| SLA | 직접 구축해야 함 (99.9% 달성에 멀티 AZ Cassandra 등 필요) | 표준 99.9% SLA 기본 제공 |
| 적합한 경우 | 데이터 주권·특수 규제·AWS 외 환경 | 운영 인력 부족, 빠른 도입 |

"서비스 간 트랜잭션 동기화를 위해 워크플로우 런타임 Temporal을 직접 배포 및 도입"이라는 표현은 = **"여러 마이크로서비스에 걸친 분산 트랜잭션(예: 주문-결제-재고-배송)을 SAGA 패턴으로 안전하게 처리하기 위해, Temporal이라는 오픈소스 워크플로우 엔진을 (Temporal Cloud라는 관리형 서비스 대신) 자사 인프라에 직접 설치·운영하기로 했다"**는 뜻이다.

일반적으로 자체 배포는 액션량 월 50M~100M 미만이거나, 팀이 Cassandra 운영 경험이 있거나, 데이터가 특정 리전을 벗어날 수 없는 규제 요건이 있을 때 고려한다.

---

## 4️⃣ 보상 트랜잭션 (Compensating Transaction)

### 4.1 두 방식 모두에서 사용됨

**보상 트랜잭션(Compensating Transaction, 이미 완료된 로컬 트랜잭션의 효과를 되돌리기 위한 반대 방향의 트랜잭션)**은 Choreography와 Orchestration 두 방식 모두에서 사용되는 공통 개념이다. 다만 "누가 보상 트랜잭션을 실행시키는가"가 다르다.

```
[Choreography 방식]                         [Orchestration 방식]
서비스 A 실패 이벤트 발행                       중앙 오케스트레이터가 실패 감지
   │                                              │
   ▼                                              ▼
서비스 B가 그 이벤트를 "구독"하고                    오케스트레이터가 "직접" B에게
자율적으로 자신의 보상 트랜잭션 실행                  보상 트랜잭션 실행을 명령
```

| 구분 | Choreography | Orchestration |
| --- | --- | --- |
| 보상 트랜잭션 존재 여부 | ✅ 사용됨 | ✅ 사용됨 |
| 트리거 방식 | 각 서비스가 실패 이벤트를 구독해 자율적으로 자신의 보상 로직 실행 | 중앙 오케스트레이터(예: Temporal Workflow)가 명시적으로 각 서비스의 보상 Activity를 호출 |

보상 트랜잭션이라는 "개념/용어" 자체는 SAGA 패턴 전체(두 구현 방식 공통)에 속하는 핵심 요소다. SAGA 패턴의 정의 자체가 "로컬 트랜잭션들의 연쇄 + 실패 시 되돌리는 보상 트랜잭션"이기 때문이다.

### 4.2 보상 트랜잭션 자체가 실패하는 문제

보상 트랜잭션도 결국 각 마이크로서비스(MS) 안에서 실행되는 "또 하나의 로컬 트랜잭션"이기 때문에, 네트워크 장애·DB 락·버그 등으로 똑같이 실패할 수 있다.

```
[정상 흐름]                         [보상 트랜잭션도 실패하는 경우]
서비스 A: 성공 ✅                     서비스 A: 성공 ✅
서비스 B: 성공 ✅                     서비스 B: 성공 ✅
서비스 C: 실패 ❌                     서비스 C: 실패 ❌
   │                                    │
   ▼ 보상 트랜잭션 시작                   ▼ 보상 트랜잭션 시작
서비스 B: 보상 성공 ✅                 서비스 B: 보상 실패 ❌ ← 여기서 멈춤
서비스 A: 보상 성공 ✅                 서비스 A: 보상 시도조차 못함
                                    → B, A는 불일치 상태로 방치
```

SAGA의 원래 이론(1987년 Garcia-Molina & Salem 논문)은 "보상 트랜잭션은 언젠가 반드시 성공한다"는 걸 전제로 깔고 있어서, 이 전제가 무너지면 이론상 구멍이 생긴다.

### 4.3 실무 대응 전략

| 대응 전략 | 설명 |
| --- | --- |
| **멱등성(Idempotency) + 무한 재시도** | 보상 트랜잭션을 성공할 때까지 반복 재시도하도록 설계. 멱등성이 있어야 여러 번 실행해도 안전 |
| **보상 트랜잭션은 최대한 "실패할 수 없게" 설계** | 정방향 트랜잭션은 복잡해도, 보상 트랜잭션은 단순한 상태값 변경처럼 실패 가능성이 낮은 연산으로 설계 |
| **Dead Letter Queue (DLQ) + 알림** | 재시도가 모두 실패하면 사람이 개입할 수 있도록 별도 큐에 쌓고 온콜에게 알림 |
| **정합성 검증 배치(Reconciliation Job)** | 주기적으로 서비스 간 데이터를 비교해 불일치를 찾아내는 별도 배치 작업을 안전망으로 둠 |

Orchestration(Temporal)은 보상 실패 시 최소한 "지금 어디서 막혀있는지"를 눈에 보이게 해주는 것이 실무에서 선호되는 큰 이유다. Choreography는 이 실패가 이벤트 로그 어딘가에 묻혀서 발견이 늦어질 위험이 더 크다.

> ⚠️ SAGA는 강한 일관성(Strong Consistency) 대신 **최종 일관성(Eventual Consistency)**을 목표로 하고, 그 최종 일관성조차 "보상 트랜잭션이 결국은 성공한다"는 걸 설계자가 재시도·알림·정합성 검증으로 직접 보장해야 얻어지는 것이다.

---

## 5️⃣ Workflow의 상태 관리

### 5.1 트랜잭션 단위 상태 관리 — Workflow ID

Temporal은 `order_id: 1`, `order_id: 2`처럼 **트랜잭션(비즈니스 단위) 하나당 하나의 독립된 Workflow Execution**을 가지며, 각각 별도의 Event History와 상태를 유지한다.

```
Temporal Server
├── Workflow Execution (Workflow ID = "order-1")
│     └── Event History: [주문생성 → 결제성공 → 재고차감성공 → 배송요청]
│     └── 현재 상태: "진행 중, 배송 대기"
├── Workflow Execution (Workflow ID = "order-2")
│     └── Event History: [주문생성 → 결제실패 → 보상트랜잭션 실행중]
│     └── 현재 상태: "롤백 중"
```

| 개념 | 설명 |
| --- | --- |
| **Workflow ID** | 개발자가 직접 부여하는 식별자. `order_id`처럼 비즈니스 ID를 그대로 Workflow ID로 쓰는 것이 실무 표준 패턴 |
| **Run ID** | 같은 Workflow ID라도 재실행(retry, continue-as-new 등)될 때마다 부여되는 내부 실행 식별자 |
| **Event History** | 각 Workflow Execution마다 완전히 독립적으로 쌓이는 이벤트 로그 |

**왜 order_id를 Workflow ID로 쓰는 게 권장되는가**: Temporal은 기본적으로 같은 Workflow ID를 가진 워크플로우가 이미 실행 중이면 중복 시작을 막는다. 즉 Workflow ID 자체가 **멱등성(Idempotency) 보장 수단**이 된다 (중복 주문 방지). 운영 시에도 `temporal workflow describe --workflow-id order-1` 처럼 order_id로 직접 상태를 조회할 수 있어 가시성이 좋아진다.

### 5.2 오케스트레이션 상태 vs 도메인 상태 — Process Manager로서의 Workflow

Temporal의 Workflow가 관리하는 상태는 **"오케스트레이션 상태(진행 상황)"**이고, 각 마이크로서비스가 가진 **"도메인 상태(실제 비즈니스 데이터)"를 대체하거나 통합하는 게 아니다.**

```
[각 MS가 소유한 "도메인 상태" (Source of Truth)]        [Temporal이 관리하는 "오케스트레이션 상태"]
결제 서비스 DB: {payment_id, amount, status}          order-1 Workflow:
재고 서비스 DB: {sku, quantity}                          "지금 결제는 끝났고, 재고 차감 대기 중"
배송 서비스 DB: {shipment_id, address}                   "재고 차감 실패 → 보상 트랜잭션 실행 중"
```

| 구분 | 도메인 상태 (Domain State) | 오케스트레이션 상태 (Orchestration State) |
| --- | --- | --- |
| 소유자 | 각 마이크로서비스 (결제 서비스, 재고 서비스 등) | Temporal Workflow (Event History) |
| 내용 | 실제 비즈니스 데이터 (결제 금액, 재고 수량 등) | "지금 어떤 단계인지" (진행/실패/보정 중/완료) |
| 저장 위치 | 각 서비스의 자체 DB | Temporal Server의 persistence 계층 |
| Temporal이 이걸 대체하나? | ❌ 아니요 | ✅ 이게 Temporal의 본래 역할 |

Temporal Workflow는 "order-1이 지금 재고 차감 단계다"라는 걸 알지만, 실제 재고가 몇 개 남았는지는 재고 서비스의 DB가 유일한 정답(Source of Truth)이다. 이 구분을 놓치면 "Temporal 안에 비즈니스 데이터를 직접 저장하면 되겠다"는 식으로 설계가 흘러갈 위험이 있는데, 이건 안티패턴이다 — Workflow 안의 상태는 어디까지나 "오케스트레이션 진행 상황"으로 한정하고, 실제 데이터 조회/쓰기는 항상 Activity를 통해 각 MS에게 위임해야 한다.

**정리**: Workflow가 관리하는 상태의 1차 단위는 "트랜잭션(=주문 하나)"이다. 그 트랜잭션 안에서 "이 트랜잭션과 관련해 각 MS를 호출한 결과가 어땠는지"를 세부적으로 추적하기 때문에, 마치 "MS별로 상태를 관리한다"처럼 보이는 것이다. 하지만 각 MS의 전체적인 상태(재고 총량, 전체 결제 이력 등)는 여전히 그 MS 자신이 소유하고, Workflow는 절대 그걸 대신 관리하지 않는다. 더 정확한 한 문장: **"Workflow는 트랜잭션 단위로, 그 트랜잭션이 건드리는 여러 MS와의 상호작용 진행 상황을 상태 머신으로 관리한다."**

### 5.3 오케스트레이션 상태의 물리적 저장 위치 — Persistence 계층

Temporal은 오케스트레이션 상태를 역할이 다른 2개의 저장소(store)로 나눠서 관리한다.

```
┌─────────────────────────────────────────────────────────┐
│                Temporal Persistence 계층                  │
├─────────────────────────────────────────────────────────┤
│  1) Default Store (필수)                                  │
│     ├─ Execution 테이블: 각 Workflow의 "현재 상태"           │
│     └─ History 테이블: 이벤트를 순서대로 쌓는 append-only 로그│
│     → Cassandra / PostgreSQL / MySQL 중 선택               │
│  2) Visibility Store (검색/조회용, 선택)                     │
│     └─ order_id로 워크플로우를 검색·필터링하기 위한 인덱스      │
│     → SQL DB(PostgreSQL/MySQL) 또는 Elasticsearch          │
└─────────────────────────────────────────────────────────┘
```

| 저장소 | 지원 DB | 저장되는 내용 |
| --- | --- | --- |
| **Default Store** (필수) | Cassandra, PostgreSQL, MySQL | `Execution 테이블`: "order-1은 지금 몇 번째 단계"라는 현재 상태 스냅샷. `History 테이블`: 그 상태에 이르기까지의 모든 이벤트 로그(append-only) |
| **Visibility Store** (선택) | SQL DB(PostgreSQL/MySQL) 또는 Elasticsearch | "실행 중인 워크플로우 목록 조회", "order_id로 필터링" 같은 검색/리스팅 기능 |

- **Default Store**는 Temporal이 동작하는 데 필수적인 유일한 의존성이다 — Workflow의 실제 정합성(consistency)과 재생(replay) 능력이 여기에 달려 있어서, 강한 일관성이 필요한 쓰기 위주 저장소(Cassandra/PostgreSQL/MySQL)를 쓴다.
- **Visibility Store**는 조회/검색 기능만 담당하기 때문에, 검색에 특화된 Elasticsearch를 옵션으로 쓸 수 있다.

지난 논의에서 다룬 "각 마이크로서비스의 도메인 상태(결제 DB, 재고 DB 등)"와는 완전히 별개의 물리적 DB다. 자체 배포(Self-hosted) 시에는 이 Default Store DB를 직접 운영·백업·이중화해야 한다는 것이 운영 부담의 핵심 원인이다.

### 5.4 Workflow ID 재사용/충돌 정책

같은 Workflow ID로 "새로 시작" 요청이 들어왔을 때, Temporal 입장에서는 "일시정지" 상태도 여전히 `Status: Running`이므로, 같은 Workflow ID로 실행 중인 게 있으면 중복 시작을 막는다는 규칙이 그대로 적용된다.

```
같은 Workflow ID로 "추가 요청" 도착
         │
         ▼
┌───────────────────────────────────────────────────┐
│  Fail (기본값)         → 거부, 에러 반환              │
│  UseExisting          → 거부하지 않고, 기존 실행 핸들만 리턴│
│  TerminateExisting    → 기존 걸 강제 종료 후 새로 시작   │
└───────────────────────────────────────────────────┘
```

| 정책 | 동작 |
| --- | --- |
| **Fail** (기본값) | `WorkflowExecutionAlreadyStartedFailure` 에러 반환 — 요청 거부 |
| **UseExisting** | 에러 없이, 지금 멈춰있는 그 Workflow의 핸들을 그대로 돌려줌 |
| **TerminateExisting** | 멈춰있는 Workflow를 강제로 죽이고 새로 시작 (⚠️ 위험 — 사람이 고치려던 진행 상태가 통째로 날아감) |

**Signal-With-Start**: 실무에서 "이미 실행 중인 order-1에 추가 정보를 전달하고 싶다"는 요구는 애초에 "새 Workflow를 시작"하는 게 아니라 Signal-With-Start라는 별도 API로 처리한다.

```
클라이언트: "order-1에 이 신호(수정된 데이터)를 보내줘"
         │
         ▼
   Temporal이 확인: order-1이 지금 실행 중(=일시정지 포함)인가?
    ┌────┴────┐
   YES        NO
    │          │
    ▼          ▼
 이미 있는     새로 Workflow를 시작하면서
 Workflow에    동시에 그 Signal도 즉시 전달
 그 Signal을
 바로 전달
 (기본 동작: USE_EXISTING)
```

기본 동작(`USE_EXISTING`)은 "이미 실행 중이면 새로 시작하지 않고, 그 실행에 Signal만 전달한다"이다. 이게 바로 "운영자가 원인을 수정한 데이터를 Signal로 보내서 멈춰있던 Workflow를 깨운다"는 것의 실제 API 메커니즘이다.

Python SDK의 `client.execute_workflow()`를 같은 ID로 재호출하면 기본 설정에서는 `WorkflowAlreadyStartedError`가 **즉시 raise**된다 — Temporal이 "이미 있는 실행에 자동으로 붙어서 결과를 기다려주는" 동작은 하지 않는다. 개발자가 이 예외를 명시적으로 처리해야 한다.

```python
from temporalio.exceptions import WorkflowAlreadyStartedError

try:
    result = await client.execute_workflow(
        DeliveryOrderWorkflow.run, order,
        id=order.order_id, task_queue="delivery-task-queue",
    )
except WorkflowAlreadyStartedError:
    # 이미 실행 중(일시정지 포함) → 기존 실행에 그냥 붙어서 결과를 기다림
    handle = client.get_workflow_handle(order.order_id)
    result = await handle.result()
```

---

## 6️⃣ Activity와 외부 시스템 통신

### 6.1 Activity는 Temporal-agnostic — 실제 MS 호출은 개발자 재량

Activity 함수 내부에는 실제로는 실제 API 호출(HTTP/gRPC) 또는 Broker 이벤트 발행이 들어간다. "보상 트랜잭션을 어떤 채널로 어느 서비스에 전달할지"는 순전히 Activity를 구현하는 개발자의 코드 안에서 결정되는 애플리케이션 로직이고, Temporal은 그 Activity를 "실행되게 보장"만 할 뿐, 그 안에서 HTTP를 쓰는지 gRPC를 쓰는지 Kafka를 쓰는지는 완전히 무관심(agnostic)하다.

```go
func RefundPayment(ctx context.Context, orderID string) error {
    resp, err := paymentServiceClient.Refund(ctx, &RefundRequest{OrderID: orderID}) // gRPC 호출 예시
    // 또는: kafkaProducer.Publish("payment.refund.requested", event) // 브로커 발행 예시
    return err
}
```

### 6.2 Task Queue ≠ Message Broker

Temporal의 Task Queue는 **"내가 배포한 Worker 프로세스"가 실행할 작업을 가져가도록 하는 내부 라우팅 메커니즘**이고, Broker(Kafka, RabbitMQ 등)는 서로 다른 시스템 간에 메시지를 전달하는 별도의 인프라다.

```
[Temporal 내부 통신]                        [MS 호출을 위한 통신 — Temporal이 모름]
Workflow (Temporal Server 안에서 관리)         Activity 코드 (개발자가 직접 작성)
   │                                             │
   ▼ Task를 Task Queue에 등록                     ▼ 여기서 실제로 결제 서비스를 호출
Worker가 폴링(polling)해서 가져감                  ├─ HTTP REST 호출
   │                                             ├─ gRPC 호출
   ▼                                             └─ 또는 Kafka/RabbitMQ에 메시지 발행
Worker 프로세스 안에서 Activity 함수 실행           (Temporal은 이 안에서 뭘 하는지 전혀 모름)
```

| 구분 | Temporal의 Task Queue | 메시지 브로커 (Kafka, RabbitMQ 등) |
| --- | --- | --- |
| 역할 | 내가 배포한 Worker 프로세스가 실행할 작업을 가져가도록 하는 내부 라우팅 메커니즘 | 서로 다른 시스템 간에 메시지를 전달하는 별도의 인프라 |
| 관리 주체 | Temporal Server가 관리 | 별도로 운영되는 독립적인 시스템(Kafka 클러스터 등) |
| Temporal이 이 정보를 알고 있나? | ✅ Task Queue 이름은 Temporal이 관리 | ❌ 브로커 주소/토픽명 같은 정보는 전혀 모름 |

Worker 프로세스는 Temporal Server와 **gRPC로만** 통신한다(Task 가져오기, 실행 결과 보고). 이 gRPC 통신은 Temporal 내부용이고, 실제 마이크로서비스(결제 서비스 등)에 도달하는 통신과는 완전히 별개의 레이어다.

| 질문 | 답변 |
| --- | --- |
| Temporal이 Broker 주소/토픽명을 관리하나? | ❌ 아니요. Activity 코드 안에 개발자가 직접 설정 |
| Temporal이 MS 호출 방식(HTTP/gRPC/Kafka)을 강제하나? | ❌ 아니요. 완전히 자유 — Temporal은 "언젠가 이 함수가 실행된다"만 보장 |
| 그럼 Temporal이 관리하는 건 뭔가? | ✅ "이 Activity가 실행됐는지, 실패했는지, 재시도해야 하는지"라는 실행 상태만 |

### 6.3 Temporal 내부 Task Queue vs 외부 Kafka/MQ 연동

```
┌─────────────────────────────────────────────────────┐
│              Temporal 내부 아키텍처                     │
├─────────────────────────────────────────────────────┤
│  Matching Service (내부 컴포넌트)                        │
│    └─ Task Queue: "이 이름의 Worker 풀에게 이 작업을 줘라"  │
│       (Kafka처럼 별도 설치하는 게 아니라 Temporal Server   │
│        자체에 내장된 기능)                                │
└─────────────────────────────────────────────────────┘
```

Temporal의 Task Queue는 Kafka/RabbitMQ 같은 범용 메시징 시스템이 아니라, "Workflow/Activity 실행 요청을 올바른 Worker 풀에게 라우팅"하는 전용 내부 메커니즘이다. **Kafka로 이걸 대체할 수 없다** — 설계 목적이 다르다: Temporal의 Task Queue는 "실행 보장·재시도·상태 관리"에 최적화되어 있고, 초당 수십만 건의 원시 이벤트를 라우팅하는 용도가 아니다. Temporal은 매우 높은 이벤트 처리량에서는 부적합하며, 메시지 버스로 쓰려는 시도는 지연만 늘리고 플랫폼의 목적 자체를 놓치는 것이다.

```
[Kafka]                          [Temporal]
"주문 생성" 이벤트 발행                  │
   │                                   │
   ▼                                   │
[얇은 Kafka Consumer Bridge] ──client.start_workflow()──▶ Workflow 시작
(별도로 직접 작성하는 서비스,                                    │
 Temporal의 일부가 아님)                                        │
                                                          Activity 안에서
                                                          다시 Kafka에 이벤트 발행 가능
```

| 연동 방식 | 설명 |
| --- | --- |
| **Kafka → Workflow 시작 트리거** | Temporal이 Kafka를 직접 구독하는 기능은 없다. 개발자가 얇은 Consumer 서비스를 직접 만들어서, Kafka 메시지를 읽고 그 안에서 `client.start_workflow()` 또는 `signal_with_start()`를 호출하는 방식으로 연동 |
| **Workflow → Kafka 발행** | Activity 코드 안에서 Kafka 프로듀서를 직접 호출 |
| **권장 설계 포인트** | Kafka의 파티션 키를 Workflow ID와 정렬(align)해서, 같은 주문의 이벤트는 항상 같은 파티션 → 같은 Workflow 실행으로 매핑되도록 설계 |

| 구분 | Temporal의 Task Queue | Kafka(외부 브로커) |
| --- | --- | --- |
| 목적 | Workflow/Activity 실행을 Worker에게 정확히 1번 전달하고 상태를 보장 | 대량의 이벤트를 순서대로, 여러 소비자에게 재생 가능하게 전달 |
| 강점 | 실행 신뢰성 보장 (재시도, 상태 추적, Event History) | 대용량 처리량 (초당 수백만 건) |
| 약점 | 초당 수십만 건 급 메시지 라우팅에는 부적합 | 그 자체로는 비즈니스 프로세스의 상태 관리를 안 해줌 |
| 실무 조합 | Kafka가 대량 이벤트를 받아 전달 → Temporal이 그 이벤트 하나하나에 대한 신뢰성 있는 실행을 담당 | 서로 대체 관계가 아니라 상호 보완 관계 |

#### ⚠️ Scale-out 시 흔한 오해 정정

"Kafka가 앞단에 있으니 Temporal 내부 큐는 신경 안 써도 된다"는 **틀렸다.**

```
[Kafka] ──100,000건/초 주문 이벤트──▶ [Consumer Bridge]
                                          │
                                          ▼ 여기서부터는 Kafka와 무관
                            client.start_workflow() × 100,000건/초
                                          │
                                          ▼
                    ┌─────────────────────────────────────┐
                    │   Temporal 내부 Task Queue/Matching   │
                    │   Service가 이 100,000건/초를          │
                    │   "고스란히" 직접 처리해야 함           │
                    │   각 Workflow마다 Activity가 4개라면    │
                    │   → 초당 400,000건의 Activity Task도    │
                    │     추가로 Temporal 내부에서 발생        │
                    └─────────────────────────────────────┘
```

| 구분 | Kafka가 완화해주는 부분 | Kafka와 무관하게 Temporal이 그대로 감당하는 부분 |
| --- | --- | --- |
| **버스트(순간 폭주) 트래픽** | ✅ 완화 — Kafka가 버퍼 역할을 해서 Temporal이 자기 처리 속도에 맞춰 천천히 꺼내가도 유실 안 됨 | — |
| **지속적인(steady-state) 총 처리량** | ❌ 전혀 안 줄어듦 | 결국 초당 X건을 처리해야 한다면, Temporal의 Task Queue/Matching Service/Persistence DB가 그 X건을 실시간으로 그대로 소화해야 함 |

self-hosted Temporal은 액션량 월 50M~100M 미만일 때 고려하라는 기준은 정확히 이 지점이다. 이 숫자는 Kafka가 앞단에 있든 없든 변하지 않는 Temporal 자체의 내부 처리 용량 한계다. Kafka를 앞에 세운다고 이 숫자가 올라가지 않는다.

**완화 전략**:

| 전략 | 설명 |
| --- | --- |
| 1 Workflow = 1 저수준 이벤트가 아니라, 1 Workflow = 1 의미있는 비즈니스 트랜잭션 | 잔이벤트를 다 Workflow로 만들지 말고, 비즈니스적으로 의미 있는 단위(주문 하나)에만 Workflow 매핑 |
| Temporal 자체의 Scale-out | Matching Service, History Service, Persistence DB를 실제 처리량에 맞게 Temporal 차원에서 직접 스케일 아웃 |
| Namespace/Task Queue 분리 | 트래픽이 많은 Workflow 타입은 별도 Task Queue/Namespace로 분리 |

### 6.4 비동기 Activity 완료 (Async Activity Completion)

MS의 처리가 즉시 끝나지 않고(비동기 처리, 사람 승인 등) Broker를 거쳐야 할 때 쓰는 패턴이다.

```
Workflow                Activity(publish_refund_request)          결제 서비스(Broker 소비자)
   │──execute_activity────────▶│                                        │
   │                           │ task_token = activity.info().task_token │
   │                           │ kafka.publish(refund_request, token 포함)│
   │                           │ activity.raise_complete_async() ← "나중에 완료됨" 표시 │
   │        [ ... 시간 경과 ... ]                                         │
   │                                                              Kafka에서 메시지 소비, 실제 환불 처리 실행
   │◀─────────── client.get_async_activity_handle(task_token).complete(result) ──┘
```

```python
# 결제 서비스로 요청을 "보내는" Activity
@activity.defn
async def refund_payment_async(input: DeliveryOrderInput) -> None:
    task_token = activity.info().task_token   # 이 Activity 실행을 나중에 식별할 토큰
    await broker_client.publish(
        topic="payment.refund.requested",
        payload={"order_id": input.order_id, "task_token": task_token.hex()},
    )
    activity.raise_complete_async()   # "나 아직 안 끝났어, 외부에서 완료시켜줄게" 선언
```

```python
# payment_service_consumer.py (결제 서비스 측 Kafka 컨슈머)
from temporalio.client import Client

async def on_refund_processed(message):
    client = await Client.connect("localhost:7233")
    handle = client.get_async_activity_handle(task_token=bytes.fromhex(message["task_token"]))

    if message["result"] == "success":
        await handle.complete(None)
    else:
        await handle.fail(RuntimeError(message["error_reason"]))
```

**"raise_complete_async를 호출하면 메모리에 살아있다"는 오해 정정**: 함수는 `raise_complete_async()` 호출 즉시 종료(return)된다. Worker의 코루틴은 이미 끝났고, Temporal Server는 그저 "이 task_token에 대한 완료/실패 보고가 아직 안 왔다"는 **레코드**만 들고 있는 것이다. "살아있음을 증명하는 책임"은 결제 서비스 쪽 코드에 있고, Temporal은 그 신호(heartbeat)가 안 오면 그냥 죽었다고 간주한다.

```python
# 결제 서비스 쪽 컨슈머 코드 — 처리 중간중간 직접 heartbeat를 "보내줘야" 함
async def process_refund(message):
    handle = client.get_async_activity_handle(task_token=bytes.fromhex(message["task_token"]))
    await handle.heartbeat("결제사 API 호출 중...")
    result = await call_payment_gateway(message["order_id"])
    await handle.complete(result)
```

### 6.5 여기서 Retry는 누가 담당하는가

| 실패 지점 | 처리 주체 |
| --- | --- |
| **"메시지를 Broker에 발행하는 것" 자체가 실패** (Kafka 다운 등) | Broker 클라이언트 라이브러리의 자체 재시도 **+ 그것도 실패하면 Temporal의 Activity Retry Policy**가 Activity 전체를 재시도 |
| **Broker 발행은 성공했지만, 결제 서비스가 일정 시간 안에 완료/Signal을 안 보냄** | Activity/Workflow 타임아웃으로 감지해야 함 |
| **결제 서비스 내부 처리 자체가 실패** | 결제 서비스가 실패했다는 결과를 Signal/Async Completion으로 명시적으로 보내야 하고, Workflow 코드가 그 실패를 받아서 다시 재시도를 걸지, DLQ로 보낼지를 직접 판단해야 함 |

즉, Broker를 거쳐도 **retry의 주체는 여전히 Temporal**이다. 다만 "언제 성공/실패했는지"를 Temporal에게 알려주는 채널이 즉시 응답(동기 RPC)이 아니라 task_token을 매개로 한 비동기 콜백이라는 점만 다르다.

### 6.6 heartbeat 재발행과 이중 retry, 멱등성 문제

heartbeat 타임아웃이 발생하면 Temporal은 Activity 함수 자체를 처음부터 다시 실행한다 → 그 안에 `broker.publish(...)`가 있으니 **새 메시지가 또 발행된다.**

멱등성으로 이를 해결해야 하는데, **키 설계가 중요**하다.

> ❌ **흔한 실수**: Activity ID를 멱등키로 쓰면 될 거라 생각 — 하지만 Activity ID는 Temporal 내부 식별자일 뿐, 결제 게이트웨이(외부 시스템)는 그 값을 전혀 모르고 신경 쓰지 않는다.

```python
# ❌ 잘못된 방식 — 매 재시도마다 새 UUID 생성 → 결제 게이트웨이는 "새 요청"으로 인식
@activity.defn
async def refund_payment_async(input):
    idempotency_key = str(uuid.uuid4())   # 재시도마다 값이 바뀜 → 멱등성 무의미
    ...

# ✅ 올바른 방식 — Workflow 코드에서 "한 번만" 키를 만들어 Activity에 넘김 (재시도돼도 값 고정)
@workflow.run
async def run(self, input: DeliveryOrderInput) -> str:
    refund_idempotency_key = f"refund-{input.order_id}"   # 결정론적으로 고정된 값
    ...
    await workflow.execute_activity(
        refund_payment_async, args=[input, refund_idempotency_key], ...
    )
```

```python
# 결제 서비스(외부 시스템) 쪽 — 이 키를 자기 DB에서 "이미 처리했는지" 체크해야 함
async def process_refund(message):
    if await db.exists("processed_idempotency_keys", message["idempotency_key"]):
        return  # 이미 처리된 요청 → 무시 (같은 메시지가 N번 와도 실제 환불은 1번만)
    ...
    await db.mark_processed(message["idempotency_key"])
```

핵심: 멱등키는 Temporal이 만들어주는 게 아니라 개발자가 Workflow 코드 안에서 한 번만 결정론적으로 생성해서 Activity에 넘기고, 그 키를 인식하고 중복을 걸러내는 로직은 결제 서비스(외부 시스템) 쪽에 반드시 구현해야 한다.

#### 이중 retry 레이어 문제

```
[레이어 1] Temporal Activity Retry           [레이어 2] Broker 자체 재전송(Kafka/RabbitMQ)
heartbeat 타임아웃 → 함수 재실행                consumer가 처리 실패 → ack 안 하고 requeue
→ 새 메시지 발행                               → 같은 메시지가 다시 소비됨
     둘 다 "독립적으로" 작동 → 서로의 존재를 모름 → 중복이 곱해질 수 있음
```

| 시나리오 | 결과 |
| --- | --- |
| Broker가 자체 재전송 중인데 Temporal도 heartbeat 타임아웃으로 재발행 | 같은 논리적 요청이 물리적으로 N개 메시지로 존재 |
| DLQ에 쌓일 때 | 이 N개 메시지가 각각 별개의 실패처럼 DLQ에 쌓임 → 운영자가 오인 |

**해결 방향 — 재시도 책임을 레이어별로 명확히 분리**:

| 레이어 | 책임 범위 (권장 설계) |
| --- | --- |
| **Temporal Activity Retry** | 오직 "Broker에 발행하는 것 자체"의 실패만 담당 (`maximum_attempts=3` 정도로 낮게) |
| **Broker/Consumer의 재전송 + 자체 DLQ** | "발행된 이후, 실제 처리 성공/실패"는 전적으로 Broker 쪽 재전송 정책이 담당 — Temporal은 이 구간에서는 재발행하지 않음 |
| **heartbeat_timeout** | Broker 쪽의 자체 재시도+DLQ 사이클이 끝날 때까지 기다릴 수 있을 만큼 충분히 길게 설정 |
| **최종 실패 통보** | Broker 쪽이 자체 재시도를 모두 소진해 진짜 DLQ에 넣기로 확정한 시점에만, 결제 서비스가 `handle.fail(error)`를 호출해 Temporal에 1번만 알림 |

---

## 7️⃣ Heartbeat

### 7.1 Heartbeat의 4가지 목적

heartbeat는 "비동기 완료 대기 중 생존 확인" 하나만을 위한 기능이 아니라, 원래 "오래 걸리는 동기(sync) Activity"를 위해 만들어진 범용 메커니즘이다.

```
┌─────────────────────────────────────────────────────────┐
│              Activity ──(heartbeat)──▶ Temporal Server     │
├─────────────────────────────────────────────────────────┤
│  ① "나 아직 살아있어" (Worker 생존 확인)                       │
│  ② "여기까지 진행했어" (진행 상황 체크포인트)                     │
│  ③ "혹시 취소됐어?" (Cancellation 수신 — 유일한 통로)           │
│  ④ (비동기 완료 대기 중) "외부 처리 아직 진행 중이야"              │
└─────────────────────────────────────────────────────────┘
```

| 목적 | 설명 |
| --- | --- |
| **① Worker 크래시 감지** | heartbeat가 없으면 오직 `start_to_close_timeout`(전체 허용 시간)이 끝나야만 실패를 알아챈다. heartbeat가 있으면 그보다 훨씬 짧은 주기로 크래시를 감지할 수 있다 |
| **② 진행 상황 체크포인트** | `heartbeat(details=...)`로 진행 상황(예: "10,000개 중 9,900번째까지 처리")을 함께 실어 보내면, Worker가 죽어서 재시도되더라도 처음부터 다시 하지 않고 9,900번째부터 이어서 처리할 수 있음 |
| **③ 취소(Cancellation) 전달** | Activity가 실행 취소(Cancellation) 요청을 받는 유일한 통로가 heartbeat다. heartbeat를 안 보내는 Activity는 취소 신호 자체를 받을 방법이 없음 |
| **④ 비동기 완료 대기 중 생존 확인** | `raise_complete_async()` 이후 외부 시스템이 `AsyncActivityHandle.heartbeat()`로 "아직 처리 중"임을 알림 |

heartbeat는 throttling(제한)되어, 실제로는 timeout의 80% 간격으로만 전송된다.

```
heartbeat_timeout = 3분으로 설정
   → 실제 heartbeat 전송 간격 = 3분 × 0.8 = 2.4분마다 1번
```

**중요한 재구성**: "timeout을 얼마나 길게 주냐"가 핵심 레버가 아니라, "이 작업이 정말 살아있음을 얼마나 자주 증명할 수 있느냐(heartbeat 주기)에 맞춰 timeout을 정하는 것"이 정답이다.

#### heartbeat_timeout을 "아주 길게" 줬을 때의 숨은 비용

```
heartbeat_timeout을 30분으로 설정 (아주 길게)
   → 결제 서비스가 진짜로 죽었다면 Temporal은 30분 동안 아무것도 모름
   → 그동안 order-1 Workflow 전체가 "결제 확인 대기"에 묶여있음
   → 고객은 "배달 확정" 알림을 30분 넘게 못 받고, 알림/온콜 호출도 그만큼 늦어짐
```

"아주 길게" 주면 중복 메시지 문제는 줄어들지만, 그 대가로 전체 SAGA가 그만큼 오래 조용히 멈춰있는 비용을 지불하게 된다.

#### 언제 heartbeat가 필요 없나

| 상황 | heartbeat 필요 여부 |
| --- | --- |
| `charge_payment`처럼 몇 초 안에 끝나는 짧은 Activity | ❌ 불필요 — `start_to_close_timeout`만으로 충분 |
| 대용량 배치 처리, 파일 변환처럼 몇 분~몇 시간 걸리는 Activity | ✅ 필요 |
| Broker를 통한 비동기 완료 대기 | ✅ 필요 |
| Workflow 안에서 Activity를 취소할 가능성이 있는 경우 | ✅ 필요 |

### 7.2 Heartbeat는 Activity 단위 — Workflow는 다른 메커니즘

Heartbeat는 철저히 "Activity 단위" 관리이고, Workflow는 애초에 heartbeat라는 개념 자체가 없다.

```
DeliveryOrderWorkflow (Workflow — heartbeat 개념 없음)
   ├─ charge_payment Activity        → heartbeat 설정 없음 (짧으니 불필요)
   ├─ start_cooking Activity         → heartbeat 설정 없음
   ├─ assign_rider Activity          → heartbeat_timeout=30초 (라이더 탐색이 오래 걸린다면)
   │     └─ 이 Activity"만의" 독립적인 heartbeat 트래킹
   └─ notify_customer Activity       → heartbeat 설정 없음
```

| 구분 | Activity | Workflow |
| --- | --- | --- |
| 생존 확인 메커니즘 | **Heartbeat** (개발자가 명시적으로 호출해야 함) | **Workflow Task Timeout** (기본 10초, 자동 동작) |
| 왜 다른 메커니즘을 쓰는가 | Activity는 실제 부수효과(외부 API 호출 등)를 실행하므로, 얼마나 걸릴지 예측 불가 → 명시적 생존 신고 필요 | Workflow 코드는 결정론적(deterministic)이고 Event History로 재생(replay) 가능하므로, Worker가 죽어도 다른 Worker가 즉시 이어받아 재생 가능 — heartbeat로 "살아있음"을 증명할 필요가 없음 |
| 개발자가 직접 관리해야 하는가 | ✅ 예 | ❌ 아니요 (Temporal이 자동 처리) |

```
Activity 코드 (예: 결제 API 호출)          Workflow 코드 (예: 순서 결정 로직)
   │                                         │
   ▼                                         ▼
외부 세계에 실제 영향을 줌                    순수하게 "무엇을 어떤 순서로 할지"만 결정
(재실행하면 중복 결제 위험 ⚠️)                (재실행해도 안전 — 결정론적이므로 같은 결과)
   │                                         │
   ▼                                         ▼
"진짜 살아있는지" 증명 필요                   Event History만 있으면 다른 Worker가
→ Heartbeat 필요                             바로 이어받아 replay 가능 → Heartbeat 불필요
```

취소(Cancellation) 전달도 마찬가지다 — Workflow를 취소하면 그 신호가 Workflow 안의 각 Activity에게 개별적으로 전달되고, 그걸 실제로 "받는" 통로가 각 Activity의 heartbeat다. 즉 취소 요청은 Workflow 단위로 시작되지만, 그걸 실어 나르는 메커니즘 자체는 여전히 Activity 단위다.

### 7.3 heartbeat_timeout 튜닝 — 매우 길게 vs 백그라운드 감시 잡

"매우 길게" 주는 방식과 "백그라운드에서 죽은 Activity를 찾아 fallback"하는 방식 중, 후자가 실무에서 검증된 패턴에 더 가깝다.

> "Signal 기반 Workflow 타입에 대해 **모니터링 잡이 주기적으로 실행**되어, 예상 최대 지속시간을 넘겨 Running 상태로 남아있는 실행을 감지하면 알림을 보낸다. **커스텀 Search Attribute**가 막힌 Workflow를 올바른 해결 담당자에게 라우팅하는 메커니즘을 제공한다."

```
┌──────────────────────────────────────────────────────────┐
│              백그라운드 감시 잡 (권장 아키텍처)                │
├──────────────────────────────────────────────────────────┤
│  주기적으로 실행 (예: 5분마다)                                │
│    ▼                                                       │
│  Temporal Visibility Store 조회:                             │
│  "OrderStatus='결제확인대기' AND 시작후 10분 경과"              │
│    ▼                                                       │
│  발견되면 → on-call 알림 + 필요 시 handle.fail() 명시적 호출     │
│           → 기존에 만들어둔 SAGA 보정 로직으로 그대로 진입        │
└──────────────────────────────────────────────────────────┘
```

| 비교 항목 | heartbeat_timeout | 백그라운드 감시 잡 |
| --- | --- | --- |
| 감지 로직 위치 | Temporal Activity 내부 메커니즘에 의존 | 내가 직접 통제하는 별도 시스템 |
| "진짜 죽었는지" 판단 | heartbeat 유무만으로 판단 (오탐 가능) | Broker의 컨슈머 랙, DLQ 적재량 등 여러 신호를 종합해서 판단 가능 |
| 재발행(중복 메시지) 위험 | 있음 (Temporal이 자동으로 Activity 재실행) | 없음 — 감시 잡이 재시도가 아니라 알림+명시적 fail만 트리거 |
| 알림 경로 | Temporal 실패 이벤트에 의존 | 온콜에게 바로 라우팅 |

**추천 — 두 방식을 역할별로 병행**:

```
1차 방어선 (heartbeat_timeout)          2차 방어선 (백그라운드 감시 잡)
"명백하고 빠른 장애" 감지                "애매하거나 오래 걸리는 정체" 감지
(결제 서비스 프로세스 자체가 죽음)         (Broker 자체 재시도 중인데 언제 끝날지 불확실한 경우)
   ▼                                        ▼
heartbeat 간격(예: 1분)에 맞춰               충분히 여유 있게(예: 10분) 잡고
timeout을 3분 정도로 짧게 설정               재발행 없이 "감지 + 알림"만 담당
```

1. heartbeat_timeout은 "짧고 빠르게" — 진짜 죽은 경우(프로세스 크래시, 네트워크 단절)는 자동으로 빠르게 잡아서 Retry Policy로 처리.
2. "진짜 죽었는지 애매한 경우"(Broker가 자체 재전송 중이라 아직 살아있을 수도 있는 경우)는 백그라운드 감시 잡이 좀 더 여유 있게 지켜본 뒤 사람에게 넘기기.
3. 어느 경로로 감지되든, 최종 처리는 항상 같은 곳(`alert_ops_team` + `wait_condition(operator_resolved)`)으로 합류시키기.

---

## 8️⃣ 실패 처리와 재개 — 종합

### 8.1 3개 MS 보상 트랜잭션 처리 — 동기/비동기 패턴

먼저 MS와의 통신이 동기(Sync)냐 비동기(Async)냐를 구분해야 한다.

```
[패턴 A: 동기 호출 (RPC 스타일)]              [패턴 B: 비동기 호출 (Signal 스타일)]
Workflow → Activity 실행                     Workflow → Activity 실행
   Activity 안에서 gRPC/HTTP 호출                Activity 안에서 메시지 발행(Kafka 등) 후 즉시 리턴
   → 응답 올 때까지 "그 자리에서" 대기              → Workflow는 "결과 대기 상태"로 들어감
   → 응답=성공 → Activity 성공 리턴                → MS가 실제 처리 완료 후 "Signal"을 Workflow에 보냄
```

**패턴 A(동기 호출)**: Broker가 필요 없다. retry는 완전히 Temporal 내부에서 처리된다.

```
┌──────────────────────────────────────────────────────────┐
│  Workflow: 3개 MS에 보상 트랜잭션 병렬 실행 (Selector 사용)     │
├──────────────────────────────────────────────────────────┤
│  future1 = ExecuteActivity(RefundPayment, orderID)        │
│  future2 = ExecuteActivity(ReleaseInventory, orderID)     │
│  future3 = ExecuteActivity(CancelShipment, orderID)       │
│  selector.AddFuture(future1, ...) 등 → 3개가 각자 끝날 때마다  │
│  결과를 받아 Workflow 상태 갱신                                │
└──────────────────────────────────────────────────────────┘
```

각 Activity(`RefundPayment` 등)는 독립적인 Retry Policy를 가진다.

| 파라미터 | 기본값 | 의미 |
| --- | --- | --- |
| Initial Interval | 1초 | 첫 재시도까지 대기 시간 |
| Backoff Coefficient | 2.0 | 재시도마다 대기 시간이 2배씩 증가 (지수 백오프) |
| Maximum Interval | 100초 | 대기 시간이 무한히 커지지 않게 상한 |
| Maximum Attempts | 무제한(기본) | 몇 번까지 재시도할지 |

**"정상 롤백됨을 오케스트레이터가 아는" 방법**: 오케스트레이터는 "MS의 롤백 완료 여부"를 Activity 함수의 반환값(성공/에러) 그 자체로 안다. 결제 서비스가 API 응답으로 "환불 처리 완료"를 명확히 돌려주면, 그게 Activity의 성공 리턴이 되고, 그 순간 Temporal이 자동으로 Event History에 기록 → Workflow의 로컬 상태가 그 이벤트를 반영해 갱신된다.

**패턴 B(비동기/Signal)**: MS 처리가 오래 걸리거나 진짜 브로커를 거쳐야 할 때 쓴다. 확인 정보를 전달하는 방식은 두 가지다:
1. **Async Completion**: 결제 서비스가 처리 완료 후 Task Token을 이용해 Temporal Client SDK로 "이 Activity 완료됐다"고 직접 통보.
2. **Signal**: Activity는 그냥 "메시지 보냈다"로 끝내고, 결제 서비스가 나중에 Workflow에 Signal을 보내서 Workflow 로직이 그 시점에 반응하도록 함. 사람 승인처럼 며칠 걸릴 수 있는 경우 Signal이 더 유리.

**종합 흐름 (3개 MS, 패턴 A 기준)**:

```
                         ┌─────────────────────────┐
                         │   Order Workflow (order-1) │
                         └──────────┬──────────────┘
                                    │ 병렬 실행 (Selector)
          ┌─────────────────────────┼─────────────────────────┐
          ▼                         ▼                         ▼
  Activity: RefundPayment    Activity: ReleaseInventory  Activity: CancelShipment
          │                         │                         │
     성공 응답 ✅                성공 응답 ✅                실패→재시도→최종실패 ❌
          └─────────────┬───────────┴─────────────────────────┘
                         ▼
        Workflow가 3개 결과를 모두 수신 → Event History에 기록됨
        → CancelShipment만 최종 실패 → Workflow 로직이 판단:
           "배송만 롤백 안 됨" → 알림/DLQ로 에스컬레이션 (사람 개입)
```

### 8.2 실무 배달 예제로 정리 — DLQ에 대한 정정

Temporal은 전통적인 DLQ(Dead Letter Queue) 개념 대신, "일시정지(Pause) → 사람이 고침 → 재개" 패턴을 쓴다.

```
[일반적인 DLQ 방식 (Kafka 등)]              [Temporal의 실제 방식]
실패 메시지 → 별도의 DLQ 토픽으로 이동          실패한 Activity → Workflow가 그 지점에서 "멈춤"
운영자가 DLQ를 별도로 조회/재처리                (Workflow 자체가 Event History와 함께 그대로 살아있음)
                                            운영자가 Temporal UI/CLI로 이 Workflow를 검색해서 확인
                                            원인 수정 후 Signal 전송 → 그 지점부터 그대로 재개
                                            (처음부터 다시 실행 X, 이미 성공한 단계는 재실행 안 함)
```

| 구분 | 전통적 DLQ | Temporal의 방식 |
| --- | --- | --- |
| 실패 데이터 위치 | 별도의 큐/토픽으로 이동 | Workflow Execution 자체가 그 자리에 남아있음 |
| 복구 방법 | DLQ에서 메시지를 꺼내 재처리 로직을 따로 실행 | 같은 Workflow에 Signal을 보내 그 지점부터 이어서 재개 |
| 이미 성공한 단계 | 재처리 로직에 따라 다시 실행될 수도 있음 | 재실행 안 됨 — Event History에 이미 성공으로 기록된 단계는 replay 시 건너뜀 |
| notify(알림) | DLQ 적재 자체를 이벤트로 감지해 알림 | `TemporalReportedProblems` 같은 검색 속성으로 실패한 Workflow를 탐지해 알림 발송 |

- notify(알림)는 동일한 목적을 가지지만, 그 알림을 트리거하는 게 "DLQ에 쌓였다"가 아니라 "Workflow가 실패/멈춤 상태로 감지됐다"라는 이벤트다.
- DLQ처럼 "별도 저장소로 옮기는" 동작은 없다 — Temporal 철학 자체가 "실패한 작업을 어딘가로 옮기지 말고, 그 자리(Event History)에 그대로 두고 그 지점부터 고쳐서 이어가자"는 것이기 때문이다.

### 8.3 Entry Point로서의 Workflow

```
[고객 앱] ──HTTP 요청──▶ [주문 API 서버 (얇은 게이트웨이)] ──client.execute_workflow()──▶ [Temporal Frontend Service]
                                                                                              │
                                                                                              ▼
                                                                                    DeliveryOrderWorkflow 시작
```

고객의 주문 요청이 도달하면, 그 이후의 모든 흐름(결제→조리/배차→알림)은 전부 `DeliveryOrderWorkflow` 안에서 결정된다. 개별 MS를 직접 호출하는 게 아니라 "이 Workflow를 시작해줘"라는 단일 요청만 진입점이 되는 것이다. 다만 실무에서는 얇은 주문 API 서버(FastAPI 등)가 앞단에서 HTTP 요청을 받아 `client.execute_workflow(...)`를 호출하는 프록시 역할을 한다. 모든 시작/조회/Signal 요청은 **Frontend Service**라는 stateless 게이트웨이를 거친다.

### 8.4 동기(gRPC) vs 비동기(Broker) 결합도 트레이드오프

**heartbeat_timeout이 결국 또 다른 타임아웃 의존이 되는 문제**는 피할 수 없는 근본적 비용이다 — 비동기로 가도 "확실성"을 얻는 게 아니라, 불확실성의 종류가 "얼마나 기다릴지"로 바뀔 뿐이다. 이건 분산 시스템에서 "저쪽이 죽었는지 그냥 느린지"를 100% 확실히 구분할 방법이 원래 없기 때문이다.

**결합(Coupling)에는 여러 종류가 있고, 비동기가 결합을 없애는 게 아니라 결합의 "종류"를 바꿀 뿐이다.**

| 결합 종류 | 동기(gRPC via Activity) | 비동기(Broker) |
| --- | --- | --- |
| **시간적 결합 (Temporal Coupling)** — 호출 시점에 상대가 떠 있어야 함 | ✅ 있음 — 단, Temporal의 Retry Policy가 이 고통을 크게 흡수 | ❌ 없음 — 상대가 꺼져있어도 큐에 안전하게 쌓임 |
| **공간적 결합 (Space Coupling)** — 상대의 네트워크 주소/프로토콜을 알아야 함 | ✅ 있음 (gRPC 엔드포인트 직접 지정) | ✅ 똑같이 있음 — 토픽명, 메시지 스키마를 알아야 함 |
| **설계 시점 결합 (Design-Time Coupling)** — 스키마/계약 변경이 서로에게 영향 | 낮음 (호출 즉시 실패해서 바로 알아챔) | ⚠️ 오히려 더 큰 위험 — "누가 이 이벤트를 구독하는지 파악 불가능", 스키마 바뀌면 예상 못한 다운스트림 장애 |

**핵심 통찰**: 비동기(Broker)로 가도 "공간적 결합"과 "설계 시점 결합"은 그대로 남고, 오히려 스키마 변경 추적이나 "누가 구독 중인지 파악"은 동기보다 더 어려워진다. Broker는 "시간적 결합"만 없앨 뿐이지 "결합 자체를 없애는 마법"이 아니다.

**gRPC의 "시간적 결합"은 정말 문제인가 — Temporal이 상당 부분 흡수함**:

```
[일반 동기 MSA 호출]                    [Temporal Activity를 통한 동기 호출]
A → B 직접 호출                        Workflow → Activity → B 호출
B 다운 → A도 즉시 에러                   B 다운 → Activity 실패 → Temporal이 자동 백오프 재시도
(A가 직접 재시도 로직을 짜야 함)          (1초→2초→4초...→100초, 개발자가 코드 안 짜도 됨)
```

"gRPC를 쓴다"는 것 자체가 문제가 아니라, "누가 그 실패를 흡수하느냐"가 문제다. Temporal의 Activity Retry Policy가 이 실패를 흡수해주기 때문에, 순수 MSA 간 직접 동기 호출보다는 결합의 고통이 훨씬 완화된다 — 다만 완전히 없어지는 건 아니다(결제 서비스가 몇 시간씩 다운되면 결국 재시도도 소진됨).

**선택 기준**:

| 판단 기준 | 동기(gRPC/HTTP via Activity) 선택 | 비동기(Broker+Signal) 선택 |
| --- | --- | --- |
| 다운스트림 처리가 원래 몇 초~몇십 초 안에 끝나는가 | ✅ (결제 승인/환불처럼 빠른 처리) | 부적합 — 굳이 복잡도만 늘림 |
| 다운스트림 처리가 원래 몇 분~며칠 걸리는가 (사람 승인, 배치 등) | 부적합 — gRPC로 몇 시간 붙잡고 있을 수 없음 | ✅ |
| 실패를 바로 알아야 하는가 | ✅ | heartbeat 추정에 의존 → 불확실성 감수 필요 |
| 멱등키/task_token/heartbeat 관리 복잡도를 감당할 여력 | 낮아도 됨 | 높은 엔지니어링 성숙도 필요 |

**결론**: `charge_payment`/`refund_payment`처럼 본질적으로 몇 초 안에 끝나는 결제 승인/환불은 gRPC(동기)로 가는 게 정답이다 — Temporal의 Retry Policy가 결합의 고통을 충분히 흡수해주고, heartbeat/멱등키/이중 재시도 같은 복잡도를 아예 피할 수 있기 때문이다. Broker+비동기 완료 패턴은, 정말로 처리가 오래 걸리는 단계에만 예외적으로 쓰는 게 맞는 방향이다.

---

## 9️⃣ 종합 예제 — 배달 서비스 SAGA Orchestrator (Python)

### 9.1 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                     배달 주문 MSA 구성도                            │
├─────────────────────────────────────────────────────────────────┤
│   클라이언트 ──(order_id로 Workflow 시작)──▶ Temporal Server         │
│                                                    │              │
│                                             DeliveryOrderWorkflow  │
│                                             (order_id = Workflow ID)│
│         ┌──────────────────────────┬───────────────┬────────────┐│
│         ▼                          ▼               ▼            ▼│
│   [결제 서비스]                [음식점 서비스]     [라이더 서비스]  [알림 서비스]│
│   charge_payment              start_cooking      assign_rider   notify_customer│
│   refund_payment(보정)          cancel_cooking(보정)                          │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 업무 흐름 (A → (B,C) → D 구조)

```
A: 결제 승인 (charge_payment)
   │
   ▼
┌──────────────────┬──────────────────┐
B: 조리 시작          C: 라이더 배정         ← 병렬 실행
(start_cooking)      (assign_rider)
└──────────────────┴──────────────────┘
   │
   ▼
D: 배달 확정 알림 (notify_customer)
```

| 단계 | 담당 MS | 정방향 Activity | 보상 Activity |
| --- | --- | --- | --- |
| A | 결제 서비스 | `charge_payment` | `refund_payment` |
| B | 음식점 서비스 | `start_cooking` | `cancel_cooking` |
| C | 라이더 서비스 | `assign_rider` | (배정 자체가 안 됐으므로 보상 불필요) |
| D | 알림 서비스 | `notify_customer` | (알림은 보상 불필요) |

### 9.3 공통 데이터 클래스

```python
# shared.py
from dataclasses import dataclass

@dataclass
class DeliveryOrderInput:
    order_id: str
    customer_id: str
    restaurant_id: str
    amount: float
```

### 9.4 Activity 정의

```python
# activities.py
from temporalio import activity
from shared import DeliveryOrderInput


@activity.defn
async def charge_payment(input: DeliveryOrderInput) -> str:
    activity.logger.info(f"[결제 서비스] {input.order_id} 결제 승인 (금액: {input.amount})")
    return f"payment-{input.order_id}"


@activity.defn
async def refund_payment(input: DeliveryOrderInput) -> None:
    activity.logger.info(f"[결제 서비스] {input.order_id} 환불 처리 시도")
    if input.order_id == "order-demo-fail":
        raise RuntimeError("결제사 API 응답 없음 — 환불 실패")


@activity.defn
async def start_cooking(input: DeliveryOrderInput) -> str:
    activity.logger.info(f"[음식점 서비스] {input.restaurant_id} 조리 시작")
    return "cooking-started"


@activity.defn
async def cancel_cooking(input: DeliveryOrderInput) -> None:
    activity.logger.info(f"[음식점 서비스] {input.restaurant_id} 조리 취소")


@activity.defn
async def assign_rider(input: DeliveryOrderInput) -> str:
    activity.logger.info(f"[라이더 서비스] {input.order_id} 라이더 탐색 중")
    raise RuntimeError("배차 가능한 라이더 없음")


@activity.defn
async def notify_customer(input: DeliveryOrderInput, message: str) -> None:
    activity.logger.info(f"[알림 서비스] 고객 {input.customer_id}에게: {message}")


@activity.defn
async def alert_ops_team(input: DeliveryOrderInput, reason: str) -> None:
    activity.logger.info(f"🚨[운영팀 알림] order={input.order_id} 수동 개입 필요 — {reason}")
```

### 9.5 Workflow (SAGA 오케스트레이터 본체)

```python
# workflow.py
import asyncio
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from shared import DeliveryOrderInput
    from activities import (
        charge_payment, refund_payment,
        start_cooking, cancel_cooking,
        assign_rider,
        notify_customer, alert_ops_team,
    )

FORWARD_RETRY = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=30),
    maximum_attempts=3,
)

COMPENSATION_RETRY = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=30),
    maximum_attempts=5,
)


@workflow.defn
class DeliveryOrderWorkflow:
    def __init__(self) -> None:
        self._ops_fixed: bool = False
        self._ops_note: str = ""

    @workflow.signal
    def operator_resolved(self, note: str) -> None:
        self._ops_note = note
        self._ops_fixed = True

    @workflow.run
    async def run(self, input: DeliveryOrderInput) -> str:
        compensations: list[tuple[str, object]] = []

        try:
            # ── A: 결제 승인 ─────────────────────────────────────
            await workflow.execute_activity(
                charge_payment, input,
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=FORWARD_RETRY,
            )
            compensations.append(("환불", refund_payment))

            # ── B, C: 조리 시작 + 라이더 배정 (병렬) ───────────────────
            cooking_result, rider_result = await asyncio.gather(
                workflow.execute_activity(
                    start_cooking, input,
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=FORWARD_RETRY,
                ),
                workflow.execute_activity(
                    assign_rider, input,
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=FORWARD_RETRY,
                ),
                return_exceptions=True,
            )

            if not isinstance(cooking_result, Exception):
                compensations.append(("조리취소", cancel_cooking))

            if isinstance(rider_result, Exception):
                raise rider_result   # 라이더 배정 최종 실패 → SAGA 보정 트리거

            # ── D: 배달 확정 알림 ────────────────────────────────
            await workflow.execute_activity(
                notify_customer, args=[input, "배달이 확정되었습니다!"],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=FORWARD_RETRY,
            )
            return f"{input.order_id}: 배달 주문 완료"

        except Exception as saga_error:
            workflow.logger.warning(f"SAGA 실패 감지, 보정 트랜잭션 시작: {saga_error}")
            await self._compensate(input, compensations, str(saga_error))
            return f"{input.order_id}: 주문 취소 및 보정 처리 완료"

    async def _compensate(
        self, input: DeliveryOrderInput, compensations, reason: str
    ) -> None:
        failed = []

        async def run_one(name: str, activity_fn) -> None:
            try:
                await workflow.execute_activity(
                    activity_fn, input,
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=COMPENSATION_RETRY,
                )
                workflow.logger.info(f"보정 성공: {name}")
            except Exception as e:
                workflow.logger.error(f"보정 최종 실패: {name} - {e}")
                failed.append(name)

        await asyncio.gather(*[
            run_one(name, fn) for name, fn in reversed(compensations)
        ])

        if failed:
            await workflow.execute_activity(
                alert_ops_team,
                args=[input, f"보정 실패 항목: {failed}, 원인: {reason}"],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=FORWARD_RETRY,
            )
            await workflow.wait_condition(lambda: self._ops_fixed)
            workflow.logger.info(f"운영자 조치 확인 완료: {self._ops_note}")
```

### 9.6 Worker & 실행 진입점

```python
# worker.py
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import DeliveryOrderWorkflow
from activities import (
    charge_payment, refund_payment,
    start_cooking, cancel_cooking,
    assign_rider, notify_customer, alert_ops_team,
)

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="delivery-task-queue",
        workflows=[DeliveryOrderWorkflow],
        activities=[
            charge_payment, refund_payment,
            start_cooking, cancel_cooking,
            assign_rider, notify_customer, alert_ops_team,
        ],
    )
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
```

```python
# starter.py — 주문을 시작시키는 클라이언트
import asyncio
from temporalio.client import Client
from shared import DeliveryOrderInput
from workflow import DeliveryOrderWorkflow

async def main():
    client = await Client.connect("localhost:7233")
    order = DeliveryOrderInput(
        order_id="order-1001",
        customer_id="cust-77",
        restaurant_id="rest-42",
        amount=18500,
    )
    result = await client.execute_workflow(
        DeliveryOrderWorkflow.run,
        order,
        id=order.order_id,          # ← Workflow ID = order_id
        task_queue="delivery-task-queue",
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

```python
# resolve_stuck_order.py — 운영자가 "일시정지"된 주문을 깨우는 스크립트
import asyncio
from temporalio.client import Client

async def main():
    client = await Client.connect("localhost:7233")
    handle = client.get_workflow_handle("order-demo-fail")
    await handle.signal("operator_resolved", "결제사 콘솔에서 수동 환불 처리 확인함")

if __name__ == "__main__":
    asyncio.run(main())
```

### 9.7 시나리오 ① — 정상 동작 (order_id = "order-1001")

| 순서 | 이벤트 | Event History에 기록되는 내용 |
| --- | --- | --- |
| 1 | `charge_payment` 성공 | ActivityTaskCompleted |
| 2 | `start_cooking` / `assign_rider` 병렬 실행 → 둘 다 성공 | ActivityTaskCompleted ×2 |
| 3 | `notify_customer` 성공 | ActivityTaskCompleted |
| 4 | Workflow 완료 | WorkflowExecutionCompleted → `"order-1001: 배달 주문 완료"` |

### 9.8 시나리오 ② — 보상 트랜잭션까지 실패 (order_id = "order-demo-fail")

```
1) charge_payment ✅ 성공        → 보정 스택: [환불]
2) start_cooking  ✅ 성공        → 보정 스택: [환불, 조리취소]
   assign_rider   ❌ 최종 실패    (FORWARD_RETRY 3회 재시도 후 포기)
      │
      ▼ SAGA 보정 트리거
3) 역순 보정 실행 (병렬):
   조리취소(cancel_cooking)  ✅ 성공
   환불(refund_payment)     ❌ 최종 실패 (COMPENSATION_RETRY 5회 재시도 후에도 실패)
      │
      ▼
4) alert_ops_team 실행 → 🚨 운영팀 알림 발송
5) workflow.wait_condition(self._ops_fixed) → Workflow "일시정지"
      (Temporal 관점에서는 여전히 Status=Running, Event History에 그대로 남아있음)
      │
      ▼ [사람이 개입: resolve_stuck_order.py 실행]
6) operator_resolved Signal 수신 → self._ops_fixed = True
7) Workflow 재개 → 완료 → "order-demo-fail: 주문 취소 및 보정 처리 완료"
```

### 9.9 코드-개념 매핑표

| 코드 위치 | 연결되는 개념 |
| --- | --- |
| `id=order.order_id` | Workflow ID = 트랜잭션(주문) 단위 상태 관리 |
| `retry_policy=FORWARD_RETRY` | Activity별 개별 Retry Policy (Broker 없이 Temporal이 자동 재시도) |
| `asyncio.gather(start_cooking, assign_rider)` | "A → (B,C) → D" 구조의 병렬 실행 |
| `compensations.append(...)` + 역순 실행 | SAGA 보상 트랜잭션 스택 |
| `COMPENSATION_RETRY` (더 많은 재시도) | "보상 트랜잭션도 실패할 수 있다"는 리스크에 대한 완화 전략 |
| `alert_ops_team` + `workflow.wait_condition` | DLQ 대신 Temporal이 쓰는 "일시정지 + Signal로 재개" 패턴 |
| `operator_resolved` Signal | Workflow ID가 이미 Running일 때 "추가 요청"이 Signal로 전달되는 방식 |

> ⚠️ 이 코드는 개념 이해를 위한 예제로, 실제 프로덕션에는 데이터 직렬화 설정, 타임아웃 세분화, 로깅/모니터링 연동이 추가로 필요하다.

### 9.10 확장 아이디어

`assign_rider`가 랜덤하게 성공/실패하도록 바꿔서 정상 시나리오와 실패 시나리오를 같은 코드로 반복 재현해보면, Retry Policy의 백오프 동작(1초→2초→4초)을 로그로 직접 확인할 수 있다.

---

## 📎 Sources

- [Temporal 공식 사이트](https://temporal.io/)
- [Temporal Workflow Execution 공식 문서](https://docs.temporal.io/workflow-execution)
- [Temporal Workers 공식 문서](https://docs.temporal.io/workers)
- [Temporal Blog - SAGA Pattern Mastery Guide](https://temporal.io/blog/mastering-saga-patterns-for-distributed-transactions-in-microservices)
- [Automation Atlas - Temporal Cloud vs Self-Hosted 2026](https://automationatlas.io/guides/temporal-cloud-vs-self-hosted-2026/)
- [Temporal Production Checklist](https://docs.temporal.io/self-hosted-guide/production-checklist)
- [Temporal Docs - Persistence](https://docs.temporal.io/temporal-service/persistence)
- [Temporal Docs - Visibility](https://docs.temporal.io/self-hosted-guide/visibility)
- [Temporal Community - Workflow ID Conflict Policy](https://ruby.temporal.io/Temporalio/WorkflowIDConflictPolicy.html)
- [Temporal Docs - Sending Messages (Signal-With-Start)](https://docs.temporal.io/sending-messages)
- [Temporal Docs - Asynchronous Activity Completion](https://docs.temporal.io/develop/python/activities/asynchronous-activity)
- [Temporal Community - Activity ID as Idempotency Key](https://community.temporal.io/t/is-a-system-generated-activity-id-suitable-to-use-as-an-idempotency-key/13181)
- [Temporal Docs - Detecting Activity Failures (Heartbeat)](https://docs.temporal.io/encyclopedia/detecting-activity-failures)
- [xgrid - Temporal Observability in Production Guide](https://www.xgrid.co/resources/temporal-observability-in-production-guide/)
- [xgrid - Temporal vs Kafka: Workflow Orchestration Guide](https://www.xgrid.co/resources/temporal-vs-kafka-workflow-orchestration/)
- [Kai Waehner - Durable Execution Engines in Event-Driven Architecture](https://www.kai-waehner.de/blog/2025/06/05/the-rise-of-the-durable-execution-engine-temporal-restate-in-an-event-driven-architecture-apache-kafka/)
- [Temporal Blog - Event-Driven Systems and the Truth About Loosely Coupled Architectures](https://temporal.io/blog/event-driven-systems-and-the-truth-about-loosely-coupled-architectures)
- [Temporal Blog - Recover Failed Workflow Steps Without Restarting](https://temporal.io/blog/keep-business-processes-moving)
- [Temporal Docs - Failure Detection (Go SDK)](https://docs.temporal.io/develop/go/failure-detection)
