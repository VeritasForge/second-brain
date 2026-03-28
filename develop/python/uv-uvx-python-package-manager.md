---
created: 2026-03-28
source: claude-code
tags: [python, uv, uvx, package-manager, pip]
---

# uv와 uvx — Python 패키지 설치 도구 완전 정리

## uv란 무엇인가?

uv는 **Rust로 작성된 Python 패키지 관리 도구**로, pip를 대체하기 위해 만들어졌다.

### pip과 uv의 관계 — 흔한 오해

"uv가 내부적으로 pip를 사용한다"는 **잘못된 정보**다. uv는 pip를 감싸는 래퍼가 아니라, pip와 **같은 표준(PyPI, wheel, sdist)**을 따르는 **완전히 별도의 구현체**다.

| -       | pip                    | uv                                    |
| ------- | ---------------------- | ------------------------------------- |
| 언어    | Python으로 작성        | Rust로 작성                           |
| 내부 구현 | pip 자체가 설치 도구 | pip를 **사용하지 않음** (독립 구현)   |
| 호환성  | PyPI 표준              | PyPI 표준 **동일하게** 지원           |

### 비유: 택배 회사

- **pip** = 우체국 택배 (오래되고 검증됨)
- **uv** = 새로 생긴 초고속 택배 회사 (Rust로 만들어서 빠름)
- 둘 다 **같은 택배 규격(PyPI 패키지 표준)**을 따르므로, 어떤 택배사를 써도 물건(패키지)은 동일하게 도착함

---

## pip로만 설치하라는 문서, uv로 해도 되나?

**된다.** 이유는 간단하다:

```
pip install some-package
    ↓
1. PyPI (https://pypi.org) 에서 패키지를 찾는다
2. wheel 또는 sdist 파일을 다운로드한다
3. 의존성을 해결한다
4. 설치한다

uv add some-package
    ↓
1. PyPI (https://pypi.org) 에서 패키지를 찾는다  ← 같은 곳!
2. wheel 또는 sdist 파일을 다운로드한다          ← 같은 파일!
3. 의존성을 해결한다                              ← 같은 규칙!
4. 설치한다 + pyproject.toml에 기록한다           ← 여기만 다름
```

문서에 pip만 적혀 있는 이유는:

1. **pip이 사실상의 표준(de facto standard)** — Python 설치하면 기본으로 딸려옴
2. **가장 넓은 사용자층** — 모든 Python 개발자가 알고 있음
3. **uv는 아직 상대적으로 새로움** — 2024년 초에 나왔고, 모든 사용자가 쓰진 않음

---

## uv의 두 가지 인터페이스

### `uv` (기본 인터페이스) vs `uv pip` (호환 인터페이스)

| -              | `uv` (기본)                | `uv pip` (호환)                       |
| -------------- | -------------------------- | ------------------------------------- |
| 대상           | uv 방식에 익숙한 사용자    | pip에서 전환 중인 사용자              |
| 가상환경       | **자동** 관리              | **수동** 관리 (직접 activate 필요)    |
| 명령 예시      | `uv add requests`          | `uv pip install requests`            |
| lock 파일      | `uv.lock` 자동 생성        | 생성 안 함                            |
| 프로젝트 관리  | `pyproject.toml` 기반      | 관여 안 함                            |

### `uv pip` 명령 상세

`uv pip`은 **pip의 인터페이스를 흉내 낸 uv의 하위 명령**이다. 이름에 "pip"이 들어가지만 **내부적으로 pip를 호출하지 않는다**.

uv 공식 문서에서도 이렇게 명시한다:

> "uv does not rely on or invoke pip. The pip interface is named as such to highlight its dedicated purpose of providing low-level commands that match pip's interface."

#### 비유: 자동차

- `uv` = 전기차의 자동 운전 모드 (알아서 경로 설정, 주차까지 해줌)
- `uv pip` = 전기차인데 수동 기어 모드로 전환 (운전자가 직접 제어)
- 엔진은 여전히 전기 모터(uv/Rust)지만, 조작 방식만 기존 수동차(pip)처럼 제공

#### 주요 명령어

```bash
# 패키지 설치
uv pip install requests

# 패키지 제거
uv pip uninstall requests

# 설치된 패키지 목록
uv pip list

# requirements.txt로 설치
uv pip install -r requirements.txt

# requirements.txt 생성 (pip-compile 대체)
uv pip compile requirements.in -o requirements.txt
```

#### 주의점

- pip과 100% 동일하지 않음 — 특수한 사용법에서는 차이가 있을 수 있음
- 가상환경을 직접 관리해야 함 — `uv` 기본 명령과 달리 자동으로 venv를 만들지 않음
- 파워 유저용 — "아직 pip에서 전환할 준비가 안 된 프로젝트"를 위한 것

---

## `uv add`는 어디에 설치하나?

### 비유: 집과 창고

```
프로젝트 폴더 (집)
├── pyproject.toml    ← 가구 목록 (어떤 패키지가 필요한지)
├── uv.lock           ← 가구 정확한 모델번호 (버전 고정)
├── .venv/            ← 창고 (실제 패키지가 설치된 곳)
│   └── lib/python3.x/site-packages/
│       └── some_package/  ← 여기에 설치됨!
└── my_script.py      ← 이 스크립트에서 import해서 사용
```

`uv add`는 **현재 프로젝트 폴더의 `.venv`**에 설치한다. 전역이 아니라 **그 프로젝트 전용**.

---

## uvx란?

**`uvx` = `uv tool run`의 축약 명령**

Python CLI 도구를 **설치 없이 바로 실행**하는 명령이다.

### 비유: 일회용 vs 구매

```
pip install / uv add  = 공구를 사서 집에 보관  (영구 설치)
uv tool install       = 공구를 사서 공구함에 보관 (전역 설치)
uvx                   = 렌탈샵에서 빌려 쓰고 반납  (일회성 실행)
```

### 내부 동작

```bash
uvx ruff check .
```

이 한 줄이 내부적으로 하는 일:

```
1. 임시 가상환경 생성 (자동)
2. ruff 패키지 다운로드 + 설치 (임시로)
3. ruff check . 실행
4. 임시 환경 정리 (자동)
```

**내 프로젝트를 전혀 건드리지 않는다.**

### npx와 비교

| JavaScript                   | Python (uv)              | 하는 일              |
| ---------------------------- | ------------------------ | -------------------- |
| `npx create-react-app`       | `uvx cookiecutter ...`   | 설치 없이 바로 실행  |
| `npm install -g eslint`      | `uv tool install ruff`   | 전역 설치            |
| `npm install lodash`         | `uv add requests`        | 프로젝트에 추가      |

`uvx`는 Python 세계의 `npx`다.

### 사용 예시

```bash
# 코드 포매팅 한번만 돌려보고 싶을 때
uvx black my_file.py

# 프로젝트 템플릿 생성할 때
uvx cookiecutter gh:user/template

# 버전 특정해서 실행할 때
uvx --from 'ruff==0.4.0' ruff check .
```

### 언제 뭘 쓰나?

```
❌ 매일 반복해서 쓰는 도구 → uv tool install (매번 다운로드 낭비)
❌ 프로젝트 코드에서 import하는 라이브러리 → uv add (프로젝트 의존성)
✅ 한번만, 또는 가끔 쓰는 CLI 도구 → uvx
```

---

## 핵심 정리

1. **uv는 pip의 독립적 대체제**로, pip를 내부적으로 사용하지 않는다 (Rust로 독립 구현)
2. **pip 전용 패키지는 없다** — PyPI 표준을 따르는 패키지는 pip, uv, 어떤 도구로든 설치 가능
3. **`uv pip`은 pip 호환 인터페이스**로, 기존 pip 사용자를 위한 전환용 명령
4. **`uv add`는 프로젝트 로컬 `.venv`에 설치**하고 pyproject.toml에 기록
5. **`uvx`는 Python의 npx** — 임시 환경에서 CLI 도구를 설치 없이 바로 실행
