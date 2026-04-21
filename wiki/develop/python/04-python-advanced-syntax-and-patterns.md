---
created: 2026-04-21
source: claude-code
tags: [python, advanced, decorator, metaclass, async, concurrency, typing, protocol, metaprogramming]
---

# 📖 Python 고급 문법과 패턴 — 프로덕션 수준의 Python

> 💡 **한줄 요약**: Python의 고급 문법은 데코레이터/메타클래스/디스크립터로 코드를 "프로그래밍하는 코드"를 작성할 수 있게 하며, async/await + Protocol 타입 시스템으로 프로덕션 수준의 동시성과 타입 안전성을 구현한다.
>
> 📌 **핵심 키워드**: Decorator, Metaclass, async/await, Protocol, ParamSpec, contextlib
> 📅 **기준**: Python 3.14 (2025.10)

---

## 1️⃣ 데코레이터 Deep Dive

### 함수 데코레이터

```python
import functools

def retry(max_attempts: int = 3):
    """데코레이터 팩토리: 실패 시 재시도"""
    def decorator(func):
        @functools.wraps(func)  # 원본 함수 메타데이터 보존
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(2 ** attempt)
        return wrapper
    return decorator

@retry(max_attempts=5)
def fetch_data(url: str) -> dict:
    ...
```

### 클래스 데코레이터

```python
def singleton(cls):
    """클래스를 싱글턴으로 만드는 데코레이터"""
    instances = {}
    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class Database:
    def __init__(self, url: str):
        self.connection = connect(url)
```

### 데코레이터 스태킹

```python
@app.route("/users")      # 3번째 적용
@require_auth              # 2번째 적용
@validate_input            # 1번째 적용 (가장 안쪽)
def get_users():
    ...
# 실행 순서: validate_input → require_auth → route
```

### 🔄 4개 언어 대응 패턴

| Python | Go | Kotlin | JS/TS |
|--------|-----|--------|-------|
| `@decorator` | 미들웨어 패턴 / 함수 래핑 | `@annotation` (AOP) | Stage 3 Decorators |
| `@retry` | retry 미들웨어 | Spring `@Retryable` | decorator (TC39) |
| `@app.route` | `http.HandleFunc` | `@GetMapping` | `@Controller` (Nest.js) |

---

## 2️⃣ 메타클래스와 디스크립터

### Descriptor Protocol

```python
class Validated:
    """값 검증 디스크립터"""
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        return getattr(obj, f"_{self.name}", None)
    
    def __set__(self, obj, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"{self.name}은 양의 정수여야 합니다")
        setattr(obj, f"_{self.name}", value)

class Order:
    quantity = Validated()  # 디스크립터 인스턴스
    price = Validated()

o = Order()
o.quantity = 10   # OK
o.quantity = -1   # ValueError!
```

이것이 `@property`, `@classmethod`, `@staticmethod`가 작동하는 원리다.

### Metaclass 기초

```python
class Meta(type):
    def __new__(mcs, name, bases, namespace):
        # 클래스 생성 시점에 개입
        for key, value in namespace.items():
            if callable(value) and not key.startswith("_"):
                namespace[key] = some_wrapper(value)
        return super().__new__(mcs, name, bases, namespace)

class MyClass(metaclass=Meta):
    ...
```

> ⚠️ **실무 조언**: 메타클래스는 **프레임워크 개발자**가 주로 사용. 일반 코드에서는 `__init_subclass__` (3.6+)이나 데코레이터로 충분.

> 📌 면접 심화: [[python-fastapi-sqlalchemy]] Q6 (메타프로그래밍)

---

## 3️⃣ Async/Await와 asyncio

### 기본 패턴

```python
import asyncio

async def fetch_user(user_id: int) -> User:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"/users/{user_id}") as resp:
            return User(**(await resp.json()))

async def main():
    # 병렬 실행
    users = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3),
    )
```

### TaskGroup (3.11+)

```python
async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_user(1))
        task2 = tg.create_task(fetch_user(2))
    # 모든 task 완료 보장, 하나라도 실패하면 나머지 취소
    print(task1.result(), task2.result())
```

### Async Iterator / Async Context Manager

```python
# Async Iterator
async for message in websocket:
    await process(message)

# Async Context Manager
async with aiofiles.open("data.txt") as f:
    content = await f.read()
```

### 🧒 12살 비유

> `async/await`는 "레스토랑 주문"과 같아. 주문(비동기 호출)을 넣고 기다리는 동안 다른 테이블 주문도 받을 수 있어(동시성). 하지만 요리사는 한 명이야(GIL) — 요리(CPU 작업)는 한 번에 하나만 가능하고, 서빙(I/O 대기)은 동시에 여러 개 처리 가능해.

### 🔄 4개 언어 비교

| 개념 | Python (asyncio) | Go (goroutine) | Kotlin (coroutine) | JS (Promise) |
|------|-----------------|----------------|-------------------|-------------|
| 비동기 함수 | `async def` | `go func()` | `suspend fun` | `async function` |
| 대기 | `await` | 채널 수신 `<-ch` | `await()` | `await` |
| 병렬 실행 | `gather()` / `TaskGroup` | 여러 goroutine | `coroutineScope` | `Promise.all()` |
| 스케줄러 | 이벤트 루프 | GMP 스케줄러 | Dispatcher | 이벤트 루프 |
| 진정한 병렬 | ❌ (GIL) | ✅ | ✅ | ❌ |

> 📌 동시성 모델 비교 상세: [[coroutine-gmp-vthread]]

---

## 4️⃣ 동시성 패턴

### threading vs multiprocessing vs asyncio

```
┌────────────────────────────────────────────────────┐
│           Python 동시성 선택 가이드                   │
│                                                      │
│  I/O bound?                                          │
│  ├── Yes → asyncio (가장 효율적)                     │
│  │         또는 threading (레거시 코드)               │
│  │                                                   │
│  └── No (CPU bound?)                                 │
│       ├── Yes → multiprocessing                      │
│       │         또는 C 확장 (Cython, Rust binding)   │
│       │         또는 free-threaded 3.14+             │
│       └── No → 동시성 불필요                          │
└────────────────────────────────────────────────────┘
```

| 방식 | GIL 영향 | 메모리 공유 | 적합한 작업 |
|------|---------|-----------|-----------|
| `asyncio` | 단일 스레드 (GIL 무관) | ✅ | 네트워크 I/O, 웹 서버 |
| `threading` | GIL 제한 | ✅ | I/O 대기, 레거시 |
| `multiprocessing` | GIL 없음 (별도 프로세스) | ❌ (IPC 필요) | CPU 집약 계산 |
| `concurrent.futures` | 위 3가지의 통합 인터페이스 | - | 범용 |

### concurrent.futures

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# I/O bound → ThreadPool
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(fetch_url, urls))

# CPU bound → ProcessPool
with ProcessPoolExecutor() as executor:
    results = list(executor.map(heavy_compute, data))
```

---

## 5️⃣ 고급 타입 시스템

### Protocol (구조적 서브타이핑, PEP 544)

```python
from typing import Protocol

class Readable(Protocol):
    def read(self) -> str: ...

def process(source: Readable) -> str:
    return source.read()

# 명시적 구현 없이도 — read()가 있으면 Readable
class MyFile:
    def read(self) -> str:
        return "data"

process(MyFile())  # ✅ mypy 통과 — Go의 구조적 타이핑과 동일!
```

### TypeVar / ParamSpec / Generic

```python
from typing import TypeVar, Generic

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> T:
        return self._items.pop()

# ParamSpec (3.10+): 데코레이터의 파라미터 타입 보존
from typing import ParamSpec, Callable

P = ParamSpec("P")
R = TypeVar("R")

def logged(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

### TypeGuard / TypeIs

```python
from typing import TypeGuard

def is_str_list(val: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)

def process(items: list[object]):
    if is_str_list(items):
        # 이 블록에서 items는 list[str]로 좁혀짐 (narrowing)
        print(items[0].upper())
```

### 🔄 4개 언어 비교

| 개념 | Python | Go | Kotlin | JS/TS |
|------|--------|-----|--------|-------|
| 구조적 타이핑 | `Protocol` | interface (기본) | ❌ (명목적) | interface (TS) |
| 제네릭 | `Generic[T]` | `[T any]` (1.18+) | `<T>` | `<T>` (TS) |
| 타입 좁히기 | `TypeGuard` | type assertion | smart cast | type guard (TS) |
| 유틸리티 타입 | 제한적 | 없음 | 없음 | `Partial`, `Pick`, `Omit` |

---

## 6️⃣ Context Manager 고급

### contextlib

```python
from contextlib import contextmanager, asynccontextmanager

@contextmanager
def managed_db():
    db = connect()
    try:
        yield db
    finally:
        db.close()

with managed_db() as db:
    db.query(...)

# Async 버전
@asynccontextmanager
async def managed_session():
    session = await create_session()
    try:
        yield session
    finally:
        await session.close()
```

### suppress / ExitStack

```python
from contextlib import suppress, ExitStack

# 특정 예외 무시
with suppress(FileNotFoundError):
    os.remove("temp.txt")

# 동적으로 여러 context manager
with ExitStack() as stack:
    files = [stack.enter_context(open(f)) for f in filenames]
    # 모든 파일이 자동으로 닫힘
```

---

## 7️⃣ 함수형 패턴

### itertools

```python
from itertools import chain, groupby, islice, product

# chain: 여러 이터러블 연결
all_items = chain(list1, list2, list3)

# groupby: 그룹화
for key, group in groupby(sorted(users, key=lambda u: u.dept), key=lambda u: u.dept):
    print(f"{key}: {list(group)}")

# islice: 지연 슬라이싱
first_10 = islice(huge_iterator, 10)
```

### functools

```python
from functools import lru_cache, partial, reduce

# lru_cache: 메모이제이션
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2: return n
    return fibonacci(n-1) + fibonacci(n-2)

# partial: 부분 적용
double = partial(multiply, factor=2)

# reduce: 누적 연산
total = reduce(lambda acc, x: acc + x, numbers, 0)
```

---

## 8️⃣ 메타프로그래밍

### `__init_subclass__` (3.6+)

```python
class Plugin:
    _registry: dict[str, type] = {}
    
    def __init_subclass__(cls, name: str = "", **kwargs):
        super().__init_subclass__(**kwargs)
        if name:
            Plugin._registry[name] = cls

class JSONPlugin(Plugin, name="json"):
    ...

class XMLPlugin(Plugin, name="xml"):
    ...

# Plugin._registry = {"json": JSONPlugin, "xml": XMLPlugin}
```

### `__set_name__` (3.6+)

```python
class Field:
    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"
    
    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name, None)
    
    def __set__(self, obj, value):
        setattr(obj, self.private_name, value)
```

> 📌 면접 심화: [[python-fastapi-sqlalchemy]] Q6 (디스크립터, 메타클래스)

---

## 📎 출처

1. [Python Descriptor HowTo Guide](https://docs.python.org/3/howto/descriptor.html) — 디스크립터 공식 가이드
2. [PEP 544 – Protocols: Structural subtyping](https://peps.python.org/pep-0544/) — Protocol
3. [PEP 612 – Parameter Specification Variables](https://peps.python.org/pep-0612/) — ParamSpec
4. [asyncio Documentation](https://docs.python.org/3/library/asyncio.html) — async/await 공식 문서
5. [contextlib Documentation](https://docs.python.org/3/library/contextlib.html) — Context Manager

---

> 📌 **이전 문서**: [[03-python-basic-syntax]] — Python 기본 문법
> 📌 **다음 문서**: [[05-python-developer-essentials-by-seniority]] — Python 개발자 필수 지식
> 📌 **관련 문서**: [[python-fastapi-sqlalchemy]] (Q1 GIL, Q2 async, Q6 메타프로그래밍), [[coroutine-gmp-vthread]]
