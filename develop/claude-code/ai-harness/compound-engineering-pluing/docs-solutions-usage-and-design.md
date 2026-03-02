---
created: 2026-03-02
source: claude-code
tags: []
---

## 1. `docs/solutions/` 파일이 어떻게 사용되는가

`/workflows:compound`로 생성된 문서는 **`learnings-researcher` 에이전트**를 통해 소비됩니다. 흐름은 이렇습니다:

```
문제 해결 → /workflows:compound → docs/solutions/<category>/<file>.md 작성
                                          ↓
                              (YAML frontmatter로 구조화)
                                          ↓
            다른 워크플로우에서 learnings-researcher가 검색·참조
```

**구체적인 소비 시점:**

| 워크플로우          | 어떻게 사용하는가                                            |
| ------------------- | ------------------------------------------------------------ |
| `/workflows:plan`   | 계획 수립 시 과거 유사 문제 해결책을 검색해서 plan에 반영    |
| `/workflows:review` | PR 리뷰 시 "Known Pattern" 플래그로 과거 해결책과 연결       |
| `/deepen-plan`      | 계획 심화 시 과거 학습 내용으로 깊이 추가                    |

**learnings-researcher의 검색 방식:**

1. 태스크에서 키워드 추출 (모듈명, 기술 용어, 문제 유형)
2. YAML frontmatter의 `title`, `tags`, `module`, `problem_type` 필드를 **Grep으로 병렬 검색**
3. 후보 파일의 frontmatter만 먼저 읽어 관련도 점수 매김
4. 높은 관련도 파일만 전체 읽기 → 요약 반환

즉, YAML frontmatter가 **검색 인덱스** 역할을 합니다.

---

## 2. 왜 CLAUDE.md나 rules/*에 넣지 않고 별도 파일로 분리하는가

핵심 이유는 **확장성(scalability)과 검색성(searchability)**입니다.

### CLAUDE.md에 넣으면 안 되는 이유

- CLAUDE.md는 **매 대화마다 컨텍스트에 주입**됩니다
- 해결된 문제가 100개 쌓이면? 모든 대화에서 수천 줄이 컨텍스트를 차지
- 컨텍스트 윈도우 낭비 + 비용 증가 + 관련 없는 정보가 노이즈로 작용

### 별도 파일로 분리하는 이점

**선택적 로딩 (Lazy Loading)**

```
CLAUDE.md → 항상 로드 (규칙, 컨벤션 등 보편적 지침)
docs/solutions/ → 필요할 때만 검색해서 관련된 것만 로드
```

**구조화된 검색**

```yaml
# YAML frontmatter 예시
title: N+1 query in brief generation
problem_type: performance_issue
module: BriefSystem
tags: [n-plus-one, activerecord, eager-loading]
severity: P1
```

→ Grep으로 `module:.*Brief`, `tags:.*n-plus-one` 같은 정밀 검색이 가능

**카테고리 분류**

```
docs/solutions/
  ├── performance-issues/    ← 성능 문제만
  ├── database-issues/       ← DB 문제만
  ├── security-issues/       ← 보안 문제만
  └── patterns/
      └── critical-patterns.md  ← 승격된 핵심 패턴 (항상 읽힘)
```

### 정리하면

| 구분       | CLAUDE.md / rules                | docs/solutions                   |
| ---------- | -------------------------------- | -------------------------------- |
| **로딩**   | 항상 전체 로드                   | 필요할 때 선택적 로드            |
| **용도**   | 보편적 규칙·컨벤션               | 특정 문제의 해결 기록            |
| **크기**   | 간결하게 유지해야 함             | 수백 개 파일도 OK                |
| **검색**   | 불가 (전체 텍스트)               | YAML frontmatter로 정밀 검색     |
| **비용**   | 매 대화마다 토큰 소비            | 관련 있을 때만 토큰 소비         |

**비유하자면:** CLAUDE.md는 "포스트잇에 붙여놓은 규칙"이고, `docs/solutions/`는 "검색 가능한 위키"입니다. 모든 위키 문서를 포스트잇에 옮겨 적으면 오히려 아무것도 안 보이게 됩니다.

단, 정말 중요한 패턴은 `docs/solutions/patterns/critical-patterns.md`로 **승격**할 수 있고, 이 파일은 learnings-researcher가 **매번 반드시** 읽습니다. 이것이 "자주 참조해야 할 핵심 지식"과 "필요할 때만 찾아볼 상세 기록"을 분리하는 메커니즘입니다.
