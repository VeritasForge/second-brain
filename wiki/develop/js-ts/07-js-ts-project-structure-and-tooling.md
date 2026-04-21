---
created: 2026-04-21
source: claude-code
tags: [javascript, typescript, project-structure, bundler, vite, eslint, biome, monorepo, nx, turborepo]
---

# 📖 JS/TS 프로젝트 구조와 도구 — 모노레포부터 배포까지

> 💡 **한줄 요약**: JS/TS 프로젝트는 Next.js(풀스택)/Nest.js(백엔드) 구조를 기본으로, Vite(번들러) + ESLint+Prettier 또는 Biome(통합 도구) + Docker/Vercel 배포를 조합하며, 대규모에서는 Nx/Turborepo 모노레포로 관리한다.
>
> 📌 **핵심 키워드**: Next.js App Router, Nest.js Module, Vite, Biome, pnpm workspace, Nx, Turborepo
> 📅 **기준**: Next.js 15 / Vite 6 / Biome 1.x (2025)

---

## 1️⃣ 프로젝트 레이아웃

### Next.js App Router (풀스택)

```
myapp/
├── src/
│   ├── app/                    ← App Router (파일 기반 라우팅)
│   │   ├── layout.tsx          ← 루트 레이아웃
│   │   ├── page.tsx            ← / 페이지
│   │   ├── users/
│   │   │   ├── page.tsx        ← /users 페이지
│   │   │   └── [id]/
│   │   │       └── page.tsx    ← /users/:id 페이지
│   │   └── api/
│   │       └── users/
│   │           └── route.ts    ← API Route Handler
│   ├── components/             ← 공유 컴포넌트
│   ├── lib/                    ← 유틸리티, DB 클라이언트
│   └── types/                  ← 타입 정의
├── public/                     ← 정적 파일
├── package.json
├── tsconfig.json
└── next.config.ts
```

### Nest.js (백엔드)

```
myapi/
├── src/
│   ├── main.ts                 ← 진입점
│   ├── app.module.ts           ← 루트 모듈
│   ├── users/
│   │   ├── users.module.ts     ← 도메인 모듈
│   │   ├── users.controller.ts ← HTTP 핸들러
│   │   ├── users.service.ts    ← 비즈니스 로직
│   │   ├── users.repository.ts ← DB 접근
│   │   └── dto/
│   │       └── create-user.dto.ts
│   └── common/
│       ├── filters/            ← 예외 필터
│       ├── guards/             ← 인증 가드
│       └── interceptors/       ← 로깅, 변환
├── test/
├── package.json
└── tsconfig.json
```

### 🔄 4개 언어 비교

| 개념 | JS/TS | Go | Python | Kotlin |
|------|-------|-----|--------|--------|
| 풀스택 프레임워크 | Next.js, Remix | 없음 | Django | 없음 |
| 백엔드 프레임워크 | Nest.js, Express | net/http, gin | FastAPI | Spring Boot |
| 라우팅 | 파일 기반 (Next.js) | 코드 기반 | 코드 기반 | 어노테이션 기반 |

---

## 2️⃣ 패키지 관리

### npm / pnpm / yarn

```bash
# pnpm (권장 — 디스크 효율적, strict)
pnpm install
pnpm add react
pnpm add -D vitest

# Workspace (모노레포)
pnpm -w add typescript  # 워크스페이스 루트에 추가
```

| 관리자 | 디스크 사용 | 속도 | 호이스팅 | 추세 |
|--------|-----------|------|---------|------|
| npm | 높음 (복사) | 보통 | 평탄화 | 기본 |
| **pnpm** | 낮음 (하드링크) | 빠름 | 격리 (strict) | **권장** |
| yarn | 중간 | 빠름 | PnP (Zero-Install) | Yarn Berry |

### 🔄 Go와 비교

| 개념 | JS/TS (pnpm) | Go |
|------|-------------|-----|
| 의존성 디렉터리 | `node_modules` (프로젝트당) | `$GOPATH/pkg/mod` (전역 캐시) |
| 락파일 | `pnpm-lock.yaml` | `go.sum` |
| 의존성 수 | 수백~수천 개 | 수십 개 (표준라이브러리 충분) |

---

## 3️⃣ 번들러와 빌드 도구

### Vite (프론트엔드 표준)

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
    plugins: [react()],
    build: {
        target: "es2022",
        rollupOptions: {
            output: { manualChunks: { vendor: ["react", "react-dom"] } },
        },
    },
});
```

| 번들러 | 용도 | 빌드 속도 | 추세 |
|--------|------|---------|------|
| **Vite** | 프론트엔드 + SSR | ⚡⚡⚡ (esbuild + Rollup) | **표준** |
| esbuild | 라이브러리, 백엔드 | ⚡⚡⚡⚡ (Go로 작성) | 빠른 빌드 |
| Webpack | 레거시 | 보통 | 유지보수 |
| Turbopack | Next.js 전용 | ⚡⚡⚡ (Rust) | 성장 중 |

> 📌 번들러와 웹 아키텍처: [[modern-web-architecture-bff-ssr-spa-vite-seo]]

---

## 4️⃣ 린팅과 포맷팅

### ESLint + Prettier (전통)

```json
// .eslintrc.json
{
  "extends": ["eslint:recommended", "plugin:@typescript-eslint/recommended"],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "no-console": "warn"
  }
}
```

### Biome (통합 도구 — Rust 기반)

```bash
# ESLint + Prettier를 하나의 도구로 대체
biome check .
biome format --write .
```

| 도구 | 역할 | 속도 | Go 대응 |
|------|------|------|--------|
| ESLint + Prettier | 린트 + 포맷 (별도) | 보통 | golangci-lint + gofmt |
| **Biome** | 린트 + 포맷 (통합, Rust) | ⚡ 35× 빠름 | golangci-lint + gofmt |

---

## 5️⃣ Docker 배포

```dockerfile
# ===== Stage 1: 빌드 =====
FROM node:22-alpine AS builder
RUN corepack enable pnpm

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

# ===== Stage 2: 실행 =====
FROM node:22-alpine
WORKDIR /app

COPY --from=builder /app/package.json /app/pnpm-lock.yaml ./
RUN corepack enable pnpm && pnpm install --frozen-lockfile --prod

COPY --from=builder /app/dist ./dist

EXPOSE 3000
CMD ["node", "dist/main.js"]
```

### 서버리스 / Edge 배포

| 플랫폼 | 특징 | Cold Start |
|--------|------|-----------|
| **Vercel** | Next.js 최적화, Edge Functions | ~50ms (Edge) |
| **Cloudflare Workers** | V8 isolate, 전역 배포 | ~0ms (warm) |
| **AWS Lambda** | Node.js 런타임 | ~200-500ms |
| **Deno Deploy** | Deno 런타임, 전역 | ~0ms (warm) |

---

## 6️⃣ 모노레포 도구

### Nx vs Turborepo

```
monorepo/
├── apps/
│   ├── web/          ← Next.js 프론트엔드
│   ├── api/          ← Nest.js 백엔드
│   └── mobile/       ← React Native
├── packages/
│   ├── ui/           ← 공유 UI 컴포넌트
│   ├── types/        ← 공유 타입 정의
│   └── utils/        ← 공유 유틸리티
├── pnpm-workspace.yaml
├── nx.json / turbo.json
└── package.json
```

| 특성 | Nx | Turborepo |
|------|-----|----------|
| 빌드 캐시 | ✅ (로컬 + 리모트) | ✅ (로컬 + 리모트) |
| 작업 오케스트레이션 | 의존 그래프 기반 | 의존 그래프 기반 |
| 코드 생성 | ✅ (generators) | ❌ |
| 플러그인 | 풍부 (React, Nest, Jest) | 미니멀 |
| 복잡도 | 높음 | 낮음 |
| 추세 | 대규모 엔터프라이즈 | 중소 규모 |

---

## 7️⃣ CI/CD 파이프라인

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  lint-test-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: pnpm
      
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint          # ESLint or Biome
      - run: pnpm typecheck     # tsc --noEmit
      - run: pnpm test          # Vitest
      - run: pnpm build         # Next.js / Vite build

  e2e:
    needs: lint-test-build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - run: pnpm install --frozen-lockfile
      - run: pnpm exec playwright install --with-deps
      - run: pnpm test:e2e
```

---

## 📎 출처

1. [Next.js Documentation](https://nextjs.org/docs) — App Router 가이드
2. [Vite Documentation](https://vite.dev/guide/) — 번들러 공식
3. [Biome Documentation](https://biomejs.dev/) — 통합 린터/포매터
4. [Nx Documentation](https://nx.dev/) — 모노레포 도구
5. [Turborepo Documentation](https://turbo.build/) — 모노레포 도구

---

> 📌 **이전 문서**: [[06-js-ts-testing-patterns]]
> 📌 **관련**: [[modern-web-architecture-bff-ssr-spa-vite-seo]], [[googlebot-crawling-mechanism-seo]]
