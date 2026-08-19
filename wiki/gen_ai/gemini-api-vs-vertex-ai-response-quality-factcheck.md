---
tags: [gemini, vertex-ai, ai-studio, fact-check, response-quality, grounding]
created: 2026-08-17
---

# Gemini API vs Vertex AI 응답 품질 차이 Fact-Check

> 대상 질문: 같은 Gemini 모델 ID를 Gemini Developer API(Google AI Studio 백엔드)와 Vertex AI에서 호출하면 인증·운영 설정 외에 응답 품질도 달라지는가?

## 결론

**두 플랫폼을 완전히 동일한 추론 경로라고 가정하면 안 된다.** 이미지 토큰화, Search grounding, Safety 필터처럼 응답에 영향을 줄 수 있는 플랫폼 계층의 차이가 확인됐다. 반면 **“AI Studio가 항상 더 좋다” 또는 “Vertex AI가 항상 더 좋다”는 일반화도 근거가 부족하다.** 방향이 서로 반대인 실사용 보고가 있고, 기존 비교 사례 상당수는 샘플링 파라미터·모델 버전·도구 설정을 통제하지 않았다.

실무적으로는 플랫폼 이름만으로 품질을 예측하지 말고, 실제 세금 문서·이미지·구조화 추출 데이터셋으로 A/B 회귀 평가를 수행해야 한다.

## 판정 기준

| 태그 | 의미 |
|---|---|
| `Confirmed` | 1차 출처 또는 재현 가능한 원문으로 핵심 사실 확인 |
| `Likely` | 강한 정황이 있으나 독립 재현·공식 원인 설명이 부족 |
| `Uncertain` | 상충 근거나 통제되지 않은 교란변수가 남음 |
| `Unverified` | 공개 자료만으로 확인할 수 없음 |

검증은 7개 주장을 15개 관점으로 분해해 수행했다. 기존 Claude Code Workflow가 세션 한도로 3개 결과만 반환하고 `synthesis=null`로 종료되어, 실패한 렌즈를 독립 조사로 다시 실행했다. 기술 주장은 공식 문서·SDK·GitHub 원문을 우선했고, C2와 C7의 핵심 URL은 최종 종합 단계에서 직접 다시 열어 인용 범위를 확인했다.

## 확신도 변경 요약

| ID | 검증 대상 | 원 태그 | 최종 태그 | 반론 결과 | 실질 영향 |
|---|---|---|---|---|---|
| C1 | 이미지 258 vs 1,806 토큰 | Confirmed | **Likely** | WEAKENED | 특정 로그는 확인됐지만 원인·보편성은 미확정 |
| C2 | AI Studio 품질 우위 포럼 보고 | Likely | **Confirmed — 보고 존재** | WEAKENED | **Uncertain — 플랫폼 전체 우열로 일반화 불가** |
| C3 | 샘플링 기본값 차이 | Confirmed/Uncertain 혼재 | **Uncertain — 차이 미확인** | WEAKENED | 실제 기본값은 양쪽이 거의 같아 보임 |
| C4 | Safety 판정 방식 차이 | Confirmed | **Confirmed — 문서상 차이** | UPHELD | 필터 활성화 시 영향 가능, 기본 요청 영향은 불확실 |
| C5 | Search grounding 기본 비활성 | Confirmed | **Confirmed — 일반 모델 호출 한정** | UPHELD | 관리형 Deep Research Agent는 예외 |
| C6 | 동일 모델 ID의 동일 weights | Unverified | **Unverified** | N-A | 동일 출력 보장도 없음 |
| C7 | FastSearch·Knowledge Graph 차등 | Likely | **Confirmed — 범위 제한** | UPHELD | 소비자 Gemini 앱 vs 제3자 Vertex grounding에만 해당 |

## C1. 이미지 토큰 258 vs 1,806

### 최종 판정: Likely

`python-genai` [GitHub 이슈 #1907](https://github.com/googleapis/python-genai/issues/1907)에는 `gemini-2.5-flash`와 같은 700×1003 이미지로 다음 결과를 얻은 재현 코드와 로그가 있다.

- Gemini Developer API: 이미지 258토큰(텍스트 포함 전체 259)
- Vertex AI: 이미지 1,806토큰
- 이슈는 2026-08-17 기준 Open이며 `type: bug`, `priority: p2`, 양 API 라벨이 붙어 있다.

다만 원 주장의 표현은 강도를 낮춰야 한다.

- 공개 댓글 작성자가 Google 직원이라는 점은 확인되지 않았다. 따라서 “Google 담당자가 원인을 공식 확인했다”고 쓰면 안 된다.
- 1,806 ÷ 258 = 7이라는 산술만으로 “정확히 7개 고해상도 타일”이라고 확정할 수 없다.
- [Gemini 이미지 토큰 계산 문서](https://ai.google.dev/gemini-api/docs/image-understanding#token-calculation)의 근사식을 700×1003에 적용하면 단순한 7타일 설명과 맞지 않는다.
- [Cloud 이미지 이해 문서](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/image-understanding#image-tokenization)와 이슈 관찰값 사이에도 설명되지 않은 간극이 남는다.

따라서 **해당 환경에서 수치 차이가 관찰됐다는 사실은 강하지만, 이것이 현재 모든 모델·이미지에 적용되는 고정 규칙인지와 정확한 전처리 원인은 미확정**이다.

### 실무 의미

- 이미지·스캔 PDF 요청은 플랫폼별 `count_tokens`와 실제 `usage_metadata`를 모두 기록한다.
- Vertex의 입력 토큰 비용이 더 커질 가능성을 비용 모델에 반영한다.
- 이미지 해상도·크기·`media_resolution`을 고정한 자체 재현 테스트 없이 7배를 일반 상수로 사용하지 않는다.

## C2. “AI Studio가 문서 태스크에서 더 낫다”는 보고

### 최종 판정: 보고 존재 Confirmed / 일반적 품질 우위 Uncertain

기존에 인용한 Google 포럼 4개 스레드는 실제로 존재하며 PDF 요약, 숫자 추출, 문서 분류, 구조화 추출에서 AI Studio 쪽 결과가 낫다는 사용자 보고를 담고 있다. 예를 들어 [utility bill 요약 스레드](https://discuss.ai.google.dev/t/why-is-there-such-a-big-difference-in-answers-between-ai-studio-and-vertex-ai/4393)는 같은 프롬프트와 모델이라고 주장하지만, 답변자는 요청이 완전히 같았는지 되묻고 대화가 끝난다.

반론 검증 결과, 이 네 사례를 플랫폼 고유 품질 차이의 증거로 일반화하기 어렵다.

1. 네 스레드 모두 `temperature`, `topP`, `topK`, 도구, Safety 설정을 완전히 고정했다고 입증하지 않았다.
2. 대부분 단일 사용자의 짧은 보고이고 Google의 공식 원인 분석이 없다.
3. 문제를 경험한 사람만 글을 쓰는 선택 편향의 분모를 알 수 없다.
4. 반대 방향 사례도 있다. [Vertex AI가 이미지 세부 묘사에 더 낫다는 포럼 답변](https://discuss.google.dev/t/gemini-vision-on-vertex-ai-vs-ai-studio/191340)과, 같은 SDK·모델·주요 파라미터에서 Vertex 출력 이미지가 더 깨끗했다는 [2026년 비교 사례](https://discuss.ai.google.dev/t/downscaling-degradation-issue-started-happening-today-with-nb2/128689)가 확인됐다.
5. Google 포럼 밖의 [Reddit 사례](https://www.reddit.com/r/Bard/comments/1falasv)도 존재하지만 AI Studio UI, Developer API, Vertex API를 혼용해 서술하고 원인 통제가 불충분하다.

결론은 **플랫폼에 따른 차이를 체감했다는 보고는 반복되지만, 우열 방향은 작업·모델·시점별로 엇갈린다**이다.

## C3. 샘플링 파라미터 기본값

### 최종 판정: Uncertain — 플랫폼별 기본값 차이 미확인

[Vertex AI의 Gemini 2.5 Flash 모델 카드](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/2-5-flash)는 다음 기본값을 명시한다.

| 파라미터 | Vertex 문서 | Gemini Developer API 검증 결과 |
|---|---:|---:|
| `temperature` | 1.0 | 1.0으로 관찰 |
| `topP` | 0.95 | 약 0.95로 관찰 |
| `topK` | 64 고정 | 64로 관찰 |
| `candidateCount` | 1 | 미지정 시 1 |

Gemini Developer API는 정적 모델 소개 페이지 대신 [Models API](https://ai.google.dev/api/models)의 `temperature`, `topP`, `topK` 필드로 백엔드 기본값을 노출한다. 비공식 [공개 API 응답 보관본](https://gist.github.com/asus4/122847cb7a9b86f959aae293343a15f3)에서도 Vertex 값과 일치했다. `candidateCount`의 미지정 기본값 1은 [GenerateContent API](https://ai.google.dev/api/generate-content#GenerationConfig)에 명시돼 있다.

따라서 **문서 배치 방식의 비대칭은 있지만, 샘플링 기본값이 실제로 다르다는 근거는 확보하지 못했다.** 과거 포럼의 품질 차이를 기본 파라미터 차이 하나로 설명하는 가설도 미검증이다.

실무에서는 이 결론과 별개로 비교 실험 시 모든 생성 파라미터를 명시적으로 고정해야 한다. 백엔드 기본값은 모델 버전과 함께 바뀔 수 있기 때문이다.

## C4. Safety 필터의 probability vs severity

### 최종 판정: 문서상 차이 Confirmed / 기본 품질 영향 Uncertain

[Gemini Developer API Safety 문서](https://ai.google.dev/gemini-api/docs/safety-settings)는 조정 가능한 필터가 위해의 **확률(probability)**을 기준으로 차단하며 severity를 사용하지 않는다고 설명한다. 반면 [Vertex AI Safety 문서](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/configure-safety-filters)는 `SEVERITY`와 `PROBABILITY`를 제공하고 API 기본 방식을 `SEVERITY`로 설명한다.

그러나 이 문서 차이가 항상 응답 품질 차이를 만드는 것은 아니다.

- 조정 가능한 필터가 `OFF`인 모델의 기본 요청에서는 판정 방식 차이가 자동 차단에 직접 쓰이지 않는다.
- 필터를 활성화하면 같은 threshold에서도 Vertex의 severity 방식이 저확률·고심각도 콘텐츠를 다르게 차단할 가능성이 있다.
- `OFF`여도 모델 자체 안전 동작과 아동 안전 등 조정 불가능한 보호 장치는 남는다.
- Vertex의 최신 영문 문서와 현지화 문서가 어느 모델부터 `OFF`가 기본인지 서로 다르게 서술한다. 따라서 “Gemini 2.5·3.x 전체가 양쪽 모두 OFF”라고 포괄하면 안 된다.
- Vertex API 기본 방식과 Vertex 콘솔 UI의 동작도 동일하다고 가정하지 않는다.

## C5. Grounding with Google Search의 기본 활성화

### 최종 판정: 일반 모델 호출에서는 Confirmed, 관리형 Agent에는 예외

일반 모델의 표준 호출에서 Google Search grounding은 양쪽 모두 opt-in이다.

- [Gemini Developer API 예제](https://ai.google.dev/gemini-api/docs/google-search)는 요청에 `google_search` 도구를 명시한다.
- [Vertex AI 예제](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/grounding/grounding-with-google-search)도 `Tool(google_search=GoogleSearch())`를 추가하거나 콘솔 토글을 켜도록 안내한다.

도구를 등록한 뒤 모델이 실제 검색 여부와 질의를 자동 결정하는 것과, 검색 도구 자체가 기본 활성화되는 것은 다른 문제다.

예외도 있다. [Gemini Deep Research Agent](https://ai.google.dev/gemini-api/docs/deep-research)는 Google Search, URL Context, Code Execution을 기본 도구로 제공한다. 따라서 정확한 표현은 **“일반 `generateContent`/Interactions 모델 호출은 opt-in이지만 사전 구성된 관리형 Agent에는 기본 포함될 수 있다”**이다.

## C6. 같은 model ID는 같은 weights인가

### 최종 판정: Unverified

Google 문서는 통합 SDK와 같은 모델 이름을 양쪽에서 사용하는 방법을 설명하지만, **동일 model ID가 비트 단위로 같은 가중치·체크포인트·서빙 스택임을 보장하지 않는다.** [Cloud 마이그레이션 가이드](https://ai.google.dev/gemini-api/docs/migrate-to-cloud)와 [Vertex SDK 개요](https://cloud.google.com/vertex-ai/generative-ai/docs/sdks/overview)의 핵심 보장은 API·코드 이동성이지 내부 동일성이다.

동일 출력은 더 강하게 보장할 수 없다.

- `seed`를 고정해도 [Vertex 공식 RPC 문서](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/reference/rpc/google.cloud.aiplatform.v1)는 결과가 대부분 결정적일 뿐 절대적 결정성을 보장하지 않는다고 설명한다.
- `latest` 별칭은 새 릴리스로 교체될 수 있다. 안정 ID도 영구 불변 weights 해시를 의미하지 않는다.
- [Vertex SLA](https://cloud.google.com/vertex-ai/generative-ai/sla)는 가용성과 오류율만 다루며 모델 품질·출력 동등성을 보장하지 않는다.

비교 실험에서는 요청 model ID 외에 응답의 `modelVersion`, API 버전, 리전, payload, 도구, Safety 설정을 함께 기록해야 한다. 값이 같아도 weights 동일성의 증명은 아니다.

## C7. DOJ 문서의 FastSearch·Knowledge Graph 차등

### 최종 판정: 역사적 사실 Confirmed / AI Studio-vs-Vertex 근거로 사용하면 스코프 오류

미 DOJ 원 전시물 [PXR0153](https://www.justice.gov/atr/media/1399416/dl?inline=)은 2024년 당시 다음 구조를 기록한다.

- 제3자 Vertex grounding에는 웹 결과가 제공됐다.
- 소비자 Gemini 앱은 Vertex 경로 외에도 Knowledge Graph, OneBox, Related Questions 등 더 풍부한 Search 기능을 받았다.
- 내부 자료는 Vertex에 제공되는 웹 결과의 품질이 Gemini 앱보다 낮다고 표현한다.

2025년 연방법원 사실인정도 이를 더 정확히 구분한다. [법원 판결문](https://law.justia.com/cases/federal/district-courts/district-of-columbia/dcdce/1%3A2020cv03010/223205/1436/)에 따르면 FastSearch는 Vertex AI에 통합되며, 제3자 Vertex 고객은 순위화된 웹 결과 원본 자체가 아니라 그 결과의 정보를 받는다. Gemini 앱도 Vertex를 사용하지만 제3자에게 없는 Knowledge Graph 일부 등 추가 Search 기능을 받았다.

이 자료가 입증하지 않는 것은 다음이다.

- Gemini Developer API/Google AI Studio와 Vertex AI의 비교
- base model weights 또는 순수 추론 품질의 차이
- 2026년 현재도 같은 기능 차등이 유지된다는 사실

전시물에는 AI Studio가 비교 당사자로 등장하지 않는다. 따라서 C7은 **소비자 Gemini 앱과 제3자 Vertex grounding 간의 2024년 검색 기능 차등**으로만 인용해야 한다. EU DMA 자료도 Google 자체 AI와 제3자의 Search 데이터 접근 격차에 대한 경쟁 우려를 보조하지만, AI Studio-vs-Vertex의 직접 교차근거는 아니다.

## 실무 권장 A/B 평가 프로토콜

플랫폼 전환 전 실제 업무 데이터로 아래 조건을 고정해 비교한다.

1. 정확한 모델 버전과 응답의 `modelVersion`
2. `temperature`, `topP`, `topK`, `candidateCount`, `seed`, thinking 설정
3. system instruction과 전체 메시지 순서
4. Safety threshold와 harm block method
5. Search grounding·URL Context·function calling 등 도구 설정
6. 이미지 원본 바이트·해상도·MIME type·`media_resolution`
7. 리전, API 버전, SDK 버전

평가는 단일 예제가 아니라 대표 세금 문서 세트로 반복한다.

| 평가 축 | 권장 지표 |
|---|---|
| 구조화 추출 | 필드별 exact match, 누락률, 잘못 채운 필드 비율 |
| 문서 이해 | 근거 문장 일치율, 숫자·날짜 정확도, 환각률 |
| 이미지/OCR | 문자·표 인식 정확도, 이미지 입력 토큰 |
| 응답 안정성 | 같은 입력 반복 시 분산, 실패·차단·truncation 비율 |
| 운영성 | TTFT, 전체 latency, 입력·출력·thinking 토큰, 비용 |

최소 30회 이상 반복하고 blind evaluation 또는 고정된 자동 채점기를 사용한다. 결과가 나빠졌다면 플랫폼 자체를 원인으로 단정하기 전에 `modelVersion`·전처리·도구·필터 차이를 먼저 분리한다.

## 최종 정리

- **확인된 차이**: 이미지 처리 토큰 수의 특정 사례, Safety 필터 방식 문서, 일반 호출의 grounding opt-in, 2024년 소비자 앱과 제3자 Vertex의 Search 기능 차등.
- **확인되지 않은 것**: 동일 model ID의 동일 weights, 플랫폼 전체에 적용되는 일관된 품질 우열, 이미지 1,806토큰의 정확한 내부 산정 원인.
- **기각한 단순 설명**: “Vertex라는 벤더가 끼어서 항상 나빠진다”, “AI Studio와 Vertex의 샘플링 기본값이 명백히 다르다”, “DOJ 문서가 AI Studio보다 Vertex가 낮은 품질임을 증명한다.”
- **실무 판단**: 엔터프라이즈 거버넌스 때문에 Vertex를 선택하더라도 품질 parity는 별도 A/B 테스트로 검증한다.

## 관련 노트

- [[vertex-ai-gemini-agent-migration-deep-research]] — 인증·SDK·Agent 프레임워크·보안·비용·관측성을 포함한 전체 전환 가이드
- [[a2a-protocol-agent-to-agent-deep-dive]] — A2A(Agent2Agent) Protocol 심층 분석
- [[genai-rag-agent-llm-workflow-concepts]] — GenAI/Agent 핵심 개념
