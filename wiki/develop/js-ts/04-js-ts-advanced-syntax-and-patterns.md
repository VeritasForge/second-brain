---
created: 2026-04-21
source: claude-code
tags: [javascript, typescript, advanced, async, generics, proxy, react, node, conditional-types, utility-types]
---

# 📖 JS/TS 고급 문법과 패턴 — 프로덕션 수준의 풀스택

> 💡 **한줄 요약**: JS/TS의 고급 영역은 TypeScript의 강력한 타입 시스템(조건부 타입, 매핑 타입), async/await 패턴, Proxy/Reflect 메타프로그래밍, 그리고 React/Node.js 프로덕션 패턴을 포함하며, 프론트엔드+백엔드를 단일 언어로 커버하는 유일한 생태계다.
>
> 📌 **핵심 키워드**: Conditional Types, Mapped Types, Promise.allSettled, Proxy, React Hooks, Nest.js DI
> 📅 **기준**: ES2024 / TypeScript 5.x (2025)

---

## 1️⃣ TypeScript 고급 타입

### Discriminated Union (판별 유니온)

```typescript
type Result<T> =
    | { status: "success"; data: T }
    | { status: "error"; error: Error }
    | { status: "loading" };

function handle(result: Result<User>) {
    switch (result.status) {
        case "success": return result.data;     // data 접근 가능 (narrowing)
        case "error": throw result.error;        // error 접근 가능
        case "loading": return null;
    }
}
```

> Kotlin의 sealed class와 동일한 패턴. TS에서는 `status` 필드가 판별자(discriminant) 역할.

### Conditional Types

```typescript
type IsString<T> = T extends string ? "yes" : "no";
type A = IsString<string>;  // "yes"
type B = IsString<number>;  // "no"

// infer: 타입 추출
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;
type Unpacked<T> = T extends Promise<infer U> ? U : T;
```

### Mapped Types

```typescript
// 모든 프로퍼티를 선택적으로
type Partial<T> = { [K in keyof T]?: T[K] };

// 모든 프로퍼티를 읽기 전용으로
type Readonly<T> = { readonly [K in keyof T]: T[K] };

// 특정 키만 선택
type Pick<T, K extends keyof T> = { [P in K]: T[P] };
```

### Template Literal Types

```typescript
type EventName = `on${Capitalize<"click" | "focus" | "blur">}`;
// → "onClick" | "onFocus" | "onBlur"

type HTTPMethod = "GET" | "POST" | "PUT" | "DELETE";
type Endpoint = `/${string}`;
type Route = `${HTTPMethod} ${Endpoint}`;
// → "GET /users" | "POST /users" | ...
```

### 주요 Utility Types

| Utility | 효과 | 용도 |
|---------|------|------|
| `Partial<T>` | 모든 프로퍼티 선택적 | 업데이트 DTO |
| `Required<T>` | 모든 프로퍼티 필수 | 완전한 객체 |
| `Pick<T, K>` | 특정 키만 선택 | 부분 뷰 |
| `Omit<T, K>` | 특정 키 제외 | 민감 필드 제거 |
| `Record<K, V>` | 키-값 매핑 | 딕셔너리 |
| `Exclude<T, U>` | 유니온에서 제거 | 타입 필터링 |
| `Extract<T, U>` | 유니온에서 추출 | 타입 필터링 |
| `NonNullable<T>` | null/undefined 제거 | 안전한 타입 |
| `ReturnType<T>` | 함수 반환 타입 추출 | 타입 추론 |
| `Awaited<T>` | Promise 언래핑 | async 반환 타입 |

### 🔄 4개 언어 비교

| 개념 | TS | Go | Python | Kotlin |
|------|-----|-----|--------|--------|
| 조건부 타입 | `T extends U ? A : B` | 없음 | 없음 | 없음 |
| 매핑 타입 | `{[K in keyof T]: ...}` | 없음 | 없음 | 없음 |
| 유틸리티 타입 | Partial, Pick, Omit 등 | 없음 | 없음 | 없음 |
| 판별 유니온 | discriminated union | type switch | match/case | sealed class |

> TS의 타입 시스템은 **튜링 완전** — 타입 수준에서 프로그래밍 가능 (다른 4개 언어에 없는 고유 능력)

---

## 2️⃣ Async 패턴

### Promise 조합

```typescript
// 모두 성공해야 — 하나라도 실패하면 즉시 reject
const [user, orders] = await Promise.all([
    fetchUser(id),
    fetchOrders(id),
]);

// 모든 결과 수집 — 실패해도 계속
const results = await Promise.allSettled([
    fetchUser(1),
    fetchUser(2),  // 실패해도 OK
]);
results.forEach(r => {
    if (r.status === "fulfilled") process(r.value);
    else logError(r.reason);
});

// 가장 빠른 성공 — 모두 실패하면 AggregateError
const fastest = await Promise.any([
    fetchFromCDN1(url),
    fetchFromCDN2(url),
]);
```

### AsyncIterator

```typescript
async function* paginate(url: string) {
    let page = 1;
    while (true) {
        const response = await fetch(`${url}?page=${page}`);
        const data = await response.json();
        if (data.length === 0) break;
        yield* data;
        page++;
    }
}

for await (const item of paginate("/api/users")) {
    process(item);
}
```

### 🔄 4개 언어 비교

| 패턴 | JS/TS | Go | Python | Kotlin |
|------|-------|-----|--------|--------|
| 병렬 대기 | `Promise.all()` | `sync.WaitGroup` | `asyncio.gather()` | `coroutineScope + async` |
| 부분 실패 허용 | `Promise.allSettled()` | 수동 구현 | `asyncio.gather(return_exceptions)` | `supervisorScope` |
| 스트림 | `AsyncIterator` | channel | `async for` | `Flow` |

---

## 3️⃣ TypeScript Generics

```typescript
// 기본 제네릭
function first<T>(arr: T[]): T | undefined {
    return arr[0];
}

// 제약 (extends)
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
    return obj[key];
}

// 제네릭 클래스
class Queue<T> {
    private items: T[] = [];
    enqueue(item: T): void { this.items.push(item); }
    dequeue(): T | undefined { return this.items.shift(); }
}
```

---

## 4️⃣ Proxy와 Reflect

```typescript
const handler: ProxyHandler<any> = {
    get(target, prop, receiver) {
        console.log(`접근: ${String(prop)}`);
        return Reflect.get(target, prop, receiver);
    },
    set(target, prop, value, receiver) {
        console.log(`설정: ${String(prop)} = ${value}`);
        return Reflect.set(target, prop, value, receiver);
    },
};

const user = new Proxy({ name: "TS" }, handler);
user.name;         // 로그: "접근: name"
user.age = 10;     // 로그: "설정: age = 10"
```

**실무 활용**: Vue 3의 반응성 시스템, Immer의 불변 업데이트, MobX 상태 추적이 모두 Proxy 기반.

---

## 5️⃣ Web API와 패턴

### Fetch + AbortController

```typescript
const controller = new AbortController();

// 타임아웃 설정
setTimeout(() => controller.abort(), 5000);

const response = await fetch("/api/data", {
    signal: controller.signal,
});
```

### WebSocket

```typescript
const ws = new WebSocket("wss://api.example.com/ws");

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateUI(data);
};
```

### Streams API

```typescript
const response = await fetch("/api/large-data");
const reader = response.body!.getReader();

while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    process(value);  // 청크 단위 처리
}
```

> 📌 SSE 패턴: [[sse-event-design-strategy-snapshot-vs-delta]]

---

## 6️⃣ React 패턴 (프론트엔드)

> 📌 상세: [[react-hydration-ssr-deep-dive]], [[react-server-components-rsc-deep-dive]]

### Custom Hook

```typescript
function useUser(id: number) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        fetchUser(id).then(setUser).finally(() => setLoading(false));
    }, [id]);
    
    return { user, loading };
}

// 사용
function UserProfile({ id }: { id: number }) {
    const { user, loading } = useUser(id);
    if (loading) return <Spinner />;
    return <div>{user?.name}</div>;
}
```

### Server Components (RSC) 요약

```
┌─────────────┐    ┌─────────────┐
│ Server       │    │ Client      │
│ Component    │    │ Component   │
│ (서버에서    │    │ (브라우저   │
│  렌더링)     │    │  에서 실행)  │
│              │    │              │
│ • DB 접근 OK │    │ • useState  │
│ • API 호출   │    │ • onClick   │
│ • 번들 제외  │    │ • 인터랙션  │
└─────────────┘    └─────────────┘
```

---

## 7️⃣ Node.js 백엔드 패턴

### Express / Fastify 미들웨어

```typescript
// Express 미들웨어 체인
app.use(cors());
app.use(helmet());
app.use(express.json());

app.get("/users/:id", async (req, res) => {
    const user = await userService.getById(req.params.id);
    res.json(user);
});
```

### Nest.js DI (Spring 스타일)

```typescript
@Injectable()
class UserService {
    constructor(
        @Inject(UserRepository)
        private readonly userRepo: UserRepository,
    ) {}
    
    async getUser(id: number): Promise<User> {
        return this.userRepo.findById(id);
    }
}

@Controller("users")
class UserController {
    constructor(private readonly userService: UserService) {}
    
    @Get(":id")
    async getUser(@Param("id") id: number): Promise<User> {
        return this.userService.getUser(id);
    }
}
```

---

## 8️⃣ 함수형 패턴

### Array 메서드 체이닝

```typescript
const result = users
    .filter(u => u.age >= 18)
    .map(u => ({ name: u.name, email: u.email }))
    .sort((a, b) => a.name.localeCompare(b.name))
    .slice(0, 10);
```

### 불변 업데이트 패턴

```typescript
// Spread로 불변 업데이트
const updated = {
    ...state,
    user: { ...state.user, name: "New Name" },
};

// Immer (Proxy 기반)
import produce from "immer";
const next = produce(state, draft => {
    draft.user.name = "New Name";  // 가변처럼 쓰지만 불변
});
```

---

## 📎 출처

1. [TypeScript Handbook: Advanced Types](https://www.typescriptlang.org/docs/handbook/2/types-from-types.html) — 고급 타입
2. [MDN: Proxy](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Proxy) — Proxy API
3. [React Documentation](https://react.dev/) — React 공식 문서
4. [Nest.js Documentation](https://docs.nestjs.com/) — Nest.js DI 패턴

---

> 📌 **이전 문서**: [[03-js-ts-basic-syntax]]
> 📌 **다음 문서**: [[05-js-ts-developer-essentials-by-seniority]]
> 📌 **관련**: [[react-hydration-ssr-deep-dive]], [[react-server-components-rsc-deep-dive]], [[sse-event-design-strategy-snapshot-vs-delta]]
