---
created: 2026-03-18
source: claude-code
tags: [concurrency, unix, atomic, mutex, semaphore, linux-kernel, cpu-architecture, cache-coherency, futex, deadlock, spinlock, lock-free]
---

# 🔬 Atomic / Mutex / Semaphore 심화 Q&A — Deep Dive

> 이 문서는 `unix-atomic-mutex-semaphore-deep-dive.md`를 학습한 후 제기된 30개 이상의 심화 질문에 대한 답변이다.
> CPU 아키텍처 기초부터 실무 AWS 아키텍처까지 넓은 범위를 다룬다.
> 12살도 이해할 수 있는 현실 비유 + 커널/하드웨어 레벨 기술 내용을 함께 담는다.

---

# Part 1: CPU 아키텍처 & 캐시 기초

---

## Q1: Memory Barrier — "순서를 지켜!" 표지판

### 🎯 현실 비유: 학교 급식 줄 서기

급식실에서 학생들이 줄을 서야 한다고 생각해보자.

> **선생님(컴파일러/CPU)** 이 "더 효율적으로 줄 세울게!" 하면서 순서를 바꾼다.
> 혼자 먹을 때는 순서가 달라져도 결과는 똑같다.
> 그런데 **두 반이 동시에** 줄을 서면? 순서가 바뀌면 충돌이 생긴다!
> **Memory Barrier** = 급식실 입구에 붙은 "여기서부터 순서 절대 바꾸지 말 것!" 표지판.

---

### 왜 Memory Barrier가 필요한가?

코드를 짤 때 우리가 적는 순서와 실제 CPU가 실행하는 순서는 **다를 수 있다.**
두 가지 재배치가 있다.

```
[재배치 종류]
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  소스코드          컴파일러 최적화        CPU 실행 순서 │
│                                                         │
│  a = 1;    ──→    b = 2;    ──→    (파이프라인 최적화)  │
│  b = 2;           a = 1;           실제 순서 불확정     │
│                                                         │
│  컴파일러 재배치: 소스 → 기계어 변환 시 발생           │
│  CPU 재배치:     실행 중 Out-of-Order 최적화 발생       │
└─────────────────────────────────────────────────────────┘
```

#### 1) 컴파일러 재배치

컴파일러는 "결과가 같으면 순서를 바꿔도 되잖아!" 라고 생각한다.

```c
// 개발자가 쓴 코드
data  = 42;
ready = 1;   // "data 준비 완료" 신호

// 컴파일러가 바꿀 수 있음!
ready = 1;   // ← 먼저 실행!
data  = 42;  // 다른 스레드가 ready=1을 보는 순간, data는 아직 42가 아님!
```

#### 2) CPU 재배치 (Out-of-Order Execution)

CPU는 파이프라인 효율을 위해 **Store Buffer** 와 **Load Buffer** 를 사용한다.
쓰기(Store)가 메모리에 반영되기 전에 다른 명령이 먼저 실행될 수 있다.

```
┌──────────────────────────────────────────────────────────────┐
│                     CPU Core 내부                            │
│                                                              │
│  명령어 스트림: [A] [B] [C] [D]                             │
│                  ↓                                           │
│         Instruction Decoder                                  │
│                  ↓                                           │
│  ┌───────────────────────────────┐                          │
│  │    Reorder Buffer (ROB)       │  ← CPU가 순서 재조정     │
│  │  실행: [C] [A] [D] [B]       │                          │
│  └───────────────────────────────┘                          │
│                  ↓                                           │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Store Buffer │  │ Load Buffer  │  ← 쓰기/읽기 지연 가능  │
│  └──────────────┘  └──────────────┘                        │
│                  ↓                                           │
│              L1 Cache / DRAM                                │
└──────────────────────────────────────────────────────────────┘
```

---

### Acquire / Release / Full Barrier 단계별 흐름

#### Acquire Barrier (잠금 잡을 때)

> 비유: 도서관 입장. "들어간 이후에 할 일은 절대 밖으로 빼내지 마!"

```
시간 흐름 →

Before         ACQUIRE BARRIER        After
  ↓                   |                ↓
[읽기A]               |            [읽기C]
[읽기B]    ← 이것들은 │ 이것들은 →  [쓰기D]
[쓰기X]      배리어 뒤로 이동 불가!  [쓰기E]
           ───────────┼───────────
                      │ 배리어 이후의 연산이
                      │ 배리어 이전으로 올라오지 못함
```

```c
// 예: 뮤텍스 lock 획득 후 임계구역 진입
pthread_mutex_lock(&mutex);  // 내부적으로 acquire barrier
// 이 아래의 읽기/쓰기는 위로 재배치되지 않음
critical_section_read();
```

#### Release Barrier (잠금 풀 때)

> 비유: 도서관 퇴장. "나가기 전에 할 일은 절대 밖으로 빼내지 마!"

```
시간 흐름 →

Before         RELEASE BARRIER        After
  ↓                   |                ↓
[읽기A]               |            [읽기C]
[쓰기B]    → 이것들은 │ 이것들은 ←  [쓰기D]
[쓰기X]      배리어 앞으로 이동 불가!
           ───────────┼───────────
                      │ 배리어 이전의 연산이
                      │ 배리어 이후로 내려가지 못함
```

```c
// 예: 임계구역 작업 후 뮤텍스 unlock
critical_section_write();
// 이 위의 읽기/쓰기는 아래로 재배치되지 않음
pthread_mutex_unlock(&mutex);  // 내부적으로 release barrier
```

#### Full Barrier (양방향 완전 봉쇄)

```
시간 흐름 →

Before         FULL BARRIER           After
  ↓                   |                ↓
[읽기A]               │            [읽기C]
[쓰기B]   ← 불가 ─── ┼ ─── 불가 →  [쓰기D]
                      │
           ═══════════╪═══════════
           양방향 모두 이동 불가!
```

```c
// C11 atomic: full barrier
atomic_thread_fence(memory_order_seq_cst);

// 또는 GCC 내장
__sync_synchronize();  // full memory barrier
```

---

### 실제 명령어 매핑: x86 vs ARM

```
┌──────────────┬─────────────────────┬────────────────────────┐
│  Barrier 종류 │      x86 명령어      │      ARM 명령어        │
├──────────────┼─────────────────────┼────────────────────────┤
│ Full Barrier │ MFENCE              │ DMB ISH                │
│ Load Barrier │ LFENCE              │ DMB ISHLD              │
│ Store Barrier│ SFENCE              │ DMB ISHST              │
│ Sync Barrier │ LOCK (접두어)       │ DSB ISH                │
├──────────────┼─────────────────────┼────────────────────────┤
│ 특이사항      │ x86은 TSO 모델:     │ ARM은 Weak Order 모델: │
│              │ 기본적으로 강한 순서  │ 배리어 명시 필수       │
│              │ 보장 → 배리어 덜 필요 │ → 더 세심한 관리 필요  │
└──────────────┴─────────────────────┴────────────────────────┘
```

```c
// C11 표준 memory order로 배리어 표현
#include <stdatomic.h>

atomic_int flag = 0;
int data = 0;

// Thread 1: 데이터 준비 후 신호 발송
void producer(void) {
    data = 42;                                    // 일반 쓰기
    atomic_store_explicit(&flag, 1,
        memory_order_release);                    // Release barrier
    //  ↑ data=42가 반드시 먼저 보임을 보장
}

// Thread 2: 신호 확인 후 데이터 읽기
void consumer(void) {
    while (atomic_load_explicit(&flag,
        memory_order_acquire) == 0);             // Acquire barrier
    //  ↑ flag=1 확인 후, data 읽기가 재배치되지 않음
    printf("data = %d\n", data);  // 반드시 42 출력
}
```

> 💡 **핵심 인사이트**
>
> - Memory Barrier는 **순서를 강제하는 울타리**다. 없으면 컴파일러/CPU가 재배치한다.
> - x86은 강한 메모리 모델(TSO)이라 기본적으로 순서가 많이 보장되지만, ARM은 Weak Order라 배리어가 필수다.
> - `mutex lock` = acquire barrier, `mutex unlock` = release barrier. 이미 매일 쓰고 있었던 것!
> - C11 `memory_order_acquire/release` 를 쓰면 플랫폼에 맞는 최적 명령어로 컴파일된다.

---

## Q2: Cache Coherency — "같은 책을 두 명이 동시에 고친다면?"

### 🎯 현실 비유: 학교 도서관의 복사본 책

학교 도서관에 책이 1권 있다. 두 학생이 동시에 읽으려고 각자 복사본을 가져갔다.
그런데 한 학생이 자기 복사본에 빨간 펜으로 고쳤다!
다른 학생의 복사본은 아직 구버전이다.

> **Cache Coherency** = 복사본들이 항상 같은 내용이도록 관리하는 규칙 시스템.

---

### CPU와 Core의 차이 (물리적 구조)

```
┌───────────────────────────────────────────────────────────┐
│                  학교 건물 = CPU Package                   │
│                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │  1반 교실    │  │  2반 교실    │  │  3반 교실    │      │
│  │  = Core 0   │  │  = Core 1   │  │  = Core 2   │      │
│  │             │  │             │  │             │      │
│  │ 선생님=ALU  │  │ 선생님=ALU  │  │ 선생님=ALU  │      │
│  │ 책상=레지스터│  │ 책상=레지스터│  │ 책상=레지스터│      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                           │
│  ← CPU = 건물 전체 (물리적 칩 1개)                        │
│  ← Core = 각 교실 (독립된 처리 단위)                      │
└───────────────────────────────────────────────────────────┘
```

- **CPU** = 마더보드에 꽂히는 물리적 칩 하나. "Intel i9-13900K" 같은 것.
- **Core** = CPU 안에 있는 독립적인 연산 엔진. 각자 ALU, 레지스터를 가짐.
- 현대 CPU: 1개 CPU에 4~24개 코어가 들어있음.

---

### L1 / L2 / L3 캐시 계층

```
                 빠름 ◄──────────────────────► 느림
                 작음 ◄──────────────────────► 큼

Core 0    Core 1    Core 2    Core 3
  │          │         │         │
┌─┴─┐      ┌─┴─┐     ┌─┴─┐     ┌─┴─┐
│L1$│      │L1$│     │L1$│     │L1$│  ← 32~64 KB, 4~5 사이클
│I+D│      │I+D│     │I+D│     │I+D│    (코어 전용, 가장 빠름)
└─┬─┘      └─┬─┘     └─┬─┘     └─┬─┘
┌─┴─┐      ┌─┴─┐     ┌─┴─┐     ┌─┴─┐
│L2$│      │L2$│     │L2$│     │L2$│  ← 256 KB~1 MB, 12~15 사이클
└─┬─┘      └─┬─┘     └─┬─┘     └─┬─┘   (코어 전용 or 2개 공유)
  └──────────┴──────────┴─────────┘
                    │
           ┌────────┴────────┐
           │  Shared L3$     │          ← 6~32 MB, 40~50 사이클
           │ (모든 코어 공유) │            (전체 코어 공유)
           └────────┬────────┘
                    │
           ┌────────┴────────┐
           │      DRAM       │          ← GB~TB, 200~300 사이클
           │  (Main Memory)  │
           └─────────────────┘
```

| 캐시 층 | 크기 | 접근 시간 | 공유 범위 | 역할 |
|---------|------|-----------|----------|------|
| L1 | 32~64 KB | 4~5 사이클 | 코어 전용 | 가장 자주 쓰는 데이터 |
| L2 | 256 KB~1 MB | 12~15 사이클 | 코어 전용 | L1 미스 시 두 번째 시도 |
| L3 | 6~32 MB | 40~50 사이클 | 전체 코어 공유 | 코어 간 데이터 공유 지점 |
| DRAM | GB~TB | 200~300 사이클 | 시스템 전체 | 실제 메모리 |

---

### MESI 프로토콜: 4가지 상태

```
┌──────────────────────────────────────────────────────────────┐
│              MESI 상태 스티커                                │
│                                                              │
│  🔴 M (Modified)  : 나만 갖고 있고, 내 버전이 최신 (수정됨) │
│  🟡 E (Exclusive) : 나만 갖고 있고, 원본과 동일             │
│  🟢 S (Shared)    : 다른 코어도 같은 내용 갖고 있음         │
│  ⚫ I (Invalid)   : 내 복사본은 구버전, 못 씀               │
└──────────────────────────────────────────────────────────────┘
```

### 두 코어가 같은 변수 x를 읽고 쓸 때 - 단계별 시나리오

#### Step 1: Core 0이 x를 읽음 (Read Miss → Load from L3)

```
Core 0: "x 값 줘!" → L1$ miss → L2$ miss → L3에서 로드

Core 0 L1$: [x=0, 🟡E]     Core 1 L1$: [없음]

→ 나만 갖고 있으니 Exclusive (E)
```

#### Step 2: Core 1도 x를 읽음 (Read → Shared로 다운그레이드)

```
Core 1: "x 값 줘!" → Coherency Bus에 요청
Core 0: "나한테 있어!" → 값 제공 + E → S 로 다운그레이드

Core 0 L1$: [x=0, 🟢S]     Core 1 L1$: [x=0, 🟢S]

→ 둘 다 같은 값, Shared (S)
```

#### Step 3: Core 0이 x = 1로 쓰기 (Write → Invalidate 전파)

```
Core 0: "x = 1로 바꿀게!" → RFO (Request For Ownership) 전송
Bus: Core 1에게 "Invalidate 신호!" 전송
Core 1: 내 캐시라인 → ⚫I (Invalid) 로 변경

Core 0 L1$: [x=1, 🔴M]     Core 1 L1$: [x=?, ⚫I]

→ Core 0만 최신값 보유, Modified (M)
```

#### Step 4: Core 1이 x를 다시 읽으려 함 (Cache Miss → 동기화)

```
Core 1: "x 읽기!" → Cache Miss (Invalid 상태)
Core 0: L3에 x=1 write-back → M → S 로 전환
Core 1: L3에서 x=1 로드 → I → S 로 전환

Core 0 L1$: [x=1, 🟢S]     Core 1 L1$: [x=1, 🟢S]

→ 다시 동기화 완료
```

#### 전체 MESI 상태 전이 다이어그램

```
                    다른 코어도 읽음
         ┌──────── S ←──────────────────┐
         │         │                   │
    내가 쓰기       │ 다른 코어 읽음    │
         │    Invalidate               │
         ▼         ▼                   │
    M ──────────► I ──── 내가 읽음 ──► E
    │             │                   │
    │  다른 코어가  │                   │ 내가 씀
    │  읽기 요청   ▼                   │
    └──────────► S                    │
                               M ◄───┘
```

> 💡 **핵심 인사이트**
>
> - 캐시는 빠른 임시 복사본이다. 복사본이 여러 개면 동기화 문제가 생긴다.
> - MESI는 "내 복사본이 최신인지, 독점인지, 공유 중인지, 무효인지" 를 추적한다.
> - **False Sharing**: 변수 A와 B가 우연히 같은 캐시라인(64바이트)에 있으면, A를 고칠 때 B를 가진 코어도 Invalidate 신호를 받는다. 성능 대폭 저하!

---

## Q3: 메모리 버스 잠금 — "공용 전화기 점유하기"

### 🎯 현실 비유: 학교 공용 전화기

학교에 전화기가 하나뿐이다. 여러 학생이 동시에 쓰려고 하면 혼선이 생긴다.

- **메모리 버스** = 공용 전화기 선로
- **LOCK 접두어** = "통화 중" 팻말을 걸고 다 쓸 때까지 아무도 못 씀
- **캐시 잠금** = 전화기 선로 전체가 아닌, 내 전화기 번호만 잠금

---

### 메모리 버스의 물리적 구조

```
┌─────────────────────────────────────────────────────────────┐
│                    CPU Package                               │
│                                                             │
│  Core 0    Core 1    Core 2    Core 3                       │
│    │          │         │         │                         │
│    └──────────┴─────────┴─────────┘                        │
│                         │                                   │
│    ┌────────────────────────────────────┐                  │
│    │         Internal Bus               │                  │
│    │  ┌──────────┐ ┌──────────┐        │                  │
│    │  │ 주소 버스 │ │ 데이터   │        │                  │
│    │  │(어디?)   │ │ 버스     │        │                  │
│    │  │          │ │(무엇?)   │        │                  │
│    │  └──────────┘ └──────────┘        │                  │
│    │  ┌──────────┐                     │                  │
│    │  │ 제어 버스 │ (읽기? 쓰기? LOCK?)  │                  │
│    │  └──────────┘                     │                  │
│    └────────────────────────────────────┘                  │
│                         │                                   │
│              Memory Controller (IMC)                        │
└─────────────────────────────────────────────────────────────┘
                          │
                    DDR DRAM
```

---

### LOCK 접두어: 버스 잠금 vs 캐시 잠금

#### 고전적 방법: 버스 잠금 (Bus Lock) — 구형 CPU

```
Core 0                    Bus                    Core 1, 2, 3
  │                        │                         │
  ├── LOCK 신호 전송 ──────►│                         │
  │                        │◄── "버스 전체 잠금!"     │
  │ (읽기 → 계산 → 쓰기)  │   다른 코어 모두 대기!  │
  ├── 완료 신호 ───────────►│                         │
  │                        │──── 버스 잠금 해제 ─────►│
```

**문제점:** 버스 전체를 잠그면 다른 코어가 메모리에 전혀 접근 못 함.

#### 현대 최적화: 캐시 잠금 (Cache Lock) — 현대 CPU

```
Core 0 L1$           Coherency Bus           Core 1 L1$
    │                      │                     │
    ├─ 캐시라인만 잠금! ───►│                     │
    │  x 읽기              │  Core 1은 다른       │
    │  x+1 계산            │  캐시라인 접근 가능! │
    │  x 쓰기              │  (버스 전체 안 막음) │
    ├─ Invalidate 전송 ────►│─────────────────────►│
    │  [x=1, M 상태]        │              [x=?, I]│
```

### 캐시 잠금 가능 조건

```
┌──────────────────────────────────────────────────────────┐
│  캐시 잠금 가능 조건                                      │
│  ✅ 대상 메모리가 L1/L2/L3 캐시에 있음                   │
│  ✅ 캐시라인 경계를 넘지 않는 정렬된 주소                 │
│  ✅ WB(Write-Back) 메모리 타입                           │
│                                                          │
│  버스 잠금 폴백 조건                                      │
│  ❌ 캐시 미스 (데이터가 DRAM에만 있음)                   │
│  ❌ 비정렬 주소 (캐시라인 경계 걸침)                     │
│  ❌ UC(Uncacheable) 메모리 타입 (MMIO 등)                │
└──────────────────────────────────────────────────────────┘
```

### False Sharing 방지: C 코드

```c
#include <stdatomic.h>

// 나쁜 예: counter_a와 counter_b가 같은 캐시라인(64바이트)에!
struct bad_counters {
    atomic_long counter_a;  // 0~7 바이트
    atomic_long counter_b;  // 8~15 바이트
};

// 좋은 예: 패딩으로 캐시라인 분리
struct good_counters {
    atomic_long counter_a;
    char pad[56];           // 64 - 8 = 56 바이트 패딩
    atomic_long counter_b;
};
```

> 💡 **핵심 인사이트**
>
> - LOCK 접두어는 "이 읽기-수정-쓰기를 쪼갤 수 없게 해줘!" 라는 CPU 명령이다.
> - 현대 CPU는 캐시 잠금으로 최적화: 버스 전체가 아닌 캐시라인만 잠근다.
> - 캐시라인(64바이트) 경계를 잘 관리하면 False Sharing을 막아 성능을 크게 높일 수 있다.

---

## Q4: CPU 전체 구조 — "거대한 공장의 설계도"

### 🎯 현실 비유: 자동차 공장

> - **CPU Package** = 공장 건물 전체
> - **Core** = 각 조립 라인 (독립적으로 차 만듦)
> - **L1 캐시** = 조립 라인 옆 작은 부품함
> - **L3 캐시** = 공장 중앙 창고 (모든 라인이 공유)
> - **DRAM** = 공장 밖 대형 물류창고

### 멀티코어 CPU 전체 아키텍처

```
╔══════════════════════════════════════════════════════════════════╗
║                        CPU Package                               ║
║                                                                  ║
║  ┌─────────────────────┐    ┌─────────────────────┐             ║
║  │       Core 0        │    │       Core 1        │             ║
║  │  ┌───────────────┐  │    │  ┌───────────────┐  │             ║
║  │  │   Front End   │  │    │  │   Front End   │  │             ║
║  │  │ (명령어 인출)  │  │    │  │ (명령어 인출)  │  │             ║
║  │  └───────┬───────┘  │    │  └───────┬───────┘  │             ║
║  │  ┌───────▼───────┐  │    │  ┌───────▼───────┐  │             ║
║  │  │   Back End    │  │    │  │   Back End    │  │             ║
║  │  │ ┌───┐ ┌─────┐ │  │    │  │ ┌───┐ ┌─────┐ │  │             ║
║  │  │ │ALU│ │ FPU │ │  │    │  │ │ALU│ │ FPU │ │  │             ║
║  │  │ └───┘ └─────┘ │  │    │  │ └───┘ └─────┘ │  │             ║
║  │  │ ┌───────────┐ │  │    │  │ ┌───────────┐ │  │             ║
║  │  │ │ 레지스터   │ │  │    │  │ │ 레지스터   │ │  │             ║
║  │  │ │ 파일 (RF) │ │  │    │  │ │ 파일 (RF) │ │  │             ║
║  │  │ └───────────┘ │  │    │  │ └───────────┘ │  │             ║
║  │  └───────────────┘  │    │  └───────────────┘  │             ║
║  │  ┌────────┐ ┌─────┐ │    │  ┌────────┐ ┌─────┐ │             ║
║  │  │ L1 I$ │ │L1 D$│ │    │  │ L1 I$ │ │L1 D$│ │             ║
║  │  │ 32KB  │ │ 32KB│ │    │  │ 32KB  │ │ 32KB│ │             ║
║  │  └────────┘ └─────┘ │    │  └────────┘ └─────┘ │             ║
║  │  ┌───────────────┐  │    │  ┌───────────────┐  │             ║
║  │  │     L2 $      │  │    │  │     L2 $      │  │             ║
║  │  │    512 KB     │  │    │  │    512 KB     │  │             ║
║  │  └───────────────┘  │    │  └───────────────┘  │             ║
║  └──────────┬──────────┘    └──────────┬──────────┘             ║
║             │                          │                         ║
║  ┌──────────┴──────────────────────────┴──────────┐             ║
║  │              Ring Bus / Mesh Network            │             ║
║  │     (코어 간 통신 + 캐시 일관성 프로토콜)        │             ║
║  └──────────────────────┬──────────────────────────┘             ║
║                         │                                        ║
║  ┌──────────────────────┴──────────────────────────┐             ║
║  │              Shared L3 Cache (16~32 MB)         │             ║
║  └──────────────────────┬──────────────────────────┘             ║
║                         │                                        ║
║  ┌──────────────────────┴──────────────────────────┐             ║
║  │           Integrated Memory Controller (IMC)    │             ║
║  └──────────────────────┬──────────────────────────┘             ║
╚════════════════════════╪═════════════════════════════════════════╝
                         │
                    DDR DRAM (16GB~1TB)
```

### 이 구조와 Atomic 연산의 연결

```
┌────────────────────────┬───────────────────────────────────────┐
│ 애플리케이션 코드       │ atomic_fetch_add(), mutex_lock()      │
├────────────────────────┼───────────────────────────────────────┤
│ C11 표준 라이브러리     │ <stdatomic.h>, memory_order           │
├────────────────────────┼───────────────────────────────────────┤
│ 컴파일러               │ 재배치 방지, 올바른 명령어 선택         │
├────────────────────────┼───────────────────────────────────────┤
│ CPU 명령어              │ LOCK XADD, LOCK CMPXCHG, MFENCE      │
├────────────────────────┼───────────────────────────────────────┤
│ 캐시 / MESI 프로토콜    │ 캐시라인 잠금, Invalidate 전파        │
├────────────────────────┼───────────────────────────────────────┤
│ 메모리 버스             │ 버스 잠금 (폴백), 버스 중재            │
├────────────────────────┼───────────────────────────────────────┤
│ DRAM                   │ 최종 데이터 저장                       │
└────────────────────────┴───────────────────────────────────────┘
```

> 💡 **핵심 인사이트**: CPU는 공장이다: 코어(생산 라인) → L1/L2(현장 창고) → L3(중앙 창고) → DRAM(외부 물류). Atomic 연산은 이 계층 전체에 걸쳐 동작한다.

---

---

# Part 2: Atomic Operations 심화 Q&A

---

## Q5: Linux 커널 Atomic API 전체 목록

### 🎯 현실 비유

학교 도서관의 "대출 시스템"이라고 생각해봐. 책을 빌릴 때 사서가 해주는 일들이 있어 — 책 읽기(read), 책 넣기(set), 책 수 세기(add/inc), 그리고 "이 책이 여기 있으면 가져가"(CAS).

### API 전체 목록 + 메모리 배리어 포함 여부

| 분류 | API | 반환값 | 메모리 배리어 | 설명 |
|------|-----|--------|--------------|------|
| **읽기** | `atomic_read(v)` | int | ❌ 없음 | 현재 값 읽기 |
| **쓰기** | `atomic_set(v, i)` | void | ❌ 없음 | 값 설정 |
| **산술** | `atomic_add(i, v)` | void | ❌ 없음 | v += i |
| **산술** | `atomic_sub(i, v)` | void | ❌ 없음 | v -= i |
| **산술** | `atomic_inc(v)` | void | ❌ 없음 | v++ |
| **산술** | `atomic_dec(v)` | void | ❌ 없음 | v-- |
| **산술+반환** | `atomic_add_return(i, v)` | int | ✅ Full barrier | v += i 후 새 값 반환 |
| **산술+반환** | `atomic_sub_return(i, v)` | int | ✅ Full barrier | v -= i 후 새 값 반환 |
| **산술+반환** | `atomic_inc_return(v)` | int | ✅ Full barrier | v++ 후 새 값 반환 |
| **산술+반환** | `atomic_dec_return(v)` | int | ✅ Full barrier | v-- 후 새 값 반환 |
| **테스트** | `atomic_dec_and_test(v)` | bool | ✅ Full barrier | v-- 후 0인지 테스트 |
| **테스트** | `atomic_inc_and_test(v)` | bool | ✅ Full barrier | v++ 후 0인지 테스트 |
| **테스트** | `atomic_sub_and_test(i, v)` | bool | ✅ Full barrier | v -= i 후 0인지 테스트 |
| **테스트** | `atomic_add_negative(i, v)` | bool | ✅ Full barrier | v += i 후 음수인지 |
| **CAS** | `atomic_cmpxchg(v, old, new)` | int | ✅ Full barrier | 이전 값 반환 |
| **CAS** | `atomic_try_cmpxchg(v, old, new)` | bool | ✅ Full barrier | 성공 여부 반환 |
| **교환** | `atomic_xchg(v, new)` | int | ✅ Full barrier | 이전 값 반환하며 교체 |

> 규칙: **"반환값이 있는 연산"은 반드시 Full barrier 포함**. 값을 읽어야 하니까 다른 CPU의 쓰기가 반영돼야 하기 때문.

### 비트 연산 API

| API | 배리어 | 설명 |
|-----|--------|------|
| `set_bit(nr, addr)` | ❌ | nr번 비트 Set |
| `clear_bit(nr, addr)` | ❌ | nr번 비트 Clear |
| `test_and_set_bit(nr, addr)` | ✅ | 이전 값 반환하며 Set |
| `test_and_clear_bit(nr, addr)` | ✅ | 이전 값 반환하며 Clear |
| `test_bit(nr, addr)` | ❌ | 읽기만 |

### 변형 타입

```
  atomic_t (32비트)          atomic64_t (64비트)
  ─────────────────          ─────────────────────
  atomic_read(v)     ←→      atomic64_read(v)
  atomic_set(v, i)   ←→      atomic64_set(v, i)
  atomic_add(i, v)   ←→      atomic64_add(i, v)
  atomic_cmpxchg(…)  ←→      atomic64_cmpxchg(…)

  atomic_long_t은 아키텍처에 따라 자동으로 32/64비트 선택
```

> 💡 **핵심 인사이트**: `atomic_read` / `atomic_set`에 배리어가 없는 건 설계상 의도다. 성능을 위해 relaxed 읽기/쓰기를 허용하고, 배리어가 필요한 곳은 `smp_rmb()` / `smp_wmb()`를 명시적으로 추가하도록 개발자에게 책임을 준다.

---

## Q6: Lock-free 큐의 동작 원리 (CAS 기반)

### 🎯 현실 비유

학교 급식 줄을 상상해봐. 보통은 선생님(Lock)이 서서 "너 들어와, 너 기다려"라고 제어해. Lock-free 큐는 **선생님 없이** 학생들이 알아서 "지금 내 앞이 비어있으면 내가 들어갈게"라고 스스로 확인하고 움직이는 방식이야.

### Michael-Scott Lock-free 큐 알고리즘

```
  초기 상태: dummy → None
             Head=dummy, Tail=dummy

  [Enqueue: "A" 삽입]
  Step 1: new_node("A") 생성
  Step 2: tail.next 읽기 → None 확인
  Step 3: CAS(tail.next, None, new_node)
          ┌── 성공 → tail.next = new_node
          └── 실패 → tail 다시 읽고 재시도
  Step 4: CAS(tail, old_tail, new_node)  ← tail 포인터 업데이트

  [Dequeue: "A" 꺼내기]
  Step 1: head 읽기 = dummy
  Step 2: next = head.next = A
  Step 3: CAS(head, dummy, A)
          ┌── 성공 → A.value 반환
          └── 실패 → 다른 스레드가 먼저 dequeue, 재시도
```

### Python 구현 예제

```python
import threading
import time
from typing import Optional, Any

class Node:
    def __init__(self, value=None):
        self.value = value
        self.next = None

class LockFreeCASSimulator:
    """CAS 시뮬레이션 (Python에는 진짜 CAS가 없어서 Lock으로 시뮬레이션)"""
    def __init__(self):
        self._cas_lock = threading.Lock()

    def compare_and_swap(self, obj, attr, expected, new_val) -> bool:
        with self._cas_lock:
            current = getattr(obj, attr)
            if current is expected:
                setattr(obj, attr, new_val)
                return True
            return False

class LockFreeQueue:
    def __init__(self):
        self._cas = LockFreeCASSimulator()
        dummy = Node()
        self._head = dummy
        self._tail = dummy

    def enqueue(self, value):
        new_node = Node(value=value)
        while True:
            tail = self._tail
            next_node = tail.next
            if tail is not self._tail:
                continue
            if next_node is None:
                if self._cas.compare_and_swap(tail, 'next', None, new_node):
                    self._cas.compare_and_swap(self, '_tail', tail, new_node)
                    return
            else:
                # Helping mechanism: 다른 스레드의 tail 업데이트 도와줌
                self._cas.compare_and_swap(self, '_tail', tail, next_node)

    def dequeue(self) -> Optional[Any]:
        while True:
            head = self._head
            tail = self._tail
            next_node = head.next
            if head is not self._head:
                continue
            if head is tail:
                if next_node is None:
                    return None  # 큐 비어있음
                self._cas.compare_and_swap(self, '_tail', tail, next_node)
            else:
                value = next_node.value
                if self._cas.compare_and_swap(self, '_head', head, next_node):
                    return value
```

### 실무에서 Lock-free 큐가 쓰이는 곳

| 사용처 | 이유 |
|--------|------|
| **로그 버퍼** | 초고속 로깅 (Lock 없이 append) |
| **LMAX Disruptor** | 금융 거래소 초저지연 메시지 패싱 |
| **NIC 드라이버 수신 큐** | 커널 내부 네트워크 패킷 큐 |
| **실시간 오디오/영상** | 지연 없는 프레임 버퍼 교환 |

> 💡 **핵심 인사이트**: Lock-free는 "절대 블록 안 됨"이 보장된다. 단, 구현이 복잡하고 ABA 문제 등 함정이 많다.

---

## Q7: 통계 카운터의 Atomic 처리 방식

### 🎯 현실 비유

학교 매점에서 오늘 얼마나 팔렸는지 세는 방법. 방법 1: 판매할 때마다 선생님(Lock)에게 보고. 방법 2: 점원마다 개인 노트에 적다가(per-CPU), 마감 때 합산.

### Python 세 가지 카운터 비교

```python
import threading
import time

# 방법 1: Lock 사용 (안전하지만 느림)
class LockCounter:
    def __init__(self):
        self._count = 0
        self._lock = threading.Lock()
    def increment(self):
        with self._lock:
            self._count += 1

# 방법 2: per-Thread 카운터 (가장 빠름!)
class PerThreadCounter:
    def __init__(self):
        self._local = threading.local()
        self._global = 0
        self._lock = threading.Lock()

    def increment(self):
        if not hasattr(self._local, 'count'):
            self._local.count = 0
        self._local.count += 1
        if self._local.count % 1000 == 0:
            self.flush()

    def flush(self):
        local_val = self._local.count
        with self._lock:
            self._global += local_val
        self._local.count = 0
```

### per-CPU 카운터 개념

```
  일반 Atomic 카운터:              per-CPU 카운터:
  CPU 0  CPU 1  CPU 2  CPU 3      CPU 0  CPU 1  CPU 2  CPU 3
    │      │      │      │          │      │      │      │
    └──────┴──────┴──────┘        [cnt0] [cnt1] [cnt2] [cnt3]
              │                     └──────┴──────┴──────┘
          [단일 카운터]                       │ (주기적 합산)
          캐시라인 핑퐁!               [global_sum]
                                    경합 없음! ✅
```

> 💡 **핵심 인사이트**: per-CPU 카운터는 약간의 지연을 허용하는 대신 극한의 성능을 낸다. Linux 커널의 `percpu_counter`가 바로 이 방식이다.

---

## Q8: ABA 문제와 버전 카운터

### 🎯 현실 비유

친구 필통을 빌리려는데, 눈 깜빡하는 사이에 다른 친구가 그 필통을 가져갔다가 돌려놨어. 겉보기엔 같은 필통(A→B→A), 근데 안에 있던 펜이 바뀌었어!

### ABA 시나리오 (Lock-free 스택)

```
  초기 스택: Top → [A] → [B] → [C] → None

  T=0  Thread 1: old_top = A 읽음
  T=1  (잠시 멈춤 — 선점됨)
  T=2  Thread 2: A pop → B pop → A push (A.next = C 로 바뀜!)
  T=5  Thread 1: CAS(top, A, B) 시도 → top이 A이므로 성공!
       → 근데 B는 이미 free! 💥 Dangling pointer!
```

### 버전 카운터(Tagged Pointer)로 해결

```
  Tagged Pointer 구조 (64비트 시스템):
  ┌─────────────────────────────┬──────────────────┐
  │  48비트 포인터              │  16비트 버전      │
  └─────────────────────────────┴──────────────────┘

  T=0  Thread 1: old = (A, version=1) 읽음
  T=2  Thread 2: ABA 생성 → (A, version=4)
  T=5  Thread 1: CAS((A, ver=1), (A, ver=4)) → 버전 다름! 실패! ✅
```

### 언어별 지원

| 언어 | 해결책 | 직접 구현? |
|------|--------|-----------|
| Java | `AtomicStampedReference` (내장) | ❌ 내장 |
| C++ | 직접 tagged pointer 구현 필요 | ✅ 직접 |
| Rust | `crossbeam-epoch` (epoch-based) | ❌ 라이브러리 |
| Linux 커널 | RCU(Read-Copy-Update)로 우회 | ❌ 커널 제공 |
| Python | GIL + 고수준 자료구조로 거의 없음 | N/A |

> 💡 **핵심 인사이트**: ABA 문제는 **객체 재사용**과 **CAS의 값 동등성 가정**이 충돌할 때 발생한다. C로 커널/시스템 프로그래밍을 할 때는 반드시 이해해야 한다.

---

## Q9: 캐시라인 경합과 ~2.5-3M ops/sec 포화

### 🎯 현실 비유

학교 식당에 음식 트레이가 한 줄에 4개씩 묶여 있어. 내가 트레이 1번을 가져가려면 옆에 있는 2, 3, 4번도 같이 들고 가야 해 (캐시라인). 다른 친구도 트레이 2번 가져가려고 해. 서로 "내 거야" 하면서 싸우는 게 캐시라인 경합이야.

### ~2.5-3M ops/sec 포화의 의미

```
  Best case (L1 Hit, No Contention):
  LOCK CMPXCHG → L1 캐시 히트: ~4 사이클 → ~750M ops/sec

  Contended (여러 CPU가 같은 캐시라인 경쟁):
  LOCK CMPXCHG → RFO + MESI 교신: ~40-100 ns/op
  → 포화점: ~2.5-3M ops/sec (하드웨어 한계)

  직관적 의미:
  - 고성능 웹서버(100K RPS): 초당 100K CAS → 충분
  - 금융 거래소(1M TPS): 포화 위험!
```

### 완화 방법

```python
# 패딩으로 캐시라인 격리
class PaddedCounter:
    def __init__(self, n_threads):
        self.counters = [{'value': 0, 'padding': bytearray(56)}
                         for _ in range(n_threads)]

    def increment(self, thread_id):
        self.counters[thread_id]['value'] += 1

    @property
    def total(self):
        return sum(c['value'] for c in self.counters)
```

> 💡 **핵심 인사이트**: 2.5-3M ops/sec는 **하드웨어 한계**다. 이 한계를 넘으려면 per-CPU 카운터로 분산해야 한다.

---

## Q10: No syscall vs CPU 스핀 소모 상관관계

### 🎯 현실 비유

화장실이 사용 중일 때 두 가지 방법:
- **방법 1(syscall)**: 선생님에게 "비면 알려주세요"라고 말하고 교실에서 딴 거 해(sleep)
- **방법 2(스핀)**: 화장실 앞에서 계속 "다 됐어? 다 됐어?" 물어보기(busy waiting)

### 스핀 vs Sleep Trade-off

```
┌──────────────────┬─────────────────┬──────────────────┐
│ 기준             │ Spin (Atomic)   │ Sleep (Mutex)    │
├──────────────────┼─────────────────┼──────────────────┤
│ 대기 시간 짧을 때│ ✅ 유리          │ ❌ syscall 낭비  │
│ 대기 시간 길 때  │ ❌ CPU 낭비      │ ✅ 다른 일 가능  │
│ 코어가 많을 때   │ ✅ 유리          │ △                │
│ 코어가 적을 때   │ ❌ 다른 코어 방해│ ✅ 유리          │
│ 실시간 시스템    │ ✅ 예측 가능     │ ❌ 스케줄러 불확실│
│ 배터리 환경      │ ❌ 전력 낭비     │ ✅ 절전           │
└──────────────────┴─────────────────┴──────────────────┘

황금 법칙:
임계 구역 실행 시간 < 2 × 컨텍스트 스위치 비용 → 스핀이 유리
임계 구역 실행 시간 > 2 × 컨텍스트 스위치 비용 → Sleep이 유리
```

> 💡 **핵심 인사이트**: Atomic ≠ 무조건 CPU 효율. "No syscall"은 커널 진입 비용 없음, "No blocking"은 스레드가 sleep하지 않음. 그러나 CAS 재시도 루프는 CPU를 100% 태우며 spin할 수 있다.

---

## Q11: atomic_read의 stale 값 문제

### 🎯 현실 비유

친구가 칠판에 숫자를 적었어. 근데 너는 아직 멀리서 보고 있어서 "아 99구나"라고 생각했는데, 사실 친구가 방금 100으로 바꿨어. 네가 본 99는 stale(낡은) 값이야.

### 왜 atomic_read에 배리어가 없는가?

```
  설계 철학: 최소 오버헤드

  메모리 배리어 비용:
  배리어 없음:     ~1-4 사이클
  smp_rmb():      ~10-40 사이클
  완전 fence:     ~100+ 사이클

  커널의 판단: "atomic_read는 그냥 값 하나 읽는 거.
  배리어가 필요한지는 문맥에 따라 다르니까,
  필요한 사람이 명시적으로 추가해."
```

### 올바른 해결 (C 커널 API)

```c
/* 문제 있는 코드 */
void producer(void) {
    data = 42;
    atomic_set(&ready, 1);   /* 배리어 없음 → CPU reorder 가능 */
}

/* 올바른 코드 */
void producer(void) {
    data = 42;
    smp_wmb();               /* Write Memory Barrier */
    atomic_set(&ready, 1);
}

int consumer(void) {
    int r = atomic_read(&ready);
    smp_rmb();               /* Read Memory Barrier */
    if (r == 1) return data; /* 이제 최신 data가 보임 */
    return 0;
}
```

> 💡 **핵심 인사이트**: `atomic_read`의 "atomic"은 **읽는 행위가 쪼개지지 않음**을 보장할 뿐, **최신 값이 반영됨**을 보장하지 않는다.

---

## Q12: CAS 재시도 루프에서 backoff 없이 spin 문제

### 🎯 현실 비유

인기 있는 게임 서버에 접속하려고 모든 사람이 동시에 새로고침을 누르면 서버가 더 힘들어져. "잠깐 기다렸다가 눌러" → "더 기다렸다가 눌러" 이렇게 기다리는 시간을 늘려가면(exponential backoff) 서버 부하가 줄고 결국 더 빨리 연결돼.

### Exponential Backoff Python 구현

```python
import threading
import time
import random

_cas_lock = threading.Lock()

def compare_and_swap(container, expected, new_val):
    with _cas_lock:
        if container[0] == expected:
            container[0] = new_val
            return True
        return False

def increment_with_backoff(counter, n_times,
                           base_delay=0.000001,  # 1μs
                           max_delay=0.001):      # 1ms
    total_spins = 0
    for _ in range(n_times):
        delay = base_delay
        while True:
            old = counter[0]
            if compare_and_swap(counter, old, old + 1):
                break
            # Exponential backoff + jitter
            actual_delay = delay * (0.5 + random.random())
            time.sleep(actual_delay)
            delay = min(delay * 2, max_delay)
            total_spins += 1
    return total_spins
```

### Backoff 전략 비교

```
┌──────────────────┬──────────────┬───────────────┬────────────┐
│ 전략             │ 스핀 횟수    │ 레이턴시      │ CPU 낭비   │
├──────────────────┼──────────────┼───────────────┼────────────┤
│ No Backoff       │ 많음         │ 짧음(경합 적을때)│ 높음     │
│ Exponential B/O  │ 적음         │ 가변          │ 낮음       │
│ E/B/O + Jitter   │ 적음         │ 가변, 분산    │ 낮음       │
│ PAUSE 힌트       │ 많음(빠른 회)│ 매우 짧음     │ 낮음(힌트) │
└──────────────────┴──────────────┴───────────────┴────────────┘
```

> 💡 **핵심 인사이트**: Linux 커널의 Mutex가 바로 **Adaptive Mutex** 패턴이다. 처음에는 스핀하다가 일정 시간 후 sleep으로 전환한다.

---

---

# Part 3: Mutex 심화 Q&A

---

## Q13: Wait Queue vs Thread Pool — 뭐가 다른가?

### 🎯 현실 비유

- **Thread Pool** = 병원 의사 팀. 처음부터 5명의 의사가 대기 중. 환자가 오면 즉시 투입, 진료 끝나면 다시 대기실로.
- **Wait Queue** = 응급실 대기자 명단. 의사가 다 바쁠 때 이름을 적어두는 종이. 의사가 한 명 비면 명단 맨 앞 사람을 부르는 것.

```
┌─────────────────────────────────────────────────────────────────┐
│  ┌─────────────────────┐     ┌──────────────────────────────┐   │
│  │    Thread Pool       │     │        Wait Queue            │   │
│  │  (미리 만든 스레드들)  │     │     (커널이 관리하는 대기 목록)  │   │
│  │                      │     │                              │   │
│  │  [T1][T2][T3][T4][T5]│     │  HEAD → [T_a] → [T_b] → NIL│   │
│  │  (재사용 가능한 자원)   │     │  (Mutex 못 잡은 스레드들)    │   │
│  │                      │     │                              │   │
│  │  역할: 작업 실행       │     │  역할: Lock 대기 중 슬립      │   │
│  └─────────────────────┘     └──────────────────────────────┘   │
│          ↑                              ↑                        │
│    유저 공간(라이브러리)           커널 공간(OS 내부)               │
└─────────────────────────────────────────────────────────────────┘
```

| 구분 | Thread Pool | Wait Queue |
|------|-------------|------------|
| **생성 시점** | 미리 생성 | 필요할 때 생성 |
| **위치** | 유저 공간 라이브러리 | 커널 공간 내부 |
| **목적** | 작업 실행 최적화 | Lock/I/O 대기 관리 |
| **사이즈** | 고정 (설정 가능) | 가변 (대기자 수) |

> 💡 **핵심 인사이트**: Thread Pool은 "작업 분배 시스템"이고, Wait Queue는 "대기 줄 관리 시스템"이다. Mutex 경합 시 Thread Pool의 스레드가 Wait Queue에 들어갈 수 있다.

---

## Q14: Futex에서의 Adaptive Spinning

### 🎯 현실 비유

화장실 앞에 도착했는데 사용 중이야. 선택 1: 바로 의자에 앉아서 잠들기(sleep). 선택 2: "곧 나올 것 같은데?" 하면서 잠깐 문 앞에서 기다려보기(spin). 곧 나오면 spin이 이득, 오래 걸리면 sleep이 이득.

### 동작 흐름

```
Lock 시도 (CAS 실패)
       │
       ▼
  Lock 소유자가 현재 CPU에서 실행 중?
  (owner->on_cpu == 1)
       │
  ┌────┴────┐
  │ YES     │ NO
  ▼         ▼
 SPIN      즉시 SLEEP
 (잠깐 CAS  (FUTEX_WAIT)
  반복)
  │
  ├─ 성공 → Lock 획득!
  └─ 실패 (스핀 한계 초과) → SLEEP
```

| 상황 | Spin | Sleep |
|------|------|-------|
| Lock 보유 시간 < context switch 비용 (~2-10μs) | ✅ 이득 | ❌ 낭비 |
| Lock 보유 시간 > context switch 비용 | ❌ CPU 낭비 | ✅ 이득 |
| Lock 소유자가 sleep 중 | ❌ 무한 spin | ✅ 바로 양보 |

> 💡 **핵심 인사이트**: Adaptive spinning은 "Lock 소유자의 상태를 보고 전략을 바꾸는" 지능적인 최적화다.

---

## Q15: Thread 라이프사이클

### 🎯 현실 비유

- **Thread Pool 없을 때** = 알바생. 일이 생기면 채용하고, 끝나면 해고. 매번 채용/해고 비용 발생.
- **Thread Pool 있을 때** = 정규직. 한 번 뽑으면 계속 대기하다가 일이 오면 처리.

```
Thread Pool 없을 때:
  [생성]→[READY]→[RUNNING]→[완료]→[소멸] (매번 반복)
          ~50-100μs        작업         ~10μs

Thread Pool 있을 때:
  [생성]→[READY]→[RUNNING]→[작업 완료]→[READY]→[RUNNING]→ ...
          한 번만         작업 1         재사용!   작업 2
```

```python
# Thread Pool 비교
import threading
import concurrent.futures
import time

# Pool 없이: 매번 새 Thread
def no_pool(n_tasks):
    threads = []
    for i in range(n_tasks):
        t = threading.Thread(target=lambda: time.sleep(0.001))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

# Pool 있음: ThreadPoolExecutor
def with_pool(n_tasks):
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(time.sleep, 0.001) for _ in range(n_tasks)]
        concurrent.futures.wait(futures)
```

---

## Q16: 커널 스레드 vs 유저 스레드

### 🎯 현실 비유

- **커널 스레드** = 학교 공식 동아리. 교감 선생님(OS 스케줄러)이 활동 시간표를 짜줌.
- **유저 스레드** = 비공식 모임. 학교 모르게 학생들끼리 운영. 교감이 관리 안 해줌.

### 매핑 모델

```
1:1 모델 (현대 Linux, Python):
  유저 스레드 ─┐
  유저 스레드 ─┼── 1:1 매핑 ── 커널 스레드
  유저 스레드 ─┘               (OS가 스케줄링)

N:1 모델 (Green Thread):
  유저 스레드 ─┐
  유저 스레드 ─┼── N:1 매핑 ── 커널 스레드 (1개!)
  유저 스레드 ─┘               (라이브러리가 스케줄링)

M:N 모델 (Go goroutine):
  유저 스레드(goroutine) ─┐
  유저 스레드(goroutine) ─┼── M:N ── 커널 스레드 (M개)
  유저 스레드(goroutine) ─┘         (Go runtime이 분배)
```

Python의 스레드: **1:1 모델** + GIL. OS 커널 스레드이지만 GIL 때문에 CPU 바운드 병렬성은 제한.

---

## Q17: Mutex CAS 동작 흐름 (state 0→1→2)

### 🎯 현실 비유

번호판 달린 창고 자물쇠. 0번 = 열림, 1번 = 잠김(줄 없음), 2번 = 잠김(줄 있음).

### 전체 흐름

```
┌────────────────────────────────────────────────────────────────┐
│                    Mutex Lock 전체 흐름                           │
│                                                                │
│  Thread A: CAS(state, 0, 1)                                    │
│    │                                                           │
│    ├─ 성공 → state=1, Lock 획득! (Fast Path, syscall 없음)      │
│    │                                                           │
│    └─ 실패 → state가 0이 아님 (이미 잠김)                        │
│       │                                                        │
│       ▼                                                        │
│  Thread B: CAS(state, 1, 2)  ← "대기자 있음" 표시              │
│    │                                                           │
│    └─ FUTEX_WAIT(state, 2) → 커널 대기 큐에서 sleep             │
│                                                                │
│  ─────────── Thread A가 unlock ───────────                     │
│                                                                │
│  Thread A: atomic_fetch_sub(state, 1)                          │
│    │                                                           │
│    ├─ 결과 == 1 (대기자 없음) → state=0, 끝                    │
│    │                                                           │
│    └─ 결과 != 1 (대기자 있음) → state=0 설정                   │
│       │                                                        │
│       └─ FUTEX_WAKE(1) → 대기 큐에서 1명 깨움                  │
│          │                                                     │
│          └─ Thread B: 깨어나서 CAS(state, 0, 2) 재시도          │
│             (실패하면 다시 FUTEX_WAIT)                           │
└────────────────────────────────────────────────────────────────┘
```

---

## Q18: glibc란 무엇인가

### 🎯 현실 비유

glibc는 **OS와 앱 사이의 통역사**. 앱이 "파일 열어줘"라고 하면 glibc가 OS가 이해하는 말(syscall)로 번역해주는 것.

```
Application → glibc → Kernel 호출 흐름:

[Your C Program]
      │ printf("hello")
      ▼
[glibc (libc.so.6)]
      │ write(1, "hello", 5)
      ▼
[Linux Kernel]
      │ sys_write()
      ▼
[Hardware (Terminal)]
```

| C 라이브러리 | 용도 | 크기 |
|-------------|------|------|
| **glibc** | 데스크톱/서버 Linux (Ubuntu, RHEL) | ~10 MB |
| **musl** | Alpine Linux, 경량 컨테이너 | ~1 MB |
| **bionic** | Android | ~2 MB |

---

## Q19: Futex는 Mutex 구현 방법 중 하나? OS별 차이

Futex는 **Linux 전용** 시스템콜이다.

| OS | Mutex 구현 기술 | 핵심 원리 |
|----|---------------|----------|
| **Linux** | futex (Fast Userspace Mutex) | CAS fast path + 커널 대기 큐 |
| **macOS** | psynch (Darwin) | ulock syscall 기반 |
| **Windows** | Critical Section / SRWLock | 유저스페이스 spin + 커널 이벤트 |
| **FreeBSD** | umtx (User-space Mutex) | futex와 유사한 설계 |

> 💡 **핵심 인사이트**: "비경합 시 syscall 없이, 경합 시에만 커널 개입"이라는 설계 철학은 모든 OS에서 동일하다. 이름과 API만 다를 뿐이다.

---

## Q20: RAII 패턴 설명

### 🎯 현실 비유: 도서관 자동 반납 시스템

도서관에서 책을 빌리면 자동으로 반납 일정이 잡히고, 기한이 되면 자동 반납. 예외(비가 오든, 감기에 걸리든) 상관없이 반드시 반환된다.

```python
# Python: with 문 = RAII와 같은 역할
import threading

lock = threading.Lock()

# ❌ 위험: 예외 시 unlock 안 됨
def unsafe():
    lock.acquire()
    risky_operation()  # 여기서 예외 발생하면?
    lock.release()     # 이 줄 실행 안 됨 → Lock 영원히 잠김!

# ✅ 안전: with 문으로 자동 해제
def safe():
    with lock:
        risky_operation()  # 예외 발생해도
    # 자동으로 lock.release() 호출됨!

# with 문의 내부 동작:
# lock.__enter__()  → lock.acquire()
# try:
#     risky_operation()
# finally:
#     lock.__exit__()  → lock.release()
```

```cpp
// C++: std::lock_guard = RAII
{
    std::lock_guard<std::mutex> guard(mutex);
    // guard 객체가 생성되면서 lock 획득
    risky_operation();
    // 스코프 끝나면 guard 소멸자에서 자동 unlock
}  // ← 여기서 guard.~lock_guard() → mutex.unlock()
```

---

## Q21: Deadlock 발생/회피 + Livelock

### 🎯 현실 비유

- **Deadlock** = 외나무다리에서 두 사람이 마주보며 "너 먼저 가" "아니 너 먼저 가"... 둘 다 안 움직임.
- **Livelock** = 복도에서 마주친 두 사람이 같은 방향으로 계속 비켜줌. 둘 다 열심히 움직이지만 전진 없음.

### Deadlock Python 예제

```python
import threading
import time

lock_a = threading.Lock()
lock_b = threading.Lock()

def thread1():
    lock_a.acquire()
    time.sleep(0.1)  # Thread 2에게 lock_b 잡을 시간 줌
    lock_b.acquire()  # ← 여기서 영원히 대기 (Thread 2가 lock_b 보유 중)
    lock_b.release()
    lock_a.release()

def thread2():
    lock_b.acquire()
    time.sleep(0.1)
    lock_a.acquire()  # ← 여기서 영원히 대기 (Thread 1이 lock_a 보유 중)
    lock_a.release()
    lock_b.release()
```

### Deadlock 4가지 필요조건 (Coffman Conditions)

| 조건 | 설명 | 방지법 |
|------|------|--------|
| **상호 배제** | 자원을 동시에 쓸 수 없음 | 공유 가능 자원 사용 |
| **점유 대기** | 하나 들고 다른 거 기다림 | 한 번에 전부 요청 |
| **비선점** | 강제로 빼앗을 수 없음 | timeout 설정 |
| **순환 대기** | A→B→A 원형 대기 | Lock 순서 고정 |

### 회피 전략: Lock 순서 고정

```python
# 올바른 코드: Lock 순서 일관되게 (항상 A → B)
def thread1_safe():
    with lock_a:
        with lock_b:
            do_work()

def thread2_safe():
    with lock_a:  # B 대신 A 먼저!
        with lock_b:
            do_work()
```

### Livelock 예제

```python
import threading
import time
import random

polite_lock_a = threading.Lock()
polite_lock_b = threading.Lock()

def polite_thread(name, first, second):
    for _ in range(10):
        first.acquire()
        if not second.acquire(blocking=False):
            first.release()         # "양보할게!" (다시 놓음)
            time.sleep(random.uniform(0.001, 0.01))  # 잠깐 대기
            continue                # 처음부터 다시
        # 둘 다 획득!
        print(f"{name}: 작업 완료!")
        second.release()
        first.release()
        return
    print(f"{name}: 포기 😢 (Livelock!)")
```

> 💡 **핵심 인사이트**: Deadlock은 "아무도 안 움직이는 상태", Livelock은 "열심히 움직이지만 전진 없는 상태". Livelock 방지에는 random backoff가 효과적.

---

## Q22: Anti-Patterns (God Lock, Lock Convoy)

### God Lock: 하나의 Lock으로 모든 것 보호

```python
# ❌ God Lock: 모든 접근에 하나의 Lock
class GodLockDB:
    def __init__(self):
        self.lock = threading.Lock()  # 전체를 이 Lock 하나로!
        self.users = {}
        self.orders = {}
        self.logs = []

    def add_user(self, user):
        with self.lock:  # User 추가할 때도
            self.users[user.id] = user

    def add_order(self, order):
        with self.lock:  # Order 추가할 때도 같은 Lock!
            self.orders[order.id] = order
            # User 접근도 이 Lock 때문에 대기...

# ✅ Fine-Grained Locking: 자원별 분리된 Lock
class FineGrainedDB:
    def __init__(self):
        self.user_lock = threading.Lock()
        self.order_lock = threading.Lock()
        self.users = {}
        self.orders = {}

    def add_user(self, user):
        with self.user_lock:  # User 전용 Lock
            self.users[user.id] = user

    def add_order(self, order):
        with self.order_lock:  # Order 전용 Lock (병렬 가능!)
            self.orders[order.id] = order
```

### Lock Convoy: 줄 서기 현상

```
Lock Convoy 발생:
  Thread1: [lock][작업 100μs][unlock][lock 시도]→ 줄 뒤에!
  Thread2: [lock][작업 100μs][unlock][lock 시도]→ 줄 뒤에!
  Thread3: [lock][작업 100μs][unlock][lock 시도]→ 줄 뒤에!

  → 마치 버스 정류장에 줄 선 것처럼 순서대로만 처리
  → CPU 코어가 4개인데 실질적으로 1개만 사용!
```

완화 방법: Lock 안에서의 작업량 최소화, 배치 처리, Lock-free 자료구조 고려.

---

---

# Part 4: Semaphore 심화 Q&A

---

## Q23: "동시성 프리미티브" 용어 해설

### 🎯 현실 비유: 요리사와 레고 블록

**Concurrency(동시성)** = 요리사 한 명이 파스타, 샐러드, 빵을 빠르게 번갈아 하니까 "동시에 하는 것처럼" 보이는 것.

**Parallelism(병렬성)** = 요리사 세 명이 각자 진짜로 동시에 만드는 것.

```
Concurrency                           Parallelism
코어 1개, 빠르게 전환                  코어 3개, 진짜 동시

코어1: [파스타][샐러드][빵][파스타]     코어1: [파스타─────────]
                                       코어2: [샐러드─────────]
                                       코어3: [빵─────────────]
```

**Primitive = 레고의 가장 기본 블록**. 더 복잡한 것들의 재료가 된다.

```
고수준 추상화 (Channel, Actor, Condition Variable, ThreadPool)
           ↑ 조합
동시성 프리미티브 (Atomic, Mutex, Semaphore)
           ↑ 구현
하드웨어 / OS 커널 (CAS, futex, syscall)
```

> 💡 **핵심 인사이트**: "프리미티브"는 하드웨어와 고수준 언어 사이의 다리 역할. 직접 쓰기보다는 그것으로 만들어진 고수준 도구를 쓰는 경우가 많지만, 내부를 이해하면 버그를 훨씬 빠르게 잡을 수 있다.

---

## Q24: 실제 DB/RabbitMQ에서 Semaphore 사용 여부

### 🎯 현실 비유: 도서관 대출 카드

도서관에서 대출 카드가 10장뿐이라면, 10명이 빌리고 있으면 11번째 사람은 기다려야 한다.

### RabbitMQ prefetch_count = Semaphore

```
Producer ──▶ [Queue: msg1, msg2, msg3, ...]

Consumer (prefetch_count=3):
  내부 카운터: Semaphore(3)
  msg1 전달 → count: 3→2
  msg2 전달 → count: 2→1
  msg3 전달 → count: 1→0
  msg4 대기 → ⏳ (count=0)
  [Consumer가 msg1 ack] → count: 0→1 → msg4 전달
```

### Python DB 커넥션 풀의 Semaphore

```python
import asyncio
import asyncpg

async def main():
    # pool max_size=5 → 내부적으로 Semaphore(5) 역할
    pool = await asyncpg.create_pool(
        "postgresql://user:pass@localhost/db",
        min_size=2,
        max_size=5  # ← Semaphore의 N 값
    )

    async def query(i):
        async with pool.acquire() as conn:  # ← sem.acquire()
            result = await conn.fetchval("SELECT $1 * 2", i)
        # with 블록 끝에서 자동 반환 (sem.release())
```

> 💡 **핵심 인사이트**: `pool_size`, `prefetch_count`, `max_connections` 같은 설정값들은 **모두 Semaphore의 N 값**이다.

---

## Q25: Semaphore 실제 예제 (Python)

### 기본 사용법

```python
import threading
import time

sem = threading.Semaphore(3)  # 동시에 3개만 허용

def worker(thread_id):
    with sem:  # acquire + release 자동
        print(f"Thread {thread_id}: 작업 중")
        time.sleep(1)
```

### 생산자-소비자 패턴 (BoundedSemaphore)

```python
import threading
from collections import deque

BUFFER_SIZE = 5
buffer = deque()
buffer_lock = threading.Lock()

empty_slots = threading.BoundedSemaphore(BUFFER_SIZE)  # 빈 슬롯 수
filled_slots = threading.Semaphore(0)                   # 채워진 항목 수

def producer(prod_id):
    for i in range(5):
        empty_slots.acquire()          # 빈 슬롯 기다림 (P 연산)
        with buffer_lock:
            buffer.append(f"P{prod_id}-Item{i}")
        filled_slots.release()          # 소비자에게 신호 (V 연산)

def consumer(cons_id):
    for _ in range(5):
        filled_slots.acquire()          # 채워진 항목 기다림 (P 연산)
        with buffer_lock:
            item = buffer.popleft()
        empty_slots.release()           # 생산자에게 빈 슬롯 알림 (V 연산)
```

### asyncio.Semaphore 비교

| 비교 항목 | `threading.Semaphore` | `asyncio.Semaphore` |
|----------|----------------------|---------------------|
| 실행 모델 | 멀티 스레드 | 단일 스레드 이벤트 루프 |
| 블로킹 시 | 스레드가 잠듦 | 다른 코루틴 실행됨 |
| 적합한 작업 | CPU 집약적 | I/O 집약적 |
| 메모리 | 스레드당 ~8MB | 코루틴당 ~수 KB |

---

## Q26: AWS 기반 대기큐 아키텍처 설계

### 🎯 현실 비유: 유명 놀이공원 롤러코스터

- 롤러코스터는 한 번에 **20명**만 탑승 (Lambda Reserved Concurrency)
- 줄을 서면 순서대로 탑승 (SQS Queue)
- 줄이 너무 길면 입장 제한 (Backpressure)

### 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS Cloud                             │
│                                                             │
│  클라이언트 ──▶ API Gateway (Rate Limit: 10,000/s)          │
│                    │                                        │
│                    ▼                                        │
│             Lambda (Handler) ← 요청 검증, SQS 전송          │
│                    │                                        │
│                    ▼                                        │
│            ┌──────────────────┐                             │
│            │    SQS Queue     │ ← Semaphore처럼 작동        │
│            │ [msg1][msg2]...  │                             │
│            └────────┬─────────┘                             │
│                     │ 실패 3번 → Dead Letter Queue           │
│                     ▼                                       │
│  Worker Lambda (Reserved Concurrency = 10) ← Semaphore(10) │
│  ┌──────────────────────────────────────┐                  │
│  │  Instance 1~10 [처리중]              │                  │
│  │  11번째는 Queue에서 대기             │                  │
│  └──────────────┬───────────────────────┘                  │
│                 ▼                                           │
│            DynamoDB (처리 결과 저장)                          │
└─────────────────────────────────────────────────────────────┘
```

### SQS + Lambda = 분산 Semaphore

```
일반 Semaphore              SQS + Lambda
━━━━━━━━━━━━━━━━━━━━━━     ━━━━━━━━━━━━━━━━━━━━━━━━
sem = Semaphore(10)         Reserved Concurrency = 10
sem.acquire()               SQS 메시지 수신 (자동)
작업 수행...                 Worker Lambda 실행...
sem.release()               메시지 delete + 함수 종료
count=0이면 블로킹           동시 10개 초과 시 Queue 대기
```

> 💡 **핵심 인사이트**: SQS + Lambda Reserved Concurrency 조합은 분산 시스템에서 Semaphore의 역할을 클라우드 규모로 확장한 것이다.

---

## Q27: Binary Semaphore vs Mutex: 소유권 차이

### 🎯 현실 비유

**Mutex = 열쇠가 있는 자물쇠** — 열쇠 가진 사람만 열 수 있다.
**Binary Semaphore = 신호등** — 신호를 바꾸는 건 누구나 할 수 있다.

### 소유권 차이로 인한 버그

```python
import threading
import time

sem = threading.Semaphore(1)

def thread_a():
    sem.acquire()
    print("Thread A: 임계 구역 진입")
    time.sleep(3)
    sem.release()

def thread_b():
    time.sleep(1)
    sem.release()  # ← A가 아직 작업 중인데 release! Semaphore는 이걸 허용!

def thread_c():
    time.sleep(1.5)
    sem.acquire()  # B가 release했으니 들어감
    print("Thread C: 임계 구역 진입")  # A와 C가 동시에 진입! 버그!
```

```python
# 올바른 해결: Mutex (threading.Lock) 사용
lock = threading.Lock()

def safe():
    with lock:
        work()  # 예외가 나도 자동 release, 다른 스레드는 release 불가
```

---

## Q28: Mutex ≠ Binary Semaphore 구현 차이

### 종합 비교

| 특성 | Mutex | Binary Semaphore |
|------|-------|-----------------|
| **소유권** | ✅ 있음 | ❌ 없음 |
| **Priority Inheritance** | ✅ 지원 | ❌ 불가 |
| **Recursive Lock** | ✅ 가능 (RLock) | ❌ 데드락 |
| **데드락 감지** | ✅ 일부 지원 | ❌ 어려움 |
| **주 목적** | 상호 배제 | 신호 전달 / 동기화 |
| **다른 스레드 signal** | ❌ 에러 | ✅ 허용 |
| **초기값** | 항상 1 | 0 또는 1 설정 가능 |

### Priority Inheritance (Mutex에만 있는 기능)

```
문제: 우선순위 역전
A(낮음): [lock 획득]─────[작업중]─────[unlock]
B(중간): ────────[실행 중!]──────────────────
C(높음): ──────────[lock 시도]─[기다림!!]────
         → C가 B에게 막힘! "우선순위 역전"

해결: Priority Inheritance
A(낮음): [lock]─[🔼 A를 C 우선순위로 승격]─[빨리 완료]─[unlock]
C(높음): ──────────────────────────────[lock 획득, 바로 실행]
```

> 💡 **핵심 인사이트**: Mutex는 "내 것을 지키는 자물쇠", Semaphore는 "신호를 주고받는 깃발". 소유권이라는 단 하나의 차이가 Priority Inheritance, Recursive Lock, 데드락 감지라는 거대한 기능 차이를 만들어낸다.

---

---

# Part 5: 통합 비교 심화 Q&A

---

## Q29: Mutex의 pshared 속성 / Named Mutex

### 🎯 현실 비유

화장실 잠금장치(Mutex)를 두 건물(프로세스)이 공유하려면, 건물 사이 벽에 구멍을 뚫어서(공유 메모리) 같은 화장실을 쓸 수 있게 만들어야 한다 — 이게 `pshared` 속성이다.

```
┌──────────────────────────┬──────────────────────────────────┐
│  PTHREAD_PROCESS_PRIVATE │  PTHREAD_PROCESS_SHARED          │
│  (기본값)                 │  (명시적 설정 필요)                │
├──────────────────────────┼──────────────────────────────────┤
│  같은 프로세스의 스레드만   │  다른 프로세스도 사용 가능           │
│  스택/힙에 배치 가능        │  반드시 공유 메모리에 배치해야 함      │
└──────────────────────────┴──────────────────────────────────┘
```

### POSIX에는 Named Mutex가 없다!

```
Windows: CreateMutex("my_mutex") → 커널 오브젝트, 이름으로 전역 접근
POSIX:   ❌ Named Mutex 없음!
         대안 1: pshared Mutex + shm (복잡, 소유권 있음)
         대안 2: Named Semaphore (단순, 소유권 없음) ← 권장
```

### 프로세스 간 Mutex vs Named Semaphore

| 비교 | pshared Mutex + shm | Named Semaphore |
|------|--------------------|--------------------|
| 소유권 | ✅ 보장 | ❌ 없음 |
| API 난이도 | ❌ 복잡 (shm 설정) | ✅ 단순 (`sem_open("/name")`) |
| 비정상 종료 시 | ❌ Lock 잠김 위험 | ✅ `sem_unlink()`로 정리 |
| N개 동시 접근 | ❌ 불가 | ✅ 지원 |

> **현실 규칙**: 프로세스 간 동기화가 필요하면 Named Semaphore를 먼저 고려하라.

---

## Q30: Atomic CAS vs Spinlock 상세 비교

### 🎯 현실 비유

- **CAS** = 줄에 한 번 가봐. 빈 자리 있으면 탑승, 없으면 돌아가. **한 번만 시도**.
- **Spinlock** = 자리가 날 때까지 입구에서 계속 들여다봐. **CPU를 태우며 계속 확인**.
- **Mutex** = 번호표 받고 벤치에 **앉아서 기다려**. 연락 오면 일어나서 가.

### C 구현

```c
#include <stdatomic.h>

// Spinlock = CAS를 while 루프로
typedef struct { atomic_flag flag; } Spinlock;

void spinlock_lock(Spinlock *sl) {
    while (atomic_flag_test_and_set_explicit(&sl->flag, memory_order_acquire)) {
        __asm__ volatile("pause" ::: "memory");  // CPU 힌트
    }
}

void spinlock_unlock(Spinlock *sl) {
    atomic_flag_clear_explicit(&sl->flag, memory_order_release);
}
```

### Spinlock 사용 상황

```
인터럽트 핸들러 또는 인터럽트 비활성화 상태?
├─ YES → 반드시 Spinlock (sleep 불가능!)
└─ NO ↓

임계 영역이 매우 짧다? (< context switch 비용 ~2-10μs)
├─ YES → Spinlock 고려
└─ NO  → Mutex 사용
```

> 💡 **핵심 인사이트**: CAS ⊂ Spinlock ⊂ Mutex. 인터럽트 컨텍스트와 아주 짧은 임계 영역이 Spinlock의 유일한 정당한 사용처다.

---

## Q31: Atomic vs Atomic CAS vs Spinlock 관계 정리

### 계층 관계

```
Level 0: Atomic Operation
  단일 CPU 명령어 (atomic_add, XADD, LOCK INC)
  재시도 없음, 그냥 원자적으로 완료
         ↑ 포함 관계
Level 1: Atomic CAS (특별한 Atomic Op)
  "비교 후 조건부 교체" (CMPXCHG, LDREX/STREX)
  재시도 없음, 성공/실패만 반환
         ↑ 사용 관계
Level 2: Spinlock (CAS + while 루프)
  while (CAS fails) { busy wait }
  성공까지 CPU 점유, sleep 없음
```

### "Mutex에서 CAS" vs "Semaphore에서 Spinlock" 핵심 차이

```
┌───────────────────────────┐    ┌─────────────────────────────────────┐
│         Mutex             │    │            Semaphore                │
│                           │    │                                     │
│  CAS = Mutex 잠금을        │    │  Spinlock = Semaphore의 카운터(count)│
│        획득하는 수단         │    │            변수를 보호하는 내부 도구   │
│                           │    │                                     │
│  CAS(0→1) 성공 = Lock 획득  │    │  spin_lock(&sem->lock):             │
│  CAS 실패 = sleep          │    │    sem->count-- 또는 add_to_queue   │
│                           │    │  spin_unlock(&sem->lock)            │
│                           │    │                                     │
│  CAS가 "잠금 획득 그 자체"   │    │  Spinlock이 "카운터 보호용 내부 부품" │
└───────────────────────────┘    └─────────────────────────────────────┘
```

### 전체 동기화 프리미티브 계층도

```
══════════════════════════════════════════════════════════════════
            전체 동기화 프리미티브 계층 구조
══════════════════════════════════════════════════════════════════

Layer 5: 고수준 추상화
┌──────────────────────────────────────────────────────────────┐
│  Python: threading.Lock   Java: synchronized   Go: sync.Mutex │
│  C++: std::mutex          Rust: Mutex<T>                      │
└──────────────────────────────────────────────────────────────┘
                    ↑ wrapping
Layer 4: POSIX API (glibc)
┌──────────────────────────────────────────────────────────────┐
│  pthread_mutex_t                sem_t (POSIX Semaphore)       │
│  Fast path: CAS만              sem_wait / sem_post            │
│  Slow path: futex syscall      내부: futex 또는 커널 호출       │
└──────────────────────────────────────────────────────────────┘
                    ↑ syscall (경합 시)
Layer 3: Kernel Space
┌──────────────────────────────────────────────────────────────┐
│  futex (hash table + wait queue)    Linux Semaphore           │
│  FUTEX_WAIT: sleep                  struct semaphore {        │
│  FUTEX_WAKE: wake                     raw_spinlock_t lock; ←─│─ Spinlock 사용
│                                       unsigned int count;    │
│                                     }                        │
└──────────────────────────────────────────────────────────────┘
                    ↑ 기반
Layer 2: Atomic CAS
┌──────────────────────────────────────────────────────────────┐
│  단발 비교+교체, 재시도 없음                                    │
│  Mutex fast path 획득, Spinlock 루프의 핵심, Lock-free 구조    │
└──────────────────────────────────────────────────────────────┘
                    ↑ 기반
Layer 1: Atomic Operations
┌──────────────────────────────────────────────────────────────┐
│  atomic_add, atomic_inc, XCHG, CAS도 이것의 한 종류           │
└──────────────────────────────────────────────────────────────┘
                    ↑ 기반
Layer 0: Hardware (CPU)
┌──────────────────────────────────────────────────────────────┐
│  x86: LOCK CMPXCHG, LOCK XADD    ARM: LDREX/STREX           │
│  MESI Cache Coherency Protocol    Memory Bus Lock             │
└──────────────────────────────────────────────────────────────┘

══════════════════════════════════════════════════════════════════
                      핵심 관계 요약
══════════════════════════════════════════════════════════════════

  Hardware LOCK CMPXCHG
       │
       ▼
  Atomic CAS ──────────────────────────────────────┐
       │                                           │
       ├──[루프로 감싸면]──▶ Spinlock               │
       │                       │                  │
       │              [커널 내부에서 사용]           │
       │                       ▼                  │
       │                Linux Semaphore의          │
       │                raw_spinlock_t             │
       │                (count 보호)               │
       │                                          │
       └──[fast path로 사용]──▶ Mutex (futex)      │
                                    │             │
                          [경합 시 커널]            │
                                    ▼             │
                              FUTEX_WAIT/WAKE ◄───┘
══════════════════════════════════════════════════════════════════
```

> 💡 **핵심 인사이트**: 동기화 프리미티브의 모든 계층은 결국 Hardware CAS 명령어 하나 위에 쌓인 추상화다. **Mutex에서 CAS는 잠금 획득 그 자체**이고, **Semaphore에서 spinlock은 카운터를 보호하는 내부 부품**이다.

---

## 📎 Sources

1. [Lockless Patterns: Compare-and-Swap — LWN.net](https://lwn.net/Articles/847973/) — 기술 기사
2. [Linux Kernel Atomic Operations](https://www.kernel.org/doc/html/v4.12/core-api/atomic_ops.html) — 공식 커널 문서
3. [Basics of Futexes — Eli Bendersky](https://eli.thegreenplace.net/2018/basics-of-futexes/) — 기술 블로그
4. [futex(7) — Linux Manual](https://man7.org/linux/man-pages/man7/futex.7.html) — 공식 man page
5. [sem_overview(7) — Linux Manual](https://man7.org/linux/man-pages/man7/sem_overview.7.html) — 공식 man page
6. [atomic_t Wrappers — kernel.org](https://docs.kernel.org/core-api/wrappers/atomic_t.html) — 공식 커널 문서
7. [pthread_mutexattr_setpshared(3) — man7.org](https://man7.org/linux/man-pages/man3/pthread_mutexattr_setpshared.3.html) — 공식 man page
8. [Spinlocks and Read-Write Locks — kernel.org](https://docs.kernel.org/locking/spinlocks.html) — 공식 커널 문서
9. [A futex overview and update — LWN.net](https://lwn.net/Articles/360699/) — 기술 기사
10. [Robust Futexes — kernel.org](https://docs.kernel.org/locking/robust-futexes.html) — 공식 커널 문서
11. [std::memory_order — cppreference](https://en.cppreference.com/w/cpp/atomic/memory_order) — 참조 문서
