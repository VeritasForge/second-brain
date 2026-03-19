---
created: 2026-03-19
source: claude-code
tags: [python, dictionary, hash-table, data-structure, cpython-internals]
---

# Python Dictionary의 Key 순서 보장 원리

## 역사

| Python 버전 | dict 삽입 순서 | 비고                                   |
| ----------- | -------------- | -------------------------------------- |
| ~3.5        | 보장 안 됨     | `OrderedDict` 필요                     |
| 3.6         | 구현상 보장    | CPython 한정, 공식 스펙은 아님         |
| 3.7+        | **공식 보장**  | 언어 스펙으로 확정                     |

---

## 왜 원래 순서를 보장 못했나?

dict는 내부적으로 **hash table**입니다. key를 저장할 때:

```
key "apple"  → hash("apple")  → 예: 394028 → 394028 % 8 = 4번 슬롯에 저장
key "banana" → hash("banana") → 예: 281003 → 281003 % 8 = 3번 슬롯에 저장
```

비유하면 **사물함**이에요:
- 이름표(key)를 해시 함수에 넣으면 사물함 번호가 나옴
- "apple"은 4번 사물함, "banana"는 3번 사물함
- 순회할 때 사물함 번호 순서(3→4)로 돌기 때문에 **넣은 순서(apple→banana)와 다를 수 있음**

---

## 순서 보장을 위한 두 가지 접근법

dict와 OrderedDict 모두 "**Hash Table + 순서 유지 장치**"의 조합이지만, 순서를 유지하는 장치가 다릅니다:

```
dict (3.7+):    Hash Table + 순서 배열
OrderedDict:    Hash Table + 이중 연결 리스트
                ──────────   ─────────────────
                같은 역할     같은 역할 (순서 유지)
                (빠른 조회)   but 구현 방식이 다름
```

---

## dict (3.7+): Hash Table + 순서 배열

**별도의 삽입 순서 배열**을 추가했습니다. dict는 **두 개의 테이블**로 구성됩니다:

```
1. Hash Table (인덱스 테이블):  hash → 순서 배열의 인덱스
2. 순서 배열 (entries):        실제 key, value, hash 저장
```

```
[기존] hash table만:
  슬롯0: -
  슬롯1: -
  슬롯2: -
  슬롯3: banana  ← hash 결과에 따른 위치
  슬롯4: apple
  → 순회: banana, apple (삽입 순서 아님!)

[3.7+] hash table + 순서 배열:
  Hash Table:  슬롯3→인덱스1, 슬롯4→인덱스0  (위치 찾기용)
  순서 배열:   [apple, banana]                  (삽입 순서 유지)
  → 순회: apple, banana (삽입 순서 보장!)
```

이 방식이 메모리도 더 적게 쓰고 순서도 보장해서 일석이조였습니다.

---

## OrderedDict: Hash Table + 이중 연결 리스트

```
d = OrderedDict([("apple", 1), ("banana", 2), ("peach", 3)])

[Hash Table]                    [이중 연결 리스트]
  "apple"  → 값1, 노드A          HEAD ⇄ 노드A ⇄ 노드B ⇄ 노드C ⇄ TAIL
  "banana" → 값2, 노드B                (apple)  (banana)  (peach)
  "peach"  → 값3, 노드C
```

| 연산                         | 누가 담당?                                  |
| ---------------------------- | ------------------------------------------- |
| `d["apple"]` (조회)          | Hash Table                                  |
| `for k in d` (순회)          | 이중 연결 리스트 (HEAD부터 따라감)          |
| `move_to_end("apple")`       | 이중 연결 리스트 (포인터 재연결)            |
| `del d["banana"]`            | Hash Table에서 제거 + 연결 리스트에서 노드 분리 |

왜 이중 연결 리스트인가? `move_to_end` 같은 **순서 조작** 때문입니다:

```
배열로 "banana를 맨 뒤로 이동":
  [apple, banana, peach] → banana 제거 → peach 앞으로 당김 → 뒤에 추가
  = O(n) (요소들을 밀어야 함)

이중 연결 리스트로 "banana를 맨 뒤로 이동":
  apple ⇄ banana ⇄ peach
  1. banana의 앞뒤 연결을 끊고 apple ⇄ peach로 이어줌
  2. peach 뒤에 banana를 붙임
  = O(1) (포인터만 변경)
```

비유:
- **dict의 순서 배열** = 줄 서있는 사람들. 중간에서 빠지면 뒤 사람들이 한 칸씩 앞으로 와야 함 (그래서 DUMMY로 대체)
- **OrderedDict의 연결 리스트** = 손을 잡고 있는 사람들. 중간에서 빠지면 양옆 사람끼리 손잡으면 끝. 맨 뒤로 이동도 손만 다시 잡으면 됨

---

## dict의 삭제 처리: Lazy Deletion

배열에서 중간 요소를 삭제하면 뒤의 요소들을 당겨야 해서 O(n)이 될 것 같지만, Python dict는 **실제로 제거하지 않고 "DUMMY(tombstone)" 표시**만 합니다:

```
삽입: apple, banana, peach

Hash Table:           순서 배열:
  슬롯3: → 인덱스0      [0] apple, 값A
  슬롯4: → 인덱스1      [1] banana, 값B
  슬롯1: → 인덱스2      [2] peach, 값C

banana 삭제 후:
  Hash Table:           순서 배열:
    슬롯3: → 인덱스0      [0] apple, 값A
    슬롯4: DUMMY  ←!!    [1] DUMMY
    슬롯1: → 인덱스2      [2] peach, 값C
```

### DUMMY가 영향을 미치는 곳

| 연산                     | DUMMY 관련 동작                                          |
| ------------------------ | -------------------------------------------------------- |
| `d["apple"]` (조회)      | hash table → 인덱스 → 바로 접근. **DUMMY 무관**          |
| `for k in d` (순회)      | 순서 배열을 훑으며 **DUMMY 건너뜀**                      |
| `"apple" in d` (존재 확인) | hash table probing 시 DUMMY 슬롯은 **"계속 탐색" 신호** |

**조회**는 hash table이 정확한 인덱스를 알려주므로 순서 배열을 훑을 필요가 없습니다.
**순회**할 때만 DUMMY를 건너뛰는 동작이 발생합니다.

### Hash Table의 DUMMY가 쌓이면 생기는 문제

Hash table에서 key를 찾을 때 **충돌(collision)**이 발생하면 다음 슬롯을 탐색합니다(probing):

```
"grape"를 찾는다고 하면:
  hash("grape") % 8 = 4번 슬롯
  → 슬롯4: DUMMY → "여기 뭔가 있었네, 다음 슬롯도 봐야 해"
  → 슬롯5: 확인... → 슬롯6: 확인...
```

- **비어있는 슬롯(empty)**: "여기까지 없으면 진짜 없는 거야" → 탐색 종료
- **DUMMY 슬롯**: "여기 뭔가 있다가 삭제됐으니, 뒤에 더 있을 수 있어" → **탐색 계속**

비유: 복도의 사물함
- 사물함이 비어있으면 "이 뒤로는 안 봐도 돼" (탐색 종료)
- 사물함에 "사용했다 비움" 스티커가 붙어있으면 "혹시 뒤에 더 있을 수 있으니 계속 봐야 해" (탐색 계속)

DUMMY가 많아지면 → probing 체인이 길어짐 → **조회 성능이 O(1)에서 점점 느려짐**

### Resize로 정리

DUMMY 비율이 일정 수준을 넘으면 **hash table을 재구성(resize)**합니다:

```
resize 전:
  Hash Table: [-, 인덱스2, -, 인덱스0, DUMMY, DUMMY, DUMMY, -]
  순서 배열:  [apple, DUMMY, peach]

resize 후:
  Hash Table: [-, 인덱스1, -, 인덱스0]  ← DUMMY 없는 깨끗한 테이블
  순서 배열:  [apple, peach]             ← DUMMY 제거, 압축
```

resize는 가끔 발생하고 O(n)이지만, **amortized(분할 상환) O(1)**로 평균적으로는 O(1)을 유지합니다.

---

## dict vs OrderedDict 비교

|                | dict (3.7+)                              | OrderedDict                  |
| -------------- | ---------------------------------------- | ---------------------------- |
| 순서 유지 방식 | 순서 배열                                | 이중 연결 리스트             |
| 메모리         | 적음                                     | 많음 (포인터 2개씩)          |
| `move_to_end`  | 지원 안 함                               | O(1)                         |
| 중간 삭제      | DUMMY 표시                               | 포인터 재연결                |
| 순회 성능      | 빠름 (연속 메모리, 캐시 친화적)          | 느림 (포인터 따라 점프)      |
| 순서 비교      | 무시 (`==`에서)                          | 고려 (`==`에서)              |
| 삽입/조회      | O(1)                                     | O(1)                         |

```python
# OrderedDict만 가능한 것
from collections import OrderedDict

od = OrderedDict([('a', 1), ('b', 2), ('c', 3)])
od.move_to_end('a')              # 특정 key를 맨 뒤로 이동
od.move_to_end('c', last=False)  # 특정 key를 맨 앞으로 이동

# 순서까지 고려한 비교
OrderedDict([('a', 1), ('b', 2)]) == OrderedDict([('b', 2), ('a', 1)])  # False
{'a': 1, 'b': 2} == {'b': 2, 'a': 1}  # True (dict는 순서 무시 비교)
```

---

## 핵심 정리

1. **원래 dict**는 hash 기반이라 key의 저장 위치가 hash 값에 의해 결정되어 삽입 순서를 보장하지 못했다
2. **Python 3.7+**에서 별도의 순서 배열을 추가하여 삽입 순서를 공식 보장하게 되었다
3. **OrderedDict**는 이중 연결 리스트로 순서를 유지하여 `move_to_end` 같은 순서 조작을 O(1)에 지원한다
4. **dict의 삭제 시** 실제로 제거하지 않고 DUMMY(tombstone) 표시로 O(1)을 유지하고, DUMMY가 쌓이면 resize로 정리한다
5. **대부분의 경우** `OrderedDict`는 불필요해졌지만, 순서 조작(`move_to_end`)이나 순서 비교가 필요하면 여전히 유용하다
