---
created: 2026-04-21
source: claude-code
tags: [python, project-structure, tooling, uv, ruff, docker, ci-cd, pyproject]
---

# 📖 Python 프로젝트 구조와 도구 — 현업 프로젝트 셋업

> 💡 **한줄 요약**: Python 프로젝트는 src 레이아웃 + pyproject.toml을 기본으로 하며, uv(패키지 관리) + Ruff(린트+포맷) + Docker multi-stage + CI 파이프라인을 조합하면 Go 수준의 일관된 개발 환경을 구축할 수 있다.
>
> 📌 **핵심 키워드**: src layout, pyproject.toml, uv, Ruff, mypy, multi-stage build
> 📅 **기준**: Python 3.14 (2025.10)

---

## 1️⃣ 프로젝트 레이아웃

### src 레이아웃 (권장)

```
myproject/
├── pyproject.toml          ← 프로젝트 메타데이터 + 의존성 + 도구 설정
├── uv.lock                 ← 의존성 락파일
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── main.py          ← FastAPI/Django 진입점
│       ├── api/
│       │   ├── __init__.py
│       │   └── routes.py
│       ├── services/
│       │   └── user.py
│       ├── repositories/
│       │   └── user.py
│       └── models/
│           └── user.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── migrations/
├── Makefile
├── Dockerfile
└── .github/workflows/ci.yml
```

### 🔄 Go와 비교

| 개념 | Python (src layout) | Go (cmd/internal/pkg) |
|------|-------------------|---------------------|
| 진입점 | `src/myapp/main.py` | `cmd/api/main.go` |
| 비공개 코드 | `_` 접두사 (관습) | `internal/` (컴파일러 강제) |
| 공개 라이브러리 | PyPI 배포 | `pkg/` |
| 의존성 | `pyproject.toml` + `uv.lock` | `go.mod` + `go.sum` |

---

## 2️⃣ 패키지 관리 — uv

> 📌 상세: [[uv-uvx-python-package-manager]], [[uv-lock-conflict-resolution-best-practice]]

```bash
# 프로젝트 초기화
uv init myproject
cd myproject

# 의존성 추가
uv add fastapi uvicorn
uv add --dev pytest ruff mypy

# 가상환경 + 의존성 동기화
uv sync

# 스크립트 실행
uv run python -m myapp.main
uv run pytest
```

### pyproject.toml 예제

```toml
[project]
name = "myapp"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "sqlalchemy>=2.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.6", "mypy>=1.11"]

[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
strict = true
python_version = "3.12"
```

---

## 3️⃣ 린팅과 포맷팅 — Ruff + mypy

### Ruff (flake8 + isort + Black 통합 대체)

```bash
# 린트
ruff check .

# 자동 수정
ruff check --fix .

# 포맷팅 (Black 대체)
ruff format .
```

**Ruff가 대체하는 도구들**: flake8, isort, black, pyflakes, pycodestyle, pydocstyle

| 도구 | 역할 | 속도 |
|------|------|------|
| **Ruff** (Rust) | 린트 + 포맷팅 + import 정렬 | ⚡ 10-100x 빠름 |
| **mypy** | 정적 타입 검사 | 보통 |
| **pyright** | 정적 타입 검사 (Microsoft) | 빠름 |

### 🔄 Go와 비교

| 역할 | Python | Go |
|------|--------|-----|
| 포맷팅 | Ruff format (선택적) | gofmt (필수) |
| 린팅 | Ruff check | golangci-lint |
| 타입 검사 | mypy/pyright (선택적) | 컴파일러 (필수) |

---

## 4️⃣ Docker 배포

```dockerfile
# ===== Stage 1: 빌드 =====
FROM python:3.14-slim AS builder

RUN pip install uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable

COPY src/ src/

# ===== Stage 2: 실행 =====
FROM python:3.14-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

CMD ["uvicorn", "myapp.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 이미지 크기 비교

| 베이스 이미지 | 크기 | Go 대응 |
|-------------|------|---------|
| python:3.14 | ~1GB | golang:1.24 (~850MB) — 빌드 전용 |
| python:3.14-slim | ~150MB | distroless (~12MB) |
| python:3.14-alpine | ~50MB | alpine (~15MB) |

> Python은 인터프리터가 필요하므로 Go의 scratch 이미지(~10MB)에 해당하는 것이 없다.

---

## 5️⃣ CI/CD 파이프라인

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --dev
      - run: uv run ruff check .
      - run: uv run ruff format --check .

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --dev
      - run: uv run mypy src/

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --dev
      - run: uv run pytest --cov=src -v
```

---

## 6️⃣ Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

```bash
pre-commit install
pre-commit run --all-files
```

---

## 📎 출처

1. [Python Packaging Guide](https://packaging.python.org/) — 공식 패키징 가이드
2. [Ruff Documentation](https://docs.astral.sh/ruff/) — Ruff 공식 문서
3. [uv Documentation](https://docs.astral.sh/uv/) — uv 공식 문서
4. [mypy Documentation](https://mypy.readthedocs.io/) — 타입 검사기

---

> 📌 **이전 문서**: [[06-python-testing-patterns]]
> 📌 **관련 문서**: [[uv-uvx-python-package-manager]], [[uv-lock-conflict-resolution-best-practice]]
