---
tags: [cache, write-through, cache-aside, read-through, stampede, hibernate-l2, redis]
created: 2026-04-14
---

# 📚 캐시 전략 완전 가이드

---

## 1. 캐시 전략 개요 — 4가지 패턴

| 항목              | Cache-Aside (Lazy Loading)       | Write-Through                  | Write-Behind (Write-Back)      | Read-Through                   |
| ----------------- | -------------------------------- | ------------------------------ | ------------------------------ | ------------------------------ |
| **읽기 흐름**     | App→Cache, MISS→DB→Cache         | App→Cache (항상 HIT)           | App→Cache (항상 HIT)           | App→Cache, MISS→자동 DB        |
| **쓰기 흐름**     | App→DB (캐시 안 건듦)            | App→Cache→DB (동기)            | App→Cache→비동기 DB            | App→Cache→동기 DB              |
| **쓰기 지연**     | 없음                             | ⚠️ 높음                       | ✅ 낮음                        | ⚠️ 높음                       |
| **읽기 지연**     | ⚠️ MISS 시 높음                 | ✅ 항상 낮음                   | ✅ 항상 낮음                   | ⚠️ MISS 시 높음               |
| **데이터 정합성** | ⚠️ stale 가능                   | ✅ 강력                        | ❌ 유실 위험                   | ✅ 강력                        |
| **Stampede 위험** | 🔴 높음                         | 🟢 거의 없음                  | 🟢 거의 없음                  | 🟡 Provider 의존              |
| **복잡도**        | ✅ 낮음                          | 🟡 중간                       | 🔴 높음                       | 🟡 중간                       |
| **대표 사용처**   | 범용 (검색 결과, 추천)           | 금융/결제 (정합성 중요)        | 게임 리더보드, 카운터          | CDN, Hibernate L2              |

---

## 2. Cache-Aside (Lazy Loading)

### 동작 원리

```
Client ──읽기──▶ Service ──▶ Cache.get("menu:123")
                               │
                          HIT? ├── Yes → 반환
                               └── No (MISS) → DB 조회 → 캐시 적재 → 반환
```

### Cache-Aside가 적합한 경우

1. **내가 데이터의 쓰기를 제어할 수 없을 때** — 다른 서비스가 DB를 직접 수정, Legacy 시스템이 DB 공유
2. **읽히지 않는 데이터까지 캐시하고 싶지 않을 때** — 100만 상품 중 조회되는 건 10%뿐, Cache-Aside는 실제 읽힌 것만 캐시 → 메모리 효율적

### Cache-Aside + Invalidation 전략 조합

| 조합                       | 동작                                               | Stampede 위험  |
| -------------------------- | -------------------------------------------------- | -------------- |
| **+ TTL**                  | 시간 지나면 자동 삭제 → 다음 읽기 시 DB             | 🔴 높음        |
| **+ 명시적 DELETE**        | DB 업데이트 후 cache.delete(key)                    | 🟡 중간        |
| **+ Event → DELETE**       | DB 변경 → Event → Consumer가 delete                 | 🟡 중간        |
| **+ Event → SET (덮어쓰기)** | DB 변경 → Event → Consumer가 새 데이터 set          | 🟢 거의 없음   |

---

## 3. Write-Through

### 동작 원리

```
Client ──쓰기──▶ Service ──▶ DB에 저장 + Cache에도 저장 (동시)
Client ──읽기──▶ Service ──▶ Cache HIT! ✅ (항상 최신)
```

### ⚠️ Write-Through의 Race Condition — Meta의 해결법

동시 쓰기 시 `cache.set()`은 Race Condition이 발생할 수 있다. Meta (Facebook)은 **Write + DELETE** 패턴을 사용:

```
✅ Meta 방식:
  db.update(key, newValue)
  cache.delete(key)  ← 멱등(idempotent)! 순서 무관!
  → 다음 읽기: MISS → DB에서 최신 값 로드
```

추가 안전장치로 **mcsqueal 데몬**이 MySQL binlog (CDC)를 읽어 캐시 무효화 이벤트를 발행. 일일 조 단위 쿼리에서 **99.99999999% (10 nines) 일관성** 달성.

> 출처: Meta Engineering Blog — "Cache Made Consistent" (2022)

### DB 성공 + Cache 실패 시

```
실무 원칙: DB가 Source of Truth, Cache는 Best Effort

1. DB 저장 ✅
2. Cache 쓰기 시도
   ├── 성공 → 끝
   └── 실패 → 1~2회 retry → 그래도 실패 → 로그 남기고 넘어감
       → 다음 읽기 시 Cache MISS → DB에서 복구 (Cache-Aside 폴백)

❌ Transaction Outbox Pattern은 캐시에 과잉(Overkill)
   Cache는 유실되어도 DB에서 복구 가능 → Outbox 불필요
```

> 💡 **Cache는 DB의 그림자.** 그림자가 잠깐 사라져도 원본(DB)이 있으니 괜찮다.

> 출처: abstractalgorithms.dev

---

## 4. Write-Behind (Write-Back)

### 동작 원리와 핵심 가치

```
[Write-Through] 쓰기 10번 = DB 쓰기 10번, 응답 6ms
[Write-Behind]  쓰기 10번 = DB 쓰기 1번!, 응답 1ms
```

**핵심: Write Coalescing + Write Combining** (Oracle Coherence 문서 기준)

| 최적화              | 동작                                                         | 효과                   |
| ------------------- | ------------------------------------------------------------ | ---------------------- |
| **Write-Coalescing** | 같은 키 병합 — user:123에 10번 쓰기 → 마지막 값만 DB에 1번 저장 | 같은 키 쓰기 부하 제거 |
| **Write-Combining**  | 다른 키들을 묶어 배치 — user:123, user:456 → 1번의 DB TX로 처리 | DB 트랜잭션 수 감소    |

### "DB에 왜 넣어? Cache 영속성 쓰면 되잖아?"

Redis 영속성(AOF/RDB)과 Write-Behind는 **다른 문제를 푼다**:

- **Redis AOF/RDB**: Redis 자체가 죽었을 때 Cache 데이터 복구 → "Cache 안의 데이터 보호"
- **Write-Behind**: DB의 쓰기 부하를 줄이면서 데이터를 DB에 넣기 → "DB를 Write Storm으로부터 보호"

DB가 여전히 필요한 이유: SQL 쿼리(JOIN, GROUP BY), BI 도구 연결, 감사/규정 준수용 영구 기록, 대용량 히스토리 저장.

> 출처: Oracle Coherence Docs, AWS Caching Strategies Whitepaper

### 실제 사용 사례

| 사용처                   | 왜 Write-Behind          | 유실 허용도        |
| ------------------------ | ------------------------ | ------------------ |
| 페이지뷰/좋아요 카운터   | 초당 1000+ 증가, 같은 키 | 몇 개 유실 OK      |
| 게임 리더보드            | 빠른 점수 업데이트        | 짧은 불일치 허용   |
| 세션 관리                | 빈번한 세션 갱신          | 짧은 stale OK      |
| 분석/텔레메트리          | 극단적 속도의 이벤트 수집 | 배치 집계와 맞음   |

---

## 5. Read-Through

### Cache-Aside와의 핵심 차이: "누가 DB를 조회하느냐"

```
[Cache-Aside = 셀프 서비스 식당] 🍽️
  너 → 카운터에 음식 있나 확인 → 없으면 직접 주방 가서 주문
  너가 "카운터"와 "주방" 둘 다 알아야 함

[Read-Through = 풀서비스 레스토랑] 🍽️
  너 → 웨이터에게 "치킨 주세요" → 웨이터가 알아서 확인/주문
  너는 "웨이터"만 알면 됨
```

| 항목              | Cache-Aside                      | Read-Through                                |
| ----------------- | -------------------------------- | ------------------------------------------- |
| **DB 조회 주체**  | App 코드                         | Cache 레이어 (CacheLoader)                  |
| **Stampede 방지** | ❌ 직접 구현 필요                | ✅ 내장 (partition lock 자동 직렬화)        |
| **코드 결합도**   | 로딩 로직이 App 전체에 산재       | CacheLoader에 캡슐화                        |
| **대표 사례**     | Redis 직접 사용                  | Hibernate L2, CDN, Oracle Coherence, AWS DAX |

### Read-Through Stampede 방지 — Oracle Coherence

100개 Thread 동시 `cache.get("menu:123")` → Partition Owner가 service-level Lock 획득 → `CacheLoader.load()` 1번만 호출. 나머지 99개는 Lock 대기 후 캐시 반환.

> "keys will have been locked at the Service level already" — Oracle Coherence ReadWriteBackingMap Javadoc

### Redis에는 이 기능이 없다

**Redis는 근본적으로 Cache-Aside 시스템.** CacheLoader 인터페이스 없음. Stampede 방지는 App에서 직접 구현 필요.

> 출처: AWS Whitepaper — Database Caching Strategies Using Redis

### 캐시 제품 계층

| Level                | 제품                                          | Read-Through | Stampede 방지 |
| -------------------- | --------------------------------------------- | ------------ | ------------- |
| **단순 Key-Value**   | Redis, Memcached                              | ❌           | ❌ 직접 구현  |
| **스마트 캐시**      | Oracle Coherence, Hazelcast, EhCache          | ✅           | ✅ 내장 Lock  |
| **ORM 내장 캐시**    | Hibernate L2 (위 프레임워크를 플러그인으로)    | ✅ 투명      | Provider 의존 |

---

## 6. Cache Stampede

### 개념

캐시가 만료되는 순간, 수많은 요청이 동시에 DB를 때리는 현상.

```
도시락 다 팔림 (= 캐시 만료)
  👤👤👤...× 1000명: "도시락 없네? 창고에서 가져와!"
  → 창고(DB)에 1000명 동시 몰림 💥
```

### 방지 전략

**방법 A: Distributed Lock** — 캐시 만료 후 1명만 DB 조회, 나머지 대기. Redis Lock 필요.

**방법 B: Probabilistic Early Expiration** — 캐시 만료 전 확률적으로 미리 갱신. 추가 인프라 불필요.

**Cold Start 방지**: Cache Warming (인기 데이터 미리 적재) + Staggered TTL (TTL에 랜덤 지터 추가).

### Cache Miss 시 Lock을 거는 이유

데이터 override는 OK, **DB 부하가 문제**. Lock 없이 1000개 동시 MISS → 동일 쿼리 1000번. Lock 있으면 → 1번만.

---

## 7. Hibernate L1 vs L2 Cache

### 구조

```
Session (요청 1개)
  └── L1 Cache: JVM 힙 HashMap, Entity 객체 참조
       → 같은 Session 안에서만 유효, Session 끝나면 사라짐

SessionFactory (앱 전체)
  └── L2 Cache: EhCache/Hazelcast/Redis
       → Dehydrated 컬럼 값 저장 (Entity 객체 아님!)
       → 모든 Session 공유, 명시적 설정 필요
```

> 비유: L1 = 책상 메모지 (퇴근하면 버림), L2 = 사무실 화이트보드

### L2 6대 함정 (Django Johnny Cache와 동일)

| #  | 함정                     | 설명                                                    |
| -- | ------------------------ | ------------------------------------------------------- |
| 1  | **Stale 데이터**         | ORM 외부 DB 수정 시 캐시 무효화 안 됨                   |
| 2  | **Native Query 우회**    | `createNativeQuery("UPDATE ...")` 는 L2 무효화 안 함    |
| 3  | **Collection 별도**      | Entity 캐시해도 `@OneToMany`는 별도 설정 필요           |
| 4  | **Query Cache N+1**      | ID만 저장 → Entity 없으면 N번 개별 SELECT               |
| 5  | **메모리 압박**          | 대량 Entity 시 GC pause                                |
| 6  | **디버깅 지옥**          | stale 원인 특정 매우 어려움                             |

### 실제 채택률

대규모 기업 대부분 L2 안 씀. L2 적합: 중규모 엔터프라이즈, 모놀리스, 읽기 전용 참조 데이터만.

> Vlad Mihalcea: "L2 캐시는 읽기 전용 데이터에만 유용. 범용 캐시로 쓰지 마라."

---

## 8. EhCache vs Hazelcast vs Redis

| 항목              | EhCache           | Hazelcast              | Redis             |
| ----------------- | ----------------- | ---------------------- | ----------------- |
| **위치**          | JVM 내부 (로컬)   | JVM + P2P 클러스터     | 외부 서버         |
| **서버 간 공유**  | ❌ 독립 (stale!)  | ✅ 자동 동기화         | ✅ 중앙 서버      |
| **속도**          | 🟢 나노초         | 🟡 중간               | 🟡 중간          |
| **적합한 경우**   | 단일 서버         | 다중 서버, MSA         | 범용              |

분산 환경 EhCache만 → **반드시 Hazelcast/Redis 필요.** 실무 가장 흔한 선택: **L2 안 쓰고 Redis Cache-Aside.**

---

## 9. Python Read-Through: dogpile.cache

```python
from dogpile.cache import make_region

region = make_region().configure(
    'dogpile.cache.redis', expiration_time=3600,
    arguments={'host': 'localhost', 'port': 6379, 'db': 0}
)

@region.cache_on_arguments()
def get_menu(menu_id):
    return Menu.objects.get(id=menu_id)
```

**dogpile lock**: 만료 시 1 Thread만 DB 조회, 나머지는 stale 즉시 반환.

---

## 10. 캐시 전략 선택 의사결정 트리

```
읽기:쓰기 >= 10:1?  ── No → 캐시하지 마라
                     └ Yes → 쓰기 시점 제어 가능?
                              ├ Yes + 정합성 중요 → Write-Through (Write+DELETE)
                              └ No → Event 수신 가능? → Event Invalidation / Cache-Aside + TTL
```

### 배달 서비스 적용

| 데이터              | 전략                         | 이유                             |
| ------------------- | ---------------------------- | -------------------------------- |
| 메뉴/레스토랑 정보  | **Write-Through (Write+DELETE)** | CUD 제어 가능, 정합성 중요       |
| 주문 상태           | **캐시 안 함**               | 실시간 정합성 + 읽기 빈도 낮음   |
| 가게 영업상태       | **Write-Through**            | 즉시 반영 필수                   |
| 검색 결과/추천      | **Cache-Aside + TTL**        | stale OK                        |

### 모니터링 임계치

- **Cache hit ratio**: 목표 > 90%, 80% 미만 → 전략 재검토
- **P99 latency on miss**: 비캐시 경로 2~3배 초과 → Cache Warming 필요

---

## 📎 출처

| 출처                                         | 주제                                |
| -------------------------------------------- | ----------------------------------- |
| Meta Engineering — "Cache Made Consistent"   | Write+DELETE, mcsqueal, 10 nines    |
| Oracle Coherence Documentation               | Read-Through, Write-Behind          |
| AWS Caching Strategies Whitepaper            | 전략 비교, Redis 패턴               |
| Vlad Mihalcea                                | Hibernate READ_WRITE Soft Lock      |
| dogpile.cache 공식 문서                      | Python Read-Through + Stampede 방지 |
