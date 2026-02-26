---
created: 2026-02-12
source: claude-code
tags:
  - algorithm
  - coding-test
  - study-strategy
---

## 코딩테스트 준비, 전략을 바꿔야 할 때

솔직하게 말하면, 지금 겪고 있는 상황은 **공부 방법의 문제**이지 능력의 문제가 아닙니다. 이미 Combination Sum, Permutations, Search in Rotated Sorted Array 같은 Medium 문제를 다루고 있는 걸 보면 기본기는 있습니다. 문제는 **학습 전략**입니다.

---

### 1. 가장 먼저 바꿔야 할 것: "30분 룰"

지금 가장 큰 비효율은 **못 푸는 문제에 1-2시간을 쓰는 것**입니다.

[BaaaaarkingDog(바킹독)](https://blog.encrypted.gg/1062)의 조언이 정확합니다:

> **초보 단계에서 30분 고민해도 실마리가 안 잡히면, 그건 내 지식 범위에서 풀 수 없는 문제일 가능성이 크다.**

못 푸는 문제를 2시간 붙잡고 있는 건, 모르는 수학 공식 문제를 공식 없이 억지로 유도하려는 것과 같습니다. 시간 대비 학습 효과가 극히 낮습니다.

**규칙**: 20-30분 시도 → 실마리 없으면 → 해설 학습으로 전환

---

### 2. 마인드셋 전환: "시험"이 아니라 "수업"

지금 단계에서 문제 풀이는 **"내가 풀 수 있나 테스트"가 아니라 "패턴을 배우는 수업"**입니다.

수학 공부를 생각해보세요. 미적분을 처음 배울 때 교재의 예제를 먼저 보고, 풀이 과정을 이해한 다음, 비슷한 문제를 직접 풀어보잖아요. 알고리즘도 마찬가지입니다.

**해설을 보는 것은 부끄러운 게 아니라, 초보 단계에서 가장 효율적인 학습법입니다.**

---

### 3. 구체적인 학습 사이클 (문제당)

[코딩 테스트 4단계 공부법](https://brunch.co.kr/@jihyun-um/41)과 [스페이스드 리피티션 전략](https://www.redgreencode.com/leetcode-tip-10-planning-a-spaced-repetition-schedule/)을 종합하면:

```
[1] 문제 읽기 & 20-30분 시도
    ↓ (못 풀면)
[2] 해설/풀이 학습 (왜 이 접근법인지 이해)
    ↓
[3] 해설을 닫고 직접 구현 (보지 않고!)
    ↓
[4] 핵심 패턴 한 줄 메모
    예: "구간 합 최대 → Kadane's Algorithm"
    예: "괄호/중첩 구조 → Stack"
    ↓
[5] 3일 후 다시 풀기 (복습 1차)
    ↓
[6] 1주일 후 다시 풀기 (복습 2차)
```

**핵심**: [3]번이 가장 중요합니다. 해설을 읽고 "아~ 이해했다"로 끝내면 다음에 또 못 풉니다. **반드시 해설을 닫고 직접 코드를 작성**해야 합니다.

---

### 4. Grind 75 유형별 재구성

순서대로 푸는 대신, **유형별로 묶어서** 공부하세요. 한 유형을 5문제 이상 연속으로 풀면 패턴이 체화됩니다.

| 순서 | 유형                     | 왜 먼저?                       |
| ---- | ------------------------ | ------------------------------ |
| 1    | **Array + Two Pointers** | 가장 기본, 자신감 확보         |
| 2    | **Hash Map**             | 빈도 높고, 패턴 단순           |
| 3    | **Stack/Queue**          | 패턴이 명확해서 익히기 쉬움    |
| 4    | **Binary Search**        | 패턴 하나로 많은 문제 커버     |
| 5    | **Linked List**          | 포인터 조작 연습               |
| 6    | **Tree (DFS/BFS)**       | 재귀 사고력의 기반             |
| 7    | **Graph**                | Tree 확장, BFS/DFS 심화        |
| 8    | **Backtracking**         | 완전탐색의 핵심                |
| 9    | **Dynamic Programming**  | 가장 어렵지만, 패턴화 가능     |
| 10   | **Heap/Greedy**          | 특정 패턴에 특화               |

각 유형마다 Grind 75에서 해당 문제를 모아서 집중 학습하면, 무작위로 푸는 것보다 **패턴 인식 속도가 훨씬 빨라집니다**.

---

### 5. 현실적인 일정 제안

| Phase        | 기간  | 목표                                   | 하루 분량                  |
| ------------ | ----- | -------------------------------------- | -------------------------- |
| **패턴 수집** | 3-4주 | Grind 75 전체를 유형별로 1회독         | 2-3문제 (1-1.5시간)        |
| **패턴 강화** | 2-3주 | 약한 유형 추가 문제 + 복습             | 2문제 + 복습 1문제         |
| **실전 모의** | 2주+  | 유형 힌트 없이 랜덤, 시간 제한         | 2문제 (실전 시뮬레이션)    |

하루 1-1.5시간이면 됩니다. 지금처럼 한 문제에 2시간 쓰는 것보다, **짧게 여러 문제의 패턴을 학습하는 것이 훨씬 효율적**입니다.

---

### 6. 추가 팁

**한국 코테 특화 조언**:

- 한국 기업 코테는 [완전탐색이 50% 이상](https://littlemobs.com/blog/coding-test-algorithms-top-down-overview/)을 차지합니다. BFS/DFS/백트래킹에 집중 투자하세요.
- 카카오, 네이버 등은 [프로그래머스 기출](https://school.programmers.co.kr/learn/challenges?tab=algorithm_practice_kit)이 있으니 나중에 실전 모의 단계에서 활용하세요.

**동기 유지**:

- [zoomkoding님의 조언](https://zoomkoding.github.io/%ED%9A%8C%EA%B3%A0/2019/12/05/how-to-algo.html)처럼, "효율적인 공부보다 재밌는 공부"가 장기전에서 이깁니다.
- 혼자 하기 힘들면 스터디를 찾아서 "오늘은 DP 데이" 같은 주제별 학습을 함께 하는 것도 좋습니다.

**스페이스드 리피티션 도구**:

- [LeetSRS](https://leetsrs.com/)나 Anki 같은 도구로 복습 주기를 자동 관리하면 "풀었는데 까먹는" 문제를 방지할 수 있습니다.

---

### 정리

| 지금                 | 바꿀 것                            |
| -------------------- | ---------------------------------- |
| 한 문제에 1-2시간    | **20-30분 시도 → 해설 학습**       |
| 순서대로 풀기        | **유형별로 묶어서 풀기**           |
| 풀면 끝              | **3일 후, 1주일 후 복습**          |
| "못 풀면 실패"       | **"패턴을 배우는 과정"**           |

**가장 중요한 한 마디**: 못 푸는 게 당연한 단계입니다. 문제를 "풀어야 한다"는 압박을 버리고, "패턴을 수집한다"는 마음으로 접근하세요. 해설을 보고 이해하고 직접 구현하는 사이클을 빠르게 돌리면, 어느 순간 "아, 이 문제 이 패턴이네"하고 보이기 시작합니다.

---

Sources:

- [BaaaaarkingDog - 해설을 보는 시점에 대한 조언](https://blog.encrypted.gg/1062)
- [코딩 테스트 4단계 공부법](https://brunch.co.kr/@jihyun-um/41)
- [zoomkoding - 비효율적이지만 효율적인 알고리즘 공부법](https://zoomkoding.github.io/%ED%9A%8C%EA%B3%A0/2019/12/05/how-to-algo.html)
- [LeetCode Spaced Repetition 전략](https://www.redgreencode.com/leetcode-tip-10-planning-a-spaced-repetition-schedule/)
- [코딩테스트 문제 유형 정리 - 완전탐색 비중](https://littlemobs.com/blog/coding-test-algorithms-top-down-overview/)
- [Grind 75 공식 사이트](https://www.techinterviewhandbook.org/grind75/)
- [효율적인 코딩 테스트 준비 방법 - F-Lab](https://f-lab.kr/insight/efficient-coding-test-preparation-20240710)
- [프로그래머스 고득점 Kit](https://school.programmers.co.kr/learn/challenges?tab=algorithm_practice_kit)
