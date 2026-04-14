---
tags: [kotlin, coroutine, go, gmp, virtual-thread, concurrency]
created: 2026-04-15
---

# Coroutine + Go GMP + Virtual Thread

---

## 1. Kotlin Coroutine

### 1.1 코루틴이란

중단(suspend)하고 재개(resume)할 수 있는 경량 비동기 실행 단위.

| 항목          | 스레드                                    | 코루틴                                   |
| ------------- | ----------------------------------------- | ---------------------------------------- |
| 관리          | OS                                        | Kotlin 런타임                            |
| 메모리        | ~1MB                                      | ~1.5-2.5KB                               |
| 스위칭 비용   | 커널 진입 필요 (수~수십 마이크로초)        | 유저스페이스 (수십~수백 나노초)           |
| 10만개        | OOM                                       | 문제없음                                 |

### 1.2 동작 원리 — 상태 머신 변환

suspend 함수는 컴파일 시점에 **상태 머신(State Machine)**으로 변환된다. Continuation 객체에 state와 로컬 변수가 저장됨.

```kotlin
// 개발자가 쓰는 코드
suspend fun fetchUserAndOrder(id: Long) {
    val user = fetchUser(id)       // 중단점 1
    val order = fetchOrder(user)   // 중단점 2
    return Pair(user, order)
}

// 컴파일러가 변환한 실제 코드 (의사코드)
fun fetchUserAndOrder(id: Long, continuation: Continuation) {
    when (continuation.state) {
        0 -> { fetchUser(id, continuation) }  // 중단 후 저장
        1 -> { fetchOrder(user, continuation) } // 재개 후 중단
        2 -> { return Pair(user, order) }
    }
}
```

### 1.3 "스레드 블로킹 없이 중단"의 정확한 의미

코루틴은 결국 스레드 위에서 돌아간다. 핵심은 **"어떤 스레드가 무엇을 기다리느냐"**.

**스레드 블로킹 (Thread.sleep / 동기 IO):**

```
Thread-1: [작업A ────────── IO 대기 중 (아무것도 못함) ──────── 재개]
Thread-2: [작업B ───]
Thread-3: [작업C ─────────]

→ Thread-1은 IO 기다리는 동안 완전히 묶여있음
→ 10만 요청 = 10만 스레드 필요
```

**코루틴 중단 (suspend):**

```
Thread-1: [코루틴A 실행] → [중단, 스레드 반납] → [코루틴C 실행] → [코루틴A 재개]
Thread-2: [코루틴B 실행] → [중단, 스레드 반납] → [코루틴D 실행]

→ Thread-1이 코루틴A를 중단시키고 코루틴C를 이어서 실행
→ 10만 요청 = 스레드 몇 개로 처리 가능
```

상태머신으로 변환되기 때문에 **"어디까지 실행했는지"를 저장하고 스레드를 반납**할 수 있는 것.

실제 실행 흐름:

```
1. Thread-1이 processOrder 실행 시작
2. fetchUser() 호출 → IO 요청 날림
3. "state = 1, id 저장" → 스레드 반납  ← 핵심!
4. Thread-1은 다른 코루틴 실행하러 감
5. IO 완료 신호 도착
6. Thread-1 (or Thread-2)이 state=1부터 재개
7. fetchOrder() 호출 → IO 요청 날림
8. "state = 2, user 저장" → 스레드 반납
9. ...반복
```

스레드 입장에서는 **"기다리는 시간이 없이 항상 일하고 있는"** 상태.

### 1.4 Dispatcher와 스케줄링

```kotlin
Dispatchers.Main       // UI 스레드 (Android)
Dispatchers.IO         // IO 작업 (DB, 네트워크)
Dispatchers.Default    // CPU 집약적 작업 — 코어수만큼
Dispatchers.Unconfined // 제한 없음 (거의 안 씀)
```

> **[검증 정정]** `Dispatchers.Default`는 **"글로벌 큐 1개"가 아니다**.
> `CoroutineScheduler`는 **글로벌 큐 + per-Worker 로컬 큐 + Work-Stealing 하이브리드** 구조이며, Go GMP 스케줄러 디자인에서 영감을 받았다고 소스코드 주석에 명시.

> **[검증 정정]** `Dispatchers.IO` 스레드 "최대 64개 한계"는 **기본값**이며 고정이 아님.
> - 기본값: `max(64, CPU코어수)`
> - `kotlinx.coroutines.io.parallelism` 시스템 프로퍼티로 변경 가능
> - `Dispatchers.IO.limitedParallelism(n)`으로 elastic하게 확장 가능

**IO 완료 시 재개 흐름:**

```
[코루틴 중단]
    ↓
[Java NIO Selector가 IO 감시] ← OS 레벨 비동기 IO (epoll/kqueue)
    ↓
[IO 완료 이벤트 발생]
    ↓
[콜백에서 Continuation.resume() 호출]
    ↓
[Dispatcher 큐에 해당 코루틴 재등록]
    ↓
[스레드가 큐에서 꺼내서 재개]
```

OS의 비동기 IO + NIO Selector + Dispatcher 큐 세 개가 맞물려서 동작.

### 1.5 launch vs async

```kotlin
// launch: 결과값 없음, fire-and-forget
launch {
    sendNotification()
}

// async: 결과값 있음, Deferred 반환
val userDeferred = async { fetchUser(id) }
val orderDeferred = async { fetchOrder(id) }

// await()로 둘 다 완료될 때까지 대기 (병렬 실행!)
val user = userDeferred.await()
val order = orderDeferred.await()
```

```kotlin
// 순차 실행: 1초 + 1초 = 2초
val user = fetchUser(id)
val order = fetchOrder(id)

// 병렬 실행: max(1초, 1초) = 1초
val user = async { fetchUser(id) }
val order = async { fetchOrder(id) }
val result = Pair(user.await(), order.await())
```

### 1.6 Spring에서의 코루틴

> **[검증 정정]** "Spring MVC는 코루틴 미지원"은 **틀림**.
> Spring 6+에서 `@Controller`의 suspend 함수, `Flow` 반환값을 지원.
> WebFlux 전용 기능(`coRouter` DSL, `CoWebFilter`, RSocket)만 미지원.

**현실적인 선택지:**

| 방식                                    | 장점                     | 단점                                |
| --------------------------------------- | ------------------------ | ----------------------------------- |
| 코루틴 + `withContext(Dispatchers.IO)`  | 기존 JPA 그대로 사용     | 결국 스레드 소비, 코루틴 이점 반감  |
| WebFlux + R2DBC                         | 코루틴 이점 100%         | 학습 비용, QueryDSL 미지원          |
| Virtual Thread (Java 21+)              | 기존 코드 변경 없음      | 구조화된 동시성 성숙도 부족         |

### 1.7 Python async/await, Go goroutine과 비교

| 항목   | Kotlin Coroutine               | Python asyncio         | Go goroutine                |
| ------ | ------------------------------ | ---------------------- | --------------------------- |
| 방식   | 컴파일러 변환 (상태머신)       | 이벤트 루프            | OS 경량 스레드              |
| 병렬성 | Dispatcher로 멀티스레드        | 기본 단일 스레드       | 진짜 병렬 (GMP)            |
| 문법   | suspend, launch, async         | async def, await       | go func()                   |
| 강제성 | suspend 함수만 중단 가능       | async 함수만 가능      | 어디서든 go 키워드          |
| 취소   | 구조화된 동시성으로 자동       | 수동 관리              | context로 수동 관리         |

Python asyncio의 함정:

```python
async def handler():
    result = requests.get(url)  # 실수로 동기 함수 호출
    # 이벤트 루프 전체가 블로킹됨 — 컴파일러가 못 잡음
```

Kotlin은 이 실수가 컴파일 단계에서 차단됨.

---

## 2. Go GMP 모델

### 2.1 구조

```
G (Goroutine): 실행할 코루틴 단위
M (Machine):  OS 스레드 (진짜 CPU 코어에 매핑)
P (Processor): 스케줄러 컨텍스트 (로컬 큐 보유)

P0 (로컬큐: G1,G2,G3)    P1 (로컬큐: G4,G5,G6)
       ↓                         ↓
      M0  ←→ CPU Core 0         M1  ←→ CPU Core 1
```

GOMAXPROCS(기본값 = CPU 코어 수)만큼 P가 생성.

### 2.2 P(Processor)란 무엇인가

P는 물리적 실체가 없는 **"고루틴 실행 허가증"**. M(OS 스레드)이 고루틴을 실행하려면 반드시 P를 들고 있어야 한다.

**왜 만들었나**: "동시에 고루틴을 실행하는 OS 스레드 수를 제한하고 싶다"

```
GOMAXPROCS = 4 (P가 4개), M은 현재 10개 (블로킹 IO 때문에 늘어남)

M0  + P0 → 고루틴 실행 중 ✅
M1  + P1 → 고루틴 실행 중 ✅
M2  + P2 → 고루틴 실행 중 ✅
M3  + P3 → 고루틴 실행 중 ✅
M4       → 시스템콜 대기 중 (P 없음, 실행 불가) ⏸️
M5       → 시스템콜 대기 중 ⏸️
M6       → 유휴 상태 ⏸️
```

P = **동시 실행 수를 제한하는 토큰 + 거기에 붙은 로컬 큐**

### 2.3 큐 3종류

```
글로벌 큐 (mutex 보호) ← 최후의 수단
    ↑
P0 [로컬큐 max 256]    P1 [로컬큐]    P2 [로컬큐]
```

**로컬 큐**: 각 P가 소유. lock-free. 최대 **256개** goroutine.

**글로벌 큐 사용 시점**:

- 로컬 큐가 **256개 가득 찼을 때** → 절반을 글로벌 큐로 이동
- `go func()`이 **다른 P의 컨텍스트**에서 호출됐을 때
- Work Stealing에서 **다른 P 로컬 큐도 비어있을 때**

**Work Stealing 순서**:

```
1. 자기 로컬 큐에서 꺼냄
2. 비었으면 → 다른 P 로컬 큐에서 절반 훔침
3. 다 비었으면 → 글로벌 큐에서 가져옴
4. 글로벌도 비었으면 → netpoller에서 ready된 G 확인
```

> **[검증 정정]** "각 P가 자기 로컬 큐만 접근 → 락 경쟁 없음"은 과도한 표현.
> 로컬 큐 접근은 lock-free이지만, 글로벌 큐는 mutex로 보호되고, Work Stealing 시에도 다른 P 큐에 접근.
> 정확한 표현: **"로컬 큐는 lock-free → 락 경쟁을 최소화함"**

### 2.4 병렬성

CPU 4코어, GOMAXPROCS=4:

```
Core0: M0 → P0 → G1 실행중
Core1: M1 → P1 → G4 실행중
Core2: M2 → P2 → G7 실행중
Core3: M3 → P3 → G10 실행중
```

이 순간 G1, G4, G7, G10이 물리적으로 동시에 실행. 다만 고루틴 수가 GOMAXPROCS를 초과하면 나머지는 큐 대기.

Kotlin도 `Dispatchers.Default`는 CPU 코어 수만큼 스레드를 띄우기 때문에 병렬 실행 가능성 자체는 동일. Go GMP의 진짜 강점은 스케줄러가 런타임에 내장되어 개발자가 Dispatcher 같은 걸 신경 안 써도 된다는 편의성.

### 2.5 네트워크 IO 처리 (netpoller)

```
G1이 net.Read() 호출
→ Go 런타임이 감지: "이건 네트워크 IO"
→ G1을 park 상태로 만들고 M 반납 ← Kotlin 코루틴과 동일 원리!
→ epoll이 IO 완료 감지
→ G1을 로컬 큐에 재등록
→ M 추가 생성 없음!
```

진짜 블로킹 시스템콜(일반 디스크 파일 IO, CGO 호출)에서만 P-M 분리 + M 추가 생성 발생. (단, pipe/terminal 같은 일부 파일 fd는 netpoller로 처리 가능)

**네트워크 IO (대부분의 서버 워크로드):**

```
Kotlin: Continuation 저장 → 스레드 반납 → NIO 감시
Go:     G park → M 반납 → netpoller 감시

→ 둘 다 스레드 추가 생성 없음, 동일한 원리
```

### 2.6 선점형 스케줄링 (Go 1.14+)

> **[검증 정정]** "10ms마다 런타임이 강제로 선점"은 부정확.
> sysmon이 **10ms 이상** 실행 중인 고루틴을 감지하면 해당 M에 **SIGURG 시그널** 전송.
> 시그널 핸들러가 **async safe-point**인지 확인 후 선점. "10ms마다"가 아니라 "10ms threshold".

Kotlin 코루틴은 비선점형 — 개발자가 `Dispatchers.Default` 분리나 `yield()`로 직접 처리해야 함.

---

## 3. 코루틴/고루틴 성능이 나오는 이유

### 3.1 핵심: IO 대기 시간을 낭비하지 않는다

일반적인 API 요청:

```
[요청 수신 1ms] → [DB 쿼리 대기 50ms] → [외부 API 대기 30ms] → [응답 1ms]

전체 82ms 중 CPU가 실제 일하는 시간: 2ms (2.4%)
나머지 97.6%는 IO 대기
```

### 3.2 유저스페이스 vs 커널스페이스

| 항목     | OS Thread 스케줄링                                 | 코루틴 스케줄링                 |
| -------- | -------------------------------------------------- | ------------------------------- |
| 경로     | App → 시스템콜 → 커널 → OS 스케줄러                | App → 유저스페이스 스케줄러     |
| 비용     | 레지스터 저장 + 스택 복원 + CPU 캐시 무효화        | Continuation 상태 저장/복원만   |

### 3.3 CPU Intensive 작업의 한계

CPU Intensive 작업은 중단점이 없어서 코루틴/고루틴의 이점이 거의 없고 오히려 starvation 위험.

- **Go**: 런타임이 선점형으로 해결 (10ms threshold + SIGURG)
- **Kotlin**: 개발자가 `Dispatchers.Default` 분리나 `yield()`로 직접 처리

하지만 구조화된 동시성(취소 전파, 리소스 누수 방지)은 IO/CPU 무관하게 가치 있음.

---

## 4. Virtual Thread vs Coroutine

### 4.1 비교

| 항목               | Virtual Thread                                        | Coroutine                        |
| ------------------ | ----------------------------------------------------- | -------------------------------- |
| 해결 레벨          | JVM 런타임                                            | 언어/컴파일러                    |
| 기존 코드 호환     | 그대로 사용 가능                                      | suspend 수정 필요                |
| 병렬 처리 표현     | ExecutorService 직접                                  | async/await 자연스러움           |
| 구조화된 동시성    | StructuredTaskScope Preview (JDK 25 6th Preview)      | 언어 레벨 기본 제공              |
| 취소 전파          | 수동 (interrupt)                                      | 자동 (스코프)                    |
| 메모리             | ~수KB                                                 | ~1.5-2.5KB (더 가벼움)           |
| 학습 비용          | 낮음                                                  | 높음                             |

> **[검증 정정]** "Virtual Thread는 구조화된 동시성이 없다"는 **틀림**.
> Java 21부터 `StructuredTaskScope`가 Preview Feature로 제공. JDK 25에서 6th Preview.
> 다만 Kotlin `coroutineScope`처럼 언어 차원에서 기본 제공되는 것과는 **성숙도 차이**.

### 4.2 블로킹 처리 방식

**Virtual Thread:**

```
VThread-1이 JDBC 블로킹 호출
→ JVM이 감지: "블로킹 발생"
→ Carrier Thread에서 VThread-1 분리 (unmount)
→ Carrier Thread는 VThread-2 실행
→ IO 완료 시 VThread-1을 다시 Carrier Thread에 mount
→ 재개

→ Go GMP의 P-M 분리와 거의 동일한 원리!
```

**Coroutine:**

```
suspend 함수 내 IO 호출
→ Continuation에 상태 저장 → 스레드 반납
→ IO 완료 시 Dispatcher 큐에 재등록 → 재개
→ 컴파일러 변환이 필요
```

### 4.3 코드 비교

```kotlin
// Virtual Thread: 기존 블로킹 코드 그대로
@Service
class UserService(val userRepository: UserRepository) {
    fun getUser(id: Long): User {
        val user = userRepository.findById(id)  // 블로킹 JPA 그대로
        return user
    }
}

// Coroutine: suspend 명시 필요, 논블로킹 라이브러리 필요
@Service
class UserService(val userRepository: UserRepository) {
    suspend fun getUser(id: Long): User {
        val user = userRepository.findById(id)  // R2DBC 필요
        return user
    }
}
```

병렬 처리:

```kotlin
// Virtual Thread: ExecutorService 직접 써야 함
val executor = Executors.newVirtualThreadPerTaskExecutor()
val userFuture = executor.submit { userRepository.findById(id) }
val orderFuture = executor.submit { orderRepository.findById(id) }
Result(userFuture.get(), orderFuture.get())

// Coroutine: 언어 레벨에서 자연스러움
suspend fun getAll(id: Long): Result {
    val user = async { userRepository.findById(id) }
    val order = async { orderRepository.findById(id) }
    return Result(user.await(), order.await())
}
```

### 4.4 Pinning — Virtual Thread의 주의사항

`synchronized` 블록 안에서 블로킹할 때 **Carrier Thread에서 unmount 불가** = OS 스레드 낭비. VT의 이점 사라짐.

```java
synchronized (lock) {
    resultSet = statement.executeQuery(sql);  // 블로킹!
    // → Carrier Thread째로 블로킹 = pinning!
}
```

이유: `synchronized`는 OS 레벨 모니터 락을 사용하며, 특정 OS 스레드에 바인딩. VThread를 다른 Carrier로 옮기면 락 소유권이 깨짐.

```
ReentrantLock → pinning 안 발생 ✅ (JVM 레벨 락)
synchronized → pinning 발생 ❌ (OS 레벨 모니터)
```

| 상황                                      | pinning? | Carrier Thread 낭비? |
| ----------------------------------------- | -------- | -------------------- |
| 네트워크 IO (read/write)                  | 아니오   | 아니오               |
| `Thread.sleep()`                          | 아니오   | 아니오               |
| `ReentrantLock.lock()`                    | 아니오   | 아니오               |
| **`synchronized` 안에서 블로킹**          | **예**   | **예**               |
| **native method (JNI) 안에서 블로킹**     | **예**   | **예**               |

`Thread.sleep()`은 JDK 21에서 VT 인식하도록 재구현 → pinning 발생 안 함.

VT 환경에서는 `synchronized` 대신 `ReentrantLock` 사용이 공식 권고. JDBC 드라이버 내부에 `synchronized` 쓰는 것도 있으므로 드라이버 버전 확인 필요.

### 4.5 Spring 환경에서 선택 기준

**Virtual Thread 유리**: 기존 Spring MVC + JPA 레거시 유지, 팀이 코루틴 학습 비용 감당 어려움, 점진적 성능 개선

**Coroutine 유리**: 신규 서비스, 높은 동시성 핵심 요구, 복잡한 병렬 처리, 취소/타임아웃 세밀한 제어

```yaml
# Virtual Thread 적용 — 한 줄
spring:
  threads:
    virtual:
      enabled: true
```
