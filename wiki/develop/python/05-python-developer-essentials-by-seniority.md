---
created: 2026-04-21
source: claude-code
tags: [python, career-growth, junior, senior, staff, interview, best-practices, essentials]
---

# 📖 Python 개발자 필수 지식 — 레벨별 성장 로드맵

> 💡 **한줄 요약**: Python 개발자의 성장 경로는 "Pythonic 코드 → 프레임워크 숙달 → CPython 내부 이해 → 언어 선택과 팀 표준 수립"으로 진행되며, GIL 이해와 async 패턴이 면접의 핵심 분기점이다.
>
> 📌 **면접 심화**: [[python-fastapi-sqlalchemy]] (Staff Engineer Interview Q&A 28문항)
> 📅 **기준**: Python 3.14 (2025.10)

---

## 성장 경로 개요

```
  Junior (0-2년)     Mid (2-4년)     Senior (4-7년)    Staff (7년+)
  ────────────      ────────────    ─────────────    ──────────
  "Pythonic하게"    "프로덕션      "CPython 내부    "기술 방향
   코드 쓰기"       수준 코드"     + 아키텍처"      + 팀 생산성"
  
  PEP 8, 타입힌트   async, 데코레이터  GIL, 메모리     언어 선택
  venv, 기본 테스트  프로파일링       메타프로그래밍    마이그레이션
  
  면접: ★★★        면접: ★★★★      면접: ★★★★★     면접: ★★★★★
```

---

## 1️⃣ Junior (0-2년) — "Pythonic하게 쓸 수 있는가"

### 필수 지식 ★★★

| 영역 | 구체 항목 | 참조 |
|------|---------|------|
| PEP 8 스타일 | 명명 규칙, 들여쓰기, 라인 길이 | [[03-python-basic-syntax]] |
| 타입 힌트 기초 | `str`, `int`, `list[T]`, `Optional` | [[03-python-basic-syntax]] §2 |
| 가상 환경 | venv, pip, uv | [[07-python-project-structure-and-tooling]] |
| 데이터 구조 | list/dict/set/tuple, comprehension | [[03-python-basic-syntax]] §5, §8 |
| 에러 처리 | try/except, 커스텀 예외, context manager | [[03-python-basic-syntax]] §7 |
| 기본 테스트 | pytest, assert, fixture 기초 | [[06-python-testing-patterns]] |
| OOP 기초 | 클래스, 상속, @property, dataclass | [[03-python-basic-syntax]] §6 |

### 흔한 실수 ★★★

| 실수 | 설명 |
|------|------|
| 가변 기본 인자 | `def f(items=[])` → 호출 간 공유! `None`으로 대체 |
| 얕은 복사 혼동 | `b = a[:]` vs `b = copy.deepcopy(a)` |
| 글로벌 변수 남용 | 모듈 수준 상태 → 테스트/동시성 문제 |
| bare except | `except:` 대신 `except Exception:` |
| f-string 안에 `\` | 3.12 이전에는 불가 |

### 면접 빈출 ★★★

- "list와 tuple의 차이점" — 가변/불변, 해시 가능성
- "GIL이 무엇인가?" — 기본 정의만
- "== vs is의 차이" — 값 비교 vs 객체 동일성
- "comprehension과 for 루프의 차이" — 성능 + 가독성

---

## 2️⃣ Mid-level (2-4년) — "프로덕션 수준 코드를 작성하는가"

### 필수 지식 ★★★★

| 영역 | 구체 항목 | 참조 |
|------|---------|------|
| 데코레이터 | 함수/클래스 데코레이터, `functools.wraps` | [[04-python-advanced-syntax-and-patterns]] §1 |
| async/await | asyncio, `gather`, `TaskGroup` | [[04-python-advanced-syntax-and-patterns]] §3 |
| 타입 시스템 중급 | `Protocol`, `TypeVar`, `Generic` | [[04-python-advanced-syntax-and-patterns]] §5 |
| 프레임워크 | FastAPI/Django 프로덕션 패턴 | [[python-fastapi-sqlalchemy]] |
| 프로파일링 | cProfile, line_profiler, memory_profiler | - |
| 패키징 | pyproject.toml, 배포 파이프라인 | [[07-python-project-structure-and-tooling]] |

### 면접 빈출 ★★★★

- "데코레이터 동작 원리를 설명하라" — 클로저, `functools.wraps`
- "asyncio와 threading의 차이" — GIL, 이벤트 루프
- "Python에서 동시성을 어떻게 구현하는가" — threading/multiprocessing/asyncio 선택 기준

---

## 3️⃣ Senior (4-7년) — "CPython 내부를 이해하는가"

### 필수 지식 ★★★★★

| 영역 | 구체 항목 | 참조 |
|------|---------|------|
| CPython 내부 | GIL 메커니즘, 바이트코드, ceval.c | [[02-python-architecture-and-runtime]] §2 |
| 메모리 관리 | Reference counting, cycle detector, pymalloc | [[02-python-architecture-and-runtime]] §3 |
| 메타프로그래밍 | 메타클래스, 디스크립터, `__init_subclass__` | [[04-python-advanced-syntax-and-patterns]] §2, §8 |
| 성능 최적화 | Cython, mypyc, C 확장, 프로파일링 | [[02-python-architecture-and-runtime]] §5 |
| 시스템 설계 | 마이크로서비스 with Python, 이벤트 기반 | - |

### 면접 빈출 ★★★★★

- "GIL이 어떻게 동작하고, 왜 존재하는가" — refcount, switch interval → interview-prep Q1
- "Python에서 CPU-bound 병렬화를 어떻게 하는가" — multiprocessing, C 확장, free-threaded
- "메모리 누수를 어떻게 디버깅하는가" — tracemalloc, objgraph, gc 모듈
- "프로덕션 성능 이슈를 어떻게 해결했는가" — 프로파일 → 원인 → 해결

---

## 4️⃣ Staff (7년+) — "기술 방향과 팀 생산성을 결정하는가"

### 필수 지식 ★★★★★

| 영역 | 구체 항목 |
|------|---------|
| 언어 선택 | Python vs Go/Kotlin 트레이드오프 판단 |
| 마이그레이션 | sync → async 전환, 2 → 3 레거시, free-threaded 도입 판단 |
| 팀 표준 | 타입힌트 정책(strict mypy), 코드 스타일, 테스트 전략 |
| 아키텍처 | 모노리스 → 마이크로서비스, Python + Go 하이브리드 |

### 면접 빈출 ★★★★★

- "Python을 선택한 기술적 근거를 설명하라" — 도메인, 팀, 성능 요구사항
- "대규모 Python 프로젝트의 타입 안전성을 어떻게 확보했는가"
- "Python의 한계를 어떻게 극복했는가" — 성능, GIL, 타입 안전

> 📌 Staff 면접 전체: [[python-fastapi-sqlalchemy]] (28문항, L6/L7)

---

## 📋 자기 진단 체크리스트

### Junior → Mid
- [ ] 데코레이터를 직접 작성할 수 있다
- [ ] async/await로 비동기 코드를 작성할 수 있다
- [ ] mypy로 타입 검사를 통과시킬 수 있다
- [ ] pytest fixture를 활용한 테스트를 작성한다

### Mid → Senior
- [ ] GIL의 동작 메커니즘을 설명할 수 있다
- [ ] cProfile로 병목을 찾고 최적화할 수 있다
- [ ] 디스크립터/메타클래스의 동작 원리를 안다
- [ ] Python 3.13+ free-threaded 모드를 이해한다

### Senior → Staff
- [ ] Python vs Go 선택 근거를 기술적으로 판단할 수 있다
- [ ] 팀 전체의 타입힌트 정책을 수립할 수 있다
- [ ] 대규모 async 마이그레이션을 계획할 수 있다

---

## 📎 출처

1. [Effective Python (Brett Slatkin)](https://effectivepython.com/) — Pythonic 코딩 가이드
2. [Python Type System (mypy docs)](https://mypy.readthedocs.io/) — 타입 시스템 가이드
3. [CPython Developer Guide](https://devguide.python.org/) — CPython 내부 가이드

---

> 📌 **이전 문서**: [[04-python-advanced-syntax-and-patterns]]
> 📌 **다음 문서**: [[06-python-testing-patterns]]
> 📌 **면접 심화**: [[python-fastapi-sqlalchemy]] (28문항)
