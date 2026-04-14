---
tags: [spring-aop, proxy, aspectj, java, aop]
created: 2026-04-13
---

# 📖 Spring AOP (Aspect-Oriented Programming) — 완전 가이드

> 💡 **한줄 요약**: Spring AOP는 프록시 기반으로 메서드 실행 시점에 로깅, 트랜잭션, 보안 같은 **횡단 관심사(Cross-Cutting Concerns)** 를 비즈니스 로직과 분리하여 모듈화하는 프로그래밍 패러다임이다.

---

## 1️⃣ 무엇인가? (What is it?)

**AOP(Aspect-Oriented Programming)** 는 OOP를 보완하는 프로그래밍 패러다임으로, 여러 클래스에 걸쳐 반복되는 **횡단 관심사**를 별도 모듈(Aspect)로 분리한다.

**현실 비유** 🏫: 학교를 생각해보자. 수학, 과학, 영어 선생님이 각자 수업을 하지만, **출석 체크**는 모든 수업에서 동일하게 일어난다. 출석 체크를 각 선생님이 직접 구현하는 대신, "출석 담당자"가 모든 교실에 들어가서 자동으로 처리하는 것 — 이것이 AOP의 핵심 아이디어다.

- **탄생 배경**: 1997년 Xerox PARC의 Gregor Kiczales 팀이 ECOOP 학회에서 AOP 개념을 제안하였고, 이후 **2001년 AspectJ 1.0**으로 Java 구현체가 공개됨. Spring AOP는 이를 **Spring IoC 컨테이너와 긴밀히 통합**하여 엔터프라이즈 문제 해결에 초점을 맞춤
- **해결하는 문제**: 로깅, 트랜잭션, 보안 등의 코드가 비즈니스 로직 전체에 흩어지는 **코드 탱글링(Tangling)** 과 **코드 스캐터링(Scattering)** 문제

> 📌 **핵심 키워드**: `Cross-Cutting Concern`, `Proxy`, `Aspect`, `Advice`, `Pointcut`, `JoinPoint`

---

## 2️⃣ 핵심 개념 (Core Concepts)

### 구성 요소 관계도

```
┌─────────────────────────────────────────────────────────┐
│                    🎯 Aspect                            │
│  (횡단 관심사를 모듈화한 클래스, @Aspect)                 │
│                                                         │
│   ┌──────────────┐         ┌──────────────────┐         │
│   │   Pointcut   │────────▶│     Advice       │         │
│   │  (어디에?)    │         │  (무엇을 할까?)   │         │
│   │              │         │                  │         │
│   │ @Pointcut    │         │ @Before          │         │
│   │ execution()  │         │ @After           │         │
│   │ @annotation()│         │ @Around          │         │
│   │ within()     │         │ @AfterReturning  │         │
│   └──────────────┘         │ @AfterThrowing   │         │
│                            └──────────────────┘         │
│                                    │                    │
│                                    ▼                    │
│                          ┌──────────────────┐           │
│                          │    JoinPoint      │           │
│                          │ (실제 실행 지점)    │           │
│                          │ = 메서드 실행 시점  │           │
│                          └──────────────────┘           │
└─────────────────────────────────────────────────────────┘
```

| 구성 요소          | 역할           | 설명                                                                                            |
| --------------- | ------------ | --------------------------------------------------------------------------------------------- |
| **Aspect**      | 모듈화 단위       | 횡단 관심사를 캡슐화한 클래스. `@Aspect` 어노테이션으로 선언                                                       |
| **Advice**      | 실행할 동작       | Aspect가 특정 JoinPoint에서 수행할 작업의 **총칭** (Before, After, Around 등이 모두 Advice)                      |
| **Pointcut**    | 적용 대상 지정     | 어떤 JoinPoint에 Advice를 적용할지 정의하는 필터 규칙. 메서드 이름으로 별명을 붙여 재사용 가능                                    |
| **JoinPoint**   | 적용 가능 지점     | 프로그램 실행 중 Aspect가 끼어들 수 있는 지점 (Spring AOP는 **메서드 실행만** 지원)                                     |
| **Weaving(위빙)** | 결합 과정        | Aspect를 대상 객체에 적용(끼워 넣는) 과정. Spring AOP는 **런타임 위빙** (프록시 감싸기)                                   |
| **Target Object** | 대상 객체        | Advice가 적용되는 원본 객체 (항상 프록시됨)                                                                   |

### 🔑 Advice 유형 정리

**Advice는 총칭이고, 아래 5가지가 구체적인 유형이다** (@Around도 Advice의 한 종류):

```
┌─────────────────────────────────────────────────────┐
│                  Advice (어드바이스)                   │
│         "Aspect가 실행하는 동작"의 총칭               │
│                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐         │
│  │ @Before  │ │ @After   │ │@AfterReturn- │         │
│  │          │ │ (항상)   │ │ ing (성공시) │         │
│  └──────────┘ └──────────┘ └──────────────┘         │
│  ┌──────────────┐ ┌──────────────────────┐          │
│  │@AfterThrowing│ │      @Around         │          │
│  │ (예외 시)    │ │ (전체를 감싸는 래퍼)  │          │
│  └──────────────┘ └──────────────────────┘          │
└─────────────────────────────────────────────────────┘
```

```
메서드 실행 타임라인
─────────────────────────────────────────────────►

  @Before       메서드 실행        @AfterReturning (정상)
     │              │                    │
     ▼              ▼                    ▼
  ┌─────┐     ┌──────────┐         ┌─────────┐
  │ Pre │────▶│  Target  │────────▶│  Post   │
  │     │     │  Method  │         │(성공 시) │
  └─────┘     └──────────┘         └─────────┘
                   │                    │
                   │ (예외 발생)         │
                   ▼                    ▼
              ┌──────────┐         ┌─────────┐
              │ @After   │         │ @After  │
              │ Throwing │         │ (항상)  │
              └──────────┘         └─────────┘

  ◄─────────── @Around (전체를 감싸는 래퍼) ───────────►
```

### @Pointcut — "어디에 AOP를 적용할지" 필터 규칙

비유: **교통 단속 카메라 설치 규칙**

```
📸 "고속도로의 모든 교차로에 단속 카메라를 설치하라"
   = @Pointcut("execution(* com.example.service.*.*(..))")

분해:
┌──────────────────────────────────────────────────────┐
│  execution(* com.example.service.*.*(..))            │
│                                                      │
│  execution( ← "메서드가 실행될 때"                    │
│    *       ← "리턴 타입 아무거나"                     │
│    com.example.service  ← "이 패키지 안의"           │
│    .*      ← "모든 클래스의"                          │
│    .*      ← "모든 메서드"                            │
│    (..)    ← "파라미터 아무거나"                      │
│  )                                                   │
└──────────────────────────────────────────────────────┘
```

```java
// Pointcut 정의: 별명(alias)을 붙여 재사용
@Pointcut("execution(* com.example.service.*.*(..))")
public void serviceLayer() {}  // ← 이 메서드 이름이 "별명"

// 다른 Advice에서 별명으로 참조
@Before("serviceLayer()")      // ← "serviceLayer 규칙에 해당하는 곳에서 실행!"
public void doSomething() { ... }
```

### @Around와 ProceedingJoinPoint

**@Around = 메서드 실행 전체를 감싸는 래퍼.** @Before + @After를 하나의 메서드 안에서 제어.

```
@Before + @After 방식:
┌────────┐  ┌─────────────┐  ┌───────┐
│@Before │→│ 원본 메서드  │→│@After │
└────────┘  └─────────────┘  └───────┘
 (독립)       (독립)           (독립)


@Around 방식:
┌─────────────────────────────────────────┐
│              @Around                     │
│  (코드A)  →  proceed()  →  (코드B)      │
│              ┌─────────┐                │
│              │원본 메서드│                │
│              └─────────┘                │
└─────────────────────────────────────────┘
 (하나의 메서드 안에서 전체 제어)
```

**ProceedingJoinPoint = @Around 전용 "리모컨".**

```
┌──────────────────────────────────────────┐
│           ProceedingJoinPoint             │
│                                          │
│  🔴 proceed()       → "원본 메서드 실행!" │
│  📋 getSignature()  → "어떤 메서드인지"   │
│  📂 getArgs()       → "전달된 파라미터"   │
│  🎯 getTarget()     → "원본 객체 참조"    │
└──────────────────────────────────────────┘

  @Before, @After  → JoinPoint (정보만 조회 가능)
  @Around          → ProceedingJoinPoint (정보 조회 + 실행 제어)
```

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

Spring AOP는 **순수 Java로 구현**되며 별도의 컴파일러나 클래스 로더가 필요 없다. 핵심은 **프록시 패턴**이다.

> ⚠️ **"순수 Java"의 정확한 의미**: "프록시 객체가 POJO(Plain Old Java Object)다"가 아니라, AOP를 위해 **별도 컴파일러(ajc 등)가 불필요**하다는 뜻. 표준 Java API(`java.lang.reflect.Proxy` 또는 CGLIB)만으로 프록시를 생성한다. 비유: "특수 오븐(AspectJ 컴파일러) 없이 일반 오븐(JDK)으로 구울 수 있다"

### 프록시를 만드는 2가지 방법 — JDK Dynamic Proxy vs CGLIB

비유: **연예인의 매니저 고용 방법**

```
📋 방식 1: JDK Dynamic Proxy (계약서 기반 매니저)
─────────────────────────────────────────────────
"이 연예인은 '가수 계약서(인터페이스)'를 갖고 있으니,
 같은 계약서를 가진 매니저를 붙여주자!"

  ┌──────────────┐        ┌──────────────┐
  │  UserService  │        │  JDK Proxy   │
  │  (interface)  │◄───────│  같은 계약서  │
  └──────┬───────┘  구현   └──────────────┘
         │ 구현
  ┌──────▼───────┐
  │ UserService  │
  │ Impl (진짜)  │
  └──────────────┘


📋 방식 2: CGLIB Proxy (쌍둥이 매니저)
─────────────────────────────────────────────────
"이 연예인은 계약서(인터페이스)가 없네?
 연예인의 쌍둥이(서브클래스)를 만들어서 매니저 역할을 시키자!"

  ┌──────────────┐
  │  UserService  │  ← 원본 클래스
  └──────┬───────┘
         │ 상속 (extends)
  ┌──────▼───────┐
  │ UserService  │  ← CGLIB이 바이트코드로 만든 서브클래스
  │ $$EnhancerBy │
  │ SpringCGLIB  │
  └──────────────┘
```

| 기준               | JDK Dynamic Proxy                    | CGLIB Proxy                |
| ---------------- | ------------------------------------ | -------------------------- |
| 🔧 생성 방식         | `java.lang.reflect.Proxy` (JDK 내장)   | 바이트코드 라이브러리로 서브클래스 생성      |
| 📋 필요 조건         | 인터페이스 구현 필수                          | 인터페이스 불필요                   |
| 🚫 제약             | 인터페이스에 정의된 메서드만 프록시                  | `final` 클래스/메서드 프록시 불가      |
| 📦 **Spring Boot 2.0+** | 명시 설정 필요                             | **기본값** (`spring.aop.proxy-target-class=true`) |

### 전체 아키텍처 다이어그램

```
┌──────────────────────────────────────────────────────────────┐
│                   Spring IoC Container                       │
│                                                              │
│  Client                  Proxy                 Target Bean   │
│  ┌──────┐          ┌─────────────┐           ┌─────────────┐│
│  │      │──call──▶│   AOP Proxy  │──delegate─▶│  UserService ││
│  │Caller│          │             │            │             ││
│  │      │◀─result─│ 1.Before    │◀─result────│ getUser()   ││
│  │      │          │ 2.Invoke    │            │             ││
│  └──────┘          │ 3.After     │            └─────────────┘│
│                    └─────────────┘                            │
│                                                              │
│  ※ 1,2,3 = Advice가 실행되는 부분                             │
│    1. Before Advice (@Before)                                │
│    2. Target 메서드 실행 (proceed())                          │
│    3. After Advice (@After, @AfterReturning 등)              │
└──────────────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (Step by Step)

```
┌─────────── Spring IoC Container 내부 ──────────────────────┐
│                                                            │
│  📦 Step 1 — Bean 정의 스캔                                 │
│  IoC Container가 @Component, @Service, @Aspect 등을        │
│  찾아서 "이런 빈들을 만들어야 해!" 목록(BeanDefinition) 작성│
│                         │                                  │
│                         ▼                                  │
│  🎯 Step 2 — Pointcut 매칭                                  │
│  AnnotationAwareAspectJAutoProxyCreator (BeanPostProcessor)│
│  가 postProcessAfterInitialization 단계에서                 │
│  각 빈의 메서드를 Pointcut 표현식과 대조                     │
│  "이 빈에 AOP를 적용할지 결정하는 필터"                      │
│                         │                                  │
│                         ▼                                  │
│  🏭 Step 3 — 프록시 생성                                    │
│  매칭되는 빈에 대해 프록시 객체를 생성                       │
│  (JDK Dynamic Proxy 또는 CGLIB)                            │
│                         │                                  │
│                         ▼                                  │
│  🔄 Step 4 — 프록시로 바꿔치기                               │
│  IoC 컨테이너의 "출석부"에서 진짜 객체를 프록시로 교체       │
│  다른 빈들이 @Autowired로 주입받으면 프록시가 주입됨         │
│                         │                                  │
│                         ▼                                  │
│  ▶️  Step 5 — 런타임 인터셉션                                │
│  클라이언트가 메서드 호출 시 프록시가 가로채서 Advice 실행    │
└────────────────────────────────────────────────────────────┘
```

### "원본 빈 대신 프록시가 등록된다" = 바꿔치기

```
━━ Step 1: 원래 계획 ━━━━━━━━━━━━━━━━━━━
  IoC 컨테이너 출석부:
  ┌──────────────────┐
  │ "UserService" →  │──▶ 진짜 UserService 객체
  └──────────────────┘

━━ Step 2: AOP 적용 후 (바꿔치기!) ━━━━━
  출석부:
  ┌──────────────────┐     ┌──────────────┐
  │ "UserService" →  │──▶  │  AOP Proxy   │
  └──────────────────┘     │  (가짜!)      │
                           │    │          │
                           │    ▼          │
                           │ 진짜 User     │
                           │ Service를     │
                           │ 안에 숨기고   │
                           │ 있음          │
                           └──────────────┘

━━ 다른 빈이 UserService를 주입받으면 ━━━━
  @Autowired
  private UserService userService;
  // → 진짜가 아니라 프록시가 주입됨!
  // → 하지만 호출하는 쪽은 모름 (같은 인터페이스니까)
```

### 💻 코드 예시

```java
@Slf4j  // Lombok — Logger 자동 생성
// 또는 수동: private static final Logger log = LoggerFactory.getLogger(LoggingAspect.class);
@Aspect
@Component
public class LoggingAspect {

    // Pointcut: service 패키지의 모든 public 메서드 (별명: serviceLayer)
    @Pointcut("execution(* com.example.service.*.*(..))")
    public void serviceLayer() {}

    // Advice: serviceLayer 별명에 해당하는 메서드 실행 전후로 로깅
    @Around("serviceLayer()")
    public Object logExecutionTime(ProceedingJoinPoint joinPoint) throws Throwable {
        long start = System.currentTimeMillis();

        Object result = joinPoint.proceed();  // 실제 메서드 실행 (리모컨의 '재생' 버튼)

        long elapsed = System.currentTimeMillis() - start;
        log.info("{} executed in {}ms",
            joinPoint.getSignature().getName(), elapsed);

        return result;
    }
}
```

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| #   | 유즈 케이스          | 설명                                       | 적합한 이유                |
| --- | --------------- | ---------------------------------------- | ---------------------- |
| 1   | **트랜잭션 관리**     | `@Transactional`로 선언적 트랜잭션               | 비즈니스 로직에서 트랜잭션 코드 분리  |
| 2   | **로깅/모니터링**     | 메서드 진입/퇴장, 실행 시간 측정                      | 모든 서비스에 공통 적용         |
| 3   | **보안/인가**       | `@Secured`, `@PreAuthorize`              | 인가 로직을 메서드 단위로 선언     |
| 4   | **캐싱**          | `@Cacheable`, `@CacheEvict`              | 캐시 로직을 비즈니스 로직에서 분리   |
| 5   | **예외 처리**       | 공통 예외 변환, 에러 로깅                          | 중앙화된 에러 핸들링           |
| 6   | **감사 추적(Audit)** | 누가, 언제, 무엇을 했는지 기록                       | 컴플라이언스 요구사항 대응        |

Spring Framework 자체도 `@Transactional`, `@Cacheable`, `@Async` 모두 내부적으로 AOP 프록시로 구현되어 있다.

### ✅ 베스트 프랙티스

1. **Pointcut을 구체적으로 작성**: `execution(* *(..))` 같은 광범위한 표현식 대신 패키지/클래스를 명시
2. **커스텀 어노테이션 활용**: `@Loggable`, `@Auditable` 같은 마커 어노테이션으로 적용 대상을 명시적으로 표현
3. **@Around보다 구체적 Advice 선호**: 가능하면 `@Before`, `@AfterReturning` 등 목적에 맞는 좁은 범위의 Advice를 사용. `@Around`는 `proceed()` 호출 누락 위험이 있으므로 전후 모두 제어가 필요할 때만 사용

```java
// ❌ 메서드 전에만 할 일인데 @Around를 씀 (과하다)
@Around("serviceLayer()")
public Object overkill(ProceedingJoinPoint jp) throws Throwable {
    log.info("시작!");
    return jp.proceed();  // proceed 안 부르면 장애!
}

// ✅ @Before로 충분 (간결하고 안전)
@Before("serviceLayer()")
public void simple(JoinPoint jp) {
    log.info("시작!");  // proceed() 걱정 없음!
}
```

4. **@Order로 실행 순서 관리**: 여러 Aspect가 같은 메서드에 적용될 때 `@Order` 어노테이션으로 우선순위 명시
5. **Spring 내장 기능 우선 사용**: 트랜잭션, 캐싱, 보안은 직접 AOP 구현보다 Spring 내장 어노테이션 사용
6. **Aspect를 stateless로 유지**: Aspect 인스턴스는 싱글톤 빈이므로 스레드 간 공유됨. 가변 상태를 갖지 않도록 설계해야 동시성 버그를 방지할 수 있다

### 🔢 @Order — 여러 Aspect의 실행 순서 제어

```java
@Aspect @Component @Order(1)  // 가장 먼저 실행
public class SecurityAspect {
    @Before("execution(* com.example.service.*.*(..))")
    public void checkAuth(JoinPoint jp) {
        log.info("🔒 보안 검사!");
    }
}

@Aspect @Component @Order(2)  // 두 번째
public class LoggingAspect {
    @Before("execution(* com.example.service.*.*(..))")
    public void logEntry(JoinPoint jp) {
        log.info("📝 로깅!");
    }
}

@Aspect @Component @Order(3)  // 세 번째
public class PerformanceAspect {
    @Around("execution(* com.example.service.*.*(..))")
    public Object measureTime(ProceedingJoinPoint jp) throws Throwable {
        long start = System.currentTimeMillis();
        Object result = jp.proceed();
        log.info("⏱️ {}ms", System.currentTimeMillis() - start);
        return result;
    }
}
```

```
실행 흐름:

@Order(1)        @Order(2)        @Order(3)         Target
Security         Logging          Performance       Method
   │                │                │                │
   ├─▶ 보안 검사 ──├─▶ 로깅 ───────├─▶ 시간 측정 ──├─▶ 실행!
   │                │                │  proceed()     │
   │                │                │  ◀────────────│
   │                │                │  ⏱️ 시간 기록   │
```

#### 🐍 Python decorator와 비교

```python
# Python decorator 순서
@A    # ← 3. 가장 바깥쪽 래퍼 → 실행 시 가장 먼저 진입
@B    # ← 2.
@C    # ← 1. 가장 먼저 래핑됨 (코드 로딩 시)
def func():
    pass
# 내부적으로: A(B(C(func)))
# 래핑 순서: C → B → A (아래→위)
# 실행 순서: A → B → C → func (위→아래)
```

| 기준     | Python decorator                    | Spring @Order              |
| ------ | ----------------------------------- | -------------------------- |
| 순서 결정  | 코드 위치 (래핑: 아래→위, 실행: 위→아래)         | `@Order` 숫자 (작을수록 먼저)      |
| 적용 범위  | 해당 함수만                              | 동일 Pointcut 매칭되는 모든 메서드    |
| 변경 용이성 | 코드 순서 변경 필요                         | 숫자만 변경                     |
| 기본값    | 항상 명시적                              | `@Order` 없으면 순서 보장 안 됨 ⚠️  |

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분     | 항목                      | 설명                                                 |
| ------ | ----------------------- | -------------------------------------------------- |
| ✅ 장점   | **횡단 관심사의 메서드 레벨 분리**    | 비즈니스 로직과 인프라 코드를 메서드 인터셉션 수준에서 깔끔하게 분리             |
| ✅ 장점   | **코드 중복 제거**             | 동일한 로깅/보안 코드를 수십 개 클래스에 반복하지 않아도 됨                 |
| ✅ 장점   | **비침투적**                 | 비즈니스 코드를 수정하지 않고 기능 추가 가능                          |
| ✅ 장점   | **Spring IoC 통합**        | 별도 컴파일러 없이 Spring Bean으로 간단히 설정                     |
| ✅ 장점   | **선언적 프로그래밍**            | `@Transactional` 한 줄로 트랜잭션 관리 가능                    |
| ❌ 단점   | **디버깅 어려움**              | 프록시 체인 때문에 콜스택이 복잡해지고 디버깅이 어려움                     |
| ❌ 단점   | **Self-invocation 제약**   | 같은 클래스 내 메서드 호출 시 프록시를 우회하여 AOP 미적용                |
| ❌ 단점   | **메서드 실행만 지원**           | 필드 접근, 생성자 호출 등은 지원하지 않음                            |
| ❌ 단점   | **런타임 오버헤드**             | 프록시 객체 생성과 메서드 인터셉션에 따른 성능 비용 (호출당 ~500ns)         |
| ❌ 단점   | **암묵적 동작**               | 코드만 봐서는 AOP가 적용되는지 알기 어려움 ("마법" 같은 느낌)             |

### ⚖️ Trade-off 분석

```
코드 깔끔함  ◄─────────── Trade-off ───────────►  디버깅 복잡도
선언적 편의  ◄─────────── Trade-off ───────────►  암묵적 동작
런타임 유연성 ◄─────────── Trade-off ───────────►  런타임 오버헤드
Spring 통합  ◄─────────── Trade-off ───────────►  Spring 종속성
```

---

## 6️⃣ 위빙(Weaving)과 Spring AOP vs AspectJ

### 위빙이란?

**위빙 = "원래 코드에 AOP 코드를 끼워 넣는 것"** — 비유: 직조(옷감 짜기)에서 세로 실(비즈니스 로직)에 가로 실(AOP 코드)을 엮는 것.

### 4가지 위빙 시점

```
  .java        .class          JVM에 로딩       실행
  소스코드   → 바이트코드   →   메모리         → 런타임
    │            │               │               │
    ▼            ▼               ▼               ▼
 ┌──────┐   ┌──────────┐   ┌──────────┐   ┌─────────┐
 │ CTW  │   │Post-CTW  │   │  LTW     │   │Spring   │
 │컴파일 │   │포스트    │   │ 로드타임  │   │AOP      │
 │타임   │   │컴파일    │   │          │   │런타임   │
 │위빙   │   │위빙      │   │  위빙    │   │위빙     │
 └──────┘   └──────────┘   └──────────┘   └─────────┘
 AspectJ     AspectJ        AspectJ        Spring
 컴파일러    컴파일러        Agent          Proxy
```

| 위빙 시점       | 약어                            | 언제?                        | 방식                                |
| ----------- | ----------------------------- | -------------------------- | --------------------------------- |
| **컴파일타임**   | CTW (Compile-Time Weaving)    | `.java` → `.class` 할 때     | AspectJ 컴파일러(ajc)가 소스에 AOP 코드 직접 삽입 |
| **포스트컴파일**  | Post-CTW                      | 이미 만들어진 `.class`/`.jar`에   | 남이 만든 라이브러리 바이트코드에도 AOP 삽입 가능     |
| **로드타임**    | LTW (Load-Time Weaving)       | JVM이 클래스를 메모리에 올릴 때        | Java Agent가 로딩 과정에서 바이트코드 변환       |
| **런타임**     | Runtime Weaving               | 프로그램 실행 중                  | Spring이 프록시 객체를 만들어서 감싸기           |

### "순수 Java"인데 AspectJ 어노테이션 쓰는 이유

**Spring AOP는 AspectJ의 "어노테이션 문법(레시피)"만 빌려 쓰고, 실행은 자체 프록시 방식(주방)으로 한다.**

```
┌──────────────────┐    ┌──────────────────┐
│    AspectJ       │    │   Spring AOP     │
│                  │    │                  │
│ 어노테이션: ✅    │    │ 어노테이션: ✅   │ ← 같음!
│ @Aspect, @Before │    │ @Aspect, @Before │
│ @Around          │    │ @Around          │
│                  │    │                  │
│ 실행방식:        │    │ 실행방식:        │ ← 다름!
│ 바이트코드 수정   │    │ 프록시 객체      │
│ (ajc 컴파일러)   │    │ (JDK/CGLIB)     │
└──────────────────┘    └──────────────────┘
```

```java
// 이 import들은 AspectJ 라이브러리에서 왔지만:
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Before;
import org.aspectj.lang.ProceedingJoinPoint;

// 실행은 Spring이 프록시로 처리!
// AspectJ 컴파일러(ajc)는 전혀 사용하지 않음!
```

### 📊 Spring AOP vs AspectJ 비교 매트릭스

| 비교 기준          | Spring AOP                  | AspectJ                        |
| -------------- | --------------------------- | ------------------------------ |
| **위빙 방식**      | 런타임 (프록시)                   | 컴파일타임 / 로드타임 / 포스트컴파일          |
| **JoinPoint**  | 메서드 실행만                     | 메서드, 생성자, 필드, 초기화 등 모두         |
| **적용 대상**      | Spring Bean만                | 모든 Java 객체                     |
| **프록시 필요**     | 필수 (JDK / CGLIB)            | 불필요 (바이트코드 직접 변경)               |
| **Self-invocation** | ❌ 미지원                       | ✅ 지원                           |
| **성능**         | 호출당 ~500ns 오버헤드             | 오버헤드 거의 0 (컴파일 시 위빙 완료)        |
| **설정 복잡도**     | 낮음 (어노테이션만)                 | 높음 (AspectJ 컴파일러 필요)           |
| **학습 곡선**      | 낮음                          | 높음                             |

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ Self-invocation (자기 호출) 문제

**같은 클래스 안에서 `this.method()`로 호출하면 프록시를 건너뛰어 AOP가 적용되지 않는 현상.**

```
━━ 정상 호출 (외부에서) ━━━━━━━━━━━━━━━━━━━━━━━━
  OrderService → UserService.getUser()

  [외부]  →  📱매니저(Proxy)  →  🧑연예인(Target)
              ✅ AOP 적용됨!

━━ Self-invocation (내부에서) ━━━━━━━━━━━━━━━━━━
  UserService.methodA() → this.methodB()

  🧑연예인이 직접 자기 메서드 호출 → 📱매니저 안 거침!
              ❌ AOP 적용 안 됨!
```

```java
@Service
public class UserService {
    @Transactional
    public void methodA() {
        this.methodB();  // ⚠️ Self-invocation!
        //   ↑ this = 진짜 객체 (프록시가 아님!)
        //   → methodB의 @Transactional이 작동하지 않음!
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void methodB() {
        // 새 트랜잭션을 기대하지만... 안 열림! 😱
    }
}
```

#### 해결 방법

| 방법                  | 설명                       | 추천도                    |
| ------------------- | ------------------------ | ---------------------- |
| 1. **빈 분리**         | methodB를 다른 클래스로 이동      | ⭐⭐⭐ (Spring 공식 권장)    |
| 2. **Self-injection** | 자기 자신을 주입받아 프록시로 호출      | ⭐⭐                     |
| 3. **AspectJ CTW/LTW** | 프록시 대신 바이트코드 위빙 사용       | ⭐ (설정 복잡)              |

### ⚠️ 기타 흔한 실수

| #   | 실수                            | 왜 문제인가                                                      | 올바른 접근                             |
| --- | ----------------------------- | ----------------------------------------------------------- | ---------------------------------- |
| 1   | **private 메서드에 AOP 적용**       | Spring은 설계상 public 메서드만 인터셉트 (CGLIB은 기술적으로 protected 가능하나 Spring이 일관성 위해 제한) | `@Transactional`, `@Cacheable` 등은 반드시 public 메서드에 |
| 2   | **`@EnableAspectJAutoProxy` 누락** | Aspect가 등록되지 않아 아무 동작도 안 함                                  | Spring Boot는 자동 설정되지만, 수동 설정 시 반드시 추가 |
| 3   | **Aspect 실행 순서 미지정**          | 여러 Aspect가 예측 불가능한 순서로 실행                                   | `@Order` 어노테이션으로 명시적 순서 지정          |
| 4   | **`@Around`에서 `proceed()` 누락** | 원본 메서드가 실행되지 않음                                             | `proceed()` 호출을 반드시 포함              |

### 🚫 Anti-Patterns

1. **AOP 남용 (Aspect Overload)**: 모든 것을 AOP로 해결하려 하면 코드 흐름이 불투명해지고 디버깅이 극도로 어려워진다. AOP는 **진정한 횡단 관심사**에만 사용할 것
2. **비즈니스 로직을 Advice에 삽입**: Advice에 비즈니스 판단 로직을 넣으면 관심사 분리의 목적이 무색해진다. Advice는 **인프라 관심사**만 담당

### 🔒 보안/성능/Virtual Thread 고려사항

- **보안**: AOP 기반 보안(`@PreAuthorize`)은 프록시를 우회하면 무력화됨. 내부 호출 경로를 반드시 확인
- **성능**: 프록시 생성은 애플리케이션 시작 시 한 번만 발생하지만, 매 메서드 호출마다 인터셉션 체인을 통과하므로 **초고빈도 호출 메서드**에는 주의
- **Virtual Thread (Java 21+)**: ThreadLocal 기반으로 컨텍스트를 전달하는 Aspect(MDC, 보안 컨텍스트 등)는 가상 스레드 환경에서 예상대로 동작하지 않을 수 있다. `ScopedValue`(Java 21+) 또는 Micrometer Tracing 사용을 권장

---

## 8️⃣ 언제 무엇을 선택? — AspectJ가 필요한 경우

### 필드 접근 인터셉션

**변수(필드)를 읽거나 쓸 때 가로채는 것.** Spring AOP는 프록시 기반이라 메서드만 가로챌 수 있고, 필드 접근은 AspectJ만 가능.

```java
// AspectJ에서만 가능 (Spring AOP ❌):
@Before("get(private String User.name)")
public void beforeFieldRead() {
    log.info("누군가 name 필드를 읽고 있어!");
}
```

비유: Spring AOP = "일기장을 **열고 닫을 때**(메서드)만 감시". AspectJ = "일기장 **안에 글을 쓰거나 읽을 때**(필드)까지 감시 및 변환 가능".

### 도메인 객체에 대한 세밀한 위빙

**`new`로 직접 만드는 비즈니스 객체(Spring Bean이 아닌 것)에도 AOP를 적용하는 것.**

```
Spring이 관리하는 Bean              new로 만드는 도메인 객체
(Spring AOP ✅ 적용 가능)          (Spring AOP ❌ 불가)

@Service UserService                Order order = new Order()
@Controller UserController          Money money = new Money(100)
@Repository UserRepo                Address addr = new Address()

IoC Container가 관리               개발자가 직접 관리
→ 프록시 감싸기 가능                → 프록시 감싸기 불가
```

AspectJ는 컴파일 시점에 바이트코드를 수정하므로 `new`로 만든 객체의 메서드에도 AOP 코드가 이미 삽입되어 있다.

### 성능: 현실적 판단

```
일반적인 API 서버 요청 처리 시간 분해:

  네트워크 I/O    :  ████████████████  50ms
  DB 쿼리         :  ██████████       30ms
  비즈니스 로직    :  ████             10ms
  직렬화/역직렬화  :  ██               5ms
  AOP 프록시 오버헤드: ▏              ~0.0005ms (500ns)

  → API 서버 기준 무시 가능 수준
```

```
성능 민감도 스펙트럼:

  일반 웹앱          고성능 API        극한 저지연 (HFT)
  ◄────────────────────────────────────────────────►
  Spring AOP ✅      Spring AOP ✅     상황에 따라
  프록시 비용         여전히 무시 가능    AspectJ CTW 또는
  신경 안 써도 됨                       C/C++/Rust 선호
```

> ⚠️ HFT(High-Frequency Trading)에서도 Java를 사용하는 사례가 다수 존재한다 (GC 튜닝, Off-heap, AOT 컴파일, LMAX Disruptor 등). "극한 저지연이면 Java를 안 쓴다"는 절대적이지 않다.

### 🏆 AspectJ를 선택하는 현실적 이유 순위

```
1위: Self-invocation 해결이 꼭 필요할 때
2위: new로 만드는 객체에 AOP가 필요할 때
3위: 필드 접근을 가로채야 할 때
4위: 극한 저지연 시스템에서 프록시 오버헤드조차 허용 불가할 때
```

대부분의 일반적인 엔터프라이즈 애플리케이션에서는 Spring AOP로 충분하다.

---

## 9️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형     | 이름                          | 링크/설명                                                                                                             |
| ------ | --------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| 📖 공식 문서 | Spring AOP Reference        | [Spring Framework Docs](https://docs.spring.io/spring-framework/reference/core/aop.html)                          |
| 📖 공식 문서 | AOP Capabilities & Goals    | [Spring AOP Goals](https://docs.spring.io/spring-framework/reference/core/aop/introduction-spring-defn.html)      |
| 📘 도서   | *Spring in Action* (Craig Walls) | AOP 챕터가 실무 중심으로 잘 정리됨                                                                                             |
| 📘 도서   | *Pro Spring 6* (Iuliana Cosmina) | AOP 내부 동작까지 깊이 다룸                                                                                                 |
| 📺 영상   | Baeldung Spring AOP Guide   | [Baeldung](https://www.baeldung.com/spring-aop) — 코드 예시 풍부                                                        |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리                | 용도                        |
| ----------------------- | ------------------------- |
| **Spring AOP**          | 런타임 프록시 기반 AOP             |
| **AspectJ**             | 완전한 AOP 프레임워크 (컴파일 타임)    |
| **Spring Boot Actuator** | AOP와 결합한 메트릭/모니터링          |
| **Micrometer**          | `@Timed` 어노테이션으로 AOP 기반 성능 측정 |

### 🔮 트렌드 & 전망

- **Spring Boot 자동 설정 강화**: AOP 설정이 점점 더 자동화되어 개발자 부담 감소
- **GraalVM Native Image 지원**: Spring AOT 컴파일과 AOP의 호환성 개선 진행 중. 단 커스텀 Aspect는 reflection hint 설정 등 추가 구성이 필요
- **Observability 통합**: Spring 6.0+의 ObservationRegistry + OpenTelemetry가 기존 커스텀 AOP 모니터링을 대체하는 추세
- **Virtual Thread 적응**: Java 21+ 가상 스레드 도입으로 ThreadLocal 기반 Aspect 패턴의 재설계 필요. `ScopedValue` 전환 추세

### 💬 커뮤니티 인사이트

- **Self-invocation은 가장 자주 겪는 함정**: `@Transactional`이 동작하지 않아 당황하는 개발자가 많으며, Spring 공식 문서도 "코드를 리팩토링하여 self-invocation을 피하라"고 권장
- **"AOP는 양날의 검"**: 잘 쓰면 코드가 깔끔해지지만, 남용하면 "보이지 않는 코드"가 되어 팀 내 디버깅 비용이 크게 증가

---

## 📎 Sources

1. [Spring AOP Capabilities and Goals — Spring Framework Docs](https://docs.spring.io/spring-framework/reference/core/aop/introduction-spring-defn.html) — 공식 문서
2. [Proxying Mechanisms — Spring Framework Docs](https://docs.spring.io/spring-framework/reference/core/aop/proxying.html) — 공식 문서
3. [Spring Blog - Debunking Myths: Proxies Impact Performance](https://spring.io/blog/2007/07/19/debunking-myths-proxies-impact-performance/) — 성능 벤치마크
4. [Understanding AOP in Spring: from Magic to Proxies — Medium/Trabe](https://medium.com/trabe/understanding-aop-in-spring-from-magic-to-proxies-6f5911e5e5a8) — 기술 블로그
5. [Spring Proxy and Internal Working of AOP — Coding Shuttle](https://www.codingshuttle.com/spring-boot-handbook/spring-proxy-and-internal-working-of-aop/) — 기술 블로그
6. [Mastering Spring AOP: Real-World Use Cases — DEV Community](https://dev.to/haraf/mastering-spring-aop-real-world-use-case-and-practical-code-samples-5859) — 커뮤니티
7. [Choosing which AOP Declaration Style to Use — Spring Framework](https://docs.spring.io/spring-framework/reference/core/aop/choosing.html) — 공식 문서
8. [Solving the Self-Invocation Issue — Medium](https://medium.com/@CodeWithTech/solving-the-self-invocation-issue-in-spring-why-your-annotations-might-not-work-3c9eb553f146) — 커뮤니티

---

## 📋 핵심 정리

1. **Spring AOP = 프록시 기반 런타임 AOP**. 별도 컴파일러 없이 Spring Bean의 메서드 실행을 인터셉트한다.
2. **프록시 2가지**: JDK Dynamic Proxy(인터페이스 기반) vs CGLIB(서브클래스 기반). Spring Boot 2.0+는 CGLIB가 기본.
3. **동작 원리**: IoC Container가 빈 생성 시 Pointcut 매칭 → 프록시 생성 → 원본 빈 대신 프록시 등록 → 런타임 인터셉션.
4. **핵심 구성요소**: Aspect(모듈) > Pointcut(어디에) + Advice(무엇을) → JoinPoint(실행 지점)에 적용.
5. **Advice 5종류**: @Before, @After, @AfterReturning, @AfterThrowing, @Around. @Around가 가장 강력하나 가능하면 구체적 Advice를 사용.
6. **@Pointcut**은 "어디에 AOP를 적용할지" 필터 규칙이며 별명(메서드명)으로 재사용 가능.
7. **ProceedingJoinPoint**는 @Around 전용 리모컨. `proceed()`로 원본 메서드를 실행.
8. **Self-invocation**: 같은 클래스 내 `this.method()` 호출 시 프록시 우회 → AOP 미적용. 가장 흔한 함정.
9. **AspectJ 어노테이션을 빌려 씀**: `@Aspect`, `@Before` 등은 AspectJ 라이브러리이지만, 실행은 Spring 프록시.
10. **AspectJ 선택 이유**: Self-invocation 해결 > 도메인 객체 AOP > 필드 인터셉션 > 극한 성능. 대부분의 엔터프라이즈에서는 Spring AOP로 충분.
11. **성능 오버헤드**: 프록시 호출당 ~500ns. 일반 API 서버에서는 무시 가능 수준.
12. **@Order(숫자)**: 여러 Aspect의 실행 순서 제어. 숫자 작을수록 먼저. 미지정 시 순서 보장 안 됨.
