---
tags: [kotlin, coroutine, java, virtual-thread, platform-thread, concurrency, jvm, jdk25, loom]
created: 2026-05-01
---

# 📖 Kotlin Coroutine vs Java Thread/Virtual Thread — Concept Deep Dive

> 💡 **한줄 요약**: 동일한 IO 대기 문제를 풀기 위해 **Java Platform Thread (OS 스레드)** → **Virtual Thread (JVM 런타임 가상화, JDK 21+)** → **Kotlin Coroutine (컴파일러 상태머신 변환)** 순으로 점점 더 가벼운 추상화를 채택해 왔다. 2026년 기준 JDK 24/25에서 `synchronized` pinning이 사라지면서 세 모델의 실무 격차가 크게 좁혀졌다.

> 🧒 **12살 비유**: 식당에서 손님(요청)이 음식(IO 결과)을 기다리는 상황을 떠올려 보자.
> - **Platform Thread**: 손님 1명에 직원 1명이 **계속 옆에 서서 대기** (인건비 폭발) 💸
> - **Virtual Thread**: 직원이 주문만 받고 **다른 테이블 응대하러 감**. 음식 나오면 알람이 울림 🔔 (식당이 자동으로 돌려줌)
> - **Coroutine**: 직원이 메모지(Continuation)에 "이 테이블은 음식 1번 다음에 음료 2번"이라고 적어두고 떠남. 음료가 준비되면 **메모지 보고 이어서** 응대 📝

---

## 1️⃣ 무엇인가? (What is it?)

세 가지 모두 **동시성(Concurrency)** 을 처리하는 단위지만, 추상화 레벨이 다르다.

| 기술 | 정의 | 등장 시기 | 관리 주체 |
|------|------|----------|----------|
| **Platform Thread** (Java Thread) | OS (Operating System) 커널 스레드와 1:1 매핑된 JVM (Java Virtual Machine) 스레드 | Java 1.0 (1996) | OS 커널 |
| **Virtual Thread** (Project Loom) | JVM 런타임이 관리하는 경량 스레드. M:N 모델로 Carrier(OS) 스레드 위에 다중화 | JDK 21 (2023) GA, JDK 25 (2026) LTS (Long Term Support) | JVM 런타임 |
| **Kotlin Coroutine** | 컴파일러가 `suspend` 함수를 상태머신으로 변환한 중단/재개 가능한 실행 단위 | Kotlin 1.3 (2018) Stable | Kotlin 라이브러리 + 컴파일러 |

> 📌 **핵심 키워드**: `M:N 스케줄링`, `Continuation`, `Carrier Thread`, `Mount/Unmount`, `CPS (Continuation Passing Style)`, `Pinning`, `구조화된 동시성 (Structured Concurrency)`

**왜 등장했나? — 등장 배경**

```
1996: Java Thread = OS Thread. C10K 문제 직면 (스레드 1만개 = 10GB RAM)
        ↓
2018: Kotlin Coroutine. 언어 차원에서 상태머신으로 해결
        ↓
2023: Project Loom (JEP 444). Java도 런타임 차원에서 Virtual Thread 도입
        ↓
2024: JEP 491 (JDK 24). synchronized pinning 해소 — VT 실용성 도약
        ↓
2025: JDK 25 LTS. JEP 491 LTS 채택, Structured Concurrency 5th Preview (JEP 505)
```

---

## 2️⃣ 핵심 개념 (Core Concepts)

### 🧱 추상화 레이어 비교

```
┌────────────────────────────────────────────────────────────────────┐
│                        Application Code                             │
└────────────────────────────────────────────────────────────────────┘
       Kotlin Coroutine          Virtual Thread          Platform Thread
              │                        │                        │
              ▼                        ▼                        │
┌─────────────────────────┐ ┌──────────────────────┐            │
│ Continuation 객체        │ │ JVM Continuation API │            │
│ (compiler-generated      │ │ (jdk.internal.vm)    │            │
│  state machine)          │ │                      │            │
└──────────┬──────────────┘ └──────────┬───────────┘            │
           │                            │                        │
           ▼                            ▼                        ▼
┌────────────────────────────────────────────────────────────────────┐
│                  ForkJoinPool / Carrier Thread                      │
│                  (= 결국 Platform Thread)                            │
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                          OS Kernel Thread                            │
└────────────────────────────────────────────────────────────────────┘
```

> 🔑 **핵심**: Coroutine과 Virtual Thread는 **결국 Platform Thread 위에서 돌아간다**. 차이는 "어디서 중단/재개를 처리하는가"이다.
> - Coroutine → **컴파일 시점**에 `suspend` 함수를 상태머신으로 변환 → 라이브러리 레벨
> - Virtual Thread → **런타임 시점**에 JVM이 mount/unmount → JVM 레벨
> - Platform Thread → **OS 커널**이 컨텍스트 스위치 → 커널 레벨

### 📦 메모리 풋프린트

| 구성 요소 | Platform Thread | Virtual Thread | Coroutine |
|-----------|-----------------|---------------|-----------|
| 스택 위치 | OS 커널 (전용 영역) | JVM heap (stack chunk 객체) | JVM heap (Continuation 객체) |
| 기본 크기 | 약 1 MB (`-Xss` 기본값) | 수 KB (가변) | ~1.5–2.5 KB (CPS 변환 결과) |
| 10만 개 띄우면 | ~100 GB RAM 필요 → OOM (Out Of Memory) | ~수백 MB | ~수백 MB |
| 메모리 비율 | 1× (기준) | ~1/100–1/123 | ~1/400–1/500 |

### ⚙️ 구성 요소

| 용어 | 역할 | 비유 |
|------|------|------|
| **Carrier Thread** | Virtual Thread를 실제로 실행할 OS 스레드 (기본 ForkJoinPool) | 택배 트럭 🚚 |
| **Mount** | Virtual Thread가 Carrier에 "올라타는" 상태 | 트럭에 짐 싣기 |
| **Unmount** | Virtual Thread가 IO 대기로 Carrier에서 "내려가는" 상태 | 짐 내려놓고 트럭은 다른 일 |
| **Continuation** | "어디까지 실행했는지"를 저장한 객체 | 책갈피 📑 |
| **CPS Transformation** | Kotlin 컴파일러가 suspend → state machine으로 변환 | 책을 챕터별로 잘라 책갈피 끼우기 |
| **Dispatcher** | Coroutine을 어떤 스레드에서 실행할지 결정 | 디스패처 (택시 콜센터) |

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

### 🏗️ Platform Thread 동작

```
[App] → Thread.start()
         ↓
       JVM → OS (pthread_create / CreateThread)
         ↓
       OS Kernel Thread 생성 (1MB stack 할당)
         ↓
[App 코드 실행]
         ↓
       IO 호출 → 시스템콜 → 스레드 BLOCKED 상태
         ↓
       OS 스케줄러가 다른 스레드로 컨텍스트 스위치
       (레지스터 저장 + 캐시 무효화 = 수~수십 µs 비용)
         ↓
       IO 완료 → 스레드 RUNNABLE → CPU 할당 받으면 재개
```

⚠️ **약점**: 1만 동시 요청 = 1만 스레드 = 10GB RAM. OS 스레드는 비싸다.

### 🏗️ Virtual Thread 동작 (JEP 444)

```
[App] → Thread.ofVirtual().start(Runnable)
         ↓
       JVM이 Virtual Thread 객체 생성 (heap에 stack chunk)
         ↓
       Carrier Thread (ForkJoinPool worker) 위에 mount
         ↓
[App 코드 실행]
         ↓
       IO 호출 (java.net, java.nio, JDBC, ...)
         ↓
       JVM이 감지 → Virtual Thread를 Carrier에서 unmount
       (Continuation으로 저장)
         ↓
       Carrier는 다른 Virtual Thread mount해서 실행
         ↓
       IO 완료 → Virtual Thread를 ForkJoinPool 큐에 재등록
         ↓
       다음에 빈 Carrier에 mount되어 재개
```

> 🎯 **핵심**: 개발자는 그냥 **`Thread`처럼 쓰면** 된다. JVM이 알아서 mount/unmount 한다.

### 🏗️ Kotlin Coroutine 동작 (CPS 변환)

```kotlin
// 개발자가 쓰는 코드
suspend fun fetchUserAndOrder(id: Long): Pair<User, Order> {
    val user = fetchUser(id)       // 중단점 1
    val order = fetchOrder(user)   // 중단점 2
    return Pair(user, order)
}

// 컴파일러가 변환한 실제 코드 (의사코드)
fun fetchUserAndOrder(id: Long, $completion: Continuation<Pair<User,Order>>): Any? {
    class StateMachine: ContinuationImpl(...)  // 상태 + 로컬변수 저장
    val state = ($completion as? StateMachine) ?: StateMachine($completion)
    when (state.label) {
        0 -> {
            state.label = 1
            val r = fetchUser(id, state)
            if (r === COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED  // 중단!
            state.user = r as User
            // fall through
        }
        1 -> {
            state.label = 2
            val r = fetchOrder(state.user, state)
            if (r === COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            state.order = r as Order
        }
        2 -> return Pair(state.user, state.order)
    }
}
```

### 🔄 IO 발생 시 흐름 비교 (Step by Step)

```
                        [같은 IO 시나리오: DB 쿼리 100ms 대기]

Platform Thread:
  1. Thread-1이 JDBC executeQuery() 호출
  2. 시스템콜 → Thread-1 BLOCKED 상태
  3. OS가 Thread-1을 wait queue로 이동 (스택 1MB 그대로 점유 ❌)
  4. 100ms 후 IO 완료 → Thread-1 RUNNABLE → 컨텍스트 스위치 비용 발생

Virtual Thread (JDK 21+):
  1. VThread-1이 JDBC executeQuery() 호출 (블로킹 호출 그대로)
  2. JVM이 감지 → VThread-1 Continuation 저장 → Carrier에서 unmount
  3. Carrier Thread는 즉시 VThread-2 mount하여 실행 (낭비 0)
  4. 100ms 후 IO 완료 → VThread-1 ForkJoinPool 큐 재등록 → 빈 Carrier에 mount → 재개

Kotlin Coroutine:
  1. Coroutine-A가 suspend fun executeQuery() 호출
  2. Continuation에 state=1, 로컬변수 저장 → 스레드 반납
  3. Dispatcher 스레드는 즉시 Coroutine-B 실행 (낭비 0)
  4. 100ms 후 IO 완료 → Continuation.resume() → Dispatcher 큐 재등록 → 재개
```

> 💡 **결론**: VT와 Coroutine은 동일한 원리(중단점에서 스레드 반납)를 **다른 레이어**(JVM vs 컴파일러)에서 구현한 것.

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| # | 시나리오 | 추천 기술 | 이유 |
|---|---------|----------|------|
| 1 | 기존 Spring MVC + JPA 레거시 동시성 향상 | ✅ **Virtual Thread** | 코드 변경 없이 `spring.threads.virtual.enabled=true` 한 줄 |
| 2 | 신규 Kotlin/Spring 서비스, 복잡한 병렬 IO | ✅ **Coroutine** | `async/await` 자연스러움, 구조화된 동시성 기본 제공 |
| 3 | CPU 집약 작업 (이미지 처리, 인코딩) | ✅ **Platform Thread** (Fixed Pool) 또는 `Dispatchers.Default` | 중단점이 없어 가상화 의미 없음 |
| 4 | Android UI 이벤트 핸들링 | ✅ **Coroutine** (`Dispatchers.Main`) | 생명주기 연동(`viewModelScope`), 자동 취소 |
| 5 | 1만+ 동시 WebSocket 연결 | ✅ **Coroutine** 또는 **Virtual Thread** | Platform Thread는 OOM |
| 6 | gRPC 스트리밍 서버 | ✅ **Coroutine** (`Flow`) | 백프레셔 자동 처리 |
| 7 | 외부 API 5개 병렬 호출 | ✅ **Coroutine** (`async`) 또는 **VT + StructuredTaskScope** | 둘 다 적합 |

### ✅ 베스트 프랙티스

1. **Virtual Thread는 "한 작업당 한 스레드(thread-per-task)"로 사용**: 풀링하지 말 것 (가벼우니 매번 생성). `Executors.newVirtualThreadPerTaskExecutor()` 사용.
2. **`synchronized` 대신 `ReentrantLock` 권장 (JDK 23 이하)**: JDK 24+에서는 JEP 491로 해소되었지만, JDK 21–23 환경에서는 여전히 pinning 위험. (단, JDK 24/25 사용 중이라면 `synchronized`도 안전)
3. **Coroutine은 `withContext(Dispatchers.IO)`로 블로킹 분리**: JDBC 같은 블로킹 코드는 IO Dispatcher에서.
4. **CPU 작업은 `Dispatchers.Default`, IO는 `Dispatchers.IO`**: 잘못 섞으면 starvation 발생.
5. **구조화된 동시성 사용**: Coroutine은 `coroutineScope { }`, VT는 `StructuredTaskScope` (JDK 25 5th Preview).
6. **VT 환경에서 JNI/native 호출 주의**: pinning 잔존 케이스 (JDK 25에서도).

### 🏢 실제 적용 사례

- **Netflix**: Coroutine을 GraphQL 서버에 도입. RxJava 대비 가독성/유지보수성 개선 ([Netflix Tech Blog](https://netflixtechblog.com/))
- **JetBrains**: IntelliJ IDEA에 Virtual Thread 채택 (백그라운드 인덱싱)
- **Spring Boot 3.2+**: `spring.threads.virtual.enabled=true` 한 줄로 VT 적용
- **Helidon, Quarkus**: VT 기본 모드 지원
- **Android Jetpack**: Coroutine이 사실상 표준 (LiveData → Flow 마이그레이션 중)

---

## 5️⃣ 장점과 단점 (Pros & Cons)

### Platform Thread

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ | 호환성 | 모든 자바 코드와 호환, 디버깅 도구 성숙 |
| ✅ | 진정한 병렬성 | OS 스케줄러가 멀티코어 자동 활용 |
| ❌ | 무거움 | ~1MB stack, 1만 개 = 10GB |
| ❌ | 컨텍스트 스위치 비용 | 수~수십 µs (커널 진입) |
| ❌ | C10K 한계 | 동시 요청 폭증 시 OOM |

### Virtual Thread

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ | 코드 변경 0 | 기존 블로킹 코드 그대로 사용 가능 |
| ✅ | 가벼움 | ~수 KB, 100만 개도 가능 |
| ✅ | 디버깅 친화적 | 일반 스레드처럼 보이고 stack trace도 정상 |
| ✅ | JEP 491 (JDK 24+) | `synchronized` pinning 해소 — 대부분의 레거시 안전 |
| ❌ | 잔존 pinning | JDK 25에서도 native 코드 + 블로킹 콜백, class initializer는 pinning |
| ❌ | 진짜 CPU 작업엔 무용 | 중단점이 없으면 효과 없음 |
| ❌ | ThreadLocal 남용 시 메모리 폭발 | 100만 VT × 큰 ThreadLocal = OOM |

### Kotlin Coroutine

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ | 가장 가벼움 | ~1.5–2.5 KB |
| ✅ | 구조화된 동시성 기본 | `coroutineScope`, 자동 취소/예외 전파 |
| ✅ | 명시적 중단점 | `suspend` 키워드로 컴파일러가 잘못된 호출 차단 |
| ✅ | `Flow`/`Channel` | 스트리밍/백프레셔 1급 시민 |
| ❌ | 학습 곡선 | suspend, scope, dispatcher, 구조화된 동시성 등 개념 다수 |
| ❌ | 라이브러리 호환성 | JPA, JDBC 등 블로킹 라이브러리는 `Dispatchers.IO`로 우회 |
| ❌ | Coroutine ↔ Java 상호운용 | `runBlocking`, `Future`/`CompletableFuture` 변환 필요 |

### ⚖️ Trade-off 분석

```
        단순함 / 호환성              제어력 / 안전성
Platform Thread ──── VT ──── Coroutine
       무거움          중간          가벼움
       OS 의존         JVM 의존     컴파일러 의존
       암묵적 동시성   암묵적 동시성  명시적 중단점
```

---

## 6️⃣ 차이점 비교 (Comparison) ⭐ 핵심 섹션

### 📊 전체 비교 매트릭스

| 비교 기준 | Platform Thread | Virtual Thread | Kotlin Coroutine |
|-----------|----------------|----------------|------------------|
| **추상화 레벨** | OS 커널 | JVM 런타임 | 컴파일러 + 라이브러리 |
| **메모리/단위** | ~1 MB | ~수 KB | ~1.5–2.5 KB |
| **생성 비용** | ~50 µs (시스템콜) | ~수 µs | ~수백 ns |
| **컨텍스트 스위치 비용** | 1–10 µs (커널) | ~수백 ns (mount/unmount) | ~수십–수백 ns (state 전환) |
| **최대 동시 개수** | ~수천 (RAM 한계) | 100만+ | 100만+ |
| **스케줄링 주체** | OS (Preemptive) | JVM (Cooperative + IO 감지) | Dispatcher (Cooperative) |
| **선점형 여부** | ✅ 선점형 | ❌ 비선점형 (CPU 작업 시 yield 필요) | ❌ 비선점형 |
| **블로킹 IO 처리** | 스레드 통째로 블록 | JVM이 unmount | suspend 함수에서 중단 |
| **병렬성 (멀티코어)** | OS 자동 | ForkJoinPool worker 수만큼 | Dispatcher worker 수만큼 |
| **취소 메커니즘** | `interrupt()` (협조적) | `interrupt()` (협조적) | `cancel()` + 구조화된 전파 |
| **구조화된 동시성** | 없음 | `StructuredTaskScope` (JDK 25 5th Preview) | `coroutineScope { }` (Stable, 언어 표준) |
| **에러 처리** | `try-catch` + `Thread.UncaughtExceptionHandler` | `try-catch` + `StructuredTaskScope` | `try-catch` + `SupervisorJob`/`CoroutineExceptionHandler` |
| **디버깅** | 일반 stack trace | 일반 stack trace (VT-aware) | suspension stack trace 별도 (`-Dkotlinx.coroutines.debug`) |
| **기존 코드 호환** | ✅ 완전 호환 | ✅ 완전 호환 | ❌ `suspend` 변경 필요 |
| **학습 비용** | 낮음 | 매우 낮음 (Thread API 그대로) | 높음 |
| **GA 시점** | Java 1.0 (1996) | JDK 21 (2023) | Kotlin 1.3 (2018) |

### 🔍 핵심 차이 요약

```
Platform Thread          Virtual Thread          Kotlin Coroutine
═══════════════════      ═══════════════════     ═══════════════════
OS가 관리                 JVM이 관리               컴파일러가 변환
1:1 OS 매핑              M:N (Carrier 위 다중화)  N:1 (Dispatcher 풀)
Preemptive               Cooperative + IO 자동    Cooperative (suspend)
1MB stack                수 KB stack chunk        ~2KB Continuation
일반 코드                 일반 코드                suspend 함수
어디서든 블록             어디서든 블록 (VT 인식)   suspend에서만 중단
```

### 🤔 언제 무엇을 선택?

```
[선택 결정 트리]

CPU-bound 작업인가?
  └─ 예 → Platform Thread (Fixed Thread Pool, 코어 수만큼)
  └─ 아니오 → IO-bound
       │
       ├─ 기존 Java 레거시 코드 유지하고 싶은가?
       │   └─ 예 → Virtual Thread (JDK 21+)
       │       └─ JDK 24+ 가능? → ✅ synchronized OK (JEP 491)
       │       └─ JDK 21–23만? → ⚠️ ReentrantLock으로 변경 필요
       │
       ├─ Kotlin 스택이고 신규 프로젝트인가?
       │   └─ 예 → Coroutine (가장 표현력 높음, 구조화된 동시성)
       │
       └─ 복잡한 병렬 IO + 백프레셔 + 스트리밍?
           └─ Coroutine + Flow (VT는 백프레셔 1급 지원 없음)
```

### 💡 같은 작업, 세 가지 코드

```kotlin
// 1) Platform Thread
val executor = Executors.newFixedThreadPool(10)
val userFuture = executor.submit { userRepo.findById(id) }
val orderFuture = executor.submit { orderRepo.findById(id) }
Result(userFuture.get(), orderFuture.get())

// 2) Virtual Thread (JDK 21+)
val executor = Executors.newVirtualThreadPerTaskExecutor()
val userFuture = executor.submit { userRepo.findById(id) }
val orderFuture = executor.submit { orderRepo.findById(id) }
Result(userFuture.get(), orderFuture.get())

// 2-b) Virtual Thread + Structured Concurrency (JDK 25)
StructuredTaskScope.open<Any>().use { scope ->
    val user = scope.fork { userRepo.findById(id) }
    val order = scope.fork { orderRepo.findById(id) }
    scope.join()
    Result(user.get(), order.get())
}

// 3) Kotlin Coroutine
suspend fun getAll(id: Long) = coroutineScope {
    val user = async { userRepo.findById(id) }
    val order = async { orderRepo.findById(id) }
    Result(user.await(), order.await())
}
```

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|------|-----------|------------|
| 1 | Virtual Thread를 풀링 (`newFixedVirtualThreadPool` 같은 시도) | VT는 가벼우므로 작업당 1개 생성이 정석. 풀링 시 캐시 효과 미미 + 복잡도 증가 | `Executors.newVirtualThreadPerTaskExecutor()` |
| 2 | VT에서 `ThreadLocal` 남용 | 100만 VT × 큰 ThreadLocal → OOM | `ScopedValue` (JDK 21+ Preview, JDK 25 4th Preview) 사용 |
| 3 | Coroutine에서 동기 블로킹 함수 호출 (`Thread.sleep`) | Dispatcher 스레드 통째로 블록 → 다른 코루틴 starvation | `delay()` 사용 또는 `withContext(Dispatchers.IO)` |
| 4 | `runBlocking { }`을 메인 코드에 사용 | 스레드를 통째로 블록 → VT 위에서는 pinning과 유사한 효과 | `suspend main` 함수, 또는 진입점에서만 사용 |
| 5 | `GlobalScope.launch { }` 남용 | 부모 스코프 없음 → 누수 + 취소 불가 | `coroutineScope`, `viewModelScope`, 명시적 스코프 |
| 6 | `synchronized` 안에서 블로킹 (JDK 21–23) | Carrier Thread 째로 pinning → VT 이점 소실 | `ReentrantLock` 사용 또는 JDK 24+ 업그레이드 |
| 7 | CPU 작업을 `Dispatchers.IO`에서 실행 | IO 풀이 가득 차면 진짜 IO가 starve | `Dispatchers.Default` 사용 |
| 8 | VT를 CPU 집약 작업에 사용 | 중단점이 없어 unmount 안 됨 = Platform Thread와 동일 | Fixed Thread Pool 사용 |

### 🚫 Anti-Patterns

1. **VT를 Connection Pool 크기 산정 기준에 포함**: 기존 풀(HikariCP 등)은 Platform Thread 가정. VT 100만 × DB 커넥션 100만 시도 시 DB 폭사 → 풀 크기는 별도 산정.
2. **Coroutine을 모든 함수에 `suspend` 붙이기**: 진짜 중단점이 없는 함수는 `suspend` 불필요. 일반 함수로 충분.
3. **Reactive(WebFlux) + Virtual Thread 혼용**: 두 추상화가 충돌. WebFlux면 Reactive 끝까지, MVC면 VT 끝까지.
4. **VT에서 `Thread.currentThread().getName()`으로 라우팅**: VT 이름은 동적이며 carrier가 바뀜. 식별자 기반 라우팅에 부적합.

### 🔒 보안/성능 고려사항

- **DoS (Denial of Service) 위험**: VT/Coroutine은 너무 가벼워서 무제한 생성 시 다운스트림(DB, 외부 API)을 폭격할 수 있음 → **세마포어/레이트 리미터 필수**
- **Tail Latency 증가**: VT가 carrier 풀이 좁으면 IO 폭주 시 unmount 대기 큐가 길어져 P99 (99 percentile latency)가 튐 → carrier 수 (`-Djdk.virtualThreadScheduler.parallelism`) 모니터링
- **ThreadLocal 메모리 누수**: VT 100만 × 32KB ThreadLocal = 32 GB. ScopedValue 권장
- **Coroutine 누수**: cancel 없이 부모 스코프가 죽으면 자식이 살아있을 수 있음 → 구조화된 동시성으로 보호

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|------|------|----------|
| 📖 공식 JEP | [JEP 444](https://openjdk.org/jeps/444) | Virtual Threads (JDK 21 GA) |
| 📖 공식 JEP | [JEP 491](https://openjdk.org/jeps/491) | Synchronize Virtual Threads without Pinning (JDK 24) |
| 📖 공식 JEP | [JEP 505](https://openjdk.org/jeps/505) | Structured Concurrency 5th Preview (JDK 25) |
| 📖 공식 문서 | [Oracle Virtual Threads Guide](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html) | Oracle JDK 21 가이드 |
| 📖 공식 문서 | [Kotlin Coroutines](https://kotlinlang.org/docs/coroutines-overview.html) | JetBrains 공식 |
| 📘 도서 | "Kotlin Coroutines: Deep Dive" — Marcin Moskala | 코루틴 내부 동작 정리 |
| 📺 영상 | "Inside Java Newscast #80" — Java 24 Virtual Threads | JEP 491 해설 |
| 🎓 강의 | [Rock the JVM — Structured Concurrency in JDK 25](https://rockthejvm.com/articles/structured-concurrency-jdk-25) | JEP 505 실습 |

### 🛠️ 관련 도구 & 라이브러리

| 도구 | 용도 |
|------|------|
| `kotlinx.coroutines` | Kotlin Coroutine 표준 라이브러리 |
| `kotlinx.coroutines.flow` | Cold/Hot 스트림 |
| `kotlinx.coroutines.reactive` | Reactor/RxJava ↔ Coroutine 브리지 |
| `Executors.newVirtualThreadPerTaskExecutor()` | VT용 표준 Executor |
| `StructuredTaskScope` (JDK 25 Preview) | VT 구조화된 동시성 |
| JFR (Java Flight Recorder) | VT pinning 이벤트 모니터링 (`jdk.VirtualThreadPinned`) |
| `-Djdk.tracePinnedThreads=full` | VT pinning 디버깅 (JDK 21–23만 유효, JDK 24부터 제거) |
| Spring Boot 3.2+ `spring.threads.virtual.enabled=true` | Tomcat을 VT 모드로 |

### 🔮 트렌드 & 전망 (2026)

```
2023 ▶ JDK 21 LTS — Virtual Thread GA
2024 ▶ JDK 24 — JEP 491 (synchronized 해소)
2025 ▶ JDK 25 LTS — JEP 505 (Structured Concurrency 5th Preview)
2026 ▶ JEP 505 정식 채택 예상 + ScopedValue Stable 예상
       Spring Framework 7 — Virtual Thread first-class
       Kotlin 2.x — Coroutine 컴파일 최적화 지속

[큰 흐름]
- "단순한 동시성"은 VT가 표준이 되어가는 중 (Java 진영)
- "복잡한 병렬/스트리밍"은 Coroutine + Flow가 우위 (Kotlin 진영)
- 두 모델은 경쟁이 아닌 보완 관계로 자리잡음
```

### 💬 커뮤니티 인사이트

- **Kotlin Discussions 포럼**: "VT는 단순함을 주지만, 구조화된 동시성·취소 전파·Flow 같은 추상화는 여전히 코루틴이 우위"라는 공감대.
- **InfoQ (2024)**: "JEP 491은 VT 도입의 마지막 큰 장벽을 제거했다"고 평가.
- **Spring 팀**: 3.2부터 VT 옵션 제공, 그러나 "WebFlux/Coroutine과 혼용 금지"를 명시.

---

## 9️⃣ 면접 Q&A 10선 (Interview Q&A) ⭐ 추가 섹션

### Q1. Virtual Thread와 Kotlin Coroutine은 결국 같은 것 아닌가요?

**A.** 같은 문제(IO 대기 시 스레드 낭비)를 다른 레이어에서 푼다는 점에서 유사하지만, 본질적 차이가 있다.

- VT: **JVM 런타임**이 IO 호출을 가로채서 mount/unmount → 코드는 일반 스레드처럼 작성
- Coroutine: **컴파일러**가 `suspend` 함수를 상태머신으로 변환 → `suspend` 키워드로 중단 가능 지점이 컴파일 타임에 명시
- 결과적으로 VT는 "투명한 비동기", Coroutine은 "명시적 비동기". 명시성 덕분에 Coroutine은 구조화된 동시성/취소를 언어 표준으로 제공할 수 있다.

### Q2. Pinning이 무엇이며 JDK 24에서 어떻게 해결됐나요?

**A.** Pinning은 Virtual Thread가 Carrier Thread에서 unmount되지 못해 OS 스레드를 점유하는 현상이다.

- **JDK 21–23**: `synchronized` 블록 안에서 블로킹 IO 호출 시 발생. 모니터 락이 OS 스레드에 바인딩되어 있어 unmount 불가
- **JDK 24 (JEP 491)**: 모니터를 Virtual Thread ID 기준으로 추적하도록 JVM을 재구현 → `synchronized` pinning 해소
- **JDK 25**에서 잔존 케이스: ① native 코드 안에서 블로킹 콜백, ② class initializer 실행 중

### Q3. CompletableFuture와 Coroutine은 어떻게 다른가요?

**A.** 둘 다 비동기 표현 도구지만 추상화 수준이 다르다.

- `CompletableFuture`: **콜백 체인** (`thenApply`, `thenCompose`). 에러 처리 분기 복잡, "callback hell" 위험.
- Coroutine: **순차 코드처럼 작성** (`val u = fetchUser()`). suspend 함수가 자동으로 비동기 실행. 가독성·디버깅 우위.
- 또한 Coroutine은 **구조화된 동시성**으로 자식 작업의 자동 취소/예외 전파 보장. CF는 수동 관리.

### Q4. Virtual Thread를 풀링하면 안 되는 이유는?

**A.** VT의 핵심은 "생성/폐기가 거의 무료"라는 점이다.

- 풀링은 비싼 리소스(Platform Thread, DB Connection)를 재사용하기 위한 패턴
- VT는 ~수 KB로 가볍고 GC가 회수 → 풀링 캐시 효과 ≈ 0
- 오히려 풀링 시 작업 간 ThreadLocal 누수, 라이프사이클 추론 어려움
- 정석: **task-per-thread** = `Executors.newVirtualThreadPerTaskExecutor()`

### Q5. Coroutine의 `Dispatchers.IO`는 내부적으로 어떻게 동작하나요?

**A.** `Dispatchers.IO`는 단일 큐가 아닌 정교한 work-stealing 스케줄러다.

- 각 워커가 **로컬 큐**(LIFO 우선)를 보유, **글로벌 큐**도 1개
- 로컬 큐가 비면 다른 워커 큐에서 **stealing** (Go GMP에서 영감)
- 기본 풀 크기 = `max(64, CPU 코어 수)`. `Dispatchers.IO.limitedParallelism(n)`으로 조정 가능
- `Default`와 스레드 풀 공유 (논리 분리), 다만 `IO`는 **블로킹 가능 풀**로 동적 확장

### Q6. Spring MVC에서 VT를 켜면 모든 요청이 자동으로 동시 처리되나요?

**A.** 아니다. 동시성을 막는 다른 자원도 함께 봐야 한다.

- Tomcat의 thread-per-request 모델은 VT로 대체되어 "스레드 한계"는 사라진다
- 하지만 **HikariCP 커넥션 풀 크기**, **Redis/외부 API rate limit**, **DB 자체 커넥션 한도**가 여전히 병목
- 결과: VT를 켜도 DB 풀이 100이면 동시 100 쿼리만 처리. 초과는 HikariCP 큐 대기
- 따라서 VT 도입 시 **다운스트림 자원 재산정** 필수

### Q7. `suspend` 함수와 일반 함수의 컴파일 결과 차이는?

**A.** Kotlin 컴파일러는 suspend 함수에 **숨은 `Continuation` 파라미터**를 추가하고 본문을 **상태머신 (state machine)** 으로 변환한다 (CPS, Continuation Passing Style).

```kotlin
// 원본
suspend fun foo(x: Int): Int

// 컴파일 결과 (의사코드)
fun foo(x: Int, $completion: Continuation<Int>): Any?
// 반환값이 Any?인 이유: 실제 결과 또는 COROUTINE_SUSPENDED 마커
```

각 중단점에는 `label`(state)이 부여되어 `TABLESWITCH`로 분기되며, 로컬 변수는 Continuation 객체에 spilling된다.

### Q8. CPU 집약 작업에 Virtual Thread를 쓰면 어떻게 되나요?

**A.** 효과 없음. 오히려 손해.

- VT의 이점은 **IO 대기 시 unmount**에서 나옴
- CPU 작업은 중단점이 없어 unmount 안 됨 → Platform Thread와 동일
- 추가로 carrier(ForkJoinPool worker)를 점유 → 다른 VT가 실행 못 해 **starvation 위험**
- 정석: CPU 작업은 `Executors.newFixedThreadPool(N=코어수)` 또는 Coroutine `Dispatchers.Default`

### Q9. 구조화된 동시성(Structured Concurrency)이 왜 중요한가요?

**A.** "자식 작업의 생명주기를 부모에 묶어 누수와 미관측 예외를 막는다"는 원칙.

- **Unstructured (전통 방식)**: `Thread.start()`, `executor.submit()` → 부모가 죽어도 자식 살아남음 → leak
- **Structured (Coroutine `coroutineScope`, JDK 25 `StructuredTaskScope`)**:
  - 부모는 자식이 모두 끝날 때까지 대기
  - 자식 하나가 실패하면 형제 자동 취소
  - 예외가 부모로 자동 전파
- 결과: **리소스 누수 + 좀비 작업 + 미관측 에러** 3대 문제를 컴파일러/런타임이 차단

### Q10. 우리 팀이 신규 Kotlin/Spring 서비스를 만든다면 VT와 Coroutine 중 무엇을 선택해야 할까요?

**A.** "팀 역량"과 "동시성 복잡도"를 두 축으로 본다.

```
                    동시성 복잡도
                        ↑
  복잡 (병렬 IO,         │  ✅ Coroutine
  스트리밍, 백프레셔)    │  (Flow, async/await,
                        │   구조화된 동시성)
                        │
                        ├──────────────────→ 팀 역량
                        │
  단순 (CRUD,            │  ✅ Virtual Thread
   요청-응답)            │  (학습 비용 낮음,
                        │   기존 패턴 그대로)
```

- **VT 선택**: 팀이 Java 기반, 학습 비용 부담, MVC + JPA 패턴 유지, JDK 24+ 가능
- **Coroutine 선택**: Kotlin 능숙, 복잡한 IO 오케스트레이션, Android 공유 코드, Flow가 핵심
- **혼용 금지**: WebFlux + VT, Coroutine + VT(같은 핸들러 안에서)는 추상화 충돌. 한 스택에서 일관성 유지.

---

## 📎 Sources

1. [JEP 444: Virtual Threads](https://openjdk.org/jeps/444) — 공식 JEP
2. [JEP 491: Synchronize Virtual Threads without Pinning](https://openjdk.org/jeps/491) — 공식 JEP (JDK 24)
3. [JEP 505: Structured Concurrency 5th Preview](https://openjdk.org/jeps/505) — 공식 JEP (JDK 25)
4. [Oracle Virtual Threads Guide](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html) — 공식 문서
5. [Kotlin Coroutines Overview](https://kotlinlang.org/docs/coroutines-overview.html) — JetBrains 공식
6. [Kotlin Language Specification: Coroutines](https://kotlinlang.org/spec/asynchronous-programming-with-coroutines.html) — 공식 명세
7. [Java 24 Stops Pinning Virtual Threads (Almost)](https://nipafx.dev/inside-java-newscast-80/) — Inside Java
8. [JDK 24's Major Improvement: Virtual Threads Without Pinning](https://www.danvega.dev/blog/jdk-24-virtual-threads-without-pinning) — Dan Vega
9. [Java Virtual Threads Performance Vs. Kotlin Coroutines](https://medium.com/@AliBehzadian/java-virtual-threads-performance-vs-kotlin-coroutines-f6b1bf798b16) — Medium 벤치마크
10. [Coroutine-Reactor-VirtualThread Microbenchmark (GitHub)](https://github.com/gaplo917/coroutine-reactor-virtualthread-microbenchmark) — 실측 벤치마크
11. [Structured Concurrency: Will Java Loom Beat Kotlin's Coroutines?](https://xebia.com/blog/structured-concurrency-will-java-loom-beat-kotlins-coroutines-2/) — Xebia
12. [Kotlin Coroutine Internals: State Machines](https://medium.com/@sivavishnu0705/under-the-hood-of-suspension-tracing-the-state-machine-behind-kotlin-coroutines-5d4c9e954d0d) — Medium
13. [The Beginner's Guide to Kotlin Coroutine Internals](https://careersatdoordash.com/blog/the-beginners-guide-to-kotlin-coroutine-internals/) — DoorDash Engineering
14. [Project Loom: Structured Concurrency in JDK 25](https://rockthejvm.com/articles/structured-concurrency-jdk-25) — Rock the JVM
15. [Kotlin Discussions: Coroutines or JVM Virtual Threads?](https://discuss.kotlinlang.org/t/kotlin-coroutines-or-jvm-virtual-threads/24050) — 커뮤니티

---

## 🔗 관련 노트

- [[coroutine-gmp-vthread]] — Coroutine + Go GMP + Virtual Thread 동시성 비교 (Go 관점 추가)
- [[verification-corrections-summary]] — 기술 내용 검증 정정 사항 (JVM, Go, epoll, HikariCP)
- [[python-go-java-performance-myth-deep-dive]] — Python vs Go/Java 성능 신화 Deep Dive
- [[spring-tuning-hikaricp]] — Spring Boot 튜닝 (Tomcat Thread Pool, HikariCP)
- [[03-aws-iam-policy-concept-explainer]] — (참고: concept-explainer 템플릿 사용 예시)

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 7
> - 수집 출처 수: 15+
> - 출처 유형: 공식 JEP 3, 공식 문서 2, 기술 블로그 7, 벤치마크 2, 커뮤니티 1
> - 작성일: 2026-05-01 (JDK 25 LTS, Kotlin 2.x 기준)
> - 검증 포인트: JEP 491 (JDK 24 synchronized 해소), JEP 505 (Structured Concurrency 5th Preview), Dispatchers.IO work-stealing 구조
