---
created: 2026-02-03
source: claude-code
tags:
  - database
  - cardinality
  - indexing
  - query-optimization
---

# 📖 카디널리티 (Cardinality) — Concept Deep Dive

> 💡 **한줄 요약**: 카디널리티는 컬럼 내 **고유 값(distinct values)의 수**를 의미하며, 인덱스 설계와 쿼리 옵티마이저의 실행 계획 선택에 결정적 영향을 미치는 지표이다.

---

## 1️⃣ 무엇인가? (What is it?)

카디널리티(Cardinality)는 원래 수학에서 **집합의 원소 개수**를 뜻하는 용어로, 데이터베이스에서는 **특정 컬럼에 존재하는 고유 값의 수**를 의미한다.

- 100만 행 테이블의 `user_id` 컬럼에 100만 개의 고유 값 → **High Cardinality**
- 100만 행 테이블의 `gender` 컬럼에 3개의 고유 값 → **Low Cardinality**

이 개념이 중요한 이유는 **인덱스의 효율성**이 카디널리티에 직접적으로 좌우되기 때문이다. 카디널리티가 높을수록 인덱스의 **선택도(Selectivity)**가 높아져 검색 범위를 크게 줄일 수 있고, 낮을수록 인덱스가 거의 도움이 되지 않는다.

> 📌 **핵심 키워드**: `Cardinality`, `Selectivity`, `Index Efficiency`, `Query Optimizer`

---

## 2️⃣ 핵심 개념 (Core Concepts)

```
┌─────────────────────────────────────────────────────────────┐
│                  카디널리티 스펙트럼                           │
│                                                             │
│  Low                    Normal                    High      │
│  ◄──────────────────────────────────────────────────►       │
│                                                             │
│  gender (M/F)      department (50)       email (unique)     │
│  boolean (T/F)     category (100)        user_id (unique)   │
│  status (3~5)      city (1,000)          UUID (unique)      │
│                                                             │
│  고유 값: 2~10      고유 값: 수십~수천     고유 값 ≈ 행 수     │
│  선택도: 낮음        선택도: 중간           선택도: 높음        │
│  인덱스: ⚠️          인덱스: ✅             인덱스: ✅          │
└─────────────────────────────────────────────────────────────┘
```

| 구성 요소       | 역할        | 설명                                              |
| --------------- | ----------- | ------------------------------------------------- |
| **Cardinality** | 고유 값의 수 | 컬럼 내 distinct value 개수                        |
| **Selectivity** | 선택도       | `카디널리티 / 전체 행 수`. 1에 가까울수록 선택적     |
| **Density**     | 밀도         | `1 / 카디널리티`. 낮을수록 인덱스에 유리             |
| **Distribution** | 분포        | 값이 균등한지 편향(skewed)되었는지                   |

### 📌 카디널리티 vs 선택도

카디널리티가 높아도 **선택도가 낮을 수 있다**. 핵심은 **상대적** 수치이다.

```
테이블: 1,000,000 행

컬럼 A: 고유 값 500,000개 → 선택도 = 0.5   (높음 ✅)
컬럼 B: 고유 값 10개       → 선택도 = 0.00001 (낮음 ❌)
컬럼 C: 고유 값 1,000,000  → 선택도 = 1.0   (최고 ✅)
```

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

### 🏗️ Query Optimizer에서의 카디널리티

```
┌──────────────────────────────────────────────────────┐
│                Query Optimizer 흐름                    │
│                                                      │
│  SQL Query                                           │
│    │                                                 │
│    ▼                                                 │
│  ┌──────────────┐                                    │
│  │   Parser      │ → 구문 분석                        │
│  └──────┬───────┘                                    │
│         ▼                                            │
│  ┌──────────────────┐    ┌───────────────────┐       │
│  │ Cardinality      │◄───│ Statistics        │       │
│  │ Estimator (CE)   │    │ (히스토그램, 통계)  │       │
│  └──────┬───────────┘    └───────────────────┘       │
│         │ "이 WHERE 조건으로 몇 행이 나올까?"           │
│         ▼                                            │
│  ┌──────────────┐                                    │
│  │  Cost Model   │ → CE 결과로 각 플랜 비용 산출       │
│  └──────┬───────┘                                    │
│         ▼                                            │
│  ┌──────────────┐                                    │
│  │ Plan Selector │ → 최저 비용 실행 계획 선택          │
│  └──────────────┘                                    │
│         │                                            │
│         ▼                                            │
│  Index Scan? Full Table Scan? Bitmap Scan?            │
└──────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (Step by Step)

1. **통계 수집**: DB가 각 컬럼의 카디널리티, 히스토그램, NULL 비율 등을 수집/갱신
2. **카디널리티 추정**: `WHERE status = 'active'`일 때 결과 행 수를 추정. 카디널리티가 낮은 컬럼이면 많은 행이 매칭된다고 추정
3. **비용 계산**: 추정 행 수를 기반으로 Index Scan vs Full Table Scan의 I/O 비용 비교
4. **실행 계획 선택**: 비용이 낮은 방식 선택. **카디널리티가 낮은 컬럼의 인덱스는 옵티마이저가 무시**할 수 있음

```sql
-- 옵티마이저의 판단 예시
SELECT * FROM users WHERE gender = 'M';
-- gender 카디널리티 = 2 → 전체의 ~50% 매칭
-- → Index Scan보다 Full Table Scan이 빠르다고 판단

SELECT * FROM users WHERE email = 'user@example.com';
-- email 카디널리티 ≈ 행 수 → 1행만 매칭
-- → Index Scan 선택
```

### ⚡ Vector DB에서의 카디널리티

Vector DB(Qdrant 등)도 메타데이터 필터의 카디널리티를 추정하여 검색 전략을 결정한다:

```
필터 카디널리티 추정
        │
        ├── High (약한 필터, 많은 결과) → HNSW 그래프 탐색 + 필터
        │
        ├── Mid (중간)                → Filterable HNSW (추가 엣지)
        │
        └── Low (강한 필터, 적은 결과) → Payload Index 검색 + 전체 rescore
```

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| #   | 유즈 케이스                         | 카디널리티      | 인덱스 전략                      |
| --- | ----------------------------------- | --------------- | -------------------------------- |
| 1   | Primary Key 조회 (`user_id`)        | 최고 (Unique)   | B-Tree ✅                        |
| 2   | 이메일/전화번호 검색                  | 높음            | B-Tree ✅                        |
| 3   | 부서/카테고리 필터링 (수십~수백)       | 중간            | B-Tree ✅ (복합 인덱스 권장)       |
| 4   | 상태 필터 (`active/inactive`)        | 낮음            | Bitmap ⚠️ 또는 복합 인덱스        |
| 5   | Boolean 플래그 (`is_deleted`)        | 최저 (2)        | Partial Index 권장                |

### ✅ 베스트 프랙티스

1. **쿼리 패턴 우선**: 카디널리티만 보지 말고 **실제 WHERE 절에서 얼마나 자주 쓰이는지**가 기준
2. **편향 분포 주의**: `status` 컬럼이 99% `active`, 1% `inactive`라면 `inactive` 검색에는 인덱스가 효과적이지만 `active` 검색에는 무의미
3. **복합 인덱스 활용**: 단독으로 카디널리티가 낮은 컬럼도 다른 컬럼과 조합하면 높아짐
4. **통계 최신화**: `ANALYZE` (PostgreSQL) / `UPDATE STATISTICS` (SQL Server)를 주기적으로 실행
5. **Partial Index**: 특정 값만 인덱싱 (예: `WHERE is_deleted = false`)

```sql
-- ❌ 카디널리티 2인 컬럼 단독 인덱스
CREATE INDEX idx_gender ON users(gender);

-- ✅ 복합 인덱스로 카디널리티 높이기
CREATE INDEX idx_gender_created ON users(gender, created_at);

-- ✅ Partial Index로 필요한 값만 인덱싱
CREATE INDEX idx_active_users ON users(created_at)
WHERE status = 'active';
```

### 🏢 실제 적용 사례

- **Qdrant**: 메타데이터 필터의 카디널리티를 추정하여 HNSW vs Payload Index 검색 전략을 자동 전환 ([Qdrant 문서](https://qdrant.tech/articles/vector-search-filtering/))
- **Pinecone**: High-cardinality 메타데이터가 pod 메모리를 과도하게 소비하므로 Selective Metadata Indexing 지원 ([Pinecone 문서](https://docs.pinecone.io/guides/data/filter-with-metadata))
- **Oracle**: B-Tree와 Bitmap 인덱스를 카디널리티에 따라 구분 사용하는 대표적 DB

---

## 5️⃣ 장점과 단점 (Pros & Cons)

### High Cardinality 인덱스

| 구분      | 항목              | 설명                                                    |
| --------- | ----------------- | ------------------------------------------------------- |
| ✅ 장점   | 높은 선택도        | 검색 범위를 극적으로 줄여 빠른 조회                        |
| ✅ 장점   | 옵티마이저 활용    | 쿼리 옵티마이저가 적극적으로 인덱스 선택                   |
| ✅ 장점   | 정확한 비용 추정   | 카디널리티 추정 오차가 적음                                |
| ❌ 단점   | 큰 인덱스 크기     | 고유 값이 많아 인덱스 자체가 테이블만큼 커질 수 있음        |
| ❌ 단점   | Write 부하         | INSERT/UPDATE마다 인덱스 갱신 비용                        |
| ❌ 단점   | 통계 불안정        | 값이 계속 추가되면 통계가 빠르게 outdated                  |

### Low Cardinality 인덱스

| 구분      | 항목                       | 설명                                    |
| --------- | -------------------------- | --------------------------------------- |
| ✅ 장점   | 작은 인덱스 크기 (Bitmap)   | 비트맵은 매우 공간 효율적                 |
| ✅ 장점   | AND/OR 연산 최적화          | 비트맵 간 Boolean 연산이 극도로 빠름       |
| ❌ 단점   | 낮은 선택도                 | 검색 범위를 충분히 줄이지 못함             |
| ❌ 단점   | 옵티마이저 무시             | Full Table Scan이 더 빠르다고 판단 가능    |
| ❌ 단점   | 동시 쓰기 취약 (Bitmap)     | 비트맵 인덱스는 OLTP에 부적합              |

### ⚖️ Trade-off 분석

```
High Cardinality   ◄──── Trade-off ────►   Low Cardinality
빠른 조회(선택도↑)  ◄─────────────────────►  느린 조회(선택도↓)
큰 인덱스 크기      ◄─────────────────────►  작은 인덱스 크기
Write 부하 높음     ◄─────────────────────►  Write 부하 낮음 (B-Tree)
B-Tree 최적        ◄─────────────────────►  Bitmap 최적 (OLAP)
```

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 인덱스 타입별 카디널리티 적합성

| 비교 기준           | B-Tree Index     | Bitmap Index        | Inverted Index         | Partial Index      |
| ------------------- | ---------------- | ------------------- | ---------------------- | ------------------ |
| 적합한 카디널리티    | 중~높음           | 낮음                 | 텍스트/태그 (다양)      | 편향 분포           |
| 주 용도             | OLTP 일반 조회    | OLAP 분석 쿼리       | 전문 검색, 태그 필터    | 특정 값 빈번 조회    |
| Write 성능          | 중간              | 나쁨 (동시성↓)       | 중간                   | 좋음 (일부만 갱신)   |
| Read 성능           | 카디널리티에 비례  | AND/OR 연산 우수      | 키워드 매칭 우수        | 매우 빠름           |
| 공간 효율           | 중간              | 높음 (압축)           | 중간                   | 높음 (부분만 저장)   |
| 대표 DB             | PostgreSQL, MySQL | Oracle, ClickHouse   | Elasticsearch, Qdrant  | PostgreSQL          |

### 🔍 RDB vs Vector DB 카디널리티 활용 비교

```
RDB                                  Vector DB
──────────────────────        ──────────────────────
카디널리티로 인덱스 설계          카디널리티로 검색 전략 전환
B-Tree / Bitmap 선택             HNSW / Payload Index 선택
옵티마이저가 자동 판단            필터 카디널리티 추정 후 전략 결정
통계 기반 (히스토그램)            실시간 추정
인덱스 안 쓰면 Full Scan         인덱스 없으면 정확한 추정 불가
```

### 🤔 언제 무엇을 선택?

- **B-Tree** → 카디널리티 중~높음, OLTP 워크로드, 범위 검색 필요 시
- **Bitmap** → 카디널리티 낮음, OLAP/분석 워크로드, 복합 AND/OR 필터 시
- **Partial Index** → 분포가 편향되어 특정 값만 자주 검색 시
- **복합 인덱스** → 단독 카디널리티는 낮지만 조합하면 높아지는 경우

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| #   | 실수                                    | 왜 문제인가                                             | 올바른 접근                                       |
| --- | --------------------------------------- | ------------------------------------------------------- | ------------------------------------------------- |
| 1   | Low Cardinality 컬럼에 B-Tree 인덱스     | 선택도 낮아 옵티마이저가 무시, Write 오버헤드만 증가        | Bitmap, Partial Index, 또는 복합 인덱스 고려        |
| 2   | 모든 컬럼에 인덱스                        | Write 성능 저하, 스토리지 낭비                             | 쿼리 패턴 기반으로 3~5개만 선택                      |
| 3   | 카디널리티만 보고 판단                     | 분포(skew)를 무시하면 잘못된 결론                          | 선택도 + 분포 + 쿼리 빈도 종합 고려                  |
| 4   | 통계 갱신 안 함                           | 옵티마이저가 오래된 카디널리티로 잘못된 플랜 선택            | 주기적 `ANALYZE` 실행                               |
| 5   | Vector DB에서 payload index 미생성        | 카디널리티 추정 불가 → 비최적 검색 전략                     | 필터링할 필드에 payload index 생성                   |

### 🚫 Anti-Patterns

1. **"인덱스가 많을수록 좋다"**: 카디널리티 낮은 컬럼에 무분별한 인덱스는 Write 성능만 저하시킴
2. **"Boolean 컬럼에 인덱스"**: `is_active = true`가 99%라면 인덱스가 있어도 Full Scan. 대신 `WHERE is_active = false`에 대한 Partial Index가 효과적
3. **"카디널리티 추정 = 정확"**: 실제 데이터 분포는 균등하지 않으며, 옵티마이저의 **독립성 가정(independence assumption)**이 틀릴 수 있음. Multi-join 쿼리에서 추정 오차가 기하급수적으로 증폭됨

### 🔒 보안/성능 고려사항

- ⚡ **카디널리티 추정 오차**: Cost Model 오차는 최대 30%이지만, 카디널리티 추정 오차는 **수 자릿수(orders of magnitude)** 까지 발생 가능 ([VLDB 연구](https://www.vldb.org/pvldb/vol9/p204-leis.pdf))
- ⚡ **Vector DB 메모리**: Pinecone Pod에서 High-cardinality 메타데이터는 메모리를 과도하게 소비하여 저장 가능한 벡터 수가 감소

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형        | 이름                                       | 링크/설명                                                                                                                                        |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| 📖 공식 문서 | MySQL Index Cardinality                    | [MySQL Tutorial](https://www.mysqltutorial.org/mysql-index/mysql-index-cardinality/)                                                             |
| 📖 공식 문서 | SQL Server Cardinality Estimation          | [Microsoft Learn](https://learn.microsoft.com/en-us/sql/relational-databases/performance/cardinality-estimation-sql-server)                       |
| 🎓 강의     | MySQL for Developers - Index Selectivity   | [PlanetScale](https://planetscale.com/learn/courses/mysql-for-developers/indexes/index-selectivity)                                               |
| 📖 튜토리얼 | Understanding Cardinality and Selectivity  | [Couchbase](https://developer.couchbase.com/tutorial-understanding-cardinality-and-selectivity/)                                                  |
| 📘 논문     | How Good Are Query Optimizers, Really?     | [Leis et al., VLDB](https://www.vldb.org/pvldb/vol9/p204-leis.pdf)                                                                               |
| 📘 논문     | Cardinality Estimation Benchmark           | [Zhu et al., VLDB](https://www.vldb.org/pvldb/vol15/p752-zhu.pdf)                                                                                |

### 🛠️ 관련 도구 & 명령어

| 도구/명령                | DB         | 용도                               |
| ------------------------ | ---------- | ---------------------------------- |
| `SHOW INDEX FROM table`  | MySQL      | 인덱스 카디널리티 확인               |
| `ANALYZE TABLE`          | MySQL      | 통계 갱신                           |
| `ANALYZE`                | PostgreSQL | 통계 수집                           |
| `pg_stats.n_distinct`    | PostgreSQL | 컬럼별 카디널리티 조회               |
| `DBCC SHOW_STATISTICS`   | SQL Server | 카디널리티 통계 확인                 |
| `EXPLAIN ANALYZE`        | PostgreSQL/MySQL | 실행 계획에서 추정 vs 실제 행 수 비교 |

### 🔮 트렌드 & 전망

- **ML 기반 카디널리티 추정**: 전통적 히스토그램 대신 딥러닝으로 데이터 분포를 학습하여 추정 정확도 향상 ([arXiv Survey](https://arxiv.org/abs/2101.01507))
- **SQL Server CE Feedback**: 런타임 피드백으로 카디널리티 모델을 자동 보정하는 적응형 접근 ([Microsoft](https://learn.microsoft.com/en-us/sql/relational-databases/performance/intelligent-query-processing-cardinality-estimation-feedback))
- **Vector DB 자동 전략 전환**: Qdrant처럼 필터 카디널리티를 실시간 추정하여 검색 알고리즘을 자동 전환하는 방식이 표준이 되는 추세

### 💬 커뮤니티 인사이트

- "Bitmap 인덱스는 low cardinality 전용"이라는 통념은 **myth**에 가깝다. Oracle 전문가 Richard Foote는 "카디널리티가 10,000인 컬럼의 Bitmap이 카디널리티 4인 컬럼보다 작을 수 있다"고 지적 ([Richard Foote's Blog](https://richardfoote.wordpress.com/2010/03/03/1196/))
- PostgreSQL은 네이티브 Bitmap Index가 없지만, B-Tree 인덱스로부터 **in-memory bitmap을 자동 구성**하여 유사한 효과를 달성

---

## 📎 Sources

1. [What Is Cardinality In Databases — Netdata](https://www.netdata.cloud/academy/what-is-cardinality-in-databases-a-comprehensive-guide/) — 종합 가이드
2. [MySQL Index Cardinality — MySQL Tutorial](https://www.mysqltutorial.org/mysql-index/mysql-index-cardinality/) — 공식 문서
3. [Index Selectivity — PlanetScale](https://planetscale.com/learn/courses/mysql-for-developers/indexes/index-selectivity) — 강의
4. [Understanding Cardinality and Selectivity — Couchbase](https://developer.couchbase.com/tutorial-understanding-cardinality-and-selectivity/) — 튜토리얼
5. [Vector Search Filtering — Qdrant](https://qdrant.tech/articles/vector-search-filtering/) — Vector DB 필터링 전략
6. [Filter with Metadata — Pinecone](https://docs.pinecone.io/guides/data/filter-with-metadata) — Vector DB 메타데이터 인덱싱
7. [How Good Are Query Optimizers, Really? — Leis et al.](https://www.vldb.org/pvldb/vol9/p204-leis.pdf) — VLDB 논문
8. [Cardinality Estimation in DBMS — Zhu et al.](https://www.vldb.org/pvldb/vol15/p752-zhu.pdf) — VLDB 벤치마크 논문
9. [Bitmap Index vs B-tree Index — Oracle](https://www.oracle.com/technical-resources/articles/sharma-indexes.html) — 인덱스 비교
10. [Myth: Bitmap Indexes With High Distinct Columns — Richard Foote](https://richardfoote.wordpress.com/2010/03/03/1196/) — 커뮤니티 인사이트
11. [High vs Low Cardinality — Last9](https://last9.io/blog/high-vs-low-cardinality/) — Observability 관점

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 6
> - 수집 출처 수: 11
> - 출처 유형: 공식 문서 3, 블로그/튜토리얼 4, 논문 2, 커뮤니티 2
