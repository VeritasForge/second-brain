---
tags: [solid, design-principles, oop, clean-architecture, dip, ioc, di]
created: 2026-04-14
---

# SOLID 원칙 완전 정복 — 정의, 예제, 관계, 실무 적용

---

## 1. SOLID란?

SOLID는 **변경에 유연한 소프트웨어를 만드는 5가지 설계 원칙**이다. Robert C. Martin이 정리했으며, 클래스 수준부터 MSA (Micro Service Architecture) 수준까지 스케일이 확장된다.

| 약자  | 원칙                                                                 | 한 줄 요약                          | 위반 신호                                       |
| ----- | -------------------------------------------------------------------- | ----------------------------------- | ----------------------------------------------- |
| **S** | SRP (Single Responsibility Principle, 단일 책임 원칙)                | 한 클래스 = 한 책임                 | "이 클래스가 왜 이것도 하지?"                   |
| **O** | OCP (Open/Closed Principle, 개방/폐쇄 원칙)                         | 확장 OK, 수정 NO                    | `when/if`에 새 분기 계속 추가                   |
| **L** | LSP (Liskov Substitution Principle, 리스코프 치환 원칙)              | 자식은 부모 자리를 대체 가능        | "이 자식 클래스 넣으면 터지네?"                 |
| **I** | ISP (Interface Segregation Principle, 인터페이스 분리 원칙)          | 인터페이스는 작게 쪼개기            | `UnsupportedOperationException` 던짐            |
| **D** | DIP (Dependency Inversion Principle, 의존성 역전 원칙)               | 추상화에 의존                       | `import com.mysql.jdbc.*` 직접 참조             |

---

## 2. 각 원칙 상세 — 예제와 함께

### S — SRP (Single Responsibility Principle, 단일 책임 원칙)

> "한 클래스는 변경할 이유가 하나뿐이어야 한다"

비유: 요리사는 요리만, 서빙은 서버가 🍳🚶

```kotlin
// ❌ BAD: 한 클래스가 두 가지 이유로 변경됨
class UserService {
    fun createUser(user: User) { /* 유저 생성 로직 */ }
    fun sendWelcomeEmail(user: User) { /* 이메일 발송 */ }
    //  ^ 유저 로직 바뀌면 수정  ^ 이메일 로직 바뀌면 수정
}

// ✅ GOOD: 책임 분리
class UserService {
    fun createUser(user: User) { /* 유저 생성만 */ }
}
class EmailService {
    fun sendWelcomeEmail(user: User) { /* 이메일만 */ }
}
```

### O — OCP (Open/Closed Principle, 개방/폐쇄 원칙)

> "확장에는 열려있고, 수정에는 닫혀있어야 한다"

비유: USB 포트처럼 — 새 장치를 꽂을 수 있지만(확장) 포트 자체를 바꿀 필요는 없음(폐쇄) 🔌

```kotlin
// ❌ BAD: 새 할인 추가할 때마다 기존 코드 수정
fun calculateDiscount(type: String, price: Double): Double = when(type) {
    "christmas" -> price * 0.8
    "vip" -> price * 0.7
    "newYear" -> price * 0.85  // 새로 추가할 때마다 여기를 수정해야 함!
    else -> price
}

// ✅ GOOD: 새 할인은 새 클래스를 추가하면 됨
interface DiscountStrategy {
    fun calculate(price: Double): Double
}
class ChristmasDiscount : DiscountStrategy {
    override fun calculate(price: Double) = price * 0.8
}
class VIPDiscount : DiscountStrategy {
    override fun calculate(price: Double) = price * 0.7
}
// 새 할인? → 새 클래스만 추가! 기존 코드 수정 없음
```

### L — LSP (Liskov Substitution Principle, 리스코프 치환 원칙)

> "자식 타입은 부모 타입을 대체해도 프로그램이 정상 동작해야 한다"

비유: 대리운전 기사가 바뀌어도 목적지에는 도착해야 함 🚗

```kotlin
// ❌ BAD: Square가 Rectangle의 계약을 위반
open class Rectangle {
    open var width: Int = 0
    open var height: Int = 0
    fun area() = width * height
}

class Square : Rectangle() {
    override var width: Int = 0
        set(value) { field = value; height = value }  // 💥 width 바꾸면 height도 바뀜
    override var height: Int = 0
        set(value) { field = value; width = value }
}

// 사용하는 쪽:
fun resize(rect: Rectangle) {
    rect.width = 5
    rect.height = 10
    assert(rect.area() == 50)  // Rectangle이면 OK, Square이면 💥 area=100!
}

// ✅ GOOD: 별도 인터페이스로 분리
interface Shape { fun area(): Int }
class Rectangle(val width: Int, val height: Int) : Shape {
    override fun area() = width * height
}
class Square(val side: Int) : Shape {
    override fun area() = side * side
}
```

#### LSP의 진짜 핵심: "계약을 지켜라"

LSP는 단순히 "인터페이스 구현하면 된다"가 아니다. **계약(Contract)**을 지키는 것이다 (Liskov/Wing 1994):

| 계약 요소                    | 규칙                                              | 위반 예시                                                   |
| ---------------------------- | ------------------------------------------------- | ----------------------------------------------------------- |
| **사전조건** (Precondition)  | 자식은 더 약하게만 (더 많이 받아들여야 함)         | 부모는 모든 금액 OK인데 자식은 10만원 한도                   |
| **사후조건** (Postcondition) | 자식은 더 강하게만 (더 많이 보장해야 함)           | 부모는 항상 영수증 반환인데 자식은 가끔 null 반환            |
| **불변식** (Invariant)       | 자식은 절대 깰 수 없음                            | Rectangle의 width/height 독립 불변식을 Square가 깸          |

```kotlin
// LSP 위반 예시: 계약 위반
interface PaymentProcessor {
    fun pay(amount: Int): Receipt  // 계약: 결제하고 영수증 반환
}

class CreditCardPayment : PaymentProcessor {
    override fun pay(amount: Int): Receipt {
        return Receipt(amount, "approved")  // ✅ 계약 준수
    }
}

class BitcoinPayment : PaymentProcessor {
    override fun pay(amount: Int): Receipt {
        if (amount > 100000) throw RuntimeException("한도 초과!")  // 💥 LSP 위반!
        // 부모 인터페이스의 "계약"에는 한도 제한이 없었는데
        // 이 구현체만 갑자기 예외를 던짐
        return Receipt(amount, "approved")
    }
}
```

### I — ISP (Interface Segregation Principle, 인터페이스 분리 원칙)

> "사용하지 않는 메소드에 의존하지 말라"

비유: 리모컨에 100개 버튼 중 5개만 쓴다면, 5개짜리 리모컨이 나은 것 🎮

```kotlin
// ❌ BAD: 거대한 인터페이스
interface Worker {
    fun work()
    fun eat()
    fun sleep()
}
class Robot : Worker {
    override fun work() { /* OK */ }
    override fun eat() { /* 로봇이 밥을?? 💥 */ }
    override fun sleep() { /* 로봇이 잠을?? 💥 */ }
}

// ✅ GOOD: 필요한 것만 구현
interface Workable { fun work() }
interface Feedable { fun eat() }
interface Sleepable { fun sleep() }

class Human : Workable, Feedable, Sleepable { /*...*/ }
class Robot : Workable { override fun work() { /*...*/ } }  // 필요한 것만!
```

### D — DIP (Dependency Inversion Principle, 의존성 역전 원칙)

> "고수준 모듈이 저수준 모듈에 의존하면 안 된다. 둘 다 추상화에 의존해야 한다"

비유: 콘센트(인터페이스)에 의존 — 어떤 전자제품이든 꽂을 수 있음 🔌

```kotlin
// ❌ BAD: 고수준(OrderService)이 저수준(MySQLRepository)에 직접 의존
class OrderService {
    private val repo = MySQLOrderRepository()  // MySQL에 묶임!
}

// ✅ GOOD: 둘 다 추상화(인터페이스)에 의존
interface OrderRepository {
    fun save(order: Order)
}
class MySQLOrderRepository : OrderRepository { /*...*/ }
class PostgresOrderRepository : OrderRepository { /*...*/ }

class OrderService(
    private val repo: OrderRepository  // 추상화에 의존! (어떤 DB든 OK)
)
```

```
의존 방향 비교:

❌ BAD:  OrderService ──→ MySQLRepository
                          (고수준이 저수준에 직접 의존)

✅ GOOD: OrderService ──→ OrderRepository ←── MySQLRepository
                          (둘 다 추상화에 의존 = 역전!)
```

---

## 3. OCP vs LSP — 뭐가 다른가?

OCP와 LSP는 둘 다 "추상화에 의존하라"는 큰 그림을 공유하지만, **바라보는 관점이 완전히 다르다**.

```
OCP (Open/Closed Principle)         LSP (Liskov Substitution Principle)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📐 설계자의 시점                    🔍 사용자(호출자)의 시점
"새 기능을 추가할 때               "구현체를 바꿨을 때
 기존 코드를 수정하지 않게           기존에 되던 게 깨지지 않게
 설계하자"                          보장하자"

질문: "확장할 때 안전한가?"         질문: "교체할 때 안전한가?"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

| 관점       | OCP (개방/폐쇄)                             | LSP (리스코프 치환)                                        |
| ---------- | ------------------------------------------- | ---------------------------------------------------------- |
| **질문**   | "새 기능 추가 시 기존 코드 수정해야 하나?"  | "구현체 교체 시 기존 동작이 깨지나?"                       |
| **위반 시** | 기존 코드에 `if/when` 분기 추가             | 구현체가 부모의 계약(contract)을 어김                      |
| **해결법** | 인터페이스 + 새 클래스 추가                 | 하위 타입이 상위 타입의 사전조건·사후조건·불변식 준수      |
| **비유**   | 멀티탭에 새 플러그 꽂기 🔌                  | 어떤 브랜드든 규격만 맞으면 동작 ⚡                        |
| **초점**   | **확장성** (Extension)                      | **호환성** (Substitutability)                              |

---

## 4. SOLID 원칙은 서로 연결된다

SOLID는 5개의 독립된 규칙이 아니라, **서로 맞물리는 톱니바퀴** ⚙️다.

```
     SRP ──────────────── ISP
  "한 클래스 =              "인터페이스를
   한 책임"                  작게 쪼개라"
      │                        │
      │ 책임을 분리하면 →        │ 인터페이스가 작으면 →
      │ 인터페이스도 작아짐       │ 구현체 교체가 쉬워짐
      │                        │
      ▼                        ▼
     OCP ─────────────── DIP
  "확장에 열리고              "추상화에
   수정에 닫혀라"              의존하라"
      │                        │
      │ 구현체를 추가할 때 →     │ 추상화에 의존하면 →
      │ 기존 코드가 안 바뀌려면   │ 교체해도 안 깨져야 함
      │ 교체해도 안 깨져야 함     │
      │                        │
      └──────────┬─────────────┘
                 ▼
                LSP
           "교체해도
            동작이 깨지면 안 됨"
```

### 연결 흐름을 코드 하나로

```kotlin
// 1️⃣ SRP: OrderService는 주문만 담당 (결제는 분리)
class OrderService(
    // 5️⃣ DIP: 추상화에 의존
    private val payment: PaymentProcessor,
    private val notification: NotificationSender
)

// 3️⃣ ISP: 결제만 하는 작은 인터페이스
interface PaymentProcessor {
    fun pay(amount: Int): Receipt
}

// 2️⃣ OCP: 새 결제 수단 = 새 클래스 추가
class CreditCardPayment : PaymentProcessor { /* ... */ }
class KakaoPayment : PaymentProcessor { /* ... */ }  // 🆕 추가만!

// 4️⃣ LSP: 어떤 구현체든 pay()의 계약을 지킴
//    → OrderService는 어떤 PaymentProcessor가 오든 안전
```

---

## 5. SOLID의 MSA 스케일 확장

SOLID는 클래스 수준부터 서비스 수준까지 동일하게 적용된다:

| SOLID   | 클래스 수준                | MSA 수준                                                  |
| ------- | -------------------------- | --------------------------------------------------------- |
| **SRP** | 한 클래스 = 한 책임        | 한 서비스 = 한 도메인 (주문 서비스, 결제 서비스)          |
| **OCP** | 새 클래스 추가로 확장      | 새 서비스 추가로 확장 (새 결제 방식 = 새 서비스)          |
| **LSP** | 구현체 교체해도 OK         | 서비스 교체해도 API 계약이 동일                           |
| **ISP** | 인터페이스 작게 쪼개기     | API를 기능별로 분리 (결제 API / 환불 API)                 |
| **DIP** | 인터페이스에 의존          | 서비스 간 직접 호출 대신 이벤트/메시지 큐 사용            |

---

## 6. SOLID와 IoC/DI의 관계

### DIP, IoC, DI — 세 개념의 관계 피라미드

```
    WHY (왜?)
    ┌─────┐
    │ DIP │  SOLID의 D — "추상화에 의존하라" (설계 원칙)
    └──┬──┘
       │ 이걸 실현하려면?
    ┌──▼──┐
    │ IoC │  "제어를 역전시키자" (아키텍처 패턴)
    └──┬──┘
       │ 구체적으로 어떻게?
    ┌──▼──┐
    │ DI  │  "의존성을 외부에서 주입하자" (구현 기법)
    └─────┘
    HOW (어떻게?)
```

| 개념                                                  | 수준            | 비유                                           | 핵심 질문                |
| ----------------------------------------------------- | --------------- | ---------------------------------------------- | ------------------------ |
| **DIP** (Dependency Inversion Principle)               | 설계 원칙       | "재료는 마트 브랜드 말고 일반 규격으로 사라"   | **왜** 역전해야 하나?    |
| **IoC** (Inversion of Control)                         | 아키텍처 패턴   | "재료는 네가 사지 말고 배달시켜"               | **무엇**을 역전하나?     |
| **DI** (Dependency Injection)                          | 구현 기법       | "배달앱으로 주문하자"                          | **어떻게** 역전하나?     |

📌 IoC는 DIP보다 넓은 독립적 개념이다. DIP는 의존성 **방향**에 대한 원칙이고, IoC는 제어 **흐름**에 대한 더 넓은 원칙이며, DI는 이 둘을 동시에 만족시키는 가장 대표적인 구현 패턴이다.

### IoC의 다양한 구현 방식

DI는 IoC를 구현하는 가장 인기 있는 방법이지만, 유일한 것은 아니다:

| IoC 구현 방식           | 설명                                   | 예시                                             |
| ----------------------- | -------------------------------------- | ------------------------------------------------ |
| **DI** (Dependency Injection) | 외부에서 의존성을 넣어줌         | Spring, Dagger, Koin                             |
| **Service Locator**     | 중앙 레지스트리에서 꺼내감             | `ServiceLocator.get(PaymentService::class)`      |
| **Template Method**     | 부모 클래스가 흐름 제어, 자식이 구현   | `AbstractController.handleRequest()`             |
| **Event/Observer**      | 프레임워크가 이벤트 발생 시 호출       | `@EventListener`, Callback                       |

Martin Fowler가 정리한 IoC의 본질: **"Don't call us, we'll call you"** (Hollywood Principle)

---

## 7. 현업에서의 SOLID

> SOLID는 "법칙"이 아니라 "나침반"이다.

- 모든 코드에 100% 적용하면 → 과도한 추상화(Over-engineering)
- 3줄짜리 유틸리티에 인터페이스 + 팩토리 + 전략 패턴? → 배보다 배꼽
- **"이 설계가 나중에 문제될까?"** 판단할 때 SOLID를 기준으로 쓰는 것이 핵심

💡 **실무 원칙**:

> SOLID는 개별 원칙을 기계적으로 적용하는 게 아니라, 설계 의사결정의 기준으로 삼는다. 특히 변경 가능성이 높은 부분에서 SOLID를 엄격히 적용하고, 안정적인 부분에서는 pragmatic하게 접근한다.

---

## 핵심 정리

1. **SRP** = 한 클래스는 변경 이유가 하나. 위반 시 → 클래스 분리
2. **OCP** = 확장에 열리고 수정에 닫힘. 위반 시 → 인터페이스 + 새 클래스 추가
3. **LSP** = 자식 교체 시 동작이 깨지면 안 됨. 핵심은 계약(사전조건/사후조건/불변식) 준수
4. **ISP** = 인터페이스는 작게 쪼개기. 위반 시 → UnsupportedOperationException 발생
5. **DIP** = 추상화에 의존. IoC/DI의 이론적 기반
6. **OCP vs LSP**: OCP는 설계자 시점(확장성), LSP는 호출자 시점(호환성)
7. **5원칙은 서로 맞물리며**, 클래스~MSA까지 동일하게 적용 가능
8. **DIP(왜) → IoC(무엇) → DI(어떻게)**: 설계 원칙에서 구현 기법으로의 흐름
9. SOLID는 **나침반이지 법칙이 아님** — 변경 가능성이 높은 곳에 집중 적용
