---
created: 2026-04-21
source: claude-code
tags: [javascript, typescript, philosophy, language-design, comparison, event-loop, tc39, structural-typing]
---

# 📖 JS/TS 철학과 차별점 — 왜 JavaScript & TypeScript인가

> 💡 **한줄 요약**: JavaScript는 "브라우저의 언어"에서 "풀스택의 언어"로 진화했고, TypeScript는 "JavaScript that scales"를 목표로 점진적 타입 시스템을 추가하여, 단일 언어로 프론트엔드+백엔드+모바일을 커버하는 유일한 생태계를 형성했다.
>
> 📌 **핵심 키워드**: "Don't break the web", TC39, Gradual Typing, Structural Typing, NPM Ecosystem
> 📅 **기준**: ECMAScript 2024 / TypeScript 5.x (2025)

---

## 1️⃣ JavaScript의 탄생 — Brendan Eich의 10일 (1995)

| 항목 | 내용 |
|------|------|
| **탄생** | 1995년 5월, Brendan Eich가 Netscape에서 **10일** 만에 프로토타입 작성 |
| **원래 이름** | Mocha → LiveScript → JavaScript (Java 마케팅 차용) |
| **영향 받은 언어** | Scheme (일급 함수), Self (프로토타입), Java (문법) |
| **핵심 목표** | "비전문가도 브라우저에서 인터랙션을 만들 수 있게" |
| **표준화** | 1997년 ECMAScript 1 (ECMA-262) |

### 🧒 12살 비유

> JavaScript는 "10일 만에 지어진 집"이야. 처음에는 작은 오두막(브라우저 스크립트)이었는데, 30년 동안 계속 증축해서 지금은 고층 빌딩(풀스택)이 됐어. 기초가 약한 부분이 있지만, 아무도 이사 갈 수 없어 — 인터넷 전체가 이 건물에 살고 있으니까.

---

## 2️⃣ TypeScript의 등장 — Microsoft의 2012년 해법

| 항목 | 내용 |
|------|------|
| **탄생** | 2012년 10월, Microsoft |
| **설계자** | **Anders Hejlsberg** (C#, Delphi 설계자) |
| **핵심 목표** | "JavaScript that scales" — 대규모 코드베이스를 위한 타입 안전 |
| **철학** | **점진적 타입** — 기존 JS 코드에 타입을 점진적으로 추가 가능 |
| **관계** | TS는 JS의 **상위 집합** — 모든 유효한 JS는 유효한 TS |

### TypeScript의 독특한 설계 결정

```
                    ┌──────────────────┐
                    │  TypeScript 소스  │
                    │  (.ts / .tsx)     │
                    └────────┬─────────┘
                             │ tsc (컴파일)
                             ▼
                    ┌──────────────────┐
                    │  JavaScript 출력  │  ← 타입 정보 완전 제거!
                    │  (.js / .jsx)     │
                    └──────────────────┘
```

**타입은 컴파일 타임에만 존재하고, 런타임에는 완전히 사라진다.** 이것이 Go(타입이 바이너리에 남음), Kotlin(JVM에 타입 정보 남음)과의 근본적 차이.

---

## 3️⃣ 핵심 설계 원칙

### JavaScript: "Don't break the web"

| 원칙 | 의미 |
|------|------|
| 하위 호환성 절대 유지 | 1997년 JS 코드도 2025년 브라우저에서 동작 |
| TC39 단계적 프로세스 | Stage 0(제안) → Stage 1(검토) → Stage 2(초안) → Stage 3(후보) → Stage 4(완료) |
| 연간 릴리스 | ES2015부터 매년 새 기능 추가 (Big Bang 변경 없음) |

### TypeScript: "Structural Typing + Gradual"

```typescript
// 구조적 타이핑: 이름이 아니라 형태(shape)로 타입 호환 판단
interface Printable {
  print(): void;
}

class Document {
  print() { console.log("doc"); }
}

// Document가 Printable을 implements하지 않았지만, print()가 있으므로 호환
const p: Printable = new Document();  // ✅ Go의 structural typing과 동일!
```

---

## 4️⃣ 4개 언어 비교 매트릭스

### 설계 목표

| 축 | JS/TS | Go | Python | Kotlin |
|----|-------|-----|--------|--------|
| **탄생 동기** | 브라우저 인터랙션 | Google 대규모 SW 공학 | 모든 사람의 프로그래밍 | Java 고통 해결 |
| **핵심 가치** | 유연·하위 호환 | 단순·빠른 빌드 | 가독성·실용성 | 안전·간결·호환 |
| **타입 시스템** | 점진적 구조적 (TS) | 정적 구조적 | 동적 + 선택적 힌트 | 정적 명목적 |
| **플랫폼** | 브라우저 + Node.js | 네이티브 바이너리 | CPython | JVM |

### 동시성 모델

| 언어 | 모델 | 진정한 병렬? | CPU-bound 해법 |
|------|------|------------|--------------|
| **JS/TS** | 이벤트 루프 (단일 스레드) | ❌ | Worker Threads |
| Go | CSP (goroutine) | ✅ | goroutine |
| Python | GIL + asyncio | ❌ (3.14부터) | multiprocessing |
| Kotlin | 코루틴 + JVM 스레드 | ✅ | Dispatchers.Default |

### 생태계

| 측면 | JS/TS | Go | Python | Kotlin |
|------|-------|-----|--------|--------|
| 패키지 수 (NPM/PyPI/etc) | **~3M** (NPM 최대) | ~500K | ~500K (PyPI) | Maven Central 공유 |
| 풀스택 가능 | ✅ (유일!) | ❌ (백엔드만) | ❌ (백엔드+ML) | ❌ (백엔드+Android) |
| 프론트엔드 | React, Vue, Angular | ❌ | ❌ | Compose Multiplatform |

---

## 5️⃣ JS/TS가 빛나는 영역 vs 약한 영역

### ✅ 빛나는 영역

| 영역 | 대표 도구 | 왜 적합한가 |
|------|---------|-----------|
| **프론트엔드 웹** | React, Vue, Angular, Svelte | 브라우저의 유일한 네이티브 언어 |
| **풀스택** | Next.js, Nuxt, Remix | 프론트+백엔드 코드·타입 공유 |
| **실시간 서비스** | Socket.io, SSE | 이벤트 루프가 고동시성 I/O에 최적 |
| **서버리스** | AWS Lambda, Cloudflare Workers | 빠른 cold start, 경량 런타임 |
| **NPM 생태계** | 300만+ 패키지 | "필요한 건 이미 있다" |

### ❌ 약한 영역

| 영역 | 왜 약한가 | 대안 |
|------|---------|------|
| **CPU 집약 작업** | 단일 스레드 이벤트 루프 | Go, Rust |
| **시스템 프로그래밍** | GC, V8 의존 | Rust, Go |
| **타입 안전 (JS)** | 동적 타입 → 런타임 에러 | TypeScript 사용 |
| **엔터프라이즈 패턴** | DI/AOP 생태계 미성숙 (Nest.js로 부분 해결) | Kotlin+Spring |
| **데이터 과학** | 생태계 부족 | Python |

---

## 6️⃣ 다른 언어에서 JS/TS로의 마인드셋 전환

### Go → JS/TS

| Go 습관 | JS/TS 방식 | 전환 포인트 |
|---------|-----------|-----------|
| goroutine + channel | Promise + async/await | 동기 스타일 → 비동기 사고 |
| 정적 타입 (컴파일러) | TS 타입 (런타임에 사라짐) | 타입이 런타임 안전을 보장하지 않음 |
| 단일 바이너리 | node_modules + 번들러 | 의존성 관리 복잡도 ↑↑ |
| `if err != nil` | `try/catch` + `Promise.catch` | 에러 전파 방식 다름 |
| gofmt | Prettier + ESLint | 도구 2개 (포맷 + 린트 분리) |

### Python → JS/TS

| Python 습관 | JS/TS 방식 | 전환 포인트 |
|-----------|-----------|-----------|
| 동적 타입 | 동적 (JS) + 정적 (TS) | 비슷하지만 TS는 컴파일 필요 |
| asyncio | Promise + async/await | 비슷한 비동기 모델 |
| pip/uv | npm/pnpm | node_modules 지옥 |
| 들여쓰기 블록 | `{}` 중괄호 블록 | 세미콜론 선택적 |
| `None` | `null` + `undefined` | 두 가지 부재값 (!) |

### Kotlin → JS/TS

| Kotlin 습관 | JS/TS 방식 | 전환 포인트 |
|-------------|-----------|-----------|
| null safety (`?`) | TS `strict`  모드 + `?` | 비슷하지만 런타임 보장 없음 |
| 코루틴 | Promise + async/await | 비슷하지만 단일 스레드 |
| sealed class | discriminated union (TS) | 동일한 패턴, 다른 문법 |
| Gradle | npm/pnpm/yarn | 빌드 도구 생태계 다름 |

---

## 7️⃣ JS/TS 주요 변화 타임라인

```
1995 ─── JavaScript 탄생 (Brendan Eich, 10일)
  │
1997 ─── ECMAScript 1 표준화
  │
2009 ─── Node.js (Ryan Dahl) — JS가 서버로
  │       ES5 (strict mode, JSON)
  │
2012 ─── TypeScript 1.0 (Microsoft, Anders Hejlsberg)
  │
2015 ─── 🎯 ES2015 (ES6): class, arrow, Promise, let/const, module
  │       "JavaScript의 대혁명"
  │
2017 ─── ES2017: async/await
  │
2020 ─── ES2020: optional chaining (?.), nullish coalescing (??)
  │       Deno 1.0 (Ryan Dahl)
  │
2022 ─── Bun 1.0 (Jarred Sumner) — Zig 기반 런타임
  │       TypeScript 4.9: satisfies 연산자
  │
2023 ─── TypeScript 5.0: decorators (TC39 Stage 3)
  │       ES2023: Array.findLast, Hashbang
  │
2024 ─── ES2024: Temporal, groupBy, Promise.withResolvers
  │       TypeScript 5.5: inferred type predicates
  │
2025 ─── Node.js에 TypeScript 기본 지원 (--experimental-strip-types)
         Bun/Deno의 TS 네이티브 지원 가속
```

---

## 📎 출처

1. [ECMAScript Language Specification (TC39)](https://tc39.es/ecma262/) — JS 공식 스펙
2. [TypeScript Handbook (typescriptlang.org)](https://www.typescriptlang.org/docs/handbook/) — TS 공식 가이드
3. [TC39 Process Document](https://tc39.es/process-document/) — TC39 단계별 프로세스
4. [JavaScript: The First 20 Years (Wirfs-Brock & Eich)](https://dl.acm.org/doi/10.1145/3386327) — JS 역사 학술 문서

---

> 📌 **다음 문서**: [[02-js-ts-architecture-and-runtime]] — V8, 이벤트 루프, Node.js
> 📌 **관련 문서**: [[modern-web-architecture-bff-ssr-spa-vite-seo]], [[react-hydration-ssr-deep-dive]]
