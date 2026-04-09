---
created: 2026-04-01
source: claude-code
tags: [architecture, python, fastapi, hexagonal-architecture, ports-and-adapters, concept-deep-dive, comprehensive]
---

# 📖 Hexagonal Architecture (Ports & Adapters) — Concept Deep Dive (Comprehensive)

> 💡 **한줄 요약**: Hexagonal Architecture는 애플리케이션을 **내부(비즈니스 로직)**와 **외부(기술 인프라)**로 나누고, **Port(인터페이스)**와 **Adapter(구현)**를 통해 연결함으로써 기술 독립성과 테스트 용이성을 달성하는 아키텍처 패턴이다.

---

## 1️⃣ 무엇인가? (What is it?)

**Hexagonal Architecture**는 2005년 Alistair Cockburn이 발표한 아키텍처 패턴이다 (HaT Technical Report, 2005.09.04, v0.9). 같은 해 7월에 **"Ports and Adapters"**로 개명되었다.

### 공식 정의 (Cockburn 원문)

> "애플리케이션이 사용자, 프로그램, 자동화 테스트, 배치 스크립트에 의해 동일하게 구동될 수 있게 하고, 최종 실행 환경의 장치와 데이터베이스로부터 **격리된 상태에서** 개발·테스트될 수 있게 한다."

### 탄생 배경

Cockburn은 1994년 OO 수업에서 MVC 패턴에서 영감받아 **모든 방향에 인터페이스**를 원했다. 같은 프로젝트에서 **DB 루프백 실패**를 경험하며 아키텍처적 사고의 필요성을 절감했다.

#### Layered Architecture의 3가지 문제

| # | 문제 | 설명 |
|---|------|------|
| 1 | **계층 경계 위반** | 사람들이 레이어의 "선"을 진지하게 받아들이지 않아 비즈니스 로직이 UI/DB로 누출 |
| 2 | **1차원의 한계** | 2개 이상의 포트가 있으면 위→아래 1차원 레이어 그림에 안 맞음 |
| 3 | **UI/DB 결합** | DB에 저장 프로시저, UI에 비즈니스 로직을 넣어 긴밀한 결합 발생 |

Hexagonal Architecture는 이 문제들을 **안/밖(inside/outside) 대칭 구조**로 해결했다. 레이어가 아니라 **육각형** 모양으로 그려서 계층적 사고를 깨뜨렸다.

> 📌 **핵심 키워드**: `Port`, `Adapter`, `Driving/Driven`, `Primary/Secondary`, `Hexagon`, `Configurator`, `Technology Agnostic`

---

## 2️⃣ 핵심 개념 (Core Concepts)

### 10가지 구성요소 전체 맵

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Hexagonal Architecture 전체 구조                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Primary Actor          ┌─────────────────────┐       Secondary Actor│
│  (사용자, 테스트,         │                     │       (DB, 이메일,   │
│   외부 프로그램)          │     HEXAGON         │        외부 API)     │
│                          │   (Application)     │                      │
│  ┌──────────────┐       │                     │       ┌────────────┐ │
│  │ Driving      │       │  ┌───────────────┐  │       │ Driven     │ │
│  │ Adapter      │──────▶│  │ Input Port    │  │       │ Adapter    │ │
│  │ (HTTP, CLI,  │       │  │ (Driving Port)│  │       │ (DB impl,  │ │
│  │  Test)       │       │  └───────┬───────┘  │       │  SMTP,     │ │
│  └──────────────┘       │          │          │       │  HTTP      │ │
│                          │          ▼          │       │  client)   │ │
│                          │  ┌───────────────┐  │       └─────▲──────┘ │
│                          │  │ Application   │  │             │        │
│                          │  │ Service       │  │             │        │
│                          │  │ (Use Case     │  │             │        │
│                          │  │  Orchestrator)│  │             │        │
│                          │  └───────┬───────┘  │             │        │
│                          │          │          │             │        │
│                          │          ▼          │             │        │
│                          │  ┌───────────────┐  │             │        │
│                          │  │ Output Port   │──┼─────────────┘        │
│                          │  │ (Driven Port) │  │                      │
│                          │  └───────────────┘  │                      │
│                          │                     │                      │
│                          └─────────────────────┘                      │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                     Configurator                              │    │
│  │  (DI Container / Factory — 어떤 Adapter를 사용할지 결정)       │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 구성요소별 상세 설명

#### 1. Hexagon (Application)

**정의**: 비즈니스 로직이 사는 **내부 영역**. 외부 기술(DB, HTTP, UI)에 대해 전혀 모른다.

**비유**: 레스토랑의 **주방**. 주방은 손님이 직접 왔든, 배달앱으로 주문했든, 전화로 주문했든 상관없이 같은 방식으로 요리한다. 주방은 주문이 어떻게 들어왔는지(Driving Adapter) 알 필요가 없다.

**역할**:
- 순수한 비즈니스 로직만 포함
- 프레임워크, DB, HTTP 등 기술적 관심사로부터 완전 독립
- Port를 통해서만 외부와 소통

**연결관계**: Input Port를 통해 외부에서 구동되고, Output Port를 통해 외부 자원을 사용한다.

```python
# Hexagon 내부 — 순수 비즈니스 로직 (프레임워크 의존성 없음)
class OrderDomain:
    """주문 도메인 모델 — Hexagon 내부"""

    def __init__(self, id: str, customer_id: str):
        self.id = id
        self.customer_id = customer_id
        self.items: list[OrderItem] = []
        self.status = "PENDING"

    def add_item(self, product_id: str, quantity: int, price: float):
        if self.status != "PENDING":
            raise ValueError("확정된 주문에 상품을 추가할 수 없습니다")
        self.items.append(OrderItem(product_id, quantity, price))

    def place(self):
        if not self.items:
            raise ValueError("상품이 없는 주문은 접수할 수 없습니다")
        self.status = "PLACED"

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)
```

---

#### 2. Port (포트)

**정의**: 애플리케이션과 외부 세계의 **통신 채널(인터페이스)**. Cockburn은 운영체제와 전자기기의 포트를 메타포로 사용했다 — "포트 프로토콜을 따르는 장치는 교체 가능하다."

**비유**: 전기 콘센트. 콘센트(Port)의 규격(인터페이스)만 맞으면 어떤 가전제품(Adapter)이든 꽂아서 쓸 수 있다. 콘센트는 뭐가 꽂혀있는지 모른다.

**역할**: 애플리케이션의 **의도(purpose)**를 정의하는 인터페이스. "무엇을 할 수 있는가"를 선언하되, "어떻게"는 Adapter가 결정한다.

**Port 수**: Cockburn 원문에 따르면 일반적으로 **2~4개** 포트가 적절하다.

**연결관계**: Hexagon의 경계에 위치. Adapter가 Port를 구현하거나 사용한다.

---

#### 3. Input Port (Driving Port)

**정의**: 외부 세계가 애플리케이션을 **구동(drive)**하기 위한 인터페이스. "애플리케이션이 제공하는 서비스"를 정의한다.

**비유**: 레스토랑의 **주문 카운터**. 손님(Primary Actor)이 주문을 넣는 창구이다. 직접 방문이든, 전화든, 앱이든 카운터의 메뉴(인터페이스)는 동일하다.

**역할**: 외부에서 애플리케이션에 요청할 수 있는 **유스케이스**를 명시한다.

**연결관계**: Application Service가 Input Port를 구현한다. Driving Adapter가 Input Port를 호출한다.

```python
from abc import ABC, abstractmethod

# Input Port — 주문 유스케이스 인터페이스
class PlaceOrderPort(ABC):
    """주문 접수 — Input Port (Driving Port)"""

    @abstractmethod
    def place_order(self, customer_id: str, items: list[dict]) -> str:
        """주문을 접수하고 주문 ID를 반환한다"""
        ...

class GetOrderPort(ABC):
    """주문 조회 — Input Port"""

    @abstractmethod
    def get_order(self, order_id: str) -> dict | None: ...

class CancelOrderPort(ABC):
    """주문 취소 — Input Port"""

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool: ...
```

---

#### 4. Output Port (Driven Port)

**정의**: 애플리케이션이 외부 자원을 **사용**하기 위한 인터페이스. "애플리케이션이 외부에 기대하는 서비스"를 정의한다.

**비유**: 레스토랑의 **식자재 주문서 양식**. 주방이 식자재를 주문할 때 사용하는 규격화된 양식이다. 어떤 납품업체(Driven Adapter)가 오든 양식만 맞으면 된다.

**역할**: 애플리케이션이 **필요로 하는 외부 서비스**를 인터페이스로 정의. DB, 이메일, 외부 API 등의 **계약(contract)**을 명시한다.

**연결관계**: Hexagon 내부에서 정의. Driven Adapter가 Output Port를 구현한다.

```python
# Output Port — 애플리케이션이 외부에 기대하는 인터페이스
class OrderRepositoryPort(ABC):
    """주문 저장/조회 — Output Port (Driven Port)"""

    @abstractmethod
    def save(self, order: OrderDomain) -> None: ...

    @abstractmethod
    def find_by_id(self, order_id: str) -> OrderDomain | None: ...

    @abstractmethod
    def find_by_customer(self, customer_id: str) -> list[OrderDomain]: ...

class NotificationPort(ABC):
    """알림 발송 — Output Port"""

    @abstractmethod
    def send_order_confirmation(self, order_id: str, customer_email: str) -> None: ...

class PaymentPort(ABC):
    """결제 처리 — Output Port"""

    @abstractmethod
    def charge(self, customer_id: str, amount: float) -> bool: ...
```

---

#### 5. Driving Adapter (Primary Adapter)

**정의**: 외부 세계의 신호를 **애플리케이션이 이해하는 형식으로 변환**하여 Input Port를 호출하는 구현체. 외부→Hexagon 방향.

**비유**: 레스토랑의 **접수 직원**. 손님의 다양한 요청(구두, 전화, 앱)을 주방이 이해하는 주문서(Input Port)로 변환한다.

**역할**: HTTP 요청 → 도메인 명령, CLI 인자 → 도메인 명령, 테스트 코드 → 도메인 명령 등의 **프로토콜 변환**을 수행한다.

**연결관계**: Input Port를 **사용**(호출)한다. Primary Actor의 신호를 Input Port로 전달한다.

**주요 예시**: REST Controller, GraphQL Resolver, CLI Handler, gRPC Server, 테스트 코드

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# Driving Adapter — FastAPI REST Controller
router = APIRouter(prefix="/orders")

class PlaceOrderRequest(BaseModel):
    customer_id: str
    items: list[dict]

class OrderResponse(BaseModel):
    order_id: str
    status: str
    total: float

@router.post("/", response_model=dict, status_code=201)
async def place_order_endpoint(
    request: PlaceOrderRequest,
    use_case: PlaceOrderPort = Depends(get_place_order_port),  # Input Port 주입
):
    """Driving Adapter: HTTP 요청 → Input Port 호출"""
    order_id = use_case.place_order(
        customer_id=request.customer_id,
        items=request.items,
    )
    return {"order_id": order_id}

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_endpoint(
    order_id: str,
    use_case: GetOrderPort = Depends(get_get_order_port),
):
    """Driving Adapter: HTTP GET → Input Port 호출"""
    order = use_case.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    return OrderResponse(**order)
```

```python
# Driving Adapter — 테스트 코드 (FIT 테스트의 현대적 형태)
def test_place_order():
    """테스트도 Driving Adapter이다"""
    # Configurator: 테스트용 Adapter 조립
    repo = InMemoryOrderRepository()
    notifier = FakeNotifier()
    payment = FakePaymentGateway(always_succeed=True)
    use_case = OrderService(repo, notifier, payment)

    # Input Port 호출
    order_id = use_case.place_order(
        customer_id="cust-1",
        items=[{"product_id": "prod-1", "quantity": 2, "price": 10000}],
    )

    # 검증
    saved = repo.find_by_id(order_id)
    assert saved is not None
    assert saved.status == "PLACED"
    assert saved.total == 20000
```

---

#### 6. Driven Adapter (Secondary Adapter)

**정의**: Output Port를 **구현**하여 애플리케이션의 요청을 실제 외부 기술로 변환하는 구현체. Hexagon→외부 방향.

**비유**: 레스토랑의 **식자재 배달 기사**. 주방이 요청한 식자재 주문서(Output Port)를 받아서 실제로 시장에 가서 물건을 사온다. 시장(DB)이든, 마트(다른 DB)든, 온라인 주문(외부 API)이든 가능하다.

**역할**: DB 저장, 이메일 발송, HTTP 외부 API 호출, 메시지 큐 발행 등 **기술적 구현**을 담당한다.

**연결관계**: Output Port를 **구현**한다. Secondary Actor와 실제 통신한다.

**주요 예시**: PostgreSQL Repository, SMTP Email Sender, Stripe Payment Client, Redis Cache

```python
from sqlmodel import Session, select

# Driven Adapter — SQLModel 기반 DB 구현
class SqlModelOrderRepository(OrderRepositoryPort):
    """Driven Adapter: Output Port를 DB 기술로 구현"""

    def __init__(self, session: Session):
        self._session = session

    def save(self, order: OrderDomain) -> None:
        db_model = self._to_db_model(order)
        self._session.merge(db_model)
        self._session.commit()

    def find_by_id(self, order_id: str) -> OrderDomain | None:
        stmt = select(OrderDBModel).where(OrderDBModel.id == order_id)
        result = self._session.exec(stmt).first()
        return self._to_domain(result) if result else None

    def find_by_customer(self, customer_id: str) -> list[OrderDomain]:
        stmt = select(OrderDBModel).where(OrderDBModel.customer_id == customer_id)
        results = self._session.exec(stmt).all()
        return [self._to_domain(r) for r in results]

# Driven Adapter — InMemory 구현 (테스트용)
class InMemoryOrderRepository(OrderRepositoryPort):
    """Driven Adapter: 테스트용 in-memory 구현"""

    def __init__(self):
        self._store: dict[str, OrderDomain] = {}

    def save(self, order: OrderDomain) -> None:
        self._store[order.id] = order

    def find_by_id(self, order_id: str) -> OrderDomain | None:
        return self._store.get(order_id)

    def find_by_customer(self, customer_id: str) -> list[OrderDomain]:
        return [o for o in self._store.values() if o.customer_id == customer_id]
```

```python
# Driven Adapter — 이메일 알림 구현
class SmtpNotificationAdapter(NotificationPort):
    """Driven Adapter: SMTP를 통한 알림 발송"""

    def __init__(self, smtp_host: str, smtp_port: int):
        self._host = smtp_host
        self._port = smtp_port

    def send_order_confirmation(self, order_id: str, customer_email: str) -> None:
        msg = MIMEText(f"주문 {order_id}이 접수되었습니다.")
        msg["Subject"] = "주문 확인"
        msg["To"] = customer_email
        with smtplib.SMTP(self._host, self._port) as server:
            server.send_message(msg)

# Driven Adapter — 테스트용 Fake
class FakeNotifier(NotificationPort):
    def __init__(self):
        self.sent: list[tuple[str, str]] = []

    def send_order_confirmation(self, order_id: str, customer_email: str) -> None:
        self.sent.append((order_id, customer_email))
```

---

#### 7. Primary Actor (1차 액터)

**정의**: 애플리케이션과의 상호작용을 **시작(initiate)**하는 외부 주체.

**비유**: 레스토랑에 오는 **손님**. 손님이 먼저 주문을 한다 (상호작용을 시작).

**역할**: 애플리케이션을 구동하는 주체. Driving Adapter를 통해 Input Port에 접근한다.

**주요 예시**:
- 사용자 (웹 브라우저를 통해)
- 자동화 테스트 스크립트
- 배치 프로세스
- 다른 시스템의 API 호출
- CLI 사용자

**Cockburn 원문**: "Primary Actor의 자연스러운 테스트 어댑터는 FIT이다. 왜냐하면 FIT이 애플리케이션을 구동(drive)하기 때문이다."

---

#### 8. Secondary Actor (2차 액터)

**정의**: 애플리케이션이 **조회하거나 통보하는** 외부 주체. 애플리케이션이 대화를 시작한다.

**비유**: 레스토랑의 **식자재 납품업체**. 주방이 필요할 때 납품업체에 주문한다 (애플리케이션이 시작).

**역할**: 애플리케이션이 필요로 하는 외부 자원을 제공하는 주체. Driven Adapter를 통해 Output Port에 연결된다.

**주요 예시**:
- 데이터베이스
- 외부 결제 서비스 (Stripe, PayPal)
- 이메일 서비스 (SendGrid, SMTP)
- 파일 스토리지 (S3, GCS)
- 메시지 큐 (RabbitMQ, Kafka)

**Cockburn 원문**: "Secondary Actor의 자연스러운 테스트 어댑터는 mock이다. 왜냐하면 애플리케이션이 대화를 시작하기 때문이다."

```
Primary Actor                               Secondary Actor
(대화를 시작하는 쪽)                           (대화에 응답하는 쪽)

👤 사용자 ──→ [Driving Adapter]              [Driven Adapter] ──→ 🗄️ DB
🤖 테스트 ──→ [Driving Adapter]              [Driven Adapter] ──→ 📧 이메일
📋 배치   ──→ [Driving Adapter]   HEXAGON    [Driven Adapter] ──→ 💳 결제
🖥️ 외부앱 ──→ [Driving Adapter]              [Driven Adapter] ──→ 📁 S3
```

---

#### 9. Configurator (설정자)

**정의**: 어떤 Adapter 인스턴스를 사용할지 **선택하는 메커니즘**. 실행 환경(프로덕션, 테스트, 개발)에 따라 다른 Adapter를 조립한다.

**비유**: 레스토랑의 **매니저**. 오늘 어떤 납품업체를 쓸지, 배달 서비스는 어떤 걸 쓸지 결정한다.

**역할**: Hexagonal Architecture의 **조립 포인트**. Dependency Injection(DI) 컨테이너, Factory 패턴, 또는 main() 함수에서 구현된다.

**연결관계**: Hexagon 외부에 위치하며, Adapter와 Port를 **연결(wire)**한다.

**Cockburn 원문**: Gerard Meszaros가 2011년에 **"Configurable Dependency"** 마스터 패턴으로 명명. "인터페이스에서 기술을 바꾸는" 핵심 메커니즘.

```python
# Configurator — FastAPI 의존성 주입을 통한 조립
from functools import lru_cache

# 프로덕션 Configurator
def create_production_dependencies():
    """프로덕션 환경: 실제 DB + SMTP + Stripe"""
    session = get_db_session()
    return {
        "order_repo": SqlModelOrderRepository(session),
        "notifier": SmtpNotificationAdapter("smtp.gmail.com", 587),
        "payment": StripePaymentAdapter(api_key="sk_live_..."),
    }

# 테스트 Configurator
def create_test_dependencies():
    """테스트 환경: InMemory + Fake"""
    return {
        "order_repo": InMemoryOrderRepository(),
        "notifier": FakeNotifier(),
        "payment": FakePaymentGateway(always_succeed=True),
    }

# FastAPI DI를 통한 Configurator
def get_place_order_port() -> PlaceOrderPort:
    deps = create_production_dependencies()
    return OrderService(
        order_repo=deps["order_repo"],
        notifier=deps["notifier"],
        payment=deps["payment"],
    )
```

---

#### 10. Application Service

**정의**: Port 뒤에서 **Use Case를 오케스트레이션**하는 서비스. Input Port를 구현하고, Output Port를 사용한다.

**비유**: 레스토랑의 **주방장(Head Chef)**. 주문(Input Port)을 받아서 각 요리사(도메인 로직)에게 지시하고, 식자재 창고(Output Port)에서 재료를 가져온다.

**역할**: Input Port의 구현체. 도메인 객체에 작업을 위임하고, Output Port를 통해 외부 자원을 사용한다.

**연결관계**: Input Port를 **구현**하고, Output Port를 **사용**한다. Hexagon 내부에 위치한다.

```python
class OrderService(PlaceOrderPort, GetOrderPort, CancelOrderPort):
    """Application Service — Input Port 구현, Output Port 사용"""

    def __init__(
        self,
        order_repo: OrderRepositoryPort,    # Output Port
        notifier: NotificationPort,          # Output Port
        payment: PaymentPort,                # Output Port
    ):
        self._order_repo = order_repo
        self._notifier = notifier
        self._payment = payment

    def place_order(self, customer_id: str, items: list[dict]) -> str:
        # 1. 도메인 객체 생성 (Hexagon 내부 로직)
        order = OrderDomain(id=str(uuid4()), customer_id=customer_id)
        for item in items:
            order.add_item(item["product_id"], item["quantity"], item["price"])

        # 2. 도메인 로직 실행
        order.place()

        # 3. 결제 처리 (Output Port 사용)
        success = self._payment.charge(customer_id, order.total)
        if not success:
            raise PaymentFailedError("결제에 실패했습니다")

        # 4. 저장 (Output Port 사용)
        self._order_repo.save(order)

        # 5. 알림 발송 (Output Port 사용)
        self._notifier.send_order_confirmation(order.id, f"{customer_id}@example.com")

        return order.id

    def get_order(self, order_id: str) -> dict | None:
        order = self._order_repo.find_by_id(order_id)
        if not order:
            return None
        return {"order_id": order.id, "status": order.status, "total": order.total}

    def cancel_order(self, order_id: str) -> bool:
        order = self._order_repo.find_by_id(order_id)
        if not order:
            return False
        order.cancel()
        self._order_repo.save(order)
        return True
```

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

```
┌──────────────────────────────────────────────────────────────────┐
│                     전체 요청 흐름                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  👤 사용자                                                        │
│    │ HTTP POST /orders                                           │
│    ▼                                                              │
│  ┌─────────────────────┐                                         │
│  │ Driving Adapter      │  FastAPI Router                        │
│  │ (REST Controller)    │  JSON → Command 변환                   │
│  └──────────┬──────────┘                                         │
│             │ use_case.place_order(...)                           │
│             ▼                                                     │
│  ┌─────────────────────┐                                         │
│  │ Input Port           │  PlaceOrderPort 인터페이스              │
│  └──────────┬──────────┘                                         │
│             │                                                     │
│             ▼                                                     │
│  ╔═══════════════════════════════════╗  ← HEXAGON 경계           │
│  ║ Application Service              ║                            │
│  ║ (OrderService)                   ║                            │
│  ║                                  ║                            │
│  ║  1. Order 도메인 객체 생성        ║                            │
│  ║  2. order.place() 비즈니스 로직   ║                            │
│  ║  3. payment.charge() → Output Port║                           │
│  ║  4. repo.save() → Output Port     ║                           │
│  ║  5. notifier.send() → Output Port ║                           │
│  ╚════════════╤══════════════════════╝                            │
│               │                                                   │
│               ▼                                                   │
│  ┌─────────────────────┐                                         │
│  │ Output Port          │  OrderRepositoryPort 인터페이스         │
│  └──────────┬──────────┘                                         │
│             │                                                     │
│             ▼                                                     │
│  ┌─────────────────────┐                                         │
│  │ Driven Adapter       │  SqlModelOrderRepository               │
│  │ (DB Implementation)  │  Domain → DB Model 변환                │
│  └──────────┬──────────┘                                         │
│             │ SQL INSERT                                          │
│             ▼                                                     │
│  🗄️ PostgreSQL                                                   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (Step by Step)

1. **Step 1**: Primary Actor(사용자)가 HTTP POST 요청 전송
2. **Step 2**: Driving Adapter(FastAPI Router)가 JSON을 파싱하여 도메인 명령으로 변환
3. **Step 3**: Input Port(PlaceOrderPort)의 메서드 호출
4. **Step 4**: Application Service(OrderService)가 도메인 객체를 생성하고 비즈니스 로직 실행
5. **Step 5**: Output Port(PaymentPort)를 통해 결제 처리
6. **Step 6**: Output Port(OrderRepositoryPort)를 통해 DB에 저장
7. **Step 7**: Output Port(NotificationPort)를 통해 확인 이메일 발송
8. **Step 8**: Driving Adapter가 결과를 HTTP 응답으로 변환하여 반환

### 핵심 설계 규칙

> **비즈니스 로직은 반드시 내부에 머물러야 한다. 내부에 속한 코드가 외부로 누출되어서는 안 된다.** — Cockburn 원문

- Hexagon 내부에서 외부 기술(FastAPI, SQLModel 등)을 **import 하지 않는다**
- 의존성 방향은 항상 **밖 → 안**
- Adapter가 Port를 구현하거나 사용하지, Port가 Adapter를 알지 못한다

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스

### 🎯 대표 유즈 케이스

| # | 유즈 케이스 | 설명 | 적합한 이유 |
|---|------------|------|------------|
| 1 | **다중 인터페이스 시스템** | REST + GraphQL + gRPC + CLI | 동일 로직에 다양한 Driving Adapter 연결 |
| 2 | **외부 서비스 교체가 잦은 시스템** | DB 마이그레이션, 결제 서비스 변경 | Driven Adapter만 교체하면 됨 |
| 3 | **테스트 주도 개발** | 높은 테스트 커버리지 요구 | Mock/Fake Adapter로 격리 테스트 |
| 4 | **마이크로서비스** | 서비스 간 독립 배포 | 각 서비스가 자체 Hexagon |
| 5 | **레거시 통합** | 레거시 DB/API와 연동 | ACL Adapter로 격리 |

### ✅ 베스트 프랙티스

1. **Port를 비즈니스 언어로 명명**: `OrderRepositoryPort`가 아니라 `OrderPersistencePort` (기술 중립적)
2. **Adapter를 얇게 유지**: 변환 로직만 포함, 비즈니스 로직 금지
3. **Port 수를 2~4개로 제한**: 너무 많으면 복잡도 증가
4. **Configurator를 명시적으로**: DI 컨테이너 또는 main()에서 조립 포인트를 명확히

### 🏢 실제 적용 사례

- **Netflix**: 비디오 스트리밍 핵심 로직을 다양한 디바이스(TV, 모바일, 웹)에서 동일하게 구동 — 다중 Driving Adapter 활용 [🟡 Likely]
- **go-hexagonal (RanchoCooper)**: Go 마이크로서비스 프레임워크, Hexagonal + DDD 조합으로 adapter/application/domain 구조 구현 [✅ Confirmed]

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ 장점 | **기술 독립성** | DB, 프레임워크 변경 시 비즈니스 로직 영향 없음 |
| ✅ 장점 | **테스트 용이성** | Mock/Fake Adapter로 완전 격리 테스트 가능 |
| ✅ 장점 | **유연한 배포** | 동일 로직을 REST, CLI, 배치 등 다양한 인터페이스로 배포 |
| ✅ 장점 | **명확한 경계** | 안/밖 경계가 Port로 명시되어 경계 위반 감지 용이 |
| ✅ 장점 | **교체 용이성** | Adapter 교체로 기술 스택 변경 가능 |
| ❌ 단점 | **초기 보일러플레이트** | Port 인터페이스 + Adapter 구현 = 코드량 증가 |
| ❌ 단점 | **과도한 간접 참조** | 단순 CRUD에 적용하면 불필요한 추상화 |
| ❌ 단점 | **내부 구조 미정의** | Hexagon 내부의 구조화 방법을 제시하지 않음 (DDD와 조합 필요) |
| ❌ 단점 | **학습 곡선** | Driving/Driven, Port/Adapter 개념 이해 필요 |

### ⚖️ Trade-off 분석

```
기술 독립성    ◄──── Trade-off ────►  초기 보일러플레이트
테스트 용이성  ◄──── Trade-off ────►  간접 참조 증가
유연한 배포    ◄──── Trade-off ────►  내부 구조 미정의
```

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 비교 매트릭스

| 비교 기준 | Hexagonal | Onion | Clean Architecture | Layered |
|---|---|---|---|---|
| **창시자** | Cockburn (2005) | Palermo (2008) | Martin (2012) | POSA (1996) |
| **핵심 메타포** | 안/밖 대칭 | 양파 껍질 | 동심원 | 수평 레이어 |
| **의존성 방향** | 밖→안 (Adapter→Port) | 밖→안 | 밖→안 (Dependency Rule) | 위→아래 |
| **내부 구조** | 미정의 | DDD 레이어 포함 | 4-레이어 정의 | 레이어별 관심사 |
| **경계 정의** | Port & Adapter | 인터페이스 (ring) | Boundary (Input/Output) | 레이어 경계 |
| **테스트 전략** | FIT + Mock Adapter | 인터페이스 대체 | 인터페이스 대체 | 레이어별 mock |
| **핵심 차별점** | 기술 교체 용이성 | DDD 통합 | Dependency Rule 정식화 | 단순함 |

### 🔍 핵심 차이 요약

```
Hexagonal                    Layered
──────────────────    vs    ──────────────────
안/밖 대칭                    위/아래 계층
Port & Adapter               Layer 경계
기술 교체 초점                관심사 분리 초점
내부 구조 자유                레이어 구조 고정
```

### 🤔 언제 무엇을 선택?

- **Hexagonal을 선택하세요** → 외부 기술 변경이 잦고, 다중 인터페이스가 필요하며, 테스트가 중요한 경우
- **Layered를 선택하세요** → 단순한 CRUD, 빠른 개발이 필요하고, 외부 기술 변경이 드문 경우
- **Hexagonal + DDD 조합** → 복잡한 비즈니스 도메인 + 기술 독립성 모두 필요한 경우

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|------|-----------|------------|
| 1 | **Port에 기술 용어 사용** | `SqlOrderPort` → 기술 종속 | `OrderPersistencePort` (비즈니스 언어) |
| 2 | **Adapter에 비즈니스 로직** | 경계 위반, 테스트 어려움 | Adapter는 변환만, 로직은 Hexagon에 |
| 3 | **Port가 너무 많음** | 복잡도 폭증 | 2~4개로 제한 (Cockburn 권고) |
| 4 | **Hexagon 내부에 프레임워크 import** | 기술 독립성 상실 | 순수 언어 코드만 사용 |
| 5 | **Configurator 생략** | Adapter 교체가 어려워짐 | DI 또는 main()에서 명시적 조립 |

### 🚫 Anti-Patterns

1. **Port-per-Method**: 메서드마다 Port를 만드는 것. 관련 메서드를 하나의 Port로 그룹화해야 한다.
2. **Adapter Leak**: Adapter의 기술적 타입(SQLAlchemy Session 등)이 Hexagon 내부로 전파되는 것.
3. **Pseudo-Hexagonal**: Port는 있지만 Adapter가 비즈니스 로직을 포함하여 사실상 Layered와 같아지는 것.

### ⚡ 성능 고려사항

- Port/Adapter 경계에서의 데이터 변환(Domain ↔ DB Model)은 성능 오버헤드를 발생시킨다
- 극도로 성능에 민감한 경로(hot path)에서는 직접 DB 접근을 고려할 수 있으나, 이는 아키텍처의 예외여야 한다

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|------|------|----------|
| 📖 원전 | Hexagonal Architecture | [alistair.cockburn.us](https://alistair.cockburn.us/hexagonal-architecture) |
| 📘 도서 | Hexagonal Architecture Explained | Cockburn & Garrido de Paz (2023) |
| 📖 인터뷰 | Interview with Cockburn | [hexagonalme](https://jmgarridopaz.github.io/content/interviewalistair.html) |
| 📖 통합 가이드 | Explicit Architecture | [herbertograca](https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/) |
| 📖 AWS 가이드 | Hexagonal Architecture Pattern | [AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/hexagonal-architecture.html) |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리 | 언어/플랫폼 | 용도 |
|---|---|---|
| [go-hexagonal](https://github.com/RanchoCooper/go-hexagonal) | Go | Hexagonal + DDD 프레임워크 |
| FastAPI + Depends | Python | DI를 통한 Configurator 구현 |
| Spring Framework | Java | `@Component`, `@Autowired`로 Port/Adapter 조립 |
| NestJS | TypeScript | Module 시스템으로 Hexagonal 구조 지원 |

### 🔮 트렌드 & 전망

- **Hexagonal + DDD**: DDD 커뮤니티가 2012년경부터 채택하여 "도메인 모델 주변에 벽을 쌓고 기술을 밀어내는" 용도로 사용 — Cockburn 인터뷰 원문
- **마이크로서비스**: 각 서비스가 자체 Hexagon으로 설계되는 패턴이 표준화
- **Clean Architecture와의 수렴**: 실무에서 Hexagonal과 Clean은 거의 동일하게 적용됨

### 💬 커뮤니티 인사이트

- "Hexagonal의 진짜 가치는 Port/Adapter 자체가 아니라, **'안에서 밖을 모른다'는 사고 방식**에 있다." — 실무자 공통 의견 [🟡 Likely]
- "Hexagon을 6각형으로 그리는 이유는 6이라는 숫자가 중요해서가 아니라, 포트와 어댑터를 삽입할 **공간을 확보**하기 위해서이다." — Cockburn 원문 [✅ Confirmed]

---

## 📎 Sources

1. [Hexagonal Architecture — Alistair Cockburn (원전, 2005)](https://alistair.cockburn.us/hexagonal-architecture) — 1차 자료
2. [Interview with Alistair Cockburn — Hexagonal Me](https://jmgarridopaz.github.io/content/interviewalistair.html) — 1차 자료
3. [Hexagonal Architecture Explained — Amazon](https://www.amazon.com/Hexagonal-Architecture-Explained-Alistair-Cockburn/dp/173751978X) — 서적
4. [AWS Prescriptive Guidance — Hexagonal Architecture](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/hexagonal-architecture.html) — 공식 문서
5. [Explicit Architecture — Herbertograca](https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/) — 기술 블로그
6. [go-hexagonal — RanchoCooper](https://github.com/RanchoCooper/go-hexagonal) — 실무 구현체
7. [Hexagonal Architecture — Wikipedia](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)) — 커뮤니티

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: Task 1 deep-research에서 수집 (추가 검색 불필요)
> - 수집 출처 수: 7
> - 출처 유형: 1차 자료 2, 공식 문서 1, 기술 블로그 1, 서적 1, 실무 구현체 1, 커뮤니티 1
> - 모든 구성요소(10개) 빠짐없이 포함 확인: ✅
