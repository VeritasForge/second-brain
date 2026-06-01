---
tags: [postgresql, concurrency, advisory-lock, redlock]
created: 2026-06-01
---

# 동시성 제어 정리: Advisory Lock · SELECT FOR UPDATE · Redis Redlock

## 1. 배경 — 왜 락이 필요한가: "COUNT 후 INSERT"의 함정

rate-limit은 "이메일당 하루 10통"을 셉니다. 그런데 두 요청이 **동시에** 오면 race condition이 발생합니다:

```text
요청A: COUNT 해보니 9통 (한도 10)
요청B: COUNT 해보니 9통 (동시에! 아직 A가 INSERT 전)
요청A: 9 < 10 → INSERT (이제 10통)
요청B: 9 < 10 → INSERT (이제 11통!)  ← 한도 초과 🚨
```

"세고 나서 넣기" 사이의 틈에 끼어드는 것이 문제입니다. 이 틈을 막으려면 "같은 키에 대해 한 번에 하나씩만" 처리하도록 직렬화해야 합니다.

---

## 2. Advisory Lock (권고 잠금)

### 2-1. 개념 — "내가 정한 이름표에 거는 열쇠"

PostgreSQL의 보통 잠금은 DB가 **행/테이블**에 자동으로 겁니다. 반면 **advisory lock은 애플리케이션이 "내가 정한 임의의 키"에 거는 자율적 잠금**입니다. DB는 그 키가 뭘 뜻하는지 모릅니다 — 그냥 "이 키는 지금 한 명이 쥐고 있다"만 관리합니다.

```ts
await tx.execute(sql`SELECT pg_advisory_xact_lock(hashtext(${k}))`);
//                    └─ 트랜잭션 동안 잠금   └─ "email:user@x.com" 문자열을
//                                              숫자로 변환(락 키는 숫자여야 함)
```

**비유: 공용 작업대의 이름표 팻말** 🪧

- `"email:user@x.com"`이라는 **이름표 팻말**을 세움 → "이 이메일 작업은 지금 내가 처리 중"
- `xact`(transaction) = 트랜잭션이 끝나면 팻말 **자동 반납**
- 다른 요청이 같은 팻말을 세우려 하면 → 앞 사람이 반납할 때까지 **대기**

락을 걸면 §1의 race가 사라집니다:

```text
요청A: 🪧팻말 획득 → COUNT 9 → INSERT(10통) → 팻말 반납
요청B: 🪧팻말 대기...... → 획득 → COUNT 10 → "한도 초과" 거부 ✅
```

### 2-2. "advisory"라는 용어의 뿌리 — OS 파일 잠금

`advisory`(권고적)는 원래 **Unix 파일 잠금**에서 나온 일반 컴퓨팅 용어입니다. 잠금에는 두 종류가 있습니다:

| 종류             | 의미                                                                | 비유                                                  |
| ---------------- | ------------------------------------------------------------------- | ----------------------------------------------------- |
| **advisory (권고)** | 모두가 "락을 확인하기로 **약속**"해야만 작동. 약속 안 한 코드는 무시하고 건드릴 수 있음 | 회의실 문의 **"사용 중" 팻말** 🪧 — 팻말 무시하고 들어가는 사람은 못 막음 |
| **mandatory (강제)** | 시스템이 **강제**. 락 무시 불가                                      | 회의실 문이 **전자키로 실제 잠김** 🔒                  |

**DB의 advisory lock은 "팻말" 방식** — 애플리케이션끼리 협조적으로 쓰는 약속이지, DB가 강제하는 게 아닙니다. (그래서 §6의 "constraint 최후 방어"가 필요합니다.)

### 2-3. DB마다 이름이 다르다 (개념은 공통, 명칭은 PostgreSQL이 표준)

"애플리케이션이 임의의 키에 거는 협조적 잠금"이라는 개념은 여러 DB에 있지만, 부르는 이름이 다릅니다:

| DB             | 함수                                          | 부르는 이름                          |
| -------------- | --------------------------------------------- | ------------------------------------ |
| **PostgreSQL** | `pg_advisory_lock`, `pg_advisory_xact_lock`   | **"Advisory Locks"** (공식 용어)     |
| **MySQL**      | `GET_LOCK()`, `RELEASE_LOCK()`                | "named lock" / "user-level lock"     |
| **SQL Server** | `sp_getapplock`, `sp_releaseapplock`          | "application lock"                   |
| **Oracle**     | `DBMS_LOCK` 패키지                            | "user lock"                          |

→ "advisory lock"이라는 정확한 명칭으로 부르는 건 **PostgreSQL이 표준화**한 것입니다.

### 2-4. `pg_advisory_xact_lock` 이름 분해

```text
pg_advisory_xact_lock
│   │        │    └─ lock  : 잠금 획득
│   │        └────── xact  : transaction 스코프 (트랜잭션 끝나면 자동 해제)
│   └─────────────── advisory : 권고적 잠금
└─────────────────── pg_   : PostgreSQL 내장 함수 접두사
```

- `pg_` = PostgreSQL 빌트인 함수 표식
- `xact` 버전은 **트랜잭션 종료 시 자동 해제** — `db.transaction(...)` 안에서 쓰면 안전. (`pg_advisory_lock`은 세션 스코프라 수동 `pg_advisory_unlock` 필요 — 깜빡하면 락이 안 풀림)

---

## 3. Advisory Lock "정렬" — deadlock(교착) 방지

여러 키를 한 번에 잠글 때(예: `email:`, `verify-attempt:`, `ipKey`, `pending:`) **순서가 제멋대로면 교착**이 생깁니다.

**Deadlock 비유: 좁은 복도에서 마주친 두 사람** 🚶↔️🚶

```text
요청1: 🔑email 쥠 → 🔑ip 기다림
요청2: 🔑ip 쥠   → 🔑email 기다림
→ A는 B가 ip 놓길, B는 A가 email 놓길 기다림 → 영원히 멈춤 (deadlock)
```

**해결: 모두가 같은 순서로 잡는다 = 정렬**

```ts
const sorted = [...keys].sort();        // ← 키를 정렬
for (const k of sorted) {
  await tx.execute(sql`SELECT pg_advisory_xact_lock(hashtext(${k}))`);
}
```

**비유: "1번 방 → 2번 방 → 3번 방" 순서 약속** 🔑🔑🔑 — 모두가 같은 순서(정렬)로 잠그면 누가 먼저든 한 명이 다 잡고 끝내므로 교착이 불가능합니다.

---

## 4. `SELECT ... FOR UPDATE`와의 차이

| 항목                                | `SELECT ... FOR UPDATE`           | Advisory Lock                          |
| ----------------------------------- | --------------------------------- | -------------------------------------- |
| 잠그는 것                           | **실제 존재하는 행(row)**         | **임의의 숫자 키** (데이터 무관)       |
| **없는 데이터 잠금**                | ❌ 불가                           | ✅ 가능                                |
| **INSERT race(phantom) 방지**       | ❌ (잠글 행 없음)                 | ✅                                     |
| 여러 테이블 논리 작업 묶기          | 어려움                            | ✅ 키로 묶음                           |
| 주 용도                             | **기존 행 read-modify-write**     | **미존재 엔티티·논리 작업 직렬화**     |

### 결정적 차이 — "아직 없는 것을 잠글 수 있는가?"

**두 요청이 동시에 `user@x.com`으로 가입 시도 (첫 가입이라 행이 아직 없음):**

```text
[FOR UPDATE]
요청A: SELECT * FROM pending WHERE email='user@x.com' FOR UPDATE
       → 행이 없음! → 잠글 대상 없음 → 통과
요청B: 똑같이 → 통과 → 둘 다 INSERT → 중복 ❌

[Advisory Lock]
요청A: pg_advisory_xact_lock(hashtext('email:user@x.com'))
       → 행이 없어도 "이 이메일 키" 잠금 ✅ → 직렬화 → 중복 방지 ✅
```

**비유: 주차장** 🅿️

- **FOR UPDATE** = 특정 **주차칸**에 "사용 중" 콘 놓기 → 칸(행)이 있어야 가능
- **Advisory** = "이 차량 번호 처리 중" **번호표** → 칸 배정 전(행 없음)에도 직렬화

### 언제 무엇을

- **`FOR UPDATE`**: 이미 존재하는 행 수정 (예: 계좌 잔액 차감 `SELECT balance ... WHERE id=1 FOR UPDATE`)
- **Advisory**: 미존재 엔티티 / 새 행 INSERT 경쟁 / 여러 자원 묶은 작업 직렬화

> 💡 advisory를 쓰는 핵심 이유: ① 카운터 테이블에 **새 행 INSERT** 경쟁(막을 기존 행 없음) ② 첫 가입이면 **pending이 아직 없음** ③ **여러 키를 하나의 논리 작업으로** 묶어 직렬화.

---

## 5. Redis Redlock(분산 락)과의 차이

### 닮은 점

둘 다 **임의의 키에 거는 협조적 락** — FOR UPDATE와 달리 "없는 것"도 잠글 수 있음.

### 다른 점 — 락과 데이터의 "거리"

| 항목                | PostgreSQL Advisory Lock          | Redis Redlock                         |
| ------------------- | --------------------------------- | ------------------------------------- |
| 락 관리 위치        | **DB 내부** (이미 쓰는 postgres)  | **별도 Redis 인스턴스 여러 개**(보통 5개) |
| 추가 인프라         | 불필요 (DB 재사용)                | Redis 클러스터 필요                   |
| **락 ↔ 데이터 거리** | **같은 DB·트랜잭션 안** (밀착)    | **분리** (락=Redis, 데이터=postgres)  |
| 해제 방식           | 트랜잭션 종료 시 자동             | **TTL(Time To Live) 만료**            |
| 분산 가용성         | DB primary 의존                   | 여러 Redis 과반(N/2+1)으로 분산       |
| 안전성              | 트랜잭션과 통합 → 일관            | **논쟁적**                            |

**비유: 락을 "건물 안"에 두느냐 "건물 밖"에 두느냐** 🏛️

- **Advisory** = 도서관 안에서 **사서가 직접** 관리 → 책(데이터)과 락이 **같은 건물**
- **Redlock** = 도서관 **밖 별도 경비실(Redis)** 에 명단을 둠 → 떨어져 있어 **불일치 위험**(경비실 명단 만료됐는데 도서관에선 작업 중)

### Redlock의 안전성 논쟁 (Martin Kleppmann, 『DDIA』 저자, 2016)

```text
1. 클라이언트A가 Redlock 획득 (TTL 10초)
2. A에서 GC(Garbage Collection) pause / 네트워크 지연 12초 발생
3. TTL 만료 → 락 자동 해제 → 클라이언트B가 같은 락 획득
4. A가 깨어남 → 자기가 아직 락 가졌다고 착각 → B와 동시 진입 💥
```

Redlock은 **fencing token**(단조 증가 번호로 stale 작업 거부)이 없어 clock drift·GC pause·네트워크 지연 시 동시 진입 가능. (antirez 반박 있어 여전히 논쟁적) — Kleppmann 권고: *"efficiency(중복 작업 줄이기)엔 OK, correctness(반드시 한 명만)엔 부적합"*.

반면 advisory lock은 **트랜잭션과 통합**되어, 클라이언트가 죽으면 연결이 끊기고 DB가 락 해제 + 데이터 변경도 롤백 → **락과 데이터가 항상 같은 운명**.

### 언제 무엇을

- **Advisory**: 이미 DB를 쓰고 **락 직후 바로 그 DB에 작업**(락-데이터 한 트랜잭션). Redis를 끼우면 오히려 분리로 불일치 위험만 생김.
- **Redlock**: 락 대상이 **DB 외부 자원**(외부 API, 파일)이거나 **여러 독립 서비스 간** 락, RDB 없이 Redis만 있을 때. 단 fencing token으로 안전성 보완 필요.

---

## 6. DB Constraint — 최후 방어선

advisory lock은 **"권고적(약속)"** 이라 코드 버그·예외로 안 지켜질 수 있습니다. 그래서 데이터 정확성의 진짜 보장은 **DB constraint(강제적)** 에 둡니다.

```ts
email: text("email").notNull().unique(),   // 같은 이메일로 2번 INSERT 불가
```

+ 표현식 unique index(예: `lower(email)` 대소문자 무시), 임시 테이블의 key unique 등.

**비유: 놀이기구 안전바** 🎢

- **advisory lock** = 직원의 "한 명씩 타세요" 안내 (사람 약속 — 실수·버그 가능)
- **DB constraint** = 좌석의 **안전바** (물리적으로 한 명만, 두 명 타면 바가 안 내려감)

```text
1차 방어: advisory lock (예의상 줄서기 — 성능·정상 흐름)
              ↓ 혹시 뚫려도
최후 방어: DB unique constraint (물리적 차단기 — 절대 중복 안 됨)
```

설령 락이 뚫려 두 요청이 동시에 같은 이메일로 INSERT를 시도해도, **DB의 `UNIQUE`가 두 번째를 무조건 거부**합니다.

---

## 7. 정리 — 언제 무엇을 쓰나

| 메커니즘              | 잠그는 대상   | 주 용도                                       | 핵심 특성                          |
| --------------------- | ------------- | --------------------------------------------- | ---------------------------------- |
| **SELECT FOR UPDATE** | 존재하는 행   | 기존 행 read-modify-write (잔액 차감 등)      | 행 없으면 못 잠금                  |
| **Advisory Lock**     | 임의 키       | 미존재 엔티티·INSERT race·논리 작업 직렬화    | DB·트랜잭션과 밀착(안전), 권고적   |
| **Redis Redlock**     | 임의 키       | DB 외부 자원·다서비스 분산 락                 | 별도 Redis(분산), 안전성 논쟁(fencing 필요) |
| **DB Constraint**     | 데이터 자체   | 정확성 최후 보장                              | 강제적 — 락 실패해도 막음          |

**핵심 원칙**: *"락을 보호 대상(데이터)과 같은 시스템에 두라."*

- 보호 대상이 postgres 데이터 → 락도 postgres advisory lock (한 트랜잭션, 한 운명) → 단순·안전
- 동시성 정확성의 진짜 보장은 "락 테스트"가 아니라 **설계(advisory 직렬화 + 정렬) + DB 제약(최후 방어) + 코드 리뷰**의 조합

---

## Sources

- [PostgreSQL Docs — Advisory Locks](https://www.postgresql.org/docs/current/explicit-locking.html#ADVISORY-LOCKS)
- [Martin Kleppmann — How to do distributed locking (Redlock 비판, 2016)](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
