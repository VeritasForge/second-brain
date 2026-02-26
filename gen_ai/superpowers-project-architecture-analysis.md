---
created: 2026-02-09
source: claude-code
tags:
  - project-analysis
  - ai-agent
  - claude-code
  - skills
---

# Superpowers 프로젝트 분석 리포트

## 1. 프로젝트 개요

**Superpowers**는 AI 코딩 에이전트(Claude Code, Codex, OpenCode)에게 **체계적인 소프트웨어 개발 워크플로우**를 부여하는 "스킬(Skills) 시스템"입니다. Jesse Vincent이 개발했으며, MIT 라이선스로 배포됩니다 (v4.2.0).

**핵심 목적:** AI 코딩 에이전트가 코드를 바로 작성하지 않고, **설계 → 계획 → TDD 기반 구현 → 코드 리뷰 → 검증**이라는 규율 있는 개발 프로세스를 따르도록 강제하는 것입니다.

---

## 2. 프로젝트 구조

```
superpowers/
├── .claude-plugin/          # Claude Code 플러그인 메타데이터
│   ├── plugin.json          # 플러그인 정보 (이름, 버전, 작성자)
│   └── marketplace.json     # 마켓플레이스 등록 정보
├── .codex/                  # Codex용 설치 가이드
│   └── INSTALL.md
├── .opencode/               # OpenCode용 플러그인
│   ├── INSTALL.md
│   └── plugins/superpowers.js  # OpenCode 시스템 프롬프트 변환 플러그인
├── hooks/                   # 세션 시작 시 실행되는 훅
│   ├── hooks.json           # 훅 설정 (SessionStart 이벤트)
│   ├── session-start.sh     # using-superpowers 스킬을 시스템 프롬프트에 주입
│   └── run-hook.cmd         # Windows 호환 훅 실행기
├── lib/
│   └── skills-core.js       # 스킬 발견/해석 핵심 라이브러리 (ESM)
├── skills/                  # 14개의 스킬 디렉토리 (핵심 자산)
│   ├── using-superpowers/   # 메타 스킬: 전체 스킬 시스템 사용법
│   ├── brainstorming/       # 아이디어 → 설계 문서 변환
│   ├── writing-plans/       # 설계 → 세분화된 구현 계획 작성
│   ├── executing-plans/     # 배치 방식 계획 실행
│   ├── subagent-driven-development/  # 서브에이전트 기반 개발 (핵심)
│   │   ├── SKILL.md
│   │   ├── implementer-prompt.md       # 구현자 서브에이전트 프롬프트
│   │   ├── spec-reviewer-prompt.md     # 스펙 준수 리뷰어 프롬프트
│   │   └── code-quality-reviewer-prompt.md  # 코드 품질 리뷰어 프롬프트
│   ├── test-driven-development/       # TDD 강제 스킬
│   │   ├── SKILL.md
│   │   └── testing-anti-patterns.md   # 테스팅 안티패턴 참조
│   ├── systematic-debugging/          # 체계적 디버깅 4단계
│   │   ├── SKILL.md
│   │   ├── root-cause-tracing.md      # 역방향 원인 추적
│   │   ├── defense-in-depth.md        # 다계층 방어
│   │   ├── condition-based-waiting.md # 조건 기반 대기
│   │   └── find-polluter.sh           # 테스트 오염자 발견 스크립트
│   ├── using-git-worktrees/           # Git worktree 기반 격리 작업
│   ├── finishing-a-development-branch/ # 브랜치 완료/머지/PR/정리
│   ├── requesting-code-review/        # 코드 리뷰 요청
│   ├── receiving-code-review/         # 코드 리뷰 수신/대응
│   ├── dispatching-parallel-agents/   # 병렬 에이전트 디스패칭
│   ├── verification-before-completion/ # 완료 전 검증 강제
│   └── writing-skills/               # 새 스킬 작성 가이드 (메타 스킬)
├── commands/                # 슬래시 커맨드 (스킬 호출 단축)
│   ├── brainstorm.md        # /brainstorm → brainstorming 스킬
│   ├── write-plan.md        # /write-plan → writing-plans 스킬
│   └── execute-plan.md      # /execute-plan → executing-plans 스킬
├── agents/                  # 재사용 에이전트 프롬프트
│   └── code-reviewer.md     # 코드 리뷰어 에이전트 정의
├── tests/                   # 테스트 스위트
│   ├── claude-code/         # Claude Code 환경 테스트
│   ├── explicit-skill-requests/  # 명시적 스킬 호출 테스트
│   ├── skill-triggering/    # 스킬 자동 트리거 테스트
│   ├── subagent-driven-dev/ # SDD 통합 테스트 (Go/Svelte 프로젝트)
│   └── opencode/            # OpenCode 플러그인 테스트
├── docs/                    # 문서
│   ├── plans/               # 기획 문서들
│   ├── README.codex.md
│   ├── README.opencode.md
│   └── testing.md
└── README.md
```

---

## 3. 아키텍처

### 3.1 플러그인 시스템 (3개 플랫폼 지원)

| 플랫폼         | 설치 방식                | 통합 메커니즘                                                    |
| -------------- | ------------------------ | ---------------------------------------------------------------- |
| **Claude Code** | 플러그인 마켓플레이스    | `hooks.json` → `session-start.sh` → 시스템 프롬프트 주입         |
| **Codex**       | Git clone + symlink      | `~/.agents/skills/superpowers` 심링크 → 네이티브 스킬 발견       |
| **OpenCode**    | JS 플러그인              | `superpowers.js` → 시스템 프롬프트 변환 함수                     |

### 3.2 부트스트랩 플로우

```
세션 시작
    ↓
SessionStart 훅 발동
    ↓
session-start.sh 실행
    ↓
using-superpowers/SKILL.md 내용을 JSON으로 래핑
    ↓
<EXTREMELY_IMPORTANT> 태그로 시스템 프롬프트에 주입
    ↓
에이전트는 모든 작업 전에 관련 스킬 확인 필수
```

### 3.3 스킬 시스템 구조

- **스킬 파일:** 각 스킬은 `skills/<skill-name>/SKILL.md` 형태
- **YAML 프론트매터:** `name`과 `description` 두 필드만 지원 (max 1024자)
- **스킬 발견:** `lib/skills-core.js`가 재귀적으로 SKILL.md를 찾아 프론트매터 파싱
- **스킬 우선순위:** 개인 스킬(personal) > Superpowers 스킬 (섀도잉 지원)
- **스킬 호출:** `Skill` 도구를 통해 로드되며, description이 트리거 조건 역할

### 3.4 서브에이전트 아키텍처 (SDD)

가장 핵심적인 실행 엔진인 **Subagent-Driven Development**의 구조:

```
컨트롤러 에이전트 (메인 세션)
    ├── 계획 파일 읽기 → 모든 태스크 추출
    ├── 태스크 N마다:
    │   ├── Implementer 서브에이전트 디스패치 (구현)
    │   │   └── TDD 기반 구현 → 자체 리뷰 → 커밋
    │   ├── Spec Reviewer 서브에이전트 디스패치 (스펙 준수 검증)
    │   │   └── 구현 vs 요구사항 라인별 비교
    │   ├── Code Quality Reviewer 서브에이전트 디스패치 (품질 검증)
    │   │   └── 아키텍처, 패턴, 보안, 성능 검토
    │   └── 문제 발견 시 → Implementer가 수정 → 재검토 반복
    └── 모든 태스크 완료 → 최종 전체 코드 리뷰 → 브랜치 마무리
```

---

## 4. 핵심 기능 분석

### 4.1 개발 워크플로우 스킬 (7단계 파이프라인)

| 단계 | 스킬                                  | 기능                                                                       |
| ---- | ------------------------------------- | -------------------------------------------------------------------------- |
| 1    | **brainstorming**                     | 아이디어를 소크라틱 대화로 발전, 200-300 단어씩 설계 제시, 2-3 접근법 비교  |
| 2    | **using-git-worktrees**               | Git worktree로 격리 작업공간 생성, 자동 프로젝트 셋업, 테스트 기준선 확인   |
| 3    | **writing-plans**                     | 2-5분 단위 bite-sized 태스크로 분해, 정확한 파일 경로/코드/검증 단계 포함   |
| 4a   | **subagent-driven-development**       | 태스크당 신선한 서브에이전트 + 2단계 리뷰 (스펙 → 품질)                     |
| 4b   | **executing-plans**                   | 배치 실행 + 사람 체크포인트 (별도 세션에서 실행)                            |
| 5    | **requesting-code-review**            | 리뷰어 서브에이전트 디스패치, Critical/Important/Minor 분류                  |
| 6    | **finishing-a-development-branch**    | 테스트 확인 → 4가지 옵션(머지/PR/유지/폐기) 제시 → 워크트리 정리           |

### 4.2 개발 규율 스킬

| 스킬                                  | 핵심 원칙                                    | 강제 방식                                                                          |
| ------------------------------------- | -------------------------------------------- | ---------------------------------------------------------------------------------- |
| **test-driven-development**           | "실패하는 테스트 없이 프로덕션 코드 없음"     | RED→GREEN→REFACTOR 사이클 강제, 테스트 전 코드 작성 시 삭제 명령                    |
| **systematic-debugging**              | "근본 원인 조사 없이 수정 없음"               | 4단계 프로세스 (근본원인→패턴→가설→구현), 3회 실패 시 아키텍처 재고                  |
| **verification-before-completion**    | "증거 없이 완료 주장 없음"                    | 검증 명령 실행 + 출력 확인 후에만 성공 주장 허용                                    |

### 4.3 협업 스킬

| 스킬                                  | 기능                                                              |
| ------------------------------------- | ----------------------------------------------------------------- |
| **receiving-code-review**             | 성과주의적 동의("Great point!") 금지, 기술적 검증 후 수용/반론     |
| **dispatching-parallel-agents**       | 독립적 문제에 병렬 에이전트 디스패치                               |

### 4.4 메타 스킬

| 스킬                   | 기능                                                                                        |
| ---------------------- | ------------------------------------------------------------------------------------------- |
| **using-superpowers**  | 스킬 시스템 사용법, "1%라도 해당 가능성 있으면 반드시 스킬 호출" 강제                        |
| **writing-skills**     | 새 스킬 작성 가이드, 스킬 자체를 TDD로 개발 (압력 테스트 → 스킬 작성 → 허점 보완)           |

---

## 5. 설계 철학

### 5.1 핵심 원칙

1. **Test-Driven Development** - 항상 테스트 먼저
2. **체계적 > 즉흥적** - 프로세스가 추측보다 우선
3. **복잡성 축소** - YAGNI (You Aren't Gonna Need It)
4. **증거 > 주장** - 검증 후 선언

### 5.2 독특한 설계 결정

- **"합리화 방지 테이블"**: 각 스킬에 AI가 규칙을 우회하려 할 때 쓰는 변명과 그에 대한 반박을 미리 포함
- **"설명이 아닌 트리거 조건"**: 스킬 설명(description)에 워크플로우를 요약하면 AI가 전체 스킬을 읽지 않고 요약만 따르는 문제 발견 → description에는 "언제 사용하는지"만 기술
- **스킬의 TDD**: 스킬 자체도 "압력 시나리오"로 테스트 - 시간 압박, 매몰 비용, 피로 등의 압력 하에서도 AI가 규칙을 따르는지 검증
- **서브에이전트 컨텍스트 격리**: 태스크마다 새로운 서브에이전트를 사용하여 컨텍스트 오염 방지

---

## 6. 기술 스택

| 요소           | 기술                                                               |
| -------------- | ------------------------------------------------------------------ |
| 스킬 정의      | Markdown + YAML 프론트매터                                          |
| 핵심 라이브러리 | JavaScript (ESM) - `skills-core.js`                                |
| 훅 시스템      | Bash 스크립트 + JSON 설정                                           |
| 플로우차트     | Graphviz DOT 문법 (스킬 내 인라인)                                  |
| 테스트         | Bash 스크립트 기반 통합 테스트                                       |
| 버전 관리      | Git + GitHub                                                        |
| 플랫폼 통합    | Claude Code 플러그인 API, OpenCode JS 플러그인, Codex 심링크        |

---

## 7. 요약

**Superpowers는 "AI 코딩 에이전트를 위한 소프트웨어 개발 방법론 프레임워크"입니다.**

일반적인 AI 코딩 도구가 "코드를 더 빨리 생성"하는 데 집중하는 반면, Superpowers는 **AI가 올바른 프로세스를 따르도록 강제**하는 데 집중합니다. 브레인스토밍에서 시작해 설계 문서 작성, 세분화된 계획 수립, TDD 기반 구현, 2단계 코드 리뷰, 검증 후 완료까지 - 전체 소프트웨어 개발 라이프사이클을 AI 에이전트가 자율적으로 수행하되, 인간이 정한 규율과 품질 기준을 벗어나지 않도록 하는 것이 핵심 가치입니다.
