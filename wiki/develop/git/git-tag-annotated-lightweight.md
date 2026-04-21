---
tags: [git, tag, gpg, release-management]
created: 2026-04-21
---

# 🏷️ Git Tag 완전 가이드 — Annotated vs Lightweight

## Tag의 두 가지 종류

Git 태그는 **두 종류**가 있고, 종류에 따라 저장되는 정보가 달라요.

| 종류              | 생성 명령      | 메타데이터         | 작성자 정보 |
| ----------------- | -------------- | ------------------ | ----------- |
| **Annotated Tag** | `git tag -a`   | Tagger, 날짜, 메시지 포함 | ✅ 저장됨    |
| **Lightweight Tag** | `git tag`    | 단순 커밋 포인터         | ❌ 없음      |

> 🎒 비유: Annotated Tag는 **"누가 붙였는지" 적힌 이름표 스티커**, Lightweight Tag는 **그냥 빈 스티커**

### 태그 종류 확인하는 법

```bash
git cat-file -t v1.0.0
```

| 출력     | 의미                              |
| -------- | --------------------------------- |
| `tag`    | Annotated Tag → Tagger 정보 있음 ✅ |
| `commit` | Lightweight Tag → Tagger 정보 없음 ❌ |

> 📌 `git cat-file`에 대한 자세한 설명은 [[git-cat-file-for-each-ref]] 참조

---

## 누가 태그를 붙였는지 확인하는 방법

### Annotated Tag인 경우

```bash
# 가장 간단한 방법
git show v1.0.0
```

출력 예시:

```
tag v1.0.0
Tagger: 홍길동 <hong@example.com>    ← 🎯 태그를 붙인 사람!
Date:   Mon Apr 21 10:00:00 2026 +0900

Release v1.0.0
```

```bash
# tagger 정보만 추출 (스크립트/자동화에 유용)
git for-each-ref --format='%(taggername) %(taggeremail) %(taggerdate)' refs/tags/v1.0.0

# 모든 태그와 작성자를 한눈에 보기
git for-each-ref --format='%(refname:short) | %(taggername) | %(taggerdate:short)' refs/tags/
```

> 📌 `git for-each-ref`에 대한 자세한 설명은 [[git-cat-file-for-each-ref]] 참조

### Lightweight Tag인 경우 (우회 방법)

Lightweight Tag는 Git 자체에 tagger 정보가 저장되지 않지만, 우회적으로 추적할 수 있어요.

| 방법                                                   | 설명                      | 한계                             |
| ------------------------------------------------------ | ------------------------- | -------------------------------- |
| `git reflog refs/tags/v1.0.0`                          | 로컬 머신의 생성 기록 확인 | 로컬 전용, 시간 지나면 정리됨     |
| `gh api repos/{owner}/{repo}/git/refs/tags/v1.0.0`     | GitHub API로 push한 사람 확인 | GitHub 사용 시만 가능         |
| 서버 reflog                                             | bare repo의 reflog 확인    | 서버 접근 권한 필요              |
| `git log -1 --format='%an <%ae>' v1.0.0`               | 커밋 author 확인           | ⚠️ 태그를 붙인 사람과 다를 수 있음 |

> 📌 reflog에 대한 자세한 설명은 [[git-reflog-recovery-guide]] 참조

### 전체 판단 흐름

```
태그 확인하고 싶다!
       │
       ▼
  git cat-file -t <tag>
       │
  ┌────┴────┐
  │         │
 tag      commit
  │         │
  ▼         ▼
Annotated  Lightweight
  │         │
  ▼         ▼
git show   git log -1
 <tag>      <tag>
  │         │
  ▼         ▼
Tagger 😊  Commit Author 🤷
(정확)      (태그 붙인 사람과 다를 수 있음)
```

---

## Annotated Tag 사용법

### 생성하기

```bash
# 기본 생성 (메시지 포함)
git tag -a v1.0.0 -m "첫 번째 정식 릴리즈"

# 에디터로 긴 메시지 작성 (-m 생략하면 에디터 열림)
git tag -a v1.0.0

# 과거 커밋에 태그 붙이기
git tag -a v0.9.0 -m "베타 릴리즈" abc1234

# GPG 서명된 태그 (보안이 중요한 릴리즈)
git tag -s v1.0.0 -m "서명된 릴리즈"
```

### 확인하기

```bash
git tag                    # 태그 목록
git tag -l "v1.*"          # 패턴 필터링
git show v1.0.0            # 상세 정보 (tagger, 날짜, 메시지)
git cat-file -t v1.0.0     # 태그 종류 확인
```

### 원격 저장소에 Push하기

> ⚠️ **중요**: 태그는 `git push`로 자동 전송되지 않아요!

```bash
git push origin v1.0.0         # 특정 태그만 push
git push origin --tags          # 모든 태그 push
git push origin --follow-tags   # annotated 태그만 push (lightweight 제외)
```

### 태그 기반 체크아웃

```bash
# 태그 시점의 코드 확인 (detached HEAD 상태)
git checkout v1.0.0

# 태그 기반으로 새 브랜치 생성 (작업할 때)
git checkout -b hotfix/v1.0.1 v1.0.0
```

---

## GPG 서명과 태그 보안

### GPG 서명이란?

**GPG** (GNU Privacy Guard) = 데이터의 **진위를 증명**하는 암호화 도구

> 🎒 비유: 옛날 왕이 편지를 보낼 때 **왕실 인장(도장)**을 찍었잖아요. GPG 서명은 **디지털 세계의 인장**이에요.

### 작동 원리

```
[개인키 (Private Key)]          [공개키 (Public Key)]
   나만 가지고 있음                 모두에게 공개됨
        │                              │
        ▼                              ▼
  "서명 생성"에 사용              "서명 검증"에 사용
        │                              │
        ▼                              ▼
  git tag -s v1.0.0            git tag -v v1.0.0
  (서명 생성)                    (서명 검증)
```

### 왜 태그에 서명이 필요해?

**위협 시나리오:**

```
😈 공격자가 할 수 있는 것:

1. Git 서버 해킹 → 태그를 다른 커밋으로 이동시킴
   v1.0.0 → 원래 안전한 코드 ✅
   v1.0.0 → 악성 코드가 포함된 커밋으로 변경 ❌💀

2. 가짜 태그를 만들어서 릴리즈인 척 위장
```

**GPG 서명이 있으면:**

```
😈 공격자가 태그를 조작하더라도
       │
       ▼
  git tag -v v1.0.0 로 검증
       │
       ▼
  "서명이 유효하지 않습니다!" ← 🚨 위조 감지!
```

### 실제 사용 사례

| 프로젝트         | 왜 쓰나?                                         |
| ---------------- | ------------------------------------------------ |
| **Linux Kernel** | Linus Torvalds가 직접 서명 → 릴리즈 진위 보증     |
| **Bitcoin Core** | 금융 소프트웨어 → 악성 코드 주입 방지 필수         |
| **Python (CPython)** | 공급망 공격(Supply Chain Attack) 방지          |

### 일반 프로젝트에서는?

- **소규모 팀/사내 프로젝트**: GPG 서명 없어도 대부분 괜찮아요
- **오픈소스/공개 릴리즈**: 강력히 권장
- **보안이 중요한 소프트웨어**: 필수

---

## `--follow-tags` 옵션

### 오해 정리 ❌

`--follow-tags`는 태그를 **자동 생성**해주는 게 아니라, 이미 만든 annotated 태그를 **자동으로 push**해주는 옵션이에요.

> 🎒 비유:
> - `git tag -a` = **택배 상자를 포장하는 것** 📦
> - `git push` = **택배를 부치는 것** 🚚
> - `--follow-tags` = **"포장된 상자가 있으면 같이 부쳐줘"** 라는 설정

### 예시로 비교

**`--follow-tags` 없이:**

```bash
git commit -m "Release v1.0.0"
git tag -a v1.0.0 -m "Release v1.0.0"   # ← 여전히 필요!
git push origin main                      # ⚠️ 태그는 push 안 됨
git push origin v1.0.0                    # ← 태그를 별도로 push 해야 함
```

**`--follow-tags` 있으면:**

```bash
git commit -m "Release v1.0.0"
git tag -a v1.0.0 -m "Release v1.0.0"   # ← 여전히 필요!
git push origin main                      # ✅ 태그도 자동으로 같이 push!
```

### 조건 (공식 help 원문 기반)

| 조건                                                   | 포함 여부 |
| ------------------------------------------------------ | --------- |
| Annotated Tag + push할 커밋에서 도달 가능(reachable)한 태그 | ✅ 자동 push |
| Lightweight Tag                                         | ❌ 무시     |
| push할 커밋에서 도달 불가능한 태그                        | ❌ 무시     |

### 기본값으로 설정하기

```bash
git config --global push.followTags true
```

---

## 태그 삭제: `--delete` vs `:ref` refspec

### 두 가지 삭제 방법

```bash
# 로컬 태그 삭제
git tag -d v1.0.0

# 원격 태그 삭제 (방법 1 - 권장)
git push origin --delete v1.0.0

# 원격 태그 삭제 (방법 2 - refspec 문법)
git push origin :v1.0.0
```

### `:`은 `--delete`의 약자가 아니다

`git push`는 내부적으로 **refspec** 문법을 사용해요:

```
git push <remote> <src>:<dst>
                   ───   ───
                   로컬   원격
```

> 🎒 비유: `<src>`는 **보낼 물건**, `<dst>`는 **받을 주소**. src를 비워두면 "아무것도 안 보냄" = 삭제!

Git 공식 help 원문: *"--delete: All listed refs are deleted from the remote repository. **This is the same as prefixing all refs with a colon.**"*

| 명령                              | 원리                               | 관계                    |
| --------------------------------- | ---------------------------------- | ----------------------- |
| `git push origin :v1.0.0`        | refspec에서 src를 비움 = 삭제       | 원조 문법               |
| `git push origin --delete v1.0.0` | 명시적 삭제 플래그 (`-d`로도 가능)  | 콜론 문법의 읽기 쉬운 별칭 |

---

## 실무 팁

### 태그 네이밍 컨벤션

```
v1.0.0        ← SemVer (Semantic Versioning) 가장 보편적
v1.0.0-rc.1   ← Release Candidate
v1.0.0-beta   ← 베타 버전
```

### 태그 메시지에 담으면 좋은 내용

```bash
git tag -a v1.2.0 -m "$(cat <<'EOF'
Release v1.2.0

주요 변경사항:
- 사용자 인증 기능 추가
- 성능 개선 (API 응답속도 30% 향상)
- VITALCARES-1234 버그 수정

Breaking Changes:
- /api/v1/users 엔드포인트 응답 형식 변경
EOF
)"
```

> 📌 `"$(cat <<'EOF' ... EOF)"` 패턴에 대한 상세 설명은 [[shell-command-substitution-heredoc]] 참조

### 전체 릴리즈 워크플로우

```
개발 완료
   │
   ▼
git tag -a v1.0.0 -m "Release v1.0.0"   ← 태그 생성
   │
   ▼
git show v1.0.0                          ← 확인
   │
   ▼
git push origin v1.0.0                   ← 원격에 push
   │
   ▼
GitHub Releases에서 확인 🎉
```

---

## 핵심 정리

1. **Annotated Tag**는 tagger 정보를 저장하고, **Lightweight Tag**는 저장하지 않는다
2. `git cat-file -t <tag>`로 태그 종류를 먼저 확인한다
3. Annotated Tag 작성자는 `git show <tag>`로 바로 확인 가능
4. Lightweight Tag 작성자는 Git 자체로 확인 불가 → GitHub API 또는 reflog로 우회
5. GPG 서명으로 태그의 진위와 무결성을 암호학적으로 증명할 수 있다
6. `--follow-tags`는 태그 push 자동화이지, 태그 생성 자동화가 아니다
7. `--delete`와 `:ref`는 같은 동작이지만 `--delete`가 더 읽기 쉽다
8. **실무에서는 항상 `git tag -a`를 사용**하여 추적성을 확보한다
