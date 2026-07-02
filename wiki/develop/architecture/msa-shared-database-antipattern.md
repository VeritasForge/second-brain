---
tags: [msa, microservices, database, architecture, anti-pattern]
created: 2026-07-03
---

# 📖 MSA(Microservices Architecture)에서의 DB(Database) 공유 패턴 — Concept Deep Dive

> 💡 **한줄 요약**: MS(Microservice, 마이크로서비스)가 하나의 DB를 공유하는 구조는 실제로 존재하지만, 정석 MSA 관점에서는 **안티패턴(Anti-pattern, 잘못된 설계 관행)**으로 분류되며 서비스 간 숨은 결합(Coupling)을 만들어 "분산 모놀리스(Distributed Monolith)"로 전락시킨다.

---

## 1️⃣ 무엇인가? (What is it?)

MSA에서 서비스마다 독립된 DB를 두는 것이 정석(Database per Service, DB 서비스별 분리 패턴)이지만, 실무에서는 **N개의 MS가 물리적으로 같은 DB 인스턴스(또는 같은 스키마)에 접근하는 구조(Shared Database, 공유 DB 패턴)**도 흔히 존재한다.

- **탄생 배경**: 모놀리스(Monolith, 단일 애플리케이션)를 MSA로 쪼갤 때, 서비스 코드는 분리했지만 DB 분리는 뒤로 미루는 경우가 많다. 데이터 마이그레이션 비용, 트랜잭션 복잡도, 조인(Join) 쿼리 문제 때문이다.
- **해결하려던 문제 vs 실제로 만드는 문제**: 초기에는 "빠른 개발 속도"를 위한 타협이지만, MSA가 원래 해결하려던 "서비스 간 독립 배포·독립 스케일링"이라는 목표 자체를 무력화시킨다.

> 📌 **핵심 키워드**: `Shared Database Anti-pattern`, `Database per Service`, `Distributed Monolith`, `Bounded Context`

---

## 2️⃣ 핵심 개념 (Core Concepts)

```
┌─────────────────────────────────────────────┐
│         두 가지 DB 소유 모델 비교              │
├─────────────────────────────────────────────┤
│  A) Database per Service (정석 패턴)          │
│  B) Shared Database (실무 타협/안티패턴)       │
└─────────────────────────────────────────────┘
```

| 구성 요소 | 역할 | 설명 |
| --- | --- | --- |
| **Bounded Context** (DDD, Domain-Driven Design의 경계 컨텍스트) | 서비스가 소유하는 데이터/로직의 경계 | 각 MS는 자신의 Bounded Context에 해당하는 데이터만 소유해야 함 |
| **API 계약(Contract)** | 서비스 간 유일한 통신 창구 | DB를 공유하면 이 계약이 무력화되고 테이블 스키마가 실질적 계약이 되어버림 |
| **스키마 분리(Schema-per-service)** | 물리적 DB는 같아도 스키마/계정을 분리 | 완전한 Shared DB보다는 완화된 절충안 |
| **데이터 소유권(Data Ownership)** | "이 테이블은 누구 것인가" | Shared DB에서는 이 소유권이 모호해짐 |

- 각 MS는 원칙적으로 **자기 데이터의 유일한 쓰기 주체(Single Writer)**여야 한다.
- Shared DB 구조에서는 여러 서비스가 같은 테이블에 직접 쓰기 때문에, 한 서비스의 스키마 변경이 다른 서비스를 깨뜨릴 수 있다.

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

### A) Database per Service (정석)

```
┌───────────┐   ┌───────────┐   ┌───────────┐
│  Order MS │   │  User MS  │   │ Payment MS│
└─────┬─────┘   └─────┬─────┘   └─────┬─────┘
      │               │               │
      ▼               ▼               ▼
  ┌───────┐       ┌───────┐       ┌───────┐
  │Order DB│      │User DB│       │Pay DB │
  └───────┘       └───────┘       └───────┘
  서비스 간 데이터 접근은 반드시 API/이벤트를 통해서만
```

### B) Shared Database (N개 MS가 하나의 DB 공유)

```
┌───────────┐   ┌───────────┐   ┌───────────┐
│  Order MS │   │  User MS  │   │ Payment MS│
└─────┬─────┘   └─────┬─────┘   └─────┬─────┘
      │               │               │
      └───────┬───────┴───────┬───────┘
              ▼               ▼
      ┌──────────────────────────┐
      │      Shared DB (1개)      │
      │  Orders / Users / Payments│
      └──────────────────────────┘
  세 서비스 모두 같은 DB에 직접 SQL 접근 → 숨은 결합 발생
```

### 🔄 왜 이 구조가 생기는가 (Step by Step)

1. **Step 1 (모놀리스→MSA 전환기)**: 코드를 서비스별로 쪼개지만, DB 마이그레이션은 리스크가 커서 뒤로 미룬다.
2. **Step 2 (임시방편)**: 여러 신규 MS가 우선 기존 모놀리스 DB에 붙어서 개발 속도를 확보한다.
3. **Step 3 (점진적 분리, Strangler Fig 패턴)**: 트래픽을 점진적으로 새 서비스로 옮기면서, 듀얼 라이트(Dual Write, 신규 DB와 기존 DB에 동시 쓰기)로 데이터를 이관한다.
4. **Step 4 (완전 분리)**: 각 서비스가 자기 DB로 완전히 독립하고, 기존 Shared DB 접근을 끊는다.

즉 Shared DB는 **"최종 상태"가 아니라 전환 과정의 과도기적 산물**로 정당화되는 경우가 많다. [Strangler fig pattern - AWS](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/strangler-fig.html)

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 Shared DB가 실제로 쓰이는 대표 상황

| # | 유즈 케이스 | 설명 | 적합한 이유 |
| --- | --- | --- | --- |
| 1 | **모놀리스 → MSA 전환 중간 단계** | 아직 데이터 분리가 끝나지 않은 레거시 시스템 | 리스크를 낮춘 점진적 이관 |
| 2 | **PoC(Proof of Concept)/MVP(Minimum Viable Product)** | 속도가 설계 완성도보다 중요한 초기 단계 | 빠른 검증이 우선 |
| 3 | **소규모 팀 (단일 팀이 여러 서비스 소유)** | 조직 경계와 서비스 경계가 일치, 마찰이 적음 | Conway's Law 상 문제가 덜 드러남 |
| 4 | **참조성(Read-only) 데이터 공유** | 코드/국가/환율 등 거의 안 바뀌는 마스터 데이터 | 쓰기 충돌 위험이 낮음 |

### ✅ Shared DB를 쓸 수밖에 없을 때의 완화 전략

1. **스키마/계정 분리**: 같은 DB 인스턴스라도 서비스별로 별도 스키마+DB 계정을 사용해 최소한 접근 권한을 격리한다.
2. **Read-only 접근 제한**: 자기 소유가 아닌 테이블은 읽기 전용으로만 접근하도록 강제한다.
3. **점진적 마이그레이션 로드맵 명시**: "임시"라고만 말하지 말고, 실제 분리 완료 시점을 로드맵에 못 박는다.

### 🏢 실제 적용 사례

- **넷플릭스(Netflix), 아마존(Amazon)** 등 MSA 선구 기업들은 서비스별 DB 소유를 원칙으로 강제하며, 이를 어기면 코드 리뷰에서 반려한다.
- 반대로 다수의 스타트업/레거시 대기업은 **모놀리스 DB에 신규 MS들이 당분간 얹혀 있는 과도기 아키텍처**를 몇 년씩 유지하는 경우도 실무에서 흔하다. [Database per Service — microservices.io](https://microservices.io/patterns/data/database-per-service.html)

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
| --- | --- | --- |
| ✅ Shared DB 장점 | 개발 속도 | 조인 쿼리, 트랜잭션을 그대로 활용 가능 |
| ✅ Shared DB 장점 | 운영 단순화 | 관리할 DB 인스턴스 수가 적음 (백업/모니터링 1곳) |
| ✅ Shared DB 장점 | 초기 비용 절감 | 인프라 프로비저닝, 라이선스 비용 절감 |
| ❌ Shared DB 단점 | 숨은 결합 | 한 서비스의 스키마 변경이 다른 서비스를 깨뜨림 |
| ❌ Shared DB 단점 | 독립 배포 불가 | DB 마이그레이션이 전체 서비스 배포를 블로킹 |
| ❌ Shared DB 단점 | 기술 선택 자유 상실 | 모든 서비스가 같은 DB 엔진에 종속 |
| ❌ Shared DB 단점 | 확장성 병목 | 하나의 DB가 모든 서비스의 부하를 감당 |

### ⚖️ Trade-off 분석

```
개발 속도/단순성   ◄──────── Trade-off ────────►   서비스 독립성/확장성
Shared Database    ◄─────────────────────────►    Database per Service
낮은 초기 비용                                      독립 배포·독립 스케일링
높은 결합도                                         분산 트랜잭션 복잡도 증가
```

[microservices.io 조사](https://dasroot.net/posts/2026/03/database-per-service-patterns-challenges-implementation/) 기준, Database per Service 도입 조직은 **배포 속도 30% 향상, 유지보수 비용 25% 절감**이 보고된 반면, 분산 트랜잭션·크로스 서비스 조인 처리 비용은 증가한다.

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 비교 매트릭스

| 비교 기준 | Shared Database (공유 DB) | Database per Service (서비스별 DB) |
| --- | --- | --- |
| 핵심 목적 | 개발 속도, 전환기 리스크 완화 | 서비스 독립성, 느슨한 결합 |
| 복잡도 | 낮음 (단일 DB, 조인 가능) | 높음 (분산 트랜잭션, Saga 필요) |
| 배포 독립성 | 낮음 (DB 변경이 전체에 영향) | 높음 (서비스별 독립 배포) |
| 트랜잭션 | ACID 트랜잭션 그대로 사용 가능 | Saga 패턴 등 Eventual Consistency 필요 |
| 기술 선택 | 전체가 동일 DB 엔진에 종속 | 서비스별로 최적 DB 선택 가능 (RDB, NoSQL, 그래프 DB 등) |
| 적합한 경우 | PoC, 전환 과도기, 소규모 팀 | 성숙한 MSA, 팀별 독립 오너십 필요 시 |

### 🔍 핵심 차이 요약

```
Shared Database                    Database per Service
──────────────────    vs    ──────────────────
같은 DB, 여러 서비스 접근            서비스마다 전용 DB
숨은 결합(암묵적 스키마 계약)         API/이벤트로만 통신
조인 쿼리 그대로 사용 가능            API Composition/CQRS 필요
"사실상 분산 모놀리스"               "진짜 MSA"에 가까움
```

### 🤔 언제 무엇을 선택?

- **Shared DB를 (한시적으로) 선택하세요** → 모놀리스에서 막 전환을 시작했거나, PoC 단계여서 아키텍처 완성도보다 검증 속도가 중요할 때. 단, "언젠가 분리한다"는 로드맵이 반드시 있어야 한다.
- **Database per Service를 선택하세요** → 서비스가 독립 배포·독립 스케일링을 실제로 필요로 하고, 팀 조직도 서비스 경계와 일치할 때 (조직이 성숙한 MSA를 지향할 때).

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| # | 실수 | 왜 문제인가 | 올바른 접근 |
| --- | --- | --- | --- |
| 1 | "서비스 코드만 분리하면 MSA다"라는 착각 | DB가 공유되면 배포·장애가 여전히 얽혀있어 사실상 모놀리스 | 서비스 분리 로드맵에 DB 분리를 반드시 포함 |
| 2 | Shared DB를 "임시"라 부르고 방치 | 임시가 수년간 고착화되는 경우가 실무에서 매우 흔함 | 분리 완료 기한을 명시적으로 관리 |
| 3 | 다른 서비스 테이블에 직접 쓰기(Write) | 데이터 소유권이 모호해지고 정합성 버그 발생 | 최소한 읽기 전용 접근으로 제한 |

### 🚫 Anti-Patterns

1. **분산 모놀리스(Distributed Monolith)**: 코드는 여러 서비스로 나눴지만 DB를 공유해서, 네트워크 호출 오버헤드는 다 떠안으면서 모놀리스의 결합도 문제는 그대로 남는 최악의 조합.
2. **암묵적 스키마 계약**: API 문서 대신 DB 테이블 구조 자체가 서비스 간 계약이 되어버려, 한 팀이 컬럼 하나만 바꿔도 다른 팀 서비스가 장애 나는 경우.

### 🔒 보안/성능 고려사항

- Shared DB 환경에서는 서비스별 접근 권한(계정, 스키마 권한)을 최소한이라도 분리하지 않으면, 한 서비스의 취약점이 전체 데이터에 접근 가능한 경로가 된다.
- 모든 서비스가 하나의 DB 커넥션 풀/리소스를 공유하므로, 특정 서비스의 트래픽 급증이 다른 서비스의 DB 성능까지 저하시킬 수 있다(Noisy Neighbor 문제).

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
| --- | --- | --- |
| 📖 공식 패턴 문서 | microservices.io | [Database per service](https://microservices.io/patterns/data/database-per-service.html) |
| 📖 AWS 가이드 | AWS Prescriptive Guidance | [Database-per-service pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/modernization-data-persistence/database-per-service.html), [Strangler fig pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/strangler-fig.html) |
| 📘 아티클 | HackerNoon | [Is a Shared Database Actually an Anti-pattern?](https://medium.com/hackernoon/is-shared-database-in-microservices-actually-anti-pattern-8cc2536adfe4) |
| 💬 커뮤니티 토론 | Hacker News | [Shared database anti-pattern 논쟁](https://news.ycombinator.com/item?id=19239952) |

### 🛠️ 관련 도구 & 패턴

| 도구/패턴 | 용도 |
| --- | --- |
| **Saga Pattern** | 분산 트랜잭션을 로컬 트랜잭션 + 보상 트랜잭션 체인으로 대체 |
| **CQRS** (Command Query Responsibility Segregation) | 쓰기(Command)와 읽기(Query) 모델을 분리해 크로스 서비스 조회 문제 완화 |
| **API Composition** | 여러 서비스의 응답을 조합해 하나의 API 응답으로 제공 |
| **Event Sourcing** | 상태 변화를 이벤트 로그로 저장해 Saga와 결합, 감사(Audit) 추적 용이 |

### 🔮 트렌드 & 전망

- 2026년 현재 업계 모범 사례는 **Saga(비동기 보상 트랜잭션) + CQRS(읽기/쓰기 분리)** 조합으로 분산 트랜잭션과 크로스 서비스 쿼리 문제를 동시에 완화하는 방향으로 수렴하고 있다.
- 완전한 Database per Service가 이상적이지만, 실무에서는 "스키마만 분리(Schema-per-service)"하는 절충안이 과도기 해법으로 널리 쓰인다.

### 💬 커뮤니티 인사이트

- Hacker News 토론에서는 "서비스 하나가 다른 서비스의 테이블에 쓰기 접근을 하는 순간, 이미 두 서비스는 하나의 배포 단위나 마찬가지"라는 의견이 다수 지지를 받았다. 즉 **읽기 공유는 논쟁의 여지가 있지만, 쓰기 공유는 거의 예외 없이 안티패턴으로 간주**된다.

---

## 📎 Sources

1. [Microservices Pattern: Database per service](https://microservices.io/patterns/data/database-per-service.html) — 공식 패턴 카탈로그
2. [Is a Shared Database in Microservices Actually an Anti-pattern? — HackerNoon](https://medium.com/hackernoon/is-shared-database-in-microservices-actually-anti-pattern-8cc2536adfe4) — 기술 블로그
3. [Shared database anti-pattern 논쟁 — Hacker News](https://news.ycombinator.com/item?id=19239952) — 커뮤니티 토론
4. [Strangler fig pattern — AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/strangler-fig.html) — 공식 문서
5. [Database-per-service pattern — AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/modernization-data-persistence/database-per-service.html) — 공식 문서
6. [Database per Service: Patterns, Challenges, and Implementation Strategies](https://dasroot.net/posts/2026/03/database-per-service-patterns-challenges-implementation/) — 기술 블로그 (배포속도/비용 통계)
7. [Microservices Pattern: Saga](https://microservices.io/patterns/data/saga.html) — 공식 패턴 카탈로그

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 6
> - 수집 출처 수: 7
> - 출처 유형: 공식 3, 블로그 3, 커뮤니티 1
