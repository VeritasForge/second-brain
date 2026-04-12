---
created: 2026-03-06
source: claude-code
tags:
  - database
  - mysql
  - postgresql
  - timestamp
  - datetime
  - unix-epoch
  - dst
---

# TIMESTAMP vs DATETIME Deep Dive

MySQL과 PostgreSQL의 시간 타입 비교, 내부 저장 구조, 설계 배경까지 정리한 기술 문서.

---

## 1. MySQL — TIMESTAMP vs DATETIME

### 비교표

| 항목      | TIMESTAMP                             | DATETIME                         |
| --------- | ------------------------------------- | -------------------------------- |
| 저장 방식 | UTC로 변환 후 저장                    | 입력값 그대로 저장               |
| 조회 시   | 세션 timezone으로 자동 변환           | 그대로 반환                      |
| 범위      | 1970-01-01 00:00:01 ~ 2038-01-19 03:14:07 UTC | 1000-01-01 00:00:00 ~ 9999-12-31 23:59:59 |
| 크기      | 4바이트 (+0~3B fractional)            | 5바이트 (+0~3B fractional)       |

> **Fractional Seconds Precision (FSP)**
> FSP 0: 추가 0B / FSP 1-2: +1B / FSP 3-4: +2B / FSP 5-6: +3B
> 즉, `DATETIME(6)` = 8바이트, `TIMESTAMP(6)` = 7바이트.
> DATETIME 5바이트는 MySQL 5.6.4+ 기준. 그 이전에는 8바이트였음.

### 쓰임 차이

#### 핵심 판단 기준

| 기준 | TIMESTAMP | DATETIME |
| ---- | --------- | -------- |
| 질문 | "이 사건이 **언제** 발생했는가?" | "이 값이 **무엇**인가?" |
| 시각의 주체 | 시스템이 자동으로 찍는 시점 | 사람이 정하는 시각 |
| 핵심 가치 | 절대 시점 (어느 순간) | 시각 자체 (몇 시) |

한 줄 요약: **TIMESTAMP = 절대 시점(시스템)**, **DATETIME = 비즈니스 시각(사람)**

**TIMESTAMP가 적합한 경우** — 시스템이 자동으로 찍는 시점

- `created_at`, `updated_at`, `last_login_at` — 레코드 생성/수정 시점
- `sent_at`, `ingested_at`, `processed_at`, `acknowledged_at` — 이벤트 라이프사이클 시각
- 이벤트 간의 **순서와 간격**이 중요하고, UTC 절대값이 유지되면 충분한 경우
- 이벤트 기반 시스템에서 발신/수신 서버가 다른 timezone에 있을 수 있어, UTC 자동 변환의 장점이 극대화됨

**DATETIME이 적합한 경우** — 사람이 정하는 시각

- 예약 시간, 진료 일시, 생년월일
- timezone 변환 없이 입력한 그대로 유지해야 할 때
- 2038년 이후 날짜가 필요할 때

#### created_at에 TIMESTAMP가 적합한 이유

DATETIME은 timezone 변환을 하지 않으므로, **모든 서버/클라이언트가 같은 timezone으로 쓴다는 전제**가 필요하다.

```
DATETIME + 컨벤션 없을 때:
서버 A (KST): INSERT → created_at = 2026-03-10 14:00:00
서버 B (UTC): INSERT → created_at = 2026-03-10 05:00:00
→ 같은 순간인데 다른 값 저장 → 순서 비교, 지연 계산 깨짐

TIMESTAMP라면:
서버 A (KST): INSERT → 저장: 2026-03-10 05:00:00 UTC
서버 B (UTC): INSERT → 저장: 2026-03-10 05:00:00 UTC
→ DB 레벨에서 자동 UTC 통일
```

| | TIMESTAMP | DATETIME |
| --- | --- | --- |
| 다중 timezone 서버 | 자동으로 UTC 통일 | 직접 UTC 통일 컨벤션 필요 |
| 컨벤션 없이 써도 안전 | O | X |
| 사람의 실수 의존 | X | O |

세션마다 표시가 달라지는 건 오히려 **장점**이다:

```
같은 created_at을 조회할 때:
한국 개발자 (KST):  2026-07-16 03:00:00  → "새벽 3시에 생성됐구나"
미국 개발자 (EDT):  2026-07-15 14:00:00  → "오후 2시에 생성됐구나"
→ 둘 다 같은 절대 시점, 자기 시간대 기준으로 이해 가능
```

#### 문제 사례 ① — 생년월일 날짜 밀림

`1990-03-15`을 TIMESTAMP로 저장하면:

```
저장: 1990-03-15 00:00:00 KST
  → UTC 변환: 1990-03-14 15:00:00 UTC (저장)
  → 세션 timezone이 UTC로 바뀌면: 3월 14일로 표시
```

생년월일은 "1990년 3월 15일"이라는 **값 자체**가 의미이지, 특정 시점이 아니다. DATETIME으로 저장해야 어떤 timezone에서 조회하든 `3월 15일`이 유지된다.

#### 문제 사례 ② — 예약 시각의 장소 맥락 소실

"도쿄 미용실 오후 2시 예약"을 TIMESTAMP로 저장하면:

```
일본 유저가 "2026-04-01 14:00" (JST) 예약 입력
→ DB에 UTC로 저장: 2026-04-01 05:00:00 UTC

중국 유저가 조회 (세션 timezone: CST/+8)
→ 2026-04-01 13:00:00 으로 보임
→ "도쿄 14시"인지 앱에서 추가 변환 로직이 필요
```

본질적 문제: **비즈니스 시각은 "어느 지역의 몇 시"라는 맥락이 필요한데, TIMESTAMP는 그 맥락을 날려버리고 UTC 절대 시점으로 바꿔버린다.**

권장 패턴 — **DATETIME + timezone 컬럼**:

```sql
reservation_time  DATETIME     -- 2026-04-01 14:00:00
timezone          VARCHAR(40)  -- Asia/Tokyo
-- 어디서 조회하든 "도쿄 14시"임이 명확
-- 필요하면 앱에서 유저 로컬 시각으로 변환 표시
```

> **주의 — DATETIME의 timezone 함정**
> DATETIME은 TZ 변환을 하지 않으므로, 서로 다른 timezone의 서버가 같은 DB에 쓸 경우 시간값이 모호해질 수 있다. 이때는 애플리케이션 레벨에서 UTC로 통일하여 저장하거나, timezone을 별도 컬럼에 기록해야 한다.

---

## 2. PostgreSQL — TIMESTAMP vs TIMESTAMPTZ

### 비교표

| 항목      | TIMESTAMP WITHOUT TIME ZONE          | TIMESTAMP WITH TIME ZONE (TIMESTAMPTZ)           |
| --------- | ------------------------------------ | ------------------------------------------------ |
| 저장 방식 | 입력값 그대로 저장                   | UTC로 변환 후 저장 (원래 timezone 정보는 미보존)  |
| 조회 시   | 그대로 반환                          | 세션 timezone으로 자동 변환                       |
| 크기      | 8바이트                              | 8바이트                                          |
| 범위      | 4713 BC ~ 294276 AD                  | 동일                                             |

> **TIMESTAMPTZ와 timezone 보존**
> TIMESTAMPTZ는 이름과 달리 timezone을 저장하지 않는다. 입력 시 timezone을 참조하여 UTC로 변환한 뒤, UTC 값만 보관한다. "사용자가 어떤 timezone에서 입력했는가"가 필요하면 별도 컬럼에 timezone name을 저장해야 한다.

### DEFAULT now() 동작

```sql
-- PostgreSQL
created_at TIMESTAMPTZ DEFAULT now()              -- OK
created_at TIMESTAMPTZ DEFAULT (now())            -- OK, 동일하게 동작
created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP  -- OK, SQL 표준
```

PostgreSQL에서 `now()`, `CURRENT_TIMESTAMP`, `transaction_timestamp()`은 모두 **현재 트랜잭션 시작 시각**을 `timestamptz`로 반환한다. `now()`는 PostgreSQL 고유 함수, `CURRENT_TIMESTAMP`는 SQL 표준 키워드라는 차이만 있을 뿐, MySQL처럼 괄호 유무로 내부 처리 경로(synonym vs expression default)가 갈리지 않는다.

> **statement vs clock 시각**
> 트랜잭션 내에서 시간이 흐른 뒤의 시각이 필요하면 `clock_timestamp()`를 사용한다.
> `now()` / `CURRENT_TIMESTAMP`는 트랜잭션 동안 값이 변하지 않는다.

### 자주 혼동되는 공식 문서 인용 (정정)

PostgreSQL 공식 문서가 "We do not recommend using the type …"이라고 비권장하는 것은 **`time with time zone`** (`timetz`) 타입이다. DST 때문에 날짜 없는 시간에 timezone을 붙이는 것이 의미가 없기 때문.

`timestamp without time zone` 비권장은 **공식 문서가 아닌 커뮤니티 위키**([Don't Do This](https://wiki.postgresql.org/wiki/Don't_Do_This)) 출처이므로 구분이 필요하다.

---

## 3. MySQL vs PostgreSQL 크로스 비교

| 항목      | MySQL DATETIME | MySQL TIMESTAMP | PG TIMESTAMP | PG TIMESTAMPTZ |
| --------- | -------------- | --------------- | ------------ | -------------- |
| TZ 변환   | X              | O               | X            | O              |
| UTC 저장  | X              | O               | X            | O              |
| 2038 제한 | X              | O               | X            | X              |
| 크기      | 5B             | 4B              | 8B           | 8B             |

### 핵심 차이점

**MySQL** — TIMESTAMP에 2038년 제한이 있어서 DATETIME을 선호하는 경우가 많음. MySQL 8.0.28+에서 `UNIX_TIMESTAMP()`, `FROM_UNIXTIME()` 등 **함수**는 64비트 플랫폼에서 2038 이후를 지원하도록 확장되었으나, **TIMESTAMP 컬럼 타입 자체의 범위는 여전히 2038-01-19까지**임.

**PostgreSQL** — 8바이트 정수(microseconds since 2000-01-01)로 저장하므로 2038년 제한 없음. 커뮤니티 위키([Don't Do This](https://wiki.postgresql.org/wiki/Don't_Do_This))에서 TIMESTAMPTZ를 거의 항상 권장함.

### 미래 예약 시간에 대한 주의

미래의 예약 시간(예: "6개월 뒤 뉴욕 시간 오후 3시")에는 TIMESTAMP/TIMESTAMPTZ 모두 적합하지 않다. DST 규칙이 변경될 수 있기 때문이다. 이 경우 **local time + timezone name**(`America/New_York`)을 별도 컬럼에 저장하는 것이 권장 패턴이다.

#### 구체적 시나리오 — 뉴욕 병원 진료 예약

2026년 1월에 유저가 6개월 뒤 진료를 예약한다.

```
예약 입력: 2026-07-15 14:00 (뉴욕 시각, EDT, UTC-4)
TIMESTAMP 저장: 2026-07-15 18:00:00 UTC
```

미국에서는 **Sunshine Protection Act**(2022년 상원 통과, 하원 미통과)로 DST 폐지 논의가 계속되고 있다. 만약 2026년 3월에 법이 통과되어 "7월에도 EST(UTC-5)를 쓴다"로 바뀌었다고 가정하면:

```
1월 (예약 시점)                          7월 (진료 시점)
    │                                        │
    ├─ 유저 의도: "7월 15일 오후 2시"         │
    ├─ 당시 규칙: EDT (UTC-4)               │
    ├─ UTC 변환: 18:00 UTC ──저장──→        DB: 18:00 UTC
    │                                        │
    │   3월: DST 폐지법 통과                 │
    │   timezone DB 업데이트                  │
    │                                        │
    │                                   조회 시: EST (UTC-5) 적용
    │                                   → 18:00 - 5 = 13:00
    │                                   → 오후 1시로 표시 ❌
```

DATETIME + timezone 컬럼이었다면 저장된 값 `14:00` 자체가 유지되므로 의미 훼손이 없다.

#### 과거 이벤트는 왜 괜찮은가

과거에 저장된 `created_at = 2026-01-15 18:00:00 UTC`는 **실제로 그 UTC 시점에 일어난 역사적 사실**이다. DST 규칙이 바뀌어도 로컬 시각 표시만 달라질 뿐, **같은 순간을 가리킨다는 사실은 변하지 않는다.**

| | created_at (시스템 시각) | 예약 시각 (비즈니스 시각) |
| --- | --- | --- |
| 로컬 표시 바뀜 | 같은 **시점**의 다른 표현 | 다른 **약속**이 되어버림 |
| 핵심 가치 | 절대 시점 (UTC) | 사람이 정한 시각 자체 |
| 표시가 바뀌면 | 의미 동일 | 의미 훼손 |

`created_at` 같은 시스템 시각은 "현지 몇 시였는지"보다 이벤트 간의 **순서와 간격**이 중요하므로, UTC 절대값이 유지되면 충분하다. 반면 미래 예약은 아직 일어나지 않은 **약속**이라, "뉴욕 오후 2시"라는 의도가 중요하지 UTC 값이 중요한 게 아니다.

---

## 4. 내부 저장 구조 — 왜 2038년까지인가?

### 핵심 원리

MySQL TIMESTAMP는 내부적으로 **Unix epoch 초**(1970-01-01 00:00:00 UTC 이후 경과한 초)를 **32비트 signed integer**로 저장한다.

```
32비트 signed integer 양수 최대: 2,147,483,647

2,147,483,647초 ÷ 60 ÷ 60 ÷ 24 ÷ 365.25 ≈ 68.05년

1970 + 68년 = 2038년 (정확히: 2038-01-19 03:14:07 UTC)
```

이것이 **Y2K38 (Year 2038 Problem)** 이다.

### 32비트 signed integer의 전체 표현 범위

```
음수 최소: -2,147,483,648  →  1901-12-13 20:45:52 UTC
양수 최대:  2,147,483,647  →  2038-01-19 03:14:07 UTC
```

### 왜 unsigned가 아니라 signed인가?

MySQL TIMESTAMP에 한정하면 사실 **합리적 설계라고 보기 어렵다.**

```
Unix time_t (C 표준)  →  signed int32로 정의됨
MySQL TIMESTAMP       →  내부적으로 time_t 기반
                      →  signed를 물려받음
                      →  하지만 음수(1970 이전)는 거부하기로 결정
```

Unix `time_t`는 1970년 이전 시간을 음수로 표현하기 위해 signed를 채택했다. 하지만 MySQL TIMESTAMP는 음수를 허용하지 않으므로(범위 시작이 1970-01-01 00:00:01), signed의 이점은 사용하지 않는 셈이다.

unsigned int32를 사용했다면 범위가 **2106년**까지 확장 가능했지만, Unix 생태계(C `time_t`, 시스템콜)의 관례를 따르다 보니 signed를 그대로 계승한 것이다.

### 비교: 각 타입의 내부 표현

| 타입               | 내부 표현                                 | 크기 | 한계       |
| ------------------ | ----------------------------------------- | ---- | ---------- |
| MySQL TIMESTAMP    | Unix epoch 초 (signed int32)              | 4B   | 2038-01-19 |
| MySQL DATETIME     | 날짜/시간 필드를 비트 패킹                | 5B   | 9999-12-31 |
| PG TIMESTAMPTZ     | 2000-01-01 기준 마이크로초 (signed int64) | 8B   | 294276 AD  |

### signed → unsigned 변환 시

비트 패턴은 동일하고 **해석만 달라진다** (two's complement):

```
비트 패턴              signed 해석        unsigned 해석
00000000...0000        0                  0
01111111...1111        2,147,483,647      2,147,483,647      ← 여기까지 동일
10000000...0000       -2,147,483,648      2,147,483,648      ← 여기서 갈림
11111111...1111       -1                  4,294,967,295
```

즉 1970년 이전 시간(음수)이 2038년 이후 시간(큰 양수)으로 잘못 해석된다.

---

## 5. Epoch 설계 배경

### Unix — 왜 1970-01-01인가?

- **초기 Unix epoch는 1971-01-01이었다.** PDP-7에서 돌아가던 초기 Unix(1969~1970)에서 시간을 1/60초 단위 unsigned 32비트로 저장했는데, 약 2.5년 만에 오버플로우 발생
- 이후 **초 단위로 변경**하면서 epoch를 1970-01-01 00:00:00 UTC로 재설정
- 1970년 1월 1일이 선택된 이유: Unix 개발 시점에 가장 가까운 **깔끔한 연도 시작점**
- 특별한 수학적/천문학적 이유는 없음 — 순전히 실용적 편의

### PostgreSQL — 왜 2000-01-01인가?

- PostgreSQL이 현재 형태로 재설계된 시점(1990년대 후반)에 가까운 **깔끔한 밀레니엄 시작점**
- **signed int64**를 사용하므로 epoch이 어디든 범위 문제가 없음
- 2000년 이전 시간은 **음수로 표현**:

```
2000-01-01 00:00:00  →  0
1999-12-31 23:59:59  → -1,000,000  (마이크로초)
1970-01-01 00:00:00  → -946,684,800,000,000
```

- 4713 BC까지만 지원하는 것은 int64의 한계가 아니라 **율리우스 역법의 시작점**(천문학적 기준일)에 맞춘 의도적 제한

### 1600년대는 signed int32로 표현 가능한가?

**불가능하다.**

```
1970 - 1600 = 370년
370 × 365.25 × 24 × 3600 ≈ 11,676,096,000초

signed int32 음수 최대: 2,147,483,648초 ≈ 68년 전 (≈ 1901년)
```

int32로는 약 1901년까지만 가능. 1600년대를 표현하려면 int64가 필요하다.

---

## 6. DST와 Timezone 변경 실제 사례

### "한국 서비스니까 괜찮지 않나?"

실무적으로 동작은 한다. 한국은 DST 없고, 단일 timezone(KST)이므로 실제로 많은 한국 서비스가 TIMESTAMP를 사용하고 있다.

다만 DATETIME을 권장하는 이유는 "지금 안 되는 것"이 아니라 **방어적 설계** 때문이다:

| 리스크 | 설명 |
| ------ | ---- |
| timezone 정책 변경 | 한국도 1987-1988년 서울 올림픽 때 DST를 시행한 적 있음 |
| 글로벌 확장 | 일본/중국만 추가해도 timezone 이슈 발생 |
| DB 서버 설정 변경 | timezone 설정이 바뀌면 TIMESTAMP 조회값이 달라짐 |
| 마이그레이션/덤프 복원 | timezone 불일치 시 시간이 밀림 |
| MySQL 2038년 제한 | TIMESTAMP 컬럼 타입의 범위 한계 |

DATETIME을 쓴다고 비용이 더 드는 것도 아니니, **"굳이 TIMESTAMP를 쓸 이유가 없다"**가 더 정확한 판단 기준이다.

### DST 역사적 사례

timezone 규칙은 정치적 결정이라 언제든 바뀔 수 있다.

| 국가 | 사건 |
| ---- | ---- |
| 러시아 | 2011년 영구 서머타임 채택 → 2014년 영구 표준시로 재변경 |
| 북한 | 2015년 UTC+8:30 도입 → 2018년 UTC+9로 복귀 |
| 터키 | 2016년 DST 폐지, 영구 UTC+3 (서머타임 고정) |
| 이집트 | DST 도입/폐지를 반복 (1957, 1975, 1982, 2011, 2014, 2015, 2023) |
| 모로코 | 영구 UTC+1이나 라마단 기간엔 시계를 1시간 되돌림 |
| 한국 | 1948-1951, 1955-1960 시행 → 26년 중단 → 1987-1988 올림픽용 일시 부활 → 이후 폐지 |

> **한국 DST 이력 정정**
> "1988년까지 DST를 시행"이라고 하면 오해의 소지가 있다. 1960년 이후 26년간 중단되었다가, 서울 올림픽(미국 TV 중계 시간대 맞추기)을 위해 1987-1988년에 **일시 부활**한 것이다. 정확한 표현은 **"마지막으로 시행한 해가 1988년"**이다.

---

## 7. Sources

1. [MySQL 8.0: Date/Time Types](https://dev.mysql.com/doc/refman/8.0/en/datetime.html) — 공식 문서
2. [MySQL 8.0: Storage Requirements](https://dev.mysql.com/doc/refman/8.0/en/storage-requirements.html) — 공식 문서
3. [PostgreSQL Docs: 8.5 Date/Time Types](https://www.postgresql.org/docs/current/datatype-datetime.html) — 공식 문서
4. [PostgreSQL Docs: 9.9 Date/Time Functions](https://www.postgresql.org/docs/current/functions-datetime.html) — 공식 문서
5. [PostgreSQL Wiki: Don't Do This](https://wiki.postgresql.org/wiki/Don't_Do_This) — 커뮤니티 위키
6. [PlanetScale: Datetimes vs Timestamps](https://planetscale.com/blog/datetimes-vs-timestamps-in-mysql) — 기술 블로그
7. [MySQL WL#1872](https://dev.mysql.com/worklog/task/?id=1872) — TIMESTAMP 범위 확장 제안 (미구현)
8. [MySQL 8.4: Server Time Zone Support](https://dev.mysql.com/doc/refman/8.4/en/time-zone-support.html) — 공식 문서
9. [W3C: Working With Time Zones](https://www.w3.org/TR/timezone/) — 표준 가이드
10. [timeanddate.com](https://www.timeanddate.com/news/time/) — 각국 timezone 변경 이력
