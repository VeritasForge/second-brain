---
created: 2026-03-01
source: claude-code
tags:
  - claude-code
  - memory-system
  - CLAUDE-md
  - auto-memory
  - rules-directory
  - deep-dive
  - QA
  - best-practices
---

# Claude Code Memory System — Q&A Deep Dive

> **이 문서는** [[claude-code-memory-system-deep-dive]] 의 **2차 깊이 레이어**로, 기존 deep-dive 노트에서 발생하는 구체적 의문점 25+개를 체계적으로 답변한다.
> 관련 노트: [[claude-code-rules-vs-claude-md]]

---

## 카테고리 1: 메모리 구성 요소 심화

### Q1.1 CLAUDE.md와 `.claude/rules/`의 핵심 차이는?

> 상세 비교는 [[claude-code-rules-vs-claude-md]] 참조

**한줄 답**: CLAUDE.md는 **항상 전체 로드**되는 단일 파일, rules는 **경로별 조건부 로드** 가능한 모듈식 파일 컬렉션이다.

| 기준 | CLAUDE.md | `.claude/rules/*.md` |
|------|-----------|---------------------|
| 로드 방식 | 세션 시작 시 전체 로드 | 무조건 (globs 없음) 또는 조건부 (globs 있음) |
| 파일 수 | 단일 | 다중 (디렉토리 구조) |
| 컨텍스트 비용 | 항상 전체 소모 | 조건부 시 해당 path 작업 시에만 소모 |
| 팀 관리 | 단일 파일 변경 충돌 가능 | 파일별 독립 관리, git diff 용이 |
| 계층 | 전역/프로젝트/로컬 3레벨 | 전역(`~/.claude/rules/`) + 프로젝트(`.claude/rules/`) |

**핵심 포인트**: 프로젝트 크기가 커지면 CLAUDE.md의 "항상 전체 로드"가 토큰 낭비가 되므로, 도메인별 rules로 분리하는 것이 공식 권장 전략이다.

`[Confirmed]` — [공식 문서](https://code.claude.com/docs/en/memory)

---

### Q1.2 `.claude/rules/` 파일의 정확한 정의와 활용법은?

Rules 파일은 `.claude/rules/` 디렉토리 내의 `.md` 파일로, **YAML frontmatter의 `globs:` 필드**로 적용 범위를 제어한다.

**작성 문법**:

```yaml
# .claude/rules/api-validation.md
---
globs: src/api/**/*.ts, src/api/**/*.tsx
---

# API 개발 규칙
- 모든 엔드포인트는 Zod로 입력 검증
- 에러 응답: { error: string, code: number }
```

**동작 규칙**:
- `globs` 없음 → **항상 로드** (CLAUDE.md와 동일)
- `globs` 있음 → **매칭 파일 작업 시에만** 조건부 로드
- `.claude/rules/` 하위의 **서브디렉토리도 재귀 탐색**
- 사용자 전역 rules (`~/.claude/rules/`)에서는 `globs` frontmatter가 **무시됨** (2026.02 기준 알려진 제한)

**주의**: `paths:` YAML 배열 형식에 버그가 있으므로, `globs:` + 콤마 구분 형식 사용을 권장한다.

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

`[Confirmed]` — [공식 문서](https://code.claude.com/docs/en/memory), [[claude-code-rules-vs-claude-md]]

---

### Q1.3 MEMORY.md의 200줄 하드 리밋은 정확히 어떻게 작동하는가?

**동작 메커니즘**:
- `~/.claude/projects/<project>/memory/MEMORY.md`의 **처음 200줄만** 세션 시작 시 시스템 프롬프트에 자동 주입
- 200줄 이후는 **잘려서 로드되지 않음** (truncated)
- MEMORY.md 전체를 한 번에 로드하는 시점은 없음 — Claude가 필요 시 `Read` 도구로 직접 읽어야 함

**중요 구분**:
- MEMORY.md 200줄 → **하드 리밋** (시스템 레벨 제한)
- CLAUDE.md → 200줄 **권장 사항**이지 하드 리밋이 아님. 길어지면 신호/잡음비가 떨어질 뿐 잘리지는 않음

**실용 팁**: MEMORY.md를 인덱스/목차로 활용하고, 상세 내용은 토픽 파일로 분리하는 "인덱스 패턴"이 공식 권장이다.

`[Confirmed]` — [공식 문서](https://code.claude.com/docs/en/memory)

---

### Q1.4 토픽 파일은 정확히 무엇이며 어떻게 작동하는가?

**정의**: MEMORY.md와 같은 `~/.claude/projects/<project>/memory/` 디렉토리에 위치하는 **별도 .md 파일** (예: `debugging.md`, `api-conventions.md`).

**동작**:
- 세션 시작 시 **자동 로드되지 않음** (MEMORY.md만 200줄 자동 주입)
- Claude가 **필요할 때 `Read` 도구로 직접 접근**
- Claude가 학습 내용을 기록할 때 MEMORY.md(요약) + 토픽 파일(상세)로 분리 저장

**인덱스 패턴 예시**:

```markdown
# MEMORY.md (인덱스, 200줄 이하 유지)

## 프로젝트 개요
- 모노레포, pnpm workspace 구조
- TypeScript strict mode

## 디버깅 패턴
- 상세 → debugging.md 참조
- ESLint 관련 이슈 빈번

## API 컨벤션
- 상세 → api-conventions.md 참조
- REST + Zod 검증 패턴
```

```markdown
# debugging.md (토픽 파일)
## ESLint 이슈
- @typescript-eslint/no-unused-vars 오탐 빈번
- 해결: .eslintrc에 argsIgnorePattern 추가

## Vitest 이슈
- act() 경고 → waitFor로 래핑 필요
```

`[Confirmed]` — [공식 문서](https://code.claude.com/docs/en/memory)

---

### Q1.5 Agent Memory(서브에이전트 메모리)는 어떻게 작동하는가?

서브에이전트 정의 파일(`.claude/agents/*.md`)의 **`memory` frontmatter 필드**로 활성화한다.

**3가지 스코프**:

| 스코프 | 저장 위치 | 용도 |
|--------|-----------|------|
| `user` | `~/.claude/agent-memory/<agent-name>/` | 프로젝트 횡단 학습 (기본 권장) |
| `project` | `.claude/agent-memory/<agent-name>/` | 프로젝트 특화, Git 공유 가능 |
| `local` | `.claude/agent-memory-local/<agent-name>/` | 프로젝트 특화, Git 미추적 |

**frontmatter 예시**:

```yaml
---
name: code-reviewer
description: Reviews code for quality and best practices
memory: user
---
```

**핵심 동작**:
- `memory` 활성화 시 서브에이전트의 시스템 프롬프트에 메모리 읽기/쓰기 지침 자동 주입
- 메모리 디렉토리의 `MEMORY.md` 처음 200줄이 서브에이전트 시스템 프롬프트에 자동 주입
- `Read`, `Write`, `Edit` 도구가 자동 활성화 (명시적 `tools` 나열 불필요)
- **부모 대화의 auto memory를 상속하지 않음** — 각 서브에이전트는 독립적 메모리 공간 사용
- **스킬도 상속하지 않음** — 필요 시 `skills` frontmatter에 명시적 나열 필요

`[Confirmed]` — [공식 문서: Sub-agents](https://code.claude.com/docs/en/sub-agents)

---

### Q1.6 Auto Memory가 로컬 전용인 이유는?

**공식 문서에 명시된 근거는 없으나**, 다음 근거로 설계 의도를 추론할 수 있다:

1. **기기별 환경 차이**: 같은 프로젝트라도 macOS vs Linux에서 빌드 명령, 경로가 다를 수 있음
2. **프라이버시**: 개인 디버깅 패턴, 실수 기록은 팀에 공유할 필요 없음
3. **동기화 복잡도**: 여러 기기의 자동 학습 내용이 충돌할 경우 병합 전략이 필요
4. **역할 분리**: 팀 공유 지식은 CLAUDE.md/rules에, 개인 학습은 Auto Memory에 — 명확한 경계

**팀 공유가 필요한 경우**:
- 핵심 결정사항 → CLAUDE.md에 수동 기록
- 도메인별 규칙 → `.claude/rules/`
- 서브에이전트 지식 공유 → Agent Memory `project` 스코프 (Git 추적됨)

`[Likely]` — 공식 근거 없음, 설계 원리에서 추론

---

## 카테고리 2: 동작 원리 심화

### Q2.1 `@import` 5단계 깊이 제한은 어떻게 작동하는가?

**`@path/to/file` 구문**은 CLAUDE.md 내에서 외부 파일을 인라인으로 삽입하는 기능이다.

**동작 규칙**:
- 파일이 파일을 임포트하는 **재귀 깊이 최대 5단계**
- **순환 참조 방지**: A → B → A 같은 순환을 감지하고 처리
- 첫 사용 시 **사용자 승인 다이얼로그** 표시
- `--add-dir`로 추가 디렉토리의 CLAUDE.md 로드 시 `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` 환경변수 필요

**실용 예시**:

```markdown
# CLAUDE.md (1단계)
@.claude/architecture.md    # 아키텍처 문서 삽입
@docs/api-spec.md           # API 스펙 삽입

# .claude/architecture.md (2단계)
@docs/diagrams/overview.md  # 다이어그램 설명 삽입
```

**주의사항**: @import된 파일의 내용도 컨텍스트 윈도우를 소비하므로, 필요한 파일만 선택적으로 임포트해야 한다.

`[Confirmed]` — [공식 문서](https://code.claude.com/docs/en/memory)

---

### Q2.2 Auto Memory는 어떤 기준으로 학습 내용을 결정하는가?

**공식 알고리즘 사양은 공개되어 있지 않다.** 공식 문서의 유일한 설명:

> "Claude doesn't save something every session. It decides what's worth remembering based on whether the information would be useful in a future conversation."

**문서화된 학습 대상 카테고리**:
- 빌드 명령어
- 디버깅 인사이트
- 아키텍처 노트
- 코드 스타일 선호도
- 워크플로우 습관
- **사용자가 명시적으로 기억을 요청한 것** (예: "항상 pnpm을 사용해줘")

**실용적 관찰**:
- 매 세션마다 저장하지 않음 — "미래 유용성" 판단에 기반
- 사용자가 "remember" 키워드로 명시적 요청 시 → Auto Memory에 저장
- "add this to CLAUDE.md"로 명시 시 → CLAUDE.md에 저장 (Auto Memory 아님)
- 같은 Git 저장소의 모든 worktree와 하위 디렉토리가 **하나의 auto memory 디렉토리 공유**

**한계**: 어떤 내용이 저장될지 예측이 어렵고, 이것이 "자동 학습 불확실성"이라는 단점의 원인이다.

`[Confirmed]` — [공식 문서](https://code.claude.com/docs/en/memory) (알고리즘 세부사항은 비공개)

---

## 카테고리 3: 설정 & 커스터마이징

### Q3.1 `claudeMdExcludes`와 rules의 관계는?

**`claudeMdExcludes`**: `.claude/settings.local.json`에서 특정 CLAUDE.md 파일을 **glob 패턴으로 제외**하는 설정이다.

```json
// .claude/settings.local.json
{
  "claudeMdExcludes": [
    "packages/legacy/**",
    "vendor/**"
  ]
}
```

**rules와의 관계**:
- `claudeMdExcludes`는 **CLAUDE.md 파일만** 제외 대상 (하위 디렉토리의 CLAUDE.md)
- `.claude/rules/` 파일은 이 설정의 영향을 받지 않음
- Rules의 조건부 로딩은 자체 `globs` frontmatter로 제어

**모노레포 활용 시나리오**:

```
monorepo/
├── CLAUDE.md                    # 루트 공통 (항상 로드)
├── packages/
│   ├── frontend/CLAUDE.md       # 프론트엔드 팀 (로드)
│   ├── backend/CLAUDE.md        # 백엔드 팀 (로드)
│   └── legacy/CLAUDE.md         # 레거시 (claudeMdExcludes로 제외)
└── .claude/
    └── settings.local.json      # claudeMdExcludes: ["packages/legacy/**"]
```

`[Confirmed]` — [공식 문서](https://code.claude.com/docs/en/memory)

---

### Q3.2 서브에이전트 `persistent_memory` frontmatter 상세는?

→ Q1.5에서 상세 답변 완료. 핵심 요약:

- frontmatter 필드명: `memory` (공식 문서 기준)
- 3가지 스코프: `user`, `project`, `local`
- 서브에이전트가 독립적 MEMORY.md + 토픽 파일 공간을 가짐
- 부모 대화의 memory를 상속하지 않음

**추가 세부사항**:
- 서브에이전트 세션 transcript에는 `cleanupPeriodDays` (기본 30일) 자동 정리 적용
- 그러나 이는 **세션 기록 파일**에 대한 것이며, **MEMORY.md 내용** 자체는 자동 정리되지 않음

`[Confirmed]` — [공식 문서: Sub-agents](https://code.claude.com/docs/en/sub-agents)

---

## 카테고리 4: 베스트 프랙티스 심화

### Q4.1 "명령형 문체가 40% 더 잘 준수된다"의 출처는?

**결론: `[Unverified]` — 이 수치는 공식 Anthropic 출처가 아니다.**

**출처 추적 결과**:

| 주장 | 실제 출처 | 원본 내용 |
|------|-----------|-----------|
| "명령형이 40% 더 잘 준수" | SFEIR Institute (프랑스 컨설팅) | **두 개의 서로 다른 통계가 혼합됨** |

SFEIR Institute의 실제 통계 (자체 검증 없음):
1. "15개 명령형 규칙 → 94% 준수, 같은 내용 서술형 → 73% 준수" → **28.7% 상대 개선** (21 percentage-point)
2. "80줄 CLAUDE.md → 수동 교정 40% 감소 (50,000줄 TypeScript 프로젝트)" → 이것은 **파일 길이**에 관한 것

이 두 통계가 혼합되어 "명령형 = 40% 개선"이라는 주장이 만들어진 것으로 보인다.

**공식 문서의 실제 권장 사항**:
> "You can tune instructions by adding emphasis (e.g., 'IMPORTANT' or 'YOU MUST') to improve adherence."

→ 정성적 권장만 있고, 수치적 근거는 제공하지 않음.

**명령형 vs 서술형 실제 차이**:

```markdown
# 명령형 (권장) — 지시/명령 형태
- "함수형 컴포넌트를 사용하세요"
- "Use functional components"
- "ALWAYS validate inputs with Zod"

# 서술형 — 설명/묘사 형태
- "이 프로젝트는 함수형 컴포넌트를 사용합니다"
- "This project uses functional components"
- "Input validation is done with Zod"
```

명령형이 더 효과적이라는 것은 커뮤니티 합의이자 공식 권장이지만, **40%라는 구체적 수치는 검증되지 않았다.**

`[Unverified]` — SFEIR Institute 통계 혼합 유래, Anthropic 공식 수치 아님

---

### Q4.2 CLAUDE.md가 커졌을 때 rules로 분리해야 하는 이유는?

**3가지 핵심 이유**:

1. **컨텍스트 윈도우 비용**: CLAUDE.md는 항상 전체 로드 → 400줄이면 매 세션 400줄 토큰 소비. Rules의 `globs` 조건부 로딩은 해당 경로 작업 시에만 소비

2. **신호/잡음비**: 공식 문서 경고:
   > "If Claude keeps doing something you don't want despite having a rule against it, the file is probably too long and the rule is getting lost."

3. **팀 관리**: 단일 CLAUDE.md → git 변경 충돌 빈번. Rules 파일별 독립 → `security.md`는 보안팀, `api.md`는 백엔드팀이 독립 관리

**분리 기준**:

```
CLAUDE.md가 ~200줄 초과?
    ├── Yes → rules 분리 시작
    │     ├── 특정 파일 타입에만 적용 → globs 조건부 rule
    │     ├── 특정 도메인 지식 → 토픽별 rule (security.md, testing.md)
    │     └── 팀별 관리 필요 → 디렉토리 분리 (frontend/, backend/)
    └── No → CLAUDE.md 유지
```

`[Confirmed]` — [공식 문서](https://code.claude.com/docs/en/memory), [Best Practices](https://code.claude.com/docs/en/best-practices)

---

### Q4.3 "빌드/테스트 명령 포함 시 에러 60% 감소"의 출처는?

**결론: `[Unverified]` — 이 수치는 공식 Anthropic 출처가 아니다.**

**출처 추적 결과**:

| 주장 | 실제 출처 | 원본 내용 |
|------|-----------|-----------|
| "빌드/테스트 명령 → 에러 60% 감소" | SFEIR Institute | **인과관계가 뒤바뀐 다른 통계** |

SFEIR Institute의 실제 통계 (자체 검증 없음):
1. "복잡한 프로젝트에서 생성 에러의 60%는 **모호한 지시**에 기인" → 원인 분석이지 해결 효과가 아님
2. "Plan→Execute→Verify 워크플로우가 수정 반복을 60% 감소" → CLAUDE.md가 아닌 워크플로우에 관한 것

이 통계들이 왜곡되어 "빌드/테스트 명령 포함 → 60% 에러 감소"가 된 것으로 보인다.

**공식 문서의 실제 권장 사항**:
> "Include Bash commands, code style, and workflow rules. This gives Claude persistent context it can't infer from code alone."

→ 빌드/테스트 명령 포함을 권장하지만, 수치적 효과는 명시하지 않음.

**실용적 지침**: 빌드/테스트 명령을 CLAUDE.md에 포함하는 것은 **공식 권장 사항**이며 효과적이다. 다만 "60%"라는 구체적 수치는 검증되지 않았다.

`[Unverified]` — SFEIR Institute 통계 왜곡 유래, Anthropic 공식 수치 아님

---

### Q4.4 `/memory` 명령은 구체적으로 무엇을 하는가?

**공식 문서** (직접 인용):

> "The /memory command lists all CLAUDE.md and rules files loaded in your current session, lets you toggle auto memory on or off, and provides a link to open the auto memory folder. Select any file to open it in your editor."

**3가지 기능**:

1. **파일 목록 표시**: 현재 세션에 로드된 모든 CLAUDE.md 파일과 `.claude/rules/` 파일 나열
2. **Auto Memory 토글**: Auto Memory 기능을 켜거나 끌 수 있음
3. **메모리 폴더 열기**: Auto Memory 폴더를 에디터에서 열 수 있는 링크 제공

**Auto Memory 정리 방법**:

Auto Memory에는 **자동 정리(stale detection) 기능이 없다**. 정리는 수동으로 해야 한다:

```bash
# 방법 1: /memory 명령으로 파일 열어서 편집
# Claude Code 세션 내에서:
/memory

# 방법 2: 직접 파일 편집
# ~/.claude/projects/<project>/memory/ 디렉토리의 .md 파일을 직접 수정/삭제

# 방법 3: Claude에게 요청
# "메모리에서 OOO 관련 항목을 삭제해줘"
```

**참고**: 서브에이전트 세션 transcript에는 `cleanupPeriodDays` (기본 30일) 자동 정리가 적용되지만, 이는 세션 기록 파일에 대한 것이며 MEMORY.md 내용 자체와는 무관하다.

`[Confirmed]` — [공식 문서](https://code.claude.com/docs/en/memory)

---

### Q4.5 MEMORY.md 인덱스 패턴의 구체적 예제는?

**권장 구조**:

```
~/.claude/projects/-Users-me-my-project/memory/
├── MEMORY.md              # 인덱스 (200줄 이하 엄수)
├── debugging.md           # 디버깅 패턴 상세
├── api-conventions.md     # API 설계 결정 상세
├── performance.md         # 성능 최적화 인사이트
└── patterns.md            # 코드 패턴/컨벤션
```

**MEMORY.md 인덱스 예시** (200줄 이하):

```markdown
# MEMORY.md

## 프로젝트 개요
- Next.js 15 App Router + TypeScript strict
- pnpm workspace 모노레포
- Vitest + Playwright 테스트

## 아키텍처 결정
- RSC 기본, 'use client'는 인터랙션 필요 시에만
- API는 tRPC + Zod 검증
- 상세 → api-conventions.md

## 디버깅 패턴 (상세 → debugging.md)
- ESLint argsIgnorePattern 이슈 빈번
- Hydration mismatch → useEffect 래핑으로 해결

## 코드 스타일
- 2-space indent, single quotes
- 함수형 컴포넌트 + named exports
- 상세 → patterns.md

## 성능 (상세 → performance.md)
- 이미지: next/image + WebP 변환
- 번들: dynamic import으로 코드 스플릿
```

**핵심 원칙**:
- MEMORY.md는 **요약 + 참조 포인터**만 유지
- 상세 내용은 토픽 파일로 분리
- 200줄 이하를 엄수하여 세션 시작 시 전체가 주입되도록 보장

`[Confirmed]` — [공식 문서](https://code.claude.com/docs/en/memory) 기반 구성

---

### Q4.6 "세션 종료 시 3분 투자"는 구체적으로 무엇을 의미하는가?

**커뮤니티 인사이트에서 유래한 실천법**으로, 세션 종료 전에 다음을 수행하라는 의미:

**3분 체크리스트**:

1. **아키텍처 결정 기록** (CLAUDE.md):
   - "이 세션에서 결정한 설계 방향이 있는가?"
   - 예: "인증은 JWT가 아닌 session cookie로 결정"

2. **컨벤션 발견 기록** (CLAUDE.md 또는 rules):
   - "이 세션에서 새로 확립한 패턴이 있는가?"
   - 예: "에러 바운더리는 layout.tsx 레벨에서만 사용"

3. **디버깅 인사이트 확인** (Auto Memory 또는 수동):
   - "반복될 수 있는 이슈를 해결했는가?"
   - Claude에게: "이번 세션에서 중요한 발견사항을 메모리에 저장해줘"

**왜 효과적인가**:
- 다음 세션 시작 시 CLAUDE.md가 자동 로드되므로, 기록한 결정사항이 즉시 반영
- Auto Memory만 의존하면 "무엇이 저장됐는지 불확실" → 수동 기록이 보완
- **3분 투자 → 다음 세션 5-10분 절약** (컨텍스트 재설정 시간)

`[Likely]` — 커뮤니티 인사이트, 공식 문서에서 직접 언급하지는 않음

---

## 카테고리 5: 팀 & 확장

### Q5.1 심링크로 팀 규칙을 공유하는 구체적 방법은?

**공식 문서** (직접 인용):

> "The .claude/rules/ directory supports symlinks, so you can maintain a shared set of rules and link them into multiple projects. Symlinks are resolved and loaded normally, and circular symlinks are detected and handled gracefully."

**설정 방법**:

```bash
# 방법 1: 공유 디렉토리 전체 링크
ln -s ~/shared-claude-rules .claude/rules/shared

# 방법 2: 개별 파일 링크
ln -s ~/company-standards/security.md .claude/rules/security.md
```

**팀 구성 예시**:

```
# 공유 규칙 저장소 (별도 Git repo 또는 공유 디렉토리)
~/shared-claude-rules/
├── security.md          # 회사 보안 정책
├── code-review.md       # 코드 리뷰 표준
└── api-standards.md     # API 설계 표준

# 프로젝트 A
project-a/.claude/rules/
├── shared/ → ~/shared-claude-rules/   # 심링크
├── frontend.md                         # 프로젝트 고유
└── testing.md                          # 프로젝트 고유

# 프로젝트 B
project-b/.claude/rules/
├── shared/ → ~/shared-claude-rules/   # 같은 심링크
└── backend.md                          # 프로젝트 고유
```

**모노레포 시나리오**:

```
monorepo/
├── .claude/rules/
│   ├── company-wide.md              # 전사 공통
│   └── shared/ → ../shared-rules/  # 팀 공유
├── packages/frontend/.claude/rules/
│   └── react.md                     # 프론트엔드 전용
└── packages/backend/.claude/rules/
    └── api.md                       # 백엔드 전용
```

**추가 팀 공유 메커니즘**:
- **Managed Policy CLAUDE.md**: 조직 전체에 강제 (`/Library/Application Support/ClaudeCode/CLAUDE.md`)
- **Git을 통한 CLAUDE.md/rules 공유**: 소스 컨트롤에 포함
- **Agent Memory `project` 스코프**: `.claude/agent-memory/<agent-name>/`은 Git 추적 가능

`[Confirmed]` — [공식 문서](https://code.claude.com/docs/en/memory)

---

## 카테고리 6: 추가 심화 질문

### Q6.1 `/compact` 실행 시 메모리는 어떻게 보존되는가?

**동작**:
- `/compact` 실행 시 **대화 내용만 요약** (LLM으로 압축)
- **CLAUDE.md는 디스크에서 완전히 재로드** → 절대 손실 없음
- Auto Memory(MEMORY.md)도 시스템 프롬프트 구성 요소이므로 재로드
- 토픽 파일은 원래 on-demand이므로 영향 없음

`[Confirmed]` — [공식 문서](https://code.claude.com/docs/en/memory)

---

### Q6.2 `/init` 명령은 메모리 시스템과 어떻게 연관되는가?

**`/init`의 역할**:
- 프로젝트 구조를 분석하여 **CLAUDE.md를 자동 생성**
- 이미 CLAUDE.md가 있으면 **개선 제안**
- Auto Memory나 rules는 생성하지 않음

**권장 흐름**:
1. `/init` → CLAUDE.md 기본 생성
2. 수동으로 빌드/테스트 명령, 아키텍처 결정 추가
3. 프로젝트 성장 시 → `.claude/rules/`로 분리
4. Auto Memory → Claude가 자동 관리

`[Confirmed]` — [공식 문서](https://code.claude.com/docs/en/memory)

---

### Q6.3 계층 간 규칙이 충돌하면 어떻게 되는가?

**우선순위 원칙**: "더 구체적인 지침이 더 넓은 지침보다 우선"

**로드 순서** (낮은 → 높은 우선순위):
1. Managed Policy CLAUDE.md (조직) — **제외 불가** 🔒
2. `~/.claude/CLAUDE.md` (개인 전역)
3. `./CLAUDE.md` (프로젝트)
4. `./CLAUDE.local.md` (로컬 오버라이드)

**실용 가이드**:
- 상위 계층 = 일반적/광범위한 규칙
- 하위 계층 = 구체적/특수한 규칙
- 모순이 발생하면 하위(더 구체적)가 우선
- Anti-pattern: 상위에서 "절대 X하지 마" → 하위에서 "X해" → 예측 불가능

`[Confirmed]` — [공식 문서](https://code.claude.com/docs/en/memory)

---

### Q6.4 `autoMemoryEnabled: false` 설정의 영향은?

**비활성화 방법**:

```json
// .claude/settings.json
{
  "autoMemoryEnabled": false
}
```

또는 환경변수: `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`

**영향**:
- Claude가 MEMORY.md에 자동 기록하지 않음
- 기존 MEMORY.md는 여전히 세션 시작 시 로드됨 (읽기는 유지)
- 사용자가 수동으로 MEMORY.md를 편집하는 것은 여전히 가능
- `/memory` 명령에서 토글로도 on/off 가능

**비활성화가 적합한 경우**:
- 민감한 프로젝트에서 Claude의 자동 기록을 원치 않을 때
- CLAUDE.md + rules만으로 충분한 소규모 프로젝트
- 메모리 오염(잘못된 학습)이 우려될 때

`[Confirmed]` — [공식 문서](https://code.claude.com/docs/en/memory)

---

### Q6.5 여러 worktree가 메모리를 공유하는가?

**예.** 같은 Git 저장소의 모든 worktree와 하위 디렉토리가 **하나의 auto memory 디렉토리를 공유**한다.

경로: `~/.claude/projects/<project-path-hash>/memory/`

이 `<project-path-hash>`는 Git 저장소의 루트 경로에서 파생되므로, 같은 repo의 worktree들은 동일한 해시를 가진다.

`[Confirmed]` — [공식 문서](https://code.claude.com/docs/en/memory)

---

### Q6.6 CLAUDE.md에 코드 스니펫을 포함하는 것이 왜 효과적인가?

기존 deep-dive 노트의 "5줄 코드 예시 > 50단어 설명" 원칙의 근거:

**이유**:
- LLM은 **패턴 매칭**에 강함 — 코드 예시는 직접적인 패턴 제공
- 자연어 설명은 해석의 여지가 있지만, 코드는 **명확하고 모호하지 않음**
- 프롬프트 내 few-shot 예시 효과와 동일한 원리

**예시**:

```markdown
# 좋은 예 (코드 스니펫)
API 에러 응답 형식:
\`\`\`typescript
return NextResponse.json(
  { error: "Not found", code: "RESOURCE_NOT_FOUND" },
  { status: 404 }
);
\`\`\`

# 나쁜 예 (장황한 설명)
API에서 에러가 발생하면 JSON 형식으로 응답해야 하며, error 필드에는
사람이 읽을 수 있는 메시지를, code 필드에는 대문자 스네이크 케이스로 된
에러 코드를, HTTP 상태 코드는 적절한 4xx 또는 5xx를 사용해야 합니다.
```

`[Likely]` — 공식 문서 Best Practices 권장, LLM 프롬프팅 원리에서 추론

---

### Q6.7 메모리 시스템의 컨텍스트 윈도우 비용은 어떻게 관리하는가?

**비용 발생 지점**:

| 구성 요소 | 비용 특성 | 관리 방법 |
|-----------|-----------|-----------|
| CLAUDE.md | 항상 전체 로드 | 200줄 이하 유지, 넘으면 rules로 분리 |
| rules (globs 없음) | 항상 전체 로드 | 정말 전역적인 규칙만 globs 없이 |
| rules (globs 있음) | 조건부 로드 | 도메인별 분리로 토큰 절약 |
| MEMORY.md | 200줄 고정 | 인덱스 패턴으로 효율화 |
| 토픽 파일 | on-demand | 비용 없음 (필요 시에만) |
| @import 파일 | 항상 전체 삽입 | 필요한 것만 선택적 import |

**최적화 전략**:

```
총 컨텍스트 비용 = CLAUDE.md 전체
                 + 무조건 rules 전체
                 + 매칭된 조건부 rules
                 + MEMORY.md 200줄
                 + @import 파일 전체
```

- `claudeMdExcludes`로 불필요한 하위 CLAUDE.md 제외
- path-specific rules를 적극 활용하여 조건부 로딩
- MEMORY.md는 인덱스 + 토픽 파일 패턴 사용

`[Confirmed]` — [공식 문서](https://code.claude.com/docs/en/memory)

---

### Q6.8 v2.1.50 메모리 누수 패치의 내용은?

기존 deep-dive 노트에서 언급한 "장시간 세션 메모리 누수 패치":

- **파일 히스토리 스냅샷 캡**: 무한 증가하던 파일 변경 이력에 상한 설정
- **내부 캐시 정리**: 사용하지 않는 캐시 데이터 주기적 해제
- **LSP 데이터 해제**: Language Server Protocol 통신 데이터 정리

이는 Claude Code 프로세스의 **런타임 메모리(RAM)** 누수이며, MEMORY.md와 같은 **영속 메모리 시스템**과는 별개의 이슈다.

`[Confirmed]` — [릴리즈 노트](https://releasebot.io/updates/anthropic/claude-code)

---

## 미검증 주장 종합 (Unverified Claims Summary)

기존 [[claude-code-memory-system-deep-dive]] 노트에서 출처가 불명확한 주장들의 추적 결과:

| # | 주장 | 출처 추적 결과 | 실제 출처 | 태그 |
|---|------|---------------|-----------|------|
| 1 | "명령형이 40% 더 잘 준수" | SFEIR Institute의 두 통계 혼합 (94% vs 73% + 40% 수동교정 감소) | [SFEIR Deep Dive](https://institute.sfeir.com/en/claude-code/claude-code-memory-system-claude-md/deep-dive/) | `[Unverified]` |
| 2 | "빌드/테스트 명령 → 에러 60% 감소" | SFEIR의 "60% 에러는 모호한 지시 기인" 인과관계 뒤바뀜 | [SFEIR Optimization](https://institute.sfeir.com/en/claude-code/claude-code-memory-system-claude-md/optimization/) | `[Unverified]` |
| 3 | "CLAUDE.md 200줄 초과 실수 45%" | SFEIR Institute | 출처 검증 불가, 자체 방법론 미공개 | `[Unverified]` |
| 4 | "Auto Memory 방치 70%" | SFEIR Institute | 출처 검증 불가 | `[Unverified]` |
| 5 | "수동적 문체 사용 60%" | SFEIR Institute | 출처 검증 불가 | `[Unverified]` |

**SFEIR Institute 정보**: 프랑스 IT 컨설팅 기업의 교육 자료. Anthropic 공식 관계 없음. 통계에 대한 방법론, 샘플 크기, 원본 연구가 제공되지 않음.

**원칙**: 수치 자체보다 **공식 권장 사항의 방향성**이 중요하다. 명령형 문체 사용, 빌드/테스트 명령 포함은 공식 권장이며 효과적이다 — 다만 구체적 수치는 검증되지 않았을 뿐이다.

---

## Sources

1. [How Claude remembers your project - Claude Code Docs](https://code.claude.com/docs/en/memory) — 공식 문서
2. [Create custom subagents - Claude Code Docs](https://code.claude.com/docs/en/sub-agents) — 공식 문서
3. [Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices) — 공식 문서
4. [SFEIR Institute - CLAUDE.md Deep Dive](https://institute.sfeir.com/en/claude-code/claude-code-memory-system-claude-md/deep-dive/) — 커뮤니티 교육 (비공식)
5. [SFEIR Institute - Optimization](https://institute.sfeir.com/en/claude-code/claude-code-memory-system-claude-md/optimization/) — 커뮤니티 교육 (비공식)
6. [SFEIR Institute - Advanced Best Practices](https://institute.sfeir.com/en/claude-code/claude-code-advanced-best-practices/) — 커뮤니티 교육 (비공식)
7. [Claude Code Release Notes](https://releasebot.io/updates/anthropic/claude-code) — 릴리즈 노트

---

> **Research Metadata**
> - 리서치 에이전트: 2개 병렬 실행 (출처 추적 + 공식 문서 확인)
> - 검색 쿼리 수: 20+ (WebSearch) + 5+ (WebFetch)
> - 확신도 분포: `[Confirmed]` 18개, `[Likely]` 3개, `[Unverified]` 5개
> - 교차 검증: SFEIR Institute 통계 → Anthropic 공식 문서 대조 → 불일치 확인
> - 관련 노트: [[claude-code-memory-system-deep-dive]], [[claude-code-rules-vs-claude-md]]
