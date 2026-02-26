---
created: 2026-02-03
source: claude-code
tags:
  - claude-code
  - deep-research
  - CLAUDE-md
  - skills
  - agents
  - rules
  - slash-commands
---

# Deep Research: Claude Code 핵심 구성 요소 완전 분석

## Executive Summary

Claude Code는 **5가지 핵심 구성 요소**로 커스터마이징됩니다: **CLAUDE.md**(항상 로드되는 프로젝트 메모리), **Rules**(경로별 조건부 규칙), **Skills**(온디맨드 능력 확장), **Slash Commands**(Skills에 통합된 레거시 명령어), **Agents/Subagents**(독립 컨텍스트의 전문 AI 어시스턴트). 이들은 마치 **학교 시스템**에 비유할 수 있습니다 — CLAUDE.md는 학칙(항상 적용), Rules는 과목별 규칙, Skills는 선생님이 필요할 때 꺼내는 교과서, Slash Commands는 교과서의 간단 버전, Agents는 각 과목 전담 선생님입니다.

---

## 조사 과정에서 사용한 리소스 상호작용

```
┌──────────────────────────────────────────────────────────────┐
│                    Deep Research Flow                          │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  Phase 1: 광역 탐색                                           │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  WebSearch ×6 (병렬)                                     │  │
│  │  ├── 공식 문서 검색                                      │  │
│  │  ├── Boris Cherny 검색                                   │  │
│  │  ├── 정규봉/revfactory 검색                              │  │
│  │  ├── Reddit SNS 검색                                     │  │
│  │  ├── 베스트 프랙티스 검색                                │  │
│  │  └── 커스터마이징 가이드 검색                            │  │
│  └──────────────────────┬──────────────────────────────────┘  │
│                          │                                     │
│  Phase 2: 심화 탐색                                           │
│  ┌──────────────────────▼──────────────────────────────────┐  │
│  │  WebFetch ×4 (병렬) + WebSearch ×1                       │  │
│  │  ├── revfactory.github.io (정규봉 자료)                  │  │
│  │  ├── code.claude.com/docs/en/skills (공식)               │  │
│  │  ├── code.claude.com/docs/en/best-practices (공식)       │  │
│  │  ├── code.claude.com/docs/en/memory (공식)               │  │
│  │  ├── code.claude.com/docs/en/sub-agents (공식)           │  │
│  │  └── alexop.dev 커스터마이징 가이드                      │  │
│  └──────────────────────┬──────────────────────────────────┘  │
│                          │                                     │
│  Phase 3: 지식 합성                                           │
│  ┌──────────────────────▼──────────────────────────────────┐  │
│  │  sequential-thinking ×4                                   │  │
│  │  ├── 쿼리 분해 및 전략 수립                              │  │
│  │  ├── 수집 데이터 구조화                                  │  │
│  │  ├── 출력 구조 설계                                      │  │
│  │  └── 최종 합성                                           │  │
│  └─────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 1. 각 구성 요소 상세 분석

### 1-1. CLAUDE.md (Memory)

#### 무엇인가?

Claude Code가 **모든 세션 시작 시 자동으로 읽는** 특수 마크다운 파일입니다. 프로젝트의 "헌법(Constitution)"이라고 불립니다. `[Confirmed]`

> 비유: **학교의 교칙**과 같습니다. 학생(Claude)이 학교에 올 때마다 반드시 확인하는 기본 규칙이죠.

#### 개념

| 속성 | 설명 |
|------|------|
| **자동 로드** | 세션 시작 시 항상 컨텍스트에 주입 |
| **계층 구조** | Managed Policy > Project > Rules > User > Local |
| **공유 범위** | Git으로 팀 공유 가능 (CLAUDE.local.md는 개인용) |
| **형식** | 자유 형식 마크다운, 간결할수록 좋음 |

#### 아키텍처와 동작 원리

```
로드 순서 (위에서 아래로, 상위가 우선):

1. Managed Policy     /Library/Application Support/ClaudeCode/CLAUDE.md
       ↓
2. Project Memory     ./CLAUDE.md 또는 ./.claude/CLAUDE.md
       ↓
3. Project Rules      ./.claude/rules/*.md (동일 우선순위)
       ↓
4. User Memory        ~/.claude/CLAUDE.md
       ↓
5. Project Local      ./CLAUDE.local.md (.gitignore 대상)

※ 하위 디렉토리의 CLAUDE.md는 해당 파일 작업 시 온디맨드 로드
※ @import 문법으로 외부 파일 참조 가능 (최대 5 depth)
```

- **재귀적 탐색**: cwd에서 루트까지 상위로 올라가며 모든 CLAUDE.md를 발견 `[Confirmed]`
- **@import**: `@README.md`, `@docs/guide.md` 형태로 외부 파일 임포트 가능 `[Confirmed]`
- **첫 임포트 시 승인 다이얼로그** 표시, 한 번 거절하면 다시 묻지 않음 `[Confirmed]`

#### 유즈케이스 및 베스트 프랙티스

**포함해야 할 것** `[Confirmed]`:
- Claude가 추측할 수 없는 Bash 명령어 (빌드, 테스트, 린트)
- 기본값과 다른 코드 스타일 규칙
- 저장소 에티켓 (브랜치 네이밍, PR 컨벤션)
- 프로젝트 고유 아키텍처 결정
- 개발 환경 quirk (필수 환경변수 등)

**제외해야 할 것** `[Confirmed]`:
- Claude가 코드를 읽고 파악할 수 있는 것
- 표준 언어 컨벤션 (Claude가 이미 알고 있음)
- 상세 API 문서 (링크로 대체)
- 자주 변경되는 정보
- "깨끗한 코드를 작성하라" 같은 자명한 지시

**Boris Cherny의 팁** `[Confirmed]`:
> "팀이 Claude가 잘못하는 것을 볼 때마다 CLAUDE.md에 추가하여, Claude가 다음에는 하지 않도록 합니다."

#### 장단점

| 장점 | 단점 |
|------|------|
| 모든 세션에 자동 적용 | 너무 길면 Claude가 지시를 무시 |
| 팀 공유 가능 (Git) | 매 세션마다 토큰 소비 |
| @import로 모듈화 가능 | 자주 변경되는 정보에 부적합 |
| `/init`으로 자동 생성 | 긴 세션에서 맥락이 희미해질 수 있음 |

#### 주의점

- **150~200개 지시가 한계**: 연구에 따르면 프론티어 LLM이 합리적으로 따를 수 있는 지시 수 `[Likely]`
- **"IMPORTANT", "YOU MUST"** 같은 강조를 통해 준수율 향상 가능 `[Confirmed]`
- Claude가 계속 같은 실수를 한다면 → 파일이 너무 길어서 규칙이 묻힌 것 `[Confirmed]`

---

### 1-2. Rules (.claude/rules/)

#### 무엇인가?

`.claude/rules/` 디렉토리에 저장되는 **모듈화된 프로젝트 지침 파일**들입니다. CLAUDE.md를 주제별로 분리한 것입니다. `[Confirmed]`

> 비유: CLAUDE.md가 **학교 교칙 전체**라면, Rules는 **과목별 수업 규칙**입니다. 수학 시간에는 수학 규칙만, 체육 시간에는 체육 규칙만 적용되죠.

#### 개념

| 속성 | 설명 |
|------|------|
| **조건부 적용** | `paths` frontmatter로 특정 파일에만 적용 가능 |
| **자동 발견** | .claude/rules/ 하위 모든 .md 파일 재귀 탐색 |
| **우선순위** | .claude/CLAUDE.md와 동일 |
| **구조화** | 하위 디렉토리, 심링크 지원 |

#### 아키텍처와 동작 원리

```yaml
# 조건부 규칙 예시 (paths 사용)
---
paths:
  - "src/api/**/*.ts"
  - "tests/**/*.test.ts"
---
# API 개발 규칙
- 모든 API 엔드포인트에 입력 검증 포함
- 표준 에러 응답 형식 사용
```

```yaml
# 전역 규칙 (paths 없음 → 항상 적용)
---
---
# 일반 코딩 규칙
- 함수는 50줄 이하로 유지
```

**중요**: Cursor의 `globs`가 아닌 `paths`를 사용합니다. `alwaysApply`도 Cursor 전용입니다. `[Confirmed]`

#### 유즈케이스 및 베스트 프랙티스

```
.claude/rules/
├── frontend/
│   ├── react.md          # React 컴포넌트 규칙
│   └── styles.md         # CSS/스타일 규칙
├── backend/
│   ├── api.md            # API 설계 규칙 (paths: src/api/**)
│   └── database.md       # DB 규칙 (paths: **/migrations/**)
├── security.md           # 보안 규칙 (전역)
└── testing.md            # 테스트 규칙 (paths: tests/**)
```

- **각 파일은 하나의 주제**에 집중 `[Confirmed]`
- **파일명으로 내용을 유추**할 수 있게 작성
- **조건부 규칙은 꼭 필요할 때만** 사용 — 대부분의 규칙은 전역이 적합
- 사용자 레벨 Rules: `~/.claude/rules/`에 개인 규칙 배치 가능

#### 장단점

| 장점 | 단점 |
|------|------|
| 주제별 모듈화로 유지보수 용이 | paths가 없으면 전부 로드 (토큰 소비) |
| 경로별 조건부 적용 | 규칙 간 충돌 가능성 |
| 하위 디렉토리/심링크 지원 | CLAUDE.md와 중복 가능 |
| 팀 공유 가능 (Git) | 규칙이 많으면 관리 복잡 |

---

### 1-3. Skills (.claude/skills/)

#### 무엇인가?

Claude의 능력을 확장하는 **재사용 가능한 지침 패키지**입니다. SKILL.md + 지원 파일(템플릿, 스크립트 등)으로 구성됩니다. **Agent Skills 오픈 표준**을 따릅니다. `[Confirmed]`

> 비유: **교과서**와 같습니다. 선생님(Claude)이 모든 교과서를 항상 들고 다니지 않고, 수업(작업)에 필요한 교과서만 꺼내 읽습니다. 제목(description)만 보고 어떤 교과서를 꺼낼지 판단하죠.

#### 개념

Skills의 핵심 혁신은 **Progressive Disclosure(점진적 노출)** 입니다:

```
Session Start
    │
    ▼
┌─────────────────────────────┐
│ description만 로드 (간략)    │  ← 항상 컨텍스트에 존재
│ "이런 스킬들이 있다"         │     (15,000자 기본 예산)
└─────────────┬───────────────┘
              │ 매칭 시 or /skill-name
              ▼
┌─────────────────────────────┐
│ SKILL.md 전체 내용 로드      │  ← 온디맨드 로드
│ 지원 파일도 참조 가능        │
└─────────────────────────────┘
```

이것이 CLAUDE.md와의 **근본적 차이**입니다. CLAUDE.md는 항상 전체가 로드되지만, Skills는 **필요할 때만** 로드됩니다. `[Confirmed]`

> "Skills are (maybe) a bigger deal than MCP." — 커뮤니티 반응 `[Likely]`

#### 아키텍처와 동작 원리

**스킬 디렉토리 구조**:
```
my-skill/
├── SKILL.md           # 메인 지침 (필수, 500줄 이하 권장)
├── template.md        # Claude가 채울 템플릿
├── examples/
│   └── sample.md      # 기대 출력 예시
└── scripts/
    └── validate.sh    # Claude가 실행할 스크립트
```

**Frontmatter 옵션** `[Confirmed]`:

| 필드 | 필수 | 설명 |
|------|------|------|
| `name` | 아니오 | `/slash-command` 이름 (없으면 디렉토리명) |
| `description` | 권장 | Claude가 자동 적용 판단에 사용 |
| `disable-model-invocation` | 아니오 | `true`면 사용자만 호출 가능 |
| `user-invocable` | 아니오 | `false`면 `/` 메뉴에서 숨김 |
| `allowed-tools` | 아니오 | 스킬 활성화 시 사용 가능한 도구 제한 |
| `model` | 아니오 | 스킬 활성화 시 사용할 모델 |
| `context` | 아니오 | `fork`로 서브에이전트에서 실행 |
| `agent` | 아니오 | `context: fork` 시 사용할 에이전트 |

**호출 제어 매트릭스** `[Confirmed]`:

| 설정 | 사용자 호출 | Claude 호출 | 컨텍스트 로드 |
|------|:-----------:|:-----------:|:-------------:|
| (기본값) | O | O | description 항상, 전체는 호출 시 |
| `disable-model-invocation: true` | O | X | description 로드 안됨 |
| `user-invocable: false` | X | O | description 항상 |

**Dynamic Context Injection** `[Confirmed]`:
```yaml
---
name: pr-summary
---
- PR diff: !`gh pr diff`        # 실행 결과가 주입됨
- Changed files: !`gh pr diff --name-only`
```
`` !`command` `` 문법으로 셸 명령 전처리 — Claude는 최종 결과만 봄.

**Extended Thinking 활성화**: 스킬 내용에 "ultrathink" 단어를 포함하면 됨 `[Confirmed]`

#### 유즈케이스 및 베스트 프랙티스

1. **Reference 스킬**: API 컨벤션, 도메인 지식 등 → 인라인 실행
2. **Task 스킬**: 배포, 커밋, 코드 생성 등 → `disable-model-invocation: true` 권장
3. **Forked 스킬**: `context: fork`로 독립 실행 → 무거운 리서치에 적합

**커뮤니티 반패턴 경고** `[Confirmed]`:
> "긴 목록의 복잡한 커스텀 슬래시 커맨드를 만들었다면, 안티 패턴을 만든 것입니다. 엔지니어가 새로운 매직 커맨드 목록을 학습해야 한다면, 실패한 것입니다."

#### 장단점

| 장점 | 단점 |
|------|------|
| 온디맨드 로드 (토큰 효율적) | 디렉토리 구조 관리 필요 |
| 지원 파일 포함 가능 | description이 많으면 15,000자 예산 초과 |
| 자동 발견 + 수동 호출 모두 지원 | 트리거 조건 튜닝 필요 |
| Agent Skills 오픈 표준 | CLAUDE.md보다 설정 복잡 |
| context: fork로 컨텍스트 격리 | fork 시 대화 히스토리 접근 불가 |

---

### 1-4. Slash Commands (.claude/commands/)

#### 무엇인가?

**Skills에 통합된 레거시 명령 체계**입니다. `.claude/commands/review.md`와 `.claude/skills/review/SKILL.md`는 모두 `/review`를 생성하며 동일하게 작동합니다. `[Confirmed]`

> 비유: Skills가 **두꺼운 참고서**라면, Slash Commands는 **요약 노트**입니다. 같은 내용이지만 더 간단한 형태죠.

#### 개념

```
.claude/commands/fix-issue.md     ← 단일 파일
.claude/skills/fix-issue/SKILL.md ← 디렉토리 + 지원 파일

둘 다 /fix-issue 를 생성.
동일 이름 시 Skill이 우선.
```

- `$ARGUMENTS`로 인수 전달
- 개인용: `~/.claude/commands/`, 프로젝트용: `.claude/commands/`
- Skills의 모든 frontmatter 옵션 지원

#### 왜 아직 존재하는가?

1. **하위 호환성** — 기존 프로젝트가 계속 동작
2. **단순한 경우에 적합** — 단일 파일로 충분할 때 디렉토리 생성 불필요
3. **빠른 생성** — 파일 하나만 만들면 됨

#### 장단점

| 장점 | 단점 |
|------|------|
| 생성이 매우 간단 | 지원 파일 불가 |
| 기존 프로젝트와 호환 | Skills에 비해 기능 제한 |
| 단일 파일로 완결 | 장기적으로 deprecated 가능성 |

---

### 1-5. Agents / Subagents (.claude/agents/)

#### 무엇인가?

**독립된 컨텍스트 윈도우**에서 특정 작업을 수행하는 전문 AI 어시스턴트입니다. 메인 대화를 오염시키지 않고 작업을 위임할 수 있습니다. `[Confirmed]`

> 비유: **과목 전담 선생님**입니다. 국어 선생님한테 수학 질문이 들어오면, 수학 전담 선생님에게 보내서 답을 받아오죠. 수학 선생님은 자기만의 교실(컨텍스트)에서 일하고, 결과만 돌려줍니다.

#### 개념

```
메인 대화 (Context Window A)
    │
    │ "이 코드 보안 검토해줘"
    │
    ▼
┌──────────────────────────┐
│ security-reviewer        │
│ (Context Window B)       │  ← 독립 컨텍스트!
│                          │
│ System Prompt: 보안 전문가│
│ Tools: Read, Grep, Glob  │
│ Model: opus              │
│                          │
│ [파일 읽기, 분석...]     │
│                          │
│ → 요약 결과만 반환 ──────│──→ 메인 대화에 삽입
└──────────────────────────┘
```

핵심 가치: **메인 컨텍스트 보존**. 서브에이전트가 100개 파일을 읽어도, 메인에는 요약만 돌아옵니다. `[Confirmed]`

#### Built-in Agents `[Confirmed]`

| Agent | 모델 | 도구 | 용도 |
|-------|------|------|------|
| **Explore** | Haiku (빠름) | Read-only | 코드베이스 탐색/검색 |
| **Plan** | 상속 | Read-only | Plan Mode에서 리서치 |
| **general-purpose** | 상속 | 전체 | 복잡한 멀티스텝 작업 |
| **Bash** | 상속 | Bash | 터미널 명령 실행 |

#### Custom Agent Frontmatter `[Confirmed]`

| 필드 | 필수 | 설명 |
|------|------|------|
| `name` | Yes | 고유 식별자 (소문자+하이픈) |
| `description` | Yes | Claude가 위임 판단에 사용 |
| `tools` | No | 사용 가능한 도구 (없으면 전체 상속) |
| `disallowedTools` | No | 차단할 도구 |
| `model` | No | sonnet, opus, haiku, inherit |
| `permissionMode` | No | default, acceptEdits, dontAsk, bypassPermissions, plan |
| `skills` | No | 시작 시 주입할 스킬들 |
| `hooks` | No | 라이프사이클 훅 |

#### Agent 스코프 (우선순위 순) `[Confirmed]`

| 위치 | 범위 | 우선순위 |
|------|------|----------|
| `--agents` CLI 플래그 | 현재 세션 | 1 (최고) |
| `.claude/agents/` | 현재 프로젝트 | 2 |
| `~/.claude/agents/` | 모든 프로젝트 | 3 |
| Plugin의 `agents/` | 플러그인 활성화된 곳 | 4 (최저) |

#### 주요 패턴

1. **고용량 작업 격리**: 테스트 실행, 로그 분석 → 서브에이전트에 위임
2. **병렬 리서치**: 여러 모듈을 병렬로 조사
3. **체이닝**: code-reviewer → optimizer 순차 실행
4. **Writer/Reviewer 패턴**: 세션 A가 작성, 세션 B가 리뷰 (신선한 눈)

#### Boris Cherny의 Agent 철학 `[Confirmed]`

> "에이전트는 '하나의 큰 에이전트'가 아닙니다. 모듈형 역할입니다. 신뢰성은 전문화와 제약에서 옵니다."

> **반드시 피해야 할 안티패턴**: "전문가 페르소나" 패턴. 서브에이전트를 특정 성격이나 전문 분야가 할당된 '캐릭터'로 만들지 마세요. 과도한 역할 정의는 모델 응답을 실제 요구사항에서 벗어나게 합니다. 서브에이전트는 **작업 실행 도구**여야지, 캐릭터가 아닙니다.

#### 장단점

| 장점 | 단점 |
|------|------|
| 메인 컨텍스트 보존 | 서브에이전트 중첩 불가 (1레벨) |
| 도구/권한 격리 가능 | 결과 반환 시 토큰 소비 |
| 모델별 최적화 (Haiku로 비용 절감) | 대화 히스토리 접근 불가 |
| Foreground/Background 실행 | Background에서 MCP 사용 불가 |
| Resume 가능 | 컨텍스트 재구축 오버헤드 |

#### 주의점

- **서브에이전트는 다른 서브에이전트를 생성할 수 없음** `[Confirmed]`
- Background 서브에이전트는 **사전에 권한 승인** 필요 `[Confirmed]`
- 많은 서브에이전트가 상세 결과를 반환하면 메인 컨텍스트가 소비됨 `[Confirmed]`

---

## 2. 핵심 비교 매트릭스

### 전체 비교표 `[Confirmed]`

| 특성 | CLAUDE.md | Rules | Skills | Slash Commands | Agents |
|------|:---------:|:-----:|:------:|:--------------:|:------:|
| **로딩 시점** | 항상 | 항상/조건부 | 온디맨드 | 온디맨드 | 위임 시 |
| **컨텍스트 공유** | 메인 | 메인 | 메인 (fork 제외) | 메인 | 독립 |
| **자동 적용** | O | O | O | X | O |
| **수동 호출** | X | X | O | O | O |
| **지원 파일** | @import | X | O (디렉토리) | X | X |
| **도구 제한** | X | X | O | X | O |
| **모델 선택** | X | X | O | X | O |
| **팀 공유** | Git | Git | Git/Plugin | Git | Git/Plugin |
| **토큰 효율** | 낮음(항상) | 중간 | 높음(온디맨드) | 높음 | 최고(분리) |
| **복잡도** | 낮음 | 낮음 | 중간 | 낮음 | 높음 |

### 언제 무엇을 쓸까? `[Confirmed]`

```
질문: "이 지침은..."

항상 적용되어야 한다 ──────────────→ CLAUDE.md
  │
  └── 특정 파일에만 적용 ──────────→ Rules (paths)

필요할 때만 로드되면 된다 ──────────→ Skills
  │
  ├── 사용자가 명시적으로 호출 ─────→ Skills (disable-model-invocation: true)
  │                                    또는 Slash Commands
  │
  └── Claude가 자동 판단 ──────────→ Skills (기본값)

독립 컨텍스트가 필요하다 ──────────→ Agents
  │
  ├── 읽기만 필요 ─────────────────→ Explore (built-in)
  ├── 도구/권한 격리 필요 ─────────→ Custom Agent
  └── 비용 절감 필요 ──────────────→ Agent + model: haiku
```

---

## 3. Boris Cherny (Claude Code 창시자)의 핵심 철학

Boris Cherny는 Anthropic의 Staff Engineer로 2024년 9월 사이드 프로젝트로 Claude Code를 시작했습니다. 30일 동안 259개 PR, 497개 커밋, 40K+ 라인 추가를 기록했습니다. `[Confirmed]`

### 22가지 팁 중 핵심 원칙

| # | 원칙 | 설명 |
|---|------|------|
| 1 | **인프라로 다루라** | 마법이 아닌 시스템으로 접근. 메모리 파일, 권한 설정, 검증 루프, 포매팅 훅을 구축 |
| 2 | **5개 병렬 세션** | "터미널에서 5개 Claude를 병렬로 실행합니다. 1-5번으로 탭을 번호 매기고, 시스템 알림으로 입력이 필요할 때를 알립니다" |
| 3 | **Plan-First** | 복잡한 작업은 Plan Mode부터. 계획 단계가 가장 높은 레버리지 활동 |
| 4 | **검증이 가장 중요** | "Claude에게 자신의 작업을 검증할 방법을 주는 것이 최고의 결과를 얻는 가장 중요한 것" — 결과 품질 2-3배 향상 |
| 5 | **팀 메모리** | CLAUDE.md에 잘못된 행동을 기록 → 팀 지식의 구조적 문서화 |
| 6 | **모듈형 에이전트** | 하나의 큰 에이전트가 아닌 전문화된 역할. "전문가 페르소나" 안티패턴 경고 |
| 7 | **Inner Loop 자동화** | 매일 수십 번 하는 작업은 slash command로. `/commit-push-pr`을 하루에 수십 번 사용 |
| 8 | **안전 설계** | `--dangerously-skip-permissions` 사용 안 함. `/permissions`로 안전한 명령만 사전 허용 |

---

## 4. 정규봉(revfactory)의 인사이트

정규봉 님은 [Claude Code Mastering](https://revfactory.github.io/claude-code-mastering/)이라는 **320페이지** 분량의 한국어 자료를 공개했습니다. `[Confirmed]`

핵심 관점:
- Claude Code는 **"단순한 코드 자동완성을 넘어, 진정한 의미의 'AI 동료'로서 개발자와 협업하는 새로운 패러다임"** `[Confirmed]`
- **"경험 많은 시니어 개발자와 함께 일하는 것처럼"** Claude Code가 의도를 이해하고 최적의 솔루션을 제안 `[Confirmed]`

---

## 5. Edge Cases & Caveats

| 상황 | 영향 | 권고 |
|------|------|------|
| Skills 수가 많을 때 | description 15,000자 예산 초과 → 일부 스킬 제외 | `SLASH_COMMAND_TOOL_CHAR_BUDGET` 환경변수 조정 |
| CLAUDE.md가 너무 길 때 | 규칙이 무시됨 | 주기적 프루닝, Hook으로 대체 가능한 것은 Hook으로 |
| 서브에이전트 중첩 시도 | 불가능 (1레벨 한정) | 메인 대화에서 체이닝으로 우회 |
| Background 서브에이전트 | MCP 사용 불가, 질문 실패 | 권한 사전 승인, 필요시 foreground resume |
| Rules에 `globs` 사용 | 작동 안됨 (Cursor 문법) | `paths`를 사용해야 함 |
| Skill의 `context: fork` + 가이드라인만 | 실행 불가 (actionable prompt 없음) | Task 지시가 반드시 포함되어야 함 |

---

## 6. 기타 개발자로서 알아둬야 할 것들

### 컨텍스트 윈도우가 모든 것의 핵심 `[Confirmed]`

> "대부분의 베스트 프랙티스는 하나의 제약에 기반합니다: Claude의 컨텍스트 윈도우가 빠르게 차고, 차면 성능이 저하됩니다." — 공식 문서

**관리 전략**:
- `/clear`를 자주 사용 (비관련 작업 전환 시)
- `/compact <지시>`로 의도적 압축
- 서브에이전트로 탐색 작업 격리
- 두 번 이상 같은 실수를 교정했다면 → `/clear` + 더 나은 프롬프트로 재시작

### Skills vs CLAUDE.md vs Hooks 선택 기준 `[Confirmed]`

| 목적 | 선택 |
|------|------|
| 예외 없이 매번 실행되어야 함 | **Hooks** (결정론적) |
| 모든 세션에 적용되는 규칙 | **CLAUDE.md** (자문적) |
| 특정 작업에서만 필요한 지식 | **Skills** (온디맨드) |
| 외부 도구/API 연동 | **MCP Servers** |
| 번들 배포 | **Plugins** |

### Agent Skills 오픈 표준 `[Confirmed]`

Claude Code의 Skills는 [agentskills.io](https://agentskills.io) 오픈 표준을 따릅니다. 이는 여러 AI 도구에서 호환되는 스킬을 만들 수 있다는 의미입니다. Claude Code는 여기에 invocation control, subagent execution, dynamic context injection을 추가로 확장합니다.

### 데이터 기반 개선 플라이휠 `[Likely]`

```
에이전트 로그 → 공통 실수 분석 → CLAUDE.md/CLI 개선 → 더 나은 에이전트
    ↑                                                         │
    └─────────────────── 반복 ─────────────────────────────────┘
```

팀 레벨에서 에이전트 로그를 리뷰하여 공통 실수, bash 에러, 미정렬된 엔지니어링 관행을 식별하고 CLAUDE.md에 반영하는 것이 권장됩니다.

---

## Contradictions Found

| 모순 | 출처 A | 출처 B | 해결 |
|------|--------|--------|------|
| Rules frontmatter: `globs` vs `paths` | 일부 프로젝트의 `.claude/rules/` | 공식 문서 | 공식 문서 기준 `paths`가 정확. `globs`는 Cursor 마이그레이션 잔재 가능 |
| Boris: "전문가 페르소나 안티패턴" vs 12개 전문가 에이전트 프로젝트 | Boris Cherny | demiurge 프로젝트 | Boris의 경고는 "성격 부여"에 대한 것이며, 도메인 지식 기반 작업 실행과는 차이가 있음. 다만 과도한 역할 정의는 주의 필요 |

---

## Sources

1. [Claude Code Skills 공식 문서](https://code.claude.com/docs/en/skills) — 공식 문서
2. [Claude Code Memory 공식 문서](https://code.claude.com/docs/en/memory) — 공식 문서
3. [Claude Code Subagents 공식 문서](https://code.claude.com/docs/en/sub-agents) — 공식 문서
4. [Claude Code Best Practices 공식 문서](https://code.claude.com/docs/en/best-practices) — 공식 문서
5. [How Boris Cherny Uses Claude Code](https://paddo.dev/blog/how-boris-uses-claude-code/) — 1차 자료
6. [Boris Cherny Claude Code Creator 22 Tips](https://medium.com/@joe.njenga/boris-cherny-claude-code-creator-shares-these-22-tips-youre-probably-using-it-wrong-1b570aedefbe) — 기술 블로그
7. [Inside Claude Code: 13 Expert Techniques](https://medium.com/@tentenco/inside-claude-code-13-expert-techniques-from-its-creator-boris-cherny-d03695fa85b1) — 기술 블로그
8. [Boris Cherny Threads 원문](https://www.threads.com/@boris_cherny/post/DUMZr4VElyb/) — 1차 자료
9. [정규봉 Claude Code Mastering](https://revfactory.github.io/claude-code-mastering/) — 커뮤니티 (320p)
10. [GitHub: revfactory/claude-code-mastering](https://github.com/revfactory/claude-code-mastering) — 커뮤니티
11. [Claude Code Customization Guide](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/) — 기술 블로그
12. [Understanding Claude Code: Skills vs Commands vs Subagents vs Plugins](https://www.youngleaders.tech/p/claude-skills-commands-subagents-plugins) — 기술 블로그
13. [The Complete Guide to CLAUDE.md](https://www.builder.io/blog/claude-md-guide) — 기술 블로그
14. [Claude Code Path-Specific Rules](https://paddo.dev/blog/claude-rules-path-specific-native/) — 기술 블로그
15. [VentureBeat: Claude Code Creator Workflow](https://venturebeat.com/technology/the-creator-of-claude-code-just-revealed-his-workflow-and-developers-are) — 기술 블로그
16. [InfoQ: Inside Claude Code Creator's Development Workflow](https://www.infoq.com/news/2026/01/claude-code-creator-workflow/) — 기술 블로그

---

## Research Metadata

- 검색 쿼리 수: 7 (일반 6 + SNS 1)
- 수집 출처 수: 16
- 출처 유형 분포: 공식 4, 1차 2, 블로그 8, 커뮤니티 2
- 확신도 분포: Confirmed 38, Likely 4, Uncertain 0, Unverified 0
- WebFetch 상세 조회: 6회 (공식 문서 4, 커뮤니티 1, 블로그 1)
- SNS 출처: Reddit 검색 시도 (직접 결과 부족, 대체 블로그 활용)
- SNS 접근 방법: WebSearch site: operator
