# Golang — Staff Engineer Interview Q&A

> 대상: FAANG L6/L7 (Staff/Principal Engineer)
> 총 문항: 26개 | 난이도: ⭐⭐⭐⭐⭐
> 버전: Go 1.22+

## 목차

1. [Goroutine Scheduler (G-M-P)](#1-goroutine-scheduler-g-m-p) — Q1~Q3
2. [Memory Model & GC](#2-memory-model--gc) — Q4~Q6
3. [Channel Patterns](#3-channel-patterns) — Q7~Q9
4. [Interface Design](#4-interface-design) — Q10~Q12
5. [Error Handling](#5-error-handling) — Q13~Q14
6. [Performance Engineering](#6-performance-engineering) — Q15~Q17
7. [sync Primitives](#7-sync-primitives) — Q18~Q20
8. [Production Patterns](#8-production-patterns) — Q21~Q22
9. [Testing Strategies](#9-testing-strategies) — Q23~Q24
10. [Module System & Build](#10-module-system--build) — Q25~Q26

---

## 1. Goroutine Scheduler (G-M-P)


> 대상: FAANG L6/L7 (Staff/Principal Engineer)
> 총 문항: 3개 | 난이도: ⭐⭐⭐⭐⭐
> 런타임: Go 1.22+

## 목차

1. [Goroutine Scheduler (G-M-P)](#1-goroutine-scheduler-g-m-p) — Q1~Q3

---

## 1. Goroutine Scheduler (G-M-P)

### Q1: G-M-P 모델의 설계 원리와 Work-Stealing

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Goroutine Scheduler (G-M-P)

**Question:**
Go 런타임의 G-M-P 스케줄링 모델을 설명하라. 왜 초기의 G-M 모델에서 P(Processor)를 도입했는지, P가 해결하는 구체적인 문제는 무엇인지 설명하라. Work-stealing 알고리즘이 어떻게 동작하는지, 그리고 `GOMAXPROCS`가 P의 수를 결정할 때 CPU 코어 수보다 크거나 작게 설정하면 어떤 영향이 있는지 프로덕션 경험을 바탕으로 논의하라.

---

**🧒 12살 비유:**
놀이공원에 여러 놀이기구(M = OS Thread)가 있고, 줄 서 있는 손님들(G = Goroutine)이 있다고 상상해 보자. 처음에는 손님들이 하나의 거대한 줄에 서서 기다렸다. 그런데 놀이기구 100개에 손님 10만 명이 줄을 서면, 줄 하나를 관리하는 직원이 병목이 된다 — 모두가 그 직원 앞에서 대기해야 하니까. 그래서 P(Processor)라는 "구역 관리자"를 도입했다. 각 관리자가 자기 구역의 줄을 관리하고, 자기 구역 줄이 비면 다른 구역에서 손님을 "훔쳐" 온다. 이게 바로 work-stealing이다. `GOMAXPROCS`는 구역 관리자 수를 정하는 것이다. 놀이기구가 8개인데 관리자를 16명 두면 관리자끼리 놀이기구를 두고 경쟁하고, 4명만 두면 놀이기구 절반이 놀게 된다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

이 질문은 Go 런타임의 핵심 설계 철학을 평가한다. 면접관이 보는 포인트는: (1) 단순 암기가 아닌 G-M-P 각 컴포넌트의 존재 이유에 대한 구조적 이해, (2) P 도입 전후의 성능 차이를 설명할 수 있는 시스템 사고력, (3) `GOMAXPROCS` 튜닝에 대한 프로덕션 판단력, (4) work-stealing의 cache locality 트레이드오프 인식. Staff 레벨에서는 "무엇이 어떻게 동작하는가"를 넘어 "왜 이렇게 설계했는가"를 논증할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

**G-M-P 각 컴포넌트:**

- **G (Goroutine):** 사용자 수준의 경량 실행 단위. 초기 스택 2~4KB (Go 1.22 기준 기본 4KB), 필요 시 동적 확장. `runtime.g` 구조체로 표현되며 스택 포인터, PC, 상태(`_Grunnable`, `_Grunning`, `_Gwaiting` 등)를 보유한다.

- **M (Machine):** OS 스레드에 1:1 매핑. `runtime.m` 구조체. 커널 스케줄러에 의해 CPU 코어에 배치된다. M은 G를 실행하기 위해 반드시 P를 획득해야 한다.

- **P (Processor):** 논리적 프로세서. Go 1.1에서 Dmitry Vyukov가 도입. `runtime.p` 구조체. 로컬 런 큐(최대 256개 G), `mcache`(메모리 할당 캐시), 타이머 힙 등 스케줄링에 필요한 컨텍스트를 보유한다.

**P 도입 전(Go 1.0)의 문제:**

Go 1.0의 스케줄러는 글로벌 런 큐 하나와 글로벌 뮤텍스(`runtime.sched.Lock`)로 동작했다. 모든 M이 G를 가져오거나 반환할 때마다 이 뮤텍스를 획득해야 했다. 코어 수가 증가하면 lock contention이 O(M) 수준으로 증가하며, 특히 `mcache`가 M에 바인딩되어 있어 syscall 블로킹 시에도 메모리 캐시를 점유하는 비효율이 있었다.

**P가 해결하는 문제:**

1. **Lock contention 제거:** 각 P가 로컬 런 큐를 가지므로 G 스케줄링이 lock-free에 가까워진다. 글로벌 큐 접근은 로컬 큐가 빈 경우에만 발생한다.
2. **mcache 효율화:** `mcache`가 M이 아닌 P에 바인딩된다. M이 syscall로 블로킹되면 P가 분리(hand-off)되어 다른 M에 붙으므로, 블로킹 중에도 메모리 캐시가 낭비되지 않는다.
3. **스케줄링 지역성:** 로컬 큐의 G들은 동일 P에서 실행될 가능성이 높아 cache locality가 향상된다.

**Work-Stealing 알고리즘 (findRunnable):**

P의 로컬 큐가 비었을 때 실행되는 순서:

```go
// runtime/proc.go — findRunnable() 의사 코드 (Go 1.22)
func findRunnable() (gp *g, inheritTime bool) {
    // 1. 로컬 런 큐 확인
    if gp := runqget(_p_); gp != nil {
        return gp, false
    }

    // 2. 글로벌 런 큐 확인 (61번 스케줄마다 1번은 글로벌 우선 — starvation 방지)
    if _g_.m.p.ptr().schedtick%61 == 0 {
        if gp := globrunqget(_p_, 1); gp != nil {
            return gp, false
        }
    }

    // 3. 네트워크 폴러 확인 (epoll/kqueue)
    if netpollinited() && lastpoll != 0 {
        if list := netpoll(0); !list.empty() {
            // ready된 G들 반환
        }
    }

    // 4. 다른 P의 로컬 큐에서 절반을 steal
    for i := 0; i < 4; i++ {
        // 랜덤 P 선택 → runqsteal()로 절반 가져옴
        if gp := runqsteal(_p_, p2, stealRunNextG); gp != nil {
            return gp, false
        }
    }

    // 5. 위 모두 실패 → M을 idle 상태로 전환
    stopm()
}
```

핵심 디테일: steal 시 **대상 P 런 큐의 절반**을 가져온다. 이는 반복적인 steal을 줄이기 위한 설계이며, `schedtick%61 == 0` 조건은 글로벌 큐의 G가 starvation에 빠지지 않도록 하는 fairness 보장 장치다.

**Step 3 — 다양한 관점**

| 관점 | 분석 |
|------|------|
| **성능** | P 도입으로 14-core 머신에서 벤치마크 스루풋이 약 10~20% 향상 (Vyukov 설계 문서). lock contention이 사실상 제거됨 |
| **메모리** | P당 mcache를 보유하므로 `GOMAXPROCS` 증가 시 메모리 사용량도 비례 증가. 각 P의 mcache는 수백 KB 수준 |
| **CPU-bound** | `GOMAXPROCS = runtime.NumCPU()`가 최적. 초과 시 OS 스케줄러의 context switch 비용 증가 |
| **I/O-bound** | `GOMAXPROCS`를 코어 수보다 높게 설정하면 이득인 경우가 있음. syscall 블로킹 시 P가 hand-off되므로, P가 부족하면 runnable G가 대기함 |
| **컨테이너** | Go 1.19+ `runtime/debug.SetMaxThreads`와 `GOMEMLIMIT` 활용. K8s cgroup v2에서 `NumCPU()`가 호스트 전체 코어를 반환하는 문제 → `automaxprocs` 라이브러리(uber-go)로 해결 |

**Step 4 — 구체적 예시**

```go
package main

import (
    "fmt"
    "runtime"
    "sync"
)

func main() {
    // 컨테이너 환경에서 cgroup CPU limit 반영
    // uber-go/automaxprocs를 import하면 init()에서 자동 설정
    fmt.Printf("GOMAXPROCS=%d, NumCPU=%d\n",
        runtime.GOMAXPROCS(0), runtime.NumCPU())

    // P별 로컬 큐 활용 확인: LockOSThread로 M-P 바인딩 관찰
    var wg sync.WaitGroup
    for i := 0; i < runtime.GOMAXPROCS(0); i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            // 이 goroutine은 P의 로컬 큐에서 스케줄됨
            // CPU-bound 작업이면 같은 P에서 연속 실행될 가능성 높음
            sum := 0
            for j := 0; j < 1_000_000; j++ {
                sum += j
            }
            fmt.Printf("goroutine %d done on thread (M)\n", id)
        }(i)
    }
    wg.Wait()
}
```

**프로덕션 GOMAXPROCS 튜닝 사례:**

```go
import _ "go.uber.org/automaxprocs" // cgroup-aware GOMAXPROCS 자동 설정

// K8s Pod spec: resources.limits.cpu = "4"
// 호스트 NumCPU() = 96 → automaxprocs가 GOMAXPROCS=4로 보정
// 이것 없이는 96개 P가 생성되어 GC STW 시간 증가, mcache 메모리 낭비
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| `GOMAXPROCS = NumCPU()` (기본) | 기본값, 대부분 최적 | 컨테이너에서 과대 설정 위험 | 베어메탈, VM |
| `automaxprocs` | cgroup 자동 감지 | 외부 의존성 추가 | K8s/Docker 환경 필수 |
| `GOMAXPROCS = 1` | 동시성 버그 재현, 결정적 실행 | 멀티코어 활용 불가 | 디버깅, 테스트 |
| `GOMAXPROCS > NumCPU()` | I/O-heavy 워크로드에서 유리 | CPU-bound 시 스래싱 | 고빈도 네트워크 서비스 |

**Step 6 — 성장 & 심화 학습**

1. Go 소스 `runtime/proc.go`의 `schedule()`, `findRunnable()`, `runqsteal()` 직접 읽기
2. Dmitry Vyukov의 원본 설계 문서: "Scalable Go Scheduler Design Doc" (2012)
3. `go tool trace`로 P별 goroutine 분배 시각화 — trace viewer에서 Proc 레인 관찰
4. `runtime/metrics`의 `/sched/goroutines:goroutines`, `/sched/latencies:seconds` 모니터링
5. Austin Clements의 GMP 관련 proposal들 (Go issue tracker) 추적

**🎯 면접관 평가 기준:**
- **L6 PASS:** G-M-P 각 역할을 정확히 설명하고, P 도입 이유(lock contention, mcache 효율화)를 구조적으로 설명. work-stealing의 기본 흐름(로컬 → 글로벌 → steal)을 알고 있음. `GOMAXPROCS`가 P 수를 결정한다는 것을 이해.
- **L7 EXCEED:** `schedtick%61` fairness 보장, steal 시 절반을 가져오는 이유, hand-off 메커니즘, 컨테이너 환경에서의 cgroup 문제와 `automaxprocs` 해결책까지 프로덕션 경험 기반으로 논증. `findRunnable` 내부 순서를 정확히 기술.
- **🚩 RED FLAG:** "Goroutine은 경량 스레드입니다"로 끝나는 답변. P의 역할을 모르거나 M과 혼동. `GOMAXPROCS`를 "스레드 수"라고 잘못 설명.

---

### Q2: Cooperative vs Asynchronous Preemption

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Goroutine Scheduler (G-M-P)

**Question:**
Go 1.14 이전의 cooperative preemption과 Go 1.14+의 asynchronous preemption의 차이를 설명하라. Cooperative preemption이 실패하는 구체적인 시나리오를 보여주고, async preemption이 이를 어떻게 해결하는지 OS 시그널 수준까지 설명하라. Async preemption이 도입됨에도 불구하고 여전히 존재하는 한계와, `runtime.Gosched()` 또는 `runtime.LockOSThread()`를 명시적으로 사용해야 하는 경우를 논의하라.

---

**🧒 12살 비유:**
교실에서 발표 시간을 나눠 쓴다고 생각해 보자. Cooperative preemption은 "각자 알아서 5분 뒤에 자리에 앉는" 규칙이다. 대부분의 아이들은 지키지만, 한 명이 신나서 멈추지 않으면 나머지 아이들은 영원히 발표를 못 한다. Async preemption은 선생님이 "타이머가 울리면 무조건 자리에 앉아!"라고 강제하는 것이다. 선생님이 종(시그널)을 치면, 어떤 아이든 멈춰야 한다. 하지만 그 아이가 칠판에 수식을 쓰고 있는 중간이라면(unsafe point), 수식을 끝낼 때까지는 기다려 줘야 한다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

이 질문은 Go 런타임의 진화를 이해하고 있는지를 평가한다. 핵심 평가 포인트: (1) preemption이 왜 필요한지에 대한 시스템 수준 이해, (2) tight loop 문제를 직접 경험했거나 인식하고 있는지, (3) OS 시그널 메커니즘에 대한 저수준 지식, (4) GC와 preemption의 관계 이해. Staff 엔지니어는 "Go에 preemption이 있다"를 넘어 구현의 제약과 트레이드오프를 논의할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

**Cooperative Preemption (Go 1.13 이전):**

Go 컴파일러가 함수 프롤로그에 **스택 확인 코드(stack bound check)**를 삽입한다. 이 코드는 goroutine의 스택이 충분한지 확인하는 동시에, `g.stackguard0` 필드가 `stackPreempt` 값으로 설정되었는지 검사한다. 런타임이 preemption을 요청하면 `g.stackguard0 = stackPreempt`로 설정하고, 다음 함수 호출 시 프롤로그에서 이를 감지하여 `runtime.morestack() → runtime.newstack() → schedule()`로 양보한다.

```go
// 컴파일러가 삽입하는 의사 코드 (모든 함수 진입점)
func someFunction() {
    if SP < g.stackguard0 {  // stackPreempt이면 이 조건이 참
        runtime.morestack()   // → 스케줄러로 양보
    }
    // 실제 함수 본문
}
```

**치명적 한계 — 함수 호출이 없는 tight loop:**

```go
// 이 goroutine은 Go 1.13 이전에서 절대 preempt되지 않는다
go func() {
    for {
        // 함수 호출 없음 → 스택 확인 코드 실행 안 됨
        // CPU를 점유한 채 다른 goroutine이 실행 불가
        i++
    }
}()
// GC STW(Stop-The-World)도 이 goroutine이 양보할 때까지 무한 대기
```

이 문제는 단순히 "한 goroutine이 느려지는" 수준이 아니다. **GC의 STW가 무한정 지연**된다. GC는 모든 goroutine을 safe point에서 멈춰야 하는데, tight loop goroutine은 safe point에 도달하지 않기 때문이다.

**Asynchronous Preemption (Go 1.14+):**

OS 시그널 기반의 비동기 preemption을 도입했다. 구현은 플랫폼별로 다르다:

- **Linux:** `SIGURG` 시그널 사용. `runtime.preemptM()`이 `tgkill()` syscall로 대상 M에 `SIGURG` 전송.
- **macOS:** 동일하게 `SIGURG` 사용. Mach thread API가 아닌 POSIX 시그널 방식.
- **Windows:** `SuspendThread` + `GetThreadContext` + `SetThreadContext` 사용.

`SIGURG`를 선택한 이유: 기존 프로그램이 거의 사용하지 않고, `SA_RESTART`로 syscall을 자동 재시작할 수 있으며, debugger(SIGTRAP, SIGINT 등)와 충돌하지 않는다.

```
시그널 기반 preemption 흐름:
1. sysmon goroutine이 10ms 이상 실행 중인 G 감지
2. runtime.preemptM(mp) 호출
3. tgkill(pid, tid, SIGURG) 전송
4. 시그널 핸들러(sighandler) 실행
5. asyncPreempt() → 현재 레지스터를 G의 스택에 저장
6. G를 _Gpreempted 상태로 전환
7. schedule() 호출 → 다른 G 실행
```

**Safe point과 unsafe point:**

Async preemption도 **어디서나** 발생할 수 있는 것은 아니다. GC의 정확성을 위해 **포인터 맵(liveness map)**이 존재하는 지점에서만 preempt 가능하다. 컴파일러는 각 명령어에 대해 "이 시점에서 어떤 레지스터/스택 슬롯이 포인터인가"를 기록하는데, 모든 명령어에 대해 이를 기록하면 바이너리 크기가 폭증한다. Go 1.14에서는 대부분의 명령어에 대해 이 정보를 생성하지만, 일부 **unsafe point**(예: 런타임 내부의 어셈블리 코드, `write barrier` 중간, 특정 atomic 연산 중)에서는 preemption이 지연된다.

**Step 3 — 다양한 관점**

| 관점 | 분석 |
|------|------|
| **GC 지연시간** | Async preemption 도입으로 GC STW 시간이 예측 가능해짐. tight loop에 의한 무한 STW 지연 제거 |
| **바이너리 크기** | async preempt를 위한 PC-to-liveness 맵 추가로 바이너리 크기 약 5~10% 증가 |
| **디버깅** | `SIGURG` 핸들러가 스택을 조작하므로 `delve` 등 디버거와의 상호작용이 복잡해짐. Go 1.15+에서 개선 |
| **CGO** | C 코드 실행 중에는 Go 시그널 핸들러가 동작하지 않으므로 async preemption 불가. C FFI 호출이 길면 여전히 문제 |
| **실시간성** | 10ms 검사 주기(sysmon)로 인해 마이크로초 수준의 정밀한 스케줄링은 불가. Go는 실시간 OS가 아님 |

**Step 4 — 구체적 예시**

```go
package main

import (
    "fmt"
    "runtime"
    "runtime/debug"
    "time"
)

func main() {
    // Go 1.14+ 에서는 이 tight loop도 preempt 가능
    runtime.GOMAXPROCS(1) // P를 1개로 제한하여 문제를 극대화

    // GC가 정상 동작하는지 확인
    debug.SetGCPercent(100)

    done := make(chan struct{})
    go func() {
        // tight loop — 함수 호출 없음
        // Go 1.13: 이 goroutine이 CPU를 독점, main goroutine 실행 불가
        // Go 1.14+: sysmon이 10ms 후 SIGURG로 preempt
        for i := 0; ; i++ {
            if i%1_000_000_000 == 0 {
                // 이 분기 자체가 cooperative preemption point가 될 수 있음
                // 순수한 tight loop 테스트를 위해선 이 조건도 제거해야 함
            }
        }
    }()

    go func() {
        time.Sleep(100 * time.Millisecond)
        fmt.Println("이 goroutine은 Go 1.14+에서 실행 가능")
        close(done)
    }()

    <-done
}
```

**`runtime.LockOSThread()`가 필요한 실전 케이스:**

```go
func initOpenGL() {
    // OpenGL 컨텍스트는 특정 OS 스레드에 바인딩되어야 함
    runtime.LockOSThread()
    defer runtime.UnlockOSThread()

    // 이 goroutine은 동일한 M에서만 실행됨
    // P는 다른 M으로 hand-off 가능하므로 다른 goroutine은 영향 없음
    window := glfw.CreateWindow(800, 600, "App", nil, nil)
    // ...
}

func callCLibrary() {
    // 일부 C 라이브러리는 thread-local storage에 의존
    runtime.LockOSThread()
    defer runtime.UnlockOSThread()

    C.some_tls_dependent_function()
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| Cooperative preemption (함수 프롤로그) | 오버헤드 최소, 예측 가능 | tight loop 문제, GC STW 지연 | Go 1.13 이하 (레거시) |
| Async preemption (SIGURG) | tight loop 해결, GC 안정화 | 바이너리 크기 증가, unsafe point 존재 | Go 1.14+ 기본 동작 |
| `runtime.Gosched()` 명시 호출 | 정밀한 양보 제어 | 코드 침투적, 개발자 부담 | 특정 스케줄링 순서 보장 필요 시 |
| `runtime.LockOSThread()` | OS 스레드 고정 보장 | 스레드 풀 축소, deadlock 위험 | GUI, TLS 의존 C 라이브러리 |
| `GOEXPERIMENT=preemptibleloops` (실험적) | 루프 백엣지에 preemption point 삽입 | 루프 성능 저하 | 디버깅/테스트 전용 |

**Step 6 — 성장 & 심화 학습**

1. Austin Clements의 proposal: "Non-cooperative goroutine preemption" (Go issue #24543)
2. `runtime/signal_unix.go`의 `sighandler`, `asyncPreempt` 구현 읽기
3. `runtime.sysmon()`의 preemption 감지 로직: `retake()` 함수 분석
4. `go tool objdump`로 함수 프롤로그의 스택 확인 코드 관찰
5. GC의 safe point 개념: Rick Hudson의 "Getting to Go" GopherCon 2018 발표

**🎯 면접관 평가 기준:**
- **L6 PASS:** Cooperative과 async의 차이를 tight loop 예시로 설명. `SIGURG` 시그널 기반이라는 것을 알고, GC STW와의 관계를 이해. `LockOSThread()`의 용도를 최소 1개 제시.
- **L7 EXCEED:** `stackguard0 = stackPreempt` 메커니즘, `sysmon`의 10ms 감지 주기, safe point/unsafe point 개념, 바이너리 크기 영향, CGO에서의 한계까지 논의. `SIGURG` 선택 이유(기존 프로그램과 충돌 방지)를 설명.
- **🚩 RED FLAG:** "Go는 preemptive 스케줄러입니다"로 끝나거나, cooperative과 async의 차이를 모름. tight loop 문제를 인식하지 못함. preemption과 concurrency를 혼동.

---

### Q3: Goroutine Leak 감지, 스택 증식, sysmon

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Goroutine Scheduler (G-M-P)

**Question:**
프로덕션 Go 서비스에서 goroutine leak을 감지하고 디버깅하는 전략을 설명하라. Goroutine 스택의 동적 증식(growable stack) 메커니즘이 메모리 사용량에 미치는 영향을 분석하고, 대량의 goroutine이 존재할 때 GC 성능에 미치는 영향을 논의하라. `sysmon` goroutine의 역할과, 이것이 일반 goroutine과 어떻게 다른지 설명하라.

---

**🧒 12살 비유:**
학교 도서관에서 책을 빌린다고 생각해 보자. Goroutine leak은 "책을 빌려놓고 돌려주지 않는 것"이다. 한두 권은 괜찮지만, 매일 10권씩 빌리고 안 돌려주면 도서관 선반이 비게 된다(메모리 고갈). 스택 증식은 "처음에 작은 가방을 들고 가서, 책이 많아지면 더 큰 가방으로 바꾸는 것"이다 — 처음부터 큰 가방을 들고 다니면 낭비니까. `sysmon`은 "도서관 관리인"이다. 다른 학생들(goroutine)처럼 줄 서서 차례를 기다리지 않고, 자기만의 통로를 쓴다. 연체된 책을 찾고, 문 잠그는 시간을 알리고, 줄 서 있는데 너무 오래 기다리는 학생이 있으면 다른 창구를 열어주는 역할을 한다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

이 질문은 프로덕션 운영 경험과 런타임 내부 지식을 동시에 평가한다. 핵심 포인트: (1) goroutine leak을 실제로 겪고 해결한 경험, (2) 스택 메모리 관리에 대한 저수준 이해, (3) 대규모 시스템에서 goroutine 수가 GC에 미치는 영향 인식, (4) `sysmon`이라는 특수한 런타임 컴포넌트에 대한 지식. Staff 레벨에서는 "goroutine leak을 pprof로 찾습니다"를 넘어, 예방적 설계와 시스템적 모니터링 전략을 제시할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

**Goroutine Leak의 주요 원인:**

1. **채널 블로킹:** unbuffered 채널에 송신/수신자 없이 대기
2. **context 미전파:** 취소 시그널이 하위 goroutine에 도달하지 않음
3. **무한 루프 + 외부 호출:** HTTP 클라이언트에 타임아웃 미설정
4. **WaitGroup 불일치:** `Add`와 `Done` 카운트 불일치
5. **select 문의 default 없는 다중 채널 대기:** 모든 채널이 닫히지 않으면 영구 대기

```go
// 전형적인 goroutine leak 패턴 #1: 수신자 없는 채널
func leakyFunction() {
    ch := make(chan int)
    go func() {
        result := expensiveComputation()
        ch <- result // 아무도 수신하지 않으면 이 goroutine은 영원히 블로킹
    }()
    // 에러 발생 시 ch를 수신하지 않고 return → leak
    if err != nil {
        return // ch <- result에서 블로킹된 goroutine은 GC 불가
    }
    <-ch
}

// 수정: context 기반 취소
func fixedFunction(ctx context.Context) error {
    ch := make(chan int, 1) // buffered로 변경: 수신자 없어도 goroutine이 송신 후 종료 가능
    go func() {
        result := expensiveComputation()
        select {
        case ch <- result:
        case <-ctx.Done():
            // context 취소 시 정리하고 종료
            return
        }
    }()

    select {
    case result := <-ch:
        return process(result)
    case <-ctx.Done():
        return ctx.Err()
    }
}
```

**Goroutine Leak 감지 전략 (프로덕션 3-Layer):**

```
Layer 1: 메트릭 모니터링 (사전 감지)
├── runtime.NumGoroutine() → Prometheus gauge로 노출
├── 알럿: goroutine 수가 baseline의 2x 초과 시
└── 그래프: 시간에 따른 goroutine 수 추이 (우상향 = leak 의심)

Layer 2: pprof 분석 (원인 특정)
├── /debug/pprof/goroutine?debug=1  → 현재 goroutine 목록
├── /debug/pprof/goroutine?debug=2  → 전체 스택 트레이스
└── go tool pprof -top profile.pb.gz → goroutine 생성 위치별 집계

Layer 3: 테스트 시점 탐지 (예방)
├── goleak (uber-go/goleak): 테스트 종료 시 잔존 goroutine 검출
└── t.Cleanup + runtime.NumGoroutine() diff 비교
```

```go
// uber-go/goleak 사용 예시
func TestNoLeak(t *testing.T) {
    defer goleak.VerifyNone(t,
        goleak.IgnoreTopFunction("go.opencensus.io/stats/view.(*worker).start"),
        // 알려진 백그라운드 goroutine은 무시
    )
    // 테스트 코드...
}
```

**스택 증식 (Growable Stack) 메커니즘:**

Go는 **contiguous stack** 방식을 사용한다 (Go 1.4+, 이전에는 segmented stack).

```
초기 스택 할당: 4KB (Go 1.22, _StackMin)
  ↓ 함수 호출 시 스택 프롤로그에서 확인
  ↓ SP < stackguard0 이면 → runtime.morestack()
  ↓ 새 스택 = 기존의 2배 크기 할당
  ↓ 기존 스택 내용을 새 스택으로 복사
  ↓ 모든 스택 포인터 조정 (pointer adjustment)
  ↓ 기존 스택 해제
```

**Contiguous stack vs Segmented stack:**

| 항목 | Segmented (Go 1.3 이전) | Contiguous (Go 1.4+) |
|------|------------------------|----------------------|
| 방식 | 새 세그먼트 연결 | 전체 복사 + 2x 확장 |
| hot split 문제 | 있음 (경계에서 반복 alloc/free) | 없음 |
| 포인터 복잡도 | 세그먼트 간 참조 관리 | 복사 시 포인터 일괄 조정 |
| 축소 | 세그먼트 해제 | GC 시 1/2로 축소 (사용량 < 1/4일 때) |

**메모리 영향 분석:**

```
goroutine 수 × 스택 크기 = 스택 메모리 사용량

예시:
100만 goroutine × 4KB(최소) = 약 4GB 스택 메모리만으로
100만 goroutine × 8KB(평균) = 약 8GB

추가 오버헤드:
- 각 goroutine의 runtime.g 구조체: ~400바이트
- 100만 × 400B = 약 400MB 메타데이터
```

스택 축소(shrink)는 GC 과정에서 발생한다. `runtime.scanstack()`이 goroutine 스택을 스캔할 때, 사용량이 할당량의 1/4 미만이면 다음 GC 사이클에서 절반으로 축소한다.

**대량 goroutine이 GC에 미치는 영향:**

1. **스택 스캔 비용:** GC는 모든 goroutine 스택을 루트로 스캔해야 한다. goroutine이 많을수록 mark phase 시간 증가.
2. **STW 시간:** Go 1.22에서도 일부 GC 단계(stack scan 시작)에는 STW가 필요. goroutine 수에 비례.
3. **메모리 압력:** 스택 메모리가 힙 외 영역이지만, 시스템 전체 메모리 압력을 증가시킴.

```go
// 프로덕션 모니터링: runtime/metrics 활용 (Go 1.16+)
import "runtime/metrics"

func collectSchedulerMetrics() {
    samples := []metrics.Sample{
        {Name: "/sched/goroutines:goroutines"},
        {Name: "/sched/latencies:seconds"},
        {Name: "/gc/cycles/total:gc-cycles"},
        {Name: "/memory/classes/heap/stacks:bytes"}, // 스택 메모리
    }
    metrics.Read(samples)
    // Prometheus/OpenTelemetry로 export
}
```

**sysmon Goroutine:**

`sysmon`은 Go 런타임의 **감시자(watchdog)**로, 일반 goroutine과 근본적으로 다르다:

```
sysmon의 특수성:
1. P 없이 실행 — M에 직접 바인딩, 스케줄러의 제어를 받지 않음
2. 독립 OS 스레드 — runtime.main()에서 newm(sysmon, nil, -1)로 생성
3. 스스로 sleep 주기 조절 — idle 시 최대 10ms까지 sleep, 활동 감지 시 20μs로 단축
```

**sysmon의 핵심 역할 5가지:**

```go
// runtime/proc.go — sysmon() 의사 코드
func sysmon() {
    for {
        // 1. 네트워크 폴링: epoll/kqueue 결과 확인 → ready goroutine을 런 큐에 삽입
        netpoll(0) // non-blocking poll

        // 2. Preemption: 10ms 이상 실행 중인 G 감지 → retake()
        retake(now) // preemptone() 호출 → SIGURG 전송 (Go 1.14+)

        // 3. 강제 GC: 2분 이상 GC 미실행 시 runtime.GC() 트리거
        if lastgc + forcegcperiod < now {
            forcegchelper()
        }

        // 4. Scavenge: 미사용 메모리를 OS에 반환
        scavenge()

        // 5. 타이머 확인: 만료된 타이머의 콜백 실행 보장
        checkTimers()

        // 동적 sleep: 20μs ~ 10ms
        usleep(delay)
    }
}
```

**Step 3 — 다양한 관점**

| 관점 | 분석 |
|------|------|
| **운영** | goroutine 수 모니터링은 Go 서비스의 가장 기본적인 health indicator. 우상향 그래프 = leak. Grafana 대시보드에 필수 포함 |
| **설계** | goroutine leak 예방의 핵심은 "모든 goroutine에 종료 경로 보장". context 전파 + 명시적 취소가 가장 효과적 |
| **성능** | 100만 goroutine 자체는 가능하지만, GC 스택 스캔 비용이 문제. worker pool 패턴으로 상한을 제어하는 것이 현실적 |
| **테스트** | `goleak`을 CI에 통합하면 leak을 코드 리뷰 단계에서 차단 가능. regression 방지에 매우 효과적 |
| **디버깅** | `GODEBUG=gctrace=1`과 `SIGQUIT`(kill -3)으로 즉시 모든 goroutine 스택 덤프 가능 |

**Step 4 — 구체적 예시**

```go
// 프로덕션 goroutine pool 패턴: 상한 제어 + graceful shutdown
type WorkerPool struct {
    maxWorkers int
    tasks      chan func()
    wg         sync.WaitGroup
}

func NewWorkerPool(maxWorkers, queueSize int) *WorkerPool {
    p := &WorkerPool{
        maxWorkers: maxWorkers,
        tasks:      make(chan func(), queueSize),
    }
    for i := 0; i < maxWorkers; i++ {
        p.wg.Add(1)
        go p.worker()
    }
    return p
}

func (p *WorkerPool) worker() {
    defer p.wg.Done()
    for task := range p.tasks { // 채널 닫히면 자동 종료 → leak 방지
        task()
    }
}

func (p *WorkerPool) Submit(task func()) error {
    select {
    case p.tasks <- task:
        return nil
    default:
        return errors.New("worker pool is full") // back-pressure
    }
}

func (p *WorkerPool) Shutdown() {
    close(p.tasks) // 모든 worker goroutine 종료 유도
    p.wg.Wait()    // 모든 worker 종료 대기
}
```

```go
// goroutine leak 디버깅 세션 예시
// 1. 메트릭에서 goroutine 수 이상 감지
// 2. pprof로 원인 특정
func debugLeakInProd() {
    // HTTP 서버에 pprof 핸들러 등록 (내부 관리 포트)
    go func() {
        mux := http.NewServeMux()
        mux.HandleFunc("/debug/pprof/", pprof.Index)
        mux.HandleFunc("/debug/pprof/goroutine", pprof.Handler("goroutine").ServeHTTP)
        http.ListenAndServe("localhost:6060", mux) // 외부 노출 금지!
    }()

    // 커맨드라인에서:
    // go tool pprof http://localhost:6060/debug/pprof/goroutine
    // (pprof) top         → 어디서 goroutine이 가장 많이 생성되는지
    // (pprof) traces      → 전체 스택 트레이스
    // (pprof) web          → 호출 그래프 시각화

    // curl http://localhost:6060/debug/pprof/goroutine?debug=2
    // → 모든 goroutine의 상태와 대기 시간 출력
    // "chan receive" 상태로 수천 개가 대기 중이면 해당 채널 추적
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| goroutine-per-request | 단순, Go 관용적 | leak 위험, GC 부담 | 요청량 예측 가능한 서비스 |
| Worker pool (고정 크기) | goroutine 수 제한, 예측 가능 | 큐 overflow 처리 필요 | 높은 처리량, 안정성 중시 |
| `semaphore.Weighted` | 동적 제어, 표준 라이브러리 | pool 대비 오버헤드 | 동시 실행 수만 제한할 때 |
| `errgroup.Group` | 에러 전파 + context 취소 내장 | 최대 동시 수 제한 옵션은 `SetLimit` | 한정된 병렬 작업 그룹 |
| `goleak` in CI | leak 사전 방지 | false positive 관리 필요 | 모든 Go 프로젝트 (필수) |

**Step 6 — 성장 & 심화 학습**

1. `runtime/proc.go`의 `sysmon()`, `retake()`, `newproc()` 소스 읽기
2. `runtime/stack.go`의 `newstack()`, `copystack()`, `shrinkstack()` 분석
3. Bryan Boreham의 "Reduce Go GC latency" GopherCon EU 발표 — goroutine 수와 GC 관계
4. uber-go/goleak 소스와 설계 철학: 어떻게 잔존 goroutine을 감지하는가
5. `GODEBUG=schedtrace=1000` 환경변수로 스케줄러 상태 1초마다 출력하여 분석
6. Go 1.21+의 `runtime/trace` v2 API로 goroutine 생성/종료 이벤트 추적

**🎯 면접관 평가 기준:**
- **L6 PASS:** goroutine leak의 주요 원인(채널 블로킹, context 미전파)을 설명하고 `pprof`와 `runtime.NumGoroutine()`으로 감지하는 방법을 제시. 스택이 동적으로 증가한다는 것을 알고, 초기 크기가 작다는 것을 이해. `sysmon`의 존재와 preemption 역할을 인지.
- **L7 EXCEED:** 3-Layer 감지 전략(메트릭 → pprof → goleak)을 체계적으로 제시. contiguous stack의 복사+포인터 조정 메커니즘을 설명. GC 스택 스캔 비용과 goroutine 수의 관계를 정량적으로 분석. `sysmon`이 P 없이 독립 M에서 실행되는 이유와 5가지 역할을 상세히 설명. worker pool vs goroutine-per-request의 트레이드오프를 프로덕션 경험으로 논증.
- **🚩 RED FLAG:** "goroutine은 가벼우니까 많이 만들어도 됩니다"로 끝나는 답변. leak 감지 방법을 모르거나 `pprof`를 사용해 본 적 없음. 스택이 고정 크기라고 잘못 설명. `sysmon`을 모름.

---

## 2. Memory Model & GC


> 대상: FAANG L6/L7 (Staff/Principal Engineer)
> 총 문항: 3개 (Q4~Q6) | 난이도: ⭐⭐⭐⭐⭐
> 런타임: Go 1.22+

## 목차

- [Q4: Happens-before & Memory Barriers](#q4-happens-before--memory-barriers)
- [Q5: Tricolor Mark-Sweep & Write Barrier](#q5-tricolor-mark-sweep--write-barrier)
- [Q6: GOGC / GOMEMLIMIT 튜닝 & Ballast](#q6-gogc--gomemlimit-튜닝--ballast)

---

### Q4: Happens-before & Memory Barriers

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Memory Model & GC

**Question:**
"Go의 memory model에서 happens-before 관계를 정의하고, 이것이 컴파일러/CPU 수준의 reordering과 어떤 관계인지 설명하세요. `sync.Mutex`, channel send/receive, `sync/atomic` 각각이 어떤 happens-before guarantee를 제공하는지 명시하고, 이 보장이 없을 때 실제 프로덕션에서 어떤 종류의 버그가 발생하는지 구체적 사례와 함께 논하세요."

---

**🧒 12살 비유:**
너랑 친구가 각자 다른 방에서 공유 칠판에 글을 쓴다고 상상해봐. 너는 "A = 1"을 쓰고, 친구는 "B = 2"를 써. 그런데 칠판이 마법 칠판이라 글을 쓴 순서가 뒤바뀔 수 있어 — 네가 먼저 썼는데 친구 방에서 보면 아직 안 써진 것처럼 보이는 거야. "happens-before"는 "이 글이 저 글보다 확실히 먼저 보인다"는 약속이야. 열쇠(Mutex)를 넘겨주거나, 전화(channel)로 "다 썼어!"라고 알려주면 그때서야 칠판의 내용이 확실히 보이는 거지.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

빅테크 면접관은 이 질문으로 세 가지를 평가한다:
1. **하드웨어 수준 이해**: 현대 CPU가 store buffer, write-combining buffer, cache coherence protocol(MESI/MOESI)을 통해 메모리 연산을 reorder한다는 사실을 아는가.
2. **언어 명세 vs 구현의 구분**: Go Memory Model은 "어떤 조건에서 하나의 goroutine이 다른 goroutine의 write를 관측할 수 있는가"를 정의하며, 이것은 컴파일러 최적화와 CPU reordering 모두를 제약한다.
3. **실전 디버깅 능력**: happens-before 위반 버그는 race detector 없이는 거의 재현 불가능하고, ARM64 같은 weakly-ordered 아키텍처에서만 발현되기도 한다. Staff 엔지니어는 이런 버그를 원인부터 진단할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

Go Memory Model(2022년 리비전, Russ Cox가 주도)은 C++ memory model의 DRF-SC(Data-Race-Free programs are Sequentially Consistent) 원칙을 채택한다. 핵심 정의:

> 만약 두 이벤트 e1, e2에 대해 e1이 e2보다 **happens-before**이면, e2는 e1의 효과를 반드시 관측한다.

happens-before는 **partial order**다. 관계가 없는 두 이벤트는 어떤 순서로든 관측될 수 있다.

**동기화 원시자별 보장:**

```go
// === 1. sync.Mutex ===
// Unlock(m) happens-before 이후의 Lock(m)
var mu sync.Mutex
var data int

// Goroutine A
mu.Lock()
data = 42          // ← 이 write는
mu.Unlock()        // ← Unlock 시점에 "publish"됨

// Goroutine B
mu.Lock()          // ← 이 Lock이 A의 Unlock 이후이면
fmt.Println(data)  // ← 42가 보장됨 (happens-before)
mu.Unlock()

// === 2. Channel ===
// ch <- v (send) happens-before <-ch (receive) 완료
// unbuffered channel: receive happens-before send 완료
// buffered channel(cap C): i번째 receive happens-before (i+C)번째 send 완료
ch := make(chan struct{})
var result string

// Goroutine A
result = "computed"
ch <- struct{}{}   // ← send happens-before...

// Goroutine B
<-ch               // ← ...receive
fmt.Println(result) // ← "computed" 보장

// === 3. sync/atomic ===
// Go 1.19+: atomic 연산은 sequentially consistent
// atomic.Store(&x, v) happens-before 이후의 atomic.Load(&x)가 v를 관측
var flag atomic.Bool
var payload int

// Goroutine A
payload = 100
flag.Store(true)   // ← atomic store = release fence 역할

// Goroutine B
if flag.Load() {   // ← atomic load = acquire fence 역할
    // payload == 100 보장 (Go 1.19+ 명세)
    fmt.Println(payload)
}
```

**컴파일러 / CPU reordering과의 관계:**

Go 컴파일러(SSA backend)는 동기화 지점 사이의 메모리 접근을 자유롭게 reorder할 수 있다. `sync.Mutex.Lock()`을 호출하면 컴파일러는 해당 지점을 기준으로 reordering barrier를 삽입한다. CPU 수준에서는:

| 아키텍처 | 메모리 모델 | Go가 삽입하는 barrier |
|----------|------------|----------------------|
| x86-64 | TSO (Total Store Order) | `MFENCE` 또는 `LOCK` prefix (거의 불필요) |
| ARM64 | Weakly ordered | `DMB ISH` (Data Memory Barrier, Inner Shareable) |
| RISC-V | RVWMO | `fence rw, rw` |

x86-64의 TSO 모델은 store-store, load-load reordering을 금지하므로 많은 버그가 x86에서는 숨어 있다가 ARM64 전환 시 발현된다.

**Step 3 — 다양한 관점**

| 관점 | 분석 |
|------|------|
| **정확성** | happens-before 없이 공유 변수 접근 = data race = Go 명세상 **undefined behavior**. 단순히 "잘못된 값"이 아니라 프로그램 전체의 동작이 정의되지 않음. |
| **성능** | memory barrier는 CPU pipeline stall을 유발. ARM64에서 `DMB ISH`는 수십 나노초. 핫 루프에서 불필요한 동기화는 성능에 직접 영향. |
| **이식성** | x86에서 통과한 테스트가 ARM64(AWS Graviton, Apple Silicon)에서 실패하는 사례가 빈번. race detector(`-race`)는 happens-before 기반 분석이므로 아키텍처 독립적으로 탐지 가능. |
| **스케일** | goroutine 수천 개가 공유 상태에 접근하는 시스템에서 happens-before 관계가 명확하지 않으면 디버깅 비용이 지수적으로 증가. |

**Step 4 — 구체적 예시: 프로덕션 버그 사례**

```go
// 🚩 실제 프로덕션 버그 패턴: "double-checked locking gone wrong"
// Go 1.18 이전에 일부 프로젝트에서 발견된 패턴

type Singleton struct {
    data map[string]string
}

var instance *Singleton
var mu sync.Mutex

// ❌ BROKEN: data race on `instance` read outside lock
func GetInstance() *Singleton {
    if instance != nil {  // ← 동기화 없는 read!
        return instance   // ← 컴파일러/CPU가 아래 write를 reorder할 수 있음
    }
    mu.Lock()
    defer mu.Unlock()
    if instance == nil {
        s := &Singleton{}
        s.data = make(map[string]string)
        s.data["key"] = "value"
        instance = s  // ← ARM64에서: 포인터 write가 map 초기화보다 먼저 보일 수 있음!
    }
    return instance
}

// ✅ CORRECT: sync.Once 사용 (내부에서 atomic + Mutex 조합)
var once sync.Once
var correctInstance *Singleton

func GetInstanceCorrect() *Singleton {
    once.Do(func() {
        s := &Singleton{}
        s.data = make(map[string]string)
        s.data["key"] = "value"
        correctInstance = s
    })
    return correctInstance
    // sync.Once.Do의 return happens-before 이후 모든 Do 호출의 return
}

// ✅ ALTERNATIVE: atomic.Pointer (Go 1.19+, lock-free fast path)
var atomicInstance atomic.Pointer[Singleton]

func GetInstanceAtomic() *Singleton {
    if p := atomicInstance.Load(); p != nil {
        return p  // ← atomic load → happens-before 보장
    }
    mu.Lock()
    defer mu.Unlock()
    if p := atomicInstance.Load(); p != nil {
        return p
    }
    s := &Singleton{data: map[string]string{"key": "value"}}
    atomicInstance.Store(s)  // ← atomic store → 이전 write 모두 visible
    return s
}
```

```go
// 🚩 또 다른 실전 패턴: 설정 reload race
// 서비스가 SIGHUP으로 설정을 reload하는데, 동기화 없이 포인터 교체

type Config struct {
    Timeout  time.Duration
    MaxRetry int
    Endpoints []string  // ← slice header는 3 words (ptr, len, cap)
}

// ❌ BROKEN: slice header의 부분 write가 관측될 수 있음
var globalConfig *Config  // data race!

// ✅ CORRECT: atomic.Value 사용
var safeConfig atomic.Value  // atomic.Value.Store/Load는 SC 보장

func ReloadConfig() {
    newCfg := &Config{
        Timeout:   5 * time.Second,
        MaxRetry:  3,
        Endpoints: []string{"host1:8080", "host2:8080"},
    }
    safeConfig.Store(newCfg)  // happens-before 이후의 Load
}

func HandleRequest() {
    cfg := safeConfig.Load().(*Config)
    // cfg의 모든 필드가 완전히 초기화된 상태로 보임
    for _, ep := range cfg.Endpoints {
        // 안전하게 순회 가능
        _ = ep
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| `sync.Mutex` | 가장 명확한 happens-before, 디버깅 용이 | contention 시 goroutine parking 비용, lock convoy | 복잡한 다중 필드 업데이트, critical section이 짧을 때 |
| `sync.RWMutex` | read 다수 / write 소수 시 처리량 향상 | write starvation 가능, 코드 복잡도 증가 | 설정 조회처럼 read-heavy 패턴 |
| `sync/atomic` | lock-free, 나노초 수준, 단일 변수 SC 보장 | 복수 변수 원자적 업데이트 불가, 코드 가독성 저하 | 카운터, 플래그, 포인터 swap |
| Channel | CSP 모델, 데이터 소유권 이전이 자연스러움 | 생성/GC 오버헤드, buffered일 때 back-pressure 설계 필요 | goroutine 간 작업 파이프라인, 결과 전달 |
| `sync.Once` | 초기화 패턴에 최적, 내부적으로 atomic fast path | 한 번만 실행, 에러 시 재시도 불가 (Go 1.21 `OnceFunc`으로 해결) | singleton, lazy init |

**Step 6 — 성장 & 심화 학습**

1. **필독 문서**: [The Go Memory Model](https://go.dev/ref/mem) (2022 리비전) — Russ Cox의 3부작 블로그("Hardware Memory Models", "Programming Language Memory Models", "Updating the Go Memory Model")와 함께 읽을 것.
2. **실습**: `-race` 플래그로 기존 프로젝트 전체 테스트 실행. ThreadSanitizer 기반이므로 false negative는 있어도 false positive는 없음.
3. **아키텍처 확장**: ARM64(Graviton) 전환 시 CI에 ARM64 runner 추가하여 memory ordering 관련 regression 탐지.
4. **심화**: `runtime/internal/atomic` 소스 코드를 아키텍처별로 비교 (amd64 vs arm64).

**🎯 면접관 평가 기준:**

- **L6 PASS**: happens-before 정의를 정확히 서술하고, Mutex/channel/atomic 각각의 보장을 구분. data race = undefined behavior임을 명시. race detector 사용 경험.
- **L7 EXCEED**: CPU memory model(TSO vs weakly-ordered)과 Go 컴파일러 reordering의 관계를 설명. x86→ARM64 마이그레이션 시 발현되는 버그 패턴을 구체적으로 논함. `sync.Once` 내부 구현(atomic fast path + mutex slow path)을 설명.
- **🚩 RED FLAG**: "Go는 goroutine이라 thread-safe" 발언. atomic과 mutex의 happens-before 차이를 모름. data race를 "그냥 잘못된 값 나오는 것" 정도로 이해.

---

### Q5: Tricolor Mark-Sweep & Write Barrier

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Memory Model & GC

**Question:**
"Go 런타임의 garbage collector가 사용하는 tricolor mark-sweep 알고리즘을 설명하고, concurrent marking 중 mutator(애플리케이션 goroutine)가 포인터를 수정할 때 발생하는 문제를 어떻게 해결하는지 논하세요. write barrier의 구체적 동작, GC의 각 phase(off → mark → mark termination → sweep)에서 STW가 발생하는 시점과 그 duration을 줄이기 위해 Go 팀이 적용한 최적화를 설명하세요."

---

**🧒 12살 비유:**
방 청소를 한다고 생각해봐. 장난감이 엄청 많은데, 쓰는 것(살아있는 객체)과 안 쓰는 것(쓰레기)을 구분해야 해. 세 가지 색 스티커를 쓰는 거야: **흰색** = "아직 안 봤어", **회색** = "봤는데 이게 가리키는 것도 봐야 해", **검은색** = "다 확인 완료". 문제는 네가 스티커 붙이는 동안 동생이 계속 장난감을 옮기고 있다는 거야! 동생이 검은색 스티커 붙은 상자에 흰색 장난감을 넣어버리면 그 장난감은 영영 안 보게 돼서 버려질 수 있어. 그래서 "동생아, 뭔가 옮길 때마다 메모 남겨줘!"(write barrier)라는 규칙을 만드는 거야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

GC는 Go의 가장 핵심적인 런타임 구성요소이며, latency-sensitive 서비스에서는 GC pause가 SLO 위반의 직접적 원인이 된다. 면접관은 다음을 평가한다:
1. **알고리즘 수준 이해**: tricolor abstraction이 단순한 mark-sweep을 concurrent하게 확장하는 방법.
2. **invariant 사고**: concurrent GC의 correctness를 보장하는 **tri-color invariant**와 이를 유지하는 write barrier의 역할.
3. **시스템 수준 최적화 인식**: STW 구간 최소화, assist mechanism, pacing 알고리즘 등 Go 팀의 엔지니어링 결정에 대한 이해.

**Step 2 — 핵심 기술 설명**

**Tricolor Abstraction:**

모든 힙 객체를 세 가지 색으로 분류:
- **White (흰색)**: 아직 방문하지 않음 → GC 완료 후 이 색이면 수거 대상.
- **Gray (회색)**: 방문했지만, 이 객체가 참조하는 다른 객체를 아직 스캔하지 않음.
- **Black (검은색)**: 방문 완료. 이 객체와 이 객체가 참조하는 모든 객체를 스캔함.

```
알고리즘 흐름:
1. 모든 root(goroutine 스택, 전역 변수)에서 참조하는 객체를 Gray로 마킹
2. Gray 셋에서 객체 하나를 꺼냄
3. 해당 객체가 참조하는 모든 White 객체를 Gray로 변경
4. 해당 객체를 Black으로 변경
5. Gray 셋이 빌 때까지 반복
6. 남은 White 객체 = garbage → sweep
```

**Tri-Color Invariant (Strong):**
> "검은색 객체가 흰색 객체를 직접 참조해서는 안 된다."

이 invariant가 깨지면 살아있는 객체가 수거되는(dangling pointer) 치명적 버그가 발생한다.

**Concurrent Marking의 문제:**

Mutator(애플리케이션 goroutine)가 marking 중에 포인터를 수정하면 invariant가 깨질 수 있다:

```
시나리오 (Dijkstra의 예시):
1. 객체 A(Black)가 객체 B(Gray)를 참조, B가 객체 C(White)를 참조
2. Mutator가 A.ptr = C로 변경 (A → C 직접 참조)
3. Mutator가 B.ptr = nil로 변경 (B → C 참조 제거)
4. GC가 B를 스캔 → C를 발견 못함
5. A는 이미 Black → 다시 스캔 안 함
6. C는 White로 남음 → ⚠️ 살아있는 객체 C가 수거됨!
```

**Go의 Write Barrier (Hybrid Write Barrier, Go 1.17+):**

Go는 **Dijkstra insertion barrier**와 **Yuasa deletion barrier**를 결합한 **hybrid write barrier**를 사용한다:

```go
// 의사 코드: hybrid write barrier
// slot = 포인터 슬롯, new = 새 값
func writeBarrier(slot *unsafe.Pointer, new unsafe.Pointer) {
    old := *slot

    // Yuasa deletion barrier: 덮어쓰이는 값(old)을 shade
    if old != nil {
        shade(old)  // old를 Gray로 마킹
    }

    // Dijkstra insertion barrier: 새 값(new)을 shade
    if new != nil {
        shade(new)  // new를 Gray로 마킹
    }

    *slot = new  // 실제 포인터 업데이트
}
```

Hybrid write barrier의 핵심 이점:
- **스택 re-scan 불필요**: 기존 Dijkstra barrier만 쓸 때는 marking 종료 시 모든 goroutine 스택을 STW로 재스캔해야 했음. Hybrid barrier는 deletion barrier가 이를 커버하므로 스택 re-scan을 제거.
- **STW 시간 대폭 단축**: 스택 re-scan이 없으므로 mark termination의 STW가 수십 마이크로초 수준.

**GC Phase 상세:**

```
┌─────────────────────────────────────────────────────────────────┐
│                        GC Cycle                                 │
│                                                                 │
│  ┌──────┐   ┌──────────────────────────┐   ┌───────┐  ┌──────┐ │
│  │ STW  │   │    Concurrent Mark       │   │  STW  │  │Conc. │ │
│  │ Mark │   │  (mutator + GC worker    │   │ Mark  │  │Sweep │ │
│  │Setup │   │   동시 실행)              │   │ Term  │  │      │ │
│  │~10μs │   │  (대부분의 시간)          │   │~10μs  │  │      │ │
│  └──────┘   └──────────────────────────┘   └───────┘  └──────┘ │
│                                                                 │
│  Phase 1     Phase 2                        Phase 3    Phase 4  │
│  - write     - root 스캔(스택, 전역)        - gray→0   - span   │
│    barrier   - 힙 객체 트레이싱              확인       단위     │
│    활성화    - GC assist(할당 속도 비례)     - write    회수     │
│  - root      - 25% CPU 사용 목표             barrier            │
│    준비                                      비활성화           │
└─────────────────────────────────────────────────────────────────┘
```

| Phase | STW? | Duration | 하는 일 |
|-------|------|----------|---------|
| Mark Setup | Yes | ~10-30μs | write barrier 활성화, root set 준비 |
| Concurrent Mark | No | ms~수십ms (힙 크기 비례) | root 스캔, 힙 트레이싱, GC assist |
| Mark Termination | Yes | ~10-30μs | gray 셋 비었는지 확인, write barrier 비활성화 |
| Concurrent Sweep | No | 백그라운드 | span 단위로 white 객체 회수, 다음 할당 시 lazy sweep도 수행 |

**GC Assist Mechanism:**

Concurrent marking 중 mutator의 할당 속도가 GC 속도를 초과하면 OOM 위험이 생긴다. Go는 **GC assist**로 이를 방어한다:

```go
// runtime/malloc.go 의사 로직
func mallocgc(size uintptr, ...) unsafe.Pointer {
    // GC가 진행 중이고, 이 goroutine이 "빚"(할당한 만큼 마킹 안 함)이 있으면
    if gcAssistAlloc() {
        // 할당량에 비례한 marking 작업을 직접 수행
        // → 이 goroutine의 latency가 증가하지만 OOM 방지
    }
    // 실제 할당 진행
}
```

**Step 3 — 다양한 관점**

| 관점 | 분석 |
|------|------|
| **Latency** | Go 1.8+ 이후 STW는 거의 항상 sub-100μs. P99 latency가 중요한 서비스(거래 시스템, 실시간 API)에서도 acceptable. |
| **Throughput** | GC worker가 25% CPU를 사용 (GOMAXPROCS=4일 때 1 코어). 높은 할당률에서는 GC assist로 mutator가 추가 비용 부담. |
| **메모리 효율** | tricolor은 compaction을 하지 않음 → fragmentation 가능. Go는 size class 기반 allocator(tcmalloc 계열)로 완화. |
| **대규모 힙** | 힙이 수십 GB일 때 marking phase가 길어짐 → GOMEMLIMIT(Go 1.19+)으로 GC 빈도 제어 가능. |

**Step 4 — 구체적 예시: GC 동작 관찰**

```go
package main

import (
    "fmt"
    "os"
    "runtime"
    "runtime/debug"
    "time"
)

func main() {
    // GC 통계 활성화
    // 실행: GODEBUG=gctrace=1 go run main.go
    // 출력 예시:
    // gc 1 @0.012s 2%: 0.011+1.2+0.009 ms clock,
    //                   0.044+0.3/1.0/0+0.036 ms cpu,
    //                   4->4->1 MB, 4 MB goal, 0 MB stacks, 0 MB globals, 4 P
    //
    // 해석:
    // 0.011+1.2+0.009 = STW1 + concurrent mark + STW2 (ms)
    // 4->4->1 = mark 시작 힙 → mark 종료 힙 → live 힙 (MB)

    // 프로그래밍 방식으로 GC 통계 수집
    var stats debug.GCStats
    debug.ReadGCStats(&stats)

    var memStats runtime.MemStats
    runtime.ReadMemStats(&memStats)

    fmt.Fprintf(os.Stderr, "GC cycles: %d\n", stats.NumGC)
    fmt.Fprintf(os.Stderr, "Last pause: %v\n", stats.Pause[0])
    fmt.Fprintf(os.Stderr, "Total pause: %v\n", stats.PauseTotal)
    fmt.Fprintf(os.Stderr, "HeapAlloc: %d MB\n", memStats.HeapAlloc/1024/1024)
    fmt.Fprintf(os.Stderr, "HeapSys: %d MB\n", memStats.HeapSys/1024/1024)
    fmt.Fprintf(os.Stderr, "NextGC: %d MB\n", memStats.NextGC/1024/1024)

    // 할당 압박 시뮬레이션: GC assist 관찰
    start := time.Now()
    var sink []*[1024]byte
    for i := 0; i < 1_000_000; i++ {
        sink = append(sink, new([1024]byte))
    }
    elapsed := time.Since(start)
    // GC assist가 발동하면 elapsed가 예상보다 크게 나옴
    fmt.Fprintf(os.Stderr, "Allocation took: %v (includes GC assist)\n", elapsed)

    runtime.KeepAlive(sink) // escape 방지용
}
```

```go
// 프로덕션 GC 모니터링: runtime/metrics (Go 1.16+)
import "runtime/metrics"

func collectGCMetrics() {
    // 원하는 메트릭 정의
    descs := []metrics.Sample{
        {Name: "/gc/cycles/total:gc-cycles"},
        {Name: "/gc/pauses/total:seconds"},
        {Name: "/gc/heap/goal:bytes"},
        {Name: "/gc/heap/live:bytes"},
    }
    metrics.Read(descs)

    for _, d := range descs {
        switch d.Value.Kind() {
        case metrics.KindUint64:
            fmt.Printf("%s: %d\n", d.Name, d.Value.Uint64())
        case metrics.KindFloat64:
            fmt.Printf("%s: %.6f\n", d.Name, d.Value.Float64())
        case metrics.KindFloat64Histogram:
            // pause duration 분포
            hist := d.Value.Float64Histogram()
            fmt.Printf("%s: %d buckets\n", d.Name, len(hist.Buckets))
        }
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| Go CMS (현행) | sub-100μs STW, concurrent, 특별 설정 불필요 | compaction 없음(fragmentation), throughput 오버헤드 ~25% CPU | 대부분의 Go 서비스 (기본값으로 충분) |
| Java ZGC/Shenandoah | concurrent compaction, 대규모 힙(TB) 지원 | JVM 오버헤드, 튜닝 파라미터 복잡, sub-ms pause이지만 load barrier 오버헤드 | 수십 GB+ 힙의 JVM 서비스 |
| Rust (no GC) | zero-cost, deterministic deallocation | 학습 곡선(ownership/borrowing), 개발 속도 저하 | 극한 latency 요구 (trading, embedded) |
| Arena allocation (Go 1.20 실험적) | GC 부하 제거(수명 일치 객체 일괄 해제) | 실험적 API, 잘못 쓰면 메모리 누수 | 요청별 할당이 지배적인 서버 (per-request arena) |

**Step 6 — 성장 & 심화 학습**

1. **소스 코드**: `runtime/mgc.go`, `runtime/mgcmark.go`, `runtime/mbarrier.go` — write barrier의 실제 어셈블리 구현 확인.
2. **공식 설계 문서**: [Getting to Go: The Journey of Go's Garbage Collector](https://go.dev/blog/ismmkeynote) — Rick Hudson의 GopherCon 2018 키노트.
3. **실험**: `GODEBUG=gctrace=1`, `GODEBUG=gcpacertrace=1`로 pacing 알고리즘 관찰.
4. **비교 학습**: Java G1/ZGC의 remembered set + load barrier 접근법과 Go의 write barrier 비교.

**🎯 면접관 평가 기준:**

- **L6 PASS**: tricolor 3색의 의미와 invariant를 정확히 설명. write barrier의 필요성과 기본 동작 설명. GC phase 4단계를 나열하고 STW 구간을 식별. `GODEBUG=gctrace=1` 경험.
- **L7 EXCEED**: hybrid write barrier(Dijkstra + Yuasa)의 결합 이유를 "스택 re-scan 제거"와 연결. GC assist mechanism의 존재와 목적 설명. Go 1.8 이전의 STW 문제 → hybrid barrier 도입 과정의 역사적 맥락. pacing 알고리즘(목표 힙 크기 계산)까지 언급.
- **🚩 RED FLAG**: "Go는 GC 있으니까 메모리 신경 안 써도 된다". tricolor과 reference counting을 혼동. write barrier를 mutex와 동일시.

---

### Q6: GOGC / GOMEMLIMIT 튜닝 & Ballast

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Memory Model & GC

**Question:**
"프로덕션 Go 서비스에서 GC 튜닝 전략을 설명하세요. GOGC의 동작 원리, Go 1.19에서 도입된 GOMEMLIMIT과의 상호작용, 그리고 GOMEMLIMIT 이전에 사용되던 ballast 기법을 비교하세요. 실제로 GOGC=off + GOMEMLIMIT 조합을 쓰는 시나리오와 그 위험을 논하고, 튜닝 시 어떤 메트릭을 기준으로 의사결정하는지 설명하세요."

---

**🧒 12살 비유:**
방이 있는데 장난감을 계속 사들이고 있어. 엄마가 "방 바닥이 반쯤 차면 정리해!"라고 했어 — 이게 GOGC(기본값 100 = 쓰레기가 살아있는 장난감만큼 쌓이면 정리). 근데 방이 작으면 너무 자주 정리해야 하잖아? 그래서 "풍선으로 바닥을 미리 채워놓으면"(ballast) 엄마가 생각하는 "반"이 더 커지니까 정리 빈도가 줄어. 하지만 Go 1.19부터는 엄마에게 "방 크기가 10평이니까 8평까지는 괜찮아"(GOMEMLIMIT)라고 직접 말할 수 있게 됐어. 풍선 트릭(ballast)보다 훨씬 깔끔하지!

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

GC 튜닝은 "이론을 아는 것"과 "프로덕션에서 쓸 수 있는 것"의 차이가 극명한 영역이다. 면접관은:
1. **정량적 사고**: GOGC 값 변경이 힙 크기와 GC 빈도에 미치는 수학적 관계를 이해하는가.
2. **역사적 맥락**: ballast → GOMEMLIMIT 진화의 이유와 각 기법의 한계를 아는가.
3. **운영 판단력**: 어떤 메트릭을 보고 튜닝 결정을 내리는지, OOM 위험을 어떻게 관리하는지.

**Step 2 — 핵심 기술 설명**

**GOGC (GC Percentage):**

GOGC는 "다음 GC 트리거 힙 크기"를 결정하는 비율이다:

```
NextGC = LiveHeap × (1 + GOGC/100)

예시 (GOGC=100, 기본값):
- LiveHeap = 100MB → NextGC = 200MB (100MB 새 할당 후 GC)
- LiveHeap = 100MB, GOGC=200 → NextGC = 300MB (200MB 새 할당 후 GC)
- LiveHeap = 100MB, GOGC=50 → NextGC = 150MB (50MB 새 할당 후 GC)
```

핵심 트레이드오프:
- **GOGC 높이면**: GC 빈도 감소(처리량 향상) → 메모리 사용량 증가
- **GOGC 낮추면**: GC 빈도 증가(latency 스파이크 가능) → 메모리 사용량 감소

```go
import "runtime/debug"

// 프로그래밍 방식으로 GOGC 설정
oldGOGC := debug.SetGCPercent(200)  // GOGC=200으로 변경
defer debug.SetGCPercent(oldGOGC)   // 복원
```

**Ballast 기법 (GOMEMLIMIT 이전):**

Twitch(2019)가 대중화한 기법. 거대한 byte slice를 할당하여 LiveHeap을 인위적으로 부풀린다:

```go
func main() {
    // 1GB ballast: 실제 메모리를 소비하지 않음 (OS의 lazy allocation)
    // Linux에서 mmap은 가상 주소만 예약, 실제 page fault 전까지 RSS 증가 없음
    ballast := make([]byte, 1<<30) // 1GB

    // LiveHeap이 ~1GB로 보이므로:
    // NextGC = 1GB × (1 + 100/100) = 2GB
    // → 실제 live 데이터가 50MB여도 GC가 2GB까지 트리거되지 않음
    // → GC 빈도 대폭 감소

    defer runtime.KeepAlive(ballast)

    startServer()
}
```

Ballast의 문제점:
- **해킹적**: GC 내부 동작에 대한 우회적(indirect) 제어
- **가상 메모리 소비**: RSS는 안 늘어도 virtual memory는 증가. 컨테이너 `memory.memsw.limit_in_bytes`에 걸릴 수 있음.
- **GOGC와 결합 한계**: 실제 live 데이터가 변동하면 예측이 어려움.
- **코드 가독성**: 의도가 불명확 (새 팀원이 "이 1GB 배열 뭐죠?" 질문).

**GOMEMLIMIT (Go 1.19+):**

soft memory limit을 직접 설정. GC pacer가 이 한도를 초과하지 않도록 GC를 더 자주/공격적으로 실행:

```go
// 환경 변수
// GOMEMLIMIT=1500MiB

// 또는 프로그래밍 방식
import "runtime/debug"
debug.SetMemoryLimit(1500 * 1024 * 1024)  // 1.5GiB
```

동작 원리:
```
                    GOGC trigger
                        │
                        ▼
  ┌─────────────────────┬────────────────┐
  │   Live Heap         │  New Alloc     │ ← GOGC=100이면 여기서 GC
  └─────────────────────┴────────────────┘
  │                                       │
  0                                    NextGC

  GOMEMLIMIT이 설정되면:
  ┌─────────────────────┬──────┬─────────┐
  │   Live Heap         │ New  │ Buffer  │
  └─────────────────────┴──────┴─────────┘
  │                                       │
  0                                  GOMEMLIMIT
                                     ↑
                          이 한도 근처에서 GC가
                          더 공격적으로 실행됨
```

**GOGC=off + GOMEMLIMIT 조합:**

```bash
GOGC=off GOMEMLIMIT=1500MiB ./myservice
```

```go
// 이 조합의 동작:
// 1. GOGC=off → NextGC가 "무한대" → 할당만으로는 GC 트리거 안 됨
// 2. GOMEMLIMIT=1500MiB → 힙이 1.5GiB에 근접하면 GC 강제 트리거
// 3. 결과: GC 빈도 최소화, 메모리를 한도까지 최대 활용
```

**위험성 — Death Spiral:**

```
GOGC=off + GOMEMLIMIT에서 live heap ≈ GOMEMLIMIT일 때:

Live Heap: 1400MiB / GOMEMLIMIT: 1500MiB

1. GC 실행 → 100MiB 회수 → Live: 1400MiB
2. 즉시 100MiB 할당 → 다시 1500MiB → GC 즉시 재트리거
3. GC가 끝없이 반복 → CPU 100% GC에 사용
4. mutator 진행 불가 → 서비스 hang
5. 이것이 "GC death spiral" 또는 "GC thrashing"

해결: GOMEMLIMIT은 컨테이너 메모리의 70-80%로 설정
     GOGC는 off 대신 적절한 값(100~400) 유지가 더 안전
```

**Step 3 — 다양한 관점**

| 관점 | GOGC 단독 | Ballast + GOGC | GOMEMLIMIT + GOGC | GOGC=off + GOMEMLIMIT |
|------|-----------|---------------|-------------------|----------------------|
| **제어 직관성** | 비율 기반, live heap 의존 | 해킹적, 의도 불명확 | 절대값 기반, 명확 | 단순하지만 위험 |
| **메모리 예측성** | 낮음 (live heap 변동) | 중간 | 높음 | 높음 (한도까지 사용) |
| **OOM 위험** | GOGC 높으면 위험 | 가상 메모리 이슈 | soft limit이므로 초과 가능 | death spiral 위험 |
| **GC CPU 오버헤드** | GOGC 낮으면 높음 | 낮음 (빈도 감소) | 적응적 | 평시 최소, 위기 시 최대 |
| **코드 유지보수** | 환경 변수 하나 | ballast 코드 필요 | 환경 변수 하나 | 환경 변수 두 개 |

**Step 4 — 구체적 예시: 프로덕션 튜닝 워크플로**

```go
// === 1단계: 현재 상태 진단 ===
// 필수 메트릭 수집

package gctuning

import (
    "fmt"
    "runtime"
    "runtime/debug"
    "runtime/metrics"
    "time"
)

type GCReport struct {
    LiveHeapMB    float64
    GoalHeapMB    float64
    TotalAllocMB  float64
    GCCycles      uint32
    AvgPauseUs    float64
    P99PauseUs    float64
    GCCPUPercent  float64
}

func DiagnoseGC() GCReport {
    var m runtime.MemStats
    runtime.ReadMemStats(&m)

    // GC pause 분포 (runtime/metrics, Go 1.16+)
    samples := []metrics.Sample{
        {Name: "/gc/pauses/total:seconds"},
        {Name: "/gc/cycles/total:gc-cycles"},
        {Name: "/cpu/classes/gc/total:cpu-seconds"},
        {Name: "/cpu/classes/total:cpu-seconds"},
    }
    metrics.Read(samples)

    report := GCReport{
        LiveHeapMB:   float64(m.HeapAlloc) / 1024 / 1024,
        GoalHeapMB:   float64(m.NextGC) / 1024 / 1024,
        TotalAllocMB: float64(m.TotalAlloc) / 1024 / 1024,
        GCCycles:     m.NumGC,
    }

    // 최근 256개 pause 분석
    pauses := make([]time.Duration, 0, 256)
    for i := 0; i < 256 && i < int(m.NumGC); i++ {
        idx := (int(m.NumGC) - 1 - i + 256) % 256
        pauses = append(pauses, time.Duration(m.PauseNs[idx]))
    }
    if len(pauses) > 0 {
        var total time.Duration
        for _, p := range pauses {
            total += p
        }
        report.AvgPauseUs = float64(total.Microseconds()) / float64(len(pauses))
    }

    return report
}

// === 2단계: 튜닝 의사결정 매트릭스 ===
func RecommendTuning(r GCReport, containerMemMB float64) string {
    switch {
    case r.GCCPUPercent > 0.30:
        // GC가 CPU의 30% 이상 소비 → GC 빈도 감소 필요
        return fmt.Sprintf(
            "GOGC=200 GOMEMLIMIT=%.0fMiB (컨테이너의 80%%)",
            containerMemMB*0.8,
        )
    case r.GoalHeapMB > containerMemMB*0.9:
        // 힙이 컨테이너 한도의 90% 이상 → OOM 위험
        return fmt.Sprintf(
            "GOGC=50 GOMEMLIMIT=%.0fMiB (컨테이너의 70%%)",
            containerMemMB*0.7,
        )
    case r.AvgPauseUs > 500:
        // GC pause가 500μs 이상 → 비정상
        return "힙 프로파일링 필요: go tool pprof -alloc_space"
    default:
        return fmt.Sprintf(
            "현재 설정 유지. GOMEMLIMIT=%.0fMiB 권장",
            containerMemMB*0.8,
        )
    }
}

// === 3단계: 프로덕션 적용 예시 ===
// Kubernetes deployment
/*
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: api-server
        resources:
          requests:
            memory: "1Gi"
          limits:
            memory: "2Gi"
        env:
        - name: GOGC
          value: "200"          # 기본 100 → 200으로 GC 빈도 절반
        - name: GOMEMLIMIT
          value: "1600MiB"      # 컨테이너 limit(2Gi)의 80%
        - name: GOMAXPROCS      # automaxprocs로 자동 설정 권장
          value: "4"
*/
```

```go
// === Ballast에서 GOMEMLIMIT으로 마이그레이션 ===

// BEFORE (Go 1.18 이하):
func mainOld() {
    // ⚠️ deprecated pattern
    ballast := make([]byte, 1<<30)  // 1GB ballast
    runtime.KeepAlive(ballast)
    // GOGC=100, effective threshold = ~2GB
}

// AFTER (Go 1.19+):
// 환경 변수만으로 동일 효과:
// GOGC=100 GOMEMLIMIT=2GiB
// ballast 코드 완전 제거

// MIGRATION CHECKLIST:
// 1. Go 1.19+ 업그레이드
// 2. ballast 코드 제거
// 3. GOMEMLIMIT = 컨테이너 memory limit × 0.8
// 4. GOGC는 기존 값 유지 (보통 100)
// 5. 카나리 배포 → GC 메트릭 비교
// 6. /gc/gomemlimit 메트릭으로 limit 도달 빈도 모니터링
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| GOGC=100 (기본) | 설정 없이 동작, 대부분 적절 | live heap 작으면 GC 과다, 클 때 OOM 위험 | 특별한 메모리 제약 없는 서비스 |
| GOGC=200~400 | GC 빈도 절반~1/4, throughput 향상 | 메모리 사용량 2~4배, OOM 가능 | 메모리 여유 + CPU-sensitive 서비스 |
| Ballast (레거시) | 간단한 트릭으로 GC 빈도 감소 | 해킹적, 가상 메모리 소비, Go 1.19+에서 불필요 | Go 1.18 이하에서만 (마이그레이션 대상) |
| GOMEMLIMIT 단독 | 절대값 기반 메모리 관리, OOM 방지 | GOGC=off 시 death spiral 위험 | Go 1.19+ 컨테이너 환경 |
| GOGC=100 + GOMEMLIMIT | 가장 안전한 조합. 이중 방어 | 설정 2개 관리 | **프로덕션 권장 조합** |
| `debug.SetGCPercent(-1)` + 수동 `runtime.GC()` | 완전 수동 제어 | 복잡, 버그 확률 높음, GC 지연 시 OOM | 극히 특수한 배치 처리 |

**Step 6 — 성장 & 심화 학습**

1. **공식 문서**: [A Guide to the Go Garbage Collector](https://tip.golang.org/doc/gc-guide) — GOGC, GOMEMLIMIT 상호작용의 공식 가이드.
2. **설계 제안**: [proposal: runtime: soft memory limit](https://github.com/golang/go/issues/48409) — Michael Knyszek의 GOMEMLIMIT 설계 문서. death spiral 방지를 위한 `gc-cpu-limiter`(GC CPU 사용률 50% 상한) 포함.
3. **프로파일링 실습**: `go tool pprof -alloc_space`, `go tool pprof -inuse_space`로 할당 핫스팟 식별. 할당 자체를 줄이는 것이 GC 튜닝보다 근본적.
4. **Uber의 사례 연구**: [How We Saved 70K Cores Across 30 Go Services with GOGC Tuning](https://www.uber.com/blog/how-we-saved-70k-cores-across-30-critical-go-services-with-gogc-tuning/) — GOGC 자동 튜닝 프레임워크.
5. **심화**: `runtime/mgcpacer.go` 소스 코드 — pacer가 목표 힙 크기를 계산하는 PID controller 로직.

**🎯 면접관 평가 기준:**

- **L6 PASS**: GOGC의 공식(`NextGC = Live × (1 + GOGC/100)`)을 정확히 서술. GOMEMLIMIT의 존재와 기본 동작 설명. ballast 기법을 알고 왜 GOMEMLIMIT이 대체하는지 설명. 컨테이너 환경에서 GOMEMLIMIT을 memory limit의 70-80%로 설정하는 실무 가이드라인 제시.
- **L7 EXCEED**: GOGC=off + GOMEMLIMIT의 death spiral 메커니즘을 단계별로 설명하고 `gc-cpu-limiter`(50% CPU 상한)의 존재를 언급. GC pacer의 feedback loop(PID controller 유사 구조) 설명. Uber의 GOGC 자동 튜닝 사례처럼 메트릭 기반 자동화 전략 제시. `runtime/metrics`를 활용한 프로덕션 모니터링 파이프라인 설계.
- **🚩 RED FLAG**: GOGC를 "GC 비활성화"로 오해. GOMEMLIMIT을 hard limit으로 착각(soft limit임). ballast를 "메모리 예약"으로 설명(실제 RSS 증가 없음을 모름). 튜닝 시 메트릭 없이 "GOGC=400으로 올리면 됩니다" 식의 답변.

---

## 3. Channel Patterns


> 대상: FAANG L6/L7 (Staff/Principal Engineer)
> 총 문항: 3개 (Q7~Q9) | 난이도: ⭐⭐⭐⭐⭐
> 언어: Go 1.22+
> Category 3: Channel Patterns

핵심 토픽: Fan-in/fan-out, pipeline, context cancellation 전파, select 랜덤 공정성, nil channel

---

### Q7: Fan-in/Fan-out Pipeline with Graceful Shutdown

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Channel Patterns

**Question:**
프로덕션에서 수백만 건의 이벤트를 실시간 처리하는 파이프라인을 설계해야 한다. Fan-out으로 N개의 worker에게 분배하고, Fan-in으로 결과를 합치는 구조를 구현하라. 이 파이프라인이 `context.Context` 취소 시 **모든 goroutine이 누수 없이 종료**되도록 보장하는 방법을 설명하고, 중간 stage에서 에러가 발생했을 때의 전파 전략을 설계하라. `errgroup`과 직접 구현의 트레이드오프도 논의하라.

---

**🧒 12살 비유:**
피자 가게를 상상해 보자. 주문이 들어오면(Fan-out) 여러 요리사에게 나눠 보낸다 — 한 명은 도우를 만들고, 한 명은 토핑을 준비하고, 한 명은 오븐을 관리한다. 다 만들어지면 포장 담당자가 하나로 합친다(Fan-in). 가게가 문을 닫을 때(context cancel) 모든 요리사가 하던 일을 깔끔하게 마무리하고, 재료가 바닥에 나뒹굴지 않게 정리하고 퇴근해야 한다. 한 요리사가 실수로 피자를 태웠을 때(에러), 그 피자만 버리고 계속할지 아니면 전체 라인을 멈출지 결정해야 한다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

면접관은 이 질문으로 세 가지를 평가한다:
1. **Channel 기본기**: unbuffered vs buffered channel의 의미론적 차이, 방향성 채널 타입(`<-chan`, `chan<-`)을 정확히 이해하는가
2. **Goroutine lifecycle 관리**: goroutine leak 없이 모든 concurrent path를 종료시킬 수 있는가. 이것은 Go 프로그래밍에서 가장 흔한 프로덕션 버그 중 하나다
3. **에러 전파 설계**: 분산 파이프라인에서 partial failure를 어떻게 다루는지, `errgroup`의 내부 동작을 이해하는가

Staff 엔지니어라면 단순히 "fan-out 하고 fan-in 한다"가 아니라, **backpressure**, **ordered vs unordered fan-in**, **graceful vs immediate shutdown** 같은 프로덕션 고려사항을 자연스럽게 논의해야 한다.

**Step 2 — 핵심 기술 설명**

Go의 pipeline 패턴은 각 stage가 inbound channel에서 읽고 outbound channel로 쓰는 함수로 구성된다. 핵심 원칙은 **"channel을 닫는 것은 보내는 쪽의 책임"**이다.

Fan-out은 하나의 channel을 여러 goroutine이 읽게 하는 것이고, Fan-in은 여러 channel의 출력을 하나의 channel로 합치는 것이다.

```go
// generator: 데이터를 파이프라인에 주입하는 첫 번째 stage
func generator(ctx context.Context, items []Event) <-chan Event {
    out := make(chan Event)
    go func() {
        defer close(out) // 보내는 쪽이 닫는다
        for _, item := range items {
            select {
            case out <- item:
            case <-ctx.Done():
                return // context 취소 시 즉시 종료
            }
        }
    }()
    return out
}

// fanOut: N개의 worker가 동일한 input channel에서 경쟁적으로 읽음
func fanOut(ctx context.Context, in <-chan Event, workers int,
    process func(Event) (Result, error)) []<-chan Result {

    channels := make([]<-chan Result, workers)
    for i := 0; i < workers; i++ {
        channels[i] = worker(ctx, in, process)
    }
    return channels
}

func worker(ctx context.Context, in <-chan Event,
    process func(Event) (Result, error)) <-chan Result {

    out := make(chan Result)
    go func() {
        defer close(out)
        for event := range in { // in이 닫히면 자연스럽게 종료
            select {
            case <-ctx.Done():
                return
            default:
            }
            result, err := process(event)
            if err != nil {
                result = Result{Err: err, OriginalEvent: event}
            }
            select {
            case out <- result:
            case <-ctx.Done():
                return
            }
        }
    }()
    return out
}

// fanIn: 여러 channel을 하나로 합침
func fanIn(ctx context.Context, channels []<-chan Result) <-chan Result {
    merged := make(chan Result)
    var wg sync.WaitGroup

    wg.Add(len(channels))
    for _, ch := range channels {
        go func(c <-chan Result) {
            defer wg.Done()
            for result := range c {
                select {
                case merged <- result:
                case <-ctx.Done():
                    // 나머지 값을 drain하지 않으면 보내는 goroutine이 블록될 수 있음
                    return
                }
            }
        }(ch)
    }

    // 모든 input channel이 닫히면 merged도 닫는다
    go func() {
        wg.Wait()
        close(merged)
    }()
    return merged
}
```

**Graceful Shutdown의 핵심 포인트:**
1. `context.WithCancel`로 전체 파이프라인에 취소 신호를 전파한다
2. 모든 `send` 연산을 `select`로 감싸서 `ctx.Done()`을 체크한다 — 이것을 빠뜨리면 goroutine이 blocked send에서 영원히 걸린다
3. `close(out)`을 `defer`로 보장하여 downstream stage가 `range` 루프에서 빠져나올 수 있게 한다
4. 취소 시 upstream channel을 drain하지 않으면 upstream goroutine이 leak된다 — 이것이 가장 흔한 실수다

**Step 3 — 다양한 관점**

**성능 관점**: Buffered channel을 사용하면 stage 간 속도 차이를 흡수할 수 있다. 버퍼 크기는 프로파일링으로 결정해야 하며, 너무 크면 메모리를 낭비하고, 너무 작으면 goroutine이 자주 block된다. 경험적으로 worker 수의 2~4배가 시작점이다.

**정확성 관점**: Fan-in은 기본적으로 **unordered**다. 순서가 필요하면 각 Result에 sequence number를 넣고 downstream에서 reorder 버퍼를 사용해야 한다. 이것은 복잡성을 크게 증가시키므로 정말 필요한지 먼저 검증하라.

**스케일 관점**: Worker 수를 `runtime.NumCPU()`에 맞추는 것은 CPU-bound 작업에만 유효하다. I/O-bound 작업이면 CPU 수의 10~100배도 가능하다. 동적으로 worker를 조절하려면 semaphore 패턴(`make(chan struct{}, maxConcurrency)`)을 고려하라.

**Step 4 — 구체적 예시: errgroup 활용**

```go
import "golang.org/x/sync/errgroup"

func ProcessEvents(ctx context.Context, events []Event) ([]Result, error) {
    // errgroup은 내부적으로 context.WithCancel을 호출한다
    // 하나의 goroutine이 non-nil error를 반환하면 cancel이 호출된다
    g, ctx := errgroup.WithContext(ctx)

    // Stage 1: Generator
    eventCh := make(chan Event, 100)
    g.Go(func() error {
        defer close(eventCh)
        for _, e := range events {
            select {
            case eventCh <- e:
            case <-ctx.Done():
                return ctx.Err()
            }
        }
        return nil
    })

    // Stage 2: Fan-out workers (errgroup이 goroutine 수를 제한)
    g.SetLimit(runtime.NumCPU()) // Go 1.22+: errgroup concurrency limit

    resultCh := make(chan Result, 100)
    var resultWg sync.WaitGroup

    for i := 0; i < runtime.NumCPU(); i++ {
        resultWg.Add(1)
        g.Go(func() error {
            defer resultWg.Done()
            for event := range eventCh {
                result, err := processEvent(event)
                if err != nil {
                    return fmt.Errorf("processing event %s: %w", event.ID, err)
                    // 이 error가 반환되면 errgroup이 ctx를 cancel한다
                    // → 다른 모든 goroutine에 종료 신호가 전파된다
                }
                select {
                case resultCh <- result:
                case <-ctx.Done():
                    return ctx.Err()
                }
            }
            return nil
        })
    }

    // resultCh를 닫는 goroutine
    go func() {
        resultWg.Wait()
        close(resultCh)
    }()

    // Stage 3: Fan-in (collector)
    var results []Result
    g.Go(func() error {
        for r := range resultCh {
            results = append(results, r)
        }
        return nil
    })

    if err := g.Wait(); err != nil {
        return results, err // partial results + error
    }
    return results, nil
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| **수동 `WaitGroup` + channel** | 완전한 제어, 커스텀 에러 전략 가능 | 코드 복잡, leak 버그 위험 높음 | 복잡한 에러 복구가 필요할 때 |
| **`errgroup`** | 깔끔한 API, context 취소 자동화, `SetLimit` 지원 | first-error-wins만 지원, partial failure 어려움 | 대부분의 프로덕션 파이프라인 |
| **`errgroup` + Result type (에러 포함)** | 부분 실패 허용하면서 구조화 | Result 타입 관리 필요 | 일부 실패를 허용해야 할 때 |
| **외부 라이브러리 (sourcegraph/conc)** | 제네릭 타입 안전성, panic recovery 내장 | 외부 의존성 | 팀이 이미 사용 중일 때 |

**Step 6 — 성장 & 심화 학습**

1. Go 공식 블로그 "Go Concurrency Patterns: Pipelines and cancellation" 정독
2. `errgroup` 소스 코드 읽기 — 100줄도 안 되지만 goroutine lifecycle 관리의 정수가 담겨 있다
3. Bryan Mills의 GopherCon 2018 "Rethinking Classical Concurrency Patterns" 발표
4. 실습: 기존 sequential 코드를 pipeline으로 변환하면서 `-race` 플래그로 지속 검증

**🎯 면접관 평가 기준:**

- **L6 PASS**: channel 방향성, close 책임, `select`로 ctx 체크를 정확히 구현. Fan-in에서 `WaitGroup`으로 close 타이밍을 제어. Goroutine leak 시나리오를 1가지 이상 설명.
- **L7 EXCEED**: Backpressure 전략, ordered fan-in의 복잡성, `errgroup` vs 수동 구현의 구체적 트레이드오프 논의. Dynamic worker pool 설계. 실제 프로덕션 사례 기반 설명.
- **🚩 RED FLAG**: Channel을 닫지 않거나 잘못된 쪽에서 닫음. `select` 없이 send/receive 수행. "goroutine은 가비지 컬렉트된다"라고 말함 (되지 않는다).

---

### Q8: Select의 랜덤 공정성과 Nil Channel을 활용한 동적 멀티플렉싱

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Channel Patterns

**Question:**
Go의 `select` 문에서 여러 case가 동시에 ready일 때 어떤 case가 선택되는가? 이 동작의 런타임 구현 원리를 설명하라. 또한, `nil` channel에 대한 send/receive가 `select` 안에서 어떻게 동작하는지 설명하고, 이 특성을 활용해서 **런타임에 동적으로 channel을 활성화/비활성화**하는 패턴을 프로덕션 코드로 보여라.

---

**🧒 12살 비유:**
우체통이 3개 있다고 상상해 보자. 너는 편지가 오면 꺼내야 한다. 그런데 3개 우체통에 동시에 편지가 도착하면? Go의 `select`는 동전을 던져서(랜덤으로) 어떤 우체통을 먼저 열지 결정한다. 한 우체통을 항상 먼저 열지 않는다 — 공정하게 랜덤이다. 그런데 하나의 우체통에 자물쇠를 걸어버리면(`nil` channel) 아예 그 우체통은 존재하지 않는 것처럼 무시한다. 이걸 이용해서 "지금은 이 우체통 안 볼래" 하고 껐다 켤 수 있다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

이 질문은 Go 런타임의 내부 동작에 대한 깊은 이해를 평가한다:
1. **`select`의 공정성 보장 메커니즘**: 왜 랜덤인지, 어떻게 구현되었는지 아는가
2. **`nil` channel의 의미론**: 대부분의 개발자가 "nil channel은 영원히 블록"이라는 것은 알지만, `select` 안에서의 동작과 이를 활용한 패턴까지 아는가
3. **실무 적용력**: 이 두 가지 특성을 조합하여 실제 문제를 해결하는 패턴을 설계할 수 있는가

Staff 레벨에서는 이것이 단순한 언어 퀴즈가 아니라, rate limiting, circuit breaking, feature toggle 같은 실제 시스템 설계에 어떻게 연결되는지를 보여줘야 한다.

**Step 2 — 핵심 기술 설명**

**Select의 랜덤 선택 원리:**

Go 런타임의 `selectgo()` 함수(`runtime/select.go`)에서 구현된다. 핵심 단계는:

1. **Polling order 결정**: `cheaprandn()` (Fisher-Yates 변형)으로 case들의 순회 순서를 셔플한다. 이것이 공정성을 보장한다.
2. **Lock order 결정**: 관련된 모든 channel을 주소 순으로 정렬하여 lock한다 — deadlock 방지를 위해.
3. **Polling phase**: 셔플된 순서로 각 case를 확인하여 즉시 실행 가능한 첫 번째 case를 선택한다.
4. **없으면 대기**: 모든 channel의 wait queue에 현재 goroutine(sudog)을 등록하고 `gopark()`로 블록한다.

```go
// 런타임 의사 코드 (runtime/select.go 기반)
func selectgo(cas0 *scase, order0 *uint16, ...) (int, bool) {
    // 1. 셔플: 공정성 보장
    norder := 0
    for i := range scases {
        j := cheaprandn(uint32(norder + 1))
        pollorder[norder] = pollorder[j]
        pollorder[j] = uint16(i)
        norder++
    }

    // 2. 채널 주소순 정렬: 데드락 방지용 lock 순서
    // 3. 모든 관련 channel lock
    // 4. 셔플된 순서로 ready case 탐색
    for _, casei := range pollorder {
        // channel의 send/recv queue 확인
        if ready {
            return casei, recvOK
        }
    }
    // 5. 없으면 모든 channel의 waitqueue에 등록 후 park
}
```

이 구현에서 중요한 점: `select`는 **uniform random**이 아니라 **pseudo-random permutation**이다. 실질적으로 동일한 공정성을 제공하지만 구현이 더 효율적이다.

**Nil channel의 동작:**

```go
var ch chan int = nil

// select 밖: 영원히 블록
<-ch     // goroutine이 영원히 블록 (deadlock 아니면)
ch <- 1  // goroutine이 영원히 블록

// select 안: 해당 case가 무시됨 (never ready)
select {
case v := <-ch:  // ch가 nil이면 이 case는 선택되지 않음
    fmt.Println(v)
case <-time.After(1 * time.Second):
    fmt.Println("timeout") // 이것만 실행됨
}
```

이것이 강력한 이유: **변수에 `nil`을 대입하는 것만으로 채널을 비활성화**할 수 있다.

**Step 3 — 다양한 관점**

**성능 관점**: `select`의 비용은 case 수에 비례한다(O(n) 셔플 + O(n) lock). Case가 많아지면(10개 이상) reflect.Select를 쓰거나 구조를 재설계해야 한다. Nil channel case는 polling에서 즉시 스킵되므로 추가 비용이 거의 없다.

**정확성 관점**: 랜덤 공정성은 통계적이다 — 짧은 시간 동안 특정 case에 편향될 수 있다. Priority가 필요하면 `select`를 중첩하거나 별도 로직을 구현해야 한다:

```go
// 우선순위 select 패턴
select {
case msg := <-highPriority: // 먼저 high priority만 체크
    handle(msg)
default:
    select {
    case msg := <-highPriority:
        handle(msg)
    case msg := <-lowPriority:
        handle(msg)
    }
}
```

**스케일 관점**: 수백 개의 channel을 멀티플렉싱해야 하면 `select`보다 단일 channel + message routing 패턴이 적합하다. 또는 `reflect.Select`를 사용하되, 이것은 일반 `select`보다 10배 이상 느리다.

**Step 4 — 구체적 예시: Nil Channel로 동적 멀티플렉싱**

```go
// DynamicMerger: 여러 소스를 동적으로 활성화/비활성화하면서 합침
// 실제 사용 사례: 여러 데이터 피드를 circuit breaker 상태에 따라 on/off
type DynamicMerger struct {
    sources map[string]<-chan Event
    active  map[string]<-chan Event // nil이면 비활성화
    control chan mergeCommand
    output  chan Event
}

type mergeCommand struct {
    action string // "enable", "disable", "add", "remove"
    name   string
    ch     <-chan Event
}

func (m *DynamicMerger) Run(ctx context.Context) <-chan Event {
    m.output = make(chan Event, 100)
    go func() {
        defer close(m.output)
        for {
            // 동적으로 select할 수 없으므로 reflect.Select 사용
            // 또는 goroutine-per-source 패턴 사용
            select {
            case <-ctx.Done():
                return
            case cmd := <-m.control:
                m.handleCommand(cmd)
            default:
                m.drainActive(ctx)
            }
        }
    }()
    return m.output
}

// 더 실용적인 패턴: 고정된 수의 소스를 nil로 토글
func mergeWithToggle(ctx context.Context,
    primary, secondary, tertiary <-chan Event,
) <-chan Event {
    out := make(chan Event)

    go func() {
        defer close(out)
        // 초기 상태: 모든 소스 활성화
        p, s, t := primary, secondary, tertiary

        for p != nil || s != nil || t != nil {
            select {
            case <-ctx.Done():
                return

            case v, ok := <-p:
                if !ok {
                    p = nil // 채널이 닫혔으면 nil로 비활성화
                    continue // → 다음 루프에서 이 case는 무시됨
                }
                select {
                case out <- v:
                case <-ctx.Done():
                    return
                }

            case v, ok := <-s:
                if !ok {
                    s = nil
                    continue
                }
                select {
                case out <- v:
                case <-ctx.Done():
                    return
                }

            case v, ok := <-t:
                if !ok {
                    t = nil
                    continue
                }
                select {
                case out <- v:
                case <-ctx.Done():
                    return
                }
            }
        }
    }()
    return out
}
```

이 패턴의 핵심: 채널이 닫히면 변수를 `nil`로 설정하여 `select`에서 제외한다. 모든 소스가 `nil`이 되면 루프가 종료된다. 이것은 `for range`로는 불가능한 **여러 채널의 graceful drain** 문제를 우아하게 해결한다.

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| **정적 `select` + nil toggle** | 컴파일 타임 안전, 최고 성능 | case 수가 컴파일 타임에 고정 | 소스 수가 고정일 때 (2~5개) |
| **`reflect.Select`** | 런타임 동적 case 수 | 10x 느림, 타입 안전성 없음 | 소스 수가 런타임에 결정될 때 |
| **goroutine-per-source + fan-in** | 소스별 독립 관리, 동적 추가/제거 | goroutine 수 증가, 합류 지점 필요 | 소스가 자주 추가/제거될 때 |
| **중첩 select (priority)** | 우선순위 구현 가능 | 코드 복잡, starvation 위험 | 명확한 우선순위가 있을 때 |

**Step 6 — 성장 & 심화 학습**

1. Go 런타임 소스 `runtime/select.go`의 `selectgo()` 함수 직접 읽기
2. Kavya Joshi의 GopherCon 2017 "Understanding Channels" 발표 — channel의 hchan 구조체와 lock-free 최적화
3. 실습: race detector(`go test -race`)로 nil channel 토글 패턴이 data race 없는지 검증
4. `runtime.GOMAXPROCS`와 `select` 공정성의 관계를 벤치마크로 확인

**🎯 면접관 평가 기준:**

- **L6 PASS**: Select의 랜덤 선택을 정확히 설명. Nil channel이 select에서 무시됨을 알고, 닫힌 채널을 nil로 설정하는 패턴을 구현. `ok` idiom으로 채널 닫힘을 감지.
- **L7 EXCEED**: 런타임의 `selectgo()` 구현을 lock ordering과 pollorder shuffling 수준에서 설명. Nil channel 토글 패턴의 메모리 모델 안전성 논의. Priority select의 starvation 문제와 해결책 제시.
- **🚩 RED FLAG**: "select는 위에서부터 순서대로 확인한다"고 말함. Nil channel에 send/receive하면 panic이 난다고 말함(panic이 아니라 영구 블록). 닫힌 채널에서 receive하면 블록된다고 말함(zero value가 즉시 반환됨).

---

### Q9: Context Cancellation 전파와 Goroutine Tree의 Lifecycle 관리

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Channel Patterns

**Question:**
대규모 API 서버에서 하나의 HTTP 요청이 수십 개의 goroutine을 생성하는 시나리오를 생각하라. `context.Context`가 취소될 때 이 goroutine tree 전체가 어떻게 종료되는가? `context.WithCancel`, `WithTimeout`, `WithDeadline`의 내부 구현 차이를 설명하고, **context cancellation이 channel을 통해 전파되는 메커니즘**을 런타임 수준에서 설명하라. 또한, context를 잘못 사용하여 goroutine leak이 발생하는 3가지 패턴과 각각의 해결책을 제시하라.

---

**🧒 12살 비유:**
학교에서 체육대회를 한다고 생각해 보자. 교장 선생님(root context)이 "체육대회 시작!"이라고 하면, 학년 부장(child context)이 각 반에 전달하고, 각 반 담임(grandchild context)이 학생들(goroutine)에게 전달한다. 비가 오면(cancel) 교장 선생님이 "중단!"이라고 하면, 그 신호가 학년 부장 → 반 담임 → 학생 순서로 전달되어 모두가 교실로 돌아간다. 중요한 점은: 3학년 부장이 "3학년만 중단!"이라고 해도, 1학년 2학년은 계속한다 — 취소는 아래로만 전파되고 위로는 전파되지 않는다.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

이 질문은 Staff 엔지니어의 시스템 사고(systems thinking)를 평가한다:
1. **Context 내부 구현 이해**: `Done()` channel이 어떻게 생성되고 전파되는지, lazy initialization이 왜 중요한지
2. **Goroutine tree 관리**: 실제 서비스에서 request당 수십~수백 개의 goroutine이 생성될 때, 이들의 lifecycle을 어떻게 보장하는지
3. **디버깅 능력**: Goroutine leak은 Go 서비스의 가장 흔한 메모리 이슈 중 하나다. 패턴을 인식하고 예방하는 능력이 있는지

프로덕션 Go 서버의 90% 이상의 메모리 leak은 goroutine leak에서 온다. 이것을 체계적으로 이해하고 예방할 수 있는지가 Staff 레벨의 핵심 역량이다.

**Step 2 — 핵심 기술 설명**

**Context의 내부 구조:**

```go
// context 패키지의 핵심 구조 (Go 1.22+ 기준)
type cancelCtx struct {
    Context                        // 부모 context 임베딩
    mu       sync.Mutex
    done     atomic.Value          // chan struct{}, lazily created
    children map[canceler]struct{} // 자식 context들의 set
    err      error                 // 취소 이유
    cause    error                 // Go 1.20+ WithCancelCause
}
```

**Cancellation 전파 메커니즘 (channel 기반):**

1. `WithCancel(parent)`이 호출되면 새로운 `cancelCtx`가 생성된다
2. `propagateCancel(parent, child)`가 호출되어 부모의 `children` map에 자식을 등록한다
3. 부모가 취소되면 `cancel()` 함수가 호출된다:

```go
// context.go의 cancel() 단순화
func (c *cancelCtx) cancel(removeFromParent bool, err, cause error) {
    c.mu.Lock()

    // 1. Done channel을 닫아서 <-ctx.Done()을 기다리는
    //    모든 goroutine에게 신호를 보낸다
    d, _ := c.done.Load().(chan struct{})
    if d == nil {
        c.done.Store(closedchan) // 이미 닫힌 전역 채널 재사용
    } else {
        close(d)                 // 이것이 실제 신호 전파!
    }

    // 2. 모든 자식을 재귀적으로 취소한다
    for child := range c.children {
        child.cancel(false, err, cause)
    }
    c.children = nil
    c.mu.Unlock()

    // 3. 부모의 children map에서 자신을 제거
    if removeFromParent {
        removeChild(c.Context, c)
    }
}
```

핵심 인사이트: **`Done()` channel의 close가 broadcast 메커니즘**이다. Channel을 close하면 그 channel에서 receive하는 모든 goroutine이 즉시 깨어난다. 이것이 1:N 취소 전파를 가능하게 한다.

**`Done()` channel의 lazy initialization:**

```go
func (c *cancelCtx) Done() <-chan struct{} {
    d := c.done.Load()
    if d != nil {
        return d.(chan struct{})
    }
    c.mu.Lock()
    defer c.mu.Unlock()
    d = c.done.Load()
    if d == nil {
        d = make(chan struct{}) // 최초 호출 시에만 생성
        c.done.Store(d)
    }
    return d.(chan struct{})
}
```

이 lazy initialization은 중요하다 — `Done()`을 호출하지 않는 context는 channel을 할당하지 않아서 메모리를 절약한다. `context.Background()`는 절대 취소되지 않으므로 `Done()`이 nil을 반환하고, nil channel은 receive 시 영원히 블록되므로 select에서 자연스럽게 무시된다.

**WithTimeout vs WithDeadline:**

```go
// WithTimeout은 WithDeadline의 편의 래퍼다
func WithTimeout(parent Context, timeout time.Duration) (Context, CancelFunc) {
    return WithDeadline(parent, time.Now().Add(timeout))
}

// WithDeadline은 timerCtx를 생성한다
type timerCtx struct {
    cancelCtx            // cancelCtx 임베딩
    timer    *time.Timer // 데드라인에 cancel을 호출하는 타이머
    deadline time.Time
}
```

`timerCtx`는 내부적으로 `time.AfterFunc(dur, cancel)`을 사용하여 데드라인에 자동으로 cancel을 트리거한다. 부모의 deadline이 자식의 deadline보다 이르면 타이머를 설정하지 않는다 — 부모가 먼저 취소될 것이기 때문이다.

**Step 3 — 다양한 관점**

**성능 관점**: Context tree가 깊어지면 취소 전파에 O(n) 시간이 걸린다(n = 자식 수). 각 레벨에서 mutex lock이 필요하므로 contention이 발생할 수 있다. Go 1.21+에서 `afterFuncer` 인터페이스를 도입하여 `propagateCancel`의 성능을 개선했다.

**정확성 관점**: `context.Value()`는 tree를 거슬러 올라가며 key를 찾는다 — O(depth) 비용. Value를 과도하게 사용하면 성능 문제가 발생한다. Context에는 request-scoped 값만 넣어야 한다(trace ID, auth token 등). 비즈니스 로직 파라미터는 함수 인자로 전달하라.

**운영 관점**: `runtime/pprof`의 goroutine 프로파일과 `runtime.NumGoroutine()`을 모니터링하여 goroutine leak을 조기에 감지해야 한다. 프로메테우스 메트릭으로 goroutine 수를 추적하고, 비정상 증가 시 알림을 설정한다.

**Step 4 — 구체적 예시: 3가지 Goroutine Leak 패턴과 해결책**

```go
// ❌ Leak 패턴 1: context를 전달하지 않는 goroutine
func handleRequest(ctx context.Context, userID string) {
    // 이 goroutine은 ctx를 받지 않으므로 요청이 취소되어도 계속 실행된다
    go func() {
        result := expensiveComputation() // 10분 걸릴 수 있음
        saveResult(result)               // 이미 클라이언트는 떠났는데...
    }()
}

// ✅ 해결: context를 전달하고 주기적으로 확인
func handleRequest(ctx context.Context, userID string) {
    go func() {
        select {
        case <-ctx.Done():
            return // 요청 취소 시 즉시 종료
        case result := <-computeAsync(ctx):
            saveResult(result)
        }
    }()
}

// ❌ Leak 패턴 2: 아무도 읽지 않는 channel에 send
func fetchAll(ctx context.Context) []Result {
    ch := make(chan Result)

    for _, url := range urls {
        go func(u string) {
            result := fetch(u)
            ch <- result // 만약 fetchAll이 일찍 반환하면,
                         // 이 goroutine은 영원히 블록된다!
        }(url)
    }

    // timeout이나 에러로 일부만 수집하고 반환하면
    // 나머지 goroutine들은 ch <- 에서 영원히 대기
    var results []Result
    for i := 0; i < 3; i++ { // 3개만 수집하고 반환
        results = append(results, <-ch)
    }
    return results
}

// ✅ 해결: buffered channel 또는 select + ctx 사용
func fetchAll(ctx context.Context) []Result {
    ch := make(chan Result, len(urls)) // buffered: 보내고 종료 가능

    ctx, cancel := context.WithCancel(ctx)
    defer cancel() // 함수 반환 시 모든 하위 goroutine에 취소 신호

    for _, url := range urls {
        go func(u string) {
            result := fetch(u)
            select {
            case ch <- result:
            case <-ctx.Done(): // cancel 시 goroutine이 빠져나올 수 있음
            }
        }(url)
    }

    var results []Result
    for i := 0; i < 3; i++ {
        select {
        case r := <-ch:
            results = append(results, r)
        case <-ctx.Done():
            return results
        }
    }
    return results
}

// ❌ Leak 패턴 3: 취소 함수를 호출하지 않음 (timer leak)
func processWithTimeout(ctx context.Context) {
    ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
    // cancel을 호출하지 않으면:
    // 1. timerCtx의 내부 timer가 30초 동안 유지됨
    // 2. 부모 context의 children map에 계속 남아있음
    // 3. 요청이 이미 끝났는데도 리소스를 점유

    result := doWork(ctx)
    handleResult(result)
    // cancel() 빠뜨림!
}

// ✅ 해결: defer cancel() 필수
func processWithTimeout(ctx context.Context) {
    ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
    defer cancel() // 항상 defer로 호출. 이미 취소되었어도 안전하다.
    // cancel()은 idempotent — 여러 번 호출해도 안전

    result := doWork(ctx)
    handleResult(result)
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| **`context.WithCancel` + defer** | 가장 기본적이고 안전 | 수동으로 cancel 호출 필요 | 명시적 취소 제어가 필요할 때 |
| **`context.WithTimeout`** | 자동 타임아웃, deadline propagation | 타이머 리소스 사용, defer cancel 필수 | 외부 서비스 호출, SLA 보장 |
| **`context.AfterFunc` (Go 1.21+)** | 취소 시 콜백 실행, 클린업 로직 분리 | 콜백이 별도 goroutine에서 실행 | 취소 시 리소스 해제가 필요할 때 |
| **`context.WithoutCancel` (Go 1.21+)** | 부모 취소가 자식에게 전파되지 않음 | 의도치 않은 goroutine leak 위험 | 백그라운드 작업이 요청 수명을 넘길 때 |
| **`errgroup.WithContext`** | 자동 cancel + 에러 수집 | first-error-wins만 지원 | 여러 goroutine의 lifecycle 관리 |

**Step 6 — 성장 & 심화 학습**

1. Go 표준 라이브러리 `context/context.go` 소스 코드 정독 — 500줄로 goroutine lifecycle 관리의 핵심을 배울 수 있다
2. Go 1.21 릴리즈 노트의 `context.WithoutCancel`, `context.WithDeadlineCause`, `context.AfterFunc` 학습
3. Sameer Ajmani의 "Go Concurrency Patterns: Context" 블로그 포스트 (Go 공식 블로그)
4. 실습: `goleak` 라이브러리(`go.uber.org/goleak`)를 테스트에 적용하여 goroutine leak 자동 감지
5. 프로덕션에서 `/debug/pprof/goroutine?debug=2`로 goroutine 스택 덤프 분석 연습

**🎯 면접관 평가 기준:**

- **L6 PASS**: Context cancellation이 channel close를 통해 전파됨을 설명. `defer cancel()` 필수성을 이해. Goroutine leak 패턴 2가지 이상 식별하고 해결. WithTimeout과 WithDeadline의 관계를 설명.
- **L7 EXCEED**: `cancelCtx`의 `children` map과 `propagateCancel` 메커니즘을 설명. `Done()` channel의 lazy initialization 이유를 메모리 최적화 관점에서 논의. Go 1.21+의 `AfterFunc`, `WithoutCancel` 같은 최신 API와 그 설계 동기를 설명. 실제 프로덕션 goroutine leak 디버깅 경험 공유.
- **🚩 RED FLAG**: "context는 그냥 값을 전달하는 용도"라고만 말함. `cancel()` 호출을 빠뜨려도 GC가 정리해준다고 말함(해주지 않는다). Context를 struct에 저장하는 패턴을 제안함(Go 공식 가이드라인 위반).

---

## 4. Interface Design

## 4. Interface Design

### Q10: Interface Segregation과 Implicit Satisfaction — Go의 "작은 인터페이스" 철학

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Interface Design

**Question:**
Go는 인터페이스를 implicit하게 만족시키는 유일한 주류 언어 중 하나다. 이 설계 결정이 대규모 코드베이스에서 interface segregation에 어떤 영향을 미치는가? "Accept interfaces, return structs" 원칙의 기술적 근거를 설명하고, 실제 프로덕션에서 인터페이스가 너무 크거나 너무 작을 때 발생하는 문제를 사례와 함께 논의하라.

---

**🧒 12살 비유:**
레고 블록을 생각해봐. Java나 C#은 "이 블록은 4x2 블록입니다"라는 라벨을 붙여야 4x2 자리에 끼울 수 있어. 그런데 Go는 라벨 없이도, 실제로 4x2 크기면 그냥 끼울 수 있어. 이렇게 하면 나중에 새 종류의 블록을 만들 때 기존 라벨 시스템을 바꿀 필요가 없어서 훨씬 유연해. 근데 블록 자리(인터페이스)를 "4x2x1 높이에 빨간색에 특수 홈이 있는 것"처럼 너무 구체적으로 만들면, 끼울 수 있는 블록이 거의 없어져. 반대로 "아무 블록"이라고 하면 엉뚱한 블록이 들어올 수 있고.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

이 질문은 Go의 타입 시스템 설계 철학에 대한 깊은 이해를 검증한다. 면접관은 (1) implicit interface satisfaction이 structural subtyping의 한 형태임을 아는지, (2) ISP(Interface Segregation Principle)를 Go 맥락에서 적용할 수 있는지, (3) 대규모 시스템에서 인터페이스 경계를 올바르게 설계할 수 있는지를 평가한다. L6/L7 엔지니어는 인터페이스 설계가 패키지 의존성 그래프, 테스트 용이성, 컴파일 시간에 미치는 파급 효과까지 논의할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

Go의 인터페이스는 **structural typing**(구조적 타이핑)에 기반한다. 타입이 인터페이스의 모든 메서드를 구현하면 별도의 `implements` 선언 없이 자동으로 해당 인터페이스를 만족시킨다. 이는 Rob Pike와 Ken Thompson이 C++/Java에서 경험한 "의존성 지옥"을 해결하기 위한 의도적 설계다.

핵심 원칙은 **소비자 측에서 인터페이스를 정의**하는 것이다. 표준 라이브러리가 이를 잘 보여준다:

```go
// io 패키지 — 1-2개 메서드의 작은 인터페이스
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

// 조합을 통한 확장
type ReadWriter interface {
    Reader
    Writer
}
```

"Accept interfaces, return structs" 원칙의 기술적 근거:

1. **의존성 역전**: 함수가 인터페이스를 받으면 구체 타입에 의존하지 않으므로 패키지 간 결합도가 낮아진다.
2. **테스트 용이성**: mock/stub 주입이 자연스럽다.
3. **구체 타입 반환**: 반환 시 구체 타입을 쓰면 호출자가 해당 타입의 모든 메서드에 접근 가능하고, 호출자가 자신의 인터페이스로 좁힐 수 있다.

```go
// 패키지 storage — 구체 타입 반환
type PostgresStore struct {
    db *sql.DB
}

func NewPostgresStore(dsn string) *PostgresStore {  // struct 반환
    db, _ := sql.Open("postgres", dsn)
    return &PostgresStore{db: db}
}

func (s *PostgresStore) GetUser(ctx context.Context, id string) (User, error) { /* ... */ }
func (s *PostgresStore) ListUsers(ctx context.Context, filter Filter) ([]User, error) { /* ... */ }
func (s *PostgresStore) DeleteUser(ctx context.Context, id string) error { /* ... */ }
func (s *PostgresStore) HealthCheck(ctx context.Context) error { /* ... */ }

// 패키지 handler — 소비자 측에서 필요한 인터페이스만 정의
type UserGetter interface {
    GetUser(ctx context.Context, id string) (storage.User, error)
}

func NewGetUserHandler(store UserGetter) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        user, err := store.GetUser(r.Context(), r.PathValue("id"))
        // ... 에러 처리 및 응답
    })
}
```

**Step 3 — 다양한 관점**

1. **인터페이스가 너무 클 때 (Fat Interface)**: 모든 DB 연산을 하나의 `Repository` 인터페이스에 넣으면 mock 작성이 고통스러워진다. 20개 메서드 중 테스트에 필요한 건 1개인데 나머지 19개를 모두 stub해야 한다. 또한 이 인터페이스를 import하는 모든 패키지가 불필요한 의존성을 끌고 온다.

2. **인터페이스가 너무 작거나 과도할 때**: 모든 함수에 1-메서드 인터페이스를 만들면 코드 추적(code navigation)이 어렵고, 인터페이스 타입이 폭발적으로 증가한다. Go 속담 "Don't abstract prematurely"를 기억해야 한다. 인터페이스는 **두 번째 구현체가 필요할 때** 또는 **테스트에서 mock이 필요할 때** 도입한다.

3. **컴파일 시간 관점**: implicit satisfaction 덕분에 패키지 A가 패키지 B의 인터페이스를 import할 필요가 없다. 이는 대규모 모노레포에서 컴파일 그래프를 얕게 유지하는 데 핵심적이다. Google의 Go 코드베이스가 수억 줄에서도 빠른 빌드를 유지하는 이유 중 하나다.

**Step 4 — 구체적 예시**

프로덕션에서 Fat Interface를 ISP 적용으로 리팩토링하는 과정:

```go
// ❌ BEFORE: Fat Interface — 모든 소비자가 이것에 의존
type OrderRepository interface {
    Create(ctx context.Context, order Order) error
    GetByID(ctx context.Context, id string) (Order, error)
    List(ctx context.Context, filter OrderFilter) ([]Order, error)
    Update(ctx context.Context, order Order) error
    Delete(ctx context.Context, id string) error
    GetByCustomer(ctx context.Context, customerID string) ([]Order, error)
    CountByStatus(ctx context.Context, status Status) (int64, error)
    BulkInsert(ctx context.Context, orders []Order) error
}

// ✅ AFTER: 소비자 측에서 필요한 만큼만 정의

// order/handler 패키지
type OrderReader interface {
    GetByID(ctx context.Context, id string) (Order, error)
}

// order/report 패키지
type OrderCounter interface {
    CountByStatus(ctx context.Context, status Status) (int64, error)
    List(ctx context.Context, filter OrderFilter) ([]Order, error)
}

// order/migration 패키지
type OrderWriter interface {
    BulkInsert(ctx context.Context, orders []Order) error
}

// 컴파일 타임 인터페이스 만족 검증 (관용적 패턴)
var _ OrderReader = (*PostgresOrderStore)(nil)
var _ OrderCounter = (*PostgresOrderStore)(nil)
var _ OrderWriter = (*PostgresOrderStore)(nil)
```

`var _ Interface = (*Struct)(nil)` 패턴은 컴파일 타임에 구조체가 인터페이스를 만족시키는지 검증한다. implicit satisfaction의 약점(실수로 메서드 시그니처를 변경하면 컴파일은 되지만 인터페이스를 더 이상 만족시키지 않음)을 보완한다.

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| **소비자 측 1-2 메서드 인터페이스** | 테스트 용이, 결합도 최저, ISP 완벽 준수 | 인터페이스 수 증가, 코드 네비게이션 어려움 | 패키지 경계가 명확한 대규모 시스템 |
| **생산자 측 중간 크기 인터페이스** | 발견 용이, 문서화 역할, IDE 지원 우수 | 불필요한 의존성 전파 | 라이브러리/SDK 공개 API |
| **인터페이스 없이 구체 타입 직접 사용** | 단순, 코드 추적 쉬움 | mock 불가, 결합도 높음 | 내부 유틸, 변경 가능성 없는 코드 |
| **Embedding으로 인터페이스 조합** | 기존 인터페이스 재사용, 점진적 확장 | 과도한 조합은 Fat Interface와 동일 | 표준 라이브러리 스타일 (io.ReadWriteCloser) |

**Step 6 — 성장 & 심화 학습**

1. Go 표준 라이브러리의 인터페이스 패턴 학습: `io`, `net/http`, `database/sql`, `sort` 패키지
2. Dave Cheney의 "SOLID Go Design" 발표 자료
3. Google 내부 Go 스타일 가이드의 인터페이스 섹션 (공개 버전: https://google.github.io/styleguide/go)
4. Ben Johnson의 "Standard Package Layout" 블로그
5. `uber-go/guide`의 인터페이스 관련 섹션

**🎯 면접관 평가 기준:**

- **L6 PASS**: implicit satisfaction의 동작 원리를 설명하고, ISP를 Go에 적용하는 방법(소비자 측 인터페이스)을 코드로 보여줄 수 있다. "Accept interfaces, return structs" 원칙의 이유를 설명한다.
- **L7 EXCEED**: 컴파일 타임 인터페이스 검증 패턴, 패키지 의존성 그래프에 미치는 영향, structural vs nominal subtyping의 트레이드오프, 대규모 모노레포에서의 실제 경험을 논의한다.
- **🚩 RED FLAG**: 인터페이스를 생산자 측에서만 정의하거나, `interface{}` 남용을 정상적이라고 답변하거나, implicit satisfaction의 컴파일 타임 안전성 한계를 인식하지 못하는 경우.

---

### Q11: Empty Interface(`any`) 함정과 Type Assertion — 타입 안전성 복원 전략

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Interface Design

**Question:**
Go 1.18 이후 `any`(`interface{}`)의 사용이 제네릭 도입으로 어떻게 변화했는가? `any`를 사용해야만 하는 정당한 케이스와 제네릭으로 대체해야 하는 케이스를 구분하라. Type assertion과 type switch의 내부 동작(itab 조회)을 설명하고, 성능 특성을 논의하라.

---

**🧒 12살 비유:**
마트에서 "아무 물건이나 넣을 수 있는 상자"가 `any`야. 편리하지만 상자를 열 때마다 "이게 사과인지 우유인지" 확인해야 해서 번거롭고 실수하기 쉬워. Go 1.18에서 나온 제네릭은 "과일 전용 상자", "음료 전용 상자"를 만들 수 있게 해줘서, 상자를 열기 전에 이미 뭐가 들었는지 알 수 있어. 근데 "진짜로 아무 물건이나" 넣어야 하는 택배 상자 같은 경우엔 여전히 `any`가 필요해.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

면접관은 (1) 제네릭 도입 전후의 Go 타입 시스템 변화를 이해하는지, (2) `any`의 정당한 사용 사례와 남용을 구분하는지, (3) 런타임 type assertion의 비용과 내부 메커니즘을 아는지 평가한다. L6/L7 엔지니어는 `any`에서 제네릭으로의 마이그레이션 전략을 실제 프로덕션 경험으로 설명할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

Go의 인터페이스 값은 내부적으로 두 개의 포인터로 구성된다:

```
┌──────────────────┐
│  interface value  │
├─────────┬────────┤
│  type   │  data  │
│  (itab) │  (ptr) │
└─────────┴────────┘
```

- **itab**: 인터페이스 타입과 구체 타입의 매핑 테이블. 메서드 디스패치를 위한 함수 포인터 배열 포함.
- **data**: 실제 값에 대한 포인터. 값이 포인터 크기 이하이면 직접 저장(scalar optimization).

`any`(빈 인터페이스)는 메서드가 없으므로 모든 타입이 만족시킨다. `any`에 값을 할당하면 boxing이 발생하고, 꺼낼 때 type assertion으로 unboxing한다.

```go
// Type assertion — itab의 타입 정보를 비교
val, ok := x.(string)  // 안전한 형태 (comma-ok pattern)
val := x.(string)       // panic 가능한 형태

// Type switch — 여러 타입을 순차 매칭
switch v := x.(type) {
case string:
    fmt.Println("string:", v)
case int:
    fmt.Println("int:", v)
case io.Reader:
    // 인터페이스 매칭도 가능 (itab 호환성 검사)
    buf := make([]byte, 1024)
    v.Read(buf)
default:
    fmt.Printf("unknown: %T\n", v)
}
```

제네릭 도입 후 `any` 사용이 정당한 케이스 vs 대체해야 하는 케이스:

```go
// ❌ 제네릭으로 대체해야 하는 케이스
// BEFORE (Go 1.17 이전)
func Contains(slice []interface{}, target interface{}) bool {
    for _, v := range slice {
        if v == target {
            return true
        }
    }
    return false
}

// AFTER (Go 1.18+) — 컴파일 타임 타입 안전성 확보
func Contains[T comparable](slice []T, target T) bool {
    for _, v := range slice {
        if v == target {
            return true
        }
    }
    return false
}

// ✅ any가 정당한 케이스: JSON 처리, reflection 기반 프레임워크
func DecodeJSON(data []byte) (map[string]any, error) {
    var result map[string]any
    err := json.Unmarshal(data, &result)
    return result, err
}

// ✅ any가 정당한 케이스: structured logging의 key-value pairs
logger.Info("user action",
    slog.String("user_id", uid),
    slog.Any("metadata", metadata),  // 런타임 타입이 결정됨
)
```

**Step 3 — 다양한 관점**

1. **성능 관점**: Type assertion은 itab 포인터 비교로 구현되므로 매우 빠르다(~1-2ns). 하지만 `any` boxing/unboxing은 힙 할당을 유발할 수 있다. 제네릭 함수는 Go 1.22 기준 **GCShape stenciling** 방식으로 컴파일되어, 포인터 타입은 하나의 구현을 공유하고 값 타입(int, float64 등)은 별도 구현을 생성한다. 따라서 값 타입에 대해 제네릭이 `any`보다 할당이 적다.

2. **코드 정확성 관점**: `any`는 타입 오류를 런타임으로 미루지만, 제네릭은 컴파일 타임에 잡는다. 대규모 코드베이스에서 `any` 관련 panic은 프로덕션 인시던트의 흔한 원인이다. 제네릭 마이그레이션 시 컴파일러가 기존 버그를 발견하는 경우가 빈번하다.

3. **API 설계 관점**: 라이브러리 작성 시 `any`를 파라미터로 받으면 사용자가 잘못된 타입을 전달하는 것을 막을 수 없다. 제네릭 constraint로 허용 타입을 명시하면 godoc이 자동으로 허용 타입을 문서화한다.

**Step 4 — 구체적 예시**

프로덕션에서 `any` 기반 미들웨어를 제네릭+type constraint로 개선하는 사례:

```go
// context에 타입 안전하게 값을 저장하는 패턴
// ❌ BEFORE: any 기반 — 키 충돌, 타입 오류 위험
type contextKey string
const userKey contextKey = "user"

func SetUser(ctx context.Context, user *User) context.Context {
    return context.WithValue(ctx, userKey, user) // any로 저장
}

func GetUser(ctx context.Context) *User {
    u, ok := ctx.Value(userKey).(*User)  // 매번 type assertion 필요
    if !ok {
        return nil  // 타입 불일치 시 silent nil
    }
    return u
}

// ✅ AFTER: 제네릭 context accessor 패턴 (Go 1.22+)
type ContextKey[T any] struct {
    name string
}

func NewContextKey[T any](name string) ContextKey[T] {
    return ContextKey[T]{name: name}
}

func WithValue[T any](ctx context.Context, key ContextKey[T], val T) context.Context {
    return context.WithValue(ctx, key, val)
}

func Value[T any](ctx context.Context, key ContextKey[T]) (T, bool) {
    val, ok := ctx.Value(key).(T)
    return val, ok
}

// 사용 — 키 정의 시점에 타입이 고정됨
var userKey = NewContextKey[*User]("user")
var traceKey = NewContextKey[string]("trace-id")

func middleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        ctx := WithValue(r.Context(), userKey, authenticatedUser)
        ctx = WithValue(ctx, traceKey, uuid.NewString())
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

func handler(w http.ResponseWriter, r *http.Request) {
    user, ok := Value(r.Context(), userKey)  // 반환 타입이 *User로 고정
    traceID, _ := Value(r.Context(), traceKey)  // 반환 타입이 string으로 고정
    // ...
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| **`any` + type assertion** | 유연, 레거시 호환, 리플렉션 연동 | 런타임 panic 위험, boxing 비용 | JSON/encoding, 프레임워크 내부 |
| **제네릭 (type parameters)** | 컴파일 타임 안전성, IDE 자동완성 | 제약된 constraint 표현력, 바이너리 크기 증가 | 컬렉션, 알고리즘, 타입 안전 API |
| **type switch** | 명시적 타입 분기, exhaustive 처리 가능 | 새 타입 추가 시 모든 switch 수정 필요 | 알려진 타입 집합의 다형성 |
| **코드 생성 (go generate)** | 제네릭 이전의 타입 안전 대안 | 빌드 복잡도, 생성 코드 관리 | 레거시 코드, 극단적 성능 요구 |

**Step 6 — 성장 & 심화 학습**

1. Go 내부: `runtime/iface.go`의 `assertI2T`, `assertI2I` 함수 소스 코드 분석
2. Go proposal #43651 (Type parameter constraints) 토론 읽기
3. Russ Cox의 "GCShape stenciling" 설계 문서
4. `go test -bench` 로 type assertion vs 제네릭 vs 리플렉션 벤치마크 직접 수행
5. Ian Lance Taylor의 "Generics Implementation" 발표

**🎯 면접관 평가 기준:**

- **L6 PASS**: `any`와 제네릭의 사용 기준을 명확히 구분하고, type assertion의 comma-ok 패턴을 올바르게 사용하며, boxing 비용을 인지한다.
- **L7 EXCEED**: itab 내부 구조와 GCShape stenciling을 설명하고, 대규모 코드베이스에서의 `any` → 제네릭 마이그레이션 전략과 실제 성능 차이를 벤치마크로 논의한다.
- **🚩 RED FLAG**: `any`와 제네릭의 차이를 "문법적 편의"로만 설명하거나, type assertion 실패 시 panic 가능성을 언급하지 않거나, 제네릭이 모든 `any` 사용을 대체할 수 있다고 단정하는 경우.

---

### Q12: Interface Embedding과 Composition — 다이아몬드 문제 없는 다형성 설계

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Interface Design

**Question:**
Go의 interface embedding은 전통적 OOP의 상속과 어떻게 다른가? 대규모 시스템에서 interface embedding을 사용한 계층적 인터페이스 설계의 모범 사례와 함정을 설명하라. 특히 struct embedding과 interface embedding의 차이가 메서드 resolution과 타입 시스템에 미치는 영향을 구체적으로 논의하라.

---

**🧒 12살 비유:**
USB 허브를 생각해봐. USB-A 포트와 USB-C 포트를 각각 가진 작은 허브 두 개가 있어. Go의 interface embedding은 이 두 허브를 합쳐서 "USB-A+C 허브"를 만드는 거야. 상속(inheritance)은 "USB-A 허브를 상속받아서 USB-C를 추가한 허브"를 만드는 건데, 부모가 바뀌면 자식도 깨져. Go 방식은 그냥 필요한 포트들을 모아 붙이는 거라서 부모-자식 관계가 없어.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

면접관은 (1) Go의 composition-over-inheritance 철학을 체화하고 있는지, (2) struct embedding의 method promotion 규칙과 interface embedding의 차이를 정확히 아는지, (3) embedding을 통한 인터페이스 조합이 실제 시스템 설계에서 어떤 패턴으로 활용되는지를 평가한다. 특히 struct embedding의 "is-a가 아닌 has-a" 본질과, embedding된 메서드의 receiver가 여전히 inner type인 점을 이해하는지가 핵심이다.

**Step 2 — 핵심 기술 설명**

**Interface Embedding**: 인터페이스 안에 다른 인터페이스를 포함시켜 메서드 집합을 합성한다. 이는 순수하게 타입 시스템 수준의 조합이다.

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Closer interface {
    Close() error
}

// Interface embedding — Reader와 Closer의 메서드 집합 합집합
type ReadCloser interface {
    Reader
    Closer
}
```

**Struct Embedding**: 구조체 안에 다른 타입을 이름 없이 포함시키면 메서드가 promote된다. 하지만 이는 "위임(delegation)"이지 "상속"이 아니다.

```go
type Logger struct {
    prefix string
}

func (l *Logger) Log(msg string) {
    fmt.Printf("[%s] %s\n", l.prefix, msg)
}

type Service struct {
    *Logger  // struct embedding — Logger의 Log 메서드가 promote됨
    name string
}

// Service에서 직접 호출 가능하지만, receiver는 여전히 *Logger
svc := &Service{Logger: &Logger{prefix: "SVC"}, name: "orders"}
svc.Log("started")  // (*svc.Logger).Log("started") 와 동일
```

핵심 차이점 — **메서드 receiver**:

```go
type Base struct{ ID int }
func (b *Base) Identify() string { return fmt.Sprintf("Base-%d", b.ID) }

type Derived struct {
    *Base
    Extra string
}

// Derived가 Identify를 "상속"한 것처럼 보이지만,
// Identify()의 receiver는 *Base다 — *Derived가 아니다.
// 따라서 Identify() 안에서 Derived.Extra에 접근할 수 없다.
// 이것이 Go embedding이 상속이 아닌 이유다.
```

**메서드 충돌 해결**: 같은 이름의 메서드가 여러 embedded field에서 promote되면 ambiguity 에러가 발생한다. 이를 해결하려면 outer type에서 직접 해당 메서드를 정의한다.

```go
type A struct{}
func (A) Do() string { return "A" }

type B struct{}
func (B) Do() string { return "B" }

type C struct {
    A
    B
}
// c.Do() → 컴파일 에러: ambiguous selector c.Do

// 해결: C에서 명시적으로 정의
func (c C) Do() string {
    return c.A.Do() + "+" + c.B.Do()  // 명시적 위임
}
```

**Step 3 — 다양한 관점**

1. **다이아몬드 문제 부재**: Go는 상속 계층이 없으므로 전통적 다이아몬드 문제가 발생하지 않는다. 동일 메서드 시그니처 충돌은 "가장 얕은 depth 우선(shallowest wins)" 규칙으로 해결되며, 동일 depth면 컴파일 에러로 명시적 해결을 강제한다.

2. **인터페이스 오염 위험**: struct embedding으로 인터페이스를 만족시킬 때, 의도하지 않은 메서드까지 promote되어 예상치 못한 인터페이스를 만족시킬 수 있다. 이는 implicit satisfaction과 결합되어 미묘한 버그를 만든다.

3. **테스트에서의 partial implementation 패턴**: 큰 인터페이스를 테스트할 때 embedding을 활용한 partial mock이 유용하다. 하지만 이 패턴의 위험성도 알아야 한다.

```go
// 주의가 필요한 partial mock 패턴
type mockStore struct {
    storage.Store  // 인터페이스 embedding — 모든 메서드를 "구현"한 것처럼 보임
}

func (m *mockStore) GetUser(ctx context.Context, id string) (User, error) {
    return User{ID: id, Name: "test"}, nil
}

// ⚠️ 위험: Store의 다른 메서드(Delete, Update 등)가 호출되면
// nil pointer panic 발생 — embedded interface가 nil이므로
```

**Step 4 — 구체적 예시**

프로덕션 미들웨어 체인에서 interface embedding을 활용한 계층적 설계:

```go
// 기본 인터페이스 — 읽기 전용 오퍼레이션
type UserReader interface {
    GetUser(ctx context.Context, id string) (User, error)
    ListUsers(ctx context.Context, opts ListOpts) ([]User, error)
}

// 쓰기 오퍼레이션
type UserWriter interface {
    CreateUser(ctx context.Context, user User) error
    UpdateUser(ctx context.Context, user User) error
}

// 삭제 오퍼레이션 (관리자 전용)
type UserDeleter interface {
    DeleteUser(ctx context.Context, id string) error
}

// 역할별 조합
type UserService interface {
    UserReader
    UserWriter
}

type UserAdmin interface {
    UserService
    UserDeleter
}

// 구현 — 하나의 struct가 모든 레벨의 인터페이스를 만족
type userStore struct {
    db *sql.DB
}

func (s *userStore) GetUser(ctx context.Context, id string) (User, error) { /* ... */ }
func (s *userStore) ListUsers(ctx context.Context, opts ListOpts) ([]User, error) { /* ... */ }
func (s *userStore) CreateUser(ctx context.Context, user User) error { /* ... */ }
func (s *userStore) UpdateUser(ctx context.Context, user User) error { /* ... */ }
func (s *userStore) DeleteUser(ctx context.Context, id string) error { /* ... */ }

// 핸들러는 필요한 인터페이스만 의존
func NewPublicHandler(r UserReader) http.Handler { /* 읽기만 */ }
func NewAuthHandler(s UserService) http.Handler { /* 읽기+쓰기 */ }
func NewAdminHandler(a UserAdmin) http.Handler { /* 전체 접근 */ }

// http.ResponseWriter의 실제 interface embedding 사례 (표준 라이브러리)
// http.Flusher, http.Hijacker 등은 ResponseWriter에 embedded되지 않고
// 런타임 type assertion으로 확인 — 왜?
// → 모든 ResponseWriter 구현이 Flush/Hijack을 지원하지 않으므로
// → 이것이 "interface embedding vs type assertion" 설계 결정의 핵심
func writeSSE(w http.ResponseWriter, data []byte) {
    w.Write(data)
    if f, ok := w.(http.Flusher); ok {  // 선택적 기능 확인
        f.Flush()
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| **Interface embedding (조합)** | 타입 안전, 역할별 분리, 문서화 역할 | 인터페이스 수 증가 | 명확한 역할 계층이 있을 때 |
| **Struct embedding (위임)** | 코드 재사용, 보일러플레이트 감소 | 의도하지 않은 메서드 노출, receiver 혼동 | 내부 구현의 코드 공유 |
| **명시적 필드 + 수동 위임** | 완전한 통제, 의도 명확 | 보일러플레이트 증가 | 세밀한 메서드 제어 필요 시 |
| **Functional options 패턴** | 유연한 설정, 인터페이스 불필요 | 타입 검사 약화 | 설정/옵션 조합 |

**Step 6 — 성장 & 심화 학습**

1. Go spec의 "Method sets" 섹션 정독 — pointer receiver vs value receiver의 메서드 집합 차이
2. 표준 라이브러리 `io` 패키지의 인터페이스 조합 패턴 분석
3. `net/http` 패키지에서 `ResponseWriter`와 `Flusher`/`Hijacker`의 관계 분석
4. Effective Go의 "Embedding" 섹션
5. Bill Kennedy의 "Composition with Go" 시리즈

**🎯 면접관 평가 기준:**

- **L6 PASS**: interface embedding과 struct embedding의 차이를 설명하고, 메서드 promotion 규칙과 충돌 해결을 코드로 보여준다. composition-over-inheritance의 Go적 의미를 이해한다.
- **L7 EXCEED**: embedded struct의 receiver가 inner type인 점의 함의, 의도하지 않은 인터페이스 만족 문제, 표준 라이브러리의 embedding 패턴(io.ReadWriteCloser, http.ResponseWriter+Flusher)을 비교 분석하며 설계 결정의 근거를 설명한다.
- **🚩 RED FLAG**: struct embedding을 "상속"이라고 부르거나, 메서드 충돌 시 해결 규칙을 모르거나, interface embedding과 struct embedding을 혼동하는 경우.

---

## 5. Error Handling

### Q13: Error Wrapping과 Sentinel Errors — 에러 체인 설계 전략

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Error Handling

**Question:**
Go의 에러 처리에서 `%w`를 사용한 error wrapping, sentinel errors, typed errors의 트레이드오프를 설명하라. `errors.Is`와 `errors.As`의 내부 동작(Unwrap chain 순회)을 설명하고, 대규모 마이크로서비스에서 에러 체인이 서비스 경계를 넘을 때 발생하는 문제와 해결 전략을 논의하라.

---

**🧒 12살 비유:**
편지 배달을 생각해봐. 네가 편지를 쓰면(원본 에러), 반장이 "이 편지가 왔는데요"라고 메모를 붙여서 선생님에게 전달하고(wrap), 선생님은 또 메모를 붙여서 교장 선생님에게 전달해(wrap). 교장 선생님이 "이 편지가 원래 누구한테서 온 거야?"라고 확인하는 게 `errors.Is`야 — 메모를 하나씩 벗겨가면서 원본을 찾는 거지. `errors.As`는 "이 편지 체인에 선생님이 쓴 메모가 있어?"처럼 특정 종류의 메모를 찾는 거야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

에러 처리는 Go 코드의 30-40%를 차지하며, 잘못 설계하면 디버깅 시간이 기하급수적으로 증가한다. 면접관은 (1) Go 1.13에서 도입된 에러 wrapping 메커니즘의 정확한 동작을 이해하는지, (2) sentinel vs typed vs wrapping의 선택 기준이 있는지, (3) 마이크로서비스 경계에서 에러 전파 전략을 설계할 수 있는지를 평가한다. L6/L7은 에러가 API 계약의 일부라는 관점에서 답변해야 한다.

**Step 2 — 핵심 기술 설명**

Go의 에러 체계는 세 가지 층위로 나뉜다:

**1. Sentinel Errors**: 패키지 수준의 전역 변수로 정의된 고정 에러값.

```go
// 표준 라이브러리 예시
var ErrNotFound = errors.New("not found")
var ErrPermissionDenied = errors.New("permission denied")

// 사용
if err == ErrNotFound { /* ... */ }
// 또는 wrapping 이후에도 비교 가능
if errors.Is(err, ErrNotFound) { /* ... */ }
```

**2. Typed Errors**: 커스텀 타입으로 정의되어 추가 컨텍스트를 포함.

```go
type NotFoundError struct {
    Resource string
    ID       string
}

func (e *NotFoundError) Error() string {
    return fmt.Sprintf("%s %s not found", e.Resource, e.ID)
}

// 사용 — errors.As로 타입 매칭 + 필드 접근
var nfe *NotFoundError
if errors.As(err, &nfe) {
    log.Printf("Resource %s with ID %s not found", nfe.Resource, nfe.ID)
}
```

**3. Error Wrapping (`%w`)**: 원본 에러를 보존하면서 컨텍스트를 추가.

```go
func (s *UserService) GetUser(ctx context.Context, id string) (User, error) {
    user, err := s.repo.FindByID(ctx, id)
    if err != nil {
        // %w로 원본 에러를 wrapping — errors.Is/As가 체인을 따라갈 수 있음
        return User{}, fmt.Errorf("GetUser(id=%s): %w", id, err)
    }
    return user, nil
}
```

`errors.Is`와 `errors.As`의 내부 동작:

```go
// errors.Is의 의사 코드 — Unwrap chain을 재귀적으로 순회
func Is(err, target error) bool {
    for {
        if err == target {  // 직접 비교
            return true
        }
        // Go 1.20+: Unwrap() []error도 지원 (multi-error)
        if x, ok := err.(interface{ Unwrap() error }); ok {
            err = x.Unwrap()
            if err == nil {
                return false
            }
            continue
        }
        // 커스텀 Is 메서드 지원
        if x, ok := err.(interface{ Is(error) bool }); ok {
            return x.Is(target)
        }
        return false
    }
}

// errors.As — 체인에서 특정 타입 찾기
func As(err error, target any) bool {
    // 체인을 순회하면서 target 타입에 할당 가능한 에러를 찾음
    // target은 반드시 non-nil 포인터여야 함
    for {
        if reflect.TypeOf(err).AssignableTo(targetType) {
            targetVal.Set(reflect.ValueOf(err))
            return true
        }
        if x, ok := err.(interface{ Unwrap() error }); ok {
            err = x.Unwrap()
            continue
        }
        return false
    }
}
```

**Step 3 — 다양한 관점**

1. **에러 wrapping의 API 계약 문제**: `%w`로 내부 에러를 wrapping하면 호출자가 `errors.Is`로 내부 구현 세부사항에 의존하게 된다. 예를 들어 `errors.Is(err, sql.ErrNoRows)`가 가능해지면 DB를 PostgreSQL에서 MongoDB로 교체할 때 호출자 코드가 깨진다. 이 때문에 **서비스 경계에서는 `%w` 대신 `%v`를 사용**하거나, 도메인 에러로 변환해야 한다.

```go
// ❌ 내부 구현 노출
func (r *repo) GetUser(ctx context.Context, id string) (User, error) {
    err := r.db.QueryRow(...).Scan(...)
    if err != nil {
        return User{}, fmt.Errorf("get user: %w", err)  // sql.ErrNoRows 노출!
    }
    return user, nil
}

// ✅ 도메인 에러로 변환 — 구현 세부사항 은닉
func (r *repo) GetUser(ctx context.Context, id string) (User, error) {
    err := r.db.QueryRow(...).Scan(...)
    if errors.Is(err, sql.ErrNoRows) {
        return User{}, fmt.Errorf("get user: %w", ErrNotFound)  // 도메인 에러로 변환
    }
    if err != nil {
        return User{}, fmt.Errorf("get user: %w", err)
    }
    return user, nil
}
```

2. **마이크로서비스 경계에서의 에러 전파**: gRPC/HTTP 경계를 넘으면 Go의 에러 체인이 직렬화되지 않는다. 서비스 경계에서는 에러를 gRPC status code + 구조화된 에러 detail로 변환하고, 수신 측에서 다시 도메인 에러로 복원해야 한다.

3. **Go 1.20 Multi-error**: `errors.Join`과 `Unwrap() []error`로 여러 에러를 하나로 합칠 수 있다. 이는 concurrent 작업의 에러 수집에 유용하다.

```go
func validateUser(u User) error {
    var errs []error
    if u.Name == "" {
        errs = append(errs, fmt.Errorf("name: %w", ErrRequired))
    }
    if u.Email == "" {
        errs = append(errs, fmt.Errorf("email: %w", ErrRequired))
    }
    if !isValidEmail(u.Email) {
        errs = append(errs, fmt.Errorf("email: %w", ErrInvalidFormat))
    }
    return errors.Join(errs...)  // nil if len(errs) == 0
}

// errors.Is는 multi-error의 모든 트리를 탐색
err := validateUser(user)
errors.Is(err, ErrRequired)      // true — 트리 내 어딘가에 있으면
errors.Is(err, ErrInvalidFormat)  // true
```

**Step 4 — 구체적 예시**

프로덕션 에러 처리 아키텍처 — 계층별 에러 변환 패턴:

```go
// ── 1. 도메인 에러 정의 (domain/errors.go) ──
package domain

// Sentinel errors — 비즈니스 규칙 위반
var (
    ErrNotFound      = errors.New("not found")
    ErrAlreadyExists = errors.New("already exists")
    ErrForbidden     = errors.New("forbidden")
)

// Typed error — 검증 실패 (상세 정보 포함)
type ValidationError struct {
    Field   string
    Message string
}
func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation: %s — %s", e.Field, e.Message)
}

// ── 2. Repository 계층 — DB 에러를 도메인 에러로 변환 ──
func (r *pgUserRepo) GetByID(ctx context.Context, id string) (domain.User, error) {
    var user domain.User
    err := r.db.QueryRowContext(ctx, "SELECT ... WHERE id=$1", id).Scan(&user.ID, &user.Name)
    switch {
    case errors.Is(err, sql.ErrNoRows):
        return domain.User{}, fmt.Errorf("user(id=%s): %w", id, domain.ErrNotFound)
    case err != nil:
        return domain.User{}, fmt.Errorf("user(id=%s) query: %w", id, err) // 인프라 에러는 wrapping
    }
    return user, nil
}

// ── 3. HTTP 계층 — 도메인 에러를 HTTP 상태 코드로 변환 ──
func errorToHTTP(w http.ResponseWriter, err error) {
    var ve *domain.ValidationError

    switch {
    case errors.Is(err, domain.ErrNotFound):
        writeJSON(w, http.StatusNotFound, map[string]string{"error": err.Error()})
    case errors.Is(err, domain.ErrForbidden):
        writeJSON(w, http.StatusForbidden, map[string]string{"error": "access denied"})
    case errors.As(err, &ve):
        writeJSON(w, http.StatusBadRequest, map[string]any{
            "error": "validation failed",
            "field": ve.Field,
            "detail": ve.Message,
        })
    default:
        // 알 수 없는 에러 — 내부 정보 노출 방지
        slog.Error("unhandled error", "err", err)
        writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "internal error"})
    }
}

// ── 4. gRPC 경계 — 도메인 에러를 gRPC status로 변환 ──
func domainToGRPCStatus(err error) error {
    switch {
    case errors.Is(err, domain.ErrNotFound):
        return status.Error(codes.NotFound, err.Error())
    case errors.Is(err, domain.ErrAlreadyExists):
        return status.Error(codes.AlreadyExists, err.Error())
    case errors.Is(err, domain.ErrForbidden):
        return status.Error(codes.PermissionDenied, err.Error())
    default:
        return status.Error(codes.Internal, "internal error")
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| **Sentinel errors (`var Err = errors.New`)** | 단순, 비교 용이, 표준 패턴 | 추가 컨텍스트 불가, 전역 상태 | 비즈니스 규칙 위반 (NotFound, Forbidden) |
| **Typed errors (`struct + Error()`)** | 풍부한 컨텍스트, 구조화된 정보 | 타입 정의 오버헤드, As() 사용 복잡 | 검증 에러, 여러 필드가 필요한 에러 |
| **`%w` wrapping** | 에러 체인 보존, 디버깅 용이 | API 결합도 증가, 내부 구현 노출 위험 | 같은 패키지/모듈 내부 계층 간 |
| **`%v` formatting (wrapping 없음)** | 구현 은닉, API 안정성 | 원본 에러 정보 소실, Is/As 불가 | 서비스 경계, 공개 API |
| **`errors.Join` (multi-error)** | 여러 에러 수집, Is/As 모두 동작 | 에러 메시지 읽기 어려움 | 검증, concurrent 작업 |

**Step 6 — 성장 & 심화 학습**

1. Go 공식 블로그 "Working with Errors in Go 1.13" 정독
2. `errors` 패키지 소스 코드 분석 (200줄 미만)
3. Go proposal #53435 (structured errors) 토론
4. hashicorp/go-multierror → errors.Join 마이그레이션 사례
5. gRPC-Go의 `status` 패키지 에러 변환 패턴

**🎯 면접관 평가 기준:**

- **L6 PASS**: sentinel/typed/wrapped 에러의 차이와 선택 기준을 명확히 설명하고, `errors.Is/As`의 체인 순회 동작을 이해한다. `%w` vs `%v`의 API 계약 관점 차이를 안다.
- **L7 EXCEED**: 서비스 경계에서의 에러 변환 전략(도메인 에러 → gRPC status → HTTP status), Go 1.20 multi-error, 에러 wrapping이 API 결합도에 미치는 영향을 실제 사례로 논의한다.
- **🚩 RED FLAG**: 에러를 `log.Fatal`이나 `panic`으로 처리하거나, `%w`와 `%v`의 차이를 모르거나, `errors.Is`를 `==`로 대체할 수 있다고 답변하는 경우.

---

### Q14: Panic/Recover와 Structured Error Handling — 경계 방어 설계

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Error Handling

**Question:**
Go에서 `panic`과 `recover`의 사용이 정당화되는 시나리오와 절대 사용하면 안 되는 시나리오를 구분하라. HTTP 서버에서 panic recovery 미들웨어의 구현 원리를 설명하고, goroutine에서 발생한 panic이 프로세스를 죽이는 메커니즘과 이에 대한 방어 전략을 논의하라. 또한 structured error handling(slog, error 코드, 에러 분류)의 프로덕션 설계를 제시하라.

---

**🧒 12살 비유:**
교실에서 수업 중에 문제가 생기면 보통 손을 들고 선생님에게 말하잖아(일반 에러 반환). 그런데 건물에 불이 나면 비상벨을 누르는 거야(panic) — 모든 수업이 중단되고 전부 대피해야 해. `recover`는 소방관이 도착해서 "오, 실제로는 토스터가 탄 거였네. 다시 돌아가도 돼요"라고 말하는 거야. 비상벨은 진짜 비상 상황에만 눌러야지, "연필이 부러졌어"라고 비상벨을 누르면 안 되겠지?

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

면접관은 (1) panic/recover의 올바른 사용 범위를 이해하고 있는지, (2) goroutine panic 전파의 런타임 동작을 아는지, (3) 프로덕션에서 panic을 안전하게 처리하는 방어적 설계를 할 수 있는지를 평가한다. "Go에서 panic은 프로그래머 에러에만 사용하라"는 원칙을 넘어, HTTP 서버/worker pool 등 실제 시스템에서의 panic 방어 전략을 설계할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

**Panic의 런타임 동작**:

1. `panic(v)`가 호출되면 현재 함수의 실행이 즉시 중단된다.
2. 현재 goroutine의 defer 스택이 **역순으로** 실행된다.
3. 모든 defer가 실행된 후, goroutine이 종료된다.
4. **어떤 goroutine의 panic이든 recover되지 않으면 전체 프로세스가 종료된다.**

```go
// panic의 전파 경로
func main() {
    go func() {
        // 이 goroutine에서 panic이 recover되지 않으면
        // main goroutine을 포함한 전체 프로세스가 죽는다
        panic("unrecovered")
    }()
    time.Sleep(time.Second) // 이 줄에 도달하지 못할 수 있음
}
```

**핵심 원칙**: 다른 goroutine의 panic은 recover할 수 없다. `recover()`는 자신이 속한 goroutine의 defer 안에서만 동작한다.

```go
// ❌ 다른 goroutine의 panic은 잡을 수 없음
func main() {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("recovered:", r) // 실행되지 않음!
        }
    }()
    go func() {
        panic("child goroutine panic") // main의 defer에서 recover 불가
    }()
    select {}
}
```

**Panic이 정당화되는 시나리오**:

```go
// 1. 프로그래머 에러 — 복구 불가능한 논리적 버그
func MustCompileRegex(pattern string) *regexp.Regexp {
    re, err := regexp.Compile(pattern)
    if err != nil {
        panic(fmt.Sprintf("invalid regex %q: %v", pattern, err))
    }
    return re
}
// init()이나 프로그램 시작 시에만 사용

// 2. 초기화 실패 — 프로그램이 실행될 수 없는 상태
func init() {
    if os.Getenv("DATABASE_URL") == "" {
        panic("DATABASE_URL environment variable is required")
    }
}

// 3. 표준 라이브러리의 내부 최적화 — encoding/json의 예
// json.Marshal 내부에서 깊은 재귀 중 에러 발생 시
// panic으로 즉시 탈출 후 외부에서 recover로 에러 변환
// (성능 최적화: 매 호출마다 err 반환하지 않기 위해)
```

**HTTP Recovery 미들웨어의 구현**:

```go
func RecoveryMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if rec := recover(); rec != nil {
                // 1. 스택 트레이스 캡처
                stack := make([]byte, 4096)
                n := runtime.Stack(stack, false) // false = 현재 goroutine만

                // 2. 구조화된 로깅
                slog.Error("panic recovered",
                    "panic", rec,
                    "method", r.Method,
                    "path", r.URL.Path,
                    "stack", string(stack[:n]),
                    "request_id", r.Header.Get("X-Request-ID"),
                )

                // 3. 메트릭 기록 (모니터링 연동)
                panicCounter.WithLabelValues(r.URL.Path).Inc()

                // 4. 안전한 에러 응답 (내부 정보 노출 방지)
                if !headerWritten(w) {
                    w.Header().Set("Content-Type", "application/json")
                    w.WriteHeader(http.StatusInternalServerError)
                    json.NewEncoder(w).Encode(map[string]string{
                        "error": "internal server error",
                    })
                }
            }
        }()
        next.ServeHTTP(w, r)
    })
}
```

**Step 3 — 다양한 관점**

1. **Worker Pool에서의 goroutine panic 방어**: 각 worker goroutine에 반드시 recover를 설치해야 한다. 하나의 worker panic이 전체 서비스를 죽이면 안 된다.

```go
func (p *Pool) worker(id int) {
    for task := range p.tasks {
        func() {  // 각 task 처리를 별도 함수로 감싸서 recover 범위 제한
            defer func() {
                if r := recover(); r != nil {
                    slog.Error("worker panic",
                        "worker_id", id,
                        "task", task.ID,
                        "panic", r,
                        "stack", string(debug.Stack()),
                    )
                    p.failedTasks.Inc()
                    // worker는 계속 다음 task를 처리
                }
            }()
            task.Execute()
        }()
    }
}
```

2. **`net/http` 서버의 기본 panic recovery**: Go의 `net/http` 서버는 각 요청을 별도 goroutine에서 처리하며, 내장 panic recovery가 있다. 하지만 이 기본 recovery는 stderr에 출력만 하고 연결을 닫으므로, 프로덕션에서는 커스텀 미들웨어가 필수적이다.

3. **panic vs os.Exit**: `panic`은 defer를 실행하지만 `os.Exit`은 defer를 실행하지 않는다. `log.Fatal`은 내부적으로 `os.Exit(1)`을 호출하므로, 리소스 정리가 필요한 상황에서 사용하면 안 된다. 테스트에서 `log.Fatal`을 사용하면 테스트 프로세스 자체가 종료되는 문제도 있다.

**Step 4 — 구체적 예시**

프로덕션 structured error handling 시스템:

```go
// ── 1. 에러 코드 체계 ──
type ErrorCode string

const (
    ErrCodeValidation   ErrorCode = "VALIDATION_ERROR"
    ErrCodeNotFound     ErrorCode = "NOT_FOUND"
    ErrCodeConflict     ErrorCode = "CONFLICT"
    ErrCodeInternal     ErrorCode = "INTERNAL_ERROR"
    ErrCodeUpstream     ErrorCode = "UPSTREAM_ERROR"
    ErrCodeRateLimit    ErrorCode = "RATE_LIMITED"
)

// ── 2. 구조화된 애플리케이션 에러 ──
type AppError struct {
    Code       ErrorCode         `json:"code"`
    Message    string            `json:"message"`
    Details    map[string]any    `json:"details,omitempty"`
    HTTPStatus int               `json:"-"` // JSON 직렬화 제외
    Cause      error             `json:"-"` // 내부 에러 — 외부 노출 안함
}

func (e *AppError) Error() string {
    if e.Cause != nil {
        return fmt.Sprintf("[%s] %s: %v", e.Code, e.Message, e.Cause)
    }
    return fmt.Sprintf("[%s] %s", e.Code, e.Message)
}

func (e *AppError) Unwrap() error { return e.Cause }

// ── 3. 에러 생성 헬퍼 ──
func NewNotFound(resource, id string) *AppError {
    return &AppError{
        Code:       ErrCodeNotFound,
        Message:    fmt.Sprintf("%s not found", resource),
        Details:    map[string]any{"resource": resource, "id": id},
        HTTPStatus: http.StatusNotFound,
    }
}

func NewValidationError(field, reason string) *AppError {
    return &AppError{
        Code:       ErrCodeValidation,
        Message:    fmt.Sprintf("invalid %s: %s", field, reason),
        Details:    map[string]any{"field": field},
        HTTPStatus: http.StatusBadRequest,
    }
}

func NewInternalError(cause error) *AppError {
    return &AppError{
        Code:       ErrCodeInternal,
        Message:    "internal server error",
        HTTPStatus: http.StatusInternalServerError,
        Cause:      cause,  // 로깅에만 사용, API 응답에는 노출 안함
    }
}

// ── 4. 통합 에러 응답 미들웨어 ──
func ErrorHandler(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // panic recovery + error handling을 하나로 통합
        defer func() {
            if rec := recover(); rec != nil {
                err := NewInternalError(fmt.Errorf("panic: %v", rec))
                slog.ErrorContext(r.Context(), "panic recovered",
                    "error", err,
                    "stack", string(debug.Stack()),
                )
                writeAppError(w, r, err)
            }
        }()
        next.ServeHTTP(w, r)
    })
}

func writeAppError(w http.ResponseWriter, r *http.Request, appErr *AppError) {
    // 구조화된 로깅 — Cause 포함 (외부 응답에는 제외)
    slog.ErrorContext(r.Context(), "request error",
        "code", appErr.Code,
        "message", appErr.Message,
        "status", appErr.HTTPStatus,
        "cause", appErr.Cause,
        "method", r.Method,
        "path", r.URL.Path,
    )

    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(appErr.HTTPStatus)
    // API 응답에는 Code, Message, Details만 포함 (Cause 제외)
    json.NewEncoder(w).Encode(appErr)
}

// ── 5. 핸들러에서의 사용 ──
func GetUserHandler(svc UserService) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        id := r.PathValue("id")
        user, err := svc.GetUser(r.Context(), id)
        if err != nil {
            var appErr *AppError
            if errors.As(err, &appErr) {
                writeAppError(w, r, appErr)
            } else {
                // 예상치 못한 에러 — 내부 에러로 변환
                writeAppError(w, r, NewInternalError(err))
            }
            return
        }
        writeJSON(w, http.StatusOK, user)
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| **panic + recover** | 깊은 호출 스택 즉시 탈출, 초기화 검증 단순화 | 남용 시 에러 흐름 불명확, goroutine 경계 제약 | init, Must* 패턴, 프레임워크 내부 |
| **에러 반환 (관용적 Go)** | 명시적, 추적 가능, 컴파일러 지원 | 보일러플레이트, 체크 누락 가능 | 모든 비즈니스 로직, I/O 작업 |
| **구조화된 AppError** | 에러 코드 표준화, API 일관성, 모니터링 연동 | 추가 추상화 비용, 팀 합의 필요 | HTTP/gRPC API 서버 |
| **slog 구조화 로깅** | 기계 파싱 가능, 비용 효율적, 표준 라이브러리 | Go 1.21+ 필요 | 모든 프로덕션 시스템 |
| **errgroup.Group** | goroutine 에러 수집, context 취소 통합 | panic은 잡지 못함 (별도 recover 필요) | concurrent 작업 조율 |

**Step 6 — 성장 & 심화 학습**

1. Go spec의 "Handling panics" 섹션 — recover의 정확한 의미론
2. `runtime/panic.go` 소스 코드 — panic의 구현 세부사항
3. `net/http` 서버의 `conn.serve()` 소스 코드 — 내장 panic recovery 확인
4. `log/slog` 패키지의 설계 문서 (Jonathan Amsterdam의 proposal)
5. Dave Cheney의 "Don't just check errors, handle them gracefully" 발표
6. `golang.org/x/sync/errgroup` 패키지 분석

**🎯 면접관 평가 기준:**

- **L6 PASS**: panic의 정당한 사용 시나리오(init, Must*, 프로그래머 에러)를 구분하고, recovery 미들웨어를 구현할 수 있다. goroutine 간 panic 격리의 필요성을 이해한다. `errors.Is/As`를 올바르게 사용한다.
- **L7 EXCEED**: 에러 코드 체계, AppError 패턴, 서비스 경계별 에러 변환 전략, worker pool 방어 설계, `slog`를 활용한 구조화된 에러 관측 시스템까지 통합적으로 설계한다. panic vs os.Exit vs log.Fatal의 defer 동작 차이를 정확히 안다.
- **🚩 RED FLAG**: panic을 일반적인 에러 처리에 사용하거나, recover 없이 goroutine을 생성하거나, 에러 메시지에 내부 구현 세부사항(스택 트레이스, DB 쿼리)을 API 응답에 노출하는 경우.

---

## 6. Performance Engineering


> 대상: FAANG L6/L7 (Staff/Principal Engineer)
> 총 문항: 6개 (Q15~Q20) | 난이도: ⭐⭐⭐⭐⭐
> 버전: Go 1.22+

## 목차

- [6. Performance Engineering](#6-performance-engineering) — Q15~Q17
- [7. sync Primitives](#7-sync-primitives) — Q18~Q20

---

## 6. Performance Engineering

### Q15: Escape Analysis와 Stack vs Heap 할당 전략

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Performance Engineering

**Question:**
"Go 컴파일러의 escape analysis가 어떻게 동작하며, 변수가 stack에서 heap으로 escape하는 구체적인 조건들을 설명하세요. `go build -gcflags='-m'` 출력을 읽고 성능을 최적화한 프로덕션 경험이 있다면 공유해주세요. stack 할당과 heap 할당의 성능 차이가 실제로 어느 정도이고, 이를 의식적으로 제어하는 기법들을 논해주세요."

---

**🧒 12살 비유:**
학교에서 연습장(stack)과 사물함(heap)이 있어. 연습장은 수업 끝나면 바로 버리는 거라 정리가 쉬워 — 그냥 페이지를 넘기면 돼. 사물함은 언제 누가 쓸지 모르니까 관리인(GC)이 돌아다니면서 "이거 아직 쓰는 거야?" 하고 확인해야 해. Go 컴파일러는 "이 메모장, 수업 끝나면 버려도 돼?"를 미리 판단해서 가능하면 연습장(stack)에 써. 하지만 다른 수업에서도 필요하면 사물함(heap)에 넣어야 해.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

면접관은 (1) Go 컴파일러 내부에 대한 이해 수준, (2) 메모리 할당이 성능에 미치는 영향을 정량적으로 파악하는 능력, (3) 실전에서 allocation-sensitive 코드를 작성한 경험을 평가한다. L6+ 엔지니어라면 "포인터 반환하면 heap" 수준을 넘어, 컴파일러의 판단 로직과 이를 활용한 최적화 기법을 구체적으로 설명해야 한다.

**Step 2 — 핵심 기술 설명**

Escape analysis는 Go 컴파일러(`cmd/compile`)의 정적 분석 단계로, 변수의 생존 범위(lifetime)가 선언된 함수의 스코프를 벗어나는지 판단한다. 벗어나지 않으면 stack에, 벗어나면 heap에 할당한다.

Heap으로 escape하는 핵심 조건:
1. **포인터가 함수 반환값으로 노출**: 함수가 로컬 변수의 포인터를 반환하면 호출자 stack frame이 살아있는 동안 접근 가능해야 하므로 heap으로 이동
2. **Interface 변환**: 구체 타입을 `interface{}`나 `any`로 변환하면 컴파일러가 사이즈를 정적으로 결정할 수 없어 escape
3. **Closure 캡처**: 클로저가 외부 변수를 캡처하면 클로저의 lifetime이 변수보다 길 수 있어 escape
4. **슬라이스/맵에 포인터 저장**: 동적 자료구조에 포인터를 넣으면 컴파일러가 lifetime을 추적할 수 없음
5. **크기를 컴파일 타임에 알 수 없는 슬라이스**: `make([]byte, n)` — n이 변수이면 escape 가능
6. **goroutine으로 전달**: 변수가 새 goroutine에서 참조되면 현재 stack frame보다 오래 생존할 수 있음

```go
package main

// Case 1: 포인터 반환 → heap escape
func newUser(name string) *User {
    u := User{Name: name} // &u escapes to heap
    return &u
}

// Case 2: 반환 없음 → stack 할당
func processUser(name string) int {
    u := User{Name: name} // stack에 할당
    return len(u.Name)
}

// Case 3: interface 변환 → heap escape
func logValue(v any) { // v interface{} → 내부적으로 heap alloc 가능
    fmt.Println(v)
}

func example() {
    x := 42
    logValue(x) // x escapes to heap (interface 변환)
}

// Case 4: 슬라이스 크기가 상수 → stack 가능
func fixedSlice() [64]byte {
    var buf [64]byte // stack 할당 (고정 크기 배열)
    return buf
}

// Case 5: 슬라이스 크기가 변수 → heap
func dynamicSlice(n int) []byte {
    buf := make([]byte, n) // heap 할당 (크기 미확정)
    return buf
}

type User struct {
    Name string
}
```

진단 명령어:
```bash
go build -gcflags='-m -m' ./...

```

**Step 3 — 다양한 관점**

| 관점 | Stack 할당 | Heap 할당 |
|------|-----------|-----------|
| **속도** | O(1) — SP 레지스터 조정만 | malloc + GC 추적 비용 |
| **GC 부하** | 없음 — 함수 종료 시 자동 해제 | GC scan 대상, STW에 기여 |
| **크기 제한** | goroutine stack (초기 2-8KB, 최대 1GB) | 가용 메모리까지 |
| **Fragmentation** | 없음 | 발생 가능 |
| **Thread safety** | goroutine 전용 — lock 불필요 | 공유 시 동기화 필요 |

실제 성능 차이는 워크로드에 따라 다르지만, hot path에서 heap allocation을 stack으로 전환하면 throughput이 10-30% 개선되는 사례가 흔하다. GC pause가 P99 latency에 미치는 영향까지 고려하면 차이는 더 커진다.

**Step 4 — 구체적 예시: Allocation 최적화 패턴**

```go
package main

import (
    "encoding/json"
    "sync"
)

// 패턴 1: sync.Pool로 반복 할당 회피
var bufPool = sync.Pool{
    New: func() any {
        b := make([]byte, 0, 4096)
        return &b
    },
}

func marshalWithPool(v any) ([]byte, error) {
    bp := bufPool.Get().(*[]byte)
    buf := (*bp)[:0] // 길이만 리셋, 용량 유지
    defer func() {
        *bp = buf
        bufPool.Put(bp)
    }()

    data, err := json.Marshal(v)
    if err != nil {
        return nil, err
    }
    buf = append(buf, data...)
    // 호출자에게는 복사본 반환 (pool 버퍼 재사용 보호)
    result := make([]byte, len(buf))
    copy(result, buf)
    return result, nil
}

// 패턴 2: 포인터 반환 대신 값 반환으로 stack 유지
type Point struct {
    X, Y float64
}

// Bad: heap escape
func NewPointPtr(x, y float64) *Point {
    return &Point{X: x, Y: y} // escapes
}

// Good: stack 할당 (작은 struct는 값 복사가 더 빠름)
func NewPoint(x, y float64) Point {
    return Point{X: x, Y: y} // stays on stack
}

// 패턴 3: 배열 기반 고정 버퍼로 heap 회피
func formatID(prefix string, id uint64) string {
    // make([]byte, ...) 대신 고정 배열 사용
    var buf [32]byte // stack 할당
    n := copy(buf[:], prefix)
    n += putUint64(buf[n:], id)
    return string(buf[:n])
}

func putUint64(buf []byte, v uint64) int {
    i := len(buf)
    for v >= 10 {
        i--
        buf[i] = byte('0' + v%10)
        v /= 10
    }
    i--
    buf[i] = byte('0' + v)
    // shift to beginning
    n := len(buf) - i
    copy(buf[:n], buf[i:])
    return n
}

// 패턴 4: 결과를 caller의 슬라이스에 append (escape 방지)
func appendResults(dst []Result, input []Data) []Result {
    for i := range input {
        r := processOne(&input[i]) // 값 반환으로 stack 유지
        dst = append(dst, r)
    }
    return dst
}

type Result struct {
    Score float64
    Label string
}

type Data struct {
    Value float64
}

func processOne(d *Data) Result {
    return Result{Score: d.Value * 1.5, Label: "ok"}
}
```

**Step 5 — 트레이드오프 & 대안**

| 기법 | 장점 | 단점 | 적용 시점 |
|------|------|------|-----------|
| 값 반환 (no pointer) | Stack 유지, GC 무관 | 큰 struct 복사 비용 | struct < 128B |
| `sync.Pool` | 반복 alloc 제거 | GC 2사이클 후 회수, pool miss 시 new 호출 | 고빈도 단명 객체 |
| 고정 배열 `[N]byte` | 확정적 stack 할당 | 크기 초과 시 panic 또는 fallback 필요 | 크기 상한이 명확한 버퍼 |
| `arena` (실험적) | batch alloc/free | Go 1.20 실험적, API 불안정 | 대량 임시 객체 (request-scoped) |
| Prealloc 슬라이스 | append 재할당 방지 | 과다 예약 시 메모리 낭비 | 크기 예측 가능한 슬라이스 |

**Step 6 — 성장 & 심화 학습**

- Go 컴파일러 소스의 `cmd/compile/internal/escape` 패키지를 읽으면 escape analysis 로직을 직접 확인할 수 있다
- `go test -bench -benchmem`의 `allocs/op` 메트릭을 CI에 통합하여 allocation regression을 자동 감지하는 것이 Staff-level practice
- Go 1.22의 PGO(Profile-Guided Optimization)를 활용하면 컴파일러가 hot path의 inlining과 escape decision을 더 공격적으로 최적화한다

**🎯 면접관 평가 기준:**
- **L6 PASS**: escape 조건 5가지 이상 정확히 열거, `-gcflags='-m'` 사용 경험, stack vs heap 성능 차이를 정량적으로 설명, sync.Pool이나 값 반환 등 최소 2가지 최적화 패턴 제시
- **L7 EXCEED**: 컴파일러 내부의 escape graph 구축 과정 설명, PGO와의 상호작용, arena 실험적 기능 언급, 실제 프로덕션에서 allocation profiling으로 P99 latency를 개선한 사례 공유, inlining budget과 escape analysis의 관계 설명
- **🚩 RED FLAG**: "포인터 쓰면 heap" 정도의 피상적 답변, `-gcflags` 사용 경험 없음, stack과 heap 성능 차이를 설명 못함, GC와의 연관성 미언급

---

### Q16: pprof 프로파일링과 프로덕션 성능 디버깅

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Performance Engineering

**Question:**
"Go 서비스의 프로덕션 환경에서 성능 문제를 진단하는 전체 워크플로를 설명하세요. `pprof`의 CPU/Memory/Goroutine/Block/Mutex 프로파일 각각이 무엇을 측정하고, 어떤 상황에서 어떤 프로파일을 봐야 하는지 구분하세요. `go tool trace`와의 차이점, 그리고 continuous profiling을 프로덕션에 적용할 때의 오버헤드와 아키텍처도 논해주세요."

---

**🧒 12살 비유:**
병원에서 건강 검진받는 것과 비슷해. X-ray(CPU profile)는 뼈 구조를 보여주고, 혈액검사(Memory profile)는 몸 안에 뭐가 쌓여있는지 보여주고, 심전도(trace)는 심장이 뛰는 타이밍을 정밀하게 보여줘. 어디가 아픈지에 따라 다른 검사를 해야 하고, 건강한 사람도 정기 검진(continuous profiling)을 받으면 문제를 일찍 발견할 수 있어.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

프로덕션 성능 문제를 체계적으로 진단하는 능력은 Staff Engineer의 핵심 역량이다. 면접관은 (1) 각 프로파일 타입의 정확한 동작 원리, (2) 증상에서 원인으로 연결하는 논리적 사고, (3) 프로덕션 환경에서의 안전한 프로파일링 경험을 평가한다. 단순히 "pprof 써봤다"가 아니라 언제, 왜, 어떤 프로파일을 선택하는지의 판단력이 핵심이다.

**Step 2 — 핵심 기술 설명**

Go의 프로파일링 생태계는 크게 `runtime/pprof`(샘플링 기반 프로파일러)와 `runtime/trace`(이벤트 기반 트레이서) 두 축으로 구성된다.

**pprof 프로파일 타입별 동작 원리:**

| 프로파일 | 측정 대상 | 샘플링 방식 | 언제 사용하는가 |
|----------|-----------|------------|-----------------|
| **CPU** | 함수별 CPU 시간 점유율 | SIGPROF 시그널, 기본 10ms 간격 | CPU 사용률 높을 때 (top, htop에서 Go 프로세스 점유율 확인) |
| **Heap (alloc_space)** | 누적 메모리 할당량 | `runtime.MemProfile` 기록, 512KB당 1회 샘플링 | 메모리 사용량 증가, GC 부하 높을 때 |
| **Heap (inuse_space)** | 현재 사용 중인 메모리 | 위와 동일, live objects만 필터 | 메모리 누수 의심 시 |
| **Goroutine** | 모든 goroutine의 현재 stack trace | 전수 조사 (샘플링 아님) | goroutine 누수, 데드락 의심 시 |
| **Block** | 동기화 프리미티브에서의 대기 시간 | `runtime.SetBlockProfileRate` | 채널/뮤텍스 contention 의심 시 |
| **Mutex** | 뮤텍스 contention 시간 | `runtime.SetMutexProfileFraction` | 뮤텍스 경합이 병목일 때 |
| **Threadcreate** | OS 스레드 생성 위치 | 전수 기록 | cgo로 인한 스레드 폭증 시 |

```go
package main

import (
    "log"
    "net/http"
    _ "net/http/pprof" // 자동 핸들러 등록
    "runtime"
)

func main() {
    // Block/Mutex 프로파일링 활성화 (기본 비활성)
    runtime.SetBlockProfileRate(1)      // 모든 blocking event 기록
    runtime.SetMutexProfileFraction(5)  // 1/5 확률로 mutex contention 기록

    // pprof HTTP 엔드포인트 노출
    go func() {
        log.Println(http.ListenAndServe("localhost:6060", nil))
    }()

    // 애플리케이션 로직...
    runServer()
}

func runServer() {
    // 실제 서비스 로직
    select {}
}
```

```bash
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

go tool pprof http://localhost:6060/debug/pprof/heap

curl http://localhost:6060/debug/pprof/goroutine?debug=2

(pprof) top 20          # 상위 20개 함수
(pprof) list funcName   # 소스 코드 라인별 프로파일
(pprof) web             # 호출 그래프 SVG 생성
(pprof) peek funcName   # caller/callee 관계
```

**pprof vs trace 차이:**

`pprof`는 "어디서 시간/메모리를 많이 쓰는가"에 대한 통계적 답변을 제공한다. 반면 `go tool trace`는 "언제, 어떤 순서로, 어떤 P/M/G에서 실행되었는가"라는 시간축 기반의 정밀한 이벤트 기록을 제공한다.

```go
import "runtime/trace"

func captureTrace() {
    f, _ := os.Create("trace.out")
    defer f.Close()
    trace.Start(f)
    defer trace.Stop()
    // ... 측정 대상 코드
}
```

```bash
go tool trace trace.out
```

**Step 3 — 다양한 관점**

성능 진단의 체계적 워크플로:

```
[증상 관찰] → [가설 수립] → [프로파일 선택] → [데이터 수집] → [분석] → [수정] → [검증]
     ↑                                                                          |
     └──────────────────────────────────────────────────────────────────────────┘
```

| 증상 | 1차 확인 | 사용할 프로파일 |
|------|----------|-----------------|
| CPU 사용률 100% | `top`, GOMAXPROCS | CPU profile |
| 메모리 지속 증가 | `runtime.ReadMemStats` | Heap (inuse_space) |
| GC pause 높음 | `GODEBUG=gctrace=1` | Heap (alloc_space) + trace |
| 요청 latency spike | P99 메트릭 | trace + block profile |
| goroutine 수 증가 | `/debug/pprof/goroutine?debug=1` | Goroutine profile |
| 처리량(throughput) 저하 | RPS 메트릭 | Mutex + CPU profile |

**Step 4 — 구체적 예시: Continuous Profiling 아키텍처**

```go
package profiling

import (
    "context"
    "runtime/pprof"
    "os"
    "time"
)

// ContinuousProfiler는 프로덕션에서 주기적으로 프로파일을 수집한다.
// 오버헤드: CPU ~1-2%, Memory ~5MB 추가
type ContinuousProfiler struct {
    interval   time.Duration
    duration   time.Duration
    uploadFunc func(profileType string, data []byte) error
}

func NewContinuousProfiler(
    interval, duration time.Duration,
    upload func(string, []byte) error,
) *ContinuousProfiler {
    return &ContinuousProfiler{
        interval:   interval, // e.g., 60s
        duration:   duration, // e.g., 10s
        uploadFunc: upload,
    }
}

func (cp *ContinuousProfiler) Run(ctx context.Context) {
    ticker := time.NewTicker(cp.interval)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            cp.collectAndUpload("cpu")
            cp.collectAndUpload("heap")
        }
    }
}

func (cp *ContinuousProfiler) collectAndUpload(profileType string) {
    f, err := os.CreateTemp("", "profile-*.pb.gz")
    if err != nil {
        return
    }
    defer os.Remove(f.Name())
    defer f.Close()

    switch profileType {
    case "cpu":
        if err := pprof.StartCPUProfile(f); err != nil {
            return
        }
        time.Sleep(cp.duration)
        pprof.StopCPUProfile()
    case "heap":
        if err := pprof.WriteHeapProfile(f); err != nil {
            return
        }
    }

    data, _ := os.ReadFile(f.Name())
    _ = cp.uploadFunc(profileType, data) // 중앙 저장소(Pyroscope, Parca 등)로 업로드
}
```

**Step 5 — 트레이드오프 & 대안**

| 도구 | 오버헤드 | 정밀도 | 프로덕션 안전성 | 용도 |
|------|---------|--------|-----------------|------|
| `pprof` CPU | ~1-2% | 통계적 (10ms 샘플링) | 안전 | 함수별 CPU 소비 분석 |
| `pprof` Heap | ~0.5% | 통계적 (512KB당 1회) | 안전 | 메모리 할당 패턴 |
| `go tool trace` | ~5-10% | 이벤트 단위 정밀 | 짧은 기간만 | 스케줄러, goroutine 상호작용 |
| `GODEBUG=gctrace=1` | 무시 가능 | GC 사이클 단위 | 안전 | GC 튜닝 |
| Pyroscope/Parca | ~2-3% | 통계적 | 안전 (continuous) | 시계열 프로파일 비교 |
| Datadog Profiler | ~2-4% | 통계적 | 안전 (continuous) | APM 통합 분석 |
| `fgprof` (felixge) | ~3-5% | wall-clock 기반 | 주의 필요 | off-CPU 시간 포함 분석 |

**Step 6 — 성장 & 심화 학습**

- Go 1.21+의 PGO는 pprof CPU 프로파일을 `default.pgo`로 저장하면 빌드 시 자동 적용된다. Continuous profiling 데이터를 PGO 피드백 루프에 연결하면 프로덕션 워크로드에 최적화된 바이너리를 자동 생성할 수 있다
- `runtime/metrics` 패키지 (Go 1.16+)는 `runtime.ReadMemStats`보다 세분화된 메트릭을 제공하며, `/gc/cycles/total:gc-cycles`나 `/sched/goroutines:goroutines` 같은 표준 메트릭을 Prometheus로 내보낼 수 있다
- Linux의 `perf`와 Go의 pprof를 결합하면 커널-레벨 syscall overhead까지 포함한 full-stack 프로파일링이 가능하다

**🎯 면접관 평가 기준:**
- **L6 PASS**: 5가지 이상 프로파일 타입을 정확히 구분, 증상별 적절한 프로파일 선택 능력, pprof HTTP endpoint 설정과 기본 명령어 숙지, pprof와 trace의 차이 설명
- **L7 EXCEED**: continuous profiling 아키텍처 설계 경험, PGO 피드백 루프 언급, off-CPU profiling(fgprof) 개념 이해, 프로덕션에서 실제 P99 latency를 프로파일링으로 개선한 구체적 사례, 샘플링 rate 조정에 따른 오버헤드-정밀도 트레이드오프 정량적 설명
- **🚩 RED FLAG**: pprof 사용 경험 없음, CPU 프로파일만 알고 나머지 프로파일 타입 구분 못함, 프로덕션에서의 오버헤드 고려 없이 "trace 돌리면 됩니다", goroutine 프로파일과 goroutine leak 연결 못함

---

### Q17: 벤치마크 방법론과 성능 테스트 함정

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Performance Engineering

**Question:**
"Go의 `testing.B` 벤치마크를 정확하게 작성하는 방법론과 흔히 빠지는 함정(pitfall)들을 설명하세요. 컴파일러 최적화가 벤치마크 결과를 왜곡하는 사례, `b.ResetTimer()`와 `b.StopTimer()`의 올바른 사용법, 그리고 `-benchmem`, `-count`, `-benchtime`의 의미를 논하세요. Sub-benchmark와 테이블 드리븐 벤치마크의 차이, 그리고 benchstat으로 통계적 유의성을 검증하는 방법도 포함해주세요."

---

**🧒 12살 비유:**
100미터 달리기 기록을 잴 때, 바람 방향(컴파일러 최적화)이 기록을 바꿀 수 있어. 심판(벤치마크)이 정확하려면: (1) 준비운동 시간은 빼야 하고(ResetTimer), (2) 바람이 등 뒤에서 불어서 빠르게 보이는 건 진짜 실력이 아니고(dead code elimination), (3) 한 번만 뛰면 운이 좋았을 수도 있으니 여러 번 뛰어서(count) 평균을 내야 해. 그리고 기록이 정말 좋아졌는지는 통계적으로(benchstat) 확인해야 해.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

잘못된 벤치마크로 잘못된 결론을 도출하면 아키텍처 결정을 그르치게 된다. 면접관은 (1) 벤치마크의 통계적 엄밀성에 대한 인식, (2) Go 컴파일러 최적화를 이해하고 벤치마크 왜곡을 방지하는 능력, (3) 성능 변경의 유의성을 검증하는 방법론을 평가한다. L6+ 엔지니어는 "빠르다/느리다"가 아닌 "통계적으로 유의미하게 3.2% 개선되었다 (p<0.05)"라고 말해야 한다.

**Step 2 — 핵심 기술 설명**

Go의 벤치마크 프레임워크(`testing.B`)는 내부적으로 b.N을 자동 조정하여 안정적인 측정 시간(기본 1초)을 확보한다. 하지만 이 자동화가 정확한 결과를 보장하지는 않는다.

**핵심 함정 1: 컴파일러 Dead Code Elimination**

```go
// BAD: 컴파일러가 결과를 사용하지 않으므로 연산 자체를 제거할 수 있음
func BenchmarkBad(b *testing.B) {
    for i := 0; i < b.N; i++ {
        computeHash("input") // 반환값 미사용 → 컴파일러가 호출 제거 가능
    }
}

// GOOD: 결과를 패키지 레벨 변수에 저장하여 제거 방지
var sink any // 패키지 레벨 sink

func BenchmarkGood(b *testing.B) {
    var result []byte
    for i := 0; i < b.N; i++ {
        result = computeHash("input")
    }
    sink = result // 컴파일러가 loop를 제거하지 못하게 함
}

func computeHash(input string) []byte {
    // hash 연산
    return []byte(input)
}
```

Go 1.21+에서는 `testing.B.Loop()` 패턴을 사용할 수도 있지만, sink 패턴이 가장 보편적이고 안전하다.

**핵심 함정 2: Timer 제어**

```go
func BenchmarkWithSetup(b *testing.B) {
    // 비용이 큰 셋업
    data := generateLargeDataset(1_000_000)

    b.ResetTimer() // 셋업 시간 제외

    for i := 0; i < b.N; i++ {
        process(data)
    }
}

func BenchmarkWithPerIterSetup(b *testing.B) {
    for i := 0; i < b.N; i++ {
        data := generateSmallDataset(100)

        b.StopTimer()  // 주의: StopTimer/StartTimer는 오버헤드가 큼
        cleanup(data)
        b.StartTimer()

        // StopTimer/StartTimer를 루프 안에서 쓰면
        // 그 자체의 오버헤드가 결과를 왜곡할 수 있음
        // → 가능하면 셋업을 루프 밖으로 빼는 것이 좋음
    }
}

func generateLargeDataset(n int) []int { return make([]int, n) }
func generateSmallDataset(n int) []int { return make([]int, n) }
func process(data []int)               {}
func cleanup(data []int)               {}
```

**핵심 함정 3: Sub-benchmark와 Table-Driven**

```go
func BenchmarkSort(b *testing.B) {
    sizes := []int{100, 1_000, 10_000, 100_000}
    for _, size := range sizes {
        b.Run(fmt.Sprintf("size=%d", size), func(b *testing.B) {
            // 각 sub-benchmark는 독립적인 b.N을 가짐
            data := generateRandomSlice(size)
            b.ResetTimer()
            for i := 0; i < b.N; i++ {
                // 주의: 원본 데이터 변형 방지를 위해 매 이터레이션마다 복사
                copied := make([]int, len(data))
                copy(copied, data)
                sort.Ints(copied)
            }
        })
    }
}

func generateRandomSlice(n int) []int {
    s := make([]int, n)
    for i := range s {
        s[i] = n - i
    }
    return s
}
```

**Step 3 — 다양한 관점: 벤치마크 실행과 분석**

```bash
go test -bench=. -benchmem ./...

go test -bench=BenchmarkSort -count=10 -benchtime=2s ./... | tee old.txt

go test -bench=BenchmarkSort -count=10 -benchtime=2s ./... | tee new.txt

benchstat old.txt new.txt
```

benchstat 출력 예시:
```
name          old time/op    new time/op    delta
Sort/size=100    1.25µs ± 2%    1.18µs ± 3%   -5.60%  (p=0.001 n=10+10)
Sort/size=1000   18.3µs ± 1%    15.1µs ± 2%  -17.49%  (p=0.000 n=10+10)

name          old alloc/op   new alloc/op   delta
Sort/size=100      896B ± 0%      896B ± 0%     ~     (p=1.000 n=10+10)
Sort/size=1000    8.19kB ± 0%    8.19kB ± 0%     ~     (p=1.000 n=10+10)
```

핵심 해석:
- `± N%`: 변동 계수 — 5% 이하가 안정적
- `p=0.001`: p-value — 0.05 미만이면 통계적으로 유의미
- `n=10+10`: 유효 샘플 수 — outlier 제거 후 실제 사용된 수

**Step 4 — 구체적 예시: 프로덕션 벤치마크 패턴**

```go
package encoding_test

import (
    "encoding/json"
    "testing"

    "google.golang.org/protobuf/proto"
)

// 실전 패턴: 직렬화 포맷 비교 벤치마크
type Message struct {
    ID        int64    `json:"id"`
    Type      string   `json:"type"`
    Payload   string   `json:"payload"`
    Tags      []string `json:"tags"`
    Timestamp int64    `json:"timestamp"`
}

var benchMessage = Message{
    ID:        12345,
    Type:      "event",
    Payload:   "benchmark test payload data for serialization comparison",
    Tags:      []string{"perf", "test", "benchmark"},
    Timestamp: 1700000000,
}

func BenchmarkMarshal(b *testing.B) {
    b.Run("JSON", func(b *testing.B) {
        var result []byte
        var err error
        b.ReportAllocs()
        for i := 0; i < b.N; i++ {
            result, err = json.Marshal(&benchMessage)
            if err != nil {
                b.Fatal(err)
            }
        }
        sink = result
    })

    // protobuf 예시 (구조 비교 목적)
    b.Run("JSON/Prealloc", func(b *testing.B) {
        buf := make([]byte, 0, 256)
        b.ReportAllocs()
        b.ResetTimer()
        for i := 0; i < b.N; i++ {
            buf = buf[:0]
            var err error
            buf, err = appendJSON(buf, &benchMessage)
            if err != nil {
                b.Fatal(err)
            }
        }
        sink = buf
    })
}

func appendJSON(buf []byte, msg *Message) ([]byte, error) {
    data, err := json.Marshal(msg)
    if err != nil {
        return nil, err
    }
    return append(buf, data...), nil
}

// Allocation 집중 벤치마크: allocs/op로 regression 감지
func BenchmarkAllocs(b *testing.B) {
    b.Run("WithAlloc", func(b *testing.B) {
        b.ReportAllocs()
        for i := 0; i < b.N; i++ {
            s := make([]int, 100)
            _ = process2(s)
        }
    })

    b.Run("WithPool", func(b *testing.B) {
        b.ReportAllocs()
        for i := 0; i < b.N; i++ {
            s := getFromPool()
            _ = process2(s)
            putToPool(s)
        }
    })
}

func process2(s []int) int { return len(s) }

// dummy pool functions
var pool = make(chan []int, 100)

func getFromPool() []int {
    select {
    case s := <-pool:
        return s[:0]
    default:
        return make([]int, 0, 100)
    }
}

func putToPool(s []int) {
    select {
    case pool <- s:
    default:
    }
}

var _ = proto.Marshal // suppress unused import
```

**Step 5 — 트레이드오프 & 대안**

| 함정 | 증상 | 해결 |
|------|------|------|
| Dead code elimination | 비정상적으로 빠른 결과 (0 ns/op) | 패키지 레벨 sink 변수 사용 |
| 셋업 시간 포함 | 일관되지 않은 결과 | `b.ResetTimer()` 사용 |
| 루프 내 StopTimer | 타이머 오버헤드가 결과 왜곡 | 셋업을 루프 밖으로 이동 |
| 단일 실행 | 분산이 큰 결과 | `-count=10` 이상 + benchstat |
| 입력 데이터 변형 | 첫 이터레이션만 정확 | 매 이터레이션 복사 또는 immutable 입력 |
| GC 간섭 | 불규칙한 spike | `GOGC=off` 비교 또는 `-benchtime=5s` |
| CPU frequency scaling | 환경에 따른 결과 변동 | `cpupower frequency-set -g performance` |
| 캐시 효과 | 현실과 다른 결과 | 다양한 입력 크기로 테스트 |

**Step 6 — 성장 & 심화 학습**

- Go 1.24의 `b.Loop()` 메서드는 sink 패턴 없이도 dead code elimination을 방지하는 내장 메커니즘을 제공하므로 주시할 가치가 있다
- CI에 `benchstat` 비교를 통합하여 PR별 성능 regression을 자동 감지하는 파이프라인을 구축하는 것이 Staff-level practice. `golang.org/x/perf/cmd/benchstat`와 GitHub Actions를 결합한다
- `perflock`(Linux)으로 CPU frequency를 고정하면 벤치마크 재현성이 크게 향상된다

**🎯 면접관 평가 기준:**
- **L6 PASS**: dead code elimination 함정 인지 및 sink 패턴 사용, ResetTimer/StopTimer 올바른 사용, `-benchmem -count` 플래그 이해, sub-benchmark 작성 능력
- **L7 EXCEED**: benchstat 사용한 통계적 유의성 검증 경험, CI 벤치마크 regression 자동 감지 파이프라인 설계, GC/CPU frequency 등 외부 요인 통제 방법 설명, 마이크로벤치마크 한계 인지(실제 워크로드와의 차이), PGO와의 연계
- **🚩 RED FLAG**: sink 패턴 모름, 벤치마크 한 번 돌리고 결론 도출, benchstat이나 통계적 검증 개념 없음, StopTimer를 루프 안에서 무분별하게 사용

---

## 7. sync Primitives

### Q18: Mutex vs RWMutex 심층 분석과 Lock 설계 원칙

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: sync Primitives

**Question:**
"Go의 `sync.Mutex`와 `sync.RWMutex`의 내부 구현 차이, starvation 방지 메커니즘(Go 1.9+), 그리고 RWMutex가 오히려 Mutex보다 성능이 나쁜 시나리오를 설명하세요. Lock granularity 설계 원칙, lock-free 대안(atomic)과의 trade-off, 그리고 대규모 시스템에서의 mutex contention 패턴 분석 방법을 논해주세요."

---

**🧒 12살 비유:**
도서관 열람실에 비유해볼게. 일반 자물쇠(Mutex)는 한 사람만 들어갈 수 있어 — 읽든 쓰든 혼자만 가능해. 특수 자물쇠(RWMutex)는 여러 명이 동시에 책을 읽을 수 있지만, 누군가 책에 메모를 쓰려면 다른 사람 모두 나가야 해. 근데 이 특수 자물쇠가 항상 좋은 건 아니야 — 사람이 적으면 자물쇠를 여닫는 복잡한 절차 자체가 시간 낭비야. 그리고 자물쇠 없이 쪽지(atomic)를 교환하는 방법도 있는데, 간단한 것만 가능하고 복잡한 작업에는 안 맞아.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

동시성 프리미티브 선택은 시스템의 throughput과 correctness를 직접 결정한다. 면접관은 (1) 내부 구현에 대한 깊은 이해, (2) 상황별 올바른 프리미티브 선택 능력, (3) contention을 진단하고 해결한 실전 경험을 평가한다. "읽기가 많으면 RWMutex"라는 단순 규칙을 넘어, 언제 그 규칙이 깨지는지를 아는 것이 Staff-level이다.

**Step 2 — 핵심 기술 설명**

**Mutex 내부 구현 (Go 1.9+ starvation mode):**

Go의 Mutex는 두 가지 모드로 동작한다:
1. **Normal mode**: Lock을 요청한 goroutine이 짧은 시간 spinning(busy-wait)을 시도한다. lock이 곧 풀리면 OS 스케줄러를 거치지 않고 즉시 획득할 수 있어 빠르다.
2. **Starvation mode**: 한 goroutine이 1ms 이상 lock을 기다리면 starvation mode로 전환된다. 이 모드에서는 lock이 FIFO 순서로 대기 중인 goroutine에 직접 전달되어 공정성이 보장된다.

```go
// sync.Mutex의 핵심 필드 (단순화)
type Mutex struct {
    state int32 // locked, woken, starving 비트 + waiter 수
    sema  uint32 // OS semaphore
}

// state 비트 레이아웃:
// [waiterCount (29 bits)] [starving (1 bit)] [woken (1 bit)] [locked (1 bit)]
```

**RWMutex 내부:**

```go
// sync.RWMutex (단순화)
type RWMutex struct {
    w           Mutex        // writer간 상호 배제
    writerSem   uint32       // writer 대기 세마포어
    readerSem   uint32       // reader 대기 세마포어
    readerCount atomic.Int32 // 활성 reader 수 (음수 = writer 대기 중)
    readerWait  atomic.Int32 // writer 이전에 시작된 reader 수
}
```

Writer가 Lock()을 호출하면:
1. `w.Lock()`으로 다른 writer 차단
2. `readerCount`를 음수로 설정 (새 reader 차단)
3. 기존 reader가 모두 `RUnlock()` 할 때까지 `writerSem` 대기

**RWMutex가 Mutex보다 느린 시나리오:**

```go
package lockbench

import (
    "sync"
    "sync/atomic"
    "testing"
)

type MutexMap struct {
    mu sync.Mutex
    m  map[string]int
}

type RWMutexMap struct {
    mu sync.RWMutex
    m  map[string]int
}

// 시나리오: 쓰기 비율 50% — RWMutex가 Mutex보다 느림
// RWMutex의 RLock/RUnlock은 내부적으로 atomic 연산 2회 + reader/writer 조율 비용이 있음
// 쓰기가 잦으면 이 추가 비용이 동시 읽기 이점을 상쇄함

func BenchmarkMutex_50Write(b *testing.B) {
    m := &MutexMap{m: map[string]int{"key": 0}}
    b.RunParallel(func(pb *testing.PB) {
        i := 0
        for pb.Next() {
            if i%2 == 0 {
                m.mu.Lock()
                m.m["key"]++
                m.mu.Unlock()
            } else {
                m.mu.Lock()
                _ = m.m["key"]
                m.mu.Unlock()
            }
            i++
        }
    })
}

func BenchmarkRWMutex_50Write(b *testing.B) {
    m := &RWMutexMap{m: map[string]int{"key": 0}}
    b.RunParallel(func(pb *testing.PB) {
        i := 0
        for pb.Next() {
            if i%2 == 0 {
                m.mu.Lock()
                m.m["key"]++
                m.mu.Unlock()
            } else {
                m.mu.RLock()
                _ = m.m["key"]
                m.mu.RUnlock()
            }
            i++
        }
    })
}

// 규칙: 읽기 비율 90% 이상 + contention이 높을 때만 RWMutex가 유리
// 읽기 비율 낮거나 contention 낮으면 Mutex가 단순하고 빠름
```

**Step 3 — 다양한 관점**

| 관점 | Mutex | RWMutex | atomic |
|------|-------|---------|--------|
| **Lock 비용** | 낮음 (CAS 1회) | 높음 (atomic 2회 + 조율) | 최소 (단일 CAS) |
| **공정성** | Starvation mode로 보장 | Writer 우선 (Go 구현) | N/A |
| **읽기 동시성** | 불가 | 가능 | 가능 |
| **적합 읽기:쓰기** | 어떤 비율이든 | 90%+ 읽기 | 단순 값 (counter, flag) |
| **디버깅** | 단순 | 복잡 (reader/writer 교착) | 매우 어려움 |
| **Cache line** | 1 cache line | 여러 cache line | 1 cache line |

**Lock granularity 설계 원칙:**

```go
// Anti-pattern: 하나의 큰 lock (coarse-grained)
type BadCache struct {
    mu    sync.Mutex
    users map[string]*User
    items map[string]*Item
    // users 접근이 items를 차단
}

// Good: 세분화된 lock (fine-grained)
type GoodCache struct {
    users struct {
        mu sync.RWMutex
        m  map[string]*User
    }
    items struct {
        mu sync.RWMutex
        m  map[string]*Item
    }
}

// Better: Sharded lock (초고빈도 접근 시)
type ShardedMap struct {
    shards [256]struct {
        mu sync.RWMutex
        m  map[string]any
    }
}

func (sm *ShardedMap) getShard(key string) *struct {
    mu sync.RWMutex
    m  map[string]any
} {
    h := fnv32(key)
    return &sm.shards[h%256]
}

func fnv32(key string) uint32 {
    hash := uint32(2166136261)
    for i := 0; i < len(key); i++ {
        hash *= 16777619
        hash ^= uint32(key[i])
    }
    return hash
}

type User struct{ Name string }
type Item struct{ ID string }
```

**Step 4 — 구체적 예시: Contention 진단과 해결**

```go
package main

import (
    "fmt"
    "runtime"
    "sync"
    "sync/atomic"
    "time"
)

// 프로덕션 패턴: adaptive lock — contention 정도에 따라 전략 변경
type AdaptiveCounter struct {
    // Phase 1: atomic (contention 낮을 때)
    fast atomic.Int64

    // Phase 2: sharded counters (contention 높을 때)
    shards    []atomic.Int64
    shardMask int64

    // 모드 전환
    mode atomic.Int32 // 0=fast, 1=sharded
}

func NewAdaptiveCounter() *AdaptiveCounter {
    nShards := runtime.GOMAXPROCS(0) * 4 // CPU 수의 4배
    // 2의 거듭제곱으로 반올림
    shardCount := 1
    for shardCount < nShards {
        shardCount <<= 1
    }
    return &AdaptiveCounter{
        shards:    make([]atomic.Int64, shardCount),
        shardMask: int64(shardCount - 1),
    }
}

func (c *AdaptiveCounter) Inc() {
    if c.mode.Load() == 0 {
        c.fast.Add(1)
        return
    }
    // goroutine ID 기반 shard 선택 (실제로는 P ID가 더 좋음)
    // runtime_procPin()은 내부 API이므로 대안 사용
    shard := runtime_fastrand() & uint32(c.shardMask)
    c.shards[shard].Add(1)
}

func (c *AdaptiveCounter) Value() int64 {
    if c.mode.Load() == 0 {
        return c.fast.Load()
    }
    var total int64
    total += c.fast.Load()
    for i := range c.shards {
        total += c.shards[i].Load()
    }
    return total
}

// SwitchToSharded는 contention이 높다고 판단될 때 호출
func (c *AdaptiveCounter) SwitchToSharded() {
    c.mode.Store(1)
}

//go:linkname runtime_fastrand runtime.fastrand
func runtime_fastrand() uint32

func main() {
    c := NewAdaptiveCounter()
    c.SwitchToSharded()

    var wg sync.WaitGroup
    start := time.Now()

    for g := 0; g < 16; g++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for i := 0; i < 1_000_000; i++ {
                c.Inc()
            }
        }()
    }

    wg.Wait()
    fmt.Printf("Count: %d, Duration: %v\n", c.Value(), time.Since(start))
}
```

**Step 5 — 트레이드오프 & 대안**

| 프리미티브 | 최적 사용처 | 피해야 할 상황 | 대안 |
|-----------|------------|--------------|------|
| `sync.Mutex` | 범용, 쓰기 빈번, 단순한 critical section | N/A (기본 선택) | channel (CSP 패턴) |
| `sync.RWMutex` | 읽기 90%+, contention 높은 경우 | 쓰기 빈번, contention 낮은 경우 | `sync.Map` (읽기 위주 + 키 안정) |
| `atomic` | 단일 값 (counter, flag, pointer) | 복합 연산 (check-then-act) | Mutex |
| `sync.Map` | 읽기 위주 + 키 집합 안정적 | 키가 자주 변하는 경우 | Sharded map |
| Channel | 소유권 전달, pipeline | 공유 상태 보호 (성능 오버헤드) | Mutex |
| Sharded lock | 초고빈도 접근, cache line contention | 복잡도 부담 가능한 경우만 | `sync.Map` |

**Step 6 — 성장 & 심화 학습**

- `go tool pprof`의 mutex profile(`runtime.SetMutexProfileFraction`)을 활용하면 어느 mutex에서 가장 많은 contention이 발생하는지 정량적으로 파악할 수 있다
- Go 런타임 소스 `src/sync/mutex.go`의 `lockSlow()` 함수를 읽으면 spinning, starvation mode 전환의 정확한 조건을 이해할 수 있다
- false sharing(같은 cache line의 다른 데이터를 여러 코어가 동시 수정)이 mutex contention과 결합되면 성능이 급격히 저하되므로, struct padding(`_ [64]byte`)으로 cache line을 분리하는 기법도 중요하다

**🎯 면접관 평가 기준:**
- **L6 PASS**: Mutex와 RWMutex의 구조적 차이 설명, starvation mode 언급, RWMutex가 불리한 시나리오 제시, lock granularity 개념 이해, atomic과의 트레이드오프 설명
- **L7 EXCEED**: Mutex 내부 state 비트 레이아웃 설명, sharded lock 구현 경험, cache line contention과 false sharing 연관 설명, mutex profile로 contention 진단한 실제 사례, adaptive locking 전략
- **🚩 RED FLAG**: "읽기가 많으면 무조건 RWMutex" 단순 규칙만 앎, starvation 개념 모름, lock contention 진단 경험 없음, atomic과 mutex 사용 기준 구분 못함

---

### Q19: sync.Pool의 GC 상호작용과 올바른 사용법

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: sync Primitives

**Question:**
"Go의 `sync.Pool`이 GC와 어떻게 상호작용하는지, 내부적으로 per-P private/shared 구조가 어떻게 동작하는지 설명하세요. `sync.Pool`을 사용해야 하는 정확한 시나리오와 사용하면 안 되는 시나리오를 구분하고, Go 1.13+에서 도입된 victim cache 메커니즘이 성능에 미치는 영향도 논해주세요."

---

**🧒 12살 비유:**
학교 미술 시간에 물감 팔레트(Pool)가 있어. 그림을 다 그리면 팔레트를 돌려놓고, 다음 학생이 재사용해. 근데 방학(GC)이 되면 선생님이 팔레트를 치워(clear). Go 1.13 이후에는 "지난 학기 팔레트"를 창고(victim cache)에 한 학기 더 보관해서, 새 학기에 바로 쓸 수 있게 해줘. 하지만 팔레트에 이름표를 붙여서 "내 것"이라고 주장하면 안 돼(Pool은 소유권을 보장하지 않음).

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

`sync.Pool`은 올바르게 사용하면 GC 부하를 극적으로 줄이지만, 잘못 사용하면 데이터 레이스, 메모리 누수, 또는 오히려 성능 저하를 일으킨다. 면접관은 (1) Pool의 내부 동작 원리, (2) GC와의 상호작용 메커니즘, (3) 올바른/잘못된 사용 패턴 구분 능력을 평가한다. 이 질문은 Go 런타임에 대한 깊은 이해를 요구하므로 L6/L7 차별화에 효과적이다.

**Step 2 — 핵심 기술 설명**

**내부 구조 (Go 1.13+):**

```
sync.Pool 내부 구조:

┌──────────────────────────────────────────┐
│              sync.Pool                    │
│                                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │   P0    │  │   P1    │  │   P2    │  │  ← per-P 로컬 풀
│  │ private │  │ private │  │ private │  │     (lock-free)
│  │ shared  │  │ shared  │  │ shared  │  │
│  │ (list)  │  │ (list)  │  │ (list)  │  │
│  └─────────┘  └─────────┘  └─────────┘  │
│                                           │
│  ┌────────────────────────────────────┐   │
│  │         victim cache              │   │  ← 이전 GC 사이클의 데이터
│  │  (이전 primary가 여기로 이동)       │   │     (Go 1.13+)
│  └────────────────────────────────────┘   │
└──────────────────────────────────────────┘
```

동작 과정:
1. **Get()**: 현재 P의 private 슬롯 확인 → shared 리스트 확인 → 다른 P의 shared steal → victim cache 확인 → New() 호출
2. **Put()**: 현재 P의 private 슬롯에 저장 (비어있으면) → shared 리스트에 추가
3. **GC 시**: primary pool → victim cache로 이동, 이전 victim cache는 삭제

```go
// Pool의 Get 경로 (단순화)
func (p *Pool) Get() any {
    // 1. 현재 P에 pin (preemption 방지)
    l := p.pin()

    // 2. private 슬롯 (lock-free, 가장 빠름)
    x := l.private
    l.private = nil
    if x != nil {
        return x
    }

    // 3. 현재 P의 shared 리스트 (lock-free pop)
    x = l.shared.popHead()
    if x != nil {
        return x
    }

    // 4. 다른 P의 shared 리스트 steal
    x = p.getSlow()
    if x != nil {
        return x
    }

    // 5. victim cache
    x = p.getFromVictim()
    if x != nil {
        return x
    }

    // 6. New 호출
    if p.New != nil {
        return p.New()
    }
    return nil
}
```

**Victim cache (Go 1.13+)의 효과:**

Go 1.12까지는 매 GC마다 Pool이 완전히 비워져서 GC 직후 cold start 문제가 심했다. Go 1.13+에서는 이전 Pool 데이터가 victim cache로 이동하여 2번의 GC 사이클 동안 유지된다. 이로 인해:
- GC 직후에도 Pool miss가 줄어든다
- 할당 burst가 완화된다
- 단, 메모리 사용량은 약간 증가한다 (2 사이클분 보존)

**Step 3 — 다양한 관점**

| 사용해야 하는 경우 | 사용하면 안 되는 경우 |
|-------------------|---------------------|
| 고빈도 단명 객체 (HTTP 요청당 버퍼) | 장시간 유지가 필요한 객체 (DB connection) |
| 생성 비용이 높은 객체 (큰 byte 슬라이스) | 상태를 가지고 재사용되면 위험한 객체 |
| GC 부하가 P99 latency에 영향을 줄 때 | Pool에서 꺼낸 객체의 lifetime을 추적해야 할 때 |
| 처리량(throughput) 최대화가 목표일 때 | 정확한 capacity 제어가 필요할 때 |
| fmt/encoding/json 내부 (표준 라이브러리 사례) | 캐시 용도 (GC가 비울 수 있으므로) |

**Step 4 — 구체적 예시**

```go
package pool

import (
    "bytes"
    "sync"
)

// 올바른 사용: byte buffer pool
var bufferPool = sync.Pool{
    New: func() any {
        return bytes.NewBuffer(make([]byte, 0, 4096))
    },
}

// 안전한 Get/Put 패턴
func ProcessRequest(data []byte) []byte {
    buf := bufferPool.Get().(*bytes.Buffer)
    buf.Reset() // 핵심: 반드시 초기화 후 사용!
    defer bufferPool.Put(buf)

    // buf 사용
    buf.Write([]byte("processed: "))
    buf.Write(data)

    // 결과 복사 후 반환 (buf는 Pool로 돌아가므로)
    result := make([]byte, buf.Len())
    copy(result, buf.Bytes())
    return result
}

// Anti-pattern 1: Pool 객체의 참조를 유지
func BadUsage() *bytes.Buffer {
    buf := bufferPool.Get().(*bytes.Buffer)
    buf.Reset()
    buf.WriteString("data")
    // BAD: Pool에 반환하지 않고 포인터를 외부로 노출
    // → 다른 goroutine이 같은 buf를 Get할 수 있음
    return buf
}

// Anti-pattern 2: 너무 큰 객체를 Pool에 반환
var largePool = sync.Pool{
    New: func() any {
        return make([]byte, 0, 1024)
    },
}

func ProcessLarge(size int) []byte {
    buf := largePool.Get().([]byte)
    buf = buf[:0]

    if cap(buf) < size {
        buf = make([]byte, size)
    } else {
        buf = buf[:size]
    }

    // 작업 수행...

    // GOOD: 비정상적으로 커진 버퍼는 Pool에 반환하지 않음
    if cap(buf) > 1024*1024 { // 1MB 초과
        return buf // Pool에 반환하지 않고 GC에 맡김
    }

    result := make([]byte, len(buf))
    copy(result, buf)
    largePool.Put(buf[:0])
    return result
}

// 프로덕션 패턴: Pool 사용 효과 측정
type PoolMetrics struct {
    hits   atomic.Int64
    misses atomic.Int64
}

var metrics PoolMetrics

var monitoredPool = sync.Pool{
    New: func() any {
        metrics.misses.Add(1) // New 호출 = cache miss
        return make([]byte, 0, 4096)
    },
}

func GetMonitored() []byte {
    v := monitoredPool.Get().([]byte)
    metrics.hits.Add(1) // Get 호출 = hit (New에서 이미 miss 카운트)
    return v[:0]
}

// 실제 hit rate = (hits - misses) / hits
```

```go
// 표준 라이브러리의 sync.Pool 사용 사례: fmt 패키지
// src/fmt/print.go에서 pp(printer) 구조체를 Pool로 관리
//
// var ppFree = sync.Pool{
//     New: func() any { return new(pp) },
// }
//
// func newPrinter() *pp {
//     p := ppFree.Get().(*pp)
//     p.panicking = false
//     p.erroring = false
//     p.wrapErrs = false
//     p.fmt.init(&p.buf)
//     return p
// }
```

**Step 5 — 트레이드오프 & 대안**

| 방식 | GC 영향 | Capacity 제어 | Thread Safety | 적합 시나리오 |
|------|---------|---------------|---------------|---------------|
| `sync.Pool` | GC가 비움 (2 cycle) | 불가 | 내장 | 단명 버퍼, 임시 객체 |
| Buffered channel | GC 무관 (참조 유지) | 채널 크기로 제어 | 내장 | 제한된 자원 풀 (DB conn) |
| Free list (linked) | GC 무관 | 수동 제어 | Mutex 필요 | 특수한 메모리 관리 |
| `arena` (실험적) | batch free | 수동 | 제한적 | request-scoped 대량 할당 |
| Object 재사용 없음 | 매번 GC 대상 | N/A | N/A | 생성 비용 낮은 객체 |

**Step 6 — 성장 & 심화 학습**

- Go 런타임 소스 `src/sync/pool.go`를 읽으면 `poolLocal`, `poolChain`(lock-free deque), victim cache의 정확한 구현을 확인할 수 있다
- `runtime.ReadMemStats`의 `Frees`와 `Mallocs` 차이를 모니터링하여 Pool이 실제로 allocation을 얼마나 줄이는지 정량적으로 측정할 수 있다
- Go 1.19+의 `runtime/debug.SetMemoryLimit`과 Pool의 상호작용을 이해하면, soft memory limit 환경에서 Pool이 메모리를 과도하게 보유하는 문제를 예방할 수 있다

**🎯 면접관 평가 기준:**
- **L6 PASS**: per-P 구조 설명, GC 시 Pool이 비워지는 동작 이해, victim cache 개념 설명, Reset() 필수성 인지, 올바른/잘못된 사용 사례 각 2개 이상 제시
- **L7 EXCEED**: private/shared/steal 경로의 성능 차이 설명, victim cache가 해결한 cold start 문제 구체적 설명, 표준 라이브러리(fmt, encoding/json)의 Pool 사용 사례 언급, Pool miss rate 모니터링 구현 경험, 버퍼 크기 제한 패턴(oversize 반환 방지)
- **🚩 RED FLAG**: Pool을 캐시로 사용 (GC가 비울 수 있음을 모름), Get 후 Reset 없이 사용, Pool 객체의 참조를 외부에 노출, connection pool 용도로 sync.Pool 제안

---

### Q20: sync.Map, errgroup, 그리고 동시성 패턴 조합

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: sync Primitives

**Question:**
"Go의 `sync.Map`이 일반 `map + Mutex`보다 유리한 정확한 조건, 내부의 read/dirty 이중 맵 구조, 그리고 miss 누적 시 promotion 메커니즘을 설명하세요. 또한 `golang.org/x/sync/errgroup`과 `sync.WaitGroup`의 차이, errgroup의 context 취소 전파, 그리고 이들을 조합하여 fan-out/fan-in, pipeline, bounded parallelism 같은 동시성 패턴을 구현하는 방법을 논해주세요."

---

**🧒 12살 비유:**
`sync.Map`은 도서관의 "자주 읽는 책 코너"(read map)와 "신간 코너"(dirty map)가 분리된 구조야. 자주 읽는 책은 카운터에서 바로 꺼내고, 신간을 찾으려면 잠금장치를 열어야 해. 신간을 너무 자주 찾으면 사서가 "이제 이것도 자주 읽는 코너에 넣자"(promotion) 하고 옮겨. `errgroup`은 친구들에게 숙제를 나눠주는데, 한 명이라도 틀리면 "다들 멈춰!" 하고 알려주는 반장이야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

실제 프로덕션 시스템에서는 단일 프리미티브가 아닌 여러 동시성 도구를 조합해야 한다. 면접관은 (1) `sync.Map`의 내부 구현과 정확한 사용 조건, (2) errgroup을 활용한 구조화된 동시성 패턴, (3) 복합 동시성 패턴의 설계 및 구현 능력을 평가한다. "sync.Map은 concurrent-safe map"이라는 수준을 넘어, 왜 특정 워크로드에서만 유리한지의 구조적 이유를 설명해야 한다.

**Step 2 — 핵심 기술 설명**

**sync.Map 내부 구조:**

```go
// sync.Map 내부 (단순화)
type Map struct {
    mu     Mutex
    read   atomic.Pointer[readOnly] // lock-free 읽기 전용 맵
    dirty  map[any]*entry           // mutex로 보호되는 쓰기 맵
    misses int                      // read에서 miss된 횟수
}

type readOnly struct {
    m       map[any]*entry
    amended bool // dirty에 read에 없는 키가 있는가?
}

type entry struct {
    p atomic.Pointer[any] // nil, expunged, 또는 실제 값
}
```

동작 메커니즘:

```
[Load 경로]
read map에서 검색 (lock-free, atomic)
  ├─ 발견 → 반환 (빠름)
  └─ 미발견 + amended=true
      └─ mu.Lock() → dirty에서 검색 → misses++
          └─ misses >= len(dirty) → dirty를 read로 promotion

[Store 경로]
read map에서 키 존재 확인
  ├─ 존재 → entry.p를 atomic swap (lock-free)
  └─ 미존재
      └─ mu.Lock() → dirty에 저장

[Delete 경로]
read map에서 키 존재 확인
  ├─ 존재 → entry.p를 nil로 atomic swap
  └─ 미존재 + amended=true
      └─ mu.Lock() → dirty에서 삭제
```

**sync.Map이 유리한 조건 (공식 문서 기준):**
1. 키가 한 번 쓰여지고 이후 읽기만 되는 경우 (config, routing table)
2. 여러 goroutine이 겹치지 않는 키 집합을 읽고 쓰는 경우 (per-goroutine cache)

불리한 경우: 키가 빈번하게 추가/삭제되면 dirty→read promotion이 자주 발생하여 `map + RWMutex`보다 느림.

```go
package main

import (
    "context"
    "errors"
    "fmt"
    "net/http"
    "sync"
    "time"

    "golang.org/x/sync/errgroup"
)

// ===== errgroup vs WaitGroup =====

// WaitGroup: 에러 전파 없음, context 통합 없음
func fetchAllWaitGroup(urls []string) []string {
    var mu sync.Mutex
    results := make([]string, 0, len(urls))
    var wg sync.WaitGroup

    for _, url := range urls {
        wg.Add(1)
        go func(u string) {
            defer wg.Done()
            resp, err := http.Get(u)
            if err != nil {
                return // 에러를 어떻게 전파하지?
            }
            defer resp.Body.Close()
            mu.Lock()
            results = append(results, u)
            mu.Unlock()
        }(url)
    }

    wg.Wait()
    return results
}

// errgroup: 에러 전파 + context 취소 + 깔끔한 인터페이스
func fetchAllErrgroup(ctx context.Context, urls []string) ([]string, error) {
    g, ctx := errgroup.WithContext(ctx)
    results := make([]string, len(urls))

    for i, url := range urls {
        i, url := i, url // Go 1.22+에서는 루프 변수 캡처 문제 해결됨
        g.Go(func() error {
            req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
            if err != nil {
                return fmt.Errorf("request %s: %w", url, err)
            }
            resp, err := http.DefaultClient.Do(req)
            if err != nil {
                return fmt.Errorf("fetch %s: %w", url, err)
            }
            defer resp.Body.Close()

            if resp.StatusCode != 200 {
                return fmt.Errorf("fetch %s: status %d", url, resp.StatusCode)
            }
            results[i] = url // 인덱스 기반이므로 mutex 불필요
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        return nil, err // 첫 번째 에러 반환, context 자동 취소
    }
    return results, nil
}
```

**Step 3 — 다양한 관점: 동시성 패턴 조합**

```go
// 패턴 1: Bounded Parallelism (동시 실행 수 제한)
func processItems(ctx context.Context, items []Item, maxConcurrency int) error {
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(maxConcurrency) // Go 1.20+ errgroup.SetLimit

    for _, item := range items {
        item := item
        g.Go(func() error {
            select {
            case <-ctx.Done():
                return ctx.Err()
            default:
                return processItem(ctx, item)
            }
        })
    }

    return g.Wait()
}

// 패턴 2: Fan-out/Fan-in with errgroup
func fanOutFanIn(ctx context.Context, input []Data) ([]Result, error) {
    g, ctx := errgroup.WithContext(ctx)
    resultCh := make(chan Result, len(input))

    // Fan-out: 각 입력에 대해 goroutine 실행
    for _, d := range input {
        d := d
        g.Go(func() error {
            r, err := transform(ctx, d)
            if err != nil {
                return err
            }
            select {
            case resultCh <- r:
                return nil
            case <-ctx.Done():
                return ctx.Err()
            }
        })
    }

    // Fan-in: 별도 goroutine에서 결과 수집
    var results []Result
    var collectErr error
    done := make(chan struct{})

    go func() {
        defer close(done)
        for r := range resultCh {
            results = append(results, r)
        }
    }()

    // 모든 producer 완료 대기
    if err := g.Wait(); err != nil {
        collectErr = err
    }
    close(resultCh)
    <-done

    if collectErr != nil {
        return nil, collectErr
    }
    return results, nil
}

// 패턴 3: Pipeline with stages
func pipeline(ctx context.Context, input []int) ([]int, error) {
    // Stage 1: Generate
    stage1 := make(chan int, 100)
    g, ctx := errgroup.WithContext(ctx)

    g.Go(func() error {
        defer close(stage1)
        for _, v := range input {
            select {
            case stage1 <- v:
            case <-ctx.Done():
                return ctx.Err()
            }
        }
        return nil
    })

    // Stage 2: Transform (multiple workers)
    stage2 := make(chan int, 100)
    const numWorkers = 4

    for w := 0; w < numWorkers; w++ {
        g.Go(func() error {
            for v := range stage1 {
                select {
                case stage2 <- v * 2:
                case <-ctx.Done():
                    return ctx.Err()
                }
            }
            return nil
        })
    }

    // Close stage2 after all workers done
    go func() {
        g.Wait() // 여기서는 별도 errgroup 분리가 더 정확하지만 단순화
        close(stage2)
    }()

    // Stage 3: Collect
    var results []int
    for v := range stage2 {
        results = append(results, v)
    }

    return results, g.Wait()
}

type Item struct{ ID int }
type Data struct{ Value int }
type Result struct{ Score int }

func processItem(ctx context.Context, item Item) error { return nil }
func transform(ctx context.Context, d Data) (Result, error) {
    return Result{Score: d.Value}, nil
}
```

**Step 4 — 구체적 예시: sync.Map 실전 패턴**

```go
package registry

import (
    "sync"
    "sync/atomic"
)

// 실전 패턴: Service Registry (키 집합이 안정적인 경우)
// 서비스는 시작 시 등록되고, 이후 읽기 위주로 사용됨 → sync.Map 최적
type ServiceRegistry struct {
    services sync.Map // map[string]*ServiceInfo
    count    atomic.Int64
}

type ServiceInfo struct {
    Address  string
    Port     int
    Healthy  atomic.Bool // 상태는 atomic으로 업데이트
    Metadata map[string]string
}

func (r *ServiceRegistry) Register(name string, info *ServiceInfo) {
    if _, loaded := r.services.LoadOrStore(name, info); !loaded {
        r.count.Add(1)
    }
}

func (r *ServiceRegistry) Lookup(name string) (*ServiceInfo, bool) {
    v, ok := r.services.Load(name)
    if !ok {
        return nil, false
    }
    return v.(*ServiceInfo), true
}

func (r *ServiceRegistry) UpdateHealth(name string, healthy bool) {
    if v, ok := r.services.Load(name); ok {
        v.(*ServiceInfo).Healthy.Store(healthy)
    }
}

// Range는 snapshot이 아님 — 순회 중 변경이 반영될 수 있음
func (r *ServiceRegistry) HealthyServices() []*ServiceInfo {
    var healthy []*ServiceInfo
    r.services.Range(func(key, value any) bool {
        info := value.(*ServiceInfo)
        if info.Healthy.Load() {
            healthy = append(healthy, info)
        }
        return true // false 반환 시 순회 중단
    })
    return healthy
}

// Anti-pattern: sync.Map을 카운터로 사용
// 키가 계속 추가/삭제되면 dirty→read promotion이 빈번하게 발생
// → sharded map + Mutex가 더 효율적
type BadUsage struct {
    counters sync.Map // map[string]*int64 — 키가 계속 늘어남 → BAD
}

// Better: 키가 고정적이라면 미리 할당
type BetterUsage struct {
    counters sync.Map // 초기화 시 모든 키 등록, 이후 값만 atomic 업데이트
}

func (b *BetterUsage) Init(keys []string) {
    for _, k := range keys {
        var counter int64
        b.counters.Store(k, &counter)
    }
}

func (b *BetterUsage) Increment(key string) {
    if v, ok := b.counters.Load(key); ok {
        atomic.AddInt64(v.(*int64), 1)
    }
}
```

**Step 5 — 트레이드오프 & 대안**

| 동시성 도구 | 최적 사용처 | 내부 비용 | 주의사항 |
|------------|-----------|-----------|---------|
| `sync.Map` | 읽기 위주, 키 안정적 | read map은 lock-free, dirty는 mutex | Range는 O(n) + 일관성 보장 안 함 |
| `map + RWMutex` | 범용, 키 추가/삭제 빈번 | 예측 가능한 성능 | 가장 단순하고 디버깅 용이 |
| `map + Mutex` | 쓰기 빈번, contention 낮음 | 최소 오버헤드 | RWMutex보다 빠를 수 있음 |
| `errgroup` | 구조화된 동시성, 에러 전파 필요 | context 생성 + goroutine 관리 | SetLimit으로 bounded parallelism |
| `WaitGroup` | 단순 fan-out, 에러 불필요 | 최소 | 에러 수집은 별도 구현 필요 |
| `semaphore.Weighted` | 가중치 기반 동시성 제어 | context 기반 대기 | errgroup.SetLimit보다 유연 |

| errgroup 패턴 | 구조 | 에러 처리 | 동시성 제어 |
|---------------|------|----------|------------|
| Fan-out/Fan-in | N goroutine → 1 collector | 첫 에러 시 context 취소 | SetLimit(N) |
| Pipeline | stage1 → stage2 → stage3 | 단계별 에러 전파 | 채널 버퍼 크기 |
| Bounded parallel | 동시 실행 수 제한 | 에러 수집 + 취소 | SetLimit |
| Scatter-gather | 병렬 요청 → 결과 합산 | 부분 실패 허용 가능 | context timeout |

**Step 6 — 성장 & 심화 학습**

- Go 런타임 소스 `src/sync/map.go`를 읽으면 `expunged` 상태의 역할 (삭제된 키가 dirty promotion 시 복사되는 것을 방지)과 `missLocked()`의 promotion 조건을 정확히 이해할 수 있다
- `golang.org/x/sync` 패키지에는 `errgroup` 외에도 `singleflight` (중복 호출 병합), `semaphore` (가중치 세마포어)가 있으며, 이들을 조합하면 cache stampede 방지나 rate-limited parallel processing 같은 고급 패턴을 구현할 수 있다
- Go 1.22의 `sync.OnceFunc`, `sync.OnceValue`, `sync.OnceValues`는 `sync.Once`의 타입 안전한 대안으로, 초기화 패턴을 더 깔끔하게 작성할 수 있다
- structured concurrency 개념 (nursery 패턴)이 Go 생태계에서 `errgroup`을 통해 어떻게 근사되는지 이해하면, 더 안전한 goroutine lifetime 관리를 설계할 수 있다

**🎯 면접관 평가 기준:**
- **L6 PASS**: sync.Map의 read/dirty 이중 구조 설명, 유리한/불리한 사용 조건 정확히 구분, errgroup과 WaitGroup의 차이 (에러 전파 + context), fan-out/fan-in 패턴 구현, bounded parallelism 구현
- **L7 EXCEED**: sync.Map의 miss→promotion 메커니즘과 expunged 상태 설명, errgroup + singleflight 조합 패턴, pipeline의 graceful shutdown 처리 (context 취소 전파), sync.Map 대신 sharded map을 선택해야 하는 조건과 벤치마크 근거, structured concurrency 개념과 Go에서의 적용
- **🚩 RED FLAG**: sync.Map을 "thread-safe map" 정도로만 이해, 내부 구조(read/dirty) 설명 못함, errgroup 사용 경험 없이 WaitGroup + channel만 사용, context 취소 전파 누락, goroutine leak 가능성 미고려

---

## 8. Production Patterns


> 대상: FAANG L6/L7 (Staff/Principal Engineer)
> 총 문항: 6개 (Q21~Q26) | 난이도: ⭐⭐⭐⭐⭐
> 버전: Go 1.22+

## 목차

- [8. Production Patterns](#8-production-patterns)
- [9. Testing Strategies](#9-testing-strategies)
- [10. Module System & Build](#10-module-system--build)

---

## 8. Production Patterns

### Q21: Graceful Shutdown과 Health Check 설계

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Production Patterns

**Question:**
"Go로 작성된 프로덕션 마이크로서비스에서 graceful shutdown을 구현할 때, OS 시그널 처리부터 in-flight 요청 드레인, 백그라운드 goroutine 정리까지 전체 lifecycle을 설계하세요. Kubernetes 환경에서 liveness/readiness/startup probe가 각각 어떤 시점에 어떤 상태를 반환해야 하는지, 그리고 preStop hook과의 상호작용까지 포함하여 설명하세요."

---

**🧒 12살 비유:**
레스토랑을 폐점한다고 생각해 봐. 갑자기 문을 닫으면 음식을 먹고 있는 손님이 쫓겨나겠지? 좋은 방법은 (1) 새 손님 입장을 막고(readiness=false), (2) 이미 앉아 있는 손님은 식사를 마치게 하고(in-flight drain), (3) 주방을 정리하고(background cleanup), (4) 마지막으로 문을 잠그는(OS 프로세스 종료) 거야. Kubernetes는 "이 레스토랑 열었어?"(startup), "주문 받을 수 있어?"(readiness), "아직 살아있어?"(liveness)를 각각 따로 물어봐.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

Staff 레벨에서는 단순히 `os.Signal`을 받아서 `server.Shutdown()`을 호출하는 수준을 넘어, Kubernetes의 Pod termination lifecycle과 Go 프로세스의 shutdown 순서를 정확히 동기화할 수 있는지를 평가한다. 실제 프로덕션에서 graceful shutdown을 잘못 구현하면 배포 시마다 5xx 에러가 스파이크 치는 문제가 발생한다. 평가 포인트: (1) OS signal과 context 전파의 정확한 이해, (2) Kubernetes probe 3종의 의미론적 차이, (3) 순서 의존성(ordering)이 있는 리소스 정리 전략.

**Step 2 — 핵심 기술 설명**

Go의 graceful shutdown은 `signal.NotifyContext` (Go 1.16+)를 중심으로 설계한다. 핵심은 shutdown을 계층적으로 전파하는 것이다.

Shutdown 시퀀스:
1. SIGTERM 수신 → root context cancel
2. Health endpoint가 readiness=false 반환 (새 트래픽 차단)
3. `http.Server.Shutdown(ctx)` 호출 — in-flight 요청 완료 대기
4. gRPC `GracefulStop()` 호출
5. 메시지 consumer 정지 (Kafka consumer group leave)
6. 백그라운드 worker goroutine 드레인 (`errgroup` 또는 `sync.WaitGroup`)
7. DB connection pool 닫기, Redis 연결 닫기
8. Flush: 로그 버퍼, 메트릭 버퍼, trace exporter
9. 프로세스 종료

Kubernetes Pod Termination과의 상호작용:
- Kubernetes는 SIGTERM 전송 후 `terminationGracePeriodSeconds`(기본 30초) 대기
- 그 전에 preStop hook이 실행됨 — 여기서 `sleep 5`를 넣어 kube-proxy/iptables 업데이트 시간을 확보
- preStop 완료 후 SIGTERM 전송 (Go 프로세스가 받음)
- 타임아웃 초과 시 SIGKILL

```go
package main

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"sync/atomic"
	"syscall"
	"time"

	"golang.org/x/sync/errgroup"
)

type Server struct {
	httpServer  *http.Server
	isReady     atomic.Bool
	isAlive     atomic.Bool
	shutdownCh  chan struct{}
}

func NewServer() *Server {
	s := &Server{
		shutdownCh: make(chan struct{}),
	}
	s.isAlive.Store(true)

	mux := http.NewServeMux()

	// Health probes — 각각의 의미론이 다르다
	mux.HandleFunc("GET /healthz", s.livenessHandler)   // 프로세스 살아있는가
	mux.HandleFunc("GET /readyz", s.readinessHandler)    // 트래픽 받을 준비 됐는가
	mux.HandleFunc("GET /startupz", s.startupHandler)    // 초기화 완료됐는가

	// Business endpoints
	mux.HandleFunc("GET /api/v1/orders", s.ordersHandler)

	s.httpServer = &http.Server{
		Addr:              ":8080",
		Handler:           mux,
		ReadHeaderTimeout: 10 * time.Second,
		IdleTimeout:       120 * time.Second,
	}
	return s
}

func (s *Server) livenessHandler(w http.ResponseWriter, r *http.Request) {
	if !s.isAlive.Load() {
		w.WriteHeader(http.StatusServiceUnavailable)
		return
	}
	w.WriteHeader(http.StatusOK)
	fmt.Fprintln(w, "alive")
}

func (s *Server) readinessHandler(w http.ResponseWriter, r *http.Request) {
	if !s.isReady.Load() {
		w.WriteHeader(http.StatusServiceUnavailable)
		return
	}
	w.WriteHeader(http.StatusOK)
	fmt.Fprintln(w, "ready")
}

func (s *Server) startupHandler(w http.ResponseWriter, r *http.Request) {
	if !s.isReady.Load() {
		w.WriteHeader(http.StatusServiceUnavailable)
		return
	}
	w.WriteHeader(http.StatusOK)
	fmt.Fprintln(w, "started")
}

func (s *Server) ordersHandler(w http.ResponseWriter, r *http.Request) {
	// 실제 비즈니스 로직 — context를 통해 shutdown 인지
	select {
	case <-r.Context().Done():
		http.Error(w, "request cancelled", http.StatusServiceUnavailable)
		return
	case <-time.After(100 * time.Millisecond): // simulate work
		fmt.Fprintln(w, `{"orders": []}`)
	}
}

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelInfo,
	}))
	slog.SetDefault(logger)

	// 1. Signal context — SIGTERM, SIGINT 수신 시 cancel
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGTERM, syscall.SIGINT)
	defer stop()

	srv := NewServer()
	g, gCtx := errgroup.WithContext(ctx)

	// 2. HTTP 서버 시작
	g.Go(func() error {
		slog.Info("starting HTTP server", "addr", srv.httpServer.Addr)
		srv.isReady.Store(true)
		if err := srv.httpServer.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			return fmt.Errorf("http server error: %w", err)
		}
		return nil
	})

	// 3. 백그라운드 워커 (예: 메트릭 수집)
	g.Go(func() error {
		ticker := time.NewTicker(30 * time.Second)
		defer ticker.Stop()
		for {
			select {
			case <-gCtx.Done():
				slog.Info("background worker shutting down")
				return nil
			case <-ticker.C:
				slog.Info("collecting metrics")
			}
		}
	})

	// 4. Graceful shutdown orchestrator
	g.Go(func() error {
		<-gCtx.Done() // SIGTERM 수신 대기
		slog.Info("shutdown signal received, starting graceful shutdown")

		// Phase 1: readiness를 false로 — 새 트래픽 차단
		srv.isReady.Store(false)
		slog.Info("readiness probe set to false")

		// Phase 2: 약간 대기 — kube-proxy가 endpoints를 업데이트할 시간
		// preStop hook에서 처리할 수도 있지만 방어적으로 여기서도 대기
		time.Sleep(3 * time.Second)

		// Phase 3: HTTP 서버 shutdown (in-flight 요청 드레인)
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
		defer cancel()

		if err := srv.httpServer.Shutdown(shutdownCtx); err != nil {
			slog.Error("http server shutdown error", "error", err)
			return err
		}
		slog.Info("http server shutdown complete")

		// Phase 4: 추가 리소스 정리 (DB, Redis, Kafka 등)
		// db.Close(), redisClient.Close(), consumer.Close() ...

		// Phase 5: Flush exporters
		// traceExporter.Shutdown(shutdownCtx)
		// meterProvider.Shutdown(shutdownCtx)

		return nil
	})

	if err := g.Wait(); err != nil {
		slog.Error("server exited with error", "error", err)
		os.Exit(1)
	}
	slog.Info("server exited gracefully")
}
```

Kubernetes manifest에서의 probe 설정:

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      terminationGracePeriodSeconds: 45  # 서버 shutdown timeout + 여유
      containers:
      - name: app
        lifecycle:
          preStop:
            exec:
              command: ["sh", "-c", "sleep 5"]  # iptables 업데이트 대기
        startupProbe:
          httpGet:
            path: /startupz
            port: 8080
          failureThreshold: 30    # 최대 150초 대기 (느린 초기화 허용)
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 0  # startupProbe 이후 시작
          periodSeconds: 10
          failureThreshold: 3     # 3번 실패 시 컨테이너 재시작
        readinessProbe:
          httpGet:
            path: /readyz
            port: 8080
          periodSeconds: 5
          failureThreshold: 1     # 1번 실패 시 즉시 endpoints에서 제거
```

**Step 3 — 다양한 관점**

| 관점 | 고려 사항 |
|------|-----------|
| **네트워크** | preStop sleep 없이 SIGTERM 즉시 처리하면, kube-proxy가 아직 endpoints를 업데이트하지 않아서 새 요청이 이미 shutdown 중인 Pod로 라우팅됨 |
| **데이터 일관성** | 트랜잭션 중간에 shutdown되면 DB 롤백은 되지만, 분산 시스템에서 SAGA 보상이 필요할 수 있음 |
| **관찰 가능성** | shutdown 과정의 각 phase를 로깅하지 않으면 배포 시 발생하는 간헐적 에러를 디버깅할 수 없음 |
| **테스트** | integration test에서 `syscall.Kill(pid, syscall.SIGTERM)`을 보내고 모든 in-flight 요청이 정상 완료되는지 검증해야 함 |
| **장기 실행 작업** | WebSocket이나 streaming gRPC는 `Shutdown()`으로 드레인되지 않을 수 있어 별도의 draining 로직 필요 |

**Step 4 — 구체적 예시: Configuration 전략과 DI**

프로덕션에서는 graceful shutdown과 함께 configuration과 DI가 lifecycle에 통합되어야 한다. Google Wire(컴파일 타임 DI)와 Uber fx(런타임 DI)의 선택:

```go
// uber/fx를 사용한 lifecycle 통합 예시
package main

import (
	"context"
	"database/sql"
	"log/slog"
	"net/http"
	"time"

	"go.uber.org/fx"
)

// Config — 환경 변수 기반 설정 (12-Factor)
type Config struct {
	HTTPAddr        string        `env:"HTTP_ADDR" envDefault:":8080"`
	DBConnString    string        `env:"DATABASE_URL,required"`
	ShutdownTimeout time.Duration `env:"SHUTDOWN_TIMEOUT" envDefault:"15s"`
	ReadTimeout     time.Duration `env:"READ_TIMEOUT" envDefault:"10s"`
}

func NewConfig() (*Config, error) {
	cfg := &Config{}
	// 실제로는 envconfig.Process() 또는 caarlos0/env 사용
	return cfg, nil
}

func NewDB(lc fx.Lifecycle, cfg *Config) (*sql.DB, error) {
	db, err := sql.Open("pgx", cfg.DBConnString)
	if err != nil {
		return nil, err
	}
	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(5)
	db.SetConnMaxLifetime(5 * time.Minute)

	lc.Append(fx.Hook{
		OnStart: func(ctx context.Context) error {
			return db.PingContext(ctx)
		},
		OnStop: func(ctx context.Context) error {
			slog.Info("closing database connection pool")
			return db.Close()
		},
	})
	return db, nil
}

func NewHTTPServer(lc fx.Lifecycle, cfg *Config, mux *http.ServeMux) *http.Server {
	srv := &http.Server{
		Addr:              cfg.HTTPAddr,
		Handler:           mux,
		ReadHeaderTimeout: cfg.ReadTimeout,
	}
	lc.Append(fx.Hook{
		OnStart: func(ctx context.Context) error {
			go srv.ListenAndServe()
			return nil
		},
		OnStop: func(ctx context.Context) error {
			shutdownCtx, cancel := context.WithTimeout(ctx, cfg.ShutdownTimeout)
			defer cancel()
			return srv.Shutdown(shutdownCtx)
		},
	})
	return srv
}

func main() {
	fx.New(
		fx.Provide(NewConfig, NewDB, NewHTTPServer),
		fx.Invoke(func(*http.Server) {}), // trigger construction
	).Run() // Run handles SIGTERM/SIGINT + calls OnStop in reverse order
}
```

Wire(컴파일 타임 DI)와 fx(런타임 DI) 비교:

| 차원 | Wire (Google) | fx (Uber) |
|------|--------------|-----------|
| DI 시점 | 컴파일 타임 (코드 생성) | 런타임 (reflection) |
| 타입 안전성 | 컴파일 에러로 잡힘 | 런타임 패닉 가능 |
| Lifecycle | 없음 — 직접 구현 | `fx.Lifecycle` 내장 |
| 학습 곡선 | 낮음 (함수 + injector) | 중간 (Module, Provide, Invoke) |
| 디버깅 | 생성된 코드 읽기 쉬움 | `fx.dotgraph`로 의존성 시각화 |
| 적합한 규모 | 소~중 규모 | 대규모 (100+ 컴포넌트) |
| Google/Uber 내부 | Google 표준 | Uber 표준 |

**Step 5 — 트레이드오프 & 대안**

| 전략 | 장점 | 단점 | 적합한 경우 |
|------|------|------|-------------|
| `signal.Notify` + 수동 정리 | 단순, 의존성 없음 | 정리 순서 수동 관리 | 소규모 서비스 |
| `errgroup` + context 전파 | goroutine 관리 깔끔 | DI 미포함 | 중규모 서비스 |
| `fx.Lifecycle` | 자동 역순 정리 | 런타임 DI 오버헤드 | 대규모 서비스 |
| `wire` + 수동 lifecycle | 컴파일 타임 안전 | lifecycle 직접 관리 | Google 스타일 |
| Kubernetes preStop + SIGTERM | 인프라 레벨 보장 | Go 코드와 동기화 필요 | K8s 환경 필수 |

**Step 6 — 성장 & 심화 학습**

- **공식 문서**: `net/http.Server.Shutdown` godoc — BaseContext, ConnContext 커스터마이징
- **Kubernetes 문서**: Pod Lifecycle — terminationGracePeriodSeconds와 preStop 상호작용
- **실전 블로그**: Cloudflare "Graceful upgrades in Go" — zero-downtime 배포에서의 listener 전달
- **라이브러리 소스**: `uber-go/fx` 내부의 lifecycle 구현 — DAG 기반 역순 shutdown
- **심화**: HashiCorp의 `go-plugin` — RPC 기반 plugin의 graceful shutdown 패턴

**🎯 면접관 평가 기준:**

- **L6 PASS**: `signal.NotifyContext` + `http.Server.Shutdown` + `errgroup`으로 in-flight 드레인 구현. liveness vs readiness 차이를 정확히 설명. preStop sleep의 필요성 인지.
- **L7 EXCEED**: shutdown 순서의 의존성 그래프를 설명. fx/wire 선택의 트레이드오프 분석. 장기 실행 작업(WebSocket, streaming)의 draining 전략. 실제 배포 시 발생하는 race condition(iptables 업데이트 지연) 경험 공유.
- **🚩 RED FLAG**: `os.Exit(0)` 직접 호출. in-flight 요청 무시. liveness와 readiness를 동일하게 구현. shutdown timeout 없이 무한 대기.

---

### Q22: Configuration 전략과 Feature Flag 시스템 설계

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Production Patterns

**Question:**
"대규모 Go 마이크로서비스 플릿에서 configuration을 관리하는 전략을 설계하세요. 정적 설정(env var, YAML)과 동적 설정(feature flag, remote config)의 경계, hot-reload 구현, 그리고 type-safe configuration이 왜 중요한지 코드와 함께 설명하세요. 설정 변경이 장애를 유발한 프로덕션 사례와 방지 전략도 논의하세요."

---

**🧒 12살 비유:**
게임 설정을 생각해 봐. 화면 해상도(정적 설정)는 게임을 재시작해야 바뀌지만, 음량(동적 설정)은 게임 중에도 슬라이더로 조절할 수 있어. 그런데 만약 음량 슬라이더에 "최대 100"이라는 제한이 없으면 누가 "999999"로 올려서 스피커가 터질 수 있어. 그래서 설정값에도 타입과 범위 체크(type-safe)가 필요한 거야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

Configuration은 "가장 강력한 API"다. 코드 변경 없이 시스템 동작을 바꿀 수 있기 때문에, 잘못된 설정 변경은 코드 배포보다 더 빠르게, 더 넓은 범위의 장애를 유발한다. Google의 2015년 postmortem에 따르면 장애의 약 70%가 configuration 변경에서 비롯된다. Staff 엔지니어는 설정의 lifecycle(로드 → 검증 → 적용 → 모니터링)을 안전하게 설계할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

Go에서 type-safe configuration의 핵심 원칙:
1. **구조체로 표현**: 모든 설정을 typed struct로 정의
2. **검증을 로드 시점에 집중**: 런타임에 `string → int` 변환 실패하는 것을 방지
3. **불변 snapshot**: 설정 변경 시 새 snapshot을 atomic하게 교체
4. **환경별 오버라이드**: base YAML + env var override + remote override

```go
package config

import (
	"fmt"
	"sync/atomic"
	"time"

	"github.com/go-playground/validator/v10"
)

// Config — 모든 필드에 타입과 검증 태그
type Config struct {
	Server   ServerConfig   `yaml:"server" validate:"required"`
	Database DatabaseConfig `yaml:"database" validate:"required"`
	Feature  FeatureConfig  `yaml:"feature"`
}

type ServerConfig struct {
	Port            int           `yaml:"port" env:"SERVER_PORT" validate:"min=1024,max=65535"`
	ReadTimeout     time.Duration `yaml:"readTimeout" env:"SERVER_READ_TIMEOUT" validate:"min=1s,max=60s"`
	ShutdownTimeout time.Duration `yaml:"shutdownTimeout" env:"SERVER_SHUTDOWN_TIMEOUT" validate:"min=5s,max=120s"`
}

type DatabaseConfig struct {
	Host            string        `yaml:"host" env:"DB_HOST" validate:"required,hostname|ip"`
	Port            int           `yaml:"port" env:"DB_PORT" validate:"min=1,max=65535"`
	MaxOpenConns    int           `yaml:"maxOpenConns" env:"DB_MAX_OPEN_CONNS" validate:"min=1,max=200"`
	MaxIdleConns    int           `yaml:"maxIdleConns" env:"DB_MAX_IDLE_CONNS" validate:"min=0,ltefield=MaxOpenConns"`
	ConnMaxLifetime time.Duration `yaml:"connMaxLifetime" env:"DB_CONN_MAX_LIFETIME" validate:"min=30s"`
}

type FeatureConfig struct {
	EnableNewCheckout  bool    `yaml:"enableNewCheckout" env:"FEAT_NEW_CHECKOUT"`
	SearchResultLimit  int     `yaml:"searchResultLimit" env:"FEAT_SEARCH_LIMIT" validate:"min=1,max=1000"`
	ABTestTrafficRatio float64 `yaml:"abTestTrafficRatio" env:"FEAT_AB_RATIO" validate:"min=0,max=1"`
}

// Validate — 로드 시점에 모든 제약 조건 검증
func (c *Config) Validate() error {
	v := validator.New()
	if err := v.Struct(c); err != nil {
		return fmt.Errorf("config validation failed: %w", err)
	}
	// Cross-field validation
	if c.Database.MaxIdleConns > c.Database.MaxOpenConns {
		return fmt.Errorf("maxIdleConns(%d) must be <= maxOpenConns(%d)",
			c.Database.MaxIdleConns, c.Database.MaxOpenConns)
	}
	return nil
}

// AtomicConfig — 동적 설정을 위한 atomic 래퍼
type AtomicConfig struct {
	value atomic.Pointer[Config]
}

func NewAtomicConfig(initial *Config) *AtomicConfig {
	ac := &AtomicConfig{}
	ac.value.Store(initial)
	return ac
}

func (ac *AtomicConfig) Load() *Config {
	return ac.value.Load()
}

// Update — 새 설정을 검증 후 atomic swap
func (ac *AtomicConfig) Update(newCfg *Config) error {
	if err := newCfg.Validate(); err != nil {
		return fmt.Errorf("refusing to apply invalid config: %w", err)
	}

	old := ac.value.Load()

	// Safety check: 위험한 변경 감지
	if err := detectDangerousChange(old, newCfg); err != nil {
		return fmt.Errorf("dangerous config change blocked: %w", err)
	}

	ac.value.Store(newCfg)
	return nil
}

func detectDangerousChange(old, new *Config) error {
	// MaxOpenConns가 50% 이상 감소하면 차단
	if new.Database.MaxOpenConns < old.Database.MaxOpenConns/2 {
		return fmt.Errorf("maxOpenConns dropped by >50%%: %d -> %d",
			old.Database.MaxOpenConns, new.Database.MaxOpenConns)
	}
	return nil
}
```

Feature Flag 시스템과 hot-reload:

```go
package featureflag

import (
	"context"
	"encoding/json"
	"log/slog"
	"sync/atomic"
	"time"
)

// Flag — 개별 feature flag 정의
type Flag struct {
	Key          string          `json:"key"`
	Enabled      bool            `json:"enabled"`
	Rollout      float64         `json:"rollout"`      // 0.0~1.0 점진적 롤아웃
	AllowList    []string        `json:"allowList"`     // 특정 사용자/팀에만 활성화
	Metadata     json.RawMessage `json:"metadata"`      // flag별 추가 설정
	LastModified time.Time       `json:"lastModified"`
}

// Store — feature flag 저장소 인터페이스
type Store interface {
	FetchAll(ctx context.Context) (map[string]*Flag, error)
	Watch(ctx context.Context, onChange func(map[string]*Flag)) error
}

// Evaluator — flag 평가 엔진
type Evaluator struct {
	flags atomic.Pointer[map[string]*Flag]
}

func NewEvaluator(store Store) *Evaluator {
	e := &Evaluator{}
	initial := make(map[string]*Flag)
	e.flags.Store(&initial)

	return e
}

// IsEnabled — 기본 on/off 평가
func (e *Evaluator) IsEnabled(key string) bool {
	flags := *e.flags.Load()
	f, ok := flags[key]
	if !ok {
		return false // unknown flag = disabled (fail-closed)
	}
	return f.Enabled
}

// IsEnabledForUser — 사용자별 점진적 롤아웃
func (e *Evaluator) IsEnabledForUser(key, userID string) bool {
	flags := *e.flags.Load()
	f, ok := flags[key]
	if !ok {
		return false
	}
	if !f.Enabled {
		return false
	}

	// AllowList 우선 체크
	for _, allowed := range f.AllowList {
		if allowed == userID {
			return true
		}
	}

	// 해시 기반 consistent rollout (동일 유저는 항상 같은 결과)
	hash := fnvHash(key + ":" + userID)
	bucket := float64(hash%1000) / 1000.0
	return bucket < f.Rollout
}

func fnvHash(s string) uint32 {
	h := uint32(2166136261)
	for i := 0; i < len(s); i++ {
		h ^= uint32(s[i])
		h *= 16777619
	}
	return h
}

// StartPolling — 주기적 폴링 기반 hot-reload
func (e *Evaluator) StartPolling(ctx context.Context, store Store, interval time.Duration) {
	go func() {
		ticker := time.NewTicker(interval)
		defer ticker.Stop()

		for {
			select {
			case <-ctx.Done():
				return
			case <-ticker.C:
				flags, err := store.FetchAll(ctx)
				if err != nil {
					slog.Error("failed to fetch feature flags", "error", err)
					continue // 실패 시 기존 값 유지 (stale > crash)
				}
				e.flags.Store(&flags)
				slog.Debug("feature flags updated", "count", len(flags))
			}
		}
	}()
}
```

**Step 3 — 다양한 관점**

| 관점 | 분석 |
|------|------|
| **안전성** | 설정 변경은 "코드 없는 배포"다. canary rollout 없이 전체 플릿에 적용되므로, percentage-based rollout이나 flag guard가 필수 |
| **관찰 가능성** | 모든 설정 변경에 audit log 남겨야 함. "누가, 언제, 무엇을 바꿨는지" 추적 불가능하면 장애 원인 파악 불가 |
| **성능** | `atomic.Pointer`는 읽기 경로에서 lock-free — 매 HTTP 요청마다 flag를 체크해도 성능 영향 0에 수렴 |
| **일관성** | 폴링 방식은 최대 interval만큼 지연. 즉시성이 필요하면 gRPC streaming이나 etcd watch 사용 |
| **테스트** | flag 조합 폭발 문제 — `n`개 flag가 있으면 `2^n` 경로. critical path만 테스트하고 나머지는 모니터링으로 커버 |

**Step 4 — 구체적 예시: 장애 사례**

```
사례: MaxOpenConns를 200 → 5로 변경하는 설정이 전체 플릿에 동시 적용
결과: connection pool 고갈 → 모든 DB 쿼리 timeout → 전체 서비스 장애
원인: 설정 변경에 대한 safety check 없음 + canary 없음
방지:
  1. detectDangerousChange() — 50% 이상 감소 차단
  2. 설정 변경도 canary deployment (10% → 50% → 100%)
  3. 자동 롤백: 설정 적용 후 error rate 급증 시 이전 값 복원
```

**Step 5 — 트레이드오프 & 대안**

| 방식 | 장점 | 단점 | 적합한 경우 |
|------|------|------|-------------|
| Env var only | 단순, 12-Factor 준수 | 재시작 필요, 타입 없음 | 소규모, 변경 드문 설정 |
| YAML + env override | 구조적, 기본값 관리 | 재시작 필요 | 중규모 서비스 |
| etcd/Consul watch | 실시간, 중앙 관리 | 인프라 의존성 추가 | 대규모 플릿 |
| LaunchDarkly 등 SaaS | 기능 풍부, UI 제공 | 비용, 외부 의존성 | Feature flag 전문 |
| ConfigMap + sidecar | K8s 네이티브 | 갱신 지연(kubelet sync) | K8s 환경 |

**Step 6 — 성장 & 심화 학습**

- **Google SRE Book**: Chapter 14 "Managing Incidents" — configuration 변경 장애 사례
- **`caarlos0/env`**: Go의 env var → struct 매핑 라이브러리 소스 코드
- **`spf13/viper`**: Go의 설정 관리 스위스 아미 나이프 — watch, remote config 지원
- **OpenFeature**: vendor-neutral feature flag SDK 표준 — Go SDK 구현체 분석
- **논문**: "An Empirical Study of Configuration Changes and Their Impact" — ICSE 2020

**🎯 면접관 평가 기준:**

- **L6 PASS**: type-safe config struct + validation. env var와 file 기반 설정의 조합. `atomic.Pointer`를 사용한 hot-reload. feature flag의 consistent hashing 기반 rollout.
- **L7 EXCEED**: 설정 변경으로 인한 장애 사례와 방지 전략(dangerous change detection, canary config). 설정의 observability(audit log, metric). flag 조합 폭발 문제와 테스트 전략. Wire vs fx의 아키텍처적 트레이드오프.
- **🚩 RED FLAG**: `os.Getenv()`를 호출 코드 곳곳에 흩뿌림. 설정 검증 없이 런타임에 파싱. `sync.Mutex`로 설정 읽기 보호(성능 문제). feature flag를 if-else 체인으로 하드코딩.

---

## 9. Testing Strategies

### Q23: Table-Driven Tests와 Race Detector 활용 전략

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Testing Strategies

**Question:**
"Go의 table-driven test 패턴이 왜 다른 언어의 테스트 패턴보다 강력한지 설명하고, subtests(`t.Run`)과 결합하여 대규모 코드베이스에서 테스트를 구조화하는 전략을 보여주세요. 또한 `-race` 플래그의 내부 동작 원리(ThreadSanitizer), CI에서의 활용 전략, 그리고 race condition을 감지하기 어려운 edge case를 구체적 코드와 함께 설명하세요."

---

**🧒 12살 비유:**
수학 시험지를 생각해 봐. 선생님이 같은 유형의 문제를 하나씩 따로 만드는 대신, 표에 "입력-정답" 쌍을 쭉 나열해서 한 번에 채점하는 거야(table-driven). 그리고 race detector는 학교 CCTV 같은 거야 — 두 학생이 동시에 같은 사물함을 열려고 하면 알려줘. 평소에는 문제가 안 생겨도, 한 번이라도 동시에 열리면 "위험!"이라고 경고해 주는 거지.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

Go의 테스트 철학은 "프레임워크 없이 표준 라이브러리로 충분하다"이다. Staff 엔지니어는 이 철학을 이해하고 대규모 코드베이스에서도 일관된 테스트 패턴을 유지할 수 있어야 한다. race detector는 Go의 "killer feature"로, 다른 언어에서 몇 주간 디버깅할 data race를 CI에서 자동 감지한다. 면접관은 (1) 테스트 구조화 능력, (2) concurrency 버그에 대한 깊이 있는 이해, (3) CI/CD 파이프라인에서의 실전 활용을 평가한다.

**Step 2 — 핵심 기술 설명**

Table-driven test의 핵심 장점은 **테스트 로직과 테스트 데이터의 분리**다. 새 케이스 추가가 O(1) — 테이블에 한 줄만 추가하면 된다.

```go
package orderservice

import (
	"context"
	"errors"
	"testing"
	"time"
)

type OrderStatus string

const (
	StatusPending   OrderStatus = "PENDING"
	StatusConfirmed OrderStatus = "CONFIRMED"
	StatusShipped   OrderStatus = "SHIPPED"
	StatusCancelled OrderStatus = "CANCELLED"
)

type Order struct {
	ID        string
	Status    OrderStatus
	Amount    float64
	CreatedAt time.Time
}

var (
	ErrInvalidTransition = errors.New("invalid status transition")
	ErrOrderTooOld       = errors.New("order too old to cancel")
)

func (o *Order) Transition(to OrderStatus) error {
	allowed := map[OrderStatus][]OrderStatus{
		StatusPending:   {StatusConfirmed, StatusCancelled},
		StatusConfirmed: {StatusShipped, StatusCancelled},
		StatusShipped:   {}, // terminal
		StatusCancelled: {}, // terminal
	}
	for _, s := range allowed[o.Status] {
		if s == to {
			o.Status = to
			return nil
		}
	}
	return ErrInvalidTransition
}

func TestOrderTransition(t *testing.T) {
	// table-driven: 데이터와 로직 분리
	tests := []struct {
		name     string
		from     OrderStatus
		to       OrderStatus
		wantErr  error
		wantFinal OrderStatus
	}{
		{
			name:      "pending to confirmed",
			from:      StatusPending,
			to:        StatusConfirmed,
			wantErr:   nil,
			wantFinal: StatusConfirmed,
		},
		{
			name:      "pending to cancelled",
			from:      StatusPending,
			to:        StatusCancelled,
			wantErr:   nil,
			wantFinal: StatusCancelled,
		},
		{
			name:      "confirmed to shipped",
			from:      StatusConfirmed,
			to:        StatusShipped,
			wantErr:   nil,
			wantFinal: StatusShipped,
		},
		{
			name:      "shipped cannot go back to confirmed",
			from:      StatusShipped,
			to:        StatusConfirmed,
			wantErr:   ErrInvalidTransition,
			wantFinal: StatusShipped, // 상태 변경 안 됨
		},
		{
			name:      "cancelled is terminal",
			from:      StatusCancelled,
			to:        StatusPending,
			wantErr:   ErrInvalidTransition,
			wantFinal: StatusCancelled,
		},
		{
			name:      "pending cannot skip to shipped",
			from:      StatusPending,
			to:        StatusShipped,
			wantErr:   ErrInvalidTransition,
			wantFinal: StatusPending,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// 각 subtest는 독립적 — parallel 실행 가능
			t.Parallel()

			order := &Order{
				ID:     "test-order-1",
				Status: tt.from,
			}

			err := order.Transition(tt.to)

			// Error 검증
			if !errors.Is(err, tt.wantErr) {
				t.Errorf("Transition(%s -> %s) error = %v, want %v",
					tt.from, tt.to, err, tt.wantErr)
			}

			// 최종 상태 검증
			if order.Status != tt.wantFinal {
				t.Errorf("after Transition(%s -> %s), status = %s, want %s",
					tt.from, tt.to, order.Status, tt.wantFinal)
			}
		})
	}
}

// 고급 패턴: 테스트 헬퍼 + custom assertion
func assertError(t *testing.T, got, want error) {
	t.Helper() // 실패 시 호출자 위치를 보여줌
	if !errors.Is(got, want) {
		t.Errorf("got error %v, want %v", got, want)
	}
}
```

**Race Detector 내부 동작**:

Go의 race detector는 Google의 ThreadSanitizer(TSan) v2를 기반으로 한다. 내부적으로 **happens-before** 관계를 추적한다.

작동 원리:
1. 컴파일러가 모든 메모리 접근(읽기/쓰기)에 계측 코드(instrumentation)를 삽입
2. 런타임이 각 goroutine의 **vector clock**을 유지
3. 동기화 연산(mutex, channel, atomic)은 vector clock을 동기화
4. 두 goroutine이 동일 메모리에 접근하고, 하나 이상이 쓰기이며, happens-before 관계가 없으면 → RACE 보고

```go
package counter

import (
	"sync"
	"sync/atomic"
	"testing"
)

// 🚨 Race condition이 있는 코드
type UnsafeCounter struct {
	count int
}

func (c *UnsafeCounter) Increment() {
	c.count++ // READ + MODIFY + WRITE — not atomic
}

func (c *UnsafeCounter) Get() int {
	return c.count
}

// ✅ Race-free 버전 1: Mutex
type MutexCounter struct {
	mu    sync.Mutex
	count int
}

func (c *MutexCounter) Increment() {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.count++
}

func (c *MutexCounter) Get() int {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.count
}

// ✅ Race-free 버전 2: Atomic (읽기 빈번한 경우 더 빠름)
type AtomicCounter struct {
	count atomic.Int64
}

func (c *AtomicCounter) Increment() {
	c.count.Add(1)
}

func (c *AtomicCounter) Get() int64 {
	return c.count.Load()
}

// go test -race 로 실행하면 UnsafeCounter에서 race 감지
func TestUnsafeCounter_Race(t *testing.T) {
	c := &UnsafeCounter{}
	var wg sync.WaitGroup

	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			c.Increment() // 🚨 DATA RACE — race detector가 잡음
		}()
	}
	wg.Wait()
	// count가 1000이 아닐 수 있음 (lost update)
}

func TestAtomicCounter_NoRace(t *testing.T) {
	c := &AtomicCounter{}
	var wg sync.WaitGroup

	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			c.Increment() // ✅ race-free
		}()
	}
	wg.Wait()

	if got := c.Get(); got != 1000 {
		t.Errorf("count = %d, want 1000", got)
	}
}

// 🔥 Race detector가 잡기 어려운 edge case:
// map의 concurrent read/write — Go 1.6+에서 fatal error
func TestMapRace(t *testing.T) {
	// 이 테스트는 -race 없이도 Go 1.6+에서 fatal error
	// runtime이 concurrent map access를 직접 감지
	m := make(map[string]int)
	var wg sync.WaitGroup

	wg.Add(2)
	go func() {
		defer wg.Done()
		for i := 0; i < 100; i++ {
			m["key"] = i // write
		}
	}()
	go func() {
		defer wg.Done()
		for i := 0; i < 100; i++ {
			_ = m["key"] // read — concurrent with write → fatal
		}
	}()
	wg.Wait()
}

// 해결: sync.Map (읽기 빈번, 키가 안정적인 경우)
func TestSyncMap_NoRace(t *testing.T) {
	var m sync.Map
	var wg sync.WaitGroup

	wg.Add(2)
	go func() {
		defer wg.Done()
		for i := 0; i < 100; i++ {
			m.Store("key", i)
		}
	}()
	go func() {
		defer wg.Done()
		for i := 0; i < 100; i++ {
			m.Load("key")
		}
	}()
	wg.Wait()
}
```

**Step 3 — 다양한 관점**

| 관점 | 분석 |
|------|------|
| **CI 통합** | `-race`는 CPU 2~10x, 메모리 5~10x 오버헤드. CI에서는 unit test는 항상 `-race`, integration test는 선택적으로 적용 |
| **False negative** | race detector는 실제 실행 경로만 분석. 특정 타이밍에서만 발생하는 race는 해당 경로가 실행되지 않으면 놓침. 따라서 높은 커버리지가 중요 |
| **t.Parallel() 주의점** | 테이블의 `tt` 변수를 클로저가 캡처할 때, Go 1.22 이전에는 루프 변수 공유 문제가 있었음. Go 1.22+에서 해결 (per-iteration scope) |
| **테스트 격리** | `t.Parallel()` 사용 시 shared state가 있으면 race 발생. 각 subtest가 독립적인 데이터를 사용해야 함 |
| **벤치마크와 race** | `go test -race -bench .`는 벤치마크 결과가 왜곡됨. race 감지와 벤치마크는 분리 실행 |

**Step 4 — 구체적 예시: httptest를 활용한 통합 테스트**

```go
package handler

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

type OrderHandler struct {
	repo OrderRepository
}

type OrderRepository interface {
	GetByID(ctx context.Context, id string) (*Order, error)
	Create(ctx context.Context, order *Order) error
}

func (h *OrderHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	switch {
	case r.Method == http.MethodGet:
		h.handleGet(w, r)
	case r.Method == http.MethodPost:
		h.handleCreate(w, r)
	default:
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
	}
}

func (h *OrderHandler) handleGet(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id") // Go 1.22+ routing
	order, err := h.repo.GetByID(r.Context(), id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(order)
}

func (h *OrderHandler) handleCreate(w http.ResponseWriter, r *http.Request) {
	var order Order
	if err := json.NewDecoder(r.Body).Decode(&order); err != nil {
		http.Error(w, "invalid request body", http.StatusBadRequest)
		return
	}
	if err := h.repo.Create(r.Context(), &order); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(order)
}

// Mock repository
type mockRepo struct {
	orders map[string]*Order
	err    error
}

func (m *mockRepo) GetByID(_ context.Context, id string) (*Order, error) {
	if m.err != nil {
		return nil, m.err
	}
	o, ok := m.orders[id]
	if !ok {
		return nil, errors.New("not found")
	}
	return o, nil
}

func (m *mockRepo) Create(_ context.Context, order *Order) error {
	if m.err != nil {
		return m.err
	}
	m.orders[order.ID] = order
	return nil
}

func TestOrderHandler(t *testing.T) {
	tests := []struct {
		name       string
		method     string
		path       string
		body       string
		repo       *mockRepo
		wantStatus int
		wantBody   string
	}{
		{
			name:   "GET existing order",
			method: http.MethodGet,
			path:   "/orders/order-1",
			repo: &mockRepo{orders: map[string]*Order{
				"order-1": {ID: "order-1", Status: StatusPending, Amount: 99.99},
			}},
			wantStatus: http.StatusOK,
			wantBody:   `"order-1"`,
		},
		{
			name:       "GET non-existent order",
			method:     http.MethodGet,
			path:       "/orders/missing",
			repo:       &mockRepo{orders: map[string]*Order{}},
			wantStatus: http.StatusNotFound,
		},
		{
			name:   "POST create order",
			method: http.MethodPost,
			path:   "/orders",
			body:   `{"id":"order-2","status":"PENDING","amount":50.00}`,
			repo:   &mockRepo{orders: map[string]*Order{}},
			wantStatus: http.StatusCreated,
		},
		{
			name:   "POST invalid JSON",
			method: http.MethodPost,
			path:   "/orders",
			body:   `{invalid`,
			repo:   &mockRepo{orders: map[string]*Order{}},
			wantStatus: http.StatusBadRequest,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			handler := &OrderHandler{repo: tt.repo}

			var bodyReader io.Reader
			if tt.body != "" {
				bodyReader = strings.NewReader(tt.body)
			}

			req := httptest.NewRequest(tt.method, tt.path, bodyReader)
			rec := httptest.NewRecorder()

			handler.ServeHTTP(rec, req)

			if rec.Code != tt.wantStatus {
				t.Errorf("status = %d, want %d", rec.Code, tt.wantStatus)
			}

			if tt.wantBody != "" && !strings.Contains(rec.Body.String(), tt.wantBody) {
				t.Errorf("body = %s, want to contain %s", rec.Body.String(), tt.wantBody)
			}
		})
	}
}
```

**Step 5 — 트레이드오프 & 대안**

| 전략 | 장점 | 단점 | 적합한 경우 |
|------|------|------|-------------|
| Table-driven + `t.Run` | 구조적, 병렬 가능, 필터 가능 | 복잡한 setup이 테이블에 맞지 않을 수 있음 | 입력-출력 매핑이 명확한 로직 |
| `testify/suite` | OOP 스타일, Setup/Teardown | 외부 의존성, Go 표준과 거리 | Java/Python 출신 팀 |
| `httptest.Server` | 실제 TCP 연결 테스트 | `httptest.NewRecorder`보다 느림 | 미들웨어, TLS 테스트 |
| `gomock`/`mockery` | 인터페이스 자동 mock 생성 | 코드 생성 필요, 과도한 mock은 brittle test | 외부 의존성이 많은 서비스 |
| Fuzzing (`testing.F`) | 예상치 못한 입력 발견 | 시간 소모, 결과 비결정적 | 파서, 인코더, 보안 코드 |

**Step 6 — 성장 & 심화 학습**

- **Go Blog**: "Using Subtests and Sub-benchmarks" — `t.Run` 설계 철학
- **TSan 논문**: "ThreadSanitizer -- data race detection in practice" (WBIA 2009) — race detector의 이론적 기반
- **Go 소스**: `src/runtime/race.go` — race detector의 Go 런타임 통합 방식
- **실전**: Google Testing Blog "Testing on the Toilet" 시리즈 — table-driven 패턴의 원조
- **Go 1.22 변경사항**: `for` 루프 변수 per-iteration scoping이 race 관련 버그를 얼마나 줄이는지

**🎯 면접관 평가 기준:**

- **L6 PASS**: table-driven test를 `t.Run` + `t.Parallel()`과 결합. race detector의 존재와 사용법(`go test -race`). `httptest.NewRecorder`로 핸들러 테스트. mock을 interface 기반으로 구현.
- **L7 EXCEED**: race detector의 내부 원리(TSan, vector clock, happens-before). CI에서의 `-race` 전략(오버헤드 관리). race detector의 한계(false negative)와 보완 전략. Go 1.22의 루프 변수 scoping 변경이 테스트에 미치는 영향.
- **🚩 RED FLAG**: `t.Parallel()` 없이 순차 실행만. race detector를 사용해 본 적 없음. `assert` 라이브러리 없이 테스트할 줄 모름(Go 표준은 `if`로 비교). 테스트에서 `time.Sleep`으로 goroutine 동기화.

---

### Q24: Go Fuzzing과 Property-Based Testing

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Testing Strategies

**Question:**
"Go 1.18에서 도입된 native fuzzing의 내부 아키텍처를 설명하세요. coverage-guided fuzzing이 무엇이고, 일반적인 random testing과 어떻게 다른지, 그리고 프로덕션 코드베이스에서 fuzzing을 효과적으로 적용하는 전략(어떤 함수를 fuzz해야 하는지, corpus 관리, CI 통합)을 구체적 코드와 함께 논의하세요."

---

**🧒 12살 비유:**
보물찾기를 생각해 봐. Random testing은 눈 감고 아무 곳이나 파는 거야. Fuzzing은 "이 방향으로 파니까 뭔가 단단한 게 느껴졌어!"(coverage 증가)라는 피드백을 받아서 더 깊이 파는 거야. 파다가 "이상한 것"(크래시, 패닉)이 나오면 그걸 보물 상자에 넣어두고(corpus) 다음에 그 근처를 더 집중적으로 파는 거지.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

Fuzzing은 수동 테스트케이스로 잡을 수 없는 edge case를 자동으로 발견한다. Go가 표준 라이브러리에 fuzzing을 포함한 것은 "보안과 안정성은 first-class citizen"이라는 메시지다. Staff 엔지니어는 (1) fuzzing의 이론적 기반, (2) 어떤 코드에 fuzzing이 효과적인지 판단하는 능력, (3) CI에서의 실용적 활용을 보여줘야 한다. Google OSS-Fuzz가 Go 프로젝트에서 수천 개의 버그를 발견한 실적이 이 질문의 배경이다.

**Step 2 — 핵심 기술 설명**

Go의 native fuzzing은 **coverage-guided mutation-based fuzzing**이다:
1. **Seed corpus**: 개발자가 제공하는 초기 입력 (`f.Add(...)` 또는 `testdata/fuzz/` 디렉토리)
2. **Mutation**: seed를 무작위로 변형 (bit flip, byte insert, arithmetic, dictionary)
3. **Coverage feedback**: 변형된 입력이 새로운 코드 경로를 실행하면 corpus에 추가
4. **Crash detection**: panic, 무한 루프(timeout), 메모리 초과 시 crasher로 기록

```go
package parser

import (
	"encoding/json"
	"errors"
	"fmt"
	"strconv"
	"strings"
	"testing"
	"unicode/utf8"
)

// 실제 fuzz 대상: 사용자 입력을 파싱하는 함수
type SearchQuery struct {
	Field    string
	Operator string
	Value    string
}

// ParseSearchQuery parses "field:operator:value" format
func ParseSearchQuery(input string) (*SearchQuery, error) {
	if len(input) == 0 {
		return nil, errors.New("empty query")
	}
	if len(input) > 1000 {
		return nil, errors.New("query too long")
	}
	if !utf8.ValidString(input) {
		return nil, errors.New("invalid UTF-8")
	}

	parts := strings.SplitN(input, ":", 3)
	if len(parts) != 3 {
		return nil, fmt.Errorf("expected field:operator:value, got %d parts", len(parts))
	}

	field, op, value := parts[0], parts[1], parts[2]

	// Field validation
	validFields := map[string]bool{"name": true, "age": true, "email": true, "status": true}
	if !validFields[field] {
		return nil, fmt.Errorf("unknown field: %q", field)
	}

	// Operator validation
	validOps := map[string]bool{"eq": true, "ne": true, "gt": true, "lt": true, "contains": true}
	if !validOps[op] {
		return nil, fmt.Errorf("unknown operator: %q", op)
	}

	// Type-specific validation
	if field == "age" && (op == "gt" || op == "lt") {
		if _, err := strconv.Atoi(value); err != nil {
			return nil, fmt.Errorf("age requires numeric value: %w", err)
		}
	}

	return &SearchQuery{Field: field, Operator: op, Value: value}, nil
}

// Fuzz test — Go 1.18+
func FuzzParseSearchQuery(f *testing.F) {
	// Seed corpus — 정상/비정상 입력을 모두 포함
	f.Add("name:eq:John")
	f.Add("age:gt:30")
	f.Add("email:contains:@gmail.com")
	f.Add("")                    // empty
	f.Add("no-colons")          // insufficient parts
	f.Add("a:b:c:d:e")          // extra colons (SplitN이 처리)
	f.Add("unknown:eq:value")   // invalid field
	f.Add("age:gt:not-a-number") // type mismatch
	f.Add(strings.Repeat("x", 2000)) // oversized

	f.Fuzz(func(t *testing.T, input string) {
		result, err := ParseSearchQuery(input)

		// Property 1: 함수는 절대 panic해서는 안 된다
		// (이것만으로도 crasher를 찾을 수 있음)

		// Property 2: error와 result는 상호 배타적
		if err != nil && result != nil {
			t.Errorf("got both error and result for input %q", input)
		}
		if err == nil && result == nil {
			t.Errorf("got neither error nor result for input %q", input)
		}

		// Property 3: 성공 시 결과의 invariant 검증
		if result != nil {
			if result.Field == "" {
				t.Error("result.Field is empty")
			}
			if result.Operator == "" {
				t.Error("result.Operator is empty")
			}
		}
	})
}

// JSON roundtrip fuzzing — 직렬화/역직렬화 일관성 검증
type UserProfile struct {
	Name  string `json:"name"`
	Age   int    `json:"age"`
	Email string `json:"email"`
	Tags  []string `json:"tags"`
}

func FuzzJSONRoundtrip(f *testing.F) {
	f.Add("Alice", 30, "alice@test.com", "dev,go")
	f.Add("", 0, "", "")
	f.Add("Bob\nSmith", -1, "a@b", "tag1")

	f.Fuzz(func(t *testing.T, name string, age int, email string, tagsStr string) {
		var tags []string
		if tagsStr != "" {
			tags = strings.Split(tagsStr, ",")
		}

		original := UserProfile{
			Name:  name,
			Age:   age,
			Email: email,
			Tags:  tags,
		}

		// Serialize
		data, err := json.Marshal(original)
		if err != nil {
			return // json.Marshal이 실패할 수 있는 입력은 skip
		}

		// Deserialize
		var decoded UserProfile
		if err := json.Unmarshal(data, &decoded); err != nil {
			t.Fatalf("Marshal succeeded but Unmarshal failed: %v", err)
		}

		// Property: roundtrip consistency
		if original.Name != decoded.Name {
			t.Errorf("Name mismatch: %q vs %q", original.Name, decoded.Name)
		}
		if original.Age != decoded.Age {
			t.Errorf("Age mismatch: %d vs %d", original.Age, decoded.Age)
		}
	})
}
```

Coverage-guided의 핵심 메커니즘:

```
Iteration 1: input = "name:eq:John" → coverage set A = {line 10, 15, 20, 25}
Iteration 2: input = "name:eq:J\x00hn" (mutation) → coverage set B = {line 10, 15, 20, 25}
  → B ⊆ A, 새로운 경로 없음 → 버림
Iteration 3: input = "age:gt:xyz" (mutation) → coverage set C = {line 10, 15, 30, 35, 40}
  → C ⊄ A, 새로운 경로 발견(line 30, 35, 40) → corpus에 추가!
Iteration 4: input = "age:gt:xy" (Iteration 3에서 mutation) → 더 깊은 경로 탐색...
```

**Step 3 — 다양한 관점**

| 관점 | 분석 |
|------|------|
| **보안** | 파서, 디코더, 역직렬화 코드는 fuzzing 1순위 대상. 외부 입력을 받는 모든 코드가 해당 |
| **성능** | fuzzing은 CPU intensive. CI에서는 `go test -fuzz=. -fuzztime=30s`로 시간 제한 |
| **Corpus 관리** | `testdata/fuzz/FuncName/` 디렉토리의 corpus 파일은 git에 커밋. crasher도 regression test로 보존 |
| **한계** | fuzzing은 "crash를 찾는 것"에 최적화. 비즈니스 로직의 correctness는 property-based assertion이 보완 |
| **Go 내부** | `go test -fuzz`는 별도 프로세스(coordinator + worker)로 실행. `-parallel` 플래그로 worker 수 조절 |

**Step 4 — 구체적 예시: CI 통합 전략**

```yaml
name: Fuzz Tests
on:
  schedule:
    - cron: '0 2 * * *'  # 매일 새벽 2시 (비피크 시간)
  push:
    branches: [main]

jobs:
  fuzz:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        fuzz-target:
          - FuzzParseSearchQuery
          - FuzzJSONRoundtrip
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'

      # Corpus 캐시 — 이전 실행에서 발견한 흥미로운 입력 재활용
      - uses: actions/cache@v4
        with:
          path: testdata/fuzz
          key: fuzz-corpus-${{ matrix.fuzz-target }}-${{ github.sha }}
          restore-keys: fuzz-corpus-${{ matrix.fuzz-target }}-

      # PR에서는 30초, scheduled에서는 5분
      - name: Run Fuzzing
        run: |
          FUZZ_TIME=30s
          if [ "${{ github.event_name }}" = "schedule" ]; then
            FUZZ_TIME=5m
          fi
          go test ./... -fuzz=${{ matrix.fuzz-target }} -fuzztime=$FUZZ_TIME

      # Crasher 발견 시 corpus를 artifact로 저장
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: fuzz-crashers-${{ matrix.fuzz-target }}
          path: testdata/fuzz/
```

**어떤 함수를 fuzz해야 하는가?**

| 우선순위 | 대상 | 이유 | 예시 |
|----------|------|------|------|
| **1 (필수)** | 외부 입력 파서 | 공격 표면 | HTTP body 파서, URL 파서 |
| **2 (강력 권장)** | 인코더/디코더 | roundtrip invariant | JSON, Protobuf, 커스텀 직렬화 |
| **3 (권장)** | 문자열 처리 | Unicode, 빈 문자열 edge case | 검색 쿼리, 필터 |
| **4 (선택)** | 수학/변환 함수 | overflow, 경계값 | 가격 계산, 단위 변환 |
| **5 (불필요)** | 비즈니스 CRUD | 입력 공간이 너무 넓음 | 주문 생성 workflow |

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 적합한 경우 |
|--------|------|------|-------------|
| Go native fuzzing | 표준 라이브러리, corpus 관리 내장 | 구조체 입력 지원 제한 | Go 전용, 단순 입력 타입 |
| go-fuzz (dvyukov) | 성숙, 많은 버그 발견 실적 | Go 1.18+ native에 대체됨 | 레거시 프로젝트 |
| OSS-Fuzz | 24/7 무료 fuzzing, 대규모 인프라 | 오픈소스 프로젝트만 | 라이브러리 개발자 |
| `rapid` (property-based) | 구조체 generator, shrinking | 외부 의존성 | 복잡한 도메인 로직 |
| `gopter` | Haskell QuickCheck 스타일 | 학습 곡선 | FP 스타일 property 테스트 |

**Step 6 — 성장 & 심화 학습**

- **Go Blog**: "Go Fuzzing" (2022) — 설계 철학과 사용법
- **Go Proposal**: #44551 — native fuzzing의 설계 결정 과정
- **AFL/libFuzzer 논문**: coverage-guided fuzzing의 이론적 기반
- **OSS-Fuzz 사이트**: Google의 오픈소스 fuzzing 인프라, Go 프로젝트 참여 방법
- **`dvyukov/go-fuzz-corpus`**: 실제 Go 표준 라이브러리에서 발견된 fuzzing 버그 모음

**🎯 면접관 평가 기준:**

- **L6 PASS**: `testing.F`를 사용한 fuzz test 작성. seed corpus의 역할 설명. coverage-guided와 random의 차이. CI에서 `-fuzztime`으로 시간 제한.
- **L7 EXCEED**: coverage-guided의 내부 메커니즘(코드 계측, 새 경로 발견 시 corpus 추가). fuzzing 대상 선정 기준(외부 입력 파서 우선). corpus 관리와 git 통합. OSS-Fuzz 경험. property-based testing과 fuzzing의 차이와 조합.
- **🚩 RED FLAG**: fuzzing을 "random input 넣는 것"으로만 이해. seed corpus 없이 fuzz 함수 작성. 모든 함수를 무차별 fuzzing(대상 선정 능력 부족). crasher를 regression test로 보존하지 않음.

---

## 10. Module System & Build

### Q25: Go Modules의 MVS 알고리즘과 의존성 관리 전략

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Module System & Build

**Question:**
"Go Modules의 Minimal Version Selection(MVS) 알고리즘이 npm, pip, Cargo 등 다른 패키지 매니저의 SAT solver 방식과 어떻게 다른지 설명하세요. MVS의 설계 철학, 장단점, 그리고 diamond dependency 문제를 어떻게 해결하는지 구체적 예시와 함께 논의하세요. 또한 Go workspace(`go.work`), vendoring, private module proxy 운영 전략도 포함하세요."

---

**🧒 12살 비유:**
레고 세트를 조립하는데 부품이 필요하다고 생각해 봐. npm/pip 방식은 "가장 최신 부품을 가져와!"인데, 부품 A의 최신 버전이 부품 B의 최신 버전과 안 맞을 수 있어서 복잡한 퍼즐(SAT solver)을 풀어야 해. Go의 MVS 방식은 "각 설명서에 적힌 최소 버전을 가져와!"야. 설명서 A가 "부품 C v1.2 이상", 설명서 B가 "부품 C v1.3 이상"이면, v1.3을 가져와 — 최신(v1.5)이 아니라 필요한 최소(v1.3). 이러면 퍼즐을 풀 필요 없이 답이 바로 나와!

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

의존성 관리는 대규모 소프트웨어 엔지니어링의 핵심 문제다. Russ Cox가 MVS를 설계한 이유는 SAT solver 기반 접근의 근본적 문제(NP-complete, 비결정적, 버전 선택의 재현 불가능성)를 해결하기 위해서다. Staff 엔지니어는 (1) 이 설계 결정의 이유를 이해하고, (2) 실제 대규모 프로젝트에서 발생하는 의존성 문제를 해결할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

**MVS(Minimal Version Selection)의 핵심 원리:**

SAT solver 방식 (npm, pip, Cargo):
- 모든 의존성의 가능한 버전 조합에서 **제약 조건을 만족하는 최신 버전**을 선택
- NP-complete 문제 → 휴리스틱 사용 → 비결정적 결과 가능
- lock 파일(`package-lock.json`, `Pipfile.lock`)로 재현성 보장 시도

MVS 방식 (Go):
- 각 모듈이 선언한 **최소 필요 버전** 중 가장 높은 것을 선택
- 다항 시간(O(n))에 해결 → 결정적, lock 파일 불필요
- `go.sum`은 lock 파일이 아니라 **무결성 체크섬** 파일

```
예시: Diamond Dependency

       A (우리 모듈)
      / \
     B   C
      \ /
       D

B requires D >= v1.2.0
C requires D >= v1.4.0

npm/pip: D의 최신 v1.8.0을 선택 (latest satisfying)
Go MVS:  D v1.4.0을 선택 (minimum satisfying)
```

**왜 최소 버전인가?**
1. **재현성**: 같은 `go.mod`에서 항상 같은 버전이 선택됨 (lock 파일 불필요)
2. **안정성**: 새 버전은 새 버그를 포함할 수 있음. 검증된 최소 버전이 더 안전
3. **단순성**: O(n) 알고리즘, 충돌 해결 불필요
4. **명시적 업그레이드**: `go get -u` 없이는 의존성이 자동으로 올라가지 않음

```go
// go.mod 예시
module github.com/mycompany/myservice

go 1.22

require (
    github.com/gin-gonic/gin v1.9.1       // 직접 의존성
    github.com/jackc/pgx/v5 v5.5.0
    google.golang.org/grpc v1.60.0
)

require (
    // 간접 의존성 — go mod tidy가 자동 관리
    golang.org/x/net v0.19.0 // indirect
    golang.org/x/text v0.14.0 // indirect
)
```

**go.sum의 역할 (lock 파일이 아님!)**:

```
// go.sum — 각 모듈의 해시값 (무결성 검증용)
github.com/gin-gonic/gin v1.9.1 h1:4idEAncQnU5cB7BeOkPtxjfCSye0AAm1R0RVIqFPSyI=
github.com/gin-gonic/gin v1.9.1/go.mod h1:hPrL/0KcuFAOsKBP...=

// lock 파일과의 차이:
// - lock 파일: "어떤 버전을 설치할지" 결정
// - go.sum: "설치된 버전이 변조되지 않았는지" 검증
// MVS가 결정적이므로 go.mod만으로 버전이 결정됨
```

**Step 3 — 다양한 관점**

| 패키지 매니저 | 알고리즘 | 결정적 | Lock 파일 필요 | 복잡도 |
|---------------|----------|--------|----------------|--------|
| Go Modules | MVS | Yes | No (`go.sum`은 checksum) | O(n) |
| npm | SAT solver | No | Yes (`package-lock.json`) | NP-complete |
| pip | SAT solver | No | Yes (`Pipfile.lock`) | NP-complete |
| Cargo | SAT solver | No | Yes (`Cargo.lock`) | NP-complete |
| Maven | Nearest-first | Yes | No | O(n) |

MVS의 **트레이드오프**:
| 장점 | 단점 |
|------|------|
| 결정적, 재현 가능 | 보안 패치가 자동으로 적용되지 않음 |
| Lock 파일 불필요 | `go get -u`를 명시적으로 실행해야 함 |
| O(n) 알고리즘 | Semantic versioning 위반 시 문제 |
| Diamond dependency 자연스럽게 해결 | Major version이 import path에 포함됨 (v2+) |

**Step 4 — 구체적 예시: Workspace, Vendoring, Private Module**

```go
// go.work — 멀티 모듈 개발 (Go 1.18+)
// monorepo에서 여러 모듈을 동시에 개발할 때 사용

// go.work
go 1.22

use (
    ./services/order
    ./services/payment
    ./libs/common
    ./libs/proto
)

// 장점: libs/common을 수정하면 services/order에서 즉시 반영
// 주의: go.work는 git에 커밋하지 않는 것이 관례 (.gitignore에 추가)
//       CI에서는 각 모듈이 독립적으로 빌드되어야 함
```

```bash

go mod vendor          # vendor/ 디렉토리 생성
go build -mod=vendor   # vendor에서만 빌드 (네트워크 접근 없음)

```

```bash

export GOPROXY="https://proxy.mycompany.com,https://proxy.golang.org,direct"
export GONOSUMDB="github.com/mycompany/*"
export GOPRIVATE="github.com/mycompany/*"
export GONOSUMCHECK="github.com/mycompany/*"

```

**Build tags와 cross-compilation:**

```go
//go:build linux && amd64
// +build linux,amd64

package platform

// 이 파일은 linux/amd64에서만 컴파일됨
func PlatformSpecificInit() {
    // epoll 기반 이벤트 루프 등
}

// === 파일 이름 기반 빌드 태그 (convention) ===
// server_linux.go   → linux에서만 컴파일
// server_darwin.go  → macOS에서만 컴파일
// server_test.go    → 테스트에서만 컴파일
```

```bash

GOOS=linux GOARCH=amd64 go build -o myapp-linux-amd64 ./cmd/server

GOOS=linux GOARCH=arm64 go build -o myapp-linux-arm64 ./cmd/server

GOOS=windows GOARCH=amd64 go build -o myapp.exe ./cmd/server

CGO_ENABLED=1 CC=x86_64-linux-musl-gcc GOOS=linux GOARCH=amd64 go build -o myapp ./cmd/server
```

**Step 5 — 트레이드오프 & 대안**

| 전략 | 장점 | 단점 | 적합한 경우 |
|------|------|------|-------------|
| `go.mod` only | 단순, 표준 | 빌드 시 네트워크 필요 | 소규모, 공개 모듈만 |
| `go mod vendor` | 오프라인 빌드, 감사 가능 | 저장소 크기 증가 | 규제 산업, air-gap 환경 |
| Private proxy (Athens) | 캐시, 접근 제어 | 인프라 운영 필요 | 대규모 기업 |
| `go.work` | 로컬 멀티 모듈 개발 편의 | CI와 동기화 주의 | monorepo |
| Bazel + rules_go | 증분 빌드, 캐시 | 학습 곡선, Go 도구와 마찰 | Google 규모 monorepo |

**Step 6 — 성장 & 심화 학습**

- **Russ Cox 블로그**: "Minimal Version Selection" — MVS 설계 철학의 원문
- **Go Blog**: "Using Go Modules" 시리즈 (4부작) — 공식 가이드
- **논문**: "Version SAT" — SAT solver 기반 의존성 해결의 NP-completeness 증명
- **Athens 프로젝트**: Go module proxy의 오픈소스 구현 — 내부 동작 분석
- **`go mod graph`**: 의존성 그래프를 시각화하여 diamond dependency 분석

**🎯 면접관 평가 기준:**

- **L6 PASS**: MVS와 SAT solver의 차이를 설명. `go.sum`이 lock 파일이 아님을 이해. `go mod tidy`, `go mod vendor` 사용. GOPROXY/GOPRIVATE 설정. 크로스 컴파일 경험.
- **L7 EXCEED**: MVS의 결정성이 왜 중요한지(재현 가능한 빌드). diamond dependency를 MVS가 해결하는 과정을 예시로 설명. `go.work`의 적절한 사용 범위. private proxy 아키텍처. CGo의 비용과 회피 전략.
- **🚩 RED FLAG**: `go.sum`을 `.gitignore`에 추가. `go get -u`를 이해 없이 습관적 사용. vendoring과 module의 차이를 모름. major version path(`/v2`)를 이해하지 못함.

---

### Q26: CGo의 비용과 Build Optimization 전략

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Module System & Build

**Question:**
"CGo를 사용할 때 발생하는 runtime 비용을 구체적 수치와 함께 설명하세요. goroutine 스택, 스케줄링, GC와의 상호작용을 포함하여 논의하고, CGo를 피하는 전략과 불가피하게 사용해야 할 때의 최적화 방법을 코드와 함께 보여주세요. 또한 `go build`의 캐시, `-ldflags`, 바이너리 크기 최적화 등 빌드 파이프라인 전체를 설계하세요."

---

**🧒 12살 비유:**
Go 코드와 C 코드가 대화하는 것은 두 나라 사람이 통역사를 통해 대화하는 거야. 직접 대화(순수 Go 함수 호출)는 1초면 되는데, 통역사를 거치면(CGo) 100배 느려져. 왜냐하면 통역사가 (1) 한국어를 영어로 번역하고(스택 전환), (2) 대화 내용을 기록하고(GC 협력), (3) 다시 한국어로 번역해야(결과 변환) 하니까. 그래서 가능하면 같은 언어(순수 Go)로 대화하고, 정말 필요할 때만 통역사를 부르는 거야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**

CGo는 Go의 "escape hatch"다. SQLite, OpenSSL, CUDA 같은 C 라이브러리를 사용할 때 필수적이지만, 그 비용은 많은 개발자가 과소평가한다. Staff 엔지니어는 (1) CGo의 정확한 runtime 오버헤드를 수치로 알고, (2) 순수 Go 대안이 있는지 판단하며, (3) 불가피한 경우 비용을 최소화하는 전략을 설계할 수 있어야 한다. 유명한 격언: "Cgo is not Go" (Dave Cheney).

**Step 2 — 핵심 기술 설명**

**CGo 호출 비용 분석:**

순수 Go 함수 호출: ~2ns
CGo 함수 호출: ~200ns (약 100x 오버헤드)

오버헤드의 원인:
1. **스택 전환**: Go goroutine은 segmented/growable stack (기본 8KB)을 사용하지만, C 코드는 고정 크기 스택이 필요. CGo는 system thread의 C 스택으로 전환.
2. **스케줄러 협력**: CGo 호출 중인 goroutine은 Go 스케줄러의 `M`(OS thread)을 점유. 다른 goroutine이 실행되려면 새 `M`이 필요할 수 있음.
3. **GC 정지**: GC는 모든 goroutine을 stop-the-world할 때 CGo 중인 goroutine을 기다려야 함. CGo 호출이 길면 GC latency 증가.
4. **메모리 복사**: Go string/slice와 C 포인터 간 데이터를 복사해야 함 (Go GC가 C 메모리를 추적할 수 없으므로).

```go
package cgodemo

/*
#include <string.h>
#include <stdlib.h>

// 간단한 C 함수
int c_add(int a, int b) {
    return a + b;
}

// 문자열 처리 — 메모리 관리가 복잡해지는 지점
char* c_to_upper(const char* input) {
    int len = strlen(input);
    char* result = (char*)malloc(len + 1);
    for (int i = 0; i < len; i++) {
        if (input[i] >= 'a' && input[i] <= 'z') {
            result[i] = input[i] - 32;
        } else {
            result[i] = input[i];
        }
    }
    result[len] = '\0';
    return result;  // 호출자가 free() 해야 함!
}
*/
import "C"

import (
	"strings"
	"unsafe"
)

// CGo를 통한 C 함수 호출 — 약 200ns/call
func CgoAdd(a, b int) int {
	return int(C.c_add(C.int(a), C.int(b)))
}

// 순수 Go — 약 2ns/call
func GoAdd(a, b int) int {
	return a + b
}

// CGo 문자열 처리 — 메모리 관리 주의!
func CgoToUpper(input string) string {
	// Go string → C string (malloc + copy)
	cInput := C.CString(input) // ⚠️ malloc 발생
	defer C.free(unsafe.Pointer(cInput)) // 반드시 free!

	// C 함수 호출
	cResult := C.c_to_upper(cInput) // ⚠️ C에서 malloc된 메모리
	defer C.free(unsafe.Pointer(cResult)) // 반드시 free!

	// C string → Go string (copy)
	return C.GoString(cResult) // Go 힙에 복사
}

// 순수 Go 대안 — 훨씬 빠르고 안전
func GoToUpper(input string) string {
	return strings.ToUpper(input) // 최적화된 Go 구현
}
```

**CGo가 불가피한 경우와 최적화:**

```go
package optimized

/*
#cgo CFLAGS: -O2 -Wall
#cgo LDFLAGS: -lsqlite3

#include <sqlite3.h>
#include <stdlib.h>

// 배치 처리 — CGo 호출 횟수를 최소화
// 나쁜 패턴: 1000개 행을 1000번 CGo 호출로 삽입
// 좋은 패턴: 1000개 행을 1번 CGo 호출로 일괄 삽입
int batch_insert(sqlite3* db, const char* values[], int count) {
    sqlite3_exec(db, "BEGIN", 0, 0, 0);
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, "INSERT INTO items(name) VALUES(?)", -1, &stmt, 0);
    for (int i = 0; i < count; i++) {
        sqlite3_bind_text(stmt, 1, values[i], -1, SQLITE_STATIC);
        sqlite3_step(stmt);
        sqlite3_reset(stmt);
    }
    sqlite3_finalize(stmt);
    sqlite3_exec(db, "COMMIT", 0, 0, 0);
    return count;
}
*/
import "C"

// 최적화 원칙: "CGo 경계를 넘는 횟수를 최소화"
// ❌ Bad: for loop에서 매번 CGo 호출
// ✅ Good: 데이터를 모아서 한 번에 전달
```

**빌드 최적화 전략:**

```bash
go env GOCACHE    # 캐시 디렉토리 확인
go clean -cache   # 캐시 초기화 (디버깅 시에만)

go build -o myapp ./cmd/server

go build -ldflags="-s -w" -o myapp ./cmd/server

upx --best myapp

go build -ldflags="-s -w \
  -X main.version=1.2.3 \
  -X main.commit=$(git rev-parse --short HEAD) \
  -X main.buildDate=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  -o myapp ./cmd/server

CGO_ENABLED=0 go build -o myapp ./cmd/server

go build -trimpath -o myapp ./cmd/server
```

```go
// 빌드 시 주입된 버전 정보 활용
package main

import "fmt"

// ldflags로 주입
var (
	version   = "dev"
	commit    = "unknown"
	buildDate = "unknown"
)

func printVersion() {
	fmt.Printf("Version: %s\nCommit: %s\nBuild Date: %s\n",
		version, commit, buildDate)
}
```

**프로덕션 Dockerfile (멀티 스테이지):**

```dockerfile
FROM golang:1.22-alpine AS builder


WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download  # 의존성 레이어 캐시

COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -trimpath \
    -ldflags="-s -w -X main.version=${VERSION}" \
    -o /app/server ./cmd/server

FROM scratch

COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

COPY --from=builder /app/server /server

EXPOSE 8080
ENTRYPOINT ["/server"]
```

**Step 3 — 다양한 관점**

| 관점 | CGo 사용 | 순수 Go 대안 |
|------|----------|-------------|
| **SQLite** | `mattn/go-sqlite3` (CGo) | `modernc.org/sqlite` (순수 Go, ~20% 느림) |
| **SSL/TLS** | OpenSSL via CGo | `crypto/tls` (Go 표준, 대부분 충분) |
| **이미지 처리** | libvips via CGo | `disintegration/imaging` (순수 Go) |
| **기계학습** | TensorFlow C API | ONNX Runtime via gRPC (프로세스 분리) |
| **시스템 콜** | CGo 불필요 | `syscall`/`golang.org/x/sys` 패키지 |

**Step 4 — 구체적 예시: CGo를 피하는 아키텍처 패턴**

```go
// 패턴: CGo 대신 프로세스 분리 (sidecar 또는 subprocess)
// C 라이브러리가 필요한 부분을 별도 프로세스로 분리하고 IPC로 통신

package mlclient

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// ❌ CGo: Go 프로세스에 C++ TensorFlow 링크
// → 빌드 복잡, 크로스 컴파일 불가, GC 간섭

// ✅ 프로세스 분리: Python/C++ ML 서버를 sidecar로 실행
type MLClient struct {
	httpClient *http.Client
	baseURL    string
}

func NewMLClient(baseURL string) *MLClient {
	return &MLClient{
		httpClient: &http.Client{
			Timeout: 5 * time.Second,
		},
		baseURL: baseURL,
	}
}

type PredictRequest struct {
	Features []float64 `json:"features"`
}

type PredictResponse struct {
	Score      float64 `json:"score"`
	Confidence float64 `json:"confidence"`
}

func (c *MLClient) Predict(ctx context.Context, features []float64) (*PredictResponse, error) {
	body, _ := json.Marshal(PredictRequest{Features: features})
	req, _ := http.NewRequestWithContext(ctx, http.MethodPost,
		fmt.Sprintf("%s/predict", c.baseURL), bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("ml prediction failed: %w", err)
	}
	defer resp.Body.Close()

	var result PredictResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode prediction: %w", err)
	}
	return &result, nil
}

// 장점:
// 1. Go 바이너리는 CGO_ENABLED=0로 빌드 (scratch 컨테이너)
// 2. ML 모델은 Python/C++ 컨테이너에서 독립 실행
// 3. 각각 독립 스케일링 가능
// 4. GC 간섭 없음
```

**Step 5 — 트레이드오프 & 대안**

| 전략 | 장점 | 단점 | 적합한 경우 |
|------|------|------|-------------|
| CGo 직접 사용 | 저지연, C API 직접 접근 | 빌드 복잡, GC 영향, 크로스 컴파일 불가 | 성능 임계, 호출 빈도 낮은 경우 |
| 순수 Go 대안 | 빌드 단순, 크로스 컴파일 | C 구현보다 느릴 수 있음 | 대부분의 경우 |
| 프로세스 분리 (sidecar) | 완전 격리, 독립 스케일링 | 네트워크 레이턴시, 직렬화 비용 | ML 추론, 이미지 처리 |
| WASM | 샌드박스, 이식성 | 성능 오버헤드, 생태계 미성숙 | 플러그인 시스템 |
| FFI (purego) | CGo 없이 shared library 호출 | 불안정, 제한적 | 실험적 사용 |

**Step 6 — 성장 & 심화 학습**

- **Dave Cheney**: "cgo is not Go" — CGo의 숨겨진 비용을 정리한 필독 블로그
- **Go 소스**: `src/runtime/cgocall.go` — CGo 호출의 런타임 구현
- **Filippo Valsorda**: "Go builds are not reproducible" → 재현 가능한 빌드 전략
- **`ko`**: Google의 Go 컨테이너 빌드 도구 — Dockerfile 없이 이미지 생성
- **Bazel `rules_go`**: 대규모 Go 프로젝트의 빌드 캐시와 원격 실행

**🎯 면접관 평가 기준:**

- **L6 PASS**: CGo의 ~100x 오버헤드를 인지. `CGO_ENABLED=0`으로 순수 Go 빌드. `-ldflags="-s -w"`로 바이너리 최적화. 멀티 스테이지 Dockerfile. 크로스 컴파일 경험.
- **L7 EXCEED**: CGo 오버헤드의 원인(스택 전환, 스케줄러, GC 상호작용)을 설명. "CGo 경계 횟수 최소화" 전략. 순수 Go 대안 vs CGo의 판단 기준. 프로세스 분리 아키텍처. 빌드 재현성(trimpath, go.sum). MVS와 빌드 시스템의 관계.
- **🚩 RED FLAG**: CGo 비용을 모름. `CGO_ENABLED` 환경 변수를 모름. Dockerfile에서 `golang:latest`를 런타임 이미지로 사용. 빌드 캐시를 활용하지 않음. C.CString 후 C.free를 빠뜨림(메모리 누수).
