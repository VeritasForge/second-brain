---
tags: [architecture, aws, sns, sqs, eda, dlq]
created: 2026-04-14
---

# 🎯 AWS SNS vs SQS DLQ 비교 — EDA 기반 MSA 메시지 전달 보장

> 💡 **핵심**: SNS도 DLQ를 지원하지만, 그 DLQ는 결국 **SQS 큐**이고, **"전달" 실패만** 잡아준다. **"처리" 실패**까지 잡으려면 SQS를 중간에 두고 SQS의 DLQ를 활용하는 게 실무 정석 패턴.

---

## 🏠 현실 비유로 이해하기

우체국(SNS)과 우편함(SQS)을 비유로 생각해보자:

```
🏠 SNS = 우체국 집배원 (직접 문 앞까지 배달)
📬 SQS = 우편함 (넣어두면 나중에 꺼내감)

📮 SNS DLQ = "집배원이 3번 배달 시도했는데 아무도 없어서, 
              반송 보관함에 넣어둠"

📮 SQS DLQ = "우편함에서 편지를 꺼내서 3번 읽었는데 
              매번 처리 실패해서, 별도 보관함으로 이동"
```

---

## 📊 SNS DLQ vs SQS DLQ 핵심 차이

| 비교 기준               | SNS DLQ                                     | SQS DLQ                               |
| ----------------------- | ------------------------------------------- | -------------------------------------- |
| 📍 **부착 위치**        | SNS **구독(Subscription)** 레벨             | SQS **소스 큐** 레벨                   |
| ⚡ **트리거**           | **전달 실패** (서버 에러, 엔드포인트 삭제 등) | **처리 실패** (maxReceiveCount 초과)   |
| 🔄 **Redrive (재처리)** | ❌ 불가 — 수동으로 꺼내야 함                 | ✅ 가능 — 원래 큐로 자동 복귀          |
| 📦 **DLQ 대상**         | 반드시 **SQS 큐**                           | 반드시 **SQS 큐**                      |
| 🕐 **버퍼링**           | ❌ 없음 (push 방식)                         | ✅ 최대 14일 보관                      |

> 💡 **핵심**: SNS DLQ도 결국 **SQS 큐**에 저장한다. SNS 자체에는 메시지를 보관하는 저장소가 없다!

---

## 🔄 세 가지 패턴 비교

### 패턴 1: SNS → Lambda (SNS만 사용)

```
┌───────┐    push     ┌──────────┐
│  SNS  │ ──────────► │  Lambda  │
│ Topic │             │ Function │
└───┬───┘             └────┬─────┘
    │                      │
    │ 전달 실패 시           │ (Lambda 처리 실패는
    │ (endpoint 에러)       │  별도 Lambda DLQ 필요)
    ▼                      │
┌────────┐                 │
│SNS DLQ │ ◄───────────────┘ ← ❌ 여기로 안 감!
│(SQS큐) │
└────────┘
```

⚠️ **주의**: Lambda가 호출은 됐는데 **내부에서 에러**가 나면? → SNS 입장에선 "전달 성공"이라 **SNS DLQ에 안 들어감!**

### 패턴 2: SNS → SQS → Lambda (SQS 버퍼 사용)

```
┌───────┐   push   ┌───────┐   poll    ┌──────────┐
│  SNS  │ ───────► │  SQS  │ ◄──────── │  Lambda  │
│ Topic │          │ Queue │           │ Function │
└───┬───┘          └───┬───┘           └──────────┘
    │                  │
    │ 전달 실패 시      │ 처리 실패 시
    ▼                  ▼
┌────────┐        ┌────────┐
│SNS DLQ │        │SQS DLQ │ ← 🔄 Redrive 가능!
│(SQS큐) │        │(SQS큐) │
└────────┘        └────────┘
```

✅ **이중 안전망**: SNS 전달 실패 → SNS DLQ / Lambda 처리 실패 → SQS DLQ

### 패턴 3: Fan-out (SNS → 여러 SQS)

```
                    ┌───────┐     ┌──────────┐
              ┌───► │ SQS A │ ──► │ Lambda A │
              │     └───┬───┘     └──────────┘
┌───────┐     │         │
│  SNS  │ ────┤     ┌───────┐     ┌──────────┐
│ Topic │     ├───► │ SQS B │ ──► │ Lambda B │
└───────┘     │     └───┬───┘     └──────────┘
              │         │
              │     ┌───────┐     ┌──────────┐
              └───► │ SQS C │ ──► │ Lambda C │
                    └───┬───┘     └──────────┘
                        │
                    각 SQS마다 독립 DLQ
```

---

## ⚠️ SNS만 쓸 때의 함정

| #   | 함정                                 | 왜 위험한가                                          | 해결책                                          |
| --- | ------------------------------------ | ---------------------------------------------------- | ----------------------------------------------- |
| 1   | **Lambda 내부 에러 ≠ 전달 실패**     | Lambda가 호출은 됐으므로 SNS는 "성공"으로 간주       | SNS+SQS 조합 또는 Lambda Destination 설정       |
| 2   | **메시지 버퍼링 없음**               | SNS는 저장소가 없어 재시도 기간 끝나면 소실          | SQS를 중간에 배치 (최대 14일 보관)              |
| 3   | **Redrive 불가**                     | SNS DLQ에서 원래 구독자로 자동 재전송 불가           | SQS DLQ의 Redrive 기능 활용                     |
| 4   | **Consumer 속도 조절 불가**          | SNS는 push 방식이라 소비자가 속도 제어 못함          | SQS의 배치 크기/동시성으로 제어                 |

---

## 🔑 SNS 재시도 정책 (Retry Policy)

```
         구독 타입별 재시도 횟수
──────────────────────────────────────────
Lambda, SQS (AWS 관리형)
   → 100,015회 / 최대 23일 ← 매우 공격적!

HTTP/S
   → 기본 50회 / 최대 1시간
   → 4단계: 즉시 → Pre-backoff → Backoff → Post-backoff

SMS, Email
   → 50회 / ~6시간
──────────────────────────────────────────

⚠️ 클라이언트 에러 (4xx, Lambda 삭제 등)
   → 재시도 없이 즉시 DLQ로!
```

---

## 🤔 결론: 언제 뭘 써야 할까?

```
질문: "이벤트 유실이 허용되나?"

    YES → SNS만으로 충분 (알림, 로깅 등)
     │
    NO → SNS + SQS 조합 사용
          │
          ├── 처리 순서 보장 필요? → FIFO Topic + FIFO Queue
          │
          └── 처리 실패 시 자동 재처리? → SQS DLQ + Redrive Policy
```

| 시나리오                         | 추천 패턴                           |
| -------------------------------- | ----------------------------------- |
| 🔔 단순 알림 (이메일, 슬랙)     | SNS만                               |
| 📊 로그/메트릭 수집              | SNS → Lambda (유실 허용)            |
| 💰 결제/주문 처리                | SNS → SQS → Lambda (이중 DLQ)      |
| 🔀 Fan-out + 각 처리 보장       | SNS → 여러 SQS → 각 Lambda         |

---

## 📎 Sources

1. [Amazon SNS dead-letter queues](https://docs.aws.amazon.com/sns/latest/dg/sns-dead-letter-queues.html) — AWS 공식 문서
2. [Amazon SNS message delivery retries](https://docs.aws.amazon.com/sns/latest/dg/sns-message-delivery-retries.html) — AWS 공식 문서
3. [Designing durable serverless apps with DLQs](https://aws.amazon.com/blogs/compute/designing-durable-serverless-apps-with-dlqs-for-amazon-sns-amazon-sqs-aws-lambda/) — AWS 블로그
4. [Amazon SNS Adds Support for DLQ (Nov 2019)](https://aws.amazon.com/about-aws/whats-new/2019/11/amazon-sns-adds-support-for-dead-letter-queues-dlq/) — AWS 발표
5. [Using dead-letter queues in Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html) — AWS 공식 문서
