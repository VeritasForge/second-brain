---
created: 2026-03-23
source: claude-code
tags: [python, uv, lock-file, dependency-management, git-merge, best-practice]
---

# uv.lock 충돌 해결 Best Practice

## 배경: uv.lock 파일이란?

uv는 Python 패키지 매니저이며, `uv.lock`은 프로젝트의 모든 의존성 버전을 정확히 기록한 잠금(lock) 파일입니다. git merge 시 양쪽 브랜치에서 이 파일이 다르게 변경되면 충돌이 발생합니다.

---

## 핵심 개념

### 핀(pin) — 버전 고정

게시판에 사진을 압정(pin)으로 꽂으면 움직이지 않듯, **버전 핀**은 "정확히 이 버전만 써!"라고 못 박는 것입니다.

```python
# ✅ 핀된 것 (==) — "정확히 이 버전만 써!"
"cryptography==46.0.5"    # 46.0.5만 사용
"requests==2.32.5"        # 2.32.5만 사용

# ❌ 핀되지 않은 것
"some-lib>=0.2.2"         # 0.2.2 이상이면 아무거나
"my-interface"            # 버전 지정 없음 (git rev로 관리)
"my-local-module"         # 로컬 path 소스 (버전 없음)
```

핵심 정리: 핀(pin) = 버전을 정확히 고정. `==`이 압정, `>=`는 "최소한 이것 이상".

### 전이 의존성 — 친구의 친구

내가 직접 설치한 라이브러리 = **직접 의존성**, 그 라이브러리가 필요로 하는 라이브러리 = **전이 의존성**

```
my-project
  ├── requests==2.32.5        ← 직접 의존성 (내가 직접 설치)
  │     ├── urllib3            ← 전이 의존성 (requests가 필요해서 딸려옴)
  │     ├── certifi            ← 전이 의존성
  │     └── charset-normalizer ← 전이 의존성
  │
  ├── ddtrace==4.6.1           ← 직접 의존성
  │     ├── bytecode           ← 전이 의존성
  │     └── ... (수십 개!)     ← 전이 의존성
```

일반적으로 직접 의존성이 수십 개인 프로젝트라도, uv.lock에는 전이 의존성까지 포함되어 훨씬 많은 패키지가 기록됩니다.

핵심 정리: 전이 의존성 = 딸려오는 라이브러리. `rm`하면 이것들이 전부 새로 계산되어 불필요한 변경이 diff에 잡힘.

### blast radius — 폭발 반경

폭탄이 터지면 얼마나 넓은 범위에 피해가 가는지를 "blast radius"라고 합니다. 소프트웨어에서는 **"어떤 작업이 영향을 미치는 범위"**를 뜻합니다.

```
rm uv.lock && uv lock 의 blast radius:
┌─────────────────────────────────────────┐
│  직접 의존성: ==핀 → 버전 안 바뀜       │  ← 영향 없음 ✅
│  전이 의존성: 핀 없음 → 바뀜!           │  ← 💥 여기가 blast radius
└─────────────────────────────────────────┘

git checkout <base-branch> -- uv.lock && uv lock 의 blast radius:
┌─────────────────────────────────────────┐
│  base branch의 검증된 버전 유지         │  ← 영향 최소 ✅
│  내 변경분만 추가 반영                  │  ← 필요한 것만
└─────────────────────────────────────────┘
```

비유: 기존 집에서 방 하나만 리모델링(checkout) vs 집을 부수고 새로 짓기(rm). `rm`하면 전이 의존성이 전부 fresh resolve되어 수십 개가 바뀔 수 있고, 코드 리뷰어가 "이 변경이 의도한 건가?" 일일이 확인해야 합니다.

직접 의존성은 `==` 핀 덕분에 **버전은 안전**하지만, lock 파일의 내용(해시, URL, 전이 의존성 버전)은 달라져서 diff가 넓어지는 것입니다.

---

## uv lock 명령의 동작 원리

uv의 공식 문서([Resolution](https://docs.astral.sh/uv/concepts/resolution/))에 따르면:

> "locked or installed versions will not change unless an incompatible version is requested or an upgrade is explicitly requested with `--upgrade`"

### 3가지 명령의 정확한 차이

| 명령                     | 기존 lock 참조                                       | 직접 의존성 (`==`) | 전이 의존성 (`>=` 또는 없음)        |
| ------------------------ | ---------------------------------------------------- | ------------------ | ----------------------------------- |
| `uv lock`                | ✅ 기존 lock의 모든 버전을 **선호(prefer)**           | 그대로             | **그대로** (새 버전 나와도 안 올림) |
| `uv lock --upgrade`      | ⚠️ 기존 lock을 읽되 **최신 호환 버전으로 업그레이드** | 그대로 (`==` 제약) | **최신으로 업데이트**               |
| `rm uv.lock && uv lock`  | ❌ lock 없이 **처음부터 fresh resolve**               | 그대로 (`==` 제약) | **최신으로 resolve**                |

### `rm + lock`과 `--upgrade`는 동일한가?

**거의 동일하지만 보장되지 않습니다.** 두 방식 모두 전이 의존성을 최신 호환 버전으로 해결하지만:

- `--upgrade`는 기존 lock의 메타데이터(source URL 등)를 참조할 수 있음
- `rm`은 완전히 백지에서 시작하므로 resolver의 내부 heuristic에 따라 미세한 차이 가능

### 핵심: `uv lock`만으로는 전이 의존성이 업데이트 되지 않는다

```
비유: 냉장고(uv.lock)에 우유가 있으면,
유통기한이 지나도 uv는 "이미 있으니까 새로 안 사도 돼"라고 합니다.
--upgrade를 해야 "유통기한 확인하고 새 우유로 교체해"가 됩니다.
```

---

## 의사결정 플로우차트

```
uv.lock 충돌 발생!
    │
    ├─ 충돌만 해결하고 싶다 (최소 변경)
    │   └─→ git checkout <base-branch> -- uv.lock && uv lock
    │        (메인테이너 권장. 변경 범위 최소화)
    │
    ├─ 충돌 해결 + 전이 의존성도 업데이트하고 싶다
    │   └─→ 커밋 분리 전략:
    │        커밋 1: git checkout <base-branch> -- uv.lock && uv lock  (충돌 해결)
    │        커밋 2: uv lock --upgrade                                  (의도적 업데이트)
    │
    ├─ 간단하게 한번에 해결하고 싶다 (== 핀이 대부분인 프로젝트)
    │   └─→ rm uv.lock && uv lock
    │        (의도적 선택이면 유효. diff가 넓어지는 것을 감수)
    │
    └─ 자동화하고 싶다
        └─→ .gitattributes merge=ours
             ⚠️ 보안이 중요한 프로젝트에서는 금지 (CVE 패치 누락 위험)
             ✅ 보안 규제가 낮은 프로젝트에서는 가능
```

---

## 충돌 해결: 3가지 방법 비교

### 방법 1: checkout + uv lock (메인테이너 권장) ✅

uv 메인테이너 **zanieb**가 [Issue #5633](https://github.com/astral-sh/uv/issues/5633)에서 직접 제시한 워크플로우:

```bash
git checkout origin/<base-branch> -- uv.lock   # base branch의 깨끗한 lock을 가져옴
uv lock                                         # 내 pyproject.toml 변경분만 반영
git add uv.lock                                 # 해결 완료
```

또 다른 메인테이너 **konstin**도 [Issue #11185](https://github.com/astral-sh/uv/issues/11185)에서:

> "my usual strategy for feature branches is to accept the changes from the base branch, then run `uv lock` to update the lockfile"

### 방법 2: rm + uv lock (단순하지만 주의 필요) ⚠️

```bash
rm uv.lock
uv lock
git add uv.lock
```

[Issue #16348](https://github.com/astral-sh/uv/issues/16348)의 메인테이너 발언:

> "will unpin any versions, and should generally not be used unless there's no recourse"

단, `==` 핀이 대부분인 프로젝트에서는 **전이 의존성만 변경**되므로 "위험"이 아니라 "불필요하게 넓은 diff를 생성하여 추적 부담 증가" 수준입니다.

**다른 관점**: 핀 되지 않은 전이 의존성은 "업데이트가 되라고 열어둔 것"이므로, 충돌 해결을 **의도적인 전이 의존성 최신화 기회**로 삼는 것도 유효한 전략입니다. 다만 이 경우 **충돌 해결과 의존성 업데이트를 별도 커밋으로 분리**하면 리뷰가 깔끔합니다:

```bash
# 커밋 1: 충돌 해결 (최소 변경)
git checkout <base-branch> -- uv.lock && uv lock && git add uv.lock
git commit -m "fix: uv.lock 충돌 해결"

# 커밋 2: 의존성 최신화 (의도적 업데이트)
uv lock --upgrade && git add uv.lock
git commit -m "chore: 전이 의존성 최신화"
```

### 방법 3: .gitattributes merge driver ⚠️

```gitattributes
uv.lock merge=ours
```

비유: 우체국 자동 분류기 — 편지(파일)가 충돌하면, 사람 대신 기계가 "이쪽 편지를 우선!"이라고 자동 결정.

기술적으로 가능하지만, `merge=ours`는 상대방 브랜치의 변경을 **완전히 무시**합니다.

| 프로젝트 유형                | 권장 여부  | 이유                                       |
| ---------------------------- | ---------- | ------------------------------------------ |
| 보안 규제가 낮은 웹 프로젝트 | ✅ 괜찮음  | CI에서 재생성 가능. 보안 규제 낮음         |
| 일반 백엔드                  | ⚠️ 조건부 | 빈번한 충돌 + 강한 CI가 있으면 가능        |
| 보안이 중요한 프로젝트       | ❌ 금지    | CVE 패치 누락 위험                         |

### 방법별 비교

| 방법                                          | 안전성    | 간편함    | 보안 중요 프로젝트 적합 |
| --------------------------------------------- | --------- | --------- | ----------------------- |
| `git checkout <base> -- uv.lock && uv lock`   | ✅ 최고   | ✅ 높음   | ✅ 적합                 |
| `rm uv.lock && uv lock`                       | ⚠️ 중간  | ✅ 최고   | ⚠️ diff 확대           |
| `.gitattributes merge=ours`                   | ❌ 위험   | ✅ 자동   | ❌ 금지                 |

---

## 명령어 단계별 해설

### 현재 상태 (명령 실행 전)

```
uv.lock 파일 안:
<<<<<<< HEAD (내 브랜치)
revision = 1
=======
revision = 2
>>>>>>> <base-branch>

→ git은 "양쪽이 다른데 어쩌라고?" 상태 (UU = Unmerged)
→ uv lock 실행하면 에러남 (유효한 TOML 파일이 아니니까)
```

### Step 1: `git checkout origin/<base-branch> -- uv.lock`

```
git checkout             → "다른 곳에서 파일을 가져와"
origin/<base-branch>     → "원격 저장소의 base 브랜치에서"
--                       → "브랜치 이름이 아니라 파일 경로가 온다는 구분자"
uv.lock                  → "이 파일을"
```

충돌 마커가 가득한 uv.lock을 **base branch의 깨끗한 uv.lock으로 덮어씀**.

```
실행 전:                          실행 후:
┌──────────────────────┐         ┌──────────────────────┐
│ <<<<<<< HEAD         │         │ revision = 2         │
│ revision = 1         │   →     │ [[package]]          │
│ =======              │         │ name = "alembic"     │
│ revision = 2         │         │ version = "1.16.5"   │
│ >>>>>>> base-branch  │         │ ...                  │
│ (충돌 마커 잔뜩)      │         │ (base의 깨끗한 파일)  │
└──────────────────────┘         └──────────────────────┘
```

비유: 두 사람이 동시에 쇼핑 목록을 수정해서 찢어졌을 때, 일단 **원본 목록을 기준**으로 깔끔하게 가져오는 것. base branch는 이미 CI/테스트를 통과한 검증된 상태이니까.

### Step 2: `uv lock`

내 브랜치의 `pyproject.toml` 변경사항을 lock에 반영.

```
입력 2개:
┌─────────────────────────┐     ┌─────────────────────────┐
│ pyproject.toml          │     │ uv.lock (Step 1에서     │
│ (내 브랜치 버전)         │     │  가져온 base 버전)       │
│                         │     │                         │
│ + new-lib>=0.2.2 (신규!)│  +  │ certifi==2026.2.25     │
│                         │     │ (base의 보안 패치)      │
└─────────────────────────┘     └─────────────────────────┘
              │                            │
              └──────────┬─────────────────┘
                         ▼
              ┌─────────────────────────┐
              │ 새 uv.lock              │
              │                         │
              │ ✅ base의 핀 유지        │
              │ ✅ 보안 패치 유지        │
              │ ✅ 내 변경 추가          │
              └─────────────────────────┘
```

비유: 원본 쇼핑 목록(base)을 기준으로, **내가 추가한 항목만 펜으로 적어넣는 것**. 원본에 이미 적혀 있는 항목은 건드리지 않음.

핵심 원리: uv는 기존 lock 파일이 있으면 그 버전을 **우선 유지**(prefer previously locked versions). base branch의 전이 의존성 버전이 그대로 보존되고, 내 pyproject.toml에서 바뀐 부분만 재계산됨.

### Step 3: `git add uv.lock`

git의 "충돌 미해결(UU)" 상태를 "해결 완료(M)"로 전환. 이후 `git merge --continue` 또는 `git commit`으로 merge를 완료할 수 있습니다.

### 전체 흐름 요약

```
[충돌 상태] ──Step 1──→ [base 기준 깨끗한 lock] ──Step 2──→ [내 변경 반영] ──Step 3──→ [해결 완료]
  (UU)      checkout      (base 핀 보존)          uv lock     (양쪽 통합)     git add     (커밋 가능)
```

---

## 상황별 적합한 도구

비유: 교통사고가 나서 차를 수리해야 하는데(충돌 해결), `--upgrade-package`는 타이어 하나만 교체하는 도구입니다. 사고 수리는 정비소(checkout + uv lock)에서 해야죠.

| 상황                          | 적합한 도구                                            |
| ----------------------------- | ------------------------------------------------------ |
| 충돌 해결 (대량 변경)         | `git checkout <base-branch> -- uv.lock && uv lock`     |
| 특정 패키지 1~2개만 업데이트  | `uv lock --upgrade-package certifi`                    |
| 전체 의존성 최신화            | `uv lock --upgrade`                                    |

### `uv lock --upgrade-package` — 정밀 업데이트

전체 lock을 건드리지 않고 **특정 패키지만 업데이트**하는 정밀 도구. 비유: 앱스토어에서 "전체 업데이트" 대신 "이 앱만 업데이트".

```bash
uv lock --upgrade-package certifi            # certifi만 최신으로
# 결과: certifi 2026.1.4 → 2026.2.25 (바뀜!)
#        나머지: 그대로 ✅

uv lock --upgrade-package certifi==2026.2.25  # 특정 버전으로 고정
```

| 명령                                         | 직접 의존성 (`==`) | 전이 의존성    | 용도                              |
| -------------------------------------------- | ------------------ | -------------- | --------------------------------- |
| `uv lock`                                    | 그대로             | **그대로**     | pyproject.toml 변경분만 반영      |
| `uv lock --upgrade`                          | 그대로 (`==` 제약) | **최신으로**   | 전체 의존성 최신화                |
| `uv lock --upgrade-package certifi`          | 그대로             | certifi만 최신 | 특정 패키지 정밀 업데이트         |
| `rm uv.lock && uv lock`                      | 그대로 (`==` 제약) | **최신으로**   | 충돌 해결 + 전체 최신화 (한번에)  |

---

## 보안이 중요한 프로젝트에서 merge=ours가 위험한 이유

### CVE 패치 누락 시나리오

```
[1주차] 내가 feature 브랜치를 만듦
         └── uv.lock: certifi==2026.1.4

[2주차] base branch에서 보안 패치 적용
         └── uv.lock: certifi==2026.2.25 (보안 업데이트!)
         💡 certifi는 전이 의존성이라 pyproject.toml에 안 적혀있음
            오직 uv.lock에만 버전이 기록됨!

[3주차] 내가 base branch를 merge → uv.lock 충돌!
```

**merge=ours가 있으면**: 충돌 → 자동으로 "내 것(ours)" 선택 → `certifi==2026.1.4` (구버전) 남음 → `certifi==2026.2.25` (보안 패치) 조용히 버려짐!

**수동 해결하면**: 충돌 → 개발자가 봄 → checkout base → uv lock → `certifi==2026.2.25` ✅ 보안 패치 반영

### 추적 가능성 관점

비유: 비행기 부품 교체는 **누가, 언제, 왜** 기록해야 합니다. "자동으로 교체됐는데 기록 없어요"라면 큰일이죠. 보안이 중요한 소프트웨어도 마찬가지:

| 요구사항           | 의미                                       | merge=ours 문제                                                |
| ------------------ | ------------------------------------------ | -------------------------------------------------------------- |
| **추적 가능성**    | 모든 의존성 변경 이유를 설명 가능해야 함   | ❌ "자동으로 무시됐음"은 이유가 안 됨                          |
| **변경 통제**      | 변경은 의도적이고 검토된 것이어야 함       | ❌ 보안 패치가 "자동 누락"은 의도적 변경이 아님                |
| **SBOM**           | 어떤 버전이 왜 포함되었는지 증명           | ❌ "왜 구버전?" → "merge driver가 알아서..." 는 감사에서 통과 불가 |

---

## uv.lock의 revision 필드

`revision`은 pyproject.toml 변경과 **무관**하며, **uv.lock 파일 포맷의 하위 버전**입니다.

```
version = 1     ← lock 파일 포맷의 메이저 버전
revision = 2    ← lock 파일 포맷의 마이너 버전 (하위 호환)
```

| revision | 추가된 것                             |
| -------- | ------------------------------------- |
| 1        | 기본 포맷                             |
| 2        | (중간 개선)                           |
| 3        | `upload-time` 메타데이터 추가 (최신)  |

로컬 uv 버전이 base branch에서 lock을 생성한 uv보다 구버전이면 revision이 낮아지고 `upload-time` 필드가 대량 삭제되는 diff가 발생합니다. `uv self update`로 해결 가능.

---

## 근본 원인: 장수명 브랜치

uv.lock 충돌의 빈도는 **브랜치 수명에 비례**합니다. Trunk-Based Development(TBD) 전략을 준수하여 브랜치 수명을 줄이면 충돌 자체가 드물어집니다.

---

## 핵심 정리

1. **충돌 해결**: `git checkout origin/<base-branch> -- uv.lock && uv lock && git add uv.lock` (메인테이너 권장)
2. **rm도 유효**: `==` 핀이 대부분인 프로젝트에서는 전이 의존성만 변경됨. 의도적 선택이면 OK
3. **커밋 분리 권장**: 충돌 해결(checkout+lock)과 의존성 업데이트(--upgrade)를 별도 커밋으로
4. **.gitattributes merge=ours 주의**: 보안이 중요한 프로젝트에서 CVE 패치 암묵적 누락 위험
5. **`uv lock`만으로는 전이 의존성 안 올라감**: `--upgrade` 또는 `rm`이 필요
6. **정밀 업데이트**: `uv lock --upgrade-package <pkg>`로 특정 패키지만 외과적 업데이트
7. **revision은 포맷 버전**: pyproject.toml 변경과 무관. uv 버전 차이로 발생
8. **근본 해결**: 장수명 브랜치를 피하는 것이 충돌 빈도 자체를 줄이는 구조적 해법

---

## Sources

1. [Document how to resolve uv.lock merge conflicts - Issue #5633](https://github.com/astral-sh/uv/issues/5633)
2. [Automatic resolution of merge conflicts - Issue #11185](https://github.com/astral-sh/uv/issues/11185)
3. [Provide a way for uv lock to ignore broken files - Issue #16348](https://github.com/astral-sh/uv/issues/16348)
4. [Force newest lock file format - Issue #15220](https://github.com/astral-sh/uv/issues/15220)
5. [Resolution - uv 공식 문서](https://docs.astral.sh/uv/concepts/resolution/)
6. [Locking and syncing - uv 공식 문서](https://docs.astral.sh/uv/concepts/projects/sync/)
7. [Lockfile merge conflicts - DEV Community](https://dev.to/francecil/lockfile-merge-conflicts-how-to-handle-it-correctly-588b)
