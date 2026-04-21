---
created: 2026-04-21
source: claude-code
tags: [python, study-guide, index, learning-path]
---

# 📖 Python 학습 가이드 — 시리즈 허브

> 💡 **한줄 요약**: Python 언어를 체계적으로 학습하기 위한 8개 문서 시리즈 + 기존 Deep Dive/면접 Q&A의 진입점. 철학부터 프로덕션 배포까지.
>
> 📅 **기준**: Python 3.14 (2025.10)

---

## 📚 전체 문서 목록

### 학습 시리즈 (번호순)

| # | 문서 | 핵심 내용 |
|---|------|----------|
| 01 | [[01-python-philosophy-and-differentiation]] | Zen of Python, 4개 언어 비교, Python 진화 타임라인 |
| 02 | [[02-python-architecture-and-runtime]] | CPython 파이프라인, GIL, 메모리, Free-threaded 3.14 |
| 03 | [[03-python-basic-syntax]] | 모듈, 타입힌트, OOP, 컴프리헨션, 에러 처리 |
| 04 | [[04-python-advanced-syntax-and-patterns]] | 데코레이터, 메타클래스, async, Protocol, 동시성 |
| 05 | [[05-python-developer-essentials-by-seniority]] | Junior→Staff 필수 지식 + 면접 빈출 |
| 06 | [[06-python-testing-patterns]] | pytest, mock, Hypothesis, testcontainers |
| 07 | [[07-python-project-structure-and-tooling]] | src layout, uv, Ruff, Docker, CI/CD |

### 기존 Deep Dive / 면접 문서

| 문서 | 위치 | 내용 |
|------|------|------|
| [[python-fastapi-sqlalchemy]] | interview-prep/ | Staff Engineer 면접 Q&A (28문항) |
| [[python-dict-key-ordering]] | python/ | Dict 내부 구조 (3.7+ 삽입 순서) |
| [[uv-uvx-python-package-manager]] | python/ | uv/uvx 패키지 관리자 |
| [[uv-lock-conflict-resolution-best-practice]] | python/ | uv.lock 충돌 해결 |
| [[python-go-java-performance-myth-deep-dive]] | performance/ | Python vs Go/Java 성능 비교 |
| [[coroutine-gmp-vthread]] | performance/ | 코루틴/goroutine/VThread 비교 |
| [[gc-g1-zgc]] | performance/ | Python RC + JVM GC + Go GC 비교 |

---

## 🎯 페르소나별 학습 경로

### 🟢 Python 입문자
```
01 철학 → 03 기본 문법 → 02 아키텍처(§1-2) → 04 고급(§1, §3)
→ 06 테스팅 → 07 프로젝트 구조 → 05 Junior/Mid 레벨
```

### 🔄 Go → Python 전환자
```
01 철학(§6 전환 가이드) → 03 기본 문법(각 섹션 Go 비교)
→ 02 아키텍처(§2 GIL vs GMP) → 04 고급(§1 데코레이터, §3 async)
→ 05 Mid 레벨
```

### 🎯 면접 준비자
```
05 필수 지식(해당 레벨) → 02 아키텍처(§2 GIL)
→ 04 고급(§2 메타클래스, §3 async) → [[python-fastapi-sqlalchemy]] (28문항)
```

---

## 📊 문서별 난이도

| 문서 | 난이도 | 예상 학습 시간 |
|------|--------|-------------|
| 01 철학 | ⭐⭐ | 25분 |
| 02 아키텍처 | ⭐⭐⭐⭐ | 45분 |
| 03 기본 문법 | ⭐⭐ | 40분 |
| 04 고급 문법 | ⭐⭐⭐⭐ | 50분 |
| 05 필수 지식 | ⭐⭐⭐ | 30분 |
| 06 테스팅 | ⭐⭐⭐ | 25분 |
| 07 프로젝트 구조 | ⭐⭐ | 20분 |
