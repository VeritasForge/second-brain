---
tags: [security, aws, iam, authentication, authorization, concept-explainer]
created: 2026-04-22
---

# 📖 AWS IAM (Identity and Access Management) — Concept Deep Dive

> 💡 **��줄 요약**: AWS IAM은 **"누가(Identity) 무엇을(Resource) 할 수 있는가(Permission)"**를 통제하는 AWS의 **무료 글로벌 접근 제어 서비스**로, User · Group · Policy · Role 4대 구성요소로 이루어진다.

> **하위 개념 상세**: [[01-aws-iam-user-concept-explainer]], [[02-aws-iam-group-concept-explainer]], [[03-aws-iam-policy-concept-explainer]], [[04-aws-iam-role-concept-explainer]]

---

## 1️⃣ 무엇인가? (What is it?)

**AWS IAM(Identity and Access Management)**은 AWS 리소스에 대한 접근을 안전하게 관리하는 **웹 서비스**이다. **인증(Authentication, 누구인가?)**과 **인가(Authorization, 무엇을 할 수 있는가?)**를 모두 담당한다.

**현실 세계 비유 (12살도 이해할 수 있는 설명):**

대형 빌딩의 **보안 시스템**을 생각하자. 이 시스템은 세 가지를 한다:
1. **신분 확인** — 출입구에서 사원증을 찍으면 "이 사람이 정말 직원인가?" 확인 (인증)
2. **권한 확인** — "이 직원이 5층 서버실에 들어갈 수 있는가?" 확인 (인가)
3. **기록** — 누가 언제 어디를 출입했는지 기록 (감사)

IAM은 AWS라는 거대한 빌딩의 보안 시스템이다. 사원증(User), 부서 카드(Group), 출입 규칙(Policy), 임시 방문증(Role)을 관리한다.

- **핵심 특성**: **무료**(추가 과금 없음), **글로벌**(리전에 종속되지 않음), **모든 AWS 서비스와 통합**
- **해결하는 문제**: Root User 남용 방지, 최소 권한 원칙 구현, 멀티 계정/멀티 서비스 환경의 중앙 접근 제어

> 📌 **핵심 키워드**: `IAM`, `Authentication`, `Authorization`, `Principal`, `Policy`, `ARN`, `Least Privilege`, `Zero Trust`

---

## 2️⃣ 핵심 개념 (Core Concepts)

IAM은 **4대 구성요소**와 이들을 평가하는 **정책 엔진**으로 이루어진다.

```
┌─────────────────────────────────────────────────────────────────┐
│                    AWS IAM 4대 구성요소                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│       ┌─────────────┐         ┌─────────────┐                   │
│       │  👤 User     │────┬───│  👥 Group    │                   │
│       │ (개별 신원)   │    │   │ (User 집합)  │                   │
│       │              │    │   │              │                   │
│       │ 장기 자격증명  │    │   │ Policy 상속  │                   │
│       └──────────────┘    │   └──────────────┘                   │
│                           │                                     │
│          ┌────────────────┴────────────────┐                    │
│          │          📋 Policy               │                    │
│          │  (JSON 권한 문서)                 │                    │
│          │  Effect + Action + Resource      │                    │
│          │  + Condition                     │                    │
│          └────────────────┬────────────────┘                    │
│                           │                                     │
│       ┌──────────────┐    │                                     │
│       │  🎭 Role      │────┘                                    │
│       │ (임시 신원)   │                                          │
│       │              │                                          │
│       │ STS 임시 토큰 │                                          │
│       │ Trust Policy  │                                          │
│       └──────────────┘                                          │
│                                                                 │
│  ════════════════════════════════════════════════                │
│  모든 요청 → IAM 정책 엔진이 평가 → Allow / Deny                  │
│  ════════════════════════════════════════════════                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

| 구성요소 | 역할 | 비유 | 상세 문서 |
|---------|------|------|----------|
| **User** | 개별 사용자/애플리케이션 신원 | 사원증 | [[01-aws-iam-user-concept-explainer]] |
| **Group** | User 집합, 권한 일괄 부여 | 부서 카드 | [[02-aws-iam-group-concept-explainer]] |
| **Policy** | JSON 권한 문서 (Allow/Deny) | 출입 규칙표 | [[03-aws-iam-policy-concept-explainer]] |
| **Role** | 임시 자격증명 기반 신원 | 임시 방문증 | [[04-aws-iam-role-concept-explainer]] |

### 🔑 인증(Authentication) vs 인가(Authorization)

| 단계 | 질문 | IAM 메커니즘 | 실패 시 |
|------|------|-------------|--------|
| **인증** | "당신은 누구인가?" | Password, Access Key, MFA, STS Token | `SignatureDoesNotMatch` |
| **인가** | "당신은 무엇을 할 수 있는가?" | Policy 평가 엔진 | `AccessDenied` |

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

IAM은 **모든 AWS API 호출의 관문**이다. 콘솔, CLI, SDK 어떤 경로든 IAM 정책 엔진을 거친다.

```
┌─────────────────────────────────────────────────────────────────┐
│                    AWS IAM 요청 처리 아키텍처                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📱 Console  💻 CLI  🔧 SDK  🌐 API                             │
│      │         │       │       │                                │
│      └─────────┴───────┴───────┘                                │
│                    │                                            │
│                    ▼                                            │
│  ┌────────────────────────────────────┐                         │
│  │        ① 인증 (Authentication)      │                         │
│  │                                    │                         │
│  │  자격증명 검증:                     │                         │
│  │  • User → Password / Access Key    │                         │
│  │  • Role → STS Token               │                         │
│  │  • Federation → SAML / OIDC Token  │                         │
│  │  • MFA 코드 검증 (설정된 경우)      │                         │
│  └──────────────┬─────────────────────┘                         │
│                  │ ✅ 신원 확인됨                                 │
│                  ▼                                              │
│  ┌────────────────────────────────────┐                         │
│  │        ② 인가 (Authorization)       │                         │
│  │                                    │                         │
│  │  정책 평가 순서:                    │                         │
│  │  1. 명시적 Deny 체크 (있으면 즉시 거부)│                       │
│  │  2. SCP / RCP 체크 (Organizations)  │                         │
│  │  3. Identity-based Policy 체크      │                         │
│  │  4. Resource-based Policy 체크      │                         │
│  │  5. Permissions Boundary 체크       │                         │
│  │  6. Session Policy 체크 (있으면)     │                         │
│  └──────────────┬─────────────────────┘                         │
│            ┌────┴────┐                                          │
│            ▼         ▼                                          │
│      ✅ 허용    ❌ 거부                                          │
│      (Action    (AccessDenied                                   │
│       실행)      반환)                                           │
│                                                                 │
│  ┌────────────────────────────────────┐                         │
│  │        ③ 감사 (Audit)               │                         │
│  │                                    │                         │
│  │  모든 API 호출 → CloudTrail 기록    │                         │
│  │  (누가, 언제, 어디서, 무엇을)        │                         │
│  └────────────────────────────────────┘                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (Step by Step)

1. **Step 1 — 요청**: 사용자/서비스가 AWS API를 호출 (예: `s3:PutObject`)
2. **Step 2 — 인증**: IAM이 자격증명(Password, Access Key, STS Token)을 검증하여 **Principal(요청 주체)**을 확인
3. **Step 3 — 컨텍스트 수집**: 요청의 Action, Resource, Condition(IP, 시간, MFA 등)을 수집
4. **Step 4 — 정책 평가**: 해당 Principal에 적용되는 모든 정책(Identity-based, Resource-based, SCP, Boundary 등)을 평가
5. **Step 5 — 결정**: 명시적 Deny → 거부 | 명시적 Allow → 허용 | 둘 다 없음 → 암묵적 거부
6. **Step 6 — 감사**: CloudTrail이 모든 호출을 기록 (성공/실패 모두)

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| # | 유즈 케이스 | IAM 구성요소 활용 | 설명 |
|---|------------|------------------|------|
| 1 | **팀별 AWS 접근 관리** | User + Group + Policy | 개발팀/운영팀/재무팀에 직무별 권한 부여 |
| 2 | **EC2 → S3 데이터 접근** | Role (Instance Profile) | Access Key 없이 임시 자격증명으로 접근 |
| 3 | **멀티 계정 조직** | Role + SCP + Organizations | 중앙 인증 + 계정별 최대 권한 제한 |
| 4 | **CI/CD 배포** | Role + OIDC Federation | GitHub Actions에서 장기 Key 없이 배포 |
| 5 | **보안 감사** | Policy + CloudTrail | ReadOnly 정책 + 모든 API 호출 기록 |

### ✅ 베스트 프랙티스

1. **🔒 Root User 잠그기**: Root User에 MFA 적용, 일상 작업에 사용 금지. 관리자 IAM User 또는 IAM Identity Center 사용 ([AWS Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html))
2. **📐 최소 권한 원칙**: 필요한 Action과 Resource만 허용. `"*"` 남용 금지. IAM Access Analyzer로 자동 검증
3. **🎭 임시 자격증명 우선**: IAM User Access Key 대신 IAM Role + STS 임시 자격증명 사용
4. **👥 Group으로 권한 관리**: 개별 User에 Policy 직접 연결 대신 Group을 통해 일괄 관리
5. **📱 MFA 필수**: 모든 사용자에 MFA 적용, 특히 관리자와 Cross-Account Role Assume에 필수
6. **📊 정기 감사**: IAM Credential Report + Access Advisor + CloudTrail로 미사용 권한/자격증명 정리

### 🏢 실제 적용 패턴

- **소규모(1-10명)**: Root 잠금 + Admin User + Developers Group + ReadOnly Group
- **중규모(10-100명)**: IAM Identity Center(SSO) + Cross-Account Role + SCP
- **대규모(100명+)**: AWS Organizations + IAM Identity Center + ABAC(태그 기반) + 자동화된 정책 리뷰

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ 장점 | **무료** | IAM 자체에 비용 없음, 모든 AWS 계정에 포함 |
| ✅ 장점 | **글로벌** | 리전에 종속되지 않고 전 세계 동일하게 적용 |
| ✅ 장점 | **세밀한 제어** | Action 수준의 권한 제어 + Condition으로 상황별 분기 |
| ✅ 장점 | **다층 방어** | Identity + Resource + Boundary + SCP 조합 |
| ✅ 장점 | **AWS 전 서비스 통합** | 모든 AWS 서비스가 IAM으로 접근 제어 |
| ❌ 단점 | **학습 곡선 높음** | 7가지 정책 유형, 복잡한 평가 로직 |
| ❌ 단점 | **디버깅 어려움** | `AccessDenied` 원인 특정이 어려움 |
| ❌ 단점 | **IAM User 한계** | 계정당 5,000명 제한, 멀티 계정 시 관리 복잡 |

### ⚖️ Trade-off 분석

```
무료 + 글로벌     ◄──────── Trade-off ────────►  학습 곡선 높음
세밀한 제어       ◄──────── Trade-off ────────►  정책 JSON 복잡도
다층 방어         ◄──────── Trade-off ────────►  평가 로직 이해 필요
전 서비스 통합    ◄──────── Trade-off ────────►  서비스별 Action 학습 필요
```

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 비교 매트릭스: 3대 클라우드 IAM 비교

| 비교 기준 | AWS IAM | Azure Entra ID (구 Azure AD) | Google Cloud IAM |
|-----------|---------|---------------------------|------------------|
| **비용** | 무료 | 기본 무료, 고급 기능 유료 | 무료 |
| **사용자 관리** | 자체 (IAM User) + Federation | Active Directory 기반 | Google Account 기반 |
| **권한 모델** | Policy JSON (Action + Resource) | RBAC (Built-in/Custom Roles) | RBAC (Predefined/Custom Roles) |
| **리소스 계층** | Account 단위 | Organization → Subscription | Organization → Project |
| **임시 자격증명** | STS AssumeRole | Managed Identity | Service Account Key / Workload Identity |
| **조직 관리** | AWS Organizations + SCP | Management Groups | Folders + Organization Policies |
| **강점** | 세밀한 JSON 정책 제어 | 기업 AD 통합 | 깔끔한 계층 구조 |

### 🔍 핵심 차이 요약

```
AWS IAM                           Azure Entra ID
──────────────────────    vs    ──────────────────────
JSON Policy (세밀, 복잡)          RBAC (구조적, 단순)
자체 User + Federation            Active Directory 기반
Account 단위 격리                  Organization 단위
Policy 자유도 높음                 Built-in Role 중심
```

### 🤔 언제 무엇을 선택?

- **AWS IAM** → AWS 전용 워크로드, 세밀한 Action 수준 제어가 필요할 때
- **Azure Entra ID** → Microsoft 365 / Active Directory 기반 기업 환경
- **Google Cloud IAM** → GCP 워크로드, 깔끔한 프로젝트 기반 구조 선호 시

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|------|-----------|------------|
| 1 | Root User로 일상 작업 | 탈취 시 계정 전체 장악, 권한 제한 불가 | 관리자 IAM User/Identity Center 사용 |
| 2 | 모든 User에 `AdministratorAccess` | 최소 권한 원칙 위반, 내부 위협 확대 | 직무별 Group + 최소 권한 Policy |
| 3 | MFA 미적용 | 패스워드만으로는 피싱에 취약 | 모든 User + Root에 MFA 필수 |
| 4 | Access Key 코드 하드코딩 | GitHub 커밋 시 수 분 내 봇이 탐지 | IAM Role (Instance Profile, OIDC) 사용 |
| 5 | 정책 리뷰 미실시 | 시간이 지나며 과도한 권한 누적 | 분기별 Access Advisor + Credential Report |

### 🚫 Anti-Patterns

1. **IAM User를 사람 접근에 남용**: AWS는 사람의 접근에 IAM Identity Center(SSO)를 **명시적으로 권장**. IAM User는 Role을 사용할 수 없는 워크로드 전용
2. **콘솔에서 수동 IAM 관리**: IaC(Terraform/CloudFormation) 없이 콘솔에서 수동으로 Policy/Role을 관리하면 드리프트 발생, 감사 불가
3. **단일 계정에 모든 것 몰아넣기**: 환경(dev/staging/prod)별로 AWS 계정을 분리하고 Organizations + SCP로 관리해야 한다

### 🔒 보안/성능 고려사항

- **보안**: IAM은 **글로벌 서비스**이므로 한 리전에서 만든 User/Role/Policy는 모든 리전에서 유효
- **보안**: CloudTrail은 IAM API 호출도 기록한다. `CreateUser`, `AttachPolicy` 등 민감한 Action에 CloudWatch Alarm 설정 권장
- **운영**: IAM API에는 Rate Limit이 있다. 자동화 스크립트에서 대량 호출 시 exponential backoff 적용

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|------|------|----------|
| 📖 공식 문서 | What is IAM? | [AWS IAM Introduction](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html) |
| 📖 공식 문서 | How IAM Works | [IAM Architecture](https://docs.aws.amazon.com/IAM/latest/UserGuide/intro-structure.html) |
| 📖 공식 문서 | Security Best Practices | [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) |
| 📘 블로그 | AWS IAM Deep Dive | [CloudChipr](https://cloudchipr.com/blog/aws-iam) |
| 📘 블로그 | 3대 클라우드 IAM 비교 | [Pluralsight](https://www.pluralsight.com/resources/blog/cloud/comparing-aws-azure-and-google-cloud-iam-services) |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리 | 플랫폼 | 용도 |
|---------------|--------|------|
| **IAM Policy Simulator** | AWS Console | 정책 동작 사전 테스트 |
| **IAM Access Analyzer** | AWS Console | 과도한 권한 탐지, 외부 접근 분석 |
| **IAM Credential Report** | AWS Console/CLI | 전체 User 자격증명 상태 CSV |
| **CloudTrail** | AWS | 모든 IAM API 호출 감사 로그 |
| **Terraform** | IaC | IAM 전체를 코드로 관리 |
| **AWS Organizations** | AWS | SCP로 멀티 계정 권한 상한 제어 |

### 🔮 트렌드 & 전망

- **IAM Identity Center 표준화**: IAM User → IAM Identity Center(SSO) 마이그레이션이 업계 표준으로 자리잡는 중
- **ABAC 확산**: 태그 기반 동적 권한 부여가 정적 Policy 수를 줄이고 확장성을 높이는 패턴으로 채택
- **Cedar Policy Language**: AWS가 개발한 새로운 정책 언어. Amazon Verified Permissions에서 사용, 향후 IAM과의 통합 가능성
- **Zero Trust 가속**: "네트워크 내부도 신뢰하지 않는다" 원칙에 따라 임시 자격증명 + Condition 강화 추세

### 💬 커뮤니티 인사이트

- "IAM은 AWS에서 가장 중요한 서비스이면서 가장 과소평가되는 서비스"라는 의견이 보안 커뮤니티에서 자주 등장
- AWS re:Invent 세션에서 반복되는 메시지: "IAM은 무료이지만, 잘못 설정하면 가장 비싼 서비스가 된다" (보안 사고 비용)
- 실무자들이 가장 먼저 추천하는 학습 순서: User → Group → Policy → Role → Organizations/SCP

---

## 📎 Sources

1. [What is IAM? - AWS Official Docs](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html) — 공식 문서
2. [How IAM Works - AWS Official Docs](https://docs.aws.amazon.com/IAM/latest/UserGuide/intro-structure.html) — 공식 문서
3. [Security Best Practices in IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) — 공식 문서
4. [Inside AWS IAM: A Deep Dive - CloudChipr](https://cloudchipr.com/blog/aws-iam) — 블로그
5. [Comparing AWS, Azure, and Google Cloud IAM - Pluralsight](https://www.pluralsight.com/resources/blog/cloud/comparing-aws-azure-and-google-cloud-iam-services) — 블로그
6. [AWS, Azure and GCP IAM Comparison - Tenable](https://www.tenable.com/blog/aws-azure-and-gcp-the-ultimate-iam-comparison) — 블로그

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 2 (+ Task 1-4의 누적 리서치 활용)
> - 수집 출처 수: 6
> - 출처 유형: 공식 3, 블로그 3, 커뮤니티 0, SNS 0
> - 관련 문서: [[01-aws-iam-user-concept-explainer]], [[02-aws-iam-group-concept-explainer]], [[03-aws-iam-policy-concept-explainer]], [[04-aws-iam-role-concept-explainer]], [[06-aws-iam-architecture-and-integration]]
