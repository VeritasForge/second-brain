---
created: 2026-02-26
source: claude-code
tags: [react, next-js, rsc, server-components, ssr, hydration, frontend, web-performance, bundle-optimization]
---

# 📖 React Server Components (RSC) — Concept Deep Dive (보강판)

> 💡 **한줄 요약**: RSC는 서버 컴포넌트의 JS를 **아예 클라이언트에 전송하지 않는** 아키텍처로, 기존 SSR + 전체 hydration의 번들 낭비를 근본적으로 해결한 진화형 렌더링 모델이다.

> 🧭 **핵심 멘탈모델**: **"구조와 데이터는 서버에서, 손가락이 닿는 것만 클라이언트에서"**

---

## 1️⃣ 무엇인가? (What is it?)

**React Server Components**는 React 팀이 2020년 소개하고 Next.js 13 App Router(2023)에서 기본값이 된 렌더링 패러다임이다. 핵심은 컴포넌트를 **"서버에서만 실행"** vs **"클라이언트에서 실행"** 으로 명시적으로 분리하는 것.

Next.js는 React 기반이고, React의 UI 구성 단위가 **Component**다. RSC는 그 Component를 서버/클라이언트로 나눠서 각자 잘하는 일을 맡기는 구조다.

> ⚠️ **선행 교정이 필요한 오해**: "RSC를 쓰면 결국 JS를 다 전달한다" → **틀렸다**.
> Server Components의 JavaScript 코드는 **클라이언트로 전송되지 않는다**. 0바이트.

- **탄생 배경**: React 앱이 커질수록 전체 JS bundle을 클라이언트가 다운로드·파싱·실행해야 하는 비용이 선형으로 증가하는 문제 해결
- **해결하려는 문제**: (1) 거대한 번들 크기, (2) 불필요한 hydration, (3) 서버 자원(DB, File System) 접근을 위한 별도 API 엔드포인트 필요성

> 📌 **핵심 키워드**: `RSC Payload`, `Server Component`, `Client Component`, `Selective Hydration`, `Zero-bundle`, `Leaf Node`

---

## 2️⃣ 핵심 개념 (Core Concepts)

RSC의 가장 중요한 두 축:

```
┌─────────────────────────────────────────────────────────┐
│                  React Component 분류                    │
├──────────────────────────┬──────────────────────────────┤
│    Server Component      │      Client Component        │
│  (기본값, 'use client'   │    ('use client' 선언 필요)  │
│   없으면 모두 여기)       │                              │
├──────────────────────────┼──────────────────────────────┤
│  ✅ DB 직접 접근 가능     │  ✅ useState, useEffect 가능 │
│  ✅ JS 번들 0바이트       │  ✅ 클릭/입력 이벤트 처리    │
│  ✅ API key 노출 없음     │  ✅ 브라우저 API 사용 가능   │
│  ❌ 상태(state) 없음      │  ❌ DB 직접 접근 불가        │
│  ❌ 이벤트 핸들러 없음    │  ❌ JS 번들에 포함됨         │
└──────────────────────────┴──────────────────────────────┘
```

| 구성 요소            | 역할              | 설명                                             |
| -------------------- | ----------------- | ------------------------------------------------ |
| **Server Component** | 서버 전용 렌더링  | JS 전송 없음. DB·파일시스템 접근. 무거운 라이브러리 격리. |
| **Client Component** | 클라이언트 인터랙티브 | JS 번들에 포함. `useState`, 이벤트 핸들러 사용.  |
| **RSC Payload**      | 서버→클라이언트 통신 포맷 | HTML + Client Component 위치 마커 + JS 파일 참조. |
| **Selective Hydration** | 선택적 수화    | Client Components만 hydrate. 서버 컴포넌트는 hydrate 안 함. |

### 🤔 Server Component로 써야 하는 판단 기준

**"DB 접근이 없어도 Server Component가 맞는 경우"** 가 있다.

```
이 컴포넌트에 무엇이 필요한가?
  │
  ├─ onClick / onChange / useState / useEffect 필요? ──► Client Component
  │
  ├─ 브라우저 API(window, localStorage) 필요? ──────────► Client Component
  │
  └─ 위 것들이 전혀 없음?
       ├─ DB / API 데이터 필요 ──────────────────────────► Server Component ✅
       ├─ 무거운 라이브러리만 사용 (marked, date-fns 등) ─► Server Component ✅
       └─ 정적 렌더링만 ─────────────────────────────────► Server Component ✅
                                           (기본값이 Server이므로 아무것도 안 해도 됨)
```

> 📌 핵심: **인터랙션이 없으면 데이터가 없어도 Server Component** 가 맞다. `date-fns`로 날짜만 포맷하는 컴포넌트도 Server Component이면 해당 라이브러리가 번들에 안 실린다.

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

세 가지 렌더링 전략을 나란히 비교해야 RSC의 위치가 명확해진다:

```
┌───────────────────────────────────────────────────────────────────┐
│                    렌더링 전략 3단 비교                             │
├─────────────────────┬───────────────────────┬─────────────────────┤
│     CSR (SPA)       │  기존 SSR + Hydration  │       RSC           │
├─────────────────────┼───────────────────────┼─────────────────────┤
│ Server              │ Server                │ Server              │
│  └─ 빈 HTML 전송    │  └─ 완성된 HTML 전송  │  └─ HTML +          │
│                     │                       │     RSC Payload     │
│         │           │         │             │         │           │
│         ▼           │         ▼             │         ▼           │
│ Client              │ Client                │ Client              │
│  └─ 전체 JS 다운    │  └─ 전체 JS 다운      │  └─ Client          │
│  └─ 클라이언트에서  │  └─ 전체 페이지       │     Components      │
│     전부 렌더링      │     Hydration         │     JS만 다운       │
│                     │  (모든 컴포넌트       │  └─ 선택적 Hydrate  │
│                     │   다시 실행)          │                     │
├─────────────────────┼───────────────────────┼─────────────────────┤
│ JS Bundle: 전체     │ JS Bundle: 전체       │ JS Bundle: Client   │
│ FCP: 느림           │ FCP: 빠름             │   Components만      │
│ TTI: 느림           │ TTI: 느림(hydration)  │ FCP: 빠름           │
│ SEO: ❌             │ SEO: ✅               │ TTI: 빠름           │
│                     │                       │ SEO: ✅             │
└─────────────────────┴───────────────────────┴─────────────────────┘
```

### 🌲 컴포넌트 트리에서의 위치

Next.js App Router에서의 전형적인 컴포넌트 트리 구조:

```
  루트 방향 ───────────────────────────────────► 잎(leaf) 방향

  Layout → Page → Section → List → Item → [Button]
                                           [Input ]
  ◄────────── Server Component (기본값) ────────►◄─ Client ─►
                                                  ↑
                                          여기서만 'use client'
```

- **루트~중간**: 구조, 레이아웃, 데이터 페칭 → **Server Component**
- **잎(leaf) 근처**: 버튼, 입력창, 토글 등 인터랙션 요소 → **Client Component**
- `'use client'`는 **가능한 한 아래(leaf)로 밀어내는 것**이 핵심 원칙

### 🔄 RSC 동작 흐름 (Step by Step)

1. **브라우저 요청** → Next.js 서버 수신
2. **서버에서 컴포넌트 트리 분석** → Server Component vs Client Component 구분
3. **Server Components 실행** → DB 쿼리, 파일 읽기 등 수행 → HTML 생성
4. **RSC Payload 생성**: 렌더링 결과 HTML + Client Component 위치 마커 + JS 파일 참조
5. **클라이언트로 전송**: HTML 스트리밍 시작 + RSC Payload
6. **클라이언트에서 Client Components의 JS만 다운로드**
7. **선택적 Hydration**: Client Component 위치에만 JS 바인딩 → 인터랙티브 활성화

```jsx
// Server Component (JS 클라이언트 전송 없음)
// app/ProductList.tsx (기본: Server Component)
async function ProductList() {
  const products = await db.query('SELECT * FROM products'); // DB 직접 접근!
  return (
    <ul>
      {products.map(p => <li key={p.id}>{p.name}</li>)}
      <AddToCartButton /> {/* ← Client Component (leaf) */}
    </ul>
  );
}

// Client Component (JS 번들에 포함)
'use client';
function AddToCartButton() {
  const [added, setAdded] = useState(false);
  return <button onClick={() => setAdded(true)}>장바구니 추가</button>;
}
```

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| #   | 유즈 케이스              | 설명                                        | 적합한 이유                     |
| --- | ------------------------ | ------------------------------------------- | ------------------------------- |
| 1   | **콘텐츠 중심 페이지**   | 블로그, 쇼핑몰 상품 목록                    | DB 직접 접근 + 번들 절감        |
| 2   | **대시보드**             | 차트 컨테이너는 서버, 인터랙티브 필터는 클라이언트 | 정적/동적 컴포넌트 혼합    |
| 3   | **Markdown 렌더링**      | `marked`, `remark` 같은 무거운 파서 서버에서만 사용 | 라이브러리가 번들에 안 들어감 |
| 4   | **SEO 중요 페이지**      | 뉴스, 커머스, 랜딩 페이지                   | 완성 HTML을 즉시 제공           |

### ✅ 베스트 프랙티스

1. **"Server by Default"**: `'use client'`를 최대한 트리 말단에만 붙여라 — 잎사귀(leaf) 컴포넌트에만
2. **데이터 페칭은 Server Component에서**: `getServerSideProps` 제거하고 컴포넌트 안에서 `await db.query()`
3. **무거운 라이브러리 격리**: `date-fns`, `marked`, `lodash` 같은 큰 라이브러리는 Server Component에만 import
4. **Suspense + Streaming**: 느린 데이터는 `<Suspense>` 로 감싸서 스트리밍 활성화

### 🔗 Server ↔ Client 컴포넌트 혼합 규칙

```
Server Component가 Client Component를 포함 ✅
  └─ Server 컴포넌트 안에서 Client 컴포넌트 import → 정상 동작

Client Component 안에 Server Component를 직접 import ❌
  └─ Client 경계 안으로 들어가면 Server로 동작 불가

Client Component에 Server Component를 children으로 전달 ✅
  └─ "구멍(slot)"을 뚫어서 넘기는 방식 → 정상 동작
```

```jsx
// ✅ 올바른 패턴: children으로 Server Component 전달
// ServerParent.tsx (Server Component)
import ClientWrapper from './ClientWrapper';
import ServerChild from './ServerChild';

export default function ServerParent() {
  return (
    <ClientWrapper>
      <ServerChild /> {/* Server Component를 children으로 전달 */}
    </ClientWrapper>
  );
}

// ClientWrapper.tsx (Client Component)
'use client';
export default function ClientWrapper({ children }) {
  const [open, setOpen] = useState(false);
  return <div onClick={() => setOpen(!open)}>{children}</div>;
  // children(= ServerChild)은 여전히 서버에서 렌더됨
}
```

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분      | 항목                       | 설명                                              |
| --------- | -------------------------- | ------------------------------------------------- |
| ✅ 장점   | **번들 크기 50-90% 감소**  | Server Component의 JS는 0바이트 전송              |
| ✅ 장점   | **DB 직접 접근**           | API 엔드포인트 없이 컴포넌트에서 바로 쿼리        |
| ✅ 장점   | **빠른 TTI**               | Hydration 범위가 Client Components로 제한         |
| ✅ 장점   | **보안 강화**              | API key, DB credentials가 서버에만 존재           |
| ✅ 장점   | **스트리밍 지원**          | Suspense로 준비된 것부터 점진적 전송              |
| ❌ 단점   | **정신 모델 복잡**         | "이 컴포넌트가 서버인가 클라이언트인가" 항상 인식 필요 |
| ❌ 단점   | **프레임워크 의존**        | 현재 Next.js App Router 등 특정 프레임워크 필요   |
| ❌ 단점   | **Context 제약**           | React Context는 Server Component에서 사용 불가    |
| ❌ 단점   | **디버깅 난이도**          | 서버/클라이언트 경계 오류가 런타임에 발생         |

### ⚖️ Trade-off 분석

```
번들 절감            ◄─────────────────────────────►  정신 모델 복잡도
SEO + 빠른 FCP       ◄─────────────────────────────►  프레임워크 의존성
서버 리소스 직접접근  ◄─────────────────────────────►  상태/이벤트 제약
```

---

## 6️⃣ 차이점 비교 (Comparison)

세 가지를 정확히 구분해야 한다.

### 📊 비교 매트릭스

| 비교 기준               | PHP/Rails SSR                       | React SSR + Hydration        | RSC                              |
| ----------------------- | ----------------------------------- | ---------------------------- | -------------------------------- |
| **첫 응답**             | 완성된 HTML                         | 완성된 HTML                  | 완성된 HTML + RSC Payload        |
| **클라이언트 JS**       | 없거나 최소 (jQuery 등)             | **전체 React 앱 번들**       | **Client Components만**          |
| **페이지 전환**         | 전체 페이지 재로드                  | SPA (클라이언트 라우팅)      | SPA (서버→클라이언트 스트리밍)   |
| **상태 보존**           | ❌ (페이지 재로드시 소멸)           | ✅ (SPA 전환)                | ✅ (reconciliation 유지)         |
| **Hydration**           | 없음                                | **전체 페이지**              | **Client Components만**          |
| **데이터 페칭**         | 컨트롤러에서 처리                   | getServerSideProps 필요      | 컴포넌트에서 직접 await          |
| **컴포넌트 단위 제어**  | ❌ (페이지 단위)                    | ❌ (앱 단위)                 | ✅ (컴포넌트 단위)               |
| **서버 자원 접근**      | ✅                                  | ✅ (별도 API 레이어 필요)    | ✅ (컴포넌트 안에서 직접)        |

### 🔍 핵심 차이 요약

```
┌─────────────────────────────────────────────────────────────┐
│  Q1. "RSC도 결국 JS를 다 보내는거 아닌가?"                   │
│                                                             │
│  기존 SSR + Hydration         RSC                           │
│  ─────────────────────  vs  ──────────────────────          │
│  Server → HTML 생성           Server → HTML 생성            │
│  Client → 전체 React앱 JS     Client → Client Components   │
│           다운로드                      JS만 다운로드        │
│  전체 페이지 hydration          선택적 hydration            │
│                                                             │
│  ❌ RSC도 모든 JS 전송 → 틀렸다!                            │
│  ✅ Server Component JS는 0바이트 전송                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Q2. "RSC = 옛날 PHP 서버 렌더링과 같지 않나?"               │
│                                                             │
│  PHP/Rails SSR               RSC                           │
│  ─────────────────  vs  ──────────────────────             │
│  페이지 전체 교체              DOM 부분 업데이트             │
│  (상태 소멸)                  (상태 보존 ✅)                 │
│  페이지 단위 렌더링            컴포넌트 단위 렌더링           │
│  내비게이션 = 전체 재로드       내비게이션 = RSC 재실행       │
│  선언적 컴포넌트 없음           선언적 React 컴포넌트 유지    │
│                                                             │
│  ❌ PHP랑 같다 → 틀렸다!                                    │
│  ✅ "서버에서 실행" + "React의 선언적 UI" = RSC              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Q3. RSC에서 역할 분담은?                                    │
│                                                             │
│  Server Component                Client Component           │
│  ─────────────────────  vs  ──────────────────────          │
│  구조, 레이아웃, 데이터             사용자 인터랙션           │
│  (루트~중간 노드)                  (leaf 근처 노드만)         │
│  DB / BFF / 파일시스템 접근         onClick, onChange        │
│  무거운 라이브러리                  useState, useEffect      │
│  인터랙션 없는 모든 것              브라우저 API              │
└─────────────────────────────────────────────────────────────┘
```

### 🤔 언제 무엇을 선택?

- **기존 SSR + Hydration**: 기존 앱 유지, 마이그레이션 비용 없앨 때
- **RSC (Next.js App Router)**: 새 프로젝트, 번들 크기가 중요한 콘텐츠 중심 앱
- **PHP/Rails SSR**: 인터랙티비티가 거의 없는 단순 정보 사이트 (JS 오버헤드 없음)

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| #   | 실수                                         | 왜 문제인가                                         | 올바른 접근                                               |
| --- | -------------------------------------------- | --------------------------------------------------- | --------------------------------------------------------- |
| 1   | Server Component에 `useState` 사용           | 서버에서는 React 훅 실행 안 됨 → 런타임 에러        | `'use client'` 추가 또는 Client Component로 분리          |
| 2   | `'use client'` 남발                          | 번들 크기 증가, RSC 이점 상실                       | 트리 최말단(잎 컴포넌트)에만 붙이기                       |
| 3   | Server Component에서 브라우저 API 사용       | `window`, `document` 없음                           | Client Component로 이동                                   |
| 4   | Server → Client → Server 컴포넌트 패스       | 직렬화 가능한 props만 넘길 수 있음                  | 함수·클래스 인스턴스는 전달 불가, 직렬화 가능 데이터만    |

### 🚫 Anti-Patterns

1. **루트 레이아웃에 `'use client'` 붙이기**: 모든 하위 컴포넌트가 Client 경계 아래로 들어가 Server Component 이점 사라짐

```
❌ 잘못된 구조:
  Layout ('use client') ← 여기 붙이면
    └─ Page           ← 이것도 Client
         └─ Section   ← 이것도 Client
              └─ List ← 이것도 Client (RSC 이점 0)

✅ 올바른 구조:
  Layout (Server)
    └─ Page (Server)
         └─ Section (Server)
              └─ List (Server)
                   └─ [Button] ('use client') ← leaf에만
```

2. **Server Component 안에서 Context Consumer 사용**: `useContext`는 클라이언트 훅이라 서버에서 동작 안 함 → Context는 Client Component에만

### 🔒 보안/성능 고려사항

- Server Component에 노출된 민감 데이터가 `props`로 Client Component에 전달되면 RSC Payload에 직렬화되어 브라우저로 전송됨 — **전달 props 범위 최소화** 필수
- Server Component는 캐싱 전략 별도 고려 필요 (`fetch` 캐시 vs DB 쿼리)

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형        | 이름                                                                                                                                               | 설명                              |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| 📖 공식 문서 | [react.dev/server-components](https://react.dev/reference/rsc/server-components)                                                                  | React 공식 RSC 레퍼런스           |
| 📖 공식 문서 | [Next.js Learn](https://nextjs.org/learn/react-foundations/server-and-client-components)                                                          | 서버/클라이언트 컴포넌트 입문     |
| 📘 딥다이브  | [Josh W. Comeau — Making Sense of RSC](https://www.joshwcomeau.com/react/server-components/)                                                      | 가장 직관적인 RSC 설명            |
| 🔬 내부 구조 | [Smashing Magazine — Forensics of RSC](https://www.smashingmagazine.com/2024/05/forensics-react-server-components/)                               | RSC Payload 포맷 해부             |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리          | 플랫폼   | 용도                         |
| ------------------------ | -------- | ---------------------------- |
| **Next.js 13+ App Router** | Node.js | RSC 기본 지원 프레임워크     |
| **React Router v7**      | Node.js  | Vite 기반 RSC 지원           |
| **Waku**                 | Node.js  | 가장 미니멀한 RSC 프레임워크 |

### 🔮 트렌드 & 전망

- **React 19 안정화**: RSC가 React 코어에 공식 통합 완료 (2024 말)
- **RSC + Actions**: `'use server'` 디렉티브로 서버 액션(폼 submit, mutation)도 서버 컴포넌트에서 처리
- **Edge Runtime 확산**: RSC를 Cloudflare Workers 등 Edge에서 실행하는 시도 증가
- **점진적 채택**: 기존 Pages Router → App Router 마이그레이션 가이드 공식 제공

### 💬 커뮤니티 인사이트

> "RSC는 SSR을 대체하는 게 아니라 SSR과 같이 동작한다. RSC = SSR(초기 HTML) + 선택적 Hydration(Client Components만) 조합이다." — [reacttraining.com](https://reacttraining.com/blog/react-architecture-spa-ssr-rsc)

> "'React on the server is not PHP' — 같은 자리에서 데이터를 가져오는 것처럼 보이지만, 상태 보존·컴포넌트 재조정·선언적 UI 모델은 PHP와 근본적으로 다르다." — [artmann.co](https://www.artmann.co/articles/react-on-the-server-is-not-php)

> **"구조와 데이터는 서버에서, 손가락이 닿는 것만 클라이언트에서"** — 이 멘탈모델로 Next.js App Router 코드를 설계할 수 있다.

---

## 📎 Sources

1. [The Forensics Of React Server Components — Smashing Magazine](https://www.smashingmagazine.com/2024/05/forensics-react-server-components/) — 기술 딥다이브
2. [React Server Components — react.dev](https://react.dev/reference/rsc/server-components) — 공식 문서
3. [React Architecture Tradeoffs: SPA, SSR, or RSC — React Training](https://reacttraining.com/blog/react-architecture-spa-ssr-rsc) — 아키텍처 비교
4. [React on the server is not PHP — artmann.co](https://www.artmann.co/articles/react-on-the-server-is-not-php) — PHP vs RSC 비교
5. [Server and Client Components — Next.js Learn](https://nextjs.org/learn/react-foundations/server-and-client-components) — 공식 Next.js 가이드
6. [Advanced SSR 2025: Selective Hydration, RSCs — blog.madrigan.com](https://blog.madrigan.com/en/blog/202601070853/) — 선택적 hydration 심화
7. [RSC vs SSR in Next.js — dev.to](https://dev.to/neetigyachahar/server-side-rendering-ssr-vs-react-server-components-rsc-in-nextjs-the-use-client-directive-4kd6) — 실용적 비교

---

> 🔬 **Research Metadata**
>
> - 검색 쿼리 수: 5
> - 수집 출처 수: 7
> - 출처 유형: 공식 2, 기술 블로그 4, 커뮤니티 1
> - 보강 내용: Server Component 판단 기준 결정 트리, 컴포넌트 트리 leaf node 전략, Server↔Client 혼합 구성 규칙(children slot 패턴), Anti-pattern 구조 비교, Q3 역할 분담 박스 추가
