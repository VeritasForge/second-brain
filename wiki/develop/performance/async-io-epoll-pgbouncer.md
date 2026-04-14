---
tags: [epoll, kqueue, iocp, async-io, pgbouncer, connection-pooling]
created: 2026-04-15
---

# 비동기 IO — epoll, kqueue, IOCP, 이벤트 루프, Pgbouncer

---

## 1. epoll — Linux IO 이벤트 감시 메커니즘

### 1.1 왜 epoll이 필요한가 — 역사적 배경

초기 방식 — select/poll:

```c
// select: 모든 fd를 매번 순회
int select(int nfds, fd_set *readfds, ...);

// 동작 방식
while (true) {
    select(1024, &fds, ...);  // 최대 1024개 제한
    // 1024개 fd 전부 순회하며 체크
    // → O(n) 탐색
    // → fd 수가 많을수록 느려짐
}
```

문제점: fd 1000개 감시 중 1개에 이벤트 발생 → 1000개 전부 순회해서 어떤 fd인지 찾아야 함 → O(n) → 동시 접속자 많을수록 급격히 느려짐.

`FD_SETSIZE`는 glibc에서 1024로 하드코딩. 사실상 하드 리밋으로 취급.

### 1.2 epoll 구조

핵심 설계: **"이벤트 발생한 fd만 알려줘"**

```
커널 내부:
┌─────────────────────────────┐
│  epoll 인스턴스              │
│  ┌─────────────────────┐    │
│  │  관심 fd 목록 (RBT) │    │  ← 레드블랙트리로 관리
│  │  fd1, fd2, fd3...   │    │
│  └─────────────────────┘    │
│  ┌─────────────────────┐    │
│  │  준비된 fd 목록      │    │  ← 이벤트 발생한 것만
│  │  fd2, fd7           │    │
│  └─────────────────────┘    │
└─────────────────────────────┘
```

### 1.3 epoll 3가지 시스템콜

```c
// 1. epoll 인스턴스 생성
int epfd = epoll_create1(0);

// 2. 감시할 fd 등록
struct epoll_event ev;
ev.events = EPOLLIN;  // 읽기 이벤트 감시
ev.data.fd = socket_fd;
epoll_ctl(epfd, EPOLL_CTL_ADD, socket_fd, &ev);

// 3. 이벤트 대기
struct epoll_event events[64];
int n = epoll_wait(epfd, events, 64, -1);
// n개의 이벤트 발생한 fd만 반환
for (int i = 0; i < n; i++) {
    handle(events[i].data.fd);
}
```

### 1.4 성능 복잡도

> **[검증 정정]** "epoll은 O(1)으로 감시"는 반쪽짜리 맞음.
> - `epoll_ctl` (fd 추가/삭제): **O(log n)** — 레드블랙 트리 연산
> - `epoll_wait` (이벤트 대기): **O(1)** 대기 + **O(k)** 반환 (k = ready event 수)
> - select의 O(n)(전체 fd 스캔)과 비교하면, 전체 fd를 스캔하지 않는 것이 핵심 차이

동시 접속자 수에 따른 처리 시간:

| 접속자   | select    | epoll |
| -------- | --------- | ----- |
| 100      | 빠름      | 빠름  |
| 1,000    | 느려짐    | 빠름  |
| 10,000   | 매우 느림 | 빠름  |
| 100,000  | 불가능    | 빠름  |

### 1.5 Level Trigger vs Edge Trigger

| 항목   | Level Trigger (기본)            | Edge Trigger (EPOLLET)          |
| ------ | ------------------------------- | ------------------------------- |
| 동작   | 데이터 남아있으면 계속 이벤트   | 상태 변화 순간에만 이벤트       |
| 안전성 | 높음 (놓칠 위험 없음)           | 낮음 (반드시 전부 읽어야)       |
| 성능   | 이벤트 중복 발생                | 고성능                          |

Go netpoller: Edge Trigger 사용 (소스코드 `EPOLLET` 플래그 확인됨)

> **[검증 정정]** "Java NIO는 Level Trigger" — 기본 Selector는 LT이나, **Netty의 EpollEventLoop는 ET를 명시적으로 사용**. "구현에 따라 다름"이 정확.

### 1.6 코루틴/고루틴과 연결

```
1. 코루틴A: DB 소켓에 read 요청
2. 런타임: epoll에 해당 소켓 fd 등록 "이 소켓에 데이터 오면 알려줘"
3. 코루틴A 중단, 스레드 반납

4. 스레드는 다른 코루틴 실행 중...

5. DB 응답 도착
   → 커널이 epoll 준비 목록에 fd 추가
   → epoll_wait 반환

6. 런타임: "코루틴A 재개"
   → Dispatcher 큐에 등록
   → 스레드가 코루틴A 재개
```

```
Kotlin (NIO 기반): epoll → Java NIO Selector → Dispatcher → 코루틴 재개
Go:                epoll → netpoller → GMP 스케줄러 → 고루틴 재개
Node.js:           epoll → libuv → 이벤트 루프 → 콜백 실행

모두 epoll 위에서 돌아감!
```

---

## 2. epoll vs IOCP

> **[검증 정정]** "IOCP가 DMA로 유저 버퍼에 직접 쓴다"는 **틀림**.
> DMA는 NIC→커널 버퍼 단계의 기술. IOCP는 Proactor 패턴으로 커널이 I/O 완료 후 유저 버퍼에 복사.

> **[검증 정정]** "epoll 2단계 복사 vs IOCP 1단계 복사"도 **틀림**.
> **둘 다 커널→유저 버퍼 복사는 1회 동일.** Reactor vs Proactor 모델 차이이지 복사 횟수 차이가 아님.

| 항목 | epoll (Reactor)                     | IOCP (Proactor)                       |
| ---- | ----------------------------------- | ------------------------------------- |
| 철학 | "읽을 준비 됐어, 네가 읽어"        | "내가 읽어놨어, 가져가"              |
| 흐름 | ready 알림 → 앱이 read() 호출      | 앱이 미리 요청 → 커널이 완료 후 통지 |
| 복사 | 커널→유저 1회                       | 커널→유저 1회 (동일)                  |
| OS   | Linux                               | Windows                               |

```c
// epoll: 준비 통지 → 앱이 직접 read
int n = epoll_wait(epfd, events, 64, -1);
for (int i = 0; i < n; i++) {
    read(events[i].fd, buffer, size);  // 앱이 직접 읽음
    process(buffer);
}
```

```c
// IOCP: 완료 통지 → 버퍼에 이미 있음
ReadFile(handle, buffer, size, NULL, &overlapped);  // 비동기 요청
// ... 다른 작업 ...
GetQueuedCompletionStatus(iocp, &bytes, &key, &overlapped, INFINITE);
process(buffer);  // 이미 buffer에 데이터 있음
```

### kqueue (macOS/BSD)

epoll과 거의 동일한 준비 통지 방식. 다만 파일 변경, 프로세스 이벤트, 시그널, 타이머(나노초) 등 더 다양한 이벤트 감시 가능. epoll은 fd 이벤트만 처리하며 나머지는 `signalfd`, `timerfd`, `inotify` 등 별도 시스템콜 필요.

### OS별 추상화

```
Go netpoller (런타임 내장)    → epoll/kqueue/IOCP
libuv (Node.js 외부 라이브러리) → epoll/kqueue/IOCP
Java NIO Selector (JDK)       → epoll/kqueue/IOCP

개발자는 신경 안 써도 됨
```

Go가 레이어가 가장 적은 이유: 스케줄러와 netpoller가 **런타임에 통합**되어 별도 리액티브 라이브러리 스택 불필요.

```
Kotlin + Spring WebFlux:
  코루틴 → Reactor → Netty → Java NIO Selector → epoll

Go:
  고루틴 → netpoller → epoll

→ Go는 런타임에 통합되어 "투명"하다가 정확한 표현
```

---

## 3. 이벤트 루프 vs 코루틴/고루틴

### 3.1 이벤트 루프 구조

```
Node.js:
단일 스레드 → [이벤트 루프] → 콜백1 → 콜백2 → 콜백3
                                ↑ IO 완료 이벤트
```

### 3.2 IO Bound만 놓고 보면 원리는 동일

```
이벤트 루프:  IO 대기 → epoll → 콜백 실행
코루틴:       IO 대기 → epoll → 코루틴 재개

원리 동일, 비용도 비슷!
```

순수 IO Bound라면 이벤트 루프가 오히려 더 단순하고 비용도 쌈. 실제로 Node.js가 Java 멀티스레드 서버를 성능으로 이긴 사례가 많았던 이유.

### 3.3 차이가 나는 지점: CPU Bound 혼합

```
순수 IO Bound:
  Node.js 이벤트 루프    ██░░░░██░░░░██  (충분히 효율적)
  코루틴 (4스레드)       ██░░░░██░░░░██  (비슷)

IO + CPU 혼합:
  Node.js 이벤트 루프    ██████████░░░░  (CPU 작업이 루프 블로킹!)
  코루틴 (4스레드)       ████░░████░░    (다른 스레드가 처리)
```

```javascript
// Node.js의 치명적 약점
app.get('/api', async (req, res) => {
    const data = await db.query()     // IO → 문제없음
    const result = heavyCalculation() // 이 순간 전체 서버 블로킹!
    res.json(result)
})
```

### 3.4 비교 정리

**단일 스레드 이벤트 루프:**

- 장점: 컨텍스트 스위칭 없음, 락/동기화 불필요, 구조 단순
- 단점: CPU 코어 1개만 사용, CPU 작업이 전체 루프 블로킹

**코루틴/고루틴 (멀티스레드):**

- 장점: CPU 코어 전부 활용, CPU 작업이 다른 코루틴 블로킹 안함
- 단점: 락/동기화 필요, 구조 복잡

Node.js는 **Worker Threads**로 CPU 작업 분리. 결국 코루틴과 같은 방향으로 수렴.

---

## 4. Pgbouncer — 커넥션 다중화(Multiplexing)

### 4.1 왜 필요한가

```
HikariCP만 사용 (API 서버 10대):

API-1 [HikariCP 10개] ──10개 연결──→ ┌────────────┐
API-2 [HikariCP 10개] ──10개 연결──→ │ PostgreSQL │
...                                  │ max_conn   │
API-10 [HikariCP 10개] ──10개 연결──→│  = 100     │
                                     └────────────┘
총 100개 연결 → 스케일아웃하면 200개 → max_connections 초과!
```

```
Pgbouncer 사용:

API-1~10 (각 10개) ──→ Pgbouncer (pool = 20) ──→ DB (연결 20개만)
100개 클라이언트 연결을 20개 DB 연결로 다중화
```

### 4.2 Multiplexing 원리

**100개 클라이언트가 동시에 쿼리를 날리지 않는다**는 사실을 이용.

```
시간 →→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→

클라이언트 (100개):
  C1: ────[트랜잭션]──────────────────[트랜잭션]────
  C2: ──────────[트랜잭션]────────────────────────────
  C3: ────────────────[트랜잭션]──────────────────────

DB 연결 풀 (20개):
  DB1: ─[C1 사용]──[C3 사용]──────[C100 사용]────────
  DB2: ────[C2 사용]──────[C1 사용]──────────────────
```

비유: **은행 창구 20개에 대기표 100명.** 대부분 서류 작성 중(비즈니스 로직)이라 창구(DB 연결)를 안 쓰고 있어서 20개로 충분.

### 4.3 풀 다 사용 중이면?

```
C21이 쿼리 보냄
    ↓
Pgbouncer: "풀 다 사용 중!"
    ↓
대기 큐에 넣음 ← query_wait_timeout (기본 120초) 동안 대기
    ↓
120초 안에 풀 반납됨? ──YES──→ 빌려줘서 처리 ✅
    │
    NO → "ERROR: no more connections allowed" ❌
```

TCP 연결이 유지되고 있으므로 Pgbouncer가 소켓 fd를 들고 있어 큐잉 후 응답 전달 문제없음.

### 4.4 용도별 풀 분리

```ini
# pgbouncer.ini
[databases]
order_db = host=db1.internal dbname=orders pool_size=15
cart_db  = host=db1.internal dbname=carts  pool_size=5
```

이유: 격리(주문 폭주해도 장바구니 무관) + 우선순위(중요 서비스에 더 많은 커넥션) + 모니터링(풀별 사용률 추적)

### 4.5 Pgbouncer는 소켓 연결만 중개

TCP 소켓 연결을 중개하는 경량 프록시:

- ✅ TCP 소켓 연결 다중화
- ✅ PostgreSQL 프로토콜 메시지 파싱/전달
- ✅ 트랜잭션/쿼리 단위로 DB 연결 빌려주고 반납
- ❌ SQL 내용 해석/변환 안 함
- ❌ 캐싱 안 함
- ❌ 쿼리 라우팅(Read/Write 분리) 안 함

풀링 모드 3가지:

```
session 모드:     API 연결 1개 = DB 연결 1개 (HikariCP와 다를 바 없음)
transaction 모드: 트랜잭션 끝나면 DB 연결 반납 ← 가장 많이 씀
statement 모드:   쿼리 하나 끝날 때마다 반납 (prepared statement 제약)
```
