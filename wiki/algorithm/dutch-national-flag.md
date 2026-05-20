---
tags: [algorithm, sorting, two-pointer, invariant, leetcode]
created: 2026-05-21
---

# 📖 Dutch National Flag (DNF) — Concept Deep Dive

> 💡 **한줄 요약**: 세 가지 값으로 이루어진 배열을 **한 번의 순회로**, **O(1) 추가 공간**으로 세 영역으로 분할하는 알고리즘 — Edsger W. Dijkstra가 1976년에 제안한 3-way partitioning의 정석.

---

## 1️⃣ 무엇인가? (What is it?)

**Dutch National Flag Problem (DNF)** 은 한 배열을 **세 가지 카테고리**(예: `<pivot`, `==pivot`, `>pivot` 혹은 `0/1/2`)로 **in-place 분할**하는 문제이자 알고리즘입니다.

- 📜 **창시자**: Edsger W. Dijkstra (1976)
- 🇳🇱 **이름의 유래**: 네덜란드 국기의 세 가로 띠(빨강·흰색·파랑)처럼 배열을 세 영역으로 나누는 모양
- 🎯 **해결 문제**: 비교 기반 정렬은 O(n log n) 하한이 있지만, **값의 종류가 3개로 제한**된 경우 O(n)에 in-place로 끝낼 수 있음을 보여주는 사례
- 🧩 **상위 맥락**: 이 알고리즘은 단독 문제일 뿐 아니라 **중복 키가 많은 QuickSort의 핵심 서브루틴**입니다 (3-way QuickSort)

> 📌 **핵심 키워드**: `three-way partitioning`, `in-place`, `loop invariant`, `pivot duplicates`, `Dijkstra`

---

## 2️⃣ 핵심 개념 (Core Concepts)

DNF는 **세 개의 인덱스 포인터**가 **불변 조건(invariant)** 을 지키며 한 방향으로 진행하는 구조입니다.

```
┌────────────────────────────────────────────────────────────┐
│            🇳🇱 Dutch National Flag — 영역 구조              │
├────────────────────────────────────────────────────────────┤
│                                                            │
│   index:   0 ─────────► low ─────► mid ──────► high ─► n-1 │
│           ┌──────────┬────────────┬──────────┬──────────┐  │
│   value:  │  RED(0)  │  WHITE(1)  │ UNKNOWN  │ BLUE(2)  │  │
│           └──────────┴────────────┴──────────┴──────────┘  │
│            (확정 영역)   (확정 영역)  (검사 영역) (확정 영역)│
│                                                            │
└────────────────────────────────────────────────────────────┘
```

| 포인터          | 의미 (불변 조건)                                                  | 진행 방향  |
| --------------- | ------------------------------------------------------------------ | ---------- |
| `low`           | `nums[0 .. low-1]` 전부 **0** (RED)                                | → 오른쪽   |
| `mid`           | `nums[low .. mid-1]` 전부 **1** (WHITE), `mid`는 현재 검사 위치    | → 오른쪽   |
| `high`          | `nums[high+1 .. n-1]` 전부 **2** (BLUE)                            | ← 왼쪽     |
| `[mid .. high]` | **아직 미확인 영역**                                               | —          |

### 🔑 핵심 원리 3가지

1. **분할은 swap만으로 완성된다** — 비교 정렬과 달리 값 카테고리가 유한해서 인덱스 조작으로 충분
2. **`mid`가 `high`를 추월하는 순간 끝** — 미확인 영역(`[mid, high]`)의 크기가 매 스텝마다 1씩 감소하므로 O(n) 보장
3. **불변 조건이 알고리즘을 정의한다** — Dijkstra가 강조한 *"correct by construction"*. 코드를 짜기 전 invariant를 먼저 정한다.

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

### 🏗️ 분기 다이어그램

```
┌──────────────────────────────────────────────────────────┐
│                  while mid <= high                       │
│                                                          │
│           ┌─────────────────────────────────┐            │
│           │       nums[mid] == ?            │            │
│           └────┬──────────┬──────────┬──────┘            │
│                │          │          │                   │
│             == 0       == 1       == 2                   │
│                │          │          │                   │
│                ▼          ▼          ▼                   │
│        ┌───────────┐ ┌────────┐ ┌────────────┐           │
│        │ swap      │ │ mid++  │ │ swap        │          │
│        │ low <-> mid│ │       │ │ mid <-> high│          │
│        │ low++,mid++│ │       │ │ high--      │          │
│        └───────────┘ └────────┘ └────────────┘           │
│                                  (⚠️ mid는 그대로!)       │
└──────────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (Step by Step)

1. **초기화**: `low = 0`, `mid = 0`, `high = n-1`
2. **루프**: `mid <= high` 인 동안 반복
3. **`nums[mid] == 0`**: `low`와 swap 후 `low++`, `mid++`
   - 왜 `mid++`? — `low`에서 가져온 건 1이거나 자기 자신, 어차피 확정 영역에 들어감
4. **`nums[mid] == 1`**: `mid++`만
   - 이미 가운데 영역 소속 값
5. **`nums[mid] == 2`**: `high`와 swap 후 `high--` (**`mid` 고정**)
   - 왜 `mid` 고정? — `high`에서 가져온 값은 미검사. 다음 루프에서 다시 확인 필요
6. **종료**: `mid > high`이면 미확인 영역 소멸 → 정렬 완료

### 💻 Python 구현

```python
def sort_colors(nums: list[int]) -> None:
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:  # 2
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
```

### 📐 복잡도 증명 스케치

미확인 영역 크기 `high - mid + 1` 은 **매 반복마다 정확히 1씩 감소**합니다 (3가지 분기 모두). 초기값 `n` → 0이 되기까지 정확히 `n` 회 → **시간 O(n)**, **공간 O(1)** (포인터 3개만).

---

## 3️⃣-A 포인터 초기값 — 왜 그렇게 두는가? (Deep Dive)

`L=0, M=0, H=n-1` 이라는 초기값은 단순한 "관례"가 아니라 **불변 조건이 처음부터 성립하도록** 정확히 계산된 값입니다.

### ✅ L과 H — 영역의 "경계선"

L과 H는 *값이 있는 자리*가 아니라 **그 값들이 채워질 영역의 경계선**입니다.

| 포인터    | 의미 (위치가 아니라 *영역의 경계*)                                                |
| --------- | --------------------------------------------------------------------------------- |
| `L = 0`   | "**0이 들어갈 다음 빈 칸**" — L 왼쪽 `[0, L)`이 0 확정 영역. 초기엔 빈 구간.       |
| `H = n-1` | "**2가 들어갈 다음 빈 칸**" — H 오른쪽 `(H, n-1]`이 2 확정 영역. 초기엔 빈 구간.   |

> 💡 즉 L과 H는 "가장 작은/큰 값이 *있는* 자리"가 아니라 "그 값들이 *채워질 영역의 경계선*" 이라는 점이 본질입니다.

### 🤏 M — "검사 안 한 영역"의 시작점

흔한 오해: "배열 사이즈가 1개일 수도 있어서 M=0?" → ❌ 그건 부수적 결과일 뿐.

**진짜 이유**: M은 "지금 검사하는 위치 = 검사 안 한 영역의 왼쪽 끝"이고, 알고리즘 시작 시점에는 **아무것도 검사 안 했으므로** 검사 안 한 영역 = 배열 전체 → 그 왼쪽 끝이 0번 인덱스.

> 🚫 만약 `M=1`로 시작하면? `nums[0]`을 영영 검사하지 않고 끝납니다 → 불변 조건 깨짐.

### 📚 책장 비유

빨강·흰색·파랑 책 더미를 정리한다고 상상해보세요.

```
┌────────────────────────────────────────────┐
│  📕📕  🤍🤍  ❓❓❓❓❓  📘📘                  │
│   ↑       ↑           ↑                     │
│  L칸    (흰책영역)    H칸                    │
│         M가 검사중                           │
└────────────────────────────────────────────┘
```

| 손가락          | 의미                                | 처음 위치               |
| --------------- | ----------------------------------- | ----------------------- |
| 🔴 L 손가락     | "다음 **빨간책** 놓을 자리"         | 책장 맨 왼쪽 (0번)      |
| 🔵 H 손가락     | "다음 **파란책** 놓을 자리"         | 책장 맨 오른쪽 (n-1번)  |
| 👀 M 손가락     | "지금 **보고 있는** 책"             | 첫 번째 책부터 봐야 하니 0번 |

→ M=0은 "배열이 작아서"가 아니라 "**첫 책부터 봐야 하니까**" 인 거죠.

### 🧪 보너스: n=1 케이스 추적

**입력**: `nums = [1]`, 초기 `L=0, M=0, H=0`

| 단계 | 조건                    | 동작                    | 상태              |
| ---- | ----------------------- | ----------------------- | ----------------- |
| 1    | `M(0) <= H(0)` ✅       | `nums[0]=1` → `M++`     | `L=0, M=1, H=0`   |
| 2    | `M(1) <= H(0)` ❌       | 종료                    | —                 |

✅ 정상 처리. 만약 M의 초기값을 잘못 줬다면 이런 작은 입력에서 바로 터집니다. 초기값 설계가 엣지 케이스의 1차 방어선인 셈입니다.

### 🎯 사고 프레임

> 💡 **포인터 초기값은 "어디에 있나"가 아니라 "어떤 invariant(불변 조건)를 처음부터 만족시키나"로 정한다.**

| 초기값      | 처음부터 성립하는 invariant       |
| ----------- | --------------------------------- |
| `L = 0`     | "0 확정 영역이 **비어있다**"      |
| `H = n-1`   | "2 확정 영역이 **비어있다**"      |
| `M = 0`     | "검사 안 한 영역이 **배열 전체**" |

이 사고법은 DNF뿐 아니라 **모든 two-pointer / sliding window 문제**에 그대로 적용됩니다. 다음에 비슷한 문제를 만나면 "포인터를 어디 두지?" 대신 "**처음에 무엇이 참이어야 하지?**" 부터 물어보세요. 🚀

### 🤔 추가 확인 포인트

- **왜 L과 M은 같은 값에서 출발해도 안전한가?** → 초기엔 `[L, M) = [0, 0) = ∅`(빈 구간)이라 "1 확정 영역이 비었다"는 invariant도 자동 성립. 이게 알고리즘이 자연스럽게 동작하는 비결입니다.
- **만약 L > M이 되면?** → invariant가 깨져 알고리즘이 망가집니다. 그래서 `nums[mid]==0` 분기에서 항상 `L++`와 `M++`를 **함께** 호출해 둘의 상대 순서를 유지합니다.

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| #   | 유즈 케이스                       | 설명                                                            | 적합한 이유                                  |
| --- | --------------------------------- | --------------------------------------------------------------- | -------------------------------------------- |
| 1   | **LeetCode 75 / Sort Colors**     | 0,1,2 in-place 정렬                                             | 문제 자체가 DNF의 교과서 예제                |
| 2   | **3-way QuickSort**               | 중복 키 많은 입력에서 QuickSort 가속 (Bentley-McIlroy)          | 동일 키 영역을 한 번에 처리 → 재귀 깊이 감소 |
| 3   | **데이터 분류/필터링**            | 부정/중립/긍정, 합격/대기/탈락 같은 3-카테고리 in-place 그룹화  | 추가 메모리 없이 한 번에 분할                |
| 4   | **Pivot equal-key 처리**          | 정렬에서 `==pivot` 원소가 다수일 때 quadratic 회귀 방지         | 동일 키 모두 가운데로 모음                   |
| 5   | **스트림 부분 정렬**              | 한정된 값 도메인의 batch in-place 재배열                        | one-pass O(1) 공간                           |

### ✅ 베스트 프랙티스

1. **invariant를 먼저 글로 적어라** — Dijkstra가 강조: 코드 전에 *"low 왼쪽은 0, mid는 검사 위치, high 오른쪽은 2"* 를 명문화
2. **루프 조건은 `mid <= high`** — `<`는 마지막 1칸을 놓침
3. **`2` 처리 시 `mid` 증가 금지** — 가장 흔한 버그. swap 받은 값을 재검사해야 함
4. **`0` 처리 시 `mid++` 안전성 확인** — `low == mid` 일 때도 안전 (self-swap → 둘 다 진행)
5. **카테고리 매핑을 추상화** — `0/1/2`가 아닌 도메인 값이라면 비교 함수를 분리 (`<pivot` / `==pivot` / `>pivot`)

### 🏢 실제 적용 사례

- **Java 표준 라이브러리** (`Arrays.sort` for primitives): Bentley-McIlroy의 3-way 변형 사용 — 중복 많은 배열에서도 우수한 성능
- **Princeton Algorithms 4e (Sedgewick & Wayne)**: 3-way QuickSort 표준 교재 알고리즘
- **C++ STL `std::partition` / `std::nth_element`**: 유사한 partitioning 사고가 내부에서 활용

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목                          | 설명                                                                    |
| ---- | ----------------------------- | ----------------------------------------------------------------------- |
| ✅   | **O(n) 시간**                 | 비교 횟수 최대 n번                                                      |
| ✅   | **O(1) 공간**                 | in-place — 포인터 3개만 사용                                            |
| ✅   | **One-pass**                  | 입력을 한 번만 훑음 (counting sort는 2-pass)                            |
| ✅   | **Quicksort 강화**            | 중복 키 많을 때 O(n) 처리로 quadratic 회귀 방지                         |
| ✅   | **Cache-friendly**            | 인덱스가 인접하게 진행 → 메모리 지역성 좋음                             |
| ❌   | **3 카테고리에 특화**         | k>3이면 일반화 어려움 (multi-pass DNF 또는 다른 알고리즘 필요)          |
| ❌   | **불안정 정렬 (Unstable)**    | swap 과정에서 같은 값의 상대 순서 보존 안 됨                            |
| ❌   | **invariant 추론 비용**       | 처음 보면 헷갈림 — counting sort보다 사고 부담 큼                       |
| ❌   | **카테고리 값이 명확해야 함** | 비교 함수가 일관된 3-way 결과를 줘야 함                                 |

### ⚖️ Trade-off 분석

```
One-pass + O(1) 공간   ◄──── Trade-off ────►   인지 부담 ↑
일반 정렬 비교 O(nlogn) ◄──── Trade-off ────►   3 카테고리 제약
중복 키에 강함         ◄──── Trade-off ────►   불안정 정렬
```

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 비교 매트릭스

| 비교 기준    | **DNF (3-pointer)**           | **Counting Sort**         | **2-pointer Partition** (Lomuto/Hoare) | **Bentley-McIlroy 3-way**      |
| ------------ | ----------------------------- | ------------------------- | -------------------------------------- | ------------------------------ |
| 시간 복잡도  | O(n)                          | O(n+k)                    | O(n)                                   | O(n) per partition             |
| 공간 복잡도  | **O(1)**                      | O(k) (카운트 배열)        | O(1)                                   | O(1)                           |
| 패스 수      | **1-pass**                    | 2-pass                    | 1-pass                                 | 1-pass                         |
| 카테고리 수  | **정확히 3**                  | k개 (도메인 크기)         | 2개                                    | 3 (≤, =, >)                    |
| 안정성       | ❌ 불안정                     | ✅ 안정                   | ❌ 불안정                              | ❌ 불안정                      |
| 대표 활용    | LeetCode 75, 3-way QS         | 한정 도메인 정수 정렬     | QuickSort 분할 단계                    | JDK `Arrays.sort` (primitive)  |
| 중복 키 처리 | 자연스러움                    | 자연스러움                | 약점 (반복 키 → O(n²))                 | 강함                           |

### 🔍 핵심 차이 요약

```
DNF (3-pointer)              Counting Sort               2-pointer Partition
─────────────────     vs    ─────────────────     vs    ─────────────────────
1-pass                       2-pass                      1-pass
3 영역 분할                   k 영역 분할                  2 영역 분할 (pivot 기준)
O(1) 공간                    O(k) 카운트 배열             O(1) 공간
포인터 3개 (low,mid,high)     카운트 후 재구성             포인터 2개 (left,right)
```

### 🤔 언제 무엇을 선택?

- **DNF 선택**: 정확히 3 카테고리이고, one-pass + O(1) 공간 제약이 있을 때 (인터뷰 follow-up, 메모리 민감한 임베디드 등)
- **Counting Sort 선택**: 카테고리 수 k가 가변이거나, **안정 정렬**이 필요하거나, 입력 검증 차원에서 2-pass가 더 직관적일 때
- **2-pointer Partition 선택**: QuickSort 같은 일반 정렬에서 pivot 분할이 목적이고, 중복 키가 적을 때
- **Bentley-McIlroy 선택**: 표준 라이브러리 수준의 견고함이 필요하고, 분할 키가 많이 중복될 가능성이 있을 때

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| #   | 실수                                       | 왜 문제인가                                | 올바른 접근                     |
| --- | ------------------------------------------ | ------------------------------------------ | ------------------------------- |
| 1   | `while mid < high` 사용                    | 마지막 한 칸 미검사 → 정렬 불완전          | `while mid <= high`             |
| 2   | `nums[mid] == 2`에서 `mid++` 함께 호출     | `high`에서 가져온 미검사 값 건너뜀         | `mid` 고정, `high--`만          |
| 3   | `nums[mid] == 0`에서 `mid++` 누락          | low/mid가 무한 루프 가능성                 | `low++`, `mid++` 둘 다          |
| 4   | 포인터 초기값 오류 (`high = n` 등)         | off-by-one → IndexError 또는 미정렬        | `high = n - 1`                  |
| 5   | invariant 없이 즉흥 코딩                   | 엣지 케이스에서 실패 → 디버깅 지옥         | 먼저 글로 invariant 명시        |

### 🚫 Anti-Patterns

1. **"내장 sort 쓰지" 함정** — 문제 제약("정렬 함수 금지" / one-pass)을 무시하면 알고리즘 학습 목적 상실
2. **카운트 후 재할당 + DNF 혼용** — 한 풀이에 두 접근 섞으면 코드만 길어지고 이점 없음
3. **k=3 이상으로 무리한 일반화** — 4 카테고리 이상은 별도 알고리즘(예: bucket/counting sort, multi-pass DNF) 권장
4. **invariant 검증 없이 변형** — 분기 조건만 살짝 바꾸면 불변 조건이 깨져 미묘한 버그 발생

### 🔒 보안/성능 고려사항

- ⚡ **성능**: 비교 함수가 무거우면 (사용자 정의 객체 등) swap보다 비교 비용이 지배적 — pivot 캐싱 고려
- ⚡ **branch prediction**: 분기가 3개라 CPU의 분기 예측 실패 가능성 존재. 매우 큰 배열에서는 분기 없는(branchless) 변형이 유리할 수도 있음
- 🔒 **immutable 입력 가정**: in-place 변경이므로 호출자가 원본 보존을 기대하면 안 됨 — 시그니처/문서에 명확히
- 📏 **stability 필요 시 사용 금지** — 같은 값의 원래 순서가 의미 있다면 안정 정렬(예: merge sort, counting sort) 사용

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형        | 이름                                                    | 링크/설명                                   |
| ----------- | ------------------------------------------------------- | ------------------------------------------- |
| 📖 위키     | Dutch national flag problem (Wikipedia)                 | 정의·역사·변형 정리                         |
| 📘 도서     | *Algorithms, 4th Edition* — Sedgewick & Wayne           | 3-way QuickSort 표준 챕터                   |
| 📘 도서     | *A Discipline of Programming* — Dijkstra (1976)         | 원전. invariant 기반 사고법                 |
| 📄 논문     | Bentley & McIlroy, *"Engineering a Sort Function"* (1993) | JDK가 채택한 3-way 변형                     |
| 📄 강의노트 | David Gries — *The Dutch National Flag* (Cornell, 2018) | invariant 4가지 비교 분석 (PDF)             |
| 🎯 연습     | LeetCode #75 Sort Colors                                | 기본기 점검                                 |
| 🎯 연습     | LeetCode #905, #922 Sort Array By Parity                | 2-way 변형으로 일반화 감각 익히기           |

### 🛠️ 관련 도구 & 라이브러리

| 도구/라이브러리                          | 언어/플랫폼   | 용도                                |
| ---------------------------------------- | ------------- | ----------------------------------- |
| `Arrays.sort` (primitive)                | Java          | 내부에 Bentley-McIlroy 3-way QS     |
| `std::partition` / `std::nth_element`    | C++ STL       | 유사한 partitioning 사고            |
| `numpy.partition`                        | Python        | k-th 원소 기준 partition            |
| `pdqsort` (Pattern-defeating QS)         | Rust/C++/Go   | 현대적 3-way 후속 (Orson Peters)    |

### 🔮 트렌드 & 전망

- 🚀 **Pattern-defeating QuickSort (pdqsort)**: 2021년 발표, Rust/C++ 표준 라이브러리 채택. DNF식 3-way를 발전시킨 현대적 변형 — 정렬된 입력·중복 키 모두에 강함
- 🧪 **Branchless variants**: SIMD/CPU 파이프라인을 고려한 분기 최소화 변형 연구 활발 (`arXiv:2502.06461`)
- 🎓 **교육적 가치**: invariant 기반 알고리즘 설계의 정석으로 여전히 CS 커리큘럼의 표준 사례

### 💬 커뮤니티 인사이트

- 💡 *"외우지 말고 invariant로 유도하라"* — Dev.to 글의 핵심 메시지. 분기 3개 외우기보다 "각 포인터가 보장하는 영역"을 명확히 하면 자연스럽게 코드가 나옴
- 💡 인터뷰에서는 보통 **2-pass counting sort → "one-pass로 줄여보세요" → DNF** 흐름이 정석. 면접관이 follow-up을 던지면 immediately 3-pointer를 꺼내는 것이 신호
- 💡 코드 리뷰에서 자주 지적되는 라인은 **`mid <= high`** 와 **`2` 분기의 `mid` 고정** — 이 두 곳에 주석 한 줄 다는 게 베스트 프랙티스

---

## 📎 Sources

1. [Dutch national flag problem — Wikipedia](https://en.wikipedia.org/wiki/Dutch_national_flag_problem) — 공식/백과
2. [The Dutch National Flag — David Gries (Cornell, 2018)](https://www.cs.cornell.edu/courses/JavaAndDS/files/sort9DutchFlag.pdf) — 학술 강의자료
3. [3-Way QuickSort (Dutch National Flag) — GeeksforGeeks](https://www.geeksforgeeks.org/dsa/3-way-quicksort-dutch-national-flag/) — 기술 블로그
4. [Quicksort — Princeton Algorithms 4e](https://algs4.cs.princeton.edu/23quicksort/) — 학술 표준 교재
5. [Partitioning and Sorting Arrays with Many Repeated Entries — Baeldung](https://www.baeldung.com/java-sorting-arrays-with-repeated-entries) — JDK Bentley-McIlroy 적용 설명
6. [Three Way Partitioning — OpenGenus](https://iq.opengenus.org/three-way-partitioning/) — 알고리즘 분석
7. [Sorting 0s, 1s, 2s: Stop Memorizing the Dutch National Flag Algorithm — Dev.to](https://dev.to/alex_hunter_44f4c9ed6671e/sorting-0s-1s-2s-stop-memorizing-the-dutch-national-flag-algorithm-3872) — 커뮤니티 인사이트
8. [Pattern-defeating Quicksort — arXiv 2106.05123](https://arxiv.org/pdf/2106.05123) — 후속 연구
9. [The Dutch National Flag Algorithm — Medium (Jyotsna)](https://medium.com/@jyotsnay24/the-dutch-national-flag-algorithm-efficient-sorting-in-three-categories-5aabe8a35d61) — 시각화 자료

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 6 (병렬 WebSearch)
> - 수집 출처 수: 9 (인용 기준), ~40 (전체 후보)
> - 출처 유형: 공식/백과 1, 학술 3, 기술 블로그 3, 커뮤니티 2
