---
created: 2026-03-22
source: claude-code
tags: [architecture, python, fastapi, sqlmodel, ddd, clean-architecture, layered-architecture, hexagonal-architecture, ports-and-adapters, comparison]
---

# 🏗️ 4대 아키텍처 통합 비교 — DDD, Layered, Clean, Hexagonal

> 💡 **한줄 요약**: DDD는 "무엇을 모델링할 것인가"의 **철학**, Layered/Clean/Hexagonal은 "어떻게 구조화할 것인가"의 **패턴**이다. 이들은 상호 배타적이 아니라 **조합하여 사용**하는 것이 실무의 정석이다.

---

## 📋 목차

1. [4대 아키텍처 한눈에 보기](#1-4대-아키텍처-한눈에-보기)
2. [Case별 아키텍처 선택 가이드](#2-case별-아키텍처-선택-가이드)
3. [Port And Adapter의 독립성 검증](#3-port-and-adapter의-독립성-검증)
4. [DDD vs Clean vs Layered 관계 검증](#4-ddd-vs-clean-vs-layered-관계-검증)
5. [동일 도메인 3가지 구현 비교](#5-동일-도메인-3가지-구현-비교)
6. [실무 조합 가이드](#6-실무-조합-가이드)

---

## 1. 4대 아키텍처 한눈에 보기

```
┌─────────────────────────────────────────────────────────────────┐
│                    4대 아키텍처 관계도                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │            DDD (Domain-Driven Design)                   │   │
│   │            유형: 설계 철학 + 방법론                         │   │
│   │            초점: "무엇을 모델링할 것인가"                    │   │
│   │                                                         │   │
│   │   ┌───────────┐  ┌───────────┐  ┌─────────────────┐    │   │
│   │   │  Layered   │  │   Clean   │  │   Hexagonal     │    │   │
│   │   │  수평 레이어 │  │ 동심원 규칙 │  │  Port & Adapter │    │   │
│   │   │  구조 패턴  │  │  구조 패턴  │  │   경계 패턴      │    │   │
│   │   └───────────┘  └───────────┘  └─────────────────┘    │   │
│   │         ↑               ↑               ↑               │   │
│   │         └───────────────┼───────────────┘               │   │
│   │                DDD가 내부를 채울 수 있음                    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📊 핵심 비교 매트릭스

| 비교 기준 | DDD | Layered | Clean | Hexagonal |
| --- | --- | --- | --- | --- |
| **유형** | 철학 + 방법론 | 구조 패턴 | 구조 패턴 | 경계 패턴 |
| **창시자** | Eric Evans (2003) | POSA (1996) / Fowler (2002) | Robert C. Martin (2012) | Alistair Cockburn (2005) |
| **핵심 질문** | 무엇을 모델링? | 어떻게 레이어를 나눌까? | 의존성 방향은? | 외부와 내부를 어떻게 분리? |
| **초점** | 도메인 복잡성 관리 | 관심사의 수평 분리 | 의존성 규칙 (안→밖) | 외부 기술과의 결합 제거 |
| **비즈니스 로직 위치** | Aggregate/Entity 내부 | Service Layer | Entity + Use Case | Domain (hexagon 내부) |
| **의존성 방향** | 미지정 (자유) | 위→아래 (단방향) | 밖→안 (동심원) | 밖→안 (Adapter→Port) |
| **도메인 전문가 필요** | 필수 | 불필요 | 선택 | 선택 |
| **학습 곡선** | 가파름 | 낮음 | 중간 | 중간 |
| **최소 적용 규모** | 복잡한 도메인 | 모든 규모 | 중규모 이상 | 외부 연동 多 |
| **단독 사용 가능** | ❌ (구조 패턴 필요) | ✅ | ✅ | ⚠️ (내부 구조 보완 권장) |

---

## 2. Case별 아키텍처 선택 가이드

### 🔀 의사결정 플로우차트

```
[프로젝트 시작]
    │
    ▼
비즈니스 로직이 복잡한가? ──── No ──── 단순 CRUD인가? ──── Yes ──→ Layered (Basic)
    │                                      │
   Yes                                     No
    │                                      │
    ▼                                      ▼
도메인 전문가 협업 가능? ──── No ────→ Clean Architecture
    │                                (Use Case 중심 설계)
   Yes
    │
    ▼
외부 시스템 연동이 많은가? ──── Yes ──→ DDD + Hexagonal + Clean
    │                               (최적 조합)
    No
    │
    ▼
DDD + Layered 또는 DDD + Clean
(도메인 중심 + 적절한 구조)
```

### 📋 프로젝트 유형별 추천

| 프로젝트 유형 | 규모 | 추천 아키텍처 | 이유 |
| --- | --- | --- | --- |
| **사내 관리 도구** | 소규모 | Layered | CRUD 위주, 빠른 개발 우선 |
| **MVP / 프로토타입** | 소규모 | Layered | 구조보다 속도, 추후 리팩토링 |
| **SaaS B2B 서비스** | 중규모 | Clean + DDD | 복잡한 비즈니스 규칙, 장기 유지보수 |
| **이커머스 플랫폼** | 대규모 | DDD + Hexagonal + Clean | 다수 Bounded Context, 외부 연동 多 |
| **핀테크 / 금융** | 대규모 | DDD + Hexagonal | 정확한 도메인 모델링 필수, 규제 준수 |
| **마이크로서비스** | 대규모 | DDD + Hexagonal | Bounded Context = 서비스 경계 |
| **API Gateway / BFF** | 중규모 | Hexagonal | 다양한 외부 어댑터 관리 |
| **데이터 파이프라인** | 중규모 | Layered 또는 Clean | 도메인보다 흐름/변환 중심 |

### 🏢 팀 구성별 추천

| 팀 상황 | 추천 | 이유 |
| --- | --- | --- |
| 1인 개발자, 빠른 출시 | Layered | 오버헤드 최소화 |
| 주니어 중심 팀 (3-5명) | Layered → Clean 점진적 도입 | 학습 곡선 고려 |
| 시니어 포함 팀 (5-10명) | Clean + DDD | 도메인 복잡도 관리 가능 |
| 도메인 전문가 + 개발팀 | DDD + Hexagonal | DDD의 본래 의도에 최적 |
| 여러 팀이 하나의 제품 | DDD (Strategic Design) | Bounded Context로 팀 경계 설정 |

---

## 3. Port And Adapter의 독립성 검증

### 🔍 검증 대상 주장

> "Port And Adapter만으로는 완전한 아키텍처가 아니다. Domain 영역은 결국 Layered/Clean/DDD가 필요하다"

### ✅ 검증 결과: **대체로 맞다 (조건부 동의)**

#### Hexagonal이 정의하는 것 vs 정의하지 않는 것

| 구분 | Hexagonal이 정의 | 설명 |
| --- | --- | --- |
| ✅ 정의함 | 외부↔내부 경계 | Application과 외부 세계 사이의 명확한 경계선 |
| ✅ 정의함 | Port (인터페이스) | 애플리케이션이 외부와 소통하는 계약 |
| ✅ 정의함 | Adapter (구현체) | Port를 기술적으로 구현하는 컴포넌트 |
| ✅ 정의함 | 의존성 방향 | Adapter → Port (외부가 내부에 의존) |
| ❌ 정의 안 함 | Domain 내부 구조 | Entity, VO, Aggregate 등의 설계 방법 |
| ❌ 정의 안 함 | Application Layer 조직 | Use Case 분리, Service 구성 방법 |
| ❌ 정의 안 함 | 도메인 모델링 방법론 | 어떻게 비즈니스를 코드로 표현할지 |

#### 현실 세계 비유

Hexagonal은 **"집의 벽과 창문(인터페이스)"**을 설계하는 것이다. 벽과 창문이 있으면 외부(비, 바람)로부터 내부를 보호할 수 있지만, **방 내부의 가구 배치(Domain 구조)**는 별도로 결정해야 한다.

- 작은 원룸이면? → 가구 배치를 정교하게 계획할 필요 없음 (소규모 프로젝트에 Hexagonal만으로 충분)
- 3층 집이면? → 층별 용도, 동선, 배관 설계가 필수 (대규모에는 DDD/Clean으로 내부 구조화 필요)

#### 근거: Cockburn 원문

Cockburn의 2005년 원문에서 Hexagonal Architecture는 "Allow an application to equally be driven by users, programs, automated test or batch scripts, and to be developed and tested in isolation from its eventual run-time devices and databases"를 목표로 한다. **Domain 내부 설계는 명시적 범위 밖이다.**

#### 결론 테이블

| 상황 | Hexagonal 단독 사용 | DDD/Clean 보완 필요 |
| --- | --- | --- |
| 소규모, 단순 도메인 | ✅ 충분 | ❌ 과잉 |
| 중규모, 보통 복잡도 | ⚠️ 가능하나 아쉬움 | ✅ 권장 (Clean) |
| 대규모, 복잡한 도메인 | ❌ 내부 혼란 | ✅ 필수 (DDD) |

### 💻 코드 예시: Hexagonal + DDD 조합 구현

**핵심 포인트**: Hexagonal이 경계(Port/Adapter)를, DDD가 내부(Domain Model)를 담당하는 조합

```python
# ========================
# 1. Domain Layer (DDD가 담당)
# ========================

# domain/value_objects.py
from pydantic import BaseModel, field_validator


class Money(BaseModel):
    """DDD Value Object: 불변, 속성값으로 동등성 판단"""
    amount: int
    currency: str = "KRW"

    @field_validator("amount")
    @classmethod
    def must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("금액은 0 이상이어야 합니다")
        return v


# domain/entities.py
import uuid
from datetime import datetime, timezone
from enum import Enum

from domain.value_objects import Money


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class Order:
    """DDD Aggregate Root: 비즈니스 규칙을 캡슐화"""

    def __init__(
        self,
        customer_id: str,
        total: Money,
        order_id: str | None = None,
        created_at: datetime | None = None,
    ):
        self.order_id = order_id or str(uuid.uuid4())
        self.customer_id = customer_id
        self.total = total
        self.status = OrderStatus.PENDING
        self.created_at = created_at or datetime.now(timezone.utc)

    def confirm(self) -> None:
        """비즈니스 규칙: PENDING만 확정 가능"""
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"PENDING 상태에서만 확정 가능 (현재: {self.status})")
        self.status = OrderStatus.CONFIRMED

    def cancel(self) -> None:
        """비즈니스 규칙: CONFIRMED 이후 취소 불가"""
        if self.status != OrderStatus.PENDING:
            raise ValueError("PENDING 상태에서만 취소 가능")
        self.status = OrderStatus.CANCELLED
```

```python
# ========================
# 2. Ports (Hexagonal이 담당 — 경계 인터페이스)
# ========================

# ports/order_repository_port.py
from abc import ABC, abstractmethod
from domain.entities import Order


class OrderRepositoryPort(ABC):
    """Driven Port: 도메인이 외부 저장소에 요구하는 계약"""

    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def find_by_id(self, order_id: str) -> Order | None: ...


# ports/notification_port.py
from abc import ABC, abstractmethod


class NotificationPort(ABC):
    """Driven Port: 도메인이 알림 시스템에 요구하는 계약"""

    @abstractmethod
    def send_order_confirmed(self, order_id: str, customer_id: str) -> None: ...
```

```python
# ========================
# 3. Application Service (DDD Use Case + Hexagonal Port 조합)
# ========================

# application/confirm_order.py
from ports.order_repository_port import OrderRepositoryPort
from ports.notification_port import NotificationPort


class ConfirmOrderUseCase:
    """Port만 의존 — 구체적 기술(DB, 이메일)을 모름"""

    def __init__(
        self,
        order_repo: OrderRepositoryPort,
        notifier: NotificationPort,
    ):
        self.order_repo = order_repo
        self.notifier = notifier

    def execute(self, order_id: str) -> dict:
        order = self.order_repo.find_by_id(order_id)
        if not order:
            raise ValueError(f"주문 없음: {order_id}")

        order.confirm()  # DDD: 도메인 로직은 Aggregate 내부에서 실행
        self.order_repo.save(order)
        self.notifier.send_order_confirmed(order.order_id, order.customer_id)

        return {"order_id": order.order_id, "status": order.status.value}
```

```python
# ========================
# 4. Adapters (Hexagonal이 담당 — 기술 구현)
# ========================

# adapters/sqlmodel_order_repository.py
from datetime import datetime

from sqlmodel import Session, SQLModel, Field, select
from domain.entities import Order, OrderStatus
from domain.value_objects import Money
from ports.order_repository_port import OrderRepositoryPort


class OrderModel(SQLModel, table=True):
    """SQLModel 테이블: Infrastructure 전용, Domain과 분리"""
    __tablename__ = "orders"
    order_id: str = Field(primary_key=True)
    customer_id: str = Field(index=True)
    status: str
    total_amount: int
    currency: str = "KRW"
    created_at: datetime | None = None


class SQLModelOrderRepository(OrderRepositoryPort):
    """Driven Adapter: Port를 SQLModel로 구현"""

    def __init__(self, session: Session):
        self.session = session

    def save(self, order: Order) -> None:
        model = OrderModel(
            order_id=order.order_id,
            customer_id=order.customer_id,
            status=order.status.value,
            total_amount=order.total.amount,
            currency=order.total.currency,
            created_at=order.created_at,
        )
        self.session.merge(model)
        self.session.commit()

    def find_by_id(self, order_id: str) -> Order | None:
        stmt = select(OrderModel).where(OrderModel.order_id == order_id)
        model = self.session.exec(stmt).first()
        if not model:
            return None
        order = Order(
            customer_id=model.customer_id,
            total=Money(amount=model.total_amount, currency=model.currency),
            order_id=model.order_id,
            created_at=model.created_at,
        )
        order.status = OrderStatus(model.status)
        return order


# adapters/email_notification.py
from ports.notification_port import NotificationPort


class EmailNotificationAdapter(NotificationPort):
    """Driven Adapter: 알림 Port를 이메일로 구현"""

    def send_order_confirmed(self, order_id: str, customer_id: str) -> None:
        print(f"[Email] 주문 {order_id} 확정 알림 → {customer_id}")
```

```python
# ========================
# 5. Driving Adapter (FastAPI Router)
# ========================

# adapters/fastapi_router.py
from fastapi import APIRouter, Depends
from sqlmodel import Session

from application.confirm_order import ConfirmOrderUseCase
from adapters.sqlmodel_order_repository import SQLModelOrderRepository
from adapters.email_notification import EmailNotificationAdapter

router = APIRouter(prefix="/orders", tags=["Orders"])


def get_session():
    from database import engine
    with Session(engine) as session:
        yield session


def get_confirm_use_case(session: Session = Depends(get_session)):
    repo = SQLModelOrderRepository(session)
    notifier = EmailNotificationAdapter()
    return ConfirmOrderUseCase(order_repo=repo, notifier=notifier)


@router.post("/{order_id}/confirm")
def confirm_order(
    order_id: str,
    use_case: ConfirmOrderUseCase = Depends(get_confirm_use_case),
):
    return use_case.execute(order_id)
```

**이 코드에서 역할 분담:**

| 구성 요소 | 담당 | 역할 |
| --- | --- | --- |
| `Order` (Aggregate), `Money` (VO) | **DDD** | 비즈니스 규칙 캡슐화 |
| `OrderRepositoryPort`, `NotificationPort` | **Hexagonal** | 외부↔내부 경계 정의 |
| `ConfirmOrderUseCase` | **DDD + Hexagonal** | Use Case 조율, Port만 의존 |
| `SQLModelOrderRepository`, `EmailNotificationAdapter` | **Hexagonal** | 기술 구현 |
| `fastapi_router` | **Hexagonal** | Driving Adapter |

---

## 4. DDD vs Clean vs Layered 관계 검증

### 🔍 검증 대상 주장

> "DDD로 Clean Architecture의 Domain 영역을 구현하고, Layered Architecture의 Service Layer를 구현할 수 있다"

### ✅ 검증 결과: **정확하다**

#### 논리적 근거

```
┌─────────────────────────────────────────────────────────────────┐
│                      관계도 시각화                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DDD (설계 철학)                                                  │
│  ├── Strategic Design → 시스템 경계 설정                           │
│  │     "Bounded Context, Context Map"                            │
│  │                                                               │
│  └── Tactical Design → 내부 구조 채우기                            │
│        "Entity, VO, Aggregate, Repository, Domain Service"       │
│                                                                 │
│        ┌─────────────────┐    ┌─────────────────┐               │
│        │ Clean Arch       │    │ Layered Arch     │               │
│        │                 │    │                  │               │
│        │ Entities Layer  │    │ Domain Layer     │               │
│        │   ← DDD 충전 → │    │   ← DDD 충전 →  │               │
│        │                 │    │                  │               │
│        │ Use Cases Layer │    │ Service Layer    │               │
│        │   ← DDD App    │    │   ← DDD App     │               │
│        │     Service →   │    │     Service →   │               │
│        └─────────────────┘    └─────────────────┘               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

| DDD 요소 | Clean Architecture 대응 | Layered Architecture 대응 |
| --- | --- | --- |
| **Entity / Aggregate** | Entities Layer (innermost) | Domain Layer (Model) |
| **Value Object** | Entities Layer | Domain Layer (Model) |
| **Repository Interface** | Interface Adapters 경계 | Domain Layer에 정의 |
| **Application Service** | Use Cases Layer | Service Layer |
| **Domain Service** | Entities Layer | Domain Layer 또는 Service Layer |
| **Domain Event** | Entities Layer | Domain Layer |

#### 핵심 통찰

1. **DDD는 "빈 칸을 채우는 도구"다**: Clean/Layered가 빈 레이어 상자를 제공하면, DDD가 그 안에 의미 있는 도메인 모델을 채운다.

2. **Clean/Layered 없이 DDD만 쓸 수 없다**: DDD는 코드 구조를 지정하지 않으므로, 반드시 구조 패턴(Layered, Clean, Hexagonal)과 조합해야 한다.

3. **DDD 없이 Clean/Layered는 "빈 껍데기"가 될 수 있다**: 구조만 있고 도메인 모델이 빈약하면 Anemic Domain Model이 되기 쉽다.

---

## 5. 동일 도메인 3가지 구현 비교

동일한 "주문 확정(Confirm Order)" 기능을 Layered, Clean, DDD+Hexagonal로 각각 구현하여 구조 차이를 직접 비교한다.

### 🅰️ Layered Architecture 구현

**특징**: 비즈니스 로직이 **Service Layer**에 위치, 모델은 데이터 컨테이너

```python
# ========== Layered Architecture ==========

# models/order.py — 데이터 모델 (SQLModel = Domain + Persistence 합침)
from sqlmodel import SQLModel, Field


class Order(SQLModel, table=True):
    __tablename__ = "orders"
    order_id: str = Field(primary_key=True)
    customer_id: str
    status: str = "PENDING"
    total_amount: int = 0


# repositories/order_repository.py — Data Access Layer
from sqlmodel import Session, select
from models.order import Order


class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, order_id: str) -> Order | None:
        return self.session.exec(
            select(Order).where(Order.order_id == order_id)
        ).first()

    def save(self, order: Order) -> None:
        self.session.merge(order)
        self.session.commit()


# services/order_service.py — ⭐ 비즈니스 로직이 여기에 집중
from repositories.order_repository import OrderRepository


class OrderService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    def confirm_order(self, order_id: str) -> Order:
        order = self.repo.find_by_id(order_id)
        if not order:
            raise ValueError(f"주문 없음: {order_id}")

        # ⭐ 비즈니스 규칙이 Service에 있음 (Anemic Model)
        if order.status != "PENDING":
            raise ValueError(f"PENDING만 확정 가능 (현재: {order.status})")
        order.status = "CONFIRMED"

        self.repo.save(order)
        return order


# routers/order_router.py — Presentation Layer
from fastapi import APIRouter, Depends
from sqlmodel import Session
from services.order_service import OrderService
from repositories.order_repository import OrderRepository

router = APIRouter(prefix="/orders")


def get_service(session: Session = Depends(get_session)):
    repo = OrderRepository(session)
    return OrderService(repo)


@router.post("/{order_id}/confirm")
def confirm(order_id: str, svc: OrderService = Depends(get_service)):
    order = svc.confirm_order(order_id)
    return {"order_id": order.order_id, "status": order.status}
```

### 🅱️ Clean Architecture 구현

**특징**: **의존성 역전**, Entity에 로직, Use Case가 조율

```python
# ========== Clean Architecture ==========

# entities/order.py — ⭐ 프레임워크 무의존, 순수 Python
class Order:
    def __init__(self, order_id: str, customer_id: str, total_amount: int):
        self.order_id = order_id
        self.customer_id = customer_id
        self.total_amount = total_amount
        self.status = "PENDING"

    def confirm(self) -> None:
        # ⭐ 비즈니스 규칙이 Entity 내부
        if self.status != "PENDING":
            raise ValueError(f"PENDING만 확정 가능 (현재: {self.status})")
        self.status = "CONFIRMED"


# use_cases/interfaces.py — Use Case가 요구하는 인터페이스 (의존성 역전)
from abc import ABC, abstractmethod
from entities.order import Order


class OrderRepositoryInterface(ABC):
    @abstractmethod
    def find_by_id(self, order_id: str) -> Order | None: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...


# use_cases/confirm_order.py — Application 규칙
from use_cases.interfaces import OrderRepositoryInterface


class ConfirmOrderUseCase:
    def __init__(self, repo: OrderRepositoryInterface):
        self.repo = repo

    def execute(self, order_id: str) -> dict:
        order = self.repo.find_by_id(order_id)
        if not order:
            raise ValueError(f"주문 없음: {order_id}")

        order.confirm()  # ⭐ Entity에게 위임
        self.repo.save(order)
        return {"order_id": order.order_id, "status": order.status}


# infrastructure/sqlmodel_repo.py — Interface Adapter (의존성 방향: 밖→안)
from sqlmodel import Session, SQLModel, Field, select
from entities.order import Order as DomainOrder
from use_cases.interfaces import OrderRepositoryInterface


class OrderModel(SQLModel, table=True):
    __tablename__ = "orders"
    order_id: str = Field(primary_key=True)
    customer_id: str
    status: str = "PENDING"
    total_amount: int = 0


class SQLModelOrderRepository(OrderRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, order_id: str) -> DomainOrder | None:
        model = self.session.exec(
            select(OrderModel).where(OrderModel.order_id == order_id)
        ).first()
        if not model:
            return None
        # ⭐ DB 모델 → Domain 모델 변환
        order = DomainOrder(model.order_id, model.customer_id, model.total_amount)
        order.status = model.status
        return order

    def save(self, order: DomainOrder) -> None:
        model = OrderModel(
            order_id=order.order_id,
            customer_id=order.customer_id,
            status=order.status,
            total_amount=order.total_amount,
        )
        self.session.merge(model)
        self.session.commit()


# frameworks/fastapi_router.py — Frameworks & Drivers (가장 바깥 원)
from fastapi import APIRouter, Depends
from sqlmodel import Session
from use_cases.confirm_order import ConfirmOrderUseCase
from infrastructure.sqlmodel_repo import SQLModelOrderRepository

router = APIRouter(prefix="/orders")


def get_use_case(session: Session = Depends(get_session)):
    repo = SQLModelOrderRepository(session)
    return ConfirmOrderUseCase(repo)


@router.post("/{order_id}/confirm")
def confirm(order_id: str, uc: ConfirmOrderUseCase = Depends(get_use_case)):
    return uc.execute(order_id)
```

### 🅲️ DDD + Hexagonal 구현

**특징**: Rich Domain Model + Port/Adapter 경계 + Value Object

```python
# ========== DDD + Hexagonal Architecture ==========

# domain/value_objects.py — ⭐ DDD Value Object
from pydantic import BaseModel, field_validator


class Money(BaseModel):
    amount: int
    currency: str = "KRW"

    @field_validator("amount")
    @classmethod
    def must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("금액은 0 이상")
        return v


# domain/order.py — ⭐ DDD Aggregate Root (Rich Domain Model)
import uuid
from datetime import datetime, timezone
from enum import Enum
from domain.value_objects import Money


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class Order:
    def __init__(
        self,
        customer_id: str,
        total: Money,
        order_id: str | None = None,
        created_at: datetime | None = None,
    ):
        self.order_id = order_id or str(uuid.uuid4())
        self.customer_id = customer_id
        self.total = total  # ⭐ Value Object 사용 (Primitive Obsession 방지)
        self.status = OrderStatus.PENDING
        self.created_at = created_at or datetime.now(timezone.utc)
        self._events: list[dict] = []

    def confirm(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"PENDING만 확정 가능 (현재: {self.status})")
        self.status = OrderStatus.CONFIRMED
        # ⭐ Domain Event 발행
        self._events.append({
            "type": "OrderConfirmed",
            "order_id": self.order_id,
            "confirmed_at": datetime.now(timezone.utc).isoformat(),
        })

    def collect_events(self) -> list[dict]:
        events = self._events.copy()
        self._events.clear()
        return events


# ports/order_repository_port.py — ⭐ Hexagonal Port (경계 인터페이스)
from abc import ABC, abstractmethod
from domain.order import Order


class OrderRepositoryPort(ABC):
    @abstractmethod
    def find_by_id(self, order_id: str) -> Order | None: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...


# application/confirm_order.py — DDD Application Service
from ports.order_repository_port import OrderRepositoryPort


class ConfirmOrderUseCase:
    def __init__(self, repo: OrderRepositoryPort):
        self.repo = repo

    def execute(self, order_id: str) -> dict:
        order = self.repo.find_by_id(order_id)
        if not order:
            raise ValueError(f"주문 없음: {order_id}")

        order.confirm()  # ⭐ Rich Domain Model
        self.repo.save(order)

        # ⭐ Domain Event 수집 (이벤트 기반 후처리 가능)
        events = order.collect_events()
        return {
            "order_id": order.order_id,
            "status": order.status.value,
            "events": events,
        }


# adapters/sqlmodel_adapter.py — ⭐ Hexagonal Adapter (기술 구현)
from datetime import datetime

from sqlmodel import Session, SQLModel, Field, select
from domain.order import Order, OrderStatus
from domain.value_objects import Money
from ports.order_repository_port import OrderRepositoryPort


class OrderModel(SQLModel, table=True):
    __tablename__ = "orders"
    order_id: str = Field(primary_key=True)
    customer_id: str
    status: str
    total_amount: int
    currency: str = "KRW"
    created_at: datetime | None = None


class SQLModelOrderAdapter(OrderRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, order_id: str) -> Order | None:
        model = self.session.exec(
            select(OrderModel).where(OrderModel.order_id == order_id)
        ).first()
        if not model:
            return None
        order = Order(
            customer_id=model.customer_id,
            total=Money(amount=model.total_amount, currency=model.currency),
            order_id=model.order_id,
            created_at=model.created_at,
        )
        order.status = OrderStatus(model.status)
        return order

    def save(self, order: Order) -> None:
        model = OrderModel(
            order_id=order.order_id,
            customer_id=order.customer_id,
            status=order.status.value,
            total_amount=order.total.amount,
            currency=order.total.currency,
            created_at=order.created_at,
        )
        self.session.merge(model)
        self.session.commit()


# adapters/fastapi_router.py — Hexagonal Driving Adapter
from fastapi import APIRouter, Depends
from sqlmodel import Session
from application.confirm_order import ConfirmOrderUseCase
from adapters.sqlmodel_adapter import SQLModelOrderAdapter

router = APIRouter(prefix="/orders")


def get_use_case(session: Session = Depends(get_session)):
    repo = SQLModelOrderAdapter(session)
    return ConfirmOrderUseCase(repo)


@router.post("/{order_id}/confirm")
def confirm(order_id: str, uc: ConfirmOrderUseCase = Depends(get_use_case)):
    return uc.execute(order_id)
```

### 📊 3가지 구현 핵심 차이 비교

| 비교 포인트 | 🅰️ Layered | 🅱️ Clean | 🅲️ DDD + Hexagonal |
| --- | --- | --- | --- |
| **비즈니스 로직 위치** | Service Layer | Entity + Use Case | Aggregate Root |
| **Domain 모델 유형** | Anemic (데이터만) | 반-Rich (일부 로직) | Rich (로직 + 이벤트) |
| **DB 모델과 Domain 분리** | ❌ 합쳐짐 (SQLModel) | ✅ 분리 | ✅ 분리 + Value Object |
| **의존성 방향** | 위→아래 (직접 참조) | 밖→안 (인터페이스) | 밖→안 (Port/Adapter) |
| **테스트 용이성** | 낮음 (DB 의존) | 높음 (Mock 가능) | 높음 (Port Mock) |
| **프레임워크 의존** | 높음 (SQLModel 전체 침투) | 낮음 (Entity 독립) | 낮음 (Domain 독립) |
| **코드량** | 적음 (~40줄) | 중간 (~70줄) | 많음 (~100줄) |
| **Value Object 사용** | ❌ 원시 타입 | ❌ 원시 타입 | ✅ Money 등 |
| **Domain Event** | ❌ 없음 | ❌ 없음 | ✅ 있음 |
| **적합한 규모** | 소규모 CRUD | 중규모 | 대규모 복잡 도메인 |

---

## 6. 실무 조합 가이드

### 🏆 추천 조합 (검증된 패턴)

| 순위 | 조합 | 적합한 상황 | 실무 빈도 |
| --- | --- | --- | --- |
| 1 | **DDD + Hexagonal** | 복잡한 도메인 + 외부 연동 多 | 가장 많음 |
| 2 | **Clean + DDD** | 복잡한 도메인 + 프레임워크 교체 가능성 | 많음 |
| 3 | **Layered (단독)** | 단순 CRUD, 빠른 개발 | 많음 |
| 4 | **DDD + Hexagonal + Clean** | 대규모 엔터프라이즈 | 드물지만 이상적 |
| 5 | **Clean (단독)** | 중규모, DDD 학습 전 단계 | 보통 |

### ⚠️ 피해야 할 조합

| 조합 | 이유 |
| --- | --- |
| DDD + 단순 CRUD | 오버엔지니어링. Aggregate, VO가 불필요한 복잡도 추가 |
| Hexagonal + MVP | Port/Adapter 추상화가 속도를 저해. Layered로 시작 후 점진적 전환 |
| 4개 모두 한꺼번에 도입 | 학습 곡선 폭발. Layered → Clean → Hexagonal → DDD 순서로 점진적 학습 |

### 📈 성장 경로 (점진적 도입)

```
Stage 1: Layered Architecture
  └── 관심사 분리의 기본을 익힘
  └── 한계 체감: "Service가 너무 뚱뚱해졌다"

Stage 2: Clean Architecture
  └── 의존성 역전 학습, Entity에 로직 이동
  └── 한계 체감: "Domain 모델링이 빈약하다"

Stage 3: DDD Tactical Design
  └── Entity, VO, Aggregate로 풍부한 도메인 모델
  └── 한계 체감: "외부 시스템 교체가 어렵다"

Stage 4: Hexagonal + DDD
  └── Port/Adapter로 외부 의존성 완전 분리
  └── 최종 목표: 비즈니스 로직에 집중할 수 있는 코드베이스
```

---

## 📎 Sources

1. [Hexagonal Architecture - Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/) — 창시자 원문
2. [The Clean Architecture - Robert C. Martin (Uncle Bob)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) — 창시자 원문
3. [Domain-Driven Design Reference - Eric Evans](https://www.domainlanguage.com/ddd/) — 공식 참조
4. [Pattern-Oriented Software Architecture (POSA) Volume 1](https://en.wikipedia.org/wiki/Pattern-Oriented_Software_Architecture) — Layered 패턴 원전
5. [Patterns of Enterprise Application Architecture - Martin Fowler](https://martinfowler.com/eaaCatalog/) — Layered/Service Layer 정의
6. [DDD, Hexagonal, Onion, Clean, CQRS - Herberto Graca](https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/) — 통합 아키텍처 분석
7. [Ready for changes with Hexagonal Architecture - Netflix Tech Blog](https://netflixtechblog.com/ready-for-changes-with-hexagonal-architecture-b315ec967749) — 실무 사례

---

> 🔬 **Research Metadata**
> - 기반 문서: 4개 concept-explainer 리포트 (DDD, Layered, Clean, Hexagonal)
> - 검증 완료: rl-verify 수렴 검증 (Tier 2, 2 iterations, 8 findings — 4 CONFIRMED, 4 LIKELY)
> - 코드 스택: Python + FastAPI + SQLModel
> - 작성일: 2026-03-22
> - 검증일: 2026-03-22
> - 검증 리포트: `docs/verify-architecture-integrated-comparison/report.md`
> - 검증 후 수정: import 누락 보완, Order 생성자 개선 (재구성 지원), created_at 영속화 추가
