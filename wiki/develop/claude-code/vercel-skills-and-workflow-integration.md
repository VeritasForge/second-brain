---
tags: [claude-code, skills, workflow, vercel]
created: 2026-05-22
---

# 📚 Vercel 스킬 3종 + 워크플로우 연계 가이드

> Vercel이 공식 배포한 3개 Claude Code 스킬의 목적/사용법을 정리하고, Superpowers(brainstorming → writing-plans → executing-plans) 및 Claude Code Plan Mode 워크플로우와 어떻게 연계할지 설명한 가이드.

---

## Part 1: Vercel 스킬 3가지 전체 정리

세 스킬은 모두 Vercel 엔지니어링 팀이 공식 배포한 가이드(MIT 라이센스)이고, 각각 **다른 영역**을 다룬다.

### 🔵 ① `vercel-react-best-practices` — 성능 최적화 룰북

| 항목                  | 내용                                                                       |
| --------------------- | -------------------------------------------------------------------------- |
| **목적**              | React/Next.js 코드의 **성능 안티패턴 방지**                                |
| **규모**              | 69개 룰, 8개 카테고리                                                      |
| **트리거 조건**       | "컴포넌트 작성/리뷰/리팩토링, 데이터 fetching, 번들 최적화"                |
| **이 프로젝트 관련성** | 🔥 **최대** — Next.js 성능 문제 대부분이 여기 룰에 정의되어 있음           |

**8개 카테고리:**

```
1. async-*     (CRITICAL)   Waterfall 제거, Promise.all, Suspense
2. bundle-*    (CRITICAL)   번들 크기, dynamic import, barrel imports
3. server-*    (HIGH)       RSC 캐싱, 병렬 fetch, 직렬화
4. client-*    (MED-HIGH)   SWR dedup, 이벤트 리스너
5. rerender-*  (MEDIUM)     리렌더 최적화, memo, transitions
6. rendering-* (MEDIUM)     SVG, hydration, content-visibility
7. js-*        (LOW-MED)    JS 미세 최적화
8. advanced-*  (LOW)        고급 패턴
```

**사용법:**

```
/vercel-react-best-practices       (Skill 도구로 invoke)
또는 Skill 도구에서 이름 선택
```

### 🟢 ② `vercel-composition-patterns` — 컴포넌트 설계 패턴

| 항목                  | 내용                                                                   |
| --------------------- | ---------------------------------------------------------------------- |
| **목적**              | 컴포넌트 **API 설계** (boolean prop 폭증 방지, 재사용성)               |
| **트리거 조건**       | "boolean prop 많은 컴포넌트 리팩토링, 컴포넌트 라이브러리 구축"        |
| **이 프로젝트 관련성** | 🟡 **중간** — 디자인 시스템 적용 중이라면 도움                         |

**4개 카테고리:**

```
1. architecture-*   (HIGH)    compound components, boolean prop 회피
2. state-*          (MEDIUM)  Provider 패턴, context interface, lift state
3. patterns-*       (MEDIUM)  explicit variants, children-over-render-props
4. react19-*        (MEDIUM)  React 19 API (use, no forwardRef)
```

**언제 쓰나:** `<Button isPrimary isLarge isLoading isDisabled />` 같이 prop이 폭증할 때, 또는 라이브러리화할 때.

### 🟣 ③ `vercel-react-native-skills` — 모바일 앱 최적화

| 항목                  | 내용                                                       |
| --------------------- | ---------------------------------------------------------- |
| **목적**              | React Native + Expo 모바일 앱 최적화                       |
| **트리거 조건**       | "React Native, Expo, FlashList, Reanimated"                |
| **웹 프로젝트 관련성** | ❌ **무관** — 웹(Next.js) 프로젝트에선 적용 불가           |

→ **웹 프로젝트에선 무시해도 됩니다.**

---

## 📊 한눈에 비교

| 스킬                       | 어떤 문제                              | 웹 프로젝트 적용 |
| -------------------------- | -------------------------------------- | ---------------- |
| `react-best-practices`     | "왜 느려?" "왜 번들 커?"               | ✅ 최우선        |
| `composition-patterns`     | "이 컴포넌트 API가 너무 복잡해"        | 🟡 필요시        |
| `react-native-skills`      | "모바일 앱이 버벅거려"                 | ❌ 무관 (웹임)   |

---

## Part 2: 워크플로우와 Vercel 스킬 연계

두 가지 워크플로우(Superpowers, Plan Mode)를 각각 분석.

### 🅰️ Superpowers 워크플로우 (brainstorming → writing-plans → executing-plans)

이 워크플로우는 3단계로 구성된다. **각 단계에서 Vercel 스킬을 끼워 넣는 위치가 다르다.**

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ brainstorming   │ →  │ writing-plans    │ →  │ executing-plans  │
│ (요구사항/디자인) │    │ (구체적 코드 플랜) │    │ (실제 코드 작성)  │
└─────────────────┘    └──────────────────┘    └──────────────────┘
       ↑                       ↑                       ↑
   Vercel을 가이드            Vercel을 사양으로        Vercel을 audit으로
   (선택지로 제시)           (코드 블록에 룰 반영)     (코드 리뷰)
```

#### 단계별 연계 방법

**🧠 1단계: brainstorming**

- 아직 코드 안 쓰는 단계. 디자인 결정만.
- 하지만 디자인 자체가 룰 위반을 유도할 수 있음 (예: "use client로 다 만들자")
- **활용법**: `Propose 2-3 approaches` 단계에서 **Vercel 권장 패턴을 후보 중 하나로 포함**

```
예시 디자인 옵션:
  A) "use client" + useEffect + fetch  (현재 패턴)
  B) Server Component + Server Action   (Vercel 권장: server-parallel-fetching)
  C) Hybrid (Server Component + SWR)    (Vercel 권장: client-swr-dedup)
```

→ 그냥 A만 떠올리던 걸 B/C가 후보에 들어오게 만든다.

**📝 2단계: writing-plans** ⭐ 가장 중요

- 플랜에 **실제 코드 블록**이 들어가는 단계. 룰을 따랐는지 가장 잘 검증되는 시점.
- **활용법 — 3가지 끼워넣기 지점:**

| 지점               | 액션                                                              |
| ------------------ | ----------------------------------------------------------------- |
| 플랜 작성 **전**   | `/vercel-react-best-practices` invoke → 룰 목록을 컨텍스트에 로드 |
| 각 Task 작성 시    | Task별로 "**적용 룰**" 명시 (예: `client-swr-dedup`)              |
| Self-Review 시     | 모든 코드 블록을 룰 기준으로 점검                                 |

**플랜 문서 예시:**

```markdown
### Task 2: 대시보드 SWR 도입

**적용 Vercel 룰**: client-swr-dedup
**Files**: app/(main)/page.tsx
**Why**: 현재 useEffect + fetch 패턴이 client-swr-dedup의
        "Incorrect 예시"와 동일. SWR로 대체.

Step 1: useSWR 임포트
Step 2: useState + useEffect 제거, useSWR("/api/reviews", fetcher) 추가
...
```

**▶️ 3단계: executing-plans**

- 이미 플랜에 룰이 녹아있다면 별도 트리거 필요 없음. 그냥 실행.
- **활용법**: 완료 후 `compound-engineering:ce-code-review`에게 **"Vercel best-practices 기준으로 audit"** 명시

```
ce-code-review 호출 시 프롬프트:
"vercel-react-best-practices 스킬의 룰 기준으로 audit해줘.
 특히 async-*, server-*, client-* 카테고리 위주."
```

---

### 🅱️ Plan Mode 워크플로우 (Claude Code 내장)

5-Phase 구조. CLAUDE.md의 플랜 템플릿과 잘 맞는다.

```
Phase 1: Initial Understanding (Explore)
   ↓
Phase 2: Design (Plan agent)
   ↓
Phase 3: Review
   ↓
Phase 4: Final Plan (플랜 파일 작성)
   ↓
Phase 5: ExitPlanMode
```

#### CLAUDE.md 플랜 템플릿의 **5번 "스킬 검색"** 섹션이 핵심 연결점

CLAUDE.md에 다음과 같이 정의되어 있다:

> ### 5. 스킬 검색 (Skill Discovery)
> - Memory에서 이전 매핑 테이블 확인
> - ~/.claude 하위 skills 실제 검색
> - 스킬 매핑 테이블 작성: 각 스킬/agent의 용도와 적용 Task를 테이블로 정리

**이 섹션이 작동하면** Vercel 스킬이 자동으로 매핑 테이블에 들어가고, **6번 Task List**의 "스킬 매핑" 필드를 통해 각 Task와 연결된다.

#### Phase별 끼워넣기

| Phase                     | 액션                                                                                |
| ------------------------- | ----------------------------------------------------------------------------------- |
| **Phase 1** (Explore)     | Explore agent에게 "기존 Vercel 룰 위반 패턴도 함께 식별" 지시                       |
| **Phase 2** (Plan agent)  | Plan agent에게 "Vercel 룰 컨텍스트 참고" 지시                                       |
| **Phase 4** (Final Plan)  | Skill Discovery에 `vercel-react-best-practices` 등록 + Task별 룰 매핑               |
| **Phase 5** (ExitPlan)    | 검토 시 룰 매핑 누락 체크                                                           |

---

## 🏗️ 비유로 정리

```
Vercel 스킬       = "건축 시방서" 📘 (Building Code)
                   - 표준 규격, 안전 기준, 자재 목록

[Superpowers 3단계]
brainstorming     = "건물 컨셉 스케치" ✏️
                    시방서 안 봐도 그릴 수 있음
                    → 단, "이 컨셉이 시방서로 지을 수 있나?" 확인

writing-plans     = "구조 도면 그리기" 📐 ⭐ 시방서 절대 필요
                    이 단계에서 시방서 안 보면
                    "지을 수 없는 도면"이 나옴

executing-plans   = "공사" 🔨
                    도면대로 시공 (시방서는 도면에 녹아있음)

[Plan Mode]
1단계 한 번에       = "약식 도면 + 즉시 시공" 🏗️
                    시방서를 도면 단계에서 한 번에 녹여야 함
                    → CLAUDE.md의 "Skill Discovery" 섹션이 그 장치
```

---

## 🎯 추천 연계 방식 — "어떤 워크플로우든 공통"

세 가지 핵심 행동이면 충분하다:

```
1️⃣ [작업 시작 시] 스택 확인 후 해당 Vercel 스킬을 invoke
   → Next.js/React 프로젝트: vercel-react-best-practices 필수

2️⃣ [플랜 작성 시] 각 Task에 "적용 룰" 라벨 명시
   → 예: "Task 2 (대시보드 SWR) — Rule: client-swr-dedup"

3️⃣ [실행 완료 후] code-review 또는 ce-code-review에게 audit 의뢰
   → "Vercel 룰 기준으로 점검"
```

이렇게 3중 안전망을 두면, **누락이 다시 발생하기 어려워진다.**

---

## 🔧 자동화 강화 옵션 (선택)

좀 더 강제력이 필요하면:

| 메커니즘                          | 효과                                                       | 비용         |
| --------------------------------- | ---------------------------------------------------------- | ------------ |
| `~/.claude/CLAUDE.md` 매핑 강화   | "Next.js/React 작업 = 무조건 vercel 스킬 invoke" 명시      | 무료, 즉시   |
| `settings.json` PreToolUse hook   | `*.tsx` Edit 전 Vercel 스킬 자동 알림                      | 5분          |
| Plan 템플릿 강화                  | "Skill Discovery에 vercel-* 빠지면 작성 거부"              | 5분          |

---

## 💡 핵심 통찰

> **룰북이 있어도, 룰북을 펴지 않으면 의미 없다.**
> 스킬은 **자동 강제력이 약하므로** 플랜 단계에서 명시적으로 매핑하는 게 핵심.

CLAUDE.md의 플랜 템플릿에 "Skill Discovery" 섹션이 정의돼 있는 건, 정확히 이런 사고를 막기 위한 안전망이다. 플랜 작성 시 그 섹션을 충실히 채우면 누락을 막을 수 있다.
