---
created: 2026-02-13
source: claude-code
tags:
  - ralph-loop
  - claude-code
  - ai-development
  - automation
---

# Ralph Loop (Ralph Wiggum Technique) - Deep Research

> 조사일: 2026-02-13 | 수집 출처: 12+

## Executive Summary

**Ralph Loop**은 Geoffrey Huntley가 발명한 **자율 AI 개발 루프 기법**으로, Claude Code에 동일한 프롬프트를 반복적으로 주입하여 작업이 완료될 때까지 자동으로 반복 실행하는 방법론.

**핵심 인사이트**: "큰 일을 한 번에 시키는 것"이 아니라 "같은 지시를 반복해서 주면서 스스로 개선하게 하는 것"

## 동작 원리

```
while :; do cat PROMPT.md | claude-code ; done
```

1. 사용자가 `/ralph-loop` 명령 실행
2. `setup-ralph-loop.sh`가 `.claude/ralph-loop.local.md` 상태 파일 생성
3. Claude Code가 작업 수행 후 종료 시도
4. Stop Hook이 종료를 가로채고 동일 프롬프트를 재주입
5. Claude는 이전에 자기가 수정한 파일과 git 히스토리를 읽고 점진적으로 개선
6. `<promise>COMPLETE</promise>` 출력 시 루프 종료

## 3대 핵심 메커니즘

| 메커니즘          | 설명                                                     |
| ----------------- | -------------------------------------------------------- |
| Stop Hook         | Claude의 종료를 가로채는 hook → 루프의 엔진              |
| Completion Promise | 완료를 신호하는 `<promise>COMPLETE</promise>` → 탈출 조건 |
| 상태 파일         | `.claude/ralph-loop.local.md` → 반복 횟수, 활성 여부, 프롬프트 저장 |

## 적합/부적합 작업

### 적합

- 그린필드 프로젝트 (명확한 PRD로 처음부터 구축)
- TDD 기반 개발 (테스트가 객관적 완료 기준)
- 대규모 리팩터링 (반복적 수정+테스트 사이클)
- 배치 작업 (동일 패턴의 반복 작업)
- 문서 생성 (코드에서 문서 추출+검증)

### 부적합

- UI/UX 디자인 (주관적 판단 필요)
- 아키텍처 설계 (인간의 의사결정 필요)
- 프로덕션 디버깅 (목표가 불명확)
- 보안 관련 작업 (높은 정확도 필요)
- 불명확한 요구사항 (완료 기준을 정의할 수 없음)

## 프롬프트 작성 베스트 프랙티스

### 1. 명확한 완료 기준

```
Build a REST API for todos.
When complete:
- [ ] All CRUD endpoints working
- [ ] Input validation in place
- [ ] Tests passing (coverage > 80%)
- Output: <promise>COMPLETE</promise>
```

### 2. 단계별 목표

```
Phase 1: User authentication (JWT, tests)
Phase 2: Product catalog (list/search, tests)
Phase 3: Shopping cart (add/remove, tests)
Output <promise>COMPLETE</promise> when ALL phases done.
```

### 3. 자기 수정 패턴 (TDD)

```
1. Write failing tests
2. Implement feature
3. Run tests
4. If any fail, debug and fix
5. Refactor if needed
6. Repeat until all green
7. Output: <promise>COMPLETE</promise>
```

### 4. 2-Phase 워크플로우

- Phase 1: 대화를 통해 스펙/PRD 작성 → Markdown 파일로 저장
- Phase 2: 새 컨텍스트에서 플랜 문서만 피드 → Ralph Loop으로 자율 실행
- 분리 이유: 컨텍스트 윈도우 오염 방지

## 필수 안전 장치 체크리스트

```
[ ] --max-iterations 설정 (권장: 20~50)
[ ] completion-promise 명확히 정의
[ ] 자동 검증 수단 확보 (테스트, 린터)
[ ] 스펙에 "하지 말 것" 명시
[ ] git으로 복구 가능한 상태 (작업 전 커밋)
[ ] 비용 제한/알림 설정
[ ] 첫 2~3번 반복을 직접 관찰
```

## 변형 비교

| 기준     | Original        | Official Plugin | Smart Ralph | Ralph Orchestrator |
| -------- | --------------- | --------------- | ----------- | ------------------ |
| 구현     | Bash while 루프 | Stop Hook       | Spec-driven | Multi-backend      |
| 복잡도   | 매우 단순       | 단순            | 중간        | 복잡               |
| 적합 규모 | 소규모          | 중소규모        | 중규모      | 대규모             |

## 주요 출처

1. ghuntley.com/ralph/ — 원작자
2. Anthropic Claude Code 공식 플러그인
3. ghuntley.com/loop/ — 원작자
4. github.com/mikeyobrien/ralph-orchestrator
5. github.com/tzachbon/smart-ralph
