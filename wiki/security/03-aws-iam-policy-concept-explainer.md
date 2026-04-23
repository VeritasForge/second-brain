---
tags: [security, aws, iam, iam-policy, concept-explainer]
created: 2026-04-22
---

# 📖 AWS IAM Policy — Concept Deep Dive

> 💡 **한줄 요약**: IAM Policy는 **"누가(Principal), 어떤 리소스(Resource)에, 어떤 작업(Action)을, 어떤 조건(Condition)에서 할 수 있는지"**를 JSON으로 정의하는 **AWS 권한의 핵심 문서**이다.

---

## 1️⃣ 무엇인가? (What is it?)

**IAM Policy**는 AWS에서 권한(Permission)을 정의하는 **JSON 형식의 문서**이다. User, Group, Role 등의 IAM 엔터티에 연결하거나, S3 버킷 같은 리소스에 직접 붙여서 **"이 요청을 허용(Allow)할 것인가, 거부(Deny)할 것인가"**를 결정한다.

**현실 세계 비유 (12살도 이해할 수 있는 설명):**

놀이공원의 **이용 규칙표**를 생각하자. "키 120cm 이상(Condition)인 사람(Principal)만, 롤러코스터(Resource)를 탈 수 있다(Action: Allow)." 이 규칙표가 곧 Policy이다. 규칙표 없으면 아무것도 못 탄다(기본 거부). 규칙표 하나를 여러 놀이기구에 붙일 수도 있고(Managed Policy), 특정 놀이기구 전용 규칙을 만들 수도 있다(Inline Policy).

- **탄생 배경**: AWS 리소스가 수백 가지로 늘어나면서, "누가 무엇을 할 수 있는지"를 체계적으로 정의할 표준 형식이 필요해졌다. JSON 기반의 선언적 정책 언어가 그 답이다.
- **해결하는 문제**: 권한의 명시적 정의, 최소 권한 원칙 구현, 멀티 계정/서비스 환경에서의 일관된 접근 제어

> 📌 **핵심 키워드**: `Policy Document`, `Statement`, `Effect`, `Action`, `Resource`, `Condition`, `ARN`, `Least Privilege`

---

## 2️⃣ 핵심 개념 (Core Concepts)

IAM Policy의 핵심은 **JSON 문서의 6대 요소**와 **7가지 정책 유형**이다.

```
┌─────────────────────────────────────────────────────────────┐
│                  📋 IAM Policy JSON 구조                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  {                                                          │
│    "Version": "2012-10-17",        ← 정책 언어 버전         │
│    "Statement": [                  ← 권한 규칙 컨테이너     │
│      {                                                      │
│        "Sid": "AllowS3Read",       ← 규칙 식별자 (선택)     │
│        "Effect": "Allow",          ← 허용 or 거부 (필수)    │
│        "Action": "s3:GetObject",   ← 어떤 작업? (필수)      │
│        "Resource": "arn:aws:s3:::  ← 어떤 리소스? (필수)    │
│            my-bucket/*",                                    │
│        "Condition": {              ← 어떤 조건에서? (선택)   │
│          "IpAddress": {                                     │
│            "aws:SourceIp":                                  │
│              "192.168.1.0/24"                               │
│          }                                                  │
│        }                                                    │
│      }                                                      │
│    ]                                                        │
│  }                                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

| 요소 | 필수 여부 | 역할 | 예시 |
|------|----------|------|------|
| **Version** | 권장 | 정책 언어 버전 | `"2012-10-17"` (항상 이 값 사용) |
| **Statement** | ✅ 필수 | 권한 규칙 배열 | 하나 이상의 규칙 포함 |
| **Effect** | ✅ 필수 | 허용/거부 결정 | `"Allow"` 또는 `"Deny"` |
| **Action** | ✅ 필수 | AWS 서비스 작업 | `"s3:GetObject"`, `"ec2:StartInstances"` |
| **Resource** | 조건부 | 대상 리소스 ARN | `"arn:aws:s3:::my-bucket/*"` |
| **Condition** | 선택 | 추가 조건 | IP 범위, MFA 여부, 시간대 등 |
| **Principal** | 조건부 | 대상 주체 | 리소스 기반 정책에서만 사용 |

### 📂 7가지 정책 유형

| # | 정책 유형 | 부착 대상 | 역할 | Managed/Inline |
|---|----------|----------|------|----------------|
| 1 | **Identity-based** | User, Group, Role | 주체에게 권한 부여 | 둘 다 가능 |
| 2 | **Resource-based** | S3, SQS, KMS 등 리소스 | 리소스에 직접 접근 제어 | Inline만 |
| 3 | **Permissions Boundary** | User, Role | 최대 권한 상한선 설정 | Managed만 |
| 4 | **SCP (Service Control Policy)** | Organization/OU | 조직 내 계정 최대 권한 제한 | N/A |
| 5 | **RCP (Resource Control Policy)** | Organization 리소스 | 리소스 최대 권한 제한 | N/A |
| 6 | **ACL (Access Control List)** | S3, VPC, WAF | 다른 계정 접근 제어 (비-JSON) | N/A |
| 7 | **Session Policy** | 임시 세션 | AssumeRole 시 추가 제한 | N/A |

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

IAM Policy 평가의 핵심은 **"명시적 Deny > 명시적 Allow > 암묵적 Deny"** 우선순위이다.

```
┌─────────────────────────────────────────────────────────────────┐
│                  IAM Policy 평가 흐름 (Evaluation Logic)          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  👤 요청: "s3:GetObject on my-bucket/file.txt"                   │
│    │                                                            │
│    ▼                                                            │
│  ┌──────────────────────────────┐                               │
│  │ ① 명시적 Deny 있는가?         │                               │
│  │   (모든 정책에서 Deny 검색)    │                               │
│  └──────────┬───────────────────┘                               │
│        ┌────┴────┐                                              │
│        │ Yes     │ No                                           │
│        ▼         ▼                                              │
│   ❌ 거부    ┌──────────────────────────────┐                   │
│   (최종)    │ ② SCP/RCP 허용하는가?          │                   │
│             │   (Organizations 정책 체크)    │                   │
│             └──────────┬───────────────────┘                   │
│                   ┌────┴────┐                                   │
│                   │ No      │ Yes                               │
│                   ▼         ▼                                   │
│              ❌ 거부   ┌──────────────────────────────┐         │
│              (암묵적)  │ ③ Identity/Resource Policy    │         │
│                       │   명시적 Allow 있는가?         │         │
│                       └──────────┬───────────────────┘         │
│                             ┌────┴────┐                         │
│                             │ No      │ Yes                     │
│                             ▼         ▼                         │
│                        ❌ 거부   ┌────────────────────┐         │
│                        (암묵적)  │ ④ Permissions      │         │
│                                 │   Boundary 허용?    │         │
│                                 └────────┬───────────┘         │
│                                     ┌────┴────┐                │
│                                     │ No      │ Yes            │
│                                     ▼         ▼                │
│                                ❌ 거부    ✅ 허용               │
│                                (암묵적)   (최종)                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (Step by Step)

1. **Step 1 — 기본 거부**: 모든 요청은 기본적으로 **거부(Implicit Deny)**된다
2. **Step 2 — 명시적 Deny 체크**: 적용되는 모든 정책에서 `"Effect": "Deny"`를 먼저 검색. 하나라도 있으면 **즉시 거부** (다른 Allow 무시)
3. **Step 3 — SCP/RCP 체크**: Organizations에 속한 계정이면 SCP/RCP가 허용하는 범위 내인지 확인
4. **Step 4 — Allow 검색**: Identity-based Policy와 Resource-based Policy에서 `"Effect": "Allow"` 검색
5. **Step 5 — Permissions Boundary 체크**: 설정되어 있으면 Allow된 Action이 Boundary 범위 내인지 확인
6. **Step 6 — 최종 결정**: 모든 조건을 통과하면 ✅ 허용, 아니면 ❌ 암묵적 거부

### 💻 정책 예시: 복합 조건

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3ReadWithMFA",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::confidential-data",
        "arn:aws:s3:::confidential-data/*"
      ],
      "Condition": {
        "Bool": {"aws:MultiFactorAuthPresent": "true"},
        "IpAddress": {"aws:SourceIp": "10.0.0.0/16"}
      }
    },
    {
      "Sid": "DenyDeleteAlways",
      "Effect": "Deny",
      "Action": "s3:DeleteObject",
      "Resource": "arn:aws:s3:::confidential-data/*"
    }
  ]
}
```

> 📌 위 정책은 "MFA 인증 + 사내 IP에서만 S3 읽기 허용, 삭제는 무조건 거부"를 의미한다.

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| # | 유즈 케이스 | 설명 | 적합한 정책 유형 |
|---|------------|------|-----------------|
| 1 | **개발팀 S3 접근 제어** | 특정 버킷에만 읽기/쓰기, 삭제는 거부 | Identity-based (Group에 연결) |
| 2 | **cross-account S3 공유** | 다른 AWS 계정이 내 S3 버킷에 접근 | Resource-based (Bucket Policy) |
| 3 | **위임 권한 상한 설정** | 팀장이 팀원에게 부여할 수 있는 최대 권한 제한 | Permissions Boundary |
| 4 | **조직 전체 서비스 제한** | 특정 리전 외 리소스 생성 금지 | SCP (Organizations) |
| 5 | **MFA 강제** | MFA 미인증 시 대부분 Action 거부 | Identity-based (Deny + Condition) |

### ✅ 베스트 프랙티스

1. **📐 최소 권한으로 시작**: `"Action": "*"`, `"Resource": "*"`로 시작하지 말고, 필요한 Action과 Resource만 명시. IAM Access Analyzer로 실제 사용된 권한을 기반으로 정책 생성 ([AWS Security Blog](https://aws.amazon.com/blogs/security/techniques-for-writing-least-privilege-iam-policies/))
2. **📋 Customer Managed Policy 사용**: AWS Managed Policy를 그대로 쓰지 말고, 필요한 부분만 복사하여 Customer Managed Policy로 커스터마이징
3. **🏷️ Condition 적극 활용**: IP 범위(`aws:SourceIp`), MFA 여부(`aws:MultiFactorAuthPresent`), 태그(`aws:ResourceTag`) 등으로 접근 범위를 세밀하게 제한
4. **📊 IAM Access Analyzer 활성화**: 과도한 권한 자동 탐지, 정책 검증(100+ 체크), CloudTrail 기반 최소 권한 정책 자동 생성
5. **🔄 정기적 정책 리뷰**: IAM Console의 **Access Advisor** 탭에서 마지막 접근 시간을 확인하여 미사용 권한 제거

### 🏢 실제 적용 사례

- **금융 기업**: SCP로 `ap-northeast-2`(서울) 리전 외 리소스 생성을 전면 차단 + Permissions Boundary로 개발팀 최대 권한 제한
- **SaaS 스타트업**: Resource-based Policy로 고객 계정 간 데이터 격리 + Condition으로 VPC Endpoint만 허용

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ 장점 | **선언적 JSON** | 코드로 관리 가능, IaC와 자연스럽게 통합 |
| ✅ 장점 | **세밀한 제어** | Action 단위(예: `s3:GetObject` vs `s3:PutObject`)로 제어 |
| ✅ 장점 | **다층 방어** | Identity + Resource + Boundary + SCP 조합으로 계층적 보안 |
| ✅ 장점 | **재사용성** | Managed Policy를 여러 엔터티에 공유 |
| ❌ 단점 | **복잡한 평가 로직** | 7가지 정책 유형의 상호작용 이해가 어려움 |
| ❌ 단점 | **크기 제한** | Managed Policy: 6,144자, Inline: 2,048자 (User), 10,240자 (Group/Role) |
| ❌ 단점 | **디버깅 어려움** | `AccessDenied` 에러가 어떤 정책 때문인지 특정하기 어려움 |
| ❌ 단점 | **Wildcard 유혹** | `"*"` 하나면 에러가 사라져서 과도한 권한 부여 유혹 |

### ⚖️ Trade-off 분석

```
세밀한 제어     ◄──────── Trade-off ────────►  JSON 작성 복잡도
다층 방어       ◄──────── Trade-off ────────►  평가 로직 이해 난이도
재사용성        ◄──────── Trade-off ────────►  관리할 정책 수 증가
Condition 유연성 ◄──────── Trade-off ────────►  조건 조합 테스트 어려움
```

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 비교 매트릭스: Managed Policy vs Inline Policy vs Resource-based Policy

| 비교 기준 | Managed Policy | Inline Policy | Resource-based Policy |
|-----------|---------------|---------------|----------------------|
| **부착 대상** | User, Group, Role | User, Group, Role | S3, SQS, KMS 등 리소스 |
| **재사용** | ✅ 다수에 공유 가능 | ❌ 1:1 관계 | ❌ 해당 리소스 전용 |
| **수명 주기** | 독립적 (삭제해도 엔터티 유지) | 엔터티 삭제 시 함께 삭제 | 리소스와 함께 |
| **크기 제한** | 6,144자 | 2,048~10,240자 | 서비스별 상이 |
| **Principal 지정** | ❌ 불필요 (부착 대상이 Principal) | ❌ 불필요 | ✅ 필수 (누구에게 허용?) |
| **Cross-account** | ❌ 불가 | ❌ 불가 | ✅ 가능 |
| **AWS 권장** | ✅ 일반적 권한 관리 | ⚠️ 특수 경우만 | ✅ cross-account, 리소스 수준 |

### 🔍 핵심 차이 요약

```
Managed Policy                  Inline Policy
──────────────────────    vs    ──────────────────────
재사용 가능 (N:M)                1:1 관계 (엔터티 전용)
독립 수명 주기                    엔터티와 생사를 같이 함
버전 관리 지원                    버전 관리 없음
최대 6,144자                     최대 2,048~10,240자
권장됨 ✅                        특수 경우만 ⚠️
```

### 🤔 언제 무엇을 선택?

- **Managed Policy** → 여러 User/Group/Role에 동일한 권한을 부여할 때 (대부분의 경우)
- **Inline Policy** → 정책이 반드시 특정 엔터티에서만 사용되어야 하고, 엔터티 삭제 시 함께 제거되어야 할 때
- **Resource-based Policy** → cross-account 접근 허용, 또는 리소스 자체에서 접근을 제어할 때

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|------|-----------|------------|
| 1 | `"Action": "*", "Resource": "*"` 사용 | 모든 서비스의 모든 리소스에 전체 접근 — 계정 장악 위험 | 필요한 Action과 Resource를 구체적으로 지정 |
| 2 | `AccessDenied` 해결하려고 `"*"` 추가 | 디버깅 대신 권한을 넓히면 보안 구멍 생성 | CloudTrail 로그에서 실패한 Action 확인 후 해당 Action만 추가 |
| 3 | Sandbox Policy를 Production에 복사 | 개발 환경의 넓은 권한이 프로덕션에 적용됨 | 환경별 별도 Policy 관리, IAM Access Analyzer로 검증 |
| 4 | Condition 없이 Deny 작성 | 의도치 않게 정당한 접근까지 차단 | Deny 규칙에는 반드시 Condition을 포함하여 범위 한정 |
| 5 | 정책 크기 제한 미인지 | 6,144자 초과 시 저장 실패 | 기능별로 Policy를 분리하여 각각 연결 |

### 🚫 Anti-Patterns

1. **Wildcard 남용**: `s3:*` 대신 실제 필요한 `s3:GetObject`, `s3:PutObject`만 지정한다. 90%의 AWS 계정에서 발견되는 가장 흔한 보안 미구성 ([DEV Community](https://dev.to/dannysteenman/10-aws-security-misconfigurations-found-in-90-of-accounts-835))
2. **정책 리뷰 없는 운영**: 정책을 만들어놓고 리뷰하지 않으면 시간이 지나며 과도한 권한이 누적된다. 분기별 IAM Access Advisor 확인 필수 ([Cloud Security In Practice](https://cloudsecurityinpractice.com/en/2026/02/01/common-aws-iam-mistakes-in-enterprises/))
3. **NotAction 오용**: `"NotAction": "iam:*"` 은 "IAM 제외 모든 서비스 허용"인데, 새 서비스 추가 시 자동 허용됨. 의도한 것이 맞는지 항상 재확인

### 🔒 보안/성능 고려사항

- **보안**: 명시적 Deny가 명시적 Allow보다 항상 우선한다 — 보안 가드레일은 Deny 정책으로 구현
- **보안**: Cross-account 접근에는 **양쪽 모두** 정책이 필요하다 (Resource-based Policy + Identity-based Policy)
- **운영**: Policy Simulator(`iam:SimulatePrincipalPolicy`)를 사용하여 배포 전 권한 동작을 테스트

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|------|------|----------|
| 📖 공식 문서 | Policies and Permissions | [AWS IAM Policies Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html) |
| 📖 공식 문서 | Policy Evaluation Logic | [Evaluation Logic](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html) |
| 📖 공식 문서 | JSON Policy Reference | [Policy Elements Reference](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html) |
| 📘 블로그 | Least Privilege 기법 | [AWS Security Blog](https://aws.amazon.com/blogs/security/techniques-for-writing-least-privilege-iam-policies/) |
| 📘 블로그 | IAM Policy Types 가이드 | [AWS Security Blog - Policy Types](https://aws.amazon.com/blogs/security/iam-policy-types-how-and-when-to-use-them/) |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리 | 플랫폼 | 용도 |
|---------------|--------|------|
| **IAM Policy Simulator** | AWS Console/CLI | 정책 동작 사전 테스트 |
| **IAM Access Analyzer** | AWS Console | 과도한 권한 탐지 + 최소 권한 정책 자동 생성 |
| **CloudTrail** | AWS | API 호출 이력 기반 실제 사용 권한 파악 |
| **Terraform** | IaC | `aws_iam_policy`, `aws_iam_policy_document` 데이터 소스 |
| **IAM Policy Visual Editor** | AWS Console | JSON 없이 GUI로 정책 작성 |
| **tfsec / checkov** | 정적 분석 | Terraform 코드에서 wildcard 정책 자동 탐지 |

### 🔮 트렌드 & 전망

- **IAM Access Analyzer 고도화**: CloudTrail 기반으로 실제 사용된 Action만 포함하는 최소 권한 정책을 **자동 생성**하는 기능이 강화되는 추세
- **ABAC (Attribute-Based Access Control)**: 리소스 태그 + 사용자 태그 기반으로 동적 권한을 부여하는 패턴이 확산 — 정적 정책 수를 줄이는 효과
- **Cedar Policy Language**: AWS에서 개발한 새로운 정책 언어로, IAM JSON보다 읽기 쉽고 정적 분석이 용이. Amazon Verified Permissions에서 사용 중

### 💬 커뮤니티 인사이트

- `AccessDenied` 디버깅 시 가장 먼저 확인할 것: CloudTrail에서 실패한 API 호출의 `eventName`과 `errorCode`
- "Policy를 잘 모르겠으면 IAM Policy Simulator부터 돌려라"가 실무자들의 공통 조언
- Terraform으로 IAM 관리 시 `aws_iam_policy_document` 데이터 소스가 JSON 직접 작성보다 훨씬 안전하고 가독성 좋다는 의견 다수

---

## 📎 Sources

1. [Policies and Permissions in IAM - AWS Official Docs](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html) — 공식 문서
2. [Policy Evaluation Logic - AWS Official Docs](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html) — 공식 문서
3. [IAM JSON Policy Element Reference](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html) — 공식 문서
4. [IAM Policy Types: How and When to Use Them - AWS Security Blog](https://aws.amazon.com/blogs/security/iam-policy-types-how-and-when-to-use-them/) — 공식 블로그
5. [Techniques for Writing Least Privilege IAM Policies - AWS Security Blog](https://aws.amazon.com/blogs/security/techniques-for-writing-least-privilege-iam-policies/) — 공식 블로그
6. [10 AWS Security Misconfigurations - DEV Community](https://dev.to/dannysteenman/10-aws-security-misconfigurations-found-in-90-of-accounts-835) — 블로그
7. [Common AWS IAM Mistakes - Cloud Security In Practice](https://cloudsecurityinpractice.com/en/2026/02/01/common-aws-iam-mistakes-in-enterprises/) — 블로그
8. [AWS IAM Anti-Patterns - StackProof](https://stackproof.dev/play-books/aws-iam-anti-patterns-and-how-to-fix-them/) — 블로그

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 5
> - 수집 출처 수: 8
> - 출처 유형: 공식 5, 블로그 3, 커뮤니티 1, SNS 0
> - 관련 문서: [[05-aws-iam-concept-explainer]], [[01-aws-iam-user-concept-explainer]], [[02-aws-iam-group-concept-explainer]], [[04-aws-iam-role-concept-explainer]]
