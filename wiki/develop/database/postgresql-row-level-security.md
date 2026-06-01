---
tags: [postgresql, rls, database-security, multi-tenancy]
created: 2026-06-01
---

# 📖 PostgreSQL RLS (Row-Level Security, 행 수준 보안) — Concept Deep Dive

> 💡 **한줄 요약**: RLS는 데이터베이스가 모든 쿼리에 자동으로 "보이지 않는 `WHERE` 절"을 덧붙여서, **누가 묻든 자기 행(row)만 보고/고치게** 강제하는 PostgreSQL의 보안 기능입니다.

🎨 **12살을 위한 비유**: 학교 사물함이 한 줄로 쭉 있다고 상상해봐. 보통은 마스터키(애플리케이션 코드)를 가진 사람이 "이 학생은 3번 사물함만 열 수 있어"라고 일일이 확인해줘야 해. 그런데 RLS는 **사물함마다 그 학생 지문에만 열리는 잠금장치**를 달아두는 거야. 누가 마스터키를 잃어버리거나 실수해도, 사물함 자체가 "넌 주인이 아니야"라며 안 열려. 잠금이 **사물함(데이터베이스) 안쪽**에 있다는 게 핵심이야! 🔐

---

## 1️⃣ 무엇인가? (What is it?)

**RLS (Row-Level Security)**는 PostgreSQL **9.5 버전(2016년)**부터 도입된 기능으로, 테이블에 **보안 정책(policy)**을 정의해서 사용자/역할(role)별로 **어떤 행을 SELECT/INSERT/UPDATE/DELETE 할 수 있는지**를 데이터베이스 엔진 차원에서 제어합니다.

- 📜 **공식 정의**: "Row security policies restrict which rows can be returned by normal queries or inserted, updated, or deleted by data modification commands" — [PostgreSQL 공식 문서](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- 🎯 **해결하려는 문제**: RLS 이전에는 "이 사용자는 자기 데이터만 봐야 한다"는 규칙을 **애플리케이션 코드의 모든 쿼리에 일일이** `WHERE user_id = ...`로 넣어야 했습니다. 쿼리 하나만 빠뜨려도 데이터가 새어 나가는(data leak) 위험이 있었죠. RLS는 이 책임을 **DB로 끌어내려** 한 곳에서 강제합니다.
- 🏛️ **핵심 통찰**: 정책은 **테이블에 묶이지 (tied to tables)**, **쿼리에 묶이지 않습니다 (not queries)**. 그래서 테이블 정책 한 번만 바꾸면 그 테이블을 건드리는 **모든 쿼리에 자동 적용**됩니다 — [Bytebase](https://www.bytebase.com/reference/postgres/how-to/postgres-row-level-security/)

> 📌 **핵심 키워드**: `POLICY`, `암시적 WHERE 절 (implicit WHERE)`, `default-deny`, `Defense in Depth`

---

## 2️⃣ 핵심 개념 (Core Concepts)

RLS는 4개의 핵심 구성 요소가 맞물려 동작합니다.

```
┌──────────────────────────────────────────────────────────┐
│                  RLS 핵심 구성 요소                        │
│                                                            │
│   ① ENABLE RLS        ② POLICY                             │
│   ┌────────────┐      ┌──────────────────────┐            │
│   │ 테이블에    │─────▶│  USING 절   (읽기 필터) │           │
│   │ 잠금 ON     │      │  WITH CHECK (쓰기 검증) │           │
│   └────────────┘      └──────────┬───────────┘            │
│         │                        │                         │
│         ▼                        ▼                         │
│   ③ ROLE (TO)          ④ Context 함수                      │
│   ┌────────────┐      ┌──────────────────────┐            │
│   │ 어떤 역할에 │      │ current_user /        │            │
│   │ 적용?       │      │ current_setting(...)  │            │
│   └────────────┘      └──────────────────────┘            │
└──────────────────────────────────────────────────────────┘
```

| 구성 요소                    | 역할         | 설명                                                                                         |
| --------------------------- | ----------- | ------------------------------------------------------------------------------------------- |
| `ENABLE ROW LEVEL SECURITY` | 🔌 스위치    | 켜지 않으면 정책을 만들어도 **무시됨**. 켜는 순간 정책 없는 테이블은 **default-deny(아무 행도 안 보임)** |
| `USING` 절                  | 👀 읽기 필터 | **기존 행**을 검사. SELECT/UPDATE/DELETE 시 이 조건이 `true`인 행만 보임                          |
| `WITH CHECK` 절             | ✍️ 쓰기 검증 | **새/수정될 행**을 검사. INSERT/UPDATE 시 `true`라야 통과, `false`면 에러                          |
| `TO role`                   | 👤 대상      | 어떤 DB 역할에 정책을 적용할지 지정 (생략 시 `PUBLIC` = 모두)                                      |

🔑 **가장 중요한 구분 — `USING` vs `WITH CHECK`**:

- `USING`은 "**볼 수 있는** 행"을 거릅니다 (read 방향).
- `WITH CHECK`는 "**쓸 수 있는** 행"을 거릅니다 (write 방향).
- ⚠️ 둘이 다르면 **"내가 볼 수 없는데 넣을 수는 있는"** 위험한 상황이 생깁니다 — [Bytebase footguns](https://www.bytebase.com/blog/postgres-row-level-security-footguns/)
- `WITH CHECK`를 생략하면 `USING` 조건이 자동으로 복사됩니다.

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

RLS는 쿼리가 들어오면 **다른 필터링보다 먼저** 정책을 적용합니다. 즉 "보이지 않는 `WHERE`"가 쿼리 플래너 단계에서 주입됩니다.

```
   애플리케이션 쿼리
   "SELECT * FROM documents;"
            │
            ▼
┌────────────────────────────────────────────────┐
│            PostgreSQL Query Planner              │
│                                                  │
│   1. RLS 정책 주입 (가장 먼저!)                  │
│      SELECT * FROM documents                     │
│      WHERE owner_id = current_user_id()  ◄── 자동│
│                                                  │
│   2. 사용자가 쓴 WHERE/JOIN/ORDER 적용           │
│                                                  │
│   3. 결과 반환 (정책 통과 행만)                  │
└────────────────────────────────────────────────┘
            │
            ▼
   본인 소유 문서만 반환 ✅
   (다른 사람 문서는 애초에 존재조차 안 보임)
```

### 🔄 동작 흐름 (Step by Step)

1. **Step 1 — 켜기**: `ALTER TABLE documents ENABLE ROW LEVEL SECURITY;`
2. **Step 2 — 정책 정의**: `CREATE POLICY ... USING (...) WITH CHECK (...)`
3. **Step 3 — 컨텍스트 주입**: 애플리케이션이 "지금 접속자는 누구"인지 DB에 알려줌 (`SET LOCAL`)
4. **Step 4 — 쿼리 실행**: DB가 정책 조건을 `WHERE`로 자동 삽입
5. **Step 5 — 강제**: 정책에 안 맞는 행은 **반환/수정 거부**

### 💻 기본 예시 — "내 문서만 보기"

```sql
-- 1. 테이블 생성
CREATE TABLE documents (
    id          serial PRIMARY KEY,
    owner_id    uuid,
    title       text,
    body        text
);

-- 2. RLS 켜기 (이 순간부터 default-deny)
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 3. 정책: 자기가 소유한 문서만 모든 작업 가능
CREATE POLICY documents_owner_policy ON documents
    FOR ALL                                   -- SELECT/INSERT/UPDATE/DELETE 전부
    USING      (owner_id = current_setting('app.user_id')::uuid)   -- 읽기 필터
    WITH CHECK (owner_id = current_setting('app.user_id')::uuid);  -- 쓰기 검증
```

### 💻 멀티테넌트(SaaS) 예시 — 런타임 변수 패턴 ⭐권장⭐

테넌트마다 DB 유저를 만드는 대신, **런타임 컨텍스트 변수**를 쓰는 게 베스트 프랙티스입니다 — [AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/saas-multitenant-managed-postgresql/rls.html)

```sql
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON orders
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- 애플리케이션이 트랜잭션마다 컨텍스트 주입:
BEGIN;
  SET LOCAL app.current_tenant = 'a1b2c3-...';   -- ⚠️ SET LOCAL (SET 아님!)
  SELECT * FROM orders;   -- 자동으로 이 테넌트 주문만 반환
COMMIT;   -- 트랜잭션 끝나면 컨텍스트 자동 리셋 → 커넥션 풀 안전
```

🔑 `SET LOCAL`을 쓰는 이유: 커넥션 풀(connection pool) 환경에서 트랜잭션이 끝나면 컨텍스트가 자동 초기화되어, **다음 사용자가 이전 테넌트 컨텍스트를 물려받는 사고**를 막습니다 — [The Nile](https://www.thenile.dev/blog/multi-tenant-rls)

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| # | 유즈 케이스                          | 설명                                          | 적합한 이유                            |
| - | ----------------------------------- | -------------------------------------------- | ------------------------------------- |
| 1 | **멀티테넌트 SaaS**                  | 한 테이블에 여러 고객사 데이터를 담고 `tenant_id`로 격리 | 고객마다 DB 분리는 비현실적, RLS로 논리적 격리 |
| 2 | **BaaS / 직접 DB 접근** (Supabase 등) | 브라우저가 DB에 직접 쿼리해도 안전                 | 클라이언트가 어떻게 접근하든 DB가 강제       |
| 3 | **다단계 권한 (조직/팀)**             | 사용자가 속한 팀의 데이터만 접근                  | 정책에 JOIN/함수로 소속 판정              |
| 4 | **규제 준수 (HIPAA/금융)**           | 민감 데이터를 역할별로 분리 접근                  | 감사(audit) 시 "DB가 강제했다"는 보증     |

### ✅ 베스트 프랙티스

1. **테넌트 데이터 테이블 전부에 RLS 적용**: 하나라도 빠지면 그 테이블이 구멍 — [AWS](https://aws.amazon.com/blogs/database/multi-tenant-data-isolation-with-postgresql-row-level-security/)
2. **런타임 변수 > 테넌트별 DB 유저**: 유저 폭증을 막고 커넥션 풀과 잘 맞음
3. **`SET LOCAL` 만 사용**: `SET`(세션 전역)은 풀 환경에서 컨텍스트 누수 위험
4. **`FORCE ROW LEVEL SECURITY` 적용**: 테이블 소유자도 정책을 받게 강제 (아래 7번 참고)
5. **정책 컬럼에 인덱스**: `USING`/`WITH CHECK`에 쓰인 컬럼은 반드시 인덱싱
6. **통합 테스트로 모든 접근 패턴 검증**: 테넌트 간 누수를 자동 테스트로 보증

### 🏢 실제 적용 사례

- **Supabase**: RLS를 인증/인가의 핵심으로 삼아, 브라우저에서 직접 PostgREST API로 DB 접근을 허용 — [Supabase Docs](https://supabase.com/docs/guides/database/postgres/row-level-security)
- **AWS**: 멀티테넌트 SaaS 레퍼런스 아키텍처에서 RLS를 데이터 격리 표준으로 권장 — [AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/saas-multitenant-managed-postgresql/welcome.html)

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분    | 항목                  | 설명                                                                                  |
| ------- | -------------------- | ------------------------------------------------------------------------------------ |
| ✅ 장점 | **DB 차원 강제**      | 클라이언트가 어떻게 접근하든(API/직접쿼리) 규칙이 새지 않음                                 |
| ✅ 장점 | **코드 단순화**       | 앱 쿼리는 비즈니스 `WHERE`만 신경, 보안 필터는 DB가 담당                                   |
| ✅ 장점 | **단일 진실 공급원**  | 정책이 테이블에 묶여 모든 쿼리에 일관 적용 → 변경 한 곳만                                   |
| ✅ 장점 | **Defense in Depth** | 앱 인가가 뚫려도 마지막 방어선 역할                                                       |
| ❌ 단점 | **성능 오버헤드**     | 잘못 짜면 행마다 함수/서브쿼리 호출 → 쿼리가 기하급수적으로 느려짐                           |
| ❌ 단점 | **디버깅 어려움**     | "왜 행이 안 나오지?" → 정책 때문인지 추적이 까다로움                                       |
| ❌ 단점 | **버전 관리 사각**    | 정책이 `pg_policies`(DB)에 살아서 코드 리뷰/Git 추적 누락되기 쉬움 — [PlanetScale](https://planetscale.com/blog/rls-sounds-great-until-it-isnt) |
| ❌ 단점 | **복잡한 권한 모델 한계** | 시간 기반/속성 기반(ABAC) 같은 정교한 규칙은 표현하기 어려움 — [Bytebase](https://www.bytebase.com/blog/postgres-row-level-security-limitations-and-alternatives/) |

### ⚖️ Trade-off 분석

```
보안 일관성   ◄──────── Trade-off ────────►   성능/단순함
(DB가 강제)                                   (잘못 짜면 느림)

운영 편의      ◄──────── Trade-off ────────►   디버깅 난이도
(테이블만 수정)                               (숨은 WHERE 추적)
```

> ⚡ **성능 핵심**: 최선의 경우 RLS는 그냥 `WHERE` 절 하나 추가 수준으로 저렴합니다. 최악의 경우(volatile 함수 호출) 행당 별도 함수 호출이 발생해 **3배 이상** 비싸집니다 — [PlanetScale](https://planetscale.com/blog/rls-sounds-great-until-it-isnt)

---

## 6️⃣ 차이점 비교 (RLS vs 애플리케이션 레벨 인가)

### 📊 비교 매트릭스

| 비교 기준    | 🛡️ RLS (DB 레벨)            | 🧑‍💻 App-Level 인가              |
| ----------- | -------------------------- | ------------------------------ |
| **강제 위치** | 데이터베이스 엔진 내부        | 앱 코드 (미들웨어, 가드)          |
| **누수 위험** | 낮음 (접근 경로 무관)        | 높음 (체크 누락 시 누수)          |
| **표현력**   | 행 필터에 강함, 복잡 로직 약함 | 임의 로직 자유 (시간/속성 기반 등) |
| **성능 제어** | 쿼리 플래너에 의존, 튜닝 필요  | 앱에서 직접 제어                 |
| **디버깅**   | 어려움 (숨은 필터)           | 쉬움 (코드에 보임)               |
| **버전 관리** | DB 마이그레이션 필요         | Git에서 자연스럽게 추적           |

### 🔍 핵심 차이 요약

```
RLS (DB 레벨)                  App-Level 인가
──────────────────     vs     ──────────────────
어디서 접근하든 강제            엔드포인트 누락 시 구멍
보안은 새지 않음               유연한 복잡 로직 가능
숨은 WHERE → 디버깅 ↑          코드에 보여 디버깅 ↓
```

### 🤔 언제 무엇을 선택?

- **RLS를 선택** → 멀티테넌트 격리, BaaS(브라우저 직접 접근), "절대 새면 안 되는" 데이터 경계
- **App-Level을 선택** → 시간/위치/속성 기반의 정교한 권한, 복잡한 워크플로우 인가
- 💡 **정답은 "둘 다(both)"**: Supabase 권고처럼 RLS를 **최후 방어선**으로 깔고, 앱 레벨에서 UX/복잡 로직을 처리하는 **Defense in Depth** 조합이 실무 표준입니다 — [Supabase](https://supabase.com/features/row-level-security)

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions) — 🚨 가장 중요한 섹션

### ⚠️ 흔한 실수 (Common Footguns)

| # | 실수                              | 왜 문제인가                                          | 올바른 접근                                          |
| - | -------------------------------- | --------------------------------------------------- | -------------------------------------------------- |
| 1 | **테이블 소유자로 접속**           | 소유자는 기본적으로 RLS를 **우회** → 정책이 무효         | `ALTER TABLE ... FORCE ROW LEVEL SECURITY` 또는 별도 앱 역할로 접속 |
| 2 | **`SET` 사용 (`SET LOCAL` 대신)** | 커넥션 풀에서 다음 사용자가 컨텍스트 상속 → **테넌트 누수** | 트랜잭션 내 `SET LOCAL` 만 사용                       |
| 3 | **`BYPASSRLS`/superuser 역할 사용** | RLS를 통째로 무시                                    | 앱 역할에 `BYPASSRLS`/`SUPERUSER` 절대 부여 금지       |
| 4 | **`WITH CHECK` 생략·오설계**      | "볼 수 없는데 INSERT는 되는" 상황 발생                  | 읽기/쓰기 정책을 명시적으로 분리 설계                  |
| 5 | **VIEW로 우회**                   | VIEW는 기본 `SECURITY DEFINER` → 생성자 권한으로 RLS 우회 | `security_invoker=true` (PG15+) 또는 VIEW 소유자 점검 |

### 🚫 Anti-Patterns

1. **행마다 함수 호출**: `USING (slow_function(row.col))` → 행 수만큼 함수 실행. PostgreSQL 함수는 느려서 N행이면 N번 호출되어 쿼리가 폭발 — [Scott Pierce](https://scottpierce.dev/posts/optimizing-postgres-rls/)
2. **non-LEAKPROOF 함수**: 인덱스를 못 쓰게 막아 **풀스캔** 유발 → 치명적 성능 저하 — [Bytebase footguns](https://www.bytebase.com/blog/postgres-row-level-security-footguns/)
3. **정책을 RLS만 믿고 rate limit 없음**: 악의적 사용자는 데이터는 못 봐도 **쿼리 자체는 계속 실행** → CPU 낭비/정직한 사용자 starvation — [PlanetScale](https://planetscale.com/blog/rls-sounds-great-until-it-isnt)

### ⚡ 성능 최적화 패턴 — SELECT Wrapper

함수를 행마다 호출하지 않고 **쿼리당 1회만** 평가하도록 서브쿼리로 감쌉니다.

```sql
-- ❌ 느림: 10,000행이면 서브쿼리 10,000번 (~450ms)
CREATE POLICY slow ON documents FOR SELECT
USING (
  EXISTS (SELECT 1 FROM team_members
          WHERE team_id = documents.team_id AND user_id = auth.uid())
);

-- ✅ 빠름: STABLE 함수를 SELECT로 감싸 쿼리당 1회 (~45ms, 10배 ↑)
CREATE OR REPLACE FUNCTION user_team_ids()
RETURNS SETOF uuid LANGUAGE sql SECURITY DEFINER STABLE AS $$
  SELECT team_id FROM team_members WHERE user_id = auth.uid();
$$;

CREATE POLICY fast ON documents FOR SELECT
USING (team_id IN (SELECT user_team_ids()));   -- ◄ SELECT wrapper

-- 정책 컬럼에 인덱스 필수
CREATE INDEX ON documents (team_id);
CREATE INDEX ON team_members (user_id, team_id);
```

출처: [SupaExplorer 성능 가이드](https://supaexplorer.com/best-practices/supabase-postgres/security-rls-performance/)

### 🔒 보안/성능 고려사항

- 🔒 **소유자/superuser 우회**는 RLS의 가장 흔한 사고 원인 — 반드시 `FORCE` + 전용 앱 역할
- ⚡ **정책 컬럼 인덱싱 + SELECT wrapper**로 대부분의 성능 문제 해결
- 🔍 RLS는 **행 단위**라서 **컬럼 단위 보안(column-level)**은 별도 처리 필요 (`GRANT`/뷰)

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형        | 이름                          | 링크/설명                                                                 |
| ----------- | ---------------------------- | ------------------------------------------------------------------------ |
| 📖 공식 문서 | PostgreSQL 5.9 Row Security Policies | [postgresql.org](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) — 1차 출처, 필독 |
| 📖 공식 문서 | CREATE POLICY 레퍼런스        | [postgresql.org](https://www.postgresql.org/docs/current/sql-createpolicy.html) — 문법 전체 |
| 📘 가이드    | Supabase RLS Guide           | [supabase.com](https://supabase.com/docs/guides/database/postgres/row-level-security) — 실전 패턴 풍부 |
| 📘 블로그    | Crunchy Data: RLS for Tenants | [crunchydata.com](https://www.crunchydata.com/blog/row-level-security-for-tenants-in-postgres) — 멀티테넌트 |
| 📺 실전      | Bytebase Footguns            | [bytebase.com](https://www.bytebase.com/blog/postgres-row-level-security-footguns/) — 함정 모음 |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리 | 언어/플랫폼 | 용도                                       |
| ------------- | ---------- | ----------------------------------------- |
| **Supabase**  | BaaS       | RLS 기반 인가를 제품 핵심으로 채택            |
| **PostgREST** | API        | RLS와 JWT 클레임 연동해 자동 REST API         |
| **psql `\d+`** | CLI        | `pg_policies` 뷰로 정책 조회/감사            |
| **Bytebase**  | DB 관리    | 정책 버전 관리·리뷰 (정책 code drift 보완)    |

### 🔮 트렌드 & 전망

- BaaS(Supabase) 부상으로 RLS가 **"브라우저→DB 직접 접근"** 시대의 핵심 인가 메커니즘으로 재조명
- PG15의 `security_invoker` 뷰 옵션 등 **RLS 우회 함정을 줄이는 방향**으로 개선 중
- 복잡한 권한은 RLS 단독보다 **외부 인가 엔진(OPA, Permit.io 등)과 병행**하는 추세 — [Permit.io](https://www.permit.io/blog/postgres-rls-implementation-guide)

### 💬 커뮤니티 인사이트

- 🗣️ "RLS는 정말 좋아 보이지만, **테스트와 스케일링**이 거의 불가능해진다" — 정책이 코드가 아니라 DB에 살아 **code drift**가 생기고, 마이그레이션이 조용히 정책을 깨뜨릴 수 있다는 실무 경고 — [PlanetScale](https://planetscale.com/blog/rls-sounds-great-until-it-isnt)
- 🗣️ 실무자들이 입을 모으는 1순위 사고: **테이블 소유자로 접속해서 정책이 통째로 무시되는 것** → 개발 환경에선 통과하다 운영에서 터지는 패턴 주의

---

## 📎 Sources

1. [PostgreSQL Documentation: 5.9 Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) — 공식 문서
2. [PostgreSQL Documentation: CREATE POLICY](https://www.postgresql.org/docs/current/sql-createpolicy.html) — 공식 문서
3. [Supabase Docs: Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security) — 공식/제품 문서
4. [Supabase Features: Authorization via RLS](https://supabase.com/features/row-level-security) — 제품 문서
5. [AWS: Multi-tenant data isolation with PostgreSQL RLS](https://aws.amazon.com/blogs/database/multi-tenant-data-isolation-with-postgresql-row-level-security/) — 공식 블로그
6. [AWS Prescriptive Guidance: RLS recommendations](https://docs.aws.amazon.com/prescriptive-guidance/latest/saas-multitenant-managed-postgresql/rls.html) — 공식 가이드
7. [Crunchy Data: Row Level Security for Tenants](https://www.crunchydata.com/blog/row-level-security-for-tenants-in-postgres) — 기술 블로그
8. [Bytebase: Postgres RLS Footguns](https://www.bytebase.com/blog/postgres-row-level-security-footguns/) — 기술 블로그
9. [Bytebase: RLS Limitations and Alternatives](https://www.bytebase.com/blog/postgres-row-level-security-limitations-and-alternatives/) — 기술 블로그
10. [PlanetScale: RLS sounds great until it isn't](https://planetscale.com/blog/rls-sounds-great-until-it-isnt) — 기술 블로그(비판적 관점)
11. [SupaExplorer: Optimize RLS Policies for Performance](https://supaexplorer.com/best-practices/supabase-postgres/security-rls-performance/) — 기술 블로그
12. [The Nile: Multi-tenant SaaS using Postgres RLS](https://www.thenile.dev/blog/multi-tenant-rls) — 기술 블로그
13. [Scott Pierce: Optimizing Postgres RLS](https://scottpierce.dev/posts/optimizing-postgres-rls/) — 기술 블로그
14. [Permit.io: Postgres RLS Implementation Guide](https://www.permit.io/blog/postgres-rls-implementation-guide) — 기술 블로그

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 7 (6 성공, 1 Reddit 무결과)
> - 수집 출처 수: 14
> - 출처 유형: 공식 6, 기술 블로그 8, 커뮤니티/SNS 0 (Reddit 검색 무결과 — 대신 PlanetScale의 비판적 실무 관점으로 contrarian 시각 보강)

---

## 🎓 한눈에 정리 (성장 포인트)

PostgreSQL RLS를 처음 배우는 입장에서 **딱 3가지**만 기억하세요:

1. **"테이블에 잠금장치를 단다"** → 쿼리마다가 아니라 테이블마다. 그래서 한 곳만 고치면 전부 적용 🔐
2. **`USING`(읽기) vs `WITH CHECK`(쓰기)** → 이 둘을 헷갈리면 "못 보는데 넣을 수 있는" 구멍이 생김 👀✍️
3. **소유자/superuser는 우회한다** → `FORCE ROW LEVEL SECURITY` + 전용 앱 역할이 없으면 개발에선 멀쩡하다 운영에서 터진다 🚨
