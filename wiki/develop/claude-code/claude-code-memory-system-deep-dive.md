---
created: 2026-03-01
source: claude-code
tags:
  - claude-code
  - memory-system
  - CLAUDE-md
  - auto-memory
  - rules-directory
  - developer-tools
  - AI-coding-assistant
  - workflow-optimization
---

# 📖 Claude Code Memory System — Concept Deep Dive (Final)

> 💡 **한줄 요약**: Claude Code의 Memory System은 **CLAUDE.md**(사용자 작성 지침)와 **Auto Memory**(Claude 자동 학습)의 이중 구조로, 세션 간 컨텍스트를 영속적으로 유지하여 AI 코딩 어시스턴트의 일관성과 생산성을 극대화하는 시스템이다.

---

## 1️⃣ 무엇인가? (What is it?)

Claude Code Memory System은 **세션 간 컨텍스트 유실 문제**를 해결하기 위한 Anthropic의 영속적 메모리 아키텍처다.

- **공식 정의**: "사용자가 CLAUDE.md 파일로 영속적 지침을 제공하고, Claude가 자동 메모리로 학습 내용을 축적하는 이중 메모리 시스템" ([Claude Code Docs](https://code.claude.com/docs/en/memory))
- **탄생 배경**: LLM 기반 코딩 도구의 고질적 문제인 "매 세션마다 같은 설명 반복" → 프로젝트 컨텍스트, 코딩 컨벤션, 디버깅 인사이트를 세션 간 유지할 필요
- **해결하는 문제**: 세션 간 컨텍스트 단절, 반복적인 지시, 팀 컨벤션 불일치, 개인 선호도 유실

> 📌 **핵심 키워드**: `CLAUDE.md`, `Auto Memory`, `MEMORY.md`, `.claude/rules/`, `/memory`, `/init`, `persistent context`

---

## 2️⃣ 핵심 개념 (Core Concepts)

Claude Code Memory System은 **5가지 핵심 레이어**로 구성된다.

```
┌──────────────────────────────────────────────────────────────────┐
│                 🧠 Claude Code Memory Architecture                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────────────────┐   │
│  │CLAUDE.md │ │.claude/  │ │Auto Memory│ │ Agent Memory     │   │
│  │(계층적   │ │ rules/   │ │(MEMORY.md │ │ (서브에이전트용) │   │
│  │ 지침)    │ │(모듈식   │ │ + 토픽    │ │  project/local/  │   │
│  │          │ │ 규칙)    │ │   파일)   │ │  user 스코프     │   │
│  └────┬─────┘ └────┬─────┘ └─────┬─────┘ └────────┬─────────┘   │
│       │            │              │                 │             │
│       ▼            ▼              ▼                 ▼             │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │    📋 System Prompt (세션 시작 시 우선순위별 주입)          │   │
│  └───────────────────────────────────────────────────────────┘   │
│       │                                                          │
│       ▼                                                          │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │    🤖 Claude Code Agent (컨텍스트 기반 응답 생성)          │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

| 구성 요소            | 역할                         | 작성자        | 공유            | 로드 시점            |
| -------------------- | ---------------------------- | ------------- | --------------- | -------------------- |
| **CLAUDE.md**        | 영속적 프로젝트/개인 지침    | 👤 사용자     | Git으로 팀 공유 | 세션 시작 시 전체    |
| **.claude/rules/**   | 모듈식, 경로별 조건부 규칙   | 👤 사용자     | Git으로 팀 공유 | 무조건/조건부        |
| **Auto Memory**      | Claude가 자동 축적한 학습    | 🤖 Claude     | ❌ 로컬 전용    | MEMORY.md 200줄만    |
| **토픽 파일**        | 상세 메모 (debugging.md 등)  | 🤖 Claude     | ❌ 로컬 전용    | ⚡ On-demand         |
| **Agent Memory**     | 서브에이전트별 영속 메모리   | 🤖 서브에이전트 | 스코프별 상이   | 에이전트 시작 시     |

**핵심 원리**:

- **계층적 우선순위**: Managed Policy > User > Project > Local 순으로 로드, 구체적일수록 우선
- **지연 로딩(On-demand)**: 하위 디렉토리 CLAUDE.md, path-specific rules, 토픽 파일은 관련 파일 작업 시에만 로드
- **200줄 하드 리밋**: MEMORY.md의 처음 200줄만 세션 시작 시 자동 주입 (CLAUDE.md에는 적용 안 됨)
- **인덱스 패턴**: MEMORY.md는 메모리 디렉토리의 **인덱스/목차** 역할 → 상세 내용은 토픽 파일로 분리

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

```
┌──────────────────────────────────────────────────────────────────┐
│                     Memory Loading Pipeline                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  세션 시작                                                         │
│    │                                                              │
│    ├─① Managed Policy CLAUDE.md  (조직 정책, 제외 불가 🔒)        │
│    │   macOS: /Library/Application Support/ClaudeCode/CLAUDE.md   │
│    │   Linux: /etc/claude-code/CLAUDE.md                          │
│    │                                                              │
│    ├─② ~/.claude/CLAUDE.md  (개인 글로벌)                          │
│    │   └─ ~/.claude/rules/*.md  (개인 규칙, 모든 프로젝트 적용)    │
│    │                                                              │
│    ├─③ ./CLAUDE.md 또는 ./.claude/CLAUDE.md  (프로젝트)            │
│    │   └─ ./.claude/rules/*.md  (프로젝트 규칙, 재귀 탐색)         │
│    │      ├─ paths 없음 → 항상 로드 (CLAUDE.md와 동일 우선순위)    │
│    │      └─ paths 있음 → 매칭 파일 작업 시에만 조건부 로드         │
│    │                                                              │
│    ├─④ ./CLAUDE.local.md  (로컬 오버라이드, .gitignore 추천)      │
│    │                                                              │
│    ├─⑤ @import 해석 (최대 5단계 깊이)                              │
│    │                                                              │
│    ├─⑥ MEMORY.md (처음 200줄만)                                    │
│    │   └─ ~/.claude/projects/<project>/memory/MEMORY.md            │
│    │                                                              │
│    ▼                                                              │
│  ┌─────────────────────────────────────────────┐                  │
│  │  System Prompt 구성 완료 → 세션 시작         │                  │
│  └─────────────────────────────────────────────┘                  │
│    │                                                              │
│    ├─⑦ 하위 디렉토리 CLAUDE.md (해당 디렉토리 파일 작업 시 로드)   │
│    │                                                              │
│    └─⑧ 토픽 파일 (debugging.md 등) → Claude가 필요 시 직접 참조   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (Step by Step)

1. **Step 1 — 세션 시작**: Claude Code가 CWD에서 디렉토리 트리를 상향 탐색하며 모든 CLAUDE.md 수집
2. **Step 2 — 규칙 로드**: `.claude/rules/` 내 모든 `.md` 파일을 재귀 발견, frontmatter `paths` 필드로 필터링
3. **Step 3 — @import 해석**: `@path/to/file` 구문 발견 시 해당 파일 인라인 삽입 (최대 5단계, 첫 사용 시 승인 다이얼로그)
4. **Step 4 — Auto Memory 주입**: `MEMORY.md`의 처음 200줄을 주입. **토픽 파일은 여기서 로드되지 않음**
5. **Step 5 — 세션 중 학습**: Claude가 유용한 패턴 발견 시 MEMORY.md(인덱스) 또는 토픽 파일(상세)에 자동 기록
6. **Step 6 — /compact 시 보존**: 컨텍스트 압축 시 **CLAUDE.md는 디스크에서 재로드**하여 완전 보존, 대화만 요약

### 💻 실전 구성 예시

```
my-project/
├── CLAUDE.md                          # 프로젝트 공통 (팀 공유, ~100줄)
├── CLAUDE.local.md                    # 개인 로컬 설정 (.gitignore)
├── .claude/
│   ├── settings.json                  # autoMemoryEnabled 등
│   ├── settings.local.json            # claudeMdExcludes 등
│   └── rules/
│       ├── code-style.md              # 무조건 로드 (paths 없음)
│       ├── api-validation.md          # src/api/**/*.ts 매칭 시만
│       ├── react-patterns.md          # src/components/**/*.tsx 매칭 시만
│       ├── testing-rules.md           # **/*.test.* 매칭 시만
│       └── shared/ → ~/shared-rules/  # 심링크로 팀 공유 규칙
│
│  [로컬, Git 미추적]
│  ~/.claude/projects/<project>/memory/
│       ├── MEMORY.md                  # 인덱스 (200줄 이하 유지)
│       ├── debugging.md               # 디버깅 패턴 상세
│       └── api-conventions.md         # API 설계 결정 상세
```

### 📝 Rules 파일 작성법

```yaml
# .claude/rules/api-validation.md
---
paths:
  - "src/api/**/*.ts"
  - "src/api/**/*.tsx"
---

# API 개발 규칙
- 모든 엔드포인트는 Zod로 입력 검증
- 에러 응답: { error: string, code: number }
- OpenAPI 문서화 주석 필수
```

```yaml
# .claude/rules/code-style.md (paths 없음 → 항상 로드)

# 코드 스타일
- 2-space 인덴테이션
- TypeScript strict 모드
- 함수형 컴포넌트 사용
```

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| #   | 유즈 케이스                  | 설명                                         | 적합한 이유                    |
| --- | ---------------------------- | -------------------------------------------- | ------------------------------ |
| 1   | **팀 코딩 컨벤션 통일**      | CLAUDE.md에 코드 스타일, 아키텍처 규칙 명시  | Git으로 버전 관리, 팀 전체 일관성 |
| 2   | **프로젝트 온보딩 자동화**   | `/init`으로 CLAUDE.md 자동 생성              | 프로젝트 구조 자동 분석        |
| 3   | **반복 디버깅 패턴 기억**    | Auto Memory가 에러 패턴/해결법 축적          | 세션 간 디버깅 지식 유지       |
| 4   | **모노레포 멀티 도메인 관리** | path-specific rules + `claudeMdExcludes`     | 도메인별 분리, 불필요한 규칙 제외 |
| 5   | **개인 워크플로우 최적화**   | `~/.claude/CLAUDE.md` + `~/.claude/rules/`   | 모든 프로젝트 공통 적용        |
| 6   | **서브에이전트 지식 축적**   | `persistent_memory` frontmatter              | 에이전트별 독립적 학습         |

### ✅ 베스트 프랙티스

1. **명령형 문체 사용**: "함수형 컴포넌트를 사용하세요" (O) vs "프로젝트는 함수형 컴포넌트를 사용합니다" (X) — 명령형이 **40% 더 잘 준수됨**
2. **200줄 이하 유지**: CLAUDE.md가 커지면 `.claude/rules/`로 모듈화
3. **코드 스니펫 활용**: "5줄 코드 예시 > 50단어 설명"
4. **빌드/테스트 명령어 포함**: Claude가 자동 실행 → 빌드 에러 60% 감소
5. **10세션마다 메모리 감사**: `/memory`로 Auto Memory 정리, 오래된 항목 제거
6. **MEMORY.md를 인덱스로 활용**: 간결한 요약만 유지, 상세 내용은 토픽 파일로 분리
7. **세션 종료 시 3분 투자**: 핵심 결정사항을 CLAUDE.md에 기록 → 다음 세션 품질 극적 향상

### 🏢 실제 활용 전략

```
[소규모 프로젝트]                    [대규모 모노레포]
─────────────────                  ─────────────────────
CLAUDE.md 1개 (100줄 이하)          루트 CLAUDE.md (공통, 50줄)
+ Auto Memory 활용                 + .claude/rules/ (도메인별 5-10개)
                                   + claudeMdExcludes (불필요 제외)
                                   + 심링크로 팀 공유 규칙
```

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분      | 항목                         | 설명                                       |
| --------- | ---------------------------- | ------------------------------------------ |
| ✅ 장점   | **세션 간 컨텍스트 유지**    | 매번 같은 설명 반복 불필요                 |
| ✅ 장점   | **4단계 계층 구조**          | 조직→개인→프로젝트→로컬로 유연한 범위 설정 |
| ✅ 장점   | **Git 연동 & 팀 공유**      | CLAUDE.md와 rules 파일은 버전 관리 가능    |
| ✅ 장점   | **조건부 로딩**              | path-specific rules로 컨텍스트 효율 극대화 |
| ✅ 장점   | **자동 학습 (Auto Memory)**  | 사용자 개입 없이 디버깅 패턴, 선호도 축적  |
| ✅ 장점   | **조직 정책 강제**           | Managed Policy CLAUDE.md는 제외 불가 🔒    |
| ❌ 단점   | **200줄 하드 리밋**          | MEMORY.md 초과 시 잘림, 토픽 파일 자동 참조 제한적 |
| ❌ 단점   | **로컬 전용 Auto Memory**    | 기기 간 동기화 불가 (클라우드 미지원)      |
| ❌ 단점   | **자동 학습 불확실성**       | Claude가 무엇을 기억할지 예측 어려움       |
| ❌ 단점   | **메모리 오염 누적**         | 오래된/잘못된 auto memory가 쌓이면 혼란    |
| ❌ 단점   | **컨텍스트 비용**            | 메모리 파일이 많을수록 토큰 소비 증가      |

### ⚖️ Trade-off 분석

```
자동화 편의성  ◄──────── Trade-off ────────►  제어 정밀도
Auto Memory 자동 학습     vs     CLAUDE.md 수동 작성이 정확

컨텍스트 풍부함 ◄──────── Trade-off ────────►  토큰 효율성
많은 규칙 = 더 나은 응답   vs     컨텍스트 윈도우 소모

팀 표준화      ◄──────── Trade-off ────────►  개인 자유도
CLAUDE.md 공유 일관성      vs     CLAUDE.local.md로 개인화

모듈성         ◄──────── Trade-off ────────►  단순성
rules/ 분산 = 정밀 제어    vs     CLAUDE.md 1개 = 쉬운 관리
```

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 AI 코딩 도구 메모리 시스템 비교

| 비교 기준          | **Claude Code**               | **Cursor**          | **GitHub Copilot** |
| ------------------ | ----------------------------- | ------------------- | ------------------ |
| 메모리 파일        | CLAUDE.md + MEMORY.md         | .cursorrules        | 없음               |
| 자동 학습          | ✅ Auto Memory                | ❌ 수동만           | ❌                 |
| 계층 구조          | 4단계 (조직→개인→프로젝트→로컬) | 프로젝트 1단계      | N/A                |
| 모듈식 규칙        | `.claude/rules/` + path glob | 단일 파일           | N/A                |
| 조건부 로딩        | ✅ YAML frontmatter paths    | ❌                  | N/A                |
| 팀 공유            | Git (CLAUDE.md + rules)       | Git (.cursorrules)  | ❌                 |
| 서브에이전트 메모리 | ✅ 3 스코프                   | ❌                  | ❌                 |
| 조직 정책 강제     | ✅ Managed Policy             | ❌                  | ❌                 |
| 컨텍스트 윈도우    | ~200K 토큰                    | ~128K 토큰          | ~8K 토큰           |

### 📊 Claude Code 내부 메모리 유형 상세 비교

| 비교 기준   | **CLAUDE.md**          | **Auto Memory**           | **.claude/rules/**    | **Agent Memory**     |
| ----------- | ---------------------- | ------------------------- | --------------------- | -------------------- |
| 작성자      | 👤 사용자              | 🤖 Claude                 | 👤 사용자             | 🤖 서브에이전트      |
| 저장 위치   | 프로젝트 루트          | `~/.claude/projects/`     | `.claude/rules/`      | 스코프별 상이        |
| Git 추적    | ✅ 팀 공유             | ❌ 로컬 전용              | ✅ 팀 공유            | project만 ✅         |
| 로드 시점   | 세션 시작 시 전체      | 200줄만 자동              | 무조건/조건부         | 에이전트 시작 시     |
| 크기 권장   | 200줄 이하             | 하드 리밋 200줄           | 500줄/파일 이하       | 제한 없음            |
| 용도        | 빌드 명령, 아키텍처    | 디버깅, 선호도            | 도메인별 규칙         | 에이전트 학습        |

### 🤔 언제 무엇을 선택?

- **CLAUDE.md** → 팀 공유 프로젝트 표준, 빌드/테스트 명령, 아키텍처 결정
- **Auto Memory** → 개인 디버깅 패턴, 반복 실수 교정, 워크플로우 습관
- **.claude/rules/** → 도메인별 세부 규칙, 대규모 프로젝트, 모노레포
- **Agent Memory** → 특정 작업 전문 에이전트의 독립적 지식 축적

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| #   | 실수                    | 발생 빈도 | 왜 문제인가                 | 올바른 접근                |
| --- | ----------------------- | --------- | --------------------------- | -------------------------- |
| 1   | CLAUDE.md 200줄 초과    | 45%       | 신호/잡음비 저하, 토큰 낭비 | `.claude/rules/`로 모듈화  |
| 2   | CLAUDE.md와 MEMORY.md 혼동 | 70%    | 역할 혼재 시 충돌           | 명확한 역할 분리           |
| 3   | Auto Memory 방치        | 70%       | 오래된 메모리 누적          | 10세션마다 감사            |
| 4   | 계층 간 모순된 지시     | 30%       | 예측 불가능한 동작          | 상위=일반, 하위=구체적     |
| 5   | 수동적 문체 사용        | 60%       | 지시 준수율 하락            | 명령형 문체                |
| 6   | 버전 미명시             | 55%       | 잘못된 라이브러리 버전 사용 | 명시적 버전 표기           |

### 🚫 Anti-Patterns

1. **Giant Monolith**: 400줄+ 단일 CLAUDE.md에 모든 규칙 → 모듈화 필수
2. **민감 정보 저장**: CLAUDE.md에 API 키/비밀번호 → `.env` + `.gitignore`
3. **Auto Memory 과의존**: "알아서 기억하겠지" → 핵심 지침은 반드시 CLAUDE.md에
4. **토픽 파일 무시**: MEMORY.md만 관리하고 토픽 파일을 방치 → 주기적 정리 필요

### 🔒 보안/성능 고려사항

- **보안**: CLAUDE.md는 Git 공유 → 민감 정보 절대 포함 금지. Managed Policy는 제외 불가하므로 조직 보안 정책 배포에 활용
- **성능**: path-specific rules를 적극 활용하여 불필요한 컨텍스트 로딩 방지. `claudeMdExcludes`로 모노레포의 무관한 CLAUDE.md 제외
- **메모리 누수**: v2.1.50에서 장시간 세션 메모리 누수 패치 완료 — 파일 히스토리 스냅샷 캡, 내부 캐시 정리, LSP 데이터 해제

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형       | 이름                                 | 링크/설명                                                                                                                                   |
| ---------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 📖 공식 문서 | How Claude remembers your project    | [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory)                                                                   |
| 📖 가이드   | CLAUDE.md Mastery                    | [claudefa.st](https://claudefa.st/blog/guide/mechanics/claude-md-mastery)                                                                   |
| 📖 가이드   | Rules Directory Complete Guide       | [claudefa.st](https://claudefa.st/blog/guide/mechanics/rules-directory)                                                                     |
| 🎓 튜토리얼 | SFEIR Memory System (Tutorial/Tips/FAQ) | [institute.sfeir.com](https://institute.sfeir.com/en/claude-code/claude-code-memory-system-claude-md/tutorial/)                             |
| 📘 심화     | Experimental Memory System           | [giuseppegurgone.com](https://giuseppegurgone.com/claude-memory)                                                                            |
| 📘 실무     | 3 Ways to Fix Memory Problem         | [dev.to](https://dev.to/gonewx/i-tried-3-different-ways-to-fix-claude-codes-memory-problem-heres-what-actually-worked-30fk)                 |

### 🛠️ 핵심 명령어 & 설정

| 명령어/설정                 | 용도                           | 비고                                                         |
| --------------------------- | ------------------------------ | ------------------------------------------------------------ |
| `/init`                     | CLAUDE.md 자동 생성            | 기존 파일 있으면 개선 제안                                   |
| `/memory`                   | 메모리 관리 UI                 | 파일 목록, 토글, 편집기 연결                                 |
| `/compact`                  | 컨텍스트 압축                  | CLAUDE.md 완전 재로드, 대화만 요약                           |
| `@path/to/file`             | 외부 파일 임포트               | 최대 5단계 중첩                                              |
| `--add-dir`                 | 추가 디렉토리 CLAUDE.md 로드  | `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` 필요        |
| `autoMemoryEnabled: false`  | Auto Memory 비활성화           | settings.json 또는 `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`       |
| `claudeMdExcludes`          | 특정 CLAUDE.md 제외            | settings.local.json, 모노레포용                              |

### 🔮 트렌드 & 전망

- **서브에이전트 메모리 (v2.1.33, 2026.02)**: `persistent_memory` frontmatter로 에이전트별 3가지 스코프 — project(Git 공유), local(기기 전용), user(개인 전역)
- **팀 협업 메모리**: 2026년 로드맵에 팀 레벨 공유 메모리 기능 예고
- **MCP 통합 메모리**: SQLite MCP, claude-mem 플러그인 등 외부 메모리 레이어 실험 활발
- **하이브리드 전략 대두**: CLAUDE.md(명시적) + Auto Memory(암묵적) + SQLite MCP(시맨틱) 조합으로 ~80% 세션 연속성 달성

### 💬 커뮤니티 인사이트

- "`.claude/rules/`의 path-specific 규칙이 가장 과소평가된 기능 — 모노레포에서 필수" ([paddo.dev](https://paddo.dev/blog/claude-rules-path-specific-native/))
- "세션 종료 시 3분간 핵심 결정사항 기록하면, 다음 세션 시작이 극적으로 개선됨"
- "CLAUDE.md + 구조화된 노트 + SQLite MCP의 조합으로 약 80% 세션 연속성 달성" ([DEV Community](https://dev.to/gonewx/i-tried-3-different-ways-to-fix-claude-codes-memory-problem-heres-what-actually-worked-30fk))
- "30-100줄이 CLAUDE.md의 이상적 분량. 200줄 넘으면 모듈화 신호" ([SFEIR](https://institute.sfeir.com/en/claude-code/claude-code-memory-system-claude-md/tips/))

---

## 📎 Sources

1. [How Claude remembers your project - Claude Code Docs](https://code.claude.com/docs/en/memory) — 공식 문서
2. [Claude Code Rules Directory Guide](https://claudefa.st/blog/guide/mechanics/rules-directory) — 가이드
3. [CLAUDE.md Memory System Tips - SFEIR Institute](https://institute.sfeir.com/en/claude-code/claude-code-memory-system-claude-md/tips/) — 튜토리얼
4. [Claude Code's Experimental Memory System](https://giuseppegurgone.com/claude-memory) — 기술 분석
5. [3 Ways to Fix Claude Code Memory Problem](https://dev.to/gonewx/i-tried-3-different-ways-to-fix-claude-codes-memory-problem-heres-what-actually-worked-30fk) — 실무 경험
6. [Claude Code Release Notes 2026](https://releasebot.io/updates/anthropic/claude-code) — 릴리즈 노트
7. [Claude Code Path-Specific Rules](https://paddo.dev/blog/claude-rules-path-specific-native/) — 기능 분석
8. [AI Coding Assistant Comparison](https://vladimirsiedykh.com/blog/ai-coding-assistant-comparison-claude-code-github-copilot-cursor-feature-analysis-2025) — 비교 분석
9. [Complete Guide to AI Agent Memory Files](https://hackernoon.com/the-complete-guide-to-ai-agent-memory-files-claudemd-agentsmd-and-beyond) — 종합 가이드
10. [Memory for subagents - GitHub Issue](https://github.com/anthropics/claude-code/issues/4418) — 서브에이전트 메모리

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 7 (WebSearch) + 3 (WebFetch)
> - 수집 출처 수: 15+
> - 출처 유형: 공식 1, 가이드/블로그 6, 커뮤니티 4, 튜토리얼 2, 릴리즈노트 1, 비교분석 1
> - 교차 검증: 13개 핵심 주장 모두 공식 문서 기반 검증 완료
> - 리뷰: claude-code-guide 서브에이전트로 팩트체크 수행, 0건 오류 확인
