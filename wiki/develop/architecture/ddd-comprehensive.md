---
created: 2026-04-01
source: claude-code
tags: [architecture, python, fastapi, sqlmodel, ddd, domain-driven-design, concept-deep-dive, comprehensive]
---

# 📖 Domain-Driven Design (DDD) — Concept Deep Dive (Comprehensive)

> 💡 **한줄 요약**: DDD는 복잡한 비즈니스 도메인을 소프트웨어 설계의 중심에 두고, 도메인 전문가와 개발자가 **공통 언어(Ubiquitous Language)**를 사용하여 **Bounded Context** 안에서 협업하는 소프트웨어 설계 접근법이다.

---

## 1️⃣ 무엇인가? (What is it?)

**Domain-Driven Design(DDD)**은 2003년 Eric Evans가 저서 *"Domain-Driven Design: Tackling Complexity in the Heart of Software"*에서 제시한 소프트웨어 설계 접근법이다.

### 공식 정의

Eric Evans의 정의에 따르면, DDD는 복잡한 소프트웨어 개발에서:
1. **핵심 도메인(Core Domain)**에 집중하고
2. 도메인 실무자와 소프트웨어 실무자가 **창조적 협업**으로 모델을 탐구하며
3. 명시적으로 정의된 **Bounded Context** 안에서 **Ubiquitous Language**를 사용한다

### 탄생 배경

현실 세계 비유: 건축가가 집을 지을 때 **거주자(도메인 전문가)**의 생활 패턴을 이해하지 못한 채 설계하면 불편한 집이 된다. 마찬가지로 소프트웨어도 비즈니스 도메인을 제대로 이해하지 못하면 쓸모없는 시스템이 된다. DDD는 이 **"비즈니스 현실과 코드 사이의 간극"**을 메우기 위해 등장했다.

### 핵심 차별점

DDD는 아키텍처 패턴이 **아닌** **설계 철학 + 방법론**이다. Layered, Hexagonal, Clean Architecture가 "어떻게 구조화할 것인가"를 다루는 반면, DDD는 **"무엇을 모델링할 것인가"**를 다룬다. 따라서 DDD는 다른 구조 패턴과 **조합하여 사용**해야 한다.

> 📌 **핵심 키워드**: `Ubiquitous Language`, `Bounded Context`, `Aggregate`, `Entity`, `Value Object`, `Repository`, `Domain Event`, `Context Map`, `Anti-Corruption Layer`

---

## 2️⃣ 핵심 개념 (Core Concepts)

DDD는 크게 **Strategic Design(전략적 설계)**과 **Tactical Design(전술적 설계)** 두 축으로 나뉜다.

```
┌─────────────────────────────────────────────────────────────────┐
│                      🏗️  DDD 전체 구조                           │
├────────────────────────────┬────────────────────────────────────┤
│   Strategic Design          │     Tactical Design               │
│   (큰 그림, 경계 설정)       │     (코드 수준, 빌딩 블록)         │
│                             │                                    │
│  ┌────────────────────┐    │    ┌────────────────────┐          │
│  │ Domain/Subdomain   │    │    │ Entity             │          │
│  ├────────────────────┤    │    ├────────────────────┤          │
│  │ Ubiquitous Language│    │    │ Value Object       │          │
│  ├────────────────────┤    │    ├────────────────────┤          │
│  │ Bounded Context    │    │    │ Aggregate          │          │
│  ├────────────────────┤    │    ├────────────────────┤          │
│  │ Context Map        │    │    │ Aggregate Root     │          │
│  │  (9가지 패턴)       │    │    ├────────────────────┤          │
│  ├────────────────────┤    │    │ Repository         │          │
│  │ Anti-Corruption    │    │    ├────────────────────┤          │
│  │ Layer              │    │    │ Domain Service     │          │
│  └────────────────────┘    │    ├────────────────────┤          │
│                             │    │ Application Service│          │
│                             │    ├────────────────────┤          │
│                             │    │ Infrastructure Svc │          │
│                             │    ├────────────────────┤          │
│                             │    │ Domain Event       │          │
│                             │    ├────────────────────┤          │
│                             │    │ Factory            │          │
│                             │    ├────────────────────┤          │
│                             │    │ Specification      │          │
│                             │    ├────────────────────┤          │
│                             │    │ Module             │          │
│                             │    └────────────────────┘          │
├────────────────────────────┴────────────────────────────────────┤
│                        DDD 4 레이어                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │   UI     │ │Application│ │  Domain  │ │ Infrastructure   │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

### 📐 Strategic Design (전략적 설계) — 5가지 구성요소

전략적 설계는 **큰 그림**을 다룬다. 시스템을 어떻게 나누고, 팀 간 어떻게 소통하며, 어디에 투자할지를 결정한다.

---

#### 1. Domain / Subdomain

**정의**: 소프트웨어가 다루는 지식과 활동의 범위. 비즈니스 전체를 여러 Subdomain으로 분류한다.

**비유**: 레스토랑이라는 Domain은 주방(Core), 예약(Supporting), 회계(Generic) 서브도메인으로 나뉜다.

| Subdomain 유형 | 설명 | 비유 | 투자 우선순위 | 구현 전략 |
|---|---|---|---|---|
| **Core Subdomain** | 비즈니스 핵심 경쟁력. 직접 개발 필수 | 레스토랑의 시그니처 레시피 | 최고 | 최고 인력 배치, DDD 전면 적용 |
| **Supporting Subdomain** | 핵심은 아니지만 비즈니스 운영에 필요 | 레스토랑의 예약 시스템 | 중간 | 내부 개발 또는 커스터마이징 |
| **Generic Subdomain** | 범용적 문제. 외부 솔루션 활용 가능 | 레스토랑의 회계 시스템 | 낮음 | 기성 솔루션 구매/위임 |

**역할**: Subdomain 분류를 통해 **어디에 투자할지** 결정한다. Core에 최고 인력과 DDD를 집중 적용하고, Generic은 기성 솔루션으로 처리한다.

**연결관계**: 각 Subdomain은 하나 이상의 Bounded Context로 구현된다.

```python
# 예시: 전자상거래 도메인의 Subdomain 분류
class SubdomainClassification:
    CORE = {
        "order_management": "주문 처리 — 비즈니스 핵심 경쟁력",
        "pricing_engine": "가격 정책 — 차별화 요소",
    }
    SUPPORTING = {
        "inventory": "재고 관리 — 운영에 필수이나 범용적",
        "customer_support": "고객 지원 — 비즈니스 특화 필요",
    }
    GENERIC = {
        "authentication": "인증 — Auth0 등 외부 솔루션 사용",
        "payment": "결제 — Stripe 등 외부 서비스",
        "notification": "알림 — SendGrid 등 외부 서비스",
    }
```

---

#### 2. Ubiquitous Language (보편 언어)

**정의**: 개발자와 도메인 전문가가 **같은 Bounded Context 안에서** 공유하는 일관된 용어 체계.

**비유**: 같은 교실에서 같은 교과서를 쓰는 것. "주문"이라는 단어가 주문팀에서는 "고객이 물건을 사는 행위"이고, 배송팀에서는 "창고에서 물건을 꺼내는 지시"일 수 있다. Ubiquitous Language는 **각 Context 안에서** 하나의 의미만 갖도록 보장한다.

**역할**: 코드, 문서, 대화에서 동일한 용어를 사용하여 소통 오류를 제거한다. **코드가 곧 도메인 모델**이 되어야 한다.

**연결관계**: Bounded Context마다 별도의 Ubiquitous Language가 존재한다. 같은 "Product"라는 단어도 카탈로그 Context와 배송 Context에서는 다른 의미를 가질 수 있다.

```python
# 잘못된 예: 용어가 모호함
class Item:
    def process(self): ...  # "처리"가 무엇인지 불명확

# 올바른 예: Ubiquitous Language 반영
class Order:
    def place(self): ...      # 주문을 "접수"한다
    def confirm(self): ...    # 주문을 "확정"한다
    def cancel(self): ...     # 주문을 "취소"한다
    def fulfill(self): ...    # 주문을 "이행"한다
```

---

#### 3. Bounded Context (경계 컨텍스트)

**정의**: 도메인 모델이 유효한 **명시적 경계**. 하나의 팀이 소유하고, 하나의 Ubiquitous Language가 적용되는 범위.

**비유**: 나라마다 다른 법률 체계. "결혼"이라는 개념이 한국과 미국에서 다른 법적 의미를 갖듯이, 같은 비즈니스 용어도 Bounded Context마다 다른 의미를 가질 수 있다.

**역할**: 모델의 경계를 명확히 하여 **모델 간 충돌을 방지**한다. 각 Context는 독립적으로 발전할 수 있다.

**연결관계**:
- 각 Bounded Context는 하나 이상의 Subdomain을 구현한다
- Context 간 관계는 Context Map으로 표현한다
- 각 Context 내부는 Tactical Design 구성요소로 구현한다

```
┌──────────────────────────────────────────────────────────────┐
│                    전자상거래 시스템                             │
│                                                               │
│  ┌─────────────────┐    ┌─────────────────┐                  │
│  │ 주문 Context     │    │ 배송 Context     │                  │
│  │                  │    │                  │                  │
│  │ Order = 고객이   │    │ Order = 창고에서  │                  │
│  │ 물건을 사는 행위  │    │ 물건을 꺼내는 지시│                  │
│  │                  │    │                  │                  │
│  │ Product = SKU +  │    │ Product = 무게 + │                  │
│  │ 가격 + 설명      │    │ 크기 + 보관조건   │                  │
│  └────────┬─────────┘    └────────┬─────────┘                │
│           │                       │                           │
│           └───────── ACL ─────────┘                           │
│                  (번역 계층)                                    │
└──────────────────────────────────────────────────────────────┘
```

```python
# 주문 Context의 Product
class CatalogProduct:
    id: str
    name: str
    price: Decimal
    description: str

# 배송 Context의 Product — 같은 "Product"이지만 다른 모델
class ShippingProduct:
    id: str
    weight_kg: float
    dimensions: Dimensions
    storage_condition: str  # "냉장", "상온" 등
```

---

#### 4. Context Map (컨텍스트 맵)

**정의**: Bounded Context 간의 **관계를 시각화**한 지도. 팀 간 커뮤니케이션, 거버넌스, "힘" 관계를 보여준다.

**비유**: 세계 지도에서 국가 간 동맹, 무역 관계, 국경 분쟁을 표시하는 것.

**역할**: 시스템 전체의 **통합 지형**을 한눈에 파악하고, 팀 간 협업 방식을 결정한다.

**9가지 Context Map 패턴:**

```
┌─────────────────────────────────────────────────────────────┐
│                  Context Map 패턴 분류                        │
├─────────────────────┬──────────────────┬────────────────────┤
│    Upstream 패턴     │   Midway 패턴    │  Downstream 패턴   │
│ (서비스 제공 측)      │ (대등한 관계)    │ (서비스 소비 측)    │
├─────────────────────┼──────────────────┼────────────────────┤
│ Open Host Service   │ Shared Kernel    │ Customer/Supplier  │
│ Event Publisher     │ Published Language│ Conformist         │
│                     │ Separate Ways    │ Anti-Corruption    │
│                     │ Partnership      │ Layer              │
└─────────────────────┴──────────────────┴────────────────────┘
```

| 패턴 | 관계 | 설명 | 비유 |
|---|---|---|---|
| **Open Host Service** | Upstream | 서브시스템에 접근할 수 있는 **공개 프로토콜** 제공. 대부분의 소비자를 수용 | 공공 도서관의 대출 시스템 |
| **Event Publisher** | Upstream | 도메인 이벤트를 메시징 시스템으로 발행. 하류가 구독하여 반응 | 뉴스 방송국 — 뉴스를 발행하면 구독자가 소비 |
| **Shared Kernel** | Midway | 두 팀이 **합의하에 공유**하는 도메인 모델의 부분집합 | 공동 소유 정원 — 변경 시 양쪽 합의 필요 |
| **Published Language** | Midway | 잘 문서화된 공유 언어(JSON Schema, Protobuf 등) | 국제 표준(ISO) — 양쪽이 따르는 공통 규격 |
| **Separate Ways** | Midway | 두 Context 간 **의미 있는 관계가 없음**. 독립적으로 존재 | 옆집과 우리집 — 각자 생활 |
| **Partnership** | Midway | 두 Context가 **함께 성공하거나 함께 실패**. 긴밀한 협력 필요 | 합작 투자 — 양쪽이 함께 일해야 성공 |
| **Customer/Supplier** | Downstream | 하류(Customer)가 상류(Supplier)에 요구사항 전달. 상류가 수용 | 식당과 식자재 납품업체 |
| **Conformist** | Downstream | 하류가 상류의 모델을 **그대로 따름**. 번역 없음 | 프랜차이즈 가맹점 — 본사 매뉴얼을 그대로 따라야 함 |
| **Anti-Corruption Layer** | Downstream | 외부 모델이 내부를 **오염시키지 않도록** 번역 계층을 둠 | 통역사 — 외국어를 내 언어로 번역 |

```python
# Anti-Corruption Layer 예시
class ExternalPaymentGateway:
    """외부 결제 서비스의 모델 (우리가 제어 불가)"""
    def charge(self, amount_cents: int, currency_code: str, card_token: str): ...

class PaymentACL:
    """ACL: 외부 모델을 내부 도메인 언어로 번역"""
    def __init__(self, gateway: ExternalPaymentGateway):
        self._gateway = gateway

    def process_payment(self, order_total: Money) -> PaymentResult:
        # 내부 Money 객체 → 외부 cents/currency 변환
        result = self._gateway.charge(
            amount_cents=order_total.to_cents(),
            currency_code=order_total.currency.code,
            card_token=self._get_token(),
        )
        # 외부 응답 → 내부 PaymentResult 변환
        return PaymentResult.from_gateway_response(result)
```

---

#### 5. Anti-Corruption Layer (ACL)

**정의**: 외부 시스템(레거시, 서드파티)의 모델이 내부 도메인 모델을 **오염시키지 않도록 보호**하는 번역 계층. Context Map 패턴이면서 동시에 **독립적인 설계 패턴**이기도 하다.

**비유**: 통역사. 외국어(외부 모델)를 내 언어(내부 도메인 모델)로 번역한다. 통역사가 없으면 외국어가 우리 대화에 침투하여 혼란을 일으킨다.

**역할**:
- 외부 시스템과의 **결합도를 최소화**
- 내부 도메인 모델의 **순수성 보호**
- 외부 변경이 내부에 미치는 영향을 **격리**

**연결관계**: Bounded Context의 경계에 위치하며, Repository, Application Service 등과 함께 Infrastructure Layer에서 구현된다.

```
외부 시스템          ACL           내부 도메인
┌──────────┐    ┌─────────┐    ┌──────────┐
│ 외부 모델  │ → │ 번역 계층 │ → │ 도메인    │
│ (변경 불가)│    │ (Adapter)│    │ 모델     │
└──────────┘    └─────────┘    └──────────┘
```

---

### 🔨 Tactical Design (전술적 설계) — 12가지 구성요소

전술적 설계는 **코드 수준**에서 도메인 모델을 구현하는 구체적인 빌딩 블록이다.

---

#### 6. Entity (엔티티)

**정의**: **고유 식별자(ID)**를 가지며, 시간이 지나도 동일성을 유지하는 가변 객체. 속성이 바뀌어도 ID가 같으면 같은 Entity이다.

**비유**: 주민등록번호가 있는 사람. 이름을 바꾸고, 나이가 들어도 주민등록번호가 같으면 같은 사람이다.

**역할**: 비즈니스에서 **고유하게 추적해야 하는 개념**을 표현한다.

**연결관계**: Aggregate의 구성원. Aggregate Root가 되거나, Root 아래의 내부 Entity가 된다.

```python
from dataclasses import dataclass, field
from uuid import UUID, uuid4

@dataclass
class Order:
    """주문 Entity — ID로 동등성 판단"""
    id: UUID = field(default_factory=uuid4)
    customer_id: UUID = field(default=None)
    status: str = "PENDING"
    items: list = field(default_factory=list)

    def __eq__(self, other):
        if not isinstance(other, Order):
            return False
        return self.id == other.id  # ID가 같으면 같은 Entity

    def __hash__(self):
        return hash(self.id)
```

---

#### 7. Value Object (값 객체)

**정의**: **식별자가 없는 불변 객체**. 속성값의 조합으로만 동등성을 판단한다. 같은 속성값이면 같은 Value Object이다.

**비유**: 지폐의 금액. 만원짜리 두 장은 "같은 만원"이다. 어떤 만원인지 구분할 필요가 없다.

**역할**: 도메인 개념을 **풍부하게 표현**하되, 추적이 불필요한 속성 묶음을 나타낸다.

**연결관계**: Entity나 Aggregate 내부에 포함된다. 독립적으로 영속화되지 않는다.

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)  # frozen=True → 불변
class Money:
    """금액 Value Object — 속성값으로 동등성 판단"""
    amount: Decimal
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("금액은 음수일 수 없습니다")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("통화가 다릅니다")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def to_cents(self) -> int:
        return int(self.amount * 100)

@dataclass(frozen=True)
class Address:
    """주소 Value Object"""
    street: str
    city: str
    zip_code: str
    country: str
```

---

#### 8. Aggregate (집합체)

**정의**: 관련된 Entity와 Value Object의 **일관성 경계(consistency boundary)** 클러스터. 데이터 변경의 단위이다.

**비유**: 쇼핑 카트. 카트와 카트 안의 상품들은 하나의 묶음으로 관리된다. 상품을 카트에 넣거나 뺄 때 카트 전체의 일관성이 유지되어야 한다.

**역할**: **트랜잭션 일관성의 경계**를 정의한다. Aggregate 내부는 항상 일관된 상태를 보장하고, Aggregate 간의 일관성은 eventual consistency로 처리한다.

**연결관계**:
- 하나의 Aggregate Root를 통해서만 접근 가능
- Repository는 Aggregate 단위로 저장/조회
- Aggregate 간 참조는 ID로만 (직접 객체 참조 금지)

**핵심 규칙**:
1. Aggregate Root만 외부에서 참조 가능
2. Aggregate 내부 객체에 직접 접근 금지
3. 하나의 트랜잭션에서 하나의 Aggregate만 수정
4. Aggregate 간 참조는 ID로만

```
┌─────────────────────────────────────────┐
│         Order Aggregate                  │
│  ┌───────────────────────────────────┐  │
│  │ Order (Aggregate Root)            │  │
│  │  - id: UUID                       │  │
│  │  - status: OrderStatus            │  │
│  │  - total: Money (VO)              │  │
│  │                                   │  │
│  │  ┌─────────────┐ ┌─────────────┐ │  │
│  │  │ OrderItem   │ │ OrderItem   │ │  │
│  │  │ (Entity)    │ │ (Entity)    │ │  │
│  │  │ - product_id│ │ - product_id│ │  │
│  │  │ - quantity  │ │ - quantity  │ │  │
│  │  │ - price(VO) │ │ - price(VO) │ │  │
│  │  └─────────────┘ └─────────────┘ │  │
│  └───────────────────────────────────┘  │
│                                          │
│  외부에서 접근: Order(Root)만 가능         │
│  OrderItem 직접 접근: ❌ 금지              │
└─────────────────────────────────────────┘
```

---

#### 9. Aggregate Root (집합 루트)

**정의**: Aggregate의 **진입점(entry point)**이 되는 Entity. 외부에서 Aggregate에 접근하려면 반드시 Root를 통해야 한다.

**비유**: 가족의 대표. 외부에서 가족과 거래할 때 대표를 통해야 하고, 대표가 가족 내부의 일관성(예: 가계 예산)을 보장한다.

**역할**:
- Aggregate 내부의 **불변식(invariant)** 보장
- 외부 접근의 **유일한 창구**
- Repository는 Aggregate Root 단위로 동작

**연결관계**: Repository에 저장/조회의 단위. Factory가 생성하는 대상.

```python
@dataclass
class Order:
    """Order는 Aggregate Root"""
    id: UUID
    customer_id: UUID
    status: OrderStatus = OrderStatus.PENDING
    _items: list[OrderItem] = field(default_factory=list)

    # Aggregate Root가 불변식을 보장
    def add_item(self, product_id: UUID, quantity: int, unit_price: Money):
        if self.status != OrderStatus.PENDING:
            raise DomainError("확정된 주문에는 상품을 추가할 수 없습니다")
        if quantity <= 0:
            raise DomainError("수량은 1 이상이어야 합니다")

        item = OrderItem(
            id=uuid4(),
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )
        self._items.append(item)

    def remove_item(self, item_id: UUID):
        if self.status != OrderStatus.PENDING:
            raise DomainError("확정된 주문에서 상품을 제거할 수 없습니다")
        self._items = [i for i in self._items if i.id != item_id]

    @property
    def total(self) -> Money:
        """총액 계산 — 불변식의 일부"""
        return sum(
            (item.subtotal for item in self._items),
            Money(Decimal("0"), "KRW"),
        )

    @property
    def items(self) -> tuple[OrderItem, ...]:
        """외부에 읽기 전용으로만 노출"""
        return tuple(self._items)
```

---

#### 10. Repository (저장소)

**정의**: Aggregate Root의 **영속성을 추상화**하는 컬렉션과 유사한 인터페이스. 도메인 코드가 데이터베이스 세부사항을 알 필요 없게 한다.

**비유**: 도서관의 검색 시스템. 책(Aggregate)을 찾고, 빌리고, 반납하는 인터페이스를 제공하지만, 책이 어떤 서가에 있는지(DB 구현)는 몰라도 된다.

**역할**:
- 도메인 레이어와 인프라 레이어를 **분리**
- Aggregate Root 단위로 저장(save)/조회(find)/삭제(delete) 제공
- **인터페이스는 Domain Layer**, 구현은 Infrastructure Layer

**연결관계**: Application Service가 Repository를 사용하여 Aggregate를 로드/저장한다.

```python
from abc import ABC, abstractmethod

# Domain Layer — 인터페이스 정의
class OrderRepository(ABC):
    """Repository 인터페이스 (Domain Layer에 위치)"""

    @abstractmethod
    def find_by_id(self, order_id: UUID) -> Order | None: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def find_by_customer(self, customer_id: UUID) -> list[Order]: ...

    @abstractmethod
    def next_identity(self) -> UUID: ...


# Infrastructure Layer — 구현
class SqlAlchemyOrderRepository(OrderRepository):
    """Repository 구현 (Infrastructure Layer에 위치)"""

    def __init__(self, session: Session):
        self._session = session

    def find_by_id(self, order_id: UUID) -> Order | None:
        row = self._session.get(OrderModel, order_id)
        return self._to_domain(row) if row else None

    def save(self, order: Order) -> None:
        model = self._to_model(order)
        self._session.merge(model)
        self._session.flush()
```

---

#### 11. Domain Service (도메인 서비스)

**정의**: 특정 Entity나 Value Object에 **자연스럽게 속하지 않는 도메인 로직**을 담는 **상태 없는(stateless)** 객체.

**비유**: 은행의 이체 처리 담당자. 출금 계좌와 입금 계좌 두 곳에 걸친 작업이므로 어느 계좌에도 속하지 않는다.

**역할**: 여러 Aggregate에 걸친 도메인 로직, 또는 단일 Entity에 어울리지 않는 비즈니스 규칙을 처리한다.

**연결관계**: Domain Layer에 위치. Ubiquitous Language의 동사(행위)를 표현한다.

**주의**: Domain Service에 로직을 너무 많이 넣으면 **Anemic Domain Model** 안티패턴이 된다. 가능하면 Entity/VO 내부에 로직을 넣고, 정말 어울리지 않는 경우에만 Domain Service를 사용한다.

```python
class TransferService:
    """계좌 이체 — 두 Account Aggregate에 걸친 로직"""

    def transfer(
        self,
        from_account: Account,
        to_account: Account,
        amount: Money,
    ) -> None:
        if from_account.balance < amount:
            raise InsufficientFundsError()

        from_account.withdraw(amount)
        to_account.deposit(amount)
        # 두 Aggregate의 변경은 Application Service가
        # 트랜잭션으로 묶어서 저장한다
```

---

#### 12. Application Service (애플리케이션 서비스)

**정의**: **Use Case(유스케이스)**를 오케스트레이션하는 서비스. 비즈니스 로직은 포함하지 않고, 도메인 객체에 작업을 **위임**한다.

**비유**: 오케스트라의 지휘자. 직접 연주하지 않지만, 각 악기(도메인 객체)에게 언제 연주할지 지시한다.

**역할**:
- 트랜잭션 경계 관리
- Repository를 통해 Aggregate 로드/저장
- Domain Service 호출
- 도메인 이벤트 발행
- 인프라 서비스 호출 (이메일, 메시지 큐 등)

**연결관계**: Application Layer에 위치. 도메인 로직은 Domain Layer에 위임한다.

**Domain Service와의 차이**: Application Service는 "어떤 순서로 호출할지" (workflow), Domain Service는 "비즈니스 규칙 자체"를 담당한다.

```python
class PlaceOrderUseCase:
    """주문 접수 — Application Service (Use Case)"""

    def __init__(
        self,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
        pricing_service: PricingService,  # Domain Service
        event_publisher: EventPublisher,  # Infrastructure
    ):
        self._order_repo = order_repo
        self._product_repo = product_repo
        self._pricing = pricing_service
        self._events = event_publisher

    def execute(self, command: PlaceOrderCommand) -> UUID:
        # 1. Aggregate 로드
        products = [
            self._product_repo.find_by_id(item.product_id)
            for item in command.items
        ]

        # 2. 도메인 로직 실행 (Aggregate/Domain Service에 위임)
        order = Order(
            id=self._order_repo.next_identity(),
            customer_id=command.customer_id,
        )
        for item, product in zip(command.items, products):
            price = self._pricing.calculate_price(product, item.quantity)
            order.add_item(product.id, item.quantity, price)

        order.place()  # 도메인 로직

        # 3. 저장
        self._order_repo.save(order)

        # 4. 이벤트 발행
        self._events.publish(OrderPlacedEvent(order_id=order.id))

        return order.id
```

---

#### 13. Infrastructure Service (인프라 서비스)

**정의**: 이메일 발송, 로깅, 파일 저장, 메시지 큐 등 **인프라 관심사**를 수행하는 서비스. Hexagonal Architecture에서는 "hexagon 외부"에 위치한다.

**비유**: 우체국. 편지(도메인 이벤트)를 보내는 일은 사업의 본질이 아니라 인프라이다.

**역할**: 기술적 구현을 캡슐화하여 도메인이 인프라에 의존하지 않게 한다.

**연결관계**: Infrastructure Layer에서 구현. 인터페이스는 Domain/Application Layer에서 정의한다.

```python
# Application Layer — 인터페이스
class EventPublisher(ABC):
    @abstractmethod
    def publish(self, event: DomainEvent) -> None: ...

class EmailSender(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> None: ...

# Infrastructure Layer — 구현
class RabbitMQEventPublisher(EventPublisher):
    def publish(self, event: DomainEvent) -> None:
        self._channel.basic_publish(
            exchange="domain_events",
            routing_key=event.event_type,
            body=json.dumps(event.to_dict()),
        )

class SmtpEmailSender(EmailSender):
    def send(self, to: str, subject: str, body: str) -> None:
        msg = MIMEText(body)
        msg["To"] = to
        msg["Subject"] = subject
        self._smtp.send_message(msg)
```

---

#### 14. Domain Event (도메인 이벤트)

**정의**: 도메인에서 발생한 **중요한 사건**을 표현하는 불변 객체. "과거에 일어난 일"을 기록한다.

**비유**: "주문이 접수되었습니다" 알림. 이미 일어난 사실을 기록하고, 관심 있는 사람(다른 Bounded Context)에게 알린다.

**역할**:
- Aggregate 간 **느슨한 결합** 실현
- Bounded Context 간 통신
- 이벤트 소싱(Event Sourcing)의 기반
- 감사(audit) 추적

**연결관계**: Aggregate에서 발생하고, Application Service가 수집하여 발행한다.

```python
from datetime import datetime

@dataclass(frozen=True)
class DomainEvent:
    """모든 도메인 이벤트의 기반"""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class OrderPlacedEvent(DomainEvent):
    """주문 접수 이벤트 — 과거형으로 명명"""
    order_id: UUID = None
    customer_id: UUID = None
    total_amount: Decimal = None

@dataclass(frozen=True)
class OrderCancelledEvent(DomainEvent):
    """주문 취소 이벤트"""
    order_id: UUID = None
    reason: str = ""

# Aggregate 내부에서 이벤트 수집
class Order:
    def __init__(self):
        self._events: list[DomainEvent] = []

    def place(self):
        self.status = OrderStatus.PLACED
        self._events.append(
            OrderPlacedEvent(
                order_id=self.id,
                customer_id=self.customer_id,
                total_amount=self.total.amount,
            )
        )

    def collect_events(self) -> list[DomainEvent]:
        events = self._events.copy()
        self._events.clear()
        return events
```

---

#### 15. Factory (팩토리)

**정의**: 복잡한 Aggregate나 Entity의 **생성 로직을 캡슐화**하는 객체. 객체가 생성 시점부터 항상 **유효한 상태**를 보장한다.

**비유**: 자동차 공장의 조립 라인. 부품을 조합하여 완성된 자동차(유효한 Aggregate)를 만든다. 불완전한 차는 출고하지 않는다.

**역할**: 생성 로직이 복잡할 때 클라이언트 코드를 단순화하고, 불변식을 생성 시점부터 보장한다.

**연결관계**: Domain Layer에 위치. Repository의 재구성(reconstitution)과 구별된다 — Factory는 "새로 만들기", Repository는 "기존 것 불러오기".

```python
class OrderFactory:
    """복잡한 Order Aggregate 생성을 캡슐화"""

    @staticmethod
    def create_order(
        customer_id: UUID,
        items: list[OrderItemDTO],
        shipping_address: Address,
        pricing_service: PricingService,
    ) -> Order:
        order = Order(
            id=uuid4(),
            customer_id=customer_id,
            shipping_address=shipping_address,
        )

        for item_dto in items:
            price = pricing_service.calculate_price(
                item_dto.product_id, item_dto.quantity
            )
            order.add_item(item_dto.product_id, item_dto.quantity, price)

        # 생성 시점에 불변식 검증
        if not order.items:
            raise DomainError("주문에는 최소 1개 이상의 상품이 필요합니다")

        return order
```

---

#### 16. Specification (명세)

**정의**: 비즈니스 규칙을 **재조합 가능한 단위**로 캡슐화하는 패턴. Boolean 로직으로 체이닝하여 복잡한 규칙을 표현한다.

**비유**: 쇼핑몰의 필터. "가격 1만원 이상 AND 카테고리 = 의류 AND (신상품 OR 세일 중)" 같은 복합 조건을 레고 블록처럼 조합할 수 있다.

**3가지 용도** (Evans 원서 기준):
1. **검증(Validation)**: 객체가 비즈니스 규칙을 만족하는지 확인
2. **선택(Selection)**: 컬렉션/DB에서 조건에 맞는 객체 조회
3. **생성(Creation)**: 조건을 만족하는 새 객체 생성

**연결관계**: Repository와 함께 사용하면 강력해진다 — Specification을 Repository에 전달하여 필터링.

```python
from abc import ABC, abstractmethod

class Specification(ABC):
    """기본 Specification 인터페이스"""

    @abstractmethod
    def is_satisfied_by(self, candidate) -> bool: ...

    def __and__(self, other: "Specification") -> "AndSpecification":
        return AndSpecification(self, other)

    def __or__(self, other: "Specification") -> "OrSpecification":
        return OrSpecification(self, other)

    def __invert__(self) -> "NotSpecification":
        return NotSpecification(self)

class AndSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate) -> bool:
        return self._left.is_satisfied_by(candidate) and self._right.is_satisfied_by(candidate)

class OrSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate) -> bool:
        return self._left.is_satisfied_by(candidate) or self._right.is_satisfied_by(candidate)

class NotSpecification(Specification):
    def __init__(self, spec: Specification):
        self._spec = spec

    def is_satisfied_by(self, candidate) -> bool:
        return not self._spec.is_satisfied_by(candidate)

# 사용 예시
class PremiumCustomerSpec(Specification):
    def is_satisfied_by(self, customer) -> bool:
        return customer.total_spent > Money(Decimal("100000"), "KRW")

class ActiveCustomerSpec(Specification):
    def is_satisfied_by(self, customer) -> bool:
        return customer.last_order_date > datetime.now() - timedelta(days=90)

# 조합: 프리미엄 AND 활성 고객
vip_spec = PremiumCustomerSpec() & ActiveCustomerSpec()
vip_customers = [c for c in customers if vip_spec.is_satisfied_by(c)]
```

---

#### 17. Module (모듈)

**정의**: 관련 클래스를 **그룹화**하는 조직 단위. Java의 패키지, Python의 모듈/패키지에 해당한다.

**비유**: 회사의 부서. 마케팅 부서에는 마케팅 관련 역할만, 개발 부서에는 개발 관련 역할만 배치한다.

**역할**:
- **높은 응집도**: 관련 개념을 한 곳에 모음
- **낮은 결합도**: 모듈 간 의존성 최소화
- Ubiquitous Language를 **코드 구조에 반영**

**연결관계**: 하나의 Bounded Context는 여러 Module을 포함할 수 있다.

```
# Python 프로젝트 구조 예시 — Module = 패키지
order_context/           # Bounded Context
├── domain/              # Domain Layer
│   ├── model/           # Module: 도메인 모델
│   │   ├── order.py     # Order Aggregate Root
│   │   ├── order_item.py# OrderItem Entity
│   │   └── money.py     # Money Value Object
│   ├── service/         # Module: Domain Service
│   │   └── pricing.py   # PricingService
│   ├── event/           # Module: Domain Event
│   │   └── order_events.py
│   ├── repository/      # Module: Repository 인터페이스
│   │   └── order_repo.py
│   └── specification/   # Module: Specification
│       └── customer_specs.py
├── application/         # Application Layer
│   ├── command/         # Module: 커맨드
│   └── use_case/        # Module: Use Case
├── infrastructure/      # Infrastructure Layer
│   ├── persistence/     # Module: DB 구현
│   └── messaging/       # Module: 메시지 큐
└── interface/           # User Interface Layer
    └── api/             # Module: REST API
```

---

### 🏢 DDD 4 레이어

Evans 원서에서 정의한 DDD의 4 레이어 아키텍처:

```
┌─────────────────────────────────────────────────────────┐
│                 🖥️  User Interface Layer                  │
│  사용자에게 정보 표현, 명령 해석                            │
│  (REST Controller, GraphQL Resolver, CLI)                │
├─────────────────────────────────────────────────────────┤
│                 ⚙️  Application Layer                     │
│  비즈니스 로직 없음. 작업 진행 상태만 관리.                  │
│  도메인 객체에 작업 위임. 트랜잭션 경계.                     │
│  (Application Service, Use Case, Command Handler)        │
├─────────────────────────────────────────────────────────┤
│                 🏗️  Domain Layer                          │
│  비즈니스 규칙과 로직의 핵심.                               │
│  Entity, VO, Aggregate, Domain Service, Event, Spec      │
│  ⭐ 이 레이어가 DDD의 심장이다                             │
├─────────────────────────────────────────────────────────┤
│                 💾  Infrastructure Layer                  │
│  기술적 지원. DB, 메시지 큐, 이메일, 외부 API               │
│  Repository 구현, ACL 구현                                │
└─────────────────────────────────────────────────────────┘

의존성 방향: UI → Application → Domain ← Infrastructure
                                  ↑
                      Infrastructure가 Domain의
                      인터페이스를 구현 (DIP)
```

---

#### 18. User Interface Layer

**정의**: 사용자(또는 외부 시스템)에게 **정보를 표현**하고 **명령을 해석**하는 계층.

**역할**: HTTP 요청 파싱, 응답 포맷팅, 입력 유효성 검사(형식 검증). **비즈니스 로직은 포함하지 않는다.**

```python
# FastAPI Router — User Interface Layer
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/orders")

@router.post("/", status_code=201)
async def place_order(
    request: PlaceOrderRequest,  # DTO
    use_case: PlaceOrderUseCase = Depends(get_place_order_use_case),
):
    command = PlaceOrderCommand(
        customer_id=request.customer_id,
        items=[
            OrderItemDTO(product_id=i.product_id, quantity=i.quantity)
            for i in request.items
        ],
    )
    order_id = use_case.execute(command)
    return {"order_id": str(order_id)}
```

---

#### 19. Application Layer

**정의**: Use Case를 **오케스트레이션**하는 계층. 비즈니스 로직을 포함하지 않고, **작업 진행 상태만 관리**하며, 도메인 객체에 작업을 **위임**한다.

**역할**: 트랜잭션 경계, Repository 호출, Domain Service 호출, 이벤트 발행.

**핵심 원칙**: "이 레이어는 얇아야 한다(thin layer)." 비즈니스 규칙이 여기에 있으면 **도메인 모델이 빈약(anemic)**하다는 신호.

> (코드 예시는 위의 Application Service 섹션 참조)

---

#### 20. Domain Layer

**정의**: 비즈니스 규칙과 로직의 **핵심**. DDD의 심장.

**역할**: Entity, Value Object, Aggregate, Domain Service, Domain Event, Specification, Repository 인터페이스가 모두 이 레이어에 위치한다.

**핵심 원칙**: **외부 의존성 없음.** 프레임워크, DB, HTTP 등 기술적 관심사에 대해 전혀 모른다. 순수한 도메인 로직만 포함한다.

---

#### 21. Infrastructure Layer

**정의**: **기술적 지원**을 제공하는 계층. DB 접근, 메시지 큐, 이메일, 파일 시스템, 외부 API 등.

**역할**: Domain Layer에서 정의한 인터페이스(Repository, EventPublisher 등)를 **구현**한다. Dependency Inversion Principle(DIP)에 의해 인프라가 도메인에 **의존**한다 (반대가 아님).

> (코드 예시는 위의 Repository, Infrastructure Service 섹션 참조)

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

```
┌─────────────────────────────────────────────────────────────────┐
│                    DDD 전체 동작 흐름                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  👤 사용자                                                       │
│    │                                                             │
│    ▼                                                             │
│  ┌──────────────────────┐                                       │
│  │ UI Layer (Controller)│  ← 요청 수신, DTO 변환                 │
│  └──────────┬───────────┘                                       │
│             │ Command                                            │
│             ▼                                                    │
│  ┌──────────────────────┐                                       │
│  │ Application Layer    │  ← Use Case 오케스트레이션              │
│  │ (Application Service)│                                       │
│  └──────┬───────┬───────┘                                       │
│         │       │                                                │
│    Repository  Domain Service                                    │
│         │       │                                                │
│         ▼       ▼                                                │
│  ┌──────────────────────┐                                       │
│  │ Domain Layer         │  ← 비즈니스 로직 실행                   │
│  │ (Aggregate, Entity,  │                                       │
│  │  VO, Domain Event)   │                                       │
│  └──────────┬───────────┘                                       │
│             │ Domain Event                                       │
│             ▼                                                    │
│  ┌──────────────────────┐                                       │
│  │ Infrastructure Layer │  ← DB 저장, 이벤트 발행, 이메일 등     │
│  │ (Repo 구현, MQ, SMTP)│                                       │
│  └──────────────────────┘                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (주문 접수 예시)

1. **Step 1**: 사용자가 HTTP POST /orders 요청 전송
2. **Step 2**: UI Layer(Controller)가 요청을 파싱하고 `PlaceOrderCommand` DTO로 변환
3. **Step 3**: Application Service(`PlaceOrderUseCase`)가 Command를 받아 처리 시작
4. **Step 4**: Repository를 통해 필요한 Aggregate(Product 등)를 로드
5. **Step 5**: Domain Service(PricingService)로 가격 계산
6. **Step 6**: Order Aggregate를 생성하고 도메인 로직 실행 (`order.place()`)
7. **Step 7**: Aggregate 내부에서 `OrderPlacedEvent` 도메인 이벤트 생성
8. **Step 8**: Repository를 통해 Order를 DB에 저장
9. **Step 9**: EventPublisher를 통해 도메인 이벤트를 발행
10. **Step 10**: 다른 Bounded Context(배송, 알림 등)가 이벤트를 수신하여 반응

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스

### 🎯 대표 유즈 케이스

| # | 유즈 케이스 | 설명 | 적합한 이유 |
|---|------------|------|------------|
| 1 | 복잡한 비즈니스 도메인 | 금융, 보험, 의료, 물류 | 비즈니스 규칙이 복잡하여 도메인 모델링이 필수 |
| 2 | 마이크로서비스 경계 설정 | 대규모 시스템 분해 | Bounded Context가 자연스러운 서비스 경계 |
| 3 | 레거시 시스템 현대화 | 단계적 마이그레이션 | ACL로 레거시를 격리하고 점진적 교체 |
| 4 | 도메인 전문가 협업 | 보험 상품 설계, 의료 워크플로우 | Ubiquitous Language로 소통 격차 해소 |
| 5 | 이벤트 드리븐 시스템 | 실시간 알림, 워크플로우 자동화 | Domain Event로 느슨한 결합 실현 |

### ✅ 베스트 프랙티스

1. **Aggregate를 작게 유지**: 하나의 Aggregate에 너무 많은 Entity를 넣지 말 것. 성능과 동시성 문제 발생
2. **Aggregate 간 참조는 ID로**: 직접 객체 참조 대신 ID로 참조하여 결합도 최소화
3. **Domain Layer에 프레임워크 의존성 금지**: 순수 Python 코드로 유지
4. **Ubiquitous Language를 코드에 반영**: 메서드명, 변수명이 도메인 용어와 일치해야 함
5. **Application Service를 얇게 유지**: 비즈니스 로직은 Domain Layer에

### 🏢 실제 적용 사례

- **Netflix**: 비디오 스트리밍(Core), 추천(Supporting), 결제(Generic) 서브도메인으로 분류하여 각각 독립적 Bounded Context로 운영 [🟡 Likely — 공식 문서 아닌 간접 사례]
- **Amazon**: 주문, 결제, 물류 등 거대한 비즈니스 도메인을 Bounded Context로 분해하여 마이크로서비스 아키텍처 구현 [🟡 Likely]
- **Zalando**: DDD를 공식적으로 채택하여 e-commerce 플랫폼의 도메인 모델링에 활용 [🟡 Likely]

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ 장점 | **비즈니스 정렬** | 코드가 비즈니스 현실을 직접 반영 |
| ✅ 장점 | **소통 개선** | Ubiquitous Language로 개발자-도메인 전문가 격차 해소 |
| ✅ 장점 | **유지보수성** | 잘 정의된 경계와 규칙으로 변경 영향 범위 제한 |
| ✅ 장점 | **테스트 용이성** | 도메인 로직이 순수하므로 단위 테스트 쉬움 |
| ✅ 장점 | **마이크로서비스 적합** | Bounded Context = 자연스러운 서비스 경계 |
| ❌ 단점 | **높은 학습 곡선** | Strategic + Tactical 패턴 모두 이해 필요 |
| ❌ 단점 | **과도한 복잡성** | 단순 CRUD에 적용하면 오히려 복잡도 증가 |
| ❌ 단점 | **도메인 전문가 필수** | 전문가 없이는 효과적 모델링 불가 |
| ❌ 단점 | **초기 비용** | 설계에 시간 투자 필요 |

### ⚖️ Trade-off 분석

```
비즈니스 정렬   ◄──── Trade-off ────►  초기 설계 비용
유지보수성      ◄──── Trade-off ────►  높은 학습 곡선
유연한 경계     ◄──── Trade-off ────►  도메인 전문가 의존
테스트 용이성   ◄──── Trade-off ────►  코드량 증가
```

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 DDD vs 다른 아키텍처 패턴

| 비교 기준 | DDD | Hexagonal | Clean Architecture | Layered |
|---|---|---|---|---|
| **유형** | 철학 + 방법론 | 구조 패턴 | 구조 패턴 | 구조 패턴 |
| **핵심 질문** | 무엇을 모델링? | 안/밖을 어떻게 분리? | 의존성 방향은? | 레이어를 어떻게 나눌까? |
| **초점** | 도메인 복잡성 관리 | 기술 결합 제거 | 의존성 규칙 | 관심사의 수평 분리 |
| **단독 사용** | ❌ (구조 패턴 필요) | ✅ | ✅ | ✅ |
| **학습 곡선** | 가파름 | 중간 | 중간 | 낮음 |
| **최적 조합** | DDD + Hexagonal 또는 DDD + Clean | — | — | — |

### 🤔 언제 무엇을 선택?

- **DDD를 선택하세요** → 비즈니스 로직이 복잡하고, 도메인 전문가와 협업 가능하며, 장기 유지보수가 중요한 경우
- **DDD를 건너뛰세요** → 단순 CRUD, 프로토타입, 도메인 전문가가 없는 경우

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|------|-----------|------------|
| 1 | **Anemic Domain Model** | Entity가 getter/setter만 있고 로직이 Service에 몰림 | 비즈니스 로직을 Entity/VO 내부에 배치 |
| 2 | **Aggregate를 너무 크게** | 동시성 문제, 성능 저하, 트랜잭션 충돌 | Aggregate를 작게 유지, ID로 참조 |
| 3 | **모든 곳에 DDD 적용** | Generic Subdomain에 DDD는 과잉 설계 | Core Subdomain에만 DDD 집중 |
| 4 | **Ubiquitous Language 무시** | 코드와 비즈니스 용어 괴리 | 코드 = 도메인 용어 |
| 5 | **기술 중심 설계** | DB 스키마 먼저 설계하고 도메인 모델 맞춤 | 도메인 모델 먼저, DB는 나중에 매핑 |

### 🚫 Anti-Patterns

1. **Smart UI**: UI에 비즈니스 로직을 직접 넣는 것. DDD의 정반대.
2. **God Aggregate**: 하나의 Aggregate에 모든 것을 넣는 것. 분해해야 한다.
3. **Leaking Domain Logic**: Application Service에 if-else 비즈니스 규칙이 산재하는 것.
4. **Shared Database**: Bounded Context 간 DB를 직접 공유하는 것. 각 Context는 자체 저장소를 가져야 한다.

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|------|------|----------|
| 📖 원전 | Domain-Driven Design (Blue Book) | Eric Evans (2003) — DDD의 바이블 |
| 📘 실무서 | Implementing DDD (Red Book) | Vaughn Vernon (2013) — 실무 구현 가이드 |
| 📘 입문서 | Learning Domain-Driven Design | Vlad Khononov (2021) — 현대적 입문서 |
| 📖 레퍼런스 | DDD Reference | [domainlanguage.com](https://www.domainlanguage.com/ddd/reference/) |
| 📺 영상 | Eric Evans - DDD: Putting the Model to Work | DDD Europe 컨퍼런스 강연 |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리 | 언어/플랫폼 | 용도 |
|---|---|---|
| [ddd-for-python](https://pypi.org/project/ddd-for-python/) | Python | DDD 빌딩 블록 기본 클래스 |
| [python-ddd](https://github.com/pgorecki/python-ddd) | Python | DDD 예제 프로젝트 |
| [Context Mapper](https://contextmapper.org/) | Java/DSL | DDD 전략적 설계 모델링 도구 |
| [EventStorming](https://www.eventstorming.com/) | 방법론 | 도메인 이벤트 기반 워크샵 |

### 🔮 트렌드 & 전망

- **마이크로서비스 + DDD**: Bounded Context가 마이크로서비스 경계 설정의 표준 방법으로 자리잡음
- **Event Sourcing + DDD**: Domain Event를 저장소로 사용하는 패턴이 증가
- **CQRS + DDD**: 읽기/쓰기 모델 분리로 성능과 복잡성 균형

### 💬 커뮤니티 인사이트

- "DDD의 가장 큰 가치는 Tactical 패턴이 아니라 Strategic Design에 있다. Bounded Context와 Ubiquitous Language를 잘 잡으면 나머지는 자연스럽게 따라온다." — 실무자 공통 의견 [🟡 Likely]
- "모든 프로젝트에 DDD를 적용하려 하지 마라. Core Subdomain에만 집중하라." — DDD 커뮤니티 반복 권고

---

## 📎 Sources

1. [Domain-Driven Design — Eric Evans (원전, 2003)](https://www.amazon.com/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215) — 1차 자료
2. [DDD Reference — Eric Evans](https://www.domainlanguage.com/ddd/reference/) — 1차 자료
3. [Martin Fowler — DDD bliki](https://martinfowler.com/bliki/DomainDrivenDesign.html) — 1차 자료
4. [Microsoft — Tactical DDD for Microservices](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/tactical-ddd) — 공식 문서
5. [Vaadin — Tactical DDD Building Blocks](https://vaadin.com/blog/ddd-part-2-tactical-domain-driven-design) — 기술 블로그
6. [Enterprise Craftsmanship — Domain vs Application Services](https://enterprisecraftsmanship.com/posts/domain-vs-application-services/) — 기술 블로그
7. [Context Mapper — Context Map Patterns](https://contextmapper.org/docs/context-map/) — 도구 문서
8. [ddd-crew — Context Mapping](https://github.com/ddd-crew/context-mapping) — 커뮤니티
9. [Specification Pattern in Python — Medium](https://douwevandermeij.medium.com/specification-pattern-in-python-ff2bd0b603f6) — 기술 블로그

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 6 (Task 1 deep-research 9건 + 추가 3건 = 총 12건 중 DDD 관련 6건)
> - 수집 출처 수: 9
> - 출처 유형: 1차 자료 3, 공식 문서 1, 기술 블로그 3, 도구 문서 1, 커뮤니티 1
> - 모든 구성요소(21개) 빠짐없이 포함 확인: ✅
