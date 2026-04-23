---
tags: [connection-pool, http, eviction, keep-alive, performance, networking]
created: 2026-04-22
---

# Connection Pool의 Eviction 전략: Lazy vs Idle (Proactive)

## 1. 개요

Connection Pool에서 "죽은 연결" 또는 "오래 쓰지 않은 연결"을 정리하는 방식은 크게 두 가지로 나뉜다.

```
                     Connection Pool Eviction 전략

                    +-----------------------------------+
                    |        Eviction 전략               |
                    +----------------+------------------+
                                     |
                    +----------------+----------------+
                    |                                 |
          +-----------------+              +---------------------+
          |  Lazy Eviction   |              |  Proactive Eviction  |
          |  (사용 시 검사)   |              |  (백그라운드 정리)    |
          +-----------------+              +----------+----------+
                                                      |
                                         +------------+------------+
                                         |                         |
                               +------------------+    +------------------+
                               | Expired Eviction  |    |  Idle Eviction   |
                               | (만료 연결 제거)   |    | (유휴 연결 제거)  |
                               |                  |    |                  |
                               | 서버 Keep-Alive   |    | 클라이언트 설정   |
                               | timeout 기반      |    | idle timeout 기반 |
                               +------------------+    +------------------+
```

---

## 2. Lazy Eviction (지연 제거)

Pool에서 연결을 꺼내는(borrow) 시점에 "이 연결이 아직 살아있나?" 검사하는 방식이다.

### 동작 흐름

```
[요청 발생]
    |
    v
Pool에서 connection 꺼냄 (borrow)
    |
    v
"이 연결 살아있나?" 검사 (stale check)
    |
    +-- 살아있음 -> 그대로 사용
    |
    +-- 죽어있음 -> 폐기 -> 새 연결 생성 -> 사용
```

> 비유: 냉장고에서 음식을 꺼낼 때마다 "이거 상했나?" 냄새를 맡아보는 것. 가끔 놓칠 수 있다.

### 한계: 100% 신뢰할 수 없다

Apache HttpClient 공식 문서의 원문:

> "HttpClient tries to mitigate the problem by testing whether the connection is 'stale', that is no longer valid because it was closed on the server side, prior to using the connection for executing an HTTP request. **The stale connection check is not 100% reliable.**"

idle 상태의 연결은 소켓 I/O 이벤트를 감지할 수 없다. 서버가 연결을 끊었더라도(FIN 전송), 클라이언트가 실제로 데이터를 보내기 전까지는 TCP 레벨에서 이를 감지하지 못하는 **half-open** 상태가 발생할 수 있다.

---

## 3. Proactive Eviction (능동 제거)

별도의 모니터 스레드가 주기적으로 Pool을 순회하며 죽거나 오래된 연결을 제거하는 방식이다. Proactive Eviction 안에 두 가지 하위 전략이 있다.

### 3.1 Expired Connection Eviction (만료 연결 제거)

서버가 `Keep-Alive: timeout=30`으로 응답했다면, 30초가 지나면 그 연결은 "만료"로 간주하고 제거한다. **서버가 선언한 수명 기반**.

### 3.2 Idle Connection Eviction (유휴 연결 제거)

서버의 Keep-Alive 설정과 무관하게, **클라이언트가 정한 기준 시간** 동안 사용되지 않은 연결을 제거한다.

### 동작 흐름

```
[모니터 스레드] (5초마다 실행)
    |
    v
Pool의 모든 idle connection 순회
    |
    +-- expired connection 발견 -> 즉시 제거
    |   (서버가 선언한 Keep-Alive timeout 초과)
    |
    +-- idle timeout 초과 connection 발견 -> 즉시 제거
        (클라이언트 설정 시간 초과, 예: 30초 이상 미사용)
```

### Apache HttpClient의 구현 예시

```java
public static class IdleConnectionMonitorThread extends Thread {
    private final HttpClientConnectionManager connMgr;
    private volatile boolean shutdown;

    @Override
    public void run() {
        try {
            while (!shutdown) {
                synchronized (this) {
                    wait(5000);  // 5초마다 실행
                    // 만료된 연결 제거 (Expired Eviction)
                    connMgr.closeExpiredConnections();
                    // 30초 이상 idle인 연결 제거 (Idle Eviction)
                    connMgr.closeIdleConnections(30, TimeUnit.SECONDS);
                }
            }
        } catch (InterruptedException ex) {
            // terminate
        }
    }
}
```

---

## 4. Lazy vs Proactive 비교

| 기준             | Lazy Eviction                         | Proactive Eviction                    |
| ---------------- | ------------------------------------- | ------------------------------------- |
| **검사 시점**    | 연결 사용(borrow) 시                  | 백그라운드 주기적                     |
| **별도 스레드**  | 불필요                                | 필요 (모니터 스레드)                  |
| **신뢰도**       | 100% 아님 (half-open 감지 불가)       | 높음 (사전 제거)                      |
| **오버헤드**     | 매 요청마다 검사 비용                 | 주기적 순회 비용 (낮음)               |
| **stale 발견**   | 실제 요청 시 (늦음)                   | 사전에 (빠름)                         |
| **사용자 영향**  | 첫 요청 지연 or 실패 가능            | 거의 없음                             |

```
시간축 -->

Lazy Eviction:
  idle idle idle idle [요청!] -> "죽었네" -> 새 연결 -> 재시도
                                ^^^^^^^^
                              여기서야 발견 (늦음)

Proactive (Idle) Eviction:
  idle idle [모니터: "30초 지남, 제거!"] ... [요청!] -> 새 연결 -> 바로 성공
            ^^^^^^^^^^^^^^^^^^^^^^^^^
            미리 정리 (빠름)
```

Apache 공식 문서는 proactive 방식을 명시적으로 권장한다:

> "the only feasible solution that does not involve a one thread per socket model for idle connections is **a dedicated monitor thread** used to evict connections"

---

## 5. Idle Eviction 시 연결 사용 후 타이머가 리셋되는가?

**리셋된다.**

idle 타이머의 기준은 **"Pool에 마지막으로 반환된 시각"**이다.

### 동작 원리

Apache HttpClient 소스코드(`PoolingHttpClientConnectionManager.java`)에서 확인:

- 연결이 Pool에 반환될 때 `entry.updateState(state)` 호출 -> `updated` 타임스탬프 갱신
- idle 검사 시 `Deadline.calculate(poolEntry.getUpdated(), idleTimeout).isExpired()`로 경과 시간 계산

```
idle 타이머의 기준 = "Pool에 마지막으로 반환된 시각"

t=0s   connection을 Pool에 반환 -> updated = 0s -> idle 타이머 시작
t=10s  Pool에서 borrow (꺼냄) -> 사용 중 (idle 아님)
t=15s  사용 완료, Pool에 반환 -> updated = 15s -> idle 타이머 리셋!
t=45s  30초 지남? -> 현재(45) - updated(15) = 30초 -> 제거 대상!
```

```
connection A의 생명주기:

  [반환] --- idle 10초 --- [borrow] -- 사용 5초 -- [반환] --- idle 30초 --- [제거!]
  t=0                     t=10                    t=15                    t=45
                                                  ^^^^
                                                  여기서 타이머 리셋!
                                                  (idle 30초 다시 카운트)
```

> 비유: 도서관 책 대출 기한과 같다. 빌려간 책을 반납하고 다시 빌리면, 대출 기한이 **반납 시점부터** 새로 시작된다. 이전에 얼마나 빌렸었는지는 무관.

HikariCP도 동일한 패턴을 따른다. `PoolEntry`의 `lastAccessed` 타임스탬프가 반환 시 갱신되며, housekeeper 스레드가 `elapsedMillis(entry.lastAccessed, now) > idleTimeout`으로 검사한다.

### 주의: HikariCP의 idleTimeout 특수 동작

HikariCP 메인테이너(Brett Wooldridge)에 따르면, `idleTimeout`은 **Pool 크기 관리용**이지 연결 수명 관리용이 아니다:

- `minimumIdle` 이하의 연결은 idle timeout이 지나도 **제거하지 않는다**
- `minimumIdle == maximumPoolSize`이면 idle eviction이 **사실상 비활성화**
- 서버 측 timeout 대응에는 `maxLifetime` 설정을 사용해야 한다

---

## 6. 라이브러리별 지원 현황

| 기능                         | urllib3 (Python)   | Apache HttpClient (Java)      | HikariCP (Java)         |
| ---------------------------- | ------------------ | ----------------------------- | ----------------------- |
| Lazy Eviction                | stale check        | stale check                   | alive test              |
| Proactive Idle Eviction      | 미지원             | `closeIdleConnections()`      | `idleTimeout`           |
| Proactive Expired Eviction   | 미지원             | `closeExpiredConnections()`   | -                       |
| Idle Timeout 설정            | 미지원             | 지원                          | 기본 600초              |
| 백그라운드 모니터 스레드     | 미지원             | 지원                          | Housekeeper             |
| 타이머 리셋 (반환 시)        | -                  | `updated` 갱신               | `lastAccessed` 갱신     |

urllib3 메인테이너의 입장 (GitHub Issue #2498 원문):

> "We don't have active idle connection cleanup as doing so would likely require background work (ie threads). Instead we have passive idle connection cleanup where a TCP connection naturally gets closed as a part of TCP_KEEPALIVE."

Python `requests`를 사용하는 환경에서는 idle eviction이 없으므로, **Retry 정책**으로 stale connection을 보완해야 한다.

---

## 핵심 정리

1. **Lazy Eviction**은 연결을 사용하는 시점에 stale check를 수행한다. 구현이 단순하지만 half-open TCP 상태를 감지하지 못해 100% 신뢰할 수 없다.
2. **Proactive Eviction**은 백그라운드 모니터 스레드가 주기적으로 만료/유휴 연결을 제거한다. Apache 공식 문서가 권장하는 방식이다.
3. **Idle Eviction은 Proactive의 하위 전략**으로, 클라이언트가 설정한 시간 동안 사용되지 않은 연결을 제거한다.
4. **연결이 사용(borrow->return)되면 idle 타이머는 리셋된다.** 기준은 "Pool에 마지막으로 반환된 시각"이며, Apache HttpClient와 HikariCP 모두 동일한 패턴을 따른다.
5. **urllib3(Python requests)는 idle eviction을 지원하지 않는다.** TCP_KEEPALIVE에 의한 자연적 정리에 의존하며, stale connection은 Retry 정책으로 보완해야 한다.

---

## Sources

1. [Apache HttpClient 공식 문서 - Connection Management](https://hc.apache.org/httpcomponents-client-4.5.x/current/tutorial/html/connmgmt.html)
2. [Apache HttpClient 소스코드 - PoolingHttpClientConnectionManager.java](https://github.com/apache/httpcomponents-client/blob/master/httpclient5/src/main/java/org/apache/hc/client5/http/impl/io/PoolingHttpClientConnectionManager.java)
3. [urllib3 GitHub Issue #2498 - Support for connection idle timeout](https://github.com/urllib3/urllib3/issues/2498)
4. [HikariCP GitHub Issue #1128 - IdleTimeout is unreliable](https://github.com/brettwooldridge/HikariCP/issues/1128)
5. [HikariCP GitHub Issue #683 - idleTimeout not working as expected](https://github.com/brettwooldridge/HikariCP/issues/683)
6. [Baeldung - Apache HttpClient Connection Management](https://www.baeldung.com/httpclient-connection-management)
