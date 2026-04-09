---
tags:
  - claude-code
  - memory
  - claude-md
  - hooks
  - every-style-guide
created: 2026-03-28
verified: true
verification: docs/demiurge/rl-verify/every-style-edit-verify/report.md
---

# Claude Code Memory, CLAUDE.md, Hook Q&A

## Q2. Memory 기능 — 뭔데, 왜 플랜에 넣었는지

근거 소스: 시스템 프롬프트의 auto memory 섹션,
`/Users/cjynim/.claude/projects/-Users-cjynim-lab-demiurge/memory/MEMORY.md`

### Memory란?

현실 비유: 메모장에 적어두는 것. 대화가 끝나면 Claude는 모든 걸 잊지만, Memory에 적어놓으면 다음
대화에서도 기억한다.

대화 1: "나는 19년차 시니어 엔지니어야"
  → Memory에 저장: user_career.md

대화 2: (새 대화 시작)
  → Claude가 MEMORY.md를 읽음 → "아, 19년차 시니어구나" 인식
  → 답변을 시니어 레벨에 맞춤

### Memory 종류

┌───────────┬──────────────────┬──────────────────────────────────────────┐
│   타입    │       용도       │                   예시                   │
├───────────┼──────────────────┼──────────────────────────────────────────┤
│ user      │ 사용자 프로필    │ "19년차 시니어, 미국 빅테크 도전 준비"   │
├───────────┼──────────────────┼──────────────────────────────────────────┤
│ feedback  │ 작업 방식 피드백 │ "플랜에 금지사항을 넣어달라"             │
├───────────┼──────────────────┼──────────────────────────────────────────┤
│ project   │ 프로젝트 상태    │ "v4.8에서 AI 백엔드 확장 완료"           │
├───────────┼──────────────────┼──────────────────────────────────────────┤
│ reference │ 외부 리소스 위치 │ "버그는 Linear INGEST 프로젝트에서 추적" │
└───────────┴──────────────────┴──────────────────────────────────────────┘

### 플랜에 Memory 저장을 넣은 이유

feedback 타입으로 "플랜 작성 시 반드시 6개 섹션 포함"을 저장하면:
- 다음 대화에서도 Claude가 이 선호를 기억한다.
- CLAUDE.md가 주 방법이고, Memory는 보조 안전망이다.

솔직히 말하면 — CLAUDE.md에 템플릿을 넣으면 Memory 저장은 부차적이다. Claude Code가 CLAUDE.md를 매 세션마다 자동 로드하기 때문이다. Memory는 "왜 이 템플릿을 쓰게 되었는지" 같은 맥락 저장에 더 유용하다.

핵심 정리: Memory는 "대화 간 기억 유지" 도구. 플랜 템플릿 자동화의 주력은 CLAUDE.md, Memory는 보조.


## Q4. CLAUDE.md가 비대해지면 어떻게 관리하나?

근거 소스: Claude Code 공식 문서 (memory.md, hooks.md)

### 공식 권장: 200줄 이하

> "200줄 이하를 목표로 하라. 길어지면 컨텍스트를 더 소모하고 준수율이 떨어진다."

비유: 학교 규칙이 1,000개면 아무도 다 기억 못 하지만, 10개면 다 지킨다.

### 해결 방법 세 가지

*방법 1: .claude/rules/ 디렉토리 (공식 권장)*

.claude/
├── CLAUDE.md              ← 핵심만 (< 200줄)
└── rules/
    ├── plan-template.md   ← 플랜 템플릿 규칙
    ├── code-style.md      ← 코딩 스타일
    └── api-design.md      ← API 설계 규칙

rules의 핵심 장점: globs 프론트매터로 조건부 로딩이 가능하다.

```yaml
---
globs: .claude/plans/**/*
---
```

```
# 플랜 작성 시 반드시 포함할 섹션
1. 완료조건.
2. 금지사항.
...
```

globs 스코핑을 적용하면 플랜 파일을 다룰 때만 규칙을 로드한다. 평소에는 컨텍스트를 차지하지 않는다.

> 주의: `paths:` YAML 배열 형식에는 버그가 있으므로, `globs:` + 콤마 구분 형식을 사용할 것 (2026년 2월 현재).

*방법 2: @import 구문*

CLAUDE.md에서 외부 파일을 참조한다:

```
# 프로젝트 규칙
@.claude/rules/plan-template.md
@.claude/rules/code-style.md
```

주의: @import된 파일은 세션 시작 시 전부 로드된다 (on-demand 아님). 따라서 컨텍스트 절약 효과는 없고, 정리와 구조화 목적으로만 유용하다.

*방법 3: 지시형 참조 (on-demand 로딩)*

```
# 플랜 작성 규칙
플랜을 작성할 때는 반드시 .claude/rules/plan-template.md 를 읽고 따를 것.
```

지시형 참조 방식은 @import와 달리 자동 로드되지 않는다. Claude가 필요할 때 Read 도구로 읽는다.

### "연결된 문서는 system prompt에 올라가나? context 뒤에 붙나?"

CLAUDE.md 자체는 system prompt가 아니다. 공식 문서에 따르면:

> "CLAUDE.md는 system prompt가 아니라 user message로 전달된다."

┌─────────────────────────────┐
│ System Prompt               │  ← Claude의 기본 동작 지시
├─────────────────────────────┤
│ CLAUDE.md (user message)    │  ← 여기에 주입됨
├─────────────────────────────┤
│ 대화 기록                    │  ← user/assistant 메시지들
├─────────────────────────────┤
│ Read 도구로 읽은 파일 내용    │  ← 지시형 참조 시 여기에 추가
└─────────────────────────────┘

- @import: 세션 시작 시 Claude Code가 CLAUDE.md와 함께 상단에 로드한다.
- 지시형 참조 ("~를 읽어라"): 대화 중간에 Read 결과로 추가한다 → 컨텍스트 뒤쪽에 위치한다.

> 단, "CLAUDE.md가 user message로 전달"된다는 주장은 공식 문서에서 명시적으로 검증되지 않았다 (UNGROUNDED). 전달 방식의 정확한 구현은 Claude Code 내부 동작에 의존한다.

### "Lost in the Middle" 우려는?

맞는 우려다. 하지만:
- CLAUDE.md는 매 턴마다 재주입된다 (컨텍스트 압축 시에도).
- rules/ 파일도 조건 매칭 시 재주입된다.
- 지시형 참조로 읽은 내용은 해당 턴의 최근 컨텍스트에 위치하므로 오히려 잘 보인다.

### 최종 권장 구조

```
~/.claude/
├── CLAUDE.md                    ← 응답 가이드라인 (기존, ~15줄)
└── rules/
    └── plan-template.md         ← 플랜 템플릿 규칙 (~30줄, globs 스코핑)
```

핵심 정리: rules/ 디렉토리 + globs 스코핑이 정답. CLAUDE.md는 핵심만, 세부 규칙은 rules/로 분리.


## Q5. Hook Latency — 무슨 말인가?

근거 소스: Claude Code 공식 hooks 문서

### 비유

Hook은 도로 검문소와 같다. 메시지를 보내면(차가 출발하면), Hook이 먼저
실행된다(검문소를 통과해야 한다). Claude Code는 Hook이 끝날 때까지 기다린다.

```
당신 메시지 → [Hook 실행 (대기)] → Claude 처리 시작
              ↑ 이 시간이 latency
```

### 실제 영향

┌─────────────────┬───────────┬───────────┐
│    Hook 내용    │ 실행 시간 │   체감    │
├─────────────────┼───────────┼───────────┤
│ 단순 grep 검사  │ ~50ms     │ 무시 가능 │
├─────────────────┼───────────┼───────────┤
│ 복잡한 스크립트 │ 1-5초     │ 약간 느림 │
├─────────────────┼───────────┼───────────┤
│ 외부 API 호출   │ 5초+      │ 체감됨    │
└─────────────────┴───────────┴───────────┘

> Hook은 기본적으로 동기 실행이지만, `async: true` 설정으로 비동기 실행도 가능하다.

### 왜 플랜에 언급했나

"리마인더 Hook을 추가하면 매번 메시지 전송 시 약간의 지연이 생긴다"는 트레이드오프를 알려드린 것이다. 단순 grep 정도면 사실상 무시할 수 있는 수준이고, CLAUDE.md + rules가 충분하면 Hook은 필요 없다.

핵심 정리: Hook은 메시지 전송 전에 실행되는 검문소. 단순한 건 체감 안 되지만, 불필요하면 안 넣는 게 좋다.

---

## 검증 이력

이 문서는 수렴 검증(rl-verify)을 거쳤다.

- 검증 리포트: `docs/demiurge/rl-verify/every-style-edit-verify/report.md`
- 검증 방법: Every 스타일 가이드 적용 → CONTRARIAN + ARCHITECT + SIMPLIFIER + EVALUATOR x3
- 수렴: 3회 iteration, 12개 발견사항 모두 안정 카운터 >= 2

### 검증으로 반영된 주요 수정

| # | 수정 내용 | 근거 |
|---|-----------|------|
| 1 | `**bold**` → `*italic*` (3곳) | Every "never bold" 규칙. 최초 수정에서 누락된 가장 큰 맹점 |
| 2 | em dash 앞뒤 공백 유지 (` — `) | 한국어 타이포그래피 관례 우선. 한글+em dash 밀착 시 가독성 저하 |
| 3 | `paths:` → `globs:` (프론트매터 키) | `paths:` YAML 배열에 버그 존재, `globs:` 콤마 구분이 공식 권장 |
| 4 | "이렇게 하면" → "globs 스코핑을 적용하면" | "This" 회피 규칙 일관 적용 |
| 5 | "Lost in the middle" → "Lost in the Middle" | headline 내 영어 title case |
| 6 | 능동태 전환 시 주어 보충 | "로드한다" → "Claude Code가 로드한다" 등 주어 명시 |
| 7 | UNGROUNDED 주장에 주석 추가 | "user message로 전달" 주장에 검증 불가 표기 |
| 8 | Hook async:true 비동기 가능 주석 추가 | 기본 동기이나 비동기도 가능함을 명시 |
