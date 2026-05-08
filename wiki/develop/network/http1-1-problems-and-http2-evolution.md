---
tags: [http, http1-1, http2, evolution, performance, deep-research]
created: 2026-04-28
---

# 🔄 HTTP/1.1의 실무 문제와 HTTP/2의 진화 — Deep Research

> 💡 **한줄 요약**: HTTP/2는 새로운 의미론을 만든 것이 아니다. **HTTP/1.1이 30년간 누적해 온 실무 우회 기법(domain sharding, sprite, bundling, inlining)을 더 이상 필요 없게 만드는 것**이 목적이었다. 즉 HTTP/2는 HTTP/1.1의 한계를 풀기 위한 **새 wire format**이다.

---

## 📌 출발점 — 왜 HTTP/2가 필요했나

```
2010년대 초반의 한 페이지 (예: 뉴스 사이트):
  - HTML 1
  - CSS 5
  - JS 12
  - 이미지 80
  - 폰트 4
  - 광고 스크립트 8
  ────────────────
  총 110+ HTTP 요청
  
HTTP/1.1의 현실:
  - 호스트당 6 connection 한계
  - 110 / 6 = 18.3 라운드 직렬화
  - 각 라운드 = 평균 80~150ms RTT
  - 단순 계산: 1.5~3초가 그냥 RTT 누적으로 소비
```

이 페이지를 빠르게 만들기 위해 개발자들은 **HTTP/1.1을 우회하는 hack**을 써야 했다. 그 hack들이 HTTP/2 등장의 동기다.

---

## 1️⃣ 핵심 문제 6가지 → HTTP/2의 해결 메커니즘 매핑

| # | HTTP/1.1 문제 | 실무가 쓰던 우회 hack | HTTP/2 해결책 | 결과 |
|---|---|---|---|---|
| 1 | **Application HoL blocking** (pipelining 시 첫 응답이 늦으면 전체 정체) | pipelining 비활성화 + connection 수 증가 | **Stream multiplexing** | 응답 순서 무관, 한 stream이 늦어도 다른 stream은 정상 |
| 2 | **호스트당 6 connection 한계** | **도메인 샤딩** (cdn1.x, cdn2.x, …) | 단일 connection + 수백 stream | 도메인 샤딩 불필요 (오히려 안티패턴) |
| 3 | **헤더 중복 전송** (Cookie, Auth, UA를 매 요청 풀텍스트로) | 쿠키 최소화, 도메인 분리 | **HPACK 압축** + dynamic table | 첫 요청 후 인덱스 한 바이트로 참조 |
| 4 | **요청당 TCP/TLS 비용** (도메인 샤딩으로 더 악화) | keep-alive, connection pool | 단일 long-lived connection | 핸드셰이크 비용 1회로 amortize |
| 5 | **자원 개수 = 요청 개수** | **sprite image, JS/CSS 번들링, inlining (data URI)** | 자원 개수 부담 사라짐 | 캐시 무효화 단위를 작게 유지 가능 |
| 6 | **Server push 불가** (실시간성 한계) | long polling, SSE, WebSocket | PUSH_PROMISE (실패) → **103 Early Hints**(RFC 8297)가 후계 | preload 힌트 정도가 현실적 |

> 🔗 long polling/SSE 우회의 상세는 [[long-polling-http-realtime-communication]]

---

## 2️⃣ 가장 충격적인 반전 — 도메인 샤딩이 HTTP/2에서 **안티패턴**

### HTTP/1.1 시대 (~2014)
```
한 origin 동시 6 connection 한계:
  cdn.example.com → 동시 6개

도메인 샤딩 hack:
  cdn1.example.com → 6
  cdn2.example.com → 6
  cdn3.example.com → 6
  cdn4.example.com → 6
  ──────────────
  총 24개 동시 다운로드 가능 (페이지 빠르게 로드)
```

### HTTP/2 시대 (2015~)
```
도메인 샤딩이 오히려 해롭다:
  - DNS 조회 N배                  ❌ latency 증가
  - TLS 핸드셰이크 N배            ❌ CPU+RTT 비용
  - HPACK dynamic table N개로 분산 ❌ 압축률 ↓
  - HTTP/2 multiplexing 무력화     ❌ 본래 효과 사라짐
  - connection coalescing 적용 받기 어려움  ❌ HTTP/2 추가 최적화 손실
```

**결론**: HTTP/2 환경에서는 **하나의 origin으로 통합**해야 multiplexing + HPACK + connection coalescing 효과가 모두 발휘된다.

> 📌 **면접 단골**: "왜 HTTP/2에서 도메인 샤딩이 안티패턴인가?" → multiplexing이 6 connection 한계를 이미 해결, 도메인 분리는 압축·핸드셰이크·DNS 비용만 증가시킨다.

---

## 3️⃣ Sprite Image / 번들링 — HTTP/2에서 다시 생각해야 한다

### HTTP/1.1: 번들링은 미덕
```
원본:                     번들링 후:
- icon-home.png    ──┐    
- icon-cart.png      ├──► sprites.png (1 요청)
- icon-search.png    │   styles-all.css (1 요청)
- icon-user.png      │   app.bundle.js (1 요청)
- icon-menu.png    ──┘   
                          
요청 수: 5+ → 3
```

### HTTP/2: 과도한 번들링은 캐시 무효화 단위만 키운다
```
번들 1MB 중 5KB만 변경 → 1MB 전체 재다운로드 (캐시 miss)
                      ❌ 5KB 변경분만 받으면 됐을 것

권장:
- 핵심 vendor bundle (자주 안 바뀜) + 변경 잦은 작은 모듈로 분할
- HTTP/2 multiplexing이 자원 개수 부담을 줄였으므로 분할 가능
```

> ⚠️ 다만 "분할 = 무조건 좋다"는 아니다. 너무 작게 쪼개면 brotli/gzip 압축 효율↓, HTTP frame 오버헤드↑. 실측 기반 튜닝 필요.

---

## 4️⃣ HoL Blocking — 두 layer를 명확히 구분하라

| Layer | HTTP/1.1 | HTTP/2 | HTTP/3 |
|---|---|---|---|
| **Application HoL** (응답 순서 강제) | ❌ pipelining HoL 발생 | ✅ multiplexing으로 해결 | ✅ |
| **TCP HoL** (패킷 손실 시 모든 stream 정체) | ❌ TCP 자체 한계 | ❌ **여전히 발생** | ✅ QUIC(UDP)로 해결 |

### 왜 HTTP/2도 TCP HoL을 못 풀었나
```
TCP는 신뢰성·순서 보장이 본질이다.
패킷 N이 손실되면 N+1, N+2가 도착해도 OS가 application에 못 넘긴다.
HTTP/2가 application layer에서 stream을 분리해도,
TCP buffer 위에 stream이 얹혀 있는 한 모든 stream이 같이 막힌다.

→ 해결하려면 transport를 바꿔야 함
→ HTTP/3 = QUIC(UDP) 위에서 stream을 직접 관리
```

> 🔗 상세는 [[http3-quic-concept-explainer]]

---

## 5️⃣ 헤더 중복 — 작아 보이지만 누적되면 큰 비용

### 측정 사례 (대략적 수치)
```
모바일 페이지 50 요청, 평균 헤더 크기 800B (Cookie 큰 사이트):
  - HTTP/1.1: 50 × 800B = 40KB (요청 전체)
  - HPACK 압축: 첫 요청 800B + 49 × ~50B(인덱스) ≈ 3.3KB
  - 절감: 약 90%
  
3G 환경에서 의미가 크다 (latency-bound):
  - 40KB → ~1초 RTT
  - 3.3KB → ~80ms
```

### HPACK이 등장한 이유
- **CRIME 공격** (TLS-level 압축 사이드채널, 2012): TLS 압축 자체를 끄게 만듦 → HTTP 헤더 압축이 사라짐
- HTTP/2는 HTTP 레이어에서 안전하게 압축할 방법이 필요 → **HPACK** = static table + dynamic table + Huffman
- `never_indexed` 플래그로 sensitive 헤더 사이드채널 차단

> 📌 HPACK도 100% 안전하지는 않다. dynamic table에 추가되는 헤더 크기 차이로 secret을 추론하는 BREACH-류 공격이 가능 → mitigation 적용 필요.

---

## 6️⃣ Server Push의 실패 — 왜 deprecated되었나

### 기대했던 시나리오
```
Client: GET /index.html
Server: HEADERS(1) "여기 index"
        PUSH_PROMISE(2) "/style.css 줄게"
        DATA(1) "<html>…<link href='/style.css'>"
        HEADERS(2)
        DATA(2) "body{…}"
→ 클라이언트가 link를 파싱하기 전에 이미 도착!
```

### 실제 결과
1. **캐시-인식 push 어려움**: 브라우저는 자기 캐시 상태를 서버에 정확히 알리지 않음 → 서버가 이미 캐시에 있는 자원도 push → 대역폭 낭비
2. **multiplexing 자원 경쟁**: push가 다른 critical 자원과 stream을 경쟁 → 오히려 느려짐
3. **CDN edge에서 push 어려움**: origin과 edge의 캐시 상태가 다름

### 결과
- Chrome: 2022년 9월 (M106 stable, 2022-09-27) server push 지원 제거
- RFC 9113: server push **deprecated**
- 후계자: **103 Early Hints** (RFC 8297) — "응답 본문 만드는 동안 미리 preload할 자원 알려줄게"

```
Server: HTTP/1.1 103 Early Hints
        Link: </style.css>; rel=preload; as=style
        Link: </app.js>; rel=preload; as=script
        
        (실제 200 응답은 나중에)
```

→ Cloudflare, Fastly가 2023년부터 광범위 지원, web.dev 측정 LCP 30%↓ 사례 보고

---

## 7️⃣ HTTP/2가 새로 만든 문제들 (trade-off)

| 새 문제 | 원인 | 대응 |
|---|---|---|
| **TCP HoL 잔존** | TCP 자체 한계 | HTTP/3 도입 |
| **Rapid Reset DoS (CVE-2023-44487)** | RST_STREAM 무제한 발송 가능 | 서버 패치, RST 비율 제한 |
| **L4 LB 부하 불균형** | long-lived connection | L7 LB(Envoy/ALB) |
| **HPACK 사이드채널** | dynamic table 헤더 크기 차이 | `never_indexed`, CSRF token rotation |
| **이진 형식 디버깅 어려움** | curl 직접 안 보임 | nghttp2, Wireshark TLS-key |
| **CPU 비용 증가** | HPACK + frame parse + TLS | 하드웨어 TLS offload, kTLS |

---

## 8️⃣ 진화 흐름 한눈에

```
                  ┌─────────────────────────────┐
HTTP/1.0 (1996) → │ HTTP/1.1 (1997, RFC 2616)   │
                  │ - persistent connection     │
                  │ - Host header               │
                  │ - chunked encoding          │
                  └─────────────────────────────┘
                           │
                           │ 실무 hack 누적: domain sharding, sprite, bundling
                           ▼
                  ┌─────────────────────────────┐
SPDY (2009) ────► │ HTTP/2 (2015 RFC 7540 →     │
                  │       2022 RFC 9113)        │
                  │ - binary frame              │
                  │ - multiplexing              │
                  │ - HPACK                     │
                  │ - server push (→deprecated) │
                  └─────────────────────────────┘
                           │
                           │ TCP HoL 미해결, 모바일 시대 connection migration 요구
                           ▼
                  ┌─────────────────────────────┐
QUIC (2012 G) ──► │ HTTP/3 (2022 RFC 9114,      │
                  │        QUIC RFC 9000)       │
                  │ - UDP + TLS 1.3 + stream    │
                  │ - 0-RTT, conn migration     │
                  │ - QPACK (RFC 9204)          │
                  └─────────────────────────────┘
```

---

## 9️⃣ 핵심 정리

1. **HTTP/2는 의미론이 아니라 wire format을 바꿨다** — RFC 9110(Semantics)는 HTTP/1.1·2·3 공통, RFC 9112/9113/9114만 버전별
2. **multiplexing은 application HoL만 해결**한다 — TCP HoL은 HTTP/3로만 가능
3. **도메인 샤딩, sprite, 과도한 번들링은 HTTP/2에서 안티패턴** — multiplexing이 자원 개수 부담을 제거했기 때문
4. **HPACK은 CRIME 이후 안전한 압축 방법으로 등장** — `never_indexed`로 sensitive 헤더 보호
5. **Server push는 실패했다** — 103 Early Hints가 실용적 대안
6. **HTTP/2는 새 문제도 만들었다** — Rapid Reset, L4 LB 불균형, HPACK 사이드채널

---

## 🔗 시리즈 노트

- [[http1-1-concept-explainer]] — HTTP/1.1 기초
- [[http2-concept-explainer]] — HTTP/2 기초
- [[why-http1-1-still-dominates]] — 왜 여전히 HTTP/1.1인가
- [[http2-perspective-grpc-and-ecosystem]] — HTTP/2를 활용하는 시스템들
- [[http3-quic-concept-explainer]] — HTTP/3 + QUIC
- [[http-protocol-interview-qa]] — 면접 대비 Q&A

## 📎 Sources

1. [RFC 9113 — HTTP/2](https://www.rfc-editor.org/rfc/rfc9113)
2. [RFC 7541 — HPACK](https://www.rfc-editor.org/rfc/rfc7541)
3. [RFC 8297 — 103 Early Hints](https://www.rfc-editor.org/rfc/rfc8297)
4. [Removing HTTP/2 Server Push from Chrome](https://developer.chrome.com/blog/removing-push/)
5. [HTTP/2 Rapid Reset attack — Cloudflare](https://blog.cloudflare.com/technical-breakdown-http2-rapid-reset-ddos-attack/)
6. [Web Almanac 2024 — HTTP](https://almanac.httparchive.org/en/2024/http)
7. [HTTP/2 anti-patterns — web.dev](https://web.dev/articles/performance-http2#dont_shard_origins_with_http2)
