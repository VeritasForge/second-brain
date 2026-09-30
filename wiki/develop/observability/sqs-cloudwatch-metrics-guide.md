---
tags: [aws, sqs, cloudwatch, observability, monitoring, fifo]
created: 2026-09-30
---

# Amazon SQS CloudWatch 지표 해설: 의미, 관계, 모니터링 방법

## 목차

1. 용어집
2. 메시지 한 건의 생애와 지표가 재는 구간
3. 지표의 두 종류: 상태 지표와 사건 지표
4. 상태 지표 5종
   - 4.1 ApproximateAgeOfOldestMessage
   - 4.2 ApproximateNumberOfMessagesVisible
   - 4.3 ApproximateNumberOfMessagesNotVisible
   - 4.4 ApproximateNumberOfMessagesDelayed와 지연 전송
   - 4.5 ApproximateNumberOfGroupsWithInflightMessages (FIFO 전용)
5. 사건 지표 7종
   - 5.1 NumberOfMessagesSent와 NumberOfMessagesReceived
   - 5.2 NumberOfMessagesDeleted
   - 5.3 NumberOfEmptyReceives
   - 5.4 NumberOfDeduplicatedSentMessages와 FIFO 중복 제거
   - 5.5 SentMessageSize
6. 지표를 조합해서 읽는 법
   - 6.1 Age와 Visible의 관계
   - 6.2 NotVisible과 GroupsWithInflight가 벌어질 때
   - 6.3 소비자를 늘려야 하는가
   - 6.4 "EmptyReceives 0 + Received 0"의 의미
7. 대시보드 예시 읽기
8. 대시보드·알람 구성 권장안
9. 실행 가능한 예제
10. 주의점
11. 정리

---

## 1. 용어집

| 용어                                        | 뜻                                                                                                                                                                                 |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **생산자 (producer)**                       | `SendMessage`로 큐에 메시지를 넣는 쪽                                                                                                                                              |
| **소비자 (consumer)**                       | `ReceiveMessage`로 큐에서 메시지를 가져가 처리하는 쪽                                                                                                                              |
| **pull 방식**                               | 큐가 소비자에게 밀어 주지 않고, 소비자가 직접 요청해서 가져가는 방식입니다. SQS는 pull 방식입니다                                                                                  |
| **long polling**                            | `ReceiveMessage`를 호출할 때 `WaitTimeSeconds`(최대 20초)만큼 메시지가 올 때까지 기다리는 방식입니다. 메시지가 오면 곧바로 반환하고, 끝까지 오지 않으면 빈 응답을 반환합니다       |
| **가시성 시간 (visibility timeout)**        | 소비자가 메시지를 받아 간 뒤 다른 소비자에게 그 메시지를 숨겨 두는 시간입니다. 이 시간 안에 삭제하지 않으면 메시지가 다시 보이게 되고 재배달됩니다                                 |
| **in-flight (처리 중)**                     | 받아 갔지만 아직 삭제하지 않았고 가시성 시간도 끝나지 않은 상태                                                                                                                    |
| **재배달 (redelivery)**                     | 삭제되지 않은 메시지가 가시성 시간이 끝난 뒤 다시 소비자에게 전달되는 것                                                                                                           |
| **FIFO 큐**                                 | 순서를 보장하는 큐입니다. 메시지 그룹 단위로 순서를 지키고, 중복 제거 기능이 있습니다                                                                                              |
| **메시지 그룹 (`MessageGroupId`)**          | FIFO 큐에서 순서를 보장하는 단위입니다. 같은 그룹 안에서는 엄격하게 순서대로 처리되고, 다른 그룹끼리는 병렬로 처리될 수 있습니다. 예를 들어 "채팅방별", "고객별"로 그룹을 나눕니다 |
| **중복 제거 ID (`MessageDeduplicationId`)** | FIFO 큐가 중복 메시지를 가려내는 데 쓰는 식별자                                                                                                                                    |
| **DLQ (Dead Letter Queue)**                 | 정해진 횟수(`maxReceiveCount`) 이상 처리에 실패한 메시지를 옮겨 두는 별도의 큐                                                                                                     |
| **backoff**                                 | 실패한 작업을 곧바로 다시 하지 않고 간격을 두고 재시도하는 방식                                                                                                                    |
| **debounce**                                | 짧은 시간에 연달아 발생한 사건을 모았다가 마지막 사건 뒤 한 번만 처리하는 방식                                                                                                     |
| **통계 (statistic)**                        | CloudWatch가 한 기간(period) 안의 데이터 포인트를 합치는 방법입니다. `Sum`, `Average`, `Maximum` 등이 있습니다                                                                     |

---

## 2. 메시지 한 건의 생애와 지표가 재는 구간

지표 이름만 봐서는 각 지표가 메시지 생애의 어느 구간을 재는지 알기 어렵습니다. 아래 그림에서 먼저 위치를 잡아 두면 이후 설명을 따라가기 쉽습니다.

```
 생산자                                      큐                              소비자
   │  SendMessage                                                              │
   ├──────────────▶ ┌─ 중복 ID면 버림 ──────────── NumberOfDeduplicatedSentMessages
   │                │
   │   Sent·Size ◀──┤  [지연 중] ─── MessagesDelayed
   │                ▼
   │           [보임 = 대기 중] ── MessagesVisible, AgeOfOldestMessage
   │                │  ReceiveMessage ───────────────────────────────────────┤
   │                │     빈 응답 ─────────────── NumberOfEmptyReceives      │
   │                ▼     받음 ────────────────── NumberOfMessagesReceived   │
   │           [안 보임 = 처리 중] ── MessagesNotVisible,                    │
   │                │                 GroupsWithInflightMessages(FIFO)        │
   │                │  DeleteMessage ─────────────────────────────────────────┤
   │                ▼     성공 ────────────────── NumberOfMessagesDeleted
   │               끝      (삭제하지 않고 가시성 시간이 지나면 → 다시 [보임] 으로)
```

상태 전이만 따로 그리면 다음과 같습니다.

```
            SendMessage
                │
                ▼
         ┌─────────────┐  지연 시간 종료   ┌─────────────┐  ReceiveMessage  ┌─────────────┐
         │   Delayed   │ ───────────────▶ │   Visible   │ ───────────────▶ │ NotVisible  │
         │ (지연 중)    │                  │ (대기 중)    │                  │ (처리 중)    │
         └─────────────┘                  └─────────────┘ ◀─────────────── └─────────────┘
          (지연이 없으면                                    가시성 시간 만료      │
           곧바로 Visible)                                  (= 재배달 준비)      │ DeleteMessage
                                                                                ▼
                                                                              삭제됨
```

---

## 3. 지표의 두 종류: 상태 지표와 사건 지표

12개 지표는 두 종류로 나뉩니다.

| 종류                    | 이름 패턴                      | 재는 것                                       | 권장 통계                          | 비유       |
| ----------------------- | ------------------------------ | --------------------------------------------- | ---------------------------------- | ---------- |
| **상태 지표** (gauge)   | `Approximate…`                 | 그 순간 큐 안에 무엇이 얼마나 있는가          | `Maximum`                          | 사진 한 장 |
| **사건 지표** (counter) | `NumberOf…`, `SentMessageSize` | 한 기간 동안 어떤 API 호출이 몇 번 일어났는가 | `Sum` (크기는 `Average`/`Maximum`) | 출입 기록  |

통계를 잘못 고르면 그래프가 다르게 읽힙니다.

- **상태 지표에 `Sum`을 쓰면** 1분 동안 여러 번 찍힌 스냅샷이 더해져서 실제보다 큰 값이 나옵니다.
- **사건 지표에 `Average`를 쓰면** 기간 안의 총 발생 횟수가 아니라 데이터 포인트당 평균이 나와서 실제보다 작게 보입니다.

공통 특성도 있습니다.

- SQS의 분산 구조 때문에 `Approximate…` 지표는 **근사값**입니다. 대부분의 경우 실제 값에 가깝지만 정확한 수치는 아닙니다.
- AWS 문서에 따르면 모든 지표는 **큐가 활성 상태일 때만** 음수가 아닌 값을 냅니다. 오랫동안 아무 활동이 없는 큐는 지표가 비어 보일 수 있습니다. 비활성으로 판정되기까지의 시간(약 6시간)은 확인이 필요합니다.
- CloudWatch 지표의 차원(dimension)은 `QueueName` 하나뿐입니다. 즉 **그룹별, 소비자별 값은 나오지 않습니다.**

---

## 4. 상태 지표 5종

### 4.1 ApproximateAgeOfOldestMessage (가장 오래된 메시지의 대략적인 수명)

**의미:** 아직 처리되지 않은 메시지 중 가장 오래된 것이 큐에 들어온 뒤 흐른 시간(초)입니다.

**읽는 법:** 모니터링에서 **가장 중요한 지표**입니다. 소비가 밀리거나 멈추면 이 값이 계속 올라갑니다. 사용자가 느끼는 "얼마나 늦었나"에 가장 가까운 지표입니다.

**큐 종류별 주의점** (AWS 문서 기준):

- **표준 큐:** 3번 이상 받아 갔는데도 삭제되지 않은 메시지는 큐 뒤쪽으로 옮겨지고 이 지표에서 빠집니다. 반복해서 실패하는 메시지(poison pill)가 Age를 끌어올리지 않는 대신, **그런 메시지가 있어도 Age로는 보이지 않을 수 있습니다.**
- **FIFO 큐:** 순서를 지키려고 메시지를 재배치하지 않습니다. 그래서 실패한 메시지 한 건이 삭제되거나 만료될 때까지 **그 그룹 전체를 막습니다.** 이때 Age가 계속 오릅니다.
- **DLQ로 옮겨진 메시지:** DLQ 쪽 Age는 원래 전송 시각이 아니라 옮겨진 시각부터 다시 셉니다.
- 메시지가 하나도 없으면 값이 보고되지 않습니다(데이터 없음).

> ❔ 받아 간 뒤 아직 삭제하지 않은(in-flight) 메시지가 Age 계산에 포함되는지는 문서에 명시되어 있지 않습니다. 문서는 "처리되지 않은(unprocessed) 메시지 중 가장 오래된 것"이라고만 적고 있습니다. (확인 필요)

### 4.2 ApproximateNumberOfMessagesVisible (표시된 메시지의 대략적인 수)

**의미:** 지금 바로 받아 갈 수 있는 대기 메시지 수, 즉 **적체량**입니다.

**읽는 법:**

- 계속 높게 유지되면 소비자가 모자라거나 처리가 막혔다는 신호입니다.
- 쌓일 수 있는 개수에 상한은 없습니다. 다만 큐의 보관 기간(retention period)이 지나면 메시지가 **알림 없이** 사라집니다.
- DLQ의 상태를 볼 때는 이 지표를 씁니다(5.1에서 설명하듯 DLQ의 Sent는 자동 이동분을 세지 않습니다).

### 4.3 ApproximateNumberOfMessagesNotVisible (표시되지 않는 메시지의 대략적인 수)

**의미:** 소비자가 받아 갔지만 아직 삭제하지 않은 메시지 수, 즉 **처리 중인 메시지 수**입니다.

**읽는 법:**

- 소비자의 동시 처리 상한(워커 수, 동시 실행 수) 부근에 계속 붙어 있으면 **소비자가 포화**된 것입니다.
- 처리가 느려지거나 소비자가 멈췄을 때도 올라갑니다.

**주의:** AWS 문서에 따르면 SQS 내부 서버 일부가 지표 보고 시점에 응답하지 못하면, 큐가 비어 있어도 **0이 아닌 값이 잠깐 찍힐 수 있습니다.** 보통 몇 분 안에 풀리므로, 이 지표로 알람을 걸 때는 한 점이 아니라 **연속된 여러 데이터 포인트**로 판정해야 합니다.

### 4.4 ApproximateNumberOfMessagesDelayed (지연된 메시지의 대략적인 수)와 지연 전송

**의미:** 지연 설정 때문에 아직 꺼낼 수 없는 메시지 수입니다.

#### 지연 전송이란

보낸 메시지를 정해 둔 시간 동안 소비자에게 보이지 않게 숨겨 두는 기능입니다. 설정 범위는 0초부터 최대 15분(900초)까지입니다.

```
 SendMessage ──▶ [숨김: DelaySeconds 동안] ──▶ [보임] ──▶ 소비자가 받아 감
                  ↑ 이 구간이 MessagesDelayed
```

거는 방법은 두 가지입니다.

| 방법                              | 범위                | 설정 위치                               | FIFO 지원                                      |
| --------------------------------- | ------------------- | --------------------------------------- | ---------------------------------------------- |
| **지연 큐 (delay queue)**         | 큐 전체의 기본 지연 | 큐 속성 `DelaySeconds`                  | ✅                                             |
| **메시지 타이머 (message timer)** | 메시지 한 건        | `SendMessage`의 `DelaySeconds` 파라미터 | ❌ FIFO 큐는 메시지별 지연을 지원하지 않습니다 |

추가로 알아 둘 동작이 있습니다.

- 메시지 타이머 값은 지연 큐의 기본값보다 우선합니다.
- 큐 단위 지연 설정을 바꾸면 **표준 큐에서는 이미 들어 있는 메시지에 적용되지 않고**, **FIFO 큐에서는 이미 들어 있는 메시지에도 적용됩니다.**
- 15분보다 긴 예약이 필요하면 AWS는 EventBridge Scheduler를 권합니다.

**가시성 시간과의 차이:** 둘 다 메시지를 소비자에게 숨긴다는 점은 같습니다. 지연은 **큐에 넣은 직후**에 숨기고, 가시성 시간은 **소비자가 받아 간 직후**에 숨긴다는 점이 다릅니다.

#### 지연 전송은 왜 쓰나

핵심은 **"지금 바로 처리하면 안 되고, 조금 기다렸다가 처리해야 맞는" 상황에서, 소비자가 타이머를 따로 두지 않고 큐가 대신 기다려 주게 하는 것**입니다. AWS 문서가 직접 드는 용도는 "소비자 애플리케이션이 메시지를 처리하기 전에 추가 시간이 필요할 때"입니다. 실무에서 흔히 쓰는 경우는 다음과 같습니다(일반적인 사용 사례이며 문서 원문은 아닙니다).

| 상황                                         | 예시                                                                           | 지연이 없으면                                                       |
| -------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| ⏳ **앞선 작업이 반영되기를 기다림**         | 주문을 DB에 쓰고 "주문 생성" 메시지를 보냄. 소비자는 복제본 DB에서 주문을 읽음 | 소비자가 복제 지연 때문에 "주문 없음"을 보고 실패합니다             |
| 🔁 **재시도 간격 두기 (backoff)**            | 외부 API 호출이 실패하면 30초 뒤에 다시 시도하도록 메시지를 다시 넣음          | 실패한 호출을 곧바로 반복해 상대 서비스를 계속 두드립니다           |
| 🧺 **잠깐 모았다가 한 번에 처리 (debounce)** | 사용자가 채팅을 연달아 보낼 때 1분 기다렸다가 한 번에 처리                     | 메시지마다 처리가 돌아 비용이 늘고, 대화가 끊긴 상태에서 판단합니다 |
| 🕐 **짧은 예약 실행**                        | "10분 뒤 알림 보내기"                                                          | 별도의 스케줄러가 필요합니다                                        |

FIFO 큐는 메시지별 지연을 걸 수 없으므로 🔁 backoff처럼 메시지마다 지연이 달라야 하는 용도에는 쓸 수 없습니다. 이런 경우에는 애플리케이션이 직접 보류 창을 두는 방식을 씁니다. 예를 들어 막 들어온 데이터는 판단을 미루고 "다음 회차에 다시 보라"고 표시해 되돌려 보내는 방식입니다.

**읽는 법:** 지연 기능을 쓰지 않는 큐라면 이 값은 **항상 0이 정상**입니다. 0이 아니라면 누군가 큐 설정을 바꿨다는 신호입니다.

### 4.5 ApproximateNumberOfGroupsWithInflightMessages (수신 후 미삭제 메시지가 있는 그룹의 대략적인 수), FIFO 전용

**의미:** 처리 중인 메시지를 하나 이상 가진 **메시지 그룹의 수**입니다. 큐 전체에 대해 **숫자 하나**가 나오며, 그룹별 값이 나오는 지표가 아닙니다.

NotVisible과 비교하면 차이가 분명해집니다.

| 지표                         | 세는 단위                                     | 예시 (그룹 A에서 2건, 그룹 B에서 1건 처리 중) |
| ---------------------------- | --------------------------------------------- | --------------------------------------------- |
| `MessagesNotVisible`         | 처리 중인 **메시지** 수                       | **3**                                         |
| `GroupsWithInflightMessages` | 처리 중인 메시지가 1건이라도 있는 **그룹** 수 | **2** (A, B)                                  |

**읽는 법:**

- 그룹을 채팅방·고객 단위로 나눴다면 "**동시에 처리 중인 채팅방·고객 수**"로 읽으면 됩니다.
- 값이 높으면 동시 처리가 잘 되고 있다는 뜻입니다.
- 적체(Visible)가 큰데 이 값이 낮게 유지되면, 소비자를 늘리거나 활성 그룹 수를 늘리는 것을 검토합니다(6.3 참고).

두 지표가 벌어지는 경우의 해석은 6.2에서 다룹니다.

---

## 5. 사건 지표 7종

### 5.1 NumberOfMessagesSent와 NumberOfMessagesReceived

**이름은 큐가 아니라 API를 부르는 쪽을 기준으로 붙어 있습니다.** SQS는 pull 방식이라 큐가 스스로 무언가를 보내는 일은 없습니다.

```
 생산자 ──SendMessage──▶  [ 큐 ]  ◀──ReceiveMessage── 소비자
         └ NumberOfMessagesSent        └ NumberOfMessagesReceived
           "생산자가 큐에 보낸 수"          "소비자가 큐에서 받아 간 수"
```

| 구분                       | Sent                                                  | Received                                |
| -------------------------- | ----------------------------------------------------- | --------------------------------------- |
| 누가 부르나                | 생산자                                                | 소비자                                  |
| 무엇을 세나                | 큐에 **성공적으로 추가된** 메시지 수                  | `ReceiveMessage`가 **돌려준** 메시지 수 |
| 같은 메시지를 여러 번 세나 | 아니요                                                | **예.** 재배달되면 또 셉니다            |
| 빠지는 것                  | 중복 제거로 버려진 전송, DLQ로 **자동** 이동한 메시지 | 없음                                    |

**읽는 법:**

- 정상이라면 Sent ≈ Received입니다.
- **Received가 Sent보다 꾸준히 크면 재배달이 일어나고 있다**는 신호입니다. 처리에 실패해 삭제하지 못했거나, 처리가 가시성 시간보다 오래 걸린 경우입니다.
- DLQ에서는 사람이 직접 보낸 메시지만 Sent로 셉니다. 자동 이동분은 빠지므로 DLQ에서는 Sent와 Received가 맞지 않을 수 있습니다.

### 5.2 NumberOfMessagesDeleted (삭제된 메시지 수)

**의미:** 성공한 삭제 요청 수, 즉 **처리 완료 수**입니다.

**주의:** 같은 메시지를 두 번 삭제해도 두 번 셉니다. 예를 들어 가시성 시간이 끝나 재배달된 메시지를 새 수신 핸들로 다시 삭제하거나, 같은 핸들로 삭제를 두 번 호출해도 모두 성공으로 셉니다. 그래서 고유 메시지 수와 정확히 일치하지는 않습니다.

**읽는 법:** Deleted가 Sent보다 계속 작으면 적체가 쌓이는 중입니다. 따라서 Sent, Received, Deleted 세 선을 **한 그래프에 겹쳐 그리는 것**이 좋습니다.

```
 정상                           재배달 발생                     적체 증가
 Sent     ────────              Sent     ────────              Sent     ────────
 Received ────────              Received ═══════▲ (위로 벌어짐)  Received ─────
 Deleted  ────────              Deleted  ────────              Deleted  ────▼ (아래로 벌어짐)
```

### 5.3 NumberOfEmptyReceives (비어 있는 수신 수)

**의미:** 메시지 없이 빈손으로 끝난 `ReceiveMessage` **호출** 수입니다.

**흔한 오해:** "소비자 8개 중 EmptyReceives가 4면, 4개는 메시지를 가져가고 4개는 빈손이었다"는 해석은 **틀렸습니다.** EmptyReceives는 **API 호출 횟수**를 세고, Received는 **메시지 건수**를 셉니다. 둘 다 소비자 수와 직접 대응하지 않습니다.

long polling의 동작부터 보면 이해가 쉽습니다.

```
 소비자 ── ReceiveMessage(최대 20초 대기) ──▶ 큐
          ├ 20초 안에 메시지가 오면 → 즉시 반환  → Received +건수
          └ 20초 동안 아무것도 없으면 → 빈 반환 → EmptyReceives +1 → 곧바로 다시 호출
```

**계산 예시** (`WaitTimeSeconds=20`, 1분 기준):

| 상황                                                  | EmptyReceives           | Received |
| ----------------------------------------------------- | ----------------------- | -------- |
| 한가한 소비자 1개                                     | 약 3 (20초마다 빈 반환) | 0        |
| 한가한 소비자 8개                                     | 약 24                   | 0        |
| 소비자 1개가 쉬지 않고 메시지 8건을 연속 처리         | 0                       | 8        |
| 소비자 8개가 모두 처리 중이라 아무도 받으러 오지 않음 | 0                       | 0        |
| 모든 소비자가 죽음                                    | 0                       | 0        |

즉 **EmptyReceives가 0이어도 모든 메시지를 가져갔다는 뜻은 아닙니다.** 소비자가 쉴 틈 없이 바빴거나, 아예 호출하지 않았다는 뜻입니다.

**읽는 법:**

- 값이 꾸준히 있으면 **소비자가 살아서 폴링 중**이라는 신호에 가깝습니다. 장애 신호가 아닙니다.
- long polling 대신 short polling(대기 없이 즉시 반환)을 쓰면 값이 매우 커지고, API 호출 비용도 늘어납니다. 이 지표로 폴링 방식을 조정할 수 있습니다.
- AWS 문서는 이 지표가 서비스 쪽 동작을 반영하며 재시도가 포함될 수 있어서, 큐 상태를 정확히 보여 주는 지표는 아니라고 말합니다.
- "EmptyReceives 0 + Received 0"의 해석은 6.4에서 다룹니다.

### 5.4 NumberOfDeduplicatedSentMessages (중복 제거된 전송 메시지 수)와 FIFO 중복 제거

**의미:** FIFO 큐에서 중복으로 판정되어 큐에 추가되지 않은 전송 수입니다. FIFO 큐에만 중복 제거 기능이 있으므로 이 지표도 FIFO 전용입니다.

#### 중복 제거 메커니즘

`SendMessage` API 레퍼런스 원문을 기준으로 정리하면 다음과 같습니다.

**① 모든 메시지에는 중복 제거 ID가 있어야 합니다.** 정하는 방법은 두 가지입니다.

| 방법                                              | 동작                                                                                                    |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| 보내는 쪽이 직접 지정                             | `MessageDeduplicationId` 파라미터에 값을 넣습니다 (최대 128자)                                          |
| 내용 기반 중복 제거 (`ContentBasedDeduplication`) | 큐 속성을 켜 두면 SQS가 **본문의 SHA-256 해시**로 ID를 만듭니다. 메시지 속성은 해시에 포함되지 않습니다 |
| 둘 다 없음                                        | 전송이 에러로 실패합니다                                                                                |

내용 기반 중복 제거가 켜져 있어도 직접 지정한 ID가 우선합니다.

**② 5분 창 안에 같은 ID가 다시 오면 성공으로 응답하지만 전달하지 않습니다.** 원문은 다음과 같습니다.

> "If a message with a particular `MessageDeduplicationId` is sent successfully, any messages sent with the same `MessageDeduplicationId` are accepted successfully but aren't delivered during the 5-minute deduplication interval."

보낸 쪽은 **성공 응답을 받습니다.** 그래서 생산자 로그에는 에러가 남지 않고, **중복 제거가 일어났다는 사실은 이 지표로만 알 수 있습니다.**

**③ 메시지를 이미 받아 가서 삭제했어도 5분 동안은 ID를 기억합니다.** 원문은 "Amazon SQS continues to keep track of the message deduplication ID even after the message is received and deleted."입니다. 5분이 지나면 같은 ID도 새 메시지로 받아들입니다.

**④ 한계:** 전송은 성공했지만 응답을 잃어버린 생산자가 **5분이 지난 뒤에** 같은 ID로 다시 보내면 SQS는 중복을 알아채지 못합니다.

```
 t=0:00  Send(id="room-123#tick-42")  → 큐에 추가       Sent +1
 t=0:30  Send(id="room-123#tick-42")  → 성공 응답, 버림  Deduplicated +1
 t=2:00  소비자가 받아 가서 삭제
 t=3:00  Send(id="room-123#tick-42")  → 성공 응답, 버림  Deduplicated +1  (삭제 후에도 기억)
 t=5:01  Send(id="room-123#tick-42")  → 큐에 추가       Sent +1          (창이 끝남)
```

#### 설계 예시: 주기 작업의 중복 적재 막기

주기적으로 "처리할 대상"을 골라 큐에 넣는 스케줄러를 생각해 보겠습니다. 스케줄러 인스턴스가 두 개 떠 있거나 재시도가 일어나면 같은 대상이 두 번 들어갈 수 있습니다. 중복 제거 ID를 `"{대상 ID}#{주기 구간 번호}"`로 만들면 다음과 같이 동작합니다.

- 같은 주기 구간 안에서 같은 대상을 두 번 넣으려 하면 두 번째는 버려집니다.
- 다음 구간이 되면 ID가 바뀌므로 정상적인 재적재는 막히지 않습니다.
- 주기가 5분 이하이면 한 구간이 중복 제거 창 안에 들어가므로 구간 안의 중복은 모두 걸러집니다. 주기가 5분보다 길면 같은 구간 안에서도 5분이 지난 뒤의 재전송은 걸러지지 않는다는 점에 주의해야 합니다.

**읽는 법:**

- 가끔 찍히는 값은 **중복 제거 장치가 의도대로 동작했다는 흔적**이므로 문제가 아닙니다.
- 값이 계속 높으면 생산자가 같은 메시지를 반복해서 보내고 있다는 뜻입니다. 생산자 쪽 재시도 로직이나 중복 실행을 점검합니다.

### 5.5 SentMessageSize (전송된 메시지 크기)

**의미:** 전송된 메시지의 크기(바이트)입니다.

**읽는 법:**

- 최대 크기는 1 MiB(1,048,576바이트)입니다.
- 첫 메시지가 전송되기 전에는 콘솔에 나타나지 않습니다.
- 페이로드 추세를 보거나 처리량 비용을 추정하는 데 씁니다. 크기가 갑자기 커지면 생산자가 보내는 내용이 바뀌었다는 신호입니다.
- 크기가 일정한 큐라면 이 값으로 "이 큐에 무엇이 들어가는지"를 역으로 추정할 수도 있습니다. 예를 들어 크기가 계속 3바이트 안팎이라면 본문이 짧은 ID 하나뿐인 큐일 가능성이 큽니다.

---

## 6. 지표를 조합해서 읽는 법

지표 하나만 보면 잘못 판단하기 쉽습니다. 실무에서 자주 나오는 네 가지 조합을 정리합니다.

### 6.1 Age와 Visible의 관계

"Visible이 늘면 Age도 늘고, 결국 적재량이 늘어 얼마나 지연되는지를 Age로 본다"는 이해는 **절반만 맞습니다.** Visible이 늘면 Age도 늘어나는 경우가 많지만, 둘은 비례하지 않고 **서로 다른 것을 잽니다.**

| 지표                 | 재는 것                                        | 비유                              |
| -------------------- | ---------------------------------------------- | --------------------------------- |
| `MessagesVisible`    | 대기 줄의 **길이** (몇 건이 기다리나)          | 은행 대기 인원                    |
| `AgeOfOldestMessage` | 맨 앞 사람이 **기다린 시간** (얼마나 늦어졌나) | 가장 오래 기다린 손님의 대기 시간 |

둘이 따로 움직이는 대표적인 세 가지 경우는 다음과 같습니다.

```
 ① 순간 폭주, 처리는 빠름        ② 한 건이 막힘 (FIFO)           ③ 소비가 유입보다 느림
 Visible ▁▁█▇▃▁▁                  Visible ▁▁▁▁▁▁▁ (1건)          Visible ▁▂▃▄▅▆▇
 Age     ▁▁▂▂▁▁▁                  Age     ▁▂▃▄▅▆▇                Age     ▁▂▃▄▅▆▇
 → 정상. 금방 소화됨              → 양은 적은데 늦어지는 중       → 둘 다 오름. 전형적인 적체
```

**②가 특히 위험합니다.** FIFO 큐에서 삭제에 실패한 메시지 한 건이 그 그룹을 막으면, 큐 전체 건수는 적어도 그 그룹의 사용자(예: 특정 채팅방)는 계속 응답을 받지 못합니다. **Visible만 보고 있으면 놓치는 장애입니다.**

③처럼 안정적으로 적체가 쌓이는 상황에서는 대략 다음 관계가 성립합니다(대기열 이론의 Little의 법칙을 단순화한 근사입니다).

```
 Age ≈ Visible ÷ 소비율(초당 처리 건수)

 예: Visible 600건, 소비자가 초당 2건 처리 → 맨 앞 메시지는 약 300초 기다린 상태
```

**모니터링 방법:**

- 🚨 **알람은 Age로 겁니다.** 사용자가 느끼는 것은 "몇 건 밀렸나"가 아니라 "얼마나 늦었나"이기 때문입니다.
- 🔍 **Visible은 원인 진단용입니다.** Age가 올랐을 때 아래 표로 원인을 가립니다.

| Age  | Visible     | 해석                        | 다음 행동                                  |
| ---- | ----------- | --------------------------- | ------------------------------------------ |
| ↑    | ↑           | 처리량 부족 (③)             | 소비자나 하위 서비스의 용량을 봅니다 (6.3) |
| ↑    | 거의 그대로 | 특정 메시지·그룹이 막힘 (②) | 해당 메시지의 처리 로그를 봅니다           |
| 낮음 | 순간 ↑      | 정상적인 폭주 (①)           | 조치하지 않습니다                          |

### 6.2 NotVisible과 GroupsWithInflight가 벌어질 때

**예시 상황:** NotVisible 3, GroupsWithInflight 1. 처리 중인 메시지 3건이 모두 한 그룹에 속해 있다는 뜻입니다.

#### SQS 규칙상으로는 정상적으로 생길 수 있는 상태입니다

FIFO 동작 문서 원문은 다음과 같습니다.

> "You may receive multiple messages from the same message group ID in one batch (up to 10 messages in a single call using the `MaxNumberOfMessages` parameter). However, you can't receive additional messages from the same message group ID in subsequent requests until: The currently received messages are deleted, or They become visible again"

즉 **한 번의 호출로는 같은 그룹 메시지를 여러 건 받을 수 있지만, 그 뒤 다음 호출부터는 그 그룹을 내주지 않습니다.** 문서는 또 SQS가 한 번의 호출에서 "같은 그룹의 메시지를 가능한 한 많이" 돌려주려 한다고도 적고 있습니다.

```
 그룹 A: [a1][a2][a3]      그룹 B: [b1]

 소비자 X ── Receive(Max=10) ──▶ a1, a2, a3 한꺼번에 받음   → NotVisible 3, Groups 1
 소비자 Y ── Receive          ──▶ 그룹 A는 내주지 않음 (처리 중이므로)
                                  b1을 받음                 → NotVisible 4, Groups 2
```

그러므로 NotVisible 3, Groups 1은 **"누군가 한 번의 호출로 한 그룹의 메시지 3건을 한꺼번에 받았다"**는 뜻입니다. 여러 소비자가 한 그룹을 동시에 나눠 받은 것이 아닙니다. 그것은 SQS가 막아 줍니다.

#### 소비 규칙을 `MaxNumberOfMessages=1`로 정한 시스템에서는 이상 신호입니다

엄격한 순서가 필요해서 모든 소비자가 `MaxNumberOfMessages=1`로 한 건씩만 받도록 설계했다면, 한 그룹에서 처리 중인 메시지는 최대 1건입니다. 따라서 **NotVisible과 Groups는 같아야 합니다.** 이 상태가 계속된다면 SQS 오류가 아니라 **"정한 소비 규칙을 지키지 않는 누군가가 큐를 읽고 있다"**는 신호입니다. 의심할 후보는 다음과 같습니다.

- 🖱️ **AWS 콘솔의 "메시지 폴링(Poll for messages)" 버튼:** 사람이 큐 내용을 확인하려고 누르면 실제로 메시지를 받아 가서 가시성 시간 동안 숨깁니다. 가장 흔한 원인입니다.
- 💻 사람이 CLI나 스크립트로 `receive-message`를 실행한 경우
- 📦 `MaxNumberOfMessages` 값이 다른 옛 버전 인스턴스나 다른 서비스가 같은 큐를 읽는 경우

#### 순간적으로 어긋나는 것은 무시합니다

- 두 값은 **근사값**이고, 같은 순간에 함께 찍힌다는 보장이 없습니다.
- NotVisible은 큐가 비어 있어도 드물게 0이 아닌 값을 잠깐 보고할 수 있습니다(4.3).

그래서 한 점만 어긋난 것은 신호로 보지 않고, **여러 데이터 포인트 동안 계속 NotVisible > Groups**일 때만 조사합니다. 반대로 Groups > NotVisible은 정의상 나올 수 없으므로, 보인다면 두 지표의 수집 시점이 어긋난 것입니다.

#### 이 상태가 왜 해로운가

"한 그룹을 한 소비자가 한 건씩 차례로 처리한다"는 규칙이 깨지면 다음 일이 생길 수 있습니다.

```
 소비자가 a1, a2, a3를 한꺼번에 받아 반복문으로 차례대로 처리
   a1 처리 → 일시 실패 → 삭제하지 않음 (재배달을 기다림)
   a2 처리 → 성공 → 삭제        ← 같은 그룹에서 나중 메시지가 먼저 처리됨
   a3 처리 → 성공 → 삭제
 가시성 시간이 지나 a1이 다시 옴  → 순서가 뒤집힘
```

게다가 a2, a3는 a1을 처리하는 동안에도 가시성 시간이 계속 흐릅니다. a1이 오래 걸리면 a2, a3는 처리되기도 전에 가시성 시간이 끝나 재배달될 수 있습니다. `MaxNumberOfMessages=1`은 이런 순서 역전을 애플리케이션 코드가 아니라 **큐의 규칙**으로 막는 설정입니다.

### 6.3 소비자를 늘려야 하는가

"`Approximate…` 값 중 NotVisible을 뺀 나머지가 계속 오르면 소비자를 늘려야 한다"는 판단은 **방향은 맞지만, 그대로 적용하면 틀리는 경우가 세 가지 있습니다.**

1. **Delayed는 빼야 합니다.** 이 값은 소비자와 무관하게 큐 설정이 만듭니다.
2. **GroupsWithInflight는 적체가 아니라 "바쁨"을 보여 줍니다.** 이 값은 소비자를 늘리면 오히려 올라갑니다. 판단 기준은 **Visible과 Age** 두 개입니다.
3. **소비자를 늘려도 풀리지 않거나 오히려 악화되는 경우가 있습니다.**

| 상황                              | 소비자를 늘리면? | 이유                                                                                                                                                                                                                           |
| --------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 적체가 여러 그룹에 퍼져 있음      | ✅ 효과 있음     | 병렬로 처리할 그룹이 많습니다                                                                                                                                                                                                  |
| 적체가 한두 그룹에 몰림 (6.1의 ②) | ❌ 효과 없음     | FIFO는 한 그룹을 한 번에 하나씩만 내줍니다                                                                                                                                                                                     |
| 하위 서비스가 병목                | ❌ 오히려 악화   | 소비자가 호출하는 API의 동시 처리 한도가 차면 거절(예: HTTP 503)이 늘어납니다. 소비자 수를 SDK의 HTTP 커넥션 풀 크기보다 크게 잡으면, 남는 소비자가 커넥션을 기다리다 요청 서명이 만료되거나 처리 시간 예산을 넘길 수 있습니다 |

**판단 순서:**

```
 Age ↑ ?
   └─ 예 ─▶ Visible도 같이 오르나?
              ├─ 아니요 ─▶ 특정 그룹 막힘 → 해당 메시지 조사 (소비자 증설 X)
              └─ 예 ─▶ GroupsWithInflight가 소비자 동시 처리 상한에 붙어 있나?
                         ├─ 아니요 ─▶ 소비자가 받으러 오지 않음 → 소비자 상태 점검 (6.4)
                         └─ 예 ─▶ 하위 서비스(호출 대상 API, DB)는 멀쩡한가?
                                    ├─ 아니요 ─▶ 하위 서비스 용량부터 해결
                                    └─ 예 ─▶ ✅ 소비자 증설
```

### 6.4 "EmptyReceives 0 + Received 0"의 의미

두 값이 모두 0이면 **아무도 `ReceiveMessage`를 부르지 않은 것**입니다. 다만 원인이 "소비자가 죽었다" 하나만은 아닙니다.

| 원인                                                 | 인스턴스(파드) 다운 알람에 잡히나?                                                                                                                                      |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 소비자 인스턴스가 죽음                               | ✅ 잡힙니다                                                                                                                                                             |
| 인스턴스는 살아 있지만 수신 루프가 멈춤 (hang, 교착) | ❌ 잡히지 않습니다                                                                                                                                                      |
| **모든 소비자가 처리 중이라 받으러 오지 않음**       | ❌ 잡히지 않습니다. 동시 처리 수가 상한에 닿으면 수신을 멈추는 역압(backpressure) 설계나, 한 건을 끝까지 처리한 뒤에야 다음 건을 받는 워커 구조에서 정상적으로 생깁니다 |

이 조합에 알람을 따로 걸면 인스턴스 다운 알람과 겹칩니다. 그래서 **Age 알람 하나로 묶는 편을 권합니다.** 세 경우 모두 결국 메시지가 기다리게 되므로 Age가 오르고, 인스턴스 다운 알람이 잡지 못하는 두 경우까지 잡힙니다. "EmptyReceives + Received = 0" 그래프는 Age 알람이 울렸을 때 원인을 가리는 **진단용**으로 둡니다.

단, 메시지가 하나도 없으면 Age 값 자체가 보고되지 않는다는 점(4.1)도 함께 기억해야 합니다. 트래픽이 원래 없는 시간대에 "EmptyReceives 0 + Received 0"이 나오면 그것은 소비자가 죽은 경우입니다. 이 경우는 인스턴스 다운 알람이나 프로세스 헬스체크가 맡아야 합니다.

---

## 7. 대시보드 예시 읽기

아래는 작은 FIFO 큐 하나를 약 12시간 동안 본 대시보드를 해석한 예시입니다.

| 관찰                                            | 해석                                                                                                                                                                                      |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SentMessageSize`가 3~3.14바이트로 일정함       | 본문이 짧은 ID 하나뿐인 큐로 추정됩니다(5.5)                                                                                                                                              |
| 중복 제거 지표와 GroupsWithInflight 지표가 있음 | FIFO 큐입니다                                                                                                                                                                             |
| Sent ≈ Received ≈ Deleted가 거의 같은 모양      | 재배달 없이 받은 만큼 삭제했습니다. 정상입니다                                                                                                                                            |
| Age, Visible, NotVisible이 모두 0               | 메시지가 쌓이기 전에 처리됐습니다                                                                                                                                                         |
| EmptyReceives가 1분에 약 3회                    | `WaitTimeSeconds=20`으로 폴링하는 소비자 하나가 살아 있다는 것과 맞는 수치입니다(5.3)                                                                                                     |
| 중복 제거가 한 번 1건 찍힘                      | 같은 주기 구간 안에서 같은 대상을 두 번 넣으려 했습니다. 스케줄러가 두 번 실행됐을 가능성이 있지만, 원인은 확인하지 않았습니다. 중복 제거 장치가 의도대로 동작한 것이므로 문제는 아닙니다 |
| Delayed가 0                                     | 지연 기능을 쓰지 않는 큐로서 정상입니다                                                                                                                                                   |

---

## 8. 대시보드·알람 구성 권장안

| 우선순위 | 지표                                                                                     | 통계              | 용도                                                         | 알람                                       |
| -------- | ---------------------------------------------------------------------------------------- | ----------------- | ------------------------------------------------------------ | ------------------------------------------ |
| 1        | `ApproximateAgeOfOldestMessage`                                                          | Maximum           | 지연 감지 (사용자 체감)                                      | ✅ 큐마다 허용 지연을 정해 임계값으로 사용 |
| 2        | `ApproximateNumberOfMessagesVisible`                                                     | Maximum           | 적체량, 원인 진단                                            | ✅ (보조)                                  |
| 3        | `NumberOfMessagesSent` / `Received` / `Deleted`                                          | Sum               | 한 그래프에 겹쳐 그림. Received − Deleted 격차 = 재배달 신호 | 선택                                       |
| 4        | `ApproximateNumberOfMessagesNotVisible`, `ApproximateNumberOfGroupsWithInflightMessages` | Maximum           | 포화 판단, 소비 규칙 위반 감지(6.2)                          | ❌ (여러 점 연속 조건으로만)               |
| 참고     | `NumberOfEmptyReceives`                                                                  | Sum               | 소비자 폴링 확인, 진단                                       | ❌                                         |
| 참고     | `NumberOfDeduplicatedSentMessages`                                                       | Sum               | 생산자 중복 전송 감지                                        | ❌                                         |
| 참고     | `ApproximateNumberOfMessagesDelayed`                                                     | Maximum           | 설정 변경 감지                                               | ❌                                         |
| 참고     | `SentMessageSize`                                                                        | Average / Maximum | 페이로드 추세                                                | ❌                                         |

**재배달이 정상 경로에 들어 있는 큐도 있습니다.** 예를 들어 일시 실패 시 "삭제하지 않고 재배달에 맡기는" 설계라면, 그 큐는 Received가 Deleted보다 큰 폭이 다른 큐보다 자주 보입니다. 큐마다 설계를 알고 기준선을 따로 잡아야 합니다.

**DLQ가 있다면** DLQ의 `ApproximateNumberOfMessagesVisible`에 "0보다 크면" 알람을 거는 것이 일반적입니다.

---

## 9. 실행 가능한 예제

### 9.1 Age 알람 (Terraform)

```hcl
variable "queue_name" {
  type = string
}

variable "alarm_topic_arn" {
  type = string
}

resource "aws_cloudwatch_metric_alarm" "sqs_oldest_message_age" {
  alarm_name          = "${var.queue_name}-oldest-message-age"
  alarm_description   = "가장 오래된 메시지가 5분 넘게 처리되지 않았다"
  namespace           = "AWS/SQS"
  metric_name         = "ApproximateAgeOfOldestMessage"
  dimensions          = { QueueName = var.queue_name }
  statistic           = "Maximum"
  period              = 60
  evaluation_periods  = 5   # 5분 연속으로 넘을 때만 울린다
  datapoints_to_alarm = 5
  threshold           = 300 # 초
  comparison_operator = "GreaterThanThreshold"
  # 메시지가 없으면 이 지표는 보고되지 않는다 → 데이터 없음은 정상으로 본다
  treat_missing_data  = "notBreaching"
  alarm_actions       = [var.alarm_topic_arn]
  ok_actions          = [var.alarm_topic_arn]
}

resource "aws_cloudwatch_metric_alarm" "sqs_backlog" {
  alarm_name          = "${var.queue_name}-backlog"
  namespace           = "AWS/SQS"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  dimensions          = { QueueName = var.queue_name }
  statistic           = "Maximum"
  period              = 60
  evaluation_periods  = 10
  datapoints_to_alarm = 10
  threshold           = 100
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [var.alarm_topic_arn]
}
```

### 9.2 지표 조회 (AWS CLI)

Sent, Received, Deleted를 한 번에 조회해 재배달 격차를 봅니다.

```bash
QUEUE=my-queue.fifo
START=$(date -u -v-3H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '-3 hours' +%Y-%m-%dT%H:%M:%SZ)
END=$(date -u +%Y-%m-%dT%H:%M:%SZ)

aws cloudwatch get-metric-data \
  --start-time "$START" --end-time "$END" \
  --metric-data-queries "[
    {\"Id\":\"sent\",\"MetricStat\":{\"Metric\":{\"Namespace\":\"AWS/SQS\",\"MetricName\":\"NumberOfMessagesSent\",\"Dimensions\":[{\"Name\":\"QueueName\",\"Value\":\"$QUEUE\"}]},\"Period\":300,\"Stat\":\"Sum\"}},
    {\"Id\":\"recv\",\"MetricStat\":{\"Metric\":{\"Namespace\":\"AWS/SQS\",\"MetricName\":\"NumberOfMessagesReceived\",\"Dimensions\":[{\"Name\":\"QueueName\",\"Value\":\"$QUEUE\"}]},\"Period\":300,\"Stat\":\"Sum\"}},
    {\"Id\":\"del\",\"MetricStat\":{\"Metric\":{\"Namespace\":\"AWS/SQS\",\"MetricName\":\"NumberOfMessagesDeleted\",\"Dimensions\":[{\"Name\":\"QueueName\",\"Value\":\"$QUEUE\"}]},\"Period\":300,\"Stat\":\"Sum\"}},
    {\"Id\":\"redelivery_gap\",\"Expression\":\"recv - del\",\"Label\":\"Received - Deleted\"}
  ]"
```

### 9.3 FIFO 생산자와 소비자 (Python, boto3)

주기 구간 번호로 중복 제거 ID를 만드는 생산자와, `MaxNumberOfMessages=1` + long polling으로 한 건씩 처리하는 소비자입니다.

```python
import time

import boto3

QUEUE_URL = "https://sqs.ap-northeast-2.amazonaws.com/123456789012/my-queue.fifo"
INTERVAL_SECONDS = 300

sqs = boto3.client("sqs")


def enqueue(target_id: int) -> None:
    """같은 주기 구간 안에서 같은 대상을 두 번 넣으면 두 번째는 SQS 가 버린다."""
    tick_no = int(time.time()) // INTERVAL_SECONDS
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=str(target_id),
        MessageGroupId=str(target_id),  # 대상별로 순서를 지킨다
        MessageDeduplicationId=f"{target_id}#{tick_no}",
    )


def process(body: str) -> None:
    print("processing", body)


def consume_forever() -> None:
    while True:
        resp = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=1,  # 한 그룹의 여러 건을 한꺼번에 받지 않는다 (6.2)
            WaitTimeSeconds=20,     # long polling: 비어 있으면 최대 20초 기다렸다가 빈 응답
            MessageSystemAttributeNames=["ApproximateReceiveCount"],
        )
        for msg in resp.get("Messages", []):
            try:
                process(msg["Body"])
            except Exception:
                # 삭제하지 않는다 → 가시성 시간이 지나면 재배달된다 (Received 는 늘고 Deleted 는 안 는다)
                continue
            sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=msg["ReceiptHandle"])


if __name__ == "__main__":
    enqueue(123)
    enqueue(123)  # NumberOfDeduplicatedSentMessages +1
    consume_forever()
```

---

## 10. 주의점

- **근사값입니다.** `Approximate…` 지표는 정확한 수치가 아니며, 두 지표가 같은 순간에 찍힌다는 보장도 없습니다. 알람은 여러 데이터 포인트 연속 조건으로 겁니다.
- **통계를 맞게 고릅니다.** 상태 지표는 `Maximum`, 사건 지표는 `Sum`을 씁니다(3절).
- **사건 지표는 고유 메시지 수가 아닙니다.** Received와 Deleted는 같은 메시지를 여러 번 셀 수 있습니다.
- **Visible만 보면 FIFO의 그룹 막힘을 놓칩니다.** 알람의 기준은 Age입니다(6.1).
- **메시지가 없으면 Age는 보고되지 않습니다.** 알람에서 데이터 없음을 정상으로 처리해야 합니다(`treat_missing_data = "notBreaching"`).
- **표준 큐의 Age는 반복 실패 메시지를 빼고 계산합니다.** 표준 큐에서는 poison pill이 Age로 드러나지 않을 수 있으므로 DLQ 설정과 DLQ 알람을 함께 둡니다.
- **콘솔의 "메시지 폴링" 버튼은 실제 소비입니다.** 운영 큐에서 누르면 메시지가 가시성 시간 동안 숨겨지고, 순서를 엄격히 지키는 FIFO 소비 규칙을 깰 수 있습니다(6.2).
- **소비자 증설이 항상 답은 아닙니다.** 그룹 쏠림과 하위 서비스 병목부터 확인합니다(6.3).
- **중복 제거는 성공 응답 뒤에 숨어 있습니다.** 생산자 로그에는 흔적이 없고 지표로만 보입니다(5.4).
- **CloudWatch SQS 지표에는 그룹별·소비자별 값이 없습니다.** 그 수준의 관측이 필요하면 소비자 애플리케이션이 직접 지표를 내보내야 합니다.

---

## 11. 정리

| 지표                                            | 한 줄 의미                                  | 핵심 용도                                         |
| ----------------------------------------------- | ------------------------------------------- | ------------------------------------------------- |
| `ApproximateAgeOfOldestMessage`                 | 가장 오래 기다린 메시지의 대기 시간         | **주 알람** (6.1)                                 |
| `ApproximateNumberOfMessagesVisible`            | 지금 대기 중인 메시지 수 (적체량)           | 원인 진단 (6.1)                                   |
| `ApproximateNumberOfMessagesNotVisible`         | 받아 갔지만 아직 삭제하지 않은 메시지 수    | 소비자 포화 판단 (4.3)                            |
| `ApproximateNumberOfMessagesDelayed`            | 지연 설정 때문에 숨겨진 메시지 수           | 설정 변경 감지 (4.4)                              |
| `ApproximateNumberOfGroupsWithInflightMessages` | 처리 중인 메시지가 있는 그룹 수 (FIFO)      | 동시 처리 그룹 수, 소비 규칙 위반 감지 (4.5, 6.2) |
| `NumberOfMessagesSent`                          | 생산자가 큐에 넣은 수                       | 유입량 (5.1)                                      |
| `NumberOfMessagesReceived`                      | 소비자가 받아 간 수 (재배달 포함)           | Sent와 비교해 재배달 감지 (5.1)                   |
| `NumberOfMessagesDeleted`                       | 처리 완료로 삭제된 수                       | Sent와 비교해 적체 감지 (5.2)                     |
| `NumberOfEmptyReceives`                         | 빈손으로 끝난 수신 호출 수                  | 소비자 폴링 확인 (5.3, 6.4)                       |
| `NumberOfDeduplicatedSentMessages`              | 5분 창 안의 같은 ID로 버려진 전송 수 (FIFO) | 생산자 중복 전송 감지 (5.4)                       |
| `SentMessageSize`                               | 전송된 메시지 크기                          | 페이로드 추세 (5.5)                               |

**기억할 세 가지:**

1. **알람은 Age로 걸고, 나머지 지표는 원인을 가리는 데 씁니다.**
2. **이름의 Sent와 Received는 큐가 아니라 생산자와 소비자의 행동입니다.** 둘의 격차가 재배달입니다.
3. **FIFO 큐는 그룹 단위로 생각합니다.** 막힘도, 병렬성도, 중복 제거도 그룹과 ID 단위로 동작합니다.

---

## Sources

- [Available CloudWatch metrics for Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-available-cloudwatch-metrics.html)
- [SendMessage API Reference](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_SendMessage.html)
- [Exactly-once processing in Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues-exactly-once-processing.html)
- [FIFO queue delivery logic in Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues-understanding-logic.html)
- [Amazon SQS delay queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-delay-queues.html)
- [Amazon SQS message timers](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-message-timers.html)
