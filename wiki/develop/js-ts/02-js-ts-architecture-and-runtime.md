---
created: 2026-04-21
source: claude-code
tags: [javascript, typescript, v8, event-loop, node, deno, bun, gc, runtime, architecture]
---

# 📖 JS/TS 아키텍처와 런타임 — V8부터 이벤트 루프까지

> 💡 **한줄 요약**: JavaScript는 V8 엔진이 "바이트코드 → JIT 최적화"로 실행하며, **단일 스레드 이벤트 루프**가 비동기 I/O를 처리하고, Node.js/Deno/Bun이 서버 사이드 런타임을 제공한다. TypeScript는 컴파일 시 타입을 제거하여 순수 JS로 변환된다.
>
> 📌 **핵심 키워드**: V8, Ignition, Turbofan, Event Loop, Microtask, libuv, Worker Threads
> 📅 **기준**: Node.js 22 LTS / V8 12.x (2025)

---

## 1️⃣ V8 엔진 파이프라인

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐
│  Source   │───►│  Parser  │───►│  AST     │───►│  Ignition    │
│  .js 파일 │    │          │    │          │    │  (바이트코드 │
└──────────┘    └──────────┘    └──────────┘    │  인터프리터) │
                                                 └──────┬───────┘
                                                        │
                                              Hot Function 감지
                                                        │
                                                        ▼
                                                 ┌──────────────┐
                                                 │  Turbofan    │
                                                 │  (최적화 JIT │
                                                 │  컴파일러)    │
                                                 └──────────────┘
                                                        │
                                                        ▼
                                                 ┌──────────────┐
                                                 │  Machine Code│
                                                 │  (최적화된   │
                                                 │  기계어)     │
                                                 └──────────────┘
```

| 단계 | 역할 | 특징 |
|------|------|------|
| **Parser** | 소스 → AST | 지연 파싱(lazy parsing): 즉시 실행되지 않는 함수는 파싱 연기 |
| **Ignition** | AST → 바이트코드 | 빠른 시작, 적은 메모리 |
| **Turbofan** | 바이트코드 → 최적화된 기계어 | 핫 함수만 JIT, 타입 피드백 기반 추측 최적화 |
| **Deoptimization** | 기계어 → 바이트코드 복귀 | 타입 추측 틀리면 최적화 코드 폐기 |

### Hidden Classes와 Inline Caches

```javascript
// V8이 내부적으로 객체에 "hidden class"를 부여
const obj1 = { x: 1, y: 2 };  // Hidden Class C0
const obj2 = { x: 3, y: 4 };  // 같은 Hidden Class C0 → 캐시 공유

// ⚠️ 속성 추가 순서가 다르면 다른 hidden class
const a = {}; a.x = 1; a.y = 2;  // C0 → C1 → C2
const b = {}; b.y = 2; b.x = 1;  // C0 → C3 → C4 (다른 경로!)
```

**성능 팁**: 같은 "형태(shape)"의 객체를 일관되게 생성하면 V8 최적화가 잘 동작한다.

### 🔄 4개 언어 실행 모델 비교

| 단계 | JS (V8) | Go | Python (CPython) | Kotlin (JVM) |
|------|---------|-----|-----------------|-------------|
| 초기 실행 | Ignition **인터프리터** | **기계어** 직접 | PVM **인터프리터** | **인터프리터** (JVM) |
| 최적화 | Turbofan **JIT** | SSA **AOT** | 없음 (3.13 실험적) | C2/Graal **JIT** |
| Deopt | ✅ (타입 추측 실패) | N/A | N/A | ✅ (uncommon trap) |

---

## 2️⃣ 이벤트 루프 Deep Dive

### Node.js 이벤트 루프 단계

```
   ┌───────────────────────────┐
┌─►│         timers             │  ← setTimeout, setInterval
│  └─────────────┬─────────────┘
│  ┌─────────────▼─────────────┐
│  │     pending callbacks     │  ← I/O 콜백 (이전 사이클에서 연기된)
│  └─────────────┬─────────────┘
│  ┌─────────────▼─────────────┐
│  │       idle, prepare       │  ← 내부 전용
│  └─────────────┬─────────────┘
│  ┌─────────────▼─────────────┐
│  │          poll              │  ← 새 I/O 이벤트 수집 (가장 중요!)
│  │  (대기 + 콜백 실행)       │     파일, 네트워크, DB 응답
│  └─────────────┬─────────────┘
│  ┌─────────────▼─────────────┐
│  │          check             │  ← setImmediate
│  └─────────────┬─────────────┘
│  ┌─────────────▼─────────────┐
│  │     close callbacks       │  ← socket.on('close')
│  └─────────────┬─────────────┘
│                │
│  ┌─────────────▼─────────────┐
│  │   Microtask Queue         │  ← Promise.then, queueMicrotask
│  │   (매 단계 전환 사이 실행) │     process.nextTick (Node.js)
│  └─────────────┬─────────────┘
│                │
└────────────────┘  (다음 사이클)
```

### Microtask vs Macrotask

| 종류 | 예시 | 실행 시점 |
|------|------|---------|
| **Microtask** | `Promise.then`, `queueMicrotask`, `MutationObserver` | **현재 태스크 직후**, 다음 단계 전 |
| **Macrotask** | `setTimeout`, `setInterval`, `setImmediate`, I/O | **이벤트 루프의 다음 사이클** |

```javascript
console.log("1: sync");
setTimeout(() => console.log("4: macrotask"), 0);
Promise.resolve().then(() => console.log("2: microtask"));
queueMicrotask(() => console.log("3: microtask"));
// 출력: 1 → 2 → 3 → 4
```

### 🧒 12살 비유

> 이벤트 루프는 "식당 웨이터 한 명"이야. 주문(I/O 요청)을 받아서 주방(OS)에 전달하고, 요리가 되면(콜백) 서빙해. 웨이터가 1명이라 한 번에 하나씩 서빙하지만, 주방에는 여러 요리사(OS 스레드)가 있어서 요리는 동시에 진행돼. Microtask는 "VIP 주문" — 일반 주문보다 항상 먼저 서빙.

### 🔄 4개 언어 비교

| 측면 | JS (이벤트 루프) | Go (GMP) | Python (asyncio) | Kotlin (Dispatcher) |
|------|-----------------|---------|-----------------|-------------------|
| 스레드 수 | **1** (메인) | M:N | **1** (기본) | 스레드 풀 |
| I/O 처리 | libuv (별도 스레드 풀) | netpoll (epoll) | selector (epoll) | Netty/NIO |
| CPU 병렬 | Worker Threads | goroutine | multiprocessing | Dispatchers.Default |

---

## 3️⃣ 메모리 관리

### V8 Heap 구조

```
┌───────────────────────────────────────┐
│              V8 Heap                   │
│                                        │
│  ┌──────────────┐  ┌──────────────┐  │
│  │ New Space    │  │ Old Space    │  │
│  │ (Young Gen)  │  │              │  │
│  │              │  │              │  │
│  │ Semi-space A │  │              │  │
│  │ Semi-space B │  │              │  │
│  └──────────────┘  └──────────────┘  │
│                                        │
│  ┌──────────────┐  ┌──────────────┐  │
│  │ Code Space   │  │ Large Object │  │
│  │ (JIT 코드)   │  │ Space        │  │
│  └──────────────┘  └──────────────┘  │
└───────────────────────────────────────┘
```

### Orinoco GC (V8의 GC)

| 특성 | V8 (Orinoco) | Go (Tricolor) |
|------|-------------|-------------|
| 세대 | ✅ Young/Old | ❌ 단일 세대 |
| 방식 | Generational + 증분 + 동시 | Concurrent tricolor |
| STW | Young GC: ~1-5ms, Old GC: 더 긴 증분 | ~10-90µs |
| 단명 객체 | Young GC에서 빠르게 수거 | 동일하게 마킹 (약점) |

---

## 4️⃣ Node.js 아키텍처

```
┌─────────────────────────────────────────┐
│            Node.js                       │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │        JavaScript (V8)           │   │
│  │  사용자 코드, 비동기 API          │   │
│  └──────────────┬───────────────────┘   │
│                  │                       │
│  ┌──────────────▼───────────────────┐   │
│  │        libuv (C)                  │   │
│  │  이벤트 루프, 스레드 풀 (기본 4)  │   │
│  │  파일 I/O, DNS, 압축 → 스레드풀  │   │
│  │  네트워크 → epoll/kqueue          │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │     C++ Bindings                  │   │
│  │  crypto, http_parser, zlib 등    │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Worker Threads (CPU 병렬)

```javascript
import { Worker, isMainThread, workerData } from 'worker_threads';

if (isMainThread) {
    const worker = new Worker('./heavy-task.js', {
        workerData: { input: largeData }
    });
    worker.on('message', result => console.log(result));
} else {
    // 별도 V8 인스턴스에서 실행 — 진짜 병렬
    const result = heavyComputation(workerData.input);
    parentPort.postMessage(result);
}
```

---

## 5️⃣ Deno와 Bun — 대안 런타임

| 런타임 | 기반 | 특징 | 타입스크립트 |
|--------|------|------|-----------|
| **Node.js** | V8 + libuv | 가장 성숙, NPM 호환 | 5.x부터 `--experimental-strip-types` |
| **Deno** | V8 + Tokio (Rust) | 보안 (권한 시스템), URL import | **네이티브 지원** |
| **Bun** | JavaScriptCore + Zig | **최빠른 시작**, 내장 번들러/테스트 | **네이티브 지원** |

---

## 6️⃣ TypeScript 컴파일

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  .ts     │───►│  tsc     │───►│  .js     │
│  소스     │    │  타입 검사│    │  (타입   │
│  (타입 有)│    │  + 변환   │    │  제거됨) │
└──────────┘    └──────────┘    └──────────┘
```

### tsconfig.json 핵심 옵션

```json
{
  "compilerOptions": {
    "strict": true,           // 모든 strict 옵션 활성화
    "target": "ES2022",       // 출력 JS 버전
    "module": "ESNext",       // 모듈 시스템
    "moduleResolution": "bundler",  // 번들러 방식 모듈 해석
    "noUncheckedIndexedAccess": true,  // 배열/객체 접근 시 undefined 포함
    "exactOptionalPropertyTypes": true  // 선택적 프로퍼티 엄격화
  }
}
```

**핵심**: TS 타입은 **런타임에 완전히 사라진다**. `as`, generic `<T>`, interface는 모두 JS에서 제거됨. 런타임 타입 검사가 필요하면 Zod, io-ts 같은 라이브러리를 사용해야 한다.

---

## 📎 출처

1. [V8 Blog (v8.dev)](https://v8.dev/blog) — V8 엔진 공식 블로그
2. [Node.js Event Loop (공식)](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick) — 이벤트 루프 가이드
3. [TypeScript Handbook: tsconfig Reference](https://www.typescriptlang.org/tsconfig/) — tsconfig 옵션

---

> 📌 **이전 문서**: [[01-js-ts-philosophy-and-differentiation]]
> 📌 **다음 문서**: [[03-js-ts-basic-syntax]]
