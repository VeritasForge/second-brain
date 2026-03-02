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

## 메모리 시스템 관점에서의 비교

> 심화 Q&A: [[claude-code-memory-system-qa]], Deep Dive: [[claude-code-memory-system-deep-dive]]

### Memory Loading Pipeline에서의 차이

```
세션 시작 시 로드 순서:

①  Managed Policy CLAUDE.md     ─ 항상 전체 로드 (제외 불가 🔒)
②  ~/.claude/CLAUDE.md          ─ 항상 전체 로드
    └─ ~/.claude/rules/*.md     ─ 항상 전체 로드 (globs 무시됨)
③  ./CLAUDE.md                  ─ 항상 전체 로드
    └─ ./.claude/rules/*.md     ─ 무조건 또는 조건부 로드
④  ./CLAUDE.local.md            ─ 항상 전체 로드
⑤  @import 해석                 ─ 최대 5단계 깊이
⑥  MEMORY.md (200줄만)          ─ 항상 자동 주입

세션 중:
⑦  하위 디렉토리 CLAUDE.md      ─ 해당 파일 작업 시 로드
⑧  토픽 파일                    ─ Claude가 Read 도구로 직접 참조
```

### 컨텍스트 윈도우 비용 비교

| 구성 요소 | 로드 방식 | 비용 특성 |
|-----------|-----------|-----------|
| CLAUDE.md | 항상 전체 | 고정 비용 — 줄 수에 비례하여 매 세션 소비 |
| rules (globs 없음) | 항상 전체 | CLAUDE.md와 동일한 고정 비용 |
| rules (globs 있음) | 조건부 | **변동 비용** — 해당 경로 작업 시에만 소비 |
| @import 파일 | 항상 전체 삽입 | 고정 비용 — import하는 모든 파일 내용 포함 |

**핵심 인사이트**: CLAUDE.md에서 rules로 분리하는 최대 이유는 **globs 조건부 로딩으로 토큰을 절약**하는 것이다. CLAUDE.md 400줄 → 공통 100줄(CLAUDE.md) + 조건부 300줄(rules)로 분리하면, 특정 도메인 작업 시에만 해당 규칙이 로드되어 평균 컨텍스트 비용이 줄어든다.

---

## Sources

1. [Manage Claude's memory - Claude Code Docs](https://code.claude.com/docs/en/memory) — 공식 문서
2. [Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices) — 공식 문서
3. [Claude Code Rules Directory Guide](https://claudefa.st/blog/guide/mechanics/rules-directory) — 커뮤니티 가이드
4. [Claude Code: Rules vs Skills vs Agents Explained](https://jonimms.com/claude-code-rules-skills-agents-explained/) — 커뮤니티 블로그
5. [Writing a good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) — 커뮤니티 가이드
