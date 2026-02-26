---
created: 2026-02-20
source: claude-code
tags:
  - ralph-loop
  - superpowers
  - compound-engineering
  - claude-code
  - ai-engineering
  - workflow
---

# Ralph Loop + Superpowers + Compound Engineering 조합 가이드

---

## 역할 분담

```
┌─────────────────────────────────────────────────────────────────┐
│                    3개 플러그인 역할 분담                          │
├───────────────────┬─────────────────────┬───────────────────────┤
│   Ralph Loop      │   Superpowers       │  Compound Engineering │
│   (엔진)          │   (품질 보장)        │  (지식 축적)           │
├───────────────────┼─────────────────────┼───────────────────────┤
│ 반복 실행         │ 설계 (brainstorming) │ 과거 학습 검색         │
│ Stop Hook         │ 계획 (writing-plans) │ 해결 기록 저장         │
│ <promise> 종료    │ TDD 강제            │ 패턴 승격 (수동)       │
│ max-iterations    │ 체계적 디버깅        │ 조직 기억 관리         │
│                   │ 코드 리뷰            │                       │
│                   │ 완료 검증            │                       │
│                   │ Git worktree        │                       │
└───────────────────┴─────────────────────┴───────────────────────┘
```

---

## 전체 워크플로우: 루프 전 → 루프 중 → 루프 후

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  BEFORE LOOP                DURING LOOP              AFTER LOOP
  (준비, 1회)                (반복, N회)               (마무리, 1회)

  ┌──────────┐              ┌──────────┐              ┌──────────┐
  │SP:브레인  │              │RL:반복   │              │CE:학습   │
  │스토밍     │              │  실행    │              │  기록    │
  ├──────────┤              ├──────────┤              ├──────────┤
  │CE:과거   │              │SP:TDD    │              │SP:코드   │
  │학습 검색  │              │SP:디버깅  │              │  리뷰    │
  ├──────────┤              │SP:검증   │              ├──────────┤
  │SP:계획   │              └──────────┘              │SP:브랜치 │
  │  작성    │                                        │  마무리  │
  ├──────────┤                                        └──────────┘
  │SP:워크   │
  │  트리    │
  └──────────┘

  SP = Superpowers
  RL = Ralph Loop
  CE = Compound Engineering

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Phase 1: 루프 전 (Before Loop)

일반 Claude Code 세션에서 실행합니다. Ralph Loop은 아직 시작하지 않습니다.

### Step 1-1. 과거 학습 검색 (Compound)

```
"이전에 비슷한 작업을 한 적 있는지 docs/solutions/를 검색해줘.
키워드: [인증, OAuth, 세션 관리 등]"
```

Compound의 `learnings-researcher`가 과거 해결 기록을 검색하여, 이전에 겪었던 함정과 해결책을 미리 파악합니다.

### Step 1-2. 브레인스토밍 (Superpowers)

Superpowers의 brainstorming이 자동 트리거됩니다.

```
"사용자 인증 시스템을 OAuth2 + JWT로 구현하고 싶어"
```

brainstorming 스킬이:

- 요구사항을 Socratic 방식으로 탐색
- 설계 대안을 제시
- 사용자 승인까지 코드 작성 차단 (Hard Gate)

### Step 1-3. 계획 작성 (Superpowers)

brainstorming 완료 후 자동으로 `writing-plans`로 전환됩니다.

```
결과: docs/plans/2026-02-20-user-auth-oauth.md
```

각 태스크가 2-5분 단위로 분해되며, 정확한 파일 경로, 완전한 테스트 코드, 검증 명령이 포함됩니다.

### Step 1-4. Git Worktree 생성 (Superpowers)

```
→ using-git-worktrees 스킬이 격리된 작업 공간 생성
→ 의존성 설치 자동 감지
→ 기존 테스트 통과 확인 (baseline)
```

---

## Phase 2: 루프 중 (During Loop)

Ralph Loop을 시작합니다. 프롬프트 작성이 핵심입니다.

### Ralph Loop 프롬프트 템플릿

```markdown
/rl "
## 작업 지시

1. docs/plans/2026-02-20-user-auth-oauth.md 계획을 읽어라.
2. 가장 우선순위 높은 미완료 태스크를 선택하라.
3. 구현 전에 docs/solutions/를 검색하여 관련 과거 해결 기록을 확인하라.
4. TDD로 구현하라:
   - 먼저 실패하는 테스트를 작성
   - 테스트가 실패하는 것을 확인
   - 최소한의 코드로 테스트 통과
   - 리팩터링
5. 모든 테스트가 통과하면:
   - 계획 파일에서 해당 태스크를 완료로 표시
   - git add -A && git commit
6. 작업 중 발견한 운영 학습이 있으면 AGENTS.md에 기록하라 (간결하게).

## 완료 기준
- [ ] 계획의 모든 태스크가 완료됨
- [ ] 모든 테스트 통과
- [ ] 린터 에러 없음

## 하지 말 것
- 기존 테스트를 삭제하지 마라
- 테스트 없이 코드를 작성하지 마라
- 요청하지 않은 기능을 추가하지 마라
- 완료되지 않았는데 promise를 출력하지 마라

모든 완료 기준이 충족되면 <promise>COMPLETE</promise>를 출력하라.
" --max-iterations 30
```

### 루프 내 동작 흐름

```
┌─────────────────── 반복 N ───────────────────────┐
│                                                   │
│  1. 계획 파일 읽기                                 │
│     └→ docs/plans/*.md에서 다음 태스크 선택         │
│                                                   │
│  2. 과거 학습 참조 (Compound)                      │
│     └→ docs/solutions/ 검색                       │
│     └→ critical-patterns.md 확인                  │
│                                                   │
│  3. TDD 실행 (Superpowers 자동 트리거)             │
│     └→ RED: 실패 테스트 작성                       │
│     └→ GREEN: 최소 구현                           │
│     └→ REFACTOR: 정리                             │
│                                                   │
│  4. 문제 발생 시 (Superpowers 자동 트리거)          │
│     └→ systematic-debugging: 4단계 근본원인 조사   │
│                                                   │
│  5. 검증 (Superpowers 자동 트리거)                 │
│     └→ verification-before-completion             │
│     └→ Iron Law: 증거 없이 완료 주장 차단          │
│     └→ Gate Function: 5단계 검증 절차              │
│                                                   │
│  6. 커밋 + 계획 업데이트                           │
│     └→ 태스크 완료 표시                            │
│                                                   │
│  7. 전체 완료?                                    │
│     ├→ No: 루프 계속 (Stop Hook → 같은 프롬프트)   │
│     └→ Yes: <promise>COMPLETE</promise>           │
│                                                   │
└───────────────────────────────────────────────────┘
```

### Superpowers 스킬 자동 트리거 조건

루프 내에서 Superpowers 스킬은 **자동으로** 작동합니다 (같은 세션이므로).
Superpowers의 SessionStart hook이 `using-superpowers` 스킬 전체를 `<EXTREMELY_IMPORTANT>` 태그로 감싸 컨텍스트에 주입하며,
"1% chance라도 스킬이 적용될 수 있으면 반드시 invoke하라"는 지시를 통해 스킬이 트리거됩니다.
이는 별도의 hard-wired 로직이 아닌 컨텍스트 주입 기반 메커니즘이므로, 컨텍스트 누적 시 invoke 빈도가 줄어들 수 있습니다.
compact 이벤트 시 SessionStart hook이 재실행(`matcher: "startup|resume|clear|compact"`)되어 컨텍스트가 재주입됩니다.

| 상황             | 트리거되는 스킬                | 동작                 |
| ---------------- | ----------------------------- | -------------------- |
| 코드 구현 시작   | test-driven-development       | RED-GREEN-REFACTOR   |
| 테스트 실패      | systematic-debugging          | 4단계 근본원인 조사  |
| "완료" 주장 시   | verification-before-completion | Iron Law + Gate Function (증거 필수) |
| 여러 독립 실패   | dispatching-parallel-agents   | 병렬 조사            |

---

## Phase 3: 루프 후 (After Loop)

Ralph Loop이 완료된 후 일반 세션으로 돌아옵니다.

### Step 3-1. 학습 기록 (Compound)

```
/workflows:compound
```

또는 루프 중 해결한 까다로운 문제가 있었다면:

```
/workflows:compound "OAuth refresh token 만료 시 race condition 해결"
```

5개 서브에이전트가 병렬로:

- 문제 맥락 분석
- 해결책 추출
- 관련 문서 검색
- 예방 전략 수립
- 카테고리 분류

→ `docs/solutions/{category}/{filename}.md` 생성

### Step 3-2. 코드 리뷰 (Superpowers)

```
→ subagent-driven-development 내장 방식으로 per-task 2단계 리뷰:
  1. spec-reviewer subagent 파견 (계획대로 구현했는가?)
  2. code-quality-reviewer subagent 파견 (품질이 충분한가?)
  (requesting-code-review는 리뷰어 subagent들이 참조하는 템플릿 역할)
```

### Step 3-3. 브랜치 마무리 (Superpowers)

```
→ finishing-a-development-branch 스킬:
  1. 테스트 전체 통과 확인
  2. 4가지 옵션 제시:
     - main에 머지
     - PR 생성
     - 브랜치 유지
     - 작업 폐기
  3. 선택 실행 + worktree 정리
```

---

## 프롬프트 설계 가이드

Ralph Loop 프롬프트에 3개 플러그인의 시너지를 최대화하려면:

### 필수 포함 요소

```markdown
## 1. 계획 참조 (Superpowers writing-plans의 산출물)
"docs/plans/{plan-file}.md를 읽고 가장 우선순위 높은 미완료 태스크를 선택하라."

## 2. 과거 학습 참조 (Compound의 docs/solutions/)
"구현 전 docs/solutions/를 검색하여 관련 과거 해결 기록을 확인하라.
 특히 docs/solutions/patterns/critical-patterns.md를 반드시 읽어라."

## 3. TDD 강제 (Superpowers TDD)
"반드시 실패하는 테스트를 먼저 작성하고, 실패를 확인한 후 구현하라.
 테스트 없이 코드를 작성하지 마라."

## 4. 검증 강제 (Superpowers verification)
"완료를 주장하기 전에 모든 테스트를 실행하고 결과를 확인하라."

## 5. 학습 기록 지시 (AGENTS.md 패턴)
"작업 중 발견한 빌드/테스트 관련 학습이 있으면 AGENTS.md에 간결하게 기록하라."

## 6. 완료 기준 + 금지 사항 (Ralph Loop 필수)
"완료 기준: [체크리스트]"
"하지 말 것: [금지 목록]"
"모든 기준 충족 시 <promise>COMPLETE</promise>"
```

### 프롬프트 전체 예시

```markdown
/rl "
## 컨텍스트
이 프로젝트는 [프로젝트 설명]. 기술 스택: [스택].

## 참조 문서
- 계획: docs/plans/2026-02-20-feature-x.md
- 과거 학습: docs/solutions/ (특히 patterns/critical-patterns.md)
- 운영 정보: AGENTS.md

## 작업 프로세스
1. AGENTS.md를 읽고 빌드/테스트 방법을 파악하라
2. 계획 파일을 읽고 가장 우선순위 높은 미완료 태스크를 선택하라
3. docs/solutions/에서 관련 과거 해결 기록을 검색하라
4. TDD로 구현하라 (테스트 먼저 → 실패 확인 → 구현 → 통과 확인)
5. 문제 발생 시 근본 원인을 조사하라 (추측으로 수정하지 마라)
6. 모든 테스트 통과 확인 후:
   - 계획에서 태스크 완료 표시
   - 운영 학습이 있으면 AGENTS.md 업데이트 (간결하게)
   - git add -A && git commit
7. 까다로운 문제를 해결했으면 docs/solutions/에 간략히 기록하라

## 완료 기준
- [ ] 계획의 모든 태스크 완료
- [ ] 모든 테스트 통과 (증거 필수)
- [ ] 린터/타입체크 에러 없음

## 하지 말 것
- 테스트 없이 코드를 작성하지 마라
- 기존 테스트를 삭제하거나 수정하지 마라
- 요청하지 않은 기능을 추가하지 마라
- 추측으로 버그를 수정하지 마라 (근본 원인 조사 필수)
- 범위 밖 코드를 수정하지 마라
- 완료되지 않았는데 promise를 출력하지 마라

모든 완료 기준이 충족되면 <promise>COMPLETE</promise>를 출력하라.
" --max-iterations 30
```

---

## 파일 구조

```
project-root/
├── AGENTS.md                          ← 운영 정보 (Ralph이 매 반복 참조+업데이트)
├── docs/
│   ├── plans/                         ← Superpowers writing-plans 산출물
│   │   └── 2026-02-20-feature-x.md
│   └── solutions/                     ← Compound Engineering 학습 저장소
│       ├── patterns/
│       │   └── critical-patterns.md   ← 필수 읽기 (모든 반복에서 참조)
│       ├── runtime-errors/
│       ├── test-failures/
│       └── ...
├── .claude/
│   └── ralph-loop.local.md            ← Ralph Loop 상태 파일
└── src/                               ← 소스 코드
```

---

## 시퀀스 다이어그램

```
개발자          Superpowers       Ralph Loop      Compound Eng.
  │                │                  │                │
  │─"기능 X 구현"──▶│                  │                │
  │                │                  │                │
  │                │◀─── learnings-researcher ────────▶│
  │                │     (과거 학습 검색)               │
  │                │                  │                │
  │◀─brainstorming─│                  │                │
  │─설계 승인──────▶│                  │                │
  │                │                  │                │
  │◀─writing-plans─│                  │                │
  │  (계획 생성)    │                  │                │
  │                │                  │                │
  │◀─git-worktree──│                  │                │
  │  (격리 환경)    │                  │                │
  │                │                  │                │
  │─/rl "프롬프트"──┼─────────────────▶│                │
  │                │                  │                │
  │                │   ┌── 반복 1 ──┐ │                │
  │                │   │ 계획 읽기   │ │                │
  │                │   │ 학습 검색───┼─┼───────────────▶│
  │                │◀──┤ TDD 실행   │ │                │
  │                │──▶│ 디버깅     │ │                │
  │                │◀──┤ 검증      │ │                │
  │                │   │ 커밋      │ │                │
  │                │   └───────────┘ │                │
  │                │   ┌── 반복 2 ──┐ │                │
  │                │   │  ...       │ │                │
  │                │   └───────────┘ │                │
  │                │         ...     │                │
  │                │   <promise>     │                │
  │◀───────────────┼─────COMPLETE────│                │
  │                │                  │                │
  │─/workflows:compound──────────────┼───────────────▶│
  │                │                  │  (학습 기록)    │
  │                │                  │                │
  │◀─code-review───│                  │                │
  │◀─finish-branch─│                  │                │
  │                │                  │                │
```

---

## Hook 충돌 분석

3개 플러그인은 서로 다른 Hook 이벤트를 사용하므로 **구조적 충돌이 불가능**합니다.

```
┌──────────────────┬───────────────────────────────────────┐
│ Hook Event       │ 등록 플러그인                          │
├──────────────────┼───────────────────────────────────────┤
│ SessionStart     │ Superpowers만 (컨텍스트 주입)          │
│ Stop             │ Ralph Loop만 (프롬프트 재주입)         │
│ Compound Eng.    │ Hook 없음 (hooks/ 디렉토리 자체 없음)  │
└──────────────────┴───────────────────────────────────────┘
```

이것이 이 3-Plugin 조합의 가장 큰 강점입니다. Hook 수준 충돌이 아닌 **스킬 수준 충돌**(brainstorming 동명 스킬)만 주의하면 됩니다.

---

## 주의사항 및 한계

| 항목                            | 설명                                                                                        | 대응                                                                |
| ------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| **컨텍스트 누적**               | Ralph Loop은 세션 내 반복이라 컨텍스트가 누적됨. 루프가 길어질수록 compaction 발생 가능 (세부 정보 손실 위험) | `--max-iterations` 설정 권장 (README: "always use as safety net", 예시값: 20-50). 코드 기본값은 unlimited(0). 작업 복잡도에 따라 조정. SP는 compact 시 컨텍스트 재주입으로 부분 보완 |
| **Superpowers brainstorming**   | `<HARD-GATE>`가 사용자 승인 대기하여 무인 루프 정체 가능                                    | 프롬프트에 "설계/브레인스토밍을 하지 마라. 계획 파일의 태스크만 실행하라" 명시 |
| **스킬 네임스페이스 충돌**      | Superpowers와 Compound 모두 `brainstorming` 동명 스킬 보유 → 어느 것이 invoke될지 비결정적 (Claude Code의 동일 이름 스킬 해소 정책 미공개) | 루프 프롬프트에 "brainstorming 스킬을 사용하지 마라" 명시하거나, 두 플러그인 중 하나를 비활성화 |
| **Compound 자동감지**             | `/workflows:compound` 커맨드에 auto_invoke trigger_phrases("that worked", "it's fixed", "working now", "problem solved"; SKILL.md 추가: "that did it")가 활성 상태. `disable-model-invocation: true`는 compound-docs **스킬**에만 설정되어 있고 **커맨드**에는 없음. 단, 루프 내에서 Claude가 이런 완료 확인 문구를 출력할 가능성은 낮아 실제 위험은 중간 수준 | 루프 후 `/workflows:compound`으로 수동 실행 권장 |
| **AGENTS.md 비대화**            | Ralph이 매 반복 업데이트하면 파일이 커질 수 있음                                            | 프롬프트에 "60줄 이내 유지, 운영 정보만" 명시                       |
| **Plan/Build 미분리**           | Playbook처럼 2개 프롬프트가 아닌 단일 프롬프트                                              | 계획 작성은 루프 전에 완료하고, 루프는 빌드만                       |

---

## Playbook 대비 커버리지 최종 평가

```
                              Playbook    RL+SP+CE 조합
                              ────────    ─────────────
요구사항 정의 (Phase 1)         ████████    █████░░░      65%
계획 수립 (Phase 2)             ████████    ███████░      87%
빌드 루프 (Phase 3)             ████████    ██████░░      75%
컨텍스트 관리                   ████████    ████░░░░      50%
역압 시스템                     ██████░░    ████████████  150% ↑
코드 품질 보장                  ████░░░░    ████████████  150% ↑
조직 기억/학습                  ██████░░    ██████████░░  130% ↑
상류 조종                       ████████    ████░░░░      50%
JTBD 스펙 체계                  ████████    ██░░░░░░      25%
───────────────────────────────────────────────────────────
───────────────────────────────────────────────────────────
종합                            100%        ~72-87%
(단순 평균 ~87%, 초과항목 상한100% 적용 ~72%,
 핵심기능 가중2배 적용 ~75%)

주요 차이:
- 요구사항 65%: JTBD→Topic→Spec 3단계 퍼널 구조 부재
- 계획 87%: 기존 코드 대비 갭 분석(500 서브에이전트 탐색) 접근 부재
- 조직기억 130%: CE docs/solutions/의 구조화된 영구 지식 저장이
  Playbook보다 풍부. AGENTS.md 자동 로딩은 Playbook에도 있는 패턴(동일).
  RL+SP+CE 차별점은 CE가 해결 지식을 docs/solutions/에 구조화된 독립 DB로
  영구 저장하는 반면, Playbook은 'Signs' 개념(PROMPT.md 언어 패턴 진화 +
  AGENTS.md 운영 발견사항 + 코드베이스 패턴 추가)을 통해 여러 파일에
  분산 체화하는 방식의 차이.
- 품질/학습은 Playbook 이상, 구조/컨텍스트는 미달
```
