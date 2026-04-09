---
created: 2026-03-20
source: claude-code
tags: [ouroboros, workflow, claude-code, devops, trivy, automation]
---

# Ouroboros 워크플로우 전체 흐름

## 배경: Ouroboros란?

Ouroboros는 **요구사항 결정화 엔진(requirement crystallization engine)**으로, 막연한 아이디어를 검증된 사양서로 변환하는 AI 워크플로우입니다. 이름("뱀이 꼬리를 물다")이 암시하듯, **순환적 진화**가 핵심 철학입니다.

### 아키텍처: Skill + MCP 하이브리드

Ouroboros는 Skill(Plugin)과 MCP 두 계층으로 구성됩니다.

```
┌─ Skill (Plugin) 계층 ─────────────────────┐
│ interview, seed, unstuck, ralph, help      │
│ → 대화 오케스트레이션, UX, 프롬프트 생성    │
│ → MCP 없어도 기본 동작 가능 (Path B)       │
└────────────────────────────────────────────┘
        ↕ 호출
┌─ MCP 계층 ─────────────────────────────────┐
│ 20개 도구 (Python 백엔드)                   │
│ → 상태 저장, 수치 계산, 비동기 실행         │
│ → 정밀한 평가와 진화 루프 구동              │
└────────────────────────────────────────────┘
```

각 Skill 문서에 **Path A (MCP 있음)** / **Path B (MCP 없음, Plugin 전용)** 두 경로가 존재합니다. MCP가 많은 이유는 **세션 간 상태 영속성, 수치 기반 수렴 판정, 백그라운드 실행** 등이 Skill(프롬프트 기반)으로는 구현 불가능하기 때문입니다.

| MCP가 필요한 기능                            | 이유                                           |
| -------------------------------------------- | ---------------------------------------------- |
| 상태 영속성 (세션, 세대 이력, 라인리지)       | Python 백엔드 + SQLite DB에 영구 저장           |
| 수치 연산 (ambiguity score, drift, 수렴도)    | Python 코드로 정밀 계산                         |
| 3단계 평가 파이프라인                         | lint/build/test 등 외부 프로세스 실행 필요       |
| 백그라운드 실행 (start_execute_seed, job_*)   | 비동기 작업 큐                                  |
| 진화 되감기 (evolve_rewind)                   | DB에 저장된 스냅샷 필요                         |

비유: Skill = 자동차 핸들/페달 (운전자 인터페이스), MCP = 엔진/변속기 (실제 동력). 핸들만으로도 방향은 정할 수 있지만(Path B), 엔진이 있어야 실제로 달립니다(Path A).

---

## Core Workflow (선형 흐름)

최초 1회 실행하는 setup을 포함하여, 기본 흐름은 5단계입니다.

| 단계 | 명령어          | 설명                                                                         | 모드         | 현재 상태                             |
| ---- | --------------- | ---------------------------------------------------------------------------- | ------------ | ------------------------------------- |
| 0    | `ooo setup`     | MCP 서버 등록 (Python 3.14+ 자동 감지)                                       | Plugin       | **완료** (MCP 도구 20개 활성)         |
| 1    | `ooo interview` | 소크라틱 인터뷰로 숨겨진 가정을 노출하고 요구사항을 명확화                   | Plugin / MCP | **완료**                              |
| 2    | `ooo seed`      | 인터뷰 결과를 검증된 Seed 사양서(YAML)로 결정화                              | Plugin / MCP | **완료** (seed.yaml 존재, git 미추적) |
| 3    | **`ooo run`**   | Seed 사양서를 실행하여 실제 구현 (PAL 라우팅 적용)                           | MCP          | **← 다음 단계**                       |
| 4    | `ooo evaluate`  | 3단계 검증: 기계적(lint/build/test) → 의미적(AC 준수) → 합의(다중 모델 투표) | MCP          | 대기                                  |

> **참고**: `ooo run`은 `ooo setup`이 선행되어야 합니다 (seed 문서: "requires `ooo setup` first"). 현재 환경에서는 MCP 서버가 이미 활성화되어 있으므로 바로 진행 가능합니다.

비유하자면:

- **setup** = 자전거 안장 높이 맞추기 (최초 1회)
- **interview** = "어떤 집이 필요해?" 질문하기
- **seed** = 설계도면 그리기
- **run** = 실제로 벽돌 쌓기
- **evaluate** = 완공 후 검수

### run과 evaluate의 관계

"일단 한 번 돌려보자"가 `run` + `evaluate`이고, "수렴할 때까지 계속 개선해"가 `evolve`입니다. 단발성 실행-검증을 원할 때 수동으로 run → evaluate를 사용합니다.

---

## Evolutionary Loop (핵심 순환 구조)

Ouroboros의 진짜 힘은 **선형 실행이 아니라 진화적 반복**에 있습니다. `ooo evolve`를 호출하면 이 전체 루프가 자동으로 돌아갑니다.

```
Interview → Seed → Execute → Evaluate
    ↑                          ↓
    +---- evolve (세대 반복) ---+
```

### evolve의 세대별 흐름

```
Gen 1: Interview → Seed(O₁) → Execute → Evaluate
Gen 2: Wonder   → Reflect   → Seed(O₂) → Execute → Evaluate
Gen 3: Wonder   → Reflect   → Seed(O₃) → Execute → Evaluate
  ... (온톨로지 유사도 ≥ 0.95가 될 때까지, 최대 30세대)
```

**Gen 1만 Interview(사람과 Q&A)이고, Gen 2부터는 Wonder/Reflect로 대체됩니다.** 사람이 매번 개입하는 것이 아닙니다.

| 단계         | Gen 1                        | Gen 2+                                                    |
| ------------ | ---------------------------- | --------------------------------------------------------- |
| 요구사항 도출 | **Interview** (사람과 Q&A)   | **Wonder** ("아직 모르는 게 뭐지?")                        |
| 사양 개선     | Seed 생성                    | **Reflect** ("온톨로지를 어떻게 변이시킬까?") → Seed 진화  |
| 실행          | Execute                      | Execute                                                    |
| 검증          | Evaluate                     | Evaluate                                                   |

- **Wonder**: 평가 결과를 보고 온톨로지 갭과 숨겨진 가정을 식별
- **Reflect**: 필드, AC, 제약조건에 대한 구체적 변이(mutation)를 제안
- **Convergence**: 온톨로지 유사도 ≥ 0.95이면 수렴 완료
- **Rewind**: 각 세대가 스냅샷이므로 특정 세대로 되돌려 분기 가능

비유: 집을 짓는데,

- **Gen 1**: 건축주(사람)에게 "어떤 집 원해요?" 물어봄 → 설계 → 시공 → 검수
- **Gen 2+**: 검수 결과를 보고 **AI가 스스로** "지붕 단열이 부족하네, 창문 위치도 이상해" (Wonder) → "이렇게 고치자" (Reflect) → 재설계 → 재시공 → 재검수

### evolve의 종료 상태

`evolve_step` 응답의 `action` 필드:

| action      | 의미                    | 다음 행동                 |
| ----------- | ----------------------- | ------------------------- |
| `continue`  | 아직 수렴 안 됨         | evolve_step을 다시 호출    |
| `converged` | 온톨로지 유사도 ≥ 0.95  | 완료! 최종 온톨로지 표시   |
| `stagnated` | 3세대 연속 변화 없음     | `lateral_think` 사용 고려  |
| `exhausted` | 최대 30세대 도달         | 최선의 결과 표시           |
| `failed`    | 오류 발생                | 에러 확인 후 재시도        |

### evolve가 "보조"가 아닌 이유

전체 20개 MCP 도구 중 evolve 전용이 **5개(25%)**를 차지합니다:

| 도구                          | 역할                 |
| ----------------------------- | -------------------- |
| `ouroboros_evolve_step`       | 1세대 실행           |
| `ouroboros_start_evolve_step` | 백그라운드 실행      |
| `ouroboros_evolve_rewind`     | 특정 세대로 되감기   |
| `ouroboros_lineage_status`    | 계보(세대 이력) 조회 |
| `ouroboros_ac_dashboard`      | AC 준수 대시보드     |

---

## ralph — "검증 통과까지 자율 반복"

ralph는 Evolutionary Loop와는 **다른 종류의 루프**입니다.

```
while iteration < max_iterations (기본 10):
    1. Execute  → 병렬로 작업 실행
    2. Verify   → 완료 확인, 테스트 통과, 드리프트 측정
    3. 실패 시  → 실패 분석 → 수정 → 1번으로
    4. 성공 시  → 종료
```

**사람과 토론하는 단계가 전혀 없습니다.** "바위를 멈추지 마(The boulder never stops)" — 검증 통과할 때까지 AI가 혼자 계속 돌립니다.

### evolve vs ralph

| 구분       | evolve                               | ralph                                |
| ---------- | ------------------------------------ | ------------------------------------ |
| 목적       | **사양(Seed) 자체를 진화**시킴        | **주어진 작업을 완료**할 때까지 반복  |
| 루프 대상  | 온톨로지, AC, 제약조건                | 코드 실행, 테스트, 빌드              |
| 사람 개입  | Gen 1에서만 (Interview)               | **없음** — 완전 자율                 |
| 종료 조건  | 온톨로지 수렴 (유사도 ≥ 0.95)         | 검증 통과 또는 max_iterations        |
| 비유       | 설계도를 계속 개선                    | 시공 중 하자 나오면 계속 고침         |

### ralph 사용 예시

```
User: ooo ralph fix all failing tests

[Ralph Iteration 1/10] → 3개 테스트 실패 → 수정 시도
[Ralph Iteration 2/10] → 1개 테스트 실패 → 수정 시도
[Ralph Iteration 3/10] → 전부 통과 → COMPLETE!
```

중간에 세션이 끊겨도 `.omc/state/ralph-state.json`에 상태가 저장되어 `ralph continue`로 재개 가능합니다.

| 명령어       | 설명                                       | 모드         |
| ------------ | ------------------------------------------ | ------------ |
| `ooo evolve` | 진화적 개발 루프 시작/모니터링              | MCP          |
| `ooo ralph`  | "멈추지 마" — 검증 통과까지 자율 반복 실행  | Plugin + MCP |

---

## unstuck — 막혔을 때의 관점 전환

막혔을 때 5가지 사고 페르소나 중 하나를 불러서 **다른 관점으로 문제를 바라보게** 해줍니다.

| 페르소나       | 스타일                                     | 언제 사용                      |
| -------------- | ------------------------------------------ | ------------------------------ |
| **hacker**     | "일단 돌아가게 만들어, 우아함은 나중에"     | 과도한 분석으로 진행이 안 될 때 |
| **researcher** | "어떤 정보가 빠져있지?"                     | 문제 자체가 불분명할 때         |
| **simplifier** | "스코프를 줄여, MVP로 돌아가"               | 복잡성에 압도당할 때            |
| **architect**  | "접근 방식을 완전히 재구조화해"             | 현재 설계가 잘못됐을 때         |
| **contrarian** | "우리가 잘못된 문제를 풀고 있는 건 아닌가?" | 가정 자체를 의심해야 할 때      |

### 자동 선택 로직

- 비슷한 실패 반복 → contrarian
- 선택지가 너무 많음 → simplifier
- 정보 부족 → researcher
- 분석 마비 → hacker
- 구조적 문제 → architect

### evolve와의 연계

evolve 루프에서 `stagnated` (3세대 연속 변화 없음) 상태가 되면 `ouroboros_lateral_think`(unstuck의 MCP 도구) 사용을 제안합니다.

비유: 수학 문제를 풀다 막혔을 때,

- hacker = "답이 대충이라도 나오게 숫자 넣어봐"
- researcher = "교과서를 다시 읽어봐"
- simplifier = "이 문제 5단계 중 1단계만 먼저 풀어봐"
- architect = "풀이 방법을 완전히 바꿔봐"
- contrarian = "이 문제를 풀어야 하는 게 맞아?"

---

## Utility 도구와 워크플로우 내 호출 시점

### 유틸리티 MCP 도구

| 도구                      | 역할                                                                                      | 자동 호출?      | 호출 시점                                          |
| ------------------------- | ----------------------------------------------------------------------------------------- | --------------- | -------------------------------------------------- |
| `ouroboros_qa`            | 반복 루프 내 경량 품질 검증 (evaluate와 구분: qa는 경량 반복용, evaluate는 3단계 최종 판정) | **자동**        | `execute_seed` 매 iteration (`skip_qa` 기본 false)  |
| `ouroboros_measure_drift` | 목표 이탈 측정 (goal 50%, constraint 30%, ontology 20%)                                   | **자동**        | evolve/ralph의 Verify 단계                          |
| `ouroboros_lateral_think` | 5개 페르소나를 통한 대안적 사고 생성                                                      | **수동/조건부** | `ooo unstuck` 호출 시 또는 evolve stagnated 시       |

### 보조 명령어

| 명령어        | 설명                                                                                | 모드   |
| ------------- | ----------------------------------------------------------------------------------- | ------ |
| `ooo status`  | 세션 상태 확인 + 목표 드리프트 체크                                                  | MCP    |
| `ooo unstuck` | 5가지 사고 페르소나로 돌파 (hacker, researcher, simplifier, architect, contrarian)    | Plugin |

### qa vs evaluate의 차이

| 속성       | `ouroboros_qa`                       | `ouroboros_evaluate`                     |
| ---------- | ------------------------------------ | ---------------------------------------- |
| 목적       | 반복 루프 내 경량 품질 검증           | 최종 3단계 판정                           |
| 세션 연결  | 선택적                               | 필수 (session_id)                         |
| 파이프라인 | 단일 판정                            | Stage 1 기계적 → Stage 2 의미적 → Stage 3 합의 |
| 용도       | "Designed for iterative loop usage"  | AC 준수, 목표 정렬 최종 확인               |

---

## 전체 MCP 도구 분류 (20개)

| 카테고리         | 도구                                                                                                            | 개수 |
| ---------------- | --------------------------------------------------------------------------------------------------------------- | ---- |
| Core Workflow    | interview, generate_seed, execute_seed, evaluate                                                                | 4    |
| Evolve           | evolve_step, start_evolve_step, evolve_rewind, lineage_status, ac_dashboard                                     | 5    |
| Job/Session 관리 | start_execute_seed, job_status, job_wait, job_result, cancel_job, cancel_execution, session_status, query_events | 8    |
| Utility          | measure_drift, lateral_think, qa                                                                                | 3    |

---

## 현재 프로젝트 상태 요약

| 항목            | 상태                                                | 비고                                               |
| --------------- | --------------------------------------------------- | -------------------------------------------------- |
| Seed 파일       | `docs/trivy-auto-remediation-seed.yaml` 존재         | git 미추적 (untracked)                              |
| Handoff 노트    | `docs/trivy-auto-remediation-handoff.md` 존재        | git 미추적                                          |
| Ambiguity Score | 0.15 (기준 <= 0.2 충족)                              | Seed 구조 유효                                      |
| 미결 설계 이슈  | 3건 (Race Condition, PR 분리/통합, Breaking Change)   | seed constraints에 인지 반영됨, 구현 단계에서 해결   |

---

## 핵심 정리

1. **기본 순서**: setup(0회) → interview → seed → run → evaluate — 이 선형 흐름 자체는 정확
2. **setup 필수**: `ooo run` 실행 전 `ooo setup`으로 MCP 서버 등록이 선행되어야 함
3. **evolve는 핵심**: 전용 도구 5개(25%), Ouroboros의 존재 이유인 순환적 진화를 담당
4. **Gen 1만 Interview**: Gen 2부터는 Wonder/Reflect로 대체되어 사람 개입 없이 AI가 자율 진화
5. **ralph ≠ evolve**: ralph는 "작업 완료까지 반복"(코드 수정), evolve는 "사양 수렴까지 반복"(온톨로지 진화)
6. **unstuck = 관점 전환**: 5가지 페르소나로 막힌 상황을 돌파, evolve stagnated 시 자동 연계
7. **유틸리티 자동 호출**: qa는 execute_seed 내 자동, measure_drift는 evolve/ralph verify 단계 자동, lateral_think은 수동/조건부
8. **MCP가 많은 이유**: 상태 영속성, 수치 계산, 백그라운드 실행은 Skill로 불가능 — Skill은 UI, MCP는 엔진
9. **다음 단계**: `/ouroboros:run docs/trivy-auto-remediation-seed.yaml`로 Seed 실행
10. **페달은 계속 돌려야 한다**: 한 번 run→evaluate로 끝이 아니라, evolve로 세대를 반복하며 개선하는 것이 Ouroboros의 진짜 사용법
