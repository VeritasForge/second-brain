---
tags: [gc, g1, zgc, jvm, python, garbage-collection]
created: 2026-04-15
---

# GC — Garbage Collection 전체

---

## 1. Python GC — Reference Counting + Cycle Detector

### 1.1 Reference Counting 동작

```python
x = User("Jay")    # User 객체 refcount = 1
y = x               # User 객체 refcount = 2
del x                # User 객체 refcount = 1
del y                # User 객체 refcount = 0 → 즉시 메모리 해제! ✅
```

### 1.2 순환 참조 문제

```python
a = Node()   # a의 refcount = 1
b = Node()   # b의 refcount = 1
a.next = b   # b의 refcount = 2
b.next = a   # a의 refcount = 2

del a        # a의 refcount = 2 → 1 (b.next가 여전히 참조)
del b        # b의 refcount = 2 → 1 (a.next가 여전히 참조)
```

```
프로그램에서 접근 불가능한데 refcount가 0이 안 됨!

     ┌──────────┐         ┌──────────┐
     │  Node a  │────────→│  Node b  │
     │ ref = 1  │←────────│ ref = 1  │
     └──────────┘         └──────────┘

→ 서로만 참조, refcount 영원히 1 = 메모리 누수! 💀
```

비유: **두 사람이 서로의 출입증을 들고 있으면, 둘 다 건물을 나갔는데도 출입증 회수가 안 되는 상황.**

### 1.3 Cycle Detector — 어떻게 찾나?

핵심: **"찾는" 게 아니라 "이미 등록되어 있음"**. Python은 컨테이너 객체 생성 시 **GC 추적 목록**에 등록해둠.

```
Step 0: 객체 생성 시 GC 추적 목록에 등록
        GC 추적 목록: [Node_a, Node_b, List_c, Dict_d, ...]
        ↑ Python이 만든 모든 컨테이너 객체가 여기 있음
        ↑ "참조할 변수가 없어도 GC가 이미 알고 있음"

Step 1: 각 객체의 refcount에서 "내부 참조"를 빼기
        Node_a: refcount 1 → 내부 참조 차감 → 임시 refcount = 0
        Node_b: refcount 1 → 내부 참조 차감 → 임시 refcount = 0

Step 2: 임시 refcount > 0 = 루트 (외부 참조 있음)
        임시 refcount = 0 = 쓰레기 후보

Step 3: 루트에서 도달 가능한 쓰레기 후보 → 살림
        도달 불가능한 쓰레기 후보 → 해제! 🗑️
```

비유: 학교 출석부(GC 추적 목록)가 있음. 친구끼리 "나 알아!"(내부 참조)를 제외하고, **선생님(루트)이 아는 학생만 남기는 것**.

---

## 2. JVM이 Reference Counting 대신 Tracing GC를 쓰는 이유

### 2.1 주된 이유: 순환 참조 처리 불가

RC 단독으로는 순환 참조를 감지할 수 없어 별도 cycle collector가 필요. 그러면 tracing GC 대비 장점이 사라짐.

### 2.2 부차적 이유: 멀티스레드 성능

```
Reference Counting + 멀티스레드:

Thread-1: obj.refcount++  ← 원자적 연산 필요!
Thread-2: obj.refcount--  ← 동시에 접근!
→ 모든 참조 변경마다 atomic operation 필요
→ CPU 캐시 라인 경쟁 (cache line bouncing)
```

```
Tracing GC + 멀티스레드:

Thread-1: obj 참조 → 그냥 포인터 대입 (atomic 불필요!)
Thread-2: obj 참조 → 그냥 포인터 대입
→ 참조 시 오버헤드 제로
```

| 항목                       | Reference Counting        | Tracing GC              |
| -------------------------- | ------------------------- | ----------------------- |
| 참조할 때마다              | atomic inc/dec 필요       | 포인터 대입만 (비용 0)  |
| 멀티스레드 확장성          | 나쁨 (캐시 경쟁)         | 좋음                    |
| Python이 쓸 수 있는 이유   | GIL이 동시 접근 차단      | -                       |

### 2.3 처리량 차이

```
Reference Counting:
  [앱코드+RC][앱코드+RC][앱코드+RC]  ← 매 순간 조금씩 느림

Tracing GC:
  [앱코드][앱코드][앱코드][====GC====][앱코드]  ← 가끔 멈추지만 평소는 빠름
```

---

## 3. Python vs JVM GC 비교

| 항목       | Python                         | JVM                         |
| ---------- | ------------------------------ | --------------------------- |
| 주력 GC    | Reference Counting (실시간)    | Tracing GC (주기적)         |
| STW 범위   | Cycle Detector만 (대상 적음)   | 전체 힙 대상 (수 GB 가능)   |
| 체감       | 일반적으로 미미                | 수십~수백 ms 가능           |

대용량 객체 그래프 Python에서는 cycle detection 체감 가능.

---

## 4. GC pause 실제 장애 사례

- **금융 서비스**: 수백ms STW → 타임아웃 → 결제 실패
- **LinkedIn** (2013): G1 Major GC 수 초 STW → 서비스 응답 불가
- **Discord** (2020): Go GC 수ms인데도 실시간 채팅 지연 → Rust로 전환

```
문제가 되는 경우:
  ✅ 금융 거래 (결제, 주문 체결) — 100ms 지연 = 타임아웃 = 돈 문제
  ✅ 실시간 시세/채팅 — ms 단위 지연이 UX에 직접 영향
  ✅ 대용량 힙 (16GB+) — G1 Major GC가 수백 ms~수 초

문제가 안 되는 경우:
  ❌ 일반 CRUD API — 200ms 응답에 20ms GC는 무의미
  ❌ 배치 처리 — 전체 실행 시간이 분 단위
  ❌ 작은 힙 (2GB 이하) — pause도 짧음
```

서비스 특성별 GC 선택 예시:

```
실시간 시세: GC pause 10ms = 지연 → ZGC 고려
주문 체결:   GC pause 100ms = 타임아웃 위험 → ZGC 고려
커뮤니티:    GC pause 50ms = 문제 없음 → G1 충분
```

---

## 5. G1 GC — "힙을 조각으로 나눠서 부분 청소"

### 5.1 세대별 영역

```
Eden (에덴동산) = 신생아실 👶  — 모든 객체가 여기서 태어남
Survivor       = 어린이집 🧒  — Eden에서 살아남은 객체
Old            = 양로원 👴    — 오래 살아남은 객체
Humongous      = 대형 창고 📦 — Region 하나에 안 들어가는 큰 객체
Free           = 빈 땅 🏗️
```

약한 세대 가설: API 요청 처리 후 95%는 Eden에서 사망.

### 5.2 Region 분할

힙을 바둑판처럼 같은 크기(1~32MB)로 약 2048개 Region으로 분할:

```
┌────┬────┬────┬────┬────┬────┬────┬────┐
│ E  │ E  │ S  │ O  │ O  │ E  │ H  │ F  │
├────┼────┼────┼────┼────┼────┼────┼────┤
│ O  │ F  │ E  │ O  │ F  │ S  │ O  │ F  │
├────┼────┼────┼────┼────┼────┼────┼────┤
│ F  │ O  │ O  │ E  │ F  │ O  │ F  │ E  │
└────┴────┴────┴────┴────┴────┴────┴────┘
```

이유: 부분 청소 + 멀티스레드 GC + 유연한 크기 조절. 논리적 목록으로 Eden만 쏙 찾아서 처리.

### 5.3 마킹 비트맵 vs Region 분할

별개 개념. Region = "어디를 청소"(방 나누기), 비트맵 = "누구를 살림"(스티커).

```
┌─────── Region 3 (Old) ──────┐
│ [객체A][객체B][객체C][객체D] │  ← 힙 메모리
│                              │
│ 마킹 비트맵: [1][0][1][0]    │  ← 별도 자료구조
│              A살아 B죽음 C살아 │
└──────────────────────────────┘
```

G1은 prev/next 두 개의 비트맵 사용.

### 5.4 Young GC (Minor) — STW 수 ms

```
[STW 시작] ─────────────────────── [STW 끝]

1. 모든 앱 스레드 멈춤
2. Eden Region만 스캔
3. 살아있는 객체를 Survivor로 복사
4. Eden을 Free로 변경
5. 재개

빠른 이유: Eden이 전체 힙의 일부 + 95% 이미 사망
```

### 5.5 Concurrent Marking

```
[Initial Mark] → [Concurrent Mark] → [Remark] → [Cleanup]
   STW 수ms        앱과 동시          STW 수ms    앱과 동시
```

### 5.6 Race Condition 해결 — SATB Write Barrier

```
앱이 참조 덮어쓸 때:

JVM 실제 실행:
  oldRef = obj.field          ← 기존 값 먼저 저장
  satbQueue.add(oldRef)       ← SATB 큐에 넣음
  obj.field = newRef
→ Remark에서 SATB 큐 확인하여 놓친 객체 보정
```

```
시퀀스:

앱 스레드                           GC 스레드
    │                                   │
    │                                   │ user 마킹 ✅
    │ user.address = newAddress         │
    │ → SATB: oldAddress를 큐에 저장    │
    │                                   │ ... marking 계속 ...
    │                                   │ [Remark STW]
    │                                   │ SATB 큐 확인
    │                                   │ oldAddress도 검사 ✅
```

Dirty card Write Barrier는 Mixed GC의 Remembered Set용으로 별개 메커니즘.

### 5.7 Mixed GC

Concurrent Marking이 각 Region의 쓰레기 비율을 계산 → 비율 순 정렬 → 시간 예산(200ms) 내 높은 순부터 청소. "Garbage First" 이름 유래.

```
Region 3 (Old): 쓰레기 80% ← 1순위!
Region 9 (Old): 쓰레기 70% ← 2순위
Region 4 (Old): 쓰레기 50%
Region 7 (Old): 쓰레기 10% ← 후순위
```

비유: 식당 잠깐 문 닫고 집중 청소. 깨끗, 근데 손님 대기.

---

## 6. ZGC — "거의 멈추지 않는 GC"

### 6.1 Colored Pointer — 세대가 아닌 GC 상태

```
64비트 포인터 (JDK 11-16):
┌──────────┬────────────────────────────────┐
│ 메타비트  │         실제 주소 (44비트)       │
│ [색상]   │                                │
└──────────┴────────────────────────────────┘

Remapped = "최신 주소" ✅
Marked0  = "이번 GC 사이클에서 살아있음 확인됨"
Marked1  = "다음 사이클용" (번갈아 사용)
```

G1 Region 태그 = 세대 구분. ZGC 색상 = GC 상태 (주소 최신 여부).

JDK 21 Generational ZGC에서 구조 변경. "포인터에 메타데이터 인코딩"이 핵심 개념.

### 6.2 G1 비트맵 vs ZGC 포인터

```
G1: 힙 [객체A][객체B]  + 비트맵 [1][0]  ← 별도 테이블
ZGC: 힙 [객체A(포인터에 색상)][객체B(포인터에 색상)]  ← 포인터 자체에 정보
```

### 6.3 0x1000→0x2000 = 메모리 압축 (세대 변화 아님)

```
이동 전: [ObjA][빈][ObjB][빈]  ← 단편화
이동 후: [ObjA][ObjB][~~~~큰 빈 공간~~~~]  ← 압축
```

### 6.4 Load Barrier

```java
// 개발자 코드
User user = obj.field;

// JVM 실제 실행
User user = obj.field;
if (user의_포인터_색상이_옛날_것이면) {   ← Load Barrier!
    user = forwarding_table에서_새_주소_조회();
    포인터_색상_업데이트(Remapped);
}
```

heap reference load 시만 발동. JIT이 불필요 barrier 제거 → throughput 1~5% 감소.

```
흐름:
포인터 읽음 → 색상 Remapped?
  ├─ YES → 그냥 사용 (비용 0)
  └─ NO → forwarding table → 새 주소 → 업데이트 → 접근
```

비유: G1 = 이사 시 우편물 멈추고(STW) 주소 변경. ZGC = 이사하면서 우편물 계속 받고 옛날 주소로 오면 전달(Load Barrier).

### 6.5 Write Barrier (G1) vs Load Barrier (ZGC)

| 항목         | G1 SATB Write Barrier          | ZGC Load Barrier                |
| ------------ | ------------------------------ | ------------------------------- |
| 발동 시점    | 참조를 **쓸 때**               | 참조를 **읽을 때**              |
| 목적         | 마킹 중 놓친 참조 보정         | 이동된 객체 주소 리다이렉트     |
| 오버헤드     | 쓰기 시 SATB 큐 추가           | 읽기 시 색상 확인               |

### 6.6 ZGC 전체 생애 vs G1

```
G1:  객체 → Eden → [Young GC STW] → Survivor → Old
     → [Concurrent Marking] → [Mixed GC STW]
     세대 명확, STW 중 이동

ZGC: 객체 → ZPage
     → [Concurrent Mark] 포인터에 Marked 색상
     → [Concurrent Relocate] 새 ZPage로 복사 + forwarding table
     → Load Barrier가 새 주소 리다이렉트
     → [Concurrent Remap] 남은 포인터 정리
     앱 안 멈추고 이동
```

JDK 21 Generational ZGC: Young/Old 추가, 핵심 메커니즘 동일.

### 6.7 ZGC vs Go GC

| 항목          | ZGC                                 | Go GC                                     |
| ------------- | ----------------------------------- | ----------------------------------------- |
| 방식          | Colored Pointers + Load Barrier     | Tri-color Marking + Write Barrier         |
| 객체 이동     | 앱과 동시에 이동 (compaction)       | 이동 안 함 (non-compacting)               |
| 단편화        | 없음                                | 있을 수 있음                              |
| 할당자        | -                                   | tcmalloc에서 영감받은 독자적 할당자       |
| STW           | sub-ms                              | sub-ms                                    |

---

## 7. GC 알고리즘 비교

| GC             | STW 시간         | 처리량      | 적합한 곳               | 만든 곳 |
| -------------- | ---------------- | ----------- | ----------------------- | ------- |
| **ZGC**        | < 1ms            | 약간 낮음   | 초저지연 (금융, 실시간) | Oracle  |
| **Shenandoah** | < 1ms            | 약간 낮음   | ZGC와 동급              | Red Hat |
| **G1**         | 수십 ms          | 높음        | 범용 (기본값)           | Oracle  |
| Parallel       | 수백 ms          | 최고        | 배치 처리               | Oracle  |
| Serial         | 가장 김          | -           | 소형 앱                 | Oracle  |

```
java -XX:+UseZGC -jar app.jar
java -XX:+UseG1GC -jar app.jar
java -XX:+UseShenandoahGC -jar app.jar
```

G1 vs ZGC: GC 빈도 trade-off가 아닌 **알고리즘 구조 차이** (STW 중 이동 vs concurrent 이동).

```
G1:  [앱][앱][STW GC 20ms][앱][앱]  → STW 동안 집중 → 처리량 높음
ZGC: [앱+GC 동시][앱+GC 동시]       → Load Barrier 오버헤드 → 처리량 약간 낮음

비유:
G1 = 식당 30분 문 닫고 집중 청소 → 깨끗, 손님 대기
ZGC = 영업하면서 청소 → 손님 안 기다림, 서빙 살짝 느림
```
