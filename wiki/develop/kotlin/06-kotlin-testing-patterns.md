---
created: 2026-04-21
source: claude-code
tags: [kotlin, testing, junit5, mockk, spring-test, coroutine-testing, testcontainers]
---

# 📖 Kotlin 테스팅 패턴 — MockK부터 Spring Test Slice까지

> 💡 **한줄 요약**: Kotlin 테스팅은 JUnit 5 + MockK(Kotlin-native mock) + Spring Test Slice + Testcontainers를 조합하며, 코루틴 테스트는 `runTest` + `TestDispatcher`로 시간을 제어한다.
>
> 📌 **핵심 키워드**: JUnit 5, MockK, @WebMvcTest, @DataJpaTest, runTest, TestDispatcher
> 📅 **기준**: Kotlin 2.1+ / Spring Boot 3.x (2025)

---

## 1️⃣ JUnit 5 + Kotlin 관용구

### Parameterized Test (테이블 드리븐)

```kotlin
@ParameterizedTest
@CsvSource("2,3,5", "-1,3,2", "0,0,0")
fun `add should return correct sum`(a: Int, b: Int, expected: Int) {
    assertThat(add(a, b)).isEqualTo(expected)
}
```

### @Nested (구조화)

```kotlin
@DisplayName("UserService")
class UserServiceTest {
    
    @Nested
    @DisplayName("getUser")
    inner class GetUser {
        @Test
        fun `존재하는 사용자를 반환한다`() { ... }
        
        @Test
        fun `존재하지 않으면 예외를 던진다`() { ... }
    }
}
```

---

## 2️⃣ MockK

```kotlin
@Test
fun `getUser should return user from repository`() {
    val repo = mockk<UserRepository>()
    val user = User("Go", 15)
    
    every { repo.findByIdOrNull(1L) } returns user
    
    val svc = UserService(repo)
    val result = svc.getUser(1L)
    
    assertThat(result).isEqualTo(user)
    verify(exactly = 1) { repo.findByIdOrNull(1L) }
}

// 코루틴 모킹
@Test
fun `fetchUser should call suspend repository`() = runTest {
    val repo = mockk<UserRepository>()
    coEvery { repo.findById(1L) } returns user  // coEvery: suspend fun 모킹
    
    val result = svc.getUser(1L)
    coVerify { repo.findById(1L) }  // coVerify: suspend fun 검증
}
```

> 📌 Spring + MockK 테스트 상세: [[spring-di-bean-test-deep-dive]]

---

## 3️⃣ Spring Test Slices

| 어노테이션 | 로드 범위 | 용도 |
|-----------|---------|------|
| `@WebMvcTest` | Controller + MVC 설정만 | API 테스트 |
| `@DataJpaTest` | JPA + Repository만 | DB 테스트 |
| `@SpringBootTest` | 전체 컨텍스트 | 통합 테스트 |
| `@WebFluxTest` | WebFlux Controller | 리액티브 API 테스트 |

```kotlin
@WebMvcTest(UserController::class)
class UserControllerTest(
    @Autowired private val mockMvc: MockMvc,
) {
    @MockkBean
    private lateinit var userService: UserService
    
    @Test
    fun `GET users_id returns user`() {
        every { userService.getUser(1L) } returns User("Go", 15)
        
        mockMvc.get("/users/1")
            .andExpect { status { isOk() } }
            .andExpect { jsonPath("$.name") { value("Go") } }
    }
}
```

---

## 4️⃣ Testcontainers

```kotlin
@SpringBootTest
@Testcontainers
class UserRepositoryIntegrationTest {
    
    companion object {
        @Container
        val postgres = PostgreSQLContainer("postgres:16-alpine")
            .withDatabaseName("testdb")
        
        @DynamicPropertySource
        @JvmStatic
        fun properties(registry: DynamicPropertyRegistry) {
            registry.add("spring.datasource.url", postgres::getJdbcUrl)
            registry.add("spring.datasource.username", postgres::getUsername)
            registry.add("spring.datasource.password", postgres::getPassword)
        }
    }
    
    @Autowired
    private lateinit var repo: UserRepository
    
    @Test
    fun `should save and find user`() {
        val user = repo.save(User("Go", 15))
        val found = repo.findByIdOrNull(user.id!!)
        assertThat(found?.name).isEqualTo("Go")
    }
}
```

---

## 5️⃣ 코루틴 테스트

```kotlin
@Test
fun `fetchUser should timeout after 3 seconds`() = runTest {
    val svc = UserService(slowRepository)
    
    assertThrows<TimeoutCancellationException> {
        withTimeout(3000) {
            svc.fetchUser(1L)
        }
    }
}

@Test
fun `flow should emit 3 users`() = runTest {
    val flow = userService.getUsers()
    
    val users = flow.toList()
    assertThat(users).hasSize(3)
}

@Test
fun `delayed operation completes instantly in test`() = runTest {
    // runTest는 가상 시간 사용 — delay(1000)이 즉시 완료
    val result = async {
        delay(1000)  // 실제로 1초 대기하지 않음
        "done"
    }
    advanceTimeBy(1000)
    assertThat(result.await()).isEqualTo("done")
}
```

---

## 6️⃣ 테스트 조직

```
src/test/kotlin/com/myapp/
├── unit/
│   ├── service/
│   │   └── UserServiceTest.kt
│   └── domain/
│       └── UserTest.kt
├── integration/
│   ├── repository/
│   │   └── UserRepositoryTest.kt
│   └── api/
│       └── UserControllerTest.kt
└── fixtures/
    └── TestFixtures.kt
```

### 🔄 4개 언어 비교

| 개념 | Kotlin | Go | Python | JS/TS |
|------|--------|-----|--------|-------|
| 프레임워크 | JUnit 5 + MockK | testing (내장) | pytest | Vitest/Jest |
| 모킹 | MockK (`every/verify`) | mockgen/수동 | unittest.mock | vi.mock |
| 테이블 테스트 | `@ParameterizedTest` | struct slice + t.Run | `@parametrize` | `test.each()` |
| 통합 테스트 | Spring test slices | build tag 분리 | 마커 분리 | 파일 분리 |

---

## 📎 출처

1. [MockK Documentation](https://mockk.io/) — MockK 공식
2. [Spring Boot Testing](https://docs.spring.io/spring-boot/reference/testing/) — 테스트 가이드
3. [kotlinx-coroutines-test](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) — 코루틴 테스트

---

> 📌 **이전 문서**: [[05-kotlin-developer-essentials-by-seniority]]
> 📌 **다음 문서**: [[07-kotlin-project-structure-and-tooling]]
> 📌 **관련**: [[spring-di-bean-test-deep-dive]]
