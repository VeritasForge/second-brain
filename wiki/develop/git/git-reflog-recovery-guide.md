---
tags: [git, reflog, recovery, debugging]
created: 2026-04-21
---

# 🛟 Git Reflog 개념과 실수 복구 활용법

---

## reflog란?

**reflog** = **ref**erence + **log** = **참조의 변경 이력**

> 🎒 비유: 도서관에서 책을 빌릴 때 **대출 기록부**가 있잖아요. reflog는 Git에서 **"HEAD나 브랜치가 어디를 가리켰는지"의 이동 기록부**예요.

---

## `git log` vs `reflog`

이 둘은 완전히 다른 것을 기록해요:

| 비교          | `git log`                    | `reflog`                          |
| ------------- | ---------------------------- | --------------------------------- |
| 기록 대상     | **커밋의 역사** (부모-자식 관계) | **HEAD/브랜치의 이동 기록**         |
| 범위          | 모든 사람이 공유               | ⚠️ **내 로컬 머신에서만**           |
| 비유          | 📖 "이 책의 목차"              | 📋 "내가 몇 페이지를 펼쳤는지 기록" |
| push 가능?    | ✅ (커밋은 push됨)             | ❌ (절대 push 안 됨)               |
| 수명          | 영구                          | ⚠️ 만료 기간 있음 (아래 참조)       |

### 시각화

```
                    git log (커밋 히스토리)
                    ========================
                    A ← B ← C ← D (main)
                    
                    reflog (HEAD 이동 기록)
                    ========================
HEAD@{0}: checkout: moving from feature to main     → D  (reachable, 90일)
HEAD@{1}: commit: 새 기능 추가                        → E  (unreachable, 30일!)
HEAD@{2}: checkout: moving from main to feature      → C  (reachable, 90일)
HEAD@{3}: reset: moving to HEAD~1                    → C  (reachable, 90일)
HEAD@{4}: commit: 실수한 커밋                          → D  (reachable, 90일)
```

---

## `git reflog` 명령 사용법

### 기본 조회

```bash
# HEAD의 이동 기록 보기 (기본)
git reflog

# 특정 브랜치의 기록 보기
git reflog show develop

# 특정 태그의 생성/변경 기록 보기
git reflog refs/tags/v1.0.0
```

출력 예시:

```
33f857b HEAD@{0}: commit: [VITALCARES-4750] MEMORY.md 활용 가이드 문서 추가
cc785ce HEAD@{1}: commit: [VITALCARES-4686] 제품 사용목적 설정을 위한 DB 모델 필드 추가
86f2c5d HEAD@{2}: merge: Merge remote-tracking branch 'origin/VITALCARES-4769'
```

### 주요 서브커맨드

| 서브커맨드            | 설명                       |
| -------------------- | -------------------------- |
| `git reflog show`    | reflog 조회 (기본값)        |
| `git reflog expire`  | 오래된 reflog 항목 삭제     |
| `git reflog delete`  | 특정 항목 삭제              |
| `git reflog exists`  | ref에 reflog가 있는지 확인  |

---

## 실수 복구 시나리오

### 시나리오 1: `git reset --hard` 후 복구

```bash
# 실수로 커밋을 날렸을 때!
git reflog                    # 이전 HEAD 위치 확인
git reset --hard HEAD@{2}     # 2단계 전으로 복구
```

### 시나리오 2: 삭제된 브랜치 복구

```bash
# 실수로 브랜치를 삭제했을 때
git reflog                              # 해당 브랜치의 마지막 커밋 SHA 확인
git checkout -b recovered-branch HEAD@{5}  # 새 브랜치로 복구
```

### 시나리오 3: 잘못된 rebase 되돌리기

```bash
# rebase가 꼬였을 때
git reflog                    # rebase 전의 HEAD 위치 확인
git reset --hard HEAD@{n}     # rebase 전으로 복구
```

---

## 만료 기간

> ⚠️ reflog 항목은 **영구 보관이 아니에요!** 도달 가능 여부에 따라 만료 기간이 다릅니다.

| 설정                             | 기본값    | 대상                                  | 예시                        |
| -------------------------------- | --------- | ------------------------------------- | --------------------------- |
| `gc.reflogExpire`                | **90일**  | 현재 tip에서 **도달 가능한** 항목       | 정상 커밋 이력               |
| `gc.reflogExpireUnreachable`     | **30일**  | 현재 tip에서 **도달 불가능한** 항목     | `reset --hard`로 버린 커밋   |

> 🎒 비유: 도서관 대출 기록부에서 **현재 보유 중인 책의 기록은 90일**, **반납 완료된(더 이상 없는) 책의 기록은 30일** 보관하는 거예요.

⚠️ 즉, `git reset --hard`로 날린 커밋을 복구하려면 **30일 안에** 해야 해요!

### 만료 설정 변경

```bash
# unreachable 항목 만료를 60일로 변경
git config gc.reflogExpireUnreachable "60 days"

# reachable 항목 만료를 180일로 변경
git config gc.reflogExpire "180 days"
```

---

## reflog 파일 위치

```
.git/logs/HEAD              ← HEAD의 이동 기록
.git/logs/refs/heads/main   ← main 브랜치의 이동 기록
.git/logs/refs/tags/v1.0.0  ← 태그의 생성/변경 기록
```

---

## 핵심 정리

1. reflog는 **로컬 머신에서만 존재하는 HEAD/브랜치 이동 일기장**
2. `git log`는 커밋 역사, `reflog`는 HEAD 이동 기록 — 완전히 다른 것
3. 실수 복구의 생명줄: reset, 브랜치 삭제, rebase 실수 모두 복구 가능
4. 도달 가능한 항목은 **90일**, 도달 불가능한 항목은 **30일** 후 정리됨
5. **실수를 복구하려면 빠르게!** unreachable 커밋은 30일만 남아있음

> 📌 관련 문서: [[git-tag-annotated-lightweight]], [[git-cat-file-for-each-ref]]
