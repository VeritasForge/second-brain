---
created: 2026-04-21
source: claude-code
tags: [javascript, typescript, testing, vitest, jest, playwright, testing-library, type-testing]
---

# 📖 JS/TS 테스팅 패턴 — Vitest부터 E2E까지

> 💡 **한줄 요약**: JS/TS 테스팅은 Vitest/Jest(단위) + Testing Library(DOM) + Playwright(E2E) + tsd(타입 테스트)의 4계층으로 구성되며, 프론트엔드+백엔드 양쪽을 커버하는 유일한 테스트 생태계다.
>
> 📌 **핵심 키워드**: Vitest, Testing Library, Playwright, MSW, tsd, testcontainers-node
> 📅 **기준**: Vitest 2.x / Playwright 1.x (2025)

---

## 1️⃣ Vitest / Jest 기본

```typescript
import { describe, it, expect, vi } from "vitest";

describe("UserService", () => {
    it("should return user by id", async () => {
        const repo = { findById: vi.fn().mockResolvedValue({ name: "TS" }) };
        const svc = new UserService(repo);
        
        const user = await svc.getUser(1);
        
        expect(user.name).toBe("TS");
        expect(repo.findById).toHaveBeenCalledWith(1);
    });
    
    // 테이블 드리븐
    it.each([
        [2, 3, 5],
        [-1, 3, 2],
        [0, 0, 0],
    ])("add(%i, %i) = %i", (a, b, expected) => {
        expect(add(a, b)).toBe(expected);
    });
});
```

### Vitest vs Jest

| 특성 | Vitest | Jest |
|------|--------|------|
| 속도 | ⚡ (Vite 기반 HMR) | 보통 |
| ESM 지원 | ✅ 네이티브 | 설정 필요 |
| TS 지원 | ✅ 별도 설정 없음 | ts-jest 필요 |
| 호환성 | Jest API 호환 | 표준 |
| 추세 | 신규 프로젝트 권장 | 레거시 유지 |

---

## 2️⃣ Testing Library (DOM 테스트)

```typescript
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

test("should submit form", async () => {
    const onSubmit = vi.fn();
    render(<LoginForm onSubmit={onSubmit} />);
    
    // 사용자 관점에서 테스트 (구현 세부사항 아닌 행동)
    await userEvent.type(screen.getByLabelText("이메일"), "test@test.com");
    await userEvent.type(screen.getByLabelText("비밀번호"), "password");
    await userEvent.click(screen.getByRole("button", { name: "로그인" }));
    
    expect(onSubmit).toHaveBeenCalledWith({
        email: "test@test.com",
        password: "password",
    });
});
```

> **핵심 원칙**: "사용자가 보는 것을 테스트하라" — `getByRole`, `getByLabelText` 우선, `getByTestId`는 최후 수단.

---

## 3️⃣ E2E 테스트 (Playwright)

```typescript
import { test, expect } from "@playwright/test";

test("사용자 로그인 플로우", async ({ page }) => {
    await page.goto("/login");
    
    await page.getByLabel("이메일").fill("test@test.com");
    await page.getByLabel("비밀번호").fill("password");
    await page.getByRole("button", { name: "로그인" }).click();
    
    await expect(page.getByText("환영합니다")).toBeVisible();
    await expect(page).toHaveURL("/dashboard");
});

test("스크린샷 비교 (Visual Regression)", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveScreenshot("dashboard.png");
});
```

---

## 4️⃣ API 테스트 (Backend)

### Supertest (Express/Fastify)

```typescript
import request from "supertest";

test("GET /users/:id returns user", async () => {
    const res = await request(app)
        .get("/users/1")
        .expect(200);
    
    expect(res.body.name).toBe("TS");
});
```

### MSW (Mock Service Worker) — API 모킹

```typescript
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

const server = setupServer(
    http.get("/api/users/:id", ({ params }) => {
        return HttpResponse.json({ name: "TS", id: params.id });
    }),
);

beforeAll(() => server.listen());
afterAll(() => server.close());

test("fetches user", async () => {
    const user = await fetchUser(1);
    expect(user.name).toBe("TS");
});
```

---

## 5️⃣ Testcontainers

```typescript
import { PostgreSqlContainer } from "@testcontainers/postgresql";

let container: StartedPostgreSqlContainer;

beforeAll(async () => {
    container = await new PostgreSqlContainer("postgres:16-alpine").start();
    process.env.DATABASE_URL = container.getConnectionUri();
});

afterAll(async () => {
    await container.stop();
});
```

---

## 6️⃣ 타입 테스트 (TS 고유)

```typescript
// expect-type 라이브러리
import { expectTypeOf } from "expect-type";

test("utility types work correctly", () => {
    type User = { name: string; age: number; email: string };
    
    expectTypeOf<Pick<User, "name">>().toEqualTypeOf<{ name: string }>();
    expectTypeOf<Partial<User>>().toMatchTypeOf<{ name?: string }>();
});
```

```typescript
// tsd: .d.ts 파일 기반
// index.test-d.ts
import { expectType, expectError } from "tsd";
import { myFunc } from "./index";

expectType<string>(myFunc("hello"));
expectError(myFunc(42));  // 숫자 인자는 에러여야 함
```

> 타입 테스트는 **JS/TS에만 존재하는 고유한 테스트 패턴** — 라이브러리 작성자가 타입 정의의 정확성을 검증.

---

## 7️⃣ 테스트 조직

```
src/
├── components/
│   ├── UserProfile.tsx
│   └── UserProfile.test.tsx    ← 컴포넌트 옆 배치 (co-location)
├── services/
│   ├── userService.ts
│   └── userService.test.ts
├── __tests__/                  ← 통합/E2E 테스트
│   └── api/
tests/
├── e2e/                        ← Playwright E2E
│   └── login.spec.ts
└── fixtures/
    └── users.json
```

### 🔄 4개 언어 비교

| 개념 | JS/TS | Go | Python | Kotlin |
|------|-------|-----|--------|--------|
| 단위 테스트 | Vitest/Jest | testing (내장) | pytest | JUnit 5 |
| DOM 테스트 | Testing Library | 없음 | 없음 | 없음 |
| E2E | Playwright | 없음 | Playwright | Selenium |
| 타입 테스트 | tsd/expect-type | 없음 | 없음 | 없음 |
| API 모킹 | MSW | httptest | responses | MockK |

---

## 📎 출처

1. [Vitest Documentation](https://vitest.dev/) — 공식 문서
2. [Testing Library](https://testing-library.com/) — DOM 테스트 공식
3. [Playwright Documentation](https://playwright.dev/) — E2E 공식

---

> 📌 **이전 문서**: [[05-js-ts-developer-essentials-by-seniority]]
> 📌 **다음 문서**: [[07-js-ts-project-structure-and-tooling]]
