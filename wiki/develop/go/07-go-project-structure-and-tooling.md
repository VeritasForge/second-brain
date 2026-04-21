---
created: 2026-04-21
source: claude-code
tags: [golang, project-structure, tooling, golangci-lint, makefile, docker, ci-cd]
---

# 📖 Go 프로젝트 구조와 도구 — 현업 프로젝트 셋업

> 💡 **한줄 요약**: Go 프로젝트는 `cmd/internal/pkg` 3계층 레이아웃을 기본으로 하며, golangci-lint + Makefile + Docker multi-stage build + CI 파이프라인을 조합하면 일관되고 재현 가능한 개발-빌드-배포 ��경을 구축할 수 있���.
>
> 📌 **핵심 키워드**: cmd/internal/pkg, golangci-lint, Multi-stage Build, scratch, CI/CD
> 📅 **기준**: Go 1.24 (2025.02)

---

## 1️⃣ 표준 프로젝트 레이아웃

### 기본 구조

```
myproject/
├── cmd/                    ← 실행 가능한 바이너리 (진입점)
│   ├── api/
│   │   └── main.go         ← HTTP API 서버
│   ├── worker/
│   │   └── main.go         ← 백그라운드 워커
│   └── cli/
│       └── main.go         ← CLI 도구
│
├── internal/               ← 외부에서 import 불가 (컴파일러 강제)
│   ├── auth/               ← 인증 로직
│   ├── user/               ← 유저 도메인
│   │   ├── handler.go      ← HTTP 핸들러
│   │   ├── service.go      ← 비즈니스 로직
│   │   ├── repository.go   ← DB 접근
│   │   └── model.go        ← 도메인 모델
│   ├── config/             ← 설정 로딩
│   └── middleware/         ← HTTP 미들웨어
│
├── pkg/                    ← 외부에서도 import 가능 (공개 라이브러리)
│   └── httputil/           �� 재사용 가능한 HTTP 유틸
│
├── api/                    ← API 명세 (OpenAPI, protobuf)
│   └── proto/
│
├── migrations/             ← DB 마이그레이션
├── scripts/                ← ��드/배포 스크립트
│
├── go.mod
├── go.sum
├── Makefile
├── Dockerfile
├── .golangci.yml
└── README.md
```

### 각 디렉터리의 역할

| 디렉터리 | 역할 | 가시성 |
|---------|------|--------|
| `cmd/` | 각 바이너리의 `main.go` | — |
| `internal/` | 비즈니스 로직, 이 모듈 내에서만 접��� | **비공개** (컴파일러 강제) |
| `pkg/` | 다른 프로젝트에서도 import 가능한 라이브러리 | **공개** |
| `api/` | API 명세, protobuf 정의 | — |
| `migrations/` | SQL 마이그레이션 파일 | — |

### 🧒 12살 비유

> - `cmd/` = 건물의 **정문들** (API용 정문, 워커용 뒷문, CLI��� 측문)
> - `internal/` = 건물 **내부** (외부인 출입 금지 — 컴파일러가 경비원 역할)
> - `pkg/` = 건물 **1층 카페** (외부인도 이용 가능)

### ⚠️ 주의: pkg/ 사�� 기준

```
pkg/를 만들어야 할 때:
  ✅ 여러 프로젝트에서 실제로 공유되는 유틸리티
  ✅ 오픈소스 라이브��리로 공개할 코드

pkg/를 만들지 말아야 할 때:
  ❌ "나중에 공유할 수도 있으니까" (YAGNI)
  ❌ internal에 넣기 싫어�� (그러면 그냥 internal에 두��)
```

### 🔄 다른 언어와 비교

| 개념 | Go | Python | JavaScript | Kotlin/Java |
|------|-----|--------|-----------|-----------|
| 프로젝트 구조 | cmd/internal/pkg | src/tests | src/dist | src/main/java |
| 접근 제한 | `internal` (컴파일러) | `_` 접두사 (관습) | 없음 | `internal` (Kotlin) |
| 진입점 | `cmd/*/main.go` | `__main__.py` | `index.js` | `Application.kt` |

---

## 2️⃣ golangci-lint — 통합 린터

### 설치 및 기본 사용

```bash
# 설치
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# 실행
golangci-lint run ./...
```

### .golangci.yml 설정 예제

```yaml
run:
  timeout: 5m
  go: "1.24"

linters:
  enable:
    - errcheck        # 에러 반환값 미확인 검출
    - govet           # go vet 통합
    - staticcheck     # 정적 분석 (SA, ST 규칙)
    - unused          # 미사용 코�� 검출
    - gosimple        # 코드 단순화 제안
    - ineffassign     # 무효한 할당 검출
    - gocritic        # 추가 정적 분석
    - revive          # golint 후속 (스타일 검사)
    - misspell        # 오타 검출
    - gofumpt         # gofmt 엄격 버전
    - gosec           # 보안 취약점 검출
    - prealloc        # slice 사전 할당 제안

linters-settings:
  errcheck:
    check-type-assertions: true
  gocritic:
    enabled-tags:
      - diagnostic
      - style
      - performance
  revive:
    rules:
      - name: unexported-return
        disabled: true

issues:
  exclude-rules:
    - path: _test\.go
      linters:
        - errcheck  # 테스트에서는 에러 체크 완화
```

### 주��� 린터 설명

| 린터 | 카테고리 | 검�� 대상 |
|------|---------|----------|
| `errcheck` | 필수 | 에러 무시 (`_ = f()` 명시 강제) |
| `staticcheck` | 필수 | 사용되지 않는 코드, 잘못된 패턴 |
| `govet` | 필수 | printf 포맷 불일치, 구조체 정렬 |
| `gosec` | 보안 | SQL 인젝션, 하드코딩된 비밀 |
| `revive` | 스타일 | 명명 규칙, 코드 스타일 |
| `prealloc` | 성능 | slice 사전 할당 누락 |

---

## 3️⃣ Makefile — 빌드 자동화

```makefile
# 변수
APP_NAME := myapp
VERSION := $(shell git describe --tags --always --dirty)
BUILD_FLAGS := -ldflags="-s -w -X main.version=$(VERSION)"

.PHONY: all build test lint clean docker

## 기본 타겟
all: lint test build

## 빌드
build:
	CGO_ENABLED=0 go build $(BUILD_FLAGS) -o bin/$(APP_NAME) ./cmd/api

## 테스트
test:
	go test -race -coverprofile=coverage.out ./...
	go tool cover -func=coverage.out

## 통합 테스트
test-integration:
	go test -race -tags=integration ./...

## 린트
lint:
	golangci-lint run ./...

## 코드 생성
generate:
	go generate ./...

## 정리
clean:
	rm -rf bin/ coverage.out

## Docker 빌드
docker:
	docker build -t $(APP_NAME):$(VERSION) .

## 개발 서버 (hot reload)
dev:
	air  # cosmtrek/air 또는 golang.org/x/tools/cmd/present

## 도움말
help:
	@grep -E '^##' Makefile | sed 's/^## //'
```

---

## 4️⃣ Docker Multi-stage Build

```dockerfile
# ===== Stage 1: 빌드 =====
FROM golang:1.24-alpine AS builder

# 빌드 의존성
RUN apk add --no-cache git ca-certificates

WORKDIR /app

# 의존성 캐싱 (go.mod/sum이 변경되지 않으면 캐시 사용)
COPY go.mod go.sum ./
RUN go mod download

# 소스 복사 및 빌드
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -ldflags="-s -w" -o /app/server ./cmd/api

# ===== Stage 2: 실행 =====
FROM scratch
# 또는 FROM gcr.io/distroless/static:nonroot

# CA 인증서 (HTTPS 호출에 필요)
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
# 바이너리
COPY --from=builder /app/server /server
# 마이그레이션 (필요시)
COPY --from=builder /app/migrations /migrations

EXPOSE 8080
ENTRYPOINT ["/server"]
```

### 이미지 크기 비교

```
┌───────────────────────┬───��──────┐
│ 베이스 이미지          │ 최종 크기 │
├───────────────────────┼──────────┤
│ golang:1.24           │ ~850 MB  │  ← 빌드 전용, 배포 금지
│ golang:1.24-alpine    │ ~260 MB  │  ← 빌드 전용
│ alpine                │ ~15 MB   │  ← CGo 필요시
│ distroless/static     │ ~12 MB   │  ← Pure Go 권장
│ scratch               │ ~10 MB   │  ← 최소 (CA 인증서 직접 포함)
└───────────────────────┴──────────┘
```

---

## 5️⃣ CI/CD 파이프라인 템플릿

### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.24"
      - uses: golangci/golangci-lint-action@v6
        with:
          version: latest

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.24"
      - run: go test -race -coverprofile=coverage.out ./...
      - run: go tool cover -func=coverage.out

  build:
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.24"
      - run: CGO_ENABLED=0 go build -ldflags="-s -w" -o bin/app ./cmd/api
      - uses: actions/upload-artifact@v4
        with:
          name: binary
          path: bin/app
```

### CI 파이프라인 흐름

```
  Push/PR
    │
    ├── lint (golangci-lint) ──── 코드 품질 검사
    │
    ├── test (go test -race) ──── 단위 테스트 + race 감지
    │
    └── build ─────────────────── 바이너리 빌드
         │
         ├── (main만) docker build → push
         │
         └── (tag만) goreleaser → GitHub Release
```

---

## 6️⃣ 유용한 도구 모��

| 도구 | 용도 | 설치 |
|------|------|------|
| `golangci-lint` | 통합 린터 | `go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest` |
| `air` | Hot reload (개발 서버) | `go install github.com/air-verse/air@latest` |
| `goreleaser` | 크로스 컴파일 릴리스 | `go install github.com/goreleaser/goreleaser@latest` |
| `goimports` | import 정리 + 포맷팅 | `go install golang.org/x/tools/cmd/goimports@latest` |
| `gopls` | Language Server (IDE) | `go install golang.org/x/tools/gopls@latest` |
| `dlv` | 디버거 (Delve) | `go install github.com/go-delve/delve/cmd/dlv@latest` |
| `govulncheck` | 의존성 취약점 검사 | `go install golang.org/x/vuln/cmd/govulncheck@latest` |
| `benchstat` | 벤치마크 통계 비교 | `go install golang.org/x/perf/cmd/benchstat@latest` |

### go.mod tool 지시어 (Go 1.24)

```
// go.mod
module myproject

go 1.24

tool (
    github.com/golangci/golangci-lint/cmd/golangci-lint
    github.com/air-verse/air
    golang.org/x/tools/cmd/stringer
)
```

`go.mod`의 `tool` 지시어로 팀 전체가 **같은 버전의 도구**를 사용할 수 있다. 기존의 `tools.go` 해킹 불필요.

---

## 📎 출처

1. [Standard Go Project Layout](https://github.com/golang-standards/project-layout) — 커뮤니티 레이아웃 가이드
2. [golangci-lint 공식 문서](https://golangci-lint.run/) — 린터 설정 가이드
3. [Go Blog: Multi-module Workspaces](https://go.dev/blog/get-familiar-with-workspaces) — 워크스페이스 가이드
4. [Docker Best Practices for Go](https://docs.docker.com/language/golang/) — Docker 공식 Go 가이드
5. [Go 1.24 Release Notes: tool directive](https://go.dev/doc/go1.24) — tool 지시어

---

> 📌 **이전 문서**: [[06-go-testing-patterns]] — Go 테스팅 패턴
> 📌 **관련 문서**: [[02-go-architecture-and-runtime]] §5 — 바이너리 구조와 배포
