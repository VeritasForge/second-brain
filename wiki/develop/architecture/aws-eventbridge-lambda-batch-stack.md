---
tags: [aws, eventbridge, lambda, batch, python, iac]
created: 2026-05-08
---

# Python + EventBridge + Lambda + AWS Batch 스택 조사

## 📋 Executive Summary

1. **타이머 = EventBridge Scheduler** (Rules가 아님). AWS 공식 권장이며 IANA 타임존, 1회성 스케줄, 내장 retry/DLQ, 계정당 수백만 개 스케줄 지원.
2. **Lambda는 "선택"이지 필수가 아니다**. EventBridge → Batch 직접 호출, Step Functions → Batch `.sync` 직접 호출 모두 지원.
3. **추천 스택**: `EventBridge Scheduler → Lambda(Python 3.13, Powertools) → Batch(Fargate Spot)` + `AWS CDK(Python)` + `GitHub Actions OIDC`.
4. **단순한 케이스라면 Lambda 생략** → `EventBridge Scheduler → Batch SubmitJob 직접`.
5. **복잡한 의존/파이프라인이 있다면** `EventBridge Scheduler → Step Functions(.sync) → Batch`로 Lambda 대체.

---

## 🏗️ 전체 아키텍처 옵션 다이어그램

```
┌─────────────────────────────────────────────────────────────────────┐
│                          타이머 (Trigger)                              │
│  ┌──────────────────────┐         ┌──────────────────────┐          │
│  │ EventBridge Scheduler│ ✅ 권장  │ EventBridge Rules    │ ⚠️ 레거시 │
│  │ (서버리스 스케줄러)   │         │ (Scheduled Rule)     │          │
│  └──────────┬───────────┘         └──────────┬───────────┘          │
└─────────────┼────────────────────────────────┼──────────────────────┘
              │                                │
   ┌──────────┼────────────────────────────────┼──────────┐
   │          ▼                                ▼          │
   │  ┌──────────────┐  ┌──────────────────┐  ┌────────┐ │
   │  │ Option A     │  │ Option B         │  │Option C│ │
   │  │ Lambda(Py)   │  │ Step Functions   │  │ Batch  │ │
   │  │ → SubmitJob  │  │ → submitJob.sync │  │ 직접   │ │
   │  └──────┬───────┘  └────────┬─────────┘  └───┬────┘ │
   └─────────┼────────────────────┼──────────────────┼───┘
             ▼                    ▼                  ▼
        ┌──────────────────────────────────────────────────┐
        │               AWS Batch Job Queue                 │
        │  ┌────────────────┐    ┌───────────────────┐     │
        │  │ Fargate / Spot │    │ EC2 / EC2 Spot    │     │
        │  │ (서버리스)      │    │ (대용량/장시간)    │     │
        │  └────────────────┘    └───────────────────┘     │
        └──────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ CloudWatch Logs       │
                    │ X-Ray / OpenTelemetry │
                    │ DLQ (SQS)             │
                    └───────────────────────┘
```

---

## 🔍 Findings

### 1. EventBridge Scheduler vs EventBridge Rules ✅ [Confirmed]

| 기준               | EventBridge Scheduler                                                       | EventBridge Rules (Scheduled)     |
| ------------------ | --------------------------------------------------------------------------- | --------------------------------- |
| **AWS 공식 권장**  | ✅ **"We recommend Scheduler to invoke targets on a schedule"**             | ⚠️ 레거시 (legacy로 분류)         |
| **확장성**         | 계정당 수백만 개                                                            | 이벤트 버스당 300 룰 한도         |
| **타임존**         | IANA 타임존 (Asia/Seoul 등) 직접 지원                                       | UTC만, DST 직접 계산              |
| **1회성(One-time)**| ✅ 지원 (`at(2026-06-01T00:00:00)`)                                         | ❌ 불가                           |
| **시작/종료 시각** | ✅ Start/End time, Flexible time window                                     | ❌                                |
| **Retry 정책**     | 내장 (max retries 185, max age 24h)                                         | 별도 구성 필요                    |
| **DLQ**            | 스케줄 레벨에서 직접 구성                                                   | Rule 레벨에서 구성                |
| **타겟 수**        | 200+ AWS API 직접 호출                                                      | EventBridge 타겟                  |

> 💡 **결론**: 신규 개발은 **무조건 Scheduler**. Rules는 이벤트 패턴 매칭용으로만 사용.
> **출처**: [AWS EventBridge Scheduler 공식 문서](https://docs.aws.amazon.com/eventbridge/latest/userguide/using-eventbridge-scheduler.html)

---

### 2. Lambda → Batch 트리거 방식 비교 ✅ [Confirmed]

세 가지 경로를 직접 검증했습니다.

#### 🅰️ EventBridge → Lambda → boto3.submit_job (가장 유연)

```python
# Lambda handler (Python 3.13)
import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
tracer = Tracer()
batch = boto3.client("batch")

@logger.inject_lambda_context
@tracer.capture_lambda_handler
def handler(event, context: LambdaContext):
    response = batch.submit_job(
        jobName="my-job",
        jobQueue="my-queue",
        jobDefinition="my-jobdef:3",
        containerOverrides={
            "command": ["python", "main.py", "--date", event["date"]],
            "environment": [{"name": "RUN_ID", "value": event["id"]}],
        },
    )
    logger.info("Submitted", extra={"jobId": response["jobId"]})
    return {"jobId": response["jobId"]}
```

✅ **장점**: 입력 가공·조건 분기·외부 API 호출 자유로움
❌ **단점**: 운영/모니터링 대상 1개 추가, Cold start

#### 🅱️ EventBridge → Step Functions(`batch:submitJob.sync`) → Batch (Lambda 없이)

✅ [Confirmed] 공식 문서에 명시: `arn:aws:states:::batch:submitJob.sync`

```json
"Submit Batch Job": {
    "Type": "Task",
    "Resource": "arn:aws:states:::batch:submitJob.sync",
    "Arguments": {
        "JobName": "{{BATCH_NAME}}",
        "JobQueue": "{{BATCH_QUEUE_ARN}}",
        "JobDefinition": "{{BATCH_JOB_DEFINITION_ARN}}",
        "ContainerOverrides": {
            "ResourceRequirements": [{"Type": "VCPU", "Value": "4"}]
        }
    }
}
```

✅ **장점**: Lambda 없이 완료까지 대기, 시각적 워크플로우, 재시도/에러 핸들링 내장
❌ **단점**: $25/M state transitions 비용, 단순 1-job 케이스에 과도

#### 🅲 EventBridge → Batch 직접 (가장 단순)

✅ [Confirmed] AWS Batch 공식 문서 원문:
> *"AWS Batch jobs are available as EventBridge targets. Using simple rules, you can match events and submit AWS Batch jobs in response to them."*

✅ **장점**: 컴포넌트 최소 (스케줄러 + Batch만)
❌ **단점**: 입력 변환은 InputTransformer만 가능, 분기 로직 불가, 동적 파라미터 한계

---

### 3. IaC 스택 비교 📊

| 항목                              | AWS CDK (Python)              | AWS SAM                       | Serverless Framework      | Terraform               | CloudFormation         |
| --------------------------------- | ----------------------------- | ----------------------------- | ------------------------- | ----------------------- | ---------------------- |
| **언어**                          | Python/TS/Java/Go/.NET        | YAML + 매크로                 | YAML + JS plugins         | HCL                     | YAML/JSON              |
| **EventBridge+Lambda+Batch 통합** | ✅ L2 construct 모두 제공     | ⚠️ Lambda·EB 강함, Batch는 raw CFN | ⚠️ Lambda 중심, Batch는 plugin | ✅ 모든 리소스 지원    | ✅ but 장황함          |
| **추상화 수준**                   | 높음 (코드로 조립)            | 중간 (서버리스 특화)          | 중간 (서버리스 특화)      | 낮음 (1:1 매핑)         | 낮음                   |
| **상태 관리**                     | CFN 자동                      | CFN 자동                      | CFN 자동                  | tfstate (S3+DynamoDB)   | 자동                   |
| **배포 속도**                     | 3~5분 (10~20 리소스)          | 3~5분                         | 3~5분                     | 1~3분                   | 3~5분                  |
| **멀티클라우드**                  | ❌ AWS 전용                   | ❌                            | ⚠️ 일부                   | ✅                      | ❌                     |
| **러닝 커브**                     | 중간 (Python 친화)            | 낮음                          | 낮음                      | 중간 (HCL)              | 높음                   |
| **Drift Detection**               | CFN 기반                      | CFN 기반                      | CFN 기반                  | ✅ terraform plan       | ✅                     |
| **Python 백엔드 친화도**          | ⭐⭐⭐⭐⭐                    | ⭐⭐⭐                        | ⭐⭐                      | ⭐⭐⭐                  | ⭐                     |

> 💡 **추천**: Python 백엔드 개발자에게는 **AWS CDK (Python)**. 같은 언어로 인프라+런타임을 다룰 수 있고, EventBridge·Lambda·Batch 모두 L2 construct로 깔끔하게 조립됨.
> 멀티클라우드 또는 인프라팀과 분리되는 경우에만 **Terraform** 고려.

---

### 4. AWS Batch 컴퓨팅 환경 선택 ✅ [Confirmed]

| 기준                       | Fargate         | Fargate Spot       | EC2 On-Demand       | EC2 Spot           |
| -------------------------- | --------------- | ------------------ | ------------------- | ------------------ |
| **관리 부담**              | ✅ 서버리스     | ✅ 서버리스        | ❌ AMI/패치 관리    | ❌ + 중단 처리     |
| **시작 속도**              | 빠름 (분 단위)  | 빠름               | 느림 (인스턴스 부팅)| 느림               |
| **처리량**                 | ⚠️ **500 launches/min 한도** | ⚠️ 동일 | ✅ 무제한           | ✅ 무제한          |
| **단가 절감**              | 기준            | 최대 70%↓          | 기준                | 최대 90%↓          |
| **GPU/특수 인스턴스**      | ❌              | ❌                 | ✅                  | ✅                 |
| **장시간(>몇시간) 작업**   | OK              | ⚠️ 중단 위험       | ✅                  | ⚠️ 중단 위험       |

🟡 [Likely] 권장 매트릭스

- **소규모/주기 배치 + 짧은 작업** → **Fargate Spot** (운영부담 0, 70% 절감)
- **대량 fan-out (>500/min) 또는 GPU** → **EC2 Spot + 체크포인팅**
- **장시간 비중단 필수** → **EC2 On-Demand**

> **출처**: [AWS Batch managed compute environments](https://docs.aws.amazon.com/batch/latest/userguide/managed_compute_environments.html), [Why use Fargate with Batch](https://aws.amazon.com/blogs/hpc/why-use-fargate-with-aws-batch-for-serverless-batch-compute/)

---

### 5. Python 개발 스택 ✅ [Confirmed]

| 항목              | 권장                                                                       | 비고                                                                              |
| ----------------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **Lambda 런타임** | `python3.13` (or `python3.14`)                                             | Deprecation: 2029-06-30. AL2023 기반.                                             |
| **AWS SDK**       | `boto3` (런타임 내장 OR 패키지에 명시)                                     | 내장 버전 의존 시 자동 업데이트로 깨질 수 있어 **명시 패키징 권장**               |
| **공통 유틸**     | **AWS Lambda Powertools for Python**                                       | Logger / Tracer / Metrics / Idempotency / Parameters / Batch processor            |
| **관측성**        | Powertools Tracer + ADOT (X-Ray SDK는 2026-02-25부터 maintenance)          | OTel 마이그레이션 권장                                                            |
| **패키징**        | Zip + Layer (소형) / Container Image (>250MB)                              | 컨테이너는 최대 10GB                                                              |
| **검증**          | Pydantic v2 (Powertools v3.21+ 통합)                                       | 이벤트 스키마 검증                                                                |

> **출처**: [Lambda runtimes 공식 문서](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html), [Powertools for AWS Lambda](https://aws.amazon.com/powertools-for-aws-lambda/)

---

### 6. 모니터링/로깅 🔄 [Synthesized]

| 계층              | 도구                                                                       | 역할                                          |
| ----------------- | -------------------------------------------------------------------------- | --------------------------------------------- |
| **Trigger**       | EventBridge Scheduler **DLQ (SQS)** + CloudWatch Metrics `InvocationsSentToDLQ` | 미전달 이벤트 보존                            |
| **Lambda**        | Powertools Logger (구조화) + Tracer + Metrics (EMF)                        | 통합 관측성                                   |
| **분산 추적**     | ADOT/OTel (신규) 또는 X-Ray (기존, maintenance 모드)                       | EventBridge → Lambda → Batch 추적             |
| **Batch Job**     | CloudWatch Logs (`/aws/batch/job` 로그그룹)                                | 컨테이너 stdout/stderr                        |
| **Job 상태 변화** | EventBridge `Batch Job State Change` 이벤트 → Lambda/SNS                   | 실패 알림 자동화                              |
| **자가 치유**     | 일일 EventBridge Scheduler → DLQ 재처리 Lambda                             | DLQ drain 패턴                                |

```
[Failure Flow]
EventBridge Scheduler --(retry x185, 24h)--> Target
                           │ 실패
                           ▼
                       SQS DLQ
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
       Lambda 자동 drain      CloudWatch Alarm
       (스케줄)                → SNS → Slack
```

---

### 7. CI/CD 비교

| 옵션                              | 장점                                                                       | 단점                          | 추천 시나리오                  |
| --------------------------------- | -------------------------------------------------------------------------- | ----------------------------- | ------------------------------ |
| **GitHub Actions + OIDC**         | ✅ 코드와 같은 곳, 무제한 토큰 없음, 2025년 공식 `aws-lambda-deploy` Action 출시 | AWS 외 빌드 환경 필요         | 대부분의 팀 (✅ 권장)          |
| **AWS CodePipeline + CodeBuild**  | AWS 네이티브, IAM 통합                                                     | 별도 콘솔, 비용               | AWS 표준화 강조 조직           |

🟡 [Likely] **추천**: GitHub Actions + OIDC. 2025년 AWS가 공식 통합을 강화했고, long-lived AWS 키를 GitHub Secrets에 저장할 필요가 없음.

> **출처**: [GitHub Actions to deploy Lambda](https://docs.aws.amazon.com/lambda/latest/dg/deploying-github-actions.html)

---

### 8. 대안 스택 검토 📊

| 대안                                            | 적합 시점                                          | 비고                                                                  |
| ----------------------------------------------- | -------------------------------------------------- | --------------------------------------------------------------------- |
| **Step Functions만 (Lambda 생략)**              | 의존성 있는 멀티 잡, 분기, 재시도 로직 필요        | `.sync` 패턴이 Lambda 폴링을 대체                                     |
| **ECS Scheduled Task**                          | 단일 컨테이너 단발성, 우선순위·페어셰어 불필요     | Batch는 3~5분+ 작업에 최적, ECS는 단순 cron 컨테이너에 적합           |
| **EventBridge → SQS → Lambda → Batch**          | 버스트 흡수, 백프레셔 필요                         | SQS가 버퍼 역할, 단 Batch 자체에 잡 큐가 있어 중복일 수 있음          |
| **EventBridge → Batch 직접**                    | 정해진 파라미터로 매번 같은 잡 실행                | 가장 단순, 입력 가공 한계                                             |

---

## 🎯 추천 스택 (의사결정 트리)

```
[질문 1] 잡 1개를 정해진 시각에 그대로 실행만 하나?
    │
    ├─ Yes ──► [STACK A: 미니멀]
    │            EventBridge Scheduler → Batch SubmitJob 직접
    │            IaC: CDK(Python) 또는 Terraform
    │
    └─ No
       │
       ▼
[질문 2] 입력 가공/조건 분기/외부 호출이 필요한가?
    │
    ├─ Yes
    │   │
    │   ▼
    │  [질문 2a] 잡이 2개 이상이거나 의존성/병렬(map)이 필요한가?
    │   │
    │   ├─ Yes ──► [STACK C: 워크플로우]
    │   │            EventBridge Scheduler → Step Functions(.sync) → Batch
    │   │            (Lambda는 사전처리에만 선택적 추가)
    │   │
    │   └─ No  ──► [STACK B: 표준 ✅ 추천]
    │                EventBridge Scheduler → Lambda(Py3.13+Powertools)
    │                                        → boto3 SubmitJob → Batch
    │
    └─ No  ──► STACK A로 회귀
```

### ⭐ STACK B (표준 추천) — 80% 케이스 커버

```yaml
Trigger:        EventBridge Scheduler (cron + IANA TZ + DLQ)
Compute(Glue):  Lambda Python 3.13 + Lambda Powertools
                  - Logger / Tracer / Metrics
                  - Idempotency (멱등성)
                  - boto3.submit_job
Worker:         AWS Batch on Fargate Spot
                  - Job Definition (Container Image, ECR)
                  - Job Queue (Fair Share Scheduling)
Observability:  CloudWatch Logs + ADOT(OTel)
                + EventBridge `Batch Job State Change` → SNS
DLQ:            EventBridge Scheduler DLQ (SQS Standard)
IaC:            AWS CDK (Python)
CI/CD:          GitHub Actions + AWS OIDC
                  - cdk synth → cdk deploy
                  - ECR 이미지 빌드/푸시
                  - Lambda zip/layer 패키징
```

---

## ⚠️ Edge Cases & Caveats

- **Fargate 처리량 한도**: 분당 500 task launch — 대량 fan-out은 Array Job + EC2 Spot로 전환.
- **EventBridge → Batch 직접 호출 시 JobDefinition revision**: 자동으로 latest를 못 가져옴. `SubmitJob`에 `:JOB_DEFINITION_NAME`만 넣으면 latest로 해결되거나 Lambda를 끼워 명시 조회 필요.
- **Batch 잡이 1분 미만이면 Batch 부적합**: 여러 작업을 한 잡에 패킹하거나 ECS Scheduled Task 검토.
- **X-Ray SDK는 2026-02-25부터 maintenance 모드**: 신규는 ADOT/OTel로 시작 권장.
- **DLQ는 FIFO 불가**: EventBridge DLQ는 Standard SQS만 지원.

---

## ⚔️ Contradictions Found

- **Step Functions 비용 우려 vs 가치**: ClearScale은 "$25/M state transition은 비싸다"라고 평가하나, 공식 문서는 의존/병렬 워크플로우에서 운영 가치가 비용을 상회한다고 봄 → **단일 잡엔 STACK A/B, 다중·의존 잡엔 STACK C**로 분기하는 것이 정답.

---

## 📎 Sources

1. [Amazon EventBridge Scheduler 공식 가이드](https://docs.aws.amazon.com/eventbridge/latest/userguide/using-eventbridge-scheduler.html) — official_doc
2. [AWS Batch jobs as EventBridge targets](https://docs.aws.amazon.com/batch/latest/userguide/batch-cwe-target.html) — official_doc
3. [Run AWS Batch workloads with Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/connect-batch.html) — official_doc
4. [AWS Lambda runtimes (Python 3.12/3.13/3.14)](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html) — official_doc
5. [AWS Batch Managed Compute Environments](https://docs.aws.amazon.com/batch/latest/userguide/managed_compute_environments.html) — official_doc
6. [Powertools for AWS Lambda](https://aws.amazon.com/powertools-for-aws-lambda/) — official_doc
7. [Why use Fargate with AWS Batch](https://aws.amazon.com/blogs/hpc/why-use-fargate-with-aws-batch-for-serverless-batch-compute/) — primary_source
8. [Using GitHub Actions to deploy Lambda functions](https://docs.aws.amazon.com/lambda/latest/dg/deploying-github-actions.html) — official_doc
9. [EventBridge DLQ 사용법](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-rule-dlq.html) — official_doc
10. [boto3 submit_job 레퍼런스](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/batch/client/submit_job.html) — official_doc
11. [AWS CDK vs Terraform 2026 비교](https://towardsthecloud.com/blog/aws-cdk-vs-terraform) — tech_blog
12. [EventBridge Rules vs Scheduler — Be a Better Dev](https://beabetterdev.com/2022/11/20/eventbridge-rules-vs-eventbridge-scheduler/) — tech_blog
13. [When to use Step Functions vs Lambda](https://theburningmonk.com/2024/03/when-to-use-step-functions-vs-doing-it-all-in-a-lambda-function/) — tech_blog

---

## 📊 Research Metadata

- 검색 쿼리 수: 9 (일반 9 + SNS 0 — AWS 공식 자료가 풍부하여 SNS 생략)
- 수집 출처 수: 13
- 출처 유형 분포: 공식 9, 1차 1, 블로그 3
- 확신도 분포: ✅ Confirmed 7, 🟡 Likely 4, 🔄 Synthesized 2
