---
tags: [security, oauth, oauth1, authentication, authorization, hmac-sha1, concept-explainer]
created: 2026-04-09
---

# OAuth 1.0 — Concept Deep Dive

> **한줄 요약**: OAuth 1.0은 사용자의 비밀번호를 제3자 앱에 알려주지 않고도, 그 앱이 사용자 대신 데이터를 사용할 수 있게 해주는 **위임 인증(Delegated Authorization) 프로토콜**이다.

---

## 1. 무엇인가? (What is it?)

**OAuth 1.0**은 **Open Authorization**의 약자로, 2007년에 처음 발표된 개방형 인증 위임 프로토콜이다. 이후 보안 취약점을 보완한 **OAuth 1.0a**가 2009년에 나왔고, 2010년 [RFC 5849](https://datatracker.ietf.org/doc/html/rfc5849)로 표준화되었다.

### 탄생 배경

2007년 이전에는, 만약 "사진 인쇄 서비스"가 Flickr에 있는 내 사진을 가져오려면 **내 Flickr 아이디와 비밀번호를 직접 알려줘야** 했다. 이것은 마치 **집 열쇠를 택배 기사에게 주면서 "냉장고에서 우유만 꺼내 주세요"라고 하는 것**과 같았다.

OAuth 1.0은 이 문제를 해결하기 위해 Twitter의 Blaine Cook, Google의 Chris Messina 등이 협력하여 만들었다. **비밀번호를 공유하지 않고도** 제3자 앱이 사용자 데이터에 접근할 수 있는 표준 방법을 제공한다.

> **비유**: OAuth 1.0은 **호텔 카드키**와 비슷하다. 마스터키(비밀번호)를 주는 대신, 특정 방만 열 수 있는 카드키(토큰)를 발급해주는 것이다.

> **핵심 키워드**: `Delegated Authorization`, `Consumer/Provider`, `Request Token`, `Access Token`, `HMAC-SHA1 Signature`, `Nonce`, `Three-Legged Flow`

---

## 2. 핵심 개념 (Core Concepts)

OAuth 1.0을 이해하려면 **3명의 등장인물**과 **4개의 핵심 자격 증명**을 먼저 알아야 한다.

### 3명의 등장인물 (Three Parties)

```
┌──────────────────────────────────────────────────────────────┐
│                   OAuth 1.0 등장인물                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐     신뢰 위임     ┌──────────────┐            │
│  │  User     │ ──────────────► │  Consumer     │            │
│  │ (Resource │     (허가증)     │ (Third-party  │            │
│  │  Owner)   │ ◄────────────── │  App)         │            │
│  └─────┬─────┘   토큰 발급     └──────┬────────┘            │
│        │                               │                     │
│        │  "이 앱이 내 데이터를          │  서명된 요청        │
│        │   사용해도 됩니다"             │  (Signed Request)   │
│        ▼                               ▼                     │
│  ┌──────────────────────────────────────────┐               │
│  │         Service Provider                  │               │
│  │  (Twitter, Flickr 등 데이터 보유 서비스)   │               │
│  └──────────────────────────────────────────┘               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

| 등장인물 | 역할 | 현실 비유 |
|----------|------|-----------|
| **User (Resource Owner)** | 데이터의 실제 주인 | 집 주인 |
| **Consumer (Client)** | 사용자 데이터를 사용하려는 제3자 앱 | 배달 기사 |
| **Service Provider** | 사용자 데이터를 보관하는 서비스 | 아파트 경비실 + 집 |

### 4개의 핵심 자격 증명 (Credentials)

| 자격 증명 | 구성 | 비유 | 수명 |
|-----------|------|------|------|
| **Consumer Key + Secret** | 앱 등록 시 발급받는 고유 ID + 비밀키 | 배달 회사 사업자등록증 | 영구 |
| **Request Token + Secret** | 인증 과정 중 임시로 사용하는 토큰 | 임시 방문증 | 약 24시간 |
| **Access Token + Secret** | 인증 완료 후 실제 API 호출에 사용하는 토큰 | 정식 출입 카드키 | 장기간 (수개월~영구) |
| **oauth_verifier** | 사용자가 "허가"했음을 증명하는 일회용 코드 | 경비실에서 받는 확인 도장 | 일회용 |

### 핵심 보안 요소

- **Nonce (Number used ONCE)**: 매 요청마다 생성하는 고유 난수. **Replay Attack 방지**.
- **Timestamp**: 요청 시각을 포함하여, 너무 오래된 요청은 거부.
- **Signature**: 모든 요청 파라미터를 암호화 서명하여 **중간자 변조(Tampering) 방지**.

---

## 3. 아키텍처와 동작 원리 (Architecture & How it Works)

### Three-Legged Authorization Flow

```
┌─────────┐          ┌─────────────┐          ┌──────────────────┐
│  User   │          │  Consumer   │          │ Service Provider │
│ (사용자) │          │ (제3자 앱)   │          │ (Twitter 등)     │
└────┬────┘          └──────┬──────┘          └────────┬─────────┘
     │                      │                          │
     │   1. 앱 사용 시작     │                          │
     │ ──────────────────► │                          │
     │                      │  2. Request Token 요청   │
     │                      │ ────────────────────────►│
     │                      │  3. Request Token 발급   │
     │                      │ ◄────────────────────────│
     │  4. 사용자를 Provider │                          │
     │     로그인 페이지로   │                          │
     │ ◄───── 리다이렉트 ───│                          │
     │  5. 로그인 + "허가" 버튼 클릭                    │
     │ ─────────────────────────────────────────────►  │
     │  6. oauth_verifier와 함께                       │
     │     Consumer로 리다이렉트                        │
     │ ──────────────────► │                          │
     │                      │  7. Access Token 교환    │
     │                      │ ────────────────────────►│
     │                      │  8. Access Token 발급    │
     │                      │ ◄────────────────────────│
     │                      │  9. API 호출 (서명 포함)  │
     │                      │ ────────────────────────►│
     │                      │  10. 데이터 응답          │
     │                      │ ◄────────────────────────│
     │  11. 결과 표시        │                          │
     │ ◄───────────────────│                          │
```

### HMAC-SHA1 서명 메커니즘 (핵심 보안 요소)

OAuth 1.0에서 **모든 요청은 반드시 서명(Signature)이 포함**되어야 한다.

> **비유**: HMAC-SHA1 서명은 **봉투에 밀랍 도장을 찍는 것**과 같다. 편지(요청) 내용이 바뀌면 도장(서명)이 맞지 않게 된다.

#### 서명 생성 3단계

**1단계: Signature Base String 조립**
```
Signature Base String = HTTP메서드 + "&" + URL(인코딩) + "&" + 파라미터(인코딩)
```

**2단계: Signing Key 조립**
```
Signing Key = Consumer Secret + "&" + Token Secret
```

> **주의**: Token Secret이 아직 없는 경우(Request Token 요청 시)에도 `&`는 반드시 포함한다.

**3단계: HMAC-SHA1 해싱 + Base64 인코딩**
```python
import hmac, hashlib, base64

key = "consumer_secret&token_secret"
base_string = "POST&https%3A%2F%2Fapi.twitter.com%2F..."
hashed = hmac.new(key.encode(), base_string.encode(), hashlib.sha1)
signature = base64.b64encode(hashed.digest()).decode()
```

#### 서명이 보호하는 것
- ✅ 요청의 무결성 (Integrity) — 파라미터 변조 시 서명 불일치
- ✅ 요청자의 신원 (Authentication) — Consumer Secret 없이 서명 생성 불가
- ✅ 재사용 방지 (Replay Protection) — Nonce + Timestamp
- ❌ 요청 본문 암호화 (Encryption) — 서명은 암호화가 아님! (HTTPS의 역할)

---

## 4. 유즈 케이스 & 베스트 프랙티스

### 대표 유즈 케이스

| # | 유즈 케이스 | 설명 |
|---|------------|------|
| 1 | **Twitter API (v1.1)** | 가장 대표적인 OAuth 1.0a 구현체 |
| 2 | **Flickr 사진 접근** | OAuth가 처음 탄생한 배경 자체 |
| 3 | **Tumblr API** | HTTP 환경에서도 서명으로 보안 유지 |
| 4 | **레거시 시스템 통합** | 기존 OAuth 1.0 인프라 호환 |

### 베스트 프랙티스

1. **라이브러리를 사용하라**: 서명 생성을 직접 구현하지 말 것
2. **Consumer Secret을 안전하게 보관하라**: 환경 변수나 Secret Manager 사용
3. **Nonce를 충분히 무작위로 생성하라**: UUID v4 수준
4. **HTTPS를 함께 사용하라**: 서명으로 무결성은 보장하지만, 본문 암호화는 HTTPS가 담당

---

## 5. 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ 장점 | **HTTP에서도 안전** | HTTPS 없이도 서명으로 요청 무결성을 보장 |
| ✅ 장점 | **비밀번호 미공유** | 사용자 비밀번호를 제3자 앱에 전혀 노출하지 않음 |
| ✅ 장점 | **Replay Attack 방지** | Nonce + Timestamp 조합으로 동일 요청 재전송 차단 |
| ✅ 장점 | **요청 변조 탐지** | 모든 파라미터가 서명에 포함 |
| ❌ 단점 | **구현 난이도 극상** | 서명 생성 로직이 매우 복잡 |
| ❌ 단점 | **디버깅 지옥** | 서명 불일치 시 어디서 틀렸는지 찾기 매우 어려움 |
| ❌ 단점 | **모바일/SPA 비적합** | Consumer Secret을 클라이언트에 안전하게 보관하기 어려움 |
| ❌ 단점 | **확장성 제한** | Auth Server와 Resource Server 역할 미분리 |

---

## 6. 현재 상태

**사실상 사용 중단 (Deprecated)**. Twitter마저 2023년에 OAuth 2.0으로 전환하면서, OAuth 1.0을 사용하는 주요 플랫폼은 사실상 없다.

학습 가치: 직접 구현할 일은 없지만, **서명 기반 인증의 원리(HMAC, Nonce, Timestamp)**를 이해하면 API 보안 전반에 대한 이해도가 크게 높아진다.

---

## 7. 사용 시 주의점

| # | 실수 | 올바른 접근 |
|---|------|------------|
| 1 | 서명을 직접 구현 | `requests-oauthlib` 등 검증된 라이브러리 사용 |
| 2 | Consumer Secret 하드코딩 | 환경 변수, Vault, Secret Manager 사용 |
| 3 | Nonce 재사용 | UUID v4 또는 cryptographic random 사용 |
| 4 | OAuth 1.0 원본 사용 | 반드시 OAuth 1.0a 이상 (Session Fixation 취약점 패치) |
| 5 | 새 프로젝트에 OAuth 1.0 도입 | OAuth 2.0 + PKCE 사용 |

---

## 8. 개발자 도구

| 도구/라이브러리 | 언어/플랫폼 | 용도 |
|---------------|-----------|------|
| `requests-oauthlib` | Python | OAuth 1.0 서명 자동 처리 |
| `Authlib` | Python | OAuth 1.0/2.0 통합 라이브러리 |
| `oauth-1.0a` | Node.js | HMAC-SHA1/SHA256 서명 생성 |
| Postman | 크로스 플랫폼 | OAuth 1.0 서명 테스트/디버깅 |

---

## Sources

1. [RFC 5849 - The OAuth 1.0 Protocol](https://datatracker.ietf.org/doc/html/rfc5849)
2. [OAuth Core 1.0 Revision A](https://oauth.net/core/1.0a/)
3. [Signing Requests | OAuth1](https://oauth1.wp-api.org/docs/basics/Signing.html)
4. [Creating a signature - X Developer](https://developer.x.com/en/docs/authentication/oauth-1-0a/creating-a-signature)
5. [Differences Between OAuth 1 and 2](https://www.oauth.com/oauth2-servers/differences-between-oauth-1-2/)
