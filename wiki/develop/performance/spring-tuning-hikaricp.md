---
tags: [spring-boot, tomcat, hikaricp, connection-pool, tuning]
created: 2026-04-15
---

# Spring Boot 튜닝 — Tomcat, HikariCP, 커넥션 풀

---

## 1. Tomcat Thread Pool

### 1.1 Tomcat이란 — Python과 비교

```
Python:  Gunicorn(WSGI 서버) + FastAPI(프레임워크)  → 멀티프로세스
Kotlin:  Tomcat(서블릿 서버)  + Spring(프레임워크)   → 멀티스레드 (하나의 JVM 프로세스)
```

**하나의 JVM 프로세스 안에 Tomcat + Spring이 함께 돌아감.** `java -jar app.jar` 실행하면 Tomcat이 내장(embedded)되어 같이 뜸.

Gunicorn에서 `--workers 4 --threads 2`로 프로세스/스레드 수 설정하듯, Tomcat도 비슷:

```
Gunicorn:
  Worker Process 1 → Thread 1, Thread 2
  Worker Process 2 → Thread 1, Thread 2
  → 총 4개 스레드가 요청 처리

Tomcat:
  하나의 JVM 프로세스 안에서
  Thread Pool (기본 200개 스레드)
  → 요청 하나당 스레드 하나 배정
```

**차이점**: Gunicorn은 **멀티프로세스**(GIL 우회 목적), Tomcat은 **멀티스레드**(JVM은 GIL이 없으니까).

### 1.2 Tomcat 멀티프로세스 가능한가?

Tomcat 단독으로는 안 됨. JVM은 GIL이 없어서 멀티프로세스를 쓸 필요가 없음.

스케일아웃은 **K8s에서 Pod 복제**로 해결.

```
Gunicorn --workers 4    ≈    K8s replicas: 4 (Pod 4개, 각각 JVM+Tomcat)
```

### 1.3 설정

```yaml
server:
  tomcat:
    threads:
      max: 200        # 최대 스레드 (기본 200)
      min-spare: 10   # 유휴 시에도 유지할 최소 스레드
    max-connections: 8192  # 동시 TCP 연결 수 (기본 8192)
    accept-count: 100      # 스레드 전부 바쁠 때 대기 큐
```

### 1.4 스레드 수 산정

공식 (경험칙):

```
적정 스레드 수 = 동시 요청 수 × (1 + IO 대기시간 / CPU 처리시간)

예: 피크 13K RPM = 초당 ~217건
    평균 응답 100ms 중 CPU 10ms, IO 대기 90ms
    → 217 × (1 + 90/10) = 217 × 10 = ~2,170
    실제로는 200개면 충분 (모든 요청이 동시 도착하지 않으므로)
```

하지만 **실무에서는 Load Test로 피크의 3배를 처리할 수 있는 수준으로 설정**하는 것이 표준. 공식은 시작점일 뿐.

---

## 2. HikariCP — DB 커넥션 풀

### 2.1 HikariCP란 — Python과 비교

DB 연결을 매 요청마다 새로 만들면 비용이 크니까, 미리 여러 개 만들어놓고 빌려쓰는 것.

```
Python:  SQLAlchemy의 connection pool (pool_size, max_overflow)
Kotlin:  HikariCP (maximumPoolSize, minimumIdle)
```

```
                     HikariCP Pool
┌──────────────────────────────────────┐
│  Connection 1 ← Thread A가 사용 중   │
│  Connection 2 ← Thread B가 사용 중   │
│  Connection 3 (유휴, 대기 중)         │
│  Connection 4 (유휴, 대기 중)         │
│  Connection 5 (유휴, 대기 중)         │
└──────────────────────────────────────┘
  maximumPoolSize = 5 (최대 이만큼)
  minimumIdle = 3 (최소 이만큼은 유휴 유지)
```

### 2.2 max-connections, thread, HikariCP의 관계

```
                   ① 연결 수락        ② 요청 처리        ③ DB 접근
클라이언트 ──→  max-connections  ──→  thread pool   ──→  HikariCP pool  ──→  DB
                (8192)              (200)              (10~20)         (max 151)
                 넓다                보통               좁다!
```

모든 요청이 DB를 쓰지 않으므로 **max-connections >> threads >> HikariCP**가 정상.

### 2.3 커넥션 풀 사이즈 공식

**PostgreSQL 프로젝트 유래** (HikariCP wiki가 인용):

```
connections = (core_count × 2) + effective_spindle_count
```

이 공식은 **"DB 서버가 효율적으로 처리할 수 있는 동시 쿼리 총합"**. API 서버 한 대의 HikariCP 설정 공식이 **아님**.

```
core×2+spindle = 전체 시스템 관점 (DB가 감당할 수 있는 총합)
HikariCP 설정 = API 서버 한 대 관점 (이 서버가 가질 연결 수)
→ 다른 질문!
```

### 2.4 effective_spindle_count

**Spindle = HDD의 물리적 회전축.**

```
HDD 1개: 읽기 헤드가 물리적으로 이동 (seek time ~5-10ms)
         동시에 2곳을 읽을 수 없음 → 병렬 디스크 IO = 1

HDD 3개 (RAID): 3개의 헤드가 각각 독립적으로 이동
         동시에 3곳을 읽을 수 있음 → 병렬 디스크 IO = 3

SSD: 물리적 이동 없음 → spindle 개념 무의미 → 0~1로 취급
```

**SSD 시대에는 이 공식 자체가 HDD 시절 유물** → Load Test가 더 정확한 이유.

### 2.5 API 서버 10대일 때 DB는 어떻게 처리하나?

```
API 서버 10대 × HikariCP 10개 = DB에 총 100개 커넥션

DB 서버 (4코어):
  100개 커넥션이 연결되어 있지만
  동시에 쿼리 실행 중인 건 ~9개
  나머지 91개는 idle (연결만 유지)
  → TCP 연결 유지하되 쿼리 실행은 순서대로
```

### 2.6 DB 서버의 커넥션 관리

일반적으로 **커넥션 풀은 API 서버(HikariCP) 또는 중간 프록시(Pgbouncer)에서 관리**. DB는 max_connections까지 수락할 뿐.

예외: Oracle DRCP는 소켓 연결이 아닌 **"DB 내부 서버 프로세스"를 풀링**:

```
일반:    conn1 ↔ process1 (1:1, 영구 바인딩)
DRCP:    conn1 → [풀에서 아무 프로세스 빌림] → 쿼리 실행 → [반납]
```

### 2.7 API 서버 HikariCP 초기값 산정

**Step 1: 상한선 계산**

```
DB max_connections (예: 150) - 시스템 예약 (10) = 140
Pgbouncer 없으면: 서버당 상한 = 140 / API 서버 대수
Pgbouncer 있으면: API의 HikariCP는 Pgbouncer 기준
```

**Step 2: 초기값 경험칙**

| 상황                           | 초기값 | 근거                              |
| ------------------------------ | ------ | --------------------------------- |
| 소규모 (API 1~3대)            | 10~20  | DB max_connections에 여유 충분    |
| 중규모 (API 5~10대)           | 5~15   | 서버수 × pool ≤ max_connections   |
| 대규모 (API 10대+, Pgbouncer) | 5~10   | Pgbouncer가 다중화               |
| **공통 원칙**                  | **작게 시작** | HikariCP wiki "less is more" |

**Step 3: Load Test로 조정**

```
초기값 10으로 설정 후 Load Test:

관찰할 메트릭:
  hikaricp.connections.active     ← 사용 중
  hikaricp.connections.pending    ← 대기 (0 유지가 목표)
  P99 쿼리 응답시간

pending > 0 지속 → 풀 부족 → 증설
pending = 0 + idle 많음 → 풀 과다 → 줄여도 됨
```

HikariCP wiki 핵심: **큰 풀이 아니라 작은 풀이 오히려 성능이 좋다.**

```
비유:
  주방장 2명에 주문서 10장 깔아놓으면 왔다갔다 → 다 느려짐
  5장만 깔아놓으면 집중 처리 → 전체 회전율 높아짐
```

### 2.8 고정 풀 설정

공식 권장: **minimumIdle을 설정하지 말 것** (= maximumPoolSize와 동일한 고정 풀).

```
minimumIdle = maximumPoolSize = 10:
시작 시:     10개 생성
트래픽 많을 때: 10개 (고정)
트래픽 없을 때: 10개 (고정)
→ 생성/소멸 오버헤드 제로
```

### 2.9 모니터링

```yaml
spring:
  datasource:
    hikari:
      register-mbeans: true

management:
  endpoints:
    web:
      exposure:
        include: metrics
```

```
GET /actuator/metrics/hikaricp.connections.active    ← 사용 중
GET /actuator/metrics/hikaricp.connections.idle       ← 유휴
GET /actuator/metrics/hikaricp.connections.pending    ← 대기 (0 유지!)
GET /actuator/metrics/hikaricp.connections.max        ← 최대

사용률 = active / max × 100%
80% 이상이면 풀 증설 검토
pending > 0 지속이면 즉시 대응
```

pending = 커넥션 풀에서 커넥션을 기다리고 있는 스레드 수. connectionTimeout(기본 30초) 초과 시 예외.

### 2.10 Stale Connection 처리

```yaml
spring:
  datasource:
    hikari:
      max-lifetime: 1800000   # 30분 — 커넥션 나이 제한 (예방적 교체)
      keepalive-time: 0       # 기본 비활성. 활성화 시 Connection.isValid() 사용
```

- **max-lifetime**: 오래된 커넥션 폐기 후 새로 생성. DB wait_timeout보다 짧게.
- **keepalive-time**: 기본 0 (비활성). HikariCP 4.0+. 활성화 시 `Connection.isValid()` (JDBC4). `SELECT 1`이 아님.
- 함께 사용 권장: max-lifetime(예방적 교체) + keepalive-time(건강 체크)
