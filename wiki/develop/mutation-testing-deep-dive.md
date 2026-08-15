---
tags: [testing, mutation-testing, test-coverage, tdd]
created: 2026-08-15
---

# Mutation Testing (뮤테이션 테스트, 돌연변이 테스트)

## 한 줄 정의

**Mutation Testing**: "테스트가 실행됐는가"가 아니라 **"테스트가 실제로 버그를 잡아내는가"를 검증하는 기법**. Coverage(커버리지) 툴의 근본적 한계를 보완하기 위해 나왔다.

## 왜 필요한가 — Coverage와의 차이

```
📏 일반 Coverage 툴이 확인하는 것
   "이 코드 줄이 테스트 중에 실행됐는가?"
   → 실행만 되면 OK. assert(검증)가 있는지는 안 봄.

🧬 Mutation Testing이 확인하는 것
   "이 코드 줄을 고의로 망가뜨리면, 테스트가 그걸 눈치채는가?"
   → 안 눈치채면 = 그 테스트는 사실상 그 코드를 지켜주지 못하고 있다는 뜻
```

## 동작 방식 (Step by Step)

예시 코드:

```python
def get_display_name(user):
    if not user.nickname:
        return user.email
    return user.nickname
```

1. **원본 코드**에 테스트를 통과시킨다 (모두 GREEN 상태)
2. 툴이 코드를 자동으로 살짝 바꾼 복사본 — **mutant(변이체)** — 을 여러 개 만든다:
   - Mutant A: `if not user.nickname` → `if user.nickname` (조건 반전)
   - Mutant B: `return user.email` → `return None` (반환값 변경)
   - Mutant C: `not user.nickname` → `not user.email` (비교 대상 변경)
3. **각 mutant에 대해 기존 테스트 스위트 전체를 다시 실행**한다.
4. 결과를 두 가지로 분류한다:
   - **Killed (죽은 mutant)**: 테스트가 실패함 → 이 테스트가 이 변화를 실제로 감지했다는 증거. 좋은 신호.
   - **Survived (살아남은 mutant)**: 테스트가 여전히 통과함 → 이 코드가 이렇게 바뀌어도 아무 테스트도 못 알아챈다는 뜻. 이게 테스트의 빈 구멍.

```
┌─────────────┐    코드 변이     ┌──────────────┐   테스트 재실행   ┌──────────────┐
│ 원본 코드     │ ─────────────→ │ Mutant 생성   │ ──────────────→ │ 결과 판정      │
│ (모든 테스트  │                │ (조건/상수/   │                 │ Killed  or    │
│  통과 상태)   │                │  리턴값 변경) │                 │ Survived      │
└─────────────┘                └──────────────┘                 └──────────────┘
```

## 실패 시나리오: coverage 100%인데 버그가 남아있는 경우

`get_display_name(user)` 예시로 이어서:

- `nickname=""` 로 테스트 1개만 작성해도 **branch coverage 100%**를 달성한다 (falsy 분기 1번, truthy 분기는 다른 테스트로 커버).
- 이후 누군가 `return user.email.split('@')[0]` 로 코드를 바꿨다고 하자. 레거시 계정 중 `email=None`인 경우가 있다면 프로덕션에서 `AttributeError`가 발생한다.
- **line/branch coverage 리포트는 여전히 100%를 보여준다.** `nickname`의 falsy 여부만 분기로 잡혔지, `email`이 None인 경우는 애초에 별도 분기가 아니었기 때문이다.
- Mutant B(`return user.email` → `return None`)를 넣었을 때, 테스트가 "email 필드의 실제 값"을 assert하지 않고 그냥 "함수가 에러 없이 리턴되는지"만 확인하는 수준이었다면 이 mutant는 **survived**로 남는다. 리포트에 뜨는 순간 "이 부분은 값 자체를 검증하는 테스트가 없었다"는 게 드러난다 — line coverage 100%였어도.

> ⚠️ 주의: mutation testing도 만능은 아니다. "어떤 입력값으로 테스트할지"는 여전히 사람이 정해야 하고, 애초에 `email=None`을 테스트 케이스로 넣은 적이 없다면 mutation testing도 그 케이스 자체를 만들어주지는 못한다. 다만 "지금 있는 테스트가 얼마나 허술한지"는 훨씬 정확하게 드러내 준다.

## Coverage 종류별 비교

| 구분              | 확인하는 것                     | email=None 시나리오 탐지 여부                                  |
| ----------------- | -------------------------------- | ---------------------------------------------------------------- |
| Line coverage     | 이 줄이 실행됐는가               | 못 잡음                                                           |
| Branch coverage   | 이 분기가 양쪽 다 실행됐는가     | 못 잡음 (같은 분기를 다른 값으로 탔을 뿐이라 구분 안 됨)          |
| Mutation testing  | 코드를 바꿔도 테스트가 눈치채는가 | 테스트에 값 검증(assert)이 있으면 잡음 — 테스트를 강화해야 한다는 신호를 줌 |

Error(예외) 케이스는 예외적으로 branch coverage로도 상당 부분 잡을 수 있다: `except ValueError / except TypeError / except KeyError`처럼 여러 except 절은 제어 흐름 그래프(CFG)상 서로 다른 분기(arc)이기 때문에, **line coverage가 아니라 branch coverage 100%를 요구**하면 특정 예외 타입만 테스트하고 나머지를 안 건드린 경우를 미달로 표시해준다.

## 용어 정리

| 용어                        | 의미                                                    |
| --------------------------- | -------------------------------------------------------- |
| Mutant (변이체)             | 코드를 한 군데 고의로 바꾼 복사본                        |
| Killed (죽음)               | 테스트가 그 변화를 감지해 실패함 → 좋은 결과              |
| Survived (생존)             | 테스트가 못 알아채고 통과함 → 테스트 구멍                 |
| Mutation Score (뮤테이션 점수) | Killed 비율(%) — 테스트 스위트가 실제로 얼마나 튼튼한가의 지표 |

## 실무 도구 (언어별)

| 언어                | 도구                       |
| ------------------- | -------------------------- |
| Python              | `mutmut`, `cosmic-ray`      |
| JavaScript/TypeScript | `Stryker`                 |
| Go                  | `go-mutesting`             |
| Java/Kotlin         | `PIT` (pitest)              |

## 알아둘 트레이드오프

- **느림**: mutant 하나마다 전체 테스트 스위트를 다시 돌리기 때문에, mutant가 100개면 테스트 스위트를 100번 도는 것과 비슷하다 → 보통 매 커밋(commit)마다는 안 돌리고 **야간 CI(지속적 통합)나 주기적 스팟체크**로 쓴다.
- coverage %는 게임(gaming)하기 매우 쉬운 지표다 — assertion 없이 코드만 실행하는 테스트도 coverage 툴은 "커버됨"으로 계산한다. 업계에서 "커버리지 90% 팀이 여전히 버그를 양산한다"는 사례가 흔한 이유이기도 하다 (Goodhart's Law: 지표가 목표가 되는 순간 좋은 지표이길 멈춘다).

## 실무 적용: 테스트 카테고리 규칙(Happy/Boundary/Error)을 coverage 툴로 대체할 수 있는가

**배경**: 개인 전역 `CLAUDE.md`에는 TDD(Test-Driven Development)의 RED phase에서 `[Happy]`/`[Boundary]`/`[Error]` 3개 카테고리 각 최소 1개 이상을 요구하는 규칙이 있다. 이미 사용 중인 superpowers `test-driven-development` 스킬에도 "edge cases and errors covered" 체크리스트와 Mutation Check(코드를 고의로 망가뜨려 테스트가 잡는지 확인)가 있어 방향성이 겹친다 — 이 규칙을 없애고 coverage 툴로 보완할 수 있는지가 쟁점이었다.

**결론부터**: 카테고리별로 coverage 툴의 대체 가능 여부가 다르다. 하나의 숫자(coverage %)로 뭉뚱그려 판단하면 안 된다.

| 카테고리 | 순수 line coverage로 대체 | branch coverage 100%로 대체 | 근본적 한계 |
| --------- | -------------------------- | ----------------------------- | ------------------------------------------------- |
| `[Happy]`    | 불가                          | 부분적                            | 코드가 실행됐다는 것만 확인, assertion 품질은 못 잼    |
| `[Boundary]` | 불가                          | 불가                              | 같은 분기를 타는 다른 값(None vs "" vs 0)을 구분 못함 |
| `[Error]`    | 불가                          | 대부분 가능                        | except 절이 서로 다른 분기(CFG arc)라 branch coverage 100% 요구 시 개별 예외 타입 누락이 잘 잡힘 |

**핵심 실패 시나리오** (위 "실패 시나리오" 절의 `email=None` 예시와 동일): `[Boundary]` 규칙이 막으려던 게 정확히 "같은 분기를 타는 서로 다른 falsy 값"이었는데, coverage 툴은 분기 자체만 보고 어떤 값으로 탔는지는 구분하지 않는다. 그래서 `[Boundary]`는 coverage로 대체 불가.

또한 coverage %는 게임하기 쉬운 지표다: assertion 없이 코드만 실행하는 테스트도 100% coverage로 잡힌다. 반대로 mutation testing은 "코드를 실제로 바꿔도 테스트가 눈치채는가"를 확인하므로, `[Happy]` 카테고리가 요구하는 "정상 흐름이 올바른 결과를 내는지 검증했는가"에 훨씬 가깝게 근접한다.

### 대안 비교

| 방안 | 내용 | 트레이드오프 |
| ----- | ---------------------------------------------- | ------------------------------------------------------------------------------- |
| A. 순수 coverage %만 | line 또는 branch coverage 임계값만 강제 | 구현은 가장 쉽지만 `[Boundary]` 누락을 못 잡고, 형식적(assertion 없는) 테스트로 숫자만 채울 위험 |
| B. coverage(branch) + mutation testing 병행 (추천) | line 대신 branch coverage 기준 사용 + mutation testing 툴(언어별 도구는 위 표 참고) 병행 | `[Error]`는 branch coverage로, `[Happy]`/`[Boundary]` 품질은 mutation testing으로 상당 부분 커버. 다만 mutation testing은 느려서 매 커밋이 아니라 야간 CI 등 주기적 실행이 적합 |
| C. CLAUDE.md 규칙 완전 삭제, 툴 도입 안 함 | 규칙만 제거 | 비추천 — 안전장치 없이 규칙만 사라짐 |

**판단**: B안이 가장 균형 잡힌 선택이다 — CLAUDE.md의 숫자 강제(카테고리당 최소 1개)가 만들 수 있는 "형식적 테스트" 리스크는 없애면서, `[Error]`는 branch coverage로, 나머지 품질 판단은 mutation testing이라는 자동화된 안전망으로 대체한다.

## 관련 노트

- [[spring-di-bean-test-deep-dive]] — Mutation Testing(PIT/pitest)이 한 줄로 언급됨, line/branch coverage 비교표도 있음
