---
created: 2026-04-21
source: claude-code
tags: [javascript, typescript, syntax, basics, this, prototype, module, type-system, destructuring]
---

# 📖 JS/TS 기본 문법 — this부터 TypeScript 타입까지

> 💡 **한줄 요약**: JS/TS의 기본 문법은 CJS/ESM 이중 모듈 시스템, `this` 바인딩의 복잡성, 프로토타입 기반 OOP, 그리고 TypeScript의 구조적 타입 시스템으로 구성되며, 구조 분해와 스프레드 연산자가 관용적 코드의 핵심이다.
>
> 📌 **핵심 키워드**: ESM, `this`, prototype, structural typing, destructuring, optional chaining
> 📅 **기준**: ES2024 / TypeScript 5.x (2025)

---

## 1️⃣ 모듈 시스템

### CommonJS vs ESM

```javascript
// CommonJS (Node.js 전통) — 동기 로딩
const fs = require('fs');
module.exports = { myFunc };

// ESM (ES2015+) — 비동기 로딩, 정적 분석 가능
import fs from 'fs';
export function myFunc() {}
export default class MyClass {}
```

| 특성 | CommonJS (CJS) | ESM |
|------|---------------|-----|
| 로딩 | 동기 | 비동기 |
| 정적 분석 | ❌ (동적 require) | ✅ (tree-shaking 가능) |
| `this` | `module.exports` | `undefined` |
| 확장자 | `.js` (기본) | `.mjs` 또는 `"type": "module"` |
| 현재 추세 | 레거시 | **표준** (권장) |

### 🔄 4개 언어 비교

| 개념 | JS/TS | Go | Python | Kotlin |
|------|-------|-----|--------|--------|
| 모듈 | CJS/ESM (이중!) | package (단일) | import (단일) | package (단일) |
| 의존성 | `package.json` | `go.mod` | `pyproject.toml` | `build.gradle.kts` |
| Tree-shaking | ✅ (ESM) | 링커가 자동 | ❌ | ProGuard/R8 |

---

## 2️⃣ 변수, 타입, TS 타입 시스템

### let / const / var

```javascript
const name = "TS";    // 재할당 불가 (권장)
let age = 10;         // 재할당 가능
var legacy = "avoid"; // 함수 스코프 (비권장) — 호이스팅 주의
```

### JavaScript 기본 타입

| 타입 | 예시 | 특이사항 |
|------|------|---------|
| `number` | `42`, `3.14`, `NaN`, `Infinity` | 64비트 IEEE 754 (정수/실수 구분 없음!) |
| `bigint` | `42n` | 무한 정밀도 정수 |
| `string` | `"hello"`, `` `template ${var}` `` | 불변 |
| `boolean` | `true`, `false` | |
| `null` | `null` | "의도적 부재" |
| `undefined` | `undefined` | "아직 할당 안 됨" |
| `symbol` | `Symbol("id")` | 유니크 식별자 |
| `object` | `{}`, `[]`, `function` | 참조 타입 |

> ⚠️ `null`과 `undefined` 두 가지 부재값이 존재하는 것은 JS의 유명한 설계 결함. TS `strict`에서는 `strictNullChecks`로 구분.

### TypeScript 기본 타입

```typescript
// 기본
let name: string = "TS";
let age: number = 10;
let active: boolean = true;

// Union type
let id: string | number = "abc";

// Literal type
let direction: "up" | "down" | "left" | "right" = "up";

// Array
let nums: number[] = [1, 2, 3];
let names: Array<string> = ["a", "b"];

// Tuple
let pair: [string, number] = ["age", 25];

// Object type
interface User {
    name: string;
    age: number;
    email?: string;  // 선택적 프로퍼티
}
```

### 🔄 4개 언어 비교

| 개념 | JS/TS | Go | Python | Kotlin |
|------|-------|-----|--------|--------|
| Null 표현 | `null` + `undefined` (2개!) | nil (zero value) | `None` | `null` (Nullable `?`) |
| 타입 | 동적(JS) / 구조적(TS) | 정적 구조적 | 동적 + 힌트 | 정적 명목적 |
| 숫자 | `number` (하나!) | int/float 구분 | int/float 구분 | Int/Long/Double |

---

## 3️⃣ 제어 흐름

### Optional Chaining + Nullish Coalescing

```typescript
// Optional chaining (?.) — null이면 short-circuit
const city = user?.address?.city;

// Nullish coalescing (??) — null/undefined만 대체 (0, "", false는 유지)
const name = user?.name ?? "Anonymous";

// 비교: || 연산자는 falsy 값(0, "", false)도 대체함
const count = 0 || 10;  // 10 (의도하지 않은 결과!)
const count2 = 0 ?? 10; // 0 (의도한 결과)
```

### for...of / for...in

```typescript
// for...of: 값 순회 (배열, Map, Set, string)
for (const item of [1, 2, 3]) { }

// for...in: 키 순회 (객체) — 배열에는 비권장
for (const key in obj) { }

// forEach (배열)
[1, 2, 3].forEach((item, index) => { });
```

---

## 4️⃣ 함수와 `this`

### Arrow Function vs Function

```typescript
// Arrow function: this를 렉시컬로 캡처 (선언 시점의 this)
const add = (a: number, b: number): number => a + b;

// Function: this가 호출 시점에 결정
function greet() {
    console.log(this.name);  // this는 호출자에 따라 다름
}
```

### `this` 바인딩 규칙

```
┌─────────────────────────────────────────────────┐
│            this 결정 우선순위                      │
│                                                   │
│  1. new 키워드 → 새 객체                          │
│  2. call/apply/bind → 명시적 this                │
│  3. 메서드 호출 (obj.method()) → obj              │
│  4. 일반 함수 호출 → globalThis (strict: undefined)│
│  5. Arrow function → 상위 스코프의 this (렉시컬)  │
└─────────────────────────────────────────────────┘
```

> ⚠️ `this`는 JS에서 **가장 혼란스러운 개념**. Arrow function을 쓰면 대부분 해결된다.

### Rest / Spread

```typescript
// Rest parameters
function sum(...nums: number[]): number {
    return nums.reduce((a, b) => a + b, 0);
}

// Spread operator
const merged = { ...defaults, ...userConfig };
const combined = [...array1, ...array2];
```

### 🔄 4개 언어 비교

| 개념 | JS/TS | Go | Python | Kotlin |
|------|-------|-----|--------|--------|
| `this` | 호출 시점 결정 (복잡!) | receiver (명시적) | `self` (명시적) | `this` (클래스 내) |
| 가변 인자 | `...args` | `...int` | `*args, **kwargs` | `vararg` |
| 기본값 인자 | ✅ | ❌ | ✅ | ✅ |
| Arrow/Lambda | `() => {}` | `func() {}` | `lambda x: x` | `{ x -> x }` |

---

## 5️⃣ 데이터 구조

### Array / Object / Map / Set

```typescript
// Array
const arr: number[] = [1, 2, 3];
arr.push(4);
const [first, ...rest] = arr;  // 구조 분해

// Object
const user = { name: "TS", age: 10 };
const { name, age } = user;  // 구조 분해

// Map (키 타입 자유)
const map = new Map<string, number>();
map.set("a", 1);

// Set (중복 제거)
const unique = new Set([1, 2, 2, 3]);  // {1, 2, 3}

// WeakMap / WeakRef (GC 친화)
const cache = new WeakMap<object, string>();
```

### 🔄 4개 언어 비교

| 개념 | JS/TS | Go | Python | Kotlin |
|------|-------|-----|--------|--------|
| 해시맵 | `Map` / `Object` | `map[K]V` | `dict` | `Map` |
| 구조 분해 | `const {a, b} = obj` | 없음 | `a, b = tuple` | `val (a, b) = pair` |
| 불변 배열 | `ReadonlyArray<T>` (TS) | `[N]T` (array) | `tuple` | `List` |

---

## 6️⃣ 프로토타입과 클래스

### Prototype Chain

```javascript
// 모든 JS 객체는 [[Prototype]] 체인을 가진다
const animal = { speak() { return "..."; } };
const dog = Object.create(animal);
dog.bark = function() { return "멍!"; };

dog.bark();   // "멍!" — dog 자체 메서드
dog.speak();  // "..." — prototype chain으로 animal에서 찾음
```

### ES6 Class (문법적 설탕)

```typescript
class Animal {
    constructor(public name: string) {}  // TS: 파라미터 프로퍼티
    speak(): string { return "..."; }
}

class Dog extends Animal {
    #breed: string;  // private field (ES2022)
    
    constructor(name: string, breed: string) {
        super(name);
        this.#breed = breed;
    }
    
    speak(): string { return `${this.name}: 멍!`; }
}
```

> ES6 class는 prototype 기반 상속의 **문법적 설탕(syntactic sugar)**. 내부적으로는 여전히 prototype chain.

---

## 7️⃣ 에러 처리

### try / catch / finally

```typescript
try {
    const data = JSON.parse(input);
} catch (error) {
    if (error instanceof SyntaxError) {
        console.error("JSON 파싱 실패:", error.message);
    } else {
        throw error;  // 알 수 없는 에러는 재throw
    }
} finally {
    cleanup();
}
```

### Custom Error

```typescript
class AppError extends Error {
    constructor(
        message: string,
        public code: string,
        public statusCode: number = 500,
        options?: ErrorOptions,  // cause 지원
    ) {
        super(message, options);
        this.name = "AppError";
    }
}

// 에러 체이닝 (ES2022)
throw new AppError("User not found", "USER_NOT_FOUND", 404, {
    cause: originalError,
});
```

### 🔄 4개 언어 비교

| 개념 | JS/TS | Go | Python | Kotlin |
|------|-------|-----|--------|--------|
| 에러 모델 | 예외 + Promise.catch | 값 (T, error) | 예외 | 예외 + Result |
| 체이닝 | `{cause}` (ES2022) | `%w` | `raise from` | `cause` |
| 타입 안전 | catch의 error는 `unknown` | `error` interface | Exception 계층 | Exception 계층 |

---

## 8️⃣ 구조 분해와 스프레드

### Object Destructuring

```typescript
const { name, age, email = "none" } = user;  // 기본값
const { name: userName } = user;              // 이름 변경
const { address: { city } } = user;           // 중첩 분해
```

### Array Destructuring

```typescript
const [first, second, ...rest] = [1, 2, 3, 4, 5];
// first=1, second=2, rest=[3,4,5]

const [, , third] = [1, 2, 3];  // skip
// third=3
```

### Spread in Practice

```typescript
// 객체 합치기 (얕은 복사)
const config = { ...defaults, ...userConfig };

// 배열 합치기
const all = [...admins, ...users];

// 함수 인자 전개
Math.max(...numbers);
```

> 구조 분해 + 스프레드는 **JS/TS에서 가장 많이 사용되는 문법**. Go에는 없고, Python은 `*`/`**` 연산자로 유사하게 제공.

---

## 📎 출처

1. [MDN JavaScript Reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference) — JS 공식 레퍼런스
2. [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/) — TS 공식 가이드
3. [ES2024 Specification](https://tc39.es/ecma262/) — 최신 ECMAScript 스펙

---

> 📌 **이전 문서**: [[02-js-ts-architecture-and-runtime]]
> 📌 **다음 문서**: [[04-js-ts-advanced-syntax-and-patterns]]
