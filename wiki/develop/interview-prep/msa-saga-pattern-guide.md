---
tags: [saga, msa, orchestration, choreography, temporal, durable-execution, dual-write]
created: 2026-04-14
---

# 📚 MSA SAGA 패턴 완전 가이드 — 보상 트랜잭션부터 Durable Execution까지

---

## 1. SAGA 패턴 개요

MSA에서 여러 서비스에 걸친 분산 트랜잭션을 관리하는 패턴. 하나의 큰 트랜잭션을 **로컬 트랜잭션의 연쇄**로 분해하고, 실패 시 **보상 트랜잭션**으로 되돌린다.

### 트랜잭션 구성 요소

```
T1 ──▶ T2 ──▶ T3 (Pivot) ──▶ T4 ──▶ T5
│       │       │
C1 ◀── C2 ◀── C3    (보상 트랜잭션, 역방향)

Compensable (되돌릴 수 있음) → Pivot (돌아올 수 없는 지점) → Retryable (반드시 성공)
```

> 출처: Chris Richardson — microservices.io, Microsoft Azure Architecture Center

---

## 2. Orchestration vs Choreography

### 아키텍처 비교

```
[Choreography — 중앙 지휘자 없음, 이벤트 기반]
  주문 ──"주문생성됨"──▶ 재고 ──"재고확보됨"──▶ 결제
       ◀────── 보상 Event ──────── 보상 Event ◀─┘

[Orchestration — 오케스트레이터가 Command/Reply로 제어]
                ┌──────────────┐
                │ 오케스트레이터 │
                └──────┬───────┘
           Command ▼  Command ▼  Command ▼
           주문 서비스  재고 서비스  결제 서비스
           Reply ▲     Reply ▲     Reply ▲
```

### 비교 매트릭스

| 기준              | Choreography                 | Orchestration                    |
| ----------------- | ---------------------------- | -------------------------------- |
| **제어**          | 분산 — 각 서비스 자율         | 중앙 — 오케스트레이터 지휘       |
| **결합도**        | 느슨 (이벤트만 의존)          | 중간 (Command/Reply)             |
| **가시성**        | ❌ 단일 아티팩트 없음         | ✅ 상태 머신으로 전체 파악       |
| **SPOF**          | ❌ 없음                      | ⚠️ 오케스트레이터 (HA로 완화)   |
| **복잡도 성장**   | 기하급수적                    | 선형                             |

### 선택 기준

| 기준       | Choreography        | Orchestration              |
| ---------- | ------------------- | -------------------------- |
| 서비스 수  | 2~4개               | 5개 이상                   |
| 워크플로우 | 단순 선형            | 분기/병렬/조건부           |
| 규제/감사  | 낮은 규제            | 금융/규제 (감사 추적 필수) |

### 실제 기업 적용

| 기업        | 방식              | 구현                                          |
| ----------- | ----------------- | --------------------------------------------- |
| **Uber**    | Orchestration     | Cadence → Temporal                            |
| **Netflix** | Orchestration     | Conductor (JSON DSL)                          |
| **Airbnb**  | Orchestration     | DAG 기반, 99.999% 일관성                      |
| **배민**    | Choreography      | SNS/SQS, Transactional Outbox                 |
| **쿠팡**    | Choreography 유사 | 자체 Vitamin MQ                               |

> 출처: 우아한형제들 기술블로그, Netflix Tech Blog

---

## 3. 보상 트랜잭션 (Compensating Transaction)

이미 커밋된 로컬 TX를 **논리적으로 되돌리는** 별도 작업.

```python
if updated == 0:  # Optimistic Lock 실패
    current = Order.objects.get(id=order_id)
    if current.status == 'cancelled':
        pos_client.cancel_order(pos_response.confirmation_id)  # 보상
    elif current.status == 'confirmed':
        pass  # 보상 불필요
```

### "보상의 보상" 재귀 함정

> Uwe Friedrichsen: "SAGA는 **비즈니스 에러**만 보상 가능. **기술적 에러**로 보상 실패 시 재귀 함정."

```
보상 실행 → 보상 실패 (서비스 다운) → 보상의 보상? → 또 실패? → ∞
```

| 유형             | 예시                       | SAGA 보상 가능? |
| ---------------- | -------------------------- | --------------- |
| **비즈니스 에러** | 재고 부족, 잔고 부족       | ✅ 결정론적     |
| **기술적 에러**   | 서비스 다운, 네트워크 장애 | ❌ 비결정론적   |

**해결**: 기술적 에러는 인프라 레벨(Retry + DLQ + Reconciliation + Durable Execution)에서 처리.

> 출처: ufried.com — "Limits of the Saga Pattern"

---

## 4. 보상 실패 시 6+1 계층 방어 모델

| Layer  | 패턴                                               | 자동화       |
| ------ | -------------------------------------------------- | ------------ |
| **0**  | 설계 시점 예방 (멱등성, Semantic Lock)              | N/A          |
| **1**  | Retry + Exponential Backoff (3~5회)                 | 완전 자동    |
| **2**  | Leveled Retry Topology (Main → Retry → DLQ)        | 완전 자동    |
| **3**  | DLQ 모니터링 + 알림 + Runbook                       | 반자동       |
| **4**  | Reconciliation 배치 Job                             | 스케줄 자동  |
| **5**  | Admin 대시보드 + 수동 개입                          | 사람         |
| **6**  | 금융 정산 T+1 Reconciliation                        | 감사         |
| **대안** | **Durable Execution Engine** (Layer 1~4 대체)      | 플랫폼 보장  |

> 출처: Microsoft Azure — Compensating Transaction Pattern

---

## 5. Dual-Write Problem

두 독립 시스템(DB + Kafka)에 동시에 써야 하는데 하나의 TX로 묶을 수 없는 문제.

```
DB COMMIT ✅ → Kafka produce 💥 = DB엔 있고 Kafka엔 없음
Kafka ✅ → DB COMMIT 💥 = Kafka엔 있고 DB엔 없음
```

### 해결 패턴

| 패턴                     | 동작                                             | 장점               | 단점               |
| ------------------------ | ------------------------------------------------ | ------------------ | ------------------ |
| **Transactional Outbox** | DB TX 안에 outbox 테이블 기록 → 별도 Kafka 발행  | 원자성 보장        | 추가 인프라        |
| **CDC (Debezium)**       | DB binlog → Kafka 자동 전달                      | Outbox poller 대체 | CDC 인프라, DB 종속 |
| **Listen-to-Yourself**   | Kafka 먼저 → Consumer가 DB 비동기 업데이트       | Dual-Write 회피    | DB Eventual        |

### Kafka에도 Outbox가 필요한가?

Kafka 트랜잭션은 Kafka→Kafka만 커버. DB+Kafka 원자성 필요하면 Outbox/CDC/Listen-to-Yourself 필요.

> 출처: Confluent — "Understanding the Dual-Write Problem"

---

## 6. Orchestration SAGA 실무 구현 패턴

### 금융 서비스 Orchestration SAGA 예시

오케스트레이터: 환전/송금 서버 \| 참여자: 출금 계좌, 입금 계좌

```
[성공] 오케스트레이터 ──HTTP 출금──▶ 계좌A ──HTTP 입금──▶ 계좌B → 완료
[실패] 입금 실패 → 오케스트레이터 ──Kafka 출금취소──▶ 계좌A (보상)
       ├─ 브로커 정상 → 서비스 브로커
       └─ 브로커 장애 → Fallback 브로커 (별도 Kafka)
```

### 브로커 장애 대응: PDL + CDL + 배치

| 장애 유형                  | 대응                                               |
| -------------------------- | -------------------------------------------------- |
| Kafka 브로커 다운          | Fallback 브로커 (별도 Kafka)가 수신                 |
| 앱 크래시 (produce 실패)   | 상태 테이블 + 배치 Job이 미완료 스캔                |
| Consumer 처리 실패         | CDL 브로커 → DL Server 재시도                       |

상태 테이블이 Outbox 역할을 하고, Fallback 브로커가 브로커 장애를 담당하는 구조.

---

## 7. Durable Execution Engine — Temporal & Restate

### 개념: 크래시에도 안전한 코드 실행

```
비유: 비디오 게임
  세이브 없음 (일반) → 크래시 시 처음부터
  자동 세이브 (Temporal) → 모든 행동 기록, 마지막 지점부터 재개
```

### Temporal 동작: Event Sourcing + History Replay

모든 단계를 이벤트로 기록. 크래시 시 새 Worker가 이벤트 히스토리를 재생하되, 완료된 Activity는 기록된 결과 반환, 미완료 지점부터 실제 실행.

### SAGA 보상 (Python + Temporal)

```python
@workflow.defn
class BookingWorkflow:
    @workflow.run
    async def run(self, input):
        compensations = []
        try:
            compensations.append(undo_book_car)
            await workflow.execute_activity(book_car, input, ...)
            compensations.append(undo_book_hotel)
            await workflow.execute_activity(book_hotel, input, ...)
            return {"status": "success"}
        except Exception:
            for compensation in reversed(compensations):
                await workflow.execute_activity(compensation, input, ...)
            return {"status": "failure"}
```

### Temporal vs Restate

| 항목           | Temporal                              | Restate                                |
| -------------- | ------------------------------------- | -------------------------------------- |
| **아키텍처**   | 외부 클러스터 (Cassandra + ES)        | 단일 Rust 바이너리 (Bifrost 내장)      |
| **코드 모델**  | Workflow + Activity 분리 필수         | 일반 함수에서 `ctx.run()` 내구성 지정  |
| **적합한 경우** | 대규모 엔터프라이즈                   | 가벼운 배포, HTTP 서비스 내구성 추가   |

### ⚠️ Temporal 한계 (rl-verify 검증)

| 한계                              | 심각도   |
| --------------------------------- | -------- |
| **50K 이벤트 하드 리밋**          | CRITICAL |
| **결정론 제약** (datetime, random 금지) | CRITICAL |
| **복잡도 이동** (제거 아님)       | CRITICAL |
| **SAGA 보상 5가지 실패 모드**     | CRITICAL |
| **Self-host 운영 오버헤드**       | MODERATE |
| **벤더 종속 (SDK lock-in)**       | MODERATE |
| **사용 기업**: Snap, Stripe, Datadog (~~Uber~~ → Cadence) | 정정 |

### 프레임워크 비교

| 항목           | Temporal              | Netflix Conductor       | Axon Framework     |
| -------------- | --------------------- | ----------------------- | ------------------ |
| **SAGA 유형**  | Orchestration         | Orchestration           | 둘 다             |
| **워크플로우** | 코드 (Go, Java, TS, Python) | JSON DSL            | 코드 (Java/Kotlin) |
| **프로덕션**   | Snap, Stripe, Datadog | Netflix, Tesla, J.P.Morgan | ING             |

---

## 📎 출처

| 출처                                             | 주제                               |
| ------------------------------------------------ | ---------------------------------- |
| Chris Richardson — microservices.io              | SAGA 정의, Countermeasures         |
| Microsoft Azure Architecture Center             | Saga, Compensating Transaction     |
| Uwe Friedrichsen — "Limits of the Saga Pattern" | 보상 재귀 한계                     |
| Confluent                                        | Dual-Write, Outbox, Listen-to-Yourself |
| Temporal 공식 문서/블로그                        | Durable Execution, History Replay  |
| Restate 공식 문서                                | Bifrost, Durable Async/Await       |
| rl-verify 검증 결과                              | Temporal 한계, 사용 기업 정정      |
