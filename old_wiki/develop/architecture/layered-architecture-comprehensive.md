---
created: 2026-04-01
source: claude-code
tags: [architecture, python, fastapi, sqlmodel, layered-architecture, concept-deep-dive, comprehensive]
---

# 📖 Layered Architecture — Concept Deep Dive (Comprehensive)

> 💡 **한줄 요약**: Layered Architecture는 소프트웨어를 **수평 레이어(Presentation → Application → Domain → Persistence)**로 나누어 각 레이어가 하나의 관심사만 담당하게 하고, **위에서 아래로** 의존하게 하는 가장 기본적이고 널리 사용되는 아키텍처 패턴이다.

---

## 1️⃣ 무엇인가? (What is it?)

**Layered Architecture(계층 아키텍처)**는 소프트웨어 아키텍처 패턴 중 가장 오래되고 가장 널리 사용되는 패턴이다. 시스템을 **수평 레이어**로 분할하여 각 레이어가 특정 관심사(concern)만 담당하게 한다.

### 원전

- **POSA Vol.1** (Buschmann et al., 1996) — "Layers" 패턴을 정식화. 시스템을 여러 상호작용하는 레이어로 분할하며, 각 레이어는 특정 책임/관심사를 담당한다.
- **Martin Fowler** "Patterns of Enterprise Application Architecture" (2002) — 엔터프라이즈 애플리케이션에서 Presentation, Domain Logic, Data Source 3 레이어 체계를 정립.

### 탄생 배경

레이어드 아키텍처는 **관심사의 분리(Separation of Concerns)** 원칙의 가장 직관적인 구현이다. 컴퓨터 네트워크의 **OSI 7-Layer 모델**(1984)에서 영감을 받았으며, 각 레이어가 독립적으로 변경·교체될 수 있다는 아이디어에 기반한다.

**비유**: 아파트 건물. 1층은 상가(Presentation), 2층은 사무실(Application), 3층은 연구소(Domain), 지하는 창고(Persistence). 각 층은 자기 역할이 있고, 아래층의 서비스를 사용한다.

> 📌 **핵심 키워드**: `Layer`, `Separation of Concerns`, `Top-Down Dependency`, `Strict Layering`, `Relaxed Layering`, `DTO`

---

## 2️⃣ 핵심 개념 (Core Concepts)

### 7가지 구성요소 전체 맵

```
┌─────────────────────────────────────────────────────────┐
│               Layered Architecture 전체 구조               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │         🖥️  Presentation Layer                     │  │
│  │    Controller, View, API Router, Template          │  │
│  │    사용자/외부 시스템과의 상호작용                     │  │
│  └──────────────────────┬─────────────────────────────┘  │
│                          │ DTO ↕                          │
│  ┌──────────────────────▼─────────────────────────────┐  │
│  │         ⚙️  Application / Service Layer            │  │
│  │    Service, Use Case, Transaction Management       │  │
│  │    유스케이스 오케스트레이션                           │  │
│  └──────────────────────┬─────────────────────────────┘  │
│                          │ Domain Object ↕                │
│  ┌──────────────────────▼─────────────────────────────┐  │
│  │         🏗️  Business / Domain Layer                │  │
│  │    Entity, Business Rule, Validation               │  │
│  │    비즈니스 규칙과 로직의 핵심                        │  │
│  └──────────────────────┬─────────────────────────────┘  │
│                          │ Domain Object ↕                │
│  ┌──────────────────────▼─────────────────────────────┐  │
│  │         💾  Persistence / Data Access Layer         │  │
│  │    Repository, DAO, ORM Mapping                    │  │
│  │    데이터베이스 접근 추상화                            │  │
│  └──────────────────────┬─────────────────────────────┘  │
│                          │ SQL / Query ↕                  │
│  ┌──────────────────────▼─────────────────────────────┐  │
│  │         🗄️  Database Layer                         │  │
│  │    PostgreSQL, MySQL, MongoDB                      │  │
│  │    실제 데이터 저장소                                │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  의존성 방향: 위 ──────────────────────→ 아래              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

### 구성요소별 상세 설명

#### 1. Presentation Layer (프레젠테이션 레이어)

**정의**: 사용자(또는 외부 시스템)와의 **상호작용을 담당**하는 최상위 레이어. HTTP 요청 수신, 응답 생성, 입력 유효성 검사(형식 검증)를 수행한다.

**비유**: 레스토랑의 **홀 서비스**. 손님을 맞이하고, 주문을 받고, 음식을 서빙한다. 요리(비즈니스 로직)는 하지 않는다.

**역할**:
- HTTP 요청/응답 처리 (REST Controller, GraphQL Resolver)
- 입력 유효성 검사 (형식 검증 — 이메일 형식, 필수값 등)
- 응답 포맷팅 (JSON, HTML, XML)
- 인증/인가 미들웨어

**포함하면 안 되는 것**: 비즈니스 로직, DB 직접 접근, SQL 쿼리

**연결관계**: Application/Service Layer를 호출하고, DTO를 통해 데이터를 주고받는다.

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/orders")

# Presentation Layer — 입력/출력 스키마 (DTO 역할)
class CreateOrderRequest(BaseModel):
    """입력 DTO — 형식 검증만"""
    customer_id: str
    customer_email: EmailStr
    items: list[dict]

class OrderResponse(BaseModel):
    """출력 DTO — 클라이언트에게 반환할 형태"""
    order_id: str
    status: str
    total: float
    message: str

# Controller — Presentation Layer
@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(
    request: CreateOrderRequest,
    service: OrderService = Depends(get_order_service),
):
    """Presentation Layer: 요청 수신 → Service 호출 → 응답 반환"""
    try:
        result = service.place_order(
            customer_id=request.customer_id,
            items=request.items,
        )
        return OrderResponse(
            order_id=result.id,
            status=result.status,
            total=result.total,
            message="주문이 접수되었습니다",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    service: OrderService = Depends(get_order_service),
):
    result = service.get_order(order_id)
    if not result:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    return OrderResponse(
        order_id=result.id,
        status=result.status,
        total=result.total,
        message="",
    )
```

---

#### 2. Application / Service Layer (애플리케이션 레이어)

**정의**: **유스케이스를 오케스트레이션**하는 레이어. 트랜잭션 경계를 관리하고, Domain Layer에 작업을 위임하며, 여러 도메인 객체 간의 조율을 담당한다.

**비유**: 레스토랑의 **주방장(Head Chef)**. 주문서를 받아서 각 요리사에게 지시하고, 모든 요리가 동시에 나올 수 있도록 조율한다. 직접 요리(비즈니스 로직)를 하지는 않는다.

**역할**:
- 유스케이스(워크플로우) 오케스트레이션
- 트랜잭션 경계 관리 (시작/커밋/롤백)
- Domain Layer와 Persistence Layer를 조율
- 외부 서비스 호출 (이메일, 메시지 큐 등)

**포함하면 안 되는 것**: 비즈니스 규칙 (if-else로 비즈니스 로직을 판단하면 안 됨)

**연결관계**: Presentation Layer에서 호출받고, Domain Layer와 Persistence Layer를 사용한다.

```python
class OrderService:
    """Application / Service Layer — 유스케이스 오케스트레이션"""

    def __init__(
        self,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
        email_service: EmailService,
    ):
        self._order_repo = order_repo
        self._product_repo = product_repo
        self._email_service = email_service

    def place_order(self, customer_id: str, items: list[dict]) -> Order:
        """주문 접수 유스케이스"""
        # 1. 도메인 객체 생성
        order = Order(customer_id=customer_id)

        # 2. 상품 조회 및 주문 항목 추가 (Domain Layer에 위임)
        for item_data in items:
            product = self._product_repo.find_by_id(item_data["product_id"])
            if not product:
                raise ValueError(f"상품을 찾을 수 없습니다: {item_data['product_id']}")
            order.add_item(product, item_data["quantity"])  # 비즈니스 로직은 Order에

        # 3. 주문 접수 (비즈니스 규칙은 Domain Layer에)
        order.place()

        # 4. 저장 (Persistence Layer에 위임)
        self._order_repo.save(order)

        # 5. 알림 (외부 서비스)
        self._email_service.send_confirmation(order)

        return order

    def get_order(self, order_id: str) -> Order | None:
        return self._order_repo.find_by_id(order_id)

    def cancel_order(self, order_id: str) -> Order:
        order = self._order_repo.find_by_id(order_id)
        if not order:
            raise ValueError("주문을 찾을 수 없습니다")
        order.cancel()  # 비즈니스 규칙은 Domain Layer에
        self._order_repo.save(order)
        return order
```

---

#### 3. Business / Domain Layer (비즈니스 레이어)

**정의**: **비즈니스 규칙과 로직의 핵심**. 도메인 모델(Entity, Value Object)과 비즈니스 규칙을 포함한다. Layered Architecture에서 가장 중요한 레이어이다.

**비유**: 레스토랑의 **레시피와 요리 기술**. 어떤 재료를 어떻게 조합하고, 어떤 온도로 조리하고, 어떤 조건에서 서빙할 수 있는지의 규칙이다.

**역할**:
- 비즈니스 규칙 캡슐화 (주문 상태 전이, 가격 계산, 재고 확인 등)
- 도메인 모델 정의 (Entity, Value Object)
- 유효성 검사 (비즈니스 규칙 기반 — "10만원 이상 주문만 무료배송")

**포함하면 안 되는 것**: DB 접근 코드, HTTP 관련 코드, 프레임워크 의존성

**연결관계**: Application Layer에 의해 사용된다. Persistence Layer를 직접 호출하지 않는다 (Strict Layering의 경우).

```python
from dataclasses import dataclass, field
from decimal import Decimal
from uuid import uuid4
from enum import Enum

class OrderStatus(Enum):
    PENDING = "PENDING"
    PLACED = "PLACED"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"

@dataclass
class Product:
    """도메인 모델 — 상품"""
    id: str
    name: str
    price: Decimal
    stock: int

    def is_available(self, quantity: int) -> bool:
        """비즈니스 규칙: 재고 확인"""
        return self.stock >= quantity

@dataclass
class OrderItem:
    """도메인 모델 — 주문 항목"""
    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity

@dataclass
class Order:
    """도메인 모델 — 주문 (비즈니스 규칙의 핵심)"""
    id: str = field(default_factory=lambda: str(uuid4()))
    customer_id: str = ""
    status: str = OrderStatus.PENDING.value
    items: list[OrderItem] = field(default_factory=list)

    def add_item(self, product: Product, quantity: int):
        """비즈니스 규칙: 재고가 있어야 추가 가능"""
        if self.status != OrderStatus.PENDING.value:
            raise ValueError("확정된 주문에 상품을 추가할 수 없습니다")
        if not product.is_available(quantity):
            raise ValueError(f"재고 부족: {product.name}")
        if quantity <= 0:
            raise ValueError("수량은 1 이상이어야 합니다")

        self.items.append(OrderItem(
            product_id=product.id,
            product_name=product.name,
            quantity=quantity,
            unit_price=product.price,
        ))

    def place(self):
        """비즈니스 규칙: 상품이 있어야 주문 접수 가능"""
        if not self.items:
            raise ValueError("상품이 없는 주문은 접수할 수 없습니다")
        self.status = OrderStatus.PLACED.value

    def cancel(self):
        """비즈니스 규칙: SHIPPED 이후는 취소 불가"""
        if self.status == OrderStatus.SHIPPED.value:
            raise ValueError("배송된 주문은 취소할 수 없습니다")
        self.status = OrderStatus.CANCELLED.value

    @property
    def total(self) -> float:
        return float(sum(item.subtotal for item in self.items))

    @property
    def is_free_shipping(self) -> bool:
        """비즈니스 규칙: 10만원 이상 무료배송"""
        return self.total >= 100000
```

---

#### 4. Persistence / Data Access Layer (영속성 레이어)

**정의**: **데이터베이스 접근을 추상화**하는 레이어. Repository 패턴 또는 DAO(Data Access Object) 패턴을 사용하여 SQL/ORM 세부사항을 캡슐화한다.

**비유**: 레스토랑의 **식자재 창고 관리자**. 어떤 식자재가 어디에 있는지, 어떻게 보관하는지를 관리한다. 주방(Domain)은 "토마토 주세요"라고만 하면 된다.

**역할**:
- 도메인 객체의 저장(Create/Update)과 조회(Read)
- SQL 쿼리, ORM 매핑, 트랜잭션 실행
- 도메인 모델 ↔ DB 모델 변환

**포함하면 안 되는 것**: 비즈니스 로직, HTTP 관련 코드

**연결관계**: Application Layer에 의해 사용된다. Database Layer에 실제 쿼리를 전달한다.

```python
from abc import ABC, abstractmethod
from sqlmodel import SQLModel, Field, Session, select

# DB 모델 — Persistence Layer에만 존재
class OrderDBModel(SQLModel, table=True):
    __tablename__ = "orders"
    id: str = Field(primary_key=True)
    customer_id: str
    status: str
    total: float

class OrderItemDBModel(SQLModel, table=True):
    __tablename__ = "order_items"
    id: int = Field(default=None, primary_key=True)
    order_id: str = Field(foreign_key="orders.id")
    product_id: str
    product_name: str
    quantity: int
    unit_price: float

# Repository 인터페이스
class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def find_by_id(self, order_id: str) -> Order | None: ...

    @abstractmethod
    def find_by_customer(self, customer_id: str) -> list[Order]: ...

# Repository 구현 — SQLModel 기반
class SqlModelOrderRepository(OrderRepository):
    """Persistence Layer — DB 접근 추상화"""

    def __init__(self, session: Session):
        self._session = session

    def save(self, order: Order) -> None:
        db_order = OrderDBModel(
            id=order.id,
            customer_id=order.customer_id,
            status=order.status,
            total=order.total,
        )
        self._session.merge(db_order)

        # 주문 항목 저장
        for item in order.items:
            db_item = OrderItemDBModel(
                order_id=order.id,
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=float(item.unit_price),
            )
            self._session.add(db_item)

        self._session.commit()

    def find_by_id(self, order_id: str) -> Order | None:
        db_order = self._session.get(OrderDBModel, order_id)
        if not db_order:
            return None

        # DB 모델 → 도메인 모델 변환
        stmt = select(OrderItemDBModel).where(
            OrderItemDBModel.order_id == order_id
        )
        db_items = self._session.exec(stmt).all()

        order = Order(
            id=db_order.id,
            customer_id=db_order.customer_id,
            status=db_order.status,
        )
        order.items = [
            OrderItem(
                product_id=i.product_id,
                product_name=i.product_name,
                quantity=i.quantity,
                unit_price=Decimal(str(i.unit_price)),
            )
            for i in db_items
        ]
        return order

    def find_by_customer(self, customer_id: str) -> list[Order]:
        stmt = select(OrderDBModel).where(
            OrderDBModel.customer_id == customer_id
        )
        db_orders = self._session.exec(stmt).all()
        return [self.find_by_id(o.id) for o in db_orders]
```

---

#### 5. Database Layer (데이터베이스 레이어)

**정의**: **실제 데이터 저장소**. PostgreSQL, MySQL, MongoDB, Redis 등 물리적 데이터베이스이다. 코드가 아닌 인프라 구성 요소이다.

**비유**: 레스토랑의 **냉장고와 창고**. 실제 식자재가 보관되는 물리적 장소.

**역할**:
- 데이터의 물리적 저장
- 인덱싱, 제약 조건, 트리거
- 백업, 복제, 마이그레이션

**연결관계**: Persistence Layer만 직접 접근. 다른 레이어에서 DB에 직접 접근하면 안 된다.

```python
# Database Layer — 설정 (Framework/Infrastructure)
from sqlmodel import create_engine, Session, SQLModel

DATABASE_URL = "postgresql://user:password@localhost:5432/orders_db"
engine = create_engine(DATABASE_URL)

def init_db():
    """DB 스키마 초기화"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """DB 세션 팩토리"""
    with Session(engine) as session:
        yield session
```

---

#### 6. DTO (Data Transfer Object)

**정의**: **레이어 간 데이터를 전달**하기 위한 단순한 데이터 구조. 비즈니스 로직이 없으며, 속성(필드)과 접근자만 가진다.

**비유**: 택배 상자. 내용물(데이터)을 안전하게 담아서 다른 곳(레이어)으로 옮기는 용도. 상자 자체에는 기능이 없다.

**역할**:
- 레이어 간 **결합도 감소**: 도메인 모델을 직접 노출하지 않음
- **보안**: 내부 필드를 선별적으로 노출
- **성능**: 필요한 데이터만 전달 (N+1 방지)

**연결관계**: 주로 Presentation ↔ Application 사이, 또는 Application ↔ Persistence 사이에서 사용.

```python
from pydantic import BaseModel
from dataclasses import dataclass

# Presentation ↔ Application 사이 DTO
class PlaceOrderDTO(BaseModel):
    """입력 DTO — Presentation → Application"""
    customer_id: str
    items: list[dict]

class OrderSummaryDTO(BaseModel):
    """출력 DTO — Application → Presentation"""
    order_id: str
    status: str
    total: float
    item_count: int
    is_free_shipping: bool

    @classmethod
    def from_domain(cls, order: Order) -> "OrderSummaryDTO":
        """도메인 모델 → DTO 변환"""
        return cls(
            order_id=order.id,
            status=order.status,
            total=order.total,
            item_count=len(order.items),
            is_free_shipping=order.is_free_shipping,
        )
```

---

#### 7. Strict vs Relaxed Layering (엄격 vs 완화 레이어링)

**정의**: 레이어 간 **의존성 규칙의 엄격도**를 결정하는 설계 결정.

| 유형 | 규칙 | 장점 | 단점 |
|---|---|---|---|
| **Strict Layering** | 바로 아래 레이어**만** 호출 가능 | 변경 영향 범위 최소화, 계층 독립성 강화 | 중간 레이어에 불필요한 pass-through 메서드 발생 |
| **Relaxed Layering** | 아래의 **모든** 레이어 호출 가능 | 불필요한 간접 참조 방지, 실무에서 더 흔함 | 결합도 증가, 변경 영향 범위 확대 |

**비유**:
- Strict: 회사의 **엄격한 보고 체계**. 팀원 → 팀장 → 본부장 → CEO. 중간을 건너뛸 수 없다.
- Relaxed: 회사의 **개방된 소통 구조**. 팀원이 필요하면 본부장에게 직접 보고할 수 있다.

```
Strict Layering:                    Relaxed Layering:
┌──────────────┐                    ┌──────────────┐
│ Presentation │                    │ Presentation │
└──────┬───────┘                    └──┬───┬───┬───┘
       │ (바로 아래만)                  │   │   │
       ▼                               │   │   │ (모든 아래 레이어)
┌──────────────┐                    ┌──▼───┘   │
│ Application  │                    │Application│  │
└──────┬───────┘                    └──┬───────┘  │
       │                               │          │
       ▼                               ▼          │
┌──────────────┐                    ┌──────────┐  │
│   Domain     │                    │  Domain  │  │
└──────┬───────┘                    └──┬───────┘  │
       │                               │          │
       ▼                               ▼          ▼
┌──────────────┐                    ┌──────────────┐
│ Persistence  │                    │ Persistence  │
└──────────────┘                    └──────────────┘
```

**실무 권장**: 대부분의 프로젝트에서 **Relaxed Layering**이 실용적이다. 단, Presentation → Persistence 직접 접근은 금지하고, Presentation → Domain 접근 정도만 허용하는 **하이브리드 방식**이 흔하다.

```python
# Strict Layering — Application이 Persistence를 통해서만 데이터 접근
class OrderService:
    def get_order_summary(self, order_id: str) -> OrderSummaryDTO:
        order = self._order_repo.find_by_id(order_id)  # Persistence 통해
        return OrderSummaryDTO.from_domain(order)

# Relaxed Layering — Presentation이 Domain 객체를 직접 사용 (허용)
@router.get("/{order_id}")
async def get_order(order_id: str, service: OrderService = Depends()):
    order = service.get_order(order_id)  # Domain 객체 직접 반환
    return {
        "order_id": order.id,
        "total": order.total,
        "is_free_shipping": order.is_free_shipping,  # Domain 로직 직접 사용
    }
```

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

```
┌────────────────────────────────────────────────────────────┐
│                  Layered Architecture 요청 흐름              │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  👤 사용자                                                  │
│    │ HTTP POST /orders                                     │
│    ▼                                                        │
│  ┌──────────────────────────┐  Presentation Layer          │
│  │ FastAPI Router           │  요청 수신, 입력 검증          │
│  │ (Controller)             │  DTO 변환                     │
│  └────────────┬─────────────┘                               │
│               │ PlaceOrderDTO                               │
│               ▼                                              │
│  ┌──────────────────────────┐  Application Layer           │
│  │ OrderService             │  유스케이스 오케스트레이션      │
│  │ (Service)                │  트랜잭션 관리                 │
│  └──────┬─────────┬─────────┘                               │
│         │         │                                          │
│         ▼         ▼                                          │
│  ┌────────────┐ ┌──────────────┐  Domain Layer             │
│  │ Order      │ │ Product      │  비즈니스 규칙 실행         │
│  │ (Entity)   │ │ (Entity)     │  order.add_item()          │
│  └────────────┘ └──────────────┘  order.place()             │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────────────────┐  Persistence Layer           │
│  │ SqlModelOrderRepository  │  도메인 → DB 변환             │
│  │ (Repository)             │  SQL 실행                     │
│  └────────────┬─────────────┘                               │
│               │ SQL INSERT                                   │
│               ▼                                              │
│  ┌──────────────────────────┐  Database Layer              │
│  │ PostgreSQL               │  물리적 저장                   │
│  └──────────────────────────┘                               │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (주문 접수 예시)

1. **Step 1**: 사용자가 HTTP POST /orders 요청 전송
2. **Step 2**: Presentation Layer(Controller)가 요청을 파싱하고 형식 검증
3. **Step 3**: Application Layer(OrderService)가 유스케이스 실행 시작
4. **Step 4**: ProductRepository를 통해 상품 조회 (Persistence → DB)
5. **Step 5**: Domain Layer(Order Entity)에서 비즈니스 규칙 실행 (add_item, place)
6. **Step 6**: OrderRepository를 통해 주문 저장 (Persistence → DB)
7. **Step 7**: Application Layer에서 이메일 발송 등 부가 작업
8. **Step 8**: Presentation Layer가 결과를 HTTP 응답으로 반환

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스

### 🎯 대표 유즈 케이스

| # | 유즈 케이스 | 설명 | 적합한 이유 |
|---|------------|------|------------|
| 1 | **단순 CRUD 애플리케이션** | 관리자 패널, 내부 도구 | 직관적이고 빠른 개발 |
| 2 | **소규모 웹 애플리케이션** | 블로그, 쇼핑몰 MVP | 학습 곡선 낮음, 빠른 시작 |
| 3 | **전통적 엔터프라이즈** | 레거시 시스템, ERP | 대부분의 프레임워크가 지원 |
| 4 | **프로토타입/MVP** | 빠른 검증이 필요 | 최소한의 설계로 시작 가능 |
| 5 | **팀 경험이 다양한 경우** | 주니어~시니어 혼합 | 누구나 이해할 수 있는 구조 |

### ✅ 베스트 프랙티스

1. **비즈니스 로직은 Domain Layer에**: Service Layer에 if-else 비즈니스 규칙을 넣지 말 것
2. **DTO로 레이어 경계 보호**: 도메인 모델을 Presentation에 직접 노출하지 말 것
3. **하이브리드 Layering 사용**: Strict + Relaxed 혼합으로 실용성 확보
4. **Persistence Layer 추상화**: ORM에 직접 의존하지 말고 Repository 인터페이스 사용

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ 장점 | **직관적 구조** | 대부분의 개발자가 즉시 이해 가능 |
| ✅ 장점 | **낮은 학습 곡선** | 별도의 패턴 학습 없이 시작 가능 |
| ✅ 장점 | **프레임워크 지원** | Django, Spring, Rails 등 대부분 기본 구조 |
| ✅ 장점 | **관심사 분리** | 각 레이어가 독립적 책임 |
| ✅ 장점 | **점진적 복잡도** | 단순하게 시작하여 필요시 발전 가능 |
| ❌ 단점 | **계층 경계 위반 쉬움** | "선"을 진지하게 안 받아들임 (Cockburn 비판) |
| ❌ 단점 | **Sinkhole Anti-pattern** | 요청이 레이어를 pass-through만 하는 경우 |
| ❌ 단점 | **의존성 방향 한계** | Domain이 Persistence에 의존 (DIP 위반) |
| ❌ 단점 | **DB 중심 설계 유도** | DB 스키마 먼저 설계하는 경향 |
| ❌ 단점 | **테스트 어려움** | Domain이 Persistence에 의존하여 격리 테스트 어려움 |

### ⚖️ Trade-off 분석

```
직관적 구조     ◄──── Trade-off ────►  계층 경계 위반 쉬움
낮은 학습 곡선  ◄──── Trade-off ────►  DB 중심 설계 유도
빠른 개발 시작  ◄──── Trade-off ────►  장기 유지보수 어려움
프레임워크 지원 ◄──── Trade-off ────►  프레임워크 결합
```

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 Layered vs Hexagonal vs Clean

| 비교 기준 | Layered | Hexagonal | Clean |
|---|---|---|---|
| **의존성 방향** | 위→아래 (단방향) | 밖→안 (대칭) | 밖→안 (동심원) |
| **도메인 위치** | 중간 레이어 | Hexagon 내부 | 최내부 원 |
| **DB 의존성** | Domain → Persistence | Domain이 DB를 모름 | Entity가 DB를 모름 |
| **테스트 용이성** | 낮음 (DB 의존) | 높음 (Mock Adapter) | 높음 (Mock Gateway) |
| **학습 곡선** | 낮음 | 중간 | 중간 |
| **DIP 적용** | 선택 | 필수 | 필수 |
| **적합한 규모** | 소~중규모 | 중~대규모 | 중~대규모 |

### 🔍 핵심 차이: 의존성 방향

```
Layered (전통적):             Hexagonal / Clean:

Presentation                  Adapter (외부)
     │                              │
     ▼                              ▼
Application                   Port/Boundary
     │                              │
     ▼                              ▼
Domain ───────► Persistence   Domain (중심, 외부를 모름)
     (Domain이 DB에 의존)           │
                                    ▼
                              Port/Boundary
                                    │
                                    ▼
                              Adapter (외부)
```

**핵심 차이**: Layered에서는 Domain이 Persistence에 **의존**한다. Hexagonal/Clean에서는 Domain이 중심에 있고 **외부를 전혀 모른다**. 이 차이가 테스트 용이성, 기술 독립성의 근본적 차이를 만든다.

### 🤔 언제 무엇을 선택?

- **Layered를 선택하세요** → 단순 CRUD, MVP, 소규모 프로젝트, 팀의 아키텍처 경험이 적을 때
- **Hexagonal/Clean으로 전환하세요** → 비즈니스 로직이 복잡해지고, 테스트가 중요해지고, 외부 기술 변경이 예상될 때
- **진화 경로**: Layered → Domain Layer에 DIP 적용 → Hexagonal/Clean으로 점진적 전환

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|------|-----------|------------|
| 1 | **Sinkhole Anti-pattern** | 요청이 레이어를 그냥 통과만 함 (로직 없이) | 80/20 규칙: 20% 이상이 sinkhole이면 구조 재검토 |
| 2 | **Controller에 비즈니스 로직** | 관심사 분리 위반, 테스트 어려움 | Domain Layer에 로직 배치 |
| 3 | **Service에 비즈니스 로직** | Anemic Domain Model 안티패턴 | Entity에 로직을 넣고, Service는 오케스트레이션만 |
| 4 | **Domain에서 직접 DB 호출** | 레이어 경계 위반, 결합도 증가 | Persistence Layer를 통해서만 접근 |
| 5 | **DTO 없이 Entity 직접 반환** | 내부 모델이 외부에 노출 | 레이어 경계마다 DTO 사용 |

### 🚫 Anti-Patterns

1. **Big Ball of Mud**: 레이어 경계를 무시하고 모든 코드가 뒤섞인 상태. Layered Architecture의 가장 흔한 퇴화 형태.
2. **Anemic Domain Model**: Domain Layer의 Entity에 로직이 없고, Service Layer에 모든 비즈니스 로직이 있는 상태.
3. **Database-Driven Design**: DB 스키마를 먼저 설계하고, 도메인 모델을 DB에 맞추는 것. 도메인 모델이 먼저 나와야 한다.

### ⚡ 성능 고려사항

- Strict Layering에서 pass-through 메서드가 많으면 **함수 호출 오버헤드** 발생
- DTO 변환이 과도하면 **객체 생성 비용** 증가
- 실무에서는 **읽기 전용 쿼리에 한해** Presentation → Persistence 직접 접근을 허용하기도 함 (CQRS적 사고)

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|------|------|----------|
| 📖 원전 | POSA Vol.1 | Buschmann et al. (1996) — Layers 패턴 |
| 📘 도서 | PofEAA | [Martin Fowler (2002)](https://martinfowler.com/eaaCatalog/) |
| 📖 블로그 | Layered Architecture | [Herbertograca](https://herbertograca.com/2017/08/03/layered-architecture/) |
| 📖 가이드 | Layered Architecture | [Baeldung](https://www.baeldung.com/cs/layered-architecture) |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리 | 언어/플랫폼 | 용도 |
|---|---|---|
| Django | Python | MVT(Model-View-Template) — 자연스러운 Layered |
| FastAPI + SQLModel | Python | 경량 Layered 구조에 적합 |
| Spring Boot | Java | Layered Architecture의 대표 프레임워크 |
| Ruby on Rails | Ruby | Convention over Configuration + Layered |
| NestJS | TypeScript | Module 기반 Layered 구조 |

### 🔮 트렌드 & 전망

- **Layered → Hexagonal/Clean 진화**: 비즈니스 복잡도가 증가하면 Layered에서 출발하여 점진적으로 전환하는 패턴이 일반적
- **Vertical Slice Architecture**: 레이어 대신 **기능 단위**로 코드를 조직하는 대안이 부상
- **여전히 기본**: 대부분의 프레임워크와 튜토리얼이 Layered 기반이므로, 첫 번째로 배우는 아키텍처로서의 가치는 변함없음

### 💬 커뮤니티 인사이트

- "Layered Architecture의 가장 큰 문제는 아키텍처 자체가 아니라, **계층 경계를 지키지 않는 개발 문화**이다." [🟡 Likely]
- "복잡한 프로젝트에서 Layered를 쓴다면, 최소한 **Domain Layer에 Dependency Inversion**을 적용하라. 그것만으로도 테스트 용이성이 극적으로 향상된다." [🟡 Likely]

---

## 📎 Sources

1. [Catalog of Patterns of Enterprise Application Architecture — Martin Fowler](https://martinfowler.com/eaaCatalog/) — 1차 자료
2. [Layered Architecture — Herbertograca](https://herbertograca.com/2017/08/03/layered-architecture/) — 기술 블로그
3. [Layered Architecture: Still a Solid Approach — NDepend Blog](https://blog.ndepend.com/layered-architecture-solid-approach/) — 기술 블로그
4. [Layered Architecture — Baeldung](https://www.baeldung.com/cs/layered-architecture) — 기술 블로그
5. [The pros and cons of layered architecture — TechTarget](https://www.techtarget.com/searchapparchitecture/tip/The-pros-and-cons-of-a-layered-architecture-pattern) — 기술 블로그

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: Task 1 deep-research에서 수집
> - 수집 출처 수: 5
> - 출처 유형: 1차 자료 1, 기술 블로그 4
> - 모든 구성요소(7개) 빠짐없이 포함 확인: ✅
