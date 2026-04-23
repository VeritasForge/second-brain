---
tags: [python, http, connection-pool, keep-alive, networking, performance]
created: 2026-04-22
---

# Python requests 라이브러리와 HTTP Connection Pool, Keep-Alive 완전 정리

## 1. requests 라이브러리의 Connection Pool 관리

`requests` 라이브러리 자체는 connection pool을 직접 관리하지 않지만, 내부적으로 `urllib3`를 사용하고 있고 `urllib3`가 connection pooling을 담당한다. **어떻게 사용하느냐**에 따라 pool이 작동하는지 여부가 달라진다.

### 1.1 두 가지 사용 방식 비교

#### `requests.get()` 직접 호출 — Pool 재활용 안 됨

```python
import requests

# 매번 새로운 연결을 만들고, 끝나면 버림
requests.get("https://api.example.com/data")
requests.get("https://api.example.com/data")  # 또 새 연결!
```

> 비유: 매번 새 택시를 잡는 것. 타고 내리면 그 택시는 사라짐.

#### `requests.Session()` 사용 — Pool 재활용 됨

```python
import requests

session = requests.Session()

# 같은 호스트로의 연결을 재활용!
session.get("https://api.example.com/data")
session.get("https://api.example.com/users")  # 기존 연결 재사용!
```

> 비유: 전용 기사가 있는 차. 한번 불러놓으면 계속 태워줌.

### 1.2 내부 동작 구조

```
requests.Session()
    |
    v
HTTPAdapter (기본 장착)
    |
    v
urllib3.PoolManager
    |
    +-- ConnectionPool("api.example.com")  <- 호스트별로 풀 생성
    |       +-- connection 1 (재사용 가능)
    |       +-- connection 2
    |       +-- ...
    |
    +-- ConnectionPool("other-api.com")
            +-- connection 1
            +-- ...
```

### 1.3 기본 설정값

| 설정               | 기본값   | 의미                                       |
| ------------------ | -------- | ------------------------------------------ |
| `pool_connections` | **10**   | 호스트(도메인)별 풀 개수                   |
| `pool_maxsize`     | **10**   | 풀 하나당 최대 연결 수                     |
| `pool_block`       | `False`  | 풀이 꽉 차면 새 연결을 만들지, 기다릴지    |

### 1.4 Pool 크기 커스터마이징

```python
from requests.adapters import HTTPAdapter

session = requests.Session()

adapter = HTTPAdapter(
    pool_connections=20,   # 20개 호스트까지 풀 유지
    pool_maxsize=50,       # 호스트당 최대 50개 연결
    pool_block=True        # 풀이 꽉 차면 기다림 (새 연결 안 만듦)
)

session.mount("https://", adapter)
session.mount("http://", adapter)
```

### 1.5 성능 차이 시각화

```
직접 호출 (requests.get):
  요청1: [DNS조회 -> TCP연결 -> TLS핸드셰이크 -> 데이터전송 -> 연결종료]
  요청2: [DNS조회 -> TCP연결 -> TLS핸드셰이크 -> 데이터전송 -> 연결종료]
  요청3: [DNS조회 -> TCP연결 -> TLS핸드셰이크 -> 데이터전송 -> 연결종료]
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
         매번 이 비용이 반복됨

Session 사용:
  요청1: [DNS조회 -> TCP연결 -> TLS핸드셰이크 -> 데이터전송]  <- 최초 1회만
  요청2:                                       [데이터전송]  <- 연결 재사용!
  요청3:                                       [데이터전송]  <- 연결 재사용!
```

### 1.6 실무 권장사항

| 상황                   | 권장 방식                            |
| ---------------------- | ------------------------------------ |
| 한두 번 요청           | `requests.get()` 괜찮음             |
| 같은 서버에 반복 요청  | **`Session()` 필수**                |
| 고성능/대량 요청       | `Session()` + `HTTPAdapter` 커스텀  |
| 비동기가 필요할 때     | `httpx` 또는 `aiohttp` 고려        |

`Session`은 connection pool 외에도 **쿠키 자동 유지**, **인증 헤더 재사용**, **기본 설정 공유**를 제공한다.

---

## 2. HTTP Keep-Alive와 Connection Pool의 관계

Connection Pool이 연결을 재사용할 수 있는 이유가 바로 **HTTP Keep-Alive** 덕분이다. 둘은 짝꿍처럼 함께 작동한다.

### 2.1 HTTP 버전별 기본 동작

| HTTP 버전    | 기본 동작                 | Keep-Alive                                               |
| ------------ | ------------------------- | -------------------------------------------------------- |
| **HTTP/1.0** | 요청마다 연결 끊음        | `Connection: keep-alive` 헤더를 **명시적으로** 보내야 유지 |
| **HTTP/1.1** | **기본이 Keep-Alive**     | 끊고 싶으면 `Connection: close`를 보내야 함              |
| **HTTP/2**   | 멀티플렉싱 (더 진화)      | 하나의 연결로 여러 요청 동시 처리                        |

> 비유:
> - **HTTP/1.0**: 전화할 때마다 번호 누르고 -> 통화 -> 끊기 -> 다시 번호 누르기
> - **HTTP/1.1 Keep-Alive**: 전화 연결해두고 -> 할 말 하고 -> 또 할 말 하고 -> 필요 없을 때 끊기
> - **HTTP/2**: 전화 여러 통을 하나의 회선으로 동시에 하는 것

### 2.2 실제 HTTP 헤더로 보는 Keep-Alive

**Keep-Alive가 작동할 때:**

```
# 요청 1
GET /api/data HTTP/1.1
Host: api.example.com
Connection: keep-alive          <- 연결 유지해줘!

# 응답 1
HTTP/1.1 200 OK
Connection: keep-alive          <- OK, 유지할게
Keep-Alive: timeout=30, max=100 <- 30초 동안, 최대 100번까지

# 요청 2 (같은 TCP 연결 위에서!)
GET /api/users HTTP/1.1         <- TCP 핸드셰이크 없이 바로!
Host: api.example.com
Connection: keep-alive
```

**Keep-Alive 없으면:**

```
# 요청 1
GET /api/data HTTP/1.1
Host: api.example.com
Connection: close               <- 끊어!

# 응답 1
HTTP/1.1 200 OK
Connection: close
    X TCP 연결 종료 (FIN -> ACK -> FIN -> ACK)

# 요청 2 -> 처음부터 다시!
    O TCP 연결 생성 (SYN -> SYN-ACK -> ACK)  <- 비용 발생!
    O TLS 핸드셰이크 (HTTPS면 추가 비용!)
```

### 2.3 세 가지의 관계 정리

```
Keep-Alive (프로토콜 레벨)
    "응답 보내고 나서도 TCP 연결 끊지 마"
         |
         v 이게 있어야
Connection Pool (클라이언트 레벨)
    "안 끊긴 연결을 모아두고 재활용하자"
         |
         v 이걸로
성능 향상
    TCP 핸드셰이크 + TLS 핸드셰이크 비용 절약!
```

> **Keep-Alive는 "문을 열어두는 것"**, **Connection Pool은 "열어둔 문을 잘 관리하는 것"**. Keep-Alive 없이는 Pool에 넣을 연결 자체가 없다.

---

## 3. 서버 Keep-Alive Timeout과 Stale Connection 문제

### 3.1 서버가 idle 연결을 끊는 과정

서버가 `Keep-Alive: timeout=30`을 설정하면, idle 상태로 30초가 지난 연결을 **서버 쪽에서 일방적으로 끊어버린다.** 클라이언트의 Pool에 있는 연결이라도.

```
시간축 -->

[A의 Pool]                           [B 서버]
 t=0s   요청 1 전송 ----------->      요청 처리
        <-----------------------      응답 + "Keep-Alive: timeout=30"
        연결을 Pool에 반환 (idle)      타이머 시작: 30... 29...

 t=25s  요청 2 전송 ----------->      타이머 리셋! 30... 29...
        <-----------------------      응답 OK
        Pool에 반환 (idle)

 t=55s  (30초 동안 아무 요청 없음)     0! 타임아웃!
        <--- TCP FIN -----------      서버가 연결 끊음!

        +-------------+
        | conn: ???   | <- Pool은 아직 idle로 알고 있음
        +-------------+
```

### 3.2 Stale Connection 문제

A의 Pool은 **서버가 연결을 끊은 걸 바로 모를 수 있다.** TCP 연결이 끊겼는데 Pool에는 아직 "idle"로 남아있는 것.

> 비유: 전화기를 귀에 대고 있는데, 상대방은 이미 끊은 상태. 말을 해봐야 "뚜뚜뚜..." 소리가 나서야 끊긴 걸 알게 됨.

### 3.3 idle 연결이 끊어지는 조건들

| 조건                 | 설명                                                       |
| -------------------- | ---------------------------------------------------------- |
| **서버 타임아웃**    | 서버가 `Keep-Alive: timeout=30` 설정 -> 30초 idle이면 끊음 |
| **클라이언트 타임아웃** | urllib3가 주기적으로 오래된 연결 정리                    |
| **Pool 초과**        | maxsize를 넘으면 가장 오래된 idle 연결부터 제거            |
| **서버 재시작**      | 서버가 재시작하면 기존 연결 모두 끊김                      |
| **네트워크 오류**    | 중간 네트워크 장비가 idle 연결을 끊을 수도 있음            |

---

## 4. Stale Connection 자동 Retry 전략

idle connection을 정리하는 처리를 안 해놨더라도, 에러 발생 시 정리하고 다시 시도하는 방법이 있다.

### 4.1 urllib3의 기본 내장 동작

`urllib3`는 stale connection을 만나면 **자동으로 retry**를 해준다:

```
[요청 시도]
    |
    v
Pool에서 idle conn 꺼냄
    |
    v
요청 전송 시도
    |
    +-- 성공 -> 응답 반환
    |
    +-- 실패 (ConnectionError, RemoteDisconnected 등)
            |
            v
        "이 연결 죽었네" -> 연결 폐기
            |
            v
        새 연결 생성 -> 요청 재전송 -> 성공
```

아무 설정 안 해도 작동한다.

### 4.2 명시적 Retry 정책 설정

```python
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = Session()

retry_strategy = Retry(
    total=3,                # 최대 3번 재시도
    connect=3,              # 연결 실패 시 3번
    read=2,                 # 읽기 실패 시 2번
    backoff_factor=0.5,     # 재시도 간격: 0.5초, 1초, 2초...
    status_forcelist=[502, 503, 504],  # 이 상태코드도 재시도
)

adapter = HTTPAdapter(
    max_retries=retry_strategy,
    pool_connections=10,
    pool_maxsize=10,
)

session.mount("https://", adapter)
session.mount("http://", adapter)
```

### 4.3 방어 레벨 비교

| Level | 방법             | stale 발생          | retry 비용 | 복잡도 |
| ----- | ---------------- | ------------------- | ---------- | ------ |
| 0     | 아무것도 안 함   | 발생 -> 에러        | -          | 없음   |
| 1     | urllib3 기본     | 발생 -> 자동 복구   | 약간       | 없음   |
| 2     | Retry 명시       | 발생 -> 정교한 복구 | 약간       | 낮음   |
| 3     | 예방적 idle 정리 | 안 발생             | 없음       | 중간   |

### 4.4 Retry 시 주의: 멱등성

```
안전한 Retry (멱등성 O):         위험한 Retry (멱등성 X):
GET  /patients/123              POST /orders
HEAD /health                    POST /payments
                                 -> 2번 결제될 수 있음!
```

```python
retry = Retry(
    total=3,
    allowed_methods=["GET", "HEAD"],  # GET, HEAD만 retry
    # POST는 retry 안 함 -> 중복 생성 방지
)
```

> 비유: "물건 확인(GET)"은 몇 번 다시 해도 괜찮지만, "돈 보내기(POST)"를 자동으로 다시 하면 큰일남.

### 4.5 실무 추천 조합

```python
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_robust_session() -> Session:
    """stale connection에 강한 세션 생성"""
    session = Session()

    retry = Retry(
        total=3,
        connect=3,
        read=2,
        backoff_factor=0.3,
        status_forcelist=[502, 503, 504],
    )

    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=10,
        pool_maxsize=10,
    )

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session
```

---

## 5. Gunicorn / Uvicorn Keep-Alive 설정

### 5.1 Gunicorn

기본 Keep-Alive timeout은 **2초**로 매우 짧다.

```bash
# CLI
gunicorn app:app --keep-alive 30

# 설정 파일 (gunicorn.conf.py)
keepalive = 30  # 초 단위
```

### 5.2 주요 서버별 기본 Keep-Alive timeout

| 서버       | 기본 timeout |
| ---------- | ------------ |
| Nginx      | 75초         |
| Apache     | 5초          |
| Gunicorn   | 2초          |
| Uvicorn    | 5초          |
| Node.js    | 5초          |
| AWS ALB    | 60초         |

### 5.3 프록시와 함께 쓸 때의 핵심 원칙

뒷단 서버의 keepalive를 앞단 프록시의 timeout보다 **길게** 설정해야 한다.

```
ALB(60s)   -> Gunicorn(65s)  : Gunicorn이 더 길어서 ALB가 먼저 끊음 -> OK
ALB(60s)   -> Gunicorn(2s)   : Gunicorn이 먼저 끊음 -> 502 Bad Gateway!
```

### 5.4 AWS ALB 사용 시 주의

```
ALB idle_timeout = 60초 (기본)

잘못된 설정:
  Gunicorn keepalive = 2 (기본값)
  -> ALB는 60초 유지하려는데 Gunicorn이 2초만에 끊음
  -> ALB가 죽은 연결로 요청 보냄 -> 502 Bad Gateway!

올바른 설정:
  Gunicorn keepalive = 65
  -> ALB(60초)보다 Gunicorn(65초)이 더 길게 유지
  -> ALB가 먼저 정리하므로 stale 없음!
```

### 5.5 일반적인 설정 조합

```python
# gunicorn.conf.py -- Nginx 뒤에서 사용 시
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
keepalive = 30

# gunicorn.conf.py -- AWS ALB 뒤에서 사용 시
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
keepalive = 65  # ALB idle_timeout(60) + 여유분
```

---

## 6. 체인 통신에서의 Read Timeout 설계

### 6.1 핵심 원칙

A -> B -> C 체인에서 A의 read timeout은 B의 read timeout보다 **반드시 길어야** 한다.

```
A --> B --> C
T(A) > T(B) > T(C)
```

### 6.2 왜 A > B 여야 하는가

**잘못된 설정: A(5초) < B(10초)**

```
[A]                [B]                [C]
 | 요청 ------>     |                   |
 |                  | 요청 ------>      |
 |                  |                   | 처리 중... (8초)
 | 5초 도달!        |                   |
 | "타임아웃!"      |                   |
 | 연결 끊음        |     <------ 응답  |  <- 8초 후 도착
 |                  | "어? A가 없네..."  |

결과: C는 일을 다 했고, B도 받았는데, A는 이미 포기 -> 자원 낭비
```

### 6.3 Timeout 설계 공식

```
A의 read timeout > B의 read timeout + B의 자체 처리시간 + 네트워크 왕복 + 여유분
```

**구체적 예시:**

| 구간 | read timeout | 근거                              |
| ---- | ------------ | --------------------------------- |
| B->C | 5초          | C 최대 3초 + 여유                 |
| A->B | 10초         | B->C(5초) + B처리(1초) + 여유     |

> 비유: 나(A): "30분 안에 안 오면 취소" / 배달앱(B): "피자집, 20분 안에 만들어줘" / 피자집(C): 실제 15분 걸림. 30 > 20 > 15 -> 잘 동작!

### 6.4 역전 시 발생하는 문제들

| 문제             | 설명                                                |
| ---------------- | --------------------------------------------------- |
| **자원 낭비**    | C가 일을 다 했는데 결과를 아무도 안 씀              |
| **유령 요청**    | A는 포기했는데 B->C 작업은 계속 진행 중             |
| **불일치 상태**  | C에서 데이터가 변경됐는데 A는 에러로 인식           |
| **재시도 폭탄**  | A가 타임아웃으로 재시도 -> B->C에 중복 요청         |

---

## 핵심 정리

1. **`requests.Session()`을 사용해야** connection pool이 작동한다. 단순 `requests.get()`은 매번 새 연결을 만든다.
2. **Connection Pool의 연결 재사용은 HTTP Keep-Alive 덕분**이다. Keep-Alive가 "문을 열어두는 것"이고, Pool이 "열어둔 문을 관리하는 것".
3. **서버는 Keep-Alive timeout으로 idle 연결을 일방적으로 끊을 수 있다.** 클라이언트 Pool은 이를 바로 감지하지 못해 Stale Connection 문제가 발생한다.
4. **urllib3가 기본적으로 stale connection을 감지하고 자동 retry**한다. 더 세밀한 제어가 필요하면 `Retry` 정책을 명시한다.
5. **Keep-Alive timeout 설계**: 뒷단 서버의 keepalive를 앞단 프록시의 timeout보다 **길게** 설정해야 502를 방지한다.
6. **Read timeout 설계**: 체인 통신에서 앞단(호출자)의 timeout을 뒷단(피호출자)의 timeout보다 **길게** 설정해야 자원 낭비와 유령 요청을 방지한다.
