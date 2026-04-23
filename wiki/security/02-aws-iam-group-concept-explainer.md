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

> 💡 **Principal과 Effect의 역할 구분**
>
> Principal이 "허용/거부를 결정한다"고 오해할 수 있지만, 실제로는 **역할이 분리**되어 있다:
>
> ```
> 📋 Policy (출입 규칙표)
> ├─ Principal  → 누가?       (예: "3학년 학생들")
> ├─ Action     → 뭘 하는?    (예: "도서관 출입")
> ├─ Resource   → 어디에?     (예: "2층 도서관")
> ├─ Effect     → 허용? 거부? (예: "Allow")    ← 이것이 허용/거부를 결정
> └─ Condition  → 어떤 조건?  (예: "평일 9시~6시")
> ```
>
> - **Principal**은 "누구에게 이 규칙이 적용되는가"를 지정
> - **Effect**가 실제 "할 수 있다(Allow) / 없다(Deny)"를 결정
> - Group이 "Principal이 아니다" = Resource-based Policy에서 Group ARN을 `"Principal"` 자리에 **지정할 수 없다**는 의미
>
> | Policy 유형 | Principal 필요? | 이유 |
> |-------------|---------------|------|
> | **Identity-based** (User/Group/Role에 붙이는 것) | ❌ 불필요 | 이미 "누구에게" 붙였는지가 명확 |
> | **Resource-based** (S3 버킷 등에 붙이는 것) | ✅ 필수 | 리소스 입장에서 "누가 접근 가능한지" 명시해야 함 |
>
> 📎 상세: [[03-aws-iam-policy-concept-explainer]]

> 💡 **`AllUsers`는 AWS 고유명사가 아니다**
>
> 문서에서 언급한 `AllUsers`는 "모든 User를 포함하는 Group이 필요하면 직접 만들어야 하고, 그때 이런 이름을 지을 수 있다" 정도의 **예시**다. 이름은 `Everyone`, `AllStaff`, `Company` 등 무엇이든 상관없다. Google Workspace의 `allUsers` 같은 시스템 그룹과 달리, **AWS IAM에는 그런 기본 제공 그룹 개념이 없다.**

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

> 💡 **"합집합"과 "명시적 Deny"의 관계를 정확히 이해하기**
>
> 권한 **범위**는 합집합이지만, **명시적 Deny는 항상 이긴다.** 이것은 IAM 평가의 황금 규칙이다:
>
> ```
> 🏆 우선순위: 명시적 Deny > 명시적 Allow > 암묵적 Deny
> ```
>
> 예를 들어, Developers Group에서 S3ReadOnly를 **Allow**했어도, Deployers Group에서 S3 접근을 **Deny**했으면:
>
> ```
> 👤 User "cjynim"이 s3:GetObject 요청
>     │
>     ├─ Group "Developers" → Policy: S3ReadOnly (Allow) ✅
>     └─ Group "Deployers"  → Policy: S3 Deny    (Deny)  ❌
>     
>     ▼ IAM 평가 엔진
>     ① 명시적 Deny 있나? → ✅ Deployers의 Deny 발견
>     ② 즉시 거부! (Developers의 Allow는 무시됨)
>     
>     결과: ❌ S3 접근 거부
> ```
>
> 12살 비유: 엄마(Developers)가 "아이스크림 먹어도 돼"라고 했는데, 아빠(Deployers)가 "아이스크림 절대 안 돼"라고 했으면? → **"안 돼"가 이긴다.** 한 명이라도 "안 돼"라고 하면 끝이다.
>
> 📎 전체 평가 흐름: [[03-aws-iam-policy-concept-explainer]] — `명시적 Deny → SCP/RCP → Allow → Permissions Boundary` 순서로 평가

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

> 💡 **AWS Organizations SCP (Service Control Policy)란?**
>
> SCP는 AWS Organizations에서 하위 계정들의 **최대 권한 상한선(ceiling)**을 설정하는 정책이다. 학교(Organization)에서 "교내에서는 스마트폰 사용 금지"라는 **교칙**을 만들면, 각 반(AWS 계정)의 선생님(IAM Admin)이 아무리 "폰 써도 돼"라고 해도 **교칙이 금지하면 못 쓴다.** SCP는 이 교칙이다.
>
> ```
> ┌──────────────────────────────────────────────┐
> │           AWS Organizations (학교)             │
> │                                              │
> │   📜 SCP: "서울 리전 외 EC2 생성 금지"        │
> │                                              │
> │   ┌────────────┐   ┌────────────┐            │
> │   │  계정 A     │   │  계정 B     │            │
> │   │ (개발팀)    │   │ (인프라팀)   │            │
> │   │             │   │             │            │
> │   │ IAM Policy: │   │ IAM Policy: │            │
> │   │ EC2Full     │   │ EC2Full     │            │
> │   │ Access      │   │ Access      │            │
> │   │             │   │             │            │
> │   │ 도쿄 리전?  │   │ 도쿄 리전?  │            │
> │   │ → ❌ SCP에  │   │ → ❌ SCP에  │            │
> │   │   의해 거부! │   │   의해 거부! │            │
> │   └────────────┘   └────────────┘            │
> └──────────────────────────────────────────────┘
> ```
>
> | 항목 | 설명 |
> |------|------|
> | **적용 범위** | Organization 전체 또는 특정 OU (Organizational Unit) |
> | **역할** | 하위 계정이 사용할 수 있는 **최대 권한의 상한선** |
> | **주의** | SCP는 권한을 **부여하지 않는다**. 권한의 천장(ceiling)만 설정 |
> | **Management Account** | SCP가 **적용되지 않는다** — 따라서 Management Account에서 워크로드를 실행하지 않는 것이 권장됨 |
>
> 📎 Policy 평가 흐름에서의 위치: `명시적 Deny 체크 → **SCP/RCP 체크** → Allow 체크 → Permissions Boundary 체크`

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
| ❌ 단점 | **Policy 10개 제한** | Group당 최대 10개 Managed Policy만 연결 가능 (**하드 리밋, 증가 요청 불가**) |
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

> 💡 **IAM Role은 "기계 전용"이 아니다**
>
> "Group은 사람을 위한 것, Role은 기계를 위한 것"이라는 공식이 실무에서 자주 인용되지만, 이는 **단순화된 설명**이다. Role은 **사람도 사용 가능**하며, 오히려 최신 권장 패턴에서는 사람도 Role을 쓴다:
>
> | Role 유형 | 누가 사용? | 예시 |
> |-----------|----------|------|
> | **Service Role** | AWS 서비스 | EC2가 S3에 접근, Lambda가 DynamoDB 읽기 |
> | **Service-Linked Role** | AWS 서비스 (자동 생성) | ECS 서비스 운영 |
> | **Cross-Account Role** | **다른 계정의 사람/서비스** | 파트너 회사 개발자가 내 S3 접근 |
> | **Web Identity Role** | **외부 사용자 (사람)** | Google 로그인한 모바일 앱 사용자 |
> | **SAML 2.0 Role** | **기업 직원 (사람)** | 회사 SSO로 로그인한 직원 |
>
> 5가지 유형 중 **3가지가 사람 대상**이다. AWS는 최근 IAM User 대신 **IAM Identity Center + Role** 조합을 권장하는 추세로, 사람도 Role을 쓰는 것이 **베스트 프랙티스**가 되고 있다.
>
> 📎 상세: [[04-aws-iam-role-concept-explainer]]

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|------|-----------|------------|
| 1 | "Frankenstein Group" 방치 | 오래된 Group에 권한이 누적되어 아무도 건드리지 못하는 괴물 Policy가 됨 | 분기별 Group Policy 리뷰 + IAM Access Analyzer |
| 2 | 팀 이름 = Group 이름 | 조직 개편 시 Group 의미가 불명확해짐 | 직무 기반 네이밍 (`DBAdmins`, `Deployers`) |
| 3 | 모든 개발자에 `AdministratorAccess` | 한 명이 뚫리면 전체 계정 장악 | 직무별 최소 권한 Group 분리 |
| 4 | Group에 User 추가만 하고 제거 안 함 | 퇴사자/부서 이동자가 이전 권한 유지 | 오프보딩 체크리스트에 Group 제거 포함 |
| 5 | Group을 Resource Policy의 Principal로 사용 시도 | **`MalformedPolicyDocument: Invalid principal in policy` 에러 (HTTP 400)로 Policy 저장 자체가 실패** | 개별 User ARN 또는 IAM Role 사용 |

> 💡 **실수 #5 상세: Group을 Principal로 사용하면 어떻게 되나?**
>
> "동작만 안 하는 것"이 아니라, **Policy 저장 자체가 에러로 거부**된다:
>
> ```json
> // ❌ 이렇게 쓰면 API 에러 발생 (Group ARN)
> {
>   "Principal": {
>     "AWS": "arn:aws:iam::123456789012:group/Developers"
>   }
> }
> // → "MalformedPolicyDocument: Invalid principal in policy"
>
> // ✅ User ARN → 동작함
> { "Principal": { "AWS": "arn:aws:iam::123456789012:user/cjynim" } }
>
> // ✅ Role ARN → 동작함
> { "Principal": { "AWS": "arn:aws:iam::123456789012:role/DevRole" } }
> ```
>
> **왜 User/Role은 되고 Group은 안 되나?**
>
> | 엔터티 | Principal 가능? | 이유 |
> |--------|---------------|------|
> | **IAM User** | ✅ | **인증 가능한 주체** (로그인 가능, Access Key 있음) |
> | **IAM Role** | ✅ | **인증 가능한 주체** (AssumeRole로 임시 자격증명 발급) |
> | **IAM Group** | ❌ | **관리 편의를 위한 컬렉션**일 뿐, 자격증명이 없어 인증 불가 |
>
> Principal = "인증할 수 있는 주체"인데, Group은 자격증명이 없고 인증할 방법이 없다. Group은 Policy를 묶어서 전달하는 **바구니**일 뿐이다.
>
> **Workaround**: Group 멤버 전체에 접근 권한을 주고 싶다면 → ① Role을 만들어 Group 멤버가 AssumeRole하도록 구성하거나, ② `aws:PrincipalTag` 조건으로 공통 태그를 활용
>
> 📎 출처: [AWS IAM Principal element 공식 문서](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html)

### 🚫 Anti-Patterns

1. **1인 1Group 안티패턴**: User마다 전용 Group을 만들면 Group의 의미가 없어지고 관리 복잡도만 증가한다. 직무 기반으로 공유 Group을 설계해야 한다 ([Cloud Security In Practice](https://cloudsecurityinpractice.com/en/2026/02/01/common-aws-iam-mistakes-in-enterprises/))
2. **Sandbox Policy를 Production Group에 복사**: 개발 환경의 넓은 권한을 프로덕션 Group에 그대로 적용하면 민감한 리소스에 대한 불필요한 접근이 열린다 ([StackProof](https://stackproof.dev/play-books/aws-iam-anti-patterns-and-how-to-fix-them/))
3. **Group 없이 개별 User에 Policy 직접 연결**: 규모가 커지면 "이 User에 왜 이 권한이 있는지" 파악이 불가능해진다. 반드시 Group을 통해 권한을 부여한다

### 🔒 보안/성능 고려사항

- **보안**: Group에 연결한 Policy의 `Resource`를 `"*"` 대신 **구체적 ARN**으로 한정해야 한다
- **보안**: `aws iam get-account-authorization-details` 명령으로 전체 Group-Policy 매핑을 주기적으로 감사
- **운영**: Group당 Policy 최대 10개 제한에 주의 — 초과 시 여러 Statement를 하나의 Custom Policy로 합치거나 Group을 분리

> 💡 **Policy 10개 제한 해결 방법 상세**
>
> 하나의 Group에 Managed Policy를 **최대 10개**까지만 연결할 수 있다 (하드 리밋, User/Role은 20으로 증가 요청 가능하지만 **Group은 불가**).
>
> **문제 상황**: Developers Group에 11개 Policy가 필요한데 10개까지만 가능
>
> **방법 1 — 여러 Statement를 하나의 Custom Policy로 합치기** 🔧
>
> ```
> ❌ Before: 별도 Policy 3개 사용 (슬롯 3개 소모)
>   - S3ReadOnly + DynamoDBReadOnly + CloudWatchReadOnly
>
> ✅ After: 하나의 Custom Policy로 합침 (슬롯 1개만 사용)
>   - MyDevReadOnlyAccess
>     └─ Statement 1: S3 Read
>     └─ Statement 2: DynamoDB Read
>     └─ Statement 3: CloudWatch Read
> ```
>
> **방법 2 — Group을 분리하기** 📂
>
> ```
> ❌ Before: "Developers" 하나에 10개 초과 위험
>
> ✅ After: 직무별로 Group 분리
>   - "Dev-Compute"  → EC2, Lambda, ECS 관련 Policy
>   - "Dev-Storage"  → S3, DynamoDB 관련 Policy
>   - "Dev-Monitor"  → CloudWatch, X-Ray 관련 Policy
>
> User는 필요한 Group에 복수 소속
> ```
>
> 📎 출처: [IAM and AWS STS quotas](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-quotas.html)

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

- "Group은 사람을 위한 것, Role은 기계를 위한 것"이라는 공식이 실무에서 자주 인용됨 (단, Role은 사람도 사용 가능 — 6️⃣ 참고)
- AWS re:Post에서 "Group 중첩 불가"로 인한 불편 호소가 빈번하지만, AWS의 공식 입장은 **flat 구조 유지** — 복잡한 조직 구조는 IAM Identity Center + AWS Organizations로 해결 권장

> 💡 **Group 중첩 불가 — 왜 불편하고, 왜 AWS는 flat을 유지하나?**
>
> **중첩 요구 측의 논리** — 학교에 "3학년 1반", "3학년 2반"이 있고 두 반 모두 "3학년 공통 규칙"(급식실, 체육관)이 필요할 때:
>
> ```
> ❌ 현재 (flat, 중첩 불가):
>   Group "Grade3-Class1" → Policy: 급식실 + 체육관 + 컴퓨터실
>   Group "Grade3-Class2" → Policy: 급식실 + 체육관 + 도서관
>                                    ^^^^^^^^^^^^^^^^
>                                    중복! 양쪽에 각각 붙여야 함
>
> ✅ 중첩 가능하다면:
>   Group "Grade3-Common" → Policy: 급식실 + 체육관
>     ├── Group "Grade3-Class1" → Policy: 컴퓨터실 (추가분만)
>     └── Group "Grade3-Class2" → Policy: 도서관   (추가분만)
> ```
>
> | 관점 | 중첩 허용 (찬성) | Flat 유지 (반대) |
> |------|----------------|----------------|
> | **Policy 중복** | ✅ 상위 Group에 공통 Policy → 중복 제거 | ❌ 같은 Policy를 여러 Group에 각각 연결 |
> | **복잡도** | ❌ 계층이 깊어지면 최종 권한 추적 어려움 | ✅ 단순하고 예측 가능 |
> | **10개 제한** | ✅ 공통 Policy를 상위로 올리면 하위 여유 확보 | ❌ 10개 제한에 더 빨리 도달 |
> | **조직 매핑** | ✅ 본부→부서→팀 계층을 자연스럽게 표현 | ❌ 계층 조직을 flat으로 펴야 함 |
>
> **결론**: 중첩의 핵심 이득은 **공통 Policy 중복 제거**, **조직 구조 매핑**, **10개 제한 완화**이다. 하지만 AWS는 권한 추적의 단순성을 위해 **의도적으로 flat을 유지**한다 — 중첩이 깊어지면 "이 User의 최종 유효 권한이 정확히 뭐지?"를 계산하기 매우 어려워지고 보안 감사가 난해해진다. flat + multi-group은 **1단계 깊이**라서 추적이 비교적 쉽다.
>
> ```
> Flat (현재):          vs    중첩 (가상):
> User → Group A              User → Group A → Group X → Group Z
> User → Group B                                  └→ Group Y
> (최대 1단계)                 (N단계 깊이, 추적 어려움)
> ```

---

## 📎 Sources

1. [IAM User Groups - AWS Official Docs](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_groups.html) — 공식 문서
2. [Security Best Practices in IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) — 공식 문서
3. [IAM Users vs Groups vs Roles - LearnAWS](https://www.learnaws.org/2022/09/27/aws-iam-roles-vs-groups/) — 블로그
4. [AWS IAM Anti-Patterns - StackProof](https://stackproof.dev/play-books/aws-iam-anti-patterns-and-how-to-fix-them/) — 블로그
5. [Common AWS IAM Mistakes - Cloud Security In Practice](https://cloudsecurityinpractice.com/en/2026/02/01/common-aws-iam-mistakes-in-enterprises/) — 블로그
6. [AWS IAM Groups Deep Dive - DEV Community](https://dev.to/ntsezenelvis/aws-iam-groups-deep-dive-11b2) — 블로그
7. [AWS Security Basics: IAM Users vs Roles vs Groups - AppSecEngineer](https://www.appsecengineer.com/blog/aws-security-basics-iam-users-vs-roles-vs-groups) — 블로그
8. [IAM Principal element - AWS Official Docs](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html) — 공식 문서
9. [IAM and AWS STS quotas - AWS Official Docs](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-quotas.html) — 공식 문서
10. [Service Control Policies (SCPs) - AWS Official Docs](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html) — 공식 문서

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 5
> - 수집 출처 수: 10
> - 출처 유형: 공식 5, 블로그 5, 커뮤니티 1, SNS 0
> - 관련 문서: [[05-aws-iam-concept-explainer]], [[01-aws-iam-user-concept-explainer]], [[03-aws-iam-policy-concept-explainer]], [[04-aws-iam-role-concept-explainer]]
