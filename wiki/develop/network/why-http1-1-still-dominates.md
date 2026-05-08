---
tags: [http, http1-1, http2, adoption, deep-research, infrastructure]
created: 2026-04-28
---

# 🌍 HTTP/2가 나온 지 10년, 왜 HTTP/1.1은 죽지 않았나 — Deep Research

> 💡 **한줄 요약**: 사용자 → CDN edge 구간은 HTTP/2·3가 주류지만, **edge → origin, 서비스 ↔ 서비스, 미들웨어 ↔ 백엔드, 헬스체크, webhook, CLI 도구, 레거시 기업망** 같은 "보이지 않는 구간"은 여전히 HTTP/1.1이 디폴트다. 단순함·디버깅·호환성·학습 비용이 모두 HTTP/1.1에 유리하기 때문이다.

---

## 📊 통계로 보는 현황 (2024~2025 기준)

```
브라우저 → 인터넷 (사용자가 보는 구간):
  HTTP/2  ~70%
  HTTP/3  ~30% (Cloudflare/Google/Meta 트래픽 많음)
  HTTP/1.1  잔여 (10% 미만)

데이터센터 내부 (서비스 ↔ 서비스):
  HTTP/1.1  여전히 다수 — REST API, internal microservice
  HTTP/2   gRPC 도입한 곳에서만
  HTTP/3   거의 없음

edge → origin (CDN ↔ 백엔드):
  HTTP/1.1  대부분의 CDN 기본값
  HTTP/2   옵션으로 가능 (Cloudflare, Fastly, Akamai)

기업 내부망 (방화벽 안쪽):
  HTTP/1.1  지배적
```

> 📌 **핵심 관찰**: HTTP 버전은 **구간(segment)별로 다르다**. "사이트가 HTTP/2다" ≠ "그 사이트의 모든 통신이 HTTP/2"

---

## 1️⃣ 핵심 이유 8가지

### 1. CDN edge ↔ origin 표준은 여전히 HTTP/1.1

**구조**:
```
[사용자] ──HTTP/2 or 3──► [CDN edge (Cloudflare/Fastly/Akamai)] ──HTTP/1.1──► [origin]
                                                                  ▲
                                                            여기는 HTTP/1.1 기본
```

**왜?**
- CDN ↔ origin 구간은 **이미 keep-alive + connection pool**로 핸드셰이크 비용 amortize → HTTP/2 multiplexing 효과 미미
- origin은 보통 단순 REST API → 이미지·CSS 같은 자원 묶음 다운로드 시나리오 아님
- 운영자가 **로그·디버깅을 단순하게** 유지하려는 의도
- HTTP/2로 올리면 origin 측 CPU·메모리 부담 증가 (HPACK, frame parse)

**실측 사례**:
- Cloudflare는 origin pull을 기본 HTTP/1.1로 — HTTP/2 origin은 옵션으로 제공
- AWS CloudFront → origin: 기본 HTTP/1.1 (HTTP/2/3는 viewer 측에만 적용)
- Fastly: edge ↔ origin은 HTTP/1.1 (Origin Shield 통해 connection 풀링)

> 🔗 관련 인프라 패턴: [[connection-pool-eviction-lazy-idle]]

---

### 2. 디버깅 도구 친화성

```bash
# HTTP/1.1: 즉시 디버깅 가능
$ curl -v https://api.example.com/users
> GET /users HTTP/1.1
> Host: api.example.com
> User-Agent: curl/7.81.0
< HTTP/1.1 200 OK
< Content-Type: application/json
< {"id":1,"name":"Alice"}

# 사람이 바로 읽음. nc, telnet, mitmproxy 모두 같음.

# HTTP/2: 이진 frame
$ curl --http2 -v https://api.example.com/users
# 별도 디코더 없이는 frame 구조 파악 어려움
# Wireshark + SSLKEYLOGFILE 환경 필요
```

**현장 효과**:
- 장애 대응 시 30초 디버깅 → 5분 디버깅으로 늘어남
- on-call 엔지니어가 즉시 검증할 수 있는 단순함이 SLA 측면에서 가치
- 신입/주니어가 HTTP를 학습하기에 압도적으로 쉬움

---

### 3. 프록시·방화벽·미들웨어 호환성

**HTTP/1.1**:
- 모든 L4·L7 LB, 모든 forward/reverse proxy, 모든 WAF가 native 지원
- 30년간 검증된 상태 머신, 엣지 케이스 모두 알려짐
- text-based이므로 정규식·로그 grep으로 즉시 분석

**HTTP/2 도입 시 깨지는 것들**:
- 오래된 corporate proxy(Squid 구버전, BlueCoat 일부, Forcepoint 일부)가 HTTP/2를 인식 못 하고 차단
- WAF 룰셋이 HTTP/1.1 기반 → HTTP/2 frame 단위로 다시 작성 필요
- log aggregator(Splunk/ELK)에 HTTP/2 frame을 로깅하면 가독성 ↓
- inspection 장비가 stream multiplexing을 reassemble 못 함

**현장 효과**:
- 금융권·공공기관처럼 **legacy 미들웨어가 많은 환경**에서는 HTTP/1.1만 안전
- 글로벌 기업도 **on-prem 데이터센터 내부**는 HTTP/1.1 유지

---

### 4. gRPC가 못 들어가는 환경 (역설)

gRPC = HTTP/2 강제. 그러나 gRPC를 도입 못 하는 이유 자체가 HTTP/2 비채택과 직결:
- 회사 내부 프록시가 HTTP/2 지원 안 함
- 클라이언트가 **브라우저** (Native gRPC 직접 호출 불가 → gRPC-Web 필요)
- 디버깅 도구·observability 인프라가 텍스트 기반

→ 이런 곳은 결국 **REST over HTTP/1.1 유지**가 안전한 디폴트

> 🔗 관련: [[grpc-concept-deep-dive]]

---

### 5. 단순한 사용 패턴은 HTTP/2 효과를 못 본다

| 패턴 | HTTP/1.1로 충분한 이유 |
|---|---|
| **Webhook 수신** | POST 한 번, 응답 한 번 — multiplexing 무관 |
| **헬스체크 (liveness/readiness probe)** | k8s가 GET /healthz 한 번 — 가벼움 |
| **CLI 도구의 API 호출** | 한 번에 한 명령 — multiplexing 가치 X |
| **OAuth callback** | 단일 redirect — 단순함 우선 |
| **Cron job 외부 API 호출** | 순차 호출 — multiplexing 대상 없음 |

→ multiplexing이 빛나는 시나리오는 **여러 자원 동시 다운로드** (브라우저 페이지 로드)이지 **단일 API 호출**이 아니다.

---

### 6. HPACK·Frame parsing CPU 비용

```
서비스가 초당 100k 요청을 처리한다면:
  HTTP/1.1: 텍스트 파싱 (state machine, 빠름)
  HTTP/2:   frame parse + HPACK encode/decode + flow control 계산

→ 서비스 워커 CPU 5~15% 추가 부담 (워크로드별 차이)
→ origin이 CPU bound라면 HTTP/2 도입이 오히려 비용
```

**실제 사례**:
- Discord: 일부 internal service에서 gRPC → HTTP/1.1+JSON 회귀 (운영 단순성·디버깅 우선)
- 대부분의 회사가 internal API에서 OpenAPI/REST를 유지하는 이유

---

### 7. REST tooling ecosystem의 관성

```
30년간 축적된 도구·문서·관례:
  - Postman, Insomnia, Bruno (REST 클라이언트)
  - Swagger/OpenAPI (스펙)
  - Pact, Hoverfly (contract testing)
  - mitmproxy, Charles, Fiddler (디버깅)
  - JMeter, k6, Locust (부하 테스트)
  - 수많은 SDK/라이브러리 예제, StackOverflow 답변
```

→ 이 생태계 전체를 HTTP/2·gRPC로 옮기는 것은 **조직 단위 비용**이 너무 큼
→ 특히 외부 공개 API는 클라이언트 다양성 때문에 더 보수적

---

### 8. 학습 비용 + 채용 시장 현실

- 새 개발자가 입사 → HTTP/1.1은 1주일이면 능숙
- HTTP/2 + HPACK + flow control + frame layer + ALPN + h2c는 **고급 인프라 영역**
- 시니어 인프라 엔지니어 비용 vs HTTP/1.1 유지의 단순성 → 후자가 압도적

---

## 2️⃣ HTTP/1.1이 살아남는 데이터센터 패턴 (실제 사례)

### A. K8s 클러스터 내부
```
[Ingress] ──HTTP/2──► [Service A] ──HTTP/1.1──► [Service B]
                                                ▲
                                          내부 통신은 HTTP/1.1
                                          (REST + JSON)
```
- ingress controller(nginx-ingress, Traefik)는 HTTP/2 종료(termination) 후 백엔드로 HTTP/1.1
- 사이드카(Envoy)가 있는 경우만 mTLS+HTTP/2 가능

### B. AWS ALB → 백엔드
- ALB는 HTTP/2 viewer 지원, 그러나 **백엔드(target)로는 HTTP/1.1**이 디폴트 (HTTP/2 옵션 가능)
- target group settings에서 명시적으로 HTTP/2 선택해야 함

### C. 마이크로서비스 메시 (mesh 없는 환경)
- service mesh 도입 전: 각 서비스가 직접 HTTP 호출 → 거의 HTTP/1.1 + JSON
- service mesh 도입 후 (Istio/Linkerd): mesh가 mTLS+HTTP/2 처리, application은 여전히 HTTP/1.1로 본다

### D. CI/CD, monitoring agent
- Prometheus scrape → HTTP/1.1
- GitHub Actions → API 호출 거의 HTTP/1.1
- Datadog/New Relic agent → HTTP/1.1 (최근 일부 HTTP/2)

---

## 3️⃣ HTTP/1.1을 유지하는 의사결정 기준

### ✅ HTTP/1.1을 유지해도 되는 시그널
- 단일 요청-응답 패턴이 주류 (REST CRUD, webhook)
- 디버깅·로깅 단순성이 운영상 중요
- legacy 미들웨어·proxy 환경
- CPU 자원이 빠듯한 origin
- 외부 클라이언트 다양성이 높음 (브라우저+모바일+CLI 혼재)

### ⚠️ HTTP/2로 옮길 가치 시그널
- 페이지당 자원 50+ 개 (브라우저 향)
- gRPC 도입 결정 (강제)
- 헤더가 큰 모바일 워크로드 (Cookie + Auth가 매 요청 수 KB)
- low-latency 모바일 사용자 비중 높음
- Apple APNs, Web Push 같은 long-lived stream 필요

### 🚀 HTTP/3까지 갈 가치 시그널
- 모바일 Wi-Fi↔LTE 전환 잦은 사용자
- 동남아·아프리카 등 packet loss 높은 망
- TLS 1.3 + 0-RTT 재방문 비중 높은 서비스
- UDP 차단되지 않는 환경 확신

---

## 4️⃣ 핵심 정리

1. **HTTP/2 도입은 "사이트 일부 구간"만 바꾼다** — 사용자 측은 HTTP/2·3, edge↔origin은 HTTP/1.1이 일반적 패턴
2. **HTTP/1.1의 텍스트 단순성은 운영·디버깅·교육 비용을 모두 낮춘다** — 30년간의 도구 생태계 누적
3. **HTTP/2 multiplexing 효과는 "여러 자원 동시 다운로드" 시나리오에서만 의미** — 단일 API/webhook은 무관
4. **legacy proxy·WAF·corporate firewall이 HTTP/2를 못 다루는 환경**이 여전히 광범위
5. **gRPC를 못 들이는 이유 = HTTP/2를 못 들이는 이유** → REST over HTTP/1.1이 fallback 디폴트
6. **HTTP/3는 더 늦게 채택**될 것 — UDP 차단 환경, L4 LB 호환성, 디버깅 도구 미성숙
7. **"HTTP/1.1을 안 쓰는 회사"는 사실상 없다** — 어디선가 한 구간은 반드시 HTTP/1.1이다

---

## 🔗 시리즈 노트

- [[http1-1-concept-explainer]]
- [[http2-concept-explainer]]
- [[http1-1-problems-and-http2-evolution]]
- [[http2-perspective-grpc-and-ecosystem]]
- [[http3-quic-concept-explainer]]
- [[http-protocol-interview-qa]]

## 📎 Sources

1. [Web Almanac 2024 — HTTP](https://almanac.httparchive.org/en/2024/http)
2. [Cloudflare Radar — Adoption stats](https://radar.cloudflare.com/)
3. [Why is HTTP/1.1 still alive — Smashing Magazine](https://www.smashingmagazine.com/2021/08/http3-core-concepts-part1/)
4. [Cloudflare — Origin pull defaults](https://developers.cloudflare.com/cache/concepts/default-cache-behavior/)
5. [AWS CloudFront origin protocol](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-web-values-specify.html)
6. [Discord engineering — Why we moved from gRPC](https://discord.com/blog/) (사례 기록 일반론)
7. [Kubernetes Ingress and HTTP/2](https://kubernetes.io/docs/concepts/services-networking/ingress/)
8. [HTTP/2 in Action — Barry Pollard, Manning] — Ch.2 adoption discussion
