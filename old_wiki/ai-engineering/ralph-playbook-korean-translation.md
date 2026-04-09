---
created: 2026-02-20
source: claude-code
tags:
  - ralph-loop
  - ai-engineering
  - claude-code
  - autonomous-agent
---

# The Ralph Playbook — 한국어 번역 및 정리

> 원문: [https://github.com/ghuntley/how-to-ralph-wiggum](https://github.com/ghuntley/how-to-ralph-wiggum)

---

## Ralph Playbook이란?

2025년 12월, [Ralph](https://ghuntley.com/ralph/)의 강력하면서도 단순한 얼굴이 대부분의 AI 관련 타임라인 상단에 올랐습니다.

[@GeoffreyHuntley](https://x.com/GeoffreyHuntley)가 공유하는 엄청나게 똑똑한 인사이트에 관심을 기울이려 했지만, 이번 여름에는 Ralph가 딱히 와닿지 않았습니다. 그런데 최근의 모든 소란 덕분에 더 이상 무시하기 어려워졌습니다.

[@mattpocockuk](https://x.com/mattpocockuk)과 [@ryancarson](https://x.com/ryancarson)의 개요가 많은 도움이 됐는데, Geoff가 나타나서 ['아닌데'](https://x.com/GeoffreyHuntley/status/2008731415312236984)라고 하기 전까지만요.

### Ralph를 최적으로 활용하는 방법은?

많은 사람들이 다양한 형태로 좋은 결과를 얻고 있지만, 저는 이 접근법을 포착했을 뿐 아니라 실제로 가장 많은 시간을 투자해 검증한 사람의 의견을 최대한 정확히 읽고 싶었습니다.

그래서 [최근 영상](https://www.youtube.com/watch?v=O2bBWDoxO4s)과 Geoff의 [원본 포스트](https://ghuntley.com/ralph/)를 깊이 파고들어, 무엇이 가장 잘 작동하는지 직접 풀어보려 했습니다.

아래는 그 결과물 — 세부 사항을 정리한 (아마 강박적인) Ralph Playbook입니다.

---

## 워크플로우

### 3단계, 2개의 프롬프트, 1개의 루프

Ralph는 단순히 "코드를 작성하는 루프"가 아닙니다. **3단계**, **2개의 프롬프트**, **1개의 루프**로 구성된 퍼널입니다.

#### Phase 1. 요구사항 정의 (LLM 대화)

- 프로젝트 아이디어를 논의 → **Jobs to Be Done (JTBD)** 식별
- 개별 JTBD를 **관심 주제(Topic of Concern)**로 분해
- 서브에이전트를 사용하여 URL에서 정보를 컨텍스트로 로드
- LLM이 관심 주제를 이해하면: 서브에이전트가 각 주제별로 `specs/FILENAME.md` 작성

#### Phase 2/3. Ralph 루프 실행 (두 가지 모드, 필요에 따라 `PROMPT.md` 교체)

| 모드         | 사용 시점                           | 프롬프트 초점                                    |
| ------------ | ----------------------------------- | ------------------------------------------------ |
| **PLANNING** | 계획이 없거나 오래됨/잘못됨        | `IMPLEMENTATION_PLAN.md` 생성/업데이트만         |
| **BUILDING** | 계획이 존재함                       | 계획에서 구현, 커밋, 부수 효과로 계획 업데이트   |

**PLANNING 모드 루프 라이프사이클:**

1. 서브에이전트가 `specs/*`와 기존 `/src` 조사
2. 스펙 대비 코드 비교 (갭 분석)
3. `IMPLEMENTATION_PLAN.md`에 우선순위 작업 생성/업데이트
4. 구현 없음

**BUILDING 모드 루프 라이프사이클:**

1. **정찰** — 서브에이전트가 `specs/*` 조사 (요구사항)
2. **계획 읽기** — `IMPLEMENTATION_PLAN.md` 조사
3. **선택** — 가장 중요한 작업 선택
4. **조사** — 서브에이전트가 관련 `/src` 조사 ("구현되지 않았다고 가정하지 마라")
5. **구현** — N개 서브에이전트로 파일 작업
6. **검증** — 빌드/테스트에 1개 서브에이전트만 (역압)
7. **`IMPLEMENTATION_PLAN.md` 업데이트** — 작업 완료 표시, 발견 사항/버그 기록
8. **`AGENTS.md` 업데이트** — 운영 학습 사항이 있으면
9. **커밋**
10. **루프 종료** → 컨텍스트 초기화 → 다음 반복 새로 시작

---

### 핵심 개념

| 용어                            | 정의                                                        |
| ------------------------------- | ----------------------------------------------------------- |
| **Job to be Done (JTBD)**       | 상위 수준 사용자 니즈 또는 결과                             |
| **관심 주제 (Topic of Concern)** | JTBD 내의 독립적 측면/컴포넌트                              |
| **스펙 (Spec)**                  | 하나의 관심 주제에 대한 요구사항 문서 (`specs/FILENAME.md`) |
| **작업 (Task)**                  | 스펙과 코드를 비교하여 도출된 작업 단위                     |

**주제 범위 테스트: "'그리고' 없이 한 문장으로"**

- ✓ "색상 추출 시스템은 이미지를 분석하여 지배적인 색상을 식별한다"
- ✗ "사용자 시스템은 인증, 프로필, 결제를 처리한다" → 3개의 주제

---

## 핵심 원칙

### ⏳ 컨텍스트가 전부다

- 200K+ 토큰이 광고되지만 실제 사용 가능한 것은 ~176K
- 40-60% 컨텍스트 활용이 "스마트 존"
- **촘촘한 작업 + 루프당 1개 작업 = 100% 스마트 존 컨텍스트 활용**

이것이 모든 것을 결정합니다:

- **메인 에이전트/컨텍스트는 스케줄러로 사용** — 비싼 작업은 서브에이전트에 위임
- **서브에이전트를 메모리 확장으로 사용** — 각 서브에이전트는 ~156kb를 가비지 컬렉션됨
- **단순함과 간결함이 승리** — 장황한 입력은 결정론성을 저하시킴
- **JSON보다 Markdown 선호** — 더 나은 토큰 효율성

### 🧭 Ralph 조종하기: 패턴 + 역압(Backpressure)

올바른 **신호와 게이트**를 만들어 Ralph의 성공적인 출력을 조종하는 것이 **핵심**입니다. 두 방향에서 조종할 수 있습니다:

**상류(Upstream) 조종:**

- 결정론적 설정 보장: 매 루프의 컨텍스트가 동일한 파일(`PROMPT.md` + `AGENTS.md`)로 시작
- 기존 코드가 생성되는 패턴을 형성
- Ralph가 잘못된 패턴을 생성하면, 유틸리티와 기존 코드 패턴을 추가/업데이트하여 올바른 방향으로 유도

**하류(Downstream) 조종:**

- 테스트, 타입체크, 린트, 빌드 등으로 **역압** 생성 — 무효/수용 불가능한 작업을 거부
- 프롬프트는 "테스트 실행"이라고 일반적으로 지시. `AGENTS.md`가 프로젝트별 실제 명령을 지정
- 주관적 기준(미적 감각, UX 느낌)에는 **LLM-as-judge 테스트**로 역압 확장 가능

### 🙏 Ralph에게 Ralph답게 하라 (Let Ralph Ralph)

Ralph의 효과는 **얼마나 Ralph를 신뢰**하는가에서 나옵니다.

- LLM의 **자기 식별, 자기 수정, 자기 개선** 능력을 활용
- 구현 계획, 작업 정의 및 우선순위에 적용
- 반복을 통한 **eventual consistency** 달성

**보호 조치:**

- 자율 운영을 위해 `--dangerously-skip-permissions` 필요 — 모든 도구 호출 승인을 우회
- 철학: "해킹당하느냐가 아니라 언제 당하느냐. 그리고 피해 범위가 얼마인가?"
- 격리된 환경(Docker 샌드박스, Fly/E2B)에서 최소한의 접근 권한만으로 실행
- 탈출구: Ctrl+C로 루프 중지, `git reset --hard`로 미커밋 변경 되돌리기, 궤적이 잘못되면 계획 재생성

### 🚦 루프 밖으로 나가라

Ralph를 최대한 활용하려면 **Ralph의 길에서 벗어나야** 합니다. Ralph가 다음에 어떤 계획된 작업을 구현할지, 어떻게 구현할지를 포함한 **모든 작업**을 해야 합니다. 당신의 일은 이제 **루프 위에** 앉는 것이지 루프 안에 있는 것이 아닙니다.

**관찰하고 경로를 수정하라** — 특히 초기에는 앉아서 관찰하라. 어떤 패턴이 나타나는가? Ralph가 어디서 잘못 가는가?

**기타로 튜닝하듯** — 모든 것을 미리 처방하는 대신, 관찰하고 반응적으로 조정. Ralph가 특정 방식으로 실패하면, 다음에 도움이 될 표지판을 추가.

그리고 기억하라, **계획은 일회용**:

- 잘못되면 버리고 처음부터 다시 시작
- 재생성 비용은 Planning 루프 1회; Ralph가 제자리를 도는 것에 비하면 저렴
- 재생성 시점: Ralph가 잘못된 것을 구현할 때, 계획이 낡았을 때, 스펙을 크게 변경했을 때

---

## 루프 메커니즘

### 외부 루프 제어

Geoff의 초기 최소 형태:

```bash
while :; do cat PROMPT.md | claude ; done
```

**무엇이 작업 연속을 제어하는가?**

1. Bash 루프가 `PROMPT.md`를 claude에 공급
2. `PROMPT.md`가 지시: "`IMPLEMENTATION_PLAN.md`를 조사하고 가장 중요한 것을 선택하라"
3. 에이전트가 하나의 작업 완료 → 디스크의 IMPLEMENTATION_PLAN.md 업데이트, 커밋, 종료
4. Bash 루프가 즉시 재시작 → 새로운 컨텍스트 윈도우
5. 에이전트가 업데이트된 계획을 읽음 → 다음으로 가장 중요한 것 선택

**핵심 통찰:** `IMPLEMENTATION_PLAN.md` 파일이 디스크에 **반복 간 지속**되어 독립된 루프 실행들 사이의 **공유 상태** 역할을 합니다.

### 내부 루프 제어 (작업 실행)

단일 작업 실행에는 하드 기술적 제한이 없습니다. 제어는 다음에 의존합니다:

- **범위 규율** — PROMPT.md가 "하나의 작업"과 "테스트 통과 시 커밋"을 지시
- **역압** — 테스트/빌드 실패가 에이전트에게 커밋 전 수정 강제
- **자연스러운 완료** — 에이전트가 성공적인 커밋 후 종료

### 향상된 루프 예제

```bash
./loop.sh              # Build 모드, 무제한
./loop.sh 20           # Build 모드, 최대 20회 반복
./loop.sh plan         # Plan 모드, 무제한
./loop.sh plan 5       # Plan 모드, 최대 5회 반복
```

CLI 플래그:

- `-p`: 헤드리스 모드 (비대화형, stdin에서 읽음)
- `--dangerously-skip-permissions`: 모든 도구 호출 자동 승인
- `--model opus`: 기본 에이전트는 복잡한 추론에 Opus 사용
- `--verbose`: 상세 실행 로깅

### 향상된 loop.sh 스크립트

```bash
#!/bin/bash
# Usage: ./loop.sh [plan] [max_iterations]
# Examples:
#   ./loop.sh              # Build mode, unlimited iterations
#   ./loop.sh 20           # Build mode, max 20 iterations
#   ./loop.sh plan         # Plan mode, unlimited iterations
#   ./loop.sh plan 5       # Plan mode, max 5 iterations

# Parse arguments
if [ "$1" = "plan" ]; then
    MODE="plan"
    PROMPT_FILE="PROMPT_plan.md"
    MAX_ITERATIONS=${2:-0}
elif [[ "$1" =~ ^[0-9]+$ ]]; then
    MODE="build"
    PROMPT_FILE="PROMPT_build.md"
    MAX_ITERATIONS=$1
else
    MODE="build"
    PROMPT_FILE="PROMPT_build.md"
    MAX_ITERATIONS=0
fi

ITERATION=0
CURRENT_BRANCH=$(git branch --show-current)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Mode:   $MODE"
echo "Prompt: $PROMPT_FILE"
echo "Branch: $CURRENT_BRANCH"
[ $MAX_ITERATIONS -gt 0 ] && echo "Max:    $MAX_ITERATIONS iterations"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f "$PROMPT_FILE" ]; then
    echo "Error: $PROMPT_FILE not found"
    exit 1
fi

while true; do
    if [ $MAX_ITERATIONS -gt 0 ] && [ $ITERATION -ge $MAX_ITERATIONS ]; then
        echo "Reached max iterations: $MAX_ITERATIONS"
        break
    fi

    cat "$PROMPT_FILE" | claude -p \
        --dangerously-skip-permissions \
        --output-format=stream-json \
        --model opus \
        --verbose

    git push origin "$CURRENT_BRANCH" || {
        echo "Failed to push. Creating remote branch..."
        git push -u origin "$CURRENT_BRANCH"
    }

    ITERATION=$((ITERATION + 1))
    echo -e "\n\n======================== LOOP $ITERATION ========================\n"
done
```

---

## 파일 구조

```
project-root/
├── loop.sh                    # Ralph 루프 스크립트
├── PROMPT_build.md           # Build 모드 지시사항
├── PROMPT_plan.md            # Plan 모드 지시사항
├── AGENTS.md                 # 매 반복 로드되는 운영 가이드
├── IMPLEMENTATION_PLAN.md    # 우선순위 작업 목록 (Ralph가 생성/업데이트)
├── specs/                    # 요구사항 스펙 (JTBD 주제당 하나)
│   ├── [jtbd-topic-a].md
│   └── [jtbd-topic-b].md
├── src/                      # 애플리케이션 소스 코드
└── src/lib/                  # 공유 유틸리티 & 컴포넌트
```

### `AGENTS.md`

단일, 정식 "루프의 심장" — 간결한 운영 "빌드/실행 방법" 가이드.

- 변경 로그나 진행 일지가 **아님**
- 프로젝트 빌드/실행 방법을 기술
- 루프를 개선하는 운영 학습을 캡처
- **간결하게 유지 (~60줄)**
- 상태, 진행, 계획은 `IMPLEMENTATION_PLAN.md`에 속함

### `IMPLEMENTATION_PLAN.md`

스펙 대비 코드 갭 분석에서 도출된 우선순위 작업 목록 — Ralph가 생성.

- PLANNING 모드로 **생성**
- BUILDING 모드에서 **업데이트** (완료 표시, 발견 사항 추가, 버그 기록)
- **재생성 가능** — Geoff: "TODO 목록을 여러 번 삭제했다" → PLANNING 모드로 전환
- **자기 수정** — BUILDING 모드가 누락된 스펙도 생성 가능

순환성은 의도적: 반복을 통한 eventual consistency.

**미리 지정된 템플릿 없음** — Ralph/LLM이 자신에게 가장 잘 맞는 형식을 결정하고 관리하게 함.

### `specs/*`

관심 주제당 하나의 마크다운 파일. 무엇을 빌드해야 하는지의 **진실의 원천(source of truth)**.

- 요구사항 단계에서 생성 (인간 + LLM 대화)
- PLANNING과 BUILDING 모드 모두에서 소비
- 비일관성 발견 시 업데이트 가능 (드묾, 서브에이전트 사용)

---

## 프롬프트 템플릿

### PROMPT_plan.md 템플릿

```
0a. Study `specs/*` with up to 250 parallel Sonnet subagents to learn the application specifications.
0b. Study @IMPLEMENTATION_PLAN.md (if present) to understand the plan so far.
0c. Study `src/lib/*` with up to 250 parallel Sonnet subagents to understand shared utilities & components.
0d. For reference, the application source code is in `src/*`.

1. Study @IMPLEMENTATION_PLAN.md (if present; it may be incorrect) and use up to 500 Sonnet subagents to study existing source code in `src/*` and compare it against `specs/*`. Use an Opus subagent to analyze findings, prioritize tasks, and create/update @IMPLEMENTATION_PLAN.md as a bullet point list sorted in priority of items yet to be implemented. Ultrathink. Consider searching for TODO, minimal implementations, placeholders, skipped/flaky tests, and inconsistent patterns. Study @IMPLEMENTATION_PLAN.md to determine starting point for research and keep it up to date with items considered complete/incomplete using subagents.

IMPORTANT: Plan only. Do NOT implement anything. Do NOT assume functionality is missing; confirm with code search first. Treat `src/lib` as the project's standard library for shared utilities and components. Prefer consolidated, idiomatic implementations there over ad-hoc copies.

ULTIMATE GOAL: We want to achieve [project-specific goal]. Consider missing elements and plan accordingly. If an element is missing, search first to confirm it doesn't exist, then if needed author the specification at specs/FILENAME.md. If you create a new element then document the plan to implement it in @IMPLEMENTATION_PLAN.md using a subagent.
```

### PROMPT_build.md 템플릿

```
0a. Study `specs/*` with up to 500 parallel Sonnet subagents to learn the application specifications.
0b. Study @IMPLEMENTATION_PLAN.md.
0c. For reference, the application source code is in `src/*`.

1. Your task is to implement functionality per the specifications using parallel subagents. Follow @IMPLEMENTATION_PLAN.md and choose the most important item to address. Before making changes, search the codebase (don't assume not implemented) using Sonnet subagents. You may use up to 500 parallel Sonnet subagents for searches/reads and only 1 Sonnet subagent for build/tests. Use Opus subagents when complex reasoning is needed (debugging, architectural decisions).
2. After implementing functionality or resolving problems, run the tests for that unit of code that was improved. If functionality is missing then it's your job to add it as per the application specifications. Ultrathink.
3. When you discover issues, immediately update @IMPLEMENTATION_PLAN.md with your findings using a subagent. When resolved, update and remove the item.
4. When the tests pass, update @IMPLEMENTATION_PLAN.md, then `git add -A` then `git commit` with a message describing the changes. After the commit, `git push`.

99999. Important: When authoring documentation, capture the why — tests and implementation importance.
999999. Important: Single sources of truth, no migrations/adapters. If tests unrelated to your work fail, resolve them as part of the increment.
9999999. As soon as there are no build or test errors create a git tag. If there are no git tags start at 0.0.0 and increment patch by 1 for example 0.0.1 if 0.0.0 does not exist.
99999999. You may add extra logging if required to debug issues.
999999999. Keep @IMPLEMENTATION_PLAN.md current with learnings using a subagent — future work depends on this to avoid duplicating efforts. Update especially after finishing your turn.
9999999999. When you learn something new about how to run the application, update @AGENTS.md using a subagent but keep it brief.
99999999999. For any bugs you notice, resolve them or document them in @IMPLEMENTATION_PLAN.md using a subagent even if it is unrelated to the current piece of work.
999999999999. Implement functionality completely. Placeholders and stubs waste efforts and time redoing the same work.
9999999999999. When @IMPLEMENTATION_PLAN.md becomes large periodically clean out the items that are completed from the file using a subagent.
99999999999999. If you find inconsistencies in the specs/* then use an Opus 4.5 subagent with 'ultrathink' requested to update the specs.
999999999999999. IMPORTANT: Keep @AGENTS.md operational only — status updates and progress notes belong in `IMPLEMENTATION_PLAN.md`. A bloated AGENTS.md pollutes every future loop's context.
```

### 주요 언어 패턴 (Geoff의 구체적 표현)

- "**study**" ("read"나 "look at"이 아닌)
- "**don't assume not implemented**" (치명적 — 아킬레스건)
- "**using parallel subagents**" / "up to N subagents"
- "**only 1 subagent for build/tests**" (역압 제어)
- "**Ultrathink**" (이전의 "Think extra hard")
- "**capture the why**"
- "**keep it up to date**"
- "**if functionality is missing then it's your job to add it**"
- "**resolve them or document them**"

---

## 확장 제안 (Enhancement)

### 1. Claude의 AskUserQuestionTool을 Planning에 사용

- Phase 1에서 Claude의 내장 인터뷰 도구로 JTBD, 엣지 케이스, 수락 기준을 체계적으로 탐색
- 흐름: 알려진 정보로 시작 → Claude가 AskUserQuestion으로 인터뷰 → 명확해질 때까지 반복 → 수락 기준과 함께 스펙 작성

### 2. 수락 기준 기반 역압 (Acceptance-Driven Backpressure)

- 계획 단계에서 수락 기준으로부터 테스트 요구사항 도출
- "치팅" 방지 — 적절한 테스트 통과 없이 완료를 주장할 수 없음
- TDD 워크플로우 활성화
- 핵심 구분: **수락 기준**(행동적 결과) vs **테스트 요구사항**(검증 포인트) vs **구현 접근법**(Ralph에게 맡김)
- "**무엇을** 검증할지(결과) 지정, **어떻게** 구현할지(접근법)는 지정하지 않음"

### 3. 비결정적 역압 (Non-Deterministic Backpressure)

프로그래밍적 검증이 어려운 수락 기준에 대해:

- 창작 품질 — 글쓰기 톤, 서사 흐름, 몰입도
- 미학적 판단 — 시각적 조화, 디자인 균형, 브랜드 일관성
- UX 품질 — 직관적 내비게이션, 명확한 정보 계층
- 콘텐츠 적합성 — 맥락 인식 메시징, 대상 적합성

**해결책:** **LLM-as-Judge** 테스트를 바이너리 pass/fail 역압으로 추가

```typescript
interface ReviewResult {
  pass: boolean;
  feedback?: string; // pass=false일 때만 존재
}

function createReview(config: {
  criteria: string;    // 무엇을 평가할지 (행동적, 관찰 가능한)
  artifact: string;    // 텍스트 내용 또는 스크린샷 경로
  intelligence?: "fast" | "smart"; // 기본값 'fast'
}): Promise<ReviewResult>;
```

- **멀티모달 지원:** 텍스트와 스크린샷(비전) 모두 지원
- **지능 수준:** `fast` (빠르고 경제적) / `smart` (미묘한 미학/창작 판단)

### 4. Ralph 친화적 작업 브랜치

**핵심 원칙:** 런타임에 필터링이 아닌, 계획 생성 시점에 범위 지정

- ❌ **잘못된 접근:** 전체 계획 생성, 런타임에 "기능 X만 필터" 요청 → 신뢰성 70-80%
- ✅ **올바른 접근:** 브랜치별로 범위 지정된 계획을 미리 생성 → 결정론적, 단순

워크플로우:

```bash
# 1. 전체 계획 (main 브랜치)
./loop.sh plan

# 2. 작업 브랜치 생성
git checkout -b ralph/user-auth-oauth

# 3. 범위 지정 계획 (작업 브랜치)
./loop.sh plan-work "OAuth를 사용한 사용자 인증 시스템과 세션 관리"

# 4. 범위 지정된 계획에서 빌드
./loop.sh

# 5. PR 생성
gh pr create --base main --head ralph/user-auth-oauth --fill
```

### 5. JTBD → 스토리 맵 → SLC 릴리즈

**관심 주제를 활동(Activity)으로 재프레이밍:**

> 주제: "색상 추출", "레이아웃 엔진" → 기능 지향적
> 활동: "사진 업로드", "추출된 색상 보기", "레이아웃 배치" → 여정 지향적

**활동을 User Story Map으로 배열:**

```
UPLOAD    →   EXTRACT    →   ARRANGE     →   SHARE

basic         auto           manual          export
bulk          palette        templates       collab
batch         AI themes      auto-layout     embed
```

**수평 슬라이스로 SLC 릴리즈 생성:**

```
                  UPLOAD    →   EXTRACT    →   ARRANGE     →   SHARE

Palette Picker:   basic         auto                           export
                  ───────────────────────────────────────────────────
Mood Board:                     palette        manual
                  ───────────────────────────────────────────────────
Design Studio:    batch         AI themes      templates       embed
```

**SLC (Simple, Lovable, Complete) 기준:**

- **Simple** — 빠르게 출시할 수 있는 좁은 범위
- **Lovable** — 사람들이 실제로 사용하고 싶어하는
- **Complete** — 해당 범위 내에서 의미 있는 일을 완전히 수행

**왜 MVP 대신 SLC?** MVP는 고객을 희생해서 학습을 최적화. SLC는 이를 뒤집음: 실제 가치를 전달하면서 시장에서 학습.

---

## 주요 내용 정리

### 한눈에 보는 Ralph Playbook 구조

```
┌──────────────────────────────────────────────────────────────┐
│                   Ralph Playbook 요약                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Phase 1: 요구사항 정의                                       │
│  ┌─────────────────────────────────────────────┐             │
│  │ 인간 + LLM 대화                              │             │
│  │  → JTBD 식별                                 │             │
│  │  → 관심 주제 분해                             │             │
│  │  → specs/*.md 생성                           │             │
│  └─────────────────────────────────────────────┘             │
│              │                                               │
│              ▼                                               │
│  Phase 2: Planning 루프                                      │
│  ┌─────────────────────────────────────────────┐             │
│  │ while :; do cat PROMPT_plan.md | claude; done│             │
│  │  → 갭 분석 (specs vs code)                    │             │
│  │  → IMPLEMENTATION_PLAN.md 생성                │             │
│  │  → 구현 없음, 계획만                          │             │
│  └─────────────────────────────────────────────┘             │
│              │                                               │
│              ▼                                               │
│  Phase 3: Building 루프                                      │
│  ┌─────────────────────────────────────────────┐             │
│  │ while :; do cat PROMPT_build.md | claude; done│            │
│  │  → 가장 중요한 작업 선택                      │             │
│  │  → 서브에이전트로 조사 + 구현                  │             │
│  │  → 테스트/빌드로 검증 (역압)                  │             │
│  │  → 커밋 + 계획 업데이트                       │             │
│  │  → 컨텍스트 초기화 → 다음 반복                │             │
│  └─────────────────────────────────────────────┘             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 5대 핵심 원칙 요약

| #   | 원칙                 | 핵심 내용                                                          |
| --- | -------------------- | ------------------------------------------------------------------ |
| 1   | **컨텍스트가 전부**  | 176K 사용 가능, 40-60%가 스마트 존. 루프당 1작업으로 100% 활용     |
| 2   | **상류+하류 조종**   | 코드 패턴으로 상류 조종, 테스트/빌드로 하류 역압                   |
| 3   | **Let Ralph Ralph**  | 자기 식별, 자기 수정 능력을 신뢰. 반복으로 eventual consistency    |
| 4   | **루프 밖에서 관찰** | 루프 안이 아닌 위에서. 실패 패턴을 관찰하고 표지판 추가            |
| 5   | **계획은 일회용**    | 잘못되면 버리고 재생성. 비용은 Planning 루프 1회                   |

### 독특한 설계 결정

| 결정                                          | 이유                                                    |
| --------------------------------------------- | ------------------------------------------------------- |
| `IMPLEMENTATION_PLAN.md`를 디스크에 공유 상태로 | 반복 간 상태 전달의 유일한 메커니즘                      |
| 빌드/테스트에 서브에이전트 **1개만**           | 의도적 역압 — 검증 병목으로 품질 게이트                  |
| 탐색에 서브에이전트 **최대 500개**             | 코드베이스 이해 극대화, 메인 컨텍스트 보호               |
| Markdown > JSON                               | 토큰 효율성                                             |
| `AGENTS.md` ~60줄 제한                         | 매 루프 로드되므로 비대화 방지                           |
| 999... 번호 체계                               | 가드레일/불변량의 중요도 표현 (숫자가 클수록 중요)       |
