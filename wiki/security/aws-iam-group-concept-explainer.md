---
tags: [security, aws, iam, iam-group, concept-explainer]
created: 2026-04-22
---

# 📖 AWS IAM Group — Concept Deep Dive

> 💡 **한줄 요약**: IAM Group은 **여러 IAM User를 묶어서 동일한 권한을 일괄 부여**하는 컬렉션으로, 대규모 사용자의 권한을 효율적으로 관리하기 위한 조직 단위이다.

---

## 1️⃣ 무엇인가? (What is it?)

**IAM Group(IAM 사용자 그룹)**은 IAM User들의 집합이다. Group에 Policy를 연결하면 그 Group에 속한 **모든 User가 해당 권한을 자동으로 상속**받는다.

**현실 세계 비유 (12살도 이해할 수 있는 설명):**

학교에서 학생마다 일일이 "도서관 출입 가능", "컴퓨터실 출입 가능"을 써주는 건 너무 번거롭다. 그래서 **반(Class)**을 만든다. "3학년 1반은 도서관 출입 가능"이라고 정하면, 1반에 속한 학생은 **자동으로** 도서관에 갈 수 있다. 새 학생이 전학 오면 1반에 넣기만 하면 되고, 졸업하면 1반에서 빼면 된다. IAM Group이 바로 이 **반**이다.

- **탄생 배경**: IAM User가 수십, 수백 명이 되면 개별 User에 Policy를 하나하나 붙이는 것이 불가능해진다. **직무(Job Function)** 단위로 묶어서 관리하기 위해 Group이 등장했다.
- **해결하는 문제**: 개별 User 권한 관리의 비효율성, 권한 일관성 유지, 인력 변동(입사/퇴사/부서 이동) 시 빠른 권한 전환

> 📌 **핵심 키워드**: `IAM User Group`, `Identity-based Policy`, `Permission Inheritance`, `Job Function`, `RBAC (Role-Based Access Control)`

---

## 2️⃣ 핵심 개념 (Core Concepts)

IAM Group의 핵심은 **"Policy는 Group에, User는 Group에"**라는 2단계 연결 구조이다.

```
┌─────────────────────────────────────────────────────────────┐
│                  IAM Group 핵심 구조                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────┐       │
│   │              📋 IAM Policy                       │       │
│   │   (S3ReadOnly, EC2FullAccess, ...)              │       │
│   └────────────────────┬────────────────────────────┘       │
│                        │ 연결 (Attach)                       │
│                        ▼                                    │
│   ┌─────────────────────────────────────────────────┐       │
│   │            👥 IAM Group ("Developers")            │       │
│   │                                                   │       │
│   │   ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐       │       │
│   │   │User A│  │User B│  │User C│  │User D│       │       │
│   │   └──────┘  └──────┘  └──────┘  └──────┘       │       │
│   │                                                   │       │
│   │   → 모든 User가 S3ReadOnly + EC2FullAccess 상속   │       │
│   └─────────────────────────────────────────────────┘       │
│                                                             │
│   ⚠️ 제약사항:                                               │
│   ├─ Group 안에 Group 넣기 ❌ (중첩 불가)                    │
│   ├─ Group을 Policy의 Principal로 지정 ❌                    │
│   └─ 기본 "전체 User" Group 없음 (수동 생성 필요)             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

| 구성 요소 | 역할 | 설명 |
|-----------|------|------|
| **Group Name** | 그룹 식별자 | 계정 내 고유한 이름 (예: `Developers`, `Admins`) |
| **Attached Policy** | 권한 정의 | Group에 연결된 Identity-based Policy (최대 10개) |
| **Member Users** | 권한 수혜자 | Group에 소속된 IAM User들 |
| **ARN** | 고유 리소스 식별자 | `arn:aws:iam::123456789012:group/Developers` |

### 📐 핵심 규칙

1. **User는 여러 Group에 소속 가능**: 한 User가 `Developers` + `S3Admins` 두 그룹에 동시 소속 → 두 그룹의 권한을 모두 받음
2. **Group 중첩 불가**: `Developers` 안에 `JuniorDevs` 하위 그룹을 넣을 수 없음 (flat 구조)
3. **Group은 Principal이 아님**: S3 Bucket Policy 등 리소스 기반 정책에서 Group을 `"Principal"`로 지정할 수 없음 — Group은 **권한 관리** 개념이지 **인증** 개념이 아니기 때문
4. **기본 Group 없음**: 모든 User를 자동으로 포함하는 기본 Group은 존재하지 않으며, 필요하면 수동으로 `AllUsers` Group을 만들어야 함

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

Group을 통한 권한 평가는 **User 직접 정책 + Group 상속 정책의 합집합(Union)**으로 결정된다.

```
┌─────────────────────────────────────────────────────────────────┐
│                    IAM Group 권한 평가 아키텍처                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  👤 IAM User "cjynim"                                           │
│    │                                                            │
│    ├─ 직접 연결 Policy: CloudWatchReadOnly                       │
│    │                                                            │
│    ├─ Group "Developers" 소속                                    │
│    │   └─ Group Policy: S3ReadOnly + CodeCommitFullAccess        │
│    │                                                            │
│    └─ Group "Deployers" 소속                                     │
│        └─ Group Policy: ECSFullAccess                            │
│                                                                 │
│    ════════════════════════════════════════                      │
│    최종 유효 권한 = 합집합 (Union)                                 │
│    ════════════════════════════════════════                      │
│                                                                 │
│    ┌─────────────┬───────────────────┬──────────────┐           │
│    │ CloudWatch  │ S3Read +          │ ECS          │           │
│    │ ReadOnly    │ CodeCommitFull    │ FullAccess   │           │
│    │ (직접)      │ (Developers)       │ (Deployers)  │           │
│    └─────────────┴───────────────────┴──────────────┘           │
│                                                                 │
│    ⚠️ 단, 명시적 Deny가 하나라도 있으면 해당 Action은 거부됨       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (Step by Step)

**시나리오: 새 개발자 온보딩**

1. **Step 1**: 관리자가 IAM User `new-dev`를 생성
2. **Step 2**: `new-dev`를 `Developers` Group에 추가
3. **Step 3**: `new-dev`는 즉시 `Developers` Group에 연결된 모든 Policy를 상속
4. **Step 4**: `new-dev`가 AWS 리소스에 접근 → IAM이 직접 Policy + Group Policy를 합산하여 평가
5. **Step 5**: 부서 이동 시 → `Developers`에서 제거, `DataEngineers`에 추가 → 권한 즉시 전환

**시나리오: CLI로 Group 관리**

```bash
# 💻 Group 생성
aws iam create-group --group-name Developers

# 📋 Policy 연결
aws iam attach-group-policy \
    --group-name Developers \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# 👤 User를 Group에 추가
aws iam add-user-to-group \
    --group-name Developers \
    --user-name cjynim

# 📊 Group의 User 목록 확인
aws iam get-group --group-name Developers

# 🗑️ User를 Group에서 제거
aws iam remove-user-from-group \
    --group-name Developers \
    --user-name cjynim
```

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| # | 유즈 케이스 | 설명 | 적합한 이유 |
|---|------------|------|------------|
| 1 | **직무별 권한 분리** | `Admins`, `Developers`, `Auditors`, `Finance` 그룹 생성 | 직무에 맞는 최소 권한을 일괄 적용 |
| 2 | **프로젝트별 리소스 접근** | `ProjectAlpha-Team` 그룹에 특정 S3 버킷, EC2 태그 기반 접근 부여 | 프로젝트 인력 변동 시 Group 멤버만 관리 |
| 3 | **보안 감사용 읽기 전용** | `SecurityAuditors` 그룹에 ReadOnly 정책 + CloudTrail 접근 | 감사인이 변경 없이 상태만 확인 가능 |
| 4 | **셀프 서비스 MFA 관리** | `ForceMFA` 그룹에 MFA 미설정 시 대부분 Action 거부 정책 연결 | 모든 User에게 MFA 강제 |

### ✅ 베스트 프랙티스

1. **🏢 직무 기반 Group 설계**: 팀/부서 이름이 아닌 **직무(Job Function)** 기반으로 Group을 만든다 (예: `DBAdmins`가 `InfraTeam`보다 낫다) ([AWS Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html))
2. **📋 Managed Policy 우선 사용**: Inline Policy 대신 **Customer Managed Policy**를 만들어 Group에 연결한다 — 재사용 가능하고 버전 관리됨
3. **🚫 직접 User Policy 최소화**: 개별 User에 Policy를 직접 붙이는 것을 피하고, 반드시 Group을 통해 권한을 부여한다
4. **🔍 정기적 멤버십 리뷰**: 분기마다 Group 멤버를 점검하여 퇴사자, 부서 이동자를 정리한다
5. **📐 기능별 Policy 분리**: 하나의 거대한 Policy 대신, 기능별로 분리된 Policy를 Group에 조합하여 연결한다 (예: `S3Access` + `CloudWatchAccess`)

### 🏢 실제 적용 사례

- **스타트업 (5-20명)**: `Admins` + `Developers` + `ReadOnly` 3개 Group으로 시작 → 성장에 따라 세분화
- **엔터프라이즈**: 직무별 30+ Group + AWS Organizations SCP와 조합하여 멀티 계정 환경에서 계층적 권한 제어

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ 장점 | **일괄 관리** | Policy 하나를 바꾸면 모든 멤버에 즉시 반영 |
| ✅ 장점 | **온/오프보딩 간소화** | 입사: Group에 추가, 퇴사: Group에서 제거 |
| ✅ 장점 | **일관성 보장** | 같은 직무의 User가 항상 동일한 권한을 가짐 |
| ✅ 장점 | **감사 용이** | "이 Group에는 이 Policy" — 누가 무슨 권한인지 한눈에 파악 |
| ❌ 단점 | **중첩 불가** | 계층적 조직 구조(팀 → 부서 → 본부)를 표현 불가 |
| ❌ 단점 | **Principal로 사용 불가** | S3 Bucket Policy 등에서 Group을 직접 지정 불가 |
| ❌ 단점 | **Policy 10개 제한** | Group당 최대 10개 Policy만 연결 가능 |
| ❌ 단점 | **IAM User 전용** | IAM Identity Center User나 Federated User에는 적용 불가 |

### ⚖️ Trade-off 분석

```
일괄 관리 편의성  ◄──────── Trade-off ────────►  세밀한 개별 제어 어려움
Flat 구조 단순성  ◄──────── Trade-off ────────►  계층적 조직 표현 불가
IAM User 전용     ◄──────── Trade-off ────────►  Federation 환경 미지원
```

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 비교 매트릭스: 권한 부여 방법별 비교

| 비교 기준 | IAM Group | IAM Role | User 직접 Policy | IAM Identity Center 그룹 |
|-----------|-----------|----------|-----------------|------------------------|
| **대상** | IAM User 집합 | 임시 자격증명 엔터티 | 개별 IAM User | Identity Center User 집합 |
| **자격증명** | 없음 (User의 것 사용) | STS 임시 토큰 | User 장기 자격증명 | SSO 임시 토큰 |
| **Principal 사용** | ❌ 불가 | ✅ 가능 | ✅ 가능 | ✅ 가능 |
| **중첩** | ❌ 불가 | N/A | N/A | ✅ 가능 |
| **관리 범위** | 단일 계정 | 단일 계정 + cross-account | 단일 계정 | 멀티 계정 |
| **적합한 경우** | IAM User 일괄 권한 | 서비스/애플리케이션 접근 | 예외적 개별 설정 | SSO 기반 조직 |

### 🔍 핵심 차이 요약

```
IAM Group                         IAM Role
──────────────────────    vs    ──────────────────────
User 집합 (컬렉션)                임시 신원 (Identity)
자격증명 없음                      STS 임시 자격증명
Policy 상속 전달                   AssumeRole로 전환
사람 권한 관리용                   서비스/cross-account용
Principal 아님                     Principal임
```

### 🤔 언제 무엇을 선택?

- **IAM Group을 선택하세요** → IAM User가 여러 명이고, 같은 직무의 사람들에게 동일한 권한을 부여할 때
- **IAM Role을 선택하세요** → EC2, Lambda 등 AWS 서비스가 다른 서비스에 접근할 때, 또는 cross-account 접근이 필요할 때
- **User 직접 Policy를 선택하세요** → 한 명의 User에게만 예외적으로 부여해야 하는 특수 권한이 있을 때 (최소화 권장)

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|------|-----------|------------|
| 1 | "Frankenstein Group" 방치 | 오래된 Group에 권한이 누적되어 아무도 건드리지 못하는 괴물 Policy가 됨 | 분기별 Group Policy 리뷰 + IAM Access Analyzer |
| 2 | 팀 이름 = Group 이름 | 조직 개편 시 Group 의미가 불명확해짐 | 직무 기반 네이밍 (`DBAdmins`, `Deployers`) |
| 3 | 모든 개발자에 `AdministratorAccess` | 한 명이 뚫리면 전체 계정 장악 | 직무별 최소 권한 Group 분리 |
| 4 | Group에 User 추가만 하고 제거 안 함 | 퇴사자/부서 이동자가 이전 권한 유지 | 오프보딩 체크리스트에 Group 제거 포함 |
| 5 | Group을 Resource Policy의 Principal로 사용 시도 | 동작하지 않아 혼란 발생 | 개별 User ARN 또는 IAM Role 사용 |

### 🚫 Anti-Patterns

1. **1인 1Group 안티패턴**: User마다 전용 Group을 만들면 Group의 의미가 없어지고 관리 복잡도만 증가한다. 직무 기반으로 공유 Group을 설계해야 한다 ([Cloud Security In Practice](https://cloudsecurityinpractice.com/en/2026/02/01/common-aws-iam-mistakes-in-enterprises/))
2. **Sandbox Policy를 Production Group에 복사**: 개발 환경의 넓은 권한을 프로덕션 Group에 그대로 적용하면 민감한 리소스에 대한 불필요한 접근이 열린다 ([StackProof](https://stackproof.dev/play-books/aws-iam-anti-patterns-and-how-to-fix-them/))
3. **Group 없이 개별 User에 Policy 직접 연결**: 규모가 커지면 "이 User에 왜 이 권한이 있는지" 파악이 불가능해진다. 반드시 Group을 통해 권한을 부여한다

### 🔒 보안/성능 고려사항

- **보안**: Group에 연결한 Policy의 `Resource`를 `"*"` 대신 **구체적 ARN**으로 한정해야 한다
- **보안**: `aws iam get-account-authorization-details` 명령으로 전체 Group-Policy 매핑을 주기적으로 감사
- **운영**: Group당 Policy 최대 10개 제한에 주의 — 초과 시 여러 Statement를 하나의 Custom Policy로 합치거나 Group을 분리

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|------|------|----------|
| 📖 공식 문서 | IAM User Groups | [AWS IAM User Groups Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_groups.html) |
| 📖 공식 문서 | IAM Best Practices | [Security Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) |
| 📘 블로그 | IAM Users vs Groups vs Roles | [LearnAWS Comparison](https://www.learnaws.org/2022/09/27/aws-iam-roles-vs-groups/) |
| 📘 블로그 | IAM Groups Deep Dive | [DEV Community](https://dev.to/ntsezenelvis/aws-iam-groups-deep-dive-11b2) |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리 | 플랫폼 | 용도 |
|---------------|--------|------|
| **AWS CLI** | Cross-platform | `aws iam create-group`, `add-user-to-group` 등 Group 관리 |
| **Terraform** | IaC | `aws_iam_group`, `aws_iam_group_policy_attachment`, `aws_iam_group_membership` |
| **IAM Access Analyzer** | AWS Console | Group에 연결된 과도한 권한 탐지 |
| **AWS CloudFormation** | IaC | `AWS::IAM::Group` 리소스로 선언적 관리 |

### 🔮 트렌드 & 전망

- **IAM Identity Center 그룹으로 전환**: 멀티 계정 환경에서 IAM Group 대신 **IAM Identity Center의 Group + Permission Set** 조합이 권장되는 추세
- **Attribute-Based Access Control (ABAC)**: 태그 기반 접근 제어가 확산되면서, 정적 Group 멤버십보다 **동적 속성 기반** 권한 부여가 보완적으로 사용
- **IaC 필수화**: Group/Policy 관리를 콘솔 수동 작업이 아닌 Terraform/CloudFormation으로 코드화하는 것이 표준

### 💬 커뮤니티 인사이트

- "Group은 사람을 위한 것, Role은 기계를 위한 것"이라는 공식이 실무에서 자주 인용됨
- AWS re:Post에서 "Group 중첩 불가"로 인한 불편 호소가 빈번하지만, AWS의 공식 입장은 **flat 구조 유지** — 복잡한 조직 구조는 IAM Identity Center + AWS Organizations로 해결 권장

---

## 📎 Sources

1. [IAM User Groups - AWS Official Docs](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_groups.html) — 공식 문서
2. [Security Best Practices in IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) — 공식 문서
3. [IAM Users vs Groups vs Roles - LearnAWS](https://www.learnaws.org/2022/09/27/aws-iam-roles-vs-groups/) — 블로그
4. [AWS IAM Anti-Patterns - StackProof](https://stackproof.dev/play-books/aws-iam-anti-patterns-and-how-to-fix-them/) — 블로그
5. [Common AWS IAM Mistakes - Cloud Security In Practice](https://cloudsecurityinpractice.com/en/2026/02/01/common-aws-iam-mistakes-in-enterprises/) — 블로그
6. [AWS IAM Groups Deep Dive - DEV Community](https://dev.to/ntsezenelvis/aws-iam-groups-deep-dive-11b2) — 블로그
7. [AWS Security Basics: IAM Users vs Roles vs Groups - AppSecEngineer](https://www.appsecengineer.com/blog/aws-security-basics-iam-users-vs-roles-vs-groups) — 블로그

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 5
> - 수집 출처 수: 7
> - 출처 유형: 공식 2, 블로그 5, 커뮤니티 1, SNS 0
> - 관련 문서: [[aws-iam-concept-explainer]], [[aws-iam-user-concept-explainer]], [[aws-iam-policy-concept-explainer]], [[aws-iam-role-concept-explainer]]
