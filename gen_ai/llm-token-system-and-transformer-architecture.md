---
created: 2026-02-02
source: claude-code
tags: [llm, token, api, transformer, flash-attention, gpu, rag]
---

# LLM API 토큰 시스템과 Transformer 연산 아키텍처

> LLM API를 호출할 때 주고받는 "토큰"이라는 단위가 무엇이고, 어떻게 과금되며, 서버 내부에서 어떤 비용을 발생시키는지를 네트워크 → GPU 메모리 → 연산 복잡도 → 최적화 기법까지 하나의 흐름으로 다룬다.

---

## 목차

```
Chapter 1. LLM API의 토큰 시스템
  1.1 토큰이란 무엇인가
  1.2 API 응답의 토큰 필드
  1.3 OpenAI vs Anthropic: 필드명이 다르다
  1.4 과금 구조

Chapter 2. Stateless API와 대화 히스토리 아키텍처
  2.1 API는 기억하지 않는다
  2.2 클라이언트가 히스토리를 관리한다
  2.3 대화가 길어지면 토큰이 "쌓이는" 이유
  2.4 Context Window와 200K 제한
  2.5 Auto-Compaction: 제한을 넘어서는 전략
  2.6 RAG는 왜 다른가

Chapter 3. 토큰의 물리적 크기와 시스템 병목
  3.1 토큰 → 바이트 변환
  3.2 언어별 토큰 효율 차이
  3.3 200K 토큰의 실제 크기
  3.4 네트워크 전송은 병목이 아니다
  3.5 진짜 병목: GPU 연산

Chapter 4. Transformer Self-Attention의 연산 비용
  4.1 Self-Attention이란
  4.2 O(n²) 복잡도의 의미
  4.3 실제 시간으로 체감하기

Chapter 5. FlashAttention — 메모리 병목의 해법
  5.1 GPU 메모리 계층 구조
  5.2 표준 Attention의 메모리 문제
  5.3 FlashAttention의 핵심: Tiling
  5.4 Online Softmax로 정확성 보장
  5.5 재계산(Recomputation)으로 역전파 해결
  5.6 결과: 연산량은 같지만 빠르다
  5.7 버전별 진화 (v1 → v2 → v3)

Chapter 6. 실무 시사점 — GenerationResult 클래스 설계
  6.1 API별 필드 매핑
  6.2 CLI 환경에서의 토큰 추적
  6.3 설계 권장사항

부록. 출처 및 참고 문헌
```

---

## Chapter 1. LLM API의 토큰 시스템

### 1.1 토큰이란 무엇인가

LLM은 텍스트를 직접 처리하지 않는다. 먼저 텍스트를 **토큰(token)** 이라는 단위로 변환(토크나이징)한 후, 토큰 시퀀스를 모델에 입력한다. 토큰은 단어 하나일 수도 있고, 단어의 일부(subword)이거나, 하나의 문자일 수도 있다.

```
영어:  "Hello, how are you?"
       → ["Hello", ",", " how", " are", " you", "?"]
       → 6 tokens

한국어: "안녕하세요, 어떻게 지내세요?"
        → ["안녕", "하", "세요", ",", " 어", "떻", "게", " 지", "내", "세요", "?"]
        → 11 tokens (같은 의미인데 토큰이 더 많음)
```

토큰은 LLM 세계의 화폐 단위이다. 입력도 토큰으로 측정하고, 출력도 토큰으로 측정하며, 비용도 토큰 단위로 청구된다.

### 1.2 API 응답의 토큰 필드

ChatGPT나 Claude의 API를 호출하면, 응답 본문에 `usage` 객체가 포함되어 해당 요청에서 소비된 토큰 수를 알려준다.

```
┌─────────────────────────────────────────────────────────┐
│                  하나의 API 요청/응답                      │
│                                                         │
│  ┌──── input tokens ───────┐  ┌── output tokens ───┐   │
│  │ system prompt           │  │ AI가 생성한 답변     │   │
│  │ + context (검색 결과 등) │  │                     │   │
│  │ + 대화 히스토리          │  │                     │   │
│  │ + 현재 질문             │  │                     │   │
│  └─────────────────────────┘  └─────────────────────┘   │
│                                                         │
│  total = input tokens + output tokens                   │
└─────────────────────────────────────────────────────────┘
```

| 필드 | 의미 | 비유 |
|------|------|------|
| **input tokens** | 사용자가 보낸 모든 입력의 크기 | 편지에 쓴 글자 수 |
| **output tokens** | AI가 생성한 응답의 크기 | 답장의 글자 수 |
| **total tokens** | 합계 | 전체 우편 무게 |

input tokens에는 눈에 보이지 않는 것들도 포함된다. system prompt, 도구 정의(tool definitions), 대화 히스토리 전체가 모두 input tokens에 합산된다. 또한 API 제공자가 내부 최적화를 위해 자동으로 추가하는 토큰이 있을 수 있으며, 이 때문에 실제 보낸 텍스트의 토큰 수와 usage에 보고되는 토큰 수가 정확히 일치하지 않을 수 있다. 다만, 자동 추가된 토큰에 대해서는 과금되지 않는다.

### 1.3 OpenAI vs Anthropic: 필드명이 다르다

같은 개념이지만, 두 API의 필드명이 다르다. 이것은 실제 코드를 작성할 때 반드시 인지해야 하는 차이다.

**OpenAI API 응답 (`/v1/chat/completions`)**

```json
{
  "usage": {
    "prompt_tokens": 13,
    "completion_tokens": 7,
    "total_tokens": 20
  }
}
```

**Anthropic Claude API 응답 (`/v1/messages`)**

```json
{
  "usage": {
    "input_tokens": 12,
    "output_tokens": 6,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 0
  }
}
```

두 API의 차이를 정리하면:

```
┌──────────────────────┬─────────────────────┬──────────────────────┐
│       개념           │    OpenAI           │    Anthropic (Claude) │
├──────────────────────┼─────────────────────┼──────────────────────┤
│ 입력 토큰            │ prompt_tokens       │ input_tokens          │
│ 출력 토큰            │ completion_tokens   │ output_tokens         │
│ 합계                 │ total_tokens        │ (필드 없음 — 직접 계산)│
│ 캐시 관련            │ cached_tokens       │ cache_creation_input  │
│                      │ (details 하위)      │ cache_read_input      │
└──────────────────────┴─────────────────────┴──────────────────────┘
```

주목할 점:
- Anthropic API에는 `total_tokens` 필드가 **존재하지 않는다**. 필요하면 클라이언트가 직접 더해야 한다.
- Anthropic은 prompt caching 관련 필드(`cache_creation_input_tokens`, `cache_read_input_tokens`)를 별도로 제공한다.
- Anthropic은 OpenAI SDK 호환 레이어를 제공하며, 이를 사용하면 `prompt_tokens`/`completion_tokens` 형식으로 변환된 응답을 받을 수 있다. 다만 이 호환 레이어는 테스트 및 비교 목적이며, 프로덕션용으로 권장되지는 않는다.
- OpenAI의 새로운 **Responses API**(`/v1/responses`)는 `input_tokens`/`output_tokens`/`total_tokens`를 사용하며, 위 표는 기존 Chat Completions API(`/v1/chat/completions`) 기준이다.
- LiteLLM 같은 통합 라이브러리를 사용하면 이 필드명 차이를 자동으로 변환해준다.

### 1.4 과금 구조

토큰은 곧 돈이다. API 과금은 토큰 수를 기준으로 이루어지며, 입력과 출력의 단가가 다르다.

**Anthropic Claude 모델별 가격 (2026년 기준, 1M 토큰당)**

```
┌──────────────────┬────────────┬─────────────┬───────────────────┐
│ 모델              │ 입력 단가  │ 출력 단가    │ 출력/입력 비율     │
├──────────────────┼────────────┼─────────────┼───────────────────┤
│ Haiku 4.5        │ $1.00      │ $5.00       │ 5배               │
│ Sonnet 4 / 4.5   │ $3.00      │ $15.00      │ 5배               │
│ Opus 4.5         │ $5.00      │ $25.00      │ 5배               │
└──────────────────┴────────────┴─────────────┴───────────────────┘

추가 요금 조건:
- 200K 초과 입력 (Long Context): 입력 $6, 출력 $22.50 (Sonnet 기준)
- Batch API: 50% 할인 (24시간 내 비동기 처리)
- Prompt Caching: 캐시 쓰기 1.25× (5분 TTL) 또는 2.0× (1시간 TTL), 캐시 읽기 0.1× (90% 절감)
- Extended Thinking: thinking 토큰은 output 가격으로 과금
```

출력이 입력보다 **5배 비싼** 배경에는 기술적 이유가 있다. 입력(prefill)은 모든 토큰을 한 번의 forward pass로 병렬 처리할 수 있지만, 출력(decode)은 토큰 하나마다 별도의 forward pass가 필요한 자기회귀(autoregressive) 특성을 갖는다. 이로 인해 출력 생성은 메모리 대역폭 측면에서 훨씬 비효율적이다. 다만, 정확히 5배라는 비율 자체는 Anthropic의 가격 정책에 의한 것이며, 다른 제공사는 다른 비율을 적용한다 (예: OpenAI GPT-4 Turbo는 약 3:1).

---

## Chapter 2. Stateless API와 대화 히스토리 아키텍처

### 2.1 API는 기억하지 않는다

LLM API의 가장 중요한 아키텍처적 특성은 **stateless**라는 것이다. 서버는 이전 대화를 기억하지 않는다. 매 요청은 완전히 독립적인 새로운 요청으로 취급된다.

```
┌─────────────────────────────────────────────────────┐
│              API 서버 (Stateless)                     │
│                                                     │
│   "나는 기억을 못하는 의사.                            │
│    환자가 매번 전체 진료기록을 가져오면                  │
│    처음부터 읽고 진료함."                              │
│                                                     │
│   - 세션 없음                                        │
│   - 이전 요청 기록 없음                               │
│   - 매번 새로운 독립 요청                             │
└───────────────────────┬─────────────────────────────┘
                        │
         매 요청마다 전체 대화 히스토리를 보냄
                        │
┌───────────────────────┴─────────────────────────────┐
│              클라이언트 (대화 관리)                    │
│   Claude Code, ChatGPT 웹, RAG 앱 등                │
│                                                     │
│   - messages 배열을 유지                             │
│   - 매 요청에 전체 히스토리 포함                      │
│   - 토큰 누적 관리 책임                              │
└─────────────────────────────────────────────────────┘
```

이 설계가 채택된 이유는 명확하다. Stateless 아키텍처는 서버를 단순하게 만들고, 수평 확장(scale-out)을 용이하게 하며, 어떤 서버 인스턴스가 요청을 처리하든 동일한 결과를 보장한다. 수백만 명의 동시 사용자 세션 상태를 서버에서 관리하는 것은 엄청난 메모리와 복잡성을 요구하므로, 이를 클라이언트에 위임한 것이다.

### 2.2 클라이언트가 히스토리를 관리한다

"대화"라는 것은 사실 클라이언트가 만들어내는 환상이다. 서버 입장에서는 매번 새로운 독립 요청일 뿐이다. 대화의 연속성을 만드는 것은 클라이언트가 `messages` 배열에 이전 대화를 모두 담아서 보내기 때문이다.

실제 API 호출의 `messages` 배열은 다음과 같은 형태다:

```json
{
  "model": "claude-sonnet-4-20250514",
  "messages": [
    {"role": "user",      "content": "안녕하세요"},
    {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"},
    {"role": "user",      "content": "파이썬 질문이 있어요"},
    {"role": "assistant", "content": "네, 말씀해주세요."},
    {"role": "user",      "content": "리스트 정렬은 어떻게 하나요?"}
  ]
}
```

5번째 턴에서 사용자가 "리스트 정렬은 어떻게 하나요?"라고만 물었지만, 클라이언트는 **1~4번째 턴의 모든 대화를 함께 보낸다**. 서버는 이 전체 messages 배열을 처음부터 읽고 맥락을 파악한 후 응답을 생성한다.

### 2.3 대화가 길어지면 토큰이 "쌓이는" 이유

이 구조의 직접적인 결과로, 대화가 진행될수록 매 요청의 입력 토큰 수가 증가한다.

```
1번째 턴:
  클라이언트 → 서버: [질문1]
  prompt tokens: ~10

2번째 턴:
  클라이언트 → 서버: [질문1, 응답1, 질문2]
  prompt tokens: ~300
                     ^^^^^^^^^^^^^^
                     이전 대화를 전부 다시 보냄

3번째 턴:
  클라이언트 → 서버: [질문1, 응답1, 질문2, 응답2, 질문3]
  prompt tokens: ~800
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                     계속 누적

  ...

50번째 턴:
  클라이언트 → 서버: [전체 히스토리 1~49턴 + 질문50]
  prompt tokens: ~195,000
                           ← 200K context window에 근접!
```

서버 입장에서는 매번 새로운 독립 요청이다. "토큰이 쌓인다"는 표현은 정확히 말하면, **클라이언트가 보내는 messages 배열이 점점 길어지는 것**이지, 서버에 상태가 축적되는 것이 아니다.

과금 관점에서 이것은 중요한 의미를 가진다. 50번째 턴에서 서버에 195,000개의 input tokens를 보내면, 그 195,000개 전체에 대해 입력 비용이 청구된다. 이전 턴들에서 이미 보냈던 토큰이라도 다시 보내면 다시 과금된다. 대화가 길어질수록 비용이 **가속적으로** 증가하는 구조다.

### 2.4 Context Window와 200K 제한

모든 LLM에는 **context window**라는 처리 한계가 있다. 이것은 모델이 한 번의 요청에서 처리할 수 있는 최대 토큰 수를 의미하며, 입력 토큰과 출력 토큰을 합산한 값이다.

```
┌────────────────────────────────────────────────────────────┐
│                  Context Window (200K)                      │
│                                                            │
│  ┌─────────────────────────────┬──────────────────────┐   │
│  │     Input Tokens            │   Output Tokens      │   │
│  │  (system prompt             │  (AI가 생성할 응답)   │   │
│  │   + 대화 히스토리            │                      │   │
│  │   + 현재 질문               │                      │   │
│  │   + 도구 정의               │                      │   │
│  │   + CLAUDE.md 등)           │                      │   │
│  └─────────────────────────────┴──────────────────────┘   │
│  ◄──────────── 합쳐서 200K 이하여야 함 ──────────────────▶ │
└────────────────────────────────────────────────────────────┘
```

Context window에 포함되는 것은 사용자가 명시적으로 작성한 텍스트만이 아니다. System prompt, CLAUDE.md 같은 설정 파일, 도구 정의, extended thinking의 현재 턴 사고 과정 등이 모두 합산된다. 다만, **이전 턴의 extended thinking 블록은 자동으로 제거**되어 공간을 절약한다.

모델별 context window 크기:

```
┌──────────────────────┬────────────────────┐
│ 모델                  │ Context Window     │
├──────────────────────┼────────────────────┤
│ Claude (일반)         │ 200K tokens        │
│ Claude (Enterprise)   │ 500K tokens        │
│ Claude (Beta, 일부)   │ 1M tokens          │
│ GPT-4o               │ 128K tokens        │
│ Gemini 1.5 Pro       │ 2M tokens          │
└──────────────────────┴────────────────────┘
```

### 2.5 Auto-Compaction: 제한을 넘어서는 전략

200K 토큰 한도에 도달하면 대화가 완전히 끊기는 것은 아니다. 현대의 LLM 클라이언트들은 **자동 요약(auto-compaction)** 메커니즘을 구현하고 있다.

```
대화가 200K에 접근하면:

  ┌──────────────────────────────┐
  │  클라이언트 감지              │
  │  "context window 부족"       │
  └────────┬─────────────────────┘
           │
           ▼
  ┌──────────────────────────────┐
  │  Auto-Compaction 실행        │  ← "생각 정리 중..." 메시지 표시
  │                              │
  │  이전 대화 50턴 분량을        │
  │  핵심 요약 3,000 토큰으로 압축│
  │                              │
  │  Before: [턴1][턴2]...[턴50] │  ← 195,000 tokens
  │  After:  [요약][턴48~50]     │  ← 10,000 tokens
  └────────┬─────────────────────┘
           │
           ▼
  ┌──────────────────────────────┐
  │  대화 계속 가능               │
  │  (요약 기반, 세부 사항 손실)  │
  └──────────────────────────────┘
```

Claude Code에서는 `/compact` 명령으로 수동 요약도 가능하다. 요약 시점에 따라 이전 대화의 세부 사항이 손실될 수 있으므로, auto-compaction이 작동하기 전에 전략적 시점에서 수동으로 compact를 실행하는 것이 좋다 (auto-compaction은 context window의 약 64~95% 시점에서 작동한다). 또한 Claude Sonnet 4.5와 Haiku 4.5는 **context awareness** 기능이 내장되어, 남은 context window 크기를 모델 자체가 인식하고 작업을 조절할 수 있다.

비유하자면, "기억을 못하는 의사"보다는 **"노트 정리를 잘하는 의사"**에 가깝다. 진료기록이 너무 많아지면 간호사가 핵심만 정리한 요약본을 만들어주고, 의사는 요약본과 최근 기록을 보고 진료를 계속한다. 대신 옛날 세부 사항은 잊어버릴 수 있다.

### 2.6 RAG는 왜 다른가

RAG(Retrieval-Augmented Generation) 시스템은 대화형 AI와 근본적으로 다른 토큰 패턴을 보인다.

```
┌─────────────────────────────────────────────────────────────┐
│              대화형 AI (ChatGPT, Claude Code)                │
│                                                             │
│  턴 1:  [Q1]                          → 10 tokens          │
│  턴 2:  [Q1, A1, Q2]                  → 300 tokens         │
│  턴 3:  [Q1, A1, Q2, A2, Q3]          → 800 tokens         │
│  ...                                                        │
│  턴 50: [전체 히스토리...]              → 195,000 tokens     │
│                                                             │
│  → 토큰이 턴마다 누적됨                                     │
│  → context window 한도에 도달 가능                           │
├─────────────────────────────────────────────────────────────┤
│              RAG 시스템 (1회성 질의응답)                      │
│                                                             │
│  질문 1: [system + context_1 + Q1]     → 2,000 tokens      │
│  질문 2: [system + context_2 + Q2]     → 2,200 tokens      │
│  질문 3: [system + context_3 + Q3]     → 1,800 tokens      │
│                                                             │
│  → 매번 독립적인 요청                                       │
│  → 대화 히스토리 없음                                       │
│  → 토큰 "누적" 없음                                        │
│  → context window 걱정 없음                                 │
└─────────────────────────────────────────────────────────────┘
```

RAG에서 `system_prompt + retrieved_context + question`의 크기는 매 질문마다 대체로 비슷한 범위에 머무른다. 이전 질문의 응답을 다음 질문에 포함시키지 않기 때문이다. Claude Code의 `claude -p` (단일 프롬프트 모드)도 동일한 패턴이다.

이 차이는 비용 예측에도 영향을 준다. 대화형 AI는 대화가 길어질수록 턴당 비용이 가속 증가하지만, RAG는 질문 수에 비례하는 선형 비용 구조를 갖는다.

---

## Chapter 3. 토큰의 물리적 크기와 시스템 병목

Chapter 2에서 "클라이언트가 매번 전체 히스토리를 서버에 보낸다"는 사실을 확인했다. 그렇다면 자연스러운 질문이 따라온다: 200K 토큰이면 실제로 얼마나 되는 데이터인가? 서버로 보내는 것이 네트워크에 부담이 되지 않는가?

### 3.1 토큰 → 바이트 변환

토큰의 물리적 크기는 언어에 따라 크게 달라진다. BPE(Byte Pair Encoding) 기반 토크나이저는 훈련 데이터에서 자주 등장하는 문자열 패턴을 하나의 토큰으로 묶는데, 영어는 인터넷 텍스트의 대다수를 차지하므로 토크나이저가 영어에 최적화되어 있다.

```
영어:   1 token ≈ 4 characters ≈ 4 bytes (UTF-8, ASCII 범위)
        "hello" → 1 token, 5 bytes

한국어: 1 token ≈ 1 한글 음절 ≈ 3 bytes (UTF-8에서 한글은 3바이트)
        "안녕하세요" → 약 3~5 tokens, 15 bytes
```

한국어가 토큰 효율이 낮은 이유는 구조적이다. 대부분의 LLM 토크나이저는 영어 중심으로 훈련되어, 한글 음절을 효율적으로 병합하지 못한다. 같은 의미를 전달하는 데 한국어는 영어 대비 약 **2.36배** 더 많은 토큰을 소모한다는 분석이 있다. 이는 한국어 사용 시 API 비용이 그만큼 높아진다는 것을 의미한다.

### 3.2 언어별 토큰 효율 차이

```
┌───────────┬──────────────────┬──────────────────┬────────────────┐
│ 언어      │ 1 토큰당 문자 수  │ 1 토큰당 바이트   │ 비용 효율      │
├───────────┼──────────────────┼──────────────────┼────────────────┤
│ 영어      │ ~3-4 chars       │ ~4 bytes         │ 기준 (1x)      │
│ 한국어    │ ~1 char (음절)   │ ~3 bytes         │ ~2.36x 비쌈    │
│ 일본어    │ ~1 char          │ ~3 bytes         │ ~2x+ 비쌈      │
│ 중국어    │ ~1 char          │ ~3 bytes         │ ~2x+ 비쌈      │
│ 프랑스어  │ ~3 chars         │ ~3-4 bytes       │ ~1.5x 비쌈     │
└───────────┴──────────────────┴──────────────────┴────────────────┘
```

CJK(Chinese, Japanese, Korean) 언어군은 토큰당 거의 1:1로 음절/문자에 매핑된다. **같은 의미를 전달하는 데 필요한 토큰 수** 기준으로는 중국어 약 1.76배, 일본어 약 2배, 한국어 약 2.36배 수준이다. 다만 **문자당 토큰 효율**(하나의 토큰이 인코딩하는 바이트 수)로 비교하면 영어 대비 4~5배 비효율적이라는 분석도 있는데, 이는 의미 기준 비용과 혼동하지 않아야 한다. 이 격차는 LLM 토크나이저가 영어 중심 훈련 데이터로 만들어졌기 때문이며, 향후 다국어 토크나이저의 개선으로 줄어들 수 있다.

### 3.3 200K 토큰의 실제 크기

이제 200K 토큰을 실제 바이트로 환산해보자.

```
┌──────────┬───────────────┬────────────────┬──────────────────┐
│ 언어     │ 200K 토큰     │ 대략 글자 수    │ 바이트 크기      │
├──────────┼───────────────┼────────────────┼──────────────────┤
│ 영어     │ 200,000 tok   │ ~800,000 자    │ ~800 KB          │
│ 한국어   │ 200,000 tok   │ ~200,000 자    │ ~600 KB          │
│ 혼합     │ 200,000 tok   │ -              │ ~700 KB          │
├──────────┼───────────────┼────────────────┼──────────────────┤
│ JSON 오버헤드 포함 (messages 배열, role, metadata 등)          │
│ 실제 HTTP 요청 크기:  약 800 KB ~ 1.5 MB                     │
└───────────────────────────────────────────────────────────────┘
```

200K 토큰의 영어 텍스트는 약 **15만 단어**, A4 용지로 약 **300장** 분량이다. 소설 한 권이 대략 7~10만 단어이므로, 200K 토큰은 소설 약 1.5~2권 분량의 텍스트에 해당한다.

### 3.4 네트워크 전송은 병목이 아니다

1~1.5MB의 HTTP 요청은 현대 네트워크에서 전혀 부담이 되지 않는다.

```
┌──────────────────────────────────────────────────────────┐
│              일상적인 데이터 크기 비교                       │
│                                                          │
│  200K 토큰 API 요청   ██                        ~1 MB    │
│  일반 웹 페이지       ██████████                ~3 MB    │
│  고해상도 사진 1장    ████████████████          ~8 MB    │
│  유튜브 1분 영상      ████████████████████████  ~15 MB   │
│  넷플릭스 1분 (HD)    ████████████████████████████ ~40MB │
│                                                          │
│  100Mbps 네트워크에서 1MB 전송 = 약 0.08초                │
│  → 네트워크는 병목이 아니다                                │
└──────────────────────────────────────────────────────────┘
```

웹 페이지 하나를 로딩할 때 이미지, CSS, JavaScript를 포함하면 3~5MB가 일반적이다. 고화질 사진 한 장은 5~10MB다. 200K 토큰의 API 요청(~1MB)은 사진 한 장보다 가벼운 수준이다.

### 3.5 진짜 병목: GPU 연산

네트워크 전송이 병목이 아니라면, 200K 토큰 요청에서 실제로 시간이 소요되는 곳은 어디인가? 답은 **서버의 GPU 연산**이다.

```
┌────────────────────────────────────────────────────────────┐
│  200K 토큰 요청의 시간 분해                                  │
│                                                            │
│  [네트워크 전송]  ██                          ~0.1초        │
│  [Prefill 연산]  ██████████████████████████   ~10-30초     │
│  [응답 생성]     ████████████████             (토큰당)      │
│                                                            │
│  Prefill = 서버가 200K 입력 토큰 전체를 "읽는" 단계          │
│  → Transformer의 self-attention 연산이 발생                 │
│  → 이 단계에서 O(n²) 연산 비용이 지배적                     │
│  → "첫 글자가 나오기까지" 기다리는 시간 = TTFT              │
│                                                            │
│  TTFT = Time To First Token                                │
└────────────────────────────────────────────────────────────┘
```

비유하자면, **택배 상자를 배달하는 건 가벼운데(네트워크), 상자 안의 퍼즐을 맞추는 게 무거운 것(GPU 연산)**이다. 그래서 Anthropic이나 OpenAI의 비용 구조에서 네트워크 인프라는 부차적이고, **GPU 클러스터 비용**이 압도적이다.

이 관점에서 보면, 대화가 길어질수록 응답이 느려지는 현상도 설명된다. 50번째 턴에서 195K 토큰을 보내면, 서버는 195K 토큰 전체에 대해 self-attention 연산을 수행해야 하며, 이 비용은 토큰 수의 제곱에 비례한다.

이제 이 "O(n²) 연산"이 정확히 무엇인지, 왜 제곱으로 증가하는지를 살펴보자.

---

## Chapter 4. Transformer Self-Attention의 연산 비용

### 4.1 Self-Attention이란

Transformer 모델의 핵심은 self-attention 메커니즘이다. 이것은 입력 시퀀스의 **모든 토큰이 다른 모든 토큰과의 관계**를 계산하는 과정이다.

"나는 은행에 갔다"라는 문장에서 "은행"이 금융기관인지 강가의 둑인지를 판단하려면, "은행"이라는 토큰이 문장 내 다른 토큰들("나는", "갔다")과의 관계를 봐야 한다. Self-attention은 이 관계를 수학적으로 계산한다.

수식으로 표현하면:

```
Attention(Q, K, V) = softmax(Q × Kᵀ / √d) × V

여기서:
  Q (Query)  = "내가 찾고 있는 정보" 행렬  [N × d]
  K (Key)    = "내가 제공하는 정보" 행렬    [N × d]
  V (Value)  = "실제 전달할 정보" 행렬      [N × d]
  N          = 토큰 수 (시퀀스 길이)
  d          = 임베딩 차원 (보통 64~128)
```

Q × Kᵀ 의 결과는 **[N × N] 크기의 행렬**이다. 이것이 바로 "모든 토큰 쌍의 관련도 점수"를 담고 있다. 이 행렬의 크기가 토큰 수의 제곱에 비례하는 것이 O(n²) 복잡도의 근원이다.

### 4.2 O(n²) 복잡도의 의미

N개의 토큰이 있으면, 모든 토큰 쌍의 관계를 계산해야 하므로 N × N 번의 연산이 필요하다.

```
┌─────────────────────────────────────────────────────────────┐
│        Self-Attention: O(n²) 복잡도                          │
│                                                             │
│  토큰 수      N×N 연산량       상대값       비유             │
│  ─────────────────────────────────────────────               │
│  1K           1,000,000        1x          퍼즐 1개         │
│  10K          100,000,000      100x        퍼즐 100개       │
│  100K         10,000,000,000   10,000x     퍼즐 1만개       │
│  200K         40,000,000,000   40,000x     퍼즐 4만개       │
│                                                             │
│  토큰이 2배 → 연산은 4배 (제곱으로 증가)                     │
│  토큰이 10배 → 연산은 100배                                  │
│  토큰이 200배 → 연산은 40,000배                              │
└─────────────────────────────────────────────────────────────┘
```

더 정확하게는, self-attention의 연산 복잡도는 O(N²d)이다. 여기서 d는 head 차원이다. Multi-head attention에서 h개의 head를 사용하면 각 head가 d/h 차원을 처리하지만, 총합은 다시 O(N²d)가 된다. N이 d보다 훨씬 큰 long context 시나리오에서는 N² 항이 지배적이 되어, 연산 비용은 사실상 시퀀스 길이의 제곱에 비례한다.

비유하자면:

> 교실에 학생 5명이 있으면 서로 악수하는 횟수는 10번이다. (쉬움)
> 교실에 학생 50명이 있으면 악수 횟수는 1,225번이다. (좀 바쁨)
> 교실에 학생 200,000명이 있으면 악수 횟수는 약 **200억 번**이다. (불가능에 가까움)
>
> 이것이 "모든 토큰이 다른 모든 토큰을 본다"는 self-attention의 비용이다.

### 4.3 메모리 비용: N×N 행렬의 크기

연산 복잡도뿐 아니라, N×N 행렬을 메모리에 저장하는 것 자체가 문제다.

```
┌────────────────────────────────────────────────────────────┐
│  N×N Attention 행렬의 메모리 크기 (FP16 기준, 2 bytes)     │
│                                                            │
│  1K 토큰:    1K × 1K × 2 bytes   = 2 MB        (가벼움)   │
│  10K 토큰:   10K × 10K × 2 bytes = 200 MB      (관리 가능)│
│  100K 토큰:  100K × 100K × 2     = 18.6 GB     (GPU 1대) │
│  200K 토큰:  200K × 200K × 2     = 74.5 GB     (A100 한계)│
│  1M 토큰:    1M × 1M × 2         = ~1.82 TiB    (불가능!)  │
│                                                            │
│  ※ 이것은 attention 행렬 하나의 크기이며, 실제로는          │
│    multi-head × multi-layer로 더 많은 메모리가 필요         │
└────────────────────────────────────────────────────────────┘
```

A100 GPU의 HBM이 80GB인데, 200K 토큰의 attention 행렬 하나만으로 74.5GB를 차지한다. 여기에 모델 파라미터, KV cache, 중간 활성화값 등을 더하면 단일 GPU로는 처리가 불가능하다. Gemini의 2M 토큰 context window나 Claude의 200K 토큰이 naive한 구현으로는 물리적으로 불가능한 이유가 여기에 있다.

이 문제를 해결하기 위해 등장한 것이 FlashAttention이다.

---

## Chapter 5. FlashAttention — 메모리 병목의 해법

### 5.1 GPU 메모리 계층 구조

FlashAttention을 이해하려면 먼저 GPU 내부의 메모리 구조를 알아야 한다. GPU에는 속도와 용량이 다른 두 종류의 메모리가 있다.

```
┌──────────────────────────────────────────────────────────────┐
│                        GPU (예: A100)                         │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  HBM (High Bandwidth Memory) = "창고"                │    │
│  │                                                     │    │
│  │  용량: 40~80 GB       (넓음)                         │    │
│  │  속도: 1.5~2.0 TB/s   (상대적으로 느림)               │    │
│  │                                                     │    │
│  │  역할: 모델 파라미터, 입력 데이터, 중간 결과 저장      │    │
│  └────────────────────────┬────────────────────────────┘    │
│                           │                                  │
│                    데이터 이동 (이것이 병목!)                  │
│                           │                                  │
│  ┌────────────────────────▼────────────────────────────┐    │
│  │  SRAM (On-chip) = "작업대"                           │    │
│  │                                                     │    │
│  │  용량: ~17 MB          (매우 좁음, 108 SM × 164 KB)   │    │
│  │  속도: ~19 TB/s        (HBM의 약 10배!)              │    │
│  │                                                     │    │
│  │  역할: 현재 계산 중인 데이터의 임시 저장               │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Tensor Core (연산 유닛) = "계산기"                           │
│  → 계산 속도는 초고속 (312 TFLOPS on A100)                   │
│  → 연산 자체보다 데이터를 가져오는 시간이 병목                 │
└──────────────────────────────────────────────────────────────┘
```

핵심 통찰: 현대 GPU에서는 **연산 속도보다 메모리 대역폭이 병목**이다. Tensor Core의 연산 능력은 충분히 빠르지만, 데이터를 HBM에서 읽어오고 다시 쓰는 시간이 전체 성능을 제한한다. 이를 **memory-bound** 문제라 한다.

비유:
> **HBM = 큰 창고** — 많이 넣을 수 있지만, 물건을 꺼내려면 복도를 걸어가야 한다.
> **SRAM = 내 책상** — 공간이 좁지만, 손을 뻗으면 바로 닿는다.
> 계산 자체는 빠른데, **창고에서 물건을 가져오는 왕복 시간**이 느린 것이다.

### 5.2 표준 Attention의 메모리 문제

표준(naive) attention 구현은 N×N 행렬을 HBM에 명시적으로 저장(materialize)한다. 이 과정에서 HBM과의 데이터 왕복이 병목이 된다.

```
┌──────────────────────────────────────────────────────────────┐
│          표준 Attention의 실행 흐름                            │
│                                                              │
│  Step 1: Q, K를 HBM에서 읽어옴            → HBM Read  ①    │
│  Step 2: S = Q × Kᵀ 계산                                    │
│  Step 3: S를 HBM에 저장                    → HBM Write ②    │
│  Step 4: S를 HBM에서 다시 읽어옴           → HBM Read  ③    │
│  Step 5: P = softmax(S) 계산                                 │
│  Step 6: P를 HBM에 저장                    → HBM Write ④    │
│  Step 7: P를 HBM에서 다시 읽어옴           → HBM Read  ⑤    │
│  Step 8: O = P × V 계산                                      │
│  Step 9: O를 HBM에 저장                    → HBM Write ⑥    │
│                                                              │
│  총 HBM 접근: 6번 (3 reads + 3 writes)                      │
│  이동한 데이터: O(Nd + N²) — N² 항이 지배적                   │
│                                                              │
│  200K 토큰일 때:                                             │
│  S 행렬: 200K × 200K × 2 bytes = ~74 GB  ← HBM에 저장!     │
│  P 행렬: 200K × 200K × 2 bytes = ~74 GB  ← 또 저장!        │
│  → 단 하나의 attention layer에서 148 GB의 HBM I/O 발생       │
└──────────────────────────────────────────────────────────────┘
```

비유:
> 학생 200,000명의 시험지를 **모두 창고 바닥에 펼쳐놓고** 서로 비교하려는 것.
> 비교 결과를 적은 카드(N×N = 400억 장)도 창고에 보관해야 한다.
> 채점할 때마다 창고와 작업대를 **6번 왕복**해야 한다.
> 창고가 아무리 커도 400억 장의 카드를 펼칠 공간이 없다.

### 5.3 FlashAttention의 핵심: Tiling

FlashAttention의 핵심 아이디어는 단순하고 강력하다: **N×N 행렬을 만들지 않는다.**

전체 행렬을 한꺼번에 계산하여 HBM에 저장하는 대신, 입력을 작은 블록으로 나누어 SRAM(작업대)에서 처리하고, 부분 결과만 HBM에 기록한다.

```
┌──────────────────────────────────────────────────────────────┐
│                     표준 Attention                            │
│                                                              │
│  Q ──┐                                                       │
│      ├──▶  S = Q×Kᵀ  ──▶  P = softmax(S)  ──▶  O = P×V    │
│  K ──┘     [N×N]           [N×N]                             │
│            ↕ HBM           ↕ HBM        ← 거대 행렬이       │
│            저장/로드        저장/로드       창고를 왕복         │
│                                                              │
│            N×N 행렬이 HBM에 존재함                            │
├──────────────────────────────────────────────────────────────┤
│                   FlashAttention (Tiling)                     │
│                                                              │
│  Q를 블록으로 분할: [Q₁][Q₂][Q₃]...                          │
│  K를 블록으로 분할: [K₁][K₂][K₃]...                          │
│  V를 블록으로 분할: [V₁][V₂][V₃]...                          │
│                                                              │
│  for each (Kⱼ, Vⱼ) block:             ← 외부 루프           │
│    HBM → SRAM: Kⱼ, Vⱼ 로드                                  │
│    for each Qᵢ block:                  ← 내부 루프           │
│      HBM → SRAM: Qᵢ 로드                                    │
│      SRAM 내에서:                                            │
│        Sᵢⱼ = Qᵢ × Kⱼᵀ    (작은 블록 연산)                    │
│        Pᵢⱼ = softmax(Sᵢⱼ) (블록 단위 softmax)               │
│        Oᵢ += Pᵢⱼ × Vⱼ     (부분 결과 누적)                   │
│      SRAM → HBM: Oᵢ 업데이트 기록                            │
│                                                              │
│  → N×N 행렬이 HBM에 존재한 적이 없음!                        │
│  → SRAM 안에서 작은 블록끼리만 곱셈                           │
│  → HBM 왕복 횟수 대폭 감소                                   │
└──────────────────────────────────────────────────────────────┘
```

비유:
> 학생 200,000명을 **50명씩 그룹**으로 나눈다.
> 그룹 50명의 시험지만 **책상 위에 올려놓고** 채점한다.
> 채점 결과(점수)만 노트에 적고, 시험지는 치운다.
> 다음 그룹 50명을 올려놓고 반복한다.
> **창고 바닥에 모든 시험지를 펼칠 필요가 없다!**

블록 크기는 SRAM 용량에 맞춰 결정된다. A100의 경우 SM당 shared memory가 최대 164KB이므로, d=64일 때 블록 크기는 수천 토큰 단위가 된다. 이 블록들을 순회하면서 최종 결과를 점진적으로 누적하면, 수학적으로 표준 attention과 **완전히 동일한 결과**를 얻을 수 있다.

### 5.4 Online Softmax로 정확성 보장

Tiling에는 한 가지 기술적 난관이 있다. Softmax 함수는 **전체 행의 합**이 필요하다.

```
softmax(xᵢ) = e^xᵢ / Σⱼ(e^xⱼ)
                      ^^^^^^^^^^
                      분모가 "전체" 합 — 블록으로 나누면 모름
```

블록 단위로 처리하면 전체 합을 알 수 없으므로, 정확한 softmax를 구할 수 없는 것처럼 보인다. FlashAttention은 **Online Softmax** 기법으로 이 문제를 해결한다. 각 블록을 처리할 때 누적 통계값(running max, running sum)을 유지하면서, 새 블록이 추가될 때마다 이전 결과를 보정한다.

```
┌─────────────────────────────────────────────────────────────┐
│                   Online Softmax 동작                        │
│                                                             │
│  블록 1 처리:                                                │
│    local_max₁ = 5,  local_sum₁ = 100                        │
│    부분 결과₁ = softmax_local(S₁) × V₁                      │
│                                                             │
│  블록 2 처리:                                                │
│    local_max₂ = 7  ← max가 바뀜!                            │
│    이전 결과 보정: 부분 결과₁ × e^(5-7) = 부분 결과₁ × 0.135 │
│    local_sum₂ = 100 × e^(5-7) + 200 = 213.5                │
│    부분 결과 누적                                            │
│                                                             │
│  블록 3 처리:                                                │
│    local_max₃ = 6  ← 또 보정                                │
│    ...                                                      │
│                                                             │
│  마지막 블록까지 끝나면:                                      │
│    누적된 통계값이 전체 행의 정확한 softmax와 일치!            │
│                                                             │
│  → 근사가 아니라 수학적으로 동일한 결과                       │
└─────────────────────────────────────────────────────────────┘
```

비유:
> 학급 전체의 **평균 키**를 구하고 싶은데, 한 번에 전교생을 모을 수 없다.
> 대신 반별로 "평균 키"와 "학생 수"를 기록해두고,
> 반이 추가될 때마다 **전체 평균을 보정**한다.
> 마지막 반까지 끝나면 정확한 전교 평균이 나온다.

이것이 FlashAttention의 핵심 혁신이다. Softmax를 결합 가능(associative)하게 만드는 이 기법 덕분에, 블록 단위 처리가 수학적 정확성을 훼손하지 않는다.

### 5.5 재계산(Recomputation)으로 역전파 해결

신경망 학습(training)에서는 역전파(backward pass)를 위해 순전파(forward pass)의 중간 결과를 저장해야 한다. 표준 attention에서는 N×N 행렬 P를 저장해두었다가 역전파에서 사용한다.

FlashAttention은 **P를 저장하지 않는다.** 대신 순전파에서 softmax 정규화 통계값(m과 l)만 저장하고, 역전파에서 필요할 때 attention 블록을 **재계산(recomputation)**한다.

```
┌────────────────────────────────────────────────────────────┐
│  표준 Attention (역전파)                                    │
│                                                            │
│  Forward:  Q, K → S → P(N×N) → O     P를 HBM에 저장 ←     │
│  Backward: P(N×N)를 HBM에서 읽어옴    O(N²) 메모리 사용    │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  FlashAttention (역전파)                                    │
│                                                            │
│  Forward:  블록 단위 계산 → O, m, l 저장  (m, l은 O(N))    │
│  Backward: Q, K, V + m, l로 P 블록을 재계산                │
│            → HBM에서 P를 읽지 않음                          │
│            → FLOPS는 증가하지만, HBM 접근은 감소            │
│            → 전체적으로 더 빠름 (memory-bound이므로)         │
└────────────────────────────────────────────────────────────┘
```

재계산으로 인해 전체 연산량(FLOPs)은 약간 증가한다. 그러나 현대 GPU에서 병목은 연산이 아니라 메모리 접근이므로, HBM I/O를 줄이는 것이 전체 속도에서 더 큰 이득을 가져온다.

### 5.6 결과: 연산량은 같지만 빠르다

FlashAttention의 결과를 표준 attention과 비교하면:

```
┌────────────────────────┬──────────────────┬──────────────────┐
│                        │ 표준 Attention    │ FlashAttention   │
├────────────────────────┼──────────────────┼──────────────────┤
│ 수학적 결과             │ 기준              │ 동일 (근사 아님!) │
│ 연산 횟수 (FLOPs)      │ O(N²d)           │ O(N²d) ← 같음   │
│ HBM 메모리 사용량      │ O(N²)            │ O(N)   ← 선형!  │
│ HBM 읽기/쓰기 횟수     │ O(Nd + N²)       │ O(N²d²/M)       │
│ 실측 속도 (A100)       │ 기준              │ 2~7.6x 빠름     │
│ 메모리 절감 (seq 2K)   │ 기준              │ 10x 절감         │
│ 메모리 절감 (seq 4K)   │ 기준              │ 20x 절감         │
└────────────────────────┴──────────────────┴──────────────────┘

M = SRAM 크기, d = head 차원
```

여기서 가장 중요한 행은 **"수학적 결과: 동일"**이다. FlashAttention은 근사(approximation)가 아니다. 표준 attention과 수학적으로 완전히 동일한 결과를 산출한다. 빨라지는 이유는 알고리즘을 바꾼 것이 아니라, **같은 알고리즘을 하드웨어 특성에 맞게 실행하는 방식**을 바꾼 것이다.

핵심 통찰을 비유로 정리하면:

```
표준:  [창고에서 꺼냄] → [계산] → [창고에 넣음] → [창고에서 꺼냄] → [계산] → ...
       ^^^^^^^^^^^^^^^^           ^^^^^^^^^^^^^^^^
       느린 부분                   느린 부분 (반복!)

Flash:  [창고에서 꺼냄] → [책상에서 계산, 계산, 계산, 계산] → [결과만 창고에 넣음]
        ^^^^^^^^^^^^^^^^                                     ^^^^^^^^^^^^^^^^^^
        1번만                                                 1번만
```

계산의 총량은 같다. 하지만 창고(HBM)를 왕복하는 횟수를 극적으로 줄임으로써, 전체 실행 시간이 단축된다.

### 5.7 버전별 진화 (v1 → v2 → v3)

FlashAttention은 2022년 첫 발표 이후 지속적으로 개선되었다. 각 버전은 이전 버전의 한계를 극복하며, 점점 더 높은 GPU 활용률을 달성했다.

**FlashAttention v1 (2022)**

Tri Dao가 발표한 최초 버전. Tiling + Online Softmax + Recomputation의 세 가지 핵심 기법을 도입했다. A100 GPU에서 표준 attention 대비 2~4배 빠르고, 메모리를 O(N²)에서 O(N)으로 줄였다.

한계: GPU 활용률이 25~40%에 머물렀다. 이론적 최대 성능(312 TFLOPS)의 절반도 쓰지 못한 것이다.

**FlashAttention v2 (2023)**

v1의 비효율을 분석하여 두 가지를 개선했다:

1. **비행렬 연산(non-matmul FLOPs) 최소화**: GPU의 Tensor Core는 행렬 곱셈에 특화되어 있다. A100에서 비행렬 연산은 행렬 연산보다 **16배 느리다.** v2는 softmax의 rescaling 등 비행렬 연산을 줄이고, softmax 정규화(나눗셈)를 블록 처리 마지막에 한번만 수행하는 lazy softmax division 기법을 도입했다.

2. **워프(warp) 간 병렬화 최적화**: GPU의 스레드 그룹인 워프 간의 작업 분배를 개선하여, 통신 오버헤드를 줄이고 head/batch/sequence 차원에서의 병렬성을 극대화했다.

결과: A100에서 **~230 TFLOPS** 달성 (GPU 활용률 ~72%). v1 대비 약 2배 빠름.

**FlashAttention v3 (2024)**

NVIDIA Hopper 아키텍처(H100 GPU)의 새로운 하드웨어 기능을 활용한 버전:

1. **비동기 실행**: v1/v2는 본질적으로 동기적이었다. v3는 H100의 비동기 WGMMA 명령어를 활용하여, softmax(비행렬 연산)와 GEMM(행렬 연산)을 **동시에** 실행한다. 한쪽이 softmax를 계산하는 동안 다른 쪽이 행렬 곱셈을 수행하는 파이프라이닝이다.

2. **Pingpong 스케줄링**: 2개의 warpgroup이 번갈아가며 softmax와 GEMM을 실행한다. Warpgroup A가 softmax를 실행하는 동안 Warpgroup B가 GEMM을 실행하고, 그 반대도 마찬가지다.

3. **FP8 저정밀도 지원**: H100의 FP8 Tensor Core를 활용하여 2배의 처리량을 달성한다.

결과: H100에서 초기 보고 **~75% GPU 활용률** (이후 업데이트에서 BF16 기준 최대 **~85%** 달성), FP16 기준 v2 대비 1.5~2배 빠름. FP8에서는 **1.2~1.3 PFLOPS** (petaFLOPS)를 달성.

```
┌──────────┬─────────────────────────┬───────────────┬──────────────┐
│ 버전     │ 핵심 아이디어            │ GPU 활용률    │ 대상 GPU     │
├──────────┼─────────────────────────┼───────────────┼──────────────┤
│ v1 (2022)│ Tiling + Recomputation  │ 25~40%       │ A100 (Ampere)│
│ v2 (2023)│ + non-matmul 최소화     │ ~72%         │ A100 (Ampere)│
│          │ + warp 병렬화 최적화    │              │              │
│ v3 (2024)│ + 비동기 실행 (WGMMA)   │ 75~85%       │ H100 (Hopper)│
│          │ + Pingpong 스케줄링     │              │              │
│          │ + FP8 저정밀도          │              │              │
└──────────┴─────────────────────────┴───────────────┴──────────────┘

표준 Attention 대비 누적 속도 향상:

  v1: ██████████                              2~4x
  v2: ████████████████████                    4~8x
  v3: ████████████████████████████████        최대 16x
```

FlashAttention이 없었다면, 200K context window는 물리적으로 불가능에 가까웠을 것이다. 이 기법이 있기에 Chapter 2에서 다룬 "200K 토큰의 대화 히스토리를 매번 서버에 보내는 구조"가 실제로 작동할 수 있다.

---

## Chapter 6. 실무 시사점 — GenerationResult 클래스 설계

이 문서에서 다룬 모든 내용은 하나의 실무 맥락에서 출발했다: LLM API를 호출하여 응답을 받아오는 RAG 시스템에서 `GenerationResult` 클래스를 어떻게 설계할 것인가.

```python
@dataclass
class GenerationResult:
    answer: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
```

### 6.1 API별 필드 매핑

이 클래스의 필드명은 OpenAI의 명명 규칙(`prompt_tokens`, `completion_tokens`)을 따르고 있다. Claude API를 호출할 경우 필드 매핑이 필요하다.

```
┌──────────────────────────────────────────────────────────────┐
│  GenerationResult     ←  OpenAI API       ←  Claude API     │
│                                                              │
│  prompt_tokens        ←  prompt_tokens    ←  input_tokens   │
│  completion_tokens    ←  completion_tokens←  output_tokens  │
│  total_tokens         ←  total_tokens     ←  (직접 합산)    │
└──────────────────────────────────────────────────────────────┘
```

LiteLLM 같은 통합 라이브러리를 사용하면 이 변환이 자동으로 이루어진다. 직접 API를 호출한다면 매핑 로직을 구현해야 한다.

### 6.2 CLI 환경에서의 토큰 추적

Claude Code CLI(`claude -p`)는 stdout에 응답 텍스트만 반환하며, 기본적으로 토큰 사용량 정보를 제공하지 않는다. `--output-format json`을 사용하면 구조화된 JSON 응답을 받을 수 있지만, API 스타일의 `usage` 객체는 포함되지 않는다.

Claude Code가 구독 기반 과금 모델을 사용하기 때문에, 토큰 추적은 사용자 입장에서 불투명한 편이다. 커뮤니티 도구(toktrack, ccusage 등)가 이 격차를 메우고 있다.

### 6.3 설계 권장사항

```
┌──────────────────────────────────────────────────────────────┐
│  상황별 GenerationResult 토큰 필드 설계 권장                   │
│                                                              │
│  ① API 직접 호출 (OpenAI/Claude):                            │
│     → 토큰 필드 유지 (비용 추적, 모니터링에 필수)              │
│     → API별 필드명 매핑 레이어 구현                           │
│                                                              │
│  ② LiteLLM 등 통합 라이브러리 사용:                           │
│     → 토큰 필드 유지 (라이브러리가 자동 매핑)                  │
│                                                              │
│  ③ CLI만 사용 (claude -p):                                   │
│     → 토큰 필드를 Optional(None)로 유지하거나 제거             │
│     → 향후 API로 전환할 가능성이 있다면 유지 권장              │
│                                                              │
│  ④ RAG 시스템 (1회성 호출):                                   │
│     → 토큰 누적 걱정 없음 (Chapter 2.6)                      │
│     → 단, 비용 모니터링 목적으로 토큰 필드 유지 권장           │
│     → retrieved context 크기에 따라 input tokens 변동 가능    │
└──────────────────────────────────────────────────────────────┘
```

---

## 부록. 출처 및 참고 문헌

### API 공식 문서
- [Anthropic Messages API Reference](https://docs.claude.com/en/api/messages)
- [Anthropic Token Counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- [Anthropic Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [Anthropic Context Windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)
- [OpenAI Token Usage Help](https://help.openai.com/en/articles/7127987-what-is-the-difference-between-prompt-tokens-and-completion-tokens)

### 토큰과 다국어
- [Understanding LLM Billing: Characters to Tokens (Eden AI)](https://www.edenai.co/post/understanding-llm-billing-from-characters-to-tokens)
- [CJK Text in LLM Pipelines (Tony Baloney)](https://tonybaloney.github.io/posts/cjk-chinese-japanese-korean-llm-ai-best-practices.html)

### LLM 아키텍처와 메모리
- [Understanding LLM Latency (Proxet)](https://www.proxet.com/blog/llm-has-a-performance-problem-inherent-to-its-architecture-latency)
- [Stateless LLMs (Medium)](https://medium.com/@kandaanusha/stateless-llms-27281a7e2056)
- [Memory and State in LLM Applications (Arize AI)](https://arize.com/blog/memory-and-state-in-llm-applications/)

### Transformer 연산 비용
- [Attention Mechanism Complexity Analysis (Medium)](https://medium.com/@mridulrao674385/attention-mechanism-complexity-analysis-7314063459b1)
- [Scaling to Millions of Tokens (NVIDIA)](https://developer.nvidia.com/blog/scaling-to-millions-of-tokens-with-efficient-long-context-llm-training/)
- [Long Context Windows in GenAI (Emerge Haus)](https://www.emerge.haus/blog/long-context-windows-in-generative-ai)

### FlashAttention
- [FlashAttention v1 논문 (Dao et al., 2022)](https://arxiv.org/abs/2205.14135)
- [FlashAttention v2 (Stanford CRFM)](https://crfm.stanford.edu/2023/07/17/flash2.html)
- [FlashAttention v3 논문](https://arxiv.org/pdf/2407.08608)
- [FlashAttention 설명 (DigitalOcean)](https://www.digitalocean.com/community/tutorials/flashattention)
- [ELI5: FlashAttention (Aleksa Gordic)](https://gordicaleksa.medium.com/eli5-flash-attention-5c44017022ad)
- [FlashAttention v1/v2/v3 비교 (Najeeb Khan)](https://medium.com/@najeebkan/flashattention-one-two-three-6760ad030ae0)
- [GitHub: Dao-AILab/flash-attention](https://github.com/Dao-AILab/flash-attention)

### Claude Code
- [Claude Code Context Window Guide (eesel.ai)](https://www.eesel.ai/blog/claude-code-context-window-size)
- [Automatic Context Compaction (Anthropic Cookbook)](https://platform.claude.com/cookbook/tool-use-automatic-context-compaction)
- [Claude Code --output-format (ClaudeLog)](https://claudelog.com/faqs/what-is-output-format-in-claude-code/)

---

*이 문서는 RAG 시스템에서 GenerationResult 클래스의 토큰 필드 설계에 대한 질문에서 출발하여, LLM API의 토큰 시스템, stateless 아키텍처, 물리적 데이터 크기, GPU 연산 비용, 그리고 이를 가능하게 하는 FlashAttention 최적화 기법까지를 하나의 흐름으로 다루었다.*
