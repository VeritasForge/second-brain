# 🎯 Senior Backend Engineer 기술 면접 Q&A 100선

> 📅 생성일: 2026-03-22
> 🏢 대상: 크디랩(쏘카인드) Senior Backend Engineer
> 📋 기반: JD 분석 + Deep Research + Concept Explainer 조사 결과
> 🔬 조사 범위: Spring Boot API 설계, DB 최적화, WebRTC, LLM 통합, Kotlin, 테스트, 팀 리딩

---

## 중요도 범례

| Tier | 범위 | JD 매핑 |
|------|------|---------|
| 🔴 Tier 1 | #1~30 | Spring Boot REST API 설계, DB 스키마/쿼리 최적화, 백엔드 아키텍처 |
| 🟠 Tier 2 | #31~55 | 팀 리딩, 개발 문화/프로세스, 기술 로드맵, 기술 부채 관리 |
| 🟡 Tier 3 | #56~80 | Kotlin, JPA/ORM, 테스트, 멀티모듈, WebRTC/WebSocket, Redis |
| 🟢 Tier 4 | #81~100 | LLM 상용화, Spring AI, 스타트업 경험, FE 협업, Agile |

---

## 🔴 Tier 1: 백엔드 아키텍처 설계 및 개발 (#1~30)

---

### Q1. Spring Boot에서 REST API를 설계할 때 가장 중요하게 고려하는 원칙은 무엇인가요?

**A.** REST API 설계의 핵심 원칙은 **자원(Resource) 중심 설계**, **일관된 응답 구조**, **적절한 HTTP 메서드/상태 코드 사용**입니다.

1. **자원 중심 URL**: `/users`, `/orders/{id}/items`처럼 명사 복수형 사용. 동사는 HTTP 메서드로 표현
2. **일관된 응답 포맷**: 성공/실패 모두 동일한 envelope 구조 (`{ status, data, error }`)를 유지하여 클라이언트의 파싱 로직을 단순화
3. **DTO를 통한 캡슐화**: 엔티티를 직접 노출하지 않고 DTO로 변환하여 내부 스키마 변경이 API 계약에 영향을 주지 않도록 분리
4. **API 버전 관리**: URI 경로(`/api/v1/`), 헤더, 쿼리 파라미터 중 팀 합의된 전략 선택. URI 경로 방식이 가장 직관적이고 캐싱에 유리
5. **HATEOAS 수준 결정**: Richardson Maturity Model Level 2(HTTP 메서드 + 상태 코드)를 기본으로, 필요 시 Level 3(하이퍼미디어 링크) 적용

> 📎 출처: [Baeldung - Spring Boot REST Best Practices](https://www.springboottutorial.com/rest-api-best-practices-with-java-and-spring), [CodingShuttle](https://www.codingshuttle.com/blogs/best-practices-for-writing-spring-boot-api/)

---

### Q2. 계층형 아키텍처(Layered)와 헥사고날 아키텍처(Hexagonal)의 차이를 설명하고, 어떤 상황에서 헥사고날을 선택하나요?

**A.**

```
┌─── 계층형 (Layered) ───┐    ┌──── 헥사고날 (Hexagonal) ────┐
│  Controller             │    │        ┌─────────┐           │
│     ↓                   │    │   Port ←│  Domain │→ Port    │
│  Service                │    │        └─────────┘           │
│     ↓                   │    │   ↑                    ↑     │
│  Repository             │    │ Adapter(Web)    Adapter(DB)  │
└─────────────────────────┘    └──────────────────────────────┘
```

| 비교 기준 | 계층형 | 헥사고날 |
|-----------|--------|----------|
| 의존 방향 | 위→아래 단방향 | 도메인이 중심, 외부→도메인 |
| 테스트 용이성 | DB/프레임워크 의존적 | 도메인 로직 독립 테스트 가능 |
| 복잡도 | 낮음 | 포트/어댑터 정의 필요, 초기 복잡도 높음 |
| 적합한 상황 | CRUD 중심, 빠른 개발 | 도메인 로직 복잡, 외부 시스템 교체 가능성 |

**선택 기준**: 쏘카인드처럼 AI 모델 제공자(OpenAI/Gemini)가 바뀔 수 있고, 도메인 로직(교육 평가 알고리즘)이 핵심인 경우 헥사고날이 적합. AI 서비스 포트를 인터페이스로 정의하면 LLM 제공자 교체가 어댑터 교체로 해결됩니다.

> 📎 출처: [JavaScript in Plain English - Hexagonal in Spring Boot](https://javascript.plainenglish.io/architecting-enterprise-grade-rest-apis-in-spring-boot-a-deep-guide-to-clean-hexagonal-fdd65df3ccb3)

---

### Q3. Spring Boot에서 전역 예외 처리를 어떻게 설계하나요?

**A.** `@ControllerAdvice` + `@ExceptionHandler`로 전역 예외 처리를 중앙 집중화합니다.

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusiness(BusinessException e) {
        return ResponseEntity.status(e.getStatus())
            .body(new ErrorResponse(e.getCode(), e.getMessage()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(MethodArgumentNotValidException e) {
        List<FieldError> errors = e.getBindingResult().getFieldErrors()
            .stream().map(f -> new FieldError(f.getField(), f.getDefaultMessage()))
            .toList();
        return ResponseEntity.badRequest()
            .body(new ErrorResponse("VALIDATION_ERROR", "입력값 검증 실패", errors));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleUnexpected(Exception e) {
        log.error("Unexpected error", e);
        return ResponseEntity.internalServerError()
            .body(new ErrorResponse("INTERNAL_ERROR", "서버 내부 오류"));
    }
}
```

**설계 원칙**:
1. **예외 계층 구조**: `BusinessException` → `NotFoundException`, `DuplicateException` 등 하위 클래스
2. **에러 코드 체계**: 도메인별 코드 (예: `USER_001`, `SESSION_002`)를 정의하여 FE/클라이언트가 에러 유형을 구분
3. **로깅 분리**: 4xx는 WARN, 5xx는 ERROR로 로그 레벨 분리
4. **민감 정보 차단**: 스택 트레이스나 DB 에러를 클라이언트에 노출하지 않음

---

### Q4. API 버전 관리 전략을 비교하고, 실무에서 어떤 방식을 선호하나요?

**A.**

| 전략 | 예시 | 장점 | 단점 |
|------|------|------|------|
| URI 경로 | `/api/v1/users` | 직관적, CDN 캐싱 용이 | URL 오염, 라우팅 복잡 |
| 쿼리 파라미터 | `?version=1` | 기존 URL 유지 | 캐시 키 복잡 |
| 커스텀 헤더 | `X-API-Version: 1` | URL 깔끔 | 브라우저 테스트 어려움 |
| Content Negotiation | `Accept: application/vnd.api.v1+json` | RESTful 원칙 준수 | 구현/테스트 복잡 |

**실무 선호**: **URI 경로 방식**. 이유:
- FE 개발자와 API 문서 공유 시 가장 명확
- Swagger/OpenAPI 문서에 자연스럽게 반영
- CDN/프록시에서 경로 기반 라우팅 가능
- 하위 호환성을 유지하면서 점진적 마이그레이션 가능

---

### Q5. DTO와 Entity를 분리해야 하는 이유와 매핑 전략은?

**A.** 분리 이유:

1. **보안**: Entity의 민감 필드(password, 내부 ID)가 API에 노출되는 것을 방지
2. **유연성**: API 스펙 변경이 DB 스키마에 영향 주지 않음 (반대도 동일)
3. **직렬화 제어**: Entity의 양방향 관계에서 발생하는 순환 참조 방지
4. **검증 분리**: 입력 DTO에 `@Valid` 검증을, Entity에 DB 제약 조건을 분리

**매핑 전략 비교**:

| 방식 | 도구 | 장점 | 단점 |
|------|------|------|------|
| 수동 매핑 | 직접 코드 | 완전 제어, 디버깅 쉬움 | 보일러플레이트 |
| MapStruct | 컴파일 타임 코드 생성 | 타입 안전, 성능 최적 | 설정 필요 |
| ModelMapper | 리플렉션 기반 | 설정 간단 | 런타임 오류 가능, 성능 저하 |
| Kotlin data class copy | `copy()` 함수 | Kotlin 네이티브, 간결 | 깊은 복사 제한 |

**권장**: Kotlin 프로젝트에서는 **확장 함수(extension function)** 를 활용한 수동 매핑이 간결하고 타입 안전합니다:

```kotlin
fun UserEntity.toDto() = UserResponse(id = this.id, name = this.name, email = this.email)
fun CreateUserRequest.toEntity() = UserEntity(name = this.name, email = this.email)
```

---

### Q6. MySQL과 PostgreSQL의 핵심 차이를 설명하고, 선택 기준은?

**A.**

| 비교 기준 | MySQL | PostgreSQL |
|-----------|-------|------------|
| MVCC 구현 | Undo Log 기반 | 다중 버전 튜플 직접 저장 |
| JSON 지원 | JSON 타입 (제한적) | JSONB 타입 (인덱스/쿼리 최적화) |
| 풀텍스트 검색 | 기본 지원 (제한적) | GIN 인덱스 + tsvector (강력) |
| 확장성 | 제한적 | 커스텀 타입, 함수, 확장 모듈 |
| 복제 | 비동기 기본 | 동기/비동기 선택, 논리적 복제 |
| 라이선스 | GPL (Oracle 소유) | BSD (완전 오픈소스) |
| 쓰기 성능 | 단순 INSERT 빠름 | 복잡 트랜잭션에 강함 |

**선택 기준**:
- **MySQL 선택**: 읽기 중심, 단순 CRUD, 이미 MySQL 인프라가 구축된 경우
- **PostgreSQL 선택**: JSONB 활용 (AI 리포트 데이터), 복잡 쿼리, 풀텍스트 검색, 확장 필요 시

쏘카인드의 경우 AI 평가 리포트(멀티모달 분석 결과)를 JSONB로 유연하게 저장하고, GIN 인덱스로 검색 최적화가 가능한 **PostgreSQL이 더 적합**합니다.

---

### Q7. 데이터베이스 인덱스 전략을 설명하세요. B-Tree 외에 어떤 인덱스 유형을 알고 있나요?

**A.**

| 인덱스 유형 | 용도 | 예시 |
|------------|------|------|
| **B-Tree** | 범위 검색, 정렬, 동등 비교 (기본) | `WHERE created_at > '2025-01-01'` |
| **Hash** | 동등 비교 전용 (PostgreSQL) | `WHERE user_id = 123` |
| **GIN** | 배열, JSONB, 풀텍스트 검색 | `WHERE tags @> '{"ai"}'` |
| **GiST** | 지리/기하학 데이터, 범위 타입 | PostGIS 좌표 검색 |
| **BRIN** | 물리적으로 정렬된 대용량 테이블 | 시계열 데이터 (created_at 기준) |
| **Partial Index** | 조건부 인덱스 | `WHERE status = 'ACTIVE'` |
| **Composite Index** | 복합 조건 검색 | `(company_id, created_at)` |

**인덱스 설계 원칙**:
1. **선택도(Selectivity)가 높은 컬럼 우선**: 유니크 값이 많은 컬럼
2. **복합 인덱스 순서**: WHERE 조건 → ORDER BY → SELECT 순서 고려 (커버링 인덱스)
3. **쓰기 오버헤드**: 인덱스가 많으면 INSERT/UPDATE 성능 저하 → 필요한 것만
4. **`EXPLAIN ANALYZE`로 검증**: 인덱스가 실제로 사용되는지 반드시 확인

```sql
-- PostgreSQL: JSONB 필드에 GIN 인덱스
CREATE INDEX idx_report_data ON evaluation_reports USING GIN (report_data);

-- Partial Index: 활성 세션만 인덱싱
CREATE INDEX idx_active_sessions ON training_sessions (user_id)
WHERE status = 'ACTIVE';
```

---

### Q8. N+1 쿼리 문제를 설명하고, 해결 방법을 3가지 이상 제시하세요.

**A.** N+1 문제는 **1개의 목록 조회 쿼리 + 각 항목마다 N개의 추가 쿼리**가 발생하는 성능 문제입니다.

```
-- 1번째 쿼리: 모든 저자 조회
SELECT * FROM authors;                       -- 1 query

-- N번째 쿼리: 각 저자의 책 조회
SELECT * FROM books WHERE author_id = 1;     -- N queries
SELECT * FROM books WHERE author_id = 2;
SELECT * FROM books WHERE author_id = 3;
...
```

**해결 방법**:

| # | 방법 | 코드 예시 | 특징 |
|---|------|-----------|------|
| 1 | **Fetch Join (JPQL)** | `@Query("SELECT a FROM Author a JOIN FETCH a.books")` | 1번 쿼리로 해결. 페이징 불가(컬렉션) |
| 2 | **@EntityGraph** | `@EntityGraph(attributePaths = {"books"})` | 선언적, 재사용 가능 |
| 3 | **Batch Fetch Size** | `spring.jpa.properties.hibernate.default_batch_fetch_size=100` | 글로벌 설정, N+1→1+(N/batch) |
| 4 | **DTO Projection** | `SELECT new AuthorDto(a.id, a.name) FROM Author a` | 필요한 필드만 조회, 성능 최적 |
| 5 | **@Fetch(SUBSELECT)** | Hibernate 전용 | 서브쿼리로 연관 데이터 한번에 로드 |

**실무 권장**: `default_batch_fetch_size=100`을 글로벌로 설정하고, 성능이 중요한 곳에서 Fetch Join 또는 DTO Projection 사용.

> 📎 출처: [Baeldung - N+1 Problem](https://www.baeldung.com/spring-hibernate-n1-problem)

---

### Q9. JPA에서 Lazy Loading과 Eager Loading의 차이와 기본 전략은?

**A.**

| 전략 | 동작 | 기본 적용 |
|------|------|-----------|
| **Lazy Loading** | 연관 엔티티를 실제 접근 시점에 쿼리 | `@OneToMany`, `@ManyToMany` |
| **Eager Loading** | 부모 엔티티 조회 시 즉시 함께 조회 | `@ManyToOne`, `@OneToOne` |

**Lazy Loading 주의사항**:
1. **LazyInitializationException**: 영속성 컨텍스트(Session) 밖에서 프록시 접근 시 발생
2. **해결**: OSIV(Open Session In View) 비활성화 + Service 계층에서 필요한 데이터를 모두 DTO로 변환
3. **직렬화 문제**: Jackson이 Lazy 프록시를 직렬화하면 오류 → `@JsonIgnore` 또는 DTO 분리

**실무 원칙**: "기본은 Lazy, 필요할 때만 Fetch Join으로 즉시 로딩"

```yaml
# OSIV 비활성화 (권장)
spring.jpa.open-in-view: false
```

---

### Q10. 쿼리 최적화를 위해 EXPLAIN ANALYZE를 어떻게 활용하나요?

**A.** `EXPLAIN ANALYZE`는 실제 쿼리를 실행하여 **실행 계획 + 실제 소요 시간**을 보여줍니다.

```sql
EXPLAIN ANALYZE
SELECT u.*, ts.score
FROM users u
JOIN training_sessions ts ON u.id = ts.user_id
WHERE ts.company_id = 42 AND ts.status = 'COMPLETED'
ORDER BY ts.created_at DESC
LIMIT 20;
```

**핵심 확인 포인트**:

| 항목 | 좋은 신호 | 나쁜 신호 |
|------|-----------|-----------|
| Scan 타입 | Index Scan, Index Only Scan | Seq Scan (대용량 테이블) |
| Rows | actual ≈ estimated | 큰 차이 (통계 업데이트 필요) |
| Sort | 인덱스 정렬 | External Merge Sort (메모리 부족) |
| Join | Nested Loop (소량), Hash Join (대량) | Nested Loop (대용량, 인덱스 없음) |

**최적화 흐름**:
1. `EXPLAIN ANALYZE`로 병목 지점 확인
2. 필요한 인덱스 추가
3. `ANALYZE` 명령으로 통계 업데이트
4. 쿼리 리팩토링 (서브쿼리 → JOIN, LIMIT 활용)
5. 재실행하여 개선 확인

---

### Q11. 대용량 테이블에서 페이징 성능을 개선하는 방법은?

**A.** 전통적인 `OFFSET`/`LIMIT` 방식은 OFFSET이 클수록 성능이 급격히 저하됩니다.

```sql
-- ❌ 느림: OFFSET 100만 → 100만 행을 스캔 후 버림
SELECT * FROM sessions ORDER BY id LIMIT 20 OFFSET 1000000;

-- ✅ 빠름: 커서 기반 (Keyset Pagination)
SELECT * FROM sessions WHERE id > :lastId ORDER BY id LIMIT 20;
```

**페이징 전략 비교**:

| 전략 | 원리 | 장점 | 단점 |
|------|------|------|------|
| OFFSET/LIMIT | 행 건너뛰기 | 구현 간단, 페이지 점프 가능 | 대용량 시 성능 저하 |
| Keyset (커서) | 마지막 키 기준 조회 | 일정한 성능, 대용량 적합 | 페이지 점프 불가 |
| Covering Index | 인덱스만으로 결과 반환 | 디스크 I/O 최소화 | 인덱스 크기 증가 |
| Deferred Join | 서브쿼리로 ID만 먼저 조회 | OFFSET 성능 개선 | 쿼리 복잡도 증가 |

**실무 권장**: 무한 스크롤 UI → Keyset Pagination, 관리자 페이지(페이지 번호) → Deferred Join

---

### Q12. Spring Boot에서 트랜잭션 관리의 핵심 원칙은?

**A.**

**`@Transactional` 핵심 속성**:

| 속성 | 설명 | 기본값 |
|------|------|--------|
| `propagation` | 트랜잭션 전파 방식 | `REQUIRED` |
| `isolation` | 격리 수준 | DB 기본값 |
| `readOnly` | 읽기 전용 최적화 | `false` |
| `rollbackFor` | 롤백 트리거 예외 | `RuntimeException` |
| `timeout` | 타임아웃 (초) | -1 (무제한) |

**실무 원칙**:
1. **Service 계층에 선언**: Controller가 아닌 Service 메서드에 `@Transactional` 부여
2. **readOnly 활용**: 조회 전용 메서드에 `@Transactional(readOnly = true)` → Hibernate 더티체킹 비활성화, 레플리카 DB 라우팅
3. **self-invocation 주의**: 같은 클래스 내 메서드 호출은 프록시를 거치지 않아 트랜잭션 미적용
4. **Checked Exception 롤백**: `@Transactional(rollbackFor = Exception.class)` 명시 필요
5. **트랜잭션 범위 최소화**: 외부 API 호출은 트랜잭션 밖에서 수행

---

### Q13. Connection Pool은 어떻게 설정하나요? HikariCP의 핵심 설정값은?

**A.** Spring Boot 기본 Connection Pool인 HikariCP의 핵심 설정:

| 설정 | 권장값 | 설명 |
|------|--------|------|
| `maximum-pool-size` | 10~20 | 코어 수 × 2 + 디스크 수 (공식) |
| `minimum-idle` | = maximum-pool-size | 유휴 커넥션 유지 (고정 풀) |
| `connection-timeout` | 30000ms | 커넥션 획득 대기 시간 |
| `idle-timeout` | 600000ms | 유휴 커넥션 유지 시간 |
| `max-lifetime` | 1800000ms | 커넥션 최대 수명 (DB wait_timeout 보다 짧게) |
| `leak-detection-threshold` | 60000ms | 커넥션 누수 감지 |

**pool size 공식**: `connections = (core_count × 2) + effective_spindle_count`
- 4코어 서버 → 약 10개가 최적
- Pool이 너무 크면 컨텍스트 스위칭 오버헤드, 너무 작으면 대기 시간 증가

---

### Q14. 동시성 문제(Race Condition)를 해결하는 방법은?

**A.**

| 전략 | 메커니즘 | 장점 | 단점 |
|------|----------|------|------|
| **Optimistic Lock** | 버전 컬럼(`@Version`) | 충돌 적을 때 성능 우수 | 충돌 시 재시도 로직 필요 |
| **Pessimistic Lock** | `SELECT ... FOR UPDATE` | 확실한 동시성 제어 | 데드락 위험, 성능 저하 |
| **Distributed Lock** | Redis SETNX + TTL | 분산 환경 지원 | 구현 복잡, Redis 의존 |
| **Idempotency Key** | 고유 키로 중복 요청 방지 | API 레벨 멱등성 보장 | 키 관리 필요 |

```java
// JPA Optimistic Locking
@Entity
public class TrainingSession {
    @Version
    private Long version;
}

// JPA Pessimistic Locking
@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("SELECT s FROM TrainingSession s WHERE s.id = :id")
Optional<TrainingSession> findByIdForUpdate(@Param("id") Long id);
```

**선택 기준**: 읽기 많음 + 충돌 적음 → Optimistic, 금융/결제 → Pessimistic, 분산 서버 → Redis Lock

---

### Q15. Spring Boot에서 비동기 처리를 구현하는 방법을 비교해주세요.

**A.**

| 방법 | 구현 | 적합한 상황 |
|------|------|------------|
| `@Async` | `@EnableAsync` + ThreadPool 설정 | 간단한 비동기 작업 (이메일, 알림) |
| `CompletableFuture` | 체이닝 가능한 비동기 | 복수 비동기 작업 조합 |
| Kotlin Coroutines | `suspend fun`, `async/await` | Kotlin 프로젝트, 구조적 동시성 |
| Virtual Threads | `spring.threads.virtual.enabled=true` | Java 21+, I/O-bound 대량 동시 처리 |
| Message Queue | RabbitMQ, Kafka | 서비스 간 비동기, 내구성 필요 |

```kotlin
// Kotlin Coroutines 예시
@Service
class AnalysisService(private val aiClient: AIClient) {
    suspend fun analyzeSession(sessionId: Long): AnalysisResult = coroutineScope {
        val speechDeferred = async { aiClient.analyzeSpeech(sessionId) }
        val faceDeferred = async { aiClient.analyzeFace(sessionId) }
        val postureDeferred = async { aiClient.analyzePosture(sessionId) }

        AnalysisResult(
            speech = speechDeferred.await(),
            face = faceDeferred.await(),
            posture = postureDeferred.await()
        )
    }
}
```

---

### Q16. Java Virtual Threads와 전통적 Thread Pool의 차이는?

**A.**

| 비교 | Platform Threads | Virtual Threads |
|------|-----------------|-----------------|
| 구현 | OS 스레드 1:1 매핑 | JVM 관리 경량 스레드 |
| 메모리 | ~1MB 스택 | ~수 KB |
| 동시 수 | 수백~수천 | 수백만 |
| 블로킹 I/O | 스레드 점유 | 자동 일시 중단/재개 |
| 활성화 | 기본 | `spring.threads.virtual.enabled=true` |

**주의사항**:
1. **synchronized 핀닝**: `synchronized` 블록 내에서 Virtual Thread가 Carrier Thread에 고정 → `ReentrantLock` 사용 권장
2. **CPU-bound에는 부적합**: 연산 집약 작업은 Platform Thread가 더 효율적
3. **ThreadLocal 남용 금지**: 수백만 VT × ThreadLocal = 메모리 폭발
4. **극단적 동시성 시 에러율 증가**: 500+ 동시 요청 시 23~30% 에러율 관찰 보고

> 📎 출처: [Java Code Geeks - Virtual Threads Performance](https://www.javacodegeeks.com/2025/04/spring-boot-performance-with-java-virtual-threads.html)

---

### Q17. REST API의 보안을 어떻게 설계하나요? JWT vs Session 비교

**A.**

| 비교 | Session 기반 | JWT 기반 |
|------|-------------|----------|
| 상태 | Stateful (서버 세션 저장) | Stateless (토큰 자체에 정보) |
| 확장성 | 세션 공유 필요 (Redis 등) | 서버 간 공유 불필요 |
| 저장소 | 서버 메모리/Redis | 클라이언트 (쿠키/헤더) |
| 만료 | 서버에서 즉시 무효화 가능 | 만료 전 무효화 어려움 (블랙리스트 필요) |
| 보안 | CSRF 공격 취약 | XSS로 토큰 탈취 위험 |

**JWT 보안 베스트 프랙티스**:
1. **HttpOnly 쿠키에 저장**: localStorage는 XSS에 취약
2. **Access Token 짧게 (15분), Refresh Token 길게 (7일)**: 토큰 탈취 피해 최소화
3. **iss, aud, exp 클레임 검증**: Spring Security OAuth2 Resource Server가 자동 처리
4. **키 로테이션**: RSA/EC 키 정기 교체
5. **Rate Limiting**: 로그인 API에 요청 제한

```java
// Spring Security 설정 (SecurityFilterChain)
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    return http
        .csrf(csrf -> csrf.disable())  // API 서버의 경우
        .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
        .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/api/public/**").permitAll()
            .requestMatchers("/api/admin/**").hasRole("ADMIN")
            .anyRequest().authenticated())
        .build();
}
```

---

### Q18. 대용량 파일(영상/음성) 업로드 처리 아키텍처를 설계하세요.

**A.** 쏘카인드의 교육 영상/음성 파일 업로드 아키텍처:

```
Client                     Backend                      Storage
  │                          │                            │
  ├─ 1. 업로드 요청 ────────→│                            │
  │                          ├─ 2. Presigned URL 발급 ──→ S3
  │←── 3. Presigned URL ─────┤                            │
  │                          │                            │
  ├─ 4. 직접 업로드 (멀티파트) ──────────────────────────→ S3
  │                          │                            │
  │                          │←── 5. S3 Event ────────────┤
  │                          ├─ 6. 메타데이터 저장 (DB)     │
  │                          ├─ 7. AI 분석 작업 큐 등록     │
  │←── 8. 완료 알림 (SSE) ───┤                            │
```

**핵심 설계 원칙**:
1. **Presigned URL**: 서버 부하 없이 S3로 직접 업로드 → 서버 대역폭 절약
2. **멀티파트 업로드**: 대용량 파일을 청크로 분할, 실패 시 해당 청크만 재시도
3. **비동기 처리**: 업로드 완료 → Message Queue → AI 분석 Worker가 처리
4. **진행률 추적**: Redis에 업로드/분석 진행률 저장, SSE로 클라이언트에 실시간 전달

---

### Q19. 캐싱 전략을 설명하세요. Cache-Aside, Write-Through, Write-Behind 비교

**A.**

| 전략 | 동작 | 장점 | 단점 |
|------|------|------|------|
| **Cache-Aside** | 앱이 캐시 확인 → 미스 시 DB 조회 → 캐시 저장 | 구현 간단, 유연 | 캐시 미스 시 지연 |
| **Write-Through** | 쓰기 시 캐시+DB 동시 기록 | 데이터 일관성 보장 | 쓰기 지연 증가 |
| **Write-Behind** | 쓰기 시 캐시만 → 비동기 DB 반영 | 쓰기 성능 우수 | 데이터 유실 위험 |
| **Read-Through** | 캐시가 DB 조회 위임 | 앱 로직 단순화 | 캐시 라이브러리 의존 |

**Spring Boot + Redis 실무**:

```java
@Cacheable(value = "companyProfile", key = "#companyId", unless = "#result == null")
public CompanyProfile getCompany(Long companyId) { ... }

@CacheEvict(value = "companyProfile", key = "#companyId")
public void updateCompany(Long companyId, CompanyUpdateDto dto) { ... }
```

**TTL 전략**: 자주 변하는 데이터(세션 목록) → 짧은 TTL(5분), 거의 변하지 않는 데이터(회사 프로필) → 긴 TTL(1시간)

---

### Q20. Spring Boot 애플리케이션의 모니터링과 Observability를 어떻게 구축하나요?

**A.** Observability 3대 축: **Metrics, Logs, Traces**

| 축 | 도구 | Spring Boot 연동 |
|----|------|------------------|
| Metrics | Micrometer + Prometheus | `spring-boot-starter-actuator` |
| Logs | SLF4J + Logback → ELK/Loki | 구조화된 JSON 로깅 |
| Traces | OpenTelemetry + Jaeger/Zipkin | `micrometer-tracing` |

**핵심 메트릭**:
- **비즈니스**: 교육 세션 완료율, AI 분석 처리 시간, 활성 사용자 수
- **애플리케이션**: API 응답시간(p50/p95/p99), 에러율, 스루풋
- **인프라**: CPU, 메모리, DB 커넥션 풀 사용률, JVM GC 빈도

```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: health, prometheus, info
  metrics:
    tags:
      application: sokind-api
```

---

### Q21. Spring Boot에서 Rate Limiting을 구현하는 방법은?

**A.**

| 알고리즘 | 원리 | 적합한 상황 |
|----------|------|------------|
| **Fixed Window** | 고정 시간 창 내 요청 수 제한 | 단순, 경계 시점 burst 가능 |
| **Sliding Window** | 이동 시간 창 | 정밀한 제어 |
| **Token Bucket** | 일정 속도로 토큰 충전, 요청 시 소모 | 버스트 허용, API Gateway 표준 |
| **Leaky Bucket** | 일정 속도로 처리 | 일정한 처리율 보장 |

**구현 방식**:
1. **Spring Cloud Gateway**: `RequestRateLimiter` 필터 (Redis 기반)
2. **Bucket4j**: 인메모리 또는 Redis 분산 Rate Limiting
3. **Resilience4j**: `@RateLimiter` 어노테이션
4. **Nginx/API Gateway**: 인프라 레벨 제어

```java
// Bucket4j 예시
@Bean
public Bucket createBucket() {
    return Bucket.builder()
        .addLimit(Bandwidth.classic(100, Refill.intervally(100, Duration.ofMinutes(1))))
        .build();
}
```

---

### Q22. 마이크로서비스 vs 모놀리식, 초기 스타트업에서의 선택 기준은?

**A.**

| 비교 | 모놀리식 | 마이크로서비스 |
|------|----------|---------------|
| 배포 | 단일 배포 단위 | 서비스별 독립 배포 |
| 복잡도 | 낮음 | 분산 시스템 복잡도 |
| 팀 규모 | 소규모(2~10명) 적합 | 대규모(10명+) 적합 |
| 운영 비용 | 낮음 | 높음 (Service Mesh, 분산 추적 등) |
| 확장 | 전체 스케일 | 서비스별 독립 스케일 |

**초기 스타트업 권장**: **Modular Monolith**

```
┌─── Modular Monolith ──────────────────┐
│  ┌──────────┐  ┌──────────┐           │
│  │ 교육 모듈 │  │ AI 분석  │           │
│  │ (training)│  │ (analysis)│          │
│  └────┬─────┘  └────┬─────┘          │
│       │              │                │
│  ┌────┴──────────────┴─────┐         │
│  │     공유 인프라 (shared)   │         │
│  │  DB, Auth, Config        │         │
│  └──────────────────────────┘         │
│                                        │
│  → 나중에 모듈 경계를 따라 분리 가능    │
└────────────────────────────────────────┘
```

**이유**: 6~10명 팀에서 마이크로서비스는 운영 오버헤드가 제품 개발 속도를 압도. Spring Modulith로 모듈 경계를 명확히 하면 나중에 분리가 용이.

---

### Q23. API 응답 시간이 느릴 때 병목을 찾는 프로세스를 설명하세요.

**A.** 체계적 병목 분석 프로세스:

```
1. APM 확인 (전체 응답 시간 분포)
   │
   ├── p99 > 목표치? → 특정 API 식별
   │
2. 해당 API 트레이싱 (Span 분석)
   │
   ├── DB 쿼리 시간?  → EXPLAIN ANALYZE → 인덱스/쿼리 최적화
   ├── 외부 API 호출? → 타임아웃 설정, Circuit Breaker, 캐싱
   ├── 비즈니스 로직?  → 프로파일링 (VisualVM, async-profiler)
   │
3. DB 커넥션 풀 확인
   │
   ├── 풀 고갈?      → pool size 조정, 느린 쿼리 해결
   │
4. JVM 확인
   │
   ├── GC 빈도 높음?  → 힙 사이즈 조정, 객체 생성 최적화
   ├── Thread 고갈?    → Virtual Threads 또는 비동기 처리
```

---

### Q24. Database Migration을 안전하게 수행하는 방법은?

**A.** Flyway 또는 Liquibase를 사용한 버전 관리 기반 마이그레이션:

**안전한 마이그레이션 원칙**:

| 원칙 | 설명 |
|------|------|
| **Backward Compatible** | 새 스키마가 이전 코드와도 호환 |
| **Expand-Contract** | 추가 → 마이그레이션 → 삭제 (3단계) |
| **무중단** | `ALTER TABLE` 시 락 최소화 |
| **롤백 가능** | 각 마이그레이션에 롤백 스크립트 준비 |

```sql
-- V1: 컬럼 추가 (Expand)
ALTER TABLE users ADD COLUMN new_email VARCHAR(255);

-- 애플리케이션이 두 컬럼 모두 읽기 시작

-- V2: 데이터 마이그레이션
UPDATE users SET new_email = email WHERE new_email IS NULL;

-- V3: 이전 컬럼 삭제 (Contract) - 모든 서버가 새 코드일 때만
ALTER TABLE users DROP COLUMN email;
ALTER TABLE users RENAME COLUMN new_email TO email;
```

---

### Q25. Spring Boot에서 멀티 데이터소스를 구성하는 방법은?

**A.** 읽기/쓰기 분리(Read Replica) 구성:

```java
@Configuration
public class DataSourceConfig {
    @Bean
    @Primary
    public DataSource routingDataSource() {
        var routing = new AbstractRoutingDataSource() {
            @Override
            protected Object determineCurrentLookupKey() {
                return TransactionSynchronizationManager.isCurrentTransactionReadOnly()
                    ? "replica" : "primary";
            }
        };
        routing.setTargetDataSources(Map.of(
            "primary", primaryDataSource(),
            "replica", replicaDataSource()
        ));
        return routing;
    }
}
```

**활용 시나리오**:
- `@Transactional(readOnly = true)` → 자동으로 Replica DB로 라우팅
- 쓰기 작업 → Primary DB로 라우팅
- AI 분석 리포트 조회(대량 읽기) → Replica에서 처리하여 Primary 부하 감소

---

### Q26. API 설계 시 멱등성(Idempotency)을 어떻게 보장하나요?

**A.**

| HTTP 메서드 | 기본 멱등성 | 추가 처리 필요 |
|------------|-----------|---------------|
| GET | ✅ 멱등 | 불필요 |
| PUT | ✅ 멱등 | 불필요 (전체 교체) |
| DELETE | ✅ 멱등 | 불필요 (없으면 404) |
| POST | ❌ 비멱등 | **Idempotency Key 필요** |
| PATCH | ❌ 비멱등 | 경우에 따라 필요 |

**Idempotency Key 구현**:
1. 클라이언트가 고유 `Idempotency-Key` 헤더를 포함하여 요청
2. 서버가 Redis에 키 존재 여부 확인
3. 이미 존재 → 저장된 이전 응답 반환
4. 미존재 → 처리 후 결과를 Redis에 TTL과 함께 저장

---

### Q27. Graceful Shutdown을 구현하는 방법과 중요성은?

**A.** 배포 시 진행 중인 요청이 완료될 때까지 기다린 후 서버를 종료:

```yaml
server:
  shutdown: graceful

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```

**동작 흐름**:
1. SIGTERM 수신 → 새 요청 거부 시작
2. 진행 중인 요청 완료 대기 (최대 30초)
3. 타임아웃 시 강제 종료
4. DB 커넥션 풀, 메시지 큐 연결 정리

**중요한 이유**: AI 분석 작업 중간에 서버가 죽으면 데이터 일관성 문제. 메시지 큐의 ACK 전 종료 시 메시지 유실 가능.

---

### Q28. Spring Boot 애플리케이션의 보안 취약점 Top 5와 대응 방법은?

**A.**

| # | 취약점 | 대응 |
|---|--------|------|
| 1 | **SQL Injection** | PreparedStatement (JPA 기본 제공), 네이티브 쿼리 시 파라미터 바인딩 필수 |
| 2 | **XSS** | 입력 검증, 출력 인코딩, CSP 헤더 설정 |
| 3 | **CSRF** | Stateless API는 비활성화, SPA+세션 시 CSRF 토큰 |
| 4 | **인증/인가 우회** | Method Security(`@PreAuthorize`), URL 패턴 화이트리스트 |
| 5 | **민감정보 노출** | Actuator 엔드포인트 보호, 에러 응답에 스택트레이스 제거 |

```yaml
# Actuator 보안 설정
management:
  endpoints:
    web:
      exposure:
        include: health, info  # 최소한만 노출
  endpoint:
    health:
      show-details: when-authorized
```

---

### Q29. CORS 설정의 원리와 Spring Boot에서의 구현 방법은?

**A.** CORS(Cross-Origin Resource Sharing)는 브라우저가 다른 도메인의 API를 호출할 때의 보안 메커니즘:

**Preflight 요청 흐름**:
```
Browser                              Server
   ├─ OPTIONS /api/users ──────────→ │
   │  Origin: https://app.sokind.ai  │
   │                                  │
   │←── Access-Control-Allow-Origin ──┤
   │    Access-Control-Allow-Methods  │
   │                                  │
   ├─ GET /api/users ─────────────→ │  (실제 요청)
```

```java
@Configuration
public class CorsConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOrigins("https://app.sokind.ai", "https://admin.sokind.ai")
            .allowedMethods("GET", "POST", "PUT", "DELETE")
            .allowedHeaders("*")
            .allowCredentials(true)
            .maxAge(3600);  // preflight 캐시 1시간
    }
}
```

---

### Q30. Spring Boot 3.x의 주요 변경사항과 마이그레이션 포인트는?

**A.**

| 변경사항 | Spring Boot 2.x | Spring Boot 3.x |
|----------|-----------------|-----------------|
| Java 버전 | Java 8+ | **Java 17+** (필수) |
| 패키지 | `javax.*` | **`jakarta.*`** |
| Spring Security | `WebSecurityConfigurerAdapter` | **`SecurityFilterChain` Bean** |
| Observability | 개별 설정 | **Micrometer Observation API** 통합 |
| Native Image | 실험적 | **GraalVM Native 공식 지원** |
| ProblemDetail | 미지원 | **RFC 7807 에러 응답** 기본 지원 |

**마이그레이션 핵심 체크리스트**:
1. `javax` → `jakarta` 패키지 전환
2. Security 설정 방식 변경
3. 의존 라이브러리 Jakarta EE 호환 버전 확인
4. Spring Boot 3.2+에서 Virtual Threads 지원

---

## 🟠 Tier 2: 팀 리딩 및 개발 문화/프로세스 (#31~55)

---

### Q31. 효과적인 코드 리뷰 문화를 어떻게 만드나요?

**A.**

**코드 리뷰 원칙**:
1. **PR 크기 제한**: 400줄 이하 (대규모 변경은 분할)
2. **리뷰 시간 SLA**: 비즈니스 시간 내 24시간 이내 첫 리뷰
3. **자동화 우선**: 린트, 포맷, 테스트는 CI에서 자동 검증 → 리뷰어는 로직/설계에 집중
4. **건설적 피드백**: "이렇게 하면 안 됩니다" → "이렇게 하면 어떨까요? 이유는..."
5. **레이블 체계**: `[Nit]` 사소한 제안, `[Must]` 반드시 수정, `[Question]` 질문

**리뷰 체크리스트**:
- 비즈니스 로직 정확성
- 엣지 케이스 처리
- 보안 취약점 (입력 검증, 인증)
- 성능 영향 (쿼리 수, 복잡도)
- 테스트 커버리지

---

### Q32. 기술 부채를 식별하고 관리하는 프로세스를 설명하세요.

**A.**

**기술 부채 분류 체계**:

| 유형 | 예시 | 긴급도 |
|------|------|--------|
| **의도적 부채** | "지금은 단순하게, 나중에 리팩토링" | 📋 백로그 등록 |
| **비의도적 부채** | 잘못된 설계가 누적 | 🔴 즉시 대응 |
| **환경 부채** | 라이브러리 EOL, 보안 패치 미적용 | 🟡 정기 점검 |
| **테스트 부채** | 테스트 커버리지 부족 | 🟠 점진적 개선 |

**관리 프로세스**:
1. **정량화**: SonarQube로 코드 복잡도, 중복, 커버리지 측정
2. **우선순위**: (영향 범위 × 변경 빈도 × 위험도)로 점수화
3. **20% 규칙**: 매 스프린트 20%를 기술 부채 해소에 투자
4. **Tech Debt Day**: 분기별 1일을 기술 부채 집중 해소에 배정
5. **ADR 기록**: 부채를 만든 결정과 향후 해결 계획을 Architecture Decision Record에 기록

> 📎 출처: [LeadDev - Building Roadmaps for Tech Debt](https://leaddev.com/legacy-technical-debt-migrations/building-realistic-roadmaps-tech-debt-cleanup)

---

### Q33. 개발팀의 기술 방향성을 어떻게 설정하나요?

**A.**

**기술 로드맵 수립 프로세스**:
1. **현황 진단**: 현재 기술 스택, 장단점, 통증점 파악
2. **비즈니스 정렬**: 6개월/1년 비즈니스 목표에 필요한 기술 역량 도출
3. **RFC(Request for Comments)**: 주요 기술 결정을 문서화하여 팀 전체 의견 수렴
4. **PoC(Proof of Concept)**: 후보 기술을 소규모 실험으로 검증
5. **점진적 도입**: Big-Bang 전환이 아닌 점진적 마이그레이션
6. **분기별 회고**: 로드맵 대비 진행률 점검 및 조정

---

### Q34. CI/CD 파이프라인을 어떻게 설계하나요?

**A.**

```
┌─ Developer ─┐
│ git push     │
└──────┬───────┘
       ▼
┌─ CI Pipeline ──────────────────────────┐
│ 1. Build (Gradle)                       │
│ 2. Unit Test                            │
│ 3. Integration Test (Testcontainers)    │
│ 4. Static Analysis (SonarQube)          │
│ 5. Docker Image Build & Push            │
└──────────────┬──────────────────────────┘
               ▼
┌─ CD Pipeline ──────────────────────────┐
│ 6. Deploy to Staging                    │
│ 7. Smoke Test / E2E Test               │
│ 8. Manual Approval (Production)         │
│ 9. Blue-Green / Canary Deploy           │
│ 10. Health Check & Rollback Trigger     │
└─────────────────────────────────────────┘
```

**핵심 원칙**:
- **Fast Feedback**: 빌드+단위테스트 3분 이내
- **환경 동일성**: Docker로 로컬/CI/프로덕션 환경 일치
- **Immutable Deploy**: 이미지 한번 빌드 → 여러 환경에 배포
- **자동 롤백**: 헬스체크 실패 시 이전 버전으로 자동 롤백

---

### Q35. 배포 전략을 비교해주세요 (Blue-Green, Canary, Rolling)

**A.**

| 전략 | 원리 | 장점 | 단점 |
|------|------|------|------|
| **Blue-Green** | 두 환경 교대 운영 | 즉시 롤백 가능 | 2배 인프라 비용 |
| **Canary** | 일부 트래픽만 새 버전 | 점진적 검증 | 라우팅 로직 필요 |
| **Rolling** | 인스턴스 순차 교체 | 리소스 효율적 | 롤백 느림, 버전 혼재 |

**쏘카인드 추천**: 소규모 팀 → **Blue-Green** (단순하고 롤백이 확실)

---

### Q36. 팀원의 기술 성장을 어떻게 지원하나요?

**A.**

| 활동 | 빈도 | 목적 |
|------|------|------|
| **1:1 미팅** | 격주 | 기술 고민, 커리어 방향, 블로커 해소 |
| **Pair Programming** | 수시 | 복잡한 기능, 신규 팀원 온보딩 |
| **Tech Talk** | 격주 | 팀원이 돌아가며 학습한 기술 공유 |
| **코드 리뷰 멘토링** | 매일 | 리뷰에서 "왜" 중심의 피드백 |
| **도전 과제 부여** | 분기 | 성장 영역에 맞는 기능 담당 배정 |

---

### Q37. Agile/Scrum에서 기술 팀 리드로서 스프린트를 어떻게 운영하나요?

**A.**

| 행사 | 주기 | 리드 역할 |
|------|------|----------|
| **Sprint Planning** | 2주 초 | 기술 복잡도 판단, 스토리 분할 지원 |
| **Daily Standup** | 매일 15분 | 블로커 해소, 기술적 의사결정 |
| **Sprint Review** | 2주 말 | 기술 데모, 기술 부채 현황 공유 |
| **Retrospective** | 2주 말 | 프로세스 개선점 도출 |
| **Backlog Refinement** | 매주 | 기술 스토리 작성, 기술 부채 항목 추가 |

**핵심 원칙**: "완벽함보다 실행 속도" → MVP로 빠르게 검증 후 개선

---

### Q38. 개발 문서를 어떻게 관리하나요? 어떤 문서를 작성하나요?

**A.**

| 문서 유형 | 목적 | 형식 |
|-----------|------|------|
| **ADR** (Architecture Decision Record) | 기술 결정과 이유 기록 | Markdown, 번호 부여 |
| **API 명세** | API 계약 정의 | OpenAPI/Swagger |
| **온보딩 가이드** | 신규 팀원 환경 설정 | README/Wiki |
| **운영 문서** | 배포 절차, 장애 대응 | Runbook 형식 |
| **설계 문서** | 기능별 기술 설계 | RFC 템플릿 |

**ADR 예시**:
```markdown
# ADR-003: LLM 제공자 추상화 레이어 도입
- 상태: Accepted
- 일자: 2026-03-22
- 결정: Spring AI ChatClient 인터페이스로 LLM 제공자 추상화
- 이유: GPT ↔ Gemini 전환 가능성, 비용 최적화
- 결과: 새 LLM 추가 시 Adapter만 구현
```

---

### Q39. Git 브랜치 전략을 설계하세요.

**A.** 소규모 팀(6~10명)에 적합한 **Trunk-Based Development**:

```
main ─────●─────●─────●─────●─────●──→ (항상 배포 가능)
           ╲   ╱ ╲   ╱       ╲   ╱
            ╲ ╱   ╲ ╱         ╲ ╱
feature/   ──●─    ──●──       ──●──    (수명 1~2일)
```

| 원칙 | 설명 |
|------|------|
| **Short-lived Branch** | feature 브랜치 수명 1~2일 |
| **Trunk에 자주 머지** | 하루 최소 1회 main에 통합 |
| **Feature Flag** | 미완성 기능은 플래그로 비활성화 |
| **CI 필수** | main 머지 전 모든 테스트 통과 |

---

### Q40. 서비스 장애 대응 프로세스를 설계하세요.

**A.**

```
장애 감지 → 공유 채널 알림 → 심각도 판정 → 대응 → 복구 → 포스트모템
```

| 심각도 | 기준 | 대응 시간 |
|--------|------|-----------|
| **P1 Critical** | 서비스 전체 중단 | 즉시 (15분 내) |
| **P2 Major** | 핵심 기능 장애 | 30분 내 |
| **P3 Minor** | 부분 기능 이상 | 업무 시간 내 |
| **P4 Low** | 사소한 이슈 | 다음 스프린트 |

**포스트모템 필수 항목**: 타임라인, 근본 원인, 영향 범위, 재발 방지 조치

---

### Q41. 설계 문서(Design Doc/RFC)를 어떻게 작성하나요?

**A.**

```markdown
# RFC: [기능/변경 제목]
## 1. 배경 및 동기
## 2. 목표 (Goals / Non-Goals)
## 3. 제안하는 설계
   - 아키텍처 다이어그램
   - API 변경사항
   - 데이터 모델 변경
## 4. 대안 검토 (Alternatives Considered)
## 5. 보안/성능 고려사항
## 6. 마이그레이션 계획
## 7. 테스트 계획
## 8. 타임라인
```

**RFC 프로세스**: 작성 → 팀 공유(3영업일 리뷰) → 피드백 반영 → 승인 → 구현

---

### Q42. 새로운 기술을 도입할 때의 의사결정 프로세스는?

**A.**

| 단계 | 활동 | 산출물 |
|------|------|--------|
| 1. 문제 정의 | 현재 기술로 해결 안 되는 이유 명확화 | 문제 정의서 |
| 2. 후보 선정 | 2~3개 후보 기술 비교 | 비교 매트릭스 |
| 3. PoC | 작은 범위에서 검증 (1~2주) | PoC 결과 보고서 |
| 4. 팀 합의 | RFC 작성 + 팀 투표 | ADR |
| 5. 점진 도입 | 비핵심 서비스부터 적용 | 마이그레이션 계획 |
| 6. 회고 | 도입 결과 평가 | 회고 문서 |

---

### Q43. 기술 면접에서 "완벽함보다 실행 속도를 우선시"한다는 것은 구체적으로 무엇을 의미하나요?

**A.**

| 상황 | ❌ 과도한 완벽주의 | ✅ 실행 속도 우선 |
|------|-------------------|------------------|
| 설계 | 모든 엣지케이스 사전 설계 | 핵심 flow 먼저 구현 → 피드백 반영 |
| 코드 품질 | 완벽한 추상화 | 동작하는 코드 → 리팩토링 |
| 기술 선택 | 6개월 비교 분석 | 1주 PoC → 결정 → 전진 |
| 배포 | 모든 테스트 완료까지 대기 | Feature Flag로 먼저 배포 → 점진적 활성화 |

**핵심**: "질러놓고 고치는 것"이 아니라, "최소한의 품질을 보장하면서 빠르게 가치를 전달"하는 것.

---

### Q44. 개발팀의 생산성을 측정하는 지표는?

**A.** DORA Metrics (DevOps Research and Assessment):

| 지표 | 설명 | 엘리트 수준 |
|------|------|------------|
| **Deployment Frequency** | 프로덕션 배포 빈도 | 하루 여러 번 |
| **Lead Time for Changes** | 커밋→배포 소요 시간 | 1시간 미만 |
| **Change Failure Rate** | 배포 후 장애 비율 | 0~15% |
| **Time to Restore** | 장애 복구 시간 | 1시간 미만 |

+ **추가 지표**: PR 리뷰 시간, 빌드 성공률, 기술 부채 지수 (SonarQube)

---

### Q45. 팀 내 기술 표준화를 어떻게 추진하나요?

**A.**

| 영역 | 표준화 항목 | 도구 |
|------|------------|------|
| 코드 스타일 | 포맷팅, 네이밍 규칙 | ktlint, EditorConfig |
| API 설계 | 응답 포맷, 에러 코드 체계 | OpenAPI spec |
| 로깅 | 구조화된 로그 포맷, 로그 레벨 | Logback MDC |
| 테스트 | 테스트 네이밍, 최소 커버리지 | JaCoCo, CI gate |
| 커밋 | Conventional Commits | commitlint |

---

### Q46. 비개발 직군(PM, 디자이너, 세일즈)과 효과적으로 소통하는 방법은?

**A.**

| 대상 | 소통 포인트 | 방법 |
|------|------------|------|
| **PM** | 기술 제약/일정 영향, trade-off 설명 | "A를 하면 2주, B를 하면 1주. B의 제약은..." |
| **디자이너** | 기술적 구현 가능성, 성능 영향 | "이 애니메이션은 모바일에서 60fps 유지 어려움" |
| **세일즈** | 기능 가용 시점, 커스터마이징 범위 | "이 기능은 다음 릴리스(3주 후)에 포함" |
| **FE** | API 계약, 에러 처리 방식 | OpenAPI spec 공유, mock server 제공 |

**원칙**: 기술 용어를 비즈니스 영향으로 번역. "DB 락 → 동시에 같은 데이터를 수정하면 충돌 방지 로직이 필요해서 개발 시간 추가 필요"

---

### Q47. 온보딩 프로세스를 어떻게 설계하나요?

**A.**

| 시점 | 활동 | 목표 |
|------|------|------|
| **Day 1** | 환경 설정, 계정 발급, 아키텍처 개요 | 로컬에서 서비스 실행 |
| **Week 1** | 코드베이스 탐색, 작은 버그 수정 | 첫 PR 머지 |
| **Week 2** | 작은 기능 개발 + 코드 리뷰 | 개발 프로세스 체화 |
| **Month 1** | 중규모 기능 담당 + 페어 프로그래밍 | 독립적 개발 가능 |
| **Month 2~3** | 설계 참여 + 코드 리뷰어 역할 | 팀 기여 |

---

### Q48. 레거시 코드를 리팩토링하는 접근 방법은?

**A.** **Strangler Fig 패턴**:

```
┌─── 레거시 시스템 ───┐
│ Module A (변경 잦음) │ ← 새 코드로 교체
│ Module B (안정적)    │ ← 유지
│ Module C (변경 잦음) │ ← 새 코드로 교체
└─────────────────────┘
```

**리팩토링 원칙**:
1. **테스트 먼저**: 리팩토링 전 기존 동작을 보장하는 테스트 추가
2. **작은 단위**: 한번에 하나의 변경. 매 변경마다 테스트 통과 확인
3. **변경 빈도 높은 모듈 우선**: 자주 수정하는 코드 = ROI 높음
4. **Boy Scout Rule**: "지나간 코드를 이전보다 깨끗하게" (매번 조금씩 개선)

---

### Q49. 기술 의사결정에서 trade-off를 어떻게 분석하나요?

**A.** 구조화된 trade-off 분석 프레임워크:

| 단계 | 활동 |
|------|------|
| 1. 제약 조건 정리 | 시간, 인력, 비용, 기술 부채 허용치 |
| 2. 평가 기준 정의 | 성능, 유지보수성, 학습 곡선, 커뮤니티 |
| 3. 가중치 부여 | 비즈니스 우선순위에 따라 |
| 4. 후보별 점수화 | 각 기준에 1~5점 |
| 5. 의사결정 기록 | ADR에 결정과 이유 기록 |

---

### Q50. "유저 경험에 대한 집착"을 백엔드 엔지니어로서 어떻게 실현하나요?

**A.**

| 영역 | 실현 방법 |
|------|----------|
| **응답 속도** | p95 < 200ms 목표, 느린 API 즉시 개선 |
| **에러 메시지** | 유저가 이해할 수 있는 에러 메시지 + 코드 |
| **일관성** | API 응답 포맷 통일, 페이지네이션 표준화 |
| **안정성** | Circuit Breaker로 외부 장애 전파 차단 |
| **실시간 피드백** | AI 분석 진행률을 SSE로 실시간 전달 |

---

### Q51. 기술 로드맵을 수립하는 방법을 설명하세요.

**A.**

| 시간축 | 내용 |
|--------|------|
| **Now (이번 분기)** | 긴급 기술 부채, 당장 필요한 인프라 |
| **Next (다음 분기)** | 중기 아키텍처 개선, 성능 최적화 |
| **Later (6개월+)** | 장기 전략 (마이크로서비스 전환, 새 기술 도입) |

**비즈니스 연계**: "해외 진출(Next) → 다국어 지원 인프라(Now) → CDN 글로벌 설정(Now)"

---

### Q52. 코드 품질을 자동으로 관리하는 방법은?

**A.**

| 도구 | 역할 | CI 단계 |
|------|------|---------|
| **ktlint** | Kotlin 코드 스타일 검사 | Build |
| **SonarQube** | 코드 복잡도, 보안 취약점, 중복 | Build 후 |
| **JaCoCo** | 테스트 커버리지 측정 | Test 후 |
| **Dependency Check** | 의존성 보안 취약점 | Build |
| **Detekt** | Kotlin 정적 분석 | Build |

**CI Quality Gate**: 커버리지 80% 미만, 심각 이슈 1건 이상이면 빌드 실패

---

### Q53. 개발자 경험(Developer Experience)을 개선하는 방법은?

**A.**

| 영역 | 개선 방법 |
|------|----------|
| **로컬 개발** | Docker Compose로 전체 환경 1분 내 구동 |
| **빌드 속도** | Gradle Build Cache, 병렬 테스트 실행 |
| **디버깅** | 구조화된 로그, Correlation ID |
| **문서** | API 문서 자동 생성 (Swagger), 코드 주석 최소화 |
| **CI 속도** | 단위 테스트 3분 이내, 전체 파이프라인 10분 이내 |

---

### Q54. A/B 테스트를 백엔드에서 어떻게 지원하나요?

**A.**

```
Request → Feature Flag Service (Redis) → 사용자 그룹 판정
                                           │
                                    ┌──────┴──────┐
                                    │ Group A      │ Group B
                                    │ (기존 로직)  │ (새 로직)
                                    └──────────────┘
```

**구현**: Feature Flag 라이브러리(Unleash, LaunchDarkly) 또는 Redis 기반 자체 구현
**핵심**: 유저별 일관성(같은 유저는 항상 같은 그룹), 비율 조절 가능, 결과 메트릭 수집

---

### Q55. 프로덕션 환경에서의 로깅 전략을 설계하세요.

**A.**

| 레벨 | 용도 | 예시 |
|------|------|------|
| **ERROR** | 서비스 장애, 데이터 정합성 문제 | DB 커넥션 실패, AI 모델 응답 오류 |
| **WARN** | 잠재적 문제, 비정상 동작 | 재시도 발생, 임계치 초과 |
| **INFO** | 핵심 비즈니스 이벤트 | 교육 세션 시작/완료, 사용자 로그인 |
| **DEBUG** | 개발 시 상세 정보 | 프로덕션에서 비활성화 |

**구조화된 로그 (JSON)**:
```json
{
  "timestamp": "2026-03-22T10:30:00Z",
  "level": "INFO",
  "service": "sokind-api",
  "traceId": "abc123",
  "userId": 42,
  "message": "Training session completed",
  "sessionId": 1001,
  "duration_ms": 3500
}
```

---

## 🟡 Tier 3: 우대사항 기술 영역 (#56~80)

---

### Q56. Java와 Kotlin의 핵심 차이와 Kotlin을 선호하는 이유는?

**A.**

| 비교 | Java | Kotlin |
|------|------|--------|
| Null 안전성 | `Optional`, `@Nullable` | **언어 레벨 `?` 타입** |
| 보일러플레이트 | Getter/Setter, Builder 필요 | **data class로 자동 생성** |
| 코루틴 | 없음 (Virtual Threads 대안) | **suspend/async/await** |
| 확장 함수 | 없음 | **기존 클래스에 함수 추가** |
| 표현력 | 장황 | **간결 (30~40% 코드 감소)** |
| 호환성 | - | **Java 100% 상호 운용** |

---

### Q57. Kotlin의 Null Safety가 실무에서 어떻게 도움이 되나요?

**A.**

```kotlin
// Kotlin: 컴파일 타임에 NPE 방지
fun getUserEmail(user: User?): String {
    return user?.email ?: "default@sokind.ai"  // Safe call + Elvis
}

// Java: 런타임 NPE 위험
public String getUserEmail(User user) {
    return user.getEmail();  // user가 null이면 NPE!
}
```

**실무 이점**:
1. NullPointerException 대부분 제거 (컴파일 에러로 전환)
2. `?.`, `?:`, `!!` 연산자로 의도를 명확히 표현
3. `let`, `also`, `apply` 스코프 함수와 결합하여 null 처리 간결화

---

### Q58. JPA와 Exposed의 차이를 설명하세요.

**A.**

| 비교 | JPA (Hibernate) | Exposed |
|------|-----------------|---------|
| 언어 | Java 중심 | **Kotlin 네이티브** |
| DSL | JPQL (문자열) | **타입 안전 SQL DSL** |
| 모드 | ORM (Entity 매핑) | **DSL + DAO 모드 선택** |
| 학습 곡선 | 높음 (프록시, 캐시 등) | 상대적으로 낮음 |
| 생태계 | 매우 넓음, Spring 완벽 통합 | 제한적, JetBrains 개발 |
| 코루틴 | 제한적 | **네이티브 지원** |

```kotlin
// Exposed DSL 예시
object TrainingSessions : Table() {
    val id = long("id").autoIncrement()
    val userId = long("user_id")
    val score = integer("score")
    override val primaryKey = PrimaryKey(id)
}

// 타입 안전 쿼리
TrainingSessions.select { TrainingSessions.userId eq 42 }
    .orderBy(TrainingSessions.score, SortOrder.DESC)
```

---

### Q59. Spring Boot에서 단위 테스트와 통합 테스트를 어떻게 구분하나요?

**A.**

| 구분 | 단위 테스트 | 통합 테스트 |
|------|-----------|------------|
| 범위 | 단일 클래스/메서드 | 여러 레이어 통합 |
| 의존성 | Mock (Mockito) | 실제 DB, 외부 서비스 |
| 속도 | 매우 빠름 (ms) | 느림 (초) |
| 도구 | JUnit + Mockito | `@SpringBootTest` + Testcontainers |
| 비율 | 60% | 30% |

```kotlin
// 단위 테스트
@Test
fun `should calculate session score correctly`() {
    val service = ScoreService(mockAnalysisRepo)
    every { mockAnalysisRepo.findBySessionId(1L) } returns mockAnalysis

    val score = service.calculateScore(1L)
    assertThat(score).isEqualTo(85)
}

// 통합 테스트 (Testcontainers)
@SpringBootTest
@Testcontainers
class SessionControllerIntegrationTest {
    @Container
    val postgres = PostgreSQLContainer("postgres:16")

    @Test
    fun `should create training session`() {
        mockMvc.post("/api/v1/sessions") {
            contentType = MediaType.APPLICATION_JSON
            content = """{"userId": 1, "companyId": 42}"""
        }.andExpect { status { isCreated() } }
    }
}
```

---

### Q60. Testcontainers를 사용하는 이유와 장점은?

**A.**

**문제**: H2 인메모리 DB로 테스트 → 프로덕션(PostgreSQL)에서 실패하는 케이스 발생
**해결**: Testcontainers로 **실제 PostgreSQL Docker 컨테이너**를 테스트에서 사용

| 장점 | 설명 |
|------|------|
| **프로덕션 동일** | 같은 DB 엔진, 같은 버전 |
| **격리** | 테스트마다 새 컨테이너 → 데이터 오염 없음 |
| **외부 서비스** | Redis, Kafka, LocalStack 등 모두 컨테이너로 |
| **CI 호환** | Docker만 있으면 어디서든 실행 |

---

### Q61. 멀티모듈 프로젝트를 어떻게 설계하나요?

**A.**

```
sokind-backend/
├── api/              ← REST Controller, DTO, Swagger
├── core/             ← 도메인 모델, 비즈니스 로직
├── persistence/      ← JPA Entity, Repository, Migration
├── ai-client/        ← AI 모델 API 클라이언트
├── notification/     ← 알림 서비스 (Email, Push)
├── shared/           ← 공통 유틸, 상수, 예외
└── app/              ← Spring Boot main, 설정, 조합
```

**핵심 규칙**:
1. **의존 방향**: `app → api → core ← persistence`, core는 외부 의존 없음
2. **순환 의존 금지**: Gradle에서 자동 감지
3. **모듈별 테스트**: 각 모듈이 독립적으로 테스트 가능
4. **버전 중앙 관리**: `gradle/libs.versions.toml` (Version Catalog)

> 📎 출처: [Bootify - Multi-Module Best Practices](https://bootify.io/multi-module/best-practices-for-spring-boot-multi-module.html)

---

### Q62. Spring Modulith와 전통적 멀티모듈의 차이는?

**A.**

| 비교 | 전통적 멀티모듈 | Spring Modulith |
|------|----------------|-----------------|
| 모듈 경계 | Gradle/Maven 모듈 | **패키지 구조** 기반 |
| 의존성 제어 | build.gradle에서 관리 | **ArchUnit 기반 자동 검증** |
| 이벤트 | 직접 구현 | **ApplicationEvent 통합** |
| 문서화 | 수동 | **자동 모듈 다이어그램 생성** |
| 적합한 규모 | 대규모, 분리 배포 필요 | 중소규모, 논리적 분리 |

---

### Q63. WebSocket과 SSE(Server-Sent Events)의 차이와 선택 기준은?

**A.**

| 비교 | WebSocket | SSE |
|------|-----------|-----|
| 통신 방향 | **양방향** | **서버→클라이언트 단방향** |
| 프로토콜 | ws:// (별도 프로토콜) | HTTP (표준) |
| 재연결 | 수동 구현 | **자동 재연결 내장** |
| 인프라 호환 | 프록시/LB 설정 필요 | HTTP 기반으로 호환 우수 |
| 적합한 상황 | 채팅, 게임, 양방향 필요 | **LLM 스트리밍, 알림, 진행률** |

**쏘카인드 적용**:
- AI 리포트 스트리밍 → **SSE** (서버→클라이언트, LLM 응답 스트리밍 표준)
- WebRTC 시그널링 → **WebSocket** (양방향 SDP/ICE 교환 필요)

---

### Q64. WebRTC 시그널링 서버를 Spring Boot로 어떻게 구현하나요?

**A.**

```
┌─ Client A ─┐                  ┌─ Client B ─┐
│   Browser   │                  │   Browser   │
│ getUserMedia│                  │ getUserMedia│
└──────┬──────┘                  └──────┬──────┘
       │ WebSocket                       │ WebSocket
       ▼                                 ▼
┌─────────────── Spring Boot Signaling Server ──────────────┐
│  1. Client A → SDP Offer → Server → Forward → Client B   │
│  2. Client B → SDP Answer → Server → Forward → Client A  │
│  3. Both → ICE Candidates → Server → Exchange → Both      │
│  4. P2P Connection Established (서버 불필요)                │
└────────────────────────────────────────────────────────────┘
```

**핵심 구성**:
- `@ServerEndpoint` 또는 Spring WebSocket(`@MessageMapping`) 사용
- STUN 서버: NAT 뒤의 공인 IP 확인 (Google 무료 STUN 서버 활용)
- TURN 서버: P2P 불가 시 릴레이 (자체 운영 또는 Twilio/Xirsys)

---

### Q65. Redis를 활용한 세션 관리와 캐싱 전략을 설명하세요.

**A.**

| 용도 | Redis 자료구조 | TTL | 예시 |
|------|---------------|-----|------|
| **HTTP 세션** | Hash | 30분 | Spring Session Redis |
| **API 캐싱** | String (JSON) | 5분~1시간 | 고객사 프로필, 교육 과정 목록 |
| **분산 락** | String (SETNX) | 10초 | 동시 AI 분석 방지 |
| **Rate Limiting** | String (INCR) | 1분 | API 요청 횟수 제한 |
| **실시간 진행률** | String | 10분 | AI 분석 진행률 (SSE로 조회) |
| **리더보드** | Sorted Set | 영구 | 교육 점수 랭킹 |

---

### Q66. Kotlin Coroutines의 Structured Concurrency를 설명하세요.

**A.** Structured Concurrency는 코루틴의 생명주기를 계층적으로 관리하여 **리소스 누수를 방지**:

```kotlin
suspend fun processSession(sessionId: Long) = coroutineScope {
    // 자식 코루틴들: 부모가 취소되면 모두 취소됨
    val speech = async { analyzeSpeech(sessionId) }     // 자식 1
    val face = async { analyzeFace(sessionId) }         // 자식 2

    // 하나가 실패하면 다른 것도 취소 (Structured)
    try {
        combineResults(speech.await(), face.await())
    } catch (e: Exception) {
        // speech 실패 → face도 자동 취소
        throw e
    }
}
```

**핵심 원칙**:
1. 부모 코루틴이 취소되면 모든 자식도 취소
2. 자식 코루틴이 실패하면 부모에게 전파
3. `coroutineScope`는 모든 자식 완료까지 대기

---

### Q67. Spring Boot에서 WebFlux vs MVC 선택 기준은?

**A.**

| 선택 기준 | Spring MVC | Spring WebFlux |
|-----------|-----------|----------------|
| I/O 패턴 | 블로킹 I/O 대부분 | **논블로킹 I/O 필요** |
| 동시 접속 | 수백~수천 | **수만~수십만** |
| 기존 코드 | JPA/JDBC 사용 중 | R2DBC/Reactive Mongo |
| 팀 역량 | 명령형 프로그래밍 익숙 | **리액티브 패러다임 이해** |
| 디버깅 | 스택트레이스 직관적 | 스택트레이스 읽기 어려움 |
| Java 21+ | **Virtual Threads**로 고동시성 해결 | - |

**쏘카인드 권장**: Spring MVC + Virtual Threads. 이유: JPA 사용, 소규모 팀 학습 곡선 고려, Java 21 Virtual Threads로 충분한 동시성 확보.

---

### Q68. JPA의 영속성 컨텍스트(Persistence Context)를 설명하세요.

**A.** 영속성 컨텍스트는 **엔티티를 관리하는 1차 캐시**:

```
┌─── 영속성 컨텍스트 (EntityManager) ───┐
│                                        │
│  1차 캐시: { id=1: UserEntity }        │
│                                        │
│  Dirty Checking: 변경 감지             │
│  → flush 시 UPDATE SQL 자동 생성       │
│                                        │
│  Write Behind: SQL을 모아서 실행       │
│                                        │
│  Identity 보장: 같은 ID = 같은 객체    │
└────────────────────────────────────────┘
```

**생명주기**: New → Managed → Detached → Removed

---

### Q69. 데이터베이스 정규화와 비정규화의 판단 기준은?

**A.**

| 정규화 | 비정규화 |
|--------|----------|
| 데이터 중복 제거 | 읽기 성능 최적화를 위해 의도적 중복 |
| 쓰기 최적화 | 읽기 최적화 |
| JOIN 필요 | JOIN 감소 |

**판단 기준**: 읽기:쓰기 비율이 10:1 이상이고, JOIN이 성능 병목이면 비정규화 고려. 단, 데이터 일관성 유지 책임이 애플리케이션으로 이동.

---

### Q70. Spring Boot에서 이벤트 기반 아키텍처를 구현하는 방법은?

**A.**

```java
// 이벤트 정의
public record SessionCompletedEvent(Long sessionId, Long userId) {}

// 이벤트 발행
@Service
public class SessionService {
    @Autowired ApplicationEventPublisher publisher;

    @Transactional
    public void completeSession(Long sessionId) {
        // 비즈니스 로직...
        publisher.publishEvent(new SessionCompletedEvent(sessionId, userId));
    }
}

// 이벤트 수신
@Component
public class AnalysisEventListener {
    @TransactionalEventListener(phase = AFTER_COMMIT)
    @Async
    public void onSessionCompleted(SessionCompletedEvent event) {
        // AI 분석 작업 시작 (트랜잭션 커밋 후)
    }
}
```

**핵심**: `@TransactionalEventListener(AFTER_COMMIT)`으로 트랜잭션 커밋 후에만 이벤트 처리 → 데이터 일관성 보장

---

### Q71. 테스트에서 Mock과 Stub의 차이는?

**A.**

| 구분 | Stub | Mock |
|------|------|------|
| 목적 | **입력에 대한 고정 응답** 제공 | **행위(호출 여부) 검증** |
| 검증 | 상태(결과값) 검증 | 상호작용(호출 횟수, 인자) 검증 |
| 예시 | `when(repo.findById(1)).thenReturn(user)` | `verify(repo, times(1)).save(any())` |

**원칙**: 가능하면 Stub으로 상태 검증을 우선하고, 외부 시스템 호출 여부를 확인해야 할 때만 Mock 사용

---

### Q72. @Transactional 테스트의 문제점은 무엇인가요?

**A.** 통합 테스트에서 `@Transactional`을 사용하면:

1. **테스트가 자동 롤백** → DB에 실제 데이터가 커밋되지 않아 트리거/제약조건 검증 불가
2. **Lazy Loading이 항상 동작** → 프로덕션에서의 `LazyInitializationException` 미발견
3. **이벤트 리스너 미동작** → `@TransactionalEventListener(AFTER_COMMIT)` 이벤트 발행 안됨

**대안**: 테스트 후 DB를 직접 정리하는 JUnit Extension 사용:
```kotlin
@AfterEach
fun cleanup() {
    jdbcTemplate.execute("TRUNCATE TABLE training_sessions CASCADE")
}
```

---

### Q73. Flyway vs Liquibase 비교

**A.**

| 비교 | Flyway | Liquibase |
|------|--------|-----------|
| 마이그레이션 포맷 | **SQL 파일** | XML/YAML/JSON/SQL |
| 학습 곡선 | 낮음 | 높음 |
| 롤백 | 유료(Teams) | **무료 지원** |
| DB 간 호환 | DB별 SQL 작성 | 추상 changeset |
| 적합한 상황 | 단일 DB, SQL 숙련 팀 | 멀티 DB, 복잡한 변경 |

**권장**: Spring Boot와의 통합이 간단하고 SQL 직접 작성이 가능한 **Flyway** (단일 DB 사용 시)

---

### Q74. Connection Leak을 어떻게 감지하고 방지하나요?

**A.**

```yaml
spring:
  datasource:
    hikari:
      leak-detection-threshold: 60000  # 60초 이상 반환 안 된 커넥션 경고
```

**감지 방법**: HikariCP의 `leak-detection-threshold` 설정 → 로그에 스택트레이스 출력
**방지**: `@Transactional` 범위 최소화, try-with-resources, 외부 API 호출을 트랜잭션 밖으로

---

### Q75. Bulk Insert/Update 성능을 최적화하는 방법은?

**A.**

```kotlin
// ❌ 느림: N번 개별 INSERT
users.forEach { userRepository.save(it) }

// ✅ 빠름: Batch INSERT
@Modifying
@Query(value = "INSERT INTO users (name, email) VALUES (:name, :email)", nativeQuery = true)
fun batchInsert(users: List<User>)

// ✅ JPA batch 설정
spring.jpa.properties.hibernate.jdbc.batch_size=50
spring.jpa.properties.hibernate.order_inserts=true
spring.jpa.properties.hibernate.order_updates=true
```

**핵심**: `batch_size` 설정 + ID 생성 전략은 `SEQUENCE` 사용 (IDENTITY는 배치 불가)

---

### Q76. Spring Boot에서 멀티테넌시(Multi-Tenancy)를 구현하는 방법은?

**A.** B2B SaaS에서 고객사(tenant)별 데이터 격리:

| 전략 | 격리 수준 | 비용 | 적합한 경우 |
|------|----------|------|------------|
| **DB 분리** | 최고 | 높음 | 규제/보안 요구 |
| **스키마 분리** | 높음 | 중간 | 중간 규모 |
| **Row-Level 분리** | 보통 | 낮음 | **대부분의 SaaS** |

```kotlin
// Row-Level: 모든 테이블에 company_id 컬럼
@Entity
@Where(clause = "company_id = :tenantId")
class TrainingSession(
    @Column(name = "company_id")
    val companyId: Long,  // tenant 식별자
    // ...
)
```

---

### Q77. 실시간 데이터 처리에서 Back Pressure를 어떻게 처리하나요?

**A.** Back Pressure는 소비자가 처리할 수 있는 속도보다 생산자가 빠를 때 발생하는 문제:

| 전략                | 설명                                 |
| ----------------- | ---------------------------------- |
| **Buffer**        | 제한된 크기의 버퍼에 저장 → 초과 시 드롭 또는 에러     |
| **Drop**          | 최신/최고 데이터만 유지                      |
| **Throttle**      | 일정 시간 간격으로만 전달                     |
| **Request-based** | 소비자가 요청한 만큼만 전달 (Reactive Streams) |

---

### Q78. Kotlin의 sealed class를 API 응답 설계에 어떻게 활용하나요?

**A.**

```kotlin
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val code: String, val message: String) : ApiResult<Nothing>()
    data object Loading : ApiResult<Nothing>()
}

// 사용
fun getSession(id: Long): ApiResult<SessionDto> {
    return try {
        val session = sessionService.findById(id)
        ApiResult.Success(session.toDto())
    } catch (e: NotFoundException) {
        ApiResult.Error("SESSION_NOT_FOUND", "세션을 찾을 수 없습니다")
    }
}
```

**장점**: `when` 표현식에서 **exhaustive check** → 모든 케이스 처리를 컴파일러가 보장

---

### Q79. Spring Boot Actuator의 커스텀 Health Check를 구현하는 방법은?

**A.**

```kotlin
@Component
class AIServiceHealthIndicator(
    private val aiClient: AIClient
) : HealthIndicator {

    override fun health(): Health {
        return try {
            val response = aiClient.ping()
            if (response.isOk) Health.up()
                .withDetail("model", response.model)
                .withDetail("latency_ms", response.latencyMs)
                .build()
            else Health.down()
                .withDetail("error", response.error)
                .build()
        } catch (e: Exception) {
            Health.down(e).build()
        }
    }
}
```

---

### Q80. Kotlin의 확장 함수(Extension Function)를 실무에서 어떻게 활용하나요?

**A.**

```kotlin
// Entity → DTO 변환
fun UserEntity.toDto() = UserResponse(
    id = this.id,
    name = this.name,
    email = this.email
)

// 날짜 포맷팅
fun LocalDateTime.toKoreanFormat(): String =
    this.format(DateTimeFormatter.ofPattern("yyyy년 MM월 dd일"))

// 컬렉션 유틸
fun <T> List<T>.safeSubList(from: Int, to: Int): List<T> =
    this.subList(from.coerceAtLeast(0), to.coerceAtMost(this.size))
```

---

## 🟢 Tier 4: LLM 상용화, 스타트업, FE 협업 (#81~100)

---

### Q81. Spring AI를 활용한 LLM 통합 아키텍처를 설명하세요.

**A.**

```
┌─── Spring AI Architecture ───────────────┐
│                                           │
│  Controller                               │
│     ↓                                     │
│  ChatClient (추상화 인터페이스)             │
│     ↓                                     │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐ │
│  │  OpenAI  │  │  Gemini  │  │  Claude  │ │
│  │ Adapter  │  │ Adapter  │  │ Adapter  │ │
│  └─────────┘  └─────────┘  └──────────┘ │
│                                           │
│  PromptTemplate → 프롬프트 관리           │
│  OutputParser → 구조화된 응답 파싱        │
└───────────────────────────────────────────┘
```

**핵심**: `ChatClient` 인터페이스로 LLM 제공자를 추상화 → 설정만 변경하면 GPT ↔ Gemini 전환 가능

---

### Q82. LLM 응답을 SSE로 스트리밍하는 방법은?

**A.**

```kotlin
@GetMapping("/api/v1/chat/stream", produces = [MediaType.TEXT_EVENT_STREAM_VALUE])
fun streamChat(@RequestParam prompt: String): Flux<ServerSentEvent<String>> {
    return chatClient.prompt()
        .user(prompt)
        .stream()
        .content()
        .map { chunk ->
            ServerSentEvent.builder(chunk)
                .event("message")
                .build()
        }
        .concatWith(Flux.just(
            ServerSentEvent.builder("[DONE]")
                .event("done")
                .build()
        ))
}
```

**SSE 장점**: HTTP 표준, 자동 재연결, LLM API 네이티브 지원 (OpenAI/Anthropic 모두 SSE)

> 📎 출처: [Medium - Streaming LLM Response in Spring AI](https://medium.com/@rajesh.sgr/streaming-llm-response-in-spring-ai-e1298eb5f366)

---

### Q83. LLM 서비스 프로덕션에서의 주요 고려사항은?

**A.**

| 고려사항 | 대응 |
|---------|------|
| **비용 관리** | 토큰 사용량 모니터링, 짧은 프롬프트 설계, 캐싱 |
| **지연 시간** | 스트리밍 응답(SSE), 프롬프트 최적화 |
| **장애 대응** | LLM 제공자 fallback (GPT → Gemini), Circuit Breaker |
| **프롬프트 관리** | 프롬프트 버전 관리, A/B 테스트 |
| **안전성** | 입출력 필터링 (PII 마스킹, 유해 콘텐츠 차단) |
| **재현성** | temperature=0, seed 설정, 요청/응답 로깅 |

---

### Q84. AI 모델 서빙 파이프라인을 백엔드에서 어떻게 설계하나요?

**A.**

```
사용자 요청 → API Server → Message Queue → AI Worker
                                              │
                              ┌────────────────┤
                              ▼                ▼
                          STT 분석         표정 분석
                              │                │
                              ▼                ▼
                          NLP 분석         자세 분석
                              │                │
                              └──────┬─────────┘
                                     ▼
                              결과 통합 (리포트 생성)
                                     │
                                     ▼
                              DB 저장 + SSE 알림
```

**핵심**: 비동기 처리 (Message Queue) + 병렬 분석 (여러 AI 모델 동시 실행) + 결과 통합

---

### Q85. Circuit Breaker 패턴을 외부 AI API 호출에 적용하는 방법은?

**A.**

```kotlin
@CircuitBreaker(name = "aiService", fallbackMethod = "fallbackAnalysis")
fun analyzeSession(sessionId: Long): AnalysisResult {
    return aiClient.analyze(sessionId)
}

fun fallbackAnalysis(sessionId: Long, e: Exception): AnalysisResult {
    log.warn("AI service unavailable, queuing for retry", e)
    retryQueue.enqueue(sessionId)
    return AnalysisResult.pending("AI 서비스 일시 장애, 분석이 지연됩니다")
}
```

**Resilience4j 설정**: `failureRateThreshold=50`, `waitDurationInOpenState=60s`, `slidingWindowSize=10`

---

### Q86. 스타트업에서 Zero-base로 서비스를 구축한 경험을 어떻게 설명하나요?

**A.** STAR 프레임워크:

- **S**: 초기 스타트업에서 백엔드 시스템이 전무한 상태
- **T**: 3개월 내 MVP 출시, 첫 고객사 PoC 성공
- **A**: 기술 스택 선정 → DB 설계 → API 개발 → CI/CD 구축 → 모니터링
- **R**: 정량적 결과 (출시 일정 준수, 첫 고객사 계약, 성능 지표)

**핵심 포인트**: "완벽한 설계보다 빠른 검증" + "기술 부채를 의식적으로 관리"

---

### Q87. FE 개발자와 효과적으로 협업하기 위한 API 계약(Contract)을 어떻게 관리하나요?

**A.**

| 방법 | 도구 | 장점 |
|------|------|------|
| **API-First** | OpenAPI Spec → 코드 생성 | 계약 우선, 병렬 개발 가능 |
| **Mock Server** | WireMock, Prism | FE가 백엔드 없이 개발 |
| **Contract Test** | Pact, Spring Cloud Contract | 계약 위반 자동 감지 |

```yaml
# OpenAPI Spec 예시
paths:
  /api/v1/sessions:
    post:
      summary: 교육 세션 생성
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateSessionRequest'
      responses:
        '201':
          description: 세션 생성 성공
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SessionResponse'
```

---

### Q88. 프로덕션 데이터베이스 성능 모니터링 방법은?

**A.**

| 도구 | 모니터링 대상 |
|------|-------------|
| `pg_stat_statements` | 느린 쿼리 Top N, 실행 횟수 |
| `pg_stat_activity` | 현재 실행 중인 쿼리, 대기 상태 |
| HikariCP Metrics | 커넥션 풀 사용률, 대기 시간 |
| Grafana Dashboard | 위 메트릭 시각화 + 알림 설정 |

**슬로우 쿼리 알림**: `log_min_duration_statement = 1000` (1초 이상 쿼리 로깅)

---

### Q89. Spring Boot에서 스케줄링 작업을 구현하는 방법은?

**A.**

```kotlin
@EnableScheduling
@Component
class ScheduledTasks {

    // 매일 새벽 2시 미완료 세션 정리
    @Scheduled(cron = "0 0 2 * * *")
    fun cleanupExpiredSessions() {
        sessionService.deleteExpired()
    }

    // 분산 환경에서는 ShedLock으로 단일 실행 보장
    @SchedulerLock(name = "cleanupExpiredSessions", lockAtMostFor = "PT30M")
    fun cleanupWithLock() { ... }
}
```

**분산 환경 주의**: 여러 서버에서 동시 실행 방지 → **ShedLock** (DB/Redis 기반 분산 락)

---

### Q90. Spring Boot에서 환경별 설정을 관리하는 방법은?

**A.**

```
application.yml              ← 공통 설정
application-local.yml        ← 로컬 개발
application-dev.yml          ← 개발 서버
application-staging.yml      ← 스테이징
application-prod.yml         ← 프로덕션
```

**민감 정보 관리**:
- DB 비밀번호, API 키 → **환경 변수** 또는 **AWS Secrets Manager**
- 절대 Git에 커밋하지 않음
- `@Value("${ai.api.key}")` → 환경 변수에서 주입

---

### Q91. Kotlin의 data class와 Java record의 차이는?

**A.**

| 비교 | Kotlin data class | Java record |
|------|------------------|-------------|
| 가변성 | `val`/`var` 선택 가능 | **불변(final) 전용** |
| `copy()` | ✅ 제공 | ❌ 없음 |
| 상속 | 불가 | 불가 |
| 디컴파일 | equals/hashCode/toString/copy | equals/hashCode/toString |
| 커스텀 로직 | body 내 메서드 추가 가능 | compact constructor |

---

### Q92. API Rate Limiting과 Throttling의 차이는?

**A.**

| 비교 | Rate Limiting | Throttling |
|------|---------------|------------|
| 초과 시 동작 | **즉시 거부** (HTTP 429) | **지연/대기** (큐잉) |
| 목적 | 남용 방지, 공정 사용 보장 | 트래픽 평활화, 백엔드 보호 |
| 응답 | `429 Too Many Requests` + `Retry-After` 헤더 | 요청 지연 후 정상 처리 |
| 구현 | Token Bucket, Sliding Window | Leaky Bucket, Request Queue |
| 적합한 상황 | 외부 API, 공개 엔드포인트 | 내부 서비스, 배치 처리 |

**실무 조합**: 외부 API에는 Rate Limiting(429 반환), 내부 AI 분석 파이프라인에는 Throttling(큐에 넣고 순차 처리)으로 조합하여 사용

---

### Q93. Spring Boot에서 Health Check와 Readiness/Liveness Probe의 차이는?

**A.**

| Probe | 목적 | 실패 시 |
|-------|------|---------|
| **Liveness** | 앱이 살아있는가? | 컨테이너 **재시작** |
| **Readiness** | 요청을 받을 준비가 됐는가? | 트래픽 **차단** (재시작 아님) |

```yaml
management:
  endpoint:
    health:
      probes:
        enabled: true
  health:
    livenessState:
      enabled: true
    readinessState:
      enabled: true
```

---

### Q94. OpenAPI/Swagger 문서를 자동 생성하는 방법은?

**A.**

```kotlin
// springdoc-openapi 사용
implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.x")

@Operation(summary = "교육 세션 생성", description = "새로운 교육 세션을 시작합니다")
@ApiResponses(
    ApiResponse(responseCode = "201", description = "세션 생성 성공"),
    ApiResponse(responseCode = "400", description = "입력값 오류")
)
@PostMapping("/api/v1/sessions")
fun createSession(@Valid @RequestBody request: CreateSessionRequest): SessionResponse
```

**접속**: `http://localhost:8080/swagger-ui.html`

---

### Q95. 초기 스타트업에서 기술 스택을 선정하는 기준은?

**A.**

| 기준 | 설명 |
|------|------|
| **팀 역량** | 팀이 가장 잘 아는 기술 (학습 비용 최소화) |
| **생태계** | 라이브러리/도구 풍부, 커뮤니티 활성화 |
| **채용 용이성** | 해당 기술 개발자 구인 가능 여부 |
| **확장성** | 사용자 10배 증가 시 대응 가능 |
| **비용** | 라이선스, 인프라 비용 |

---

### Q96. Kotlin의 sealed interface와 when을 활용한 도메인 모델링은?

**A.**

```kotlin
sealed interface SessionState {
    data class Waiting(val scheduledAt: LocalDateTime) : SessionState
    data class InProgress(val startedAt: LocalDateTime) : SessionState
    data class Analyzing(val progress: Int) : SessionState
    data class Completed(val report: Report) : SessionState
    data class Failed(val error: String) : SessionState
}

fun handleState(state: SessionState): String = when (state) {
    is SessionState.Waiting -> "대기 중"
    is SessionState.InProgress -> "진행 중"
    is SessionState.Analyzing -> "분석 중 (${state.progress}%)"
    is SessionState.Completed -> "완료"
    is SessionState.Failed -> "실패: ${state.error}"
    // 컴파일러가 모든 케이스 처리를 보장!
}
```

---

### Q97. 프로덕션에서 메모리 누수를 감지하고 해결하는 방법은?

**A.**

| 단계 | 도구 | 확인 포인트 |
|------|------|------------|
| 1. 모니터링 | Grafana + JVM Metrics | 힙 사용량 증가 추세 |
| 2. 힙 덤프 | `jmap -dump:format=b,file=heap.hprof <pid>` | 대용량 객체 식별 |
| 3. 분석 | Eclipse MAT, VisualVM | Dominator Tree, Leak Suspects |
| 4. 수정 | 코드 리뷰 | 닫지 않은 리소스, 캐시 무한 증가, 이벤트 리스너 해제 |

---

### Q98. Spring Boot에서 국제화(i18n)를 구현하는 방법은?

**A.**

```
resources/
├── messages.properties          ← 기본 (한국어)
├── messages_en.properties       ← 영어
├── messages_ja.properties       ← 일본어
```

```kotlin
@Service
class MessageService(private val messageSource: MessageSource) {
    fun getMessage(code: String, locale: Locale): String {
        return messageSource.getMessage(code, null, locale)
    }
}
```

**쏘카인드 적용**: 해외 진출(영어/일본어) 대비, API 에러 메시지 + 리포트 내용 다국어 지원

---

### Q99. Docker 기반 개발 환경 구성 방법은?

**A.**

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: sokind
      POSTGRES_USER: app
      POSTGRES_PASSWORD: dev123
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  app:
    build: .
    depends_on: [postgres, redis]
    environment:
      SPRING_PROFILES_ACTIVE: local
    ports:
      - "8080:8080"
```

**원칙**: `docker-compose up` 한 번으로 전체 환경 구동 가능하게

---

### Q100. 기술 면접에서 "모른다"고 말하는 것의 중요성은?

**A.**

| 상황 | ❌ 나쁜 대응 | ✅ 좋은 대응 |
|------|-------------|-------------|
| 모르는 질문 | 추측으로 답변 | "직접 경험은 없지만, 유사한 경험으로 접근하면..." |
| 부분적 지식 | 아는 척 | "X까지는 알고 있고, Y 부분은 추가 학습이 필요합니다" |
| 실수 발견 | 무시 | "방금 답변에서 X 부분이 잘못된 것 같습니다. 정정하면..." |

**핵심**: 시니어 엔지니어는 "무엇을 모르는지 아는 것"이 더 중요. 모르는 것을 인정하고 학습하는 태도가 팀에 더 큰 가치.

---

## 📎 Research Sources

1. [Spring Boot REST API Best Practices](https://www.codingshuttle.com/blogs/best-practices-for-writing-spring-boot-api/) — 기술 블로그
2. [Hexagonal Architecture in Spring Boot](https://javascript.plainenglish.io/architecting-enterprise-grade-rest-apis-in-spring-boot-a-deep-guide-to-clean-hexagonal-fdd65df3ccb3) — 기술 블로그
3. [Baeldung - N+1 Problem](https://www.baeldung.com/spring-hibernate-n1-problem) — 기술 블로그
4. [PostgreSQL Interview Questions - GeeksforGeeks](https://www.geeksforgeeks.org/postgresql/postgresql-interview-questions/) — 기술 블로그
5. [Virtual Threads Performance](https://www.javacodegeeks.com/2025/04/spring-boot-performance-with-java-virtual-threads.html) — 기술 블로그
6. [Spring Security JWT Best Practices](https://katyella.com/blog/spring-boot-security-best-practices/) — 기술 블로그
7. [WebRTC Guide - Baeldung](https://www.baeldung.com/webrtc) — 기술 블로그
8. [Spring AI Streaming](https://medium.com/@rajesh.sgr/streaming-llm-response-in-spring-ai-e1298eb5f366) — 기술 블로그
9. [Multi-Module Best Practices - Bootify](https://bootify.io/multi-module/best-practices-for-spring-boot-multi-module.html) — 기술 블로그
10. [LeadDev - Tech Debt Roadmap](https://leaddev.com/legacy-technical-debt-migrations/building-realistic-roadmaps-tech-debt-cleanup) — 기술 블로그
11. [Spring WebFlux vs MVC - GeeksforGeeks](https://www.geeksforgeeks.org/blogs/spring-mvc-vs-spring-web-flux/) — 기술 블로그
12. [Kotlin Coroutines with Spring Boot - Baeldung](https://www.baeldung.com/kotlin/spring-boot-kotlin-coroutines) — 기술 블로그
13. [Redis Caching with Spring Boot](https://medium.com/simform-engineering/spring-boot-caching-with-redis-1a36f719309f) — 기술 블로그
14. [Testcontainers with Spring Boot](https://medium.com/@aleksanderkolata/integration-tests-with-testcontainers-and-spring-boot-3-1-39103ff95bd7) — 기술 블로그
15. [Spring Boot Testing Best Practices - Wim Deblauwe](https://www.wimdeblauwe.com/blog/2025/07/30/how-i-test-production-ready-spring-boot-applications/) — 1차 자료
16. [Spring AI - Awesome Spring AI](https://github.com/spring-ai-community/awesome-spring-ai) — 커뮤니티

---

## 📊 Research Metadata

- 검색 쿼리 수: 15 (일반 13 + SNS 2)
- 수집 출처 수: 16
- 출처 유형: 공식 2, 블로그 12, 커뮤니티 2
- Deep Research: Phase 1 (광역 탐색) + Phase 2 (심화 탐색) + Phase 3 (지식 합성) 수행
- Concept Explainer: 5개 핵심 개념 (WebFlux/MVC, WebRTC, SSE/LLM, N+1, 멀티모듈) 8관점 분석
