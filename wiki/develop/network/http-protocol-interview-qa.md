---
tags: [http, http1-1, http2, http3, interview, qa, backend]
created: 2026-04-28
---

# 🎤 HTTP/1.1·2·3 면접 대비 Q&A 30+

> 💡 **사용법**: 각 질문은 **답변 + follow-up + backlink** 구조다. 면접관은 첫 답변 후 반드시 꼬리질문을 던진다 — 단답으로 끝내지 말고 follow-up까지 준비해라.

---

## 🟦 카테고리 A — 기본 개념 (8문항)

### Q1. HTTP/1.1과 HTTP/2의 가장 결정적인 차이를 한 문장으로?
**답**: HTTP/1.1은 텍스트 기반에 한 connection으로 한 요청만 처리하는 직렬 모델이고, HTTP/2는 이진 frame 기반에 한 connection 위에 여러 stream을 동시 처리하는 multiplexing 모델이다.

**Follow-up 1**: 그럼 HTTP 의미론(GET, 200, Content-Type)도 다른가?
→ **아니다**. RFC 9110(HTTP Semantics)이 1.1·2·3 공통이고, 버전별 RFC(9112/9113/9114)는 wire format만 정의한다.

**Follow-up 2**: multiplexing이 있는데 왜 HTTP/2도 한계가 있나?
→ **TCP HoL**. 패킷 1개 손실되면 OS가 다른 stream 패킷도 application에 안 넘긴다. HTTP/3가 QUIC(UDP)로 해결.

🔗 [[http1-1-concept-explainer]], [[http2-concept-explainer]]

---

### Q2. HTTP/1.1의 persistent connection(keep-alive)은 왜 도입되었나?
**답**: HTTP/1.0은 매 요청마다 TCP 새로 열어서 핸드셰이크 비용이 누적됐다. 페이지 하나에 자원 50개면 핸드셰이크만 50번 → latency 폭발. HTTP/1.1은 응답 후에도 connection을 유지해 다음 요청이 같은 TCP를 재사용하도록 했다.

**Follow-up 1**: keep-alive로 모든 문제가 해결됐나?
→ 아니다. 응답 순서를 강제하는 한계 때문에 pipelining 시 HoL blocking이 생기고, 호스트당 6 connection 한계로 자원 많은 페이지는 직렬화된다.

**Follow-up 2**: keep-alive timeout은 보통 어떻게 설정하나?
→ nginx 기본 75초, AWS ELB는 60초. 너무 길면 메모리 압박, 짧으면 효과 없음. 프록시 chain에서 client < server timeout이어야 race condition 회피.

🔗 [[http1-1-concept-explainer]]

---

### Q3. HTTP/1.1의 chunked transfer encoding이 무엇이고 언제 쓰나?
**답**: 응답 본문 전체 크기를 미리 모를 때 청크 단위로 스트리밍하는 방식. `Transfer-Encoding: chunked`로 선언하고, 각 청크는 `<크기 hex>\r\n<데이터>\r\n`, 마지막은 `0\r\n\r\n`.

**Follow-up 1**: HTTP/2에서도 chunked encoding을 쓰나?
→ **아니다**. HTTP/2는 frame 단위 전송이라 chunked가 redundant — 명세상 사용 금지.

**Follow-up 2**: chunked + Content-Length 동시 사용 위험은?
→ **HTTP request smuggling**. front-end proxy와 back-end가 우선순위를 다르게 해석하면 요청 경계 혼동 → 캐시 오염, 인증 우회.

🔗 [[http1-1-concept-explainer]]

---

### Q4. HTTP/2의 stream과 frame은 무엇인가?
**답**: Frame은 HTTP/2의 최소 전송 단위(Length+Type+Flags+StreamID+Payload). Stream은 한 connection 안의 가상 양방향 통로로, 한 RPC 또는 한 요청-응답이 한 stream에 매핑된다. 한 connection에 stream 수백 개가 동시 진행 가능.

**Follow-up 1**: Stream ID는 어떻게 할당되나?
→ Client-initiated는 홀수(1, 3, 5, …), server-initiated(server push, deprecated)는 짝수. 한 connection 안에서 monotonically increasing.

**Follow-up 2**: Frame type에는 어떤 게 있나?
→ DATA, HEADERS, RST_STREAM, SETTINGS, PUSH_PROMISE(deprecated), PING, GOAWAY, WINDOW_UPDATE, CONTINUATION (RFC 9113 9개).

🔗 [[http2-concept-explainer]]

---

### Q5. HPACK이 무엇이고 왜 도입되었나?
**답**: HTTP/2의 헤더 압축 알고리즘 (RFC 7541). HTTP/1.1은 같은 헤더(Cookie, User-Agent 등)를 매 요청 풀텍스트로 보내 대역폭 낭비가 컸다. HPACK은 static table(61개 표준 헤더) + dynamic table(connection별 학습) + Huffman 코딩으로 90%까지 압축 가능.

**Follow-up 1**: 왜 그냥 gzip/brotli를 안 썼나?
→ **CRIME 공격(2012)**. TLS 압축이 사이드채널 누출로 secret을 추출 가능했다. HTTP 헤더 압축도 같은 위험. HPACK은 sensitive 헤더에 `never_indexed` 플래그를 두어 dynamic table 제외, mitigation을 명시.

**Follow-up 2**: HPACK도 100% 안전한가?
→ 아니다. dynamic table에 추가될 때의 크기 차이로 secret 추론하는 BREACH-류 공격 변형이 가능. CSRF token rotation, secret 헤더 never_indexed 등 application 레벨 mitigation 필요.

🔗 [[http2-concept-explainer]], [[http1-1-problems-and-http2-evolution]]

---

### Q6. QUIC이 무엇이고 HTTP/3와의 관계는?
**답**: QUIC은 UDP 위에 TLS 1.3 + multi-stream + reliability를 통합한 transport 프로토콜(RFC 9000). HTTP/3는 그 위에서 동작하는 application protocol(RFC 9114). 즉 HTTP/3 = HTTP semantics + binary frame + QUIC.

**Follow-up 1**: 왜 TCP 대신 UDP인가? 신뢰성은?
→ TCP는 OS 커널이라 진화 속도 느리고, 순서 보장 때문에 stream HoL이 강제된다. QUIC은 UDP 위에 application 공간에서 reliability를 직접 구현 → 진화 빠름, stream별 독립 reliability.

**Follow-up 2**: HTTP/3가 즉시 HTTP/2를 대체하는가?
→ 아니다. UDP 차단 환경, L4 LB 호환성, CPU 비용으로 공존. 모바일·CDN edge가 우선 채택.

🔗 [[http3-quic-concept-explainer]]

---

### Q7. ETag와 If-None-Match의 역할은?
**답**: 서버가 응답에 ETag(리소스 버전 식별자)를 보내면 클라이언트가 다음 요청 시 If-None-Match로 같은 ETag를 보낸다. 변경 없으면 서버가 본문 없이 304 Not Modified — 대역폭과 latency 절감. Cache-Control max-age 만료 후 재검증 메커니즘.

**Follow-up 1**: ETag와 Last-Modified의 차이는?
→ Last-Modified는 초 단위라 1초 안에 두 번 변경 시 구분 못 함. ETag는 hash나 version 번호 — 더 정확. RFC 9110에 따르면 둘 다 보낼 수 있고 클라이언트는 ETag 우선.

**Follow-up 2**: Strong vs Weak ETag?
→ Strong ETag(`"abc"`)는 byte-byte 일치, Weak ETag(`W/"abc"`)는 의미적 동등성. Weak는 gzip 변환 등에 유용.

🔗 [[http1-1-concept-explainer]]

---

### Q8. ALPN(Application-Layer Protocol Negotiation)이란?
**답**: TLS 핸드셰이크 중 application protocol을 협상하는 확장(RFC 7301). 클라이언트가 ClientHello에 지원 protocol 목록(`h2`, `http/1.1`, `h3`)을 보내고 서버가 선택. 한 번의 RTT 안에 protocol 결정.

**Follow-up 1**: HTTP/2 cleartext(h2c)는 어떻게 협상하나?
→ HTTP Upgrade 헤더(101 Switching Protocols) 또는 prior knowledge. 그러나 모든 주요 브라우저는 h2c 미지원 → TLS 필수.

**Follow-up 2**: HTTP/3 협상은?
→ ALPN `h3` + Alt-Svc 헤더 + DNS HTTPS RR(RFC 9460). 첫 방문은 HTTP/2로, Alt-Svc 받은 뒤 다음부터 HTTP/3 시도.

🔗 [[http2-concept-explainer]], [[http3-quic-concept-explainer]]

---

## 🟨 카테고리 B — 함정·심화 질문 (8문항)

### Q9. (함정) HTTP/2에서 Head-of-Line blocking이 정말 사라졌나?
**답**: **부분적으로만 사라졌다**. Application layer HoL은 stream multiplexing으로 해결됐지만, **TCP layer HoL은 여전**하다. 패킷 1개 손실되면 TCP는 순서 보장이라 OS가 다른 stream 패킷도 application에 안 넘긴다.

**Follow-up 1**: 그럼 어떻게 해결하나?
→ HTTP/3가 QUIC(UDP) 위에 stream을 application 공간에서 직접 관리해 stream별 독립 reliability를 제공.

**Follow-up 2**: 패킷 손실이 적은 환경에서는 HTTP/2와 HTTP/3 차이가 별로 없나?
→ 그렇다. 데이터센터 내부처럼 손실률 ~0%면 HTTP/2도 충분. 모바일·glonal CDN처럼 손실률이 있는 환경에서 HTTP/3 효과가 큼.

🔗 [[http1-1-problems-and-http2-evolution]], [[http3-quic-concept-explainer]]

---

### Q10. (함정) HTTP/2에서 도메인 샤딩(domain sharding)을 쓰면 어떻게 되나?
**답**: **안티패턴**이다. HTTP/1.1은 호스트당 6 connection 한계가 있어 도메인을 cdn1, cdn2, …으로 나누면 동시 다운로드 늘릴 수 있었지만, HTTP/2는 단일 connection으로 수백 stream을 동시 처리한다. 도메인 샤딩하면 (1) DNS 조회 N배 (2) TLS 핸드셰이크 N배 (3) HPACK dynamic table 분산으로 압축률↓ (4) connection coalescing 못 받음.

**Follow-up 1**: 그럼 HTTP/2 환경에서는 무조건 한 도메인이 좋나?
→ 거의 그렇다. 단, 같은 IP+같은 인증서면 connection coalescing이 자동 적용되어 다른 host도 connection 공유.

**Follow-up 2**: 이미 HTTP/1.1 시절 샤딩한 사이트는 HTTP/2 마이그레이션 시 어떻게?
→ subdomain 통합 → `<link rel="preconnect">` 정리 → CDN 설정에서 단일 origin으로.

🔗 [[http1-1-problems-and-http2-evolution]]

---

### Q11. (함정) HTTP/2 server push가 deprecated된 이유는?
**답**: 캐시-인식 push가 어려웠다. 서버가 클라이언트 캐시 상태를 모르기 때문에 이미 캐시된 자원도 푸시 → 대역폭 낭비. 또 push가 다른 critical 자원과 stream 자원을 경쟁 → 오히려 느려지는 케이스도. 결국 Chrome이 2022년 server push 지원 제거(M106), RFC 9113이 deprecated 선언.

**Follow-up 1**: 후계자는?
→ **103 Early Hints** (RFC 8297). 서버가 응답 본문 만드는 동안 "이 자원 미리 preload해" 힌트만 보냄. 실제 자원 전송은 클라이언트가 결정.

**Follow-up 2**: 103을 지원하는 곳은?
→ Cloudflare, Fastly가 2023년부터 광범위 지원. Chrome 103+, Firefox 91+. web.dev에서 LCP 30%↓ 사례 보고.

🔗 [[http1-1-problems-and-http2-evolution]], [[http2-concept-explainer]]

---

### Q12. (함정) HPACK이 보안에 미치는 영향은?
**답**: HPACK 자체가 사이드채널이 될 수 있다. dynamic table에 헤더가 추가될 때의 응답 크기 차이로 secret(예: CSRF token)을 추론하는 공격이 이론적으로 가능 — BREACH-류 변형. 그래서 RFC 7541은 sensitive 헤더에 `never_indexed` 플래그를 명시해 dynamic table 제외하도록 권고.

**Follow-up 1**: 실제 mitigation 책임은 누구인가?
→ 라이브러리/프레임워크가 sensitive 헤더(Authorization, Cookie 일부)를 자동으로 never_indexed 처리. 추가로 application 단에서 CSRF token rotation, length padding.

**Follow-up 2**: HTTP/3의 QPACK은 같은 위험인가?
→ 비슷하지만 QPACK은 encoder/decoder stream을 분리해 추가 복잡성이 생겼다. 동일한 mitigation 원칙 적용.

🔗 [[http2-concept-explainer]], [[http3-quic-concept-explainer]]

---

### Q13. (함정) HTTP/3는 UDP를 쓴다는데, 그럼 신뢰성은 어떻게 보장하나?
**답**: QUIC이 UDP 위에 application layer에서 신뢰성을 구현한다. sequence + offset, ACK frame, retransmission, congestion control(RFC 9002 — TCP CUBIC/BBR 알고리즘 차용 가능). 즉 UDP는 단지 "OS가 손대지 않는 비신뢰 데이터그램 채널"로만 쓰고, 신뢰성·순서·혼잡 제어는 모두 QUIC이 한다.

**Follow-up 1**: TCP 대신 UDP를 고른 진짜 이유는?
→ TCP는 OS 커널이라 진화 속도 느림 + middlebox(NAT, firewall, load balancer)가 TCP를 깊이 파싱해 ossification(굳어짐) 발생 → 새 기능 추가 불가능. UDP는 단순한 데이터그램이라 application이 자유로움.

**Follow-up 2**: 모든 환경에서 HTTP/3가 빠른가?
→ 아니다. UDP 차단된 기업망이나 ISP에서는 fallback. 데이터센터처럼 손실률 ~0% 환경에서는 HTTP/2와 차이 미미.

🔗 [[http3-quic-concept-explainer]]

---

### Q14. (함정) QPACK이 HPACK과 다른 이유는?
**답**: HPACK은 dynamic table 업데이트가 stream 사이에 **순서대로** 도착해야 동작한다. HTTP/2는 TCP라서 자연히 순서 보장. 그러나 HTTP/3는 QUIC stream이 비순차 도착 가능 — HPACK 그대로 쓰면 dynamic table HoL 재발생. QPACK은 encoder stream/decoder stream을 별도 unidirectional stream으로 분리해 비순차 도착에도 동작.

**Follow-up 1**: QPACK이 HPACK보다 압축률이 떨어지나?
→ 약간 떨어진다. dynamic table 참조 시 ack 받기 전까지 사용 못 하는 안전성 측면 때문에. 그러나 실측 차이 미미.

**Follow-up 2**: 둘 다 구현해야 하나?
→ HTTP/2 서버는 HPACK, HTTP/3는 QPACK. 둘 지원하면 둘 다 필요. quiche 등 라이브러리가 처리.

🔗 [[http3-quic-concept-explainer]]

---

### Q15. (함정) HTTP/2 Rapid Reset DoS(CVE-2023-44487)란?
**답**: 2023년 10월 발견된 HTTP/2 DoS 취약점. 공격자가 stream을 열자마자 RST_STREAM으로 즉시 취소를 무한 반복 — 서버는 stream 생성/취소 비용이 비대칭이라 자원 고갈. nginx, Envoy, Go, .NET 등 모든 주요 구현체에 영향. 2024년 초까지 패치 배포.

**Follow-up 1**: 어떻게 방어하나?
→ (1) RST_STREAM 비율 제한 (2) MAX_CONCURRENT_STREAMS 보수적 설정 (3) 패치 적용 — Cloudflare, Google이 자체 mitigation 발표.

**Follow-up 2**: HTTP/3에도 같은 취약점이 있나?
→ 변형이 가능하다. QUIC도 stream cancel 가능 — 마찬가지로 비율 제한과 자원 회계 필요.

🔗 [[http2-concept-explainer]]

---

### Q16. (함정) HTTP request smuggling이란?
**답**: front-end proxy와 back-end 서버가 요청 경계를 다르게 해석할 때 발생. 가장 흔한 패턴은 `Content-Length`와 `Transfer-Encoding`을 둘 다 보낼 때. 한쪽은 CL, 다른 쪽은 TE로 해석하면 추가 요청을 두 번째 사용자의 응답에 섞어 넣을 수 있다(CL.TE / TE.CL).

**Follow-up 1**: 어떻게 방어하나?
→ (1) front-end가 두 헤더 동시 존재 시 거부 (2) HTTP/1.1 → HTTP/2 다운그레이드 경계에서 strict 검증 (3) RFC 9112의 명확한 규칙 준수.

**Follow-up 2**: HTTP/2도 smuggling 위험이 있나?
→ HTTP/2 → HTTP/1.1 다운그레이드 경계에서 발생 가능. 2022년 Cloudflare 사고가 대표적 — front-end HTTP/2 → back-end HTTP/1.1 변환 시 헤더 정규화가 깨지는 변형.

🔗 [[http1-1-concept-explainer]]

---

## 🟩 카테고리 C — 성능·운영 (7문항)

### Q17. HTTP/1.1 keep-alive timeout과 connection pool 크기는 어떻게 결정하나?
**답**: keep-alive timeout은 클라이언트가 다음 요청 보낼 가능성·서버 메모리 압박 trade-off. 일반적 기본값: nginx 75초, AWS ELB 60초. Pool 크기는 (1) per-host 동시 RPS × 평균 응답시간 + 여유 (2) 메모리 한계. python `urllib3` `pool_maxsize=10`, Go `http.Transport.MaxIdleConnsPerHost=2` 기본값을 워크로드별 튜닝.

**Follow-up 1**: client timeout > server timeout이면 무슨 일이?
→ Race condition. 서버가 close 보낸 직후 client가 같은 connection에 새 요청 → 응답 없음, retry 필요. **client timeout < server timeout** 이 안전.

**Follow-up 2**: connection pool eviction 정책은?
→ idle timeout 기반 lazy eviction (요청 시점에 검사). 자세히는 [[connection-pool-eviction-lazy-idle]].

🔗 [[python-requests-connection-pool-keepalive]]

---

### Q18. HTTP/2 MAX_CONCURRENT_STREAMS는 얼마로 설정하나?
**답**: 일반적으로 100~250. 너무 작으면 multiplexing 효과↓, 너무 크면 (1) 서버 메모리 압박 (2) Rapid Reset류 DoS 노출. nginx 기본 128, Envoy 2147483647(상한 없음, 별도 제한 필요), Go net/http2 250.

**Follow-up 1**: stream 하나당 메모리 비용은?
→ HEADER buffer(~8KB), HPACK 상태(~수KB), flow control window 상태, 그리고 application 측 처리 메모리. 250 streams × 64KB = 16MB per connection (대략).

**Follow-up 2**: gRPC에서 권장값은?
→ gRPC docs는 100~1000. 단 production에서는 측정 후 결정.

🔗 [[http2-concept-explainer]]

---

### Q19. HTTP/2를 도입했는데 페이지가 더 느려졌다. 의심할 원인은?
**답**: (1) 도메인 샤딩이 그대로 남아 있어 단일 connection 효과 못 봄 (2) 과도한 server push로 캐시 자원도 재전송 (3) L4 LB로 connection 단위 분배 → 부하 불균형 (4) HPACK CPU 비용이 작은 origin에서 부담 (5) TCP HoL이 모바일 환경에서 더 두드러짐 (6) priority 처리 미흡한 구현체.

**Follow-up 1**: 도메인 샤딩이 남았는지 어떻게 확인?
→ Chrome DevTools Network 탭에서 connection ID 확인. 같은 페이지에서 connection ID가 4개 이상이면 샤딩 의심.

**Follow-up 2**: 부하 불균형은 어떻게 모니터링?
→ LB의 active_connections, request_count 메트릭을 backend별로 비교. 한 backend에 connection 몰리면 L7 LB로 전환.

🔗 [[http2-concept-explainer]], [[http1-1-problems-and-http2-evolution]]

---

### Q20. HTTP/2와 gRPC를 디버깅할 때 어떤 도구를 쓰나?
**답**: (1) **nghttp2** CLI — `nghttp -v` (2) curl `--http2 -v` (3) Wireshark + `SSLKEYLOGFILE`로 TLS 평문화 후 HTTP/2 dissector (4) **grpcurl** — gRPC용 curl (5) chrome://net-export/ — Chrome 내부 HTTP/2 frame log (6) Envoy admin endpoint `/stats`로 stream metrics.

**Follow-up 1**: HTTP/3는?
→ Wireshark + SSLKEYLOGFILE + QUIC dissector. **qlog/qvis**로 표준 QUIC 로그 시각화. curl `--http3` (빌드 시 quiche/ngtcp2 필요).

**Follow-up 2**: 프로덕션 운영에서는?
→ Envoy admin stats, OpenTelemetry tracing(span name에 stream ID 포함), Prometheus h2 stream 메트릭.

🔗 [[http2-concept-explainer]], [[http3-quic-concept-explainer]]

---

### Q21. (함정) Connection migration이 모바일에서 왜 결정적인가?
**답**: 모바일 사용자는 Wi-Fi → LTE → Wi-Fi를 빈번히 전환한다. TCP는 4-tuple(srcIP, srcPort, dstIP, dstPort)로 connection 식별 → IP 변경 시 끊김 → application은 reconnect + TLS 재핸드셰이크 + state 복원 필요. QUIC은 Connection ID(8~20byte 랜덤 ID)로 식별 → IP 변경에도 ID 그대로 → 같은 connection 유지.

**Follow-up 1**: 영상 스트리밍에 어떤 차이?
→ TCP: Wi-Fi 끊기면 영상 정지 → reconnect → 버퍼 재구성 → 1~5초 끊김. QUIC: path validation 후 즉시 재개 → 수 ms 내 회복.

**Follow-up 2**: 보안 우려는?
→ Connection ID가 영구적이면 device tracking 가능. QUIC은 NEW_CONNECTION_ID frame으로 주기적 rotation 권고.

🔗 [[http3-quic-concept-explainer]]

---

### Q22. CDN 환경에서 HTTP 버전이 어떻게 설정되어 있나?
**답**: 일반적 패턴은 **viewer ↔ edge는 HTTP/2/3, edge ↔ origin은 HTTP/1.1**. 사용자는 multiplexing·HPACK 혜택, origin은 단순한 HTTP/1.1로 디버깅·운영 용이. 단 gRPC origin이면 edge ↔ origin도 HTTP/2 강제.

**Follow-up 1**: 왜 origin도 HTTP/2로 하지 않나?
→ (1) edge ↔ origin은 이미 connection pool로 핸드셰이크 amortize → multiplexing 가치 미미 (2) origin CPU 부담 증가 (3) 디버깅 단순성.

**Follow-up 2**: HTTP/3까지 가는 CDN은?
→ Cloudflare, Fastly, Akamai가 viewer 측에서 HTTP/3 광범위 지원. 그러나 edge ↔ origin은 여전히 HTTP/1.1 또는 HTTP/2.

🔗 [[why-http1-1-still-dominates]]

---

### Q23. L4 LB와 L7 LB 중 HTTP/2 환경에서 무엇을 써야 하나?
**답**: **L7 LB**. L4 LB는 connection 단위 분배인데 HTTP/2는 long-lived connection이라 connection 하나에 stream 수백 → 한 backend에 부하 몰림. L7 LB는 stream/request 단위 인지로 균등 분배 가능.

**Follow-up 1**: 그럼 L4 LB는 못 쓰나?
→ TLS termination 없이 raw connection forwarding이면 가능. 보통 L4(외부) + L7(내부) 조합.

**Follow-up 2**: AWS에서는 어떻게?
→ ALB(L7)가 HTTP/2 native, NLB(L4)는 raw forwarding. gRPC면 ALB target group을 HTTP/2/gRPC로 설정.

🔗 [[http2-concept-explainer]], [[why-http1-1-still-dominates]]

---

## 🟪 카테고리 D — 시스템 디자인·실무 (5문항)

### Q24. 새 service mesh 도입 시 service ↔ service 통신을 HTTP/1.1과 HTTP/2 중 무엇으로 할까?
**답**: gRPC 사용하면 HTTP/2 강제. REST + JSON이라면 HTTP/1.1이 디폴트로 무난. 결정 기준: (1) 요청 패턴이 single request-response면 HTTP/1.1로 충분 (2) streaming/long-lived면 HTTP/2 (3) sidecar(Envoy/Linkerd) 도입 시 mesh가 자동으로 HTTP/2 + mTLS 처리하므로 application은 HTTP/1.1로 봐도 됨.

**Follow-up 1**: HTTP/2 메시 + REST application 조합의 의미는?
→ Envoy가 application의 HTTP/1.1 트래픽을 받아 HTTP/2로 변환해 다른 sidecar로 전송. application은 단순함 유지하면서 인프라 효율 확보.

**Follow-up 2**: 디버깅은 어디서?
→ Envoy admin endpoint, Istio kiali 대시보드, OpenTelemetry trace.

🔗 [[http2-perspective-grpc-and-ecosystem]]

---

### Q25. 글로벌 모바일 사용자 대상 서비스에서 HTTP/3로 갈 가치가 있을까?
**답**: 케이스에 따라 다르다. 가치 시그널: (1) 모바일 비중 60%↑ (2) 모바일 네트워크 전환 잦은 사용자 다수 (3) 패킷 손실 환경(동남아·인도) 트래픽 비중 높음 (4) latency-sensitive (라이브 스트리밍, 게임). 비용 시그널: (1) 자체 LB 인프라 → HTTP/3 native LB 필요 (2) 디버깅·observability 도구 재정비 (3) CPU 비용 증가 (4) UDP 차단 환경 사용자 fallback 검증.

**Follow-up 1**: 검증은 어떻게?
→ Cloudflare/Fastly로 일부 트래픽만 HTTP/3 활성화 → A/B 테스트로 LCP/TTFB 비교.

**Follow-up 2**: 현실적 첫 단계는?
→ CDN 측에서 HTTP/3 활성화(Alt-Svc 헤더). Origin은 그대로 HTTP/1.1/2 유지.

🔗 [[http3-quic-concept-explainer]]

---

### Q26. Webhook 수신 endpoint를 만든다. 어떤 HTTP 버전이 필요한가?
**답**: **HTTP/1.1로 충분**. Webhook은 단일 POST + 단일 응답 패턴 — multiplexing·streaming 가치 없음. 외부 시스템(GitHub, Stripe, Slack)이 HTTP/1.1로 보내는 경우가 많고, HTTP/1.1 endpoint가 디버깅(curl, log)도 단순.

**Follow-up 1**: HTTPS는 필요한가?
→ 필수. 페이로드에 sensitive data, signature가 들어감.

**Follow-up 2**: 큰 webhook 페이로드는?
→ chunked encoding 또는 streaming JSON parser. 그러나 대부분 webhook은 1MB 미만이라 일반 처리로 충분.

🔗 [[why-http1-1-still-dominates]]

---

### Q27. 백엔드 서비스 간 streaming이 필요한 새 기능. 어떻게 설계?
**답**: 먼저 streaming 패턴을 분류: (1) server → client one-way (예: 진행 상황 알림) → SSE 또는 gRPC server streaming (2) bidirectional → gRPC bidirectional streaming 또는 WebSocket. 현대 백엔드 ↔ 백엔드면 gRPC가 강타입 + HTTP/2 + flow control + bidirectional 모두 제공.

**Follow-up 1**: SSE vs gRPC server streaming 차이는?
→ SSE는 HTTP/1.1 기반 텍스트 스트림(text/event-stream), 브라우저 native. gRPC는 HTTP/2 frame 기반 protobuf, 강타입.

**Follow-up 2**: WebSocket 대신 gRPC를 고르는 이유는?
→ 강타입 스키마, flow control 빌트인, HTTP 인프라 친화. 단 브라우저는 native gRPC 못 받으므로 gRPC-Web/Connect 필요.

🔗 [[http2-perspective-grpc-and-ecosystem]], [[long-polling-http-realtime-communication]]

---

### Q28. (함정) 같은 origin의 큰 자원이 작은 자원의 다운로드를 막고 있다. 원인은?
**답**: 가능한 원인: (1) HTTP/1.1이고 6 connection 한계로 직렬화 (2) HTTP/2에서 priority 처리가 잘못됨 — 큰 자원이 stream 자원을 점유 (3) flow control window가 큰 자원에 몰림 (4) 도메인 샤딩 잔재로 같은 origin이지만 connection 분리 (5) TCP HoL — 큰 자원 패킷 손실 시 모든 stream 정체.

**Follow-up 1**: HTTP/2 priority가 잘 작동하는지 확인하는 법?
→ Chrome DevTools에서 priority 값 확인, Envoy stream stats. 다만 priority RFC 7540 방식은 deprecated → RFC 9218 Extensible Priorities로 이주 중.

**Follow-up 2**: HTTP/3가 이 문제를 더 잘 푸는가?
→ TCP HoL은 해결되지만 priority/flow control 로직 자체는 비슷한 함정 가능. 측정 + tuning 필요.

🔗 [[http2-concept-explainer]], [[http1-1-problems-and-http2-evolution]]

---

## 🟧 카테고리 E — HTTP/3·QUIC 심화 (5문항)

### Q29. 0-RTT는 정확히 어떻게 동작하고, 왜 위험한가?
**답**: 재방문 시 client가 cached secret(TLS 1.3 PSK)으로 ClientHello + 첫 application data를 한 번에 보냄. server는 1-RTT 핸드셰이크 완료 전에 application data를 처리. 위험: replay attack — 공격자가 가로챈 0-RTT data를 재전송하면 server가 중복 처리. 그래서 idempotent 요청(GET/HEAD/OPTIONS)만 0-RTT 허용.

**Follow-up 1**: server 측 mitigation은?
→ (1) anti-replay token bucket — 같은 PSK ID로 들어온 0-RTT 응답을 추적 (2) single-use ticket — TLS session ticket을 한 번만 사용 가능하게 (3) application 단에서 idempotency key.

**Follow-up 2**: 모든 GET이 진짜 안전한가?
→ 아니다. side effect 있는 GET (예: `/logout`, `/click?token=...`)이면 replay로 동일 효과 → application 책임으로 idempotent 보장.

🔗 [[http3-quic-concept-explainer]]

---

### Q30. QUIC은 사용자 공간(user-space)에서 동작한다. 이게 왜 중요한가?
**답**: TCP는 OS 커널의 일부 → 새 기능 추가하려면 모든 OS 업데이트 필요 → 진화 속도 매우 느림 + middlebox(NAT, firewall)가 TCP를 깊이 검사해 ossification(굳어짐). QUIC은 application 공간이라 라이브러리 업데이트만으로 진화 가능. Cloudflare/Google이 production에서 검증된 변경을 빠르게 적용.

**Follow-up 1**: 단점은?
→ CPU 비용 — 커널의 효율적 TCP 처리 대비 사용자 공간이 1.5~2배 부담. GSO(Generic Segmentation Offload)·GRO·kTLS로 완화.

**Follow-up 2**: 이게 보안에 미치는 영향?
→ 메타데이터 암호화로 middlebox 침투 차단 — 운영자가 SNI sniffing, deep packet inspection 못 함. 기업 inspection 도구는 별도 정책 필요.

🔗 [[http3-quic-concept-explainer]]

---

### Q31. UDP 차단 환경에서 HTTP/3 클라이언트는 어떻게 동작하나?
**답**: 첫 시도: UDP 443으로 QUIC 핸드셰이크 → 차단 시 timeout(보통 수 백 ms~몇 초) → fallback to HTTP/2 over TCP 443. 브라우저는 fail 경험을 캐시해 다음 방문에서 즉시 HTTP/2로 시도(Alt-Svc TTL).

**Follow-up 1**: timeout 동안 사용자가 보는 latency는?
→ 추가 1~3초. 이게 HTTP/3 활성화 전 반드시 검증해야 하는 이유.

**Follow-up 2**: 항상 HTTP/3 시도가 좋은 게 아닌가?
→ 일반 가정망·모바일은 가치 큼, 기업망은 fail 비율 높음. CDN의 비율 기반 활성화 + RUM(Real User Monitoring)으로 결정.

🔗 [[http3-quic-concept-explainer]]

---

### Q32. Multipath QUIC과 MASQUE가 무엇인가?
**답**: **Multipath QUIC**(draft 진행 중): 한 connection을 Wi-Fi + LTE 같은 여러 path로 동시 사용해 throughput 향상·redundancy 확보. **MASQUE**(RFC 9298 등): VPN/proxy를 QUIC 위에서 통일하는 프레임워크. Apple Private Relay가 MASQUE 기반.

**Follow-up 1**: Multipath TCP(MPTCP)와 다른가?
→ MPTCP는 커널 변경 필요해 광범위 채택 어려움. Multipath QUIC은 사용자 공간이라 application 단 채택 가능 → 모바일 OS에 자연 통합.

**Follow-up 2**: MASQUE를 쓰는 서비스는?
→ Apple Private Relay(iOS/macOS), Cloudflare WARP. 향후 enterprise SASE 솔루션이 MASQUE 위로 이주할 가능성.

🔗 [[http3-quic-concept-explainer]]

---

### Q33. (함정) HTTP/2는 stream priority 기능이 deprecated되었다. 그럼 priority는 어떻게?
**답**: RFC 9113이 PRIORITY frame을 deprecated 표시 → **RFC 9218 Extensible Priorities for HTTP**가 후계. `priority` 응답 헤더와 `urgency`, `incremental` 파라미터로 표현. HTTP/2와 HTTP/3 공통.

**Follow-up 1**: 왜 RFC 7540 priority가 폐기됐나?
→ stream dependency tree가 너무 복잡해 구현체마다 동작 다름 → 의도한 효과 안 남. 단순한 헤더 기반으로 회귀.

**Follow-up 2**: 브라우저가 RFC 9218을 쓰나?
→ Chrome, Firefox가 점진 도입 중(2023년부터). 서버 측은 nginx, Envoy가 지원 시작.

🔗 [[http2-concept-explainer]]

---

## 🔥 카테고리 F — 빈출 1줄 답변 (보너스)

| Q | A |
|---|---|
| HTTP/1.1 첫 요청 latency는? | DNS + TCP(1RTT) + TLS(1~2RTT) + HTTP RTT |
| HTTP/2 connection preface? | `PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n` (24 bytes 매직) |
| HTTP/2 server-side stream ID? | 짝수 (deprecated) |
| HPACK static table 크기? | 61 entries |
| HPACK dynamic table 기본 크기? | 4096 bytes |
| HTTP/3의 핵심 문서 RFC? | RFC 9114 |
| QUIC의 핵심 문서 RFC? | RFC 9000 |
| QPACK의 핵심 문서 RFC? | RFC 9204 |
| HTTP/3 ALPN identifier? | `h3` |
| HTTP/2 cleartext ALPN identifier? | `h2c` (브라우저 미지원) |
| 103 Early Hints RFC? | RFC 8297 |
| HTTP/2 Rapid Reset CVE? | CVE-2023-44487 |

---

## 🔗 시리즈 노트

- [[http1-1-concept-explainer]]
- [[http2-concept-explainer]]
- [[http1-1-problems-and-http2-evolution]]
- [[why-http1-1-still-dominates]]
- [[http2-perspective-grpc-and-ecosystem]]
- [[http3-quic-concept-explainer]]
- [[grpc-concept-deep-dive]]
- [[long-polling-http-realtime-communication]]
- [[http-status-code-429-303]]

## 📎 Sources

1. [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
2. [RFC 9112 — HTTP/1.1](https://www.rfc-editor.org/rfc/rfc9112)
3. [RFC 9113 — HTTP/2](https://www.rfc-editor.org/rfc/rfc9113)
4. [RFC 9114 — HTTP/3](https://www.rfc-editor.org/rfc/rfc9114)
5. [RFC 9000 — QUIC](https://www.rfc-editor.org/rfc/rfc9000)
6. [RFC 9204 — QPACK](https://www.rfc-editor.org/rfc/rfc9204)
7. [RFC 9218 — Extensible Priorities](https://www.rfc-editor.org/rfc/rfc9218)
8. [RFC 8297 — 103 Early Hints](https://www.rfc-editor.org/rfc/rfc8297)
9. [HTTP/2 Rapid Reset analysis — Cloudflare](https://blog.cloudflare.com/technical-breakdown-http2-rapid-reset-ddos-attack/)
10. [HTTP/3 explained — Daniel Stenberg](https://http3-explained.haxx.se/)
