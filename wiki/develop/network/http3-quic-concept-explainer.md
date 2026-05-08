---
tags: [http, http3, quic, network-protocol, backend, concept-explainer]
created: 2026-04-28
---

# 📖 HTTP/3 + QUIC — Concept Deep Dive

> 💡 **한줄 요약**: HTTP/3는 **HTTP/2의 의미론을 그대로 두면서 트랜스포트를 TCP→QUIC(UDP+TLS 1.3+multi-stream)으로 바꾼** 프로토콜이다. TCP HoL blocking 해결, 0-RTT 핸드셰이크, Wi-Fi↔LTE 전환에도 연결 유지(connection migration)가 핵심 이득이고, 그 대가로 UDP 차단·L4 LB 비호환·디버깅 어려움을 받는다.

---

## 1️⃣ 무엇인가? (What is it?)

HTTP/3는 **2022년 RFC 9114**로 표준화된 HTTP 의미론(GET/POST/200/Header)을 그대로 유지하되, 트랜스포트 계층을 **QUIC(RFC 9000)** 으로 교체한 버전이다. QUIC는 Google이 2012년부터 실험해 온 **UDP 기반 + TLS 1.3 통합 + multi-stream** 신뢰성 프로토콜이다. 즉:

```
HTTP/2  =  HTTP semantics + binary frame + TCP + TLS
HTTP/3  =  HTTP semantics + binary frame + QUIC (= UDP + TLS 1.3 + stream)
                                           ▲
                                    여기가 결정적 차이
```

🎯 **현실 비유**: HTTP/2가 **"한 컨테이너 트럭에 여러 박스를 실어 보내지만 트럭은 정해진 도로(TCP)만 다닐 수 있고, 도로 한 곳이 막히면 모든 박스가 같이 멈추는 시스템"** 이라면, HTTP/3는 **"각 박스가 독립적으로 GPS(QUIC stream ID)와 신뢰성 보장(QUIC reliability layer)을 가진 자율주행 드론으로 날아가는 시스템"** — 도로가 막혀도 다른 박스는 멈추지 않는다.

### 📜 탄생 배경

- **2012**: Google이 QUIC(Quick UDP Internet Connections) 실험 시작 — Chrome ↔ Google 서비스
- **2016**: IETF QUIC WG 결성 — Google QUIC을 표준화 작업
- **2018**: HTTP-over-QUIC을 **HTTP/3**로 명명 결정
- **2020**: QUIC v1 draft 안정화
- **2022 5월**: **RFC 9000 (QUIC core), 9001 (QUIC TLS), 9002 (Loss Detection)** 발표
- **2022 6월**: **RFC 9114 (HTTP/3), 9204 (QPACK)** 발표
- **2024~**: Cloudflare/Google/Meta/Akamai 광범위 사용. Web Almanac 2024 기준 트래픽 ~30% 도달

> 📌 **핵심 키워드**: `QUIC`, `UDP`, `connection migration`, `0-RTT`, `QPACK`, `Stream`, `ALPN h3`, `Alt-Svc`, `multipath QUIC`, `MASQUE`

---

## 2️⃣ 핵심 개념 (Core Concepts)

### QUIC가 한 패키지로 묶은 것

```
HTTP/2 stack (총 핸드셰이크 ≥ 2 RTT):           HTTP/3 stack (1 RTT, 재방문 0-RTT):
┌──────────────────────┐                       ┌──────────────────────┐
│ HTTP/2 frame         │                       │ HTTP/3 frame         │
├──────────────────────┤                       ├──────────────────────┤
│ TLS 1.2/1.3          │ ← 별도 핸드셰이크      │ QUIC                 │
├──────────────────────┤                       │  + TLS 1.3 통합       │
│ TCP                  │ ← 별도 핸드셰이크      │  + Stream multiplex  │
├──────────────────────┤                       │  + Reliability       │
│ IP                   │                       │  + Congestion ctrl   │
└──────────────────────┘                       ├──────────────────────┤
                                               │ UDP                  │ ← 핸드셰이크 없음
                                               ├──────────────────────┤
                                               │ IP                   │
                                               └──────────────────────┘
```

### QUIC의 4가지 결정적 기능

| 기능 | 설명 |
|---|---|
| **UDP 기반 + 사용자 공간 reliability** | 운영체제 TCP 스택을 우회 → 진화 속도 빠름 |
| **TLS 1.3 통합 핸드셰이크** | 1 RTT, 재방문 0-RTT |
| **Connection ID 기반 식별** | 4-tuple(IP+port) 변경에도 connection 유지 (= **connection migration**) |
| **Stream 독립 reliability** | 한 stream의 패킷 손실이 다른 stream에 영향 없음 (TCP HoL 해결) |

### 0-RTT vs 1-RTT 핸드셰이크

```
TLS 1.3 over TCP (HTTP/2):
  RTT 1: TCP SYN → SYN-ACK → ACK
  RTT 2: ClientHello → ServerHello + Cert + Finished
  RTT 3: 첫 application data
  → 총 ~2 RTT (실제로는 TCP+TLS 합쳐 측정)

QUIC 1-RTT (HTTP/3 첫 방문):
  RTT 1: Initial(ClientHello) → Initial(ServerHello + Cert)
  RTT 2: 첫 application data
  → 총 1 RTT

QUIC 0-RTT (재방문):
  RTT 0: Initial(ClientHello + cached secret + DATA) → server에 즉시 도착
  → 첫 byte부터 application data 포함

⚠️ 0-RTT data는 replay 가능 → idempotent 요청만 (GET/HEAD)
```

### Connection Migration — 모바일에서 결정적

```
TCP connection (HTTP/1.1·2):
  identifier = (src_IP, src_port, dst_IP, dst_port)
  
  사용자가 Wi-Fi → LTE 전환:
    src_IP 변경 → 4-tuple 변경 → TCP는 끊김
    → application은 reconnect 필요 (TLS 재핸드셰이크 + state 복원)
    → 영상 스트리밍 끊김, 게임 disconnect

QUIC connection:
  identifier = Connection ID (8~20 byte 랜덤 ID)
  
  Wi-Fi → LTE 전환:
    src_IP/port 변경 → 그러나 Connection ID 그대로
    → server가 같은 connection으로 인식
    → 일시적 path validation 후 즉시 재개 (수 ms)
    → 영상 끊김 없음, 게임 끊김 없음
```

### Stream — TCP HoL의 진정한 해결

```
HTTP/2 over TCP, 패킷 1개 손실:
  TCP buffer:  [pkt1][pkt2][pkt3:lost][pkt4][pkt5]
                                        ▲
                            OS는 pkt4,5를 보유하지만 application에 안 넘김
                            (TCP는 순서 보장이라)
  
  → HTTP/2 stream A, B, C 모두 정체
  → application HoL은 해결, TCP HoL은 잔존

HTTP/3 over QUIC, 같은 손실:
  Stream 1 packets: [s1p1][s1p2:lost][s1p3]    ← s1만 영향
  Stream 2 packets: [s2p1][s2p2][s2p3]         ← 진행 정상
  Stream 3 packets: [s3p1][s3p2][s3p3]         ← 진행 정상
  
  → 손실은 stream 1만 정체 → 다른 stream은 즉시 application으로
  → 진정한 HoL 해결
```

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

### HTTP/3 협상 (Alt-Svc)

브라우저가 HTTP/3를 쓰려면 **서버가 HTTP/3를 지원한다는 사실을 먼저 알아야** 한다:

```
1. 첫 방문: 브라우저가 HTTP/2 (TCP+TLS+ALPN h2)로 접속
   → server 응답에 헤더:
     Alt-Svc: h3=":443"; ma=86400
   
2. 다음 방문: 브라우저가 UDP 443으로 QUIC 시도
   → 성공 시 HTTP/3 (ALPN "h3")
   → UDP 차단 등 실패 시 HTTP/2 fallback
```

또는 **DNS HTTPS RR 레코드**(RFC 9460)로 첫 방문에서도 HTTP/3 시도 가능:
```
example.com.  HTTPS  1 . alpn="h3,h2"  ipv4hint=...
```

### QPACK — 왜 HPACK을 못 쓰는가

```
HPACK의 전제: dynamic table 업데이트가 stream 사이에 순서대로 도착
  → HTTP/2는 TCP라서 이 가정이 성립

HTTP/3 over QUIC:
  → stream이 비순차 도착 가능 (그게 QUIC의 장점!)
  → HPACK의 순서 의존 → HoL 재발생 → 무용지물

QPACK (RFC 9204):
  → encoder stream과 decoder stream 분리
  → 동적 table 업데이트는 별도 unidirectional stream으로
  → 헤더 frame은 dynamic table 참조 시 "이 인덱스 사용 가능 여부 ack 받은 뒤" 사용
  → 비순차 도착에도 동작
```

### QUIC packet 형식 (단순화)

```
Long Header (handshake 시):
+-+-+-+-+-+-+-+-+
|1|1|T T|RES|PNL|     ← Header form, Long, Type, Reserved, Packet Number Length
+-+-+-+-+-+-+-+-+
|         Version (32)         |
+-+-+-+-+-+-+-+-+
| DCIL | SCIL  |              ← Destination/Source Connection ID Length
+-+-+-+-+-+-+-+-+
| Destination Connection ID (variable)
+-+-+-+-+-+-+-+-+
| Source Connection ID (variable)
+-+-+-+-+-+-+-+-+
| Packet Number (variable)
| Payload (encrypted with TLS 1.3 keys)
+-+-+-+-+-+-+-+-+

Short Header (1-RTT 이후 일반 데이터):
+-+-+-+-+-+-+-+-+
|0|1|...           ← Header form, Fixed bit, …
+-+-+-+-+-+-+-+-+
| Destination Connection ID (variable)
| Packet Number (variable)
| Payload (encrypted)
+-+-+-+-+-+-+-+-+
```

대부분의 메타데이터가 **암호화**된다 (Connection ID 정도만 평문) — middlebox 침투를 막는 설계.

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 HTTP/3가 큰 효과를 보는 시나리오

| # | 유즈 케이스 | 왜 HTTP/3인가 |
|---|---|---|
| 1 | **모바일 영상 스트리밍** (YouTube, Netflix) | connection migration + TCP HoL 해결 |
| 2 | **글로벌 SaaS** (Google Workspace, Meta) | 0-RTT로 cold start 단축, 패킷 손실 환경 강건 |
| 3 | **고품질 화상 회의** (Google Meet) | 양방향 stream 안정성 |
| 4 | **온라인 게임 매치메이킹** | 0-RTT로 매치 시간 단축, 모바일 핸드오프에도 끊김 X |
| 5 | **CDN 글로벌 트래픽** (Cloudflare, Fastly) | edge ↔ user 구간 latency 개선 |
| 6 | **광고 실시간 입찰 (RTB)** | latency-sensitive |

### ✅ 베스트 프랙티스

1. **HTTP/2 fallback은 필수**
   - UDP 차단·기업 방화벽·구식 클라이언트 → HTTP/2로 자동 강등
   - Alt-Svc 헤더 + ALPN으로 안전하게 협상

2. **0-RTT는 idempotent 요청만**
   - GET/HEAD/OPTIONS만 0-RTT
   - POST/PUT/DELETE는 1-RTT 강제 (replay 공격 방지)

3. **Connection ID rotation**
   - 같은 Connection ID를 영원히 쓰면 추적 가능 → 주기적 rotation
   - QUIC 명세는 NEW_CONNECTION_ID frame으로 지원

4. **CPU/메모리 비용 모니터링**
   - QUIC은 사용자 공간 처리 → CPU 사용량 HTTP/2 대비 1.5~2배 보고됨
   - kernel UDP segmentation offload(GSO/GRO) 활성화로 완화

5. **L7 LB 사용**
   - L4 LB는 4-tuple 기반 분배 → connection migration 인식 못 함
   - HTTP/3 native LB (Cloudflare, Envoy with QUIC, AWS CloudFront 등) 필요

> 🔗 관련: [[http2-concept-explainer]] (fallback 비교)

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|---|---|---|
| ✅ 장점 | **TCP HoL 해결** | 패킷 손실에 강건 |
| ✅ 장점 | **0-RTT 재방문** | latency 단축 |
| ✅ 장점 | **Connection migration** | Wi-Fi↔LTE 끊김 없음 |
| ✅ 장점 | **TLS 1.3 강제** | downgrade attack 차단 |
| ✅ 장점 | **메타데이터 암호화** | middlebox ossification 방어 |
| ✅ 장점 | **사용자 공간 진화** | OS 업데이트 없이 프로토콜 개선 |
| ❌ 단점 | **UDP 차단 환경** | 기업 방화벽·일부 ISP가 UDP 제한 |
| ❌ 단점 | **CPU 비용 증가** | TCP 대비 1.5~2배 보고 (워크로드별) |
| ❌ 단점 | **L4 LB 비호환** | connection migration·encrypted header 처리 못 함 |
| ❌ 단점 | **디버깅 도구 미성숙** | Wireshark QUIC dissector는 있으나 secret key 필요 |
| ❌ 단점 | **0-RTT replay 위험** | idempotent만 안전 |
| ❌ 단점 | **MTU 의존성** | UDP는 fragmentation 회피해야 함 → 1200 byte 권장 |
| ❌ 단점 | **DDoS 방어 다름** | UDP amplification 우려, 별도 방어 설계 필요 |

---

## 6️⃣ 차이점 비교 (Comparison)

### HTTP/2 vs HTTP/3 — 핵심 매트릭스

| 항목 | HTTP/2 | HTTP/3 |
|---|---|---|
| **트랜스포트** | TCP + TLS 1.2/1.3 | QUIC (UDP + TLS 1.3) |
| **TCP HoL blocking** | ❌ 발생 | ✅ 해결 |
| **첫 핸드셰이크** | ~2 RTT | 1 RTT |
| **재방문 핸드셰이크** | TLS 1.3로 1 RTT (TCP 별도) | **0 RTT** (idempotent만) |
| **Connection migration** | ❌ | ✅ |
| **헤더 압축** | HPACK | QPACK |
| **방화벽 호환성** | 광범위 (TCP 80/443) | 제한적 (UDP 443) |
| **L4 LB** | 잘 동작 | 비호환 (Connection ID 인식 필요) |
| **CPU 비용** | 보통 | 1.5~2배 |
| **사용자 공간 stack** | OS 의존 (TCP) | 사용자 공간 (libquic, msquic, quiche) |
| **Wireshark 디버깅** | TLS key export로 가능 | QUIC dissector + key export |
| **표준 RFC** | RFC 9113 | RFC 9114 (HTTP/3) + RFC 9000 (QUIC) |

### TCP vs QUIC — 트랜스포트 단

| 항목 | TCP | QUIC |
|---|---|---|
| **위치** | 커널 | 사용자 공간 |
| **신뢰성** | sequence number, ACK, retransmit | sequence + offset, ACK, retransmit |
| **Stream** | 단일 byte stream | 다중 stream, 독립 reliability |
| **혼잡 제어** | 다양한 알고리즘(CUBIC/BBR) | TCP 알고리즘 차용 가능, 또는 자체 |
| **암호화** | optional (TLS 별도) | mandatory (TLS 1.3 내장) |
| **연결 식별** | 4-tuple | Connection ID |
| **0-RTT** | TLS 1.3 + TFO 조합 가능 | 빌트인 |
| **진화 속도** | OS update 필요 | application 업데이트로 가능 |

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|---|---|---|
| 1 | **HTTP/3만 활성화하고 fallback 미준비** | UDP 차단 환경에서 접속 실패 | HTTP/2 fallback 필수 (Alt-Svc) |
| 2 | **POST를 0-RTT로 보냄** | replay 공격 위험 | GET/HEAD만 0-RTT 허용 |
| 3 | **L4 LB로 HTTP/3 트래픽 분배** | connection migration 깨짐 | HTTP/3 native LB |
| 4 | **MTU 1500으로 UDP 가정** | path MTU < 1500이면 fragmentation 발생, QUIC은 fragment 거부 | 1200 byte 권장 |
| 5 | **방화벽에서 UDP 443 차단된 환경 무시** | 사용자 일부 접속 불가 | HTTP/2 fallback 필수 |
| 6 | **HPACK 도구로 디버깅** | QPACK은 다른 알고리즘 | QPACK 도구 사용 |
| 7 | **CPU 모니터링 누락** | UDP 처리 비용으로 서비스 저하 | GSO/GRO + kTLS 등 활용 |

### 🔒 보안 주의점

- **0-RTT replay**: TLS 1.3과 동일 — server는 anti-replay (token bucket, single-use ticket) 적용 필요
- **UDP amplification DDoS**: QUIC handshake 응답 크기 제한 (3x rule), 패딩 적용
- **Connection ID linkability**: 같은 ID 영구 사용 시 device tracking 가능 → rotation 필수
- **Middlebox ossification 방어**: 메타데이터 암호화로 침투 차단 — 다만 enterprise inspection 도구가 어려워짐 (분리된 정책 필요)

### 🎯 성능 함정

- **kernel UDP 처리 비용**: TCP는 NIC 오프로드 + 커널 최적화가 성숙, UDP는 application까지 올라옴 → CPU 부담
- **Path MTU discovery 복잡**: UDP는 ICMP fragmentation 의존 못 함 → DPLPMTUD (RFC 8899) 사용
- **NAT timeout**: UDP는 NAT가 빠르게 timeout → keep-alive (PING) 필요

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|---|---|---|
| 📖 RFC | RFC 9000 | QUIC core |
| 📖 RFC | RFC 9001 | Using TLS to Secure QUIC |
| 📖 RFC | RFC 9002 | Loss Detection and Congestion Control |
| 📖 RFC | RFC 9114 | HTTP/3 |
| 📖 RFC | RFC 9204 | QPACK |
| 📖 RFC | RFC 9460 | DNS HTTPS RR (HTTP/3 advertise) |
| 📖 책 | *HTTP/3 Explained* | Daniel Stenberg (curl 저자) — 무료 (http3-explained.haxx.se) |
| 📖 web.dev | HTTP/3 Deep Dive | web.dev/articles/performance-http3 |
| 📖 Cloudflare | The Road to HTTP/3 | blog.cloudflare.com/the-road-to-quic |

### 🛠️ 실무 도구·구현

| 도구/라이브러리 | 용도 |
|---|---|
| **curl --http3** | curl 7.66+ 실험적, 빌드 시 quiche/ngtcp2 필요 |
| **quiche** (Cloudflare) | Rust 라이브러리, Cloudflare 프로덕션 사용 |
| **msquic** (Microsoft) | C 라이브러리, Windows·Linux |
| **ngtcp2 + nghttp3** | C 라이브러리, curl 기본 |
| **quic-go** | Go QUIC 구현 |
| **aioquic** | Python QUIC, 학습용 좋음 |
| **Wireshark + SSLKEYLOGFILE** | QUIC packet 디코딩 |
| **qlog / qvis** | QUIC 표준 로그 포맷 + 시각화 |

### 📊 알아두면 좋은 숫자

| 숫자 | 의미 |
|---|---|
| **8~20** | Connection ID 길이 (bytes) |
| **1200** | 권장 QUIC 초기 MTU (UDP fragment 회피) |
| **3x** | amplification 방지 응답 크기 비율 |
| **2022 6월** | RFC 9114 (HTTP/3) 발표 |
| **~30%** | Web Almanac 2024 HTTP/3 트래픽 점유율 |

### 💬 커뮤니티 인사이트

- HTTP/3 채택은 **사용자 경험 측면에서 모바일 사용자가 많은 서비스가 먼저** (YouTube, Meta, TikTok)
- **B2B SaaS, 기업 내부 시스템은 HTTP/2로 충분** — UDP 차단·L4 LB 호환성·디버깅 비용이 우선
- **Multipath QUIC** (draft 진행) — Wi-Fi + LTE 동시 사용으로 throughput 향상
- **MASQUE** (RFC 9298 등) — VPN/proxy를 QUIC 위에서 통일 (Apple Private Relay가 사용)
- HTTP/3는 **HTTP/2를 즉시 대체하지 않는다** — 둘은 당분간 공존

---

## 🔗 시리즈 노트

- [[http1-1-concept-explainer]]
- [[http2-concept-explainer]]
- [[http1-1-problems-and-http2-evolution]]
- [[why-http1-1-still-dominates]]
- [[http2-perspective-grpc-and-ecosystem]]
- [[http-protocol-interview-qa]]

## 📎 Sources

1. [RFC 9000 — QUIC: A UDP-Based Multiplexed and Secure Transport](https://www.rfc-editor.org/rfc/rfc9000)
2. [RFC 9001 — Using TLS to Secure QUIC](https://www.rfc-editor.org/rfc/rfc9001)
3. [RFC 9002 — QUIC Loss Detection and Congestion Control](https://www.rfc-editor.org/rfc/rfc9002)
4. [RFC 9114 — HTTP/3](https://www.rfc-editor.org/rfc/rfc9114)
5. [RFC 9204 — QPACK](https://www.rfc-editor.org/rfc/rfc9204)
6. [RFC 9460 — DNS HTTPS RR](https://www.rfc-editor.org/rfc/rfc9460)
7. [HTTP/3 Explained — Daniel Stenberg](https://http3-explained.haxx.se/)
8. [The Road to HTTP/3 — Cloudflare](https://blog.cloudflare.com/the-road-to-quic/)
9. [Web Almanac 2024 — HTTP](https://almanac.httparchive.org/en/2024/http)
10. [QUIC at Google — design and lessons](https://www.chromium.org/quic/)
