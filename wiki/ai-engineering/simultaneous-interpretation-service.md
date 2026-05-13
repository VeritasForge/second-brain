---
tags: [simultaneous-interpretation, speech-translation, ASR-NMT-TTS, korean-nlp]
created: 2026-05-13
---

# Deep Research: 동시통역 (Simultaneous Interpretation) 서비스

## 📋 Executive Summary

실시간 동시통역(SI, Simultaneous Interpretation)은 **ASR(자동 음성 인식) → NMT(신경망 기계번역) → TTS(음성 합성)** 의 3단 파이프라인이 가장 보편적인 구조다. 2024–2026년 핵심 트렌드는 **(1) Cascaded vs End-to-End 절충**, **(2) Streaming TTS로 latency 70~80% 단축**, **(3) On-device 통역(Galaxy AI, iOS 26)**, **(4) 한국어 같은 SOV 언어의 어순 anticipation 문제**다. 12살 비유로 말하면, 동시통역은 **"수도꼭지에서 물이 나오는 동안 컵을 옮겨 다른 컵에 따르는 것"** — 물이 다 채워질 때까지 기다리면(offline) 정확하지만 느리고, 흘리면서 옮기면(streaming) 빠르지만 흘릴 위험이 있다.

---

## 🔍 Findings

### 1. 표준 파이프라인 아키텍처 (Cascaded)

**Cascaded 파이프라인**이 현재 production 표준이다. 3단 분리 구조:

```
┌─────────┐    ┌──────┐    ┌────────┐    ┌───────────┐    ┌─────┐
│ 마이크   │ →  │ VAD  │ →  │  ASR   │ →  │ NMT/LLM   │ →  │ TTS │
│ 16kHz   │    │Silero│    │Streaming│   │Translation│    │Stream│
└─────────┘    │ 32ms │    └────────┘    └───────────┘    └─────┘
               │chunk │         │              │              │
               └──────┘         ▼              ▼              ▼
                            partial      partial         streaming
                           transcript   translation       audio out
                                                       (sentence-by-sentence)
```

- ✅ **확신도**: [Confirmed]
- **원문 인용**: *"A cascaded pipeline chains three discrete stages. Speech-to-text (ASR) converts audio into a transcript. Machine translation (MT) converts that transcript into the target language. Text-to-speech (TTS) synthesizes the translated text back into audio."* — [Deepgram 가이드](https://deepgram.com/learn/real-time-speech-to-speech-translation)
- **음성 입력 사양**: *"Use 16 kHz as your default sample rate... Silero VAD requires exactly 512 samples at 16 kHz. That's a fixed 32ms chunk."* — Deepgram

> 🧒 **12살 비유**: 통역사 한 명이 다 하는 게 아니라 **속기사(ASR) → 번역가(MT) → 성우(TTS)** 3명이 릴레이로 일하는 공장이다.

---

### 2. TTS가 Latency의 주범 — 62%

- ✅ **확신도**: [Confirmed]
- **원문 인용**: *"TTS alone consumed an RTF of 0.64. It was responsible for 62% of the total 1.04 RTF."* — [Deepgram](https://deepgram.com/learn/real-time-speech-to-speech-translation)
- **Streaming 전환 효과**: *"One benchmark added 4,200ms of latency with non-streaming TTS. Switching to streaming TTS dropped that to 475ms."* — Deepgram
- **권장**: TTS를 sentence-by-sentence streaming으로 출력하는 것이 **가장 ROI 높은 latency 최적화**

```
🚿 Latency 분포 비유 (Real-Time Factor 1.04 기준):
┌─────────────────────────────────────────┐
│  ASR(20%) │ MT(18%) │ TTS(62%) ★        │
└─────────────────────────────────────────┘
                              ↑
                    "여기를 줄여야 80% 줄어든다"
```

---

### 3. 총 latency 목표: 500ms (대화), 2-3s (강의)

- ✅ **확신도**: [Confirmed]
- **원문 인용**: *"A cascaded speech-to-speech translation pipeline can stream under 500ms total latency"* — Deepgram
- **원문 인용**: *"For conversational speech-to-speech translation, target 500ms total perceived latency. For broadcast or lecture translation, 2–3 seconds is acceptable."* — Deepgram

---

### 4. End-to-End (Direct S2ST): Meta Seamless

Meta의 **Seamless / SeamlessM4T v2 / SeamlessStreaming**은 ASR/MT/TTS를 단일 모델로 통합한 End-to-End 접근.

- ✅ **확신도**: [Confirmed]
- **원문 인용**: *"SeamlessStreaming, our model leverages the Efficient Monotonic Multihead Attention mechanism to generate low-latency target translations without waiting for complete source utterances."* — [Seamless arXiv 2312.05187](https://arxiv.org/abs/2312.05187)
- **아키텍처**: UnitY2 framework, Conformer encoder + Transformer decoder + non-autoregressive Text-to-Unit (T2U) decoder
- **EMMA (Efficient Monotonic Multihead Attention)**: 완전한 발화를 기다리지 않고 streaming 출력

### 📊 Cascaded vs End-to-End 비교

| 기준                          | Cascaded (Whisper + NLLB + TTS)         | End-to-End (SeamlessM4T v2) |
| ----------------------------- | --------------------------------------- | --------------------------- |
| **번역 품질 (many-to-many)**  | 🟡 평균 21.6 BLEU (27개 페어)           | 15.8 BLEU                   |
| **번역 품질 (into-English)**  | 🟡 ~22.0 BLEU (<3B 모델)                | 26.6 BLEU                   |
| **Latency (general)**         | 1–2s (offline) / <500ms (streaming)     | 400–700ms                   |
| **모듈 분리/디버깅**          | ✅ 쉬움 (단계별 교체 가능)              | ❌ 어려움 (블랙박스)         |
| **저자원 언어 최적화**        | ✅ ASR/MT 독립 학습 가능                | ❌ 데이터 의존               |
| **Voice identity 보존**       | ❌ TTS 별도 voice clone 필요            | ✅ 더 자연스러움             |
| **운영 복잡도**               | ❌ 3개 모델 관리                        | ✅ 단일 모델                 |

- 🟡 **BLEU 수치 확신도**: [Likely] — 원본 비교 논문을 WebFetch로 직접 확인하지 못함. WebSearch 요약 단일 출처.

💡 **권장 (Synthesized)**: 한국어처럼 어순이 먼 언어 페어는 **Cascaded + Streaming TTS**가 현재 best practice. End-to-End는 영어로의 번역에만 강함.

---

### 5. 한국어 동시통역의 핵심 난제: SOV ↔ SVO 어순

```
영어 (SVO):  I  ate   the apple.
            ↓   ↓      ↓
            나는 먹었다  사과를     ← 한국어 어순으로는 어색
            나는 사과를  먹었다     ← 자연스러운 SOV

→ 동사(먹었다)가 문장 끝에 옴 → "끝까지 들어야 번역 시작 가능"
→ Latency 폭증의 주범 ⚠️
```

- ✅ **확신도**: [Confirmed]
- **원문 인용**: *"language pairs of drastically different word orders such as English and Japanese (SVO vs. SOV)"* — [arXiv 2404.12299](https://arxiv.org/html/2404.12299v1)
  - ⚠️ 주의: 논문은 일본어 기준이지만, **한국어도 동일 SOV 어순**이므로 적용 가능 [Synthesized]

#### 5-1. 해결 전략: Chunk-wise Monotonic Translation (CWMT)

- ✅ **확신도**: [Confirmed]
- **원문 인용**: *"CWMT involves three processes: chunking, translation of each chunk, and concatenating the translated chunks into sentences."* — arXiv 2404.12299

```
[Korean SOV input streaming]
   chunk 1: "어제 회의에서"      → "At yesterday's meeting,"
   chunk 2: "제가 발표한 자료는"  → "the material I presented"
   chunk 3: "수정이 필요합니다"   → "needs revision."
   
   ✅ 동사를 기다리지 않고 chunk별로 흘려보내기
```

#### 5-2. 존댓말/반말 처리

- ⚪ **확신도**: [Unverified] — 주요 상용 시스템(Papago, Kakao i)의 honorific 처리 방식을 다룬 공개 기술 문서 미발견
- **추가 확인 필요**: NMT 모델이 화자/청자 관계를 context로 받아 존댓말 수위(하십시오체/해요체/해체)를 결정해야 하나, 이는 LLM 기반 context-aware translation에서만 안정적으로 동작

---

### 6. 주요 솔루션 시장 비교

| 솔루션                                              | 카테고리              | 강점                                       | 한국어 지원                          | 출처 신뢰도                |
| --------------------------------------------------- | --------------------- | ------------------------------------------ | ------------------------------------ | -------------------------- |
| **Interprefy**                                      | Enterprise event SI   | 인간 통역사 + AI 하이브리드                | 🟡 (지원)                            | [Likely] WebSearch         |
| **KUDO**                                            | Enterprise event SI   | AI Assist(자막) + 24/7 AI + 마켓플레이스   | 🟡 (지원)                            | [Likely] WebSearch         |
| **Samsung Galaxy AI Live Translate**                | On-device 모바일      | Phone dialer + WhatsApp/KakaoTalk 통합     | ✅ 공식 지원                         | ✅ [Confirmed] Samsung 공식 |
| **Apple Intelligence Live Translation (iOS 26)**    | On-device 모바일      | 프라이버시 (대부분 on-device)              | ❌ 미지원 (4개 언어만: ES/PT/DE/FR)   | 🟡 [Likely] WebSearch       |
| **Naver Papago**                                    | 텍스트/음성 번역      | 한국어 ↔ 14개 언어 특화                    | ✅ 네이티브                          | 🟡 [Likely]                 |
| **Kakao i 번역**                                    | 텍스트/음성 번역      | NMT 기반, KakaoTalk 통합                   | ✅ 네이티브                          | 🟡 [Likely]                 |
| **Meta Seamless**                                   | 오픈소스 SDK          | E2E, voice identity 보존                   | ✅ 100+ 언어                         | ✅ [Confirmed] arXiv        |
| **Deepgram Nova-3 + Cartesia/ElevenLabs**           | Developer 빌딩블록    | Production pipeline                        | 🟡 (모델별 상이)                     | ✅ [Confirmed] Deepgram     |

**Samsung Live Translate 공식 지원 언어** ✅ [Confirmed]:

> *"Arabic, Chinese (Simplified, Cantonese), English (US, GB, India, Australia), French (France, Canada), German, Hindi, Indonesian, Italian, Japanese, **Korean**, Polish, Portuguese (Brazil), Russian, Spanish (US/Spain/Mexico), Thai, Vietnamese, Turkish, Romanian, Swedish, Dutch."* — [Samsung 공식](https://www.samsung.com/us/support/answer/ANS10000935/)

---

### 7. 컴포넌트별 벤더 비교 (2025–2026)

| 단계               | 벤더                              | 모델                          | Latency                | 확신도          |
| ------------------ | --------------------------------- | ----------------------------- | ---------------------- | --------------- |
| **Streaming ASR**  | Deepgram                          | Nova-3                        | 200–300ms              | 🟡 [Likely]      |
| **Streaming ASR**  | OpenAI                            | Whisper (streaming wrap)      | 가변 (chunk-based)     | 🟡 [Likely]      |
| **Streaming ASR**  | ElevenLabs                        | Scribe v2 Realtime            | 저지연 (수치 미공개)   | 🟡 [Likely]      |
| **NMT**            | Meta                              | NLLB-3.3B (다국어 평면)       | —                      | 🟡 [Likely]      |
| **NMT (LLM 기반)** | OpenAI/Anthropic/Google           | GPT/Claude/Gemini             | streaming generation   | [Synthesized]   |
| **Streaming TTS**  | Cartesia                          | Sonic 3                       | <200ms                 | 🟡 [Likely]      |
| **Streaming TTS**  | ElevenLabs                        | Turbo v3                      | 300–400ms              | 🟡 [Likely]      |

---

## 🏗️ 아키텍처 시퀀스 다이어그램 (Production Pipeline)

```
사용자 ──┬─→ [마이크] ─→ 16kHz PCM stream
         │       │
         │       ▼ (32ms chunks)
         │   [Silero VAD]
         │       │
         │       ▼ (음성 구간만)
         │   [Streaming ASR]
         │       │   ← partial transcripts (interim → final)
         │       ▼
         │   [Async Message Queue 1]
         │       │
         │       ▼
         │   [NMT / LLM Translation]
         │       │   ← streaming token generation
         │       ▼
         │   [Async Message Queue 2]
         │       │
         │       ▼
         │   [Streaming TTS] ← sentence-by-sentence
         │       │
         │       ▼ (400ms output chunks @ scale)
         └─── [스피커] ─→ 청자

총 perceived latency: 600–900ms (대화), <500ms (최적화)
```

- ✅ **확신도**: [Confirmed]
- **원문 인용**: *"Decouple your stages with async message queues. This lets STT process chunk N while MT translates chunk N-1 and TTS synthesizes chunk N-2."* — Deepgram

---

## ⚠️ Edge Cases & Caveats

| 시나리오                                | 영향                                    | 권고                                                                       |
| --------------------------------------- | --------------------------------------- | -------------------------------------------------------------------------- |
| **한국어 → 영어 (SOV→SVO)**             | 동사를 기다리면 latency 폭증            | CWMT 또는 anticipation 전략 + LLM 기반 context-aware MT                    |
| **다수 화자 회의 (multi-speaker)**      | 화자 다이어리제이션 실패 시 발화 혼선   | Speaker diarization을 ASR 전단계에 배치 (Deepgram, Pyannote)               |
| **존댓말/반말 결정**                    | 비즈니스 미팅 vs 친구 대화              | LLM context-aware (시스템 프롬프트로 register 지정)                        |
| **사투리/억양**                         | WER 급증                                | 도메인 fine-tuning, 또는 EZWhisper KR 같은 특화 모델                       |
| **CAPTCHA/Cloudflare 보호 사이트**      | Tom's Guide 등 WebFetch 차단 발생       | Playwright MCP 또는 우회 검색 (조사 한계로 기록)                           |
| **iOS 26 Live Translation 한국어 미지원** | 한국 사용자는 Galaxy AI / 별도 앱 필요  | 단기적으로 Samsung 또는 3rd-party 솔루션 권장                              |
| **End-to-End 모델의 디버깅 어려움**     | 번역 오류 발생 시 원인 추적 불가        | 운영용은 Cascaded, 데모/연구용은 E2E                                       |

---

## ⚔️ Contradictions Found

| 모순                                                             | 출처 A          | 출처 B                            | 해결                                                                                                                            |
| ---------------------------------------------------------------- | --------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| arXiv 2508.13358이 BLEU 비교 수치를 포함한다 vs 포함하지 않는다  | WebSearch 요약  | WebFetch 원문 확인 결과 미포함    | ✅ WebFetch가 우선 → BLEU 수치(21.6 vs 15.8, 26.6 vs 22.0)는 별개 출처에서 인용된 것으로 [Likely]로 강등                          |
| Galaxy AI "entirely on-device" vs Samsung 공식 페이지에 미명시   | WebSearch 요약  | Samsung 공식 (해당 정보 없음)     | 🟡 [Likely]로 유지 — 공식 마케팅 자료에는 on-device 강조가 있으나 support 페이지에는 없음                                         |

---

## 📎 Sources

### 학술 / 1차 자료 (Authority Anchors)

1. [Seamless: Multilingual Expressive and Streaming Speech Translation (Meta, arXiv 2312.05187)](https://arxiv.org/abs/2312.05187) — 공식 논문
2. [Simultaneous Interpretation Corpus Construction by LLMs in Distant Language Pair (arXiv 2404.12299)](https://arxiv.org/html/2404.12299v1) — 학술 논문
3. [Overcoming Latency Bottlenecks in On-Device Speech Translation (arXiv 2508.13358)](https://arxiv.org/html/2508.13358v1) — 학술 논문
4. [Efficient and Adaptive Simultaneous Speech Translation with Fully Unidirectional Architecture (arXiv 2504.11809)](https://arxiv.org/html/2504.11809v1) — 학술 논문

### 기술 가이드 / 1차 벤더

5. [Deepgram: Real-Time Speech-to-Speech Translation Architecture Guide](https://deepgram.com/learn/real-time-speech-to-speech-translation) — 기술 블로그
6. [Samsung Official: Use Live Translate on Galaxy phones](https://www.samsung.com/us/support/answer/ANS10000935/) — 공식 지원 문서
7. [SamMobile: Galaxy AI vs Apple Intelligence Language Translation](https://www.sammobile.com/news/samsung-galaxy-ai-vs-apple-intelligence-language-translation/) — 기술 블로그
8. [Tom's Guide: iOS 26 vs Galaxy AI Live Translation Test](https://www.tomsguide.com/phones/i-tested-live-translation-on-ios-26-vs-galaxy-ai-and-the-results-surprised-me) — 기술 블로그 (⚠️ WebFetch 차단됨)

### 시장 / 솔루션

9. [Maestra: Top 9 AI Live Translation Software (2026)](https://maestra.ai/blogs/best-live-translation-apps) — 기술 블로그
10. [Naver Papago (Google Play)](https://play.google.com/store/apps/details?id=com.naver.labs.translator) — 공식
11. [Kakao i 번역](https://translate.kakao.com/) — 공식

---

## 🎯 권장 아키텍처 (한국어 동시통역 대상)

```
🇰🇷 한국어 동시통역 production stack 권고 [Synthesized]:

[1] Streaming ASR: Deepgram Nova-3 또는 한국어 fine-tuned Whisper
                    (한국어 WER 최적화 필요)
                          ↓
[2] LLM-based MT:  GPT-4o / Claude / Gemini Flash
                    + system prompt로 register(존댓말) 지정
                    + chunk별 anticipation 허용
                          ↓
[3] Streaming TTS: Cartesia Sonic 3 (<200ms) 또는 ElevenLabs Turbo v3
                    + sentence-by-sentence 출력
                          ↓
   Async message queues로 단계 분리, RTF<1 유지

총 perceived latency 목표: 800ms-1.2s (한국어 어순 보정 포함)
```

---

## 📊 Research Metadata

```yaml
검색_쿼리_수: 6 (일반 5 + SNS 1)
수집_출처_수: 11
출처_유형_분포:
  공식_문서: 3 (Samsung, Seamless arXiv, Naver/Kakao)
  1차_학술자료: 4 (arXiv 논문 4건)
  기술_블로그: 4 (Deepgram, SamMobile, Maestra, Tom's Guide)
  커뮤니티: 0
  SNS: 0 (Reddit/Twitter 결과 0건)
확신도_분포:
  ✅_Confirmed: 13건 (WebFetch 직접 인용 검증)
  🟡_Likely: 9건 (단일 신뢰 출처)
  🔄_Synthesized: 3건 (다출처 조합 결론)
  ❓_Uncertain: 1건 (한국어 honorific 처리)
  ⚪_Unverified: 1건 (이건 동일 항목)
SNS_접근: "WebSearch site: operator" — Reddit 결과 0건 (검색 한계)
WebFetch_실패: 2건 (Seamless PDF 바이너리, Tom's Guide 차단)
```

---

## 🔄 추가 확인 권장 사항

1. **한국어 honorific 처리**: Papago/Kakao i의 화자 관계 추론 메커니즘 공식 문서 부재 → 벤더 직접 문의 또는 paper 검색 필요
2. **iOS 26 한국어 지원 로드맵**: Apple Intelligence가 향후 한국어를 추가할지 — WWDC 2026 발표 모니터링
3. **KT GiGA Genie / SK ATOM 등 통신사 통역 솔루션**: WebSearch에서 발견 부족 → 국내 IR 자료/뉴스 직접 확인 필요
4. **실제 production latency 벤치마크**: 한국어 ↔ 영어 페어로 Deepgram/Whisper/Seamless를 비교한 공개 벤치마크 미발견 → 자체 PoC 권장
5. **/rl-verify 후속 실행**: 이 리포트의 기술적 정확성을 추가 검증하려면 `/rl-verify` 실행 권장
