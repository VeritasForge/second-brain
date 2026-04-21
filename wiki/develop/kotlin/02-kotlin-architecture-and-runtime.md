---
created: 2026-04-21
source: claude-code
tags: [kotlin, architecture, jvm, k2-compiler, gc, coroutine-runtime, spring-boot, runtime]
---

# 📖 Kotlin 아키텍처와 런타임 — K2 컴파일러부터 JVM까지

> 💡 **한줄 요약**: Kotlin은 K2 프론트엔드가 소스를 FIR(Frontend IR)로 변환한 뒤 JVM/JS/Native 백엔드로 다중 타겟 바이트코드를 생성하며, JVM 위에서 G1/ZGC로 GC를 수행하고, 코루틴은 컴파일 타임에 상태 머신으로 변환되어 Dispatcher를 통해 스케줄링된다.
>
> 📌 **핵심 키워드**: K2, FIR, JVM, G1/ZGC, Continuation Passing, Dispatcher, Spring Boot Startup
> 📅 **기준**: Kotlin 2.1+ / JDK 21+ (2025)

---

## 1️⃣ Kotlin 컴파일 파이프라인

### K2 컴파일러 (Kotlin 2.0+)

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐
│  Source   │───►│  K2      │───►│  FIR     │───►│  Backend     │
│  .kt 파일 │    │  Frontend│    │  (Front  │    │  (타겟별)     │
└──────────┘    │  Parser  │    │  IR)     │    │              │
                └──────────┘    └──────────┘    │  ┌─── JVM    │
                                                 │  ├─── JS     │
                                                 │  ├─── Native │
                                                 │  └─── Wasm   │
                                                 └──────┬───────┘
                                                        │
                                                        ▼
                                                 ┌──────────────┐
                                                 │  .class (JVM)│
                                                 │  .js (JS)    │
                                                 │  binary (Nat)│
                                                 └──────────────┘
```

### K2 성능 개선 (K1 대비)

| 지표 | 개선폭 | 프로젝트 |
|------|--------|---------|
| 클린 빌드 | **최대 94% 빠름** | Anki-Android (58s → 30s) |
| 분석 단계 | **194% 빠름** | Anki-Android |
| 증분 빌드 (ABI 변경) | **275% 빠름** | Anki-Android |
| Gradle 전체 | **~20% 빠름** | 일반 프로젝트 |

> K2는 10만 줄 이상의 프론트엔드를 완전히 재작성한 것 — 1만 프로젝트, 1800만 개발자 대상 테스트 후 안정화.

### 🔄 4개 언어 컴파일 비교

| 단계 | Kotlin (K2) | Go | Python (CPython) | JS (V8) |
|------|-----------|-----|-----------------|---------|
| 파싱 | K2 → FIR | Parser → AST | Parser → AST | Parser → AST |
| 타입 검사 | FIR에서 통합 | types2 | 런타임 (힌트는 선택) | TS: tsc, JS: 없음 |
| 최적화 | JVM JIT (런타임) | SSA (컴파일 타임) | 없음 | Turbofan JIT (런타임) |
| 타겟 | JVM/JS/Native/Wasm | 네이티브 바이너리 | 바이트코드(.pyc) | V8 바이트코드 |

---

## 2️⃣ JVM 런타임 구조

### JVM 메모리 구조

```
┌───────────────────────────────────────────┐
│                 JVM Process                │
│                                            │
│  ┌────────────────────────────────────┐   │
│  │            Heap                     │   │
│  │  ┌──────────┐  ┌────────────────┐  │   │
│  │  │Young Gen │  │   Old Gen      │  │   │
│  │  │ Eden     │  │   (Tenured)    │  │   │
│  │  │ S0 / S1  │  │                │  │   │
│  │  └──────────┘  └────────────────┘  │   │
│  └────────────────────────────────────┘   │
│                                            │
│  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │Metaspace │  │Thread    │  │Native  │  │
│  │(클래스)   │  │Stacks   │  │Memory  │  │
│  └──────────┘  └──────────┘  └────────┘  │
└───────────────────────────────────────────┘
```

| 영역 | 역할 | Go 대응 |
|------|------|--------|
| **Young Gen** | 새 객체 할당, Minor GC | mcache (소형 객체) |
| **Old Gen** | 장수 객체 | mheap |
| **Metaspace** | 클래스 메타데이터 | 없음 (바이너리에 내장) |
| **Thread Stack** | 스레드별 호출 스택 | goroutine 스택 (2KB 시작) |

### GC 전략

> 📌 GC 상세 비교: [[gc-g1-zgc]] — G1/ZGC/Go GC/Python RC 비교

| GC | STW | 적합한 상황 | JDK 기본값 |
|-----|-----|-----------|----------|
| **G1** | 1-10ms | 범용, 중간 힙 | JDK 9~20 기본 |
| **ZGC** | ~1ms | 대용량 힙, 저지연 | JDK 21+ 추천 |
| **Shenandoah** | ~1ms | ZGC 대안 | Red Hat JDK |

### 🧒 12살 비유

> JVM은 "놀이공원 운영 시스템"이야. Young Gen은 "놀이기구 줄서기 공간"(새로운 방문객), Old Gen은 "연간 이용권 구역"(오래 머무는 단골). G1 GC는 "청소부가 구역별로 돌면서 치우는 것"이고, ZGC는 "방문객이 놀면서도 동시에 청소하는 로봇"이야.

---

## 3️⃣ 코루틴 런타임 아키텍처

### Continuation Passing (컴파일 타임 변환)

```kotlin
// 원본 코드
suspend fun fetchUser(id: Int): User {
    val response = httpClient.get("/users/$id")  // suspension point 1
    val user = parseUser(response)               // suspension point 2
    return user
}

// 컴파일러가 변환한 상태 머신 (의사 코드)
fun fetchUser(id: Int, cont: Continuation<User>): Any? {
    val sm = cont as? FetchUserSM ?: FetchUserSM(cont)
    when (sm.state) {
        0 -> { sm.state = 1; return httpClient.get(..., sm) }
        1 -> { sm.state = 2; return parseUser(sm.result, sm) }
        2 -> { sm.cont.resume(sm.result) }
    }
}
```

### Dispatcher

```
┌─────────────────────────────────────────────────┐
│              Coroutine Dispatchers               │
│                                                   │
│  Dispatchers.Default ─── CPU 집약 작업           │
│  (코어 수만큼 스레드 풀)                          │
│                                                   │
│  Dispatchers.IO ──────── I/O 집약 작업           │
│  (최대 64개 또는 코어 수 중 큰 값)                │
│                                                   │
│  Dispatchers.Main ────── UI 스레드 (Android)     │
│                                                   │
│  Dispatchers.Unconfined ─ 호출자 스레드에서 시작  │
│  (재개 시 어떤 스레드든 가능 — 주의 필요)         │
└─────────────────────────────────────────────────┘
```

> 📌 코루틴 vs goroutine vs Virtual Thread 비교: [[coroutine-gmp-vthread]]

### 🔄 4개 언어 동시성 런타임 비교

| 측면 | Kotlin (코루틴) | Go (GMP) | Python (asyncio) | JS (이벤트 루프) |
|------|---------------|---------|-----------------|----------------|
| 구현 방식 | 컴파일 타임 상태 머신 | 런타임 스케줄러 | 이벤트 루프 | 이벤트 루프 |
| 메모리/인스턴스 | ~수백 바이트 | ~2KB (goroutine) | ~수 KB (Task) | ~수 KB (Promise) |
| 10만 동시 인스턴스 | ✅ 가능 | ✅ 가능 | ✅ 가능 | ✅ 가능 |
| 스레드 풀 | Dispatcher가 관리 | P가 관리 (GMP) | 단일 스레드 | 단일 스레드 |

---

## 4️⃣ Spring Boot 시작 파이프라인

```
SpringApplication.run()
    │
    ├── 1. 환경 준비 (Environment)
    │     PropertySource 로딩, 프로파일 활성화
    │
    ├── 2. ApplicationContext 생성
    │     AnnotationConfigServletWebServerApplicationContext
    │
    ├── 3. Bean 정의 스캔
    │     @Component, @Service, @Repository 등 발견
    │
    ├── 4. Auto-Configuration 적용
    │     spring-boot-autoconfigure의 조건부 @Conditional 평가
    │     (WebServerAutoConfiguration, DataSourceAutoConfiguration 등)
    │
    ├── 5. Bean 인스턴스화 + 의존성 주입
    │     @Autowired, 생성자 주입, @Value
    │
    ├── 6. BeanPostProcessor 실행
    │     AOP 프록시 생성, @Transactional 래핑 등
    │
    └── 7. 서버 시작
          Tomcat/Netty 시작, 포트 바인딩
          "Started MyApp in X.XXX seconds"
```

### Spring Boot 시작 시간 최적화

| 방법 | 효과 | 트레이드오프 |
|------|------|-----------|
| Lazy initialization | 시작 빠름 | 첫 요청 느림 |
| Spring AOT (3.0+) | 컴파일 타임 처리 | 빌드 복잡 |
| GraalVM Native Image | ~50ms 시작 | 리플렉션 제한, 빌드 느림 |
| Virtual Threads (21+) | I/O 처리 개선 | 시작 시간은 동일 |

---

## 5️⃣ 바이너리 구조와 배포

### JVM 배포 (기본)

```bash
# Fat JAR 빌드
./gradlew bootJar
# → build/libs/myapp-0.1.0.jar (~50-80MB)

# 실행
java -jar myapp-0.1.0.jar
```

### GraalVM Native Image

```bash
# Native 빌드 (Spring Boot 3.x + GraalVM)
./gradlew nativeCompile
# → build/native/nativeCompile/myapp (~80-120MB 바이너리)

# 실행: JVM 불필요, ~50ms 시작
./myapp
```

| 배포 방식 | 시작 시간 | 메모리 | 파일 크기 | 리플렉션 |
|---------|---------|--------|---------|---------|
| **JVM JAR** | ~2-5s | ~200-400MB | ~50-80MB | ✅ 자유 |
| **GraalVM Native** | **~50ms** | ~50-100MB | ~80-120MB | ❌ 제한 (설정 필요) |
| Go (비교) | ~1ms | ~10-30MB | ~10-15MB | N/A |

### 🔄 4개 언어 배포 비교

| 측면 | Kotlin/JVM | Go | Python | JS/TS |
|------|-----------|-----|--------|-------|
| 결과물 | .jar | 단일 바이너리 | .py + venv | .js 번들 |
| 런타임 | JVM | 없음 | CPython | Node.js |
| 컨테이너 이미지 | eclipse-temurin (~300MB) | scratch (~10MB) | python:slim (~150MB) | node:slim (~180MB) |
| 시작 시간 | 2-5s (JVM) / 50ms (Native) | ~1ms | ~30ms | ~50ms |

---

## 📎 출처

1. [K2 Compiler Performance Benchmarks (JetBrains)](https://blog.jetbrains.com/kotlin/2024/04/k2-compiler-performance-benchmarks-and-how-to-measure-them-on-your-projects/) — K2 벤치마크
2. [JVM Architecture (Oracle)](https://docs.oracle.com/javase/specs/jvms/se21/html/) — JVM 스펙
3. [Structured Concurrency (Roman Elizarov)](https://elizarov.medium.com/structured-concurrency-722d765aa952) — 코루틴 설계 근거
4. [Spring Boot Reference Documentation](https://docs.spring.io/spring-boot/reference/) — Spring Boot 시작 파이프라인
5. [GraalVM Native Image (oracle.com)](https://www.graalvm.org/latest/reference-manual/native-image/) — Native Image 가이드

---

> 📌 **이전 문서**: [[01-kotlin-philosophy-and-differentiation]]
> 📌 **다음 문서**: [[03-kotlin-basic-syntax]]
> 📌 **관련 문서**: [[gc-g1-zgc]], [[coroutine-gmp-vthread]], [[kotlin-spring]] (Q7-Q9 JVM)
