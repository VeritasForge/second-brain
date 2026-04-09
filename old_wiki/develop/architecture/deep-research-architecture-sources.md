---
created: 2026-04-01
source: claude-code
tags: [architecture, deep-research, ddd, hexagonal-architecture, clean-architecture, layered-architecture, sources]
---

# 🔬 Deep Research: 4대 아키텍처 패턴 공식 참고 자료

> 💡 **한줄 요약**: DDD, Hexagonal, Clean, Layered Architecture의 원전과 권위 있는 참고 자료를 3단계 Deep Research 프로토콜로 수집하고 교차 검증한 결과.

---

## 📋 Executive Summary

4대 아키텍처 패턴의 원전을 수집하고 교차 검증한 결과:
- **Layered Architecture (1996)**: POSA Vol.1이 원전, Fowler(2002)가 실무 체계화
- **DDD (2003)**: Eric Evans의 "Blue Book"이 원전, Strategic + Tactical 설계로 구성
- **Hexagonal Architecture (2005)**: Alistair Cockburn이 Layered의 계층 경계 위반 문제를 해결하기 위해 고안
- **Onion Architecture (2008)**: Jeffrey Palermo가 DDD 레이어를 Ports & Adapters에 통합
- **Clean Architecture (2012)**: Robert C. Martin이 Hexagonal + Onion + DCI를 통합

이들은 배타적이 아니라 **상호보완적**이며, 실무에서는 **DDD + Hexagonal** 또는 **DDD + Clean** 조합이 가장 일반적이다.

---

## 🔍 Findings

### 1. Layered Architecture — 원전 및 구성요소

- ✅ **확신도**: [Confirmed]
- **원전**:
  - POSA Vol.1 (Buschmann et al., 1996) — "Layers" 패턴
  - Martin Fowler, "Patterns of Enterprise Application Architecture" (2002) — 실무 체계화
- **핵심 구성요소**: Presentation Layer, Application/Service Layer, Business/Domain Layer, Persistence/Data Access Layer, Database Layer, DTO
- **Strict vs Relaxed Layering**:
  - Strict: 바로 아래 레이어만 호출 가능 → 변경 영향 최소화
  - Relaxed: 아래의 모든 레이어 호출 가능 → 불필요한 proxy 방지, 실무에서 더 흔함

**출처**:
- [Catalog of Patterns of Enterprise Application Architecture — Martin Fowler](https://martinfowler.com/eaaCatalog/)
- [Layered Architecture: Still a Solid Approach — NDepend Blog](https://blog.ndepend.com/layered-architecture-solid-approach/)
- [Layered Architecture — Baeldung](https://www.baeldung.com/cs/layered-architecture)
- [Layered Architecture — Herbertograca](https://herbertograca.com/2017/08/03/layered-architecture/)

---

### 2. Domain-Driven Design (DDD) — 원전 및 구성요소

- ✅ **확신도**: [Confirmed]
- **원전**: Eric Evans, "Domain-Driven Design: Tackling Complexity in the Heart of Software" (2003, Addison-Wesley)
- **보충 자료**: Vaughn Vernon, "Implementing Domain-Driven Design" (2013) — 실무 구현 가이드

#### Strategic Design 구성요소
| 구성요소 | 역할 |
|---|---|
| **Domain / Subdomain** | 소프트웨어가 다루는 지식/활동 범위. Core/Supporting/Generic으로 분류 |
| **Ubiquitous Language** | 개발자와 도메인 전문가가 공유하는 일관된 용어 체계 |
| **Bounded Context** | 도메인 모델이 유효한 명시적 경계. 하나의 팀이 소유 |
| **Context Map** | Bounded Context 간 관계를 시각화. 거버넌스/커뮤니케이션 이슈 식별 |
| **Anti-Corruption Layer (ACL)** | 외부 컨텍스트의 모델이 내부 도메인 모델을 오염시키지 않도록 보호하는 번역 계층 |

**Context Map 패턴**:
- Upstream: Open Host Service, Event Publisher
- Midway: Shared Kernel, Published Language, Separate Ways, Partnership
- Downstream: Customer/Supplier, Conformist, Anti-Corruption Layer

#### Tactical Design 구성요소
| 구성요소 | 역할 |
|---|---|
| **Entity** | 고유 식별자(ID)를 가진 가변 객체. ID로 동등성 판단 |
| **Value Object** | 식별자 없는 불변 객체. 속성값으로만 동등성 판단 |
| **Aggregate** | 관련 Entity/VO의 일관성 단위 클러스터 |
| **Aggregate Root** | Aggregate의 진입점. 외부에서 참조 가능한 유일한 Entity |
| **Repository** | Aggregate의 영속성을 추상화하는 컬렉션 인터페이스 |
| **Domain Service** | Entity/VO에 속하지 않는 도메인 로직을 담는 상태 없는 객체 |
| **Application Service** | Use Case 오케스트레이션. 비즈니스 로직은 포함하지 않음 |
| **Infrastructure Service** | 이메일 발송, 로깅 등 인프라 관심사 수행 |
| **Domain Event** | 도메인에서 발생한 중요 사건을 표현하는 객체 |
| **Factory** | 복잡한 Aggregate/Entity 생성 로직을 캡슐화 |
| **Specification** | 비즈니스 규칙을 재조합 가능한 단위로 캡슐화. 검증/선택/생성 3가지 용도 |
| **Module** | 관련 클래스를 그룹화 (Java의 패키지, C#의 네임스페이스) |

#### DDD 4 레이어 (Evans 원서 기준)
| 레이어 | 역할 |
|---|---|
| **User Interface** | 사용자에게 정보 표현, 명령 해석 |
| **Application Layer** | 비즈니스 로직 없음. 작업 진행 상태만 관리. 도메인 객체에 작업 위임 |
| **Domain Layer** | 비즈니스 규칙과 로직의 핵심. 비즈니스 객체 상태 보유 |
| **Infrastructure Layer** | 기술적 지원. 레이어 간 통신, 영속성, UI 라이브러리 |

**출처**:
- [Domain-Driven Design — Amazon](https://www.amazon.com/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215)
- [DDD Reference — Domain Language (Eric Evans)](https://www.domainlanguage.com/ddd/reference/)
- [Martin Fowler — Domain Driven Design bliki](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Microsoft — Use Tactical DDD to Design Microservices](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/tactical-ddd)
- [Enterprise Craftsmanship — Domain vs Application Services](https://enterprisecraftsmanship.com/posts/domain-vs-application-services/)
- [Vaadin — Tactical DDD Building Blocks](https://vaadin.com/blog/ddd-part-2-tactical-domain-driven-design)

---

### 3. Hexagonal Architecture (Ports & Adapters) — 원전 및 구성요소

- ✅ **확신도**: [Confirmed]
- **원전**: Alistair Cockburn, HaT Technical Report (2005.09.04, v0.9). 2005년 7월에 "Ports and Adapters"로 개명
- **서적**: Cockburn & Garrido de Paz, "Hexagonal Architecture Explained" (2023, ISBN 978-1737519782)

#### 핵심 구성요소
| 구성요소 | 역할 |
|---|---|
| **Hexagon (Application)** | 비즈니스 로직이 사는 내부. 외부 기술에 대해 무지 |
| **Port** | 애플리케이션과 외부 세계의 통신 채널(인터페이스). 2~4개가 일반적 |
| **Input/Driving Port** | 외부가 애플리케이션을 구동하기 위한 인터페이스 |
| **Output/Driven Port** | 애플리케이션이 외부 자원을 사용하기 위한 인터페이스 |
| **Driving Adapter (Primary)** | 외부 → 애플리케이션 신호 변환 (GUI, HTTP, 테스트 등) |
| **Driven Adapter (Secondary)** | 애플리케이션 → 외부 신호 변환 (DB, 이메일, 외부 API 등) |
| **Primary Actor** | 애플리케이션 상호작용을 시작하는 외부 주체 (사용자, 테스트 스크립트, 배치) |
| **Secondary Actor** | 애플리케이션이 조회/통보하는 외부 주체 (DB, 외부 서비스, 하드웨어) |
| **Configurator** | 어떤 어댑터 인스턴스를 사용할지 선택하는 메커니즘 (DI, Factory 등) |
| **Application Service** | Port 뒤에서 Use Case를 오케스트레이션하는 서비스 |

#### 탄생 동기 (Cockburn 인터뷰 원문 기반)
> "나는 port가 뭔지도 몰랐다. 그냥 그렇게 되어야 한다는 것만 알았다." — Cockburn, 1994년 OO 수업에서 MVC에서 영감받아 모든 방향에 인터페이스를 원함. **DB 루프백 실패** 프로젝트에서 아키텍처 사고의 동기 부여.

Layered Architecture의 문제점:
1. 계층 경계를 "선"으로만 그리니 사람들이 진지하게 받아들이지 않음 → 비즈니스 로직 누출
2. 2개 이상의 포트가 있으면 1차원 레이어 그림에 안 맞음
3. DB에 저장 프로시저, UI에 비즈니스 로직 → 긴밀한 결합

**출처**:
- [Hexagonal Architecture — Alistair Cockburn (원전)](https://alistair.cockburn.us/hexagonal-architecture)
- [Interview with Alistair Cockburn — Hexagonal Me](https://jmgarridopaz.github.io/content/interviewalistair.html)
- [Hexagonal Architecture Explained — Amazon](https://www.amazon.com/Hexagonal-Architecture-Explained-Alistair-Cockburn/dp/173751978X)
- [AWS Prescriptive Guidance — Hexagonal Architecture Pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/hexagonal-architecture.html)
- [Hexagonal Architecture — Wikipedia](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software))

---

### 4. Onion Architecture — 맥락 참고

- ✅ **확신도**: [Confirmed]
- **원전**: Jeffrey Palermo, "The Onion Architecture: Part 1~4" (2008.07~2013)
- **핵심 원칙**:
  1. 애플리케이션은 독립적인 객체 모델을 중심으로 구축
  2. 내부 레이어가 인터페이스를 정의, 외부 레이어가 구현
  3. 결합 방향은 항상 중심을 향함
  4. 모든 애플리케이션 코어 코드는 인프라 없이 컴파일/실행 가능

**Hexagonal과의 관계**: "DDD 레이어를 Ports & Adapters 아키텍처에 통합" — Herbertograca
- 외부 hexagon = Onion의 Infrastructure
- 내부 hexagon = Onion의 Application Core (Application Services → Domain Services → Domain Model)

**출처**:
- [The Onion Architecture: Part 1 — Jeffrey Palermo (원전)](https://jeffreypalermo.com/2008/07/the-onion-architecture-part-1/)
- [Onion Architecture — Herbertograca](https://herbertograca.com/2017/09/21/onion-architecture/)

---

### 5. Clean Architecture — 원전 및 구성요소

- ✅ **확신도**: [Confirmed]
- **원전**: Robert C. Martin, "The Clean Architecture" 블로그 포스트 (2012.08.13)
- **서적**: "Clean Architecture: A Craftsman's Guide to Software Structure and Design" (2017, Prentice Hall)

#### 핵심 구성요소
| 구성요소 | 레이어 | 역할 |
|---|---|---|
| **Entity** | 1 (최내부) | Enterprise 범위 비즈니스 규칙. 변경 가능성 최소 |
| **Use Case (Interactor)** | 2 | Application 특화 비즈니스 규칙. 데이터 흐름 오케스트레이션 |
| **Interface Adapter** | 3 | Use Case ↔ 외부 시스템 간 데이터 변환 (MVC, DB 어댑터) |
| **Controller** | 3 | 사용자 입력 수신 |
| **Presenter** | 3 | 표시용 데이터 포맷팅 |
| **ViewModel** | 3 | 레이어 간 전달되는 단순 데이터 구조 |
| **Gateway** | 3 | DB/서비스용 인터페이스 어댑터 |
| **Framework & Driver** | 4 (최외부) | 웹 프레임워크, DB, 외부 도구 |
| **Boundary (Input/Output)** | 2-3 경계 | 레이어 간 제어 역전을 가능케 하는 인터페이스 |

#### The Dependency Rule (핵심 규칙)
> "소스 코드 의존성은 오직 안쪽으로만 향할 수 있다." — Bob Martin

- 내부 원에 있는 어떤 것도 외부 원에 대해 알 수 없음
- 외부 원에서 선언된 이름을 내부 원의 코드에서 언급해서는 안 됨
- 경계를 넘는 데이터는 "격리된 단순 데이터 구조"만 허용 (Entity나 DB row 금지)

#### 관련 아키텍처와의 관계 (Bob Martin 원문)
> "Hexagonal Architecture, Onion Architecture, DCI 등 모두 **관심사의 분리를 레이어 설계를 통해 달성**한다는 공통 목적을 공유한다."

**출처**:
- [The Clean Architecture — Uncle Bob 블로그 (원전)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Clean Architecture — Amazon](https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164)

---

### 6. 사용자 제공 참고 자료 분석

#### Herbertograca — Explicit Architecture

- ✅ **확신도**: [Confirmed] (다수 기술 블로그에서 인용)
- **핵심 기여**: DDD + Hexagonal + Onion + Clean + CQRS를 **하나의 다이어그램**으로 통합
- **3가지 기본 구성**: User Interface ↔ Application Core ↔ Infrastructure
- **Ports & Adapters로 연결**, 모든 의존성은 중심을 향함
- **도메인별 패키징(Package by component)** 권장
- **이벤트 기반 통신 + 공유 커널**로 컴포넌트 간 결합도 최소화

**출처**: [Explicit Architecture — Herbertograca (원문)](https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/)

#### RanchoCooper/go-hexagonal

- 🟡 **확신도**: [Likely] (실무 구현체, 101 stars)
- **핵심**: Go 마이크로서비스 프레임워크, Hexagonal + DDD 조합
- **구조**: adapter/ (외부) → application/ (유스케이스) → domain/ (비즈니스 로직)
- **기술 스택**: Gin, GORM, Redis, MongoDB, Wire(DI), CQRS, Domain Events
- **DDD 구성요소 구현**: Aggregate, Entity, Value Object, Repository, Domain Event, CQRS

**출처**: [go-hexagonal — GitHub](https://github.com/RanchoCooper/go-hexagonal)

---

## 📊 아키텍처 간 역사적 진화 관계

```
1996  POSA Vol.1 ──── Layered Architecture (수평 레이어, 위→아래 의존성)
  │                    문제: 계층 경계 위반, UI/DB에 비즈니스 로직 누출
  │
2002  Fowler ─────── PofEAA (Layered 실무 체계화)
  │
2003  Eric Evans ─── DDD (도메인 모델링 철학 + 전략/전술 설계)
  │                    DDD는 내부 구조를 정의하지만, 외부 경계 관리는 미지정
  │
2005  Cockburn ───── Hexagonal (Ports & Adapters)
  │                    Layered의 1차원 한계 해결, 안/밖 대칭 구조
  │                    DDD의 외부 경계를 관리하는 보완적 패턴으로 채택
  │
2008  Palermo ────── Onion Architecture
  │                    DDD 레이어를 Hexagonal 구조에 통합
  │                    내부→외부 의존성 규칙 명시화
  │
2012  Bob Martin ─── Clean Architecture
                      Hexagonal + Onion + DCI 통합
                      Dependency Rule을 핵심 원칙으로 정식화
                      4-레이어 동심원 모델
```

**핵심 인과관계** ✅ [Confirmed]:
- Layered의 "계층 경계 위반" → Hexagonal의 "안/밖 대칭" 탄생
- DDD의 "내부 구조 필요" + Hexagonal의 "외부 경계 관리" → 상호보완적 조합
- Onion이 DDD + Hexagonal 통합 → Clean이 이를 정식화

---

## ⚔️ Contradictions Found

- **DDD 연도**: DDD(2003)는 Hexagonal(2005)보다 먼저 출판되었지만, Cockburn은 1994년부터 Hexagonal 개념을 구상했음. 따라서 "Hexagonal이 DDD 이후에 나왔다"는 것은 출판 기준이지 아이디어 기준은 아님 ✅ [Confirmed]
- **Layered의 레이어 수**: 3-tier, 4-tier 등 출처마다 다름. POSA는 일반 패턴으로 레이어 수를 제한하지 않음. Fowler는 3 레이어(Presentation, Domain, Data Source)를 주로 사용 🟡 [Likely]

---

## ⚠️ Edge Cases & Caveats

- DDD의 모든 구성요소를 소규모 프로젝트에 적용하면 **과도한 복잡성** 초래
- Hexagonal의 Configurator는 원전에서만 명시적으로 다루고, 실무 블로그에서는 자주 생략됨
- Clean Architecture의 ViewModel은 Bob Martin 원문에서 간략히만 언급되며, 실무에서는 다양하게 해석됨

---

## 📎 Sources (전체 목록)

### 원전 (Primary Sources)
1. [Hexagonal Architecture — Alistair Cockburn (원전, 2005)](https://alistair.cockburn.us/hexagonal-architecture) — 1차 자료
2. [The Clean Architecture — Robert C. Martin (원전, 2012)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) — 1차 자료
3. [The Onion Architecture: Part 1 — Jeffrey Palermo (원전, 2008)](https://jeffreypalermo.com/2008/07/the-onion-architecture-part-1/) — 1차 자료
4. [Domain-Driven Design — Eric Evans (서적, 2003)](https://www.amazon.com/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215) — 1차 자료
5. [DDD Reference — Eric Evans](https://www.domainlanguage.com/ddd/reference/) — 1차 자료

### 권위 있는 기술 문서
6. [AWS Prescriptive Guidance — Hexagonal Architecture](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/hexagonal-architecture.html) — 공식 문서
7. [Microsoft Azure — Tactical DDD for Microservices](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/tactical-ddd) — 공식 문서
8. [Martin Fowler — PofEAA Catalog](https://martinfowler.com/eaaCatalog/) — 1차 자료

### 통합/비교 분석
9. [Explicit Architecture — Herbertograca](https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/) — 기술 블로그
10. [Interview with Alistair Cockburn — Hexagonal Me](https://jmgarridopaz.github.io/content/interviewalistair.html) — 1차 자료
11. [go-hexagonal — RanchoCooper](https://github.com/RanchoCooper/go-hexagonal) — 실무 구현체

### 보조 자료
12. [Hexagonal Architecture — Wikipedia](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)) — 커뮤니티
13. [Layered Architecture — Baeldung](https://www.baeldung.com/cs/layered-architecture) — 기술 블로그
14. [Enterprise Craftsmanship — Domain vs Application Services](https://enterprisecraftsmanship.com/posts/domain-vs-application-services/) — 기술 블로그
15. [Vaadin — Tactical DDD Building Blocks](https://vaadin.com/blog/ddd-part-2-tactical-domain-driven-design) — 기술 블로그

---

## 📊 Research Metadata

- 검색 쿼리 수: 9 (일반 8 + SNS 1, SNS 결과 없음)
- 수집 출처 수: 15
- 출처 유형 분포: 공식 문서 2, 1차 자료 6, 기술 블로그 5, 커뮤니티 1, 실무 구현체 1
- WebFetch 원문 확인: 5건 (Cockburn 원전, Bob Martin 원전, Cockburn 인터뷰, Herbertograca, go-hexagonal)
- 확신도 분포: ✅ Confirmed 7, 🟡 Likely 2, 🔄 Synthesized 0, ❓ Uncertain 0, ⚪ Unverified 0
- Wikipedia 403 차단 → WebSearch 대체 경로 사용
- Semantic Scholar API 429 rate limit → 학술 논문 검색 생략 (원전 서적/블로그로 충분)
