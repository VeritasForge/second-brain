---
tags: [security, idor, access-control, owasp, authorization, broken-access-control, concept-explainer]
created: 2026-06-04
---

# IDOR (Insecure Direct Object Reference) — Concept Deep Dive

> **한줄 요약**: IDOR는 서버가 사용자 제공 식별자를 **소유권 검증 없이 직접** 데이터 계층에 전달하여, 인증된 사용자가 타인의 객체에 접근할 수 있게 되는 접근 제어 취약점이다. 핵심은 "인가(Authorization) 검증 누락"이다.

---

## 1. 무엇인가? (What is it?)

IDOR (Insecure Direct Object Reference, 불안전한 직접 객체 참조)는 **애플리케이션이 내부 객체(데이터베이스 레코드, 파일, 사용자 ID 등)를 직접 URL이나 파라미터로 노출하고, 해당 사용자가 그 객체에 실제로 접근할 권한이 있는지 검증하지 않을 때** 발생하는 취약점이다.

- OWASP Top 10 2025에서 **A01: Broken Access Control (깨진 접근 제어)** 내 대표적 예시 중 하나 `[Confirmed]` — [OWASP Top 10 2025 A01](https://owasp.org/Top10/2025/A01_2025-Broken_Access_Control/) (A01에는 40+ CWE가 매핑되며, IDOR는 명시적으로 열거된 패턴임)
- 웹 취약점 중 발견 빈도가 높고, 버그바운티 보고서에 단골로 등장

### 현실 세계 비유 (12살도 이해할 수 있는 버전)

**도서관 사물함**을 떠올려보자.

- 도서관에 입장(로그인)하면 사물함 번호 `1234`를 배정받는다
- 다른 학생의 사물함은 `1235`, `1236`...으로 순서대로 번호가 붙어있다
- **나쁜 도서관**: "도서관에 입장한 사람은 누구나 모든 사물함을 열 수 있다" (인증만 확인)
- **좋은 도서관**: "도서관에 입장했더라도, **본인의 사물함 번호**를 직원에게 확인받아야만 열 수 있다" (인가까지 확인)

IDOR는 "나쁜 도서관"처럼 번호만 바꾸면 남의 사물함이 열리는 상황이다.

---

## 2. 인증 vs 인가 — 핵심 구분

IDOR를 이해하려면 이 두 개념을 반드시 구분해야 한다:

| 개념 | 영어 | 질문 | 예시 |
|------|------|------|------|
| **인증** | Authentication | "너 누구야?" | 로그인 성공 여부 |
| **인가** | Authorization | "너 이걸 해도 돼?" | 해당 데이터 접근 권한 |

```
❌ IDOR 취약 서버의 논리:
   Request: GET /api/orders/9999
   ├── "이 요청자가 로그인했는가?" → Yes ✅
   └── 데이터 반환! (9999번 주문이 내 것인지 확인 안 함 🚨)

✅ 안전한 서버의 논리:
   Request: GET /api/orders/9999
   ├── "이 요청자가 로그인했는가?" → Yes ✅
   ├── "9999번 주문의 소유자가 이 사람인가?" → 확인 ✅
   └── 일치 → 데이터 반환 / 불일치 → 403 Forbidden
```

---

## 3. 공격 벡터 (Attack Vectors)

IDOR는 다양한 위치에서 발생한다. `[Confirmed]` — [MDN Web Security](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/IDOR), [PortSwigger](https://portswigger.net/web-security/access-control/idor)

### 3-1. URL 경로 파라미터

```
# 공격자의 요청: URL의 ID만 바꿔서 남의 데이터 접근
GET /api/users/1234/profile   ← 내 계정
GET /api/users/1235/profile   ← 타인 계정 (그냥 1 증가)
```

### 3-2. 쿼리 스트링

```
GET /orders?order_id=9999
GET /download?file_id=42
```

### 3-3. POST 요청 바디

```json
POST /api/update-email
{
  "user_id": 1234,   ← 이 값을 조작
  "email": "hacker@evil.com"
}
```

### 3-4. 숨겨진 폼 필드 (Hidden Form Field)

```html
<!-- 클라이언트에서 개발자 도구로 값 변경 가능 -->
<form action="/updateProfile" method="POST">
  <input type="hidden" name="user_id" value="1234" />
  <button type="submit">프로필 수정</button>
</form>
```

### 3-5. 파일 경로 추측

```
# 순차적 파일명 → 손쉬운 열거(Enumeration)
/static/reports/2024-01-report.pdf
/static/reports/2024-02-report.pdf
/api/invoices/12144.pdf
/api/invoices/12145.pdf
```

### 3-6. 쿠키/헤더

```http
Cookie: user_id=1234
X-User-Id: 1234
```

---

## 4. 권한 상승 유형

PortSwigger에 따르면 IDOR로 인한 권한 상승은 두 방향으로 발생한다. `[Confirmed]`

```
┌─────────────────────────────────────────────────┐
│              권한 상승 유형                       │
├─────────────────────────────────────────────────┤
│                                                  │
│  수평적 권한 상승 (Horizontal Privilege Escalation)│
│  ┌──────┐   IDOR   ┌──────┐                     │
│  │ 일반  │ ──────→ │ 다른  │  같은 권한 레벨이지만  │
│  │유저 A│          │유저 B│  타인의 데이터 접근    │
│  └──────┘          └──────┘                     │
│                                                  │
│  수직적 권한 상승 (Vertical Privilege Escalation)  │
│  ┌──────┐   IDOR   ┌──────┐                     │
│  │ 일반  │ ──────→ │ 관리  │  더 높은 권한 레벨로  │
│  │ 유저  │          │  자  │  상승                │
│  └──────┘          └──────┘                     │
│                                                  │
│  복합형 (Combined)                               │
│  수평 접근으로 관리자 계정 발견 → 수직 상승으로 활용│
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## 5. 취약 코드 vs 안전 코드

### 5-1. 취약한 예제 (Node.js)

```javascript
// ❌ BAD: 인증(req.isAuthenticated)만 확인, 인가 없음
app.get("/api/orders/:orderId", (req, res) => {
  if (!req.isAuthenticated()) return res.status(401).send("Unauthorized");

  // req.params.orderId가 이 사용자의 것인지 전혀 확인하지 않음!
  const order = db.orders.findById(req.params.orderId);
  res.json(order);
});
```

### 5-2. 안전한 예제 (Node.js)

```javascript
// ✅ GOOD: 인증 + 인가 모두 확인
app.get("/api/orders/:orderId", (req, res) => {
  if (!req.isAuthenticated()) return res.status(401).send("Unauthorized");

  // 현재 로그인한 유저 소유의 주문 중에서만 조회
  const order = db.orders.findOne({
    id: req.params.orderId,
    userId: req.session.userId  // ← 반드시 현재 사용자로 범위 제한
  });

  if (!order) return res.status(403).send("Forbidden");
  res.json(order);
});
```

### 5-3. 안전한 예제 (Python/Django ORM)

```python
# ✅ GOOD (Object-Level Authorization): Django ORM으로 소유권 검증
def get_order(request, order_id):
    # id=order_id AND user=request.user → 다른 유저 주문은 404 반환
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # ⚠️ Field-Level Authorization은 별도 보장 필요:
    #    to_dict()가 결제수단·배송이력 등 민감 연관 필드를 노출하지 않는지 확인할 것.
    #    연관 객체 직렬화 시 필드별 접근 제어가 추가로 요구된다.
    return JsonResponse(order.to_dict())
```

---

## 6. 실제 사례

`[Likely]` — 보안 블로그 및 CVE 기록 기반

| 사례 | 영향 | CVSS |
|------|------|------|
| **CVE-2025-27507** — ZITADEL Admin API IDOR | LDAP 설정 변경을 통한 계정 탈취 | 9.0 |
| **CVE-2025-13526** — WordPress OneClick Chat to Order (≤1.0.8) | 다른 고객 주문 정보 열람 (이름/이메일/주소), 비인증 접근 가능 | 7.5 |
| **CVE-2024-28320** — Hospital Management System | 환자 데이터 읽기/수정 | 7.6 |
| **CVE-2024-46528** — KubeSphere | 저권한 사용자의 클러스터·노드·계정 정보 무단 접근 | 4.9 |
| **CVE-2025-25282** — RAGFlow | 크로스 테넌트 사용자 목록 열람 및 계정 추가 | 8.1 |
| HackerOne — Shopify | 보조 플로우에서 인가 검증 누락 `[Unverifiable]` | - |

> 💡 **패턴**: 순차적 ID(정수, 파일명 등)를 사용하면 자동화 스크립트로 대량 열거가 가능해 피해가 더 심각해진다.

---

## 7. 예방 기법

`[Confirmed]` — [OWASP IDOR Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html)

### 7-1. (필수) 서버 사이드 인가 검증

```
모든 객체 접근마다 반드시:
"현재 인증된 사용자가 이 특정 객체에 접근할 권한이 있는가?"
를 서버에서 확인한다.
```

**클라이언트 사이드 숨기기로는 절대 충분하지 않다.** 개발자 도구로 즉시 우회 가능.

### 7-2. (권장) 예측 불가능한 식별자 사용

```
# BAD: 순차적 정수 → 열거 공격(Enumeration) 쉬움
/api/users/1
/api/users/2
/api/users/3

# GOOD: UUID → 열거 사실상 불가능
/api/users/550e8400-e29b-41d4-a716-446655440000
```

> ⚠️ **중요**: UUID는 **추가 방어(Defense in Depth)** 수단이지, 인가 검증을 **대체하지 않는다**. UUID를 써도 인가 없이 수락하면 IDOR는 그대로 존재한다. `[Confirmed]` — OWASP Cheat Sheet

### 7-3. (권장) 간접 참조 맵 (Indirect Reference Map)

```
사용자에게 노출되는 ID ≠ 내부 DB의 실제 ID
세션마다 임시 매핑 테이블을 사용하여 실제 ID를 감춘다.

예:
  세션 매핑: { "token_abc": 1234 }
  URL:       GET /orders/token_abc
  서버 처리: 세션에서 token_abc → 1234로 해석 후 현재 유저 검증
```

> ⚠️ **멀티서버 환경 주의**: 세션 기반 매핑은 수평 확장(scale-out) 시 세션 공유 스토리지(Redis 등)가 없으면 다른 서버로 라우팅된 요청에서 매핑을 찾지 못하는 문제가 생긴다. 서버 사이드 인가 검증이 충분히 구현된 경우 간접 참조 맵 없이도 충분하다.

### 7-4. (권장) 식별자 노출 최소화

가능하면 URL/바디에 아예 ID를 넣지 않는다:

```javascript
// 파라미터로 ID 받는 대신, 세션에서 현재 사용자 정보만 사용
app.get("/api/my-profile", (req, res) => {
  const user = db.users.findById(req.session.userId); // 세션 기반
  res.json(user);
});
```

### 요약 매트릭스

| 기법 | 효과 | 단독으로 충분한가? |
|------|------|----------------|
| ✅ 서버 사이드 인가 검증 | 근본적 해결 | **Yes** (필수) |
| 🔑 UUID 사용 | 열거 공격 방지 | No (인가 검증 보완) |
| 🗺️ 간접 참조 맵 | 실제 ID 은닉 | No (인가 검증 보완) |
| 🙈 ID 노출 최소화 | 공격 표면 축소 | No (인가 검증 보완) |
| 🛡️ PostgreSQL RLS | 개발자 실수 자동 차단 | No (인가 검증 보완, 마지막 방어선) |

### 7-5. (심층 방어) PostgreSQL RLS (Row-Level Security)

PostgreSQL 9.5+에서 제공하는 기능으로, **테이블 정책에 "보이지 않는 WHERE 절"을 한 번만 정의하면 DB 엔진이 모든 쿼리에 자동으로 삽입**한다. 앱 코드에서 인가 체크를 빠뜨려도 DB 차원에서 차단된다. → 자세한 내용: [[postgresql-row-level-security]]

> 💡 **IDOR와의 연결**: IDOR의 근본 원인은 "개발자가 `AND user_id = :me`를 빠뜨리는 것"이다. RLS는 이 망각을 DB 레벨에서 보완한다.

**동작 방식 — "보이지 않는 WHERE" 자동 삽입**

```
   개발자가 실수로 소유권 체크를 누락한 쿼리:
   SELECT * FROM orders WHERE id = 9999;
            │
            ▼ PostgreSQL RLS 정책 주입
   SELECT * FROM orders WHERE id = 9999
     AND user_id = 'current-user-uuid';  ← DB가 자동 삽입 ✅
```

**최소 적용 예시**

```sql
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders FORCE ROW LEVEL SECURITY;  -- 테이블 소유자도 우회 금지

CREATE POLICY orders_owner_policy ON orders
  USING (user_id = current_setting('app.current_user')::uuid);

-- 트랜잭션마다 컨텍스트 주입 (SET LOCAL: 커넥션 풀 안전)
BEGIN;
  SET LOCAL app.current_user = '사용자-UUID';
  SELECT * FROM orders WHERE id = 9999;  -- 자동으로 내 주문만 반환
COMMIT;
```

**RLS가 IDOR를 막는 범위**

| 시나리오 | RLS 방어 | 이유 |
|---------|---------|------|
| 개발자가 `WHERE user_id` 누락 | ✅ 막음 | DB 자동 필터 |
| 새 API 엔드포인트 추가 시 누락 | ✅ 막음 | 테이블 정책 자동 적용 |
| 다른 서비스가 직접 DB 접근 | ✅ 막음 | 접근 경로 무관하게 강제 |
| `superuser`/테이블 소유자 접속 | ❌ 못 막음 | RLS 우회 특권 역할 (`FORCE ROW LEVEL SECURITY` 필수) |
| VIEW를 통한 접근 (PG15 미만) | ❌ 못 막음 | VIEW가 생성자 권한으로 실행 |
| 컬럼 단위 노출 (FLA) | ❌ 못 막음 | RLS는 행(row) 단위만 제어 |

> ⚠️ **RLS는 최후 방어선이지, 앱 레벨 인가를 대체하지 않는다.** 복잡한 권한 로직(RBAC, ABAC 등)은 여전히 앱에서 처리해야 한다. Supabase도 "RLS + 앱 레벨 인가" 둘 다 적용하는 Defense in Depth를 실무 표준으로 권장한다.

---

## 8. 탐지 방법

### 8-1. 수동 테스트 (Pen Test)

```
1. 계정 A로 로그인 → 자신의 리소스 ID 기록
2. 계정 B로 로그인 → 계정 A의 ID로 요청 시도
3. 성공하면 IDOR 존재
```

### 8-2. 자동화 도구

| 도구 | 유형 | 특징 |
|------|------|------|
| Burp Suite | DAST | Intruder/Repeater로 ID 열거 자동화 |
| OWASP ZAP | DAST | 무료 오픈소스 스캐너 |
| Postman | 수동 + 자동 | API 테스트에서 ID 조작 |
| Custom Scripts | 자동화 | 대량 열거 스크립트 작성 |

> ⚠️ **주의**: 기존 DAST 도구는 비즈니스 로직 기반 IDOR를 잘 탐지하지 못한다. 수동 테스트 + 코드 리뷰 병행이 필수. `[Likely]` — [APIiro](https://apiiro.com/blog/why-dast-tools-miss-real-idor-vulnerabilities-and-how-ai-helps/)

### 8-3. 코드 리뷰 체크포인트

```
아래 패턴을 발견하면 인가 검증이 있는지 반드시 확인:
- db.findById(req.params.id)
- db.find(req.query.id)
- File.open(req.params.filename)
```

---

## 9. IDOR vs 관련 취약점 비교

| 취약점 | 핵심 문제 | 공격 대상 |
|--------|----------|----------|
| **IDOR** | 인가 검증 누락 | 다른 사용자의 객체 |
| **Path Traversal** | 파일 경로 조작 | 서버 파일 시스템 |
| **Broken Auth** | 인증 메커니즘 결함 | 세션/토큰 탈취 |
| **Mass Assignment** | 모델 바인딩 미검증 | 객체 속성 무단 수정 |
| **Forced Browsing** | 숨겨진 URL 직접 접근 | 미인가 기능 접근 |

---

## 10. 면접 Q&A

**Q. IDOR와 인증 취약점의 차이점은?**
> 인증 취약점은 "로그인을 우회하는" 문제이고, IDOR는 "로그인은 했지만 권한 없는 데이터에 접근하는" 문제다. IDOR는 인증이 정상적으로 작동해도 발생한다.

**Q. UUID를 쓰면 IDOR가 해결되는가?**
> 아니다. UUID는 열거(enumeration) 공격을 어렵게 만들 뿐이다. UUID를 받아도 서버가 해당 UUID가 현재 사용자의 것인지 검증하지 않으면 IDOR는 여전히 존재한다.

**Q. IDOR는 어느 OWASP 카테고리인가?**
> OWASP Top 10 2021/2025 A01: Broken Access Control (깨진 접근 제어)에 해당한다.

**Q. PostgreSQL RLS (Row-Level Security)로 IDOR를 완전히 방지할 수 있는가?**
> 상당히 보완하지만 완전하지는 않다. RLS는 개발자가 인가 체크를 빠뜨려도 DB가 자동으로 소유권 필터를 삽입하는 "마지막 방어선"이다. 다만 superuser/테이블 소유자 접속, VIEW를 통한 우회, 컬럼 단위 FLA(Field-Level Authorization)는 별도로 처리해야 한다. 앱 레벨 인가와 RLS를 함께 쓰는 Defense in Depth가 실무 표준이다.

---

## 📎 참고 출처

1. [OWASP — IDOR Community Page](https://owasp.org/www-community/attacks/insecure_direct_object_reference) — 공식 문서
2. [OWASP — IDOR Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html) — 공식 예방 가이드
3. [PortSwigger Web Security Academy — IDOR](https://portswigger.net/web-security/access-control/idor) — 실습 포함 심화 설명
4. [MDN Web Security — IDOR](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/IDOR) — 코드 예제 포함
5. [OWASP — IDOR Testing Guide](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References) — 테스트 방법론
