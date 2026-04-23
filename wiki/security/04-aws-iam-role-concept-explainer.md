---
tags: [security, aws, iam, iam-role, iam-sts, concept-explainer]
created: 2026-04-22
updated: 2026-04-23
---

# 📖 AWS IAM Role — Concept Deep Dive

> 💡 **한줄 요약**: IAM Role은 **장기 자격증명 없이 임시 보안 토큰(STS)**을 발급받아 AWS 리소스에 접근하는 **"입을 수 있는 모자"** 같은 신원(Identity)이다.

---

## 1️⃣ 무엇인가? (What is it?)

**IAM Role**은 AWS 계정 내의 Identity로, **특정 권한을 가지되 장기 자격증명(Password, Access Key)이 없다**. 대신 Role을 **"Assume(맡다)"**하면 AWS STS(Security Token Service)가 **임시 자격증명**(Access Key + Secret Key + Session Token)을 발급해준다.

**현실 세계 비유 (12살도 이해할 수 있는 설명):**

놀이공원에서 **스태프 조끼**를 생각하자. 이 조끼(Role)를 입으면 직원 전용 통로를 사용할 수 있고, 벗으면 다시 일반 손님이 된다. 조끼 자체에 이름표는 없다(누구나 입을 수 있다). 하지만 **"누가 이 조끼를 입을 수 있는지"**는 규칙(Trust Policy)으로 정해져 있다. 손님이 함부로 입을 수 없고, 조끼를 입는 순간부터 일정 시간이 지나면 자동으로 벗겨진다(임시 자격증명 만료).

- **탄생 배경**: IAM User의 장기 Access Key는 유출 위험이 크다. AWS 서비스(EC2, Lambda)가 다른 서비스에 접근할 때, 또는 다른 AWS 계정과 협업할 때 **안전하게 임시 권한을 위임**하는 메커니즘이 필요했다.
- **해결하는 문제**: Access Key 유출 위험 제거, 서비스 간 안전한 권한 위임, cross-account 접근, 외부 IdP(Identity Provider) 연동

> 📌 **핵심 키워드**: `IAM Role`, `AssumeRole`, `STS`, `Trust Policy`, `Temporary Credentials`, `Instance Profile`, `OIDC Federation`

### 🛠️ Role은 직접 만들 수 있다

IAM Role은 IAM User, Group, Policy처럼 **관리자가 직접 생성하는 리소스**이다. Service-Linked Role만 AWS 서비스가 자동 생성하며, 그 외 모든 Role은 사용자가 직접 만든다.

| 방법 | 도구 | 예시 |
|------|------|------|
| 🖥️ AWS Console | IAM → Roles → Create Role | GUI에서 클릭 |
| 💻 AWS CLI | `aws iam create-role` | 명령어로 생성 |
| 🏗️ IaC | Terraform `aws_iam_role` | 코드로 관리 |

```bash
# CLI로 Role 만들기 예시
aws iam create-role \
  --role-name MyAppRole \
  --assume-role-policy-document file://trust-policy.json
```

> 💡 비유: 놀이공원 관리자가 "스태프 조끼"를 새로 만드는 것과 같다. 조끼를 만들면서 ① 누가 입을 수 있는지(Trust Policy), ② 입으면 뭘 할 수 있는지(Permission Policy)를 정한다.

---

## 2️⃣ 핵심 개념 (Core Concepts)

IAM Role은 **두 개의 Policy**로 구성된다: **"누가 이 Role을 맡을 수 있는가"**(Trust Policy)와 **"이 Role이 무엇을 할 수 있는가"**(Permission Policy).

```
┌─────────────────────────────────────────────────────────────┐
│                    IAM Role 핵심 구조                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────────────────────────────────────┐              │
│   │             🎭 IAM Role                   │              │
│   │                                          │              │
│   │  ┌──────────────────────────────┐        │              │
│   │  │ 🔐 Trust Policy              │        │              │
│   │  │ (누가 이 Role을 Assume?)      │        │              │
│   │  │                              │        │              │
│   │  │  • AWS 서비스 (ec2, lambda)   │        │              │
│   │  │  • 다른 AWS 계정             │        │              │
│   │  │  • OIDC/SAML IdP            │        │              │
│   │  │  • 같은 계정의 User/Role     │        │              │
│   │  └──────────────────────────────┘        │              │
│   │                                          │              │
│   │  ┌──────────────────────────────┐        │              │
│   │  │ 📋 Permission Policy          │        │              │
│   │  │ (이 Role이 무엇을 할 수 있나?) │        │              │
│   │  │                              │        │              │
│   │  │  • S3 읽기/쓰기              │        │              │
│   │  │  • DynamoDB 쿼리             │        │              │
│   │  │  • SQS 메시지 전송           │        │              │
│   │  └──────────────────────────────┘        │              │
│   │                                          │              │
│   │  📊 메타데이터                             │              │
│   │  ├─ ARN: arn:aws:iam::123456:role/MyRole │              │
│   │  ├─ Max Session Duration: 1~12시간       │              │
│   │  └─ Path: /application/                  │              │
│   └──────────────────────────────────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

| 구성 요소 | 역할 | 설명 |
|-----------|------|------|
| **Trust Policy** | 접근 제어 (Who) | Role을 Assume할 수 있는 Principal 정의 (Resource-based Policy) |
| **Permission Policy** | 권한 정의 (What) | Role이 수행할 수 있는 Action/Resource 정의 (Identity-based Policy) |
| **STS Token** | 임시 자격증명 | Access Key ID + Secret Key + Session Token (1~12시간) |
| **Instance Profile** | EC2용 래퍼 | Role을 EC2 인스턴스에 전달하는 컨테이너 |
| **External ID** | 혼동된 대리인 방지 | 서드파티 위임 시 추가 보안 식별자 |

> 💡 **Trust Policy ↔ Authentication, Permission Policy ↔ Authorization**. 일반적인 보안 모델로 대응하면:
> - **Trust Policy 검증** = **Authentication(인증)** — "너 누구야? 이 Role 맡을 자격 있어?"
> - **Permission Policy 검증** = **Authorization(인가)** — "OK 신원 확인됐어. 이 작업은 허용돼 있어?"
>
> 비유: 공항에서 **여권 심사(Trust Policy/인증)** → **출입 구역 확인(Permission Policy/인가)**

### 📦 Instance Profile 상세 — "EC2용 Role 택배 상자"

EC2 인스턴스는 IAM Role을 직접 "입을" 수 없다. Role을 **Instance Profile이라는 래퍼(wrapper)**에 담아서 EC2에 전달해야 한다.

```
┌─────────────────────────┐
│  Instance Profile (상자)  │
│  ┌───────────────────┐  │
│  │   IAM Role (물건)   │  │
│  └───────────────────┘  │
└─────────────────────────┘
         │
         ▼
    EC2 인스턴스 (배송지)
```

**실제 동작 흐름:**
1. IAM Role을 만든다
2. Instance Profile을 만든다
3. Role을 Instance Profile에 넣는다 (`aws iam add-role-to-instance-profile`)
4. EC2 인스턴스를 만들 때 Instance Profile을 지정한다

> 📌 AWS Console에서 EC2에 Role을 연결하면, Console이 자동으로 같은 이름의 Instance Profile을 만들어줘서 사용자가 Instance Profile의 존재를 모르는 경우가 많다. CLI/Terraform에서는 직접 만들어야 한다.

### 🆔 External ID 상세 — "혼동된 대리인 방지 비밀 암호"

External ID는 서드파티(SaaS)에게 Role을 위임할 때, **다른 고객의 리소스에 접근하지 못하게 막는 추가 검증 값**이다.

```
❌ External ID 없을 때:

고객 A ──Trust──▶ SaaS 업체
고객 B ──Trust──▶ SaaS 업체

SaaS 업체가 고객 A의 Role ARN을 알면,
고객 B의 요청을 처리하면서 고객 A의 Role을 Assume할 수 있다!

✅ External ID 있을 때:

고객 A ──Trust + ExternalID="abc123"──▶ SaaS 업체
고객 B ──Trust + ExternalID="xyz789"──▶ SaaS 업체

ExternalID가 다르므로 교차 접근 불가!
```

> 💡 비유: 아파트 경비실에서 택배기사에게 비밀번호를 알려주는 것. 택배기사(SaaS)가 "102동 김 씨 택배입니다"라고 하면, 경비실이 "비밀번호는?" 하고 물어본다. 비밀번호를 모르면 통과 불가!

### 🏢 AWS STS (Security Token Service) 상세

STS는 IAM과 별개의 **독립 AWS 서비스**로, **"임시 출입증 발급소"** 역할을 한다. IAM이 "권한을 정의"하는 서비스라면, STS는 "임시 자격증명을 발급"하는 서비스이다.

> 💡 비유: 학교 방문자 명찰 발급 데스크. 신분 확인 후 "임시 명찰"을 주고, 시간이 지나면 자동 만료된다.

**IAM · STS · AWS 서비스의 역할 분담:**

| 단계 | 담당 | 역할 | 보는 Policy |
|------|------|------|-----------|
| ① Assume 요청 | **STS** | "이 Role 맡을 자격 있어?" 검증 | **Trust Policy** |
| ② 토큰 발급 | **STS** | 검증 통과 시 임시 자격증명 발급 | - |
| ③ API 호출 | **AWS 서비스** (S3 등) | "이 자격증명으로 이 작업 가능?" 검증 | **Permission Policy** |

> 💡 비유: 도서관(IAM)에 책(Role)이 보관되어 있지만, 빌리는 행위(AssumeRole)는 사서 데스크(STS)가 처리한다. 각 열람실(AWS 서비스)은 대출증(임시 자격증명)을 확인하고 열람 허용/거부를 결정한다.

| STS API | 용도 |
|---------|------|
| `AssumeRole` | Role을 맡아서 임시 자격증명 받기 |
| `AssumeRoleWithWebIdentity` | OIDC IdP(Google, GitHub)로 Role Assume |
| `AssumeRoleWithSAML` | SAML IdP(Okta, AD)로 Role Assume |
| `GetSessionToken` | IAM User가 MFA 포함 임시 토큰 받기 |
| `GetCallerIdentity` | "나 지금 누구로 인증됐지?" 확인 |

STS가 발급하는 **임시 자격증명 구성**:

```
┌──────────────────────────────────────┐
│  STS 임시 자격증명                    │
│  ├── AccessKeyId     (ASIA... 시작)  │  ← IAM User의 AKIA...와 구별됨
│  ├── SecretAccessKey (임시)          │
│  ├── SessionToken    (필수 첨부)     │
│  └── Expiration      (자동 만료)     │
└──────────────────────────────────────┘
```

#### 🔤 AKIA vs ASIA — Access Key 접두사의 의미

| 접두사 | 의미 | 용도 |
|--------|------|------|
| **AKIA** | IAM User/Root의 **장기** Access Key 식별자 | 영구적, 직접 교체해야 함 ⚠️ |
| **ASIA** | STS가 발급한 **임시** Access Key 식별자 | 자동 만료 ✅ |

> ⚠️ AWS는 AKIA, ASIA의 **풀네임(정식 약자 풀이)을 공식적으로 공개한 적이 없다.** 확실한 것은 **AKIA = 장기(영구) Key, ASIA = 임시(세션) Key**라는 기능적 구분뿐이다. 접두사만 봐도 장기/임시를 구분할 수 있다.

#### 🎫 SessionToken은 왜 필요한가?

IAM User는 AccessKeyId + SecretAccessKey만으로 API를 호출할 수 있는데, STS 임시 자격증명에는 왜 SessionToken이 추가로 필요할까?

**SessionToken은 AWS에게 "이 자격증명이 임시 자격증명이다"라고 알려주는 필수 첨부물**이다:

1. **🔑 임시 자격증명 식별**: API 호출 시 `X-Amz-Security-Token` 헤더로 전달되어, AWS가 임시 자격증명임을 인식
2. **🔐 변조 방지**: AWS가 내부적으로 서명한 **불투명(opaque) 토큰**이므로, 위조·수정 불가
3. **⏰ 세션 유효성 검증**: AWS가 이 토큰을 통해 세션 만료 여부, 원본 Role 등을 내부적으로 검증

> 📌 SessionToken의 내부 구조(어떤 데이터가 들어있는지)는 AWS가 공개하지 않는다. 토큰은 불투명(opaque)한 문자열이며, AWS 내부에서만 해석된다.

> 💡 비유: IAM User Access Key = **집 열쇠** (열쇠만 있으면 문 열림). STS 임시 자격증명 = **호텔 카드키 + 투숙 확인 바코드**. 카드키(AccessKeyId+SecretAccessKey)로 서명하고, 바코드(SessionToken)를 같이 제시해야 호텔 시스템이 "유효한 투숙객"인지 확인할 수 있다.

### 🔤 `sts:AssumeRole`의 `sts:`와 ARN의 `iam:`은 다르다

Policy의 **Action 접두사**와 ARN의 **서비스 접두사**는 서로 다른 맥락에서 쓰인다.

```
Action 접두사:   서비스명:API명           ← "어떤 서비스의 어떤 동작?"
                 s3:GetObject             ← S3의 GetObject API
                 sts:AssumeRole           ← STS의 AssumeRole API
                 iam:CreateUser           ← IAM의 CreateUser API

ARN 접두사:      arn:aws:서비스명:리전:계정:리소스   ← "어떤 서비스에 존재하는 리소스?"
                 arn:aws:s3:::my-bucket
                 arn:aws:iam::123456:role/MyRole
                 arn:aws:iam::123456:user/Alice
```

> 💡 비유: 도서관(IAM)에 책(Role)이 보관되어 있지만, 빌리는 행위(AssumeRole)는 사서 데스크(STS)가 처리한다. Role이라는 "리소스"는 IAM 서비스에 있지만, Role을 "맡는 동작"은 STS 서비스가 처리한다.

### 🎭 Role의 5가지 유형

| 유형 | Trust Principal | 용도 |
|------|----------------|------|
| **Service Role** | AWS 서비스 (ec2, lambda, ecs) | AWS 서비스가 다른 리소스에 접근 |
| **Service-Linked Role** | 특정 AWS 서비스 (자동 생성) | 서비스 운영에 필수적인 사전 정의 Role |
| **Cross-Account Role** | 다른 AWS 계정 | 계정 간 리소스 공유 |
| **Web Identity Role** | OIDC IdP (Google, GitHub) | 외부 IdP 인증 사용자에게 AWS 접근 |
| **SAML 2.0 Role** | SAML IdP (AD, Okta) | 기업 IdP 연동 |

> 💡 **Trust Policy ≠ Cross-Account 전용**. Trust Policy는 "누가 이 Role을 Assume할 수 있는가"를 정의하는 것으로, cross-account는 여러 용도 중 하나일 뿐이다. AWS 서비스 연동(Lambda → SQS 등)이 가장 흔한 사용 사례이며, 같은 계정 내 권한 전환이나 외부 IdP(OIDC/SAML) 연동에도 모두 사용된다.

#### 📛 서비스별 Role 관용 명칭

위 5가지 유형은 **IAM 서비스 자체의 분류**이다. 이와 별개로, 각 AWS 서비스가 Role을 사용할 때 **공식적으로 부르는 이름**이 있다:

| 관용 명칭 | 공식 용어? | 어디서 공식? | Trust Policy Principal | 본질 |
|-----------|----------|------------|----------------------|------|
| **Execution Role** | ✅ Lambda 공식 | [Lambda 문서](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html) | `lambda.amazonaws.com` | 일반 IAM Role |
| **Task Role** | ✅ ECS 공식 | [ECS 문서](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html) | `ecs-tasks.amazonaws.com` | 일반 IAM Role |
| **Task Execution Role** | ✅ ECS 공식 | ECS 문서 | `ecs-tasks.amazonaws.com` | 일반 IAM Role (인프라용) |
| **IRSA** | ✅ EKS 공식 | EKS 문서 | OIDC Provider ARN | 일반 IAM Role |

> 📌 IAM 콘솔에서 Role을 만들 때 "Execution Role 타입"을 선택하는 것이 아니다. 일반 IAM Role을 만들고 Trust Policy에 `lambda.amazonaws.com`을 지정하면 그것이 Lambda에서 말하는 "Execution Role"이 된다. 비유: "운전 면허증"은 하나의 형식이지만, 택시 회사에서 "영업면허", 물류 회사에서 "배송면허"라고 부르는 것과 같다.

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

AssumeRole의 핵심은 **"Trust Policy 검증 → STS 토큰 발급 → 임시 자격증명으로 API 호출"** 3단계이다.

```
┌─────────────────────────────────────────────────────────────────┐
│                    AssumeRole 동작 아키텍처                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  👤 Principal (User/Service/외부IdP)                             │
│    │                                                            │
│    │ ① sts:AssumeRole 요청                                      │
│    │   (Role ARN + [External ID] + [MFA Token])                 │
│    ▼                                                            │
│  ┌──────────────────────────────────────┐                       │
│  │          AWS STS 서비스               │                       │
│  │                                      │                       │
│  │  ② Trust Policy 검증                 │                       │
│  │     - Principal이 허용된 주체인가?     │                       │
│  │     - Condition 충족하는가?           │                       │
│  │     - External ID 일치하는가?         │                       │
│  │                                      │                       │
│  │  ③ 검증 통과 시 임시 자격증명 발급     │                       │
│  │     - AccessKeyId (임시)             │                       │
│  │     - SecretAccessKey (임시)         │                       │
│  │     - SessionToken                   │                       │
│  │     - Expiration (만료 시간)          │                       │
│  └──────────────┬───────────────────────┘                       │
│                  │                                               │
│                  ▼                                               │
│  👤 Principal (이제 Role의 권한으로 활동)                          │
│    │                                                            │
│    │ ④ 임시 자격증명으로 AWS API 호출                             │
│    ▼                                                            │
│  ┌──────────────────────────────────────┐                       │
│  │  AWS 서비스 (S3, DynamoDB, EC2...)    │                       │
│  │                                      │                       │
│  │  ⑤ Permission Policy 기반 권한 평가   │                       │
│  │     → ✅ 허용 또는 ❌ 거부             │                       │
│  └──────────────────────────────────────┘                       │
│                                                                 │
│  ⏰ 세션 만료 시 → 자격증명 자동 무효화                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (Step by Step)

아래 시나리오들은 위 AssumeRole 아키텍처의 **자동화 버전**이다. 수동으로 `sts:AssumeRole`을 호출하는 대신, AWS 서비스(EC2, Lambda 등)가 뒤에서 자동으로 AssumeRole을 수행한다.

**시나리오: EC2에서 S3 접근 (Instance Profile)**

1. **Step 1**: 관리자가 S3 접근 권한이 있는 IAM Role 생성, Trust Policy에 `ec2.amazonaws.com` 지정
2. **Step 2**: Instance Profile에 Role을 연결하고 EC2 인스턴스에 부착
3. **Step 3**: EC2 내 애플리케이션이 **IMDS(Instance Metadata Service)**에서 자동으로 임시 자격증명 획득
4. **Step 4**: AWS SDK가 이 자격증명으로 S3 API 호출
5. **Step 5**: 자격증명 만료 전에 자동으로 새 자격증명 갱신

> 💡 **Trust Policy에 `ec2.amazonaws.com`을 지정**한다는 것은 "EC2 서비스가 이 Role을 Assume할 수 있다"고 허용하는 것이다:
> ```json
> {
>   "Effect": "Allow",
>   "Principal": { "Service": "ec2.amazonaws.com" },
>   "Action": "sts:AssumeRole"
> }
> ```
> ⚠️ 이 설정은 해당 계정의 **모든** EC2 인스턴스에 적용된다. 특정 EC2만 허용하려면 태그 기반 Condition을 추가해야 한다.

> 💡 **Instance Profile 부착 방법:**
> - **Console**: EC2 → 인스턴스 선택 → 작업 → 보안 → IAM 역할 수정 → Role 선택 (Console이 알아서 Instance Profile 생성)
> - **CLI**: ① `aws iam create-instance-profile` → ② `aws iam add-role-to-instance-profile` → ③ `aws ec2 associate-iam-instance-profile --instance-id i-xxx --iam-instance-profile Name=MyProfile`

#### 🔍 IMDS (Instance Metadata Service) 상세

**IMDS**는 EC2 인스턴스 안에서만 접근 가능한 **특수한 내부 HTTP 엔드포인트** (`http://169.254.169.254`)이다. IMDS 자체가 STS를 호출하는 것이 아니라, **EC2 서비스(AWS Control Plane)**가 STS를 호출하고 그 결과를 IMDS에 저장한다.

```
EC2 내 앱       IMDS (저장소)      EC2 서비스        STS
  │               │              (Control Plane)     │
  │               │   ①AssumeRole  │              │
  │               │                ├─────────────►│
  │               │                │  Trust Policy │
  │               │   ②결과 저장    │◄─────────────┤
  │               │◄───────────────┤              │
  │ ③자격증명 요청 │                │              │
  ├──────────────►│                │              │
  │ ④임시 자격증명 │                │              │
  │◄──────────────┤                │              │
  │   (만료 5분 전 EC2 서비스가 자동 갱신)          │
```

```bash
# EC2 인스턴스 내부에서 임시 자격증명 조회
$ curl http://169.254.169.254/latest/meta-data/iam/security-credentials/MyEC2Role
# → { "AccessKeyId": "ASIA...", "SecretAccessKey": "...", "Token": "...", "Expiration": "..." }
```

> 📌 **IMDS v1 vs v2**: 보안을 위해 현재는 **IMDSv2**(토큰 기반)가 권장된다. v1은 SSRF 공격에 취약한 것으로 알려져 있다.

**시나리오: Cross-Account 접근**

```bash
# 💻 Account B의 User가 Account A의 Role을 Assume
aws sts assume-role \
    --role-arn arn:aws:iam::111111111111:role/CrossAccountRole \
    --role-session-name my-session \
    --external-id UniqueExternalId123

# 응답:
# {
#   "Credentials": {
#     "AccessKeyId": "ASIA...",
#     "SecretAccessKey": "wJalr...",
#     "SessionToken": "FwoGZX...",
#     "Expiration": "2026-04-22T13:00:00Z"
#   }
# }
```

**시나리오: Lambda + SQS Trigger (Access Key 완전 불필요)**

Lambda에서 SQS 트리거를 사용할 때, 개발자가 Access Key를 관리할 필요가 전혀 없다. AWS 런타임이 모든 자격증명을 자동으로 처리한다.

```
┌──────────────────────────────────────────────────────────┐
│  Lambda + SQS + IAM Role 동작 흐름                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ① 관리자가 Lambda Execution Role 생성                    │
│     Trust Policy: lambda.amazonaws.com이 Assume 가능      │
│     Permission Policy: sqs:ReceiveMessage 등 허용         │
│                                                          │
│  ② Lambda 함수에 이 Role을 연결                           │
│                                                          │
│  ③ SQS에 메시지 도착 → Lambda 트리거                      │
│                                                          │
│  ④ Lambda 런타임이 자동으로:                               │
│     ├── STS에서 임시 자격증명 발급 (개발자 모름)             │
│     ├── 환경변수에 임시 Key 주입                           │
│     │   AWS_ACCESS_KEY_ID=ASIA...    (임시!)              │
│     │   AWS_SECRET_ACCESS_KEY=...    (임시!)              │
│     │   AWS_SESSION_TOKEN=...                            │
│     └── AWS SDK가 자동으로 이 자격증명 사용                 │
│                                                          │
│  ⑤ 개발자 코드에서는 그냥:                                │
│     import boto3                                         │
│     sqs = boto3.client('sqs')  ← Key 안 넣어도 됨!       │
│     sqs.receive_message(...)   ← 자동으로 Role 권한 사용  │
│                                                          │
│  ⑥ 임시 자격증명은 Lambda 실행 종료 후 자동 만료            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

이 패턴은 Lambda뿐 아니라 거의 모든 AWS 서비스에 적용된다:

| 서비스 | Role 연결 방식 | 자격증명 자동 관리 |
|--------|---------------|-----------------|
| **Lambda** | Execution Role | ✅ 환경변수 자동 주입 |
| **EC2** | Instance Profile | ✅ IMDS에서 자동 갱신 |
| **ECS** | Task Role | ✅ 컨테이너 자격증명 엔드포인트 |
| **EKS** | IRSA (OIDC) | ✅ Pod 단위 Role 매핑 |

> 💡 **핵심 원칙**: AWS 서비스 위에서 돌아가는 코드는 **항상 Role을 사용**하고, **절대 Access Key를 하드코딩하지 않는다**. 이것이 AWS 보안의 기본 중의 기본이다.

### 💻 Trust Policy 예시

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::222222222222:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "UniqueExternalId123"
        }
      }
    }
  ]
}
```

> 💡 **예시 해석 (한 줄씩):**
>
> | 항목 | 의미 | 비유 |
> |------|------|------|
> | `Effect: Allow` | 조건 만족 시 허용 | "문을 열어줘" |
> | `Principal: 222222222222:root` | AWS 계정 222222222222 | "택배 회사 B가" |
> | `Action: sts:AssumeRole` | Role Assume 행위 | "이 조끼를 입으려 할 때" |
> | `sts:ExternalId: UniqueExternalId123` | 이 External ID 제시 필수 | "비밀번호를 말해야만" |
>
> `sts:ExternalId`는 Condition 안에서 사용하는 **조건 키(Condition Key)**이다. AssumeRole API 호출 시 `--external-id` 파라미터로 전달한 값이 이 조건과 매칭된다.

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| # | 유즈 케이스 | 설명 | 적합한 이유 |
|---|------------|------|------------|
| 1 | **EC2/ECS/Lambda → AWS 서비스** | 애플리케이션이 S3, DynamoDB 등에 접근 | Access Key 하드코딩 없이 자동 자격증명 갱신 |
| 2 | **Cross-Account 접근** | Account A의 리소스를 Account B에서 접근 | Access Key 공유 없이 안전한 계정 간 위임 |
| 3 | **GitHub Actions OIDC** | CI/CD 파이프라인에서 AWS 리소스 배포 | 장기 Key 없이 빌드 시점에만 임시 접근 |
| 4 | **Break-Glass 비상 접근** | 긴급 시 관리자가 높은 권한 Role을 Assume | 평소에는 낮은 권한, 필요할 때만 상승 |
| 5 | **서드파티 SaaS 연동** | Datadog, CloudQuery 등이 모니터링 위해 접근 | External ID로 혼동된 대리인 문제 방지 |

### ✅ 베스트 프랙티스

1. **🔄 IAM User 대신 Role 사용**: 사람의 접근은 IAM Identity Center(SSO) + Role Assume, 서비스 접근은 Instance Profile/Task Role 사용 ([AWS Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html))
2. **🔐 Trust Policy 최소화**: `"Principal": {"AWS": "*"}`는 절대 사용하지 않는다. 특정 계정/서비스/IdP만 명시
3. **📱 Cross-Account에 MFA 요구**: Trust Policy Condition에 `aws:MultiFactorAuthPresent` 추가
4. **🆔 서드파티에 External ID 필수**: 혼동된 대리인 공격 방지를 위해 External ID를 항상 요구 ([AWS Security Blog](https://aws.amazon.com/blogs/security/how-to-use-external-id-when-granting-access-to-your-aws-resources/))
5. **⏰ 최소 세션 시간 설정**: `MaxSessionDuration`을 작업에 필요한 최소 시간으로 설정 (기본 1시간)

### 🏢 실제 적용 사례

- **GitHub Actions + OIDC**: `aws-actions/configure-aws-credentials` Action으로 장기 Key 없이 AWS 배포. GitHub의 OIDC 토큰으로 Role Assume
- **멀티 계정 조직**: Hub Account에 IAM Identity Center, Spoke Account에 Cross-Account Role 배치 → 중앙 인증 + 분산 권한

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ 장점 | **임시 자격증명** | 자동 만료되므로 유출되어도 피해 시간 제한 |
| ✅ 장점 | **Key 관리 불필요** | Access Key 교체, 저장, 보호 부담 제거 |
| ✅ 장점 | **Cross-Account 지원** | 계정 간 안전한 리소스 공유 |
| ✅ 장점 | **Federation 지원** | OIDC/SAML로 외부 IdP 연동 |
| ✅ 장점 | **자동 자격증명 갱신** | EC2 IMDS, ECS Task Role 등에서 SDK가 자동 갱신 |
| ❌ 단점 | **Trust Policy 복잡성** | 잘못 설정하면 의도치 않은 접근 허용 |
| ❌ 단점 | **디버깅 어려움** | AssumeRole 실패 시 원인 파악이 어려움 |
| ❌ 단점 | **세션 시간 제한** | 장시간 작업 시 갱신 로직 필요 |

### ⚖️ Trade-off 분석

```
보안성 (임시 자격증명)  ◄──── Trade-off ────►  설정 복잡도 (Trust Policy)
유연성 (누구나 Assume)  ◄──── Trade-off ────►  관리 책임 (누가 Assume 가능?)
자동 갱신              ◄──── Trade-off ────►  세션 만료 처리 필요
```

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 비교 매트릭스: IAM Role vs IAM User

| 비교 기준 | IAM Role | IAM User |
|-----------|----------|----------|
| **자격증명** | 임시 (STS Token, 1~12시간) | 장기 (Access Key, 영구) |
| **소유자** | 누구나 Assume 가능 (Trust Policy에 따라) | 1명에 고정 |
| **Password** | ❌ 없음 | ✅ 콘솔 로그인용 |
| **Access Key** | ❌ 없음 (임시 토큰만) | ✅ 생성 가능 |
| **Key 유출 위험** | ⚡ 낮음 (자동 만료) | ⚠️ 높음 (영구 유효) |
| **AWS 서비스 연동** | ✅ Instance Profile, Task Role | ❌ 불가 (Key 하드코딩 필요) |
| **Cross-Account** | ✅ Trust Policy로 지원 | ❌ Key 공유 필요 |
| **OIDC/SAML** | ✅ Federation 지원 | ❌ 미지원 |
| **AWS 권장** | ✅ 강력 권장 | ⚠️ 최소 사용 |

### 🔍 핵심 차이 요약

```
IAM Role                         IAM User
──────────────────────    vs    ──────────────────────
임시 자격증명 (STS Token)         장기 자격증명 (Access Key)
아무도 "소유"하지 않음             특정 1명에 귀속
모자처럼 "입었다 벗는다"           사원증처럼 "항상 소지"
서비스/계정 간 위임용              개인 접근용
Key 유출 위험 최소                Key 유출 시 즉시 위험
```

### 🔑 "Access Key가 필요한 게 아니라 인증이 필요한 것"

모든 AWS API 호출에는 서명(Signature V4)이 필요하고, 서명에는 Key가 필요하다. **하지만 그 Key가 반드시 IAM User의 "장기" Access Key여야 하는 것은 아니다.**

```
모든 AWS API 호출
    │
    └── 서명(Signature V4) 필요
         │
         └── Key가 필요
              │
              ├── 장기 Key (IAM User)     ⚠️ 영구, 유출 위험 (AKIA... 시작)
              │
              └── 임시 Key (STS/Role)     ✅ 자동 만료, 자동 갱신 (ASIA... 시작)
                   │
                   └── 누가 발급?
                        ├── SSO 로그인 → STS 발급
                        ├── Role Assume → STS 발급
                        ├── OIDC → STS 발급
                        └── Instance Profile → STS 자동 발급
```

> 💡 비유: **집 열쇠(IAM User Access Key)** vs **호텔 카드키(STS 임시 자격증명)**. 둘 다 "문을 연다"는 기능은 같지만, 유출 시 위험도가 완전히 다르다. 집 열쇠를 잃어버리면 자물쇠를 교체해야 하지만, 호텔 카드키는 체크아웃하면 자동 비활성화된다.

#### 🤯 "같은 계정이면 IAM Role 없이도 되는 거 아냐?"

**아니다. 같은 계정이라도 IAM Role이 필요하다.** AWS의 근본 원칙은 **"모든 것은 기본적으로 거부된다 (Default Deny)"**이다.

```
❌ 잘못된 생각:
  "같은 계정이니까 Lambda → SQS 그냥 되겠지?"

✅ 실제:
  Lambda가 SQS에 메시지를 보내려면:
  1. sqs:SendMessage API를 호출해야 함
  2. 모든 API 호출에는 서명(Signature V4)이 필요
  3. 서명에는 AccessKeyId + SecretAccessKey가 필요
  4. 이 Key를 어디서 받지??? → IAM Role이 자동 발급!
```

**"Policy를 정해주면 되는 거 아니야?"** — Policy는 정해야 하지만, Policy만으로는 안 된다. **Policy는 "무엇을 할 수 있는가"를 정의**하는 것이고, 그 Policy를 **들고 있는 Identity(IAM Role)**가 있어야 한다.

```
Policy만 있고 Identity가 없으면? → 누구한테 적용할지 모름!

Policy(규칙집) + Identity(IAM Role) = 작동 ✅
```

개발자가 직접 Access Key를 관리하지는 않는다. **AWS가 자동으로 처리한다:**
1. Lambda 함수 만들기
2. IAM Role 만들기 (Permission: `sqs:SendMessage`)
3. Lambda에 Role 연결 → **끝!** Access Key를 만질 필요 없음
4. (AWS가 자동으로) STS로 임시 Key 발급 → 환경변수 주입 → SDK가 서명 → 실행 후 만료

> 💡 AWS가 "같은 계정이면 무조건 접근 허용"으로 만들지 않은 이유: Lambda A가 모든 S3 버킷, 모든 DynamoDB 테이블, 모든 SQS 큐에 접근 가능해지면 **최소 권한 원칙이 완전히 깨진다.** IAM Role로 각 서비스가 필요한 리소스에만 접근하도록 제한하는 것이 AWS 보안 모델의 핵심이다.

### 📊 실행 환경별 권장 인증 방식

| 실행 환경 | 권장 인증 방식 | 장기 Access Key 필요? |
|-----------|--------------|---------------------|
| AWS 서비스 위 (Lambda, EC2, ECS) | IAM Role (자동 Assume) | ❌ 불필요 |
| 개발자 로컬 PC (aws cli) | IAM Identity Center (SSO 로그인) | ❌ 불필요 |
| CI/CD 파이프라인 (GitHub Actions) | OIDC Federation (Web Identity Role) | ❌ 불필요 |
| 온프레미스 서버 | IAM Roles Anywhere (X.509 인증서) | ❌ 불필요 |
| 레거시 도구 🦕 (Role 미지원) | IAM User Access Key (최소 권한 + 교체) | ⚠️ 어쩔수없음 |

### 🤔 언제 무엇을 선택?

- **IAM Role을 선택하세요** → EC2/Lambda/ECS에서 AWS 서비스 접근, cross-account 접근, CI/CD OIDC 연동, 서드파티 SaaS 연동
- **IAM User를 선택하세요** → IAM Role을 지원하지 않는 레거시 서드파티 도구, CodeCommit SSH 접근 (최소한으로 제한)

> 💡 **"이게 이해가 안 가네"에 대한 해설:**
>
> | 가이드 항목 | 의미 | 예시 |
> |------------|------|------|
> | EC2/Lambda/ECS에서 AWS 서비스 접근 | Lambda가 SQS에 메시지 보내기, EC2가 S3 읽기 | Execution Role, Instance Profile |
> | cross-account 접근 | 다른 AWS 계정의 리소스에 접근 | Cross-Account Role + Trust Policy |
> | CI/CD OIDC 연동 | GitHub Actions에서 AWS에 배포 | OIDC Federation + Web Identity Role |
> | 서드파티 SaaS 연동 | Datadog이 CloudWatch 모니터링 | Cross-Account Role + External ID |
>
> 평소 AWS Console에서 Lambda 함수를 만들 때 "실행 역할"을 선택하는 화면이 바로 IAM Role을 연결하는 것이다. 자동으로 처리되어서 인식하지 못했을 뿐, 이미 사용하고 있었을 가능성이 높다.

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|------|-----------|------------|
| 1 | Trust Policy에 `"Principal": {"AWS": "*"}` | 모든 AWS 계정이 Role을 Assume 가능 | 특정 계정/서비스 ARN만 명시 |
| 2 | 서드파티 위임 시 External ID 미사용 | **혼동된 대리인(Confused Deputy)** 공격에 취약 | Condition에 `sts:ExternalId` 필수 추가 |
| 3 | Permission Policy에 `"*"` 과도 사용 | Role을 Assume한 주체가 모든 리소스 접근 가능 | 최소 권한 원칙 적용 |
| 4 | MaxSessionDuration을 12시간으로 설정 | 자격증명 유출 시 피해 시간이 길어짐 | 작업에 필요한 최소 시간 설정 |
| 5 | Cross-Account Role에 MFA 미요구 | 탈취된 자격증명으로 다른 계정까지 침투 | Trust Policy에 MFA Condition 추가 |
| 6 | "Role = Organizations/SSO 필수"라는 오해 | Role 도입을 불필요하게 지연 | **Organizations 없이도 IAM Role은 독립적으로 사용 가능**. SSO(IAM Identity Center)만 Organizations가 필요하다 |

### 🚫 Anti-Patterns

1. **혼동된 대리인(Confused Deputy)**: SaaS 업체 A가 고객 B의 Role ARN으로 고객 C의 리소스에 접근하는 공격. 연구에 따르면 90개 벤더 중 **37%가 External ID를 올바르게 구현하지 않았다** ([Praetorian](https://www.praetorian.com/blog/aws-iam-assume-role-vulnerabilities/))
2. **Role 체이닝 남용**: Role A → Role B → Role C처럼 여러 Role을 연쇄적으로 Assume하면 세션 시간이 1시간으로 제한되고, 디버깅이 극도로 어려워진다
3. **과도한 Trust 범위**: `"Principal": {"Service": "ec2.amazonaws.com"}`을 설정하면 해당 계정의 **모든** EC2 인스턴스가 Role을 사용 가능. 태그 기반 Condition으로 제한해야 한다

### 🔒 보안/성능 고려사항

- **보안**: Trust Policy 변경은 즉시 적용된다. 코드 리뷰/IaC 없이 콘솔에서 변경하면 감사 추적이 어렵다
- **보안**: `aws:SourceArn`과 `aws:SourceAccount` Condition을 Service Role에 추가하여 혼동된 대리인 방지
- **성능**: STS API에는 Rate Limit이 있다 (리전당 초당 수백 회). 대량 Assume 시 throttling 주의

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 💻 로컬 AWS CLI에서 Role 사용하기

#### 방법 1: IAM Identity Center (SSO) — AWS 최고 권장 ✅

> ⚠️ **전제조건**: AWS Organizations 활성화 + IAM Identity Center 활성화 필요

```bash
# SSO 프로필 설정
$ aws configure sso
SSO session name: my-sso
SSO start URL: https://my-org.awsapps.com/start
SSO region: ap-northeast-2

# 매일 로그인 (브라우저 열림 → 회사 계정으로 로그인)
$ aws sso login --profile my-profile

# 사용 — 장기 Access Key 없이 임시 자격증명 자동 사용
$ aws s3 ls --profile my-profile
$ aws ssm start-session --target i-xxx --profile my-profile
```

설정 후 `~/.aws/config`:

```ini
[profile my-profile]
sso_session = my-sso
sso_account_id = 123456789012
sso_role_name = AdministratorAccess
region = ap-northeast-2

[sso-session my-sso]
sso_start_url = https://my-org.awsapps.com/start
sso_region = ap-northeast-2
sso_registration_scopes = sso:account:access
```

#### 방법 2: Profile Chaining (Organizations 없이 사용 가능) ✅

IAM User에 `sts:AssumeRole` 권한만 부여하고, 실제 작업은 항상 Role의 임시 자격증명으로 수행하는 방식이다.

```ini
# ~/.aws/config

# 기본 프로필 (User의 장기 Key - sts:AssumeRole만 가능)
[profile base]
region = ap-northeast-2

# Role 프로필 (실제 작업용 - base를 통해 자동 AssumeRole)
[profile dev]
role_arn = arn:aws:iam::123456789012:role/DevRole
source_profile = base
region = ap-northeast-2
# mfa_serial = arn:aws:iam::123456789012:mfa/cjynim  ← MFA 사용 시
```

```bash
# 사용 — 내부적으로 자동 AssumeRole 처리
$ aws s3 ls --profile dev
```

> 💡 장기 Key는 남아있지만, `sts:AssumeRole` 외에는 아무 권한이 없으므로 유출 피해가 극히 제한된다.

#### 두 방식 비교

| 항목 | SSO (Identity Center) | Profile Chaining |
|------|----------------------|-----------------|
| Organizations 필요 | ✅ 필요 | ❌ 불필요 |
| 장기 Key 존재 | ❌ 없음 | ✅ 있음 (최소 권한) |
| 실제 작업 자격증명 | 임시 토큰 ✅ | 임시 토큰 ✅ |
| Key 유출 시 피해 | 🎉 Key 없음 | ⚡ AssumeRole 권한만 노출 |
| 설정 난이도 | ⭐⭐⭐ | ⭐⭐ |
| 보안 수준 | ⭐⭐⭐⭐ | ⭐⭐⭐ |

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|------|------|----------|
| 📖 공식 문서 | IAM Roles | [AWS IAM Roles Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) |
| 📖 공식 문서 | Confused Deputy Problem | [Confused Deputy Prevention](https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html) |
| 📖 공식 문서 | Common Scenarios for Roles | [Common Role Scenarios](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_common-scenarios.html) |
| 📖 공식 문서 | IAM Identity Center | [AWS IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html) |
| 📘 블로그 | Trust Policy 가이드 | [AWS Security Blog](https://aws.amazon.com/blogs/security/how-to-use-trust-policies-with-iam-roles/) |
| 📘 블로그 | External ID 사용법 | [AWS Security Blog](https://aws.amazon.com/blogs/security/how-to-use-external-id-when-granting-access-to-your-aws-resources/) |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리 | 플랫폼 | 용도 |
|---------------|--------|------|
| **AWS STS CLI** | CLI | `aws sts assume-role`, `get-caller-identity` |
| **aws-actions/configure-aws-credentials** | GitHub Actions | OIDC 기반 Role Assume |
| **Terraform** | IaC | `aws_iam_role`, `aws_iam_role_policy`, `assume_role_policy` |
| **IAM Access Analyzer** | AWS Console | Trust Policy 외부 접근 분석 |
| **Leapp** | Desktop App | 로컬 개발 시 Role Assume 세션 관리 GUI |

### 🔮 트렌드 & 전망

- **OIDC Federation 표준화**: GitHub Actions, GitLab CI, CircleCI 등 주요 CI/CD가 OIDC를 지원하면서 장기 Access Key 사용이 급격히 줄어드는 추세
- **IAM Roles Anywhere**: 온프레미스 서버에서도 X.509 인증서 기반으로 Role을 Assume할 수 있는 기능 — 클라우드-온프레미스 하이브리드 환경에서 통일된 인증 제공
- **Zero Trust 가속**: "항상 검증" 원칙에 따라 Role의 세션 시간 단축 + Condition 강화 추세

### 💬 커뮤니티 인사이트

- "IAM User는 사람용, IAM Role은 그 외 모든 것용" — 가장 자주 인용되는 AWS 커뮤니티 격언
- EC2에서 Access Key 하드코딩하는 것은 "AWS 보안의 원죄"로 불림. Instance Profile이 항상 정답
- Trust Policy 디버깅 시 `aws sts get-caller-identity`가 첫 번째 확인 명령어

---

## 📎 Sources

1. [IAM Roles - AWS Official Docs](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) — 공식 문서
2. [AssumeRole - AWS STS API Reference](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html) — 공식 문서
3. [The Confused Deputy Problem - AWS Official Docs](https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html) — 공식 문서
4. [How to Use Trust Policies - AWS Security Blog](https://aws.amazon.com/blogs/security/how-to-use-trust-policies-with-iam-roles/) — 공식 블로그
5. [How to Use External ID - AWS Security Blog](https://aws.amazon.com/blogs/security/how-to-use-external-id-when-granting-access-to-your-aws-resources/) — 공식 블로그
6. [AWS Trust Policy Complete Guide - DEV Community](https://dev.to/aws-builders/aws-trust-policy-complete-guide-how-to-control-iam-role-access-in-2025-cfi) — 블로그
7. [AWS IAM Assume Role Vulnerabilities - Praetorian](https://www.praetorian.com/blog/aws-iam-assume-role-vulnerabilities/) — 보안 연구
8. [IAM Roles Types & Use Cases - QloudX](https://www.qloudx.com/aws-iam-roles-types-use-cases/) — 블로그
9. [AWS IAM Identity Center - AWS Official Docs](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html) — 공식 문서
10. [AWS STS - AWS Official Docs](https://docs.aws.amazon.com/STS/latest/APIReference/welcome.html) — 공식 문서
11. [Programmatic Access & Security Credentials - AWS Official Docs](https://docs.aws.amazon.com/IAM/latest/UserGuide/security-creds-programmatic-access.html) — 공식 문서 (AKIA/ASIA 접두사)
12. [EC2 IMDS Security Credentials - AWS Official Docs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-metadata-security-credentials.html) — 공식 문서 (IMDS 동작)
13. [Lambda Execution Role - AWS Official Docs](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html) — 공식 문서 (Execution Role)
14. [ECS Task IAM Role - AWS Official Docs](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html) — 공식 문서 (Task Role)
15. [Signature V4 Signing - AWS Official Docs](https://docs.aws.amazon.com/general/latest/gr/sigv4-add-signature-to-request.html) — 공식 문서 (SessionToken/Sig V4)
16. [SQS Access Management - AWS Official Docs](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-overview-of-managing-access.html) — 공식 문서 (같은 계정 접근 권한)

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 4 + 5 (Q&A 검증)
> - 수집 출처 수: 16
> - 출처 유형: 공식 13, 블로그 2, 보안 연구 1, SNS 0
> - 관련 문서: [[05-aws-iam-concept-explainer]], [[01-aws-iam-user-concept-explainer]], [[02-aws-iam-group-concept-explainer]], [[03-aws-iam-policy-concept-explainer]]
