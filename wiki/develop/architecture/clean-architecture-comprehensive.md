---
created: 2026-04-01
source: claude-code
tags: [architecture, python, fastapi, clean-architecture, concept-deep-dive, comprehensive]
---

# 📖 Clean Architecture — Concept Deep Dive (Comprehensive)

> 💡 **한줄 요약**: Clean Architecture는 소프트웨어를 **동심원 레이어**로 구성하고, **Dependency Rule(소스 코드 의존성은 오직 안쪽으로만)**을 핵심 원칙으로 삼아 비즈니스 로직을 프레임워크·DB·UI로부터 독립시키는 아키텍처 패턴이다.

---

## 1️⃣ 무엇인가? (What is it?)

**Clean Architecture**는 2012년 8월 13일 Robert C. Martin(Uncle Bob)이 블로그 포스트 *"The Clean Architecture"*에서 발표하고, 2017년 서적 *"Clean Architecture: A Craftsman's Guide to Software Structure and Design"*으로 정식화한 아키텍처 패턴이다.

### 공식 정의 (Bob Martin 원문)

> "소스 코드 의존성은 오직 **안쪽으로만** 향할 수 있다. 내부 원에 있는 어떤 것도 외부 원에 대해 알 수 없다." — [The Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

### 탄생 배경

Bob Martin은 여러 아키텍처 패턴들이 **공통된 목적**을 가지고 있음을 발견했다:
- **Hexagonal Architecture** (Cockburn, 2005) — Ports & Adapters
- **Onion Architecture** (Palermo, 2008) — DDD 레이어 + 의존성 역전
- **DCI** (Data, Context, Interaction) — Trygve Reenskaug & James Coplien

이 모든 패턴이 **"관심사의 분리를 레이어 설계를 통해 달성한다"**는 공통점을 가지고 있었고, Clean Architecture는 이를 **하나의 통합 원칙(Dependency Rule)**으로 정식화했다.

> 📌 **핵심 키워드**: `Dependency Rule`, `Entity`, `Use Case`, `Interface Adapter`, `Boundary`, `Controller`, `Presenter`, `Gateway`, `ViewModel`

---

## 2️⃣ 핵심 개념 (Core Concepts)

### 4-레이어 동심원 모델

```
┌───────────────────────────────────────────────────────────┐
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                                                      │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │                                                │  │  │
│  │  │  ┌──────────────────────────────────────────┐  │  │  │
│  │  │  │                                          │  │  │  │
│  │  │  │         ⭐ ENTITIES                      │  │  │  │
│  │  │  │    Enterprise Business Rules             │  │  │  │
│  │  │  │                                          │  │  │  │
│  │  │  └──────────────────────────────────────────┘  │  │  │
│  │  │                                                │  │  │
│  │  │            ⚙️ USE CASES                        │  │  │
│  │  │       Application Business Rules               │  │  │
│  │  │                                                │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │                                                      │  │
│  │               🔌 INTERFACE ADAPTERS                  │  │
│  │     Controllers, Presenters, Gateways                │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│                  🔧 FRAMEWORKS & DRIVERS                   │
│            Web, DB, Devices, External Interfaces           │
│                                                            │
└───────────────────────────────────────────────────────────┘

              의존성 방향: 밖 ──────────────→ 안
              (소스 코드 의존성은 오직 안쪽으로만)
```

### 10가지 구성요소 전체 목록

| 구성요소 | 레이어 | 역할 | 비유 |
|---|---|---|---|
| **Entity** | 1 (최내부) | Enterprise 범위 비즈니스 규칙 | 체스의 규칙 — 보드가 뭐든, 온라인이든 오프라인이든 규칙은 같다 |
| **Use Case (Interactor)** | 2 | Application 특화 비즈니스 규칙 | 체스 대회의 진행 규칙 — 시간 제한, 대진표 등 |
| **Interface Adapter** | 3 | Use Case ↔ 외부 간 데이터 변환 | 통역사 — 내부 언어와 외부 언어 사이 번역 |
| **Controller** | 3 | 사용자 입력 수신, Use Case 호출 | 접수 데스크 — 요청을 받아 담당자에게 전달 |
| **Presenter** | 3 | Use Case 결과를 표시용으로 포맷팅 | 리포터 — 결과를 읽기 쉬운 형태로 가공 |
| **ViewModel** | 3 | 레이어 간 전달되는 단순 데이터 구조 | 메모지 — 꼭 필요한 정보만 적혀있는 전달 수단 |
| **Gateway** | 3 | DB/외부 서비스용 인터페이스 | 창구 — 외부 시스템과의 소통 창구 |
| **Framework & Driver** | 4 (최외부) | 웹 프레임워크, DB, 외부 도구 | 건물의 외벽 — 내부를 보호하는 껍데기 |
| **Dependency Rule** | 전체 관통 | 소스 코드 의존성은 오직 안쪽으로만 | 중력 — 모든 것은 중심을 향한다 |
| **Boundary (I/O)** | 2-3 경계 | 레이어 간 제어 역전을 가능케 하는 인터페이스 | 국경 검문소 — 레이어 간 통과 규칙을 정의 |

---

### 구성요소별 상세 설명

#### 1. Entity

**정의**: **Enterprise 범위**의 비즈니스 규칙을 캡슐화하는 객체. 메서드를 가진 객체일 수도 있고, 데이터 구조와 함수의 집합일 수도 있다. 가장 **변경 가능성이 낮은** 핵심 레이어.

**비유**: 체스의 규칙. 나무 보드든 유리 보드든, 온라인이든 오프라인이든, 비숍은 대각선으로 움직인다. **보드(프레임워크)가 바뀌어도 규칙은 변하지 않는다.**

**역할**:
- 조직 전체에서 공유될 수 있는 비즈니스 규칙
- 외부 변경(UI, DB, 프레임워크)에 의해 바뀌지 않는 핵심 로직
- DDD의 Entity/Value Object/Aggregate와 대응

**연결관계**: Use Case에 의해 사용된다. 어떤 외부 레이어도 직접 Entity를 변경하지 못한다.

**Bob Martin 원문과의 차이**: Clean Architecture의 Entity는 DDD의 Entity와 다르다. **Enterprise 범위 비즈니스 규칙 전체**를 의미하며, DDD의 Entity + Value Object + Domain Service를 포괄한다.

```python
from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4
from enum import Enum

class OrderStatus(Enum):
    PENDING = "PENDING"
    PLACED = "PLACED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

@dataclass(frozen=True)
class Money:
    """Value Object — Enterprise 비즈니스 규칙"""
    amount: Decimal
    currency: str = "KRW"

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("통화가 다릅니다")
        return Money(self.amount + other.amount, self.currency)

@dataclass
class OrderItem:
    """Entity 내부 구성요소"""
    product_id: UUID
    quantity: int
    unit_price: Money

    @property
    def subtotal(self) -> Money:
        return Money(self.unit_price.amount * self.quantity, self.unit_price.currency)

@dataclass
class Order:
    """Entity — Enterprise 비즈니스 규칙"""
    id: UUID = field(default_factory=uuid4)
    customer_id: UUID = None
    status: OrderStatus = OrderStatus.PENDING
    items: list[OrderItem] = field(default_factory=list)

    def add_item(self, product_id: UUID, quantity: int, unit_price: Money):
        """비즈니스 규칙: PENDING 상태에서만 상품 추가 가능"""
        if self.status != OrderStatus.PENDING:
            raise ValueError("확정된 주문에 상품을 추가할 수 없습니다")
        self.items.append(OrderItem(product_id, quantity, unit_price))

    def place(self):
        """비즈니스 규칙: 상품이 있어야 주문 접수 가능"""
        if not self.items:
            raise ValueError("상품이 없는 주문은 접수할 수 없습니다")
        self.status = OrderStatus.PLACED

    @property
    def total(self) -> Money:
        if not self.items:
            return Money(Decimal("0"))
        return Money(
            sum(item.subtotal.amount for item in self.items),
            self.items[0].unit_price.currency,
        )
```

---

#### 2. Use Case (Interactor)

**정의**: **Application 특화** 비즈니스 규칙을 포함하는 객체. 시스템의 **데이터 흐름을 오케스트레이션**한다. Entity를 사용하여 유스케이스의 목적을 달성한다.

**비유**: 체스 대회의 진행 규칙. "시간 제한 5분, 3판 2선승" 같은 것은 체스 규칙(Entity)이 아니라 이 대회(Application)의 규칙이다.

**역할**:
- Application에 특화된 비즈니스 흐름 정의
- Entity에 작업 위임
- **Boundary(Input/Output)**를 통해 외부와 소통
- 이 레이어의 변경은 Entity에 영향을 주지 않는다
- 이 레이어는 Framework(DB, Web)의 변경에 영향받지 않는다

**연결관계**: Entity를 사용하고, Output Boundary를 통해 Presenter에 결과를 전달한다. Input Boundary를 구현하여 Controller의 호출을 받는다.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

# Input Boundary — Use Case의 입력 인터페이스
@dataclass
class PlaceOrderRequest:
    """Use Case Input DTO"""
    customer_id: str
    items: list[dict]  # [{product_id, quantity, price}]

# Output Boundary — Use Case의 출력 인터페이스
@dataclass
class PlaceOrderResponse:
    """Use Case Output DTO"""
    order_id: str
    total: str
    status: str

class PlaceOrderOutputBoundary(ABC):
    """Output Boundary — Presenter가 구현"""
    @abstractmethod
    def present_success(self, response: PlaceOrderResponse) -> None: ...

    @abstractmethod
    def present_error(self, error: str) -> None: ...

# Gateway — Use Case가 외부 자원에 접근하기 위한 인터페이스
class OrderGateway(ABC):
    """Gateway 인터페이스 — Use Case에서 정의"""
    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def find_by_id(self, order_id: UUID) -> Order | None: ...

class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, customer_id: str, amount: Decimal) -> bool: ...

# Use Case (Interactor) — Application 비즈니스 규칙
class PlaceOrderUseCase:
    """Use Case (Interactor) — Application 특화 비즈니스 규칙"""

    def __init__(
        self,
        order_gateway: OrderGateway,
        payment_gateway: PaymentGateway,
        presenter: PlaceOrderOutputBoundary,
    ):
        self._order_gateway = order_gateway
        self._payment_gateway = payment_gateway
        self._presenter = presenter

    def execute(self, request: PlaceOrderRequest) -> None:
        try:
            # 1. Entity 생성 및 비즈니스 규칙 실행
            order = Order(customer_id=UUID(request.customer_id))
            for item in request.items:
                order.add_item(
                    product_id=UUID(item["product_id"]),
                    quantity=item["quantity"],
                    unit_price=Money(Decimal(str(item["price"]))),
                )
            order.place()

            # 2. 외부 서비스 호출 (Gateway를 통해)
            success = self._payment_gateway.charge(
                request.customer_id, order.total.amount
            )
            if not success:
                self._presenter.present_error("결제에 실패했습니다")
                return

            # 3. 저장 (Gateway를 통해)
            self._order_gateway.save(order)

            # 4. 결과를 Presenter에 전달 (Output Boundary를 통해)
            self._presenter.present_success(
                PlaceOrderResponse(
                    order_id=str(order.id),
                    total=str(order.total.amount),
                    status=order.status.value,
                )
            )
        except ValueError as e:
            self._presenter.present_error(str(e))
```

---

#### 3. Interface Adapter

**정의**: Use Case와 Entity에게 가장 편리한 형태의 데이터를 **외부 에이전시(DB, Web 등)에 가장 편리한 형태**로 변환하는 레이어. MVC 아키텍처 전체가 이 레이어에 해당한다.

**비유**: 공항의 통역 서비스. 내부(국내)에서 사용하는 언어와 외부(해외)에서 사용하는 언어 사이를 번역한다.

**역할**: 데이터 형식 변환의 **중개자**. 내부 도메인 모델 ↔ 외부 데이터 형식 간 변환을 담당한다.

---

#### 4. Controller

**정의**: 사용자(또는 외부 시스템)의 입력을 **수신**하고, Use Case가 이해할 수 있는 형식으로 변환하여 **Use Case를 호출**하는 구성요소.

**비유**: 호텔의 프런트 데스크. 고객의 요청을 받아서 해당 부서(Use Case)에 전달한다.

**역할**: HTTP 요청 파싱, 입력 유효성 검사(형식 검증), Use Case Input DTO 생성, Use Case 호출.

**연결관계**: Framework & Driver 레이어(FastAPI)로부터 호출되고, Use Case의 Input Boundary를 호출한다.

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# Controller — Interface Adapter 레이어
router = APIRouter(prefix="/orders")

class PlaceOrderHTTPRequest(BaseModel):
    """외부 형식 (HTTP JSON)"""
    customer_id: str
    items: list[dict]

@router.post("/", status_code=201)
async def place_order_controller(
    http_request: PlaceOrderHTTPRequest,
    use_case: PlaceOrderUseCase = Depends(get_use_case),
):
    """Controller: 외부 HTTP 형식 → Use Case Input 형식으로 변환"""
    # 1. HTTP 요청을 Use Case Input DTO로 변환
    request = PlaceOrderRequest(
        customer_id=http_request.customer_id,
        items=http_request.items,
    )
    # 2. Use Case 실행
    use_case.execute(request)
    # Presenter가 결과를 ViewModel에 저장 (아래 참조)
```

---

#### 5. Presenter

**정의**: Use Case의 출력을 **표시(presentation)에 적합한 형태**로 포맷팅하는 구성요소. Use Case의 Output Boundary를 구현한다.

**비유**: 뉴스 앵커. 취재 기자(Use Case)가 가져온 사실을 시청자가 이해하기 쉬운 형태로 가공하여 전달한다.

**역할**:
- Use Case의 결과 데이터를 ViewModel로 변환
- 날짜 포맷팅, 통화 형식 변환, 에러 메시지 구성 등
- **Use Case는 Presenter가 어떻게 표시하는지 모른다** (Output Boundary로만 소통)

**연결관계**: Use Case의 Output Boundary를 구현. ViewModel을 생성하여 View(Framework)에 전달.

```python
@dataclass
class OrderViewModel:
    """ViewModel — 표시에 최적화된 데이터 구조"""
    order_id: str
    formatted_total: str  # "₩25,000"
    status_label: str     # "주문 접수됨"
    status_color: str     # "green"
    error_message: str | None = None

class FastAPIPresenter(PlaceOrderOutputBoundary):
    """Presenter — Use Case Output을 HTTP 응답용으로 변환"""

    def __init__(self):
        self.view_model: OrderViewModel | None = None

    def present_success(self, response: PlaceOrderResponse) -> None:
        self.view_model = OrderViewModel(
            order_id=response.order_id,
            formatted_total=f"₩{int(Decimal(response.total)):,}",
            status_label=self._status_to_korean(response.status),
            status_color="green",
        )

    def present_error(self, error: str) -> None:
        self.view_model = OrderViewModel(
            order_id="",
            formatted_total="",
            status_label="오류",
            status_color="red",
            error_message=error,
        )

    @staticmethod
    def _status_to_korean(status: str) -> str:
        mapping = {
            "PLACED": "주문 접수됨",
            "CONFIRMED": "주문 확정됨",
            "CANCELLED": "주문 취소됨",
        }
        return mapping.get(status, status)
```

---

#### 6. ViewModel

**정의**: 레이어 간 전달되는 **단순한 데이터 구조**. Entity나 DB row를 직접 전달하는 것이 아니라, **수신 측에 편리한 형태**로 가공된 데이터이다.

**비유**: 메모지. 꼭 필요한 정보만 간결하게 적혀있는 전달 수단. 원본 문서(Entity)를 통째로 넘기지 않는다.

**Bob Martin 원문**: "경계를 넘는 데이터는 **격리된 단순 데이터 구조**여야 한다. Entity나 DB row를 전달하지 마라."

**역할**: Presenter가 생성하여 View에 전달. Entity의 내부 구조가 외부에 노출되는 것을 방지.

**연결관계**: Presenter가 생성 → View(Framework)가 소비.

> (코드 예시는 위 Presenter 섹션의 `OrderViewModel` 참조)

---

#### 7. Gateway

**정의**: Use Case가 외부 자원(DB, 외부 API 등)에 접근하기 위한 **인터페이스 어댑터**. Hexagonal Architecture의 Output Port + Driven Adapter에 해당한다.

**비유**: 은행 창구. 고객(Use Case)은 창구 직원(Gateway 인터페이스)에게 요청하고, 창구 뒤에서 어떤 시스템(DB, 외부 API)을 사용하는지는 모른다.

**역할**:
- **인터페이스는 Use Case 레이어에서 정의** (안쪽)
- **구현은 Framework & Driver 레이어에서** (바깥쪽)
- Dependency Inversion으로 의존성 방향을 역전

**연결관계**: Use Case에서 정의(인터페이스), Framework에서 구현(구체 클래스).

```python
# Gateway 인터페이스 — Use Case 레이어에서 정의
class OrderGateway(ABC):
    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def find_by_id(self, order_id: UUID) -> Order | None: ...

# Gateway 구현 — Framework & Driver 레이어에서 구현
class SqlModelOrderGateway(OrderGateway):
    """Gateway 구현: SQLModel을 사용한 DB 접근"""

    def __init__(self, session: Session):
        self._session = session

    def save(self, order: Order) -> None:
        db_model = self._to_db_model(order)
        self._session.merge(db_model)
        self._session.commit()

    def find_by_id(self, order_id: UUID) -> Order | None:
        result = self._session.get(OrderDBModel, str(order_id))
        return self._to_domain(result) if result else None

    def _to_db_model(self, order: Order) -> OrderDBModel:
        """도메인 → DB 모델 변환"""
        return OrderDBModel(
            id=str(order.id),
            customer_id=str(order.customer_id),
            status=order.status.value,
            total=float(order.total.amount),
        )

    def _to_domain(self, db_model: OrderDBModel) -> Order:
        """DB 모델 → 도메인 변환"""
        order = Order(
            id=UUID(db_model.id),
            customer_id=UUID(db_model.customer_id),
            status=OrderStatus(db_model.status),
        )
        return order
```

---

#### 8. Framework & Driver

**정의**: 웹 프레임워크, 데이터베이스, 외부 도구 등 **기술적 세부사항**이 위치하는 최외부 레이어. Bob Martin은 이 레이어에 대해 "많은 코드를 쓰지 않는다"고 말했다.

**비유**: 건물의 외벽과 배관. 내부 공간(비즈니스 로직)을 보호하고 연결하는 인프라이다. 외벽을 바꿔도 내부 구조에는 영향이 없다.

**역할**:
- FastAPI, SQLModel, Redis 등 기술적 구현을 담당
- 가능한 한 **최소한의 접착 코드**만 작성
- Gateway 인터페이스의 구현체를 제공
- 애플리케이션의 **진입점(main, app factory)** 포함

**연결관계**: Interface Adapter를 통해서만 내부에 접근. 직접 Entity나 Use Case를 호출하지 않는다.

```python
# Framework & Driver — FastAPI 앱 설정 (진입점)
from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine, Session

app = FastAPI(title="Order Service")

# DB 설정 — Framework 레이어
engine = create_engine("postgresql://user:pass@localhost/orders")

def get_session():
    with Session(engine) as session:
        yield session

# 의존성 조립 — Configurator 역할
def get_use_case():
    session = next(get_session())
    presenter = FastAPIPresenter()
    return PlaceOrderUseCase(
        order_gateway=SqlModelOrderGateway(session),
        payment_gateway=StripePaymentGateway(api_key="sk_live_..."),
        presenter=presenter,
    )

# Router 등록
app.include_router(router)
```

---

#### 9. Dependency Rule (의존성 규칙)

**정의**: Clean Architecture의 **핵심 원칙**. 소스 코드 의존성은 오직 **안쪽으로만** 향할 수 있다.

> "내부 원에 있는 어떤 것도 외부 원에 대해 **전혀 알 수 없다**. 외부 원에서 선언된 이름(함수, 클래스, 변수 등)을 내부 원의 코드에서 **언급해서는 안 된다**." — Bob Martin

**비유**: 중력의 법칙. 모든 물체는 중심을 향해 끌린다. 중심(Entity)은 바깥(Framework)의 존재를 모르지만, 바깥은 중심에 의존한다.

**역할**: 이 규칙 하나가 Clean Architecture 전체를 작동시킨다. 위반하면 아키텍처가 무너진다.

**위반 시 일어나는 일**:
- Entity가 SQLAlchemy를 import → DB 변경 시 비즈니스 로직 수정 필요
- Use Case가 FastAPI를 import → 프레임워크 변경 시 유스케이스 수정 필요

```python
# ❌ Dependency Rule 위반 — Entity가 외부 프레임워크를 import
from sqlmodel import SQLModel, Field  # 외부 레이어!

class Order(SQLModel, table=True):  # Entity가 DB 프레임워크에 의존
    id: str = Field(primary_key=True)
    status: str

# ✅ Dependency Rule 준수 — Entity는 순수 Python
from dataclasses import dataclass

@dataclass
class Order:  # 순수 도메인 모델, 외부 의존성 없음
    id: UUID
    status: OrderStatus

    def place(self):
        if not self.items:
            raise ValueError("상품 없음")
        self.status = OrderStatus.PLACED
```

---

#### 10. Boundary (Input/Output)

**정의**: 레이어 간 **제어 역전(Inversion of Control)**을 가능케 하는 인터페이스. Use Case와 Interface Adapter 사이의 경계에 위치한다.

**비유**: 국경 검문소. 두 나라(레이어) 사이의 통과 규칙을 정의한다. 어떤 형태의 데이터만 통과할 수 있는지, 누가 누구를 호출할 수 있는지를 규정한다.

**Bob Martin 원문**: 경계를 넘는 데이터는 "격리된 단순 데이터 구조(isolated, simple data structures)"여야 한다.

**2가지 종류**:

| Boundary | 방향 | 역할 | 구현 |
|---|---|---|---|
| **Input Boundary** | Controller → Use Case | Use Case의 입력 인터페이스 | Use Case가 직접 구현 (or 별도 인터페이스) |
| **Output Boundary** | Use Case → Presenter | Use Case의 출력 인터페이스 | Presenter가 구현 |

**역할**: Dependency Rule을 위반하지 않으면서 **제어 흐름과 의존성 방향을 분리**한다.

```
제어 흐름:   Controller ──→ Use Case ──→ Presenter
의존성 방향: Controller ──→ Use Case ←── Presenter
                                    ↑
                          Output Boundary
                       (Use Case에서 정의,
                        Presenter가 구현)
```

```python
# Input Boundary — Use Case의 입력 계약
class PlaceOrderInputBoundary(ABC):
    @abstractmethod
    def execute(self, request: PlaceOrderRequest) -> None: ...

# Output Boundary — Use Case의 출력 계약
class PlaceOrderOutputBoundary(ABC):
    @abstractmethod
    def present_success(self, response: PlaceOrderResponse) -> None: ...
    @abstractmethod
    def present_error(self, error: str) -> None: ...

# Use Case가 Input Boundary를 구현
class PlaceOrderUseCase(PlaceOrderInputBoundary):
    def __init__(self, presenter: PlaceOrderOutputBoundary, ...):
        self._presenter = presenter  # Output Boundary에 의존 (인터페이스)

    def execute(self, request: PlaceOrderRequest) -> None:
        # ... 비즈니스 로직 ...
        self._presenter.present_success(response)  # Output Boundary 호출

# Presenter가 Output Boundary를 구현
class FastAPIPresenter(PlaceOrderOutputBoundary):
    def present_success(self, response: PlaceOrderResponse) -> None:
        self.view_model = self._format(response)
```

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

```
┌───────────────────────────────────────────────────────────────┐
│                    Clean Architecture 요청 흐름                 │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  👤 사용자                                                     │
│    │ HTTP POST /orders                                        │
│    ▼                                                           │
│  ┌─────────────────────┐ Layer 4: Framework & Driver          │
│  │ FastAPI Router       │ (HTTP 수신)                          │
│  └──────────┬──────────┘                                      │
│             │                                                  │
│             ▼                                                  │
│  ┌─────────────────────┐ Layer 3: Interface Adapter           │
│  │ Controller           │ (HTTP → Input DTO 변환)              │
│  └──────────┬──────────┘                                      │
│             │ Input Boundary                                   │
│             ▼                                                  │
│  ┌─────────────────────┐ Layer 2: Use Case                    │
│  │ PlaceOrderUseCase    │ (Application 비즈니스 규칙)           │
│  │ (Interactor)         │                                      │
│  └──────┬───────┬──────┘                                      │
│         │       │                                              │
│    Gateway    Entity      Layer 1: Entity                      │
│    (Output    (비즈니스    (Enterprise 비즈니스 규칙)            │
│     Boundary)  규칙)                                           │
│         │                                                      │
│         ▼                                                      │
│  ┌─────────────────────┐ Layer 3: Interface Adapter           │
│  │ Gateway 구현         │ (도메인 → DB 모델 변환)               │
│  └──────────┬──────────┘                                      │
│             │                                                  │
│             ▼                                                  │
│  ┌─────────────────────┐ Layer 4: Framework & Driver          │
│  │ SQLModel / DB        │ (실제 DB 접근)                       │
│  └─────────────────────┘                                      │
│                                                                │
│  ┌─────────────────────┐ Layer 3: Interface Adapter           │
│  │ Presenter            │ (Output → ViewModel 변환)            │
│  └──────────┬──────────┘                                      │
│             │                                                  │
│             ▼                                                  │
│  ┌─────────────────────┐ Layer 4: Framework & Driver          │
│  │ FastAPI Response     │ (HTTP JSON 응답)                     │
│  └─────────────────────┘                                      │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (Step by Step)

1. **Step 1**: 사용자가 HTTP POST /orders 요청
2. **Step 2**: Framework(FastAPI)가 요청을 수신하여 Controller에 전달
3. **Step 3**: Controller가 HTTP 데이터를 Use Case Input DTO로 변환
4. **Step 4**: Controller가 Input Boundary를 통해 Use Case를 호출
5. **Step 5**: Use Case가 Entity를 생성/조작하여 비즈니스 규칙 실행
6. **Step 6**: Use Case가 Gateway(Output Boundary)를 통해 DB에 저장
7. **Step 7**: Use Case가 Output Boundary를 통해 Presenter에 결과 전달
8. **Step 8**: Presenter가 결과를 ViewModel로 변환
9. **Step 9**: Framework(FastAPI)가 ViewModel을 HTTP JSON으로 응답

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스

### 🎯 대표 유즈 케이스

| # | 유즈 케이스 | 설명 | 적합한 이유 |
|---|------------|------|------------|
| 1 | **중규모 이상 애플리케이션** | 팀이 3명 이상, 수개월 유지보수 | Use Case별 명확한 책임 분리 |
| 2 | **프레임워크 교체 가능성** | FastAPI → Django, 또는 React → Vue | Framework이 최외부 레이어 |
| 3 | **높은 테스트 커버리지** | 비즈니스 로직의 독립 테스트 필수 | Entity/Use Case가 프레임워크 무관 |
| 4 | **다중 배포 타겟** | 웹 + 모바일 + CLI | Interface Adapter만 다르게 구성 |
| 5 | **도메인 복잡도 중간~높음** | 단순 CRUD가 아닌 비즈니스 규칙 존재 | Entity + Use Case로 체계적 관리 |

### ✅ 베스트 프랙티스

1. **Dependency Rule을 기계적으로 검증**: 내부 레이어의 import 문에 외부 레이어 패키지가 없는지 CI에서 확인
2. **DTO를 경계마다 생성**: Entity를 직접 반환하지 말고, 레이어별 DTO/ViewModel을 사용
3. **Use Case를 작게 유지**: 하나의 Use Case = 하나의 유스케이스 (Single Responsibility)
4. **Framework 레이어를 얇게**: 가능한 한 최소한의 접착 코드만 작성

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ 장점 | **프레임워크 독립** | FastAPI → Django 교체 시 비즈니스 로직 변경 없음 |
| ✅ 장점 | **테스트 용이성** | Entity/Use Case를 DB/HTTP 없이 단위 테스트 가능 |
| ✅ 장점 | **명확한 의존성 규칙** | Dependency Rule 하나로 아키텍처 일관성 유지 |
| ✅ 장점 | **비즈니스 로직 보호** | 외부 변경이 핵심 로직에 영향 못 줌 |
| ✅ 장점 | **독립적 개발** | 각 레이어를 독립적으로 개발/교체 가능 |
| ❌ 단점 | **보일러플레이트 증가** | DTO, Boundary, Gateway 등 인터페이스 다수 필요 |
| ❌ 단점 | **과도한 간접 참조** | 단순 CRUD에 적용하면 불필요한 복잡도 |
| ❌ 단점 | **학습 곡선** | Boundary, Presenter, ViewModel 등 개념 이해 필요 |
| ❌ 단점 | **실무 해석 차이** | Bob Martin의 원문이 추상적이어서 팀마다 다르게 해석 |

### ⚖️ Trade-off 분석

```
프레임워크 독립   ◄──── Trade-off ────►  보일러플레이트 증가
테스트 용이성     ◄──── Trade-off ────►  간접 참조 복잡도
명확한 규칙       ◄──── Trade-off ────►  해석의 다양성
```

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 Clean vs Hexagonal vs Onion

| 비교 기준 | Clean | Hexagonal | Onion |
|---|---|---|---|
| **창시자** | Martin (2012) | Cockburn (2005) | Palermo (2008) |
| **핵심 원칙** | Dependency Rule | 안/밖 대칭 | 의존성 중심 향함 |
| **레이어 수** | 4 (명시) | 미정 (Port 수에 따라) | 4~5 (동심원) |
| **내부 구조** | Entity + Use Case | Hexagon (자유) | Domain Model + Service |
| **경계 정의** | Boundary (I/O) | Port + Adapter | 인터페이스 (ring) |
| **데이터 흐름** | Controller→UC→Presenter | Adapter→Port→App→Port→Adapter | 밖→안→밖 |
| **Presenter 개념** | ✅ 명시적 | ❌ 없음 | ❌ 없음 |
| **실무 구현** | 거의 동일 | 거의 동일 | 거의 동일 |

### 🔍 핵심 차이 요약

```
Clean Architecture               Hexagonal Architecture
──────────────────────    vs    ──────────────────────
4-레이어 동심원                    안/밖 대칭 (레이어 수 자유)
Dependency Rule 정식화            Port & Adapter 메커니즘
Presenter + ViewModel 명시        데이터 흐름 미정의
Hexagonal + Onion + DCI 통합      독립적 패턴
```

### 🤔 언제 무엇을 선택?

- **Clean Architecture를 선택하세요** → 팀 규모가 크고, 명확한 규칙(Dependency Rule)과 정형화된 레이어 구조가 필요한 경우
- **Hexagonal을 선택하세요** → 외부 기술 교체가 핵심 관심사이고, 내부 구조는 자유롭게 하고 싶은 경우
- 실무에서는 **거의 동일하게 적용된다**. 이름과 메타포만 다를 뿐 핵심 원칙은 같다.

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|------|-----------|------------|
| 1 | **Entity에 ORM 어노테이션** | Dependency Rule 위반 | 순수 도메인 모델 + 별도 DB 모델 |
| 2 | **Use Case에서 HTTP 응답 직접 반환** | 프레임워크 결합 | Presenter/ViewModel을 통해 변환 |
| 3 | **모든 프로젝트에 적용** | 단순 CRUD에 과잉 설계 | 복잡도가 있는 프로젝트에만 |
| 4 | **Boundary 없이 직접 호출** | 레이어 경계 무너짐 | Input/Output Boundary 인터페이스 사용 |
| 5 | **Entity를 DTO로 직접 전달** | 내부 모델이 외부에 노출 | 경계마다 별도 DTO 사용 |

### 🚫 Anti-Patterns

1. **Screaming Framework**: Entity가 프레임워크에 의존하여 "Django Entity", "FastAPI Entity"가 되는 것. Entity는 순수해야 한다.
2. **Anemic Use Case**: Use Case가 단순히 Gateway를 호출만 하고 비즈니스 로직이 없는 것. Use Case에는 Application 비즈니스 규칙이 있어야 한다.
3. **Boundary Skip**: Controller가 직접 Entity를 조작하거나, Use Case가 HTTP Response를 직접 만드는 것.

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|------|------|----------|
| 📖 원전 | The Clean Architecture | [Uncle Bob 블로그 (2012)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) |
| 📘 도서 | Clean Architecture (2017) | Robert C. Martin, Prentice Hall |
| 📘 실무서 | Architecture Patterns with Python | Harry Percival & Bob Gregory — Python + Clean |
| 📖 통합 가이드 | Explicit Architecture | [Herbertograca](https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/) |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리 | 언어/플랫폼 | 용도 |
|---|---|---|
| FastAPI + Depends | Python | DI 및 Configurator 구현 |
| [python-clean-architecture](https://github.com/pcah/python-clean-architecture) | Python | Clean Architecture 기반 프레임워크 |
| Spring Boot | Java | Clean Architecture 적용 사례 풍부 |
| NestJS | TypeScript | Module 기반 Clean Architecture |

### 🔮 트렌드 & 전망

- **Clean + DDD 조합**: Entity를 DDD의 Aggregate로 구현하는 패턴이 표준화
- **Vertical Slice Architecture와의 경쟁**: 기능 단위 슬라이싱 vs 레이어 단위 슬라이싱 논쟁
- **실무에서의 간소화**: Presenter/ViewModel을 생략하고 Use Case가 직접 DTO를 반환하는 실용적 변형이 흔함

### 💬 커뮤니티 인사이트

- "Clean Architecture의 핵심은 **Dependency Rule 하나**이다. 나머지는 이를 지키기 위한 수단일 뿐이다." [🟡 Likely — 다수 기술 블로그 공통 의견]
- "실무에서 Presenter + ViewModel까지 엄격하게 구현하는 경우는 드물다. Use Case가 직접 Response DTO를 반환하는 변형이 더 흔하다." [🟡 Likely]

---

## 📎 Sources

1. [The Clean Architecture — Robert C. Martin (원전, 2012)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) — 1차 자료
2. [Clean Architecture — Amazon (서적, 2017)](https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164) — 1차 자료
3. [Explicit Architecture — Herbertograca](https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/) — 기술 블로그
4. [Understanding Clean Architectures — DEV Community](https://dev.to/xoubaman/understanding-clean-architectures-33j0) — 기술 블로그
5. [Clean Architecture Deep Dive — Spaceteams](https://www.spaceteams.de/en/insights/clean-architecture-a-deep-dive-into-structured-software-design) — 기술 블로그

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: Task 1 deep-research에서 수집
> - 수집 출처 수: 5
> - 출처 유형: 1차 자료 2, 기술 블로그 3
> - 모든 구성요소(10개) 빠짐없이 포함 확인: ✅
