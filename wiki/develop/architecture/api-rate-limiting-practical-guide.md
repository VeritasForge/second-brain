---
tags: [rate-limiting, slowapi, nginx, fastapi, api-design, security]
created: 2026-05-30
---

# 🚦 API Rate Limiting — 실무 가이드

> 이 문서는 FastAPI/Starlette 기반 백엔드의 rate limiting을 중심으로, 앱 레이어와 인프라 레이어를 모두 다루며 자주 빠지는 함정과 안티패턴을 정리합니다.
> 모든 주장은 공식 문서(slowapi, limits, Flask-Limiter, nginx, OWASP)로 검증된 내용입니다.

---

## 1. 🍔 Rate Limiting이 뭔가요?

### 한 줄 정의

**"누가, 얼마나 자주 호출했는지를 세서 일정 한도를 넘으면 거절하는 메커니즘"**

### 12살 비유: "햄버거 가게 줄서기"

| 상황                              | 비유                                |
| --------------------------------- | ----------------------------------- |
| 손님 1명이 1분에 햄버거 100개 주문 | 가게 마비 💥                        |
| 사장이 규칙을 만듦: **"1인당 1분에 5개까지"** | **Rate Limit**                |
| 손님을 식별하는 기준              | **IP, user_id, API key 등**         |
| 6번째 주문 → "잠시 후 다시 오세요" | **HTTP 429 Too Many Requests**     |

### 핵심 3요소

```
1. 식별 키 (Key)      — 누구인가? (IP, user_id, plan, ...)
2. 한도 (Limit)        — 얼마나? (60/minute, 100/hour, ...)
3. 시간 윈도우 (Window) — 어느 기간에? (fixed-window, sliding-window, leaky-bucket)
```

---

## 2. 🎯 왜 필요한가? — 5가지 핵심 시나리오

| #   | 시나리오                              | 예시                                                 | 위협                                          |
| --- | ------------------------------------- | ---------------------------------------------------- | --------------------------------------------- |
| **A** | 💸 **외부 API 비용 폭증 방지**         | LLM(OpenAI), 결제(Stripe), 지도, 시세 데이터          | 무한 루프 1번에 하루 1만 달러 폭탄             |
| **B** | 🔨 **DB / 시스템 자원 보호**           | 쓰기 API, 인덱스 비대화, 누적 데이터                  | "Noisy Neighbor" — 한 유저가 시스템 전체 다운  |
| **C** | 🤖 **봇 / 스크래퍼 방어**              | 카탈로그 수집, 데이터 마이닝                          | 정당한 계정으로도 비정상 사용                 |
| **D** | 🔐 **계정 탈취(ATO) 피해 최소화**      | 탈취된 JWT로 1초 100회 호출                            | 이상행동 감지 시간 확보                       |
| **E** | 💼 **비즈니스 정책 (Free vs Pro)**     | 차등 한도, SaaS 매출 모델                            | rate limit이 보안이 아닌 **수익 도구**         |

추가로:
- **F** 🔒 **brute-force 방어**: 로그인, 비밀번호 변경, OTP 검증
- **G** 📊 **트래픽 평탄화**: 갑작스러운 피크 흡수, downstream 보호

---

## 3. 🏗️ 어디서 처리할 수 있나? — 계층별 비교

```
🌐 인터넷
   │
   ▼ ① CDN / WAF                ← L7 DDoS, 봇, 지역 차단
   │   (Cloudflare, AWS Shield, Akamai)
   │
   ▼ ② API Gateway              ← API key별 throttle, usage plan
   │   (AWS API GW, Kong, Apigee, Tyk)
   │
   ▼ ③ Reverse Proxy            ← IP당 거친 한도
   │   (nginx, Envoy, HAProxy)
   │
   ▼ ④ Service Mesh             ← Pod 간 mTLS + 정책
   │   (Istio, Linkerd, Cilium)
   │
   ▼ ⑤ 애플리케이션 미들웨어     ← 비즈니스 컨텍스트 기반
   │   (slowapi, express-rate-limit, ...)
   │
   ▼ 비즈니스 로직
```

### 각 레이어의 역할

| 레이어          | 강점                              | 약점                                  |
| --------------- | --------------------------------- | ------------------------------------- |
| CDN/WAF         | 거대 DDoS, 봇 차단, anycast 분산  | per-user 정교한 한도 어려움          |
| API Gateway     | API key별 정책, 비용 계산         | 키 관리 인프라 필요                  |
| Reverse Proxy   | IP/header 기반 가볍게 거절        | 비즈니스 컨텍스트 모름                |
| Service Mesh    | 마이크로서비스 간 정책            | 운영 복잡도 ↑↑                       |
| 앱 미들웨어     | user_id, plan, 엔드포인트별 자유 | DDoS 1차 방어엔 부적합                |

> ⚠️ **잘 알려진 오해**: "Defense in Depth(다층 방어)가 정석"이라는 단정은 표준 근거가 없습니다. OWASP API Security Top 10:2023 API4(Unrestricted Resource Consumption)도 "rate limiting을 적용하라"고만 권고하고 **어느 레이어에서/몇 겹으로 적용할지는 규정하지 않습니다**. 환경(서버리스, 매니지드 게이트웨이, 단일 인스턴스)에 따라 단일 레이어로도 충분합니다.

---

## 4. 🐍 앱 레이어 — slowapi (FastAPI/Starlette)

### 4.1 기본 정보

- **출처**: [slowapi](https://github.com/laurents/slowapi) — Flask-Limiter를 FastAPI/Starlette용으로 **부분 적응(partial adaptation)** 한 라이브러리
- **백엔드**: [limits](https://limits.readthedocs.io/) 라이브러리 공유 (Flask-Limiter와 동일)
- **지원**: in-memory, Redis, Memcached, MongoDB

### 4.2 최소 설정

```python
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

# ① Limiter 만들기 — 식별 기준 정의
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()

# ② 앱에 등록
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ③ 엔드포인트에 적용
@app.get("/items")
@limiter.limit("60/minute")
def list_items(request: Request):    # ★ request 인자 필수
    ...
```

### 4.3 ⚠️ 가장 흔한 함정 4가지

#### (1) `request: Request` 인자를 빼먹음

공식 docs:
> *"The `request` argument must be explicitly passed to your endpoint, or slowapi won't be able to hook into it."*

FastAPI의 dependency injection만으로는 hook이 안 됩니다. WebSocket은 `websocket: WebSocket`으로 대체.

#### (2) 프록시 뒤에서 IP가 LB IP로 통일됨

```python
limiter = Limiter(key_func=get_remote_address)  # 직접 연결 IP만 봄
```

CDN/LB 뒤에 있으면 **모든 요청이 LB의 IP**로 보여서 글로벌 한도 하나로 수렴 (false positive 폭증).

→ `X-Forwarded-For`를 파싱하는 커스텀 `key_func` 필요:

```python
def real_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    return forwarded.split(",")[0].strip() if forwarded else get_remote_address(request)
```

⚠️ X-Forwarded-For는 **신뢰할 수 있는 LB 뒤에서만** 사용 (공격자가 임의 헤더 보낼 수 있음).

#### (3) 멀티워커 메모리 백엔드의 카운터 분리

```python
limiter = Limiter(key_func=get_remote_address)  # storage_uri 미지정 = memory://
```

`gunicorn -w 4` 또는 `uvicorn --workers 4`로 띄우면 **각 워커가 자기 카운터**만 봅니다.

> 📌 **자주 잘못 알려진 사실**: "실효 한도가 정확히 N배" → ❌ **부정확**
>
> 정확한 표현: **"최대 N배 (up to N×)"**

이론적 분석 (balls-into-bins 모델):

```
N=4 워커, 한도=100/min, 단일 IP에서 R 요청:
- 가장 무거운 워커 ≈ R/N + Θ(√(R log N / N))
- R=400이면 가장 빨리 차는 워커가 R≈340~360에서 거절 시작
- → 실효 한도 ≈ 3.4~3.6× (정확히 4× 아님)
- keep-alive sticky 연결 시 → 1×로 수렴 (단일 워커 고정)
```

추가 사실:
- gunicorn `--preload`는 해결책 아님 (fork 후 카운터 mutation은 워커별 분리)
- 단일 워커 운영 시 무관
- 정확한 글로벌 한도 필요 → **Redis 백엔드 필수**

#### (4) `key_func`을 plan/role로 잘못 설정 (P0 보안 결함)

❌ **잘못된 코드 — 실제로 자주 보는 버그**:

```python
@limiter.limit("60/minute", key_func=lambda r: get_user_plan(r))
```

**왜 위험한가**:
- `key_func`이 `"pro"` 반환 → **모든 Pro 사용자가 단일 버킷 공유**
- Pro 유저 1명이 60req/min 쓰면 **다른 모든 Pro 유저 차단**
- 더 나쁘게: **DoS amplification 보안 결함** — Free 계정 1개로 모든 Free 유저 차단 가능

✅ **올바른 패턴** — 식별자와 정책 분리:

```python
def _user_limit(request: Request) -> str:
    """정책: plan에 따라 한도값 결정"""
    plan = get_user_plan(request)
    return {"pro": "300/minute", "free": "60/minute"}.get(plan, "10/minute")

def _user_key(request: Request) -> str:
    """식별자: user_id 있으면 user별, 없으면 IP별로 격리"""
    user_id = getattr(request.state, "user_id", None)
    return f"user:{user_id}" if user_id else f"ip:{get_remote_address(request)}"

@limiter.limit(_user_limit, key_func=_user_key)
async def endpoint(request: Request): ...
```

**핵심 원칙**:
- `key_func` = **식별자** (누구인가)
- `limit string` = **정책** (얼마나 허용하는가)
- 두 개를 섞으면 안 됨

추가 고려:
- JWT decode 실패 시 anonymous 폴백 정책
- 익명 요청은 IP 키로 격리 (단일 버킷 방지)
- plan 변경 시 캐시 무효화

### 4.4 Rate Limit 문자열 문법

```
"60/minute"            → 1분에 60회
"100/hour"             → 1시간에 100회
"5/second"             → 1초에 5회
"10/minute;100/hour"   → 둘 다 동시 적용 (세미콜론, 콤마도 동작)
```

### 4.5 저장소(Storage) 선택

| Backend          | 특징                                            | 권장 시점                                  |
| ---------------- | ----------------------------------------------- | ------------------------------------------ |
| **memory://** (기본값) | 프로세스 메모리. 빠르지만 멀티 워커/재시작에 약함 | 단일 워커 개발/MVP                         |
| **redis://**     | 여러 워커·서버 간 공유 가능                     | 멀티 워커 + 정확 글로벌 한도 필요          |
| **memcached://** | 비슷                                            | Redis 미사용 환경                          |
| **mongodb://**   | 영속성                                          | 거의 안 씀                                |

Redis 백엔드 도입 시 트레이드오프:
- ➕ 정확한 글로벌 한도 보장
- ➖ Latency +0.1~5ms (네트워크 거리에 따라)
- ➖ SPOF (fail-open / fail-closed 정책 결정 필수)
- ➖ 운영 비용 (모니터링, 백업)

> ⚠️ **"프로덕션 = 무조건 Redis"는 신화입니다.** 단일 워커 또는 N배 오차 허용 가능한 abuse 방지 목적이면 memory로 충분합니다.

### 4.6 응답 헤더 (`headers_enabled=True`)

```python
limiter = Limiter(
    key_func=get_remote_address,
    headers_enabled=True,
)
```

slowapi 소스 확인 결과 정확한 동작:
- **모든 응답**에 4개 헤더 주입 (200 응답에도 `Retry-After` 포함 — RFC 7231 의미론과 다름)
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`
  - `Retry-After`
- 헤더 이름은 `Limiter` 생성자가 아닌 **app config**로만 변경:
  - `RATELIMIT_HEADER_LIMIT`
  - `RATELIMIT_HEADER_REMAINING`
  - `RATELIMIT_HEADER_RESET`
  - `RATELIMIT_HEADER_RETRY_AFTER`
  - `RATELIMIT_HEADER_RETRY_AFTER_VALUE` (`"http-date"` 또는 delta-seconds)

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 23
X-RateLimit-Reset: 1698765432
Retry-After: 37        ← 200 응답에도 붙음 (잔여 시간)
```

한도 초과 시:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60

{"error": "Rate limit exceeded: 60 per 1 minute"}
```

---

## 5. 🌐 인프라 레이어 — nginx

### 5.1 기본 문법

`/etc/nginx/nginx.conf`:

```nginx
http {
    # zone 정의: $binary_remote_addr 키, 10MB 공유 메모리, 분당 30회
    limit_req_zone $binary_remote_addr zone=general:10m rate=30r/m;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    server {
        location /api/auth/login {
            limit_req zone=login burst=2 nodelay;
            proxy_pass http://app;
        }
        location /api/ {
            limit_req zone=general burst=10 nodelay;
            proxy_pass http://app;
        }
    }
}
```

옵션 의미:
- `zone=<name>:<size>` — 공유 메모리 영역 (1MB ≈ 16,000개 키 저장 가능)
- `rate=Nr/s` 또는 `Nr/m` — 초당/분당 요청 한도
- `burst=N` — 일시적 폭주 허용량 (큐에 쌓음)
- `nodelay` — burst 큐를 통과시키되 즉시 처리 (큐에 대기 없음)

### 5.2 JWT 인증 사용자 식별 옵션

> ⚠️ **자주 잘못 알려진 사실**: "nginx는 JWT 처리 거의 안 함, Lua/OpenResty 필요" → ❌ **옵션 공간 인위 축소**

✅ **정확한 4가지 옵션** (모두 실제 사용 가능):

| 옵션                                  | 라이선스       | 특징                                                                                  |
| ------------------------------------- | -------------- | ------------------------------------------------------------------------------------- |
| **(a) njs (NGINX JavaScript)**        | 오픈소스 공식  | JS로 JWT 디코드. 서명 검증은 Web Crypto API 수동 구현                                  |
| **(b) `auth_request` 서브리퀘스트**   | 오픈소스       | 외부 인증 서비스에 위임 후 응답 헤더에서 user_id 추출. `--with-http_auth_request_module` 필요 |
| **(c) nginx-plus `auth_jwt`**         | 상용           | 1줄 디렉티브로 RS256/ES256/HS256 검증                                                  |
| **(d) OpenResty + lua-resty-jwt**     | 오픈소스       | LuaJIT 기반. 라이브러리 유지보수 활성도 낮음 (v0.1.11, 2017)                            |

### 5.3 nginx rate limit의 한계

- ❌ **L7 DDoS (botnet) 방어 부적합**: IP-based limit이라 IP 분산 공격에 무력 → CDN/WAF 영역
- ❌ **비즈니스 컨텍스트 모름**: plan, 엔드포인트별 정교한 한도 불가능
- ❌ **설정 변경 시 reload 필요**: 핫 리로드 가능하지만 코드 변경처럼 즉시 반영은 안 됨

---

## 6. ⚖️ 앱 vs 인프라 레이어 — 어디에 둘까?

### 핵심 비교

| 항목                       | nginx `limit_req`                       | 앱 레이어 (slowapi 등)                       |
| -------------------------- | --------------------------------------- | -------------------------------------------- |
| **차단 비용**              | 💚 매우 저렴 (~µs)                      | 💛 가볍지만 앱이 받음 (~수십 µs, asyncio)    |
| **식별 키**                | IP, header 정도                         | user_id, JWT sub, API key, 엔드포인트별 자유 |
| **비즈니스 컨텍스트**      | ❌ 모름                                 | ✅ "Pro 플랜은 한도 ↑" 가능                  |
| **응답 커스터마이징**      | 제한적                                  | 자유 (JSON, i18n)                            |
| **설정 변경**              | reload 필요                             | 코드/env로 즉시                              |
| **분산 환경**              | 인스턴스 간 공유 어려움                 | Redis 백엔드로 공유 가능                     |
| **DDoS 방어**              | 작은 규모 가능, 큰 규모는 CDN 영역      | ❌ 부적합                                    |

### 의사결정 가이드

```
질문 1: 인증 없는 공개 엔드포인트인가?
  YES → 앱 또는 nginx (IP 키) 필수
  NO ↓

질문 2: 외부 유료 API 호출이 있는가?
  YES → 앱 레이어 (user_id 키) 필수 — nginx는 키 추출 불편
  NO ↓

질문 3: DB 쓰기 + 누적 자원 소모인가?
  YES → 앱 레이어 (user_id 키) 권장
  NO ↓

질문 4: 로그인/인증/비밀번호 변경 엔드포인트인가?
  YES → 매우 보수적 (5/min, IP 키) 필수 — brute-force 방어
  NO ↓

질문 5: Free vs Pro 등 비즈니스 차등?
  YES → 앱 레이어 + 동적 limit string 필수
  NO ↓

질문 6: 수만 RPS 이상 트래픽 또는 L7 DDoS 우려?
  YES → CDN/WAF (Cloudflare, AWS Shield) — nginx 단독으로는 부족
  NO ↓

→ rate limit 불필요. 추가하면 운영 부담만 ↑
```

### 성능에 관한 흔한 오해

> ⚠️ **자주 잘못 알려진 사실**: "10만 RPS 시 nginx 1차 차단 없이는 앱이 못 버틴다"

✅ **정확한 진실**:
- slowapi 거절 비용 (uvicorn/asyncio, memory 백엔드): **수십 µs/req**
- nginx `limit_req` 거절 비용: **수 µs/req**
- 단일 호스트 1만 RPS 이하에서는 **의미 있는 차이 없음** (측정 필요)
- "10만 RPS"는 위협 모델 과장 — 진짜 L7 DDoS면 nginx의 IP-based limit도 **botnet에 무력** → CDN/Shield 영역

> ⚠️ **자주 잘못 알려진 사실**: "요즘 트렌드는 앱 레벨이 우세"

✅ **정확한 진실**: 표준이 합의된 트렌드는 **없습니다**. 환경별로:
- 모놀리식 단일 인스턴스 → 앱 레이어가 흔함
- MSA/서비스 메시 → Istio `RequestAuthentication`, Envoy 사이드카 등 **인프라 외주화**
- API Gateway 환경 → Kong, AWS API Gateway, Apigee가 native 제공
- eBPF 기반 → Cilium, Pixie (신흥)

---

## 7. 🤔 "인증된 API에도 rate limit이 필요한가?"

**솔직히 — 많은 회사가 인증된 API에는 안 겁니다.** 그래서 안 써본 게 이상한 게 아닙니다.

### 12살 비유: 회원제 헬스장

| 정책                  | 비유                | rate limit 관점                              |
| --------------------- | ------------------- | -------------------------------------------- |
| 문 앞 신분증 확인     | 인증 (JWT)          | "당신이 누구인지 확인"                       |
| 1인당 러닝머신 1대    | rate limit          | "정당한 회원이라도 자원은 공평하게"          |
| 회원증 출입 무제한    | rate limit 없음     | "한 사람이 모든 기구 차지해도 OK"            |

→ **회원이라도 시스템 자원·비용·다른 회원 경험은 보호해야 함**.

### 인증된 API에 필요한 경우 (앞의 5가지 시나리오 재방문)

| 케이스                                  | rate limit 필요?              |
| --------------------------------------- | ----------------------------- |
| 사내 도구 (직원 100명만 씀)             | ❌ 보통 불필요                |
| 인증된 API + DB 읽기만 + 자원 안 비쌈   | ❌ 불필요                     |
| MVP/베타 (트래픽 적음)                  | ❌ 후순위                     |
| 비용 민감 외부 호출 없음                | ❌ 우선순위 낮음              |
| **공개 API + 외부 호출/비용**           | ✅ **필수**                   |
| **공개 API + DB 쓰기**                  | ✅ 권장                       |
| **로그인/인증 엔드포인트**              | ✅ **필수** (brute-force)     |
| **자원 차등 SaaS (Free/Pro)**           | ✅ 필수                       |
| **계정 탈취 피해 최소화**               | ✅ 보안 권장                  |

### 현업에서 잘 안 보이는 3가지 이유

1. 🏗️ **인프라 레이어로 외주화** (가장 흔함): Cloudflare, AWS API Gateway가 알아서 처리
2. 📉 **트래픽이 적어서 안 필요했음**: 작은 서비스는 운영 부담 > 보호 가치
3. 🕳️ **그냥 빚(tech debt)으로 쌓인 것**: 첫 incident 후 부랴부랴 도입

---

## 8. 🚨 안티패턴 모음 (Anti-patterns)

자주 보는 잘못된 패턴들:

### ❌ AP1: key_func에 식별자 아닌 값 넣기 (P0 보안 결함)

```python
# 잘못된 예
@limiter.limit("60/minute", key_func=lambda r: get_user_plan(r))  # ❌ 모든 Pro 유저 단일 버킷
@limiter.limit("60/minute", key_func=lambda r: get_user_role(r))  # ❌ 모든 admin 단일 버킷
```

→ **올바른 패턴**: 키는 식별자(user_id), 한도값을 정책으로 분기.

### ❌ AP2: `request: Request` 인자 누락

```python
@app.get("/items")
@limiter.limit("60/minute")
def list_items():  # ❌ request 없음 → slowapi가 hook 못 함
    ...
```

→ **올바른 패턴**: `def list_items(request: Request):`

### ❌ AP3: 멀티워커에서 memory 백엔드 사용

```python
# gunicorn -w 4로 띄우면서
limiter = Limiter(key_func=get_remote_address)  # ❌ 워커별 카운터 분리
```

→ **올바른 패턴**: Redis 백엔드 또는 단일 워커.

### ❌ AP4: 프록시 뒤에서 IP 키 직접 사용

```python
# Cloudflare/LB 뒤에서
limiter = Limiter(key_func=get_remote_address)  # ❌ 모든 요청이 LB IP로
```

→ **올바른 패턴**: X-Forwarded-For 파싱 + 신뢰 가능 프록시 검증.

### ❌ AP5: 인증 엔드포인트 무방비

```python
@app.post("/auth/login")  # ❌ rate limit 없음 → brute-force 노출
def login(...):
    ...
```

→ **올바른 패턴**: `@limiter.limit("5/minute", key_func=ip_key)` 정도 보수적으로.

### ❌ AP6: Redis 백엔드 fail 정책 미정

```python
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://...",
    # ❌ Redis 다운 시 어떻게 할지 미결정
)
```

→ **올바른 패턴**: fail-open(보안 약화) vs fail-closed(가용성 붕괴) 명시적 결정 + 알림.

### ❌ AP7: rate limit이 외부 API 호출 *뒤*에 있음

```python
@app.get("/expensive")
def expensive(request: Request):
    result = call_external_api()  # ❌ 비용 발생 후 throttle
    if too_many_calls():
        raise HTTPException(429)
    return result
```

→ **올바른 패턴**: 데코레이터로 외부 호출 *전에* 차단.

### ❌ AP8: 동기 WSGI 환경에서 거대한 동시 요청 처리 시 미들웨어가 worker를 점유

asyncio가 아닌 동기 WSGI (gunicorn sync worker + Flask) 환경에서는 slowapi 거절도 worker를 점유하므로 백프레셔 비용 발생. 이 경우 **nginx 1차 차단의 가치가 비동기보다 상대적으로 큼**.

---

## 9. 🛠️ 운영 시 체크리스트

### 코드 작성 시

- [ ] `request: Request` 인자 포함
- [ ] `key_func`은 **식별자**(user_id, IP)만 반환
- [ ] 한도값은 `limit string` 또는 callable에 정의 (plan별 분기)
- [ ] 인증 + 익명 모두 키가 안전하게 격리 (anonymous는 IP로 폴백)
- [ ] 외부 API 호출 *전*에 데코레이터 배치
- [ ] 데코레이터 순서: `@router.get(...)` → `@limiter.limit(...)` → `def`

### 인프라 결정 시

- [ ] 워커 수 확인 (단일 → memory OK, 멀티 → Redis)
- [ ] 프록시(LB/CDN) 뒤에 있으면 X-Forwarded-For 처리
- [ ] Redis 도입 시 fail-open vs fail-closed 결정
- [ ] 모니터링: 429 응답률 dashboard 추가
- [ ] 알림: 429가 비정상적으로 급증하면 통지

### 보안 감사 시

- [ ] 로그인/인증/비밀번호 변경 엔드포인트에 rate limit 적용
- [ ] 외부 API 호출 엔드포인트에 rate limit 적용
- [ ] DB 쓰기 + 누적 자원 엔드포인트에 rate limit 적용
- [ ] 응답 헤더(`X-RateLimit-*`) 노출 정책 결정 (보안적으로는 안 노출이 보수적)

---

## 10. 📚 참고 출처

### slowapi / limits

- [slowapi readthedocs](https://slowapi.readthedocs.io/en/latest/)
- [slowapi GitHub](https://github.com/laurents/slowapi)
- [slowapi extension.py 소스](https://github.com/laurents/slowapi/blob/master/slowapi/extension.py)
- [limits 라이브러리 docs](https://limits.readthedocs.io/en/stable/quickstart.html)
- [limits memory storage 소스](https://github.com/alisaifee/limits/blob/master/limits/storage/memory.py)
- [Flask-Limiter configuration](https://flask-limiter.readthedocs.io/en/stable/configuration.html) — 멀티프로세스 경고

### nginx

- [ngx_http_limit_req_module](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html)
- [ngx_http_auth_request_module](https://nginx.org/en/docs/http/ngx_http_auth_request_module.html)
- [ngx_http_auth_jwt_module (nginx-plus)](https://nginx.org/en/docs/http/ngx_http_auth_jwt_module.html)
- [njs 설치](https://nginx.org/en/docs/njs/install.html)
- [njs JWT 예제](https://github.com/nginx/njs-examples)

### OpenResty

- [lua-resty-jwt](https://github.com/SkyLothar/lua-resty-jwt)

### 베스트 프랙티스 / 표준

- OWASP API Security Top 10:2023 API4 (Unrestricted Resource Consumption)
- RFC 7231 §7.1.3 (Retry-After 의미론)
- [GitHub API rate limit](https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting) — 인증 유무 차등 (60 vs 5000)
- [Stripe API rate limits](https://stripe.com/docs/rate-limits) — 인증 API에 100/sec 적용 (SaaS 표준)

---

## 11. ✅ 핵심 요약 카드

```
┌─────────────────────────────────────────────────────────┐
│ Rate Limiting 한 줄 요약                                  │
├─────────────────────────────────────────────────────────┤
│ ① 식별 키, ② 한도, ③ 시간 윈도우 — 이 3개만 정의하면 끝   │
│                                                         │
│ key_func = 식별자 (user_id, IP)                          │
│ limit string = 정책 (plan별 한도)                        │
│ 둘을 절대 섞지 말 것 (P0 보안 결함의 원인)                 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ "정석"은 없다 — 환경에 맞춰 결정                          │
├─────────────────────────────────────────────────────────┤
│ • 인증 없는 공개 API → 반드시                            │
│ • 외부 유료 API 호출 → 반드시                            │
│ • 로그인 엔드포인트 → 반드시 (brute-force)               │
│ • DB 쓰기 + 누적 → 권장                                  │
│ • DDoS 우려 → 앱 레이어 ❌, CDN/WAF ✅                   │
│ • 사내 도구 / MVP → 안 해도 됨                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 흔한 신화 정정                                            │
├─────────────────────────────────────────────────────────┤
│ ❌ "정확히 N배"      → ✅ "최대 N배 (up to N×)"           │
│ ❌ "JWT는 Lua 필수"  → ✅ njs/auth_request/plus/OpenResty │
│ ❌ "Defense in Depth │   "                               │
│    가 정석"          → ✅ 환경에 따라 결정                │
│ ❌ "10만 RPS면 nginx │   "                               │
│    가 살린다"        → ✅ 진짜 위협은 CDN/WAF 영역        │
│ ❌ "프로덕션=Redis"  → ✅ 멀티워커 + 정확 한도 필요할 때만 │
└─────────────────────────────────────────────────────────┘
```
