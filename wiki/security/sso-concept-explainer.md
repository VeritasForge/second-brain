---
tags: [security, sso, authentication, identity-provider, concept-explainer]
created: 2026-04-09
---

# SSO (Single Sign-On) — Concept Deep Dive

> **한줄 요약**: SSO는 한 번의 로그인으로 여러 개의 서비스와 애플리케이션에 접근할 수 있게 해주는 인증 메커니즘이다.

---

## 1. 무엇인가? (What is it?)

**SSO(Single Sign-On)**는 사용자가 **한 번만 로그인하면** 연결된 여러 애플리케이션과 서비스에 추가 로그인 없이 접근할 수 있게 해주는 **인증(Authentication) 서비스**이다.

**현실 세계 비유 (12살도 이해할 수 있는 설명):**

놀이공원에 가면 **자유이용권**이 있다. 매표소에서 한 번만 자유이용권을 사면, 그 다음부터는 롤러코스터, 바이킹, 회전목마 어디를 가든 일일이 표를 사지 않아도 된다. 팔찌(자유이용권)를 보여주기만 하면 된다. SSO가 바로 이 자유이용권이다. 한 번 로그인(매표소)하면, 그 다음부터는 Gmail, YouTube, Google Drive 같은 서비스에 따로 로그인하지 않아도 된다.

- **탄생 배경**: 기업 환경에서 직원들이 수십 개의 업무용 앱을 사용하게 되면서, 각각의 비밀번호를 관리하는 것이 큰 부담이 되었다. 비밀번호를 잊어버리거나, 같은 비밀번호를 여러 곳에 재사용하는 보안 문제가 커졌고, 이를 해결하기 위해 SSO가 등장했다.
- **해결하는 문제**: 비밀번호 피로(password fatigue), 인증 중복, 보안 취약점, 사용자 경험 저하

> **핵심 키워드**: `Authentication`, `Identity Provider (IdP)`, `Service Provider (SP)`, `Token`, `Federated Identity`

---

## 2. 핵심 개념 (Core Concepts)

SSO를 이해하려면 세 명의 등장인물과 그들 사이를 오가는 "신분증(Token)"을 이해하면 된다.

```
┌─────────────────────────────────────────────────────────────┐
│                   SSO 핵심 구성 요소                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐    인증 요청     ┌──────────────────┐        │
│   │  사용자   │ ──────────────► │  Identity Provider│        │
│   │  (User)  │ ◄────────────── │     (IdP)         │        │
│   └──────────┘   Token 발급     └──────────────────┘        │
│        │                              ▲                     │
│        │ Token 제시                    │ Token 검증          │
│        ▼                              │                     │
│   ┌──────────────────────────────────────┐                  │
│   │        Service Providers (SP)         │                  │
│   │  ┌──────┐  ┌──────┐  ┌──────┐       │                  │
│   │  │ App A│  │ App B│  │ App C│       │                  │
│   │  └──────┘  └──────┘  └──────┘       │                  │
│   └──────────────────────────────────────┘                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

| 구성 요소 | 역할 | 비유 |
|-----------|------|------|
| **User (사용자)** | 서비스에 접근하려는 사람 | 놀이공원 방문객 |
| **Identity Provider (IdP)** | 사용자의 신원을 확인하고 Token을 발급하는 중앙 인증 서버 | 놀이공원 매표소 |
| **Service Provider (SP)** | 사용자가 접근하려는 애플리케이션/서비스 | 놀이공원 안의 놀이기구들 |
| **Authentication Token** | 사용자의 신원이 확인되었음을 증명하는 디지털 증표 | 자유이용권 팔찌 |
| **Session** | Token이 유효한 동안 유지되는 인증 상태 | 팔찌의 유효 시간 (오늘 하루) |

**핵심 원리:**
- **중앙 집중식 인증**: 모든 인증은 IdP 한 곳에서 처리된다
- **신뢰 관계 (Trust)**: SP는 IdP가 발급한 Token을 신뢰한다 (사전에 계약/설정 필요)
- **토큰 기반 검증**: 비밀번호가 아닌, IdP가 발급한 Token으로 신원을 증명한다

---

## 3. 아키텍처와 동작 원리 (Architecture & How it Works)

SSO의 전체 동작 흐름을 단계별로 살펴보자.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SSO 인증 흐름 (전체 아키텍처)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  사용자(Browser)          Service Provider (App)      IdP (인증서버) │
│       │                         │                         │         │
│  [1]  │── App A 접근 요청 ─────►│                         │         │
│       │                         │                         │         │
│  [2]  │◄── "로그인 필요" ───────│                         │         │
│       │    (IdP로 리다이렉트)    │                         │         │
│       │                         │                         │         │
│  [3]  │── 로그인 페이지 요청 ──────────────────────────► │         │
│       │                         │                         │         │
│  [4]  │── ID/PW 입력 ─────────────────────────────────► │         │
│       │                         │                         │         │
│  [5]  │◄── Token 발급 + App A로 리다이렉트 ──────────── │         │
│       │                         │                         │         │
│  [6]  │── Token 제시 ──────────►│                         │         │
│       │                         │── Token 유효성 확인 ──►│         │
│       │                         │◄── "유효함" ───────────│         │
│  [7]  │◄── 접근 허가! ──────────│                         │         │
│       │                         │                         │         │
│  ─ ─ ─ ─ ─ ─ ─  이후 App B 접근 시  ─ ─ ─ ─ ─ ─ ─ ─ ─           │
│       │                         │                         │         │
│  [8]  │── App B 접근 요청 ─────►│(App B)                  │         │
│  [9]  │◄── IdP로 리다이렉트 ───│                         │         │
│  [10] │── (이미 세션 있음) ────────────────────────────► │         │
│  [11] │◄── Token 자동 발급 (로그인 불필요!) ─────────── │         │
│  [12] │── Token 제시 ──────────►│                         │         │
│  [13] │◄── 접근 허가! ──────────│                         │         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 동작 흐름 (Step by Step)

1. **Step 1-2**: 사용자가 App A에 접근한다. App A는 "이 사람 누구지?" 하고 IdP에게 물어보라고 사용자를 리다이렉트한다.
2. **Step 3-4**: 사용자가 IdP의 로그인 페이지에서 ID와 비밀번호를 입력한다.
3. **Step 5**: IdP가 "이 사람은 진짜 맞아!"라고 확인하고, **Authentication Token**을 발급한다.
4. **Step 6-7**: 사용자가 이 Token을 App A에 제시하면, App A는 IdP에게 "이 토큰 진짜야?"라고 확인한 후 접근을 허가한다.
5. **Step 8-13 (핵심!)**: 이후 App B에 접근할 때, IdP에 이미 로그인 세션이 남아 있으므로 **비밀번호를 다시 입력하지 않아도** Token이 자동 발급된다.

**SSO를 구현하는 대표 프로토콜:**

```python
# OIDC 기반 SSO 로그인 요청 예시 (Python Flask)
from authlib.integrations.flask_client import OAuth

oauth = OAuth(app)
oauth.register(
    name='google',
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

@app.route('/login')
def login():
    redirect_uri = url_for('callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/callback')
def callback():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.parse_id_token(token, nonce=None)
    session['user'] = user_info
    return redirect('/')
```

---

## 4. 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 대표 유즈 케이스

| # | 유즈 케이스 | 설명 | 적합한 이유 |
|---|------------|------|------------|
| 1 | **기업 내부 업무 시스템** | 사원이 이메일, HR, ERP, 메신저 등 수십 개 앱에 한 번에 접근 | 비밀번호 피로 해소, IT 헬프데스크 비용 절감 |
| 2 | **Google Workspace** | Gmail 로그인 한 번으로 Drive, YouTube, Calendar 자동 접근 | 같은 생태계 내 끊김 없는 사용자 경험 |
| 3 | **B2B SaaS 제품** | 기업 고객이 자사 IdP(Okta 등)로 SaaS에 로그인 | 대기업 영업 시 SSO 지원이 필수 요구사항 |
| 4 | **교육 기관** | 학생이 LMS, 도서관, 이메일에 학교 계정 하나로 접근 | 수만 명 사용자 관리 효율화 |
| 5 | **의료 시스템** | 의사/간호사가 EMR, PACS 등 임상 시스템에 빠르게 접근 | 응급 상황에서 빠른 인증이 중요 |

### 베스트 프랙티스

1. **반드시 MFA(다중 인증)와 함께 사용하라**: SSO만으로는 부족하다. 비밀번호 + OTP/생체인증을 결합해야 한다.
2. **표준 프로토콜을 사용하라**: 자체 구현 대신 SAML 2.0 또는 OIDC 같은 검증된 표준을 채택하라.
3. **자동 프로비저닝/디프로비저닝 구현**: 직원이 퇴사하면 SSO 계정을 즉시 비활성화해야 한다. SCIM 프로토콜 활용 권장.
4. **토큰 만료 시간을 적절히 설정하라**: 너무 길면 보안 위험, 너무 짧으면 사용자 불편.
5. **감사 로그(Audit Log)를 남겨라**: 누가 언제 어디에 접근했는지 기록하여 컴플라이언스 충족.

---

## 5. 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ 장점 | **비밀번호 피로 해소** | 하나의 비밀번호만 기억하면 되므로 더 강한 비밀번호 사용 가능 |
| ✅ 장점 | **사용자 경험 향상** | 서비스 간 이동 시 반복 로그인 없이 매끄러운 경험 제공 |
| ✅ 장점 | **보안 강화** | 중앙에서 MFA, 접근 정책, 감사 로그를 일괄 관리 가능 |
| ✅ 장점 | **IT 운영 비용 절감** | "비밀번호 재설정" 헬프데스크 요청이 크게 줄어듬 |
| ✅ 장점 | **컴플라이언스 충족** | 중앙 로그로 HIPAA, SOC2 등 규제 요건 대응 용이 |
| ❌ 단점 | **단일 장애점 (SPOF)** | IdP가 다운되면 모든 서비스에 로그인 불가능 |
| ❌ 단점 | **보안 집중 위험** | SSO 계정이 탈취되면 연결된 모든 서비스가 노출됨 |
| ❌ 단점 | **구현 복잡도** | SAML/OIDC 프로토콜 이해, IdP 연동, 엣지 케이스 처리 필요 |
| ❌ 단점 | **벤더 종속** | 특정 IdP(Okta, Azure AD)에 의존하게 될 수 있음 |

---

## 6. 차이점 비교 (Comparison)

SSO는 "개념"이고, 이를 구현하는 "프로토콜"이 SAML, OAuth 2.0, OIDC이다.

```
┌─────────────────────────────────────────────────┐
│              SSO (개념/목표)                      │
│     "한 번 로그인하면 여러 곳에 접근"              │
│                                                  │
│  구현 프로토콜:                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │  SAML    │ │ OAuth 2.0│ │ OIDC             │ │
│  │ (인증+   │ │ (인가    │ │ (OAuth2 +        │ │
│  │  인가)   │ │  전용)   │ │  인증 = 완전체)  │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
└─────────────────────────────────────────────────┘
```

| 비교 기준 | SAML 2.0 | OAuth 2.0 | OIDC |
|-----------|----------|-----------|------|
| **핵심 목적** | 인증 + 인가 | 인가(Authorization)만 | 인증 + 인가 |
| **데이터 형식** | XML | JSON | JSON (JWT) |
| **Token 유형** | SAML Assertion (XML) | Access Token | ID Token (JWT) + Access Token |
| **주요 대상** | 엔터프라이즈/레거시 | API 접근 위임 | 모던 웹/모바일 앱 |
| **복잡도** | 높음 (XML 파싱) | 중간 | 중간 |
| **모바일 지원** | 어려움 | 좋음 | 매우 좋음 |
| **현재 트렌드** | 레거시 유지 | 인가 전용으로 사용 | 신규 프로젝트 표준 |

---

## 7. 사용 시 주의점 (Pitfalls & Cautions)

### 흔한 실수

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|------|-----------|------------|
| 1 | **MFA 없이 SSO만 적용** | SSO 계정 하나 뚫리면 모든 서비스 노출 | 반드시 MFA와 함께 적용 |
| 2 | **토큰 만료 시간 너무 길게 설정** | 탈취된 토큰으로 장시간 악용 가능 | 업무 시간 기준 적절한 TTL 설정 |
| 3 | **퇴사자 계정 미삭제** | 퇴사한 직원이 여전히 시스템에 접근 가능 | SCIM으로 자동 디프로비저닝 구현 |
| 4 | **SSO 프로토콜 자체 구현** | 보안 취약점 발생 확률 극히 높음 | 검증된 라이브러리/서비스 사용 |
| 5 | **state 파라미터 누락 (OAuth/OIDC)** | CSRF 공격에 노출됨 | state 파라미터 필수 포함 및 검증 |

---

## 8. 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 관련 도구 & 라이브러리

| 도구/라이브러리 | 언어/플랫폼 | 용도 |
|---------------|-----------|------|
| **Keycloak** | Java (Self-hosted) | 오픈소스 IdP, SAML/OIDC 모두 지원 |
| **Auth0** | SaaS | 가장 쉬운 SSO 구현, 개발자 친화적 |
| **Okta** | SaaS | 엔터프라이즈 SSO의 표준 |
| **Authlib** | Python | OAuth/OIDC 클라이언트 라이브러리 |
| **NextAuth.js** | Next.js | React/Next.js 앱의 인증 통합 |

### 트렌드 & 전망

- **OIDC가 SAML을 빠르게 대체 중**: 신규 프로젝트에서는 OIDC가 사실상 표준
- **Passkey/FIDO2 통합**: 비밀번호 없는 SSO가 확산 중
- **B2B SaaS에서 SSO는 필수**: 대기업에 SaaS를 팔려면 SAML 또는 OIDC SSO 지원이 영업 전제 조건

---

## Sources

1. [What is SSO? - Cloudflare](https://www.cloudflare.com/learning/access-management/what-is-sso/)
2. [How Single Sign-On Works - OneLogin](https://www.onelogin.com/learn/how-single-sign-on-works)
3. [SSO: OAuth2 vs OIDC vs SAML - Pomerium](https://www.pomerium.com/blog/sso-oauth2-vs-oidc-vs-saml)
4. [SSO Best Practices - WorkOS](https://workos.com/guide/sso-best-practices)
5. [What is SSO? - AWS](https://aws.amazon.com/what-is/sso/)
