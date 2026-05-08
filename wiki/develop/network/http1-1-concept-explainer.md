---
tags: [http, http1-1, network-protocol, backend, concept-explainer]
created: 2026-04-28
---

# 📖 HTTP/1.1 (Hypertext Transfer Protocol, version 1.1) — Concept Deep Dive

> 💡 **한줄 요약**: HTTP/1.1은 **하나의 TCP 연결을 여러 요청에 재사용 (persistent connection)** 하고 텍스트 기반으로 요청-응답을 주고받는, 1997년부터 30년 가까이 웹의 기본 약속(default contract) 역할을 해 온 프로토콜이다.

---

## 1️⃣ 무엇인가? (What is it?)

HTTP/1.1은 **요청 메시지와 응답 메시지를 텍스트(ASCII)로 주고받는 stateless 애플리케이션 계층 프로토콜**이다. HTTP/1.0(RFC 1945, 1996)이 매 요청마다 TCP 연결을 새로 열어야 했던 한계를 해결하기 위해 1997년 RFC 2068, 1999년 RFC 2616으로 정식화되었고, 2014년 RFC 7230~7235로 분할 정비, 2022년 **RFC 9110~9112**로 다시 통합·현행화되었다.

🎯 **현실 비유**: HTTP/1.0이 "전화 한 통 걸 때마다 새로 다이얼을 돌려야 하는 옛날 공중전화"였다면, HTTP/1.1은 **"한 번 통화 연결되면 여러 번 말하고 들을 수 있는 무전기"**다. 무전기 한 대 = TCP 연결 하나, 통화 = 요청/응답 한 쌍.

### 📜 탄생 배경

- HTTP/1.0 시대(1996): 페이지 하나 로드 = HTML + 이미지 + CSS + JS → 각각 새 TCP 연결 → **TCP 핸드셰이크 비용 폭발**
- 1997: RFC 2068에서 keep-alive 도입 → **persistent connection이 기본**으로 채택
- 1999: RFC 2616 — Host 헤더 의무화로 **가상 호스팅(virtual hosting)** 가능 → 한 IP에 여러 도메인 운영
- 2014: RFC 7230~7235 — 모호한 부분 정리·세분화
- 2022: **RFC 9110 (HTTP Semantics) + RFC 9111 (Caching) + RFC 9112 (HTTP/1.1)** — HTTP/2·3와 의미론을 분리하여 공통화

> 📌 **핵심 키워드**: `persistent connection`, `pipelining`, `chunked encoding`, `Host header`, `Content-Type`, `Cache-Control`, `ETag`, `keep-alive`, `connection pooling`, `head-of-line blocking`

---

## 2️⃣ 핵심 개념 (Core Concepts)

### 메시지 구조

```
┌──────────── HTTP/1.1 요청 메시지 ────────────┐
│ GET /api/users/42 HTTP/1.1   ← Request line │
│ Host: api.example.com         ← Headers     │
│ Accept: application/json                    │
│ Authorization: Bearer abc123                │
│ User-Agent: Mozilla/5.0                     │
│                              ← Empty line   │
│ (Body — GET은 보통 비어 있음)                  │
└─────────────────────────────────────────────┘

┌──────────── HTTP/1.1 응답 메시지 ────────────┐
│ HTTP/1.1 200 OK              ← Status line  │
│ Content-Type: application/json ← Headers    │
│ Content-Length: 87                          │
│ Cache-Control: max-age=300                  │
│ ETag: "a1b2c3"                              │
│                              ← Empty line   │
│ {"id":42,"name":"Alice"}     ← Body         │
└─────────────────────────────────────────────┘
```

**요점**: 모두 **텍스트 기반(ASCII)** — `curl`, `nc`, Wireshark에서 사람 눈으로 바로 읽힌다. 이 단순함이 HTTP/1.1의 최대 자산이자 비효율의 근원이다.

### 핵심 메커니즘 6가지

| 메커니즘 | 무엇을 해결하는가 | 어떻게 동작하는가 |
|---|---|---|
| **Persistent Connection (Keep-Alive)** | TCP 핸드셰이크 비용 | 응답 후 TCP 연결 유지 → 다음 요청에 재사용. `Connection: keep-alive`(HTTP/1.1 기본) |
| **Pipelining** | 응답 대기 시간 | 요청을 응답 기다리지 않고 **연속 전송** → 단, 응답은 순서대로 와야 함 (HoL 발생) |
| **Chunked Transfer Encoding** | 전체 본문 크기를 미리 모를 때 | `Transfer-Encoding: chunked` → 청크 단위 스트리밍, 마지막에 `0\r\n\r\n` |
| **Host Header (필수)** | 한 IP에 여러 도메인 | `Host: api.example.com` → 가상 호스팅의 토대 |
| **Content Negotiation** | 같은 리소스를 다른 형식으로 | `Accept`, `Accept-Language`, `Accept-Encoding` 헤더 |
| **Conditional Request + Caching** | 같은 리소스 반복 다운로드 | `ETag` / `Last-Modified` + `If-None-Match` / `If-Modified-Since` → `304 Not Modified` |

### 🌐 connection 모델

```
HTTP/1.0 (Connection: close):                HTTP/1.1 (Keep-Alive 기본):
                                              
[Client] ──TCP open──► [Server]              [Client] ──TCP open──► [Server]
         ◄── ACK ──                                   ◄── ACK ──
         ──── REQ ─►                                  ──── REQ #1 ─►
         ◄─── RES ──                                  ◄─── RES #1 ──
         ──TCP close─►                                ──── REQ #2 ─►
                                                     ◄─── RES #2 ──
[Client] ──TCP open──► [Server]   ← 또 핸드셰이크!     ──── REQ #3 ─►
         ──── REQ ─►                                  ◄─── RES #3 ──
         ◄─── RES ──                                  (idle 유지, 재사용)
         ──TCP close─►
```

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

### 🔄 요청 한 번의 전 생애주기

```
1. DNS 조회              api.example.com → 93.184.216.34
2. TCP 핸드셰이크         SYN → SYN-ACK → ACK (1 RTT)
3. (HTTPS) TLS 핸드셰이크  ClientHello → ServerHello → ... (1~2 RTT)
4. HTTP 요청 전송         GET /api/users/42 HTTP/1.1 ...
5. 서버 처리             routing → controller → DB → response build
6. HTTP 응답 수신         HTTP/1.1 200 OK ...
7. 연결 유지(Keep-Alive)  다음 요청 대기 (timeout까지)
8. (timeout/명시적 close) FIN → ACK
```

### Connection Pool & Per-Host Limit

브라우저와 클라이언트 라이브러리는 **호스트(origin)당 동시 연결 수에 상한**을 둔다. RFC 2616 권고는 2개였으나 현대 브라우저는 6~8개로 운영한다.

```
Chrome / Firefox / Safari (대략):
  - 한 origin (scheme+host+port) 당 동시 TCP 연결 상한: 6
  - 전체 동시 연결 상한: 17 ~ 256 (브라우저별)

영향:
  같은 페이지에 24개 리소스 요청 → 4 라운드(6×4) 직렬화 → latency 누적
  → "도메인 샤딩" hack 등장 (cdn1.x.com, cdn2.x.com … 으로 origin 늘림)
```

> 🔗 관련: [[python-requests-connection-pool-keepalive]] — Python `requests`/`urllib3`의 connection pool 동작 원리

### 🚧 Head-of-Line (HoL) Blocking — 가장 유명한 한계

```
Pipelining ON, 3개 요청을 한 connection에 쏨:

[Client] ──REQ1, REQ2, REQ3──► [Server]
                                    │
                                    ├─ REQ1 처리 중 (DB 슬로우 쿼리)
                                    │       ⏳ 5초 걸림
                                    ├─ REQ2 이미 끝났지만 → 대기!
                                    └─ REQ3 이미 끝났지만 → 대기!
                                    
[Client] ◄──RES1──── (5초 후)
         ◄──RES2────
         ◄──RES3────

→ 응답은 요청 순서대로 보내야 한다 (HTTP/1.1 명세).
   첫 응답이 느리면 뒤 모든 응답이 막힌다.
```

이 때문에 실무에선 **pipelining을 거의 비활성화**하고 (Chrome은 2011년에 폐기) connection 여러 개를 병렬로 쓰는 방식을 택한다.

### 🗄️ 캐싱 — `Cache-Control` + `ETag`

```
첫 요청:
  GET /logo.png
  → 200 OK, ETag: "v1", Cache-Control: max-age=3600
  
1시간 안:
  → 브라우저 캐시 hit, 네트워크 요청 자체 발생 X
  
1시간 후:
  GET /logo.png
  If-None-Match: "v1"     ← 조건부 요청
  → 서버: ETag 비교
    - 같으면: 304 Not Modified (본문 없음, 헤더만 — 비용 거의 0)
    - 다르면: 200 OK + 새 본문 + 새 ETag
```

> 🔗 관련: [[http-status-code-429-303]] — 429/303과 PRG 패턴

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 HTTP/1.1이 여전히 1순위인 영역

| # | 유즈 케이스 | 왜 HTTP/1.1인가 |
|---|---|---|
| 1 | **CDN edge ↔ origin** 통신 | 텍스트 기반 디버깅, 광범위한 프록시 호환성, 단순한 HTTP keep-alive |
| 2 | **내부 헬스체크 / liveness probe** | curl 한 줄, 가벼움, 디버깅 즉시 가능 |
| 3 | **REST 공개 API** | 모든 클라이언트(브라우저/모바일/CLI)에서 즉시 사용 |
| 4 | **레거시 시스템 통합** | 기업망 방화벽·proxy가 HTTP/1.1만 안전하게 통과 |
| 5 | **간단한 webhook 수신** | POST 한 번이면 끝, HTTP/2 셋업 불필요 |

### ✅ 베스트 프랙티스

1. **Keep-Alive 명시적 활용**
   ```python
   # ✅ requests.Session() 사용 → 내부적으로 connection pool + keep-alive
   import requests
   session = requests.Session()
   for url in urls:
       session.get(url)  # 같은 host면 TCP 재사용
   
   # ❌ 매번 requests.get() 호출 → 매번 새 TCP+TLS 핸드셰이크
   ```

2. **`Content-Length` 또는 `Transfer-Encoding: chunked` 둘 중 하나 명확히**
   - 둘 다 없으면 connection close까지 본문으로 간주 (위험)
   - 둘 다 있으면 RFC 7230 §3.3.3 — `Transfer-Encoding`이 우선, 다만 **request smuggling** 공격 벡터

3. **`Cache-Control` 정책 선언**
   - 정적 자원: `Cache-Control: public, max-age=31536000, immutable`
   - 동적 응답: `Cache-Control: private, no-cache` + ETag
   - 민감 데이터: `Cache-Control: no-store`

4. **HTTPS 강제 + HSTS**
   - 평문 HTTP/1.1은 헤더가 그대로 노출됨 → 프로덕션은 항상 TLS

5. **Connection pool 크기 튜닝**
   - 클라이언트 측: `urllib3` `pool_maxsize`, Go `http.Transport.MaxIdleConnsPerHost`
   - 서버 측: nginx `keepalive_requests`, `keepalive_timeout`

> 🔗 관련: [[python-requests-connection-pool-keepalive]], [[connection-pool-eviction-lazy-idle]]

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|---|---|---|
| ✅ 장점 | **단순함** | 텍스트 기반 — `curl`, `telnet`, Wireshark로 즉시 디버깅 |
| ✅ 장점 | **광범위한 호환성** | 모든 프록시·방화벽·로드밸런서가 native 지원 |
| ✅ 장점 | **무상태(stateless) 설계** | 각 요청 독립 → 서버 수평 확장 용이 |
| ✅ 장점 | **풍부한 도구 생태계** | curl, Postman, Charles, mitmproxy 등 30년 축적 |
| ✅ 장점 | **명세 안정** | RFC 9110~9112로 정착 — 새 학습 없음 |
| ❌ 단점 | **Head-of-Line blocking** | pipelining 시 첫 응답이 느리면 전체 정체 |
| ❌ 단점 | **헤더 중복·비압축** | 같은 헤더(`Cookie`, `User-Agent`)가 매 요청 그대로 전송 → 대역폭 낭비 |
| ❌ 단점 | **per-host 6 connection 한계** | 페이지 자원 많을 때 직렬화 발생 |
| ❌ 단점 | **TCP 1개 = HTTP 1개** 동시 처리 | 진정한 multiplexing 불가 |
| ❌ 단점 | **Server push 불가** | 서버가 클라이언트에 먼저 푸시 못 함 (long polling/SSE 우회) |
| ❌ 단점 | **Latency 민감** | RTT 누적이 곧 페이지 로딩 시간 |

> 🔗 관련: [[long-polling-http-realtime-communication]] — server push가 안 되어 등장한 long polling/SSE/WebSocket

---

## 6️⃣ 차이점 비교 (Comparison)

### HTTP/0.9 → 1.0 → 1.1 → 2 → 3 진화

| 버전 | 발표 | 핵심 추가 | 한계 |
|---|---|---|---|
| HTTP/0.9 | 1991 | GET만, HTML만 | 메타데이터 없음 |
| HTTP/1.0 | 1996 | 헤더, 상태 코드, 메서드 다양화 | 매 요청마다 TCP 새로 |
| **HTTP/1.1** | **1997** | **persistent connection, Host, chunked, caching** | **HoL blocking, 헤더 중복** |
| HTTP/2 | 2015 (RFC 7540) → 2022 (RFC 9113) | 이진 frame, multiplexing, HPACK, server push | TCP HoL 여전 |
| HTTP/3 | 2022 (RFC 9114) | QUIC(UDP), 0-RTT, connection migration | 기업망 UDP 차단 |

### HTTP/1.1 vs HTTP/2 핵심 비교 (요약 — 자세한 비교는 [[http1-1-problems-and-http2-evolution]])

| 항목 | HTTP/1.1 | HTTP/2 |
|---|---|---|
| 표현 | 텍스트 | 이진(binary frame) |
| 동시성 | TCP 6개 병렬 (per host) | TCP 1개 + stream 다수 (multiplexing) |
| 헤더 압축 | 없음 | HPACK (RFC 7541) |
| Server push | ❌ | ✅ (다만 2022년 deprecated) |
| HoL blocking | application + TCP 모두 | application은 해결, TCP는 여전 |
| 디버깅 | curl 즉시 | nghttp2, Wireshark 디코더 필요 |

### 진화 동기 (한 줄)

```
HTTP/1.1 한계 ──┐
                ├──► HTTP/2가 application layer HoL을 해결
헤더 중복 ──────┘     하지만 TCP layer HoL은 그대로

TCP HoL ────────► HTTP/3 (QUIC = UDP 기반)으로 해결
```

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|---|---|---|
| 1 | 매 요청마다 새 TCP 연결 | 핸드셰이크 비용 누적 (HTTPS는 더 심함) | Session/HTTP client 재사용 |
| 2 | `Content-Length`와 `Transfer-Encoding` 둘 다 설정 | **HTTP request smuggling** 공격 벡터 | 둘 중 하나만 |
| 3 | Pipelining ON으로 두기 | HoL blocking + 프록시 호환성 깨짐 | 비활성화(브라우저 기본값) |
| 4 | `Host` 헤더 누락 | HTTP/1.1에서 필수 → 400 Bad Request | 클라이언트가 자동 설정하는지 확인 |
| 5 | `Cache-Control` 미설정 | 캐시 정책 일관성 깨짐 | 명시적 선언 (정적/동적 구분) |
| 6 | TLS 없는 평문 HTTP | 헤더(Cookie, Auth)가 그대로 노출 | HTTPS 강제 + HSTS |
| 7 | per-host 연결 한계 무시 | 같은 origin에 수십 개 자원 동시 요청 → 직렬화 | 도메인 샤딩 또는 HTTP/2로 이전 |

### 🔒 보안 주의점

- **HTTP request smuggling**: front-end proxy와 back-end가 `Content-Length` vs `Transfer-Encoding` 우선순위를 다르게 해석 → 요청 경계 혼동 → 캐시 오염, 인증 우회
- **헤더 인젝션 (CRLF injection)**: 사용자 입력을 헤더에 그대로 넣지 말 것
- **slowloris**: 헤더만 천천히 보내면서 connection 점유 → DoS → 서버에 read timeout 필요

### 🎯 성능 함정

- **TLS 핸드셰이크 비용** > **TCP 핸드셰이크 비용**: HTTPS에서 keep-alive 효과가 더 크다
- **`keepalive_timeout`이 너무 길면 서버 메모리 압박**, 너무 짧으면 효과 없음 (보통 60~120s)
- **L4 로드밸런서**가 connection 단위로 분배하면, keep-alive로 인해 **로드 불균형** 발생 가능 → L7 LB 권장

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|---|---|---|
| 📖 RFC | RFC 9110 | HTTP Semantics (현행) |
| 📖 RFC | RFC 9111 | HTTP Caching (현행) |
| 📖 RFC | RFC 9112 | HTTP/1.1 (현행, RFC 7230 대체) |
| 📖 MDN | HTTP overview | developer.mozilla.org/en-US/docs/Web/HTTP |
| 📘 도서 | *HTTP: The Definitive Guide* (O'Reilly) | David Gourley — HTTP/1.x 결정판 |
| 📺 영상 | High Performance Browser Networking — Ilya Grigorik | 무료 온라인 (hpbn.co) |

### 🛠️ 실무 도구

| 도구 | 용도 |
|---|---|
| **curl** | HTTP/1.1 요청 디버깅 표준 |
| **httpie** | curl보다 가독성 좋은 CLI |
| **mitmproxy** | 인터셉트 프록시, HTTP/1.1·2·3 지원 |
| **Charles / Proxyman** | macOS GUI 프록시 |
| **Wireshark** | 패킷 레벨 분석 (TLS 키 export 시 평문 가능) |
| **nginx** | 대표적 HTTP/1.1 reverse proxy |
| **HAProxy** | L7 load balancer, HTTP/1.1 native |

### 📊 알아두면 좋은 숫자

| 숫자 | 의미 |
|---|---|
| **6** | 브라우저당 한 origin 동시 연결 상한 (대략) |
| **60~120s** | nginx 기본 keep-alive timeout |
| **8KB** | 일반적인 헤더 크기 상한 (서버별 설정) |
| **1 RTT** | TCP 3-way handshake (TLS 1.2 추가 1~2 RTT) |
| **2014 / 2022** | RFC 7230 / RFC 9112 발표 연도 |

### 💬 커뮤니티 인사이트

- HTTP/2가 나온 지 10년이 지났지만 **HTTP/1.1은 여전히 죽지 않는다** — 자세한 이유는 [[why-http1-1-still-dominates]]
- HTTP/1.1을 깊이 이해하지 못하면 HTTP/2의 multiplexing과 HPACK이 **왜** 그렇게 설계되었는지 알 수 없다
- 면접에서 HTTP/1.1 한계를 묻는 질문은 사실상 **HTTP/2 등장 동기를 묻는 것**과 같다 → [[http-protocol-interview-qa]]

---

## 🔗 시리즈 노트

- [[http2-concept-explainer]] — HTTP/2 frame, multiplexing, HPACK
- [[http1-1-problems-and-http2-evolution]] — 한계 → HTTP/2 해결 메커니즘 매핑
- [[why-http1-1-still-dominates]] — 왜 여전히 HTTP/1.1인가
- [[http2-perspective-grpc-and-ecosystem]] — HTTP/2 위에서 동작하는 시스템들
- [[http3-quic-concept-explainer]] — HTTP/3 + QUIC
- [[http-protocol-interview-qa]] — 면접 대비 Q&A

## 📎 Sources

1. [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
2. [RFC 9111 — HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111)
3. [RFC 9112 — HTTP/1.1](https://www.rfc-editor.org/rfc/rfc9112)
4. [MDN — HTTP overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
5. *High Performance Browser Networking* — Ilya Grigorik (https://hpbn.co)
6. [HTTP/1.1 connection management — MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Connection_management_in_HTTP_1.x)
