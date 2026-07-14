---
tags: [nextjs, app-router, route-group, layout]
created: 2026-07-14
---

# Next.js 라우트 그룹 (Route Group) 정리

## 1. 라우트 그룹이란?

`app/(auth)`, `app/(main)`처럼 폴더명을 괄호로 감싸면 **Next.js App Router (Next.js 프레임워크의 파일 기반 라우팅 시스템)** 가 이를 "라우트 그룹"으로 인식한다. 핵심 특징은 **URL 경로에는 전혀 나타나지 않으면서, 그 하위 라우트들끼리 별도의 레이아웃(layout)을 공유**하게 해준다는 점이다.

### 실제 프로젝트 구조 예시

```
app/
├── layout.tsx              ← 전체 공통 레이아웃 (최상위)
├── (auth)/                 ← URL에 안 나타남, 그룹 이름일 뿐
│   ├── layout.tsx          ← 로그인용 레이아웃
│   ├── login/
│   └── signup/
│       └── verify/
└── (main)/                 ← URL에 안 나타남, 그룹 이름일 뿐
    ├── layout.tsx          ← 서비스 화면용 레이아웃 (Sidebar + MobileNav)
    ├── page.tsx
    ├── tasks/
    ├── categories/
    ├── history/
    ├── statistics/
    ├── strategies/
    └── settings/
```

### URL과의 관계

| 실제 파일 경로                        | 브라우저 URL                        |
| -------------------------------------- | ------------------------------------ |
| `app/(auth)/login/page.tsx`            | `/login` (auth는 URL에서 사라짐)     |
| `app/(main)/tasks/page.tsx`            | `/tasks` (main도 URL에서 사라짐)     |

즉, 괄호 폴더는 "이 페이지들을 이런 레이아웃 묶음으로 관리하겠다"는 조직화 표시일 뿐, 사용자가 보는 주소창에는 흔적이 남지 않는다.

## 2. 핵심 용도: 레이아웃 공유

프로젝트에서 확인한 두 레이아웃 파일:

```tsx
// (auth)/layout.tsx
export default function AuthLayout({ children }) {
  return <>{children}</>;   // 껍데기만 통과 — 사이드바/네비게이션 없음
}
```

```tsx
// (main)/layout.tsx
import { Sidebar } from "@/components/layout/sidebar";
import { MobileNav } from "@/components/layout/mobile-nav";

// Auth gate: 모든 (main) 라우트는 proxy.ts middleware로 보호됨.
// 비로그인 사용자는 /login으로 redirect (matcher: api/_next/* 제외 전부).
// proxy.ts 매처가 변경되면 settings/dashboard 등이 노출될 수 있으니 함께 검토 필수.
export default function MainLayout({ children }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 pb-16 md:pb-0">
        <div className="mx-auto max-w-4xl p-4 md:p-6">{children}</div>
      </main>
      <MobileNav />
    </div>
  );
}
```

### 요청 처리 순서도

```
요청: GET /tasks
        │
        ▼
  app/layout.tsx (최상위, 항상 적용)
        │
        ▼
  이 경로가 어느 그룹에 속하나?
        │
   ┌────┴────┐
   │         │
 (auth)?   (main)?
   │         │
   ▼         ▼
껍데기만   Sidebar+MobileNav
 통과       로 감싸서 렌더
```

> 💡 **보안 관련 주의사항**: `(main)/layout.tsx`의 주석에 따르면, `(main)` 그룹은 단순 레이아웃 분리 용도만이 아니라 **인증 게이트(auth gate)의 경계선** 역할도 겸한다. `proxy.ts`의 matcher 설정이 바뀌면 `/settings`, `/statistics` 등이 로그인 없이 노출될 위험이 있으므로, 이 그룹 구조를 건드릴 때는 `proxy.ts`의 matcher도 함께 검토해야 한다.

## 3. 라우트 그룹 vs 일반 폴더 — 왜 괄호가 필요한가

`app/auth/layout.tsx` + `app/auth/login/page.tsx`처럼 **괄호 없는 일반 폴더**로도 레이아웃 분리 자체는 기술적으로 가능하다. 문제는 그렇게 하면 `auth`라는 이름이 실제 URL 경로에 그대로 노출된다는 점이다.

| 방식                        | 파일 경로                          | 결과 URL                            |
| --------------------------- | ----------------------------------- | ------------------------------------ |
| **일반 폴더** `auth/`       | `app/auth/login/page.tsx`           | `/auth/login` (auth가 경로에 남음)   |
| **라우트 그룹** `(auth)`    | `app/(auth)/login/page.tsx`         | `/login` (auth가 사라짐)             |

```
목표: 레이아웃만 분리하고 싶다, URL엔 흔적 남기기 싫다
        │
        ├─ 일반 폴더(auth/) 사용 → 레이아웃 분리는 되지만 URL에 /auth가 강제로 붙음 ❌
        │
        └─ 괄호 폴더((auth)) 사용 → 레이아웃 분리 + URL 그대로 유지 ✅
```

이 프로젝트는 `/login`, `/signup`처럼 짧고 직관적인 URL을 원하는 제품 요구사항이 있어서, 일반 폴더가 아닌 괄호 문법(라우트 그룹)을 택한 것이다.

## 4. 정확한 개념 정리 — 흔한 오해 교정

| 오해하기 쉬운 것                                          | 실제 동작                                                                                       |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| "그룹으로 묶으면 라우팅 로직도 하나로 합쳐진다"            | ❌ 아님. `/login`, `/tasks`는 여전히 **완전히 독립된 라우트**로 각자 동작                        |
| "그룹 폴더는 URL 경로 세그먼트 하나를 차지한다"            | ❌ 아님. `(auth)`, `(main)`은 URL 계산에서 **완전히 무시**됨                                     |
| "그룹은 단지 파일시스템상 정리(organization) 장치다"       | ✅ 맞음. 라우팅 자체엔 영향 없고, 같은 그룹에 속한 페이지들끼리 레이아웃 등 **부가 설정을 공유** |

> 한 줄 요약: 라우트 그룹은 "라우팅을 묶는" 게 아니라 **"URL에 안 남기고 폴더만 묶는"** 장치이고, 그렇게 묶인 폴더 하위 페이지들끼리 레이아웃 같은 설정을 공유할 수 있게 해주는 것이다.

## 5. 라우트 그룹의 추가 기능 (이 프로젝트에는 미사용)

### 5.1 여러 개의 최상위 레이아웃 (Multiple Root Layouts)

원래 Next.js App Router는 `app/layout.tsx` 딱 하나만 최상위(root) 레이아웃이 될 수 있고, 그 안에 `<html>`, `<body>` 태그를 한 번만 선언한다. 이 프로젝트의 `(auth)/layout.tsx`, `(main)/layout.tsx`도 `<html>`/`<body>`를 직접 쓸 수 없는데, 이미 최상위 `app/layout.tsx`가 그것을 선언하고 있고 나머지 중첩 레이아웃은 그 안의 "내용물"일 뿐이기 때문이다.

**중첩 레이아웃(이 프로젝트 방식)이 못 하는 것**이 여기서 필요해진다: 그룹마다 `<html lang="...">`나 `<body class="...">`를 다르게 주는 것.

#### 구체적 예시 서비스: 마케팅 랜딩페이지 + 로그인 후 앱

```
app/
├── (marketing)/
│   ├── layout.tsx     ← <html lang="ko">, 화려한 히어로 폰트, GA/픽셀 스크립트 삽입
│   ├── page.tsx       → "/"        (첫 방문자용 랜딩)
│   ├── pricing/
│   │   └── page.tsx   → "/pricing"
│   └── about/
│       └── page.tsx   → "/about"
└── (app)/
    ├── layout.tsx     ← <html lang="ko" className="antialiased">, 모노스페이스 폰트,
    │                     WebSocket Provider, 마케팅 스크립트는 아예 안 실음
    ├── dashboard/
    │   └── page.tsx   → "/dashboard"
    └── settings/
        └── page.tsx   → "/settings"
```

이 구조에서는 공통 `app/layout.tsx`를 아예 없애고, `(marketing)/layout.tsx`와 `(app)/layout.tsx`가 각각 독립적으로 `<html>`부터 새로 선언한다.

#### 중첩 레이아웃 vs Multiple Root Layouts — 할 수 있는 것 비교

| 하고 싶은 것                                                                                     | 중첩 레이아웃 (이 프로젝트 방식) | Multiple Root Layouts |
| -------------------------------------------------------------------------------------------------- | :---------------------------------: | :-----------------------: |
| 사이드바 유무, 페이지 여백 등 UI 구조 다르게                                                      | ✅ 가능 (지금 이 프로젝트가 이미 함) | ✅ 가능                   |
| `<html lang="ko">` vs `<html lang="en">`을 그룹마다 다르게                                        | ❌ 불가능 (최상위 하나뿐)            | ✅ 가능                   |
| 마케팅 페이지에만 구글 애널리틱스 `<script>`를 `<head>`에 삽입, 로그인 앱 쪽엔 절대 안 실리게      | ❌ 불가능 (공통 layout에 넣으면 앱 쪽에도 다 실림) | ✅ 가능 (그룹별 `<head>` 완전 분리) |
| `<body>`에 전역 폰트 클래스를 그룹마다 다르게 (마케팅=세리프 폰트, 앱=모노스페이스)                 | ❌ 불가능 (`<body>`는 한 곳에서만 선언 가능) | ✅ 가능                   |

즉, "보여지는 화면 구조"만 다르면 중첩 레이아웃으로 충분하고, "문서 자체의 언어/스크립트/폰트 같은 `<html>`·`<body>` 레벨 설정"까지 완전히 분리해야 할 때만 Multiple Root Layouts가 필요하다.

**이 프로젝트에 왜 없는가**: 지금 `(auth)`와 `(main)`은 둘 다 한국어, 둘 다 같은 폰트, 둘 다 같은 스크립트 셋을 쓴다 — 즉 "화면 구조"만 다르고 "문서 레벨 설정"은 같다. 그래서 공통 `app/layout.tsx` 하나 + 중첩 레이아웃 두 개로 충분하며, 굳이 Multiple Root Layouts를 도입할 이유가 없다.

> 💡 **대안**: 완전히 분리된 `<html>` 없이도, 조건부로 스크립트/폰트를 넣는 방법(예: `usePathname()`으로 분기)도 있지만, 이 경우 번들에 두 그룹의 스크립트/폰트가 전부 포함되어 로딩 성능상 불리하다. 진짜 "이 그룹 페이지에서는 저 그룹 코드가 아예 로드조차 안 되게" 하려면 Multiple Root Layouts처럼 물리적으로 트리를 나누는 게 유일한 방법이다.

### 5.2 `loading.tsx`, `error.tsx`, `template.tsx`도 그룹 단위로 스코프됨

`layout.tsx`뿐 아니라 로딩 UI(`loading.tsx`), 에러 UI(`error.tsx`), 템플릿(`template.tsx`) 같은 특수 파일들도 라우트 그룹 안에 넣으면 그 그룹에만 적용된다. 예를 들어 `(main)/loading.tsx`를 만들면 `/tasks`, `/settings` 등 `(main)` 그룹 페이지 전환 시에만 로딩 스피너가 뜨고, `(auth)` 쪽엔 영향이 없다.

### 5.3 이름 충돌 규칙 — URL이 겹치면 빌드 에러

라우트 그룹 이름 자체는 URL에 안 남지만, 서로 다른 그룹에 속한 두 페이지가 최종적으로 같은 URL을 만들어내면 Next.js가 에러를 낸다.

```
app/
├── (marketing)/about/page.tsx   → /about
└── (shop)/about/page.tsx       → /about   ← 충돌! 빌드/개발 서버 에러 발생
```

## 6. 정리

| 기능                                              | 사용 중인가? | 용도                                                                 |
| --------------------------------------------------- | :-----------: | ----------------------------------------------------------------------- |
| URL 안 남기고 레이아웃 분리                        | ✅ 사용 중 (`(auth)`, `(main)`) | 핵심 기능                                                     |
| 여러 개의 최상위 레이아웃 (Multiple Root Layouts)  | ❌ 미사용     | 그룹별로 완전히 다른 `<html>` 문서(언어/스크립트/폰트) 필요할 때 |
| 그룹 스코프 loading/error/template                  | ❌ 미사용     | 그룹별로 다른 로딩·에러 화면 필요할 때                              |
| URL 충돌 방지 규칙                                  | 해당 없음 (충돌 없음) | 그룹 늘릴 때 주의해야 할 제약사항                              |

**참고로 헷갈리기 쉬운 것**: `(auth)`, `(main)` = 라우트 그룹 → URL에 안 나타남. `[id]`, `[...nextauth]` (예: `app/api/tasks/[id]`) = 동적 세그먼트 → URL에 실제 값으로 나타남 (예: `/tasks/abc123`). 둘 다 괄호를 쓰지만 완전히 다른 기능이다.
