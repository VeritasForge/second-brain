---
tags: [security, oauth, oauth2, authorization, access-token, concept-explainer]
created: 2026-04-09
---

# OAuth 2.0 — Concept Deep Dive

> **한줄 요약**: OAuth 2.0은 사용자의 비밀번호를 제3자 앱에 직접 알려주지 않고도, 그 앱이 사용자의 데이터에 **제한적으로 접근**할 수 있게 해주는 **권한 위임(Authorization) 프레임워크**이다.

---

## 1. 무엇인가? (What is it?)

OAuth 2.0은 **제3자 애플리케이션이 HTTP 서비스에 대한 제한된 접근 권한을 얻을 수 있게 해주는 인가(Authorization) 프레임워크**이다. [RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)로 2012년 10월 표준화되었다.

### 현실 세계 비유 (12살도 이해할 수 있는 버전)

**호텔 카드키**를 떠올려보자.

- 너(사용자)가 호텔(Google)에 체크인한다
- 친구(제3자 앱)가 네 방에 있는 책을 가져와야 한다
- 너는 **방 마스터키(비밀번호)를 주는 대신**, 프론트에서 **"이 사람은 오늘 오후 3시까지만, 책장에만 접근 가능"이라는 제한된 카드키(Access Token)를 발급**해준다

이것이 바로 OAuth 2.0이 하는 일이다. **비밀번호를 공유하지 않고, 필요한 권한만 위임**하는 것.

### 탄생 배경

- **OAuth 1.0** (2007): 복잡한 서명(Signature) 메커니즘이 구현 부담
- **OAuth 2.0** (2012): OAuth 1.0과 **완전히 새로 설계** (호환되지 않음)
- **해결한 문제**: 제3자 앱에 비밀번호를 직접 줘야 했던 위험한 관행을 제거

> **핵심 키워드**: `Authorization`, `Access Token`, `Grant Type`, `Scope`, `Resource Owner`, `RFC 6749`

---

## 2. 핵심 개념 (Core Concepts)

```
┌─────────────────────────────────────────────────────────────┐
│                  OAuth 2.0 핵심 4대 역할                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  👤 Resource Owner          🖥️  Client                      │
│  (사용자 = 너)               (제3자 앱 = Notion, Figma 등)    │
│       │                          │                          │
│       ▼                          ▼                          │
│  🔐 Authorization Server    📦 Resource Server              │
│  (권한 서버 = Google Auth)   (자원 서버 = Google Drive API)   │
│  - 사용자 인증               - 보호된 자원 호스팅              │
│  - 동의 확인                 - Access Token 검증              │
│  - 토큰 발급                 - 데이터 응답                    │
└─────────────────────────────────────────────────────────────┘
```

| 구성 요소 | 역할 | 현실 비유 |
|-----------|------|----------|
| **Resource Owner** | 보호된 자원의 소유자 (사용자) | 호텔 방 주인 |
| **Client** | 자원에 접근하려는 제3자 앱 | 책을 가져와야 하는 친구 |
| **Authorization Server** | 사용자 인증 + Access Token 발급 | 호텔 프론트 데스크 |
| **Resource Server** | 보호된 자원 호스팅 + 토큰 검증 | 호텔 방 (카드키로 출입) |

### 주요 개념

| 개념 | 설명 | 비유 |
|------|------|------|
| **Access Token** | 보호된 자원 접근 자격 증명 | 제한된 카드키 |
| **Refresh Token** | AT 만료 시 재발급 토큰 | 카드키 재발급 쿠폰 |
| **Scope** | 접근 권한 범위 (read:email 등) | "책장만 접근 가능" |
| **Grant Type** | Token을 얻는 방법 종류 | 카드키 발급 방법 |
| **Authorization Code** | 임시 일회용 코드 → AT로 교환 | 프론트 임시 번호표 |
| **Redirect URI** | 인가 후 사용자를 되돌려보내는 URL | 카드키 전달 주소 |

---

## 3. 아키텍처와 동작 원리

### Authorization Code Flow (가장 안전한 흐름)

```
┌──────────┐                                    ┌──────────────────┐
│  👤 User │  (1) 로그인 버튼 클릭                │  🖥️  Client App   │
│ (브라우저)│ ──────────────────────────────────► │  (예: Notion)     │
│          │  (2) Auth Server로 리다이렉트        │                  │
│          │ ◄────────────────────────────────── │                  │
└────┬─────┘                                    └────────┬─────────┘
     │                                                   │
     │  (3) 로그인 + 동의 화면                             │
     ▼                                                   │
┌──────────────────┐                                     │
│  🔐 Authorization │  (4) Authorization Code 발급        │
│     Server       │ ──► User → redirect_uri ──────────►│
│  (예: Google)    │  (5) Code + Client Secret 전송       │
│                  │ ◄───────────────────────────────────│
│                  │  (6) Access Token + Refresh Token    │
│                  │ ────────────────────────────────────►│
└──────────────────┘                                     │
                                                         │
┌──────────────────┐  (7) Access Token으로 API 호출       │
│  📦 Resource     │ ◄───────────────────────────────────│
│     Server       │  (8) 보호된 데이터 응답               │
│                  │ ────────────────────────────────────►│
└──────────────────┘                                     │
```

### 동작 흐름

1. **사용자가 로그인 클릭** → Client가 Auth Server로 리다이렉트
   ```
   https://accounts.google.com/o/oauth2/v2/auth
     ?client_id=app_123&response_type=code
     &redirect_uri=https://app.com/callback
     &scope=email+profile&state=xyz_random
   ```
2. **사용자 인증 + 동의** → Google 로그인 + 동의 화면
3. **Authorization Code 발급** → `https://app.com/callback?code=abc123&state=xyz_random`
4. **Code → Token 교환** (서버 간 통신, 브라우저에 안 보임)
5. **API 호출**: `Authorization: Bearer ya29.a0AfH6SM...`

### 왜 안전한가?
- Authorization Code는 브라우저를 통하지만, 그것만으론 아무것도 못 함
- Access Token은 서버 간(Back-channel)에서만 교환 → 브라우저에 미노출
- Client Secret이 서버에서만 사용

### Grant Types

| Grant Type | 용도 |
|-----------|------|
| Authorization Code + PKCE | 소셜 로그인, 모바일/SPA (가장 권장) |
| Client Credentials | 서버 간 통신 |
| Device Code | 키보드 없는 IoT/TV |
| ~~Implicit~~ | **폐지 예정** (OAuth 2.1에서 제거) |

---

## 4. 유즈 케이스 & 베스트 프랙티스

### 대표 유즈 케이스

| # | 유즈 케이스 | 적합한 Grant Type |
|---|------------|------------------|
| 1 | **소셜 로그인** (Google/GitHub/Kakao) | Authorization Code + PKCE |
| 2 | **API 접근 위임** (캘린더 읽기) | Authorization Code |
| 3 | **서버 간 통신** | Client Credentials |
| 4 | **모바일/SPA 앱** | Authorization Code + PKCE |
| 5 | **IoT 디바이스** | Device Code |

### 베스트 프랙티스

1. **항상 PKCE를 사용하라**: OAuth 2.1에서 필수화
2. **HTTPS 필수**: 모든 OAuth 2.0 통신은 TLS 위에서
3. **Scope를 최소화하라**: 필요한 권한만 요청
4. **state 파라미터 필수**: CSRF 공격 방지
5. **Token을 안전하게 저장**: LocalStorage 금지 → HttpOnly Cookie

---

## 5. 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ 장점 | **비밀번호 비공유** | 제3자 앱에 비밀번호 전달 불필요 |
| ✅ 장점 | **세밀한 권한 제어** | Scope로 읽기/쓰기 등 세밀하게 제한 |
| ✅ 장점 | **토큰 만료** | 탈취되어도 피해 범위 제한 |
| ✅ 장점 | **권한 철회 가능** | 언제든 제3자 앱 접근 취소 |
| ✅ 장점 | **업계 표준** | Google, GitHub, Kakao 등 모두 채택 |
| ❌ 단점 | **구현 복잡도** | Grant Type, 토큰 관리, 리다이렉트 처리 |
| ❌ 단점 | **스펙 유연성 = 혼란** | 구현마다 미묘하게 다를 수 있음 |
| ❌ 단점 | **인증은 아님** | OAuth 2.0은 인가만. 인증 → OIDC 추가 필요 |
| ❌ 단점 | **구현 실수에 취약** | redirect_uri 검증 누락 = 보안 취약점 |

---

## 6. 차이점 비교

| 비교 기준 | OAuth 2.0 | OAuth 1.0 | SAML | OIDC |
|-----------|----------|-----------|------|------|
| **핵심 목적** | 인가 | 인가 | 인증 | 인증 |
| **발표 연도** | 2012 | 2007 | 2005 | 2014 |
| **데이터 형식** | JSON | 서명 파라미터 | XML | JWT |
| **전송 프로토콜** | HTTPS 필수 | HTTP + 서명 | HTTP/SOAP | HTTPS |
| **모바일 지원** | 우수 | 제한적 | 어려움 | 우수 |

### 핵심 차이

```
OAuth 2.0                        OpenID Connect (OIDC)
──────────────────────    vs    ──────────────────────
"이 앱이 뭘 할 수 있나"           "이 사람이 누구인가"
인가 (Authorization)              인증 (Authentication)
Access Token 발급                 ID Token (JWT) 추가 발급
```

---

## 7. 사용 시 주의점

| # | 실수 | 올바른 접근 |
|---|------|------------|
| 1 | redirect_uri 검증 누락 | 정확한 문자열 매칭 whitelist |
| 2 | state 파라미터 미사용 | 요청마다 랜덤 state → 콜백에서 검증 |
| 3 | Implicit Grant 사용 | Authorization Code + PKCE |
| 4 | 과도한 Scope 요청 | 최소 필요 권한만 |
| 5 | Token을 LocalStorage에 저장 | HttpOnly Secure Cookie |

### Anti-Patterns
- **"OAuth로 인증한다"는 착각**: OAuth 2.0은 인가 프레임워크. 인증 → OIDC 필요
- **Client Secret을 프론트엔드에 노출**: Public Client → PKCE 사용
- **Access Token을 URL 파라미터로 전달**: Authorization 헤더 사용

---

## 8. 개발자 도구

| 도구/라이브러리 | 언어/플랫폼 | 용도 |
|---------------|-----------|------|
| **Authlib** | Python | OAuth 클라이언트/서버 구현 |
| **Passport.js** | Node.js | Express용 OAuth 미들웨어 |
| **NextAuth.js** | Next.js | React/Next.js 인증 |
| **Auth0** | SaaS | 관리형 OAuth/OIDC 서비스 |
| **Keycloak** | Java | 오픈소스 IAM 서버 |

### 트렌드
- **OAuth 2.1**: PKCE 필수, Implicit 제거, RT Rotation 기본
- **GNAP**: OAuth의 차세대 후보
- **Passkey/FIDO2**: 비밀번호 없는 인증과 결합 확산

---

## Sources

1. [RFC 6749 - The OAuth 2.0 Authorization Framework](https://datatracker.ietf.org/doc/html/rfc6749)
2. [Auth0 - Authorization Code Flow](https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow)
3. [Auth0 - Which OAuth 2.0 Flow Should I Use?](https://auth0.com/docs/get-started/authentication-and-authorization-flow/which-oauth-2-0-flow-should-i-use)
4. [Okta - OAuth vs OpenID Connect vs SAML](https://www.okta.com/identity-101/whats-the-difference-between-oauth-openid-connect-and-saml/)
5. [Doyensec - Common OAuth Vulnerabilities](https://blog.doyensec.com/2025/01/30/oauth-common-vulnerabilities.html)
6. [OAuth 2.0 Simplified - Aaron Parecki](https://aaronparecki.com/oauth-2-simplified/)

---

> **관련 문서**: [[sso-concept-explainer]], [[oauth1-concept-explainer]], [[sso-oauth-comparison-and-architecture]]
