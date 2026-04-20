---
tags: [http, status-code, rate-limiting, nginx, prg-pattern, retry]
created: 2026-04-20
---

# HTTP Status Code 429 & 303 완전 가이드

> ⚠️ Rate Limit 수치는 서비스별로 수시 변경됩니다. 아래 수치는 참고용이며, 반드시 공식 문서에서 최신 값을 확인하세요.

## 📊 개요

| 코드   | 이름              | 카테고리          | 한마디 요약                         |
| ------ | ----------------- | ----------------- | ----------------------------------- |
| **429** | Too Many Requests | 4xx (클라이언트 에러) | "너무 많이 요청했어, 좀 쉬어!"       |
| **303** | See Other         | 3xx (리다이렉션)    | "결과는 다른 곳에 있어, 거기로 가!" |

---

## 🔴 429 - Too Many Requests

### 뭔가요?

서버가 **"주어진 시간 내에 너무 많은 요청을 보냈다"** 고 요청을 제한하는 응답이다. RFC 6585 원문: *"The user has sent too many requests in a given amount of time."* 서버가 처리 *불가능*한 게 아니라, 클라이언트가 너무 많이 보냈으므로 **처리를 거부**하는 것이다 (4xx = 클라이언트 측 문제).

### 🧒 비유

놀이공원 매표소에서 한 사람이 계속 "표 주세요! 표 주세요!" 하면 직원이 **"잠깐만요, 너무 빨리 오시네요. 5분 후에 다시 오세요"** 라고 하는 것과 같다.

### 왜 발생하나요?

```
[클라이언트] --요청1--> [서버]  ✅ OK
[클라이언트] --요청2--> [서버]  ✅ OK
[클라이언트] --요청3--> [서버]  ✅ OK
[클라이언트] --요청4--> [서버]  ❌ 429! (Rate Limit 초과)
```

- **Rate Limiting (속도 제한)**: API가 "1분에 60번까지만 허용"처럼 제한을 걸어둠
- **서버 과부하 방지**: 한 사용자가 서버 자원을 독점하지 못하게 보호
- **비용 제어**: 유료 API에서 과도한 호출 방지

### 흔한 사례

- ChatGPT / Claude API 호출 한도 초과
- GitHub API rate limit 초과
- AWS API throttling

### 얼마나 자주 보내야 429가 뜨나?

**서비스마다 완전히 다르다.** 정해진 표준 없이 각 서비스가 자체 설정하며, 수시로 변경될 수 있다.

| 서비스                | Rate Limit (참고, 변경 가능)    | 기준                          |
| --------------------- | ------------------------------- | ----------------------------- |
| Claude API (Free)     | ~5 RPM (Requests Per Minute)    | API Key당, 모델별 상이        |
| GitHub API (인증)     | 5,000 req/hour                  | 토큰당 (PAT/App별 차이 있음)  |
| GitHub API (미인증)   | 60 req/hour                     | IP당                          |
| X(Twitter) API        | tier/엔드포인트별 상이          | 2023년 유료화 이후 대폭 변경  |

> 핵심: **"얼마나 자주"가 아니라 "서비스가 몇으로 설정했냐"**가 답이다. 구체적 수치는 반드시 **각 서비스의 공식 문서**에서 확인하라.

---

## 🏗️ Rate Limiting 아키텍처: 어디서 제한을 거나?

**Nginx, API Gateway, Application 모두 가능하고, 보통 이중 레이어로 쓴다.**

```
[클라이언트]
     ↓ 요청
┌─────────────────────────────────────┐
│  🔒 Layer 1: Nginx (인프라 레벨)      │  ← 무차별 폭탄 차단
│  "IP당 초당 10개까지"                  │
├─────────────────────────────────────┤
│  🔒 Layer 2: API Gateway             │  ← API Key별 플랜 적용 (선택)
│  "Free 플랜은 분당 60개"              │
├─────────────────────────────────────┤
│  🔒 Layer 3: Application (앱 레벨)    │  ← 비즈니스 로직 기반
│  "이 유저는 분당 100개, 이 엔드포인트는 10개" │
└─────────────────────────────────────┘
```

### 🧒 비유

- **Nginx(게이트 직원)**: "1분에 10명까지만 입장!" → 초과하면 바로 돌려보냄
- **Application(안내데스크)**: "이 회원은 VIP니까 1분에 100명, 일반은 10명" → 더 세밀한 규칙

| 레이어                              | 역할                                     | 예시                             |
| ----------------------------------- | ---------------------------------------- | -------------------------------- |
| **Nginx**                           | 인프라 보호 (DDoS 방어 수준)             | IP당 초당 N개                    |
| **API Gateway** (Kong, AWS API GW 등) | 플랜/키별 제한                           | Free vs Pro 차등                 |
| **Application** (코드)              | 비즈니스 로직 기반 세밀한 제어           | 유저별, 엔드포인트별, 시간대별   |

### Nginx Rate Limiting 설정

> 아래는 **기본(vanilla) Nginx** 기준이다. OpenResty/lua-nginx-module 환경에서는 더 동적인 제어가 가능하다.

```nginx
# 1. rate limit zone 정의 (http 블록)
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
#              ^^^^^^^^^^^^^^^^    ^^^^^^^^^^  ^^^^^^^^^
#              IP 기준              zone 이름    초당 10개

# 2. 적용 (server/location 블록)
location /api/ {
    limit_req zone=api burst=20 nodelay;
    #              ^^^^^^^^ ^^^^^^
    #              순간 버스트 20개 허용   대기 없이 즉시 처리/거부

    # 429 반환 설정 (기본은 503)
    limit_req_status 429;

    proxy_pass http://backend;
}
```

---

## ⏱️ Retry-After 헤더: 이론 vs 현실

### Retry-After는 어디서 넣나?

| 방식                           | Retry-After | 동적 계산 | 예시                                 |
| ------------------------------ | :---------: | :-------: | ------------------------------------ |
| **Nginx limit_req** (기본)     |      ❌      |     ❌     | 고정값만 수동 추가 가능              |
| **API Gateway** (Kong, AWS 등) |      ✅      |     ✅     | rate limit 플러그인에 내장           |
| **Application 레벨**           |      ✅      |     ✅     | Redis 기반 정확한 잔여 시간 계산     |

> **기본 Nginx의 `limit_req`는 `Retry-After` 헤더를 자동으로 넣어주지 않는다.** 수동으로 추가하려면:

```nginx
location /api/ {
    limit_req zone=api burst=20 nodelay;
    limit_req_status 429;
    error_page 429 = @rate_limited;
}

location @rate_limited {
    add_header Retry-After 60 always;  # 수동으로 60초 고정값 추가
    return 429 '{"error": "Too Many Requests"}';
}
```

### 현실: Retry-After 제공 여부는 서비스마다 다르다

RFC 6585에서 Retry-After는 **MAY**(선택) 수준으로 권장한다. 실제 제공 여부는 서비스마다 갈린다:

| 서비스       | Retry-After 제공 | 비고                          |
| ------------ | :--------------: | ----------------------------- |
| GitHub API   |        ✅         | secondary rate limit에서 제공 |
| Stripe API   |        ✅         | SDK 내부에서 자동 활용        |
| OpenAI API   |        ✅         | 429 응답에 포함               |
| Azure        |        ✅         | 표준 제공                     |
| Cloudflare   |        ✅         | 429 응답에 포함               |
| AWS API      |        ❌         | 대부분 미제공                 |

### 업계 표준: Exponential Backoff + Jitter

Retry-After 헤더가 있든 없든, 클라이언트 측 재시도 전략의 표준은 **Exponential Backoff + Jitter**다. AWS와 Google이 공식 권장한다.

```
[이론]  429 → Retry-After 확인 → 그만큼 대기
[현실]  429 → Exponential Backoff + Jitter → 알아서 대기
                                    ↑
                               이게 업계 표준
```

```python
import time
import random

def call_api_with_retry(url, max_retries=5):
    for attempt in range(max_retries):
        response = requests.get(url)

        if response.status_code != 429:
            return response

        # 실무 패턴: Exponential Backoff + Jitter
        base_delay = min(2 ** attempt, 60)  # 1, 2, 4, 8, 16, 최대 60초
        jitter = random.uniform(0, base_delay * 0.5)
        wait = base_delay + jitter

        # Retry-After가 있으면 참고는 하되 (있는 경우가 드물지만)
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            wait = max(wait, int(retry_after))  # 더 큰 값 사용

        time.sleep(wait)

    raise Exception("Max retries exceeded")
```

**Jitter(랜덤)가 중요한 이유**: 여러 클라이언트가 동시에 재시도하면 또 429가 터짐 → 랜덤으로 분산시킨다.

> 💡 **사전 방지도 가능하다**: `X-RateLimit-Remaining` 같은 응답 헤더를 모니터링하면 429가 터지기 전에 요청 속도를 자체 조절할 수 있다.

---

## 🟡 303 - See Other

### 뭔가요?

서버가 **"요청은 처리했는데, 결과는 다른 URL에서 GET으로 가져가"** 라고 알려주는 응답이다.

### 🧒 비유

편의점에서 택배를 맡기면(POST) 직원이 **"접수 완료! 송장 번호는 저기 화면에서 확인하세요"** 라고 다른 곳을 가리키는 것과 같다.

### 동작 흐름

```
[클라이언트] --POST /orders--> [서버]     (주문 생성 요청)
     ↓
[서버] 303 See Other
       Location: /orders/12345              (결과 확인 URL 안내)
     ↓
[클라이언트] --GET /orders/12345--> [서버]  (자동으로 이동)
     ↓
[서버] 200 OK + 주문 상세 정보              ✅
```

### 303의 사용 빈도

| 상황                                 | 사용 빈도   | 설명                                                              |
| ------------------------------------ | :---------: | ----------------------------------------------------------------- |
| 전통적 웹 앱 (서버 사이드 렌더링)    | ⭐⭐⭐⭐⭐ | PRG 패턴의 핵심. Rails, Django, Spring MVC 등에서 사용             |
| REST API                            | ⭐          | 거의 안 씀. POST 후 `201 Created` + `Location` 헤더가 표준        |
| SPA (React, Vue 등)                 | ⭐          | 프론트엔드가 직접 상태 관리하므로 불필요                          |
| OAuth / 인증 흐름                    | ⭐⭐⭐      | 로그인 후 원래 페이지로 돌려보낼 때 간혹 사용                     |

---

## 🔄 PRG 패턴 (Post/Redirect/Get) 심화

### 핵심 원리: 브라우저는 "마지막 요청"을 기억한다

> ⚠️ 아래 설명은 **전통적 MPA(Multi-Page Application)/SSR 환경**에서의 동작이다. SPA(React, Vue 등)에서는 새로고침 시 초기 HTML에 대한 GET만 재요청되며, 이전 API 호출(fetch/XHR)은 재전송되지 않는다.

전통적 폼 제출 환경에서 새로고침 = **마지막으로 보낸 요청을 그대로 다시 보내는 것**이다. 폼의 input 값이 다시 채워지는 것과는 별개로, **브라우저가 내부적으로 POST 요청 데이터를 기억하고 있다가 그대로 재전송**한다.

### ❌ PRG 없는 경우 (중복 제출 발생)

```
1. 사용자: POST /order (치킨 1마리 주문)
2. 서버:   200 OK "주문 완료!" 페이지 직접 반환
3. 브라우저의 마지막 요청 = POST /order  ← 이게 핵심!

4. 사용자: F5 (새로고침)
5. 브라우저: "마지막 요청을 다시 보낼게" → POST /order 재전송!
6. 서버: 치킨 1마리 또 주문 접수됨 😱
```

> 이때 브라우저가 **"양식을 다시 제출하시겠습니까?"** 라는 경고 팝업을 보여준다.

### ✅ PRG 패턴 적용한 경우 (중복 제출 방지)

```
1. 사용자: POST /order (치킨 1마리 주문)
2. 서버:   303 See Other → Location: /order/result/123
3. 브라우저: 자동으로 GET /order/result/123 요청
4. 서버:   200 OK "주문 완료!" 페이지 반환
5. 브라우저의 마지막 요청 = GET /order/result/123  ← POST가 아님!

6. 사용자: F5 (새로고침)
7. 브라우저: "마지막 요청을 다시 보낼게" → GET /order/result/123
8. 서버: 결과 페이지만 다시 보여줌 ✅ (주문 중복 없음)
```

### 흐름 비교

```
PRG 없이                          PRG 적용
──────────                        ──────────
POST /order ─┐                    POST /order ─┐
             ↓                                 ↓
       200 "완료!"                       303 → /result/123
             ↓                                 ↓
       F5 = POST 재전송 💥              GET /result/123 → 200 "완료!"
                                               ↓
                                         F5 = GET 재전송 ✅
```

### 302 vs 303 vs 307: PRG에서의 리다이렉트 코드 선택

PRG 패턴에서 의미적으로 가장 정확한 코드는 **303**이지만, 실무 프레임워크의 기본값은 대부분 **302**이다.

| 코드    | RFC 명세                       | 브라우저 실제 동작                        | PRG 적합성                       |
| ------- | ------------------------------ | ----------------------------------------- | -------------------------------- |
| **302** | 원래 메서드 유지               | POST → GET으로 변환 (명세와 다름)         | ⚠️ 동작은 하지만 명세상 부정확    |
| **303** | 명시적으로 GET으로 전환        | POST → GET으로 전환                       | ✅ 의미적으로 정확                |
| **307** | 원래 메서드 유지               | POST → POST 유지 (명세대로)               | ❌ PRG 목적에 부적합              |

```
302의 현실: 명세 ≠ 구현
┌─────────────────────────────────┐
│  RFC 7231 says:  "302는 메서드 유지"  │
│  Browsers do:    "302도 GET으로 변환"  │
│  결과:           303과 사실상 동일     │
└─────────────────────────────────┘
```

| 프레임워크  | 기본 리다이렉트 코드 | 303 사용 방법                                       |
| ----------- | :------------------: | --------------------------------------------------- |
| Ruby on Rails |         302          | `redirect_to url, status: :see_other`               |
| Django        |         302          | `HttpResponseSeeOther` (4.2+)                       |
| Spring MVC    |         302          | `return new ResponseEntity<>(HttpStatus.SEE_OTHER)` |
| Express.js    |         302          | `res.redirect(303, url)`                            |

> 303이 "올바른" 선택이지만, 302도 브라우저에서 동일하게 동작한다. 프레임워크 기본값이 302인 코드를 보더라도 PRG가 깨지는 것은 아니다.

---

## 🔬 실제 사례: deep-research에서의 303 에러

### 발생 상황

```
⏺ Fetch(https://www.nature.com/articles/s41598-025-02149-x)
  ⎿  Error: Request failed with status code 303

⏺ Fetch(https://link.springer.com/article/10.1007/s10462-025-11397-2)
  ⎿  Error: Request failed with status code 303

⏺ Springer/Nature 403 — WebSearch 캐시로 대체합니다.
```

### 원인: 브라우저 vs WebFetch의 차이

브라우저로 접속하면 논문이 정상 표시되는데 WebFetch에서는 303 에러가 나는 이유:

```
[브라우저 접속 시]
GET /articles/...
  → 서버: User-Agent 확인 → "브라우저네"
  → 쿠키 기반 세션 생성
  → 303 → consent/preview 페이지
  → 브라우저가 자동으로 따라감
  → 200 OK + 논문 내용 표시 ✅

[WebFetch 접속 시]
GET /articles/...
  → 서버: User-Agent 확인 → "봇이네" 🤖
  → 303 → 인증/제한 페이지로 리다이렉트
  → WebFetch: 따라가지 못함 → Error ❌
```

| 요소                  | 브라우저                | WebFetch |
| --------------------- | :---------------------: | :------: |
| 쿠키/세션 관리        |           ✅            |    ❌     |
| JavaScript 실행       |           ✅            |    ❌     |
| 리다이렉트 체인 추적  |           ✅            | 제한적   |
| Bot 감지 우회         |   ✅ (사람으로 인식)    |    ❌ (봇으로 인식)    |
| CAPTCHA 처리          |           ✅            |    ❌     |

Nature/Springer는 **Open Access 논문이라도** 봇 접근 시에는 동의 페이지나 인증 흐름을 거치게 하는 경우가 많다. deep-research 스킬은 이를 인지하고 **WebSearch 캐시로 자동 대체**하여 처리한다.

---

## 🔑 핵심 정리

1. **429 (Too Many Requests)**: 서비스별 Rate Limit 설정 초과 시 발생. "처리 불가"가 아닌 "처리 거부"(RFC 6585: *sent too many requests*)
2. **Rate Limit 수치는 서비스별, 시점별로 다르다**: 구체적 수치는 반드시 공식 문서에서 확인
3. **Rate Limiting은 다층 구조**: Nginx(1차 방어) + API Gateway(플랜별) + Application(세밀한 제어) 이중/삼중 레이어가 일반적
4. **Retry-After 헤더**: RFC에서 MAY(선택) 수준. 주요 API(GitHub, OpenAI, Stripe) 제공하지만 미제공 서비스(AWS)도 있음
5. **Exponential Backoff + Jitter가 클라이언트 재시도의 업계 표준**: AWS/Google 공식 권장. `X-RateLimit-Remaining` 모니터링으로 사전 방지도 가능
6. **303 (See Other)**: PRG 패턴에서 의미적으로 가장 정확한 리다이렉트 코드. 단, 실무 프레임워크(Rails, Django, Spring) 기본값은 302이며 브라우저에서 동일하게 동작
7. **PRG 패턴의 핵심** (MPA/SSR 한정): 새로고침은 폼을 다시 채우는 게 아니라, 브라우저가 마지막 HTTP 요청 자체를 재전송. SPA에서는 해당 없음
8. **학술 사이트 303 에러**: 브라우저와 WebFetch의 근본적 차이(쿠키, JS, User-Agent)로 인한 봇 차단
