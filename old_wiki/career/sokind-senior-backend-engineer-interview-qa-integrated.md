# 🎯 Senior Backend Engineer 면접 Q&A 통합본

> 📅 생성일: 2026-03-22
> 🏢 대상: 크디랩(쏘카인드) Senior Backend Engineer
> 📋 구성: Q1~Q14 심화 답변 (60+ 세부 질문 포함) + Q15~Q100 기본 답변
> 🔬 조사 기반: Deep Research + Concept Explainer + JD 분석
> 📖 사용자 배경: Python/FastAPI/SQLAlchemy 경험, Spring Boot 면접 준비

---

## 📑 목차

### Part 1: 심화 답변 (Q1~Q14)
- Q1. HATEOAS 수준 결정
- Q2. 헥사고날 아키텍처 도메인 내부 구조
- Q3. Spring Boot 전역 예외 처리 (6개 세부 질문)
- Q4. API 버전 관리 전략 (7개 세부 질문)
- Q5. DTO와 Entity 분리 (기본 답변)
- Q6. MySQL vs PostgreSQL 심화 (MVCC, JSON, 풀텍스트, 확장성, 쓰기/읽기 성능)
- Q7. 데이터베이스 인덱스 전략 (Clustered Index, 카디널리티, 커버링 인덱스)
- Q8. N+1 쿼리 문제 (SQLAlchemy 비교, Fetch Join 페이징, EntityGraph, SUBSELECT)
- Q9. JPA Lazy/Eager Loading (OneToMany, ManyToMany, OneToOne 예시)
- Q10. EXPLAIN ANALYZE (MySQL vs PostgreSQL 분리)
- Q11. 대용량 페이징 (Offset vs Cursor 내부 동작 원리)
- Q12. 트랜잭션 관리 (Service 계층 이유, Dirty Checking, Checked Exception)
- Q13. Connection Pool (HikariCP, DB 서버 관점의 pool size)
- Q14. 동시성 문제 (DB 락 vs 분산 락 구분, Redis Lock, Idempotency Key)

### Part 2: 기본 답변 (Q15~Q100)
- 🔴 Tier 1: Q15~Q30 (백엔드 아키텍처)
- 🟠 Tier 2: Q31~Q55 (팀 리딩, 개발 문화)
- 🟡 Tier 3: Q56~Q80 (Kotlin, JPA, 테스트, WebRTC)
- 🟢 Tier 4: Q81~Q100 (LLM, 스타트업, FE 협업)

---

## 중요도 범례

| Tier | 범위 | JD 매핑 |
|------|------|---------|
| 🔴 Tier 1 | #1~30 | Spring Boot REST API 설계, DB 스키마/쿼리 최적화, 백엔드 아키텍처 |
| 🟠 Tier 2 | #31~55 | 팀 리딩, 개발 문화/프로세스, 기술 로드맵, 기술 부채 관리 |
| 🟡 Tier 3 | #56~80 | Kotlin, JPA/ORM, 테스트, 멀티모듈, WebRTC/WebSocket, Redis |
| 🟢 Tier 4 | #81~100 | LLM 상용화, Spring AI, 스타트업 경험, FE 협업, Agile |

---

# Part 1: 심화 답변 (Q1~Q14)

> 📖 이 섹션은 기본 답변에 대한 60+ 세부 질문의 심화 답변입니다.
> 비유, 단계별 설명, 비교 테이블, 코드 예시를 포함합니다.

---



# 면접 준비 질문 답변

---

## Q1. HATEOAS 수준 결정

### 현실 세계 비유 🎮

HATEOAS를 **놀이공원 안내 시스템**이라고 생각해보자.

- **Level 0**: 놀이공원에 들어갔는데 안내판이 하나도 없어. "회전목마 어딨어요?" 하면 직원이 "저기요" 하고 끝.
- **Level 1**: 안내판에 "회전목마", "롤러코스터" 같은 **이름표**는 있어. 근데 어디로 가야 하는지는 안 알려줘.
- **Level 2**: 안내판에 이름표 + "왼쪽으로 가세요", "줄 서세요" 같은 **행동 지침**이 있어.
- **Level 3 (HATEOAS)**: 안내판이 **"지금 당신 상태"에 따라 달라져**. 이미 롤러코스터를 탔으면 "다음은 회전목마 어때요?" 하고, 아직 표를 안 샀으면 "먼저 매표소로 가세요" 라고 알려줘.

### 단계별 설명: Richardson Maturity Model

이건 Leonard Richardson이 만든 **REST API 성숙도 모델**이야. 4단계로 나뉘어.

| 레벨 | 이름 | 설명 | 예시 |
|------|------|------|------|
| **Level 0** | The Swamp of POX | 하나의 URI, 하나의 HTTP 메서드 | `POST /api` 에 모든 요청 |
| **Level 1** | Resources | 리소스별 URI 분리 | `POST /users`, `POST /orders` |
| **Level 2** | HTTP Verbs | HTTP 메서드 활용 | `GET /users`, `POST /users`, `DELETE /users/1` |
| **Level 3** | HATEOAS | 응답에 **다음 가능한 행동 링크** 포함 | 아래 예시 참조 |

### HATEOAS 구체적 수준 결정

💡 핵심 질문: **"우리 API에 HATEOAS를 얼마나 적용할 것인가?"**

실무에서는 Full HATEOAS (Level 3)을 완전히 구현하는 경우가 드물어. 그래서 **수준을 결정**해야 해.

#### 수준 1: 최소 HATEOAS — self 링크만

```json
{
  "id": 1,
  "name": "김철수",
  "_links": {
    "self": { "href": "/users/1" }
  }
}
```

📌 **언제?**: 클라이언트가 이미 API 스펙을 잘 알고 있을 때. 내부 서비스 간 통신.

#### 수준 2: 관계 링크 포함

```json
{
  "id": 1,
  "name": "김철수",
  "_links": {
    "self": { "href": "/users/1" },
    "orders": { "href": "/users/1/orders" },
    "update": { "href": "/users/1", "method": "PUT" }
  }
}
```

📌 **언제?**: 외부 개발자가 쓰는 Public API. 탐색(discovery)이 중요할 때.

#### 수준 3: 상태 기반 동적 링크 (Full HATEOAS)

```json
// 주문 상태가 "PAID"일 때
{
  "id": 100,
  "status": "PAID",
  "_links": {
    "self": { "href": "/orders/100" },
    "ship": { "href": "/orders/100/ship", "method": "POST" },
    "cancel": { "href": "/orders/100/cancel", "method": "POST" }
  }
}

// 주문 상태가 "SHIPPED"일 때 — cancel 링크가 사라짐!
{
  "id": 100,
  "status": "SHIPPED",
  "_links": {
    "self": { "href": "/orders/100" },
    "track": { "href": "/orders/100/tracking" }
  }
}
```

📌 **언제?**: 상태 머신(state machine)이 복잡하고, 클라이언트가 "지금 뭘 할 수 있는지"를 동적으로 알아야 할 때.

### 실무 판단 기준 테이블

| 기준 | 최소 (self만) | 관계 링크 | Full HATEOAS |
|------|:---:|:---:|:---:|
| 내부 마이크로서비스 | ✅ 적합 | ⚠️ 과잉 | ❌ 과잉 |
| 외부 Public API | ⚠️ 부족 | ✅ 적합 | ✅ 이상적 |
| 상태 머신 복잡도 높음 | ❌ 부족 | ⚠️ 부족 | ✅ 적합 |
| 구현/유지보수 비용 | 낮음 | 중간 | 높음 |
| 클라이언트 편의성 | 낮음 | 중간 | 높음 |

### 💡 면접 팁

> "HATEOAS는 REST의 이상적인 최종 형태이지만, 실무에서는 **비용 대비 효과**를 따져서 수준을 결정합니다. 대부분의 내부 API는 Level 2 + self 링크 정도면 충분하고, Public API나 복잡한 워크플로우가 있을 때만 Full HATEOAS를 고려합니다."

---

## Q2. 헥사고날 아키텍처 — 도메인 내부는 자유다

### 현실 세계 비유 🏠

헥사고날 아키텍처를 **집**이라고 생각해보자.

- **Port & Adapter** = 집의 **문과 창문**. 외부(택배기사, 우체부, 손님)와 내부(거실)를 연결하는 통로.
- **Domain** = 집 **내부 인테리어**. 거실을 어떻게 꾸밀지는 집주인 마음이야!

문과 창문의 규격(Port & Adapter)만 지키면, 집 안에서 **원룸 스타일(Layered)**로 살든, **방마다 용도를 나눈 스타일(Clean Architecture)**로 살든 자유야.

### 단계별 설명

#### Step 1: 헥사고날이 정의하는 것과 정의하지 않는 것

| 헥사고날이 **정의하는 것** | 헥사고날이 **정의하지 않는 것** |
|---|---|
| Inbound Port (외부 → 도메인) | 도메인 내부 계층 구조 |
| Outbound Port (도메인 → 외부) | Entity 설계 방법 |
| Adapter 구현 방법 | Use Case 구조 |
| 의존성 방향 (바깥 → 안쪽) | 도메인 서비스 패턴 |

📌 즉, **너의 이해가 맞아!** 도메인 내부는 Clean Architecture를 쓸 수도, Layered를 쓸 수도, DDD를 쓸 수도 있어.

#### Step 2: 쏘카인드(AI 모델 제공자) 예시

쏘카인드 같은 회사가 **AI 모델 추론 API**를 제공한다고 가정해보자.

```
[클라이언트] → [REST API] → [헥사고날 경계] → [도메인] → [모델 서빙 인프라]
```

**Port & Adapter (헥사고날이 정의하는 부분):**

```
Inbound Adapter: REST Controller, gRPC Server
    ↓
Inbound Port: InferenceUseCase (interface)
    ↓
  ┌─────────── 도메인 내부 (자유 영역) ───────────┐
  │                                                │
  │   여기를 어떻게 구성할지가 질문의 핵심!          │
  │                                                │
  └────────────────────────────────────────────────┘
    ↓
Outbound Port: ModelRepositoryPort, GPUClusterPort (interface)
    ↓
Outbound Adapter: S3ModelRepository, KubernetesGPUAdapter
```

#### Step 3: 도메인 내부를 다르게 구성하는 3가지 방식

**방식 A: Layered 스타일 (단순)**

```
InferenceUseCase (Port)
    → InferenceService (비즈니스 로직)
        → InferenceRequest (DTO)
        → Model (Entity)
```

모든 로직이 Service 한 층에 몰려있어. 간단한 서비스에 적합.

```java
// Layered: Service에 모든 로직
@Service
public class InferenceService implements InferenceUseCase {
    public InferenceResult infer(InferenceRequest req) {
        Model model = modelRepo.findById(req.getModelId());
        // 검증, 전처리, 추론, 후처리 모두 여기에
        validateQuota(req.getUserId());
        preprocessed = preprocess(req.getInput());
        raw = gpuCluster.run(model, preprocessed);
        return postprocess(raw);
    }
}
```

**방식 B: Clean Architecture 스타일 (계층 분리)**

```
InferenceUseCase (Port)
    → InferenceInteractor (Use Case 계층 - 오케스트레이션)
        → Model (Entity 계층 - 핵심 도메인 규칙)
        → QuotaPolicy (Entity 계층 - 도메인 규칙)
```

Use Case 계층과 Entity 계층이 명확히 분리돼.

```java
// Clean Architecture: Use Case는 오케스트레이션만
public class InferenceInteractor implements InferenceUseCase {
    public InferenceResult infer(InferenceRequest req) {
        Model model = modelRepo.findById(req.getModelId());
        
        // Entity가 자체 규칙을 가짐
        model.validateCompatibility(req.getInput());
        quotaPolicy.checkAndConsume(req.getUserId());
        
        return model.runInference(req.getInput(), gpuCluster);
    }
}

// Entity에 도메인 규칙이 살아있음
public class Model {
    public void validateCompatibility(Input input) {
        if (!this.supportedFormats.contains(input.getFormat())) {
            throw new IncompatibleInputException();
        }
    }
}
```

**방식 C: DDD 스타일 (도메인 중심)**

```
InferenceUseCase (Port)
    → InferenceApplicationService (Application Layer)
        → ModelAggregate (Domain Layer - Aggregate Root)
            → InferenceSession (Value Object)
            → QuotaPolicy (Domain Service)
```

Aggregate, Value Object, Domain Service 같은 DDD 전술 패턴 활용.

#### Step 4: 어떤 걸 선택해야 할까?

| 기준 | Layered | Clean Architecture | DDD |
|------|:---:|:---:|:---:|
| 도메인 규칙 복잡도 낮음 | ✅ 적합 | ⚠️ 과잉 | ❌ 과잉 |
| 도메인 규칙 복잡도 높음 | ❌ 스파게티 | ✅ 적합 | ✅ 적합 |
| 팀 규모 작음 (1~3명) | ✅ 적합 | ⚠️ 가능 | ❌ 과잉 |
| 팀 규모 큼 (5명+) | ❌ 충돌 잦음 | ✅ 적합 | ✅ 적합 |
| 테스트 용이성 | 보통 | 높음 | 높음 |

### 💡 핵심 정리

> 헥사고날 아키텍처는 **"외부와의 경계를 어떻게 만들 것인가"**에 대한 답이고, 도메인 내부 구조는 별개의 결정이야. 마치 USB 포트(규격)가 정해져 있어도, 컴퓨터 내부 회로 설계는 제조사 마음인 것처럼. **Port & Adapter는 껍데기의 규칙이고, 도메인 내부는 비즈니스 복잡도에 맞게 선택**하면 돼.

---

## Q3. Spring Boot 전역 예외 처리

### Q3-1: 전역 예외 = FastAPI의 ExceptionHandler?

✅ **맞아, 거의 같은 개념이야!**

#### 현실 세계 비유

학교에서 **문제가 생겼을 때**를 생각해봐:
- **교실 안에서 선생님이 해결** = 비즈니스 로직 내 try-catch
- **교무실에서 처리** = 전역 예외 처리 (어떤 교실에서든 올라온 문제를 일관되게 처리)

#### 비교 테이블

| 개념 | FastAPI | Spring Boot |
|------|---------|-------------|
| 전역 예외 핸들러 등록 | `@app.exception_handler(SomeException)` | `@RestControllerAdvice` + `@ExceptionHandler` |
| 특정 예외 처리 | `async def handler(req, exc)` | `public ResponseEntity handle(SomeException e)` |
| HTTP 예외 | `HTTPException` | `ResponseStatusException` |
| Validation 예외 | `RequestValidationError` | `MethodArgumentNotValidException` |
| 동작 원리 | ASGI Middleware 체인 | DispatcherServlet의 HandlerExceptionResolver 체인 |

📌 **원리도 동일해.** 둘 다 프레임워크가 요청 처리 중 발생한 예외를 가로채서, 등록된 핸들러에게 위임하는 구조야. FastAPI에서 `exception_handler` 데코레이터로 등록하는 것과, Spring에서 `@RestControllerAdvice`로 등록하는 것은 **같은 패턴의 다른 문법**이야.

"전역 예외"라는 표현이 좀 오해를 줄 수 있는데:
- ❌ "비즈니스 로직이 아닌 예외만" 이라는 뜻이 아니야
- ✅ **"어떤 컨트롤러에서든 발생하는 예외를 한 곳에서 처리"** 라는 뜻이야

비즈니스 예외(`InsufficientBalanceException` 같은)도 전역 핸들러에서 처리하는 게 일반적이야.

---

### Q3-2: @ControllerAdvice vs @RestControllerAdvice

#### 현실 세계 비유

- `@ControllerAdvice` = 학교 **교무실** (문제를 받아서 처리하고, 처리 결과를 **편지**(View)로 줄 수도 있고 **말**(JSON)로 할 수도 있어)
- `@RestControllerAdvice` = 학교 교무실인데 **항상 말(JSON)로만 대답**하는 규칙

#### 단계별 설명

**Step 1: @ControllerAdvice**

```java
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(NotFoundException.class)
    public String handleNotFound(Model model) {
        model.addAttribute("message", "페이지를 찾을 수 없습니다");
        return "error/404";  // → View(HTML)를 반환
    }
    
    @ExceptionHandler(BusinessException.class)
    @ResponseBody  // 이걸 붙여야 JSON 반환
    public ErrorResponse handleBusiness(BusinessException e) {
        return new ErrorResponse(e.getCode(), e.getMessage());
    }
}
```

- 기본적으로 **View 이름을 반환**하는 것으로 간주
- JSON을 반환하려면 메서드마다 `@ResponseBody`를 붙여야 해

**Step 2: @RestControllerAdvice**

```java
@RestControllerAdvice  // = @ControllerAdvice + @ResponseBody
public class GlobalExceptionHandler {
    
    @ExceptionHandler(NotFoundException.class)
    public ErrorResponse handleNotFound(NotFoundException e) {
        return new ErrorResponse("NOT_FOUND", e.getMessage());
        // 자동으로 JSON 변환! @ResponseBody 불필요
    }
}
```

- **모든 메서드에 `@ResponseBody`가 자동 적용**
- REST API 서버라면 거의 100% 이걸 씀

| 비교 | @ControllerAdvice | @RestControllerAdvice |
|------|:---:|:---:|
| 반환 기본 동작 | View 이름 | JSON/XML (직렬화) |
| @ResponseBody 필요? | ✅ 메서드마다 | ❌ 자동 적용 |
| 용도 | MVC (HTML 반환) | REST API (JSON 반환) |
| 관계 | 부모 | `@ControllerAdvice` + `@ResponseBody` |

💡 이건 `@Controller` vs `@RestController` 관계와 **완전히 동일**해.

---

### Q3-3: @ExceptionHandler의 역할

✅ **맞아, 정확한 이해야!**

`@ExceptionHandler`는 **"이 메서드가 어떤 예외를 처리하는 녀석인지"를 표시하는 annotation**이야.

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)      // ← "나는 BusinessException 담당이야"
    public ResponseEntity<ErrorResponse> handleBusiness(BusinessException e) {
        // ...
    }

    @ExceptionHandler(NotFoundException.class)       // ← "나는 NotFoundException 담당이야"
    public ResponseEntity<ErrorResponse> handleNotFound(NotFoundException e) {
        // ...
    }
    
    @ExceptionHandler({IOException.class, TimeoutException.class})  // ← 여러 개도 가능
    public ResponseEntity<ErrorResponse> handleIO(Exception e) {
        // ...
    }
}
```

비유하면:
- `@RestControllerAdvice` = **교무실** (예외를 모아서 처리하는 장소)
- `@ExceptionHandler` = 교무실 안의 **담당 선생님 이름표** ("나는 싸움 담당", "나는 지각 담당")

참고: `@ExceptionHandler`는 `@RestControllerAdvice` 없이도 **개별 Controller 안에서** 쓸 수 있어. 그러면 해당 Controller에서 발생한 예외만 처리해.

```java
@RestController
public class UserController {
    
    @ExceptionHandler(UserNotFoundException.class)  // 이 Controller 안에서만 동작
    public ErrorResponse handleUserNotFound(UserNotFoundException e) {
        // ...
    }
}
```

---

### Q3-4: HTTP Status Code만으로 충분하지 않은가?

좋은 질문이야! 이건 **규모에 따라 답이 달라져.**

#### 현실 세계 비유

병원에 갔는데:
- **HTTP Status Code만** = 의사가 "아파요" 라고만 적어줌 (400 = 잘못 요청, 404 = 못 찾음)
- **도메인 에러 코드** = 의사가 "위염 (A01)", "식도역류 (A02)" 처럼 구체적 병명을 적어줌

둘 다 "배가 아프다(400)"는 같은데, **뭐가 문제인지** 세부 정보가 다르지.

#### 왜 HTTP Status Code만으로는 부족한가?

```
상황 1: 잔액 부족으로 결제 실패
상황 2: 일일 한도 초과로 결제 실패
상황 3: 카드가 만료되어 결제 실패
```

셋 다 HTTP Status Code는 **400 Bad Request** 또는 **422 Unprocessable Entity**야. 클라이언트가 이걸 구분할 방법이 없어.

```json
// HTTP Status Code만
{ "status": 400, "message": "결제 실패" }  // 뭐가 문제인데??

// 도메인 에러 코드 포함
{ 
  "status": 400, 
  "code": "PAYMENT_001",       // 잔액 부족
  "message": "잔액이 부족합니다",
  "detail": "현재 잔액: 1,000원, 필요 금액: 5,000원"
}
```

#### 판단 기준 테이블

| 상황 | HTTP Status만으로 충분? | 도메인 코드 필요? |
|------|:---:|:---:|
| 단순 CRUD API | ✅ | ❌ |
| 내부 마이크로서비스 통신 | ✅ | ⚠️ 선택 |
| 결제/금융 API | ❌ | ✅ |
| Public API (외부 개발자용) | ❌ | ✅ |
| 클라이언트가 에러별 분기 처리 필요 | ❌ | ✅ |
| 에러 모니터링/대시보드 필요 | ❌ | ✅ |

💡 **네 말도 맞아.** 간단한 서비스에서는 HTTP Status Code만으로 충분할 수 있어. 하지만 서비스가 커지면:

1. **같은 400이라도 원인이 다양** → 클라이언트가 에러별로 다른 UI를 보여줘야 함
2. **에러 추적** → "PAYMENT_001이 급증했다"가 "400이 많다"보다 유용
3. **다국어 지원** → 에러 코드로 클라이언트가 적절한 메시지를 매핑

---

### Q3-5: 4xx가 WARNING인 이유, ERROR가 될 수도 있나?

#### 현실 세계 비유

식당에서:
- **4xx (WARNING)** = 손님이 메뉴에 없는 걸 주문함 → 서버(웨이터) 잘못이 아님, "없는 메뉴입니다" 하면 됨
- **5xx (ERROR)** = 주방에서 불이 남 → 식당 자체 문제, 즉시 대응 필요

#### 왜 기본적으로 4xx = WARNING인가?

```
4xx = 클라이언트의 실수 → 서버는 정상 동작 중
5xx = 서버의 문제 → 서버에 장애가 있음
```

로깅의 핵심 목적은 **"우리 시스템에 문제가 있는가?"**를 파악하는 거야. 4xx는 클라이언트가 잘못한 거니까, 서버 운영팀이 긴급 대응할 필요가 없어.

#### ✅ 하지만 네 말도 맞아! 4xx가 ERROR가 되어야 하는 경우

| 상황 | 로그 레벨 | 이유 |
|------|:---:|------|
| 일반적인 400 (잘못된 입력) | ⚠️ WARN | 클라이언트 실수, 서버 정상 |
| 일반적인 404 (없는 페이지) | ⚠️ WARN | 클라이언트가 잘못된 URL 요청 |
| 401/403이 **갑자기 급증** | ❌ ERROR | 보안 공격 가능성 → 즉시 확인 필요 |
| 내부 서비스 간 통신에서 4xx | ❌ ERROR | 내부 서비스는 잘못된 요청을 보내면 안 됨 → 버그 |
| 429 (Rate Limit) 급증 | ❌ ERROR | DDoS 공격이거나 클라이언트 구현 버그 |
| 404인데 **있어야 하는 리소스** | ❌ ERROR | 데이터 정합성 문제일 수 있음 |

```java
@ExceptionHandler(BusinessException.class)
public ResponseEntity<ErrorResponse> handle(BusinessException e) {
    if (e instanceof SecurityRelatedException) {
        log.error("보안 관련 예외 발생: {}", e.getMessage());  // ERROR!
    } else {
        log.warn("비즈니스 예외: {}", e.getMessage());         // WARN
    }
    return ResponseEntity.status(e.getStatus()).body(...);
}
```

💡 **결론**: "4xx = WARN"은 **기본값(default)**이지 **절대 규칙**이 아니야. 상황에 따라 동적으로 로그 레벨을 조절하는 게 좋은 설계야. 특히 **보안 관련 4xx**와 **내부 서비스 간 4xx**는 ERROR로 격상하는 게 맞아.

---

### Q3-6: BusinessException, MethodArgumentNotValidException — 기본 제공?

| 예외 | Spring 기본 제공? | 설명 |
|------|:---:|------|
| `MethodArgumentNotValidException` | ✅ 기본 제공 | `@Valid` 검증 실패 시 Spring이 자동으로 던짐 |
| `BusinessException` | ❌ 직접 만들어야 함 | 관례적 이름이지, Spring에 없음 |

#### 상세 설명

**MethodArgumentNotValidException** — Spring 기본 제공 ✅

```java
// Controller에서 @Valid를 쓰면
@PostMapping("/users")
public User createUser(@Valid @RequestBody CreateUserRequest req) { ... }

// CreateUserRequest의 유효성 검증 실패 시
// Spring이 자동으로 MethodArgumentNotValidException을 던짐
public class CreateUserRequest {
    @NotBlank String name;      // null이면 → 예외 발생
    @Email String email;         // 이메일 형식 아니면 → 예외 발생
    @Min(0) Integer age;         // 음수면 → 예외 발생
}
```

이건 `spring-boot-starter-validation` (Hibernate Validator) 의존성에서 나와. 패키지는 `org.springframework.web.bind`.

**BusinessException** — 직접 만들어야 함 ❌

```java
// 이건 개발자가 직접 정의하는 커스텀 예외
public class BusinessException extends RuntimeException {
    private final ErrorCode errorCode;
    
    public BusinessException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
    }
}

// 이런 식으로 확장
public class InsufficientBalanceException extends BusinessException {
    public InsufficientBalanceException() {
        super(ErrorCode.INSUFFICIENT_BALANCE);
    }
}
```

Spring에서 **기본 제공하는 주요 예외들**을 정리하면:

| 예외 | 발생 상황 |
|------|-----------|
| `MethodArgumentNotValidException` | `@Valid` 검증 실패 |
| `HttpRequestMethodNotSupportedException` | 허용되지 않은 HTTP 메서드 (405) |
| `HttpMediaTypeNotSupportedException` | 지원하지 않는 Content-Type (415) |
| `MissingServletRequestParameterException` | 필수 파라미터 누락 (400) |
| `NoHandlerFoundException` | 매핑된 핸들러 없음 (404) |
| `ResponseStatusException` | 개발자가 상태코드 지정 (다양) |
| `AccessDeniedException` | Spring Security 권한 부족 (403) |

FastAPI 비교:

| Spring Boot | FastAPI |
|---|---|
| `MethodArgumentNotValidException` | `RequestValidationError` (Pydantic) |
| `BusinessException` (커스텀) | 커스텀 Exception class |
| `ResponseStatusException` | `HTTPException` |

---

## Q4. API 버전 관리 전략

### Q4-1: URL 오염과 라우팅 복잡성

#### URL 오염 (URL Pollution)

현실 비유: 집 주소에 **불필요한 정보가 계속 추가**되는 것.

```
정상: 서울시 강남구 테헤란로 123
오염: 서울시 강남구 테헤란로 123 (2024년도버전) (우편번호변경이력있음)
```

API에서:

```
/v1/users/123
/v2/users/123
/v3/users/123
```

**리소스 자체는 같은 User인데**, URL이 달라져. REST 원칙에서 **하나의 리소스는 하나의 URI**로 식별되어야 하는데, 같은 리소스에 여러 URI가 생기는 거야. 이걸 "URL이 오염됐다"고 표현해.

추가 문제:
- 문서화할 때 모든 버전의 URL을 관리해야 함
- 클라이언트가 "어떤 버전 쓰지?" 혼란
- 버전이 쌓이면 URL이 지저분해짐

#### 라우팅 복잡성

```java
// 버전이 3개면 같은 로직에 라우팅이 3벌
@GetMapping("/v1/users/{id}")  // v1 로직
@GetMapping("/v2/users/{id}")  // v2 로직 (v1과 약간 다름)
@GetMapping("/v3/users/{id}")  // v3 로직 (v2와 약간 다름)
```

- 라우팅 테이블이 버전 수 x 엔드포인트 수 만큼 증가
- v1과 v2의 차이가 "필드 하나 추가"뿐인데도 별도 라우팅 필요
- API Gateway에서 라우팅 규칙 관리가 복잡해짐

⚠️ 단, 이건 **이론적 단점**이고, 실무에서는 URI 방식이 **가장 널리 쓰이는 방식**이야. 단점이 있지만 단순하고 명확하다는 장점이 더 크기 때문이야.

---

### Q4-2: CDN에서 API 응답을 캐싱하는가?

#### 짧은 답변: ✅ 해. 하지만 **모든 API를 하는 건 아니야.**

#### 현실 비유

CDN 캐싱은 **편의점 진열대**와 같아:
- 자주 팔리는 인기 상품(자주 조회되는 읽기 전용 API) → 진열대에 진열 ✅
- 주문 제작 상품(개인화된 API 응답) → 진열 안 함 ❌

#### CDN에서 캐싱하기 좋은 API vs 안 하는 API

| 캐싱 적합 | 캐싱 부적합 |
|-----------|-------------|
| `GET /v1/products` (상품 목록) | `POST /v1/orders` (주문 생성) |
| `GET /v1/categories` (카테고리) | `GET /v1/users/me` (개인 정보) |
| `GET /v1/config` (앱 설정) | `GET /v1/cart` (장바구니) |
| Public API 응답 | 인증 필요한 API |

#### ✅ 네 말이 맞아 — 세밀한 제어 가능

```
# CDN 설정 예시 (Cloudflare/AWS CloudFront)
/v1/products/*     → Cache TTL: 5분
/v1/categories/*   → Cache TTL: 1시간
/v1/users/*        → No Cache (Bypass)
/v1/orders/*       → No Cache (Bypass)
```

- **어떤 API를 캐싱할지**: 경로(path) 기반 규칙으로 지정
- **Invalidation 기준**: TTL(Time to Live) 설정, 또는 수동 purge API 호출
- **Cache-Control 헤더**: 서버가 `Cache-Control: public, max-age=300` 같이 헤더로 지시

URI 방식(`/v1/`, `/v2/`)이 CDN 캐싱에 유리한 이유는, CDN이 **URL 기반으로 캐시 키를 만들기 때문**이야. `/v1/products`와 `/v2/products`가 자동으로 다른 캐시 엔트리가 돼. Header 방식은 CDN이 `Vary` 헤더를 해석해야 해서 설정이 복잡해져.

---

### Q4-3: URI vs URL

#### 현실 비유

- **URI** = 사람의 **이름** (식별만 하면 됨). "김철수"
- **URL** = 사람의 **집 주소** (찾아갈 수 있음). "서울시 강남구 테헤란로 123에 사는 김철수"

#### 관계

```
URI (Uniform Resource Identifier) — 리소스를 "식별"
 ├── URL (Uniform Resource Locator) — 위치로 식별 (접근 방법 포함)
 └── URN (Uniform Resource Name) — 이름으로 식별
```

| | URI | URL | URN |
|--|-----|-----|-----|
| 의미 | 리소스 식별자 | 리소스 위치 | 리소스 이름 |
| 예시 | `/users/123` | `https://api.com/users/123` | `urn:isbn:0451450523` |
| 접근 방법 포함? | 아닐 수도 있음 | ✅ 항상 (https, ftp 등) | ❌ 없음 |
| 관계 | 상위 개념 | URI의 하위 | URI의 하위 |

📌 **실무에서는?** 거의 구분 없이 혼용해. 대부분의 웹 API 맥락에서 URI라고 하면 URL을 의미해. 면접에서는 "URI는 식별자의 상위 개념이고, URL은 위치를 포함하는 URI의 하위 개념입니다" 정도로 답하면 충분해.

---

### Q4-4: 쿼리 파라미터 & 커스텀 헤더 방식, X- 접두사는 표준?

#### 쿼리 파라미터 방식

```
GET /users/123?version=2
GET /users/123?api-version=2024-01-15    ← Azure 스타일
```

실제 사용하는 곳: **Microsoft Azure API**, Google Cloud 일부

#### 커스텀 헤더 방식

```
GET /users/123
X-API-Version: 2
```

또는:

```
GET /users/123
Api-Version: 2
```

#### ⚠️ X- 접두사는 더 이상 표준이 아니야!

이건 중요한 포인트야:

| 시기 | 상태 | 설명 |
|------|------|------|
| 2012년 이전 | 표준 관례 | RFC 2047 등에서 비표준 헤더에 `X-` 붙이는 게 관례 |
| 2012년 (RFC 6648) | **공식 폐기(deprecated)** | `X-` 접두사 사용을 **더 이상 권장하지 않음** |
| 현재 | 레거시 유지 | 기존 `X-Request-ID`, `X-Forwarded-For` 등은 관성으로 남아 있음 |

**왜 폐기됐나?**

비표준으로 시작한 `X-` 헤더가 나중에 표준이 되면 이름을 바꿔야 하는 문제가 있었어. 예를 들어:
- `X-Forwarded-For` → 나중에 표준인 `Forwarded` 헤더가 생겼지만, 이미 다들 `X-Forwarded-For` 쓰고 있어서 바꿀 수가 없음

**현재 권장**:

```
# 올바른 방식 (X- 없이)
Api-Version: 2
Request-Id: abc-123

# 레거시 (여전히 널리 쓰임)
X-API-Version: 2
X-Request-ID: abc-123
```

💡 면접에서 물어보면: "X- 접두사는 RFC 6648에서 2012년에 폐기되었습니다. 새로 만드는 커스텀 헤더는 X- 없이 명명하는 것이 권장되지만, 기존의 X-Forwarded-For 같은 헤더는 관성으로 계속 사용됩니다."

---

### Q4-5: Content Negotiation, RESTful 원칙

#### Content Negotiation이 뭐야?

현실 비유: **같은 책을 다른 언어로 읽는 것**.

서점에 가서 "해리포터 주세요"라고 하면:
- "한국어로요? 영어로요?" → **언어 협상**
- "종이책이요? 전자책이요?" → **형식 협상**

HTTP에서도 **같은 리소스**를 클라이언트가 원하는 **형식으로 달라고 요청**할 수 있어:

```http
# "JSON으로 주세요"
GET /users/123
Accept: application/json

# "XML로 주세요"
GET /users/123
Accept: application/xml

# "버전 2의 JSON으로 주세요" (버저닝에 활용)
GET /users/123
Accept: application/vnd.myapi.v2+json
```

이게 **Content Negotiation** — 클라이언트와 서버가 리소스의 **표현(representation)**을 협상하는 것.

#### 왜 이게 RESTful 원칙을 준수하는가?

REST의 핵심 원칙 중 하나:

> **"리소스"와 "리소스의 표현"은 분리되어야 한다.**

- **리소스**: User ID 123번 (추상적 개념)
- **표현**: JSON, XML, v1 형식, v2 형식 (구체적 형태)

```
# Content Negotiation 방식 (RESTful) ✅
GET /users/123                          ← 리소스 URI는 하나
Accept: application/vnd.myapi.v2+json   ← 표현을 헤더로 협상

# URI 방식 ⚠️
GET /v1/users/123                       ← 같은 리소스인데 URI가 다름
GET /v2/users/123                       ← URI에 "표현 정보"가 섞임
```

#### URI 방식은 RESTful하지 않은가?

| 원칙 | Content Negotiation | URI 방식 |
|------|:---:|:---:|
| 하나의 리소스 = 하나의 URI | ✅ `/users/123` | ❌ `/v1/users/123`, `/v2/users/123` |
| 리소스와 표현의 분리 | ✅ 헤더로 분리 | ⚠️ URI에 표현 정보 혼합 |
| HATEOAS 친화적 | ✅ 링크가 깔끔 | ⚠️ 링크에 버전 포함 |
| 캐싱 용이성 | ⚠️ `Vary` 헤더 필요 | ✅ URL만으로 캐시 키 |
| 사용 편의성 | ❌ 헤더 설정 필요 | ✅ URL만 바꾸면 됨 |
| 브라우저 테스트 | ❌ 어려움 | ✅ URL 입력만으로 가능 |

⚠️ **중요**: URI 방식이 "RESTful하지 않다"고 말하기보다, "**학술적으로 엄격한 REST 제약 조건을 완벽히 충족하지는 않지만, 실용적으로 가장 많이 쓰이는 방식**"이라고 이해하는 게 맞아.

#### RESTful 원칙 정리

Roy Fielding이 2000년 박사 논문에서 정의한 REST의 6가지 제약 조건:

| 제약 조건 | 설명 | 비유 |
|-----------|------|------|
| **Client-Server** | 클라이언트와 서버 분리 | 손님과 주방 분리 |
| **Stateless** | 서버가 클라이언트 상태를 저장하지 않음 | 매번 주문서 전체를 제출 |
| **Cacheable** | 응답이 캐시 가능해야 함 | 자주 나가는 메뉴는 미리 준비 |
| **Uniform Interface** | 일관된 인터페이스 (리소스 식별, 표현으로 조작, 자기 서술적 메시지, HATEOAS) | 모든 식당이 같은 주문 방식 |
| **Layered System** | 계층적 구조 허용 | 중간에 매니저가 있어도 됨 |
| **Code on Demand** (선택) | 서버가 코드를 보낼 수 있음 | 조리법을 손님에게 줄 수도 |

Content Negotiation은 **Uniform Interface** 중 "리소스와 표현의 분리" 원칙에 해당해.

### 💡 면접용 정리

> "API 버전 관리에서 URI 방식이 가장 실용적이고 널리 쓰이지만, 엄밀한 REST 관점에서는 Content Negotiation이 리소스와 표현의 분리 원칙에 더 부합합니다. 실무에서는 팀의 상황과 클라이언트 편의성을 고려해 선택하되, 대부분의 경우 URI 방식이 가장 합리적인 선택입니다."

---

긴 질문들인데, 핵심을 요약하면:

1. **HATEOAS**: Richardson Maturity Model Level 3으로, 실무에서는 비용 대비 효과를 따져 수준을 선택
2. **헥사고날 도메인 내부**: 네 이해가 맞음. Port & Adapter는 경계 규칙이고, 내부는 Layered/Clean/DDD 자유 선택
3. **Spring 예외 처리**: FastAPI의 `exception_handler`와 동일 패턴. `BusinessException`은 커스텀, `MethodArgumentNotValidException`은 Spring 기본 제공
4. **API 버전 관리**: URI 방식이 실용적 주류. Content Negotiation이 REST 원칙에는 더 부합하지만 실용성에서 밀림. `X-` 접두사는 RFC 6648로 폐기됨


---

### Q5. DTO와 Entity를 분리해야 하는 이유와 매핑 전략은?

**A.** 분리 이유:

1. **보안**: Entity의 민감 필드(password, 내부 ID)가 API에 노출되는 것을 방지
2. **유연성**: API 스펙 변경이 DB 스키마에 영향 주지 않음 (반대도 동일)
3. **직렬화 제어**: Entity의 양방향 관계에서 발생하는 순환 참조 방지
4. **검증 분리**: 입력 DTO에 `@Valid` 검증을, Entity에 DB 제약 조건을 분리

**매핑 전략 비교**:

| 방식 | 도구 | 장점 | 단점 |
|------|------|------|------|
| 수동 매핑 | 직접 코드 | 완전 제어, 디버깅 쉬움 | 보일러플레이트 |
| MapStruct | 컴파일 타임 코드 생성 | 타입 안전, 성능 최적 | 설정 필요 |
| ModelMapper | 리플렉션 기반 | 설정 간단 | 런타임 오류 가능, 성능 저하 |
| Kotlin data class copy | `copy()` 함수 | Kotlin 네이티브, 간결 | 깊은 복사 제한 |

**권장**: Kotlin 프로젝트에서는 **확장 함수(extension function)** 를 활용한 수동 매핑이 간결하고 타입 안전합니다:

```kotlin
fun UserEntity.toDto() = UserResponse(id = this.id, name = this.name, email = this.email)
fun CreateUserRequest.toEntity() = UserEntity(name = this.name, email = this.email)
```

---


---

이제 충분한 근거를 확보했습니다. 볼트에 있는 기존 노트들과 데이터베이스 내부 동작에 대한 지식을 바탕으로 상세 답변을 작성하겠습니다.

---

## Q6. MySQL과 PostgreSQL의 핵심 차이 (심화 질문 모음)

---

### Q6-1: MVCC 구현이 뭐지?

#### 📌 먼저 MVCC가 뭔지

MVCC(Multi-Version Concurrency Control)는 **여러 사람이 동시에 같은 데이터를 읽고 쓸 수 있게 해주는 기술**이야. 핵심 원리는 "데이터를 수정할 때 이전 버전을 남겨두어, 다른 사람이 이전 버전을 읽을 수 있게 하는 것"이야.

> 🧒 **12살 비유 — 도서관의 책 수정 방식**
>
> 도서관에 "세계 역사" 책이 있어. 여러 사람이 동시에 이 책을 읽고 싶어 하는데, 누군가 책 내용을 수정해야 할 때 어떻게 할까? MySQL과 PostgreSQL은 이 문제를 완전히 다른 방식으로 풀어.

---

#### 📘 MySQL (InnoDB) — Undo Log 기반: "원본 위에 덧쓰고, 수정 전 내용은 메모장에 적어두기"

**비유**: 도서관에 책이 딱 1권 있어. 누군가 책 내용을 고치면, **원본 책 위에 바로 새 내용을 덧씌워**. 하지만 수정하기 전의 내용을 별도 **메모장(Undo Log)** 에 적어둬. 다른 사람이 "나는 수정 전 버전을 보고 싶어"라고 하면, 메모장을 뒤져서 이전 버전을 복원해서 보여줘.

**단계별 동작:**

1. **UPDATE가 발생하면**: 현재 행(row)을 **제자리(in-place)에서 직접 수정**
2. **수정 전 값은 Undo Log에 저장**: Undo Log는 체인처럼 연결돼서, 버전1 → 버전2 → 버전3... 이런 식으로 이전 버전들이 연결
3. **읽기(SELECT)할 때**: 
   - 행의 `DB_TRX_ID`(이 행을 마지막으로 수정한 트랜잭션 ID)를 확인
   - 내 트랜잭션보다 나중에 수정된 거면 → Undo Log를 따라가서 나한테 보이는 버전을 찾음
   - 내 트랜잭션보다 이전에 수정된 거면 → 현재 행을 바로 읽음 (빠름!)

```
[테이블 데이터 페이지]         [Undo Log]
┌──────────────────┐         ┌──────────────┐
│ id=1, name="Bob" │ ──────► │ name="Alice" │ (이전 버전)
│ DB_TRX_ID = 200  │         │ TRX_ID = 150 │
└──────────────────┘         └──────┬───────┘
                                    │
                              ┌─────▼────────┐
                              │ name="Anna"  │ (더 이전 버전)
                              │ TRX_ID = 100 │
                              └──────────────┘
```

**💡 핵심 특징:**
- 최신 데이터 읽기가 빠름 (Undo Log 안 봐도 됨)
- 오래된 스냅샷을 읽으면 Undo Log 체인을 쭉 따라가야 해서 느려질 수 있음

---

#### 📗 PostgreSQL — 다중 버전 튜플 직접 저장: "새 판 책을 옆에 꽂아두기"

**비유**: 도서관에 같은 책의 **여러 판(edition)을 전부 서가에 꽂아둬**. 2024년판, 2025년판, 2026년판... 다 있어. 수정할 때 원본을 건드리지 않고, **새 판을 만들어서 옆에 꽂아**. 각 사람이 도서관에 입장한 시점에 맞는 판을 읽으면 돼.

**단계별 동작:**

1. **UPDATE가 발생하면**: 기존 행은 그대로 두고, **새로운 행(튜플)을 만들어서 테이블에 추가**
2. **기존 행에는 "삭제 표시(xmax)"를 남김**: "이 버전은 트랜잭션 200번에서 더 이상 유효하지 않다"
3. **새 행에는 "생성 표시(xmin)"**: "이 버전은 트랜잭션 200번에서 만들어졌다"
4. **읽기(SELECT)할 때**: 내 스냅샷 기준으로 xmin/xmax를 보고 보이는 버전을 결정

```
[같은 테이블 데이터 페이지 안에 여러 버전이 공존]

┌─────────────────────────────────────┐
│ id=1, name="Anna", xmin=100, xmax=150  │ ← TRX 100~149 사이에 시작한 트랜잭션에 보임
│ id=1, name="Alice", xmin=150, xmax=200 │ ← TRX 150~199 사이에 시작한 트랜잭션에 보임
│ id=1, name="Bob",  xmin=200, xmax=0    │ ← TRX 200 이후 시작한 트랜잭션에 보임 (현재 유효)
└─────────────────────────────────────┘
```

**💡 핵심 특징:**
- UPDATE가 사실상 INSERT + DELETE 표시 → 쓰기 자체는 빠를 수 있음
- 하지만 테이블에 **죽은 튜플(dead tuple)**이 계속 쌓임 → 디스크 팽창

---

#### 🧹 PostgreSQL의 VACUUM — 왜 필요하고, 어떤 문제를 일으키는가

**비유 이어가기**: 도서관에 옛날 판 책들이 계속 쌓이면 어떻게 될까? 서가가 꽉 차서 새 책을 놓을 자리가 없어져. 그래서 **사서(VACUUM)**가 주기적으로 "아무도 안 읽는 옛날 판"을 골라서 치워야 해.

**VACUUM이 필요한 이유:**
1. PostgreSQL은 UPDATE/DELETE 시 이전 버전을 테이블에 그대로 놔둠
2. 이 dead tuple들이 쌓이면 **테이블 팽창(bloat)** 발생 → 디스크 공간 낭비 + 풀 스캔 느려짐
3. 또한 **Transaction ID Wraparound** 문제: PostgreSQL의 트랜잭션 ID는 32비트(약 42억)이고 순환함. VACUUM이 오래된 데이터를 정리해야 "frozen" 표시를 해서 wraparound를 방지

**VACUUM 종류:**

| 종류 | 동작 | 테이블 잠금 | 용도 |
|------|------|------------|------|
| **VACUUM (일반)** | dead tuple을 "재사용 가능"으로 표시 | ❌ 잠금 없음 | 일상적 정리 |
| **VACUUM FULL** | 테이블 전체를 새로 다시 씀 | ✅ 배타적 잠금 | 심한 bloat 해소 |
| **autovacuum** | 백그라운드에서 자동 실행 | ❌ 잠금 없음 | 기본 운영 |

**⚠️ VACUUM 때문에 발생하는 주요 문제들:**

1. **테이블 Bloat**: autovacuum이 충분히 자주/빠르게 못 돌면 dead tuple이 쌓여서 테이블이 실제 데이터보다 2~10배 커질 수 있음. SELECT 풀 스캔 시 dead tuple도 읽어야 해서 느려짐.

2. **VACUUM FULL 시 서비스 중단**: VACUUM FULL은 테이블에 배타적 잠금(Access Exclusive Lock)을 걸어서, 그 동안 해당 테이블 읽기/쓰기 불가. 큰 테이블이면 수십 분~수 시간 걸릴 수 있음.

3. **장기 트랜잭션이 VACUUM 차단**: 어떤 트랜잭션이 1시간 동안 열려 있으면, 그 트랜잭션이 시작된 이후의 모든 dead tuple을 VACUUM이 정리 못함 → dead tuple 폭발적 증가

4. **Transaction ID Wraparound 위험**: VACUUM이 오래된 데이터를 "frozen" 처리 못하면, 트랜잭션 ID가 순환하면서 **데이터가 갑자기 "미래에서 온 것"처럼 보여서 보이지 않게 됨** → 사실상 데이터 손실. PostgreSQL은 이를 방지하기 위해 극단적으로 **DB 전체를 읽기 전용으로 전환**(failsafe autovacuum)함.

5. **autovacuum 설정 튜닝 어려움**: 기본 설정은 보수적이라 대용량/고트래픽 테이블에서는 부족. `autovacuum_vacuum_scale_factor`, `autovacuum_vacuum_cost_delay` 등을 테이블 단위로 튜닝해야 함.

---

#### ✅ MySQL의 Undo Log는 왜 VACUUM이 필요 없는가

**비유**: MySQL은 도서관에 책이 항상 1권만 있고, 수정 전 내용은 메모장(Undo Log)에 적어둔다고 했잖아? 이 메모장은 **Purge Thread라는 자동 청소 로봇**이 알아서 치워줘. 그리고 이 청소 작업이 훨씬 간단해.

**왜 간단한가:**

| 비교 | PostgreSQL VACUUM | MySQL Purge |
|------|-------------------|-------------|
| **정리 대상 위치** | 테이블 데이터 페이지 안에 있음 (같은 공간) | 별도 Undo Tablespace에 있음 (분리됨) |
| **정리 방식** | dead tuple을 "재사용 가능" 표시 or 테이블 재작성 | Undo Log 세그먼트를 해제 (append-only 구조라 간단) |
| **테이블 크기 영향** | dead tuple 때문에 테이블이 부풀어오름 | 테이블 자체는 항상 최신 데이터만 → 부풀지 않음 |
| **잠금 필요** | VACUUM FULL은 테이블 잠금 필요 | Purge는 잠금 필요 없음 |
| **별도 관리** | autovacuum 튜닝 필요 | 거의 자동 (innodb_purge_threads 정도) |

**핵심 차이의 근본적 이유:**

MySQL/InnoDB는 **최신 버전을 테이블에, 과거 버전을 별도 공간(Undo Log)에** 저장하기 때문에:
- 테이블 자체는 항상 깨끗 (dead tuple 개념 없음)
- Undo Log는 별도 관리되는 공간이라, "이 Undo Log를 참조하는 트랜잭션이 더 이상 없으면" 간단히 해제하면 됨
- 별도로 DBA가 "VACUUM"을 신경 쓸 필요가 없음

⚠️ **다만 MySQL도 완전히 문제가 없진 않아**: 장기 트랜잭션이 있으면 Undo Log가 해제되지 못하고 계속 커져서 디스크 공간을 차지하고, Undo Log 체인이 길어지면 읽기 성능도 저하됨. 하지만 PostgreSQL처럼 "테이블 자체가 부풀어오르는" 문제는 없어서 관리가 훨씬 쉬움.

---

### Q6-2: JSON 지원 차이

#### 📌 MySQL JSON vs PostgreSQL JSONB — 뭐가 다른 건데?

> 🧒 **비유**: MySQL의 JSON은 **편지를 봉투에 넣어서 보관하는 것**이야. 편지를 찾으려면 매번 봉투를 뜯어서 읽어야 해. PostgreSQL의 JSONB는 **편지 내용을 분해해서 색인 카드로 정리해둔 것**이야. "주소가 서울인 편지"를 찾고 싶으면 색인 카드만 넘기면 됨.

#### 내부 저장 방식의 차이

| 항목        | MySQL JSON                          | PostgreSQL JSONB                 |                                |
| --------- | ----------------------------------- | -------------------------------- | ------------------------------ |
| **저장 형태** | 텍스트를 파싱해서 바이너리로 저장 (but 내부 구조 제한적)  | 분해(decomposed) 바이너리 형태로 저장       |                                |
| **키 조회**  | 바이너리 내에서 키를 순차 탐색                   | 해시 기반으로 키 직접 접근                  |                                |
| **인덱스**   | 가상 컬럼(Generated Column) 만들어서 B-Tree | **GIN 인덱스로 JSON 내부 키/값 전체를 인덱싱** |                                |
| **연산자**   | `JSON_EXTRACT()`, `->`, `->>` 정도    | `@>`, `?`, `?                    | `, `?&`, `#>`, `#>>` 등 풍부한 연산자 |
| **키 순서**  | 보존                                  | 보존하지 않음 (바이너리 변환 시 정렬)           |                                |
| **중복 키**  | 마지막 값 유지                            | 마지막 값 유지                         |                                |

#### 핵심 차이: 인덱싱 능력

**MySQL** — JSON 컬럼 자체에 인덱스를 걸 수 없음:
```sql
-- MySQL: JSON 내부 값을 검색하려면 가상 컬럼을 따로 만들어야 함
ALTER TABLE products 
ADD COLUMN category VARCHAR(50) 
GENERATED ALWAYS AS (JSON_UNQUOTE(data->'$.category')) STORED;

CREATE INDEX idx_category ON products(category);

-- 검색할 수 있는 키를 사전에 알아야 하고, 키마다 컬럼+인덱스 추가 필요
```

**PostgreSQL** — GIN 인덱스 하나로 JSON 내부 전체를 인덱싱:
```sql
-- PostgreSQL: GIN 인덱스 하나면 JSON 내부 모든 키/값 검색 가능
CREATE INDEX idx_data ON products USING GIN (data);

-- 이제 어떤 키든 인덱스를 타는 검색 가능
SELECT * FROM products WHERE data @> '{"category": "electronics"}';
SELECT * FROM products WHERE data ? 'discount';  -- 키 존재 여부
SELECT * FROM products WHERE data @> '{"tags": ["sale"]}';  -- 배열 포함
```

#### 개발자 관점 장단점

| 관점 | MySQL JSON | PostgreSQL JSONB |
|------|-----------|-----------------|
| **✅ 장점** | 스키마 검증 내장 (유효하지 않은 JSON 거부), 키 순서 보존, 단순한 사용법 | 강력한 인덱싱, 풍부한 연산자, 부분 업데이트 가능, 복잡 쿼리 지원 |
| **❌ 단점** | 인덱싱 제한 (가상 컬럼 필요), 연산자 부족, 부분 업데이트 시 전체 재작성 | 키 순서 미보존, 약간의 저장 공간 오버헤드, 입력 시 바이너리 변환 비용 |
| **적합 시나리오** | 단순 설정값 저장, 스키마가 고정된 JSON | 유연한 스키마, 복잡한 검색/필터링, 문서형 데이터 |

💡 **실무 팁**: Python/FastAPI + SQLAlchemy 경험이 있으니, SQLAlchemy에서 `JSONB` 타입을 쓰면 `@>` 같은 PostgreSQL 전용 연산자를 ORM 수준에서 사용할 수 있어:
```python
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column

class Product(Base):
    data = Column(JSONB)

# 쿼리
session.query(Product).filter(
    Product.data['category'].astext == 'electronics'
)
```

---

### Q6-3: 풀텍스트 검색

#### `LIKE '%keyword%'`는 풀텍스트 검색인가?

**❌ 아니야.** `LIKE '%keyword%'`는 풀텍스트 검색이 아니라 **패턴 매칭(pattern matching)**이야. 풀텍스트 검색과는 근본적으로 다른 메커니즘이야.

> 🧒 **비유**: `LIKE '%keyword%'`는 **도서관의 모든 책을 하나하나 펼쳐서, 모든 페이지의 모든 줄을 눈으로 읽으면서 "keyword"라는 단어가 있는지 찾는 것**이야. 풀텍스트 검색은 **도서관 뒤에 있는 "색인(index)" 책을 펴서, "keyword"를 찾으면 "이 단어는 3번 책 42쪽, 7번 책 15쪽에 있습니다"라고 바로 알려주는 것**이야.

**왜 `LIKE '%keyword%'`가 slow query를 일으키는지:**

1. 앞에 `%`가 붙으면 **B-Tree 인덱스를 사용할 수 없음** (인덱스는 접두사 기반이라 "이 글자로 시작하는 것"만 빠르게 찾음)
2. 따라서 **Full Table Scan** 발생 → 테이블의 모든 행을 하나하나 확인
3. 100만 행이면 100만 번 문자열 비교 → 당연히 느림

---

#### PostgreSQL의 GIN 인덱스 + tsvector가 이 문제를 어떻게 해결하는가

**Step 1 — tsvector란?**

tsvector는 **텍스트를 검색에 최적화된 형태로 변환한 것**이야.

```
원본 텍스트: "The quick brown fox jumps over the lazy dog"
tsvector:    'brown':3 'dog':9 'fox':4 'jump':5 'lazi':8 'quick':2
```

- 불용어(the, over) 제거
- 어근(stemming) 추출 (jumps → jump, lazy → lazi)
- 각 단어의 **위치 정보** 저장

**Step 2 — GIN 인덱스란?**

GIN(Generalized Inverted Index)은 **역색인(inverted index)**이야. 구글 검색 엔진이 웹페이지를 찾는 것과 같은 원리야.

```
[GIN 인덱스 내부 구조]

"brown"  → {row_id: 1, 5, 42, 100}
"fox"    → {row_id: 1, 33}
"jump"   → {row_id: 1, 5, 7, 88, 200}
"quick"  → {row_id: 1, 99}
...

"brown"을 검색하면 → 바로 row 1, 5, 42, 100을 반환 (테이블 풀 스캔 없음!)
```

**Step 3 — 실제 사용:**
```sql
-- 1. tsvector 컬럼 추가 + GIN 인덱스 생성
ALTER TABLE articles ADD COLUMN search_vector tsvector;
UPDATE articles SET search_vector = to_tsvector('english', title || ' ' || body);
CREATE INDEX idx_search ON articles USING GIN (search_vector);

-- 2. 풀텍스트 검색 (인덱스를 탐)
SELECT * FROM articles 
WHERE search_vector @@ to_tsquery('english', 'quick & fox');

-- 3. 순위 매기기까지 가능
SELECT *, ts_rank(search_vector, to_tsquery('english', 'database')) AS rank
FROM articles 
WHERE search_vector @@ to_tsquery('english', 'database')
ORDER BY rank DESC;
```

**⚠️ PostgreSQL에서도 slow query가 발생할 수 있는 경우:**
- GIN 인덱스를 만들지 않고 `to_tsvector()` 함수를 직접 WHERE에 쓰면 → 매번 변환 + 풀 스캔
- 매우 일반적인 단어(stopword가 아닌데 거의 모든 행에 있는 단어)를 검색하면 → 인덱스를 타도 결과가 너무 많아서 느림
- GIN 인덱스 업데이트 비용: INSERT/UPDATE가 매우 빈번하면 GIN 인덱스 유지 비용이 높음
- 하지만 **`LIKE '%keyword%'`에 비하면 차원이 다른 성능**

---

#### MySQL에서 풀텍스트 검색 문제를 어떻게 해결하나

**방법 1: MySQL FULLTEXT 인덱스 사용 (내장)**

```sql
-- FULLTEXT 인덱스 생성
ALTER TABLE articles ADD FULLTEXT INDEX ft_idx (title, body);

-- 검색 (LIKE 대신 MATCH...AGAINST 사용)
SELECT * FROM articles 
WHERE MATCH(title, body) AGAINST('keyword' IN BOOLEAN MODE);
```

| 항목 | MySQL FULLTEXT | PostgreSQL tsvector + GIN |
|------|---------------|--------------------------|
| 언어 지원 | 영어 위주 (한국어/CJK는 ngram parser 필요) | 다국어 사전 지원, 커스텀 사전 가능 |
| 연산자 | `+`, `-`, `*`, `""` (기본적) | `&`, `|`, `!`, `<->` (근접 검색), 가중치 |
| 순위 매기기 | 기본적인 relevance | `ts_rank`, `ts_rank_cd` (커버 밀도) |
| 인덱스 타입 | InnoDB FULLTEXT (inverted index) | GIN (더 범용적) |
| CJK 한국어 | ngram parser (MySQL 5.7.6+) 필요 | 별도 사전 설정 필요 |

**방법 2: 외부 검색 엔진 (가장 흔한 실무 해결책)**

실무에서 MySQL로 풀텍스트 검색이 필요하면, 대부분 **외부 검색 엔진**을 도입해:

| 솔루션 | 특징 | 적합 |
|--------|------|------|
| **Elasticsearch** | 분산 검색 엔진, 강력한 분석/집계 | 대규모 로그, 복잡한 검색 요구 |
| **Meilisearch** | 가볍고 빠름, 타이핑 중 검색 | 소규모~중규모, 빠른 구축 |
| **OpenSearch** | Elasticsearch fork, AWS 관리형 | AWS 인프라 |

**방법 3: 가상 컬럼 + B-Tree (간단한 경우)**

특정 패턴만 검색한다면:
```sql
-- 접두사 검색으로 바꿀 수 있다면
WHERE name LIKE 'keyword%'  -- B-Tree 인덱스 사용 가능!

-- 또는 역순 인덱스
ALTER TABLE t ADD COLUMN name_reversed VARCHAR(255) 
GENERATED ALWAYS AS (REVERSE(name)) STORED;
CREATE INDEX idx_rev ON t(name_reversed);
-- 접미사 검색: WHERE name_reversed LIKE REVERSE('%keyword')
```

💡 **네 경험과 연결**: MySQL 8.x에서 `LIKE '%keyword%'` slow query를 겪었다면, 가장 현실적인 해결책은:
1. 먼저 `FULLTEXT` 인덱스 + `MATCH...AGAINST`로 전환 시도
2. 한국어가 포함되면 `ngram_token_size` 설정과 함께 ngram parser 사용
3. 검색 요구사항이 복잡하면 Elasticsearch 같은 전용 엔진 도입

---

### Q6-4: 확장성

#### 어떤 확장성을 이야기하는 거야?

여기서 말하는 확장성(Extensibility)은 **하드웨어 확장(스케일링)이 아니라, 데이터베이스 기능 자체를 확장할 수 있는 능력**이야.

> 🧒 **비유**: 
> - MySQL은 **조립식 장난감 세트**야. 설명서에 있는 모델만 만들 수 있어. 부품을 바꾸거나 새 부품을 추가하는 건 제한적.
> - PostgreSQL은 **레고**야. 기본 블록으로 원하는 거 다 만들 수 있고, 다른 회사의 특수 블록(확장 모듈)도 끼울 수 있어.

#### MySQL의 확장 — 무엇이 가능하고 왜 제한적인가

**MySQL이 할 수 있는 것:**
- 스토리지 엔진 교체 (InnoDB, MyISAM, MEMORY 등) — 이건 MySQL의 독특한 장점
- UDF(User Defined Function)를 C/C++로 작성
- 플러그인 시스템 (인증, 감사, 암호화 등)

**왜 제한적인가:**

| 제한 | 설명 |
|------|------|
| **커스텀 데이터 타입 불가** | INT, VARCHAR, JSON 등 내장 타입만 사용. "좌표", "화폐", "IP주소" 같은 새 타입을 만들 수 없음 |
| **커스텀 인덱스 타입 불가** | B-Tree, Hash, FULLTEXT, R-Tree만 제공. 새로운 인덱스 알고리즘을 추가할 수 없음 |
| **커스텀 연산자 불가** | `+`, `-`, `=` 같은 연산자를 새로 정의하거나 오버로딩 불가 |
| **프로시저 언어 제한** | SQL과 (제한적인) 내장 프로시저 언어만 사용. Python이나 JavaScript로 함수 작성 불가 |
| **외부 데이터 접근 제한** | 다른 DB나 파일 시스템을 "외부 테이블"로 연결하는 표준 방법 없음 |

---

#### PostgreSQL의 확장 — 커스텀 타입, 함수, 확장 모듈

**1) 커스텀 데이터 타입 (Custom Types)**

PostgreSQL은 새로운 데이터 타입을 만들 수 있어:
```sql
-- 복합 타입 (Composite Type)
CREATE TYPE address AS (
    street TEXT,
    city TEXT,
    zip_code VARCHAR(10)
);

-- 열거 타입 (Enum)
CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');

-- 범위 타입 (Range Type)
CREATE TYPE salary_range AS RANGE (subtype = numeric);
```

**2) 커스텀 함수 — 여러 언어로 작성 가능**

```sql
-- PL/pgSQL (기본)
CREATE FUNCTION calculate_tax(price NUMERIC) RETURNS NUMERIC AS $$
BEGIN
    RETURN price * 0.1;
END;
$$ LANGUAGE plpgsql;

-- PL/Python (Python으로 DB 함수 작성!)
CREATE FUNCTION sentiment_analysis(text_input TEXT) RETURNS TEXT AS $$
    import nltk  -- Python 라이브러리 사용 가능!
    return analyze(text_input)
$$ LANGUAGE plpython3u;

-- PL/V8 (JavaScript로도 가능)
```

**3) 확장 모듈(Extension) — PostgreSQL의 핵심 강점**

`CREATE EXTENSION` 한 줄로 강력한 기능을 추가:

| 확장 모듈 | 기능 | MySQL에서의 대안 |
|-----------|------|-----------------|
| **PostGIS** | 지리/공간 데이터 처리 (위도/경도 검색, 거리 계산) | MySQL Spatial (매우 제한적) |
| **pg_trgm** | 유사 문자열 검색 (오타 허용, fuzzy match) | 없음 (앱 레벨에서 처리) |
| **hstore** | 키-값 저장 (JSONB보다 가벼움) | 없음 |
| **uuid-ossp** | UUID 생성 | MySQL 8.0+ UUID() 함수 (제한적) |
| **pgcrypto** | 암호화 함수 | AES_ENCRYPT 등 (제한적) |
| **timescaledb** | 시계열 데이터 최적화 | 없음 (InfluxDB 등 별도 DB 필요) |
| **pg_stat_statements** | 쿼리 성능 분석 | Performance Schema (내장) |
| **FDW (Foreign Data Wrapper)** | 다른 DB/CSV/API를 외부 테이블로 연결 | FEDERATED 엔진 (매우 제한적) |

💡 **핵심 차이의 근본 이유**: PostgreSQL은 설계 초기부터 **"사용자가 타입, 연산자, 인덱스, 함수를 확장할 수 있는 카탈로그 기반 아키텍처"**로 만들어졌어. 시스템 카탈로그(pg_type, pg_operator, pg_proc 등)에 새 항목을 등록하면 엔진이 자연스럽게 인식함. MySQL은 **애플리케이션 중심 설계**로, 빠르고 간단한 사용에 초점을 맞추다 보니 내부 확장 포인트가 적어.

---

### Q6-5: 쓰기 성능

#### PostgreSQL INSERT가 더 빠르고 MySQL이 느린 것 아닌가?

**좋은 질문이야. 상황에 따라 다르고, 단순 비교가 어려워.** 하나씩 풀어보자.

> 🧒 **비유**:
> - MySQL INSERT: 책장에 새 책을 꽂을 때, **목차(인덱스)도 같이 업데이트**하고, **수정 이력 메모장(Undo Log)도 준비**해야 함
> - PostgreSQL INSERT: 새 책을 그냥 **서가 빈 자리에 꽂기만** 하면 됨. 목차는 나중에 업데이트

**단순 INSERT 성능 비교:**

| 요소 | MySQL/InnoDB | PostgreSQL |
|------|-------------|------------|
| **INSERT 시 해야 할 일** | 데이터 페이지에 쓰기 + Undo Log 준비 + redo log(WAL) | 데이터 페이지에 쓰기 + WAL |
| **클러스터드 인덱스** | ✅ InnoDB는 PK 순서로 데이터 저장 → PK 순서 INSERT 빠름, 랜덤 PK INSERT 느림 | ❌ 힙(heap) 테이블 → 빈 곳에 아무데나 넣음. PK 순서 무관 |
| **UPDATE의 본질** | in-place 수정 + Undo Log 체인 생성 | 새 튜플 INSERT + 이전 튜플에 xmax 표시 |

**실제로는:**
- **단순 대량 INSERT (벌크)**: 비슷하거나 MySQL이 약간 빠를 수 있음 (클러스터드 인덱스로 순차 쓰기 시)
- **UPDATE가 섞인 혼합 워크로드**: PostgreSQL의 UPDATE는 사실상 INSERT+DELETE이므로, UPDATE 자체는 I/O가 더 많지만 잠금 경합은 적음
- **동시 쓰기(concurrent writes)**: PostgreSQL이 유리할 수 있음. MySQL InnoDB는 Undo Log에 대한 잠금과 gap lock 등이 동시 쓰기를 제한

📌 **원래 표의 "MySQL = 단순 INSERT 빠름"은 주로 InnoDB의 클러스터드 인덱스가 순차 PK INSERT에 최적화되어 있다는 맥락**이고, PostgreSQL이 INSERT 자체가 느리다는 뜻은 아니야.

---

#### "복잡 트랜잭션에 강하다"는 어떤 의미인가?

**트랜잭션의 단순/복잡 구분:**

| 구분 | 단순 트랜잭션 | 복잡 트랜잭션 |
|------|-------------|-------------|
| **예시** | 단일 행 INSERT, 단일 행 UPDATE, 포인트 조회 | 여러 테이블 JOIN + 집계 + 서브쿼리 + CTE + 조건부 UPDATE |
| **특징** | 빠르게 시작-종료, 잠금 범위 좁음 | 오래 걸림, 여러 테이블/행에 걸쳐 잠금 |
| **비유** | 편의점에서 물 하나 사기 | 대형마트에서 장바구니 가득 채워서 한번에 결제하기 |

**PostgreSQL이 복잡 트랜잭션에 강한 이유:**

| 이유                                     | 설명                                                                                                                                                                |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. 쿼리 옵티마이저가 더 정교**                  | PostgreSQL의 옵티마이저는 CTE, Window Function, Lateral Join, Recursive Query 등 복잡한 쿼리 패턴에 대해 더 다양한 실행 계획을 고려함. MySQL 옵티마이저는 역사적으로 단순 쿼리에 최적화                            |
| **2. MVCC 잠금 모델**                      | PostgreSQL의 SSI(Serializable Snapshot Isolation)는 낙관적 — 읽기가 쓰기를 블로킹하지 않음. MySQL의 Serializable은 비관적(모든 SELECT가 LOCK IN SHARE MODE) → 복잡 트랜잭션에서 교착(deadlock) 가능성 높음 |
| **3. 풍부한 SQL 기능**                      | 복잡한 비즈니스 로직을 SQL 수준에서 처리 가능 (RETURNING 절, UPSERT, 배열 연산, JSON 연산 등) → 트랜잭션 내 라운드트립 감소                                                                             |
| **4. Partial Index, Expression Index** | 복잡한 조건의 쿼리도 인덱스로 최적화 가능 → 복잡 트랜잭션 내 쿼리 성능 향상                                                                                                                      |
| **5. DDL 트랜잭셔널**                       | PostgreSQL은 `CREATE TABLE`, `ALTER TABLE` 등 DDL도 트랜잭션 안에서 롤백 가능. MySQL은 DDL이 암묵적 COMMIT을 발생시킴                                                                     |

**구체적 예시:**

```sql
-- 복잡 트랜잭션 예시: 재고 이동 + 감사 로그 + 조건부 알림
BEGIN;

-- 1. CTE로 대상 선정
WITH low_stock AS (
    SELECT product_id, warehouse_id, quantity
    FROM inventory
    WHERE quantity < threshold
    FOR UPDATE  -- 행 잠금
)
-- 2. 다른 창고에서 재고 이동
, transfer AS (
    UPDATE inventory SET quantity = quantity - 10
    WHERE warehouse_id = 'A' AND product_id IN (SELECT product_id FROM low_stock)
    RETURNING product_id, 10 AS transferred  -- RETURNING: MySQL에 없음
)
-- 3. 대상 창고 재고 증가
INSERT INTO inventory (product_id, warehouse_id, quantity)
SELECT product_id, 'B', transferred FROM transfer
ON CONFLICT (product_id, warehouse_id) 
DO UPDATE SET quantity = inventory.quantity + EXCLUDED.quantity;

-- 4. 감사 로그 (같은 트랜잭션 안에서)
INSERT INTO audit_log (action, details)
SELECT 'TRANSFER', jsonb_build_object('product', product_id, 'qty', transferred)
FROM transfer;

COMMIT;
```

MySQL에서 이 쿼리를 하려면 여러 개의 개별 쿼리로 분리해야 하고, 중간에 애플리케이션 코드가 개입해야 하는 경우가 많아.

---

### Q6-6: 읽기 성능

> 🧒 **비유**: 
> - MySQL은 **도서관 사서가 책을 찾아주는 속도가 빠른 것** — 단순하게 "이 책 찾아줘"하면 정말 빠름
> - PostgreSQL은 **연구사서가 여러 책을 조합해서 분석해주는 것** — 복잡한 질문에 강함

#### 단순 읽기 (Point Query, 단일 행)

| 요소 | MySQL/InnoDB | PostgreSQL |
|------|-------------|------------|
| **클러스터드 인덱스** | ✅ PK 검색 시 B-Tree 타고 바로 데이터에 도달 (한 번의 인덱스 탐색) | ❌ 인덱스 → CTID(행 위치) → 힙 테이블에서 한 번 더 조회 (추가 I/O) |
| **버퍼 풀** | InnoDB Buffer Pool이 데이터+인덱스 캐싱에 매우 효율적 | shared_buffers + OS 페이지 캐시 이중 캐싱 (튜닝 필요) |
| **MVCC 오버헤드** | 최신 버전이 테이블에 있으므로 대부분 Undo Log 안 봐도 됨 | 여러 버전 중 가시성 판단 필요 (xmin/xmax 확인) |

**📌 결론: 단순 PK 조회는 MySQL이 유리**

MySQL의 클러스터드 인덱스가 핵심이야. PK로 검색하면 B-Tree 리프 노드에 데이터가 바로 있어서 추가 I/O 없이 읽을 수 있음. PostgreSQL은 인덱스에서 행의 물리적 위치(CTID)를 찾고, 다시 힙 테이블로 가서 데이터를 읽어야 함. (이걸 보완하기 위해 PostgreSQL은 **Index-Only Scan**과 **Visibility Map**을 제공하지만 추가 관리 비용이 있음)

#### 복잡 읽기 (JOIN, 집계, 서브쿼리)

| 요소 | MySQL | PostgreSQL |
|------|-------|------------|
| **JOIN 알고리즘** | MySQL 8.0+: Hash Join 추가 (이전엔 Nested Loop만) | Hash Join, Merge Join, Nested Loop 모두 지원 (오래전부터) |
| **병렬 쿼리** | ❌ 단일 쿼리는 단일 스레드 | ✅ Parallel Seq Scan, Parallel Hash Join 등 (9.6+) |
| **CTE 최적화** | MySQL 8.0+: CTE 지원, 최적화 제한적 | CTE 인라이닝, 재귀 CTE 최적화 |
| **Window Function** | MySQL 8.0+: 기본 지원 | 더 다양한 Window 함수 + 최적화 |
| **통계 정보** | 히스토그램 (MySQL 8.0+, 수동 생성) | 다변량 통계 (pg 10+), 자동 ANALYZE |

**📌 결론: 복잡한 읽기 쿼리는 PostgreSQL이 유리**

특히 **병렬 쿼리**의 차이가 큼. PostgreSQL은 하나의 쿼리를 여러 CPU 코어에 분배해서 처리할 수 있어서, 대용량 테이블 집계/분석에서 확연한 성능 차이가 남.

#### MVCC가 읽기에 미치는 영향

| 시나리오 | MySQL | PostgreSQL |
|----------|-------|------------|
| **최신 데이터 읽기** | ✅ 빠름 (테이블에 바로 있음) | 약간 느림 (가시성 확인 필요) |
| **오래된 스냅샷 읽기** | ⚠️ Undo Log 체인 따라가야 함 | ✅ 해당 버전 튜플이 테이블에 있으면 바로 읽음 |
| **bloat된 테이블** | 영향 없음 (테이블에 dead tuple 없음) | ⚠️ dead tuple이 많으면 Seq Scan 느려짐 |

#### 종합 비교

| 읽기 시나리오 | 유리한 DB | 이유 |
|-------------|----------|------|
| PK 단건 조회 | ✅ **MySQL** | 클러스터드 인덱스 → 한 번의 I/O |
| 세컨더리 인덱스 조회 | MySQL 약간 유리 | 커버링 인덱스 시 동등, 아니면 MySQL이 클러스터드 인덱스 참조 필요 |
| 대량 범위 스캔 | **PostgreSQL** | 병렬 쿼리 가능 |
| 복잡 JOIN/집계 | **PostgreSQL** | 다양한 Join 알고리즘 + 병렬 처리 + 정교한 옵티마이저 |
| 풀텍스트 검색 | **PostgreSQL** | GIN + tsvector (앞서 설명) |
| JSON 내부 검색 | **PostgreSQL** | JSONB + GIN 인덱스 |
| 단순 CRUD 대량 처리 | **MySQL** | 가벼운 오버헤드, 효율적 버퍼 풀 |

---

### 📌 전체 요약

| 관점 | MySQL | PostgreSQL |
|------|-------|------------|
| MVCC | Undo Log (테이블 깨끗, 관리 쉬움) | 다중 버전 튜플 (VACUUM 필요, 관리 어려움) |
| JSON | 기본적, 가상 컬럼 인덱싱 | JSONB + GIN = 강력한 문서 DB 수준 |
| 풀텍스트 | FULLTEXT 인덱스 (제한적) | tsvector + GIN (강력) |
| 확장성 | 스토리지 엔진 교체 가능 (그 외 제한적) | 타입/함수/연산자/인덱스 모두 확장 가능 |
| 쓰기 | 단순 순차 INSERT 빠름 | 복잡 트랜잭션 + 동시 쓰기에 강함 |
| 읽기 | 단순 PK 조회 빠름 (클러스터드 인덱스) | 복잡 쿼리 + 병렬 처리에 강함 |

💡 **면접 팁**: "MySQL vs PostgreSQL 어떤 게 좋냐"는 질문에 "PostgreSQL이 좋습니다"라고 답하면 안 돼. **워크로드에 따라 다르다**고 답하고, 구체적으로 어떤 워크로드에 어떤 DB가 유리한지 위 내용을 기반으로 설명하면 됨.


---



# 데이터베이스 인덱스, N+1 문제, JPA Loading 전략 종합 답변

---

## Q7. 데이터베이스 인덱스 전략

### Q7-1: MySQL vs PostgreSQL 인덱스 유형 비교

#### 📌 현실 비유: 도서관의 책 정리 시스템

도서관을 생각해보자.
- **Clustered Index** = 책이 실제로 꽂혀 있는 **물리적 순서** (가나다순으로 책꽂이에 배치)
- **Non-Clustered Index** = 도서관 입구의 **카드 목록함**. 카드에 "이 책은 3층 A구역 12번 칸에 있어요"라고 적혀있는 것

#### 인덱스 유형 비교 테이블

| 인덱스 유형 | MySQL | PostgreSQL | 비고 |
|---|---|---|---|
| **B-Tree** | ✅ (기본) | ✅ (기본) | 양쪽 모두 기본 인덱스 |
| **Hash** | ✅ | ✅ | 등호(=) 비교에 특화 |
| **Full-Text** | ✅ | ✅ | 텍스트 검색용 (구현 방식 다름) |
| **Spatial (R-Tree)** | ✅ | ✅ (GiST 기반) | 지리/공간 데이터 |
| **Clustered Index** | ✅ (InnoDB 필수) | ❌ 개념 다름 | 아래 상세 설명 |
| **Prefix Index** | ✅ | ❌ (expression index로 대체) | 문자열 앞부분만 인덱싱 |
| **Adaptive Hash Index** | ✅ (InnoDB 자동) | ❌ | InnoDB가 자동 생성 |
| **GiST** | ❌ | ✅ | 범용 검색 트리 |
| **GIN** | ❌ | ✅ | 역인덱스 (배열, JSONB, Full-Text) |
| **BRIN** | ❌ | ✅ | 블록 범위 인덱스 |
| **SP-GiST** | ❌ | ✅ | 비균형 파티션 트리 |
| **Partial Index** | ❌ | ✅ | 조건부 인덱스 |
| **Expression Index** | ❌ (generated column 우회) | ✅ | 함수/표현식 기반 인덱스 |
| **Covering Index (INCLUDE)** | ✅ (8.0+, InnoDB 자체 지원) | ✅ (11+, INCLUDE 구문) | 추가 컬럼 포함 |

#### ✅ Clustered Index란?

맞다. **MySQL InnoDB에서 PK는 자동으로 Clustered Index**가 된다.

**단계별 설명:**

**1단계: Clustered Index의 정의**
- 테이블의 데이터 행(row)이 **물리적으로 인덱스 키 순서대로 저장**되는 구조
- 테이블당 **단 하나만** 존재 가능 (물리적 순서는 하나뿐이니까)

**2단계: MySQL InnoDB의 동작**
```
[Clustered Index = PK 기준으로 데이터가 정렬 저장]

PK=1 → | id=1, name="Alice", age=25 |  ← 실제 데이터 행 전체
PK=2 → | id=2, name="Bob",   age=30 |
PK=3 → | id=3, name="Carol", age=28 |
```
- InnoDB에서 테이블 자체가 곧 Clustered Index (이것을 **IOT, Index-Organized Table**이라 부름)
- PK가 없으면? → UNIQUE NOT NULL 컬럼을 찾음 → 그것도 없으면? → InnoDB가 내부적으로 숨겨진 6바이트 row ID를 만들어 Clustered Index를 구성

**3단계: Secondary Index (보조 인덱스)와의 관계**
```
Secondary Index (name 컬럼)
"Alice" → PK=1  ← PK값을 포인터로 저장
"Bob"   → PK=2
"Carol" → PK=3

→ name으로 검색하면: Secondary Index에서 PK 찾고 → Clustered Index에서 실제 행 조회
→ 이 두 번의 조회를 "더블 룩업" 또는 "bookmark lookup"이라 부름
```

**4단계: 왜 PK를 auto_increment로 쓰라고 하는가?**
- Clustered Index는 데이터가 물리적으로 정렬되어 있으므로, PK가 랜덤(예: UUID)이면 **새 행 삽입 시 페이지 분할(page split)**이 빈번 → 성능 저하
- auto_increment면 항상 끝에 추가되므로 효율적

#### ⚠️ PostgreSQL에는 Clustered Index가 없나?

**정확한 답: "MySQL 같은 방식의 Clustered Index는 없다."**

PostgreSQL은 **Heap Table** 구조를 사용한다:
- 데이터 행은 삽입 순서대로 **아무 빈 공간에** 저장 (물리적 정렬 없음)
- 모든 인덱스가 **Secondary Index**처럼 동작: 인덱스 → TID(Tuple ID, 물리적 위치) → 실제 행

PostgreSQL에 `CLUSTER` 명령어가 있긴 하다:
```sql
CLUSTER table_name USING index_name;
```
하지만 이것은:
- **한 번만** 물리적으로 재정렬해주는 것 (일회성)
- 이후 INSERT/UPDATE하면 다시 무작위 위치에 저장됨
- InnoDB처럼 **자동으로 유지되지 않음**
- 테이블에 **EXCLUSIVE LOCK**이 걸려서 운영 중 사용이 어려움

💡 **그래서 PostgreSQL에서는:**
- Covering Index (`INCLUDE` 구문)로 더블 룩업 회피
- BRIN 인덱스로 물리적 순서와 상관관계 활용
- 이런 대안을 통해 Clustered Index 없이도 성능을 확보

---

### Q7-2: 각 인덱스 유형의 구현과 효과적 사용 케이스

#### 1. B-Tree Index (MySQL, PostgreSQL 공통 기본)

**🏠 비유: 백과사전의 "ㄱ-ㄴ-ㄷ" 목차 구조**

백과사전은 "ㄱ"을 펼치면 그 안에 "가-갸-거-겨..."로 나뉘고, "가" 안에서 "가격-가구-가방..."으로 더 세분화된다. B-Tree도 이런 계층적 분류와 같다.

**구현 원리:**
```
                    [50]                    ← Root (Level 0)
                  /      \
          [20, 35]        [70, 85]          ← Branch (Level 1)
         /   |   \       /   |   \
    [10,15][25,30][40,45][60,65][75,80][90,95]  ← Leaf (Level 2)
    
    Leaf 노드끼리 양방향 연결 리스트 (PostgreSQL)
    Leaf 노드끼리 단방향 연결 리스트 (MySQL InnoDB)
```

- **Balanced**: 루트에서 모든 Leaf까지 깊이가 동일 → 어떤 값을 찾든 동일한 시간
- 일반적으로 3~4 레벨이면 수백만~수천만 행 커버 가능 (한 노드에 수백 개 키)
- Leaf 노드가 연결되어 있으므로 **범위 검색**(BETWEEN, >, <)에 효율적

**효과적인 경우:**
- 등호(`=`), 범위(`>`, `<`, `BETWEEN`), 정렬(`ORDER BY`), `LIKE 'abc%'` (앞부분 일치)
- **대부분의 경우에 사용** — "뭘 쓸지 모르겠으면 B-Tree"

**비효과적인 경우:**
- `LIKE '%abc'` (앞에 와일드카드) → 인덱스 풀스캔
- 매우 낮은 카디널리티 (boolean 같은 것) → 풀스캔이 더 나을 수 있음

---

#### 2. Hash Index

**🏠 비유: 학교 사물함 번호**

학생 이름 "김철수" → 해시 함수 → 42번 사물함. 이름을 넣으면 바로 사물함 번호가 나오는 것. 중간이 없다. 42번이냐 아니냐만 있다.

**구현 원리:**
```
key "alice" → hash("alice") = 0x3A2B → bucket 42 → row pointer
key "bob"   → hash("bob")   = 0x7F1C → bucket 15 → row pointer
```

**MySQL에서의 상태:**
- InnoDB에서 명시적 Hash Index 생성은 지원하지만, 내부적으로 B-Tree로 처리됨
- 대신 **Adaptive Hash Index**가 있음: InnoDB가 자주 접근되는 B-Tree 페이지를 자동으로 해시 인덱스로 캐싱

**PostgreSQL에서의 상태:**
- PostgreSQL 10 이전에는 WAL(Write-Ahead Log) 미지원으로 크래시 시 손상 위험 → 사실상 사용 금지
- PostgreSQL 10 이후 WAL 지원으로 안전해짐, 하지만 여전히 B-Tree 대비 장점이 제한적

**효과적인 경우:**
- **정확한 등호 비교만** 할 때 (`WHERE session_id = 'abc123'`)
- 이론적으로 O(1) 접근

**❌ 절대 안 되는 경우:**
- 범위 검색, 정렬, 부분 일치 — 해시는 순서 개념이 없음

---

#### 3. GIN Index (PostgreSQL 전용)

**🏠 비유: 책 맨 뒤의 "찾아보기(색인)" 페이지**

책 뒤에 "인공지능: p.15, p.42, p.103" 이렇게 적혀있는 것. 하나의 키워드가 여러 페이지에 등장하는 것을 역으로 추적하는 구조.

**구현 원리:**
```
GIN = Generalized Inverted Index (일반화된 역인덱스)

원본 데이터:
  row1: tags = ['python', 'fastapi', 'async']
  row2: tags = ['python', 'django']
  row3: tags = ['java', 'spring']

GIN 인덱스 내부:
  'async'   → {row1}
  'django'  → {row2}
  'fastapi' → {row1}
  'java'    → {row3}
  'python'  → {row1, row2}
  'spring'  → {row3}
```

**효과적인 경우:**
- **JSONB 컬럼 검색**: `WHERE data @> '{"status": "active"}'`
- **배열 포함 검색**: `WHERE tags @> ARRAY['python']`
- **Full-Text Search**: `WHERE to_tsvector('english', content) @@ to_tsquery('database & index')`
- 하나의 행이 **여러 값을 가지는** 구조에 최적

**트레이드오프:**
- INSERT/UPDATE 시 인덱스 갱신 비용이 B-Tree보다 높음
- `GIN_PENDING_LIST_LIMIT`으로 fastupdate 조절 가능

---

#### 4. GiST Index (PostgreSQL 전용)

**🏠 비유: 지도에서 "이 근처 음식점" 찾기**

네이버 지도에서 "현재 위치 반경 1km 음식점"을 검색하면, 지도가 영역을 잘게 나눠서 빠르게 찾아준다.

**구현 원리:**
```
GiST = Generalized Search Tree

공간을 계층적으로 분할:
  전체 서울 → [강남구, 서초구, 송파구, ...]
    강남구 → [역삼동, 대치동, 삼성동, ...]
      역삼동 → [블록1, 블록2, ...]
        블록1 → 개별 좌표점들
```

**효과적인 경우:**
- **공간 데이터**: PostGIS와 함께 `ST_DWithin(geom, point, 1000)` (1km 이내)
- **범위 타입**: `WHERE daterange @> '2024-01-15'` (겹침, 포함 연산)
- **Full-Text Search**: GIN보다 빌드 빠르고 크기 작지만, 검색은 느림 (write가 많으면 GiST, read가 많으면 GIN)

---

#### 5. BRIN Index (PostgreSQL 전용)

**🏠 비유: 아파트 층별 안내판**

"1~3층: 상가, 4~10층: 사무실, 11~30층: 주거" 이런 안내판. 정확한 호수는 모르지만, "주거 공간을 찾으려면 11층 이상만 보면 돼"라고 범위를 빠르게 좁혀줌.

**구현 원리:**
```
BRIN = Block Range INdex

테이블의 물리적 블록을 그룹으로 묶어 요약 정보만 저장:

  Block 0~127:   created_at min=2024-01-01, max=2024-01-31
  Block 128~255: created_at min=2024-02-01, max=2024-02-28
  Block 256~383: created_at min=2024-03-01, max=2024-03-31
  
WHERE created_at = '2024-02-15' → Block 128~255만 스캔
```

**효과적인 경우:**
- **시계열 데이터**: 로그, 이벤트, 센서 데이터처럼 삽입 순서와 값의 순서가 상관관계가 높은 경우
- **매우 큰 테이블**: 인덱스 크기가 B-Tree의 1/100~1/1000 수준
- `pages_per_range` 파라미터로 정밀도 조절 가능

**⚠️ 주의:**
- 데이터가 물리적으로 정렬되어 있어야 효과적. 랜덤 삽입이면 모든 블록 범위가 겹쳐서 의미 없음
- PostgreSQL은 Clustered Index가 없으므로, 주기적으로 `CLUSTER` 또는 처음부터 시간순 삽입되는 데이터에 적합

---

#### 6. SP-GiST Index (PostgreSQL 전용)

**🏠 비유: 전화번호부 — 010으로 시작 → 010-1234 → 010-1234-5...**

접두사를 공유하는 데이터를 트리로 분할하는 구조. Trie, Quadtree, k-d tree 등의 자료구조를 일반화한 것.

**효과적인 경우:**
- IP 주소 범위 검색 (`inet` 타입)
- 전화번호, 우편번호처럼 계층적 구조의 문자열
- 2D 공간에서 GiST보다 나은 경우가 있음 (데이터 분포에 따라)

---

#### 7. Full-Text Index (구현 방식 차이)

| 측면 | MySQL | PostgreSQL |
|---|---|---|
| 엔진 | InnoDB 자체 구현 | `tsvector`/`tsquery` 타입 + GIN/GiST |
| 한국어 | 기본 미지원 (ngram parser 필요) | 기본 미지원 (외부 사전 필요) |
| 유연성 | 제한적 | 가중치, 랭킹, 사전 커스텀 가능 |
| 성능 | 소규모 텍스트에 적합 | 대규모 텍스트에 적합 |

---

#### 8. Partial Index (PostgreSQL 전용)

```sql
CREATE INDEX idx_active_users ON users (email) WHERE is_active = true;
```

**비유:** 전교생 명단에서 "현재 재학 중인 학생만" 따로 정리한 명단. 졸업생은 포함하지 않아서 목록이 훨씬 작고 빠름.

**효과적인 경우:**
- `is_deleted = false`인 행만 자주 검색할 때
- 특정 상태값을 가진 행이 전체의 소수일 때
- 인덱스 크기를 줄여 메모리 효율 증가

---

### Q7-3: 인덱스 설계 원칙

#### 카디널리티(Cardinality) 기반 인덱스 설계

**🏠 비유: 분류 기준의 "구별 능력"**

반 친구 30명을 찾을 때:
- "성별"로 분류 → 남/여 2그룹 → 한 그룹에 15명 → **구별 능력 낮음** (Low Cardinality)
- "이름"으로 분류 → 거의 30그룹 → 한 그룹에 1명 → **구별 능력 높음** (High Cardinality)
- "생년월일"로 분류 → 비슷한 친구가 있을 수 있지만 꽤 잘 구별됨 → **중간 Cardinality**

**원칙: 카디널리티가 높을수록 인덱스 효과가 크다.**

**단계별 설명:**

**1단계: 왜 높은 카디널리티가 좋은가?**
```
gender 인덱스로 WHERE gender = 'M' 검색:
→ 전체 100만 행 중 50만 행이 해당 → 인덱스가 50%를 걸러냄 → 별 효과 없음
→ 옵티마이저가 "차라리 Full Table Scan이 낫겠다"고 판단할 수 있음

email 인덱스로 WHERE email = 'alice@ex.com' 검색:
→ 전체 100만 행 중 1행이 해당 → 인덱스가 99.9999%를 걸러냄 → 매우 효과적
```

**2단계: 카디널리티 확인 방법**
```sql
-- MySQL
SHOW INDEX FROM users;  -- Cardinality 컬럼 확인

-- PostgreSQL
SELECT n_distinct FROM pg_stats WHERE tablename = 'users';
-- n_distinct > 0: 고유값 개수 추정
-- n_distinct < 0: 비율 (-0.5 = 전체의 50%가 고유)
```

**3단계: 복합 인덱스에서의 카디널리티**
```sql
-- 복합 인덱스에서는 카디널리티가 높은 컬럼을 앞에 배치
-- ❌ (gender, email) → gender='M'으로 먼저 50%를 걸러낸 후 email 검색
-- ✅ (email, gender) → email로 먼저 거의 1개로 좁힘

-- 단, 쿼리 패턴이 더 중요! (아래에서 설명)
```

**⚠️ 예외 상황:**
- Boolean 컬럼이라도 `WHERE is_deleted = false`를 거의 항상 검색한다면 → **PostgreSQL의 Partial Index**가 정답
- 낮은 카디널리티라도 다른 컬럼과 복합 인덱스로 묶으면 효과적일 수 있음

---

#### 복합 인덱스 순서: WHERE → ORDER BY → SELECT

**🏠 비유: 도서관에서 책 찾는 순서**

"파이썬 프로그래밍 책 중에서 최신순으로 정렬해서, 제목과 저자만 알고 싶어"

1. **WHERE** = "파이썬 프로그래밍 책 찾기" (조건 필터)
2. **ORDER BY** = "최신순 정렬" (정렬)
3. **SELECT** = "제목과 저자만" (필요한 정보)

이 순서가 복합 인덱스의 컬럼 순서와 일치해야 한다.

**단계별 설명:**

**1단계: 쿼리 예시**
```sql
SELECT name, email           -- 3️⃣ 가져올 컬럼
FROM users
WHERE status = 'active'      -- 1️⃣ 필터 조건
  AND department_id = 5      -- 1️⃣ 필터 조건
ORDER BY created_at DESC     -- 2️⃣ 정렬 조건
LIMIT 20;
```

**2단계: 이상적인 복합 인덱스**
```sql
CREATE INDEX idx_users_optimal 
ON users (status, department_id, created_at DESC, name, email);
--        ^^^^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^   ^^^^^^^^^^
--        WHERE 조건 (필터)      ORDER BY (정렬)   SELECT (커버링)
```

**3단계: 왜 이 순서인가?**

```
인덱스 B-Tree 구조:

Level 1: status = 'active' (필터 → 범위 축소)
  Level 2: department_id = 5 (추가 필터 → 더 축소)
    Level 3: created_at DESC 순서로 정렬되어 있음
             → 별도 정렬(filesort) 불필요! 
             → Leaf 노드에 name, email 포함
             → 테이블 접근(더블 룩업) 불필요!
```

만약 순서가 `(created_at, status, department_id)`라면?
```
Level 1: created_at = ??? → 범위 전체를 스캔해야 함
  → 그 중에서 status='active', department_id=5를 필터
  → 인덱스는 있지만 비효율적
```

**4단계: 등호(=) 조건은 앞에, 범위 조건은 뒤에**
```sql
-- 이 쿼리에서:
WHERE status = 'active'        -- 등호 (=)
  AND department_id = 5        -- 등호 (=)
  AND created_at > '2024-01-01' -- 범위 (>)

-- 최적 인덱스: (status, department_id, created_at)
-- 범위 조건 이후의 컬럼은 인덱스 검색에 활용 안 됨 (스캔만 가능)
```

#### ✅ MySQL과 PostgreSQL 공통인가?

**예, 공통 원칙이다.** B-Tree 인덱스의 구조적 특성에서 나오는 원칙이므로, B-Tree를 사용하는 모든 RDBMS에 적용된다.

다만 세부 차이:
| 측면 | MySQL (InnoDB) | PostgreSQL |
|---|---|---|
| 옵티마이저 | 비용 기반, 인덱스 힌트 가능 | 비용 기반, 더 정교한 통계 |
| DESC 인덱스 | 8.0+ 지원 | 오래전부터 지원 |
| Covering 활용 | Clustered Index에 모든 컬럼 → 이미 커버링 | INCLUDE로 명시 필요 |
| Index-Only Scan | "Using index" (EXPLAIN) | "Index Only Scan" (EXPLAIN) |

---

#### 💡 커버링 인덱스(Covering Index)란?

**🏠 비유: 카드 목록함에 이미 답이 적혀있는 경우**

도서관에서 "파이썬 책의 저자가 누구야?"라는 질문에:
- **일반 인덱스**: 카드 목록함에서 "파이썬 책은 3층 A구역 12번 칸" → 직접 가서 저자 확인 (2번 이동)
- **커버링 인덱스**: 카드 목록함에 이미 "파이썬 책, 저자: 홍길동"이라고 적혀있음 → 가지 않아도 됨 (1번만 조회)

**정의:** 쿼리가 필요로 하는 **모든 컬럼이 인덱스 안에 포함**되어 있어서, 테이블 본체에 접근할 필요가 없는 인덱스.

```sql
-- 쿼리
SELECT name, email FROM users WHERE status = 'active';

-- 인덱스에 (status, name, email)이 포함되어 있으면 → 커버링 인덱스
-- 테이블 접근(Random I/O) 없이 인덱스만으로 응답 가능
```

**PostgreSQL 11+의 INCLUDE 구문:**
```sql
CREATE INDEX idx_users_covering 
ON users (status) INCLUDE (name, email);
-- status는 검색/정렬에 사용, name/email은 조회만 (트리 구조에 포함 안 됨)
-- → 인덱스 크기를 줄이면서 커버링 효과
```

**INCLUDE vs 그냥 복합 인덱스 차이:**
```sql
-- 이것은: (status, name, email) 세 컬럼 모두 B-Tree 키
CREATE INDEX idx1 ON users (status, name, email);
-- → name, email로도 정렬/검색 가능하지만 인덱스가 더 큼

-- 이것은: status만 B-Tree 키, name/email은 Leaf에만 저장
CREATE INDEX idx2 ON users (status) INCLUDE (name, email);
-- → name, email로 정렬/검색 불가, 하지만 인덱스가 더 작고 유지비 낮음
```

---

## Q8. N+1 쿼리 문제 해결 방법

### Q8-1: SQLAlchemy에서 N+1 해결 방법 5가지

**🏠 비유: 학교에서 학생 30명의 성적표를 모으는 방법**

- **방법 A**: 교실에 가서 "1번 학생 성적표 줘" → 다시 가서 "2번 학생" → ... → 30번 반복 (N+1)
- **방법 B**: "1반 전체 학생 성적표 한꺼번에 줘" (한 번에 해결)

SQLAlchemy에서 사용 가능한 N+1 해결 방법:

| 방법 | SQLAlchemy 지원 | 설명 |
|---|---|---|
| **1. Eager Loading (joinedload)** | ✅ `joinedload()` | SQL JOIN으로 한 번에 로드 |
| **2. Subquery Loading** | ✅ `subqueryload()` | 서브쿼리로 연관 데이터 별도 로드 |
| **3. Select-In Loading** | ✅ `selectinload()` | `WHERE id IN (...)` 으로 로드 |
| **4. Batch Loading (Lazy)** | ✅ `lazy='selectin'` 또는 relationship 설정 | 배치 단위로 로드 |
| **5. DTO Projection** | ✅ `query(User.name, User.email)` 또는 `load_only()` | 필요한 컬럼만 조회 |

**각각의 SQLAlchemy 코드:**

```python
# 1. Joined Load (= JPA의 Fetch Join과 유사)
session.query(User).options(joinedload(User.orders)).all()
# → SELECT * FROM users LEFT JOIN orders ON ...

# 2. Subquery Load (= JPA의 @Fetch(SUBSELECT)과 유사)
session.query(User).options(subqueryload(User.orders)).all()
# → SELECT * FROM users;
# → SELECT * FROM orders WHERE user_id IN (SELECT id FROM users);

# 3. Select-In Load (SQLAlchemy 1.2+, 가장 권장)
session.query(User).options(selectinload(User.orders)).all()
# → SELECT * FROM users;
# → SELECT * FROM orders WHERE user_id IN (1, 2, 3, ...);

# 4. Batch 크기 조절 (relationship 레벨)
class User(Base):
    orders = relationship("Order", lazy="selectin")
    # 또는 lazy="subquery"

# 5. 필요한 컬럼만 (Projection)
session.query(User.id, User.name).join(User.orders).all()
# → 연관 엔티티 자체를 로드하지 않음 → N+1 발생하지 않음
```

💡 **SQLAlchemy에서 가장 권장되는 방법은 `selectinload()`이다.** `joinedload()`는 카테시안 곱 문제가 있을 수 있고, `subqueryload()`는 서브쿼리가 복잡해질 수 있다. `selectinload()`는 깔끔한 `IN` 절로 해결한다.

---

### Q8-2: Fetch Join에서 페이징은 정말 불가능한가?

**짧은 답: "불가능한 것이 아니라, 위험하다."**

**🏠 비유로 이해하기:**

책방에서 "저자별로 책 목록"을 만들 때:
- 저자 A: 책 3권
- 저자 B: 책 2권
- 저자 C: 책 4권

JOIN 결과는 이렇게 된다:
```
row 1: 저자A - 책1
row 2: 저자A - 책2    ← 저자A인데 3행
row 3: 저자A - 책3
row 4: 저자B - 책1
row 5: 저자B - 책2    ← 저자B인데 2행
row 6: 저자C - 책1
...
row 9: 저자C - 책4
```

여기서 `LIMIT 3 OFFSET 0`을 걸면?
→ row 1~3 = 저자A의 책 3개만 나옴
→ **저자 단위로 "3명의 저자"를 원했는데, 실제로는 1명만 나옴!**

**JPA/Hibernate에서 이것이 문제인 이유:**

```java
// 이 코드를 실행하면:
@Query("SELECT u FROM User u JOIN FETCH u.orders")
Page<User> findAll(Pageable pageable);
```

Hibernate가 하는 일:
1. SQL에 LIMIT/OFFSET을 **붙이지 않음**
2. 전체 데이터를 **메모리로 다 가져옴**
3. **Java 메모리 안에서** 페이징 처리
4. 로그에 경고: `HHH000104: firstResult/maxResults specified with collection fetch; applying in memory!`

→ 100만 건이면 100만 건이 메모리에 올라옴 → **OOM(Out Of Memory) 위험**

**해결 방법들:**

**방법 1: 2단계 쿼리 (가장 안전)**
```sql
-- 1단계: ID만 페이징해서 가져옴
SELECT u.id FROM users u WHERE ... ORDER BY u.created_at LIMIT 20 OFFSET 40;

-- 2단계: 해당 ID들에 대해 Fetch Join
SELECT u FROM User u JOIN FETCH u.orders WHERE u.id IN (:ids)
```

**방법 2: @BatchSize + Lazy Loading**
```java
// 페이징은 User 엔티티만 대상
// 연관 데이터는 BatchSize만큼 IN 절로 로드
@BatchSize(size = 100)
@OneToMany(mappedBy = "user")
private List<Order> orders;
```

**방법 3: 질문의 "offset 쿼리"에 대해**
직접 네이티브 SQL로 `OFFSET`을 적용할 수는 있지만, 위에서 설명한 것처럼 JOIN된 결과의 행 수가 원래 엔티티 수와 다르기 때문에 의도한 페이징이 되지 않는다. **부모 엔티티 기준이 아닌 JOIN 결과 행 기준으로 잘리기 때문이다.**

---

### Q8-3: EntityGraph 방식이란?

**🏠 비유: 쇼핑 목록에 "이것도 같이 가져와"라고 체크 표시하기**

마트에 갈 때 쇼핑 목록을 만든다. 기본적으로 "우유"만 사려고 했는데, 목록에 "시리얼도 같이(체크)" 표시하면 한 번에 가져온다.

EntityGraph는 **"이 엔티티를 조회할 때 어떤 연관 엔티티를 함께 로드할지"를 선언적으로 지정**하는 JPA 2.1 표준 기능이다.

```java
// 방법 1: 어노테이션으로 정의
@Entity
@NamedEntityGraph(
    name = "User.withOrders",
    attributeNodes = @NamedAttributeNode("orders")  // orders도 같이 가져와
)
public class User {
    @OneToMany(mappedBy = "user")
    private List<Order> orders;  // 기본은 LAZY
}

// Repository에서 사용
@EntityGraph(value = "User.withOrders", type = EntityGraphType.LOAD)
List<User> findAll();

// 방법 2: 동적으로 정의 (어노테이션 없이)
@EntityGraph(attributePaths = {"orders", "orders.orderItems"})
List<User> findByStatus(String status);
```

**Fetch Join과의 비교:**

| 측면 | Fetch Join | EntityGraph |
|---|---|---|
| 정의 위치 | JPQL 쿼리 안 | 어노테이션 또는 별도 정의 |
| 재사용성 | 쿼리마다 작성 | 한 번 정의, 여러 곳 재사용 |
| JOIN 타입 | INNER JOIN (기본) | LEFT JOIN (기본) |
| 유연성 | 쿼리마다 다르게 가능 | 같은 그래프를 여러 쿼리에 적용 |
| 페이징 문제 | 동일하게 발생 | **동일하게 발생** |
| 표준 | JPQL 문법 | JPA 2.1 표준 |

**💡 핵심:** EntityGraph도 내부적으로 LEFT JOIN을 생성하므로, Fetch Join과 본질적으로 같은 메커니즘이다. 차이는 **선언 방식**이다. EntityGraph는 "무엇을 로드할지"를 쿼리와 분리해서 선언적으로 관리한다는 것이 장점.

---

### Q8-4: Batch Fetch Size와 Fetch Join의 관계

**결론부터: Batch Fetch Size는 Fetch Join과 함께 사용하는 것이 아니다. 별개의 전략이다.**

**🏠 비유:**

- **Fetch Join** = "한 트럭에 전부 싣고 한 번에 배달" (JOIN으로 한 쿼리)
- **Batch Fetch Size** = "택배를 100개씩 묶어서 여러 번 배달" (여러 쿼리지만, 1개씩이 아닌 배치 단위)

**동작 방식:**

```java
// application.yml
spring:
  jpa:
    properties:
      hibernate:
        default_batch_fetch_size: 100

// 또는 엔티티에 직접
@BatchSize(size = 100)
@OneToMany(mappedBy = "user")
private List<Order> orders;
```

```
설정: batch_fetch_size = 100
User 300명 조회 시:

Fetch Join 없이 Lazy Loading + BatchSize:
  쿼리 1: SELECT * FROM users;                              -- User 300명
  쿼리 2: SELECT * FROM orders WHERE user_id IN (1,2,...,100);   -- 1~100번 User의 주문
  쿼리 3: SELECT * FROM orders WHERE user_id IN (101,...,200);   -- 101~200번
  쿼리 4: SELECT * FROM orders WHERE user_id IN (201,...,300);   -- 201~300번
  
  총 4개 쿼리 (1 + 300/100 = 4)

BatchSize 없이 Lazy Loading:
  쿼리 1: SELECT * FROM users;
  쿼리 2: SELECT * FROM orders WHERE user_id = 1;
  쿼리 3: SELECT * FROM orders WHERE user_id = 2;
  ...
  쿼리 301: SELECT * FROM orders WHERE user_id = 300;
  
  총 301개 쿼리 (1 + 300 = 301) ← 이것이 N+1
```

**핵심:** BatchSize는 **Lazy Loading이 발생할 때**, 1개씩 가져오는 대신 지정된 크기만큼 묶어서 `IN` 절로 가져온다. Fetch Join을 사용하면 BatchSize는 무시된다 (이미 JOIN으로 다 가져왔으므로).

---

### Q8-5: DTO Projection이 어떻게 N+1을 해결하는가?

**좋은 지적이다. DTO Projection 자체가 N+1을 "해결"하는 것은 아니다.** 정확히 말하면 **N+1이 발생할 수 있는 구조를 아예 회피**하는 것이다.

**🏠 비유:**

N+1 문제는 "연관된 물건"을 따로따로 가지러 가는 문제이다.
- **엔티티 조회**: "사람 객체"를 가져오면, 그 사람의 "주문 목록" "배송 주소" 등 연관 객체가 딸려 있음 → 접근 시 추가 쿼리
- **DTO Projection**: "이름, 이메일, 주문 개수"만 **딱 필요한 값만** 가져옴 → 연관 엔티티 자체를 로드하지 않음 → Lazy Loading 트리거 자체가 없음

**단계별 설명:**

```java
// ❌ 엔티티 조회 → N+1 위험
List<User> users = userRepository.findAll();
for (User u : users) {
    System.out.println(u.getOrders().size());  // 여기서 Lazy Loading 발생!
}

// ✅ DTO Projection → N+1 불가능
@Query("SELECT new com.example.UserDTO(u.name, u.email, COUNT(o)) " +
       "FROM User u LEFT JOIN u.orders o GROUP BY u.name, u.email")
List<UserDTO> findUserSummaries();
// → 단일 쿼리, 엔티티가 아닌 순수 데이터 → Persistence Context에 들어가지 않음
// → Lazy Loading 자체가 불가능 → N+1 불가능
```

**그래서 네 말이 맞다:** SELECT를 간소화하는 것이 맞다. 그런데 그 간소화의 결과로, **연관 엔티티를 아예 로드하지 않게 되어** N+1이 구조적으로 발생하지 않는 것이다. "해결"이라기보다 **"회피"**가 정확한 표현이다.

---

### Q8-6: @Fetch(SUBSELECT)란? Fetch Join과 무엇이 다른가?

**🏠 비유:**

- **Fetch Join** = "학생 명단과 각 학생의 시험 점수를 하나의 큰 표(JOIN)로 합쳐서 가져오기"
- **@Fetch(SUBSELECT)** = "학생 명단을 먼저 가져오고, 그 다음에 '이 학생들 전원의 시험 점수'를 한 번에 가져오기"

**동작 방식:**

```java
@Entity
public class User {
    @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
    @Fetch(FetchMode.SUBSELECT)  // Hibernate 전용 (JPA 표준 아님)
    private List<Order> orders;
}
```

```sql
-- 1번째 쿼리: User 조회
SELECT * FROM users WHERE department_id = 5;

-- 2번째 쿼리: 위 쿼리의 결과에 해당하는 모든 orders를 서브쿼리로 한 번에
SELECT * FROM orders 
WHERE user_id IN (
    SELECT id FROM users WHERE department_id = 5  -- 원래 쿼리가 서브쿼리로 들어감
);
```

**Fetch Join vs SUBSELECT vs BatchSize 비교:**

| 측면 | Fetch Join | @Fetch(SUBSELECT) | @BatchSize |
|---|---|---|---|
| 쿼리 수 | **1개** | **2개** | **1 + N/size** |
| JOIN 발생 | ✅ (카테시안 곱 위험) | ❌ | ❌ |
| 페이징 문제 | ✅ 있음 | ❌ 없음 | ❌ 없음 |
| 메모리 | JOIN 결과가 커질 수 있음 | 적절 | 적절 |
| 설정 위치 | JPQL에서 명시 | 엔티티 어노테이션 | 엔티티/전역 설정 |
| 표준 | JPA 표준 | Hibernate 전용 | Hibernate 전용 |
| 연관 컬렉션 여러 개 | 1개만 가능 | 여러 개 가능 | 여러 개 가능 |

**질문의 핵심에 대해: "서브쿼리가 SELECT 절에 있으면 문제 아닌가?"**

정확한 지적이다. 만약 이런 쿼리라면:
```sql
-- ❌ 이건 N+1과 같은 문제 (Correlated Subquery)
SELECT u.*, 
    (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) as order_count
FROM users u;
-- → users 행마다 서브쿼리 실행 가능
```

하지만 @Fetch(SUBSELECT)는 이렇게 동작하지 않는다:
```sql
-- ✅ 이건 독립적인 서브쿼리 (Non-correlated → 한 번만 실행)
SELECT * FROM orders 
WHERE user_id IN (SELECT id FROM users WHERE department_id = 5);
-- → 서브쿼리는 한 번 실행되고, 그 결과로 IN 절을 만들어 orders를 한 번에 가져옴
```

**핵심 차이:** SUBSELECT는 WHERE ... IN (서브쿼리) 형태로 **FROM/WHERE 절에서** 사용되며, 각 행마다 반복 실행되는 Correlated Subquery가 아니다. 원래 쿼리를 통째로 서브쿼리로 넣어서, 연관 데이터를 **한 방에** 가져오는 것이다.

---

## Q9. JPA에서 Lazy Loading과 Eager Loading

### Q9-1: Lazy Loading이 N+1의 원인이 맞는가?

**✅ 맞다. 정확한 이해다.**

**단계별로 왜 그런지 설명:**

**1단계: Lazy Loading의 동작**
```java
List<User> users = userRepository.findAll();
// → SELECT * FROM users;  (1개 쿼리)
// 이 시점에서 user.orders는 "프록시 객체" (빈 껍데기)
```

**2단계: N+1 발생**
```java
for (User user : users) {  // users가 100명이라면
    user.getOrders().size(); // ← 여기서 프록시가 초기화됨
    // → SELECT * FROM orders WHERE user_id = 1;
    // → SELECT * FROM orders WHERE user_id = 2;
    // → ...100번 반복
}
// 총 쿼리: 1 (User 조회) + 100 (각 User의 Orders) = 101개 → N+1
```

**3단계: 그래서 Fetch Join으로 해결**
```java
@Query("SELECT u FROM User u JOIN FETCH u.orders")
List<User> findAllWithOrders();
// → SELECT u.*, o.* FROM users u INNER JOIN orders o ON u.id = o.user_id;
// → 1개 쿼리로 끝
```

**💡 정리:**
```
Lazy Loading 자체는 "나쁜 것"이 아님
  → 연관 데이터를 안 쓰면 로드 안 해서 효율적

문제는 "Lazy Loading + 반복 접근" 조합
  → N+1 발생
  
해결: 미리 알고 있으면 Fetch Join / Batch Size / SUBSELECT 등으로 한 번에 가져옴
```

그런데 **Eager Loading이 답이냐?** → ❌ 아니다.
```
Eager Loading을 기본값으로 쓰면:
  → 안 쓰는 연관 데이터도 무조건 로드
  → 연관의 연관의 연관까지 줄줄이 로드될 수 있음
  → 성능 대참사
  
업계 표준: "모든 연관관계는 LAZY로, 필요할 때 Fetch Join"
```

---

### Q9-2: OneToMany, ManyToMany, OneToOne 실제 예시

**쏘카인드 교육 도메인**을 사용하여 설명.

#### 도메인 모델

```
Company (회사: 쏘카인드)
   │
   ├── 1:N ── User (사용자: 직원들)
   │            │
   │            ├── N:M ── EducationSession (교육 세션)
   │            │            │
   │            │            └── 1:1 ── AIReport (AI 리포트)
   │            │
   │            └── 1:1 ── UserProfile (사용자 프로필)
   │
   └── 1:N ── EducationSession (교육 세션은 회사에 소속)
```

---

#### 📌 @OneToMany: 회사 → 사용자들

**테이블 구조:**
```
companies                    users
+----+-----------+          +----+--------+------------+
| id | name      |          | id | name   | company_id |  ← FK
+----+-----------+          +----+--------+------------+
| 1  | 쏘카인드  |          | 1  | 김철수 | 1          |
+----+-----------+          | 2  | 이영희 | 1          |
                            | 3  | 박민수 | 1          |
                            +----+--------+------------+
```

**JPA 엔티티:**
```java
@Entity
public class Company {
    @Id @GeneratedValue
    private Long id;
    private String name;
    
    @OneToMany(mappedBy = "company", fetch = FetchType.LAZY)  // 기본값이 LAZY
    private List<User> users;
}

@Entity
public class User {
    @Id @GeneratedValue
    private Long id;
    private String name;
    
    @ManyToOne(fetch = FetchType.LAZY)  // 주의: ManyToOne 기본값은 EAGER!
    @JoinColumn(name = "company_id")
    private Company company;
}
```

**N+1 발생 시나리오:**
```java
// "모든 회사와 각 회사의 직원 수를 조회"
List<Company> companies = companyRepository.findAll();
// → SELECT * FROM companies;  (1쿼리)

for (Company c : companies) {
    System.out.println(c.getName() + ": " + c.getUsers().size());
    // → SELECT * FROM users WHERE company_id = 1;  (회사마다 1쿼리)
    // → SELECT * FROM users WHERE company_id = 2;
    // → ...
}
```

---

#### 📌 @ManyToMany: 사용자 ↔ 교육 세션

**비유:** 학교 수강신청. 한 학생이 여러 수업을 듣고, 한 수업에 여러 학생이 있음.

**테이블 구조:**
```
users                  user_sessions (중간 테이블)       education_sessions
+----+--------+       +---------+------------+         +----+----------------+
| id | name   |       | user_id | session_id |         | id | title          |
+----+--------+       +---------+------------+         +----+----------------+
| 1  | 김철수 |       | 1       | 1          |         | 1  | AI 기초        |
| 2  | 이영희 |       | 1       | 2          |         | 2  | Python 심화    |
| 3  | 박민수 |       | 2       | 1          |         | 3  | 리더십 교육    |
+----+--------+       | 2       | 3          |         +----+----------------+
                      | 3       | 1          |
                      | 3       | 2          |
                      | 3       | 3          |
                      +---------+------------+
```

김철수: AI 기초, Python 심화 수강
이영희: AI 기초, 리더십 교육 수강
박민수: 전부 수강

**JPA 엔티티:**
```java
@Entity
public class User {
    @ManyToMany(fetch = FetchType.LAZY)  // 기본값이 LAZY
    @JoinTable(
        name = "user_sessions",
        joinColumns = @JoinColumn(name = "user_id"),
        inverseJoinColumns = @JoinColumn(name = "session_id")
    )
    private List<EducationSession> sessions;
}

@Entity
public class EducationSession {
    @ManyToMany(mappedBy = "sessions", fetch = FetchType.LAZY)
    private List<User> participants;
}
```

**N+1 발생 시나리오:**
```java
// "각 교육 세션에 참여한 사람 목록"
List<EducationSession> sessions = sessionRepository.findAll();
// → SELECT * FROM education_sessions;  (1쿼리)

for (EducationSession s : sessions) {
    System.out.println(s.getTitle() + ": " + s.getParticipants().size());
    // → SELECT u.* FROM users u 
    //   JOIN user_sessions us ON u.id = us.user_id 
    //   WHERE us.session_id = 1;   (세션마다 1쿼리)
}
```

**⚠️ ManyToMany 추가 주의사항:**
- 중간 테이블(`user_sessions`)에 추가 컬럼(수강일, 점수 등)이 필요하면 → ManyToMany 사용 불가 → **별도 엔티티로 분리해야 함** (`UserSession` 엔티티)
- 실무에서는 거의 대부분 별도 엔티티로 분리한다

---

#### 📌 @OneToOne: 교육 세션 → AI 리포트

**비유:** 한 세션이 끝나면 AI가 리포트를 **딱 하나** 생성. 세션과 리포트는 1:1 관계.

**테이블 구조:**
```
education_sessions              ai_reports
+----+----------------+        +----+------------+--------+-------+
| id | title          |        | id | session_id | score  | summary |
+----+----------------+        +----+------------+--------+-------+
| 1  | AI 기초        |        | 1  | 1          | 85.5   | "참여도 높음" |
| 2  | Python 심화    |        | 2  | 2          | 72.0   | "실습 필요" |
| 3  | 리더십 교육    |        +----+------------+--------+-------+
+----+----------------+        (세션 3은 아직 리포트 없음)
```

**JPA 엔티티:**
```java
@Entity
public class EducationSession {
    @Id @GeneratedValue
    private Long id;
    private String title;
    
    @OneToOne(mappedBy = "session", fetch = FetchType.LAZY)
    private AIReport aiReport;
}

@Entity
public class AIReport {
    @Id @GeneratedValue
    private Long id;
    private Double score;
    private String summary;
    
    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id")
    private EducationSession session;
}
```

**⚠️ OneToOne의 특수한 N+1 문제:**

```java
List<EducationSession> sessions = sessionRepository.findAll();
// → SELECT * FROM education_sessions;

// 여기서 문제: OneToOne의 "mappedBy 쪽"(FK가 없는 쪽)은 
// LAZY가 제대로 동작하지 않을 수 있음!
```

**왜?** FK가 없는 쪽(EducationSession)은 aiReport가 null인지 아닌지를 모른다.
- 프록시 객체를 만들려면 "존재 여부"라도 알아야 함
- null이면 프록시가 아닌 null을 넣어야 함
- **결국 확인하려고 쿼리를 날림** → LAZY인데도 EAGER처럼 동작

**해결 방법:**
1. FK가 있는 쪽(AIReport)에서 Session을 참조하도록 방향 변경
2. `@LazyToOne(LazyToOneOption.NO_PROXY)` + 바이트코드 향상(bytecode enhancement)
3. `optional = false`로 설정 (null 불가능하다고 보장하면 프록시 생성 가능)
4. `@MapsId`를 사용하여 PK를 공유

---

#### 📌 전체 Loading 기본값 정리

| 관계 | 기본 FetchType | N+1 위험도 | 이유 |
|---|---|---|---|
| `@OneToMany` | **LAZY** ✅ | 높음 (반복 접근 시) | 컬렉션이므로 지연 로드가 기본 |
| `@ManyToMany` | **LAZY** ✅ | 높음 (반복 접근 시) | 컬렉션이므로 지연 로드가 기본 |
| `@ManyToOne` | **EAGER** ⚠️ | 중간 | 단일 객체라 JPA가 즉시 로드함 → **LAZY로 변경 권장** |
| `@OneToOne` | **EAGER** ⚠️ | 높음 | 위에서 설명한 프록시 문제 + 기본 EAGER |

💡 **실무 원칙:** 모든 연관관계를 `FetchType.LAZY`로 설정하고, 필요한 곳에서만 Fetch Join / EntityGraph / BatchSize로 즉시 로드하라. 특히 `@ManyToOne`의 기본값이 EAGER인 것을 항상 LAZY로 바꿔야 한다.

---

### 전체 요약 테이블

| 문제/개념 | 핵심 한 줄 |
|---|---|
| Clustered Index | 데이터가 PK 순서로 물리 저장 (MySQL InnoDB), PostgreSQL은 Heap Table |
| 카디널리티 | 높을수록 인덱스 효과 큼 (고유값이 많은 컬럼) |
| 커버링 인덱스 | 인덱스만으로 쿼리 응답, 테이블 접근 불필요 |
| N+1 문제 | Lazy Loading + 반복 접근 = 쿼리 폭발 |
| Fetch Join | JOIN으로 한 방 쿼리, 단 페이징과 다중 컬렉션에 주의 |
| BatchSize | Lazy + IN 절로 배치 로드 (페이징 가능) |
| EntityGraph | 선언적으로 "함께 로드할 것" 지정 (내부는 LEFT JOIN) |
| DTO Projection | 엔티티 안 쓰면 N+1 구조 자체를 회피 |
| @Fetch(SUBSELECT) | 원래 쿼리를 서브쿼리로 넣어 연관 데이터 한 번에 로드 |
| OneToOne LAZY 함정 | FK 없는 쪽은 LAZY가 안 될 수 있음 |


---



# Spring Boot 면접 준비 - 심화 답변

---

## Q10. 쿼리 최적화를 위해 EXPLAIN ANALYZE

### Q10-1: MySQL과 PostgreSQL 분리 설명

**현실 비유**: EXPLAIN은 "내비게이션의 경로 미리보기"야. 실제로 운전하기 전에 "이 길로 갈 거야"라고 보여주는 거지. EXPLAIN ANALYZE는 "실제로 운전해보고 걸린 시간까지 알려주는 것"이야.

#### MySQL의 EXPLAIN

MySQL에서는 EXPLAIN과 EXPLAIN ANALYZE가 **별개의 기능**이야.

**Step 1: EXPLAIN (예측만)**
```sql
EXPLAIN SELECT * FROM users WHERE age > 25;
```
- 쿼리를 **실행하지 않고** 실행 계획만 보여줌
- 테이블 형태로 출력됨 (id, select_type, table, type, possible_keys, key, rows, Extra 등)

**Step 2: EXPLAIN ANALYZE (실제 실행)**
```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE age > 25;
```
- MySQL 8.0.18부터 지원
- 쿼리를 **실제로 실행**하고, 예측값 vs 실제값을 비교
- 트리 형태로 출력됨

⚠️ **주의**: EXPLAIN ANALYZE는 실제로 쿼리를 실행하므로, DELETE/UPDATE에 쓰면 **실제로 데이터가 변경됨!**

#### PostgreSQL의 EXPLAIN

PostgreSQL은 옵션을 조합해서 사용해.

**Step 1: EXPLAIN (예측만)**
```sql
EXPLAIN SELECT * FROM users WHERE age > 25;
```
- 트리 형태로 실행 계획 출력
- 예상 cost, rows 표시

**Step 2: EXPLAIN ANALYZE (실제 실행)**
```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE age > 25;
```
- 실제 실행 후 actual time, actual rows 추가 표시

**Step 3: 추가 옵션 조합**
```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) SELECT * FROM users WHERE age > 25;
```
- `BUFFERS`: 디스크 I/O 정보
- `FORMAT JSON/YAML/TEXT`: 출력 포맷 지정
- `VERBOSE`: 더 자세한 정보
- `COSTS`: cost 표시 on/off
- `TIMING`: 시간 측정 on/off

---

### Q10-2: 구문 차이, 출력 차이, 해석 방법 차이

#### 📌 구문 차이 비교

| 항목 | MySQL | PostgreSQL |
|------|-------|------------|
| 기본 EXPLAIN | `EXPLAIN SELECT ...` | `EXPLAIN SELECT ...` |
| 실행 분석 | `EXPLAIN ANALYZE SELECT ...` (8.0.18+) | `EXPLAIN ANALYZE SELECT ...` |
| 포맷 지정 | `EXPLAIN FORMAT=JSON SELECT ...` | `EXPLAIN (FORMAT JSON) SELECT ...` |
| 버퍼 정보 | ❌ 없음 | `EXPLAIN (BUFFERS) SELECT ...` |
| 옵션 조합 | 제한적 | 괄호 안에 자유롭게 조합 |

#### 📌 출력 차이 비교

**MySQL EXPLAIN 출력 (테이블 형태)**:
```
+----+-------------+-------+------+---------------+------+---------+------+------+-------------+
| id | select_type | table | type | possible_keys | key  | key_len | ref  | rows | Extra       |
+----+-------------+-------+------+---------------+------+---------+------+------+-------------+
|  1 | SIMPLE      | users | ALL  | NULL          | NULL | NULL    | NULL | 1000 | Using where |
+----+-------------+-------+------+---------------+------+---------+------+------+-------------+
```

핵심 컬럼들:
- **type**: 접근 방식. `ALL`(풀스캔, 최악) → `index` → `range` → `ref` → `eq_ref` → `const`(최고)
- **key**: 실제 사용된 인덱스
- **rows**: 스캔할 예상 행 수
- **Extra**: `Using index`(커버링 인덱스 ✅), `Using filesort`(정렬 필요 ⚠️), `Using temporary`(임시 테이블 ⚠️)

**MySQL EXPLAIN ANALYZE 출력 (트리 형태)**:
```
-> Filter: (users.age > 25)  (cost=100.25 rows=333)
   (actual time=0.045..1.234 rows=450 loops=1)
    -> Table scan on users  (cost=100.25 rows=1000)
       (actual time=0.033..0.987 rows=1000 loops=1)
```

**PostgreSQL EXPLAIN 출력 (트리 형태)**:
```
Seq Scan on users  (cost=0.00..17.50 rows=333 width=44)
  Filter: (age > 25)
```

**PostgreSQL EXPLAIN ANALYZE 출력**:
```
Seq Scan on users  (cost=0.00..17.50 rows=333 width=44)
                   (actual time=0.015..0.234 rows=450 loops=1)
  Filter: (age > 25)
  Rows Removed by Filter: 550
Planning Time: 0.085 ms
Execution Time: 0.312 ms
```

#### 📌 해석 방법 차이

| 해석 포인트 | MySQL | PostgreSQL |
|------------|-------|------------|
| 풀스캔 감지 | type = `ALL` | `Seq Scan` |
| 인덱스 스캔 | type = `range`, `ref` 등 | `Index Scan`, `Index Only Scan` |
| 예상 vs 실제 비교 | rows vs actual rows | rows vs actual rows |
| 비용 단위 | cost (상대적 단위) | cost (시퀀셜 I/O 기준, `seq_page_cost=1.0`) |
| 정렬 비용 | Extra: `Using filesort` | `Sort` 노드 |
| 조인 방식 | type 컬럼에서 확인 | `Nested Loop`, `Hash Join`, `Merge Join` 노드 |

💡 **해석 팁**:
1. **rows 예측이 실제와 크게 다르면** → 통계가 오래됨 → `ANALYZE 테이블명` 실행 (MySQL), `ANALYZE` (PostgreSQL)
2. **cost가 높은 노드**를 찾아서 그 부분을 최적화
3. MySQL은 **type 컬럼을 먼저** 확인, PostgreSQL은 **최상위 노드의 cost**를 먼저 확인

---

## Q11. 대용량 테이블에서 페이징 성능 개선

### Q11-1: 페이징 전략 실제 구현 코드 (Spring Boot/JPA)

#### 방법 1: Offset 기반 (기본, 간단하지만 느림)

```java
// Controller
@GetMapping("/posts")
public Page<PostDto> getPosts(
    @RequestParam(defaultValue = "0") int page,
    @RequestParam(defaultValue = "20") int size
) {
    Pageable pageable = PageRequest.of(page, size, Sort.by("id").descending());
    return postService.getPosts(pageable);
}

// Repository
public interface PostRepository extends JpaRepository<Post, Long> {
    // Spring Data JPA가 자동으로 OFFSET/LIMIT 쿼리 생성
    Page<Post> findAll(Pageable pageable);
}
```

생성되는 SQL:
```sql
SELECT * FROM posts ORDER BY id DESC LIMIT 20 OFFSET 1000000;
-- + COUNT 쿼리도 추가로 실행됨 (총 개수 파악용)
```

#### 방법 2: Cursor(Keyset) 기반 (빠름, 무한 스크롤에 적합)

```java
// Controller
@GetMapping("/posts")
public List<PostDto> getPosts(
    @RequestParam(required = false) Long lastId,
    @RequestParam(defaultValue = "20") int size
) {
    return postService.getPostsAfter(lastId, size);
}

// Repository
public interface PostRepository extends JpaRepository<Post, Long> {
    
    // 첫 페이지 (lastId가 null일 때)
    List<Post> findTopByOrderByIdDesc(Pageable pageable);
    
    // 다음 페이지 (lastId 기준)
    @Query("SELECT p FROM Post p WHERE p.id < :lastId ORDER BY p.id DESC")
    List<Post> findByIdLessThan(@Param("lastId") Long lastId, Pageable pageable);
}

// Service
@Service
public class PostService {
    public List<PostDto> getPostsAfter(Long lastId, int size) {
        Pageable pageable = PageRequest.of(0, size); // offset은 항상 0!
        
        List<Post> posts;
        if (lastId == null) {
            posts = postRepository.findTopByOrderByIdDesc(pageable);
        } else {
            posts = postRepository.findByIdLessThan(lastId, pageable);
        }
        return posts.stream().map(PostDto::from).toList();
    }
}
```

생성되는 SQL:
```sql
-- 첫 페이지
SELECT * FROM posts ORDER BY id DESC LIMIT 20;

-- 다음 페이지 (lastId = 999980)
SELECT * FROM posts WHERE id < 999980 ORDER BY id DESC LIMIT 20;
```

#### 방법 3: Covering Index + Deferred Join (중간 지점, offset이 필요할 때)

```java
// Repository - Native Query 사용
@Query(value = """
    SELECT p.* FROM posts p
    INNER JOIN (
        SELECT id FROM posts ORDER BY id DESC LIMIT :size OFFSET :offset
    ) AS sub ON p.id = sub.id
    ORDER BY p.id DESC
    """, nativeQuery = true)
List<Post> findWithDeferredJoin(
    @Param("offset") int offset, 
    @Param("size") int size
);
```

핵심: 서브쿼리에서 **id만** 먼저 찾고 (인덱스만 스캔), 그 id로 본 테이블을 조인.

| 전략 | 장점 | 단점 | 적합한 상황 |
|------|------|------|------------|
| Offset | 간단, 페이지 번호 지원 | 뒤로 갈수록 느림 | 관리자 화면, 소규모 데이터 |
| Cursor | 일관된 성능, 데이터 정합성 | 페이지 번호 불가, "5페이지로 건너뛰기" 불가 | 무한 스크롤, 타임라인 |
| Deferred Join | Offset보다 빠름, 페이지 번호 지원 | 복잡한 쿼리, DB 종속적 | Offset이 필요하지만 성능도 필요할 때 |

---

### Q11-2: 커서 기반이 offset보다 빠른 이유

좋은 질문이야! 핵심을 정확히 짚어볼게.

**현실 비유**: 도서관에서 책을 찾는 상황을 생각해봐.

- **Offset 방식**: "100만 번째 책부터 20권 주세요" → 사서가 첫 번째 책부터 하나씩 세면서 100만 번째까지 감 → 그 다음 20권 뽑음
- **Cursor 방식**: "ISBN 번호가 999980보다 작은 것 중에서 20권 주세요" → 사서가 ISBN 색인(인덱스)을 펼쳐서 999980 바로 앞 위치를 찾음 → 거기서 20권 뽑음

#### 단계별로 보자

**Offset 쿼리**:
```sql
SELECT * FROM posts ORDER BY id DESC LIMIT 20 OFFSET 1000000;
```

DB 내부 동작:
1. `ORDER BY id DESC` → PK 인덱스를 역순으로 탐색 시작
2. 1번째 행 읽음 → "아직 offset 안 채움, 버림"
3. 2번째 행 읽음 → "아직 offset 안 채움, 버림"
4. ... (100만 번 반복)
5. 1,000,001번째 행 → "이제 시작!" → 결과에 포함
6. 20개 모은 후 종료

**Cursor 쿼리**:
```sql
SELECT * FROM posts WHERE id < 999980 ORDER BY id DESC LIMIT 20;
```

DB 내부 동작:
1. `WHERE id < 999980` → PK 인덱스에서 **B-Tree 탐색** (O(log n))으로 999979 위치를 바로 찾음
2. 거기서부터 역순으로 20개만 읽음
3. 끝!

#### 핵심 차이

> **Offset은 인덱스를 사용하긴 하지만, "몇 번째"라는 위치를 찾기 위해 처음부터 세야 함.**
> **Cursor는 WHERE 조건으로 B-Tree 인덱스를 직접 탐색(seek)하므로 바로 그 위치로 점프함.**

너의 질문 "offset 방식은 where절에서 index를 사용하지 않아서 그런가?" → ✅ 정확해! Offset 쿼리에는 WHERE 절이 없어. `ORDER BY id DESC`로 인덱스를 타긴 하지만, OFFSET 1000000이라는 건 "인덱스를 처음부터 100만 개 건너뛰어라"는 뜻이고, B-Tree는 **"몇 번째 노드"를 직접 찾는 기능이 없어**. 하나씩 세야 해.

반면 Cursor의 `WHERE id < 999980`은 B-Tree가 가장 잘하는 **값 기반 탐색(seek)**이야. 트리 높이만큼만 내려가면 바로 찾아 (보통 3~4단계).

---

### Q11-3: "Offset이 100만행을 스캔하고 버린다"는게 무슨 소리?

**현실 비유**: 줄 서있는 100만 명 중에 "100만 1번째부터 20명 나오세요"라고 하면, 앞에 100만 명이 한 명씩 "저 아니에요"하고 지나가야 해. 100만 1번째 사람이 손들 수 있으려면.

#### DB 엔진 내부 동작 (단계별)

```sql
SELECT * FROM posts ORDER BY id DESC LIMIT 20 OFFSET 1000000;
```

**Step 1: 실행 계획 수립**
- 옵티마이저가 `ORDER BY id DESC`를 보고 PK 인덱스를 역순으로 읽기로 결정

**Step 2: 인덱스 스캔 시작**
- B-Tree 인덱스의 가장 마지막(가장 큰 id) 리프 노드로 이동
- 여기서부터 역순으로 하나씩 읽기 시작

**Step 3: Offset 카운팅 (이게 비용이 큰 부분!)**
```
행 1 읽음 (id=2000000) → offset 카운터: 1/1000000 → 결과에 안 넣음
행 2 읽음 (id=1999999) → offset 카운터: 2/1000000 → 결과에 안 넣음
행 3 읽음 (id=1999998) → offset 카운터: 3/1000000 → 결과에 안 넣음
...
행 1000000 읽음 (id=1000001) → offset 카운터: 1000000/1000000 → 결과에 안 넣음
```

여기서 **"읽음"이란 무엇인가?**
- 인덱스 리프 노드를 하나씩 탐색 (인덱스 리프 노드 간 연결 리스트를 따라감)
- 각 엔트리에서 해당 행의 실제 데이터가 필요하면 테이블 데이터 페이지까지 접근 (random I/O)
- `SELECT *`이므로 **매 행마다 실제 데이터 페이지를 읽어야** 함 ⚠️

💡 만약 `SELECT id`만 했다면 인덱스에 id가 있으니 테이블 접근 없이 인덱스만 스캔 (Covering Index). 그래도 100만 개를 세는 건 마찬가지.

**Step 4: 실제 결과 수집**
```
행 1000001 읽음 (id=1000000) → LIMIT 카운터: 1/20 → ✅ 결과에 포함!
행 1000002 읽음 (id=999999)  → LIMIT 카운터: 2/20 → ✅ 결과에 포함!
...
행 1000020 읽음 (id=999981)  → LIMIT 카운터: 20/20 → ✅ 결과에 포함!
```

**Step 5: 완료 → 결과 반환**

#### 왜 "100만번째에서 바로 시작" 못하나?

> B-Tree 인덱스는 **값(value) 기반** 자료구조이지, **위치(position) 기반**이 아니야.

B-Tree는 "id=999980인 노드 어디있어?" → O(log n)으로 바로 찾을 수 있어.
하지만 "100만 번째 노드 어디있어?" → 이건 **몰라**. 세봐야 알아.

이건 배열(Array)과 연결 리스트(Linked List)의 차이와 비슷해:
- 배열: `arr[1000000]` → 바로 접근 (O(1))
- 연결 리스트: 1000000번째 → 처음부터 하나씩 따라가야 (O(n))

B-Tree 리프 노드들은 **연결 리스트**처럼 연결되어 있어. 그래서 "N번째"를 찾으려면 처음부터 세야 해.

---

### Q11-4: Offset/Limit으로 무한 스크롤 못 만드나?

✅ **네 말이 맞아. "못 만든다"가 아니라 "성능 문제가 있다"가 정확해.**

Offset 기반으로 무한 스크롤 완벽하게 만들 수 있어:

```javascript
// 프론트엔드
let page = 0;
const size = 20;

async function loadMore() {
    const response = await fetch(`/api/posts?page=${page}&size=${size}`);
    const data = await response.json();
    appendToList(data.content);
    page++;
}
```

이거 잘 동작해. 문제는 **성능**이야:

| 스크롤 위치 | Offset 값 | 스캔하는 행 수 | 체감 속도 |
|-----------|-----------|-------------|----------|
| 1페이지 | 0 | 20 | ⚡ 즉시 |
| 50페이지 | 1,000 | 1,020 | ⚡ 빠름 |
| 500페이지 | 10,000 | 10,020 | ✅ 괜찮음 |
| 5,000페이지 | 100,000 | 100,020 | ⚠️ 느려짐 |
| 50,000페이지 | 1,000,000 | 1,000,020 | ❌ 매우 느림 |

추가로 **데이터 정합성 문제**도 있어:

사용자가 1페이지를 보는 동안 새 글이 5개 추가되면:
- 2페이지 요청 시 `OFFSET 20`인데, 새 글 5개가 앞에 들어와서
- 1페이지에서 봤던 글 5개가 2페이지에 또 나옴 (중복!)

Cursor 기반은 `WHERE id < lastId`라서 이 문제가 없어.

#### 결론

| 구분 | Offset 기반 | Cursor 기반 |
|------|-----------|------------|
| 무한 스크롤 구현 | ✅ 가능 | ✅ 가능 |
| 초반 성능 | ✅ 빠름 | ✅ 빠름 |
| 후반 성능 | ❌ 점점 느려짐 | ✅ 일정함 |
| 데이터 중복/누락 | ⚠️ 발생 가능 | ✅ 없음 |
| 페이지 번호 | ✅ 가능 | ❌ 불가 |
| 특정 페이지 점프 | ✅ 가능 | ❌ 불가 |

---

## Q12. Spring Boot에서 트랜잭션 관리의 핵심 원칙

### Q12-1: Service 계층에 @Transactional을 선언하는 이유

**현실 비유**: 은행에서 "계좌이체"라는 업무를 생각해봐.

- **Controller** = 은행 창구 직원. 고객의 요청을 접수하고 결과를 전달하는 역할
- **Service** = 실제 업무 처리 담당자. "A 계좌에서 빼고, B 계좌에 넣고, 이체 기록 남기기"를 하나의 업무로 묶어서 처리
- **Repository** = 금고 담당. 돈을 넣거나 빼는 단일 작업만 함

#### Controller에 선언하면?

```java
@Transactional  // ❌ 여기?
@PostMapping("/transfer")
public ResponseEntity<?> transfer(@RequestBody TransferRequest req) {
    transferService.withdraw(req.from(), req.amount());
    transferService.deposit(req.to(), req.amount());
    // HTTP 응답 만들기, 로깅 등도 트랜잭션 안에 포함됨
    return ResponseEntity.ok("완료");
}
```

문제점:
- ⚠️ 트랜잭션 범위가 너무 넓어짐 (HTTP 응답 직렬화까지 포함)
- ⚠️ Connection을 오래 잡고 있음 → Connection Pool 고갈 위험
- ⚠️ Controller는 웹 요청/응답 처리가 역할인데, 비즈니스 트랜잭션 경계까지 책임지면 **단일 책임 원칙(SRP) 위반**
- ⚠️ 같은 Service를 다른 Controller, 스케줄러, 메시지 리스너에서 호출할 때 트랜잭션이 보장 안 됨

#### Repository에 선언하면?

```java
@Repository
public class AccountRepository {
    @Transactional  // ❌ 여기?
    public void withdraw(Long accountId, BigDecimal amount) { ... }
    
    @Transactional  // ❌ 여기?
    public void deposit(Long accountId, BigDecimal amount) { ... }
}
```

문제점:
- ⚠️ withdraw와 deposit이 **각각 별도의 트랜잭션**으로 실행됨
- ⚠️ withdraw 성공 후 deposit에서 실패하면? → 돈이 사라짐! 💸
- ⚠️ 비즈니스 로직의 원자성(Atomicity)을 보장할 수 없음

#### Service에 선언하는 것이 맞는 이유 ✅

```java
@Service
public class TransferService {
    @Transactional  // ✅ 여기!
    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        accountRepository.withdraw(fromId, amount);   // 같은 트랜잭션
        accountRepository.deposit(toId, amount);       // 같은 트랜잭션
        transferLogRepository.save(new TransferLog(...)); // 같은 트랜잭션
        // 하나라도 실패하면 전부 롤백!
    }
}
```

- ✅ 비즈니스 로직 단위로 트랜잭션 경계가 정해짐
- ✅ 여러 Repository 작업을 하나의 트랜잭션으로 묶을 수 있음
- ✅ Controller/스케줄러/메시지 리스너 어디서 호출해도 트랜잭션 보장

---

### Q12-2: 더티 체킹(Dirty Checking)이 뭐야?

**현실 비유**: 시험 감독관이 학생들의 답안지를 감시하는 거야.

1. 시험 시작할 때 각 학생의 답안지를 **복사**해둠 (원본 스냅샷)
2. 시험 끝나면 원본 스냅샷과 현재 답안지를 **비교**
3. 바뀐 부분이 있으면 → "이 학생 답안 수정했음!"으로 기록 → **UPDATE SQL 자동 생성**

#### 단계별 설명

```java
@Transactional
public void updateUserName(Long userId, String newName) {
    User user = userRepository.findById(userId).get(); // Step 1
    user.setName(newName);                              // Step 2
    // save() 안 해도 됨!                                // Step 3
}
```

**Step 1: 엔티티 로딩**
- DB에서 User를 가져옴
- Hibernate가 이 User의 **스냅샷(사본)을 1차 캐시에 저장**
- 이때 상태: `name = "철수"` (원본 스냅샷도 `name = "철수"`)

**Step 2: 필드 변경**
- `user.setName("영희")` → 엔티티의 name이 "영희"로 바뀜
- 하지만 스냅샷은 여전히 `name = "철수"`

**Step 3: 트랜잭션 커밋 시점 (flush)**
- Hibernate가 1차 캐시에 있는 모든 엔티티를 순회
- 각 엔티티의 **현재 상태**와 **로딩 시 스냅샷**을 필드 하나하나 비교
- `name: "철수" → "영희"` → 변경 감지! → **UPDATE SQL 자동 생성 및 실행**

```sql
UPDATE users SET name = '영희' WHERE id = 1;
```

#### readOnly = true면?

```java
@Transactional(readOnly = true)
public User getUser(Long userId) {
    return userRepository.findById(userId).get();
}
```

- Hibernate가 **스냅샷을 저장하지 않음** (어차피 수정 안 할 거니까)
- 트랜잭션 커밋 시 **비교 작업(dirty checking)을 건너뜀**
- 결과: **메모리 절약** (스냅샷 안 만듦) + **CPU 절약** (비교 안 함)

💡 이건 마치 "이 시험은 채점 안 해도 돼요~ 연습이에요~"라고 감독관에게 말하는 것과 같아. 감독관이 답안지 복사도 안 하고, 비교도 안 하니까 편해지는 거지.

---

### Q12-3: Checked Exception 롤백

#### rollbackFor에 정의된 예외가 아니면 커밋하는가?

Spring의 기본 롤백 규칙:

| 예외 타입 | 기본 동작 | 예시 |
|----------|----------|------|
| **Unchecked Exception** (RuntimeException, Error) | ✅ 자동 롤백 | `NullPointerException`, `IllegalArgumentException` |
| **Checked Exception** (Exception) | ❌ 커밋됨 | `IOException`, `SQLException`, 커스텀 Checked Exception |

그러니까 맞아. `rollbackFor`에 명시하지 않은 Checked Exception이 발생하면 **커밋해버려**. ⚠️

#### 여러 Exception을 선언하고 싶으면?

```java
// 방법 1: 배열로 여러 개 지정
@Transactional(rollbackFor = {IOException.class, CustomException.class, PaymentException.class})
public void doSomething() { ... }

// 방법 2: 최상위 Exception으로 한방에 (모든 예외에서 롤백)
@Transactional(rollbackFor = Exception.class)
public void doSomething() { ... }

// 방법 3: 롤백하지 않을 것만 제외
@Transactional(
    rollbackFor = Exception.class,
    noRollbackFor = BusinessWarningException.class  // 이것만 롤백 안 함
)
public void doSomething() { ... }
```

💡 실무 팁: 많은 팀에서 `rollbackFor = Exception.class`를 기본으로 쓰고, 롤백하지 않을 것만 `noRollbackFor`로 빼는 전략을 사용해.

#### 왜 Spring은 기본적으로 Checked Exception에서 롤백하지 않는가?

이건 **Java의 예외 설계 철학** 때문이야.

**Step 1: Java의 의도**
- **Checked Exception** = "예상 가능한, 복구 가능한 상황" (파일 못 찾음, 네트워크 끊김)
- **Unchecked Exception** = "프로그래밍 오류, 복구 불가능한 상황" (null 참조, 배열 범위 초과)

**Step 2: Spring의 철학**
- Checked Exception은 "비즈니스적으로 예상된 상황"이니까, 개발자가 **catch해서 적절히 처리**할 것으로 기대
- 예: 결제 시 잔액 부족 → `InsufficientBalanceException` (Checked) → 롤백하지 말고, 사용자에게 "잔액 부족" 알림만 보낼 수도 있잖아?
- Unchecked Exception은 "예상 못 한 오류"니까 → 무조건 롤백이 안전

**Step 3: 현실과의 괴리**
- 하지만 실제로는 Checked Exception도 롤백해야 하는 경우가 대부분
- 그래서 Spring 커뮤니티에서도 `rollbackFor = Exception.class`를 권장하는 추세
- 사실 EJB(Enterprise JavaBeans) 시절의 관례를 Spring이 따른 것이기도 해

**비유**: "교통사고(Unchecked)가 나면 보험처리(롤백) 자동이지만, 타이어 펑크(Checked)는 네가 알아서 수리하든 견인하든 결정해라"라는 철학이야. 근데 현실에서는 펑크도 보험처리 하고 싶잖아? 그래서 `rollbackFor = Exception.class`로 설정하는 거지.

---

## Q13. Connection Pool과 HikariCP

### Q13-1: maximum-pool-size 공식 (코어 × 2 + 디스크 수)의 이유

**공식**: `pool size = (core_count * 2) + effective_spindle_count`

이 공식은 PostgreSQL wiki에서 유래한 것으로, HikariCP 공식 문서에서도 인용하고 있어.

#### 왜 코어 × 2인가?

**현실 비유**: 레스토랑 주방에 요리사(코어)가 4명이야.

- 요리사 1명이 스테이크를 굽고 있어 (DB I/O 대기 중)
- 스테이크가 구워지는 동안 다른 주문(쿼리)을 처리할 수 있어
- 그래서 요리사 1명당 최대 2개의 주문을 동시에 처리 가능
- 4명 × 2 = 8개의 동시 주문

기술적으로:
- CPU 코어 1개는 한 번에 1개의 쓰레드만 실행
- 하지만 **DB 작업은 디스크 I/O가 포함**되니까, I/O 대기 중에 다른 쓰레드를 처리할 수 있어
- 그래서 코어당 2개의 Connection이 적절한 거야
- 코어 × 2 = **CPU가 I/O 대기 시간에 다른 커넥션을 처리하는 것을 반영**

#### "더 많아도 되는거 아니야?"에 대한 답

❌ 아니야. 여기서 중요한 건 **DB 서버 측의 처리 능력**이야.

- Connection이 아무리 많아도, **DB 서버의 CPU 코어**가 동시에 처리할 수 있는 쿼리 수는 한정적
- Connection이 늘어나면:
  1. DB 서버에서 더 많은 쓰레드가 동시에 동작 → **DB 서버의 컨텍스트 스위칭** 증가
  2. 각 Connection은 DB 서버에서 **메모리를 소비** (MySQL: 커넥션당 약 ~10MB)
  3. Lock contention이 증가 (더 많은 트랜잭션이 같은 행을 동시에 접근)

💡 핵심: "IO 작업이라 금방 쓰고 반환한다"고 생각할 수 있지만, **DB 서버 입장에서는 그 커넥션들이 동시에 쿼리를 던지는 것**이야. DB 서버의 CPU도 한계가 있어!

#### effective_spindle_count는 뭐야?

**Spindle** = 하드 디스크의 **회전축(물리적 디스크)**을 말해.

- HDD 1개 = spindle 1개 → `effective_spindle_count = 1`
- RAID 구성으로 HDD 4개 → `effective_spindle_count ≈ 4`
- SSD는 spindle이 없지만, 동시 I/O 처리 능력을 감안해서 보통 1로 둠 (SSD가 이미 충분히 빠르니까)

디스크가 많으면 **동시에 여러 I/O를 처리**할 수 있으니까, 그만큼 더 많은 Connection이 유의미한 작업을 할 수 있어서 pool size에 더해주는 거야.

⚠️ 이 공식은 **출발점(starting point)**이야. 실제로는 부하 테스트를 통해 조정해야 해. 현대의 NVMe SSD 환경에서는 이 공식보다 **DB 서버의 CPU 코어 수**가 더 중요한 기준이 되기도 해.

---

### Q13-2: Pool이 너무 크면 컨텍스트 스위칭 오버헤드 — 사용자 시나리오 분석

사용자 시나리오를 정리하면:
- DB: 동기 방식
- Connection Pool: 4개
- 코어: 4개
- 스레드: 8개

#### 사용자 분석이 맞는 부분 ✅

> "스레드 4개가 코어 4개에 할당돼서 connection pool에서 4개의 connection을 가져갔고, DB 처리가 되고 있는 동안 block이 되니 다른 스레드들이 코어에서 스케줄링이 되고 이때 context switching이 발생"

✅ 맞아. 애플리케이션 서버(Spring Boot)에서의 동작은 정확하게 이해하고 있어.

> "이건 connection pool과는 관계가 없지 않아?"

✅ **이것도 맞아!** 애플리케이션 서버 측의 컨텍스트 스위칭은 **스레드 수** 때문이지, connection pool 크기 때문이 아니야.

#### 사용자가 놓친 핵심 포인트 ⚠️

**"Pool size가 크면 문제가 되는 곳은 애플리케이션 서버가 아니라 DB 서버야!"**

자, 시나리오를 바꿔볼게. Connection Pool을 **100개**로 늘렸다고 해보자.

**애플리케이션 서버 (Spring Boot):**
```
스레드 200개 → 동시에 100개가 Connection을 획득 → DB에 쿼리 100개를 동시에 전송
```

**DB 서버 (MySQL/PostgreSQL):**
```
100개의 Connection이 동시에 쿼리 실행을 요청
→ DB 서버의 CPU 코어가 8개라면?
→ 8개만 동시 실행 가능, 나머지 92개는 대기
→ DB 서버 내부에서 92개의 쓰레드가 스케줄링됨
→ DB 서버에서 컨텍스트 스위칭 오버헤드 발생!
→ Lock contention 증가 (같은 테이블/행을 더 많은 트랜잭션이 접근)
→ 메모리 사용량 증가 (Connection당 메모리 할당)
→ 결과: 모든 쿼리가 느려짐 📉
```

#### 비유로 설명

**레스토랑 비유**:
- 애플리케이션 서버 = 웨이터들 (주문 받는 사람)
- Connection Pool = 주방에 전달하는 주문서 슬롯
- DB 서버 = 주방 (요리사 = DB CPU 코어)

웨이터가 아무리 많아도 주방 요리사가 4명이면:
- 주문서 슬롯(pool)이 4개 → 요리사가 딱 맞게 일함 ✅
- 주문서 슬롯(pool)이 100개 → 주문 100개가 동시에 주방에 쌓임 → 요리사들이 이 주문 저 주문 왔다갔다(컨텍스트 스위칭) → 모든 요리가 느려짐 ❌

#### 정리

| 구분 | Pool 크기 영향 |
|------|-------------|
| 앱 서버 컨텍스트 스위칭 | ❌ 관계 없음 (스레드 수에 의존) — 사용자 분석 맞음 |
| DB 서버 컨텍스트 스위칭 | ✅ 직접적 영향 (동시 Connection = DB 동시 쿼리) |
| DB 서버 메모리 | ✅ Connection당 메모리 소비 |
| DB 서버 Lock contention | ✅ 동시 트랜잭션 증가 → 충돌 증가 |
| 앱 서버 Connection 대기 | Pool 작으면 대기 증가, 크면 대기 감소 |

---

### Q13-3: HikariCP 이름의 의미

#### Hikari = 光 (ひかり, 빛)

✅ **Hikari는 일본어로 "빛(光)"을 의미해.** "빛처럼 빠른 Connection Pool"이라는 뜻이야.

CP는 맞아, **Connection Pool**의 약자.

HikariCP는 2012년경 Brett Wooldridge가 만든 Java Connection Pool 라이브러리로, 기존의 C3P0, DBCP, Tomcat Pool보다 **월등히 빠른 성능**을 자랑해서 Spring Boot 2.0부터 **기본 Connection Pool**로 채택되었어.

#### Python의 uvicorn, gunicorn에 hikari 설정이 있나?

❌ **아니야, 착각이 맞아.**

| 도구 | 언어 | 역할 | Connection Pool |
|------|------|------|-----------------|
| HikariCP | Java/JVM | DB Connection Pool | 본인이 곧 CP |
| uvicorn | Python | ASGI 웹 서버 | DB CP 아님 |
| gunicorn | Python | WSGI 웹 서버 | DB CP 아님 |

Python에서 DB Connection Pool을 쓰려면:
- **SQLAlchemy**: 내장 Connection Pool (QueuePool이 기본)
- **asyncpg**: PostgreSQL 전용 async pool
- **aiomysql**: MySQL 전용 async pool

uvicorn/gunicorn은 **웹 서버(HTTP 요청 처리)**이지 DB Connection Pool이 아니야. 너가 FastAPI/SQLAlchemy를 쓸 때 `create_engine(pool_size=5, max_overflow=10)` 같은 설정을 한 적 있을 수 있는데, 그게 SQLAlchemy 내장 Pool 설정이야.

혹시 **Hikari**와 **worker** 설정을 혼동한 게 아닐까? gunicorn의 `--workers 4` 같은 설정이 HikariCP의 pool-size와 비슷한 "리소스 개수 조절"이라서 헷갈릴 수 있어.

---

## Q14. 동시성 문제 해결 방법

### Q14-1: Optimistic Lock이 충돌이 적을 때 성능이 우수한 이유

**현실 비유**: 구글 문서(Google Docs)에서 협업하는 상황이야.

- **Optimistic Lock**: "일단 다 같이 편집하고, 저장할 때 충돌 체크하자!" → 충돌이 거의 없으면 모두가 자유롭게 작업 ✅
- **Pessimistic Lock**: "내가 편집하는 동안 아무도 건드리지 마!" → 한 사람이 끝날 때까지 나머지가 대기 ⏳

#### 내부 동작 단계별

**Step 1: 엔티티에 version 필드 추가**
```java
@Entity
public class Product {
    @Id
    private Long id;
    private String name;
    private int stock;
    
    @Version  // Optimistic Lock용 버전 필드
    private Long version;
}
```

**Step 2: 데이터 읽기**
```sql
SELECT id, name, stock, version FROM products WHERE id = 1;
-- 결과: id=1, name='키보드', stock=100, version=3
```
- 이때 **아무런 락을 걸지 않음** ✅
- DB 자원을 점유하지 않음

**Step 3: 비즈니스 로직 수행 (애플리케이션에서)**
```java
product.setStock(product.getStock() - 1); // 99로 변경
```
- 이 동안 다른 트랜잭션도 자유롭게 읽기/쓰기 가능

**Step 4: 저장 시 버전 체크 (UPDATE)**
```sql
UPDATE products 
SET stock = 99, version = 4  -- version + 1
WHERE id = 1 AND version = 3;  -- 읽었을 때의 version으로 조건!
```

**경우 1: 충돌 없음 (대부분의 경우)**
- `WHERE version = 3` → 매칭됨 → UPDATE 성공 (affected rows = 1)
- 완료! 락 없이 빠르게 처리됨 ⚡

**경우 2: 충돌 발생 (다른 누군가가 먼저 업데이트)**
- 다른 트랜잭션이 이미 version을 4로 올려버림
- `WHERE version = 3` → 매칭 안 됨 → affected rows = 0
- JPA가 `OptimisticLockException` 발생
- 애플리케이션이 재시도 또는 에러 반환

#### 왜 충돌이 적을 때 성능이 좋은가?

| 단계 | Optimistic Lock | Pessimistic Lock |
|------|----------------|-----------------|
| 읽기 | 일반 SELECT (락 없음) | `SELECT ... FOR UPDATE` (행 잠금) |
| 처리 중 | 다른 트랜잭션 자유 | 다른 트랜잭션 대기(block) |
| 쓰기 | UPDATE with version check | UPDATE (락 해제) |
| DB 자원 | 거의 안 씀 | 락 관리자가 메모리/CPU 사용 |
| Connection 점유 시간 | 짧음 | 김 (락 유지 동안 점유) |

충돌이 적으면 → Optimistic은 거의 항상 "경우 1"로 동작 → 락 오버헤드 제로에 가까움!

---

### Q14-2: Pessimistic Lock (FOR UPDATE) 심화

#### 충돌이 잦은 상황에서 쓰나? ✅

맞아. 동일한 데이터를 **여러 트랜잭션이 동시에 자주 수정**할 때 사용해.

#### Optimistic Lock보다 빠른가?

**상황에 따라 다르다!** 이게 바로 trade-off야.

#### 데드락과 성능 저하 이유

**데드락 시나리오**:
```
트랜잭션 A: 행 1 잠금 → 행 2 잠금 시도 (대기)
트랜잭션 B: 행 2 잠금 → 행 1 잠금 시도 (대기)
→ 둘 다 영원히 대기 → 데드락!
```

**성능 저하 이유**:
1. 락을 잡는 동안 **다른 트랜잭션이 블로킹됨** → 처리량(throughput) 감소
2. 블로킹 시간만큼 **Connection을 오래 점유** → Connection Pool 고갈 위험
3. 락 관리 자체가 DB 서버의 **메모리와 CPU를 소비**

#### 📌 Trade-off 정리 (핵심)

이걸 **깨진 유리창 수리비** 비유로 생각해보자.

- **Optimistic Lock** = "유리창이 깨질 확률이 낮으니 보험 안 들어. 깨지면 그때 수리비(재시도 비용) 내자."
- **Pessimistic Lock** = "유리창이 자주 깨지니까 보험료(락 비용)를 매달 내자. 깨져도 수리비는 안 들어."

| 상황 | Optimistic | Pessimistic | 승자 |
|------|-----------|-------------|------|
| 충돌률 1% | 재시도 거의 없음 ✅ | 매번 락 비용 ❌ | Optimistic |
| 충돌률 5% | 가끔 재시도 | 매번 락 비용 | Optimistic (보통) |
| 충돌률 20% | 재시도 빈번 ⚠️ | 락으로 순차 처리 | **상황에 따라** |
| 충돌률 50%+ | 재시도 폭발 ❌ | 순차 처리가 오히려 효율적 ✅ | Pessimistic |

**Optimistic의 재시도 비용**:
```
충돌 시: 읽기 → 처리 → 쓰기 실패 → 다시 읽기 → 처리 → 쓰기 (2배 비용)
충돌이 연속으로 나면? → 3배, 4배... 기하급수적 비용!
```

**Pessimistic의 대기 비용**:
```
항상: 락 획득 대기 → 처리 → 완료 → 다음 트랜잭션 시작
비용이 선형적이고 예측 가능함
```

💡 **결론**: 충돌이 많으면 Optimistic의 **비용이 예측 불가능**해지고 Pessimistic은 **예측 가능한 비용**이 장점이야. 하지만 Pessimistic은 처리량(throughput)의 상한이 낮아.

---

### Q14-3: Redis 분산 락

#### ⚠️ 먼저 중요한 오해 교정!

> "Optimistic/Pessimistic Lock도 분산 락이잖아?"

**❌ 아니야!** 이건 정확히 구분해야 해.

| 구분 | Optimistic/Pessimistic Lock | Redis 분산 락 |
|------|---------------------------|--------------|
| **레벨** | DB 레벨 락 | 애플리케이션 레벨 분산 락 |
| **범위** | 단일 DB 내부 | 여러 서버/서비스 간 |
| **관리자** | DB 엔진 (MySQL InnoDB, PostgreSQL) | Redis (외부 시스템) |
| **대상** | 테이블의 행(row) | 논리적 리소스 (아무 키든 가능) |
| **분산?** | ❌ 단일 DB 인스턴스 내에서만 유효 | ✅ 여러 서버에서 동시에 사용 가능 |

**비유**:
- **DB 락** = 교실 안의 사물함 자물쇠. 그 교실(DB) 안에서만 의미가 있어.
- **분산 락** = 학교 전체에서 공유하는 체육관 열쇠. 어느 교실(서버)에서든 이 열쇠를 가진 사람만 체육관을 쓸 수 있어.

DB 락은 **같은 DB에 연결된 트랜잭션들 사이**에서만 동작해. 만약:
- 서버 A → MySQL DB → 재고 차감
- 서버 B → MySQL DB → 재고 차감

이 경우 두 서버가 **같은 DB**를 쓰니까 DB 락으로 충분해. 하지만:
- 서버 A → 외부 API 호출 + DB 업데이트 + 캐시 갱신
- 서버 B → 같은 작업을 동시에 시도

이 경우 DB 락만으로는 **외부 API 호출의 중복**을 막을 수 없어. 분산 락이 필요한 이유야.

#### Spin Lock 방식

**비유**: 화장실 문 앞에서 계속 "문 열렸나?" 확인하면서 기다리는 거야.

```python
# 개념 코드 (Redis SETNX 기반)
import redis
import time

def acquire_lock(redis_client, lock_key, timeout=10):
    while True:
        # SETNX: 키가 없을 때만 SET (원자적 연산)
        acquired = redis_client.set(
            lock_key, 
            "locked", 
            nx=True,        # 키가 없을 때만 설정
            ex=timeout       # TTL 설정 (데드락 방지)
        )
        if acquired:
            return True      # 락 획득 성공!
        time.sleep(0.01)     # 10ms 대기 후 재시도 (스핀)

def release_lock(redis_client, lock_key):
    redis_client.delete(lock_key)
```

- ✅ 구현이 간단
- ⚠️ 스핀 대기 중 Redis에 계속 요청 → 부하 발생
- ⚠️ sleep 간격 조정이 필요 (너무 짧으면 Redis 부하, 너무 길면 대기 시간 증가)

실제로는 `Redisson` (Java) 같은 라이브러리가 Pub/Sub 기반으로 이 문제를 해결해. 스핀하지 않고 락이 해제되면 **알림을 받는 방식**이야.

#### RedLock 방식

**비유**: 중요한 결정을 할 때 5명의 위원 중 3명 이상의 동의를 받아야 하는 위원회야.

RedLock은 **여러 Redis 인스턴스**에서 과반수 이상 락을 획득해야 성공으로 인정하는 알고리즘이야.

```
Redis 1: ✅ 락 획득
Redis 2: ✅ 락 획득  
Redis 3: ✅ 락 획득    → 3/5 성공 → 과반수! → 락 획득 성공! ✅
Redis 4: ❌ 실패
Redis 5: ❌ 실패
```

왜 필요한가?
- Redis 1대만 쓰면, 그 Redis가 죽으면 락이 풀려버림 → 두 곳에서 동시 접근 가능
- 5대 중 과반수를 쓰면, 2대까지 죽어도 안전

⚠️ **참고**: RedLock은 Martin Kleppmann (DDIA 저자)과 Redis 창시자 Antirez 사이에 유명한 논쟁이 있었어. 100% 안전하지 않다는 비판도 있어서, **극도로 정확한 분산 락이 필요하면 ZooKeeper나 etcd**를 고려하기도 해.

#### 판단 기준 정리

| 상황 | 추천 방식 | 이유 |
|------|----------|------|
| 단일 DB, 읽기 많음, 충돌 적음 | Optimistic Lock (DB) | 락 비용 없이 version check만 |
| 단일 DB, 쓰기 많음, 충돌 잦음 | Pessimistic Lock (DB) | 재시도 비용보다 락이 효율적 |
| 다중 서버, 같은 DB 접근 | DB 락이면 충분 | 같은 DB라면 DB가 동시성 관리 |
| 다중 서버, DB 외 리소스도 보호 | Redis 분산 락 | API 호출, 캐시 등 DB 밖 리소스 |
| 다중 서버, 여러 DB/서비스 걸침 | Redis 분산 락 | 단일 DB 범위를 벗어남 |
| 극도의 정합성 (금융 정산) | DB Pessimistic + 분산 락 조합 | 이중 보호 |

---

### Q14-4: Idempotency Key (멱등성 키)

**현실 비유**: 

택배 주문을 생각해봐. 너가 "주문하기" 버튼을 눌렀는데 화면이 멈췄어. "어? 안 됐나?" 하고 **또 누름**. 그럼 같은 물건이 2번 주문될 수 있지?

**Idempotency Key**는 "주문서에 고유 번호를 붙이는 것"이야.

```
1번째 클릭: 주문번호 ABC-123으로 요청 → 서버: "ABC-123 처음 봄, 처리!" ✅
2번째 클릭: 주문번호 ABC-123으로 요청 → 서버: "ABC-123 이미 처리했는데? 기존 결과 돌려줄게" ✅ (중복 처리 안 함!)
```

#### 구현 개념

```java
// 클라이언트가 고유 키를 생성해서 요청에 포함
POST /api/payments
Headers:
  Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000

Body:
  { "amount": 50000, "to": "seller123" }
```

```java
@PostMapping("/payments")
public ResponseEntity<?> pay(
    @RequestHeader("Idempotency-Key") String idempotencyKey,
    @RequestBody PaymentRequest req
) {
    // 1. 이 키로 이미 처리한 적 있나?
    Optional<PaymentResult> existing = paymentRepository.findByIdempotencyKey(idempotencyKey);
    
    if (existing.isPresent()) {
        // 2. 있으면 → 기존 결과 반환 (재처리 안 함!)
        return ResponseEntity.ok(existing.get());
    }
    
    // 3. 없으면 → 실제 결제 처리
    PaymentResult result = paymentService.process(req, idempotencyKey);
    return ResponseEntity.ok(result);
}
```

💡 **핵심**: 같은 요청이 여러 번 와도 **결과가 한 번만 적용**되는 것을 보장. 이걸 **멱등성(Idempotency)**이라고 해. "같은 연산을 여러 번 해도 결과가 같다"는 수학 개념에서 온 거야 (f(f(x)) = f(x)).

#### 어디서 많이 쓰나?

- 결제 API (Stripe, Toss Payments 등이 Idempotency Key를 필수로 요구)
- 메시지 전송 (같은 알림 2번 보내면 안 되니까)
- 주문 생성

---

### Q14-5: 구체적인 선택 기준 — 교육 세션 도메인 예시

**"쏘카인드"라는 교육 플랫폼**이 있다고 가정하자. 다음 같은 기능들이 있어:

#### 시나리오 1: 수강 후기 조회 (읽기 많음 + 충돌 거의 없음)

```
상황: 교육 세션의 수강 후기를 조회. 동시에 수정하는 경우는 극히 드뭄.
→ ✅ Optimistic Lock
```

```java
@Entity
public class Review {
    @Id private Long id;
    private String content;
    private int rating;
    @Version private Long version;  // Optimistic Lock
}
```

후기를 수정할 때 version 체크만 하면 돼. 동시에 같은 후기를 수정할 확률은 거의 0이니까 재시도 비용도 거의 없어.

#### 시나리오 2: 교육 세션 수강 신청 (충돌 잦음, 정확한 인원 관리)

```
상황: 인기 세션에 정원 30명. 동시에 100명이 신청 버튼을 누름.
→ ✅ Pessimistic Lock
```

```java
@Repository
public interface SessionRepository extends JpaRepository<EducationSession, Long> {
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT s FROM EducationSession s WHERE s.id = :id")
    EducationSession findByIdWithLock(@Param("id") Long id);
}

@Service
public class EnrollmentService {
    @Transactional
    public void enroll(Long sessionId, Long userId) {
        EducationSession session = sessionRepository.findByIdWithLock(sessionId);
        if (session.getCurrentCount() >= session.getMaxCapacity()) {
            throw new SessionFullException("정원 초과");
        }
        session.incrementCount();
        enrollmentRepository.save(new Enrollment(sessionId, userId));
    }
}
```

왜 Optimistic이 아닌가?
- 100명이 동시에 신청 → version 충돌 99번 → 99번 재시도 → 재시도하는 사이에 또 충돌 → 카스케이드 실패!
- Pessimistic으로 한 명씩 순차 처리가 더 효율적

#### 시나리오 3: 교육 수료증 PDF 생성 (분산 서버, DB 외 리소스)

```
상황: 서버 3대가 운영 중. 수료증 생성은 DB 업데이트 + PDF 생성 API 호출 + S3 업로드.
사용자가 "수료증 발급" 버튼을 여러 번 클릭할 수 있음.
→ ✅ Redis 분산 락 + Idempotency Key
```

```java
@Service
public class CertificateService {
    
    private final RedissonClient redisson;
    
    public CertificateResult issueCertificate(Long userId, Long sessionId, String idempotencyKey) {
        // 1. Idempotency 체크 (중복 발급 방지)
        Optional<Certificate> existing = certRepo.findByIdempotencyKey(idempotencyKey);
        if (existing.isPresent()) return existing.get().toResult();
        
        // 2. 분산 락 획득 (같은 유저의 동시 요청 방지)
        String lockKey = "cert:" + userId + ":" + sessionId;
        RLock lock = redisson.getLock(lockKey);
        
        try {
            if (lock.tryLock(5, 30, TimeUnit.SECONDS)) {
                // 3. DB 업데이트
                Certificate cert = new Certificate(userId, sessionId, idempotencyKey);
                certRepo.save(cert);
                
                // 4. PDF 생성 (외부 API) - DB 락으로는 보호 불가!
                byte[] pdf = pdfService.generate(cert);
                
                // 5. S3 업로드 - 역시 DB 락 범위 밖!
                String url = s3Service.upload(pdf);
                
                cert.setUrl(url);
                certRepo.save(cert);
                
                return cert.toResult();
            }
            throw new LockAcquisitionException("잠시 후 다시 시도해주세요");
        } finally {
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }
}
```

왜 Redis 분산 락인가?
- 서버 3대 중 어느 서버에서든 같은 수료증 발급을 한 번만 처리해야 함
- PDF 생성, S3 업로드는 **DB 밖의 작업**이라 DB 락으로 보호 불가

#### 시나리오 4: 결제 (금융, 절대 중복 불가)

```
상황: 교육 세션 결제. 10만원짜리 세션을 2번 결제하면 큰일남.
→ ✅ Pessimistic Lock + Idempotency Key (이중 보호)
```

#### 전체 선택 흐름도

```
질문 1: DB 하나만 관련되나?
├── Yes → 질문 2: 충돌이 잦은가?
│   ├── 거의 없다 → Optimistic Lock ✅
│   └── 잦다 → Pessimistic Lock ✅
└── No (여러 서버/서비스) → 질문 3: 어떤 리소스를 보호?
    ├── DB 행만 → DB 락이면 충분 (같은 DB니까)
    └── DB + 외부 API/캐시/파일 → Redis 분산 락 ✅

추가 질문: 동일 요청 중복 가능성?
└── Yes → Idempotency Key 추가 ✅
```

---

이상으로 Q10~Q14까지의 답변이야. 각 질문의 핵심을 정리하면:

- **Q10**: EXPLAIN은 내비, EXPLAIN ANALYZE는 실제 주행 기록. MySQL은 테이블 형태, PostgreSQL은 트리 형태 + 다양한 옵션 조합 가능.
- **Q11**: Offset은 "처음부터 세기", Cursor는 "값으로 바로 점프". 무한 스크롤은 Offset으로도 되지만 성능이 문제.
- **Q12**: @Transactional은 비즈니스 단위(Service)에, readOnly는 스냅샷 안 뜨는 것, Checked Exception 롤백은 `rollbackFor = Exception.class`로 해결.
- **Q13**: Pool size 공식은 DB 서버 기준, pool이 크면 DB 서버가 고생, HikariCP = "빛처럼 빠른 CP", Python에는 HikariCP가 없어.
- **Q14**: DB 락(Optimistic/Pessimistic)은 단일 DB 내부, Redis 분산 락은 서버/서비스 간. 상황별 trade-off를 이해하는 게 핵심.


---

# Part 2: 기본 답변 (Q15~Q100)

> 📖 이 섹션은 기본 답변입니다.

---

### Q15. Spring Boot에서 비동기 처리를 구현하는 방법을 비교해주세요.

**A.**

| 방법 | 구현 | 적합한 상황 |
|------|------|------------|
| `@Async` | `@EnableAsync` + ThreadPool 설정 | 간단한 비동기 작업 (이메일, 알림) |
| `CompletableFuture` | 체이닝 가능한 비동기 | 복수 비동기 작업 조합 |
| Kotlin Coroutines | `suspend fun`, `async/await` | Kotlin 프로젝트, 구조적 동시성 |
| Virtual Threads | `spring.threads.virtual.enabled=true` | Java 21+, I/O-bound 대량 동시 처리 |
| Message Queue | RabbitMQ, Kafka | 서비스 간 비동기, 내구성 필요 |

```kotlin
// Kotlin Coroutines 예시
@Service
class AnalysisService(private val aiClient: AIClient) {
    suspend fun analyzeSession(sessionId: Long): AnalysisResult = coroutineScope {
        val speechDeferred = async { aiClient.analyzeSpeech(sessionId) }
        val faceDeferred = async { aiClient.analyzeFace(sessionId) }
        val postureDeferred = async { aiClient.analyzePosture(sessionId) }

        AnalysisResult(
            speech = speechDeferred.await(),
            face = faceDeferred.await(),
            posture = postureDeferred.await()
        )
    }
}
```

---

### Q16. Java Virtual Threads와 전통적 Thread Pool의 차이는?

**A.**

| 비교 | Platform Threads | Virtual Threads |
|------|-----------------|-----------------|
| 구현 | OS 스레드 1:1 매핑 | JVM 관리 경량 스레드 |
| 메모리 | ~1MB 스택 | ~수 KB |
| 동시 수 | 수백~수천 | 수백만 |
| 블로킹 I/O | 스레드 점유 | 자동 일시 중단/재개 |
| 활성화 | 기본 | `spring.threads.virtual.enabled=true` |

**주의사항**:
1. **synchronized 핀닝**: `synchronized` 블록 내에서 Virtual Thread가 Carrier Thread에 고정 → `ReentrantLock` 사용 권장
2. **CPU-bound에는 부적합**: 연산 집약 작업은 Platform Thread가 더 효율적
3. **ThreadLocal 남용 금지**: 수백만 VT × ThreadLocal = 메모리 폭발
4. **극단적 동시성 시 에러율 증가**: 500+ 동시 요청 시 23~30% 에러율 관찰 보고

> 📎 출처: [Java Code Geeks - Virtual Threads Performance](https://www.javacodegeeks.com/2025/04/spring-boot-performance-with-java-virtual-threads.html)

---

### Q17. REST API의 보안을 어떻게 설계하나요? JWT vs Session 비교

**A.**

| 비교 | Session 기반 | JWT 기반 |
|------|-------------|----------|
| 상태 | Stateful (서버 세션 저장) | Stateless (토큰 자체에 정보) |
| 확장성 | 세션 공유 필요 (Redis 등) | 서버 간 공유 불필요 |
| 저장소 | 서버 메모리/Redis | 클라이언트 (쿠키/헤더) |
| 만료 | 서버에서 즉시 무효화 가능 | 만료 전 무효화 어려움 (블랙리스트 필요) |
| 보안 | CSRF 공격 취약 | XSS로 토큰 탈취 위험 |

**JWT 보안 베스트 프랙티스**:
1. **HttpOnly 쿠키에 저장**: localStorage는 XSS에 취약
2. **Access Token 짧게 (15분), Refresh Token 길게 (7일)**: 토큰 탈취 피해 최소화
3. **iss, aud, exp 클레임 검증**: Spring Security OAuth2 Resource Server가 자동 처리
4. **키 로테이션**: RSA/EC 키 정기 교체
5. **Rate Limiting**: 로그인 API에 요청 제한

```java
// Spring Security 설정 (SecurityFilterChain)
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    return http
        .csrf(csrf -> csrf.disable())  // API 서버의 경우
        .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
        .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/api/public/**").permitAll()
            .requestMatchers("/api/admin/**").hasRole("ADMIN")
            .anyRequest().authenticated())
        .build();
}
```

---

### Q18. 대용량 파일(영상/음성) 업로드 처리 아키텍처를 설계하세요.

**A.** 쏘카인드의 교육 영상/음성 파일 업로드 아키텍처:

```
Client                     Backend                      Storage
  │                          │                            │
  ├─ 1. 업로드 요청 ────────→│                            │
  │                          ├─ 2. Presigned URL 발급 ──→ S3
  │←── 3. Presigned URL ─────┤                            │
  │                          │                            │
  ├─ 4. 직접 업로드 (멀티파트) ──────────────────────────→ S3
  │                          │                            │
  │                          │←── 5. S3 Event ────────────┤
  │                          ├─ 6. 메타데이터 저장 (DB)     │
  │                          ├─ 7. AI 분석 작업 큐 등록     │
  │←── 8. 완료 알림 (SSE) ───┤                            │
```

**핵심 설계 원칙**:
1. **Presigned URL**: 서버 부하 없이 S3로 직접 업로드 → 서버 대역폭 절약
2. **멀티파트 업로드**: 대용량 파일을 청크로 분할, 실패 시 해당 청크만 재시도
3. **비동기 처리**: 업로드 완료 → Message Queue → AI 분석 Worker가 처리
4. **진행률 추적**: Redis에 업로드/분석 진행률 저장, SSE로 클라이언트에 실시간 전달

---

### Q19. 캐싱 전략을 설명하세요. Cache-Aside, Write-Through, Write-Behind 비교

**A.**

| 전략 | 동작 | 장점 | 단점 |
|------|------|------|------|
| **Cache-Aside** | 앱이 캐시 확인 → 미스 시 DB 조회 → 캐시 저장 | 구현 간단, 유연 | 캐시 미스 시 지연 |
| **Write-Through** | 쓰기 시 캐시+DB 동시 기록 | 데이터 일관성 보장 | 쓰기 지연 증가 |
| **Write-Behind** | 쓰기 시 캐시만 → 비동기 DB 반영 | 쓰기 성능 우수 | 데이터 유실 위험 |
| **Read-Through** | 캐시가 DB 조회 위임 | 앱 로직 단순화 | 캐시 라이브러리 의존 |

**Spring Boot + Redis 실무**:

```java
@Cacheable(value = "companyProfile", key = "#companyId", unless = "#result == null")
public CompanyProfile getCompany(Long companyId) { ... }

@CacheEvict(value = "companyProfile", key = "#companyId")
public void updateCompany(Long companyId, CompanyUpdateDto dto) { ... }
```

**TTL 전략**: 자주 변하는 데이터(세션 목록) → 짧은 TTL(5분), 거의 변하지 않는 데이터(회사 프로필) → 긴 TTL(1시간)

---

### Q20. Spring Boot 애플리케이션의 모니터링과 Observability를 어떻게 구축하나요?

**A.** Observability 3대 축: **Metrics, Logs, Traces**

| 축 | 도구 | Spring Boot 연동 |
|----|------|------------------|
| Metrics | Micrometer + Prometheus | `spring-boot-starter-actuator` |
| Logs | SLF4J + Logback → ELK/Loki | 구조화된 JSON 로깅 |
| Traces | OpenTelemetry + Jaeger/Zipkin | `micrometer-tracing` |

**핵심 메트릭**:
- **비즈니스**: 교육 세션 완료율, AI 분석 처리 시간, 활성 사용자 수
- **애플리케이션**: API 응답시간(p50/p95/p99), 에러율, 스루풋
- **인프라**: CPU, 메모리, DB 커넥션 풀 사용률, JVM GC 빈도

```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: health, prometheus, info
  metrics:
    tags:
      application: sokind-api
```

---

### Q21. Spring Boot에서 Rate Limiting을 구현하는 방법은?

**A.**

| 알고리즘 | 원리 | 적합한 상황 |
|----------|------|------------|
| **Fixed Window** | 고정 시간 창 내 요청 수 제한 | 단순, 경계 시점 burst 가능 |
| **Sliding Window** | 이동 시간 창 | 정밀한 제어 |
| **Token Bucket** | 일정 속도로 토큰 충전, 요청 시 소모 | 버스트 허용, API Gateway 표준 |
| **Leaky Bucket** | 일정 속도로 처리 | 일정한 처리율 보장 |

**구현 방식**:
1. **Spring Cloud Gateway**: `RequestRateLimiter` 필터 (Redis 기반)
2. **Bucket4j**: 인메모리 또는 Redis 분산 Rate Limiting
3. **Resilience4j**: `@RateLimiter` 어노테이션
4. **Nginx/API Gateway**: 인프라 레벨 제어

```java
// Bucket4j 예시
@Bean
public Bucket createBucket() {
    return Bucket.builder()
        .addLimit(Bandwidth.classic(100, Refill.intervally(100, Duration.ofMinutes(1))))
        .build();
}
```

---

### Q22. 마이크로서비스 vs 모놀리식, 초기 스타트업에서의 선택 기준은?

**A.**

| 비교 | 모놀리식 | 마이크로서비스 |
|------|----------|---------------|
| 배포 | 단일 배포 단위 | 서비스별 독립 배포 |
| 복잡도 | 낮음 | 분산 시스템 복잡도 |
| 팀 규모 | 소규모(2~10명) 적합 | 대규모(10명+) 적합 |
| 운영 비용 | 낮음 | 높음 (Service Mesh, 분산 추적 등) |
| 확장 | 전체 스케일 | 서비스별 독립 스케일 |

**초기 스타트업 권장**: **Modular Monolith**

```
┌─── Modular Monolith ──────────────────┐
│  ┌──────────┐  ┌──────────┐           │
│  │ 교육 모듈 │  │ AI 분석  │           │
│  │ (training)│  │ (analysis)│          │
│  └────┬─────┘  └────┬─────┘          │
│       │              │                │
│  ┌────┴──────────────┴─────┐         │
│  │     공유 인프라 (shared)   │         │
│  │  DB, Auth, Config        │         │
│  └──────────────────────────┘         │
│                                        │
│  → 나중에 모듈 경계를 따라 분리 가능    │
└────────────────────────────────────────┘
```

**이유**: 6~10명 팀에서 마이크로서비스는 운영 오버헤드가 제품 개발 속도를 압도. Spring Modulith로 모듈 경계를 명확히 하면 나중에 분리가 용이.

---

### Q23. API 응답 시간이 느릴 때 병목을 찾는 프로세스를 설명하세요.

**A.** 체계적 병목 분석 프로세스:

```
1. APM 확인 (전체 응답 시간 분포)
   │
   ├── p99 > 목표치? → 특정 API 식별
   │
2. 해당 API 트레이싱 (Span 분석)
   │
   ├── DB 쿼리 시간?  → EXPLAIN ANALYZE → 인덱스/쿼리 최적화
   ├── 외부 API 호출? → 타임아웃 설정, Circuit Breaker, 캐싱
   ├── 비즈니스 로직?  → 프로파일링 (VisualVM, async-profiler)
   │
3. DB 커넥션 풀 확인
   │
   ├── 풀 고갈?      → pool size 조정, 느린 쿼리 해결
   │
4. JVM 확인
   │
   ├── GC 빈도 높음?  → 힙 사이즈 조정, 객체 생성 최적화
   ├── Thread 고갈?    → Virtual Threads 또는 비동기 처리
```

---

### Q24. Database Migration을 안전하게 수행하는 방법은?

**A.** Flyway 또는 Liquibase를 사용한 버전 관리 기반 마이그레이션:

**안전한 마이그레이션 원칙**:

| 원칙 | 설명 |
|------|------|
| **Backward Compatible** | 새 스키마가 이전 코드와도 호환 |
| **Expand-Contract** | 추가 → 마이그레이션 → 삭제 (3단계) |
| **무중단** | `ALTER TABLE` 시 락 최소화 |
| **롤백 가능** | 각 마이그레이션에 롤백 스크립트 준비 |

```sql
-- V1: 컬럼 추가 (Expand)
ALTER TABLE users ADD COLUMN new_email VARCHAR(255);

-- 애플리케이션이 두 컬럼 모두 읽기 시작

-- V2: 데이터 마이그레이션
UPDATE users SET new_email = email WHERE new_email IS NULL;

-- V3: 이전 컬럼 삭제 (Contract) - 모든 서버가 새 코드일 때만
ALTER TABLE users DROP COLUMN email;
ALTER TABLE users RENAME COLUMN new_email TO email;
```

---

### Q25. Spring Boot에서 멀티 데이터소스를 구성하는 방법은?

**A.** 읽기/쓰기 분리(Read Replica) 구성:

```java
@Configuration
public class DataSourceConfig {
    @Bean
    @Primary
    public DataSource routingDataSource() {
        var routing = new AbstractRoutingDataSource() {
            @Override
            protected Object determineCurrentLookupKey() {
                return TransactionSynchronizationManager.isCurrentTransactionReadOnly()
                    ? "replica" : "primary";
            }
        };
        routing.setTargetDataSources(Map.of(
            "primary", primaryDataSource(),
            "replica", replicaDataSource()
        ));
        return routing;
    }
}
```

**활용 시나리오**:
- `@Transactional(readOnly = true)` → 자동으로 Replica DB로 라우팅
- 쓰기 작업 → Primary DB로 라우팅
- AI 분석 리포트 조회(대량 읽기) → Replica에서 처리하여 Primary 부하 감소

---

### Q26. API 설계 시 멱등성(Idempotency)을 어떻게 보장하나요?

**A.**

| HTTP 메서드 | 기본 멱등성 | 추가 처리 필요 |
|------------|-----------|---------------|
| GET | ✅ 멱등 | 불필요 |
| PUT | ✅ 멱등 | 불필요 (전체 교체) |
| DELETE | ✅ 멱등 | 불필요 (없으면 404) |
| POST | ❌ 비멱등 | **Idempotency Key 필요** |
| PATCH | ❌ 비멱등 | 경우에 따라 필요 |

**Idempotency Key 구현**:
1. 클라이언트가 고유 `Idempotency-Key` 헤더를 포함하여 요청
2. 서버가 Redis에 키 존재 여부 확인
3. 이미 존재 → 저장된 이전 응답 반환
4. 미존재 → 처리 후 결과를 Redis에 TTL과 함께 저장

---

### Q27. Graceful Shutdown을 구현하는 방법과 중요성은?

**A.** 배포 시 진행 중인 요청이 완료될 때까지 기다린 후 서버를 종료:

```yaml
server:
  shutdown: graceful

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```

**동작 흐름**:
1. SIGTERM 수신 → 새 요청 거부 시작
2. 진행 중인 요청 완료 대기 (최대 30초)
3. 타임아웃 시 강제 종료
4. DB 커넥션 풀, 메시지 큐 연결 정리

**중요한 이유**: AI 분석 작업 중간에 서버가 죽으면 데이터 일관성 문제. 메시지 큐의 ACK 전 종료 시 메시지 유실 가능.

---

### Q28. Spring Boot 애플리케이션의 보안 취약점 Top 5와 대응 방법은?

**A.**

| # | 취약점 | 대응 |
|---|--------|------|
| 1 | **SQL Injection** | PreparedStatement (JPA 기본 제공), 네이티브 쿼리 시 파라미터 바인딩 필수 |
| 2 | **XSS** | 입력 검증, 출력 인코딩, CSP 헤더 설정 |
| 3 | **CSRF** | Stateless API는 비활성화, SPA+세션 시 CSRF 토큰 |
| 4 | **인증/인가 우회** | Method Security(`@PreAuthorize`), URL 패턴 화이트리스트 |
| 5 | **민감정보 노출** | Actuator 엔드포인트 보호, 에러 응답에 스택트레이스 제거 |

```yaml
# Actuator 보안 설정
management:
  endpoints:
    web:
      exposure:
        include: health, info  # 최소한만 노출
  endpoint:
    health:
      show-details: when-authorized
```

---

### Q29. CORS 설정의 원리와 Spring Boot에서의 구현 방법은?

**A.** CORS(Cross-Origin Resource Sharing)는 브라우저가 다른 도메인의 API를 호출할 때의 보안 메커니즘:

**Preflight 요청 흐름**:
```
Browser                              Server
   ├─ OPTIONS /api/users ──────────→ │
   │  Origin: https://app.sokind.ai  │
   │                                  │
   │←── Access-Control-Allow-Origin ──┤
   │    Access-Control-Allow-Methods  │
   │                                  │
   ├─ GET /api/users ─────────────→ │  (실제 요청)
```

```java
@Configuration
public class CorsConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOrigins("https://app.sokind.ai", "https://admin.sokind.ai")
            .allowedMethods("GET", "POST", "PUT", "DELETE")
            .allowedHeaders("*")
            .allowCredentials(true)
            .maxAge(3600);  // preflight 캐시 1시간
    }
}
```

---

### Q30. Spring Boot 3.x의 주요 변경사항과 마이그레이션 포인트는?

**A.**

| 변경사항 | Spring Boot 2.x | Spring Boot 3.x |
|----------|-----------------|-----------------|
| Java 버전 | Java 8+ | **Java 17+** (필수) |
| 패키지 | `javax.*` | **`jakarta.*`** |
| Spring Security | `WebSecurityConfigurerAdapter` | **`SecurityFilterChain` Bean** |
| Observability | 개별 설정 | **Micrometer Observation API** 통합 |
| Native Image | 실험적 | **GraalVM Native 공식 지원** |
| ProblemDetail | 미지원 | **RFC 7807 에러 응답** 기본 지원 |

**마이그레이션 핵심 체크리스트**:
1. `javax` → `jakarta` 패키지 전환
2. Security 설정 방식 변경
3. 의존 라이브러리 Jakarta EE 호환 버전 확인
4. Spring Boot 3.2+에서 Virtual Threads 지원

---

## 🟠 Tier 2: 팀 리딩 및 개발 문화/프로세스 (#31~55)

---

### Q31. 효과적인 코드 리뷰 문화를 어떻게 만드나요?

**A.**

**코드 리뷰 원칙**:
1. **PR 크기 제한**: 400줄 이하 (대규모 변경은 분할)
2. **리뷰 시간 SLA**: 비즈니스 시간 내 24시간 이내 첫 리뷰
3. **자동화 우선**: 린트, 포맷, 테스트는 CI에서 자동 검증 → 리뷰어는 로직/설계에 집중
4. **건설적 피드백**: "이렇게 하면 안 됩니다" → "이렇게 하면 어떨까요? 이유는..."
5. **레이블 체계**: `[Nit]` 사소한 제안, `[Must]` 반드시 수정, `[Question]` 질문

**리뷰 체크리스트**:
- 비즈니스 로직 정확성
- 엣지 케이스 처리
- 보안 취약점 (입력 검증, 인증)
- 성능 영향 (쿼리 수, 복잡도)
- 테스트 커버리지

---

### Q32. 기술 부채를 식별하고 관리하는 프로세스를 설명하세요.

**A.**

**기술 부채 분류 체계**:

| 유형 | 예시 | 긴급도 |
|------|------|--------|
| **의도적 부채** | "지금은 단순하게, 나중에 리팩토링" | 📋 백로그 등록 |
| **비의도적 부채** | 잘못된 설계가 누적 | 🔴 즉시 대응 |
| **환경 부채** | 라이브러리 EOL, 보안 패치 미적용 | 🟡 정기 점검 |
| **테스트 부채** | 테스트 커버리지 부족 | 🟠 점진적 개선 |

**관리 프로세스**:
1. **정량화**: SonarQube로 코드 복잡도, 중복, 커버리지 측정
2. **우선순위**: (영향 범위 × 변경 빈도 × 위험도)로 점수화
3. **20% 규칙**: 매 스프린트 20%를 기술 부채 해소에 투자
4. **Tech Debt Day**: 분기별 1일을 기술 부채 집중 해소에 배정
5. **ADR 기록**: 부채를 만든 결정과 향후 해결 계획을 Architecture Decision Record에 기록

> 📎 출처: [LeadDev - Building Roadmaps for Tech Debt](https://leaddev.com/legacy-technical-debt-migrations/building-realistic-roadmaps-tech-debt-cleanup)

---

### Q33. 개발팀의 기술 방향성을 어떻게 설정하나요?

**A.**

**기술 로드맵 수립 프로세스**:
1. **현황 진단**: 현재 기술 스택, 장단점, 통증점 파악
2. **비즈니스 정렬**: 6개월/1년 비즈니스 목표에 필요한 기술 역량 도출
3. **RFC(Request for Comments)**: 주요 기술 결정을 문서화하여 팀 전체 의견 수렴
4. **PoC(Proof of Concept)**: 후보 기술을 소규모 실험으로 검증
5. **점진적 도입**: Big-Bang 전환이 아닌 점진적 마이그레이션
6. **분기별 회고**: 로드맵 대비 진행률 점검 및 조정

---

### Q34. CI/CD 파이프라인을 어떻게 설계하나요?

**A.**

```
┌─ Developer ─┐
│ git push     │
└──────┬───────┘
       ▼
┌─ CI Pipeline ──────────────────────────┐
│ 1. Build (Gradle)                       │
│ 2. Unit Test                            │
│ 3. Integration Test (Testcontainers)    │
│ 4. Static Analysis (SonarQube)          │
│ 5. Docker Image Build & Push            │
└──────────────┬──────────────────────────┘
               ▼
┌─ CD Pipeline ──────────────────────────┐
│ 6. Deploy to Staging                    │
│ 7. Smoke Test / E2E Test               │
│ 8. Manual Approval (Production)         │
│ 9. Blue-Green / Canary Deploy           │
│ 10. Health Check & Rollback Trigger     │
└─────────────────────────────────────────┘
```

**핵심 원칙**:
- **Fast Feedback**: 빌드+단위테스트 3분 이내
- **환경 동일성**: Docker로 로컬/CI/프로덕션 환경 일치
- **Immutable Deploy**: 이미지 한번 빌드 → 여러 환경에 배포
- **자동 롤백**: 헬스체크 실패 시 이전 버전으로 자동 롤백

---

### Q35. 배포 전략을 비교해주세요 (Blue-Green, Canary, Rolling)

**A.**

| 전략 | 원리 | 장점 | 단점 |
|------|------|------|------|
| **Blue-Green** | 두 환경 교대 운영 | 즉시 롤백 가능 | 2배 인프라 비용 |
| **Canary** | 일부 트래픽만 새 버전 | 점진적 검증 | 라우팅 로직 필요 |
| **Rolling** | 인스턴스 순차 교체 | 리소스 효율적 | 롤백 느림, 버전 혼재 |

**쏘카인드 추천**: 소규모 팀 → **Blue-Green** (단순하고 롤백이 확실)

---

### Q36. 팀원의 기술 성장을 어떻게 지원하나요?

**A.**

| 활동 | 빈도 | 목적 |
|------|------|------|
| **1:1 미팅** | 격주 | 기술 고민, 커리어 방향, 블로커 해소 |
| **Pair Programming** | 수시 | 복잡한 기능, 신규 팀원 온보딩 |
| **Tech Talk** | 격주 | 팀원이 돌아가며 학습한 기술 공유 |
| **코드 리뷰 멘토링** | 매일 | 리뷰에서 "왜" 중심의 피드백 |
| **도전 과제 부여** | 분기 | 성장 영역에 맞는 기능 담당 배정 |

---

### Q37. Agile/Scrum에서 기술 팀 리드로서 스프린트를 어떻게 운영하나요?

**A.**

| 행사 | 주기 | 리드 역할 |
|------|------|----------|
| **Sprint Planning** | 2주 초 | 기술 복잡도 판단, 스토리 분할 지원 |
| **Daily Standup** | 매일 15분 | 블로커 해소, 기술적 의사결정 |
| **Sprint Review** | 2주 말 | 기술 데모, 기술 부채 현황 공유 |
| **Retrospective** | 2주 말 | 프로세스 개선점 도출 |
| **Backlog Refinement** | 매주 | 기술 스토리 작성, 기술 부채 항목 추가 |

**핵심 원칙**: "완벽함보다 실행 속도" → MVP로 빠르게 검증 후 개선

---

### Q38. 개발 문서를 어떻게 관리하나요? 어떤 문서를 작성하나요?

**A.**

| 문서 유형 | 목적 | 형식 |
|-----------|------|------|
| **ADR** (Architecture Decision Record) | 기술 결정과 이유 기록 | Markdown, 번호 부여 |
| **API 명세** | API 계약 정의 | OpenAPI/Swagger |
| **온보딩 가이드** | 신규 팀원 환경 설정 | README/Wiki |
| **운영 문서** | 배포 절차, 장애 대응 | Runbook 형식 |
| **설계 문서** | 기능별 기술 설계 | RFC 템플릿 |

**ADR 예시**:
```markdown
# ADR-003: LLM 제공자 추상화 레이어 도입
- 상태: Accepted
- 일자: 2026-03-22
- 결정: Spring AI ChatClient 인터페이스로 LLM 제공자 추상화
- 이유: GPT ↔ Gemini 전환 가능성, 비용 최적화
- 결과: 새 LLM 추가 시 Adapter만 구현
```

---

### Q39. Git 브랜치 전략을 설계하세요.

**A.** 소규모 팀(6~10명)에 적합한 **Trunk-Based Development**:

```
main ─────●─────●─────●─────●─────●──→ (항상 배포 가능)
           ╲   ╱ ╲   ╱       ╲   ╱
            ╲ ╱   ╲ ╱         ╲ ╱
feature/   ──●─    ──●──       ──●──    (수명 1~2일)
```

| 원칙 | 설명 |
|------|------|
| **Short-lived Branch** | feature 브랜치 수명 1~2일 |
| **Trunk에 자주 머지** | 하루 최소 1회 main에 통합 |
| **Feature Flag** | 미완성 기능은 플래그로 비활성화 |
| **CI 필수** | main 머지 전 모든 테스트 통과 |

---

### Q40. 서비스 장애 대응 프로세스를 설계하세요.

**A.**

```
장애 감지 → 공유 채널 알림 → 심각도 판정 → 대응 → 복구 → 포스트모템
```

| 심각도 | 기준 | 대응 시간 |
|--------|------|-----------|
| **P1 Critical** | 서비스 전체 중단 | 즉시 (15분 내) |
| **P2 Major** | 핵심 기능 장애 | 30분 내 |
| **P3 Minor** | 부분 기능 이상 | 업무 시간 내 |
| **P4 Low** | 사소한 이슈 | 다음 스프린트 |

**포스트모템 필수 항목**: 타임라인, 근본 원인, 영향 범위, 재발 방지 조치

---

### Q41. 설계 문서(Design Doc/RFC)를 어떻게 작성하나요?

**A.**

```markdown
# RFC: [기능/변경 제목]
## 1. 배경 및 동기
## 2. 목표 (Goals / Non-Goals)
## 3. 제안하는 설계
   - 아키텍처 다이어그램
   - API 변경사항
   - 데이터 모델 변경
## 4. 대안 검토 (Alternatives Considered)
## 5. 보안/성능 고려사항
## 6. 마이그레이션 계획
## 7. 테스트 계획
## 8. 타임라인
```

**RFC 프로세스**: 작성 → 팀 공유(3영업일 리뷰) → 피드백 반영 → 승인 → 구현

---

### Q42. 새로운 기술을 도입할 때의 의사결정 프로세스는?

**A.**

| 단계 | 활동 | 산출물 |
|------|------|--------|
| 1. 문제 정의 | 현재 기술로 해결 안 되는 이유 명확화 | 문제 정의서 |
| 2. 후보 선정 | 2~3개 후보 기술 비교 | 비교 매트릭스 |
| 3. PoC | 작은 범위에서 검증 (1~2주) | PoC 결과 보고서 |
| 4. 팀 합의 | RFC 작성 + 팀 투표 | ADR |
| 5. 점진 도입 | 비핵심 서비스부터 적용 | 마이그레이션 계획 |
| 6. 회고 | 도입 결과 평가 | 회고 문서 |

---

### Q43. 기술 면접에서 "완벽함보다 실행 속도를 우선시"한다는 것은 구체적으로 무엇을 의미하나요?

**A.**

| 상황 | ❌ 과도한 완벽주의 | ✅ 실행 속도 우선 |
|------|-------------------|------------------|
| 설계 | 모든 엣지케이스 사전 설계 | 핵심 flow 먼저 구현 → 피드백 반영 |
| 코드 품질 | 완벽한 추상화 | 동작하는 코드 → 리팩토링 |
| 기술 선택 | 6개월 비교 분석 | 1주 PoC → 결정 → 전진 |
| 배포 | 모든 테스트 완료까지 대기 | Feature Flag로 먼저 배포 → 점진적 활성화 |

**핵심**: "질러놓고 고치는 것"이 아니라, "최소한의 품질을 보장하면서 빠르게 가치를 전달"하는 것.

---

### Q44. 개발팀의 생산성을 측정하는 지표는?

**A.** DORA Metrics (DevOps Research and Assessment):

| 지표 | 설명 | 엘리트 수준 |
|------|------|------------|
| **Deployment Frequency** | 프로덕션 배포 빈도 | 하루 여러 번 |
| **Lead Time for Changes** | 커밋→배포 소요 시간 | 1시간 미만 |
| **Change Failure Rate** | 배포 후 장애 비율 | 0~15% |
| **Time to Restore** | 장애 복구 시간 | 1시간 미만 |

+ **추가 지표**: PR 리뷰 시간, 빌드 성공률, 기술 부채 지수 (SonarQube)

---

### Q45. 팀 내 기술 표준화를 어떻게 추진하나요?

**A.**

| 영역 | 표준화 항목 | 도구 |
|------|------------|------|
| 코드 스타일 | 포맷팅, 네이밍 규칙 | ktlint, EditorConfig |
| API 설계 | 응답 포맷, 에러 코드 체계 | OpenAPI spec |
| 로깅 | 구조화된 로그 포맷, 로그 레벨 | Logback MDC |
| 테스트 | 테스트 네이밍, 최소 커버리지 | JaCoCo, CI gate |
| 커밋 | Conventional Commits | commitlint |

---

### Q46. 비개발 직군(PM, 디자이너, 세일즈)과 효과적으로 소통하는 방법은?

**A.**

| 대상 | 소통 포인트 | 방법 |
|------|------------|------|
| **PM** | 기술 제약/일정 영향, trade-off 설명 | "A를 하면 2주, B를 하면 1주. B의 제약은..." |
| **디자이너** | 기술적 구현 가능성, 성능 영향 | "이 애니메이션은 모바일에서 60fps 유지 어려움" |
| **세일즈** | 기능 가용 시점, 커스터마이징 범위 | "이 기능은 다음 릴리스(3주 후)에 포함" |
| **FE** | API 계약, 에러 처리 방식 | OpenAPI spec 공유, mock server 제공 |

**원칙**: 기술 용어를 비즈니스 영향으로 번역. "DB 락 → 동시에 같은 데이터를 수정하면 충돌 방지 로직이 필요해서 개발 시간 추가 필요"

---

### Q47. 온보딩 프로세스를 어떻게 설계하나요?

**A.**

| 시점 | 활동 | 목표 |
|------|------|------|
| **Day 1** | 환경 설정, 계정 발급, 아키텍처 개요 | 로컬에서 서비스 실행 |
| **Week 1** | 코드베이스 탐색, 작은 버그 수정 | 첫 PR 머지 |
| **Week 2** | 작은 기능 개발 + 코드 리뷰 | 개발 프로세스 체화 |
| **Month 1** | 중규모 기능 담당 + 페어 프로그래밍 | 독립적 개발 가능 |
| **Month 2~3** | 설계 참여 + 코드 리뷰어 역할 | 팀 기여 |

---

### Q48. 레거시 코드를 리팩토링하는 접근 방법은?

**A.** **Strangler Fig 패턴**:

```
┌─── 레거시 시스템 ───┐
│ Module A (변경 잦음) │ ← 새 코드로 교체
│ Module B (안정적)    │ ← 유지
│ Module C (변경 잦음) │ ← 새 코드로 교체
└─────────────────────┘
```

**리팩토링 원칙**:
1. **테스트 먼저**: 리팩토링 전 기존 동작을 보장하는 테스트 추가
2. **작은 단위**: 한번에 하나의 변경. 매 변경마다 테스트 통과 확인
3. **변경 빈도 높은 모듈 우선**: 자주 수정하는 코드 = ROI 높음
4. **Boy Scout Rule**: "지나간 코드를 이전보다 깨끗하게" (매번 조금씩 개선)

---

### Q49. 기술 의사결정에서 trade-off를 어떻게 분석하나요?

**A.** 구조화된 trade-off 분석 프레임워크:

| 단계 | 활동 |
|------|------|
| 1. 제약 조건 정리 | 시간, 인력, 비용, 기술 부채 허용치 |
| 2. 평가 기준 정의 | 성능, 유지보수성, 학습 곡선, 커뮤니티 |
| 3. 가중치 부여 | 비즈니스 우선순위에 따라 |
| 4. 후보별 점수화 | 각 기준에 1~5점 |
| 5. 의사결정 기록 | ADR에 결정과 이유 기록 |

---

### Q50. "유저 경험에 대한 집착"을 백엔드 엔지니어로서 어떻게 실현하나요?

**A.**

| 영역 | 실현 방법 |
|------|----------|
| **응답 속도** | p95 < 200ms 목표, 느린 API 즉시 개선 |
| **에러 메시지** | 유저가 이해할 수 있는 에러 메시지 + 코드 |
| **일관성** | API 응답 포맷 통일, 페이지네이션 표준화 |
| **안정성** | Circuit Breaker로 외부 장애 전파 차단 |
| **실시간 피드백** | AI 분석 진행률을 SSE로 실시간 전달 |

---

### Q51. 기술 로드맵을 수립하는 방법을 설명하세요.

**A.**

| 시간축 | 내용 |
|--------|------|
| **Now (이번 분기)** | 긴급 기술 부채, 당장 필요한 인프라 |
| **Next (다음 분기)** | 중기 아키텍처 개선, 성능 최적화 |
| **Later (6개월+)** | 장기 전략 (마이크로서비스 전환, 새 기술 도입) |

**비즈니스 연계**: "해외 진출(Next) → 다국어 지원 인프라(Now) → CDN 글로벌 설정(Now)"

---

### Q52. 코드 품질을 자동으로 관리하는 방법은?

**A.**

| 도구 | 역할 | CI 단계 |
|------|------|---------|
| **ktlint** | Kotlin 코드 스타일 검사 | Build |
| **SonarQube** | 코드 복잡도, 보안 취약점, 중복 | Build 후 |
| **JaCoCo** | 테스트 커버리지 측정 | Test 후 |
| **Dependency Check** | 의존성 보안 취약점 | Build |
| **Detekt** | Kotlin 정적 분석 | Build |

**CI Quality Gate**: 커버리지 80% 미만, 심각 이슈 1건 이상이면 빌드 실패

---

### Q53. 개발자 경험(Developer Experience)을 개선하는 방법은?

**A.**

| 영역 | 개선 방법 |
|------|----------|
| **로컬 개발** | Docker Compose로 전체 환경 1분 내 구동 |
| **빌드 속도** | Gradle Build Cache, 병렬 테스트 실행 |
| **디버깅** | 구조화된 로그, Correlation ID |
| **문서** | API 문서 자동 생성 (Swagger), 코드 주석 최소화 |
| **CI 속도** | 단위 테스트 3분 이내, 전체 파이프라인 10분 이내 |

---

### Q54. A/B 테스트를 백엔드에서 어떻게 지원하나요?

**A.**

```
Request → Feature Flag Service (Redis) → 사용자 그룹 판정
                                           │
                                    ┌──────┴──────┐
                                    │ Group A      │ Group B
                                    │ (기존 로직)  │ (새 로직)
                                    └──────────────┘
```

**구현**: Feature Flag 라이브러리(Unleash, LaunchDarkly) 또는 Redis 기반 자체 구현
**핵심**: 유저별 일관성(같은 유저는 항상 같은 그룹), 비율 조절 가능, 결과 메트릭 수집

---

### Q55. 프로덕션 환경에서의 로깅 전략을 설계하세요.

**A.**

| 레벨 | 용도 | 예시 |
|------|------|------|
| **ERROR** | 서비스 장애, 데이터 정합성 문제 | DB 커넥션 실패, AI 모델 응답 오류 |
| **WARN** | 잠재적 문제, 비정상 동작 | 재시도 발생, 임계치 초과 |
| **INFO** | 핵심 비즈니스 이벤트 | 교육 세션 시작/완료, 사용자 로그인 |
| **DEBUG** | 개발 시 상세 정보 | 프로덕션에서 비활성화 |

**구조화된 로그 (JSON)**:
```json
{
  "timestamp": "2026-03-22T10:30:00Z",
  "level": "INFO",
  "service": "sokind-api",
  "traceId": "abc123",
  "userId": 42,
  "message": "Training session completed",
  "sessionId": 1001,
  "duration_ms": 3500
}
```

---

## 🟡 Tier 3: 우대사항 기술 영역 (#56~80)

---

### Q56. Java와 Kotlin의 핵심 차이와 Kotlin을 선호하는 이유는?

**A.**

| 비교 | Java | Kotlin |
|------|------|--------|
| Null 안전성 | `Optional`, `@Nullable` | **언어 레벨 `?` 타입** |
| 보일러플레이트 | Getter/Setter, Builder 필요 | **data class로 자동 생성** |
| 코루틴 | 없음 (Virtual Threads 대안) | **suspend/async/await** |
| 확장 함수 | 없음 | **기존 클래스에 함수 추가** |
| 표현력 | 장황 | **간결 (30~40% 코드 감소)** |
| 호환성 | - | **Java 100% 상호 운용** |

---

### Q57. Kotlin의 Null Safety가 실무에서 어떻게 도움이 되나요?

**A.**

```kotlin
// Kotlin: 컴파일 타임에 NPE 방지
fun getUserEmail(user: User?): String {
    return user?.email ?: "default@sokind.ai"  // Safe call + Elvis
}

// Java: 런타임 NPE 위험
public String getUserEmail(User user) {
    return user.getEmail();  // user가 null이면 NPE!
}
```

**실무 이점**:
1. NullPointerException 대부분 제거 (컴파일 에러로 전환)
2. `?.`, `?:`, `!!` 연산자로 의도를 명확히 표현
3. `let`, `also`, `apply` 스코프 함수와 결합하여 null 처리 간결화

---

### Q58. JPA와 Exposed의 차이를 설명하세요.

**A.**

| 비교 | JPA (Hibernate) | Exposed |
|------|-----------------|---------|
| 언어 | Java 중심 | **Kotlin 네이티브** |
| DSL | JPQL (문자열) | **타입 안전 SQL DSL** |
| 모드 | ORM (Entity 매핑) | **DSL + DAO 모드 선택** |
| 학습 곡선 | 높음 (프록시, 캐시 등) | 상대적으로 낮음 |
| 생태계 | 매우 넓음, Spring 완벽 통합 | 제한적, JetBrains 개발 |
| 코루틴 | 제한적 | **네이티브 지원** |

```kotlin
// Exposed DSL 예시
object TrainingSessions : Table() {
    val id = long("id").autoIncrement()
    val userId = long("user_id")
    val score = integer("score")
    override val primaryKey = PrimaryKey(id)
}

// 타입 안전 쿼리
TrainingSessions.select { TrainingSessions.userId eq 42 }
    .orderBy(TrainingSessions.score, SortOrder.DESC)
```

---

### Q59. Spring Boot에서 단위 테스트와 통합 테스트를 어떻게 구분하나요?

**A.**

| 구분 | 단위 테스트 | 통합 테스트 |
|------|-----------|------------|
| 범위 | 단일 클래스/메서드 | 여러 레이어 통합 |
| 의존성 | Mock (Mockito) | 실제 DB, 외부 서비스 |
| 속도 | 매우 빠름 (ms) | 느림 (초) |
| 도구 | JUnit + Mockito | `@SpringBootTest` + Testcontainers |
| 비율 | 60% | 30% |

```kotlin
// 단위 테스트
@Test
fun `should calculate session score correctly`() {
    val service = ScoreService(mockAnalysisRepo)
    every { mockAnalysisRepo.findBySessionId(1L) } returns mockAnalysis

    val score = service.calculateScore(1L)
    assertThat(score).isEqualTo(85)
}

// 통합 테스트 (Testcontainers)
@SpringBootTest
@Testcontainers
class SessionControllerIntegrationTest {
    @Container
    val postgres = PostgreSQLContainer("postgres:16")

    @Test
    fun `should create training session`() {
        mockMvc.post("/api/v1/sessions") {
            contentType = MediaType.APPLICATION_JSON
            content = """{"userId": 1, "companyId": 42}"""
        }.andExpect { status { isCreated() } }
    }
}
```

---

### Q60. Testcontainers를 사용하는 이유와 장점은?

**A.**

**문제**: H2 인메모리 DB로 테스트 → 프로덕션(PostgreSQL)에서 실패하는 케이스 발생
**해결**: Testcontainers로 **실제 PostgreSQL Docker 컨테이너**를 테스트에서 사용

| 장점 | 설명 |
|------|------|
| **프로덕션 동일** | 같은 DB 엔진, 같은 버전 |
| **격리** | 테스트마다 새 컨테이너 → 데이터 오염 없음 |
| **외부 서비스** | Redis, Kafka, LocalStack 등 모두 컨테이너로 |
| **CI 호환** | Docker만 있으면 어디서든 실행 |

---

### Q61. 멀티모듈 프로젝트를 어떻게 설계하나요?

**A.**

```
sokind-backend/
├── api/              ← REST Controller, DTO, Swagger
├── core/             ← 도메인 모델, 비즈니스 로직
├── persistence/      ← JPA Entity, Repository, Migration
├── ai-client/        ← AI 모델 API 클라이언트
├── notification/     ← 알림 서비스 (Email, Push)
├── shared/           ← 공통 유틸, 상수, 예외
└── app/              ← Spring Boot main, 설정, 조합
```

**핵심 규칙**:
1. **의존 방향**: `app → api → core ← persistence`, core는 외부 의존 없음
2. **순환 의존 금지**: Gradle에서 자동 감지
3. **모듈별 테스트**: 각 모듈이 독립적으로 테스트 가능
4. **버전 중앙 관리**: `gradle/libs.versions.toml` (Version Catalog)

> 📎 출처: [Bootify - Multi-Module Best Practices](https://bootify.io/multi-module/best-practices-for-spring-boot-multi-module.html)

---

### Q62. Spring Modulith와 전통적 멀티모듈의 차이는?

**A.**

| 비교 | 전통적 멀티모듈 | Spring Modulith |
|------|----------------|-----------------|
| 모듈 경계 | Gradle/Maven 모듈 | **패키지 구조** 기반 |
| 의존성 제어 | build.gradle에서 관리 | **ArchUnit 기반 자동 검증** |
| 이벤트 | 직접 구현 | **ApplicationEvent 통합** |
| 문서화 | 수동 | **자동 모듈 다이어그램 생성** |
| 적합한 규모 | 대규모, 분리 배포 필요 | 중소규모, 논리적 분리 |

---

### Q63. WebSocket과 SSE(Server-Sent Events)의 차이와 선택 기준은?

**A.**

| 비교 | WebSocket | SSE |
|------|-----------|-----|
| 통신 방향 | **양방향** | **서버→클라이언트 단방향** |
| 프로토콜 | ws:// (별도 프로토콜) | HTTP (표준) |
| 재연결 | 수동 구현 | **자동 재연결 내장** |
| 인프라 호환 | 프록시/LB 설정 필요 | HTTP 기반으로 호환 우수 |
| 적합한 상황 | 채팅, 게임, 양방향 필요 | **LLM 스트리밍, 알림, 진행률** |

**쏘카인드 적용**:
- AI 리포트 스트리밍 → **SSE** (서버→클라이언트, LLM 응답 스트리밍 표준)
- WebRTC 시그널링 → **WebSocket** (양방향 SDP/ICE 교환 필요)

---

### Q64. WebRTC 시그널링 서버를 Spring Boot로 어떻게 구현하나요?

**A.**

```
┌─ Client A ─┐                  ┌─ Client B ─┐
│   Browser   │                  │   Browser   │
│ getUserMedia│                  │ getUserMedia│
└──────┬──────┘                  └──────┬──────┘
       │ WebSocket                       │ WebSocket
       ▼                                 ▼
┌─────────────── Spring Boot Signaling Server ──────────────┐
│  1. Client A → SDP Offer → Server → Forward → Client B   │
│  2. Client B → SDP Answer → Server → Forward → Client A  │
│  3. Both → ICE Candidates → Server → Exchange → Both      │
│  4. P2P Connection Established (서버 불필요)                │
└────────────────────────────────────────────────────────────┘
```

**핵심 구성**:
- `@ServerEndpoint` 또는 Spring WebSocket(`@MessageMapping`) 사용
- STUN 서버: NAT 뒤의 공인 IP 확인 (Google 무료 STUN 서버 활용)
- TURN 서버: P2P 불가 시 릴레이 (자체 운영 또는 Twilio/Xirsys)

---

### Q65. Redis를 활용한 세션 관리와 캐싱 전략을 설명하세요.

**A.**

| 용도 | Redis 자료구조 | TTL | 예시 |
|------|---------------|-----|------|
| **HTTP 세션** | Hash | 30분 | Spring Session Redis |
| **API 캐싱** | String (JSON) | 5분~1시간 | 고객사 프로필, 교육 과정 목록 |
| **분산 락** | String (SETNX) | 10초 | 동시 AI 분석 방지 |
| **Rate Limiting** | String (INCR) | 1분 | API 요청 횟수 제한 |
| **실시간 진행률** | String | 10분 | AI 분석 진행률 (SSE로 조회) |
| **리더보드** | Sorted Set | 영구 | 교육 점수 랭킹 |

---

### Q66. Kotlin Coroutines의 Structured Concurrency를 설명하세요.

**A.** Structured Concurrency는 코루틴의 생명주기를 계층적으로 관리하여 **리소스 누수를 방지**:

```kotlin
suspend fun processSession(sessionId: Long) = coroutineScope {
    // 자식 코루틴들: 부모가 취소되면 모두 취소됨
    val speech = async { analyzeSpeech(sessionId) }     // 자식 1
    val face = async { analyzeFace(sessionId) }         // 자식 2

    // 하나가 실패하면 다른 것도 취소 (Structured)
    try {
        combineResults(speech.await(), face.await())
    } catch (e: Exception) {
        // speech 실패 → face도 자동 취소
        throw e
    }
}
```

**핵심 원칙**:
1. 부모 코루틴이 취소되면 모든 자식도 취소
2. 자식 코루틴이 실패하면 부모에게 전파
3. `coroutineScope`는 모든 자식 완료까지 대기

---

### Q67. Spring Boot에서 WebFlux vs MVC 선택 기준은?

**A.**

| 선택 기준 | Spring MVC | Spring WebFlux |
|-----------|-----------|----------------|
| I/O 패턴 | 블로킹 I/O 대부분 | **논블로킹 I/O 필요** |
| 동시 접속 | 수백~수천 | **수만~수십만** |
| 기존 코드 | JPA/JDBC 사용 중 | R2DBC/Reactive Mongo |
| 팀 역량 | 명령형 프로그래밍 익숙 | **리액티브 패러다임 이해** |
| 디버깅 | 스택트레이스 직관적 | 스택트레이스 읽기 어려움 |
| Java 21+ | **Virtual Threads**로 고동시성 해결 | - |

**쏘카인드 권장**: Spring MVC + Virtual Threads. 이유: JPA 사용, 소규모 팀 학습 곡선 고려, Java 21 Virtual Threads로 충분한 동시성 확보.

---

### Q68. JPA의 영속성 컨텍스트(Persistence Context)를 설명하세요.

**A.** 영속성 컨텍스트는 **엔티티를 관리하는 1차 캐시**:

```
┌─── 영속성 컨텍스트 (EntityManager) ───┐
│                                        │
│  1차 캐시: { id=1: UserEntity }        │
│                                        │
│  Dirty Checking: 변경 감지             │
│  → flush 시 UPDATE SQL 자동 생성       │
│                                        │
│  Write Behind: SQL을 모아서 실행       │
│                                        │
│  Identity 보장: 같은 ID = 같은 객체    │
└────────────────────────────────────────┘
```

**생명주기**: New → Managed → Detached → Removed

---

### Q69. 데이터베이스 정규화와 비정규화의 판단 기준은?

**A.**

| 정규화 | 비정규화 |
|--------|----------|
| 데이터 중복 제거 | 읽기 성능 최적화를 위해 의도적 중복 |
| 쓰기 최적화 | 읽기 최적화 |
| JOIN 필요 | JOIN 감소 |

**판단 기준**: 읽기:쓰기 비율이 10:1 이상이고, JOIN이 성능 병목이면 비정규화 고려. 단, 데이터 일관성 유지 책임이 애플리케이션으로 이동.

---

### Q70. Spring Boot에서 이벤트 기반 아키텍처를 구현하는 방법은?

**A.**

```java
// 이벤트 정의
public record SessionCompletedEvent(Long sessionId, Long userId) {}

// 이벤트 발행
@Service
public class SessionService {
    @Autowired ApplicationEventPublisher publisher;

    @Transactional
    public void completeSession(Long sessionId) {
        // 비즈니스 로직...
        publisher.publishEvent(new SessionCompletedEvent(sessionId, userId));
    }
}

// 이벤트 수신
@Component
public class AnalysisEventListener {
    @TransactionalEventListener(phase = AFTER_COMMIT)
    @Async
    public void onSessionCompleted(SessionCompletedEvent event) {
        // AI 분석 작업 시작 (트랜잭션 커밋 후)
    }
}
```

**핵심**: `@TransactionalEventListener(AFTER_COMMIT)`으로 트랜잭션 커밋 후에만 이벤트 처리 → 데이터 일관성 보장

---

### Q71. 테스트에서 Mock과 Stub의 차이는?

**A.**

| 구분 | Stub | Mock |
|------|------|------|
| 목적 | **입력에 대한 고정 응답** 제공 | **행위(호출 여부) 검증** |
| 검증 | 상태(결과값) 검증 | 상호작용(호출 횟수, 인자) 검증 |
| 예시 | `when(repo.findById(1)).thenReturn(user)` | `verify(repo, times(1)).save(any())` |

**원칙**: 가능하면 Stub으로 상태 검증을 우선하고, 외부 시스템 호출 여부를 확인해야 할 때만 Mock 사용

---

### Q72. @Transactional 테스트의 문제점은 무엇인가요?

**A.** 통합 테스트에서 `@Transactional`을 사용하면:

1. **테스트가 자동 롤백** → DB에 실제 데이터가 커밋되지 않아 트리거/제약조건 검증 불가
2. **Lazy Loading이 항상 동작** → 프로덕션에서의 `LazyInitializationException` 미발견
3. **이벤트 리스너 미동작** → `@TransactionalEventListener(AFTER_COMMIT)` 이벤트 발행 안됨

**대안**: 테스트 후 DB를 직접 정리하는 JUnit Extension 사용:
```kotlin
@AfterEach
fun cleanup() {
    jdbcTemplate.execute("TRUNCATE TABLE training_sessions CASCADE")
}
```

---

### Q73. Flyway vs Liquibase 비교

**A.**

| 비교 | Flyway | Liquibase |
|------|--------|-----------|
| 마이그레이션 포맷 | **SQL 파일** | XML/YAML/JSON/SQL |
| 학습 곡선 | 낮음 | 높음 |
| 롤백 | 유료(Teams) | **무료 지원** |
| DB 간 호환 | DB별 SQL 작성 | 추상 changeset |
| 적합한 상황 | 단일 DB, SQL 숙련 팀 | 멀티 DB, 복잡한 변경 |

**권장**: Spring Boot와의 통합이 간단하고 SQL 직접 작성이 가능한 **Flyway** (단일 DB 사용 시)

---

### Q74. Connection Leak을 어떻게 감지하고 방지하나요?

**A.**

```yaml
spring:
  datasource:
    hikari:
      leak-detection-threshold: 60000  # 60초 이상 반환 안 된 커넥션 경고
```

**감지 방법**: HikariCP의 `leak-detection-threshold` 설정 → 로그에 스택트레이스 출력
**방지**: `@Transactional` 범위 최소화, try-with-resources, 외부 API 호출을 트랜잭션 밖으로

---

### Q75. Bulk Insert/Update 성능을 최적화하는 방법은?

**A.**

```kotlin
// ❌ 느림: N번 개별 INSERT
users.forEach { userRepository.save(it) }

// ✅ 빠름: Batch INSERT
@Modifying
@Query(value = "INSERT INTO users (name, email) VALUES (:name, :email)", nativeQuery = true)
fun batchInsert(users: List<User>)

// ✅ JPA batch 설정
spring.jpa.properties.hibernate.jdbc.batch_size=50
spring.jpa.properties.hibernate.order_inserts=true
spring.jpa.properties.hibernate.order_updates=true
```

**핵심**: `batch_size` 설정 + ID 생성 전략은 `SEQUENCE` 사용 (IDENTITY는 배치 불가)

---

### Q76. Spring Boot에서 멀티테넌시(Multi-Tenancy)를 구현하는 방법은?

**A.** B2B SaaS에서 고객사(tenant)별 데이터 격리:

| 전략 | 격리 수준 | 비용 | 적합한 경우 |
|------|----------|------|------------|
| **DB 분리** | 최고 | 높음 | 규제/보안 요구 |
| **스키마 분리** | 높음 | 중간 | 중간 규모 |
| **Row-Level 분리** | 보통 | 낮음 | **대부분의 SaaS** |

```kotlin
// Row-Level: 모든 테이블에 company_id 컬럼
@Entity
@Where(clause = "company_id = :tenantId")
class TrainingSession(
    @Column(name = "company_id")
    val companyId: Long,  // tenant 식별자
    // ...
)
```

---

### Q77. 실시간 데이터 처리에서 Back Pressure를 어떻게 처리하나요?

**A.** Back Pressure는 소비자가 처리할 수 있는 속도보다 생산자가 빠를 때 발생하는 문제:

| 전략 | 설명 |
|------|------|
| **Buffer** | 제한된 크기의 버퍼에 저장 → 초과 시 드롭 또는 에러 |
| **Drop** | 최신/최고 데이터만 유지 |
| **Throttle** | 일정 시간 간격으로만 전달 |
| **Request-based** | 소비자가 요청한 만큼만 전달 (Reactive Streams) |

---

### Q78. Kotlin의 sealed class를 API 응답 설계에 어떻게 활용하나요?

**A.**

```kotlin
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val code: String, val message: String) : ApiResult<Nothing>()
    data object Loading : ApiResult<Nothing>()
}

// 사용
fun getSession(id: Long): ApiResult<SessionDto> {
    return try {
        val session = sessionService.findById(id)
        ApiResult.Success(session.toDto())
    } catch (e: NotFoundException) {
        ApiResult.Error("SESSION_NOT_FOUND", "세션을 찾을 수 없습니다")
    }
}
```

**장점**: `when` 표현식에서 **exhaustive check** → 모든 케이스 처리를 컴파일러가 보장

---

### Q79. Spring Boot Actuator의 커스텀 Health Check를 구현하는 방법은?

**A.**

```kotlin
@Component
class AIServiceHealthIndicator(
    private val aiClient: AIClient
) : HealthIndicator {

    override fun health(): Health {
        return try {
            val response = aiClient.ping()
            if (response.isOk) Health.up()
                .withDetail("model", response.model)
                .withDetail("latency_ms", response.latencyMs)
                .build()
            else Health.down()
                .withDetail("error", response.error)
                .build()
        } catch (e: Exception) {
            Health.down(e).build()
        }
    }
}
```

---

### Q80. Kotlin의 확장 함수(Extension Function)를 실무에서 어떻게 활용하나요?

**A.**

```kotlin
// Entity → DTO 변환
fun UserEntity.toDto() = UserResponse(
    id = this.id,
    name = this.name,
    email = this.email
)

// 날짜 포맷팅
fun LocalDateTime.toKoreanFormat(): String =
    this.format(DateTimeFormatter.ofPattern("yyyy년 MM월 dd일"))

// 컬렉션 유틸
fun <T> List<T>.safeSubList(from: Int, to: Int): List<T> =
    this.subList(from.coerceAtLeast(0), to.coerceAtMost(this.size))
```

---

## 🟢 Tier 4: LLM 상용화, 스타트업, FE 협업 (#81~100)

---

### Q81. Spring AI를 활용한 LLM 통합 아키텍처를 설명하세요.

**A.**

```
┌─── Spring AI Architecture ───────────────┐
│                                           │
│  Controller                               │
│     ↓                                     │
│  ChatClient (추상화 인터페이스)             │
│     ↓                                     │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐ │
│  │  OpenAI  │  │  Gemini  │  │  Claude  │ │
│  │ Adapter  │  │ Adapter  │  │ Adapter  │ │
│  └─────────┘  └─────────┘  └──────────┘ │
│                                           │
│  PromptTemplate → 프롬프트 관리           │
│  OutputParser → 구조화된 응답 파싱        │
└───────────────────────────────────────────┘
```

**핵심**: `ChatClient` 인터페이스로 LLM 제공자를 추상화 → 설정만 변경하면 GPT ↔ Gemini 전환 가능

---

### Q82. LLM 응답을 SSE로 스트리밍하는 방법은?

**A.**

```kotlin
@GetMapping("/api/v1/chat/stream", produces = [MediaType.TEXT_EVENT_STREAM_VALUE])
fun streamChat(@RequestParam prompt: String): Flux<ServerSentEvent<String>> {
    return chatClient.prompt()
        .user(prompt)
        .stream()
        .content()
        .map { chunk ->
            ServerSentEvent.builder(chunk)
                .event("message")
                .build()
        }
        .concatWith(Flux.just(
            ServerSentEvent.builder("[DONE]")
                .event("done")
                .build()
        ))
}
```

**SSE 장점**: HTTP 표준, 자동 재연결, LLM API 네이티브 지원 (OpenAI/Anthropic 모두 SSE)

> 📎 출처: [Medium - Streaming LLM Response in Spring AI](https://medium.com/@rajesh.sgr/streaming-llm-response-in-spring-ai-e1298eb5f366)

---

### Q83. LLM 서비스 프로덕션에서의 주요 고려사항은?

**A.**

| 고려사항 | 대응 |
|---------|------|
| **비용 관리** | 토큰 사용량 모니터링, 짧은 프롬프트 설계, 캐싱 |
| **지연 시간** | 스트리밍 응답(SSE), 프롬프트 최적화 |
| **장애 대응** | LLM 제공자 fallback (GPT → Gemini), Circuit Breaker |
| **프롬프트 관리** | 프롬프트 버전 관리, A/B 테스트 |
| **안전성** | 입출력 필터링 (PII 마스킹, 유해 콘텐츠 차단) |
| **재현성** | temperature=0, seed 설정, 요청/응답 로깅 |

---

### Q84. AI 모델 서빙 파이프라인을 백엔드에서 어떻게 설계하나요?

**A.**

```
사용자 요청 → API Server → Message Queue → AI Worker
                                              │
                              ┌────────────────┤
                              ▼                ▼
                          STT 분석         표정 분석
                              │                │
                              ▼                ▼
                          NLP 분석         자세 분석
                              │                │
                              └──────┬─────────┘
                                     ▼
                              결과 통합 (리포트 생성)
                                     │
                                     ▼
                              DB 저장 + SSE 알림
```

**핵심**: 비동기 처리 (Message Queue) + 병렬 분석 (여러 AI 모델 동시 실행) + 결과 통합

---

### Q85. Circuit Breaker 패턴을 외부 AI API 호출에 적용하는 방법은?

**A.**

```kotlin
@CircuitBreaker(name = "aiService", fallbackMethod = "fallbackAnalysis")
fun analyzeSession(sessionId: Long): AnalysisResult {
    return aiClient.analyze(sessionId)
}

fun fallbackAnalysis(sessionId: Long, e: Exception): AnalysisResult {
    log.warn("AI service unavailable, queuing for retry", e)
    retryQueue.enqueue(sessionId)
    return AnalysisResult.pending("AI 서비스 일시 장애, 분석이 지연됩니다")
}
```

**Resilience4j 설정**: `failureRateThreshold=50`, `waitDurationInOpenState=60s`, `slidingWindowSize=10`

---

### Q86. 스타트업에서 Zero-base로 서비스를 구축한 경험을 어떻게 설명하나요?

**A.** STAR 프레임워크:

- **S**: 초기 스타트업에서 백엔드 시스템이 전무한 상태
- **T**: 3개월 내 MVP 출시, 첫 고객사 PoC 성공
- **A**: 기술 스택 선정 → DB 설계 → API 개발 → CI/CD 구축 → 모니터링
- **R**: 정량적 결과 (출시 일정 준수, 첫 고객사 계약, 성능 지표)

**핵심 포인트**: "완벽한 설계보다 빠른 검증" + "기술 부채를 의식적으로 관리"

---

### Q87. FE 개발자와 효과적으로 협업하기 위한 API 계약(Contract)을 어떻게 관리하나요?

**A.**

| 방법 | 도구 | 장점 |
|------|------|------|
| **API-First** | OpenAPI Spec → 코드 생성 | 계약 우선, 병렬 개발 가능 |
| **Mock Server** | WireMock, Prism | FE가 백엔드 없이 개발 |
| **Contract Test** | Pact, Spring Cloud Contract | 계약 위반 자동 감지 |

```yaml
# OpenAPI Spec 예시
paths:
  /api/v1/sessions:
    post:
      summary: 교육 세션 생성
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateSessionRequest'
      responses:
        '201':
          description: 세션 생성 성공
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SessionResponse'
```

---

### Q88. 프로덕션 데이터베이스 성능 모니터링 방법은?

**A.**

| 도구 | 모니터링 대상 |
|------|-------------|
| `pg_stat_statements` | 느린 쿼리 Top N, 실행 횟수 |
| `pg_stat_activity` | 현재 실행 중인 쿼리, 대기 상태 |
| HikariCP Metrics | 커넥션 풀 사용률, 대기 시간 |
| Grafana Dashboard | 위 메트릭 시각화 + 알림 설정 |

**슬로우 쿼리 알림**: `log_min_duration_statement = 1000` (1초 이상 쿼리 로깅)

---

### Q89. Spring Boot에서 스케줄링 작업을 구현하는 방법은?

**A.**

```kotlin
@EnableScheduling
@Component
class ScheduledTasks {

    // 매일 새벽 2시 미완료 세션 정리
    @Scheduled(cron = "0 0 2 * * *")
    fun cleanupExpiredSessions() {
        sessionService.deleteExpired()
    }

    // 분산 환경에서는 ShedLock으로 단일 실행 보장
    @SchedulerLock(name = "cleanupExpiredSessions", lockAtMostFor = "PT30M")
    fun cleanupWithLock() { ... }
}
```

**분산 환경 주의**: 여러 서버에서 동시 실행 방지 → **ShedLock** (DB/Redis 기반 분산 락)

---

### Q90. Spring Boot에서 환경별 설정을 관리하는 방법은?

**A.**

```
application.yml              ← 공통 설정
application-local.yml        ← 로컬 개발
application-dev.yml          ← 개발 서버
application-staging.yml      ← 스테이징
application-prod.yml         ← 프로덕션
```

**민감 정보 관리**:
- DB 비밀번호, API 키 → **환경 변수** 또는 **AWS Secrets Manager**
- 절대 Git에 커밋하지 않음
- `@Value("${ai.api.key}")` → 환경 변수에서 주입

---

### Q91. Kotlin의 data class와 Java record의 차이는?

**A.**

| 비교 | Kotlin data class | Java record |
|------|------------------|-------------|
| 가변성 | `val`/`var` 선택 가능 | **불변(final) 전용** |
| `copy()` | ✅ 제공 | ❌ 없음 |
| 상속 | 불가 | 불가 |
| 디컴파일 | equals/hashCode/toString/copy | equals/hashCode/toString |
| 커스텀 로직 | body 내 메서드 추가 가능 | compact constructor |

---

### Q92. API Rate Limiting과 Throttling의 차이는?

**A.**

| 비교 | Rate Limiting | Throttling |
|------|---------------|------------|
| 초과 시 동작 | **즉시 거부** (HTTP 429) | **지연/대기** (큐잉) |
| 목적 | 남용 방지, 공정 사용 보장 | 트래픽 평활화, 백엔드 보호 |
| 응답 | `429 Too Many Requests` + `Retry-After` 헤더 | 요청 지연 후 정상 처리 |
| 구현 | Token Bucket, Sliding Window | Leaky Bucket, Request Queue |
| 적합한 상황 | 외부 API, 공개 엔드포인트 | 내부 서비스, 배치 처리 |

**실무 조합**: 외부 API에는 Rate Limiting(429 반환), 내부 AI 분석 파이프라인에는 Throttling(큐에 넣고 순차 처리)으로 조합하여 사용

---

### Q93. Spring Boot에서 Health Check와 Readiness/Liveness Probe의 차이는?

**A.**

| Probe | 목적 | 실패 시 |
|-------|------|---------|
| **Liveness** | 앱이 살아있는가? | 컨테이너 **재시작** |
| **Readiness** | 요청을 받을 준비가 됐는가? | 트래픽 **차단** (재시작 아님) |

```yaml
management:
  endpoint:
    health:
      probes:
        enabled: true
  health:
    livenessState:
      enabled: true
    readinessState:
      enabled: true
```

---

### Q94. OpenAPI/Swagger 문서를 자동 생성하는 방법은?

**A.**

```kotlin
// springdoc-openapi 사용
implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.x")

@Operation(summary = "교육 세션 생성", description = "새로운 교육 세션을 시작합니다")
@ApiResponses(
    ApiResponse(responseCode = "201", description = "세션 생성 성공"),
    ApiResponse(responseCode = "400", description = "입력값 오류")
)
@PostMapping("/api/v1/sessions")
fun createSession(@Valid @RequestBody request: CreateSessionRequest): SessionResponse
```

**접속**: `http://localhost:8080/swagger-ui.html`

---

### Q95. 초기 스타트업에서 기술 스택을 선정하는 기준은?

**A.**

| 기준 | 설명 |
|------|------|
| **팀 역량** | 팀이 가장 잘 아는 기술 (학습 비용 최소화) |
| **생태계** | 라이브러리/도구 풍부, 커뮤니티 활성화 |
| **채용 용이성** | 해당 기술 개발자 구인 가능 여부 |
| **확장성** | 사용자 10배 증가 시 대응 가능 |
| **비용** | 라이선스, 인프라 비용 |

---

### Q96. Kotlin의 sealed interface와 when을 활용한 도메인 모델링은?

**A.**

```kotlin
sealed interface SessionState {
    data class Waiting(val scheduledAt: LocalDateTime) : SessionState
    data class InProgress(val startedAt: LocalDateTime) : SessionState
    data class Analyzing(val progress: Int) : SessionState
    data class Completed(val report: Report) : SessionState
    data class Failed(val error: String) : SessionState
}

fun handleState(state: SessionState): String = when (state) {
    is SessionState.Waiting -> "대기 중"
    is SessionState.InProgress -> "진행 중"
    is SessionState.Analyzing -> "분석 중 (${state.progress}%)"
    is SessionState.Completed -> "완료"
    is SessionState.Failed -> "실패: ${state.error}"
    // 컴파일러가 모든 케이스 처리를 보장!
}
```

---

### Q97. 프로덕션에서 메모리 누수를 감지하고 해결하는 방법은?

**A.**

| 단계 | 도구 | 확인 포인트 |
|------|------|------------|
| 1. 모니터링 | Grafana + JVM Metrics | 힙 사용량 증가 추세 |
| 2. 힙 덤프 | `jmap -dump:format=b,file=heap.hprof <pid>` | 대용량 객체 식별 |
| 3. 분석 | Eclipse MAT, VisualVM | Dominator Tree, Leak Suspects |
| 4. 수정 | 코드 리뷰 | 닫지 않은 리소스, 캐시 무한 증가, 이벤트 리스너 해제 |

---

### Q98. Spring Boot에서 국제화(i18n)를 구현하는 방법은?

**A.**

```
resources/
├── messages.properties          ← 기본 (한국어)
├── messages_en.properties       ← 영어
├── messages_ja.properties       ← 일본어
```

```kotlin
@Service
class MessageService(private val messageSource: MessageSource) {
    fun getMessage(code: String, locale: Locale): String {
        return messageSource.getMessage(code, null, locale)
    }
}
```

**쏘카인드 적용**: 해외 진출(영어/일본어) 대비, API 에러 메시지 + 리포트 내용 다국어 지원

---

### Q99. Docker 기반 개발 환경 구성 방법은?

**A.**

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: sokind
      POSTGRES_USER: app
      POSTGRES_PASSWORD: dev123
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  app:
    build: .
    depends_on: [postgres, redis]
    environment:
      SPRING_PROFILES_ACTIVE: local
    ports:
      - "8080:8080"
```

**원칙**: `docker-compose up` 한 번으로 전체 환경 구동 가능하게

---

### Q100. 기술 면접에서 "모른다"고 말하는 것의 중요성은?

**A.**

| 상황 | ❌ 나쁜 대응 | ✅ 좋은 대응 |
|------|-------------|-------------|
| 모르는 질문 | 추측으로 답변 | "직접 경험은 없지만, 유사한 경험으로 접근하면..." |
| 부분적 지식 | 아는 척 | "X까지는 알고 있고, Y 부분은 추가 학습이 필요합니다" |
| 실수 발견 | 무시 | "방금 답변에서 X 부분이 잘못된 것 같습니다. 정정하면..." |

**핵심**: 시니어 엔지니어는 "무엇을 모르는지 아는 것"이 더 중요. 모르는 것을 인정하고 학습하는 태도가 팀에 더 큰 가치.

---

## 📎 Research Sources

1. [Spring Boot REST API Best Practices](https://www.codingshuttle.com/blogs/best-practices-for-writing-spring-boot-api/) — 기술 블로그
2. [Hexagonal Architecture in Spring Boot](https://javascript.plainenglish.io/architecting-enterprise-grade-rest-apis-in-spring-boot-a-deep-guide-to-clean-hexagonal-fdd65df3ccb3) — 기술 블로그
3. [Baeldung - N+1 Problem](https://www.baeldung.com/spring-hibernate-n1-problem) — 기술 블로그
4. [PostgreSQL Interview Questions - GeeksforGeeks](https://www.geeksforgeeks.org/postgresql/postgresql-interview-questions/) — 기술 블로그
5. [Virtual Threads Performance](https://www.javacodegeeks.com/2025/04/spring-boot-performance-with-java-virtual-threads.html) — 기술 블로그
6. [Spring Security JWT Best Practices](https://katyella.com/blog/spring-boot-security-best-practices/) — 기술 블로그
7. [WebRTC Guide - Baeldung](https://www.baeldung.com/webrtc) — 기술 블로그
8. [Spring AI Streaming](https://medium.com/@rajesh.sgr/streaming-llm-response-in-spring-ai-e1298eb5f366) — 기술 블로그
9. [Multi-Module Best Practices - Bootify](https://bootify.io/multi-module/best-practices-for-spring-boot-multi-module.html) — 기술 블로그
10. [LeadDev - Tech Debt Roadmap](https://leaddev.com/legacy-technical-debt-migrations/building-realistic-roadmaps-tech-debt-cleanup) — 기술 블로그
11. [Spring WebFlux vs MVC - GeeksforGeeks](https://www.geeksforgeeks.org/blogs/spring-mvc-vs-spring-web-flux/) — 기술 블로그
12. [Kotlin Coroutines with Spring Boot - Baeldung](https://www.baeldung.com/kotlin/spring-boot-kotlin-coroutines) — 기술 블로그
13. [Redis Caching with Spring Boot](https://medium.com/simform-engineering/spring-boot-caching-with-redis-1a36f719309f) — 기술 블로그
14. [Testcontainers with Spring Boot](https://medium.com/@aleksanderkolata/integration-tests-with-testcontainers-and-spring-boot-3-1-39103ff95bd7) — 기술 블로그
15. [Spring Boot Testing Best Practices - Wim Deblauwe](https://www.wimdeblauwe.com/blog/2025/07/30/how-i-test-production-ready-spring-boot-applications/) — 1차 자료
16. [Spring AI - Awesome Spring AI](https://github.com/spring-ai-community/awesome-spring-ai) — 커뮤니티

---

## 📊 Research Metadata

- 검색 쿼리 수: 15 (일반 13 + SNS 2)
- 수집 출처 수: 16
- 출처 유형: 공식 2, 블로그 12, 커뮤니티 2
- Deep Research: Phase 1 (광역 탐색) + Phase 2 (심화 탐색) + Phase 3 (지식 합성) 수행
- Concept Explainer: 5개 핵심 개념 (WebFlux/MVC, WebRTC, SSE/LLM, N+1, 멀티모듈) 8관점 분석
