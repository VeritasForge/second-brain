---
created: 2026-02-26
source: claude-code
tags: [react, next.js, ssr, hydration, frontend, web-performance]
---

# 📖 Hydration — Concept Deep Dive

> 💡 **한줄 요약**: 서버에서 만들어진 정적 HTML에 React가 연결(attach)되어 인터랙티브하게 살아나는 과정

---

## 1️⃣ 무엇인가? (What is it?)

**Hydration**은 서버가 미리 만들어 보낸 정적 HTML에, 브라우저의 JavaScript(React)가 연결되면서 이벤트 핸들러·상태 등을 붙여 **완전한 인터랙티브 앱으로 만드는 과정**입니다.

- **공식 React 정의**: "클라이언트 React가 기존 DOM을 채택(adopt)하는 과정" — DOM을 새로 만드는 것이 아니라 이미 있는 DOM에 달라붙는 것
- **탄생 배경**: SSR(Server-Side Rendering)이 등장하면서 "서버는 HTML을 주고, 클라이언트는 그걸 다시 인터랙티브하게 만들어야 한다"는 문제를 해결하기 위해 등장
- **해결하는 문제**: 최초 페이지 로딩 속도(FCP)는 SSR로 빠르게, 이후 동적 동작은 React로 처리하는 두 마리 토끼

> 📌 **핵심 키워드**: `SSR`, `hydrateRoot`, `Reconciliation`, `Hydration Mismatch`, `FCP`, `TTI`

---

## 2️⃣ 핵심 개념 (Core Concepts)

```
┌──────────────────────────────────────────────────────┐
│               Hydration의 3가지 핵심 요소              │
├──────────────────────────────────────────────────────┤
│                                                      │
│   Static HTML          React Virtual DOM             │
│  (서버가 만든 것)   ───►  (클라이언트가 만든 것)        │
│       │                        │                     │
│       └──────── 비교(Reconcile) ┘                     │
│                      │                               │
│                      ▼                               │
│           DOM에 Event Handler 연결 완료               │
│                (Interactive!)                        │
└──────────────────────────────────────────────────────┘
```

| 핵심 요소       | 역할             | 설명                                          |
| --------------- | ---------------- | --------------------------------------------- |
| **SSR**         | 정적 HTML 생성   | 서버에서 React 컴포넌트를 HTML 문자열로 렌더링  |
| **hydrateRoot()** | 하이드레이션 진입점 | React가 DOM에 달라붙는 API                  |
| **Reconciliation** | DOM 비교      | 서버 HTML과 클라이언트 Virtual DOM이 같은지 확인 |
| **Event Binding** | 인터랙티브화    | click, input 등 이벤트 핸들러 연결             |

> 📎 **보충 — Reconciliation 어원**
>
> 라틴어 `reconciliare` → `re-`(다시) + `conciliare`(일치시키다, 모으다).
> **"두 상태의 불일치를 해소해 일치시킨다"** 는 본질적 의미다.
>
> | 맥락              | 무엇을 비교하나              | 목적                     |
> | ----------------- | ---------------------------- | ------------------------ |
> | 결제 배치 처리    | 장부 기록 vs 실제 거래 내역  | 불일치 찾아 바로잡기     |
> | React             | 이전 Virtual DOM vs 새 Virtual DOM | 차이(diff)만 실제 DOM에 반영 |
>
> 전 직장에서 봤던 결제 배치 reconciliation과 React Reconciliation은 단어만 같은 게 아니라, **"두 상태를 비교해서 불일치를 최소 비용으로 해소한다"** 는 본질적 의미가 동일하다.

> 💡 **핵심 구분**: Hydration ≠ Rendering. 렌더링은 DOM을 새로 만들지만, 하이드레이션은 **이미 있는 DOM을 재사용**한다.

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

```
┌──────────────────────────────────────────────────────────────┐
│                   SSR + Hydration 전체 흐름                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  [서버]                          [브라우저]                   │
│                                                              │
│  React 컴포넌트                                               │
│      │                                                       │
│      ▼                                                       │
│  renderToString()  ──── HTML 전송 ────►  화면 표시 ← FCP 발생 │
│  (정적 HTML 생성)                         (아직 클릭 안 됨)   │
│                                              │               │
│                                              ▼               │
│                              JS 번들 다운로드 & 실행          │
│                                              │               │
│                                              ▼               │
│                              hydrateRoot() 호출              │
│                                              │               │
│                                    서버HTML == 클라이언트?    │
│                                         ✅ 일치               │
│                                              │               │
│                                              ▼               │
│                                   Event Handler 연결         │
│                                   ← TTI 완료 (이제 클릭!)    │
└──────────────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (Step by Step)

1. **서버에서 HTML 생성**: React 컴포넌트를 `renderToString()`으로 정적 HTML 문자열로 변환
2. **HTML 브라우저로 전송**: 브라우저가 즉시 화면을 표시 → **FCP(First Contentful Paint) 발생** (인터랙티브 X)
3. **JS 번들 다운로드**: React 코드 + 앱 번들이 브라우저에서 로드됨
4. **`hydrateRoot()` 호출**: React가 클라이언트 쪽 Virtual DOM 트리를 구성
5. **Reconciliation**: 서버 HTML과 클라이언트 Virtual DOM을 비교 — 완전히 같아야 함
6. **Event Binding 완료**: onClick, onChange 등 이벤트 핸들러가 기존 DOM에 연결됨 → **TTI(Time to Interactive) 완료**

```tsx
// Next.js는 내부적으로 이 과정을 자동 처리함
// React 18 코드 예시
import { hydrateRoot } from 'react-dom/client';

hydrateRoot(
  document.getElementById('root'),
  <App />  // 서버와 똑같은 컴포넌트 트리를 전달해야 함
);
```

> 📎 **보충 — JS 번들 재다운로드와 캐싱**
>
> 화면이 켜진 상태에서는 이미 메모리에 로드된 JS를 다시 받지 않는다. 새 탭을 열거나 새로고침해야 새 번들을 받는 시점이 생긴다. 브라우저가 "새 배포인지"를 구분하는 방법은 **파일명에 포함된 content hash**다:
>
> ```
> main.a3f2c1d8.js   ← 파일 내용의 해시값이 이름에 포함됨
> main.9b4e72fa.js   ← 코드가 바뀌면 해시도 바뀜 → 새 URL → 새 다운로드
> ```
>
> | 파일        | Cache-Control              | 이유                                          |
> | ----------- | -------------------------- | --------------------------------------------- |
> | HTML        | `no-cache`                 | 항상 서버에 최신 여부 확인                     |
> | JS/CSS 번들 | `max-age=31536000, immutable` | URL 자체가 바뀌므로 1년 캐시해도 안전       |
>
> **흐름 요약:**
> ```
> 새 배포
>   → HTML (no-cache) → 서버 확인 → 새 HTML 수신
>   → 새 HTML은 새 hash URL의 JS 참조
>   → 브라우저: 이 URL은 캐시에 없음 → 새로 다운로드
>   → 바뀌지 않은 react/lodash 등은 hash 동일 → 캐시에서 즉시 로드
> ```
> 새 배포를 해도 실제로 다운로드되는 건 변경된 파일뿐이다.

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| #  | 유즈 케이스             | 설명                                          | 적합한 이유              |
| -- | ----------------------- | --------------------------------------------- | ------------------------ |
| 1  | **Next.js SSR 페이지**  | 서버에서 데이터를 포함한 HTML 생성 후 하이드레이션 | SEO + 빠른 초기 로딩  |
| 2  | **이커머스 상품 페이지** | HTML은 즉시 보여주고 장바구니 버튼은 JS 이후 활성화 | 체감 속도 개선        |
| 3  | **뉴스/블로그 사이트**  | 본문은 서버 렌더, 댓글/좋아요는 하이드레이션 후 동작 | SEO 필수 + 인터랙션  |
| 4  | **React 18 Streaming**  | 청크 단위로 서버→클라이언트 전송 + 부분 하이드레이션 | 대형 페이지 성능    |

### ✅ 베스트 프랙티스

1. **서버/클라이언트 렌더 결과를 동일하게 유지**: `typeof window`나 `Math.random()` 등 환경에 따라 다른 값이 나오는 코드를 초기 렌더에 쓰지 말 것
2. **클라이언트 전용 로직은 `useEffect` 안에**: localStorage, window, Date 등은 마운트 후 실행
3. **React 18 Selective Hydration 활용**: `<Suspense>`로 감싸면 무거운 컴포넌트는 나중에 하이드레이션

```tsx
// ✅ 올바른 패턴: 클라이언트 전용 값은 useEffect 후에
const [isClient, setIsClient] = useState(false);
useEffect(() => setIsClient(true), []);

return <div>{isClient ? window.innerWidth : null}</div>;
```

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분    | 항목                   | 설명                                                    |
| ------- | ---------------------- | ------------------------------------------------------- |
| ✅ 장점 | **빠른 FCP**           | 서버 HTML이 먼저 표시되어 사용자가 즉시 콘텐츠를 봄     |
| ✅ 장점 | **SEO 친화적**         | 검색엔진이 정적 HTML을 바로 읽을 수 있음                |
| ✅ 장점 | **DOM 재사용**         | 새로 만들지 않고 기존 DOM을 재활용해 성능 이득          |
| ❌ 단점 | **TTI 지연**           | HTML은 보여도 JS 로드 전까지 클릭 등 동작 안 함         |
| ❌ 단점 | **Hydration Mismatch** | 서버/클라이언트 불일치 시 에러 또는 레이아웃 깨짐       |
| ❌ 단점 | **JS 번들 필요**       | 결국 클라이언트에서 JS를 다 받아야 함                   |

> 📎 **보충 — FCP란?**
>
> **FCP(First Contentful Paint)**: 브라우저가 DOM에서 처음으로 텍스트나 이미지를 화면에 그린 시점. Google Core Web Vitals 중 하나다.
>
> ```
> CSR:  [JS 다운로드] → [React 실행] → [DOM 생성] → FCP  (느림)
> SSR:  [HTML 수신]  → FCP (빠름) → [JS 다운로드] → Hydration
> ```
>
> **LCP(Largest Contentful Paint)** 는 "가장 큰 콘텐츠"가 그려진 시점. FCP = 첫 픽셀, LCP = 메인 콘텐츠 기준.

> 📎 **보충 — TTI 지연, 실제로 체감되나?**
>
> **대부분의 경우 체감 못 하는 게 정상이다.** 이유:
> - Hydration 자체는 보통 수백ms 이내로 끝남
> - 사용자는 페이지 뜨자마자 반사적으로 클릭하지 않음. 텍스트를 읽고 스크롤을 내리는 사이에 이미 완료됨
> - React 18의 Selective Hydration은 사용자가 상호작용하려는 영역을 **우선** hydrate해서 더 개선됨
>
> 단, JS 번들이 매우 크거나 저사양 기기 / 느린 네트워크 환경에서는 수 초 이상 지연이 실제로 발생할 수 있다.

### ⚖️ Trade-off 분석

```
빠른 첫 화면(FCP)  ◄──────────────────────►  인터랙션 지연(TTI)
SEO 최적화        ◄──────────────────────►  JS 번들 용량 부담
DOM 재사용 효율   ◄──────────────────────►  Mismatch 에러 위험
```

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 렌더링 방식 비교 매트릭스

| 비교 기준        | **CSR**    | **SSR + Hydration** | **RSC (React Server Components)** |
| ---------------- | ---------- | ------------------- | --------------------------------- |
| 첫 화면 속도     | 느림       | 빠름                | 매우 빠름                         |
| SEO              | 어려움     | 좋음                | 좋음                              |
| Hydration 필요   | 없음       | 있음                | 최소화                            |
| JS 번들          | 전체 필요  | 전체 필요           | 클라이언트 컴포넌트만             |
| 서버 비용        | 없음       | 있음                | 있음                              |

### 🔍 핵심 차이 요약

```
CSR (Client-Side)           SSR + Hydration
────────────────    vs     ───────────────────
빈 HTML 전송                완성된 HTML 전송
JS가 다 만들음              서버가 먼저 만들고
                            JS가 "붙음"(Hydrate)
SEO 불리                    SEO 유리
```

### 🤔 언제 무엇을 선택?

- **CSR만** → 관리자 도구, 로그인 필수 대시보드 (SEO 불필요)
- **SSR + Hydration** → 공개 페이지, SEO 필요, Next.js Pages Router
- **RSC + 선택적 Hydration** → Next.js App Router, 최신 프로젝트 권장

> 📎 **보충 — RSC(React Server Components) 상세**
>
> RSC는 **Next.js App Router(v13+)에서 기본 컴포넌트 타입**이다. `'use client'`를 선언하지 않으면 모두 Server Component다.
>
> ```
> SSR + Hydration:
>   서버 → HTML 생성 → 클라이언트
>   클라이언트 → JS 번들 수신 → hydrateRoot() → 인터랙티브
>
> RSC:
>   서버 → 렌더링 후 직렬화된 결과 전송 → 클라이언트
>   클라이언트 → JS 없음 → Hydration 없음 → 정적 HTML로 끝
> ```
>
> RSC의 특징:
> - DB / 파일시스템에 직접 접근 가능 (서버에서만 실행)
> - API 키 등 민감 정보가 클라이언트에 노출 안 됨
> - `useState`, `useEffect`, 이벤트 핸들러 사용 불가
> - 해당 컴포넌트의 JS가 클라이언트로 가지 않으므로 번들 크기 감소
>
> **RSC는 SSR을 대체하는 게 아니라 함께 동작한다.** RSC로 HTML을 생성(SSR)하고, `'use client'` 컴포넌트는 그 안에서 Hydration된다. 두 개념이 레이어처럼 쌓여 있다.

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수

| #  | 실수                                  | 왜 문제인가                             | 올바른 접근                        |
| -- | ------------------------------------- | --------------------------------------- | ---------------------------------- |
| 1  | **`typeof window` 초기 렌더에서 사용** | 서버는 window가 없어 분기 → mismatch   | `useEffect` 안에서 처리            |
| 2  | **`Math.random()`, `Date.now()` 렌더에 사용** | 서버/클라이언트 값이 다름      | 서버에서 생성한 값을 props로 전달  |
| 3  | **잘못된 HTML 중첩**                  | `<p>` 안에 `<div>` 등 → React가 전체 재렌더 | HTML 시맨틱 규칙 준수         |
| 4  | **`suppressHydrationWarning` 남용**   | 진짜 버그를 숨김                        | 원인을 찾아 수정                   |

> 📎 **보충 — Hydration Mismatch 구체적 원인들**
>
> 서버에서 렌더한 HTML과 클라이언트 React가 그리려는 DOM이 다를 때 발생한다:
>
> **1. 실행 시점마다 값이 달라지는 코드**
> ```tsx
> <p>{Date.now()}</p>   // 서버와 클라이언트 실행 시각이 다름
> <p>{Math.random()}</p>
> ```
>
> **2. 브라우저 전용 API 접근**
> ```tsx
> <p>{window.innerWidth}</p>  // 서버에는 window가 없음
> ```
>
> **3. 타임존 차이** — 서버는 UTC, 클라이언트는 사용자 로컬 타임존으로 날짜 포맷
>
> **4. HTML 구조 오류** — `<p>` 안에 `<div>`를 넣는 등 잘못된 중첩. 브라우저가 파싱 중 DOM을 자체 수정해버림
>
> **5. mounted 상태 사용 패턴**
> ```tsx
> const [mounted, setMounted] = useState(false);
> useEffect(() => setMounted(true), []);
> // mounted false → true 전환 시 렌더 결과가 달라짐 → mismatch
> ```
>
> `suppressHydrationWarning={true}`는 타임존 의존 UI처럼 불가피한 경우에만 **해당 태그에만** 좁게 써야 한다.

### 🚫 Anti-Patterns

1. **`suppressHydrationWarning={true}` 전체에 적용**: 경고를 숨길 뿐 mismatch 원인은 남아있음
2. **초기 렌더에서 localStorage 직접 읽기**: 서버엔 localStorage가 없어 에러 발생

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형        | 이름                                  | 링크                                                                                   |
| ----------- | ------------------------------------- | -------------------------------------------------------------------------------------- |
| 📘 블로그   | The Perils of Hydration (Josh W. Comeau) | [joshwcomeau.com](https://www.joshwcomeau.com/react/the-perils-of-rehydration/)     |
| 📖 공식 문서 | React `hydrateRoot` API              | [react.dev](https://react.dev/reference/react-dom/client/hydrateRoot)                 |
| 📖 공식 문서 | Next.js Hydration Error              | [nextjs.org](https://nextjs.org/docs/messages/react-hydration-error)                  |

### 🛠️ 관련 도구 & 패턴

| 도구/패턴                            | 용도                                       |
| ------------------------------------ | ------------------------------------------ |
| `hydrateRoot()`                      | React 18 하이드레이션 진입점               |
| `<Suspense>`                         | Selective/Streaming Hydration 활용         |
| `useEffect` + `useState`             | 클라이언트 전용 로직 안전하게 처리         |
| `dynamic({ ssr: false })`            | 특정 컴포넌트 SSR/하이드레이션 비활성화    |
| Content Hash (`main.a3f2c1d8.js`)   | 빌드 산출물 캐싱 전략 핵심                 |

### 🔮 트렌드 & 전망

- React 18의 **Selective Hydration**: `<Suspense>` 경계별로 우선순위 하이드레이션
- **React Server Components**: 서버 컴포넌트는 아예 JS를 클라이언트에 안 보냄 → Hydration 자체를 최소화하는 방향으로 진화 중

---

## 📎 Sources

1. [The Perils of Hydration — Josh W. Comeau](https://www.joshwcomeau.com/react/the-perils-of-rehydration/) — 블로그
2. [hydrateRoot — React 공식](https://react.dev/reference/react-dom/client/hydrateRoot) — 공식 문서
3. [Next.js Hydration Error](https://nextjs.org/docs/messages/react-hydration-error) — 공식 문서
