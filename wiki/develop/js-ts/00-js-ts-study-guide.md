---
created: 2026-04-21
source: claude-code
tags: [javascript, typescript, study-guide, index, learning-path]
---

# 📖 JS/TS 학습 가이드 — 시리즈 허브

> 💡 **한줄 요약**: JavaScript + TypeScript를 체계적으로 학습하기 위한 8개 문서 시리즈 + 기존 프론트엔드 Deep Dive의 진입점.
>
> 📅 **기준**: ES2024 / TypeScript 5.x / Node.js 22 (2025)

---

## 📚 전체 문서 목록

### 학습 시리즈

| # | 문서 | 핵심 내용 |
|---|------|----------|
| 01 | [[01-js-ts-philosophy-and-differentiation]] | JS 10일 탄생, TS 등장, TC39, 4개 언어 비교 |
| 02 | [[02-js-ts-architecture-and-runtime]] | V8, 이벤트 루프, Node.js, Deno/Bun, TS 컴파일 |
| 03 | [[03-js-ts-basic-syntax]] | CJS/ESM, this, 프로토타입, TS 타입, 구조 분해 |
| 04 | [[04-js-ts-advanced-syntax-and-patterns]] | TS 고급 타입, async, Proxy, React/Node 패턴 |
| 05 | [[05-js-ts-developer-essentials-by-seniority]] | Frontend/Backend/Full-stack 3트랙 로드맵 |
| 06 | [[06-js-ts-testing-patterns]] | Vitest, Testing Library, Playwright, 타입 테스트 |
| 07 | [[07-js-ts-project-structure-and-tooling]] | Next.js/Nest.js, Vite, Biome, 모노레포 |

### 기존 프론트엔드 Deep Dive

| 문서 | 위치 | 내용 |
|------|------|------|
| [[react-hydration-ssr-deep-dive]] | fe/ | React Hydration/SSR 메커니즘 |
| [[react-server-components-rsc-deep-dive]] | fe/ | React Server Components |
| [[modern-web-architecture-bff-ssr-spa-vite-seo]] | fe/ | BFF, SSR, SPA, Vite, SEO |
| [[googlebot-crawling-mechanism-seo]] | fe/ | Googlebot 크롤링, SEO |
| [[sse-event-design-strategy-snapshot-vs-delta]] | fe/ | SSE 이벤트 설계 전략 |

---

## 🎯 페르소나별 학습 경로

### 🟢 JS/TS 입문자
```
01 철학 → 03 기본 문법 → 02 아키텍처(§2 이벤트 루프)
→ 04 고급(§1 TS 타입) → 06 테스팅 → 07 프로젝트 구조
→ 05 Junior 레벨
```

### 🔄 Go/Python → JS/TS 전환자
```
01 철학(§6 전환 가이드) → 03 기본 문법(§2 타입, §4 this)
→ 02 아키텍처(§2 이벤트 루프 vs GMP/asyncio)
→ 04 고급(§2 async, §7 Node.js 패턴)
```

### 🎯 프론트엔드 심화
```
04 고급(§6 React) → [[react-hydration-ssr-deep-dive]]
→ [[react-server-components-rsc-deep-dive]]
→ [[modern-web-architecture-bff-ssr-spa-vite-seo]]
→ 05 Senior Frontend 트랙
```
