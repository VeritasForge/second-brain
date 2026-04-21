---
created: 2026-04-21
source: claude-code
tags: [golang, architecture, runtime, compiler, gc, memory, linker, binary, ssa, escape-analysis]
---

# 📖 Go 아키텍처와 런타임 — 소스코드에서 실행까지

> 💡 **한줄 요약**: Go의 아키텍처는 "컴파일러 + 런타임 + 표준 라이브러리"의 삼각 구조로, 런타임이 GC/스케줄러/네트워크 폴러를 내장하여 별도 VM 없이 단일 바이너리로 동작하며, 이 구조가 Go의 성능 특성과 배포 단순성을 결정한다.
>
> 📌 **핵심 키워드**: SSA (Static Single Assignment), GMP, tcmalloc, Tricolor GC, Escape Analysis
> 📅 **기준**: Go 1.24 (2025.02)

---

## 1️⃣ Go 컴파일 파이프라인 — 소스에서 바이너리까지

### 🏗️ 전체 흐름

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐
│  Source   │───►│  Lexer / │───►│  Type    │───►│  Unified IR  │
│  .go 파일 │    │  Parser  │    │  Check   │    │  (Noding)    │
└──────────┘    └──────────┘    └──────────┘    └──────┬───────┘
                                                        │
                                                        ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐
│  Object  │◄───│  Machine │◄───│  Generic │◄───│  Middle-End  │
│  File    │    │  SSA     │    │  SSA     │    │  최적화       │
│  + Export│    │  (arch별)│    │  (범용)  │    │  (인라인 등)  │
└────┬─────┘    └──────────┘    └──────────┘    └──────────────┘
     │
     ▼
┌──────────┐    ┌──────────┐
│  Linker  │───►│  Binary  │  ← 런타임 포함된 단일 실행 파일
└──────────┘    └──────────┘
```

### 🔍 각 단계 상세

| 단계 | 패키지 | 역할 |
|------|--------|------|
| **Lexer/Parser** | `cmd/compile/internal/syntax` | 소스를 토큰화하고 AST (Abstract Syntax Tree) 생성 |
| **Type Check** | `types2` (go/types 포트) | 타입 검사, 제네릭 인스턴스화 |
| **Unified IR** | `noder` | 타입 검사된 AST를 컴파일러 내부 IR로 변환 |
| **Middle-End** | `inline`, `devirtualize`, `escape` | 인라이닝, 인터페이스 탈가상화, 이스케이프 분석, 데드 코드 제거 |
| **Walk/Desugar** | `walk` | 고수준 연산을 런타임 호출로 변환 (map/channel → runtime 함수) |
| **Generic SSA** | `ssa` | 머신 독립 최적화 — nil 체크 제거, 상수 폴딩, SCCP |
| **Machine SSA** | `ssa` (lower pass) | 아키텍처별 명령어 변환, 레지스터 할당, 스택 프레임 레이아웃 |
| **Linker** | `cmd/link` | 객체 파일 결합, 런타임 삽입, 실행 바이너리 생성 |

### 🔧 SSA 최적화 주요 패스

```
Generic SSA (머신 독립):
├── Dead code elimination
├── Nil check elimination (중복 제거)
├── Unused branch removal
├── Constant folding / expression simplification
└── SCCP (Sparse Conditional Constant Propagation)

Machine SSA (아키텍처 의존):
├── Generic → arch-specific 변환 (lower)
├── Dead code (2nd pass)
├── Move values closer to use sites
├── Register allocation
├── Stack frame layout
└── Pointer liveness analysis (GC용)
```

> 💡 **팁**: `GOSSAFUNC=함수명 go build`로 SSA HTML 디버그 출력을 생성하면 모든 패스의 IR을 볼 수 있다.

### 🧒 12살 비유

> Go 컴파일은 "레시피(소스) → 요리사(컴파일러) → 도시락(바이너리)" 과정이야. 요리사가 레시피를 읽고(Parser), 재료가 맞는지 확인하고(Type Check), 불필요한 단계를 생략하고(최적화), 최종적으로 도시락 하나에 반찬까지 다 넣어서(런타임 포함) 완성해.

### 🔄 다른 언어와 비교

| 단계 | Go | Python | JavaScript (V8) | Kotlin/JVM |
|------|-----|--------|-----------------|-----------|
| 파싱 | AST → IR → SSA | AST → Bytecode | AST → Bytecode → JIT | AST → JVM Bytecode |
| 최적화 시점 | **컴파일 타임** (AOT) | 없음 (인터프리터) | **런타임** (JIT) | **런타임** (JIT) |
| 결과물 | 네이티브 바이너리 | .pyc (바이트코드) | 메모리 내 기계어 | .class (바이트코드) |
| 런타임 | 바이너리에 내장 | CPython 인터프리터 | V8 엔진 | JVM |

---

## 2️⃣ Go 런타임의 구조

### 런타임이 바이너리에 포함되는 구조

```
┌─────────────────────────────────────────┐
│              Go Binary                   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │         사용자 코드               │   │
│  │   (main, 패키지 함수들)          │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │         Go Runtime               │   │
│  │  ┌────────┐ ┌─────────────┐     │   │
│  │  │Scheduler│ │  Memory     │     │   │
│  │  │  (GMP) │ │  Allocator  │     │   │
│  │  └────────┘ └─────────────┘     │   │
│  │  ┌────────┐ ┌─────────────┐     │   │
│  │  │  GC    │ │  Network    │     │   │
│  │  │(triclr)│ │  Poller     │     │   │
│  │  └────────┘ └─────────────┘     │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │    Standard Library (사용된 것만) │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**JVM과의 핵심 차이**: JVM은 별도 프로세스로 실행되는 가상 머신이지만, Go 런타임은 바이너리에 **정적으로 링크**되어 함께 배포된다. 별도 설치가 필요 없다.

### 🔄 4대 서브시스템 개요

| 서브시스템 | 역할 | 상세 문서 |
|-----------|------|----------|
| **Scheduler (GMP)** | goroutine 스케줄링, 작업 훔치기, 선점 | [[goroutine-gmp-scheduler-deep-dive]] |
| **Memory Allocator** | tcmalloc 기반 계층적 메모리 할당 | 이 문서 §3 |
| **Garbage Collector** | Tricolor concurrent mark-sweep | 이 문서 §4 |
| **Network Poller** | epoll/kqueue/IOCP 추상화 | 아래 요약 |

#### Network Poller 요약

```
goroutine이 네트워크 I/O 호출
        │
        ▼
  ┌─────────────┐
  │ 즉시 완료?  │── Yes ──► 계속 실행
  └──────┬──────┘
         │ No
         ▼
  goroutine을 park (대기 상태)
  M(OS 스레드)은 해제 → 다른 goroutine 실행
        │
        ▼
  ┌─────────────────┐
  │ OS 이벤트 감지   │  ← epoll(Linux) / kqueue(macOS) / IOCP(Windows)
  │ (sysmon 주기적   │
  │  폴링 또는 별도  │
  │  netpoll 스레드) │
  └────────┬────────┘
           ▼
  goroutine을 runnable로 복원
```

**핵심**: goroutine이 네트워크 I/O로 블로킹되어도 **M(OS 스레드)이 낭비되지 않는다**.

### 🔄 다른 언어 런타임과의 비교

| 측면 | Go Runtime | CPython | V8 (JS) | JVM (Kotlin) |
|------|-----------|---------|---------|-------------|
| 배포 | 바이너리에 내장 | 별도 설치 | 별도 설치 | 별도 설치 (200MB+) |
| 스케줄러 | GMP (M:N) | GIL (1:1) | 이벤트 루프 (1 thread) | OS 스레드 + Virtual Thread |
| GC | Concurrent tricolor | Reference counting + cycle detector | Generational (V8) | Generational (G1/ZGC) |
| 메모리 관리 | tcmalloc 기반 | pymalloc + system malloc | V8 heap | JVM heap + metaspace |
| 시작 시간 | ~1ms | ~30ms | ~50ms | ~200-500ms (JIT warm-up) |

---

## 3️⃣ 메모리 관리 아키텍처

### 🏗️ Escape Analysis — 스택 vs 힙 결정

컴파일러가 **컴파일 타임에** 변수가 스택에 머물 수 있는지 판단한다:

```
변수 선언
    │
    ├── 함수 내에서만 사용? ──── Yes ──► 스택 할당 (빠르다)
    │
    └── 아래 조건 중 하나라도? ──► 힙 할당 (GC 대상)
         • 주소(&)가 함수 밖으로 반환
         • interface{}에 저장
         • goroutine에 전달
         • 스택에 비해 너무 큰 크기
```

```bash
# escape analysis 결과 확인
go build -gcflags="-m" ./...
# 상세 이유 확인
go build -gcflags="-m -m" ./...
```

**성능 영향**: 스택 할당은 **포인터 증가** 한 번이지만, 힙 할당은 런타임 장부 작업 + 미래 GC 작업을 발생시킨다. **핫 패스의 할당을 스택에 유지하는 것이 Go 성능 최적화의 핵심 레버**.

### 🏗️ mcache → mcentral → mheap 계층

```
┌──────────────────────────────────────────────────┐
│                    mheap (전역)                    │
│     • 8192 byte 페이지 단위 관리                  │
│     • 대형 객체(>32KB) 직접 할당                  │
│     • 전역 락 필요                                │
│                                                    │
│  ┌────────────────────────────────────────────┐   │
│  │           mcentral (사이즈 클래스별)         │   │
│  │  • ~70개 사이즈 클래스 × 2 = ~136개         │   │
│  │  • swept/unswept span 세트 관리             │   │
│  │  • 사이즈 클래스별 거친 락                   │   │
│  │                                              │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐     │   │
│  │  │ mcache  │  │ mcache  │  │ mcache  │     │   │
│  │  │ (P0)    │  │ (P1)    │  │ (P2)    │     │   │
│  │  │ 락 없음 │  │ 락 없음 │  │ 락 없음 │     │   │
│  │  └─────────┘  └─────────┘  └─────────┘     │   │
│  └────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────┘
```

| 계층 | 소유자 | 락 | 역할 |
|------|--------|-----|------|
| **mcache** | P (논리 프로세서) 1개당 1개 | **없음** (P가 독점) | 소형 객체 빠른 할당 |
| **mcentral** | 사이즈 클래스당 1개 (~136개) | 거친 락 | mcache에 span 보급 |
| **mheap** | 전역 1개 | 전역 락 | 페이지 할당, 대형 객체 직접 할당 |

#### 할당 경로

```
객체 할당 요청
    │
    ├── ≤32KB → mcache에서 사이즈 클래스 선택 → span에서 할당 (락 없음!)
    │              └── mcache 빈 경우 → mcentral에서 span 가져옴
    │                    └── mcentral 빈 경우 → mheap에서 새 span 할당
    │
    └── >32KB → mheap에서 직접 할당 (전역 락)
```

### 🔧 사이즈 클래스 (Size Class)

~70개의 사이즈 클래스가 8 byte ~ 32KB 범위를 커버:

```
8, 16, 24, 32, 48, 64, 80, 96, 112, 128, ...
... 1024, 1152, 1280, ... 8192, ... 32768
```

**내부 단편화 트레이드오프**: 33 byte 객체는 48 byte 클래스에 할당되어 15 byte 낭비. 하지만 사이즈 클래스 덕분에 **외부 단편화가 거의 없고 할당이 매우 빠르다**.

### 🧒 12살 비유

> 학교 사물함을 생각해봐.
> - **mcache** = 너의 책상 서랍 (바로 꺼낼 수 있고, 다른 사람 신경 안 써도 돼)
> - **mcentral** = 학급 사물함 (여러 학생이 공유하니까 줄 서야 할 수도)
> - **mheap** = 학교 창고 (큰 물건은 여기서 직접 가져오는데, 관리자 허락이 필요해)

### 🔧 GOGC와 GOMEMLIMIT 튜닝

| 파라미터 | 기본값 | 역할 | 공식 |
|---------|--------|------|------|
| **GOGC** | 100 | GC 빈도 조절 | Target heap = Live heap + (Live heap + GC roots) × GOGC/100 |
| **GOMEMLIMIT** | 무제한 | 소프트 메모리 상한 (Go 1.19+) | 이 값에 근접하면 GOGC 무시하고 즉시 GC |

```
GOGC=100 (기본):
  Live heap 100MB → 다음 GC는 ~200MB에서 트리거

GOGC=200:
  Live heap 100MB → 다음 GC는 ~300MB에서 트리거
  → GC 빈도 ↓, CPU 비용 ↓, 메모리 사용 ↑

GOGC=50:
  Live heap 100MB → 다음 GC는 ~150MB에서 트리거
  → GC 빈도 ↑, CPU 비용 ↑, 메모리 사용 ↓
```

**프로덕션 권장 패턴** (컨테이너 환경):
```bash
# 컨테이너 메모리 제한의 ~90%로 GOMEMLIMIT 설정
# GOGC를 높여서 GC 빈도 감소
GOMEMLIMIT=900MiB GOGC=200 ./myapp
```

### 🔄 다른 언어 메모리 관리 비교

| 측면 | Go | Python | JavaScript (V8) | Kotlin/JVM |
|------|-----|--------|-----------------|-----------|
| 할당 전략 | tcmalloc 기반 사이즈 클래스 | pymalloc (소형) + system malloc | V8 heap (generational) | TLAB + Eden → Survivor |
| 스택/힙 결정 | 컴파일 타임 (escape analysis) | 모든 객체가 힙 | V8이 런타임에 결정 | JIT가 스칼라 치환 (escape analysis) |
| 튜닝 파라미터 | GOGC, GOMEMLIMIT | 제한적 | V8 --max-old-space-size | -Xmx, -Xms, GC 알고리즘 선택 |

---

## 4️⃣ GC (Garbage Collector) 동작 원리

### 🏗️ Tricolor Concurrent Mark-Sweep

Go의 GC는 **3색 마킹 알고리즘**을 사용한 **동시적(concurrent)** mark-sweep 방식이다:

```
┌────────────────────────────────────────────────────┐
│              Tricolor Mark Algorithm                 │
│                                                      │
│  ⚪ 흰색 (White)  = 아직 방문하지 않은 객체          │
│  ⬜ 회색 (Gray)   = 방문했지만, 참조하는 객체 미확인  │
│  ⬛ 검은색 (Black) = 방문 완료, 참조 객체도 모두 확인  │
│                                                      │
│  시작: 모든 객체가 흰색                              │
│  종료: 흰색 = 가비지 (수거 대상)                     │
│                                                      │
│  1. 루트에서 도달 가능한 객체를 회색으로              │
│  2. 회색 객체를 하나 꺼내서:                         │
│     - 이 객체가 참조하는 흰색 객체를 회색으로         │
│     - 이 객체를 검은색으로                           │
│  3. 회색이 없을 때까지 반복                          │
│  4. 남은 흰색 = 도달 불가 → 수거                    │
└────────────────────────────────────────────────────┘
```

### GC 사이클 전체 흐름

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌───────────┐
│ Sweep           │───►│ Sweep            │───►│ Mark            │───►│ Mark      │
│ (concurrent)    │    │ Termination      │    │ (concurrent)    │    │ Termin.   │
│                 │    │ 🔴 STW ~10-30µs  │    │ ~25% CPU 사용   │    │ 🔴 STW    │
│ 이전 사이클의   │    │ write barrier    │    │ 사용자 코드와   │    │ ~60-90µs  │
│ 흰색 객체 수거  │    │ 활성화          │    │ 동시 실행       │    │ barrier   │
│                 │    │                  │    │                 │    │ 비활성화  │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └───────────┘
                                                                            │
                                                                            ▼
                                                                    다음 Sweep 시작
```

| 단계 | STW? | 설명 |
|------|------|------|
| **Sweep** | ❌ 동시적 | 이전 사이클에서 흰색으로 남은 객체 수거 |
| **Sweep Termination** | 🔴 **STW** (~10-30µs) | Write barrier 활성화, GC 시작 준비 |
| **Mark** | ❌ 동시적 | 3색 마킹 수행, CPU의 ~25% 사용 |
| **Mark Termination** | 🔴 **STW** (~60-90µs) | Write barrier 비활성화, 정리 |

### 🔧 Hybrid Write Barrier (Go 1.8+)

GC가 마킹하는 동안 사용자 코드가 동시에 포인터를 수정할 수 있다. **Write barrier**가 이를 안전하게 처리:

```
// 컴파일러가 포인터 쓰기에 자동 삽입하는 의사 코드
if runtime.writeBarrier.enabled {
    // Dijkstra + Yuasa 하이브리드:
    // 1. 새 포인터가 가리키는 객체를 회색으로 (Dijkstra)
    // 2. 덮어쓰기 전 기존 포인터의 객체도 회색으로 (Yuasa)
    runtime.gcWriteBarrier(slot, newVal)
} else {
    *slot = newVal  // barrier 비활성 시 그냥 쓰기
}
```

**성능**: barrier가 활성화된 동안 포인터 쓰기마다 조건 분기 1회. 비활성 시 `CMPL` 한 명령어로 fast-path.

### 🧒 12살 비유

> 놀이터 청소를 생각해봐. 아이들이 **놀면서 동시에** 청소부가 치운다(concurrent).
> - ⚪ 흰색: 아직 누가 쓰는지 확인 안 된 장난감
> - ⬜ 회색: "이거 누구 거야?" 확인 중인 장난감
> - ⬛ 검은색: "이건 철수 거" 확인 완료된 장난감
> - 청소부가 "잠깐 멈춰!"(STW) 하는 건 **딱 두 번**, 각각 0.01초만!

### 🔄 Go GC vs Java GC 포지셔닝

| 측면 | Go (Concurrent tricolor) | Java G1 | Java ZGC (JDK 15+) |
|------|--------------------------|---------|---------------------|
| STW 시간 | **10-90µs** | 1-10ms | ~1ms |
| 동시성 | Mark/Sweep 모두 동시적 | Mixed GC에서 STW | 거의 전부 동시적 |
| 세대별 수집 | ❌ 없음 (단일 세대) | ✅ Young/Old 세대 | ✅ 세대별 |
| CPU 오버헤드 | GC 중 ~25% | 가변 | 가변 |
| 최적 대상 | 레이턴시 민감 서비스 | 범용 처리량 | 대용량 힙 + 저지연 |

**Go GC의 약점**: 세대별 수집이 없어서 수명이 짧은 객체도 동일하게 마킹 → 단명 객체가 많으면 GC 작업량 증가. Go 팀이 세대별 GC 실험 진행 중 (2024~).

---

## 5️⃣ 바이너리 구조와 배포

### 정적 링킹 vs 동적 링킹

```
┌──────────────────────────────────────────────┐
│          Pure Go (CGo 없음)                   │
│                                               │
│  CGO_ENABLED=0 go build                      │
│  → 완전한 정적 바이너리                       │
│  → scratch 이미지에서 실행 가능               │
│  → 크로스 컴파일 자유                         │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│          CGo 사용                             │
│                                               │
│  CGO_ENABLED=1 go build                      │
│  → libc 동적 링크                             │
│  → distroless/base 또는 alpine 필요          │
│  → 크로스 컴파일 시 타겟 C 컴파일러 필요     │
│                                               │
│  정적 링크 강제:                              │
│  -tags netgo,osusergo                        │
│  -ldflags '-extldflags "-static"'            │
└──────────────────────────────────────────────┘
```

### 바이너리 크기 분석

```bash
# 기본 빌드
go build -o myapp         # ~10-15MB (Hello World 기준)

# 디버그 정보 제거
go build -ldflags="-s -w" -o myapp  # ~7-10MB

# UPX 압축 (선택)
upx --best myapp          # ~3-5MB
```

| 빌드 옵션 | 대략 크기 | 설명 |
|-----------|----------|------|
| 기본 | 10-15MB | DWARF 디버그 + 심볼 테이블 포함 |
| `-ldflags="-s -w"` | 7-10MB | 심볼/디버그 제거, 프로덕션 권장 |
| + UPX | 3-5MB | 실행 시 압축 해제 오버헤드 |

### 크로스 컴파일

```bash
# Linux AMD64 (가장 흔한 서버 타겟)
GOOS=linux GOARCH=amd64 go build -o myapp-linux

# macOS ARM64 (Apple Silicon)
GOOS=darwin GOARCH=arm64 go build -o myapp-mac

# Windows
GOOS=windows GOARCH=amd64 go build -o myapp.exe
```

**Pure Go라면 크로스 컴파일에 추가 도구가 필요 없다.** `GOOS`와 `GOARCH`만 설정하면 된다.

### 컨테이너 배포 패턴

```dockerfile
# ---- Multi-stage build ----
# Stage 1: 빌드
FROM golang:1.24-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /app/server

# Stage 2: 실행 (최소 이미지)
FROM scratch
# 또는 FROM gcr.io/distroless/static:nonroot
COPY --from=builder /app/server /server
ENTRYPOINT ["/server"]
```

| 베이스 이미지 | 크기 | 용도 |
|-------------|------|------|
| `scratch` | **0 MB** | Pure Go, TLS 인증서 직접 포함 필요 |
| `distroless/static` | ~2 MB | Pure Go, CA 인증서 포함 |
| `distroless/base` | ~20 MB | CGo 사용 시 (glibc 포함) |
| `alpine` | ~5 MB | CGo + musl libc |

### 🔄 다른 언어 배포 비교

| 측면 | Go | Python | JavaScript | Kotlin/JVM |
|------|-----|--------|-----------|-----------|
| 아티팩트 | 단일 바이너리 | .py + requirements.txt | .js + node_modules | .jar + JVM |
| 컨테이너 이미지 | scratch (~10MB) | python:slim (~150MB) | node:slim (~180MB) | eclipse-temurin (~300MB) |
| 시작 시간 | ~1ms | ~30ms | ~50ms | ~200-500ms |
| 메모리 풋프린트 | ~10-30MB | ~30-80MB | ~40-100MB | ~100-300MB |

---

## 6️⃣ Go 1.24 런타임 변경사항

### Swiss Tables 기반 내장 map (Go 1.24)

기존 bucket-chain 방식에서 **Swiss Tables** (open addressing + SIMD 탐색)로 교체:

```
기존 (Go ≤1.23):                    신규 (Go 1.24):
┌─────────────┐                     ┌─────────────────────┐
│ bucket (8슬롯)│                    │ group (8슬롯)        │
│ ┌─┬─┬─┬─┬─┬─┬─┬─┐              │ ┌─┬─┬─┬─┬─┬─┬─┬─┐  │
│ │k│k│k│k│k│k│k│k│              │ │k│k│k│k│k│k│k│k│  │
│ └─┴─┴─┴─┴─┴─┴─┴─┘              │ └─┴─┴─┴─┴─┴─┴─┴─┘  │
│ overflow → 다음 bucket            │ 64-bit control word  │
│              (체이닝)              │ (7-bit hash + 1-bit) │
└─────────────┘                     │ quadratic probing    │
                                    └─────────────────────┘
```

| 지표 | 개선폭 | 출처 |
|------|--------|------|
| 대형 map 접근 | **+30%** | Go 벤치마크 |
| pre-sized map 할당 | **+35%** | Go 벤치마크 |
| map 순회 | **+10~60%** | Go 벤치마크 |
| 메모리 사용 (3.5M 항목) | **-70%** (726 MiB → 217 MiB) | Datadog 측정 |
| 평균 CPU 오버헤드 | **-2~3%** | Go 벤치마크 스위트 |

### 기타 1.24 런타임 개선

| 기능 | 설명 |
|------|------|
| `runtime.AddCleanup` | `SetFinalizer` 대체 — 다중 cleanup, interior pointer 지원, cycle-safe |
| `spinbitMutex` | 런타임 내부 락 최적화 |
| GNU Build ID / LC_UUID | 링커가 기본 생성 (디버깅 편의) |
| `os.Root` | 디렉터리 범위 제한 파일 접근 타입 |

---

## 📎 출처

1. [Go Compiler README (go.dev 공식)](https://go.dev/src/cmd/compile/README) — 컴파일 파이프라인 공식 문서
2. [Go SSA Backend README (go.dev 공식)](https://go.dev/src/cmd/compile/internal/ssa/README) — SSA 패스 상세
3. [A Guide to the Go Garbage Collector (go.dev 공식)](https://go.dev/doc/gc-guide) — GC 동작, GOGC, GOMEMLIMIT
4. [Go 1.24 Release Notes (go.dev 공식)](https://go.dev/doc/go1.24) — Swiss Tables, AddCleanup
5. [How Go 1.24's Swiss Tables saved us hundreds of gigabytes — Datadog](https://www.datadoghq.com/blog/engineering/go-swiss-tables/) — 실측 성능/메모리 데이터
6. [Understanding the Go Runtime: Memory Allocator](https://internals-for-interns.com/posts/go-memory-allocator/) — mcache/mcentral/mheap 상세
7. [Stack Allocations and Escape Analysis (goperf.dev)](https://goperf.dev/01-common-patterns/stack-alloc/) — 이스케이프 분석 가이드

---

> 📌 **이전 문서**: [[01-go-philosophy-and-differentiation]] — Go의 철학과 다른 언어와의 차별점
> 📌 **다음 문서**: [[03-go-basic-syntax]] — Go 기본 문법
> 📌 **상세 문서**: [[goroutine-gmp-scheduler-deep-dive]], [[go-channel-deep-dive]]
