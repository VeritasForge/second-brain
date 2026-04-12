---
created: 2026-02-20
source: claude-code
tags:
  - sqlite
  - database
  - embedded-db
  - slack-sticker-bot
---

# 📖 SQLite — Concept Deep Dive

> 💡 **한줄 요약**: SQLite는 별도 서버 없이 **파일 하나에 전체 DB를 담는** 임베디드 관계형 데이터베이스이며, 우리 스티커 봇에서는 스티커 메타데이터(이름, 생성자, 파일 경로 등)를 저장하는 용도로 사용합니다.

---

## 1️⃣ 무엇인가? (What is it?)

SQLite는 **서버가 필요 없는(serverless) 임베디드 SQL 데이터베이스 엔진**입니다. MySQL이나 PostgreSQL처럼 별도 프로세스로 돌아가는 게 아니라, 앱 프로세스 안에 **라이브러리로 내장**되어 디스크의 단일 파일을 직접 읽고 씁니다.

- 2000년 D. Richard Hipp이 미 해군 구축함의 소프트웨어용으로 개발
- 현재 세계에서 **가장 많이 배포된 DB 엔진** (모든 스마트폰, 브라우저, OS에 내장)
- 별도 설치/설정이 필요 없어 **zero-configuration**으로 즉시 사용 가능

> 📌 **핵심 키워드**: `embedded`, `serverless`, `single-file`, `zero-config`, `ACID`

---

## 2️⃣ 핵심 개념 (Core Concepts)

```
┌─────────────────────────────────────────────┐
│              SQLite 내부 구조                 │
├─────────────────────────────────────────────┤
│                                             │
│   SQL Text                                  │
│     │                                       │
│     ▼                                       │
│   ┌──────────┐   ┌────────┐   ┌─────────┐  │
│   │Tokenizer │──▶│ Parser │──▶│Code Gen │  │
│   └──────────┘   └────────┘   └────┬────┘  │
│                                     │       │
│                                     ▼       │
│                              ┌──────────┐   │
│                              │  VM      │   │
│                              │(bytecode)│   │
│                              └────┬─────┘   │
│                                   │         │
│   ┌──────────┐   ┌────────┐   ┌──▼──────┐  │
│   │OS Layer  │◀──│ Pager  │◀──│ B-Tree  │  │
│   └──────────┘   └────────┘   └─────────┘  │
│        │                                    │
│        ▼                                    │
│   📄 stickers.db (단일 파일)                 │
│                                             │
└─────────────────────────────────────────────┘
```

| 구성 요소          | 역할       | 설명                                         |
| ------------------ | ---------- | -------------------------------------------- |
| **Tokenizer + Parser** | SQL 해석   | SQL 문자열을 구문 트리로 변환                |
| **Code Generator** | 컴파일     | 구문 트리를 바이트코드로 변환                |
| **Virtual Machine** | 실행       | 바이트코드를 실행하여 결과 반환              |
| **B-Tree**         | 저장 구조  | 테이블/인덱스를 B-트리로 관리                |
| **Pager**          | 페이지 캐시 | 디스크 I/O를 4KB 페이지 단위로 처리, 트랜잭션/롤백 담당 |
| **OS Layer**       | 파일 접근  | 운영체제별 파일 시스템 추상화                |

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

### 🏗️ 스티커 봇에서의 SQLite 구조

```
┌────────────────────────────────────────────┐
│            Bolt App (Node.js)               │
│                                            │
│  StickerService                            │
│    │                                       │
│    ├─ register("happy_cat", "U123", ...)   │
│    ├─ search("happy")                      │
│    ├─ delete(sticker_id)                   │
│    └─ rename(sticker_id, "new_name")       │
│         │                                  │
│         ▼                                  │
│  ┌─────────────────┐                      │
│  │  better-sqlite3  │ ← Node.js 라이브러리 │
│  │  (동기식, 빠름)   │                      │
│  └────────┬────────┘                      │
│           │                                │
└───────────┼────────────────────────────────┘
            │
            ▼
    📄 /data/db/stickers.db
    ┌──────────────────────────────────┐
    │ stickers 테이블                   │
    │ ┌────┬────────────┬───────────┐  │
    │ │ id │ name       │ created_by│  │
    │ ├────┼────────────┼───────────┤  │
    │ │ 1  │ happy_cat  │ U123ABC   │  │
    │ │ 2  │ sad_dog    │ U456DEF   │  │
    │ └────┴────────────┴───────────┘  │
    └──────────────────────────────────┘
```

### 🔄 동작 흐름 (스티커 검색 예시)

1. **사용자**: `/sticker search happy` 입력
2. **Bolt Handler**: StickerService.search("happy") 호출
3. **better-sqlite3**: `SELECT * FROM stickers WHERE name LIKE '%happy%'` 실행
4. **SQLite 엔진**: B-Tree에서 인덱스 탐색 → 결과 반환
5. **Bolt Handler**: 결과를 Block Kit 메시지로 포맷 → 에피머럴 응답

### 💻 스키마 예시

```sql
CREATE TABLE stickers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  file_path TEXT NOT NULL,
  created_by TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_stickers_name ON stickers(name);
```

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| #   | 유즈 케이스              | 설명                          | 적합한 이유                      |
| --- | ------------------------ | ----------------------------- | -------------------------------- |
| 1   | **Slack 봇 메타데이터**  | 스티커 이름, 경로, 생성자 저장 | 단일 프로세스, 낮은 동시성       |
| 2   | 모바일 앱 로컬 DB        | Android/iOS 앱 데이터 저장     | 서버 불필요, 앱에 내장           |
| 3   | IoT 디바이스             | 센서 데이터 로컬 저장          | 경량, 리소스 효율적              |
| 4   | 개발/테스트 환경         | 프로토타입 빠른 구현           | 설정 0초, 즉시 사용              |

### ✅ 베스트 프랙티스

1. **WAL 모드 활성화**: `PRAGMA journal_mode=WAL` → 읽기/쓰기 동시성 개선
2. **better-sqlite3 사용**: Node.js에서 동기식 API로 10배 빠른 성능
3. **인덱스 설계**: 검색 대상 컬럼(name)에 반드시 인덱스 생성

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분      | 항목             | 설명                                                                |
| --------- | ---------------- | ------------------------------------------------------------------- |
| ✅ 장점   | **제로 설정**    | 별도 서버 설치/설정 불필요. Docker에 DB 컨테이너 추가 안 해도 됨    |
| ✅ 장점   | **단일 파일**    | stickers.db 파일 하나로 백업/이동/복사 가능                         |
| ✅ 장점   | **빠름**         | 네트워크 왕복 없이 직접 파일 접근. 소규모 쿼리에서 PostgreSQL보다 빠름 |
| ✅ 장점   | **안정성**       | ACID 트랜잭션 완전 지원. 20년+ 검증된 엔진                         |
| ❌ 단점   | **동시 쓰기 제한** | 한 번에 하나의 쓰기만 가능 (읽기는 동시 가능)                      |
| ❌ 단점   | **수평 확장 불가** | 서버 여러 대에서 같은 DB 공유 불가                                 |
| ❌ 단점   | **대용량 부적합** | 1TB 이상 데이터에서 성능 저하                                      |

### ⚖️ Trade-off 분석

```
간결함   ◄──────── Trade-off ────────►  확장성
제로설정  ◄─────────────────────────►  동시쓰기 제한
단일파일  ◄─────────────────────────►  분산 불가
```

**스티커 봇에서는?** 스티커 등록은 가끔, 조회가 대부분 → 동시 쓰기 제한이 문제 안 됨. **장점만 취하는 최적의 유즈 케이스**.

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 비교 매트릭스

| 비교 기준          | SQLite        | PostgreSQL          | MySQL            |
| ------------------ | ------------- | ------------------- | ---------------- |
| 서버 필요          | ❌ 불필요     | ✅ 별도 프로세스     | ✅ 별도 프로세스  |
| 설치 복잡도        | 없음          | 중간                | 중간             |
| Docker 컨테이너    | 불필요        | 필요                | 필요             |
| 동시 쓰기          | ⚠️ 1개       | ✅ 수천              | ✅ 수백           |
| 저장 용량 한계     | ~281 TB       | 사실상 무제한       | 사실상 무제한    |
| 스티커 500개 기준  | ⚡ 최적       | 과잉                | 과잉             |
| 백업               | 파일 복사     | pg_dump             | mysqldump        |
| Node.js 라이브러리 | better-sqlite3 | pg                  | mysql2           |

### 🤔 언제 무엇을 선택?

- **SQLite를 선택하세요** → 단일 서버, 낮은 동시성, 간단한 CRUD (우리 스티커 봇)
- **PostgreSQL을 선택하세요** → 복잡한 쿼리, 높은 동시성, 여러 서비스에서 접근
- **MySQL을 선택하세요** → 웹 앱, 중간 규모, AWS RDS로 관리형 사용

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수

| #   | 실수                              | 왜 문제인가                         | 올바른 접근                                  |
| --- | --------------------------------- | ----------------------------------- | -------------------------------------------- |
| 1   | WAL 모드 미활성화                 | 기본 journal 모드는 읽기도 블로킹   | `PRAGMA journal_mode=WAL` 설정               |
| 2   | Node.js에서 `sqlite3` 패키지 사용 | 비동기 콜백 기반, 느림              | `better-sqlite3` 사용 (동기, 10x 빠름)      |
| 3   | DB 파일을 컨테이너 내부에 저장    | 컨테이너 재시작 시 데이터 소실      | Docker volume으로 호스트에 마운트             |

### 🔒 보안/성능 고려사항

- DB 파일 권한을 `600`으로 설정 (소유자만 읽기/쓰기)
- 사용자 입력은 반드시 **prepared statement** 사용 (SQL injection 방지)

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리          | 언어    | 용도                           |
| ------------------------ | ------- | ------------------------------ |
| **better-sqlite3**       | Node.js | 동기식 SQLite 바인딩 (권장)    |
| **Drizzle ORM**          | Node.js | 타입 안전 ORM, SQLite 지원     |
| **DB Browser for SQLite** | GUI     | DB 파일 시각적 탐색/편집       |

### 📚 학습 리소스

| 유형       | 이름                | 링크                                                             |
| ---------- | ------------------- | ---------------------------------------------------------------- |
| 📖 공식 문서 | SQLite 아키텍처      | [sqlite.org/arch.html](https://sqlite.org/arch.html)             |
| 📖 공식 문서 | 적절한 사용 사례     | [sqlite.org/whentouse.html](https://sqlite.org/whentouse.html)   |

---

## 📎 Sources

1. [Architecture of SQLite](https://sqlite.org/arch.html) — 공식 문서
2. [Appropriate Uses For SQLite](https://sqlite.org/whentouse.html) — 공식 문서
3. [SQLite vs MySQL vs PostgreSQL 비교](https://runcloud.io/blog/sqlite-vs-mysql-vs-postgresql) — 기술 블로그
4. [DigitalOcean RDBMS 비교](https://www.digitalocean.com/community/tutorials/sqlite-vs-mysql-vs-postgresql-a-comparison-of-relational-database-management-systems) — 기술 블로그
