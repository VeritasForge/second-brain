---
created: 2026-04-21
source: claude-code
tags: [golang, testing, table-driven, mock, fuzzing, benchmark, race-detector, testcontainers]
---

# 📖 Go 테스팅 패턴 — 프로덕션 코드를 지키는 테스트

> 💡 **한줄 요약**: Go의 테스팅은 표준 라이브러리 `testing`만으로 table-driven test, 벤치마크, fuzzing까지 지원하며, race detector와 testcontainers를 조합하면 동시성 안전성과 통합 테스트까지 커버할 수 있다.
>
> 📌 **핵심 키워드**: Table-Driven Test, -race, Fuzzing, mockgen, testcontainers, benchstat
> 📅 **기준**: Go 1.24 (2025.02)

---

## 1️⃣ Table-Driven Test — Go의 기본 테스트 패턴

### 기본 구조

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"양수끼리", 2, 3, 5},
        {"음수 포함", -1, 3, 2},
        {"0 더하기", 0, 5, 5},
        {"큰 수", 1<<31 - 1, 1, 1 << 31},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.expected {
                t.Errorf("Add(%d, %d) = %d, want %d", tt.a, tt.b, got, tt.expected)
            }
        })
    }
}
```

### 왜 Table-Driven인가

| 장점 | 설명 |
|------|------|
| **케이스 추가 용이** | 새 테스트 = 테이블에 한 줄 추가 |
| **패턴 통일** | 팀 전체가 같은 구조 사용 |
| **서브테스트** | `t.Run`으로 개별 실행/필터링 가능 |
| **에러 메시지 명확** | 어떤 케이스가 실패했는지 즉시 파악 |

```bash
# 특정 서브테스트만 실행
go test -run TestAdd/양수끼리
```

### 🔄 다른 언어와 비교

| 개념 | Go | Python | JavaScript | Kotlin |
|------|-----|--------|-----------|--------|
| 테이블 테스트 | 구조체 슬라이스 + t.Run | @pytest.mark.parametrize | test.each() (Jest) | @ParameterizedTest |
| 프레임워크 | `testing` (내장) | pytest (외부) | Jest/Vitest (외부) | JUnit (외부) |
| 실행 | `go test` | `pytest` | `npm test` | `gradle test` |

---

## 2️⃣ Mock 생성

### 인터페이스 기반 Mock (수동)

```go
// 프로덕션 코드
type UserRepository interface {
    GetByID(ctx context.Context, id int) (*User, error)
}

// 테스트용 Mock
type mockUserRepo struct {
    getByIDFn func(ctx context.Context, id int) (*User, error)
}

func (m *mockUserRepo) GetByID(ctx context.Context, id int) (*User, error) {
    return m.getByIDFn(ctx, id)
}

// 테스트
func TestGetUser(t *testing.T) {
    repo := &mockUserRepo{
        getByIDFn: func(_ context.Context, id int) (*User, error) {
            if id == 1 {
                return &User{Name: "Go"}, nil
            }
            return nil, ErrNotFound
        },
    }
    
    svc := NewUserService(repo)
    user, err := svc.GetUser(context.Background(), 1)
    // assert...
}
```

### mockgen (자동 생성)

```bash
# 인터페이스에서 Mock 자동 생성
mockgen -source=repository.go -destination=mock_repository_test.go -package=service

# 또는 go:generate 사용
//go:generate mockgen -source=repository.go -destination=mock_repository_test.go
```

### moq (경량 대안)

```bash
# moq: 구조체 기반 Mock 생성 (mockgen보다 단순)
moq -out mock_repository_test.go . UserRepository
```

| 도구 | 장점 | 단점 |
|------|------|------|
| **수동 Mock** | 의존성 없음, 완전한 제어 | 보일러플레이트 코드 |
| **mockgen** | 자동 생성, 기대값 검증 | 무거운 의존성 |
| **moq** | 경량, 구조체 기반 | 기대값 검증 없음 |

### 🧒 12살 비유

> Mock은 "연극 연습"과 같아. 진짜 데이터베이스(본 무대) 대신 "가짜 데이터베이스(리허설 파트너)"를 만들어서 코드가 제대로 동작하는지 연습하는 거야. 본 무대가 없어도 연습할 수 있지!

---

## 3️⃣ testcontainers — 진짜 인프라로 통합 테스트

```go
func TestPostgresIntegration(t *testing.T) {
    if testing.Short() {
        t.Skip("통합 테스트는 -short 모드에서 건너뜀")
    }

    ctx := context.Background()
    
    // 실제 PostgreSQL 컨테이너 시작
    container, err := postgres.Run(ctx,
        "postgres:16-alpine",
        postgres.WithDatabase("testdb"),
        postgres.WithUsername("test"),
        postgres.WithPassword("test"),
        testcontainers.WithWaitStrategy(
            wait.ForLog("database system is ready").
                WithOccurrence(2).
                WithStartupTimeout(5*time.Second)),
    )
    t.Cleanup(func() { container.Terminate(ctx) })
    
    connStr, _ := container.ConnectionString(ctx, "sslmode=disable")
    
    // 실제 DB로 테스트
    db, _ := sql.Open("postgres", connStr)
    repo := NewUserRepository(db)
    // ... 테스트 수행
}
```

**언제 testcontainers를 쓸까**:
- ✅ DB 쿼리 로직, 마이그레이션, 트랜잭션 테스트
- ✅ Redis, Kafka 등 외부 의존성 통합 테스트
- ❌ 단위 테스트 (인터페이스 Mock이 더 빠르고 가벼움)

---

## 4️⃣ Golden File 테스트

복잡한 출력(JSON, HTML, 로그 등)을 파일로 저장하고 비교하는 패턴:

```go
func TestRenderTemplate(t *testing.T) {
    got := renderTemplate(data)
    
    golden := filepath.Join("testdata", t.Name()+".golden")
    
    if *update {  // -update 플래그로 golden 파일 갱신
        os.WriteFile(golden, got, 0644)
    }
    
    want, _ := os.ReadFile(golden)
    if !bytes.Equal(got, want) {
        t.Errorf("출력이 golden 파일과 다릅니다:\n%s", diff(want, got))
    }
}
```

```bash
# golden 파일 갱신
go test -run TestRenderTemplate -update

# 일반 테스트 (비교만)
go test -run TestRenderTemplate
```

---

## 5️⃣ Fuzzing (Go 1.18+)

```go
func FuzzParseJSON(f *testing.F) {
    // Seed corpus: 정상적인 입력 예제
    f.Add([]byte(`{"name":"Go","version":1}`))
    f.Add([]byte(`{}`))
    f.Add([]byte(`[]`))

    // Fuzz 함수: 무작위 입력으로 테스트
    f.Fuzz(func(t *testing.T, data []byte) {
        var result map[string]any
        err := json.Unmarshal(data, &result)
        if err != nil {
            return  // 파싱 실패는 OK (에러 반환하면 됨)
        }
        
        // 파싱 성공했으면 다시 직렬화 가능해야 함
        _, err = json.Marshal(result)
        if err != nil {
            t.Errorf("Marshal 실패: %v", err)
        }
    })
}
```

```bash
# Fuzzing 실행 (30초)
go test -fuzz=FuzzParseJSON -fuzztime=30s

# 발견된 crash 재현
go test -run=FuzzParseJSON/corpus_entry
```

**Fuzzing이 찾아내는 것들**:
- 예상치 못한 입력에서의 panic
- 인코딩/디코딩 라운드트립 불일치
- 정수 오버플로, 무한 루프
- 메모리 할당 폭발

---

## 6️⃣ Race Detector

```bash
# 테스트 시 race 감지
go test -race ./...

# 빌드 시 race 감지 (프로덕션 비권장 — 2-10x 느림)
go build -race ./...
```

```go
// 이 코드는 -race에서 감지됨
var counter int

func TestRace(t *testing.T) {
    var wg sync.WaitGroup
    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            counter++  // DATA RACE: 동시 쓰기
        }()
    }
    wg.Wait()
}
```

> **원칙**: `go test -race`는 CI에서 **항상** 실행. race condition은 -race 없이는 발견이 매우 어렵다.

---

## 7️⃣ 벤치마크

### 기본 벤치마크

```go
func BenchmarkFibonacci(b *testing.B) {
    for b.Loop() {  // Go 1.24: b.Loop()이 기존 for i := 0; i < b.N; i++ 대체
        fibonacci(30)
    }
}
```

> 💡 **Go 1.24**: `b.Loop()`은 컴파일러 최적화 방지를 자동 처리하고, 이터레이션이 더 빠르다.

### benchstat으로 비교

```bash
# 변경 전
go test -bench=BenchmarkFib -count=10 > old.txt

# 변경 후
go test -bench=BenchmarkFib -count=10 > new.txt

# 통계적 비교
benchstat old.txt new.txt
```

```
name       old time/op  new time/op  delta
Fib-8      45.2µs ± 2%  32.1µs ± 1%  -28.98%  (p=0.000 n=10+10)
```

### 메모리 벤치마크

```go
func BenchmarkAlloc(b *testing.B) {
    b.ReportAllocs()  // 할당 횟수/크기 보고
    for b.Loop() {
        _ = make([]byte, 1024)
    }
}
// BenchmarkAlloc-8  100000  1024 B/op  1 allocs/op
```

### 🔄 다른 언어와 비교

| 개념 | Go | Python | JavaScript | Kotlin |
|------|-----|--------|-----------|--------|
| 벤치마크 | `testing.B` (내장) | timeit / pytest-benchmark | benchmark.js | JMH |
| 퍼지 테스트 | `testing.F` (내장) | hypothesis | fast-check | - |
| Race 감지 | `-race` (내장) | N/A (GIL) | N/A (단일 스레드) | 없음 (JVM 의존) |

---

## 8️⃣ 테스트 조직 패턴

### 파일 구조

```
mypackage/
├── user.go              ← 프로덕션 코드
├── user_test.go         ← 단위 테스트 (같은 패키지)
├── user_integration_test.go  ← 통합 테스트
└── testdata/            ← golden file, 테스트 fixture
    ├── TestRender.golden
    └── sample.json
```

### 테스트 헬퍼

```go
// t.Helper(): 에러 보고 시 호출 위치를 헬퍼가 아닌 호출자로 표시
func assertEqual(t *testing.T, got, want any) {
    t.Helper()
    if got != want {
        t.Errorf("got %v, want %v", got, want)
    }
}

// t.Cleanup(): 테스트 종료 시 자동 정리
func setupDB(t *testing.T) *sql.DB {
    db := connectTestDB()
    t.Cleanup(func() { db.Close() })
    return db
}
```

### Build Tag로 테스트 분리

```go
//go:build integration

package mypackage

func TestDatabaseIntegration(t *testing.T) {
    // 통합 테스트 코드
}
```

```bash
# 단위 테스트만
go test ./...

# 통합 테스트 포함
go test -tags=integration ./...
```

---

## 📎 출처

1. [Go Testing Package (go.dev 공식)](https://pkg.go.dev/testing) — testing 패키지 문서
2. [Go Blog: Table-Driven Tests](https://go.dev/wiki/TableDrivenTests) — 공식 가이드
3. [Go Blog: Fuzzing](https://go.dev/doc/security/fuzz/) — Fuzzing 공식 문서
4. [Go Blog: Data Race Detector](https://go.dev/doc/articles/race_detector) — Race detector 가이드
5. [testcontainers-go](https://golang.testcontainers.org/) — testcontainers 공식 문서

---

> 📌 **이전 문서**: [[05-go-developer-essentials-by-seniority]] — Go 개발자 필수 지식
> 📌 **다음 문서**: [[07-go-project-structure-and-tooling]] — Go 프로젝트 구조와 도구
