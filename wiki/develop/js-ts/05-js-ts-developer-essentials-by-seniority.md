---
created: 2026-04-21
source: claude-code
tags: [javascript, typescript, career-growth, junior, senior, staff, interview, frontend, backend, fullstack]
---

# 📖 JS/TS 개발자 필수 지식 — 레벨별 성장 로드맵

> 💡 **한줄 요약**: JS/TS 개발자의 성장은 Frontend/Backend/Full-stack 3트랙으로 분화되며, "문법 → 프레임워크 → 런타임 이해 → 아키텍처 설계"의 공통 경로를 따르되, 각 트랙별 깊이가 다르다.
>
> 📅 **기준**: ES2024 / TypeScript 5.x / Node.js 22 (2025)

---

## 성장 경로 (3트랙)

```
                    Junior          Mid            Senior         Staff
                    ──────         ──────         ──────         ──────
  Frontend         HTML/CSS/JS    React 심화     V8/번들러 내부  마이크로FE
                    React 기초     상태관리       성능 최적화    플랫폼 도구

  Backend          Node.js CRUD   Express/Nest   이벤트루프내부  분산 시스템
                    DB 기본        ORM/캐시       Worker/클러스터 아키텍처

  Full-stack       양쪽 기초      Next.js/Remix  SSR/RSC 내부    모노레포 전략
                                   tRPC          Edge Computing  팀 표준
```

---

## 1️⃣ Junior — "JS/TS로 동작하는 코드를 쓸 수 있는가"

### 필수 지식 ★★★
- JS 기본: 변수, 함수, 배열, 객체, `this` 기초
- TS 기본: 기본 타입, interface, union, generic 기초
- React/Vue 기초: 컴포넌트, props, state, useEffect
- Node.js: Express/Fastify CRUD, 기본 미들웨어
- 도구: npm/pnpm, ESLint, Prettier, Git

### 면접 빈출 ★★★
- "var vs let vs const" — 스코핑, 호이스팅
- "Promise와 콜백의 차이" — 비동기 패턴 진화
- "== vs ===" — 타입 강제 변환 vs strict
- "closure란 무엇인가" — 렉시컬 스코프 캡처

---

## 2️⃣ Mid — "프로덕션 수준 코드를 작성하는가"

### 필수 지식 ★★★★
- TS 중급: 제네릭, utility types (Partial, Pick, Omit), discriminated union
- React 심화: Custom hooks, 상태관리 (Zustand/Jotai), React Query
- 성능: Lighthouse, Core Web Vitals, 코드 스플리팅
- 테스트: Vitest/Jest, Testing Library, MSW (API 모킹)
- SSR/SSG: Next.js App Router, 데이터 페칭 패턴

### 면접 빈출 ★★★★
- "이벤트 루프를 설명하라" — microtask vs macrotask
- "TypeScript의 타입은 런타임에 어떻게 되는가" — 완전 제거
- "React의 렌더링 사이클" — virtual DOM, reconciliation

---

## 3️⃣ Senior — "런타임을 이해하고 시스템을 설계하는가"

### 필수 지식 ★★★★★
- V8 내부: Hidden classes, JIT 최적화/deopt, GC → [[02-js-ts-architecture-and-runtime]]
- Node.js 심화: Worker Threads, 클러스터 모드, libuv
- 번들러 내부: Vite/webpack 플러그인, tree-shaking 원리
- 보안: XSS, CSRF, CSP, OWASP for Web
- 아키텍처: 마이크로 프론트엔드, BFF 패턴

> 📌 BFF/SSR 아키텍처: [[modern-web-architecture-bff-ssr-spa-vite-seo]]

### 면접 빈출 ★★★★★
- "V8의 JIT 최적화와 deoptimization" — Turbofan, hidden class
- "Node.js에서 CPU-bound를 어떻게 처리하는가" — Worker Threads, cluster
- "마이크로 프론트엔드를 설계하라" — Module Federation, iframe, Web Components

---

## 4️⃣ Staff — "플랫폼 도구와 팀 생산성을 결정하는가"

### 필수 지식 ★★★★★
- 모노레포: Nx/Turborepo 전략, 패키지 발행
- TS strict 마이그레이션: 점진적 도입 전략
- 풀스택 아키텍처: Next.js vs Remix vs Astro 선택
- Edge Computing: Vercel Edge, Cloudflare Workers, Deno Deploy
- 팀 표준: ESLint 규칙, 코딩 가이드, 테스트 전략

### 면접 빈출 ★★★★★
- "대규모 JS/TS 프로젝트의 TS strict 마이그레이션 전략"
- "모노레포에서 빌드 캐시와 CI 최적화를 어떻게 했는가"
- "프론트엔드 플랫폼 팀의 역할과 성과를 설명하라"

---

## 📋 자기 진단 체크리스트

### Junior → Mid
- [ ] TypeScript strict 모드에서 코드를 작성할 수 있다
- [ ] Custom hook을 만들고 상태를 관리할 수 있다
- [ ] 이벤트 루프의 microtask/macrotask 순서를 설명할 수 있다

### Mid → Senior
- [ ] V8의 Hidden Class와 JIT 최적화를 설명할 수 있다
- [ ] Node.js Worker Threads로 CPU-bound 작업을 처리할 수 있다
- [ ] Lighthouse 90+ 점수를 달성할 수 있다

### Senior → Staff
- [ ] 모노레포 전략(Nx/Turborepo)을 설계할 수 있다
- [ ] TS strict 마이그레이션을 팀 규모에서 계획할 수 있다
- [ ] Edge Computing 도입 여부를 판단할 수 있다

---

## 📎 출처

1. [web.dev — Performance](https://web.dev/performance/) — 웹 성능 가이드
2. [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices) — Node.js 모범 사례

---

> 📌 **이전 문서**: [[04-js-ts-advanced-syntax-and-patterns]]
> 📌 **다음 문서**: [[06-js-ts-testing-patterns]]
