---
created: 2026-02-06
source: claude-code
tags:
  - git
  - rebase
  - branching
---

# `git rebase --onto` 설명

## 기본 구문

```bash
git rebase --onto <새로운_베이스> <기존_베이스> <브랜치>
```

의미: **`<브랜치>`에서 `<기존_베이스>` 이후의 커밋들만 떼어내서 `<새로운_베이스>` 위에 붙여라**

## 예시 1: 브랜치 기반 변경 (release → develop)

release 브랜치에서 분기한 feature 브랜치를, develop 기반으로 옮기고 싶을 때:

```
기존 상태:

         E (release)
        /
A - B - C (develop)
         \
          F (feature) ← 우리 커밋

명령어:
git rebase --onto origin/develop origin/release feature

결과:

         E (release)
        /
A - B - C (develop)
          \
           F' (feature) ← develop 위로 이동됨
```

- `origin/release` (E) 이후의 커밋 = F
- 그 F를 `origin/develop` (C) 위에 얹음

## 예시 2: 파생 브랜치 기반 변경

feature-A에서 파생된 feature-B를, main 기반으로 바꾸고 싶을 때:

```
기존 상태:

A - B - C (main)
         \
          D - E (feature-A)
               \
                F - G (feature-B)

명령어:
git rebase --onto main feature-A feature-B

결과:

A - B - C (main)
        |\
        | D - E (feature-A)
         \
          F' - G' (feature-B) ← main 위로 이동됨
```

- `feature-A` (E) 이후의 커밋 = F, G
- 그것들을 `main` (C) 위에 얹음

## 예시 3: 중간 커밋 제거

특정 범위의 커밋만 골라서 옮길 때:

```
기존 상태:

A - B - C - D - E (my-branch)

B~D 커밋(C, D)을 빼고 E만 B 위에 올리고 싶다면:

git rebase --onto B D my-branch

결과:

A - B - E' (my-branch)
```

- `D` 이후의 커밋 = E
- 그 E를 `B` 위에 얹음 → C, D가 사라짐

## 일반 rebase와의 차이

| 명령어                        | 동작                                             |
| ----------------------------- | ------------------------------------------------ |
| `git rebase main`             | 현재 브랜치의 **모든 고유 커밋**을 main 위로     |
| `git rebase --onto A B C`     | C 브랜치에서 **B 이후 커밋만** A 위로            |

핵심은 `--onto`가 **"어디서부터 떼어낼지"**와 **"어디에 붙일지"**를 분리해서 지정할 수 있다는 점입니다.
