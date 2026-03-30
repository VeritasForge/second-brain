---
created: 2026-03-30
source: claude-code
tags: [agent-skills, claude-code, cross-platform, plugin, open-standard, deep-research]
---

# Agent Skills 오픈 표준과 Claude Code 플러그인 시스템

## 1. 배경: 내 환경의 스킬/플러그인 설치 현황

직접 작성한 것을 제외하면 두 가지 경로로 관리되고 있다.

| 관리 방식                                | 설치 도구        | 항목                                                                                       |
| ---------------------------------------- | ---------------- | ------------------------------------------------------------------------------------------ |
| **Claude Code Plugins** (마켓플레이스)   | `/plugin`        | CE, superpowers, ralph-loop, ouroboros, context7, Notion                                    |
| **Agent Skills** (오픈 표준)             | `npx skills add` | vercel-react-best-practices, vercel-composition-patterns, vercel-react-native-skills, web-design-guidelines |

---

## 2. Agent Skills란?

### 한줄 요약

**Anthropic이 만든 스펙** + **Vercel이 만든 패키지 매니저** = AI 코딩 에이전트를 위한 범용 스킬 포맷 표준

비유하면, 요리할 때마다 레시피를 처음부터 설명하는 대신(긴 프롬프트), 레시피를 한 번 써서 선반에 올려두면(SKILL.md), 주방의 어떤 요리사든(Claude, Cursor, Codex...) 그 레시피를 꺼내 쓸 수 있는 구조다.

### 스킬 포맷

스킬은 SKILL.md 파일을 포함하는 디렉토리다:

```
skill-name/
  SKILL.md          # YAML frontmatter + Markdown 지시사항
  scripts/          # 선택: 실행 가능한 스크립트
  references/       # 선택: 참조 문서
  assets/           # 선택: 템플릿, 스키마 등
```

SKILL.md 구조:

```markdown
---
name: pdf-processing
description: Extract PDF text, fill forms, merge files.
---

# PDF Processing
## 지시사항
...
```

### 지원 플랫폼 (33개)

Claude Code, Cursor, GitHub Copilot, VS Code, OpenAI Codex, Google Gemini CLI, Windsurf/Kiro, JetBrains Junie, Goose, Amp, Roo Code, Databricks, Snowflake 등

### CLI 명령어

```bash
npx skills add vercel-labs/agent-skills   # 설치
npx skills check                          # 업데이트 확인
npx skills update                         # 업데이트 실행
npx skills list                           # 설치된 스킬 목록
npx skills remove <name>                  # 제거
```

### 설치 아키텍처

```
GitHub repo (vercel-labs/agent-skills)
    ↓ clone & copy
~/.agents/skills/vercel-*          ← 실제 파일 저장 (canonical)
    ↓ symlink
~/.claude/skills/vercel-*          ← Claude Code가 읽는 위치
```

- `~/.agents/skills/` = 단일 진실 소스 (물리 파일)
- `~/.claude/skills/` = 상대 symlink (`../../.agents/skills/...`)
- `.skill-lock.json` = Git tree SHA로 버전 추적
- **자동 업데이트: 없음** — cron, hook, 백그라운드 프로세스 없이 완전 수동 (`npx skills update`)

---

## 3. Agent Skills vs Claude Code Plugins 비교

| 항목               | Agent Skills                          | Claude Code Plugins                                        |
| ------------------ | ------------------------------------- | ---------------------------------------------------------- |
| **비유**           | MP3 포맷 (범용 음악 파일)             | iTunes (전용 앱스토어)                                     |
| **만든 곳**        | Anthropic (스펙) + Vercel (CLI)       | Anthropic                                                  |
| **호환 범위**      | 33개 에이전트 플랫폼                  | Claude Code 전용                                           |
| **설치 방법**      | `npx skills add`                      | `/plugin install`                                          |
| **저장 위치**      | `~/.agents/skills/`                   | `~/.claude/plugins/`                                       |
| **포함 가능 항목** | SKILL.md + scripts + references       | Skills + **Agents + Hooks + MCP서버 + LSP서버**            |
| **마켓플레이스**   | GitHub repo (any git host)            | 전용 marketplace.json                                      |
| **자동 업데이트**  | 없음 (수동)                           | 공식은 자동, 서드파티는 opt-in                             |

### 관계: 경쟁이 아니라 보완

```
Claude Code Plugin (예: compound-engineering)
├── skills/          ← Agent Skills 포맷의 SKILL.md 들
├── agents/          ← Claude Code 전용 서브에이전트
├── hooks/           ← Claude Code 전용 훅
└── .mcp.json        ← Claude Code 전용 MCP 서버
```

Plugin은 Agent Skills 포맷을 **포함**할 수 있다:

- **범용 스킬**은 Agent Skills로 만들면 → 모든 에이전트에서 사용 가능
- **Claude 전용 기능**(MCP, 훅, 에이전트)이 필요하면 → Plugin으로 번들링

Claude Code 공식 문서에서도 이를 명시한다:

> "Claude Code skills follow the **Agent Skills** open standard, which works across multiple AI tools. Claude Code **extends** the standard with additional features."

---

## 4. 크로스 플랫폼 호환성: 실제로 어디까지 호환되는가?

### 공통 스펙 (3개 플랫폼에서 확인)

| 필드                                          | Claude Code | Codex | Gemini CLI |
| --------------------------------------------- | ----------- | ----- | ---------- |
| `name`                                        | ✅          | ✅    | ✅         |
| `description`                                 | ✅          | ✅    | ✅         |
| `license`, `compatibility`, `metadata`        | ✅          | ✅    | ✅         |
| SKILL.md + Markdown body                      | ✅          | ✅    | ✅         |
| Progressive disclosure                        | ✅          | ✅    | ✅         |
| `scripts/`, `references/`, `assets/`          | ✅          | ✅    | ✅         |

### 플랫폼 전용 확장 필드 (다른 플랫폼에서는 무시됨)

| 확장 필드                                     | Claude Code           | Codex | Gemini CLI |
| --------------------------------------------- | --------------------- | ----- | ---------- |
| `allowed-tools`                               | ✅ (스펙에서 Experimental) | ❓    | ❓         |
| `disable-model-invocation`                    | ✅ Claude 전용        | ❌    | ❌         |
| `user-invocable`                              | ✅ Claude 전용        | ❌    | ❌         |
| `context: fork` (서브에이전트)                | ✅ Claude 전용        | ❌    | ❌         |
| `model`, `effort`, `hooks`, `paths`, `shell`  | ✅ Claude 전용        | ❌    | ❌         |
| `` !`command` `` 동적 주입                    | ✅ Claude 전용        | ❌    | ❌         |

비유하면, **HTML은 어떤 브라우저에서든 렌더링되지만, `-webkit-` prefix CSS는 Chrome에서만 동작하는 것**과 같다.

---

## 5. 수렴 검증 결과: 수정이 필요한 부분

3개 검증 에이전트(claude-code-guide, contrarian, best-practices-researcher)로 Tier 3 심층 검증을 수행한 결과, 원래 리서치의 **방향은 맞으나 표현 수정이 필요**한 것으로 판정되었다.

### 수정된 표현 4가지

| 원래 표현                              | 수정 표현                                  | 이유                                                                       |
| -------------------------------------- | ------------------------------------------ | -------------------------------------------------------------------------- |
| "동일하게 **동작**한다"                | "동일하게 **파싱**된다"                    | 파싱과 실행은 다른 수준. 본문 내 플랫폼 특화 도구 지시는 타 플랫폼에서 실행 불가 |
| "**de facto standard**"               | "**수렴 중인 공통 포맷**"                  | 33개 플랫폼 나열은 사실이나 구현 깊이가 상이                               |
| "확장 필드는 **무시된다**"             | "**무시될 것으로 추론**"                   | 실증 테스트 근거 없음. silent failure가 에러보다 위험할 수 있음             |
| "필수 필드: name, description"         | "**스펙에서는 필수, Claude Code에서는 선택**" | 스펙과 구현이 이미 다름                                                    |

### 호환성 5단계 모델 (CONTRARIAN이 제안)

| Level | 의미                                                       | 호환 여부                                              |
| ----- | ---------------------------------------------------------- | ------------------------------------------------------ |
| 0     | .md 파일 읽기                                              | 모든 플랫폼                                            |
| 1     | YAML frontmatter 파싱                                      | 대부분 플랫폼                                          |
| 2     | 스킬 등록/검색/활성화                                      | 주요 플랫폼 (Claude, Codex, Gemini, Cursor 등)         |
| 3     | 본문 지시사항 실행                                         | 플랫폼별 도구 차이로 제한적                            |
| 4     | 확장 필드 동작 (allowed-tools, context:fork 등)            | 플랫폼 전용                                            |

### 유지되는 결론

- Agent Skills는 Anthropic이 제안하고 33개 플랫폼이 채택한 **가장 유력한 공통 포맷**
- 레거시 포맷(.cursorrules, .windsurfrules)에서 Agent Skills로 **수렴 중**인 추세 (Cursor는 `/migrate-to-skills` 마이그레이션 도구까지 제공)
- **경쟁 표준이 없음** — 이것이 공통 포맷으로서 가장 강력한 근거
- `allowed-tools`는 agentskills.io 스펙에서 **Experimental**, Claude Code에서는 정식 지원
- OpenAI Codex의 Agent Skills 지원은 현재 **experimental** 상태 (stable 전환 발표 없음)

### CONTRARIAN의 핵심 통찰

> 크로스 플랫폼 호환성 추구보다 **해당 플랫폼에서 최대한 효과적인 스킬을 만드는 것**이 더 실용적일 수 있다. "모든 IDE에서 동일하게 동작하는 플러그인을 만들자"는 것처럼, 이론적으로는 매력적이지만 실용적으로는 **최소공배수 함정(lowest common denominator trap)**에 빠진다.

---

## 6. 핵심 정리

1. **Agent Skills**는 Anthropic이 만든 스펙 + Vercel이 만든 CLI로, SKILL.md라는 공통 포맷을 33개 AI 코딩 에이전트에서 사용할 수 있게 한다
2. **Claude Code Plugins**는 Claude Code 전용 앱스토어로, Skills에 더해 MCP서버, 훅, 서브에이전트까지 번들링할 수 있다
3. 두 시스템은 **경쟁이 아니라 보완** 관계 — Plugin이 Agent Skills 포맷을 포함할 수 있다
4. 크로스 플랫폼 호환성은 **파싱 수준(Level 0-2)에서는 호환**, 실행 수준(Level 3-4)에서는 **플랫폼마다 다르다**
5. "de facto standard"보다는 "**수렴 중인 공통 포맷**"이 정확한 표현이다 — 레거시 포맷에서 이동 중이지만 구현 깊이는 상이
6. 실용적 조언: **범용 지식/가이드**는 Agent Skills로, **플랫폼 특화 자동화**(MCP, 훅, 에이전트)는 Claude Code Plugin으로 만드는 것이 최적
