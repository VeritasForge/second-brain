---
tags: [redis, concurrency, system-design, lua-script, distributed-systems, high-availability]
created: 2026-04-14
---

# 선착순 쿠폰 발급 시스템 설계

## 문제 정의

| 항목         | 수치            | 의미                      |
| ------------ | --------------- | ------------------------- |
| 쿠폰 수     | 100개           | 극소량 한정 자원          |
| 동시 요청    | ~1,000만 건     | 초당 수백만 TPS           |
| 성공률       | 0.001%          | 99.999%는 실패 응답       |
| 시간 집중도  | 특정 시각 정각  | 트래픽 스파이크 극심      |
| 요구사항     | 고가용성        | HA 설계 필수              |

> 핵심: 대부분의 요청에게 "실패"를 **빠르고 안전하게** 알려주는 것이 설계의 핵심.

> **맥락 구분**: 소규모(1K TPS 이하)에서는 DB `SELECT FOR UPDATE SKIP LOCKED`만으로 충분. 아래 아키텍처는 **만 단위 이상 동시 요청**이 전제.

---

## 전체 아키텍처

```
                          ┌──────────────┐
                          │   CDN / WAF  │  ← 봇/DDoS 차단
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │   L4/L7 LB   │  ← 트래픽 분산
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │  API Gateway │  ← 인증, IP Rate Limit
                          └──────┬───────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
        ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐
        │  Coupon    │    │  Coupon    │    │  Coupon    │
        │  Server    │    │  Server    │    │  Server    │
        │ [로컬 플래그]│    │ [로컬 플래그]│    │ [로컬 플래그]│
        └─────┬─────┘    └─────┬─────┘    └─────┬─────┘
              └──────────────────┼──────────────────┘
                                 │
                          ┌──────▼───────┐
                          │    Redis     │  ← SETNX(Dedup) + INCR/Lua
                          │  (Sentinel)  │
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │   MySQL/PG   │  ← 동기 INSERT + UK 제약
                          └──────────────┘
```

### 구성 요소별 역할

#### WAF (Web Application Firewall)

HTTP 요청 내용(SQL Injection, 봇 패턴 등)을 검사하는 L7 방화벽. 일반 방화벽(L3/L4)은 IP/포트만 차단하지만, WAF는 요청 본문까지 검사.

#### LB와 API Gateway 역할 분리

| 구분         | Load Balancer              | API Gateway                    |
| ------------ | -------------------------- | ------------------------------ |
| **핵심**     | "어떤 서버로 보낼까?"      | "이 요청을 허용할까?"          |
| **기능**     | 헬스체크, 라운드로빈       | 인증, Rate Limit, 라우팅       |

Nginx, Kong, Envoy 등이 두 역할을 동시에 하기도 하지만, 개념적으로는 분리.

#### 다층 Rate Limiting

| 계층 | 위치        | 기준         | 목적                        |
| ---- | ----------- | ------------ | --------------------------- |
| L1   | WAF         | IP 기반      | 봇/DDoS 방어 (느슨: 100/s) |
| L2   | API Gateway | 글로벌       | 시스템 보호 (TPS 상한)      |
| L3   | 앱 레벨     | **userId**   | 동일 유저 중복 차단 (SETNX) |

> userId Rate Limit은 비즈니스 로직(1인 N개 등)에 따라 변하므로 API Gateway가 아닌 앱 레벨에서 처리.

#### 조기 차단 플래그

```java
// AtomicBoolean: Java 표준 (java.util.concurrent.atomic)
// CAS(Compare-And-Swap) CPU 명령어 기반, 멀티 스레드 안전
AtomicBoolean soldOutFlag = new AtomicBoolean(false);
```

- **안전장치가 아니라 성능 최적화**: 정합성은 Redis가 보장
- SOLD_OUT은 **false → true 단방향**이라 전파 지연이 무해
- 서버 재시작 시 Redis에서 플래그 상태 복원

로컬 캐시 옵션: `AtomicBoolean`(Java 표준, 최적) / `Caffeine`(별도 라이브러리, TTL 지원) / `ConcurrentHashMap`(Java 표준)

#### SETNX 기반 Dedup (중복 제거)

```
SETNX = "SET if Not eXists" — 키가 없을 때만 세팅 (존재 확인용, 락이 아님)
```

**SETNX ≠ RedLock:**

| 비교   | SETNX                      | RedLock                          |
| ------ | -------------------------- | -------------------------------- |
| 본질   | 단일 Redis 명령어          | 5개 Redis 인스턴스 분산 락       |
| 명령어 | `SET key val NX PX ttl`    | 동일 명령어를 5곳에 실행         |
| RTT    | 1회                        | 10회+ (획득 5 + 해제 5)          |
| 성능   | ~10만 TPS                  | ~1만 TPS                         |

> **RTT (Round-Trip Time)** = 요청을 보내고 응답을 받기까지의 왕복 시간.

**RedLock 알고리즘**: `SET key val NX PX 30000`을 5개 독립 인스턴스에 실행 → 과반수(3/5) 성공 + 경과시간 < TTL이면 획득.

#### 안전망 구조

```
1차: API Gateway → 인증 + IP Rate Limit (비즈니스 무관)
2차: SETNX Dedup → 동일 유저 중복 차단 (앱 레벨)
3차: DB UK 제약 → 최종 방어 (INSERT 시 자동 체크)
```

DB UK 제약이 SELECT FOR UPDATE보다 나은 이유: INSERT할 행이 아직 없으면 락을 걸 수 없음.

#### DB 스키마

```sql
CREATE TABLE coupon (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    event_id    VARCHAR(64) NOT NULL,
    user_id     BIGINT NOT NULL,
    coupon_code VARCHAR(32) NOT NULL,
    status      ENUM('ISSUED', 'USED', 'EXPIRED') DEFAULT 'ISSUED',
    issued_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_event_user (event_id, user_id)
);
```

**1인 N개 케이스**: UK 제약 제거, Redis `INCR coupon:user:{userId}:count`로 유저별 카운팅.

#### 고가용성 (HA)

| 계층           | 전략                                                  |
| -------------- | ----------------------------------------------------- |
| Server         | Stateless → K8s HPA 수평 확장, 이벤트 전 Pre-warming  |
| Redis          | Sentinel: Master 장애 시 Replica 자동 승격 (< 5초)    |
| Redis Fallback | 전체 장애 시 → DB 비관적 락으로 전환 (성능 저하 감수) |
| DB             | Primary-Replica 구성                                  |
| LB             | 다중 AZ 배치, 헬스체크 기반 자동 서버 제외            |

---

## Redis 내부 동작 원리

### I/O Multiplexing

**Multiplexing = 여러 개를 하나로 합치는 것** (통신 분야 유래)

하나의 스레드로 수만 개 소켓을 관리하는 기법. 소켓마다 별도 스레드를 만드는 대신, 이벤트 감시 시스템(epoll)이 "데이터 도착한 소켓"만 알려줌.

| 기술     | FD 제한  | 성능                       | 원리                                      |
| -------- | -------- | -------------------------- | ----------------------------------------- |
| `select` | 1,024개  | O(n)                       | 매번 전체 fd 비트마스크 순회              |
| `poll`   | 없음     | O(n)                       | 제한 해제, 여전히 전체 순회              |
| `epoll`  | 없음     | 전체 FD 스캔 불필요        | 커널 Red-Black Tree + ready list          |

> epoll_wait()는 엄밀히 O(k) (k = ready events). "O(1)"은 "전체 FD를 스캔하지 않는다"는 의미의 간소화 표현.

### Pipelining

클라이언트가 요청을 모아서 한 번에 보내고, 서버가 순서대로 처리한 결과를 버퍼에 쌓아서 TCP 패킷으로 한 번에 돌려보내는 것. 처리량 최대 **10배** 향상.

| 항목       | Pipelining     | MULTI/EXEC       | Lua Script            |
| ---------- | -------------- | ----------------- | --------------------- |
| 원자성     | ❌              | ✅                 | ✅                     |
| 조건 분기  | ❌              | ❌                 | ✅                     |
| 목적       | RTT 절감       | 원자적 실행 보장  | 읽기-판단-쓰기 원자적 |

---

## Architecture A: Redis INCR + Lua Script

### 핵심 — Lua Script 원자적 패턴

```lua
-- 실무 표준 패턴: 원자적 조건부 차감
local count = redis.call('INCR', KEYS[1])
if count > tonumber(ARGV[1]) then
    redis.call('DECR', KEYS[1])
    return -1  -- 거절 (카운터 원래대로)
end
return count  -- 성공
```

> Redis 공식: "Redis guarantees the script's atomic execution. While executing the script, all server activities are blocked."

### 코드

```java
public CouponResult tryIssueCoupon(Long userId) {
    if (soldOutFlag.get()) return CouponResult.SOLD_OUT;

    Boolean isNew = redis.setnx("coupon:dedup:" + userId, "1", Duration.ofMinutes(5));
    if (!isNew) return CouponResult.ALREADY_REQUESTED;

    Long count = evalLuaScript("coupon:count", 100);
    if (count == -1) { soldOutFlag.set(true); return CouponResult.SOLD_OUT; }

    try {
        couponRepository.save(new Coupon(eventId, userId, generateCode()));
        return CouponResult.SUCCESS;
    } catch (DuplicateKeyException e) {
        return CouponResult.ALREADY_ISSUED;
    } catch (Exception e) {
        redis.decr("coupon:count");  // 즉시 DECR (정산 배치 아님)
        return CouponResult.FAIL_RETRY;
    }
}
```

### DB 실패 시 — 즉시 DECR

이벤트 진행 중 정산 배치(30초 뒤)는 치명적 — 빈 슬롯이 있는데 "매진"으로 거절. 즉시 DECR이 실무 표준.

> **TOCTOU 주의**: Lua Script는 INCR 단계만 감싸고 DB 실패 후 DECR은 Lua 밖 별도 명령어. 이 사이에 다른 유저가 거절당하는 일시적 under-issue 발생 가능. 다만 **oversell은 아님** (Lua가 100 초과를 원자적으로 막으므로).

### 요청 흐름

```
10,000,000 요청
    ▼
[WAF]             ── 봇/DDoS 차단 ──────────► ~9,000,000 통과
    ▼
[LB]              ── 서버 분산 ─────────────► 통과
    ▼
[API Gateway]     ── 인증 + IP Rate Limit ──► ~5,000,000 통과
    ▼
[로컬 플래그]     ── 소진 후 즉시 차단 ──────► ~수백 건만 Redis 도달
    ▼
[Redis SETNX]     ── 유저 중복 제거 ─────────► 중복 제거
    ▼
[Redis Lua INCR]  ── 원자적 카운터 ──────────► 정확히 100건 성공
    ▼
[DB INSERT]       ── 동기 저장 + UK 안전망 ──► 100건 INSERT
                     (실패 시 즉시 DECR)
```

---

## Architecture B: Redis List 기반 쿠폰 풀

> **용어 주의**: Rate Limiting의 "Token Bucket" (HASH + 시간 기반 리필)과 다른 개념. 여기서는 **"Redis List 기반 쿠폰 풀"** 또는 **"재고 큐"**.

### 설계 원칙: "가역적 연산을 선택하라"

- **가역적**: LPOP + RPUSH (꺼냈다 돌려놓기 자연스러움)
- **비가역적**: INCR (DECR 가능하지만 사이에 다른 요청 끼어듦)

### 코드

```java
public CouponResult tryIssueCoupon(Long userId) {
    if (soldOutFlag.get()) return CouponResult.SOLD_OUT;

    String token = redis.lpop("coupon:bucket:" + eventId);
    if (token == null) { soldOutFlag.set(true); return CouponResult.SOLD_OUT; }

    Boolean isNew = redis.setnx("coupon:dedup:" + userId, token, Duration.ofMinutes(5));
    if (!isNew) {
        redis.rpush("coupon:bucket:" + eventId, token);
        return CouponResult.ALREADY_REQUESTED;
    }

    try {
        couponRepository.save(new Coupon(eventId, userId, token));
        return CouponResult.SUCCESS;
    } catch (DuplicateKeyException e) {
        return CouponResult.ALREADY_ISSUED;
    } catch (Exception e) {
        redis.rpush("coupon:bucket:" + eventId, token);
        redis.del("coupon:dedup:" + userId);
        return CouponResult.FAIL_RETRY;
    }
}
```

> **RPUSH 실패 시 토큰 영구 유실** — SAGA "보상 트랜잭션 자체의 실패" 문제.

### ACK 기반 개선

Redis `LMOVE` (구 `RPOPLPUSH`): token_list → processing_list 이동 → DB 성공 시 processing에서 제거 (ACK). 타임아웃 시 token_list로 복귀. 완전 구현하면 사실상 메시지 큐와 동일.

---

## DB 기반 대안: SELECT FOR UPDATE

### NOWAIT vs SKIP LOCKED

```sql
-- NOWAIT: 락 실패 시 즉시 에러 → 재시도 필요
SELECT * FROM coupon_stock WHERE event_id='X' FOR UPDATE NOWAIT;

-- SKIP LOCKED: 잠긴 행 건너뜀 → 재시도 불필요
SELECT id FROM coupon WHERE event_id='X' AND status='AVAILABLE'
LIMIT 1 FOR UPDATE SKIP LOCKED;
```

**SKIP LOCKED는 사실상 "DB 버전 쿠폰 풀"** — 100개를 개별 행으로 만들면 동시 100명 처리 가능.

**NOWAIT로 커넥션 풀 고갈은 방지 가능.** 진짜 문제는 1,000만 요청을 DB가 감당할 수 없다는 것:

```
Redis INCR: ~10μs → 초당 10만 건
DB FOR UPDATE: ~5ms → 초당 ~200건
```

---

## 종합 비교

| 평가 차원              | INCR (+Lua) | 쿠폰 풀 (List) | 근거                                    |
| ---------------------- | ----------- | -------------- | --------------------------------------- |
| 성능 (100개 규모)      | ★★★★        | ★★★★            | ~1ms 내 소진, 실질 동등                 |
| 원자성 경계            | ★★★★★       | ★★★             | Lua 내 TOCTOU 0, 밖 1 vs 3             |
| Safety (초과 방지)     | ★★★★★       | ★★★★            | Phantom Token 위험                      |
| Liveness (완전 발급)   | ★★★★        | ★★★             | 양쪽 모두 under-issue 가능              |
| 상태 관찰 가능성       | ★★★★★       | ★★              | GET 1개 vs in-flight 추적불가           |
| DB 실패 시 복구        | ★★★★        | ★★★★            | 즉시 DECR vs RPUSH (동등)               |
| 정산 배치 복잡도       | ★★★★★       | ★★★             | 카운터 비교 vs 리스트+키스캔            |
| 운영 복잡도            | ★★★★★       | ★★★             | 초기화/키관리/디버깅                    |
| 코드 단순성            | ★★★★★       | ★★★             | Lua 5줄 vs 다중 명령어                  |
| 채택 현황*             | ★★★★★       | ★★              | 대규모 선착순 프로덕션 사례             |

> *"채택 현황"은 기술적 우열이 아닌 **업계 채택률** 반영. 위 매트릭스는 운영 관점 비중이 높아 INCR에 유리한 프레임.

### 실무 사례

| 회사            | 패턴                           | 특이사항                                 |
| --------------- | ------------------------------ | ---------------------------------------- |
| 여기어때        | INCR + Kafka                   | Redis+Kafka 조합                         |
| 배민 (선착순)   | Counter                        | **교훈: 마스터만 참조** (리플리카 지연)   |
| 배민 (선물하기) | Set (SADD/SREM/SCARD)          | 유일한 비카운터 사례                     |
| 올리브영        | 이중 카운터 + RabbitMQ         | 초기 Pub/Sub → List → 최종 RabbitMQ 전환 |
| Alibaba         | Lua + Hash (HMGET+HINCRBY)     | 600K QPS                                 |

> 대규모 선착순 시나리오에서 INCR(카운터)이 업계 주류. List를 재고 카운팅 자체에 사용하는 대규모 프로덕션 사례는 미확인.

### Redis Failover 복구

두 방식 모두 **coupon table이 Source of Truth**:

```sql
SELECT COUNT(*) FROM coupon WHERE event_id = 'X'  -- 결과: 87개
-- INCR: SET coupon:count 87
-- 쿠폰 풀: 100-87=13개 토큰 재생성 후 RPUSH
```

---

## 핵심 정리

1. **INCR + Lua Script가 업계 표준**: 대규모 선착순 시나리오에서 카운터 기반이 주류.
2. **정산 배치는 이벤트 중 부적합**: Lua Script로 원자적 INCR+조건확인+DECR이 실무 표준.
3. **SELECT FOR UPDATE NOWAIT는 커넥션 풀 고갈 방지 가능**: 다만 만 단위 동시 요청은 DB가 감당 불가. 소규모(1K TPS 이하)에서는 SKIP LOCKED만으로 충분.
4. **Redis List 쿠폰 풀의 장점은 자연스러운 롤백**: RPUSH 반환이 직관적이지만, RPUSH 자체 실패(SAGA 보상 실패), 운영 복잡도가 약점.
5. **양쪽 모두 TOCTOU 존재**: INCR의 Lua 밖 DECR도, 쿠폰 풀의 LPOP→RPUSH 사이도 under-issue 방향 TOCTOU. oversell은 아님.
6. **Redis I/O Multiplexing(epoll)과 싱글 스레드가 10만 TPS의 핵심**: Pipelining으로 RTT 절감, 처리량 최대 10배 향상.
7. **Kafka는 후속 처리(알림, 포인트) 시 도입**: 100건 동기 INSERT에는 over-engineering.
