# Cross-cutting Staff Engineer — Interview Q&A

> 대상: FAANG L6/L7 (Staff/Principal Engineer)
> 총 문항: 39개 | 난이도: ⭐⭐⭐⭐⭐
> 특징: Python/Go/Kotlin 폴리글랏 비교 포함

## 목차

1. [System Design at Scale](#1-system-design-at-scale) — Q1~Q8
2. [Distributed Systems](#2-distributed-systems) — Q9~Q14
3. [Database Internals](#3-database-internals) — Q15~Q20
4. [Networking & Protocols](#4-networking--protocols) — Q21~Q25
5. [Observability & SRE](#5-observability--sre) — Q26~Q30
6. [Technical Leadership](#6-technical-leadership) — Q31~Q35
7. [Security Across Stacks](#7-security-across-stacks) — Q36~Q39

---


> FAANG L6/L7 Staff/Principal Engineer Level | 8 Questions
> Polyglot Focus: Python/FastAPI, Go, Kotlin/Spring

---

## Q1: Distributed Rate Limiter

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: System Design at Scale

**Question:** Design a distributed rate limiter that handles 100K+ RPS across multiple API gateway instances. Compare token bucket vs sliding window algorithms, and explain how you'd implement atomic operations using Redis Lua scripts. How do you handle clock skew and network partitions?

---

**🧒 12살 비유:**
놀이공원 입구에 직원이 여러 명 있다고 상상해봐. 각 직원이 "이 사람 오늘 몇 번 들어왔지?"를 따로 세면, 한 사람이 여러 입구를 돌아다니며 무제한 입장할 수 있어. 그래서 모든 직원이 하나의 공유 칠판(Redis)을 보면서 "이 사람 지금까지 몇 번 왔는지" 확인하는 거야. 칠판에 적는 것과 읽는 것을 한 번에 해야(Lua script) 두 직원이 동시에 봐도 숫자가 꼬이지 않아.

**📋 단계별 답변:**

**Step 1 — 맥락 & 평가 포인트**

면접관은 다음을 평가한다:
- 분산 환경에서의 동시성 제어 이해
- 알고리즘별 트레이드오프 분석 능력 (정확도 vs 메모리 vs 성능)
- Redis atomic operation과 Lua script의 필요성 인식
- Edge case 처리: clock skew, partition, failover

핵심 요구사항 정리:
```
Functional: per-user, per-IP, per-API key rate limiting
Non-functional: <1ms latency overhead, 100K+ RPS, multi-region
Scale: 10M+ unique keys, 50+ API gateway instances
```

**Step 2 — 핵심 설계**

```
                    ┌─────────────────────────────┐
                    │        Load Balancer         │
                    └──────┬──────┬──────┬─────────┘
                           │      │      │
                    ┌──────▼┐ ┌───▼───┐ ┌▼──────┐
                    │ GW-1  │ │ GW-2  │ │ GW-N  │  (API Gateways)
                    │       │ │       │ │       │
                    │ Local │ │ Local │ │ Local │  (L1: in-process cache)
                    │ Cache │ │ Cache │ │ Cache │
                    └───┬───┘ └───┬───┘ └───┬───┘
                        │         │         │
                    ┌───▼─────────▼─────────▼───┐
                    │     Redis Cluster          │  (L2: shared state)
                    │  ┌───────┐  ┌───────┐     │
                    │  │Shard 1│  │Shard N│     │
                    │  │Lua Scr│  │Lua Scr│     │
                    │  └───────┘  └───────┘     │
                    └───────────────────────────┘
```

**알고리즘 비교:**

| 속성 | Token Bucket | Sliding Window Log | Sliding Window Counter |
|------|-------------|-------------------|----------------------|
| 정확도 | 버스트 허용 | 정확 | 근사 (~0.1% 오차) |
| 메모리 | O(1) per key | O(N) per key | O(1) per key |
| Redis 연산 | GET/SET | ZADD + ZRANGEBYSCORE | HINCRBY + EXPIRE |
| 복잡도 | 낮음 | 높음 | 중간 |
| 추천 | 일반 API | 과금/결제 | 대부분의 경우 |

**Sliding Window Counter** 선택 근거: 메모리 효율과 정확도의 최적 밸런스. 100K RPS에서 Sliding Window Log는 Redis 메모리 폭발.

**Step 3 — 다양한 관점 (스케일별 차이)**

**Single Instance (1K RPS):**
- In-memory token bucket으로 충분
- `golang.org/x/time/rate` 또는 Python `limits` 라이브러리

**Multi-Instance (10K RPS):**
- Redis 중앙 집중, Lua script로 atomic 보장
- Local cache (100ms TTL)로 Redis 부하 감소

**Multi-Region (100K+ RPS):**
- 각 리전에 Redis cluster → 리전 간 비동기 sync
- "Approximate global rate limiting": 각 리전이 전체 할당량의 일부 보유
- 예: 전체 1000 req/min → US: 400, EU: 350, APAC: 250 (동적 조정)

**Clock Skew 대응:**
- Redis 서버 시간 기준 (`TIME` 명령어)으로 통일
- 클라이언트 타임스탬프 사용 금지
- NTP 동기화 + 모니터링

**Step 4 — 구체적 예시: Redis Lua Script**

```lua
-- sliding_window_counter.lua
-- KEYS[1] = rate limit key
-- ARGV[1] = window size (seconds)
-- ARGV[2] = max requests
-- ARGV[3] = current timestamp (from Redis TIME)

local key = KEYS[1]
local window = tonumber(ARGV[1])
local max_req = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local current_window = math.floor(now / window)
local prev_window = current_window - 1

local curr_key = key .. ":" .. current_window
local prev_key = key .. ":" .. prev_window

local curr_count = tonumber(redis.call('GET', curr_key) or "0")
local prev_count = tonumber(redis.call('GET', prev_key) or "0")

-- Weighted count: previous window의 남은 비율 반영
local elapsed = now - (current_window * window)
local weight = 1 - (elapsed / window)
local total = math.floor(prev_count * weight) + curr_count

if total >= max_req then
    return {0, total, max_req - total}  -- denied, current count, remaining
end

redis.call('INCR', curr_key)
redis.call('EXPIRE', curr_key, window * 2)

return {1, total + 1, max_req - total - 1}  -- allowed, current count, remaining
```

**Step 5 — 트레이드오프 & 대안**

| 관점 | Option A: Centralized Redis | Option B: Local + Sync | Option C: Cell-based |
|------|---------------------------|----------------------|---------------------|
| 정확도 | 높음 (exact) | 중간 (eventual) | 높음 (cell 내) |
| Latency | +1~3ms (Redis RTT) | +0ms (local) | +1ms (cell 내) |
| Partition 시 | Rate limit 해제 위험 | Local fallback 가능 | Cell 독립 동작 |
| 복잡도 | 낮음 | 중간 | 높음 |
| 추천 | 단일 리전 | 멀티 리전 | 초대규모 |

**Partition 시 전략:**
- **Fail-open**: Redis 불통 시 요청 허용 → 가용성 우선 (대부분의 API)
- **Fail-close**: Redis 불통 시 요청 차단 → 안전성 우선 (결제/인증)
- **Local fallback**: 로컬 카운터로 전환, 보수적 limit 적용

**Step 6 — Polyglot Implementation Notes**

| 관점 | Python/FastAPI | Go | Kotlin/Spring |
|------|---------------|-----|--------------|
| 미들웨어 패턴 | `@app.middleware("http")` 데코레이터. `slowapi` 라이브러리가 Redis 기반 rate limit 제공. async/await로 Redis 호출 non-blocking | `gin.HandlerFunc` 또는 gRPC interceptor. `go-redis`의 `Eval`로 Lua 실행. goroutine 기반이라 blocking Redis 호출도 효율적 | `HandlerInterceptor` 또는 Spring Cloud Gateway `RequestRateLimiter` 필터. `Bucket4j` + Redis (Redisson) 조합이 사실상 표준 |
| Local Cache | `cachetools.TTLCache` (GIL로 thread-safe) | `sync.Map` 또는 `groupcache`. lock-free 구조 가능 | `Caffeine` cache. `LoadingCache`로 자동 갱신 |
| 동시성 모델 | asyncio 이벤트 루프. 단일 프로세스에서는 GIL이 오히려 race condition 방지. 멀티 프로세스 시 Redis 필수 | goroutine + channel. `sync/atomic`으로 로컬 카운터 lock-free 구현 가능 | Coroutine + `AtomicLong`. Virtual Thread (Loom) 시 blocking Redis client도 OK |
| Redis 클라이언트 | `redis.asyncio` (aioredis 후속). Pipeline/Lua 지원 | `go-redis/v9`. Context 기반 timeout 우수 | `Lettuce` (비동기, Netty 기반) 또는 `Redisson` (분산 객체 추상화) |
| 배포 특이점 | Gunicorn worker 수 × rate = 실질 rate. worker 간 공유 불가하므로 Redis 필수 | 단일 바이너리, goroutine이 커넥션 풀 공유. 가장 효율적 | Reactive Stack(`WebFlux`) 시 Lettuce 필수. Servlet Stack 시 Jedis도 가능 |

**🎯 면접관 평가 기준:**

- **L6 PASS**: Token bucket vs sliding window 비교, Redis Lua로 atomic 보장, local cache + Redis 2-tier 설계
- **L7 EXCEED**: Multi-region approximate rate limiting, cell-based architecture, partition 시 fail-open/close 전략 구분, clock skew 해법 (Redis TIME 기준)
- **🚩 RED FLAG**: "각 서버에서 로컬로 카운트하면 됩니다" (분산 환경 미고려), Lua script 필요성 모름, race condition 설명 불가

---

## Q2: Distributed Cache

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: System Design at Scale

**Question:** Design a distributed caching layer for a social media platform serving 500M DAU. Address consistent hashing for shard distribution, cache stampede prevention, and compare write-through vs write-behind strategies. How do you handle cache coherence across data centers?

---

**🧒 12살 비유:**
도서관에 인기 있는 책이 있는데, 매번 창고(DB)에서 가져오면 느려. 그래서 카운터 앞에 자주 찾는 책 복사본을 놓아두는 거야(캐시). 근데 문제가 있어: 1) 복사본을 어느 선반에 놓을지(consistent hashing), 2) 100명이 동시에 같은 책을 달라고 하면(stampede), 3) 원본이 수정되면 복사본도 바꿔야 하는데(invalidation). 분관이 여러 곳이면 더 복잡해져(multi-DC).

**📋 단계별 답변:**

**Step 1 — 맥락 & 평가 포인트**

면접관이 보는 것:
- Consistent hashing과 가상 노드(vnode)의 이해
- Cache stampede / thundering herd 문제 인식과 해결
- Write 전략의 데이터 일관성 vs 성능 트레이드오프
- Multi-DC cache coherence 설계

```
Scale: 500M DAU, ~50K RPS read, ~5K RPS write
Data: User profiles, feeds, relationships
SLA: p99 read <5ms, cache hit ratio >95%
```

**Step 2 — 핵심 설계**

```
Client Request
      │
      ▼
┌──────────┐
│ App Server│
└─────┬────┘
      │
      ▼
┌──────────────────────────────────────────┐
│           Cache Layer (L1 + L2)          │
│                                          │
│  ┌─────────┐   Miss   ┌──────────────┐  │
│  │L1: Local│ ──────── │L2: Redis     │  │
│  │ (per    │          │  Cluster     │  │
│  │ process)│ ◄─────── │  (shared)    │  │
│  │ 10s TTL │   Fill   │  5min TTL    │  │
│  └─────────┘          └──────┬───────┘  │
│                              │ Miss     │
└──────────────────────────────┼──────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │    Database      │
                    │  (Source of      │
                    │   Truth)         │
                    └──────────────────┘
```

**Consistent Hashing with Virtual Nodes:**

```
Hash Ring (0 ~ 2^32)
     ┌────────────────────────────┐
     │    VN-A1   VN-B1   VN-C1  │
     │   ╱          │        ╲   │
     │  ╱     VN-A2 │ VN-B2   ╲  │
     │ Node-A       │      Node-C│
     │        Node-B             │
     │  VN-C2   VN-A3   VN-B3   │
     └────────────────────────────┘

Key → hash(key) → 시계방향 첫 vnode → 물리 노드
Virtual nodes per physical: 150~200 (균등 분포)
```

노드 추가/제거 시 전체 키의 1/N만 재배치.

**Step 3 — 다양한 관점**

**Cache Stampede 방지 (3가지 전략):**

| 전략 | 원리 | 장점 | 단점 |
|------|------|------|------|
| **Mutex/Lock** | 첫 요청만 DB 조회, 나머지 대기 | 정확, DB 보호 | 대기 latency |
| **Stale-while-revalidate** | 만료 데이터 반환 + 비동기 갱신 | 0 latency | 잠깐 stale data |
| **Probabilistic early expiry** | TTL 전에 확률적으로 갱신 | 자연스러운 분산 | 구현 복잡 |

**Stampede 방어 — Mutex 패턴 의사코드:**
```
func get(key):
    value = cache.get(key)
    if value != null:
        return value

    lock_key = "lock:" + key
    if cache.setnx(lock_key, 1, ttl=5s):   # 락 획득
        value = db.query(key)
        cache.set(key, value, ttl=300s)
        cache.del(lock_key)
        return value
    else:
        sleep(50ms)                          # 락 대기
        return get(key)                      # 재시도
```

**Write 전략 비교:**

| 전략 | 동작 | 일관성 | 성능 | 위험 |
|------|------|--------|------|------|
| **Write-Through** | 캐시+DB 동시 쓰기 | 강함 | 쓰기 느림 (2x) | 쓰기 latency |
| **Write-Behind** | 캐시 먼저, DB 비동기 | 약함 | 쓰기 빠름 | 데이터 손실 가능 |
| **Write-Around** | DB만 쓰기, 캐시 무효화 | 중간 | 쓰기 빠름 | 다음 읽기 miss |
| **Cache-Aside** | 앱이 캐시+DB 직접 관리 | 중간 | 유연 | 코드 복잡 |

추천: **Cache-Aside + Write-Around** (읽기 heavy 시스템), **Write-Behind** (쓰기 heavy + 손실 허용)

**Step 4 — 구체적 예시: Multi-DC Cache Coherence**

```
        DC-West                          DC-East
   ┌──────────────┐               ┌──────────────┐
   │ Redis Cluster│◄── Pub/Sub ──►│ Redis Cluster│
   │  (Primary)   │   (async)     │  (Replica)   │
   └──────┬───────┘               └──────┬───────┘
          │                               │
   ┌──────▼───────┐               ┌──────▼───────┐
   │   MySQL      │◄── binlog ───►│   MySQL      │
   │  (Primary)   │   replication │  (Read       │
   │              │               │   Replica)   │
   └──────────────┘               └──────────────┘
```

**Cache Invalidation 전략 (Multi-DC):**
```
1. Write 발생 (DC-West)
2. DB 업데이트 + 로컬 캐시 무효화
3. Invalidation 메시지 발행 (Kafka/Redis Pub-Sub)
4. DC-East 수신 → 로컬 캐시 무효화
5. 다음 읽기 시 Read Replica에서 조회 → 캐시 채움

문제: replication lag (100~500ms)
해법: write 후 같은 DC에서 읽기 보장 (sticky routing)
      또는 invalidation 메시지에 version 포함 → stale 버전 거부
```

**Step 5 — 트레이드오프 & 대안**

| 관점 | Redis Cluster | Memcached | Application-level (Caffeine/Ristretto) |
|------|--------------|-----------|---------------------------------------|
| 데이터 구조 | Rich (hash, sorted set) | Key-Value only | Key-Value only |
| 복제 | 내장 (Primary-Replica) | 없음 (client sharding) | 없음 (local only) |
| 메모리 효율 | 중간 (overhead 있음) | 높음 (slab allocator) | 매우 높음 |
| 지속성 | RDB/AOF 선택 | 없음 | 없음 |
| Multi-thread | 6.0+ I/O threading | Multi-threaded | In-process |
| 추천 | 범용, 풍부한 기능 | 단순 KV, 극한 성능 | L1 local cache |

**Step 6 — Polyglot Implementation Notes**

| 관점 | Python/FastAPI | Go | Kotlin/Spring |
|------|---------------|-----|--------------|
| L1 Local Cache | `cachetools.TTLCache` 또는 `functools.lru_cache`. GIL 덕에 thread-safe하지만 멀티 프로세스 시 각 worker 독립 캐시 | `github.com/dgraph-io/ristretto` (admission policy + TinyLFU). goroutine-safe, 매우 높은 처리량 | `com.github.benmanes.caffeine` — JVM 최고의 캐시. `Window-TinyLFU` eviction, 비동기 갱신 지원 |
| L2 Redis Client | `redis.asyncio` (async) + `redis-py-cluster`. `Pipeline`으로 배치 호출 | `go-redis/v9` — context 기반, cluster mode 내장, `Pipeliner` 인터페이스 | `Lettuce` (Netty 비동기) — Spring `@Cacheable` + `RedisCacheManager`. Reactive에서 `ReactiveRedisTemplate` |
| Cache Stampede 방어 | `aiocache`의 `@cached(lock=True)` 데코레이터. `redis.asyncio` SETNX로 분산 락 | `singleflight` 패키지 (표준 라이브러리!). 같은 키 요청을 자동으로 하나로 합침 — Go의 킬러 기능 | `Caffeine.asyncReloading()` + `@Cacheable(sync=true)`. Spring의 `sync=true`가 JVM 레벨 mutex 제공 |
| Serialization | `msgpack` 또는 `orjson` (JSON 대비 3-5x 빠름). Pydantic model → bytes 변환 | `encoding/json` 또는 `protobuf`. struct tag 기반 자동 직렬화 | `Kryo` (바이너리, 가장 빠름) 또는 `Jackson` + `Smile` (바이너리 JSON). `GenericJackson2JsonRedisSerializer` 기본 제공 |
| 모니터링 | `prometheus_client` + Redis `INFO` 명령. hit/miss ratio를 미들웨어에서 추적 | `prometheus/client_golang` + `go-redis` 내장 hook. OpenTelemetry span 자동 생성 | Micrometer + `spring-boot-actuator`. `cache.gets`, `cache.puts`, `cache.evictions` 자동 메트릭 |

**🎯 면접관 평가 기준:**

- **L6 PASS**: Consistent hashing + vnode, cache-aside 패턴, TTL 기반 invalidation, stampede 인식
- **L7 EXCEED**: Multi-DC coherence 전략, write-behind의 데이터 손실 위험과 WAL 보호, singleflight/probabilistic early refresh, version-based invalidation
- **🚩 RED FLAG**: "TTL 설정하면 됩니다" (invalidation 전략 없음), consistent hashing 필요성 모름, stampede 문제 인식 못함

---

## Q3: URL Shortener at Scale

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: System Design at Scale

**Question:** Design a URL shortening service handling 1B+ shortened URLs with 100:1 read-to-write ratio. How do you generate globally unique short codes without coordination? Discuss Base62 encoding, distributed ID generation, and read-heavy optimization strategies.

---

**🧒 12살 비유:**
아주 긴 주소를 짧은 별명으로 바꾸는 서비스야. "서울시 강남구 테헤란로 123번지 4층 501호"를 "강남-A7"이라고 부르는 것처럼. 문제는: 1) 전 세계에서 동시에 별명을 만들 때 같은 별명이 겹치면 안 돼(ID 생성), 2) 별명으로 주소 찾는 게 100배 더 많아서 찾기를 엄청 빠르게 해야 해(read 최적화), 3) 별명은 가능한 짧아야 해(Base62).

**📋 단계별 답변:**

**Step 1 — 맥락 & 평가 포인트**

```
Write: 10M URLs/day (~116 RPS)
Read:  1B reads/day (~11,600 RPS), peaks 50K RPS
Storage: 1B URLs × 1KB avg = 1TB
Short code length: 7 chars (62^7 = 3.5 trillion combinations)
```

평가 포인트:
- 분산 ID 생성 전략 (coordination-free)
- Base62 인코딩과 short code 길이 계산
- Read-heavy 최적화 (캐싱, CDN, DB 파티셔닝)
- 만료/삭제, analytics, abuse 방지

**Step 2 — 핵심 설계**

```
┌──────────┐     ┌───────────────────────────────────────────┐
│  Client  │────►│            API Gateway / LB               │
└──────────┘     └───┬──────────┬──────────┬────────────────┘
                     │          │          │
              ┌──────▼───┐ ┌───▼────┐ ┌───▼────┐
              │ Write    │ │ Read   │ │ Read   │
              │ Service  │ │Service │ │Service │
              │ (少)     │ │ (多)   │ │ (多)   │
              └────┬─────┘ └───┬────┘ └───┬────┘
                   │           │          │
              ┌────▼─────┐ ┌──▼──────────▼──┐
              │ ID Gen   │ │   Redis Cache   │
              │ Service  │ │  (Hot URLs)     │
              │ (Snowflk)│ │  Hit ratio >90% │
              └────┬─────┘ └────────┬────────┘
                   │                │ Miss
              ┌────▼────────────────▼────────┐
              │      Database Cluster        │
              │  ┌─────────┐  ┌──────────┐   │
              │  │ Primary │  │ Replicas │   │
              │  │ (Write) │  │ (Read)   │   │
              │  └─────────┘  └──────────┘   │
              └──────────────────────────────┘
```

**분산 ID 생성 전략 비교:**

| 전략 | 원리 | 장점 | 단점 |
|------|------|------|------|
| **Auto-increment** | DB sequence | 단순 | 단일 장애점, 병목 |
| **UUID** | 랜덤 128-bit | Coordination-free | 너무 김 (22 Base62) |
| **Snowflake** | timestamp + worker + seq | 정렬 가능, 고유 | 시간 의존, worker ID 관리 |
| **KSUID** | timestamp + random | 정렬 가능, 단순 | Snowflake보다 긴 ID |
| **Pre-generated range** | 미리 범위 할당 | 매우 빠름 | 범위 관리 복잡 |
| **Hash (MD5/SHA)** | URL 해시 후 잘라냄 | Deterministic | 충돌 처리 필요 |

**추천: Snowflake 변형 (48-bit)**

```
┌─────────────────────────────────────────────────┐
│          48-bit Custom Snowflake ID              │
├────────────────┬──────────┬─────────────────────┤
│  32-bit        │ 6-bit    │ 10-bit              │
│  Timestamp     │ Worker   │ Sequence            │
│  (seconds)     │ ID       │ (per-second)        │
│  ~136 years    │ 64 nodes │ 1024/sec/node       │
└────────────────┴──────────┴─────────────────────┘

48-bit → Base62 → 8 chars (충분히 짧음)
```

**Base62 인코딩:**
```
Alphabet: [0-9a-zA-Z]  (62 characters)
7 chars: 62^7 = 3,521,614,606,208 (~3.5T combinations)
8 chars: 62^8 = 218,340,105,584,896 (~218T combinations)

encode(12345678) → "dnh6"
decode("dnh6")   → 12345678
```

**Step 3 — 다양한 관점**

**Read-Heavy 최적화 (100:1 ratio):**

```
Layer 1: Browser Cache
  → HTTP 301 (permanent) vs 302 (temporary)
  → 301 = 브라우저 캐싱 (analytics 손실)
  → 302 = 매번 서버 경유 (analytics 가능) ← 추천

Layer 2: CDN (CloudFront/Fastly)
  → Edge에서 리다이렉트 응답 캐싱
  → TTL: 1시간 (변경 가능성 고려)

Layer 3: Redis Cache
  → Hot URLs (Pareto: 20% URLs = 80% traffic)
  → LRU eviction, TTL 24h
  → Expected hit ratio: 90%+

Layer 4: DB Read Replicas
  → 3-5 replicas for read scaling
  → short_code에 B-tree index → O(log N) lookup
```

**DB 스키마 & 파티셔닝:**
```sql
CREATE TABLE urls (
    short_code  CHAR(8) PRIMARY KEY,    -- Base62 encoded
    long_url    TEXT NOT NULL,
    user_id     BIGINT,
    created_at  TIMESTAMP DEFAULT NOW(),
    expires_at  TIMESTAMP,
    click_count BIGINT DEFAULT 0
) PARTITION BY HASH(short_code);        -- 균등 분포
-- 16~64 partitions across shards
```

**Step 4 — 구체적 예시: 전체 쓰기/읽기 흐름**

**Write Flow:**
```
1. POST /api/v1/urls  {long_url: "https://example.com/very/long/path"}
2. ID Generator → Snowflake ID (예: 283749182)
3. Base62 encode → "dR4x2"
4. Check collision (VERY rare with Snowflake) → DB INSERT
5. Cache에 저장: SET "dR4x2" → "https://example.com/very/long/path"
6. Return: {"short_url": "https://sho.rt/dR4x2"}
```

**Read Flow:**
```
1. GET https://sho.rt/dR4x2
2. CDN cache? → HIT → 302 redirect (done)
3. Redis cache? → HIT → 302 redirect (done)
4. DB lookup (read replica) → 302 redirect
5. Async: update cache, increment click_count (batch)
```

**Analytics 분리:**
```
Click event → Kafka → Analytics Service → ClickHouse/BigQuery
(비동기, 메인 리다이렉트 latency에 영향 없음)
```

**Step 5 — 트레이드오프 & 대안**

| 관점 | Counter-based ID | Hash-based | Pre-allocated Range |
|------|-----------------|------------|-------------------|
| 충돌 | 불가능 | 가능 (처리 필요) | 불가능 |
| 예측 가능성 | 순차적 → 보안 위험 | 랜덤 | 범위 내 순차 |
| Coordination | Worker ID 등록 | 없음 | 범위 할당 시 |
| Custom alias | 별도 처리 | 자연스러움 | 별도 처리 |
| 추천 | 일반적 (+ randomize) | 단순 MVP | 초대규모 |

**Custom Alias 지원:**
```
POST /api/v1/urls {long_url: "...", custom_alias: "my-brand"}
→ custom_alias 유일성 검사 (DB unique constraint)
→ 예약어 필터 (profanity, system paths)
```

**Step 6 — Polyglot Implementation Notes**

| 관점 | Python/FastAPI | Go | Kotlin/Spring |
|------|---------------|-----|--------------|
| Base62 구현 | 순수 Python으로 구현 쉬움. `short_url` 라이브러리 존재하나 직접 구현 추천 (20줄). `divmod` 루프 | `math/big` 또는 직접 구현. `strings.Builder`로 효율적 문자열 생성. 표준 라이브러리만으로 충분 | `BigInteger.toString(62)` 없으므로 직접 구현. `StringBuilder` + `tailrec` 재귀로 깔끔하게 |
| ID Generator | `snowflake-id` 또는 직접 구현. GIL이 sequence 부분의 동시성 보호. `time.time_ns()` 사용 | `bwmarrin/snowflake` 라이브러리 성숙. `sync/atomic`으로 sequence 관리. 네이티브 성능으로 단일 노드 100K+ ID/sec | `com.twitter.snowflake` 포크 또는 직접 구현. `AtomicLong`으로 sequence. Spring의 `@Singleton`으로 worker ID 관리 |
| Read 최적화 | `@app.get("/{code}")` + `RedirectResponse(status_code=302)`. `orjson` 직렬화. Uvicorn worker 수로 수평 확장 | `http.Redirect(w, r, url, 302)` — 가장 빠름. 단일 바이너리 50K+ RPS 가능. `net/http` 기본 서버로 충분 | `ResponseEntity.status(302).location(URI(url)).build()`. WebFlux 사용 시 리다이렉트도 non-blocking |
| DB 접근 | `asyncpg` (PostgreSQL async driver). SQLAlchemy 2.0 async. 커넥션 풀 관리 주의 | `pgx` (pure Go PostgreSQL driver). `database/sql` + 커넥션 풀 내장. 가장 세밀한 제어 가능 | Spring Data JPA 또는 R2DBC (reactive). `@Repository` 추상화 편리하나 N+1 주의 |
| 처리량 비교 | 단일 인스턴스 ~5K RPS (uvicorn). CPU-bound 작업 없어서 충분 | 단일 인스턴스 ~50K RPS. 리다이렉트 전용이라면 Go가 가장 효율적 | 단일 인스턴스 ~20K RPS (WebFlux). Servlet은 ~10K RPS |

**🎯 면접관 평가 기준:**

- **L6 PASS**: Base62 인코딩 원리, Snowflake ID, Cache + DB read replica, 301 vs 302 차이
- **L7 EXCEED**: Custom Snowflake 비트 설계, pre-allocated range의 장단점, analytics 분리 아키텍처, abuse 방지 (rate limit, captcha, blacklist), hot key 처리
- **🚩 RED FLAG**: "UUID를 그대로 short URL로" (너무 김), auto-increment를 분산 환경에서 그대로 사용, read-heavy 최적화 없이 모든 요청 DB 조회

---

## Q4: Real-time Notification System

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: System Design at Scale

**Question:** Design a real-time notification system that delivers push notifications, in-app alerts, and email to 100M+ users with sub-second latency. Compare WebSocket vs SSE vs Long Polling for persistent connections. How do you handle 1M+ concurrent connections and ensure delivery guarantees?

---

**🧒 12살 비유:**
친구한테 소식을 전하는 방법이 세 가지야: 1) 전화 연결을 계속 유지하면서 양쪽이 말하기(WebSocket) — 가장 빠르지만 전화비가 비싸, 2) 라디오처럼 한쪽만 계속 보내기(SSE) — 간단하지만 답장은 못 해, 3) "소식 있어?" 하고 계속 물어보기(Long Polling) — 쉽지만 낭비가 심해. 100만 명에게 동시에 전화를 연결하려면 특별한 방법이 필요해.

**📋 단계별 답변:**

**Step 1 — 맥락 & 평가 포인트**

```
Users: 100M+ registered, 10M+ concurrent online
Channels: Push (mobile), In-app (WebSocket), Email, SMS
Latency: <1s for in-app, <5s for push, best-effort for email
Volume: 1B+ notifications/day
Concurrent connections: 1M+ WebSocket connections
```

평가 포인트:
- 커넥션 관리 전략 (C10K/C1M problem)
- 전송 채널별 적합한 프로토콜 선택
- 메시지 전달 보장 (at-least-once)
- Fan-out 전략 (1:1 vs 1:N)

**Step 2 — 핵심 설계**

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Service A   │  │ Service B   │  │ Service C   │
│ (Order)     │  │ (Social)    │  │ (System)    │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       ▼                ▼                ▼
┌──────────────────────────────────────────────┐
│              Kafka / Message Bus             │
│          (notification.events topic)         │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│         Notification Service                 │
│  ┌───────────┐  ┌────────────┐  ┌─────────┐ │
│  │ Router    │  │ Template   │  │ Priority│ │
│  │ (channel  │  │ Engine     │  │ & Rate  │ │
│  │  select)  │  │            │  │ Control │ │
│  └─────┬─────┘  └────────────┘  └─────────┘ │
└────────┼─────────────────────────────────────┘
         │
    ┌────┼──────────┬──────────────┐
    │    │          │              │
    ▼    ▼          ▼              ▼
┌──────┐ ┌──────┐ ┌──────┐  ┌─────────┐
│WebSkt│ │ Push │ │Email │  │   SMS   │
│Server│ │(APNs/│ │(SES/ │  │(Twilio) │
│      │ │ FCM) │ │SGrid)│  │         │
└──┬───┘ └──────┘ └──────┘  └─────────┘
   │
   ▼ (1M+ connections)
┌────────────────────────────────┐
│  Connection Manager Cluster   │
│  ┌──────┐ ┌──────┐ ┌──────┐  │
│  │Node 1│ │Node 2│ │Node N│  │
│  │ 50K  │ │ 50K  │ │ 50K  │  │
│  │conns │ │conns │ │conns │  │
│  └──────┘ └──────┘ └──────┘  │
└────────────────────────────────┘
```

**프로토콜 비교:**

| 속성 | WebSocket | SSE (Server-Sent Events) | Long Polling |
|------|-----------|-------------------------|-------------|
| 방향 | 양방향 (Full-duplex) | 단방향 (Server→Client) | 단방향 (시뮬레이션) |
| 프로토콜 | ws:// / wss:// | HTTP/1.1 | HTTP/1.1 |
| 재연결 | 수동 구현 | 자동 (EventSource API) | 매 요청 새 연결 |
| 프록시/LB | 특별 설정 필요 | HTTP 호환 | HTTP 호환 |
| 브라우저 | 전체 지원 | IE 미지원 | 전체 지원 |
| 서버 자원 | 커넥션당 메모리 | 커넥션당 메모리 | 요청당 스레드 |
| 추천 | 채팅, 게임 | 알림, 피드 | 폴백 |

**결정: In-app 알림 → SSE (단방향 충분), 채팅 → WebSocket**

**Step 3 — 다양한 관점**

**C1M Problem (100만 동시 커넥션):**

```
1M connections ÷ 50K per node = 20 nodes minimum

Per-connection memory:
  - TCP buffer: ~4KB (read) + ~4KB (write) = ~8KB
  - Application state: ~2KB
  - Total: ~10KB per connection
  - 50K connections = ~500MB per node

Node spec: 4 CPU cores, 4GB RAM, 높은 파일 디스크립터 제한
OS tuning: ulimit -n 100000, net.core.somaxconn=65535
```

**Connection Registry (누가 어디에 연결되어 있는지):**
```
Redis:
  user:12345:connection → {"node": "ws-node-3", "connected_at": "..."}

알림 전송 시:
  1. user_id → Redis에서 연결된 node 조회
  2. 해당 node에 메시지 전달 (내부 gRPC 또는 Redis Pub/Sub)
  3. node가 해당 user의 WebSocket/SSE에 push
```

**Offline 사용자 처리:**
```
1. 연결 없음 → Push notification (APNs/FCM)
2. Push도 실패 → Notification inbox (DB 저장)
3. 사용자 재접속 시 → inbox에서 미읽음 알림 조회
4. 이메일 → 별도 큐, 배치 처리 (digest)
```

**Step 4 — 구체적 예시: 전달 보장 메커니즘**

```
┌─────────────────────────────────────┐
│       Delivery State Machine        │
│                                     │
│  CREATED → QUEUED → SENT → DELIVERED│
│              │         │            │
│              ▼         ▼            │
│           FAILED    EXPIRED         │
│              │                      │
│              ▼                      │
│            DLQ                      │
└─────────────────────────────────────┘
```

**At-least-once 전달:**
```
1. Notification 생성 → DB에 status=CREATED 저장
2. Kafka에 발행 → status=QUEUED
3. Consumer가 처리 → status=SENT
4. Client ACK 수신 → status=DELIVERED
5. ACK 미수신 (30s timeout) → 재전송 (max 3회)
6. 최종 실패 → status=FAILED, DLQ

클라이언트 중복 처리:
  - notification_id 기반 dedup
  - 이미 표시된 알림은 무시
```

**Fan-out 전략 (1:N 알림, 예: "좋아요"):**
```
Small fan-out (< 1000 recipients):
  → 즉시 각 사용자에게 개별 전송

Large fan-out (> 1000, 예: 셀럽 포스트):
  → Fan-out on read: 알림 목록 조회 시 동적으로 구성
  → 또는 Background worker가 batch로 분배 (5분 지연 허용)
```

**Step 5 — 트레이드오프 & 대안**

| 관점 | Push Model (서버 발신) | Pull Model (클라이언트 조회) | Hybrid |
|------|----------------------|--------------------------|--------|
| Latency | <1s | Polling 간격에 의존 | <1s for online |
| 서버 부하 | 커넥션 유지 비용 | 빈 응답 낭비 | 최적화 가능 |
| Offline | Push/inbox 필요 | 자연스러움 | Push + inbox |
| 복잡도 | 높음 (연결 관리) | 낮음 | 중간 |
| Battery | 효율적 (대기만) | 비효율 (반복 요청) | 효율적 |

**Step 6 — Polyglot Implementation Notes**

| 관점 | Python/FastAPI | Go | Kotlin/Spring |
|------|---------------|-----|--------------|
| WebSocket | `fastapi.WebSocket` + Starlette 내장. `websockets` 라이브러리. async/await 기반이지만 단일 프로세스 커넥션 제한 (~10K) | `gorilla/websocket` 또는 `nhooyr/websocket`. goroutine per connection — 50K+ 커넥션/노드 자연스러움. 메모리 효율 최고 | Spring WebFlux `WebSocketHandler` + Reactor Netty. 또는 Spring WebSocket (Servlet). Kotlin coroutine과 자연스러운 통합 |
| SSE | `StreamingResponse` + `async def event_generator()`. 간결하지만 Gunicorn worker 수 = max 동시 SSE | `http.Flusher` 인터페이스. `w.(http.Flusher).Flush()` 호출. HTTP/2 multiplexing과 자연스러운 조합 | `Flux<ServerSentEvent>` 반환. WebFlux에서 매우 자연스러움. `Sinks.Many`로 브로드캐스트 |
| 동시 연결 수 | 단일 프로세스 ~10K (asyncio). 멀티 프로세스 시 각각 독립. 총 ~50K/노드 (5 workers) | 단일 프로세스 ~100K (goroutine 경량). C1M 가능한 유일한 선택지. `epoll` 직접 사용 가능 | WebFlux: ~50K/노드 (Netty event loop). Servlet: ~5K (스레드 풀 제한). Virtual Thread: ~30K |
| 내부 메시징 | Redis Pub/Sub (`aioredis`). 노드 간 알림 전파. 또는 Kafka consumer group | Redis Pub/Sub 또는 NATS (Go 네이티브, 초경량). gRPC streaming으로 노드 간 통신 | Redis Pub/Sub (`ReactiveRedisTemplate.listenTo`). Spring Cloud Stream + Kafka. Spring Integration |
| 프로덕션 고려 | PyPy 사용 시 2-3x 성능 향상. CPU-bound 없어서 Python도 충분. 하지만 C1M은 Go에 위임 추천 | 알림 시스템의 커넥션 관리 레이어는 Go가 압도적. Uber, Discord 등 실제 사례 | Kotlin coroutine + WebFlux로 우아한 코드. 하지만 JVM 메모리 오버헤드로 커넥션당 비용 Go 대비 높음 |

**🎯 면접관 평가 기준:**

- **L6 PASS**: WebSocket vs SSE vs Long Polling 비교, Kafka 기반 아키텍처, online/offline 분기, connection registry
- **L7 EXCEED**: C1M 솔루션 (OS tuning, goroutine 모델), fan-out on read/write 전략, delivery state machine + at-least-once 보장, multi-channel priority (in-app > push > email)
- **🚩 RED FLAG**: "모든 사용자에게 WebSocket 연결" (리소스 무한), 오프라인 사용자 처리 없음, 전달 보장 메커니즘 없음

---

## Q5: Distributed Task Queue

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: System Design at Scale

**Question:** Design a distributed task queue system (like Celery or Temporal) that handles 10M+ tasks/day with priority scheduling, at-least-once delivery guarantees, and dead letter queue support. How do you handle exactly-once semantics, task dependencies (DAG), and worker scaling?

---

**🧒 12살 비유:**
학교 선생님이 숙제를 나눠주는 시스템이야. 선생님(Producer)이 숙제(Task)를 큰 바구니(Queue)에 넣으면, 학생들(Worker)이 하나씩 가져가서 해. 중요한 건: 1) 급한 숙제부터(Priority), 2) 한 명이 아프면 다른 학생이 대신해야 하고(재시도), 3) 아무도 못 풀면 따로 모아두고(DLQ), 4) 수학 먼저 해야 과학을 할 수 있어(DAG dependency).

**📋 단계별 답변:**

**Step 1 — 맥락 & 평가 포인트**

```
Volume: 10M+ tasks/day (~116 TPS avg, burst 1000 TPS)
Task types: image processing, email, ML inference, data ETL
Latency: <100ms enqueue, execution depends on task type
Workers: 100~1000 (auto-scaled)
Requirements: priority, retry, DLQ, DAG, visibility timeout
```

평가 포인트:
- at-least-once vs exactly-once 시맨틱스의 현실적 구현
- Priority queue 분산 구현 (단순 FIFO가 아닌)
- 가시성 타임아웃(visibility timeout)과 재시도 전략
- DAG 기반 워크플로우 관리

**Step 2 — 핵심 설계**

```
Producers                      Task Queue System                    Workers
┌─────────┐          ┌──────────────────────────────────┐     ┌───────────┐
│Service A│──┐       │                                  │     │Worker Pool│
│         │  │       │  ┌──────────┐    ┌────────────┐  │  ┌──│  Group A  │
└─────────┘  │       │  │ Enqueue  │    │ Dispatcher │  │  │  │(img proc) │
┌─────────┐  ├──────►│  │   API    │───►│            │──┼──┤  └───────────┘
│Service B│──┤       │  └──────────┘    │ ┌────────┐ │  │  │  ┌───────────┐
│         │  │       │                  │ │Priority│ │  │  ├──│  Group B  │
└─────────┘  │       │  ┌──────────┐    │ │ Router │ │  │  │  │ (email)   │
┌─────────┐  │       │  │ Scheduler│    │ └────────┘ │  │  │  └───────────┘
│Cron/    │──┘       │  │(delayed/ │    └────────────┘  │  │  ┌───────────┐
│Schedule │          │  │ periodic)│                    │  └──│  Group C  │
└─────────┘          │  └──────────┘    ┌────────────┐  │     │ (ML infer)│
                     │                  │    DLQ     │  │     └───────────┘
                     │                  │ (max retry │  │
                     │                  │  exceeded) │  │
                     │                  └────────────┘  │
                     └──────────────────────────────────┘
```

**Priority Queue 구현:**
```
┌─────────────────────────────────────┐
│       Priority Queues (Redis)       │
│                                     │
│  queue:critical  ← P0 (즉시 처리)   │
│  queue:high      ← P1 (1분 이내)    │
│  queue:normal    ← P2 (best-effort) │
│  queue:low       ← P3 (유휴 시)     │
│                                     │
│  Dispatcher: 항상 높은 우선순위부터  │
│  Starvation 방지: weighted fair     │
│  (P0:8, P1:4, P2:2, P3:1)          │
└─────────────────────────────────────┘
```

**Step 3 — 다양한 관점**

**Delivery Semantics 비교:**

| 시맨틱 | 구현 | 장점 | 단점 | 사용처 |
|--------|------|------|------|--------|
| **At-most-once** | Fire & forget | 단순, 빠름 | 유실 가능 | 로그, 메트릭 |
| **At-least-once** | ACK + retry | 유실 없음 | 중복 가능 | 대부분의 작업 |
| **Exactly-once** | Idempotency key + dedup | 정확 | 복잡, 느림 | 결제, 정산 |

**Exactly-once의 현실:**
```
진정한 exactly-once는 불가능 (Two Generals Problem).
실질적 구현 = at-least-once + idempotent execution

방법 1: Idempotency Key
  - 태스크마다 unique key 할당
  - Worker가 실행 전 "이미 처리했나?" 확인
  - DB: INSERT ... ON CONFLICT DO NOTHING

방법 2: Transactional Outbox
  - 비즈니스 로직 + 태스크 상태를 같은 DB 트랜잭션으로
  - Outbox 테이블 → CDC로 큐에 발행
```

**Visibility Timeout 메커니즘:**
```
1. Worker가 task를 가져감 (BRPOPLPUSH → processing list)
2. Visibility timeout 시작 (예: 5분)
3-a. Worker가 완료 → ACK → processing list에서 제거
3-b. Timeout 초과 → task를 다시 queue로 이동 (재처리)

이를 통해: Worker 크래시 → task 자동 복구
```

**Step 4 — 구체적 예시: DAG Workflow**

```
         ┌──────────┐
         │ Extract  │
         │  Data    │
         └────┬─────┘
              │
      ┌───────┼───────┐
      │       │       │
      ▼       ▼       ▼
┌─────────┐┌──────┐┌──────────┐
│Transform││Clean ││ Validate │
│  A      ││ B    ││   C      │
└────┬────┘└──┬───┘└────┬─────┘
     │        │         │
     └────────┼─────────┘
              │
              ▼
        ┌───────────┐
        │   Load    │
        │  (merge)  │
        └───────────┘
```

**DAG 실행 엔진:**
```python
class TaskNode:
    task_id: str
    dependencies: List[str]   # 선행 task IDs
    status: Enum              # PENDING, READY, RUNNING, DONE, FAILED
    retry_count: int
    max_retries: int

def schedule_ready_tasks(dag):
    for node in dag.nodes:
        if node.status == PENDING:
            deps_met = all(
                dag.get(dep).status == DONE
                for dep in node.dependencies
            )
            if deps_met:
                node.status = READY
                enqueue(node)
```

**Retry 전략:**
```
Retry Policy:
  max_retries: 3
  backoff: exponential (1s, 2s, 4s) + jitter
  retry_on: [TimeoutError, ConnectionError, 5xx]
  no_retry_on: [ValidationError, 4xx]

After max retries:
  → DLQ (dead letter queue)
  → Alert (PagerDuty/Slack)
  → Manual intervention dashboard
```

**Step 5 — 트레이드오프 & 대안**

| 관점 | Redis-based (자체 구현) | RabbitMQ | Kafka | Temporal/Cadence |
|------|----------------------|----------|-------|-----------------|
| Priority | ZPOPMIN (sorted set) | Built-in (0-255) | Topic per priority | Activity priority |
| Persistence | RDB/AOF (위험) | Disk-backed | Log-based (견고) | DB-backed |
| DAG | 직접 구현 | 직접 구현 | 직접 구현 | Built-in workflow |
| Exactly-once | 직접 구현 | 제한적 | Kafka Streams EOS | Built-in |
| 복잡도 | 중간 | 낮음 | 중간 | 높음 (학습 곡선) |
| 추천 | 소규모, 빠른 구현 | 전통적 큐 | 이벤트 스트림 | 복잡한 워크플로우 |

**Step 6 — Polyglot Implementation Notes**

| 관점 | Python/FastAPI | Go | Kotlin/Spring |
|------|---------------|-----|--------------|
| 프레임워크 | **Celery** — 사실상 표준. Redis/RabbitMQ 브로커. `@task` 데코레이터. Canvas로 chord/chain/group (DAG). `celery beat`로 periodic | **Asynq** (Redis 기반, Celery-like) 또는 **Machinery**. goroutine worker로 높은 처리량. Temporal Go SDK가 가장 성숙 | **Spring Batch** (배치) + **Spring Integration** (메시징). 또는 **Temporal Java SDK**. `@Async` + `ThreadPoolTaskExecutor` 단순 케이스 |
| Worker 모델 | Celery prefork (멀티프로세스) 또는 gevent (코루틴). CPU-bound → prefork, I/O-bound → gevent. `-c 4` (concurrency 설정) | goroutine pool (`ants` 라이브러리). `runtime.GOMAXPROCS` 설정. Worker당 수만 concurrent task 가능 | `@Async` + `CompletableFuture`. Coroutine `Dispatchers.IO`. Virtual Thread (Loom) 시 I/O-bound 작업 효율적 |
| Priority 구현 | Celery `task_routes` + 큐별 priority. `CELERY_TASK_QUEUES`로 큐 정의. `-Q critical,high` worker 시작 | Asynq `asynq.Queue("critical", 6)` — weight 기반 fair scheduling. 간결한 API | Spring `@JmsListener` + priority header. 또는 Redis ZSET 기반 직접 구현. `PriorityBlockingQueue` JVM 내 |
| DLQ 처리 | Celery `task_reject_on_worker_lost=True` + `acks_late=True`. `on_failure` 핸들러로 DLQ 전송 | Asynq 내장 DLQ (`asynq.Retention`). Web UI로 DLQ 조회/재처리. 직관적 | Spring AMQP `x-dead-letter-exchange` 설정. RabbitMQ DLQ 네이티브 지원. `@RabbitListener` 자동 ACK/NACK |
| 모니터링 | **Flower** (Celery 대시보드). task 상태, worker 현황, 실시간 그래프. Prometheus exporter 존재 | Asynq Web UI 내장. 또는 Temporal Web UI (워크플로우 시각화, 매우 강력). Prometheus metrics 내장 | Spring Boot Actuator + Micrometer. Grafana 대시보드. Temporal Java SDK + Web UI |

**🎯 면접관 평가 기준:**

- **L6 PASS**: Visibility timeout, at-least-once + idempotency, priority queue 설계, retry with backoff
- **L7 EXCEED**: DAG scheduler 구현, exactly-once의 현실적 한계 설명 (Two Generals), Temporal vs 자체 구현 비교, worker auto-scaling (queue depth 기반 HPA), starvation prevention (weighted fair)
- **🚩 RED FLAG**: "exactly-once는 ACK하면 됩니다" (이론적 불가능성 인식 없음), DLQ 없는 설계, retry 시 backoff/jitter 없음

---

## Q6: Search Autocomplete

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: System Design at Scale

**Question:** Design a search autocomplete system for an e-commerce platform with 100M+ products. Compare Trie-based vs ElasticSearch-based approaches. How do you handle ranking, personalization, typo tolerance, and sub-50ms response times at scale?

---

**🧒 12살 비유:**
네이버 검색창에 "아이" 까지 치면 "아이폰", "아이패드", "아이스크림"이 뜨잖아. 이걸 만드는 두 가지 방법이 있어: 1) 단어를 나뭇가지처럼 저장(Trie) — "아" 가지에서 "이" 가지로 가면 그 밑의 모든 단어가 보여, 2) 책 뒤의 색인처럼(ElasticSearch) — 미리 모든 단어를 분류해놓고 빠르게 찾아. 중요한 건 인기 많은 거부터 보여주고(ranking), 내가 자주 찾는 것도 우선 보여주는 거야(personalization).

**📋 단계별 답변:**

**Step 1 — 맥락 & 평가 포인트**

```
Products: 100M+
Queries: 50K QPS (keystroke마다 요청)
Latency: <50ms p99
Features: prefix match, typo tolerance, personalization, trending
Languages: multi-language (한국어, 영어, 일본어)
```

평가 포인트:
- Trie vs inverted index 트레이드오프
- Ranking 알고리즘 (popularity, freshness, personalization)
- Typo tolerance (edit distance, phonetic)
- 성능 최적화 (caching, debounce, CDN)

**Step 2 — 핵심 설계**

```
Client (Browser/App)
  │  debounce 200ms
  │  min 2 chars
  ▼
┌────────────────────────────┐
│         CDN/Edge           │ ← 인기 prefix 캐싱
│  (popular prefixes cached) │
└────────────┬───────────────┘
             │ Cache Miss
             ▼
┌────────────────────────────┐
│    Autocomplete Service    │
│  ┌──────────────────────┐  │
│  │ Query Preprocessor   │  │  ← 정규화, 오타 교정
│  │  - normalize         │  │
│  │  - spell check       │  │
│  └──────────┬───────────┘  │
│             │              │
│  ┌──────────▼───────────┐  │
│  │  Suggestion Engine   │  │
│  │  ┌────────────────┐  │  │
│  │  │ L1: Redis/Trie │  │  │  ← Hot prefix (Top 10K)
│  │  ├────────────────┤  │  │
│  │  │ L2: Elastic    │  │  │  ← Full search
│  │  │    Search      │  │  │
│  │  └────────────────┘  │  │
│  └──────────┬───────────┘  │
│             │              │
│  ┌──────────▼───────────┐  │
│  │  Ranker / Blender    │  │  ← 점수 계산 + 개인화
│  └──────────────────────┘  │
└────────────────────────────┘
```

**Trie vs ElasticSearch 비교:**

| 속성 | Trie (In-memory) | ElasticSearch |
|------|-----------------|---------------|
| Latency | <1ms (메모리 직접) | ~5-20ms (네트워크+디스크) |
| Typo tolerance | 직접 구현 (BK-tree) | Built-in (fuzziness) |
| Ranking | 노드에 score 저장 | BM25 + custom scoring |
| 메모리 | ~10GB (100M 단어) | 디스크 기반, 캐싱 |
| 업데이트 | 전체 재빌드 or 점진적 | Near real-time indexing |
| 다국어 | 직접 tokenizer 구현 | Analyzer 플러그인 |
| 추천 | Hot prefix L1 캐시 | 메인 검색 엔진 |

**Step 3 — 다양한 관점**

**Ranking Algorithm:**
```
final_score = w1 * popularity_score     # 검색 빈도
            + w2 * freshness_score      # 최신성
            + w3 * revenue_score        # 매출 기여
            + w4 * personal_score       # 개인화
            + w5 * exact_match_boost    # 정확 매칭 보너스

Weights (e-commerce):
  w1=0.35, w2=0.15, w3=0.20, w4=0.20, w5=0.10

Personalization signals:
  - 최근 검색 이력
  - 구매 카테고리
  - 클릭 이력
  - 위치/시간대
```

**Typo Tolerance 전략:**

| 방법 | 원리 | 장점 | 단점 |
|------|------|------|------|
| **Edit Distance** | Levenshtein distance ≤ 2 | 정확 | 느림 (O(m×n)) |
| **N-gram** | "iphone" → {"ip","ph","ho","on","ne"} | 인덱싱 가능 | 메모리 사용 |
| **Phonetic** | Soundex/Double Metaphone | 발음 유사 | 영어 편향 |
| **Symmetric Delete** | 삭제 변형만 미리 생성 | 빠름 | 메모리 2x |
| **ES Fuzziness** | Auto fuzziness (1-2 edits) | 쉬운 설정 | 제한적 커스텀 |

**한국어 특수 처리:**
```
"ㅋㅍ" → "커피" (초성 검색)
"아이펀" → "아이폰" (오타)
"맥북프로" → "맥북 프로" (띄어쓰기 교정)

구현: nori tokenizer (ES) + jamo 분해 (Python hangul-jamo)
```

**Step 4 — 구체적 예시**

**Redis 기반 L1 (Hot Prefix):**
```
ZADD autocomplete:iph 100 "iphone 15"
ZADD autocomplete:iph 80  "iphone 14"
ZADD autocomplete:iph 50  "iphone case"

ZREVRANGE autocomplete:iph 0 9 WITHSCORES

ZINCRBY autocomplete:iph 1 "iphone 15"
```

**ElasticSearch L2 (Full Search):**
```json
{
  "suggest": {
    "product-suggest": {
      "prefix": "iph",
      "completion": {
        "field": "suggest",
        "size": 10,
        "fuzzy": {
          "fuzziness": "AUTO"
        },
        "contexts": {
          "category": ["electronics"],
          "locale": ["ko-KR"]
        }
      }
    }
  }
}
```

**클라이언트 최적화:**
```javascript
// Debounce: 200ms 동안 추가 입력 없을 때만 요청
// Min chars: 2글자 이상
// Cancel: 새 요청 시 이전 요청 취소 (AbortController)
// Cache: 동일 prefix 로컬 캐싱 (SessionStorage)
```

**Step 5 — 트레이드오프 & 대안**

| 관점 | Redis Sorted Set | Custom Trie | ElasticSearch Completion | Algolia |
|------|-----------------|-------------|------------------------|---------|
| Latency | <1ms | <1ms | ~10ms | ~20ms (managed) |
| 유지보수 | 낮음 | 높음 (메모리 관리) | 중간 | 매우 낮음 |
| 기능 | 제한적 | 유연 | 풍부 | 매우 풍부 |
| 비용 | 메모리 비용 | 개발 비용 | 인프라 비용 | SaaS 비용 |
| 추천 | L1 hot cache | 특수 요구 | L2 메인 엔진 | 빠른 출시 |

**Step 6 — Polyglot Implementation Notes**

| 관점 | Python/FastAPI | Go | Kotlin/Spring |
|------|---------------|-----|--------------|
| Trie 구현 | `pygtrie` 라이브러리 또는 dict 기반 직접 구현. 메모리 효율 낮지만 프로토타이핑 빠름. `__slots__`로 최적화 가능 | 직접 구현 (struct + map). 메모리 효율 높음 (포인터 크기 작음). `sync.RWMutex`로 concurrent read/write | `HashMap` 기반 Trie. Kotlin `data class`로 노드 정의 깔끔. `ConcurrentHashMap`으로 thread-safe |
| ES 클라이언트 | `elasticsearch-py` (async 지원). `AsyncElasticsearch`. 비동기 completion suggest 호출 | `olivere/elastic` 또는 공식 `go-elasticsearch`. type-safe query builder 부족하여 raw JSON 자주 사용 | Spring Data Elasticsearch. `@Document` 어노테이션. `ElasticsearchRestTemplate`. ReactiveElasticsearchClient (WebFlux) |
| 응답 시간 | FastAPI async → Redis <1ms, ES ~15ms. `orjson` response 직렬화. 단일 노드 충분 | net/http → Redis <1ms, ES ~10ms. 가장 낮은 오버헤드. JSON encoding `json-iterator` 사용 시 2x 빠름 | WebFlux → Redis <1ms, ES ~12ms. Jackson 직렬화. `@Cacheable` + Caffeine L1 + Redis L2 자동 구성 |
| 한국어 처리 | `hangul-jamo` (초성 분해), `konlpy` (형태소 분석). ES nori plugin과 조합 | `hangul` Go 패키지 (제한적). 대부분 ES에 위임. 한국어 NLP는 Python 에코시스템이 압도적 | `open-korean-text` (과거 twitter-korean-text). ES nori와 조합. JVM 기반 NLP 도구 다수 |
| 개인화 | `scikit-learn` / `LightGBM`으로 ranking model. Feature store (Feast) 연동. ML 모델 서빙은 Python 강점 | ranking은 단순 score 계산으로 충분하면 Go. ML 모델 필요 시 Python 서비스 호출 (gRPC) | Spring ML (제한적). 보통 Python ML 서비스를 gRPC/REST로 호출. TensorFlow Serving 연동 |

**🎯 면접관 평가 기준:**

- **L6 PASS**: Trie vs ES 비교, debounce + min chars 클라이언트 최적화, popularity 기반 ranking, CDN/Redis 캐싱
- **L7 EXCEED**: Multi-signal ranking formula, personalization 아키텍처 (feature store + ML ranker), 다국어 처리 전략, A/B testing for suggestion quality, prefix → completion suggestion의 data pipeline (Kafka → ES near-realtime)
- **🚩 RED FLAG**: "DB에서 LIKE 검색하면 됩니다" (스케일 불가), typo tolerance 무시, ranking 없이 알파벳 순서

---

## Q7: Event-Driven Order Processing

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: System Design at Scale

**Question:** Design an event-driven order processing system for an e-commerce platform handling 100K orders/day. Implement the SAGA pattern for distributed transactions across Order, Payment, Inventory, and Shipping services. How do you handle compensating transactions and ensure eventual consistency?

---

**🧒 12살 비유:**
피자 주문을 생각해봐. 주문(Order) → 결제(Payment) → 재고 확인(Inventory) → 배달(Shipping) 이 4단계를 거쳐. 만약 결제는 됐는데 재고가 없으면? 결제를 취소(보상 트랜잭션)해야 해. 각 단계가 다른 가게에서 일어나기 때문에(마이크로서비스), 한꺼번에 "취소!"라고 못 해. 대신 "결제 취소해주세요"라는 편지(이벤트)를 보내서 하나씩 되돌리는 거야.

**📋 단계별 답변:**

**Step 1 — 맥락 & 평가 포인트**

```
Orders: 100K/day (~1.2 TPS avg, peak 10 TPS)
Services: Order, Payment, Inventory, Shipping, Notification
SLA: Order placement <2s, eventual consistency <30s
Failure rate: ~2% (payment decline, out of stock, etc.)
```

평가 포인트:
- Choreography vs Orchestration SAGA 비교
- 보상 트랜잭션 설계 (idempotent, 순서 보장)
- Eventual consistency와 사용자 경험
- 이벤트 스키마 설계와 버전 관리

**Step 2 — 핵심 설계**

**SAGA 패턴 — Orchestration 방식 (추천):**

```
┌──────────────────────────────────────────────────┐
│              SAGA Orchestrator                   │
│          (Order Saga Coordinator)                │
│                                                  │
│  State Machine:                                  │
│  ┌─────────┐   ┌─────────┐   ┌──────────┐       │
│  │ Order   │──►│ Payment │──►│Inventory │──►...  │
│  │ Created │   │ Process │   │ Reserve  │        │
│  └────┬────┘   └────┬────┘   └────┬─────┘       │
│       │ fail        │ fail        │ fail         │
│       ▼             ▼             ▼              │
│  ┌─────────┐   ┌─────────┐   ┌──────────┐       │
│  │ Order   │◄──│ Payment │◄──│Inventory │       │
│  │ Cancel  │   │ Refund  │   │ Release  │       │
│  └─────────┘   └─────────┘   └──────────┘       │
└─────────────────────┬────────────────────────────┘
                      │ Commands (Kafka)
         ┌────────────┼────────────┬───────────┐
         ▼            ▼            ▼           ▼
    ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌────────┐
    │ Order   │ │ Payment  │ │Inventory│ │Shipping│
    │ Service │ │ Service  │ │ Service │ │Service │
    └─────────┘ └──────────┘ └─────────┘ └────────┘
```

**Choreography vs Orchestration:**

| 속성 | Choreography (이벤트) | Orchestration (명령) |
|------|---------------------|---------------------|
| 결합도 | 낮음 (서비스 독립) | 중간 (오케스트레이터 의존) |
| 가시성 | 낮음 (추적 어려움) | 높음 (중앙 상태 관리) |
| 복잡도 | N개 서비스 → 이벤트 폭발 | 중앙 집중 → 관리 용이 |
| 순환 의존 | 위험 있음 | 없음 |
| 보상 순서 | 보장 어려움 | 명시적 보장 |
| 추천 | 3개 이하 단순 플로우 | 4개 이상 복잡 플로우 |

**Step 3 — 다양한 관점**

**SAGA State Machine (정상 + 실패 흐름):**

```
                    Happy Path
    ┌──────────────────────────────────────────────────┐
    │                                                  │
    ▼                                                  │
ORDER_CREATED ──► PAYMENT_PENDING ──► INVENTORY_RESERVED
    │                  │                    │
    │                  │ fail               │ fail
    │                  ▼                    ▼
    │           PAYMENT_FAILED      INVENTORY_FAILED
    │                  │                    │
    │                  │           ┌────────┘
    │                  │           │ compensate
    │                  │           ▼
    │                  │    PAYMENT_REFUNDED
    │                  │           │
    ▼                  ▼           ▼
ORDER_CANCELLED ◄──────────────────
    │
    ▼
ORDER_COMPLETED ──► SHIPPING_INITIATED ──► ORDER_DELIVERED
```

**보상 트랜잭션 테이블:**

| Step | 정상 Action | 보상 Action | 멱등성 키 |
|------|-----------|------------|----------|
| 1. Order | createOrder() | cancelOrder() | order_id |
| 2. Payment | processPayment() | refundPayment() | payment_id |
| 3. Inventory | reserveStock() | releaseStock() | reservation_id |
| 4. Shipping | createShipment() | cancelShipment() | shipment_id |

**Step 4 — 구체적 예시**

**이벤트 스키마 (CloudEvents 표준):**
```json
{
  "specversion": "1.0",
  "type": "com.ecommerce.order.created",
  "source": "/order-service",
  "id": "evt-a1b2c3",
  "time": "2026-03-17T10:00:00Z",
  "datacontenttype": "application/json",
  "subject": "order-12345",
  "data": {
    "order_id": "order-12345",
    "customer_id": "cust-789",
    "items": [
      {"product_id": "prod-001", "quantity": 2, "price": 29900}
    ],
    "total_amount": 59800,
    "saga_id": "saga-xyz-789",
    "correlation_id": "corr-abc-123"
  },
  "extensions": {
    "schemaversion": "1.2",
    "sagastep": 1
  }
}
```

**Saga Orchestrator 상태 저장:**
```sql
CREATE TABLE saga_instances (
    saga_id         UUID PRIMARY KEY,
    saga_type       VARCHAR(50) NOT NULL,
    current_step    INT NOT NULL,
    state           JSONB NOT NULL,        -- 각 step의 결과 저장
    status          VARCHAR(20) NOT NULL,  -- RUNNING, COMPENSATING, COMPLETED, FAILED
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL,
    version         INT NOT NULL           -- Optimistic locking
);

-- 감사 로그
CREATE TABLE saga_step_log (
    id              BIGSERIAL PRIMARY KEY,
    saga_id         UUID REFERENCES saga_instances(saga_id),
    step_number     INT NOT NULL,
    action          VARCHAR(20) NOT NULL,  -- EXECUTE, COMPENSATE
    status          VARCHAR(20) NOT NULL,  -- SUCCESS, FAILED
    request_payload JSONB,
    response_payload JSONB,
    executed_at     TIMESTAMP NOT NULL
);
```

**Outbox Pattern (이벤트 발행 보장):**
```
┌──────────────────────────────────────┐
│            Order Service             │
│                                      │
│  BEGIN TRANSACTION                   │
│    INSERT INTO orders (...)          │
│    INSERT INTO outbox (              │
│      event_type, payload, status     │
│    )                                 │
│  COMMIT                             │
│                                      │
│  Outbox Poller (async):             │
│    SELECT * FROM outbox             │
│      WHERE status = 'PENDING'        │
│    → Kafka produce                   │
│    → UPDATE outbox SET               │
│        status = 'PUBLISHED'          │
└──────────────────────────────────────┘
```

**Step 5 — 트레이드오프 & 대안**

| 관점 | SAGA Orchestration | SAGA Choreography | 2PC (Two-Phase Commit) | Event Sourcing |
|------|-------------------|-------------------|----------------------|---------------|
| 일관성 | Eventual | Eventual | Strong | Eventual |
| 성능 | 중간 | 높음 | 낮음 (lock) | 높음 |
| 복잡도 | 중간 | 높음 (이벤트 추적) | 낮음 | 높음 |
| 장애 복구 | Saga state에서 복구 | 이벤트 재생 | Coordinator 장애 치명적 | 이벤트 재생 |
| 운영 가시성 | 높음 (중앙 로그) | 낮음 (분산 로그) | 높음 | 이벤트 저장소 조회 |
| 추천 | 대부분의 MSA | 단순 플로우 | 모놀리스 | CQRS 결합 시 |

**Step 6 — Polyglot Implementation Notes**

| 관점 | Python/FastAPI | Go | Kotlin/Spring |
|------|---------------|-----|--------------|
| SAGA 프레임워크 | 직접 구현이 일반적. `temporalio` Python SDK (Temporal). 상태 머신은 `transitions` 라이브러리. `faust` (Kafka Streams Python) | Temporal Go SDK (가장 성숙). `go-saga` 경량 라이브러리. 직접 구현 시 `statemachine` 패턴 | **Axon Framework** — SAGA + Event Sourcing 통합 (JVM 최강). Spring State Machine. Temporal Java SDK |
| 이벤트 발행 | `aiokafka` (async Kafka producer). `confluent-kafka` (C-binding, 더 빠름). FastAPI + Kafka 조합 | `segmentio/kafka-go` 또는 `confluentinc/confluent-kafka-go`. 성능 우수, 네이티브 바이너리 | Spring Kafka (`@KafkaListener`, `KafkaTemplate`). Spring Cloud Stream으로 브로커 추상화 |
| Outbox 패턴 | SQLAlchemy + async. `debezium` (CDC) 연동으로 polling 대체. 또는 `APScheduler`로 주기적 polling | `pgx` + Kafka producer. CDC 방식 추천 (`Debezium`). 또는 Go routine으로 polling (효율적) | **Spring Modulith Events** — `@ApplicationModuleListener` + outbox 자동화! JPA `@Transactional` + outbox INSERT 한 트랜잭션 |
| 보상 트랜잭션 | `try/except` + compensate 함수 호출. decorator로 retry/compensation 패턴화. `tenacity` 라이브러리 (retry) | `defer`로 cleanup 패턴. error handling이 명시적이어서 보상 흐름 명확. `errgroup`으로 병렬 보상 | `@Transactional(rollbackFor=...)`. Axon `@SagaEventHandler` + `@EndSaga`. Kotlin `runCatching`으로 깔끔한 에러 처리 |
| 테스트 | `pytest` + embedded Kafka (`testcontainers`). SAGA 흐름 통합 테스트 | `testcontainers-go`. 테이블 기반 테스트로 SAGA 시나리오 커버. Temporal test framework 내장 | `@SpringBootTest` + `@EmbeddedKafka`. Axon test fixtures (`AggregateTestFixture`). TestContainers Kotlin |

**🎯 면접관 평가 기준:**

- **L6 PASS**: Choreography vs Orchestration 비교, 보상 트랜잭션 목록, eventual consistency 설명, 이벤트 스키마 설계
- **L7 EXCEED**: SAGA state machine 설계 + persistence, Outbox pattern으로 이벤트 발행 보장, CloudEvents 표준, schema versioning (forward/backward compatibility), dead letter + manual intervention 전략
- **🚩 RED FLAG**: 2PC를 MSA에서 사용 제안, 보상 트랜잭션 누락, 이벤트 멱등성 미고려, "순서대로 하면 되지 않나요?" (분산 환경 이해 부족)

---

## Q8: Multi-Region Data Replication

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: System Design at Scale

**Question:** Design a multi-region data replication system for a globally distributed application serving users across US, EU, and APAC. How do you handle conflict resolution with CRDTs, ensure data sovereignty (GDPR), and optimize for latency? Discuss the CAP theorem implications and your consistency model choices.

---

**🧒 12살 비유:**
서울, 뉴욕, 런던에 각각 일기장 복사본이 있다고 생각해봐. 세 곳에서 동시에 같은 페이지를 고치면 어떻게 될까? 1) 한 곳만 쓰기 허용(single-leader) — 안전하지만 느려, 2) 아무 데서나 쓰기 허용(multi-leader) — 빠르지만 충돌 해결 필요, 3) 특별한 자료구조(CRDT)를 써서 충돌이 자동으로 해결되게 만들기. 그리고 유럽 사람 일기는 법(GDPR)에 의해 유럽 밖으로 못 가져가!

**📋 단계별 답변:**

**Step 1 — 맥락 & 평가 포인트**

```
Regions: US-West, US-East, EU-West, APAC-Tokyo
Users: 500M+ globally
Latency: <100ms read, <500ms write (same region)
Cross-region latency: US↔EU ~80ms, US↔APAC ~150ms
Data sovereignty: EU data stays in EU (GDPR Art. 44-49)
Consistency: tunable per data type
```

평가 포인트:
- CAP theorem과 현실적 consistency 모델 선택
- CRDT 이해와 적용 가능한 데이터 타입
- Conflict resolution 전략 (LWW, vector clock, merge function)
- GDPR data residency 아키텍처

**Step 2 — 핵심 설계**

```
                    Global Control Plane
                    ┌──────────────────┐
                    │  Config/Routing  │
                    │  DNS (GeoDNS)    │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   US Region   │  │   EU Region   │  │  APAC Region  │
│               │  │               │  │               │
│ ┌───────────┐ │  │ ┌───────────┐ │  │ ┌───────────┐ │
│ │ App Tier  │ │  │ │ App Tier  │ │  │ │ App Tier  │ │
│ └─────┬─────┘ │  │ └─────┬─────┘ │  │ └─────┬─────┘ │
│       │       │  │       │       │  │       │       │
│ ┌─────▼─────┐ │  │ ┌─────▼─────┐ │  │ ┌─────▼─────┐ │
│ │ DB Primary│ │  │ │ DB Primary│ │  │ │ DB Primary│ │
│ │ (US data) │◄┼──┼─┤ (EU data) │◄┼──┼─┤(APAC data)│ │
│ │           │─┼──┼►│           │─┼──┼►│           │ │
│ └───────────┘ │  │ └───────────┘ │  │ └───────────┘ │
│               │  │               │  │               │
│ ┌───────────┐ │  │ ┌───────────┐ │  │ ┌───────────┐ │
│ │ Read      │ │  │ │ Read      │ │  │ │ Read      │ │
│ │ Replicas  │ │  │ │ Replicas  │ │  │ │ Replicas  │ │
│ └───────────┘ │  │ └───────────┘ │  │ └───────────┘ │
└───────────────┘  └───────────────┘  └───────────────┘

Replication: Async (default) / Sync (critical data)
Conflict Resolution: LWW + CRDT (per data type)
```

**Replication Topology 비교:**

| 토폴로지 | 설명 | 장점 | 단점 |
|----------|------|------|------|
| **Single-Leader** | 1개 리전만 쓰기 | 충돌 없음, 단순 | 쓰기 latency (원격) |
| **Multi-Leader** | 각 리전 쓰기 가능 | 낮은 latency | 충돌 해결 필요 |
| **Leaderless** | 어디서든 쓰기 (quorum) | 가용성 최고 | 복잡, 일관성 어려움 |

**데이터 타입별 전략:**

| 데이터 | 모델 | 이유 |
|--------|------|------|
| User profile | Single-Leader | 충돌 드물, 일관성 중요 |
| Shopping cart | Multi-Leader (CRDT) | 동시 편집 빈번, 가용성 우선 |
| Order/Payment | Single-Leader | 정확성 필수 (돈) |
| User preferences | Multi-Leader (LWW) | 충돌 시 최신 값 우선 |
| Like/View count | Leaderless (G-Counter) | 정확도보다 가용성 |
| Inventory | Single-Leader | 과잉 판매 방지 |

**Step 3 — 다양한 관점**

**CAP Theorem 현실적 적용:**
```
CAP는 binary가 아닌 spectrum:

CP (Consistency + Partition tolerance):
  → 결제, 재고 — partition 시 쓰기 거부
  → DynamoDB strong consistency, CockroachDB

AP (Availability + Partition tolerance):
  → 장바구니, 좋아요 — partition 시에도 각 리전 독립 쓰기
  → DynamoDB eventual consistency, Cassandra

실제로는: "partition 발생 시 이 데이터는 어떻게 할까?"로 결정
  → 주문: 거부 (CP)
  → 장바구니: 허용 후 나중에 합침 (AP)
```

**CRDT (Conflict-free Replicated Data Types):**

| CRDT 타입 | 동작 | 사용 예 |
|-----------|------|---------|
| **G-Counter** | 증가만 가능 | 조회수, 좋아요 수 |
| **PN-Counter** | 증가/감소 | 재고 카운터 (주의) |
| **G-Set** | 추가만 가능 | 태그 목록 |
| **OR-Set** | 추가/삭제 | 장바구니 아이템 |
| **LWW-Register** | 최신 타임스탬프 승리 | 사용자 이름 변경 |
| **MV-Register** | 동시 값 모두 유지 | 협업 편집 |

**G-Counter 예시 (좋아요 수):**
```
Node US: {US: 5, EU: 0, APAC: 0} → total = 5
Node EU: {US: 0, EU: 3, APAC: 0} → total = 3
Node APAC: {US: 0, EU: 0, APAC: 2} → total = 2

Merge: {US: max(5,0,0), EU: max(0,3,0), APAC: max(0,0,2)}
     = {US: 5, EU: 3, APAC: 2} → total = 10

특성: 순서 무관, 중복 merge 안전, 항상 수렴
```

**OR-Set 예시 (장바구니):**
```
US에서: add("iPhone", tag=US-1)
EU에서: add("MacBook", tag=EU-1)
US에서: remove("iPhone", tag=US-1)

Merge 결과: {"MacBook"(EU-1)}  ← iPhone의 US-1 태그가 제거됨

핵심: 각 add에 고유 태그 → remove는 특정 태그만 제거
→ 동시 add/remove 충돌 자동 해결
```

**Step 4 — 구체적 예시: GDPR Data Residency**

```
┌──────────────────────────────────────────────┐
│              Data Classification             │
│                                              │
│  ┌────────────┐  ┌────────────┐  ┌─────────┐│
│  │ Global     │  │ Regional   │  │ Local   ││
│  │ (non-PII)  │  │ (PII)      │  │(payment)││
│  │            │  │            │  │         ││
│  │ Products   │  │ User name  │  │ Credit  ││
│  │ Categories │  │ Email      │  │ card    ││
│  │ Prices     │  │ Address    │  │ Bank    ││
│  │            │  │ Phone      │  │ details ││
│  └────────────┘  └────────────┘  └─────────┘│
│   Replicate      Stay in        Stay in     │
│   everywhere     user's region  user's      │
│                                 region +    │
│                                 encrypted   │
└──────────────────────────────────────────────┘
```

**GDPR 구현 아키텍처:**
```
EU 사용자 → GeoDNS → EU Region
  → PII: EU DB에만 저장 (암호화)
  → non-PII: 글로벌 복제 OK

US에서 EU 사용자 데이터 접근 시:
  → Proxy를 통해 EU DB 조회 (데이터 이동 없음)
  → 또는 tokenized reference만 US에 저장

데이터 삭제 (Right to be forgotten):
  → EU DB에서 PII 삭제
  → 모든 리전의 캐시 무효화
  → Analytics 데이터 익명화 (되돌릴 수 없게)
```

**Conflict Resolution — Vector Clock:**
```
Event 1 (US): {US:1, EU:0} — user changes name to "Alice"
Event 2 (EU): {US:0, EU:1} — user changes name to "Alicia"

비교: {US:1,EU:0} vs {US:0,EU:1} → 동시 발생! (neither dominates)

Resolution strategies:
  a) LWW (Last Writer Wins): 물리 타임스탬프 비교 → 간단하지만 데이터 손실
  b) Application-level merge: 사용자에게 충돌 표시 → UX 복잡
  c) CRDT: 자료구조가 자동 해결 → 데이터 타입 제한

추천: 데이터별 전략 혼합
  - Profile name: LWW (마지막 변경 우선)
  - Cart items: OR-Set (합집합)
  - Counters: G-Counter (각 리전 독립 카운트)
```

**Step 5 — 트레이드오프 & 대안**

| 관점 | CockroachDB (CP) | DynamoDB Global Tables (AP) | Cassandra (AP) | Custom (Kafka + CRDT) |
|------|------------------|---------------------------|----------------|---------------------|
| 일관성 | Serializable | Eventual (configurable) | Tunable | CRDT convergence |
| Latency (write) | Higher (consensus) | Low (local write) | Low (local write) | Low (local write) |
| Conflict | 없음 (CP) | LWW (자동) | LWW / custom | CRDT (자동) |
| GDPR | Region pinning 지원 | Table-level region 설정 | DC-aware replication | 직접 구현 |
| 복잡도 | 낮음 (SQL 호환) | 낮음 (관리형) | 중간 | 높음 |
| 추천 | 금융, 재고 | 일반 글로벌 앱 | 시계열, 로그 | 특수 요구 |

**Step 6 — Polyglot Implementation Notes**

| 관점 | Python/FastAPI | Go | Kotlin/Spring |
|------|---------------|-----|--------------|
| CRDT 라이브러리 | `pycrdt` (Yjs Python binding). 또는 직접 구현 (dict 기반 G-Counter 간단). Research/프로토타이핑에 적합 | `github.com/automerge/automerge-go`. 또는 직접 구현 — Go struct로 CRDT 정의, `sync.Mutex`로 보호. 프로덕션 적합 | `com.alipay.sofa:jraft` (SOFAJRaft). Kotlin data class로 CRDT 모델링 깔끔. Akka Distributed Data (Lightbend) |
| Multi-region DB | `asyncpg` + CockroachDB (PostgreSQL wire protocol 호환). `databases` 라이브러리로 connection routing | `pgx` + CockroachDB. `jackc/pgx` — region-aware connection pool. 또는 DynamoDB `aws-sdk-go-v2` | Spring Data + CockroachDB (JPA 호환). `AbstractRoutingDataSource`로 리전별 라우팅. R2DBC for reactive |
| Conflict Resolution | Python의 유연한 dict merge가 conflict resolution 로직에 적합. `deepmerge` 라이브러리 | explicit 에러 핸들링으로 conflict 처리 명확. `errors.Is` 패턴으로 conflict 타입 분기 | Kotlin `sealed class`로 conflict 타입 모델링 우아함. `when` expression으로 전략 분기 |
| CDC/Replication | `debezium` + `faust` (Kafka Streams in Python). Change event 처리. `confluent-kafka` for low-level | `debezium` + `segmentio/kafka-go`. Go consumer가 변경 이벤트를 처리하여 CRDT merge 실행 | Spring Cloud Stream + Debezium Embedded. `@ChangeEventHandler` 패턴. Axon Server (이벤트 저장소 + 복제) |
| Data Residency | SQLAlchemy `binds`로 DB 라우팅. middleware에서 user region 감지 → 적절한 DB 연결 | `context.Value`에 region 정보 전파. middleware → handler → repository 체인으로 DB 선택 | `@Transactional` + custom `DataSource` routing. Spring Security의 `SecurityContext`에서 user region 추출 |

**🎯 면접관 평가 기준:**

- **L6 PASS**: CAP theorem 설명, single-leader vs multi-leader 비교, async replication의 eventual consistency, conflict resolution 기본 (LWW)
- **L7 EXCEED**: CRDT 종류별 특성과 적용 (G-Counter, OR-Set), vector clock으로 동시성 감지, 데이터 타입별 consistency 모델 혼합 전략, GDPR data residency 아키텍처 (분류 + 라우팅 + 삭제), CockroachDB의 Raft 기반 consensus 이해
- **🚩 RED FLAG**: "모든 데이터를 강한 일관성으로" (latency 무시), CRDT를 들어본 적 없음, GDPR을 "암호화만 하면 된다"로 축소, conflict resolution 전략 없이 multi-leader 제안

---

## Summary Table

| Q# | Topic | Key Concepts | Difficulty Focus |
|----|-------|-------------|-----------------|
| Q1 | Rate Limiter | Token Bucket, Sliding Window, Redis Lua, Multi-region | 분산 동시성, Partition 대응 |
| Q2 | Distributed Cache | Consistent Hashing, Stampede, Write Strategy, Multi-DC | 캐시 일관성, 다층 아키텍처 |
| Q3 | URL Shortener | Base62, Snowflake ID, Read-heavy 최적화 | 분산 ID 생성, 스케일링 |
| Q4 | Real-time Notification | WebSocket vs SSE, C1M, Delivery Guarantee | 커넥션 관리, 전달 보장 |
| Q5 | Distributed Task Queue | At-least-once, Priority, DLQ, DAG | 실행 시맨틱스, 워크플로우 |
| Q6 | Search Autocomplete | Trie vs ES, Ranking, Personalization | 검색 알고리즘, 다국어 |
| Q7 | Event-Driven Order | SAGA, Compensation, Outbox Pattern | 분산 트랜잭션, 이벤트 설계 |
| Q8 | Multi-Region Replication | CRDT, Conflict Resolution, GDPR | 데이터 일관성, 규제 준수 |

---


> 대상: FAANG L6/L7 (Staff/Principal Engineer)
> 총 문항: 12개 (Q9~Q20) | 난이도: ⭐⭐⭐⭐⭐
> 스택: Python / Go / Kotlin 비교 포함

## 목차

### Category 2: Distributed Systems (Q9~Q14)
- [Q9: CAP/PACELC 정리와 실제 시스템 분류](#q9-cappacelc-정리와-실제-시스템-분류)
- [Q10: 분산 합의 — Raft/Paxos](#q10-분산-합의--raftpaxos)
- [Q11: 분산 트랜잭션 — 2PC vs SAGA vs TCC](#q11-분산-트랜잭션--2pc-vs-saga-vs-tcc)
- [Q12: 분산 시계 — Lamport/Vector/HLC](#q12-분산-시계--lamportvectorhlc)
- [Q13: 일관성 모델 — Linearizability vs Sequential vs Eventual](#q13-일관성-모델--linearizability-vs-sequential-vs-eventual)
- [Q14: 분산 락 — Redlock 논쟁과 Fencing Token](#q14-분산-락--redlock-논쟁과-fencing-token)

### Category 3: Database Internals (Q15~Q20)
- [Q15: B-tree vs LSM-tree](#q15-b-tree-vs-lsm-tree)
- [Q16: MVCC와 Isolation Level](#q16-mvcc와-isolation-level)
- [Q17: Query Optimizer](#q17-query-optimizer)
- [Q18: Sharding 전략](#q18-sharding-전략)
- [Q19: 커넥션 풀링 비교](#q19-커넥션-풀링-비교)
- [Q20: Replication 전략](#q20-replication-전략)

---

## Category 2: Distributed Systems

### Q9: CAP/PACELC 정리와 실제 시스템 분류

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Distributed Systems

**Question:**
CAP 정리의 한계를 설명하고, PACELC가 이를 어떻게 보완하는지 논의하라. 실제 프로덕션에서 사용하는 데이터 저장소(예: DynamoDB, Cassandra, Spanner, CockroachDB, etcd)를 CAP/PACELC 프레임워크로 분류하고, 각 시스템이 왜 그런 선택을 했는지 설계 배경을 설명하라. 팀에서 새로운 서비스의 데이터 저장소를 결정해야 할 때, 이 프레임워크를 어떻게 의사결정에 활용하는지 구체적으로 설명하라.

---

**🧒 12살 비유:**
세 친구(C, A, P)가 있는데, 항상 셋이 동시에 놀 수는 없다 — 이게 CAP 정리야. 네트워크 파티션(P)은 인터넷이 끊기는 것과 같아서, 실제로는 피할 수 없어. 그래서 진짜 선택은 "인터넷이 끊겼을 때 정확한 답을 줄까(CP), 아니면 빠르게라도 답을 줄까(AP)"야. PACELC는 여기에 "인터넷이 정상일 때도 빠른 응답(L)과 정확한 일관성(C) 중 뭘 고를래?"를 추가한 거야. 마치 시험에서 "정확하게 쓸까 vs 빨리 쓸까"를 상황별로 따로 정하는 것과 비슷해.

**📋 단계별 답변:**

**Step 1 — 맥락: CAP 정리의 탄생과 한계**

Eric Brewer가 2000년에 제안한 CAP 정리는 분산 시스템에서 Consistency(일관성), Availability(가용성), Partition Tolerance(분할 허용) 셋 중 둘만 보장할 수 있다고 말한다. 2002년 Gilbert와 Lynch가 형식적으로 증명했다. 그러나 CAP에는 심각한 한계가 있다:

1. **이진 선택의 함정**: 실제 시스템은 C와 A를 0/1이 아닌 스펙트럼으로 조절한다
2. **파티션 발생 시에만 의미**: 정상 상태에서의 Latency-Consistency 트레이드오프를 다루지 않는다
3. **일관성의 모호함**: CAP의 C는 linearizability만을 의미하지만, 실제로는 다양한 일관성 수준이 존재한다

**Step 2 — 핵심 기술: PACELC 프레임워크**

Daniel Abadi가 2012년에 제안한 PACELC는 CAP를 확장한다:

```
if (Partition) then {Availability vs Consistency}
else {Latency vs Consistency}

표기: P+A/E+L  →  "파티션 시 A 선택, 정상 시 L 선택"
      P+C/E+C  →  "파티션 시 C 선택, 정상 시도 C 선택"
```

실제 시스템 분류:

| 시스템 | CAP | PACELC | 설계 배경 |
|--------|-----|--------|-----------|
| **DynamoDB** | AP | PA/EL | 아마존 쇼핑 카트 — 가용성과 속도 최우선 |
| **Cassandra** | AP | PA/EL | Facebook 메시징 — 쓰기 가용성 극대화 (tunable consistency) |
| **Spanner** | CP | PC/EC | Google 광고 — 글로벌 strong consistency 필요 (TrueTime) |
| **CockroachDB** | CP | PC/EC | Spanner 오픈소스 대안 — serializable 기본 |
| **etcd** | CP | PC/EC | Kubernetes 메타데이터 — Raft 기반 강한 일관성 |
| **MongoDB** | CP* | PC/EL | *기본 설정 CP이지만 read preference로 AP 가능 |

**Step 3 — 다양한 관점: 스택별 클라이언트 구현 차이**

```python
import boto3
from botocore.config import Config

dynamodb = boto3.resource('dynamodb', config=Config(
    retries={'max_attempts': 3, 'mode': 'adaptive'}
))
table = dynamodb.Table('orders')
response = table.get_item(
    Key={'order_id': '12345'},
    ConsistentRead=False  # PA/EL: eventual consistency, 낮은 latency
)

response = table.get_item(
    Key={'order_id': '12345'},
    ConsistentRead=True   # PC/EC 모드: 2x RCU 소모, 높은 latency
)
```

```go
// Go — etcd (PC/EC 시스템)
import (
    clientv3 "go.etcd.io/etcd/client/v3"
    "go.etcd.io/etcd/client/v3/concurrency"
)

func getWithLinearizable(cli *clientv3.Client, key string) (*clientv3.GetResponse, error) {
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    // etcd는 기본적으로 serializable read (follower에서 읽기 가능, 빠름)
    // WithSerializable() 제거하면 linearizable (leader에서만 읽기, 강한 일관성)
    return cli.Get(ctx, key) // linearizable by default — PC/EC 선택
}

// Serializable read — latency 최적화가 필요할 때
func getWithSerializable(cli *clientv3.Client, key string) (*clientv3.GetResponse, error) {
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    return cli.Get(ctx, key, clientv3.WithSerializable())
}
```

```kotlin
// Kotlin — CockroachDB (PC/EC 시스템)
import org.springframework.transaction.annotation.Transactional
import org.springframework.transaction.annotation.Isolation

@Service
class OrderService(private val orderRepo: OrderRepository) {

    // CockroachDB 기본: SERIALIZABLE isolation
    // PC/EC 선택 → 강한 일관성, follower read로 latency 조절
    @Transactional(isolation = Isolation.SERIALIZABLE)
    fun placeOrder(order: Order): Order {
        // CockroachDB는 retry 필수 — serialization conflict 발생 가능
        return RetryHelper.withRetry(maxAttempts = 3) {
            orderRepo.save(order)
        }
    }

    // Follower Read — stale data 허용하여 latency 최적화
    @Transactional(readOnly = true)
    fun getOrderHistory(userId: String): List<Order> {
        // AS OF SYSTEM TIME '-10s' → 10초 전 스냅샷 읽기
        return orderRepo.findByUserIdAsOfSystemTime(userId, "-10s")
    }
}
```

**Step 4 — 구체적 예시: 의사결정 프레임워크 적용**

실제 팀에서 새 서비스의 저장소를 결정할 때 사용하는 의사결정 트리:

```
1. 데이터 특성 분석
   ├─ 금융/결제 → Strong Consistency 필수 → PC/EC (Spanner, CockroachDB)
   ├─ 소셜/피드 → Availability 우선 → PA/EL (Cassandra, DynamoDB)
   ├─ 세션/캐시 → Speed 최우선 → PA/EL (Redis Cluster)
   └─ 메타데이터/설정 → Consistency 우선 → PC/EC (etcd, ZooKeeper)

2. SLA 요구사항
   ├─ p99 < 10ms → EL 필수 → DynamoDB, Cassandra
   ├─ p99 < 100ms → EC 가능 → CockroachDB (follower read)
   └─ p99 < 500ms → EC 가능 → Spanner (글로벌)

3. 파티션 시 행동
   ├─ 주문 접수는 계속 → PA 선택 (DynamoDB)
   └─ 잔액 조회 정확해야 → PC 선택 (CockroachDB)
```

**Step 5 — 트레이드오프 & 대안**

| 선택 | 얻는 것 | 잃는 것 | 완화 전략 |
|------|---------|---------|-----------|
| PA/EL | 높은 가용성, 낮은 지연 | 일시적 불일치 | read-repair, anti-entropy |
| PC/EC | 강한 일관성 | 파티션 시 불가용 | multi-region Raft, witness replica |
| PA/EC | 가용성 + 일관성 | 복잡성 | MongoDB 기본 설정이 이 영역 |
| PC/EL | 드문 조합 | — | PNUTS (Yahoo) 가 시도 |

Tunable Consistency 접근 (Cassandra):
```
QUORUM = ⌊N/2⌋ + 1
R + W > N → Strong Consistency (PC/EC 흉내)
R=1, W=1 → Eventual Consistency (PA/EL)
```

**Step 6 — 성장 & 심화**

- Jepsen 테스트로 실제 파티션 상황에서 시스템 행동 검증 (Kyle Kingsbury)
- TrueTime (Spanner)이 GPS + 원자시계로 불확실성 구간을 줄여 CP를 "실용적"으로 만든 혁신
- CockroachDB의 closed timestamp 메커니즘이 follower read를 가능하게 하는 방식
- CALM 정리 (Hellerstein) — coordination-free consistency의 이론적 기반

**🎯 면접관 평가 기준:**

| 수준 | 기대 |
|------|------|
| **L6 PASS** | CAP 3가지 속성 정확히 설명, 실제 시스템 2-3개 분류, PA vs PC 차이 설명 |
| **L7 EXCEED** | PACELC로 확장, tunable consistency 설명, 의사결정 프레임워크 제시, Jepsen/TrueTime 언급 |
| **🚩 RED FLAG** | "CP면 C와 P를 고른 것" (P는 선택이 아님), CAP의 C를 ACID의 C와 혼동, 파티션을 "서버 다운"과 혼동 |

---

### Q10: 분산 합의 — Raft/Paxos

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Distributed Systems

**Question:**
Raft 합의 알고리즘의 leader election과 log replication 과정을 단계별로 설명하라. Paxos와 비교하여 Raft가 어떤 설계 결정을 통해 "이해 가능성(understandability)"을 높였는지 논의하라. Split-brain 방지, 네트워크 파티션 시 safety 보장, 그리고 프로덕션에서 Raft를 사용하는 시스템(etcd, CockroachDB, TiKV)의 최적화 기법을 설명하라.

---

**🧒 12살 비유:**
반 학생 5명이 학급 일지를 쓴다고 상상해. 한 명이 "반장"(Leader)이 되어 일지를 쓰고, 다른 4명에게 복사본을 나눠준다. 반장이 갑자기 아프면, 나머지 학생들이 투표로 새 반장을 뽑는다 — 이때 3명 이상(과반)이 동의해야 한다. 만약 교실이 둘로 나뉘어져 2명/3명이 되면, 3명 쪽에서만 새 반장을 뽑을 수 있다 (과반이니까). 2명 쪽은 반장을 뽑을 수 없어서 일지 쓰기를 멈춘다. 이렇게 하면 동시에 두 명이 반장인 "Split-brain" 문제가 생기지 않아.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 분산 합의가 필요한가**

분산 시스템에서 여러 노드가 동일한 상태를 유지하려면, "어떤 값을 어떤 순서로 적용할지" 합의해야 한다. 이것이 State Machine Replication (SMR) 문제다. Lamport의 Paxos(1989)가 최초의 해법이었지만, 너무 이해하기 어렵다는 비판이 있었다. 2014년 Diego Ongaro와 John Ousterhout가 Raft를 발표하며 "이해 가능성"을 설계 목표로 삼았다.

**Step 2 — 핵심 기술: Raft 동작 원리**

Raft는 합의 문제를 세 가지 독립적인 하위 문제로 분해한다:

**(1) Leader Election**
```
모든 노드 상태: Follower → Candidate → Leader

Term = 논리적 시간 단위 (단조 증가)

[Follower]
  │ election timeout (150~300ms 랜덤)
  ▼
[Candidate]
  │ 자신에게 투표 + RequestVote RPC 전송
  │
  ├─ 과반 득표 → [Leader] (heartbeat 시작)
  ├─ 다른 Leader 발견 → [Follower]
  └─ 타임아웃 → Term 증가 후 재선거
```

Safety 보장: 각 Term에서 최대 1명의 Leader (노드당 Term별 1표만 행사)

**(2) Log Replication**
```
Client → Leader: Write("x=5")
Leader: log에 entry 추가 (index=7, term=3, cmd="x=5")
Leader → Followers: AppendEntries RPC
Followers: log에 entry 추가 → ACK
Leader: 과반 ACK 수신 → commit (index 7까지)
Leader → Followers: 다음 heartbeat에 commitIndex=7 전달
Followers: commitIndex까지 state machine에 적용
```

**(3) Safety (Log Matching Property)**
- 두 로그의 같은 index에 같은 term의 entry가 있으면, 해당 index까지 모든 entry가 동일
- Leader Completeness: 한번 commit된 entry는 이후 모든 Leader의 log에 존재
- Election Restriction: 자신보다 log가 뒤처진 candidate에게 투표하지 않음

**Step 3 — 다양한 관점: Paxos vs Raft**

| 측면 | Paxos | Raft |
|------|-------|------|
| **구조** | 단일 값 합의를 반복 (Multi-Paxos) | Leader 기반 연속 로그 복제 |
| **역할** | Proposer, Acceptor, Learner (중복 가능) | Leader, Follower, Candidate (명확) |
| **Leader** | 선택적 최적화 | 필수 구성 요소 |
| **로그 구멍** | 허용 (out-of-order commit) | 불허 (연속적 commit) |
| **이해 난이도** | 매우 높음 | 낮음 (논문 목표) |
| **실용 시스템** | Chubby, Megastore | etcd, CockroachDB, TiKV, Consul |

```go
// Go — etcd의 Raft 구현 사용 (go.etcd.io/raft)
import "go.etcd.io/raft/v3"

// Raft 노드 설정
cfg := &raft.Config{
    ID:              0x01,
    ElectionTick:    10,        // election timeout = 10 * tick interval
    HeartbeatTick:   1,         // heartbeat = 1 * tick interval
    Storage:         storage,
    MaxSizePerMsg:   4096,
    MaxInflightMsgs: 256,
}
node := raft.StartNode(cfg, peers)

// 메인 루프 — Raft 상태 머신 구동
for {
    select {
    case <-ticker.C:
        node.Tick()
    case rd := <-node.Ready():
        // 1. WAL에 entries 저장
        wal.Save(rd.HardState, rd.Entries)
        // 2. 스냅샷 적용
        if !raft.IsEmptySnap(rd.Snapshot) {
            storage.ApplySnapshot(rd.Snapshot)
        }
        // 3. 네트워크로 메시지 전송
        transport.Send(rd.Messages)
        // 4. committed entries를 state machine에 적용
        for _, entry := range rd.CommittedEntries {
            applyToStateMachine(entry)
        }
        node.Advance()
    }
}
```

```python
from pysyncobj import SyncObj, replicated

class KVStore(SyncObj):
    def __init__(self, self_addr, partners):
        super().__init__(self_addr, partners)
        self._data = {}

    @replicated  # Raft log replication 자동 처리
    def set(self, key, value):
        self._data[key] = value

    def get(self, key):
        return self._data.get(key)

store = KVStore('localhost:4321', ['localhost:4322', 'localhost:4323'])
store.set('leader', 'node1')  # 과반 복제 후 commit
```

```kotlin
// Kotlin — Spring + Apache Ratis (Raft 구현)
import org.apache.ratis.protocol.RaftGroup
import org.apache.ratis.server.RaftServer

@Configuration
class RaftConfig {
    @Bean
    fun raftServer(
        @Value("\${raft.node-id}") nodeId: String,
        @Value("\${raft.peers}") peers: List<String>
    ): RaftServer {
        val properties = RaftProperties().apply {
            // Election timeout: 1~2초 (프로덕션 권장)
            setTimeDuration(
                RaftServerConfigKeys.Rpc.TIMEOUT_MIN_KEY, 1, TimeUnit.SECONDS
            )
            setTimeDuration(
                RaftServerConfigKeys.Rpc.TIMEOUT_MAX_KEY, 2, TimeUnit.SECONDS
            )
        }
        return RaftServer.newBuilder()
            .setServerId(RaftPeerId.valueOf(nodeId))
            .setGroup(buildRaftGroup(peers))
            .setStateMachine(KVStateMachine()) // 상태 머신 구현
            .setProperties(properties)
            .build()
            .also { it.start() }
    }
}
```

**Step 4 — 구체적 예시: 프로덕션 최적화 기법**

| 최적화 | 시스템 | 설명 |
|--------|--------|------|
| **Pre-vote** | etcd | 네트워크 분리된 노드가 재합류 시 불필요한 election 방지 |
| **Pipeline** | TiKV | AppendEntries를 ACK 기다리지 않고 연속 전송 |
| **Batch** | CockroachDB | 여러 client request를 하나의 log entry로 묶기 |
| **Learner** | etcd 3.4+ | 투표권 없는 노드로 데이터 복제 (읽기 확장) |
| **Joint Consensus** | Raft 논문 | 멤버십 변경 시 안전한 전환 (2-phase) |
| **Witness** | CockroachDB | 데이터 없이 투표만 하는 경량 노드 (비용 절감) |

**Step 5 — 트레이드오프 & 대안**

| 선택 | 장점 | 단점 |
|------|------|------|
| **Raft** | 이해 쉬움, 구현 검증 다수 | Leader 병목, 쓰기 지연 |
| **Multi-Paxos** | 이론적 최적, Leader 없는 변형 가능 | 구현 복잡, 버그 위험 |
| **EPaxos** | Leaderless, 낮은 지연 | 구현 극도로 복잡, 실전 검증 부족 |
| **Viewstamped Replication** | Raft와 유사, 더 오래됨 | 생태계 작음 |

Leader 병목 완화 전략:
- **Read Index**: Leader가 commit index 확인 후 follower에서 읽기
- **Lease Read**: Leader가 lease 기간 동안 로컬 읽기 (시계 의존)
- **Follower Read**: stale 허용 시 follower에서 직접 읽기

**Step 6 — 성장 & 심화**

- Raft 논문의 Figure 2 (요약 표)를 완전히 이해하면 구현 가능 수준
- TLA+ 명세를 통한 Raft 안전성 검증 (모든 가능한 상태 탐색)
- Multi-Raft: CockroachDB가 Range 단위로 독립 Raft 그룹 운영하여 확장
- Flexible Paxos (Heidi Howard): 쿼럼 교차 조건만 충족하면 과반이 아닌 쿼럼도 가능

**🎯 면접관 평가 기준:**

| 수준 | 기대 |
|------|------|
| **L6 PASS** | Leader election, log replication, commit 과정 정확히 설명. safety 속성 2개 이상 언급 |
| **L7 EXCEED** | Paxos 비교, split-brain 방지 메커니즘, 프로덕션 최적화(pre-vote, pipeline, read index), Multi-Raft 설명 |
| **🚩 RED FLAG** | "과반이면 2/5도 되나요?" (과반 = ⌊N/2⌋+1 = 3), committed와 applied 혼동, term의 역할 설명 못함 |

---

### Q11: 분산 트랜잭션 — 2PC vs SAGA vs TCC

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Distributed Systems

**Question:**
마이크로서비스 환경에서 분산 트랜잭션을 처리하는 세 가지 패턴(2PC, SAGA, TCC)을 비교하라. 각각의 일관성 보장 수준, 성능 특성, 장애 시나리오별 동작을 설명하라. 실제 e-commerce 주문 처리 시스템을 예로 들어, 왜 SAGA를 선택하고 보상 로직을 어떻게 설계하는지, Choreography와 Orchestration 방식의 트레이드오프를 포함하여 논의하라.

---

**🧒 12살 비유:**
친구들과 함께 생일 파티를 준비한다고 해 보자. **2PC**는 선생님(코디네이터)이 "케이크 준비됐어? 음료 준비됐어? 장식 준비됐어?" 하고 전부 확인한 뒤에 "시작!" 하는 것 — 한 명이라도 안 되면 전부 취소. **SAGA**는 각자 순서대로 준비하되, 중간에 실패하면 이미 한 것을 되돌리는 것 — 케이크 주문 취소, 음료 반품. **TCC**는 먼저 "예약"해 놓고(Try), 전부 예약 성공하면 "확정"(Confirm), 하나라도 실패하면 "예약 취소"(Cancel) 하는 방식이야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 분산 트랜잭션이 어려운가**

모놀리식에서는 하나의 DB 트랜잭션이 ACID를 보장한다. MSA에서는 각 서비스가 자체 DB를 가지므로(Database per Service), 여러 서비스에 걸친 비즈니스 트랜잭션의 원자성을 보장하기 어렵다. 네트워크 실패, 부분 실패, 메시지 유실 등의 문제가 추가된다.

**Step 2 — 핵심 기술: 세 패턴 비교**

| 속성 | 2PC | SAGA | TCC |
|------|-----|------|-----|
| **일관성** | Strong (ACID) | Eventual (BASE) | Eventual (예약→확정) |
| **격리성** | 전체 락 | 없음 (dirty read 가능) | Try 단계에서 자원 예약 |
| **가용성** | 낮음 (코디네이터 SPOF) | 높음 | 중간 |
| **성능** | 느림 (동기 블로킹) | 빠름 (비동기) | 중간 |
| **복잡도** | 낮음 (DB 지원) | 보상 로직 필요 | Try/Confirm/Cancel 3벌 |
| **적합 사례** | 단일 DB 벤더, 짧은 트랜잭션 | 장기 실행, MSA 간 | 금융, 재고 예약 |

**(1) 2PC (Two-Phase Commit)**
```
Phase 1 — Prepare:
  Coordinator → Participants: "PREPARE"
  Participants: 로컬 트랜잭션 실행 (commit 안 함), WAL 기록 → "VOTE YES/NO"

Phase 2 — Commit/Abort:
  모두 YES → Coordinator: "COMMIT" → Participants: commit
  하나라도 NO → Coordinator: "ABORT" → Participants: rollback
```

문제점: Coordinator 장애 시 participants가 PREPARED 상태에서 영원히 블로킹 (blocking protocol)

**(2) SAGA 패턴**
```
정방향: T1 → T2 → T3 → ... → Tn (각각 로컬 트랜잭션)
보상:   C1 ← C2 ← C3 ← ... ← Ci (Ti+1 실패 시 역순 보상)
```

**(3) TCC (Try-Confirm-Cancel)**
```
Try:     각 서비스에서 자원 예약 (재고 -5 → reserved +5)
Confirm: 예약 확정 (reserved -5, 실제 차감 완료)
Cancel:  예약 취소 (reserved -5 → 재고 +5)
```

**Step 3 — 다양한 관점: 스택별 SAGA 구현**

```python
from temporalio import workflow, activity
from temporalio.common import RetryPolicy
from dataclasses import dataclass

@dataclass
class OrderSagaInput:
    order_id: str
    user_id: str
    items: list
    total_amount: float

@activity.defn
async def reserve_inventory(order_id: str, items: list) -> dict:
    """Step 1: 재고 예약"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{INVENTORY_URL}/reserve",
            json={"order_id": order_id, "items": items}
        )
        resp.raise_for_status()
        return resp.json()

@activity.defn
async def process_payment(order_id: str, amount: float) -> dict:
    """Step 2: 결제 처리"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{PAYMENT_URL}/charge",
            json={"order_id": order_id, "amount": amount}
        )
        resp.raise_for_status()
        return resp.json()

@activity.defn
async def compensate_inventory(order_id: str, items: list):
    """보상: 재고 예약 취소"""
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{INVENTORY_URL}/release",
            json={"order_id": order_id, "items": items}
        )

@workflow.defn
class OrderSagaWorkflow:
    @workflow.run
    async def run(self, input: OrderSagaInput) -> dict:
        retry = RetryPolicy(maximum_attempts=3)

        # Step 1: 재고 예약
        inv_result = await workflow.execute_activity(
            reserve_inventory, args=[input.order_id, input.items],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )

        # Step 2: 결제 — 실패 시 재고 보상
        try:
            pay_result = await workflow.execute_activity(
                process_payment, args=[input.order_id, input.total_amount],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry,
            )
        except Exception as e:
            # 보상 트랜잭션: 재고 예약 취소
            await workflow.execute_activity(
                compensate_inventory, args=[input.order_id, input.items],
                start_to_close_timeout=timedelta(seconds=30),
            )
            raise  # 워크플로우 실패 전파

        return {"order_id": input.order_id, "status": "COMPLETED"}
```

```go
// Go — SAGA Choreography (이벤트 기반)
// 각 서비스가 이벤트를 발행하고, 다음 서비스가 구독

type OrderEvent struct {
    OrderID   string    `json:"order_id"`
    EventType string    `json:"event_type"` // CREATED, INVENTORY_RESERVED, PAYMENT_COMPLETED, ...
    Payload   []byte    `json:"payload"`
    Timestamp time.Time `json:"timestamp"`
}

// Inventory Service — 이벤트 핸들러
func (s *InventoryService) HandleOrderCreated(ctx context.Context, event OrderEvent) error {
    // 재고 예약 시도
    err := s.reserveStock(ctx, event.OrderID, event.Payload)
    if err != nil {
        // 실패 → 보상 이벤트 발행
        return s.publisher.Publish(ctx, OrderEvent{
            OrderID:   event.OrderID,
            EventType: "INVENTORY_RESERVATION_FAILED",
            Timestamp: time.Now(),
        })
    }
    // 성공 → 다음 단계 이벤트 발행
    return s.publisher.Publish(ctx, OrderEvent{
        OrderID:   event.OrderID,
        EventType: "INVENTORY_RESERVED",
        Timestamp: time.Now(),
    })
}

// Payment Service — 보상 핸들러
func (s *PaymentService) HandlePaymentFailed(ctx context.Context, event OrderEvent) error {
    // 이미 결제된 것이 있으면 환불
    if charged, _ := s.repo.FindCharge(ctx, event.OrderID); charged != nil {
        return s.refund(ctx, charged)
    }
    return nil // 멱등성: 결제 안 했으면 아무것도 안 함
}
```

```kotlin
// Kotlin/Spring — SAGA Orchestrator (Axon Framework)
@Saga
class OrderSaga {

    @Autowired @Transient
    private lateinit var commandGateway: CommandGateway

    private lateinit var orderId: String
    private var inventoryReserved = false
    private var paymentProcessed = false

    @StartSaga
    @SagaEventHandler(associationProperty = "orderId")
    fun on(event: OrderCreatedEvent) {
        orderId = event.orderId
        // Step 1: 재고 예약 커맨드
        commandGateway.send<Any>(
            ReserveInventoryCommand(orderId, event.items)
        )
    }

    @SagaEventHandler(associationProperty = "orderId")
    fun on(event: InventoryReservedEvent) {
        inventoryReserved = true
        // Step 2: 결제 커맨드
        commandGateway.send<Any>(
            ProcessPaymentCommand(orderId, event.totalAmount)
        )
    }

    @SagaEventHandler(associationProperty = "orderId")
    fun on(event: PaymentCompletedEvent) {
        paymentProcessed = true
        // 모든 단계 성공 → 주문 확정
        commandGateway.send<Any>(ConfirmOrderCommand(orderId))
        SagaLifecycle.end()
    }

    // 보상 로직
    @SagaEventHandler(associationProperty = "orderId")
    fun on(event: PaymentFailedEvent) {
        // 결제 실패 → 재고 예약 취소 (보상)
        if (inventoryReserved) {
            commandGateway.send<Any>(
                ReleaseInventoryCommand(orderId)
            )
        }
        commandGateway.send<Any>(RejectOrderCommand(orderId, event.reason))
        SagaLifecycle.end()
    }

    @SagaEventHandler(associationProperty = "orderId")
    fun on(event: InventoryReservationFailedEvent) {
        // 재고 부족 → 주문 거절 (보상할 것 없음)
        commandGateway.send<Any>(
            RejectOrderCommand(orderId, "Insufficient inventory")
        )
        SagaLifecycle.end()
    }
}
```

**Step 4 — 구체적 예시: 보상 로직 설계 원칙**

```
E-commerce 주문 SAGA:

정방향:  주문 생성 → 재고 예약 → 결제 → 배송 요청 → 완료
보상:    주문 취소 ← 재고 복원 ← 환불   ← 배송 취소

핵심 원칙:
1. 보상은 "의미적 되돌리기" (물리적 undo 아님)
   - 결제 보상 = 환불 (새 트랜잭션), delete가 아님
   - 재고 보상 = 재고 +N (reserved 해제)

2. 멱등성 필수: 보상이 2번 실행되어도 안전
   - compensation_id로 중복 체크
   - 상태 머신으로 전이 관리

3. 역순 실행: 마지막 성공 단계부터 역순으로 보상
   - T1 → T2 → T3(실패) → C2 → C1

4. Pivot Transaction: 되돌릴 수 없는 단계 식별
   - 외부 결제 API 호출 = pivot (환불은 가능하지만 다른 트랜잭션)
   - pivot 이전에 가능한 많은 검증 수행
```

Choreography vs Orchestration:

| 측면 | Choreography | Orchestration |
|------|-------------|---------------|
| **결합도** | 느슨 (이벤트만 알면 됨) | 오케스트레이터에 집중 |
| **가시성** | 낮음 (흐름 추적 어려움) | 높음 (중앙에서 전체 보임) |
| **복잡도** | 서비스 수 증가 시 이벤트 폭발 | 오케스트레이터 복잡도 증가 |
| **장애 대응** | 분산 보상 (어려움) | 중앙 보상 (쉬움) |
| **적합** | 3-4개 서비스, 단순 흐름 | 5+ 서비스, 복잡한 흐름 |
| **도구** | Kafka, RabbitMQ | Temporal, Cadence, Axon |

**Step 5 — 트레이드오프 & 대안**

SAGA의 격리성 문제와 대응:

| 문제 | 설명 | 해결책 |
|------|------|--------|
| **Lost Update** | 다른 SAGA가 보상 중 데이터 덮어씀 | Semantic Lock (상태 필드: PENDING) |
| **Dirty Read** | 보상될 데이터를 다른 SAGA가 읽음 | Commutative Update (절대값 대신 delta) |
| **Fuzzy Read** | 같은 데이터를 두 번 읽으면 다른 값 | Version 체크 (Optimistic Lock) |

```
Semantic Lock 예시:
  order.status = "PENDING_PAYMENT"  (SAGA 진행 중)
  → 다른 SAGA가 이 주문을 수정 시도하면 거부
  order.status = "CONFIRMED"        (SAGA 완료 후)
```

**Step 6 — 성장 & 심화**

- Temporal의 Workflow Replay 메커니즘: deterministic execution으로 정확한 재실행
- SAGA의 격리성 향상: Garcia-Molina의 원 논문(1987)에서 countermeasures 패턴 제안
- Distributed Sagas (Caitie McCaffrey, 2015): SAGA를 분산 시스템에 적용한 실전 사례
- TCC의 변형: AT (Automatic Transaction) 모드 — Seata 프레임워크가 SQL 파싱으로 자동 보상 생성

**🎯 면접관 평가 기준:**

| 수준 | 기대 |
|------|------|
| **L6 PASS** | 2PC/SAGA 차이 명확히 설명, 보상 로직 설계, Choreography vs Orchestration 비교 |
| **L7 EXCEED** | 격리성 문제(lost update, dirty read)와 해결책, TCC 설명, Temporal/Axon 같은 프레임워크 경험, pivot transaction 개념 |
| **🚩 RED FLAG** | SAGA가 ACID를 보장한다고 주장, 보상 = rollback이라고 설명, 멱등성 고려 없이 보상 설계 |

---

### Q12: 분산 시계 — Lamport/Vector/HLC

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Distributed Systems

**Question:**
분산 시스템에서 물리적 시계에 의존할 수 없는 이유를 설명하고, Lamport Clock, Vector Clock, Hybrid Logical Clock (HLC)의 동작 원리와 한계를 비교하라. 각각이 어떤 인과 관계(causality)를 포착할 수 있고 어떤 것을 포착할 수 없는지 명확히 구분하라. 실제 시스템(Dynamo, CockroachDB, Spanner)에서 시계 문제를 어떻게 해결하는지 설명하라.

---

**🧒 12살 비유:**
세 친구가 각각 다른 나라에 살면서 편지를 주고받는다고 해 보자. 각자 벽시계가 있는데, 시간이 조금씩 다르다. "내가 먼저 보냈어!"라고 싸우면 해결할 수 없어. 그래서 **Lamport Clock**은 편지를 받을 때마다 "상대방 시계와 내 시계 중 큰 것 + 1"로 맞추는 규칙이야 — 순서는 알 수 있지만, 두 편지가 동시인지는 모른다. **Vector Clock**은 각자가 "모든 친구의 시계"를 기록하는 것 — "영희 시계=3, 철수 시계=5, 나 시계=7". 이러면 동시 사건도 구분할 수 있어. **HLC**는 "물리 시계 + 논리 카운터"를 합쳐서, 실제 시간에 가까우면서도 인과 순서를 보장하는 절충안이야.

**📋 단계별 답변:**

**Step 1 — 맥락: 물리적 시계의 한계**

분산 시스템에서 물리적 시계(wall clock)에 의존할 수 없는 이유:

1. **Clock Skew**: NTP 동기화는 수십ms~수백ms 오차 (인터넷), 수십us~수ms (데이터센터)
2. **Clock Drift**: 수정 발진기는 10^-6 수준으로 표류 (하루 ~86ms)
3. **비단조성**: NTP 스텝 조정 시 시간이 되감길 수 있음
4. **장애**: NTP 서버 불가용, leap second 처리 오류

Leslie Lamport의 1978년 논문 "Time, Clocks, and the Ordering of Events in a Distributed System"이 이 문제의 근본적 해법을 제시했다.

**Step 2 — 핵심 기술: 세 가지 논리적 시계**

**(1) Lamport Clock (1978)**

규칙:
```
1. 내부 이벤트: LC = LC + 1
2. 메시지 전송: LC = LC + 1, 메시지에 LC 첨부
3. 메시지 수신: LC = max(LC_local, LC_msg) + 1

속성:
- e → f (e happens-before f) ⇒ LC(e) < LC(f)      [참]
- LC(e) < LC(f) ⇒ e → f                             [거짓 — 역은 성립 안 함!]
- 동시 사건(concurrent) 구분 불가
```

**(2) Vector Clock (Fidge-Mattern, 1988)**

규칙:
```
N개 노드 → 벡터 크기 N
노드 i의 벡터: VC_i = [c1, c2, ..., cN]

1. 내부 이벤트: VC_i[i] += 1
2. 메시지 전송: VC_i[i] += 1, 메시지에 VC_i 첨부
3. 메시지 수신: VC_i = pointwise_max(VC_i, VC_msg); VC_i[i] += 1

비교:
VC(a) <= VC(b) iff 모든 k에 대해 VC(a)[k] <= VC(b)[k]
VC(a) < VC(b) iff VC(a) <= VC(b) 그리고 VC(a) != VC(b) → a happens-before b
VC(a) || VC(b) iff 어느 쪽도 <= 아님 → concurrent!

속성:
- e → f iff VC(e) < VC(f)                            [양방향!]
- 동시 사건 완벽 구분                                  [참]
- 벡터 크기 = O(N) → 수천 노드에서 비효율              [단점]
```

**(3) Hybrid Logical Clock — HLC (Kulkarni et al., 2014)**

```
HLC = (l, c) where:
l  = 지금까지 본 가장 큰 physical time
c  = 같은 l 내에서의 논리적 카운터

규칙:
1. 로컬/전송 이벤트:
   if pt > l: l = pt, c = 0
   else: c += 1

2. 수신 이벤트 (msg에서 l_msg, c_msg):
   if pt > l and pt > l_msg: l = pt, c = 0
   elif l == l_msg: l = l, c = max(c, c_msg) + 1
   elif l > l_msg: c += 1
   else: l = l_msg, c = c_msg + 1

속성:
- 인과 순서 보장 (Lamport Clock처럼)          [참]
- 물리 시간에 근접 (|l - pt| <= epsilon)      [참]
- 크기 고정 (벡터 불필요)                      [참]
- 동시 사건 구분 불가 (Lamport 한계 동일)      [단점]
```

**Step 3 — 다양한 관점: 스택별 구현**

```python
from dataclasses import dataclass, field
from threading import Lock

@dataclass
class LamportClock:
    """Thread-safe Lamport Clock"""
    _counter: int = 0
    _lock: Lock = field(default_factory=Lock)

    def tick(self) -> int:
        """내부 이벤트"""
        with self._lock:
            self._counter += 1
            return self._counter

    def send(self) -> int:
        """메시지 전송 시 호출"""
        return self.tick()

    def receive(self, msg_timestamp: int) -> int:
        """메시지 수신 시 호출"""
        with self._lock:
            self._counter = max(self._counter, msg_timestamp) + 1
            return self._counter

    @property
    def value(self) -> int:
        return self._counter


@dataclass
class VectorClock:
    node_id: str
    _clock: dict = field(default_factory=dict)

    def tick(self):
        self._clock[self.node_id] = self._clock.get(self.node_id, 0) + 1

    def send(self) -> dict:
        self.tick()
        return dict(self._clock)

    def receive(self, msg_clock: dict):
        for node, ts in msg_clock.items():
            self._clock[node] = max(self._clock.get(node, 0), ts)
        self.tick()

    def happens_before(self, other: dict) -> bool:
        """self < other (self happens-before other)"""
        all_keys = set(self._clock.keys()) | set(other.keys())
        at_least_one_less = False
        for k in all_keys:
            if self._clock.get(k, 0) > other.get(k, 0):
                return False
            if self._clock.get(k, 0) < other.get(k, 0):
                at_least_one_less = True
        return at_least_one_less

    def is_concurrent(self, other: 'VectorClock') -> bool:
        """동시 사건인지 판별"""
        return (not self.happens_before(other._clock)
                and not other.happens_before(self._clock))
```

```go
// Go — HLC 구현 (CockroachDB 스타일)
import (
    "sync"
    "time"
)

type Timestamp struct {
    WallTime int64
    Logical  int32
}

func (t Timestamp) Less(o Timestamp) bool {
    return t.WallTime < o.WallTime ||
        (t.WallTime == o.WallTime && t.Logical < o.Logical)
}

type HLC struct {
    mu        sync.Mutex
    maxOffset time.Duration
    wallTime  int64 // l
    logical   int32 // c
}

func NewHLC(maxOffset time.Duration) *HLC {
    return &HLC{maxOffset: maxOffset}
}

func (h *HLC) Now() Timestamp {
    h.mu.Lock()
    defer h.mu.Unlock()

    pt := time.Now().UnixNano()
    if pt > h.wallTime {
        h.wallTime = pt
        h.logical = 0
    } else {
        h.logical++
    }
    return Timestamp{WallTime: h.wallTime, Logical: h.logical}
}

func (h *HLC) Update(msg Timestamp) Timestamp {
    h.mu.Lock()
    defer h.mu.Unlock()

    pt := time.Now().UnixNano()
    if pt > h.wallTime && pt > msg.WallTime {
        h.wallTime = pt
        h.logical = 0
    } else if h.wallTime == msg.WallTime {
        if msg.Logical > h.logical {
            h.logical = msg.Logical + 1
        } else {
            h.logical++
        }
    } else if h.wallTime > msg.WallTime {
        h.logical++
    } else {
        h.wallTime = msg.WallTime
        h.logical = msg.Logical + 1
    }

    // Clock skew 감지: |l - pt| > maxOffset이면 거부
    if h.wallTime-pt > int64(h.maxOffset) {
        panic("clock skew exceeds maximum offset")
    }
    return Timestamp{WallTime: h.wallTime, Logical: h.logical}
}
```

```kotlin
// Kotlin — Vector Clock (Dynamo 스타일 충돌 감지)
data class VectorClock(
    private val clock: MutableMap<String, Long> = mutableMapOf()
) {
    fun increment(nodeId: String): VectorClock {
        clock[nodeId] = (clock[nodeId] ?: 0) + 1
        return this
    }

    fun merge(other: VectorClock): VectorClock {
        val merged = mutableMapOf<String, Long>()
        val allKeys = clock.keys + other.clock.keys
        for (key in allKeys) {
            merged[key] = maxOf(clock[key] ?: 0, other.clock[key] ?: 0)
        }
        return VectorClock(merged)
    }

    fun dominates(other: VectorClock): Boolean {
        val allKeys = clock.keys + other.clock.keys
        var atLeastOneGreater = false
        for (key in allKeys) {
            val mine = clock[key] ?: 0
            val theirs = other.clock[key] ?: 0
            if (mine < theirs) return false
            if (mine > theirs) atLeastOneGreater = true
        }
        return atLeastOneGreater
    }

    fun isConcurrent(other: VectorClock): Boolean =
        !this.dominates(other) && !other.dominates(this)
}

// 사용: Dynamo 스타일 읽기 충돌 해결
@Service
class DynamoStyleStore(private val replicas: List<ReplicaClient>) {
    fun get(key: String): Pair<ByteArray, VectorClock> {
        val responses = replicas.map { it.get(key) }
        val latest = responses.maxByOrNull { it.vectorClock.clock.values.sum() }!!

        val conflicts = responses.filter {
            it.vectorClock.isConcurrent(latest.vectorClock)
        }
        if (conflicts.size > 1) {
            throw ConflictException(siblings = responses)
        }
        return latest.value to latest.vectorClock
    }
}
```

**Step 4 — 구체적 예시: 실제 시스템의 시계 선택**

| 시스템 | 시계 | 이유 |
|--------|------|------|
| **Amazon DynamoDB** | Vector Clock (초기) → 서버측 LWW | 클라이언트 충돌 해결이 너무 복잡 |
| **Cassandra** | LWW + 물리 시계 | 단순성 우선, NTP 의존 (데이터 유실 가능) |
| **CockroachDB** | HLC | 인과 순서 + 물리 시간 근접, max offset으로 skew 제한 |
| **Google Spanner** | TrueTime (GPS + 원자시계) | 불확실성 구간 [earliest, latest], commit-wait |
| **Riak** | Dotted Version Vectors | Vector Clock의 sibling explosion 해결 |

Spanner의 TrueTime:
```
TrueTime.now() → TTinterval { earliest, latest }
불확실성: epsilon = latest - earliest (보통 ~7ms)

Commit-wait: commit 후 epsilon만큼 대기
→ 이후 트랜잭션이 반드시 더 큰 timestamp
→ External consistency (linearizability보다 강한 보장)
```

**Step 5 — 트레이드오프 & 대안**

| 시계 | 크기 | 인과 추적 | 동시 감지 | 물리 시간 | 적합 |
|------|------|-----------|-----------|-----------|------|
| Lamport | O(1) | 부분적 | 불가 | 무관 | 전순서 필요 시 |
| Vector | O(N) | 완전 | 가능 | 무관 | N이 작은 시스템 |
| HLC | O(1) | 부분적 | 불가 | 근접 | 대규모 분산 DB |
| TrueTime | O(1) | 물리적 | 불가 | 정확 | 전용 하드웨어 |

**Step 6 — 성장 & 심화**

- Interval Tree Clocks (ITC): Vector Clock의 동적 노드 추가/제거 문제 해결
- Bloom Clock: 확률적 인과 추적, O(1) 크기 + 동시 사건 감지 (false positive 존재)
- CockroachDB의 Uncertainty Interval: HLC max offset 기반 불확실 구간 처리
- Logical Physical Clock (LPC): HLC 변형, bounded skew 없이도 동작

**🎯 면접관 평가 기준:**

| 수준 | 기대 |
|------|------|
| **L6 PASS** | Lamport/Vector Clock 동작 원리, happens-before 관계, 물리 시계의 한계 설명 |
| **L7 EXCEED** | HLC 설명, TrueTime의 commit-wait, Vector Clock 크기 문제와 대안, 실제 시스템 비교 |
| **🚩 RED FLAG** | Lamport Clock으로 동시 사건 감지 가능하다고 주장, Vector Clock 비교 규칙 틀림, "NTP면 충분하다" |

---

### Q13: 일관성 모델 — Linearizability vs Sequential vs Eventual

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Distributed Systems

**Question:**
Linearizability, Sequential Consistency, Causal Consistency, Eventual Consistency를 정의하고, 각 모델이 보장하는 것과 허용하는 이상 현상(anomaly)을 구체적으로 설명하라. Session Guarantees(Read Your Writes, Monotonic Reads 등)가 어떻게 Eventual Consistency를 보완하는지, 그리고 실제 시스템(ZooKeeper, DynamoDB, Cassandra)이 어떤 일관성 모델을 제공하는지 프로덕션 관점에서 논의하라.

---

**🧒 12살 비유:**
칠판이 3개 있고 선생님들이 각각 하나씩 관리한다고 생각해. **Linearizability**는 세 칠판이 항상 "한 칠판처럼" 보이는 것 — 누군가 "5"를 쓰면 그 순간부터 모든 칠판에서 "5"가 보여. **Sequential Consistency**는 모든 학생이 같은 순서로 변화를 보지만, 실시간은 아닐 수 있어 — 영희가 쓴 것이 철수가 쓴 것보다 나중에 보일 수도. **Eventual Consistency**는 "언젠가는 모든 칠판이 같아질 거야"라는 약속 — 하지만 중간에 다른 값이 보일 수 있어. **Read Your Writes**는 "내가 쓴 건 적어도 나한테는 바로 보여!"라는 추가 약속이야.

**📋 단계별 답변:**

**Step 1 — 맥락: 일관성 모델의 계층 구조**

```
강함 ←───────────────────────────────────────── 약함
Strict → Linearizable → Sequential → Causal → Eventual

Strict:          물리적 시간 순서 정확히 반영 (불가능)
Linearizable:    실시간 순서 + 원자적 (가능하지만 비쌈)
Sequential:      프로그램 순서 보존, 실시간 보장 없음
Causal:          인과 관계만 보존
Eventual:        결국 수렴, 중간 불일치 허용
```

**Step 2 — 핵심 기술: 각 모델 상세**

**(1) Linearizability (강한 일관성)**
- 모든 연산이 invocation과 response 사이의 어떤 시점에 원자적으로 실행된 것처럼 보임
- 실시간 순서 보존: op1이 op2보다 먼저 완료되면, op1이 먼저 적용
- Herlihy & Wing (1990) 정의

```
Client A:  |--write(x=1)--|
Client B:       |--read(x)--|  → 반드시 1 반환
Client C:              |--read(x)--|  → 반드시 1 반환

위반 예: Client B가 read(x)=0 반환 (write가 완료된 후인데도)
```

**(2) Sequential Consistency**
- 모든 프로세스의 연산이 어떤 전역 순서로 실행된 것처럼 보임
- 각 프로세스 내의 프로그램 순서(program order)는 보존
- 실시간 순서 보장 없음

```
Client A: write(x=1)          write(x=3)
Client B:          write(x=2)

Sequential에서 유효한 순서들:
  w(x=1) → w(x=2) → w(x=3)  [유효]
  w(x=2) → w(x=1) → w(x=3)  [유효]
  w(x=1) → w(x=3) → w(x=2)  [무효: A의 program order 위반]
```

**(3) Causal Consistency**
- 인과적으로 관련된 연산만 순서 보존
- 인과 무관(concurrent) 연산은 다른 순서로 볼 수 있음

```
Client A: write(x=1)
Client B: read(x)=1 → write(y=2)  // x=1을 본 후 y=2를 썼으므로 인과적
Client C: read(y)=2 → read(x)     // y=2를 봤으면 x=1도 반드시 보여야 함
```

**(4) Eventual Consistency + Session Guarantees**

| Guarantee | 보장 | 위반 시 문제 |
|-----------|------|-------------|
| **Read Your Writes** | 자신이 쓴 값을 반드시 읽음 | 프로필 수정 후 이전 값 보임 |
| **Monotonic Reads** | 한번 본 값보다 이전 값 안 봄 | 새로고침마다 다른 값 |
| **Monotonic Writes** | 같은 클라이언트 쓰기 순서 보존 | 이메일 순서 뒤바뀜 |
| **Writes Follow Reads** | 읽은 값에 의존하는 쓰기 인과 보존 | 댓글이 원글보다 먼저 |

**Step 3 — 다양한 관점: 스택별 구현**

```python
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('user_profiles')

def get_profile_fast(user_id: str) -> dict:
    response = table.get_item(
        Key={'user_id': user_id},
        ConsistentRead=False  # eventual
    )
    return response.get('Item', {})

def get_profile_consistent(user_id: str) -> dict:
    response = table.get_item(
        Key={'user_id': user_id},
        ConsistentRead=True   # linearizable
    )
    return response.get('Item', {})

def update_and_read(user_id: str, updates: dict) -> dict:
    table.update_item(
        Key={'user_id': user_id},
        UpdateExpression="SET #n = :n",
        ExpressionAttributeNames={'#n': 'name'},
        ExpressionAttributeValues={':n': updates['name']},
    )
    return get_profile_consistent(user_id)  # 직후엔 strong read
```

```go
// Go — Cassandra Tunable Consistency
import "github.com/gocql/gocql"

func setupSession() *gocql.Session {
    cluster := gocql.NewCluster("node1", "node2", "node3")
    cluster.Keyspace = "myapp"
    cluster.Consistency = gocql.Quorum // 기본
    session, _ := cluster.CreateSession()
    return session
}

// Linearizable: SERIAL (Paxos 기반 Cassandra LWT)
func getLinearizable(session *gocql.Session, key string) (string, error) {
    var value string
    query := session.Query("SELECT value FROM kv WHERE key = ?", key)
    query.SerialConsistency(gocql.Serial)
    err := query.Scan(&value)
    return value, err
}

// Eventual: ONE (가장 가까운 replica)
func getEventual(session *gocql.Session, key string) (string, error) {
    var value string
    query := session.Query("SELECT value FROM kv WHERE key = ?", key)
    query.Consistency(gocql.One)
    err := query.Scan(&value)
    return value, err
}

// Quorum으로 tunable strong consistency
// R + W > N → strong consistency 보장
// QUORUM read + QUORUM write (RF=3: R=2, W=2 → 2+2 > 3)
func getQuorum(session *gocql.Session, key string) (string, error) {
    var value string
    query := session.Query("SELECT value FROM kv WHERE key = ?", key)
    query.Consistency(gocql.Quorum)
    err := query.Scan(&value)
    return value, err
}
```

```kotlin
// Kotlin/Spring — ZooKeeper 일관성 모델 활용
import org.apache.curator.framework.CuratorFramework

@Service
class ConfigService(private val curator: CuratorFramework) {

    // ZooKeeper: Sequential Consistency (기본 읽기)
    // 쓰기는 leader를 통해 전역 순서, 읽기는 follower에서 가능 (stale 가능)
    fun getConfig(path: String): ByteArray? {
        return curator.data.forPath(path)
    }

    // Linearizable Read: sync() 후 읽기
    fun getConfigLinearizable(path: String): ByteArray? {
        curator.sync().forPath(path)  // leader와 동기화
        return curator.data.forPath(path)
    }

    // Read Your Writes: ZooKeeper는 같은 세션 내 자동 보장
    fun updateAndRead(path: String, data: ByteArray): ByteArray {
        curator.setData().forPath(path, data)
        return curator.data.forPath(path)  // 같은 세션 → 자신의 쓰기 보장
    }

    // Watch 기반: Causal Consistency에 가까운 패턴
    fun watchConfig(path: String, onChange: (ByteArray) -> Unit) {
        val cache = org.apache.curator.framework.recipes.cache
            .CuratorCache.build(curator, path)
        cache.listenable().addListener { _, _, data ->
            onChange(data.data)
        }
        cache.start()
    }
}
```

**Step 4 — 구체적 예시: 실제 시스템의 일관성 모델**

| 시스템 | 기본 모델 | 조정 가능 | 특이 사항 |
|--------|-----------|-----------|-----------|
| **ZooKeeper** | Sequential | sync()로 linearizable | 쓰기는 항상 linearizable |
| **etcd** | Linearizable | WithSerializable()로 sequential | Raft 기반 |
| **DynamoDB** | Eventual | ConsistentRead=True → strong | 단일 항목만 |
| **Cassandra** | Eventual | QUORUM/SERIAL로 조정 | LWT로 linearizable |
| **Spanner** | External Consistency | - | Linearizability보다 강함 |
| **MongoDB** | Read Your Writes | readConcern/writeConcern | causal session (4.0+) |

**Step 5 — 트레이드오프 & 대안**

일관성-성능 트레이드오프 정량화:

```
지연 (3-region 배포 기준):
  Linearizable read: ~50ms (cross-region RTT)
  Sequential read:   ~1ms  (local follower)
  Eventual read:     ~1ms  (local replica)
```

| 모델 | 가용성 | 지연 | 적합 |
|------|--------|------|------|
| Linearizable | 낮음 | 높음 | 금융, 결제 |
| Sequential | 중간 | 낮음 | 메타데이터, 설정 |
| Causal | 높음 | 낮음 | 소셜, 협업 |
| Eventual | 최고 | 최저 | 캐시, 피드, 로그 |

**Step 6 — 성장 & 심화**

- SNOW 정리 (Lu et al., 2016): Strict Serializability + Nonblocking + One response + Write-conflict-free — 4개 중 3개만 가능
- PBS (Probabilistically Bounded Staleness): eventual consistency에서 stale 확률 정량화
- Bolt-on Causal Consistency (Bailis et al., 2013): eventual consistency 위에 causal 구축
- RedBlue Consistency: 작업을 red(강한 일관성)와 blue(약한 일관성)로 분류

**🎯 면접관 평가 기준:**

| 수준 | 기대 |
|------|------|
| **L6 PASS** | Linearizability vs Eventual 차이, Session Guarantees 2개 이상 설명, 실제 시스템 매핑 |
| **L7 EXCEED** | Sequential vs Linearizable 정확한 구분, Causal Consistency 설명, tunable consistency 정량화 |
| **🚩 RED FLAG** | "Strong = Linearizable = Sequential" 혼동, Session Guarantee 모름, "Eventual이면 데이터가 틀린다"고만 설명 |

---

### Q14: 분산 락 — Redlock 논쟁과 Fencing Token

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Distributed Systems

**Question:**
분산 환경에서 상호 배제(mutual exclusion)를 보장하는 분산 락의 필요성과 구현 방법을 설명하라. Redis 단일 인스턴스 락의 한계, Redlock 알고리즘의 동작 원리, 그리고 Martin Kleppmann과 Antirez 간의 유명한 Redlock 논쟁을 양측 입장에서 설명하라. Fencing Token이 왜 필요하고 어떻게 동작하는지, lease-based 락과 비교하여 논의하라.

---

**🧒 12살 비유:**
화장실이 하나인데 여러 사람이 쓰려면 문을 잠그고 들어가야 해. 열쇠가 하나면 간단한데, 열쇠를 여러 개 만들면 문제가 생길 수 있어. **Redlock**은 5개 열쇠함 중 3개 이상에서 열쇠를 받아야 입장하는 방식이야. 그런데 Martin Kleppmann은 "화장실 안에서 잠이 들면(GC pause) 열쇠가 만료되어도 나는 모르잖아! 다른 사람이 들어올 수 있어!"라고 비판했어. 해결책은 **Fencing Token** — 출입증에 번호를 매기고, 번호가 더 큰 사람만 변기를 내릴 수 있게 하는 거야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 분산 락이 필요한가**

두 가지 목적:
1. **Efficiency (효율성)**: 같은 작업을 두 번 하지 않기 위해 (예: 중복 결제 방지)
2. **Correctness (정확성)**: 동시 접근으로 인한 데이터 손상 방지 (예: 잔액 차감)

단일 노드 락(mutex)은 프로세스 크래시 시 락이 영원히 유지되거나 유실된다. 분산 락은 여러 노드/프로세스 간 상호 배제를 보장해야 한다.

**Step 2 — 핵심 기술: 구현 방식들**

**(1) Redis 단일 인스턴스 락**
```
SET lock_key unique_value NX PX 30000

if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
end
```

한계: Redis 마스터 장애 시 failover에서 락 유실 (비동기 복제)

**(2) Redlock 알고리즘 (Salvatore Sanfilippo, 2015)**
```
N = 5 독립 Redis 인스턴스 (복제 없음)
과반 = floor(N/2) + 1 = 3

1. 현재 시각 T1 기록
2. 5개 인스턴스 모두에 SET NX PX 시도 (짧은 타임아웃)
3. 과반(3+)에서 성공 AND 경과 시간 < TTL이면 락 획득
4. 유효 시간 = TTL - (T2 - T1) - clock drift 보정
5. 실패 시: 모든 인스턴스에서 DEL (cleanup)
```

**(3) Kleppmann vs Antirez 논쟁**

Kleppmann의 비판 ("How to do distributed locking", 2016):

```
Client 1이 Redlock으로 락 획득 (TTL = 30s)
    |
    +-- GC pause / 네트워크 지연이 30초 이상 발생
    |
    +-- 락 만료 (Client 1은 모름)
    |
    +-- Client 2가 같은 락 획득
    → 두 클라이언트가 동시에 "보호 영역" 접근!

핵심 주장:
1. 실시간 시계에 의존하는 알고리즘은 GC pause, 네트워크 지연에 취약
2. 정확성(correctness)이 필요하면 fencing token 필수
3. 효율성만 필요하면 단일 Redis로 충분
4. 정확성이 필요하면 ZooKeeper/etcd (합의 기반) 사용
```

Antirez의 반박:
```
1. GC pause가 30초 이상? 현실적이지 않음
2. Redlock의 clock drift 보정이 이를 완화
3. 합의 기반 시스템도 클라이언트 GC pause에 동일하게 취약
4. 실용적 관점에서 Redlock은 충분히 안전
```

**(4) Fencing Token**
```
Fencing Token = 단조 증가하는 숫자

Client 1: 락 획득 → token=33 → (GC pause) → write(data, token=33)
Client 2: 락 획득 → token=34 → write(data, token=34)

Storage: token=34 수신 후 → token=33 거부 (stale token)

핵심: 저장소가 fencing token을 검증해야 → 저장소 측 지원 필요
```

**Step 3 — 다양한 관점: 스택별 구현**

```python
import redis
import uuid
from contextlib import contextmanager

class DistributedLock:
    def __init__(self, redis_client: redis.Redis, key: str, ttl_ms: int = 30000):
        self.redis = redis_client
        self.key = f"lock:{key}"
        self.fence_key = f"fence:{key}"
        self.ttl_ms = ttl_ms
        self.value = str(uuid.uuid4())

    def acquire(self) -> int | None:
        """락 획득 → fencing token 반환"""
        acquired = self.redis.set(
            self.key, self.value, nx=True, px=self.ttl_ms
        )
        if not acquired:
            return None
        token = self.redis.incr(self.fence_key)
        return token

    def release(self):
        """Lua로 원자적 해제"""
        lua = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else return 0 end
        """
        self.redis.eval(lua, 1, self.key, self.value)

    @contextmanager
    def hold(self):
        token = self.acquire()
        if token is None:
            raise LockNotAcquiredError()
        try:
            yield token
        finally:
            self.release()

def process_payment(order_id: str):
    lock = DistributedLock(redis_client, f"payment:{order_id}")
    with lock.hold() as fencing_token:
        db.execute(
            "UPDATE orders SET status='PAID' "
            "WHERE id=%s AND fence_token < %s",
            (order_id, fencing_token)
        )
```

```go
// Go — etcd 기반 분산 락 (합의 기반, Kleppmann 권장)
import (
    "context"
    "time"
    clientv3 "go.etcd.io/etcd/client/v3"
    "go.etcd.io/etcd/client/v3/concurrency"
)

type EtcdLock struct {
    client  *clientv3.Client
    session *concurrency.Session
    mutex   *concurrency.Mutex
}

func NewEtcdLock(client *clientv3.Client, key string, ttl int) (*EtcdLock, error) {
    session, err := concurrency.NewSession(client,
        concurrency.WithTTL(ttl),
    )
    if err != nil {
        return nil, err
    }
    return &EtcdLock{
        client:  client,
        session: session,
        mutex:   concurrency.NewMutex(session, "/locks/"+key),
    }, nil
}

func (l *EtcdLock) Lock(ctx context.Context) (int64, error) {
    if err := l.mutex.Lock(ctx); err != nil {
        return 0, err
    }
    // etcd revision = 단조 증가 → fencing token
    resp, err := l.client.Get(ctx, l.mutex.Key())
    if err != nil {
        return 0, err
    }
    return resp.Kvs[0].CreateRevision, nil
}

func (l *EtcdLock) Unlock(ctx context.Context) error {
    return l.mutex.Unlock(ctx)
}

func processWithLock(client *clientv3.Client, orderID string) error {
    lock, err := NewEtcdLock(client, "payment:"+orderID, 30)
    if err != nil {
        return err
    }
    defer lock.session.Close()

    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

    fencingToken, err := lock.Lock(ctx)
    if err != nil {
        return err
    }
    defer lock.Unlock(ctx)
    return updateWithFencing(orderID, fencingToken)
}
```

```kotlin
// Kotlin/Spring — Redisson 분산 락 + Watchdog
import org.redisson.api.RedissonClient
import java.util.concurrent.TimeUnit

@Service
class PaymentService(
    private val redisson: RedissonClient,
    private val paymentRepo: PaymentRepository,
) {
    // Redisson Watchdog: 락 보유 중 자동 갱신 (leaseTime 미지정 시)
    fun processPayment(orderId: String) {
        val lock = redisson.getLock("lock:payment:$orderId")

        // waitTime=10s, leaseTime=-1 (watchdog 30초마다 갱신)
        val acquired = lock.tryLock(10, -1, TimeUnit.SECONDS)
        if (!acquired) throw LockNotAcquiredException(orderId)

        try {
            val payment = paymentRepo.findByOrderId(orderId)
                ?: throw PaymentNotFoundException(orderId)
            if (payment.status != PaymentStatus.PENDING) return // 멱등성
            payment.status = PaymentStatus.COMPLETED
            paymentRepo.save(payment)
        } finally {
            if (lock.isHeldByCurrentThread) lock.unlock()
        }
    }

    // Fencing Token 패턴
    fun processWithFencing(orderId: String) {
        val lock = redisson.getLock("lock:payment:$orderId")
        val fenceCounter = redisson.getAtomicLong("fence:payment:$orderId")

        if (!lock.tryLock(10, 30, TimeUnit.SECONDS))
            throw LockNotAcquiredException(orderId)
        try {
            val fencingToken = fenceCounter.incrementAndGet()
            val updated = paymentRepo.updateWithFencing(
                orderId = orderId,
                status = PaymentStatus.COMPLETED,
                fencingToken = fencingToken
            )
            if (updated == 0) {
                log.warn("Stale lock detected for order $orderId")
            }
        } finally {
            if (lock.isHeldByCurrentThread) lock.unlock()
        }
    }
}
```

**Step 4 — 구체적 예시: 선택 가이드**

```
분산 락 선택 의사결정 트리:

1. 목적이 무엇인가?
   +-- 효율성 (중복 방지, best-effort)
   |   +-- Redis 단일 인스턴스 + TTL (충분!)
   +-- 정확성 (데이터 정합성 필수)
       +-- 저장소가 fencing token 지원?
       |   +-- Yes → Redis/Redlock + fencing token
       |   +-- No  → etcd/ZooKeeper (합의 기반)
       +-- 극한 정확성 (금융 수준)
           +-- etcd/ZooKeeper + fencing token + 저장소 검증
```

| 구현 | 성능 | 정확성 | 운영 복잡도 |
|------|------|--------|-------------|
| Redis 단일 | ~0.1ms | 낮음 | 낮음 |
| Redlock (5대) | ~2-5ms | 논쟁 중 | 중간 |
| etcd/ZooKeeper | ~5-20ms | 높음 | 높음 |
| DB Advisory Lock | ~1-5ms | 높음 (단일 DB) | 낮음 |

**Step 5 — 트레이드오프 & 대안**

| 측면 | Lease-based | Fencing Token |
|------|-------------|---------------|
| **원리** | 시간 기반 소유권 | 순서 기반 거부 |
| **GC pause** | 취약 (만료 미감지) | 안전 (token 비교) |
| **시계 의존** | 높음 | 없음 |
| **저장소 수정** | 불필요 | 필요 (검증 로직) |
| **Watchdog** | 일부 완화 | 불필요 |

대안들:
- **DB Advisory Lock**: PostgreSQL `pg_advisory_lock()` — 단일 DB라면 가장 간단
- **Chubby Lock**: Google의 분산 락 서비스 (Paxos 기반)
- **DynamoDB Conditional Write**: `attribute_not_exists(lock_owner) OR lock_expiry < :now`

**Step 6 — 성장 & 심화**

- Kleppmann의 "DDIA" 8장: 분산 락의 근본 한계
- Chubby 논문 (Burrows, 2006): Google의 분산 락 서비스
- FaunaDB Calvin: 락 없는 직렬화 — 전역 로그 순서로 대체
- CockroachDB의 Transaction Lock: MVCC + intent 기반 (별도 락 서비스 불필요)

**🎯 면접관 평가 기준:**

| 수준 | 기대 |
|------|------|
| **L6 PASS** | Redis 락 구현, TTL 필요성, GC pause 문제 인식, Redlock 기본 동작 |
| **L7 EXCEED** | Kleppmann/Antirez 논쟁 양측 설명, fencing token 메커니즘, 목적별 도구 선택 근거 |
| **🚩 RED FLAG** | "Redis SET NX면 충분하다", fencing token 모름, GC pause 영향 인식 못함 |

---

## Category 3: Database Internals

### Q15: B-tree vs LSM-tree

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Database Internals

**Question:**
B-tree와 LSM-tree의 내부 구조, 쓰기/읽기 경로를 상세히 설명하라. Write Amplification, Read Amplification, Space Amplification의 관점에서 두 구조를 비교하고, 각각이 어떤 워크로드에 적합한지 논의하라. RocksDB의 compaction 전략(Leveled vs Tiered)과 튜닝 포인트를 포함하여 실전 경험을 설명하라.

---

**🧒 12살 비유:**
**B-tree**는 정리된 책장이야 — 새 책을 꽂으려면 다른 책들을 밀어야 하지만(쓰기 느림), 찾을 때는 알파벳 순서대로 바로 찾을 수 있어(읽기 빠름). **LSM-tree**는 책상 위에 쌓아놓는 방식이야 — 새 책은 그냥 맨 위에 올려놓으면 돼(쓰기 빠름), 하지만 찾을 때는 여러 더미를 뒤져야 해(읽기 느림). 가끔 시간이 날 때 더미들을 정리해서 합치는 것이 compaction이야.

**📋 단계별 답변:**

**Step 1 — 맥락: 저장소 엔진의 두 갈래**

데이터베이스의 저장소 엔진은 크게 두 가지 계열로 나뉜다:
- **B-tree 계열**: PostgreSQL, MySQL (InnoDB), SQL Server, Oracle — 전통적 RDBMS
- **LSM-tree 계열**: RocksDB, LevelDB, Cassandra, HBase, ScyllaDB — NoSQL, 시계열

이 선택은 워크로드 특성에 따라 시스템 성능을 10배 이상 좌우할 수 있다.

**Step 2 — 핵심 기술: 내부 구조 비교**

**(1) B-tree**
```
구조: 균형 잡힌 N-ary 트리 (보통 B+ tree)
페이지 크기: 4KB~16KB (PostgreSQL: 8KB, InnoDB: 16KB)

쓰기 경로:
  1. 루트에서 리프까지 탐색 (O(log_B N))
  2. 리프 페이지에 쓰기 (in-place update)
  3. 페이지 가득 차면 split → 부모 업데이트
  4. WAL에 먼저 기록 (crash recovery)

읽기 경로:
  1. 루트에서 리프까지 탐색 (O(log_B N))
  2. 리프 페이지에서 값 반환
  3. 버퍼 풀(캐시)에 있으면 디스크 I/O 없음

특성:
  - Branching factor B ≈ 수백 (16KB 페이지 / (key+pointer))
  - 4단계면 수 TB 커버 (256^4 = 4B 페이지)
  - 읽기 최적, 쓰기 시 random I/O
```

**(2) LSM-tree (Log-Structured Merge-tree)**
```
구조: 메모리(MemTable) + 디스크(SSTable 레벨들)

쓰기 경로:
  1. WAL에 기록 (순차 쓰기)
  2. MemTable에 삽입 (Red-Black tree / Skip List)
  3. MemTable 가득 차면 → SSTable로 flush (순차 쓰기)
  4. 백그라운드 compaction: SSTable 병합 + 정렬

읽기 경로:
  1. MemTable 확인
  2. 없으면 L0 → L1 → ... → Ln SSTable 순서로 검색
  3. 각 SSTable에서 Bloom Filter로 빠른 음성 판정
  4. 존재 가능하면 인덱스로 데이터 블록 찾아 읽기

특성:
  - 모든 쓰기가 순차 I/O (SSD/HDD 모두 유리)
  - 읽기 시 여러 레벨 검색 (read amplification)
  - Compaction이 공간/성능/쓰기 증폭 결정
```

**Amplification 비교:**

| 지표 | B-tree | LSM-tree |
|------|--------|----------|
| **Write Amplification** | 높음 (페이지 전체 재기록, WAL) | 중간~높음 (compaction 반복) |
| **Read Amplification** | 낮음 (O(log N), 보통 1-2 I/O) | 높음 (여러 레벨 검색) |
| **Space Amplification** | 낮음 (in-place update) | 중간 (dead entries, compaction 전) |

**Step 3 — 다양한 관점: 스택별 활용**

```python
from sqlalchemy import create_engine, Column, Index, text
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

class Order(Base):
    __tablename__ = 'orders'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, nullable=False)
    total_amount = Column(Numeric(10, 2))

    # B-tree 인덱스 (기본값) — 범위 쿼리에 최적
    __table_args__ = (
        Index('idx_orders_user_created', 'user_id', 'created_at'),
        # Partial Index — B-tree의 장점: 조건부 인덱스
        Index('idx_orders_pending', 'created_at',
              postgresql_where=text("status = 'PENDING'")),
    )


def analyze_query(session: Session, user_id: int):
    result = session.execute(text("""
        EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
        SELECT * FROM orders
        WHERE user_id = :uid AND created_at > now() - interval '7 days'
        ORDER BY created_at DESC
        LIMIT 20
    """), {"uid": user_id})
    plan = result.scalar()
    # shared_blks_hit vs shared_blks_read → 캐시 히트율
    # Index Scan vs Seq Scan → 인덱스 효과
    return plan
```

```go
// Go — RocksDB (LSM-tree) 직접 사용
import (
    "github.com/linxGnu/grocksdb"
)

func setupRocksDB() *grocksdb.DB {
    bbto := grocksdb.NewDefaultBlockBasedTableOptions()
    // Bloom Filter: 읽기 amplification 완화 (false positive ~1%)
    bbto.SetFilterPolicy(grocksdb.NewBloomFilter(10))
    // Block Cache: 자주 읽는 데이터 메모리 캐싱
    bbto.SetBlockCache(grocksdb.NewLRUCache(256 * 1024 * 1024)) // 256MB

    opts := grocksdb.NewDefaultOptions()
    opts.SetBlockBasedTableFactory(bbto)
    opts.SetCreateIfMissing(true)

    // Write Buffer (MemTable) 설정
    opts.SetWriteBufferSize(64 * 1024 * 1024)    // 64MB MemTable
    opts.SetMaxWriteBufferNumber(3)                // 최대 3개 MemTable
    opts.SetMinWriteBufferNumberToMerge(2)         // 2개 모이면 flush

    // Compaction 전략: Leveled (읽기 최적화)
    opts.SetCompactionStyle(grocksdb.LevelStyleCompaction)
    opts.SetMaxBytesForLevelBase(256 * 1024 * 1024)   // L1 = 256MB
    opts.SetMaxBytesForLevelMultiplier(10)              // L(n+1) = L(n) * 10
    // L0=64MB, L1=256MB, L2=2.5GB, L3=25GB, L4=250GB

    opts.SetNumLevels(7)

    db, err := grocksdb.OpenDb(opts, "/data/mydb")
    if err != nil {
        panic(err)
    }
    return db
}

// Compaction 전략 비교:
// Leveled: 읽기 최적화 (read amp 낮음, write amp 높음)
//   - 각 레벨에 1개의 정렬된 run
//   - 상위 레벨과 merge하며 compaction
//   - 읽기: 레벨당 최대 1개 SSTable만 검색
//
// Tiered (Universal): 쓰기 최적화 (write amp 낮음, space amp 높음)
//   - 각 레벨에 여러 개의 정렬된 run
//   - 비슷한 크기의 run들을 merge
//   - 쓰기: compaction 빈도 낮음
```

```kotlin
// Kotlin — B-tree 인덱스 최적화 (Spring Data JPA + Hibernate)
import jakarta.persistence.*
import org.hibernate.annotations.BatchSize

@Entity
@Table(
    name = "orders",
    indexes = [
        // Covering Index: 쿼리에 필요한 모든 컬럼 포함
        // → Index-Only Scan 가능 (힙 접근 불필요)
        Index(name = "idx_orders_covering",
              columnList = "user_id, created_at, status, total_amount"),
    ]
)
class Order(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(nullable = false)
    val userId: Long,

    @Column(nullable = false, length = 20)
    var status: String,

    @Column(nullable = false)
    val createdAt: LocalDateTime,

    @Column(nullable = false, precision = 10, scale = 2)
    val totalAmount: BigDecimal,
)

@Repository
interface OrderRepository : JpaRepository<Order, Long> {

    // B-tree 인덱스 활용: 범위 스캔 + 정렬
    @Query("""
        SELECT o FROM Order o
        WHERE o.userId = :userId
        AND o.createdAt > :since
        ORDER BY o.createdAt DESC
    """)
    fun findRecentOrders(
        @Param("userId") userId: Long,
        @Param("since") since: LocalDateTime,
        pageable: Pageable
    ): Page<Order>
}

// B-tree 깊이 계산 예시 (InnoDB, 16KB 페이지):
// Key=8B(bigint), Pointer=6B → Branching Factor = 16384/(8+6) ≈ 1170
// 깊이 3: 1170^3 = ~1.6B rows → 대부분의 테이블은 3단계
// 루트 + 1~2단계는 버퍼 풀에 캐시 → 실제 디스크 I/O = 1~2회
```

**Step 4 — 구체적 예시: 워크로드별 선택**

| 워크로드 | 최적 엔진 | 이유 |
|----------|-----------|------|
| OLTP (읽기 중심) | B-tree (PostgreSQL, MySQL) | 낮은 read amp, 포인트 쿼리 빠름 |
| OLTP (쓰기 중심) | LSM-tree (RocksDB) | 순차 쓰기, 높은 처리량 |
| 시계열 데이터 | LSM-tree (InfluxDB, TimescaleDB) | append-only 패턴에 적합 |
| 분석 (OLAP) | 컬럼형 (Parquet, ClickHouse) | 별도 범주 |
| 키-값 캐시 | LSM-tree (RocksDB), B-tree (BoltDB) | 단순 구조 |
| 분산 DB | LSM-tree (CockroachDB=Pebble, TiKV=RocksDB) | 범위 스캔 + 높은 쓰기 |

RocksDB 튜닝 체크리스트:
```
1. MemTable 크기: 쓰기 처리량에 비례 (64MB~256MB)
2. Bloom Filter bits: 10 bits/key → ~1% false positive
3. Block Cache: 전체 메모리의 30-50%
4. Compaction 스레드: CPU 코어 수의 25-50%
5. Rate Limiter: compaction I/O 제한 (foreground 영향 방지)
6. Compression: L0-L1=none/Snappy, L2+=ZSTD (CPU vs I/O)
```

**Step 5 — 트레이드오프 & 대안**

| 측면 | B-tree | LSM-tree | 영향 |
|------|--------|----------|------|
| 쓰기 지연 | 높음 (random I/O) | 낮음 (sequential) | SSD에서 격차 축소 |
| 읽기 지연 | 낮음 (1-2 I/O) | 높음 (여러 레벨) | Bloom Filter로 완화 |
| 공간 효율 | 높음 (~67% fill) | 중간 (dead data) | compaction 전략 의존 |
| 예측 가능성 | 높음 (안정적) | 낮음 (compaction spike) | rate limiter로 완화 |
| 동시성 | 잠금 기반 (래치) | Lock-free MemTable | LSM이 쓰기 동시성 우수 |

최근 트렌드:
- **Pebble** (CockroachDB): RocksDB의 Go 재구현, 더 나은 concurrent compaction
- **SILK** (Facebook): compaction 우선순위 스케줄링으로 latency spike 완화
- **FLSM**: fractional cascading으로 LSM-tree 읽기 최적화

**Step 6 — 성장 & 심화**

- WiscKey (2016): key-value 분리로 write amp 대폭 감소 (key만 LSM, value는 vLog)
- Dostoevsky (2018): lazy leveling — Leveled와 Tiered의 하이브리드
- Monkey (2017): Bloom Filter 메모리를 레벨별 최적 분배하는 분석 프레임워크
- B-epsilon tree: B-tree + 버퍼 → 쓰기 amp 감소 (BetrFS, TokuDB)

**🎯 면접관 평가 기준:**

| 수준 | 기대 |
|------|------|
| **L6 PASS** | 두 구조의 쓰기/읽기 경로 설명, amplification 3종 비교, 워크로드별 선택 근거 |
| **L7 EXCEED** | Leveled vs Tiered compaction, Bloom Filter 역할, RocksDB 튜닝 경험, WiscKey 등 최신 연구 |
| **🚩 RED FLAG** | "LSM이 항상 빠르다", compaction 개념 모름, B-tree의 page split 설명 못함 |

---

### Q16: MVCC와 Isolation Level

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Database Internals

**Question:**
MVCC(Multi-Version Concurrency Control)의 동작 원리를 PostgreSQL과 MySQL(InnoDB)의 구현 차이를 포함하여 설명하라. Snapshot Isolation에서 발생하는 Write Skew anomaly를 예시와 함께 설명하고, 이를 방지하기 위한 Serializable Snapshot Isolation(SSI)의 메커니즘을 논의하라. 각 Isolation Level에서 허용/방지되는 anomaly를 정리하라.

---

**🧒 12살 비유:**
도서관에서 같은 책을 여러 사람이 동시에 읽을 수 있게 하려면, 각자 복사본을 주면 돼 — 이게 MVCC야. 누군가 책을 고치고 있어도, 다른 사람들은 이전 버전을 계속 읽을 수 있어. 문제는 두 사람이 각자 "빈 자리 있네!"하고 동시에 예약하면 자리가 초과될 수 있다는 거야. 이게 **Write Skew**야. 이걸 막으려면 "누가 뭘 읽었는지" 추적해서, 충돌하면 한 명을 취소시켜 — 이게 **SSI**야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 MVCC인가**

전통적 잠금 기반(2PL) 동시성 제어는 읽기-쓰기 충돌 시 블로킹한다. MVCC는 각 트랜잭션에게 데이터의 "스냅샷"을 제공하여, 읽기가 쓰기를 블로킹하지 않고 쓰기가 읽기를 블로킹하지 않는다. 현대 대부분의 RDBMS가 MVCC를 채택한다.

**Step 2 — 핵심 기술: MVCC 구현 비교**

**(1) PostgreSQL — Tuple Versioning**
```
각 행에 xmin, xmax 시스템 컬럼:
  xmin = 이 버전을 생성한 트랜잭션 ID
  xmax = 이 버전을 삭제/갱신한 트랜잭션 ID (0이면 현재 유효)

UPDATE orders SET status='SHIPPED' WHERE id=1;
→ 기존 행의 xmax = 현재 txid
→ 새 행 생성 (xmin = 현재 txid, xmax = 0)

가시성 판단 (Snapshot):
  행이 보이려면:
  1. xmin이 커밋됨 AND xmin < snapshot의 txid
  2. xmax가 없거나 커밋 안 됨 OR xmax > snapshot의 txid

Dead Tuple 정리: VACUUM이 더 이상 어떤 스냅샷에서도 안 보이는 행 제거
```

**(2) MySQL/InnoDB — Undo Log**
```
현재 행에는 최신 버전만 저장 (in-place update)
이전 버전은 Undo Log에 체인으로 연결

READ:
  1. 최신 버전의 DB_TRX_ID 확인
  2. 내 스냅샷보다 나중이면 → Undo Log 따라가서 이전 버전 찾기
  3. 보이는 버전을 찾을 때까지 반복

장점: 최신 데이터 읽기가 빠름 (Undo 추적 불필요)
단점: 오래된 스냅샷은 긴 Undo 체인 추적 필요
```

**Isolation Level과 Anomaly:**

| Anomaly | Read Uncommitted | Read Committed | Repeatable Read | Serializable |
|---------|:---:|:---:|:---:|:---:|
| **Dirty Read** | O | X | X | X |
| **Non-repeatable Read** | O | O | X | X |
| **Phantom Read** | O | O | O* | X |
| **Write Skew** | O | O | O | X |

*PostgreSQL RR은 Phantom 방지, MySQL RR은 gap lock으로 부분 방지

**Write Skew 예시:**
```
의사 당직 시스템: 최소 1명은 당직 유지 규칙
현재: Alice=ON, Bob=ON (2명 당직)

T1 (Alice):                    T2 (Bob):
  BEGIN                          BEGIN
  SELECT count(*) FROM          SELECT count(*) FROM
    oncall WHERE on=true         oncall WHERE on=true
  → 결과: 2 (OK, 1명 남음)       → 결과: 2 (OK, 1명 남음)
  UPDATE SET on=false            UPDATE SET on=false
    WHERE name='Alice'             WHERE name='Bob'
  COMMIT                         COMMIT

결과: 둘 다 OFF → 규칙 위반! (각자 "나 빼도 1명 남아"라고 판단)
```

**Step 3 — 다양한 관점: 스택별 구현**

```python
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

engine = create_engine(
    "postgresql://localhost/mydb",
    isolation_level="SERIALIZABLE",  # SSI 활성화
)

def toggle_oncall(session: Session, doctor_name: str):
    try:
        # SSI: 읽기 의존성 추적 (rw-dependencies)
        count = session.execute(
            text("SELECT count(*) FROM oncall WHERE on_duty = true")
        ).scalar()

        if count > 1:
            session.execute(
                text("UPDATE oncall SET on_duty = false WHERE name = :name"),
                {"name": doctor_name}
            )
            session.commit()
        else:
            session.rollback()
            raise BusinessRuleViolation("최소 1명 당직 필요")

    except OperationalError as e:
        if "could not serialize" in str(e):
            session.rollback()
            # SSI 충돌 감지 → 재시도
            raise SerializationConflict("Write skew detected, retry")
        raise

def toggle_oncall_pessimistic(session: Session, doctor_name: str):
    # FOR UPDATE: 읽은 행에 배타적 잠금 → write skew 원천 차단
    count = session.execute(
        text("SELECT count(*) FROM oncall WHERE on_duty = true FOR UPDATE")
    ).scalar()
    if count > 1:
        session.execute(
            text("UPDATE oncall SET on_duty = false WHERE name = :name"),
            {"name": doctor_name}
        )
    session.commit()
```

```go
// Go — MySQL/InnoDB의 Gap Lock과 Next-Key Lock
import (
    "database/sql"
    "fmt"
    _ "github.com/go-sql-driver/mysql"
)

// MySQL Repeatable Read: Gap Lock으로 Phantom 방지 (부분적)
func transferFunds(db *sql.DB, fromID, toID int64, amount float64) error {
    tx, err := db.BeginTx(ctx, &sql.TxOptions{
        Isolation: sql.LevelSerializable, // InnoDB: 2PL + Gap Lock
    })
    if err != nil {
        return err
    }
    defer tx.Rollback()

    // InnoDB Serializable = 모든 SELECT가 자동으로 SELECT ... LOCK IN SHARE MODE
    var fromBalance float64
    err = tx.QueryRow(
        "SELECT balance FROM accounts WHERE id = ?", fromID,
    ).Scan(&fromBalance)
    if err != nil {
        return err
    }

    if fromBalance < amount {
        return fmt.Errorf("insufficient balance: %.2f < %.2f", fromBalance, amount)
    }

    _, err = tx.Exec(
        "UPDATE accounts SET balance = balance - ? WHERE id = ?",
        amount, fromID,
    )
    if err != nil {
        return err
    }

    _, err = tx.Exec(
        "UPDATE accounts SET balance = balance + ? WHERE id = ?",
        amount, toID,
    )
    if err != nil {
        return err
    }

    return tx.Commit()
}

// InnoDB Lock 종류:
// Record Lock: 인덱스 레코드에 대한 잠금
// Gap Lock: 인덱스 레코드 사이의 "간격"에 대한 잠금
// Next-Key Lock: Record Lock + Gap Lock (Phantom 방지)
//
// 예: WHERE age BETWEEN 20 AND 30
//   → age=20,25,30 레코드 잠금 + (20,25), (25,30) 간격 잠금
//   → 이 범위에 INSERT 불가 → Phantom 방지
```

```kotlin
// Kotlin/Spring — @Transactional Isolation Level
import org.springframework.transaction.annotation.Isolation
import org.springframework.transaction.annotation.Transactional

@Service
class AccountService(
    private val accountRepo: AccountRepository,
    private val jdbcTemplate: JdbcTemplate,
) {
    // PostgreSQL SSI: Write Skew 자동 감지 + 재시도
    @Transactional(isolation = Isolation.SERIALIZABLE)
    @Retryable(
        retryFor = [CannotSerializeTransactionException::class],
        maxAttempts = 3,
        backoff = Backoff(delay = 100, multiplier = 2.0)
    )
    fun toggleOnCall(doctorName: String) {
        val onCallCount = jdbcTemplate.queryForObject(
            "SELECT count(*) FROM oncall WHERE on_duty = true",
            Int::class.java
        ) ?: 0

        if (onCallCount > 1) {
            jdbcTemplate.update(
                "UPDATE oncall SET on_duty = false WHERE name = ?",
                doctorName
            )
        } else {
            throw BusinessRuleViolation("최소 1명 당직 필요")
        }
        // SSI가 rw-dependency 감지하면 CannotSerializeTransactionException
        // → @Retryable이 자동 재시도
    }

    // Optimistic Locking (JPA @Version)
    // MVCC의 애플리케이션 레벨 활용
    @Transactional(isolation = Isolation.READ_COMMITTED)
    fun updateOrderOptimistic(orderId: Long, newStatus: String) {
        val order = accountRepo.findById(orderId)
            .orElseThrow { NotFoundException(orderId) }
        // @Version 필드: UPDATE 시 version 비교
        // 다른 트랜잭션이 먼저 변경했으면 OptimisticLockException
        order.status = newStatus
        accountRepo.save(order) // version 자동 증가
    }
}

// PostgreSQL SSI vs MySQL Serializable 차이:
// PostgreSQL SSI:
//   - 낙관적: 실행 후 충돌 감지 시 abort
//   - 읽기가 쓰기를 블로킹하지 않음
//   - rw-dependency 그래프에서 cycle 감지
//
// MySQL Serializable:
//   - 비관적: 모든 SELECT가 LOCK IN SHARE MODE
//   - 읽기가 쓰기를 블로킹할 수 있음
//   - Gap Lock으로 범위 잠금
```

**Step 4 — 구체적 예시: SSI 동작 원리**

```
Serializable Snapshot Isolation (Cahill et al., 2008):

rw-dependency 추적:
  T1이 읽은 데이터를 T2가 쓰면: T1 --rw--> T2

Dangerous Structure 감지:
  T1 --rw--> T2 --rw--> T1 (cycle!)
  → 한 트랜잭션을 abort하여 직렬화 가능성 보장

Write Skew 예시의 SSI 처리:
  T1: read(oncall) --rw--> T2: write(Bob=OFF)
  T2: read(oncall) --rw--> T1: write(Alice=OFF)
  → Cycle 감지 → T2 abort (또는 T1)

PostgreSQL 구현:
  - SIReadLock: 읽기 시 "누가 이 데이터를 읽었는지" 기록
  - rw-conflict: 쓰기 시 이미 읽은 트랜잭션과 충돌 감지
  - commit 시 dangerous structure 확인 → abort or commit
```

**Step 5 — 트레이드오프 & 대안**

| Isolation | 성능 | 이상 현상 | 적합 |
|-----------|------|-----------|------|
| Read Committed | 최고 | Write Skew, Phantom | 대부분의 웹 앱 |
| Repeatable Read | 높음 | Write Skew (PG), Phantom(MySQL) | 보고서, 집계 |
| Serializable (SSI) | 중간 | 없음 | 금융, 의료 |
| Serializable (2PL) | 낮음 | 없음 (데드락 가능) | 짧은 트랜잭션 |

MVCC Garbage Collection 비교:
```
PostgreSQL: VACUUM (별도 프로세스, autovacuum)
  - Dead tuple이 쌓이면 bloat → 주기적 VACUUM FULL 필요
  - 장기 트랜잭션이 VACUUM 차단 → xid wraparound 위험

MySQL/InnoDB: Purge Thread (백그라운드)
  - Undo Log 자동 정리
  - 장기 트랜잭션 → Undo Log 비대화 → 성능 저하
```

**Step 6 — 성장 & 심화**

- Cahill의 SSI 논문 (2008): Snapshot Isolation에서 serializable로 가는 실용적 방법
- PostgreSQL의 Predicate Lock: 페이지/튜플/인덱스 수준 세분화
- CockroachDB의 SSI: HLC timestamp 기반으로 글로벌 직렬화
- Spanner의 2PL + MVCC 하이브리드: 쓰기는 2PL, 읽기는 MVCC

**🎯 면접관 평가 기준:**

| 수준 | 기대 |
|------|------|
| **L6 PASS** | MVCC 기본 원리, Isolation Level 4단계 anomaly 매핑, Write Skew 예시 |
| **L7 EXCEED** | PostgreSQL vs MySQL MVCC 차이, SSI 동작 원리, VACUUM/Purge 문제, 실전 tuning |
| **🚩 RED FLAG** | "MVCC면 락이 필요 없다", Write Skew 모름, Serializable = "느린 것"으로만 인식 |

---

### Q17: Query Optimizer

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Database Internals

**Question:**
RDBMS의 Query Optimizer가 실행 계획을 결정하는 과정을 설명하라. Cost Model의 구성 요소, 주요 Join 알고리즘(Nested Loop, Hash Join, Sort-Merge Join)의 특성과 선택 기준, 그리고 실행 계획이 잘못되었을 때의 진단과 해결 방법을 프로덕션 경험을 바탕으로 논의하라.

---

**🧒 12살 비유:**
네비게이션이 목적지까지 여러 경로를 계산해서 가장 빠른 길을 알려주는 것처럼, Query Optimizer는 데이터를 찾는 여러 방법 중 "가장 비용이 적은 방법"을 고른다. 만약 친구 3명을 만나야 할 때, 순서를 바꾸면 이동 거리가 크게 달라지듯이, 테이블 3개를 JOIN하는 순서도 성능을 100배 이상 바꿀 수 있어.

**📋 단계별 답변:**

**Step 1 — 맥락: 쿼리 최적화의 중요성**

같은 SQL이라도 실행 계획에 따라 성능 차이가 100~10000배 발생할 수 있다. Query Optimizer는 SQL이라는 "무엇을(What)" 기술에서 "어떻게(How)" 실행할지를 결정하는 핵심 컴포넌트다. 대부분의 RDBMS는 Cost-Based Optimizer(CBO)를 사용한다.

**Step 2 — 핵심 기술: 최적화 과정**

```
SQL 쿼리
  → Parser (구문 분석)
  → Rewriter (뷰 확장, 서브쿼리 변환)
  → Optimizer (실행 계획 탐색)
     ├─ 1. Logical Plan 생성 (관계 대수 변환)
     ├─ 2. 후보 Physical Plan 열거
     ├─ 3. Cost Estimation (통계 기반)
     └─ 4. 최저 비용 Plan 선택
  → Executor (실행)
```

**(1) Cost Model 구성 요소**

| 요소 | 설명 | 출처 |
|------|------|------|
| **Cardinality** | 각 연산의 결과 행 수 추정 | 히스토그램, ndistinct |
| **Selectivity** | WHERE 조건이 걸러내는 비율 | 통계 테이블 (pg_statistic) |
| **I/O Cost** | 디스크 페이지 읽기 횟수 | seq_page_cost, random_page_cost |
| **CPU Cost** | 행 처리, 비교 연산 비용 | cpu_tuple_cost, cpu_operator_cost |
| **메모리** | work_mem 내 정렬/해시 가능 여부 | 설정값 |

**(2) Join 알고리즘 비교**

| Algorithm | 시간 복잡도 | 적합 조건 | 특성 |
|-----------|------------|-----------|------|
| **Nested Loop** | O(N*M) | 작은 테이블, 인덱스 있을 때 | Index NL은 O(N*logM) |
| **Hash Join** | O(N+M) | 등호 조건, 큰 테이블 | 메모리 필요 (빌드 측) |
| **Sort-Merge** | O(NlogN+MlogM) | 이미 정렬됨, 범위 조건 | 정렬 비용 or 인덱스 활용 |

**(3) Join 순서의 폭발적 경우의 수**

```
N개 테이블 JOIN → 가능한 순서: N! (factorial)
  3개: 6가지
  5개: 120가지
  10개: 3,628,800가지

최적화 전략:
  - 소규모 (≤10-12): Dynamic Programming (최적해 보장)
  - 대규모 (>12): Greedy/Genetic Algorithm (근사해)
  - PostgreSQL: GEQO (Genetic Query Optimization) for 12+ tables
```

**Step 3 — 다양한 관점: 스택별 실행 계획 분석**

```python
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://localhost/mydb")

def analyze_slow_query(user_id: int) -> dict:
    with engine.connect() as conn:
        result = conn.execute(text("""
            EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON, TIMING)
            SELECT o.id, o.status, p.name, p.price
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            WHERE o.user_id = :uid
            AND o.created_at > now() - interval '30 days'
            ORDER BY o.created_at DESC
            LIMIT 20
        """), {"uid": user_id})

        plan = result.scalar()
        return plan


def refresh_statistics(table_name: str):
    with engine.connect() as conn:
        conn.execute(text(f"ANALYZE {table_name}"))

```

```go
// Go — MySQL EXPLAIN + 실행 계획 분석
import (
    "database/sql"
    "encoding/json"
    "fmt"
)

type ExplainRow struct {
    ID           int     `json:"id"`
    SelectType   string  `json:"select_type"`
    Table        string  `json:"table"`
    Type         string  `json:"type"`      // system > const > eq_ref > ref > range > index > ALL
    PossibleKeys *string `json:"possible_keys"`
    Key          *string `json:"key"`
    KeyLen       *int    `json:"key_len"`
    Rows         int64   `json:"rows"`
    Filtered     float64 `json:"filtered"`
    Extra        string  `json:"extra"`
}

func analyzeQuery(db *sql.DB, userID int64) ([]ExplainRow, error) {
    rows, err := db.Query(`
        EXPLAIN FORMAT=JSON
        SELECT o.id, o.status, p.name
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        WHERE o.user_id = ?
        AND o.created_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
        ORDER BY o.created_at DESC
        LIMIT 20
    `, userID)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var plan string
    for rows.Next() {
        rows.Scan(&plan)
    }
    fmt.Println(plan)
    return nil, nil
}

// MySQL 실행 계획 Type 해석:
// const:   기본키/유니크 인덱스로 1행 조회 (최고)
// eq_ref:  JOIN에서 기본키/유니크로 1행 조회
// ref:     비유니크 인덱스로 여러 행 조회
// range:   인덱스 범위 스캔 (BETWEEN, <, >)
// index:   인덱스 풀 스캔 (커버링 인덱스)
// ALL:     테이블 풀 스캔 (최악 — 인덱스 필요)

// Extra 경고 신호:
// "Using filesort"     → ORDER BY에 인덱스 활용 못함
// "Using temporary"    → 임시 테이블 생성 (GROUP BY, DISTINCT)
// "Using where"        → 스토리지 엔진 반환 후 서버에서 필터링
// "Using index"        → 커버링 인덱스 (좋음!)
```

```kotlin
// Kotlin/Spring — JPA 쿼리 최적화 전략
import jakarta.persistence.QueryHint
import org.hibernate.jpa.HibernateHints

@Repository
interface OrderRepository : JpaRepository<Order, Long> {

    // N+1 문제 방지: FETCH JOIN
    @Query("""
        SELECT DISTINCT o FROM Order o
        JOIN FETCH o.items oi
        JOIN FETCH oi.product p
        WHERE o.userId = :userId
        AND o.createdAt > :since
        ORDER BY o.createdAt DESC
    """)
    fun findRecentOrdersWithDetails(
        @Param("userId") userId: Long,
        @Param("since") since: LocalDateTime,
    ): List<Order>

    // Read-Only 힌트: MVCC 스냅샷 최적화
    @QueryHints(QueryHint(name = HibernateHints.HINT_READ_ONLY, value = "true"))
    @Query("SELECT o FROM Order o WHERE o.status = :status")
    fun findByStatusReadOnly(@Param("status") status: String): List<Order>
}

@Service
class QueryAnalysisService(private val em: EntityManager) {

    // Hibernate Statistics로 N+1 감지
    fun analyzeQueryPerformance() {
        val sessionFactory = em.entityManagerFactory.unwrap(
            org.hibernate.SessionFactory::class.java
        )
        val stats = sessionFactory.statistics
        stats.isStatisticsEnabled = true

        // 쿼리 실행 후...
        println("Query count: ${stats.queryExecutionCount}")
        println("Slowest query: ${stats.queryExecutionMaxTimeQueryString}")
        println("Second level cache hit: ${stats.secondLevelCacheHitCount}")

        // 쿼리 수가 예상보다 많으면 N+1 의심
        // 해결: @BatchSize, @Fetch(FetchMode.SUBSELECT), JOIN FETCH
    }
}

// 실행 계획이 잘못되는 흔한 원인과 해결:
// 1. 통계 부정확 → ANALYZE 실행
// 2. 파라미터 스니핑 (MySQL Prepared Statement) → 바인딩 값에 따라 Plan 변동
// 3. Correlation 무시 → 다중 컬럼 통계 (CREATE STATISTICS)
// 4. 대량 데이터 변경 후 → 통계 자동 갱신 대기
```

**Step 4 — 구체적 예시: 실행 계획 진단 체크리스트**

```
프로덕션 느린 쿼리 진단 워크플로:

1. EXPLAIN ANALYZE로 실제 실행 계획 확인
2. 예상 행 수 vs 실제 행 수 비교 (10배 이상 차이 → 통계 문제)
3. 가장 비용이 높은 노드 식별
4. Join 알고리즘 적절성 검증
5. 인덱스 사용 여부 확인
6. 필요 시: 인덱스 추가, 통계 갱신, 쿼리 리라이팅

흔한 수정 사항:
  - 복합 인덱스 컬럼 순서: (equality, range, sort) 순
  - Covering Index로 heap 접근 제거
  - 서브쿼리 → JOIN 변환
  - LIMIT + ORDER BY에 적합한 인덱스
  - work_mem 조정 (Hash Join spill 방지)
```

**Step 5 — 트레이드오프 & 대안**

| Optimizer 유형 | 장점 | 단점 | 사용 시스템 |
|---------------|------|------|------------|
| Rule-Based (RBO) | 예측 가능 | 통계 무시, 비효율 | 구형 Oracle |
| Cost-Based (CBO) | 데이터 적응적 | 통계 부정확 시 오판 | PostgreSQL, MySQL |
| Adaptive | 실행 중 Plan 변경 | 복잡 | Oracle 12c+ |
| ML-Based | 학습 기반 | 블랙박스, 학습 비용 | Bao (연구), Learned Index |

**Step 6 — 성장 & 심화**

- Volcano/Cascades Optimizer: 현대 옵티마이저의 프레임워크 (CockroachDB 채택)
- Join Enumeration: DPccp, DPhyp 알고리즘으로 대규모 JOIN 최적화
- Adaptive Query Processing: SQL Server의 Adaptive Join, Oracle의 Adaptive Plan
- Learned Optimizer: SageDB, Bao — ML로 cost estimation 개선

**🎯 면접관 평가 기준:**

| 수준 | 기대 |
|------|------|
| **L6 PASS** | 3가지 Join 알고리즘, EXPLAIN 읽기, 인덱스 설계 원칙, N+1 문제 인식 |
| **L7 EXCEED** | Cost Model 구성 요소, cardinality estimation 오류 진단, 쿼리 리라이팅, 통계 관리 |
| **🚩 RED FLAG** | "인덱스 추가하면 항상 빨라진다", EXPLAIN 못 읽음, Join 순서 영향 모름 |

---

### Q18: Sharding 전략

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Database Internals

**Question:**
데이터베이스 Sharding의 Hash 기반과 Range 기반 전략을 비교하고, 각각의 핫스팟 문제, Resharding 절차, Cross-shard 쿼리 처리 방법을 설명하라. Consistent Hashing이 왜 필요하고 Virtual Node가 어떤 문제를 해결하는지, 그리고 실제 시스템(Vitess, CockroachDB, DynamoDB)의 sharding 접근법을 비교하라.

---

**🧒 12살 비유:**
학교에 학생이 10000명이라 출석부 한 권으로는 관리가 안 돼. 반을 나눠야 해. **Hash Sharding**은 학생 번호를 나머지 연산해서 반 배정 — "12345 % 4 = 1반". 골고루 나뉘지만, 1반 학생과 3반 학생이 같이 해야 하는 수업은 복잡해 (cross-shard). **Range Sharding**은 이름 순 — "A-G반, H-N반, O-Z반". 하지만 "Kim" 성이 많은 한국에서는 "H-N반"이 터져 (핫스팟). **Consistent Hashing**은 원형 시계에 반을 배치하는 것 — 반 하나가 빠져도 옆 반만 영향 받아.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 Sharding이 필요한가**

단일 데이터베이스의 한계:
- **쓰기 확장**: 단일 마스터의 쓰기 처리량 한계 (~10K-50K TPS)
- **저장 용량**: 단일 서버의 디스크 한계 (~수십 TB)
- **읽기 확장**: Replica로 해결 가능하지만, 쓰기는 불가

Sharding = 데이터를 여러 독립 DB에 수평 분할하여 각 shard가 독립적으로 쓰기/읽기 처리

**Step 2 — 핵심 기술: 전략 비교**

| 측면 | Hash Sharding | Range Sharding |
|------|:---:|:---:|
| **분배 균등성** | 높음 | 데이터 분포 의존 |
| **범위 쿼리** | 모든 shard 스캔 | 연속 shard만 스캔 |
| **핫스팟** | 낮음 (해시 분산) | 높음 (최신 데이터 집중) |
| **Resharding** | 어려움 (전체 재분배) | 쉬움 (range split) |
| **순서 보존** | 불가 | 가능 |

**Consistent Hashing:**
```
기존 Modular Hash: shard = hash(key) % N
  → N 변경 시 거의 모든 키가 이동 (N-1/N 비율)

Consistent Hashing: 해시 링에 노드 배치
  → 노드 추가/제거 시 인접 노드만 영향 (1/N 비율)

문제: 노드 수가 적으면 불균등 분배
해결: Virtual Node — 각 물리 노드가 링에 100-200개 가상 노드 배치
```

**Step 3 — 다양한 관점: 스택별 구현**

```python
from sqlalchemy import create_engine
from hashlib import md5

class ShardRouter:
    """Hash-based shard routing"""

    def __init__(self, shard_configs: list[str], virtual_nodes: int = 150):
        self.engines = {
            i: create_engine(cfg) for i, cfg in enumerate(shard_configs)
        }
        self.num_shards = len(shard_configs)
        # Consistent Hashing ring
        self.ring = SortedDict()
        for shard_id in range(self.num_shards):
            for vn in range(virtual_nodes):
                hash_val = self._hash(f"shard-{shard_id}-vn-{vn}")
                self.ring[hash_val] = shard_id

    def _hash(self, key: str) -> int:
        return int(md5(key.encode()).hexdigest(), 16)

    def get_shard(self, shard_key: str) -> int:
        """Consistent hashing으로 shard 결정"""
        h = self._hash(shard_key)
        # 링에서 시계 방향으로 가장 가까운 노드
        idx = self.ring.bisect_left(h)
        if idx >= len(self.ring):
            idx = 0
        return self.ring.values()[idx]

    def get_engine(self, shard_key: str):
        shard_id = self.get_shard(shard_key)
        return self.engines[shard_id]

    def scatter_gather(self, query: str, params: dict) -> list:
        """Cross-shard 쿼리: 모든 shard에서 실행 후 병합"""
        results = []
        for engine in self.engines.values():
            with engine.connect() as conn:
                rows = conn.execute(text(query), params).fetchall()
                results.extend(rows)
        return results

router = ShardRouter([
    "postgresql://shard0/db",
    "postgresql://shard1/db",
    "postgresql://shard2/db",
    "postgresql://shard3/db",
])

engine = router.get_engine(shard_key=user_id)
with engine.connect() as conn:
    orders = conn.execute(
        text("SELECT * FROM orders WHERE user_id = :uid"),
        {"uid": user_id}
    ).fetchall()

totals = router.scatter_gather(
    "SELECT status, count(*) FROM orders GROUP BY status", {}
)
```

```go
// Go — Vitess 기반 MySQL Sharding
import (
    "vitess.io/vitess/go/vt/vtgate/vtgateconn"
)

// Vitess VSchema — Sharding 설정 (JSON)
/*
{
  "sharded": true,
  "vindexes": {
    "hash": {
      "type": "hash"  // 해시 기반 vindex
    },
    "lookup_unique": {
      "type": "lookup_unique",  // 보조 인덱스
      "params": {
        "table": "order_lookup",
        "from": "order_id",
        "to": "user_id"
      }
    }
  },
  "tables": {
    "orders": {
      "column_vindexes": [
        {"column": "user_id", "name": "hash"}  // user_id로 shard
      ]
    }
  }
}
*/

func queryVitess(ctx context.Context) error {
    conn, err := vtgateconn.Dial(ctx, "vtgate:15991")
    if err != nil {
        return err
    }
    defer conn.Close()

    session := conn.Session("@primary", nil)

    // 단일 shard 쿼리: vtgate가 자동 라우팅
    _, err = session.Execute(ctx,
        "SELECT * FROM orders WHERE user_id = :uid",
        map[string]*querypb.BindVariable{
            "uid": sqltypes.Int64BindVariable(12345),
        },
    )

    // Cross-shard 쿼리: vtgate가 scatter-gather 자동 처리
    _, err = session.Execute(ctx,
        "SELECT user_id, COUNT(*) FROM orders GROUP BY user_id LIMIT 100",
        nil,
    )

    return err
}

// Vitess Resharding (Online):
// 1. SplitClone: 기존 shard 데이터를 새 shard로 복제
// 2. VReplication: 실시간 변경 스트리밍 (binlog 기반)
// 3. SwitchReads: 읽기를 새 shard로 전환
// 4. SwitchWrites: 쓰기를 새 shard로 전환 (짧은 다운타임)
// 5. 기존 shard 정리
```

```kotlin
// Kotlin/Spring — CockroachDB 자동 Sharding (Range-based)
import org.springframework.jdbc.core.JdbcTemplate

@Service
class ShardingDemo(private val jdbcTemplate: JdbcTemplate) {

    // CockroachDB: Range 기반 자동 sharding
    // 테이블 생성 시 shard key 지정 불필요 — PK 기준 자동 분할
    fun createTable() {
        jdbcTemplate.execute("""
            CREATE TABLE orders (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                user_id INT NOT NULL,
                status STRING NOT NULL,
                created_at TIMESTAMP DEFAULT now(),
                -- Hash-Sharded Index: 쓰기 핫스팟 방지
                INDEX idx_orders_created (created_at) USING HASH
            )
        """)
    }

    // Range Split 제어 (수동)
    fun splitRange() {
        // 특정 키에서 range split 강제
        jdbcTemplate.execute("""
            ALTER TABLE orders SPLIT AT VALUES ('00000000-0000-0000-0000-000000000000')
        """)
    }

    // Zone Config: 데이터 배치 제어
    fun configureZone() {
        // 특정 테이블의 데이터를 특정 region에 고정
        jdbcTemplate.execute("""
            ALTER TABLE orders CONFIGURE ZONE USING
                constraints = '[+region=us-east]',
                num_replicas = 3,
                lease_preferences = '[[+region=us-east]]'
        """)
    }

    // Cross-Range 쿼리: CockroachDB가 DistSQL로 자동 분산 처리
    fun crossShardQuery(startDate: LocalDateTime): List<Map<String, Any>> {
        return jdbcTemplate.queryForList("""
            SELECT user_id, COUNT(*) as order_count
            FROM orders
            WHERE created_at > ?
            GROUP BY user_id
            ORDER BY order_count DESC
            LIMIT 100
        """, startDate)
        // 내부적으로: 각 range에서 부분 집계 → coordinator에서 병합
    }
}

// Sharding 전략 비교 (실제 시스템):
// Vitess (MySQL):  Application-level, VSchema 기반 수동 설정
// CockroachDB:     Range 기반 자동 분할, Raft로 range 관리
// DynamoDB:        Hash 기반 파티션, 자동 분할 (adaptive capacity)
// MongoDB:         Hash or Range 선택, balancer가 chunk migration
```

**Step 4 — 구체적 예시: Resharding 전략**

```
Online Resharding 절차 (무중단):

1. 새 shard 프로비저닝
2. 데이터 복제 (initial snapshot)
3. 변경 분 스트리밍 (CDC/binlog)
4. 복제 지연 0에 수렴
5. 읽기 전환 (new shard로)
6. 쓰기 전환 (짧은 pause, ~수초)
7. 기존 shard 데이터 정리

핵심 과제:
  - 전환 시점의 데이터 일관성
  - 진행 중 트랜잭션 처리
  - 롤백 계획
```

**Step 5 — 트레이드오프 & 대안**

Shard Key 선택 기준:
```
좋은 Shard Key:
  - 카디널리티 높음 (user_id: 수백만 가지)
  - 쿼리에 항상 포함 (WHERE user_id = ?)
  - 분포 균등 (UUID, 해시)

나쁜 Shard Key:
  - 카디널리티 낮음 (status: 5가지 → 5개 shard만 사용)
  - 시간 기반 (created_at: 최신 shard에 쓰기 집중)
  - 쿼리에 안 쓰임 → 모든 쿼리가 scatter-gather
```

Sharding 대안:
| 대안 | 설명 | 적합 |
|------|------|------|
| **Read Replica** | 읽기 확장만 필요할 때 | 읽기 90%+ 워크로드 |
| **Partitioning** | 단일 DB 내 파티션 | 수백 GB 수준 |
| **NewSQL** | 자동 sharding (CockroachDB, Spanner) | 운영 부담 최소화 |
| **Citus** | PostgreSQL 확장 | PostgreSQL 유지하면서 sharding |

**Step 6 — 성장 & 심화**

- Shard Rebalancing: Consistent Hashing + 부하 기반 동적 재분배
- DynamoDB의 Adaptive Capacity: 핫 파티션 자동 감지 및 분할
- CockroachDB의 Range Merging: 너무 작은 range를 자동 병합
- Spanner의 Interleaved Table: 부모-자식 테이블을 같은 split에 co-locate

**🎯 면접관 평가 기준:**

| 수준 | 기대 |
|------|------|
| **L6 PASS** | Hash vs Range 비교, Consistent Hashing 원리, shard key 선택 기준 |
| **L7 EXCEED** | Virtual Node, Online Resharding 절차, cross-shard 쿼리 최적화, 실제 시스템 비교 |
| **🚩 RED FLAG** | "modular hash면 충분하다", resharding 시 다운타임 불가피하다고 단정, cross-shard join 비용 인식 못함 |

---

### Q19: 커넥션 풀링 비교

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Database Internals

**Question:**
데이터베이스 커넥션 풀링의 필요성과 내부 동작을 설명하라. Python(SQLAlchemy), Go(database/sql), Kotlin(HikariCP)의 커넥션 풀 구현을 비교하고, 각 스택의 동시성 모델이 풀 설계에 어떤 영향을 미치는지 논의하라. 프로덕션에서 풀 크기 결정, 커넥션 누수 감지, PgBouncer 같은 외부 풀링 프록시의 역할을 설명하라.

---

**🧒 12살 비유:**
수영장에 탈의실이 10개 있어. 손님이 올 때마다 탈의실을 새로 짓는 건 너무 비싸고 느려. 그래서 미리 10개를 만들어두고, 손님이 오면 빈 탈의실을 배정하고, 나가면 다음 손님에게 주는 거야. 이게 커넥션 풀이야. **탈의실 수(pool size)**를 너무 적게 하면 대기 줄이 길어지고, 너무 많으면 수영장이 복잡해져서 오히려 느려져 (context switching, DB process 과부하).

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 커넥션 풀이 필요한가**

DB 커넥션 생성 비용:
```
TCP 3-way handshake:    ~0.5ms (로컬), ~50ms (cross-region)
TLS handshake:          ~2-10ms
Authentication:         ~1-5ms
Backend process 생성:   ~5-10ms (PostgreSQL fork)
총 비용:                ~10-70ms per connection

vs 풀에서 재사용: ~0.01-0.1ms
```

PostgreSQL은 커넥션당 프로세스를 fork하므로 커넥션 수 = OS 프로세스 수. 수백 개 이상이면 context switching과 메모리 소비로 성능 급락.

**Step 2 — 핵심 기술: 스택별 풀 비교**

| 속성 | SQLAlchemy (Python) | database/sql (Go) | HikariCP (Kotlin/JVM) |
|------|:---:|:---:|:---:|
| **동시성 모델** | Thread/AsyncIO | Goroutine | Thread |
| **기본 풀 크기** | pool_size=5 | 무제한 (MaxOpen=0) | maximumPoolSize=10 |
| **커넥션 검증** | pool_pre_ping | PingContext | connectionTestQuery/keepalive |
| **유휴 타임아웃** | pool_recycle | ConnMaxIdleTime | idleTimeout=600s |
| **대기 전략** | 블로킹/타임아웃 | 블로킹 | 30초 타임아웃 |
| **누수 감지** | pool_timeout | 없음 (defer Close) | leakDetectionThreshold |

**Step 3 — 다양한 관점: 스택별 구현**

```python
from sqlalchemy import create_engine, event, text
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "postgresql://user:pass@localhost/db",

    # 풀 설정
    poolclass=QueuePool,
    pool_size=10,           # 상시 유지 커넥션 수
    max_overflow=20,        # 피크 시 추가 허용 (총 30까지)
    pool_timeout=30,        # 커넥션 대기 최대 시간 (초)
    pool_recycle=1800,      # 30분마다 커넥션 재생성 (stale 방지)
    pool_pre_ping=True,     # 사용 전 유효성 검증 (SELECT 1)

    # AsyncIO 사용 시
    # from sqlalchemy.ext.asyncio import create_async_engine
    # engine = create_async_engine("postgresql+asyncpg://...")
)

@event.listens_for(engine, "checkout")
def on_checkout(dbapi_conn, connection_record, connection_proxy):
    """커넥션이 풀에서 꺼내질 때"""
    logger.debug(f"Pool checkout: {engine.pool.status()}")

@event.listens_for(engine, "checkin")
def on_checkin(dbapi_conn, connection_record):
    """커넥션이 풀에 반환될 때"""
    logger.debug(f"Pool checkin: {engine.pool.status()}")

def get_pool_status():
    pool = engine.pool
    return {
        "size": pool.size(),          # 설정된 풀 크기
        "checkedin": pool.checkedin(), # 사용 가능한 커넥션
        "checkedout": pool.checkedout(), # 사용 중인 커넥션
        "overflow": pool.overflow(),   # 초과 생성된 커넥션
    }

```

```go
// Go — database/sql 내장 커넥션 풀
import (
    "database/sql"
    "time"
    _ "github.com/jackc/pgx/v5/stdlib"
)

func setupDB() *sql.DB {
    db, err := sql.Open("pgx", "postgres://user:pass@localhost/db")
    if err != nil {
        panic(err)
    }

    // 풀 설정
    db.SetMaxOpenConns(25)              // 최대 열린 커넥션 (0=무제한, 위험!)
    db.SetMaxIdleConns(10)              // 유휴 커넥션 유지 수
    db.SetConnMaxLifetime(30 * time.Minute) // 커넥션 최대 수명
    db.SetConnMaxIdleTime(5 * time.Minute)  // 유휴 최대 시간

    return db
}

// Go 특수 사항:
// - Goroutine은 매우 경량 → 수천 개가 동시에 DB 호출 가능
// - MaxOpenConns 미설정 시 DB에 수천 커넥션 폭탄 → 반드시 설정!
// - database/sql이 자체 풀링 내장 → 외부 라이브러리 불필요
// - Goroutine이 블로킹되어도 다른 Goroutine에 영향 없음 (M:N 스케줄링)

// 커넥션 풀 모니터링
func monitorPool(db *sql.DB) {
    stats := db.Stats()
    prometheus.GaugeVec.Set(float64(stats.OpenConnections))  // 열린 커넥션
    prometheus.GaugeVec.Set(float64(stats.InUse))            // 사용 중
    prometheus.GaugeVec.Set(float64(stats.Idle))             // 유휴
    prometheus.GaugeVec.Set(float64(stats.WaitCount))        // 대기 횟수
    prometheus.GaugeVec.Set(float64(stats.WaitDuration))     // 총 대기 시간
}

// 커넥션 누수 방지: defer로 반드시 반환
func getUser(db *sql.DB, id int64) (*User, error) {
    row := db.QueryRow("SELECT id, name FROM users WHERE id = $1", id)
    // QueryRow는 자동 반환

    // 주의: Query()는 rows.Close() 필수!
    rows, err := db.Query("SELECT * FROM users WHERE active = true")
    if err != nil {
        return nil, err
    }
    defer rows.Close()  // 반드시! 안 하면 커넥션 누수
    // ...
}
```

```kotlin
// Kotlin/Spring — HikariCP (JVM 최고 성능 풀)
// application.yml
/*
spring:
  datasource:
    url: jdbc:postgresql://localhost/db
    username: user
    password: pass
    hikari:
      maximum-pool-size: 20        # 최대 커넥션
      minimum-idle: 5              # 최소 유휴 커넥션
      idle-timeout: 600000         # 유휴 타임아웃 (10분, ms)
      max-lifetime: 1800000        # 커넥션 최대 수명 (30분)
      connection-timeout: 30000    # 커넥션 획득 대기 (30초)
      leak-detection-threshold: 60000  # 누수 감지 (60초 이상 미반환)
      pool-name: MyHikariPool
*/

@Configuration
class DataSourceConfig {

    @Bean
    fun dataSource(): HikariDataSource {
        return HikariDataSource().apply {
            jdbcUrl = "jdbc:postgresql://localhost/db"
            username = "user"
            password = "pass"
            maximumPoolSize = 20
            minimumIdle = 5

            // 커넥션 검증
            connectionTestQuery = "SELECT 1"  // JDBC4 미지원 드라이버용
            // JDBC4+ 드라이버는 Connection.isValid() 자동 사용

            // 누수 감지: 60초 이상 체크아웃 → 로그 경고
            leakDetectionThreshold = 60000

            // 메트릭 연동
            metricsTrackerFactory = PrometheusMetricsTrackerFactory()
        }
    }
}

// HikariCP 내부 동작:
// - ConcurrentBag: lock-free 자료구조로 커넥션 관리
//   → ThreadLocal 캐시: 같은 스레드가 같은 커넥션 재사용 (cache hit)
//   → CAS (Compare-And-Swap) 연산으로 락 최소화
// - Connection.close() → 풀에 반환 (실제 close 아님)
// - ProxyConnection: JDBC Connection을 감싸서 추적

// 풀 크기 공식 (HikariCP 권장):
// connections = ((core_count * 2) + effective_spindle_count)
// SSD 기준: core 4개 → (4 * 2) + 1 = 9~10 적정
// 이유: DB 작업은 CPU + I/O, 2배는 I/O 대기 중 다른 쿼리 처리

// 프로메테우스 메트릭
@Component
class PoolMetricsLogger(private val dataSource: HikariDataSource) {
    @Scheduled(fixedRate = 10000)
    fun logPoolMetrics() {
        val pool = dataSource.hikariPoolMXBean
        log.info("""
            Pool Stats:
            Active: ${pool.activeConnections}
            Idle: ${pool.idleConnections}
            Total: ${pool.totalConnections}
            Waiting: ${pool.threadsAwaitingConnection}
        """)
    }
}
```

**Step 4 — 구체적 예시: PgBouncer와 외부 풀링**

```
왜 외부 풀링 프록시가 필요한가?

문제: 마이크로서비스 100개 * 인스턴스 3개 * pool_size 10 = 3000 커넥션
PostgreSQL은 ~300-500 커넥션이 최적 → 6-10배 초과!

PgBouncer 모드:
  Session:      클라이언트 세션 = 백엔드 커넥션 (1:1, 절약 없음)
  Transaction:  트랜잭션 동안만 백엔드 할당 (가장 많이 사용)
  Statement:    쿼리 단위 할당 (prepared statement 불가)

아키텍처:
  App (pool_size=10) → PgBouncer (max_db=100) → PostgreSQL (max_connections=200)
  300개 앱 커넥션 → PgBouncer 100개 → PostgreSQL 100개 (30:1 멀티플렉싱)
```

**Step 5 — 트레이드오프 & 대안**

| 풀링 위치 | 장점 | 단점 |
|-----------|------|------|
| Application (HikariCP) | 단순, 지연 낮음 | 서비스 수 * 풀 크기 = 과다 |
| Sidecar (PgBouncer) | 서비스별 독립, 투명 | 운영 복잡도 증가 |
| Centralized (PgBouncer 중앙) | 커넥션 통합 관리 | SPOF, 추가 네트워크 홉 |
| DB 내장 (MySQL Thread Pool) | 별도 컴포넌트 불필요 | DB 부담 증가 |

**Step 6 — 성장 & 심화**

- PostgreSQL의 connection scaling 문제와 향후 개선 (pg_bouncer 대안으로 논의 중인 in-core pooling)
- MySQL Thread Pool (Enterprise): 커넥션당 스레드 대신 풀링된 스레드 그룹
- Connection Multiplexing: ProxySQL의 쿼리 수준 멀티플렉싱
- Serverless DB (Aurora Serverless, Neon): 커넥션 풀링을 인프라 수준에서 해결

**🎯 면접관 평가 기준:**

| 수준 | 기대 |
|------|------|
| **L6 PASS** | 풀링 필요성, 풀 크기 결정 요소, 커넥션 누수 인식, 스택 1개 이상 상세 설명 |
| **L7 EXCEED** | 3개 스택 비교, PgBouncer 역할, HikariCP 내부 구조, 동시성 모델이 풀에 미치는 영향 |
| **🚩 RED FLAG** | "풀 크기는 클수록 좋다", Go에서 MaxOpenConns 미설정, 커넥션 누수 감지 방법 모름 |

---

### Q20: Replication 전략

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Database Internals

**Question:**
데이터베이스 Replication의 Synchronous, Asynchronous, Semi-synchronous 방식을 비교하고, 각각의 데이터 유실 가능성, 성능 특성, 장애 시나리오를 설명하라. Replication Lag의 원인과 모니터링 방법, 그리고 lag으로 인한 이상 현상을 방지하기 위한 전략을 실제 사례와 함께 논의하라.

---

**🧒 12살 비유:**
선생님(Primary)이 칠판에 쓰면 조교들(Replica)이 베껴 써. **동기(Sync)**는 모든 조교가 베꼈다고 확인할 때까지 선생님이 기다리는 것 — 느리지만 하나도 안 놓쳐. **비동기(Async)**는 선생님이 계속 쓰고 조교들이 알아서 따라잡는 것 — 빠르지만 선생님이 갑자기 칠판을 지우면 못 베긴 부분이 생겨. **반동기(Semi-sync)**는 조교 한 명이라도 베꼈으면 넘어가는 것 — 속도와 안전의 절충.

**📋 단계별 답변:**

**Step 1 — 맥락: Replication의 목적**

1. **고가용성 (HA)**: Primary 장애 시 Replica가 승격 (failover)
2. **읽기 확장**: Replica에서 읽기 분산 (read scaling)
3. **지리적 분산**: 사용자 가까이에 데이터 배치 (latency 감소)
4. **백업**: 실시간 백업 역할 (Primary에 영향 없이)

**Step 2 — 핵심 기술: 복제 방식 비교**

| 속성 | Synchronous | Semi-synchronous | Asynchronous |
|------|:---:|:---:|:---:|
| **커밋 완료 조건** | 모든 replica ACK | 1+ replica ACK | Primary WAL만 |
| **데이터 유실** | 없음 (RPO=0) | 거의 없음 | 가능 (RPO>0) |
| **쓰기 지연** | 높음 (RTT * N) | 중간 (RTT * 1) | 낮음 (로컬) |
| **가용성** | Replica 장애 시 쓰기 블로킹 | 1개만 살아있으면 OK | 항상 쓰기 가능 |
| **사용 시스템** | PostgreSQL sync replication | MySQL semi-sync | 대부분 기본값 |

**(1) Asynchronous Replication**
```
Primary: COMMIT → WAL 기록 → 클라이언트 응답 → (비동기) WAL 전송
Replica: WAL 수신 → 적용

문제: Primary 장애 시 아직 전송 안 된 WAL = 데이터 유실
장점: 가장 빠름, Replica 장애가 Primary에 영향 없음
```

**(2) Synchronous Replication**
```
Primary: COMMIT → WAL 기록 → WAL 전송 → 모든 Replica ACK 대기 → 클라이언트 응답

문제: Replica 하나만 느려도 전체 쓰기 지연
장점: 데이터 유실 제로
```

**(3) Semi-synchronous (MySQL)**
```
Primary: COMMIT → WAL 기록 → WAL 전송 → 1개 Replica ACK → 클라이언트 응답

MySQL Semi-sync:
  - AFTER_SYNC (loss-less): binlog flush 후 ACK 대기 → 응답
  - AFTER_COMMIT: commit 후 ACK 대기 → 응답 (phantom read 가능)
  - ACK timeout 시 async로 전환 (가용성 우선)
```

**Step 3 — 다양한 관점: 스택별 구현**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

primary_engine = create_engine("postgresql://primary:5432/db")
replica_engine = create_engine("postgresql://replica:5432/db")

class RoutingSession(Session):
    """읽기/쓰기 자동 라우팅"""

    def get_bind(self, mapper=None, clause=None, **kw):
        if self._flushing or self.is_modified():
            return primary_engine  # 쓰기 → Primary
        return replica_engine      # 읽기 → Replica

class LagAwareSession(Session):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._recent_write = False
        self._write_time = None

    def get_bind(self, mapper=None, clause=None, **kw):
        if self._flushing:
            self._recent_write = True
            self._write_time = time.time()
            return primary_engine

        # 쓰기 후 5초 이내 → Primary에서 읽기 (Read Your Writes)
        if self._recent_write and (time.time() - self._write_time) < 5:
            return primary_engine

        return replica_engine

def check_replication_lag(primary_conn, replica_conn) -> dict:
    # Primary 측
    primary_lsn = primary_conn.execute(
        text("SELECT pg_current_wal_lsn()")
    ).scalar()

    # Replica 측
    result = replica_conn.execute(text("""
        SELECT
            pg_last_wal_receive_lsn() AS receive_lsn,
            pg_last_wal_replay_lsn() AS replay_lsn,
            EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))
                AS replay_lag_seconds
    """)).fetchone()

    return {
        "primary_lsn": primary_lsn,
        "receive_lsn": result.receive_lsn,
        "replay_lsn": result.replay_lsn,
        "replay_lag_seconds": result.replay_lag_seconds,
    }
```

```go
// Go — MySQL Semi-sync + Lag 모니터링
import (
    "database/sql"
    "time"
)

type ReplicaPool struct {
    primary  *sql.DB
    replicas []*sql.DB
    maxLag   time.Duration
}

func NewReplicaPool(primaryDSN string, replicaDSNs []string) *ReplicaPool {
    primary, _ := sql.Open("mysql", primaryDSN)
    replicas := make([]*sql.DB, len(replicaDSNs))
    for i, dsn := range replicaDSNs {
        replicas[i], _ = sql.Open("mysql", dsn)
    }
    return &ReplicaPool{
        primary:  primary,
        replicas: replicas,
        maxLag:   5 * time.Second,
    }
}

// Lag 인식 Replica 선택
func (p *ReplicaPool) GetReadDB() *sql.DB {
    for _, replica := range p.replicas {
        lag, err := p.checkLag(replica)
        if err == nil && lag < p.maxLag {
            return replica
        }
    }
    // 모든 replica lag 초과 → Primary에서 읽기 (fallback)
    return p.primary
}

func (p *ReplicaPool) checkLag(db *sql.DB) (time.Duration, error) {
    var secondsBehind sql.NullFloat64
    err := db.QueryRow("SHOW SLAVE STATUS").Scan(
        // ... 많은 컬럼 중 Seconds_Behind_Master 추출
        // 실제로는 전용 struct나 map으로 파싱
    )
    if err != nil {
        return 0, err
    }
    if !secondsBehind.Valid {
        return time.Hour, nil // NULL = 복제 중단
    }
    return time.Duration(secondsBehind.Float64) * time.Second, nil
}

// GTID 기반 일관성 읽기 (MySQL 8.0+)
func (p *ReplicaPool) ReadAfterWrite(
    ctx context.Context, gtidSet string, query string, args ...any,
) (*sql.Rows, error) {
    // WAIT_FOR_EXECUTED_GTID_SET: 특정 GTID까지 replica가 따라잡을 때까지 대기
    replica := p.replicas[0]
    _, err := replica.ExecContext(ctx,
        "SELECT WAIT_FOR_EXECUTED_GTID_SET(?, ?)", gtidSet, 5, // 5초 타임아웃
    )
    if err != nil {
        // 타임아웃 → Primary fallback
        return p.primary.QueryContext(ctx, query, args...)
    }
    return replica.QueryContext(ctx, query, args...)
}

// MySQL Semi-sync 설정:
// Primary: SET GLOBAL rpl_semi_sync_master_enabled = 1;
//          SET GLOBAL rpl_semi_sync_master_timeout = 10000; -- 10초 후 async 전환
// Replica: SET GLOBAL rpl_semi_sync_slave_enabled = 1;
```

```kotlin
// Kotlin/Spring — Read/Write 분리 + @Transactional(readOnly)
import org.springframework.jdbc.datasource.lookup.AbstractRoutingDataSource
import org.springframework.transaction.support.TransactionSynchronizationManager

enum class DataSourceType { PRIMARY, REPLICA }

class RoutingDataSource : AbstractRoutingDataSource() {
    override fun determineCurrentLookupKey(): Any {
        val isReadOnly = TransactionSynchronizationManager
            .isCurrentTransactionReadOnly()
        return if (isReadOnly) DataSourceType.REPLICA
               else DataSourceType.PRIMARY
    }
}

@Configuration
class DataSourceConfig {
    @Bean
    fun dataSource(
        @Qualifier("primaryDS") primary: DataSource,
        @Qualifier("replicaDS") replica: DataSource,
    ): DataSource {
        val routing = RoutingDataSource()
        routing.setTargetDataSources(mapOf(
            DataSourceType.PRIMARY to primary,
            DataSourceType.REPLICA to replica,
        ))
        routing.setDefaultTargetDataSource(primary)
        return routing
    }
}

@Service
class OrderService(private val orderRepo: OrderRepository) {

    // readOnly=true → Replica로 라우팅
    @Transactional(readOnly = true)
    fun getOrders(userId: Long): List<Order> {
        return orderRepo.findByUserId(userId)
    }

    // readOnly=false (기본) → Primary로 라우팅
    @Transactional
    fun createOrder(order: Order): Order {
        return orderRepo.save(order)
    }

    // Read Your Writes 패턴: 쓰기 직후에는 Primary에서 읽기
    @Transactional
    fun createAndVerify(order: Order): Order {
        val saved = orderRepo.save(order)
        // 같은 트랜잭션 → 같은 커넥션 (Primary) → Read Your Writes 보장
        return orderRepo.findById(saved.id)
            .orElseThrow { IllegalStateException("Just created!") }
    }
}

// Replication Lag 모니터링 (PostgreSQL)
@Component
class ReplicationLagMonitor(private val jdbcTemplate: JdbcTemplate) {

    @Scheduled(fixedRate = 5000)
    fun checkLag() {
        // pg_stat_replication (Primary에서 실행)
        val lags = jdbcTemplate.queryForList("""
            SELECT client_addr,
                   state,
                   pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes,
                   replay_lag
            FROM pg_stat_replication
        """)

        for (lag in lags) {
            val lagBytes = lag["lag_bytes"] as Long
            if (lagBytes > 10 * 1024 * 1024) { // 10MB 이상
                alerting.warn("Replication lag: ${lagBytes / 1024 / 1024}MB")
            }
        }
    }
}
```

**Step 4 — 구체적 예시: Lag으로 인한 이상 현상**

```
1. Stale Read: 사용자가 프로필 수정 후 이전 값 보임
   → 해결: Read Your Writes (쓰기 직후 Primary 읽기)

2. Monotonicity Violation: 새로고침마다 다른 replica에서 읽어 값이 "왔다갔다"
   → 해결: Sticky Session (같은 replica에서 읽기)

3. Causal Violation: 사용자 A가 쓴 글을 사용자 B가 보고 댓글을 달았는데,
   사용자 C에게는 댓글만 보이고 원글은 안 보임
   → 해결: Causal Consistency (GTID 기반)

4. Failover 데이터 유실: Async Primary 장애 → 아직 안 보낸 WAL 유실
   → 해결: Semi-sync 또는 최소 2개 replica ACK 정책
```

Lag 모니터링 지표:
```
PostgreSQL:
  - pg_stat_replication.replay_lag (시간)
  - pg_wal_lsn_diff() (바이트)

MySQL:
  - Seconds_Behind_Master (부정확할 수 있음)
  - GTID 차이 계산 (정확)
  - pt-heartbeat (Percona, 가장 정확)

알림 기준 (예시):
  - Warning: lag > 5초
  - Critical: lag > 30초
  - Emergency: lag > 5분 (복제 중단 의심)
```

**Step 5 — 트레이드오프 & 대안**

| 전략 | 유실 가능성 | 쓰기 성능 | 가용성 | 적합 |
|------|-----------|-----------|--------|------|
| Async | 있음 | 최고 | 최고 | 로그, 분석, 캐시 |
| Semi-sync | 거의 없음 | 중간 | 높음 | 일반 OLTP |
| Sync | 없음 | 낮음 | 중간 | 금융, 의료 |
| Group Replication | 없음 | 중간 | 높음 | MySQL HA |

Logical vs Physical Replication:
```
Physical (WAL Shipping):
  - 바이트 수준 복제 (정확한 복사본)
  - 빠름, 간단
  - 동일 버전/OS 필요

Logical (Row-based):
  - SQL/행 수준 복제
  - 선택적 테이블 복제 가능
  - 다른 버전/스키마 가능
  - CDC (Change Data Capture) 가능
```

**Step 6 — 성장 & 심화**

- Chain Replication: Primary → R1 → R2 → R3 (직렬 체인, CRAQ 변형)
- PostgreSQL의 Quorum-based Synchronous Replication (12+): ANY 2 (replica1, replica2, replica3)
- MySQL Group Replication: Paxos 기반 다중 Primary 지원
- AWS Aurora의 Storage-level Replication: 6-way 복제, 4/6 write quorum, 3/6 read quorum

**🎯 면접관 평가 기준:**

| 수준 | 기대 |
|------|------|
| **L6 PASS** | Sync/Async 차이, lag 원인과 영향, Read/Write 분리 구현, lag 모니터링 |
| **L7 EXCEED** | Semi-sync 상세, GTID 기반 일관성 읽기, failover 데이터 유실 시나리오, Logical vs Physical |
| **🚩 RED FLAG** | "Async면 데이터가 안 날아간다", lag 모니터링 안 함, Replica에서 쓰기 시도 |

---


> 대상: FAANG L6/L7 (Staff/Principal Engineer)
> 총 문항: 10개 (Q21~Q30) | 난이도: ⭐⭐⭐⭐⭐
> 스택: Python / Go / Kotlin

## 목차

### Category 4: Networking & Protocols (Q21~Q25)
- [Q21: TCP 내부 — 혼잡 제어, Nagle, TIME_WAIT](#q21-tcp-내부--혼잡-제어-nagle-time_wait)
- [Q22: HTTP/2 vs HTTP/3 — multiplexing, QUIC, 0-RTT](#q22-http2-vs-http3--multiplexing-quic-0-rtt)
- [Q23: gRPC vs REST — protobuf, streaming, L7 LB](#q23-grpc-vs-rest--protobuf-streaming-l7-lb)
- [Q24: WebSocket at Scale — 백만 커넥션](#q24-websocket-at-scale--백만-커넥션)
- [Q25: DNS & Service Discovery](#q25-dns--service-discovery)

### Category 5: Observability & SRE (Q26~Q30)
- [Q26: 폴리글랏 분산 트레이싱 — OpenTelemetry](#q26-폴리글랏-분산-트레이싱--opentelemetry)
- [Q27: SLO/SLI 설계 — error budget, burn rate](#q27-slosli-설계--error-budget-burn-rate)
- [Q28: 인시던트 대응 — on-call, postmortem](#q28-인시던트-대응--on-call-postmortem)
- [Q29: 메트릭 시스템 설계 — cardinality, recording rules](#q29-메트릭-시스템-설계--cardinality-recording-rules)
- [Q30: Chaos Engineering — fault injection](#q30-chaos-engineering--fault-injection)

---

## Category 4: Networking & Protocols

---

### Q21: TCP 내부 — 혼잡 제어, Nagle, TIME_WAIT

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Networking & Protocols

**Question:** "당신이 운영하는 마이크로서비스 클러스터에서 내부 RPC 지연이 간헐적으로 튀는 현상이 발생합니다. tcpdump 분석 결과 Nagle/지연 ACK 상호작용과 TIME_WAIT 소켓 누적이 원인으로 보입니다. TCP 혼잡 제어(Cubic vs BBR)까지 포함하여, 각 문제의 근본 원인과 해결 전략을 설명하고, Python/Go/Kotlin 서버에서 어떻게 소켓 튜닝하는지 구체적으로 보여주세요."

---

**12살 비유:**

편지를 보내는 우체국을 상상해봐. Nagle 알고리즘은 "편지가 조금밖에 없으면 좀 모아서 한번에 보내자"는 규칙이야. 지연 ACK는 "답장을 바로 안 쓰고 40ms 기다렸다가 다른 답장이랑 묶어서 보내자"는 규칙이야. 둘 다 효율을 위한 건데, 동시에 켜지면 서로 "너 먼저 보내" "아니 너 먼저"하면서 40ms씩 낭비하는 거지. TIME_WAIT는 편지를 다 주고받은 후에도 "혹시 길에 남은 편지가 있을 수 있으니 2분 더 기다리자"는 규칙인데, 너무 많은 편지함이 이 상태에 빠지면 새 편지함을 열 수 없게 돼. 혼잡 제어는 도로 상황에 따라 택배차 속도를 조절하는 건데, Cubic은 "막히면 확 줄이고 서서히 올려", BBR은 "도로 용량 자체를 측정해서 딱 맞는 속도로 달려"야.

**단계별 답변:**

**Step 1 — 맥락**

TCP는 40년 된 프로토콜이지만 현대 데이터센터 내부 통신에서도 여전히 지배적입니다. 문제는 TCP의 기본 동작이 WAN(인터넷) 최적화 기준으로 설계되어 있어, 데이터센터 내부의 low-latency 환경과 충돌한다는 점입니다. 세 가지 핵심 영역을 구분해야 합니다:

1. **Nagle + Delayed ACK 상호작용**: small write 패턴에서 40ms 지연 유발
2. **TIME_WAIT 누적**: 짧은 수명의 커넥션이 다량 생성될 때 포트 고갈
3. **혼잡 제어 알고리즘**: 패킷 로스 기반(Cubic) vs 대역폭 측정 기반(BBR)

**Step 2 — 핵심 기술**

**Nagle/Delayed ACK 상호작용:**

Nagle 알고리즘(RFC 896)은 미완성 ACK가 있으면 작은 세그먼트 전송을 보류합니다. Delayed ACK(RFC 1122)는 ACK를 최대 40ms(Linux 기본) 지연시켜 피기백 기회를 노립니다. 둘이 만나면:

```
Client: send(200 bytes) → Nagle이 "이전 ACK 대기 중, 보류"
Server: recv() 대기 중 → Delayed ACK가 "40ms 기다려 보자"
→ 40ms 후 Delayed ACK 타이머 만료 → ACK 전송 → Nagle 해제 → 데이터 전송
```

이것이 "Nagle-Delayed ACK deadlock"이며, RPC 지연의 고전적 원인입니다.

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

```

```go
// Go — net.TCPConn에서 직접 설정
conn, _ := net.DialTCP("tcp", nil, addr)
conn.SetNoDelay(true)  // Go net/http는 기본 true

// Go의 net/http 서버는 기본적으로 TCP_NODELAY=true
// gRPC-Go도 기본 TCP_NODELAY=true
// 커스텀 dialer에서 주의:
dialer := &net.Dialer{
    Timeout:   5 * time.Second,
    KeepAlive: 30 * time.Second,
}
```

```kotlin
// Kotlin (Netty 기반 — Spring WebFlux, Ktor)
val bootstrap = ServerBootstrap()
    .childOption(ChannelOption.TCP_NODELAY, true)
    .childOption(ChannelOption.SO_KEEPALIVE, true)

// Ktor 설정
embeddedServer(Netty, port = 8080) {
    // Ktor-Netty는 기본 TCP_NODELAY=true
}
```

**TIME_WAIT 소켓 누적:**

TCP 연결 종료 시 active closer 측이 2 * MSL(Maximum Segment Lifetime, Linux 기본 60초) 동안 TIME_WAIT 상태를 유지합니다. 마이크로서비스에서 짧은 HTTP 요청이 반복되면 수만 개의 TIME_WAIT 소켓이 쌓여 ephemeral port(기본 32768-60999)가 고갈됩니다.

```bash
echo 1 > /proc/sys/net/ipv4/tcp_tw_reuse

echo "1024 65535" > /proc/sys/net/ipv4/ip_local_port_range

```

```python
import httpx

client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20,
        keepalive_expiry=30.0,
    ),
    http2=True,  # HTTP/2 multiplexing으로 커넥션 수 감소
)
```

```go
// Go — http.Transport 커넥션 풀링
transport := &http.Transport{
    MaxIdleConns:        100,
    MaxIdleConnsPerHost: 10,
    IdleConnTimeout:     90 * time.Second,
    // Keep-Alive로 커넥션 재사용 → TIME_WAIT 감소
}
client := &http.Client{Transport: transport}
```

```kotlin
// Kotlin — OkHttp 커넥션 풀링
val client = OkHttpClient.Builder()
    .connectionPool(ConnectionPool(
        maxIdleConnections = 10,
        keepAliveDuration = 5,
        TimeUnit.MINUTES
    ))
    .build()
```

**혼잡 제어 — Cubic vs BBR:**

| 특성 | Cubic (Linux 기본) | BBR (Google) |
|------|-------------------|-------------|
| 신호 | 패킷 로스 기반 | 대역폭 + RTT 측정 기반 |
| 버퍼블로트 | 취약 (버퍼 채울 때까지 증가) | 강건 (BDP 기반 pacing) |
| 데이터센터 | 로스 없는 환경에서 과도한 윈도우 | RTT 기반이라 적합 |
| 공정성 | Cubic 끼리 공정 | Cubic과 공존 시 불공정 가능 |

```bash
echo "net.core.default_qdisc = fq" >> /etc/sysctl.conf
echo "net.ipv4.tcp_congestion_control = bbr" >> /etc/sysctl.conf
sysctl -p

sysctl net.ipv4.tcp_congestion_control
```

데이터센터 내부에서는 DCTCP(Data Center TCP)도 고려할 만합니다. ECN(Explicit Congestion Notification) 마킹을 사용해 로스 없이 혼잡을 감지하며, 스위치 ECN 지원이 필요합니다.

**Step 3 — 다양한 관점**

- **애플리케이션 개발자 관점**: TCP_NODELAY 설정과 커넥션 풀링으로 대부분 해결. 프레임워크가 기본 처리하는 경우가 많으므로 기본값 확인이 중요.
- **SRE/인프라 관점**: sysctl 튜닝, BBR 전환, 커넥션 모니터링(ss -s로 TIME_WAIT 카운트) 필요.
- **네트워크 엔지니어 관점**: 스위치 버퍼 크기, ECN 지원 여부, MTU(Jumbo Frame 9000) 설정이 혼잡 제어 효과에 영향.

**Step 4 — 구체적 예시**

Google 내부에서 BBR 도입 후 YouTube 처리량이 4-14% 향상되었고, RTT가 33-53% 감소했습니다. 데이터센터 내부에서는 Cubic의 sawtooth 패턴이 tail latency를 유발하는데, BBR의 pacing 방식이 이를 완화합니다. Netflix는 BBRv2를 테스트하여 Cubic 대비 p99 지연 개선을 보고했습니다.

TIME_WAIT 실제 사례: 한 회사에서 서비스 간 HTTP/1.1 단발성 요청이 초당 5000개 발생하여 6만 개 TIME_WAIT 소켓이 누적, ephemeral port 고갈로 EADDRNOTAVAIL 에러 발생. 해결: HTTP/2 + 커넥션 풀링 도입으로 활성 커넥션 수를 50개 이하로 감소.

**Step 5 — 트레이드오프 & 대안**

| 해결책 | 장점 | 단점 |
|--------|------|------|
| TCP_NODELAY | 간단, 지연 제거 | 작은 패킷 증가 → 대역폭 낭비 |
| 커넥션 풀링 | TIME_WAIT 근본 해결 | 메모리, idle 커넥션 관리 |
| BBR | 대역폭 효율, 낮은 지연 | Cubic 공존 불공정, 커널 버전 요구 |
| DCTCP | DC 최적화 | ECN 인프라 필요, WAN 부적합 |
| QUIC/HTTP3 | TIME_WAIT 없음, 0-RTT | 아직 DC 내부 채택 낮음 |

**Step 6 — 성장 & 심화**

- **심화 주제**: TCP Fast Open(TFO), MPTCP(Multi-Path TCP), io_uring을 활용한 zero-copy 소켓
- **면접 확장 질문**: "BBR이 Cubic과 공존할 때 공정성 문제를 어떻게 해결하겠는가?" → BBRv2가 ProbeRTT 개선으로 공정성 강화, 또는 DC 내부 전체를 BBR로 통일
- **모니터링 필수**: `ss -ti`로 cwnd, rtt, retrans 확인, `netstat -s`로 TCP 통계

**면접관 평가 기준:**

| 수준 | 기대 답변 |
|------|-----------|
| ✅ **L6 PASS** | Nagle/Delayed ACK 상호작용 설명, TCP_NODELAY + 커넥션 풀링 해결, Cubic vs BBR 차이 설명 |
| 🌟 **L7 EXCEED** | DCTCP/ECN, BBR의 BDP 기반 pacing 모델, TIME_WAIT 문제의 시스템 레벨 해결(tw_reuse + port range), 3개 언어 스택별 소켓 옵션 차이 |
| 🚩 **RED FLAG** | "TCP_NODELAY를 모른다", "TIME_WAIT를 tcp_tw_recycle로 해결" (NAT 환경에서 위험, 커널 4.12에서 제거됨), BBR을 단순 "빠른 TCP"로만 설명 |

---

### Q22: HTTP/2 vs HTTP/3 — multiplexing, QUIC, 0-RTT

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Networking & Protocols

**Question:** "현재 서비스가 HTTP/1.1로 운영 중인데 HTTP/2 또는 HTTP/3(QUIC)로 마이그레이션을 검토하고 있습니다. 각 프로토콜의 multiplexing 방식, 헤더 압축(HPACK vs QPACK), QUIC의 0-RTT 핸드셰이크를 포함하여 기술적 차이를 설명하고, 어떤 상황에서 어떤 프로토콜을 선택해야 하는지 전략을 제시하세요."

---

**12살 비유:**

고속도로를 상상해봐. HTTP/1.1은 차선이 하나인 도로야 — 앞차가 느리면 뒤에 줄 서야 해(Head-of-Line blocking). HTTP/2는 차선이 여러 개인 도로야 — 여러 차가 동시에 달릴 수 있어. 그런데 도로 자체(TCP)에 사고가 나면 모든 차선이 다 막혀. HTTP/3(QUIC)는 아예 각 차에 독립된 터널을 줘서, 한 터널이 막혀도 다른 차는 영향 없이 달리는 거야. 0-RTT는 단골 가게에 전화할 때 "나 김씨인데 항상 먹는 거"라고 바로 주문하는 거 — 처음 가는 가게에서는 안 되지만 자주 가는 곳에서는 시간 절약이지.

**단계별 답변:**

**Step 1 — 맥락**

HTTP 프로토콜 진화의 핵심 동기는 **Head-of-Line(HoL) blocking 제거**입니다. HTTP/1.1은 요청-응답 직렬화로 파이프라이닝이 실패했고, HTTP/2는 TCP 위 바이너리 프레이밍으로 application-layer HoL을 해결했지만 TCP-layer HoL이 남아있으며, HTTP/3는 QUIC(UDP 기반)로 transport-layer HoL까지 제거했습니다.

**Step 2 — 핵심 기술**

**Multiplexing 비교:**

```
HTTP/1.1:  Request1 → Response1 → Request2 → Response2 (직렬)
           (6개 병렬 커넥션으로 우회 → 비효율)

HTTP/2:    ┌─ Stream 1: Req1/Resp1 ─┐
           │─ Stream 3: Req2/Resp2 ─│  (단일 TCP 커넥션)
           └─ Stream 5: Req3/Resp3 ─┘
           ⚠ TCP 패킷 로스 → 모든 스트림 블락

HTTP/3:    ┌─ QUIC Stream 1 ─┐
           │─ QUIC Stream 3 ─│  (독립적 스트림, UDP 위)
           └─ QUIC Stream 5 ─┘
           ✅ Stream 1 로스 → Stream 3,5 영향 없음
```

**헤더 압축:**

HPACK(HTTP/2)은 정적/동적 테이블 + Huffman 인코딩을 사용합니다. 순서 보장이 필요해서 TCP 위에서만 동작합니다. QPACK(HTTP/3)은 HPACK의 HoL 문제를 해결하기 위해 인코더/디코더 스트림을 분리하고, 동적 테이블 업데이트와 헤더 블록 전송을 독립적으로 처리합니다.

```
HPACK 동적 테이블:
  [0] :method GET       ← 인덱스로 참조 (1바이트)
  [1] :path /api/v1     ← 반복 요청 시 크기 극감
  [2] authorization Bearer xxx  ← 큰 헤더도 인덱싱

QPACK 차이점:
  - 인코더 스트림: 동적 테이블 업데이트 지시
  - 디코더 스트림: 업데이트 승인
  - 헤더 블록: 업데이트와 독립적으로 전송 가능
  - Required Insert Count로 디코딩 시점 제어
```

**QUIC 0-RTT:**

```
일반 TLS 1.3 (1-RTT):
  Client → ServerHello     ← 1 RTT
  Client ← EncryptedExts
  Client → Finished + Data  ← 이 시점부터 데이터 전송

QUIC 0-RTT (재연결):
  Client → Initial + 0-RTT Data  ← 첫 패킷부터 데이터!
  Client ← Handshake + 1-RTT Data
  (이전 세션의 PSK + transport params 캐싱)
```

**0-RTT 보안 위험**: Replay attack에 취약합니다. 서버는 0-RTT 데이터를 멱등한 요청(GET)에만 허용하고, anti-replay 메커니즘(strike register, single-use ticket)을 구현해야 합니다.

```python

import httpx
async with httpx.AsyncClient(http2=True) as client:
    resp = await client.get("https://api.example.com/data")
    print(resp.http_version)  # "HTTP/2"
```

```go
// Go — HTTP/2는 net/http 기본 지원
server := &http.Server{
    Addr:    ":443",
    Handler: mux,
    TLSConfig: &tls.Config{
        MinVersion: tls.VersionTLS13,
    },
}
server.ListenAndServeTLS("cert.pem", "key.pem")
// HTTP/2는 TLS 사용 시 자동 활성화 (h2 ALPN)

// HTTP/3 — quic-go 라이브러리
import "github.com/quic-go/quic-go/http3"
http3.ListenAndServeQUIC(":443", "cert.pem", "key.pem", mux)
```

```kotlin
// Kotlin — Ktor HTTP/2
embeddedServer(Netty, port = 8443) {
    // Netty는 ALPN h2 자동 협상
    install(DefaultHeaders)
}.start()

// OkHttp 클라이언트 — HTTP/2 기본 지원
val client = OkHttpClient.Builder()
    .protocols(listOf(Protocol.HTTP_2, Protocol.HTTP_1_1))
    .build()
// HTTP/3: Cronet 라이브러리 (Chromium 기반) 사용
```

**Step 3 — 다양한 관점**

- **프론트엔드/모바일**: HTTP/2 Server Push(현재 Chrome에서 제거됨) 대신 103 Early Hints 사용. 모바일 환경은 네트워크 전환(Wi-Fi→LTE)이 빈번하므로 QUIC의 Connection Migration이 큰 이점.
- **백엔드 서비스 간**: DC 내부는 패킷 로스가 극히 낮아 HTTP/2 HoL 문제가 드물게 발생. gRPC(HTTP/2)가 이미 표준. HTTP/3는 아직 DC 내부 도입 초기 단계.
- **CDN/Edge**: Cloudflare, AWS CloudFront, Akamai 모두 HTTP/3 지원. Edge↔Origin은 HTTP/2, Edge↔Client는 HTTP/3가 일반적 구성.

**Step 4 — 구체적 예시**

Google은 2015년부터 QUIC를 프로덕션에 배포하여 YouTube 리버퍼링을 18% 감소시켰습니다. Cloudflare 데이터에 따르면 HTTP/3는 HTTP/2 대비 TTFB(Time to First Byte)를 12.4% 개선했으며, 특히 고지연(>100ms RTT) 환경에서 효과가 큽니다. Facebook/Meta는 모바일 앱에서 QUIC 사용 시 요청 에러율을 20-50% 감소시켰습니다.

**Step 5 — 트레이드오프 & 대안**

| 프로토콜 | 장점 | 단점 | 최적 사용 사례 |
|----------|------|------|---------------|
| HTTP/1.1 | 단순, 디버깅 쉬움, 방화벽 친화 | HoL blocking, 커넥션 낭비 | 레거시, 단순 API |
| HTTP/2 | 멀티플렉싱, 헤더 압축, 성숙 | TCP HoL, 단일 커넥션 장애 | DC 내부 gRPC, 일반 웹 |
| HTTP/3 | 모든 HoL 제거, 0-RTT, 연결 마이그레이션 | UDP 차단 방화벽, CPU 비용 높음, 디버깅 어려움 | 모바일, 고지연, Edge |

**Step 6 — 성장 & 심화**

- **마이그레이션 전략**: Alt-Svc 헤더로 HTTP/3 점진 도입. `Alt-Svc: h3=":443"; ma=3600` → 클라이언트가 다음 요청부터 QUIC 시도, 실패 시 HTTP/2 폴백
- **QUIC 내부 구조**: 패킷 번호 단조증가(retransmit 구분), ACK Frame에 ECN 카운트 포함, Path Validation으로 NAT rebinding 감지
- **성능 측정**: LightHouse에서 protocol 확인, Chrome DevTools Network 탭의 Protocol 컬럼, `curl --http3` 테스트

**면접관 평가 기준:**

| 수준 | 기대 답변 |
|------|-----------|
| ✅ **L6 PASS** | HTTP/2 multiplexing과 TCP HoL 문제 설명, QUIC가 UDP 기반임을 알고 독립 스트림 이해, HPACK 기본 원리 |
| 🌟 **L7 EXCEED** | QPACK의 인코더/디코더 스트림 분리 이유, 0-RTT replay attack 및 방어 전략, Connection Migration의 CID(Connection ID) 메커니즘, DC 내부 vs Edge 전략 구분 |
| 🚩 **RED FLAG** | "HTTP/3는 그냥 더 빠른 HTTP/2", QUIC이 UDP라서 unreliable하다고 오해, 0-RTT를 보안 위험 없이 모든 요청에 사용 가능하다고 답변 |

---

### Q23: gRPC vs REST — protobuf, streaming, L7 LB

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Networking & Protocols

**Question:** "마이크로서비스 간 통신을 REST에서 gRPC로 전환하는 것을 검토 중입니다. protobuf 직렬화, 4가지 스트리밍 패턴, L7 로드밸런싱의 기술적 차이를 설명하고, 언제 REST를 유지해야 하고 언제 gRPC가 적합한지 판단 기준을 제시하세요."

---

**12살 비유:**

REST는 편지로 대화하는 거야 — 편지(JSON)를 쓰고, 봉투에 주소(URL) 적고, 우체부(HTTP)가 배달해. 누구나 편지를 읽을 수 있어서 편해. gRPC는 무전기로 대화하는 거야 — 암호 코드(protobuf)로 빠르게 말하고, 양방향으로 동시에 말할 수도 있어(streaming). 대신 무전기 주파수(protobuf 스키마)를 양쪽이 미리 맞춰야 해. 로드밸런싱은 여러 무전기 교환원 중 한 명에게 연결하는 건데, REST는 전화 한 통마다 교환원을 바꿀 수 있지만, gRPC는 한번 연결하면 계속 같은 교환원과 대화하니까 다른 방식이 필요해.

**단계별 답변:**

**Step 1 — 맥락**

gRPC는 Google이 내부 Stubby를 공개한 것으로, HTTP/2 위에서 protobuf를 사용하는 고성능 RPC 프레임워크입니다. REST(JSON over HTTP)와의 핵심 차이는: (1) 직렬화 효율, (2) 스트리밍 지원, (3) 강타입 계약, (4) 로드밸런싱 모델입니다. 선택은 "성능 vs 접근성" 트레이드오프입니다.

**Step 2 — 핵심 기술**

**Protobuf 직렬화:**

```protobuf
// user.proto
syntax = "proto3";

message User {
  int64 id = 1;        // 필드 번호 = 와이어 식별자
  string name = 2;
  repeated string tags = 3;
  optional Address address = 4;
}
```

```
JSON:  {"id": 12345, "name": "Alice", "tags": ["admin"]}  → ~52 bytes
Proto: 0x08 B9 60 12 05 41 6C 69 63 65 1A 05 61 64 6D ...  → ~18 bytes
       ↑ field 1, varint    ↑ field 2, length-delimited

직렬화 성능 (벤치마크 기준):
- 크기: protobuf는 JSON 대비 60-80% 작음
- 인코딩 속도: protobuf는 JSON 대비 3-10x 빠름
- 디코딩 속도: protobuf는 JSON 대비 2-5x 빠름
```

```python
import grpc
from concurrent import futures
import user_pb2, user_pb2_grpc

class UserService(user_pb2_grpc.UserServiceServicer):
    async def GetUser(self, request, context):
        # request.id는 이미 int64 (파싱 불필요)
        user = await db.get_user(request.id)
        return user_pb2.User(id=user.id, name=user.name)

    async def ListUsers(self, request, context):
        # Server streaming: 한 명씩 스트리밍
        async for user in db.stream_users(request.filter):
            yield user_pb2.User(id=user.id, name=user.name)

server = grpc.aio.server()
user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
server.add_insecure_port('[::]:50051')
await server.start()
```

```go
// Go — gRPC 서버 (가장 성능이 좋은 gRPC 구현체)
type userServer struct {
    pb.UnimplementedUserServiceServer
}

func (s *userServer) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.User, error) {
    user, err := db.GetUser(ctx, req.Id)
    if err != nil {
        return nil, status.Errorf(codes.NotFound, "user %d not found", req.Id)
    }
    return &pb.User{Id: user.ID, Name: user.Name}, nil
}

// Server streaming
func (s *userServer) ListUsers(req *pb.ListUsersRequest, stream pb.UserService_ListUsersServer) error {
    users, _ := db.ListUsers(req.Filter)
    for _, u := range users {
        if err := stream.Send(&pb.User{Id: u.ID, Name: u.Name}); err != nil {
            return err
        }
    }
    return nil
}
// Go gRPC는 protoc-gen-go-grpc로 코드 생성
```

```kotlin
// Kotlin — gRPC 서버 (grpc-kotlin coroutines)
class UserService : UserServiceGrpcKt.UserServiceCoroutineImplBase() {
    override suspend fun getUser(request: GetUserRequest): User {
        val user = db.getUser(request.id)
            ?: throw StatusException(Status.NOT_FOUND)
        return user { id = user.id; name = user.name }
    }

    // Server streaming → Flow 반환
    override fun listUsers(request: ListUsersRequest): Flow<User> = flow {
        db.streamUsers(request.filter).collect { user ->
            emit(user { id = user.id; name = user.name })
        }
    }
}
// Kotlin gRPC는 protobuf-gradle-plugin + grpc-kotlin
```

**4가지 스트리밍 패턴:**

```
1. Unary:           Client --Request--> Server --Response--> Client
                    (일반 REST와 동일)

2. Server Stream:   Client --Request--> Server ==Response1==> Client
                                               ==Response2==>
                                               ==Response3==>
                    (실시간 피드, 대량 데이터)

3. Client Stream:   Client ==Request1==> Server --Response--> Client
                           ==Request2==>
                           ==Request3==>
                    (파일 업로드, 배치 전송)

4. Bidirectional:   Client ==Request1==> Server ==Response1==> Client
                           ==Request2==>        ==Response2==>
                    (채팅, 실시간 동기화)
```

**L7 로드밸런싱 — 핵심 차이:**

REST(HTTP/1.1)는 요청마다 독립적이므로 L4/L7 어디서든 라운드로빈이 잘 동작합니다. gRPC는 HTTP/2 의 단일 long-lived 커넥션 위에 여러 스트림이 다중화되므로, L4 LB는 커넥션 단위로만 분배하여 한 서버에 모든 트래픽이 몰릴 수 있습니다.

```
L4 LB (TCP) + gRPC 문제:
  Client ──TCP──→ LB ──TCP──→ Server A  (모든 RPC가 A로)
                        ✗    Server B  (유휴)
                        ✗    Server C  (유휴)

해결책 1: L7 LB (Envoy, nginx with grpc_pass)
  Client ──HTTP/2──→ Envoy ──HTTP/2──→ Server A (RPC 1, 4)
                            ──HTTP/2──→ Server B (RPC 2, 5)
                            ──HTTP/2──→ Server C (RPC 3, 6)

해결책 2: 클라이언트 사이드 LB (gRPC 내장)
  Client ──→ Server A (직접 연결)
         ──→ Server B
         ──→ Server C
  (xDS API, DNS, 또는 서비스 디스커버리로 엔드포인트 획득)
```

```go
// Go — gRPC 클라이언트 사이드 로드밸런싱
conn, _ := grpc.Dial(
    "dns:///my-service:50051",  // DNS resolver
    grpc.WithDefaultServiceConfig(`{
        "loadBalancingConfig": [{"round_robin": {}}]
    }`),
    grpc.WithTransportCredentials(insecure.NewCredentials()),
)
// pick_first(기본) → round_robin → 커스텀(weighted, ring_hash)
```

**Step 3 — 다양한 관점**

- **개발 생산성**: REST는 curl, Postman으로 즉시 테스트. gRPC는 grpcurl, Bloom RPC 필요. JSON은 사람이 읽기 쉽고, protobuf는 디버깅 시 디코딩 단계 필요.
- **API 진화**: protobuf의 필드 번호 체계가 하위 호환성을 자연스럽게 지원(새 필드 추가 시 기존 클라이언트 무영향). REST는 URL 버전닝(v1/v2) 전략 필요.
- **브라우저 지원**: 브라우저에서 gRPC 직접 호출 불가(HTTP/2 trailer 접근 제한). gRPC-Web이나 Connect Protocol로 우회. 외부 API는 REST/GraphQL이 실용적.

**Step 4 — 구체적 예시**

Netflix는 내부 서비스 간 통신을 gRPC로 마이그레이션하면서 직렬화 CPU 사용량을 40% 절감했습니다. Square는 gRPC 도입 후 모바일-서버 간 대역폭을 70% 절감했습니다. 반면 Stripe은 외부 API를 REST로 유지하면서 내부만 gRPC를 사용하는 하이브리드 전략을 채택했습니다.

**Step 5 — 트레이드오프 & 대안**

| 기준 | REST (JSON) | gRPC (protobuf) |
|------|-------------|-----------------|
| 성능 | 보통 | 높음 (3-10x 직렬화) |
| 브라우저 | 네이티브 | gRPC-Web 필요 |
| 스트리밍 | SSE/WebSocket 별도 | 4패턴 내장 |
| 디버깅 | curl로 충분 | grpcurl, 전용 도구 |
| 스키마 | OpenAPI (선택) | protobuf (필수) |
| LB | L4/L7 모두 가능 | L7 또는 client-side 필요 |
| 학습 곡선 | 낮음 | 중간 |

**대안**: Connect Protocol(Buf)은 gRPC 호환이면서 HTTP/1.1+JSON 폴백을 지원하여 "gRPC의 성능 + REST의 접근성"을 제공합니다.

**Step 6 — 성장 & 심화**

- **gRPC 고급 기능**: Interceptor(미들웨어), Deadline propagation(timeout 전파), Metadata(HTTP 헤더 유사), Health check protocol, Reflection(런타임 스키마 조회)
- **xDS API**: Envoy의 제어 프로토콜을 gRPC 클라이언트가 직접 사용 → 서비스 메시 없이 고급 라우팅, 가중치 LB, 서킷 브레이커 구현
- **protobuf 대안**: FlatBuffers(zero-copy 디시리얼라이제이션), Cap'n Proto(제로 인코딩 시간), MessagePack(JSON 호환 바이너리)

**면접관 평가 기준:**

| 수준 | 기대 답변 |
|------|-----------|
| ✅ **L6 PASS** | protobuf 바이너리 효율, 4가지 스트리밍 패턴 설명, L7 LB 필요성 이해 |
| 🌟 **L7 EXCEED** | protobuf 와이어 포맷(varint, field number), xDS/클라이언트 사이드 LB 상세, deadline propagation, API 진화 전략(필드 번호 하위호환), Connect Protocol 대안 제시 |
| 🚩 **RED FLAG** | "gRPC가 항상 REST보다 좋다", 브라우저 제약을 모름, L4 LB로 gRPC 분배가 잘 될 것이라 가정 |

---

### Q24: WebSocket at Scale — 백만 커넥션

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Networking & Protocols

**Question:** "실시간 알림 서비스를 설계하는데, 동시 백만 WebSocket 커넥션을 처리해야 합니다. 커넥션 관리, 하트비트 전략, 재연결 로직, 로드밸런싱 아키텍처를 설계하고, 각 언어 런타임(Python/Go/Kotlin)에서 C10M 수준의 커넥션을 어떻게 처리하는지 설명하세요."

---

**12살 비유:**

전화 교환원을 상상해봐. REST는 전화할 때마다 새로 걸어야 하는 거고, WebSocket은 전화를 끊지 않고 계속 연결해놓는 거야. 백만 명이 동시에 전화를 걸어놓으면 교환원(서버)이 엄청 바쁘겠지? 그래서 여러 교환원을 두고(수평 확장), "여보세요?" 하고 주기적으로 확인하고(하트비트), 전화가 끊기면 자동으로 다시 거는(재연결) 시스템이 필요해. 중요한 건 "교환원 A에게 연결됐던 사람이 다시 걸 때 아무 교환원에게 가도 대화가 이어져야" 한다는 거야.

**단계별 답변:**

**Step 1 — 맥락**

WebSocket(RFC 6455)은 HTTP Upgrade를 통해 전이중(full-duplex) TCP 커넥션을 설정합니다. 실시간 서비스(채팅, 알림, 주식 시세, 게임)에서 핵심이지만, stateful한 long-lived 커넥션이라는 특성이 스케일링을 복잡하게 만듭니다. HTTP의 stateless 모델과 근본적으로 다른 운영 전략이 필요합니다.

**Step 2 — 핵심 기술**

**커넥션당 리소스 비용:**

```
커넥션 1개 비용 (Linux):
- File Descriptor: 1개 (ulimit -n 기본 1024 → 변경 필요)
- TCP 소켓 버퍼: recv 87KB + send 16KB ≈ ~100KB (기본값)
- 애플리케이션 메모리: 구현체에 따라 1-10KB
- 총계: ~110KB/conn → 100만 커넥션 ≈ ~110GB (기본값은 비현실적)

최적화 후:
- TCP 버퍼를 4KB로 줄이면: ~14KB/conn → 100만 ≈ ~14GB
- epoll/io_uring으로 스레드 수 최소화
```

```bash
echo "* soft nofile 2000000" >> /etc/security/limits.conf
echo "* hard nofile 2000000" >> /etc/security/limits.conf
echo 2000000 > /proc/sys/fs/file-max

echo "4096 4096 4096" > /proc/sys/net/ipv4/tcp_rmem
echo "4096 4096 4096" > /proc/sys/net/ipv4/tcp_wmem

echo 65535 > /proc/sys/net/core/somaxconn

echo "1024 65535" > /proc/sys/net/ipv4/ip_local_port_range
```

**언어별 구현:**

```python
import asyncio
import websockets

CONNECTIONS = set()

async def handler(websocket):
    CONNECTIONS.add(websocket)
    try:
        async for message in websocket:
            # 메시지 처리
            pass
    finally:
        CONNECTIONS.discard(websocket)

async def broadcast(message: str):
    # 대량 브로드캐스트 — 배치 처리
    if CONNECTIONS:
        await asyncio.gather(
            *[ws.send(message) for ws in CONNECTIONS],
            return_exceptions=True,  # 하나 실패해도 나머지 계속
        )

```

```go
// Go — goroutine 기반 (단일 서버 100만+ 가능)
// gobwas/ws: 커넥션당 goroutine 없이 epoll 직접 사용
import (
    "github.com/gobwas/ws"
    "github.com/gobwas/ws/wsutil"
    "github.com/mailru/easygo/netpoll"
)

// epoll 기반 — 커넥션당 goroutine 불필요
poller, _ := netpoll.New(nil)

func onConnect(conn net.Conn) {
    desc := netpoll.Must(netpoll.HandleRead(conn))
    poller.Start(desc, func(ev netpoll.Event) {
        if ev&netpoll.EventRead != 0 {
            msg, _, _ := wsutil.ReadClientData(conn)
            handleMessage(conn, msg)
        }
    })
}

// 표준 gorilla/websocket: 커넥션당 2 goroutine (read + write)
// 100만 커넥션 = 200만 goroutine → 각 4KB 스택 = ~8GB
// gobwas/ws + epoll: goroutine 최소화 → 메모리 효율 10x
```

```kotlin
// Kotlin — Ktor + Netty (단일 서버 ~200K-500K)
fun Application.configureSockets() {
    install(WebSockets) {
        pingPeriod = Duration.ofSeconds(30)
        timeout = Duration.ofSeconds(15)
        maxFrameSize = Long.MAX_VALUE
    }
    routing {
        webSocket("/ws") {
            val userId = call.parameters["userId"]
            ConnectionManager.add(userId, this)
            try {
                for (frame in incoming) {
                    when (frame) {
                        is Frame.Text -> handleMessage(frame.readText())
                        is Frame.Ping -> send(Frame.Pong(frame.data))
                        else -> {}
                    }
                }
            } finally {
                ConnectionManager.remove(userId)
            }
        }
    }
}

// Netty의 EventLoop 모델: 소수 스레드로 수십만 커넥션 처리
// JVM Heap 튜닝: -Xmx16g -XX:+UseZGC (저지연 GC)
```

**하트비트 전략:**

```
Application-level Heartbeat (권장):
┌─────────┐          ┌─────────┐
│ Client  │──PING──→ │ Server  │    매 30초
│         │←──PONG── │         │    5초 내 응답 없으면 dead
└─────────┘          └─────────┘

TCP Keepalive (보조):
- SO_KEEPALIVE=true, TCP_KEEPIDLE=60, TCP_KEEPINTVL=10, TCP_KEEPCNT=3
- 프록시/LB 뒤에서는 L7 프록시 timeout(예: nginx proxy_read_timeout)도 설정 필요

하트비트 최적화 (백만 커넥션):
- 타이머 휠(Hashed Timer Wheel): O(1) 타이머 추가/제거
- 지터(jitter) 추가: 30s ± 5s로 thundering herd 방지
- 서버→클라이언트 PING 방향 (클라이언트가 보내면 동시 PING 폭풍)
```

**재연결 전략:**

```javascript
// 클라이언트 측 — Exponential Backoff + Jitter
class ReconnectingWebSocket {
    baseDelay = 1000;    // 1초
    maxDelay  = 30000;   // 30초
    attempt   = 0;

    reconnect() {
        const delay = Math.min(
            this.baseDelay * Math.pow(2, this.attempt),
            this.maxDelay
        );
        const jitter = delay * 0.5 * Math.random();
        setTimeout(() => this.connect(), delay + jitter);
        this.attempt++;
    }

    onOpen() {
        this.attempt = 0;  // 성공 시 리셋
        // 마지막 수신 이벤트 ID로 gap 요청
        this.send({ type: "RESUME", lastEventId: this.lastEventId });
    }
}
```

**로드밸런싱 아키텍처:**

```
                    ┌─────────────────────────────┐
                    │       L7 Load Balancer       │
                    │  (Sticky: IP hash or cookie) │
                    └──────┬──────┬──────┬────────┘
                           │      │      │
                    ┌──────▼┐ ┌──▼────┐ ┌▼──────┐
                    │WS GW 1│ │WS GW 2│ │WS GW 3│  (WebSocket Gateway)
                    │ 333K  │ │ 333K  │ │ 333K  │  (커넥션)
                    └──┬────┘ └──┬────┘ └──┬────┘
                       │         │         │
                    ┌──▼─────────▼─────────▼──┐
                    │     Pub/Sub Backbone      │  (Redis Pub/Sub, Kafka, NATS)
                    └──────────────────────────┘
                       │         │         │
                    ┌──▼────┐ ┌─▼─────┐ ┌─▼─────┐
                    │Biz Svc│ │Biz Svc│ │Biz Svc│  (비즈니스 로직)
                    └───────┘ └───────┘ └───────┘

핵심 설계:
1. WebSocket Gateway는 커넥션만 관리 (stateless 비즈니스 로직과 분리)
2. Pub/Sub으로 서버 간 메시지 전달 (User A가 GW1에, User B가 GW2에)
3. 커넥션 레지스트리: Redis에 userId→gatewayId 매핑 저장
4. Graceful drain: 배포 시 새 커넥션 거부 + 기존 커넥션 점진적 이전
```

**Step 3 — 다양한 관점**

- **인프라/비용**: 커넥션당 메모리 비용이 선형 증가하므로 서버 사양 선택이 중요. c5.4xlarge(32GB)에 100K 커넥션 vs r5.8xlarge(256GB)에 100만은 비용 트레이드오프.
- **모바일 관점**: 모바일 네트워크에서 NAT timeout(보통 30-60초)으로 인해 하트비트 주기가 짧아야 함. iOS 백그라운드 제약으로 APNs/FCM 폴백 필요.
- **보안**: WebSocket은 HTTP Upgrade 후 HTTP 보안 미들웨어를 우회할 수 있으므로, 메시지 레벨 인증/인가 필요.

**Step 4 — 구체적 예시**

Slack은 수백만 동시 WebSocket 커넥션을 처리하며, 커넥션 게이트웨이 레이어를 Go로 구현하고 비즈니스 로직은 PHP/Java로 분리했습니다. Discord는 Elixir/Erlang의 경량 프로세스 모델을 활용하여 단일 서버에서 수백만 커넥션을 처리하고, Guild(서버) 단위로 프로세스를 분배합니다. Phoenix LiveView는 200만 동시 WebSocket 커넥션을 단일 서버에서 데모한 바 있습니다.

**Step 5 — 트레이드오프 & 대안**

| 방식 | 장점 | 단점 | 적합 사례 |
|------|------|------|-----------|
| WebSocket | 양방향, 저지연 | stateful, 스케일링 복잡 | 채팅, 게임 |
| SSE (Server-Sent Events) | 단방향, HTTP 호환, 자동 재연결 | 서버→클라이언트만 | 알림, 피드 |
| Long Polling | 가장 호환성 좋음 | 지연, 리소스 낭비 | 레거시 폴백 |
| gRPC Bidirectional Stream | protobuf 효율, 강타입 | 브라우저 미지원 | 서비스 간 실시간 |
| MQTT | IoT 최적화, QoS 레벨 | 별도 브로커 필요 | IoT, 저대역 |

**Step 6 — 성장 & 심화**

- **io_uring**: Linux 5.1+에서 epoll보다 효율적인 비동기 I/O. Go의 netpoll이 io_uring 백엔드 실험 중.
- **QUIC WebSocket**: WebSocket over HTTP/3(RFC 9220)로 TCP HoL 제거 + Connection Migration 활용.
- **Edge WebSocket**: Cloudflare Durable Objects로 Edge에서 WebSocket 상태 관리 — 지연 최소화.

**면접관 평가 기준:**

| 수준 | 기대 답변 |
|------|-----------|
| ✅ **L6 PASS** | 커넥션당 리소스 비용 이해, Pub/Sub 기반 멀티서버 아키텍처, 하트비트+재연결 기본 설계 |
| 🌟 **L7 EXCEED** | epoll vs goroutine 트레이드오프(gobwas/ws), 타이머 휠, graceful drain 전략, 언어별 C10M 한계 분석, 커넥션 레지스트리 + Pub/Sub 상세 설계 |
| 🚩 **RED FLAG** | "서버 스펙을 올리면 된다" (수직 확장만 의존), TCP keepalive만으로 하트비트 충분하다고 답변, 재연결 시 backoff 없이 즉시 재연결 |

---

### Q25: DNS & Service Discovery

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Networking & Protocols

**Question:** "마이크로서비스 환경에서 DNS 기반 서비스 디스커버리의 한계를 설명하고, 서비스 메시(Istio/Linkerd)의 control plane vs data plane 아키텍처, 그리고 DNS TTL이 배포 전략에 미치는 영향까지 포함하여 현대적 서비스 디스커버리 전략을 설계하세요."

---

**12살 비유:**

전화번호부를 상상해봐. DNS는 "김철수네 가게 전화번호"를 찾아주는 전화번호부야. 그런데 전화번호부는 1년에 한 번만 업데이트되잖아(TTL)? 가게가 이사하면 옛날 번호로 전화하게 돼. 서비스 디스커버리는 실시간으로 업데이트되는 스마트폰 연락처 같은 거야. 서비스 메시는 더 나아가서 모든 전화 사이에 비서를 두는 거야 — 비서(sidecar proxy)가 "지금 어디로 전화해야 하는지, 통화 품질이 어떤지, 통화를 녹음해야 하는지" 다 관리해줘. Control plane은 비서들에게 규칙을 알려주는 본사이고, data plane은 실제로 전화를 연결해주는 비서들이야.

**단계별 답변:**

**Step 1 — 맥락**

서비스 디스커버리는 "어떤 서비스 인스턴스가 어디에 있는가"를 동적으로 해결하는 문제입니다. 전통적 DNS는 정적 인프라에 최적화되어 있어, 컨테이너가 초 단위로 생성/소멸하는 현대 환경과 맞지 않습니다. Kubernetes 환경에서 CoreDNS → kube-proxy → Service Mesh로 진화하는 맥락을 이해해야 합니다.

**Step 2 — 핵심 기술**

**DNS 기반 서비스 디스커버리의 한계:**

```
문제 1: TTL 캐싱
  Client가 DNS TTL=30s로 캐싱 → 서버 IP 변경 후 최대 30초 동안 구 서버로 요청
  Java는 기본 DNS TTL이 무한대(!) → JVM 옵션 필요:
    -Dsun.net.inetaddr.ttl=10
  Go: net.DefaultResolver 캐시 없음 (매 요청 DNS 조회 → 성능 문제)
  Python: socket.getaddrinfo() 캐시 없음 (OS 레벨 nscd에 의존)

문제 2: 부하 분산 한계
  DNS 라운드로빈은 가중치 불가, 헬스체크 없음
  A 레코드 3개 반환 → 클라이언트가 항상 첫 번째 선택 가능

문제 3: 헬스체크 부재
  DNS는 "이 서버가 살아있는가"를 모름
  unhealthy 인스턴스의 IP가 TTL 동안 계속 반환

문제 4: 연결 드레이닝
  graceful shutdown 시 DNS 레코드 제거 후에도 TTL 동안 트래픽 수신
```

**Kubernetes 서비스 디스커버리 레이어:**

```
Layer 1: CoreDNS (클러스터 DNS)
  my-service.my-namespace.svc.cluster.local → ClusterIP
  Headless Service: 개별 Pod IP 반환 (StatefulSet에서 사용)

Layer 2: kube-proxy (L4 로드밸런싱)
  ClusterIP → iptables/IPVS 규칙으로 Pod IP에 분배
  iptables: O(n) 규칙 탐색, 5000개 서비스 이상에서 성능 저하
  IPVS: O(1) 해시 기반, 대규모에 적합

Layer 3: Service Mesh (L7 로드밸런싱 + 관측성)
  Sidecar proxy가 모든 트래픽을 인터셉트
  L7 라우팅, mTLS, 재시도, 서킷 브레이커, 메트릭 자동 수집
```

**Control Plane vs Data Plane:**

```
┌─────────────────────────────────────────────────────┐
│                  Control Plane                       │
│  ┌──────────┐ ┌──────────┐ ┌───────────────────┐   │
│  │  istiod   │ │  Config  │ │  Service Registry │   │
│  │(Pilot+    │ │  Store   │ │  (K8s API Server) │   │
│  │ Citadel+  │ │ (etcd)   │ │                   │   │
│  │ Galley)   │ │          │ │                   │   │
│  └─────┬─────┘ └──────────┘ └───────────────────┘   │
│        │ xDS API (LDS, RDS, CDS, EDS)                │
│        │ (Listener, Route, Cluster, Endpoint)        │
└────────┼────────────────────────────────────────────┘
         │
┌────────▼────────────────────────────────────────────┐
│                   Data Plane                         │
│                                                      │
│  ┌────────┐    ┌────────┐    ┌────────┐             │
│  │ Pod A  │    │ Pod B  │    │ Pod C  │             │
│  │┌──────┐│    │┌──────┐│    │┌──────┐│             │
│  ││Envoy ││──→ ││Envoy ││──→ ││Envoy ││             │
│  ││Proxy ││    ││Proxy ││    ││Proxy ││             │
│  │└──────┘│    │└──────┘│    │└──────┘│             │
│  │┌──────┐│    │┌──────┐│    │┌──────┐│             │
│  ││ App  ││    ││ App  ││    ││ App  ││             │
│  │└──────┘│    │└──────┘│    │└──────┘│             │
│  └────────┘    └────────┘    └────────┘             │
│       mTLS 자동         mTLS 자동                    │
└──────────────────────────────────────────────────────┘

xDS API 종류:
- LDS (Listener Discovery): 어떤 포트에서 트래픽을 수신할지
- RDS (Route Discovery): 어떤 경로를 어떤 클러스터로 라우팅할지
- CDS (Cluster Discovery): 업스트림 클러스터 정의 (타임아웃, 서킷브레이커)
- EDS (Endpoint Discovery): 각 클러스터의 실제 엔드포인트 (Pod IP:Port)
```

**DNS TTL과 배포 전략:**

```python
import socket

import aiodns
resolver = aiodns.DNSResolver()
result = await resolver.query("my-service.example.com", "A")
```

```go
// Go — DNS 캐시 구현
// Go net 패키지는 DNS 캐시 없음 → 매번 시스템 resolver 호출
// 프로덕션에서는 dnscache 라이브러리 사용:
import "github.com/rs/dnscache"

r := &dnscache.Resolver{}
go func() {
    t := time.NewTicker(5 * time.Minute)
    for range t.C {
        r.Refresh(true)  // 주기적 리프레시
    }
}()

transport := &http.Transport{
    DialContext: func(ctx context.Context, network, addr string) (net.Conn, error) {
        host, port, _ := net.SplitHostPort(addr)
        ips, _ := r.LookupHost(ctx, host)
        // 라운드로빈 또는 랜덤 선택
        return net.Dial(network, net.JoinHostPort(ips[0], port))
    },
}
```

```kotlin
// Kotlin/JVM — DNS TTL 설정
// JVM은 기본 DNS TTL=무한대 (보안 관련 설정)
// 반드시 변경해야 함:
java.security.Security.setProperty("networkaddress.cache.ttl", "10")
java.security.Security.setProperty("networkaddress.cache.negative.ttl", "5")

// Spring Cloud에서는 서비스 디스커버리 클라이언트:
// Eureka, Consul, 또는 K8s 네이티브 사용
@LoadBalanced
@Bean
fun restTemplate(): RestTemplate = RestTemplate()
// "http://my-service/api" → 자동으로 서비스 디스커버리 + LB
```

**배포 시 DNS TTL 영향:**

```
Blue-Green 배포:
  1. Green 환경 준비 완료
  2. DNS를 Blue → Green으로 전환
  3. TTL 동안 Blue로 트래픽 유입 지속 → 데이터 불일치 위험
  해결: TTL을 미리 낮추기 (배포 전 TTL=5s, 배포 후 TTL=60s)

Canary 배포:
  DNS 가중치 라운드로빈 (Route53 Weighted Routing)
  Blue: 90%, Green: 10% → 점진적으로 Green 비율 증가
  DNS 기반은 정밀도 낮음 → 서비스 메시 기반 Canary가 정밀

Rolling 배포 (K8s 기본):
  kube-proxy가 Endpoint 변경을 감지 → iptables/IPVS 즉시 업데이트
  DNS TTL 무관 — Service ClusterIP는 변경 없음
```

**Step 3 — 다양한 관점**

- **개발자 관점**: "서비스 이름으로 호출하면 된다"가 이상적. K8s Service + CoreDNS가 이를 충족. 서비스 메시는 개발자에게 투명해야 함.
- **플랫폼 팀 관점**: Istio의 리소스 오버헤드(Envoy sidecar당 50-100MB 메모리, 2-5ms 지연 추가) 대비 관측성/보안 이점 평가 필요.
- **멀티 클러스터**: 클러스터 간 서비스 디스커버리는 Istio Multi-Cluster, AWS Cloud Map, 또는 HashiCorp Consul Federation 사용.

**Step 4 — 구체적 예시**

Airbnb는 SmartStack(Nerve + Synapse)에서 Envoy 기반 서비스 메시로 전환하며, 서비스 디스커버리를 ZooKeeper 기반에서 xDS API 기반으로 마이그레이션했습니다. Lyft는 Envoy를 만들면서 자체 서비스 디스커버리의 DNS 한계(TTL 불일치, 헬스체크 부재)를 해결했습니다. Uber는 자체 M3 플랫폼에서 Ringpop(일관된 해싱 기반 peer discovery)을 사용합니다.

**Step 5 — 트레이드오프 & 대안**

| 방식 | 복잡도 | 기능 | 오버헤드 | 적합 규모 |
|------|--------|------|----------|-----------|
| DNS (CoreDNS) | 낮음 | 기본 | 거의 없음 | 소규모 |
| Client-side (Eureka) | 중간 | 헬스체크, LB | SDK 의존 | 중간 |
| kube-proxy (IPVS) | 낮음 | L4 LB | 낮음 | K8s 내부 |
| Service Mesh (Istio) | 높음 | L7 LB, mTLS, 관측성 | sidecar 리소스 | 대규모 |
| Ambient Mesh | 중간 | L4 ztunnel + L7 waypoint | sidecar 없음 | 차세대 |

**Istio Ambient Mesh**: sidecar 없이 노드 레벨 ztunnel(L4 mTLS)과 선택적 waypoint proxy(L7 정책)로 메시 기능을 제공. sidecar 리소스 오버헤드 제거.

**Step 6 — 성장 & 심화**

- **eBPF 기반 서비스 메시**: Cilium은 sidecar 대신 커널 레벨 eBPF로 L3/L4 정책 적용. Envoy와 조합하여 L7도 커버.
- **gRPC xDS**: gRPC 클라이언트가 직접 xDS API를 소비 → sidecar 없이 서비스 메시 기능(LB, 서킷 브레이커) 사용. "proxyless mesh".
- **DNS-over-HTTPS (DoH)**: 보안 향상이지만 캐싱 계층 복잡화. 내부 서비스에는 불필요.

**면접관 평가 기준:**

| 수준 | 기대 답변 |
|------|-----------|
| ✅ **L6 PASS** | DNS TTL 캐싱 문제 이해, K8s Service/CoreDNS 동작 설명, control plane vs data plane 구분 |
| 🌟 **L7 EXCEED** | xDS API 4종 설명(LDS/RDS/CDS/EDS), JVM DNS TTL 무한대 함정, Ambient Mesh/eBPF 차세대 메시, 배포 전략별 DNS TTL 조정 전략 |
| 🚩 **RED FLAG** | "DNS로 충분하다" (동적 환경 무시), sidecar 오버헤드를 고려하지 않고 무조건 Istio 추천, control plane 장애 시 data plane 영향을 모름 (정답: 기존 설정으로 계속 동작) |

---

## Category 5: Observability & SRE

---

### Q26: 폴리글랏 분산 트레이싱 — OpenTelemetry

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Observability & SRE

**Question:** "Python, Go, Kotlin으로 작성된 마이크로서비스들이 혼재된 환경에서 분산 트레이싱을 구축해야 합니다. OpenTelemetry의 아키텍처, W3C TraceContext를 활용한 context propagation, 그리고 폴리글랏 환경에서의 구현 전략을 상세히 설명하세요."

---

**12살 비유:**

택배가 여러 물류센터를 거쳐 배달되는 걸 상상해봐. 각 물류센터가 다른 나라에 있어서 다른 언어를 써(폴리글랏). 택배 상자에 운송장(TraceContext)을 붙이면, 어느 나라 물류센터든 "이 택배가 어디서 왔고, 어디를 거쳤는지" 알 수 있어. OpenTelemetry는 모든 나라가 합의한 "국제 운송장 표준"이야. Trace ID는 택배 번호, Span은 각 물류센터에서의 처리 기록이야. 마지막에 모든 기록을 모으면 "택배가 어디서 오래 걸렸는지" 한눈에 볼 수 있지.

**단계별 답변:**

**Step 1 — 맥락**

분산 시스템에서 요청 하나가 10개 이상의 서비스를 거칠 때, 어디서 지연이 발생했는지 찾는 것은 가장 중요한 관측성(Observability) 과제입니다. OpenTelemetry(OTel)는 CNCF 프로젝트로 Jaeger/Zipkin/Datadog 등 벤더 중립적인 계측 표준을 제공합니다. 핵심 개념: **Traces**(요청 전체 경로), **Spans**(개별 작업 단위), **Context Propagation**(서비스 간 추적 정보 전달).

**Step 2 — 핵심 기술**

**OpenTelemetry 아키텍처:**

```
┌──────────────────────────────────────────────────────────┐
│                    Application Code                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Auto-Instrum │  │ Manual Spans │  │   Metrics    │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         └────────────┬────┘                  │           │
│              ┌───────▼────────┐              │           │
│              │  OTel SDK      │              │           │
│              │  (TracerProvider,│             │           │
│              │   SpanProcessor)│             │           │
│              └───────┬────────┘              │           │
│                      │ OTLP (gRPC/HTTP)      │           │
└──────────────────────┼───────────────────────┼───────────┘
                       │                       │
              ┌────────▼───────────────────────▼──┐
              │       OTel Collector               │
              │  ┌──────────┐ ┌──────────────────┐ │
              │  │Receivers │ │   Processors     │ │
              │  │(OTLP,    │ │(batch, filter,   │ │
              │  │ Jaeger,  │ │ tail sampling,   │ │
              │  │ Zipkin)  │ │ resource detect) │ │
              │  └──────────┘ └──────────────────┘ │
              │  ┌──────────────────────────────┐  │
              │  │       Exporters              │  │
              │  │(Jaeger, Tempo, Datadog, X-Ray)│ │
              │  └──────────────────────────────┘  │
              └────────────────────────────────────┘
```

**W3C TraceContext:**

```
HTTP 헤더:
  traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
               ↑   ↑ Trace ID (128bit)          ↑ Parent Span ID  ↑ Flags
               version                           (64bit)            (sampled=01)

  tracestate: vendor1=value1,vendor2=value2
              (벤더별 추가 정보, 예: congo=t61rcWkgMzE)

전파(Propagation) 흐름:
  Service A (Python) → HTTP → Service B (Go) → gRPC → Service C (Kotlin)

  A: traceparent 생성 → HTTP 헤더에 삽입
  B: traceparent 추출 → 새 Span 생성 (parent=A의 span) → gRPC metadata에 삽입
  C: traceparent 추출 → 새 Span 생성 (parent=B의 span)
```

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.composite import CompositeHTTPPropagator
from opentelemetry.trace.propagation import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator

set_global_textmap(CompositeHTTPPropagator([
    TraceContextTextMapPropagator(),
    W3CBaggagePropagator(),
]))

provider = TracerProvider(
    resource=Resource.create({
        "service.name": "user-service",
        "service.version": "1.2.0",
        "deployment.environment": "production",
    })
)
provider.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(endpoint="otel-collector:4317"),
    max_queue_size=2048,
    max_export_batch_size=512,
    schedule_delay_millis=5000,
))
trace.set_tracer_provider(provider)

FastAPIInstrumentor.instrument()
HTTPXClientInstrumentor().instrument()
SQLAlchemyInstrumentor().instrument(engine=engine)

tracer = trace.get_tracer("user-service")
async def get_user(user_id: int):
    with tracer.start_as_current_span("db.get_user",
        attributes={"user.id": user_id}
    ) as span:
        user = await db.find(user_id)
        span.set_attribute("user.found", user is not None)
        if not user:
            span.set_status(trace.Status(trace.StatusCode.ERROR, "User not found"))
        return user
```

```go
// Go — OpenTelemetry 설정
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/propagation"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    "go.opentelemetry.io/otel/sdk/resource"
    semconv "go.opentelemetry.io/otel/semconv/v1.24.0"
    "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
    "go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"
)

func initTracer(ctx context.Context) (*sdktrace.TracerProvider, error) {
    exporter, _ := otlptracegrpc.New(ctx,
        otlptracegrpc.WithEndpoint("otel-collector:4317"),
        otlptracegrpc.WithInsecure(),
    )

    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter,
            sdktrace.WithMaxQueueSize(2048),
            sdktrace.WithBatchTimeout(5*time.Second),
        ),
        sdktrace.WithResource(resource.NewWithAttributes(
            semconv.SchemaURL,
            semconv.ServiceName("order-service"),
            semconv.ServiceVersion("2.0.1"),
            semconv.DeploymentEnvironment("production"),
        )),
        sdktrace.WithSampler(sdktrace.ParentBased(
            sdktrace.TraceIDRatioBased(0.1), // 10% 샘플링
        )),
    )

    // W3C TraceContext propagator
    otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
        propagation.TraceContext{},
        propagation.Baggage{},
    ))
    otel.SetTracerProvider(tp)
    return tp, nil
}

// HTTP 미들웨어 자동 계측
handler := otelhttp.NewHandler(mux, "server")

// gRPC 자동 계측
grpcServer := grpc.NewServer(
    grpc.UnaryInterceptor(otelgrpc.UnaryServerInterceptor()),
    grpc.StreamInterceptor(otelgrpc.StreamServerInterceptor()),
)
```

```kotlin
// Kotlin — OpenTelemetry (Java Agent 기반)
// JVM에서는 Java Agent로 zero-code 계측 가능:
// java -javaagent:opentelemetry-javaagent.jar \
//   -Dotel.service.name=payment-service \
//   -Dotel.exporter.otlp.endpoint=http://otel-collector:4317 \
//   -Dotel.traces.sampler=parentbased_traceidratio \
//   -Dotel.traces.sampler.arg=0.1 \
//   -jar app.jar

// 수동 계측 (SDK 직접 사용)
val tracer = GlobalOpenTelemetry.getTracer("payment-service")

suspend fun processPayment(orderId: String, amount: BigDecimal): PaymentResult {
    val span = tracer.spanBuilder("payment.process")
        .setAttribute("order.id", orderId)
        .setAttribute("payment.amount", amount.toDouble())
        .startSpan()

    return span.makeCurrent().use { scope ->
        try {
            val result = paymentGateway.charge(orderId, amount)
            span.setAttribute("payment.status", result.status.name)
            result
        } catch (e: Exception) {
            span.recordException(e)
            span.setStatus(StatusCode.ERROR, e.message ?: "Payment failed")
            throw e
        } finally {
            span.end()
        }
    }
}

// Spring Boot + OTel: spring-cloud-sleuth는 Micrometer Tracing으로 이전
// implementation("io.micrometer:micrometer-tracing-bridge-otel")
```

**Sampling 전략:**

```
1. Head-based Sampling (SDK에서):
   - TraceIDRatioBased(0.1): 10%만 수집
   - ParentBased: 부모 Span의 결정을 따름
   - 장점: 리소스 절약 / 단점: 중요 에러 트레이스 누락 가능

2. Tail-based Sampling (Collector에서):
   - 트레이스 완성 후 에러/지연 기준으로 결정
   - OTel Collector의 tail_sampling processor
   processors:
     tail_sampling:
       decision_wait: 10s
       policies:
         - name: errors
           type: status_code
           status_code: { status_codes: [ERROR] }
         - name: slow-traces
           type: latency
           latency: { threshold_ms: 500 }
         - name: default
           type: probabilistic
           probabilistic: { sampling_percentage: 5 }
   - 장점: 에러 트레이스 100% 포착 / 단점: Collector 메모리 사용 증가

3. Always-on + 경량 수집:
   - 모든 Span 메타데이터 수집, 상세 속성은 샘플링
   - Google Cloud Trace 방식
```

**Step 3 — 다양한 관점**

- **개발자 관점**: 자동 계측(auto-instrumentation)으로 코드 변경 없이 시작. 비즈니스 로직에 수동 Span 추가는 점진적으로.
- **SRE 관점**: Collector 파이프라인 설계가 핵심 — 버퍼링, 배치, 재시도, 백프레셔. Collector 장애 시 데이터 유실 vs 애플리케이션 영향 트레이드오프.
- **비용 관점**: Datadog APM은 인제스트 Span당 과금. Grafana Tempo는 오브젝트 스토리지 기반으로 비용 효율적. 샘플링이 비용에 직결.

**Step 4 — 구체적 예시**

Uber는 Jaeger를 만들어 수천 개 서비스(Go/Java/Python)의 트레이싱을 통합했으며, adaptive sampling으로 초당 수백만 Span을 효율적으로 처리합니다. Google은 Dapper 논문에서 "always-on tracing"이 가능함을 보여줬고, 이것이 OpenTelemetry의 이론적 기반이 되었습니다. Grafana Labs는 Tempo에서 trace-to-logs, trace-to-metrics 연계를 구현하여 Three Pillars(Logs/Metrics/Traces) 통합을 실현했습니다.

**Step 5 — 트레이드오프 & 대안**

| 계측 방식 | 장점 | 단점 |
|-----------|------|------|
| Auto-instrumentation | 코드 변경 없음, 빠른 도입 | 커스텀 비즈니스 정보 부족 |
| SDK 수동 계측 | 정밀한 비즈니스 Span | 코드 침투, 유지보수 비용 |
| eBPF 기반 | 완전 무침투, 커널 레벨 | L7 프로토콜 인식 제한 |

| 백엔드 | 특징 | 비용 모델 |
|--------|------|-----------|
| Jaeger (self-hosted) | 오픈소스, Elasticsearch/Cassandra 저장 | 인프라 비용 |
| Grafana Tempo | S3/GCS 저장, 저비용 | 인프라 비용 |
| Datadog APM | 풍부한 UI, anomaly detection | Span당 과금 |
| AWS X-Ray | AWS 통합 | Trace당 과금 |

**Step 6 — 성장 & 심화**

- **Continuous Profiling**: OTel에 profiling signal 추가 예정. Trace-to-profile 연계로 "이 느린 Span에서 어떤 함수가 CPU를 잡아먹었는가" 확인 가능.
- **Context propagation beyond HTTP**: Kafka 메시지 헤더, SQS 메시지 속성, Redis pub/sub에도 traceparent 전파 필요 → 비동기 처리 추적.
- **W3C Baggage**: 트레이스 컨텍스트와 별도로 key-value 데이터를 서비스 간 전파. 예: tenant-id, feature-flag 값.

**면접관 평가 기준:**

| 수준 | 기대 답변 |
|------|-----------|
| ✅ **L6 PASS** | OTel SDK/Collector 아키텍처, W3C traceparent 구조, 자동 vs 수동 계측 구분 |
| 🌟 **L7 EXCEED** | Tail-based sampling 설계, Collector 파이프라인 커스터마이징, 비동기 메시지 context propagation, 3개 언어 구현 차이(Java Agent vs Python auto-instrumentation vs Go interceptor) |
| 🚩 **RED FLAG** | context propagation 없이 독립적으로 Span만 생성, 샘플링 전략 없이 100% 수집 주장, 벤더 종속 SDK만 사용(OTel 무시) |

---

### Q27: SLO/SLI 설계 — error budget, burn rate

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Observability & SRE

**Question:** "서비스의 SLI를 정의하고 SLO를 설정한 후, error budget 기반 의사결정과 burn rate alert를 설계하는 전체 과정을 설명하세요. multi-window, multi-burn-rate alert 전략까지 포함하여 실제 프로덕션 환경에서 어떻게 운영하는지 보여주세요."

---

**12살 비유:**

시험 점수로 생각해봐. SLO는 "이번 학기 평균 95점 이상 유지하자"는 목표야. SLI는 실제 시험 점수야. Error budget은 "5점까지는 깎여도 괜찮다"는 여유분이야. 한 달에 시험이 여러 번 있는데, 한 번 60점을 받으면(장애) error budget이 확 줄어들지. Burn rate는 "지금 이 속도로 점수가 떨어지면 학기 끝나기 전에 여유분이 바닥난다"는 경고야. 빨리 깎이면 빨리 경고하고(1시간 윈도우), 천천히 깎여도 오래 지속되면 경고해(6시간 윈도우) — 이게 multi-window alert이야.

**단계별 답변:**

**Step 1 — 맥락**

SRE의 핵심 철학은 "100% 가용성은 목표가 아니다"입니다. 신뢰성과 변경 속도(feature velocity) 사이의 균형을 **정량적으로** 관리하는 것이 SLO/Error Budget의 목적입니다. Google SRE Book과 The Art of SLOs 워크숍의 내용을 기반으로 합니다.

**Step 2 — 핵심 기술**

**SLI 정의 — 사용자 관점:**

```
좋은 SLI = 사용자가 체감하는 것을 측정

┌──────────────────────────────────────────────┐
│           SLI 유형별 정의                      │
├──────────────┬───────────────────────────────┤
│ 가용성        │ 성공 요청 수 / 전체 요청 수     │
│ 지연          │ p99 < 300ms인 요청 비율         │
│ 처리량        │ 정상 처리된 작업 수 / 전체 작업   │
│ 정확성        │ 올바른 응답 수 / 전체 응답 수     │
│ 신선도        │ TTL 내 업데이트된 데이터 비율     │
│ 내구성        │ 복구 가능한 데이터 비율           │
└──────────────┴───────────────────────────────┘

핵심 원칙:
- 서버 메트릭이 아닌 사용자 여정 기반
- "서버 CPU 80%"는 SLI가 아님
- "체크아웃 요청의 99.9%가 1초 내 성공"이 SLI
```

**SLO 설정:**

```
SLO: 지난 30일(rolling window) 동안 99.9% 가용성

Error Budget 계산:
  30일 = 30 × 24 × 60 = 43,200분
  0.1% error budget = 43,200 × 0.001 = 43.2분 허용 다운타임

  99.9% → 43.2분/월
  99.95% → 21.6분/월
  99.99% → 4.32분/월

  또는 요청 기반:
  월 1억 요청 × 0.1% = 10만 건 에러 허용
```

**Burn Rate & Multi-Window Alert:**

```
Burn rate = 실제 에러율 / SLO 에러율

예시: SLO 99.9% → 에러 예산율 0.1%
  현재 에러율 1% → burn rate = 1% / 0.1% = 10x
  "10배 속도로 예산 소진 중" → 3일 만에 30일 예산 소진

Multi-burn-rate, Multi-window Alert (Google 권장):
┌──────────┬────────────┬─────────────┬────────────────────┐
│ Severity │ Burn Rate  │ Long Window │ Short Window       │
├──────────┼────────────┼─────────────┼────────────────────┤
│ PAGE     │ 14.4x      │ 1h          │ 5m                 │
│ PAGE     │ 6x         │ 6h          │ 30m                │
│ TICKET   │ 3x         │ 1d          │ 2h                 │
│ TICKET   │ 1x         │ 3d          │ 6h                 │
└──────────┴────────────┴─────────────┴────────────────────┘

왜 Multi-window?
- Long window만: 느린 응답 → 사후 대응
- Short window만: 스파이크에 과민 반응 (false positive)
- 둘 다 충족 시에만 알림 → 정밀도 ↑

14.4x in 1h: 1시간에 예산의 2% 소진 (1/720 × 14.4 = 0.02)
             → 이 속도 유지 시 약 2.08일 만에 예산 소진 → 긴급 PAGE
```

```python

SLI_RECORDING_RULES = """
groups:
  - name: sli_rules
    rules:
      # 가용성 SLI: 성공 요청 비율
      - record: sli:http_requests:availability
        expr: |
          sum(rate(http_requests_total{status!~"5.."}[5m]))
          /
          sum(rate(http_requests_total[5m]))

      # 지연 SLI: p99 < 300ms 비율
      - record: sli:http_requests:latency
        expr: |
          sum(rate(http_request_duration_seconds_bucket{le="0.3"}[5m]))
          /
          sum(rate(http_request_duration_seconds_count[5m]))
"""

BURN_RATE_ALERTS = """
groups:
  - name: burn_rate_alerts
    rules:
      # 14.4x burn rate, 1h/5m window → PAGE
      - alert: HighErrorBurnRate_Page
        expr: |
          (
            1 - sli:http_requests:availability:rate1h > 14.4 * 0.001
          )
          and
          (
            1 - sli:http_requests:availability:rate5m > 14.4 * 0.001
          )
        labels:
          severity: page
        annotations:
          summary: "Error budget burn rate is 14.4x (1h window)"
          dashboard: "https://grafana.example.com/d/slo-dashboard"

      # 6x burn rate, 6h/30m window → PAGE
      - alert: MediumErrorBurnRate_Page
        expr: |
          (
            1 - sli:http_requests:availability:rate6h > 6 * 0.001
          )
          and
          (
            1 - sli:http_requests:availability:rate30m > 6 * 0.001
          )
        labels:
          severity: page

      # 3x burn rate, 1d/2h window → TICKET
      - alert: LowErrorBurnRate_Ticket
        expr: |
          (
            1 - sli:http_requests:availability:rate1d > 3 * 0.001
          )
          and
          (
            1 - sli:http_requests:availability:rate2h > 3 * 0.001
          )
        labels:
          severity: ticket
"""
```

```go
// Go — SLI 계측 미들웨어
import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    httpRequestsTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total HTTP requests",
        },
        []string{"method", "path", "status"},
    )
    httpRequestDuration = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "http_request_duration_seconds",
            Help:    "HTTP request latency",
            Buckets: []float64{0.01, 0.05, 0.1, 0.3, 0.5, 1.0, 2.0, 5.0},
            // SLO 임계값(0.3s)을 반드시 버킷에 포함
        },
        []string{"method", "path"},
    )
)

func sliMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        rw := &responseWriter{ResponseWriter: w, statusCode: 200}
        next.ServeHTTP(rw, r)
        duration := time.Since(start).Seconds()

        httpRequestsTotal.WithLabelValues(
            r.Method, r.URL.Path, strconv.Itoa(rw.statusCode),
        ).Inc()
        httpRequestDuration.WithLabelValues(
            r.Method, r.URL.Path,
        ).Observe(duration)
    })
}
```

```kotlin
// Kotlin — Micrometer 기반 SLI
@Configuration
class SliMetricsConfig {
    @Bean
    fun sliTimerFilter(): WebFilter = WebFilter { exchange, chain ->
        val start = System.nanoTime()
        chain.filter(exchange).doFinally {
            val duration = (System.nanoTime() - start) / 1_000_000_000.0
            val status = exchange.response.statusCode?.value() ?: 0
            Metrics.counter("http_requests_total",
                "method", exchange.request.method.name(),
                "status", status.toString()
            ).increment()
            Metrics.timer("http_request_duration_seconds",
                "method", exchange.request.method.name()
            ).record(Duration.ofNanos(System.nanoTime() - start))
        }
    }
}

// Spring Boot Actuator + Micrometer → Prometheus 자동 연동
// management.endpoints.web.exposure.include=prometheus
// management.metrics.distribution.slo.http.server.requests=100ms,300ms,500ms,1s
```

**Error Budget 기반 의사결정:**

```
┌─────────────────────────────────────────────────┐
│              Error Budget Policy                 │
├──────────────────┬──────────────────────────────┤
│ Budget > 50%     │ 자유롭게 배포, 실험 가능       │
│ Budget 20-50%    │ 배포 계속, 추가 테스트 강화     │
│ Budget 5-20%     │ 변경 동결 검토, 리스크 높은 배포 중단 │
│ Budget < 5%      │ 변경 동결, 안정성 개선에만 집중  │
│ Budget 소진       │ 완전 변경 동결, postmortem 필수 │
└──────────────────┴──────────────────────────────┘

핵심: Error Budget은 팀 간 협상 도구
- 제품팀: "빨리 배포하고 싶다"
- SRE팀: "안정성이 우려된다"
→ Error Budget 잔량이 객관적 판단 기준
```

**Step 3 — 다양한 관점**

- **제품 관리자 관점**: SLO는 사용자 기대치와 일치해야 함. 99.99%를 목표로 하면 변경 속도가 극도로 느려짐. 대부분의 서비스는 99.9%로 충분.
- **엔지니어링 관점**: SLO 기반 온콜 부담 관리. Error budget 소진 시에만 PAGE → 불필요한 야간 호출 감소.
- **경영진 관점**: SLO는 비즈니스 KPI와 연결되어야 함. "99.9% 가용성 미달 시 월 매출 X% 감소" 같은 정량화.

**Step 4 — 구체적 예시**

Google은 내부적으로 모든 서비스에 SLO를 설정하고, error budget 소진 시 자동으로 변경 동결(change freeze)을 시행합니다. Spotify는 SLO를 "Golden Signals"(지연, 트래픽, 에러, 포화도)에 기반하여 정의하고, 팀 자율적으로 SLO 수준을 결정합니다. LinkedIn은 SLO 대시보드를 경영진에게 공유하여 인프라 투자 의사결정에 활용합니다.

**Step 5 — 트레이드오프 & 대안**

| 알림 방식 | 장점 | 단점 |
|-----------|------|------|
| 임계값 기반 (에러율>1%) | 단순, 이해 쉬움 | 문맥 부재, false positive 많음 |
| Burn rate 단일 윈도우 | 예산 소진 예측 | 스파이크/느린 저하 구분 못함 |
| Multi-window burn rate | 정밀, false positive 최소 | 설정 복잡, 이해 필요 |
| Anomaly detection | 자동 임계값 | 블랙박스, 오탐/미탐 위험 |

**Step 6 — 성장 & 심화**

- **SLO as Code**: OpenSLO 표준(YAML)으로 SLO를 코드로 관리. Sloth(Prometheus)나 Google SLO Generator로 자동 recording rule + alert 생성.
- **Composite SLO**: 여러 SLI를 가중 평균하여 단일 SLO 구성. "가용성 × 0.6 + 지연 × 0.4"
- **SLO 리뷰 프로세스**: 분기별 SLO 리뷰 미팅 — 목표 적절성 검토, 사용자 기대치 변화 반영, error budget 사용 패턴 분석.

**면접관 평가 기준:**

| 수준 | 기대 답변 |
|------|-----------|
| ✅ **L6 PASS** | SLI/SLO/Error Budget 정의와 관계, burn rate 개념, 요청 기반 vs 시간 기반 SLI 구분 |
| 🌟 **L7 EXCEED** | Multi-window, multi-burn-rate alert 설계 (14.4x/6x/3x/1x), error budget policy 구체화, SLO를 팀 간 협상 도구로 설명, recording rule 최적화 |
| 🚩 **RED FLAG** | SLO를 "목표 가용성"으로만 이해(error budget 모름), 모든 서비스에 99.99% 제시, burn rate 없이 단순 임계값 알림만 설계 |

---

### Q28: 인시던트 대응 — on-call, postmortem

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Observability & SRE

**Question:** "on-call 로테이션 구조, 인시던트 대응 프로세스, blameless postmortem 문화를 어떻게 설계하고 운영하시겠습니까? 인시던트 발생부터 해결, 사후 분석, 재발 방지까지의 전체 사이클을 설명하세요."

---

**12살 비유:**

소방서를 상상해봐. On-call은 당직 소방관이야 — 항상 누군가가 전화를 받을 준비가 되어 있어야 해. 인시던트는 화재 신고야 — 불이 나면 먼저 끄고(mitigate), 나중에 원인을 찾아(investigate). Postmortem은 화재 조사 보고서야 — "누가 불을 냈는가"가 아니라 "왜 스프링클러가 작동하지 않았는가"를 찾는 거야(blameless). 이 보고서를 보고 다음에는 스프링클러를 고치고, 화재 감지기를 더 설치하는 거지(action items).

**단계별 답변:**

**Step 1 — 맥락**

인시던트 관리는 기술적 문제이자 조직적 문제입니다. Google, Meta, Netflix 등의 SRE 조직은 인시던트 대응을 체계적 프로세스로 표준화하고, blameless 문화를 통해 조직 학습을 극대화합니다. 핵심은 "개인 실수를 비난하지 않되, 시스템 개선은 반드시 실행한다"는 것입니다.

**Step 2 — 핵심 기술**

**On-call 구조 설계:**

```
┌─────────────────────────────────────────────────┐
│              On-call Structure                   │
├──────────────┬──────────────────────────────────┤
│ Primary      │ 최초 응답자, 5분 내 응답 의무     │
│ Secondary    │ Primary 미응답 시 10분 후 에스컬   │
│ Escalation   │ 30분 미해결 시 TL/Manager         │
│ SME (Subject │ 특정 서비스 전문가, 필요 시 호출   │
│ Matter Expert)│                                  │
└──────────────┴──────────────────────────────────┘

로테이션 모범 사례:
- 1주 단위 로테이션 (2주는 피로도 과다)
- 팀 최소 5명 → 5주에 1주 on-call (부담 20%)
- 야간(18-09) 호출 시 다음 날 오전 off
- 인수인계 문서: 현재 진행 중 이슈, 주의 서비스, 최근 변경사항
- Follow-the-sun: 글로벌 팀이면 시간대별 핸드오프
```

**인시던트 대응 프로세스:**

```
Phase 1: Detection (감지)                    [0-5분]
  ├─ 자동: 모니터링 알림 (PagerDuty/OpsGenie)
  ├─ 수동: 사용자 리포트, 동료 호출
  └─ 판단: Severity 분류
      SEV1: 전체 서비스 다운, 매출 영향      → 즉시 War Room
      SEV2: 부분 기능 장애, 일부 사용자 영향  → 30분 내 대응
      SEV3: 성능 저하, workaround 가능       → 업무 시간 대응
      SEV4: 미미한 영향                      → 백로그

Phase 2: Triage & Communication (분류 & 소통) [5-15분]
  ├─ Incident Commander(IC) 지정
  ├─ 커뮤니케이션 채널 개설 (Slack #inc-YYYYMMDD-title)
  ├─ 상태 페이지 업데이트 (Statuspage.io)
  └─ 이해관계자 통보 (자동화)

Phase 3: Mitigation (완화)                   [15분-?]
  ├─ 원인 찾기 전에 영향 줄이기가 우선!
  ├─ 전략:
  │   ├─ 롤백: 최근 배포가 원인이면 즉시 롤백
  │   ├─ 트래픽 전환: 장애 리전에서 정상 리전으로
  │   ├─ 기능 플래그 OFF: 문제 기능 비활성화
  │   ├─ 스케일 업/아웃: 부하 문제 시
  │   └─ 서킷 브레이커: 의존 서비스 차단
  └─ IC가 타임라인 기록 (분 단위)

Phase 4: Resolution (해결)
  ├─ 근본 원인 식별 및 수정
  ├─ 정상 상태 확인 (SLI 복구)
  └─ 인시던트 종료 선언

Phase 5: Postmortem (사후 분석)               [48시간 내]
  └─ 별도 프로세스 (아래 상세)
```

**Incident Commander(IC) 역할:**

```
IC의 핵심 원칙:
1. IC는 직접 디버깅하지 않음 — 조율에 집중
2. 명확한 위임: "Alice, 데이터베이스 상태 확인해주세요"
3. 주기적 상태 업데이트: 15분마다 요약 공유
4. 의사결정 기록: 왜 롤백 대신 hotfix를 선택했는지

IC 체크리스트:
□ Severity 확정
□ 커뮤니케이션 채널 개설
□ 역할 배정 (조사, 소통, 기록)
□ 15분 간격 상태 업데이트
□ 타임라인 기록
□ 이해관계자 통보
□ 해결 후 인시던트 종료 선언
□ 48시간 내 postmortem 일정 잡기
```

**Blameless Postmortem:**

```markdown
## Postmortem: 결제 서비스 장애 (2026-03-15)

### Incident Summary
- **Duration**: 14:23 - 15:07 UTC (44분)
- **Severity**: SEV1
- **Impact**: 결제 성공률 45% → 정상 99.9%
- **Affected**: 약 12,000명 사용자, 추정 매출 손실 $180K

### Timeline (UTC)
| 시각 | 이벤트 |
|------|--------|
| 14:20 | DB 마이그레이션 배포 (인덱스 추가) |
| 14:23 | 결제 API p99 지연 300ms → 15s |
| 14:25 | PagerDuty SEV1 알림, Primary on-call 응답 |
| 14:28 | IC 지정, #inc-20260315-payment 채널 개설 |
| 14:35 | DB 락 경합 확인, 마이그레이션이 테이블 락 획득 |
| 14:42 | 마이그레이션 중단 시도 → 실패 (이미 진행 중) |
| 14:50 | 읽기 트래픽을 replica로 전환 |
| 15:02 | 마이그레이션 완료, 락 해제 |
| 15:07 | SLI 정상 복구, 인시던트 종료 |

### Root Cause
대용량 테이블(1.2B rows)에 인덱스 추가 마이그레이션이
테이블 레벨 락을 획득하여 모든 쓰기 쿼리 블록.
마이그레이션이 `ALGORITHM=INPLACE, LOCK=NONE` 옵션 없이 실행됨.

### Contributing Factors (NOT "Who")
1. 마이그레이션 리뷰 체크리스트에 "대용량 테이블" 기준 없었음
2. 프로덕션 DB 마이그레이션의 스테이징 테스트가 소규모 데이터로만 수행
3. 마이그레이션 자동 롤백 메커니즘 부재

### What Went Well
- 알림이 2분 내 발동 (빠른 감지)
- IC가 신속하게 역할 배정 (효과적 소통)
- replica 전환으로 읽기 트래픽 복구 (부분 완화)

### Action Items
| # | Action | Owner | Priority | Due |
|---|--------|-------|----------|-----|
| 1 | 마이그레이션 체크리스트에 테이블 크기 기준 추가 | DB팀 | P0 | 1주 |
| 2 | gh-ost/pt-online-schema-change 도입 | DB팀 | P0 | 2주 |
| 3 | 스테이징에 프로덕션 규모 데이터 미러링 | 인프라 | P1 | 1달 |
| 4 | 마이그레이션 자동 영향 분석 도구 개발 | 플랫폼 | P2 | 분기 |
```

**Blameless 문화의 핵심:**

```
❌ "Bob이 마이그레이션 옵션을 빠뜨렸다"
✅ "마이그레이션 도구가 위험한 옵션을 기본값으로 사용했다"

❌ "Alice가 테스트를 안 했다"
✅ "CI/CD 파이프라인에 대용량 테이블 마이그레이션 검증 단계가 없었다"

원칙:
1. 사람이 아닌 시스템/프로세스를 개선 대상으로
2. "왜 그 선택을 했는가?"를 이해 (당시 맥락에서 합리적이었을 수 있음)
3. Action Items는 자동화/도구/가드레일로 — "더 주의하자"는 AI가 아님
4. Postmortem은 학습 자산 — 검색 가능하게 저장, 정기적 리뷰
```

**Step 3 — 다양한 관점**

- **엔지니어 관점**: On-call 부담이 과도하면 번아웃. "toil budget" 관리 필요 — 수동 작업을 자동화로 대체하여 on-call 부담 감소.
- **관리자 관점**: Postmortem action items의 완료율 추적이 중요. 미완료 AI가 쌓이면 같은 사고 반복.
- **비즈니스 관점**: 인시던트의 비즈니스 영향(매출 손실, 사용자 이탈)을 정량화하여 인프라 투자 근거로 활용.

**Step 4 — 구체적 예시**

Google의 SRE 팀은 postmortem을 "공개 문서"로 관리하며, 전사적으로 공유하여 다른 팀이 유사 사고를 예방합니다. Etsy는 "Debriefing Facilitation Guide"를 공개하여 blameless 문화를 체계화했습니다. PagerDuty는 "Full-Service Ownership" 모델로 서비스를 만든 팀이 운영까지 책임지며, MTTA(Mean Time to Acknowledge)를 5분 이내로 유지합니다.

**Step 5 — 트레이드오프 & 대안**

| 측면 | 옵션 A | 옵션 B |
|------|--------|--------|
| On-call 모델 | 전담 SRE 팀 | Full-Service Ownership (개발팀=운영팀) |
| | 전문성 높음, 서비스 이해 낮음 | 서비스 이해 높음, 부담 분산 |
| Postmortem | 모든 인시던트 | SEV1/SEV2만 |
| | 완전한 학습, 시간 소모 | 효율적, 학습 기회 손실 |
| 알림 도구 | PagerDuty | OpsGenie | Grafana OnCall |
| | 성숙도 최고, 비쌈 | 가성비 좋음 | OSS, Grafana 통합 |

**Step 6 — 성장 & 심화**

- **Chaos Engineering + Incident 연계**: GameDay(계획된 장애 훈련)로 인시던트 대응 근육 기르기. 실제 장애 전에 대응 절차 검증.
- **AI-assisted Incident Response**: LLM이 과거 postmortem 검색, 유사 인시던트 패턴 매칭, 자동 runbook 제안.
- **Incident Metrics**: MTTA, MTTD(Detect), MTTR(Resolve), 재발률, action item 완료율 — 이 메트릭의 트렌드가 SRE 성숙도 지표.

**면접관 평가 기준:**

| 수준 | 기대 답변 |
|------|-----------|
| ✅ **L6 PASS** | IC 역할 설명, severity 분류, blameless postmortem 원칙, "완화 먼저, 원인 분석 나중" |
| 🌟 **L7 EXCEED** | On-call 부담 관리(toil budget), error budget과 변경 동결 연계, postmortem action item 추적 프로세스, multi-team incident coordination, 인시던트 메트릭(MTTA/MTTD/MTTR) |
| 🚩 **RED FLAG** | "원인 먼저 찾고 고치자" (완화 우선 무시), 특정 개인 비난, postmortem을 안 쓰거나 형식적으로만, 모든 알림에 PAGE |

---

### Q29: 메트릭 시스템 설계 — cardinality, recording rules

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Observability & SRE

**Question:** "Prometheus 기반 메트릭 시스템을 대규모로 운영할 때, cardinality 폭발 문제를 어떻게 해결하고, recording rules와 관리형 서비스(Cortex/Thanos/Mimir)를 어떻게 활용하는지 설명하세요. 각 언어(Python/Go/Kotlin)에서의 메트릭 계측 모범 사례도 포함해주세요."

---

**12살 비유:**

도서관에서 책을 분류하는 걸 상상해봐. 카테고리가 "소설/과학/역사"면 3개 칸만 있으면 돼(낮은 cardinality). 그런데 "작가별, 출판년도별, 페이지 수별"로 분류하면 칸이 수만 개 필요하지(cardinality 폭발). 메트릭 시스템도 라벨(분류 기준)이 너무 세밀하면 저장 공간과 조회 시간이 폭발해. Recording rules는 "매일 밤에 미리 통계를 계산해놓자"는 거야 — 매번 전체 책을 세는 대신 미리 정리해놓은 보고서를 보는 것처럼.

**단계별 답변:**

**Step 1 — 맥락**

Prometheus는 pull 기반 시계열 데이터베이스로 CNCF 졸업 프로젝트입니다. 단일 Prometheus 인스턴스의 한계(수직 스케일링, 장기 보존 부재)를 극복하기 위해 Thanos, Cortex, Mimir(Grafana) 같은 분산 솔루션이 등장했습니다. 가장 흔한 운영 문제는 **cardinality 폭발** — 라벨 조합이 기하급수적으로 증가하여 메모리/스토리지를 소진하는 현상입니다.

**Step 2 — 핵심 기술**

**Cardinality 폭발:**

```
메트릭: http_requests_total{method, path, status, user_id}

라벨 조합:
  method: 5개 (GET, POST, PUT, DELETE, PATCH)
  path: 100개 엔드포인트
  status: 10개 (200, 201, 400, 401, 403, 404, 500, 502, 503, 504)
  user_id: 100만명 👈 고유 카디널리티!

총 시계열 = 5 × 100 × 10 × 1,000,000 = 50억 개 ← 💥 폭발

해결 원칙:
1. 고유 ID(user_id, request_id, trace_id)는 라벨에 절대 넣지 않음
2. 경로 정규화: /users/123 → /users/{id}
3. 라벨 값은 유한 집합만 (enum-like)
4. 카디널리티 = 모든 라벨 값의 곱 (cartesian product)
```

```python

from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_client import start_http_server

http_requests = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'path_template', 'status_class']  # status_class: 2xx, 4xx, 5xx
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'Request duration',
    ['method', 'path_template'],
    buckets=[0.01, 0.05, 0.1, 0.3, 0.5, 1.0, 2.0, 5.0, 10.0]
)


def normalize_path(path: str) -> str:
    """
    /users/123/orders/456 → /users/{id}/orders/{id}
    FastAPI에서는 request.scope["route"].path로 template 획득
    """
    import re
    return re.sub(r'/\d+', '/{id}', path)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    path_template = request.scope.get("route", None)
    path = path_template.path if path_template else normalize_path(request.url.path)

    with request_duration.labels(
        method=request.method,
        path_template=path,
    ).time():
        response = await call_next(request)

    status_class = f"{response.status_code // 100}xx"
    http_requests.labels(
        method=request.method,
        path_template=path,
        status_class=status_class,
    ).inc()
    return response
```

```go
// Go — prometheus/client_golang
import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
    httpRequests = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Namespace: "myapp",
            Name:      "http_requests_total",
            Help:      "Total HTTP requests",
        },
        []string{"method", "path_template", "status_class"},
    )

    requestDuration = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Namespace: "myapp",
            Name:      "http_request_duration_seconds",
            Help:      "HTTP request duration",
            Buckets:   []float64{0.01, 0.05, 0.1, 0.3, 0.5, 1.0, 2.0, 5.0},
        },
        []string{"method", "path_template"},
    )

    // Cardinality 제한: CurryWith로 라벨 값 사전 등록
    // 또는 ConstLabels로 고정 라벨
)

// chi/mux에서 route pattern 추출
func metricsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        rw := &responseWriter{ResponseWriter: w, statusCode: 200}
        next.ServeHTTP(rw, r)

        // chi: chi.RouteContext(r.Context()).RoutePattern()
        pattern := chi.RouteContext(r.Context()).RoutePattern()

        httpRequests.WithLabelValues(
            r.Method,
            pattern,
            fmt.Sprintf("%dxx", rw.statusCode/100),
        ).Inc()

        requestDuration.WithLabelValues(
            r.Method,
            pattern,
        ).Observe(time.Since(start).Seconds())
    })
}
```

```kotlin
// Kotlin — Micrometer (Spring Boot 표준)
@Configuration
class MetricsConfig(private val registry: MeterRegistry) {
    // Micrometer는 자동으로 uri 라벨을 template화
    // GET /users/123 → uri="/users/{id}"

    // 카디널리티 제한: MeterFilter
    @Bean
    fun cardinalityLimiter(): MeterFilter = MeterFilter.maximumAllowableMetrics(10000)

    // 커스텀 메트릭
    fun recordBusinessMetric(orderType: String, amount: Double) {
        registry.counter("orders_total", "type", orderType).increment()
        registry.timer("order_processing_time", "type", orderType)
            .record(Duration.ofMillis(processingTime))
    }
}

// application.yml
// management:
//   metrics:
//     distribution:
//       slo:
//         http.server.requests: 100ms,300ms,500ms,1s,5s
//       percentiles:
//         http.server.requests: 0.5,0.95,0.99
//     tags:
//       application: my-service
//       environment: production
```

**Recording Rules:**

```yaml
groups:
  - name: sli_recording
    interval: 30s
    rules:
      # 5분 평균 요청 성공률 (SLI)
      - record: sli:http_requests:success_rate:5m
        expr: |
          sum(rate(http_requests_total{status_class!="5xx"}[5m]))
          /
          sum(rate(http_requests_total[5m]))

      # 1시간 평균 (burn rate alert용)
      - record: sli:http_requests:success_rate:1h
        expr: |
          sum(rate(http_requests_total{status_class!="5xx"}[1h]))
          /
          sum(rate(http_requests_total[1h]))

      # 서비스별 p99 지연 (대시보드용)
      - record: service:http_request_duration:p99:5m
        expr: |
          histogram_quantile(0.99,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)
          )

  - name: capacity_planning
    interval: 5m
    rules:
      # 시간당 요청 수 (용량 계획용)
      - record: service:http_requests:rate1h
        expr: sum(rate(http_requests_total[1h])) by (service)

```

**스케일링 — Prometheus 한계와 해결:**

```
단일 Prometheus 한계:
- 활성 시계열: ~1000만 개 (메모리 16-32GB)
- 장기 보존: 로컬 디스크 (15일 기본)
- HA: 단일 장애 지점

┌─────────────────────────────────────────────────────┐
│                  Scaling Solutions                    │
├──────────┬──────────────────────────────────────────┤
│ Thanos   │ Sidecar 패턴, S3 장기 저장, 글로벌 뷰    │
│          │ 기존 Prometheus에 sidecar 추가만으로 확장 │
│          │                                          │
│ Mimir    │ Grafana, 수평 확장, 멀티테넌시            │
│ (Cortex) │ Write path: distributor → ingester        │
│          │ Read path: query-frontend → querier       │
│          │ S3/GCS 장기 저장                          │
│          │                                          │
│ 관리형   │ Grafana Cloud, Amazon Managed Prometheus  │
│          │ Datadog, New Relic                        │
│          │ 운영 부담 제거, 비용 높음                  │
└──────────┴──────────────────────────────────────────┘

Thanos 아키텍처:
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Prom + S │  │ Prom + S │  │ Prom + S │  (S = Thanos Sidecar)
└─────┬────┘  └─────┬────┘  └─────┬────┘
      │             │             │
      └──────┬──────┘──────┬──────┘
             │             │
      ┌──────▼──────┐ ┌───▼────┐
      │ Thanos Query│ │ S3/GCS │ (장기 저장)
      └──────┬──────┘ └───┬────┘
             │             │
      ┌──────▼─────────────▼──┐
      │    Thanos Compactor    │ (다운샘플링: 5m → 1h → raw)
      └────────────────────────┘
```

**Step 3 — 다양한 관점**

- **개발자 관점**: "어떤 메트릭을 노출해야 하는가?" → RED 방법(Rate, Errors, Duration)을 서비스에, USE 방법(Utilization, Saturation, Errors)을 인프라에 적용.
- **플랫폼 팀 관점**: Cardinality 가드레일 — CI에서 메트릭 정의 검증, 라벨 화이트리스트, 런타임 카디널리티 모니터링 알림.
- **비용 관점**: Datadog은 커스텀 메트릭당 과금, 카디널리티가 직접 비용. 오픈소스(Mimir+Grafana)는 인프라 비용만.

**Step 4 — 구체적 예시**

GitLab은 Prometheus 하나로 시작했다가 시계열 3000만 개 돌파 후 Thanos로 전환했습니다. Grafana Labs는 자체 Mimir를 사용하여 초당 100만 샘플 인제스트, 10억 활성 시계열을 처리합니다. Uber는 M3를 자체 개발하여 초당 5억 메트릭 데이터포인트를 처리하며, 집계와 다운샘플링으로 장기 보존 비용을 90% 절감했습니다.

**Step 5 — 트레이드오프 & 대안**

| 솔루션 | 운영 복잡도 | 비용 | 확장성 | 적합 규모 |
|--------|------------|------|--------|-----------|
| 단일 Prometheus | 낮음 | 낮음 | 수직만 | <1000만 시계열 |
| Thanos | 중간 | 중간 (S3) | 수평 | ~1억 시계열 |
| Mimir/Cortex | 높음 | 중간 | 수평, 멀티테넌트 | ~10억 시계열 |
| Grafana Cloud | 낮음 | 높음 | 무제한 | 모든 규모 |
| Datadog | 낮음 | 매우 높음 | 무제한 | 예산 있을 때 |

**Step 6 — 성장 & 심화**

- **Exemplars**: 메트릭 데이터 포인트에 trace ID를 연결 → 메트릭에서 트레이스로 드릴다운. `histogram.observe(0.5, exemplar={"trace_id": "abc123"})`
- **Native Histograms**: Prometheus 2.40+에서 실험적 지원. 버킷을 자동 결정하여 카디널리티 감소하면서 정밀도 유지.
- **PromQL 고급**: `label_replace()`, `group_left/right` 조인, `predict_linear()`로 용량 예측.

**면접관 평가 기준:**

| 수준 | 기대 답변 |
|------|-----------|
| ✅ **L6 PASS** | Cardinality 개념과 폭발 원인(고유 ID 라벨), recording rules 활용, RED/USE 메서드 |
| 🌟 **L7 EXCEED** | Thanos/Mimir 아키텍처 상세(sidecar vs remote write), 다운샘플링 전략, exemplar 활용, 카디널리티 가드레일 CI 파이프라인, 언어별 경로 정규화 차이 |
| 🚩 **RED FLAG** | user_id를 라벨에 넣겠다, recording rules 모르고 매번 raw 쿼리, Prometheus 하나로 1억 시계열 처리 가능하다고 답변 |

---

### Q30: Chaos Engineering — fault injection

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Observability & SRE

**Question:** "프로덕션 환경에서 Chaos Engineering을 어떻게 안전하게 실행하시겠습니까? steady state hypothesis, blast radius 제어, fault injection 유형, 그리고 조직적 성숙도에 따른 점진적 도입 전략을 설명하세요."

---

**12살 비유:**

소방 훈련을 상상해봐. 진짜 불이 나기 전에 "만약 불이 나면 어떻게 될까?"를 미리 테스트하는 거야. 하지만 진짜 학교에 불을 지르면 안 되잖아(blast radius 제어). 그래서 한 교실에서만, 방과 후에만, 소방관이 대기한 상태에서 연기만 피우는 거야. Steady state는 "평소에 학생들이 5분 내에 대피한다"는 기준이야. 훈련 후 대피가 10분 걸렸다면, 비상구 표시가 부족하다는 걸 발견한 거지. Chaos Engineering은 시스템에 이런 소방 훈련을 하는 거야 — 일부러 서버를 죽이거나, 네트워크를 느리게 만들어서 시스템이 잘 대처하는지 확인하는 거야.

**단계별 답변:**

**Step 1 — 맥락**

Netflix가 Chaos Monkey를 만든 이유: "장애는 불가피하다. 그렇다면 의도적으로 장애를 일으켜 시스템의 약점을 사전에 발견하자." Chaos Engineering은 분산 시스템의 신뢰성을 **실험**으로 검증하는 학문입니다. 핵심 원칙은 Principles of Chaos Engineering(principlesofchaos.org)에서 정의됩니다.

**Step 2 — 핵심 기술**

**Chaos Engineering 프로세스:**

```
Step 1: Steady State Hypothesis (정상 상태 가설)
  "시스템이 정상일 때 관측 가능한 행동을 정의"
  예: "p99 지연 < 300ms AND 에러율 < 0.1% AND 주문 처리량 > 1000 req/s"

Step 2: Hypothesis Formation (실험 가설)
  "데이터베이스 replica 하나가 죽어도 정상 상태가 유지된다"

Step 3: Design Experiment (실험 설계)
  - 변수: DB replica 1개 종료
  - 측정: p99 지연, 에러율, 처리량
  - Blast radius: 특정 AZ의 replica 1개만
  - 롤백 계획: 자동 재시작, 수동 개입 기준
  - 시간: 업무 시간 (14:00-15:00), 트래픽 피크가 아닌 시간

Step 4: Run Experiment (실험 실행)
  - 모니터링 대시보드 실시간 관찰
  - abort 조건 자동화 (SLO 위반 시 즉시 중단)

Step 5: Analyze & Learn (분석 & 학습)
  - 가설이 맞았다면: 신뢰도 증가, 다음 실험으로
  - 가설이 틀렸다면: 약점 발견! → 수정 → 재실험
```

**Fault Injection 유형:**

```
┌─────────────────────────────────────────────────────┐
│               Fault Injection Types                  │
├──────────────┬──────────────────────────────────────┤
│ 인프라 레벨  │                                      │
│  - VM/Pod 종료   │ 인스턴스 장애 복구력 검증        │
│  - AZ 장애       │ 다중 AZ 장애 전이 검증           │
│  - 디스크 채우기  │ 스토리지 고갈 대응 검증          │
│  - CPU/메모리 압박│ 리소스 부족 시 graceful 저하     │
├──────────────┼──────────────────────────────────────┤
│ 네트워크 레벨│                                      │
│  - 지연 주입     │ 느린 의존 서비스 시뮬레이션      │
│  - 패킷 로스     │ 불안정 네트워크 대응              │
│  - DNS 장애      │ 서비스 디스커버리 복구력          │
│  - 파티션        │ 네트워크 분할 시 일관성           │
├──────────────┼──────────────────────────────────────┤
│ 애플리케이션 │                                      │
│  - 예외 주입     │ 에러 핸들링 경로 검증             │
│  - 응답 지연     │ 타임아웃/서킷 브레이커 동작       │
│  - 의존성 장애   │ 폴백 로직 검증                   │
│  - 데이터 오염   │ 입력 검증 로직 검증               │
└──────────────┴──────────────────────────────────────┘
```

**도구별 구현:**

```python

experiment = {
    "title": "DB Replica 장애 시 서비스 가용성 유지",
    "description": "DB replica 1개를 종료해도 p99 < 300ms 유지",
    "steady-state-hypothesis": {
        "title": "서비스 정상 상태",
        "probes": [
            {
                "type": "probe",
                "name": "p99-latency-under-300ms",
                "provider": {
                    "type": "http",
                    "url": "http://prometheus:9090/api/v1/query",
                    "arguments": {
                        "query": 'histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) < 0.3'
                    }
                },
                "tolerance": True
            },
            {
                "type": "probe",
                "name": "error-rate-under-0.1-percent",
                "provider": {
                    "type": "http",
                    "url": "http://prometheus:9090/api/v1/query",
                    "arguments": {
                        "query": 'rate(http_requests_total{status_class="5xx"}[5m]) / rate(http_requests_total[5m]) < 0.001'
                    }
                },
                "tolerance": True
            }
        ]
    },
    "method": [
        {
            "type": "action",
            "name": "terminate-db-replica",
            "provider": {
                "type": "python",
                "module": "chaosk8s.pod.actions",
                "func": "terminate_pods",
                "arguments": {
                    "label_selector": "app=postgres,role=replica",
                    "qty": 1
                }
            }
        }
    ],
    "rollbacks": [
        {
            "type": "action",
            "name": "ensure-replica-restarted",
            "provider": {
                "type": "python",
                "module": "chaosk8s.pod.probes",
                "func": "pods_in_phase",
                "arguments": {
                    "label_selector": "app=postgres,role=replica",
                    "phase": "Running"
                }
            }
        }
    ]
}

```

```go
// Go — Toxiproxy로 네트워크 장애 시뮬레이션
import (
    "github.com/Shopify/toxiproxy/v2/client"
)

func setupChaosProxy() {
    toxiClient := toxiproxy.NewClient("localhost:8474")

    // 프록시 생성: 앱 → DB 사이
    proxy, _ := toxiClient.CreateProxy("postgres", "localhost:15432", "postgres:5432")

    // 지연 주입: 100ms 추가 지연, 30% 확률
    proxy.AddToxic("latency", "latency", "downstream", 1.0, toxiproxy.Attributes{
        "latency": 100,
        "jitter":  50,
    })

    // 커넥션 끊김: 10초마다 커넥션 리셋
    proxy.AddToxic("reset_peer", "reset_peer", "downstream", 1.0, toxiproxy.Attributes{
        "timeout": 10000,
    })

    // 대역폭 제한: 1KB/s
    proxy.AddToxic("bandwidth", "bandwidth", "downstream", 1.0, toxiproxy.Attributes{
        "rate": 1,
    })
}

// 테스트에서 활용:
func TestOrderCreationWithDBLatency(t *testing.T) {
    // 1. steady state 확인
    assertP99Under300ms(t)

    // 2. fault injection
    addLatencyToxic(100) // 100ms 추가

    // 3. steady state 재확인
    assertP99Under300ms(t) // 서킷 브레이커/타임아웃이 정상 동작하는지

    // 4. 정리
    removeAllToxics()
}
```

```kotlin
// Kotlin — Spring Boot + Chaos Monkey for Spring Boot
// implementation("de.codecentric:chaos-monkey-spring-boot:3.1.0")

// application.yml
// chaos:
//   monkey:
//     enabled: true
//     assaults:
//       level: 5                    # 5번 중 1번 공격
//       latencyActive: true
//       latencyRangeStart: 1000     # 1-3초 지연
//       latencyRangeEnd: 3000
//       exceptionsActive: true
//       killApplicationActive: false  # 프로세스 종료는 비활성
//     watcher:
//       controller: true
//       restController: true
//       service: true
//       repository: true

// 런타임 제어 (Actuator 엔드포인트)
// POST /actuator/chaosmonkey/assaults
// {"latencyActive": true, "latencyRangeStart": 2000}

// 프로그래밍 방식으로 fault injection:
@Component
class OrderServiceChaos(
    @Value("\${chaos.enabled:false}") private val enabled: Boolean
) {
    fun <T> withChaos(block: () -> T): T {
        if (enabled && Random.nextInt(10) < 2) { // 20% 확률
            delay(Duration.ofMillis(Random.nextLong(500, 3000))) // 지연 주입
        }
        return block()
    }
}
```

**Blast Radius 제어:**

```
점진적 확장 전략 (Maturity Model):

Level 1: 개발 환경 (Development)
  - 단위 테스트에서 fault injection
  - Toxiproxy로 의존성 장애 시뮬레이션
  - 위험도: 매우 낮음

Level 2: 스테이징 환경 (Staging)
  - 프로덕션 미러 환경에서 실험
  - Chaos Toolkit으로 자동화된 실험
  - 위험도: 낮음

Level 3: 프로덕션 — 카나리 (Canary Chaos)
  - 프로덕션 트래픽의 1-5%만 영향
  - 특정 Pod/AZ에만 fault injection
  - 자동 abort 조건 설정
  - 위험도: 중간

Level 4: 프로덕션 — GameDay
  - 계획된 날짜에 팀 전체가 참여
  - AZ 장애, 대규모 의존성 장애 시뮬레이션
  - IC 역할 연습 포함
  - 위험도: 중-상

Level 5: 프로덕션 — 연속 Chaos (Continuous)
  - Netflix Chaos Monkey: 상시 랜덤 Pod 종료
  - 자동화된 실험 파이프라인
  - 위험도: 상 (성숙한 조직만)

Safety Controls:
  ├─ Kill Switch: 실험 즉시 중단 버튼
  ├─ Auto-abort: SLO 위반 감지 시 자동 중단
  ├─ Blast radius: 영향 범위를 명시적으로 제한
  ├─ 시간 제한: 실험 지속 시간 상한 설정
  └─ 롤백: 자동 복구 메커니즘 사전 검증
```

**Step 3 — 다양한 관점**

- **엔지니어 관점**: Chaos Engineering은 "모니터링이 정상 동작하는지"도 검증. 장애를 주입했는데 알림이 안 오면 관측성 갭 발견.
- **관리자 관점**: GameDay는 팀 빌딩 + 인시던트 대응 훈련의 기회. 실제 장애 시 당황하지 않는 문화 구축.
- **비즈니스 관점**: "프로덕션에서 일부러 장애를 일으킨다고?" → 비유: "내진 설계를 검증하려면 진동 테스트를 해야 한다. 지진이 오기 전에."

**Step 4 — 구체적 예시**

Netflix의 Chaos Monkey는 프로덕션에서 상시 가동되며 매일 랜덤 인스턴스를 종료합니다. 이를 통해 Netflix 엔지니어들은 "모든 서비스가 인스턴스 장애에 자동 복구되어야 한다"는 원칙을 내재화했습니다. Gremlin(상용 도구)은 GameDay 플랫폼을 제공하여 대규모 Chaos 실험을 안전하게 관리합니다. AWS는 Fault Injection Simulator(FIS)를 제공하여 EC2, ECS, RDS, VPC 수준의 장애를 안전하게 주입할 수 있습니다.

**Step 5 — 트레이드오프 & 대안**

| 도구 | 유형 | 장점 | 단점 |
|------|------|------|------|
| Chaos Toolkit | OSS, 선언적 | 다양한 프로바이더, CI 통합 | 학습 곡선 |
| Litmus Chaos | OSS, K8s 네이티브 | CRD 기반, GitOps 호환 | K8s 전용 |
| Gremlin | 상용 | UI 우수, 안전 장치 내장 | 비용 |
| AWS FIS | 관리형 | AWS 서비스 직접 장애 | AWS 전용 |
| Toxiproxy | OSS, 네트워크 | 간단, 테스트 통합 | 네트워크만 |
| Chaos Monkey | OSS, 인스턴스 | 상시 가동, 문화 구축 | 인스턴스 종료만 |

**Step 6 — 성장 & 심화**

- **Chaos + CI/CD**: PR 머지 시 자동으로 스테이징에서 Chaos 실험 실행. 서킷 브레이커/타임아웃 설정 변경 시 자동 검증.
- **Observability Chaos**: "메트릭 수집기를 죽이면 알림이 발동하는가?", "로그 파이프라인이 죽으면 감지할 수 있는가?" → 관측성 시스템 자체의 복원력 검증.
- **Multi-region Chaos**: 리전 간 장애 전이(cascading failure) 시뮬레이션. 가장 가치 높지만 가장 위험한 실험.

**면접관 평가 기준:**

| 수준 | 기대 답변 |
|------|-----------|
| ✅ **L6 PASS** | Steady state hypothesis 개념, blast radius 제어, 기본 fault injection 유형(Pod 종료, 네트워크 지연), abort 조건 |
| 🌟 **L7 EXCEED** | Maturity model에 따른 점진적 도입 전략, GameDay 운영 경험/설계, Chaos 결과를 SLO/error budget과 연계, 관측성 시스템 자체의 Chaos 검증, CI/CD 파이프라인 통합 |
| 🚩 **RED FLAG** | "프로덕션에서는 위험하니 스테이징에서만" (프로덕션 검증이 핵심), blast radius 제어 없이 실험, steady state 정의 없이 fault injection만 강조 |

---


> 대상: FAANG L6/L7 (Staff/Principal Engineer)
> 총 문항: 9개 (Q31~Q39) | 난이도: ⭐⭐⭐⭐⭐
> Category 6: Technical Leadership (Q31~Q35)
> Category 7: Security Across Stacks (Q36~Q39)

## 목차

### Category 6: Technical Leadership
1. [기술 부채 관리](#q31-기술-부채-관리--정량화-우선순위-경영진-설득) — Q31
2. [크로스팀 영향력](#q32-크로스팀-영향력--alignment-without-authority) — Q32
3. [멘토링과 팀 성장](#q33-멘토링과-팀-성장) — Q33
4. [아키텍처 의사결정](#q34-아키텍처-의사결정--adr과-trade-off-분석) — Q34
5. [Staff+ IC vs EM 경계](#q35-staff-ic-vs-em-경계--기술적-방향-설정과-조직-레버리지) — Q35

### Category 7: Security Across Stacks
6. [인증 패턴 비교](#q36-인증-패턴-비교--jwt-vs-session-oauth2-pkce) — Q36
7. [Supply Chain Security](#q37-supply-chain-security--dependency-scanning과-sbom) — Q37
8. [Secret Management](#q38-secret-management--vault-aws-sm-rotation) — Q38
9. [API Security](#q39-api-security--rate-limiting-cors-csp) — Q39

---

## Category 6: Technical Leadership

### Q31: 기술 부채 관리 — 정량화, 우선순위, 경영진 설득

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Technical Leadership

**Question:**
대규모 서비스에서 누적된 기술 부채를 어떻게 정량화하고 우선순위를 매기는가? 비기술적 이해관계자(VP, PM)를 어떻게 설득하여 기술 부채 상환에 엔지니어링 시간을 할당받았는가? 점진적 상환 전략과 그 결과를 구체적으로 설명하라.

---

**🧒 12살 비유:**
방을 청소하지 않고 계속 물건을 쌓으면 처음에는 괜찮지만, 어느 순간 원하는 물건을 찾으려면 30분이 걸리고 새 물건을 놓을 자리도 없게 된다. 기술 부채는 이 "어질러진 방"과 같다. 부모님(경영진)한테 "오늘 하루는 청소만 할게요"라고 하면 "숙제는?"이라고 묻는다. 그래서 "매일 10분씩 구역별로 정리하면, 다음 주부터 숙제 시간이 30분 단축됩니다"라고 숫자로 보여줘야 한다. 핵심은 "청소가 필요하다"가 아니라 "청소하면 속도가 빨라진다"를 증명하는 것이다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

Staff+ 엔지니어의 핵심 역량 중 하나는 기술적 판단을 비즈니스 언어로 번역하는 능력이다. 면접관은 (1) 기술 부채를 감정이 아닌 데이터로 표현하는 능력, (2) 우선순위 프레임워크의 체계성, (3) 비기술 이해관계자와의 협상 경험, (4) 점진적 접근의 전략성을 평가한다. "코드가 더럽다"는 DISAGREE, "이 모듈의 변경 비용이 평균 3배이며 분기 목표 달성을 위협한다"가 AGREE다.

**Step 2 — 핵심 설명: 기술 부채 정량화 프레임워크**

**정량화 축:**

| 메트릭 | 측정 방법 | 비즈니스 의미 |
|--------|-----------|---------------|
| **Change Failure Rate** | 해당 모듈 배포 후 롤백/핫픽스 비율 | 안정성 리스크 |
| **Lead Time for Changes** | 해당 영역 PR 머지까지 평균 시간 | 개발 속도 저하 |
| **Cognitive Complexity** | SonarQube/CodeClimate 지표 | 온보딩 비용, 버그 확률 |
| **Dependency Staleness** | 의존성 최신 버전 대비 지연 | 보안 취약점 노출 |
| **Incident Correlation** | 장애의 root cause가 해당 모듈인 비율 | 운영 비용 |

**우선순위 매트릭스 (Impact × Effort):**

```
        High Impact
            │
   Quick    │   Strategic
   Wins     │   Investment
  ──────────┼──────────────
   Fill     │   Deliberate
   Backlog  │   Deferral
            │
        Low Impact
   Low Effort ──→ High Effort
```

- **Quick Wins:** 2주 내 완료, 즉시 효과 — 먼저 실행하여 신뢰 구축
- **Strategic Investment:** 분기 단위 계획, 경영진 buy-in 필요
- **Fill Backlog:** 여유 시간에 처리
- **Deliberate Deferral:** 명시적으로 "지금은 안 한다" 기록

**Step 3 — 다양한 관점: 경영진 설득 전략**

경영진은 "기술 부채"라는 단어에 반응하지 않는다. 대신:

1. **비용 언어 사용:** "이 모듈 때문에 매 스프린트 2명의 엔지니어가 하루씩 워크어라운드를 만든다 → 분기당 60 engineer-days 손실"
2. **기회비용 프레임:** "이 리팩토링을 하면 Feature X 개발이 4주에서 2주로 단축된다"
3. **리스크 프레임:** "이 의존성은 EOL 상태이며, 보안 패치가 중단되었다. 6개월 내 마이그레이션하지 않으면 SOC2 감사에서 지적 가능"
4. **점진적 제안:** "20% 세금 모델 — 매 스프린트의 20%를 기술 부채에 할당하면, 6개월 후 전체 velocity가 30% 향상된다"

**Step 4 — 구체적 예시 (STAR)**

**Situation:** 3년간 운영된 결제 서비스의 모놀리식 트랜잭션 처리 모듈. 새 결제 수단 추가에 평균 6주, 연간 장애 12건 중 8건이 이 모듈 관련. 팀 5명, PM은 "새 기능 우선"을 강하게 밀고 있었다.

**Task:** 기술 부채 상환을 위한 엔지니어링 시간 확보와 점진적 리팩토링 실행.

**Action:**
1. **데이터 수집 (2주):** DORA 메트릭 대시보드를 구축. 해당 모듈의 Lead Time이 다른 모듈 대비 3.2배, Change Failure Rate 34% (다른 모듈 8%)임을 시각화.
2. **비즈니스 케이스 작성:** "Q4 목표인 3개 신규 결제 수단 추가는 현 구조에서 18주 예상. Strategy Pattern 도입 후 6주로 단축 가능. 초기 투자 4주."
3. **점진적 상환 설계:** Strangler Fig 패턴 — 새 결제 수단은 새 아키텍처로, 기존 수단은 점진 마이그레이션.
4. **20% 세금 협상:** VP에게 "다음 2 스프린트는 80% 기능, 20% 리팩토링. 3번째 스프린트부터 velocity 증가 보여드리겠다"고 약속하고 매주 메트릭 공유.

**Result:** 3개월 후 Lead Time 60% 감소, Change Failure Rate 34% → 11%. 새 결제 수단 추가가 평균 6주 → 2주로 단축. VP가 다음 분기부터 "Tech Health Budget"을 정식 항목으로 승인.

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 |
|--------|------|------|
| **Big-Bang 리팩토링** | 깔끔한 결과 | 높은 리스크, 기능 개발 중단 |
| **20% 세금** | 지속적, 낮은 리스크 | 대규모 변경 어려움 |
| **Strangler Fig** | 점진적 + 안전 | 과도기 복잡성 |
| **Boy Scout Rule** | 문화 정착 | 체계적 해결 어려움 |

최적 조합: Strangler Fig + 20% 세금 + Boy Scout Rule. 대규모 구조 변경은 Strangler Fig, 일상적 개선은 20% 세금, 개인 습관은 Boy Scout Rule.

**Step 6 — 성장 & 심화**

- Martin Fowler의 "Technical Debt Quadrant" (Reckless/Prudent × Deliberate/Inadvertent) 참고
- Google의 "Code Health" 팀 사례 — 자동화된 코드 건강 메트릭 + readability review
- "Accelerate" (Forsgren, Humble, Kim) — DORA 메트릭과 조직 성과의 상관관계 연구

**🎯 면접관 평가 기준:**
- ✅ **L6 PASS:** 기술 부채를 정량화하고 비즈니스 언어로 번역한 경험. 점진적 상환 전략 실행 경험.
- ✅ **L7 EXCEED:** 조직 수준의 기술 부채 관리 프로세스를 수립. 메트릭 기반 의사결정 문화 정착. VP/Director 레벨과의 협상 성공 사례.
- 🚩 **RED FLAG:** "코드가 더러워서 리팩토링해야 한다"만 반복. 데이터 없이 감정 호소. Big-Bang 리팩토링만 제안. 비기술 이해관계자와의 소통 경험 부재.

---

### Q32: 크로스팀 영향력 — Alignment Without Authority

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Technical Leadership

**Question:**
공식적인 관리 권한 없이 다른 팀의 기술적 의사결정에 영향을 미쳐야 했던 경험을 설명하라. RFC(Request for Comments) 프로세스를 어떻게 활용했는가? 반대 의견을 가진 시니어 엔지니어를 어떻게 설득했는가?

---

**🧒 12살 비유:**
학교에서 선생님이 아닌데 반 전체가 체육대회에서 같은 전략으로 뛰게 만들어야 한다고 상상해 보자. "내 말 들어!"라고 소리치면 아무도 안 듣는다. 대신 (1) 작전판에 왜 이 전략이 좋은지 그림으로 보여주고, (2) 가장 운동 잘하는 친구를 먼저 설득해서 동맹을 만들고, (3) 연습 경기에서 실제로 이기는 걸 보여주면, 자연스럽게 모두가 따라온다. 이게 "권한 없이 영향력을 미치는 것"이다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

Staff+ 엔지니어의 정의적 특성은 "팀 경계를 넘는 영향력"이다. IC로서 관리 권한이 없으므로, 기술적 설득력과 관계적 신뢰로 alignment를 만들어야 한다. 면접관은 (1) RFC 등 구조화된 의사결정 프로세스 경험, (2) 반대 의견에 대한 성숙한 대응, (3) 결과적으로 조직 전체가 더 나은 방향으로 이동한 사례를 찾는다.

**Step 2 — 핵심 설명: RFC 프로세스와 영향력의 구조**

**RFC 프로세스 구조:**

```
1. Problem Statement    ← 왜 이 변경이 필요한가 (데이터 기반)
2. Proposed Solution    ← 무엇을 제안하는가 (구체적 설계)
3. Alternatives         ← 어떤 대안을 검토했는가
4. Trade-off Analysis   ← 각 옵션의 장단점
5. Migration Plan       ← 어떻게 점진적으로 전환하는가
6. Open Questions       ← 피드백을 원하는 영역
7. Decision Record      ← 최종 결정과 근거
```

**영향력의 3계층:**

| 계층 | 메커니즘 | 예시 |
|------|----------|------|
| **Technical Credibility** | 코드, 프로토타입, 벤치마크 | "이 PoC에서 latency가 40% 개선됨" |
| **Relationship Capital** | 1:1, 비공식 대화, 신뢰 | 핵심 이해관계자와의 사전 논의 |
| **Process Leverage** | RFC, ADR, Tech Radar | 공식 의사결정 경로 활용 |

**Step 3 — 다양한 관점: 반대 의견 처리**

**Steel-Manning 기법:** 상대의 반대 의견을 상대보다 더 잘 설명한 후 반론한다.

```
❌ "그 방법은 틀렸습니다."
✅ "당신이 걱정하는 X는 완전히 타당합니다. 실제로 Y 사례에서 그 문제가 발생했습니다.
    제 제안에서는 Z 메커니즘으로 이를 해결하는데, 구체적으로..."
```

**Disagree and Commit:** 합의에 도달하지 못할 때는 의사결정권자를 명확히 하고, 결정이 내려지면 fully commit한다. Staff+ 엔지니어는 자기 의견이 채택되지 않아도 팀의 성공을 위해 움직인다.

**Step 4 — 구체적 예시 (STAR)**

**Situation:** 회사 내 5개 백엔드 팀이 각각 다른 API 인증 방식을 사용. Team A는 API Key, B는 JWT, C는 mTLS, D는 OAuth2, E는 커스텀 토큰. 신규 내부 서비스가 다른 팀 API를 호출할 때마다 인증 통합에 1~2주 소요. 나는 Platform 팀 소속 Staff Engineer로, 다른 팀에 대한 관리 권한 없음.

**Task:** 회사 전체의 내부 서비스 간 인증을 mTLS + JWT 이중 레이어로 표준화하는 것을 추진.

**Action:**
1. **데이터 수집:** 최근 6개월간 cross-team API 통합에 소비된 시간을 집계 → 총 47 engineer-weeks. 이를 비용으로 환산하여 RFC 서두에 배치.
2. **사전 Alliance 구축:** 각 팀의 Tech Lead와 1:1 커피챗. 그들의 pain point를 경청하고, 제안에 그들의 우려를 반영. 특히 Team C (mTLS 팀)의 시니어 엔지니어 K가 "JWT는 보안이 약하다"고 강하게 반대.
3. **K의 우려 Steel-Manning:** RFC에 "JWT 단독 사용의 보안 한계" 섹션을 추가하고, mTLS를 transport 레이어로, JWT를 application 레이어 인가용으로 결합하는 이중 레이어를 제안. K의 mTLS 전문성을 활용하여 구현 가이드 공동 작성 제안.
4. **PoC 제공:** 2주간 prototype 구현. 기존 방식 대비 통합 시간 1~2주 → 2시간으로 단축되는 데모 준비.
5. **RFC 리뷰 미팅:** 전체 리뷰에서 K가 공동 저자로 발표. 나머지 팀 buy-in 획득.

**Result:** 6개월 내 4/5 팀 마이그레이션 완료. cross-team 통합 시간 89% 감소. K가 가장 강력한 advocate로 전환. 이 RFC 프로세스가 회사 표준 기술 의사결정 프로세스로 채택됨.

**Step 5 — 트레이드오프 & 대안**

| 전략 | 효과 | 리스크 |
|------|------|--------|
| **Top-down Mandate** | 빠른 채택 | 반발, 표면적 준수 |
| **Bottom-up RFC** | 깊은 buy-in | 느린 속도, 합의 실패 가능 |
| **Working Code (PoC)** | 설득력 높음 | 시간 투자 큼 |
| **Standards Body** | 공식적 권위 | 관료적, 느림 |

Staff+ 최적: Bottom-up RFC + Working Code. PoC로 기술적 타당성 입증 + RFC로 조직적 합의.

**Step 6 — 성장 & 심화**

- Will Larson "Staff Engineer" — "영향력의 4가지 도구: 조언, 가드레일, 프로세스, 모델링"
- Google의 "Readability" 프로세스 — 코드 리뷰를 통한 표준 전파
- Netflix의 "Paved Road" — 표준을 강제하지 않고 가장 쉬운 경로로 만든다

**🎯 면접관 평가 기준:**
- ✅ **L6 PASS:** RFC를 작성하고 피드백을 반영한 경험. 다른 팀과 기술적 합의를 이끈 사례.
- ✅ **L7 EXCEED:** 조직 수준의 기술 의사결정 프로세스를 수립. 강한 반대 의견을 가진 시니어를 동맹으로 전환. 결과가 조직 표준으로 정착.
- 🚩 **RED FLAG:** "내가 옳으니까 따라야 한다" 태도. 반대 의견을 무시하거나 에스컬레이션으로만 해결. RFC/ADR 없이 구두 합의만 의존. 결과 측정 부재.

---

### Q33: 멘토링과 팀 성장

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Technical Leadership

**Question:**
주니어 엔지니어의 온보딩과 성장을 어떻게 체계적으로 지원했는가? 코드 리뷰 문화를 어떻게 정착시켰는가? 1:1 미팅에서 기술적 성장과 커리어 방향을 어떻게 코칭했는가? 구체적인 사례와 그 엔지니어의 성장 결과를 설명하라.

---

**🧒 12살 비유:**
수영을 배울 때, 좋은 코치는 "그냥 물에 뛰어들어"라고 하지 않는다. 먼저 얕은 곳에서 발차기를 가르치고, 킥보드를 주고, 옆에서 같이 수영하면서 자세를 고쳐주고, 점점 깊은 곳으로 나간다. 멘토링도 마찬가지다 — 처음에는 작은 버그 수정부터 시작해서, 점점 어려운 설계 문제를 맡기고, 옆에서 "여기서 이렇게 하면 어떨까?"라고 질문을 던져주는 것이다. 코드 리뷰는 "틀렸어"가 아니라 "여기서 이런 패턴을 쓰면 더 좋을 수 있는데, 왜 그런지 같이 보자"라고 하는 것이다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

Staff+ 엔지니어의 레버리지는 본인의 코드가 아니라 팀 전체의 역량 향상에서 나온다. 면접관은 (1) 체계적인 온보딩 프로그램 설계 경험, (2) 코드 리뷰를 "게이트키핑"이 아닌 "학습 기회"로 전환한 사례, (3) 1:1에서 기술+커리어 코칭을 병행한 경험, (4) 멘티의 실질적 성장 결과를 평가한다.

**Step 2 — 핵심 설명: 체계적 멘토링 프레임워크**

**온보딩 30-60-90 플랜:**

| 기간 | 목표 | 구체적 활동 |
|------|------|------------|
| **Day 1-30** | 환경 셋업 + 첫 PR | 페어 프로그래밍, 아키텍처 워크스루, "Good First Issue" 3개 |
| **Day 31-60** | 독립적 기능 구현 | 설계 리뷰 참여, on-call shadow, 코드 리뷰어 역할 시작 |
| **Day 61-90** | 소규모 프로젝트 리드 | 기술 문서 작성, 팀 발표, 독립 on-call |

**코드 리뷰 문화의 3원칙:**

1. **Ask, Don't Tell:** "이 부분을 X로 바꿔주세요" 대신 "이 함수가 두 가지 책임을 가지고 있는 것 같은데, 분리하면 테스트가 어떻게 변할까요?"
2. **Praise Publicly:** 좋은 코드에 구체적 칭찬. "이 에러 핸들링 패턴이 명확합니다. 팀 전체에 공유할 가치가 있어요."
3. **Nit vs Blocking:** 리뷰 코멘트를 `[nit]`, `[suggestion]`, `[blocking]`으로 명시. Blocking만 머지 차단.

**Step 3 — 다양한 관점: 1:1 구조**

**효과적인 1:1 프레임워크:**

```
매주 30분:
├── 5분: Check-in (기분, 블로커)
├── 10분: 기술 토픽 (최근 PR에서 배운 것, 읽은 논문/블로그)
├── 10분: 성장 토픽 (다음 레벨 요구사항 대비 현재 갭)
└── 5분: Action items (다음 주까지 시도할 것 1가지)
```

**Skill Matrix로 성장 시각화:**

```
                 Week 1    Week 12    Week 24
System Design      ■□□□□    ■■■□□      ■■■■□
Code Quality       ■■□□□    ■■■□□      ■■■■□
Debugging          ■□□□□    ■■□□□      ■■■■□
Communication      ■■□□□    ■■■□□      ■■■■■
Ownership          ■□□□□    ■■■□□      ■■■■□
```

**Step 4 — 구체적 예시 (STAR)**

**Situation:** 신입 엔지니어 J가 팀에 합류. CS 전공이지만 실무 경험 없음. 팀은 고트래픽 실시간 알림 서비스를 운영 중. 기존 팀 문화는 "코드 리뷰 = 시니어가 주니어 코드 검열"이라는 인식이 강했고, 주니어들이 PR 올리는 것을 두려워했다.

**Task:** J를 6개월 내 독립적으로 기능 개발 가능한 엔지니어로 성장시키고, 코드 리뷰 문화를 "학습 중심"으로 전환.

**Action:**
1. **30-60-90 플랜 수립:** J와 함께 구체적 마일스톤 설정. 첫 달은 매일 30분 페어 프로그래밍.
2. **코드 리뷰 가이드 작성:** 팀 전체에 "Code Review Guidelines" 문서 공유. `[nit]`/`[blocking]` 라벨 도입. 리뷰어 로테이션으로 시니어↔주니어 쌍방향 리뷰 문화 도입.
3. **점진적 난이도 조절:** Week 1~4: 버그 수정 → Week 5~8: 기존 API 확장 → Week 9~16: 신규 기능 설계부터 구현 → Week 17~24: 프로젝트 리드.
4. **1:1 기술 코칭:** 매주 "이번 주 가장 어려웠던 기술 결정은?"으로 시작. 답을 주지 않고 질문으로 사고를 유도. "만약 트래픽이 10배 늘면 이 설계가 어떻게 되나요?" 같은 확장 질문.
5. **실패 안전망:** "첫 프로젝트에서 실수하는 건 당연하다. 내가 safety net이다. 배포 전 내가 최종 리뷰한다"고 명시적으로 안심시킴.

**Result:** 6개월 후 J가 독립적으로 알림 배치 시스템을 설계·구현·배포. 코드 리뷰 turnaround가 평균 48시간 → 12시간으로 단축 (리뷰가 학습 기회가 되니 적극 참여). 주니어 PR 올리는 횟수 2배 증가. J가 1년 후 중급 엔지니어로 승진, 이후 자기 멘티를 갖게 됨. 코드 리뷰 가이드가 부서 전체 표준으로 채택.

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 |
|--------|------|------|
| **Sink or Swim** | 자기주도 학습 | 높은 이탈률, 느린 성장 |
| **Heavy Pairing** | 빠른 지식 전달 | 시니어 bandwidth 소진 |
| **Structured 30-60-90** | 균형, 측정 가능 | 설계·관리 비용 |
| **Self-Serve Docs Only** | 확장성 | 맥락 부족, 고립감 |

최적: Structured 30-60-90 + 점진적 Pairing 감소 (Week 1: 매일 → Week 4: 주 2회 → Week 8: 필요 시).

**Step 6 — 성장 & 심화**

- Google의 "Engineering Ladders" — 레벨별 기대 역량 명시로 코칭 방향 설정
- Lara Hogan "Resilient Management" — 1:1의 구조와 성장 대화 기법
- "An Elegant Puzzle" (Will Larson) — 시스템 사고로 팀 성장 설계
- Dreyfus Model of Skill Acquisition — 초보자→전문가 단계별 맞춤 교육

**🎯 면접관 평가 기준:**
- ✅ **L6 PASS:** 주니어 1~2명을 체계적으로 멘토링한 경험. 코드 리뷰 프로세스 개선 기여. 멘티의 구체적 성장 결과 제시.
- ✅ **L7 EXCEED:** 팀/조직 수준의 온보딩·멘토링 프로그램 설계. 코드 리뷰 문화를 근본적으로 변화. 멘티가 멘토가 되는 선순환 구축.
- 🚩 **RED FLAG:** "가르쳐 줬는데 못 따라왔다"식의 책임 전가. 코드 리뷰를 게이트키핑으로만 사용. 멘티의 성장 결과를 측정하지 않음. 1:1이 업무 상태 체크만 하는 미팅.

---

### Q34: 아키텍처 의사결정 — ADR과 Trade-off 분석

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Technical Leadership

**Question:**
중요한 아키텍처 의사결정을 어떻게 구조화하는가? ADR(Architecture Decision Record)을 어떻게 활용하는가? Reversible decision과 irreversible decision을 어떻게 구분하고, 각각에 다른 의사결정 프로세스를 적용하는가? 잘못된 아키텍처 결정을 뒤집어야 했던 경험이 있는가?

---

**🧒 12살 비유:**
레고로 거대한 성을 만든다고 생각해 보자. 레고 블록 색깔을 바꾸는 건 쉽다 — 빨간 블록을 빼고 파란 블록을 끼우면 된다 (Reversible). 하지만 성의 기초(바닥판 크기와 모양)를 바꾸려면 위에 쌓은 것을 다 허물어야 한다 (Irreversible). 그래서 블록 색깔은 빨리 정하고 "잘못되면 바꾸자"로 가지만, 바닥판 크기는 "정말 이게 맞는지" 설계도를 그리고, 친구들한테 의견을 물어보고, 충분히 고민한 후에 결정한다. ADR은 "왜 이 바닥판을 골랐는지" 적어두는 기록장이다 — 나중에 "왜 이렇게 했지?"라고 물을 때 답이 있도록.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

Staff+ 엔지니어의 핵심 산출물 중 하나가 "좋은 결정"이다. 면접관은 (1) 의사결정의 구조화 능력, (2) 결정의 가역성 판단 역량, (3) trade-off를 명시적으로 분석하는 습관, (4) 잘못된 결정을 인정하고 수정하는 성숙함을 평가한다. Jeff Bezos의 "Type 1 vs Type 2 decisions" 개념과 직결된다.

**Step 2 — 핵심 설명: ADR 구조와 의사결정 프레임워크**

**ADR (Architecture Decision Record) 구조:**

```markdown
- Status: PROPOSED | ACCEPTED | DEPRECATED | SUPERSEDED
- Date: YYYY-MM-DD
- Deciders: [의사결정 참여자]

## Context
왜 이 결정이 필요한가? 어떤 제약 조건이 있는가?

## Decision
무엇을 결정했는가?

## Alternatives Considered
| 옵션 | 장점 | 단점 | 비용 |
|------|------|------|------|

## Consequences
이 결정으로 인한 긍정적/부정적 결과.

## Compliance
이 결정의 준수 여부를 어떻게 검증하는가?
```

**Reversible vs Irreversible 의사결정 매트릭스:**

| 차원 | Reversible (Type 2) | Irreversible (Type 1) |
|------|---------------------|----------------------|
| **전환 비용** | 낮음 (일~주) | 높음 (월~분기) |
| **의사결정 속도** | 빠르게 (~70% 확신) | 신중하게(~90% 확신) |
| **참여자** | 개인/소규모 | 팀 전체 + 이해관계자 |
| **문서화** | 경량 (Slack 스레드, 코멘트) | ADR 필수 |
| **예시** | 라이브러리 선택, API 필드명 | DB 엔진 변경, 프로토콜 전환, 데이터 모델 |

**Trade-off 분석 도구:**

```
Quality Attribute Workshop (QAW):
┌─────────────────────────────────────┐
│  Stimulus → Response Measure        │
│                                     │
│  "1000 req/s 부하 시"              │
│  → "p99 latency < 200ms"           │
│  → 어떤 아키텍처가 이를 만족하는가? │
└─────────────────────────────────────┘

ATAM (Architecture Tradeoff Analysis Method):
1. 비즈니스 드라이버 식별
2. 아키텍처 접근법 제시
3. Quality Attribute Tree 작성
4. 시나리오별 분석
5. Sensitivity Points & Tradeoff Points 식별
6. 리스크 테마 도출
```

**Step 3 — 다양한 관점: 의사결정 안티패턴**

| 안티패턴 | 설명 | 대안 |
|----------|------|------|
| **Analysis Paralysis** | 완벽한 정보를 기다리다 결정 지연 | Time-box + "70% 확신이면 GO" |
| **HiPPO** | 가장 높은 직급의 의견이 곧 결정 | ADR 기반 데이터 중심 결정 |
| **Resume-Driven** | 이력서에 쓸 기술 선택 | 비즈니스 요구사항 기반 평가 |
| **Golden Hammer** | 익숙한 기술만 반복 사용 | 요구사항별 기술 적합성 평가 |
| **Invisible Decision** | 결정이 문서화되지 않음 | 모든 Type 1 결정은 ADR 작성 |

**Step 4 — 구체적 예시 (STAR)**

**Situation:** 실시간 이벤트 처리 시스템 설계. 팀 내 의견이 Kafka vs Pulsar vs AWS Kinesis로 갈림. 각 옵션에 강한 지지자가 있었고, 3주째 결론이 나지 않고 있었다. 이 결정은 데이터 파이프라인 전체에 영향을 미치는 Type 1 결정.

**Task:** 구조화된 의사결정 프로세스를 통해 합리적 결론 도출.

**Action:**
1. **Decision Framework 도입:** "이 결정은 Type 1이다. 메시지 브로커를 전환하는 비용은 3개월 이상이고 전체 파이프라인에 영향" → ADR 작성 및 ATAM 기반 분석 제안.
2. **Quality Attribute 정의:** 팀과 함께 핵심 품질 속성 우선순위 합의 — (1) 운영 복잡성, (2) 처리량, (3) 비용, (4) 생태계 성숙도, (5) 팀 역량.
3. **PoC Sprint:** 각 지지자에게 1주 time-box로 동일한 시나리오 구현 요청. 메트릭: throughput, latency, 운영 setup 시간, 모니터링 통합 난이도.
4. **ADR 작성:** PoC 결과 + 품질 속성별 점수를 표로 정리. Kafka가 처리량과 생태계에서 우세, Pulsar이 multi-tenancy에서 우세, Kinesis가 운영 복잡성에서 우세.
5. **의사결정:** 우선순위 1인 "운영 복잡성"에서 Kinesis가 가장 우수하지만, 팀이 AWS lock-in을 우려. 차선책인 Kafka를 선택하되 Managed Kafka(MSK) 사용으로 운영 부담 절충. Pulsar 지지자의 multi-tenancy 우려는 Kafka topic naming convention으로 해결.
6. **Decision Record 공유:** ADR에 "왜 Pulsar를 선택하지 않았는가"를 구체적으로 기록. 향후 조건 변경 시 재검토 트리거 조건 명시.

**Result:** 3주간의 교착 상태가 5일 만에 해소. ADR이 6개월 후 신규 팀원의 "왜 Kafka?"에 대한 완벽한 답변이 됨. 이 프레임워크가 이후 3건의 주요 기술 결정에 재활용. 1년 후 실제로 Pulsar 재검토 트리거 조건에 도달하여 ADR 업데이트 — "Type 1 결정도 조건부로 재검토 가능"한 문화 정착.

**Step 5 — 트레이드오프 & 대안**

**결정 속도 vs 결정 품질 스펙트럼:**

```
빠른 결정 ─────────────────────── 신중한 결정
   │                                    │
 Type 2                              Type 1
 "Two-way door"                    "One-way door"
 Reversible                        Irreversible
 70% 확신                          90% 확신
 개인/소규모 결정                   ADR + 팀 합의
 라이브러리, 코드 구조              DB, 프로토콜, 언어
```

Staff+의 판단: Type 1을 Type 2로 착각하면 재앙, Type 2를 Type 1로 착각하면 속도 저하. 정확한 분류가 핵심 역량.

**Step 6 — 성장 & 심화**

- Michael Nygard "Documenting Architecture Decisions" — ADR 원조 논문
- Jeff Bezos 2016 Letter — "Type 1 and Type 2 decisions"
- SEI ATAM — Architecture Tradeoff Analysis Method 공식 가이드
- ThoughtWorks Technology Radar — 조직 수준 기술 의사결정 프레임워크

**🎯 면접관 평가 기준:**
- ✅ **L6 PASS:** ADR을 작성하고 trade-off를 구조적으로 분석한 경험. Reversible/Irreversible 구분 이해.
- ✅ **L7 EXCEED:** 조직의 의사결정 프로세스 자체를 설계. 잘못된 결정을 데이터 기반으로 뒤집은 경험. 결정의 재검토 조건을 사전 정의하는 성숙함.
- 🚩 **RED FLAG:** 직감 기반 결정만 이야기. 문서화 경험 없음. 잘못된 결정을 인정하지 못함. "내가 항상 옳았다"식의 답변. Resume-Driven 기술 선택.

---

### Q35: Staff+ IC vs EM 경계 — 기술적 방향 설정과 조직 레버리지

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Technical Leadership

**Question:**
Staff+ IC(Individual Contributor)와 Engineering Manager의 역할 차이를 어떻게 이해하는가? Staff Engineer으로서 기술적 방향을 설정할 때, EM의 영역을 침범하지 않으면서 조직에 최대 레버리지를 발휘하려면 어떻게 해야 하는가? "기술적 의사결정"과 "사람 의사결정"의 경계를 어떻게 관리하는가?

---

**🧒 12살 비유:**
축구팀에서 감독(EM)과 주장(Staff IC)의 차이를 생각해 보자. 감독은 "누가 출전할지, 교체 시기, 선수들의 컨디션 관리"를 결정한다. 주장은 "필드 위에서 어떤 전술로 공격할지, 수비 라인을 어디에 세울지"를 결정한다. 좋은 주장은 감독의 결정을 존중하면서도, 필드 위에서 실시간으로 전술을 조율한다. 만약 주장이 "야, 너 교체돼. 내려가"라고 하면 권한 침범이고, 감독이 "패스는 항상 오른쪽으로만 해"라고 하면 기술적 마이크로매니징이다. 각자의 영역을 존중하면서 팀이 이기는 것이 목표다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

Staff+ IC 역할이 비교적 새롭고, 많은 회사에서 이 역할의 경계가 모호하다. 면접관은 (1) IC와 EM의 역할 차이에 대한 명확한 이해, (2) EM과의 건강한 파트너십 구축 경험, (3) 기술적 리더십의 레버리지를 극대화하는 방법론, (4) 경계 충돌 시의 성숙한 해결 능력을 평가한다.

**Step 2 — 핵심 설명: Staff IC vs EM 역할 매트릭스**

**영역 분리:**

| 차원 | Staff+ IC | EM |
|------|-----------|-----|
| **기술 방향** | 아키텍처, 기술 표준, 기술 로드맵 | 리소스 배분, 일정 관리 |
| **사람** | 기술적 멘토링, 코드 리뷰 | 채용, 평가, 승진, 1:1 |
| **프로세스** | 기술 프로세스 (RFC, ADR) | 팀 프로세스 (sprint, retro) |
| **대외** | Tech talk, 기술 블로그, 외부 신뢰 | 매니저 미팅, 예산, 상위 보고 |
| **의사결정** | "무엇을, 어떻게" (기술) | "누가, 언제" (사람+일정) |

**Staff+ IC의 4가지 아키타입 (Will Larson):**

```
┌─────────────────────────────────────────────────┐
│  Tech Lead     │  Architect     │  Solver       │
│  팀 내 기술    │  조직 전체     │  어려운 문제  │
│  리더십        │  기술 방향     │  전문 해결    │
├────────────────┴────────────────┴───────────────┤
│              Right Hand                         │
│              리더십 확장 (EM/VP의 기술적 분신)   │
└─────────────────────────────────────────────────┘
```

**레버리지 극대화 공식:**

```
Staff IC Leverage = (기술적 영향 범위) × (조직 승수)

기술적 영향 범위:
  - 코드 작성: 1x (본인만)
  - 설계 리뷰: 5x (팀)
  - 기술 표준: 20x (부서)
  - 플랫폼/도구: 100x (회사)

조직 승수:
  - EM과 파트너십: 2x
  - 경영진 신뢰: 3x
  - 문화 형성: 5x
```

**Step 3 — 다양한 관점: 경계 충돌 시나리오**

| 시나리오 | 잘못된 대응 | 올바른 대응 |
|----------|-------------|-------------|
| 특정 엔지니어가 기술적으로 부족 | IC가 직접 성과 피드백 | EM에게 관찰 공유, 기술 멘토링 제안 |
| 기술 방향에 EM이 간섭 | 충돌/에스컬레이션 | "왜"를 공유하고 데이터로 설득 |
| 팀 리소스 부족으로 기술 부채 방치 | IC가 단독으로 추가 인력 요청 | EM과 함께 비즈니스 케이스 작성 |
| 채용 과정에서 기술 판단 필요 | IC가 채용 최종 결정 | 기술 평가 제공, 최종 결정은 EM |

**Step 4 — 구체적 예시 (STAR)**

**Situation:** 결제 플랫폼 팀의 Staff Engineer. EM이 새로 부임. EM은 "분기 내 3개 신규 기능 출시"에 집중, 나는 "모놀리스 → MSA 전환이 6개월 내 필수"라고 판단. 기존 모놀리스의 배포 주기가 2주이고, 장애 시 전체 서비스 영향. 두 목표가 리소스 경쟁.

**Task:** EM과의 갈등 없이 기술 방향(MSA 전환)과 비즈니스 목표(신규 기능)를 모두 달성하는 전략 수립.

**Action:**
1. **EM과의 파트너십 구축:** 첫 1:1에서 "기술 방향은 내가, 사람·일정은 당신이. 우리의 공통 목표는 팀의 성공"이라고 명시적 합의.
2. **Strangler Fig 전략 제안:** "신규 기능 3개를 새 MSA로 구현 → 모놀리스에서 분리 → 기존 기능은 점진 마이그레이션." 이렇게 하면 신규 기능 출시(EM 목표)와 MSA 전환(IC 목표)이 동시 달성.
3. **기술 로드맵 + 비즈니스 로드맵 통합:** EM과 함께 분기 계획을 기술·비즈니스 두 축으로 작성. 기술 마일스톤이 비즈니스 마일스톤을 enable하는 구조로 설계.
4. **영역 존중:** 팀 구성(누가 MSA 작업을 하는지)은 EM이 결정. 기술 설계(서비스 경계, API 계약, 데이터 분리 전략)는 내가 RFC로 결정.
5. **정기 Sync:** 매주 30분 IC-EM sync. 기술 리스크를 공유하고, EM이 상위 보고에 활용할 수 있는 기술 진행 요약 제공.

**Result:** 분기 목표 3개 기능 중 2개를 새 MSA로 출시, 1개는 기존 모놀리스에서 출시 후 다음 분기 마이그레이션 예정. 배포 주기 2주 → 2일 (MSA 서비스). EM이 상위 보고에서 "기술 전환과 기능 출시를 동시에 달성한 좋은 사례"로 발표. 이후 다른 팀의 IC-EM 파트너십 모델로 참조됨.

**Step 5 — 트레이드오프 & 대안**

**IC가 빠지기 쉬운 함정:**

| 함정 | 증상 | 해결 |
|------|------|------|
| **Shadow Manager** | IC가 사람 관리까지 개입 | EM 영역 존중, 기술 멘토링에 집중 |
| **Ivory Tower** | 코드 안 짜고 설계만 함 | 주당 30~50%는 hands-on 코딩 유지 |
| **Lone Wolf** | 혼자 결정, 혼자 구현 | RFC, 설계 리뷰로 팀 참여 유도 |
| **Feature Factory** | 기능 구현에만 매몰 | 기술 로드맵 + 플랫폼 개선에 시간 할당 |

**IC의 시간 배분 가이드 (L6/L7):**

```
L6 (Staff):
  Coding: 40-50%
  Design/Review: 20-30%
  Mentoring: 10-15%
  Strategy/Communication: 10-15%

L7 (Principal):
  Coding: 20-30%
  Design/Review: 25-30%
  Strategy/Communication: 25-30%
  Mentoring/Culture: 15-20%
```

**Step 6 — 성장 & 심화**

- Will Larson "Staff Engineer" — Staff IC의 4가지 아키타입과 실전 사례
- Tanya Reilly "The Staff Engineer's Path" — IC 리더십의 기술과 조직적 측면
- Pat Kua "Talking with Tech Leads" — Tech Lead와 EM의 경계 관리
- Charity Majors — "The Engineer/Manager Pendulum" 블로그 시리즈

**🎯 면접관 평가 기준:**
- ✅ **L6 PASS:** IC와 EM의 역할 차이를 명확히 이해. EM과 건강한 파트너십 경험. 기술적 방향 설정 + hands-on 균형.
- ✅ **L7 EXCEED:** 조직 수준의 기술 전략을 수립하고 실행. EM과의 파트너십 모델을 다른 팀에 전파. 기술적 의사결정의 조직적 레버리지를 극대화한 경험.
- 🚩 **RED FLAG:** IC vs EM 경계를 모름. "EM이 시키는 대로 했다" 또는 "EM 역할까지 했다". 기술적 방향 없이 기능 구현만 나열. 조직적 영향력 사례 부재.

---

## Category 7: Security Across Stacks

### Q36: 인증 패턴 비교 — JWT vs Session, OAuth2, PKCE

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Security Across Stacks

**Question:**
JWT 기반 인증과 Session 기반 인증의 근본적인 trade-off를 설명하라. OAuth2의 Authorization Code Flow에서 PKCE가 왜 필요하게 되었는가? Python(FastAPI), Go(net/http), Kotlin(Spring Security)에서 각각의 인증 구현 방식은 어떻게 다른가? 프로덕션에서 JWT를 사용할 때 가장 흔히 저지르는 보안 실수는 무엇인가?

---

**🧒 12살 비유:**
놀이공원에 입장하는 두 가지 방법이 있다. (1) **손목 밴드(JWT):** 매표소에서 밴드를 받으면 놀이기구마다 보여주기만 하면 된다. 직원이 매표소에 "이 사람 진짜 입장했나요?" 확인 전화를 할 필요가 없다. 하지만 밴드를 빼앗기면 입장 취소가 어렵다 — 밴드 자체가 "유효"하니까. (2) **입장 번호(Session):** 매표소 컴퓨터에 "3번 입장"이라 기록하고 번호표를 받는다. 놀이기구마다 직원이 매표소에 "3번 진짜 입장?" 확인 전화를 해야 한다. 느리지만 "3번 취소"하면 즉시 효과가 있다. PKCE는 "누군가 밴드 발급 요청을 가로채서 대신 받는 것"을 막는 비밀 암호다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

인증은 모든 시스템의 기초이면서 가장 많은 보안 사고가 발생하는 영역이다. 면접관은 (1) JWT/Session의 근본적 차이를 stateless vs stateful로 이해하는지, (2) OAuth2 플로우의 보안 모델을 설명할 수 있는지, (3) 각 언어/프레임워크의 구현 차이를 실무 수준으로 아는지, (4) 프로덕션에서의 실수와 대응 경험을 평가한다.

**Step 2 — 핵심 설명: JWT vs Session 근본 Trade-off**

**핵심 차이: "신뢰의 위치"**

| 차원 | JWT (Stateless) | Session (Stateful) |
|------|-----------------|---------------------|
| **상태 저장** | 클라이언트 (토큰 자체) | 서버 (Redis, DB) |
| **검증 방식** | 서명 검증 (암호학) | 저장소 조회 (I/O) |
| **즉시 폐기** | 불가능 (만료까지 유효) | 가능 (세션 삭제) |
| **확장성** | 우수 (서버 무상태) | 세션 스토어 필요 |
| **페이로드** | Claims 포함 가능 | 별도 조회 필요 |
| **크기** | 크다 (수백 바이트~KB) | 작다 (세션 ID만) |

**JWT 즉시 폐기 해결책:**

```
1. Short-lived Access Token (15분) + Refresh Token (7일)
2. Token Blocklist (Redis) — 로그아웃 시 jti 등록
3. Token Versioning — User 테이블에 token_version, 변경 시 모든 기존 토큰 무효
```

**OAuth2 Authorization Code Flow + PKCE:**

```
┌──────────┐                    ┌──────────┐                   ┌──────────┐
│  Client  │                    │  AuthZ   │                   │ Resource │
│  (SPA)   │                    │  Server  │                   │  Server  │
└────┬─────┘                    └────┬─────┘                   └────┬─────┘
     │                               │                              │
     │ 1. Generate code_verifier     │                              │
     │    + code_challenge           │                              │
     │                               │                              │
     │ 2. /authorize?                │                              │
     │    code_challenge=X           │                              │
     │    code_challenge_method=S256 │                              │
     │──────────────────────────────►│                              │
     │                               │                              │
     │ 3. auth_code                  │                              │
     │◄──────────────────────────────│                              │
     │                               │                              │
     │ 4. /token                     │                              │
     │    code=auth_code             │                              │
     │    code_verifier=V            │                              │
     │──────────────────────────────►│                              │
     │                               │ 5. Verify:                   │
     │                               │    SHA256(V) == X?           │
     │ 6. access_token               │                              │
     │◄──────────────────────────────│                              │
     │                               │                              │
     │ 7. /api/resource              │                              │
     │    Authorization: Bearer AT   │                              │
     │─────────────────────────────────────────────────────────────►│
```

**PKCE가 필요한 이유:** SPA/모바일 앱은 `client_secret`을 안전하게 저장할 수 없다. Authorization Code를 가로채더라도 `code_verifier`가 없으면 토큰 교환 불가.

**Step 3 — 다양한 관점: 스택별 구현 비교**

**Python (FastAPI):**

```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401)
    return await get_user(user_id)

```

**Go (net/http + middleware):**

```go
// JWT 인증 — golang-jwt/jwt
func JWTMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        tokenStr := extractBearerToken(r)
        if tokenStr == "" {
            http.Error(w, "Unauthorized", http.StatusUnauthorized)
            return
        }
        token, err := jwt.Parse(tokenStr, func(t *jwt.Token) (interface{}, error) {
            if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
                return nil, fmt.Errorf("unexpected signing method: %v", t.Header["alg"])
            }
            return []byte(secretKey), nil
        })
        if err != nil || !token.Valid {
            http.Error(w, "Unauthorized", http.StatusUnauthorized)
            return
        }
        claims := token.Claims.(jwt.MapClaims)
        ctx := context.WithValue(r.Context(), "user_id", claims["sub"])
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
// 특징: 미들웨어 체이닝, context.Value로 claims 전달
// 장점: 명시적, 프레임워크 독립적, 제로 매직
// 주의: alg 검증 필수 (Algorithm Confusion 방지)
```

**Kotlin (Spring Security):**

```kotlin
// JWT 인증 — Spring Security + OAuth2 Resource Server
@Configuration
@EnableWebSecurity
class SecurityConfig {
    @Bean
    fun securityFilterChain(http: HttpSecurity): SecurityFilterChain {
        http
            .oauth2ResourceServer { it.jwt { jwtDecoder() } }
            .authorizeHttpRequests {
                it.requestMatchers("/public/**").permitAll()
                  .requestMatchers("/admin/**").hasRole("ADMIN")
                  .anyRequest().authenticated()
            }
        return http.build()
    }

    @Bean
    fun jwtDecoder(): JwtDecoder =
        NimbusJwtDecoder.withPublicKey(rsaPublicKey).build()
}
// 특징: 선언적 설정, Spring Security Filter Chain
// 장점: OAuth2/OIDC 풀스택 지원, 역할 기반 인가 내장
// 주의: 설정 복잡도 높음, 디버깅 시 FilterChain 이해 필수
```

**Step 4 — 구체적 예시: 프로덕션 JWT 보안 실수 Top 5**

| 순위 | 실수 | 영향 | 대응 |
|------|------|------|------|
| 1 | **alg: none 허용** | 서명 없이 토큰 조작 가능 | 허용 알고리즘 화이트리스트 필수 |
| 2 | **Secret을 코드에 하드코딩** | Git 유출 시 전체 토큰 위조 가능 | 환경변수/Vault + RS256 전환 |
| 3 | **만료 시간 너무 길게 설정** | 토큰 탈취 시 장기간 악용 | Access: 15분, Refresh: 7일 |
| 4 | **민감 정보를 Payload에 포함** | JWT는 인코딩이지 암호화가 아님 | PII/PHI 절대 포함 금지 |
| 5 | **Refresh Token 미사용** | Access Token 재발급 메커니즘 부재 | Refresh Token + Rotation |

**Step 5 — 트레이드오프 & 대안**

| 시나리오 | 권장 | 이유 |
|----------|------|------|
| **MSA + 수평 확장** | JWT | Stateless, 서비스 간 전파 용이 |
| **단일 서버 + 즉시 로그아웃 필수** | Session | 즉시 폐기 가능 |
| **SPA + 모바일** | OAuth2 + PKCE | Client secret 불필요 |
| **서버 간 통신** | mTLS + JWT | Transport + Application 이중 보안 |
| **높은 보안 요구 (금융)** | Session + Redis | 완전한 서버 제어 |

**Step 6 — 성장 & 심화**

- OWASP JWT Cheat Sheet — JWT 보안 best practices
- RFC 7636 — PKCE 공식 스펙
- Auth0 "JWT Handbook" — JWT의 모든 것
- "API Security in Action" (Neil Madden) — OAuth2/OIDC 실전

**🎯 면접관 평가 기준:**
- ✅ **L6 PASS:** JWT vs Session trade-off를 stateless/stateful 관점에서 설명. PKCE의 필요성 이해. 한 가지 스택에서의 구현 경험.
- ✅ **L7 EXCEED:** 3개 스택의 구현 차이를 비교. JWT 보안 실수와 프로덕션 대응 경험. OAuth2 전체 플로우(Authorization Code, Client Credentials, Device Code)에 대한 깊은 이해.
- 🚩 **RED FLAG:** JWT를 암호화로 착각. alg 검증의 중요성 모름. PKCE 없이 SPA에서 Implicit Flow 사용. "프레임워크가 알아서 한다"식의 답변.

---

### Q37: Supply Chain Security — Dependency Scanning과 SBOM

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Security Across Stacks

**Question:**
소프트웨어 공급망 보안(Supply Chain Security)이 왜 최근 몇 년간 중요해졌는가? SBOM(Software Bill of Materials)이란 무엇이고 왜 필요한가? Python, Go, Kotlin/JVM 생태계에서 의존성 보안 스캐닝은 어떻게 다른가? SolarWinds나 Log4Shell 사태에서 어떤 교훈을 얻었는가?

---

**🧒 12살 비유:**
피자를 만든다고 하자. 밀가루, 토마토소스, 치즈를 각각 다른 가게에서 사 온다. 만약 밀가루 공장에서 몰래 이상한 물질을 넣었다면? 피자 가게는 "우리는 좋은 재료만 쓴다"고 하지만 실제로 밀가루 안에 뭐가 들었는지 모른다. SBOM은 "이 피자에 들어간 모든 재료의 산지, 제조사, 유통기한 목록"이다. 재료 리콜이 나오면 즉시 "우리 피자에 그 재료가 들어갔는지" 확인할 수 있다. Log4Shell은 전 세계 피자에 들어간 특정 밀가루에서 문제가 발견된 것과 같다 — 근데 대부분의 피자 가게가 어떤 밀가루를 쓰는지 기록하지 않았다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

2020년 SolarWinds, 2021년 Log4Shell, 2024년 XZ Utils 사태 이후 공급망 보안은 더 이상 "nice-to-have"가 아니다. 미국 정부(Executive Order 14028)가 SBOM을 의무화했고, EU Cyber Resilience Act도 유사 요구사항을 포함한다. 면접관은 (1) 공급망 공격 벡터 이해, (2) SBOM의 목적과 구조, (3) 언어/생태계별 도구와 차이, (4) 실제 대응 경험을 평가한다.

**Step 2 — 핵심 설명: 공급망 보안 레이어**

**공급망 공격 벡터:**

```
┌─────────────────────────────────────────────┐
│            Your Application                  │
├─────────────────────────────────────────────┤
│  Direct Dependencies (requirements.txt 등)   │
├─────────────────────────────────────────────┤
│  Transitive Dependencies (A → B → C)        │  ← 가장 위험
├─────────────────────────────────────────────┤
│  Build Tools (compiler, bundler)             │
├─────────────────────────────────────────────┤
│  Base Images (Docker)                        │
├─────────────────────────────────────────────┤
│  CI/CD Pipeline                              │
└─────────────────────────────────────────────┘
```

| 공격 유형 | 예시 | 탐지 방법 |
|-----------|------|-----------|
| **Typosquatting** | `requests` → `requets` | Package name verification |
| **Dependency Confusion** | 내부 패키지명과 동일한 공개 패키지 등록 | Private registry 우선순위 설정 |
| **Compromised Maintainer** | event-stream (npm) | 코드 리뷰, 서명 검증 |
| **Build System Injection** | SolarWinds Orion | 빌드 재현성, SLSA |
| **Transitive Vulnerability** | Log4Shell (log4j-core) | 전이 의존성 스캔 |

**SBOM (Software Bill of Materials):**

```json
// CycloneDX 형식 (JSON)
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "components": [
    {
      "type": "library",
      "name": "fastapi",
      "version": "0.109.0",
      "purl": "pkg:pypi/fastapi@0.109.0",
      "licenses": [{"id": "MIT"}],
      "hashes": [{"alg": "SHA-256", "content": "abc123..."}]
    }
  ],
  "dependencies": [
    {
      "ref": "pkg:pypi/fastapi@0.109.0",
      "dependsOn": ["pkg:pypi/starlette@0.35.0", "pkg:pypi/pydantic@2.5.0"]
    }
  ]
}
```

**SBOM 표준 비교:**

| 표준 | 관리 조직 | 강점 | 채택 |
|------|-----------|------|------|
| **CycloneDX** | OWASP | 보안 중심, VEX 통합 | 보안 커뮤니티 |
| **SPDX** | Linux Foundation | 라이선스 중심, ISO 표준 | 컴플라이언스 |

**Step 3 — 다양한 관점: 스택별 의존성 보안 비교**

**Python:**

```bash
pip-audit          # PyPI 취약점 DB (osv.dev)
safety             # PyUp 취약점 DB (상용)
pip-compile        # 의존성 잠금 (pip-tools)
cyclonedx-bom      # SBOM 생성


```

**Go:**

```bash
govulncheck        # 공식 Go 취약점 DB (vuln.go.dev)
nancy              # Sonatype OSS Index
go mod graph       # 의존성 트리 시각화
cyclonedx-gomod    # SBOM 생성


```

**Kotlin/JVM:**

```bash
OWASP Dependency-Check  # NVD 기반 (가장 포괄적)
Snyk                     # 상용, 자동 PR 생성
gradle dependencies      # 의존성 트리
cyclonedx-gradle-plugin  # SBOM 생성


```

**스택별 비교 표:**

| 차원 | Python | Go | Kotlin/JVM |
|------|--------|-----|------------|
| **Lock 파일** | requirements.txt (수동) / pip-compile | go.sum (자동, 암호학적) | gradle.lockfile (선택적) |
| **Checksum 검증** | pip hash (선택) | sum.golang.org (필수) | Maven Central 서명 |
| **Transitive 관리** | 약함 | MVS (강함) | 복잡함 (exclude 필요) |
| **공식 취약점 DB** | osv.dev | vuln.go.dev | NVD |
| **False Positive** | 높음 | 낮음 (govulncheck) | 중간 |
| **SBOM 도구 성숙도** | 중간 | 높음 | 높음 |

**Step 4 — 구체적 예시: Log4Shell 대응 타임라인**

```
2021-12-09 (목): CVE-2021-44228 공개
2021-12-10 (금):
  ├── SBOM이 있는 조직: 30분 내 영향 범위 파악 → 4시간 내 패치 배포
  └── SBOM이 없는 조직: "우리 어디에 Log4j 쓰지?" 2~3일 수동 조사
2021-12-11 (토):
  ├── govulncheck 사용자: "우리 Go 서비스는 영향 없음" 즉시 확인
  └── JVM 서비스: gradle dependencies | grep log4j → transitive 포함 발견
```

**교훈:**
1. SBOM은 "사고 전에" 준비해야 한다 — 사고 후에 만들면 늦다
2. Transitive 의존성이 진짜 위험 — 직접 의존하지 않아도 취약
3. 언어마다 tooling 성숙도가 다르다 — Go가 가장 앞서 있음

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 보안 수준 | 개발자 마찰 | 비용 |
|--------|-----------|-------------|------|
| **수동 감사** | 낮음 | 낮음 | 낮음 |
| **CI 게이트 (자동 차단)** | 높음 | 높음 | 중간 |
| **비동기 알림 (Slack)** | 중간 | 낮음 | 낮음 |
| **자동 PR (Snyk/Dependabot)** | 높음 | 중간 | 중간~높음 |
| **SLSA Level 3+** | 최고 | 높음 | 높음 |

권장: CI 게이트(CRITICAL/HIGH 차단) + 자동 PR(MEDIUM 이하) + 주간 SBOM 생성.

**Step 6 — 성장 & 심화**

- SLSA (Supply-chain Levels for Software Artifacts) — 빌드 보안 프레임워크
- Sigstore / cosign — 컨테이너 이미지 서명
- in-toto — 빌드 파이프라인 무결성 검증
- NIST SP 800-218 (SSDF) — 소프트웨어 공급망 보안 프레임워크

**🎯 면접관 평가 기준:**
- ✅ **L6 PASS:** SBOM의 목적과 구조 이해. 하나 이상의 스택에서 의존성 스캐닝 경험. Log4Shell 같은 사례의 교훈 설명.
- ✅ **L7 EXCEED:** 3개 스택의 도구/생태계 차이를 비교. 조직 수준의 SBOM 정책 수립. SLSA, Sigstore 등 최신 supply chain 보안 프레임워크 이해. CI/CD에 자동화 통합 경험.
- 🚩 **RED FLAG:** SBOM을 모름. "npm audit만 돌린다"로 끝. Transitive 의존성의 위험성 인식 부재. 공급망 공격 벡터를 설명하지 못함.

---

### Q38: Secret Management — Vault, AWS SM, Rotation

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Security Across Stacks

**Question:**
프로덕션 환경에서 시크릿(API 키, DB 비밀번호, 인증서 등)을 어떻게 관리하는가? 환경변수, HashiCorp Vault, AWS Secrets Manager의 trade-off를 설명하라. Secret rotation은 왜 필요하고 어떻게 무중단으로 구현하는가? Python, Go, Kotlin 환경에서의 통합 방식은 어떻게 다른가?

---

**🧒 12살 비유:**
집 열쇠를 관리하는 세 가지 방법이 있다. (1) **화분 밑에 숨기기(환경변수):** 가족은 다 알고, 찾기 쉽지만, 도둑도 알 수 있다. (2) **은행 금고(Vault):** 가장 안전하지만, 열쇠를 꺼내려면 은행에 가야 하고, 은행이 문 닫으면 곤란하다. (3) **스마트 도어락(AWS SM):** 편리하고 안전하지만, 매달 비용이 나간다. Secret rotation은 "3개월마다 열쇠를 바꾸는 것" — 누군가 열쇠를 복사했더라도 3개월 후에는 무용지물이 된다. 핵심은 열쇠를 바꾸는 동안 집에 못 들어가면 안 된다는 것(무중단).

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

시크릿 유출은 가장 흔하고 비용이 큰 보안 사고 중 하나다. GitGuardian 보고서에 따르면 2023년 GitHub 공개 커밋에서 발견된 시크릿이 1200만 건 이상이다. 면접관은 (1) 시크릿 관리의 계층적 이해, (2) 도구별 trade-off 분석, (3) rotation의 무중단 구현 역량, (4) 스택별 통합 경험을 평가한다.

**Step 2 — 핵심 설명: Secret Management 계층**

**시크릿 관리 성숙도 모델:**

```
Level 0: 코드에 하드코딩                    ← 절대 금지
Level 1: 환경변수                           ← 최소 수준
Level 2: 암호화된 설정 파일 (SOPS, sealed-secrets)
Level 3: 중앙 집중 시크릿 관리 (Vault, AWS SM)
Level 4: Dynamic Secrets + Auto-Rotation    ← 목표
Level 5: Zero Standing Privileges           ← 이상적
```

**도구별 비교:**

| 차원 | 환경변수 | HashiCorp Vault | AWS Secrets Manager |
|------|----------|-----------------|---------------------|
| **보안** | 낮음 (ps, /proc 노출) | 최고 (암호화, 감사) | 높음 (KMS 통합) |
| **동적 시크릿** | 불가 | 가능 (DB, PKI) | 제한적 (RDS 가능) |
| **Rotation** | 수동 | 자동 + 커스텀 | 자동 (Lambda) |
| **운영 복잡도** | 없음 | 높음 (HA, unsealing) | 낮음 (managed) |
| **비용** | 무료 | 오픈소스/Enterprise | $0.40/secret/월 |
| **Multi-cloud** | 해당 없음 | 가능 | AWS only |
| **감사 로그** | 없음 | 상세 | CloudTrail |

**Vault Dynamic Secrets:**

```
┌─────────┐     1. Request DB creds      ┌─────────┐
│   App   │──────────────────────────────►│  Vault  │
│         │                               │         │
│         │◄──────────────────────────────│         │
│         │     2. Temporary creds        │         │
│         │        (TTL: 1h)              │         │
└────┬────┘                               └────┬────┘
     │                                         │
     │  3. Connect with temp creds             │ 4. Auto-revoke
     │                                         │    after TTL
     ▼                                         ▼
┌─────────┐                               ┌─────────┐
│   DB    │                               │  Revoke  │
└─────────┘                               └─────────┘
```

핵심: DB 비밀번호가 "고정"이 아니라 "요청할 때마다 생성되고 자동 만료"된다. 유출되어도 1시간 후 무효.

**Step 3 — 다양한 관점: 무중단 Secret Rotation**

**Dual-Version Rotation 패턴:**

```
Phase 1: Create new secret (v2), keep old (v1) active
   ├── DB에 새 비밀번호(v2) 추가 (v1도 유효)
   └── App은 여전히 v1 사용 중

Phase 2: Update app to use new secret (v2)
   ├── App config 업데이트 → v2로 전환
   └── Connection pool graceful drain

Phase 3: Revoke old secret (v1)
   ├── v1 비활성화
   └── 모니터링으로 v1 사용 없음 확인

총 소요: 수 분 (자동화 시)
```

**스택별 통합 방식:**

**Python (FastAPI + AWS SM):**

```python
import boto3
from functools import lru_cache
import json

class SecretManager:
    def __init__(self):
        self.client = boto3.client("secretsmanager")
        self._cache: dict[str, tuple[str, float]] = {}
        self._ttl = 300  # 5분 캐시

    def get_secret(self, secret_id: str) -> dict:
        now = time.time()
        if secret_id in self._cache:
            value, cached_at = self._cache[secret_id]
            if now - cached_at < self._ttl:
                return json.loads(value)

        response = self.client.get_secret_value(SecretId=secret_id)
        self._cache[secret_id] = (response["SecretString"], now)
        return json.loads(response["SecretString"])

```

**Go (Vault SDK):**

```go
import (
    vault "github.com/hashicorp/vault/api"
)

func NewVaultClient() (*vault.Client, error) {
    config := vault.DefaultConfig()
    client, err := vault.NewClient(config)
    if err != nil {
        return nil, fmt.Errorf("vault client: %w", err)
    }
    client.SetToken(os.Getenv("VAULT_TOKEN"))
    return client, nil
}

func GetDBCreds(client *vault.Client) (string, string, error) {
    secret, err := client.Logical().Read("database/creds/my-role")
    if err != nil {
        return "", "", fmt.Errorf("vault read: %w", err)
    }
    username := secret.Data["username"].(string)
    password := secret.Data["password"].(string)
    // secret.LeaseDuration → TTL, 자동 갱신 가능
    return username, password, nil
}

// 특징: Dynamic secrets 네이티브, lease 기반 자동 갱신
// 주의: Vault Agent Sidecar로 앱 코드 변경 최소화 가능
```

**Kotlin (Spring Cloud Vault):**

```kotlin
// application.yml
// spring:
//   cloud:
//     vault:
//       uri: https://vault.example.com
//       authentication: KUBERNETES
//       kubernetes:
//         role: my-app
//       generic:
//         backend: secret
//       database:
//         enabled: true
//         role: my-db-role

@Configuration
class DatabaseConfig {
    @Value("\${spring.datasource.username}")  // Vault에서 자동 주입
    lateinit var dbUsername: String

    @Value("\${spring.datasource.password}")  // Vault에서 자동 주입
    lateinit var dbPassword: String
}

// 특징: Spring Cloud Vault가 자동으로 Vault 연동
// PropertySource 추상화로 앱 코드 변경 불필요
// DB credential rotation 시 connection pool 자동 갱신
// 주의: Spring Boot 시작 시 Vault 연결 필수 → 장애 전파 가능
```

**Step 4 — 구체적 예시: 시크릿 유출 사고 대응**

```
T+0분:   GitGuardian 알림 — GitHub public repo에 AWS Access Key 노출
T+2분:   AWS Access Key 즉시 비활성화 (IAM Console)
T+5분:   새 Access Key 생성 + Secrets Manager 업데이트
T+10분:  영향받는 서비스 재시작 (새 키 로드)
T+15분:  CloudTrail 감사 — 키가 악용되었는지 확인
T+30분:  git-filter-repo로 Git 히스토리에서 키 제거
T+1시간: 사후 분석(Post-mortem) 작성
T+1주:   pre-commit hook에 gitleaks 추가 (재발 방지)
```

**Step 5 — 트레이드오프 & 대안**

| 시나리오 | 권장 도구 | 이유 |
|----------|-----------|------|
| **스타트업 (5인 이하)** | AWS SM + env vars | 운영 부담 최소 |
| **중규모 (Multi-team)** | Vault (OSS) | Dynamic secrets, 세밀한 접근 제어 |
| **대규모 (Multi-cloud)** | Vault Enterprise | Multi-cloud, 네임스페이스 |
| **Kubernetes 네이티브** | External Secrets Operator + AWS SM/Vault | K8s Secret과 자동 동기화 |

**시크릿 관리 안티패턴:**

| 안티패턴 | 리스크 | 대안 |
|----------|--------|------|
| .env 파일을 Git에 커밋 | 영구적 유출 | .gitignore + pre-commit hook |
| 모든 서비스가 같은 시크릿 공유 | 폭발 반경 확대 | 서비스별 시크릿 분리 |
| Rotation 없음 | 유출 시 무기한 악용 | 90일 자동 rotation |
| 시크릿 접근 로그 없음 | 감사 불가 | Vault 감사 로그 활성화 |

**Step 6 — 성장 & 심화**

- HashiCorp Vault Architecture Guide — HA 구성, Auto-unseal
- AWS Secrets Manager Rotation Templates — Lambda 기반 자동 rotation
- NIST SP 800-57 — 키 관리 권고사항
- "Zero Trust Networks" (Gilman & Barth) — 시크릿을 포함한 제로 트러스트 아키텍처

**🎯 면접관 평가 기준:**
- ✅ **L6 PASS:** 환경변수의 한계 인식. Vault 또는 AWS SM 사용 경험. Secret rotation의 필요성 이해.
- ✅ **L7 EXCEED:** Dynamic secrets 구현 경험. 무중단 rotation 설계. 시크릿 유출 사고 대응 경험. 3개 스택에서의 통합 방식 비교. 조직 수준의 시크릿 관리 정책 수립.
- 🚩 **RED FLAG:** 환경변수만으로 충분하다고 인식. Rotation 개념 부재. 시크릿을 코드/Git에 커밋한 경험을 문제로 인식 못함.

---

### Q39: API Security — Rate Limiting, CORS, CSP

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Security Across Stacks

**Question:**
프로덕션 API의 보안을 어떻게 설계하는가? Rate limiting의 알고리즘별 trade-off를 설명하라. CORS와 CSP는 무엇을 보호하고, 잘못 설정하면 어떤 공격에 노출되는가? Input validation은 어느 레이어에서 해야 하는가? Python(FastAPI), Go(net/http), Kotlin(Spring) 각각의 보안 미들웨어 구현을 비교하라.

---

**🧒 12살 비유:**
집에 친구를 초대했는데, 보안 규칙이 필요하다. (1) **Rate Limiting:** "1시간에 초인종 10번까지만 누를 수 있어" — 장난으로 초인종을 계속 누르는 걸 방지. (2) **CORS:** "우리 집 정문으로만 들어와. 뒷문(다른 웹사이트)에서는 우리 집 물건을 가져갈 수 없어." (3) **CSP:** "우리 집에서는 승인된 장난감(스크립트)만 사용할 수 있어. 밖에서 이상한 장난감을 가져오면 작동 안 돼." (4) **Input Validation:** "선물을 가져오면 현관에서 X-ray 검사 — 위험한 물건은 안 됨."

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

API는 공격 표면의 최전선이다. OWASP API Security Top 10(2023)의 대부분이 인증/인가, rate limiting, input validation 부재와 관련된다. 면접관은 (1) 계층별 보안 설계(Defense in Depth) 능력, (2) rate limiting 알고리즘에 대한 깊은 이해, (3) CORS/CSP의 정확한 이해, (4) 스택별 미들웨어 구현 경험을 평가한다.

**Step 2 — 핵심 설명: API 보안 계층**

**Defense in Depth — API 보안 레이어:**

```
Internet
    │
    ▼
┌──────────────┐
│   WAF/CDN    │  ← DDoS 방어, Bot 탐지, GeoIP 차단
├──────────────┤
│   API GW     │  ← Rate Limiting, 인증, API Key 검증
├──────────────┤
│  App Layer   │  ← Input Validation, CORS, CSP, 비즈니스 인가
├──────────────┤
│  Data Layer  │  ← 암호화, 접근 제어, 감사 로그
└──────────────┘
```

**Rate Limiting 알고리즘 비교:**

| 알고리즘 | 동작 | 장점 | 단점 | 구현 복잡도 |
|----------|------|------|------|-------------|
| **Fixed Window** | 고정 시간 윈도우 (예: 1분)당 카운트 | 단순, 메모리 효율적 | 윈도우 경계에서 2배 burst 가능 | 낮음 |
| **Sliding Window Log** | 요청 타임스탬프 기록 | 정확함 | 메모리 소비 큼 | 중간 |
| **Sliding Window Counter** | 이전/현재 윈도우 가중 평균 | 정확 + 메모리 효율 | 근사값 | 중간 |
| **Token Bucket** | 일정 속도로 토큰 충전, 요청 시 소비 | Burst 허용 + 평균 제한 | 설정 파라미터 많음 | 중간 |
| **Leaky Bucket** | 일정 속도로 처리, 초과 시 큐잉/드롭 | 출력 속도 균일 | Burst 허용 안 함 | 중간 |

**Token Bucket 상세:**

```
Parameters:
  - capacity: 10 (버킷 최대 토큰)
  - refill_rate: 2/sec (초당 토큰 충전)

Timeline:
  T=0:  tokens=10
  T=0:  burst 5 requests → tokens=5   ← burst 허용
  T=1:  refill +2 → tokens=7
  T=1:  3 requests → tokens=4
  T=2:  refill +2 → tokens=6
  ...

분산 환경: Redis + Lua script로 원자적 연산
```

**CORS (Cross-Origin Resource Sharing):**

```

Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true

Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 86400
```

**CSP (Content Security Policy):**

```

Content-Security-Policy:
  default-src 'self';
  script-src 'self' https://cdn.example.com;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' https://api.example.com;
  frame-ancestors 'none';              # 클릭재킹 방지
  report-uri /csp-violation-report;    # 위반 리포팅

```

**Step 3 — 다양한 관점: 스택별 보안 미들웨어 비교**

**Python (FastAPI):**

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/resource")
@limiter.limit("10/minute")
async def get_resource(request: Request):
    ...

from pydantic import BaseModel, Field, EmailStr

class CreateUser(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=0, le=150)

```

**Go (net/http + 미들웨어):**

```go
// Rate Limiting (golang.org/x/time/rate — Token Bucket)
func RateLimitMiddleware(rps float64, burst int) func(http.Handler) http.Handler {
    limiter := rate.NewLimiter(rate.Limit(rps), burst)
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            if !limiter.Allow() {
                w.Header().Set("Retry-After", "60")
                http.Error(w, "Too Many Requests", http.StatusTooManyRequests)
                return
            }
            next.ServeHTTP(w, r)
        })
    }
}

// Per-IP Rate Limiting (sync.Map + rate.Limiter)
var visitors sync.Map

func getVisitorLimiter(ip string) *rate.Limiter {
    v, loaded := visitors.LoadOrStore(ip, rate.NewLimiter(10, 20))
    if !loaded {
        go func() { // cleanup after 3min
            time.Sleep(3 * time.Minute)
            visitors.Delete(ip)
        }()
    }
    return v.(*rate.Limiter)
}

// CORS (rs/cors)
c := cors.New(cors.Options{
    AllowedOrigins:   []string{"https://app.example.com"},
    AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE"},
    AllowCredentials: true,
})
handler := c.Handler(mux)

// Input Validation (go-playground/validator)
type CreateUser struct {
    Name  string `json:"name" validate:"required,min=1,max=100"`
    Email string `json:"email" validate:"required,email"`
    Age   int    `json:"age" validate:"gte=0,lte=150"`
}

// 특징: 명시적 미들웨어 체이닝, 표준 라이브러리 활용
// 장점: 컴파일 타임 검증, 제로 매직, 성능 최적
// 주의: Per-IP limiter 메모리 관리 필수 (visitor cleanup)
```

**Kotlin (Spring Security + Bucket4j):**

```kotlin
// Rate Limiting (Bucket4j — Token Bucket)
@Configuration
class RateLimitConfig {
    @Bean
    fun rateLimitFilter(): FilterRegistrationBean<RateLimitFilter> {
        val registration = FilterRegistrationBean<RateLimitFilter>()
        registration.filter = RateLimitFilter()
        registration.addUrlPatterns("/api/*")
        return registration
    }
}

class RateLimitFilter : OncePerRequestFilter() {
    private val buckets = ConcurrentHashMap<String, Bucket>()

    override fun doFilterInternal(
        request: HttpServletRequest,
        response: HttpServletResponse,
        chain: FilterChain
    ) {
        val ip = request.remoteAddr
        val bucket = buckets.computeIfAbsent(ip) { createBucket() }
        if (bucket.tryConsume(1)) {
            chain.doFilter(request, response)
        } else {
            response.status = 429
            response.setHeader("Retry-After", "60")
        }
    }

    private fun createBucket(): Bucket = Bucket.builder()
        .addLimit(Bandwidth.classic(10, Refill.greedy(10, Duration.ofMinutes(1))))
        .build()
}

// CORS (Spring Security)
@Bean
fun corsConfigurationSource(): CorsConfigurationSource {
    val config = CorsConfiguration().apply {
        allowedOrigins = listOf("https://app.example.com")
        allowedMethods = listOf("GET", "POST", "PUT", "DELETE")
        allowCredentials = true
    }
    return UrlBasedCorsConfigurationSource().apply {
        registerCorsConfiguration("/api/**", config)
    }
}

// Input Validation (Jakarta Bean Validation)
data class CreateUser(
    @field:NotBlank @field:Size(min = 1, max = 100) val name: String,
    @field:Email val email: String,
    @field:Min(0) @field:Max(150) val age: Int
)

// 특징: Spring Security Filter Chain, 선언적 검증
// 장점: Bean Validation 표준, 에러 핸들링 통합
// 주의: Filter 순서가 보안에 직접 영향
```

**Step 4 — 구체적 예시: CORS Misconfiguration 공격**

```
공격 시나리오:
1. victim.com API가 Access-Control-Allow-Origin: * 설정
2. evil.com에서 JavaScript로 victim.com API 호출
3. 로그인한 사용자의 브라우저가 쿠키를 자동 첨부
4. evil.com이 사용자 데이터를 탈취

방어:
1. Allow-Origin을 명시적 도메인으로 제한
2. Allow-Credentials: true 시 * 사용 불가 (브라우저가 거부)
3. Origin 헤더의 동적 반영 금지 — 화이트리스트 방식만 사용
```

**Input Validation 레이어 전략:**

```
Client-side:  UX용 (빠른 피드백). 보안 목적 아님.
API Gateway:  스키마 검증 (JSON Schema). 기본 필터링.
App Layer:    비즈니스 규칙 검증. 핵심 보안 레이어. ← 여기가 메인
Data Layer:   DB 제약조건. 최후의 방어선.

원칙: "Never trust client input. Validate at every boundary."
```

**Step 5 — 트레이드오프 & 대안**

| 차원 | 엄격한 보안 | 개발 편의성 |
|------|-------------|-------------|
| **CORS** | 명시적 Origin only | `*` 허용 |
| **CSP** | `strict-dynamic` + nonce | `unsafe-inline` |
| **Rate Limit** | Per-user + Per-IP | Global only |
| **Validation** | 4-layer 검증 | App layer only |

**Rate Limiting 분산 환경:**

| 접근 | 정확도 | 성능 | 운영 복잡도 |
|------|--------|------|-------------|
| **Local (in-memory)** | 인스턴스별 분산 | 최고 | 낮음 |
| **Redis centralized** | 정확 | 네트워크 왕복 | 중간 |
| **Redis + local cache** | 근사 | 높음 | 중간 |
| **API Gateway (Kong, Envoy)** | 정확 | 높음 | 높음 |

**Step 6 — 성장 & 심화**

- OWASP API Security Top 10 (2023) — API 특화 보안 위협
- "API Security in Action" (Neil Madden) — 실전 API 보안 설계
- Cloudflare Rate Limiting Architecture — 글로벌 분산 rate limiting
- Mozilla Observatory — HTTP 보안 헤더 진단 도구

**🎯 면접관 평가 기준:**
- ✅ **L6 PASS:** Rate limiting 알고리즘 2개 이상 설명. CORS/CSP의 보호 대상 명확히 이해. 한 가지 스택에서의 보안 미들웨어 구현 경험.
- ✅ **L7 EXCEED:** Token Bucket vs Sliding Window의 trade-off를 분산 환경에서 분석. CORS misconfiguration 공격 시나리오 설명. 3개 스택의 보안 미들웨어 비교. 조직 수준의 API 보안 표준 수립 경험.
- 🚩 **RED FLAG:** Rate limiting을 "그냥 Nginx에서 설정"으로 끝. CORS를 `*`로 설정해도 괜찮다고 인식. Input validation을 클라이언트에서만 수행. CSP를 모르거나 `unsafe-inline`을 문제로 인식 못함.

---

> **End of Cross-Stack Categories 6-7**
> Q31~Q39 (9문항) | Technical Leadership 5문항 + Security Across Stacks 4문항
