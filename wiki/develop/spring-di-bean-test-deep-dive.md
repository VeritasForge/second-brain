---
tags: [spring, di, ioc, bean, mockk, tdd, testcontainers]
created: 2026-04-14
---

# Spring 핵심 개념 완전 정복 — IoC, DI, Bean, 테스트, TDD

---

## 1. Spring IoC Container & DI 기초

### IoC (Inversion of Control)란?

IoC는 **설계 원칙/패턴**이다. 객체 생성의 제어권이 개발자에서 프레임워크(Spring)로 역전되는 것.

```
❌ 전통적인 방식 (개발자가 직접 다 만듦)

class OrderService {
    private PaymentService payment = new PaymentService();
    private EmailService email = new EmailService();
    // PaymentService가 바뀌면? → OrderService 코드를 수정해야 함
    // 테스트할 때? → 진짜 결제가 일어남 😱
}

✅ IoC 방식 (Spring이 대신 만들어줌)

class OrderService {
    private final PaymentService payment;
    // 생성자로 받기만 하면 됨
    OrderService(PaymentService payment) {
        this.payment = payment;
    }
}
```

비유: 요리사는 요리만 하고, 재료는 배달업체(Spring)가 가져다 주는 것 🚛→🍳

### IoC, DI, Bean, Container 관계

```
┌─────────────────────────────────────────────────────────┐
│                   Spring IoC Container                   │
│                   (= 빈 공장 + 빈 창고)                   │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │  Bean A   │  │  Bean B   │  │  Bean C   │              │
│  │ (Order    │  │ (Payment  │  │ (Email    │              │
│  │  Service) │  │  Service) │  │  Service) │              │
│  └────┬─────┘  └─────┬────┘  └──────────┘               │
│       └──────┬───────┘                                    │
│              │                                            │
│         DI (의존성 주입)                                    │
│     "A가 B를 필요로 하네? 내가 B를 만들어서 A에 넣어줄게!"  │
└─────────────────────────────────────────────────────────┘
```

| 용어                                   | 비유            | 정의                                                    |
| -------------------------------------- | --------------- | ------------------------------------------------------- |
| **IoC** (Inversion of Control)         | 배달 시스템 🚛  | "니가 만들지 마, 내가 만들어줄게" — 제어권이 역전         |
| **DI** (Dependency Injection)          | 배달 행위 📦→🏠 | IoC를 실현하는 방법. 필요한 객체를 외부에서 넣어주는 것   |
| **Bean**                               | 배달 물품 📦    | Spring IoC 컨테이너가 관리하는 객체                      |
| **IoC Container** (ApplicationContext) | 배달 회사 🏭    | Bean을 생성, 조립, 관리, 소멸하는 Spring의 핵심 엔진     |

---

## 2. IoC Container 아키텍처

### 컨테이너의 계층 구조

```
                    ┌──────────────────┐
                    │  BeanFactory     │  ← 최상위 인터페이스 (Bean 생성/관리만)
                    └────────┬─────────┘
                             │ 상속
                    ┌────────▼─────────┐
                    │ ApplicationContext│  ← 우리가 실제로 쓰는 것
                    └────────┬─────────┘     (이벤트, 국제화, AOP 등)
                             │ 구현체들
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
    AnnotationConfig    ClassPathXml    WebApplication
    ApplicationCtx      ApplicationCtx  Context
    (@Config 기반) ✅    (XML, 레거시)   (웹 전용) ✅
```

| 기능           | BeanFactory | ApplicationContext |
| -------------- | ----------- | ------------------ |
| Bean 생성/관리 | ✅          | ✅                 |
| Bean 지연 로딩 | ✅ (기본)   | ❌ (즉시 로딩)     |
| 이벤트 발행    | ❌          | ✅                 |
| AOP 통합       | ❌          | ✅                 |
| **실무 사용**  | 거의 안 씀  | **이것만 씀**      |

---

## 3. Spring 핵심 개념 7가지

Spring은 "거대한 DI 시스템"이라는 말이 있는데, **반은 맞고 반은 부족하다**. IoC/DI Container가 토대인 건 맞지만 그 위에 훨씬 많은 것이 쌓여 있다.

비유: DI는 건물의 **철골 구조** 🏗️이고, 다른 기능들은 그 위에 세워진 각 층.

```
┌─────────────────────────────────────────────┐
│            Spring 생태계 건물 🏢              │
├─────────────────────────────────────────────┤
│ 7F  Spring Cloud (MSA, Config, Discovery)   │
├─────────────────────────────────────────────┤
│ 6F  Spring Security (인증/인가)              │
├─────────────────────────────────────────────┤
│ 5F  Spring Data (JPA, Redis, MongoDB)       │
├─────────────────────────────────────────────┤
│ 4F  Spring MVC / WebFlux (웹 프레임워크)     │
├─────────────────────────────────────────────┤
│ 3F  Transaction Management (@Transactional)  │
├─────────────────────────────────────────────┤
│ 2F  AOP (관점 지향 프로그래밍)                │
├─────────────────────────────────────────────┤
│ 1F  IoC / DI Container (핵심 엔진) 🔧        │
├─────────────────────────────────────────────┤
│ 🏗️  Spring Boot (자동 설정 + 부트스트래핑)    │
└─────────────────────────────────────────────┘
```

| #   | 개념                                               | 한 줄 설명                                             | 비유                             |
| --- | -------------------------------------------------- | ------------------------------------------------------ | -------------------------------- |
| 1   | **IoC/DI Container**                               | Bean 생성·조립·관리 엔진                               | 건물 철골 🏗️                     |
| 2   | **AOP** (Aspect-Oriented Programming)              | 로깅, 트랜잭션 등 공통 관심사를 비즈니스 로직에서 분리 | CCTV — 코드 수정 없이 감시 📹   |
| 3   | **Spring MVC**                                     | HTTP 요청→Controller→응답 웹 프레임워크                | 우체국 📮                        |
| 4   | **Transaction Management**                         | `@Transactional`로 선언적 트랜잭션 관리                | 은행 이체 — 둘 다 성공 or 취소 💳 |
| 5   | **Spring Data**                                    | Repository 인터페이스만 정의하면 CRUD 자동 생성        | 자판기 🎰                        |
| 6   | **Spring Security**                                | 인증(Authentication) + 인가(Authorization)             | 건물 보안 시스템 🔐              |
| 7   | **Spring Boot Auto-configuration**                 | 클래스패스 기반 자동 Bean 등록                          | 가전제품 — 꽂으면 알아서 동작 🔌 |

### AOP 동작 원리 (특히 중요)

```
너의 코드:                    Spring이 실제로 실행하는 것:
┌──────────────────┐         ┌──────────────────────────┐
│ @Transactional   │         │ Proxy (가짜 OrderService) │
│ class OrderService│   →    │  ├── TX 시작              │
│   fun createOrder│         │  ├── 진짜 createOrder 호출 │
│                  │         │  ├── TX 커밋 (or 롤백)    │
└──────────────────┘         └──────────────────────────┘

💡 Spring은 Bean을 만들 때 "Proxy"로 감싼다.
   = BeanPostProcessor가 하는 일!
```

---

## 4. DI 구현 방법: 생성자 vs Setter vs @Autowired

### 생성자 주입 (권장 ✅)

```kotlin
@Service
class OrderService(
    private val paymentService: PaymentService,  // val = 불변!
    private val emailService: EmailService
) {
    // 생성자 1개면 @Autowired 생략 가능 (Spring 4.3+)
}
```

왜 좋은가:

- **불변성**: `val` (final) — 한번 넣으면 못 바꿈 → 멀티스레드 안전
- **완전한 초기화 보장 (Fail-Fast)**: 의존성 없으면 → 앱 시작 자체가 안 됨
- **테스트 용이성**: `val service = OrderService(mockPayment, mockEmail)` — Spring 없이 바로 테스트
- **의존성 가시성**: 생성자만 보면 뭘 필요로 하는지 한눈에 파악

### Setter 주입

Setter 메소드를 만드는 것 자체는 그냥 Java/Kotlin 문법(POJO). **Spring이 자동으로 Setter를 호출해서 Bean을 넣어주는 것**이 Spring 기능.

```kotlin
// POJO로서의 Setter (Spring 없이도 동작)
class NotificationService {
    private var emailSender: EmailSender? = null
    fun setEmailSender(sender: EmailSender) {
        this.emailSender = sender
    }
}
val service = NotificationService()
service.setEmailSender(GmailSender())  // 직접 setter 호출 → POJO!

// Spring의 Setter 주입 (@Autowired 필요)
@Service
class NotificationService {
    private var emailSender: EmailSender? = null

    @Autowired  // ← "Spring아, 이 setter를 자동으로 호출해서 Bean을 넣어줘"
    fun setEmailSender(sender: EmailSender) {
        this.emailSender = sender
    }
}
```

📌 **언제 사용?** 선택적(optional) 의존성 — 없어도 기본 동작이 가능할 때

### Setter + @Autowired vs 필드 @Autowired — 같은 문제인가?

비슷하지만 **완전히 같지는 않다**. Setter가 한 단계 나음:

| 문제점            | Setter + @Autowired               | 필드 @Autowired                  |
| ----------------- | --------------------------------- | -------------------------------- |
| 불변성 깨짐       | ❌ 같음 (`var`)                   | ❌ 같음 (`lateinit var`)         |
| Spring 결합       | ❌ 같음 (@Autowired 필요)         | ❌ 같음                          |
| 의존성 숨김       | ⚠️ **좀 나음** — setter가 public | ❌ 완전히 숨겨짐                  |
| 테스트 용이성     | ⚠️ **좀 나음** — setter 호출 가능 | ❌ 리플렉션 필요                  |
| POJO 호환         | ✅ **다름!** — @Autowired 떼면 POJO | ❌ 떼면 주입 불가                |

```kotlin
// Setter + @Autowired: 테스트에서 리플렉션 없이 가능
val service = NotificationService()
service.setEmailSender(mockSender)  // OK! 그냥 setter 호출

// 필드 @Autowired: 리플렉션 없이는 불가능
val service = NotificationService()
// service.emailSender = mockSender  ← private이라 접근 불가! 💥
```

💡 **결론**: 둘 다 생성자 주입보다 안 좋지만, Setter가 필드보다는 한 단계 나음 (테스트 가능 + POJO 호환). 그래서 "선택적 의존성"에는 Setter를 허용하는 것.

### @Autowired (필드 주입) — 비권장

```kotlin
@Service
class OrderService {
    @Autowired
    private lateinit var paymentService: PaymentService  // ⚠️ 비권장!
}
```

| 문제점            | 설명                                           |
| ----------------- | ---------------------------------------------- |
| ❌ 의존성 숨김    | 생성자 시그니처에 안 보임                       |
| ❌ 불변성 깨짐    | `val` 사용 불가                                 |
| ❌ 테스트 어려움  | Spring 컨테이너 없이 테스트하려면 리플렉션 필요 |
| ❌ God Class 유도 | 너무 쉽게 의존성 추가 → 클래스 비대화           |

📌 쓸 수 있는 경우: **테스트 클래스**에서 `@SpringBootTest` + `@Autowired`는 OK

### 3가지 비교 총정리

| 관점              | 생성자 주입 ✅    | Setter 주입        | 필드 주입 (@Autowired) |
| ----------------- | ----------------- | ------------------ | ---------------------- |
| **불변성**        | ✅ `val` (final)  | ❌ `var` (mutable) | ❌ `lateinit var`      |
| **필수/선택**     | ✅ 필수           | 선택 가능          | ⚠️ 런타임 실패        |
| **테스트**        | ✅ `new(mock)` OK | ⚠️ setter 호출     | ❌ 리플렉션 필요       |
| **의존성 가시성** | ✅ 생성자에 전부  | ⚠️ setter 흩어짐   | ❌ 숨겨짐              |
| **순환 참조 감지** | ✅ 즉시 실패     | ❌ 허용됨          | ❌ 허용됨              |
| **Spring 결합도** | ✅ POJO           | ⚠️ @Autowired 필요 | ❌ @Autowired 필수     |

### Kotlin `lateinit var`란?

"나중에 초기화할 거야"라는 Kotlin 전용 약속.

```kotlin
lateinit var name: String  // 지금은 안 넣지만 나중에 반드시 넣을게
name = "홍길동"            // 이후 사용 가능
// 초기화 안 하고 접근하면? → 💥 UninitializedPropertyAccessException
```

MockK 테스트에서 `lateinit`을 쓰는 이유: Mock 객체는 프레임워크가 테스트 시작 전에 생성하므로, 선언 시점에는 아직 없음.

| 구분               | `var x: T? = null`         | `lateinit var x: T`          |
| ------------------ | -------------------------- | ---------------------------- |
| 타입               | Nullable (`T?`)            | Non-null (`T`)               |
| 사용 시            | `x?.method()` (null 체크)  | `x.method()` (직접 호출)     |
| 초기화 안 하면     | null (조용히 실패)          | 💥 예외 (빠른 실패)          |
| 용도               | 정말 null일 수 있는 값     | DI/테스트에서 나중에 주입될 값 |

---

## 5. Bean 종류 & 아키텍처 매핑

### Spring Bean 어노테이션 전체

| 어노테이션        | 특수 기능                                                          | 용도                     |
| ----------------- | ------------------------------------------------------------------ | ------------------------ |
| `@Component`      | 없음 (기본)                                                        | 범용 Bean                |
| `@Service`        | 없음 (의미론적 구분)                                                | 비즈니스 로직            |
| `@Repository`     | ✅ DB 예외 자동 변환 (`SQLException → DataAccessException`)         | 데이터 접근              |
| `@Controller`     | ✅ `@RequestMapping` 활성화                                         | 웹 요청 처리 (View 반환) |
| `@RestController` | ✅ `@Controller` + `@ResponseBody`                                  | REST API (JSON 반환)     |
| `@Configuration`  | ✅ `@Bean` 메소드가 프록시로 감싸짐 (싱글톤 보장)                    | 설정 클래스              |

### @Component 가족 관계

```
@Component (범용)
 ├── @Service        → 비즈니스 로직 계층
 ├── @Repository     → 데이터 접근 계층 (+ DB 예외 자동 변환)
 ├── @Controller     → 웹 요청 처리 계층
 └── @Configuration  → 설정 클래스 (+ @Bean 메소드 포함)
```

### Layered Architecture 매핑

```
┌────────────────────────────────────────────────┐
│ 📱 Presentation Layer                          │  @Controller, @RestController
├────────────────────────────────────────────────┤
│ ⚙️ Service Layer (Business Logic)              │  @Service
├────────────────────────────────────────────────┤
│ 💾 Data Access Layer                           │  @Repository
├────────────────────────────────────────────────┤
│ 🔧 Cross-cutting / Config                     │  @Configuration, @Component
└────────────────────────────────────────────────┘
```

### Clean Architecture 매핑

```
┌────────────────────────────────────────────────┐
│ Frameworks & Drivers (가장 바깥쪽)              │  @Controller, @Configuration
├────────────────────────────────────────────────┤
│ Interface Adapters (어댑터 계층)                │  @Repository (구현체), @Component
├────────────────────────────────────────────────┤
│ Use Cases (유즈케이스 계층)                     │  @Service
├────────────────────────────────────────────────┤
│ Entities / Domain (가장 안쪽)                   │  ❌ Spring 어노테이션 없음!
└────────────────────────────────────────────────┘

💡 Domain 계층에는 Spring 어노테이션이 없어야 함 = Clean Architecture의 핵심
```

---

## 6. Bean 라이프사이클

### 전체 흐름도

```
┌─── Phase 1: 빈 정의 수집 ────────────────────────┐
│  @ComponentScan으로 @Component 붙은 클래스 찾기     │
│  → BeanDefinition 객체들 생성 (설계도)              │
└──────────────────┬───────────────────────────────┘
                   ▼
┌─── Phase 2: 빈 인스턴스 생성 ────────────────────┐
│  리플렉션으로 실제 객체 생성 (new)                  │
└──────────────────┬───────────────────────────────┘
                   ▼
┌─── Phase 3: 의존성 주입 (DI) ────────────────────┐
│  생성자 주입 / Setter 주입 / 필드 주입 수행         │
└──────────────────┬───────────────────────────────┘
                   ▼
┌─── Phase 4: 초기화 콜백 ─────────────────────────┐
│  @PostConstruct → InitializingBean → initMethod    │
└──────────────────┬───────────────────────────────┘
                   ▼
┌─── Phase 5: 사용 (대부분의 시간) ────────────────┐
└──────────────────┬───────────────────────────────┘
                   ▼
┌─── Phase 6: 소멸 콜백 ──────────────────────────┐
│  @PreDestroy → DisposableBean → destroyMethod      │
└──────────────────────────────────────────────────┘
```

### 비유: 회사 신입사원의 하루

| Phase            | Bean 라이프사이클  | 신입사원 비유 🧑‍💼          |
| ---------------- | ------------------ | -------------------------- |
| 1. 정의 수집     | @Component 스캔    | 이력서(설계도) 수집        |
| 2. 인스턴스 생성 | `new OrderService()` | 합격! 첫 출근            |
| 3. 의존성 주입   | 필요한 Bean 주입   | 노트북, 계정, 팀 배정 받음 |
| 4. 초기화        | @PostConstruct     | 온보딩 완료!               |
| 5. 사용          | 비즈니스 로직 수행 | 열심히 일하는 중...        |
| 6. 소멸          | @PreDestroy        | 퇴사 전 인수인계           |

---

## 7. Bean Scope

| Scope                | 인스턴스 수     | 소멸 관리         | 용도                         |
| -------------------- | --------------- | ----------------- | ---------------------------- |
| **singleton** (기본) | 1개             | Spring이 관리     | 대부분의 Service, Repository |
| **prototype**        | 매번 새로       | ⚠️ Spring이 안 함 | 상태 있는 객체               |
| request              | HTTP 요청당 1개 | 요청 끝나면       | 웹 전용                      |
| session              | HTTP 세션당 1개 | 세션 끝나면       | 웹 전용                      |

### Prototype Scope: 누가 소멸 관리?

Spring은 Prototype을 만들어만 주고 참조를 추적하지 않는다 (추적하면 메모리 누수). **개발자 + GC (Garbage Collector)**가 관리.

상태 있는 객체 예시: 파일 업로드 핸들러, DB 커넥션 래퍼, 빌더 객체, CSV/Excel 파서

---

## 8. Reflection (리플렉션)

**런타임에 클래스의 구조를 들여다보고 조작하는 기능**. 클래스 이름(문자열)으로 인스턴스를 만들 수도 있다.

```kotlin
// 1️⃣ 클래스 이름(String) → 인스턴스 생성
val className = "com.example.OrderService"
val clazz = Class.forName(className)
val instance = clazz.getDeclaredConstructor().newInstance()

// 2️⃣ Kotlin KClass로 인스턴스 생성
val kClass = OrderService::class
val instance2 = kClass.createInstance()  // 기본 생성자 필요

// 3️⃣ private 필드 접근
val field = clazz.getDeclaredField("secretKey")
field.isAccessible = true  // private 뚫기! 🔓
val value = field.get(instance)

// 4️⃣ Kotlin에서 프로퍼티 탐색
import kotlin.reflect.full.memberProperties
OrderService::class.memberProperties.forEach { prop ->
    println("${prop.name}: ${prop.returnType}")
}
```

Spring이 Reflection을 쓰는 곳: ComponentScan(어노테이션 확인), Bean 인스턴스 생성(`Constructor.newInstance()`), @Autowired 필드 주입(`Field.set()`), AOP Proxy 생성

---

## 9. BeanPostProcessor

Bean 라이프사이클에 끼어드는 **후처리기**. Bean이 만들어진 후, 초기화 전후에 "가로채서" 수정할 수 있다.

비유: 공장의 품질 검사 라인 🏭

```
Bean 생성 → DI → postProcessBeforeInitialization() → @PostConstruct → postProcessAfterInitialization()
                                                                        ⭐ AOP Proxy가 여기서 만들어짐!
```

| Processor                              | 하는 일                                          |
| -------------------------------------- | ------------------------------------------------ |
| `AutowiredAnnotationBeanPostProcessor` | `@Autowired`, `@Value` 처리                       |
| `CommonAnnotationBeanPostProcessor`    | `@PostConstruct`, `@PreDestroy` 처리              |
| `AbstractAutoProxyCreator`             | `@Transactional`, `@Cacheable` 등 AOP Proxy 생성 |
| `ScheduledAnnotationBeanPostProcessor` | `@Scheduled` (크론잡) 처리                        |

💡 `@Transactional`이 붙은 Bean은 `postProcessAfterInitialization`에서 Proxy로 감싸짐. 그래서 **같은 클래스 내부에서 호출하면 @Transactional이 안 먹는** 유명한 문제가 있다 (Proxy를 안 거치니까).

---

## 10. @Conditional

"**조건이 맞을 때만** Bean을 등록해라". Spring Boot Auto-configuration의 핵심.

```kotlin
@Configuration
class CacheConfig {
    @Bean
    @ConditionalOnClass(RedisClient::class)
    fun redisCacheManager(): CacheManager = RedisCacheManager()

    @Bean
    @ConditionalOnMissingBean(CacheManager::class)
    fun noOpCacheManager(): CacheManager = NoOpCacheManager()
}
```

| 어노테이션                     | 조건                              |
| ------------------------------ | --------------------------------- |
| `@ConditionalOnProperty`       | 설정값이 특정 값일 때             |
| `@ConditionalOnClass`          | 특정 클래스가 클래스패스에 있을 때 |
| `@ConditionalOnMissingBean`    | 같은 타입 Bean이 아직 없을 때     |
| `@ConditionalOnBean`           | 특정 Bean이 이미 있을 때          |
| `@ConditionalOnWebApplication` | 웹 앱으로 실행 중일 때            |
| `@Profile("dev")`              | 활성 프로파일이 맞을 때 (`@Conditional` 내부 사용) |

Spring Boot Auto-configuration의 비밀: `spring-boot-autoconfigure` jar 안에 수백 개의 `@Configuration` 클래스가 있는데, 전부 `@Conditional`로 보호됨 → "Convention over Configuration"의 정체.

---

## 11. 순환 참조 (Circular Dependency)

### 문제

```kotlin
@Service
class OrderService(private val paymentService: PaymentService)  // A → B
@Service
class PaymentService(private val orderService: OrderService)    // B → A
// → 💥 BeanCurrentlyInCreationException
```

### Spring의 3단계 캐시 (Setter/Field 주입에서만 동작)

```
Level 1: singletonObjects      → 완성품 보관
Level 2: earlySingletonObjects  → 반제품 보관
Level 3: singletonFactories     → 반제품 만드는 공장

과정: A 생성(빈 껍데기) → L3 등록 → B 생성 → B가 A 필요 →
      L3에서 반제품 A 꺼냄 → B 완성 → A에 B 주입 → A 완성

⚠️ 생성자 주입에서는 불가 (완전한 객체만 주입 가능)
```

### Spring Boot 2.6+에서 기본 금지

순환 참조 = 설계 결함의 신호. 해결법 우선순위:

1. ✅ **설계 리팩토링** — 공통 로직을 세 번째 클래스로 추출
2. ⚠️ **@Lazy** — 프록시를 먼저 주입, 실제 사용 시점에 진짜 생성
3. ❌ `spring.main.allow-circular-references=true` — 비권장

---

## 12. @SpringBootTest와 테스트 전략

### @SpringBootTest란?

전체 ApplicationContext를 로드하는 무거운 테스트. 학교 전체를 열어서 시험 보는 것 🏫

### 테스트 종류별 비교

| 테스트 종류                | 로딩 범위    | 속도     | 용도            |
| -------------------------- | ------------ | -------- | --------------- |
| Plain Unit (Mockito/MockK) | Spring 없음  | ~100ms   | 비즈니스 로직   |
| `@WebMvcTest`              | 웹 레이어만  | 2~5초    | Controller      |
| `@DataJpaTest`             | JPA 레이어만 | 2~5초    | Repository      |
| `@SpringBootTest`          | 전체         | 10~30초+ | E2E 통합 테스트 |

---

## 13. Mock, Stub, Spy, Fake — 테스트 더블

### 핵심 구분

MockK에서 `every`는 **Stub** 행위(응답 설정)이고, `verify`는 **Mock** 행위(호출 검증). 같은 객체에서 두 역할을 다 함.

```kotlin
every { paymentService.charge(100.0) } returns true  // ← Stub (응답 설정)
orderService.createOrder(100.0)
verify { paymentService.charge(100.0) }               // ← Mock (호출 검증)
```

| 구분       | Stub 🎰                   | Mock 🎭                            | Spy 🕵️                     | Fake 🏗️           |
| ---------- | ------------------------- | ---------------------------------- | --------------------------- | ------------------ |
| **객체**   | 가짜                      | 가짜                               | **진짜** (일부 가짜)        | **진짜** (간소화)  |
| **응답**   | ✅ `every { } returns`    | ✅ `every { } returns`             | 일부만                      | ❌ 자체 로직        |
| **검증**   | ❌ 안 함                  | ✅ `verify { }`                    | ✅ 가능                     | ❌ 안 함            |
| **만들기** | `mockk()` + `every`       | `mockk()` + `every` + `verify`     | `spyk(realObj)`             | 직접 클래스 작성   |
| **비유**   | 자판기                    | 보안카메라                          | 이중스파이                  | 연습용 미니어처    |

### Fake 예시: FakeRedis

FakeRedis (Python fakeredis)는 Fake의 교과서적 예시. 실제 Redis 인터페이스를 In-Memory로 구현해서 Redis 없이 테스트.

### MockK + @ExtendWith 예제 (Kotlin)

```kotlin
@ExtendWith(MockKExtension::class)
class OrderServiceTest {

    @MockK
    lateinit var paymentService: PaymentService

    @MockK
    lateinit var emailService: EmailService

    @InjectMockKs
    lateinit var orderService: OrderService
    // → MockK가 OrderService(paymentService, emailService) 생성자 호출

    @Test
    fun `주문 생성 시 결제가 호출되어야 한다`() {
        // Given (Stub)
        every { paymentService.charge(100.0) } returns true
        every { emailService.send(any()) } just Runs

        // When
        orderService.createOrder(100.0)

        // Then (Mock)
        verify { paymentService.charge(100.0) }
        verify { emailService.send(any()) }
    }
}
```

### `every` 주요 패턴

```kotlin
every { mock.method(100.0) } returns true             // 특정 값
every { mock.method(any()) } returns true              // 아무 값이든
every { mock.method(more(1000.0)) } returns false      // 조건부
every { mock.method(any()) } throws IllegalArgumentException()  // 예외
every { mock.voidMethod(any()) } just Runs             // void 메소드
every { mock.method(any()) } returnsMany listOf(true, true, false)  // 연속 호출
every { mock.method(capture(slot)) } answers { slot.captured > 0 }  // 캡처+커스텀
```

### @ExtendWith vs @SpringBootTest

```
@ExtendWith(MockKExtension::class)          @SpringBootTest
├── Spring 없음 ❌                          ├── Spring IoC Container ✅
├── @Service, @Component 무시 ❌            ├── 모든 Bean 라이프사이클 ✅
├── 단순히 클래스 Mock + 주입 ✅            ├── @MockBean으로 특정 Bean만 교체 ✅
└── ⚡ ~100ms                               └── 🐌 10~30초
```

MockK는 Spring을 전혀 모른다. `@Service`가 붙어있든 아니든 그냥 Kotlin/Java 클래스를 모킹하는 것. 통합 테스트로 실제 Bean이 필요하면 `@SpringBootTest`.

---

## 14. TDD 전략 (Spring 환경)

### 테스트 원칙

- 모든 public 메소드는 단위 테스트
- DB, Cache는 통합 테스트
- External API는 Mocking
- 비율이 아닌 **원칙** 기반

### Testcontainers vs docker-compose

| 관점           | docker-compose              | Testcontainers                 |
| -------------- | --------------------------- | ------------------------------ |
| **시작 속도**  | ✅ 이미 떠있어서 빠름       | ❌ 매번 새로 시작 (10~30초)    |
| **상태 깨끗함** | ❌ 이전 데이터 남을 수 있음 | ✅ 매번 깨끗한 상태            |
| **포트 충돌**  | ❌ 고정 포트                | ✅ 랜덤 포트                   |
| **CI/CD**      | ⚠️ docker-compose 설치 필요 | ✅ Docker만 있으면 OK          |

Testcontainers의 `withReuse(true)`로 로컬에서는 컨테이너를 재사용하고, CI에서는 clean 모드로 돌려 양쪽 장점을 취합 가능.

### 커버리지

| 기준             | 장점                                    | 단점               |
| ---------------- | --------------------------------------- | ------------------ |
| **라인 커버리지** | ✅ 이해하기 쉬움, 시각화 직관적         | ❌ 분기를 놓침     |
| **분기 커버리지** | ✅ 조건문 누락 잡아냄, 엣지 케이스 강제 | ❌ 달성하기 어려움 |

커버리지는 "어디를 테스트 안 했는지" 찾는 **레이더**일 뿐. 진짜 품질은 버그 시나리오 기반 테스트와 의미 있는 assertion에서 나온다.

추가 도구: **Mutation Testing** (PIT/pitest) — 코드를 일부러 살짝 바꿔서 테스트가 잡는지 확인

---

## 핵심 정리

1. **IoC** = 제어의 역전 (프레임워크가 객체 생성), **DI** = IoC의 대표적 구현 방법
2. **IoC Container** (ApplicationContext) = Bean의 생성~소멸까지 전체 라이프사이클 관리
3. **Spring = DI(토대) + AOP + MVC + 트랜잭션 + Data + Security + Auto-config**
4. **생성자 주입** 권장: 불변 + 안전 + 테스트 쉬움 / Setter = 선택적 / @Autowired 필드 = 테스트에서만
5. **Bean 라이프사이클** 6단계: 정의 수집 → 생성 → DI → 초기화 → 사용 → 소멸
6. **BeanPostProcessor**로 AOP Proxy 생성 → `@Transactional` 내부 호출 안 먹는 이유
7. **@Conditional** = Spring Boot Auto-configuration의 핵심 메커니즘
8. **순환 참조**: 생성자 주입에서 즉시 감지 (장점). 해결법은 설계 리팩토링이 최선
9. **Mock vs Stub**: `every` = Stub(응답 설정), `verify` = Mock(호출 검증)
10. **@ExtendWith(MockKExtension::class)**: Spring 없이 단위 테스트, `@SpringBootTest`: 통합 테스트
