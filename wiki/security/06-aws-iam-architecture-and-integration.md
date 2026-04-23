---
tags: [security, aws, iam, iam-user, iam-group, iam-policy, iam-role, architecture, deep-research]
created: 2026-04-22
---

# 🔬 AWS IAM 4요소 유기적 결합 — Deep Research

> **관련 문서**: [[05-aws-iam-concept-explainer]], [[01-aws-iam-user-concept-explainer]], [[02-aws-iam-group-concept-explainer]], [[03-aws-iam-policy-concept-explainer]], [[04-aws-iam-role-concept-explainer]]

---

## 📋 Executive Summary

AWS IAM의 4대 구성요소(User, Group, Policy, Role)는 독립적으로 존재하지 않는다. **Policy가 "무엇을"**, **User/Role이 "누가"**, **Group이 "어떤 단위로"**를 정의하며, 이들의 조합이 실제 운영 환경의 접근 제어를 형성한다.

이 문서는 4가지 실제 시나리오를 통해 이들이 어떻게 유기적으로 결합되는지 분석한다:
1. 신규 개발자 온보딩
2. CI/CD 파이프라인 (GitHub Actions + OIDC)
3. Cross-Account 접근 (멀티 계정)
4. 엔터프라이즈 멀티 계정 조직 관리

---

## 1️⃣ IAM 4요소의 관계: "조직 → 신원 → 규칙"

SSO/OAuth가 "목표 vs 수단"의 관계였던 것처럼, IAM 4요소도 **역할 분담**의 관계이다.

```
┌─────────────────────────────────────────────────────────────────┐
│                  IAM 4요소 관계 다이어그램                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   "누가?"                "어떤 단위로?"          "무엇을?"        │
│   (Identity)            (Organization)         (Permission)     │
│                                                                 │
│   ┌──────────┐          ┌──────────┐          ┌──────────┐     │
│   │ 👤 User  │──소속──►│ 👥 Group │◄──연결──│ 📋 Policy│     │
│   │ (장기)   │          │ (집합)   │          │ (규칙)   │     │
│   └──────────┘          └──────────┘          └──────────┘     │
│                                                    │            │
│   ┌──────────┐                                     │            │
│   │ 🎭 Role  │◄───────────── 연결 ────────────────┘            │
│   │ (임시)   │                                                  │
│   └──────────┘                                                  │
│        ▲                                                        │
│        │ AssumeRole                                             │
│   ┌────┴─────────────────────────────────┐                     │
│   │  AWS 서비스 | 다른 계정 | 외부 IdP    │                     │
│   │  (EC2, Lambda, GitHub Actions, ...)  │                     │
│   └──────────────────────────────────────┘                     │
│                                                                 │
│   ════════════════════════════════════════════                  │
│   핵심 원칙: Policy는 항상 "누군가"에게 연결되어야 효력이 있다     │
│   • User에 직접 → 개별 권한 (비권장)                             │
│   • Group에 연결 → User들이 상속 (사람 관리용)                   │
│   • Role에 연결 → AssumeRole 시 획득 (서비스/위임용)             │
│   ════════════════════════════════════════════                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 🤔 User vs Role: 언제 무엇을?

| 상황 | User | Role | 이유 |
|------|------|------|------|
| 사람이 콘솔 접근 | ⚠️ 레거시 | ✅ IAM Identity Center + Role | 임시 자격증명이 안전 |
| EC2 → S3 접근 | ❌ Key 하드코딩 | ✅ Instance Profile | 자동 자격증명 갱신 |
| GitHub Actions 배포 | ❌ 장기 Key | ✅ OIDC Federation | Key 유출 위험 제거 |
| 서드파티 SaaS 연동 | ❌ Key 공유 | ✅ Cross-Account Role | External ID로 보안 강화 |
| Role 미지원 레거시 도구 | ✅ 유일한 대안 | ❌ 불가 | 최소한으로 제한 |

---

## 2️⃣ 시나리오 A: 신규 개발자 온보딩

### 📋 시나리오 설명

새 개발자 "cjynim"이 팀에 합류하여 S3 읽기/쓰기, EC2 인스턴스 관리, CloudWatch 로그 조회가 필요하다.

### 🔄 결합 흐름

```
┌─────────────────────────────────────────────────────────────────┐
│                  신규 개발자 온보딩 흐름                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ① IAM User "cjynim" 생성                                      │
│     └─ Console Password + MFA 필수 설정                         │
│                                                                 │
│  ② Group에 추가                                                 │
│     ├─ "Developers" Group → S3/EC2/CloudWatch 권한 상속         │
│     └─ "ForceMFA" Group → MFA 미설정 시 대부분 Action 거부       │
│                                                                 │
│  ③ Group에 연결된 Policy들                                       │
│     ├─ CustomDeveloperPolicy (S3 + EC2 + CloudWatch)            │
│     ├─ ForceMFAPolicy (MFA Condition 기반 Deny)                 │
│     └─ DenyDeletePolicy (S3 삭제 명시적 거부)                    │
│                                                                 │
│  ④ 부서 이동 시                                                  │
│     ├─ "Developers"에서 제거                                     │
│     └─ "DataEngineers"에 추가 → 즉시 권한 전환                   │
│                                                                 │
│  ⑤ 퇴사 시                                                      │
│     ├─ 모든 Group에서 제거                                       │
│     ├─ Console Password 비활성화                                 │
│     ├─ Access Key 비활성화/삭제                                   │
│     └─ IAM User 삭제 (또는 보관)                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 💻 Terraform 코드 예시

```hcl
# ── Group 정의 ──────────────────────────────────
resource "aws_iam_group" "developers" {
  name = "Developers"
}

# ── Custom Policy 정의 ──────────────────────────
data "aws_iam_policy_document" "developer_access" {
  # S3 읽기/쓰기 (특정 버킷만)
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
    resources = [
      "arn:aws:s3:::project-alpha-*",
      "arn:aws:s3:::project-alpha-*/*"
    ]
  }

  # EC2 인스턴스 관리 (태그 기반)
  statement {
    effect  = "Allow"
    actions = [
      "ec2:StartInstances",
      "ec2:StopInstances",
      "ec2:DescribeInstances"
    ]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "ec2:ResourceTag/Team"
      values   = ["development"]
    }
  }

  # CloudWatch 로그 조회
  statement {
    effect    = "Allow"
    actions   = ["logs:GetLogEvents", "logs:DescribeLogGroups", "logs:DescribeLogStreams"]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "developer_access" {
  name   = "CustomDeveloperAccess"
  policy = data.aws_iam_policy_document.developer_access.json
}

# ── Group에 Policy 연결 ────────────────────────
resource "aws_iam_group_policy_attachment" "developers_policy" {
  group      = aws_iam_group.developers.name
  policy_arn = aws_iam_policy.developer_access.arn
}

# ── User 생성 및 Group 소속 ────────────────────
resource "aws_iam_user" "cjynim" {
  name = "cjynim"
  tags = { Team = "development", Role = "developer" }
}

resource "aws_iam_user_group_membership" "cjynim_groups" {
  user   = aws_iam_user.cjynim.name
  groups = [aws_iam_group.developers.name]
}
```

---

## 3️⃣ 시나리오 B: CI/CD 파이프라인 (GitHub Actions + OIDC)

### 📋 시나리오 설명

GitHub Actions에서 Terraform으로 AWS 인프라를 배포한다. **장기 Access Key 없이** OIDC Federation으로 임시 자격증명을 획득한다.

### 🔄 결합 흐름

```
┌─────────────────────────────────────────────────────────────────┐
│              GitHub Actions OIDC 배포 흐름                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  GitHub Actions Runner                                          │
│    │                                                            │
│    │ ① GitHub OIDC Token 발급                                   │
│    │   (JWT: repo, branch, workflow 정보 포함)                   │
│    │                                                            │
│    ▼                                                            │
│  AWS STS                                                        │
│    │                                                            │
│    │ ② AssumeRoleWithWebIdentity                                │
│    │   - OIDC Provider 검증                                     │
│    │   - Trust Policy 조건 확인                                  │
│    │     (repo = "myorg/myrepo", branch = "main")               │
│    │                                                            │
│    │ ③ 임시 자격증명 발급 (15분~1시간)                            │
│    ▼                                                            │
│  Terraform                                                      │
│    │                                                            │
│    │ ④ 임시 자격증명으로 AWS API 호출                             │
│    │   - Permission Policy가 허용하는 범위 내에서만               │
│    │                                                            │
│    ▼                                                            │
│  AWS 리소스 (EC2, S3, RDS, ...)                                  │
│    │                                                            │
│    │ ⑤ CloudTrail 감사 로그                                     │
│    │   - "github-actions-session" 세션 이름으로 추적              │
│    ▼                                                            │
│  ⏰ 세션 만료 → 자격증명 자동 무효화                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 💻 Terraform 코드 예시

```hcl
# ── OIDC Provider 등록 ─────────────────────────
resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

# ── IAM Role + Trust Policy ────────────────────
data "aws_iam_policy_document" "github_actions_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    # 🔒 특정 repo + main 브랜치에서만 Assume 허용
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:myorg/myrepo:ref:refs/heads/main"]
    }
  }
}

resource "aws_iam_role" "github_actions_deploy" {
  name               = "GitHubActionsDeployRole"
  assume_role_policy = data.aws_iam_policy_document.github_actions_trust.json
  max_session_duration = 3600  # 1시간
}

# ── Permission Policy (배포에 필요한 최소 권한) ──
resource "aws_iam_role_policy_attachment" "deploy_permissions" {
  role       = aws_iam_role.github_actions_deploy.name
  policy_arn = aws_iam_policy.terraform_deploy.arn
}
```

**GitHub Actions Workflow 예시:**

```yaml
# .github/workflows/deploy.yml
jobs:
  deploy:
    permissions:
      id-token: write   # OIDC 토큰 요청 권한
      contents: read

    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsDeployRole
          aws-region: ap-northeast-2

      - run: terraform apply -auto-approve
```

> 📌 **핵심**: IAM User의 Access Key가 전혀 필요 없다. GitHub의 OIDC Token → STS AssumeRole → 임시 자격증명 체인으로 **Zero Secret** 배포를 실현한다.

---

## 4️⃣ 시나리오 C: Cross-Account 접근

### 📋 시나리오 설명

Account A(Production)의 DynamoDB 데이터를 Account B(Analytics)에서 읽어야 한다.

### 🔄 결합 흐름

```
┌─────────────────────────────────────────────────────────────────┐
│              Cross-Account 접근 흐름                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Account B (Analytics)              Account A (Production)      │
│  ┌─────────────────────┐           ┌─────────────────────┐     │
│  │                     │           │                     │     │
│  │  👤 User "analyst"  │           │  🎭 Role            │     │
│  │  (Group: Analytics) │           │  "CrossAccountRead" │     │
│  │                     │           │                     │     │
│  │  📋 Policy:         │           │  📋 Trust Policy:   │     │
│  │  sts:AssumeRole     │  ── ① ──►│  Account B 허용     │     │
│  │  (Account A의 Role) │           │  + External ID 필수 │     │
│  │                     │           │                     │     │
│  └─────────────────────┘           │  📋 Permission:     │     │
│           │                        │  DynamoDB ReadOnly  │     │
│           │ ② AssumeRole           │                     │     │
│           │ (+ External ID)        └─────────┬───────────┘     │
│           ▼                                   │                │
│  ┌─────────────────────┐                     │                │
│  │  STS 임시 자격증명    │  ── ③ ──────────────┘                │
│  │  (1시간)             │                                      │
│  └─────────┬───────────┘                                      │
│            │ ④ DynamoDB 읽기                                   │
│            ▼                                                   │
│  ┌─────────────────────┐                                      │
│  │  DynamoDB Table     │                                      │
│  │  (Account A)        │                                      │
│  └─────────────────────┘                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 핵심 포인트

**양쪽 모두에 Policy가 필요하다:**
1. **Account B (Source)**: User/Role에 `sts:AssumeRole` 권한 + Account A의 Role ARN 지정
2. **Account A (Target)**: Role의 Trust Policy에 Account B를 Principal로 허용 + External ID Condition

---

## 5️⃣ 시나리오 D: 엔터프라이즈 멀티 계정 조직

### 📋 시나리오 설명

AWS Organizations로 dev/staging/prod 계정을 분리하고, 중앙 인증 + 계정별 권한 제한을 구현한다.

### 🔄 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│              엔터프라이즈 멀티 계정 아키텍처                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  AWS Organizations (Root)                                       │
│  │                                                              │
│  ├── 📋 SCP: DenyRegionOutsideSeoul                             │
│  │   (ap-northeast-2 외 리소스 생성 금지)                        │
│  │                                                              │
│  ├── OU: Security                                               │
│  │   ├── Account: Audit (CloudTrail, Config, GuardDuty)         │
│  │   └── Account: Log Archive (S3 로그 보관)                    │
│  │                                                              │
│  ├── OU: Identity                                               │
│  │   └── Account: Hub (IAM Identity Center)                     │
│  │       │                                                      │
│  │       │  SSO 로그인 → Role Assume                            │
│  │       │                                                      │
│  │       ├── Permission Set: "DeveloperAccess"                  │
│  │       │   → dev, staging 계정의 Developer Role 매핑          │
│  │       │                                                      │
│  │       ├── Permission Set: "AdminAccess"                      │
│  │       │   → 모든 계정의 Admin Role 매핑 (MFA 필수)            │
│  │       │                                                      │
│  │       └── Permission Set: "ReadOnlyAccess"                   │
│  │           → 모든 계정의 ReadOnly Role 매핑                    │
│  │                                                              │
│  ├── OU: Workloads                                              │
│  │   ├── OU: Development                                        │
│  │   │   ├── 📋 SCP: AllowAllExceptBilling                      │
│  │   │   └── Account: Dev                                       │
│  │   │       ├── 🎭 Role: DeveloperRole (broad 권한)            │
│  │   │       └── 🎭 Role: CI/CDRole (OIDC Federation)           │
│  │   │                                                          │
│  │   ├── OU: Staging                                             │
│  │   │   ├── 📋 SCP: DenyDestructiveActions                     │
│  │   │   └── Account: Staging                                   │
│  │   │                                                          │
│  │   └── OU: Production                                          │
│  │       ├── 📋 SCP: StrictLeastPrivilege                        │
│  │       ├── 📋 SCP: DenyIAMUserCreation                        │
│  │       └── Account: Production                                │
│  │           ├── 🎭 Role: AppRole (EC2/ECS 서비스용)             │
│  │           ├── 🎭 Role: DBAdminRole (MFA + IP 제한)            │
│  │           └── ⚠️ IAM User 생성 금지 (SCP 강제)                │
│  │                                                              │
│  └── OU: Sandbox                                                 │
│      ├── 📋 SCP: SpendingLimit ($100/월)                         │
│      └── Account: Sandbox (실험용)                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📊 환경별 IAM 구성 요소 비교

| 구성 요소 | Development | Staging | Production |
|-----------|------------|---------|------------|
| **IAM User** | ⚠️ 최소 | ❌ 금지 권장 | ❌ SCP로 금지 |
| **IAM Group** | 초기 셋업용 | - | - |
| **IAM Role** | 개발자 + CI/CD | CI/CD + ReadOnly | 서비스 + 긴급 접근 |
| **SCP** | 느슨한 가드레일 | 파괴적 Action 제한 | 엄격한 최소 권한 |
| **인증 방식** | Identity Center SSO | Identity Center SSO | Identity Center SSO + MFA |
| **Policy 관리** | AWS Managed 가능 | Customer Managed 권장 | Customer Managed 필수 |

---

## 6️⃣ 보안 체크리스트 (CIS Benchmark 기반)

[CIS AWS Foundations Benchmark](https://www.cisecurity.org/benchmark/amazon_web_services) 기반으로 IAM 관련 핵심 항목을 정리한다.

### ✅ 필수 체크리스트

| # | 항목 | 카테고리 | 확인 방법 |
|---|------|---------|----------|
| 1 | Root User에 MFA 활성화 | 인증 | `aws iam get-account-summary` → `AccountMFAEnabled` |
| 2 | Root User Access Key 없음 | 인증 | IAM Credential Report → root 행의 access_key_active |
| 3 | 모든 IAM User에 MFA 활성화 | 인증 | `aws iam generate-credential-report` |
| 4 | 90일 이상 미사용 자격증명 없음 | 자격증명 | Credential Report → password_last_used, access_key_last_used |
| 5 | Access Key 90일 이내 교체 | 자격증명 | Credential Report → access_key_last_rotated |
| 6 | `"*"` 와일드카드 Policy 없음 | 권한 | IAM Access Analyzer 실행 |
| 7 | IAM User에 직접 Policy 연결 없음 | 권한 | `aws iam list-user-policies` + `list-attached-user-policies` |
| 8 | CloudTrail 모든 리전 활성화 | 감사 | `aws cloudtrail describe-trails` |
| 9 | IAM Password Policy 강도 설정 | 인증 | `aws iam get-account-password-policy` |
| 10 | Support Role 생성됨 | 운영 | `aws iam list-roles` → `AWSSupportAccess` 확인 |

### 🚫 Anti-Pattern 체크리스트

| # | Anti-Pattern | 위험도 | 올바른 대안 |
|---|-------------|--------|------------|
| 1 | Root User로 일상 작업 | 🔴 Critical | IAM Identity Center + Admin Role |
| 2 | Access Key 코드 하드코딩 | 🔴 Critical | IAM Role (Instance Profile, OIDC) |
| 3 | `AdministratorAccess` 광범위 부여 | 🔴 Critical | 직무별 최소 권한 Policy |
| 4 | 퇴사자 IAM User 미삭제 | 🟠 High | 오프보딩 자동화 (CloudTrail + Lambda) |
| 5 | MFA 미적용 | 🟠 High | 모든 User/Root에 MFA 필수 |
| 6 | 콘솔에서 수동 IAM 관리 | 🟡 Medium | Terraform/CloudFormation IaC |
| 7 | 단일 계정에 모든 환경 | 🟡 Medium | Organizations + 계정 분리 |
| 8 | Policy 리뷰 미실시 | 🟡 Medium | 분기별 Access Advisor + Credential Report |

---

## 7️⃣ AWS Managed Policies for Job Functions

AWS는 일반적인 직무에 맞춰 사전 정의된 Managed Policy를 제공한다. 초기 설정에 유용하지만, **프로덕션에서는 Customer Managed Policy로 세분화**해야 한다.

| 직무 | Policy 이름 | 주요 권한 | 사용 시기 |
|------|------------|----------|----------|
| 관리자 | `AdministratorAccess` | 모든 서비스 전체 접근 | ⚠️ 최소 인원에만, MFA 필수 |
| 개발자 | `PowerUserAccess` | IAM/Organizations 제외 전체 | 초기 개발 단계 |
| 읽기 전용 | `ReadOnlyAccess` | 모든 서비스 읽기 | 감사인, 신규 입사자 초기 |
| DBA | `DatabaseAdministrator` | RDS, DynamoDB, Redshift | DB 전담 팀 |
| 네트워크 | `NetworkAdministrator` | VPC, ELB, CloudFront, Route53 | 네트워크 팀 |
| 보안 감사 | `SecurityAudit` | 보안 서비스 읽기 + CloudTrail | 보안 팀, 외부 감사 |

> 📌 **마이그레이션 경로**: AWS Managed Policy로 시작 → IAM Access Advisor로 실제 사용 권한 파악 → Customer Managed Policy로 세분화 ([AWS Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html))

---

## 8️⃣ 결론: 성숙도별 IAM 전략

```
┌─────────────────────────────────────────────────────────────────┐
│                  IAM 성숙도 모델                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Level 1: 시작 (1-5명)                                          │
│  ├─ Root 잠금 + Admin IAM User                                  │
│  ├─ Developers + ReadOnly Group (2개)                           │
│  ├─ AWS Managed Policy 사용                                     │
│  └─ MFA 필수                                                    │
│                                                                 │
│  Level 2: 성장 (5-30명)                                         │
│  ├─ IAM Identity Center(SSO) 도입                               │
│  ├─ 직무별 Group 세분화 (5-10개)                                 │
│  ├─ Customer Managed Policy 전환                                │
│  ├─ Terraform으로 IAM 코드 관리                                  │
│  └─ CI/CD에 OIDC Role 적용                                      │
│                                                                 │
│  Level 3: 확장 (30-100명)                                       │
│  ├─ AWS Organizations + 계정 분리                               │
│  ├─ SCP로 환경별 가드레일                                        │
│  ├─ Cross-Account Role 체계화                                   │
│  ├─ IAM Access Analyzer 상시 운영                               │
│  └─ Permissions Boundary로 위임 제한                             │
│                                                                 │
│  Level 4: 엔터프라이즈 (100명+)                                  │
│  ├─ ABAC (태그 기반 동적 권한)                                    │
│  ├─ IAM User 전면 폐지 → Identity Center + Role only            │
│  ├─ 자동화된 정책 리뷰 파이프라인                                 │
│  ├─ CIS Benchmark 자동 준수 검증                                │
│  └─ Zero Trust 아키텍처 완성                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📎 Sources

1. [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) — 공식 문서
2. [AWS Managed Policies for Job Functions](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_job-functions.html) — 공식 문서
3. [SCP Best Practices - AWS Security Blog](https://aws.amazon.com/blogs/security/how-to-use-service-control-policies-to-set-permission-guardrails-across-accounts-in-your-aws-organization/) — 공식 블로그
4. [CIS AWS Foundations Benchmark](https://www.cisecurity.org/benchmark/amazon_web_services) — 보안 표준
5. [GitHub Actions OIDC + Terraform](https://dev.to/camillehe1992/deploy-terraform-resources-to-aws-using-github-actions-via-oidc-3b9g) — 블로그
6. [Multi-Account Hub-Spoke IAM Strategy](https://medium.com/@senchuknazar6/architecting-aws-at-scale-a-deep-dive-into-multi-account-hub-spoke-and-iam-strategies-fbfb265a26e0) — 블로그
7. [Cross-Account IAM Architecture](https://iamdaybyday.com/platforms/aws-iam/cross-account/) — 블로그
8. [terraform-aws-modules/iam](https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest) — Terraform Registry

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 6 (일반 5 + SNS 1)
> - 수집 출처 수: 8
> - 출처 유형 분포: 공식 3, 블로그 4, 보안 표준 1
> - 확신도 분포: ✅ Confirmed 5, 🟡 Likely 3, 🔄 Synthesized 2
