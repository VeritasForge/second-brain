---
tags: [security, aws, iam, iam-role, concept-explainer]
created: 2026-04-22
---

# 📖 AWS IAM Role — Concept Deep Dive

> 💡 **한줄 요약**: IAM Role은 **장기 자격증명 없이 임시 보안 토큰(STS)**을 발급받아 AWS 리소스에 접근하는 **"입을 수 있는 모자"** 같은 신원(Identity)이다.

---

## 1️�� 무엇인가? (What is it?)

**IAM Role**은 AWS 계정 내의 Identity로, **특정 권한을 가지되 장기 자격증명(Password, Access Key)이 없다**. 대신 Role을 **"Assume(맡다)"**하면 AWS STS(Security Token Service)가 **임시 자격증명**(Access Key + Secret Key + Session Token)을 발급해준다.

**현실 세계 비유 (12살도 이해할 수 있는 설명):**

놀이공원에서 **스태프 조끼**를 생각하자. 이 조끼(Role)를 입으면 직원 전용 통로를 사용할 수 있고, 벗으면 다시 일반 손님이 된다. 조끼 자체에 이름표는 없다(누구나 입을 수 있다). 하지만 **"누가 이 조끼를 입을 수 있는지"**는 규칙(Trust Policy)으로 정해져 있다. 손님이 함부로 입을 수 없고, 조끼를 입는 순간부터 일정 시간이 지나면 자동으로 벗겨진다(임시 자격증명 만료).

- **탄생 배경**: IAM User의 장기 Access Key는 유출 위험이 크다. AWS 서비스(EC2, Lambda)가 다른 서비스에 접근할 때, 또는 다른 AWS 계정과 협업할 때 **안전하게 임시 권한을 위임**하는 메커니즘이 필요했다.
- **해결하는 문제**: Access Key 유출 위험 제거, 서비스 간 안전한 권한 위임, cross-account 접근, 외부 IdP(Identity Provider) 연동

> 📌 **핵심 키워드**: `IAM Role`, `AssumeRole`, `STS`, `Trust Policy`, `Temporary Credentials`, `Instance Profile`, `OIDC Federation`

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

### 🎭 Role의 5가지 유형

| 유형 | Trust Principal | 용도 |
|------|----------------|------|
| **Service Role** | AWS 서비스 (ec2, lambda, ecs) | AWS 서비스가 다른 리소스에 접근 |
| **Service-Linked Role** | 특정 AWS 서비스 (자동 생성) | 서비스 운영에 필수적인 사전 정의 Role |
| **Cross-Account Role** | 다른 AWS 계정 | 계정 간 리소스 공유 |
| **Web Identity Role** | OIDC IdP (Google, GitHub) | 외부 IdP 인증 사용자에게 AWS 접근 |
| **SAML 2.0 Role** | SAML IdP (AD, Okta) | 기업 IdP 연동 |

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

**시나리오: EC2에서 S3 접근 (Instance Profile)**

1. **Step 1**: 관리자가 S3 접근 권한이 있는 IAM Role 생성, Trust Policy에 `ec2.amazonaws.com` 지정
2. **Step 2**: Instance Profile에 Role을 연결하고 EC2 인스턴스에 부착
3. **Step 3**: EC2 내 애플리케이션이 **IMDS(Instance Metadata Service)**에서 자동으로 임시 자격증명 획득
4. **Step 4**: AWS SDK가 이 자격증명으로 S3 API 호출
5. **Step 5**: 자격증명 만료 전에 IMDS가 자동으로 새 자격증명 갱신

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

### 🤔 언제 무엇을 선택?

- **IAM Role을 선택하세요** → EC2/Lambda/ECS에서 AWS 서비스 접근, cross-account 접근, CI/CD OIDC 연동, 서드파티 SaaS 연동
- **IAM User를 선택하세요** → IAM Role을 지원하지 않는 레거시 서드파티 도구, CodeCommit SSH 접근 (최소한으로 제한)

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

### 🚫 Anti-Patterns

1. **혼동된 대리인(Confused Deputy)**: SaaS 업체 A가 고객 B의 Role ARN으로 고객 C의 리소스에 접근하는 공격. 연구에 따르면 90개 벤더 중 **37%가 External ID를 올바르게 구현하지 않았다** ([Praetorian](https://www.praetorian.com/blog/aws-iam-assume-role-vulnerabilities/))
2. **Role 체이닝 남용**: Role A → Role B → Role C처럼 여러 Role을 연쇄적으로 Assume하면 세션 시간이 1시간으로 제한되고, 디버깅이 극도로 어려워진다
3. **과도한 Trust 범위**: `"Principal": {"Service": "ec2.amazonaws.com"}`을 설정하면 해당 계정의 **모든** EC2 인스턴스가 Role을 사용 가능. 태그 기반 Condition으로 제한해야 한다

### 🔒 보안/성능 고려사항

- **보안**: Trust Policy 변경은 즉시 적용된다. 코드 리뷰/IaC 없이 콘솔에서 변경하면 감사 추적이 어렵다
- **보안**: `aws:SourceArn`과 `aws:SourceAccount` Condition을 Service Role에 추가하여 혼동된 대리인 방지
- **성능**: STS API에는 Rate Limit이 있다 (리전당 초당 수백 회). 대량 Assume 시 throttling 주의

---

## 8️�� 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|------|------|----------|
| 📖 공식 문서 | IAM Roles | [AWS IAM Roles Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) |
| 📖 공식 문서 | Confused Deputy Problem | [Confused Deputy Prevention](https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html) |
| 📖 공식 문서 | Common Scenarios for Roles | [Common Role Scenarios](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_common-scenarios.html) |
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

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 4
> - 수집 출처 수: 8
> - 출처 유형: 공식 5, 블로그 2, 보안 연구 1, SNS 0
> - 관련 문서: [[05-aws-iam-concept-explainer]], [[01-aws-iam-user-concept-explainer]], [[02-aws-iam-group-concept-explainer]], [[03-aws-iam-policy-concept-explainer]]
