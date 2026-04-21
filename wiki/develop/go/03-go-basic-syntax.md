---
created: 2026-04-21
source: claude-code
tags: [golang, syntax, basics, type-system, struct, interface, error-handling, slice, map, pointer]
---

# 📖 Go 기본 문법 — 25개 키워드로 만드는 프로그램

> 💡 **한줄 요약**: Go의 기본 문법은 25개 키워드와 명시적 타입 시스템으로 구성되며, "선언이 곧 문서"라는 철학 아래 변수/함수/구조체/인터페이스/에러 처리의 패턴이 일관되게 설계되어 있다.
>
> 📌 **핵심 키워드**: zero value, multiple return, structural typing, slice, if err != nil
> 📅 **기준**: Go 1.24 (2025.02)

---

## 1️⃣ 패키지와 모듈 시스템

### package 선언과 import

```go
package main  // 실행 가능한 프로그램의 진입점

import (
    "fmt"           // 표준 라이브러리
    "net/http"      // 중첩 경로
    
    "github.com/gin-gonic/gin"  // 외부 모듈
)

func main() {
    fmt.Println("Hello, Go!")
}
```

**핵심 규칙**:
- 모든 `.go` 파일은 `package` 선언으로 시작
- `package main` + `func main()`이 프로그램 진입점
- **사용하지 않는 import는 컴파일 에러** (의존성 최소화 강제)

### go.mod / go.sum

```
myproject/
├── go.mod      ← 모듈 이름 + Go 버전 + 의존성 목록
├── go.sum      ← 의존성 체크섬 (무결성 보장)
├── main.go
└── internal/
    └── handler.go
```

```
// go.mod
module github.com/myname/myproject

go 1.24

require (
    github.com/gin-gonic/gin v1.9.1
)
```

### exported vs unexported (대문자 규칙)

```go
type User struct {
    Name  string  // 대문자 시작 → exported (public)
    email string  // 소문자 시작 → unexported (private)
}

func GetUser() {}   // exported
func validate() {}  // unexported
```

Go에는 `public/private/protected` 키워드가 없다. **첫 글자의 대소문자**가 가시성을 결정한다.

### init() 함수

```go
func init() {
    // 패키지 로드 시 자동 실행
    // 여러 init()이 있으면 파일 순서대로 실행
    // main() 이전에 실행됨
}
```

> ⚠️ **주의**: init()은 테스트와 디버깅을 어렵게 만든다. 꼭 필요한 경우(설정 검증 등)에만 사용.

### 🔄 다른 언어와 비교

| 개념 | Go | Python | JavaScript | Kotlin |
|------|-----|--------|-----------|--------|
| 모듈 선언 | `go.mod` | `requirements.txt`/`pyproject.toml` | `package.json` | `build.gradle.kts` |
| 가시성 | 대문자/소문자 | `_`접두사 (관습) | `export` 키워드 | `public/private/internal` |
| 패키지 구조 | 디렉터리 = 패키지 | `__init__.py` | `index.js` | 패키지 선언 자유 |
| 미사용 import | **컴파일 에러** | 경고 (무시 가능) | lint 경고 | 경고 (무시 가능) |

---

## 2️⃣ 변수, 상수, 타입 시스템

### var vs := (short declaration)

```go
// 명시적 선언
var name string = "Go"
var age int     // zero value: 0

// 짧은 선언 (함수 내에서만)
name := "Go"     // 타입 추론
age := 30
```

### 기본 타입

| 타입 | Zero Value | 설명 |
|------|-----------|------|
| `bool` | `false` | 참/거짓 |
| `int`, `int8`~`int64` | `0` | 정수 (int는 플랫폼 의존: 32/64bit) |
| `uint`, `uint8`~`uint64` | `0` | 부호 없는 정수 |
| `float32`, `float64` | `0.0` | 부동소수점 |
| `string` | `""` | UTF-8 문자열 (불변) |
| `byte` | `0` | `uint8`의 별칭 |
| `rune` | `0` | `int32`의 별칭 (유니코드 코드포인트) |

### Zero Value 철학: "Make the zero value useful"

```go
var b bytes.Buffer  // 선언만으로 바로 사용 가능!
b.WriteString("Hello")

var m sync.Mutex    // 선언만으로 즉시 Lock/Unlock 가능!
m.Lock()

var s []int         // nil slice도 append 가능!
s = append(s, 1, 2, 3)
```

**원칙**: 모든 타입은 선언만으로 유효한 상태를 가진다. 생성자(constructor)가 불필요한 경우가 많다.

### const와 iota

```go
const Pi = 3.14159

// iota: 연속 상수 자동 생성
type Weekday int
const (
    Sunday Weekday = iota  // 0
    Monday                  // 1
    Tuesday                 // 2
    Wednesday               // 3
)

// 비트 플래그 패턴
type Permission uint
const (
    Read    Permission = 1 << iota  // 1
    Write                           // 2
    Execute                         // 4
)
```

### 타입 변환 (명시적 only)

```go
var i int = 42
var f float64 = float64(i)    // 명시적 변환 필수
var u uint = uint(f)

// 아래는 컴파일 에러!
// var f float64 = i  // ← 암묵적 변환 없음
```

### 🔄 다른 언어와 비교

| 개념 | Go | Python | JavaScript | Kotlin |
|------|-----|--------|-----------|--------|
| 타입 시스템 | 정적, 명시적 변환 | 동적 | 동적, 암묵적 변환 | 정적, 스마트 캐스트 |
| Null/부재 | zero value (타입별 다름) | `None` | `null`/`undefined` | `null` (Nullable 타입) |
| 상수 | `const` (컴파일 타임) | 관습 (대문자) | `const` (런타임) | `const val` (컴파일 타임) |
| 타입 추론 | `:=` (함수 내) | 항상 | `let`/`const` | `val`/`var` |

---

## 3️⃣ 제어 흐름

### if (초기화문 포함)

```go
// 기본
if x > 10 {
    fmt.Println("크다")
}

// 초기화문 포함 (Go 고유!)
if err := validate(); err != nil {
    return err  // err은 이 블록에서만 유효
}

// 조건에 괄호 없음 — 중괄호는 필수
```

### for (Go의 유일한 루프)

```go
// C-style
for i := 0; i < 10; i++ { }

// while-style
for condition { }

// 무한 루프
for { }

// range (컬렉션 순회)
for i, v := range slice { }
for k, v := range myMap { }
for i, ch := range "Hello 세계" { }  // rune 단위 순회
```

Go에는 `while`, `do-while`이 없다. `for` 하나로 모든 루프를 표현한다.

### switch (break 불필요)

```go
switch day {
case "Monday":
    fmt.Println("월요일")  // 자동 break (C와 다름!)
case "Tuesday", "Wednesday":
    fmt.Println("화수")
default:
    fmt.Println("기타")
}

// 조건 없는 switch (if-else 대체)
switch {
case score >= 90:
    grade = "A"
case score >= 80:
    grade = "B"
default:
    grade = "C"
}

// fallthrough: 명시적으로 다음 case 실행
switch n {
case 1:
    fmt.Println("1")
    fallthrough  // 다음 case도 실행
case 2:
    fmt.Println("2")
}
```

### defer, panic, recover 기본

```go
// defer: 함수 종료 시 실행 (LIFO 순서)
func readFile() {
    f, _ := os.Open("file.txt")
    defer f.Close()  // 함수 끝나면 자동으로 닫힘
    // ... 파일 사용
}

// 여러 defer는 LIFO (Last In, First Out)
defer fmt.Println("1")  // 3번째 실행
defer fmt.Println("2")  // 2번째 실행
defer fmt.Println("3")  // 1번째 실행
// 출력: 3, 2, 1
```

### 🔄 다른 언어와 비교

| 개념 | Go | Python | JavaScript | Kotlin |
|------|-----|--------|-----------|--------|
| 루프 종류 | `for`만 (3가지 형태) | `for`, `while` | `for`, `while`, `for...of` | `for`, `while`, `forEach` |
| switch break | **자동** (fallthrough 명시) | match (3.10+) | **수동** break 필요 | `when` (자동) |
| 리소스 정리 | `defer` | `with` (context manager) | `finally` / `using` | `use` (Closeable) |
| 조건문 괄호 | 없음 | 없음 | 필수 | 필수 |

---

## 4️⃣ 함수와 메서드

### 다중 반환값

```go
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("0으로 나눌 수 없습니다")
    }
    return a / b, nil
}

result, err := divide(10, 3)
if err != nil {
    log.Fatal(err)
}
```

### Named return values

```go
func rectangle(w, h float64) (area, perimeter float64) {
    area = w * h
    perimeter = 2 * (w + h)
    return  // naked return (named values 자동 반환)
}
```

> ⚠️ **주의**: naked return은 짧은 함수에서만 사용. 긴 함수에서는 가독성 저하.

### 가변 인자 (variadic)

```go
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}

sum(1, 2, 3)       // 6
sum([]int{1,2,3}...) // 슬라이스 전개
```

### 일급 함수 / 클로저

```go
// 함수를 변수에 할당
add := func(a, b int) int { return a + b }
fmt.Println(add(1, 2))

// 클로저: 외부 변수 캡처
func counter() func() int {
    count := 0
    return func() int {
        count++
        return count
    }
}

c := counter()
c()  // 1
c()  // 2
```

### 메서드 — value receiver vs pointer receiver

```go
type Circle struct {
    Radius float64
}

// Value receiver: 복사본에서 동작
func (c Circle) Area() float64 {
    return 3.14 * c.Radius * c.Radius
}

// Pointer receiver: 원본을 수정
func (c *Circle) Scale(factor float64) {
    c.Radius *= factor  // 원본 변경
}
```

**결정 기준표**:

| 조건 | 사용할 receiver |
|------|---------------|
| 구조체 필드를 수정해야 한다 | `*T` (포인터) |
| 구조체가 크다 (복사 비용) | `*T` (포인터) |
| 일관성: 하나라도 `*T`이면 | `*T` (포인터) — 전부 통일 |
| 작고 읽기 전용 | `T` (값) — 하지만 위 규칙 우선 |

### 🔄 다른 언어와 비교

| 개념 | Go | Python | JavaScript | Kotlin |
|------|-----|--------|-----------|--------|
| 다중 반환 | 기본 지원 `(T, error)` | 튜플 반환 | 객체/배열 반환 | `Pair`/`Triple`/data class |
| 메서드 정의 | receiver function | class 메서드 | prototype/class | class 메서드 |
| 클로저 | ✅ 지원 | ✅ 지원 | ✅ 지원 | ✅ 지원 (람다) |
| 오버로딩 | ❌ 없음 | ❌ 없음 (관습적) | ❌ 없음 | ✅ 지원 |

---

## 5️⃣ 데이터 구조

### Array vs Slice

```go
// Array: 고정 길이, 값 타입
var arr [5]int = [5]int{1, 2, 3, 4, 5}

// Slice: 가변 길이, 참조 타입 (실제로는 array의 뷰)
s := []int{1, 2, 3}
s = append(s, 4, 5)
```

#### Slice 내부 구조

```
┌───────────────────────┐
│     Slice Header      │
│  ┌─────────────────┐  │
│  │ ptr  → ─────────│──│──► [ 1 | 2 | 3 | _ | _ | _ ]
│  │ len  = 3        │  │          ▲               ▲
│  │ cap  = 6        │  │          │               │
│  └─────────────────┘  │       len=3까지        cap=6까지
└───────────────────────┘       사용 가능        확장 가능
```

| 속성 | Array | Slice |
|------|-------|-------|
| 길이 | 컴파일 타임 고정 | 런타임 가변 |
| 타입 | `[5]int` (길이가 타입의 일부) | `[]int` |
| 전달 방식 | **복사** (값 타입) | **참조** (헤더 복사, 배열은 공유) |
| 사용 빈도 | 낮음 | **매우 높음** |

#### Slice 확장 전략 (append)

```
capacity가 부족할 때 append()의 확장 규칙 (Go 1.18+):

  현재 cap < 256:  새 cap = 현재 cap × 2     (2배 성장)
  현재 cap ≥ 256:  새 cap = 현재 cap × 1.25 + 192  (점진적 성장)
```

### Map

```go
// 선언과 초기화
m := map[string]int{
    "apple":  5,
    "banana": 3,
}

// 접근
v, ok := m["apple"]  // ok: 키 존재 여부
if !ok {
    fmt.Println("키 없음")
}

// 삭제
delete(m, "banana")

// 순회 (순서 보장 안 됨!)
for k, v := range m {
    fmt.Println(k, v)
}
```

> ⚠️ **주의**: map은 동시 접근 시 panic 발생. 동시성에서는 `sync.Map` 또는 mutex 사용.

### Struct

```go
type User struct {
    Name    string `json:"name"`     // 필드 태그
    Age     int    `json:"age"`
    Email   string `json:"email,omitempty"`
}

// 생성
u := User{Name: "Go", Age: 15}
u2 := User{"Go", 15, "go@dev"}  // 순서 기반 (비권장)

// 임베딩 (상속 대신 구성)
type Admin struct {
    User            // 임베딩 → User의 필드/메서드를 승격
    Permissions []string
}

a := Admin{User: User{Name: "Admin"}, Permissions: []string{"all"}}
fmt.Println(a.Name)  // User.Name에 직접 접근 가능 (승격)
```

### 🧒 12살 비유

> - **Array** = 고정칸 사물함 (5칸이면 5칸, 늘릴 수 없어)
> - **Slice** = 늘어나는 서랍 (꽉 차면 자동으로 더 큰 서랍으로 이사)
> - **Map** = 이름표 붙은 상자 (이름으로 찾기)
> - **Struct** = 레고 블록 (여러 부품을 조합해서 새로운 형태 만들기)

### 🔄 다른 언어와 비교

| 개념 | Go | Python | JavaScript | Kotlin |
|------|-----|--------|-----------|--------|
| 가변 배열 | slice (`[]T`) | list | Array | List/MutableList |
| 해시맵 | map (`map[K]V`) | dict | Object/Map | Map/MutableMap |
| 구조체/클래스 | struct (메서드 별도) | class | class/object | data class |
| 상속 | ❌ 없음 → 임베딩(구성) | class 상속 | prototype 상속 | class 상속 |

---

## 6️⃣ 인터페이스 기초

### Implicit Satisfaction (구조적 타이핑)

```go
// 인터페이스 정의
type Speaker interface {
    Speak() string
}

// 구현 — implements 키워드 없음!
type Dog struct{ Name string }
func (d Dog) Speak() string { return d.Name + ": 멍멍" }

type Cat struct{ Name string }
func (c Cat) Speak() string { return c.Name + ": 야옹" }

// 사용
func greet(s Speaker) {
    fmt.Println(s.Speak())
}

greet(Dog{"바둑이"})  // Dog가 Speak()을 가지므로 자동으로 Speaker
greet(Cat{"나비"})    // Cat도 마찬가지
```

**핵심**: Go의 인터페이스는 **구조적 타이핑(structural typing)** — 메서드 집합이 일치하면 자동으로 만족. `implements` 선언이 필요 없다.

### interface{} / any

```go
// Go 1.18 이전
func printAnything(v interface{}) { fmt.Println(v) }

// Go 1.18 이후 (any는 interface{}의 별칭)
func printAnything(v any) { fmt.Println(v) }
```

> ⚠️ Go Proverb #6: "interface{} says nothing" — 빈 인터페이스는 타입 정보를 잃는다. 제네릭(1.18+)으로 대체하자.

### Type Assertion과 Type Switch

```go
// Type assertion
var i interface{} = "hello"
s, ok := i.(string)  // s="hello", ok=true
n, ok := i.(int)     // n=0, ok=false

// Type switch
switch v := i.(type) {
case string:
    fmt.Println("문자열:", v)
case int:
    fmt.Println("정수:", v)
default:
    fmt.Println("모르는 타입")
}
```

### Stringer, error 인터페이스

```go
// fmt.Stringer: fmt.Println에서 자동 호출
type User struct{ Name string }
func (u User) String() string {
    return "User: " + u.Name
}

// error: Go의 에러 인터페이스
type error interface {
    Error() string
}
```

### 🔄 다른 언어와 비교

| 개념 | Go | Python | JavaScript | Kotlin |
|------|-----|--------|-----------|--------|
| 인터페이스 구현 | **암묵적** (구조적) | ABC/Protocol | 없음 (덕 타이핑) | **명시적** (`interface`) |
| 타입 검사 | type assertion/switch | `isinstance()` | `typeof`/`instanceof` | `is`/`as` |
| 빈 타입 | `any` (interface{}) | `Any` | `any` (TS) | `Any` |

---

## 7️⃣ 에러 처리 기초

### error 인터페이스

```go
// Go의 error는 단순한 인터페이스
type error interface {
    Error() string
}
```

### if err != nil 패턴

```go
f, err := os.Open("config.json")
if err != nil {
    return fmt.Errorf("설정 파일 열기 실패: %w", err)
}
defer f.Close()

data, err := io.ReadAll(f)
if err != nil {
    return fmt.Errorf("설정 파일 읽기 실패: %w", err)
}
```

Go 코드의 **상당 부분**이 `if err != nil`이다. 이것은 버그가 아니라 **설계 의도**이다:
- 에러 경로가 코드에 명시적으로 보인다
- 어디서 에러가 발생하는지 추적이 쉽다
- 에러를 무시하면 컴파일러가 경고한다 (`err` 미사용)

### errors.New, fmt.Errorf

```go
// 단순 에러 생성
var ErrNotFound = errors.New("not found")

// 문맥 추가 (wrapping)
err := fmt.Errorf("사용자 %d 조회 실패: %w", userID, ErrNotFound)
// → "사용자 42 조회 실패: not found"
```

### 🧒 12살 비유

> Python/JS에서 에러 처리는 "폭탄 돌리기"야 — 에러(예외)가 발생하면 누군가 잡을 때까지 위로 날아가. 아무도 안 잡으면 프로그램이 폭발해.
>
> Go에서 에러 처리는 "편지 전달"이야 — 함수가 결과와 함께 "문제가 있었어요"라는 편지(error)를 돌려줘. 받은 사람이 **반드시** 편지를 확인해야 해.

### 🔄 다른 언어와 비교

| 개념 | Go | Python | JavaScript | Kotlin |
|------|-----|--------|-----------|--------|
| 에러 표현 | `error` 값 | `Exception` 클래스 | `Error` 객체 | `Exception` 클래스 |
| 에러 전달 | 반환값 `(T, error)` | `raise` → `except` | `throw` → `catch` | `throw` → `catch` |
| 에러 무시 | `_, _ = f()` (명시적) | pass (묵시적 가능) | empty catch | empty catch |
| 문맥 추가 | `%w` wrapping | `raise ... from ...` | `new Error(msg, {cause})` | `cause` 파라미터 |

---

## 8️⃣ 포인터 기초

### & (address-of)와 * (dereference)

```go
x := 42
p := &x     // p는 x의 주소를 가리키는 포인터 (*int 타입)
fmt.Println(*p)  // 42 (역참조: 주소에서 값 꺼내기)

*p = 100    // 포인터를 통해 x의 값 변경
fmt.Println(x)   // 100
```

```
변수 x:        포인터 p:
┌────────┐    ┌────────────┐
│  100   │◄───│ 0xc0000b2008│
│ (값)   │    │ (x의 주소)  │
└────────┘    └────────────┘
  메모리           메모리
  0xc0000b2008     0xc0000b2010
```

### 포인터 산술 없음

```go
// C에서는 가능:
// int *p = &arr[0];
// p++;  // 다음 원소로 이동

// Go에서는 불가:
// p++  // 컴파일 에러!
```

Go는 **포인터 산술을 금지**한다. 이는 메모리 안전성을 위한 의도적 제한이다 (unsafe 패키지 제외).

### nil 포인터와 zero value

```go
var p *int       // nil (zero value for pointer)
// fmt.Println(*p)  // panic: nil pointer dereference!

// nil 체크 필수
if p != nil {
    fmt.Println(*p)
}
```

### new와 & 비교

```go
// new: 타입의 zero value를 할당하고 포인터 반환
p := new(int)     // *int, 값은 0

// &: 복합 리터럴의 주소
u := &User{Name: "Go"}  // *User

// 실무에서는 &가 훨씬 많이 사용됨
```

### 🧒 12살 비유

> 포인터는 "집 주소"야.
> - `x`는 집 안에 있는 물건 (값)
> - `&x`는 집 주소를 적은 메모 (포인터)
> - `*p`는 메모에 적힌 주소로 가서 물건을 꺼내기 (역참조)
> - Go에서는 주소를 계산해서 이웃집에 몰래 들어가는 것(포인터 산술)은 금지!

### 🔄 다른 언어와 비교

| 개념 | Go | Python | JavaScript | Kotlin |
|------|-----|--------|-----------|--------|
| 포인터 | 명시적 `*T`, `&x` | 없음 (모든 것이 참조) | 없음 (모든 것이 참조) | 없음 (JVM 참조) |
| 포인터 산술 | ❌ 금지 | N/A | N/A | N/A |
| Null/Nil | `nil` (포인터만) | `None` | `null`/`undefined` | `null` (Nullable) |
| 값 vs 참조 | 명시적 선택 | 항상 참조 | 원시=값, 객체=참조 | 원시=값, 객체=참조 |

---

## 📎 출처

1. [The Go Programming Language Specification](https://go.dev/ref/spec) — 공식 언어 스펙
2. [Effective Go](https://go.dev/doc/effective_go) — 관용적 Go 코딩 가이드
3. [A Tour of Go](https://go.dev/tour/) — 공식 튜토리얼
4. [Go Blog: Slices internals](https://go.dev/blog/slices-intro) — Slice 내부 구조
5. [Go Blog: Error handling](https://go.dev/blog/error-handling-and-go) — 에러 처리 철학

---

> 📌 **이전 문서**: [[02-go-architecture-and-runtime]] — Go의 아키텍처와 런타임
> 📌 **다음 문서**: [[04-go-advanced-syntax-and-patterns]] — Go 고급 문법과 패턴
