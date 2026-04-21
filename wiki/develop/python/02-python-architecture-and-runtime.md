---
created: 2026-04-21
source: claude-code
tags: [python, cpython, architecture, runtime, gil, memory, gc, pypy, jit, free-threaded]
---

# 📖 Python 아키텍처와 런타임 — CPython 내부 구조

> 💡 **한줄 요약**: CPython은 "소스 → 바이트코드 → 가상 머신(PVM)"의 인터프리터 구조로, GIL이 멀티스레드를 제한하지만 3.13의 free-threaded 모드와 3.14의 concurrent.interpreters로 이 한계를 점진적으로 극복하고 있다.
>
> 📌 **핵심 키워드**: CPython, PVM, GIL, Reference Counting, pymalloc, Free-threaded, Per-interpreter GIL
> 📅 **기준**: Python 3.14 (2025.10)

---

## 1️⃣ CPython 실행 파이프라인

### 🏗️ 소스에서 실행까지

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐
│  Source   │───►│  Lexer / │───►│  AST     │───►│  Compiler    │
│  .py 파일 │    │  Parser  │    │          │    │  (compile.c) │
└──────────┘    └──────────┘    └──────────┘    └──────┬───────┘
                                                        │
                                                        ▼
                                                 ┌──────────────┐
                                                 │  Bytecode    │
                                                 │  (.pyc 파일) │
                                                 └──────┬───────┘
                                                        │
                                                        ▼
                                                 ┌──────────────┐
                                                 │  PVM         │
                                                 │  (ceval.c)   │
                                                 │  평가 루프    │
                                                 └──────────────┘
```

| 단계 | 역할 | Go와의 차이 |
|------|------|-----------|
| **Lexer/Parser** | 토큰화 → AST 생성 | Go도 동일 |
| **Compiler** | AST → 바이트코드 (.pyc) | Go는 네이티브 기계어 생성 |
| **PVM** | 바이트코드 해석 실행 (ceval.c) | Go는 직접 CPU에서 실행 |

### 바이트코드 확인

```python
import dis
dis.dis(lambda x: x + 1)
#   LOAD_FAST    0 (x)
#   LOAD_CONST   1 (1)
#   BINARY_ADD
#   RETURN_VALUE
```

### 🧒 12살 비유

> Go는 "레시피를 완전한 도시락으로 만들어서 전달"하는 거야 (AOT 컴파일). Python은 "레시피를 읽으면서 실시간으로 요리"하는 거야 (인터프리터). 그래서 Go 도시락은 어디서든 바로 먹을 수 있지만, Python은 매번 요리사(CPython)가 필요해.

### 🔄 4개 언어 실행 모델 비교

| 단계 | Python (CPython) | Go | Kotlin/JVM | JS (V8) |
|------|-----------------|-----|-----------|---------|
| 1단계 | AST → **바이트코드** | AST → SSA → **기계어** | AST → **JVM 바이트코드** | AST → **V8 바이트코드** |
| 2단계 | PVM **해석 실행** | CPU **직접 실행** | JVM **JIT → 기계어** | Ignition → **Turbofan JIT** |
| 최적화 | 없음 (3.13 실험적 JIT) | 컴파일 타임 SSA | 런타임 JIT (C1/C2) | 런타임 JIT (Turbofan) |
| 결과물 | .pyc (바이트코드) | 단일 바이너리 | .jar (바이트코드) | 메모리 내 기계어 |

---

## 2️⃣ GIL (Global Interpreter Lock) Deep Dive

### GIL이란?

```
┌───────────────────────────────────────────┐
│           CPython 프로세스                  │
│                                            │
│  Thread 1 ─┐                               │
│  Thread 2 ─┤── 🔒 GIL ──► 한 번에 하나만   │
│  Thread 3 ─┘         바이트코드 실행        │
│                                            │
│  결과: CPU 코어가 4개여도                  │
│        Python 스레드는 1개만 실행           │
└───────────────────────────────────────────┘
```

**GIL**은 CPython 인터프리터의 **전역 뮤텍스**로, 한 번에 하나의 스레드만 Python 바이트코드를 실행할 수 있게 한다.

### 왜 GIL이 존재하는가?

**Reference Counting** 때문이다:

```python
a = [1, 2, 3]  # refcount = 1
b = a           # refcount = 2
del a           # refcount = 1
del b           # refcount = 0 → 즉시 해제
```

모든 Python 객체에는 `ob_refcnt`(참조 횟수)가 있다. 여러 스레드가 동시에 refcount를 수정하면 **데이터 레이스**가 발생한다. GIL은 이를 단순하게 방지한다.

### GIL의 전환 규칙

```
Thread 1 실행 중
    │
    ├── 5ms 경과 (switch interval) → 다른 스레드에 GIL 양보
    │
    ├── I/O 호출 (file, network) → GIL 해제 → 다른 스레드 실행
    │
    └── C 확장 호출 → GIL 해제 가능 (확장이 명시적으로 해제)
```

> 📌 면접 심화: [[python-fastapi-sqlalchemy]] Q1 (GIL 동작 메커니즘)

### GIL의 실질적 영향

| 작업 유형 | GIL 영향 | 해법 |
|---------|---------|------|
| **I/O bound** (웹 서버, DB 쿼리) | 거의 없음 — I/O 중 GIL 해제 | asyncio 또는 threading |
| **CPU bound** (계산, 데이터 처리) | **심각** — 멀티스레드 무의미 | multiprocessing, C 확장, Go 호출 |

> 📌 성능 수치: [[python-go-java-performance-myth-deep-dive]] — CPU bound에서 Go 대비 37~63× 느림

### 🔄 다른 언어와 비교

| 측면 | Python (GIL) | Go (GMP) | Kotlin (JVM) | JS (이벤트 루프) |
|------|-------------|---------|-------------|---------------|
| 스레드 모델 | OS 스레드 + GIL | M:N (goroutine) | OS 스레드 + Virtual Thread | 단일 스레드 |
| 진정한 병렬 | ❌ (3.13t부터 실험적 ✅) | ✅ | ✅ | ❌ |
| 해법 | multiprocessing | goroutine 수백만 개 | Virtual Thread | Worker 분리 |

---

## 3️⃣ 메모리 관리

### Reference Counting + Cycle Detector

```
┌──────────────────────────────────────────┐
│       Python GC = 2단계                   │
│                                           │
│  1단계: Reference Counting (즉시)         │
│  ┌─────────┐                              │
│  │ refcnt=0│ → 즉시 메모리 해제           │
│  └─────────┘                              │
│                                           │
│  2단계: Cycle Detector (주기적)           │
│  ┌──────┐     ┌──────┐                    │
│  │  A   │────►│  B   │                    │
│  │ rc=1 │◄────│ rc=1 │ ← 순환 참조!      │
│  └──────┘     └──────┘                    │
│  refcount만으로는 해제 불가               │
│  → 세대별 Cycle Detector가 감지·해제     │
│                                           │
│  세대 0 (young): 자주 검사                │
│  세대 1 (mid): 가끔 검사                  │
│  세대 2 (old): 드물게 검사                │
└──────────────────────────────────────────┘
```

> 📌 GC 비교 상세: [[gc-g1-zgc]] — Python RC, JVM G1/ZGC, Go Tricolor GC

### pymalloc (소형 객체 할당기)

| 계층 | 크기 | 역할 |
|------|------|------|
| **pymalloc** | ≤ 512 bytes | 소형 객체 전용 풀 할당 (arena → pool → block) |
| **system malloc** | > 512 bytes | OS malloc 직접 사용 |

```
Arena (256KB) → Pool (4KB, 사이즈 클래스별) → Block (8~512 bytes)
```

Go의 tcmalloc (mcache → mcentral → mheap)과 유사한 계층 구조이지만, Python은 **모든 객체가 힙**에 할당된다 (스택 할당 없음).

### 🧒 12살 비유

> Python의 메모리 관리는 "도서관 대출 시스템"이야.
> - **Reference Counting** = 빌려간 사람 수 세기. 아무도 안 빌려가면(rc=0) 즉시 서가로 돌아가.
> - **Cycle Detector** = 철수가 영희 책을 빌려가고, 영희가 철수 책을 빌려가서 서로 돌려주지 않는 상황. 사서(GC)가 주기적으로 순회하면서 "아무도 안 읽는 책"을 찾아서 회수해.

---

## 4️⃣ Python 3.12~3.14 — GIL의 진화

### 3.12: Per-interpreter GIL (PEP 684)

```
기존 (3.11 이하):                3.12+:
┌──────────────────┐            ┌──────────────────┐
│ Process          │            │ Process          │
│                  │            │                  │
│ 🔒 GIL (1개)    │            │ Interp A: 🔒 GIL│
│                  │            │ Interp B: 🔒 GIL│
│ Thread 1 ─┐     │            │ Thread 1 ─┐ (A) │
│ Thread 2 ─┘     │            │ Thread 2 ─┘ (B) │
│   직렬 실행      │            │   병렬 실행!     │
└──────────────────┘            └──────────────────┘
```

- **C-API 전용** (3.12), **Python API** (3.14: `concurrent.interpreters`)
- 각 서브인터프리터가 독립 GIL → 같은 프로세스에서 **진정한 병렬 실행**

### 3.13: Free-threaded Mode (PEP 703)

```bash
# 빌드: --disable-gil 플래그
# 실행: python3.13t (suffix 't')
# 상태: 실험적 (Experimental)
```

GIL 자체를 제거하여 모든 스레드가 동시에 바이트코드를 실행할 수 있게 한다.

### 3.14: Free-threaded 공식 지원 (PEP 779)

```
3.13: Experimental (실험적)
  ↓
3.14: Supported (공식 지원으로 승격)  ← 현재
  ↓
향후: 기본값으로?
```

**추가**: `concurrent.interpreters` 모듈로 Per-interpreter GIL을 Python 코드에서 직접 사용 가능.

### GIL 진화 정리

| 버전 | 변화 | 상태 |
|------|------|------|
| 3.12 | Per-interpreter GIL (C-API) | 안정 |
| 3.13 | Free-threaded mode | 실험적 |
| 3.14 | Free-threaded → **공식 지원**, `concurrent.interpreters` | **안정** |

---

## 5️⃣ 대안 런타임

| 런타임 | 방식 | 장점 | 단점 |
|--------|------|------|------|
| **CPython** | 인터프리터 | 표준, 100% 호환 | 느림 |
| **PyPy** | JIT 컴파일 | CPython 대비 **4~10× 빠름** | C 확장 호환성 이슈 |
| **GraalPy** | GraalVM JIT | JVM 생태계 연동 | 아직 초기 |
| **Cython** | Python → C 컴파일 | 핫 루프 최적화 | 별도 빌드 단계 |
| **mypyc** | 타입 힌트 → C 확장 | mypy 연동, 점진적 적용 | 지원 범위 제한 |

```
성능 스펙트럼:

  CPython ◄────────────────────────────────────────────────► Go/Rust
  (1x)     PyPy(4-10x)  Cython(10-50x)  mypyc(2-5x)      (37-63x)
```

### 🔄 다른 언어 대안 런타임 비교

| 언어 | 기본 런타임 | 대안 런타임 |
|------|-----------|-----------|
| **Python** | CPython | PyPy, GraalPy, Cython |
| **Go** | (유일한 런타임) | TinyGo (임베디드용) |
| **Kotlin** | JVM | GraalVM Native Image, Kotlin/Native (LLVM) |
| **JS** | V8 (Chrome/Node) | SpiderMonkey (Firefox), JavaScriptCore (Safari), Bun (Zig) |

---

## 6️⃣ CPython 내부 구조

### 인터프리터 상태 계층

```
┌────────────────────────────────────┐
│ Runtime State (전역)               │
│  └── Interpreter State (인터프리터)│
│       └── Thread State (스레드)    │
│            └── Frame (프레임)      │
│                 ├── 로컬 변수      │
│                 ├── 바이트코드 PC   │
│                 └── 값 스택        │
└────────────────────────────────────┘
```

### 평가 루프 (ceval.c)

```c
// 단순화된 의사 코드
for (;;) {
    opcode = NEXT_OPCODE();
    switch (opcode) {
        case LOAD_FAST:    push(locals[oparg]); break;
        case BINARY_ADD:   b=pop(); a=pop(); push(a+b); break;
        case RETURN_VALUE: return pop();
        // ... 약 120개 opcode
    }
}
```

Python 3.14에서 **tail-call 인터프리터**로 전환 → 3~5% 성능 향상.

---

## 📎 출처

1. [PEP 684 – Per-Interpreter GIL](https://peps.python.org/pep-0684/) — 3.12 서브인터프리터 GIL
2. [PEP 703 – Making the GIL Optional](https://peps.python.org/pep-0703/) — Free-threaded CPython
3. [PEP 779 – Criteria for Supported Status for Free-threaded CPython](https://peps.python.org/pep-0779/) — 3.14 공식 지원
4. [What's New in Python 3.14](https://docs.python.org/3/whatsnew/3.14.html) — 최신 변경 사항
5. [Python Memory Management (CPython)](https://docs.python.org/3/c-api/memory.html) — 메모리 관리 공식 문서
6. [Python Glossary: GIL](https://docs.python.org/3/glossary.html#term-global-interpreter-lock) — GIL 공식 정의

---

> 📌 **이전 문서**: [[01-python-philosophy-and-differentiation]] — Python 철학과 차별점
> 📌 **다음 문서**: [[03-python-basic-syntax]] — Python 기본 문법
> 📌 **관련 문서**: [[python-fastapi-sqlalchemy]] (Q1 GIL), [[gc-g1-zgc]], [[coroutine-gmp-vthread]], [[python-go-java-performance-myth-deep-dive]]
