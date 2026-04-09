---
created: 2026-03-22
source: claude-code
tags: [architecture, python, fastapi, sqlmodel, layered-architecture]
---

# 📖 Layered Architecture — Concept Deep Dive

> 💡 **한줄 요약**: Layered Architecture는 애플리케이션을 Presentation, Business Logic, Persistence, Database 등 수평적 계층으로 분리하여 **관심사의 분리(Separation of Concerns)**를 달성하는 가장 보편적인 소프트웨어 아키텍처 패턴이다.

---

## 1️⃣ 무엇인가? (What is it?)

**Layered Architecture**(계층형 아키텍처)는 소프트웨어를 **수평적인 계층(layer)**으로 나누어 각 계층이 특정 역할만 담당하도록 구조화하는 설계 패턴이다. **N-Tier Architecture**라고도 불린다.

- **공식 정의**: 컴포넌트를 수평적 계층으로 조직하며, 각 계층은 애플리케이션 내에서 특정 역할을 수행한다 ([O'Reilly - Software Architecture Patterns](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/ch01.html))
- **탄생 배경**: 초기 엔터프라이즈 애플리케이션들은 UI 코드, 비즈니스 규칙, DB 접근 코드가 한 모듈에 혼재되어 있었다. 1996년 POSA(Pattern-Oriented Software Architecture)에서 공식 패턴으로 정리되었고, 2002년 Martin Fowler의 *Patterns of Enterprise Application Architecture*에서 체계화되었다. 테스트, 변경, 확장이 모두 어려운 **스파게티 코드** 문제를 해결하기 위해 등장했다.
- **해결하는 문제**: 코드의 결합도(coupling)를 낮추고, 각 관심사를 독립적으로 개발/테스트/유지보수할 수 있게 만든다.

> 현실 비유: 🏢 건물을 생각해보자. 1층은 로비(사용자 접점), 2층은 사무실(업무 처리), 지하는 창고(데이터 보관). 각 층은 자기 역할만 하고, 엘리베이터(인터페이스)로만 소통한다.

> 📌 **핵심 키워드**: `Separation of Concerns`, `N-Tier`, `Layer Isolation`, `Top-Down Dependency`

---

## 2️⃣ 핵심 개념 (Core Concepts)

Layered Architecture를 구성하는 핵심 요소와 원리를 살펴보자.

```
┌─────────────────────────────────────────────────────┐
│              Layered Architecture 구조               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │  🖥️  Presentation Layer (Router / API 엔드포인트) │  │
│  │     → HTTP 요청/응답 처리, 입력 검증            │  │
│  └──────────────────┬────────────────────────────┘  │
│                     │ 호출 (↓ only)                  │
│  ┌──────────────────▼────────────────────────────┐  │
│  │  ⚙️  Service Layer (비즈니스 로직)              │  │
│  │     → 도메인 규칙, 트랜잭션 관리                │  │
│  └──────────────────┬────────────────────────────┘  │
│                     │ 호출 (↓ only)                  │
│  ┌──────────────────▼────────────────────────────┐  │
│  │  💾  Persistence Layer (Repository / DAO)      │  │
│  │     → 데이터 접근, ORM 매핑                     │  │
│  └──────────────────┬────────────────────────────┘  │
│                     │ 호출 (↓ only)                  │
│  ┌──────────────────▼────────────────────────────┐  │
│  │  🗄️  Database Layer (실제 DB)                  │  │
│  │     → 데이터 저장/조회                          │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

| 구성 요소 | 역할 | FastAPI 매핑 |
|-----------|------|-------------|
| **Presentation Layer** | HTTP 요청/응답, 입력 검증, 라우팅 | `APIRouter`, Pydantic Schema |
| **Service Layer** | 비즈니스 로직, 트랜잭션 관리 | Service 클래스 |
| **Persistence Layer** | 데이터 접근, ORM 매핑, CRUD | Repository / DAO 클래스 |
| **Database Layer** | 실제 데이터 저장소 | SQLite / PostgreSQL |

### 핵심 원리

1. **Top-Down Dependency (하향 의존)**: 상위 계층은 하위 계층에만 의존한다. 역방향 의존은 금지.
2. **Layer Isolation (계층 격리)**: 각 계층은 자신의 역할만 수행하며, 다른 계층의 내부 구현을 모른다.
3. **Closed Layer vs Open Layer (폐쇄/개방 계층)**:
   - **Closed Layer**: 요청은 반드시 바로 아래 계층을 거쳐야 한다 (계층 건너뛰기 금지). 격리를 보장하지만 pass-through 코드가 생길 수 있다.
   - **Open Layer**: 상위 계층이 해당 계층을 건너뛰고 그 아래 계층에 직접 접근할 수 있다. Sinkhole 문제를 완화하지만 격리가 약해진다.
4. **Interface Contract (인터페이스 계약)**: 계층 간 통신은 정의된 인터페이스(DTO/Schema)를 통해서만 이루어진다.
5. **Dependency Inversion 적용 가능**: 순수 Layered Architecture는 상위가 하위에 직접 의존하지만, 인터페이스(ABC)를 도입하여 의존성을 역전시키면 테스트 용이성과 교체 가능성이 높아진다. 이것이 Clean Architecture로의 진화 경로가 된다.

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

Python + FastAPI + SQLModel 기반의 실제 프로젝트 구조와 동작 흐름을 살펴보자.

### 📁 프로젝트 구조

```
app/
├── main.py                  # FastAPI 앱 초기화
├── routers/                 # 🖥️ Presentation Layer
│   └── user_router.py
├── services/                # ⚙️ Service Layer
│   └── user_service.py
├── repositories/            # 💾 Persistence Layer
│   └── user_repository.py
├── models/                  # 도메인 모델 (SQLModel)
│   └── user.py
├── schemas/                 # DTO (요청/응답 스키마)
│   └── user_schema.py
├── database.py              # 🗄️ Database 설정
└── dependencies.py          # 의존성 주입 설정
```

### 💻 코드로 보는 각 계층

**1. Database Layer — `database.py`**

```python
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

**2. Model — `models/user.py`**

```python
from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True)
    is_active: bool = Field(default=True)
```

**3. Schema (DTO) — `schemas/user_schema.py`**

```python
from sqlmodel import SQLModel

class UserCreate(SQLModel):
    name: str
    email: str

class UserResponse(SQLModel):
    id: int
    name: str
    email: str
    is_active: bool
```

**4. Persistence Layer — `repositories/user_repository.py`**

```python
from sqlmodel import Session, select
from models.user import User
from typing import Optional

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user: User) -> User:
        self.session.add(user)
        # commit은 Service Layer에서 관리 (트랜잭션 경계 분리)
        self.session.flush()
        self.session.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def get_all(self) -> list[User]:
        statement = select(User)
        return self.session.exec(statement).all()
```

**5. Service Layer — `services/user_service.py`**

```python
from fastapi import HTTPException
from models.user import User
from schemas.user_schema import UserCreate, UserResponse
from repositories.user_repository import UserRepository

class UserService:
    def __init__(self, repository: UserRepository, session: Session):
        self.repository = repository
        self.session = session  # 트랜잭션 관리를 위해 Session 보유

    def create_user(self, user_data: UserCreate) -> UserResponse:
        # 비즈니스 로직: 이메일 중복 검사
        existing = self.repository.get_by_email(user_data.email)
        if existing:
            raise HTTPException(status_code=400, detail="이메일이 이미 존재합니다")

        user = User(name=user_data.name, email=user_data.email)
        created = self.repository.create(user)
        self.session.commit()  # 트랜잭션 커밋은 Service Layer에서 관리
        return UserResponse.model_validate(created)

    def get_user(self, user_id: int) -> UserResponse:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        return UserResponse.model_validate(user)

    def list_users(self) -> list[UserResponse]:
        users = self.repository.get_all()
        return [UserResponse.model_validate(u) for u in users]
```

**6. Presentation Layer — `routers/user_router.py`**

```python
from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from schemas.user_schema import UserCreate, UserResponse
from services.user_service import UserService
from repositories.user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["users"])

def get_user_service(session: Session = Depends(get_session)) -> UserService:
    repository = UserRepository(session)
    return UserService(repository, session)

@router.post("/", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    return service.create_user(user_data)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    return service.get_user(user_id)

@router.get("/", response_model=list[UserResponse])
def list_users(
    service: UserService = Depends(get_user_service),
):
    return service.list_users()
```

**7. App Entry Point — `main.py`**

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import create_db_and_tables
from routers.user_router import router as user_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()  # startup
    yield
    # shutdown 로직이 필요하면 여기에 작성

app = FastAPI(title="Layered Architecture Demo", lifespan=lifespan)
app.include_router(user_router)
```

> **Note**: FastAPI 0.93+에서는 `@app.on_event("startup")`이 deprecated되었고, `lifespan` 컨텍스트 매니저 방식이 권장된다.

### 🔄 동작 흐름 (Step by Step)

```
Client                Router              Service           Repository          DB
  │                     │                    │                   │               │
  │  POST /users/       │                    │                   │               │
  │────────────────────▶│                    │                   │               │
  │                     │  create_user()     │                   │               │
  │                     │───────────────────▶│                   │               │
  │                     │                    │  get_by_email()   │               │
  │                     │                    │──────────────────▶│  SELECT ...   │
  │                     │                    │                   │──────────────▶│
  │                     │                    │                   │◀──────────────│
  │                     │                    │◀──────────────────│               │
  │                     │                    │  create()         │               │
  │                     │                    │──────────────────▶│  INSERT ...   │
  │                     │                    │                   │──────────────▶│
  │                     │                    │                   │◀──────────────│
  │                     │                    │◀──────────────────│               │
  │                     │◀───────────────────│                   │               │
  │  201 Created (JSON) │                    │                   │               │
  │◀────────────────────│                    │                   │               │
```

1. **Step 1**: 클라이언트가 `POST /users/`로 요청 → **Router(Presentation)**가 수신
2. **Step 2**: Router는 입력을 `UserCreate` 스키마로 검증 후 **Service**에 위임
3. **Step 3**: Service는 비즈니스 로직(이메일 중복 검사) 수행 → **Repository**에 조회 요청
4. **Step 4**: Repository는 SQLModel을 통해 **Database**에 쿼리 실행
5. **Step 5**: 결과가 역순으로 올라가며 `UserResponse` DTO로 변환되어 클라이언트에 반환

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| # | 유즈 케이스 | 설명 | 적합한 이유 |
|---|------------|------|------------|
| 1 | **CRUD 기반 웹 API** | 사용자/상품/주문 관리 REST API | 표준적인 요청-응답 흐름과 계층 구분이 명확 |
| 2 | **사내 관리 시스템** | ERP, CRM, 인사관리 시스템 | 비즈니스 규칙이 명확하고 팀 분업에 유리 |
| 3 | **MVP / 스타트업 초기 제품** | 빠르게 출시해야 하는 초기 서비스 | 학습 곡선이 낮고 구조가 직관적 |
| 4 | **전통적 엔터프라이즈 앱** | 금융, 보험, 공공기관 시스템 | 조직 구조(프론트팀, 백엔드팀, DBA)와 자연스럽게 매핑 |

### ✅ 베스트 프랙티스

1. **비즈니스 로직은 반드시 Service Layer에**: Router에 비즈니스 로직을 넣지 말 것. Router는 HTTP 관심사(요청 검증, 응답 형태)만 담당한다.

```python
# ❌ Bad: Router에 비즈니스 로직
@router.post("/users/")
def create_user(data: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == data.email)).first()
    if existing:
        raise HTTPException(400, "중복")
    user = User(**data.dict())
    session.add(user)
    session.commit()
    return user

# ✅ Good: Service에 위임
@router.post("/users/")
def create_user(data: UserCreate, service: UserService = Depends(get_user_service)):
    return service.create_user(data)
```

2. **FastAPI Depends()로 의존성 주입 활용**: 계층 간 결합도를 낮추고 테스트 시 Mock 교체를 용이하게 한다.
3. **DTO(Schema)로 계층 간 데이터 전달**: SQLModel 모델을 직접 반환하지 말고, 응답 전용 Schema를 사용한다.
4. **Repository는 commit을 직접 하지 않는 것이 이상적**: 트랜잭션 관리는 Service Layer에서 담당하는 것이 좋다 ([DEV Community - Layered Architecture & DI](https://dev.to/markoulis/layered-architecture-dependency-injection-a-recipe-for-clean-and-testable-fastapi-code-3ioo)).

### 🧪 계층별 테스트 예시

계층형 아키텍처의 핵심 장점인 **독립적 테스트**를 실제 코드로 살펴보자.

```python
# tests/test_user_service.py
import pytest
from unittest.mock import MagicMock
from services.user_service import UserService
from schemas.user_schema import UserCreate
from models.user import User

def test_create_user_duplicate_email():
    """Service Layer 단위 테스트: Repository를 Mock으로 대체"""
    mock_repo = MagicMock()
    mock_session = MagicMock()
    mock_repo.get_by_email.return_value = User(id=1, name="기존유저", email="a@b.com")

    service = UserService(repository=mock_repo, session=mock_session)

    with pytest.raises(Exception):  # HTTPException 발생 확인
        service.create_user(UserCreate(name="새유저", email="a@b.com"))

    mock_repo.create.assert_not_called()  # 중복이면 create 미호출 확인

def test_create_user_success():
    """Service Layer 단위 테스트: 정상 생성 흐름"""
    mock_repo = MagicMock()
    mock_session = MagicMock()
    mock_repo.get_by_email.return_value = None
    mock_repo.create.return_value = User(id=1, name="새유저", email="new@b.com", is_active=True)

    service = UserService(repository=mock_repo, session=mock_session)
    result = service.create_user(UserCreate(name="새유저", email="new@b.com"))

    assert result.email == "new@b.com"
    mock_session.commit.assert_called_once()
```

> **포인트**: Service Layer만 테스트하면서 Repository는 Mock으로 교체했다. 이것이 계층 분리의 실질적 이점이다.

### 🏢 실제 적용 사례

- **대부분의 Spring Boot 프로젝트**: Controller → Service → Repository 구조가 사실상 업계 표준
- **Django REST Framework**: View → Serializer → Model/Manager 구조도 계층형의 변형
- **FastAPI 실무 프로젝트**: [fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices)에서 Router → Service → DAO 분리를 권장

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ 장점 | **관심사 분리** | 각 계층이 독립적 역할을 수행하여 코드 이해도와 유지보수성이 높아짐 |
| ✅ 장점 | **독립적 개발/테스트** | 계층별로 독립 테스트 가능, Mock을 활용한 단위 테스트가 용이 |
| ✅ 장점 | **팀 분업 용이** | 프론트팀(Presentation), 백엔드팀(Service), DBA(Persistence)로 자연스럽게 분업 |
| ✅ 장점 | **낮은 학습 곡선** | 가장 널리 알려진 패턴으로 대부분의 개발자가 친숙함 |
| ✅ 장점 | **컴포넌트 교체 용이** | DB나 UI 프레임워크를 교체할 때 해당 계층만 수정하면 됨 |
| ❌ 단점 | **성능 오버헤드** | 모든 요청이 여러 계층을 거쳐야 하므로 단순 조회에도 불필요한 레이어 통과 발생 |
| ❌ 단점 | **Architecture Sinkhole** | 계층을 거치지만 아무 로직도 수행하지 않는 pass-through 코드가 생길 수 있음 |
| ❌ 단점 | **변경 전파** | 요구사항 변경 시 여러 계층을 동시에 수정해야 하는 경우가 빈번 |
| ❌ 단점 | **과도한 복잡성** | 간단한 CRUD에도 Router + Service + Repository + Schema를 모두 만들어야 함 |

### ⚖️ Trade-off 분석

```
유지보수성 향상    ◄──── Trade-off ────►  개발 속도 저하 (초기 보일러플레이트)
관심사 분리        ◄──── Trade-off ────►  성능 오버헤드 (계층 통과 비용)
팀 분업 용이       ◄──── Trade-off ────►  변경 시 계층 간 조율 필요
구조적 명확성      ◄──── Trade-off ────►  간단한 앱에 과도한 복잡성
```

---

## 6️⃣ 차이점 비교 (Comparison)

Layered Architecture와 자주 비교되는 **Clean Architecture**, **Hexagonal Architecture**를 비교한다.

### 📊 비교 매트릭스

| 비교 기준 | Layered Architecture | Clean Architecture | Hexagonal Architecture |
|-----------|---------------------|--------------------|----------------------|
| **핵심 목적** | 관심사의 수평적 분리 | 비즈니스 로직 보호 (의존성 역전) | 외부 시스템과의 교체 가능성 |
| **의존 방향** | 위 → 아래 (Top-Down) | 바깥 → 안쪽 (Outside-In) | Port/Adapter를 통한 격리 |
| **복잡도** | ⭐⭐ 낮음 | ⭐⭐⭐⭐ 높음 | ⭐⭐⭐ 중간 |
| **학습 곡선** | 낮음 (가장 직관적) | 높음 (DIP, Use Case 등 추상화) | 중간 (Port/Adapter 이해 필요) |
| **테스트 용이성** | 중간 | 매우 높음 | 높음 |
| **적합한 경우** | MVP, CRUD, 소/중규모 | 복잡한 도메인, 장기 유지보수 | 외부 시스템 연동이 많은 앱 |
| **제안자** | POSA (1996), Fowler (2002) | Robert C. Martin (2012 블로그, 2017 도서) | Alistair Cockburn (2005) |

### 🔍 핵심 차이 요약

```
Layered Architecture              Clean Architecture              Hexagonal Architecture
─────────────────────    vs    ─────────────────────    vs    ─────────────────────
위→아래 단방향 의존              바깥→안쪽 동심원 의존            Port/Adapter 기반 격리
계층 간 직접 호출                인터페이스 통한 간접 호출          포트로 추상화된 호출
DB 계층이 가장 아래              DB가 외부(Infrastructure)         DB는 Adapter로 교체 가능
구조 단순, 빠른 시작              구조 복잡, 견고한 도메인           유연한 외부 시스템 교체
```

### 🤔 언제 무엇을 선택?

- **Layered Architecture를 선택하세요** → MVP나 초기 프로젝트, CRUD 중심 앱, 팀이 아키텍처 경험이 적을 때, 빠른 개발이 중요할 때
- **Clean Architecture를 선택하세요** → 복잡한 비즈니스 도메인, 장기 유지보수가 예상될 때, 프레임워크 독립성이 중요할 때
- **Hexagonal Architecture를 선택하세요** → 외부 시스템(결제, 메시지큐 등) 연동이 많고 자주 교체될 때, 높은 테스트 커버리지가 필요할 때

> 💡 **실무 팁**: Layered Architecture로 시작해서, 도메인이 복잡해지면 점진적으로 Clean/Hexagonal로 진화시키는 전략이 실용적이다 ([Medium - Layered vs Clean vs Hexagonal](https://medium.com/@rup.singh88/stop-confusing-clean-onion-hexagonal-architecture-heres-when-to-use-each-692079e56267)).

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|------|-----------|------------|
| 1 | **Router에 비즈니스 로직 작성** | Service Layer의 존재 의미가 사라지고 테스트 불가 | 비즈니스 로직은 반드시 Service로 분리 |
| 2 | **계층 건너뛰기 (Layer Skipping)** | Router에서 직접 Repository 호출 시 의존 관계가 꼬임 | 반드시 바로 아래 계층만 호출 |
| 3 | **SQLModel 모델을 API 응답으로 직접 반환** | DB 스키마 변경이 API 계약에 직접 영향 | 별도의 Response Schema(DTO) 사용 |
| 4 | **Service에서 HTTP 상태코드 관리** | Service가 HTTP에 종속되어 CLI, 배치 등에서 재사용 불가 | 커스텀 Exception을 정의하고 Router에서 HTTP 매핑 |

### 🚫 Anti-Patterns

1. **Architecture Sinkhole Anti-Pattern**: 요청이 각 계층을 통과하지만 아무 로직도 수행하지 않는 pass-through 코드가 전체의 80% 이상이면, 계층 구분이 과도한 것이다. 이 경우 일부 계층을 Open Layer로 전환하는 것을 고려한다.

```python
# ❌ Sinkhole: Service가 아무것도 안 하고 그냥 전달만
class UserService:
    def get_user(self, user_id: int):
        return self.repository.get_by_id(user_id)  # 로직 없이 pass-through
```

2. **Lasagna Architecture**: 과도한 추상화로 계층이 너무 많아져 디버깅이 어렵고, 프록시 메서드/클래스가 난무하는 상태 ([moldstud.com](https://moldstud.com/articles/p-common-pitfalls-in-layered-architecture-key-insights-and-solutions-to-avoid-mistakes)).

3. **Circular Dependency**: Service A가 Service B를, Service B가 다시 Service A를 참조하면 테스트와 모듈화가 불가능해진다.

### 🔒 보안/성능 고려사항

- **보안**: 인증/인가 로직은 Presentation Layer(미들웨어 또는 Dependency)에서 처리하되, 권한 기반 비즈니스 로직은 Service Layer에서 수행한다.
- **성능**: 단순 조회 API에서 N+1 쿼리 문제가 Repository 계층에서 발생하기 쉽다. SQLModel의 `selectinload`를 활용하여 Eager Loading을 적용한다.

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload

# N+1 방지: 관계 데이터를 미리 로딩
statement = select(User).options(selectinload(User.posts))
```

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|------|------|----------|
| 📖 공식 문서 | FastAPI 공식 Docs | [fastapi.tiangolo.com](https://fastapi.tiangolo.com) |
| 📖 공식 문서 | SQLModel 공식 Docs | [sqlmodel.tiangolo.com](https://sqlmodel.tiangolo.com) |
| 📘 도서 | *Software Architecture Patterns* (Mark Richards) | [O'Reilly](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/) — Ch.1이 Layered Architecture 전용 |
| 📘 도서 | *Clean Architecture* (Robert C. Martin) | Layered와 비교하며 읽으면 아키텍처 시야가 넓어짐 |
| 📺 블로그 | Herberto Graca — Layered Architecture | [herbertograca.com](https://herbertograca.com/2017/08/03/layered-architecture/) |
| 🎓 강의 | UQ CSSE6400 Layered Architecture Lecture | [uqcloud.net](https://csse6400.uqcloud.net/handouts/layered.pdf) |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리 | 언어/플랫폼 | 용도 |
|---------------|-----------|------|
| **FastAPI** | Python | 고성능 비동기 웹 프레임워크 (Presentation Layer) |
| **SQLModel** | Python | Pydantic + SQLAlchemy 통합 ORM (Model + Persistence) |
| **Pydantic** | Python | 데이터 검증 및 직렬화 (Schema/DTO) |
| **Alembic** | Python | DB 마이그레이션 도구 |
| **pytest** | Python | 계층별 단위/통합 테스트 |
| **Depends (FastAPI)** | Python | 의존성 주입 시스템 |

### 🔮 트렌드 & 전망

- **Layered → Modular Monolith 진화**: 순수 계층형에서 도메인 모듈 단위로 분리하는 Modular Monolith가 트렌드. 각 모듈 내부에서 계층형을 유지하되, 모듈 간에는 명확한 경계를 둔다.
- **FastAPI + SQLModel 생태계 성장**: SQLModel이 Pydantic v2와 통합되면서 Schema/Model 중복 코드가 줄어들고, 계층형 아키텍처에서의 DTO 관리가 더 간편해지고 있다.
- **점진적 아키텍처 진화**: 업계에서는 "처음부터 Clean Architecture를 적용하지 말고, Layered로 시작하여 필요에 따라 진화시키라"는 실용주의가 확산되고 있다.

### 💬 커뮤니티 인사이트

- "Layered Architecture의 가장 큰 실수는 Service Layer를 만들어 놓고 거기서 아무 로직도 안 하는 것이다. 그러면 그냥 Repository를 직접 호출하는 게 낫다" — Reddit 개발 커뮤니티 다수 의견
- "FastAPI의 `Depends()`는 Layered Architecture와 궁합이 매우 좋다. 각 계층을 쉽게 주입/교체할 수 있어서 테스트가 편해진다" — [DEV Community](https://dev.to/markoulis/layered-architecture-dependency-injection-a-recipe-for-clean-and-testable-fastapi-code-3ioo)
- "80% 이상의 요청이 Sinkhole(pass-through)이면 계층 구분을 재고해야 한다. Open Layer를 도입하거나 계층을 합치는 것이 현실적이다" — Mark Richards, *Software Architecture Patterns*

---

## 📎 Sources

1. [Software Architecture Patterns - O'Reilly (Mark Richards)](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/ch01.html) — 도서 (1장 Layered Architecture 전용)
2. [Layered Architecture & DI: Clean FastAPI Code - DEV Community](https://dev.to/markoulis/layered-architecture-dependency-injection-a-recipe-for-clean-and-testable-fastapi-code-3ioo) — 기술 블로그
3. [Layered Architecture - Herberto Graca](https://herbertograca.com/2017/08/03/layered-architecture/) — 기술 블로그
4. [Understanding Layered Architecture Pattern - DEV Community](https://dev.to/yasmine_ddec94f4d4/understanding-the-layered-architecture-pattern-a-comprehensive-guide-1e2j) — 기술 블로그
5. [Layered Architecture - Baeldung](https://www.baeldung.com/cs/layered-architecture) — 교육 자료
6. [The pros and cons of a layered architecture pattern - TechTarget](https://www.techtarget.com/searchapparchitecture/tip/The-pros-and-cons-of-a-layered-architecture-pattern) — 기술 미디어
7. [Layered vs Clean vs Hexagonal - Medium](https://medium.com/@rup.singh88/stop-confusing-clean-onion-hexagonal-architecture-heres-when-to-use-each-692079e56267) — 블로그
8. [Common Pitfalls in Layered Architecture - moldstud.com](https://moldstud.com/articles/p-common-pitfalls-in-layered-architecture-key-insights-and-solutions-to-avoid-mistakes) — 기술 블로그
9. [Hexagonal, Clean, Onion, Layered Deep Dive - Medium](https://romanglushach.medium.com/understanding-hexagonal-clean-onion-and-traditional-layered-architectures-a-deep-dive-c0f93b8a1b96) — 블로그
10. [FastAPI Best Practices - GitHub](https://github.com/zhanymkanov/fastapi-best-practices) — 커뮤니티

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 7
> - 수집 출처 수: 10
> - 출처 유형: 도서 1, 블로그 6, 교육 1, 기술 미디어 1, 커뮤니티 1

> 🔄 **Convergence Verification (2026-03-22)**
> - **정확성 수정**: Layered Architecture 기원을 "1980년대"에서 POSA(1996)/Fowler(2002)로 정정, Clean Architecture 제안자 연도 보강
> - **일관성 수정**: Repository 코드에서 `session.commit()` → `session.flush()`로 변경하여 베스트 프랙티스 #4(트랜잭션 관리는 Service Layer)와 일치시킴
> - **완전성 보강**: Open vs Closed Layer 구분 추가, Dependency Inversion 적용 가능성 언급, 테스트 코드 예시 추가
> - **코드 현행화**: FastAPI `on_event("startup")` deprecated → `lifespan` 컨텍스트 매니저 방식으로 업데이트
> - **오탈자 수정**: "시야이" → "시야가"
