---
created: 2026-04-01
source: claude-code
tags: [architecture, python, fastapi, sqlmodel, ddd, clean-architecture, layered-architecture, hexagonal-architecture, comparison, comprehensive]
---

# 🏗️ 4대 아키텍처 종합 비교 — 연관관계, 상호보완/배타, 선택 가이드, Python 예제

> 💡 **한줄 요약**: DDD는 "무엇을 모델링할 것인가"의 **철학**, Layered/Clean/Hexagonal은 "어떻게 구조화할 것인가"의 **패턴**이다. 이들은 상호 배타적이 아니라 **조합하여 사용**하는 것이 실무의 정석이다.

---

## 📋 목차

1. [역사적 진화와 연관관계](#1-역사적-진화와-연관관계)
2. [상호보완 vs 배타 관계 분석](#2-상호보완-vs-배타-관계-분석)
3. [상황별 아키텍처 선택 가이드](#3-상황별-아키텍처-선택-가이드)
4. [동일 도메인 4가지 구현 비교 — Python/FastAPI](#4-동일-도메인-4가지-구현-비교)

---

## 1. 역사적 진화와 연관관계

### 📅 타임라인

```
1984  OSI 7-Layer Model ─── 레이어 개념의 원조
  │
1996  POSA Vol.1 ──────────── Layered Architecture 정식화
  │                             (Buschmann et al.)
  │                             수평 레이어, 위→아래 의존성
  │
  │   ⚠️ 문제 발생:
  │   - 계층 경계를 "선"으로만 그리니 사람들이 진지하게 안 받아들임
  │   - UI/DB에 비즈니스 로직 누출
  │   - 2개 이상의 포트가 있으면 1차원 그림에 안 맞음
  │
2002  Fowler ─────────────── PofEAA (Layered 실무 체계화)
  │                          Presentation, Domain, Data Source 3 레이어
  │
2003  Eric Evans ─────────── DDD (도메인 모델링 철학 + 전략/전술 설계)
  │                          "무엇을 모델링할 것인가"에 집중
  │                          내부 구조 정의 (Entity, Aggregate 등)
  │                          ⚠️ 외부 경계 관리는 미지정
  │
  │   💡 Cockburn은 1994년부터 "모든 방향에 인터페이스" 아이디어를 구상
  │      1994년 OO 수업에서 MVC 영감, DB 루프백 실패 경험
  │
2005  Alistair Cockburn ─── Hexagonal Architecture (Ports & Adapters)
  │                          Layered의 1차원 한계 해결
  │                          안/밖 대칭 구조
  │                          💡 DDD의 "외부 경계"를 관리하는 보완 패턴으로 채택됨
  │
2008  Jeffrey Palermo ───── Onion Architecture
  │                          DDD 레이어를 Hexagonal에 통합
  │                          의존성이 중심을 향하는 규칙 명시화
  │                          Hexagonal과 DDD의 "다리" 역할
  │
2012  Robert C. Martin ──── Clean Architecture
  │                          Hexagonal + Onion + DCI를 통합
  │                          Dependency Rule을 핵심 원칙으로 정식화
  │                          4-레이어 동심원 모델
  │
2017  Herberto Graça ────── Explicit Architecture
                              DDD + Hexagonal + Onion + Clean + CQRS
                              하나의 다이어그램으로 통합
```

### 🔗 인과관계 맵

```
┌──────────────────────────────────────────────────────────────────┐
│                    아키텍처 간 인과관계                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Layered (1996)                                                  │
│    │                                                              │
│    │ ⚠️ "계층 경계 위반, UI/DB 결합"                               │
│    │                                                              │
│    ├──────────────────────────────────────────┐                   │
│    │                                          │                   │
│    ▼                                          ▼                   │
│  Hexagonal (2005)                          DDD (2003)            │
│  "안/밖 대칭으로                             "도메인 모델링         │
│   경계 위반 방지"                             철학 + 전술 설계"     │
│    │                                          │                   │
│    │  💡 "DDD의 외부 경계를                    │                   │
│    │     관리하는 보완 패턴"                    │                   │
│    │     — Cockburn 인터뷰                     │                   │
│    │                                          │                   │
│    └──────────┬───────────────────────────────┘                   │
│               │                                                   │
│               ▼                                                   │
│          Onion (2008)                                             │
│          "DDD 레이어를 Hexagonal에 통합"                           │
│               │                                                   │
│               ▼                                                   │
│        Clean Architecture (2012)                                  │
│        "Hexagonal + Onion + DCI 통합,                             │
│         Dependency Rule 정식화"                                    │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 핵심 인과관계 요약

| 원인 | 결과 | 근거 |
|---|---|---|
| Layered의 **계층 경계 위반** | Hexagonal의 **안/밖 대칭** 탄생 | Cockburn 원문: "사람들이 레이어의 선을 진지하게 안 받아들인다" ✅ [Confirmed] |
| DDD의 **내부 구조 필요** + Hexagonal의 **외부 경계 관리** | **상호보완적 조합** 형성 | Cockburn 인터뷰: "DDD는 내부 코드 조직, Hexagonal은 외부 경계 관리" ✅ [Confirmed] |
| Onion이 **DDD + Hexagonal 통합** | Clean Architecture가 이를 **정식화** | Bob Martin 원문: "Hexagonal, Onion, DCI 등 모두 공통 목적 공유" ✅ [Confirmed] |

---

## 2. 상호보완 vs 배타 관계 분석

### 📊 관계 매트릭스

```
              DDD     Hexagonal   Clean    Layered
DDD           —       🤝 상호보완  🤝 상호보완  ⚠️ 조건부
Hexagonal    🤝       —           🔄 수렴    ❌ 배타적
Clean        🤝       🔄          —          ❌ 배타적
Layered      ⚠️       ❌          ❌          —

🤝 = 상호보완   🔄 = 거의 동일   ❌ = 의존성 방향이 반대   ⚠️ = 조건부 호환
```

---

### 🤝 상호보완 관계

#### DDD + Hexagonal (가장 강력한 조합)

**왜 궁합이 맞는가:**
- DDD는 **Hexagon 내부**(비즈니스 로직)를 구조화한다: Entity, Aggregate, Domain Service 등
- Hexagonal은 **Hexagon 외부**(기술 경계)를 관리한다: Port & Adapter
- DDD는 외부 경계 관리를 **미지정**으로 남겼고, Hexagonal이 이를 **채운다**

```
┌────────────────────────────────────────────────────────┐
│                DDD + Hexagonal 조합                      │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Driving Adapter ──→ Input Port ──→ ┌────────────────┐ │
│  (HTTP, CLI, Test)                  │  HEXAGON 내부   │ │
│                                     │  (DDD가 채움)    │ │
│                                     │                  │ │
│                                     │  Aggregate Root  │ │
│                                     │  Entity          │ │
│                                     │  Value Object    │ │
│                                     │  Domain Service  │ │
│                                     │  Domain Event    │ │
│                                     │  Repository(IF)  │ │
│                                     │                  │ │
│  Driven Adapter ←── Output Port ←── └────────────────┘ │
│  (DB, Email, MQ)                                        │
│                                                         │
│  DDD = 내부 구조      Hexagonal = 외부 경계              │
└────────────────────────────────────────────────────────┘
```

#### DDD + Clean Architecture

DDD + Hexagonal과 매우 유사하지만, Clean Architecture의 **Dependency Rule**과 **Presenter/ViewModel** 개념이 추가된다.

- Entity = DDD의 Entity + Value Object + Aggregate
- Use Case = DDD의 Application Service
- Gateway = DDD의 Repository 인터페이스
- Presenter = 출력 변환 (DDD에서는 미정의)

---

### ❌ 배타적 관계

#### Layered vs Hexagonal/Clean: 의존성 방향이 반대

**핵심 차이**: 의존성 방향

| | Layered | Hexagonal/Clean |
|---|---|---|
| **Domain → Persistence** | Domain이 Persistence에 **의존** | Domain이 Persistence를 **모름** |
| **테스트** | DB 없이 Domain 테스트 어려움 | Mock Adapter로 완전 격리 테스트 |
| **DB 변경 영향** | Domain 코드 수정 필요 가능 | Adapter만 교체하면 됨 |

```
Layered (전통적):              Hexagonal/Clean:

Presentation                   Adapter (외부)
     │                               │
     ▼                               ▼
Application                    Port/Boundary (인터페이스)
     │                               │
     ▼                               ▼
Domain ──────► Persistence     Domain (중심, 외부를 모름)
(Domain이 DB에 의존!)                 ↑
                               Port/Boundary (인터페이스)
                                      ↑
                               Adapter (외부)
                               (Adapter가 Domain에 의존!)
```

**따라서**: 순수 Layered(Domain이 Persistence에 의존)와 Hexagonal/Clean(Domain이 중심에서 외부를 모름)은 **의존성 방향이 정반대**이므로 동시에 적용할 수 없다. 둘 중 하나를 선택해야 한다.

**단, "진화된 Layered"는 가능**: Layered Architecture에서 Domain Layer에 **Dependency Inversion Principle(DIP)**을 적용하면 사실상 Hexagonal/Clean과 동일해진다. 이것은 Layered의 "진화" 또는 "DIP가 적용된 Layered"이지, 순수 Layered는 아니다.

---

### 🔄 수렴 관계: Hexagonal ≈ Clean ≈ Onion

**실무에서 거의 동일하게 적용된다.** 이름과 메타포만 다를 뿐 핵심 원칙은 같다:

| 개념 | Hexagonal | Clean | Onion |
|---|---|---|---|
| 비즈니스 로직 위치 | Hexagon 내부 | Entity + Use Case | Domain Model |
| 외부 인터페이스 | Port | Boundary | 인터페이스 (ring) |
| 외부 구현체 | Adapter | Framework & Driver | Infrastructure |
| 의존성 규칙 | 밖→안 | Dependency Rule | 결합 방향 = 중심 |

---

### ⚠️ 조건부 호환: DDD + Layered

DDD는 원래 자체 4-레이어(UI, Application, Domain, Infrastructure)를 정의한다. 이것은 Layered Architecture와 유사하지만, **Infrastructure Layer가 Domain에 의존**하는 점에서 순수 Layered와 다르다 (DIP 적용).

Evans 원서의 DDD 레이어는 사실상 **"DIP가 적용된 Layered"**에 해당한다. 따라서:
- DDD + 순수 Layered = ⚠️ 가능하지만 Domain이 Persistence에 의존하는 한계
- DDD + DIP 적용 Layered = ✅ Evans 원서의 의도와 일치

---

## 3. 상황별 아키텍처 선택 가이드

### 🔀 의사결정 플로우차트

```
[프로젝트 시작]
    │
    ▼
비즈니스 로직이 복잡한가? ─── No ──→ 단순 CRUD? ─── Yes ──→ ✅ Layered (Basic)
    │                                    │
   Yes                                  No
    │                                    │
    ▼                                    ▼
도메인 전문가                      중간 복잡도
협업 가능?                        외부 연동 많음?
    │                                    │
   Yes                    ├─── Yes ──→ ✅ Hexagonal
    │                     │
    ▼                     └─── No ───→ ✅ Clean Architecture
DDD + Hexagonal                         (Use Case 중심)
또는
DDD + Clean
    │
    ▼
✅ DDD + Hexagonal (가장 강력)
   - Aggregate, Entity, Domain Event
   - Port & Adapter
   - 완전한 기술 독립성
```

### 📊 상황별 추천 매트릭스

| 상황 | 추천 아키텍처 | 이유 |
|---|---|---|
| **내부 관리 도구, 간단 CRUD** | Layered | 직관적, 빠른 개발, 모든 팀원 이해 가능 |
| **MVP / 프로토타입** | Layered | 최소 설계로 시작, 나중에 진화 가능 |
| **중규모 SaaS (3~10명 팀)** | Clean Architecture | Use Case 중심, 명확한 의존성 규칙 |
| **외부 API 연동이 많은 서비스** | Hexagonal | Adapter 교체 용이, 기술 독립성 |
| **복잡한 비즈니스 도메인 (금융, 보험, 물류)** | DDD + Hexagonal | 도메인 모델링 + 기술 독립성 |
| **마이크로서비스** | DDD + Hexagonal 또는 Clean | Bounded Context = 서비스 경계 |
| **레거시 현대화** | Hexagonal + ACL | 레거시를 Adapter로 격리 |
| **높은 테스트 커버리지 요구** | Hexagonal 또는 Clean | Mock Adapter/Gateway로 격리 테스트 |
| **팀의 아키텍처 경험 부족** | Layered → 점진적 진화 | 낮은 학습 곡선, 점진적 DIP 적용 |

### 진화 경로

```
Layered (시작)
    │
    │ 비즈니스 복잡도 증가
    │
    ▼
Layered + DIP (Domain Layer에 인터페이스 적용)
    │
    │ 외부 기술 교체 필요
    │
    ▼
Hexagonal / Clean (Port & Adapter / Boundary)
    │
    │ 도메인 복잡도 폭증
    │
    ▼
DDD + Hexagonal / Clean (최종 형태)
```

---

## 4. 동일 도메인 4가지 구현 비교

**도메인**: 주문(Order) — 고객이 상품을 주문하고, 결제하고, 주문을 관리하는 시나리오

### 프로젝트 구조 비교

```
# 1. Layered Architecture
layered_order/
├── presentation/          # Controller, DTO
│   ├── router.py
│   └── schemas.py
├── service/               # Application Service
│   └── order_service.py
├── domain/                # Entity, Business Rules
│   └── order.py
├── persistence/           # Repository, DB Model
│   ├── models.py
│   └── order_repository.py
└── main.py

# 2. Hexagonal Architecture
hexagonal_order/
├── adapters/              # Driving + Driven Adapters
│   ├── inbound/
│   │   └── rest_api.py    # Driving Adapter (HTTP)
│   └── outbound/
│       ├── db_adapter.py  # Driven Adapter (DB)
│       └── email_adapter.py
├── ports/                 # Input + Output Ports
│   ├── inbound/
│   │   └── order_port.py  # Input Port (인터페이스)
│   └── outbound/
│       ├── order_repo_port.py
│       └── notification_port.py
├── domain/                # Hexagon 내부
│   ├── order.py
│   └── order_service.py   # Application Service
└── config.py              # Configurator

# 3. Clean Architecture
clean_order/
├── entities/              # Layer 1: Enterprise Rules
│   └── order.py
├── use_cases/             # Layer 2: Application Rules
│   ├── place_order.py
│   └── gateways.py        # Gateway 인터페이스
├── interface_adapters/    # Layer 3: Adapters
│   ├── controllers/
│   │   └── order_controller.py
│   ├── presenters/
│   │   └── order_presenter.py
│   └── gateways/
│       └── sql_order_gateway.py
├── frameworks/            # Layer 4: Frameworks
│   ├── fastapi_app.py
│   └── db.py
└── main.py

# 4. DDD + Hexagonal (최종 형태)
ddd_hexagonal_order/
├── order_context/                 # Bounded Context
│   ├── domain/                    # Domain Layer
│   │   ├── model/
│   │   │   ├── order.py           # Aggregate Root
│   │   │   ├── order_item.py      # Entity
│   │   │   ├── money.py           # Value Object
│   │   │   └── order_status.py    # Value Object (Enum)
│   │   ├── service/
│   │   │   └── pricing_service.py # Domain Service
│   │   ├── event/
│   │   │   └── order_events.py    # Domain Event
│   │   ├── repository/
│   │   │   └── order_repo.py      # Repository Interface (Output Port)
│   │   ├── specification/
│   │   │   └── order_specs.py     # Specification
│   │   └── factory/
│   │       └── order_factory.py   # Factory
│   ├── application/               # Application Layer
│   │   ├── port/
│   │   │   └── place_order_port.py  # Input Port
│   │   ├── service/
│   │   │   └── order_app_service.py # Application Service
│   │   └── dto/
│   │       └── order_commands.py
│   ├── infrastructure/            # Infrastructure Layer
│   │   ├── persistence/
│   │   │   ├── models.py          # DB Model (Driven Adapter)
│   │   │   └── sql_order_repo.py  # Repository Impl
│   │   └── messaging/
│   │       └── event_publisher.py # Event Publisher
│   └── interface/                 # User Interface Layer
│       └── api/
│           ├── router.py          # Driving Adapter
│           └── schemas.py
├── shared_kernel/                 # Shared Kernel
│   └── base_entity.py
└── main.py                        # Configurator
```

---

### 구현 1: Layered Architecture

```python
# === domain/order.py === (Domain Layer)
from dataclasses import dataclass, field
from decimal import Decimal
from uuid import uuid4

@dataclass
class OrderItem:
    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity

@dataclass
class Order:
    id: str = field(default_factory=lambda: str(uuid4()))
    customer_id: str = ""
    status: str = "PENDING"
    items: list[OrderItem] = field(default_factory=list)

    def add_item(self, product_id: str, name: str, qty: int, price: Decimal):
        if self.status != "PENDING":
            raise ValueError("확정된 주문에 상품 추가 불가")
        self.items.append(OrderItem(product_id, name, qty, price))

    def place(self):
        if not self.items:
            raise ValueError("상품 없는 주문 불가")
        self.status = "PLACED"

    @property
    def total(self) -> Decimal:
        return sum(i.subtotal for i in self.items)


# === service/order_service.py === (Application/Service Layer)
class OrderService:
    def __init__(self, order_repo, product_repo):
        self._order_repo = order_repo      # Persistence Layer에 직접 의존
        self._product_repo = product_repo

    def place_order(self, customer_id: str, items: list[dict]) -> Order:
        order = Order(customer_id=customer_id)
        for item in items:
            product = self._product_repo.find_by_id(item["product_id"])
            order.add_item(product.id, product.name, item["quantity"], product.price)
        order.place()
        self._order_repo.save(order)
        return order


# === persistence/order_repository.py === (Persistence Layer)
from sqlmodel import Session, select

class SqlOrderRepository:
    """Layered: 구체 클래스에 직접 의존 (인터페이스 없음)"""
    def __init__(self, session: Session):
        self._session = session

    def save(self, order: Order) -> None:
        db_model = OrderDBModel(id=order.id, customer_id=order.customer_id,
                                 status=order.status, total=float(order.total))
        self._session.merge(db_model)
        self._session.commit()

    def find_by_id(self, order_id: str) -> Order | None:
        result = self._session.get(OrderDBModel, order_id)
        return self._to_domain(result) if result else None


# === presentation/router.py === (Presentation Layer)
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/orders")

@router.post("/", status_code=201)
async def create_order(request: dict, service: OrderService = Depends(get_service)):
    order = service.place_order(request["customer_id"], request["items"])
    return {"order_id": order.id, "total": float(order.total)}
```

**Layered의 특징**:
- `OrderService`가 `SqlOrderRepository`(구체 클래스)에 **직접 의존**
- 인터페이스/Port 없음 — 단순하지만 DB 교체 시 Service도 수정 필요
- 의존성: Presentation → Service → Domain → Persistence

---

### 구현 2: Hexagonal Architecture

```python
# === ports/inbound/order_port.py === (Input Port)
from abc import ABC, abstractmethod

class PlaceOrderPort(ABC):
    @abstractmethod
    def place_order(self, customer_id: str, items: list[dict]) -> str: ...

class GetOrderPort(ABC):
    @abstractmethod
    def get_order(self, order_id: str) -> dict | None: ...


# === ports/outbound/order_repo_port.py === (Output Port)
class OrderRepositoryPort(ABC):
    @abstractmethod
    def save(self, order: Order) -> None: ...
    @abstractmethod
    def find_by_id(self, order_id: str) -> Order | None: ...

class NotificationPort(ABC):
    @abstractmethod
    def send_confirmation(self, order_id: str) -> None: ...


# === domain/order_service.py === (Application Service — Hexagon 내부)
class OrderService(PlaceOrderPort, GetOrderPort):
    """Input Port를 구현, Output Port를 사용"""
    def __init__(self, repo: OrderRepositoryPort, notifier: NotificationPort):
        self._repo = repo          # Output Port (인터페이스)
        self._notifier = notifier  # Output Port (인터페이스)

    def place_order(self, customer_id: str, items: list[dict]) -> str:
        order = Order(customer_id=customer_id)
        for item in items:
            order.add_item(item["product_id"], item["name"],
                          item["quantity"], Decimal(str(item["price"])))
        order.place()
        self._repo.save(order)
        self._notifier.send_confirmation(order.id)
        return order.id

    def get_order(self, order_id: str) -> dict | None:
        order = self._repo.find_by_id(order_id)
        if not order:
            return None
        return {"order_id": order.id, "status": order.status, "total": float(order.total)}


# === adapters/outbound/db_adapter.py === (Driven Adapter)
class SqlModelOrderAdapter(OrderRepositoryPort):
    """Driven Adapter: Output Port를 DB 기술로 구현"""
    def __init__(self, session: Session):
        self._session = session

    def save(self, order: Order) -> None:
        db_model = OrderDBModel(id=order.id, customer_id=order.customer_id,
                                 status=order.status, total=float(order.total))
        self._session.merge(db_model)
        self._session.commit()

    def find_by_id(self, order_id: str) -> Order | None:
        result = self._session.get(OrderDBModel, order_id)
        return self._to_domain(result) if result else None


# === adapters/inbound/rest_api.py === (Driving Adapter)
router = APIRouter(prefix="/orders")

@router.post("/", status_code=201)
async def create_order(request: dict, port: PlaceOrderPort = Depends(get_port)):
    order_id = port.place_order(request["customer_id"], request["items"])
    return {"order_id": order_id}


# === config.py === (Configurator)
def create_order_service(session: Session) -> OrderService:
    """Configurator: Adapter와 Port를 연결"""
    repo = SqlModelOrderAdapter(session)
    notifier = SmtpNotificationAdapter("smtp.example.com")
    return OrderService(repo=repo, notifier=notifier)
```

**Hexagonal의 특징**:
- `OrderService`는 `OrderRepositoryPort`(인터페이스)에만 의존
- DB 교체 시 `SqlModelOrderAdapter`만 교체하면 됨
- `Configurator`가 조립 포인트를 명시적으로 관리

---

### 구현 3: Clean Architecture

```python
# === entities/order.py === (Layer 1: Entity — Enterprise Rules)
# (위의 Layered와 동일한 Order 도메인 모델 사용)


# === use_cases/gateways.py === (Gateway 인터페이스 — Use Case에서 정의)
class OrderGateway(ABC):
    @abstractmethod
    def save(self, order: Order) -> None: ...
    @abstractmethod
    def find_by_id(self, order_id: str) -> Order | None: ...


# === use_cases/place_order.py === (Layer 2: Use Case)
@dataclass
class PlaceOrderRequest:
    customer_id: str
    items: list[dict]

@dataclass
class PlaceOrderResponse:
    order_id: str
    total: str
    status: str

class PlaceOrderOutputBoundary(ABC):
    @abstractmethod
    def present_success(self, response: PlaceOrderResponse) -> None: ...
    @abstractmethod
    def present_error(self, error: str) -> None: ...

class PlaceOrderUseCase:
    def __init__(self, gateway: OrderGateway, presenter: PlaceOrderOutputBoundary):
        self._gateway = gateway
        self._presenter = presenter

    def execute(self, request: PlaceOrderRequest) -> None:
        try:
            order = Order(customer_id=request.customer_id)
            for item in request.items:
                order.add_item(item["product_id"], item["name"],
                              item["quantity"], Decimal(str(item["price"])))
            order.place()
            self._gateway.save(order)
            self._presenter.present_success(PlaceOrderResponse(
                order_id=order.id, total=str(order.total), status=order.status,
            ))
        except ValueError as e:
            self._presenter.present_error(str(e))


# === interface_adapters/presenters/order_presenter.py === (Layer 3: Presenter)
class FastAPIPresenter(PlaceOrderOutputBoundary):
    def __init__(self):
        self.view_model: dict = {}

    def present_success(self, response: PlaceOrderResponse) -> None:
        self.view_model = {
            "order_id": response.order_id,
            "total": f"₩{int(Decimal(response.total)):,}",
            "status": "주문 접수됨",
        }

    def present_error(self, error: str) -> None:
        self.view_model = {"error": error}


# === interface_adapters/controllers/order_controller.py === (Layer 3: Controller)
router = APIRouter(prefix="/orders")

@router.post("/", status_code=201)
async def place_order_controller(request: dict):
    presenter = FastAPIPresenter()
    session = next(get_session())
    gateway = SqlOrderGateway(session)
    use_case = PlaceOrderUseCase(gateway=gateway, presenter=presenter)

    use_case.execute(PlaceOrderRequest(
        customer_id=request["customer_id"],
        items=request["items"],
    ))

    if "error" in presenter.view_model:
        raise HTTPException(400, presenter.view_model["error"])
    return presenter.view_model  # ViewModel 반환
```

**Clean Architecture의 특징**:
- **Presenter + ViewModel** 패턴으로 출력 변환을 명시적으로 분리
- Use Case가 `PlaceOrderOutputBoundary`를 통해 Presenter에 결과를 **push**
- Controller → Use Case → Presenter 흐름 (제어 흐름과 의존성 방향 분리)

---

### 구현 4: DDD + Hexagonal (최종 형태)

```python
# === domain/model/money.py === (Value Object)
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "KRW"

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("통화 불일치")
        return Money(self.amount + other.amount, self.currency)

    def multiply(self, factor: int) -> "Money":
        return Money(self.amount * factor, self.currency)


# === domain/model/order.py === (Aggregate Root)
@dataclass
class Order:
    """Aggregate Root — 모든 불변식을 보장"""
    id: UUID
    customer_id: UUID
    status: OrderStatus = OrderStatus.PENDING
    _items: list["OrderItem"] = field(default_factory=list)
    _events: list = field(default_factory=list)

    def add_item(self, product_id: UUID, quantity: int, unit_price: Money):
        if self.status != OrderStatus.PENDING:
            raise DomainError("확정된 주문에 상품 추가 불가")
        if quantity <= 0:
            raise DomainError("수량은 1 이상")
        item = OrderItem(id=uuid4(), product_id=product_id,
                         quantity=quantity, unit_price=unit_price)
        self._items.append(item)

    def place(self):
        if not self._items:
            raise DomainError("상품 없는 주문 불가")
        self.status = OrderStatus.PLACED
        self._events.append(OrderPlacedEvent(
            order_id=self.id, customer_id=self.customer_id,
            total=self.total.amount,
        ))

    def cancel(self):
        if self.status in (OrderStatus.SHIPPED, OrderStatus.CANCELLED):
            raise DomainError("취소 불가 상태")
        self.status = OrderStatus.CANCELLED
        self._events.append(OrderCancelledEvent(order_id=self.id))

    @property
    def total(self) -> Money:
        if not self._items:
            return Money(Decimal("0"))
        return Money(sum(i.subtotal.amount for i in self._items))

    @property
    def items(self) -> tuple:
        return tuple(self._items)

    def collect_events(self) -> list:
        events = self._events.copy()
        self._events.clear()
        return events


# === domain/event/order_events.py === (Domain Event)
@dataclass(frozen=True)
class OrderPlacedEvent:
    order_id: UUID
    customer_id: UUID
    total: Decimal
    occurred_at: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class OrderCancelledEvent:
    order_id: UUID
    occurred_at: datetime = field(default_factory=datetime.utcnow)


# === domain/service/pricing_service.py === (Domain Service)
class PricingService:
    """도메인 서비스 — Entity에 속하지 않는 도메인 로직"""
    def calculate_price(self, product_id: UUID, quantity: int) -> Money:
        # 할인 정책, 대량 구매 할인 등 복잡한 가격 로직
        base_price = self._get_base_price(product_id)
        if quantity >= 10:
            return base_price.multiply(quantity).add(
                Money(Decimal("-1000"))  # 대량 구매 할인
            )
        return base_price.multiply(quantity)


# === domain/specification/order_specs.py === (Specification)
class HighValueOrderSpec(Specification):
    """10만원 이상 주문"""
    def is_satisfied_by(self, order: Order) -> bool:
        return order.total.amount >= Decimal("100000")

class PendingOrderSpec(Specification):
    def is_satisfied_by(self, order: Order) -> bool:
        return order.status == OrderStatus.PENDING


# === domain/factory/order_factory.py === (Factory)
class OrderFactory:
    @staticmethod
    def create(customer_id: UUID, items: list[dict],
               pricing: PricingService) -> Order:
        order = Order(id=uuid4(), customer_id=customer_id)
        for item in items:
            price = pricing.calculate_price(
                UUID(item["product_id"]), item["quantity"]
            )
            order.add_item(UUID(item["product_id"]), item["quantity"], price)
        return order


# === domain/repository/order_repo.py === (Repository Interface = Output Port)
class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None: ...
    @abstractmethod
    def find_by_id(self, order_id: UUID) -> Order | None: ...
    @abstractmethod
    def find_by_spec(self, spec: Specification) -> list[Order]: ...


# === application/port/place_order_port.py === (Input Port)
class PlaceOrderPort(ABC):
    @abstractmethod
    def execute(self, command: PlaceOrderCommand) -> UUID: ...


# === application/service/order_app_service.py === (Application Service)
class OrderApplicationService(PlaceOrderPort):
    def __init__(self, repo: OrderRepository, pricing: PricingService,
                 event_publisher: EventPublisher):
        self._repo = repo
        self._pricing = pricing
        self._events = event_publisher

    def execute(self, command: PlaceOrderCommand) -> UUID:
        # Factory로 Aggregate 생성
        order = OrderFactory.create(
            customer_id=command.customer_id,
            items=command.items,
            pricing=self._pricing,
        )
        # 비즈니스 규칙 실행
        order.place()
        # 저장
        self._repo.save(order)
        # Domain Event 발행
        for event in order.collect_events():
            self._events.publish(event)
        return order.id


# === infrastructure/persistence/sql_order_repo.py === (Driven Adapter)
class SqlModelOrderRepository(OrderRepository):
    def __init__(self, session: Session):
        self._session = session

    def save(self, order: Order) -> None:
        # Domain → DB Model 변환 후 저장
        ...

    def find_by_id(self, order_id: UUID) -> Order | None:
        # DB Model → Domain 변환 후 반환
        ...

    def find_by_spec(self, spec: Specification) -> list[Order]:
        all_orders = self._find_all()
        return [o for o in all_orders if spec.is_satisfied_by(o)]


# === interface/api/router.py === (Driving Adapter)
router = APIRouter(prefix="/orders")

@router.post("/", status_code=201)
async def place_order(request: PlaceOrderRequest,
                      port: PlaceOrderPort = Depends(get_port)):
    command = PlaceOrderCommand(
        customer_id=UUID(request.customer_id),
        items=request.items,
    )
    order_id = port.execute(command)
    return {"order_id": str(order_id)}
```

**DDD + Hexagonal의 특징**:
- **모든 DDD 구성요소** 포함: Aggregate Root, Entity, Value Object, Domain Event, Domain Service, Factory, Specification, Repository
- **Hexagonal 경계**: Input Port(PlaceOrderPort) + Output Port(OrderRepository, EventPublisher)
- **Application Service**가 Input Port를 구현하고, Output Port를 사용
- **Domain Event**가 Aggregate에서 발생하고, Application Service가 발행
- **Factory**가 복잡한 Aggregate 생성을 캡슐화
- **Specification**으로 복합 조건 쿼리 지원

---

### 📊 4가지 구현 비교 요약

| 비교 기준 | Layered | Hexagonal | Clean | DDD + Hexagonal |
|---|---|---|---|---|
| **코드량** | 최소 | 중간 | 중간~많음 | 많음 |
| **인터페이스 수** | 0~1개 | 4~6개 | 4~6개 | 6~10개 |
| **테스트 용이성** | 낮음 | 높음 | 높음 | 높음 |
| **기술 교체 비용** | 높음 | 낮음 | 낮음 | 최저 |
| **학습 곡선** | 낮음 | 중간 | 중간 | 높음 |
| **도메인 표현력** | 낮음 | 중간 | 중간 | 높음 |
| **적합 규모** | 소규모 | 중규모 | 중규모 | 대규모/복잡도메인 |
| **DDD 구성요소** | Entity만 | Entity + Port | Entity + UseCase | 전체 (17+) |

---

## 📎 Sources

1. [Hexagonal Architecture — Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture) — 원전
2. [The Clean Architecture — Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) — 원전
3. [Interview with Cockburn — Hexagonal Me](https://jmgarridopaz.github.io/content/interviewalistair.html) — 인터뷰
4. [Explicit Architecture — Herbertograca](https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/) — 통합 분석
5. [go-hexagonal — RanchoCooper](https://github.com/RanchoCooper/go-hexagonal) — 실무 구현체
6. [Onion Architecture — Jeffrey Palermo](https://jeffreypalermo.com/2008/07/the-onion-architecture-part-1/) — 원전
