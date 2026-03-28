---
created: 2026-03-04
source: claude-code
tags:
  - ouroboros
  - compound-engineering
  - superpowers
  - claude-code
  - ai-engineering
  - plugin-comparison
  - workflow
  - document-review
  - mcp-dependency
  - cross-compatibility
---

# Ouroboros vs Compound Engineering vs Superpowers: 심층 비교 분석

---

## 1. 개요 — 세 도구의 정체성

| 항목         | Ouroboros                                         | Compound Engineering                                                                            | Superpowers                                             |
| ---------- | ------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| **한마디 정의** | 자기참조적 요구사항 결정화 엔진                                 | 자율 엔지니어링 워크플로우 파이프라인                                                                            | 체계적 개발 방법론 스킬 프레임워크                                     |
| **리포지토리**  | [Q00/ouroboros](https://github.com/Q00/ouroboros) | [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) | [obra/superpowers](https://github.com/obra/superpowers) |
| **아키텍처**   | Python MCP 서버 (18패키지, 166모듈, EventSourcing)<br>   | Markdown 기반 커맨드+스킬+에이전트 (24 에이전트, 13 커맨드, 11 스킬)                                                | Markdown 기반 스킬 프레임워크 (14 스킬, hook 기반 자동 트리거)            |
| **핵심 철학**  | 진화적 수렴 (Evolutionary Convergence)                 | 자율 워크플로우 자동화 (Autonomous Pipeline)                                                              | 증거 기반 체계적 개발 (Evidence-Based Discipline)                |
| **메타포**    | 우로보로스 (자기를 먹는 뱀 — 매 세대가 자기를 개선)                   | 공장 라인 (brainstorm → plan → deepen → work → review → compound)                                   | 장인 도제 시스템 (스킬을 내재화한 에이전트가 규율을 지키며 개발)                   |

---

## 2. 스킬/커맨드 상세 매핑

### 2.1 Ouroboros 스킬 맵 (12개 스킬 + 12개 MCP 도구)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Ouroboros Workflow                                │
│                                                                     │
│  [welcome/setup/tutorial/help]  ← 온보딩 레이어                      │
│           │                                                         │
│           ▼                                                         │
│  ┌─── interview ───┐    Socratic 질문 → 모호성 점수 ≤ 0.2 게이트    │
│  │  ouroboros_interview MCP                                         │
│  │  ambiguity scoring (가중 평균)                                    │
│  │  greenfield 3축 / brownfield 4축                                 │
│  └────────┬────────┘                                                │
│           ▼                                                         │
│  ┌──── seed ───────┐    인터뷰 → 불변 YAML 스펙 결정화               │
│  │  ouroboros_generate_seed MCP                                     │
│  │  GOAL, CONSTRAINTS, AC, ONTOLOGY,                                │
│  │  EVALUATION_PRINCIPLES, EXIT_CONDITIONS                          │
│  └────────┬────────┘                                                │
│           ▼                                                         │
│  ┌──── run ────────┐    Seed 실행 (Double Diamond 분해)              │
│  │  ouroboros_execute_seed MCP                                      │
│  │  PAL Router (Frugal/Standard/Frontier 자동 선택)                  │
│  └────────┬────────┘                                                │
│           ▼                                                         │
│  ┌── evaluate ─────┐    3단계 검증 파이프라인                        │
│  │  ouroboros_evaluate MCP                                          │
│  │  Stage 1: Mechanical (lint/build/test)                           │
│  │  Stage 2: Semantic (AC 준수, goal 정렬, drift)                    │
│  │  Stage 3: Multi-model Consensus (선택적)                          │
│  └────────┬────────┘                                                │
│           ▼                                                         │
│  ┌── evolve ───────┐    진화 루프 (수렴까지 반복)                     │
│  │  ouroboros_evolve_step MCP                                       │
│  │  Wonder → Reflect → Seed → Execute → Evaluate                   │
│  │  ontology similarity ≥ 0.95 → 수렴                               │
│  │  stagnation detection (3회 동일, 진동, 질문 반복 70%+)            │
│  │  max 30 generations safety cap                                   │
│  │  ouroboros_evolve_rewind → 특정 세대로 되감기                     │
│  └────────┬────────┘                                                │
│           ▼                                                         │
│  ┌── ralph ────────┐    세션 경계를 넘는 영속 루프                    │
│  │  .omc/state/ralph-state.json                                     │
│  │  max 10 iterations, checkpoint 저장                               │
│  └─────────────────┘                                                │
│                                                                     │
│  [status]   ouroboros_measure_drift → drift 측정                     │
│             ouroboros_session_status → 세션 상태                      │
│             ouroboros_lineage_status → 진화 계보                      │
│             ouroboros_ac_dashboard → AC 준수 대시보드                  │
│                                                                     │
│  [unstuck]  ouroboros_lateral_think → 5개 페르소나 횡적사고            │
│             hacker / researcher / simplifier / architect / contrarian│
│                                                                     │
│  [9 Agents] socratic-interviewer, ontologist, seed-architect,       │
│             evaluator, contrarian, hacker, simplifier,              │
│             researcher, architect                                   │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Compound Engineering 스킬 맵 (핵심 워크플로우)

```
┌─────────────────────────────────────────────────────────────────────┐
│                Compound Engineering Pipeline                        │
│                                                                     │
│  /ce:brainstorm                                                     │
│  │  Phase 0: 명확성 평가 (필요 여부 판단)                              │
│  │  Phase 1: 아이디어 이해 (순차적 질문, 다지선다 제시)                  │
│  │  Phase 2: 접근법 탐색 (2-3개 옵션, YAGNI 원칙)                     │
│  │  Phase 3: 설계 캡처 (docs/brainstorms/ 저장)                      │
│  │  Phase 4: 핸드오프 → /ce:plan                                     │
│  │                                                                  │
│  ▼                                                                  │
│  /ce:plan                                                           │
│  │  Phase 1: 입력 + brainstorm 연결 (14일 이내 문서 자동 감지)          │
│  │  Phase 2: 리서치 (repo-research-analyst, learnings-researcher,    │
│  │           best-practices-researcher, framework-docs-researcher)   │
│  │  Phase 3: 계획 구조화 (MINIMAL/MORE/A LOT 3단계 상세도)             │
│  │  Phase 4: SpecFlow Analysis (spec-flow-analyzer 실행)             │
│  │  Phase 5-7: 상세도 선택 + 포매팅 + brainstorm 교차검증              │
│  │  Phase 8: docs/plans/ 저장 (필수)                                 │
│  │  Phase 9: 후속 옵션 (deepen/work/review/issue 생성)               │
│  │                                                                  │
│  ▼                                                                  │
│  /deepen-plan                                                       │
│  │  1. 계획 파싱 → 섹션별 매니페스트                                   │
│  │  2. 스킬 동적 발견 + 매칭 (project/global/plugin 모든 소스)         │
│  │  3. docs/solutions/ 학습 적용 (YAML frontmatter 기반 필터링)       │
│  │  4. 섹션별 Explore 에이전트 리서치 (Context7 + WebSearch)          │
│  │  5. 40+ 리뷰 에이전트 전체 병렬 실행 (필터링 없이)                   │
│  │  6. 종합 + 섹션 강화 (Research/Best Practices/Performance/         │
│  │     Edge Cases/References 추가)                                   │
│  │                                                                  │
│  ▼                                                                  │
│  /ce:work                                                           │
│  │  Phase 1: Quick Start (계획 읽기, 환경 설정, Todo 생성)             │
│  │  Phase 2: Execute (태스크 루프 + unit/integration 테스트)           │
│  │  Phase 3: Quality Check (전체 테스트 + 리뷰어 에이전트)             │
│  │  Phase 4: Ship It (커밋 + PR + 스크린샷)                           │
│  │                                                                  │
│  ▼                                                                  │
│  /ce:review                                                         │
│  │  Phase 1: 타겟 결정 + Git Worktree 설정                           │
│  │  Phase 2: 병렬 에이전트 분석 (native-reviewer + 조건부 전문가)      │
│  │  Phase 3: Ultra-Thinking 심층 분석 (5개 이해관계자 관점)            │
│  │  Phase 4: 발견사항 종합 + Todo 생성 (P1/P2/P3)                     │
│  │                                                                  │
│  ▼                                                                  │
│  /ce:compound                                                       │
│  │  5개 서브에이전트 병렬: Context Analyzer, Solution Extractor,      │
│  │  Related Docs Finder, Prevention Strategist, Category Classifier  │
│  │  → docs/solutions/{category}/{filename}.md 단일 파일 생성          │
│  │                                                                  │
│  ────────────────────────────────────────────────                    │
│  /lfg (전체 자동화)                                                   │
│  plan → deepen-plan → work → review → resolve_todo →                │
│  test-browser → feature-video → DONE                                │
│                                                                     │
│  24 Agents: review/(14), research/(5), design/(3), workflow/(2)     │
└─────────────────────────────────────────────────────────────────────┘
```

#### CE 스킬 심화: document-review

> 💡 비유: 요리 레시피를 친구에게 전달하기 전에 "이 부분 설명이 부족한데?", "이건 왜 넣은 거야?", "더 간단하게 못 해?"라고 점검해주는 친구.

**목적**: 브레인스톰/플랜 문서를 다음 단계로 넘기기 전에 품질을 높이는 구조화된 리뷰 스킬.

**동작 과정 (6단계)**:

```
[Step 1] 문서 확보 — 경로 지정 또는 최근 문서 탐색
   ↓
[Step 2] 평가 질문 — 5가지 핵심 질문으로 문제점 발굴
   │  ├─ 불명확한 것은?
   │  ├─ 불필요한 것은?
   │  ├─ 회피된 결정은?
   │  ├─ 명시되지 않은 가정은?
   │  └─ 스코프가 확장될 위험은?
   ↓
[Step 3] 점수 평가 — Clarity / Completeness / Specificity / YAGNI 4개 기준
   ↓
[Step 4] 핵심 개선점 식별 — "반드시 고쳐야 할 1가지" 하이라이트
   ↓
[Step 5] 수정 적용 (사소: 자동 / 구조적: 승인 요청)
   ↓
[Step 6] 다음 액션 — 재검토 or 완료 (2회 후 완료 권장)
```

**단순화(Simplification) 원칙**: 가상의 미래 요구사항을 위한 내용, 중복 정보, 다음 단계에 불필요한 디테일은 제거. 단, 구현에 영향을 주는 제약이나 대안 거부 사유는 보존.

#### CE 스킬 심화: every-style-editor

> 💡 비유: 학교에서 선생님이 빨간 펜으로 작문을 고쳐주는 것. 단, "Every 스타일 가이드"라는 교과서를 기준으로만 채점.

**목적**: Every 매체의 스타일 가이드에 맞춰 글을 줄 단위로 교정하는 전문 편집 스킬.

**동작 과정 (4단계)**:

```
[Step 1] 초기 평가 — 문서 유형, 대상 독자, 톤 파악
   ↓
[Step 2] 상세 라인 편집 — 문장별로 문법/구두점/대소문자/어휘 검토
   ↓
[Step 3] 기계적 검토 — 포매팅 일관성, 숫자 표기, 링크 형식 확인
   ↓
[Step 4] 결과 출력 — 에러 목록 + 규칙 참조 + 반복 패턴 + 개선 권고
```

**출력 포맷**: 각 에러마다 `위치 → 이슈 유형 → 원본 → 수정안 → 규칙 참조 → 설명` 구조화 제시.

**핵심 원칙**:
- ✅ 저자의 목소리(voice) 보존, 에러만 수정
- ✅ 모호한 경우 옵션 제시 + 가장 명확한 선택 추천
- ⚠️ Every 영문 매체 특화 — 범용 한국어 문체 검토에는 직접 적용 어려움

---

### 2.3 Superpowers 스킬 맵 (14개 스킬)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Superpowers Skill Chain                           │
│                                                                     │
│  using-superpowers (메타 스킬)                                       │
│  │  "1% 가능성이라도 있으면 반드시 스킬 invoke"                         │
│  │  SessionStart hook → EXTREMELY_IMPORTANT 태그로 컨텍스트 주입      │
│  │  프로세스 스킬 > 구현 스킬 우선순위                                  │
│  │                                                                  │
│  ▼                                                                  │
│  brainstorming                                                      │
│  │  1. 프로젝트 컨텍스트 탐색                                         │
│  │  2. 한 번에 하나씩 명확화 질문                                      │
│  │  3. 2-3개 접근법 제안 + 추천                                       │
│  │  4. 설계 문서 작성 (docs/plans/YYYY-MM-DD-<topic>-design.md)      │
│  │  5. 설계 승인까지 구현 차단 (HARD GATE)                             │
│  │  → writing-plans만 후속 가능                                       │
│  │                                                                  │
│  ▼                                                                  │
│  writing-plans                                                      │
│  │  2-5분 단위 태스크 분해                                             │
│  │  TDD 방법론 기반 (실패 테스트 → 구현 → 통과 → 커밋)                  │
│  │  정확한 파일 경로 + 완전한 코드 샘플 + 테스트 명령 포함               │
│  │  docs/plans/YYYY-MM-DD-<feature>.md 저장                          │
│  │                                                                  │
│  ▼ (두 가지 실행 경로)                                                │
│  ┌────────────────────┬──────────────────────────┐                   │
│  │ subagent-driven-   │ executing-plans           │                   │
│  │ development        │ (별도 세션 실행)            │                   │
│  │ (현재 세션 실행)    │                            │                   │
│  │                    │ 배치 실행 (기본 3개씩)       │                   │
│  │ 태스크별:          │ 체크포인트 리뷰              │                   │
│  │ implementer 파견   │ 블로커 즉시 중단             │                   │
│  │ → spec-reviewer    │                            │                   │
│  │ → quality-reviewer │                            │                   │
│  │ (2단계 리뷰 게이트) │                            │                   │
│  └────────┬───────────┴──────────┬───────────────┘                   │
│           ▼                      ▼                                   │
│  test-driven-development (자동 트리거)                                │
│  │  RED → GREEN → REFACTOR (Iron Law: 테스트 없는 코드 삭제)           │
│  │                                                                  │
│  verification-before-completion (자동 트리거)                         │
│  │  "증거 없이 완료 주장 차단" (Iron Law)                               │
│  │  5단계 Gate Function: IDENTIFY → RUN → READ → VERIFY → CLAIM     │
│  │                                                                  │
│  systematic-debugging (문제 발생 시 자동 트리거)                       │
│  │  4단계 근본원인 분석                                                │
│  │                                                                  │
│  dispatching-parallel-agents (3+ 독립 실패 시)                       │
│  │  도메인별 에이전트 병렬 파견                                        │
│  │                                                                  │
│  requesting-code-review / receiving-code-review                     │
│  │  commit SHA 기반 리뷰 요청 + 피드백 즉시 반영                       │
│  │                                                                  │
│  finishing-a-development-branch                                     │
│  │  테스트 통과 필수 → 4가지 옵션 (merge/PR/유지/폐기)                  │
│  │                                                                  │
│  using-git-worktrees                                                │
│  │  격리된 작업 공간 생성 + 의존성 설치                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. 9축 비교 분석

### 3.1 철학/패러다임

| 축 | Ouroboros | Compound Engineering | Superpowers |
|----|-----------|---------------------|-------------|
| **패러다임** | 진화적 수렴 (Evolutionary) | 파이프라인 자동화 (Pipeline) | 규율 기반 장인 (Disciplined Craft) |
| **핵심 가치** | 요구사항을 수학적으로 결정화 | 최대 병렬화로 빠른 배포 | 증거와 테스트로 품질 보장 |
| **비유** | 생물 진화 — 세대를 거듭하며 적자생존 | 공장 컨베이어 벨트 — 단계별 자동 처리 | 도제 훈련 — 규율과 습관이 품질을 만듦 |
| **자기 인식** | 있음 (drift 측정, 수렴 감지, 정체 탐지) | 없음 (파이프라인은 앞으로만 진행) | 제한적 (verification은 있으나 메타인지 아님) |

### 3.2 워크플로우 구조

| 축 | Ouroboros | Compound Engineering | Superpowers |
|----|-----------|---------------------|-------------|
| **구조** | **루프** (interview → seed → run → evaluate → evolve, 수렴까지 반복) | **선형 파이프라인** (brainstorm → plan → deepen → work → review → compound) | **순차 체인** (brainstorm → plan → execute, 스킬 자동 트리거) |
| **분기** | evolve_rewind로 이전 세대 분기 가능 | /lfg로 전체 자동화, 개별 단계 독립 실행 가능 | subagent-driven vs executing-plans 분기 |
| **세션 관리** | EventSourcing + 체크포인트 (세션 간 상태 영속) | docs/plans/ 파일 기반 (상태 암시적) | Git worktree 기반 격리 |
| **되돌림** | evolve_rewind (특정 세대로 되감기) | 없음 (git revert 수동) | 없음 (블로커 시 즉시 중단) |

### 3.3 요구사항 정제 방식

| 축 | Ouroboros | Compound Engineering | Superpowers |
|----|-----------|---------------------|-------------|
| **방식** | **Socratic Interview** (수학적 게이팅) | **Brainstorm Session** (구조화된 대화) | **Brainstorm** (설계 문서 작성) |
| **깊이** | 모호성 점수 ≤ 0.2 수학적 게이트 (greenfield 3축, brownfield 4축 가중 평균) | Phase 0-3 (명확성 평가 → 이해 → 탐색 → 캡처), 정량적 게이트 없음 | 6단계 (컨텍스트 → 질문 → 접근법 → 설계 → 문서 → 전환), HARD GATE는 "승인" 여부 |
| **9개 전문 에이전트** | socratic-interviewer + ontologist가 본질적 정의 추구 | 단독 brainstorming 스킬 (에이전트 미분리) | 단독 brainstorming 스킬 (에이전트 미분리) |
| **산출물** | 모호성 점수 + 인터뷰 세션 상태 (MCP 영속) | docs/brainstorms/YYYY-MM-DD-topic-brainstorm.md | docs/plans/YYYY-MM-DD-topic-design.md |
| **"너무 단순해서 안 해도 됨" 방지** | 모호성 점수가 수치로 판단 | Phase 0에서 skip 가능 (명시적 AC + 좁은 범위일 때) | "This Is Too Simple To Need A Design" 안티패턴으로 명시적 차단 |

### 3.4 계획 수립 방식

| 축 | Ouroboros | Compound Engineering | Superpowers |
|----|-----------|---------------------|-------------|
| **계획 형태** | **Seed** — 불변 YAML 사양서 (GOAL, CONSTRAINTS, AC, ONTOLOGY, EVALUATION_PRINCIPLES, EXIT_CONDITIONS) | **Plan Document** — Markdown 문서 (3단계 상세도: MINIMAL/MORE/A LOT) | **Plan File** — Markdown 문서 (2-5분 단위 TDD 태스크) |
| **계획 강화** | evolve가 seed를 세대별로 진화시킴 (ontology mutation) | /deepen-plan이 40+ 에이전트 병렬로 리서치 주입 | 없음 (계획 작성 시 1회 완료) |
| **리서치 통합** | 없음 (seed는 인터뷰에서만 도출) | 4개 리서치 에이전트 + Context7 MCP + WebSearch + docs/solutions/ 학습 | 프로젝트 파일/커밋/문서 탐색만 |
| **외부 지식** | 없음 | Context7 (프레임워크 문서) + WebSearch (2024-2026 모범사례) | 없음 |
| **검증 체크** | seed-architect 에이전트가 완전성/명확성 검증 | spec-flow-analyzer + brainstorm 교차검증 | 없음 (사용자 승인만) |

### 3.5 실행 방식

| 축 | Ouroboros | Compound Engineering | Superpowers |
|----|-----------|---------------------|-------------|
| **실행 엔진** | **ouroboros_execute_seed** MCP — Double Diamond 분해 + PAL Router | **/ce:work** — Todo 기반 태스크 루프 + 선택적 Swarm Mode | **executing-plans** — 배치 실행 (3개씩) + 체크포인트 리뷰 |
| **모델 최적화** | PAL Router (Frugal/Standard/Frontier 자동 에스컬레이션/디에스컬레이션) | 없음 (Claude Code 기본) | 없음 (Claude Code 기본) |
| **병렬화** | AC 레벨 병렬 실행 (parallel=true 옵션) | Swarm Mode (5+ 독립 태스크 시 병렬 에이전트 파견) | dispatching-parallel-agents (3+ 독립 실패 시) + subagent per task |
| **자동화 수준** | evolve/ralph로 완전 자율 루프 가능 | /lfg로 plan→work→review→compound 완전 자동 | 배치 단위 인간 체크포인트 필수 |
| **TDD 강제** | 없음 (evaluate에서 사후 검증) | 언급되지만 강제 아님 ("unit tests with mocks + integration tests") | **Iron Law** — 테스트 없는 코드 삭제 강제 |

### 3.6 검증 방식

| 축 | Ouroboros | Compound Engineering | Superpowers |
|----|-----------|---------------------|-------------|
| **검증 구조** | **3단계 파이프라인** (Mechanical → Semantic → Consensus) | **다중 에이전트 리뷰** (14 review agents + Ultra-Thinking) | **증거 기반 체크리스트** (verification-before-completion) |
| **Stage 1** | Mechanical: lint, build, test (최저 비용, 빠른 실패) | 전체 테스트 + 린팅 | 검증 명령 실행 + 출력 읽기 |
| **Stage 2** | Semantic: AC 준수, goal 정렬, drift 측정 (Standard tier) | 병렬 리뷰 에이전트 (security-sentinel, performance-oracle, data-integrity-guardian 등) | spec-reviewer + code-quality-reviewer (2단계 리뷰) |
| **Stage 3** | Multi-model Consensus: 다중 모델 합의 투표 (Frontier tier, 선택적) | Ultra-Thinking (5 이해관계자 관점: 개발자/운영/사용자/보안/비즈니스) | 없음 |
| **수치 측정** | drift score (goal 50% + constraint 30% + ontology 20%) | P1/P2/P3 심각도 분류 | pass/fail 바이너리 |
| **Multi-model** | 있음 (LiteLLM 100+ 모델) | 없음 | 없음 |

### 3.7 문서 리뷰 메커니즘

기존 3.6은 **코드/실행 결과물 검증**을 다룬다. 이 섹션은 **brainstorm/plan 문서 리뷰**를 다룬다. "document-review"를 단일 도구로 다루는 것은 부정확하며, 실제로는 3종류가 존재한다.

> 수렴 검증 완료: 4회 iteration, 9개 발견사항 안정 카운터 >= 2, CONTESTED 0건
> 리포트: `docs/demiurge/rl-verify/plan-tools-doc-review-compat/report.md`

| 리뷰 도구 | 소속 | 평가 기준 | 대상 | 형태 |
|-----------|------|----------|------|------|
| **CE document-review** | Compound Engineering | Clarity, Completeness, Specificity, YAGNI | brainstorm/plan **문서** | standalone interactive skill |
| **spec/plan-document-reviewer** | Superpowers | Scope, Completeness, Spec-Alignment, Buildability | spec/plan **문서** | subagent dispatch template (2종) |
| **ouroboros evaluate** | Ouroboros | Mechanical → Semantic → Consensus | **코드/실행 결과물** | 3단계 파이프라인 (MCP 기반) |

| 축 | Ouroboros | Compound Engineering | Superpowers |
|----|-----------|---------------------|-------------|
| **리뷰 도구** | evaluate (3단계 파이프라인) | CE document-review | spec-reviewer + plan-reviewer (2종) |
| **평가 기준** | AC 충족, Goal Alignment, Drift | Clarity, Completeness, Specificity, YAGNI | Scope, Spec-Alignment, Buildability |
| **대상** | 코드/실행 결과물 | brainstorm/plan 문서 | spec/plan 문서 |
| **파이프라인 의존성** | 높음 (session_id + Seed + AC 필요) | 낮음 (파일만 있으면 됨) | 낮음 (파일만 있으면 됨, plan-reviewer는 Spec도 필요) |
| **출력** | 정량적 점수 (Path A) / 정성적 (Fallback) | 정성적 피드백 | 정성적 피드백 |

### 3.8 교차 호환성

각 harness의 워크플로우를 따르면 자체 리뷰가 이미 포함되어 있다. 그러나 **교차 검증은 "중복"이 아니라 "보완"**에 가깝다 — 평가 기준이 다르기 때문이다.

| 도구 | 파일 생성 | CE document-review | 자체 리뷰 메커니즘 |
|------|----------|-------------------|-------------------|
| **Plan Mode** (내장) | O* (`~/.claude/plans/`) | O* (경로 지정 필요) | 없음 |
| **superpowers:writing-plans** | O (`docs/superpowers/plans/`) | O* (경로 지정 필요) | **plan-document-reviewer** |
| **superpowers:brainstorming** | O (`docs/superpowers/specs/`) | O* (경로 지정 필요) | **spec-document-reviewer** |
| **CE workflows:plan** | O (`docs/plans/`) | **O** (네이티브) | CE document-review |
| **CE workflows:brainstorm** | O (`docs/brainstorms/`) | **O** (네이티브) | CE document-review |
| **ouroboros:interview** | O*/X (Path 의존) | O* (MCP + 경로 지정) | **ouroboros evaluate** |
| **ouroboros:seed** | O (Seed YAML) | O* (경로 지정 필요) | ouroboros evaluate |

> `O*` = 가능하나 추가 조건 있음 (경로 직접 지정, 특정 모드 등)

**교차 검증 실무 기준**: 단순한 작업 → 자체 리뷰 충분. 복잡한 작업 → CE의 YAGNI + superpowers의 Buildability가 서로 다른 약점을 잡아줌. 고위험 작업 → ouroboros evaluate의 다관점 수렴이 가장 강력.

**방향성 제약**: ouroboros evaluate → 타 harness 산출물은 어려움 (Seed+AC 필요). CE document-review → ouroboros 산출물은 가능 (파일만 있으면 됨).

### 3.9 MCP 의존성 (Ouroboros)

Superpowers와 CE는 **Markdown 파일만으로 모든 기능이 동작**한다. Ouroboros는 스킬에 따라 MCP 의존도가 다르다.

| 스킬 | MCP 필요 | Fallback | Fallback 품질 |
|------|----------|----------|--------------|
| interview | 선호 | O (agent 기반) | 괜찮음 — 디스크 저장 안 됨 |
| seed | 선호 | O (컨텍스트에서 생성) | 괜찮음 |
| unstuck | 선호 | O (agent 위임) | 괜찮음 |
| **run** | **필수** | X | — |
| **evaluate** | **필수** | △ (evaluator agent) | 정성적 평가만 |
| **status** | **필수** | X | — |
| **evolve** | **필수** | X | — |
| **ralph** | **Plugin+MCP** | 부분적 | 부분적 |
| welcome/tutorial/help | 불필요 | O | 완전 |

> 비유: ouroboros는 **온라인 게임** — 캐릭터 생성(interview)과 스킬트리(seed)는 오프라인 가능, 실제 전투(run)/전적(status)/랭크(evaluate)는 서버 필수. superpowers/CE는 **오프라인 싱글플레이** — 파일만 있으면 전부 동작.

### 3.10 정체 해결 (Unstuck)

| 축 | Ouroboros | Compound Engineering | Superpowers |
|----|-----------|---------------------|-------------|
| **메커니즘** | **ouroboros_lateral_think** — 5개 페르소나 | 없음 (파이프라인 중단 없는 설계) | **systematic-debugging** — 4단계 근본원인 분석 |
| **접근** | 횡적 사고 (문제를 다른 관점으로 재정의) | — | 종적 사고 (근본 원인을 깊이 추적) |
| **페르소나** | hacker("일단 작동시켜"), researcher("문서부터 읽어"), simplifier("불필요한 것 제거"), architect("구조 재설계"), contrarian("전제를 의심해") | — | 없음 (체계적 프로세스, 페르소나 없음) |
| **자동 트리거** | "I'm stuck", "think sideways" 등 자연어 | — | 테스트 실패 시 자동 (systematic-debugging) |
| **진화적 되감기** | evolve_rewind로 이전 세대 복원 + 다른 방향 탐색 | — | — |

### 3.11 자기 참조 / 메타인지

| 축 | Ouroboros | Compound Engineering | Superpowers |
|----|-----------|---------------------|-------------|
| **Drift 측정** | goal drift(50%) + constraint drift(30%) + ontology drift(20%) → 3단계 판정 (0-0.15 excellent, 0.15-0.30 acceptable, 0.30+ exceeded) | 없음 | 없음 |
| **수렴 감지** | ontology similarity ≥ 0.95 → 자동 수렴 종료 | 없음 | 없음 |
| **정체 탐지** | 3회 동일 세대, period-2 진동, 70%+ 질문 반복 → 자동 종료 | 없음 | 없음 |
| **세대 계보** | ouroboros_lineage_status — 세대별 ontology 진화 추적 | 없음 | 없음 |
| **AC 대시보드** | ouroboros_ac_dashboard — AC별 pass/fail 매트릭스 (세대 횡단) | 없음 | 없음 |
| **자기 참조** | 자기 출력을 다음 세대 입력으로 사용 (우로보로스 루프) | 없음 | 없음 |

### 3.12 지식 축적

| 축 | Ouroboros | Compound Engineering | Superpowers |
|----|-----------|---------------------|-------------|
| **메커니즘** | EventSourcing (모든 이벤트 영속 저장, 세션 재구성 가능) | **/ce:compound** (5 서브에이전트 → docs/solutions/ 구조화 저장) + learnings-researcher 자동 검색 | 없음 (기본 프레임워크에는 지식 축적 없음) |
| **검색** | ouroboros_query_events (이벤트 타입/세션별 필터 + 페이지네이션) | learnings-researcher (YAML frontmatter — tags, category, module, symptom, root_cause) | — |
| **조직 기억** | session → lineage → event store (기술적 이벤트 로그) | docs/solutions/ (인간 읽기 가능한 해결 기록) | — |
| **재사용** | 기존 세션 resume, lineage rewind | /ce:plan이 14일 이내 brainstorm 자동 연결, /deepen-plan이 docs/solutions/ 자동 참조 | — |

---

## 4. 핵심 차별점 요약

### Ouroboros만의 고유 기능
1. **수학적 게이팅** — 모호성 점수, ontology similarity, drift score 등 정량 지표로 워크플로우 전환 판단
2. **진화적 루프** — seed가 세대를 거듭하며 자기 개선 (수렴 또는 정체까지)
3. **되감기(rewind)** — 이전 세대로 분기하여 다른 진화 경로 탐색
4. **Multi-model Consensus** — LiteLLM 통합으로 다중 모델 합의 검증
5. **PAL Router** — 비용 최적화된 모델 자동 선택 (Frugal/Standard/Frontier)
6. **9개 전문 에이전트** — 각 역할(socratic, ontologist, contrarian 등)에 특화된 페르소나
7. **Drift 측정** — 실행 중 목표 이탈도를 실시간 추적

### Compound Engineering만의 고유 기능
1. **40+ 에이전트 병렬 리뷰** — /deepen-plan에서 발견된 모든 에이전트를 무차별 병렬 실행
2. **/lfg 완전 자동화** — plan → deepen → work → review → compound → test → video 원스톱
3. **3단계 계획 상세도** — MINIMAL/MORE/A LOT 상황별 선택
4. **Context7 + WebSearch 통합** — 외부 프레임워크 문서와 최신 모범사례 자동 리서치
5. **Ultra-Thinking 리뷰** — 5개 이해관계자 관점으로 심층 인지 프로세스
6. **docs/solutions/ 지식 DB** — 구조화된 YAML frontmatter로 해결 기록 영구 저장 + 자동 검색
7. **Feature Video** — PR에 변경사항 스크린샷/비디오 자동 첨부

### Superpowers만의 고유 기능
1. **TDD Iron Law** — 테스트 없는 코드는 삭제해야 한다는 절대 규칙
2. **Verification Iron Law** — 증거 없는 완료 주장 차단 (5단계 Gate Function)
3. **SessionStart Hook 자동 주입** — "1% 가능성이라도 스킬 invoke" 강제
4. **2단계 리뷰 게이트** — spec-reviewer → code-quality-reviewer 순차 통과 필수
5. **Systematic Debugging** — 4단계 근본원인 분석 (추측 수정 차단)
6. **Git Worktree 통합** — 격리된 개발 환경 강제
7. **배치 실행 + 인간 체크포인트** — 3개 태스크마다 인간 피드백 수집

---

## 5. 강점과 약점

### Ouroboros

| 강점 | 약점 |
|------|------|
| 요구사항 모호성을 수학적으로 측정하고 게이팅 | 실제 코딩/TDD 강제력 부재 — 코드 품질은 별도 도구 필요 |
| 진화적 루프로 스펙이 자동 개선 | Python 3.14+ 요구 — 환경 제약 높음 |
| Drift 측정으로 목표 이탈 실시간 감지 | 학습 곡선 높음 (9 에이전트, 12 MCP 도구, EventSourcing) |
| Multi-model consensus로 검증 신뢰도 향상 | 코드 구현 자체보다 스펙 결정화에 집중 — 실행은 별도 |
| 되감기로 대안 진화 경로 탐색 가능 | UI/UX 개발, 프론트엔드 등에는 과도한 추상화 |
| 비용 최적화 (PAL Router) | 단순 작업에도 interview → seed 절차 필수 |
| 횡적 사고 5 페르소나로 정체 해결 | Compound/Superpowers 대비 커뮤니티/생태계 작음 |

### Compound Engineering

| 강점 | 약점 |
|------|------|
| /lfg 하나로 전 과정 자동화 (제로 개입) | 요구사항 정제가 피상적 — 수학적 게이트 없음 |
| 40+ 에이전트 병렬 리뷰로 포괄적 품질 검증 | 파이프라인 중간 되돌림/분기 메커니즘 없음 |
| docs/solutions/ 지식 DB + 자동 검색 | 자기 인식/drift 측정 없음 — 목표 이탈 감지 불가 |
| 외부 리서치 통합 (Context7 + WebSearch) | 정체 해결 메커니즘 없음 — 막히면 수동 개입 필요 |
| 3단계 계획 상세도로 유연한 대응 | TDD 강제력 없음 — "테스트 권장"에 그침 |
| 설치 간편 (Markdown 기반, 런타임 의존성 없음) | /deepen-plan의 무차별 병렬 실행은 토큰 비용 높음 |
| Feature video + 스크린샷 자동 PR 첨부 | 진화/수렴 개념 없음 — 계획은 1회성 |

### Superpowers

| 강점 | 약점 |
|------|------|
| TDD Iron Law + Verification Iron Law로 품질 절대 보장 | 외부 리서치 통합 없음 — 프로젝트 내부 정보만 활용 |
| SessionStart Hook으로 스킬 자동 트리거 보장 | 지식 축적 메커니즘 없음 — 세션 간 학습 저장 없음 |
| 2단계 리뷰 게이트 (spec + quality) 순차 통과 | 요구사항 정제에 수학적/정량적 게이트 없음 |
| Systematic Debugging으로 추측 수정 차단 | 완전 자동화(/lfg 같은) 파이프라인 없음 |
| Git Worktree 격리 강제 | 모델 비용 최적화 없음 |
| 배치 실행 + 인간 체크포인트로 안전한 진행 | 되돌림/진화/drift 측정 없음 |
| 설치 간편 + 경량 (Hook 1개 + Markdown 스킬) | 에이전트 수가 적어 리뷰 관점 다양성 제한적 |

---

## 6. 종합 비교 테이블

| 비교 축 | Ouroboros | Compound Engineering | Superpowers |
|---------|-----------|---------------------|-------------|
| 철학 | 진화적 수렴 | 파이프라인 자동화 | 규율 기반 장인정신 |
| 워크플로우 | 루프 (수렴까지) | 선형 파이프라인 | 순차 체인 (Hook 자동) |
| 요구사항 정제 | Socratic + 수학적 게이트 (≤0.2) | Brainstorm 4단계 | Brainstorm + HARD GATE |
| 계획 수립 | 불변 YAML Seed + 진화 | 3단계 상세도 Plan + deepen | 2-5분 TDD 태스크 Plan |
| 계획 강화 | evolve (세대별 자동 개선) | deepen-plan (40+ 에이전트 리서치) | 없음 |
| 외부 리서치 | 없음 | Context7 + WebSearch | 없음 |
| 실행 방식 | MCP 엔진 + PAL Router | Todo 루프 + Swarm | 배치 실행 + Subagent |
| TDD 강제 | 없음 | 권장 수준 | Iron Law (절대 강제) |
| 검증 | 3단계 (Mechanical→Semantic→Consensus) | 다중 에이전트 + Ultra-Thinking | 증거 기반 Gate Function |
| Multi-model | 있음 (LiteLLM 100+) | 없음 | 없음 |
| Drift 측정 | 있음 (3축 가중 점수) | 없음 | 없음 |
| 정체 해결 | 5 페르소나 횡적사고 + 되감기 | 없음 | Systematic Debugging |
| 자기 참조 | 있음 (진화 루프 핵심) | 없음 | 없음 |
| 지식 축적 | EventStore (기술 이벤트) | docs/solutions/ (인간 읽기) | 없음 |
| 자동화 수준 | evolve/ralph (완전 자율) | /lfg (완전 자동) | 배치별 인간 체크포인트 |
| 환경 요구 | Python 3.14+ MCP 서버 | Markdown only | Markdown + Hook |
| 에이전트 수 | 9 (전문 페르소나) | 24+ (리뷰/리서치/디자인/워크플로우) | code-reviewer 1 + subagent 프롬프트 |
| 문서 리뷰 | evaluate (Fallback: 정성적) | CE document-review (Clarity/YAGNI) | spec+plan reviewer (Alignment/Buildability) |
| 교차 호환 | 낮음 (DB 의존) | 높음 (파일 기반, 범용) | 높음 (파일 기반, 범용) |
| MCP 의존도 | 높음 (4+1개 필수, 3개 선호) | 없음 (Markdown only) | 없음 (Markdown + Hook) |

---

## 7. 사용 가이드 — 어떤 상황에서 어떤 도구를?

### Ouroboros가 적합한 경우
- **요구사항이 극도로 모호한 프로젝트** — "뭔가 좋은 걸 만들고 싶어"에서 시작하는 greenfield
- **스펙 정확성이 최우선인 도메인** — 금융, 의료, 보안 등 잘못된 스펙이 치명적인 영역
- **장기 진화가 필요한 프로젝트** — 스펙이 여러 세대를 거쳐 정제되어야 하는 연구/탐색적 작업
- **Multi-model 검증이 필요한 경우** — 단일 모델의 편향을 합의로 보완해야 할 때
- **비용 최적화가 중요한 대규모 작업** — PAL Router로 모델 비용 자동 조절

### Compound Engineering이 적합한 경우
- **빠른 기능 배포가 목표** — /lfg 하나로 계획부터 PR까지 자동화
- **팀의 지식을 축적하고 재사용하고 싶을 때** — docs/solutions/ + learnings-researcher
- **외부 리서치가 중요한 작업** — 새로운 프레임워크/라이브러리 도입, 모범사례 조사
- **다양한 관점의 리뷰가 필요할 때** — 24+ 에이전트가 보안/성능/아키텍처/데이터 등 다축 검증
- **비개발 산출물도 필요할 때** — Feature video, 스크린샷, changelog 자동 생성

### Superpowers가 적합한 경우
- **코드 품질이 절대적으로 중요한 프로젝트** — TDD Iron Law + Verification Iron Law
- **인간 감독을 유지하며 개발하고 싶을 때** — 배치 체크포인트로 매 3개 태스크마다 검토
- **경량 설치로 빠르게 시작하고 싶을 때** — Hook 1개 + Markdown 스킬만으로 동작
- **체계적 디버깅이 빈번한 레거시 코드 작업** — systematic-debugging 4단계 근본원인 분석
- **다른 도구와 조합하고 싶을 때** — Ralph Loop 엔진 + Compound 지식 DB와 자연스럽게 조합 가능 (see: [[ralph-superpowers-compund]])

### 3도구 조합 전략

```
┌──────────────────────────────────────────────────────────────────┐
│                     최적 조합 시나리오                             │
│                                                                  │
│  [초기 스펙이 극도로 모호]                                         │
│    → Ouroboros interview + seed로 스펙 결정화                     │
│    → 결정화된 seed를 Superpowers writing-plans로 태스크 분해       │
│    → Compound /ce:work로 실행 + /ce:compound로 학습 축적           │
│                                                                  │
│  [일반 기능 개발]                                                  │
│    → Compound /ce:brainstorm + /ce:plan + /deepen-plan           │
│    → Superpowers 스킬이 TDD/검증/디버깅 자동 트리거                │
│    → Compound /ce:compound로 학습 기록                            │
│                                                                  │
│  [긴급 버그 수정]                                                  │
│    → Superpowers systematic-debugging 즉시 투입                   │
│    → verification-before-completion으로 수정 증명                  │
│    → Compound /ce:compound로 해결 기록                            │
│                                                                  │
│  [연구/탐색적 프로젝트]                                             │
│    → Ouroboros evolve 루프로 스펙 자체를 탐색                      │
│    → drift 측정으로 방향성 모니터링                                 │
│    → unstuck으로 정체 시 돌파                                      │
└──────────────────────────────────────────────────────────────────┘
```

---

## 8. 결론

세 도구는 **동일한 문제 영역**(AI 에이전트를 활용한 소프트웨어 개발)을 다루지만, **근본적으로 다른 철학**에 기반한다:

1. **Ouroboros**는 "요구사항의 불확실성"을 핵심 문제로 본다. 모호한 요구사항을 수학적으로 측정하고, 진화적 루프를 통해 스펙 자체를 수렴시키는 것이 유일하게 올바른 접근이라고 주장한다. 자기참조, drift 측정, 되감기 등 **메타인지 능력**이 가장 뛰어나지만, 실제 코드 작성과 품질 보장은 약하다.

2. **Compound Engineering**은 "속도와 자동화"를 핵심 가치로 본다. /lfg 하나로 계획부터 PR까지 완전 자동화하고, 40+ 에이전트 병렬 리뷰와 외부 리서치 통합으로 **처리량(throughput)**이 가장 높지만, 자기 인식과 정체 해결 능력이 없다.

3. **Superpowers**는 "코드 품질의 규율"을 핵심 가치로 본다. TDD Iron Law와 Verification Iron Law로 **품질의 절대적 보장**을 추구하며, 다른 도구와의 조합성이 가장 높지만, 단독으로는 리서치/지식축적/자동화가 부족하다.

**세 도구는 경쟁이 아닌 보완 관계**에 있으며, 각각 스펙 결정화(Ouroboros), 파이프라인 자동화(Compound), 품질 규율(Superpowers)이라는 서로 다른 레이어를 담당한다.

---

**Final Verdict: SUCCESS**
