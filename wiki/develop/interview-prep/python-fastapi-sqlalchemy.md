# Python / FastAPI / SQLAlchemy — Staff Engineer Interview Q&A

> 대상: FAANG L6/L7 (Staff/Principal Engineer)
> 총 문항: 28개 | 난이도: ⭐⭐⭐⭐⭐
> 프레임워크: Python 3.12+, FastAPI 0.115+, Pydantic v2, SQLAlchemy 2.0+

## 목차

- [1. Python Runtime Internals](#1-python-runtime-internals)
- [2. Async/Concurrency Deep Dive](#2-asyncconcurrency-deep-dive)
- [3. FastAPI Internals & Production](#3-fastapi-internals--production)
- [4. SQLAlchemy Session & ORM](#4-sqlalchemy-session--orm)
- [5. DB Connection Management](#5-db-connection-management)
- [6. Type System & Metaprogramming](#6-type-system--metaprogramming)
- [7. Performance & Profiling](#7-performance--profiling)
- [8. Testing at Scale](#8-testing-at-scale)
- [9. Production Debugging](#9-production-debugging)
- [10. Design Patterns in Python](#10-design-patterns-in-python)

---

## 1. Python Runtime Internals

### Q1: GIL의 실제 동작 메커니즘과 우회 전략

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Python Runtime Internals

**Question:**
"CPython의 GIL이 정확히 어떤 수준에서 락을 잡고, 언제 릴리스되는지 설명하세요. GIL이 있음에도 멀티스레딩이 유용한 경우와, GIL 때문에 반드시 멀티프로세싱으로 가야 하는 경우를 프로덕션 사례와 함께 논하세요. Python 3.12의 per-interpreter GIL과 3.13의 free-threaded 모드(PEP 703)가 이 landscape를 어떻게 바꾸는지도 설명하세요."

---

**🧒 12살 비유:**
놀이공원에 놀이기구가 하나 있는데(CPU 코어), 열쇠가 딱 하나(GIL)야. 친구 10명이 왔어도 열쇠를 가진 한 명만 탈 수 있어. 그런데 놀이기구가 천천히 올라가는 동안(I/O 대기) 열쇠를 잠깐 다음 친구한테 넘겨줄 수 있어. 하지만 수학 문제를 푸는 것처럼(CPU 연산) 집중해야 하는 일은 열쇠를 안 놓아서 다른 친구들이 계속 기다려야 해. 그래서 진짜 동시에 하려면 놀이기구를 여러 대(멀티프로세싱) 만들어야 해.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
빅테크는 이 질문으로 (1) CPython 내부에 대한 깊이 있는 이해, (2) concurrency 모델 선택 시 trade-off 분석 능력, (3) 최신 Python 발전 방향에 대한 awareness를 평가한다. Staff 엔지니어는 "GIL 때문에 Python 느려요"라는 피상적 답변이 아니라 정확한 메커니즘과 상황별 최적 전략을 제시해야 한다.

**Step 2 — 핵심 기술 설명**

GIL(Global Interpreter Lock)은 CPython의 mutex로, Python 바이트코드 실행 시 인터프리터 상태(reference count, 객체 할당 등)를 보호한다.

핵심 메커니즘:
- **바이트코드 단위**: GIL은 Python 바이트코드 명령어(instruction) 단위로 동작한다. 하나의 Python 문장이라도 여러 바이트코드로 분해되므로, 문장 중간에 스레드 전환이 일어날 수 있다.
- **릴리스 시점**: I/O 작업(socket, file), C 확장 모듈이 명시적으로 `Py_BEGIN_ALLOW_THREADS` 호출 시, `time.sleep()` 호출 시 GIL을 릴리스한다.
- **스케줄링**: Python 3.2+에서 `sys.setswitchinterval()` (기본 5ms)마다 GIL을 요청하는 대기 스레드에 양보를 시도한다. 이전의 `sys.setcheckinterval()`(바이트코드 100개마다)보다 공정한 스케줄링을 제공한다.
- **Reference counting 보호**: `Py_INCREF`/`Py_DECREF`가 atomic이 아니므로 GIL 없이는 race condition 발생.

```python
import sys
import dis

# GIL 스위치 인터벌 확인/설정
print(sys.getswitchinterval())  # 0.005 (5ms)

# 바이트코드 레벨에서 thread-unsafe한 예시
x = 0
# x += 1 은 아래 바이트코드로 분해됨:
# LOAD_GLOBAL x
# LOAD_CONST 1
# BINARY_ADD
# STORE_GLOBAL x
# -> LOAD_GLOBAL과 STORE_GLOBAL 사이에 스레드 전환 가능!
```

**Step 3 — 다양한 관점**

| 워크로드 유형 | GIL 영향 | 최적 전략 |
|--------------|---------|-----------|
| I/O-bound (HTTP, DB) | 낮음 — I/O 중 GIL 릴리스 | asyncio 또는 threading |
| CPU-bound (순수 Python) | 치명적 — 코어 1개만 사용 | multiprocessing, C extension |
| CPU-bound (NumPy/Pandas) | 낮음 — C 레벨에서 GIL 릴리스 | threading도 가능 |
| Mixed | 중간 | 작업별 분리 (I/O는 async, CPU는 ProcessPool) |

**Step 4 — 구체적 예시**

```python
# 프로덕션 패턴: I/O-bound + CPU-bound 혼합 워크로드
import asyncio
from concurrent.futures import ProcessPoolExecutor
from functools import partial

# CPU-intensive 작업은 프로세스 풀로 오프로드
_process_pool = ProcessPoolExecutor(max_workers=4)

def cpu_heavy_sync(data: bytes) -> dict:
    """순수 Python CPU 작업 — GIL 영향 받음"""
    # 예: 복잡한 파싱, 암호화, 직렬화
    import hashlib
    result = hashlib.pbkdf2_hmac('sha256', data, b'salt', 100_000)
    return {"hash": result.hex()}

async def handle_request(payload: bytes) -> dict:
    """I/O + CPU 혼합 핸들러"""
    # Step 1: I/O-bound — GIL 릴리스, async 적합
    async with aiohttp.ClientSession() as session:
        resp = await session.get("https://api.example.com/validate")

    # Step 2: CPU-bound — 별도 프로세스에서 실행
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        _process_pool,
        partial(cpu_heavy_sync, payload)
    )

    # Step 3: I/O-bound — DB 저장
    await db.execute(insert_query, result)
    return result
```

```python
# Python 3.12+ per-interpreter GIL (PEP 684)
# 각 sub-interpreter가 독립 GIL을 가짐
# 아직 고수준 API가 제한적이나 방향성은 명확
import _interpreters  # 저수준 API

# Python 3.13 free-threaded mode (PEP 703)
# python3.13t (no-GIL 빌드) — 실험적
# 빌드 시 --disable-gil 옵션
# C extension은 Py_mod_gil 슬롯으로 호환성 선언 필요
import sysconfig
print(sysconfig.get_config_var('Py_GIL_DISABLED'))  # 1 if free-threaded
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| asyncio | 경량, 단일 스레드로 수천 동시 연결 | CPU-bound 불가, 모든 라이브러리 async 필요 | Web API, I/O 집약 서비스 |
| threading | 기존 코드 호환, I/O 병렬 | CPU-bound 시 GIL 병목 | 레거시 코드, I/O-bound |
| multiprocessing | 진정한 CPU 병렬 | 프로세스 간 통신 오버헤드, 메모리 복제 | CPU-bound 배치 처리 |
| C extension (Cython/Rust) | GIL 릴리스 + 네이티브 속도 | 개발/디버깅 복잡 | 핫 루프 최적화 |
| free-threaded (3.13+) | GIL 제거, 진정한 멀티스레드 | 생태계 미성숙, single-thread 성능 ~10% 저하 | 실험/미래 준비 |

**Step 6 — 성장 & 심화 학습**
- CPython 소스의 `Python/ceval_gil.c` 읽기 — GIL 구현의 실제 condvar/mutex 코드
- PEP 703 (free-threaded) 전문 + Sam Gross의 `nogil` 프로젝트 이력 추적
- `immortal objects` (PEP 683, Python 3.12) — free-threaded 모드의 전제 조건
- Larry Hastings의 Gilectomy 실패에서 배운 교훈

**🎯 면접관 평가 기준:**
- L6 PASS: GIL이 바이트코드 레벨에서 동작, I/O 시 릴리스됨을 설명. 워크로드별 전략 제시. `run_in_executor` 패턴 설명 가능.
- L7 EXCEED: switch interval 메커니즘, reference counting과 GIL의 관계, PEP 703의 biased reference counting 전략까지 설명. per-interpreter GIL과 free-threaded의 차이와 생태계 영향 논의.
- 🚩 RED FLAG: "GIL 때문에 Python은 멀티스레딩 불가"라고 단정. asyncio와 threading의 차이를 GIL 관점에서 설명 못함.

---

### Q2: CPython의 메모리 관리 — Reference Counting + Generational GC

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Python Runtime Internals

**Question:**
"CPython이 reference counting과 generational garbage collection을 함께 사용하는 이유를 설명하세요. 순환 참조가 메모리 릭을 일으키는 구체적 시나리오를 보여주고, `gc` 모듈로 이를 진단하는 방법과 프로덕션에서 GC 튜닝을 해야 했던 경험을 논하세요. `__del__`의 위험성과 weakref의 올바른 사용법도 포함하세요."

---

**🧒 12살 비유:**
도서관에서 책을 빌리면 대출 카드에 기록해(reference count). 아무도 안 빌리면(count=0) 바로 서가로 돌려놓아. 그런데 두 명이 서로의 카드를 참조하면(순환 참조) 둘 다 count가 0이 안 돼. 그래서 도서관 사서(GC)가 주기적으로 돌아다니면서 "이 책들 진짜 누가 읽고 있나?" 확인하는 거야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
메모리 관리는 장시간 실행 서비스(ASGI 서버, 배치 파이프라인)의 안정성을 결정한다. Staff 엔지니어는 메모리 릭을 진단하고 GC 동작을 이해해 튜닝할 수 있어야 한다. 특히 async 서버에서 GC pause가 latency spike를 유발하는 문제를 해결한 경험이 중요하다.

**Step 2 — 핵심 기술 설명**

**Reference Counting:**
- 모든 Python 객체의 `ob_refcnt` 필드가 참조 수를 추적
- 참조 생성 시 `Py_INCREF`, 해제 시 `Py_DECREF`
- count가 0이 되면 즉시 `tp_dealloc` 호출 → 결정적(deterministic) 해제
- 장점: 즉각적 해제, 예측 가능한 메모리 사용. 단점: 순환 참조 해결 불가

**Generational GC:**
- Generation 0, 1, 2 (young → old)
- 새 객체는 Gen 0에 할당
- Gen 0이 threshold(기본 700)에 도달하면 수집 시작
- 살아남은 객체는 다음 세대로 승격
- Gen 1 수집은 Gen 0이 10번 수집될 때, Gen 2는 Gen 1이 10번 수집될 때

```python
import gc
import sys

# 현재 GC threshold 확인
print(gc.get_threshold())  # (700, 10, 10)

# 객체의 reference count 확인
x = []
print(sys.getrefcount(x))  # 2 (x 자체 + getrefcount 인자)

# 순환 참조 시나리오
class Node:
    def __init__(self):
        self.parent = None
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        child.parent = self  # 순환 참조 생성!

parent = Node()
child = Node()
parent.add_child(child)
# parent.children -> child, child.parent -> parent
# del parent, del child 해도 refcount가 0이 안 됨
# -> GC의 cycle detector가 필요
```

**Step 3 — 다양한 관점**

GC 튜닝은 워크로드에 따라 전혀 다른 전략이 필요하다:

- **짧은 수명 요청 처리 (Web API)**: Gen 0 수집이 빈번하지만 빠름. 대부분 문제없음.
- **장시간 배치 처리**: 대량 객체 생성 시 Gen 0 threshold를 높여 수집 빈도 감소.
- **저지연 서비스**: GC pause가 p99 latency spike 유발. Gen 2 수집을 수동 제어하거나 비활성화 후 유휴 시간에 수동 실행.

```python
# 프로덕션 GC 튜닝 예시: 저지연 서비스
import gc

# 자동 GC 비활성화 (위험! 수동 관리 필수)
gc.disable()

# 유휴 시간에 수동 수집
async def periodic_gc():
    while True:
        await asyncio.sleep(60)
        # Gen 0, 1만 수집 (빠름)
        gc.collect(generation=0)
        gc.collect(generation=1)
        # Gen 2는 트래픽 적은 시간에
        if is_low_traffic():
            gc.collect(generation=2)
```

**Step 4 — 구체적 예시**

```python
# __del__의 위험성: 순환 참조 + __del__ = 수집 불가 (Python 3.3 이전)
# Python 3.4+ (PEP 442) 이후 개선되었지만 여전히 주의 필요

class Resource:
    def __del__(self):
        # 파이널라이저 — 호출 시점 보장 안 됨
        # 인터프리터 종료 시 전역 변수가 이미 None일 수 있음
        self.connection.close()  # AttributeError 가능!

# 올바른 패턴: context manager + weakref
import weakref

class ConnectionPool:
    def __init__(self):
        self._connections: dict[int, weakref.ref] = {}
        self._finalizer = weakref.finalize(
            self, self._cleanup, self._connections
        )

    @staticmethod
    def _cleanup(connections):
        """invoke시 self 참조 없이 정리 — prevent preventing GC"""
        for conn_ref in connections.values():
            conn = conn_ref()
            if conn is not None:
                conn.close()

    def get_connection(self, conn_id: int):
        ref = self._connections.get(conn_id)
        if ref is not None:
            conn = ref()
            if conn is not None:
                return conn
        # create new connection...

# GC 디버깅: 릭 탐지
gc.set_debug(gc.DEBUG_SAVEALL)
gc.collect()
print(f"Uncollectable: {len(gc.garbage)}")
for obj in gc.garbage[:10]:
    print(type(obj), sys.getrefcount(obj))
```

```python
# weakref 캐시 패턴 — 메모리 압박 시 자동 해제
import weakref

class ExpensiveObject:
    def __init__(self, key: str):
        self.key = key
        self.data = load_heavy_data(key)

class WeakCache:
    def __init__(self):
        self._cache: weakref.WeakValueDictionary[str, ExpensiveObject] = (
            weakref.WeakValueDictionary()
        )

    def get(self, key: str) -> ExpensiveObject:
        obj = self._cache.get(key)
        if obj is None:
            obj = ExpensiveObject(key)
            self._cache[key] = obj
        return obj
    # 외부 참조가 사라지면 자동으로 캐시에서도 제거됨
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| 기본 GC (auto) | 설정 불필요, 대부분 충분 | GC pause 예측 불가 | 일반 서비스 |
| GC disable + 수동 | latency 제어 가능 | 순환 참조 릭 위험 | 저지연 서비스 |
| threshold 튜닝 | 수집 빈도 조절 | 잘못 설정 시 메모리 폭증 | 배치 파이프라인 |
| `__slots__` 사용 | 메모리 절감 40-50%, 속도 향상 | 상속 복잡, 동적 속성 불가 | 대량 인스턴스 |
| weakref | 자동 메모리 해제 | 참조 유효성 체크 필요 | 캐시, observer 패턴 |

**Step 6 — 성장 & 심화 학습**
- CPython `Modules/gcmodule.c` — cycle detector의 실제 "subtract internal references" 알고리즘
- Instagram의 CPython GC 비활성화 사례 (copy-on-write + fork 최적화)
- PEP 442 (Safe object finalization) — `__del__`과 순환 참조의 역사
- `pymalloc` 할당자 vs `jemalloc` — 메모리 단편화 대응

**🎯 면접관 평가 기준:**
- L6 PASS: refcount + generational GC 이중 구조 설명. 순환 참조 예시. `gc.collect()` 사용법.
- L7 EXCEED: GC의 "subtract internal references" 알고리즘 설명. Instagram 사례처럼 fork + COW 시나리오에서 GC 비활성화 근거 논의. `__del__` vs `weakref.finalize` 차이 + PEP 442 맥락.
- 🚩 RED FLAG: "Python이 알아서 메모리 관리하니 신경 안 써도 됨." `gc.disable()`의 위험성 인지 못함.

---

### Q3: `__slots__`, Interning, 그리고 CPython 메모리 최적화 기법

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Python Runtime Internals

**Question:**
"수백만 개의 작은 객체를 메모리에 유지해야 하는 시스템에서 CPython의 메모리 사용을 최적화하는 전략을 설명하세요. `__slots__`, string/integer interning, `pymalloc` 할당자, struct 모듈 등을 비교하고, 각각이 어떤 레벨에서 메모리를 절약하는지 설명하세요."

---

**🧒 12살 비유:**
서랍장을 생각해봐. 보통 Python 객체는 뭐든 넣을 수 있는 큰 가방(`__dict__`)을 들고 다녀. 그런데 백만 명이 다 큰 가방을 들고 있으면 공간이 부족해. `__slots__`는 "너는 연필이랑 지우개만 넣을 수 있어"라고 정해진 작은 파우치를 주는 거야. Interning은 같은 단어가 적힌 이름표를 매번 새로 만들지 않고 하나만 만들어서 공유하는 거야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
대규모 인메모리 데이터 구조(캐시, 인덱스, 그래프)를 다루는 Staff 엔지니어는 CPython 객체의 메모리 레이아웃을 이해하고 최적화할 수 있어야 한다. 이 질문은 언어 런타임에 대한 깊이와 실제 최적화 경험을 동시에 평가한다.

**Step 2 — 핵심 기술 설명**

CPython 객체의 메모리 구조:
```
일반 객체 (with __dict__):
┌─────────────────────┐
│ ob_refcnt (8 bytes)  │
│ ob_type   (8 bytes)  │  <- PyObject_HEAD
│ __dict__  (8 bytes)  │  <- dict 포인터
│ __weakref__(8 bytes) │
│ ... (dict는 별도 56+ bytes) │
└─────────────────────┘
총: 최소 ~160 bytes (빈 인스턴스 + dict 오버헤드)

__slots__ 객체:
┌─────────────────────┐
│ ob_refcnt (8 bytes)  │
│ ob_type   (8 bytes)  │  <- PyObject_HEAD
│ slot_0    (8 bytes)  │  <- 직접 저장
│ slot_1    (8 bytes)  │
└─────────────────────┘
총: ~48 bytes (2개 속성)
```

```python
import sys

class PointRegular:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

class PointSlots:
    __slots__ = ('x', 'y')
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

regular = PointRegular(1.0, 2.0)
slotted = PointSlots(1.0, 2.0)

print(sys.getsizeof(regular))  # 48 (객체) + 104+ (__dict__)
print(sys.getsizeof(slotted))  # 48 (dict 없음)
# __dict__ 확인
print(sys.getsizeof(regular.__dict__))  # 104 (빈 dict=64, 2키=104+)

# 백만 개 객체 시 차이: ~160MB vs ~48MB
```

**String/Integer Interning:**
```python
# Python은 자동으로 특정 문자열/정수를 intern
a = "hello"
b = "hello"
print(a is b)  # True — 동일 객체 공유

# 정수: -5 ~ 256 범위는 미리 생성 (singleton)
a = 256
b = 256
print(a is b)  # True
a = 257
b = 257
print(a is b)  # False (CPython 구현 의존)

# 명시적 interning — 대량 반복 문자열에 유용
import sys
status_values = [sys.intern(s) for s in raw_statuses]
# 1M 레코드에 "active"가 800K개면 → 800K개 문자열 대신 1개 공유
```

**Step 3 — 다양한 관점**

메모리 최적화는 레이어별로 다른 도구가 적합하다:

| 레이어 | 기법 | 절감률 | 복잡도 |
|--------|------|--------|--------|
| Python 객체 | `__slots__` | 40-60% | 낮음 |
| 문자열 중복 | `sys.intern()` | 가변적 (90%+도 가능) | 낮음 |
| 컬렉션 | `array.array` vs `list` | 50-70% (숫자) | 낮음 |
| 바이너리 | `struct.pack` | 80-90% | 중간 |
| 외부 | numpy ndarray, Arrow | 90%+ | 중간 |
| 극단적 | shared memory + mmap | 프로세스 간 공유 | 높음 |

**Step 4 — 구체적 예시**

```python
# 프로덕션 예시: 대량 이벤트 인메모리 인덱스
import struct
from array import array

# Bad: 일반 클래스
class EventNaive:
    def __init__(self, ts: int, user_id: int, event_type: str):
        self.ts = ts
        self.user_id = user_id
        self.event_type = event_type
# 1M 이벤트 = ~200MB

# Good: __slots__ + interning
class EventOptimized:
    __slots__ = ('ts', 'user_id', 'event_type')
    _INTERN_CACHE: dict[str, str] = {}

    def __init__(self, ts: int, user_id: int, event_type: str):
        self.ts = ts
        self.user_id = user_id
        # event_type은 카디널리티가 낮으므로 intern
        if event_type not in self._INTERN_CACHE:
            self._INTERN_CACHE[event_type] = event_type
        self.event_type = self._INTERN_CACHE[event_type]
# 1M 이벤트 = ~72MB

# Best (극단적): struct packing + 별도 lookup
class EventStore:
    """Column-oriented 저장 — numpy 없이도 가능"""
    # 'Q' = unsigned long long (8B), 'H' = unsigned short (2B)
    STRUCT = struct.Struct('<QQH')  # ts(8B) + user_id(8B) + type_idx(2B)

    def __init__(self):
        self._buffer = bytearray()
        self._type_table: list[str] = []
        self._type_index: dict[str, int] = {}

    def append(self, ts: int, user_id: int, event_type: str):
        if event_type not in self._type_index:
            self._type_index[event_type] = len(self._type_table)
            self._type_table.append(event_type)
        type_idx = self._type_index[event_type]
        self._buffer.extend(self.STRUCT.pack(ts, user_id, type_idx))

    def get(self, index: int) -> tuple:
        offset = index * self.STRUCT.size
        ts, uid, tidx = self.STRUCT.unpack_from(self._buffer, offset)
        return ts, uid, self._type_table[tidx]
# 1M 이벤트 = ~18MB (18 bytes/event)
```

```python
# pymalloc 할당자 이해
# CPython은 512바이트 이하 객체에 pymalloc 사용
# 512바이트 초과 시 system malloc (glibc malloc/jemalloc)
# pymalloc은 arena(256KB) > pool(4KB) > block 구조

# 프로덕션 팁: PYTHONMALLOC=malloc + jemalloc으로 단편화 개선
# LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so python app.py

# tracemalloc으로 할당 추적
import tracemalloc
tracemalloc.start()
# ... 코드 실행 ...
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| `__slots__` | 간단, 속성 접근 빠름 | 동적 속성 불가, 다중 상속 주의 | 대량 인스턴스 |
| `sys.intern` | 중복 문자열 제거 | intern된 문자열은 GC 안 됨 | 낮은 카디널리티 문자열 |
| `struct.pack` | 극단적 메모리 절감 | 사용 복잡, 타입 안전성 없음 | 수천만 레코드 |
| `numpy`/`Arrow` | 벡터 연산, 메모리 효율 | 의존성, 학습 곡선 | 수치/분석 워크로드 |
| `__dict__` 제거 | dict 오버헤드 제거 | 유연성 감소 | 성능 크리티컬 경로 |

**Step 6 — 성장 & 심화 학습**
- `pymalloc` 내부: `Objects/obmalloc.c` — arena, pool, block 계층 구조
- PEP 659 (Specializing Adaptive Interpreter, 3.11) — 인라인 캐시가 메모리에 미치는 영향
- Instagram의 `__dict__` sharing 최적화 (같은 클래스 인스턴스끼리 key 배열 공유)
- `compact dict` (Python 3.6+) — 메모리 20-25% 절감한 dict 내부 구조 변화

**🎯 면접관 평가 기준:**
- L6 PASS: `__slots__` 메모리 절감 원리, interning 개념, `sys.getsizeof` 활용.
- L7 EXCEED: pymalloc 할당자 계층, dict sharing 최적화, column-oriented 저장 패턴 제시. tracemalloc 기반 프로덕션 프로파일링 경험.
- 🚩 RED FLAG: `__slots__`를 "속도 최적화"로만 이해. 메모리 프로파일링 도구 모름.

---

## 2. Async/Concurrency Deep Dive

### Q4: Event Loop 내부 — uvloop, 콜백 스케줄링, 그리고 Task 생명주기

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Async/Concurrency Deep Dive

**Question:**
"Python asyncio event loop의 내부 동작을 한 tick(iteration) 단위로 설명하세요. `call_soon`, `call_later`, I/O 폴링(epoll/kqueue)이 한 iteration에서 어떤 순서로 실행되는지, `Task`가 `Future` 위에 어떻게 구축되는지 설명하세요. uvloop이 기본 loop 대비 왜 빠른지 구체적 이유를 들어 논하세요."

---

**🧒 12살 비유:**
레스토랑 혼자 일하는 웨이터를 생각해봐. 웨이터는 (1) 먼저 바로 할 수 있는 일(call_soon: 물 갖다주기)을 처리하고, (2) 주방에 "요리 됐나?" 확인(I/O 폴링)하고, (3) "5분 뒤에 디저트 가져가기"(call_later) 알람을 체크해. 이 세 단계를 계속 반복하는 거야. uvloop은 이 웨이터가 운동화(C로 짠 libuv)를 신은 거라 더 빨리 돌아다닐 수 있는 거야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
Staff 엔지니어는 async 코드를 "작성"하는 것을 넘어 event loop의 동작을 이해해 성능 병목을 진단하고, 적절한 loop 구현을 선택하며, edge case(blocking call in async context)를 예방할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

**Event Loop 한 iteration (tick):**
```
┌──────────────────────────────────────────────┐
│              One Event Loop Iteration         │
│                                              │
│  1. _ready 큐의 콜백 실행 (call_soon)         │
│     └─ 모든 ready 콜백을 순서대로 실행        │
│                                              │
│  2. I/O 폴링 (select/epoll/kqueue)           │
│     └─ timeout = 가장 빠른 scheduled 콜백까지 │
│     └─ ready된 I/O 이벤트의 콜백 → _ready 큐  │
│                                              │
│  3. scheduled 큐 확인 (call_later/call_at)    │
│     └─ 만료된 타이머 콜백 → _ready 큐          │
│                                              │
│  4. → 1번으로 돌아감                          │
└──────────────────────────────────────────────┘
```

```python
import asyncio
import time

async def demonstrate_loop_internals():
    loop = asyncio.get_running_loop()

    order = []

    # call_soon: 현재 iteration의 _ready 큐에 추가
    loop.call_soon(lambda: order.append("call_soon_1"))
    loop.call_soon(lambda: order.append("call_soon_2"))

    # call_later: scheduled 힙에 추가, 시간 후 _ready로 이동
    loop.call_later(0.01, lambda: order.append("call_later"))

    # await은 현재 코루틴을 일시정지 → loop가 다른 작업 실행
    await asyncio.sleep(0)  # 다음 iteration으로 양보
    order.append("after_sleep_0")

    await asyncio.sleep(0.02)
    order.append("after_sleep_002")

    print(order)
    # ['call_soon_1', 'call_soon_2', 'after_sleep_0', 'call_later', 'after_sleep_002']

# Task와 Future의 관계
# Future: 미래 결과의 placeholder (low-level)
# Task(Future): coroutine을 Future로 감싸서 event loop에서 스케줄링
# await task → task의 Future가 done이 될 때까지 현재 코루틴 일시정지

async def show_task_lifecycle():
    async def worker(name: str, delay: float) -> str:
        await asyncio.sleep(delay)
        return f"{name} done"

    task = asyncio.create_task(worker("A", 0.1))
    # Task 상태: PENDING
    # 내부: task.__step()이 call_soon으로 스케줄됨
    # worker의 첫 await에서 task.__step이 I/O 콜백 등록 후 반환
    # sleep 완료 시 task.__step이 다시 call_soon → 코루틴 resume

    result = await task  # Task 상태: FINISHED
    print(result)
```

**uvloop vs 기본 asyncio loop:**
```python
# uvloop이 빠른 이유:
# 1. libuv (Node.js의 이벤트 루프) 기반 — C로 구현
# 2. 콜백 스케줄링이 C 레벨 → Python 함수 호출 오버헤드 감소
# 3. I/O 폴링 최적화: libuv의 epoll/kqueue 래핑이 더 효율적
# 4. DNS 해석이 c-ares 라이브러리 사용 (기본 loop는 getaddrinfo 스레드풀)
# 5. 타이머 관리: min-heap이 C 레벨

# 설치 및 사용
# pip install uvloop
import uvloop

# 방법 1: 전역 설정
uvloop.install()  # asyncio.run()이 uvloop 사용

# 방법 2: 명시적 (테스트 시 유용)
async def main():
    pass

loop = uvloop.new_event_loop()
loop.run_until_complete(main())

# 벤치마크 차이 (HTTP 에코 서버 기준):
# 기본 asyncio:  ~15,000 req/s
# uvloop:        ~60,000 req/s (4x)
# 원인: loop iteration당 Python ↔ C 전환 횟수 감소
```

**Step 3 — 다양한 관점**

| 관점 | 기본 asyncio | uvloop | 비고 |
|------|-------------|--------|------|
| 순수 성능 | 기준선 | 2-4x 빠름 | I/O 집약 워크로드 |
| 디버깅 | Python 코드 추적 가능 | C 레벨이라 traceback 제한 | 개발 시 기본 loop 사용 권장 |
| 호환성 | 모든 플랫폼 | Linux/macOS (Windows 미지원) | CI에서 주의 |
| 메모리 | 약간 더 사용 | libuv 오버헤드 | 대부분 무시 가능 |
| 생태계 | 표준 | uvicorn 기본 채택 | 프로덕션 de facto |

**Step 4 — 구체적 예시**

```python
# 프로덕션 안티패턴: event loop 블로킹
import asyncio
import time

async def bad_handler():
    # 🚫 동기 I/O가 event loop를 블로킹!
    data = open("/dev/urandom", "rb").read(1024 * 1024)  # 블로킹 I/O
    time.sleep(0.1)  # 전체 서버가 0.1초 멈춤
    result = heavy_cpu_work(data)  # CPU-bound도 블로킹

async def good_handler():
    loop = asyncio.get_running_loop()

    # I/O: aiofiles 또는 executor
    async with aiofiles.open("/dev/urandom", "rb") as f:
        data = await f.read(1024 * 1024)

    # CPU-bound: ProcessPoolExecutor
    result = await loop.run_in_executor(
        process_pool, heavy_cpu_work, data
    )

    return result

# 블로킹 감지: asyncio debug mode
# PYTHONASYNCIODEBUG=1 python app.py
# 또는
asyncio.get_event_loop().set_debug(True)
# slow_callback_duration 초과 시 warning 출력
asyncio.get_event_loop().slow_callback_duration = 0.05  # 50ms
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| asyncio 기본 | 표준, 디버깅 용이 | 상대적 저성능 | 개발/테스트 |
| uvloop | 4x 성능 | Windows 미지원, 디버깅 어려움 | 프로덕션 Linux |
| trio | structured concurrency 강제 | asyncio 비호환 | 새 프로젝트, 안전성 우선 |
| anyio | trio/asyncio 추상화 | 추가 레이어 | 라이브러리 코드 |

**Step 6 — 성장 & 심화 학습**
- CPython `Lib/asyncio/base_events.py`의 `_run_once()` 메서드 — 실제 tick 구현
- libuv 소스의 `uv_run()` — uvloop의 핵심
- structured concurrency: PEP 654 (ExceptionGroup) + `asyncio.TaskGroup` (3.11+)
- Edge-triggered vs Level-triggered epoll — 고성능 서버의 선택

**🎯 면접관 평가 기준:**
- L6 PASS: event loop iteration의 3단계 설명. Task/Future 관계. uvloop의 존재와 성능 이점.
- L7 EXCEED: `_run_once()`의 실제 동작, I/O 폴링 timeout 계산 로직, uvloop이 빠른 구체적 이유(C-level callback, c-ares DNS). 블로킹 감지를 위한 debug mode 활용.
- 🚩 RED FLAG: "await이 멀티스레딩이다"라고 혼동. event loop가 blocking call 시 어떤 일이 일어나는지 모름.

---

### Q5: asyncio vs threading vs multiprocessing — 언제 무엇을 쓰는가

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Async/Concurrency Deep Dive

**Question:**
"10,000개의 외부 API 호출, 이미지 리사이징 파이프라인, 실시간 웹소켓 서버 — 이 세 가지 워크로드에 각각 어떤 concurrency 모델을 선택하겠습니까? 선택 근거와 함께 혼합 사용 패턴, 그리고 각 모델의 failure mode를 프로덕션 관점에서 설명하세요."

---

**🧒 12살 비유:**
요리를 해야 하는데 세 가지 방법이 있어. (1) 혼자서 여러 냄비를 동시에 봐(async) — 파스타 물 끓는 동안 소스를 저어. (2) 친구를 불러서 같은 주방에서 함께 해(threading) — 같은 냉장고를 같이 쓰니 부딪힐 수 있어. (3) 각자 다른 주방에서 해(multiprocessing) — 안 부딪히지만 재료를 전달하려면 복도를 왔다 갔다 해야 해.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
이 질문은 실제 시스템 설계 판단력을 본다. 교과서적 "I/O-bound면 async, CPU-bound면 multiprocessing"을 넘어, 실제 프로덕션에서의 경계가 모호한 상황, 혼합 워크로드, failure mode에 대한 이해를 평가한다.

**Step 2 — 핵심 기술 설명**

```python
# 시나리오 1: 10,000개 외부 API 호출 — asyncio + 세마포어
import asyncio
import aiohttp
from dataclasses import dataclass

@dataclass
class APIResult:
    url: str
    status: int
    body: bytes
    error: str | None = None

async def fetch_all(urls: list[str], max_concurrent: int = 100) -> list[APIResult]:
    semaphore = asyncio.Semaphore(max_concurrent)
    connector = aiohttp.TCPConnector(
        limit=max_concurrent,
        limit_per_host=20,       # 호스트당 커넥션 제한
        ttl_dns_cache=300,       # DNS 캐시
        enable_cleanup_closed=True
    )
    timeout = aiohttp.ClientTimeout(total=30, connect=5)

    async def fetch_one(session: aiohttp.ClientSession, url: str) -> APIResult:
        async with semaphore:
            try:
                async with session.get(url, timeout=timeout) as resp:
                    body = await resp.read()
                    return APIResult(url=url, status=resp.status, body=body)
            except Exception as e:
                return APIResult(url=url, status=0, body=b"", error=str(e))

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [asyncio.create_task(fetch_one(session, url)) for url in urls]
        # gather vs TaskGroup
        # gather: 하나 실패해도 나머지 계속 (return_exceptions=True)
        # TaskGroup: 하나 실패 시 나머지 취소 (structured concurrency)
        results = await asyncio.gather(*tasks, return_exceptions=False)
        return results

# 왜 threading이 아닌가?
# - 10,000 스레드 = ~80GB 스택 메모리 (기본 8MB/스레드)
# - 스레드 수를 줄이면(ThreadPool 100) 처리량 감소
# - asyncio는 코루틴당 ~2KB → 10,000개도 ~20MB
```

```python
# 시나리오 2: 이미지 리사이징 — multiprocessing + 큐
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image
import io

def resize_image_sync(image_bytes: bytes, target_size: tuple[int, int]) -> bytes:
    """각 프로세스에서 독립 실행 — GIL 없이 CPU 코어 100% 활용"""
    img = Image.open(io.BytesIO(image_bytes))
    img = img.resize(target_size, Image.LANCZOS)
    output = io.BytesIO()
    img.save(output, format="WEBP", quality=85)
    return output.getvalue()

async def resize_batch(images: list[bytes], target: tuple[int, int]) -> list[bytes]:
    """async 핸들러에서 CPU-bound 작업을 ProcessPool로 오프로드"""
    loop = asyncio.get_running_loop()
    # worker 수 = CPU 코어 수 (I/O가 아니므로 코어 이상 무의미)
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as pool:
        futures = [
            loop.run_in_executor(pool, resize_image_sync, img, target)
            for img in images
        ]
        return await asyncio.gather(*futures)

# 왜 threading이 아닌가?
# - Pillow의 이미지 처리는 Python 레벨 코드 비중 높음 → GIL 병목
# - 4코어에서 threading: 1코어만 사용 (GIL)
# - 4코어에서 multiprocessing: 4코어 모두 사용 (4x 처리량)
#
# 주의: ProcessPoolExecutor는 인자를 pickle → IPC 전송
# 큰 이미지 배열은 shared_memory 고려
```

```python
# 시나리오 3: 실시간 웹소켓 — asyncio + broadcast
from collections import defaultdict
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self._rooms: dict[str, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, room: str, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self._rooms[room].add(ws)

    async def disconnect(self, room: str, ws: WebSocket):
        async with self._lock:
            self._rooms[room].discard(ws)

    async def broadcast(self, room: str, message: str):
        async with self._lock:
            connections = list(self._rooms[room])
        # lock 밖에서 전송 — 블로킹 최소화
        dead = []
        for ws in connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        if dead:
            async with self._lock:
                for ws in dead:
                    self._rooms[room].discard(ws)

manager = ConnectionManager()

@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await manager.connect(room, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(room, data)
    except WebSocketDisconnect:
        await manager.disconnect(room, websocket)

# 왜 asyncio인가?
# - 각 WebSocket은 대부분 idle (I/O-bound)
# - 10,000 동시 연결 시 스레드 모델은 비현실적
# - 메시지 수신/발신이 비동기 I/O의 전형
```

**Step 3 — 다양한 관점**

**Failure mode 비교:**

| 모델 | 대표 Failure Mode | 영향 범위 | 대응 |
|------|-------------------|-----------|------|
| asyncio | blocking call이 loop 정지 | 전체 서버 | debug mode, watchdog |
| threading | race condition, deadlock | 데이터 손상 | lock 최소화, 불변 객체 |
| multiprocessing | 자식 프로세스 OOM kill | 해당 프로세스 | 모니터링, 재시작 정책 |

**Step 4 — 구체적 예시 (혼합 패턴)**

```python
# 프로덕션 혼합 패턴: FastAPI + async + process pool
from contextlib import asynccontextmanager
from concurrent.futures import ProcessPoolExecutor

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 프로세스 풀 생성
    app.state.process_pool = ProcessPoolExecutor(max_workers=4)
    yield
    # 종료 시 정리
    app.state.process_pool.shutdown(wait=True)

app = FastAPI(lifespan=lifespan)

@app.post("/analyze")
async def analyze(file: UploadFile):
    content = await file.read()                         # I/O: async
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(                # CPU: process pool
        app.state.process_pool,
        cpu_intensive_analysis,
        content
    )
    await db.save(result)                               # I/O: async
    await notify_webhook(result.summary)                # I/O: async
    return result
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| Pure asyncio | 경량, 수만 동시 연결 | CPU-bound 불가, 생태계 제약 | 웹 서버, API 게이트웨이 |
| asyncio + ProcessPool | 혼합 워크로드 처리 | IPC 직렬화 오버헤드 | 일반적 웹 서비스 |
| threading | 기존 동기 라이브러리 활용 | GIL, race condition | 레거시 통합 |
| Celery/분산 큐 | 내결함성, 수평 확장 | 인프라 복잡도 | 대규모 배치 |

**Step 6 — 성장 & 심화 학습**
- `asyncio.to_thread()` (3.9+) — `loop.run_in_executor(None, ...)` 의 syntactic sugar
- `TaskGroup` (3.11+) vs `gather` — structured concurrency의 이점
- `multiprocessing.shared_memory` (3.8+) — IPC 없이 대용량 데이터 공유
- Go의 goroutine과 비교 — M:N 스케줄링 vs Python의 1:1

**🎯 면접관 평가 기준:**
- L6 PASS: 세 워크로드에 적절한 모델 선택 + 근거. Semaphore를 이용한 동시성 제한.
- L7 EXCEED: failure mode 분석, 혼합 패턴의 실제 코드, 메모리/IPC 오버헤드 수치 제시. shared_memory 활용.
- 🚩 RED FLAG: 모든 상황에 하나의 모델만 제시. 스레드 10,000개 생성 제안.

---

### Q6: async가 오히려 느려지는 경우와 진단

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Async/Concurrency Deep Dive

**Question:**
"async/await을 도입했는데 동기 코드보다 성능이 떨어지는 시나리오들을 설명하세요. 각 시나리오의 근본 원인, 진단 방법, 그리고 해결 전략을 제시하세요."

---

**🧒 12살 비유:**
한 번에 한 과목씩 공부하면(동기) 집중이 잘 돼. 그런데 5과목을 번갈아 공부하면(async) 책 꺼냈다 넣었다 하는 시간(context switching cost)이 생겨. 특히 한 과목이 수학(CPU-bound)이면 어차피 다른 과목은 수학 끝날 때까지 못 해. 이럴 때 번갈아 하는 건 오히려 시간 낭비야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
"async는 항상 빠르다"는 흔한 오해다. Staff 엔지니어는 async의 한계를 이해하고, 성능 저하 시 근본 원인을 진단해 올바른 결정을 내릴 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

**시나리오 1: 코루틴 오버헤드 > I/O 대기 시간**
```python
# 매우 빠른 로컬 캐시 조회 — async가 오히려 느림
import asyncio
import time
import redis
import redis.asyncio as aioredis

# 동기: ~0.1ms/call (Redis 로컬 연결)
def get_sync(r: redis.Redis, key: str):
    return r.get(key)

# 비동기: ~0.3ms/call (코루틴 생성 + event loop 스케줄링 오버헤드)
async def get_async(r: aioredis.Redis, key: str):
    return await r.get(key)

# 원인:
# 1. 코루틴 객체 생성 비용 (~0.5μs)
# 2. event loop에 콜백 등록/해제
# 3. 컨텍스트 스위칭 (coroutine frame push/pop)
# 로컬 Redis RTT(0.1ms)에서 이 오버헤드가 유의미함
#
# 해결: 동시 요청이 수백 이상일 때만 async 유리
# 단건 조회 위주라면 동기가 빠름
```

**시나리오 2: CPU-bound 작업이 event loop 블로킹**
```python
# 🚫 async 함수인데 실제로는 CPU-bound
async def bad_async_handler(data: bytes):
    # JSON 파싱 — 작은 데이터면 괜찮지만 100MB는 event loop 블로킹
    import json
    parsed = json.loads(data)  # 동기 CPU 작업!
    # 이 동안 다른 모든 요청이 대기

    # 진단: asyncio debug mode
    # WARNING: Executing <Task ...> took 2.5 seconds

    return process(parsed)

# ✅ 수정
async def good_async_handler(data: bytes):
    import orjson  # C 확장 + 더 빠름
    # 작은 데이터: 그냥 호출 (충분히 빠름)
    if len(data) < 1_000_000:  # 1MB 미만
        return orjson.loads(data)
    # 큰 데이터: executor로 오프로드
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, orjson.loads, data)
```

**시나리오 3: async 전염(contagion) — 라이브러리 비호환**
```python
# 동기 라이브러리를 async에서 사용할 때 성능 저하
from sqlalchemy import create_engine  # 동기 엔진!
from sqlalchemy.orm import Session

async def bad_db_query():
    # 동기 DB 드라이버가 event loop 블로킹
    with Session(engine) as session:
        result = session.execute(text("SELECT * FROM big_table"))
        # 이 동안 전체 서버 정지
        return result.all()

# asyncio.to_thread는 해결책이지만 차선책
async def ok_db_query():
    def _sync():
        with Session(engine) as session:
            return session.execute(text("SELECT * FROM big_table")).all()
    return await asyncio.to_thread(_sync)

# 최선: 네이티브 async 드라이버
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
async_engine = create_async_engine("postgresql+asyncpg://...")

async def good_db_query():
    async with AsyncSession(async_engine) as session:
        result = await session.execute(text("SELECT * FROM big_table"))
        return result.all()
```

**시나리오 4: Task 과다 생성 (task thrashing)**
```python
# 🚫 100만 개 Task를 한 번에 생성
async def bad_mass_tasks():
    tasks = [asyncio.create_task(process(item)) for item in million_items]
    return await asyncio.gather(*tasks)
    # 문제: 100만 Task 객체 = ~1GB 메모리
    # event loop의 _ready 큐가 거대해짐

# ✅ 배치 + 세마포어
async def good_mass_tasks(items: list, batch_size: int = 1000):
    semaphore = asyncio.Semaphore(batch_size)

    async def bounded_process(item):
        async with semaphore:
            return await process(item)

    tasks = [asyncio.create_task(bounded_process(item)) for item in items]
    return await asyncio.gather(*tasks)

# ✅✅ 더 나은 방법: async generator + batching
async def best_mass_tasks(items: list, batch_size: int = 1000):
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = await asyncio.gather(
            *[process(item) for item in batch]
        )
        results.extend(batch_results)
    return results
```

**Step 3 — 다양한 관점**

| async가 느린 경우 | 근본 원인 | 진단 방법 | 해결책 |
|-------------------|-----------|-----------|--------|
| 로컬 캐시 단건 조회 | 코루틴 오버헤드 > I/O 시간 | 벤치마크 비교 | 동기 유지 |
| CPU-bound in async | event loop 블로킹 | debug mode, py-spy | executor/프로세스 풀 |
| 동기 라이브러리 호출 | 전체 loop 정지 | slow callback 경고 | native async 드라이버 |
| 과다 Task 생성 | 메모리 + 스케줄링 부하 | tracemalloc, task count | 세마포어, 배치 |
| 과도한 lock contention | `asyncio.Lock` 대기 체인 | task dump, profiling | lock-free 구조, sharding |

**Step 4 — 진단 도구 모음**

```python
# 1. asyncio debug mode
import asyncio
import logging
logging.basicConfig(level=logging.DEBUG)
# PYTHONASYNCIODEBUG=1 python app.py

# 2. Task 수 모니터링
def log_task_count():
    tasks = asyncio.all_tasks()
    print(f"Active tasks: {len(tasks)}")
    for task in list(tasks)[:5]:
        print(f"  {task.get_name()}: {task.get_coro()}")

# 3. 커스텀 slow-task 감지 미들웨어 (FastAPI)
import time

@app.middleware("http")
async def slow_request_detector(request, call_next):
    start = time.monotonic()
    response = await call_next(request)
    duration = time.monotonic() - start
    if duration > 1.0:  # 1초 초과
        logger.warning(
            "Slow request",
            path=request.url.path,
            duration=duration,
            method=request.method,
        )
    return response
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| 순수 동기 | 단순, 디버깅 쉬움 | 동시성 제한 | 낮은 동시성, CPU-bound |
| async 전면 채택 | 높은 동시 처리 | 전염 문제, 생태계 제약 | 고동시성 I/O 서비스 |
| 혼합 (async + executor) | 유연성 | 복잡도 증가 | 혼합 워크로드 |
| Gunicorn 멀티워커 | 프로세스 격리 | 메모리 사용 증가 | 프로세스 레벨 병렬 |

**Step 6 — 성장 & 심화 학습**
- `asyncio.TaskGroup` — structured concurrency로 Task 생명주기 관리
- `aiomonitor` — 실행 중 async 앱의 Task 상태 실시간 모니터링
- Python 3.12의 `asyncio.Runner` — loop 생명주기 관리 개선
- async 프로파일링: `yappi`(async 지원), `py-spy`(wall-time 프로파일링)

**🎯 면접관 평가 기준:**
- L6 PASS: CPU-bound 블로킹, 동기 라이브러리 문제 설명. Semaphore 패턴.
- L7 EXCEED: 코루틴 오버헤드 수치, task thrashing 메커니즘, debug mode 활용. "async가 불필요한 경우"를 자신 있게 제시.
- 🚩 RED FLAG: "async는 항상 빠르다." 블로킹 코드를 async 함수 안에 넣어도 문제없다고 생각.

---

## 3. FastAPI Internals & Production

### Q7: Starlette 기반 구조와 Middleware 체인 실행 순서

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: FastAPI Internals & Production

**Question:**
"FastAPI가 Starlette 위에 어떻게 구축되어 있는지 계층 구조를 설명하세요. ASGI 요청이 들어올 때 middleware 체인이 어떤 순서로 실행되고, `app.add_middleware`와 `@app.middleware("http")`의 차이, 그리고 ASGI middleware vs HTTP middleware의 차이를 설명하세요. 미들웨어 순서 실수로 인한 프로덕션 버그 사례도 논하세요."

---

**🧒 12살 비유:**
택배를 보내는 것처럼 생각해봐. 택배(요청)가 오면 여러 검문소(미들웨어)를 거쳐. 첫 번째 검문소는 보안 검사(CORS), 두 번째는 무게 측정(logging), 세 번째는 라벨 확인(auth). 그런데 중요한 건 — 들어올 때는 1→2→3 순서지만, 돌아올 때(응답)는 3→2→1 역순이야. 양파 껍질처럼 감싸는 구조(onion model)야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
FastAPI/Starlette의 미들웨어 실행 순서는 프로덕션에서 CORS 에러, 인증 우회, 로깅 누락 등의 버그 원인이 된다. Staff 엔지니어는 프레임워크 내부를 이해해 이런 문제를 설계 단계에서 방지해야 한다.

**Step 2 — 핵심 기술 설명**

**FastAPI 계층 구조:**
```
┌──────────────────────────────────────────┐
│               FastAPI (app)               │
│  - Pydantic 검증, OpenAPI 자동 생성       │
│  - 의존성 주입 시스템                     │
│  - APIRouter                             │
├──────────────────────────────────────────┤
│              Starlette                    │
│  - Routing, Request/Response 객체        │
│  - Middleware 체인                        │
│  - WebSocket, Static Files              │
├──────────────────────────────────────────┤
│           ASGI Interface                  │
│  - async def __call__(scope, receive,    │
│                        send)              │
├──────────────────────────────────────────┤
│        Uvicorn / Hypercorn               │
│  - ASGI 서버, HTTP 파싱                  │
│  - uvloop event loop                     │
└──────────────────────────────────────────┘
```

**미들웨어 실행 순서 — Onion Model:**
```python
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

# add_middleware는 LIFO 순서 (마지막에 추가된 것이 가장 바깥)
# 코드 순서와 실행 순서가 반대!

# 3번째 추가 → 가장 바깥 (요청 시 첫 번째 실행)
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# 2번째 추가 → 중간
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print("LOG: request in")           # 요청 시 2번째
        response = await call_next(request)
        print("LOG: response out")          # 응답 시 2번째
        return response
app.add_middleware(LoggingMiddleware)

# 1번째 추가 → 가장 안쪽 (요청 시 마지막 실행)
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print("AUTH: check")               # 요청 시 3번째
        response = await call_next(request)
        print("AUTH: done")                 # 응답 시 1번째
        return response
app.add_middleware(AuthMiddleware)

# 실행 순서:
# 요청 → CORS → Logging(in) → Auth(check) → Route Handler
# 응답 ← CORS ← Logging(out) ← Auth(done) ← Route Handler
```

**ASGI middleware vs HTTP middleware:**
```python
# 1. BaseHTTPMiddleware (HTTP 수준)
# - Request/Response 객체 사용
# - 편리하지만 streaming response에 문제 있음
# - response body를 메모리에 완전히 읽음!
class BadStreamingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # ⚠️ StreamingResponse의 body가 여기서 소비됨
        # 큰 파일 다운로드 시 메모리 폭발
        return response

# 2. Pure ASGI middleware (ASGI 수준)
# - scope, receive, send 직접 다룸
# - streaming 호환, 더 세밀한 제어
# - 구현 복잡도 높음
class PureASGIMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # 요청 헤더 조작 가능
            headers = dict(scope.get("headers", []))
            # request-id 주입
            import uuid
            request_id = str(uuid.uuid4())
            scope["headers"] = [
                *scope.get("headers", []),
                (b"x-request-id", request_id.encode()),
            ]

            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    # 응답 헤더에 request-id 추가
                    headers = list(message.get("headers", []))
                    headers.append((b"x-request-id", request_id.encode()))
                    message["headers"] = headers
                await send(message)

            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)

# 사용
app.add_middleware(PureASGIMiddleware)  # Pure ASGI는 이렇게 추가
```

**Step 3 — 다양한 관점**

| 측면 | BaseHTTPMiddleware | Pure ASGI | `@app.middleware("http")` |
|------|-------------------|-----------|--------------------------|
| 사용성 | 쉬움 | 어려움 | 매우 쉬움 |
| Streaming | 비호환 (body 버퍼링) | 완전 호환 | 비호환 |
| WebSocket | 미지원 | 지원 | 미지원 |
| 성능 | 약간의 오버헤드 | 최적 | BaseHTTPMiddleware와 동일 |
| 순서 제어 | LIFO | LIFO | 등록 역순 |

**Step 4 — 프로덕션 버그 사례**

```python
# 버그 1: CORS middleware가 Auth보다 안쪽 → preflight 실패
# 잘못된 순서
app.add_middleware(CORSMiddleware, ...)  # 1번째 추가 → 안쪽
app.add_middleware(AuthMiddleware)        # 2번째 추가 → 바깥쪽
# OPTIONS preflight → AuthMiddleware가 먼저 → 토큰 없어서 401
# CORS 헤더가 응답에 안 붙음 → 브라우저에서 CORS 에러

# 올바른 순서: CORS가 가장 바깥 (마지막에 add_middleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(CORSMiddleware, ...)  # 가장 바깥 → preflight 먼저 처리

# 버그 2: BaseHTTPMiddleware가 SSE streaming을 깨뜨림
from sse_starlette.sse import EventSourceResponse

@app.get("/stream")
async def stream_events():
    async def event_generator():
        for i in range(100):
            yield {"data": f"event {i}"}
            await asyncio.sleep(0.1)
    return EventSourceResponse(event_generator())

# BaseHTTPMiddleware의 dispatch가 response body를 소비 → stream 깨짐
# 해결: Pure ASGI middleware 사용 또는 해당 경로 제외

# 버그 3: exception handler와 middleware 순서 충돌
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

# exception_handler는 middleware 안쪽에서 동작
# middleware에서 발생한 예외는 exception_handler가 잡지 못함!
# → middleware 내부에서 자체 try/except 필요
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| BaseHTTPMiddleware | 간단, Request/Response 접근 | streaming 비호환 | 인증, 로깅 |
| Pure ASGI | 완전 제어, streaming 호환 | 구현 복잡 | 고성능, streaming |
| Dependencies (Depends) | route-specific, 타입 안전 | 전역 적용 어려움 | 인증, DB 세션 |
| Starlette 내장 | 검증됨, 안정적 | 커스터마이즈 제한 | CORS, GZip, TrustedHost |

**Step 6 — 성장 & 심화 학습**
- Starlette 소스: `starlette/middleware/base.py` — `BaseHTTPMiddleware`의 body 버퍼링 구현
- ASGI spec 3.0 — `scope`, `receive`, `send`의 정확한 프로토콜
- `asgi-correlation-id` — 분산 추적 미들웨어 레퍼런스 구현
- Uvicorn의 HTTP/1.1 vs HTTP/2 처리 차이

**🎯 면접관 평가 기준:**
- L6 PASS: 미들웨어 실행 순서(onion model). CORS/Auth 순서 문제. BaseHTTPMiddleware vs Pure ASGI 차이.
- L7 EXCEED: ASGI 프로토콜 수준에서의 middleware 구현. streaming 비호환 문제의 근본 원인. exception handler vs middleware 범위 차이.
- 🚩 RED FLAG: 미들웨어 순서가 코드 작성 순서와 같다고 생각. ASGI 프로토콜을 모름.

---

### Q8: FastAPI의 의존성 주입 — Lifecycle, Caching, 그리고 함정

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: FastAPI Internals & Production

**Question:**
"FastAPI의 `Depends` 시스템이 내부적으로 어떻게 동작하는지 설명하세요. dependency의 캐싱 메커니즘, generator dependency의 lifecycle, 중첩 dependency의 해석 순서, 그리고 `Depends`를 사용한 DI가 전통적 DI 프레임워크와 어떻게 다른지 비교하세요. 프로덕션에서 만난 DI 관련 함정도 공유하세요."

---

**🧒 12살 비유:**
레고 조립 설명서처럼 생각해봐. "자동차를 만들려면 바퀴 4개가 필요하고(Depends), 바퀴를 만들려면 타이어와 림이 필요해(중첩 Depends)." FastAPI는 이 설명서를 읽고 필요한 부품을 밑에서부터 자동으로 만들어줘. 그리고 같은 요청에서 "바퀴" 부품이 두 번 필요하면 한 번만 만들어서 재사용해(캐싱).

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
DI 시스템은 FastAPI 앱의 핵심 구조를 결정한다. 잘못 사용하면 메모리 릭, 커넥션 풀 고갈, 테스트 불가능한 구조가 된다. Staff 엔지니어는 DI의 내부 동작을 이해해 올바른 설계를 이끌어야 한다.

**Step 2 — 핵심 기술 설명**

**DI 해석(Resolution) 과정:**
```python
from fastapi import FastAPI, Depends, Request
from typing import Annotated

app = FastAPI()

# FastAPI 내부에서 일어나는 일:
# 1. 엔드포인트의 시그니처를 inspect
# 2. Depends 파라미터 발견 → 의존성 그래프(DAG) 구성
# 3. 위상 정렬(topological sort)로 해석 순서 결정
# 4. 요청마다 dependency_cache(dict) 생성
# 5. 같은 callable이 여러 곳에서 의존되면 캐시에서 재사용

class DBSession:
    def __init__(self):
        self.id = id(self)

async def get_db() -> DBSession:
    db = DBSession()
    print(f"Created DB session {db.id}")
    try:
        yield db  # generator dependency
    finally:
        print(f"Closed DB session {db.id}")
        # cleanup (session.close() 등)

async def get_current_user(
    db: Annotated[DBSession, Depends(get_db)]
) -> dict:
    # get_db는 이미 위에서 해석됨 → 캐시에서 재사용
    return {"user_id": 1}

async def get_user_permissions(
    db: Annotated[DBSession, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)]
) -> list[str]:
    # get_db가 세 번 참조되지만 실제 생성은 1번!
    # dependency_cache = {get_db: <DBSession>, get_current_user: {...}}
    return ["read", "write"]

@app.get("/protected")
async def protected_route(
    permissions: Annotated[list[str], Depends(get_user_permissions)],
    db: Annotated[DBSession, Depends(get_db)],
):
    # 해석 순서: get_db → get_current_user → get_user_permissions
    # get_db는 전체에서 1번만 호출됨 (same request scope)
    return {"permissions": permissions, "db_id": db.id}
```

**캐싱 메커니즘:**
```python
# use_cache=True (기본값): 같은 요청 내에서 같은 callable → 같은 인스턴스
# use_cache=False: 매번 새로 생성

async def get_db():
    return create_session()

# 기본: 캐시됨 (같은 세션 공유)
db1: Annotated[Session, Depends(get_db)]
db2: Annotated[Session, Depends(get_db)]
# db1 is db2 → True

# 캐시 비활성화: 별도 세션
db3: Annotated[Session, Depends(get_db, use_cache=False)]
# db3 is db1 → False

# ⚠️ 함정: 캐시 키는 callable 자체 (id)
# lambda나 partial은 매번 새 객체 → 캐시 안 됨!
# Bad
Depends(lambda: get_db_with_schema("tenant_a"))  # 매번 새 lambda!

# Good: 명시적 함수 정의
def get_tenant_a_db():
    return get_db_with_schema("tenant_a")
Depends(get_tenant_a_db)  # 동일 함수 객체 → 캐시 동작
```

**Generator dependency lifecycle:**
```python
# Generator dependency는 try/finally 패턴 — context manager와 유사
async def get_db_session():
    session = AsyncSession(engine)
    try:
        yield session
        # yield 이후: 요청 처리 완료 후 실행
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

# 실행 순서:
# 1. yield 전: 리소스 획득 (session 생성)
# 2. yield: 엔드포인트에 session 전달, 엔드포인트 실행
# 3. yield 후 (정상): commit
# 4. except (예외 시): rollback
# 5. finally: 항상 close

# ⚠️ 중요: response가 이미 전송된 후에 finally가 실행됨
# → finally에서 예외 발생 시 클라이언트는 이미 200을 받았을 수 있음
```

**Step 3 — 다양한 관점**

| 비교 | FastAPI Depends | Spring DI | Python inject 라이브러리 |
|------|----------------|-----------|------------------------|
| 스코프 | Request (기본) | Singleton/Prototype/Request | 설정 가능 |
| 해석 시점 | 요청마다 런타임 | 앱 시작 시 컴파일 | 앱 시작 시 |
| 타입 안전성 | 런타임 (Pydantic) | 컴파일 타임 | 런타임 |
| 테스트 | `app.dependency_overrides` | `@MockBean` | mock/patch |
| 성능 | 매 요청 그래프 해석 | 시작 시 1회 | 시작 시 1회 |

**Step 4 — 프로덕션 함정과 해결**

```python
# 함정 1: 무거운 의존성을 매 요청 생성
# 🚫
async def get_ml_model():
    model = load_model("big_model.pt")  # 500ms + 2GB 메모리
    return model

# ✅ 앱 레벨 캐싱
from functools import lru_cache

@lru_cache(maxsize=1)
def get_ml_model_cached():
    return load_model("big_model.pt")

async def get_ml_model():
    return get_ml_model_cached()  # 첫 호출만 로드

# ✅✅ 더 나은 방법: lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = load_model("big_model.pt")
    yield
    del app.state.model

async def get_ml_model(request: Request):
    return request.app.state.model
```

```python
# 함정 2: Generator dependency에서 BackgroundTask와의 충돌
from fastapi import BackgroundTasks

async def get_db():
    session = AsyncSession(engine)
    try:
        yield session
    finally:
        await session.close()  # ← 요청 완료 후 즉시 실행

@app.post("/process")
async def process_data(
    db: Annotated[AsyncSession, Depends(get_db)],
    background_tasks: BackgroundTasks,
):
    data = await db.execute(query)

    # 🚫 BackgroundTask에서 db 사용 → session이 이미 닫힘!
    background_tasks.add_task(background_work, db, data)

    # ✅ BackgroundTask에서 새 session 생성
    async def safe_background_work(data):
        async with AsyncSession(engine) as bg_session:
            await do_work(bg_session, data)

    background_tasks.add_task(safe_background_work, data)
    return {"status": "accepted"}
```

```python
# 함정 3: dependency_overrides 테스트 후 정리 안 함
# ✅ pytest fixture로 안전하게
@pytest.fixture
def override_db(app):
    async def mock_db():
        yield mock_session

    app.dependency_overrides[get_db] = mock_db
    yield
    app.dependency_overrides.clear()  # 필수 정리!
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| Depends (함수) | 간단, 타입 힌트 호환 | Singleton 패턴 불편 | 대부분 |
| Depends (클래스) | 설정 주입 가능 | 보일러플레이트 | 설정 기반 의존성 |
| `app.state` | 앱 레벨 싱글턴 | DI 그래프 밖 | ML 모델, 커넥션 풀 |
| `dependency_overrides` | 테스트 편의 | 전역 상태 변경 | 통합 테스트 |

**Step 6 — 성장 & 심화 학습**
- FastAPI 소스: `fastapi/dependencies/utils.py` — `solve_dependencies` 함수
- Starlette `Request.state` vs `app.state` — 스코프 차이
- `python-inject`, `dependency-injector` — 전통적 DI 프레임워크와 비교
- `Annotated` (PEP 593) + `Depends` — 현대적 타입 안전 DI 패턴

**🎯 면접관 평가 기준:**
- L6 PASS: 캐싱 동작, generator dependency lifecycle, `dependency_overrides` 테스트 패턴.
- L7 EXCEED: DAG 해석 과정, 캐시 키 메커니즘(callable identity), BackgroundTask와 generator dependency 충돌 문제.
- 🚩 RED FLAG: 매 요청 무거운 리소스 재생성. generator dependency의 cleanup 시점 모름.

---

### Q9: BackgroundTasks vs Celery vs 기타 비동기 작업 처리

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: FastAPI Internals & Production

**Question:**
"FastAPI의 BackgroundTasks, Celery, arq, Dramatiq 등 다양한 비동기 작업 처리 옵션을 비교하세요. 각각의 내부 동작, 실패 처리, 재시도 메커니즘, 그리고 어떤 규모와 요구사항에서 어떤 도구를 선택해야 하는지 프로덕션 경험 기반으로 설명하세요."

---

**🧒 12살 비유:**
피자 가게를 생각해봐. BackgroundTasks는 피자 배달 나간 뒤 카운터에서 테이블 닦는 거야(간단, 같은 사람). Celery는 별도 배달부를 고용하는 거야(다른 서버에서 실행). 배달부가 사고 나면 다른 배달부가 대신 가고(retry), 어떤 배달이 어디까지 갔는지 추적도 돼(task monitoring). 가게가 작으면 직접 닦는 게 빠르고, 크면 배달부를 쓰는 게 맞아.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
비동기 작업 처리는 시스템 아키텍처의 핵심 결정이다. 잘못된 선택은 작업 유실, 중복 실행, 리소스 고갈로 이어진다. Staff 엔지니어는 규모와 요구사항에 맞는 도구를 선택하고 그 한계를 이해해야 한다.

**Step 2 — 핵심 기술 설명**

**BackgroundTasks 내부 동작:**
```python
# BackgroundTasks는 response 전송 후 같은 프로세스에서 실행
# 내부: response.background 속성에 태스크 추가
# Starlette의 Response.__call__에서 body 전송 후 background 실행

from fastapi import BackgroundTasks
import asyncio

@app.post("/notify")
async def send_notification(
    background_tasks: BackgroundTasks,
    user_id: int,
):
    # 이 태스크들은 response 전송 후 순차 실행
    background_tasks.add_task(send_email, user_id)
    background_tasks.add_task(send_push, user_id)
    return {"status": "accepted"}  # 즉시 응답

# ⚠️ 한계:
# 1. 서버 재시작 시 진행 중 태스크 유실
# 2. 재시도 메커니즘 없음
# 3. 같은 이벤트 루프에서 실행 → CPU-bound 시 다음 요청 지연
# 4. 결과 추적 불가 (fire-and-forget)
# 5. 수평 확장 불가 (해당 프로세스에서만 실행)
```

```python
# Celery: 분산 태스크 큐
from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,           # 완료 후 ACK → 실패 시 재실행
    reject_on_worker_lost=True,  # 워커 죽으면 재큐잉
)
def process_video(self, video_id: int):
    try:
        video = download_video(video_id)
        result = transcode(video)
        upload_result(result)
    except TransientError as exc:
        # 지수 백오프 재시도
        raise self.retry(
            exc=exc,
            countdown=2 ** self.request.retries * 60
        )
    except PermanentError:
        # 재시도 안 함 — DLQ 로깅
        log_permanent_failure(video_id)
        raise

# FastAPI에서 호출
@app.post("/videos/{video_id}/transcode")
async def start_transcode(video_id: int):
    task = process_video.delay(video_id)
    return {"task_id": task.id}

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,      # PENDING, STARTED, SUCCESS, FAILURE
        "result": result.result if result.ready() else None,
    }
```

```python
# arq: asyncio 네이티브 태스크 큐 (경량 Celery 대안)
from arq import create_pool
from arq.connections import RedisSettings

async def send_welcome_email(ctx: dict, user_id: int):
    """arq worker에서 실행되는 태스크"""
    async with get_async_session() as session:
        user = await session.get(User, user_id)
        await email_service.send(user.email, "Welcome!")

class WorkerSettings:
    functions = [send_welcome_email]
    redis_settings = RedisSettings(host="localhost")
    max_jobs = 10
    job_timeout = 300          # 5분
    retry_jobs = True
    max_tries = 3

# FastAPI에서 호출
@app.on_event("startup")
async def startup():
    app.state.arq_pool = await create_pool(RedisSettings())

@app.post("/users")
async def create_user(user_data: UserCreate):
    user = await save_user(user_data)
    # arq로 비동기 작업 enqueue
    await app.state.arq_pool.enqueue_job(
        "send_welcome_email",
        user.id,
        _defer_by=timedelta(seconds=5),  # 5초 후 실행
    )
    return user
```

**Step 3 — 다양한 관점**

| 기준 | BackgroundTasks | Celery | arq | Dramatiq |
|------|----------------|--------|-----|----------|
| 복잡도 | 매우 낮음 | 높음 | 중간 | 중간 |
| 신뢰성 | 낮음 (fire-forget) | 높음 | 중간 | 높음 |
| 재시도 | 없음 | 풍부 | 기본 | 풍부 |
| 결과 추적 | 없음 | Redis/DB | Redis | Redis/RabbitMQ |
| async 지원 | 네이티브 | 제한적 | 네이티브 | 아님 |
| 브로커 | 없음 | Redis/RabbitMQ | Redis | Redis/RabbitMQ |
| 수평 확장 | 불가 | 워커 수 확장 | 워커 수 확장 | 워커 수 확장 |
| 모니터링 | 없음 | Flower | arq dashboard | 대시보드 |
| 적합 규모 | 소규모 | 대규모 | 중소규모 | 중대규모 |

**Step 4 — 선택 기준 의사결정 트리**

```
작업 유실 허용 가능?
├─ Yes → 실행 시간 < 30초?
│        ├─ Yes → BackgroundTasks
│        └─ No  → 서버 부하 분리 필요 → arq/Celery
└─ No  → 재시도 필요?
         ├─ Yes → 복잡한 워크플로우?
         │        ├─ Yes → Celery (chord, chain, group)
         │        └─ No  → arq (간단 재시도)
         └─ No  → 순서 보장 필요?
                  ├─ Yes → Celery + priority queue
                  └─ No  → arq
```

```python
# 프로덕션 팁: BackgroundTasks를 안전하게 사용하는 패턴
# "at-most-once" 의미론이 허용되는 경우에만

@app.post("/analytics/events")
async def track_event(
    event: AnalyticsEvent,
    background_tasks: BackgroundTasks,
):
    # 1. 핵심 로직은 동기적으로 완료
    event_id = await save_event(event)

    # 2. 부수 효과만 background로
    background_tasks.add_task(
        update_realtime_dashboard,  # 유실 가능
        event_id
    )
    background_tasks.add_task(
        invalidate_cache,           # 유실 가능
        event.user_id
    )

    return {"event_id": event_id}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| BackgroundTasks | 제로 인프라, 간단 | 유실 가능, 확장 불가 | 알림, 캐시 무효화 |
| Celery | 성숙, 풍부한 기능 | 복잡한 설정, 동기 코드 | 대규모, 복잡 워크플로우 |
| arq | async 네이티브, 경량 | Celery보다 기능 적음 | FastAPI 서비스 |
| Cloud 서비스 (SQS+Lambda) | 관리형, 무한 확장 | 벤더 종속, 비용 | 클라우드 네이티브 |
| Temporal/Prefect | 워크플로우 오케스트레이션 | 학습 곡선, 인프라 | 복잡한 비즈니스 로직 |

**Step 6 — 성장 & 심화 학습**
- Celery 내부: prefork pool vs eventlet pool vs gevent pool의 동작 차이
- `exactly-once` 처리의 불가능성과 `effectively-once` 패턴 (멱등성 키)
- Temporal.io — Celery의 한계를 넘는 durable execution
- SAQ (Simple Async Queue) — arq의 간소화 버전

**🎯 면접관 평가 기준:**
- L6 PASS: BackgroundTasks의 한계 인지. Celery vs arq 비교. 재시도 메커니즘 설명.
- L7 EXCEED: acks_late + reject_on_worker_lost의 at-least-once 보장 메커니즘. 의사결정 트리 제시. Temporal/durable execution 개념.
- 🚩 RED FLAG: 모든 비동기 작업에 BackgroundTasks 사용. 작업 유실 가능성 인지 못함.

---

## 4. SQLAlchemy Session & ORM

### Q10: Unit of Work 패턴과 Identity Map — SQLAlchemy Session 내부

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: SQLAlchemy Session & ORM

**Question:**
"SQLAlchemy의 Session이 구현하는 Unit of Work 패턴과 Identity Map을 설명하세요. `session.flush()` vs `session.commit()` vs `session.expire_all()`의 차이, identity map이 동일 트랜잭션 내에서 객체 일관성을 어떻게 보장하는지, 그리고 `expire_on_commit`이 프로덕션에서 일으키는 문제를 논하세요."

---

**🧒 12살 비유:**
숙제 노트를 생각해봐. Session은 너의 연습장이야(메모리). 문제를 풀면(객체 수정) 연습장에만 적히고 아직 선생님(DB)한테는 안 넘겨. `flush`는 선생님한테 답을 보여주는 거(SQL 실행, 아직 수정 가능). `commit`은 제출하는 거(최종 확정). Identity Map은 연습장에 "같은 학생은 한 장만"이라는 규칙 — 학생번호 5번을 두 번 불러도 같은 페이지를 보는 거야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
SQLAlchemy Session은 ORM의 핵심이지만, 내부 동작을 모르면 stale data, 불필요한 쿼리, 메모리 릭 등의 문제에 빠진다. Staff 엔지니어는 Session의 상태 머신을 이해해 올바른 scoping과 lifecycle 관리를 설계해야 한다.

**Step 2 — 핵심 기술 설명**

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column

engine = create_engine("postgresql://...")

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]

# Identity Map 동작
with Session(engine) as session:
    # 첫 조회: SELECT 실행, identity map에 저장
    user1 = session.get(User, 1)

    # 같은 PK 재조회: DB 안 침, identity map에서 반환
    user2 = session.get(User, 1)

    assert user1 is user2  # True — 동일 Python 객체!

    # identity map 키: (User, (1,)) → User instance
    # 이것이 "같은 트랜잭션 내 객체 일관성"을 보장

    # 쿼리로 조회해도 identity map 적용
    user3 = session.execute(
        select(User).where(User.id == 1)
    ).scalar_one()
    assert user3 is user1  # True — 쿼리는 실행하지만 기존 객체 반환
```

```python
# Unit of Work 내부 동작
with Session(engine) as session:
    # 1. new (Pending) — session.add() 후
    new_user = User(name="Alice", email="alice@example.com")
    session.add(new_user)
    # 상태: new_user in session.new → True

    # 2. flush — SQL 실행 (INSERT/UPDATE/DELETE)
    session.flush()
    # INSERT INTO users (...) VALUES (...) 실행
    # new_user.id에 DB 생성 ID 할당
    # 상태: new_user in session.new → False
    #        new_user in session.identity_map → True
    # 아직 COMMIT 안 됨!

    # 3. dirty — 속성 변경 시 자동 추적
    new_user.name = "Alice Updated"
    # 상태: new_user in session.dirty → True
    # SQLAlchemy가 __setattr__을 오버라이드해서 변경 감지

    # 4. autoflush — 쿼리 실행 전 자동 flush
    # select 실행 시 dirty 객체가 flush됨
    result = session.execute(select(User).where(User.name == "Alice Updated"))
    # 위 쿼리 전에 UPDATE 자동 실행 (autoflush=True일 때)

    # 5. commit — 트랜잭션 확정
    session.commit()
    # COMMIT 실행
    # 기본: expire_on_commit=True → 모든 속성 만료
    # → 이후 접근 시 새 SELECT 실행 (lazy reload)

    print(new_user.name)
    # SELECT users.name FROM users WHERE users.id = ? (lazy reload!)
```

**expire_on_commit 프로덕션 문제:**
```python
# 문제 시나리오: API 응답에서 commit 후 객체 접근
@app.post("/users")
async def create_user(user_data: UserCreate):
    async with AsyncSession(engine) as session:
        user = User(**user_data.model_dump())
        session.add(user)
        await session.commit()

        # ⚠️ expire_on_commit=True (기본)
        # user의 모든 속성이 만료됨
        # 아래 접근 시 새 SELECT 실행되지만...
        # commit 후 session이 곧 닫히므로 DetachedInstanceError 가능!
        return UserResponse.model_validate(user)

# 해결 1: expire_on_commit=False
async_engine = create_async_engine("postgresql+asyncpg://...")
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    expire_on_commit=False  # commit 후에도 속성 유지
)

# 해결 2: refresh로 명시적 로드
async with AsyncSession(engine) as session:
    session.add(user)
    await session.commit()
    await session.refresh(user)  # 명시적 reload
    return UserResponse.model_validate(user)

# 해결 3: 반환 전 필요한 속성만 미리 접근
async with AsyncSession(engine) as session:
    session.add(user)
    await session.flush()  # ID 할당
    user_dict = {
        "id": user.id,
        "name": user.name,
        "email": user.email
    }
    await session.commit()
    return UserResponse(**user_dict)
```

**Step 3 — 다양한 관점**

| 동작 | flush() | commit() | expire_all() | expunge() |
|------|---------|----------|-------------|-----------|
| SQL 실행 | Yes (INSERT/UPDATE/DELETE) | flush + COMMIT | No | No |
| 트랜잭션 | 유지 | 종료 + 새 시작 | 유지 | 유지 |
| 객체 상태 | persistent | expired (기본) | expired | detached |
| identity map | 유지 | 유지 (expired) | 유지 (expired) | 제거 |
| 롤백 가능 | Yes | No | N/A | N/A |

**Step 4 — Session 상태 머신**

```
┌──────────┐   add()   ┌──────────┐   flush()  ┌───────────┐
│ Transient ├──────────►│ Pending  ├───────────►│ Persistent│
│ (new obj) │           │ (in new) │            │ (in identity_map)
└──────────┘           └──────────┘            └─────┬─────┘
                                                      │
                                          expire/commit│
                                                      ▼
                                               ┌──────────┐
               expunge()     ┌────────────────►│ Expired  │
              ┌──────────────┤                 │ (lazy)   │
              │              │                 └──────────┘
              ▼              │
        ┌──────────┐   delete()  ┌──────────┐
        │ Detached │◄───────────│ Deleted  │
        │ (no session)          │ (pending │
        └──────────┘            │  delete) │
                                └──────────┘
```

```python
from sqlalchemy import inspect

user = session.get(User, 1)
state = inspect(user)
print(state.persistent)  # True
print(state.expired)     # False
print(state.detached)    # False
print(state.pending)     # False
print(state.transient)   # False

# 변경 추적
print(state.attrs.name.history)
# History(added=['new_name'], unchanged=(), deleted=['old_name'])
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| expire_on_commit=True | 항상 최신 데이터 | 추가 SELECT, DetachedInstanceError | 기본값, 데이터 정합성 중요 |
| expire_on_commit=False | 성능, 에러 방지 | stale 데이터 가능 | API 응답, read-heavy |
| flush + dict 추출 | 안전, 명시적 | 코드 장황 | 복잡한 트랜잭션 |
| session.refresh() | 최신 데이터, 명시적 | 추가 SELECT | 특정 객체만 갱신 |

**Step 6 — 성장 & 심화 학습**
- SQLAlchemy 소스: `sqlalchemy/orm/session.py` — `Session._flush` 메서드
- `UnitOfWorkTransaction` 클래스 — topological sort로 INSERT/UPDATE/DELETE 순서 결정
- Martin Fowler의 "Patterns of Enterprise Application Architecture" — Unit of Work 원전
- Django ORM vs SQLAlchemy — implicit save vs explicit flush/commit 철학 차이

**🎯 면접관 평가 기준:**
- L6 PASS: flush vs commit 차이. identity map 설명. expire_on_commit 문제 인지.
- L7 EXCEED: 상태 머신 전체 설명. autoflush 동작과 비활성화 시나리오. UoW의 topological sort. history tracking 활용.
- 🚩 RED FLAG: flush와 commit을 구분 못함. identity map을 캐시로 오해.

---

### Q11: N+1 문제 — 감지, 방지, 그리고 최적 로딩 전략

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: SQLAlchemy Session & ORM

**Question:**
"ORM의 N+1 쿼리 문제를 SQLAlchemy 2.0 컨텍스트에서 설명하세요. lazy loading, eager loading(joinedload, selectinload, subqueryload), raiseload의 동작과 trade-off를 비교하고, async 환경에서 lazy loading이 작동하지 않는 이유를 설명하세요. 프로덕션에서 N+1을 감지하고 방지하는 체계를 설계하세요."

---

**🧒 12살 비유:**
선생님이 반 학생 30명의 부모 연락처를 알고 싶어. N+1 방식은: "1번 학생 부모 전화번호 줘, 2번 학생 부모 전화번호 줘..." 31번 물어야 해(1+30). joinedload는 "학생 명단이랑 부모 연락처를 한 장에 같이 줘"라고 1번만 물어봐. selectinload는 "학생 명단 줘, 그리고 이 학생들의 부모 연락처 한꺼번에 줘"라고 2번만 물어봐.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
N+1은 ORM 성능 문제의 #1 원인이다. Staff 엔지니어는 로딩 전략의 trade-off를 이해하고, 체계적인 감지/방지 시스템을 설계할 수 있어야 한다. 특히 async + SQLAlchemy에서 lazy loading이 작동하지 않는 것은 흔한 함정이다.

**Step 2 — 핵심 기술 설명**

```python
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import (
    relationship, joinedload, selectinload,
    subqueryload, raiseload, lazyload,
    Mapped, mapped_column, DeclarativeBase
)

class Base(DeclarativeBase):
    pass

class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    books: Mapped[list["Book"]] = relationship(back_populates="author")

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped["Author"] = relationship(back_populates="books")
    reviews: Mapped[list["Review"]] = relationship()

class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))

# N+1 발생
with Session(engine) as session:
    authors = session.execute(select(Author)).scalars().all()
    # 1 쿼리: SELECT * FROM authors (10명)

    for author in authors:
        print(author.books)
        # 10 쿼리: SELECT * FROM books WHERE author_id = ? (각 저자별)
    # 총 11 쿼리 → N+1!

    for author in authors:
        for book in author.books:
            print(book.reviews)
            # 추가 쿼리: 각 book마다 SELECT * FROM reviews ...
    # 총 1 + 10 + (10*평균_책수) 쿼리 → N+1의 N+1!
```

**로딩 전략 비교:**
```python
# 1. joinedload — LEFT OUTER JOIN
stmt = select(Author).options(joinedload(Author.books))
# SELECT authors.*, books.* FROM authors LEFT OUTER JOIN books ON ...
# 1 쿼리, 하지만:
# - 카르테시안 곱으로 결과 행 증가
# - 컬렉션이 크면 메모리/네트워크 폭발
# - 다대다에서 중복 행 심각

# 2. selectinload — 별도 IN 쿼리 (권장 기본값)
stmt = select(Author).options(selectinload(Author.books))
# SELECT * FROM authors
# SELECT * FROM books WHERE author_id IN (1, 2, 3, ...)
# 2 쿼리 — 카르테시안 곱 없음, 대부분 최적

# 3. subqueryload — 서브쿼리
stmt = select(Author).options(subqueryload(Author.books))
# SELECT * FROM authors
# SELECT * FROM books WHERE author_id IN (SELECT id FROM authors)
# 2 쿼리 — selectinload와 유사하지만 IN 절이 서브쿼리

# 4. raiseload — 접근 시 에러 발생 (방어적)
stmt = select(Author).options(raiseload(Author.books))
# author.books 접근 시 → InvalidRequestError!
# N+1 방지를 강제
```

**async 환경에서 lazy loading 불가:**
```python
# async에서 lazy loading이 안 되는 이유:
# lazy loading은 속성 접근(__getattr__) 시 동기적으로 SQL 실행
# async session은 await 없이 I/O 불가!

async with AsyncSession(engine) as session:
    author = await session.get(Author, 1)
    # ⚠️ MissingGreenlet: greenlet_spawn has not been called
    print(author.books)  # 💥 에러!

    # 해결 1: eager loading (selectinload 등)
    stmt = select(Author).options(
        selectinload(Author.books)
    ).where(Author.id == 1)
    author = (await session.execute(stmt)).scalar_one()
    print(author.books)  # ✅ 이미 로드됨

    # 해결 2: awaitable lazy loading (run_sync)
    # 권장하지 않음 — greenlet 필요 (asyncpg에서는 작동 안 함)

    # 해결 3: 모든 relationship에 raiseload 기본 적용
    class Author(Base):
        books: Mapped[list["Book"]] = relationship(
            lazy="raise"  # 기본값을 raise로 변경
        )
    # → 항상 명시적 eager loading 강제
```

**Step 3 — 다양한 관점**

| 전략 | 쿼리 수 | 메모리 | 적합 | 부적합 |
|------|---------|--------|------|--------|
| lazy (기본) | 1+N | 낮음 (지연) | 관계를 항상 접근하지 않을 때 | async, 대량 반복 |
| joinedload | 1 | 높음 (카르테시안) | 1:1, 작은 1:N | 큰 컬렉션, 다대다 |
| selectinload | 2 | 중간 | 1:N 컬렉션 (일반적 최적) | PK 매우 많을 때 (IN 절 한계) |
| subqueryload | 2 | 중간 | selectin과 유사 | 복잡한 필터 쿼리 |
| raiseload | 1 | 최소 | 방어적 설계, async | 유연한 탐색 필요 시 |

**Step 4 — N+1 감지 체계**

```python
# 방법 1: SQLAlchemy event로 쿼리 카운트 추적
from sqlalchemy import event
import threading

class QueryCounter:
    _local = threading.local()

    @classmethod
    def start(cls):
        cls._local.count = 0
        cls._local.queries = []

    @classmethod
    def get_count(cls):
        return getattr(cls._local, 'count', 0)

    @classmethod
    def get_queries(cls):
        return getattr(cls._local, 'queries', [])

@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    QueryCounter._local.count = getattr(QueryCounter._local, 'count', 0) + 1
    QueryCounter._local.queries = getattr(QueryCounter._local, 'queries', [])
    QueryCounter._local.queries.append(statement[:200])

# FastAPI 미들웨어로 요청별 쿼리 수 모니터링
@app.middleware("http")
async def query_count_middleware(request, call_next):
    QueryCounter.start()
    response = await call_next(request)
    count = QueryCounter.get_count()
    response.headers["X-Query-Count"] = str(count)
    if count > 20:  # 임계값 초과
        logger.warning(
            "Excessive queries detected",
            path=request.url.path,
            query_count=count,
            queries=QueryCounter.get_queries()[:5],
        )
    return response

# 방법 2: pytest에서 쿼리 수 assertion
@pytest.fixture
def assert_max_queries(session):
    counter = {"count": 0}

    @event.listens_for(session.bind, "before_cursor_execute")
    def count_queries(*args):
        counter["count"] += 1

    class MaxQueryAssertion:
        def __init__(self, max_count: int):
            self.max_count = max_count

        def __enter__(self):
            counter["count"] = 0
            return self

        def __exit__(self, *args):
            assert counter["count"] <= self.max_count, (
                f"Expected max {self.max_count} queries, got {counter['count']}"
            )

    return MaxQueryAssertion

def test_list_authors(client, assert_max_queries):
    with assert_max_queries(3):  # 최대 3쿼리
        response = client.get("/authors?include=books")
    assert response.status_code == 200
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| 기본 lazy + 필요 시 eager | 유연함 | N+1 실수 가능 | 동기 전용, 소규모 |
| 기본 raiseload + 명시적 eager | N+1 불가능 | 모든 쿼리에 options 필요 | async, 대규모 (권장) |
| GraphQL DataLoader | 자동 배칭 | 복잡도 | GraphQL API |
| raw SQL / hybrid | 최적 성능 | ORM 이점 상실 | 복잡한 보고서/대시보드 |

**Step 6 — 성장 & 심화 학습**
- `sqlalchemy-collectd`, `sqltap` — 프로덕션 쿼리 모니터링 도구
- Django의 `select_related`(joinedload) / `prefetch_related`(selectinload) 비교
- DataLoader 패턴 (Facebook) — 배치 + 캐싱으로 N+1 해결
- `contains_eager` — 이미 JOIN한 쿼리에서 관계 로딩 (수동 최적화)

**🎯 면접관 평가 기준:**
- L6 PASS: N+1 설명, joinedload/selectinload 차이, async에서 lazy 불가 인지.
- L7 EXCEED: raiseload 기반 방어적 설계, 쿼리 카운트 모니터링 체계 설계, contains_eager 활용.
- 🚩 RED FLAG: "joinedload를 항상 쓰면 된다." async에서 lazy loading 에러 경험 없음.

---

### Q12: Session Scoping — 요청별 세션 관리와 async 환경

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: SQLAlchemy Session & ORM

**Question:**
"FastAPI + SQLAlchemy에서 세션 스코핑 전략을 설계하세요. `scoped_session`, `async_scoped_session`, dependency-based session 관리의 차이를 설명하고, 트랜잭션 경계 설정, nested transaction(savepoint), 그리고 여러 마이크로서비스 간 분산 트랜잭션 처리 전략을 논하세요."

---

**🧒 12살 비유:**
식당에서 주문서를 생각해봐. 각 테이블(요청)마다 별도 주문서(세션)가 있어야 해. 한 주문서를 여러 테이블이 공유하면(세션 공유) A 테이블 주문이 B 테이블로 잘못 가. scoped_session은 "각 웨이터(스레드)에게 자기 주문서를 줘"라는 규칙이야. 세이브포인트는 "여기까지 주문은 확정, 다음 건 취소될 수 있어"라는 중간 체크포인트야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
세션 관리 실수는 데이터 손상, 커넥션 릭, 동시성 버그의 주요 원인이다. Staff 엔지니어는 프레임워크별 세션 스코핑 패턴을 이해하고 올바른 트랜잭션 경계를 설계해야 한다.

**Step 2 — 핵심 기술 설명**

```python
# FastAPI + async SQLAlchemy: Dependency-based 세션 관리 (권장)
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,      # 커넥션 유효성 사전 검사
    pool_recycle=3600,        # 1시간 후 커넥션 재생성
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,   # API 서비스에서 권장
)

# Dependency: 요청당 세션
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        async with session.begin():  # 자동 commit/rollback
            yield session
        # begin() 컨텍스트: 정상 → commit, 예외 → rollback
        # session 컨텍스트: close (커넥션 반환)

# 사용
@app.post("/users")
async def create_user(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = User(**user_data.model_dump())
    db.add(user)
    # commit은 get_db의 begin() 컨텍스트가 처리
    await db.flush()  # ID 할당
    return UserResponse.model_validate(user)
```

```python
# scoped_session vs dependency-based

# scoped_session (동기, Flask 스타일) — FastAPI에서 권장하지 않음
from sqlalchemy.orm import scoped_session, sessionmaker

SessionLocal = sessionmaker(bind=engine)
ScopedSession = scoped_session(SessionLocal)
# 스레드 로컬 스토리지 기반 — 같은 스레드에서 항상 같은 세션
# 문제: asyncio는 단일 스레드 → 모든 코루틴이 같은 세션 공유!

# async_scoped_session (특수 케이스)
from sqlalchemy.ext.asyncio import async_scoped_session
from asyncio import current_task

AsyncScopedSession = async_scoped_session(
    AsyncSessionLocal,
    scopefunc=current_task,  # Task별 세션 격리
)
# 사용 케이스가 제한적 — Dependency 방식이 더 명확하고 안전
```

**Nested Transaction (Savepoint):**
```python
async def transfer_with_audit(
    db: AsyncSession,
    from_id: int,
    to_id: int,
    amount: float,
):
    # 메인 트랜잭션: 이체 + 감사 로그
    from_account = await db.get(Account, from_id)
    to_account = await db.get(Account, to_id)

    from_account.balance -= amount
    to_account.balance += amount

    # Savepoint: 감사 로그는 실패해도 이체는 유지
    try:
        async with db.begin_nested():  # SAVEPOINT
            audit = AuditLog(
                action="transfer",
                from_id=from_id,
                to_id=to_id,
                amount=amount,
            )
            db.add(audit)
            await db.flush()
            # 감사 로그 INSERT 실패 시 → ROLLBACK TO SAVEPOINT
            # 하지만 이체는 유지됨
    except Exception as e:
        logger.error(f"Audit log failed: {e}")
        # 메인 트랜잭션은 영향 없음

    # 메인 트랜잭션 commit (이체만)
    await db.commit()
```

**Step 3 — 다양한 관점**

```python
# 트랜잭션 경계 전략 비교

# 전략 1: 세션 = 요청 수명 (일반적)
async def get_db():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            yield session

# 전략 2: 서비스 레이어에서 트랜잭션 제어
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session  # begin 없이 전달
        # 서비스 레이어가 begin/commit 제어

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user_with_profile(self, data):
        async with self.db.begin():  # 서비스가 트랜잭션 관리
            user = User(...)
            self.db.add(user)
            await self.db.flush()
            profile = Profile(user_id=user.id, ...)
            self.db.add(profile)
        # 자동 commit 또는 rollback

# 전략 3: Repository 패턴 + UoW
class UnitOfWork:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.users = UserRepository(self.session)
        self.orders = OrderRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

# 사용
async with UnitOfWork(AsyncSessionLocal) as uow:
    user = await uow.users.get(user_id)
    order = Order(user_id=user.id, ...)
    uow.orders.add(order)
    await uow.commit()
```

**Step 4 — 분산 트랜잭션 (마이크로서비스)**

```python
# SAGA 패턴: 분산 트랜잭션 대신 보상 트랜잭션
# 2PC는 사용하지 않음 (가용성 저하, 성능 병목)

class OrderSaga:
    """Orchestration SAGA 패턴"""

    async def create_order(self, order_data: OrderCreate) -> Order:
        # Step 1: 주문 생성 (local tx)
        order = await self._create_order_local(order_data)

        try:
            # Step 2: 재고 차감 (외부 서비스 호출)
            await inventory_service.reserve(order.items)
        except Exception:
            # 보상: 주문 취소
            await self._cancel_order(order.id)
            raise

        try:
            # Step 3: 결제 (외부 서비스 호출)
            await payment_service.charge(order.total)
        except Exception:
            # 보상: 재고 복원 + 주문 취소
            await inventory_service.release(order.items)
            await self._cancel_order(order.id)
            raise

        await self._confirm_order(order.id)
        return order
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| Dependency session | 명시적, 테스트 용이 | 매 요청 setup | FastAPI (권장) |
| scoped_session | 암묵적, 편리 | async 비호환, 디버깅 어려움 | Flask 동기 |
| UoW 패턴 | 깔끔한 트랜잭션 경계 | 보일러플레이트 | DDD, 복잡한 도메인 |
| SAGA | 분산 트랜잭션 | 보상 로직 복잡 | 마이크로서비스 |

**Step 6 — 성장 & 심화 학습**
- SQLAlchemy "Session Basics" 공식 문서 — 세션 상태 머신 전체
- 2PC vs SAGA vs TCC — 분산 트랜잭션 패턴 깊이 비교
- Outbox 패턴 — 메시지 발행과 DB 트랜잭션의 원자성 보장
- `asyncio.TaskGroup` + 세션 스코핑 — 병렬 Task에서의 세션 안전성

**🎯 면접관 평가 기준:**
- L6 PASS: Dependency-based 세션 관리. begin/commit/rollback 경계. expire_on_commit 설정.
- L7 EXCEED: Savepoint 활용, UoW 패턴 구현, SAGA/Outbox 패턴. scoped_session이 async에서 안 되는 이유(thread-local vs coroutine).
- 🚩 RED FLAG: 전역 세션 사용. 트랜잭션 경계 없이 commit. 세션 close 누락.

---

## 5. DB Connection Management

### Q13: Connection Pooling 심화 — QueuePool, PgBouncer, 그리고 async 드라이버

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: DB Connection Management

**Question:**
"SQLAlchemy의 커넥션 풀링(QueuePool, NullPool, StaticPool)의 내부 동작을 설명하세요. PgBouncer와 함께 사용할 때 주의점, asyncpg 드라이버의 아키텍처, 그리고 프로덕션에서 커넥션 고갈이 발생했을 때 진단/해결 과정을 설명하세요."

---

**🧒 12살 비유:**
수영장 사물함을 생각해봐. QueuePool은 사물함이 20개(pool_size)인데, 다 차면 대기줄(overflow)에 서야 해. 대기줄도 꽉 차면 "다음에 오세요"(timeout error). PgBouncer는 수영장 입구에 있는 안내원이야 — 사물함을 더 효율적으로 관리해서 더 많은 사람이 쓸 수 있게 해주지. NullPool은 사물함이 없어서 매번 새 사물함을 만들었다 부수는 거야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
커넥션 풀 설정 실수는 프로덕션에서 가장 흔한 DB 장애 원인이다. Staff 엔지니어는 풀 사이즈 계산, PgBouncer 상호작용, 커넥션 릭 디버깅을 할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

```python
from sqlalchemy import create_engine, event, text
from sqlalchemy.pool import QueuePool, NullPool, StaticPool

# QueuePool (기본, 프로덕션 권장)
engine = create_engine(
    "postgresql+psycopg2://user:pass@db:5432/mydb",
    pool_size=20,          # 유지할 커넥션 수
    max_overflow=10,       # pool_size 초과 시 추가 생성 가능 수
    pool_timeout=30,       # 커넥션 대기 최대 시간 (초)
    pool_recycle=1800,     # 30분 후 커넥션 재생성 (DB timeout 방지)
    pool_pre_ping=True,    # checkout 시 "SELECT 1"로 유효성 검사
    echo_pool="debug",     # 풀 디버그 로깅
)
# 최대 동시 커넥션: pool_size + max_overflow = 30
# pool_size 계산 공식:
# pool_size = (workers * 2) + 여유분
# 4코어 서버, uvicorn workers=4 → pool_size = 10~20

# NullPool (PgBouncer 사용 시)
engine_with_pgbouncer = create_engine(
    "postgresql+psycopg2://user:pass@pgbouncer:6432/mydb",
    poolclass=NullPool,    # SQLAlchemy 풀링 비활성화
    # PgBouncer가 풀링 담당 → 이중 풀링 방지
)

# StaticPool (테스트용 — 인메모리 SQLite)
test_engine = create_engine(
    "sqlite://",
    poolclass=StaticPool,  # 단일 커넥션 재사용
    connect_args={"check_same_thread": False},
)
```

**PgBouncer 상호작용:**
```python
# PgBouncer 모드별 SQLAlchemy 설정

# 1. Session mode (기본, 권장)
# - 트랜잭션 완료 시 서버 커넥션 반환
# - PREPARE 문 주의: server_reset_query 설정 필요
engine_session = create_engine(
    "postgresql+psycopg2://user:pass@pgbouncer:6432/mydb",
    poolclass=NullPool,
    # prepared statements 비활성화 (session mode 호환)
    connect_args={"prepare_threshold": 0},  # psycopg2
)

# 2. Transaction mode
# - 각 트랜잭션마다 서버 커넥션 할당/반환
# - SET, LISTEN/NOTIFY, PREPARE 사용 불가!
engine_tx = create_engine(
    "postgresql+psycopg2://user:pass@pgbouncer:6432/mydb",
    poolclass=NullPool,
    # 트랜잭션 밖에서 SET 사용 방지
    execution_options={"isolation_level": "AUTOCOMMIT"},  # 필요 시
)
# ⚠️ transaction mode에서 advisory lock, temp table 사용 불가

# 3. Statement mode (거의 사용 안 함)
# - 각 SQL 문마다 서버 커넥션 할당/반환
# - 멀티 스테이트먼트 트랜잭션 불가
```

**asyncpg 드라이버 아키텍처:**
```python
# asyncpg: 순수 Python async PostgreSQL 드라이버
# - libpq 미사용, PostgreSQL wire protocol 직접 구현
# - prepared statements 자동 캐싱 (성능 이점)
# - binary protocol (text 변환 없음 → 빠른 파싱)

from sqlalchemy.ext.asyncio import create_async_engine

async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@db:5432/mydb",
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    # asyncpg 특화 설정
    connect_args={
        "server_settings": {
            "jit": "off",           # 짧은 쿼리에서 JIT 오버헤드 방지
            "statement_timeout": "30000",  # 30초
        },
        "prepared_statement_cache_size": 1024,
    },
)

# ⚠️ asyncpg + PgBouncer 주의사항:
# asyncpg는 기본적으로 prepared statements 사용
# PgBouncer transaction mode에서 prepared statements 불가!
# 해결:
async_engine_pgbouncer = create_async_engine(
    "postgresql+asyncpg://user:pass@pgbouncer:6432/mydb",
    poolclass=NullPool,
    connect_args={
        "prepared_statement_cache_size": 0,  # prepared statement 비활성화
        "statement_cache_size": 0,
    },
)
```

**Step 3 — 커넥션 고갈 진단**

```python
# 증상: "QueuePool limit reached" 또는 "connection timed out"

# 진단 1: 풀 상태 모니터링
from sqlalchemy.pool import QueuePool

pool: QueuePool = engine.pool
print(f"Pool size: {pool.size()}")
print(f"Checked in: {pool.checkedin()}")   # 사용 가능
print(f"Checked out: {pool.checkedout()}") # 사용 중
print(f"Overflow: {pool.overflow()}")       # 초과 생성 수

# Prometheus 메트릭 연동
from prometheus_client import Gauge

pool_checkedout = Gauge('sqlalchemy_pool_checkedout', 'Connections in use')
pool_overflow = Gauge('sqlalchemy_pool_overflow', 'Overflow connections')

@event.listens_for(engine, "checkout")
def on_checkout(dbapi_conn, connection_record, connection_proxy):
    pool_checkedout.set(engine.pool.checkedout())

@event.listens_for(engine, "checkin")
def on_checkin(dbapi_conn, connection_record):
    pool_checkedout.set(engine.pool.checkedout())

# 진단 2: 커넥션 릭 감지
@event.listens_for(engine, "checkout")
def checkout_listener(dbapi_conn, connection_record, connection_proxy):
    import traceback
    connection_record.info["checkout_stack"] = traceback.format_stack()
    connection_record.info["checkout_time"] = time.monotonic()

# 주기적으로 장시간 체크아웃된 커넥션 확인
async def check_leaked_connections():
    pool = engine.pool
    now = time.monotonic()
    for rec in pool._pool:  # 내부 구현 접근 (디버깅 전용)
        checkout_time = rec.info.get("checkout_time", 0)
        if now - checkout_time > 60:  # 60초 이상 체크아웃
            logger.error(
                "Possible connection leak",
                stack=rec.info.get("checkout_stack"),
                duration=now - checkout_time,
            )
```

**Step 4 — 풀 사이즈 계산**

```python
# 최적 커넥션 수 공식 (PostgreSQL 공식 권장):
# connections = (core_count * 2) + effective_spindle_count
# SSD 서버: connections ≈ core_count * 2 + 1

# 예: 8코어 DB 서버
# PostgreSQL max_connections = 17
# 하지만 실제로는 여유분 포함 ~100

# 앱 서버별 pool_size 계산:
# total_app_pool = max_connections - reserved (superuser, monitoring)
# pool_per_server = total_app_pool / num_app_servers
# 예: max_connections=100, reserved=10, 3 앱서버
# pool_per_server = 90 / 3 = 30
# pool_size=20, max_overflow=10 → 최대 30
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| QueuePool (기본) | 간단, 대부분 충분 | 프로세스당 풀 | 단일/소수 서버 |
| NullPool + PgBouncer | 중앙 관리, 높은 다중화 | 인프라 추가 | 다수 앱 서버, K8s |
| pgpool-II | 로드 밸런싱, 레플리카 분산 | 복잡도, 성능 오버헤드 | 읽기 분산 |
| RDS Proxy (AWS) | 관리형, serverless 호환 | AWS 종속, 비용 | Lambda, Aurora |

**Step 6 — 성장 & 심화 학습**
- PostgreSQL `pg_stat_activity` — 실시간 커넥션 모니터링 쿼리
- PgBouncer `SHOW POOLS`, `SHOW STATS` — 풀 상태 진단
- asyncpg의 wire protocol 구현: `asyncpg/protocol/` — binary format 이해
- Connection draining — 배포 시 기존 커넥션 안전하게 종료

**🎯 면접관 평가 기준:**
- L6 PASS: QueuePool 파라미터 설명. pool_pre_ping 목적. PgBouncer와 NullPool 조합.
- L7 EXCEED: asyncpg + PgBouncer prepared statement 충돌 해결. 풀 사이즈 계산 공식. 커넥션 릭 감지 이벤트 훅 구현.
- 🚩 RED FLAG: pool_size를 "크게 잡으면 빠르다"고 생각. PgBouncer 모드별 제약 모름.

---

### Q14: 커넥션 릭 감지와 async 환경의 특수 문제

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: DB Connection Management

**Question:**
"async FastAPI 서비스에서 커넥션 릭이 발생하는 패턴들을 설명하세요. generator dependency에서의 예외 처리 미스, Task 취소 시 세션 정리, 그리고 graceful shutdown 시 풀 정리 전략을 프로덕션 코드와 함께 보여주세요."

---

**🧒 12살 비유:**
물풍선을 빌려주는 가게야. 10개(pool_size)밖에 없어. 누군가 빌려가서 반납을 안 하면(커넥션 릭) 결국 하나도 남지 않아서 다른 손님이 오래 기다려야 해. async에서는 바람이 갑자기 불어서(Task 취소) 물풍선을 들고 가던 사람이 사라지는 경우도 있어. 이때 물풍선이 길바닥에 놓여있게 되는 거야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
커넥션 릭은 점진적으로 발생해 프로덕션에서 갑자기 폭발한다. async 환경에서는 Task 취소, 예외 전파 등 추가적인 릭 패턴이 있어 더 까다롭다.

**Step 2 — 핵심 기술 설명**

```python
# 릭 패턴 1: try/finally 누락
async def leaky_query():
    session = AsyncSessionLocal()
    result = await session.execute(text("SELECT 1"))
    # 예외 발생 시 session.close() 호출 안 됨!
    # 커넥션이 풀에 반환되지 않음
    await session.close()

# 해결: context manager 사용
async def safe_query():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        # __aexit__에서 자동 close
```

```python
# 릭 패턴 2: Task 취소 시 cleanup 미실행
import asyncio

async def long_running_query(db: AsyncSession):
    # 장시간 쿼리 실행 중 클라이언트가 연결 끊음
    result = await db.execute(text("SELECT pg_sleep(60)"))
    # Task가 cancel되면 여기 도달 못함
    return result

# asyncio.CancelledError는 BaseException의 서브클래스
# except Exception으로 잡히지 않음!

# 해결: generator dependency의 finally가 CancelledError도 처리
async def get_db():
    session = AsyncSessionLocal()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        # CancelledError 포함 모든 경우에 실행됨
        await session.close()
```

```python
# 릭 패턴 3: Background task에서 세션 공유
@app.post("/process")
async def process_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    background_tasks: BackgroundTasks,
):
    data = await db.execute(query)

    # 🚫 세션이 요청 종료 시 닫힘 → background task에서 에러
    async def bg_work():
        await db.execute(another_query)  # 이미 닫힌 세션!

    background_tasks.add_task(bg_work)

    # ✅ background task에 새 세션 생성
    async def safe_bg_work():
        async with AsyncSessionLocal() as bg_session:
            await bg_session.execute(another_query)

    background_tasks.add_task(safe_bg_work)
```

```python
# 릭 패턴 4: 예외 처리 중 새 예외 발생
async def double_fault():
    session = AsyncSessionLocal()
    try:
        await session.execute(bad_query)
    except Exception:
        # rollback 중 DB 연결이 끊겼다면?
        await session.rollback()  # 여기서 또 예외!
        # session.close()에 도달 못함 → 릭

# 해결: nested try/finally
async def safe_double_fault():
    session = AsyncSessionLocal()
    try:
        await session.execute(bad_query)
    except Exception:
        try:
            await session.rollback()
        except Exception:
            pass  # rollback 실패는 무시
        raise
    finally:
        try:
            await session.close()
        except Exception:
            pass  # close 실패도 무시
```

**Graceful Shutdown:**
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up, pool status",
                pool_size=engine.pool.size(),
                checkedout=engine.pool.checkedout())
    yield

    # Shutdown
    logger.info("Shutting down, waiting for connections",
                checkedout=engine.pool.checkedout())

    # 1. 새 요청 수신 중단 (uvicorn이 처리)
    # 2. 진행 중 요청 완료 대기 (uvicorn --timeout-graceful-shutdown)
    # 3. 엔진 dispose — 모든 커넥션 닫기
    await engine.dispose()
    logger.info("All connections closed")

app = FastAPI(lifespan=lifespan)

# uvicorn 설정
# uvicorn app:app --timeout-graceful-shutdown 30
# SIGTERM → 30초 내 요청 완료 대기 → 강제 종료
```

**Step 3 — 프로덕션 모니터링**

```python
# 커넥션 릭 조기 경고 시스템
import asyncio
from prometheus_client import Gauge, Counter

conn_checkedout = Gauge('db_connections_active', 'Active DB connections')
conn_overflow = Gauge('db_connections_overflow', 'Overflow connections')
conn_leak_warnings = Counter('db_connection_leak_warnings_total', 'Leak warnings')

async def monitor_pool():
    """주기적 풀 상태 체크"""
    while True:
        pool = engine.pool
        checkedout = pool.checkedout()
        overflow = pool.overflow()
        total = pool.size() + overflow

        conn_checkedout.set(checkedout)
        conn_overflow.set(overflow)

        # 경고 조건
        utilization = checkedout / max(total, 1)
        if utilization > 0.8:
            conn_leak_warnings.inc()
            logger.warning(
                "Connection pool near exhaustion",
                checkedout=checkedout,
                total=total,
                utilization=f"{utilization:.0%}",
            )

        await asyncio.sleep(10)
```

**Step 4 — 구체적 예시**

```python
# PostgreSQL에서 릭 확인
# SELECT * FROM pg_stat_activity WHERE state = 'idle' AND query_start < now() - interval '5 minutes';

# SQLAlchemy에서 릭 확인 — checkout event hook
import time
import traceback

_active_connections: dict[int, dict] = {}

@event.listens_for(engine.sync_engine, "checkout")
def on_checkout(dbapi_conn, record, proxy):
    conn_id = id(dbapi_conn)
    _active_connections[conn_id] = {
        "time": time.monotonic(),
        "stack": "".join(traceback.format_stack()),
    }

@event.listens_for(engine.sync_engine, "checkin")
def on_checkin(dbapi_conn, record):
    _active_connections.pop(id(dbapi_conn), None)

# 디버그 엔드포인트
@app.get("/debug/connections")
async def debug_connections():
    now = time.monotonic()
    stale = {
        k: {**v, "age_seconds": now - v["time"]}
        for k, v in _active_connections.items()
        if now - v["time"] > 30
    }
    return {
        "pool_checkedout": engine.pool.checkedout(),
        "stale_connections": len(stale),
        "details": stale,
    }
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| Context manager | 자동 cleanup | 모든 코드에 적용 필요 | 기본 전략 |
| Event hooks 모니터링 | 조기 감지 | 성능 오버헤드 | 프로덕션 |
| pool_recycle | 오래된 커넥션 자동 교체 | DB timeout과 맞춤 필요 | 장시간 서비스 |
| pool_pre_ping | 죽은 커넥션 감지 | 매 checkout마다 SELECT 1 | 프로덕션 (권장) |

**Step 6 — 성장 & 심화 학습**
- `asyncio.shield()` — 취소로부터 cleanup 코드 보호
- SQLAlchemy `pool_events` 공식 문서 — 전체 이벤트 목록
- PostgreSQL `idle_in_transaction_session_timeout` — 서버 측 릭 방지
- OpenTelemetry DB instrumentation — 분산 환경 커넥션 추적

**🎯 면접관 평가 기준:**
- L6 PASS: context manager 패턴. CancelledError와 커넥션 릭 관계. pool_pre_ping.
- L7 EXCEED: Task 취소 시 cleanup 보장 메커니즘. checkout event hook으로 릭 디버깅. graceful shutdown + dispose.
- 🚩 RED FLAG: "커넥션 풀이 알아서 관리하니 신경 안 써도 됨." Task 취소 시나리오 고려 안 함.

---

## 6. Type System & Metaprogramming

### Q15: Metaclass, Descriptor, 그리고 ORM/Framework이 이를 활용하는 방법

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Type System & Metaprogramming

**Question:**
"Python의 metaclass와 descriptor protocol을 설명하고, SQLAlchemy와 Pydantic이 이들을 어떻게 활용하는지 구체적으로 설명하세요. `__init_subclass__`, `__set_name__`, `__class_getitem__`과 같은 현대적 대안이 metaclass를 얼마나 대체할 수 있는지도 논하세요."

---

**🧒 12살 비유:**
붕어빵 틀(metaclass)과 붕어빵(class)의 관계야. 보통은 기본 틀(type)로 붕어빵을 만드는데, 특수한 틀을 만들면 "모든 붕어빵에 팥이 들어가야 해"같은 규칙을 강제할 수 있어. descriptor는 붕어빵 안에 있는 "온도계"야 — 누가 온도를 읽으면(get) 자동으로 변환해주고, 온도를 바꾸면(set) 유효 범위 체크를 해줘.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
Metaclass와 descriptor는 Python의 가장 깊은 메커니즘이다. SQLAlchemy의 `DeclarativeBase`, Pydantic의 `BaseModel`, Django의 `Model` 등 주요 프레임워크가 이를 기반으로 동작한다. Staff 엔지니어는 이 레벨을 이해해야 프레임워크의 "마법"을 디버깅하고, 필요 시 확장할 수 있다.

**Step 2 — 핵심 기술 설명**

```python
# Metaclass 기본 — 클래스를 만드는 클래스
class RegistryMeta(type):
    """모든 서브클래스를 자동 등록하는 메타클래스"""
    _registry: dict[str, type] = {}

    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases:  # 베이스 클래스 자체는 등록 안 함
            RegistryMeta._registry[name] = cls
        return cls

class Handler(metaclass=RegistryMeta):
    pass

class EmailHandler(Handler):
    pass

class SlackHandler(Handler):
    pass

print(RegistryMeta._registry)
# {'EmailHandler': <class 'EmailHandler'>, 'SlackHandler': <class 'SlackHandler'>}
```

```python
# Descriptor Protocol
# __get__, __set__, __delete__ 중 하나 이상 구현한 객체

class TypedField:
    """타입 검증 descriptor"""
    def __set_name__(self, owner, name):
        # Python 3.6+ — descriptor가 어떤 이름으로 할당되었는지 자동 전달
        self.name = name
        self.private_name = f"_{name}"

    def __init__(self, expected_type: type):
        self.expected_type = expected_type

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self  # 클래스에서 접근 시 descriptor 자체 반환
        return getattr(obj, self.private_name, None)

    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name} must be {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        setattr(obj, self.private_name, value)

class User:
    name = TypedField(str)
    age = TypedField(int)

    def __init__(self, name: str, age: int):
        self.name = name  # TypedField.__set__ 호출
        self.age = age

user = User("Alice", 30)  # OK
user.age = "thirty"        # TypeError!
```

**SQLAlchemy의 활용:**
```python
# SQLAlchemy mapped_column은 descriptor
# InstrumentedAttribute가 __get__/__set__ 구현

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

# User.name은 InstrumentedAttribute (descriptor)
# 클래스 레벨: User.name → SQL 표현식으로 사용 가능
print(User.name == "Alice")  # <BinaryExpression ...> (SQL 조건)

# 인스턴스 레벨: user.name → 실제 값
user = User(name="Alice")
print(user.name)  # "Alice"

# 이것이 가능한 이유:
# InstrumentedAttribute.__get__(None, User) → SQL 표현식
# InstrumentedAttribute.__get__(user, User) → user._sa_instance_state에서 값
```

**Step 3 — 현대적 대안**

```python
# __init_subclass__ (Python 3.6+) — metaclass 대부분 대체
class Plugin:
    _plugins: dict[str, type] = {}

    def __init_subclass__(cls, *, plugin_name: str = None, **kwargs):
        super().__init_subclass__(**kwargs)
        name = plugin_name or cls.__name__
        Plugin._plugins[name] = cls

class EmailPlugin(Plugin, plugin_name="email"):
    pass

# 메타클래스 없이 동일한 효과!
print(Plugin._plugins)  # {'email': <class 'EmailPlugin'>}

# __class_getitem__ (Python 3.7+) — Generic 구현
class Response:
    def __class_getitem__(cls, item):
        # Response[User] 같은 표현 가능
        return type(f"Response[{item.__name__}]", (cls,), {"_type": item})

# 실제로는 typing.Generic을 사용하는 것이 표준적
from typing import Generic, TypeVar
T = TypeVar("T")

class Response(Generic[T]):
    def __init__(self, data: T):
        self.data = data
```

**Step 4 — Pydantic v2의 내부**

```python
# Pydantic v2는 Rust(pydantic-core)로 검증 로직 구현
# 메타클래스: ModelMetaclass가 __new__에서:
# 1. 필드 정의 수집 (type annotations + FieldInfo)
# 2. Rust core validator 생성 (SchemaValidator)
# 3. __init__, __repr__ 등 자동 생성

from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str
    age: int

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        if v < 0:
            raise ValueError("age must be positive")
        return v

# 내부적으로:
# 1. ModelMetaclass.__new__가 'name', 'age' annotation 수집
# 2. pydantic_core.SchemaValidator 생성 (Rust 컴파일)
# 3. User.__init__은 Rust validator를 호출
# → 순수 Python 대비 5-50x 빠른 검증

# model_rebuild() — 순환 참조 해결
class Parent(BaseModel):
    children: list["Child"] = []

class Child(BaseModel):
    parent: "Parent | None" = None

Parent.model_rebuild()  # ForwardRef 해석 + validator 재생성
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| Metaclass | 완전한 제어 | 복잡, 다중 상속 충돌 | 프레임워크 내부 |
| `__init_subclass__` | 간단, metaclass 불필요 | metaclass보다 제한적 | 플러그인 등록, 검증 |
| Descriptor | 속성 접근 가로채기 | 보일러플레이트 | ORM 필드, 검증 |
| `dataclasses` | 표준, 가벼움 | 검증 없음 | 단순 데이터 컨테이너 |
| Pydantic BaseModel | 검증 + 직렬화 | 런타임 비용 | API 입출력 |

**Step 6 — 성장 & 심화 학습**
- `type.__new__` vs `type.__init__` — 클래스 생성 2단계
- `__prepare__` — metaclass가 namespace dict를 커스터마이즈 (예: OrderedDict)
- CPython의 `tp_descr_get` — descriptor protocol의 C 레벨 구현
- PEP 487 (`__init_subclass__`, `__set_name__`) — metaclass 사용 감소의 역사

**🎯 면접관 평가 기준:**
- L6 PASS: Metaclass = 클래스의 클래스. Descriptor protocol (`__get__`, `__set__`). SQLAlchemy/Pydantic이 어떻게 활용하는지 개념적 설명.
- L7 EXCEED: `__set_name__`의 역할, descriptor resolution order (data descriptor > instance dict > non-data descriptor). Pydantic v2의 Rust core 아키텍처. `__init_subclass__`로 metaclass 대체 패턴.
- 🚩 RED FLAG: metaclass와 inheritance 혼동. descriptor를 "property의 고급 버전"으로만 이해.

---

### Q16: Protocol vs ABC, 그리고 structural subtyping

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Type System & Metaprogramming

**Question:**
"Python의 `typing.Protocol`과 `abc.ABC`의 차이를 설명하세요. structural subtyping vs nominal subtyping의 trade-off, runtime checkable protocol의 한계, 그리고 대규모 코드베이스에서 어떤 것을 언제 사용하는 것이 적절한지 설계 관점에서 논하세요."

---

**🧒 12살 비유:**
ABC는 "자격증"이야 — "요리사 자격증(ABC)"이 있어야 요리할 수 있어. Protocol은 "실력 검증"이야 — 자격증이 없어도 요리를 잘 하면 인정해줘. Go 언어처럼 "오리처럼 걷고 오리처럼 울면, 그건 오리야(duck typing)"를 타입 체커가 검증하는 거야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
대규모 코드베이스에서 인터페이스 설계는 결합도와 확장성을 결정한다. Staff 엔지니어는 nominal vs structural subtyping의 trade-off를 이해하고 상황에 맞는 추상화를 선택해야 한다.

**Step 2 — 핵심 기술 설명**

```python
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

# ABC (Abstract Base Class) — Nominal Subtyping
# "명시적으로 상속해야 인정"
class Serializable(ABC):
    @abstractmethod
    def serialize(self) -> bytes:
        ...

    @abstractmethod
    def deserialize(self, data: bytes) -> None:
        ...

class User(Serializable):  # 명시적 상속 필수
    def serialize(self) -> bytes:
        return json.dumps({"name": self.name}).encode()

    def deserialize(self, data: bytes) -> None:
        d = json.loads(data)
        self.name = d["name"]

# Serializable을 상속하지 않으면 isinstance 체크 실패
class ExternalUser:
    def serialize(self) -> bytes:
        return b"..."
    def deserialize(self, data: bytes) -> None:
        pass

isinstance(ExternalUser(), Serializable)  # False! 메서드가 있지만 상속 안 함
```

```python
# Protocol — Structural Subtyping
# "필요한 메서드/속성이 있으면 인정"
@runtime_checkable
class Serializable(Protocol):
    def serialize(self) -> bytes: ...
    def deserialize(self, data: bytes) -> None: ...

class ExternalUser:
    """Protocol을 상속하지 않지만 메서드가 있음"""
    def serialize(self) -> bytes:
        return b"..."
    def deserialize(self, data: bytes) -> None:
        pass

# mypy 검증: ExternalUser는 Serializable과 호환!
def process(obj: Serializable) -> None:
    data = obj.serialize()
    # ...

process(ExternalUser())  # ✅ mypy 통과

# runtime_checkable 한계
isinstance(ExternalUser(), Serializable)  # True (메서드 존재 확인만)
# ⚠️ 하지만: 시그니처(인자 타입, 반환 타입)는 체크 안 됨!
# 런타임에는 메서드 이름만 확인 → 타입 안전성 보장 불가
```

**Step 3 — 다양한 관점**

```python
# 설계 시나리오별 선택 가이드

# 1. 내부 코드 계층 — ABC 적합
# 이유: 구현 강제, 누락 즉시 감지 (인스턴스화 시 TypeError)
class Repository(ABC):
    @abstractmethod
    async def get(self, id: int) -> Entity: ...

    @abstractmethod
    async def save(self, entity: Entity) -> None: ...

# 2. 외부 라이브러리 호환 — Protocol 적합
# 이유: 서드파티 코드를 수정 없이 타입 호환
class HasClose(Protocol):
    def close(self) -> None: ...

def cleanup(resource: HasClose) -> None:
    resource.close()
# file object, DB connection, HTTP session 모두 호환!

# 3. 플러그인 시스템 — ABC + register
class Transformer(ABC):
    @abstractmethod
    def transform(self, data: dict) -> dict: ...

# 서드파티 클래스를 가상 서브클래스로 등록
@Transformer.register
class ExternalTransformer:
    def transform(self, data: dict) -> dict:
        return data

isinstance(ExternalTransformer(), Transformer)  # True
# 하지만 abstractmethod 검증은 안 됨!
```

**Step 4 — 고급 Protocol 패턴**

```python
from typing import Protocol, TypeVar, Generic

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)

# Generic Protocol
class Repository(Protocol[T]):
    async def get(self, id: int) -> T | None: ...
    async def save(self, entity: T) -> None: ...
    async def list(self, limit: int = 100) -> list[T]: ...

# 이 Protocol을 만족하는 모든 클래스가 호환
class UserRepo:
    async def get(self, id: int) -> User | None: ...
    async def save(self, entity: User) -> None: ...
    async def list(self, limit: int = 100) -> list[User]: ...

# Callback Protocol — callable 시그니처 정의
class EventHandler(Protocol):
    async def __call__(self, event: Event, *, retry: bool = False) -> None: ...

async def on_user_created(event: Event, *, retry: bool = False) -> None:
    pass

handler: EventHandler = on_user_created  # ✅ mypy 통과

# Intersection-like 패턴 (multiple Protocol)
class Closeable(Protocol):
    def close(self) -> None: ...

class Flushable(Protocol):
    def flush(self) -> None: ...

def safe_close(obj: Closeable & Flushable) -> None:  # Python 3.12 intersection 제안
    obj.flush()
    obj.close()
# 현재는 별도 Protocol로 조합
class CloseableAndFlushable(Closeable, Flushable, Protocol):
    ...
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| ABC | 구현 강제, 런타임 검증 | 결합도 높음, 서드파티 어려움 | 내부 추상화, 프레임워크 |
| Protocol | 느슨한 결합, 서드파티 호환 | 런타임 검증 제한적 | 인터페이스, 플러그인 |
| duck typing (no annotation) | 최대 유연성 | 타입 안전성 없음 | 스크립트, 작은 프로젝트 |
| `@runtime_checkable` Protocol | isinstance 사용 가능 | 시그니처 체크 안 됨 | DI, 분기 로직 |

**Step 6 — 성장 & 심화 학습**
- PEP 544 — Protocol의 공식 제안서 (동기와 설계 결정)
- Go의 implicit interface와 비교 — Python Protocol의 영감
- `typing_extensions.TypeVarTuple` — variadic generics (PEP 646)
- mypy의 Protocol 호환성 검증 — `--strict` 모드에서의 동작

**🎯 면접관 평가 기준:**
- L6 PASS: Protocol vs ABC 핵심 차이 (structural vs nominal). 사용 시점 구분. runtime_checkable 한계.
- L7 EXCEED: Generic Protocol, Callback Protocol, covariant TypeVar 활용. 대규모 코드베이스에서의 설계 원칙 제시. Go interface와의 비교.
- 🚩 RED FLAG: Protocol과 ABC를 동일하게 취급. structural subtyping 개념 모름.

---

### Q17: Pydantic v2 내부 — Rust 코어와 성능 최적화

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Type System & Metaprogramming

**Question:**
"Pydantic v2가 v1 대비 5-50배 빠른 이유를 아키텍처 레벨에서 설명하세요. `pydantic-core`의 Rust 구현, SchemaValidator의 동작 방식, 그리고 v1에서 v2 마이그레이션 시 겪는 주요 breaking change와 그 설계적 이유를 논하세요."

---

**🧒 12살 비유:**
Pydantic v1은 한국어 통역사(Python)가 하나하나 번역하던 거야. v2는 동시통역기(Rust)를 설치한 거야. 통역사가 할 일이 줄어들어서 훨씬 빨라. 그리고 번역 규칙(schema)을 미리 컴파일해서 기계에 넣어놓으니, 같은 규칙을 반복해서 읽을 필요가 없어.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
Pydantic은 FastAPI의 핵심 의존성이다. v2의 아키텍처 변화를 이해하면 성능 최적화, 커스텀 타입 구현, 마이그레이션 전략을 제대로 세울 수 있다.

**Step 2 — 핵심 기술 설명**

```python
# Pydantic v2 아키텍처
# ┌─────────────────────────────┐
# │    Python Layer (pydantic)   │
# │  BaseModel, Field, validator │
# ├─────────────────────────────┤
# │  pydantic-core (Rust/PyO3)  │
# │  SchemaValidator             │
# │  SchemaSerializer            │
# │  CoreSchema types            │
# └─────────────────────────────┘

# v1 동작: Python으로 검증
# 1. 매 검증마다 Python 함수 호출 체인
# 2. isinstance, try/except 기반 타입 변환
# 3. dict 복사, 재귀 검증 모두 Python 레벨

# v2 동작: Rust로 검증
# 1. 모델 정의 시 CoreSchema 생성 (한 번)
# 2. CoreSchema → Rust SchemaValidator 컴파일 (한 번)
# 3. 검증 시 Rust 코드 직접 실행 (매번, 매우 빠름)

from pydantic import BaseModel

class Address(BaseModel):
    street: str
    city: str
    zip_code: str

class User(BaseModel):
    name: str
    age: int
    addresses: list[Address]

# 내부에서 일어나는 일:
# 1. ModelMetaclass가 annotation 수집
# 2. CoreSchema 생성:
#    core_schema.model_schema(
#        User,
#        core_schema.model_fields_schema({
#            'name': core_schema.model_field(core_schema.str_schema()),
#            'age': core_schema.model_field(core_schema.int_schema()),
#            'addresses': core_schema.model_field(
#                core_schema.list_schema(
#                    core_schema.model_schema(Address, ...)
#                )
#            )
#        })
#    )
# 3. SchemaValidator(core_schema) → Rust 컴파일된 validator
# 4. User(name="Alice", age=30, ...) → Rust validator.validate_python(data)
```

```python
# 성능 차이 구체적 측정
import timeit
from pydantic import BaseModel

class SimpleModel(BaseModel):
    name: str
    age: int
    active: bool

data = {"name": "Alice", "age": 30, "active": True}

# Pydantic v2: ~0.5μs per validation
# Pydantic v1: ~5μs per validation  (10x 차이)

# 복잡한 모델 (중첩, 리스트)에서 차이 더 큼: 30-50x

# 직렬화도 Rust
user = SimpleModel(**data)
user.model_dump()       # Rust SchemaSerializer 사용
user.model_dump_json()  # JSON 직렬화도 Rust (orjson급 속도)
```

**v1→v2 주요 breaking changes:**
```python
# 1. Config class → model_config dict
# v1
class User(BaseModel):
    class Config:
        orm_mode = True

# v2
class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # orm_mode → from_attributes

# 2. validator → field_validator / model_validator
# v1
class User(BaseModel):
    @validator("name")
    def validate_name(cls, v):
        return v.strip()

# v2
class User(BaseModel):
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip()

    @model_validator(mode="after")
    def validate_model(self) -> "User":
        # 전체 모델 검증
        return self

# 3. .dict() → .model_dump(), .json() → .model_dump_json()
# 4. __fields__ → model_fields
# 5. schema() → model_json_schema()
```

```python
# 커스텀 타입 — v2의 __get_pydantic_core_schema__
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from typing import Any

class Color:
    def __init__(self, hex_value: str):
        if not hex_value.startswith("#") or len(hex_value) != 7:
            raise ValueError(f"Invalid color: {hex_value}")
        self.hex = hex_value

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(
            cls._validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda v: v.hex,
                info_arg=False,
            ),
        )

    @classmethod
    def _validate(cls, value: Any) -> "Color":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            return cls(value)
        raise ValueError(f"Cannot create Color from {type(value)}")

class Theme(BaseModel):
    primary: Color
    secondary: Color

theme = Theme(primary="#FF0000", secondary="#00FF00")
print(theme.model_dump())  # {'primary': '#FF0000', 'secondary': '#00FF00'}
```

**Step 3 — 다양한 관점**

| 비교 | v1 | v2 |
|------|----|----|
| 검증 속도 | 기준 | 5-50x 빠름 |
| JSON 직렬화 | Python json | Rust (jiter) |
| 커스텀 타입 | `__get_validators__` | `__get_pydantic_core_schema__` |
| strict mode | 없음 | `ConfigDict(strict=True)` |
| 에러 메시지 | Python 예외 | 구조화된 ValidationError |
| 메모리 | 모델 인스턴스 무거움 | `__slots__` 기반, 가벼움 |

**Step 4 — 실전 최적화 팁**

```python
# 1. TypeAdapter — BaseModel 없이 검증 (더 가벼움)
from pydantic import TypeAdapter

UserListValidator = TypeAdapter(list[User])
users = UserListValidator.validate_python(raw_data)
# BaseModel wrapping 없이 직접 검증 → 더 빠름

# 2. model_validate vs __init__
# model_validate: 외부 데이터 (dict, JSON) → 검증 + 변환
# __init__: 이미 검증된 데이터 → 검증 생략하고 싶으면 model_construct
user = User.model_construct(name="Alice", age=30)
# ⚠️ 검증 없이 생성 — 내부 코드에서만 사용

# 3. Deferred annotation 처리
from __future__ import annotations  # 모든 annotation이 문자열

class Tree(BaseModel):
    value: int
    children: list[Tree] = []  # ForwardRef

Tree.model_rebuild()  # 명시적 rebuild 필요
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| Pydantic v2 BaseModel | 검증+직렬화+스키마 | 런타임 비용 (작지만 있음) | API 입출력 |
| TypeAdapter | BaseModel 없이 검증 | 모델 기능 없음 | 내부 검증, 컬렉션 |
| model_construct | 검증 생략, 최고 속도 | 안전성 없음 | 내부 신뢰 데이터 |
| dataclasses | 표준, 가벼움 | 검증/직렬화 없음 | 내부 데이터 구조 |
| attrs | 유연, 슬롯 지원 | Pydantic보다 기능 적음 | 검증 불필요한 DTO |
| msgspec | Pydantic보다 빠름 | 생태계 작음 | 극한 성능 |

**Step 6 — 성장 & 심화 학습**
- pydantic-core 소스 (Rust) — `validators/` 디렉토리의 각 타입별 validator
- PyO3 — Rust ↔ Python 바인딩 프레임워크 (pydantic-core가 사용)
- `jiter` — pydantic이 사용하는 Rust JSON 파서 (속도 비밀)
- Pydantic v2 마이그레이션 가이드 + `bump-pydantic` 자동화 도구

**🎯 면접관 평가 기준:**
- L6 PASS: v2가 Rust 코어 사용. CoreSchema/SchemaValidator 개념. v1→v2 주요 변경점.
- L7 EXCEED: `__get_pydantic_core_schema__`로 커스텀 타입 구현. TypeAdapter 활용. model_construct의 용도와 위험성. Rust 컴파일 단계 설명.
- 🚩 RED FLAG: v1과 v2 API를 혼동. "Pydantic은 느리다"라는 구시대적 인식.

---

## 7. Performance & Profiling

### Q18: ASGI 서비스의 메모리 릭 진단과 GC 튜닝

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Performance & Profiling

**Question:**
"장시간 실행되는 FastAPI/ASGI 서비스에서 메모리가 점진적으로 증가하는 현상을 진단하고 해결하는 전체 과정을 설명하세요. tracemalloc, objgraph, memray 등의 도구를 비교하고, 실제 프로덕션에서 GC 튜닝으로 p99 latency를 개선한 사례를 논하세요."

---

**🧒 12살 비유:**
방이 매일 조금씩 더러워지는 거야. 처음엔 모르는데 한 달 후엔 움직이기도 힘들어(OOM kill). 메모리 릭 진단은 방을 사진 찍어서(snapshot) "어제와 오늘 뭐가 늘었나?" 비교하는 거야. tracemalloc은 "이 쓰레기가 어디서 왔는지" 추적하는 CCTV고, GC 튜닝은 청소 로봇의 청소 주기를 조정하는 거야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
메모리 릭은 프로덕션에서 가장 디버깅하기 어려운 문제 중 하나다. 특히 async 서비스에서는 코루틴, 클로저, 이벤트 핸들러의 순환 참조가 일반적이다. Staff 엔지니어는 체계적인 진단 프로세스와 도구 활용 능력을 보여야 한다.

**Step 2 — 핵심 기술 설명**

```python
# 진단 Step 1: 메모리 증가 패턴 확인
import psutil
import os

def get_memory_mb() -> float:
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

# FastAPI 미들웨어로 요청별 메모리 추적
@app.middleware("http")
async def memory_tracking(request, call_next):
    mem_before = get_memory_mb()
    response = await call_next(request)
    mem_after = get_memory_mb()
    mem_diff = mem_after - mem_before
    if mem_diff > 1.0:  # 1MB 이상 증가
        logger.warning(
            "Memory increase detected",
            path=request.url.path,
            mem_before=f"{mem_before:.1f}MB",
            mem_after=f"{mem_after:.1f}MB",
            diff=f"{mem_diff:.1f}MB",
        )
    return response
```

```python
# 진단 Step 2: tracemalloc으로 할당 추적
import tracemalloc
import linecache

# 앱 시작 시 활성화
tracemalloc.start(25)  # 25 프레임 깊이 추적

# 스냅샷 비교 엔드포인트
_snapshot1 = None

@app.get("/debug/memory/snapshot")
async def take_snapshot():
    global _snapshot1
    _snapshot1 = tracemalloc.take_snapshot()
    return {"status": "snapshot taken"}

@app.get("/debug/memory/diff")
async def memory_diff():
    if _snapshot1 is None:
        return {"error": "Take snapshot first"}
    snapshot2 = tracemalloc.take_snapshot()
    # 두 스냅샷 간 차이 — "어디서 메모리가 늘었나?"
    top_stats = snapshot2.compare_to(_snapshot1, "lineno")
    results = []
    for stat in top_stats[:20]:
        results.append({
            "file": str(stat.traceback),
            "size_diff": stat.size_diff,
            "size": stat.size,
            "count_diff": stat.count_diff,
        })
    return {"top_increases": results}
```

```python
# 진단 Step 3: objgraph로 객체 그래프 분석
import objgraph

@app.get("/debug/memory/objects")
async def object_stats():
    # 가장 많은 객체 타입
    most_common = objgraph.most_common_types(limit=20)

    # 증가하는 객체 타입 (두 번 호출해서 비교)
    growth = objgraph.growth(limit=20)

    return {
        "most_common": most_common,
        "growth": growth,
    }

# 특정 객체의 참조 체인 추적
# objgraph.show_backrefs(
#     objgraph.by_type('MyLeakyClass')[:3],
#     filename='refs.png'
# )
```

```python
# GC 튜닝: p99 latency 개선
import gc
import time

# 문제: Gen 2 GC가 10-50ms pause 유발
# → p99 latency spike

# 해결 1: GC threshold 조정
gc.set_threshold(50000, 500, 1000)
# Gen 0: 700 → 50000 (수집 빈도 감소)
# Gen 1: 10 → 500
# Gen 2: 10 → 1000
# 트레이드오프: 메모리 사용량 증가, 하지만 GC pause 빈도 감소

# 해결 2: GC를 비동기적으로 제어
class GCController:
    def __init__(self, gen2_interval: float = 60.0):
        self.gen2_interval = gen2_interval
        gc.disable()  # 자동 GC 비활성화
        gc.set_threshold(0)  # Gen 2 자동 수집 방지

    async def run(self):
        while True:
            # Gen 0, 1: 짧은 pause, 자주 실행
            gc.collect(0)
            gc.collect(1)

            # Gen 2: 유휴 시간에만
            await asyncio.sleep(self.gen2_interval)
            start = time.monotonic()
            collected = gc.collect(2)
            duration = time.monotonic() - start
            logger.info(
                "GC gen2 completed",
                collected=collected,
                duration_ms=f"{duration*1000:.1f}",
            )

# lifespan에서 시작
@asynccontextmanager
async def lifespan(app: FastAPI):
    gc_controller = GCController(gen2_interval=30.0)
    task = asyncio.create_task(gc_controller.run())
    yield
    task.cancel()
```

**Step 3 — 흔한 릭 패턴**

```python
# 릭 1: 글로벌 리스트/딕셔너리에 무한 축적
_request_log = []  # 🚫 무한 증가!

@app.middleware("http")
async def log_middleware(request, call_next):
    _request_log.append({  # 릭!
        "path": request.url.path,
        "time": datetime.now(),
    })
    return await call_next(request)

# 해결: maxlen 있는 deque 또는 외부 저장소
from collections import deque
_request_log = deque(maxlen=10000)

# 릭 2: 클로저가 큰 객체 캡처
def create_handler(large_data: bytes):
    async def handler():
        # large_data가 클로저에 캡처됨
        # handler가 살아있는 한 large_data도 GC 안 됨
        return len(large_data)
    return handler

# 릭 3: asyncio.Task 미정리
tasks = set()
async def fire_and_forget(coro):
    task = asyncio.create_task(coro)
    tasks.add(task)
    # task.add_done_callback(tasks.discard) 를 빼먹으면 릭!
    task.add_done_callback(tasks.discard)  # ✅
```

**Step 4 — 프로파일링 도구 비교**

| 도구 | 오버헤드 | 프로덕션 사용 | 추적 대상 | 특징 |
|------|---------|-------------|-----------|------|
| tracemalloc | 10-30% | 조건부 활성화 | Python 할당 | 스냅샷 비교, 할당 위치 |
| memray | 5-10% | 가능 | 모든 할당 (C 포함) | flamegraph, 가장 포괄적 |
| objgraph | 높음 | 디버깅 시만 | 객체 참조 | 그래프 시각화 |
| py-spy | ~0% | 가능 | CPU + 메모리 | 샘플링, 비침습적 |
| guppy3 (heapy) | 높음 | 디버깅 시만 | 힙 분석 | 상세하지만 느림 |

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| tracemalloc | 표준 라이브러리, 위치 추적 | Python만, 오버헤드 | 개발/스테이징 |
| memray | C 할당 포함, flamegraph | 외부 설치 | 프로덕션 디버깅 |
| GC 비활성화 + 수동 | latency 제어 | 릭 위험 | 저지연 서비스 |
| 프로세스 재시작 (workaround) | 간단 | 근본 해결 안 됨 | 긴급 대응 |

**Step 6 — 성장 & 심화 학습**
- Instagram의 메모리 최적화 사례 — copy-on-write + GC 비활성화
- `memray` (Bloomberg 개발) — Python 최고의 메모리 프로파일러
- Linux `/proc/{pid}/smaps` — RSS, PSS, USS 차이 이해
- `PYTHONMALLOC=malloc` + jemalloc — pymalloc 대체로 단편화 감소

**🎯 면접관 평가 기준:**
- L6 PASS: tracemalloc 스냅샷 비교. 흔한 릭 패턴(글로벌 리스트, 클로저). GC 세대 개념.
- L7 EXCEED: memray 활용, GC 튜닝 전략 + p99 개선 사례, 프로덕션 안전한 디버깅 엔드포인트 설계. pymalloc vs jemalloc 선택.
- 🚩 RED FLAG: "메모리 릭이면 서버 재시작하면 됩니다." 프로파일링 도구 사용 경험 없음.

---

### Q19: py-spy, cProfile, 그리고 async 코드 프로파일링

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Performance & Profiling

**Question:**
"async FastAPI 서비스의 CPU 성능 병목을 찾는 프로파일링 전략을 설명하세요. cProfile의 한계, py-spy의 장점, async 코드에서 wall-time vs CPU-time 프로파일링의 차이, 그리고 프로덕션에서 안전하게 프로파일링하는 방법을 논하세요."

---

**🧒 12살 비유:**
달리기 시합에서 느린 구간을 찾는 거야. cProfile은 스톱워치를 코스 곳곳에 달아놓은 거(침습적 — 스톱워치 무게로 느려짐). py-spy는 드론으로 위에서 사진 찍는 거(비침습적 — 선수에게 영향 없음). async에서는 "뛰는 시간(CPU)"과 "쉬는 시간(await 대기)"을 구분해야 진짜 느린 구간을 찾을 수 있어.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
async 코드 프로파일링은 전통적 도구로는 잘 안 된다. CPU 시간과 wall 시간의 차이를 이해하고, 프로덕션 서비스에 영향 없이 프로파일링하는 능력이 Staff 레벨에 기대된다.

**Step 2 — 핵심 기술 설명**

```python
# cProfile의 한계 — async에서 부정확
import cProfile

# cProfile은 함수 호출/반환을 추적
# async def에서는 await마다 "반환"으로 기록 → I/O 대기 시간이 누적됨
# CPU-bound 병목과 I/O 대기를 구분 못함

async def slow_handler():
    await asyncio.sleep(1)     # I/O 대기 1초
    heavy_computation()         # CPU 사용 0.01초
# cProfile: slow_handler = 1.01초 (CPU 병목이 아닌데 느려보임)

# py-spy: 샘플링 프로파일러 — 프로덕션 안전
# 장점:
# 1. 프로세스 외부에서 동작 (attach 방식)
# 2. 오버헤드 ~0% (샘플링 기반)
# 3. 실행 중인 프로세스에 연결 가능
# 4. native C extension 콜스택도 추적
```

```bash
# py-spy 사용법 (프로덕션)
# 1. flamegraph 생성
# py-spy record -o profile.svg --pid 12345 --duration 30

# 2. top-like 실시간 모니터링
# py-spy top --pid 12345

# 3. async 코드 프로파일링: --subprocesses + --native
# py-spy record -o profile.svg --pid 12345 --native --subprocesses

# 4. Wall-time vs CPU-time
# py-spy record --idle  # idle 스레드 포함 (wall-time 효과)
# py-spy record         # 기본: CPU 시간만 (active 스레드)
```

```python
# yappi: async 지원 프로파일러 (Python 레벨)
import yappi

# Wall-time 프로파일링 (async에 적합)
yappi.set_clock_type("wall")
yappi.start()

# ... 앱 실행 ...

yappi.stop()
# 코루틴별 통계
func_stats = yappi.get_func_stats()
func_stats.sort("totaltime", "desc")
func_stats.print_all(
    columns={
        0: ("name", 80),
        1: ("ncall", 10),
        2: ("tsub", 8),    # 자체 시간 (서브 호출 제외)
        3: ("ttot", 8),    # 총 시간
        4: ("tavg", 8),    # 평균 시간
    }
)

# 코루틴 추적도 가능
yappi.set_clock_type("cpu")  # CPU 시간만 — I/O 대기 제외
```

```python
# 프로덕션 안전 프로파일링 엔드포인트
import asyncio
import cProfile
import pstats
import io

@app.post("/debug/profile")
async def profile_endpoint(duration: int = 10):
    """특정 시간 동안 프로파일링 수행"""
    profiler = cProfile.Profile()
    profiler.enable()

    await asyncio.sleep(duration)

    profiler.disable()
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumulative")
    stats.print_stats(30)

    return {"profile": stream.getvalue()}

# 더 나은 방법: 미들웨어로 특정 요청만 프로파일링
@app.middleware("http")
async def profiling_middleware(request, call_next):
    if request.headers.get("X-Profile") == "true":
        import yappi
        yappi.set_clock_type("wall")
        yappi.start()
        response = await call_next(request)
        yappi.stop()
        stats = yappi.get_func_stats()
        # 결과를 응답 헤더나 별도 저장소에 기록
        stats.save("/tmp/profile.pstat", type="pstat")
        yappi.clear_stats()
        response.headers["X-Profile-File"] = "/tmp/profile.pstat"
        return response
    return await call_next(request)
```

**Step 3 — Wall-time vs CPU-time**

| 측정 | 포함 | 미포함 | 적합 |
|------|------|--------|------|
| CPU time | 실제 CPU 사용 시간 | I/O 대기, sleep, await | CPU-bound 병목 찾기 |
| Wall time | 모든 경과 시간 | - | I/O 병목 포함 전체 분석 |

```python
# 예시: DB 쿼리가 느린 경우
async def get_report():
    data = await db.execute(slow_query)  # 2초 대기 (wall)
    result = transform(data)              # 0.01초 CPU
    return result

# CPU profiling: transform이 100% — 오해 유발
# Wall profiling: db.execute가 99.5% — 실제 병목 발견
```

**Step 4 — 프로파일링 도구 비교**

| 도구 | 방식 | async 지원 | 프로덕션 | 오버헤드 | 출력 |
|------|------|-----------|---------|---------|------|
| cProfile | 계측 | 부분적 | 비권장 | 10-30% | pstats |
| py-spy | 샘플링 | 간접 | 안전 | ~0% | flamegraph |
| yappi | 계측 | 네이티브 | 조건부 | 5-20% | pstats, callgrind |
| scalene | 샘플링 | 제한적 | 개발 | 5-10% | HTML report |
| Austin | 샘플링 | 부분적 | 안전 | ~0% | flamegraph |

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| py-spy (external) | 비침습적, 프로덕션 안전 | async 세부 불가 | 프로덕션 CPU 분석 |
| yappi (internal) | async 네이티브, wall/cpu 선택 | 코드 수정 필요 | 개발/스테이징 |
| OpenTelemetry spans | 분산 추적, 구조적 | 수동 계측 | 서비스 간 레이턴시 |
| 커스텀 미들웨어 | 엔드포인트별 분석 | 제한적 | 특정 경로 병목 |

**Step 6 — 성장 & 심화 학습**
- `perf` (Linux) — 커널 레벨 프로파일링으로 syscall 분석
- `flamegraph.pl` — Brendan Gregg의 flamegraph 생성 도구
- Continuous profiling (Datadog, Pyroscope) — 프로덕션 상시 프로파일링
- `snakeviz` — cProfile 결과 시각화

**🎯 면접관 평가 기준:**
- L6 PASS: cProfile 한계, py-spy 사용법. wall-time vs CPU-time 차이.
- L7 EXCEED: yappi의 async 네이티브 프로파일링. 프로덕션 안전 프로파일링 설계. Continuous profiling 경험.
- 🚩 RED FLAG: async 코드에 cProfile만 사용. 프로덕션 프로파일링 경험 없음.

---

## 8. Testing at Scale

### Q20: pytest fixture lifecycle과 async 테스트 패턴

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Testing at Scale

**Question:**
"pytest의 fixture scope(function, class, module, session)와 async fixture의 lifecycle을 설명하세요. FastAPI + async SQLAlchemy 테스트에서 DB 격리를 보장하는 전략, 그리고 대규모 테스트 스위트의 실행 시간을 단축하는 기법을 논하세요."

---

**🧒 12살 비유:**
과학 실험을 생각해봐. 실험 전에 도구를 준비(setup)하고, 실험 후에 정리(teardown)해야 해. function scope는 "매 실험마다 새 도구", session scope는 "오늘 하루 같은 도구 계속 사용". DB 격리는 "각 실험이 다른 실험의 결과를 오염시키지 않게" 각자 다른 실험 테이블에서 하는 거야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
테스트 인프라 설계는 Staff 엔지니어의 핵심 역할이다. 특히 async + DB 테스트는 격리, 성능, 신뢰성 사이의 균형이 까다롭다. 수천 개 테스트를 수 분 내 실행하는 인프라를 설계할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

```python
# pytest fixture scope 계층
# session > package > module > class > function

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Session scope: 전체 테스트 스위트에서 한 번만
@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost/test_db",
        echo=False,
    )
    # 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    # 테스트 종료 후 정리
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

# Function scope: 매 테스트마다 새로운 세션
@pytest_asyncio.fixture(scope="function")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    # 트랜잭션 격리 패턴
    async with engine.connect() as connection:
        await connection.begin()  # 트랜잭션 시작
        session = AsyncSession(bind=connection, expire_on_commit=False)

        yield session

        # 테스트 후: 롤백으로 모든 변경 취소
        await session.close()
        await connection.rollback()  # 핵심! DB 격리 보장

@pytest_asyncio.fixture(scope="function")
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    # DI override로 테스트 세션 주입
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()
```

**DB 격리 전략 비교:**
```python
# 전략 1: 트랜잭션 롤백 (가장 빠름, 권장)
# 장점: 매우 빠름 (COMMIT 안 함)
# 단점: 코드 내 commit이 있으면 깨짐 (nested transaction 필요)
@pytest_asyncio.fixture
async def db_session(engine):
    async with engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()  # SAVEPOINT — 앱의 commit이 이것만 커밋

        session = AsyncSession(bind=conn)

        @event.listens_for(session.sync_session, "after_transaction_end")
        def restart_savepoint(session, transaction):
            if transaction.nested and not transaction._parent.nested:
                session.begin_nested()

        yield session
        await session.close()
        await conn.rollback()

# 전략 2: TRUNCATE (중간 속도)
@pytest_asyncio.fixture
async def db_session(engine):
    session = AsyncSession(engine)
    yield session
    await session.close()
    # 모든 테이블 truncate
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f"TRUNCATE {table.name} CASCADE"))

# 전략 3: 테스트별 DB (가장 안전, 가장 느림)
# CI에서 병렬 실행 시 유용
@pytest.fixture(scope="session")
def db_name():
    import uuid
    return f"test_{uuid.uuid4().hex[:8]}"
```

**Step 3 — 대규모 테스트 실행 최적화**

```python
# 1. pytest-xdist: 병렬 실행
# pytest -n 4 --dist=loadscope  # 4 프로세스, 모듈 단위 분배

# 2. 테스트 DB 격리 (병렬 안전)
@pytest.fixture(scope="session")
def worker_id(request):
    """pytest-xdist worker ID"""
    if hasattr(request.config, "workerinput"):
        return request.config.workerinput["workerid"]
    return "master"

@pytest_asyncio.fixture(scope="session")
async def engine(worker_id):
    db_name = f"test_db_{worker_id}"
    # 워커별 별도 DB 생성
    admin_engine = create_async_engine("postgresql+asyncpg://postgres@localhost/postgres")
    async with admin_engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
        await conn.execute(text(f"CREATE DATABASE {db_name}"))
    await admin_engine.dispose()

    engine = create_async_engine(f"postgresql+asyncpg://postgres@localhost/{db_name}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

# 3. Factory fixture 패턴 — 테스트 데이터 생성
@pytest.fixture
def make_user(db_session):
    async def _make_user(**kwargs) -> User:
        defaults = {
            "name": "Test User",
            "email": f"test_{uuid.uuid4().hex[:6]}@example.com",
        }
        defaults.update(kwargs)
        user = User(**defaults)
        db_session.add(user)
        await db_session.flush()
        return user
    return _make_user

async def test_user_permissions(client, make_user):
    user = await make_user(name="Admin", role="admin")
    response = await client.get(f"/users/{user.id}/permissions")
    assert response.status_code == 200
```

**Step 4 — async 테스트 특수 패턴**

```python
# pytest-asyncio configuration
# pyproject.toml
# [tool.pytest.ini_options]
# asyncio_mode = "auto"  # 모든 async def test_*를 자동 인식

# anyio로 backend 독립적 테스트
import anyio

@pytest.mark.anyio
async def test_with_anyio():
    async with anyio.create_task_group() as tg:
        tg.start_soon(some_task)

# 타임아웃 설정
@pytest.mark.timeout(10)  # 10초 제한
async def test_potentially_hanging():
    result = await slow_operation()
    assert result is not None

# mock async 함수
from unittest.mock import AsyncMock

async def test_external_call(client, monkeypatch):
    mock_response = AsyncMock(return_value={"status": "ok"})
    monkeypatch.setattr("app.services.external_api.call", mock_response)

    response = await client.post("/process")
    assert response.status_code == 200
    mock_response.assert_awaited_once()
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| 트랜잭션 롤백 | 최고 속도 | savepoint 복잡도 | 대부분 (권장) |
| TRUNCATE | 간단, 안전 | 느림 (100ms+/테스트) | 트랜잭션 테스트 |
| 워커별 DB | 완전 격리 | 생성/삭제 오버헤드 | CI 병렬 실행 |
| SQLite in-memory | 초고속 | PostgreSQL 비호환 | 유닛 테스트 (비권장) |
| Testcontainers | 실제 DB, 격리 | Docker 필요, 느린 시작 | 통합 테스트 |

**Step 6 — 성장 & 심화 학습**
- `factory_boy` + `faker` — 테스트 데이터 팩토리 자동화
- `hypothesis` — property-based testing으로 edge case 발견
- `testcontainers-python` — Docker 기반 테스트 인프라
- pytest 플러그인 개발 — 커스텀 fixture/marker 생성

**🎯 면접관 평가 기준:**
- L6 PASS: fixture scope 이해. 트랜잭션 롤백 격리. AsyncClient 사용.
- L7 EXCEED: savepoint 기반 격리의 내부 동작. pytest-xdist 병렬 전략. Factory fixture 패턴.
- 🚩 RED FLAG: 테스트 간 상태 공유. 실제 DB 없이 SQLite로 테스트. mock 남용.

---

### Q21: Property-Based Testing과 Contract Testing

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Testing at Scale

**Question:**
"property-based testing(hypothesis)과 contract testing(schemathesis)을 설명하세요. 기존 example-based testing의 한계, property-based testing이 발견하는 버그 유형, 그리고 FastAPI의 OpenAPI 스키마를 활용한 자동 API 테스트 전략을 논하세요."

---

**🧒 12살 비유:**
수학 시험에서 선생님이 "3+5=8, 7+2=9" 같은 예시 문제(example-based)만 내면 특정 경우만 확인해. property-based는 "아무 두 수를 더해도 각각보다 크거나 같다"는 규칙을 확인하는 거야. 컴퓨터가 수천 가지 랜덤 숫자를 넣어보고 규칙이 깨지는 걸 찾아.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
example-based 테스트는 개발자가 생각한 경우만 테스트한다. Property-based testing은 프로그램의 불변 조건(invariant)을 명시하고 자동으로 반례를 찾아 보이지 않는 버그를 발견한다. Staff 엔지니어는 이를 활용해 테스트 커버리지의 질을 높일 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

```python
from hypothesis import given, strategies as st, assume, settings
from hypothesis import HealthCheck

# 기본: 데이터 변환 함수의 속성 테스트
def serialize_user(user: dict) -> bytes:
    return json.dumps(user, sort_keys=True).encode()

def deserialize_user(data: bytes) -> dict:
    return json.loads(data)

# Property: serialize → deserialize = identity
@given(st.fixed_dictionaries({
    "name": st.text(min_size=1, max_size=100),
    "age": st.integers(min_value=0, max_value=150),
    "email": st.emails(),
}))
def test_roundtrip(user):
    """직렬화 후 역직렬화하면 원본과 동일해야 한다"""
    serialized = serialize_user(user)
    deserialized = deserialize_user(serialized)
    assert deserialized == user

# Pydantic 모델 검증 속성
@given(st.builds(
    User,
    name=st.text(min_size=1, max_size=100),
    age=st.integers(min_value=0, max_value=150),
))
def test_user_model_validity(user: User):
    """생성된 모든 User 모델은 유효해야 한다"""
    dumped = user.model_dump()
    restored = User.model_validate(dumped)
    assert restored == user
```

```python
# Stateful testing — 상태 기반 테스트
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize

class UserAPIMachine(RuleBasedStateMachine):
    """API의 상태 전이가 올바른지 검증"""

    def __init__(self):
        super().__init__()
        self.users: dict[int, dict] = {}  # 모델 상태
        self.client = TestClient(app)

    @initialize()
    def init_db(self):
        self.client.post("/admin/reset-db")
        self.users.clear()

    @rule(name=st.text(min_size=1, max_size=50), age=st.integers(0, 150))
    def create_user(self, name, age):
        resp = self.client.post("/users", json={"name": name, "age": age})
        if resp.status_code == 201:
            user_id = resp.json()["id"]
            self.users[user_id] = {"name": name, "age": age}

    @rule(data=st.data())
    def get_user(self, data):
        if not self.users:
            return
        user_id = data.draw(st.sampled_from(list(self.users.keys())))
        resp = self.client.get(f"/users/{user_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == self.users[user_id]["name"]

    @rule(data=st.data())
    def delete_user(self, data):
        if not self.users:
            return
        user_id = data.draw(st.sampled_from(list(self.users.keys())))
        resp = self.client.delete(f"/users/{user_id}")
        assert resp.status_code == 204
        del self.users[user_id]
        # 삭제 후 조회 시 404 확인
        resp = self.client.get(f"/users/{user_id}")
        assert resp.status_code == 404

TestUserAPI = UserAPIMachine.TestCase
```

```python
# Schemathesis: OpenAPI 스키마 기반 자동 API 테스트
# pip install schemathesis

import schemathesis

schema = schemathesis.from_asgi("/openapi.json", app=app)

@schema.parametrize()
def test_api(case):
    """
    OpenAPI 스키마의 모든 엔드포인트에 대해:
    1. 스키마에 맞는 랜덤 요청 생성
    2. 응답이 스키마와 일치하는지 검증
    3. 5xx 에러 발생하지 않는지 확인
    """
    response = case.call_asgi()
    case.validate_response(response)

# CLI 사용
# schemathesis run http://localhost:8000/openapi.json
# --stateful=links  # 상태 기반 테스트 (링크 따라가기)
# --hypothesis-max-examples=1000
```

**Step 3 — property-based testing이 발견하는 버그 유형**

| 버그 유형 | 예시 | example-based로 놓치는 이유 |
|-----------|------|--------------------------|
| 경계값 | 빈 문자열, 0, 음수, MAX_INT | 개발자가 정상 케이스만 테스트 |
| Unicode | 이모지, 특수문자, RTL 텍스트 | ASCII만 생각 |
| 부동소수점 | NaN, Inf, 정밀도 오차 | 정수로만 테스트 |
| 순서 의존 | 특정 순서에서만 발생하는 race | 고정된 순서만 테스트 |
| 크기 | 매우 큰/작은 입력 | 적당한 크기만 테스트 |

**Step 4 — 실전 통합**

```python
# hypothesis + Pydantic v2 통합
from hypothesis import strategies as st
from pydantic import BaseModel

def pydantic_strategy(model_cls: type[BaseModel]) -> st.SearchStrategy:
    """Pydantic 모델에서 자동으로 hypothesis strategy 생성"""
    field_strategies = {}
    for name, field_info in model_cls.model_fields.items():
        annotation = field_info.annotation
        if annotation is str:
            field_strategies[name] = st.text(max_size=100)
        elif annotation is int:
            field_strategies[name] = st.integers()
        elif annotation is float:
            field_strategies[name] = st.floats(allow_nan=False)
        elif annotation is bool:
            field_strategies[name] = st.booleans()
        # ... 더 많은 타입 매핑
    return st.builds(model_cls, **field_strategies)

# hypothesis-jsonschema 패키지로 더 정확하게
# from hypothesis_jsonschema import from_schema
# strategy = from_schema(User.model_json_schema())
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| Example-based | 명확, 읽기 쉬움 | 편향된 커버리지 | 비즈니스 로직, 핵심 시나리오 |
| Property-based | 자동 탐색, edge case 발견 | 느림, property 정의 어려움 | 직렬화, 변환, 알고리즘 |
| Schemathesis | OpenAPI 자동 테스트 | False positive 가능 | API 견고성 |
| Fuzzing (atheris) | 보안 취약점 발견 | 설정 복잡 | 파서, 보안 코드 |

**Step 6 — 성장 & 심화 학습**
- `hypothesis` profiles — CI에서 더 많은 예제 실행
- `hypothesis.database` — 이전에 실패한 입력 기억 (회귀 방지)
- `crosshair` — symbolic execution으로 반례 찾기
- `dredd` — API Blueprint/OpenAPI 기반 계약 테스트

**🎯 면접관 평가 기준:**
- L6 PASS: property-based testing 개념과 hypothesis 기본 사용법. roundtrip 속성 테스트.
- L7 EXCEED: stateful testing (RuleBasedStateMachine). schemathesis 활용. 커스텀 strategy 생성. property-based가 발견하는 구체적 버그 유형.
- 🚩 RED FLAG: "랜덤 테스트는 비결정적이라 쓸모없다." property를 정의할 줄 모름.

---

## 9. Production Debugging

### Q22: Structured Logging과 async context 분산 트레이싱

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Production Debugging

**Question:**
"FastAPI 서비스에서 structured logging(structlog)을 설계하고, 요청 간 context를 전파하는 방법을 설명하세요. async 환경에서 `contextvars`가 어떻게 동작하는지, OpenTelemetry와 통합한 분산 트레이싱 전략, 그리고 로그 기반 디버깅의 한계와 보완 방법을 논하세요."

---

**🧒 12살 비유:**
택배 추적 시스템이야. 택배(요청)에 추적 번호(trace_id)를 붙여. 택배가 물류센터(서비스)를 거칠 때마다 "14:03 서울센터 도착, 14:30 분류 완료"처럼 기록(structured log). 이 번호로 어디서 지연됐는지 전체 경로를 추적할 수 있어. contextvars는 택배에 붙은 스티커야 — 어디를 가든 그 정보가 같이 따라다녀.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
프로덕션 디버깅의 90%는 로그에서 시작한다. 비구조화 로그(`print`, `logging.info("User created")`)로는 수만 RPS 환경에서 문제를 찾을 수 없다. Staff 엔지니어는 structured logging + 분산 트레이싱 인프라를 설계할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

```python
# structlog 설정 — JSON structured logging
import structlog
import logging
from contextvars import ContextVar

# Request context를 ContextVar로 관리
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
user_id_var: ContextVar[int | None] = ContextVar("user_id", default=None)

def add_request_context(logger, method_name, event_dict):
    """structlog processor: ContextVar에서 자동으로 컨텍스트 추가"""
    request_id = request_id_var.get()
    if request_id:
        event_dict["request_id"] = request_id
    user_id = user_id_var.get()
    if user_id:
        event_dict["user_id"] = user_id
    return event_dict

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,  # contextvars 자동 병합
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        add_request_context,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),  # JSON 출력
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()
```

```python
# FastAPI 미들웨어: 요청별 context 설정
import uuid
from starlette.middleware.base import BaseHTTPMiddleware

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # trace_id: 외부에서 오거나 신규 생성
        request_id = request.headers.get(
            "X-Request-ID",
            str(uuid.uuid4())
        )
        # ContextVar 설정 — async에서 자동 전파!
        request_id_var.set(request_id)

        # structlog contextvars 사용 (더 편리)
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            path=request.url.path,
            method=request.method,
        )

        logger.info("request_started")
        response = await call_next(request)

        logger.info(
            "request_completed",
            status_code=response.status_code,
        )

        response.headers["X-Request-ID"] = request_id
        return response

# ContextVar가 async에서 작동하는 이유:
# - asyncio.Task는 생성 시 현재 Context를 복사
# - 각 코루틴이 자신의 Context에서 실행
# - threading.local과 달리 코루틴 간 격리됨
```

```python
# OpenTelemetry 통합
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

# 설정
provider = TracerProvider()
processor = BatchSpanProcessor(
    OTLPSpanExporter(endpoint="http://jaeger:4317")
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# 자동 계측
FastAPIInstrumentor.instrument_app(app)
SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
HTTPXClientInstrumentor().instrument()

# 커스텀 span 추가
tracer = trace.get_tracer(__name__)

async def process_order(order_data: dict):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_data["id"])
        span.set_attribute("order.total", order_data["total"])

        with tracer.start_as_current_span("validate_inventory"):
            await check_inventory(order_data["items"])

        with tracer.start_as_current_span("charge_payment"):
            await process_payment(order_data)

# structlog + OpenTelemetry 연결
def add_trace_context(logger, method_name, event_dict):
    span = trace.get_current_span()
    if span.is_recording():
        ctx = span.get_span_context()
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict
# → 로그에 trace_id 포함 → Jaeger/Tempo에서 검색 가능
```

**Step 3 — 다양한 관점**

| 비교 | 비구조화 로그 | structlog (JSON) | OpenTelemetry |
|------|-------------|-----------------|---------------|
| 검색 | grep (느림) | ELK 쿼리 (빠름) | trace_id 추적 |
| 컨텍스트 | 수동 포매팅 | 자동 바인딩 | 자동 전파 |
| 비용 | 낮음 | 중간 (인프라) | 높음 (인프라) |
| 분석 | 제한적 | 집계/대시보드 | 분산 추적 |
| 적합 규모 | 개발/소규모 | 중규모 | 대규모/마이크로서비스 |

**Step 4 — 프로덕션 패턴**

```python
# 로그 레벨 동적 변경 (재배포 없이)
import logging

@app.post("/admin/log-level")
async def set_log_level(level: str):
    numeric_level = getattr(logging, level.upper(), None)
    if numeric_level is None:
        raise HTTPException(400, f"Invalid log level: {level}")
    logging.getLogger().setLevel(numeric_level)
    return {"level": level}

# 요청별 상세 로깅 (feature flag 기반)
@app.middleware("http")
async def debug_logging_middleware(request, call_next):
    # 특정 사용자/요청만 DEBUG 레벨
    if request.headers.get("X-Debug") == "true":
        structlog.contextvars.bind_contextvars(debug=True)
        # 이 요청에서는 SQL 쿼리, 응답 본문 등 상세 로깅
    return await call_next(request)

# 에러 로그에 충분한 컨텍스트 포함
@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.error(
        "unhandled_exception",
        exc_type=type(exc).__name__,
        exc_message=str(exc),
        path=request.url.path,
        method=request.method,
        query_params=dict(request.query_params),
        # body는 이미 consume되었을 수 있으므로 주의
        exc_info=exc,  # structlog가 traceback 포함
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| structlog + JSON | 구조화, 검색 용이 | 설정 복잡도 | 모든 프로덕션 서비스 |
| OpenTelemetry | 표준, 벤더 중립 | 인프라 비용 | 마이크로서비스 |
| Sentry | 에러 집계, alerting | SaaS 비용 | 에러 모니터링 |
| ELK/Loki | 로그 집계/검색 | 운영 복잡도 | 로그 분석 |

**Step 6 — 성장 & 심화 학습**
- W3C Trace Context 표준 — `traceparent` 헤더 형식
- `contextvars` 내부 구현 (PEP 567) — copy-on-write Context
- structlog vs loguru vs stdlib logging — 성능/기능 비교
- Exemplar 패턴 — 메트릭에 trace_id 연결 (Prometheus + Tempo)

**🎯 면접관 평가 기준:**
- L6 PASS: structured logging 필요성. ContextVar로 request_id 전파. OpenTelemetry 기본 설정.
- L7 EXCEED: ContextVar가 async Task에서 복사되는 메커니즘. 로그 + 트레이스 + 메트릭 통합(3 pillars). 동적 로그 레벨 변경.
- 🚩 RED FLAG: `print`로 디버깅. 로그에 request_id 없음. 분산 추적 경험 없음.

---

### Q23: 프로덕션 메모리 덤프와 faulthandler

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Production Debugging

**Question:**
"프로덕션에서 Python 프로세스가 hang(무응답)되었을 때의 진단 절차를 설명하세요. `faulthandler`, `signal` 기반 스레드 덤프, `gdb`를 이용한 CPython 디버깅, 그리고 async 서비스에서 deadlock/hang을 진단하는 방법을 논하세요."

---

**🧒 12살 비유:**
컴퓨터가 멈춘 것 같아. 화면에 아무것도 안 나와. faulthandler는 "지금 뭐 하고 있었니?" 물어보는 거야 — 프로그램이 어디서 멈췄는지 사진(traceback)을 찍어줘. gdb는 의사가 환자를 정밀 검사하는 것처럼 프로그램 내부를 직접 들여다보는 거야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
프로덕션 hang은 재현이 어렵고, 전통적 디버깅이 불가능하다. Staff 엔지니어는 실행 중인 프로세스에서 비침습적으로 정보를 추출하고, 근본 원인을 찾을 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

```python
# faulthandler: segfault나 hang 시 traceback 출력
import faulthandler
import sys

# 1. 기본 활성화 — SIGSEGV, SIGFPE 등에서 traceback
faulthandler.enable(file=sys.stderr)

# 2. 주기적 traceback 덤프 (watchdog)
faulthandler.dump_traceback_later(
    timeout=300,       # 300초 후 덤프
    repeat=True,       # 반복
    file=sys.stderr,
    exit=False,        # 덤프 후 계속 실행
)

# 3. 시그널로 즉시 덤프 (프로덕션 핵심!)
import signal

def dump_traceback(signum, frame):
    """SIGUSR1 수신 시 모든 스레드 traceback 출력"""
    faulthandler.dump_traceback(file=sys.stderr, all_threads=True)

signal.signal(signal.SIGUSR1, dump_traceback)
# 사용: kill -USR1 <pid>
```

```python
# 더 상세한 async task 덤프
import asyncio
import signal
import traceback

def dump_async_tasks(signum, frame):
    """SIGUSR2: 모든 async task의 코루틴 스택 출력"""
    loop = asyncio.get_event_loop()
    if loop.is_running():
        tasks = asyncio.all_tasks(loop)
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"ASYNC TASK DUMP: {len(tasks)} tasks", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        for task in tasks:
            print(f"\nTask: {task.get_name()}", file=sys.stderr)
            print(f"State: {'done' if task.done() else 'pending'}", file=sys.stderr)
            coro = task.get_coro()
            if coro is not None:
                print(f"Coroutine: {coro}", file=sys.stderr)
                # 코루틴 스택 프레임 추출
                frames = []
                cr = coro
                while cr is not None:
                    if hasattr(cr, 'cr_frame') and cr.cr_frame:
                        frames.append(cr.cr_frame)
                    cr = getattr(cr, 'cr_await', None)
                if frames:
                    print("Stack:", file=sys.stderr)
                    for line in traceback.format_stack(frames[0]):
                        print(f"  {line.rstrip()}", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)

    # 동기 스레드도 덤프
    faulthandler.dump_traceback(file=sys.stderr, all_threads=True)

signal.signal(signal.SIGUSR2, dump_async_tasks)
# 사용: kill -USR2 <pid>
```

```python
# 프로덕션 hang 진단 절차

# Step 1: 프로세스 상태 확인
# ps aux | grep python
# strace -p <pid> -c  # syscall 분석 (Linux)
# dtruss -p <pid>      # macOS

# Step 2: faulthandler 덤프
# kill -USR1 <pid>  → 동기 스레드 traceback
# kill -USR2 <pid>  → async task 덤프

# Step 3: py-spy로 실시간 확인
# py-spy dump --pid <pid>  # 모든 스레드 스택
# py-spy top --pid <pid>   # CPU 사용 실시간

# Step 4: GDB 디버깅 (최후의 수단)
# gdb python <pid>
# (gdb) py-bt           # Python traceback (CPython debug symbols 필요)
# (gdb) info threads    # 모든 스레드
# (gdb) thread apply all py-bt  # 모든 스레드의 Python traceback
```

**Step 3 — 흔한 hang 원인과 진단**

```python
# Hang 1: Deadlock (threading)
import threading

lock_a = threading.Lock()
lock_b = threading.Lock()

def worker_1():
    with lock_a:
        time.sleep(0.1)
        with lock_b:  # lock_b를 기다리며 hang
            pass

def worker_2():
    with lock_b:
        time.sleep(0.1)
        with lock_a:  # lock_a를 기다리며 hang
            pass
# 진단: faulthandler dump에서 두 스레드가 각각 다른 lock에서 대기

# Hang 2: Event loop 블로킹 (async)
async def bad_handler():
    # 동기 I/O가 event loop 블로킹 → 전체 서버 멈춤
    data = requests.get("http://slow-api.com")  # 60초 타임아웃
# 진단: py-spy에서 requests.get이 CPU 0%인데 wall-time 100%

# Hang 3: 풀 고갈 (DB connections)
# 모든 커넥션이 사용 중 → 새 요청이 pool_timeout까지 대기
# 진단: pg_stat_activity에서 idle in transaction 커넥션 확인
```

**Step 4 — 안전한 프로덕션 디버깅 엔드포인트**

```python
@app.get("/debug/threads")
async def debug_threads():
    """스레드 상태 덤프 (인증 필수!)"""
    import threading
    threads = []
    for thread in threading.enumerate():
        threads.append({
            "name": thread.name,
            "daemon": thread.daemon,
            "alive": thread.is_alive(),
            "ident": thread.ident,
        })
    return {"threads": threads, "count": len(threads)}

@app.get("/debug/tasks")
async def debug_tasks():
    """async task 상태"""
    tasks = asyncio.all_tasks()
    task_info = []
    for task in tasks:
        task_info.append({
            "name": task.get_name(),
            "done": task.done(),
            "cancelled": task.cancelled(),
            "coro": str(task.get_coro()),
        })
    return {"tasks": task_info, "count": len(task_info)}
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| faulthandler + signal | 표준, 경량 | 출력 해석 수동 | 기본 설정 (항상 ON) |
| py-spy | 비침습적, 프로덕션 안전 | 외부 도구 필요 | 실시간 CPU 분석 |
| gdb + py-bt | 최심층 디버깅 | 프로세스 일시 정지 | C extension 디버깅 |
| aiomonitor | async 특화 | 별도 포트 필요 | async 서비스 개발 |
| core dump | 사후 분석 가능 | 큰 파일 크기 | crash 분석 |

**Step 6 — 성장 & 심화 학습**
- `aiomonitor` — 실행 중 async 앱에 telnet 접속해서 Task 상태 확인
- CPython debug build — `--with-pydebug` 옵션으로 빌드해서 gdb 확장 사용
- `pyrasite` — 실행 중 Python 프로세스에 코드 주입 (디버깅용)
- Linux `perf` + Python `perf` support (3.12+) — 커널 레벨 프로파일링

**🎯 면접관 평가 기준:**
- L6 PASS: faulthandler 활성화. signal 기반 traceback dump. py-spy 사용.
- L7 EXCEED: async task dump 구현. deadlock vs pool exhaustion 구분. gdb + py-bt 활용. 프로덕션 안전 디버깅 엔드포인트 설계.
- 🚩 RED FLAG: "프로덕션에서는 디버깅할 수 없다." faulthandler 모름.

---

## 10. Design Patterns in Python

### Q24: 동적 언어에서의 SOLID와 DI 패턴

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Design Patterns in Python

**Question:**
"SOLID 원칙이 Python과 같은 동적 언어에서 어떻게 다르게 적용되는지 설명하세요. 특히 DIP(Dependency Inversion)를 프레임워크 없이 구현하는 방법, duck typing이 인터페이스를 어떻게 대체하는지, 그리고 과도한 추상화(over-engineering)를 피하는 기준을 논하세요."

---

**🧒 12살 비유:**
Java/C#에서 SOLID는 꼭 맞는 정장(interface, abstract class)을 입어야 해. Python에서는 캐주얼(duck typing)도 괜찮아 — "넥타이를 매야 한다"는 규칙(Interface) 없이도 "깔끔하게 입으면 돼(Protocol)". 하지만 회사가 커지면 드레스코드(타입 힌트)가 필요해질 수 있어.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
Java/C#에서 온 개발자는 Python에서 과도한 추상화를 만들고, 순수 Python 개발자는 추상화가 너무 적은 경향이 있다. Staff 엔지니어는 "Python스러운" 적절한 추상화 수준을 판단할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

```python
# Python에서의 DIP: 프레임워크 없이 DI

# Java 스타일 (과도한 추상화)
class UserRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, id: int) -> User: ...
    @abstractmethod
    async def save(self, user: User) -> None: ...

class PostgresUserRepository(UserRepositoryInterface):
    async def get(self, id: int) -> User: ...
    async def save(self, user: User) -> None: ...

class UserService:
    def __init__(self, repo: UserRepositoryInterface): ...

# Python 스타일 (Protocol 기반, 필요할 때만 추상화)
class UserRepository(Protocol):
    async def get(self, id: int) -> User | None: ...
    async def save(self, user: User) -> None: ...

class PostgresUserRepository:
    """Protocol을 상속하지 않지만 호환됨"""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> User | None:
        return await self.session.get(User, id)

    async def save(self, user: User) -> None:
        self.session.add(user)
        await self.session.flush()

# DI: 단순 함수 인자로 주입
class UserService:
    def __init__(self, repo: UserRepository):  # Protocol 타입 힌트
        self.repo = repo

# FastAPI에서의 DI
async def get_user_repo(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> PostgresUserRepository:
    return PostgresUserRepository(db)

async def get_user_service(
    repo: Annotated[PostgresUserRepository, Depends(get_user_repo)]
) -> UserService:
    return UserService(repo)

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.get(user_id)
```

**Python에서 SOLID이 달라지는 점:**

```python
# SRP (Single Responsibility) — 동일하게 중요
# 다만 Python에서는 모듈 수준 함수로도 충분한 경우가 많음
# Java: UserValidator class
# Python: validate_user() 함수면 충분할 수 있음

# OCP (Open/Closed) — 데코레이터와 1급 함수로 자연스럽게
def with_retry(max_attempts: int = 3):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except TransientError:
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)
        return wrapper
    return decorator

@with_retry(max_attempts=3)
async def call_external_api(url: str):
    ...
# 기존 함수를 수정 없이 확장 (Open for extension, Closed for modification)

# LSP (Liskov Substitution) — duck typing이 자연스럽게 보장
# 같은 인터페이스(메서드 시그니처)를 가지면 치환 가능

# ISP (Interface Segregation) — Protocol로 작은 인터페이스
class Readable(Protocol):
    def read(self) -> bytes: ...

class Writable(Protocol):
    def write(self, data: bytes) -> None: ...

class ReadWrite(Readable, Writable, Protocol):
    ...
# 필요한 것만 요구 — file, socket, BytesIO 모두 호환

# DIP (Dependency Inversion) — 위에서 설명한 Protocol + DI
```

**Step 3 — 과도한 추상화 판단 기준**

```python
# ✅ 추상화가 가치 있는 경우:
# 1. 구현이 2개 이상 존재하거나 예정 (테스트 mock 포함)
# 2. 외부 시스템 의존 (DB, API, 메시지 큐)
# 3. 비즈니스 규칙이 복잡하고 변경 가능

# 🚫 과도한 추상화 징후:
# 1. AbstractFactory → ConcreteFactory → Factory → UserFactory (4계층)
# 2. 인터페이스에 구현이 딱 하나, 앞으로도 하나
# 3. DTO → Domain → Response 변환이 모두 동일한 필드 복사
# 4. "미래를 위한" 추상화 (YAGNI 위반)

# Python의 "적절한 추상화 수준"
# Rule of Three: 같은 패턴이 3번 반복될 때 추상화
# Start concrete, abstract when needed
```

**Step 4 — 실용적 패턴**

```python
# 1. Registry 패턴 — 플러그인 아키텍처
from typing import Callable, Any

HandlerFunc = Callable[[dict], Any]
_handlers: dict[str, HandlerFunc] = {}

def register(event_type: str):
    def decorator(func: HandlerFunc) -> HandlerFunc:
        _handlers[event_type] = func
        return func
    return decorator

@register("user.created")
async def handle_user_created(event: dict):
    ...

@register("order.placed")
async def handle_order_placed(event: dict):
    ...

async def dispatch(event: dict):
    handler = _handlers.get(event["type"])
    if handler:
        await handler(event)

# 2. Strategy 패턴 — 함수가 곧 전략
# Java: Strategy interface → ConcreteStrategy class
# Python: 함수 전달
PricingStrategy = Callable[[float, int], float]

def flat_discount(price: float, quantity: int) -> float:
    return price * 0.9

def volume_discount(price: float, quantity: int) -> float:
    if quantity > 100:
        return price * 0.7
    return price * 0.85

def calculate_total(
    items: list[dict],
    strategy: PricingStrategy = flat_discount,
) -> float:
    return sum(strategy(item["price"], item["qty"]) for item in items)
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| Protocol (structural) | 느슨한 결합, 유연 | IDE 자동완성 제한적 | 라이브러리 API, 플러그인 |
| ABC (nominal) | 명시적, 구현 강제 | 결합도 높음 | 내부 핵심 추상화 |
| 함수 전달 | 간단, Pythonic | 복잡한 상태 관리 어려움 | Strategy, Callback |
| DI 프레임워크 (dependency-injector) | 체계적, 스코프 관리 | 복잡도 추가 | 대규모 앱 |
| FastAPI Depends | 프레임워크 통합 | FastAPI 종속 | Web API |

**Step 6 — 성장 & 심화 학습**
- Brandon Rhodes의 "Python Design Patterns" — pythonic 패턴 해석
- "Stop Writing Classes" (PyCon talk by Jack Diederich) — 과도한 클래스화 경계
- Clean Architecture in Python — domain layer에서의 추상화 원칙
- `dependency-injector` 라이브러리 — 대규모 DI 컨테이너

**🎯 면접관 평가 기준:**
- L6 PASS: SOLID을 Python 컨텍스트에서 설명. Protocol 기반 DI. 과도한 추상화 인식.
- L7 EXCEED: "Java SOLID != Python SOLID" 명확한 구분. 추상화 기준(Rule of Three). 함수 기반 패턴(Strategy, Registry)이 클래스 기반보다 나은 경우 제시.
- 🚩 RED FLAG: Java 패턴을 Python에 그대로 이식. 모든 것에 ABC 사용. YAGNI 무시.

---

### Q25: Context Manager 패턴과 리소스 관리

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Design Patterns in Python

**Question:**
"Python의 context manager 패턴을 깊이 있게 설명하세요. `__enter__`/`__exit__` vs `contextlib` vs async context manager, 그리고 프로덕션에서 리소스 관리(DB 커넥션, 파일 핸들, 분산 락)에 어떻게 활용하는지 실전 코드와 함께 논하세요. 중첩 context manager, ExitStack, 그리고 에러 처리 전략도 포함하세요."

---

**🧒 12살 비유:**
도서관에서 책을 빌리는 절차야. `with`는 "도서관 들어가기(enter) → 책 읽기(body) → 나올 때 반드시 반납(exit)"을 자동으로 해주는 거야. 비가 와도 지진이 나도(예외) 책은 반납돼. `ExitStack`은 여러 도서관에서 동시에 빌릴 때 "어디서 빌렸든 전부 반납"을 보장해주는 매니저야.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
리소스 관리 실수는 커넥션 릭, 파일 핸들 고갈, 분산 락 미해제 등의 프로덕션 장애를 일으킨다. Context manager는 Python의 핵심 리소스 관리 패턴이며, 올바른 사용은 시스템 안정성의 기반이다.

**Step 2 — 핵심 기술 설명**

```python
# 1. 클래스 기반 context manager
class Timer:
    def __init__(self, name: str):
        self.name = name

    def __enter__(self):
        self.start = time.monotonic()
        return self  # with ... as timer 에서 반환

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.monotonic() - self.start
        logger.info(f"{self.name}: {duration:.3f}s")
        return False  # True를 반환하면 예외를 삼킴!

with Timer("db_query") as t:
    result = db.execute(query)
```

```python
# 2. contextlib 데코레이터 (간편)
from contextlib import contextmanager, asynccontextmanager

@contextmanager
def managed_resource(name: str):
    resource = acquire_resource(name)
    try:
        yield resource  # 여기서 일시 정지, with 본문 실행
    except Exception:
        resource.rollback()
        raise
    else:
        resource.commit()  # 예외 없을 때만
    finally:
        resource.release()  # 항상 실행

# async 버전
@asynccontextmanager
async def managed_db_session():
    session = AsyncSession(engine)
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
```

```python
# 3. ExitStack — 동적/가변 개수 리소스 관리
from contextlib import AsyncExitStack

async def process_batch(file_paths: list[str]):
    async with AsyncExitStack() as stack:
        # 가변 개수의 파일을 안전하게 열기
        files = []
        for path in file_paths:
            f = await stack.enter_async_context(aiofiles.open(path))
            files.append(f)

        # 모든 파일이 열린 상태에서 처리
        for f in files:
            data = await f.read()
            await process(data)

    # ExitStack이 모든 파일을 역순으로 닫음
```

```python
# 4. 분산 락 context manager
import redis.asyncio as aioredis

class DistributedLock:
    def __init__(
        self,
        redis: aioredis.Redis,
        key: str,
        timeout: float = 30.0,
        blocking_timeout: float = 10.0,
    ):
        self.redis = redis
        self.key = f"lock:{key}"
        self.timeout = timeout
        self.blocking_timeout = blocking_timeout
        self.lock_id = str(uuid.uuid4())

    async def __aenter__(self):
        end_time = time.monotonic() + self.blocking_timeout
        while time.monotonic() < end_time:
            acquired = await self.redis.set(
                self.key,
                self.lock_id,
                nx=True,            # SET IF NOT EXISTS
                ex=int(self.timeout),  # 자동 만료
            )
            if acquired:
                return self
            await asyncio.sleep(0.1)
        raise TimeoutError(f"Could not acquire lock: {self.key}")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Lua 스크립트로 원자적 해제 (자신의 락만 해제)
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        await self.redis.eval(script, 1, self.key, self.lock_id)
        return False

# 사용
async def update_inventory(product_id: int, delta: int):
    async with DistributedLock(redis, f"inventory:{product_id}"):
        current = await get_inventory(product_id)
        await set_inventory(product_id, current + delta)
```

**Step 3 — __exit__의 에러 처리 심화**

```python
# __exit__의 반환값 의미
class SuppressErrors:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is ValueError:
            logger.warning(f"Suppressed: {exc_val}")
            return True   # 예외 삼킴! with 블록 밖에서 예외 안 보임
        return False      # 다른 예외는 전파

# ⚠️ 주의: __exit__에서 새 예외 발생 시
class DangerousResource:
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()  # 여기서 예외 발생하면?
        # 원래 예외(exc_val)가 새 예외로 대체됨!
        # 원래 에러 정보 유실!

# 안전한 패턴:
class SafeResource:
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.close()
        except Exception:
            if exc_type is None:
                raise  # with 블록 자체가 정상이면 close 예외 전파
            # with 블록에서 예외 발생했으면 close 예외는 로깅만
            logger.error("Error during cleanup", exc_info=True)
        return False
```

**Step 4 — 고급 패턴**

```python
# 재진입 가능한 context manager
from contextlib import contextmanager

class ReentrantLock:
    """같은 코루틴에서 여러 번 진입 가능한 락"""
    def __init__(self):
        self._lock = asyncio.Lock()
        self._owner: int | None = None
        self._count = 0

    async def __aenter__(self):
        task_id = id(asyncio.current_task())
        if self._owner == task_id:
            self._count += 1
            return self
        await self._lock.acquire()
        self._owner = task_id
        self._count = 1
        return self

    async def __aexit__(self, *exc):
        self._count -= 1
        if self._count == 0:
            self._owner = None
            self._lock.release()
        return False

# Context manager로 트랜잭션 범위 제어
@asynccontextmanager
async def transaction(session: AsyncSession):
    """명시적 트랜잭션 경계"""
    if session.in_transaction():
        # 이미 트랜잭션 내 → savepoint
        async with session.begin_nested():
            yield session
    else:
        # 새 트랜잭션
        async with session.begin():
            yield session
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| `__enter__/__exit__` | 완전 제어, 재사용 | 보일러플레이트 | 복잡한 리소스 |
| `@contextmanager` | 간결, Pythonic | 재사용 어려움 | 간단한 setup/teardown |
| `ExitStack` | 동적 리소스 관리 | 복잡도 | 가변 개수 리소스 |
| try/finally | 명시적 | 누락 위험 | 사용하지 않는 것을 권장 |

**Step 6 — 성장 & 심화 학습**
- `contextlib.suppress()` — 특정 예외 무시
- `contextlib.redirect_stdout/stderr` — 출력 리다이렉션
- `contextlib.nullcontext()` — 조건부 context manager (3.7+)
- PEP 343 — `with` 문의 역사와 설계 결정

**🎯 면접관 평가 기준:**
- L6 PASS: `__enter__/__exit__` 동작. `@contextmanager` 패턴. async context manager.
- L7 EXCEED: `__exit__` 반환값 의미와 에러 처리 전략. ExitStack 활용. 분산 락 context manager 구현. 재진입 가능 패턴.
- 🚩 RED FLAG: try/finally 대신 context manager를 쓰는 이유 모름. `__exit__`에서 예외 삼키는 위험 인지 못함.

---

## Appendix: 추가 심화 문제 (Bonus)

### Q26: FastAPI에서 request/response 스트리밍과 대용량 파일 처리

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: FastAPI Internals & Production

**Question:**
"FastAPI에서 수 GB 크기의 파일 업로드/다운로드를 메모리 효율적으로 처리하는 방법을 설명하세요. `StreamingResponse`, `UploadFile`의 내부 동작, SSE(Server-Sent Events), 그리고 WebSocket과 HTTP 스트리밍의 선택 기준을 논하세요."

---

**🧒 12살 비유:**
큰 물통(파일)을 옮길 때 한 번에 들면(메모리에 전부 로드) 너무 무거워. 대신 호스로 물을 흘려보내면(스트리밍) 조금씩 계속 보낼 수 있어. StreamingResponse는 수도꼭지야 — 물이 나오는 대로 바로 보내. SSE는 라디오 방송이야 — 서버가 일방적으로 계속 송출. WebSocket은 전화통화야 — 양쪽 다 말할 수 있어.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
대용량 데이터 처리는 메모리 관리의 실전 테스트다. Staff 엔지니어는 스트리밍 패턴으로 상수 메모리 사용을 유지하면서 대용량 I/O를 처리할 수 있어야 한다.

**Step 2 — 핵심 기술 설명**

```python
from fastapi import UploadFile, File
from fastapi.responses import StreamingResponse
import aiofiles

# 대용량 업로드: 청크 단위 읽기
@app.post("/upload")
async def upload_large_file(file: UploadFile = File(...)):
    # UploadFile 내부:
    # - 작은 파일 (< 1MB): SpooledTemporaryFile (메모리)
    # - 큰 파일 (>= 1MB): 디스크의 임시 파일
    # .read()는 전체를 메모리에 올림 → 대용량 시 OOM!

    total_size = 0
    hash_obj = hashlib.sha256()

    # ✅ 청크 단위 처리 — 상수 메모리
    async with aiofiles.open(f"/data/{file.filename}", "wb") as f:
        while chunk := await file.read(1024 * 1024):  # 1MB 청크
            await f.write(chunk)
            hash_obj.update(chunk)
            total_size += len(chunk)

    return {
        "filename": file.filename,
        "size": total_size,
        "sha256": hash_obj.hexdigest(),
    }

# 대용량 다운로드: StreamingResponse
@app.get("/download/{file_id}")
async def download_file(file_id: str):
    file_path = f"/data/{file_id}"

    async def file_streamer():
        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(1024 * 1024):
                yield chunk

    return StreamingResponse(
        file_streamer(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={file_id}",
        },
    )
```

```python
# SSE (Server-Sent Events) — 서버 → 클라이언트 단방향 스트리밍
from sse_starlette.sse import EventSourceResponse

@app.get("/events/stream")
async def event_stream(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            # 이벤트 생성
            data = await get_latest_events()
            if data:
                yield {
                    "event": "update",
                    "data": json.dumps(data),
                    "id": str(uuid.uuid4()),
                    "retry": 5000,  # 재연결 대기 (ms)
                }
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())

# ⚠️ BaseHTTPMiddleware와 SSE 충돌 주의!
# BaseHTTPMiddleware가 response body를 버퍼링 → stream 깨짐
# 해결: Pure ASGI middleware 사용 또는 SSE 경로 미들웨어 제외
```

**Step 3 — HTTP 스트리밍 vs WebSocket vs SSE**

| 기준 | StreamingResponse | SSE | WebSocket |
|------|------------------|-----|-----------|
| 방향 | 서버→클라이언트 | 서버→클라이언트 | 양방향 |
| 프로토콜 | HTTP/1.1 | HTTP/1.1 | WS (upgrade) |
| 재연결 | 수동 | 자동 (브라우저 내장) | 수동 |
| 바이너리 | 지원 | 텍스트만 | 지원 |
| 로드밸런서 호환 | 좋음 | 좋음 | 설정 필요 |
| 사용 예 | 파일 다운로드 | 실시간 알림, LLM 출력 | 채팅, 게임 |

**Step 4 — 프로덕션 패턴: LLM 스트리밍 응답**

```python
# AI/LLM 서비스에서 흔한 패턴: 토큰 단위 SSE 스트리밍
@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        async for token in llm_client.stream(request.prompt):
            yield {
                "event": "token",
                "data": json.dumps({"token": token}),
            }
        yield {
            "event": "done",
            "data": json.dumps({"usage": {"tokens": total_tokens}}),
        }

    return EventSourceResponse(generate())
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| UploadFile (chunked) | 간단, 표준 | 단일 파일 | 일반 업로드 |
| Multipart + background | 즉시 응답 | 복잡도 | 대용량 비동기 처리 |
| Pre-signed URL (S3) | 서버 부하 없음 | AWS 종속 | 대용량 클라우드 |
| tus 프로토콜 | 이어받기 지원 | 구현 복잡 | 불안정한 네트워크 |

**Step 6 — 성장 & 심화 학습**
- HTTP/2 Server Push vs SSE — 성능 차이
- `aiohttp` WebSocket vs FastAPI WebSocket — 성능 비교
- Chunked Transfer Encoding 내부 동작
- gRPC streaming vs HTTP streaming — 바이너리 효율성

**🎯 면접관 평가 기준:**
- L6 PASS: StreamingResponse 사용. 청크 단위 파일 처리. SSE 기본 구현.
- L7 EXCEED: BaseHTTPMiddleware + streaming 충돌 인지. 상수 메모리 처리 설계. LLM 스트리밍 패턴. tus/pre-signed URL 활용.
- 🚩 RED FLAG: `await file.read()`로 전체 파일 메모리 로드. streaming 필요성 인지 못함.

---

### Q27: SQLAlchemy 2.0의 새로운 쿼리 스타일과 마이그레이션

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: SQLAlchemy Session & ORM

**Question:**
"SQLAlchemy 1.x에서 2.0으로의 주요 변경점을 설명하세요. `select()` 기반 새 쿼리 API, `Session.execute()` vs 레거시 `Query`, `Mapped` 타입 annotation, 그리고 대규모 코드베이스 마이그레이션 전략을 논하세요."

---

**🧒 12살 비유:**
게임이 버전 업그레이드됐어. 옛날 방식(1.x)은 `session.query(User).filter(User.name == "Alice")` — "검색 도우미한테 말로 시켜". 새 방식(2.0)은 `select(User).where(User.name == "Alice")` — "검색 명령서를 직접 써서 제출해". 새 방식이 async와 더 잘 맞고, 타입 체커도 더 정확하게 도와줄 수 있어.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
SQLAlchemy 2.0은 패러다임 전환이다. 기존 코드베이스 마이그레이션은 Staff 엔지니어의 핵심 역할이며, 새 API의 설계 의도를 이해해야 올바른 결정을 내릴 수 있다.

**Step 2 — 핵심 기술 설명**

```python
# 1.x 스타일 (레거시) vs 2.0 스타일

# --- 기본 조회 ---
# 1.x
users = session.query(User).filter(User.age > 18).all()

# 2.0
stmt = select(User).where(User.age > 18)
result = session.execute(stmt)
users = result.scalars().all()

# --- 조인 ---
# 1.x
orders = (
    session.query(Order)
    .join(User)
    .filter(User.name == "Alice")
    .all()
)

# 2.0
stmt = (
    select(Order)
    .join(User)
    .where(User.name == "Alice")
)
orders = session.execute(stmt).scalars().all()

# --- 집계 ---
# 1.x
count = session.query(func.count(User.id)).scalar()

# 2.0
stmt = select(func.count(User.id))
count = session.execute(stmt).scalar_one()

# --- UPDATE/DELETE ---
# 1.x
session.query(User).filter(User.age < 18).update({"active": False})

# 2.0
stmt = update(User).where(User.age < 18).values(active=False)
session.execute(stmt)
```

```python
# Mapped annotation (2.0 declarative)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

# 1.x 스타일
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    orders = relationship("Order", back_populates="user")

# 2.0 스타일 — 타입 힌트 통합
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None]  # nullable
    orders: Mapped[list["Order"]] = relationship(back_populates="user")

# 장점:
# 1. mypy/pyright가 타입 추론 가능
# 2. nullable이 타입 annotation으로 결정 (Mapped[str] = NOT NULL)
# 3. IDE 자동완성 정확
```

**Step 3 — 마이그레이션 전략**

```python
# 단계적 마이그레이션 (대규모 코드베이스)

# Phase 1: 2.0 호환 모드 활성화
from sqlalchemy import create_engine
engine = create_engine(
    "postgresql://...",
    future=True,  # 2.0 스타일 강제
)

# 1.x 코드에서 deprecation warning 확인
import warnings
warnings.filterwarnings("error", category=DeprecationWarning)
# → 1.x 전용 API 사용 시 에러 발생

# Phase 2: 모델을 Mapped 스타일로 변환
# 자동화 도구: sqlalchemy2-stubs의 마이그레이션 스크립트

# Phase 3: 쿼리를 select() 스타일로 변환
# session.query(User) → select(User)
# .filter() → .where()
# .all() → .scalars().all()

# Phase 4: async 전환 (선택)
# create_engine → create_async_engine
# Session → AsyncSession
# session.execute → await session.execute
```

**Step 4 — 2.0의 설계 의도**

```python
# 왜 select() 스타일로 바뀌었나?

# 1. SQL Core와 ORM 통합
# 1.x: session.query (ORM 전용) vs select (Core 전용)
# 2.0: select 하나로 통합 → Core/ORM 경계 제거

# 2. Async 호환
# session.query().all()은 내부적으로 동기 I/O
# session.execute(select(...))는 await 가능

# 3. 타입 안전성
# select(User).where(User.name == 123) → mypy가 타입 에러 감지
# session.query(User).filter(User.name == 123) → mypy 미지원

# 4. Result 객체의 유연성
result = session.execute(select(User.name, User.email))
# result.all() → list[Row]
# result.scalars().all() → list[str] (첫 번째 컬럼만)
# result.mappings().all() → list[dict]
# result.one() → Row (정확히 1개 아니면 에러)
# result.first() → Row | None
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| 점진적 마이그레이션 | 안전, 기존 코드 유지 | 두 스타일 공존 | 대규모 코드베이스 |
| 일괄 마이그레이션 | 깔끔, 일관성 | 리스크, 큰 PR | 소규모 코드베이스 |
| 새 코드만 2.0 | 기존 코드 안 건드림 | 불일치 | 보수적 전략 |
| 자동 변환 도구 | 빠름 | 복잡한 쿼리 누락 | 초기 변환 보조 |

**Step 6 — 성장 & 심화 학습**
- SQLAlchemy 2.0 Migration Guide — 공식 문서
- `sqlalchemy2-stubs` → 내장 타입 지원 (2.0에서 별도 stubs 불필요)
- `Result` 객체의 내부 — `CursorResult`, `MappingResult`, `ScalarResult`
- Alembic과 2.0 Mapped의 자동 마이그레이션 생성

**🎯 면접관 평가 기준:**
- L6 PASS: select() vs query() 차이. Mapped annotation 사용. 기본적 마이그레이션 인지.
- L7 EXCEED: 설계 의도(Core/ORM 통합, async 호환). Result 객체 활용. 대규모 마이그레이션 전략 수립.
- 🚩 RED FLAG: 1.x와 2.0 차이 모름. async에서 session.query 사용.

---

### Q28: Python 서비스의 Graceful Shutdown과 Zero-Downtime Deploy

> 난이도: ⭐⭐⭐⭐⭐ (L6/L7) | 카테고리: Production Debugging

**Question:**
"FastAPI/uvicorn 서비스의 graceful shutdown 메커니즘을 설명하세요. SIGTERM 처리, 진행 중 요청 완료, 커넥션 풀 드레이닝, 그리고 Kubernetes 환경에서 zero-downtime 배포를 구현하는 전체 과정을 논하세요."

---

**🧒 12살 비유:**
가게 문 닫을 때를 생각해봐. "즉시 폐점"(SIGKILL)은 손님이 계산하고 있어도 불 꺼버리는 거야. "graceful 폐점"(SIGTERM)은 "새 손님은 안 받고, 안에 있는 손님 다 계산할 때까지 기다린 후" 문 닫는 거야. Kubernetes에서는 옆에 새 가게(새 Pod)를 먼저 열고, 손님이 다 새 가게로 가면 구 가게를 닫아.

**📋 단계별 답변:**

**Step 1 — 맥락: 왜 이 질문을 하는가**
Zero-downtime 배포는 프로덕션 서비스의 기본 요구사항이다. Graceful shutdown을 잘못 구현하면 요청 유실, 데이터 손상, 커넥션 릭이 발생한다. Staff 엔지니어는 OS 시그널부터 K8s lifecycle hook까지 전체 체인을 이해해야 한다.

**Step 2 — 핵심 기술 설명**

```python
# Uvicorn의 Graceful Shutdown 시퀀스
# 1. SIGTERM 수신
# 2. 새 연결 수락 중단
# 3. 기존 연결의 요청 완료 대기
# 4. timeout 후 강제 종료

# uvicorn 설정
# uvicorn app:app \
#   --timeout-graceful-shutdown 30 \  # 30초 대기
#   --timeout-keep-alive 5             # keep-alive 타임아웃

# FastAPI lifespan에서 정리 작업
from contextlib import asynccontextmanager
import signal

@asynccontextmanager
async def lifespan(app: FastAPI):
    # === Startup ===
    logger.info("Starting up")

    # DB 엔진
    app.state.engine = create_async_engine(DB_URL)

    # 백그라운드 작업
    app.state.bg_tasks = set()
    app.state.shutting_down = False

    yield

    # === Shutdown ===
    logger.info("Shutting down gracefully")
    app.state.shutting_down = True

    # 1. 백그라운드 태스크 완료 대기
    if app.state.bg_tasks:
        logger.info(f"Waiting for {len(app.state.bg_tasks)} background tasks")
        await asyncio.gather(*app.state.bg_tasks, return_exceptions=True)

    # 2. DB 커넥션 풀 드레인
    await app.state.engine.dispose()
    logger.info("All connections closed")

    # 3. 외부 서비스 연결 종료
    # await http_client.aclose()
    # await redis_pool.close()

app = FastAPI(lifespan=lifespan)

# 셧다운 중 새 작업 거부
@app.middleware("http")
async def shutdown_guard(request, call_next):
    if request.app.state.shutting_down:
        return JSONResponse(
            status_code=503,
            content={"detail": "Service shutting down"},
            headers={"Retry-After": "5"},
        )
    return await call_next(request)
```

```yaml
# Kubernetes zero-downtime 배포 설정
apiVersion: apps/v1
kind: Deployment
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # 추가 Pod 1개 허용
      maxUnavailable: 0  # 항상 최소 replicas 유지
  template:
    spec:
      terminationGracePeriodSeconds: 45  # SIGTERM → SIGKILL 대기
      containers:
      - name: api
        ports:
        - containerPort: 8000

        # Readiness: 트래픽 수신 가능 여부
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          failureThreshold: 3

        # Liveness: 컨테이너 정상 여부
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 10

        # PreStop hook: SIGTERM 전에 실행
        lifecycle:
          preStop:
            exec:
              command: ["sleep", "10"]
              # 왜 sleep?
              # K8s가 Service endpoint에서 Pod를 제거하는 것과
              # SIGTERM을 보내는 것이 동시에 발생
              # sleep으로 endpoint 제거가 전파될 시간을 줌
              # → 이미 라우팅된 요청이 완료될 수 있음
```

```python
# Health check 엔드포인트
@app.get("/health/live")
async def liveness():
    """프로세스가 살아있는가? (hang 감지용)"""
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness():
    """트래픽을 받을 준비가 되었는가?"""
    # DB 연결 확인
    try:
        async with app.state.engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "reason": "db unavailable"},
        )

    # 셧다운 중이면 not ready
    if app.state.shutting_down:
        return JSONResponse(
            status_code=503,
            content={"status": "shutting down"},
        )

    return {"status": "ready"}
```

**Step 3 — Zero-Downtime 배포 시퀀스**

```
┌─────────────────────────────────────────────────────────────┐
│                 Rolling Update Sequence                       │
│                                                             │
│  1. 새 Pod 생성 (v2)                                        │
│  2. readinessProbe 통과 대기                                 │
│  3. Service endpoint에 v2 Pod 추가                           │
│  4. 구 Pod (v1)에서 endpoint 제거 시작                       │
│  5. preStop hook 실행 (sleep 10)                             │
│     → endpoint 제거가 모든 kube-proxy/ingress에 전파됨        │
│  6. SIGTERM 전송                                             │
│  7. uvicorn이 새 연결 중단 + 기존 요청 완료 대기              │
│  8. terminationGracePeriodSeconds 경과 시 SIGKILL            │
│                                                             │
│  Timeline:                                                   │
│  [preStop 10s][graceful shutdown 30s][SIGKILL]               │
│  [           terminationGracePeriod 45s        ]             │
└─────────────────────────────────────────────────────────────┘
```

**Step 4 — 흔한 실수와 해결**

```python
# 실수 1: preStop hook 없음
# → SIGTERM과 endpoint 제거가 동시에 발생
# → 이미 라우팅된 요청이 SIGTERM 중인 Pod로 도착
# → 503 에러

# 실수 2: terminationGracePeriodSeconds < preStop + graceful shutdown
# → graceful shutdown 완료 전에 SIGKILL
# → 요청 유실

# 실수 3: readinessProbe가 너무 빠름
# → 앱이 준비 안 된 상태에서 트래픽 수신
# initialDelaySeconds를 충분히 설정

# 실수 4: 커넥션 풀 드레인 안 함
# → 셧다운 시 "connection reset by peer" 에러
# → engine.dispose() 필수
```

**Step 5 — 트레이드오프 & 대안**

| 접근법 | 장점 | 단점 | 사용 시점 |
|--------|------|------|-----------|
| Rolling Update | 간단, 기본 전략 | 배포 중 두 버전 공존 | 대부분의 서비스 |
| Blue-Green | 즉시 전환, 롤백 쉬움 | 2배 리소스 | 중요 서비스, DB 마이그레이션 없을 때 |
| Canary | 점진적 검증 | 복잡한 라우팅 | 대규모 사용자 서비스 |
| Recreate | 단순 | 다운타임 존재 | 개발/스테이징 |

**Step 6 — 성장 & 심화 학습**
- K8s Pod lifecycle — `Running`, `Terminating` 상태 전이
- Envoy/NGINX draining — L7 로드밸런서의 graceful shutdown
- `uvicorn.Server.shutdown()` 내부 구현
- `gunicorn --graceful-timeout` — 다중 워커 환경의 graceful shutdown

**🎯 면접관 평가 기준:**
- L6 PASS: SIGTERM 처리. lifespan shutdown. health check 엔드포인트. K8s rolling update 기본.
- L7 EXCEED: preStop hook + endpoint 제거 race condition 이해. terminationGracePeriodSeconds 계산. 커넥션 풀 드레이닝. Blue-Green/Canary 전략 비교.
- 🚩 RED FLAG: graceful shutdown 고려 안 함. K8s에서 SIGKILL에 의존. health check 없음.
