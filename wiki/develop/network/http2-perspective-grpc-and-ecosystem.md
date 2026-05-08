---
tags: [http, http2, grpc, ecosystem, network-protocol, deep-research]
created: 2026-04-28
---

# 🔌 HTTP/2 관점에서 본 gRPC, 그리고 HTTP/2 위에서 동작하는 시스템들

> 💡 **한줄 요약**: gRPC는 HTTP/2의 모든 핵심 기능(stream multiplexing, HPACK, flow control, **trailers**, bidirectional)을 RPC 의미론으로 그대로 매핑한 시스템이다. 그래서 gRPC는 **HTTP/2 없이는 존재할 수 없다**. gRPC 외에도 Apple APNs, Web Push, Kubernetes API server, Envoy xDS, AWS ALB 등이 HTTP/2를 핵심 인프라로 사용한다.

> ⚠️ 이 노트는 **gRPC 사용법**(API, codegen, stub 작성법)을 다루지 않는다. gRPC 사용법은 [[grpc-concept-deep-dive]]를 참고. 본 노트는 **gRPC가 HTTP/2를 어떻게 쓰는가**의 프로토콜 관점만 다룬다.

---

## 1️⃣ gRPC가 HTTP/2를 활용하는 방식 — 기능별 매핑표

| gRPC 기능 | HTTP/2 메커니즘 | 어떻게 매핑되는가 |
|---|---|---|
| **RPC 1건** | **Stream 1개** (HEADERS → DATA → trailing HEADERS) | 한 RPC = 한 stream lifetime |
| **요청 metadata** (Auth, deadline, …) | **HEADERS frame** | gRPC metadata = HTTP/2 헤더로 인코딩 |
| **요청/응답 body** | **DATA frame** | length-prefixed protobuf message |
| **Streaming RPC** (server/client/bidi) | Stream lifetime을 길게 유지 | DATA frame을 여러 개 연속 송수신 |
| **응답 status code** (`OK`, `NOT_FOUND`, …) | **Trailing HEADERS (Trailers)** | `grpc-status`, `grpc-message` 헤더로 본문 뒤에 도착 |
| **Backpressure** | **per-stream WINDOW_UPDATE** | gRPC consumer가 빨리 못 받으면 producer가 자동 멈춤 |
| **헤더 효율** | **HPACK** | 반복되는 metadata 압축 |
| **요청 취소** | **RST_STREAM** | client가 deadline 만료 → RST_STREAM으로 즉시 종료 |
| **연결 종료 시그널** | **GOAWAY** | server graceful shutdown |
| **Keep-alive** | **PING** | 양쪽 모두 ping으로 dead connection 감지 |
| **다중 RPC 동시 진행** | **Multiplexing** | 한 connection으로 수백 RPC 동시 |

---

## 2️⃣ 한 RPC의 wire-level 모습

```
gRPC Unary RPC: client.SayHello(ctx, &HelloRequest{Name: "Alice"})

[Client]                                          [Server]
   │                                                  │
   ├──────────── HEADERS frame (stream=3) ─────────►  │
   │   :method = POST                                 │
   │   :scheme = https                                │
   │   :path   = /helloworld.Greeter/SayHello         │
   │   :authority = api.example.com                   │
   │   te = trailers                                  │
   │   content-type = application/grpc                │
   │   grpc-encoding = gzip                           │
   │   grpc-timeout = 5S                              │
   │                                                  │
   ├──────────── DATA frame (stream=3) ────────────►  │
   │   [0x00][len:4][protobuf payload of Hello]       │
   │   END_STREAM flag                                │
   │                                                  │
   │                                                  │ ← server 처리
   │                                                  │
   │   ◄────────── HEADERS frame (stream=3) ──────────┤
   │      :status = 200                               │
   │      content-type = application/grpc             │
   │                                                  │
   │   ◄────────── DATA frame (stream=3) ─────────────┤
   │      [0x00][len:4][protobuf payload of HelloRes] │
   │                                                  │
   │   ◄────────── HEADERS frame (stream=3, trailer) ─┤
   │      grpc-status  = 0  (OK)                      │
   │      grpc-message = ""                           │
   │      END_STREAM flag                             │
```

**중요**: 응답 status가 본문 **뒤**의 trailing HEADERS로 도착한다. 이 점이 HTTP/1.1로는 불가능한 이유 — HTTP/1.1에는 trailer 개념이 거의 사용되지 않고 브라우저가 expose하지 않는다.

---

## 3️⃣ DATA frame 안의 메시지 구조 (length-prefixed)

```
gRPC 메시지 1건 = 5 byte prefix + protobuf payload

  Byte 0:    Compression flag (0=raw, 1=compressed)
  Byte 1-4:  Big-endian message length (uint32)
  Byte 5+:   Protobuf-encoded message bytes

→ DATA frame 하나에 메시지 N개가 들어갈 수 있다 (특히 streaming RPC).
→ HTTP/2 frame과 별도의 framing layer 필요한 이유 = streaming RPC에서 메시지 경계를 알아야 함.
```

---

## 4️⃣ Streaming RPC와 HTTP/2 stream lifetime

| RPC 타입 | Stream 사용 패턴 |
|---|---|
| **Unary** | client: HEADERS+DATA+END / server: HEADERS+DATA+TRAILER |
| **Server streaming** | client: HEADERS+DATA+END / server: HEADERS+DATA+DATA+…+TRAILER |
| **Client streaming** | client: HEADERS+DATA+DATA+…+END / server: HEADERS+DATA+TRAILER |
| **Bidirectional** | 양쪽 모두 DATA frame을 자유롭게 송수신, 마지막에 server가 TRAILER 보냄 |

**Bidirectional streaming은 HTTP/1.1에서 절대 불가능**: 한 connection 한 방향씩만 진행하는 HTTP/1.1로는 양방향 동시 전송이 안 된다 (WebSocket은 별도 프로토콜).

---

## 5️⃣ 왜 브라우저는 native gRPC를 못 쓰는가

```
HTTP/2 trailing HEADERS:
  - HTTP/2 명세상 정상 기능 ✅
  - 브라우저 Fetch API: trailers를 application에 expose하지 않음 ❌
  - XHR: trailers 접근 불가 ❌

→ gRPC의 status code(grpc-status)는 trailer로 오므로 브라우저가 받을 수 없음
→ 해결책:
   1. gRPC-Web: HTTP/1.1·2 호환, trailer를 본문 끝에 인코딩
   2. Connect: gRPC와 호환되면서 HTTP/1.1까지 fallback 가능
   3. envoy grpc-web filter: gRPC-Web ↔ native gRPC 변환
```

> 🔗 상세: [[grpc-concept-deep-dive]] (gRPC-Web, Connect 비교)

---

## 6️⃣ Flow Control — gRPC backpressure의 정체

```
gRPC server streaming, server가 초당 10MB 생성 / client가 초당 1MB 처리:

[Server] ──DATA(stream=3, 1MB)──► [Client]    window: 65535 - 65535 = 0
         ──DATA(stream=3, 64K)──►              ← block! window 부족
         (서버가 stream 측 송신 멈춤)
         
[Client] consumer가 메시지 처리 후
         ◄── WINDOW_UPDATE(stream=3, 64K) ──   window 회복
         
[Server] ──DATA(stream=3, …)────►              송신 재개
```

→ **backpressure가 transport layer에 빌트인** = application 코드에 별도 throttling 안 짜도 됨
→ HTTP/1.1로는 직접 구현해야 함 (chunk 수동 관리, ACK 메시지 정의 등)

---

## 7️⃣ HPACK과 gRPC metadata

gRPC는 메타데이터를 매 RPC에 보낸다 — auth token, request ID, trace context, deadline 등:
```
authorization: Bearer eyJhbGc...           (~500B)
x-request-id: 7f3a...                      (~50B)
traceparent: 00-...                        (~60B)
grpc-timeout: 5S                           (~20B)
content-type: application/grpc             (~30B)

총 ~700B per RPC
```

같은 connection에서 1000 RPC → 700KB 헤더 트래픽
HPACK 압축 시: 첫 RPC 700B + 999 × ~30B(인덱스만) = ~30KB → 95%↓

→ gRPC가 마이크로서비스 간 통신에서 효율적인 핵심 이유 중 하나

---

## 8️⃣ gRPC over HTTP/3 — 현재 상황 (2024~2025)

```
표준화: IETF에서 논의 중 (draft-ietf-httpbis-... 진행)
구현 현황:
  - grpc-go: 실험적 지원, production 권장 안 함
  - grpc-java: 미지원
  - grpc-js (Node.js): 미지원
  - .NET Core: 부분 지원
  - Cloudflare/Google internal: 일부 사용

장점:
  - QUIC connection migration → 모바일 네트워크 변경에도 RPC 지속
  - 0-RTT → cold start 시 latency ↓
  - TCP HoL blocking 해결 → 패킷 손실 환경에서 더 안정

장벽:
  - 기업망 UDP 차단
  - L4/L7 LB 호환성 (HTTP/3 native 지원 LB 적음)
  - 디버깅 도구 미성숙 (Wireshark QUIC 지원은 있으나 HPACK/QPACK 분석 도구 적음)
  - protocol buffer + QUIC 결합의 검증 사례 부족
```

> 📌 **요점**: 가까운 미래에도 gRPC = HTTP/2가 디폴트. HTTP/3는 옵션.

> 🔗 상세는 [[http3-quic-concept-explainer]]

---

## 9️⃣ gRPC 외에 HTTP/2를 핵심 인프라로 쓰는 시스템들

### A. Apple APNs (Apple Push Notification service)
```
2015년 이전: 자체 binary protocol (proprietary)
2015년 이후: HTTP/2 API로 전환

이유:
  - 한 connection으로 수많은 device push 동시 전송 (multiplexing)
  - 응답 status를 HTTP/2 status code로 명확화
  - 표준 도구(Postman/curl)로 디버깅 가능
  - 안정적 long-lived connection (PING으로 keep-alive)

특징:
  - JWT auth 헤더가 매 요청 → HPACK 압축 효과 큼
  - device token 별 stream 동시 진행
  - server가 throttle 시 GOAWAY로 graceful shutdown
```

### B. Web Push (RFC 8030)
```
브라우저 ↔ Push service 사이 표준:
  - Subscription endpoint = HTTP/2 over TLS
  - VAPID(JWT) 인증 헤더
  - Push payload는 한 번에 1KB~4KB 제한
  - server-side encryption(RFC 8291)
  
HTTP/2를 쓰는 이유:
  - 수백만 구독 device로 동시 push할 때 multiplexing 효과
  - 표준 HTTP infrastructure 재사용 (별도 binary protocol 불필요)
```

### C. Kubernetes API server
```
kubectl, controller, operator가 모두 HTTP/2로 API server에 접속:

핵심 기능:
  - Watch API: long-lived stream으로 리소스 변경 이벤트 push
  - HTTP/2 stream 1개에 watch 1개 (수십 watch 동시)
  - HPACK으로 ServiceAccount token, RBAC user 헤더 압축
  - mTLS over HTTP/2

→ HTTP/1.1로는 watch가 어렵다 (각 watch마다 long-lived connection 필요)
→ HTTP/2가 K8s 운영의 backbone
```

### D. Envoy / Istio xDS (Discovery Service)
```
xDS = gRPC streaming을 통한 동적 설정 분배
  - LDS (Listener), RDS (Route), CDS (Cluster), EDS (Endpoint), SDS (Secret)
  - control plane(Istiod) → sidecar(Envoy) bidirectional stream
  - 변경 발생 시 즉시 push (incremental delta xDS)

→ 이게 service mesh의 brain — HTTP/2 streaming 없이는 작동 불가
```

### E. AWS ALB → 백엔드
```
ALB는 viewer 측에서 HTTP/2/3 지원 + 백엔드 protocol 옵션:
  - 디폴트: HTTP/1.1 (대부분 케이스)
  - 옵션: HTTP/2 (gRPC 백엔드용, 'gRPC' protocol 선택 시)
  - HTTP/2 over TLS: ALPN 협상

→ 사용자 → ALB는 HTTP/2 종료, 백엔드는 보통 HTTP/1.1
   (단, gRPC 백엔드면 HTTP/2 그대로 forward)
```

### F. 기타 시스템
| 시스템 | HTTP/2 사용 위치 |
|---|---|
| **Cloudflare Workers** server-side fetch | edge worker 내부 fetch가 HTTP/2 |
| **Twirp** (Twitch RPC) | gRPC 호환, HTTP/1.1·2 혼용 가능 |
| **Connect (Buf)** | gRPC 호환 + 브라우저 친화 |
| **Tonic** (Rust gRPC) | tokio + hyper HTTP/2 |
| **Helm v3** chart repository | OCI registry over HTTP/2 |
| **GitHub Actions runner registration** | HTTP/2 streaming |
| **Datadog APM agent** | trace export HTTP/2 옵션 |

---

## 🔟 핵심 정리

1. **gRPC ≠ HTTP/2 위의 RPC 라이브러리**, gRPC ≈ **HTTP/2의 RPC 사용 사례 그 자체**
2. **trailers의 활용**이 gRPC를 HTTP/2에 묶는 결정적 이유 — HTTP/1.1로는 불가
3. **HPACK + multiplexing**이 마이크로서비스 metadata 비용을 압도적으로 줄임
4. **Bidirectional streaming**은 HTTP/2 stream의 자연스러운 확장 — WebSocket과 비교해 HTTP 인프라 친화적
5. **브라우저 native gRPC 차단**은 Fetch API의 trailer 비공개 때문 — gRPC-Web/Connect로 우회
6. **gRPC over HTTP/3**는 실험 단계, 운영은 HTTP/2가 디폴트
7. **HTTP/2 사용처는 gRPC만 아니다** — APNs, Web Push, K8s, Envoy xDS, ALB 등 인프라 골격
8. **HTTP/2 없이는 현대 service mesh가 작동하지 않는다** — xDS streaming은 HTTP/2의 결정적 활용

---

## 🔗 시리즈 노트

- [[http2-concept-explainer]]
- [[grpc-concept-deep-dive]] — gRPC 사용법, Protobuf, anti-patterns
- [[http3-quic-concept-explainer]] — gRPC over HTTP/3 가능성
- [[http-protocol-interview-qa]] — 면접 Q&A

## 📎 Sources

1. [gRPC over HTTP/2 — Protocol Design](https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md)
2. [RFC 9113 — HTTP/2 (trailers, frames)](https://www.rfc-editor.org/rfc/rfc9113)
3. [Apple APNs HTTP/2 API](https://developer.apple.com/documentation/usernotifications/sending_notification_requests_to_apns)
4. [RFC 8030 — Generic Event Delivery Using HTTP Push (Web Push)](https://www.rfc-editor.org/rfc/rfc8030)
5. [Kubernetes API server protocol](https://kubernetes.io/docs/concepts/architecture/control-plane-node-communication/)
6. [Envoy xDS protocol](https://www.envoyproxy.io/docs/envoy/latest/api-docs/xds_protocol)
7. [AWS ALB gRPC support](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html)
8. [Connect: gRPC-compatible alternative](https://connectrpc.com/)
9. [grpc-web project](https://github.com/grpc/grpc-web)
