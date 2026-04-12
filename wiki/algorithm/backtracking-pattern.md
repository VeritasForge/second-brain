---
created: 2026-02-10
source: claude-code
tags:
  - algorithm
  - backtracking
  - dfs
  - recursion
---

## 백트래킹 (Backtracking)

### 한마디로

**"선택 → 탐색 → 되돌리기"를 반복하는 탐색 전략**입니다.

### 현실 비유: 미로 찾기

갈림길이 3개인 미로를 상상해보세요:

```
       [시작]
      /  |  \
     A   B   C
    / \     / \
   X   Y   Z   출구!
  (막힘)     (막힘)
```

1. A를 선택 → X로 가봄 → 막힘 → **A로 되돌아감** (backtrack!)
2. Y로 가봄 → 막힘 → **A로 되돌아감** → A 다 봤으니 **시작으로 되돌아감**
3. B를 선택 → 막힘 → **시작으로 되돌아감**
4. C를 선택 → 출구 발견!

"막다른 길이면 **되돌아와서** 다른 길을 시도한다" — 이 **되돌아오는 행위**가 backtrack입니다.

### 방금 풀었던 코드와 매핑

```python
for i in range(start, len(candidates)):
    path.append(candidates[i])          # 1. 선택 (길을 고른다)
    f(i, path, remain - candidates[i])  # 2. 탐색 (그 길로 들어간다)
    path.pop()                          # 3. 되돌리기 (돌아와서 다른 길 시도)
```

`path.pop()`이 바로 **backtrack**하는 순간입니다. 이 한 줄이 없으면 이전 선택이 남아서 엉망이 됩니다.

### 백트래킹의 패턴

거의 모든 백트래킹 문제가 이 구조를 따릅니다:

```
함수(현재 상태):
    if 정답 조건:
        결과 저장
        return
    if 불가능 조건:
        return              ← 가지치기 (pruning)

    for 선택지 in 후보들:
        선택                 ← append / 값 변경
        함수(다음 상태)       ← 재귀
        되돌리기              ← pop / 값 복원
```

### 어디에 쓰이나?

| 문제 유형   | 예시                                       |
| ----------- | ------------------------------------------ |
| 조합/순열   | **39. Combination Sum**, 46. Permutations  |
| 부분집합    | 78. Subsets                                |
| 그리드 탐색 | N-Queens, 스도쿠                           |
| 문자열      | 17. Letter Combinations of a Phone Number  |

이전에 풀었던 46. Permutations도 동일한 백트래킹 패턴이었습니다. 앞으로 이 세 줄 (선택 → 재귀 → 되돌리기)이 보이면 "백트래킹이구나"라고 바로 알아볼 수 있을 겁니다.
