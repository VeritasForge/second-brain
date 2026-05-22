---
tags: [algorithm, two-pointer, in-place, array, pattern, leetcode]
created: 2026-05-22
---

# 📖 Read / Write 패턴 완벽 가이드

## 🎯 핵심 정의

> **두 개의 포인터(read, write)를 같은 방향으로 움직이며, "보관할 원소"만 앞쪽에 채워나가는 in-place 처리 패턴**

- **read 포인터** 📖: 배열 전체를 한 칸씩 읽으며 스캔 (멈추지 않음)
- **write 포인터** ✍️: "유효한 원소"가 들어갈 다음 빈 자리 (조건 만족 시에만 전진)

핵심 아이디어: **read는 항상 앞서간다 (`read ≥ write`)** — 그래서 write 자리에 덮어써도 아직 안 읽은 원소를 잃지 않습니다.

---

## 🍱 12살을 위한 비유: 사진첩 정리하기

```
📷 책상 위 사진들 (입력):
[ 흐릿 | 선명 | 흐릿 | 선명 | 선명 ]

목표: 새 앨범에 선명한 사진만 앞에서부터 채우기 (in-place)
```

| 역할    | 비유                              | 동작                                          |
| ------- | --------------------------------- | --------------------------------------------- |
| `read`  | 사진을 한 장씩 넘겨보는 손가락 👆 | 모든 사진을 차례로 본다 (멈추지 않음)         |
| `write` | 새 앨범의 다음 빈 페이지 📔       | 선명한 사진을 만났을 때만 한 칸 넘긴다        |

**규칙:**

1. read가 흐릿한 사진을 보면 → **그냥 넘어감** (write는 그대로)
2. read가 선명한 사진을 보면 → **write 자리에 사진을 둠** → write 한 칸 이동

결과: 앨범 앞쪽 = 선명한 사진들, 뒤쪽 = (무엇이 남아있든 상관없음)

---

## 🧩 일반화된 코드 구조

```python
def in_place_filter(nums: list[int]) -> int:
    """조건을 만족하는 원소만 앞쪽에 모은다. write 인덱스를 반환."""
    write = 0
    for read in range(len(nums)):
        if 조건_만족(nums[read]):
            nums[write] = nums[read]   # 덮어쓰기 or swap
            write += 1
    return write   # write = "유효한 원소 개수"
```

**구성요소 3가지**:

| 요소                            | 역할                  |
| ------------------------------- | --------------------- |
| `for read in range(...)`        | 전체 스캔             |
| `if 조건_만족(...)`             | 보관 여부 결정        |
| `nums[write] = ...; write += 1` | 채우고 한 칸 전진     |

---

## 📊 단계별 시각화: `move_zeroes([0, 1, 0, 3, 12])`

조건: **"0이 아닌 원소"만 앞으로**

```
초기:  write=0, read=0
       ┌─ write
       ↓
nums = [0, 1, 0, 3, 12]
       ↑
       └─ read

read=0: nums[0]=0 → 스킵
        write=0, read=1

       ┌─ write
       ↓
nums = [0, 1, 0, 3, 12]
          ↑
          └─ read
read=1: nums[1]=1 ≠ 0 → swap(write=0, read=1)
        nums = [1, 0, 0, 3, 12]
        write=1, read=2

          ┌─ write
          ↓
nums = [1, 0, 0, 3, 12]
             ↑
             └─ read
read=2: nums[2]=0 → 스킵
        write=1, read=3

          ┌─ write
          ↓
nums = [1, 0, 0, 3, 12]
                ↑
                └─ read
read=3: nums[3]=3 ≠ 0 → swap(write=1, read=3)
        nums = [1, 3, 0, 0, 12]
        write=2, read=4

             ┌─ write
             ↓
nums = [1, 3, 0, 0, 12]
                   ↑
                   └─ read
read=4: nums[4]=12 ≠ 0 → swap(write=2, read=4)
        nums = [1, 3, 12, 0, 0]
        write=3, read=5

종료. 결과: [1, 3, 12, 0, 0] ✅
```

---

## 🔒 불변량 (Invariant) — 이 패턴의 심장 ❤️

**루프의 매 시점에 다음이 성립합니다:**

```
nums[0 : write]      → "조건을 만족하는 확정된 원소들"
nums[write : read]   → "이미 읽었지만 조건 불만족 (혹은 swap된 0들)"
nums[read :]         → "아직 안 읽음"
```

시각화:

```
[ ✅ 확정된 유효 원소 | 🗑️ 스킵된 원소들 | ❓ 미탐색 ]
 0                  write                read           n
```

> 💡 **불변량을 입으로 말할 수 있으면 코드는 거의 자동으로 나옵니다.** TDD에서 "테스트 먼저"처럼, 이 패턴에서는 "불변량 먼저"입니다.

---

## 🎯 언제 쓰는가? — 패턴 식별 신호

다음 키워드가 보이면 read/write를 의심하세요:

| 키워드                            | 예시                                       |
| --------------------------------- | ------------------------------------------ |
| **"in-place로 ~~를 제거"**        | 27. Remove Element                         |
| **"중복 제거 후 길이 반환"**      | 26. Remove Duplicates from Sorted Array    |
| **"~~를 끝으로 이동"**            | 283. Move Zeroes                           |
| **"순서를 유지하면서 필터링"**    | 일반적 stream filtering                    |
| **"O(1) 추가 공간" + 배열 수정**  | 거의 확정                                  |

---

## 📚 LeetCode 대표 문제 매핑

| #    | 문제                                  | 조건                                          | 동작                                |
| ---- | ------------------------------------- | --------------------------------------------- | ----------------------------------- |
| 26   | Remove Duplicates from Sorted Array   | `nums[read] != nums[write-1]`                 | `nums[++write] = nums[read]`        |
| 27   | Remove Element                        | `nums[read] != val`                           | `nums[write++] = nums[read]`        |
| 80   | Remove Duplicates II (최대 2개 허용)  | `write < 2 or nums[read] != nums[write-2]`    | `nums[write++] = nums[read]`        |
| 283  | Move Zeroes                           | `nums[read] != 0`                             | swap 또는 덮어쓰기                  |
| 905  | Sort Array By Parity                  | (변형: 양쪽에서 swap)                         | 짝/홀 분리                          |
| 1089 | Duplicate Zeros                       | (역방향 read/write)                           | 뒤에서부터 복사                     |

---

## 🔀 두 가지 변형: Swap vs Overwrite

### 변형 A: Swap (예: 283 Move Zeroes — 원본 원소를 보존해야 할 때)

```python
nums[write], nums[read] = nums[read], nums[write]
write += 1
```

- read 자리에 있던 값이 write 자리로 **이동** (사라지지 않음)
- Move Zeroes에서 0이 뒤로 밀려나는 효과

### 변형 B: Overwrite (예: 27 Remove Element — 버려도 될 때)

```python
nums[write] = nums[read]
write += 1
```

- read 자리 값을 write에 **덮어쓰기**
- write < read일 수 있고, write 뒤의 값은 보장 안 함
- 보통 "유효한 길이"만 반환하는 문제

| 변형      | 예시 문제   | 비교                                  |
| --------- | ----------- | ------------------------------------- |
| swap      | 283, 905    | 모든 원소를 보존 (위치만 재배치)      |
| overwrite | 26, 27, 80  | 잉여 원소는 버려도 됨                 |

---

## ⚠️ 자주 하는 실수

### 🚩 실수 1: read를 조건부로 전진

```python
# ❌ 잘못된 패턴
while read < len(nums):
    if nums[read] == 0:
        write += 1     # write를 잘못 움직임
    else:
        ...
    read += 1
```

→ **read는 항상 전진**, write만 조건부로 전진. 이걸 섞으면 거의 항상 버그.

### 🚩 실수 2: write 자리에 덮어쓰고 원본을 잃음

```python
# ❌ 정렬 안 된 배열에서
nums[write] = nums[read]   # write < read일 때만 안전
```

→ `nums[write]`에 아직 안 읽은 중요한 값이 있을 수 있음. swap이 안전한 기본 선택.

### 🚩 실수 3: write를 안 올림 / 두 번 올림

```python
if 조건:
    nums[write] = nums[read]
    # ❌ write += 1 빠뜨림 → 무한히 같은 자리에 덮어씀
```

→ "쓰고 나면 반드시 한 칸 전진" 짝으로 외우세요.

---

## 🔄 다른 두-포인터 패턴과의 비교

| 패턴                          | 포인터 방향              | 대표 문제                       | 키워드             |
| ----------------------------- | ------------------------ | ------------------------------- | ------------------ |
| **read/write**                | 같은 방향 (단방향)       | 26, 27, 283                     | in-place 필터      |
| **양 끝 좁히기** (left/right) | 반대 방향 (수렴)         | 167. Two Sum II, 11. Container  | 정렬 + 합/곱       |
| **fast/slow**                 | 같은 방향, 다른 속도     | 141. Linked List Cycle          | 사이클 감지        |
| **sliding window**            | 같은 방향, [L, R) 구간   | 3. Longest Substring            | 부분 구간 최적화   |

**암기 팁** 🧠:

- 한쪽이 **"무엇을 채울 자리"**면 → **read/write**
- 양쪽이 **"탐색 경계"**면 → **left/right**
- 한쪽이 **"느리고 한쪽이 빠르면"** → **fast/slow**
- 양쪽이 **"구간의 끝"**이면 → **sliding window**

---

## 🧪 작은 연습 문제

다음 코드의 빈칸을 채워보세요 (LeetCode 27. Remove Element):

```python
def remove_element(nums: list[int], val: int) -> int:
    """val과 같은 원소를 제거하고 새 길이를 반환."""
    write = 0
    for read in range(len(nums)):
        if _________:           # ← 조건은?
            nums[write] = nums[read]
            _________            # ← 무엇을 해야?
    return write
```

<details>
<summary>👀 정답 보기</summary>

```python
if nums[read] != val:
    nums[write] = nums[read]
    write += 1
```

</details>

---

## 💡 다음에 확인하면 좋을 것

1. **역방향 read/write** (LeetCode 88. Merge Sorted Array, 1089. Duplicate Zeros) — 앞에서 쓰면 원본 소실 → 뒤에서부터 채우는 트릭
2. **다중 조건 read/write** (LeetCode 80) — `write-1`, `write-2`까지 비교하는 누적 조건
3. **불변량 작성 훈련** — 새 문제를 풀 때 "nums[0:write]는 ___" 한 문장을 먼저 적어보기

이 패턴을 익히면 in-place 배열 조작 문제의 70%는 같은 틀로 해결됩니다. 직접 27번 또는 26번을 풀어보시면 체화에 도움이 됩니다. 🚀

---

## 관련 문서

- [[dutch-national-flag]] — 3-포인터 + invariant 사고법 (read/write의 확장)
- [[subarray-vs-subsequence-vs-subset]] — 배열 부분 구조 개념
- [[coding-test-preparation-strategy]] — 코딩 테스트 준비 전략
