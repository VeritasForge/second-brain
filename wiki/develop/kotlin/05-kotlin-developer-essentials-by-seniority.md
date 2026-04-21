---
created: 2026-04-21
source: claude-code
tags: [kotlin, spring, career-growth, junior, senior, staff, interview, essentials]
---

# 📖 Kotlin+Spring 개발자 필수 지식 — 레벨별 성장 로드맵

> 💡 **한줄 요약**: Kotlin+Spring 개발자의 성장은 "Kotlin 기본 + Spring Boot CRUD → 코루틴 + Spring 내부 이해 → JVM 튜닝 + 시스템 설계 → 아키텍처 결정 + 팀 표준"의 이중 트랙으로 진행된다.
>
> 📌 **면접 심화**: [[kotlin-spring]] (Staff Engineer Interview Q&A 26문항)
> 📅 **기준**: Kotlin 2.1+ / Spring Boot 3.x (2025)

---

## 성장 경로 (Kotlin + Spring 이중 트랙)

```
  Junior (0-2년)     Mid (2-4년)       Senior (4-7년)     Staff (7년+)
  ────────────      ────────────      ─────────────     ──────────
  Kotlin 기본       코루틴 활용        JVM 내부 이해      아키텍처 결정
  + Spring CRUD     + Spring 심화      + Spring 내부      + 팀 생산성
  
  val/var, null?    suspend, Flow     GC 튜닝, AOP      언어 선택
  @RestController   @Transactional    BeanPostProcessor  모듈러 모노리스
  JPA 기본          MockK, test slice  pprof/JFR         KMP 전략
```

---

## 1️⃣ Junior — "Kotlin + Spring Boot로 CRUD를 만들 수 있는가"

### 필수 지식 ★★★
- Kotlin 기본: `val/var`, null safety(`?`, `?.`, `?:`), data class, when
- Spring Boot: `@RestController`, `@Service`, `@Repository`, JPA 기본
- Gradle: `build.gradle.kts` 기본 설정
- 테스트: JUnit 5, 기본 `@SpringBootTest`
- 에러 처리: `try/catch`, `@ExceptionHandler`

### 면접 빈출 ★★★
- "val과 var의 차이" — 불변/가변, Java final
- "Kotlin null safety 설명" — `?`, `?.`, `?:`, `!!`, smart cast
- "data class가 자동 생성하는 것" — equals, hashCode, toString, copy, componentN

---

## 2️⃣ Mid — "프로덕션 코드를 작성하고 코루틴을 활용하는가"

### 필수 지식 ★★★★
- 코루틴: `suspend fun`, `launch/async`, `coroutineScope`, `Flow` → [[04-kotlin-advanced-syntax-and-patterns]] §1
- Spring 심화: `@Transactional` 동작 원리, 프로파일, `@ConfigurationProperties` → [[spring-di-bean-test-deep-dive]]
- 테스트: MockK, `@WebMvcTest`/`@DataJpaTest` (test slices) → [[06-kotlin-testing-patterns]]
- 제네릭: `in/out` variance, reified
- Gradle: 멀티 모듈, 빌드 캐시

### 면접 빈출 ★★★★
- "코루틴과 스레드의 차이" — 상태 머신, Dispatcher, 구조화된 동시성
- "@Transactional self-invocation 문제" — 프록시 우회, AOP
- "sealed class 용도" — 완전성 검사, Result 패턴

---

## 3️⃣ Senior — "JVM 내부를 이해하고 시스템을 설계하는가"

### 필수 지식 ★★★★★
- JVM 내부: GC 동작 (G1/ZGC), 메모리 구조, JIT → [[02-kotlin-architecture-and-runtime]] §2-3, [[gc-g1-zgc]]
- Spring 내부: BeanPostProcessor, Auto-configuration 원리 → [[spring-aop-complete-guide]]
- 코루틴 심화: Dispatcher 설계, 코루틴 디버깅, 예외 전파 → [[kotlin-spring]] Q1-Q6
- 성능: JFR (Java Flight Recorder), async profiler, R2DBC
- 시스템 설계: gRPC, 분산 트레이싱 (OpenTelemetry)

### 면접 빈출 ★★★★★
- "G1 GC 동작 원리" → interview-prep Q7-Q9
- "코루틴 예외 전파와 supervisorScope" → interview-prep Q4
- "Spring Auto-configuration 동작 원리"
- "프로덕션 성능 이슈 디버깅 경험"

---

## 4️⃣ Staff — "기술 방향과 팀 표준을 결정하는가"

### 필수 지식 ★★★★★
- 언어 선택: Kotlin vs Go 트레이드오프 → [[kotlin-vs-go]]
- 아키텍처: 모듈러 모노리스 vs MSA, Spring Modulith
- KMP 전략: Kotlin Multiplatform 도입 판단
- GraalVM: Native Image 도입 vs JVM 유지 판단
- 팀 표준: Kotlin 코딩 컨벤션, 코루틴 사용 가이드라인

### 면접 빈출 ★★★★★
- "Kotlin+Spring vs Go 선택 근거" — 도메인, 팀, 성능
- "대규모 Spring 프로젝트의 시작 시간을 어떻게 개선했는가"
- "코루틴 도입이 팀 생산성에 미친 영향"

> 📌 Staff 면접 전체: [[kotlin-spring]] (26문항, L6/L7)

---

## 📋 자기 진단 체크리스트

### Junior → Mid
- [ ] 코루틴으로 비동기 API를 작성할 수 있다
- [ ] `@Transactional`의 self-invocation 문제를 설명할 수 있다
- [ ] MockK로 서비스 레이어를 테스트할 수 있다
- [ ] sealed class로 Result 패턴을 구현할 수 있다

### Mid → Senior
- [ ] G1/ZGC의 차이와 선택 기준을 설명할 수 있다
- [ ] Spring Auto-configuration 원리를 설명할 수 있다
- [ ] 코루틴 예외 전파 규칙을 알고 있다 (supervisorScope vs coroutineScope)
- [ ] JFR/async profiler로 병목을 찾을 수 있다

### Senior → Staff
- [ ] Kotlin vs Go 선택 근거를 기술적으로 판단할 수 있다
- [ ] 팀의 Kotlin/Spring 코딩 표준을 수립할 수 있다
- [ ] GraalVM Native Image 도입 여부를 판단할 수 있다

---

## 📎 출처

1. [Kotlin Coding Conventions (공식)](https://kotlinlang.org/docs/coding-conventions.html)
2. [Spring Boot Reference](https://docs.spring.io/spring-boot/reference/)
3. [Uber Go Style Guide (참고)](https://github.com/uber-go/guide) — 팀 스타일 가이드 예시

---

> 📌 **이전 문서**: [[04-kotlin-advanced-syntax-and-patterns]]
> 📌 **다음 문서**: [[06-kotlin-testing-patterns]]
> 📌 **면접**: [[kotlin-spring]] (26문항)
