---
tags: [security, aws, iam, iam-user, concept-explainer]
created: 2026-04-22
---

# 📖 AWS IAM User — Concept Deep Dive

> 💡 **한줄 요약**: IAM User는 AWS 계정 내에서 특정 사람이나 애플리케이션을 나타내는 **영구적 자격증명을 가진 신원(Identity)**으로, AWS 리소스에 대한 접근 권한을 부여받는 기본 단위이다.

---

## 1️⃣ 무엇인가? (What is it?)

**IAM User**는 AWS 계정 안에 생성하는 엔터티(Entity)로, **이름과 자격증명(Credentials)**을 가진다. 사람(Human) 또는 워크로드(Application)가 이 자격증명을 사용해 AWS에 요청을 보낸다.

**현실 세계 비유 (12살도 이해할 수 있는 설명):**

회사에 새로 입사하면 **사원증**을 발급받는다. 이 사원증에는 이름, 사번, 사진이 있고, 이걸로 건물에 들어가고(인증), 허가된 층만 갈 수 있다(인가). IAM User는 바로 이 **AWS 세계의 사원증**이다. 사원증 없이는 건물에 못 들어가고, 사원증이 있어도 허가된 곳만 갈 수 있다.

- **탄생 배경**: AWS 계정을 만들면 **Root User**(만능 관리자)가 생기는데, 이걸 일상적으로 쓰면 보안 위험이 너무 크다. 그래서 "필요한 권한만 가진 개별 사용자"를 만들 수 있도록 IAM User가 등장했다.
- **해결하는 문제**: Root User 남용 방지, 최소 권한 원칙(Least Privilege) 실현, 개별 사용자별 활동 추적(Audit)

> 📌 **핵심 키워드**: `IAM User`, `Credentials`, `Access Key`, `Console Password`, `MFA`, `ARN`, `Least Privilege`

---

## 2️⃣ 핵심 개념 (Core Concepts)

IAM User를 이해하려면 **식별자**, **자격증명**, **권한** 세 가지를 알아야 한다.

```
┌─────────────────────────────────────────────────────────────┐
│                    IAM User 핵심 구성 요소                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────────────────────────────────────┐              │
│   │           🪪 IAM User                     │              │
│   │                                          │              │
│   │  식별자 (Identity)                        │              │
│   │  ├─ Friendly Name: "cjynim"              │              │
│   │  ├─ ARN: arn:aws:iam::123456:user/cjynim │              │
│   │  └─ Unique ID: AIDA...  (내부용)          │              │
│   │                                          │              │
│   │  자격증명 (Credentials)                   │              │
│   │  ├─ 🔑 Console Password (콘솔 로그인)     │              │
│   │  ├─ 🗝️  Access Key (프로그래밍 접근)       │              │
│   │  ├─ 📱 MFA Device (2차 인증)              │              │
│   │  └─ 🔐 SSH Key (CodeCommit용)            │              │
│   │                                          │              │
│   │  권한 (Permissions)                       │              │
│   │  ├─ 직접 연결된 Policy                    │              │
│   │  ├─ Group에서 상속받은 Policy              │              │
│   │  └─ Permissions Boundary (최대 권한 제한)  │              │
│   └──────────────────────────────────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

| 구성 요소 | 역할 | 설명 |
|-----------|------|------|
| **Friendly Name** | 사람이 읽는 이름 | 콘솔에서 보이는 이름 (예: `dev-cjynim`) |
| **ARN** | 리소스 고유 식별자 | `arn:aws:iam::123456789012:user/dev-cjynim` |
| **Console Password** | 콘솔 로그인 | AWS Management Console 접근용 비밀번호 |
| **Access Key** | 프로그래밍 접근 | Access Key ID + Secret Access Key 쌍 |
| **MFA** | 2단계 인증 | TOTP 앱, 보안 키, 패스키 등 |
| **Permissions Boundary** | 권한 상한선 | User에게 부여 가능한 최대 권한을 제한 |

### 🔑 Root User vs IAM User

| 비교 기준 | Root User | IAM User |
|-----------|-----------|----------|
| **생성 시점** | AWS 계정 생성 시 자동 | 관리자가 수동 생성 |
| **권한** | 모든 권한 (제한 불가) | 부여된 권한만 |
| **삭제 가능** | ❌ 불가 | ✅ 가능 |
| **수량** | 계정당 1개 | 계정당 최대 5,000개 |
| **일상 사용** | ⚠️ 비권장 | ✅ 권장 |
| **MFA** | 필수 권장 | 필수 권장 |

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

IAM User는 **두 가지 경로**로 AWS에 접근한다: 콘솔(사람)과 프로그래밍(애플리케이션).

```
┌─────────────────────────────────────────────────────────────────┐
│                    IAM User 인증 아키텍처                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  👤 사람 (Human)                  🤖 애플리케이션 (Workload)      │
│    │                                │                           │
│    │ ① ID + Password + MFA          │ ① Access Key ID           │
│    │                                │   + Secret Access Key     │
│    ▼                                ▼                           │
│  ┌──────────────┐          ┌──────────────────┐                │
│  │ AWS Console  │          │ AWS CLI / SDK    │                │
│  │ (웹 브라우저) │          │ (터미널 / 코드)   │                │
│  └──────┬───────┘          └────────┬─────────┘                │
│         │                           │                           │
│         └─────────┬─────────────────┘                           │
│                   ▼                                             │
│         ┌──────────────────┐                                    │
│         │   AWS IAM 서비스  │                                    │
│         │                  │                                    │
│         │  ② 자격증명 검증   │                                   │
│         │  ③ 권한 평가       │                                   │
│         │  ④ 허용/거부 결정  │                                   │
│         └────────┬─────────┘                                    │
│                  │                                              │
│           ┌──────┴──────┐                                       │
│           ▼             ▼                                       │
│     ✅ 허용          ❌ 거부                                     │
│    (리소스 접근)    (AccessDenied)                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (Step by Step)

**경로 A: 콘솔 접근 (사람)**

1. **Step 1**: 사용자가 AWS Console 로그인 페이지에 접속
2. **Step 2**: Account ID(또는 Alias) + IAM User Name + Password 입력
3. **Step 3**: MFA가 활성화되어 있으면 MFA 코드 입력
4. **Step 4**: IAM이 자격증명을 검증하고, 세션 토큰(임시 자격증명) 발급
5. **Step 5**: 사용자가 콘솔에서 작업 → 각 API 호출마다 권한 평가

**경로 B: 프로그래밍 접근 (워크로드)**

1. **Step 1**: 애플리케이션이 Access Key ID + Secret Access Key로 요청에 서명
2. **Step 2**: AWS가 서명을 검증하여 사용자 신원 확인
3. **Step 3**: 해당 User에 연결된 Policy를 평가하여 허용/거부 결정
4. **Step 4**: 허용되면 리소스에 접근, 거부되면 `AccessDenied` 에러 반환

```python
# 💻 Access Key를 사용한 프로그래밍 접근 예시 (boto3)
import boto3

# ⚠️ 하드코딩 금지! 환경변수 또는 AWS 설정 파일 사용
session = boto3.Session(
    aws_access_key_id='AKIAIOSFODNN7EXAMPLE',      # Access Key ID
    aws_secret_access_key='wJalrXUtnFEMI/K7MDENG',  # Secret Access Key
    region_name='ap-northeast-2'
)

s3 = session.client('s3')
buckets = s3.list_buckets()
```

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| # | 유즈 케이스 | 설명 | 적합한 이유 |
|---|------------|------|------------|
| 1 | **서드파티 도구 연동** | IAM Role을 지원하지 않는 외부 도구에 Access Key 제공 | Role 기반 접근이 불가능한 경우의 유일한 대안 |
| 2 | **CodeCommit SSH 접근** | Git 저장소 접근용 SSH Key 관리 | IAM User만 SSH Key 연결 가능 |
| 3 | **긴급 콘솔 접근** | IAM Identity Center 장애 시 백업 접근 경로 | Federation 불가 시 fallback |
| 4 | **소규모 팀 초기 설정** | AWS Organizations 미사용 환경에서 개별 사용자 관리 | 단일 계정에서 빠른 셋업 |

### ✅ 베스트 프랙티스

1. **🔒 MFA 필수 활성화**: 모든 IAM User에 MFA를 적용한다. 피싱 방지가 가능한 **패스키(Passkey)** 또는 **보안 키(FIDO2)**를 권장한다 ([AWS Security Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html))
2. **⏰ Access Key 주기적 교체**: 장기 자격증명을 사용해야 한다면 90일마다 교체하고, 사용하지 않는 키는 즉시 비활성화한다
3. **📐 최소 권한 원칙**: `AdministratorAccess` 같은 광범위 정책 대신 **필요한 Action만 허용하는 커스텀 Policy**를 연결한다
4. **🔄 IAM Identity Center 우선**: 사람(Human)의 AWS 접근은 IAM User 대신 **IAM Identity Center(SSO)**를 사용하여 임시 자격증명 기반으로 전환한다
5. **📊 자격증명 리포트 활용**: IAM Credential Report를 정기적으로 확인하여 미사용 자격증명을 정리한다

### 🏢 실제 적용 사례

- **스타트업 초기**: 팀원 3-5명일 때 IAM User로 시작 → 팀이 커지면 IAM Identity Center로 마이그레이션
- **CI/CD 파이프라인**: GitHub Actions OIDC Federation을 지원하지 않는 레거시 CI 서버에서 IAM User Access Key 사용 (점진적 Role 전환 권장)

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ 장점 | **설정이 간단** | 몇 분 안에 생성하고 바로 사용 가능 |
| ✅ 장점 | **개별 추적 가능** | CloudTrail로 사용자별 활동 이력 추적 |
| ✅ 장점 | **세밀한 권한 제어** | Policy를 직접 연결하거나 Group으로 관리 |
| ✅ 장점 | **외부 의존성 없음** | IdP(Identity Provider) 없이 독립적으로 운영 |
| ❌ 단점 | **장기 자격증명 위험** | Access Key는 교체하지 않으면 영구적으로 유효 |
| ❌ 단점 | **확장성 제한** | 계정당 5,000명 제한, 멀티 계정 환경에서 관리 복잡 |
| ❌ 단점 | **Key 유출 위험** | 코드/깃헙에 실수로 커밋하면 즉시 악용 가능 |
| ❌ 단점 | **수동 라이프사이클** | 퇴사자 Key 비활성화 등 수동 관리 필요 |

### ⚖️ Trade-off 분석

```
간편한 설정    ◄──────── Trade-off ────────►  장기 보안 위험
독립적 운영    ◄──────── Trade-off ────────►  확장성 제한
영구 자격증명  ◄──────── Trade-off ────────►  유출 시 피해 범위
개별 관리      ◄──────── Trade-off ────────►  대규모 운영 비효율
```

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 비교 매트릭스: IAM User vs IAM Identity Center User vs Federated User

| 비교 기준 | IAM User | IAM Identity Center User | Federated User |
|-----------|----------|-------------------------|----------------|
| **자격증명 유형** | 장기(영구) | 임시(세션 기반) | 임시(세션 기반) |
| **관리 범위** | 단일 계정 | 멀티 계정(Organizations) | 외부 IdP 연동 |
| **인증 방식** | ID/PW + MFA | SSO Portal | SAML 2.0 / OIDC |
| **Access Key** | ✅ 생성 가능 | ❌ 직접 생성 불가 | ❌ 직접 생성 불가 |
| **설정 복잡도** | ⭐ 낮음 | ⭐⭐ 중간 | ⭐⭐⭐ 높음 |
| **보안 수준** | ⚠️ 관리 필요 | ✅ 높음 | ✅ 높음 |
| **AWS 권장** | 워크로드 한정 | ✅ 사람 접근 권장 | ✅ 기업 환경 권장 |

### 🔍 핵심 차이 요약

```
IAM User                        IAM Identity Center User
──────────────────────    vs    ──────────────────────────
장기 자격증명 (Access Key)       임시 자격증명 (STS Token)
단일 AWS 계정 소속               멀티 계정 중앙 관리
수동 라이프사이클 관리            자동 세션 만료
코드에 Key 노출 위험              Key가 존재하지 않음
```

### 🤔 언제 무엇을 선택?

- **IAM User를 선택하세요** → IAM Role을 지원하지 않는 서드파티 도구, CodeCommit SSH 접근, IAM Identity Center 미사용 환경
- **IAM Identity Center를 선택하세요** → 사람(Human)의 AWS 접근, 멀티 계정 환경, 기업 SSO 연동
- **Federation을 선택하세요** → 이미 Active Directory/Okta 등 IdP를 운영 중이고, IAM Identity Center 없이 직접 연동할 때

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|------|-----------|------------|
| 1 | Access Key를 코드에 하드코딩 | GitHub에 푸시되면 수 분 내 봇이 탐지하여 악용 | 환경변수, AWS SDK 자격증명 체인, IAM Role 사용 |
| 2 | `AdministratorAccess` 일괄 부여 | 한 명이 뚫리면 전체 인프라가 위험 | 최소 권한 Policy + Permissions Boundary 설정 |
| 3 | 퇴사자 Key 미삭제 | 퇴사 후에도 AWS 리소스에 접근 가능 | 오프보딩 체크리스트에 IAM User 삭제/비활성화 포함 |
| 4 | MFA 미적용 | 패스워드만으로는 피싱/무차별 대입에 취약 | 모든 User에 MFA 필수, 가능하면 FIDO2 보안 키 |
| 5 | Access Key 미교체 | 장기간 같은 Key 사용 시 유출 확률 증가 | 90일 교체 정책 + 미사용 Key 자동 비활성화 |

### 🚫 Anti-Patterns

1. **IAM User 공유 사용**: 여러 사람이 하나의 IAM User를 공유하면 **누가 무엇을 했는지 추적이 불가능**해진다. 반드시 1인 1 User 원칙을 지킨다 ([StackProof](https://stackproof.dev/play-books/aws-iam-anti-patterns-and-how-to-fix-them/))
2. **사람 접근에 IAM User 사용**: AWS는 사람의 AWS 접근에 IAM Identity Center(SSO)를 **명시적으로 권장**한다. IAM User는 Role을 사용할 수 없는 워크로드 전용으로 제한한다 ([AWS Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html))
3. **Sandbox Policy를 Production에 복사**: 개발 환경의 넓은 권한 정책을 프로덕션에 그대로 적용하면 민감한 리소스에 불필요한 쓰기 권한이 노출된다 ([Cloud Security In Practice](https://cloudsecurityinpractice.com/en/2026/02/01/common-aws-iam-mistakes-in-enterprises/))

### 🔒 보안/성능 고려사항

- **보안**: Access Key 유출 시 즉시 **비활성화 → 새 Key 발급 → CloudTrail 로그 점검** 순서로 대응
- **보안**: IAM Access Analyzer를 활성화하여 과도한 권한을 자동 탐지
- **성능**: IAM 자체는 무료 서비스이며 API 호출에 요금이 부과되지 않지만, STS `AssumeRole` 호출에는 Rate Limit이 있음

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|------|------|----------|
| 📖 공식 문서 | IAM Users | [AWS IAM User Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users.html) |
| 📖 공식 문서 | Security Best Practices | [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) |
| 📖 공식 문서 | IAM Identity Comparison | [Compare IAM Identities](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction_identity-management.html) |
| 📘 블로그 | Root vs IAM User | [BeyondTrust 비교 가이드](https://www.beyondtrust.com/blog/entry/aws-root-vs-iam-user-what-to-know-when-to-use-them) |
| 📘 블로그 | IAM Anti-Patterns | [StackProof IAM Anti-Patterns](https://stackproof.dev/play-books/aws-iam-anti-patterns-and-how-to-fix-them/) |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리 | 플랫폼 | 용도 |
|---------------|--------|------|
| **AWS CLI** | Cross-platform | `aws iam create-user`, `aws iam create-access-key` 등 User 관리 |
| **IAM Access Analyzer** | AWS Console | 과도한 권한 탐지 및 최소 권한 정책 생성 |
| **IAM Credential Report** | AWS Console/CLI | 모든 User의 자격증명 상태 CSV 다운로드 |
| **AWS CloudTrail** | AWS | User별 API 호출 이력 추적 및 감사 |
| **Terraform** | IaC | `aws_iam_user`, `aws_iam_access_key` 리소스로 코드 관리 |

### 🔮 트렌드 & 전망

- **IAM User 축소 추세**: AWS가 IAM Identity Center를 강력히 권장하면서, 사람 접근용 IAM User는 점차 줄어드는 추세
- **임시 자격증명 표준화**: OIDC Federation, Instance Profile 등 **임시 자격증명** 기반 접근이 업계 표준으로 자리잡는 중
- **Zero Trust 확산**: "항상 검증, 절대 신뢰하지 않기" 원칙에 따라 장기 자격증명인 IAM User Access Key의 사용이 더욱 제한될 전망

### 💬 커뮤니티 인사이트

- AWS re:Post에서 "IAM User vs IAM Identity Center" 질문이 빈번하게 올라오며, 공식 답변은 일관되게 **"사람은 Identity Center, 워크로드는 IAM Role"**을 권장
- 멀티 계정 환경에서 IAM User를 계정마다 만드는 것은 "관리 지옥"이라는 실무자 경험담이 다수

---

## 📎 Sources

1. [IAM Users - AWS Official Docs](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users.html) — 공식 문서
2. [Compare IAM Identities and Credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction_identity-management.html) — 공식 문서
3. [Security Best Practices in IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) — 공식 문서
4. [Root User Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html) — 공식 문서
5. [AWS Root vs IAM User - BeyondTrust](https://www.beyondtrust.com/blog/entry/aws-root-vs-iam-user-what-to-know-when-to-use-them) — 블로그
6. [AWS IAM Anti-Patterns - StackProof](https://stackproof.dev/play-books/aws-iam-anti-patterns-and-how-to-fix-them/) — 블로그
7. [Common AWS IAM Mistakes - Cloud Security In Practice](https://cloudsecurityinpractice.com/en/2026/02/01/common-aws-iam-mistakes-in-enterprises/) — 블로그
8. [AWS IAM Identity Center Guide - CloudQuery](https://www.cloudquery.io/blog/aws-identity-center-guide) — 블로그

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 6
> - 수집 출처 수: 8
> - 출처 유형: 공식 4, 블로그 4, 커뮤니티 2, SNS 0
> - 관련 문서: [[05-aws-iam-concept-explainer]], [[02-aws-iam-group-concept-explainer]], [[03-aws-iam-policy-concept-explainer]], [[04-aws-iam-role-concept-explainer]]
