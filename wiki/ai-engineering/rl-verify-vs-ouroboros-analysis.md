---
created: 2026-03-21
source: claude-code
tags: [ouroboros, rl-verify, ontology, convergence, ai-tools, specification-first]
---

# rl-verify vs Ouroboros 비교 분석 및 Ouroboros 온톨로지 심층 탐구 (검증 반영판)

> 본 문서는 rl-verify 수렴 검증(Tier 2, 4회 iteration, 14개 발견사항 수렴)을 거쳐 정정된 버전입니다.
> 검증 리포트: `verify-rl-verify-vs-ouroboros/report.md`
>
> 2차 검증: QA 답변 16개에 대한 rl-verify 수렴 검증(Tier 2, RESEARCHER/CONTRARIAN/EVALUATOR). 12개 CONFIRMED, 4개 수정 반영.

## 배경: 두 도구의 정체

### rl-verify — 수렴 검증기

`/rl-verify`는 **기존 산출물(문서, 코드, 플랜)을 다각도로 검증**하는 스킬이다.

- **입력**: 기존 문서/코드/아이디어
- **출력**: `plan.md` (검증 플랜) + `report.md` (검증 리포트)
- **핵심 메커니즘**: 여러 전문 agent가 각자 관점에서 검토 → EVALUATOR가 종합 판정 → 안정 카운터로 수렴 추적

**Tier 시스템으로 복잡도에 따라 검증 깊이를 조절한다:**

| Tier               | 조건                              | 최소 관점 | 필수 역할                          |
| ------------------- | --------------------------------- | --------- | ---------------------------------- |
| Tier 1 (경량)       | 단일 파일, 영향 제한적            | 2개       | CONTRARIAN, EVALUATOR              |
| Tier 2 (표준)       | 여러 파일, 중간 영향              | 3개       | CONTRARIAN, EVALUATOR              |
| Tier 3 (심층)       | 시스템 전체, 되돌리기 어려움      | 4개       | CONTRARIAN, EVALUATOR, RESEARCHER  |

**판정 라벨 체계:**

| 라벨       | 조건                                           |
| ---------- | ---------------------------------------------- |
| CONFIRMED  | 다수 agent 동의 + 외부 근거 존재               |
| LIKELY     | 다수 agent 동의, 외부 근거 미확인              |
| CONTESTED  | Agent 간 의견 분열                             |
| REFUTED    | 다수 agent 반대 또는 외부 근거가 반박          |
| UNGROUNDED | 외부 검증 불가 + 자기 참조만 존재              |

**동적 agent 할당**: 보안 감사 → `security-sentinel`, 성능 → `performance-oracle`, Rails 코드 → `dhh-rails-reviewer` 등 도메인에 맞는 전문 agent를 자동 조합한다.

**rl-verify의 구조적 한계** (검증에서 발견):

- **프레이밍 의존성**: Phase 1에서 작업 유형을 3가지(문서검증/코드리뷰/리서치)로 판별하는데, 초기 프레이밍이 잘못되면 전체 검증이 잘못된 방향으로 수렴할 수 있다
- **echo chamber 위험**: 실행 Phase는 단일 모델(`claude-opus-4-6`)이므로 위험이 있으나, 평가 Phase(Stage 3 Consensus)는 3개 서로 다른 모델(GPT-4o, Claude Opus, Gemini 2.5 Pro)을 사용하고, 정체 탈출은 5가지 페르소나로 동작하므로 전체 시스템이 echo chamber라고 할 수는 없다. Phase별 구분이 필요하다
- **정체 대응 부재**: rl-verify에는 ouroboros의 unstuck/lateral thinking 같은 "검증 프레임 자체가 틀렸을 수 있다"는 메타 반성 메커니즘이 없다

### Ouroboros — 명세 우선 AI 워크플로우 엔진

Ouroboros는 **모호한 아이디어를 명확한 명세로 변환하고, 반복적으로 진화시키는** 도구이다.

```
Interview → Seed → Execute → Evaluate
    ↑                           ↓
    └─── Evolutionary Loop ─────┘
```

- **Interview**: 소크라테스식 질문으로 요구사항 명확화 (ambiguity ≤ 0.2)
- **Seed**: 구조화된 명세 생성 (YAML — goal, constraints, acceptance_criteria, ontology_schema)
- **Evolve**: 반복 루프 — Wonder("뭘 모르나?") → Reflect("어떻게 바꿀까?") → 새 Seed → Execute → Evaluate
- **Ralph**: 실행-검증-재시도의 자체 수렴 검증 루프 (max 10회, score 기반)
- **Unstuck/Lateral Thinking**: 정체 감지 시 5개 페르소나(hacker, researcher, simplifier, architect, contrarian) 전환으로 돌파
- **Rewind**: 특정 세대로 되돌아가 진화를 분기(branch)

---

## 핵심 비교: rl-verify vs Ouroboros

### 비유

- **Ouroboros (interview → seed → evolve)** = **건축가**: "어떤 집을 지을까?" 질문하고, 설계도를 그리고, 반복적으로 설계를 개선
- **rl-verify** = **건축 감리사**: 이미 그려진 설계도나 지어진 집을 검사하고, 여러 전문가(구조, 전기, 소방)가 각자 관점에서 결함을 찾음

### 상세 비교

| 차원           | ouroboros                                                     | rl-verify                                             |
| -------------- | ------------------------------------------------------------- | ----------------------------------------------------- |
| **목적**       | 무엇을 만들지 명확히 → 만들기                                 | 이미 있는 것이 맞는지 검증                            |
| **입력**       | 모호한 아이디어                                               | 기존 문서/코드/플랜                                   |
| **출력**       | Seed YAML (설계 명세)                                         | 검증 리포트 (발견사항 + 판정)                         |
| **수렴 대상**  | 온톨로지 유사도 ≥ 0.95                                        | 발견사항의 안정 카운터 ≥ 2~3                          |
| **Agent 구성** | 고정 (socratic-interviewer → seed-architect → evaluator)      | **동적** (도메인에 맞는 agent 자동 할당)              |
| **반론 메커니즘** | evolve의 Wonder ("뭘 모르는가?")                            | CONTRARIAN 필수 + CONTESTED 시 제3 관점 투입          |
| **자체 검증**  | ralph (반복 검증 루프), convergence gates                     | 안정 카운터 + EVALUATOR 판정                          |
| **정체 대응**  | unstuck/lateral thinking (5개 페르소나)                       | 없음                                                  |
| **되돌리기**   | rewind (세대 분기)                                            | 아카이브 후 재시작만 가능                             |

### 기능 중복이 있으나 관점이 다른 보완 조합

> **검증 결과**: "대체 불가"라는 원래 주장은 **UNGROUNDED**(근거 부재) 판정을 받았다. ouroboros 자체에 ralph(검증 루프), convergence gates(eval_gate, ac_gate, regression_gate), unstuck(정체 탈출) 등 풍부한 자체 검증 메커니즘이 존재한다. 따라서 정확한 표현은 **"ouroboros도 자체 수렴 검증이 가능하며, rl-verify는 추가적 검증 레이어를 제공한다"**이다.

**ouroboros에만 있는 것:**

1. 모호한 아이디어에서 명확한 스펙 생성 (ambiguity ≤ 0.2)
2. 온톨로지 진화 (데이터 모델 자체를 반복 개선)
3. 실제 코드 실행 + 평가 루프 (Execute → Evaluate)
4. Rewind/Branch (특정 세대로 돌아가 분기)
5. Unstuck/Lateral thinking (정체 시 페르소나 전환)

**rl-verify에만 있는 것:**

1. **도메인 특화 agent 자동 할당** — 기존 에코시스템의 전문 agent를 동적으로 조합
2. **정형화된 판정 라벨** — CONFIRMED / LIKELY / CONTESTED / REFUTED / UNGROUNDED
3. **안정 카운터 + Tier 시스템** — 복잡도에 따라 수렴 기준이 달라지는 구조
4. **CONTESTED → 제3 관점 자동 투입** — 의견 충돌 시 새로운 전문가를 자동으로 추가

**기능 중복 영역:**

- 반복 검증 루프 (ralph ↔ 수렴 루프) — 다만 rl-verify의 다관점 합의 메커니즘이 더 정교
- EVALUATOR 역할 (ouroboros:evaluator ↔ rl-verify EVALUATOR)
- CONTRARIAN 역할 (ouroboros:contrarian ↔ rl-verify CONTRARIAN)

---

## Ouroboros 온톨로지 심층 분석

### 온톨로지란?

**온톨로지 = "이 프로젝트가 다루는 데이터의 구조 정의"**

> **검증 결과**: "온톨로지 = DDD Entity"라는 비유는 **REFUTED**(반박됨) 판정을 받았다. OntologySchema는 `frozen=True`인 평면적(flat) Pydantic 모델로, DDD Entity의 핵심 조건(identity, behavior, invariant, lifecycle)을 전혀 충족하지 않는다. **DTO(Data Transfer Object) 또는 Value Object에 가깝고, "의미 주석이 달린 JSON Schema(JSON Schema with semantic annotation)"라고 보는 것이 더 정확하다.**

코드로 보면:

```python
class OntologySchema(BaseModel, frozen=True):
    name: str = Field(..., min_length=1)        # 예: "TaskManager"
    description: str = Field(..., min_length=1)  # 예: "Task management domain model"
    fields: tuple[OntologyField, ...] = Field(default_factory=tuple)  # 기본값: 빈 tuple

class OntologyField(BaseModel, frozen=True):
    name: str          # 예: "title"
    field_type: str    # 예: "string"
    description: str   # 예: "Task title"
    required: bool     # 필수 여부
```

소프트웨어는 현실 세계를 데이터로 표현하고, 비즈니스 로직이 이 데이터를 조작해서 요구사항을 만족시킨다. 따라서 데이터 구조가 바뀐다는 것은 현실 세계에 대한 이해가 바뀐 것이고, 안 바뀐다는 것은 이해가 안정된 것이다. **온톨로지가 수렴한다 = "이 도메인을 표현하는 데 필요한 개념을 더 이상 새로 발견하지 못했다"**

비유하면 지도 제작자가 탐험하면서 지도를 그리다가 더 이상 새로운 지형이 안 나오면 지도가 완성된 것이다.

### 유사도 계산의 원리와 한계

두 세대의 온톨로지를 나란히 놓고 "얼마나 비슷한가?"를 숫자로 매기는 것이다.

```
유사도 = 0.5 × 이름점수 + 0.3 × 타입점수 + 0.2 × 완전일치점수
```

| 가중치  | 비교 대상      | 의미                                         |
| ------- | -------------- | -------------------------------------------- |
| **50%** | 이름 존재 여부 | 같은 이름의 필드가 양쪽에 있는가?            |
| **30%** | 타입 일치      | 같은 이름 + 같은 타입(string, array 등)인가? |
| **20%** | 완전 일치      | 이름 + 타입 + 설명까지 모두 같은가?          |

**구체적 예시:**

Gen 2: `title(string:"할 일 제목")`, `status(string:"완료 여부")`
Gen 3: `title(string:"할 일 제목")`, `status(string:"진행 상태")`, `priority(integer:"우선순위")`

```
전체 필드 집합 = {title, status, priority} → 3개
이름점수 = 2/3 = 0.667
타입점수 = 2/3 = 0.667
완전일치 = 1/3 = 0.333

유사도 = 0.5×0.667 + 0.3×0.667 + 0.2×0.333 = 0.600
```

**0.600 < 0.95** → 아직 수렴 안 됨, 계속 진화!

**유사도 계산의 한계** (검증에서 발견):

- **필드 간 관계 미포착**: "Task가 Tag를 참조한다"와 같은 관계성(foreign key, composition)은 이름/타입만으로 포착 불가
- **중첩 구조 미포착**: flat 필드 목록만 비교하므로 중첩 객체의 변화를 놓칠 수 있음
- **의미론적 동치 미인식**: `user_name` → `username`은 불일치로 판정되지만 의미적으로 동일. 반대로, `status`의 의미가 바뀌어도 이름이 같으면 일치로 판정

---

## 온톨로지의 생성과 수정 시점

### 최초 생성: Interview → Seed (Gen 1)

```
사용자: "할 일 관리 CLI 만들어줘"
  ↓
Interview: "할 일에 어떤 속성이 필요해요?" "태그 기능은요?" "마감일은?"
  ↓
Seed 생성 시 ontology_schema가 포함됨
```

### 수정: Evolve 루프 (Gen 2+에서 진화)

Seed(목표, 제약)는 불변이지만, 온톨로지는 세대를 거치며 진화한다:

```
Gen 1: Interview → Seed(O₁) → Execute → Evaluate
Gen 2: Wonder → Reflect → Seed(O₂) → Execute → Evaluate
Gen 3: Wonder → Reflect → Seed(O₃) → Execute → Evaluate
```

#### Wonder — "우리가 아직 모르는 게 뭐지?"

**LLM(claude-opus-4-6, temperature=0.7)에게 물어서** 질문을 생성한다. 현재 온톨로지 + 평가 결과 + 실행 결과 + 진화 이력을 입력으로 받는다. 시스템 프롬프트 핵심: **구현 질문(어떻게 코딩할까?)이 아닌 온톨로지 질문(이것이 무엇인가?)에 집중하라.**

LLM 호출이 실패하면 규칙 기반 폴백(degraded mode)으로 질문을 생성한다.

#### Reflect — "온톨로지를 어떻게 바꿀까?"

Wonder의 질문에 답하면서 구체적인 변경(mutation)을 제안한다:

```python
class OntologyMutation(BaseModel):
    action: MutationAction    # ADD, MODIFY, REMOVE
    field_name: str           # "priority"
    field_type: str | None    # "integer"
    reason: str               # "정렬 기능에 필요"
```

### 레고 비유로 보는 전체 진화 과정

```
Gen 1: 부품 목록 = [빨강, 파랑]
       → 조립해봄 → "바퀴가 없어서 굴러가질 않네?"

Gen 2: Wonder: "바퀴가 필요한 거 아냐?"
       Reflect: ADD wheel
       → 부품 목록에 바퀴 추가 → 다시 조립

Gen 3: Wonder: "축이 없으면 바퀴가 안 달리잖아?"
       Reflect: ADD axle
       → 부품 목록에 축 추가 → 다시 조립

Gen 4: Wonder: "이제 다 맞는 것 같은데?"
       Reflect: 변경 없음 → 유사도 0.98 → 수렴! 종료
```

---

## 수렴 판정과 안전장치

### eval_gate는 실행 시 기본 ON

> **검증 결과**: 원래 "eval_gate가 기본으로 꺼져있다"고 했으나 이는 **부분적 오류**다. `ConvergenceCriteria` 클래스 수준의 기본값은 `False`이지만, 실제 실행 경로에서 `EvolutionaryLoopConfig`이 `True`로 override하여 전달한다. **따라서 `ooo evolve`를 별도 설정 없이 실행하면 eval_gate는 켜져 있다.**

비유하면, 자동차 엔진 자체에는 "시동 끔"이 기본이지만, 자동차 키를 꽂으면 "시동 켬"으로 override된다. 사용자가 차에 타면 시동이 걸린다.

### 온톨로지 수렴 ≥ 0.95이더라도 차단하는 5가지 게이트

1. **eval_gate** (실행 시 기본 ON) — 평가 점수가 기준(0.7) 미만이면 수렴 차단
2. **ac_gate** — 개별 AC(수락 기준)가 실패하면 수렴 차단 (mode: "all" 또는 "ratio")
3. **regression_gate** (기본 ON) — 이전에 통과했던 AC가 실패하면 차단
4. **false convergence gate** — 한 번도 온톨로지가 변한 적 없으면 차단 (Wonder/Reflect 실패일 수 있음)
5. **oscillation detection** — A→B→A→B 반복이면 강제 종료

### 테스트 통과 확인 과정

Phase 4 Evaluation의 3단계 파이프라인에서 테스트를 실행한다:

```
Stage 1: Mechanical ($0)  — lint, build, test 실행, 커버리지 70%
Stage 2: Semantic ($$)    — AC 준수 여부, 목표 일치도, drift
Stage 3: Consensus ($$$)  — 다중 모델 투표 (선택적)
```

eval_gate가 기본으로 켜져 있으므로, **실행 시 기본 동작에서 온톨로지 수렴 + 평가 통과 모두를 요구한다.**

---

## 성능 개선에 ouroboros를 쓸 수 있는가?

**가능하다.** ouroboros는 brownfield(기존 코드베이스) 모드를 지원한다.

**그러나** 성능 개선은 ouroboros의 "sweet spot"이 아니다. brownfield 지원은 기존 코드의 "구조와 패턴을 이해"하기 위한 컨텍스트 수집용이지, 프로파일링 데이터를 분석하거나 벤치마크를 실행하는 것이 아니다. 성능 개선은 "프로파일링 → 병목 찾기 → 고치기"라는 명확한 프로세스가 있어서, 소크라테스식 탐색이 꼭 필요하진 않다.

---

## AI 자율주행 개발의 현실

### 왜 "한 번에 완성"이 아직 신뢰하기 어려운가

> **검증 결과**: "불가능"은 과도한 표현이라는 LIKELY 판정. ouroboros 자체가 AI 자율 진화 루프(seed → execute → evaluate → evolve)를 구현하고 있으므로, "불가능"보다는 **"문제 정의의 자율성이 아직 신뢰할 수 없다"**가 더 정확하다.

```
1. 요구사항 자체가 불완전하다
   → 사용자 본인도 뭘 원하는지 정확히 모름
   → 써봐야 "이건 아닌데"를 알게 됨

2. 복잡도가 비선형으로 증가한다
   → 기능 10개짜리 앱은 기능 5개짜리의 2배가 아니라
     5배~10배 복잡함 (기능 간 상호작용)

3. 맥락이 중요하다
   → AI가 코드를 생성할 수 있지만,
     "이 팀은 이런 패턴을 쓴다" 같은 암묵지를 모름
```

자동차 비유로 구분하면: ouroboros는 "목적지를 인간이 정하고 경로는 AI가 결정하는" Level 3 자율주행이다. 현재 어려운 것은 "목적지까지 AI가 정하는" Level 5다.

### 현실적인 워크플로우

원래 문서의 워크플로우에서 seed, evaluate, drift 단계가 누락되어 있었다. 현실적인 워크플로우:

```
ouroboros interview → 요구사항 명확화
  ↓
ooo seed → 명세 구조화 (YAML)
  ↓
[선택] ooo evolve → 온톨로지 수렴까지 명세 진화
  ↓
기능별 점진 구현
  ↓
ooo evaluate → 각 기능 3단계 검증
  ↓
ooo status → goal drift 확인
  ↓
[필요시] rl-verify → 최종 산출물 다관점 수렴 검증
  ↓
사용자 확인
```

AI는 **각 단계에서의 강력한 도우미**이지 **자율주행 운전자**가 아니다. 점진적 개발이 현실적으로 가장 효과적이며, 내부 점진성(seed evolve — 하나의 seed 안에서의 품질 수렴)과 외부 점진성(전체 시스템을 어떤 순서로 개발할 것인가)은 **다른 층위의 관심사**다.

---

## Ouroboros 심화 Q&A (rl-verify 검증 완료)

> 2차 rl-verify 수렴 검증(Tier 2, 3관점): 16개 답변 중 12개 CONFIRMED, 4개 수정 반영

### rl-verify의 구조적 한계 상세

**프레이밍 의존성**: 병원 접수대에서 "내과"로 분류했는데 실제는 정형외과인 것과 같다. Phase 1에서 작업 유형(문서검증/코드리뷰/리서치)을 잘못 판별하면, 이후 아무리 철저히 검증해도 잘못된 방향으로 수렴한다.

**Echo Chamber**: 같은 LLM의 편향이 반복되는 현상. 단, 실행 Phase(단일 모델)와 평가 Phase(다중 모델), 정체 탈출(다중 페르소나)을 구분해야 한다.

**정체 대응 부재**: ouroboros의 CONTRARIAN은 "잘못된 문제를 풀고 있는 건 아닌가?"라는 메타 질문을 던지지만, rl-verify는 주어진 프레임 안에서만 수렴을 추구한다.

### Ralph vs Evolve

| 차이점     | Ralph                          | Evolve                              |
| ---------- | ------------------------------ | ----------------------------------- |
| **바뀌는 것** | 실행 방법                      | 명세(온톨로지) 자체                 |
| **목표**   | 테스트를 통과시키자            | 뭘 만들어야 하는지 파악하자         |
| **최대 반복** | 10회                           | 30세대                              |
| **수렴 기준** | 검증 통과                      | 온톨로지 유사도 ≥ 0.95             |
| **정체 감지** | ❌ 없음 (단순 반복 설계)       | ✅ 있음 (stagnation → lateral_think 권고) |

비유: Ralph = 레시피대로 반복 시도, Evolve = 레시피 자체를 진화.

### Unstuck/Lateral Thinking 동작 방식

4가지 정체 패턴(Spinning, Oscillation, No Drift, Diminishing Returns)을 감지하면 5개 페르소나 중 적합한 것을 선택한다. 각 페르소나는 **복수의 패턴에 친화성**을 가진다(다대다 관계):

| 페르소나   | 친화 패턴                       |
| ---------- | ------------------------------- |
| HACKER     | Spinning                        |
| RESEARCHER | No Drift, Diminishing Returns   |
| SIMPLIFIER | Diminishing Returns, Oscillation |
| ARCHITECT  | Oscillation, No Drift           |
| CONTRARIAN | 모든 4가지 패턴                 |

⚠️ **검증 정정**: Evolve에서 정체 감지 시 lateral thinking은 "자동 트리거"가 아니라 SKILL.md가 "권고(Consider)"하는 수준이다. 내비게이션이 "정체 구간입니다, 우회 경로를 검색하시겠습니까?" 알림을 띄우는 것에 가깝다.

### Rewind = 게임 세이브 포인트

특정 세대로 되돌아가 다른 방향으로 진화를 분기할 수 있다. `rewind_to()`는 지정 세대까지 truncate하고 status를 ACTIVE로 설정하여 재진화 가능 상태로 만든다.

### Gate = 수렴을 인정하기 전 통과해야 하는 관문

온톨로지가 수렴(≥0.95)해도 각 gate에서 실패하면 루프가 계속 돌며 Wonder/Reflect/Execute로 수정 과정을 거친다. 졸업 요건과 같다 — 학점이 4.0이어도 졸업 논문을 안 냈으면 졸업 불가.

### 소크라테스식 탐색

답을 주는 대신 질문을 던져서 사용자 자신도 모르던 요구사항을 드러나게 하는 방법. ouroboros interview의 핵심 규칙: 항상 질문으로 끝남, 가장 모호한 부분을 타겟, 코드를 쓰지 않음, ambiguity ≤ 0.2까지 계속.

### ooo evaluate 3단계 상세

| Stage                | 비용 | 방법                                   | 핵심                                   |
| -------------------- | ---- | -------------------------------------- | -------------------------------------- |
| Stage 1: Mechanical  | $0   | `uv run ruff/pytest/mypy` 자동 체크    | 커버리지 70% 필수                      |
| Stage 2: Semantic    | $$   | claude-opus-4-6 (temp=0.2)             | AC 준수, 목표 정렬, drift 측정         |
| Stage 3: Consensus   | $$$  | GPT-4o + Claude + Gemini 투표          | drift>0.3 시 자동 트리거, 2/3 다수결   |

### Goal Drift = 원래 목표에서의 이탈도

`combined_drift = goal×0.5 + constraint×0.3 + ontology×0.2`

- 0.0~0.15: ✅ Excellent
- 0.15~0.30: 🟡 Acceptable
- 0.30+: ❌ Exceeded → Consensus 검토 필요

### 기능별 점진 구현

⚠️ **검증 정정**: `ooo run`은 "seed 실행기"이지 "기능 분할기"가 아니다. 설계 의도에 가까운 사용법은 **하나의 seed에 모든 AC를 넣고 한 번의 run으로 실행** → Double Diamond이 AC를 자동 분해하여 병렬 실행.

### 내부 점진성 vs 외부 점진성

- **외부 점진성**: "이번 달에 로그인, 다음 달에 결제" — 전략적 순서 결정 (사람의 판단 영역)
- **내부 점진성**: 하나의 seed 안에서 Gen1→Gen2→Gen3→수렴 — ouroboros 자동 처리
- ⚠️ Double Diamond의 AC 자동 분해로 경계가 일부 겹칠 수 있으나, 마일스톤 수준의 전략적 결정은 여전히 사람의 영역

### 성능 개선용 AI 도구

ouroboros는 성능 프로파일링에 부적합하지만, brownfield에서 기능 추가/리팩토링/테스트 추가에는 적합하다. 성능 개선에는:
- **로컬**: performance-oracle agent, compound-engineering 성능 스킬 템플릿
- **외부**: CodeRabbit(PR 리뷰), Amazon CodeGuru(프로파일링), Dynatrace/Datadog(APM)

---

## 핵심 정리

1. **ouroboros와 rl-verify는 기능 중복이 있으나 관점이 다른 보완 조합이다.** ouroboros도 자체 수렴 검증(ralph, convergence gates)이 가능하며, rl-verify는 추가적 다관점 검증 레이어를 제공한다.
2. **온톨로지는 DDD Entity가 아니라 DTO/Value Object에 가까운 데이터 구조 정의**다. frozen flat field list로 행동/관계/생명주기가 없다.
3. **유사도는 0.5×이름 + 0.3×타입 + 0.2×완전일치 가중 합산**이며, 필드 간 관계나 중첩 구조는 포착하지 못하는 한계가 있다.
4. **eval_gate는 실행 시 기본으로 켜져 있다.** 클래스 수준 기본값(False)과 실행 시 기본값(True)의 레이어 차이다.
5. **Wonder는 claude-opus-4-6, temperature=0.7**로 온톨로지 질문을 생성한다. LLM 실패 시 규칙 기반 폴백이 작동한다.
6. **AI 자율주행 개발은 "불가능"이 아니라 "문제 정의의 자율성이 아직 신뢰할 수 없다"**가 정확하다. ouroboros 자체가 자율 진화 루프를 제공한다.
7. **점진적 개발에서 내부 점진성(seed evolve)과 외부 점진성(개발 전략)은 다른 층위**다. 둘 다 필요하며 이중 루프가 아니다.
8. **페르소나별 친화 패턴은 다대다 관계**다. HACKER만 1개(Spinning), 나머지는 2~4개 패턴에 친화성을 가진다.
9. **lateral thinking은 "자동 트리거"가 아니라 SKILL.md의 "권고(Consider)" 수준**이다.
10. **ooo run은 seed 실행기**이지 기능 분할기가 아니다. Double Diamond이 AC를 자동 분해한다.
11. **Goal Drift는 goal×0.5 + constraint×0.3 + ontology×0.2**로 계산되며, 0.30 초과 시 Consensus 검토가 필요하다.
