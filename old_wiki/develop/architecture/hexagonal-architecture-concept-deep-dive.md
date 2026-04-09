---
created: 2026-03-22
source: claude-code
tags: [architecture, python, fastapi, sqlmodel, hexagonal-architecture, ports-and-adapters]
---

# 📖 Port And Adapter (Hexagonal Architecture) — Concept Deep Dive

> 💡 **한줄 요약**: Hexagonal Architecture는 비즈니스 로직(도메인)을 중심에 두고, 외부 세계와의 모든 상호작용을 **Port(인터페이스)**와 **Adapter(구현체)**로 분리하여 기술 독립적이고 테스트 가능한 시스템을 만드는 아키텍처 패턴이다.

---

## 1️⃣ 무엇인가? (What is it?)

**Hexagonal Architecture**(헥사고날 아키텍처)는 2005년 **Alistair Cockburn**이 제안한 소프트웨어 아키텍처 패턴으로, 공식 명칭은 **Ports and Adapters** 패턴이다.

- **공식 정의**: 애플리케이션 컴포넌트를 느슨하게 결합(loosely coupled)하여, Port와 Adapter를 통해 소프트웨어 환경과 쉽게 연결할 수 있도록 설계하는 패턴 ([Wikipedia](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)))
- **탄생 배경**: Cockburn은 1994년 처음 육각형 그림을 그렸고, 이후 디자인 패턴을 학습하며 육각형의 각 변이 형식적 의미에서 Port를 나타낸다는 것을 깨달았다. 2005년 Portland Pattern Repository 위키에서 패턴명을 "Ports and Adapters"로 공식 개명했다. 기존 계층형 아키텍처에서 발생하는 **UI 코드와 비즈니스 로직의 오염**, **계층 간 원치 않는 의존성** 문제를 해결하기 위해 등장했다 ([Alistair Cockburn 원문](https://alistair.cockburn.us/hexagonal-architecture))
- **해결하려는 문제**: 데이터 저장소나 UI에 의존하지 않고 애플리케이션 컴포넌트를 독립적으로 테스트할 수 있는 구조를 만드는 것

> 📌 **핵심 키워드**: `Port`, `Adapter`, `Domain`, `Dependency Inversion`, `Loosely Coupled`, `Technology Agnostic`

---

## 2️⃣ 핵심 개념 (Core Concepts)

Hexagonal Architecture를 구성하는 3가지 핵심 요소는 **Domain**, **Port**, **Adapter**이다.

```
┌──────────────────────────────────────────────────────────────┐
│                    외부 세계 (External World)                  │
│                                                              │
│  ┌──────────┐                            ┌──────────────┐   │
│  │ REST API │──┐                    ┌──▶ │  PostgreSQL  │   │
│  │ (Driving)│  │                    │    │  (Driven)    │   │
│  └──────────┘  │                    │    └──────────────┘   │
│                │  ┌──────────────┐  │                       │
│  ┌──────────┐  ├─▶│              │──┤    ┌──────────────┐   │
│  │   CLI    │──┘  │   DOMAIN    │  └──▶ │  Email SMTP  │   │
│  │ (Driving)│     │  (핵심 로직)  │       │  (Driven)    │   │
│  └──────────┘  ┌─▶│              │──┐    └──────────────┘   │
│                │  └──────────────┘  │                       │
│  ┌──────────┐  │    ▲          ▲    │    ┌──────────────┐   │
│  │  Test    │──┘    │          │    └──▶ │  Redis Cache │   │
│  │ (Driving)│   Input Port  Output Port  │  (Driven)    │   │
│  └──────────┘  (Driving)    (Driven)     └──────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

| 구성 요소 | 역할 | 설명 |
|-----------|------|------|
| **Domain (도메인)** | 비즈니스 로직의 핵심 | 외부 기술에 대한 의존성이 전혀 없는 순수한 비즈니스 규칙과 엔티티 |
| **Port (포트)** | 기술 비종속 인터페이스 | 애플리케이션이 외부 세계와 통신하는 방법을 정의하는 추상 인터페이스 (Python의 ABC) |
| **Adapter (어댑터)** | 포트의 구체적 구현 | 특정 기술(REST, DB, SMTP 등)을 사용하여 포트 인터페이스를 실제로 구현하는 클래스 |
| **Driving (Primary)** | 입력 측 어댑터 | 애플리케이션을 **사용하는** 측 (REST Controller, CLI, Test) |
| **Driven (Secondary)** | 출력 측 어댑터 | 애플리케이션이 **사용하는** 측 (DB, 메시지 큐, 외부 API) |

- **Port**는 USB 포트와 비슷하다: 다양한 장치(어댑터)가 같은 규격(인터페이스)으로 연결됨 ([AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/hexagonal-architecture.html))
- **Dependency Inversion Principle(DIP)**이 핵심 원리: 도메인이 인터페이스를 정의하고, 외부 기술이 그 인터페이스를 구현한다

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

### 📂 Python + FastAPI + SQLModel 디렉토리 구조

```
my_app/
├── domain/                    # 🏗️ 도메인 계층 (순수 비즈니스 로직)
│   ├── models.py              #   엔티티, 값 객체
│   └── ports.py               #   Port 인터페이스 (ABC)
├── application/               # ⚙️ 애플리케이션 계층 (유즈케이스)
│   └── use_cases.py           #   유즈케이스 (오케스트레이션)
├── adapters/                  # 🔌 어댑터 계층
│   ├── inbound/               #   Driving Adapter
│   │   └── api.py             #     FastAPI Router
│   └── outbound/              #   Driven Adapter
│       └── sqlmodel_repo.py   #     SQLModel Repository
├── bootstrap.py               # 💉 의존성 주입 설정
└── main.py                    # 🚀 FastAPI 앱 진입점
```

```
┌─────────────────────────────────────────────────────────────┐
│                  아키텍처 레이어 다이어그램                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Inbound Adapter (FastAPI Router)           │   │
│  │  POST /users  →  api.py  →  UserCreateRequest       │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                          │ calls                            │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Application (Use Cases)                   │   │
│  │  CreateUserUseCase.execute(command)                  │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                          │ uses Port                        │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Domain (Port + Model)                   │   │
│  │  UserRepository(ABC)  ←  User(Entity)               │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                          │ implemented by                   │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         Outbound Adapter (SQLModel Repo)             │   │
│  │  SQLModelUserRepository → PostgreSQL                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (Step by Step)

1. **Step 1 — 요청 수신**: FastAPI Router(Inbound Adapter)가 HTTP 요청을 받음
2. **Step 2 — DTO 변환**: 요청 데이터를 도메인이 이해하는 Command/DTO로 변환
3. **Step 3 — 유즈케이스 실행**: Application 계층의 UseCase가 비즈니스 흐름을 오케스트레이션
4. **Step 4 — 도메인 로직**: Domain 엔티티가 비즈니스 규칙을 실행 (유효성 검증 등)
5. **Step 5 — Port를 통한 저장**: UseCase가 Output Port(Repository 인터페이스)를 호출
6. **Step 6 — Adapter 실행**: SQLModel Adapter가 실제 DB에 데이터 저장
7. **Step 7 — 응답 반환**: 결과를 역방향으로 전달하여 HTTP 응답 생성

### 💻 코드 예시: Python + FastAPI + SQLModel

**1. Domain Layer — 엔티티 & 포트**

```python
# domain/models.py
from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class User:
    """순수 도메인 엔티티 — 외부 의존성 없음"""
    name: str
    email: str
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True

    def deactivate(self) -> None:
        """비즈니스 규칙: 사용자 비활성화"""
        if not self.is_active:
            raise ValueError("이미 비활성화된 사용자입니다.")
        self.is_active = False

    def change_email(self, new_email: str) -> None:
        """비즈니스 규칙: 이메일 변경 시 유효성 검증"""
        if "@" not in new_email:
            raise ValueError("유효하지 않은 이메일 형식입니다.")
        self.email = new_email
```

```python
# domain/ports.py
from abc import ABC, abstractmethod
from uuid import UUID
from domain.models import User


class UserRepositoryPort(ABC):
    """Output Port — 도메인이 정의하는 저장소 인터페이스"""

    @abstractmethod
    def save(self, user: User) -> User:
        ...

    @abstractmethod
    def find_by_id(self, user_id: UUID) -> User | None:
        ...

    @abstractmethod
    def find_by_email(self, email: str) -> User | None:
        ...

    @abstractmethod
    def delete(self, user_id: UUID) -> None:
        ...
```

**2. Application Layer — 유즈케이스**

```python
# application/use_cases.py
from dataclasses import dataclass
from uuid import UUID
from domain.models import User
from domain.ports import UserRepositoryPort


@dataclass
class CreateUserCommand:
    name: str
    email: str


class CreateUserUseCase:
    """유즈케이스: 사용자 생성 — Port를 통해 외부와 통신"""

    def __init__(self, user_repo: UserRepositoryPort):
        self._user_repo = user_repo  # Port 주입 (구체 구현 모름)

    def execute(self, command: CreateUserCommand) -> User:
        # 비즈니스 규칙: 이메일 중복 체크
        existing = self._user_repo.find_by_email(command.email)
        if existing is not None:
            raise ValueError(f"이메일 '{command.email}'은 이미 사용 중입니다.")

        user = User(name=command.name, email=command.email)
        return self._user_repo.save(user)


class GetUserUseCase:
    def __init__(self, user_repo: UserRepositoryPort):
        self._user_repo = user_repo

    def execute(self, user_id: UUID) -> User:
        user = self._user_repo.find_by_id(user_id)
        if user is None:
            raise ValueError(f"사용자를 찾을 수 없습니다: {user_id}")
        return user
```

**3. Outbound Adapter — SQLModel Repository**

```python
# adapters/outbound/sqlmodel_repo.py
from uuid import UUID
from sqlmodel import SQLModel, Field, Session, select
from domain.models import User as DomainUser
from domain.ports import UserRepositoryPort


class UserTable(SQLModel, table=True):
    """SQLModel 테이블 모델 — 인프라 관심사"""
    __tablename__ = "users"

    id: UUID = Field(primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    is_active: bool = Field(default=True)


class SQLModelUserRepository(UserRepositoryPort):
    """Driven Adapter — SQLModel로 Port 인터페이스 구현"""

    def __init__(self, session: Session):
        self._session = session

    def save(self, user: DomainUser) -> DomainUser:
        db_user = UserTable(
            id=user.id, name=user.name,
            email=user.email, is_active=user.is_active
        )
        self._session.add(db_user)
        self._session.commit()
        self._session.refresh(db_user)
        return self._to_domain(db_user)

    def find_by_id(self, user_id: UUID) -> DomainUser | None:
        db_user = self._session.get(UserTable, user_id)
        return self._to_domain(db_user) if db_user else None

    def find_by_email(self, email: str) -> DomainUser | None:
        statement = select(UserTable).where(UserTable.email == email)
        db_user = self._session.exec(statement).first()
        return self._to_domain(db_user) if db_user else None

    def delete(self, user_id: UUID) -> None:
        db_user = self._session.get(UserTable, user_id)
        if db_user:
            self._session.delete(db_user)
            self._session.commit()

    @staticmethod
    def _to_domain(db_user: UserTable) -> DomainUser:
        """DB 모델 → 도메인 모델 변환 (매핑)"""
        return DomainUser(
            id=db_user.id, name=db_user.name,
            email=db_user.email, is_active=db_user.is_active
        )
```

**4. Inbound Adapter — FastAPI Router**

```python
# adapters/inbound/api.py
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from application.use_cases import CreateUserUseCase, CreateUserCommand, GetUserUseCase
from bootstrap import get_create_user_use_case, get_get_user_use_case

router = APIRouter(prefix="/users", tags=["users"])


class UserCreateRequest(BaseModel):
    name: str
    email: str


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    is_active: bool


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    request: UserCreateRequest,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
):
    """Driving Adapter — HTTP 요청을 UseCase Command로 변환"""
    try:
        command = CreateUserCommand(name=request.name, email=request.email)
        user = use_case.execute(command)
        return UserResponse(
            id=user.id, name=user.name,
            email=user.email, is_active=user.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    use_case: GetUserUseCase = Depends(get_get_user_use_case),
):
    try:
        user = use_case.execute(user_id)
        return UserResponse(
            id=user.id, name=user.name,
            email=user.email, is_active=user.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

**5. Bootstrap — 의존성 주입**

```python
# bootstrap.py
from sqlmodel import Session, create_engine
from adapters.outbound.sqlmodel_repo import SQLModelUserRepository
from application.use_cases import CreateUserUseCase, GetUserUseCase

DATABASE_URL = "postgresql://user:pass@localhost:5432/mydb"
engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session


def get_create_user_use_case():
    with Session(engine) as session:
        repo = SQLModelUserRepository(session)
        yield CreateUserUseCase(user_repo=repo)


def get_get_user_use_case():
    with Session(engine) as session:
        repo = SQLModelUserRepository(session)
        yield GetUserUseCase(user_repo=repo)
```

**6. Main — FastAPI 앱 진입점**

```python
# main.py
from fastapi import FastAPI
from sqlmodel import SQLModel
from bootstrap import engine
from adapters.inbound.api import router

app = FastAPI(title="Hexagonal Architecture Demo")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

app.include_router(router)
```

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| # | 유즈 케이스 | 설명 | 적합한 이유 |
|---|------------|------|------------|
| 1 | **복잡한 비즈니스 로직이 있는 서비스** | 결제, 예약, 주문 처리 등 규칙이 복잡한 도메인 | 도메인 로직을 인프라로부터 격리하여 변경에 안전 |
| 2 | **멀티 채널 입력 시스템** | REST + GraphQL + CLI + 메시지 큐로 같은 도메인 접근 | 여러 Driving Adapter가 같은 Port를 공유 |
| 3 | **DB 마이그레이션이 예정된 프로젝트** | MySQL → PostgreSQL, 또는 RDB → NoSQL 전환 | Driven Adapter만 교체하면 도메인 변경 불필요 |
| 4 | **마이크로서비스 아키텍처** | 서비스 간 독립적 배포와 기술 스택 선택 | 각 서비스가 독립적 Hexagon으로 동작 |
| 5 | **TDD/BDD 기반 개발** | 테스트 주도 개발이 필수인 프로젝트 | Mock Adapter로 인프라 없이 도메인 테스트 가능 |

### ✅ 베스트 프랙티스

1. **도메인 모델에서 프레임워크 의존성 제거**: `domain/` 패키지에는 `fastapi`, `sqlmodel` 등의 import가 없어야 한다
2. **Port를 도메인 계층에 정의**: Output Port(ABC)는 도메인 계층이 소유하고, 어댑터가 구현한다 (DIP)
3. **유즈케이스 단위로 클래스 분리**: `CreateUserUseCase`, `GetUserUseCase`처럼 하나의 유즈케이스 = 하나의 클래스
4. **DB 모델 ↔ 도메인 모델 매핑**: SQLModel 테이블 모델과 도메인 엔티티를 분리하고 변환 로직을 Adapter에 둔다
5. **의존성 주입 컨테이너 활용**: `bootstrap.py`에서 모든 조립(wiring)을 수행하여 결합도를 한 곳에서 관리

### 🏢 실제 적용 사례

- **Netflix**: 마이크로서비스 간 기술 독립성 확보를 위해 Ports & Adapters 패턴 활용. JSON API → GraphQL 데이터 소스 전환 시 비즈니스 로직 변경 없이 Adapter만 교체하여 성공적으로 마이그레이션 ([Netflix Tech Blog](https://netflixtechblog.com/ready-for-changes-with-hexagonal-architecture-b315ec967749))
- **AWS Lambda**: AWS 공식 가이드에서 Lambda + DynamoDB 조합의 Hexagonal Architecture 패턴을 권장 ([AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/hexagonal-architecture.html))
- **Spotify**: 마이크로서비스 설계에 Hexagonal 원칙을 적용한 것으로 알려져 있으나, Spotify 공식 엔지니어링 블로그에서 직접 확인된 바는 없음 (⚠️ 3rd-party 출처 기반)

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ 장점 | **테스트 용이성** | Mock Adapter로 DB 없이 도메인 로직 단위 테스트 가능 |
| ✅ 장점 | **기술 독립성** | DB, 프레임워크 교체 시 도메인 코드 변경 불필요 |
| ✅ 장점 | **유연한 확장** | 새 입출력 채널 추가 시 Adapter만 구현하면 됨 |
| ✅ 장점 | **도메인 집중** | 비즈니스 로직이 명확히 분리되어 가독성과 유지보수성 향상 |
| ✅ 장점 | **기술 결정 지연** | DB 선택 등을 나중에 결정해도 개발 진행 가능 |
| ❌ 단점 | **초기 복잡도** | 간단한 CRUD에도 Port, Adapter, UseCase 등 많은 파일 필요 |
| ❌ 단점 | **학습 곡선** | DIP, ABC, 매핑 등 Python에서 자연스럽지 않은 개념 요구 |
| ❌ 단점 | **성능 오버헤드** | 간접 호출 계층이 추가되어 미세한 성능 저하 가능 |
| ❌ 단점 | **디버깅 난이도** | 추상화 계층이 많아 실제 실행 코드 추적이 어려울 수 있음 |
| ❌ 단점 | **팀 규율 필요** | 계층 간 경계를 지키려면 코드 리뷰 등 지속적 관리 필요 |

### ⚖️ Trade-off 분석

```
테스트 용이성     ◄──────── Trade-off ────────►  초기 보일러플레이트 증가
기술 독립성       ◄──────── Trade-off ────────►  매핑 코드 유지보수 비용
도메인 순수성     ◄──────── Trade-off ────────►  Python 답지 않은 패턴 (ABC)
유연한 확장       ◄──────── Trade-off ────────►  간단한 앱에는 과도한 설계
```

> 💡 **판단 기준**: 비즈니스 로직이 복잡하고, 기술 스택 변경 가능성이 있으며, 장기 유지보수가 필요한 프로젝트라면 Hexagonal Architecture의 ROI가 충분하다 ([Medium - Fastned](https://medium.com/fastned/when-and-when-not-to-use-hexagonal-architecture-c0850d643b3b))

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 비교 매트릭스

| 비교 기준 | Hexagonal (Ports & Adapters) | Clean Architecture | Onion Architecture | Layered (N-Tier) |
|-----------|------------------------------|--------------------|--------------------|------------------|
| **창시자** | Alistair Cockburn (2005) | Robert C. Martin (2012) | Jeffrey Palermo (2008) | 전통적 패턴 |
| **핵심 메타포** | 육각형 + Port/Adapter | 동심원 + Dependency Rule | 양파 껍질 레이어 | 수직 계층 |
| **핵심 원리** | 외부 교체 가능성 | 의존성 방향 규칙 | 도메인 보호 | 계층 간 순차 호출 |
| **복잡도** | 중간 | 높음 (4개 원) | 중간~높음 | 낮음 |
| **테스트 용이성** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **기술 교체 유연성** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **학습 곡선** | 중간 | 높음 | 중간 | 낮음 |
| **적합한 경우** | 다양한 I/O 채널 | 대규모 엔터프라이즈 | DDD 기반 프로젝트 | 간단한 CRUD 앱 |

### 🔍 핵심 차이 요약

```
Hexagonal                        Clean Architecture
──────────────────────    vs    ──────────────────────
Port/Adapter 중심                Dependency Rule 중심
2개 영역 (내부/외부)              4개 동심원 (Entity→UC→Interface→FW)
기술 교체에 초점                  계층 책임 명확화에 초점
비교적 가벼운 구조                명시적이고 엄격한 구조

Hexagonal                        Layered (N-Tier)
──────────────────────    vs    ──────────────────────
의존성이 안쪽을 향함               의존성이 아래를 향함
Port로 추상화                    직접 호출
DB 교체 용이                     DB 변경 시 전파 발생
```

### 🤔 언제 무엇을 선택?

- **Hexagonal을 선택하세요** → 다양한 입출력 채널이 필요하거나, DB/프레임워크 교체 가능성이 높은 프로젝트. 중소규모에서 대규모까지 적합 ([DEV Community](https://dev.to/dev_tips/hexagonal-vs-clean-vs-onion-which-one-actually-survives-your-app-in-2026-273f))
- **Clean Architecture를 선택하세요** → 대규모 엔터프라이즈 앱에서 각 계층의 책임을 매우 명확히 구분해야 할 때
- **Onion Architecture를 선택하세요** → DDD를 적극 활용하고 도메인 모델 보호가 최우선일 때
- **Layered Architecture를 선택하세요** → 비즈니스 로직이 단순한 CRUD 위주의 소규모 서비스

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|------|-----------|------------|
| 1 | 도메인에 SQLModel import | 도메인이 인프라에 의존하게 됨 | `dataclass`나 순수 Python 클래스로 도메인 모델 정의 |
| 2 | UseCase 간 직접 호출 | UseCase가 서로 얽혀 변경 전파 | 각 UseCase는 독립적으로, 필요 시 도메인 서비스 공유 |
| 3 | Adapter에 비즈니스 로직 삽입 | 로직이 분산되어 테스트/유지보수 어려움 | 모든 비즈니스 규칙은 도메인 엔티티 또는 UseCase에 |
| 4 | DB 스키마 먼저 설계 | 기술이 도메인을 지배하게 됨 | 도메인 모델 먼저, DB 스키마는 Adapter에서 매핑 |
| 5 | 모든 모듈에 Hexagonal 적용 | 단순 CRUD에 과도한 설계 | 복잡한 도메인이 있는 모듈에만 선택적 적용 |

### 🚫 Anti-Patterns

1. **Anemic Domain Model**: 도메인 엔티티가 데이터만 담고 로직은 UseCase에 몰려 있는 패턴. 도메인 엔티티에 비즈니스 메서드(`deactivate()`, `change_email()` 등)를 넣어야 한다 ([Medium - Allousas](https://medium.com/@allousas/hexagonal-architecture-common-pitfalls-f155e12388a3))

2. **Adapter가 Adapter를 호출**: Driven Adapter가 다른 Driven Adapter를 직접 참조하면 결합도가 높아진다. 반드시 UseCase를 통해서만 조율해야 한다 ([Thomas Pierrain Blog](http://tpierrain.blogspot.com/2020/03/hexagonal-architecture-dont-get-lost-on.html))

3. **Hexagon = Domain이라는 오해**: Hexagon은 도메인만이 아니라 **Application 계층(UseCase)까지 포함**한다. 도메인과 애플리케이션 계층을 합친 것이 Hexagon이다 ([Medium - Gara Mohamed](https://medium.com/@gara.mohamed/hexagonal-architectures-common-misconceptions-9aa2380c13c0))

### 🔒 보안/성능 고려사항

- **보안**: Port 인터페이스에 입력 유효성 검증 로직을 반드시 포함. Adapter에서 들어오는 데이터를 신뢰하지 말 것
- ⚡ **성능**: 매핑 레이어(DB 모델 ↔ 도메인 모델)에서 불필요한 객체 복사를 최소화. 대량 데이터 처리 시 bulk 연산을 Adapter 레벨에서 최적화
- **Python 특수사항**: Python에는 Java처럼 강제적 interface가 없으므로, `abc.ABC` + `@abstractmethod`를 사용하더라도 런타임에서만 검증됨. `mypy`나 `pyright` 같은 정적 타입 체커와 함께 사용 권장

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|------|------|----------|
| 📖 공식 원문 | Alistair Cockburn 원문 | [alistair.cockburn.us/hexagonal-architecture](https://alistair.cockburn.us/hexagonal-architecture) |
| 📘 도서 | *Hexagonal Architecture Explained* | Alistair Cockburn & Juan Manuel Garrido de Paz 공저 (2024) |
| 📖 AWS 가이드 | AWS Prescriptive Guidance | [Hexagonal Architecture Pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/hexagonal-architecture.html) |
| 📺 블로그 | Szymon Miks — Hexagonal in Python | [blog.szymonmiks.pl](https://blog.szymonmiks.pl/p/hexagonal-architecture-in-python/) |
| 📺 블로그 | Herberto Graca — Explicit Architecture | [herbertograca.com](https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/) |
| 🎓 GitHub | FastAPI Hexagonal Example | [szymon6927/hexagonal-architecture-python](https://github.com/szymon6927/hexagonal-architecture-python) |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리 | 언어/플랫폼 | 용도 |
|---------------|-----------|------|
| **FastAPI** | Python | Driving Adapter (HTTP API 프레임워크) |
| **SQLModel** | Python | Driven Adapter (ORM + Pydantic 통합) |
| **dependency-injector** | Python | 의존성 주입 컨테이너 |
| **pytest** | Python | Mock Adapter 기반 도메인 테스트 |
| **mypy / pyright** | Python | Port 인터페이스의 정적 타입 검증 |
| **pydantic** | Python | DTO/Command 객체 유효성 검증 |

### 🔮 트렌드 & 전망

- **2026년 현재**, Hexagonal Architecture는 Clean/Onion과 함께 "도메인 중심 아키텍처"의 대표 패턴으로 자리잡음 ([DEV Community](https://dev.to/dev_tips/hexagonal-vs-clean-vs-onion-which-one-actually-survives-your-app-in-2026-273f))
- **서버리스(AWS Lambda)** 환경에서도 Hexagonal 패턴이 적극 활용되는 추세 — AWS 공식 가이드에 포함
- **DDD + CQRS + Event Sourcing**과 결합하여 더 정교한 아키텍처로 발전하는 흐름
- Python 생태계에서 `FastAPI + SQLModel` 조합이 Hexagonal 구현의 인기 있는 스택으로 부상

### 💬 커뮤니티 인사이트

- "Hexagonal Architecture가 모든 곳에 필요하지는 않다. 복잡한 비즈니스 로직이 있는 모듈에만 선택적으로 적용하라" — 다수 Python 개발자 의견 ([blog.szymonmiks.pl](https://blog.szymonmiks.pl/p/hexagonal-architecture-in-python/))
- "Python에서 interface(ABC)를 강제하는 것이 Pythonic하지 않다고 느낄 수 있지만, 프로젝트가 커지면 그 가치가 증명된다" — 커뮤니티 공통 의견
- Vaughn Vernon(DDD 전문가)은 "Hexagonal Architecture에는 pitfall이 없다, 잘못 구현하는 것이 pitfall"이라고 언급 ([LinkedIn](https://www.linkedin.com/posts/vaughnvernon_hexagonal-architecture-common-pitfalls-activity-7157454786202685440-PH7x))

---

## 📎 Sources

1. [Alistair Cockburn — Hexagonal Architecture 원문](https://alistair.cockburn.us/hexagonal-architecture) — 공식 원문
2. [Wikipedia — Hexagonal Architecture](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)) — 백과사전
3. [AWS Prescriptive Guidance — Hexagonal Architecture Pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/hexagonal-architecture.html) — 공식 문서 (AWS)
4. [Netflix Tech Blog — Ready for Changes with Hexagonal Architecture](https://netflixtechblog.com/ready-for-changes-with-hexagonal-architecture-b315ec967749) — 공식 기술 블로그 (Netflix)
5. [Szymon Miks — Hexagonal Architecture in Python](https://blog.szymonmiks.pl/p/hexagonal-architecture-in-python/) — 기술 블로그
6. [DEV Community — Hexagonal vs Clean vs Onion (2026)](https://dev.to/dev_tips/hexagonal-vs-clean-vs-onion-which-one-actually-survives-your-app-in-2026-273f) — 커뮤니티
7. [Medium/Fastned — When and When Not to Use Hexagonal Architecture](https://medium.com/fastned/when-and-when-not-to-use-hexagonal-architecture-c0850d643b3b) — 기술 블로그
8. [Medium — Hexagonal Architecture Common Pitfalls](https://medium.com/@allousas/hexagonal-architecture-common-pitfalls-f155e12388a3) — 기술 블로그
9. [HappyCoders.eu — Hexagonal Architecture](https://www.happycoders.eu/software-craftsmanship/hexagonal-architecture/) — 기술 블로그
10. [Herberto Graca — DDD, Hexagonal, Onion, Clean, CQRS](https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/) — 기술 블로그
11. [Thomas Pierrain — Don't Get Lost on Your Right-Side](http://tpierrain.blogspot.com/2020/03/hexagonal-architecture-dont-get-lost-on.html) — 기술 블로그

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 7
> - 수집 출처 수: 11
> - 출처 유형: 공식 4 (Cockburn 원문, Wikipedia, AWS, Netflix Tech Blog), 블로그 5, 커뮤니티 1, SNS 1
>
> 🔍 **Convergence Verification (2026-03-22)**
> - 검증 라운드: 1회 (수렴 완료)
> - 검증 항목: 정확성(Accuracy), 완전성(Completeness), 일관성(Consistency), 기술 정확성(Technical Correctness), 출처 품질(Source Quality)
> - 수정 사항:
>   - Cockburn 타임라인: "2002년경 Port 개념 인식" → "이후 디자인 패턴 학습 과정에서 Port 개념 인식, 2005년 공식 개명"으로 수정 (원문 기반 팩트체크)
>   - Netflix 출처: HappyCoders.eu(3rd-party) → Netflix Tech Blog(1st-party)로 교체, JSON→GraphQL 마이그레이션 사례 추가
>   - Spotify 사례: 1st-party 출처 부재 명시 (3rd-party 기반 주의 표시 추가)
>   - Sources: Netflix Tech Blog 추가 (10개 → 11개)
> - 검증 결과: PASS (정확성 보강 완료, 미검증 주장에 경고 표시 추가)
