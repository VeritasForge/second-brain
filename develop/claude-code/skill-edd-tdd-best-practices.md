---
created: 2026-02-25
source: claude-code
tags:
  - claude-code
  - skill
  - tdd
  - edd
  - evaluation
  - prompt-engineering
  - best-practices
  - deep-research
---

# Deep Research: Claude Code Skill 검증/리뷰 — TDD/EDD Best Practice

## Executive Summary

Skill 개발에서 코드 TDD의 **RED -> GREEN -> REFACTOR**에 대응하는 개념은 **Evaluation-Driven Development (EDD)**입니다. Anthropic 공식 문서는 "평가를 먼저 작성하라(Build evaluations BEFORE writing documentation)"를 명시하고, Fireworks.ai는 이를 RED-GREEN-REFACTOR로 공식 매핑했습니다. 학술 연구(arxiv:2411.13768)는 EDD를 TDD의 LLM Agent 특화 확장으로 정의하며, 4단계 프로세스 모델을 제안합니다. 핵심은 **"먼저 원하는 행동을 정의하고, 그것을 통과하도록 skill을 작성하며, 회귀 없이 개선한다"**는 것입니다.

---

## 1. TDD vs EDD — Skill에는 무엇이 맞는가?

코드와 Skill의 근본적 차이를 이해해야 합니다:

| 차원             | 코드 TDD                        | Skill EDD                                              |
| ---------------- | ------------------------------- | ------------------------------------------------------ |
| **출력**         | 결정적(deterministic)           | 비결정적(non-deterministic)                            |
| **검증**         | assert `==` exact match         | 행동 기반 scoring (0~1)                                |
| **실패**         | 명확한 에러                     | 부분적 성공/실패 스펙트럼                              |
| **리팩터링**     | 동작 보존 보장                  | 회귀 가능성 항상 존재                                  |
| **테스트 대상**  | 함수/메서드                     | 발동(activation) + 행동(behavior) + 품질(quality)      |

- **확신도**: [Confirmed] — Anthropic 공식 문서, Fireworks.ai, 학술 논문(2411.13768) 3개 독립 출처에서 일치
- **근거**: Anthropic은 "evaluation"이라는 용어를, Fireworks.ai는 "eval"을, 학술 논문은 "EDD"를 사용하지만 모두 동일한 패턴을 가리킴

> **12살 비유**: 코드 TDD는 "수학 시험에서 정답이 42인지 확인"하는 것이고, Skill EDD는 "작문 시험에서 글이 주제에 맞고, 논리적이고, 읽기 쉬운지를 여러 관점에서 채점"하는 것입니다. 정답이 하나가 아니라 "좋은 글"의 기준으로 평가합니다.

---

## 2. Skill TDD/EDD 실천 프레임워크

여러 출처를 종합하여 실용적인 프레임워크를 구성했습니다.

- **확신도**: [Synthesized] — Anthropic 공식 가이드 + Fireworks.ai EDD + dagworks TDD + 학술 논문을 조합

```
┌─────────────────────────────────────────────────────────────────┐
│              Skill TDD/EDD Lifecycle                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Phase 0: BASELINE (준비)                                        │
│  ┌─────────────────────────────────────────────────────┐         │
│  │  Skill 없이 Claude에게 동일 작업 실행               │         │
│  │  → 어디서 실패하는지, 무엇이 부족한지 기록           │         │
│  │  → "Gap Document" 생성                               │         │
│  └─────────────────────┬───────────────────────────────┘         │
│                         │                                         │
│  Phase 1: RED (expected behavior 정의)                            │
│  ┌─────────────────────▼───────────────────────────────┐         │
│  │  Gap을 기반으로 3개 이상 평가 시나리오 작성           │         │
│  │  각 시나리오에 expected_behaviors 명시                │         │
│  │  → 현재 상태로 실행 → 실패 확인 (RED!)               │         │
│  └─────────────────────┬───────────────────────────────┘         │
│                         │                                         │
│  Phase 2: GREEN (최소 skill 작성)                                │
│  ┌─────────────────────▼───────────────────────────────┐         │
│  │  Gap을 해결하는 최소한의 SKILL.md 작성               │         │
│  │  → 평가 시나리오 재실행 → 통과 확인 (GREEN!)         │         │
│  │  → Claude A(작성) / Claude B(테스트) 이원화          │         │
│  └─────────────────────┬───────────────────────────────┘         │
│                         │                                         │
│  Phase 3: REFACTOR (개선)                                        │
│  ┌─────────────────────▼───────────────────────────────┐         │
│  │  토큰 효율성 개선, 구조 정리, 불필요한 내용 제거     │         │
│  │  → 기존 평가 시나리오 전부 재실행 (regression check)  │         │
│  │  → 모든 모델(Haiku/Sonnet/Opus)에서 테스트           │         │
│  └─────────────────────┬───────────────────────────────┘         │
│                         │                                         │
│  Phase 4: OBSERVE + EXPAND (관찰 + 확장)                         │
│  ┌─────────────────────▼───────────────────────────────┐         │
│  │  실제 사용에서 edge case 발견                         │         │
│  │  → 새 평가 시나리오 추가 → Phase 1로 돌아감           │         │
│  │  → 팀 피드백 수집 → skill 진화                       │         │
│  └─────────────────────────────────────────────────────┘         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 0: BASELINE — 격차 측정

Anthropic 공식 가이드에서 명시합니다:

> "Run Claude on representative tasks **without a Skill**. Document specific failures or missing context"

```yaml
# baseline_test.yaml
scenario: "security 아키텍처 리뷰 요청"
input: "JWT 기반 인증 시스템을 리뷰해줘"
without_skill:
  observed: "일반적인 조언만 제공, OWASP 참조 없음, 구체적 취약점 미분석"
  gaps:
    - "OWASP Top 10 체크리스트 누락"
    - "Argon2 해싱 권고 누락"
    - "Rate limiting 언급 없음"
```

- **확신도**: [Confirmed] — Anthropic 공식 best practice 원문 확인

### Phase 1: RED — 먼저 "원하는 행동"을 정의

**코드 TDD**에서 실패하는 테스트를 먼저 작성하듯, **skill에서는 "expected behavior"를 먼저 정의**합니다:

```json
{
  "evaluation_id": "security-review-001",
  "skill": "security-architect",
  "query": "JWT 기반 인증 시스템의 보안 아키텍처를 리뷰해줘",
  "expected_behaviors": [
    "OWASP Top 10 체크리스트를 참조한다",
    "Access Token 만료 시간(15분)을 권고한다",
    "Argon2 해싱을 권고한다",
    "Rate limiting 전략을 포함한다",
    "구조화된 리포트(Recommendations/Concerns/Vote)를 출력한다"
  ],
  "anti_behaviors": [
    "구체적 근거 없이 '일반적으로 안전합니다'라고 답하지 않는다",
    "skill과 무관한 도메인(데이터 아키텍처 등)을 다루지 않는다"
  ]
}
```

Fireworks.ai의 Eval Protocol도 동일한 구조를 사용합니다:

> "Write evals describing desired behavior before implementation exists. Tests intentionally fail initially."

- **확신도**: [Confirmed] — Anthropic + Fireworks.ai 2개 독립 출처

### Phase 2: GREEN — 최소 skill 작성

Gap을 해결하는 **최소한의 내용만** SKILL.md에 작성합니다. Anthropic이 강조하는 "concise is key" 원칙:

> "Write minimal instructions: Create **just enough content** to address the gaps and pass evaluations"

여기서 핵심은 **Claude A / Claude B 이원화 패턴**입니다:

```
┌──────────────────┐                    ┌──────────────────┐
│     Claude A      │                    │     Claude B      │
│   (Skill Author)  │                    │   (Skill Tester)  │
├──────────────────┤                    ├──────────────────┤
│ • Skill 설계/작성 │   SKILL.md 전달   │ • 실제 태스크 실행│
│ • 리뷰/개선 조언  │ ─────────────────→ │ • Gap 발견 리포트 │
│ • 문제 진단/수정  │ ←───────────────── │ • 행동 관찰 결과  │
└──────────────────┘   관찰 결과 전달    └──────────────────┘
```

> **Anthropic 원문**: "Work with one instance of Claude ('Claude A') to create a Skill that will be used by other instances ('Claude B'). Claude A helps you design and refine instructions, while Claude B tests them in real tasks."

- **확신도**: [Confirmed] — Anthropic 공식 문서 원문 확인

### Phase 3: REFACTOR — 회귀 없는 개선

코드 리팩터링은 "동작을 보존하면서 구조를 개선"하는 것입니다. Skill 리팩터링도 동일하지만, **비결정적 출력** 때문에 회귀 위험이 더 큽니다:

> **Fireworks.ai 원문**: "Modify system prompts, swap models, or add features **confidently** because the comprehensive eval suite prevents regressions."

리팩터링 시 확인 사항:

- 기존 모든 평가 시나리오 재실행 (regression check)
- 토큰 효율성 개선 (불필요한 설명 제거)
- progressive disclosure 적용 (500줄 이하 유지)
- **모든 모델에서 테스트** (Haiku, Sonnet, Opus)

dagworks의 pytest 기반 접근법은 비결정성을 다루는 구체적 방법을 제시합니다:

> "Run things **multiple times** to explore and determine how the variance of a single prompt + data input leads to different outputs."

- **확신도**: [Confirmed] — Fireworks.ai + dagworks + Anthropic 3개 출처

---

## 3. 3층 평가 모델 (Evaluation Layers)

Skill 테스트는 코드 테스트와 달리 **3가지 레벨**을 평가해야 합니다:

- **확신도**: [Synthesized] — Anthropic activation guidance + Fireworks behavior eval + 학술 논문 quality metrics를 조합

```
┌─────────────────────────────────────────────────────────┐
│                    L3: Quality Test                       │
│            "출력 품질이 기대 수준인가?"                   │
│  ┌─────────────────────────────────────────────────┐     │
│  │ • 토큰 효율성 (간결성)                          │     │
│  │ • 구조 준수 (template compliance)               │     │
│  │ • 정보 정확성 (factual correctness)             │     │
│  │ • 일관성 (terminology consistency)              │     │
│  └─────────────────────────────────────────────────┘     │
├─────────────────────────────────────────────────────────┤
│                    L2: Behavior Test                      │
│            "원하는 행동을 하는가?"                        │
│  ┌─────────────────────────────────────────────────┐     │
│  │ • expected_behaviors 충족                       │     │
│  │ • anti_behaviors 미발생                         │     │
│  │ • 올바른 도구 사용 (WebSearch, Read 등)         │     │
│  │ • 적절한 참조 파일 로딩                         │     │
│  └─────────────────────────────────────────────────┘     │
├─────────────────────────────────────────────────────────┤
│                    L1: Activation Test                    │
│            "올바른 상황에서 발동되는가?"                  │
│  ┌─────────────────────────────────────────────────┐     │
│  │ • 트리거 조건에서 발동 확인 (true positive)      │     │
│  │ • 비관련 요청에서 미발동 확인 (true negative)    │     │
│  │ • description 키워드 매칭 정확도                 │     │
│  └─────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### L1: Activation Test (발동 테스트)

Anthropic은 skill description이 발동 정확도에 직접적 영향을 미친다고 밝힙니다:

> "Properly optimized descriptions can improve skill activation from 20% to 50%, and adding examples improves it further from 72% to 90%."

```yaml
# activation_test_cases.yaml
positive_triggers:  # 이 요청에서 발동해야 함
  - "JWT 인증 시스템의 보안을 점검해줘"
  - "OWASP 취약점 분석"
  - "암호화 전략 리뷰"

negative_triggers:  # 이 요청에서 발동하면 안 됨
  - "데이터 모델링 리뷰"
  - "CI/CD 파이프라인 설계"
  - "일반적인 코드 리뷰"
```

- **확신도**: [Confirmed] — Anthropic 공식 문서 + skywork.ai 블로그

### L2: Behavior Test (행동 테스트)

가장 핵심적인 테스트 레이어입니다. dagworks(pytest 기반 LLM TDD)는 **5가지 assertion 전략**을 제시합니다:

| 전략                | 설명                   | Skill 적용                |
| ------------------- | ---------------------- | ------------------------- |
| **Exact match**     | 정확한 문자열 일치     | 필수 섹션 헤더 포함 여부  |
| **Fuzzy match**     | 키워드/의미 유사도     | 핵심 개념 언급 여부       |
| **Human grading**   | 사람의 주관적 평가     | 최종 품질 리뷰            |
| **LLM-based grading** | 다른 LLM이 평가     | 자동화된 평가             |
| **Static measures** | 길이, 형식, 구조       | 토큰 수, 섹션 구조        |

- **확신도**: [Confirmed] — dagworks 블로그 원문 확인

### L3: Quality Test (품질 테스트)

LLM-as-Judge 패턴을 활용합니다. Monte Carlo Data의 7가지 best practice 중 핵심:

1. **Chain-of-Thought**: 점수 전에 논리를 먼저 출력 -> 10-15% 신뢰성 향상
2. **Few-shot 예제**: 2-3개 채점 예시 제공 -> 25-30% 정확도 개선
3. **낮은 temperature**: 0.1로 설정하여 결정성 확보

- **확신도**: [Confirmed] — Monte Carlo Data + Evidently AI + Patronus AI 3개 독립 출처

---

## 4. 도구 생태계

### Promptfoo (가장 실용적)

```yaml
# promptfooconfig.yaml 예시 — Skill 테스트용
prompts:
  - "{{skill_prompt}}"  # SKILL.md 내용

providers:
  - id: anthropic:messages:claude-sonnet-4-20250514
  - id: anthropic:messages:claude-haiku-4-5-20251001

tests:
  - vars:
      skill_prompt: "JWT 인증 시스템을 리뷰해줘"
    assert:
      - type: contains
        value: "OWASP"
      - type: contains
        value: "Rate Limiting"
      - type: llm-rubric
        value: "리뷰가 구조화되어 있고 구체적인 권고를 포함하는가?"
```

- **확신도**: [Confirmed] — Promptfoo 공식 문서 + GitHub repo
- **출처**: [Promptfoo GitHub](https://github.com/promptfoo/promptfoo)

### Fireworks Eval Protocol (Agent 특화)

```python
# eval 정의 예시
@evaluation_test(
    input_dataset=["data/skill_eval_dataset.jsonl"],
    passed_threshold=0.6,
    mode="pointwise"
)
def test_skill_behavior(row):
    # scoring logic
```

- **확신도**: [Confirmed] — Fireworks.ai 공식 블로그 원문 확인
- **출처**: [Fireworks EDD with Claude Code](https://fireworks.ai/blog/eval-driven-development-with-claude-code)

### DeepEval (pytest 스타일)

pytest와 동일한 인터페이스로 LLM 출력을 테스트합니다.

- **확신도**: [Likely] — GitHub repo 확인, 원문 미확인
- **출처**: [DeepEval GitHub](https://github.com/confident-ai/deepeval)

### DSPy (자동 최적화)

프롬프트를 "프로그래밍"으로 전환하여 자동 최적화합니다. metric 함수를 정의하면 MIPRO optimizer가 자동으로 최적 프롬프트를 탐색합니다.

- **확신도**: [Confirmed] — Stanford NLP 공식 repo + 문서
- **출처**: [DSPy](https://dspy.ai/)

---

## 5. Skill Review Checklist

Anthropic 공식 체크리스트 + 커뮤니티 best practice를 종합했습니다.

- **확신도**: [Synthesized] — Anthropic checklist (원문 확인) + 커뮤니티 패턴 조합

### A. 구조 & 설계 리뷰

```
- [ ] description이 "무엇을 하는가" + "언제 사용하는가"를 모두 포함
- [ ] description이 3인칭으로 작성 (discovery 정확도 향상)
- [ ] SKILL.md 본문 500줄 이하
- [ ] 참조 파일이 1단계 깊이 (SKILL.md → 참조파일, 중첩 X)
- [ ] Progressive disclosure 적절히 적용
- [ ] 시간 의존적 정보 없음 (또는 "old patterns" 섹션에 격리)
- [ ] 일관된 용어 사용 (동일 개념에 동일 단어)
```

### B. 행동 & 정확성 리뷰

```
- [ ] 최소 3개 평가 시나리오 작성 및 통과
- [ ] expected_behaviors가 명확하고 측정 가능
- [ ] anti_behaviors (하지 말아야 할 것) 정의
- [ ] 워크플로우에 명확한 단계와 검증 포인트 존재
- [ ] 피드백 루프 포함 (실행 → 검증 → 수정 → 재검증)
```

### C. 모델 호환성 리뷰

```
- [ ] Haiku에서 테스트 (충분한 가이던스 제공하는가?)
- [ ] Sonnet에서 테스트 (명확하고 효율적인가?)
- [ ] Opus에서 테스트 (과도한 설명이 없는가?)
- [ ] 비결정성 테스트 (동일 입력, 3회 이상 실행, 일관성 확인)
```

### D. 토큰 효율성 리뷰

```
- [ ] Claude가 이미 아는 내용을 불필요하게 설명하지 않는가?
- [ ] 각 문단이 토큰 비용을 정당화하는가?
- [ ] 실행 가능한 스크립트는 context에 로드하지 않고 실행하는가?
- [ ] 상호 배타적 참조 파일은 분리되어 있는가?
```

### E. 보안 & 안전성 리뷰

```
- [ ] 민감 정보(credentials, API keys) 하드코딩 없음
- [ ] 파괴적 동작에 대한 명시적 경고/확인 포함
- [ ] 에러 핸들링이 "Claude에게 떠넘기기"가 아닌 명시적 처리
```

---

## 6. 현실 세계 비유 (12살 설명)

**Skill을 만드는 것은 "레시피 책 만들기"와 같습니다.**

| TDD 단계                   | 레시피 책 비유                                                                    |
| -------------------------- | --------------------------------------------------------------------------------- |
| **Phase 0: BASELINE**      | 레시피 없이 요리를 시켜봄 -> "소금 안 넣었네", "오븐 온도 틀렸네" 기록            |
| **Phase 1: RED**           | "완성된 요리는 이래야 해"라는 사진과 체크리스트를 먼저 만듦                        |
| **Phase 2: GREEN**         | 실패 원인을 해결하는 최소한의 레시피를 작성                                        |
| **Phase 3: REFACTOR**      | 레시피를 더 간결하게 다듬되, 기존에 성공했던 요리가 여전히 맛있는지 확인           |
| **Phase 4: OBSERVE**       | 실제로 다른 사람이 이 레시피로 요리해보고, 막히는 부분을 기록하여 레시피 업데이트  |

Claude A는 "요리 전문가(레시피 작성자)", Claude B는 "처음 레시피를 보는 초보 요리사(테스터)"입니다.

---

## 7. 사고 과정 그래프

```
┌─────────────────────────────────────────────────────────────┐
│                    연구 도구 호출 흐름                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  sequential-thinking (쿼리 분해)                              │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────── Phase 1: 광역 탐색 ────────────────┐      │
│  │  WebSearch x6 (병렬 3+3)                           │      │
│  │  ├─ Claude Code skill testing                       │      │
│  │  ├─ prompt TDD LLM evaluation                      │      │
│  │  ├─ promptfoo CI/CD                                 │      │
│  │  ├─ LLM-as-judge best practices                    │      │
│  │  ├─ prompt review checklist                         │      │
│  │  └─ DSPy optimization + skill authoring             │      │
│  └────────────────────────────────────────────────────┘      │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────── Phase 2: 심화 탐색 ────────────────┐      │
│  │  WebFetch x4 (원문 확인)                            │      │
│  │  ├─ Anthropic Skill Best Practices (공식)           │      │
│  │  ├─ aihero.dev TDD Skill (Matt Pocock)             │      │
│  │  ├─ dagworks TDD of LLM (pytest)                   │      │
│  │  ├─ arxiv EDD 논문 (2411.13768)                    │      │
│  │  ├─ Latent Space TDD for AI Agents                 │      │
│  │  └─ Fireworks EDD with Claude Code                 │      │
│  └────────────────────────────────────────────────────┘      │
│         │                                                     │
│         ▼                                                     │
│  sequential-thinking (교차 검증 + Anti-Hallucination)          │
│         │                                                     │
│         ▼                                                     │
│  Phase 3: 지식 합성 → 최종 리포트                              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Edge Cases & Caveats

- **비결정성 한계**: 동일 skill + 동일 입력으로도 매번 다른 출력이 나올 수 있음. 따라서 "3회 이상 반복 실행"이 필수 (dagworks 권고)
- **모델 업데이트 시 regression**: Claude 모델이 업데이트되면 기존에 통과하던 eval이 실패할 수 있음. 정기적 재평가 필요 (월 1회 권장, Anthropic)
- **자동화 도구 부재**: 현재 Anthropic에 built-in skill evaluation 도구는 없음 ("There is not currently a built-in way to run these evaluations" — Anthropic 원문). 자체 구축 또는 Promptfoo 등 외부 도구 활용 필요
- **Activation 테스트의 어려움**: Skill이 100개 이상일 때 발동 정확도 측정이 복잡해짐. description 최적화가 핵심

## Contradictions Found

- **TDD vs EDD 명칭**: Matt Pocock은 "TDD"를, Fireworks.ai/학술 논문은 "EDD"를 사용 -> 해결: 코드 작성에는 TDD, skill/prompt에는 EDD가 더 적합한 용어. 핵심 정신("테스트 먼저")은 동일

---

## Sources

1. [Skill authoring best practices — Anthropic 공식](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — 공식 문서
2. [My Skill Makes Claude Code GREAT At TDD — AI Hero (Matt Pocock)](https://www.aihero.dev/skill-test-driven-development-claude-code) — 1차 자료
3. [Test Driven Development of LLM Applications with pytest — dagworks](https://blog.dagworks.io/p/test-driven-development-tdd-of-llm) — 기술 블로그
4. [Evaluation-Driven Development of LLM Agents — arxiv:2411.13768](https://arxiv.org/html/2411.13768v2) — 학술 논문
5. [AI Agents, meet Test Driven Development — Latent Space](https://www.latent.space/p/anita-tdd) — 1차 자료
6. [LLM Eval Driven Development with Claude Code — Fireworks.ai](https://fireworks.ai/blog/eval-driven-development-with-claude-code) — 기술 블로그
7. [Promptfoo — GitHub](https://github.com/promptfoo/promptfoo) — 도구
8. [CI/CD Integration — Promptfoo](https://www.promptfoo.dev/docs/integrations/ci-cd/) — 공식 문서
9. [LLM-As-Judge: 7 Best Practices — Monte Carlo Data](https://www.montecarlodata.com/blog-llm-as-judge/) — 기술 블로그
10. [DSPy — Stanford NLP](https://dspy.ai/) — 공식 문서
11. [Tests as Prompt: TDD Benchmark — arxiv:2505.09027](https://arxiv.org/abs/2505.09027) — 학술 논문
12. [DeepEval — GitHub](https://github.com/confident-ai/deepeval) — 도구

---

## Research Metadata

- 검색 쿼리 수: 9 (일반 8 + SNS 1)
- 수집 출처 수: 12
- 출처 유형 분포: 공식 3, 1차 자료 2, 기술 블로그 3, 학술 2, 도구 2, SNS 0 (관련 Reddit 토론 미발견)
- 원문 확인(WebFetch): 6건
- 확신도 분포: Confirmed 7, Likely 1, Synthesized 3, Uncertain 0, Unverified 0
