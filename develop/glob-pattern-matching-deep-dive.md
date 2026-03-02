---
created: 2026-03-02
source: claude-code
tags:
  - glob
  - pattern-matching
  - unix
  - shell
  - filesystem
---

# 📖 Glob — Concept Deep Dive

> 💡 **한줄 요약**: Glob은 유닉스 쉘에서 탄생한 **와일드카드 기반 파일 경로 패턴 매칭** 시스템으로, `*`, `?`, `[]` 등의 간결한 문법으로 파일명을 필터링한다.

---

## 1️⃣ 무엇인가? (What is it?)

**Glob**(Global의 줄임말)은 **와일드카드 문자를 사용하여 파일 경로를 패턴 매칭**하는 프로그래밍 개념이다. 쉘에서 `ls *.txt`처럼 입력하면, 쉘이 `*.txt`에 매칭되는 모든 파일명으로 확장(expand)한 뒤 명령어를 실행한다.

- **1971년** AT&T Unix Version 1에서 `/etc/glob`이라는 **독립 프로그램**으로 최초 등장
- **B 프로그래밍 언어**로 작성되었으며, 유닉스 메인라인에서 **고급 언어로 작성된 최초의 소프트웨어**
- Unix V7 (1979)의 Bourne Shell에 내장되면서 쉘의 핵심 기능으로 자리잡음
- 이후 C 라이브러리 함수 `glob()`과 `fnmatch()`로 표준화

> 📌 **핵심 키워드**: `wildcard`, `pattern matching`, `filename expansion`, `fnmatch`, `globbing`

---

## 2️⃣ 핵심 개념 (Core Concepts)

Glob 패턴은 소수의 **특수 문자(와일드카드)**와 **리터럴 문자**의 조합으로 구성된다.

```
┌─────────────────────────────────────────────────────────┐
│              🔤 Glob 패턴 구성 요소                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   리터럴 문자          와일드카드 문자                     │
│   ─────────           ──────────────                    │
│   "src/app"    +      *  ?  []  **  !                   │
│                       │  │  │   │   │                   │
│       ┌───────────────┘  │  │   │   │                   │
│       │   ┌──────────────┘  │   │   │                   │
│       │   │   ┌─────────────┘   │   │                   │
│       │   │   │   ┌─────────────┘   │                   │
│       │   │   │   │   ┌─────────────┘                   │
│       ▼   ▼   ▼   ▼   ▼                                │
│     any  one char  recursive  negate                    │
│     seq  char range  dir                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

| 와일드카드 | 이름            | 매칭 대상                          | 예시 패턴 → 매칭 결과                       |
| ---------- | --------------- | ---------------------------------- | ------------------------------------------- |
| `*`        | Asterisk        | 임의의 문자열 (0개 이상, `/` 제외) | `*.js` → `app.js`, `index.js`              |
| `?`        | Question Mark   | 정확히 **1개** 문자                | `file?.txt` → `file1.txt`, `fileA.txt`     |
| `[abc]`    | Bracket (목록)  | 괄호 안 문자 중 **1개**            | `[CB]at` → `Cat`, `Bat`                    |
| `[a-z]`    | Bracket (범위)  | 범위 내 문자 **1개**               | `file[0-9].log` → `file3.log`              |
| `[!abc]`   | Negated Bracket | 괄호 안 문자를 **제외**한 1개      | `[!0-9]*` → 숫자로 시작하지 않는 파일      |
| `**`       | Globstar        | **재귀적** 디렉토리 탐색 (0개 이상) | `src/**/*.ts` → 모든 하위의 `.ts` 파일     |

### 핵심 규칙

1. **경로 구분자 불투과**: `*`는 `/`를 넘지 못한다 → `src/*.js`는 `src/a/b.js`에 매칭 안 됨
2. **암묵적 앵커링**: Glob은 항상 **전체 문자열** 매칭 (regex와 다르게 부분 매칭 없음)
3. **닷파일 무시**: 기본적으로 `*`는 `.`으로 시작하는 숨김 파일을 매칭하지 않음

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

```
┌─────────────────────────────────────────────────────────────┐
│                 🔄 Glob 매칭 파이프라인                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  사용자 입력          쉘/런타임            파일 시스템          │
│  ──────────          ─────────            ─────────         │
│                                                             │
│  ls src/**/*.ts  ──►  ┌──────────────┐                      │
│                       │ 1. 패턴 파싱   │                      │
│                       │    (Parse)     │                      │
│                       └──────┬───────┘                      │
│                              │                              │
│                              ▼                              │
│                       ┌──────────────┐    ┌─────────────┐   │
│                       │ 2. 디렉토리   │───►│  readdir()  │   │
│                       │    탐색       │◄───│  (OS call)  │   │
│                       └──────┬───────┘    └─────────────┘   │
│                              │                              │
│                              ▼                              │
│                       ┌──────────────┐                      │
│                       │ 3. fnmatch() │                      │
│                       │  패턴 매칭    │                      │
│                       └──────┬───────┘                      │
│                              │                              │
│                              ▼                              │
│                       ┌──────────────┐                      │
│                       │ 4. 결과 정렬  │                      │
│                       │  & 확장      │                      │
│                       └──────┬───────┘                      │
│                              │                              │
│                              ▼                              │
│              ls src/app.ts src/lib/utils.ts                 │
│              (확장된 명령어 실행)                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (Step by Step)

1. **패턴 파싱**: 입력 문자열을 리터럴 세그먼트와 와일드카드로 분리. `src/**/*.ts` → `["src", "**", "*.ts"]`
2. **디렉토리 탐색**: 리터럴 prefix(`src/`)부터 시작하여 `readdir()` 시스템 콜로 파일 목록 조회
3. **패턴 매칭(fnmatch)**: 각 파일명/경로를 패턴과 비교. `**`이 있으면 재귀적으로 하위 디렉토리 탐색
4. **결과 정렬 & 확장**: 매칭된 파일 경로를 알파벳순 정렬 후, 원래 명령의 인자로 치환

### ⚡ 알고리즘 성능

[Russ Cox의 연구](https://research.swtch.com/glob)에 따르면, `*` 처리 방식에 따라 성능이 극적으로 달라진다:

| 구현 방식          | 시간 복잡도       | 설명                                |
| ------------------ | ----------------- | ----------------------------------- |
| 나이브 백트래킹    | **O(2^n)** 지수적 | 대부분의 쉘 구현 (위험)             |
| 탐욕적(greedy) 선형 | **O(n·m)**        | glibc, Go filepath.Match           |
| Regex 변환         | 엔진에 의존       | Python fnmatch (regex 기반)         |

> 패턴 `a*a*a*a*a*a*a*a*b`에 대해 100자 문자열 매칭: 나이브 → **7분 이상**, 선형 → **밀리초 단위**

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| #   | 유즈 케이스              | 예시                                    | 적합한 이유                          |
| --- | ------------------------ | --------------------------------------- | ------------------------------------ |
| 1   | **빌드 도구 파일 선택**  | `src/**/*.ts` (webpack, esbuild)        | 특정 확장자 파일을 재귀적으로 수집   |
| 2   | **.gitignore 패턴**      | `node_modules/`, `*.log`, `dist/**`     | 불필요한 파일 추적 제외              |
| 3   | **쉘 일괄 처리**         | `rm *.tmp`, `mv report_202?.pdf archive/` | 복수 파일 일괄 작업                |
| 4   | **CI/CD 트리거**         | `paths: ['src/**', '!src/**/*.test.ts']` | 변경 파일 기반 파이프라인 제어      |
| 5   | **린터/포매터 대상 지정** | `eslint 'src/**/*.{ts,tsx}'`            | 특정 파일만 검사                     |
| 6   | **에디터 파일 탐색**     | VS Code `files.exclude`, search glob    | 작업 영역 파일 필터링                |

### ✅ 베스트 프랙티스

1. **구체적 prefix 사용**: `**/*.js` 대신 `src/**/*.js` — 검색 범위를 좁혀 성능 향상
2. **`{}` 중괄호 확장 활용**: `*.{js,ts,jsx,tsx}` — 여러 확장자를 하나의 패턴으로
3. **negation 패턴 조합**: `!**/node_modules/**` — 불필요한 디렉토리 명시적 제외
4. **테스트 도구 활용**: [globster.xyz](https://globster.xyz) 같은 온라인 도구로 패턴 사전 검증

### 🏢 실제 적용 사례

- **Git (.gitignore)**: Glob 패턴으로 추적 제외 파일 관리 — 사실상 모든 프로젝트에서 사용
- **VS Code**: 파일 탐색, 검색, `files.exclude` 등 [전용 글로브 문법 문서](https://code.visualstudio.com/docs/editor/glob-patterns) 제공
- **GitHub Actions**: `paths`, `paths-ignore` 필터에서 글로브로 워크플로우 트리거 제어

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분      | 항목                 | 설명                                                     |
| --------- | -------------------- | -------------------------------------------------------- |
| ✅ 장점   | **직관적 문법**      | `*.txt`만 봐도 "모든 txt 파일"임을 즉시 이해             |
| ✅ 장점   | **학습 곡선 낮음**   | 와일드카드 3-4개만 알면 대부분의 상황 커버               |
| ✅ 장점   | **광범위한 지원**    | 쉘, Git, 에디터, 빌드 도구, CI/CD 등 어디서나 사용 가능 |
| ✅ 장점   | **파일 시스템 특화** | 경로 구분자 인식, 닷파일 처리 등 파일 탐색에 최적화      |
| ❌ 단점   | **표현력 제한**      | "숫자 3자리 + 문자" 같은 복잡한 패턴 표현 불가           |
| ❌ 단점   | **구현체별 차이**    | 쉘, 언어, 도구마다 미묘하게 다른 문법 (특히 `**`)       |
| ❌ 단점   | **POSIX 미표준 (`**`)** | Globstar는 공식 POSIX 표준에 포함되지 않음            |
| ❌ 단점   | **성능 위험**        | 대규모 디렉토리에서 `**` 사용 시 탐색 시간 폭증 가능    |

### ⚖️ Trade-off 분석

```
간결한 문법  ◄──────── Trade-off ────────►  제한된 표현력
파일 특화    ◄──────── Trade-off ────────►  범용성 부족
직관적 이해  ◄──────── Trade-off ────────►  복잡한 조건 불가
빠른 작성    ◄──────── Trade-off ────────►  구현체별 비일관성
```

---

## 6️⃣ 차이점 비교 (Comparison) — Glob vs Regex

### 📊 비교 매트릭스

| 비교 기준      | Glob                                   | Regex                                    |
| -------------- | -------------------------------------- | ---------------------------------------- |
| **핵심 목적**  | 파일 경로 매칭                         | 범용 텍스트 패턴 매칭                    |
| **`*`의 의미** | 임의의 문자열 (0+)                     | 앞 패턴의 0회 이상 반복                  |
| **`?`의 의미** | 임의의 1개 문자                        | 앞 패턴의 0 또는 1회                     |
| **`.`의 의미** | 리터럴 점 문자                         | 임의의 1개 문자                          |
| **앵커링**     | 항상 **전체 매칭** (암묵적)            | 부분 매칭 (`^`, `$`로 명시)              |
| **학습 곡선**  | 낮음 (5분)                             | 높음 (수 시간~수 일)                     |
| **표현력**     | 제한적                                 | 매우 강력 (캡처, 룩어라운드 등)          |
| **주요 사용처** | 쉘, .gitignore, 빌드 도구             | 텍스트 편집기, 로그 분석, 입력 검증      |
| **경로 인식**  | `/` 구분자 자동 처리                   | 경로 구분자에 대한 특별 처리 없음        |

### 🔍 핵심 차이 요약

```
Glob                             Regex
────────────────────    vs    ────────────────────
*.txt = 모든 txt 파일          .*\.txt = 모든 txt 포함 텍스트
?  = 아무 문자 1개              ?  = 앞 패턴 0-1회
전체 매칭 (anchored)            부분 매칭 (unanchored)
파일 시스템 전용                 범용 텍스트
간단하지만 제한적               복잡하지만 강력
```

### 🤔 언제 무엇을 선택?

- **Glob을 선택하세요** → 파일명/경로 필터링, .gitignore, 빌드 설정, 쉘 명령
- **Regex를 선택하세요** → 텍스트 내용 검색, 입력값 검증, 로그 파싱, 문자열 치환

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| #   | 실수                                     | 왜 문제인가                          | 올바른 접근                                    |
| --- | ---------------------------------------- | ------------------------------------ | ---------------------------------------------- |
| 1   | `*`로 숨김 파일 포함 기대                | `*`는 `.`으로 시작하는 파일 무시     | `.*`을 별도로 추가하거나 `dotglob` 옵션 설정   |
| 2   | `*`가 하위 디렉토리까지 매칭된다고 착각  | `*`는 `/`를 넘지 못함               | `**`를 사용하여 재귀 탐색                      |
| 3   | 대규모 트리에서 `**` 남용                | 탐색 시간이 기하급수적으로 증가      | 구체적 prefix로 범위 제한                      |
| 4   | OS별 대소문자 차이 무시                  | macOS/Windows: 대소문자 무시, Linux: 구분 | 크로스 플랫폼 시 명시적 규칙 설정         |
| 5   | `tests/*` vs `tests/**` 혼동            | `tests/*`는 1단계만, `tests/**`는 모든 하위 | 의도에 맞는 깊이 선택                  |

### 🚫 Anti-Patterns

1. **최상위 `**` 단독 사용**: `**/*.js` — 전체 파일 시스템 탐색으로 극심한 성능 저하. 항상 prefix 지정
2. **상충하는 include/exclude 패턴**: `*.js`를 exclude하고 `src/**/*.js`를 include → 도구에 따라 결과가 예측 불가. 순서와 우선순위를 문서 확인

### 🔒 보안/성능 고려사항

- **Glob DoS**: 악의적 패턴으로 백트래킹 폭발 가능 — 사용자 입력을 직접 glob 패턴으로 사용하지 말 것
- **심볼릭 링크 루프**: `**` 탐색 시 symlink가 순환 참조를 만들 수 있음 — `follow_symlinks` 옵션 주의
- **대규모 디렉토리**: `node_modules/**` 탐색은 수십만 파일을 포함할 수 있음 — 반드시 exclude 패턴 병행

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형          | 이름                                          | 링크/설명                                                                                            |
| ------------- | --------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 📖 공식 문서  | Python glob                                   | [docs.python.org/3/library/glob.html](https://docs.python.org/3/library/glob.html)                   |
| 📖 공식 문서  | VS Code Glob Patterns                         | [code.visualstudio.com/docs/editor/glob-patterns](https://code.visualstudio.com/docs/editor/glob-patterns) |
| 📖 공식 문서  | .NET File Globbing                            | [learn.microsoft.com](https://learn.microsoft.com/en-us/dotnet/core/extensions/file-globbing)        |
| 📘 심화 글    | Glob Matching Can Be Simple And Fast Too      | [research.swtch.com/glob](https://research.swtch.com/glob)                                           |
| 📘 가이드     | A Beginner's Guide: Glob Patterns             | [malikbrowne.com](https://www.malikbrowne.com/blog/a-beginners-guide-glob-patterns/)                 |
| 🛠️ 테스트 도구 | Globster — Glob 패턴 테스터                   | [globster.xyz](https://globster.xyz)                                                                 |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리  | 언어/플랫폼 | 용도                                     |
| ---------------- | ----------- | ---------------------------------------- |
| `minimatch`      | Node.js     | npm 생태계 표준 glob 매처 (npm, eslint 등) |
| `fast-glob`      | Node.js     | 고성능 glob 탐색 (빌드 도구에서 선호)    |
| `glob` (모듈)    | Python      | 표준 라이브러리 파일 패턴 매칭           |
| `pathlib.glob()` | Python 3    | 객체지향 경로 탐색                       |
| `filepath.Glob`  | Go          | 표준 라이브러리 (선형 시간 보장)         |
| `Dir.glob`       | Ruby        | 파일 패턴 매칭                           |
| `wcmatch`        | Python      | 확장 glob 기능 (negation, brace 등)      |

### 🔮 트렌드 & 전망

- **Globstar(`**`)의 표준화 움직임**: 아직 POSIX 미포함이지만, Bash 4+(2009), Zsh, Fish 등 대부분의 현대 쉘에서 지원하며 사실상 표준
- **빌드 도구 통합 심화**: Vite, esbuild, Turbopack 등 차세대 빌드 도구들이 glob 기반 파일 선택을 핵심 설정으로 활용
- **AI 코딩 도구**: Claude Code, Cursor 등 AI 도구에서 glob 패턴을 컨텍스트 파일 지정에 적극 활용

### 💬 커뮤니티 인사이트

- **"Glob은 regex를 배우기 전의 관문"** — 많은 개발자가 glob을 통해 패턴 매칭 개념을 처음 접한 뒤 regex로 확장
- `.gitignore`의 glob 문법이 **"대부분의 개발자가 glob을 처음 본격적으로 사용하는 계기"**라는 의견이 다수
- `**` 동작의 쉘별 미묘한 차이가 여전히 혼란을 유발 — 테스트 도구 사용이 강력히 권장됨

---

## 📎 Sources

1. [Glob (programming) - Wikipedia](https://en.wikipedia.org/wiki/Glob_(programming)) — 백과사전
2. [Glob Matching Can Be Simple And Fast Too - Russ Cox](https://research.swtch.com/glob) — 알고리즘 분석
3. [A Beginner's Guide: Glob Patterns - Malik Browne](https://www.malikbrowne.com/blog/a-beginners-guide-glob-patterns/) — 입문 가이드
4. [Glob vs. Regex - Apify Blog](https://blog.apify.com/glob-vs-regex/) — 비교 분석
5. [Globbing and Regex: So Similar, So Different - Linux Journal](https://www.linuxjournal.com/content/globbing-and-regex-so-similar-so-different) — 비교 분석
6. [Origin and Evolution of the Globstar - Mergify](https://mergify.com/blog/origin-and-evolution-of-the-globstar) — 역사
7. [VS Code Glob Patterns Reference](https://code.visualstudio.com/docs/editor/glob-patterns) — 공식 문서
8. [Python glob Documentation](https://docs.python.org/3/library/glob.html) — 공식 문서
9. [Greg's Wiki - glob](https://mywiki.wooledge.org/glob) — 커뮤니티 위키
10. [DeepSource - Tips for writing glob patterns](https://deepsource.com/blog/glob-file-patterns) — 실무 팁

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 7
> - 수집 출처 수: 10
> - 출처 유형: 공식 3, 블로그 4, 커뮤니티 2, 백과사전 1
