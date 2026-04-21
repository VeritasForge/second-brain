---
created: 2026-04-21
source: claude-code
tags: [kotlin, syntax, basics, null-safety, data-class, sealed-class, when, extension-function]
---

# 📖 Kotlin 기본 문법 — Null Safety부터 Sealed Class까지

> 💡 **한줄 요약**: Kotlin의 기본 문법은 null safety(`?`), data class, sealed class, extension function 등 Java의 보일러플레이트를 제거하면서도 정적 타입의 안전성을 유지하는 구조로 설계되어 있다.
>
> 📌 **핵심 키워드**: val/var, nullable `?`, data class, sealed class, when, extension function
> 📅 **기준**: Kotlin 2.1+ (2025)

---

## 1️⃣ 패키지와 빌드 시스템

### Gradle Kotlin DSL

```kotlin
// build.gradle.kts
plugins {
    kotlin("jvm") version "2.1.0"
    kotlin("plugin.spring") version "2.1.0"
    id("org.springframework.boot") version "3.3.0"
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0")
    testImplementation("io.mockk:mockk:1.13.12")
}
```

### 🔄 4개 언어 비교

| 개념 | Kotlin | Go | Python | JS/TS |
|------|--------|-----|--------|-------|
| 빌드 도구 | Gradle KTS | `go build` | uv/pip | npm/pnpm |
| 의존성 파일 | `build.gradle.kts` | `go.mod` | `pyproject.toml` | `package.json` |
| 가시성 | `public/private/internal/protected` | 대문자/소문자 | `_` 관습 | `export` |

---

## 2️⃣ 변수, 타입, Null Safety

### val / var

```kotlin
val name: String = "Kotlin"  // 불변 (Java final)
var age: Int = 10            // 가변
val inferred = "타입 추론"    // String으로 추론
```

### Null Safety 체계

```kotlin
// Non-null vs Nullable
var safe: String = "hello"    // null 할당 불가
var nullable: String? = null  // null 가능

// Safe call (?.)
val length: Int? = nullable?.length  // null이면 null 반환

// Elvis operator (?:)
val len: Int = nullable?.length ?: 0  // null이면 기본값

// Not-null assertion (!!)
val len2: Int = nullable!!.length  // null이면 NPE — 최후 수단

// Smart cast
if (nullable != null) {
    println(nullable.length)  // 자동으로 String으로 캐스트됨
}

// let 스코프 함수
nullable?.let { nonNull ->
    println(nonNull.length)  // 이 블록에서는 non-null 보장
}
```

### 기본 타입

| 타입 | 크기 | Go 대응 | 특이사항 |
|------|------|--------|---------|
| `Int` | 32bit | `int32` | Java int와 동일 |
| `Long` | 64bit | `int64` | `L` 접미사: `42L` |
| `Double` | 64bit | `float64` | 기본 소수점 타입 |
| `Boolean` | - | `bool` | `true`/`false` |
| `String` | - | `string` | 불변, 문자열 템플릿 `$name` |
| `Char` | 16bit | `rune` | UTF-16 |
| `Any` | - | `any` | 모든 타입의 루트 |
| `Nothing` | - | 없음 | 반환하지 않는 함수의 반환 타입 |
| `Unit` | - | 없음 (void) | `void` 대체 |

---

## 3️⃣ 제어 흐름

### when (= switch의 상위 버전)

```kotlin
// 기본
when (status) {
    "active" -> process()
    "inactive", "paused" -> skip()
    else -> error("Unknown: $status")
}

// 표현식으로 사용
val message = when {
    score >= 90 -> "A"
    score >= 80 -> "B"
    else -> "C"
}

// 타입 검사 + smart cast
when (obj) {
    is String -> println(obj.length)  // smart cast
    is Int -> println(obj + 1)
    is List<*> -> println(obj.size)
}

// Guard conditions (Kotlin 2.1+)
when (user) {
    is Admin if user.isSuperAdmin -> fullAccess()
    is Admin -> limitedAdminAccess()
    is Member -> memberAccess()
}
```

### for / while

```kotlin
for (i in 1..10) { }          // 1~10 (inclusive)
for (i in 0 until 10) { }     // 0~9
for (i in 10 downTo 0 step 2) { }  // 10, 8, 6, 4, 2, 0
for ((index, value) in list.withIndex()) { }  // 인덱스 + 값

while (condition) { }
do { } while (condition)
```

### Destructuring

```kotlin
val (name, age) = User("Go", 15)  // data class의 componentN()
val (key, value) = mapEntry
```

### 🔄 4개 언어 비교

| 개념 | Kotlin | Go | Python | JS/TS |
|------|--------|-----|--------|-------|
| 패턴 매칭 | `when` (완전성 검사 with sealed) | `switch` | `match/case` | `switch` |
| 범위 | `1..10`, `until`, `downTo` | `for i := 0; i < 10` | `range(10)` | `for (let i=0; i<10)` |
| 구조 분해 | `val (a, b) = pair` | 없음 | `a, b = tuple` | `const {a, b} = obj` |

---

## 4️⃣ 함수

### 기본 함수 + 기본값 + Named Arguments

```kotlin
fun greet(name: String, greeting: String = "Hello"): String {
    return "$greeting, $name!"
}

greet("Go")                    // "Hello, Go!"
greet("Go", greeting = "Hi")  // "Hi, Go!" — named argument
```

### Extension Function

```kotlin
fun String.isPalindrome(): Boolean = this == this.reversed()

"racecar".isPalindrome()  // true
```

### Higher-Order Function

```kotlin
fun <T> List<T>.customFilter(predicate: (T) -> Boolean): List<T> {
    return filter(predicate)
}

val adults = users.customFilter { it.age >= 18 }
```

### infix / tailrec

```kotlin
infix fun Int.power(exp: Int): Long = // ...
val result = 2 power 10  // 중위 표기법

tailrec fun factorial(n: Int, acc: Long = 1): Long =
    if (n <= 1) acc else factorial(n - 1, n * acc)  // 꼬리 재귀 최적화
```

---

## 5️⃣ 데이터 구조

### Collections

```kotlin
// 불변 (기본)
val list: List<Int> = listOf(1, 2, 3)
val map: Map<String, Int> = mapOf("a" to 1, "b" to 2)
val set: Set<String> = setOf("a", "b")

// 가변
val mutableList: MutableList<Int> = mutableListOf(1, 2, 3)
mutableList.add(4)

// 함수형 연산 체이닝
val result = users
    .filter { it.age >= 18 }
    .sortedBy { it.name }
    .map { it.name.uppercase() }
    .take(10)
```

### Sequence (지연 평가)

```kotlin
// Sequence: 중간 컬렉션 생성 없이 파이프라인 처리
val result = users.asSequence()
    .filter { it.age >= 18 }  // 하나씩 처리
    .map { it.name }
    .take(10)
    .toList()  // 최종 연산에서 실체화
```

### 🔄 4개 언어 비교

| 개념 | Kotlin | Go | Python | JS/TS |
|------|--------|-----|--------|-------|
| 불변 리스트 | `listOf()` (기본) | 없음 (slice는 가변) | `tuple` | `Object.freeze()` |
| 지연 평가 | `Sequence` | 없음 | generator | 없음 (라이브러리) |
| 함수형 체이닝 | `.filter{}.map{}` | for 루프 | comprehension / map | `.filter().map()` |

---

## 6️⃣ 클래스와 OOP

### Data Class

```kotlin
data class User(val name: String, val age: Int)
// 자동 생성: equals, hashCode, toString, copy, componentN

val user = User("Go", 15)
val older = user.copy(age = 16)  // 불변 복사
```

### Sealed Class / Interface

```kotlin
sealed interface Result<out T> {
    data class Success<T>(val data: T) : Result<T>
    data class Error(val message: String) : Result<Nothing>
    data object Loading : Result<Nothing>
}

// when에서 완전성 검사 → else 불필요
fun handle(result: Result<User>) = when (result) {
    is Result.Success -> showUser(result.data)
    is Result.Error -> showError(result.message)
    is Result.Loading -> showSpinner()
    // else 필요 없음 — 컴파일러가 모든 경우를 확인
}
```

### Object / Companion Object

```kotlin
// Singleton
object DatabaseConfig {
    val url = "jdbc:postgresql://..."
}

// Companion (static 대체)
class User(val name: String) {
    companion object {
        fun create(name: String) = User(name)
    }
}
val user = User.create("Go")
```

### Delegation (`by`)

```kotlin
interface Printer {
    fun print(msg: String)
}

class ConsolePrinter : Printer {
    override fun print(msg: String) = println(msg)
}

// 위임: Printer 구현을 ConsolePrinter에 위임
class LoggingPrinter(printer: Printer) : Printer by printer
```

---

## 7️⃣ 인터페이스와 제네릭 기초

### Interface with Default Methods

```kotlin
interface Cacheable {
    val cacheKey: String
    fun cacheExpiry(): Duration = Duration.ofMinutes(5)  // 기본 구현
}
```

### Basic Generics

```kotlin
class Stack<T> {
    private val items = mutableListOf<T>()
    fun push(item: T) { items.add(item) }
    fun pop(): T = items.removeLast()
}

// Type bound
fun <T : Comparable<T>> max(a: T, b: T): T = if (a > b) a else b
```

---

## 8️⃣ 에러 처리

### try/catch (기본)

```kotlin
try {
    val result = riskyOperation()
} catch (e: IOException) {
    logger.error("IO error", e)
} finally {
    cleanup()
}
```

### Result + runCatching

```kotlin
val result: Result<User> = runCatching { fetchUser(id) }

result
    .onSuccess { user -> process(user) }
    .onFailure { error -> log(error) }

val user: User = result.getOrElse { defaultUser }
val user2: User? = result.getOrNull()
```

### require / check

```kotlin
fun createUser(name: String, age: Int): User {
    require(name.isNotBlank()) { "이름은 비어있을 수 없습니다" }  // IllegalArgumentException
    check(age >= 0) { "나이는 0 이상이어야 합니다" }              // IllegalStateException
    return User(name, age)
}
```

### 🔄 4개 언어 비교

| 개념 | Kotlin | Go | Python | JS/TS |
|------|--------|-----|--------|-------|
| 에러 모델 | 예외 + Result | 값 (T, error) | 예외 | 예외 |
| Checked 예외 | ❌ 없음 | N/A | ❌ 없음 | ❌ 없음 |
| 안전한 래퍼 | `runCatching` | 없음 (패턴으로) | 없음 | 없음 |
| 전제 조건 | `require`/`check` | 없음 | `assert` | `console.assert` |

---

## 📎 출처

1. [Kotlin Language Reference](https://kotlinlang.org/docs/reference/) — 공식 문법 레퍼런스
2. [Kotlin Coding Conventions](https://kotlinlang.org/docs/coding-conventions.html) — 코딩 컨벤션
3. [Kotlin Sealed Classes](https://kotlinlang.org/docs/sealed-classes.html) — Sealed 클래스 가이드

---

> 📌 **이전 문서**: [[02-kotlin-architecture-and-runtime]]
> 📌 **다음 문서**: [[04-kotlin-advanced-syntax-and-patterns]]
