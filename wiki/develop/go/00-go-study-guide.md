---
created: 2026-04-21
source: claude-code
tags: [golang, study-guide, index, learning-path]
---

# 📖 Go 학습 가이드 — 시리즈 허브

> 💡 **한줄 요약**: Go 언어를 체계적으로 학습하기 위한 8개 문서 시리즈 + 기존 Deep Dive 문서의 진입점. 철학부터 프로덕션 배포까지, 레벨에 맞는 학습 경로를 안내한다.
>
> 📅 **기준**: Go 1.24 (2025.02)

---

## 📚 전체 문서 목록

### 학습 시리즈 (번호순)

| # | 문서 | 핵심 내용 |
|---|------|----------|
| 01 | [[01-go-philosophy-and-differentiation]] | Go 철학, Go Proverbs, 5개 언어 비교 (Python/JS/Kotlin/Rust) |
| 02 | [[02-go-architecture-and-runtime]] | 컴파일 파이프라인, GMP/GC/Memory/NetPoller 런타임, 바이너리 |
| 03 | [[03-go-basic-syntax]] | 패키지, 타입, 제어흐름, 함수, Slice/Map/Struct, 인터페이스, 에러, 포인터 |
| 04 | [[04-go-advanced-syntax-and-patterns]] | 제네릭, Context, 동시성 패턴, sync, Reflection, 에러 고급 |
| 05 | [[05-go-developer-essentials-by-seniority]] | Junior→Staff 필수 지식 + 면접 빈출 마커 |
| 06 | [[06-go-testing-patterns]] | Table-driven test, Mock, Fuzzing, Race detector, 벤치마크 |
| 07 | [[07-go-project-structure-and-tooling]] | cmd/internal/pkg, golangci-lint, Docker, CI/CD |

### 기존 Deep Dive 문서

| 문서 | 핵심 내용 | 깊이 |
|------|----------|------|
| [[go-channel-deep-dive]] | hchan 구조, sudog, 원형 버퍼, sendDirect | 런타임 소스 수준 |
| [[goroutine-gmp-scheduler-deep-dive]] | G-M-P 관계, work-stealing, 선점, 스택 관리 | 런타임 소스 수준 |
| [[monkey-patching-and-uber-fx-deep-dive]] | 정적 언어 몽키 패칭, IoC/DI, uber-go/fx | 프레임워크 수준 |

### 관련 문서

| 문서 | 위치 | 내용 |
|------|------|------|
| [[golang]] | interview-prep/ | Staff Engineer 면접 Q&A (26문항) |
| [[kotlin-vs-go]] | develop/ | Kotlin vs Go 언어 선택 가이드 |
| [[python-go-java-performance-myth-deep-dive]] | develop/performance/ | Python/Go/Java 성능 비교 연구 |

---

## 🗺️ 읽기 순서

```
                    ┌──────────────────────────────┐
                    │  여기 (00 허브 페이지)        │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │  01 Go 철학 & 차별점          │
                    │  "왜 Go인가"                  │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │  02 아키텍처 & 런타임         │
                    │  "어떻게 동작하는가"          │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │  03 기본 문법                  │
                    │  "어떻게 쓰는가"              │
                    └──────────────┬───────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                     │
   ┌──────────▼─────────┐  ┌──────▼──────────┐         │
   │  기존 Deep Dive:   │  │  04 고급 문법    │         │
   │  • Channel 내부    │◄─│  & 패턴          │         │
   │  • GMP 스케줄러    │  │  "프로덕션 수준" │         │
   │  • Monkey Patching │  └──────┬──────────┘         │
   └────────────────────┘         │                     │
                    ┌─────────────▼─────────────┐       │
                    │  05 필수 지식 by 레벨      │       │
                    │  "면접 + 커리어 성장"      │       │
                    └─────────────┬─────────────┘       │
                                  │                      │
              ┌───────────────────┼──────────────────────┘
              │                   │
   ┌──────────▼─────────┐ ┌──────▼──────────┐
   │  06 테스팅 패턴    │ │  07 프로젝트    │
   │  "코드를 지키기"   │ │  구조 & 도구    │
   │                     │ │  "현업 셋업"    │
   └─────────────────────┘ └────────────────┘
```

---

## 🎯 페르소나별 학습 경로

### 🟢 Go 입문자

> Go를 처음 배우는 개발자

```
01 철학 → 03 기본 문법 → 02 아키텍처(§1~3) → 04 고급(§1~3)
  → 07 프로젝트 구조 → 06 테스팅 → 05 Junior/Mid 레벨
```

### 🔄 Python → Go 전환자

> Python 경험이 있고 Go로 전환하는 개발자

```
01 철학(§6 마인드셋 전환 중점) → 03 기본 문법(각 섹션 Python 비교)
  → 02 아키텍처(§6 CPython 비교) → 04 고급(§1~3 동시성 패턴)
  → 05 Mid 레벨 → 07 프로젝트 구조
```

### 🔄 JS/Kotlin → Go 전환자

> JavaScript 또는 Kotlin 경험이 있고 Go로 전환하는 개발자

```
01 철학(§4 언어 비교, §6 마인드셋 전환) → 03 기본 문법(§6 인터페이스, §8 포인터)
  → 04 고급(§2 Context = coroutine 대응, §3 동시성)
  → 02 아키텍처(§2 런타임 비교) → 05 Mid 레벨
```

### 🎯 면접 준비자

> Go 면접을 앞둔 개발자 (목표 레벨별)

```
Junior/Mid:
  05 필수 지식(§1-2) → 03 기본 문법 → 04 고급(§2-3)

Senior:
  05 필수 지식(§3) → Deep Dive (Channel, GMP) → 02 아키텍처(§3-4 메모리/GC)
  → [[golang]] 면접 Q&A (26문항)

Staff:
  05 필수 지식(§4) → 01 철학(§4-5 언어 선택) → [[golang]] 면접 Q&A 전체
  → [[kotlin-vs-go]] → [[python-go-java-performance-myth-deep-dive]]
```

---

## 📊 문서별 난이도와 시간

| 문서 | 난이도 | 예상 학습 시간 |
|------|--------|-------------|
| 01 철학 | ⭐⭐ | 30분 |
| 02 아키텍처 | ⭐⭐⭐⭐ | 1시간 |
| 03 기본 문법 | ⭐⭐ | 45분 |
| 04 고급 문법 | ⭐⭐⭐⭐ | 1시간 |
| 05 필수 지식 | ⭐⭐⭐ | 45분 |
| 06 테스팅 | ⭐⭐⭐ | 30분 |
| 07 프로젝트 구조 | ⭐⭐ | 20분 |
| Deep Dive (3개) | ⭐⭐⭐⭐⭐ | 각 1시간+ |

---

## 📌 향후 추가 예정

- `08-go-standard-library-essentials.md` — 표준 라이브러리 필수 가이드
- `09-go-common-idioms-and-patterns.md` — Go 관용구 모음
- `10-go-web-service-patterns.md` — 웹 서비스 패턴
- `11-go-containerization-and-deployment.md` — 컨테이너화와 배포
- `12-go-grpc-and-protobuf.md` — gRPC와 Protocol Buffers
