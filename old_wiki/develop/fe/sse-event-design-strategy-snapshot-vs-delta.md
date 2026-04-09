---
created: 2026-03-02
updated: 2026-03-04
source: claude-code
tags: [sse, real-time, event-driven, web-architecture, frontend, backend, dashboard, streaming, kafka, event-sourcing]
---

# 📖 SSE 이벤트 설계 전략 비교 — Snapshot vs Delta Event

> 💡 **한줄 요약**: 업계에서는 SSE 이벤트 설계를 Fact Event(스냅샷)과 Delta Event(개별)로 구분하며, 이벤트 빈도·페이로드 크기·정합성 요구에 따라 선택이 달라진다. 실무에서는 두 방식을 결합한 하이브리드 접근이 가장 흔하다.

> 📌 **용어 출처**: "Fact Event / Delta Event" 분류는 [Confluent의 이벤트 스트리밍 설계 과정](https://developer.confluent.io/courses/event-design/fact-vs-delta-events/)에서 유래. 원래 Apache Kafka 기반 이벤트 스트리밍 패턴이며, SSE 설계에도 동일하게 적용 가능하다.

---

## 1️⃣ Approach A: 스냅샷 (대시보드 전체 상태 전송)

반응 발생 → 서버가 대시보드 전체 데이터를 재계산 → `dashboard_update` 이벤트로 전송

```js
// 프론트엔드: setState 한 줄이면 끝. 항상 정확.
setDashboardState(event.data);
```

## 2️⃣ Approach B: 개별 이벤트 (반응 하나만 전송)

반응 발생 → `{ type: "HIT", tags: [...], menu: "아메리카노" }` 전송 → 프론트에서 카운트 +1, 태그 분포 재계산, 메뉴 순위 재정렬

```js
// 프론트엔드: 각 컴포넌트마다 reducer로 증분 계산 (복잡)
dispatch({ type: "HIT", payload: event.data });
```

## 3️⃣ Approach C: 하이브리드 (실무 권장)

평상시에는 Delta 이벤트로 경량 전송, 재연결 시에는 Snapshot으로 전체 상태 동기화.

```js
// 재연결 감지 시 → Snapshot으로 전체 상태 복원
// 정상 스트리밍 시 → Delta로 증분 업데이트
eventSource.onopen = () => requestFullSnapshot();
eventSource.onmessage = (e) => {
  if (e.type === 'snapshot') setDashboardState(e.data);
  else dispatch({ type: e.data.type, payload: e.data });
};
```

---

## 4️⃣ 비교표

| 항목 | A: 스냅샷 | B: 개별 이벤트 |
|------|-----------|----------------|
| **네트워크 페이로드** | 크다 (~1-5KB/이벤트) | 작다 (~100-200B/이벤트) |
| **데이터 정합성** | 완벽 (항상 서버 기준) | 이벤트 누락 시 drift 위험 * |
| **프론트엔드 복잡도** | 최소 (setState 한 줄) | 높음 (컴포넌트별 reducer 필요) |
| **서버 부하** | 상태 재계산 필요 ** | 거의 없음 (이벤트 전달만) |
| **재접속 처리** | 간단 (최신 스냅샷 전송) | 복잡 (이벤트 리플레이 또는 전체 resync) |
| **전일 대비 delta 계산** | 서버에서 계산, 항상 정확 | 클라이언트 단독 계산 불가 |
| **디버깅** | 이벤트 하나만 보면 전체 상태 파악 | 이벤트 시퀀스 재구성 필요 |
| **구현 시간** | 낮음 (기존 overview API 재사용) | 높음 (새 reducer + 에러 처리) |

> \* SSE 명세의 `Last-Event-ID`는 best-effort 메커니즘으로, 모든 이벤트 전달을 보장하지 않는다. ([WHATWG SSE 명세](https://html.spec.whatwg.org/dev/server-sent-events.html))
>
> \*\* "이벤트마다 DB 풀 재조회"는 단순 구현 기준. Redis 등 인메모리 캐시에 집계 상태를 유지하면 서버 부하를 크게 줄일 수 있다.

> 📊 **수치 참고**: 페이로드 크기(1-5KB, 100-200B) 및 빈도 임계값(1/sec, 10/sec)은 공식 업계 벤치마크가 아닌 경험적 가이드라인이다. 실제 시스템 특성에 따라 조정 필요.

---

## 5️⃣ 핵심 판단 기준

### 스냅샷이 적합한 경우

- 이벤트 빈도가 낮을 때 (초당 1건 이하)
- 페이로드가 작을 때 (10KB 이하)
- 여러 위젯이 같은 소스 데이터에서 파생될 때
- 전일 대비 같은 서버 계산이 필요할 때

### 개별 이벤트가 적합한 경우

- 이벤트 빈도가 높을 때 (초당 10건 이상)
- 위젯이 완전히 독립적일 때
- append-only 유스케이스 (로그, 채팅, 알림 리스트)

### 하이브리드가 적합한 경우 (실무 최다 선택)

- Delta의 효율성 + Snapshot의 정합성이 모두 필요할 때
- 재연결이 빈번한 모바일 환경
- 장시간 연결 유지가 필요한 대시보드

---

## 6️⃣ SSE 설계 시 필수 고려사항

### 브라우저 동시 연결 제한

HTTP/1.1 환경에서 브라우저는 **도메인당 최대 6개**의 동시 연결만 허용한다. SSE는 지속적 HTTP 연결을 사용하므로, 같은 도메인에 여러 탭을 열면 이 한도를 공유한다. **HTTP/2 사용 시 단일 연결에서 100~200개 스트림 다중화가 가능**하여 이 제한이 사실상 해소된다. ([MDN SSE 문서](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events))

### SSE 텍스트 전용 제약

SSE 명세는 UTF-8 텍스트만 지원한다. 바이너리 데이터 전송 시 base64 인코딩이 필요하며, 약 **33%의 추가 페이로드 오버헤드**가 발생한다.

### gzip 압축 충돌

SSE 스트림에 gzip 압축 적용 시 이론상 70~90% 대역폭 절감이 가능하지만, 많은 프레임워크에서 압축 인코더의 버퍼링으로 인해 **실시간 flush가 지연**되는 문제가 발생한다. SSE 사용 시 압축 설정에 주의가 필요하다.

### 자동 재연결

브라우저 `EventSource`는 연결 끊김 시 자동 재연결을 시도한다. 기본 지연 2~3초이며, 서버의 `retry:` 필드로 조정 가능하다.

---

## 7️⃣ 참고 자료

- [Confluent: Fact vs. Delta Events](https://developer.confluent.io/courses/event-design/fact-vs-delta-events/)
- [WHATWG HTML Standard: Server-sent events](https://html.spec.whatwg.org/dev/server-sent-events.html)
- [MDN: Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)
- [O'Reilly/hpbn.co: Server-Sent Events (SSE)](https://hpbn.co/server-sent-events-sse/)
- [Martin Fowler: Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html)
- [Ably: WebSockets vs SSE](https://ably.com/blog/websockets-vs-sse)
