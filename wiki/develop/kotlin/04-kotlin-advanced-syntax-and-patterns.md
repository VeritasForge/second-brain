---
created: 2026-04-21
source: claude-code
tags: [kotlin, advanced, coroutines, spring-di, aop, generics, dsl, flow, scope-functions]
---

# 📖 Kotlin 고급 문법과 패턴 — 코루틴부터 Spring 통합까지

> 💡 **한줄 요약**: Kotlin의 고급 문법은 코루틴(structured concurrency) + Spring DI/AOP + 제네릭(variance) + DSL 빌더를 조합하여 프로덕션 수준의 엔터프라이즈 백엔드를 구현할 수 있게 하며, scope function과 delegation으로 관용적 Kotlin 코드를 작성한다.
>
> 📌 **핵심 키워드**: structured concurrency, Flow, Spring DI, AOP, variance (in/out), DSL, scope function
> 📅 **기준**: Kotlin 2.1+ / Spring Boot 3.x (2025)

---

## 1️⃣ 코루틴과 Structured Concurrency

### 기본 패턴

```kotlin
// launch: 결과 없는 비동기 작업
val job = scope.launch {
    val user = fetchUser(id)  // suspend fun — 여기서 중단 가능
    updateUI(user)
}

// async: 결과 있는 비동기 작업
val deferred = scope.async {
    fetchUser(id)
}
val user: User = deferred.await()

// 병렬 실행
coroutineScope {
    val user = async { fetchUser(id) }
    val orders = async { fetchOrders(id) }
    process(user.await(), orders.await())
}
```

### Structured Concurrency 원칙

```
coroutineScope {              ← 부모
    launch { task1() }        ← 자식 1
    launch { task2() }        ← 자식 2
}
// 자식이 모두 완료되어야 부모 완료
// 자식 중 하나가 실패하면 나머지 자동 취소
// 부모가 취소되면 모든 자식 취소
```

### Flow (리액티브 스트림)

```kotlin
fun userUpdates(): Flow<User> = flow {
    while (true) {
        emit(fetchLatestUser())
        delay(1000)
    }
}

// 수집
userUpdates()
    .filter { it.isActive }
    .map { it.name }
    .collect { name -> println(name) }
```

> 📌 코루틴 면접 심화: [[kotlin-spring]] Q1-Q6 (코루틴 deep dive)
> 📌 코루틴 비교: [[coroutine-gmp-vthread]]

### 🔄 4개 언어 비교

| 개념 | Kotlin | Go | Python | JS/TS |
|------|--------|-----|--------|-------|
| 비동기 함수 | `suspend fun` | `go func()` | `async def` | `async function` |
| 스트림 | `Flow` | channel | `AsyncIterator` | `AsyncGenerator` |
| 구조화된 동시성 | `coroutineScope` | 없음 (패턴으로) | `TaskGroup` (3.11+) | 없음 |
| 취소 전파 | 자동 (부모→자식) | context.Cancel | 자동 (TaskGroup) | AbortController |

---

## 2️⃣ Spring DI와 IoC

> 📌 DI 상세: [[spring-di-bean-test-deep-dive]], [[spring-di-deep-dive-followup-q1-q11]]
> (아래는 Kotlin 관점의 핵심 요약 — 기존 문서와 중복 없음)

### Kotlin에서의 생성자 주입

```kotlin
@Service
class UserService(
    private val userRepository: UserRepository,  // 생성자 주입 (Kotlin 기본)
    private val eventPublisher: EventPublisher,
) {
    fun getUser(id: Long): User =
        userRepository.findByIdOrNull(id)
            ?: throw UserNotFoundException(id)
}
```

> Kotlin은 **생성자 주입이 기본** — Java의 `@Autowired` 불필요. `val` 파라미터가 자동으로 final 필드 + 주입.

### @ConfigurationProperties with Data Class

```kotlin
@ConfigurationProperties(prefix = "app.cache")
data class CacheProperties(
    val ttl: Duration = Duration.ofMinutes(5),
    val maxSize: Int = 1000,
    val enabled: Boolean = true,
)
```

---

## 3️⃣ Spring AOP와 Transaction

> 📌 AOP 상세: [[spring-aop-complete-guide]]

### @Transactional 핵심 주의점

```kotlin
@Service
class OrderService(private val repo: OrderRepository) {
    
    @Transactional
    fun createOrder(request: CreateOrderRequest): Order {
        val order = Order.from(request)
        return repo.save(order)
    }
    
    // ⚠️ SELF-INVOCATION 함정!
    fun processAndCreate(request: CreateOrderRequest): Order {
        // 같은 클래스 내 호출 → 프록시를 거치지 않음 → @Transactional 무시!
        return createOrder(request)  // 트랜잭션이 적용되지 않음
    }
}
```

**해결**: 별도 서비스로 분리하거나 `TransactionTemplate` 직접 사용.

---

## 4️⃣ 제네릭 고급 (Variance)

### in / out (공변/반공변)

```kotlin
// out (공변) — Producer: T를 반환만
interface Source<out T> {
    fun next(): T
}
// Source<Dog>를 Source<Animal>로 사용 가능 (Dog은 Animal의 서브타입)

// in (반공변) — Consumer: T를 소비만
interface Sink<in T> {
    fun put(item: T)
}
// Sink<Animal>을 Sink<Dog>로 사용 가능

// Star projection
fun printAll(list: List<*>) {
    list.forEach { println(it) }
}
```

### Reified Type Parameters

```kotlin
// inline + reified: 런타임에 타입 정보 유지
inline fun <reified T> isType(value: Any): Boolean = value is T

isType<String>("hello")  // true — 런타임에 T가 String임을 알 수 있음
```

> Java의 Type Erasure를 `inline + reified`로 극복. Go의 GCShape stenciling과 다른 접근.

### 🔄 4개 언어 비교

| 개념 | Kotlin | Go | Python | JS/TS |
|------|--------|-----|--------|-------|
| Variance | `in/out` (선언 사이트) | 없음 | `TypeVar(covariant=True)` | 없음 (구조적) |
| 런타임 타입 | `reified` (inline만) | GCShape + dictionary | 런타임 타입 항상 존재 | 타입 제거 (TS) |
| 제네릭 제약 | `<T : Comparable<T>>` | `[T comparable]` | `TypeVar(bound=...)` | `<T extends ...>` |

---

## 5️⃣ DSL과 Operator Overloading

### Type-Safe Builder (DSL)

```kotlin
// HTML DSL 예제
fun html(init: HTML.() -> Unit): HTML {
    val html = HTML()
    html.init()
    return html
}

val page = html {
    head {
        title { +"My Page" }
    }
    body {
        h1 { +"Hello, Kotlin DSL!" }
        p { +"This is type-safe" }
    }
}
```

### Kotlin 실무 DSL 예제들

```kotlin
// Ktor routing DSL
routing {
    get("/users/{id}") {
        val id = call.parameters["id"]?.toLong()
        call.respond(userService.getUser(id!!))
    }
}

// Exposed SQL DSL
Users.select { Users.age greaterEq 18 }
    .orderBy(Users.name)
    .limit(10)

// Gradle Kotlin DSL
dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
}
```

### @DslMarker

```kotlin
@DslMarker
annotation class HtmlDsl

@HtmlDsl
class HTML { ... }

// @DslMarker가 있으면 중첩 수신자의 암묵적 호출을 방지
// → DSL 스코프 혼동 방지
```

---

## 6️⃣ Scope Functions과 관용구

### let / run / with / apply / also

```kotlin
// let: null 체크 + 변환
user?.let { nonNullUser ->
    println(nonNullUser.name)
}

// apply: 객체 초기화 (builder 대체)
val user = User().apply {
    name = "Go"
    age = 15
    tags = mutableListOf("dev")
}

// also: 부수 효과 (로깅 등)
val result = fetchData()
    .also { logger.info("Fetched: $it") }
    .process()

// run: 객체의 메서드 호출 + 결과 반환
val length = "hello".run { length }

// with: 여러 메서드 호출
with(config) {
    host = "localhost"
    port = 8080
    ssl = false
}
```

### 선택 가이드

| 함수 | `this` 접근 | 반환값 | 주 용도 |
|------|-----------|--------|---------|
| `let` | `it` | 람다 결과 | null 체크, 변환 |
| `run` | `this` | 람다 결과 | 설정 + 결과 계산 |
| `with` | `this` | 람다 결과 | 여러 메서드 호출 |
| `apply` | `this` | 수신 객체 | 객체 초기화 |
| `also` | `it` | 수신 객체 | 부수 효과 (로깅) |

---

## 7️⃣ Delegation 패턴

### Property Delegation

```kotlin
// lazy: 첫 접근 시 초기화
val heavyObject: HeavyThing by lazy {
    loadHeavyThing()  // 최초 1회만 실행
}

// observable: 변경 감지
var name: String by Delegates.observable("") { _, old, new ->
    println("$old → $new")
}

// Map delegation: JSON 파싱 등에 유용
class Config(map: Map<String, Any?>) {
    val host: String by map
    val port: Int by map
}
```

---

## 8️⃣ Kotlin-Spring 통합 패턴

### 코루틴 + Spring WebFlux

```kotlin
@RestController
class UserController(private val userService: UserService) {
    
    @GetMapping("/users/{id}")
    suspend fun getUser(@PathVariable id: Long): User =
        userService.getUser(id)  // suspend fun — 코루틴으로 비동기 처리
    
    @GetMapping("/users")
    fun getUsers(): Flow<User> =  // Flow 반환 — 스트리밍
        userService.getAllUsers()
}

@Service
class UserService(private val repo: UserRepository) {
    suspend fun getUser(id: Long): User =
        repo.findById(id) ?: throw UserNotFoundException(id)
    
    fun getAllUsers(): Flow<User> = repo.findAll()  // R2DBC Flow
}
```

### Spring + Kotlin 확장 함수

```kotlin
// Spring이 제공하는 Kotlin 확장
val user = repo.findByIdOrNull(id)  // findById().orElse(null)의 Kotlin 버전

// WebClient + 코루틴
val response = webClient.get()
    .uri("/api/users/$id")
    .retrieve()
    .awaitBody<User>()  // suspend 확장 함수
```

---

## 📎 출처

1. [Kotlin Coroutines Guide (공식)](https://kotlinlang.org/docs/coroutines-guide.html) — 코루틴 가이드
2. [Kotlin Generics (공식)](https://kotlinlang.org/docs/generics.html) — 제네릭 variance
3. [Type-Safe Builders (공식)](https://kotlinlang.org/docs/type-safe-builders.html) — DSL 빌더
4. [Spring Framework Kotlin Support](https://docs.spring.io/spring-framework/reference/languages/kotlin.html) — Spring + Kotlin

---

> 📌 **이전 문서**: [[03-kotlin-basic-syntax]]
> 📌 **다음 문서**: [[05-kotlin-developer-essentials-by-seniority]]
> 📌 **상세 문서**: [[spring-aop-complete-guide]], [[spring-di-bean-test-deep-dive]], [[spring-di-deep-dive-followup-q1-q11]], [[coroutine-gmp-vthread]]
