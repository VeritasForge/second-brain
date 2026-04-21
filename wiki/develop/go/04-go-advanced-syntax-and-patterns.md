---
created: 2026-04-21
source: claude-code
tags: [golang, advanced, generics, context, reflection, concurrency-patterns, sync, error-handling, functional-options]
---

# 📖 Go 고급 문법과 패턴 — 프로덕션 수준의 Go

> 💡 **한줄 요약**: Go의 고급 문법은 제네릭/컨텍스트/리플렉션/unsafe 등 런타임과 타입 시스템의 경계를 다루며, 이들을 올바르게 조합하면 프로덕션 수준의 견고한 동시성 패턴과 추상화를 구현할 수 있다.
>
> 📌 **핵심 키워드**: GCShape Stenciling, Context Propagation, Fan-out/Fan-in, Functional Options, Error Wrapping
> 📅 **기준**: Go 1.24 (2025.02)

---

## 1️⃣ Generics (Go 1.18+)

### Type Parameters 문법

```go
// 제네릭 함수
func Map[T, U any](s []T, f func(T) U) []U {
    result := make([]U, len(s))
    for i, v := range s {
        result[i] = f(v)
    }
    return result
}

// 사용
names := Map([]int{1, 2, 3}, func(n int) string {
    return fmt.Sprintf("Item_%d", n)
})
// → ["Item_1", "Item_2", "Item_3"]
```

### Type Constraints와 interface 조합

```go
// 기본 제약
type Number interface {
    ~int | ~int32 | ~int64 | ~float32 | ~float64
}

func Sum[T Number](nums []T) T {
    var total T
    for _, n := range nums {
        total += n
    }
    return total
}

// ~int: int를 기반(underlying type)으로 하는 모든 타입 허용
type UserID int
Sum([]UserID{1, 2, 3})  // ~int 덕분에 가능
```

### comparable, any, constraints

| 제약 | 의미 | 용도 |
|------|------|------|
| `any` | 아무 타입 | 제약 없는 제네릭 |
| `comparable` | `==`, `!=` 비교 가능 | map 키, 중복 검사 |
| `constraints.Ordered` | `<`, `>` 비교 가능 | 정렬, 최소/최대 |

### 제네릭 사용이 적절한 경우 vs 과도한 경우

| ✅ 적절한 사용 | ❌ 과도한 사용 |
|---------------|--------------|
| 컬렉션 유틸리티 (Map, Filter, Reduce) | 1-2가지 타입만 쓰는 함수 |
| 자료구조 (Stack, Queue, Tree) | 비즈니스 로직 |
| 타입 안전한 결과 래퍼 | 이미 interface로 충분한 경우 |

### 🔧 GCShape Stenciling — Go의 제네릭 구현 방식

Go는 **Full Monomorphization** (Rust)도 아니고 **Pure Dictionary** (Java erasure)도 아닌, **GCShape Stenciling + Dictionary** 하이브리드를 사용한다:

```
┌────────────────────────────────────────────────────┐
│              제네릭 구현 스펙트럼                     │
│                                                      │
│  Pure Dictionary ◄───────────────► Full Stenciling   │
│  (Java erasure)     Go (GCShape)    (Rust/C++)       │
│                        │                              │
│  런타임 오버헤드 ↑    │    바이너리 크기 ↑           │
│  바이너리 크기 ↓     │    런타임 오버헤드 ↓          │
└────────────────────────────────────────────────────┘
```

**GCShape**: 타입의 크기(size), 정렬(alignment), 포인터 포함 여부가 같으면 같은 GCShape. 같은 GCShape의 타입들은 **하나의 코드**를 공유하고, **dictionary** 인자로 타입별 차이를 처리한다.

```
func Sum[T Number](nums []T) T

  int32 호출 ─┐
              ├── 같은 GCShape → 하나의 코드 + dictionary
  float32 호출─┘

  int64 호출 ─── 다른 GCShape → 별도 코드 생성
```

**트레이드오프**: 인터페이스 메서드 호출이 ��파일 타임에 완전히 해소되지 않아 인라이닝 기회를 잃을 수 있다. 성능 민감 코드에서는 벤치마크 필수.

### 🔄 다른 언어와 비교

| 측면 | Go (GCShape) | Python (typing.Generic) | JavaScript (TS) | Kotlin (JVM) | Rust |
|------|-------------|----------------------|----------------|-------------|------|
| 구현 | 컴파일 타임 stenciling | 런타임 없음 (힌트만) | 컴파일 타임 제거 | Type erasure (JVM) | Full monomorphization |
| 런타임 비용 | dictionary 조회 | 없음 (타입 검사 안 함) | 없음 | boxing | 없음 |
| 바이너리 크기 | 중간 | N/A | N/A | 작음 | 큼 (타입별 코드) |

---

## 2️⃣ Context 패턴

### context.Context 인터페이스

```go
type Context interface {
    Deadline() (deadline time.Time, ok bool)
    Done() <-chan struct{}
    Err() error
    Value(key any) any
}
```

### WithCancel, WithTimeout, WithDeadline, WithValue

```go
// 취소 가능한 context
ctx, cancel := context.WithCancel(context.Background())
defer cancel()

// 타임아웃 (3초 후 자동 취소)
ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
defer cancel()

// 데드라인 (특정 시각에 취소)
ctx, cancel := context.WithDeadline(context.Background(), time.Now().Add(5*time.Second))
defer cancel()

// 값 전달 (요청 ID 등)
ctx = context.WithValue(ctx, "requestID", "abc-123")
```

### Context Propagation 패턴

```go
func handler(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()  // HTTP 요청의 context
    
    user, err := getUser(ctx, userID)      // ctx 전파
    if err != nil { ... }
    
    orders, err := getOrders(ctx, user.ID)  // ctx 전파
    if err != nil { ... }
}

func getUser(ctx context.Context, id int) (*User, error) {
    // ctx.Done()을 통해 취소 신호 감지
    select {
    case <-ctx.Done():
        return nil, ctx.Err()
    default:
        // DB 쿼리 등
    }
}
```

```
HTTP Request
    │
    ▼
  handler(ctx) ──► getUser(ctx) ──► DB Query(ctx)
    │                                     │
    │              취소 신호 전파           │
    ◄─────────────────────────────────────┘
    (클라이언트가 연결 끊으면 전체 체인 취소)
```

### ⚠️ Anti-pattern: Context에 비즈니스 데이터 넣기

```go
// ❌ BAD: 비즈니스 로직을 context에 숨김
ctx = context.WithValue(ctx, "user", user)
ctx = context.WithValue(ctx, "permissions", perms)

// ✅ GOOD: 함수 인자로 명시적 전달
func processOrder(ctx context.Context, user *User, perms Permissions) error
```

Context의 Value는 **요청 범위 메타데이터**(요청 ID, 트레이스 ID)에만 사용하고, 비즈니스 데이터는 명시적 함수 인자로 전달한다.

### 🔄 다른 언어와 비교

| 개념 | Go (context.Context) | Python (contextvars) | JavaScript | Kotlin |
|------|---------------------|---------------------|-----------|--------|
| 취소 전파 | `ctx.Done()` 채널 | asyncio.Task.cancel() | AbortController | coroutineContext + Job.cancel() |
| 타임아웃 | `WithTimeout` | `asyncio.timeout()` | `setTimeout` | `withTimeout {}` |
| 값 전파 | `WithValue` | `ContextVar` | AsyncLocalStorage | `CoroutineContext[Key]` |

---

## 3️⃣ 동시성 패턴 (Channel 활용)

> 📌 Channel 내부 동작(hchan, sudog)은 [[go-channel-deep-dive]] 참조

### Fan-out / Fan-in

```
              ┌── Worker 1 ──┐
              │               │
  Producer ───┼── Worker 2 ──┼──► Collector
              │               │
              └── Worker 3 ──┘
  
  Fan-out: 하나의 입력을     Fan-in: 여러 출력을
  여러 worker가 병렬 처리    하나의 채널로 합침
```

```go
func fanOut(in <-chan int, workers int) []<-chan int {
    outs := make([]<-chan int, workers)
    for i := 0; i < workers; i++ {
        outs[i] = process(in)
    }
    return outs
}

func fanIn(channels ...<-chan int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup
    for _, ch := range channels {
        wg.Add(1)
        go func(c <-chan int) {
            defer wg.Done()
            for v := range c {
                out <- v
            }
        }(ch)
    }
    go func() {
        wg.Wait()
        close(out)
    }()
    return out
}
```

### Pipeline 패턴

```
  Generate ──► Square ──► Filter ──► Print
  (1,2,3,4)   (1,4,9,16)  (>5)      (9,16)
```

```go
func generate(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            out <- n
        }
    }()
    return out
}

func square(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            out <- n * n
        }
    }()
    return out
}

// 사용: 파이프 연결
pipeline := square(generate(1, 2, 3, 4))
for v := range pipeline {
    fmt.Println(v)  // 1, 4, 9, 16
}
```

### Worker Pool 패턴

```go
func workerPool(ctx context.Context, jobs <-chan Job, results chan<- Result, workers int) {
    var wg sync.WaitGroup
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            for job := range jobs {
                select {
                case <-ctx.Done():
                    return
                default:
                    results <- process(job)
                }
            }
        }(i)
    }
    go func() {
        wg.Wait()
        close(results)
    }()
}
```

### Rate Limiting

```go
// 토큰 버킷 방식
limiter := rate.NewLimiter(rate.Every(100*time.Millisecond), 10) // 초당 10개, 버스트 10

for req := range requests {
    if err := limiter.Wait(ctx); err != nil {
        break  // context 취소
    }
    process(req)
}
```

### Graceful Shutdown 패턴

```go
func main() {
    ctx, stop := signal.NotifyContext(context.Background(), 
        syscall.SIGINT, syscall.SIGTERM)
    defer stop()

    srv := &http.Server{Addr: ":8080"}
    
    go func() {
        if err := srv.ListenAndServe(); err != http.ErrServerClosed {
            log.Fatal(err)
        }
    }()

    <-ctx.Done()  // 시그널 대기
    
    shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    srv.Shutdown(shutdownCtx)  // 진행 중 요청 완료 대기
}
```

---

## 4️⃣ sync 패키지 심화

| 타입 | 용도 | 핵심 특성 |
|------|------|----------|
| `sync.Mutex` | 상호 배제 | 가장 기본적인 락 |
| `sync.RWMutex` | 읽기/쓰기 분리 | 여러 reader 동시 허용, writer는 단독 |
| `sync.WaitGroup` | goroutine 완료 대기 | Add → Done → Wait |
| `sync.Once` | 한 번만 실행 | 지연 초기화(lazy init)에 적합 |
| `sync.Pool` | 객체 재사용 | GC 친화적, 임시 객체 캐싱 |
| `sync.Map` | 동시 안전 map | 읽기 많고 쓰기 적은 경우에 최적 |
| `sync/atomic` | 원자적 연산 | 락 없이 카운터/플래그 업데이트 |

### sync.Once (Lazy Initialization)

```go
var (
    instance *DB
    once     sync.Once
)

func GetDB() *DB {
    once.Do(func() {
        instance = connectDB()  // 최초 1회만 실행
    })
    return instance
}
```

### sync.Pool (GC 친화적 객체 재사용)

```go
var bufPool = sync.Pool{
    New: func() any {
        return new(bytes.Buffer)
    },
}

func process() {
    buf := bufPool.Get().(*bytes.Buffer)
    defer func() {
        buf.Reset()
        bufPool.Put(buf)  // 재사용을 위해 반환
    }()
    // buf 사용
}
```

> ⚠️ **주의**: Pool의 객체는 GC 때 제거될 수 있다. 영구 캐시로 사용하지 말 것.

### sync.Map — 언제 쓸 것인가

```go
// ✅ 적합: 키가 안정적이고 읽기가 대부분
var cache sync.Map
cache.Store("key", value)
v, ok := cache.Load("key")

// ❌ 부적합: 쓰기가 빈번하거나, 범위 순회가 필요한 경우
// → map + sync.RWMutex가 더 효율적
```

### 🔄 다른 언어와 비교

| 개념 | Go | Python | JavaScript | Kotlin |
|------|-----|--------|-----------|--------|
| 뮤텍스 | `sync.Mutex` | `threading.Lock` | N/A (단일 스레드) | `ReentrantLock` |
| 한 번 실행 | `sync.Once` | `functools.lru_cache(1)` | N/A | `lazy val` |
| 원자적 연산 | `sync/atomic` | N/A (GIL) | `Atomics` (SharedArrayBuffer) | `AtomicInteger` |

---

## 5️⃣ Reflection과 unsafe

### reflect 패키지 기본

```go
v := 42
t := reflect.TypeOf(v)   // int
val := reflect.ValueOf(v) // 42

fmt.Println(t.Kind())    // int
fmt.Println(val.Int())   // 42
```

### Struct Tag 읽기 (JSON, DB 매핑의 원리)

```go
type User struct {
    Name  string `json:"name" db:"user_name"`
    Email string `json:"email" validate:"required,email"`
}

t := reflect.TypeOf(User{})
field, _ := t.FieldByName("Name")
fmt.Println(field.Tag.Get("json"))     // "name"
fmt.Println(field.Tag.Get("db"))       // "user_name"
```

이것이 `encoding/json`, `database/sql`, validator 라이브러리가 작동하는 원리다.

### reflect의 성능 비용

| 연�� | 직접 접근 | reflect 사용 | 배수 |
|------|---------|------------|------|
| 필드 읽기 | ~1ns | ~100ns | ~100× |
| 메서드 호출 | ~2ns | ~200ns | ~100× |
| 구조체 생성 | ~5ns | ~500ns | ~100× |

> Go Proverb #14: "Reflection is never clear" — 가능하면 피하고, 제네릭(1.18+)이나 코드 생성(`go generate`)으로 대체하라.

### unsafe.Pointer

```go
// unsafe.Pointer: 모든 포인터 타입 간 변환 허용
var x int64 = 42
p := unsafe.Pointer(&x)
fp := (*float64)(p)  // int64의 메모리를 float64로 해��
```

> Go Proverb #12: "With the unsafe package there are no guarantees" — Go의 메모리 안전, GC 안전, 호환성 보장이 모두 사라진다. 런타임 내부 최적화나 시스템 프로그래밍에서만 사용.

### 컴파일러 디렉티브

```go
//go:noescape    // 이 함수의 인자가 힙에 escape하지 않음을 컴파일러에 선언
//go:linkname    // 다른 패키지의 비공개 심볼에 접근
//go:nosplit     // 스택 분할 검사 건너뛰기
//go:noinline    // 인라이닝 금지
```

---

## 6️⃣ 에러 처리 고급

> 📌 기초: [[03-go-basic-syntax]] §7 참조

### Error Wrapping (fmt.Errorf + %w)

```go
func getUser(id int) (*User, error) {
    row := db.QueryRow("SELECT ...", id)
    if err := row.Scan(&user); err != nil {
        return nil, fmt.Errorf("사용자 %d 조회 실패: %w", id, err)
    }
    return &user, nil
}
// 에러 메시지: "사용자 42 조회 실패: sql: no rows in result set"
```

### errors.Is / errors.As 체인

```go
// errors.Is: 에러 체인에서 특정 에러 찾기
if errors.Is(err, sql.ErrNoRows) {
    return nil, ErrNotFound
}

// errors.As: 에러 체인에서 특정 타입 찾기
var pathErr *os.PathError
if errors.As(err, &pathErr) {
    fmt.Println("경로:", pathErr.Path)
}
```

```
에러 체인 (wrapping):

  "사용자 42 조회 실패"
    └── wraps: "DB 연결 실패"
          └── wraps: "dial tcp: connection refused"

  errors.Is(err, ErrConnRefused) → true (체인 전체 탐색)
```

### Sentinel Errors vs Custom Error Types

```go
// Sentinel: 패키지 수준 변수
var (
    ErrNotFound    = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
)

// Custom Type: 추가 정보 포함
type ValidationError struct {
    Field   string
    Message string
}
func (e *ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Message)
}
```

### 에러 처리 전략 설계

```
┌─────────────────────────────────────────┐
│         에러 처리 계층                    │
│                                          │
│  [HTTP Handler]  ← 에러를 HTTP 응답으로  │
│       │            변환 (최종 처리)       │
│       ▼                                  │
│  [Service Layer] ← 비즈니스 에러로 변환  │
│       │            (도메인 에러 타입)     │
│       ▼                                  │
│  [Repository]    ← 인프라 에러에 문맥    │
│       │            추가 (%w wrapping)    │
│       ▼                                  │
│  [Database/API]  ← 원본 에러 발생        │
└─────────────────────────────────────────┘
```

### 🔄 다른 언어와 비교

| 개념 | Go | Python | JavaScript | Kotlin |
|------|-----|--------|-----------|--------|
| 에러 체이닝 | `%w` + `errors.Is/As` | `raise from` | `Error(msg, {cause})` | `cause` property |
| 커스텀 에러 | error interface 구현 | Exception 상속 | Error 상속 | sealed class |
| 패턴 매�� | type switch | except 체인 | catch 체인 | `when(e)` |

---

## 7️⃣ 인터페이스 고급 패턴

### Embedding으로 Composition

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

// 작은 인터페이스를 조합해서 큰 인터페이스 생성
type ReadWriter interface {
    Reader
    Writer
}
```

> Go Proverb #4: "The bigger the interface, the weaker the abstraction" — `io.Reader`(1 메서드)가 `ReadWriteCloserSeeker`보다 강력한 추상화이다.

### Functional Options 패턴

```go
type Server struct {
    port    int
    timeout time.Duration
    logger  *log.Logger
}

type Option func(*Server)

func WithPort(port int) Option {
    return func(s *Server) { s.port = port }
}

func WithTimeout(d time.Duration) Option {
    return func(s *Server) { s.timeout = d }
}

func NewServer(opts ...Option) *Server {
    s := &Server{port: 8080, timeout: 30 * time.Second}  // 기본값
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// 사용: 읽기 쉽고 확장 가능
srv := NewServer(
    WithPort(9090),
    WithTimeout(1 * time.Minute),
)
```

### Accept Interfaces, Return Structs 원칙

```go
// ✅ GOOD: 인터페이스를 받고, 구체 타입을 반환
func Process(r io.Reader) *Result {
    // r은 파일, 네트워크, 버퍼 등 무엇이든 가능
    data, _ := io.ReadAll(r)
    return &Result{Data: data}
}

// ❌ BAD: 구체 타입을 받음
func Process(f *os.File) *Result { ... }
```

### Interface Segregation (io.Reader 설계 원리)

```
io 패키지의 인터페이스 설계:

  io.Reader      (1 메서드)  ← 가장 많이 사용
  io.Writer      (1 메서드)
  io.Closer      (1 메서드)
  io.ReadWriter  (2 메서드 = Reader + Writer)
  io.ReadCloser  (2 메서드 = Reader + Closer)
  io.ReadWriteCloser (3 메서드)

  최소한의 인터페이스 → 최대한의 호환성
```

---

## 8️⃣ 코드 생성과 빌드

### go generate

```go
//go:generate stringer -type=Weekday
//go:generate mockgen -source=repository.go -destination=mock_repository.go
```

```bash
go generate ./...  # 모든 패키지의 //go:generate 실행
```

### Build Tags / Build Constraints

```go
//go:build linux && amd64
// +build linux,amd64  (Go 1.16 이전 문법)

package mypackage
// 이 파일은 linux/amd64에서만 컴파일됨
```

### //go:embed

```go
import "embed"

//go:embed templates/*.html
var templates embed.FS

//go:embed version.txt
var version string

//go:embed logo.png
var logo []byte
```

### internal 패키지 규칙

```
myproject/
├── cmd/
├── internal/        ← 이 패키지는 myproject 내에서만 import 가능
│   ├── auth/        ← 외부 모듈에서 import 불가 (컴파일러가 강제)
│   └── database/
└── pkg/             ← 외부에서도 import 가능
    └── api/
```

### go.mod tool 지시어 (Go 1.24)

```
// go.mod
module myproject

go 1.24

tool (
    golang.org/x/tools/cmd/stringer
    github.com/golang/mock/mockgen
)
```

`go.mod`의 `tool` 지시어로 실행 파일 의존성을 표준화. 기존의 `tools.go` 해킹 패턴 대체.

---

## 📎 출처

1. [Go Generics Implementation: GCShape Stenciling](https://go.googlesource.com/proposal/+/refs/heads/master/design/generics-implementation-gcshape.md) — 공식 설계 제안서
2. [Generics can make your Go code slower — PlanetScale](https://planetscale.com/blog/generics-can-make-your-go-code-slower) — 성능 분석
3. [Go Concurrency Patterns — Go Blog](https://go.dev/blog/pipelines) — Pipeline, Fan-out/Fan-in 공식 가이드
4. [Context — Go Blog](https://go.dev/blog/context) — Context 사용 가이드
5. [Working with Errors in Go 1.13+](https://go.dev/blog/go1.13-errors) — Error wrapping 공식 가이드
6. [Effective Go](https://go.dev/doc/effective_go) — 인터페이스, 에러, 동시성 패턴

---

> 📌 **이전 문서**: [[03-go-basic-syntax]] — Go 기본 문법
> 📌 **다음 문서**: [[05-go-developer-essentials-by-seniority]] — Go 개발자 필수 지식
> 📌 **상세 문서**: [[go-channel-deep-dive]], [[goroutine-gmp-scheduler-deep-dive]], [[monkey-patching-and-uber-fx-deep-dive]]
