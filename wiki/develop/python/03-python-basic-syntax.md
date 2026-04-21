---
created: 2026-04-21
source: claude-code
tags: [python, syntax, basics, type-hints, oop, comprehension, dataclass, error-handling]
---

# 📖 Python 기본 문법 — 가독성이 곧 문법

> 💡 **한줄 요약**: Python의 기본 문법은 들여쓰기 기반 블록, 동적 타입 + 선택적 타입힌트, 풍부한 내장 데이터 구조, 그리고 OOP와 함수형을 자연스럽게 조합하는 멀티패러다임 구조로 설계되어 있다.
>
> 📌 **핵심 키워드**: duck typing, type hints, dataclass, comprehension, context manager, dunder methods
> 📅 **기준**: Python 3.14 (2025.10)

---

## 1️⃣ 모듈과 패키지 시스템

### import 기본

```python
import os                          # 모듈 전체
from pathlib import Path           # 특정 이름만
from typing import Optional, List  # 타입힌트
import numpy as np                 # 별칭
```

### 패키지 구조

```
myproject/
├── pyproject.toml      ← 프로젝트 메타데이터 + 의존성
├── src/
│   └── mypackage/
│       ├── __init__.py  ← 패키지 표시 (빈 파일도 OK)
│       ├── core.py
│       └── utils.py
└── tests/
    └── test_core.py
```

### `__all__`과 가시성

```python
# mypackage/__init__.py
__all__ = ["User", "create_user"]  # from mypackage import * 제어

# 관습: _접두사 = private (강제 아님)
def _internal_helper():
    pass
```

### 🔄 4개 언어 비교

| 개념 | Python | Go | Kotlin | JS/TS |
|------|--------|-----|--------|-------|
| 모듈 선언 | `pyproject.toml` | `go.mod` | `build.gradle.kts` | `package.json` |
| 가시성 | `_` 관습 (강제 아님) | 대문자/소문자 (컴파일러) | `public/private` | `export` |
| 미사용 import | 경고 (무시 가능) | **컴파일 에러** | 경고 | lint 경고 |

---

## 2️⃣ 변수, 타입, 타입 힌트

### 동적 타입

```python
x = 42          # int — 타입 선언 불필요
x = "hello"     # str — 같은 변수에 다른 타입 할당 가능
x = [1, 2, 3]   # list
```

### 기본 타입

| 타입 | 예시 | 특징 |
|------|------|------|
| `int` | `42`, `0xff`, `1_000_000` | 무한 정밀도 (!) |
| `float` | `3.14` | 64비트 IEEE 754 |
| `str` | `"hello"`, `f"name={n}"` | 불변, 유니코드 |
| `bool` | `True`, `False` | int의 서브클래스 |
| `None` | `None` | 부재값 (Go의 nil) |
| `bytes` | `b"hello"` | 바이트 시퀀스 |

### Type Hints (PEP 484+)

```python
# 기본 타입힌트
def greet(name: str) -> str:
    return f"Hello, {name}"

# 컬렉션
def process(items: list[int]) -> dict[str, int]:  # 3.9+
    return {str(i): i for i in items}

# Optional
def find_user(id: int) -> User | None:  # 3.10+
    ...
```

**타입힌트는 런타임에 강제되지 않는다** — mypy/pyright 같은 정적 분석 도구가 검사.

### 🧒 12살 비유

> Python의 타입 시스템은 "이름표는 붙이지만, 검사는 선택"이야. Go는 "반드시 이름표를 확인하고 입장"(컴파일러 강제), TypeScript는 "이름표를 확인하지만 문 앞에서만"(컴파일 후 제거), Python은 "이름표를 붙일 수 있지만, 안 붙여도 입장 가능"(선택적).

### 🔄 4개 언어 비교

| 개념 | Python | Go | Kotlin | JS/TS |
|------|--------|-----|--------|-------|
| 타입 시스템 | 동적 + 선택적 힌트 | 정적 | 정적 | 동적 (JS) / 정적 (TS) |
| Null 표현 | `None` | nil (zero value) | `null` (Nullable `?`) | `null`/`undefined` |
| 정수 크기 | **무한 정밀도** | 64bit | 64bit (JVM Long) | 64bit (Number) |
| 타입 변환 | `int()`, `str()` | `int64(x)` (명시적) | `.toInt()` | `Number()`, `String()` |

---

## 3️⃣ 제어 흐름

### if/elif/else

```python
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
else:
    grade = "C"

# 삼항 연산자
result = "짝수" if x % 2 == 0 else "홀수"
```

### for/while

```python
# for: 이터러블 순회
for item in [1, 2, 3]:
    print(item)

for i, v in enumerate(items):  # 인덱스 + 값
    print(i, v)

for k, v in mapping.items():   # dict 순회
    print(k, v)

# while
while condition:
    do_something()

# for-else (Python 고유!)
for item in items:
    if item.is_valid():
        break
else:
    # break 없이 루프가 끝나면 실행
    print("유효한 항목 없음")
```

### match/case (3.10+)

```python
match command:
    case "quit":
        sys.exit()
    case "greet" | "hello":
        print("안녕!")
    case {"action": "move", "x": x, "y": y}:
        move(x, y)  # 구조적 패턴 매칭!
    case _:
        print("알 수 없는 명령")
```

### Walrus Operator `:=` (3.8+)

```python
# 할당과 조건을 동시에
if (n := len(items)) > 10:
    print(f"항목이 {n}개로 너무 많습니다")

# while에서도 유용
while chunk := file.read(8192):
    process(chunk)
```

### 🔄 4개 언어 비교

| 개념 | Python | Go | Kotlin | JS/TS |
|------|--------|-----|--------|-------|
| 패턴 매칭 | `match/case` (3.10+) | `switch` | `when` (완전성 검사) | `switch` |
| 루프 종류 | `for`, `while` | `for`만 | `for`, `while`, `forEach` | `for`, `while`, `for...of` |
| for-else | ✅ (고유 기능) | ❌ | ❌ | ❌ |

---

## 4️⃣ 함수

### 기본 함수

```python
def add(a: int, b: int) -> int:
    return a + b
```

### *args / **kwargs

```python
def flexible(*args, **kwargs):
    print(args)    # (1, 2, 3) — 튜플
    print(kwargs)  # {"name": "Go"} — 딕셔너리

flexible(1, 2, 3, name="Go")
```

### 데코레이터 기초

```python
def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__}: {time.time() - start:.3f}s")
        return result
    return wrapper

@timer  # process = timer(process)
def process(data):
    ...
```

### Lambda / 클로저

```python
# Lambda
square = lambda x: x ** 2
sorted(items, key=lambda x: x.name)

# 클로저
def counter():
    count = 0
    def increment():
        nonlocal count  # 외부 변수 수정
        count += 1
        return count
    return increment
```

### 🔄 4개 언어 비교

| 개념 | Python | Go | Kotlin | JS/TS |
|------|--------|-----|--------|-------|
| 가변 인자 | `*args`, `**kwargs` | `...int` | `vararg` | `...args` |
| 데코레이터 | `@decorator` | 없음 (미들웨어 패턴) | 없음 (어노테이션은 다름) | Stage 3 Decorators |
| 기본값 인자 | ✅ | ❌ | ✅ | ✅ |
| 이름 인자 | ✅ (`name=value`) | ❌ | ✅ | ❌ (객체로 대체) |

---

## 5️⃣ 데이터 구조

### list / tuple / dict / set

```python
# List — 가변 순서열
items = [1, 2, 3]
items.append(4)

# Tuple — 불변 순서열
point = (3, 4)

# Dict — 키-값 매핑 (3.7+에서 삽입 순서 보장)
user = {"name": "Go", "age": 15}

# Set — 중복 없는 집합
tags = {"python", "go", "kotlin"}
```

> 📌 Dict 내부 구조 상세: [[python-dict-key-ordering]]

### dataclass (3.7+)

```python
from dataclasses import dataclass, field

@dataclass
class User:
    name: str
    age: int
    tags: list[str] = field(default_factory=list)
    
    @property
    def is_adult(self) -> bool:
        return self.age >= 18

# 자동 생성: __init__, __repr__, __eq__
u = User("Go", 15)
print(u)  # User(name='Go', age=15, tags=[])
```

### Named Tuple

```python
from typing import NamedTuple

class Point(NamedTuple):
    x: float
    y: float

p = Point(3.0, 4.0)
print(p.x, p.y)       # 이름으로 접근
x, y = p              # 언패킹
```

### 🔄 4개 언어 비교

| 개념 | Python | Go | Kotlin | JS/TS |
|------|--------|-----|--------|-------|
| 가변 배열 | `list` | `[]T` (slice) | `MutableList` | `Array` |
| 불변 배열 | `tuple` | `[N]T` (array) | `List` | `ReadonlyArray` (TS) |
| 해시맵 | `dict` | `map[K]V` | `Map` | `Map` / `Object` |
| 데이터 클래스 | `@dataclass` | struct | `data class` | interface (TS) |

---

## 6️⃣ 클래스와 OOP

### 기본 클래스

```python
class Animal:
    def __init__(self, name: str):
        self.name = name
    
    def speak(self) -> str:
        raise NotImplementedError

class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name}: 멍멍"

class Cat(Animal):
    def speak(self) -> str:
        return f"{self.name}: 야옹"
```

### Dunder Methods (매직 메서드)

```python
class Vector:
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y
    
    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)
    
    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"
    
    def __len__(self) -> int:
        return 2
```

| Dunder | 역할 | 호출 시점 |
|--------|------|---------|
| `__init__` | 초기화 | `obj = Class()` |
| `__repr__` | 문자열 표현 | `repr(obj)`, 디버깅 |
| `__str__` | 사용자 친화 문자열 | `str(obj)`, `print(obj)` |
| `__eq__` | 동등 비교 | `a == b` |
| `__hash__` | 해시값 | `hash(obj)`, dict 키 |
| `__len__` | 길이 | `len(obj)` |
| `__getitem__` | 인덱싱 | `obj[key]` |
| `__iter__` | 이터레이션 | `for x in obj` |

### MRO (Method Resolution Order)

```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass

print(D.__mro__)
# (D, B, C, A, object) — C3 Linearization
```

### 🔄 4개 언어 비교

| 개념 | Python | Go | Kotlin | JS/TS |
|------|--------|-----|--------|-------|
| 클래스 | ✅ class | ❌ struct + 메서드 | ✅ class | ✅ class |
| 상속 | 다중 상속 (MRO) | ❌ (임베딩으로 구성) | 단일 상속 + interface | 단일 상속 + mixin |
| 연산자 오버로딩 | ✅ dunder | ❌ | ✅ `operator fun` | ❌ (제한적) |

---

## 7️⃣ 에러 처리

### try / except / else / finally

```python
try:
    result = risky_operation()
except ValueError as e:
    print(f"값 에러: {e}")
except (TypeError, KeyError):
    print("타입 또는 키 에러")
else:
    # 예외 없이 성공한 경우만 실행
    process(result)
finally:
    # 항상 실행 (정리 코드)
    cleanup()
```

### 커스텀 예외

```python
class UserNotFoundError(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User {user_id} not found")

# 체이닝
try:
    db.query(...)
except DBError as e:
    raise UserNotFoundError(42) from e  # 원인 연결
```

### Context Manager (`with`)

```python
# 리소스 자동 정리
with open("file.txt") as f:
    data = f.read()
# 자동으로 f.close() 호출

# 여러 리소스
with open("in.txt") as fin, open("out.txt", "w") as fout:
    fout.write(fin.read())
```

### 🔄 4개 언어 비교

| 개념 | Python | Go | Kotlin | JS/TS |
|------|--------|-----|--------|-------|
| 에러 모델 | 예외 (try/except) | 값 (T, error) | 예외 + Result | 예외 (try/catch) |
| 리소스 정리 | `with` (context manager) | `defer` | `use` (Closeable) | `finally` / `using` |
| 에러 체이닝 | `raise ... from ...` | `%w` wrapping | `cause` | `Error(msg, {cause})` |

---

## 8️⃣ 컴프리헨션과 제너레이터

### List / Dict / Set Comprehension

```python
# List comprehension
squares = [x**2 for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]

# Dict comprehension
word_lengths = {w: len(w) for w in ["hello", "world"]}

# Set comprehension
unique_lengths = {len(w) for w in words}

# 중첩
matrix = [[1,2,3], [4,5,6]]
flat = [x for row in matrix for x in row]  # [1,2,3,4,5,6]
```

### Generator (지연 평가)

```python
# Generator expression (메모리 효율적)
total = sum(x**2 for x in range(1_000_000))  # 리스트 생성 안 함

# Generator function
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

for n in fibonacci():
    if n > 100:
        break
    print(n)
```

### 🧒 12살 비유

> Comprehension은 "한 줄 레시피"야 — `[요리(재료) for 재료 in 장바구니 if 신선한(재료)]`. 같은 걸 for 루프로 쓰면 5줄이 되는데, comprehension으로는 1줄이야.
>
> Generator는 "주문이 들어올 때마다 하나씩 만드는 빵집"이야 — 1000개를 미리 만들어 놓지 않고(리스트), 주문(next())이 올 때마다 하나씩 구워서 줘(yield). 메모리를 거의 안 써!

### 🔄 4개 언어 비교

| 개념 | Python | Go | Kotlin | JS/TS |
|------|--------|-----|--------|-------|
| 컴프리헨션 | ✅ list/dict/set | ❌ (for 루프) | ❌ (map/filter) | ❌ (map/filter) |
| 제너레이터 | `yield` | ❌ (채널로 유사 구현) | `sequence { yield() }` | `function*` / `yield` |
| 지연 평가 | generator expression | 없음 | `Sequence` | 없음 (라이브러리) |

---

## 📎 출처

1. [Python Tutorial (공식)](https://docs.python.org/3/tutorial/) — 기본 문법 가이드
2. [PEP 484 – Type Hints](https://peps.python.org/pep-0484/) — 타입힌트 도입
3. [PEP 557 – Data Classes](https://peps.python.org/pep-0557/) — dataclass
4. [PEP 634 – Structural Pattern Matching](https://peps.python.org/pep-0634/) — match/case
5. [Python Data Model](https://docs.python.org/3/reference/datamodel.html) — dunder 메서드

---

> 📌 **이전 문서**: [[02-python-architecture-and-runtime]] — CPython 아키텍처
> 📌 **다음 문서**: [[04-python-advanced-syntax-and-patterns]] — Python 고급 문법
> 📌 **관련 문서**: [[python-dict-key-ordering]] (dict 내부 구조)
