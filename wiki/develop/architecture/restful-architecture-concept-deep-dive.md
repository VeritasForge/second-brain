---
created: 2026-03-22
source: claude-code
tags: [architecture, restful, rest-api, http, python, fastapi, sqlmodel, api-design, hateoas, content-negotiation]
---

# 📖 RESTful Architecture — Concept Deep Dive

> 💡 **한줄 요약**: REST(Representational State Transfer)는 Roy Fielding이 2000년 박사 논문에서 정의한 **분산 하이퍼미디어 시스템을 위한 아키텍처 스타일**로, 6가지 제약 조건(Client-Server, Stateless, Cache, Uniform Interface, Layered System, Code-On-Demand)을 통해 웹의 **확장성, 독립적 진화, 단순성**을 달성하는 API 설계의 사실상 표준이다.

---

## 1️⃣ 무엇인가? (What is it?)

**REST(Representational State Transfer)**는 2000년 Roy Fielding이 UC Irvine 박사 논문 *"Architectural Styles and the Design of Network-based Software Architectures"*에서 정의한 아키텍처 스타일이다. Fielding은 HTTP/1.0과 HTTP/1.1 명세의 공동 저자로서, 웹이 왜 성공적으로 확장될 수 있었는지를 설명하기 위해 REST를 형식화했다.

- **공식 정의**: "REST는 분산 하이퍼미디어 시스템의 아키텍처 스타일로, 컴포넌트 역할·제약·상호작용에 대한 일련의 아키텍처 제약 조건의 조합이다." — [Fielding Dissertation, Chapter 5](https://roy.gbiv.com/pubs/dissertation/rest_arch_style.htm)
- **탄생 배경**: 1990년대 후반 웹의 폭발적 성장 속에서, HTTP/1.1을 설계하면서 **웹이 왜 작동하는지(why the Web works)**를 아키텍처 관점에서 설명할 필요가 있었다
- **해결하는 문제**: 분산 시스템에서 확장성(scalability), 독립적 진화(independent evolvability), 단순성(simplicity), 가시성(visibility)을 동시에 달성하기 어려운 문제
- **주의**: "REST = HTTP + JSON"이 아니다. REST는 프로토콜이 아니라 **아키텍처 스타일(제약 조건의 집합)**이며, HTTP는 REST를 구현하는 가장 대표적인 프로토콜일 뿐이다

### 🏠 현실 비유: 도서관 시스템

| REST 개념 | 도서관 비유 | 설명 |
|-----------|------------|------|
| **Resource** | 책 | 시스템이 관리하는 정보의 단위 |
| **URI** | 도서 번호 (ISBN) | 각 책을 고유하게 식별하는 주소 |
| **HTTP Method** | 대출/반납 규칙 | GET=열람, POST=신간 등록, PUT=정보 수정, DELETE=폐기 |
| **Representation** | 목록 카드, PDF, 실물 책 | 같은 자원의 다양한 형태 |
| **Stateless** | 매번 도서관 카드 제시 | 이전 방문 기록을 기억하지 않음 |
| **HATEOAS** | 안내 데스크 안내문 | "이 책을 빌리려면 → 2층 대출 창구로", "반납하려면 → 1층 반납함으로" |

> 📌 **핵심 키워드**: `REST Constraints`, `Uniform Interface`, `HATEOAS`, `Stateless`, `Resource-Oriented`, `Richardson Maturity Model`

---

## 2️⃣ 핵심 개념 (Core Concepts)

### A. REST의 6가지 제약 조건 (Architectural Constraints)

Fielding은 **Null Style(제약 없음)**에서 출발하여 하나씩 제약을 추가하는 **유도 과정(derivation process)**으로 REST를 정의했다. 각 제약은 특정 아키텍처 속성을 보장한다.

```
┌─────────────────────────────────────────────────────────────────┐
│                    REST 아키텍처 제약 조건                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Client ←──→ [Cache] ←──→ [Proxy/LB] ←──→ Server                │
│    │          (③)          (⑤ Layered)      │                    │
│    │                                         │                    │
│    ├── ① Client-Server: 관심사 분리           │                    │
│    ├── ② Stateless: 요청마다 완전한 정보       │                    │
│    ├── ③ Cache: 응답의 캐시 가능 여부 명시     │                    │
│    ├── ④ Uniform Interface: 통일된 인터페이스  │                    │
│    ├── ⑤ Layered System: 계층화된 시스템      │                    │
│    └── ⑥ Code-On-Demand: 코드 다운로드 (선택) │                    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

| # | 제약 조건 | Fielding 원문 정의 | 목적 | 위반 시 문제 |
|---|----------|-------------------|------|-------------|
| ① | **Client-Server** | "Separation of concerns is the principle behind the client-server constraints" | UI와 데이터 저장의 분리 → 이식성, 확장성, 독립 진화 | 클라이언트-서버가 강결합되어 독립 배포 불가 |
| ② | **Stateless** | "Each request from client to server must contain all of the information necessary to understand the request" | 가시성(visibility), 신뢰성(reliability), 확장성(scalability) | 서버 간 세션 공유 필요 → 수평 확장 어려움 |
| ③ | **Cache** | "Data within a response to a request be implicitly or explicitly labeled as cacheable or non-cacheable" | 네트워크 효율성 향상, 사용자 체감 지연 감소 | 불필요한 네트워크 트래픽, 느린 응답 |
| ④ | **Uniform Interface** | "Applying the software engineering principle of generality to the component interface" | 전체 시스템 아키텍처 단순화, 구현과 서비스의 분리 | API 일관성 부재 → 학습 비용 증가, 재사용 불가 |
| ⑤ | **Layered System** | "Each component cannot see beyond the immediate layer with which they are interacting" | 시스템 복잡성 경계화, 레거시 캡슐화, 로드 밸런싱 | 보안 경계 불명확, 인프라 변경 시 연쇄 영향 |
| ⑥ | **Code-On-Demand** | "Client functionality extended by downloading and executing code (applets/scripts)" | 클라이언트 사전 구현 부담 감소, 확장성 향상 | (선택적 제약) 가시성 감소 가능 |

> ⚠️ **Code-On-Demand**만 유일한 **선택적(optional)** 제약이다. 나머지 5개는 REST를 구성하기 위해 반드시 준수해야 한다.

### B. Uniform Interface의 4가지 하위 제약

Uniform Interface는 REST의 핵심 차별점으로, 4가지 하위 제약으로 구성된다.

#### B-1. Resource Identification (자원 식별)

모든 자원은 **URI로 고유하게 식별**된다. 자원 자체(개념)와 표현(데이터)은 분리된다.

```python
# ✅ 좋은 URI 설계 — 명사 + 복수형 + 계층 관계
GET  /users                    # 사용자 목록
GET  /users/42                 # 특정 사용자
GET  /users/42/orders          # 특정 사용자의 주문 목록
GET  /users/42/orders/7        # 특정 주문

# ❌ 나쁜 URI 설계 — 동사 사용, RPC 스타일
POST /getUser?id=42
POST /createUser
POST /deleteUserById
```

#### B-2. Manipulation through Representations (표현을 통한 자원 조작)

클라이언트는 자원의 **표현(representation)**을 받으며, 이 표현에 충분한 메타데이터가 포함되어 있어 자원을 수정하거나 삭제할 수 있다.

```python
# 클라이언트가 받은 표현(JSON)으로 자원을 수정
# GET /users/42 → 표현 획득
response = {
    "id": 42,
    "name": "Kim",
    "email": "kim@example.com"
}

# PUT /users/42 → 표현을 보내 자원 수정
request_body = {
    "id": 42,
    "name": "Kim (Updated)",
    "email": "kim-new@example.com"
}
```

#### B-3. Self-descriptive Messages (자기 서술적 메시지)

각 메시지는 **자신을 어떻게 처리해야 하는지 충분한 정보를 포함**한다.

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8    ← 어떤 파서를 사용할지
Cache-Control: max-age=3600                      ← 캐시 가능 여부
ETag: "v1-user42-abc123"                         ← 버전 식별자
Link: </users?page=2>; rel="next"                ← 다음 페이지 안내

{"id": 42, "name": "Kim", "email": "kim@example.com"}
```

#### B-4. HATEOAS (Hypermedia as the Engine of Application State)

클라이언트는 **하이퍼미디어 링크를 통해 동적으로 사용 가능한 액션을 발견**한다. 웹 브라우저가 HTML의 링크를 따라가듯, API 클라이언트도 응답의 링크를 따라간다.

```python
# HATEOAS가 적용된 응답 예시
{
    "id": 42,
    "name": "Kim",
    "email": "kim@example.com",
    "status": "active",
    "_links": {
        "self":     {"href": "/users/42", "method": "GET"},
        "update":   {"href": "/users/42", "method": "PUT"},
        "delete":   {"href": "/users/42", "method": "DELETE"},
        "orders":   {"href": "/users/42/orders", "method": "GET"},
        "deactivate": {"href": "/users/42/deactivate", "method": "POST"}
    }
}
```

> 💡 **HATEOAS의 핵심 가치**: 클라이언트가 API 문서 없이도 서버가 제공하는 링크만 따라가면 모든 기능을 발견할 수 있다. URI가 변경되어도 클라이언트 코드를 수정할 필요가 없다.

### C. HTTP Methods와 REST

| Method | CRUD 매핑 | Safe | Idempotent | 요청 Body | 응답 예시 |
|--------|----------|------|------------|----------|----------|
| `GET` | Read | ✅ | ✅ | 없음 | `200 OK` + 자원 표현 |
| `POST` | Create | ❌ | ❌ | 있음 | `201 Created` + Location 헤더 |
| `PUT` | Update (전체) | ❌ | ✅ | 있음 | `200 OK` 또는 `204 No Content` |
| `PATCH` | Update (부분) | ❌ | ❌* | 있음 | `200 OK` + 수정된 자원 |
| `DELETE` | Delete | ❌ | ✅ | 없음/있음 | `204 No Content` |
| `HEAD` | Metadata | ✅ | ✅ | 없음 | 헤더만 반환 (Body 없음) |
| `OPTIONS` | 지원 메서드 조회 | ✅ | ✅ | 없음 | `Allow: GET, POST, PUT, DELETE` |

> *`PATCH`는 구현에 따라 멱등(idempotent)할 수도 있지만, 스펙상 멱등성이 보장되지는 않는다.

**Safe vs Idempotent 개념 정리**:
- **Safe**: 서버 상태를 변경하지 않음 (부작용 없음). GET, HEAD, OPTIONS
- **Idempotent**: 같은 요청을 여러 번 보내도 결과가 동일. GET, PUT, DELETE + Safe 메서드들

### D. Richardson Maturity Model

Leonard Richardson이 2008년 QCon에서 발표하고, Martin Fowler가 [자신의 블로그](https://martinfowler.com/articles/richardsonMaturityModel.html)에서 "steps toward the glory of REST"로 대중화한 REST API 성숙도 모델이다.

```
                    ┌─────────────────────────────────────┐
          Level 3   │   Hypermedia Controls (HATEOAS)     │  ← "Glory of REST"
                    │   응답에 하이퍼미디어 링크 포함       │
                    ├─────────────────────────────────────┤
          Level 2   │   HTTP Verbs                        │  ← 대부분의 "RESTful" API
                    │   GET/POST/PUT/DELETE + Status Code │
                    ├─────────────────────────────────────┤
          Level 1   │   Resources (URI)                   │
                    │   개별 자원에 고유 URI 부여           │
                    ├─────────────────────────────────────┤
          Level 0   │   The Swamp of POX                  │
                    │   단일 엔드포인트, HTTP = 터널링      │
                    └─────────────────────────────────────┘
```

| Level | 이름 | 특징 | 실제 예시 |
|-------|------|------|----------|
| **0** | The Swamp of POX | 단일 URI(`/api`), HTTP는 전송 수단일 뿐, 모든 요청 POST | SOAP, XML-RPC |
| **1** | Resources | 개별 URI(`/doctors/mjones`), 하지만 모든 요청 POST | 초기 REST API |
| **2** | HTTP Verbs | HTTP 메서드 의미 준수 + 적절한 Status Code 사용 | 대부분의 현대 REST API |
| **3** | Hypermedia Controls | HATEOAS 구현, 응답에 다음 액션 링크 포함 | 극소수의 API (GitHub API 일부) |

> ⚠️ **Fielding의 경고**: Fielding은 자신의 블로그에서 *"if the engine of application state (and hence the API) is not being driven by hypertext, then it cannot be RESTful and cannot be a REST API. Period."* 라고 밝혔다 ([REST APIs Must Be Hypertext-Driven, 2008](https://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven)). Martin Fowler도 이를 "Level 3 RMM is a pre-condition of REST"로 요약했다. 하지만 실무에서는 Level 2가 사실상 표준(de facto standard)이다.

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

Python + FastAPI + SQLModel 기반의 RESTful API 프로젝트 구조와 요청 흐름을 살펴보자.

### A. 프로젝트 구조

```
┌─────────────────────────────────────────────────────────────┐
│                     📁 프로젝트 구조                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  app/                                                         │
│  ├── main.py              ← 🚀 FastAPI 엔트리 + OpenAPI 설정  │
│  ├── database.py          ← 🗄️ DB 엔진 + 세션 관리            │
│  │                                                            │
│  ├── models/                                                  │
│  │   └── user.py          ← 📦 SQLModel 도메인 모델           │
│  │                                                            │
│  ├── schemas/                                                 │
│  │   ├── user.py          ← 📋 Request/Response DTO           │
│  │   ├── pagination.py    ← 📄 페이지네이션 스키마              │
│  │   └── error.py         ← ⚠️ RFC 7807 에러 스키마            │
│  │                                                            │
│  ├── routers/                                                 │
│  │   └── user.py          ← 🌐 REST 엔드포인트 (Router)        │
│  │                                                            │
│  ├── services/                                                │
│  │   └── user.py          ← ⚙️ 비즈니스 로직                   │
│  │                                                            │
│  ├── repositories/                                            │
│  │   └── user.py          ← 💾 데이터 접근 계층                 │
│  │                                                            │
│  └── exceptions.py        ← 🚨 커스텀 예외 + 핸들러             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### B. 핵심 코드 예시

#### B-1. SQLModel 모델 정의

```python
# app/models/user.py
from datetime import datetime
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """사용자 도메인 모델 (DB 테이블과 매핑)"""
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True)
    email: str = Field(max_length=255, unique=True, index=True)
    status: str = Field(default="active", max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

#### B-2. Request/Response 스키마 (HATEOAS 링크 포함)

```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr


# --- HATEOAS Link 구조 ---
class Link(BaseModel):
    href: str
    method: str = "GET"
    type: str = "application/json"


class HATEOASMixin(BaseModel):
    """HATEOAS 링크를 제공하는 Mixin (Richardson Maturity Level 3)"""
    links: dict[str, Link] = {}


# --- Request 스키마 ---
class UserCreate(BaseModel):
    name: str
    email: EmailStr


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    status: str | None = None


# --- Response 스키마 ---
class UserResponse(HATEOASMixin):
    id: int
    name: str
    email: str
    status: str

    @classmethod
    def from_model(cls, user, base_url: str = "") -> "UserResponse":
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            status=user.status,
            links={
                "self":    Link(href=f"{base_url}/users/{user.id}"),
                "update":  Link(href=f"{base_url}/users/{user.id}", method="PUT"),
                "delete":  Link(href=f"{base_url}/users/{user.id}", method="DELETE"),
                "orders":  Link(href=f"{base_url}/users/{user.id}/orders"),
            },
        )
```

#### B-3. 페이지네이션 스키마

```python
# app/schemas/pagination.py
from pydantic import BaseModel


# --- Offset 기반 페이지네이션 ---
class PageMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int


class PaginatedResponse[T](BaseModel):
    """제네릭 페이지네이션 응답 (Python 3.12+ 문법)"""
    data: list[T]
    meta: PageMeta
    links: dict[str, str]  # self, next, prev, first, last


# --- Cursor 기반 페이지네이션 ---
class CursorPaginatedResponse[T](BaseModel):
    """대용량 데이터셋에 적합한 Cursor 기반 페이지네이션"""
    data: list[T]
    next_cursor: str | None = None
    has_more: bool = False
    links: dict[str, str]  # self, next
```

**Offset vs Cursor 비교**:

| 기준 | Offset (`?page=2&per_page=20`) | Cursor (`?cursor=abc123&limit=20`) |
|------|-------------------------------|-----------------------------------|
| **구현 난이도** | ✅ 간단 | ❌ 복잡 (인코딩/디코딩 필요) |
| **성능 (대용량)** | ❌ OFFSET이 클수록 느림 | ✅ 일정한 성능 |
| **임의 페이지 접근** | ✅ `?page=50` 가능 | ❌ 불가 (순차 탐색만) |
| **실시간 데이터** | ❌ 삽입/삭제 시 중복/누락 | ✅ 일관된 결과 |
| **적합한 경우** | 관리자 화면, 소규모 데이터 | 무한 스크롤, 대용량 피드 |

#### B-4. RFC 7807 Problem Details 에러 핸들링

```python
# app/schemas/error.py
from pydantic import BaseModel


class ProblemDetail(BaseModel):
    """RFC 7807 (RFC 9457로 업데이트) Problem Details for HTTP APIs

    표준화된 에러 응답 형식으로, 기계가 읽을 수 있고 사람이 이해할 수 있는
    에러 정보를 제공한다.
    """
    type: str = "about:blank"        # 에러 유형을 식별하는 URI
    title: str                       # 사람이 읽을 수 있는 에러 요약
    status: int                      # HTTP 상태 코드
    detail: str | None = None        # 이 발생에 특화된 설명
    instance: str | None = None      # 이 발생을 식별하는 URI
    errors: list[dict] | None = None # 필드별 검증 에러 (확장 필드)
```

```python
# app/exceptions.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.schemas.error import ProblemDetail


class ResourceNotFoundError(Exception):
    def __init__(self, resource: str, resource_id: int | str):
        self.resource = resource
        self.resource_id = resource_id


class ConflictError(Exception):
    def __init__(self, detail: str):
        self.detail = detail


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ResourceNotFoundError)
    async def not_found_handler(request: Request, exc: ResourceNotFoundError):
        return JSONResponse(
            status_code=404,
            media_type="application/problem+json",
            content=ProblemDetail(
                type="https://api.example.com/errors/not-found",
                title="Resource Not Found",
                status=404,
                detail=f"{exc.resource} with id '{exc.resource_id}' was not found",
                instance=str(request.url),
            ).model_dump(),
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError):
        return JSONResponse(
            status_code=409,
            media_type="application/problem+json",
            content=ProblemDetail(
                type="https://api.example.com/errors/conflict",
                title="Resource Conflict",
                status=409,
                detail=exc.detail,
                instance=str(request.url),
            ).model_dump(),
        )
```

#### B-5. CRUD Router (완전한 REST 엔드포인트)

```python
# app/routers/user.py
from fastapi import APIRouter, Depends, Query, Response, status
from sqlmodel import Session

from app.database import get_session
from app.exceptions import ResourceNotFoundError
from app.models.user import User
from app.schemas.pagination import PaginatedResponse, PageMeta
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


# ── GET /users — 목록 조회 (Pagination) ──
@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(1, ge=1, description="페이지 번호"),
    per_page: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    status_filter: str | None = Query(None, alias="status"),
    sort: str = Query("-created_at", description="정렬 기준 (-필드: 내림차순)"),
    session: Session = Depends(get_session),
):
    """사용자 목록 조회 — Offset 기반 페이지네이션, 필터링, 정렬 지원"""
    query = session.query(User)

    # 필터링
    if status_filter:
        query = query.filter(User.status == status_filter)

    # 정렬
    if sort.startswith("-"):
        query = query.order_by(getattr(User, sort[1:]).desc())
    else:
        query = query.order_by(getattr(User, sort))

    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = (total + per_page - 1) // per_page

    return PaginatedResponse(
        data=[UserResponse.from_model(u) for u in users],
        meta=PageMeta(
            page=page, per_page=per_page,
            total=total, total_pages=total_pages,
        ),
        links={
            "self":  f"/users?page={page}&per_page={per_page}",
            "first": f"/users?page=1&per_page={per_page}",
            "last":  f"/users?page={total_pages}&per_page={per_page}",
            **({"next": f"/users?page={page+1}&per_page={per_page}"}
               if page < total_pages else {}),
            **({"prev": f"/users?page={page-1}&per_page={per_page}"}
               if page > 1 else {}),
        },
    )


# ── POST /users — 생성 ──
@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    response: Response,
    session: Session = Depends(get_session),
):
    """사용자 생성 — 201 Created + Location 헤더 반환"""
    user = User(**body.model_dump())
    session.add(user)
    session.commit()
    session.refresh(user)

    # Location 헤더: 새로 생성된 자원의 URI (REST 필수 관례)
    response.headers["Location"] = f"/users/{user.id}"
    return UserResponse.from_model(user)


# ── GET /users/{user_id} — 단건 조회 ──
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    response: Response,
    session: Session = Depends(get_session),
):
    """사용자 조회 — ETag 기반 캐시 지원"""
    user = session.get(User, user_id)
    if not user:
        raise ResourceNotFoundError("User", user_id)

    # ETag 설정 (조건부 요청 지원)
    etag = f'"{user.id}-{user.updated_at.isoformat()}"'
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "private, max-age=60"

    return UserResponse.from_model(user)


# ── PUT /users/{user_id} — 전체 수정 (Idempotent) ──
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    body: UserUpdate,
    session: Session = Depends(get_session),
):
    """사용자 전체 수정 — 멱등성(idempotent) 보장"""
    user = session.get(User, user_id)
    if not user:
        raise ResourceNotFoundError("User", user_id)

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return UserResponse.from_model(user)


# ── PATCH /users/{user_id} — 부분 수정 ──
@router.patch("/{user_id}", response_model=UserResponse)
async def patch_user(
    user_id: int,
    body: UserUpdate,
    session: Session = Depends(get_session),
):
    """사용자 부분 수정 — exclude_unset으로 전송된 필드만 수정"""
    user = session.get(User, user_id)
    if not user:
        raise ResourceNotFoundError("User", user_id)

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return UserResponse.from_model(user)


# ── DELETE /users/{user_id} — 삭제 ──
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
):
    """사용자 삭제 — 204 No Content (본문 없음)"""
    user = session.get(User, user_id)
    if not user:
        raise ResourceNotFoundError("User", user_id)

    session.delete(user)
    session.commit()
    # 204 No Content — 응답 본문 없음
```

#### B-6. Content Negotiation 예시

```python
# app/routers/user.py (Content Negotiation 확장)
from fastapi import Header
import csv
import io


@router.get("/{user_id}/export")
async def export_user(
    user_id: int,
    accept: str = Header("application/json"),
    session: Session = Depends(get_session),
):
    """Content Negotiation: Accept 헤더에 따라 다른 표현 반환"""
    user = session.get(User, user_id)
    if not user:
        raise ResourceNotFoundError("User", user_id)

    if "text/csv" in accept:
        # CSV 표현
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "name", "email", "status"])
        writer.writerow([user.id, user.name, user.email, user.status])
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=user_{user_id}.csv"},
        )
    else:
        # 기본 JSON 표현
        return UserResponse.from_model(user)
```

#### B-7. Database 설정

```python
# app/database.py
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```

#### B-8. FastAPI 애플리케이션 엔트리

```python
# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.exceptions import register_exception_handlers
from app.routers import user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan 이벤트 (on_event 대신 권장)"""
    create_db_and_tables()
    yield


app = FastAPI(
    title="RESTful API Example",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.include_router(user.router)
```

### C. 요청/응답 흐름

```
┌──────────┐         ┌──────────┐        ┌──────────┐        ┌──────────┐        ┌────┐
│  Client  │         │  Router  │        │ Service  │        │   Repo   │        │ DB │
└────┬─────┘         └────┬─────┘        └────┬─────┘        └────┬─────┘        └──┬─┘
     │                     │                   │                   │                 │
     │  GET /users/42      │                   │                   │                 │
     │ Accept: app/json    │                   │                   │                 │
     │────────────────────►│                   │                   │                 │
     │                     │                   │                   │                 │
     │                     │  get_user(42)     │                   │                 │
     │                     │──────────────────►│                   │                 │
     │                     │                   │                   │                 │
     │                     │                   │  find_by_id(42)   │                 │
     │                     │                   │──────────────────►│                 │
     │                     │                   │                   │                 │
     │                     │                   │                   │  SELECT * FROM   │
     │                     │                   │                   │  users WHERE     │
     │                     │                   │                   │  id = 42         │
     │                     │                   │                   │────────────────►│
     │                     │                   │                   │                 │
     │                     │                   │                   │  User row       │
     │                     │                   │                   │◄────────────────│
     │                     │                   │                   │                 │
     │                     │                   │  User model       │                 │
     │                     │                   │◄──────────────────│                 │
     │                     │                   │                   │                 │
     │                     │  UserResponse     │                   │                 │
     │                     │  (+ HATEOAS links)│                   │                 │
     │                     │◄──────────────────│                   │                 │
     │                     │                   │                   │                 │
     │  200 OK             │                   │                   │                 │
     │  Content-Type: json │                   │                   │                 │
     │  ETag: "42-2026..." │                   │                   │                 │
     │  Cache-Control: ... │                   │                   │                 │
     │  {id, name, _links} │                   │                   │                 │
     │◄────────────────────│                   │                   │                 │
     │                     │                   │                   │                 │
```

### D. Status Code 설계 가이드

| Operation | Success | Client Error | Server Error |
|-----------|---------|-------------|-------------|
| `GET /users` | `200 OK` | `400 Bad Request` (잘못된 쿼리) | `500 Internal Server Error` |
| `GET /users/42` | `200 OK` | `404 Not Found` | `500 Internal Server Error` |
| `POST /users` | `201 Created` + Location | `400 Bad Request`, `409 Conflict` (중복) | `500 Internal Server Error` |
| `PUT /users/42` | `200 OK` / `204 No Content` | `400`, `404`, `409` | `500 Internal Server Error` |
| `PATCH /users/42` | `200 OK` | `400`, `404`, `422 Unprocessable Entity` | `500 Internal Server Error` |
| `DELETE /users/42` | `204 No Content` | `404 Not Found` | `500 Internal Server Error` |
| Rate Limited | — | `429 Too Many Requests` + Retry-After | — |
| Unauthorized | — | `401 Unauthorized` | — |
| Forbidden | — | `403 Forbidden` | — |

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스

### A. URI 설계 규칙

```
✅ 올바른 패턴                    ❌ 피해야 할 패턴
──────────────────────────────   ──────────────────────────────
/users                          /getUsers
/users/42                       /user/42  (단수형)
/users/42/orders                /getUserOrders?userId=42
/users/42/orders/7              /api/v1/user_orders/
/search?q=keyword               /searchUsers  (동사)
```

| 규칙 | 설명 | 예시 |
|------|------|------|
| **명사 + 복수형** | URI는 자원을 나타내며, 컬렉션은 복수형 | `/users`, `/orders` |
| **계층 관계** | 소유 관계를 경로로 표현 | `/users/42/orders` |
| **소문자 + 하이픈** | 일관된 명명 규칙 | `/user-profiles`, `/order-items` |
| **확장자 없음** | Content Negotiation 사용 | `/users/42` (not `.json`) |
| **Trailing Slash 없음** | 일관성 유지 | `/users` (not `/users/`) |
| **필터는 Query String** | 컬렉션 필터링에 사용 | `/users?status=active&sort=-created_at` |

### B. Versioning 전략 비교

| 전략 | 예시 | 장점 | 단점 | 추천 |
|------|------|------|------|------|
| **URI Path** | `/v1/users`, `/v2/users` | 명확, 캐시 친화적, 테스트 쉬움 | URI 변경됨, "RESTful하지 않다" 논쟁 | ✅ 실무 권장 |
| **Query Param** | `/users?version=2` | 기존 URI 유지 | 캐시 키 복잡, 선택적 사용 혼란 | ⚠️ 제한적 |
| **Header** | `Accept: application/vnd.api.v2+json` | URI 깔끔, RESTful | 디버깅 어려움, 브라우저 테스트 불편 | ⚠️ 제한적 |
| **Media Type** | `Content-Type: application/vnd.api.v2+json` | 진정한 Content Negotiation | 복잡한 구현 | ❌ 드묾 |

> 💡 **실무 가이드**: 대부분의 팀에는 URI Path 방식(`/v1/...`)이 최선이다. 단순하고, 테스트하기 쉽고, 캐시 친화적이다.

### C. Filtering / Sorting 컨벤션

```http
# 필터링 — Query Parameter로 필드=값
GET /products?category=electronics&min_price=100&max_price=500

# 정렬 — sort 파라미터, - 접두사로 내림차순
GET /products?sort=-price,name    # 가격 내림차순 → 이름 오름차순

# 필드 선택 (Sparse Fields) — 응답 크기 최적화
GET /users?fields=id,name,email

# 검색
GET /users/search?q=kim

# 복합 예시
GET /orders?status=shipped&sort=-created_at&page=2&per_page=20
```

### D. Caching 전략

```
┌──────────┐                  ┌──────────┐                  ┌──────────┐
│  Client  │                  │  Cache   │                  │  Server  │
│          │                  │(CDN/Proxy)│                  │          │
└────┬─────┘                  └────┬─────┘                  └────┬─────┘
     │                              │                              │
     │  ①  GET /users/42            │                              │
     │─────────────────────────────►│                              │
     │                              │  Cache MISS                  │
     │                              │─────────────────────────────►│
     │                              │                              │
     │                              │  200 OK                      │
     │                              │  ETag: "abc123"              │
     │                              │  Cache-Control: max-age=60   │
     │                              │◄─────────────────────────────│
     │  200 OK (+ headers)          │                              │
     │◄─────────────────────────────│                              │
     │                              │                              │
     │  ②  GET /users/42            │  (60초 이내)                 │
     │─────────────────────────────►│                              │
     │  200 OK (from cache)         │  Cache HIT — 서버 호출 없음   │
     │◄─────────────────────────────│                              │
     │                              │                              │
     │  ③  GET /users/42            │  (60초 경과 후)              │
     │  If-None-Match: "abc123"     │                              │
     │─────────────────────────────►│                              │
     │                              │  If-None-Match: "abc123"     │
     │                              │─────────────────────────────►│
     │                              │                              │
     │                              │  304 Not Modified (변경 없음) │
     │                              │◄─────────────────────────────│
     │  304 Not Modified            │                              │
     │  (캐시된 본문 재사용)         │                              │
     │◄─────────────────────────────│                              │
```

**캐시 관련 HTTP 헤더 정리**:

| 헤더 | 방향 | 용도 | 예시 |
|------|------|------|------|
| `Cache-Control` | Response | 캐시 정책 지시 | `max-age=3600, private` |
| `ETag` | Response | 자원의 버전 식별자 | `"v1-abc123"` |
| `Last-Modified` | Response | 마지막 수정 시각 | `Thu, 22 Mar 2026 10:00:00 GMT` |
| `If-None-Match` | Request | 조건부 요청 (ETag 비교) | `"v1-abc123"` |
| `If-Modified-Since` | Request | 조건부 요청 (시각 비교) | `Thu, 22 Mar 2026 10:00:00 GMT` |
| `Vary` | Response | 캐시 키 구성 요소 명시 | `Accept, Accept-Encoding` |

### E. Rate Limiting 헤더

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000          # 윈도우당 최대 요청 수
X-RateLimit-Remaining: 997       # 남은 요청 수
X-RateLimit-Reset: 1711101600    # 윈도우 리셋 시각 (Unix timestamp)

# 한도 초과 시
HTTP/1.1 429 Too Many Requests
Retry-After: 60                  # 재시도까지 대기 시간(초)
```

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 관점 | ✅ 장점 | ❌ 단점 |
|------|---------|---------|
| **확장성** | Stateless → 서버 수평 확장 용이, 로드 밸런서 뒤에 서버 추가만 하면 됨 | 요청마다 인증 정보 전송 → 네트워크 오버헤드 |
| **단순성** | HTTP 표준 기반 → 별도 SDK 불필요, 브라우저에서도 테스트 가능 | 복잡한 쿼리나 관계형 데이터 조회 시 여러 번 요청 필요 (Over-fetching / Under-fetching) |
| **캐싱** | HTTP 캐시 인프라(CDN, 프록시) 그대로 활용 가능 | POST/PUT/DELETE는 캐시 불가 → 쓰기 작업 최적화 어려움 |
| **기술 독립성** | 프로토콜/포맷에 독립적 (JSON, XML, CSV 등 자유롭게 선택) | 표준화된 에러 포맷 부재 (RFC 7807이 있지만 강제가 아님) |
| **진화 용이성** | HATEOAS + Content Negotiation → 서버 독립적 변경 가능 | HATEOAS 구현 복잡, 실무 채택율 낮음 |
| **생태계** | OpenAPI/Swagger, Postman 등 풍부한 도구 지원 | Chatty API: 하나의 화면을 그리기 위해 N번의 API 호출 필요 |
| **학습 곡선** | HTTP만 알면 기본 사용 가능, 진입 장벽 낮음 | "진정한 REST" (Level 3)까지의 학습 곡선은 가파름 |

---

## 6️⃣ 차이점 비교 (REST vs GraphQL vs gRPC)

### 비교 매트릭스

| 기준 | REST | GraphQL | gRPC |
|------|------|---------|------|
| **프로토콜** | HTTP/1.1, HTTP/2 | HTTP (주로 POST) | HTTP/2 (필수) |
| **데이터 포맷** | JSON, XML, CSV 등 | JSON (고정) | Protocol Buffers (바이너리) |
| **스키마/계약** | OpenAPI (선택적) | GraphQL SDL (필수) | .proto 파일 (필수) |
| **타입 안전성** | ❌ 약함 (OpenAPI로 보완) | ✅ 강력한 타입 시스템 | ✅ 강력한 타입 시스템 |
| **캐싱** | ✅ HTTP 캐시 네이티브 | ❌ 어려움 (POST 기반) | ❌ 어려움 (바이너리) |
| **Over/Under-fetching** | ❌ 발생 가능 | ✅ 클라이언트가 필요한 필드만 요청 | ⚠️ 메시지 기반으로 제한적 |
| **실시간 통신** | ⚠️ SSE, WebSocket 별도 | ✅ Subscription 내장 | ✅ Bidirectional Streaming |
| **브라우저 지원** | ✅ 네이티브 | ✅ HTTP 기반 | ❌ gRPC-Web 필요 |
| **성능** | ~20K req/s* | ~15K complex req/s* | ~50K req/s* |
| **디버깅** | ✅ curl, 브라우저 직접 | ⚠️ GraphQL 전용 도구 필요 | ❌ 바이너리라 읽기 어려움 |
| **학습 곡선** | 낮음 | 중간 | 높음 |
| **파일 업로드** | ✅ multipart 네이티브 | ❌ 별도 처리 필요 | ⚠️ 스트리밍으로 가능 |

> *성능 수치는 참고용 근사치이며, 표준화된 벤치마크가 아닙니다. 실제 성능은 페이로드 크기, 직렬화 포맷, 네트워크 조건, 하드웨어, 애플리케이션 로직에 따라 크게 달라집니다. 상대적 순서(gRPC >> REST > GraphQL)는 다수의 연구에서 일관되게 보고됩니다.

### 언제 무엇을 선택할까?

```
┌─────────────────────────────────────────────────────────────────┐
│                    API 기술 선택 가이드                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Public API / Third-party 연동?                                  │
│  ├── Yes ──► REST (범용성, 도구 지원, 캐싱)                      │
│  └── No                                                          │
│       │                                                          │
│       ├── 다양한 클라이언트 + 복잡한 데이터 관계?                  │
│       │   ├── Yes ──► GraphQL (유연한 쿼리, N+1 해결)            │
│       │   └── No                                                 │
│       │                                                          │
│       └── 내부 마이크로서비스 간 통신?                             │
│           ├── 고성능 + 스트리밍 필요 ──► gRPC                     │
│           └── 단순 CRUD ──► REST (or tRPC for TypeScript)        │
│                                                                   │
│  💡 2025-2026 트렌드: 하이브리드 스택                             │
│     • Public API → REST                                          │
│     • Frontend BFF → GraphQL or tRPC                             │
│     • Internal Services → gRPC                                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

| 시나리오 | 추천 | 이유 |
|---------|------|------|
| 공개 API (제3자 소비) | **REST** | 범용성, HTTP 캐시, 풍부한 문서 도구 |
| 모바일 앱 백엔드 | **GraphQL** | Over-fetching 해결, 단일 엔드포인트 |
| 마이크로서비스 간 통신 | **gRPC** | 고성능, 양방향 스트리밍, 코드 생성 |
| 관리자 대시보드 | **REST** | 단순, CRUD에 적합, Swagger UI |
| 실시간 채팅/알림 | **gRPC** 또는 **GraphQL Subscription** | 스트리밍 네이티브 지원 |
| 레거시 시스템 통합 | **REST** | 낮은 진입 장벽, 광범위한 호환성 |

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Anti-Patterns)

### A. 흔한 실수

| 실수 | 왜 문제인가 | 올바른 방법 |
|------|------------|------------|
| URI에 동사 사용 (`/getUser`, `/createOrder`) | REST는 자원(명사) 중심, 행위는 HTTP 메서드로 표현 | `GET /users`, `POST /orders` |
| 모든 응답에 `200 OK` 반환 | 에러 상황을 구분할 수 없음, 클라이언트 에러 처리 불가 | 적절한 상태 코드 사용 (201, 204, 400, 404, 409 등) |
| `GET`으로 상태 변경 | Safe 메서드 계약 위반, 캐시/프리페치가 부작용 유발 | 상태 변경은 POST/PUT/PATCH/DELETE |
| Stateless 위반 (서버 세션 의존) | 수평 확장 어려움, 세션 동기화 필요 | JWT/토큰 기반 인증, 요청에 모든 정보 포함 |
| 중첩 URI 과도 사용 (`/a/1/b/2/c/3/d`) | URI 복잡성 증가, 커플링 심화 | 2-3단계까지만, 그 이상은 쿼리 파라미터 |
| 에러 응답에 구조 없음 | 클라이언트 에러 파싱 불가 | RFC 7807 Problem Details 사용 |

### B. Anti-Patterns

#### 1. RPC over REST ("Fake REST")
```
❌ POST /api/getUserById      → 단일 엔드포인트 + 동사
   body: {"userId": 42}

✅ GET /users/42              → 자원 중심 + HTTP 메서드
```

#### 2. God Endpoint
```
❌ POST /api
   body: {"action": "getUser", "params": {"id": 42}}
   body: {"action": "createOrder", "params": {...}}

✅ 각 자원에 개별 URI 부여
   GET /users/42
   POST /orders
```

#### 3. Chatty API (N+1 API 호출 문제)
```
❌ 화면 하나에 5번의 API 호출
   GET /users/42
   GET /users/42/profile
   GET /users/42/orders
   GET /users/42/notifications
   GET /users/42/preferences

✅ 해결 방법
   1. 복합 응답: GET /users/42?include=profile,orders
   2. BFF 패턴: Backend-for-Frontend에서 집계
   3. GraphQL 도입 검토
```

### C. Security Checklist

| 영역 | 실천 사항 |
|------|----------|
| **인증** | OAuth 2.0 / JWT Bearer Token, API Key는 보조 수단으로만 |
| **인가** | 자원 레벨 접근 제어 (RBAC / ABAC) |
| **CORS** | 허용된 origin만 명시적으로 허용, `*` 금지 |
| **입력 검증** | 모든 입력에 Pydantic 검증, SQL Injection / XSS 방지 |
| **Rate Limiting** | IP/토큰 기반 요청 제한, `429 Too Many Requests` 반환 |
| **HTTPS** | 프로덕션에서 TLS 필수, HTTP → HTTPS 리다이렉트 |
| **민감 데이터** | 응답에 비밀번호/토큰 노출 금지, 로그에 PII 제외 |
| **헤더 보안** | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` |

---

## 8️⃣ 개발자가 알아둬야 할 것들

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|------|------|----------|
| 📖 논문 (원전) | Fielding Dissertation, Chapter 5 | [roy.gbiv.com](https://roy.gbiv.com/pubs/dissertation/rest_arch_style.htm) — REST를 정의한 원전, 필독 |
| 📘 도서 | *RESTful Web APIs* (Leonard Richardson, Mike Amundsen) | O'Reilly — REST + HATEOAS 실무 가이드 |
| 📘 도서 | *REST API Design Rulebook* (Mark Massé) | O'Reilly — URI 설계, 메서드 선택 규칙 |
| 📄 표준 | RFC 9110 (HTTP Semantics) | [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110) — HTTP 메서드·상태 코드 정의 (RFC 7231 대체) |
| 📄 표준 | RFC 9457 (Problem Details) | [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457) — RFC 7807 업데이트, 에러 응답 표준 |
| 📄 표준 | RFC 9110 §8.8 (Conditional Requests) | ETag, If-None-Match, If-Modified-Since 명세 |
| 📝 블로그 | Richardson Maturity Model (Martin Fowler) | [martinfowler.com](https://martinfowler.com/articles/richardsonMaturityModel.html) |
| 📝 블로그 | REST API Tutorial | [restfulapi.net](https://restfulapi.net/) — 종합 가이드 |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리 | 언어/플랫폼 | 용도 |
|---------------|-----------|------|
| **FastAPI** | Python | 고성능 비동기 REST API 프레임워크, OpenAPI 자동 생성 |
| **SQLModel** | Python | SQLAlchemy + Pydantic 통합 ORM (FastAPI 공식 추천) |
| **fastapi-hypermodel** | Python/PyPI | [HATEOAS 링크 자동 생성](https://github.com/jtc42/fastapi-hypermodel) (HAL, Siren 지원) |
| **httpx** | Python | 비동기 HTTP 클라이언트 (REST API 테스트/소비) |
| **Swagger UI / ReDoc** | Web | FastAPI 내장 OpenAPI 문서 브라우저 |
| **Postman** | Cross-platform | API 테스트, 문서화, 모니터링 |
| **Bruno** | Cross-platform | Git 친화적 오픈소스 API 클라이언트 (Postman 대안) |
| **Hoppscotch** | Web | 경량 오픈소스 API 테스트 도구 |

### 🔮 트렌드 & 전망 (2025-2026)

- **하이브리드 API 스택**: REST + GraphQL + gRPC를 계층별로 조합하는 것이 2026년 표준 접근법으로 자리잡음
- **OpenAPI 3.1**: JSON Schema와 완전 호환, Webhooks 지원 추가
- **JSON:API & HAL**: HATEOAS를 표준화하려는 시도가 지속되지만, 광범위한 채택까지는 도달하지 못함
- **REST + SSE**: Server-Sent Events를 통한 실시간 업데이트 패턴이 WebSocket 대안으로 부상
- **API-First Design**: OpenAPI 스펙을 먼저 작성하고 코드를 생성하는 Contract-First 접근법이 확산
- **AI와 API**: LLM Agent가 REST API를 직접 호출하는 패턴 증가 → OpenAPI 스펙의 중요성 더욱 부각

### 💬 커뮤니티 인사이트

- "HATEOAS는 이론적으로 아름답지만, 실무에서 구현하는 팀은 극소수다. Level 2 REST + 좋은 문서가 대부분의 팀에게 최선이다." — 커뮤니티 공통 의견
- "REST vs GraphQL 논쟁은 끝났다. 답은 '둘 다'다. 공개 API는 REST, 프론트엔드 BFF는 GraphQL." — 2025-2026 트렌드
- "gRPC의 50K req/s vs REST의 20K req/s 벤치마크는 인상적이지만, 대부분의 앱은 1K req/s도 안 된다. 기술 선택의 핵심은 성능이 아니라 팀의 경험과 생태계다." — 실무 관점

---

## 📎 Sources

1. [Fielding Dissertation, Chapter 5 — REST](https://roy.gbiv.com/pubs/dissertation/rest_arch_style.htm) — 공식 원전 (2000)
2. [Richardson Maturity Model (Martin Fowler)](https://martinfowler.com/articles/richardsonMaturityModel.html) — 성숙도 모델 원전
3. [HATEOAS Guide (pradeepl.com)](https://pradeepl.com/blog/rest/hateoas/) — HATEOAS 실무 가이드
4. [REST API Design Best Practices 2026 (Codebrand)](https://www.codebrand.us/blog/rest-api-design-best-practices-2026/) — 최신 베스트 프랙티스
5. [REST API Best Practices (Postman Blog)](https://blog.postman.com/rest-api-best-practices/) — Postman 공식 가이드
6. [GraphQL vs REST vs gRPC 2026 (Java Code Geeks)](https://www.javacodegeeks.com/2026/02/graphql-vs-rest-vs-grpc-the-2026-api-architecture-decision.html) — 기술 비교
7. [REST vs GraphQL vs gRPC 2026 (Pockit)](https://pockit.tools/blog/rest-graphql-trpc-grpc-api-comparison-2026/) — 하이브리드 스택 가이드
8. [fastapi-hypermodel (GitHub)](https://github.com/jtc42/fastapi-hypermodel) — FastAPI HATEOAS 라이브러리
9. [HTTP Caching — MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching) — 캐싱 공식 문서
10. [ETag — MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/ETag) — ETag 공식 문서
11. [RFC 9457 — Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457) — 에러 응답 표준
12. [REST — Wikipedia](https://en.wikipedia.org/wiki/REST) — 참고 자료

---

## 📊 Research Metadata

```yaml
research_metadata:
  protocol: Deep Research (3-Phase)
  date: 2026-03-22
  search_queries: 8 (일반 6 + SNS 2)
  sources_collected: 12
  source_types:
    official_docs: 3 (Fielding 논문, MDN, RFC)
    primary_sources: 2 (Martin Fowler, fastapi-hypermodel)
    tech_blogs: 5 (Codebrand, Postman, pradeepl, Java Code Geeks, Pockit)
    community: 2 (Wikipedia, Reddit 시도 — 결과 없음)
  webfetch_verifications: 4
    - Fielding Dissertation Ch.5 (6 constraints + 4 sub-constraints 원문 확인)
    - Martin Fowler Richardson Maturity Model (Level 0-3 정의 확인)
    - fastapi-hypermodel GitHub README (HAL/Siren 포맷 확인)
    - REST API Design Best Practices 2026 (URI/versioning/pagination 확인)
  confidence_distribution:
    confirmed: 8 (REST constraints, RMM levels, HTTP methods, caching)
    likely: 3 (performance benchmarks, trend predictions)
    synthesized: 1 (hybrid stack recommendation)
  sns_search: Reddit 2회 시도, 관련 결과 없음
  concept_analysis: 8-perspective analysis integrated into document sections
```
