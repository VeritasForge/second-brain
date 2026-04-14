---
tags: [throttling, kill-switch, rate-limiting, graceful-degradation, blameless-rca]
created: 2026-04-14
---

# 🔧 Throttling, Kill Switch, Blameless RCA 가이드

---

## 1️⃣ 확률적 Rate Limiting (Probabilistic Throttling)

### 개요

이 패턴은 **"Probabilistic Load Shedding"** 또는 **"Random Early Drop"** 이라고 불린다. 네트워크의 RED (Random Early Detection) 알고리즘에서 영감을 받은 방식이다.

### 🏗️ 구현 방식 (Python 예제)

```python
import random
from functools import wraps

class ProbabilisticThrottler:
    """Feature Flag 기반 확률적 트래픽 제어"""
    
    def __init__(self, feature_flag_client):
        self.ff_client = feature_flag_client
    
    def should_accept(self, feature_key: str) -> bool:
        # Feature Flag에서 허용 비율을 가져옴 (0.0 ~ 1.0)
        accept_rate = self.ff_client.get_float(feature_key, default=1.0)
        
        # 난수를 생성하여 허용 비율과 비교
        return random.random() < accept_rate
    
    def throttle(self, feature_key: str):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.should_accept(feature_key):
                    # 503 Service Unavailable 또는 적절한 응답 반환
                    return {"status": 503, "message": "서비스 과부하, 잠시 후 재시도"}
                return func(*args, **kwargs)
            return wrapper
        return decorator

# 사용 예시
throttler = ProbabilisticThrottler(feature_flag_client)

@throttler.throttle("entry_api_accept_rate")  # Feature Flag에 0.3 설정 → 30%만 허용
def entry_point_api(request):
    return {"status": 200, "data": "정상 응답"}
```

### 📊 동작 원리 시각화

```
Feature Flag: accept_rate = 0.3 (30%)

요청 →  random() 생성  →  비교 판정
─────────────────────────────────────────────
Req 1 →  0.15          →  0.15 < 0.3  ✅ 허용
Req 2 →  0.82          →  0.82 < 0.3  ❌ 거부 (503)
Req 3 →  0.27          →  0.27 < 0.3  ✅ 허용
Req 4 →  0.91          →  0.91 < 0.3  ❌ 거부 (503)
Req 5 →  0.03          →  0.03 < 0.3  ✅ 허용
```

### 🔑 핵심 포인트

| 항목       | 설명                                                          |
| ---------- | ------------------------------------------------------------- |
| **장점**   | 구현이 매우 단순, 외부 저장소 불필요, 서버별 독립 동작         |
| **단점**   | 정확한 비율 보장 불가 (확률적이므로), 요청량 적을 때 편차 큼   |
| **적합한 상황** | 비상 시 트래픽 급감 필요, Entry Point에서 조기 차단          |
| **부적합한 상황** | 사용자별/API별 정밀한 Rate Limit 필요 시                   |

> 💡 **핵심**: 정밀한 Rate Limiting이 아닌, 장애 상황에서의 Load Shedding 목적. 서버별 상태 공유 없이 독립적으로 동작할 수 있는 것이 핵심 장점이다.

---

## 2️⃣ Token Bucket vs Sliding Window

### 📊 비교 표

| 구분             | Token Bucket                                                     | Sliding Window Log                                               | Sliding Window Counter                               |
| ---------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------- |
| **비유** 🧒      | 양동이에 물이 일정 속도로 차오름. 물 있으면 사용, 없으면 대기     | 모든 방문 기록이 있는 출석부. 현재 시점에서 1시간 전까지 세기     | 고정 창 2개를 겹쳐서 가중 평균으로 계산               |
| **메모리**       | O(1)                                                             | O(N) — 요청 로그 전부 저장                                       | O(1)                                                 |
| **정확도**       | 버스트 허용 (유연)                                               | 매우 정확                                                        | 근사치 (충분히 정확)                                  |
| **구현 복잡도**  | 낮음                                                             | 높음                                                             | 중간                                                 |
| **Redis 적합성** | ⭐⭐⭐                                                           | ⭐⭐ (sorted set)                                                 | ⭐⭐⭐                                                |

### 🪣 Token Bucket 동작 원리

```
용량(Capacity) = 5 tokens, 충전 속도(Refill Rate) = 1 token/sec

시간  │ 토큰 수 │ 요청  │ 결과
──────┼─────────┼───────┼──────────
0s    │ 5       │ Req1  │ ✅ 4 남음
0.1s  │ 4       │ Req2  │ ✅ 3 남음
0.2s  │ 3       │ Req3  │ ✅ 2 남음
0.3s  │ 2       │ Req4  │ ✅ 1 남음
0.4s  │ 1       │ Req5  │ ✅ 0 남음
0.5s  │ 0       │ Req6  │ ❌ 거부!
1.0s  │ 0.5→1   │ Req7  │ ✅ 충전되어 허용
```

```python
import time

class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity          # 최대 토큰 수
        self.refill_rate = refill_rate    # 초당 충전되는 토큰 수
        self.tokens = capacity
        self.last_refill = time.monotonic()
    
    def allow(self) -> bool:
        now = time.monotonic()
        # 경과 시간만큼 토큰 충전
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
```

### 📐 Sliding Window Counter 동작 원리

```
고정 창(Fixed Window) 크기 = 1분, Rate Limit = 100 req/min

  이전 창 (00:00~01:00)      현재 창 (01:00~02:00)
  ┌────────────────────┐    ┌──────────┬─────────┐
  │  총 84건 처리       │    │ 36건     │ ???     │
  └────────────────────┘    └──────────┘         │
                             ← 40초 경과 →        │
                                                  now (01:40)

  가중치 계산:
  이전 창 기여 = 84 × (1 - 40/60) = 84 × 0.33 = 28
  현재 창 기여 = 36
  추정 총량    = 28 + 36 = 64  ← 100 미만이므로 ✅ 허용
```

```python
import time
import math

class SlidingWindowCounter:
    def __init__(self, window_size: int, max_requests: int):
        self.window_size = window_size      # 윈도우 크기 (초)
        self.max_requests = max_requests
        self.prev_count = 0
        self.curr_count = 0
        self.curr_window_start = 0
    
    def allow(self) -> bool:
        now = time.monotonic()
        curr_window = math.floor(now / self.window_size)
        
        # 새 윈도우로 넘어갔으면 카운터 교체
        if curr_window != self.curr_window_start:
            self.prev_count = self.curr_count
            self.curr_count = 0
            self.curr_window_start = curr_window
        
        # 이전 창의 가중치 계산
        elapsed_ratio = (now % self.window_size) / self.window_size
        weighted_count = self.prev_count * (1 - elapsed_ratio) + self.curr_count
        
        if weighted_count < self.max_requests:
            self.curr_count += 1
            return True
        return False
```

### 🔄 Traffic Control 스펙트럼

```
┌─────────────────────────────────────────────────────┐
│              Traffic Control 스펙트럼                 │
│                                                      │
│  간단/비상용 ◄────────────────────────► 정밀/상시용   │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │확률적     │  │Token     │  │Sliding Window     │  │
│  │Load      │  │Bucket    │  │(Log / Counter)    │  │
│  │Shedding  │  │          │  │                   │  │
│  │          │  │          │  │                   │  │
│  │• 상태없음 │  │• 서버별   │  │• 사용자별/IP별     │  │
│  │• Feature │  │  로컬상태 │  │• Redis 등 공유저장 │  │
│  │  Flag    │  │• 버스트   │  │• 정확한 카운팅     │  │
│  │• 비상차단 │  │  허용    │  │• API Gateway      │  │
│  └──────────┘  └──────────┘  └───────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 3️⃣ Kill Switch & Graceful Degradation

### 💡 Graceful Degradation이란?

> 🧒 **비유**: 비행기 엔진 하나가 고장나도 나머지 엔진으로 착륙하는 것. 완벽하진 않지만, 추락(전체 장애)은 막는 것.

Graceful Degradation은 시스템 일부가 고장나도 핵심 기능은 유지하는 전략이다. 아래는 대표적인 패턴 예시:

### 📋 실무 패턴 매핑

| 실무 예시                                        | Graceful Degradation 패턴 | 분류              |
| ------------------------------------------------ | ------------------------- | ----------------- |
| POS 장애 시 → TTS(Text-To-Speech)로 주문 전달    | **Fallback 전략**         | Alternative Path  |
| 재고 서버 장애 시 → 재고 연동 생략, 주문 통과     | **Feature Degradation**   | Fail-Open         |

### 🔀 Kill Switch 동작 시퀀스 다이어그램

**Case 1: POS Fallback → TTS**

```
┌──────┐     ┌──────────┐     ┌───────────┐     ┌─────┐     ┌─────┐
│Client│     │API Server│     │Kill Switch │     │ POS │     │ TTS │
└──┬───┘     └────┬─────┘     └─────┬─────┘     └──┬──┘     └──┬──┘
   │   주문 요청   │                 │               │           │
   │──────────────>│  POS 상태 확인   │               │           │
   │               │────────────────>│               │           │
   │               │  ❌ POS OFF      │               │           │
   │               │<────────────────│               │           │
   │               │                 │               │           │
   │               │─── Fallback ────────────────────────────────>│
   │               │                 │               │     TTS로  │
   │               │                 │               │     주문전달│
   │               │<────────────────────────────────────── ✅ ───│
   │   주문 완료    │                 │               │           │
   │<──────────────│                 │               │           │
```

**Case 2: 재고 연동 Skip (Fail-Open)**

```
┌──────┐     ┌──────────┐     ┌───────────┐     ┌──────────┐
│Client│     │API Server│     │Kill Switch │     │재고 서버  │
└──┬───┘     └────┬─────┘     └─────┬─────┘     └────┬─────┘
   │   주문 요청   │                 │                 │
   │──────────────>│  재고연동 상태?   │                 │
   │               │────────────────>│                 │
   │               │  ❌ 재고연동 OFF  │                 │  💀 장애
   │               │<────────────────│                 │
   │               │                 │                 │
   │               │── 재고 확인 SKIP ──────── ✖ ──────│
   │               │── 주문 바로 생성 (Fail-Open) ──>  │
   │   주문 완료    │                 │                 │
   │<──────────────│                 │                 │
```

### 🎛️ Graceful Degradation 전략 분류

```
                    Graceful Degradation 전략
                    ┌───────────────┐
                    │               │
           ┌───────┴───────┐ ┌─────┴──────────┐
           │  Fail-Open    │ │  Fallback       │
           │  (기능 생략)   │ │  (대안 경로)     │
           └───────┬───────┘ └─────┬──────────┘
                   │               │
        ┌──────────┤        ┌──────┤
        │          │        │      │
   ┌────┴────┐ ┌───┴───┐ ┌─┴────┐ ┌────────┐
   │재고 연동 │ │추천   │ │POS→  │ │실시간→ │
   │ Skip    │ │엔진   │ │TTS   │ │배치    │
   │         │ │Skip   │ │      │ │처리    │
   └─────────┘ └───────┘ └──────┘ └────────┘
```

### ⚠️ Kill Switch 구현 시 핵심 고려사항

```python
# Kill Switch 구현 예시 (Python + Feature Flag)
class KillSwitchMiddleware:
    """서비스별 Kill Switch를 Feature Flag로 관리"""
    
    DEGRADATION_MAP = {
        "pos_service": {
            "fallback": "tts_service",           # Fallback 전략
            "strategy": "alternative_path",
        },
        "inventory_service": {
            "fallback": None,                     # Fail-Open
            "strategy": "skip",
            "log_level": "CRITICAL",              # 모니터링 강화
        },
    }
    
    def call_with_kill_switch(self, service_name: str, request_func, *args):
        config = self.DEGRADATION_MAP.get(service_name)
        
        # Kill Switch가 ON이면 (서비스 차단)
        if self.ff_client.is_enabled(f"kill_switch_{service_name}"):
            if config["strategy"] == "alternative_path":
                # Fallback 서비스 호출
                return self.call_fallback(config["fallback"], *args)
            elif config["strategy"] == "skip":
                # 해당 단계 건너뛰기 (Fail-Open)
                logger.critical(f"[KILL_SWITCH] {service_name} skipped")
                return None  # 또는 기본값
        
        # 정상 호출
        return request_func(*args)
```

---

## 4️⃣ Blameless RCA (Root Cause Analysis) 프레임워크

### 📝 Blameless RCA 5단계 프레임워크

```
┌─────────────────────────────────────────────────────────────┐
│                   Blameless RCA 프로세스                      │
│                                                              │
│  1️⃣ Timeline     →  분 단위로 사건 재구성                     │
│      Construction     "14:03 알람 발생 → 14:07 확인 → ..."    │
│                                                              │
│  2️⃣ 5 Whys       →  근본 원인까지 파고들기                    │
│      Analysis         "왜 감지 못했나? → 모니터링이 없었다      │
│                       → 왜 없었나? → 우선순위에서 밀렸다"       │
│                                                              │
│  3️⃣ Contributing →  사람 탓 ❌ → 시스템/프로세스 탓 ✅          │
│      Factors         "담당자가 실수" → "실수를 방지할              │
│                       가드레일이 없었다"                        │
│                                                              │
│  4️⃣ Action Items →  재발 방지책을 구체적으로                   │
│                      담당자 + 기한 + 측정 기준 포함              │
│                                                              │
│  5️⃣ Follow-up    →  Action Items 이행 추적                   │
│                      2주 후 리뷰, 유사 사례 자동 감지 구축       │
└─────────────────────────────────────────────────────────────┘
```

### 🎯 핵심 원칙

Blameless RCA의 일관된 원칙은 **'사람이 아닌 시스템을 고친다'**는 것이다. 예를 들어 '개발자가 배포 전 확인을 빼먹었다'는 원인을 '배포 파이프라인에 자동 검증 단계가 없었다'로 재정의하고, CI/CD (Continuous Integration / Continuous Delivery)에 자동 검증을 추가하는 것을 Action Item으로 도출한다.

---

## 5️⃣ Throttling vs Kill Switch 적용 기준

### 🔀 판단 흐름도

```
                    장애 감지!
                       │
                       ▼
              ┌─────────────────┐
              │ 서비스 완전 불능? │
              └────────┬────────┘
                 Yes   │   No
                 ┌─────┴─────┐
                 ▼           ▼
           ┌──────────┐ ┌───────────────┐
           │Kill Switch│ │ 응답 지연/     │
           │ 즉시 ON   │ │ 에러율 상승?   │
           └──────────┘ └───────┬───────┘
                          Yes   │   No
                          ┌─────┴─────┐
                          ▼           ▼
                    ┌──────────┐  정상 운영
                    │Throttling│
                    │ 적용     │
                    └──────────┘
                         │
                    ┌────┴────┐
                    ▼         ▼
              확률적        Token Bucket/
              Load          Sliding Window
              Shedding      (정밀 제어)
              (비상용)       (상시 보호)
```

> 💡 **핵심 한 줄**: Throttling은 **"트래픽을 줄여서 살리자"**, Kill Switch는 **"이 기능을 꺼서 나머지를 살리자"**. 목적이 다릅니다.
