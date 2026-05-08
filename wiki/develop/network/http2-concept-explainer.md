---
tags: [http, http2, network-protocol, backend, concept-explainer, hpack, multiplexing]
created: 2026-04-28
---

# 📖 HTTP/2 — Concept Deep Dive

> 💡 **한줄 요약**: HTTP/2는 HTTP/1.1의 의미론(메서드, 헤더, 상태 코드)을 그대로 두면서, **전송 형태를 텍스트 → 이진 frame**으로 바꾸고 **하나의 TCP 연결 위에서 여러 stream을 동시에 다중화(multiplexing)** 하여 HTTP/1.1의 head-of-line blocking과 헤더 중복 문제를 application layer에서 해결한 프로토콜이다.

---

## 1️⃣ 무엇인가? (What is it?)

HTTP/2는 **2009년 Google의 SPDY 실험**에서 출발해 **2015년 RFC 7540**으로 표준화되고, **2022년 RFC 9113**으로 현행화된 HTTP의 차세대 버전이다. 이름은 "HTTP version 2"이지만 실제로는 **새 wire format(전송 형식)** 이고, 의미론(GET/POST, 200/404, Content-Type 등)은 HTTP/1.1과 100% 호환된다.

🎯 **현실 비유**: HTTP/1.1이 **편지 한 장씩 차례로 보내는 우편**이라면, HTTP/2는 **하나의 컨테이너 트럭에 여러 사람의 짐을 작은 박스(frame)로 잘라 한꺼번에 싣고, 도착지에서 다시 사람별로 조립하는 컨테이너 운송**이다. 트럭(TCP 연결) 한 대로 수많은 짐(stream)을 동시에 옮긴다.

### 📜 탄생 배경

- **2009**: Google이 SPDY (스피디) 실험 시작 — Chrome ↔ Google 서버에서 50% 페이지 로드 속도 개선 보고
- **2012**: IETF HTTPbis WG가 HTTP/2.0 작업 시작 (SPDY를 기반으로)
- **2015 5월**: **RFC 7540 (HTTP/2)** + **RFC 7541 (HPACK)** 발표
- **2022 6월**: **RFC 9113 (HTTP/2)** 발표 — server push deprecated, priority 기능 RFC 9218(Extensible Priorities)로 분리, request smuggling 보안 강화
- **2024년 4월**: **HTTP/2 Rapid Reset (CVE-2023-44487)** 패치 권고 — RST_STREAM 폭주 DoS

> 📌 **핵심 키워드**: `binary framing`, `stream`, `multiplexing`, `HPACK`, `flow control`, `server push (deprecated)`, `connection preface`, `SETTINGS`, `Rapid Reset`

---

## 2️⃣ 핵심 개념 (Core Concepts)

### 4-Layer 모델 (HTTP/1.1과의 차이)

```
HTTP/1.1                           HTTP/2
┌─────────────────────┐            ┌─────────────────────┐
│ HTTP semantics       │            │ HTTP semantics       │ ← 동일 (RFC 9110)
│ (GET, 200, Content-) │            │ (GET, 200, Content-) │
├─────────────────────┤            ├─────────────────────┤
│ Text wire format     │            │ Binary frame layer   │ ← 다름!
│ (CRLF로 구분)         │            │ (Length+Type+Flags+) │
├─────────────────────┤            ├─────────────────────┤
│ TCP                  │            │ TCP                  │ ← 동일
└─────────────────────┘            └─────────────────────┘
                                    + Stream multiplexing
                                    + HPACK header compression
                                    + Flow control
```

### Frame — HTTP/2의 최소 단위

```
+-----------------------------------------------+
|                 Length (24 bits)              |  ← payload 길이 (max 16MB but SETTINGS로 제한)
+---------------+---------------+---------------+
|   Type (8)    |   Flags (8)   |               
+-+-------------+---------------+
|R|              Stream ID (31 bits)            |  ← 0=connection-level, 홀수=client-init, 짝수=server-init
+-+-------------------------------------------+
|                  Frame Payload                |  ← Type별 다른 형식
+-----------------------------------------------+
```

### Frame Type 9가지 (RFC 9113)

| Type | 코드 | 용도 |
|---|---|---|
| `DATA` | 0x0 | 메시지 본문 |
| `HEADERS` | 0x1 | 요청/응답 헤더 (HPACK 인코딩) |
| `PRIORITY` | 0x2 | 우선순위 (RFC 9113에서 deprecated, RFC 9218로 대체) |
| `RST_STREAM` | 0x3 | stream 즉시 종료 |
| `SETTINGS` | 0x4 | connection 파라미터 협상 |
| `PUSH_PROMISE` | 0x5 | server push 시작 (deprecated) |
| `PING` | 0x6 | RTT 측정, keep-alive |
| `GOAWAY` | 0x7 | connection 정상 종료 시그널 |
| `WINDOW_UPDATE` | 0x8 | flow control 윈도우 갱신 |
| `CONTINUATION` | 0x9 | HEADERS/PUSH_PROMISE의 연속 (헤더가 한 frame에 다 안 들어갈 때) |

### Stream — 가상의 양방향 통로

```
하나의 TCP 연결                              
┌─────────────────────────────────────────────┐
│                                             │
│  Stream 1 ──HEADERS──DATA──DATA──END_STREAM │  ← /api/users 요청-응답
│  Stream 3 ──HEADERS──DATA────────END_STREAM │  ← /api/products 요청-응답
│  Stream 5 ──HEADERS──DATA──DATA──DATA       │  ← 진행 중
│  Stream 7 ──HEADERS                         │  ← 막 시작
│                                             │
└─────────────────────────────────────────────┘
                                              
규칙:                                          
- Client-initiated stream ID: 홀수 (1, 3, 5, …)
- Server-initiated (push): 짝수 (deprecated)   
- Stream ID는 한 connection 안에서 monotonically increasing
```

### Stream 상태 머신

```
              idle
                │
       ┌────────┴────────┐
       │                 │
  send PUSH_PROMISE   recv HEADERS
       │                 │
       ▼                 ▼
  reserved          open
       │           ┌──┴──┐
       │      send END   recv END
       │           │     │
       ▼           ▼     ▼
  half-closed (local/remote)
       │
   send/recv END_STREAM
       │
       ▼
     closed
```

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

### Connection 시작 절차

```
1. Connection Preface
   Client → Server: "PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"  (24 bytes 매직 문자열)
   
2. SETTINGS 교환 (양방향)
   Client → Server: SETTINGS (MAX_CONCURRENT_STREAMS, INITIAL_WINDOW_SIZE, …)
   Server → Client: SETTINGS
   
3. SETTINGS_ACK 교환
   양쪽 모두 ACK

4. 정상 stream 통신 시작
   HEADERS, DATA, RST_STREAM, …
```

### Multiplexing — HoL Blocking을 application layer에서 해소

```
HTTP/1.1 (pipelining 가정):
[Client] → REQ1, REQ2, REQ3 → [Server]
                                  │
                                  ├─ REQ1 (5초 슬로우 쿼리)
                                  ├─ REQ2 (대기, 순서 강제)
                                  └─ REQ3 (대기, 순서 강제)
[Client] ← RES1, RES2, RES3 (5초 후 한꺼번에)

HTTP/2:
[Client] → HEADERS(stream=1, REQ1)
         → HEADERS(stream=3, REQ2)
         → HEADERS(stream=5, REQ3)
                            ↓
[Server] ← DATA(stream=3, RES2 chunk 1)
         ← DATA(stream=5, RES3 chunk 1)
         ← DATA(stream=3, RES2 chunk 2, END_STREAM)
         ← DATA(stream=5, RES3 chunk 2, END_STREAM)
         ← DATA(stream=1, RES1 chunk 1, END_STREAM)  ← 가장 늦게 끝남
         
→ stream 2,3은 stream 1과 무관하게 진행, 순서 무관!
```

### 🗜️ HPACK — 헤더 압축 (RFC 7541)

```
HTTP/1.1 헤더 (매 요청 그대로):
GET /api/users HTTP/1.1
Host: api.example.com
User-Agent: Mozilla/5.0 (Macintosh; ...)  ← 200+ bytes
Accept: */*
Cookie: session=eyJhbGc...                ← 1KB+
Authorization: Bearer eyJ...               ← 500+ bytes

→ 같은 페이지의 100개 자원에 똑같은 헤더 100번 반복!

HPACK:
1. Static Table (61개) — 자주 쓰는 헤더 사전 (예: index 2 = ":method GET")
2. Dynamic Table — connection별 동적 추가 (이전에 본 헤더 기억)
3. Huffman 코딩 — 문자열 압축

첫 요청:  헤더 풀텍스트 → Dynamic table에 추가 → 인덱스 부여
다음 요청: 같은 헤더 → 인덱스 한 바이트로 참조
```

| 헤더 | HTTP/1.1 평균 크기 | HPACK 압축 후 |
|---|---|---|
| `:method GET` | "GET" (3B) + line | 1 byte (static index 2) |
| `cookie: session=...` | 1KB | 인덱스 + 변경분만 |
| 100요청 누적 | 100KB | 5~20KB (90%↓) |

### 💧 Flow Control — per-stream 백프레셔

```
초기 window: 65,535 bytes (per stream, per connection)

[Client]                            [Server]
   │                                    │
   ├─ DATA(stream=1, 60KB) ──────────►  │  window: 65,535 - 60,000 = 5,535
   ├─ DATA(stream=1, 5KB) ───────────►  │  window: 535
   │                                    │  ⚠ 더 못 받음 (window 부족)
   │  ◄── WINDOW_UPDATE(stream=1, 65K)  │  ← consumer가 처리 후 윈도우 보충
   │  window: 65,535 회복               │
   ├─ DATA(stream=1, …) ─────────────►  │
```

→ 각 stream이 독립 윈도우를 갖고, connection 전체 윈도우도 따로 → **slow consumer가 다른 stream을 막지 않음**

### 🚫 Server Push — 왜 deprecated인가

원래 의도: 서버가 클라이언트 요청을 예측해서 미리 푸시.
```
Client: GET /index.html
Server: HEADERS(stream=1) "여기 index.html"
        PUSH_PROMISE(promised stream=2) "/style.css 줄 거니까 받아"
        DATA(stream=1) "<html>…"
        HEADERS(stream=2) "/style.css 응답"
        DATA(stream=2) "body{…}"
```

실제 결과:
- 브라우저가 이미 **캐시에 있는 자원도 푸시**받아 대역폭 낭비
- 캐시-인식 push 알고리즘이 너무 어려움
- Chrome은 2022년 9월 server push 지원 제거 (M106 stable, 2022-09-27)
- **RFC 9113에서 deprecated** → 대안: `103 Early Hints` (RFC 8297)

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 HTTP/2가 빛나는 영역

| # | 유즈 케이스 | 왜 HTTP/2인가 |
|---|---|---|
| 1 | **현대 웹 페이지 (자원 50+ 개)** | multiplexing으로 직렬화 제거 → LCP/FCP 개선 |
| 2 | **gRPC** | stream 기반 RPC, bidirectional streaming, trailers — [[http2-perspective-grpc-and-ecosystem]] |
| 3 | **Apple APNs (Push Notification)** | 장기 연결 위에 수많은 알림 stream |
| 4 | **Kubernetes API server** | watch 같은 long-lived stream에 적합 |
| 5 | **Envoy / Istio xDS** | control plane이 sidecar에 설정 streaming |
| 6 | **AWS ALB → 백엔드** | 백엔드 connection 수 절감 |

### ✅ 베스트 프랙티스

1. **TLS 위에서만 사용 (h2)**
   - 평문 HTTP/2 (h2c)는 명세상 가능하지만 **모든 주요 브라우저는 거부**
   - ALPN(Application-Layer Protocol Negotiation)으로 TLS 핸드셰이크 중에 h2 협상

2. **`MAX_CONCURRENT_STREAMS` 적정값 설정**
   - 너무 작으면 multiplexing 효과 ↓
   - 너무 크면 서버 메모리·CPU 압박 + DoS 위험
   - 일반적: 100~250

3. **HPACK dynamic table 크기 튜닝**
   - 기본 4096B — 커지면 압축률 ↑, 메모리 ↑
   - sensitive 헤더(`Authorization`)는 `never_indexed` 플래그로 dynamic table 제외 (CRIME류 방어)

4. **L7 로드밸런서 사용**
   - L4 LB는 connection 단위 분배 → HTTP/2 long-lived connection으로 부하 불균형
   - Envoy, ALB, nginx 등이 stream-level 인지

5. **HTTP/1.1 fallback 준비**
   - 기업 프록시·오래된 미들웨어가 HTTP/2 못 다룸 → ALPN에서 fallback

> 🔗 관련: [[http2-perspective-grpc-and-ecosystem]], [[why-http1-1-still-dominates]]

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|---|---|---|
| ✅ 장점 | **Multiplexing** | 한 TCP 위 수많은 stream → application HoL 해결 |
| ✅ 장점 | **HPACK 헤더 압축** | 반복 헤더 90%↓ 크기 |
| ✅ 장점 | **이진 형식의 효율성** | 파싱 빠름, 모호함 적음 |
| ✅ 장점 | **Stream priority/dependency** | 중요 자원 먼저 (브라우저는 RFC 9218로 이주 중) |
| ✅ 장점 | **Flow control** | per-stream 백프레셔 → slow consumer 격리 |
| ✅ 장점 | **단일 connection 모델** | per-host 6 connection 한계 해소 |
| ❌ 단점 | **TCP HoL blocking 여전** | 패킷 1개 손실 → 모든 stream 정체 (HTTP/3로만 해결) |
| ❌ 단점 | **디버깅 어려움** | 이진 → curl로는 안 보임, nghttp2/Wireshark 필요 |
| ❌ 단점 | **HPACK 보안 측면 (CRIME류)** | 헤더 압축 사이드채널, mitigation 적용해도 완전 제거는 어려움 |
| ❌ 단점 | **CPU 비용 증가** | TLS + HPACK + frame parsing |
| ❌ 단점 | **L4 LB 부하 불균형** | long-lived connection으로 connection별 trafic 차이 큼 |
| ❌ 단점 | **Rapid Reset DoS (CVE-2023-44487)** | RST_STREAM 폭주 → 서버 자원 고갈 (2023년 패치 필수) |
| ❌ 단점 | **Server push 실패** | 이론과 달리 실용성 부족 → deprecated |

---

## 6️⃣ 차이점 비교 (Comparison)

### HTTP/1.1 vs HTTP/2 핵심 매트릭스

| 항목 | HTTP/1.1 | HTTP/2 |
|---|---|---|
| **표현** | 텍스트(ASCII) | 이진 frame |
| **동시성** | 호스트당 6 TCP 병렬 | TCP 1개 + stream 수백 |
| **헤더** | 매번 풀텍스트 반복 | HPACK 압축 + dynamic table |
| **HoL blocking** | application + TCP 모두 | application은 해결, **TCP는 여전** |
| **Server push** | ❌ (long polling/SSE 우회) | ✅ → 2022 deprecated |
| **Priority** | ❌ | PRIORITY frame (deprecated) → RFC 9218 Extensible Priorities |
| **Flow control** | TCP 레벨만 | per-stream + per-connection |
| **TLS 의무** | 사실상 권장 | 사실상 강제 (브라우저는 h2 only) |
| **디버깅** | curl, telnet | nghttp2, Wireshark TLS-key export |
| **연결 수립 비용** | TCP + TLS | TCP + TLS + ALPN + SETTINGS exchange |
| **자원 분산** | 도메인 샤딩 권장 | **도메인 샤딩 안티패턴** (HPACK·multiplexing 효과 깨짐) |

### HTTP/2 vs HTTP/3 — 무엇이 다른가

| 항목 | HTTP/2 | HTTP/3 |
|---|---|---|
| **트랜스포트** | TCP + TLS | **QUIC = UDP + TLS 1.3** |
| **HoL blocking (TCP layer)** | 발생 | 해결 (UDP기반 stream) |
| **헤더 압축** | HPACK (RFC 7541) | **QPACK** (RFC 9204) |
| **0-RTT 핸드셰이크** | ❌ (TLS 1.3로 가능하지만 TCP 별도) | ✅ (QUIC 1-RTT, 재방문 0-RTT) |
| **Connection migration** | ❌ (4-tuple 변경 시 끊김) | ✅ (Wi-Fi↔LTE 이동에도 유지) |
| **방화벽 호환성** | 광범위 (TCP 80/443) | 제한적 (UDP 차단 환경 많음) |

상세는 [[http3-quic-concept-explainer]]

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|---|---|---|
| 1 | **도메인 샤딩 유지** | HPACK·multiplexing 효과 무력화, DNS·TLS 비용 증가 | 단일 도메인으로 통합 |
| 2 | **이미지 스프라이트, JS/CSS 번들링 과도** | HTTP/1.1 시대 hack, HTTP/2에서 캐시 무효화 단위가 너무 커짐 | 적정 단위로 분할 (개수 제한 완화) |
| 3 | **Server push 광범위 사용** | 캐시 hit 자원도 푸시해서 낭비 + deprecated | `103 Early Hints` 사용 |
| 4 | **`MAX_CONCURRENT_STREAMS` 과도** | DoS 노출, 서버 메모리 압박 | 100~250 권장 |
| 5 | **L4 LB 그대로 사용** | connection 단위 분배 → 부하 불균형 | L7 LB(Envoy/ALB/nginx) |
| 6 | **HTTP/2 활성화하고 HTTP/1.1 fallback 미준비** | 일부 클라이언트(레거시 프록시)에서 차단 | ALPN으로 fallback 보장 |
| 7 | **Sensitive 헤더 평문 indexing** | HPACK dynamic table에 들어가면 사이드채널 공격 면 | `never_indexed` 플래그 |

### 🔒 보안 주의점

- **HTTP/2 Rapid Reset (CVE-2023-44487)**: RST_STREAM을 광범위하게 보내 서버 stream 생성/취소 비용을 폭증시키는 DoS — 2023년 10월 발견, 2024년 초까지 모든 주요 서버(nginx, Envoy, Go, .NET) 패치 — **반드시 최신 버전 사용**
- **HPACK 사이드채널**: dynamic table에 추가되는 헤더 크기 차이로 secret을 추론하는 공격 — `never_indexed` + HSTS + CSRF token rotation으로 완화
- **Cleartext HTTP/2 (h2c)**: 명세상 가능하나 보안상 절대 비권장 — TLS 필수
- **request smuggling 변형**: HTTP/1.1 → HTTP/2 다운그레이드 경계에서 발생 (예: Cloudflare 2022년 사고)

### 🎯 성능 함정

- **TCP packet 1개 손실**: TCP는 순서 보장이라 모든 stream이 정체 — HTTP/2의 multiplexing 효과를 무력화
- **TLS 핸드셰이크 비용**: 한 connection 위에 모든 트래픽 → 첫 RTT가 매우 중요 (TLS 1.3 + ALPN 권장)
- **HPACK dynamic table sync 비용**: 서버 재시작이나 connection migration 시 처음부터 재학습

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|---|---|---|
| 📖 RFC | RFC 9113 | HTTP/2 (현행, RFC 7540 대체) |
| 📖 RFC | RFC 7541 | HPACK |
| 📖 RFC | RFC 9218 | Extensible Priorities for HTTP |
| 📖 RFC | RFC 8297 | 103 Early Hints |
| 📖 도서 | *HTTP/2 in Action* (Manning) | Barry Pollard — 실무 가이드 |
| 📖 무료 | http2 explained | Daniel Stenberg (curl 저자) — http2-explained.haxx.se |
| 📖 web.dev | Introduction to HTTP/2 | web.dev/performance-http2 |

### 🛠️ 실무 도구

| 도구 | 용도 |
|---|---|
| **nghttp2** | HTTP/2 CLI 클라이언트 + 서버 (`nghttp`, `h2load`) |
| **curl --http2** | curl 7.43+ HTTP/2 지원 |
| **h2c (golang)** | Go 표준 라이브러리 HTTP/2 디버깅 |
| **Wireshark + SSLKEYLOGFILE** | TLS 평문화 후 frame 디코딩 |
| **Chrome DevTools Network** | h2 stream/priority 시각화 |
| **chrome://net-export/** | Chrome 내부 네트워크 로그 (HTTP/2 frame 확인) |
| **Envoy / nginx / HAProxy** | HTTP/2 reverse proxy |

### 📊 알아두면 좋은 숫자

| 숫자 | 의미 |
|---|---|
| **9** | RFC 9113 frame type 개수 |
| **65,535** | 초기 flow control 윈도우 (per stream) |
| **4,096** | HPACK dynamic table 기본 크기 (bytes) |
| **100~250** | 권장 `MAX_CONCURRENT_STREAMS` |
| **2015 / 2022** | RFC 7540 / RFC 9113 발표 |
| **2023-44487** | Rapid Reset CVE 번호 |

### 💬 커뮤니티 인사이트

- HTTP/2는 **frontend 성능 개선용으로 등장**했지만, 가장 큰 수혜자는 **gRPC와 같은 backend RPC** — [[http2-perspective-grpc-and-ecosystem]]
- HTTP/2를 켰다고 자동으로 빨라지는 것은 아니다 — **도메인 샤딩 제거, 번들링 재검토** 등 응용 단 변경 필요
- `103 Early Hints`가 server push의 진정한 후계자로 정착 중 (Cloudflare, Fastly 2023년부터 광범위 지원)
- HTTP/2 Rapid Reset 이후 HTTP/2 보안 검토 풍토가 강화됨 — **patch hygiene 중요**

---

## 🔗 시리즈 노트

- [[http1-1-concept-explainer]] — HTTP/1.1 기초
- [[http1-1-problems-and-http2-evolution]] — HTTP/1.1 → HTTP/2 진화 동기
- [[why-http1-1-still-dominates]] — 왜 HTTP/1.1이 여전히 주류인가
- [[http2-perspective-grpc-and-ecosystem]] — gRPC가 HTTP/2를 어떻게 활용하는가
- [[http3-quic-concept-explainer]] — HTTP/3 + QUIC
- [[http-protocol-interview-qa]] — 면접 대비 Q&A

## 📎 Sources

1. [RFC 9113 — HTTP/2](https://www.rfc-editor.org/rfc/rfc9113)
2. [RFC 7541 — HPACK](https://www.rfc-editor.org/rfc/rfc7541)
3. [RFC 9218 — Extensible Priorities for HTTP](https://www.rfc-editor.org/rfc/rfc9218)
4. [RFC 8297 — 103 Early Hints](https://www.rfc-editor.org/rfc/rfc8297)
5. [HTTP/2 explained](https://http2-explained.haxx.se/) — Daniel Stenberg
6. [Introduction to HTTP/2 — web.dev](https://web.dev/articles/performance-http2)
7. [HTTP/2 Rapid Reset — Cloudflare](https://blog.cloudflare.com/technical-breakdown-http2-rapid-reset-ddos-attack/)
8. [Chrome to remove HTTP/2 push](https://developer.chrome.com/blog/removing-push/)
