---
created: 2026-02-10
source: claude-code
tags:
  - trunk-based-development
  - branching-strategy
  - git
  - release-management
---

# Scaled Trunk-Based Development — 종합 정리

> 💡 **한줄 요약**: 대규모 팀이 하나의 trunk에서 협업하되, short-lived feature branch + feature flag + release branch cherry-pick으로 안정성과 속도를 동시에 확보하는 브랜칭 전략

---

## 1. Scaled TBD란

단일 trunk에서 모든 개발자가 협업하되, **short-lived feature branch**(수 시간~2-3일) + **feature flag** + **release branch cherry-pick**으로 대규모 팀의 안정성과 속도를 동시에 확보하는 브랜칭 전략.

> *"A source-control branching model, where developers collaborate on code in a single branch called 'trunk', resist any pressure to create other long-lived development branches by employing documented techniques."*
> — [trunkbaseddevelopment.com](https://trunkbaseddevelopment.com/)

- **기원**: Paul Hammant이 [trunkbaseddevelopment.com](https://trunkbaseddevelopment.com/)에서 체계화. Google, Facebook(Meta) 등 대규모 조직의 실무에서 발전
- **탄생 배경**: Git Flow의 long-lived branch가 대규모 팀에서 merge conflict, 통합 지연, branch 관리 복잡도를 유발하는 문제를 해결하기 위해 등장

> 📌 **핵심 키워드**: `trunk`, `short-lived branch`, `feature flag`, `cherry-pick forward`, `continuous integration`, `release branch`

---

## 2. 핵심 원칙 4가지

### 원칙 1: Trunk = Single Source of Truth

모든 코드 변경은 trunk에서 시작. Long-lived branch 생성 금지.

### 원칙 2: Fix on Trunk First, Cherry-pick to Release

버그/보안 수정은 **반드시 trunk에서 먼저** → release branch로 `cherry-pick -x`. 역방향(release → trunk merge) 금지.

### 원칙 3: Release Branch는 임시, Merge Back 금지

release branch는 just-in-time 분기, cherry-pick만 허용, 릴리스 완료 후 삭제(태그는 보존).

### 원칙 4: Feature Flag로 미완성 기능 격리

미완성 기능은 flag OFF 상태로 trunk에 merge. Long-lived feature branch 불필요.

---

## 3. 핵심 구성 요소

```
┌───────────────────────────────────────────────────────────────────┐
│                   Scaled TBD 핵심 구성 요소                        │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────┐  │
│  │  🌳 Single      │    │  🚩 Feature      │    │ 🏷️ Release  │  │
│  │     Trunk       │◄──►│     Flags        │    │    Branch   │  │
│  │  (단일 메인)    │    │  (기능 격리)      │    │  (릴리스용) │  │
│  └────────┬────────┘    └────────┬─────────┘    └──────┬──────┘  │
│           │                      │                      │         │
│           ▼                      ▼                      ▼         │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────┐  │
│  │  🔀 Short-lived │    │  🔄 Continuous   │    │ 🍒 Cherry   │  │
│  │     Feature BR  │    │     Integration  │    │    -pick    │  │
│  │  (수시간~수일)  │    │  (지속적 통합)    │    │  (버그수정) │  │
│  └─────────────────┘    └──────────────────┘    └─────────────┘  │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

| 구성 요소                      | 역할                | 설명                                                                                  |
| ------------------------------ | ------------------- | ------------------------------------------------------------------------------------- |
| **Single Trunk**               | 유일한 통합 지점    | 모든 코드가 궁극적으로 합류하는 단일 브랜치. Long-lived branch 생성 금지               |
| **Short-lived Feature Branch** | 코드 리뷰/CI        | 수 시간~최대 2-3일. PR 리뷰 + CI 통과 후 즉시 trunk merge. 소규모 TBD와의 핵심 차이점 |
| **Feature Flags**              | 미완성 기능 격리    | 코드는 trunk에 merge하되 flag로 비활성화. Long-lived branch 필요성 제거                |
| **Release Branch**             | 릴리스 안정화       | trunk에서 just-in-time으로 분기. 추가 개발 금지, cherry-pick만 허용                    |
| **Cherry-pick Forward**        | 버그/보안 수정 방향 | **반드시 trunk에서 먼저 수정** → release branch로 cherry-pick. 역방향 금지             |
| **Continuous Integration**     | 품질 게이트         | 모든 커밋에 대해 자동 빌드/테스트. 깨진 trunk은 최우선 수정 대상                       |

---

## 4. 아키텍처와 동작 원리

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Scaled TBD 전체 흐름도                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Developer A    Developer B    Developer C                              │
│      │              │              │                                    │
│      ▼              ▼              ▼                                    │
│  ┌───────┐     ┌───────┐     ┌───────┐                                 │
│  │feat/x │     │feat/y │     │fix/z  │  ◄── Short-lived branches       │
│  │(2시간)│     │(1일)  │     │(30분) │      (수 시간 ~ 최대 수 일)     │
│  └───┬───┘     └───┬───┘     └───┬───┘                                 │
│      │    PR+CI    │    PR+CI    │  PR+CI                               │
│      ▼             ▼             ▼                                      │
│  ════╪═════════════╪═════════════╪════════════════  trunk               │
│      A             B             C     D     E                          │
│                                        │                                │
│                              ┌─────────┘  (just-in-time 분기)          │
│                              ▼                                          │
│                    ┌──────────────────┐                                  │
│                    │ release/v1.0     │  ◄── Release branch             │
│                    │  (추가개발 금지)  │      (cherry-pick만 허용)       │
│                    └────────┬─────────┘                                  │
│                             │                                           │
│  trunk에서 bug fix ─────────┤                                           │
│        commit F      cherry-pick -x                                     │
│                             │                                           │
│                         🏷️ v1.0-rc1                                     │
│                         🏷️ v1.0 (GA)                                    │
│                             │                                           │
│                    branch 삭제 (태그 보존)                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (Step by Step)

1. **Feature 개발**: 개발자가 trunk에서 short-lived feature branch 생성 (수 시간~최대 수 일)
2. **PR + CI**: Pull Request 생성 → 자동 빌드/테스트 + 코드 리뷰
3. **Trunk 통합**: CI 통과 + 리뷰 승인 시 **즉시 trunk에 merge**
4. **미완성 기능**: Feature flag로 감싸서 trunk에 merge (flag OFF 상태)
5. **릴리스 준비**: 릴리스 직전에 trunk에서 release branch **just-in-time** 분기
6. **버그 수정**: trunk에서 **먼저** 수정 → release branch로 `git cherry-pick -x` (출처 커밋 기록)
7. **릴리스**: release branch에서 태그 발행 → 배포
8. **정리**: 릴리스 활동 종료 후 release branch 삭제 (태그는 영구 보존)

```bash
# Cherry-pick Forward 워크플로우 예시
git checkout trunk
git commit -m "fix: CVE-XXXX-YYYY 보안 취약점 수정"  # trunk에서 먼저 수정

git checkout release/v1.0
git cherry-pick -x abc123f    # -x: "(cherry picked from commit abc123f)" 기록
git tag v1.0.1-rc1
```

---

## 5. 왜 Release Branch를 분리하는가

```
release branch 없이 (trunk freeze 필요):

trunk: ──A──B──C── 🔒FREEZE── QA ── bugfix ── 🏷️GA ──D──E──
                   │                                  │
                   └─── 모든 개발자 작업 중단 ────────┘

release branch 분리 (trunk 개발 계속):

trunk:   ──A──B──C──D──E──F──G──   (개발 멈추지 않음)
                   │
                   └─▶ release/v1.0 ── QA ── bugfix ── 🏷️GA
                       (안정화만 집중)
```

| 이점             | 설명                                                       |
| ---------------- | ---------------------------------------------------------- |
| 개발 속도 유지   | trunk을 freeze하지 않아 전체 팀의 작업이 중단되지 않음     |
| 릴리스 범위 확정 | 분기 시점에 릴리스에 포함될 코드가 확정됨                   |
| 병렬 안정화      | QA/버그수정이 신규 개발과 독립적으로 진행                   |

---

## 6. 왜 Trunk First인가 (역방향 금지 이유)

"release에서 수정하고 trunk에 merge하면 안 되나?"라는 자연스러운 의문에 대한 답:

### 이유 1: "잊어버림" 방지 (가장 흔함)

```
release에서 버그 수정 → "나중에 trunk에도 반영해야지" → 잊음
→ 다음 릴리스에 같은 버그 재발

trunk first면 → 수정이 이미 trunk에 있으므로 다음 릴리스에 자동 포함
```

### 이유 2: Release-specific 코드 오염 방지

release branch에는 버전 번호, 환경 설정, 임시 workaround 등 릴리스 전용 변경이 있을 수 있음. 이것을 trunk에 merge하면 의도치 않은 변경이 유입됨.

### 이유 3: Merge conflict 규모 차이

```
cherry-pick (trunk → release):  단일 커밋 diff → conflict 범위 제한적
merge (release → trunk):        release의 모든 변경 vs trunk의 수십~수백 커밋 → 거대한 conflict
```

> *"You should not fix bugs on the release branch in the expectation of cherry-picking them back to the trunk."*
> — [trunkbaseddevelopment.com/branch-for-release](https://trunkbaseddevelopment.com/branch-for-release/)

---

## 7. 대규모 리팩토링 후 Cherry-pick 불가능 상황

trunk에서 대규모 리팩토링이 일어나면, 리팩토링 전 release branch로의 cherry-pick이 실패할 수 있다. 이것은 Scaled TBD의 현실적 한계.

### Cherry-pick 성공률과 divergence 기간

```
divergence 기간  │  cherry-pick 성공률  │  대응 전략
─────────────────┼──────────────────────┼────────────────
1-2주            │  ~95%               │  정상 cherry-pick
1-2개월          │  ~70%               │  minor conflict 해결
3개월+           │  ~30%               │  수동 백포트 필요
6개월+           │  ~10%               │  사실상 재작성
```

### 해결 방법 4가지

**방법 1: Manual Backport (수동 백포트)** — 가장 일반적

cherry-pick이 아닌, **같은 의도의 수정을 해당 코드 구조에 맞게 재작성**. Linux kernel이 수십 년간 사용해온 표준 방식.

> *"Backporting is not just cherry-picking. It is adapting the fix to the older codebase."*
> — [docs.kernel.org/process/backporting.html](https://docs.kernel.org/process/backporting.html)

```bash
git cherry-pick -x abc123    # 실패!
git cherry-pick --abort

# trunk의 수정 의도를 이해하고, release branch 코드에 맞게 수동 수정
git checkout release/v1.0
# 직접 수정 작성
git commit -m "fix: CVE-XXXX 수동 백포트 (원본: abc123)"
```

**방법 2: Release branch에서 직접 수정 (원칙의 예외)**

조건: trunk에 이미 동일 의도의 수정이 존재하고, release → trunk merge는 하지 않는 경우에만 허용.

**방법 3: 예방 — Branch by Abstraction (점진적 리팩토링)**

대규모 리팩토링을 cherry-pick 친화적으로 수행:

```
┌──────────────────────────────────────────────────┐
│        Branch by Abstraction                      │
├──────────────────────────────────────────────────┤
│                                                   │
│  Phase 1: 추상화 레이어 도입 (기존 코드와 공존)   │
│  Client ──▶ Abstraction Layer ──▶ Old Code       │
│                                                   │
│  Phase 2: 새 구현 추가 (Feature Flag OFF)         │
│  Client ──▶ Abstraction Layer ──┬▶ Old Code      │
│                                 └▶ New Code (OFF) │
│                                                   │
│  Phase 3: 전환 완료, 기존 코드 제거               │
│  Client ──▶ Abstraction Layer ──▶ New Code       │
│                                                   │
└──────────────────────────────────────────────────┘

각 Phase가 작은 커밋 → cherry-pick 가능성 유지
Big Bang 리팩토링(50개 파일 한번에 변경) 회피
```

**방법 4: Release branch 수명 관리 (EOL 정책)**

release branch를 오래 유지할수록 trunk과의 divergence가 커지므로, **EOL 정책을 명확히 정의**하여 cherry-pick 불가능 상황 자체를 줄임.

---

## 8. Scaled TBD vs Git Flow vs GitHub Flow

| 기준                   | Scaled TBD                | Git Flow                   | GitHub Flow             |
| ---------------------- | ------------------------- | -------------------------- | ----------------------- |
| **커밋 방식**          | short-lived branch → PR   | feature branch → develop   | feature branch → main   |
| **Feature branch 수명** | 수 시간~2-3일             | 수 일~수 주               | 수 시간~수 일           |
| **Long-lived branch**  | trunk만                   | main + develop             | main만                  |
| **Release branch**     | just-in-time, 임시        | develop → release → main   | 없음 (main = 배포)      |
| **Feature flag**       | **필수**                  | 불필요                     | 권장                    |
| **버그 수정 방향**     | trunk → cherry-pick       | hotfix → main + develop    | main 직접               |
| **적합 팀 규모**       | 10명~수천 명              | 5-50명                     | 5-20명                  |
| **Multi-product**      | **최적**                  | 복잡 (브랜치 폭발)         | 어려움                  |
| **CI/CD 요구 수준**    | 매우 높음                 | 중간                       | 높음                    |

### Git Flow로 전환해도 해결되지 않는 문제들

| 문제                           | Git Flow에서의 상황                                                        |
| ------------------------------ | -------------------------------------------------------------------------- |
| 보안 패치 다중 적용            | 동일 — main, develop, release 3곳에 적용 필요                              |
| Long-lived feature branch      | 악화 — Git Flow는 feature branch 장기 유지 경향                            |
| Multi-product 릴리스 독립성    | 악화 — 단일 제품 기준 설계, multi-product에서 branch 수 폭발               |

> Vincent Driessen(Git Flow 창시자)의 2020년 3월 reflection:
> *"I would suggest to adopt a much simpler workflow (like GitHub flow) instead of trying to shoehorn git-flow into your team."*
> — [nvie.com](https://nvie.com/posts/a-successful-git-branching-model/)
>
> (주의: "trunk-based"라는 용어를 직접 사용한 것은 아니며, "GitHub Flow 같은 더 단순한 워크플로우"를 추천)

### 🤔 언제 무엇을 선택?

- **Scaled TBD를 선택하세요** → 10명 이상, Monorepo, CI/CD 파이프라인 성숙, 다제품/다팀 환경
- **Small-team TBD를 선택하세요** → 5명 이하, 높은 신뢰도, 페어 프로그래밍 문화
- **Git Flow를 선택하세요** → 긴 릴리스 주기, 다중 버전 동시 유지보수, CI/CD 미성숙
- **GitHub Flow를 선택하세요** → SaaS/웹, 단일 제품, 빠른 배포 주기, 소규모~중규모 팀

---

## 9. Multi-product Monorepo에서의 Scaled TBD

### 제품별 독립 Release Branch 전략

```
네이밍 규칙: release/{product}/{version}

trunk:  ──A──B──C──D──E──F──
              │         │
              ▼         ▼
     release/product-a/v1.0    release/product-b/v2.0
        (A 제품 릴리스)            (B 제품 릴리스)
```

### Cherry-pick Forward 프로세스

```
trunk:  ──A──B──[security-fix]──C──D──
                     │
           cherry-pick (최신 → 오래된 순)
                     │
           ┌─────────┼─────────┐
           ▼         ▼         ▼
    release/a/v1.1  release/b/v2.0  (다른 release branch)
```

워크플로우:

1. 보안 스캐너에서 이슈 발견
2. **trunk에서 수정 PR 생성 + 테스트**
3. trunk merge 후 CI 통과 확인
4. cherry-pick 스크립트로 **각 활성 release branch에 자동 PR 생성**
5. 각 branch에서 독립 CI + 리뷰
6. 각 branch에서 patch 버전 태그

(참고: Kubernetes의 `hack/cherry_pick_pull.sh` — [github.com/kubernetes/community](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-release/cherry-picks.md))

### 릴리스 독립성 옵션

| 옵션                          | 장점                                        | 단점                                   |
| ----------------------------- | ------------------------------------------- | -------------------------------------- |
| **A. 완전 독립**              | 각 제품이 자유롭게 릴리스                   | 공유 코드 변경 시 호환성 검증 부담     |
| **B. 동기화된 독립 (권장)**   | 공유 코드 변경은 함께, 제품 코드는 독립     | 동기화 시점 조율 필요                  |
| **C. 동시 릴리스**            | 단순, 호환성 보장                           | 한 제품이 다른 제품에 끌려다님         |

---

## 10. 흔한 실수와 Anti-Pattern

| #   | 실수                                    | 왜 문제인가                                                 | 올바른 접근                                         |
| --- | --------------------------------------- | ----------------------------------------------------------- | --------------------------------------------------- |
| 1   | Release branch에서 직접 버그 수정       | trunk에 수정 누락 → 다음 릴리스 regression                  | **항상 trunk first** → cherry-pick                  |
| 2   | Feature branch 1주일 이상 유지          | Merge conflict 누적, 통합 이슈 늦게 발견                    | 작업을 작게 분할, 2-3일 이내 merge                  |
| 3   | Feature flag 삭제 기한 미설정           | flag 누적 → 코드 복잡도 폭발                                | 릴리스 후 flag 제거 일정 문서화                     |
| 4   | 느린 CI에서 Scaled TBD 도입             | Merge 대기열, 생산성 저하                                    | CI 10분 이내 최적화 먼저                            |
| 5   | 보안 패치를 각 branch에서 독립 작업     | 동일 수정의 다중 중복, 불일치 위험                           | Cherry-pick forward 자동화                          |
| 6   | Big Bang 리팩토링                       | 이전 release로의 cherry-pick 불가능                          | Branch by Abstraction (점진적)                      |
| 7   | Release branch를 6개월 이상 유지        | trunk과 divergence → cherry-pick 실패율 급증                 | EOL 정책 정의, 빠른 GA 릴리스                       |

### 🚫 Anti-Patterns

1. **"Scaled TBD라면서 Long-lived feature branch"**: branch 이름만 feature/xxx이지 실제로는 수 주~수 개월 유지. 이는 TBD가 아니라 Git Flow도 아닌 무질서 상태
2. **"Release branch에서 역방향 merge"**: release branch의 수정을 trunk으로 merge back하는 것. trunk에 의도치 않은 release-specific 설정이 유입될 위험

### 🔒 보안/성능 고려사항

- **보안 패치 전파 자동화**: cherry-pick 스크립트 + CI로 모든 활성 release branch에 일관되게 적용. K8s의 `hack/cherry_pick_pull.sh` 참고
- **CI 성능**: trunk에 빈번한 커밋이 들어오므로 빌드 캐싱, 변경 영향 범위 기반 선택적 테스트(affected test selection) 필수
- **Feature flag 보안**: flag 상태가 사용자에게 노출되지 않도록 서버사이드 평가 권장

---

## 11. 장점과 단점

| 구분    | 항목                       | 설명                                                                    |
| ------- | -------------------------- | ----------------------------------------------------------------------- |
| ✅ 장점 | **Merge conflict 최소화**  | 모든 코드가 빈번하게 trunk에 통합되어 divergence 방지                   |
| ✅ 장점 | **항상 배포 가능한 trunk** | CI 게이트를 통해 trunk 안정성 보장, 긴급 배포 가능                      |
| ✅ 장점 | **통합 이슈 조기 발견**    | Feature flag로 미완성 코드도 trunk CI에서 검증                          |
| ✅ 장점 | **브랜치 관리 단순화**     | long-lived branch가 없어 관리 오버헤드 감소                             |
| ✅ 장점 | **유연한 릴리스**          | 제품별 독립 release branch로 필요 시점에 릴리스                         |
| ❌ 단점 | **높은 CI/CD 인프라 요구** | 모든 커밋에 대한 빠른 빌드/테스트 필수. 느린 CI = 병목                  |
| ❌ 단점 | **Feature flag 관리 부담** | flag가 누적되면 코드 복잡도 증가. "#ifdef considered harmful" 위험      |
| ❌ 단점 | **팀 규율 필수**           | 깨진 trunk은 전체 팀에 영향. 높은 테스트 자동화 수준 필요               |
| ❌ 단점 | **Cherry-pick conflict**   | trunk과 release branch의 코드 차이가 클수록 cherry-pick 충돌 가능성     |

### ⚖️ Trade-off 분석

```
빠른 통합/배포 ◄────── Trade-off ──────► CI/CD 인프라 투자
브랜치 단순화  ◄────── Trade-off ──────► Feature flag 관리 부담
Merge 충돌 감소 ◄────── Trade-off ──────► 팀 규율/자동화 요구
릴리스 유연성  ◄────── Trade-off ──────► Cherry-pick 운영 비용
```

---

## 12. 실제 적용 사례

- **Google**: 35,000+ 개발자가 단일 monorepo trunk에서 작업. 자체 VCS(Piper) 개발. Release branch는 trunk 스냅샷 + cherry-pick 방식 ([paulhammant.com](https://paulhammant.com/2014/01/08/googles-vs-facebooks-trunk-based-development/))
- **Meta(Facebook)**: Mercurial 기반 trunk 운영. 모든 diff를 커밋 전 CI 빌드/테스트로 검증하여 trunk 무결성 보장 ([qeunit.com](https://qeunit.com/blog/how-google-does-monorepo/))
- **Microsoft**: Windows 팀이 Git monorepo로 전환. VFS for Git 개발하여 대규모 repo 성능 문제 해결 ([devblogs.microsoft.com](https://devblogs.microsoft.com/ise/working-with-a-monorepo/))

---

## 13. 개발자가 알아둬야 할 것들

### 📚 학습 리소스

| 유형         | 이름                     | 링크/설명                                                                                                                                                                                       |
| ------------ | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 📖 공식 문서 | Trunk Based Development  | [trunkbaseddevelopment.com](https://trunkbaseddevelopment.com/) — Paul Hammant 운영                                                                                                             |
| 📖 공식 문서 | Branch for Release       | [trunkbaseddevelopment.com/branch-for-release](https://trunkbaseddevelopment.com/branch-for-release/)                                                                                           |
| 📖 공식 문서 | Feature Flags            | [trunkbaseddevelopment.com/feature-flags](https://trunkbaseddevelopment.com/feature-flags/)                                                                                                     |
| 📖 참고 사례 | K8s Cherry-pick 프로세스 | [github.com/kubernetes/community](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-release/cherry-picks.md)                                                           |
| 📘 도서      | *Continuous Delivery*    | Jez Humble & David Farley — TBD의 이론적 기반                                                                                                                                                   |
| 📘 도서      | *Accelerate*             | Nicole Forsgren et al. — DORA 메트릭스에서 TBD와 성과 상관관계 입증                                                                                                                             |
| 📘 도서      | *DevOps Handbook*        | Gene Kim et al. — 대규모 조직 TBD 적용 사례                                                                                                                                                     |
| 📖 비교 분석 | TBD vs Git Flow          | [Toptal](https://www.toptal.com/developers/software/trunk-based-development-git-flow), [Atlassian](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development) |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리    | 플랫폼            | 용도                                                   |
| ------------------ | ----------------- | ------------------------------------------------------ |
| **LaunchDarkly**   | SaaS              | Feature flag 관리 플랫폼                               |
| **Unleash**        | Self-hosted/Cloud | 오픈소스 Feature flag 서버                             |
| **Harness FF**     | SaaS              | Feature flag + CI/CD 통합                              |
| **DevCycle**       | SaaS              | Feature flag + TBD 가이드 제공                         |
| **Graphite**       | CLI/SaaS          | Stacked PR 관리로 short-lived branch 워크플로우 최적화 |
| **Renovate**       | GitHub/GitLab     | 다중 base branch 대상 의존성 자동 업데이트             |
| **Nx / Turborepo** | Node.js           | Monorepo 빌드 최적화 (affected 기반 선택적 빌드)       |

### 🔮 트렌드 & 전망

- **DORA 메트릭스와의 상관관계**: Accelerate 연구에서 TBD 실천 팀이 배포 빈도, 변경 리드타임에서 월등히 높은 성과를 보임
- **Monorepo + Scaled TBD 확산**: Google/Meta/Microsoft의 사례가 업계 표준으로 자리잡는 추세
- **AI 코드 리뷰 통합**: short-lived PR에 AI 리뷰 자동화를 결합하여 리뷰 병목 해소

### 💬 커뮤니티 인사이트

- **"Feature flag 없는 Scaled TBD는 없다"**: 실무에서 feature flag 없이 TBD를 시도하면 미완성 기능이 사용자에게 노출되는 사고가 반복됨
- **"CI가 10분 넘으면 TBD는 고통"**: trunk에 빈번한 merge가 들어오는데 CI가 느리면 merge queue가 쌓여 오히려 생산성 저하
- **"Cherry-pick은 자동화하지 않으면 잊는다"**: K8s처럼 봇/스크립트로 cherry-pick PR을 자동 생성하는 프로세스가 필수

---

## 📎 Sources

1. [Trunk Based Development](https://trunkbaseddevelopment.com/) — 공식 레퍼런스 사이트 (Paul Hammant)
2. [Branch for Release](https://trunkbaseddevelopment.com/branch-for-release/) — Release branch 원칙
3. [Feature Flags](https://trunkbaseddevelopment.com/feature-flags/) — Feature flag 가이드
4. [Monorepos](https://trunkbaseddevelopment.com/monorepos/) — Monorepo에서의 TBD
5. [Trunk-based Development \| Atlassian](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development) — 개요 및 비교
6. [TBD vs Git Flow \| Toptal](https://www.toptal.com/developers/software/trunk-based-development-git-flow) — 비교 분석
7. [Google's vs Facebook's TBD](https://paulhammant.com/2014/01/08/googles-vs-facebooks-trunk-based-development/) — 대규모 적용 사례
8. [How Google Does Monorepo](https://qeunit.com/blog/how-google-does-monorepo/) — Google 사례 상세
9. [K8s Cherry-pick Process](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-release/cherry-picks.md) — 업계 표준 cherry-pick 프로세스
10. [A Successful Git Branching Model](https://nvie.com/posts/a-successful-git-branching-model/) — Git Flow 원문 + 2020 reflection
11. [TBD vs GitFlow \| Splunk](https://www.splunk.com/en_us/blog/learn/trunk-based-development-vs-gitflow.html) — 비교 분석
12. [Branching Strategies for Monorepo \| Graphite](https://graphite.com/guides/branching-strategies-monorepo) — Monorepo 전략
13. [Linux Kernel Backporting](https://docs.kernel.org/process/backporting.html) — Manual backport 방법론
