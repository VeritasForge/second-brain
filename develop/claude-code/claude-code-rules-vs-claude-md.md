---
created: 2026-02-20
source: claude-code
tags:
  - claude-code
  - rules
  - claude-md
  - configuration
  - developer-tools
---

# Claude Code: CLAUDE.md vs `.claude/rules/` 차이점

## 핵심 차이

| 기준           | CLAUDE.md                       | `.claude/rules/*.md`                       |
| -------------- | ------------------------------- | ------------------------------------------ |
| **적용 범위**  | 항상 전체 로드                  | 전역 또는 **경로별 조건부 로드**           |
| **구조**       | 단일 파일                       | 다중 파일, 디렉토리 구조                   |
| **최대 장점**  | 간단, 한 곳에서 관리            | **glob pattern으로 특정 파일에만 적용**    |
| **우선순위**   | High                            | High (동일)                                |
| **팀 관리**    | 하나의 파일에 변경 충돌         | 파일별 독립 관리, git diff 용이            |

---

## 메모리 계층 구조

| 메모리 타입        | 위치                                                        | 용도                     | 공유 범위                 |
| ------------------ | ----------------------------------------------------------- | ------------------------ | ------------------------- |
| **Managed policy** | `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS) | 조직 전체 정책           | 조직 내 모든 사용자       |
| **Project memory** | `./CLAUDE.md` 또는 `./.claude/CLAUDE.md`                    | 팀 공유 프로젝트 지침    | 팀 (소스 컨트롤)          |
| **Project rules**  | `./.claude/rules/*.md`                                      | 모듈형, 토픽별 지침      | 팀 (소스 컨트롤)          |
| **User memory**    | `~/.claude/CLAUDE.md`                                       | 개인 전역 설정           | 본인만 (모든 프로젝트)    |
| **Project local**  | `./CLAUDE.local.md`                                         | 개인 프로젝트별 설정     | 본인만 (현재 프로젝트)    |
| **User rules**     | `~/.claude/rules/*.md`                                      | 개인 전역 규칙           | 본인만 (모든 프로젝트)    |
| **Auto memory**    | `~/.claude/projects/<project>/memory/`                      | Claude 자동 학습 노트    | 본인만 (프로젝트별)       |

**핵심 원칙**: 더 구체적인 지침이 더 넓은 지침보다 우선합니다.

---

## rules의 킬러 기능: 경로별 조건부 로딩

```yaml
---
globs: src/api/**/*.ts, src/routes/**/*.ts
---

# API Development Rules
- 모든 엔드포인트에 입력 검증 필수
- 일관된 에러 응답 포맷 사용
```

이 규칙은 **`src/api/` 하위 `.ts` 파일을 편집할 때만** 활성화됩니다. React 컴포넌트를 편집할 때는 로드되지 않아 컨텍스트 낭비를 방지합니다.

### 지원하는 Glob 패턴

| 패턴                         | 매칭 대상                       |
| ---------------------------- | ------------------------------- |
| `**/*.ts`                    | 모든 디렉토리의 TypeScript 파일 |
| `src/**/*`                   | `src/` 하위 모든 파일           |
| `*.md`                       | 프로젝트 루트의 Markdown 파일   |
| `src/components/*.tsx`       | 특정 디렉토리의 React 컴포넌트  |
| `src/**/*.{ts,tsx}`          | .ts와 .tsx 모두 매칭            |
| `{src,lib}/**/*.ts`          | src와 lib 디렉토리 모두 매칭    |

---

## 언제 무엇을 사용?

### 의사결정 프레임워크

```
이 지침이 항상 모든 파일에 적용되는가?
    ├── Yes → CLAUDE.md
    └── No
         └── 특정 파일/디렉토리에만 적용?
              ├── Yes → .claude/rules/ (with globs)
              └── No → .claude/rules/ (토픽별 분리, globs 없이)
```

### CLAUDE.md에 넣어야 할 것

| 포함해야 할 내용                         | 예시                                   |
| ---------------------------------------- | -------------------------------------- |
| Claude가 추측할 수 없는 빌드/테스트 명령 | `npm run test:unit`, `pnpm lint`       |
| 기본값과 다른 코드 스타일 규칙           | "Use 2-space indentation"              |
| 테스트 러너 및 선호 테스트 방식          | "Use vitest, not jest"                 |
| 아키텍처 결정 사항                       | "We use hexagonal architecture"        |
| 흔한 실수/비직관적 동작                  | "Don't use lodash - we have custom utils" |

### rules로 분리해야 할 것

| 포함해야 할 내용                       | 예시                                            |
| -------------------------------------- | ----------------------------------------------- |
| 특정 파일 타입에만 적용되는 규칙       | React 컴포넌트 패턴, API 엔드포인트 규칙        |
| 도메인별 지식                          | security.md, performance.md, accessibility.md   |
| 팀별 독립 관리가 필요한 규칙           | frontend/, backend/, infra/ 디렉토리로 분리     |
| 조직 공통 표준 (symlink 활용)          | 회사 보안 정책, 코딩 표준                       |

---

## 디렉토리 구조 예시

```
your-project/
├── .claude/
│   ├── CLAUDE.md               # 글로벌 규칙만
│   └── rules/
│       ├── general.md          # 모든 파일에 적용
│       ├── code-style.md       # 코드 스타일
│       ├── testing.md          # 테스트 규칙 (globs: **/*.test.ts)
│       ├── security.md         # 보안 규칙
│       ├── frontend/
│       │   ├── react.md        # globs: src/components/**/*.tsx
│       │   └── styles.md       # globs: **/*.css
│       └── backend/
│           ├── api.md          # globs: src/api/**/*.ts
│           └── database.md     # globs: src/db/**/*.ts
```

---

## 실제 Rules 파일 작성 예시

### 보안 민감 코드 규칙

```yaml
---
globs: src/auth/**/*.*, src/payments/**/*.*
---

# Security-Critical Code Rules
- Never log sensitive data (passwords, tokens, card numbers)
- Validate all inputs at function boundaries
- Use parameterized queries exclusively
```

### 테스트 작성 표준

```yaml
---
globs: **/*.test.ts, **/*.spec.ts
---

# Test Writing Standards
- Descriptive test names: "should [action] when [condition]"
- One assertion per test when possible
- Mock external dependencies, never call real APIs
```

### DB Migration 안전 규칙

```yaml
---
globs: prisma/migrations/**/*
---

# Migration Safety Rules
- Always include rollback instructions
- Never delete columns in same migration as removing code
```

---

## 주의사항 (2026년 2월 현재)

### paths frontmatter 버그

`paths:` YAML 배열 형식에 버그가 있습니다. **`globs:` + 콤마 구분 + 따옴표 없는 패턴**이 가장 안정적입니다:

```yaml
# 권장
---
globs: **/*.ts, src/**/*.tsx
---

# 비권장 (버그 가능성)
---
paths:
  - "**/*.ts"
---
```

### User-level rules 제한

- `~/.claude/rules/`에 넣은 규칙의 `paths:` frontmatter가 무시됩니다
- 개인 전역 규칙은 조건부 적용이 불가능한 상태

### CLAUDE.md가 너무 길어졌을 때의 징후

공식 문서에서 명시적으로 경고하는 내용:

> "If Claude keeps doing something you don't want despite having a rule against it, the file is probably too long and the rule is getting lost."

이 경우 rules로 분리하는 것이 해결책입니다.

---

## 점진적 설정 전략 (공식 권장)

1. **시작**: `CLAUDE.md`만으로 시작 (`/init` 명령어 활용)
2. **성장**: CLAUDE.md가 길어지면 도메인별 `.claude/rules/` 파일로 분리
3. **성숙**: 반복 워크플로우는 skills로, 필수 실행은 hooks로 분리
4. **지속**: 주기적으로 리뷰하고, Claude가 이미 잘하는 것은 삭제

---

## Sources

1. [Manage Claude's memory - Claude Code Docs](https://code.claude.com/docs/en/memory) — 공식 문서
2. [Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices) — 공식 문서
3. [Claude Code Rules Directory Guide](https://claudefa.st/blog/guide/mechanics/rules-directory) — 커뮤니티 가이드
4. [Claude Code: Rules vs Skills vs Agents Explained](https://jonimms.com/claude-code-rules-skills-agents-explained/) — 커뮤니티 블로그
5. [Writing a good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) — 커뮤니티 가이드
