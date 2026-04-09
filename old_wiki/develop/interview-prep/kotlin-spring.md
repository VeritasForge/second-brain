# Kotlin / Spring — Staff Engineer Interview Q&A

> 대상: FAANG L6/L7 (Staff/Principal Engineer)
> 총 문항: 26개 | 난이도: ⭐⭐⭐⭐⭐
> 프레임워크: Kotlin 2.0+, Spring Boot 3.3+, Spring Framework 6.1+

## 목차

1. [Coroutines Deep Dive](#1-coroutines-deep-dive) — Q1~Q3
2. [Flow & Reactive](#2-flow--reactive) — Q4~Q6
3. [JVM Internals](#3-jvm-internals) — Q7~Q9
4. [Spring DI & Lifecycle](#4-spring-di--lifecycle) — Q10~Q12
5. [Spring WebFlux & Reactive](#5-spring-webflux--reactive) — Q13~Q14
6. [Kotlin Language Mastery](#6-kotlin-language-mastery) — Q15~Q17
7. [Spring Security](#7-spring-security) — Q18~Q19
8. [Testing in Spring](#8-testing-in-spring) — Q20~Q21
9. [Spring Boot Operational](#9-spring-boot-operational) — Q22~Q23
10. [Data Access](#10-data-access) — Q24~Q26

---

## 1. Coroutines Deep Dive

### Q1: Structured Concurrency와 CancellationException 전파

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Coroutines Deep Dive

**Question:**
프로덕션에서 `coroutineScope` 안에서 여러 자식 코루틴을 실행할 때, 하나가 실패하면 나머지는 어떻게 되는가? `supervisorScope`와의 차이를 설명하고, `CancellationException`이 다른 예외와 다르게 전파되는 이유를 설명하라. 실제로 부분 실패를 허용하면서도 구조화된 동시성을 유지하는 패턴을 설계하라.

---

**🧒 12살 비유:**
학교 조별 과제를 생각해 보자. `coroutineScope`는 "한 명이라도 숙제를 안 하면 조 전체가 F를 받는" 엄격한 선생님이다. 한 명이 실패하면 나머지 애들한테도 "너희도 그만해"라고 한다. `supervisorScope`는 "각자 따로 채점하는" 선생님이다. 한 명이 F를 받아도 나머지는 자기 점수를 받는다. `CancellationException`은 "집에 가야 해서 일찍 가는 것"이다 — 이건 실패가 아니라 정상적인 조기 종료이기 때문에 선생님이 벌을 주지 않는다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
빅테크 면접관은 이 질문으로 (1) 코루틴의 Job 트리 구조에 대한 정확한 이해, (2) 예외 전파 메커니즘의 내부 동작 파악, (3) 프로덕션에서 부분 실패 처리 설계 능력을 평가한다. 단순히 "supervisorScope를 쓰면 된다"가 아니라, 왜 그런 설계가 필요한지와 그 한계까지 설명할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

Kotlin의 Structured Concurrency는 코루틴이 **Job 트리**를 형성하는 것에 기반한다. 모든 코루틴은 부모 Job을 가지며, 부모는 자식이 모두 완료될 때까지 완료되지 않는다.

예외 전파의 핵심 규칙:
- **일반 예외**: 자식 → 부모로 전파 → 부모가 다른 자식들을 취소 → 부모 자신도 실패
- **CancellationException**: 해당 코루틴만 취소, 부모로 전파되지 않음. 이유는 취소는 "정상적인 제어 흐름"이기 때문이다
- **SupervisorJob**: 자식의 실패가 부모나 형제에게 전파되지 않음. 내부적으로 `childCancelled()`가 `false`를 반환하여 전파를 차단한다

```kotlin
// coroutineScope: 하나의 실패가 전체를 취소
suspend fun fetchAllOrFail(): List<UserData> = coroutineScope {
    val profile = async { userService.getProfile(userId) }     // 실패 시 →
    val orders = async { orderService.getOrders(userId) }      // ← 이것도 취소됨
    val recommendations = async { recService.getRecs(userId) } // ← 이것도 취소됨
    listOf(profile.await(), orders.await(), recommendations.await())
}

// supervisorScope: 각 자식이 독립적으로 실패
suspend fun fetchWithPartialFailure(): AggregatedResult = supervisorScope {
    val profile = async {
        runCatching { userService.getProfile(userId) }
    }
    val orders = async {
        runCatching { orderService.getOrders(userId) }
    }
    val recommendations = async {
        runCatching { recService.getRecs(userId) }
    }
    AggregatedResult(
        profile = profile.await().getOrNull(),
        orders = orders.await().getOrDefault(emptyList()),
        recommendations = recommendations.await().getOrDefault(emptyList())
    )
}
```

`CancellationException`이 특별한 이유는 `JobSupport.childCancelled()` 구현에 있다:

```kotlin
// kotlinx.coroutines 내부 (단순화)
public open fun childCancelled(cause: Throwable): Boolean {
    if (cause is CancellationException) return true // 처리 완료, 전파 안 함
    return cancelImpl(cause) // 일반 예외는 부모를 취소시킴
}
```

**Step 3 — 다양한 관점**

| 관점 | coroutineScope | supervisorScope |
|------|----------------|-----------------|
| 일관성 | All-or-nothing (강한 일관성) | 부분 성공 허용 (가용성 우선) |
| 에러 핸들링 | 단순 — 하나만 잡으면 됨 | 복잡 — 각 자식별로 핸들링 필요 |
| 리소스 정리 | 자동 — 취소 시 모두 정리 | 수동 — 실패한 것만 정리, 성공한 것은 유지 |
| 적합한 곳 | 트랜잭션성 작업, 데이터 정합성 중요 | BFF 집계, 대시보드, 비핵심 데이터 |

프로덕션에서의 주의점: `supervisorScope` 안에서 `launch`를 쓸 때 예외를 잡지 않으면 `CoroutineExceptionHandler`로 전파되어 **앱이 크래시**할 수 있다. `async`는 `await()` 시점에 예외가 노출되므로 `runCatching`으로 감싸는 패턴이 안전하다.

**Step 4 — 구체적 예시**

프로덕션 BFF(Backend For Frontend) 집계 패턴:

```kotlin
@Service
class DashboardAggregator(
    private val userClient: UserServiceClient,
    private val analyticsClient: AnalyticsClient,
    private val notificationClient: NotificationClient,
    private val meterRegistry: MeterRegistry
) {
    suspend fun getDashboard(userId: String): DashboardResponse = supervisorScope {
        val profileDeferred = async {
            withTimeoutAndMetrics("user.profile") {
                userClient.getProfile(userId)
            }
        }
        val statsDeferred = async {
            withTimeoutAndMetrics("user.analytics") {
                analyticsClient.getStats(userId)
            }
        }
        val notiDeferred = async {
            withTimeoutAndMetrics("user.notifications") {
                notificationClient.getUnread(userId)
            }
        }

        // 프로필은 필수, 나머지는 선택
        val profile = profileDeferred.await() // 실패 시 전체 실패 허용
        val stats = runCatching { statsDeferred.await() }.getOrElse {
            meterRegistry.counter("dashboard.partial_failure", "component", "analytics").increment()
            Stats.empty()
        }
        val notifications = runCatching { notiDeferred.await() }.getOrElse {
            meterRegistry.counter("dashboard.partial_failure", "component", "notifications").increment()
            emptyList()
        }

        DashboardResponse(profile, stats, notifications)
    }

    private suspend inline fun <T> withTimeoutAndMetrics(
        name: String,
        crossinline block: suspend () -> T
    ): T {
        val timer = meterRegistry.timer("dashboard.component.duration", "component", name)
        return timer.recordSuspend {
            withTimeout(3.seconds) { block() }
        }
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| `coroutineScope` | 단순, all-or-nothing 보장 | 하나 실패 시 전체 재시도 필요 | 결제, 트랜잭션 |
| `supervisorScope` + `runCatching` | 부분 실패 허용, 가용성 높음 | 에러 핸들링 복잡, 빈 데이터 처리 필요 | BFF 집계, 대시보드 |
| `supervisorScope` + `CoroutineExceptionHandler` | launch 기반 fire-and-forget에 적합 | 예외가 삼켜질 수 있음, 디버깅 어려움 | 로그 전송, 메트릭 수집 |
| Channel/Actor 기반 격리 | 완전한 격리, 재시도 로직 내장 가능 | 구현 복잡도 높음, 오버엔지니어링 위험 | 복잡한 워크플로 |

**Step 6 — 성장 & 심화 학습**
- `CoroutineExceptionHandler`가 `async`에서는 동작하지 않는 이유 (deferred 예외는 `await()`에서 노출)
- `NonCancellable` 컨텍스트와 cleanup 코드에서의 활용
- Kotlin 2.0의 `@SubclassOptInRequired`가 sealed exception hierarchy에 미치는 영향
- Project Loom의 Virtual Thread와 Kotlin Coroutine의 공존 전략

**🎯 면접관 평가 기준:**
- **L6 PASS**: Job 트리 구조, CancellationException 특수성, supervisorScope 활용을 정확히 설명. 프로덕션 부분 실패 패턴 제시
- **L7 EXCEED**: 내부 `childCancelled()` 메커니즘까지 설명. 메트릭/옵저버빌리티 연계. 팀 컨벤션으로 확장 (언제 어떤 스코프를 쓸지 가이드라인 제시)
- 🚩 **RED FLAG**: "supervisorScope 쓰면 예외가 전파 안 된다"로만 답변 (launch vs async 차이 모름). CancellationException을 일반 예외처럼 catch하는 코드 작성

---

### Q2: CoroutineContext와 Dispatchers 내부 동작

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Coroutines Deep Dive

**Question:**
`CoroutineContext`는 내부적으로 어떤 자료구조인가? `Dispatchers.Default`와 `Dispatchers.IO`는 실제로 같은 스레드 풀을 공유하는가? `withContext(Dispatchers.IO)` 호출 시 실제로 스레드 스위칭이 발생하는 조건과, `limitedParallelism()`이 도입된 이유를 설명하라.

---

**🧒 12살 비유:**
`CoroutineContext`는 여행 가방에 넣는 "태그들의 묶음"이다. 이름표(Job), 어디서 일할지(Dispatcher), 에러 처리 방법(ExceptionHandler) 등 여러 태그를 하나로 합쳐서 들고 다닌다. 태그가 겹치면 나중에 넣은 게 이긴다. `Dispatchers.Default`는 "수학 문제 풀기 전용 책상"이고, `Dispatchers.IO`는 "택배 기다리기 전용 대기실"인데, 사실 같은 건물 안에 있다. `limitedParallelism()`은 "이 대기실에 최대 5명만 들어갈 수 있다"는 표지판이다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
이 질문은 코루틴을 "마법의 경량 스레드"가 아니라 구체적인 JVM 스레드 위에서 동작하는 메커니즘으로 이해하는지 검증한다. Staff 레벨 엔지니어는 Dispatcher 선택이 스레드 풀 크기와 컨텍스트 스위칭 비용에 어떤 영향을 미치는지 정량적으로 설명할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

`CoroutineContext`는 **indexed set** 자료구조다. 각 Element는 고유한 `Key`를 가지며, `+` 연산자로 합치면 같은 Key의 Element는 덮어쓴다:

```kotlin
// CoroutineContext의 핵심 인터페이스 (단순화)
public interface CoroutineContext {
    operator fun <E : Element> get(key: Key<E>): E?
    fun <R> fold(initial: R, operation: (R, Element) -> R): R
    operator fun plus(context: CoroutineContext): CoroutineContext
}
// 내부적으로 CombinedContext라는 linked list 형태로 구현됨
```

Dispatchers 내부 구조:
- `Dispatchers.Default`: `CommonPool` 기반, 스레드 수 = `max(2, CPU 코어 수)`. CPU-bound 작업에 최적화
- `Dispatchers.IO`: Default와 **같은 스레드 풀을 공유**하되, 추가로 최대 64개(또는 코어 수 중 큰 값)까지 스레드를 확장. blocking I/O가 Default 스레드를 고갈시키지 않도록 설계
- 같은 `CoroutineScheduler`를 사용하지만, IO는 `LimitingDispatcher`로 래핑되어 동시 실행 수를 제한

```kotlin
// 실제 동작 (kotlinx.coroutines 내부)
// Dispatchers.IO = Dispatchers.Default의 CoroutineScheduler에
// LimitingDispatcher(parallelism=64)를 씌운 것

// withContext(Dispatchers.IO) 호출 시:
// 1. 현재 스레드가 이미 IO dispatcher의 스레드면 → 스위칭 없음
// 2. 현재 스레드가 Default dispatcher의 스레드면 → 같은 스레드에서 실행 가능
//    (같은 CoroutineScheduler이므로), 단 IO parallelism 카운터만 증가
// 3. 완전히 다른 스레드(예: Main)면 → 실제 스레드 스위칭 발생
```

`limitedParallelism()`이 도입된 이유 (kotlinx.coroutines 1.6):

```kotlin
// 문제: IO dispatcher가 64개 스레드를 공유하면
// 하나의 느린 서비스가 모든 IO 스레드를 점유할 수 있음

// 해결: 서비스별 독립적인 parallelism 제한
val dbDispatcher = Dispatchers.IO.limitedParallelism(10)    // DB용 최대 10
val httpDispatcher = Dispatchers.IO.limitedParallelism(20)   // HTTP용 최대 20
val fileDispatcher = Dispatchers.IO.limitedParallelism(5)    // 파일 I/O용 최대 5

// 이들은 여전히 같은 CoroutineScheduler의 스레드를 공유하지만
// 각각의 동시 실행 수는 독립적으로 제한됨 — Bulkhead 패턴
```

**Step 3 — 다양한 관점**

스레드 스위칭이 **발생하지 않는** 경우를 아는 것이 중요하다:
- `withContext(coroutineContext)` — 같은 컨텍스트면 no-op
- `withContext(Dispatchers.Default)`를 Default 스레드에서 호출 — 이미 맞는 디스패처
- `Dispatchers.Unconfined` — 첫 중단점까지 현재 스레드에서 실행

성능 관점에서 `Dispatchers.Default`에서 blocking I/O를 하면:
- CPU 코어 수만큼의 스레드가 모두 blocking 되어 다른 코루틴이 스케줄링되지 못함
- GC, JIT 컴파일 등 JVM 내부 작업도 영향 받을 수 있음

**Step 4 — 구체적 예시**

```kotlin
@Configuration
class DispatcherConfig {
    // 서비스별 Bulkhead 패턴
    @Bean("paymentDispatcher")
    fun paymentDispatcher(): CoroutineDispatcher =
        Dispatchers.IO.limitedParallelism(15)

    @Bean("inventoryDispatcher")
    fun inventoryDispatcher(): CoroutineDispatcher =
        Dispatchers.IO.limitedParallelism(10)

    @Bean("cpuIntensiveDispatcher")
    fun cpuIntensiveDispatcher(): CoroutineDispatcher =
        Dispatchers.Default.limitedParallelism(
            (Runtime.getRuntime().availableProcessors() / 2).coerceAtLeast(2)
        )
}

@Service
class OrderService(
    @Qualifier("paymentDispatcher") private val paymentDispatcher: CoroutineDispatcher,
    @Qualifier("inventoryDispatcher") private val inventoryDispatcher: CoroutineDispatcher
) {
    suspend fun processOrder(order: Order): OrderResult = coroutineScope {
        val payment = async(paymentDispatcher) {
            paymentGateway.charge(order.paymentInfo) // 느린 외부 API
        }
        val inventory = async(inventoryDispatcher) {
            inventoryService.reserve(order.items) // DB blocking
        }
        OrderResult(payment.await(), inventory.await())
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| `Dispatchers.IO` 공유 | 단순, 기본 설정으로 충분 | 한 서비스가 스레드 풀 독점 가능 | 소규모 서비스, 외부 의존 적음 |
| `limitedParallelism()` | Bulkhead 격리, 장애 전파 방지 | 설정 관리 필요, 총합이 IO 풀보다 클 수 있음 | 다수 외부 서비스 호출 |
| 커스텀 `ExecutorService` 기반 | 완전한 격리, 모니터링 용이 | 스레드 재사용 없음, 리소스 낭비 | 레거시 통합, 특수 요구사항 |
| Virtual Thread (Loom) | 수십만 개 생성 가능, blocking 무관 | JVM 21+ 필요, 라이브러리 호환성 이슈 | 그린필드 + JVM 21+ |

**Step 6 — 성장 & 심화 학습**
- `CoroutineScheduler`의 work-stealing 알고리즘 이해
- `Dispatchers.Default`와 `ForkJoinPool`의 차이점
- Kotlin 2.0에서의 `Dispatchers.IO`와 Virtual Thread 통합 (`Dispatchers.IO.limitedParallelism()` vs `Dispatchers.IO` on Loom)
- Micrometer로 Dispatcher 스레드 풀 메트릭 수집 패턴

**🎯 면접관 평가 기준:**
- **L6 PASS**: Default와 IO가 같은 스케줄러를 공유한다는 사실, limitedParallelism의 Bulkhead 역할을 설명
- **L7 EXCEED**: CoroutineScheduler의 work-stealing, 스레드 스위칭 발생/미발생 조건, Virtual Thread와의 비교까지 논의
- 🚩 **RED FLAG**: "IO는 무한 스레드를 만든다", "withContext는 항상 스레드를 바꾼다"

---

### Q3: SupervisorScope와 예외 처리 전략 설계

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Coroutines Deep Dive

**Question:**
대규모 이벤트 처리 시스템에서 수천 개의 코루틴이 동시에 실행된다. 일부 이벤트 처리 실패가 전체 시스템을 멈추면 안 된다. `CoroutineExceptionHandler`, `SupervisorJob`, `try-catch`, `runCatching`을 조합한 계층적 예외 처리 전략을 설계하라. 각 계층에서 어떤 도구를 쓸지, 그리고 예외가 삼켜지는(silently swallowed) 위험을 어떻게 방지하는지 설명하라.

---

**🧒 12살 비유:**
대형 공장에서 1000개의 컨베이어 벨트가 동시에 돌아가고 있다고 상상하자. 벨트 하나가 고장 나면 그 벨트만 멈추고 수리해야지, 공장 전체를 정지시키면 안 된다. `SupervisorJob`은 "각 벨트가 독립적으로 동작하게 하는 설계"다. `CoroutineExceptionHandler`는 "고장 난 벨트를 감지해서 관리실에 알려주는 센서"다. 문제는 센서가 고장을 감지했는데 아무한테도 안 알리면(예외가 삼켜지면) 불량품이 그대로 출하된다는 것이다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
Staff 레벨에서는 단일 코루틴의 예외 처리가 아닌, 시스템 수준의 예외 전략 설계 능력을 평가한다. 특히 "예외가 삼켜지는 것"은 프로덕션에서 가장 위험한 버그 중 하나이며, 이를 구조적으로 방지하는 설계를 요구한다.

**Step 2 — 핵심 기술 설명**

예외 처리 도구별 동작 범위:

```
┌──────────────────────────────────────────────────────┐
│ Layer 1: CoroutineExceptionHandler (최후의 안전망)     │
│  - launch의 uncaught exception만 처리                │
│  - async에는 동작하지 않음 (await()에서 노출)          │
│  - root coroutine에만 설치 가능                      │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │ Layer 2: SupervisorJob/supervisorScope        │    │
│  │  - 자식 실패가 형제/부모에 전파 안 됨           │    │
│  │  - launch 자식: CEH로 전달                    │    │
│  │  - async 자식: await()에서 throw              │    │
│  │                                              │    │
│  │  ┌──────────────────────────────────┐        │    │
│  │  │ Layer 3: try-catch / runCatching  │        │    │
│  │  │  - 개별 코루틴 내부의 예외 처리    │        │    │
│  │  │  - 비즈니스 로직 수준의 에러 핸들링 │        │    │
│  │  └──────────────────────────────────┘        │    │
│  └──────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

핵심 규칙:
1. `CoroutineExceptionHandler`는 `launch`의 uncaught exception만 잡는다. `async`에는 **무효**다
2. `SupervisorJob` 없이 CEH를 자식 코루틴에 설치하면 — 동작하지 않는다 (자식의 예외는 부모로 전파되기 때문)
3. `runCatching`으로 `CancellationException`을 잡으면 코루틴 취소가 깨진다

**Step 3 — 다양한 관점**

예외가 삼켜지는 5가지 시나리오:

| 시나리오 | 원인 | 결과 |
|----------|------|------|
| `launch` + 빈 `catch {}` | 개발자 실수 | 무음 실패 |
| `async` without `await()` | Deferred 결과 무시 | 예외 소멸 |
| `runCatching`으로 CancellationException 포착 | 취소 신호 차단 | 코루틴이 안 죽음 |
| `Flow.catch {}`에서 로깅만 하고 재throw 안 함 | 의도적이지만 위험 | 다운스트림 모름 |
| CEH에서 로깅만 하고 알림 안 함 | 모니터링 부재 | 장애 미감지 |

**Step 4 — 구체적 예시**

```kotlin
@Component
class EventProcessingEngine(
    private val eventHandlers: Map<String, EventHandler>,
    private val meterRegistry: MeterRegistry,
    private val alertService: AlertService
) {
    // Layer 1: 최후의 안전망 — 여기까지 온 예외는 버그
    private val exceptionHandler = CoroutineExceptionHandler { ctx, throwable ->
        val eventType = ctx[EventTypeKey]?.type ?: "unknown"
        logger.error(throwable) { "Unhandled exception in event processing: $eventType" }
        meterRegistry.counter(
            "events.unhandled_exception", "type", eventType
        ).increment()
        // 프로덕션에서는 알림 필수
        alertService.critical("Unhandled coroutine exception", throwable)
    }

    // Layer 2: SupervisorScope로 이벤트 간 격리
    private val processingScope = CoroutineScope(
        SupervisorJob() + Dispatchers.Default + exceptionHandler
    )

    fun processEvents(events: List<Event>) {
        events.forEach { event ->
            processingScope.launch(EventTypeKey(event.type)) {
                // Layer 3: 개별 이벤트 내부의 비즈니스 예외 처리
                processWithRetry(event)
            }
        }
    }

    private suspend fun processWithRetry(event: Event, maxRetries: Int = 3) {
        var lastException: Throwable? = null
        repeat(maxRetries) { attempt ->
            try {
                eventHandlers[event.type]?.handle(event)
                    ?: throw UnknownEventTypeException(event.type)
                meterRegistry.counter("events.processed", "type", event.type).increment()
                return // 성공 시 즉시 반환
            } catch (e: CancellationException) {
                throw e // 절대 삼키면 안 됨!
            } catch (e: RetryableException) {
                lastException = e
                delay((1000L * (attempt + 1)).coerceAtMost(5000L)) // backoff
                meterRegistry.counter("events.retry", "type", event.type).increment()
            } catch (e: NonRetryableException) {
                logger.warn(e) { "Non-retryable failure for event ${event.id}" }
                deadLetterQueue.send(event, e)
                meterRegistry.counter("events.dlq", "type", event.type).increment()
                return
            }
            // 그 외 예외는 catch하지 않음 → Layer 1(CEH)로 전파
        }
        // 재시도 소진
        logger.error(lastException) { "All retries exhausted for event ${event.id}" }
        deadLetterQueue.send(event, lastException!!)
    }

    fun shutdown() {
        processingScope.cancel("Application shutting down")
    }
}

// CancellationException 안전한 runCatching 확장
suspend inline fun <T> runSuspendCatching(block: () -> T): Result<T> {
    return try {
        Result.success(block())
    } catch (e: CancellationException) {
        throw e // 항상 재throw
    } catch (e: Throwable) {
        Result.failure(e)
    }
}

// Context Element로 이벤트 타입 전달
data class EventTypeKey(val type: String) : CoroutineContext.Element {
    companion object Key : CoroutineContext.Key<EventTypeKey>
    override val key: CoroutineContext.Key<*> get() = Key
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| CEH + SupervisorJob (위 패턴) | 계층적 격리, 모니터링 통합 | 설계 복잡도, CEH/async 함정 | 이벤트 처리, 백그라운드 작업 |
| Channel + Actor 패턴 | 순서 보장, 백프레셔 내장 | 구현 복잡, Channel API 변경 중 | 순서 중요한 이벤트 |
| Flow.catch + retry 연산자 | 선언적, 조합 용이 | cold stream 재구독 비용 | 스트리밍 데이터 처리 |
| Spring @Async + CompletableFuture | Spring 통합 용이 | 코루틴 장점 포기, 스레드 풀 관리 | 레거시 마이그레이션 |

**Step 6 — 성장 & 심화 학습**
- `kotlin.runCatching`이 CancellationException을 잡는 문제 — Arrow의 `Either`나 커스텀 `runSuspendCatching` 사용
- Structured Concurrency와 Reactive Streams의 에러 모델 비교 (코루틴 예외 vs `onErrorResume`)
- kotlinx.coroutines의 `CoroutineExceptionHandler`와 Thread.UncaughtExceptionHandler의 관계
- 분산 시스템에서의 Dead Letter Queue 패턴과 코루틴 예외의 연결

**🎯 면접관 평가 기준:**
- **L6 PASS**: 3계층 예외 처리 전략 설명, CancellationException 재throw 필수성, CEH가 async에 무효인 이유
- **L7 EXCEED**: 예외가 삼켜지는 5가지 시나리오 열거, 모니터링/알림 통합, DLQ 패턴 연계, 팀 가이드라인 수립
- 🚩 **RED FLAG**: `catch(e: Exception) {}`으로 모든 예외 삼킴, CancellationException 특수 처리 모름, CEH를 자식 코루틴에 설치

---

## 2. Flow & Reactive

### Q4: Cold Flow vs Hot Flow (StateFlow/SharedFlow) 선택 전략

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Flow & Reactive

**Question:**
`Flow`, `StateFlow`, `SharedFlow`의 내부 구현 차이를 설명하라. 실시간 가격 피드 시스템에서 수천 명의 구독자에게 데이터를 전달할 때, 각각의 장단점은 무엇인가? `replay`와 `extraBufferCapacity`의 조합이 메모리와 데이터 신선도에 미치는 영향을 분석하라.

---

**🧒 12살 비유:**
Cold `Flow`는 넷플릭스다 — 누군가 재생 버튼을 누를 때마다 처음부터 새로 보여준다. 100명이 보면 100번 따로 재생한다. `SharedFlow`는 라디오 방송이다 — 방송국은 한 번만 방송하고 듣는 사람이 몇 명이든 같은 내용을 들을 수 있다. `StateFlow`는 전광판이다 — 항상 최신 점수만 보여주고, 지나간 점수는 알 수 없다. 새로 온 사람도 현재 점수는 바로 볼 수 있다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
면접관은 reactive stream의 cold/hot 개념을 단순 암기가 아니라 실제 시스템 설계에 적용하는 능력을 본다. 특히 멀티 구독자 시나리오에서의 리소스 효율성, 데이터 일관성, 메모리 관리 능력이 핵심이다.

**Step 2 — 핵심 기술 설명**

```kotlin
// Cold Flow: 수집할 때마다 새로 실행 (producer per collector)
fun pricesFeed(): Flow<Price> = flow {
    while (currentCoroutineContext().isActive) {
        emit(exchangeApi.getLatestPrice()) // 수집자마다 API 호출
        delay(100)
    }
}
// 문제: 구독자 1000명이면 API 호출 1000배

// SharedFlow: 하나의 producer, 다수의 collector
private val _prices = MutableSharedFlow<Price>(
    replay = 1,               // 새 구독자에게 마지막 1개 즉시 전달
    extraBufferCapacity = 64, // emit이 collector 속도에 블록되지 않도록
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
val prices: SharedFlow<Price> = _prices.asSharedFlow()

// StateFlow: SharedFlow(replay=1)의 특수 케이스 + conflation + equality check
private val _currentPrice = MutableStateFlow(Price.ZERO)
val currentPrice: StateFlow<Price> = _currentPrice.asStateFlow()
// 특징: 같은 값을 emit하면 구독자에게 전달되지 않음 (distinctUntilChanged 내장)
```

내부 구현 차이:
- `Flow`: 단순 `suspend fun collect()` — 람다 실행의 연속
- `SharedFlow`: 내부에 `SharedFlowSlot[]` 배열로 구독자 관리, `replay` 캐시용 circular buffer
- `StateFlow`: `SharedFlow(replay=1, BufferOverflow.DROP_OLDEST)` + `distinctUntilChanged` + 항상 초기값 보유. `value` 프로퍼티로 non-suspend 접근 가능

**Step 3 — 다양한 관점**

| 특성 | Flow (Cold) | SharedFlow (Hot) | StateFlow (Hot) |
|------|-------------|-------------------|-----------------|
| 생산 시점 | collect 시 | 독립적 (구독자 무관) | 독립적 |
| 구독자 0명일 때 | 미실행 | emit 가능 (버퍼 or 드랍) | 값 보유, 대기 |
| 중복 값 | 모두 전달 | 모두 전달 | 무시 (equality check) |
| 초기값 | 없음 | replay 설정에 따라 | 필수 (항상 존재) |
| 적합한 곳 | DB 쿼리, 1회성 API | 이벤트 스트림, 채팅 메시지 | UI 상태, 현재 설정값 |

**Step 4 — 구체적 예시**

```kotlin
@Service
class RealTimePriceFeedService(
    private val exchangeClient: ExchangeClient,
    private val meterRegistry: MeterRegistry
) {
    // 전략: Cold Flow를 SharedFlow로 변환하여 단일 upstream 유지
    private val _priceUpdates = MutableSharedFlow<PriceUpdate>(
        replay = 1,
        extraBufferCapacity = 256,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    // 현재가: StateFlow로 conflation (같은 가격이면 무시)
    private val _latestPrices = MutableStateFlow<Map<String, Price>>(emptyMap())
    val latestPrices: StateFlow<Map<String, Price>> = _latestPrices.asStateFlow()

    // 가격 히스토리 스트림: SharedFlow (모든 변경 이벤트 전달)
    val priceStream: SharedFlow<PriceUpdate> = _priceUpdates.asSharedFlow()

    @PostConstruct
    fun startFeed() {
        // 단일 upstream — 구독자 수에 무관하게 API 호출 1회
        scope.launch {
            exchangeClient.priceStream()     // suspend fun → Flow<RawPrice>
                .map { raw -> raw.toPriceUpdate() }
                .onEach { update ->
                    _latestPrices.update { current ->
                        current + (update.symbol to update.price)
                    }
                    meterRegistry.counter("price.updates", "symbol", update.symbol).increment()
                }
                .retry(3) { e ->
                    e is IOException && run {
                        delay(1000)
                        true
                    }
                }
                .catch { e ->
                    logger.error(e) { "Price feed failed permanently" }
                    alertService.critical("Price feed down", e)
                }
                .collect { update ->
                    _priceUpdates.emit(update)
                }
        }
    }
}

// REST SSE 엔드포인트 — 수천 클라이언트가 동일 SharedFlow 구독
@RestController
class PriceController(private val feedService: RealTimePriceFeedService) {

    @GetMapping("/prices/stream", produces = [MediaType.TEXT_EVENT_STREAM_VALUE])
    fun streamPrices(@RequestParam symbols: List<String>): Flow<ServerSentEvent<PriceUpdate>> {
        return feedService.priceStream
            .filter { it.symbol in symbols }
            .map { update ->
                ServerSentEvent.builder(update)
                    .id(update.id)
                    .event("price-update")
                    .build()
            }
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| `shareIn(scope, SharingStarted.WhileSubscribed())` | 구독자 없으면 자동 정지, 리소스 절약 | 재시작 딜레이, 첫 구독 시 cold start | 간헐적 구독 |
| `shareIn(scope, SharingStarted.Eagerly)` | 항상 최신 데이터 유지 | 구독자 없어도 리소스 사용 | 실시간 필수 시스템 |
| `stateIn` | 항상 최신 값, non-suspend 접근 | conflation으로 중간 값 소실 | 설정, 상태 관리 |
| Reactor `Flux.share()` | Java 생태계 통합 | 코루틴 비호환, 학습 비용 | 기존 WebFlux 프로젝트 |

**Step 6 — 성장 & 심화 학습**
- `SharingStarted.WhileSubscribed(stopTimeoutMillis, replayExpirationMillis)` 파라미터 튜닝
- `SharedFlow`의 `subscriptionCount`를 활용한 동적 upstream 제어
- Flow의 `conflate()` vs `buffer(CONFLATED)` 차이
- Kotlin/JS, Kotlin/Native에서의 Flow 동작 차이

**🎯 면접관 평가 기준:**
- **L6 PASS**: Cold/Hot 차이 명확히 설명, 멀티 구독자에서 Cold Flow의 리소스 문제 인지, shareIn/stateIn 적절한 사용
- **L7 EXCEED**: replay/buffer 설정의 메모리 영향 분석, WhileSubscribed의 timeout 파라미터 최적화, 시스템 설계 수준의 선택 근거 제시
- 🚩 **RED FLAG**: "StateFlow는 LiveData의 코루틴 버전", SharedFlow와 Channel 혼동

---

### Q5: Flow의 Backpressure와 Buffer 전략

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Flow & Reactive

**Question:**
Kotlin Flow에서 producer가 consumer보다 빠를 때 어떤 일이 발생하는가? `buffer()`, `conflate()`, `collectLatest()`의 내부 동작 방식과 각각이 적합한 시나리오를 설명하라. Reactive Streams의 `request(n)` 기반 backpressure와 Flow의 suspension 기반 backpressure는 근본적으로 어떻게 다른가?

---

**🧒 12살 비유:**
초밥 레스토랑의 컨베이어 벨트를 생각하자. `buffer()`는 벨트를 길게 만드는 것이다 — 요리사가 빨리 만들어도 벨트 위에 쌓아둔다. `conflate()`는 "같은 종류 초밥이면 최신 것만 남기기"다. `collectLatest()`는 "새 초밥이 오면 지금 먹고 있던 것을 버리고 새 걸 먹기"다. Reactive Streams의 `request(n)`은 "나 3개만 줘"라고 요리사에게 주문하는 것이고, Flow의 방식은 "내가 다 먹을 때까지 요리사가 기다리기"다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
backpressure는 프로덕션 시스템의 안정성에 직결된다. OOM이나 unbounded queue 증가를 방지하려면 producer/consumer 속도 불일치를 체계적으로 관리해야 한다. 면접관은 이 개념의 이론적 이해와 실무 적용 능력을 동시에 본다.

**Step 2 — 핵심 기술 설명**

Flow의 backpressure는 **suspension 기반**이다. 기본적으로 `emit()`과 `collect()`는 같은 코루틴에서 순차 실행되므로, consumer가 처리를 마칠 때까지 producer가 자동으로 중단된다:

```kotlin
// 기본 동작: emit은 collect가 끝날 때까지 suspend됨
flow {
    repeat(1000) {
        emit(it)          // collect의 처리가 끝날 때까지 여기서 중단
        println("emitted $it")
    }
}.collect { value ->
    delay(1000)           // 느린 consumer
    println("collected $value")
}
// 출력: emitted 0 → collected 0 → emitted 1 → collected 1 → ...
// 완전히 순차적, 같은 코루틴에서 실행
```

`buffer()`의 내부 동작:

```kotlin
// buffer()는 producer와 consumer를 별도 코루틴으로 분리
// 내부적으로 Channel을 사용하여 비동기화
flow {
    repeat(1000) { emit(it) } // 별도 코루틴에서 Channel로 send
}
.buffer(capacity = 64, onBufferOverflow = BufferOverflow.SUSPEND)
// BufferOverflow.SUSPEND: 버퍼 가득 차면 emit 중단 (기본)
// BufferOverflow.DROP_OLDEST: 가장 오래된 값 버림
// BufferOverflow.DROP_LATEST: 새 값 버림
.collect { process(it) }  // 별도 코루틴에서 Channel로부터 receive

// conflate() = buffer(CONFLATED) = buffer(1, DROP_OLDEST)와 유사
// 항상 최신 값만 유지, 중간 값은 소실

// collectLatest: 새 값이 오면 이전 collect 블록을 취소하고 재시작
flow.collectLatest { value ->
    // 이 블록이 실행 중에 새 값이 오면, 이 블록은 취소됨
    val result = heavyProcessing(value) // 여기서 취소 가능
    updateUI(result) // 새 값이 안 왔으면 여기까지 실행
}
```

Reactive Streams(`request(n)`) vs Flow(suspension) 비교:

```
Reactive Streams:
  Subscriber --request(10)--> Publisher
  Publisher  --onNext(1..10)--> Subscriber
  Subscriber --request(5)---> Publisher
  → pull 기반, consumer가 demand를 명시적으로 선언

Flow:
  emit() ←───suspend───→ collect()
  → 코루틴 suspension으로 자동 조절, demand 개념 없음
  → producer/consumer가 같은 코루틴이면 순차, buffer()로 분리하면 Channel 기반
```

**Step 3 — 다양한 관점**

| 전략 | 데이터 보존 | 레이턴시 | 메모리 | 적합한 곳 |
|------|------------|---------|--------|-----------|
| 기본 (unbuffered) | 100% | 높음 (순차) | 최소 | 순서 보장 필수 |
| `buffer(64)` | 100% (버퍼 내) | 중간 | 버퍼 크기만큼 | 배치 처리 |
| `conflate()` | 최신 값만 | 최소 | 최소 | 센서 데이터, 최신 상태 |
| `collectLatest` | 최신 값만 | 최소 | 처리 중인 것만 | 검색 자동완성, UI 업데이트 |
| `buffer(DROP_OLDEST)` | 최신 N개 | 낮음 | 고정 | 로그, 메트릭 |

**Step 4 — 구체적 예시**

```kotlin
@Service
class SensorDataProcessor(
    private val sensorGateway: SensorGateway,
    private val anomalyDetector: AnomalyDetector,
    private val timeSeriesDb: TimeSeriesRepository
) {
    // 시나리오: IoT 센서 1000개에서 초당 10개씩 데이터 유입 (10,000 events/sec)

    // 전략 1: 실시간 이상 탐지 — conflate (최신 값만 중요)
    suspend fun monitorAnomalies() {
        sensorGateway.dataStream()
            .conflate()  // 센서 값이 밀리면 최신 값만 분석
            .collect { reading ->
                val result = anomalyDetector.analyze(reading)
                if (result.isAnomaly) {
                    alertService.fire(result)
                }
            }
    }

    // 전략 2: 시계열 저장 — buffer + 배치 (모든 데이터 보존)
    suspend fun persistReadings() {
        sensorGateway.dataStream()
            .buffer(capacity = 1024, onBufferOverflow = BufferOverflow.SUSPEND)
            .chunked(100)  // 100개씩 배치
            .collect { batch ->
                timeSeriesDb.batchInsert(batch)  // 배치 insert가 단건보다 10x 빠름
            }
    }

    // 전략 3: 대시보드 갱신 — collectLatest (렌더링 도중 새 데이터 오면 재시작)
    suspend fun updateDashboard() {
        sensorGateway.aggregatedStream()
            .collectLatest { snapshot ->
                // 무거운 집계 도중 새 스냅샷이 오면 이 블록은 취소됨
                val aggregated = withContext(Dispatchers.Default) {
                    statisticsEngine.compute(snapshot)  // CPU-intensive
                }
                dashboardService.push(aggregated)
            }
    }
}

// chunked 확장 함수 (Flow에는 기본 제공 안 됨)
fun <T> Flow<T>.chunked(size: Int): Flow<List<T>> = flow {
    val buffer = mutableListOf<T>()
    collect { value ->
        buffer.add(value)
        if (buffer.size >= size) {
            emit(buffer.toList())
            buffer.clear()
        }
    }
    if (buffer.isNotEmpty()) emit(buffer.toList())
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| Flow + buffer | 코루틴 네이티브, 단순 | Reactive Streams 대비 연산자 부족 | Kotlin-first 프로젝트 |
| Reactor Flux | 풍부한 연산자, backpressure 정교 | 학습 곡선, 디버깅 어려움 | 기존 WebFlux 생태계 |
| Channel (producer pattern) | 양방향 통신, select 가능 | 구조화된 동시성 깨지기 쉬움 | Fan-out/fan-in |
| `callbackFlow` | callback API 통합 | 버퍼 오버플로 관리 필요 | 레거시 listener 통합 |

**Step 6 — 성장 & 심화 학습**
- `flowOn()`과 `buffer()`의 관계 (flowOn은 내부적으로 buffer를 사용)
- `produceIn()`과 `receiveAsFlow()`를 통한 Channel-Flow 상호 변환
- Project Reactor의 `onBackpressureBuffer/Drop/Latest`와 Flow 전략의 1:1 매핑
- Virtual Thread 환경에서 Flow backpressure의 의미 변화

**🎯 면접관 평가 기준:**
- **L6 PASS**: suspension 기반 backpressure 설명, buffer/conflate/collectLatest 적합한 사용처 제시
- **L7 EXCEED**: Reactive Streams의 request(n)과의 근본적 차이 분석, Channel 기반 내부 구현 이해, 시스템 수준 backpressure 전략 설계
- 🚩 **RED FLAG**: "Flow는 backpressure가 없다", buffer 크기 설정의 메모리 영향 고려 못 함

---

### Q6: callbackFlow와 Flow-Reactive 통합

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Flow & Reactive

**Question:**
레거시 Java 라이브러리가 callback 기반 API를 제공한다. 이를 Kotlin Flow로 래핑할 때 `callbackFlow`를 사용하는데, `awaitClose`를 빼먹으면 어떤 일이 발생하는가? `channelFlow`와의 차이는 무엇인가? Spring WebFlux 환경에서 `Flow`와 `Flux`를 상호 변환할 때의 주의점을 설명하라.

---

**🧒 12살 비유:**
`callbackFlow`는 전화 통역사다. 외국어를 사용하는 사람(callback API)이 말할 때마다 통역사가 한국어(Flow)로 번역해서 전달한다. `awaitClose`는 "통화가 끝나면 전화를 끊는다"는 약속이다. 이걸 안 하면 통화가 끝났는데도 전화기를 붙들고 있어서 전화비가 계속 나간다(리소스 누수). `channelFlow`는 여러 사람이 동시에 번역할 수 있는 회의 통역 시스템이다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
실무에서 callback 기반 라이브러리(AWS SDK v1, gRPC StreamObserver, WebSocket 등)를 코루틴으로 래핑하는 것은 매우 흔한 작업이다. 리소스 누수와 동시성 안전성은 Staff 레벨에서 반드시 관리할 줄 알아야 한다.

**Step 2 — 핵심 기술 설명**

```kotlin
// callbackFlow: callback → Flow 브릿지
fun WebSocket.messagesFlow(): Flow<Message> = callbackFlow {
    val listener = object : WebSocketListener() {
        override fun onMessage(ws: WebSocket, msg: String) {
            // trySend: non-suspend, Channel에 전송 (실패 시 ChannelResult 반환)
            trySend(Message.parse(msg)).onFailure {
                logger.warn { "Buffer full, dropping message" }
            }
        }
        override fun onFailure(ws: WebSocket, t: Throwable, response: Response?) {
            close(t) // Flow를 에러로 종료
        }
        override fun onClosed(ws: WebSocket, code: Int, reason: String) {
            close() // Flow를 정상 종료
        }
    }

    val ws = this@messagesFlow
    ws.addListener(listener)

    // awaitClose: collector가 취소될 때까지 suspend
    // 이 블록 안에서 cleanup 수행
    awaitClose {
        ws.removeListener(listener)
        ws.close(1000, "Flow cancelled")
    }
}
```

`awaitClose`를 빼먹으면:
1. `callbackFlow` 블록이 즉시 완료됨
2. 내부적으로 `ProducerCoroutine`이 종료되어 Channel이 닫힘
3. 이후 callback에서 `trySend()`하면 `ClosedSendChannelException`
4. **listener가 해제되지 않아 메모리 누수** — GC root로 유지됨
5. 런타임에 `IllegalStateException: 'awaitClose { yourCallbackOrListener.cancel() }' should be used in the end of callbackFlow block` 경고 발생

`channelFlow` vs `callbackFlow`:

```kotlin
// channelFlow: 여러 코루틴에서 동시에 emit 가능
fun mergedFeeds(): Flow<FeedItem> = channelFlow {
    launch { feedA.collect { send(it) } }  // 별도 코루틴
    launch { feedB.collect { send(it) } }  // 병렬 수집
    launch { feedC.collect { send(it) } }
}
// callbackFlow는 channelFlow의 특수 케이스:
// - awaitClose 강제
// - callback 등록/해제 패턴에 최적화
// channelFlow는 범용 멀티코루틴 emit용
```

**Step 3 — 다양한 관점**

Flow-Flux 상호 변환 주의점:

```kotlin
// Flow → Flux (Spring에서 자동 변환)
@GetMapping("/stream", produces = [MediaType.TEXT_EVENT_STREAM_VALUE])
fun stream(): Flow<Data> = dataFlow  // Spring이 내부적으로 asFlux()

// Flux → Flow
val flow: Flow<Data> = flux.asFlow()  // kotlinx-coroutines-reactor

// 주의점 1: Context 전파
// Reactor Context ≠ CoroutineContext
// ReactorContext 브릿지를 통해 전파해야 함
flux.asFlow()
    .flowOn(ReactorContext(reactorContext)) // Reactor Context를 코루틴으로 전달

// 주의점 2: 취소 전파
// Flow 취소 → Flux subscription 취소 (자동)
// Flux 에러 → Flow 예외 (자동)
// 그러나 Flux의 timeout 연산자는 Flow의 withTimeout과 다르게 동작

// 주의점 3: Backpressure 모델 차이
// Flux: request(n) 기반 — subscriber가 명시적으로 demand 선언
// Flow: suspension 기반 — collect의 속도가 자동으로 producer를 조절
// 변환 시 bridge가 내부적으로 request(1)을 반복 호출
```

**Step 4 — 구체적 예시**

```kotlin
// gRPC StreamObserver를 Flow로 래핑
fun <T> StreamObserver<T>.asFlow(): Flow<T> = callbackFlow {
    val delegate = object : StreamObserver<T> {
        override fun onNext(value: T) {
            // Channel이 닫혀 있으면 조용히 무시
            trySend(value).onClosed {
                logger.debug { "Channel closed, ignoring onNext" }
            }
        }
        override fun onError(t: Throwable) {
            close(t)
        }
        override fun onCompleted() {
            close()
        }
    }

    // gRPC 스트림 시작
    val call = grpcStub.streamingCall(request, delegate)

    awaitClose {
        // Flow 취소 시 gRPC 호출도 취소
        call.cancel("Flow collector cancelled", null)
    }
}

// AWS SDK v2 paginator를 Flow로
fun S3Client.listObjectsFlow(bucket: String): Flow<S3Object> = flow {
    var continuationToken: String? = null
    do {
        val response = listObjectsV2 {
            this.bucket = bucket
            this.continuationToken = continuationToken
        }
        response.contents().forEach { emit(it) }
        continuationToken = response.nextContinuationToken()
    } while (response.isTruncated)
}

// Spring WebFlux에서 Flow/Flux 혼용 서비스
@Service
class HybridService(
    private val reactiveRedis: ReactiveRedisTemplate<String, String>, // Flux 반환
    private val coroutineService: SuspendingService                   // suspend fun
) {
    // Flux API를 코루틴에서 사용
    suspend fun getCachedOrCompute(key: String): String {
        return reactiveRedis.opsForValue()
            .get(key)
            .awaitSingleOrNull()  // Mono → suspend
            ?: coroutineService.compute(key).also { result ->
                reactiveRedis.opsForValue()
                    .set(key, result, Duration.ofMinutes(10))
                    .awaitSingle()
            }
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| `callbackFlow` | 안전한 리소스 관리, awaitClose 강제 | callback 스레드에서 trySend (blocking 위험) | Listener/Callback 래핑 |
| `channelFlow` | 멀티 코루틴 emit, 유연 | awaitClose 미강제, 실수 가능 | 여러 Flow 병합 |
| `suspendCancellableCoroutine` | 단건 callback → suspend 변환 | 스트림에 부적합 | 단건 비동기 API |
| Reactor 어댑터 직접 사용 | 변환 오버헤드 없음 | 두 패러다임 혼용 복잡 | Flux 네이티브 유지 필요 시 |

**Step 6 — 성장 & 심화 학습**
- `callbackFlow`에서 `trySend` vs `send`의 선택 기준 (callback 스레드 blocking 여부)
- `channelFlow` 내부의 `ProducerScope`와 `Channel.BUFFERED` 기본 설정
- Kotlin 2.0의 `Flow.merge()` 최적화와 `channelFlow` 대체 가능성
- `kotlinx-coroutines-reactor` 모듈의 `ReactorContext` 브릿지 내부

**🎯 면접관 평가 기준:**
- **L6 PASS**: callbackFlow/awaitClose 역할 명확히 설명, 리소스 누수 시나리오 인지, Flow-Flux 변환 가능
- **L7 EXCEED**: trySend의 스레드 안전성, Reactor Context 전파 문제, backpressure 모델 차이 분석, 팀 래핑 가이드라인 제시
- 🚩 **RED FLAG**: awaitClose 없이 callbackFlow 작성, send(blocking)를 callback 스레드에서 호출

---


## 3. JVM Internals

### Q7: GC 알고리즘 비교 — G1 vs ZGC vs Shenandoah

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: JVM Internals

**Question:**
G1, ZGC, Shenandoah GC 각각의 핵심 설계 철학과 내부 동작 방식을 설명하라. 코루틴 기반 Spring Boot 서비스(평균 힙 4GB, P99 레이턴시 목표 50ms)에서 어떤 GC를 선택할지, 그리고 그 튜닝 전략은 무엇인가? GC가 코루틴의 suspension/resumption에 미치는 영향을 분석하라.

---

**🧒 12살 비유:**
GC는 방 청소하는 로봇이다. G1 로봇은 "방을 구역으로 나누고, 쓰레기가 많은 구역부터 청소"한다 — 때때로 청소하느라 잠깐 멈추지만 예측 가능하다. ZGC 로봇은 "사람들이 놀고 있는 동안에도 동시에 청소"하는 닌자 로봇이다 — 거의 멈추지 않지만 청소 도구가 비싸다. Shenandoah 로봇은 ZGC와 비슷한 닌자지만 "집이 작아도 잘 청소"한다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
Staff 레벨 엔지니어는 GC 선택이 SLO(P99 레이턴시)에 직접적 영향을 미치는 것을 이해하고, 워크로드 특성에 맞는 GC를 선택/튜닝할 수 있어야 한다. 특히 코루틴 기반 시스템은 수십만 개의 짧은 수명 객체(continuation)를 생성하므로 GC 전략이 중요하다.

**Step 2 — 핵심 기술 설명**

```
G1 (Garbage-First):
  - 힙을 동일 크기 Region(1-32MB)으로 분할
  - Young GC: Eden/Survivor region 수집 (STW, 보통 5-10ms)
  - Mixed GC: Young + 쓰레기 비율 높은 Old region 함께 수집
  - Full GC: 최후의 수단 (긴 STW — 이걸 방지하는 게 튜닝 목표)
  - 핵심: -XX:MaxGCPauseMillis 목표를 맞추기 위해 region 수를 조절
  - JDK 17+ 기본 GC

ZGC (Z Garbage Collector):
  - Colored Pointers: 객체 포인터에 메타데이터 비트 내장 (marked0, marked1, remapped, finalizable)
  - Load Barrier: 객체 참조 로드 시마다 barrier 코드 실행 → concurrent relocation 가능
  - 거의 모든 작업이 concurrent (STW < 1ms, 힙 크기 무관)
  - JDK 21+에서 Generational ZGC 도입 — young/old 분리로 처리량 향상
  - 단점: 메모리 오버헤드 (colored pointers), CPU 오버헤드 (load barrier)

Shenandoah:
  - Brooks Pointer: 모든 객체에 forwarding pointer 추가 (8바이트 오버헤드/객체)
  - Concurrent compaction: G1과 달리 compaction도 concurrent
  - STW: init-mark, final-mark만 (< 1ms)
  - 장점: ZGC보다 작은 힙에서도 효과적
  - 단점: forwarding pointer 메모리 오버헤드, Oracle JDK에 미포함 (OpenJDK만)
```

코루틴과 GC의 상호작용:

```kotlin
// 코루틴이 생성하는 객체들:
// 1. Continuation 객체 (suspend 함수마다 1개)
// 2. CoroutineContext 체인 (CombinedContext linked list)
// 3. Job 트리 노드
// 4. Channel 내부 버퍼 (Segment 기반 linked list)

// suspend fun이 많은 시스템의 특성:
// - 다수의 단명(short-lived) 객체 → Young GC 빈도 증가
// - 중단된 코루틴의 continuation은 장수(long-lived) → Old Gen으로 promotion
// - STW가 발생하면 모든 코루틴이 resume 불가 → P99 tail latency 증가
```

**Step 3 — 다양한 관점**

| 기준 | G1 | ZGC | Shenandoah |
|------|-----|-----|------------|
| 최대 STW | 10-200ms (튜닝 가능) | < 1ms | < 1ms |
| 처리량 (throughput) | 높음 | 중간 (load barrier 비용) | 중간 |
| 메모리 오버헤드 | 낮음 | 높음 (colored pointers) | 중간 (forwarding ptr) |
| 최소 권장 힙 | 1GB+ | 2GB+ | 1GB+ |
| 튜닝 복잡도 | 중간 (여러 플래그) | 낮음 (거의 플래그 불요) | 낮음 |
| JDK 버전 | 8+ (기본 11+) | 15+ (prod-ready 17+) | 12+ (OpenJDK만) |

코루틴 서비스에서의 영향:

```
P99 latency = application_time + GC_pause_time + scheduling_delay

G1 (MaxGCPauseMillis=20):
  - Young GC 10ms × 빈번 = P99에 간헐적 스파이크
  - Mixed GC 30-50ms = P99 초과 가능
  - 코루틴 수천 개의 continuation이 Old Gen으로 가면 Mixed GC 빈도 증가

ZGC:
  - STW < 1ms → P99에 GC 영향 거의 없음
  - load barrier로 인한 전체적 throughput 5-10% 감소
  - 코루틴 시스템에 적합 (STW 최소화가 최우선)

Shenandoah:
  - ZGC와 유사한 STW 특성
  - 더 작은 힙에서도 효과적 (4GB면 충분)
  - OpenJDK 환경이면 좋은 선택
```

**Step 4 — 구체적 예시**

```bash
# 시나리오: 코루틴 기반 API 서버, 힙 4GB, P99 목표 50ms

# 옵션 A: Generational ZGC (JDK 21+ 권장)
java -XX:+UseZGC -XX:+ZGenerational \
     -Xms4g -Xmx4g \
     -XX:SoftMaxHeapSize=3500m \
     -XX:+UseTransparentHugePages \
     -jar app.jar
# SoftMaxHeapSize: GC가 이 이하로 유지하려 노력 (탄력적 여유)

# 옵션 B: G1 (보수적 선택)
java -XX:+UseG1GC \
     -Xms4g -Xmx4g \
     -XX:MaxGCPauseMillis=15 \
     -XX:G1NewSizePercent=30 \
     -XX:G1MaxNewSizePercent=40 \
     -XX:G1HeapRegionSize=4m \
     -XX:InitiatingHeapOccupancyPercent=45 \
     -jar app.jar
# G1NewSizePercent 높게: 코루틴의 단명 객체가 많으므로 Young 비율 확대
# MaxGCPauseMillis=15: 여유를 두고 P99 50ms 충족

# 모니터링 필수 JVM 플래그
-Xlog:gc*:file=gc.log:time,uptime,level,tags:filecount=5,filesize=100m
-XX:+HeapDumpOnOutOfMemoryError
```

```kotlin
// GC 친화적 코루틴 코드 패턴
@Service
class GcFriendlyService {
    // BAD: suspend마다 새 객체 할당
    suspend fun processRequest(request: Request): Response {
        val context = RequestContext(request.id, request.headers) // 매번 할당
        val validated = ValidationResult(validate(request))       // 매번 할당
        return createResponse(context, validated)
    }

    // BETTER: 객체 재사용, inline 클래스 활용
    @JvmInline
    value class RequestId(val value: String) // 힙 할당 없음 (인라인됨)

    suspend fun processRequestOptimized(request: Request): Response {
        val id = RequestId(request.id) // boxing 없음
        val isValid = validate(request) // primitive boolean
        return if (isValid) successResponse(id) else errorResponse(id)
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| ZGC (Generational) | 초저지연, 튜닝 최소 | CPU/메모리 오버헤드, JDK 21+ | 레이턴시 최우선 API |
| G1 (튜닝됨) | 검증된 안정성, 높은 처리량 | 간헐적 STW 스파이크 | 배치/높은 처리량 |
| Shenandoah | 저지연 + 낮은 메모리 | Oracle JDK 미지원 | OpenJDK + 작은 힙 |
| GraalVM Native Image | GC 없음 (Serial GC) | 빌드 시간, 리플렉션 제한 | 서버리스, CLI |

**Step 6 — 성장 & 심화 학습**
- `jcmd <pid> GC.heap_info`와 `jfr` 기반 GC 분석
- Kotlin의 `@JvmInline value class`가 GC 부하를 줄이는 원리
- TLAB(Thread Local Allocation Buffer)과 코루틴의 관계 — 코루틴이 스레드를 자주 바꾸면 TLAB 효율 저하
- ZGC의 colored pointer가 CompressedOops와 호환 불가한 이유 (JDK 21에서 해결)

**🎯 면접관 평가 기준:**
- **L6 PASS**: G1/ZGC/Shenandoah 핵심 차이, 워크로드별 선택 근거, 기본 튜닝 플래그 제시
- **L7 EXCEED**: colored pointer/load barrier 내부 메커니즘, 코루틴-GC 상호작용, TLAB 영향, JFR 기반 분석
- 🚩 **RED FLAG**: "ZGC가 항상 최고", GC 튜닝 경험 없이 플래그만 나열

---

### Q8: JIT 컴파일러 — C1/C2/Graal 파이프라인

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: JVM Internals

**Question:**
JVM의 Tiered Compilation에서 C1과 C2 컴파일러는 각각 어떤 최적화를 수행하는가? 코루틴의 `suspend` 함수가 CPS(Continuation-Passing Style) 변환 후 JIT에 의해 최적화되는 과정을 설명하라. GraalVM JIT과 C2의 차이, 그리고 프로덕션에서 JIT warmup이 P99 레이턴시에 미치는 영향과 완화 전략은?

---

**🧒 12살 비유:**
JIT 컴파일러는 "자주 사용하는 레시피를 외우는 요리사"다. 처음에는 레시피(바이트코드)를 한 줄씩 읽으면서 요리한다(인터프리터). C1은 "빠르게 대충 외운다" — 속도는 좀 빨라지지만 최고 실력은 아니다. C2는 "완벽하게 외우고 변형까지 만든다" — 최고 속도지만 외우는 데 오래 걸린다. GraalVM은 "레시피를 분석해서 아예 새로운 요리법을 발명하는 천재 요리사"다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
JIT 동작을 이해하면 성능 벤치마크 해석, warmup 전략, 프로덕션 배포 시 cold start 문제를 해결할 수 있다. 특히 코루틴의 CPS 변환이 JIT에 미치는 영향은 Kotlin-specific 심화 주제다.

**Step 2 — 핵심 기술 설명**

Tiered Compilation (5 레벨):

```
Level 0: 인터프리터 (프로파일링 없음)
Level 1: C1 (간단한 최적화, 프로파일링 없음)
Level 2: C1 (제한적 프로파일링)
Level 3: C1 (전체 프로파일링) — 보통 여기서 먼저 실행
Level 4: C2 (공격적 최적화) — hot method가 여기로 승격

일반적 경로: L0 → L3 → L4
빠른 C2 가용 시: L0 → L4 (C1 스킵)
C2 큐 포화 시: L0 → L3 (C1에 머무름)
```

C1 vs C2 최적화 비교:

```
C1 최적화:
  - Inlining (작은 메서드)
  - 상수 전파 (constant folding)
  - Null check 제거 (간단한 경우)
  - 컴파일 시간: < 1ms

C2 최적화:
  - 공격적 Inlining (깊은 호출 체인)
  - Escape Analysis → 스택 할당 (힙 할당 회피)
  - Loop Unrolling, Vectorization (SIMD)
  - 분기 예측 기반 speculative optimization
  - 타입 추론 + deoptimization trap
  - 컴파일 시간: 수~수십 ms
```

코루틴 `suspend` 함수의 CPS 변환과 JIT:

```kotlin
// 소스 코드
suspend fun fetchUserData(id: String): UserData {
    val profile = userService.getProfile(id)    // suspension point 1
    val orders = orderService.getOrders(id)     // suspension point 2
    return UserData(profile, orders)
}

// CPS 변환 후 (Kotlin 컴파일러가 생성하는 바이트코드, 단순화):
fun fetchUserData(id: String, cont: Continuation<UserData>): Any? {
    val sm = cont as? FetchUserDataContinuation ?: FetchUserDataContinuation(cont)

    when (sm.label) {
        0 -> {
            sm.label = 1
            sm.id = id  // 로컬 변수를 Continuation 객체에 저장
            val result = userService.getProfile(id, sm)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            sm.result = result
        }
        1 -> {
            sm.profile = sm.result as Profile
            sm.label = 2
            val result = orderService.getOrders(sm.id, sm)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            sm.result = result
        }
        2 -> {
            sm.orders = sm.result as List<Order>
            return UserData(sm.profile, sm.orders)
        }
    }
    // ... (이후 label에 대한 처리)
}
```

JIT가 이 코드에 적용하는 최적화:
- **Switch → jump table**: label switch가 O(1) 점프로 변환
- **Escape Analysis**: Continuation 객체가 escape하지 않으면 스택 할당 (하지만 suspend되면 escape → 힙 할당 불가피)
- **Inlining**: 짧은 suspend 함수는 caller에 인라인 (하지만 CPS 변환이 메서드를 크게 만들어 인라인 임계값 초과 가능)
- **Type profiling**: `sm.result`의 실제 타입을 추적하여 checkcast 제거

**Step 3 — 다양한 관점**

JIT warmup이 P99에 미치는 영향:

```
Cold Start Timeline:
  0-5초:   인터프리터 → P99 200-500ms (10-50x 느림)
  5-15초:  C1 컴파일 → P99 100-200ms
  15-60초: C2 컴파일 → P99 30-50ms (목표 도달)
  60초+:   Steady State → P99 20-30ms

문제: 배포 직후 첫 트래픽이 SLO 위반
해결: warmup 전략 필요
```

**Step 4 — 구체적 예시**

```bash
# JIT 분석용 JVM 플래그
-XX:+PrintCompilation                    # 컴파일되는 메서드 로그
-XX:+UnlockDiagnosticVMOptions
-XX:+LogCompilation                      # 상세 JIT 로그 (XML)
-XX:+PrintInlining                       # 인라인 결정 추적

# Warmup 전략 1: Class Data Sharing (CDS)
# JDK 19+ AppCDS로 시작 시간 단축
java -XX:ArchiveClassesAtExit=app-cds.jsa -jar app.jar  # 1회 실행
java -XX:SharedArchiveFile=app-cds.jsa -jar app.jar       # 이후 실행

# Warmup 전략 2: JIT 프리컴파일 (AOT with Leyden, JDK 24+)
# Training Run → Profile → Production Run
java -XX:+PreserveFramePointer -XX:AOTMode=record -jar app.jar  # 프로파일 수집
java -XX:AOTMode=create -XX:AOTConfiguration=app.aotconf -jar app.jar  # AOT 생성
```

```kotlin
// Warmup 전략 3: 애플리케이션 레벨 warmup
@Component
class JitWarmupRunner(
    private val routes: List<RouteDefinition>,
    private val webTestClient: WebTestClient
) : ApplicationRunner {
    override fun run(args: ApplicationArguments) {
        // K8s readiness probe가 성공하기 전에 주요 경로 warmup
        runBlocking {
            repeat(1000) { // JIT C2 임계값 (기본 10,000이지만 tiered에서는 더 일찍)
                routes.forEach { route ->
                    launch(Dispatchers.IO) {
                        try {
                            webTestClient.get()
                                .uri(route.path)
                                .exchange()
                        } catch (_: Exception) { /* warmup 실패 무시 */ }
                    }
                }
            }
        }
        logger.info { "JIT warmup completed for ${routes.size} routes" }
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| Tiered (C1+C2) 기본 | 균형 잡힌 warmup vs peak | warmup 기간 존재 | 대부분의 서비스 |
| GraalVM JIT | 더 공격적 최적화, Peak 성능 우수 | 컴파일 시간 길다, 메모리 많이 사용 | 연산 집약 서비스 |
| GraalVM Native Image | 즉시 시작, warmup 없음 | 리플렉션 제한, 빌드 느림 | 서버리스, CLI |
| CRaC (Coordinated Restore at Checkpoint) | warmup된 상태에서 시작 | 체크포인트 관리, 파일 핸들 복원 | 빈번한 스케일링 |

**Step 6 — 성장 & 심화 학습**
- `jitwatch`로 JIT 컴파일 로그 시각화하여 핫 메서드 분석
- `@JvmStatic`, `@JvmOverloads`가 JIT 인라인 결정에 미치는 영향
- Project Leyden (JDK 24+): condensation 기반 ahead-of-time 최적화
- Kotlin compiler의 `-Xjvm-default=all` 플래그와 default method JIT 처리

**🎯 면접관 평가 기준:**
- **L6 PASS**: Tiered Compilation 레벨 설명, CPS 변환 개요, warmup 전략 1개 이상 제시
- **L7 EXCEED**: Escape Analysis와 코루틴 Continuation의 관계, JIT 로그 분석 경험, CRaC/Leyden 등 최신 솔루션
- 🚩 **RED FLAG**: "JIT가 알아서 최적화해준다"로 끝남, warmup 문제 인식 없음

---

### Q9: JVM 메모리 모델과 동시성

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: JVM Internals

**Question:**
JSR-133(Java Memory Model)에서 `happens-before` 관계를 설명하라. `volatile` 변수와 코루틴의 `Mutex`는 각각 어떤 메모리 가시성 보장을 제공하는가? Kotlin의 `@Volatile`과 `Atomic*` 클래스의 내부 동작 차이, 그리고 코루틴에서 공유 상태를 안전하게 관리하는 전략을 비교하라.

---

**🧒 12살 비유:**
컴퓨터의 CPU 코어들은 각자 "작은 메모장"(CPU 캐시)을 가지고 있다. 같은 숫자를 바꿔도 다른 코어의 메모장에는 바로 안 보인다. `volatile`은 "메모장에 적으면 즉시 칠판(메인 메모리)에도 적고, 읽을 때도 칠판에서 읽어라"는 규칙이다. `happens-before`는 "A 작업이 끝난 후 B 작업이 시작하면, A가 적은 것을 B가 반드시 볼 수 있다"는 약속이다. `Mutex`는 "한 번에 한 명만 칠판에 쓸 수 있는 잠금장치"다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
동시성 버그는 재현이 어렵고 디버깅이 극도로 어렵다. Staff 레벨에서는 메모리 모델을 정확히 이해하여 lock-free 알고리즘을 설계하거나, 최소한 동시성 코드의 정확성을 추론할 수 있어야 한다. 코루틴은 스레드를 넘나들기 때문에 전통적 Java 동시성보다 더 미묘한 문제가 생긴다.

**Step 2 — 핵심 기술 설명**

JSR-133 `happens-before` 규칙 (핵심 7가지):

```
1. Program Order: 같은 스레드 내에서 앞의 액션 HB 뒤의 액션
2. Monitor Lock: unlock() HB 이후의 lock()
3. Volatile: volatile 변수 write HB 이후의 read
4. Thread Start: Thread.start() HB 해당 스레드의 모든 액션
5. Thread Termination: 스레드의 모든 액션 HB join() 반환
6. Interruption: interrupt() HB 인터럽트 감지
7. Transitivity: A HB B, B HB C → A HB C
```

코루틴에서의 메모리 가시성:

```kotlin
// 코루틴은 suspension point에서 스레드가 바뀔 수 있다
suspend fun example() {
    var x = 0
    x = 42                    // 스레드 A에서 실행
    delay(100)                // suspension point → 스레드 B로 resume 가능
    println(x)                // 스레드 B에서 x=42가 보이는가? → YES

    // kotlinx.coroutines는 suspension/resumption 시
    // happens-before 관계를 보장한다.
    // 내부적으로 Continuation의 상태를 전달할 때
    // volatile write/read 또는 CAS를 사용
}

// 그러나 여러 코루틴이 공유 변수에 접근하면 다른 이야기:
var sharedCounter = 0  // NOT SAFE

suspend fun incrementConcurrently() = coroutineScope {
    repeat(10_000) {
        launch(Dispatchers.Default) {
            sharedCounter++  // Race condition! read-modify-write는 atomic이 아님
        }
    }
    // sharedCounter는 10,000보다 작을 수 있음
}
```

**Step 3 — 다양한 관점**

코루틴에서 공유 상태 관리 전략 비교:

```kotlin
// 전략 1: Mutex (코루틴 전용 잠금)
val mutex = Mutex()
var counter = 0

suspend fun safeIncrement() {
    mutex.withLock {
        counter++  // mutual exclusion 보장
    }
}
// 장점: suspend 가능 (스레드 블로킹 없음)
// 단점: lock contention 시 성능 저하, deadlock 가능

// 전략 2: AtomicInteger (lock-free)
val counter = AtomicInteger(0)

fun atomicIncrement() {
    counter.incrementAndGet()  // CAS 기반, lock-free
}
// 장점: 최고 성능, contention 적을 때
// 단점: 복합 연산 불가 (여러 필드 동시 업데이트)

// 전략 3: Channel을 actor로 사용 (메시지 패싱)
sealed class CounterMsg
data object Increment : CounterMsg()
data class GetCount(val response: CompletableDeferred<Int>) : CounterMsg()

fun CoroutineScope.counterActor() = actor<CounterMsg> {
    var count = 0
    for (msg in channel) {
        when (msg) {
            is Increment -> count++
            is GetCount -> msg.response.complete(count)
        }
    }
}
// 장점: 상태 격리, 복합 연산 안전
// 단점: 메시지 패싱 오버헤드, 구현 복잡

// 전략 4: 단일 스레드 confinement
val singleThread = newSingleThreadContext("CounterThread")
var counter = 0

suspend fun confinedIncrement() {
    withContext(singleThread) {
        counter++  // 항상 같은 스레드에서 실행 → race 없음
    }
}
// 장점: 단순, 복합 연산 안전
// 단점: 병렬성 없음, 스레드 낭비
```

**Step 4 — 구체적 예시**

```kotlin
// 프로덕션: Rate Limiter (Sliding Window) — Atomic + volatile 조합
class SlidingWindowRateLimiter(
    private val maxRequests: Int,
    private val windowMillis: Long
) {
    // ConcurrentLinkedDeque: lock-free, 내부적으로 CAS 사용
    private val timestamps = ConcurrentLinkedDeque<Long>()

    @Volatile  // 다른 코루틴에서의 가시성 보장
    private var lastCleanup = System.currentTimeMillis()

    suspend fun tryAcquire(): Boolean {
        val now = System.currentTimeMillis()
        val windowStart = now - windowMillis

        // 주기적 cleanup (정확한 타이밍 불필요 → volatile로 충분)
        if (now - lastCleanup > windowMillis / 2) {
            lastCleanup = now
            while (timestamps.peekFirst()?.let { it < windowStart } == true) {
                timestamps.pollFirst()
            }
        }

        return if (timestamps.size < maxRequests) {
            timestamps.addLast(now)
            true
        } else {
            false
        }
    }
}

// 프로덕션: Thread-safe Cache with Mutex
class SuspendingCache<K, V>(
    private val maxSize: Int = 1000,
    private val ttl: Duration = 5.minutes
) {
    private val mutex = Mutex()
    private val cache = LinkedHashMap<K, CacheEntry<V>>(maxSize, 0.75f, true)

    suspend fun getOrPut(key: K, compute: suspend () -> V): V {
        // 먼저 lock 없이 읽기 시도 (double-checked locking 패턴)
        cache[key]?.takeIf { !it.isExpired() }?.let { return it.value }

        return mutex.withLock {
            // lock 획득 후 다시 확인
            cache[key]?.takeIf { !it.isExpired() }?.let { return it.value }

            val value = compute()  // suspend 가능! — synchronized에서는 불가
            cache[key] = CacheEntry(value, Clock.System.now())
            if (cache.size > maxSize) {
                cache.entries.iterator().let { it.next(); it.remove() }
            }
            value
        }
    }

    private data class CacheEntry<V>(val value: V, val createdAt: Instant) {
        fun isExpired() = Clock.System.now() - createdAt > 5.minutes
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| `Mutex` | suspend 호환, 복합 연산 안전 | contention 시 느림, deadlock 위험 | 복합 상태 업데이트 |
| `Atomic*` | lock-free, 최고 성능 | 단일 변수만, ABA 문제 | 카운터, 플래그 |
| Actor (Channel) | 상태 격리, 메시지 패싱 | 오버헤드, Channel API 실험적 | 복잡한 상태 머신 |
| Single-thread confinement | 단순, 안전 | 병렬성 없음 | 상태 작고 접근 빈번 |
| `ConcurrentHashMap` | Java 검증된 구현 | suspend 불가, 복합 연산 주의 | 읽기 위주 캐시 |

**Step 6 — 성장 & 심화 학습**
- `kotlinx.atomicfu` 플러그인: 컴파일 타임에 `AtomicRef` → `AtomicReferenceFieldUpdater` 변환 (힙 할당 제거)
- Kotlin/Native의 new memory model과 JVM memory model 차이
- `MutableStateFlow`의 내부 동시성 구현 (CAS 기반 lock-free)
- Java 9+ `VarHandle` vs `Unsafe` vs `AtomicFieldUpdater` 성능 비교

**🎯 면접관 평가 기준:**
- **L6 PASS**: happens-before 핵심 규칙 3개 이상, 코루틴 suspension의 가시성 보장, Mutex vs Atomic 적절한 선택
- **L7 EXCEED**: CAS 내부 동작, double-checked locking의 코루틴 버전, Actor 패턴과 CSP 이론 연결, lock-free 알고리즘 설계 경험
- 🚩 **RED FLAG**: "`synchronized`를 `suspend` 함수 안에서 써도 된다", volatile의 가시성만 설명하고 ordering 무시

---


## 4. Spring DI & Lifecycle

### Q10: Bean Scopes와 순환 의존성 해결

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Spring DI & Lifecycle

**Question:**
Spring의 Bean scope(singleton, prototype, request, session)에서, singleton Bean이 prototype Bean을 주입받으면 어떤 문제가 발생하는가? 이 문제의 해결책들(Provider, ObjectFactory, lookup method)의 트레이드오프를 비교하라. 또한 Spring이 `@Autowired`의 순환 의존성(Circular Dependency)을 해결하는 3-level 캐시 메커니즘을 설명하고, Spring Boot 3.x에서 이 동작이 어떻게 변했는지 설명하라.

---

**🧒 12살 비유:**
싱글톤은 "학교에 딱 하나 있는 도서관"이고, 프로토타입은 "학생마다 따로 받는 프린트물"이다. 도서관 안에 프린트물을 고정해두면, 모든 학생이 같은 프린트물을 보게 된다 — 이건 원래 의도가 아니다. 해결법은 도서관에 "프린트 복사기"(Provider)를 두어서 필요할 때마다 새 프린트를 만드는 것이다. 순환 의존성은 "닭이 먼저냐 달걀이 먼저냐" 문제다 — A를 만들려면 B가 필요하고, B를 만들려면 A가 필요하다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
DI는 Spring의 핵심인데, scope 불일치와 순환 의존성은 프로덕션에서 미묘한 버그를 유발한다. Staff 레벨에서는 Spring IoC 컨테이너의 내부 동작을 이해하고 올바른 해결책을 제시할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

**Scope 불일치 문제:**

```kotlin
@Component
@Scope("prototype")
class RequestTracker {
    val requestId = UUID.randomUUID() // 매번 새로 생성되길 기대
}

@Service // singleton (기본)
class OrderService(
    private val tracker: RequestTracker // 🚨 singleton이 prototype을 직접 주입
) {
    fun process() {
        println(tracker.requestId) // 항상 같은 값! prototype이 singleton과 함께 한 번만 생성됨
    }
}
```

해결책 비교:

```kotlin
// 해결 1: ObjectProvider (Spring 5+, 권장)
@Service
class OrderService(
    private val trackerProvider: ObjectProvider<RequestTracker>
) {
    fun process() {
        val tracker = trackerProvider.getObject() // 매번 새 인스턴스
        println(tracker.requestId)
    }
}

// 해결 2: jakarta.inject.Provider (표준 API)
@Service
class OrderService(
    private val trackerProvider: Provider<RequestTracker>
) {
    fun process() {
        val tracker = trackerProvider.get() // 매번 새 인스턴스
    }
}

// 해결 3: @Lookup method (CGLib proxy 기반)
@Service
abstract class OrderService { // abstract 클래스 필요!
    @Lookup
    abstract fun createTracker(): RequestTracker // Spring이 구현 생성

    fun process() {
        val tracker = createTracker() // 매번 새 인스턴스
    }
}

// 해결 4: Scoped Proxy (Request/Session scope에 주로 사용)
@Component
@Scope("request", proxyMode = ScopedProxyMode.TARGET_CLASS)
class RequestTracker { ... }

@Service
class OrderService(
    private val tracker: RequestTracker // 실제로는 CGLIB proxy 주입
    // 메서드 호출 시마다 현재 request의 인스턴스를 조회
)
```

**순환 의존성과 3-level 캐시:**

```
DefaultSingletonBeanRegistry의 3-level 캐시:

1. singletonObjects (1차 캐시): 완전히 초기화된 Bean
2. earlySingletonObjects (2차 캐시): 초기화 중인 Bean (프록시 가능)
3. singletonFactories (3차 캐시): Bean을 생성하는 ObjectFactory

해결 과정 (A → B → A 순환):
  1. A 생성 시작 → A의 ObjectFactory를 3차 캐시에 등록
  2. A 초기화 중 B 필요 → B 생성 시작
  3. B 초기화 중 A 필요 → 3차 캐시에서 A의 ObjectFactory 발견
  4. ObjectFactory 실행 → A의 "early reference" 생성 (AOP proxy 포함 가능)
  5. early A를 2차 캐시로 이동 + 3차 캐시에서 제거
  6. B에 early A 주입 → B 초기화 완료 → 1차 캐시
  7. A에 완성된 B 주입 → A 초기화 완료 → 1차 캐시
```

**Spring Boot 3.x 변경사항:**

```kotlin
// Spring Boot 2.6+ (spring.main.allow-circular-references=false가 기본)
// 순환 의존성은 기본적으로 BeanCurrentlyInCreationException 발생!

// Spring Boot 3.x에서는 더 엄격:
// - 생성자 주입의 순환 의존성: 해결 불가 (항상 실패)
// - 필드/setter 주입의 순환 의존성: 기본 비활성화 (설정으로 허용 가능하나 비권장)

// 올바른 해결: 설계 개선
// Before (순환):
@Service class A(private val b: B)
@Service class B(private val a: A)

// After (이벤트 기반 디커플링):
@Service class A(private val eventPublisher: ApplicationEventPublisher) {
    fun doSomething() {
        eventPublisher.publishEvent(SomethingHappened(data))
    }
}
@Service class B {
    @EventListener
    fun onSomethingHappened(event: SomethingHappened) { ... }
}

// After (인터페이스 분리):
interface BReader { fun read(): Data }
@Service class A(private val bReader: BReader)
@Service class B(private val a: A) : BReader { ... }
```

**Step 3 — 다양한 관점**

| 해결책 | 타입 안전성 | 테스트 용이성 | 성능 | 코드 가독성 |
|--------|-----------|-------------|------|-----------|
| ObjectProvider | 높음 (제네릭) | 좋음 (mock 용이) | 좋음 | 명시적 |
| Provider (JSR-330) | 높음 | 좋음 | 좋음 | 표준적 |
| @Lookup | 중간 | 어려움 (abstract) | 좋음 | 마법적 |
| Scoped Proxy | 낮음 (런타임 에러) | 어려움 | 프록시 오버헤드 | 암시적 |

**Step 4 — 구체적 예시**

```kotlin
// 실무 패턴: Multi-tenant 환경에서 tenant별 설정을 request scope로 관리
@Component
@Scope(WebApplicationContext.SCOPE_REQUEST, proxyMode = ScopedProxyMode.TARGET_CLASS)
class TenantContext {
    lateinit var tenantId: String
    lateinit var config: TenantConfig
}

@Configuration
class TenantConfig {
    @Bean
    @Scope(WebApplicationContext.SCOPE_REQUEST, proxyMode = ScopedProxyMode.TARGET_CLASS)
    fun tenantDataSource(tenantContext: TenantContext): DataSource {
        return dataSourceMap[tenantContext.tenantId]
            ?: throw TenantNotFoundException(tenantContext.tenantId)
    }
}

@Service
class OrderService(
    private val tenantContext: TenantContext, // Scoped Proxy 주입
    private val tenantDataSource: DataSource   // 마찬가지
) {
    suspend fun getOrders(): List<Order> {
        // 각 request마다 올바른 tenant의 DataSource 사용
        return withContext(Dispatchers.IO) {
            tenantDataSource.connection.use { conn ->
                // tenant별 DB에서 조회
            }
        }
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| ObjectProvider | 명시적, 테스트 용이 | 호출 코드 필요 | prototype 주입 |
| Scoped Proxy | 투명한 사용 | 디버깅 어려움, 런타임 에러 | request/session scope |
| 이벤트 기반 디커플링 | 순환 근본 해결, 느슨한 결합 | 간접성, 디버깅 어려움 | 순환 의존성 해결 |
| 인터페이스 분리 원칙 | 깨끗한 설계 | 인터페이스 추가 | 큰 서비스 분리 |

**Step 6 — 성장 & 심화 학습**
- `BeanPostProcessor`와 `BeanFactoryPostProcessor`의 라이프사이클 순서
- Spring AOT (Ahead-Of-Time) 처리에서 scope proxy의 네이티브 이미지 호환성
- `@RefreshScope`(Spring Cloud)의 내부 동작과 Bean 재생성
- Kotlin의 `by lazy`와 Spring의 `@Lazy`의 차이와 상호작용

**🎯 면접관 평가 기준:**
- **L6 PASS**: Scope 불일치 문제와 해결책 2개 이상, 3-level 캐시 메커니즘 설명, Spring Boot 3.x의 기본 변경 인지
- **L7 EXCEED**: 순환 의존성을 설계 문제로 인식하고 이벤트/인터페이스로 해결, multi-tenant scoped proxy 패턴, AOT 호환성
- 🚩 **RED FLAG**: "allow-circular-references=true로 해결", prototype scope 문제 모름

---

### Q11: BeanPostProcessor와 Spring Bean 라이프사이클

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Spring DI & Lifecycle

**Question:**
Spring Bean의 전체 라이프사이클을 순서대로 설명하라. `BeanPostProcessor`, `BeanFactoryPostProcessor`, `InstantiationAwareBeanPostProcessor`는 각각 어느 시점에 개입하는가? 커스텀 어노테이션 `@Monitored`를 만들어서, 해당 어노테이션이 붙은 Bean의 모든 메서드 호출에 자동으로 Micrometer 타이머를 적용하는 BeanPostProcessor를 설계하라.

---

**🧒 12살 비유:**
Bean의 라이프사이클은 "새 학생이 학교에 입학하는 과정"이다. `BeanFactoryPostProcessor`는 "입학 전에 학칙을 바꾸는 교장"이다 — 학생이 들어오기 전에 규칙을 수정한다. `BeanPostProcessor`는 "입학 후 학생을 교육하는 담임 선생"이다 — 학생(Bean)이 만들어진 후에 추가 교육(프록시, 설정)을 한다. `InitializingBean`은 "학생이 첫 날 자기 소개를 하는 것"이다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
Spring의 마법(AOP, @Transactional, @Cacheable 등)은 모두 BeanPostProcessor로 구현된다. 이 메커니즘을 이해하면 커스텀 인프라 코드를 작성하고, Spring의 내부 동작을 디버깅할 수 있다.

**Step 2 — 핵심 기술 설명**

```
Spring Bean 전체 라이프사이클 (순서):

1. BeanFactoryPostProcessor.postProcessBeanFactory()
   → BeanDefinition 수정 (Bean 메타데이터 변경)
   → 예: PropertySourcesPlaceholderConfigurer (${...} 치환)

2. InstantiationAwareBPP.postProcessBeforeInstantiation()
   → 인스턴스 생성 전 개입 (대체 객체 반환 가능)
   → 예: AbstractAutoProxyCreator

3. Constructor 호출 (인스턴스 생성)

4. InstantiationAwareBPP.postProcessAfterInstantiation()
   → 필드 주입 전 개입

5. InstantiationAwareBPP.postProcessProperties()
   → 프로퍼티 주입 (AutowiredAnnotationBPP가 @Autowired 처리)

6. BeanPostProcessor.postProcessBeforeInitialization()
   → 초기화 전 (CommonAnnotationBPP가 @PostConstruct 처리)

7. InitializingBean.afterPropertiesSet() / @PostConstruct

8. Custom init-method

9. BeanPostProcessor.postProcessAfterInitialization()
   → 초기화 후 (AOP 프록시 생성은 여기서!)
   → 예: AnnotationAwareAspectJAutoProxyCreator

10. Bean 사용 가능

... (애플리케이션 실행) ...

11. @PreDestroy
12. DisposableBean.destroy()
13. Custom destroy-method
```

**Step 3 — 다양한 관점**

BeanFactoryPostProcessor vs BeanPostProcessor 핵심 차이:

| 측면 | BeanFactoryPostProcessor | BeanPostProcessor |
|------|-------------------------|-------------------|
| 시점 | Bean 인스턴스 생성 **전** | Bean 인스턴스 생성 **후** |
| 대상 | BeanDefinition (메타데이터) | Bean 인스턴스 (실제 객체) |
| 용도 | 설정값 치환, 등록 수정 | 프록시 래핑, 초기화 보강 |
| 주의 | 여기서 Bean을 getBean()하면 BPP 적용 안 됨 | 순서 중요 (@Order) |

**Step 4 — 구체적 예시**

```kotlin
// 커스텀 @Monitored 어노테이션 + BeanPostProcessor

@Target(AnnotationTarget.CLASS)
@Retention(AnnotationRetention.RUNTIME)
annotation class Monitored(
    val prefix: String = "",  // 메트릭 접두사
    val percentiles: DoubleArray = [0.5, 0.95, 0.99]
)

@Component
class MonitoringBeanPostProcessor(
    private val meterRegistry: MeterRegistry
) : BeanPostProcessor, Ordered {

    // Bean 원본 클래스를 추적 (프록시 후에도 어노테이션 확인용)
    private val originalClasses = ConcurrentHashMap<String, Class<*>>()

    override fun getOrder(): Int = Ordered.LOWEST_PRECEDENCE // AOP 프록시 후에 실행

    override fun postProcessBeforeInitialization(bean: Any, beanName: String): Any {
        // 어노테이션이 있는 Bean 기록
        if (bean.javaClass.isAnnotationPresent(Monitored::class.java)) {
            originalClasses[beanName] = bean.javaClass
        }
        return bean
    }

    override fun postProcessAfterInitialization(bean: Any, beanName: String): Any {
        val originalClass = originalClasses[beanName] ?: return bean
        val annotation = originalClass.getAnnotation(Monitored::class.java) ?: return bean

        val prefix = annotation.prefix.ifBlank {
            originalClass.simpleName.replaceFirstChar { it.lowercase() }
        }

        // CGLIB 프록시 생성
        return ProxyFactory(bean).apply {
            addAdvice(MonitoringMethodInterceptor(prefix, annotation.percentiles, meterRegistry))
            isProxyTargetClass = true
        }.proxy
    }
}

class MonitoringMethodInterceptor(
    private val prefix: String,
    private val percentiles: DoubleArray,
    private val meterRegistry: MeterRegistry
) : MethodInterceptor {

    override fun invoke(invocation: MethodInvocation): Any? {
        val method = invocation.method
        // Object 메서드, private, synthetic 제외
        if (method.declaringClass == Any::class.java) {
            return invocation.proceed()
        }

        val timerName = "$prefix.${method.name}"
        val timer = Timer.builder(timerName)
            .publishPercentiles(*percentiles)
            .tag("class", prefix)
            .tag("method", method.name)
            .register(meterRegistry)

        val sample = Timer.start(meterRegistry)
        return try {
            val result = invocation.proceed()
            // suspend 함수 지원: Continuation을 반환하는 경우 처리
            if (result is kotlin.coroutines.Continuation<*>) {
                // 코루틴 완료 시 타이머 기록하는 래퍼 필요
                wrapContinuation(result, sample, timer)
            } else {
                sample.stop(timer)
                result
            }
        } catch (e: Throwable) {
            sample.stop(Timer.builder(timerName)
                .tag("exception", e.javaClass.simpleName)
                .register(meterRegistry))
            throw e
        }
    }
}

// 사용 예
@Monitored(prefix = "order.service")
@Service
class OrderService(private val repository: OrderRepository) {
    fun createOrder(request: OrderRequest): Order { ... }
    fun getOrder(id: Long): Order { ... }
}
// 자동으로 order.service.createOrder, order.service.getOrder 타이머 생성
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| BeanPostProcessor + Proxy | 투명, 기존 코드 수정 불요 | 프록시 중첩 위험, self-invocation 문제 | 인프라 수준 cross-cutting |
| AOP (@Aspect) | 선언적, 포인트컷 강력 | AspectJ 학습 필요, 디버깅 어려움 | 공통 관심사 |
| Kotlin Delegation | 컴파일 타임, 타입 안전 | 인터페이스 필요, DI와 별개 | 데코레이터 패턴 |
| Micrometer @Timed | 즉시 사용 가능, 표준 | 커스터마이징 제한 | 단순 메트릭 |

**Step 6 — 성장 & 심화 학습**
- `SmartInstantiationAwareBeanPostProcessor`와 AOP 프록시 early reference의 관계
- Spring Boot 3의 AOT에서 BeanPostProcessor가 빌드 타임에 처리되는 방식
- `@Lazy`와 BeanPostProcessor 실행 순서의 미묘한 상호작용
- Spring의 `Ordered`와 `@Order`가 BPP 적용 순서에 미치는 영향

**🎯 면접관 평가 기준:**
- **L6 PASS**: 라이프사이클 순서 정확히 설명, BeanPostProcessor로 프록시 생성 구현, @PostConstruct 시점 이해
- **L7 EXCEED**: BeanFactoryPostProcessor와의 차이, self-invocation 문제와 해결, AOT 환경에서의 제약, Ordered 인터페이스 활용
- 🚩 **RED FLAG**: 라이프사이클 순서 모름, BeanPostProcessor에서 getBean() 호출 위험성 모름

---

### Q12: Custom Auto-Configuration 설계

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Spring DI & Lifecycle

**Question:**
Spring Boot의 Auto-Configuration이 내부적으로 어떻게 동작하는가? `@Conditional*` 어노테이션의 평가 순서와 `AutoConfiguration.imports` 파일의 역할을 설명하라. 회사 내부의 공통 라이브러리를 위한 커스텀 Auto-Configuration starter를 설계하되, 사용자가 쉽게 커스터마이징하고 비활성화할 수 있도록 하라.

---

**🧒 12살 비유:**
Auto-Configuration은 "스마트 가구 조립 설명서"다. 상자를 열면(의존성 추가) 자동으로 "이 부품이 있으니 이 가구를 만들겠습니다"라고 판단한다. `@ConditionalOnClass`는 "이 부품이 있을 때만", `@ConditionalOnMissingBean`은 "아직 이 가구가 없을 때만" 조립한다. 사용자가 직접 가구를 만들었으면(Bean 등록) 자동 조립을 건너뛴다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
대규모 조직에서 Staff 엔지니어는 팀 간 공유 라이브러리를 설계한다. Auto-Configuration은 "관례 기반 설정"의 핵심이며, 잘 설계하면 사용자가 설정 없이도 동작하고, 필요 시 쉽게 커스터마이징할 수 있다.

**Step 2 — 핵심 기술 설명**

Auto-Configuration 로딩 과정:

```
1. @SpringBootApplication
   → @EnableAutoConfiguration
   → AutoConfigurationImportSelector 실행

2. AutoConfigurationImportSelector:
   → META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
     (Spring Boot 3.x, 이전에는 spring.factories)
   → 파일에 나열된 모든 AutoConfiguration 클래스 로드

3. 필터링:
   → @ConditionalOnClass: 클래스패스에 특정 클래스 존재?
   → @ConditionalOnProperty: 프로퍼티 값 확인
   → @ConditionalOnMissingBean: 사용자가 이미 Bean 등록했는지?
   → 조건 미충족 시 건너뜀

4. 순서 결정:
   → @AutoConfiguration(before/after)로 순서 제어
   → @AutoConfigureBefore/@AutoConfigureAfter (레거시)

5. 조건 충족된 Configuration만 Bean 등록
```

**Step 3 — 다양한 관점**

`@Conditional*` 평가 순서와 성능:

```
Phase 1 (클래스 로딩 전, 빠름):
  @ConditionalOnClass      → 클래스패스 스캔 (ASM, 클래스 로딩 없이)
  @ConditionalOnWebApplication
  @ConditionalOnNotWebApplication

Phase 2 (Bean 등록 시, 느림):
  @ConditionalOnBean       → BeanFactory 조회
  @ConditionalOnMissingBean → BeanFactory 조회
  @ConditionalOnProperty   → Environment 조회
```

**Step 4 — 구체적 예시**

```kotlin
// ===== 회사 내부 공통 라이브러리: Observability Starter =====

// 1. Auto-Configuration Properties
@ConfigurationProperties(prefix = "company.observability")
data class ObservabilityProperties(
    val enabled: Boolean = true,
    val tracing: TracingProperties = TracingProperties(),
    val metrics: MetricsProperties = MetricsProperties(),
    val logging: LoggingProperties = LoggingProperties()
) {
    data class TracingProperties(
        val enabled: Boolean = true,
        val samplingRate: Double = 0.1,     // 10% 샘플링
        val propagation: PropagationType = PropagationType.W3C,
        val excludePaths: List<String> = listOf("/health", "/ready", "/metrics")
    )
    data class MetricsProperties(
        val enabled: Boolean = true,
        val prefix: String = "app",
        val histogramPercentiles: List<Double> = listOf(0.5, 0.95, 0.99)
    )
    data class LoggingProperties(
        val enabled: Boolean = true,
        val format: LogFormat = LogFormat.JSON,
        val includeHeaders: List<String> = listOf("x-request-id", "x-trace-id")
    )
}

// 2. Auto-Configuration 클래스
@AutoConfiguration
@EnableConfigurationProperties(ObservabilityProperties::class)
@ConditionalOnProperty(prefix = "company.observability", name = ["enabled"], havingValue = "true", matchIfMissing = true)
class ObservabilityAutoConfiguration {

    // 트레이싱 설정 — OpenTelemetry가 클래스패스에 있을 때만
    @Configuration
    @ConditionalOnClass(name = ["io.opentelemetry.api.OpenTelemetry"])
    @ConditionalOnProperty(prefix = "company.observability.tracing", name = ["enabled"], havingValue = "true", matchIfMissing = true)
    class TracingConfiguration {

        @Bean
        @ConditionalOnMissingBean // 사용자가 커스텀 SpanProcessor 등록 가능
        fun companySpanProcessor(properties: ObservabilityProperties): SpanProcessor {
            return BatchSpanProcessor.builder(
                OtlpGrpcSpanExporter.builder().build()
            ).build()
        }

        @Bean
        @ConditionalOnMissingBean
        fun companySampler(properties: ObservabilityProperties): Sampler {
            return Sampler.traceIdRatioBased(properties.tracing.samplingRate)
        }

        @Bean
        fun tracingWebFilter(properties: ObservabilityProperties): WebFilter {
            return TracingWebFilter(properties.tracing.excludePaths)
        }
    }

    // 메트릭 설정 — Micrometer가 있을 때만
    @Configuration
    @ConditionalOnClass(name = ["io.micrometer.core.instrument.MeterRegistry"])
    @ConditionalOnProperty(prefix = "company.observability.metrics", name = ["enabled"], havingValue = "true", matchIfMissing = true)
    class MetricsConfiguration {

        @Bean
        @ConditionalOnMissingBean
        fun companyMeterFilter(properties: ObservabilityProperties): MeterFilter {
            return MeterFilter.renameTag("", "application", properties.metrics.prefix)
        }

        @Bean
        fun jvmMetricsBindings(): List<MeterBinder> = listOf(
            JvmGcMetrics(),
            JvmMemoryMetrics(),
            JvmThreadMetrics(),
            ProcessorMetrics()
        )
    }

    // 로깅 설정
    @Configuration
    @ConditionalOnProperty(prefix = "company.observability.logging", name = ["enabled"], havingValue = "true", matchIfMissing = true)
    class LoggingConfiguration {

        @Bean
        @ConditionalOnMissingBean
        fun structuredLoggingFilter(properties: ObservabilityProperties): WebFilter {
            return StructuredLoggingFilter(properties.logging)
        }
    }
}

// 3. META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
// 한 줄로 등록:
// com.company.observability.ObservabilityAutoConfiguration

// 4. 사용자 커스터마이징 예시
// application.yml:
// company:
//   observability:
//     tracing:
//       sampling-rate: 1.0  # 100% 샘플링 (개발 환경)
//       exclude-paths:
//         - /health
//         - /internal/*
//     metrics:
//       prefix: order-service

// 5. 완전 비활성화:
// company.observability.enabled=false
// 또는 특정 모듈만:
// company.observability.tracing.enabled=false
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| @ConditionalOnMissingBean | 사용자 오버라이드 최우선 | 순서 의존적, 디버깅 어려움 | 기본 구현 제공 |
| @ConditionalOnProperty | 명시적 on/off | 프로퍼티 폭증 | 기능 토글 |
| @ConditionalOnClass | 의존성 기반 자동 감지 | 클래스 이름 하드코딩 | 선택적 통합 |
| 수동 @Import | 완전한 제어 | 자동화 없음 | 내부 모듈 간 |

**Step 6 — 성장 & 심화 학습**
- `ConditionEvaluationReport`로 Auto-Configuration 적용/제외 이유 디버깅
- Spring Boot 3.x의 AOT 처리에서 `@Conditional`이 빌드 타임에 평가되는 방식
- `@ImportAutoConfiguration`과 테스트 슬라이싱의 관계
- Spring Boot의 `spring-boot-autoconfigure-processor`가 빌드 시 메타데이터를 생성하는 과정

**🎯 면접관 평가 기준:**
- **L6 PASS**: Auto-Configuration 로딩 과정, @Conditional* 사용, 사용자 커스터마이징 지원
- **L7 EXCEED**: 평가 순서 최적화, starter 모듈 구조 설계, AOT 호환, 회사 수준의 공통 라이브러리 경험
- 🚩 **RED FLAG**: spring.factories와 AutoConfiguration.imports 차이 모름, @ConditionalOnMissingBean 없이 설계

---


## 5. Spring WebFlux & Reactive

### Q13: Netty Event Loop와 코루틴 통합

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Spring WebFlux & Reactive

**Question:**
Spring WebFlux의 Netty 기반 아키텍처에서 event loop 스레드가 blocking되면 어떤 일이 발생하는가? 코루틴의 `suspend` 함수가 WebFlux 핸들러에서 실행될 때 내부적으로 어떤 Dispatcher가 사용되며, `Dispatchers.IO`로 전환해야 하는 시점은 언제인가? R2DBC를 사용할 때와 JDBC를 래핑할 때의 스레드 모델 차이를 설명하라.

---

**🧒 12살 비유:**
Netty의 event loop는 "회전초밥 레스토랑의 컨베이어 벨트 관리인"이다. 관리인은 접시(요청)를 올리고 내리는 일을 엄청 빠르게 하지만, 만약 관리인이 직접 초밥을 만들기 시작하면(blocking) 벨트가 멈추고 모든 손님이 기다린다. `Dispatchers.IO`로 전환하는 것은 "초밥 만드는 일을 주방(별도 스레드)에 맡기고, 관리인은 계속 벨트를 돌리는 것"이다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
WebFlux를 사용하면서 event loop를 blocking하는 것은 가장 흔하고 치명적인 실수다. Staff 레벨에서는 스레드 모델을 정확히 이해하고, 어떤 코드가 어떤 스레드에서 실행되는지 추론할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

```
Netty 스레드 모델:
  Boss EventLoopGroup (1개): TCP accept만 처리
  Worker EventLoopGroup (CPU 코어 수): I/O 이벤트 처리 + 핸들러 실행

  Worker 스레드가 blocking되면:
  → 해당 스레드에 할당된 모든 Connection의 I/O가 멈춤
  → CPU 코어가 4개면 Worker 4개, 하나가 blocking되면 처리량 25% 감소
  → 모든 Worker가 blocking되면 전체 서비스 응답 불가
```

코루틴 + WebFlux에서의 Dispatcher:

```kotlin
@RestController
class UserController(private val userService: UserService) {

    // Spring WebFlux가 suspend 함수를 감지하면
    // 내부적으로 Dispatchers.Unconfined를 사용 (또는 Reactor 스레드 유지)
    @GetMapping("/users/{id}")
    suspend fun getUser(@PathVariable id: Long): UserResponse {
        // 이 코드는 Netty event loop 스레드에서 실행됨!
        val user = userService.findById(id) // R2DBC면 OK, JDBC면 🚨 BLOCKING!
        return user.toResponse()
    }

    // JDBC를 써야 한다면 명시적으로 IO dispatcher로 전환
    @GetMapping("/users/{id}/legacy")
    suspend fun getUserLegacy(@PathVariable id: Long): UserResponse {
        val user = withContext(Dispatchers.IO) {
            jdbcUserRepository.findById(id) // blocking I/O → IO 스레드에서 실행
        }
        // 여기는 다시 event loop 스레드
        return user.toResponse()
    }
}
```

R2DBC vs JDBC 래핑:

```kotlin
// R2DBC: 완전 non-blocking
// 내부적으로 Netty event loop에서 DB 통신 (TCP non-blocking I/O)
// 추가 스레드 전환 없음 → 최고 효율
interface UserRepository : CoroutineCrudRepository<User, Long> {
    suspend fun findByEmail(email: String): User?
}

// JDBC 래핑: blocking I/O를 IO dispatcher로 격리
@Repository
class JdbcUserRepository(private val jdbcTemplate: JdbcTemplate) {
    private val dbDispatcher = Dispatchers.IO.limitedParallelism(20) // DB 커넥션 풀 크기에 맞춤

    suspend fun findById(id: Long): User? = withContext(dbDispatcher) {
        jdbcTemplate.queryForObject("SELECT * FROM users WHERE id = ?", userRowMapper, id)
    }
}
```

**Step 3 — 다양한 관점**

| 시나리오 | event loop blocking? | 해결책 |
|----------|---------------------|--------|
| R2DBC 쿼리 | No | 그대로 사용 |
| JDBC/JPA 쿼리 | Yes | `withContext(Dispatchers.IO)` |
| WebClient 호출 | No (Netty 기반) | 그대로 사용 |
| RestTemplate 호출 | Yes | WebClient로 교체 또는 IO dispatcher |
| 파일 I/O | Yes | IO dispatcher |
| CPU 집약 연산 | Yes (event loop 독점) | `withContext(Dispatchers.Default)` |
| Thread.sleep() | Yes | `delay()` 사용 |
| `synchronized` 블록 | Yes (contention 시) | `Mutex` 사용 |

**Step 4 — 구체적 예시**

```kotlin
// 프로덕션 패턴: blocking 감지 + 알림
@Configuration
class BlockingDetectionConfig {
    @Bean
    fun blockingDetection(): BlockHound.Builder = BlockHound.builder()
        .allowBlockingCallsInside("io.netty.util.concurrent.GlobalEventExecutor", "take")
        .blockingMethodCallback { method ->
            // 프로덕션에서는 로그 + 메트릭, 개발에서는 에러
            logger.error {
                "Blocking call detected on ${Thread.currentThread().name}: " +
                "${method.declaringClass.name}.${method.name}"
            }
            meterRegistry.counter("blocking.detected",
                "class", method.declaringClass.simpleName,
                "method", method.name
            ).increment()
        }
}

// WebFlux + 코루틴 + R2DBC 통합 서비스
@Service
class OrderService(
    private val orderRepository: OrderCoroutineRepository, // R2DBC
    private val paymentClient: WebClient,                   // non-blocking HTTP
    private val legacyInventory: LegacyInventoryClient,     // blocking SOAP
    private val inventoryDispatcher: CoroutineDispatcher
) {
    suspend fun createOrder(request: OrderRequest): OrderResponse = coroutineScope {
        // R2DBC: event loop에서 직접 실행 (non-blocking)
        val savedOrder = orderRepository.save(Order.from(request))

        // WebClient: event loop에서 직접 실행 (non-blocking)
        val paymentDeferred = async {
            paymentClient.post()
                .uri("/payments")
                .bodyValue(PaymentRequest(savedOrder.id, request.amount))
                .retrieve()
                .awaitBody<PaymentResponse>()
        }

        // Legacy blocking API: IO dispatcher로 격리
        val inventoryDeferred = async(inventoryDispatcher) {
            legacyInventory.reserve(request.items) // blocking SOAP call
        }

        val payment = paymentDeferred.await()
        val inventory = inventoryDeferred.await()

        orderRepository.save(savedOrder.copy(
            paymentId = payment.id,
            inventoryReserved = true
        )).toResponse()
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| 순수 R2DBC + WebClient | 최고 성능, 최소 스레드 | 에코시스템 제한, 학습 곡선 | 그린필드 |
| JDBC + IO Dispatcher | 기존 코드 재사용 | 스레드 전환 비용, 커넥션 풀 관리 | 마이그레이션 |
| Virtual Thread + Spring MVC | 간단, blocking OK | JDK 21+ 필요, 핀닝 주의 | JDK 21+ 가능할 때 |
| Spring MVC + 코루틴 | 단순, 익숙한 모델 | event loop 장점 없음 | 대부분의 CRUD |

**Step 6 — 성장 & 심화 학습**
- BlockHound를 CI에 통합하여 blocking 호출 자동 감지
- Virtual Thread의 "pinning" 문제 (`synchronized`와 `native call`에서 carrier thread 점유)
- Netty의 `ChannelPipeline`과 Spring WebFlux 핸들러 체인의 관계
- `Schedulers.boundedElastic()`과 `Dispatchers.IO`의 내부 차이

**🎯 면접관 평가 기준:**
- **L6 PASS**: event loop blocking의 위험성, R2DBC vs JDBC의 스레드 모델 차이, IO dispatcher 전환 시점
- **L7 EXCEED**: BlockHound 활용, Virtual Thread와의 비교, 레거시 시스템 점진적 마이그레이션 전략, Netty 파이프라인 이해
- 🚩 **RED FLAG**: "suspend 쓰면 자동으로 non-blocking", WebFlux에서 JDBC 직접 사용

---

### Q14: R2DBC와 코루틴 기반 데이터 접근

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Spring WebFlux & Reactive

**Question:**
R2DBC에서 트랜잭션 관리는 JPA의 `@Transactional`과 어떻게 다른가? 코루틴 컨텍스트에서 `@Transactional`이 동작하는 방식과, 복잡한 트랜잭션(nested, savepoint)을 코루틴으로 처리할 때의 제한사항을 설명하라. N+1 문제는 R2DBC에서 어떻게 나타나고 해결하는가?

---

**🧒 12살 비유:**
트랜잭션은 "게임의 세이브 포인트"다. JPA의 `@Transactional`은 "게임 시작할 때 자동 세이브하고, 죽으면 되돌리기"다. R2DBC에서는 "세이브 포인트를 직접 만들고 관리"해야 하는데, 코루틴이 중간에 스레드를 바꿀 수 있어서 "다른 기기에서 세이브 파일을 이어받기"처럼 복잡해진다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
R2DBC의 트랜잭션은 ThreadLocal 기반이 아니기 때문에 전통적인 Spring AOP 기반 `@Transactional`과 근본적으로 다르다. 코루틴과의 통합에서 미묘한 버그가 발생할 수 있으며, 이를 정확히 이해하는 것이 중요하다.

**Step 2 — 핵심 기술 설명**

```kotlin
// JPA @Transactional: ThreadLocal에 Connection 저장
// → 같은 스레드의 모든 Repository 호출이 같은 Connection 사용
// → PlatformTransactionManager가 관리

// R2DBC @Transactional: Reactor Context에 Connection 저장
// → ReactiveTransactionManager가 관리
// → 코루틴에서는 CoroutineContext의 ReactorContext를 통해 전파

// Spring 6.1+에서 코루틴 suspend 함수에 @Transactional 직접 사용 가능
@Service
class OrderService(
    private val orderRepository: OrderCoroutineRepository,
    private val orderItemRepository: OrderItemCoroutineRepository
) {
    @Transactional // ReactiveTransactionManager 사용
    suspend fun createOrder(request: OrderRequest): Order {
        val order = orderRepository.save(Order.from(request))
        request.items.forEach { item ->
            orderItemRepository.save(OrderItem(orderId = order.id, item))
        }
        return order
        // 예외 발생 시 자동 rollback
    }
}
```

코루틴에서 트랜잭션 컨텍스트 전파:

```kotlin
// 내부 동작 (단순화):
// 1. AOP 프록시가 suspend 함수를 가로챔
// 2. ReactiveTransactionManager.getReactiveTransaction() 호출
// 3. Connection을 Reactor Context에 저장
// 4. suspend 함수의 Continuation에 ReactorContext 전달
// 5. Repository 호출 시 ReactorContext에서 Connection 꺼내 사용
// 6. 완료/예외 시 commit/rollback

// 주의: withContext(Dispatchers.IO)로 스레드를 바꿔도
// ReactorContext는 CoroutineContext에 포함되어 있으므로 전파됨!
// 하지만 새로운 coroutineScope를 만들면 컨텍스트가 복사됨 → 안전
```

N+1 문제와 해결:

```kotlin
// R2DBC에는 JPA의 @EntityGraph나 JOIN FETCH가 없음
// N+1은 수동으로 해결해야 함

// BAD: N+1
suspend fun getOrdersWithItems(userId: Long): List<OrderWithItems> {
    val orders = orderRepository.findByUserId(userId) // 1 query
    return orders.map { order ->
        val items = orderItemRepository.findByOrderId(order.id) // N queries!
        OrderWithItems(order, items.toList())
    }
}

// GOOD: 배치 로딩
suspend fun getOrdersWithItems(userId: Long): List<OrderWithItems> {
    val orders = orderRepository.findByUserId(userId).toList()
    val orderIds = orders.map { it.id }
    val allItems = orderItemRepository.findByOrderIdIn(orderIds).toList() // 1 query
    val itemsByOrderId = allItems.groupBy { it.orderId }

    return orders.map { order ->
        OrderWithItems(order, itemsByOrderId[order.id] ?: emptyList())
    }
}

// BETTER: 커스텀 쿼리로 JOIN
@Query("""
    SELECT o.*, oi.id as item_id, oi.product_id, oi.quantity
    FROM orders o
    LEFT JOIN order_items oi ON o.id = oi.order_id
    WHERE o.user_id = :userId
""")
fun findOrdersWithItemsByUserId(userId: Long): Flow<OrderWithItemRow>

// 그 후 애플리케이션 레벨에서 그룹핑
```

**Step 3 — 다양한 관점**

R2DBC 트랜잭션의 제한사항:

| 기능 | JPA/JDBC | R2DBC |
|------|----------|-------|
| @Transactional | ThreadLocal 기반 | Reactor Context 기반 |
| Nested Transaction | @Transactional(NESTED) | 미지원 (Savepoint 수동) |
| Savepoint | 자동 | DatabaseClient로 수동 |
| Propagation.REQUIRES_NEW | 새 Connection | 제한적 지원 |
| Lazy Loading | 지원 (프록시) | 미지원 |
| 2nd Level Cache | Hibernate Cache | 없음 (직접 구현) |
| Batch Insert | JPA batch_size | 수동 Statement batching |

**Step 4 — 구체적 예시**

```kotlin
// 프로덕션: Savepoint 수동 관리
@Service
class PaymentService(
    private val transactionalOperator: TransactionalOperator,
    private val r2dbcEntityTemplate: R2dbcEntityTemplate,
    private val databaseClient: DatabaseClient
) {
    suspend fun processPaymentWithPartialRollback(
        orderId: Long,
        payments: List<PaymentRequest>
    ): PaymentResult {
        return transactionalOperator.executeAndAwait {
            val results = mutableListOf<PaymentAttempt>()

            for (payment in payments) {
                try {
                    // Savepoint 생성
                    databaseClient.sql("SAVEPOINT sp_${payment.id}").await()

                    val result = processSinglePayment(payment)
                    results.add(PaymentAttempt.success(payment, result))
                } catch (e: PaymentException) {
                    // 이 결제만 롤백, 나머지는 유지
                    databaseClient.sql("ROLLBACK TO SAVEPOINT sp_${payment.id}").await()
                    results.add(PaymentAttempt.failure(payment, e))
                }
            }

            // 전체 트랜잭션은 커밋 (부분 성공)
            PaymentResult(results)
        }
    }
}

// 프로덕션: R2DBC 배치 insert (N+1 방지)
@Repository
class R2dbcOrderItemRepository(
    private val databaseClient: DatabaseClient
) {
    suspend fun batchInsert(items: List<OrderItem>) {
        val sql = "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES ($1, $2, $3, $4)"

        databaseClient.inConnectionMany { connection ->
            val statement = connection.createStatement(sql)
            items.forEachIndexed { index, item ->
                statement
                    .bind(0, item.orderId)
                    .bind(1, item.productId)
                    .bind(2, item.quantity)
                    .bind(3, item.price)
                if (index < items.size - 1) {
                    statement.add() // 배치에 추가
                }
            }
            Flux.from(statement.execute())
                .flatMap { result -> result.rowsUpdated }
        }.asFlow().collect { }
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| R2DBC + 코루틴 | 완전 non-blocking | ORM 기능 부족, N+1 수동 해결 | 고성능 API |
| JPA + Virtual Thread | 풍부한 ORM, 익숙함 | JDK 21+, JPA lazy loading 주의 | 복잡한 도메인 |
| jOOQ + R2DBC | 타입 안전 SQL, 강력한 쿼리 | 학습 곡선, 라이센스 | 복잡한 쿼리 |
| Exposed (Kotlin ORM) | Kotlin-native, DSL | 커뮤니티 작음, R2DBC 미지원 | 단순 CRUD |

**Step 6 — 성장 & 심화 학습**
- Spring Data R2DBC의 `@Query`와 SpEL 표현식 활용
- `io.r2dbc.pool.ConnectionPool` 설정과 모니터링
- Flyway/Liquibase의 R2DBC 호환 마이그레이션
- Project Loom 환경에서 R2DBC vs JDBC + Virtual Thread 성능 비교

**🎯 면접관 평가 기준:**
- **L6 PASS**: ThreadLocal vs Reactor Context 기반 트랜잭션 차이, N+1 해결 패턴, @Transactional 코루틴 지원
- **L7 EXCEED**: Savepoint 수동 관리, 배치 insert 패턴, Virtual Thread 대안 비교, R2DBC 커넥션 풀 튜닝
- 🚩 **RED FLAG**: "R2DBC도 JPA처럼 @Transactional만 쓰면 된다", N+1 인식 못 함

---

## 6. Kotlin Language Mastery

### Q15: Sealed Hierarchy와 Exhaustive When

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Kotlin Language Mastery

**Question:**
Kotlin 2.0의 sealed class/interface를 활용하여 복잡한 도메인 상태 머신을 모델링하라. `when` 표현식의 exhaustiveness가 컴파일 타임에 보장되는 조건과, sealed hierarchy가 모듈 경계를 넘을 수 없는 제약의 설계 의도를 설명하라. ADT(Algebraic Data Type)로서의 sealed class와 enum class의 사용 구분을 논하라.

---

**🧒 12살 비유:**
`sealed class`는 "이 상자에는 정확히 이 종류들만 들어갈 수 있다"는 규칙이다. 빨강, 파랑, 초록 공만 넣을 수 있는 상자가 있으면, "빨강이면 이렇게, 파랑이면 저렇게" 모든 경우를 처리했는지 컴파일러가 확인해준다. `enum`은 "공이 3개뿐"이고, `sealed class`는 "빨강 공은 크기가 다를 수 있다" — 각 종류가 자기만의 데이터를 가질 수 있다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
Sealed hierarchy는 도메인 모델링의 핵심 도구다. 올바르게 사용하면 "불가능한 상태를 불가능하게" 만들 수 있고, 새 상태 추가 시 컴파일러가 모든 처리 누락을 잡아준다.

**Step 2 — 핵심 기술 설명**

```kotlin
// ADT로 결제 상태 머신 모델링
sealed interface PaymentState {
    val orderId: OrderId
    val amount: Money

    // 초기 상태
    data class Pending(
        override val orderId: OrderId,
        override val amount: Money,
        val createdAt: Instant
    ) : PaymentState

    // 처리 중 (외부 PG 응답 대기)
    data class Processing(
        override val orderId: OrderId,
        override val amount: Money,
        val pgTransactionId: String,
        val startedAt: Instant
    ) : PaymentState

    // 성공
    data class Completed(
        override val orderId: OrderId,
        override val amount: Money,
        val pgTransactionId: String,
        val completedAt: Instant,
        val receipt: Receipt
    ) : PaymentState

    // 실패 — 실패 이유가 sealed로 또 분류됨
    data class Failed(
        override val orderId: OrderId,
        override val amount: Money,
        val reason: FailureReason,
        val failedAt: Instant
    ) : PaymentState

    // 환불
    data class Refunded(
        override val orderId: OrderId,
        override val amount: Money,
        val originalTransaction: String,
        val refundedAt: Instant
    ) : PaymentState
}

// 실패 이유도 sealed로 모델링 (중첩 ADT)
sealed interface FailureReason {
    data class InsufficientFunds(val available: Money) : FailureReason
    data class CardDeclined(val code: String, val message: String) : FailureReason
    data class NetworkError(val cause: Throwable) : FailureReason
    data class FraudDetected(val riskScore: Double) : FailureReason
    data object Timeout : FailureReason
}

// 상태 전이 함수 — exhaustive when으로 모든 경우 처리
fun PaymentState.transition(event: PaymentEvent): PaymentState = when (this) {
    is PaymentState.Pending -> when (event) {
        is PaymentEvent.StartProcessing -> PaymentState.Processing(
            orderId, amount, event.pgTransactionId, Instant.now()
        )
        is PaymentEvent.Cancel -> PaymentState.Failed(
            orderId, amount, FailureReason.CardDeclined("CANCELLED", "User cancelled"), Instant.now()
        )
        else -> this // 다른 이벤트는 무시
    }
    is PaymentState.Processing -> when (event) {
        is PaymentEvent.Complete -> PaymentState.Completed(
            orderId, amount, pgTransactionId, Instant.now(), event.receipt
        )
        is PaymentEvent.Fail -> PaymentState.Failed(
            orderId, amount, event.reason, Instant.now()
        )
        else -> this
    }
    is PaymentState.Completed -> when (event) {
        is PaymentEvent.Refund -> PaymentState.Refunded(
            orderId, amount, pgTransactionId, Instant.now()
        )
        else -> this
    }
    is PaymentState.Failed -> this  // terminal state
    is PaymentState.Refunded -> this // terminal state
}
// 새 PaymentState를 추가하면 → 여기서 컴파일 에러 → 처리 강제!
```

Sealed vs Enum:

```kotlin
// Enum: 인스턴스가 고정, 데이터 없음 (싱글톤)
enum class Direction { NORTH, SOUTH, EAST, WEST }

// Sealed: 각 서브타입이 자기만의 데이터를 가짐
sealed interface Result<out T> {
    data class Success<T>(val data: T) : Result<T>
    data class Failure(val error: AppError) : Result<Nothing>
    data object Loading : Result<Nothing>
}
// Result.Success("hello")와 Result.Success(42)는 다른 인스턴스

// Sealed interface vs Sealed class (Kotlin 2.0):
// sealed interface: 다중 상속 가능, 상태 없는 계층에 적합
// sealed class: 공통 상태/메서드 공유 시
```

모듈 경계 제약의 설계 의도:

```kotlin
// sealed의 서브클래스는 같은 모듈(같은 compilation unit)에서만 정의 가능
// 이유: exhaustiveness를 컴파일 타임에 보장하려면 모든 서브타입을 알아야 함
// 다른 모듈에서 서브타입을 추가하면 기존 when 표현식이 깨짐 → 컴파일 보장 불가

// 모듈 간 확장이 필요하면 → 일반 interface 사용 + visitor 패턴
```

**Step 3 — 다양한 관점**

| 패턴 | Sealed Class | Enum | Interface + Visitor |
|------|-------------|------|---------------------|
| 인스턴스 | 다수 (데이터 포함) | 고정 (싱글톤) | 다수 |
| 모듈 경계 | 같은 모듈만 | 같은 파일만 | 어디서나 |
| Exhaustiveness | 컴파일 타임 | 컴파일 타임 | 런타임 |
| 적합한 곳 | 상태 머신, Result 타입 | 방향, 요일, 종류 | 플러그인 확장 |

**Step 4 — 구체적 예시**

```kotlin
// 프로덕션: API 에러 응답을 sealed hierarchy로 타입 안전하게
sealed interface AppError {
    val code: String
    val message: String

    sealed interface ClientError : AppError {
        data class Validation(
            override val code: String = "400001",
            override val message: String,
            val fieldErrors: Map<String, String>
        ) : ClientError

        data class NotFound(
            override val code: String = "404001",
            override val message: String,
            val resourceType: String,
            val resourceId: String
        ) : ClientError

        data class Unauthorized(
            override val code: String = "401001",
            override val message: String
        ) : ClientError
    }

    sealed interface ServerError : AppError {
        data class Internal(
            override val code: String = "500001",
            override val message: String = "Internal server error",
            val cause: Throwable? = null
        ) : ServerError

        data class ServiceUnavailable(
            override val code: String = "503001",
            override val message: String,
            val retryAfter: Duration? = null
        ) : ServerError
    }
}

// Exception Handler에서 exhaustive when
@RestControllerAdvice
class GlobalExceptionHandler {
    fun handleAppError(error: AppError): ResponseEntity<ErrorResponse> {
        val status = when (error) {
            is AppError.ClientError.Validation -> HttpStatus.BAD_REQUEST
            is AppError.ClientError.NotFound -> HttpStatus.NOT_FOUND
            is AppError.ClientError.Unauthorized -> HttpStatus.UNAUTHORIZED
            is AppError.ServerError.Internal -> HttpStatus.INTERNAL_SERVER_ERROR
            is AppError.ServerError.ServiceUnavailable -> HttpStatus.SERVICE_UNAVAILABLE
        } // else 불필요 — 컴파일러가 모든 케이스 확인
        return ResponseEntity.status(status).body(error.toResponse())
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| Sealed hierarchy | 컴파일 타임 안전, 패턴 매칭 | 모듈 경계 제약 | 유한한 상태/타입 |
| Enum + data 필드 | 싱글톤, 순서 보장 | 인스턴스별 데이터 불가 | 고정 목록 |
| Interface + Visitor | 모듈 확장 가능 | 타입 안전성 약함 | 플러그인 시스템 |
| Arrow의 Either/Validated | FP 패턴, 합성 용이 | Arrow 의존성 | 함수형 스타일 |

**Step 6 — 성장 & 심화 학습**
- Kotlin 2.0의 `@SubclassOptInRequired`로 sealed hierarchy 확장 시 의도적 opt-in 요구
- Jackson의 sealed class 직렬화: `@JsonTypeInfo` + `@JsonSubTypes` 설정
- Arrow의 `Either`와 sealed `Result`의 trade-off
- sealed interface의 `when` 표현식이 value로 사용될 때만 exhaustive 검사하는 이유

**🎯 면접관 평가 기준:**
- **L6 PASS**: 상태 머신 모델링, exhaustive when의 컴파일 보장, enum과의 구분
- **L7 EXCEED**: 중첩 ADT 설계, 모듈 경계 제약의 이론적 근거 (컴파일 안전성), 직렬화/API 응답 통합 패턴
- 🚩 **RED FLAG**: else 분기로 sealed 장점 상실, sealed와 abstract class 혼동

---

### Q16: Kotlin DSL과 @DslMarker

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Kotlin Language Mastery

**Question:**
Kotlin의 Type-Safe Builder 패턴으로 DSL을 설계할 때 `@DslMarker`가 필요한 이유를 설명하라. 중첩된 빌더에서 암시적 리시버(implicit receiver)가 의도치 않게 외부 스코프에 접근하는 문제를 보이고, `@DslMarker`가 이를 어떻게 해결하는지 설명하라. Spring의 Router DSL, Kotest의 테스트 DSL 등의 구현 원리를 분석하라.

---

**🧒 12살 비유:**
DSL은 "레고 설명서를 만드는 도구"다. 빨간 블록 안에서 파란 블록을 조립할 때, `@DslMarker` 없으면 실수로 빨간 블록의 부품을 파란 블록에 끼울 수 있다. `@DslMarker`는 "지금 파란 블록 안에 있으니까, 빨간 블록 부품을 쓰려면 명시적으로 말해야 해"라는 규칙이다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
Kotlin DSL은 라이브러리 설계의 핵심 기술이다. Staff 레벨에서는 사용하는 것을 넘어 DSL을 설계하고, 다른 개발자가 안전하게 사용할 수 있도록 가드레일을 제공해야 한다.

**Step 2 — 핵심 기술 설명**

```kotlin
// @DslMarker 없이 — 위험한 암시적 리시버 접근
class Table {
    fun tr(block: Row.() -> Unit) { /*...*/ }
}
class Row {
    fun td(block: Cell.() -> Unit) { /*...*/ }
}
class Cell {
    var text: String = ""
}

fun table(block: Table.() -> Unit) = Table().apply(block)

// 문제:
table {
    tr {
        td {
            text = "hello"
            tr { } // 🚨 Cell 안에서 Table의 tr()에 접근 가능!
            // 컴파일러가 외부 리시버(Table)의 tr()을 찾아서 호출
        }
    }
}

// @DslMarker로 해결:
@DslMarker
annotation class HtmlDsl

@HtmlDsl class Table { fun tr(block: Row.() -> Unit) { } }
@HtmlDsl class Row { fun td(block: Cell.() -> Unit) { } }
@HtmlDsl class Cell { var text: String = "" }

table {
    tr {
        td {
            text = "hello"
            tr { } // ❌ 컴파일 에러! Cell 스코프에서 Table의 tr() 접근 불가
            this@table.tr { } // ✅ 명시적 접근은 허용
        }
    }
}
```

Spring Router DSL 구현 원리:

```kotlin
// Spring의 CoRouterFunctionDsl (단순화)
@RouterDsl  // @DslMarker 어노테이션
class CoRouterFunctionDsl(private val routes: MutableList<RouterFunction<ServerResponse>>) {

    fun GET(pattern: String, handler: suspend (ServerRequest) -> ServerResponse) {
        routes.add(RouterFunctions.route()
            .GET(pattern) { req ->
                mono { handler(req) } // 코루틴 → Mono 변환
            }.build())
    }

    fun POST(pattern: String, handler: suspend (ServerRequest) -> ServerResponse) { /*...*/ }

    // 중첩 라우팅
    fun "/api".nest(block: CoRouterFunctionDsl.() -> Unit) {
        val nested = CoRouterFunctionDsl(mutableListOf()).apply(block)
        routes.add(RouterFunctions.nest(RequestPredicates.path("/api"), nested.build()))
    }
}

// 사용
fun routes() = coRouter {
    "/api".nest {
        GET("/users") { req -> ok().bodyValueAndAwait(userService.findAll()) }
        POST("/users") { req ->
            val body = req.awaitBody<CreateUserRequest>()
            created(URI("/api/users/${user.id}")).bodyValueAndAwait(userService.create(body))
        }
    }
}
```

**Step 3 — 다양한 관점**

DSL 설계 핵심 메커니즘:

| 기법 | 역할 | 예시 |
|------|------|------|
| Extension function on lambda receiver | 스코프 제한 | `Table.() -> Unit` |
| `@DslMarker` | 외부 리시버 접근 차단 | `@HtmlDsl` |
| `inline` + `reified` | 런타임 타입 정보 유지 | `inline fun <reified T>` |
| Operator overloading | 자연스러운 문법 | `"path" / "sub"` |
| Infix functions | 가독성 | `item shouldBe expected` |
| Context receivers (실험적) | 다중 리시버 | `context(Logger, Metrics)` |

**Step 4 — 구체적 예시**

```kotlin
// 프로덕션: 커스텀 Pipeline DSL 설계
@DslMarker
annotation class PipelineDsl

@PipelineDsl
class PipelineBuilder<T> {
    private val stages = mutableListOf<Stage<T>>()

    fun validate(block: suspend (T) -> ValidationResult) {
        stages.add(Stage.Validation(block))
    }

    fun transform(block: suspend (T) -> T) {
        stages.add(Stage.Transformation(block))
    }

    fun enrich(block: suspend (T) -> T) {
        stages.add(Stage.Enrichment(block))
    }

    fun onError(block: suspend (T, Throwable) -> ErrorAction) {
        stages.add(Stage.ErrorHandler(block))
    }

    // 조건부 스테이지
    fun conditional(
        predicate: suspend (T) -> Boolean,
        block: PipelineBuilder<T>.() -> Unit
    ) {
        val nested = PipelineBuilder<T>().apply(block)
        stages.add(Stage.Conditional(predicate, nested.build()))
    }

    internal fun build(): Pipeline<T> = Pipeline(stages.toList())
}

inline fun <reified T> pipeline(block: PipelineBuilder<T>.() -> Unit): Pipeline<T> {
    return PipelineBuilder<T>().apply(block).build()
}

// 사용
val orderPipeline = pipeline<Order> {
    validate { order ->
        if (order.items.isEmpty()) ValidationResult.failure("Empty order")
        else ValidationResult.success()
    }
    enrich { order ->
        val pricing = pricingService.calculate(order)
        order.copy(totalAmount = pricing.total, tax = pricing.tax)
    }
    conditional({ it.totalAmount > Money(1000) }) {
        validate { order ->
            fraudService.check(order) // 고액 주문만 사기 검증
        }
    }
    transform { order ->
        order.copy(status = OrderStatus.CONFIRMED)
    }
    onError { order, throwable ->
        logger.error(throwable) { "Pipeline failed for order ${order.id}" }
        ErrorAction.RETRY
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| Type-Safe Builder + @DslMarker | 컴파일 안전, IDE 지원 우수 | 설계 복잡 | 반복 사용되는 구조화 코드 |
| Annotation Processing (KSP) | 코드 생성, 유연 | 빌드 시간, 디버깅 어려움 | 보일러플레이트 제거 |
| String-based DSL | 유연, 런타임 파싱 | 타입 안전성 없음 | 사용자 입력 기반 |
| Builder Pattern (Java 스타일) | 단순, 익숙 | 장황, 타입 안전성 약함 | 간단한 객체 생성 |

**Step 6 — 성장 & 심화 학습**
- Kotlin Context Receivers (실험적)가 DSL 설계를 어떻게 변화시킬 수 있는지
- `@DslMarker`의 scope control 알고리즘 (이름이 같은 함수가 여러 리시버에 있을 때)
- Jetpack Compose의 `@Composable` DSL 구현과 컴파일러 플러그인의 역할
- kotlinx.html과 같은 라이브러리의 내부 구현 분석

**🎯 면접관 평가 기준:**
- **L6 PASS**: @DslMarker의 필요성과 동작, Type-Safe Builder 패턴 구현, Spring Router DSL 이해
- **L7 EXCEED**: 커스텀 DSL 설계 경험, context receiver와의 연계, 컴파일러 수준의 스코프 제어 이해
- 🚩 **RED FLAG**: DSL을 사용하기만 하고 만들지 못함, @DslMarker 없이 빌더 설계

---

### Q17: Inline Functions, Reified Types, 그리고 Contracts

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Kotlin Language Mastery

**Question:**
`inline` 함수의 바이트코드 레벨 동작과 성능 영향을 설명하라. `reified` 타입 파라미터가 JVM의 타입 소거를 우회하는 메커니즘, `crossinline`과 `noinline`의 차이, 그리고 Kotlin Contracts(`contract {}`)가 스마트 캐스트에 미치는 영향을 코드와 함께 설명하라.

---

**🧒 12살 비유:**
`inline`은 "레시피를 복사해서 붙여넣기"다. 함수를 호출하는 대신 함수의 코드를 그 자리에 직접 복사한다 — 전화 안 하고 메모를 보는 것처럼 빠르다. `reified`는 "포장을 뜯어서 안에 뭐가 있는지 확인"하는 것이다. 보통 Java에서는 포장지(제네릭)가 벗겨져서(타입 소거) 안의 물건 종류를 모르는데, `reified`는 복사-붙여넣기 덕분에 종류를 알 수 있다. `contract`는 "이 함수가 true를 반환하면 이 변수는 null이 아니야"라고 컴파일러에게 약속하는 것이다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
이 기능들은 Kotlin의 고급 추상화를 가능하게 하는 핵심 메커니즘이다. `require()`, `check()`, `run {}`, `let {}` 등 stdlib 함수가 모두 이 기능에 기반하며, 라이브러리 설계 시 필수적이다.

**Step 2 — 핵심 기술 설명**

```kotlin
// inline 함수의 바이트코드 효과
inline fun <T> measureTime(block: () -> T): Pair<T, Long> {
    val start = System.nanoTime()
    val result = block()
    val elapsed = System.nanoTime() - start
    return result to elapsed
}

// 호출 코드:
val (result, time) = measureTime { heavyComputation() }

// 컴파일 후 (인라인됨):
val start = System.nanoTime()
val result = heavyComputation()     // block()이 직접 삽입됨
val elapsed = System.nanoTime() - start
val pair = result to elapsed
// → Function 객체 할당 없음, 함수 호출 오버헤드 없음

// reified: 타입 소거 우회
inline fun <reified T> fromJson(json: String): T {
    // T::class.java 사용 가능! (non-inline에서는 컴파일 에러)
    return objectMapper.readValue(json, T::class.java)
}
// 호출: val user = fromJson<User>(jsonString)
// 컴파일 후: objectMapper.readValue(jsonString, User.class)
// → T가 구체적 타입으로 치환됨

// crossinline vs noinline
inline fun transaction(
    noinline onError: (Throwable) -> Unit,   // 인라인 안 됨, 변수에 저장 가능
    crossinline block: () -> Unit            // 인라인 되지만 non-local return 불가
) {
    try {
        // crossinline: block 안에서 return하면 transaction이 아니라
        // 바깥 함수를 return하게 될 수 있어서 막음
        runInNewThread { block() } // 다른 컨텍스트에서 실행되므로 non-local return 불가
    } catch (e: Throwable) {
        onError(e) // 변수로 저장/전달 가능 (noinline)
    }
}
```

Kotlin Contracts:

```kotlin
// contract: 컴파일러에게 함수의 효과를 알려줌
@OptIn(ExperimentalContracts::class)
inline fun <T> requireNotNull(value: T?, lazyMessage: () -> String): T {
    contract {
        returns() implies (value != null) // 이 함수가 정상 반환하면 value는 non-null
    }
    if (value == null) throw IllegalArgumentException(lazyMessage())
    return value
}

// 사용 후 스마트 캐스트:
fun processUser(user: User?) {
    requireNotNull(user) { "User must not be null" }
    // 여기서 user는 자동으로 User (non-null) 타입으로 스마트 캐스트!
    println(user.name) // Safe, 컴파일러가 non-null 보장
}

// callsInPlace contract: 람다 실행 보장
@OptIn(ExperimentalContracts::class)
inline fun <R> run(block: () -> R): R {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE) // 정확히 1번 실행
    }
    return block()
}

// 효과: 지역 변수 초기화를 보장
val result: String
run {
    result = "initialized" // callsInPlace(EXACTLY_ONCE) 덕분에
}                          // 컴파일러가 초기화를 인정함
println(result) // OK! contract 없으면 "must be initialized" 에러
```

**Step 3 — 다양한 관점**

inline의 트레이드오프:

| 측면 | inline 사용 | inline 미사용 |
|------|------------|--------------|
| Function 객체 할당 | 없음 (0 allocation) | 매번 할당 (GC 부하) |
| 바이트코드 크기 | 증가 (호출 지점마다 복사) | 작음 (함수 1개) |
| 디버깅 | 스택트레이스 복잡 | 명확한 스택 |
| non-local return | 가능 | 불가 |
| reified | 사용 가능 | 불가 |
| 적합한 크기 | 작은 함수 (1-5줄) | 큰 함수 |

**Step 4 — 구체적 예시**

```kotlin
// 프로덕션: Type-safe config reader with reified
@Service
class ConfigService(private val environment: Environment) {

    inline fun <reified T> getRequired(key: String): T {
        val value = environment.getProperty(key, T::class.java)
            ?: throw ConfigMissingException("Required config '$key' (${T::class.simpleName}) not found")
        return value
    }

    inline fun <reified T> getOptional(key: String, default: T): T {
        return environment.getProperty(key, T::class.java) ?: default
    }
}

// 사용: 타입 추론 + 타입 안전
val port: Int = config.getRequired("server.port")          // String → Int 자동 변환
val timeout: Duration = config.getRequired("app.timeout")  // String → Duration
val debug: Boolean = config.getOptional("app.debug", false)

// 프로덕션: Contract 기반 유효성 검증 DSL
@OptIn(ExperimentalContracts::class)
inline fun <T : Any> T?.validate(
    fieldName: String,
    block: T.() -> Unit
): T {
    contract {
        returns() implies (this@validate != null)
    }
    requireNotNull(this) { "$fieldName must not be null" }
    this.block() // 스마트 캐스트 적용
    return this
}

// 사용
fun createOrder(request: OrderRequest?) {
    val validated = request.validate("request") {
        require(items.isNotEmpty()) { "Order must have items" }
        require(amount > Money.ZERO) { "Amount must be positive" }
    }
    // validated는 자동으로 OrderRequest (non-null)
    orderService.process(validated)
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| `inline` + `reified` | 제로 오버헤드, 타입 정보 유지 | 바이트코드 증가, public API 제한 | 유틸리티, DSL |
| 일반 제네릭 + `KClass` 파라미터 | 비인라인 가능, 오버라이드 가능 | 호출 시 `::class` 명시 | 인터페이스, abstract |
| Contracts | 스마트 캐스트 지원 | 실험적 API, 검증 안 됨 (신뢰 기반) | 검증 함수, 스코프 함수 |
| TypeToken (Java 패턴) | 중첩 제네릭 보존 | 장황, Kotlin스럽지 않음 | 복잡한 제네릭 |

**Step 6 — 성장 & 심화 학습**
- `inline class`(value class)와 `inline fun`의 관계 (둘 다 인라인이지만 메커니즘 다름)
- Kotlin 2.0 K2 컴파일러에서 Contract의 확장 (custom contract annotations)
- `@PublishedApi`와 `internal inline fun`의 관계
- `inline` 함수의 바이트코드를 javap으로 분석하는 방법

**🎯 면접관 평가 기준:**
- **L6 PASS**: inline의 바이트코드 효과, reified의 타입 소거 우회, crossinline/noinline 차이
- **L7 EXCEED**: Contract의 스마트 캐스트 영향, 바이트코드 크기 트레이드오프 분석, 커스텀 라이브러리에서의 활용
- 🚩 **RED FLAG**: "inline은 성능을 위해 모든 함수에 사용", reified 없이 타입 소거 문제 모름

---

## 7. Spring Security

### Q18: OAuth2 Resource Server와 JWT 검증 파이프라인

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Spring Security

**Question:**
Spring Security의 OAuth2 Resource Server에서 JWT 토큰 검증이 내부적으로 어떤 단계를 거치는지 설명하라. `JwtDecoder`, `JwtAuthenticationConverter`, `ReactiveJwtDecoder`의 역할과 커스터마이징 포인트를 논하고, multi-tenant 환경에서 issuer별로 다른 JWK Set URI를 사용해야 할 때의 설계 전략을 제시하라.

---

**🧒 12살 비유:**
JWT는 "신분증"이고, Resource Server는 "건물 경비원"이다. 경비원이 하는 일: (1) 신분증이 진짜인지 확인 (서명 검증 - JwtDecoder), (2) 유효기간이 안 지났는지 확인, (3) 이 사람이 어떤 층에 갈 수 있는지 확인 (권한 변환 - JwtAuthenticationConverter). Multi-tenant는 "여러 회사가 입주한 빌딩"이라서, 각 회사의 신분증 시스템이 다르다 — 경비원이 회사별로 다른 검증 규칙을 적용해야 한다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
마이크로서비스 아키텍처에서 모든 서비스는 JWT를 검증해야 한다. Staff 레벨에서는 기본 설정을 넘어 커스텀 검증 로직, multi-tenant 지원, 성능 최적화(JWK 캐싱)를 설계할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

```
JWT 검증 파이프라인 (Spring Security 6.x):

Request → BearerTokenAuthenticationFilter
  → BearerTokenResolver.resolve(request) // Authorization: Bearer <token>
  → JwtDecoder.decode(token)
     1. 헤더 파싱 (kid, alg 추출)
     2. JWK Set URI에서 공개키 조회 (캐시 활용)
     3. 서명 검증 (RSA/EC)
     4. Claims 검증 (exp, nbf, iss, aud)
     5. Jwt 객체 반환
  → JwtAuthenticationConverter.convert(jwt)
     1. Claims에서 authorities 추출 (scope, roles 등)
     2. JwtAuthenticationToken 생성
  → SecurityContext에 Authentication 저장
```

```kotlin
// 커스터마이징 포인트들
@Configuration
@EnableWebFluxSecurity
class SecurityConfig {

    @Bean
    fun securityFilterChain(http: ServerHttpSecurity): SecurityWebFilterChain {
        return http
            .oauth2ResourceServer { oauth2 ->
                oauth2.jwt { jwt ->
                    jwt.jwtDecoder(customJwtDecoder())
                    jwt.jwtAuthenticationConverter(customConverter())
                }
            }
            .build()
    }

    // 커스텀 JwtDecoder: 추가 검증 로직
    @Bean
    fun customJwtDecoder(): ReactiveJwtDecoder {
        val decoder = NimbusReactiveJwtDecoder
            .withJwkSetUri("https://auth.company.com/.well-known/jwks.json")
            .jwsAlgorithm(SignatureAlgorithm.RS256)
            .build()

        // 추가 검증: issuer, audience, custom claims
        val validators = listOf(
            JwtTimestampValidator(Duration.ofSeconds(60)), // 60초 clock skew 허용
            JwtIssuerValidator("https://auth.company.com"),
            audienceValidator(),
            customClaimValidator() // 커스텀 claim 검증
        )
        decoder.setJwtValidator(DelegatingOAuth2TokenValidator(validators))
        return decoder
    }

    // 커스텀 권한 변환: JWT claims → Spring authorities
    @Bean
    fun customConverter(): ReactiveJwtAuthenticationConverter {
        val converter = ReactiveJwtAuthenticationConverter()
        converter.setJwtGrantedAuthoritiesConverter { jwt ->
            val roles = jwt.getClaimAsStringList("roles") ?: emptyList()
            val permissions = jwt.getClaimAsStringList("permissions") ?: emptyList()
            Flux.fromIterable(
                roles.map { SimpleGrantedAuthority("ROLE_$it") } +
                permissions.map { SimpleGrantedAuthority(it) }
            )
        }
        return converter
    }
}
```

Multi-tenant JWT 검증:

```kotlin
// 방법 1: Tenant별 JwtDecoder 라우팅
@Bean
fun multiTenantJwtDecoder(
    tenantRepository: TenantRepository
): ReactiveJwtDecoder {
    val decoderCache = ConcurrentHashMap<String, ReactiveJwtDecoder>()

    return ReactiveJwtDecoder { token ->
        // JWT 파싱 (검증 전) — issuer 추출
        val issuer = try {
            val jwt = JWTParser.parse(token)
            (jwt as? SignedJWT)?.jwtClaimsSet?.issuer
                ?: throw JwtException("Missing issuer")
        } catch (e: Exception) {
            throw JwtException("Invalid JWT format", e)
        }

        // issuer별 JwtDecoder 캐시
        val decoder = decoderCache.computeIfAbsent(issuer) { iss ->
            val tenant = tenantRepository.findByIssuer(iss)
                ?: throw JwtException("Unknown issuer: $iss")
            NimbusReactiveJwtDecoder
                .withJwkSetUri(tenant.jwkSetUri)
                .build()
                .also { it.setJwtValidator(tenantValidator(tenant)) }
        }

        decoder.decode(token)
    }
}

// 방법 2: Spring Security의 JwtIssuerReactiveAuthenticationManagerResolver (내장)
@Bean
fun authenticationManagerResolver(): JwtIssuerReactiveAuthenticationManagerResolver {
    val trustedIssuers = setOf(
        "https://tenant-a.auth.com",
        "https://tenant-b.auth.com"
    )
    return JwtIssuerReactiveAuthenticationManagerResolver { issuer ->
        if (issuer in trustedIssuers) {
            Mono.just(JwtReactiveAuthenticationManager(
                NimbusReactiveJwtDecoder.withJwkSetUri("$issuer/.well-known/jwks.json").build()
            ))
        } else {
            Mono.error(JwtException("Untrusted issuer: $issuer"))
        }
    }
}
```

**Step 3 — 다양한 관점**

| 측면 | Opaque Token | JWT (Self-contained) |
|------|-------------|---------------------|
| 검증 방식 | Auth Server에 introspection 요청 | 로컬 서명 검증 |
| 네트워크 의존 | 매 요청마다 (캐시 가능) | JWK 초기 로드만 |
| Revocation | 즉시 (서버에서 확인) | 어려움 (만료까지 유효) |
| 페이로드 크기 | 작음 (참조만) | 클 수 있음 (claims 포함) |
| 적합한 곳 | 보안 최우선, 즉시 revoke 필요 | 마이크로서비스, 분산 검증 |

**Step 4 — 구체적 예시**

```kotlin
// JWK 캐싱 최적화
@Bean
fun optimizedJwtDecoder(): ReactiveJwtDecoder {
    // JWK Set 캐싱: 기본 5분, 실패 시 30초 후 재시도
    val jwkSource = JWKSourceBuilder
        .create<SecurityContext>(URL("https://auth.company.com/.well-known/jwks.json"))
        .cache(
            Duration.ofMinutes(5).toMillis(),  // TTL
            Duration.ofMinutes(15).toMillis()   // Refresh timeout
        )
        .rateLimited(
            Duration.ofSeconds(30).toMillis()   // 최소 갱신 간격
        )
        .build()

    return NimbusReactiveJwtDecoder(
        NimbusJwtDecoder.withJwkSource(jwkSource).build()::decode
    )
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| JWK Set URI 기반 | 표준적, 키 로테이션 자동 | 네트워크 의존 (초기) | 대부분 |
| 공개키 직접 설정 | 네트워크 무의존 | 키 로테이션 수동 | 키 고정 환경 |
| Multi-tenant resolver | 유연한 issuer 라우팅 | 캐시 관리 복잡 | SaaS |
| Token introspection | 즉시 revoke | 매 요청 네트워크 호출 | 고보안 |

**Step 6 — 성장 & 심화 학습**
- JWT revocation 전략: short-lived token + refresh token rotation, token blacklist(Redis)
- Spring Security의 `SecurityContext` 전파와 코루틴의 관계 (`ReactorContextWebFilter`)
- PASETO vs JWT, DPoP(Demonstrating Proof of Possession) 바인딩
- OAuth 2.1의 변경사항 (implicit flow 제거, PKCE 필수)

**🎯 면접관 평가 기준:**
- **L6 PASS**: JWT 검증 파이프라인 설명, JwtDecoder/Converter 커스터마이징, multi-tenant 접근법 1개
- **L7 EXCEED**: JWK 캐싱 최적화, token revocation 전략, Opaque vs JWT trade-off, 보안 헤더 설정 (HSTS, CSP)
- 🚩 **RED FLAG**: JWT 서명 검증 원리 모름, Secret key로 HMAC 사용(마이크로서비스에서)

---

### Q19: Method Security와 Reactive Security Chain

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Spring Security

**Question:**
Spring Security 6.x의 `@PreAuthorize`, `@PostAuthorize`, `@PostFilter`는 내부적으로 어떻게 동작하는가? AOP 기반 method security와 WebFlux의 reactive security filter chain은 어떻게 통합되는가? 코루틴의 `suspend` 함수에 `@PreAuthorize`를 적용할 때의 제한사항과 해결책을 설명하라.

---

**🧒 12살 비유:**
`@PreAuthorize`는 "문 앞의 경비원"이고, `@PostAuthorize`는 "나갈 때 짐검사하는 경비원"이다. `@PostFilter`는 "가방에서 허용된 물건만 남기는 세관원"이다. WebFlux의 security chain은 "건물 입구의 여러 검문소"인데, reactive라서 "줄을 서지 않고 번호표를 받는 시스템"이다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
URL 기반 보안만으로는 부족한 상황(같은 API에서 사용자 역할에 따라 다른 데이터 반환)에서 method security가 필수적이다. 코루틴 환경에서의 동작을 정확히 이해해야 보안 허점을 방지할 수 있다.

**Step 2 — 핵심 기술 설명**

```kotlin
// Method Security 내부 동작 (Spring Security 6.x):
// 1. @EnableMethodSecurity → AuthorizationAdvisor 등록
// 2. 각 @PreAuthorize Bean에 AOP 프록시 생성
// 3. 메서드 호출 시 → AuthorizationManagerBeforeMethodInterceptor 실행
// 4. SpEL 표현식 평가 → SecurityContext에서 Authentication 획득
// 5. 권한 확인 후 원본 메서드 호출 또는 AccessDeniedException

@Service
@PreAuthorize("isAuthenticated()") // 클래스 레벨: 모든 메서드에 적용
class OrderService(private val orderRepository: OrderRepository) {

    @PreAuthorize("hasRole('ADMIN') or #userId == authentication.principal.id")
    suspend fun getOrders(userId: String): List<Order> {
        return orderRepository.findByUserId(userId)
    }

    @PostAuthorize("returnObject.ownerId == authentication.principal.id or hasRole('ADMIN')")
    suspend fun getOrder(orderId: String): Order {
        return orderRepository.findById(orderId)
            ?: throw NotFoundException("Order not found")
    }

    @PostFilter("filterObject.status != 'DRAFT' or hasRole('ADMIN')")
    suspend fun getAllOrders(): List<Order> {
        return orderRepository.findAll() // DRAFT 주문은 ADMIN만 볼 수 있음
    }

    @PreAuthorize("@orderSecurityService.canCancel(#orderId, authentication)")
    suspend fun cancelOrder(orderId: String) {
        // @로 다른 Bean의 메서드를 SpEL에서 호출 가능
        orderRepository.updateStatus(orderId, OrderStatus.CANCELLED)
    }
}

// 커스텀 Authorization 로직을 Bean으로 분리
@Service("orderSecurityService")
class OrderSecurityService(private val orderRepository: OrderRepository) {
    suspend fun canCancel(orderId: String, authentication: Authentication): Boolean {
        val order = orderRepository.findById(orderId) ?: return false
        val user = authentication.principal as UserDetails
        return order.ownerId == user.id &&
               order.status in listOf(OrderStatus.PENDING, OrderStatus.CONFIRMED) &&
               order.createdAt.isAfter(Instant.now().minus(Duration.ofHours(24)))
    }
}
```

코루틴 + Method Security 제한사항:

```kotlin
// Spring Security 6.x에서 코루틴 suspend 함수의 @PreAuthorize 지원됨
// 내부적으로 ReactiveMethodSecurityConfiguration 사용

// 주의점 1: SecurityContext 전파
// WebFlux → 코루틴: ReactorContext를 통해 SecurityContext 전파
// 새 coroutineScope를 만들어도 ReactorContext는 전파됨 → 안전

// 주의점 2: @PostAuthorize에서 returnObject
// suspend 함수의 반환값은 Continuation을 통해 전달됨
// Spring Security가 이를 unwrap하여 실제 반환값으로 @PostAuthorize 평가

// 주의점 3: @PostFilter는 List/Collection에서만 동작
// Flow<T>에는 직접 적용 불가 → 수동 필터링 필요
@PreAuthorize("isAuthenticated()")
fun getOrdersFlow(): Flow<Order> {
    return orderRepository.findAllAsFlow()
        .filter { order ->
            // 수동 필터링
            val auth = ReactiveSecurityContextHolder.getContext()
                .awaitSingleOrNull()?.authentication
            order.status != OrderStatus.DRAFT || auth?.hasRole("ADMIN") == true
        }
}
```

**Step 3 — 다양한 관점**

| 방식 | 검사 시점 | 적합한 곳 | 성능 영향 |
|------|----------|-----------|----------|
| URL 기반 (SecurityFilterChain) | 요청 진입 시 | 경로별 인증/인가 | 최소 |
| @PreAuthorize | 메서드 호출 전 | 비즈니스 로직 수준 권한 | AOP 프록시 비용 |
| @PostAuthorize | 메서드 호출 후 | 결과 기반 권한 | 불필요한 DB 조회 가능 |
| @PostFilter | 결과 반환 시 | 결과 필터링 | 전체 로드 후 필터 (N+1 주의) |
| 프로그래밍 방식 | 코드 내부 | 복잡한 조건 | 직접 제어 |

**Step 4 — 구체적 예시**

```kotlin
// 프로덕션: 커스텀 Permission Evaluator
@Component
class DomainPermissionEvaluator : PermissionEvaluator {
    override fun hasPermission(
        authentication: Authentication,
        targetDomainObject: Any?,
        permission: Any
    ): Boolean {
        val user = authentication.principal as UserPrincipal
        return when (targetDomainObject) {
            is Order -> evaluateOrderPermission(user, targetDomainObject, permission as String)
            is Document -> evaluateDocumentPermission(user, targetDomainObject, permission as String)
            else -> false
        }
    }

    override fun hasPermission(
        authentication: Authentication,
        targetId: Serializable,
        targetType: String,
        permission: Any
    ): Boolean {
        // ID 기반 검증 (lazy loading)
        return when (targetType) {
            "Order" -> orderRepository.existsByIdAndOwnerId(targetId as String, authentication.name)
            else -> false
        }
    }

    private fun evaluateOrderPermission(user: UserPrincipal, order: Order, permission: String): Boolean {
        return when (permission) {
            "read" -> order.ownerId == user.id || user.hasRole("ADMIN")
            "write" -> order.ownerId == user.id && order.status == OrderStatus.DRAFT
            "cancel" -> order.ownerId == user.id && order.status in cancellableStatuses
            else -> false
        }
    }
}

// 사용
@PreAuthorize("hasPermission(#orderId, 'Order', 'write')")
suspend fun updateOrder(orderId: String, request: UpdateRequest): Order { ... }
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| SpEL @PreAuthorize | 선언적, 코드와 분리 | SpEL 디버깅 어려움 | 간단한 역할 기반 |
| PermissionEvaluator | 복잡한 도메인 권한 | 설정 복잡 | 객체 수준 ACL |
| 프로그래밍 방식 (직접 if문) | 명시적, 디버깅 용이 | 코드 산재, 누락 위험 | 복잡한 조건부 로직 |
| OPA(Open Policy Agent) 통합 | 정책 외부화, 통합 관리 | 네트워크 오버헤드 | 대규모 마이크로서비스 |

**Step 6 — 성장 & 심화 학습**
- Spring Security 6.x의 `AuthorizationProxyFactory`와 `@AuthorizeReturnObject`
- `@Secured` vs `@PreAuthorize` vs `@RolesAllowed` (JSR-250) 차이
- ABAC(Attribute-Based Access Control)와 RBAC의 trade-off
- Spring Authorization Server를 활용한 사내 IdP 구축

**🎯 면접관 평가 기준:**
- **L6 PASS**: AOP 기반 method security 동작 원리, SpEL 활용, 코루틴 지원 상태 인지
- **L7 EXCEED**: PermissionEvaluator 커스터마이징, Flow에서의 수동 보안 필터링, SecurityContext 전파 메커니즘, OPA 통합 경험
- 🚩 **RED FLAG**: URL 기반 보안만 알고 method security 모름, @PostFilter의 성능 영향 인식 없음

---


## 8. Testing in Spring

### Q20: TestContainers와 코루틴 테스트 전략

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Testing in Spring

**Question:**
Spring Boot 3.x에서 TestContainers를 활용한 통합 테스트 전략을 설계하라. `@ServiceConnection`과 `@DynamicPropertySource`의 차이, TestContainers의 라이프사이클 관리(테스트 클래스 vs 전체 스위트), 그리고 코루틴 테스트에서 `runTest`의 `TestCoroutineScheduler`가 `delay()`를 어떻게 가상화하는지 설명하라. 느린 통합 테스트를 최적화하는 전략을 제시하라.

---

**🧒 12살 비유:**
TestContainers는 "테스트용 미니 도시"다. 진짜 데이터베이스, 진짜 Redis를 작은 상자(Docker 컨테이너)에 넣어서 테스트한다. `runTest`는 "시간을 빨리 감기하는 리모컨"이다 — `delay(10분)`이 있어도 실제로 10분을 기다리지 않고 가상으로 10분을 넘긴다. `@ServiceConnection`은 "미니 도시의 주소를 자동으로 알려주는 네비게이션"이다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
테스트 전략은 Staff 레벨의 핵심 역량이다. 느린 통합 테스트는 개발 속도를 저하시키고, 불안정한 테스트는 CI 파이프라인의 신뢰도를 떨어뜨린다. TestContainers와 코루틴 테스트의 정확한 사용법을 아는 것이 중요하다.

**Step 2 — 핵심 기술 설명**

```kotlin
// Spring Boot 3.1+: @ServiceConnection (자동 설정 연결)
@SpringBootTest
@Testcontainers
class OrderServiceIntegrationTest {

    companion object {
        @Container
        @ServiceConnection // application.yml 없이 자동으로 connection 설정
        val postgres = PostgreSQLContainer("postgres:16-alpine")
            .withDatabaseName("orders")
            .withReuse(true) // 컨테이너 재사용으로 시작 시간 절약

        @Container
        @ServiceConnection
        val redis = GenericContainer("redis:7-alpine")
            .withExposedPorts(6379)
    }

    // @DynamicPropertySource: ServiceConnection이 지원하지 않는 경우
    companion object {
        @JvmStatic
        @DynamicPropertySource
        fun configureKafka(registry: DynamicPropertyRegistry) {
            registry.add("spring.kafka.bootstrap-servers") { kafka.bootstrapServers }
        }
    }
}
```

코루틴 테스트와 `runTest`:

```kotlin
// runTest: TestCoroutineScheduler로 가상 시간 사용
@Test
fun `should retry with backoff`() = runTest {
    val service = RetryService(testScheduler = this.testScheduler)

    // delay(1000), delay(2000), delay(4000)을 포함하는 로직
    val result = service.fetchWithRetry()

    // 실제 시간: 0ms (가상으로 7000ms 진행됨)
    assertEquals("success", result)
}

// TestDispatcher의 두 가지 모드
@Test
fun `StandardTestDispatcher - explicit advance`() = runTest {
    var result = ""
    launch {
        delay(1000)
        result = "done"
    }
    assertEquals("", result)        // 아직 실행 안 됨
    advanceTimeBy(1000)             // 가상 시간 진행
    assertEquals("done", result)    // 이제 실행됨
}

@Test
fun `UnconfinedTestDispatcher - eager execution`() = runTest(UnconfinedTestDispatcher()) {
    var result = ""
    launch {
        result = "done" // 즉시 실행 (delay 전까지)
    }
    assertEquals("done", result) // 바로 확인 가능
}
```

**Step 3 — 다양한 관점**

TestContainers 라이프사이클 전략:

| 전략 | 시작 시간 | 격리 | 적합한 곳 |
|------|----------|------|-----------|
| 테스트 메서드별 | 매우 느림 | 완벽 | 상태 오염 불가 허용 |
| 테스트 클래스별 (@Container) | 느림 | 클래스 내 공유 | 기본 전략 |
| Singleton (abstract base) | 빠름 (1회) | 테스트 간 데이터 누적 | CI 최적화 |
| .withReuse(true) | 최소 (재사용) | 수동 cleanup 필요 | 로컬 개발 |

**Step 4 — 구체적 예시**

```kotlin
// 프로덕션 테스트 베이스 클래스: Singleton TestContainers
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfile("test")
abstract class IntegrationTestBase {

    companion object {
        // Singleton 패턴: 모든 테스트 클래스가 같은 컨테이너 공유
        @JvmStatic
        val postgres = PostgreSQLContainer("postgres:16-alpine")
            .withDatabaseName("testdb")
            .apply { start() } // companion object 초기화 시 시작

        @JvmStatic
        val redis = GenericContainer("redis:7-alpine")
            .withExposedPorts(6379)
            .apply { start() }

        @JvmStatic
        @DynamicPropertySource
        fun properties(registry: DynamicPropertyRegistry) {
            registry.add("spring.r2dbc.url") {
                "r2dbc:postgresql://${postgres.host}:${postgres.firstMappedPort}/testdb"
            }
            registry.add("spring.r2dbc.username", postgres::getUsername)
            registry.add("spring.r2dbc.password", postgres::getPassword)
            registry.add("spring.data.redis.host", redis::getHost)
            registry.add("spring.data.redis.port") { redis.firstMappedPort }
        }
    }

    @Autowired
    lateinit var webTestClient: WebTestClient

    @Autowired
    lateinit var r2dbcEntityTemplate: R2dbcEntityTemplate

    // 각 테스트 전 DB 클린업
    @BeforeEach
    fun cleanUp() = runBlocking {
        r2dbcEntityTemplate.databaseClient
            .sql("TRUNCATE orders, order_items CASCADE")
            .await()
    }
}

// 실제 테스트
class OrderApiTest : IntegrationTestBase() {

    @Test
    fun `should create order and return 201`() = runTest {
        val request = CreateOrderRequest(
            items = listOf(OrderItem("product-1", 2)),
            amount = Money(100.0)
        )

        webTestClient.post()
            .uri("/api/v1/orders")
            .contentType(MediaType.APPLICATION_JSON)
            .bodyValue(request)
            .exchange()
            .expectStatus().isCreated
            .expectBody<OrderResponse>()
            .consumeWith { response ->
                assertNotNull(response.responseBody?.id)
                assertEquals(OrderStatus.PENDING, response.responseBody?.status)
            }
    }

    @Test
    fun `should handle concurrent order creation`() = runTest {
        // 동시성 테스트: 같은 상품의 재고가 정확히 차감되는지
        val results = (1..10).map {
            async(Dispatchers.IO) {
                runCatching {
                    webTestClient.post()
                        .uri("/api/v1/orders")
                        .bodyValue(CreateOrderRequest(listOf(OrderItem("limited-product", 1)), Money(50.0)))
                        .exchange()
                        .returnResult<OrderResponse>()
                        .status
                }
            }
        }.awaitAll()

        val successes = results.count { it.getOrNull()?.is2xxSuccessful == true }
        assertTrue(successes <= AVAILABLE_STOCK)
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| TestContainers | 실제 DB 테스트, 높은 신뢰도 | Docker 필요, 느린 시작 | 통합 테스트 |
| H2 In-Memory | 빠른 시작, Docker 불요 | SQL 방언 차이, 기능 제한 | 단순 CRUD 테스트 |
| MockK + 단위 테스트 | 최고 속도, 격리 | 통합 문제 미발견 | 비즈니스 로직 |
| @DataR2dbcTest (슬라이스) | 빠름, 필요한 것만 로드 | 전체 통합 미검증 | Repository 테스트 |

**Step 6 — 성장 & 심화 학습**
- TestContainers Cloud: 로컬 Docker 없이 원격 컨테이너 사용
- `runTest`의 `backgroundScope`와 `testScope`의 차이
- Turbine 라이브러리로 Flow 테스트 (awaitItem, awaitComplete)
- Spring Boot 3.1의 `@TestConfiguration` + TestContainers `@Bean` 패턴

**🎯 면접관 평가 기준:**
- **L6 PASS**: TestContainers 설정 및 라이프사이클 관리, runTest 기본 사용, 슬라이스 테스트 이해
- **L7 EXCEED**: Singleton 패턴으로 테스트 최적화, 동시성 테스트 설계, 가상 시간 활용, CI 파이프라인 최적화
- 🚩 **RED FLAG**: H2로만 테스트하고 실제 DB 차이 모름, runTest 안 쓰고 runBlocking으로 코루틴 테스트

---

### Q21: MockK vs Mockito와 Slice Testing

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Testing in Spring

**Question:**
Kotlin에서 MockK이 Mockito보다 선호되는 기술적 이유를 설명하라. `suspend` 함수 모킹, `extension function` 모킹, `object` 모킹에서의 차이를 코드로 보여라. Spring의 슬라이스 테스트(`@WebFluxTest`, `@DataR2dbcTest`)에서 MockK을 사용할 때의 설정과, `coEvery`/`coVerify`의 내부 동작을 설명하라.

---

**🧒 12살 비유:**
Mockito는 "Java용 연극 대역"이고, MockK은 "Kotlin용 연극 대역"이다. Kotlin 배우는 특별한 기술이 있다 — 잠깐 멈추기(`suspend`), 분신술(`extension function`), 유일한 존재(`object`). Mockito 대역은 이런 기술을 잘 흉내 못 내지만, MockK 대역은 완벽히 따라 한다. `coEvery`는 "이 배우가 잠깐 멈추는 장면에서는 이렇게 연기해"라는 지시다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
Kotlin 프로젝트에서 테스트 라이브러리 선택은 팀 생산성에 직접적 영향을 미친다. Staff 레벨에서는 도구의 내부 동작을 이해하고 적합한 선택을 할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

```kotlin
// MockK이 Mockito보다 Kotlin에 적합한 이유:

// 1. suspend 함수 모킹
// MockK:
val service = mockk<UserService>()
coEvery { service.findById(any()) } returns User("test") // coEvery for suspend

// Mockito: 별도 설정 필요
// `whenever(runBlocking { service.findById(any()) }).thenReturn(User("test"))`
// 또는 mockito-kotlin 확장 사용해도 어색함

// 2. Extension function 모킹
// MockK:
mockkStatic("com.example.ExtensionsKt") // 파일 레벨 지정
every { "test".encrypt() } returns "encrypted"

// Mockito: 불가능 (static method 모킹으로 우회해야 함)

// 3. Object / Companion 모킹
// MockK:
mockkObject(UserValidator)
every { UserValidator.validate(any()) } returns true

// Mockito: 매우 어려움 (mockStatic 사용)

// 4. Final class 모킹 (Kotlin의 기본이 final)
// MockK: 기본 지원 (Objenesis + bytecode manipulation)
// Mockito: mockito-extensions 파일 또는 @MockitoSettings 필요

// 5. 타입 안전한 matchers
// MockK:
every { service.find(match { it.length > 3 }) } returns result

// Mockito: any() 남용 시 타입 안전성 저하
```

코루틴 테스트에서 MockK 활용:

```kotlin
@WebFluxTest(OrderController::class)
@Import(MockKTestConfiguration::class)
class OrderControllerTest {

    @Autowired
    lateinit var webTestClient: WebTestClient

    @MockkBean // Spring MockK 통합
    lateinit var orderService: OrderService

    @Test
    fun `GET orders should return 200`() = runTest {
        // coEvery: suspend 함수 스텁 설정
        coEvery {
            orderService.getOrders(any())
        } returns listOf(
            Order(id = "1", status = OrderStatus.PENDING)
        )

        webTestClient.get()
            .uri("/api/v1/orders?userId=user1")
            .exchange()
            .expectStatus().isOk
            .expectBodyList<OrderResponse>()
            .hasSize(1)

        // coVerify: suspend 함수 호출 검증
        coVerify(exactly = 1) {
            orderService.getOrders("user1")
        }
    }

    @Test
    fun `should handle service timeout`() = runTest {
        coEvery {
            orderService.getOrders(any())
        } coAnswers {
            delay(5000) // 가상 시간에서 timeout 시뮬레이션
            throw TimeoutCancellationException("Timeout")
        }

        webTestClient.get()
            .uri("/api/v1/orders?userId=user1")
            .exchange()
            .expectStatus().is5xxServerError
    }
}
```

**Step 3 — 다양한 관점**

| 기능 | MockK | Mockito-Kotlin | 비고 |
|------|-------|----------------|------|
| suspend 함수 | coEvery/coVerify | runBlocking 래핑 | MockK이 자연스러움 |
| Extension function | mockkStatic | 불가 (우회 필요) | MockK 고유 기능 |
| Object/Companion | mockkObject | mockStatic (Java) | MockK이 간편 |
| Final class | 기본 지원 | 설정 필요 | MockK 편의성 |
| Relaxed mock | mockk(relaxed=true) | 없음 | 빠른 프로토타이핑 |
| Spring 통합 | @MockkBean (SpringMockK) | @MockBean (내장) | 추가 의존성 차이 |
| DSL 스타일 | Kotlin DSL | Kotlin DSL (확장) | 유사 |

**Step 4 — 구체적 예시**

```kotlin
// 슬라이스 테스트: Repository 레이어만 테스트
@DataR2dbcTest
@Import(TestR2dbcConfiguration::class)
class OrderRepositoryTest(
    @Autowired private val repository: OrderCoroutineRepository,
    @Autowired private val template: R2dbcEntityTemplate
) {

    @Test
    fun `should save and find order`() = runTest {
        val order = Order(
            userId = "user-1",
            status = OrderStatus.PENDING,
            amount = BigDecimal("100.00")
        )

        val saved = repository.save(order)
        assertNotNull(saved.id)

        val found = repository.findById(saved.id!!)
        assertNotNull(found)
        assertEquals("user-1", found?.userId)
    }
}

// 단위 테스트: 비즈니스 로직 격리
class OrderServiceUnitTest {

    private val orderRepository = mockk<OrderCoroutineRepository>()
    private val paymentService = mockk<PaymentService>()
    private val eventPublisher = mockk<ApplicationEventPublisher>(relaxed = true)

    private val sut = OrderService(orderRepository, paymentService, eventPublisher)

    @Test
    fun `should create order with payment validation`() = runTest {
        // Given
        val request = CreateOrderRequest(items = listOf(item), amount = Money(100))
        coEvery { paymentService.validate(any()) } returns PaymentValidation.APPROVED
        coEvery { orderRepository.save(any()) } answers {
            firstArg<Order>().copy(id = "generated-id")
        }

        // When
        val result = sut.createOrder(request)

        // Then
        assertEquals("generated-id", result.id)
        assertEquals(OrderStatus.PENDING, result.status)

        coVerify(ordering = Ordering.ORDERED) {
            paymentService.validate(any())
            orderRepository.save(match { it.amount == Money(100) })
        }
        verify { eventPublisher.publishEvent(ofType<OrderCreatedEvent>()) }
    }

    @Test
    fun `should throw when payment declined`() = runTest {
        coEvery { paymentService.validate(any()) } returns PaymentValidation.DECLINED

        assertThrows<PaymentDeclinedException> {
            sut.createOrder(CreateOrderRequest(items = listOf(item), amount = Money(100)))
        }

        coVerify(exactly = 0) { orderRepository.save(any()) }
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| MockK | Kotlin 네이티브, suspend 지원 | 추가 의존성, 일부 성능 이슈 | Kotlin 프로젝트 |
| Mockito-Kotlin | Spring 내장 지원 | suspend 어색, final class 설정 | Java+Kotlin 혼용 |
| Fakes (수동 구현) | 완전한 제어, 높은 신뢰도 | 구현/유지 비용 | 핵심 도메인 |
| Kotest | BDD 스타일, 풍부한 assertions | 학습 곡선, Spring 통합 설정 | BDD 선호 팀 |

**Step 6 — 성장 & 심화 학습**
- MockK의 `spyk()` vs `mockk()`의 사용 구분 (부분 모킹)
- `clearAllMocks()` vs `unmockkAll()`의 차이와 테스트 격리
- Kotest의 `eventually()`, `continually()` 비동기 assertion
- Spring의 `@MockBean`이 ApplicationContext를 재생성하는 문제와 해결

**🎯 면접관 평가 기준:**
- **L6 PASS**: MockK의 Kotlin 우위 설명, coEvery/coVerify 사용, 슬라이스 테스트 설정
- **L7 EXCEED**: Fake vs Mock 전략적 선택, 테스트 피라미드 설계, ApplicationContext 재생성 최적화, 동시성 테스트
- 🚩 **RED FLAG**: 모든 테스트에 @SpringBootTest, mock 남용(실제 통합 미검증)

---

## 9. Spring Boot Operational

### Q22: Actuator 커스터마이징과 Micrometer

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Spring Boot Operational

**Question:**
Spring Boot Actuator의 Health Check 아키텍처를 설명하라. 커스텀 `HealthIndicator`가 외부 서비스(DB, Redis, 외부 API)의 상태를 반영할 때, cascading failure를 방지하는 전략은 무엇인가? Micrometer로 비즈니스 메트릭(주문 처리량, 결제 성공률)을 수집하고 Prometheus로 노출할 때의 메트릭 설계 원칙(카디널리티, 네이밍, 히스토그램 vs 서머리)을 논하라.

---

**🧒 12살 비유:**
Health Check는 "매일 아침 선생님이 출석 체크하는 것"이다. 학생(서비스)이 "여기요!"라고 대답하면 건강한 것. 커스텀 HealthIndicator는 "체육 선생님이 특별히 체력 테스트를 하는 것"이다. 그런데 체력 테스트 자체가 너무 힘들면(외부 서비스 타임아웃) 학생이 쓰러진다(cascading failure). Micrometer는 "학교 곳곳에 설치된 CCTV와 센서"다 — 무슨 일이 일어나는지 숫자로 기록한다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
프로덕션 운영에서 적절한 health check과 메트릭은 장애 감지, 자동 복구(K8s readiness/liveness), 비즈니스 모니터링의 기반이다. 잘못된 health check이 오히려 장애를 유발하는 사례가 많다.

**Step 2 — 핵심 기술 설명**

```kotlin
// Health Check 아키텍처
// /actuator/health → HealthEndpoint → CompositeHealthContributor
//   → HealthIndicator들을 순회하며 상태 수집
//   → 가장 나쁜 상태가 전체 상태 결정 (DOWN > OUT_OF_SERVICE > UP)

// Liveness vs Readiness 분리 (K8s)
// /actuator/health/liveness  → 앱이 살아있는가? (restart 결정)
// /actuator/health/readiness → 트래픽 받을 수 있는가? (routing 결정)

@Component
class ExternalApiHealthIndicator(
    private val webClient: WebClient
) : ReactiveHealthIndicator {

    override fun health(): Mono<Health> {
        return webClient.get()
            .uri("/health")
            .retrieve()
            .toBodilessEntity()
            .timeout(Duration.ofSeconds(3)) // 타임아웃 필수!
            .map { Health.up().build() }
            .onErrorResume { ex ->
                // Health check 실패가 서비스를 죽이지 않도록
                Mono.just(
                    Health.down()
                        .withDetail("error", ex.message)
                        .withDetail("timestamp", Instant.now())
                        .build()
                )
            }
    }
}

// Readiness 그룹에만 포함 (외부 서비스 장애 시 트래픽만 중단, 재시작 안 함)
// application.yml:
// management.endpoint.health.group:
//   readiness:
//     include: db, redis, externalApi
//   liveness:
//     include: livenessState  # 앱 자체만 (외부 의존 없음)
```

Micrometer 메트릭 설계:

```kotlin
@Service
class OrderMetricsService(private val meterRegistry: MeterRegistry) {

    // 카운터: 주문 처리 결과
    private val orderCounter = Counter.builder("orders.processed")
        .description("Total orders processed")
        .tag("service", "order-service")
        .register(meterRegistry)

    // 타이머: 주문 처리 시간 (히스토그램)
    private val orderTimer = Timer.builder("orders.processing.duration")
        .description("Order processing duration")
        .publishPercentileHistogram() // Prometheus histogram으로 노출
        .minimumExpectedValue(Duration.ofMillis(10))
        .maximumExpectedValue(Duration.ofSeconds(30))
        .register(meterRegistry)

    // 게이지: 현재 처리 중인 주문 수
    private val activeOrders = AtomicInteger(0)
    init {
        Gauge.builder("orders.active", activeOrders) { it.get().toDouble() }
            .description("Currently processing orders")
            .register(meterRegistry)
    }

    // DistributionSummary: 주문 금액 분포
    private val orderAmountSummary = DistributionSummary.builder("orders.amount")
        .description("Order amount distribution")
        .publishPercentiles(0.5, 0.95, 0.99) // client-side percentiles
        .baseUnit("dollars")
        .register(meterRegistry)

    suspend fun recordOrderProcessed(order: Order, status: String, duration: Duration) {
        orderCounter.increment()
        orderTimer.record(duration)
        orderAmountSummary.record(order.amount.toDouble())

        // 동적 태그는 카디널리티 주의!
        meterRegistry.counter("orders.by_status",
            "status", status,        // OK: 제한된 값 (COMPLETED, FAILED, CANCELLED)
            // "user_id", order.userId // 🚨 절대 금지! 무한 카디널리티
        ).increment()
    }
}
```

**Step 3 — 다양한 관점**

메트릭 설계 원칙 — RED/USE 방법론:

| 방법론 | 지표 | 예시 |
|--------|------|------|
| **RED** (Request) | Rate | orders.processed (Counter) |
| | Error | orders.by_status{status=FAILED} |
| | Duration | orders.processing.duration (Timer) |
| **USE** (Resource) | Utilization | jvm.memory.used / jvm.memory.max |
| | Saturation | jvm.threads.states{state=BLOCKED} |
| | Errors | jvm.gc.pause |

카디널리티 문제:

```
카디널리티 = 태그의 가능한 값 조합 수

LOW (안전):  status={COMPLETED, FAILED, CANCELLED} → 3개
MEDIUM:      endpoint={/api/v1/orders, /api/v1/users, ...} → 10-50개
HIGH (위험): userId={user1, user2, ...} → 수백만 개!

카디널리티가 높으면:
  - Prometheus 메모리 폭증
  - 쿼리 성능 저하
  - Grafana 대시보드 렌더링 실패
```

**Step 4 — 구체적 예시**

```kotlin
// 프로덕션: 커스텀 Actuator 엔드포인트
@Component
@Endpoint(id = "orderStats")
class OrderStatsEndpoint(
    private val orderRepository: OrderCoroutineRepository,
    private val meterRegistry: MeterRegistry
) {
    @ReadOperation
    suspend fun stats(): OrderStatsResponse {
        return OrderStatsResponse(
            totalOrders = orderRepository.count(),
            activeOrders = meterRegistry.get("orders.active").gauge().value().toLong(),
            averageProcessingTime = meterRegistry.get("orders.processing.duration")
                .timer().mean(TimeUnit.MILLISECONDS),
            successRate = calculateSuccessRate()
        )
    }

    @ReadOperation
    suspend fun statsByStatus(@Selector status: String): StatusStats {
        return StatusStats(
            status = status,
            count = orderRepository.countByStatus(OrderStatus.valueOf(status))
        )
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| Prometheus histogram | 서버 사이드 집계, 정확 | 버킷 설정 필요, 저장 비용 | SLO 기반 알림 |
| Client-side percentiles | 설정 간단, 직관적 | 집계 불가(여러 인스턴스) | 단일 인스턴스 |
| OpenTelemetry Metrics | 벤더 중립, 트레이싱 통합 | 설정 복잡 | 멀티 벤더 |
| Custom Actuator endpoint | 비즈니스 메트릭 노출 | 구현 필요 | 운영 대시보드 |

**Step 6 — 성장 & 심화 학습**
- SLO 기반 알림: `histogram_quantile(0.99, rate(http_duration_bucket[5m]))` 기반 설정
- Micrometer의 `MeterFilter`로 메트릭 이름 변환, 태그 추가/제거, 카디널리티 제한
- Spring Boot Admin과 Actuator 통합
- Grafana에서의 Prometheus 쿼리 최적화 (recording rules)

**🎯 면접관 평가 기준:**
- **L6 PASS**: Health Check liveness/readiness 분리, 메트릭 타입(Counter/Timer/Gauge) 적절한 사용, 카디널리티 인식
- **L7 EXCEED**: cascading failure 방지 전략, RED/USE 방법론, 히스토그램 vs 서머리 trade-off, SLO 기반 알림 설계
- 🚩 **RED FLAG**: Health check에 타임아웃 없음, userId를 태그로 사용, Counter vs Gauge 혼동

---

### Q23: GraalVM Native Image와 시작 최적화

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Spring Boot Operational

**Question:**
Spring Boot 3.x의 GraalVM Native Image 지원이 내부적으로 어떻게 동작하는가? AOT(Ahead-of-Time) 처리가 리플렉션, 프록시, 리소스 접근에 미치는 영향과 제약사항을 설명하라. Native Image 빌드에서 실패하는 흔한 패턴과 해결 방법, 그리고 JIT 기반 대비 trade-off를 분석하라. 코루틴은 Native Image에서 어떻게 동작하는가?

---

**🧒 12살 비유:**
JIT은 "시험 시간에 교과서를 보면서 문제를 푸는 것"이다 — 처음엔 느리지만 자주 보는 페이지는 점점 빨리 찾는다. Native Image는 "시험 전에 교과서를 모두 암기하는 것"이다 — 시험 시작하자마자 바로 풀 수 있지만(빠른 시작), 교과서에 없는 문제가 나오면(리플렉션) 답할 수 없다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
서버리스, 컨테이너 환경에서 cold start 시간은 SLA에 직접 영향을 미친다. 그러나 Native Image의 제약을 이해하지 못하면 빌드 실패와 런타임 에러에 시달리게 된다.

**Step 2 — 핵심 기술 설명**

```
Spring Boot AOT 처리 파이프라인:

1. 빌드 시 (processAot):
   → ApplicationContext를 시뮬레이션
   → Bean 등록, @Conditional 평가, BeanPostProcessor 실행
   → 결과를 Java 코드/리소스로 생성

2. 생성되는 것들:
   → BeanDefinition 등록 코드 (리플렉션 대체)
   → Proxy 클래스 (동적 프록시 대체)
   → reflect-config.json (리플렉션 힌트)
   → resource-config.json (리소스 접근 힌트)
   → serialization-config.json

3. Native Image 빌드 (native:compile):
   → GraalVM native-image 도구 실행
   → Reachability Analysis: 도달 가능한 코드만 포함
   → Closed World Assumption: 런타임에 새 클래스 로딩 불가
```

제약사항과 해결:

```kotlin
// 1. 리플렉션: 빌드 시 등록 필수
@RegisterReflectionForBinding(OrderRequest::class, OrderResponse::class)
@Configuration
class NativeHints {
    // Jackson 직렬화에 리플렉션 필요
}

// 또는 RuntimeHintsRegistrar 구현
class MyRuntimeHints : RuntimeHintsRegistrar {
    override fun registerHints(hints: RuntimeHints, classLoader: ClassLoader?) {
        hints.reflection()
            .registerType(OrderRequest::class.java, MemberCategory.INVOKE_DECLARED_CONSTRUCTORS)
        hints.resources()
            .registerPattern("templates/*.html")
        hints.proxies()
            .registerJdkProxy(MyService::class.java)
    }
}

// 2. 동적 프록시: 인터페이스 기반만 가능 (CGLIB 대체)
// Spring Boot 3.x에서 @Configuration(proxyBeanMethods = false) 권장

// 3. 실패하는 흔한 패턴:
// ❌ Class.forName() 동적 로딩
// ❌ 런타임 바이트코드 생성 (ByteBuddy, CGLIB)
// ❌ ServiceLoader (명시적 등록 필요)
// ❌ 리소스 파일 직접 접근 (ClassLoader.getResource)

// 4. 코루틴 + Native Image:
// kotlinx-coroutines는 Native Image와 호환
// 단, 코루틴 디버깅 에이전트는 사용 불가 (-Dkotlinx.coroutines.debug)
// suspend 함수의 CPS 변환은 컴파일 타임에 완료되므로 문제 없음
```

**Step 3 — 다양한 관점**

| 측면 | JIT (HotSpot) | Native Image (GraalVM) |
|------|---------------|----------------------|
| 시작 시간 | 2-10초 | 0.05-0.5초 |
| Peak 성능 | 높음 (C2 최적화) | 중간 (AOT 한계) |
| 메모리 사용 | 높음 (JIT, 메타데이터) | 낮음 (50-70% 절감) |
| 빌드 시간 | 빠름 | 느림 (5-15분) |
| 디버깅 | 풍부 (JFR, JMX, heap dump) | 제한적 |
| 리플렉션 | 자유로움 | 명시적 등록 필수 |
| 라이브러리 호환 | 거의 모든 | 제한적 (native-incompatible 존재) |
| 적합한 곳 | 장시간 서비스, 복잡한 앱 | 서버리스, CLI, 짧은 수명 |

**Step 4 — 구체적 예시**

```kotlin
// 시작 최적화 조합 전략 (Native Image 없이)
@SpringBootApplication
class Application

fun main(args: Array<String>) {
    SpringApplication(Application::class.java).apply {
        // 1. Lazy initialization: 사용 시점에 Bean 생성
        setLazyInitialization(true)

        // 2. JVM 플래그 최적화
        // -XX:TieredStopAtLevel=1  (C1만, C2 스킵 — 시작 빠르지만 peak 낮음)
        // -XX:+UseSerialGC        (작은 힙에서 효율적)
        // -Xss256k                (스레드 스택 크기 축소)

        // 3. Spring Boot 3.2+: Virtual Thread 활용
        // spring.threads.virtual.enabled=true
    }.run(*args)
}

// CDS (Class Data Sharing) 활용
// Step 1: 클래스 리스트 추출
// java -Xshare:off -XX:DumpLoadedClassList=classes.lst -jar app.jar
// Step 2: 공유 아카이브 생성
// java -Xshare:dump -XX:SharedClassListFile=classes.lst -XX:SharedArchiveFile=app-cds.jsa
// Step 3: 아카이브와 함께 실행
// java -Xshare:on -XX:SharedArchiveFile=app-cds.jsa -jar app.jar
// 효과: 시작 시간 20-30% 단축
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 시작 시간 | Peak 성능 | 복잡도 | 사용 시점 |
|--------|----------|----------|--------|-----------|
| GraalVM Native | 최소 (50ms) | 중간 | 높음 | 서버리스 |
| CDS + AppCDS | 중간 (30% 개선) | 높음 | 낮음 | 일반 서비스 |
| Spring AOT (JIT) | 중간 (일부 개선) | 높음 | 중간 | AOT 전처리만 |
| CRaC (Checkpoint/Restore) | 최소 (즉시) | 높음 | 중간 | JDK 21+ |
| Lazy init + Tiered L1 | 중간 | 낮음 (초기) | 낮음 | 개발 환경 |

**Step 6 — 성장 & 심화 학습**
- `native-image --initialize-at-build-time` vs `--initialize-at-run-time` 제어
- Spring Boot의 `@Aot` 전용 설정과 프로파일
- GraalVM의 PGO(Profile-Guided Optimization)로 Native Image 성능 개선
- Project Leyden: JIT과 AOT의 중간 지점 (Condensation)

**🎯 면접관 평가 기준:**
- **L6 PASS**: AOT 처리 과정, 리플렉션 제약과 RuntimeHints, JIT vs Native trade-off
- **L7 EXCEED**: 빌드 파이프라인 최적화, CRaC/CDS 등 대안, 라이브러리 호환성 평가, PGO 활용
- 🚩 **RED FLAG**: "Native Image는 무조건 빠르다", 리플렉션 제약 모름

---

## 10. Data Access

### Q24: JPA vs Exposed, 트랜잭션 전파

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Data Access

**Question:**
Spring의 `@Transactional`에서 propagation 속성(REQUIRED, REQUIRES_NEW, NESTED, MANDATORY 등)이 각각 어떻게 동작하는가? `REQUIRES_NEW`가 새 Connection을 사용하는 이유와, Connection Pool 고갈의 위험을 설명하라. JPA의 1차 캐시(Persistence Context)와 `REQUIRES_NEW`의 상호작용, 그리고 Kotlin의 Exposed 프레임워크와 JPA의 설계 철학 차이를 논하라.

---

**🧒 12살 비유:**
트랜잭션은 "은행에서 돈을 옮기는 과정"이다. `REQUIRED`는 "이미 진행 중인 거래가 있으면 같이 처리"하는 것이다. `REQUIRES_NEW`는 "새 창구에서 완전히 별도 거래를 시작"하는 것 — 첫 번째 거래가 실패해도 두 번째는 영향 없다. 문제는 창구(Connection)가 제한되어 있어서, 새 창구를 계속 열면 다른 손님이 대기해야 한다. `NESTED`는 "같은 창구에서 부분 취소가 가능한 거래"다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
트랜잭션 전파를 잘못 사용하면 데이터 불일치, 데드락, Connection Pool 고갈이 발생한다. 특히 `REQUIRES_NEW`는 강력하지만 위험한 도구여서, 정확한 이해가 필수적이다.

**Step 2 — 핵심 기술 설명**

```kotlin
// Propagation 동작 비교
@Service
class OrderService(
    private val paymentService: PaymentService,
    private val auditService: AuditService
) {
    @Transactional // REQUIRED (기본)
    fun createOrder(request: OrderRequest): Order {
        val order = orderRepository.save(Order.from(request))

        // paymentService.charge()가 @Transactional(REQUIRED)이면:
        // → 같은 트랜잭션 참여, charge 실패 시 order도 롤백
        paymentService.charge(order)

        // auditService.log()가 @Transactional(REQUIRES_NEW)이면:
        // → 새 Connection으로 새 트랜잭션 시작
        // → order 트랜잭션이 롤백되어도 audit log는 유지!
        // → 하지만 Connection 2개 동시 사용 (Pool 주의)
        auditService.log(AuditEvent.ORDER_CREATED, order.id)

        return order
    }
}

@Service
class AuditService {
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    fun log(event: AuditEvent, entityId: String) {
        // 이 메서드는 항상 독립적으로 commit됨
        // 호출자 트랜잭션이 실패해도 감사 로그는 남아야 하므로
        auditRepository.save(AuditLog(event, entityId, Instant.now()))
    }
}
```

Connection Pool 고갈 시나리오:

```
Pool Size: 10 connections

Thread-1: @Transactional(REQUIRED) → Connection 1 획득
  └→ @Transactional(REQUIRES_NEW) → Connection 2 획득
      └→ @Transactional(REQUIRES_NEW) → Connection 3 획득

Thread-1이 3개의 Connection을 동시에 보유!
10개 스레드가 동시에 실행되면: 30개 Connection 필요 → Pool 고갈 → 데드락!

해결:
  1. REQUIRES_NEW 중첩 최소화 (최대 1단계)
  2. Pool 크기 = maxThreads * maxNestedTransactions
  3. 가능하면 NESTED 사용 (같은 Connection 내 Savepoint)
```

```kotlin
// Propagation 전체 정리
enum class Propagation {
    REQUIRED,      // 기존 트랜잭션 참여, 없으면 새로 생성 (기본)
    REQUIRES_NEW,  // 항상 새 트랜잭션 (기존 트랜잭션 중단)
    NESTED,        // 기존 트랜잭션 내 Savepoint (JDBC만, JPA 제한적)
    MANDATORY,     // 기존 트랜잭션 필수, 없으면 예외
    SUPPORTS,      // 있으면 참여, 없으면 없이 실행
    NOT_SUPPORTED, // 트랜잭션 없이 실행 (기존 트랜잭션 중단)
    NEVER          // 트랜잭션 없어야 함, 있으면 예외
}
```

JPA 1차 캐시와 REQUIRES_NEW:

```kotlin
@Transactional
fun processOrder(orderId: Long) {
    val order = orderRepository.findById(orderId) // 1차 캐시에 저장 (PC1)
    order.status = OrderStatus.PROCESSING

    // REQUIRES_NEW: 새 트랜잭션 = 새 Persistence Context (PC2)
    auditService.logWithNewTx(orderId) // PC2에서는 order 변경 안 보임!

    // PC1과 PC2는 완전히 독립
    // PC2에서 같은 order를 조회하면 DB에서 다시 읽음 (이전 상태)
}
```

JPA vs Exposed:

```kotlin
// JPA: 영속성 컨텍스트 기반, 엔티티 상태 추적
@Entity
class Order(
    @Id @GeneratedValue val id: Long = 0,
    var status: OrderStatus,
    @OneToMany(mappedBy = "order", cascade = [CascadeType.ALL])
    val items: MutableList<OrderItem> = mutableListOf()
)
// Dirty Checking: status 변경 시 자동으로 UPDATE 생성
// Lazy Loading: items 접근 시 별도 쿼리 (N+1 위험)

// Exposed: SQL DSL + DAO, 명시적 쿼리
object Orders : LongIdTable() {
    val status = enumerationByName<OrderStatus>("status", 20)
    val amount = decimal("amount", 10, 2)
}

// DSL 방식 (Type-safe SQL)
transaction {
    Orders.select(Orders.status eq OrderStatus.PENDING)
        .map { it[Orders.id].value to it[Orders.status] }
}

// DAO 방식
class OrderEntity(id: EntityID<Long>) : LongEntity(id) {
    var status by Orders.status
}
```

**Step 3 — 다양한 관점**

| 측면 | JPA/Hibernate | Exposed |
|------|---------------|---------|
| 패러다임 | ORM (객체-관계 매핑) | SQL DSL + 선택적 DAO |
| 쿼리 가시성 | 숨겨짐 (Dirty Checking, Lazy) | 명시적 (DSL이 곧 SQL) |
| N+1 문제 | 숨겨진 위험 | DSL에서 명시적 JOIN |
| 학습 곡선 | 높음 (PC 이해 필수) | 중간 (SQL 알면 쉬움) |
| Kotlin 친화도 | 낮음 (Java 기반) | 높음 (Kotlin DSL) |
| 2차 캐시 | 내장 (Ehcache 등) | 없음 |
| 마이그레이션 | Flyway/Liquibase | 동일 |
| 커뮤니티/생태계 | 거대 | 작음 (JetBrains) |

**Step 4 — 구체적 예시**

```kotlin
// 프로덕션: 안전한 REQUIRES_NEW 사용 패턴
@Service
class PaymentProcessingService(
    private val paymentRepository: PaymentRepository,
    private val auditService: AuditService,
    private val notificationService: NotificationService
) {
    @Transactional
    fun processPayment(paymentId: Long): PaymentResult {
        val payment = paymentRepository.findById(paymentId)
            ?: throw NotFoundException("Payment not found")

        return try {
            val result = executePayment(payment)
            payment.status = PaymentStatus.COMPLETED
            paymentRepository.save(payment)

            // 감사 로그: 결제 성공/실패와 무관하게 반드시 기록
            auditService.logPayment(payment, result) // REQUIRES_NEW

            result
        } catch (e: PaymentException) {
            payment.status = PaymentStatus.FAILED
            paymentRepository.save(payment)

            auditService.logPayment(payment, PaymentResult.failure(e)) // REQUIRES_NEW

            throw e // 외부 트랜잭션은 롤백되지만 audit log는 커밋됨
        }
    }
}

// Connection Pool 안전한 설정
// application.yml:
// spring.datasource.hikari:
//   maximum-pool-size: 20
//   minimum-idle: 5
//   connection-timeout: 5000  # 5초 대기 후 실패
//   leak-detection-threshold: 30000  # 30초 이상 미반환 시 경고
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| REQUIRED | 단순, Connection 절약 | 부분 롤백 불가 | 대부분의 경우 |
| REQUIRES_NEW | 독립 트랜잭션 보장 | Connection 추가, Pool 고갈 위험 | 감사 로그, 알림 |
| NESTED | 같은 Connection, Savepoint | JPA 제한적 지원 | 부분 롤백 필요 |
| 이벤트 기반 | 비동기 분리, 트랜잭션 격리 | 복잡성, eventual consistency | 마이크로서비스 |

**Step 6 — 성장 & 심화 학습**
- `TransactionTemplate`로 프로그래밍 방식 트랜잭션 제어
- `@Transactional` readOnly=true의 최적화 효과 (Hibernate flush mode, read replica 라우팅)
- JPA의 OSIV(Open Session In View) 안티패턴과 비활성화
- Spring의 `@TransactionalEventListener`와 `TransactionPhase`

**🎯 면접관 평가 기준:**
- **L6 PASS**: Propagation 옵션 4개 이상 설명, REQUIRES_NEW의 Connection 영향, JPA 1차 캐시 동작
- **L7 EXCEED**: Connection Pool 고갈 시나리오와 해결, Exposed와 JPA 설계 철학 비교, OSIV 이해
- 🚩 **RED FLAG**: self-invocation에서 @Transactional 동작 안 하는 이유 모름, REQUIRES_NEW 남용

---

### Q25: Optimistic Locking과 동시성 제어

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Data Access

**Question:**
JPA의 `@Version` 기반 Optimistic Locking은 내부적으로 어떻게 동작하는가? Optimistic vs Pessimistic Locking의 trade-off를 분석하고, 높은 동시성 환경(예: 좌석 예약, 재고 차감)에서 어떤 전략이 적합한지 설명하라. `OptimisticLockException` 발생 시 retry 전략과, 분산 환경에서의 분산 락(Redis, DB advisory lock) 패턴을 비교하라.

---

**🧒 12살 비유:**
Optimistic Locking은 "게시판에 메모 붙이기"다. 내가 메모를 쓰는 동안 아무도 안 바꿨을 거라고 낙관적으로 생각한다. 붙이려는 순간 누군가 먼저 바꿨으면 "다시 읽고 다시 쓰세요"라고 한다. Pessimistic Locking은 "화장실 문 잠그기"다 — 내가 쓰는 동안 아무도 못 들어온다. 분산 락은 "여러 건물의 화장실 열쇠를 중앙 관리소(Redis)에서 빌리는 것"이다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
동시성 제어는 데이터 정합성의 핵심이다. 잘못된 전략은 데이터 유실(lost update), 데드락, 성능 저하를 유발한다. 특히 마이크로서비스에서의 분산 락은 Staff 레벨의 필수 역량이다.

**Step 2 — 핵심 기술 설명**

```kotlin
// Optimistic Locking: @Version 필드
@Entity
class Product(
    @Id val id: Long,
    var name: String,
    var stock: Int,
    @Version var version: Long = 0 // JPA가 자동 관리
)

// JPA가 생성하는 SQL:
// UPDATE product SET stock = ?, version = version + 1
// WHERE id = ? AND version = ?
//
// 영향받은 row = 0이면 → OptimisticLockException 발생
// → 다른 트랜잭션이 먼저 version을 증가시켰다는 뜻

// Pessimistic Locking
interface ProductRepository : JpaRepository<Product, Long> {
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT p FROM Product p WHERE p.id = :id")
    fun findByIdForUpdate(id: Long): Product?
    // → SELECT ... FOR UPDATE (DB 행 잠금)
}
```

Retry 전략:

```kotlin
// Spring Retry + Optimistic Locking
@Retryable(
    retryFor = [OptimisticLockingFailureException::class],
    maxAttempts = 3,
    backoff = Backoff(delay = 100, multiplier = 2.0, random = true)
)
@Transactional
fun decreaseStock(productId: Long, quantity: Int): Product {
    val product = productRepository.findById(productId)
        ?: throw NotFoundException("Product not found")

    require(product.stock >= quantity) { "Insufficient stock" }
    product.stock -= quantity

    return productRepository.save(product)
    // OptimisticLockException 발생 시 자동 재시도
}

// 코루틴 기반 수동 retry
suspend fun decreaseStockWithRetry(productId: Long, quantity: Int): Product {
    repeat(3) { attempt ->
        try {
            return withContext(Dispatchers.IO) {
                transactionTemplate.execute {
                    val product = productRepository.findById(productId).orElseThrow()
                    require(product.stock >= quantity) { "Insufficient stock" }
                    product.stock -= quantity
                    productRepository.save(product)
                }!!
            }
        } catch (e: OptimisticLockingFailureException) {
            if (attempt == 2) throw e
            delay((100L * (attempt + 1)) + Random.nextLong(50)) // jitter
        }
    }
    throw IllegalStateException("Unreachable")
}
```

분산 락 비교:

```kotlin
// Redis 분산 락 (Redisson)
@Service
class DistributedStockService(
    private val redissonClient: RedissonClient,
    private val productRepository: ProductRepository
) {
    @Transactional
    fun decreaseStockDistributed(productId: Long, quantity: Int): Product {
        val lock = redissonClient.getLock("stock:$productId")
        val acquired = lock.tryLock(5, 10, TimeUnit.SECONDS) // 5초 대기, 10초 TTL

        if (!acquired) throw ConcurrentModificationException("Cannot acquire lock")

        try {
            val product = productRepository.findById(productId).orElseThrow()
            require(product.stock >= quantity) { "Insufficient stock" }
            product.stock -= quantity
            return productRepository.save(product)
        } finally {
            if (lock.isHeldByCurrentThread) {
                lock.unlock()
            }
        }
    }
}

// DB Advisory Lock (PostgreSQL)
@Repository
class AdvisoryLockRepository(private val jdbcTemplate: JdbcTemplate) {
    fun tryAdvisoryLock(lockId: Long): Boolean {
        return jdbcTemplate.queryForObject(
            "SELECT pg_try_advisory_xact_lock(?)", Boolean::class.java, lockId
        ) ?: false
        // 트랜잭션 종료 시 자동 해제
    }
}
```

**Step 3 — 다양한 관점**

| 전략 | 경합 낮을 때 | 경합 높을 때 | 데드락 위험 | 확장성 |
|------|------------|------------|-----------|--------|
| Optimistic | 최고 성능 | retry 폭증 | 없음 | 높음 |
| Pessimistic | 불필요한 락 | 안정적 | 있음 | 중간 |
| Redis 분산 락 | 오버헤드 | 안정적 | 없음 (TTL) | 높음 |
| DB Advisory Lock | 중간 | 안정적 | 없음 (xact) | DB 의존 |
| Atomic SQL | 최고 성능 | 최고 성능 | 없음 | 최고 |

```kotlin
// Atomic SQL: 가장 효율적인 재고 차감
@Modifying
@Query("UPDATE Product p SET p.stock = p.stock - :quantity WHERE p.id = :id AND p.stock >= :quantity")
fun decreaseStock(id: Long, quantity: Int): Int
// 반환값 = 0이면 재고 부족, 1이면 성공
// version 불필요, 단일 SQL로 원자적 처리
```

**Step 4 — 구체적 예시**

```kotlin
// 프로덕션: 좌석 예약 시스템 — Pessimistic Lock + 타임아웃
@Service
class SeatReservationService(
    private val seatRepository: SeatRepository,
    private val reservationRepository: ReservationRepository
) {
    @Transactional(timeout = 5) // 5초 초과 시 롤백
    fun reserveSeats(eventId: Long, seatIds: List<Long>, userId: String): Reservation {
        // 정렬하여 데드락 방지 (항상 같은 순서로 락 획득)
        val sortedIds = seatIds.sorted()

        val seats = seatRepository.findByIdsForUpdate(sortedIds) // FOR UPDATE
        val unavailable = seats.filter { it.status != SeatStatus.AVAILABLE }
        if (unavailable.isNotEmpty()) {
            throw SeatUnavailableException(unavailable.map { it.id })
        }

        seats.forEach { it.status = SeatStatus.RESERVED }
        seatRepository.saveAll(seats)

        return reservationRepository.save(
            Reservation(eventId = eventId, seatIds = sortedIds, userId = userId)
        )
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| Optimistic + Retry | 단순, 높은 처리량 | 경합 높으면 비효율 | 일반 CRUD, 낮은 경합 |
| Pessimistic (SELECT FOR UPDATE) | 데이터 일관성 보장 | 데드락, 성능 저하 | 높은 경합, 짧은 트랜잭션 |
| Redis 분산 락 | 다중 서비스 지원 | Redis 의존, 네트워크 오버헤드 | MSA 환경 |
| Atomic SQL | 최고 성능 | 단순 연산만 가능 | 카운터, 재고 차감 |
| MVCC (PostgreSQL) | 읽기 차단 없음 | 쓰기 경합 시 serialization 에러 | 읽기 위주 |

**Step 6 — 성장 & 심화 학습**
- Redisson의 RedLock 알고리즘과 Martin Kleppmann의 비판
- PostgreSQL의 `SKIP LOCKED`를 활용한 작업 큐 패턴
- JPA의 `LockModeType.OPTIMISTIC_FORCE_INCREMENT`와 연관 엔티티 잠금
- 이벤트 소싱에서의 동시성 제어 (event stream version)

**🎯 면접관 평가 기준:**
- **L6 PASS**: Optimistic/Pessimistic 차이, @Version 내부 SQL, retry 전략 구현
- **L7 EXCEED**: 데드락 방지(순서 정렬), Atomic SQL 패턴, 분산 락 비교, SKIP LOCKED 활용
- 🚩 **RED FLAG**: 동시성 문제를 synchronized로 해결, 분산 환경 고려 없음

---

### Q26: N+1 문제와 JPA/Hibernate 캐시 전략

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Data Access

**Question:**
JPA의 N+1 문제가 발생하는 근본 원인을 Hibernate의 Proxy 메커니즘으로 설명하라. `@EntityGraph`, `JOIN FETCH`, `@BatchSize`, `@Fetch(FetchMode.SUBSELECT)`의 내부 동작과 trade-off를 비교하라. Hibernate의 1차 캐시(Persistence Context)와 2차 캐시(L2 Cache)의 차이, 그리고 2차 캐시가 동시성 문제를 일으킬 수 있는 시나리오를 설명하라.

---

**🧒 12살 비유:**
N+1 문제는 "반 학생 30명의 성적표를 가져오는데, 먼저 학생 목록 1번 조회하고, 각 학생의 성적을 하나씩 30번 더 조회"하는 것이다. 총 31번 사무실에 다녀와야 한다. JOIN FETCH는 "학생 목록과 성적을 한 번에 가져오기"다. 1차 캐시는 "선생님의 단기 기억"이고, 2차 캐시는 "교무실의 공유 파일 캐비닛"이다 — 여러 선생님이 같은 캐비닛을 쓰니까 누군가 파일을 바꾸면 혼란이 올 수 있다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
N+1은 JPA에서 가장 흔하고 성능에 치명적인 문제다. Staff 레벨에서는 여러 해결책의 내부 동작과 상황별 적합성을 정확히 판단할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

```kotlin
// N+1 발생 근본 원인: Lazy Loading Proxy
@Entity
class Order(
    @Id val id: Long,
    @OneToMany(mappedBy = "order", fetch = FetchType.LAZY) // 기본값
    val items: MutableList<OrderItem> = mutableListOf()
)

// Hibernate는 items에 Proxy 컬렉션 삽입 (PersistentBag)
// items에 접근하는 순간 별도 SELECT 실행

val orders = orderRepository.findAll() // SELECT * FROM orders (1번)
orders.forEach { order ->
    println(order.items.size) // SELECT * FROM order_items WHERE order_id = ? (N번!)
}
// 총 N+1 쿼리

// 해결 1: JOIN FETCH (JPQL)
@Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.userId = :userId")
fun findWithItems(userId: String): List<Order>
// → 1개의 JOIN 쿼리로 해결
// ⚠️ 주의: Collection JOIN FETCH는 페이징과 함께 사용 불가!
// HHH90003004: "firstResult/maxResults specified with collection fetch"
// → 메모리에서 페이징 (전체 로드 후 잘라냄) → OOM 위험

// 해결 2: @EntityGraph (Spring Data JPA)
@EntityGraph(attributePaths = ["items", "items.product"])
fun findByUserId(userId: String): List<Order>
// → LEFT JOIN으로 변환
// JOIN FETCH와 유사하지만 더 선언적

// 해결 3: @BatchSize (Hibernate)
@OneToMany(mappedBy = "order")
@BatchSize(size = 100) // IN절로 100개씩 배치 로딩
val items: MutableList<OrderItem> = mutableListOf()
// SELECT * FROM order_items WHERE order_id IN (?, ?, ..., ?)
// N/100 + 1 쿼리로 감소

// 해결 4: @Fetch(SUBSELECT)
@OneToMany(mappedBy = "order")
@Fetch(FetchMode.SUBSELECT)
val items: MutableList<OrderItem> = mutableListOf()
// SELECT * FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE ...)
// 항상 2개 쿼리 (orders + items)
```

**Step 3 — 다양한 관점**

| 해결책 | 쿼리 수 | 페이징 호환 | 카티전 곱 | 사용 시점 |
|--------|---------|-----------|----------|-----------|
| JOIN FETCH | 1 | 불가 (Collection) | 있음 | 단일 조회, 적은 데이터 |
| @EntityGraph | 1 | 불가 (Collection) | 있음 | Spring Data JPA |
| @BatchSize | N/batch + 1 | 가능 | 없음 | 목록 조회 + 페이징 |
| @Fetch(SUBSELECT) | 2 | 가능 | 없음 | 전체 목록 로딩 |
| DTO Projection | 1 | 가능 | 없음 | 읽기 전용 |

카티전 곱(Cartesian Product) 문제:

```kotlin
// 여러 Collection을 JOIN FETCH하면:
@Query("SELECT o FROM Order o JOIN FETCH o.items JOIN FETCH o.payments")
fun findWithAll(): List<Order>
// items 3개 × payments 2개 = 6행 반환 (중복!)
// MultipleBagFetchException 발생 가능 (List + List)

// 해결: Set 사용 또는 별도 쿼리 분리
@OneToMany(mappedBy = "order")
val items: MutableSet<OrderItem> = mutableSetOf() // Set으로 변경
```

Hibernate 캐시 아키텍처:

```
┌─────────────────────────────────────────────────────────┐
│                   Application                            │
├─────────────────────────────────────────────────────────┤
│  Session (EntityManager)                                 │
│  ┌──────────────────────────────────────┐               │
│  │ 1차 캐시 (Persistence Context)        │               │
│  │ - 트랜잭션 범위                       │               │
│  │ - 엔티티 identity map                │               │
│  │ - 스레드 안전 (단일 스레드)           │               │
│  └──────────────────────────────────────┘               │
├─────────────────────────────────────────────────────────┤
│  SessionFactory (EntityManagerFactory)                    │
│  ┌──────────────────────────────────────┐               │
│  │ 2차 캐시 (L2 Cache)                   │               │
│  │ - SessionFactory 범위 (전역)          │               │
│  │ - 여러 트랜잭션이 공유               │               │
│  │ - 구현: Ehcache, Hazelcast, Redis     │               │
│  │ - 동시성 문제 가능!                   │               │
│  └──────────────────────────────────────┘               │
│  ┌──────────────────────────────────────┐               │
│  │ 쿼리 캐시                             │               │
│  │ - 쿼리 결과 ID 목록 캐싱              │               │
│  │ - 2차 캐시와 함께 사용해야 효과적     │               │
│  └──────────────────────────────────────┘               │
├─────────────────────────────────────────────────────────┤
│                    Database                               │
└─────────────────────────────────────────────────────────┘
```

2차 캐시 동시성 문제:

```kotlin
// 시나리오: READ_WRITE 전략
// Thread A: Product(id=1, stock=10)을 캐시에서 읽음
// Thread B: Product(id=1)의 stock을 8로 업데이트 → 캐시 무효화
// Thread A: 이전 캐시 값(stock=10)으로 비즈니스 로직 실행 → 정합성 깨짐!

// 캐시 동시성 전략:
@Entity
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
// READ_ONLY: 불변 데이터만, 변경 시 예외
// NONSTRICT_READ_WRITE: eventual consistency (짧은 불일치 허용)
// READ_WRITE: soft lock 사용 (일관성 높지만 성능 낮음)
// TRANSACTIONAL: JTA 필요 (XA 트랜잭션)
class Product(
    @Id val id: Long,
    @NaturalId val sku: String,
    var stock: Int,
    @Version var version: Long = 0
)
```

**Step 4 — 구체적 예시**

```kotlin
// 프로덕션: DTO Projection으로 N+1 완전 회피
interface OrderSummary {
    val orderId: Long
    val status: OrderStatus
    val itemCount: Long
    val totalAmount: BigDecimal
}

@Query("""
    SELECT o.id as orderId, o.status as status,
           COUNT(i) as itemCount, SUM(i.price * i.quantity) as totalAmount
    FROM Order o LEFT JOIN o.items i
    WHERE o.userId = :userId
    GROUP BY o.id, o.status
""")
fun findOrderSummaries(userId: String, pageable: Pageable): Page<OrderSummary>
// 장점: 1개 쿼리, 페이징 가능, 필요한 컬럼만 조회
// 단점: 엔티티가 아니므로 수정 불가

// 프로덕션: 2차 캐시 + 쿼리 캐시 설정
@Configuration
class CacheConfig {
    @Bean
    fun hibernateProperties(): HibernatePropertiesCustomizer {
        return HibernatePropertiesCustomizer { props ->
            props["hibernate.cache.use_second_level_cache"] = "true"
            props["hibernate.cache.use_query_cache"] = "true"
            props["hibernate.cache.region.factory_class"] =
                "org.hibernate.cache.jcache.JCacheRegionFactory"
            props["hibernate.javax.cache.provider"] =
                "org.ehcache.jsr107.EhcacheCachingProvider"
        }
    }
}

// 캐시 적합한 엔티티: 자주 읽히고 거의 변경되지 않는 것
@Entity
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
class Category(
    @Id val id: Long,
    val name: String,
    val description: String
    // 거의 변경 안 됨 → 2차 캐시 적합
)

// 캐시 부적합: 자주 변경되는 것 (Product.stock 등)
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| JOIN FETCH | 1쿼리, 단순 | 페이징 불가, 카티전 곱 | 단일 조회 |
| @BatchSize | 페이징 호환, 점진적 로딩 | 완벽한 1쿼리는 아님 | 목록 + 페이징 |
| DTO Projection | 최고 성능, 필요한 것만 | 수정 불가, 쿼리 작성 필요 | 읽기 전용 |
| 2차 캐시 | 반복 조회 최적화 | 동시성 복잡, 메모리 사용 | 읽기 위주 참조 데이터 |
| CQRS | 읽기/쓰기 분리 최적화 | 아키텍처 복잡도 | 읽기/쓰기 패턴이 극단적으로 다를 때 |

**Step 6 — 성장 & 심화 학습**
- Hibernate 6의 `@Fetch` 전략 변경사항
- Spring Data JPA의 `@QueryHints`로 쿼리 캐시 활성화
- Hibernate Statistics(`hibernate.generate_statistics=true`)로 캐시 히트율 모니터링
- jOOQ + JPA 혼용 전략: 복잡한 읽기는 jOOQ, 쓰기는 JPA

**🎯 면접관 평가 기준:**
- **L6 PASS**: N+1 원인과 3개 이상 해결책, JOIN FETCH의 페이징 제한, 1차 vs 2차 캐시 차이
- **L7 EXCEED**: 카티전 곱 문제와 해결, 2차 캐시 동시성 전략, DTO Projection 패턴, CQRS 연결
- 🚩 **RED FLAG**: FetchType.EAGER로 N+1 해결 시도, 2차 캐시를 무조건 적용

---

## 마무리

> 이 문서의 26개 질문은 FAANG L6/L7 레벨에서 Kotlin/Spring 기술 역량을 평가하기 위해 설계되었습니다.
> 각 질문은 단순 지식 확인이 아닌, **프로덕션 경험 기반의 설계 판단력**을 평가합니다.
>
> **학습 우선순위:**
> 1. Coroutines + Flow (가장 차별화되는 Kotlin 역량)
> 2. JVM Internals (시니어 엔지니어의 깊이)
> 3. Spring DI & Transaction (Spring 핵심 이해도)
> 4. Data Access (실무 성능 문제 해결)
> 5. 나머지 (WebFlux, Security, Testing, Operational)
