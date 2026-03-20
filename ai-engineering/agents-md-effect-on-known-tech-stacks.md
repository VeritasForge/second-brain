---
created: 2026-03-20
source: claude-code
tags:
  - claude-code
  - skills
  - agents-md
  - invocation-rate
  - deep-research
  - evaluation
  - context-files
  - coding-agents
---

# Deep Research: Claude Code Skill 호출 확률, AGENTS.md 효과, 기술 스택별 분석 — 전체 통합

> **연구 이력**: Deep Research 3회(Skill 호출 확률 / AI 씬 반응 / 기술 스택별 효과) → 수렴 검증(Tier 3, 5관점, 5 iterations) → 1차 Q&A(20+ 질문) → 2차 Q&A(8개 심화 질문)
> **최종 통합**: 2026-03-20

---

## Executive Summary

Claude Code Skills의 자동 호출률은 모델과 description 품질에 따라 크게 달라진다. Scott Spence의 Haiku 4.5 테스트에서 기본 20-40%, Sonnet에서 기본 55% 수준이었다. Description 최적화, CLAUDE.md 참조, Forced-Eval Hook, 예제 추가 등으로 개선할 수 있다 (구체 수치는 Part 1.3 차트 참조 — Haiku 4.5 한정 데이터).

AGENTS.md(= Claude Code의 CLAUDE.md)를 통한 효과는 **학습 데이터 포함 여부**가 핵심 변수이다:
- **신규/니치 기술**: Vercel Next.js 16에서 **+47pp**(53%→100%) — 극적 효과
- **잘 알려진 기술**: ETH Zurich 연구에서 **-0.5%~+4%** — 미미하거나 역효과
- **LLM 생성 context file**: Python 벤치마크에서 일관되게 **성능 저하** — 주의하여 사용, 효과 측정 필수 `[Likely — Python 한정, 타 스택 미검증]`

수렴 검증 결과, Vercel의 +47pp는 자사 벤치마크 특화이며 일반화는 미검증(OVERSTATED). "20% 호출률"은 Haiku 4.5 한정(DEBUNKED).

**한 문장 요약** (SIMPLIFIER):
> "LLM에게 더 많은 맥락을 주면 더 잘 작동한다. Skills는 lazy loading, AGENTS.md는 eager loading이다. 프로젝트 규모와 모델이 모르는 지식의 양에 따라 선택하면 된다."

---

## Part 1: Skill 호출 확률 — 왜 낮고, 어떻게 높이는가?

### 1.1 근본 원인: 순수 LLM 추론 기반 라우팅

Skills의 라우팅은 **순수 LLM 추론(pure LLM reasoning)**에 의존한다. 키워드 매칭이나 알고리즘 기반 intent detection이 아니다.

```
사용자 프롬프트
    │
    ▼
┌─────────────────────────────────┐
│ Claude의 시스템 프롬프트         │
│                                  │
│ <available_skills>               │
│   skill-1: "description..."     │  ← description만 존재
│   skill-2: "description..."     │     (전체 SKILL.md 아님)
│   skill-3: "description..."     │
│ </available_skills>              │
│                                  │
│ + 대화 히스토리                  │
│ + CLAUDE.md                      │
│ + Rules                          │
│ + 기타 컨텍스트                  │
└─────────────────────────────────┘
    │
    ▼
Claude가 "이 프롬프트에 맞는 스킬이 있나?" 판단
    │
    ├── 매칭 판단 ──→ Skill(skill-name) 호출
    └── 매칭 안됨 ──→ 직접 처리
```

> **비유**: Skills의 자동 호출은 도서관에서 사서(Claude)에게 "필요한 책을 알아서 가져다 주세요"라고 하는 것과 같다. 책등(description)에 적힌 제목이 모호하면 사서가 그 책을 찾지 못한다.

### 1.2 구체적 실패 원인

| 원인                         | 설명                                                                   | 확신도                                |
| ---------------------------- | ---------------------------------------------------------------------- | ------------------------------------- |
| **모호한 description**       | "Helps with documents" 같은 설명은 Claude가 매칭하지 못함              | `[Confirmed]`                         |
| **15,000자 예산 초과**       | 스킬이 많으면 일부가 시스템 프롬프트에서 잘림 → 인지조차 못함          | `[Confirmed]`                         |
| **수동적 제안 무시**         | "If the prompt matches..." 같은 지시는 배경 소음으로 무시됨            | `[Confirmed]`                         |
| **컨텍스트 경쟁**            | description이 대화 히스토리, CLAUDE.md 등과 토큰을 경쟁                | `[Confirmed]`                         |
| **위치(positioning) 열세**   | CLAUDE.md는 "프로젝트 지시문"(상위), Skill은 "도구 목록 중 하나"(하위) | `[Uncertain — structural inference]`  |

### 1.3 호출률 향상 전략 (단계별)

```
호출 성공률 (%) — Haiku 4.5 기준, Scott Spence 200+ 프롬프트 테스트

       Haiku 4.5 기본   Sonnet 기본
            ↓               ↓
0%    20%       50%  55%  70%   80%  84%  90%  100%
├──────┼──────────┼────┼───┼─────┼────┼────┼────┤
│█████ │          │    │   │     │    │    │    │  기본 — Haiku (DEBUNKED: 일반화 부적절)
│      │          │    │███│     │    │    │    │  기본 — Sonnet (수렴 검증 수정치)
│      │██████████│    │   │     │    │    │    │  Description 최적화 (Haiku 기준)
│      │          │████│   │     │    │    │    │  CLAUDE.md 참조
│      │          │    │   │█████│    │    │    │  예제 포함
│      │          │    │   │     │████│    │    │  LLM Eval Hook
│      │          │    │   │     │    │████│    │  Forced Eval Hook
│      │          │    │   │     │    │    │████│  예제 + 강제 평가
└──────┴──────────┴────┴───┴─────┴────┴────┴────┘

⚠️ 수렴 검증 결과: "20% 기본 호출률"은 Haiku 4.5 한정 (DEBUNKED).
   Sonnet은 기본 55%이므로, 각 단계의 절대 효과가 다를 수 있음.
   위 수치는 참고용이며 모델/description 품질에 따라 크게 달라진다.
```

#### Level 1: Description 최적화 (Haiku 기준 20% → 50%)

```yaml
# BAD (20% 호출률)
---
name: api-conventions
description: Helps with API design
---

# GOOD (50% 호출률)
---
name: api-conventions
description: REST API design conventions for this codebase.
  Enforces kebab-case URLs, camelCase JSON, pagination for lists.
  Use when creating API endpoints, reviewing API code, or when
  user mentions REST, endpoint, or API design.
  Do NOT load for general backend discussions unrelated to API endpoints.
---
```

**공식 권장 패턴**: WHEN + WHEN NOT, 3인칭, 구체적 키워드, 1024자 이내, 동명사(gerund) 형태 네이밍

#### Level 2: CLAUDE.md에 스킬 참조 추가 (→ 60-70%)

```markdown
# CLAUDE.md
## Available Skills
- API 엔드포인트 작업 시 → /api-conventions 스킬 활용
- 보안 코드 리뷰 시 → /security-review 스킬 활용
```

#### Level 3: Forced-Eval Hook (→ 84%)

`settings.json`에 설치. Claude가 구현 전 모든 skill에 YES/NO 평가를 강제한다.

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "echo '🔍 INSTRUCTION: Before implementing, evaluate EVERY available skill. For each skill, write YES or NO with a one-line reason. Then activate matching skills with Skill(name) before proceeding.'"
      }]
    }]
  }
}
```

제작: **Scott Spence** (@spences10), `github.com/spences10/claude-code-toolkit`

| 속성           | Forced Eval | LLM Eval    |
| -------------- | :---------: | :---------: |
| 성공률         |   **84%**   |     80%     |
| 비용/프롬프트  |   $0.0067   | **$0.0061** |
| 일관성         |  **높음**   |    가변적   |
| 외부 의존성    |  **없음**   |   API 필요  |
| 최악의 경우    |  약간 저하  | 완전 실패 가능 |

#### Level 4: 예제 추가 (→ 90%)

```yaml
---
name: security-review
description: >
  Security code review specialist.
  Example triggers:
  - "review this code for security issues"
  - "check if there are any vulnerabilities"
  Do NOT use for: general code review, performance optimization.
---
```

#### Level 5: 토큰 예산 확보

```bash
SLASH_COMMAND_TOOL_CHAR_BUDGET=30000 claude
```

진단: `/context` 명령으로 제외된 스킬 확인

---

## Part 2: AGENTS.md — Vercel의 주장과 독립 검증

### 2.1 AGENTS.md란?

**도구 간 통일 표준**으로 등장한 context file의 이름이다.

```
도구별 context file 이름:
├── Claude Code    → CLAUDE.md (+ .claude/rules/)
├── Cursor         → .cursor/rules/ (+ .cursorrules)
├── GitHub Copilot → .github/copilot-instructions.md
├── Codex (OpenAI) → AGENTS.md
└── 범용 표준       → AGENTS.md (GitHub 제안)
```

**Claude Code에서는 CLAUDE.md에 쓰면 된다.** `AGENTS.md`라는 파일을 자동으로 읽지 않는다.

> **비유**: 학교마다 숙제장 이름이 다른 것과 같다. A학교는 "학습노트", B학교는 "공부일지"라고 부르지만, 안에 쓰는 내용은 같다. Claude Code라는 학교에서는 "CLAUDE.md"라는 이름의 숙제장을 읽는다.

### 2.2 Vercel의 실험: +47pp (53% → 100%)

Vercel은 Next.js 16의 **학습 데이터에 없는 신규 API**를 대상으로 테스트했다:

| 설정                                | 통과율 | 개선폭    |
| ----------------------------------- | ------ | --------- |
| No docs (baseline)                  | 53%    | -         |
| Agent Skill (default)               | 53%    | +0pp      |
| Agent Skill + explicit instructions | 79%    | +26pp     |
| AGENTS.md docs index (8KB)          | 100%   | **+47pp** |

테스트된 API들: `connection()`, `'use cache'`, `cacheLife()`, `cacheTag()`, `forbidden()`, `unauthorized()`, `after()`, `proxy.ts`, async `cookies()`, `headers()`

**핵심 기법: Pipe-delimited docs index**

```
# AGENTS.md 안의 docs index (8KB)
docs/app-router/caching|caching.md,cache-handler.md,revalidation.md
docs/app-router/routing|layouts.md,pages.md,route-groups.md
```

40KB 전체 문서가 아닌 8KB 인덱스(목차)만 삽입. Claude는 인덱스를 보고 **필요한 파일만 on-demand로 Read 도구로 읽는다.** `.claude/rules/`의 on-demand 패턴과 유사하다.

> **비유**: 도서관의 "도서 목록 카드"와 같다. 목록 카드(인덱스)만 책상 위에 있고, 실제 책(md 파일)은 서가에 있다. 목록을 보고 필요한 책만 가져온다.

### 2.3 수렴 검증 결과

| #  | 항목                                | 판정            | 핵심                                     |
| -- | ----------------------------------- | --------------- | ---------------------------------------- |
| 1  | Scott Spence "20%" 호출률           | **DEBUNKED**    | Haiku 4.5 한정, Sonnet은 55%             |
| 2  | Vercel 56% 미호출, 53% baseline     | **CONFIRMED**   | 수치 자체는 원문과 정확 일치             |
| 3  | AGENTS.md 100%, +47pp "우월"        | **OVERSTATED**  | Vercel 자사 벤치마크, Next.js 16 특화    |
| 4  | 독립연구 4%, -2%, -3%, 20%          | **LIKELY**      | 대체로 정확, 일부 HN 해석치              |
| 5  | Anthropic 공식 반응 없음            | **CONFIRMED**   | 검증 시점 기준 사실                      |
| 6  | "Skills 2.0 = Anthropic 간접 인정"  | **UNLIKELY**    | post hoc 오류, 자연적 제품 진화 가능     |
| 7  | 사용자 기억("20-30%") 추정 논리     | **UNGROUNDED**  | 외부 검증 불가                           |
| 8  | Cursor Forum 100% compliance        | **LIKELY**      | 수치 정확, 2 runs 소규모                 |

### 검증으로 드러난 구조적 문제

1. **확신도 인플레이션**: 단일 출처(Vercel 자사 벤치마크, Scott Spence 1인 테스트)에 `[Confirmed]` 부여
2. **서술적/규범적 주장 혼재**: "56% 미호출"(사실) → "Skills가 불안정"(판단) 전환에 암묵적 전제
3. **대안 프레임 누락**: "Skills vs AGENTS.md" 이분법에 갇혀 "아무것도 안 하기"가 유효한 선택지임을 미제시

---

## Part 3: 기술 스택별 AGENTS.md 효과 — 핵심 변수는 "학습 데이터"

### 3.1 벤치마크 결과 비교

> **확신도 태그 기준**: 이 표의 확신도는 **"해당 수치가 원문에서 정확한가"**(수치 정확성)를 평가한다. **일반화 가능성**은 별도 열로 표기한다.

| 구분                        | 벤치마크                             | 대상 기술 스택                                      | 효과                                 | 수치 정확성 | 일반화 가능성                  |
| --------------------------- | ------------------------------------ | --------------------------------------------------- | ------------------------------------ | ----------- | ------------------------------ |
| ETH Zurich (SWE-bench Lite) | 300 tasks, 11개 Python 리포          | Django, SymPy, scikit-learn 등 (학습 데이터에 포함) | LLM 생성: **-0.5%**, 사람 작성: 미미 | `[High]`    | `[Likely]` — Python 한정       |
| ETH Zurich (AGENTbench)     | 138 tasks, 12개 니치 Python 리포     | 덜 유명한 Python 프로젝트 (개발자 작성 context file) | 사람 작성: **+4%**                   | `[High]`    | `[Likely]` — Python 한정       |
| Vercel (Next.js 16 evals)   | Next.js 16 신규 API eval suite       | Next.js 16 **신규 API** (학습 데이터에 미포함)      | docs index: **+47pp** (53% → 100%)   | `[High]`    | `[Uncertain]` — 자사 벤치마크, OVERSTATED |

### 3.2 ETH Zurich 논문 (arXiv:2602.11988) 세부

#### SWE-bench Lite: 잘 알려진 Python 프로젝트들

11개 인기 Python 리포지토리로 구성. 전체 task의 대부분이 Django에서 온다:

| 리포지토리   | Task 수 | 특성                                      |
| ------------ | ------- | ----------------------------------------- |
| django       | 850     | 가장 많은 비중, 매우 잘 알려진 프레임워크 |
| sympy        | 386     | 수학 라이브러리, 학습 데이터에 풍부       |
| scikit-learn | 229     | ML 라이브러리, 학습 데이터에 풍부         |
| matplotlib   | 184     | 시각화 라이브러리                         |
| sphinx       | 187     | 문서 도구                                 |
| pytest       | 119     | 테스트 프레임워크                         |
| astropy      | 95      | 천문학 라이브러리                         |
| xarray       | 110     | 데이터 구조 라이브러리                    |
| pylint       | 57      | 린터                                      |
| requests     | 44      | HTTP 라이브러리                           |
| flask        | 11      | 웹 프레임워크                             |
| seaborn      | 22      | 시각화 라이브러리                         |

**결과:**
- LLM 생성 context file: 성공률 약 **-0.5%** (오히려 감소)
- 사람 작성 context file: 유의미한 개선 없음
- 추론 비용: **+20% 이상** 증가

**논문 원문 인용:**
> "Since this is a language that is widely represented in the training data, much detailed knowledge about tooling, dependencies, and other repository specifics might be present in the models' parametric knowledge, **nullifying the effect of context files**."

#### AGENTbench: 니치(덜 유명한) Python 프로젝트들

- 138개 task, 12개 덜 유명한 Python 리포지토리
- 개발자가 직접 작성한 context file이 이미 존재하는 리포지토리만 선정
- 평균 context file 크기: 641 words, 9.7 sections

**결과:**
- 개발자 작성 context file: **+4% 성공률 향상**
- LLM 생성 context file: **-2%~-3% 감소** (논문 abstract: -3%, 본문: -2%. 문서 제거 시 오히려 개선)

#### 리포지토리별 세부 결과

논문의 Figure 12:
> "for both SWE-bench Lite and AGENTbench, there is no single repository where the presence of context files has a significant impact."

**어떤 특정 리포지토리에서도 context file이 극적인 효과를 보인 경우는 없다.**

### 3.3 +47pp vs +4%: 왜 이렇게 다른가?

| 요인              | ETH (SWE-bench)                | Vercel (Next.js 16)                      |
| ----------------- | ------------------------------ | ---------------------------------------- |
| 대상 기술         | Django, Flask 등 (잘 알려짐)   | Next.js 16 신규 API (학습 데이터에 없음) |
| Context file 유형 | LLM 생성 + 사람 작성           | 최적화된 docs index (8KB)                |
| 효과              | -0.5% ~ +4%                    | +47pp                                    |
| 학습 데이터 포함  | O (Python 생태계 전체)         | X (신규 API)                             |

**"학습 데이터 포함 여부"가 핵심 변수라는 근거:**
1. ETH 논문이 직접 이 가설을 언급하고 인정 `[High]`
2. Vercel이 의도적으로 학습 데이터에 없는 API를 선택 `[High]`
3. 그러나 **통제된 비교 실험은 아직 없다** (동일 프레임워크에서 기존 API vs 신규 API를 직접 비교한 연구 부재) `[Uncertain]`

Vercel 자신도 이 차이를 명시적으로 인정했다:
> "Next.js 16 introduces APIs... **that aren't in current model training data**."
> "That's where doc access matters most."

### 3.4 실무자 경험 보고 (HN, Reddit, 커뮤니티)

#### "이미 아는 기술에는 안 써도 된다" 관점

> "I only add information... when the LLM gets something wrong and I need to correct it"
> -- Hacker News commenter `[Medium]`

> "If your codebase follows conventions, the agent already understands them."
> -- Augment Code blog `[Medium]`

#### "그래도 쓸모있다" 관점

> "4% improvement is massive!" (고위험 코딩에서 작은 개선도 중요)
> -- HN commenter `[Medium]`

> Helios 프로젝트: AGENTS.md로 소유권 제약 조건을 인코딩하여 **90% zero-human-review PR** 달성
> -- HN 사례 보고 `[Medium]`

#### "오히려 해롭다" 관점

> "Your CLAUDE.md Is Making Your Agent Dumber"
> -- Medium 기사 (Cordero Core) `[Medium]`

Augment Code의 분석에 따르면, 삭제해야 할 항목들:
- 폴더 구조 설명 (에이전트가 직접 탐색 가능)
- 기술 스택 문서 (학습 데이터에 이미 있음)
- 린터가 이미 강제하는 코딩 스타일 규칙
- 기존 코드에서 보이는 API 패턴

### 3.5 미해결 질문 / 연구 공백

1. **Java/Spring, Go, Rust 등 다른 기술 스택에 대한 직접적인 연구가 없다** `[Uncertain]`
2. **동일 프레임워크 내에서 기존 API vs 신규 API를 통제 비교한 연구가 없다** `[Uncertain]`
3. **"4% 개선"의 통계적 유의성이 불명확하다** `[Uncertain]`
4. **Context file의 최적 크기/구조에 대한 체계적 연구 부재** `[Uncertain]`

---

## Part 4: 2차 후속 Q&A (8개 심화 질문)

### Q1. AGENTS.md = CLAUDE.md인가?

**기능적으로 같고, 이름이 다르다.** Claude Code에서는 `CLAUDE.md`에 쓰면 된다. `AGENTS.md`라는 파일을 자동으로 읽지 않는다.

### Q2. Commitment 메커니즘(YES/NO 강제)은 학술 연구에서 검증된 건가?

**학술 연구로 직접 검증된 것은 아니다.** 커뮤니티 실험(Scott Spence)에서 발견된 패턴이며, 관련 학술 연구는 Chain-of-Thought(Wei et al., 2022)이다.

| 구분       | Chain-of-Thought (CoT)       | YES/NO Commitment                |
| ---------- | ---------------------------- | -------------------------------- |
| **출처**   | 학술 논문 (Wei et al., 2022) | 커뮤니티 실험 (Scott Spence)     |
| **검증**   | 대규모 벤치마크 (GSM8K 등)   | 개인 200+ 프롬프트 (Haiku 4.5)  |
| **재현성** | 높음                         | **낮음** `[Uncertain]`           |

> **비유**: 시험 볼 때 "정답이라고 생각하면 O, 아니면 X를 쓰고 이유를 적어라"라고 하면, 대충 넘어가는 문제가 줄어드는 것과 같다. CoT 논문은 있지만, "O/X 강제가 시험 성적을 올린다"를 직접 증명한 논문은 아직 없다.

### Q3. Pipe-delimited 인덱스: Claude가 파일을 다 읽지 않나?

**아니다.** 목차(인덱스)만 컨텍스트에 로드되고, 개별 파일은 필요할 때 Read 도구로 읽는다.

| 비교        | AGENTS.md docs index  | .claude/rules/          |
| ----------- | --------------------- | ----------------------- |
| 목차 로드   | 항상 (인덱스 8KB)     | 항상 (파일명만)         |
| 개별 파일   | 필요할 때 Read 도구로 | globs 매칭 시 자동      |
| 로드 트리거 | Claude의 판단         | 편집 중인 파일 경로     |
| 비용        | 인덱스 크기만큼 고정  | 매칭된 rule만큼 변동    |

### Q4. claude-code-toolkit이 뭔가?

**Scott Spence의 Claude Code 플러그인**. `github.com/spences10/claude-code-toolkit`. Forced-Eval Hook(skill 호출률 84%)을 포함한다. 단, Haiku 4.5에서의 테스트 결과이며, Sonnet/Opus에서는 기본 호출률이 이미 더 높다(55%+).

### Q5. Tessl.io "Without Skill 34%, With Skill 89%"의 의미?

**호출률이 아니라 정답률(pass rate)**이다.

```
두 가지 서로 다른 문제:
문제 1: "Skill이 호출되는가?" (호출률) → 20-55%
문제 2: "호출되면 성능이 오르는가?" (정답률) → 34%→89% (확실히 오른다)
```

> **비유**: 수학 시험에서 "공식집 없이 풀면 34점, 공식집을 보고 풀면 89점"이라는 뜻이다. 공식집이 34%만 열린다는 뜻이 아니다.

### Q6. Skill description과 CLAUDE.md의 Attention 차이?

**위치(positioning)와 양(volume)의 차이**. `[Uncertain — structural inference]`

| 요인   | CLAUDE.md                       | Skill description                |
| ------ | ------------------------------- | -------------------------------- |
| 위치   | "프로젝트 지시문" 섹션 (상위)   | "도구 목록" 섹션 내부 (하위)     |
| 경쟁   | 1개 파일 (단독)                 | 200+ skills 중 하나              |
| 역할   | "이것을 따르라" (지시)          | "이런 도구가 있다" (참조)        |

> Anthropic이 공식 설명한 적 없으므로 구조적 추론이다.

> **비유**: 선생님이 수업 시작할 때 칠판에 크게 적는 "오늘의 규칙"(CLAUDE.md)과, 교실 뒤편 게시판에 작은 글씨로 붙어 있는 "참고서 목록"(Skill descriptions) 중 100번째 항목.

### Q7 + Q8. Context validation 도구 / Skills 2.0 eval 내장 여부

**자동화된 내장 도구는 아직 없다.** Anthropic 공식 문서: "There is not currently a built-in way to run these evaluations"

| 방법           | 유형      | 특징                                         |
| -------------- | --------- | -------------------------------------------- |
| **Promptfoo**  | 외부 도구 | YAML 기반, CI/CD 통합, 여러 모델 동시 테스트 |
| **EDD**        | 방법론    | Phase 0(baseline) → RED → GREEN → REFACTOR  |
| **Claude A/B** | 수동 패턴 | Anthropic 공식 권장, 가장 접근성 높음        |

Skills 2.0에서 eval이 추가되었다는 블로그 기사가 있으나, Vercel 비판 대응인지 자연적 제품 진화인지는 판별 불가(`[UNLIKELY]`).

---

## Part 5: 전략 가이드 — 언제 무엇을 선택하는가?

### 효과가 큰 경우 (신규/니치 기술)

```
모델의 학습 데이터에 없는 정보
├── 신규 API (Next.js 16의 connection(), cacheLife() 등)
├── 니치 도구 (pixi, uv 같은 최신 Python 패키지 매니저)
├── 프로젝트 고유 컨벤션 (커스텀 빌드 파이프라인, 배포 절차)
└── 팀 특유의 아키텍처 결정 (코드만 봐서는 알 수 없는 것)
```

### 효과가 미미하거나 역효과인 경우 (잘 알려진 기술)

```
모델의 학습 데이터에 이미 있는 정보
├── Django의 ORM 패턴, Flask의 라우팅
├── React의 컴포넌트 구조, Spring의 DI 패턴
├── 표준 테스트 프레임워크 (pytest, JUnit)
└── 일반적인 Git 워크플로우
```

### 의사결정 플로우

```
Q0: Context file이 정말 필요한가?
├── NO → 아무것도 안 해도 된다
│         (잘 알려진 기술에서 -0.5%~+4%라면,
│          작성/유지 비용 대비 ROI가 없을 수 있음)
│
└── YES → Q1: 모델이 모르는 지식이 많은가?
    ├── YES → AGENTS.md/CLAUDE.md에 docs index 작성
    │         (Vercel 사례: +47pp — 단, 자사 벤치마크 한정, OVERSTATED)
    │
    └── NO → Q2: 자동 Skill 호출이 필요한가?
        ├── YES → Q3: 스킬이 5개 미만?
        │   ├── YES → Description 최적화만으로 충분
        │   └── NO → Q4: 호출 실패가 치명적?
        │       ├── YES → Forced-Eval Hook (Haiku 84%)
        │       └── NO → Description + CLAUDE.md 참조 (60-70%)
        │
        └── NO → CLAUDE.md만으로 충분
                  (Boris Cherny: 핵심은 /skill-name 명시 호출)
```

### 잘 알려진 스택에서의 실무 권장

> **주의**: 아래 권장사항은 **Python 벤치마크(ETH Zurich)**를 주요 근거로 한다. Java/Spring, Go, Rust 등 다른 기술 스택에 대한 직접 연구는 부재하므로, 타 언어 적용 시 추정(extrapolation)임을 인지할 것. `[Likely — Python 검증, 타 스택 미검증]`

1. **LLM이 자동 생성한 context file은 주의하여 사용** (Python에서 -0.5%~-3% 성능 저하 + 비용 +20% 증가) `[Likely — Python 한정]`
2. **반응적으로 작성할 것**: 에이전트가 실수한 부분만 추가 — 프레임워크의 매우 기본적인 패턴(라우팅, DI 등)은 중복일 가능성이 높으나, 경계가 모호하므로 실수 기반 추가가 더 실용적 `[Likely]`
3. **프로젝트 고유 정보만 기술할 것**: 빌드 커맨드, 배포 절차, known gotchas `[Likely]`
4. **간결하게 유지할 것** (Boris Cherny: CLAUDE.md 2.5k 토큰 권장, context window 경쟁 최소화) `[Medium — 구체 수치의 최적값은 미검증]`

### 신규/니치 기술 스택에서의 실무 권장

1. **AGENTS.md/CLAUDE.md가 극적 효과 발휘 가능** (Vercel 사례: +47pp — 단, 자사 Next.js 16 벤치마크 한정, 수렴 검증에서 OVERSTATED 판정) `[Likely — 일반화 미검증]`
2. **문서 전체가 아닌 docs index(목차 + 파일 경로)를 제공** `[Medium]`
3. **항상 사용 가능한 passive context가 on-demand skill보다 나을 수 있음** `[Medium]`

### 대부분의 프로젝트에서 충분한 전략

대규모 팀이나 자동화된 CI/CD가 아닌 경우, 체계적 eval보다 **반응적 작성**(에이전트 실수 시 추가)만으로 충분할 수 있다. "아무것도 안 하기"도 유효한 선택지이다.

---

## Sources

### 공식 문서

1. [Skill authoring best practices — Anthropic](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
2. [Extend Claude with skills — Anthropic](https://code.claude.com/docs/en/skills)
3. [Manage Claude's memory — Anthropic](https://code.claude.com/docs/en/memory)

### 학술 논문

4. [Evaluating AGENTS.md — ETH Zurich (arXiv:2602.11988)](https://arxiv.org/html/2602.11988v1)
5. [EDD of LLM Agents — arxiv:2411.13768](https://arxiv.org/html/2411.13768v2)
6. Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (2022)

### 1차 자료 (원저자)

7. [AGENTS.md outperforms skills — Vercel](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)
8. [How to Make Claude Code Skills Activate Reliably — Scott Spence](https://scottspence.com/posts/how-to-make-claude-code-skills-activate-reliably)
9. [Claude Code Skills Don't Auto-Activate — Scott Spence](https://scottspence.com/posts/claude-code-skills-dont-auto-activate)
10. [How Boris Uses Claude Code — paddo.dev](https://paddo.dev/blog/how-boris-uses-claude-code/)

### 기술 블로그 / 커뮤니티

11. [Skills Auto-Activation via Hooks — paddo.dev](https://paddo.dev/blog/claude-skills-hooks-solution/)
12. [Claude Code Skills Structure — mellanon (GitHub Gist)](https://gist.github.com/mellanon/50816550ecb5f3b239aa77eef7b8ed8d)
13. [LLM Eval Driven Development — Fireworks.ai](https://fireworks.ai/blog/eval-driven-development-with-claude-code)
14. [How to write a great agents.md — GitHub Blog](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/)
15. [Augment Code — Your agent's context is a junk drawer](https://www.augmentcode.com/blog/your-agents-context-is-a-junk-drawer)
16. [InfoQ — New Research Reassesses the Value of AGENTS.md](https://www.infoq.com/news/2026/03/agents-context-file-value-review/)
17. [HN Discussion — Evaluating AGENTS.md](https://news.ycombinator.com/item?id=47034087)
18. [HN Discussion — AGENTS.md outperforms skills](https://news.ycombinator.com/item?id=46809708)

### Vault 참조

19. `gen_ai/claude-code-skills-invocation-rate-optimization.md` — Skill 호출률 최적화 Deep Research
20. `develop/claude-code/skill-edd-tdd-best-practices.md` — EDD/TDD 방법론
21. `develop/claude-code/claude-code-rules-vs-claude-md.md` — Rules vs CLAUDE.md
22. `verify-skill-invocation-agents-md/report.md` — 수렴 검증 리포트

---

## Research Metadata

- **총 연구 기간**: Deep Research 3회 + 수렴 검증 + Q&A 2회
- **검색 쿼리 수**: 15+ (일반 12 + SNS 3)
- **수집 출처 수**: 22
- **출처 유형 분포**: 공식 3, 1차 자료 4, 학술 3, 블로그 4, 커뮤니티 4, Vault 4
- **수렴 검증**: Tier 3, 5개 관점, 5 iterations, 8/8 항목 수렴
- **확신도 분포**: Confirmed 8, Likely 4, Overstated 1, Debunked 2, Unlikely 1, Uncertain 3, Ungrounded 1

---

## 핵심 정리

1. **Skill 호출률은 모델에 따라 크게 다르다**: Haiku 20-40%, Sonnet 55%. "20%"는 Haiku 한정(DEBUNKED)
2. **Description 최적화가 가장 효율적인 첫 단계**: WHEN + WHEN NOT 패턴 적용
3. **Forced-Eval Hook은 Haiku에서 84%**이나, Sonnet/Opus에서는 효과가 줄어들 수 있음
4. **학습 데이터 포함 여부가 핵심 변수일 가능성이 높다**: 단, 통제된 비교 실험은 부재 `[Likely]`
5. **Python 벤치마크에서 LLM 생성 context file은 성능 저하**: 타 스택 미검증이므로 "금지"가 아닌 "주의" `[Likely]`
6. **Vercel의 +47pp는 자사 벤치마크 한정**: docs index 자체는 유망하나 일반화 미검증(OVERSTATED)
7. **반응적 작성이 가장 실용적**: 에이전트가 실수한 부분만 추가. "아무것도 안 하기"도 유효한 선택지
8. **내장 eval 도구는 아직 없음**: 대부분의 프로젝트에서는 반응적 작성만으로 충분
9. **현실적 전략**: 핵심 워크플로우는 `/skill-name` 명시 호출, 자동 호출은 편의 기능으로 활용
