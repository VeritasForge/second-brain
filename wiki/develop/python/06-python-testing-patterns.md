---
created: 2026-04-21
source: claude-code
tags: [python, testing, pytest, mock, hypothesis, testcontainers, async-testing, benchmark]
---

# 📖 Python 테스팅 패턴 — pytest 중심의 테스트 전략

> 💡 **한줄 요약**: Python 테스팅은 pytest의 fixture/parametrize를 중심으로 unittest.mock, Hypothesis(속성 기반 테스트), testcontainers를 조합하면 단위부터 통합까지 커버할 수 있다.
>
> 📌 **핵심 키워드**: pytest, fixture, parametrize, MagicMock, Hypothesis, testcontainers, pytest-asyncio
> 📅 **기준**: Python 3.14 (2025.10)

---

## 1️⃣ pytest 기본 — Python의 테이블 드리븐 테스트

### 기본 테스트

```python
def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
```

### parametrize (테이블 드리븐)

```python
@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    (-1, 3, 2),
    (0, 0, 0),
    (1 << 31, 1, (1 << 31) + 1),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### Fixture

```python
@pytest.fixture
def db_session():
    session = create_session()
    yield session  # 테스트에 제공
    session.rollback()
    session.close()

@pytest.fixture(scope="module")  # 모듈당 1회
def app():
    return create_app(testing=True)

def test_create_user(db_session):
    user = User(name="Go")
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
```

| Fixture Scope | 생명 주기 | 용도 |
|--------------|---------|------|
| `function` (기본) | 각 테스트 함수 | 대부분의 경우 |
| `class` | 테스트 클래스 | 클래스 내 공유 |
| `module` | 모듈(.py 파일) | DB 연결 등 무거운 설정 |
| `session` | 전체 테스트 세션 | 앱 인스턴스 |

### 🔄 Go 테스트와 비교

| 개념 | Python (pytest) | Go (testing) |
|------|----------------|-------------|
| 테이블 테스트 | `@parametrize` | struct slice + `t.Run` |
| 설정/해제 | `fixture` (yield) | `t.Cleanup()` |
| 서브테스트 | `@parametrize` ID | `t.Run("name")` |
| 테스트 발견 | `test_` 접두사 (자동) | `Test` 접두사 (자동) |

---

## 2️⃣ Mocking

### unittest.mock

```python
from unittest.mock import MagicMock, patch, AsyncMock

# MagicMock
mock_repo = MagicMock(spec=UserRepository)
mock_repo.get_by_id.return_value = User(name="Go")

svc = UserService(repo=mock_repo)
user = svc.get_user(1)
mock_repo.get_by_id.assert_called_once_with(1)

# patch (컨텍스트 매니저)
with patch("myapp.services.send_email") as mock_send:
    mock_send.return_value = True
    result = process_order(order)
    mock_send.assert_called_once()

# AsyncMock (async 함수 모킹)
mock_client = AsyncMock()
mock_client.fetch.return_value = {"status": "ok"}
result = await handler(mock_client)
```

### side_effect

```python
# 순서대로 다른 값 반환
mock.get.side_effect = [result1, result2, TimeoutError()]

# 커스텀 로직
mock.process.side_effect = lambda x: x * 2
```

---

## 3️⃣ testcontainers

```python
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg.get_connection_url()

def test_user_crud(postgres):
    engine = create_engine(postgres)
    # 실제 PostgreSQL로 테스트
```

---

## 4️⃣ Hypothesis — 속성 기반 테스트

```python
from hypothesis import given
from hypothesis import strategies as st

@given(st.lists(st.integers()))
def test_sort_is_idempotent(lst):
    """정렬을 두 번 해도 결과가 같다"""
    assert sorted(sorted(lst)) == sorted(lst)

@given(st.text(min_size=1), st.text(min_size=1))
def test_concat_length(a, b):
    """문자열 연결의 길이 = 각 길이의 합"""
    assert len(a + b) == len(a) + len(b)
```

| 개념 | Hypothesis (Python) | Fuzzing (Go) |
|------|-------------------|-------------|
| 입력 생성 | 전략(strategies) 기반 | 무작위 바이트 |
| 실패 축소 | 자동 shrinking | 자동 |
| 타입 인식 | ✅ (전략이 타입별) | ❌ (바이트 수준) |

---

## 5️⃣ Async 테스트

```python
import pytest

@pytest.mark.asyncio
async def test_fetch_user():
    user = await fetch_user(1)
    assert user.name == "Go"

@pytest.mark.asyncio
async def test_concurrent_fetch():
    users = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
    )
    assert len(users) == 2
```

---

## 6️⃣ 커버리지와 테스트 조직

```bash
# 커버리지 측정
pytest --cov=src --cov-report=html

# 특정 마커만 실행
pytest -m "not slow"

# 병렬 실행
pytest -n auto  # pytest-xdist
```

### 파일 구조

```
src/myapp/
├── services/
│   └── user.py
tests/
├── conftest.py          ← 공유 fixture
├── unit/
│   └── test_user.py
├── integration/
│   └── test_user_db.py
└── e2e/
    └── test_api.py
```

---

## 📎 출처

1. [pytest Documentation](https://docs.pytest.org/) — 공식 문서
2. [Hypothesis Documentation](https://hypothesis.readthedocs.io/) — 속성 기반 테스트
3. [testcontainers-python](https://testcontainers-python.readthedocs.io/) — 통합 테스트

---

> 📌 **이전 문서**: [[05-python-developer-essentials-by-seniority]]
> 📌 **다음 문서**: [[07-python-project-structure-and-tooling]]
