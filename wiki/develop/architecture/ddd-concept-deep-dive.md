---
created: 2026-03-22
source: claude-code
tags: [architecture, python, fastapi, sqlmodel, ddd, domain-driven-design]
---

# 📖 Domain-Driven Design (DDD) — Concept Deep Dive

> 💡 **한줄 요약**: DDD는 복잡한 비즈니스 도메인을 소프트웨어 설계의 중심에 두고, 도메인 전문가와 개발자가 **공통 언어(Ubiquitous Language)**를 사용하여 협업하는 소프트웨어 설계 접근법이다.

---

## 1️⃣ 무엇인가? (What is it?)

**Domain-Driven Design(DDD)**은 2003년 Eric Evans가 저서 *"Domain-Driven Design: Tackling Complexity in the Heart of Software"*에서 제시한 소프트웨어 설계 접근법이다.

Eric Evans의 공식 정의에 따르면, DDD는 복잡한 소프트웨어 개발에서 다음을 수행하는 접근법이다:
1. **핵심 도메인(Core Domain)**에 집중한다
2. 도메인 실무자와 소프트웨어 실무자가 **창조적 협업**으로 모델을 탐구한다
3. 명시적으로 정의된 **Bounded Context** 안에서 **Ubiquitous Language**를 사용한다

DDD가 탄생한 배경은 간단하다. 현실 세계의 비유로 설명하면, 마치 **건축가가 집을 지을 때** 거주자(도메인 전문가)의 생활 패턴을 이해하지 못한 채 설계하면 불편한 집이 되는 것처럼, 소프트웨어도 비즈니스 도메인을 제대로 이해하지 못하면 쓸모없는 시스템이 된다. DDD는 이 **"비즈니스 현실과 코드 사이의 간극"**을 메우기 위해 등장했다.

> 📌 **핵심 키워드**: `Ubiquitous Language`, `Bounded Context`, `Aggregate`, `Entity`, `Value Object`, `Repository`, `Domain Event`

---

## 2️⃣ 핵심 개념 (Core Concepts)

DDD는 크게 **Strategic Design(전략적 설계)**과 **Tactical Design(전술적 설계)** 두 축으로 나뉜다.

```
┌─────────────────────────────────────────────────────────────┐
│                  🏗️  DDD 핵심 구조                          │
├──────────────────────────┬──────────────────────────────────┤
│   Strategic Design       │     Tactical Design              │
│   (큰 그림, 경계 설정)    │     (코드 수준, 빌딩 블록)        │
│                          │                                  │
│  ┌──────────────────┐    │    ┌──────────────────┐          │
│  │ Bounded Context  │    │    │ Entity           │          │
│  ├──────────────────┤    │    ├──────────────────┤          │
│  │ Ubiquitous       │    │    │ Value Object     │          │
│  │ Language          │    │    ├──────────────────┤          │
│  ├──────────────────┤    │    │ Aggregate        │          │
│  │ Context Map      │    │    ├──────────────────┤          │
│  ├──────────────────┤    │    │ Repository       │          │
│  │ Subdomain        │    │    ├──────────────────┤          │
│  │ (Core/Supporting/│    │    │ Domain Service   │          │
│  │  Generic)        │    │    ├──────────────────┤          │
│  └──────────────────┘    │    │ Domain Event     │          │
│                          │    ├──────────────────┤          │
│                          │    │ Factory          │          │
│                          │    └──────────────────┘          │
└──────────────────────────┴──────────────────────────────────┘
```

| 구성 요소 | 유형 | 역할 | 비유 |
|-----------|------|------|------|
| **Ubiquitous Language** | Strategic | 개발자·도메인 전문가가 공유하는 공통 언어 | 같은 교실에서 같은 교과서를 쓰는 것 |
| **Bounded Context** | Strategic | 모델이 유효한 명시적 경계 | 나라마다 다른 법률 체계 |
| **Entity** | Tactical | 고유 식별자를 가진 객체 | 주민등록번호가 있는 사람 |
| **Value Object** | Tactical | 식별자 없이 속성값으로 정의되는 불변 객체 | 지폐의 금액 (만원은 만원) |
| **Aggregate** | Tactical | Entity와 Value Object의 일관성 단위 묶음 | 쇼핑 카트 (카트 + 상품들) |
| **Repository** | Tactical | Aggregate의 영속성을 추상화하는 인터페이스 | 도서관의 검색 시스템 |
| **Domain Service** | Tactical | Entity/VO에 속하지 않는 도메인 로직 | 은행의 이체 처리 담당자 |
| **Domain Event** | Tactical | 도메인에서 발생한 중요 사건을 표현 | "주문이 완료됨" 알림 |
| **Factory** | Tactical | 복잡한 Aggregate/Entity 생성 로직을 캡슐화 | 자동차 공장의 조립 라인 |

### 🗺️ Strategic Design 상세

**Subdomain 유형:**

| 유형 | 설명 | 비유 | 투자 우선순위 |
|------|------|------|-------------|
| **Core Subdomain** | 비즈니스 핵심 경쟁력. 직접 개발 필수 | 레스토랑의 시그니처 레시피 | 최고 |
| **Supporting Subdomain** | 핵심은 아니지만 비즈니스 운영에 필요 | 레스토랑의 예약 시스템 | 중간 |
| **Generic Subdomain** | 범용적 문제. 외부 솔루션 활용 가능 | 레스토랑의 회계 시스템 | 낮음 (구매/위임) |

**Context Map 패턴 (Bounded Context 간 관계):**

| 패턴 | 설명 | 언제 사용? |
|------|------|-----------|
| **Shared Kernel** | 두 Context가 공통 모델을 공유 | 긴밀히 협력하는 팀, 변경 비용 감수 가능 |
| **Customer-Supplier** | 상류(Supplier)가 하류(Customer)에 맞춰 API 제공 | 팀 간 협력이 원활할 때 |
| **Conformist** | 하류가 상류 모델을 그대로 수용 | 상류 팀에 영향력이 없을 때 |
| **Anti-Corruption Layer (ACL)** | 외부 모델을 번역하는 중간 레이어 | 레거시 시스템 통합, 외부 API 연동 |
| **Open Host Service** | 공개 프로토콜로 서비스 제공 | 다수의 소비자가 있을 때 |
| **Published Language** | 표준화된 교환 형식 정의 | Open Host Service와 함께 사용 |

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

DDD는 전통적으로 **Layered Architecture**를 사용하며, 현대에는 **Hexagonal(Ports & Adapters)** 구조와 결합하는 경우가 많다.

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI + DDD 아키텍처                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  🖥️  Presentation Layer (FastAPI Router)             │    │
│  │  - API 엔드포인트, Request/Response 스키마            │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │ Depends()                         │
│  ┌──────────────────────▼──────────────────────────────┐    │
│  │  ⚙️  Application Layer (Use Case / App Service)      │    │
│  │  - 유즈케이스 조율, 트랜잭션 관리                      │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                   │
│  ┌──────────────────────▼──────────────────────────────┐    │
│  │  🏗️  Domain Layer (핵심!)                            │    │
│  │  - Entity, Value Object, Aggregate, Domain Service   │    │
│  │  - Repository Interface (추상)                       │    │
│  │  - Domain Event                                      │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │ 의존성 역전                        │
│  ┌──────────────────────▼──────────────────────────────┐    │
│  │  💾  Infrastructure Layer                            │    │
│  │  - SQLModel 테이블 모델, Repository 구현체            │    │
│  │  - 외부 API 클라이언트, 이메일 서비스                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 📁 Python + FastAPI + SQLModel 프로젝트 구조

```
app/
├── main.py                          # FastAPI 앱 진입점
├── order/                           # 📦 "주문" Bounded Context
│   ├── domain/
│   │   ├── entities.py              # Entity, Aggregate Root
│   │   ├── value_objects.py         # Value Object
│   │   ├── events.py               # Domain Event
│   │   ├── services.py             # Domain Service
│   │   └── repositories.py         # Repository Interface (ABC)
│   ├── application/
│   │   └── use_cases.py            # Application Service
│   ├── infrastructure/
│   │   ├── models.py               # SQLModel 테이블 모델
│   │   └── repositories.py         # Repository 구현체
│   └── presentation/
│       ├── router.py               # FastAPI Router
│       └── schemas.py              # Pydantic Request/Response
├── catalog/                         # 📚 "카탈로그" Bounded Context
│   ├── domain/ ...
│   ├── application/ ...
│   ├── infrastructure/ ...
│   └── presentation/ ...
└── shared_kernel/                   # 🔗 공유 커널
    └── domain_event_bus.py
```

### 🔄 동작 흐름 (Step by Step)

**시나리오: 주문 생성 API 호출**

1. **Step 1 — HTTP 요청 수신**: FastAPI Router가 `POST /orders` 요청을 받아 Pydantic 스키마로 검증
2. **Step 2 — Use Case 호출**: `Depends()`로 주입된 `CreateOrderUseCase`를 실행
3. **Step 3 — 도메인 로직 실행**: Aggregate Root인 `Order`가 생성되고, 비즈니스 규칙(최소 1개 이상 상품 등)을 검증
4. **Step 4 — Domain Event 발행**: `OrderCreatedEvent` 발행
5. **Step 5 — 영속화**: Repository 구현체가 SQLModel을 통해 DB에 저장
6. **Step 6 — 응답 반환**: Application Service가 결과를 DTO로 변환하여 반환

### 💻 코드 예시: 전체 흐름

**Domain Layer — Entity & Value Object:**

```python
# app/order/domain/value_objects.py
from pydantic import BaseModel, field_validator


class Money(BaseModel):
    """Value Object: 불변, 식별자 없음, 속성값으로 동등성 판단"""
    amount: int
    currency: str = "KRW"

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: int) -> int:
        if v < 0:
            raise ValueError("금액은 0 이상이어야 합니다")
        return v


class OrderItem(BaseModel):
    """Value Object: 주문 항목"""
    product_id: str
    product_name: str
    quantity: int
    unit_price: Money

    @property
    def subtotal(self) -> Money:
        return Money(
            amount=self.unit_price.amount * self.quantity,
            currency=self.unit_price.currency,
        )
```

```python
# app/order/domain/entities.py
import uuid
from datetime import UTC, datetime
from enum import Enum

from app.order.domain.value_objects import Money, OrderItem


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


class Order:
    """Aggregate Root: 주문"""

    def __init__(
        self,
        customer_id: str,
        items: list[OrderItem],
        order_id: str | None = None,
    ):
        self.order_id = order_id or str(uuid.uuid4())
        self.customer_id = customer_id
        self.items = items
        self.status = OrderStatus.PENDING
        self.created_at = datetime.now(UTC)
        self._events: list = []

        # 비즈니스 규칙: 최소 1개 이상의 상품
        if not items:
            raise ValueError("주문에는 최소 1개 이상의 상품이 필요합니다")

    @property
    def total_amount(self) -> Money:
        total = sum(item.subtotal.amount for item in self.items)
        return Money(amount=total)

    def confirm(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"PENDING 상태에서만 확정 가능 (현재: {self.status})")
        self.status = OrderStatus.CONFIRMED
        self._events.append({"type": "OrderConfirmed", "order_id": self.order_id})

    def cancel(self) -> None:
        if self.status in (OrderStatus.SHIPPED, OrderStatus.CANCELLED):
            raise ValueError(f"배송 완료/취소된 주문은 취소 불가 (현재: {self.status})")
        self.status = OrderStatus.CANCELLED
        self._events.append({"type": "OrderCancelled", "order_id": self.order_id})

    def collect_events(self) -> list:
        events = self._events.copy()
        self._events.clear()
        return events
```

**Domain Layer — Domain Event:**

```python
# app/order/domain/events.py
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events"""
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class OrderCreatedEvent(DomainEvent):
    order_id: str = ""
    customer_id: str = ""


@dataclass(frozen=True)
class OrderConfirmedEvent(DomainEvent):
    order_id: str = ""


@dataclass(frozen=True)
class OrderCancelledEvent(DomainEvent):
    order_id: str = ""
```

**Domain Layer — Repository Interface:**

```python
# app/order/domain/repositories.py
from abc import ABC, abstractmethod

from app.order.domain.entities import Order


class OrderRepository(ABC):
    """Repository Interface: 도메인 레이어에 정의, 인프라에서 구현"""

    @abstractmethod
    async def save(self, order: Order) -> None: ...

    @abstractmethod
    async def find_by_id(self, order_id: str) -> Order | None: ...

    @abstractmethod
    async def find_by_customer(self, customer_id: str) -> list[Order]: ...
```

**Infrastructure Layer — SQLModel 모델 & Repository 구현:**

```python
# app/order/infrastructure/models.py
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class OrderItemModel(SQLModel, table=True):
    __tablename__ = "order_items"

    id: int | None = Field(default=None, primary_key=True)
    order_id: str = Field(foreign_key="orders.order_id")
    product_id: str
    product_name: str
    quantity: int
    unit_price: int
    currency: str = "KRW"

    order: "OrderModel" = Relationship(back_populates="items")


class OrderModel(SQLModel, table=True):
    __tablename__ = "orders"

    order_id: str = Field(primary_key=True)
    customer_id: str = Field(index=True)
    status: str
    created_at: datetime
    total_amount: int

    items: list[OrderItemModel] = Relationship(back_populates="order")
```

```python
# app/order/infrastructure/repositories.py
from sqlmodel import Session, select

from app.order.domain.entities import Order, OrderStatus
from app.order.domain.repositories import OrderRepository
from app.order.domain.value_objects import Money, OrderItem
from app.order.infrastructure.models import OrderItemModel, OrderModel


class SQLModelOrderRepository(OrderRepository):
    """Repository 구현체: SQLModel을 사용하여 영속성 처리

    ⚠️ 주의: 아래 예시는 개념 설명용으로 async def + 동기 Session을 혼용하고 있음.
    실무에서는 AsyncSession(from sqlalchemy.ext.asyncio)을 사용하거나,
    인터페이스를 동기(def)로 통일해야 함.
    """

    def __init__(self, session: Session):
        self.session = session

    async def save(self, order: Order) -> None:
        order_model = OrderModel(
            order_id=order.order_id,
            customer_id=order.customer_id,
            status=order.status.value,
            created_at=order.created_at,
            total_amount=order.total_amount.amount,
            items=[
                OrderItemModel(
                    order_id=order.order_id,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price.amount,
                    currency=item.unit_price.currency,
                )
                for item in order.items
            ],
        )
        self.session.add(order_model)
        self.session.commit()

    async def find_by_id(self, order_id: str) -> Order | None:
        statement = select(OrderModel).where(OrderModel.order_id == order_id)
        order_model = self.session.exec(statement).first()
        if not order_model:
            return None
        return self._to_domain(order_model)

    async def find_by_customer(self, customer_id: str) -> list[Order]:
        statement = select(OrderModel).where(
            OrderModel.customer_id == customer_id
        )
        models = self.session.exec(statement).all()
        return [self._to_domain(m) for m in models]

    def _to_domain(self, model: OrderModel) -> Order:
        items = [
            OrderItem(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=Money(amount=item.unit_price, currency=item.currency),
            )
            for item in model.items
        ]
        order = Order(
            customer_id=model.customer_id,
            items=items,
            order_id=model.order_id,
        )
        order.status = OrderStatus(model.status)
        order.created_at = model.created_at
        return order
```

**Application Layer — Use Case:**

```python
# app/order/application/use_cases.py
from dataclasses import dataclass

from app.order.domain.entities import Order
from app.order.domain.repositories import OrderRepository
from app.order.domain.value_objects import Money, OrderItem


@dataclass
class CreateOrderCommand:
    customer_id: str
    items: list[dict]  # [{"product_id": "...", "name": "...", "qty": 1, "price": 10000}]


class CreateOrderUseCase:
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo

    async def execute(self, command: CreateOrderCommand) -> Order:
        # DTO → Domain Value Object 변환
        order_items = [
            OrderItem(
                product_id=item["product_id"],
                product_name=item["name"],
                quantity=item["qty"],
                unit_price=Money(amount=item["price"]),
            )
            for item in command.items
        ]

        # Aggregate 생성 (비즈니스 규칙 검증은 도메인 내부에서)
        order = Order(customer_id=command.customer_id, items=order_items)

        # 영속화
        await self.order_repo.save(order)

        return order


class ConfirmOrderUseCase:
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo

    async def execute(self, order_id: str) -> Order:
        order = await self.order_repo.find_by_id(order_id)
        if not order:
            raise ValueError(f"주문을 찾을 수 없습니다: {order_id}")

        order.confirm()  # 도메인 로직 실행
        await self.order_repo.save(order)
        return order
```

**Presentation Layer — FastAPI Router:**

```python
# app/order/presentation/schemas.py
from pydantic import BaseModel


class OrderItemRequest(BaseModel):
    product_id: str
    name: str
    qty: int
    price: int


class CreateOrderRequest(BaseModel):
    customer_id: str
    items: list[OrderItemRequest]


class OrderResponse(BaseModel):
    order_id: str
    customer_id: str
    status: str
    total_amount: int
```

```python
# app/order/presentation/router.py
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.order.application.use_cases import (
    CreateOrderCommand,
    CreateOrderUseCase,
    ConfirmOrderUseCase,
)
from app.order.infrastructure.repositories import SQLModelOrderRepository
from app.order.presentation.schemas import CreateOrderRequest, OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


def get_session():
    # 실제로는 engine에서 Session 생성
    from app.database import engine
    with Session(engine) as session:
        yield session


def get_order_repo(session: Session = Depends(get_session)):
    return SQLModelOrderRepository(session)


def get_create_order_use_case(
    repo: SQLModelOrderRepository = Depends(get_order_repo),
):
    return CreateOrderUseCase(order_repo=repo)


@router.post("/", response_model=OrderResponse)
async def create_order(
    request: CreateOrderRequest,
    use_case: CreateOrderUseCase = Depends(get_create_order_use_case),
):
    command = CreateOrderCommand(
        customer_id=request.customer_id,
        items=[item.model_dump() for item in request.items],
    )
    order = await use_case.execute(command)
    return OrderResponse(
        order_id=order.order_id,
        customer_id=order.customer_id,
        status=order.status.value,
        total_amount=order.total_amount.amount,
    )
```

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| # | 유즈 케이스 | 설명 | 적합한 이유 |
|---|------------|------|------------|
| 1 | **이커머스 플랫폼** | 주문, 결제, 배송, 재고 등 복잡한 도메인 | 다수의 Bounded Context와 복잡한 비즈니스 규칙 존재 |
| 2 | **금융/핀테크** | 계좌, 거래, 정산, 규제 준수 | 정확한 도메인 모델링이 비즈니스 리스크와 직결 |
| 3 | **물류 시스템** | 운송, 추적, 경로 최적화, 창고 관리 | 여러 하위 도메인 간 복잡한 상호작용 |
| 4 | **의료 시스템** | 환자, 진료, 처방, 보험 청구 | 도메인 전문가(의사) 협업이 필수적 |
| 5 | **마이크로서비스 전환** | 모놀리스를 서비스 단위로 분리 | Bounded Context가 서비스 경계의 자연스러운 기준 |

### ✅ 베스트 프랙티스

1. **도메인 전문가와 함께 모델링하라**: 개발자 혼자 모델을 설계하지 말 것. Event Storming 같은 워크숍을 활용
2. **Bounded Context를 명확히 정의하라**: 같은 단어가 다른 의미로 쓰이면 별도 Context로 분리
3. **Aggregate를 작게 유지하라**: 하나의 Aggregate에 너무 많은 Entity를 포함하면 성능과 동시성 문제 발생
4. **도메인 레이어의 순수성을 지켜라**: 도메인 객체가 DB 프레임워크나 HTTP에 의존하지 않도록
5. **Value Object를 적극 활용하라**: Primitive Obsession을 피하고, `Money`, `Email`, `Address` 같은 VO로 표현력을 높여라

```python
# ❌ Primitive Obsession
def create_order(customer_id: str, total: int, currency: str): ...

# ✅ Value Object 활용
def create_order(customer_id: str, total: Money): ...
```

### 🏢 실제 적용 사례

> ⚠️ **검증 상태**: 아래 사례들은 업계에서 널리 알려진 정보이나, 각 기업의 공식 기술 블로그에서 "DDD"를 명시적으로 언급하는지는 개별 확인이 필요함.

- **Netflix**: 마이크로서비스 아키텍처에서 각 서비스를 Bounded Context로 설계하여 독립적 배포와 확장을 실현
- **Spotify**: Squad 모델과 DDD Bounded Context를 결합하여 팀 자율성과 도메인 전문성을 확보
- **쿠팡**: 이커머스 도메인(주문, 결제, 배송, 로켓배송)을 DDD 기반으로 서비스 분리

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ 장점 | **비즈니스 정렬** | 소프트웨어 모델이 비즈니스 현실을 정확히 반영하여 요구사항 변경에 유연 |
| ✅ 장점 | **커뮤니케이션 향상** | Ubiquitous Language로 개발자-비즈니스 팀 간 오해 감소 |
| ✅ 장점 | **유지보수성** | 명확한 경계와 레이어 분리로 변경 영향 범위 최소화 |
| ✅ 장점 | **테스트 용이성** | 도메인 레이어가 인프라와 분리되어 순수 단위 테스트 가능 |
| ✅ 장점 | **마이크로서비스 친화** | Bounded Context가 서비스 분리의 자연스러운 가이드 |
| ❌ 단점 | **높은 학습 곡선** | Entity, VO, Aggregate, Repository 등 다양한 개념 학습 필요 |
| ❌ 단점 | **도메인 전문가 필수** | 비즈니스 도메인을 깊이 이해하는 전문가 참여가 필수적 |
| ❌ 단점 | **초기 개발 속도 저하** | 모델링과 구조 설계에 시간이 많이 소요됨 |
| ❌ 단점 | **단순 CRUD에 과잉** | 비즈니스 로직이 적은 시스템에는 불필요한 복잡도 추가 |
| ❌ 단점 | **코드량 증가** | 레이어 분리와 변환 로직으로 보일러플레이트 코드 증가 |

### ⚖️ Trade-off 분석

```
비즈니스 정렬     ◄──────── Trade-off ────────►  초기 개발 속도 저하
유지보수 용이     ◄──────── Trade-off ────────►  높은 학습 곡선
테스트 용이       ◄──────── Trade-off ────────►  코드량 증가 (보일러플레이트)
명확한 경계       ◄──────── Trade-off ────────►  도메인 전문가 필수
장기적 생산성 ↑   ◄──────── Trade-off ────────►  단기적 생산성 ↓
```

---

## 6️⃣ 차이점 비교 (Comparison)

DDD와 자주 비교되는 아키텍처 접근법들: **Clean Architecture**, **Hexagonal Architecture**, **Transaction Script**

### 📊 비교 매트릭스

| 비교 기준 | DDD | Clean Architecture | Hexagonal Architecture | Transaction Script |
|-----------|-----|-------------------|----------------------|-------------------|
| **핵심 목적** | 도메인 복잡성 관리 | 관심사 분리, 의존성 규칙 | 외부 시스템과의 결합 제거 | 절차적 비즈니스 로직 처리 |
| **초점** | 비즈니스 도메인 모델링 | 아키텍처 레이어 규칙 | 포트와 어댑터 | 트랜잭션 단위 스크립트 |
| **복잡도** | 높음 | 중-높음 | 중간 | 낮음 |
| **학습 곡선** | 가파름 | 중간 | 중간 | 낮음 |
| **적합한 규모** | 대규모 복잡 도메인 | 중-대규모 | 중-대규모 | 소규모, 단순 CRUD |
| **도메인 전문가 필요** | 필수 | 선택 | 선택 | 불필요 |
| **관계** | 설계 **철학** | 설계 **패턴** | 설계 **패턴** | 설계 **패턴** |

### 🔍 핵심 차이 요약

```
DDD                              Clean Architecture
──────────────────────    vs    ──────────────────────
설계 철학 + 방법론                아키텍처 구조 패턴
도메인 모델링이 핵심              의존성 규칙이 핵심
"무엇을 만들 것인가"              "어떻게 구조화할 것인가"
Bounded Context 중심              Use Case 중심
```

```
DDD                              Transaction Script
──────────────────────    vs    ──────────────────────
풍부한 도메인 모델                절차적 스크립트
객체가 행동을 캡슐화              함수가 로직을 순차 실행
높은 초기 투자                    빠른 개발 시작
복잡한 도메인에 적합              단순한 CRUD에 적합
```

### 🤔 언제 무엇을 선택?

- **DDD를 선택하세요** → 비즈니스 규칙이 복잡하고, 도메인 전문가와 협업이 가능하며, 장기 유지보수가 중요한 프로젝트
- **Clean Architecture를 선택하세요** → 프레임워크 독립성과 테스트 용이성이 최우선이고, 도메인이 비교적 단순한 경우
- **Hexagonal Architecture를 선택하세요** → 다양한 외부 시스템(DB, 메시지 큐, API 등)과의 통합이 많은 경우
- **Transaction Script를 선택하세요** → 비즈니스 로직이 단순한 CRUD 위주의 소규모 프로젝트

> 💡 **실무 팁**: DDD + Hexagonal Architecture는 매우 자주 함께 사용된다. DDD가 **"무엇"**을 모델링하는 철학이라면, Hexagonal은 **"어떻게"** 코드를 구조화하는 패턴이다. 상호 보완적이며 배타적 선택이 아니다.

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|------|-----------|------------|
| 1 | **패턴만 따르고 도메인을 무시** | DDD는 패턴이 아니라 도메인 이해가 핵심. Entity/VO만 만든다고 DDD가 아님 | 도메인 전문가와 Event Storming부터 시작 |
| 2 | **단순 CRUD에 DDD 적용** | 불필요한 레이어와 추상화로 개발 속도만 저하 | 비즈니스 로직이 충분히 복잡한지 먼저 판단 |
| 3 | **거대한 Aggregate 설계** | 동시성 충돌, 성능 저하, 트랜잭션 Lock 범위 확대 | 하나의 Aggregate는 하나의 트랜잭션 일관성 경계 |
| 4 | **Ubiquitous Language 무시** | 개발자 용어와 비즈니스 용어 불일치로 소통 비용 증가 | 코드의 클래스/메서드명에 도메인 용어를 그대로 사용 |
| 5 | **모든 것을 한 Bounded Context에** | 모놀리식 모델로 변질, 변경 영향 범위 확대 | Context Map을 그려서 경계를 시각화 |

### 🚫 Anti-Patterns

1. **Anemic Domain Model**: Entity에 getter/setter만 있고 비즈니스 로직이 Service에 모여 있는 패턴. Martin Fowler가 명시적으로 anti-pattern으로 지적. 도메인 객체에 행동(behavior)을 넣어라.

```python
# 🚫 Anemic Domain Model (Anti-Pattern)
class Order:
    def __init__(self):
        self.status = "PENDING"
        self.items = []
        # getter/setter만 있고, 비즈니스 로직 없음

class OrderService:
    def confirm_order(self, order: Order):
        if order.status != "PENDING":
            raise ValueError("...")
        order.status = "CONFIRMED"  # 로직이 서비스에 집중


# ✅ Rich Domain Model
class Order:
    def confirm(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"PENDING 상태에서만 확정 가능")
        self.status = OrderStatus.CONFIRMED
        self._events.append(OrderConfirmedEvent(self.order_id))
```

2. **Technical Slicing**: 도메인 경계가 아닌 기술 레이어(controller/, service/, repository/)로만 패키지를 분리하면, 도메인 응집도가 떨어지고 변경 시 여러 패키지를 동시에 수정해야 함. **Feature/Domain 기반 슬라이싱**을 사용하라.

3. **DDD for DDD's Sake**: 비즈니스 가치 창출 없이 Context Map만 예쁘게 그리고 끝나는 것. DDD는 비즈니스 성과를 위한 도구이지, 그 자체가 목적이 아니다.

### 🔒 보안/성능 고려사항

- **보안**: Aggregate Root를 통해서만 내부 Entity에 접근하도록 강제하면, 권한 검증 포인트를 일원화할 수 있음
- **성능**: Aggregate 크기가 클수록 DB Lock 범위가 넓어짐. **Eventual Consistency**를 고려하여 Aggregate 간 통신은 Domain Event로 비동기 처리
- ⚡ **SQLModel 특이사항**: SQLModel은 SQLAlchemy 기반이므로, 도메인 모델과 DB 모델을 분리하지 않으면 도메인 레이어가 인프라에 의존하게 됨. `table=True`는 Infrastructure 레이어에서만 사용

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|------|------|----------|
| 📖 공식 도서 | *Domain-Driven Design* (Eric Evans, 2003) | DDD 원전. "Blue Book"으로 불림 |
| 📘 실전 도서 | *Implementing Domain-Driven Design* (Vaughn Vernon, 2013) | "Red Book". 실무 적용 중심 |
| 📘 입문 도서 | *Domain-Driven Design Distilled* (Vaughn Vernon, 2016) | DDD 핵심만 압축한 입문서 |
| 📘 Python 특화 | *Architecture Patterns with Python* (Percival & Gregory) | Python으로 DDD, Repository, UoW 패턴 구현 |
| 📺 영상 | [What is DDD - Eric Evans (DDD Europe)](https://www.youtube.com/watch?v=pMuiVlnGqjk) | 창시자의 직접 설명 |
| 🎓 강의 | [DDD Fundamentals - Pluralsight](https://www.pluralsight.com/courses/fundamentals-domain-driven-design) | 체계적 온라인 강의 |
| 📖 레퍼런스 | [DDD Reference (Eric Evans)](https://www.domainlanguage.com/ddd/) | 공식 DDD 용어 참조 문서 |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리 | 언어/플랫폼 | 용도 |
|---------------|-----------|------|
| **FastAPI** | Python | 고성능 웹 프레임워크, DI 내장 |
| **SQLModel** | Python | Pydantic + SQLAlchemy 기반 ORM |
| **Pydantic** | Python | Value Object, DTO 검증에 활용 |
| **dependency-injector** | Python | IoC/DI 컨테이너 |
| **import-linter** | Python | Bounded Context 간 의존성 규칙 강제 |
| **Event Storming** | 방법론 | 도메인 이벤트 기반 모델링 워크숍 |
| **Miro / FigJam** | 도구 | Event Storming 온라인 협업 보드 |

### 🔮 트렌드 & 전망

- **DDD + Event Sourcing + CQRS**: 이벤트 중심 아키텍처와의 결합이 마이크로서비스에서 주류 패턴으로 자리잡는 중
- **AI 시대의 DDD**: LLM을 활용한 도메인 모델링 지원 도구 등장 (코드 생성, Ubiquitous Language 추출)
- **Modular Monolith**: 마이크로서비스 피로감으로 인해, DDD의 Bounded Context를 모듈러 모놀리스로 구현하는 트렌드 강화
- **Python DDD 생태계 성장**: FastAPI + SQLModel/SQLAlchemy 조합이 Python DDD 구현의 사실상 표준으로 정착

### 💬 커뮤니티 인사이트

- "DDD의 가장 큰 가치는 코드 패턴이 아니라 **팀의 소통 방식을 바꾸는 것**이다. Ubiquitous Language 하나만 제대로 해도 절반은 성공" — 실무자 공통 의견
- "Aggregate를 너무 크게 만드는 실수를 가장 많이 한다. **작게 시작하고 필요할 때 합쳐라**" — DDD 커뮤니티 반복 조언
- "단순 CRUD 프로젝트에 DDD를 적용하면 팀원들이 **'왜 이렇게 복잡하지?'**라고 불만을 표한다. 복잡도가 있는 도메인에서만 빛난다" — Reddit/커뮤니티 공통 피드백

---

## 📎 Sources

1. [Domain-Driven Design - Wikipedia](https://en.wikipedia.org/wiki/Domain-driven_design) — 백과사전
2. [Domain Driven Design - Martin Fowler](https://martinfowler.com/bliki/DomainDrivenDesign.html) — 기술 블로그
3. [DDD: A Summary - Software Engineering Book](https://softengbook.org/articles/ddd) — 교육 자료
4. [DDD with Python and FastAPI - ActiDoo](https://www.actidoo.com/en/blog/python-fastapi-domain-driven-design) — 기술 블로그
5. [Implementing DDD with FastAPI - Hyunil Kim / Delivus](https://medium.com/delivus/implementing-domain-driven-design-with-fastapi-6aed788779af) — 기술 블로그
6. [Bounded Context - Martin Fowler](https://martinfowler.com/bliki/BoundedContext.html) — 기술 블로그
7. [The Pros and Cons of DDD - AppDevCon](https://appdevcon.nl/the-pros-and-cons-of-domain-driven-design/) — 기술 컨퍼런스
8. [DDD Anti-Patterns - Alok Mishra](https://alok-mishra.com/2021/11/03/ddd-anti-patterns/) — 기술 블로그
9. [Anemic Domain Model - Martin Fowler](https://martinfowler.com/bliki/AnemicDomainModel.html) — 기술 블로그
10. [DDD Architectures in Comparison - MaibornWolff](https://www.maibornwolff.de/en/ddd-architectures-in-comparison/) — 기술 블로그
11. [DDD, Hexagonal, Onion, Clean, CQRS - Herberto Graca](https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/) — 기술 블로그
12. [Unit of Work and Repository with SQLModel - DEV](https://dev.to/manukanne/a-python-implementation-of-the-unit-of-work-and-repository-design-pattern-using-sqlmodel-3mb5) — 커뮤니티

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 7
> - 수집 출처 수: 12
> - 출처 유형: 공식 1, 블로그 8, 커뮤니티 2, 교육 1

---

> 🔄 **Convergence Verification Report** (2026-03-22)
>
> **검증 항목 및 결과:**
>
> | 검증 영역 | 상태 | 발견 사항 |
> |-----------|------|----------|
> | 정확성 (Accuracy) | Improved | `datetime.utcnow()` → `datetime.now(UTC)` 수정, async/sync 불일치 주석 추가 |
> | 완전성 (Completeness) | Improved | Context Map 패턴 6종, Subdomain 유형 3종, Factory 설명, Domain Event 코드 예시 추가 |
> | 일관성 (Consistency) | Improved | 다이어그램에만 있던 개념들(Factory, Context Map, Subdomain)에 설명 보강 |
> | 검증 필요 항목 | Flagged | Netflix/Spotify/쿠팡 DDD 적용 사례 - 공식 출처 미확인 |
>
> **수정 내역:**
> 1. `datetime.utcnow()` deprecated API를 `datetime.now(UTC)`로 수정
> 2. Strategic Design 상세 섹션 추가 (Subdomain 유형, Context Map 패턴)
> 3. Factory 패턴을 핵심 개념 테이블에 추가
> 4. Domain Event 코드 예시(`events.py`) 추가
> 5. Repository 구현체의 async/sync 혼용 주의사항 명시
> 6. 기업 적용 사례에 검증 상태 표기 추가
