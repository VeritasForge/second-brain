# Gemini API → Vertex AI 전환 Deep Research: AI Agent 개발 실무 가이드

> 조사일: 2026-08-15 | 방법: 5개 독립 리서치 에이전트 병렬 조사(공식 문서 원문 WebFetch + 커뮤니티 교차검증) → 종합·모순 해소
> 대상 독자: Gemini API(Google AI Studio)를 직접 호출해 AI Agent를 개발해온 팀이, Vertex AI 경유 호출로 전환을 검토하는 상황

---

## 🚨 가장 먼저 알아야 할 것 2가지

### 1) "Vertex AI"라는 이름 자체가 2026년 4월에 바뀌었습니다

2026년 4월 22일 Google Cloud Next '26에서 Google은 **"Vertex AI"를 "Gemini Enterprise Agent Platform (GEAP, 제미나이 엔터프라이즈 에이전트 플랫폼)"으로 리브랜딩(rebranding, 명칭 변경)**했습니다. 4개의 독립된 조사(기술 차이/SDK/Agent 프레임워크/보안·비용 조사)에서 모두 동일한 날짜·내용으로 확인되어 확신도 ✅ **[Confirmed]**입니다.

> 원문: "It's the evolution of Vertex AI... Moving forward, all Vertex AI services and roadmap evolutions will be delivered exclusively through the Agent Platform, rather than as a standalone service." — [Google Cloud 공식 블로그](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform) (2026-04-23)

**실무적으로 중요한 건 다음입니다**: 콘솔 UI·문서 URL·마케팅 명칭은 바뀌었지만, **기술적 명칭(API 엔드포인트 `aiplatform.googleapis.com`, IAM(Identity and Access Management, 신원 및 접근 관리) 역할명 `roles/aiplatform.*`, Python 패키지명 `google-cloud-aiplatform`)은 하위 호환을 위해 그대로 유지**됩니다. 이 문서는 사용자가 질문에서 사용한 "Vertex AI"라는 이름을 그대로 쓰되, 최신 문서를 찾을 때는 `gemini-enterprise-agent-platform` 경로도 함께 검색해야 한다는 점을 전제로 합니다.

구 명칭 → 신 명칭 대응표:

| 구 명칭 (~2026년 3월까지 자료) | 신 명칭 (2026년 4월 이후) | 확신도 |
|---|---|---|
| Vertex AI | Gemini Enterprise Agent Platform | ✅ Confirmed |
| Vertex AI Agent Builder | Agent Studio | ✅ Confirmed |
| Vertex AI Agent Engine (구 Reasoning Engine) | Agent Runtime | ✅ Confirmed |
| Agentspace | Gemini Enterprise (2025-10-09, 별도의 앞선 리브랜딩) | 🟡 Likely |
| Agent Development Kit (ADK) | (이름 그대로 유지) | ✅ Confirmed |

### 2) API 키 정책이 3주 안에 바뀝니다 (2026년 9월)

오늘(2026-08-15) 기준으로, **AI Studio의 "표준 API 키(Standard API key, 발급자 식별 없는 익명 키)"가 2026년 9월부터 전면 거부**됩니다. 이후로는 서비스 계정(Service Account)에 결합된 "인가 키(Authorization key)"만 허용됩니다.

> 원문: "By September 2026, all standard keys will be rejected." — [ai.google.dev/gemini-api/docs/api-key](https://ai.google.dev/gemini-api/docs/api-key) (최종 수정 2026-07-30)

지금 팀이 발급받아 쓰고 있는 "그냥 API 키"가 표준 키 방식이라면, **Vertex AI 전환 여부와 무관하게 곧 인증 방식을 바꿔야 합니다.** 이 마감이 이번 마이그레이션 검토의 시급성을 높이는 요인입니다.

---

## 📖 용어집 (Glossary)

이 문서에 반복 등장하는 약어를 먼저 정리합니다. 각 용어는 본문 최초 등장 시에도 다시 병기합니다.

| 약어 | 풀네임 | 한 줄 설명 |
|---|---|---|
| ADC | Application Default Credentials | GCP(Google Cloud Platform)가 코드 실행 환경에 따라 자동으로 인증 정보를 찾아주는 표준 방식 |
| ADK | Agent Development Kit | Google의 오픈소스 AI Agent 개발 프레임워크 |
| A2A | Agent2Agent Protocol | 에이전트와 에이전트 사이의 통신·발견(discovery) 표준 프로토콜 |
| MCP | Model Context Protocol | 에이전트와 외부 도구/데이터소스를 연결하는 표준 프로토콜 |
| IAM | Identity and Access Management | GCP의 신원·접근 권한 관리 체계 |
| WIF | Workload Identity Federation | 서비스 계정 키 파일 없이 외부/사내 워크로드를 GCP에 인증시키는 방식 |
| VPC-SC | VPC(Virtual Private Cloud) Service Controls | 데이터 유출 방지를 위한 서비스 경계(perimeter) 설정 |
| CMEK | Customer-Managed Encryption Keys | 고객이 직접 관리하는 암호화 키로 저장 데이터를 암호화하는 기능 |
| PSC | Private Service Connect | 인터넷을 거치지 않는 사설 네트워크 경로로 GCP 서비스에 접근하는 기능 |
| DSQ | Dynamic Shared Quota | 프로젝트별 고정 쿼터 없이 리전 내 가용 용량을 여러 고객이 동적으로 나눠 쓰는 방식 |
| PT | Provisioned Throughput | 처리량(throughput)을 고정 요금으로 사전 예약하는 옵션 |
| GSU | Generative AI Scale Unit | PT의 처리량을 측정하는 단위 |
| SLA / SLO | Service Level Agreement / Objective | 서비스 가동률 등에 대한 (계약상 보장 / 목표) 수치 |
| RPM/TPM/RPD | Requests per Minute / Tokens per Minute / Requests per Day | API 호출 빈도 제한 단위 |
| EDP | Enterprise Discount Program | GCP 대량 사용 기업 대상 할인 프로그램 |
| AFC | Automatic Function Calling | SDK가 함수 호출(tool use)과 실행을 자동으로 처리해주는 기능 |
| GA | General Availability | 정식 출시(프리뷰/베타를 벗어난 상태) |

**확신도 태그 범례** (아래 본문 전체에서 사용):

| 태그 | 의미 |
|---|---|
| ✅ [Confirmed] | 2개 이상의 독립 출처에서 원문을 직접 확인해 일치 |
| 🟡 [Likely] | 신뢰할 만한 출처 1개에서 원문 확인, 추가 교차검증은 부족 |
| ❓ [Uncertain] | 출처 간 모순이 있거나 근거가 제한적 |
| ⚪ [Unverified] | 검증 가능한 1차 출처를 찾지 못함, 참고용 |

---

## 1. Gemini API(AI Studio) vs Vertex AI: 핵심 기술 차이

### 1.1 한눈에 보는 비교표

| 항목 | AI Studio (Gemini Developer API) | Vertex AI (Gemini Enterprise Agent Platform) |
|---|---|---|
| 인증 | API 키 문자열 (`x-goog-api-key` 헤더) | GCP 서비스 계정 + IAM (역할 `roles/aiplatform.user`), OAuth2 스코프 `cloud-platform` |
| 엔드포인트 | 리전 개념 없음 (국가 단위 허용/차단만) | 리전별 엔드포인트 + 글로벌 엔드포인트 병존 |
| 데이터 레지던시(data residency) | 데이터 처리 위치를 선택/보장받을 수단 없음 | 리전 지정 시 해당 리전 내 처리 보장 (단, 공식 커미트먼트는 미국·EU 리전 한정) |
| 신규 모델 출시 | Vertex AI와 동시 출시(공식 방침) | AI Studio와 동시 출시 (세부 GA 시점은 유동적) |
| Quota/Rate Limit | 사용액 기반 4단계 티어(Free~Tier3), RPM/TPM/RPD 제한 | 신규 모델은 DSQ(고정 쿼터 없음), 구형 모델은 프로젝트×리전 쿼터 |
| 토큰 단가 | 동일 (예: gemini-2.5-pro 입력 $1.25/출력 $10.00 per 1M, 200K 초과 시 2배) | 동일 |
| 결제 계정 | Google 계정만으로 무료 이용 가능 | GCP 프로젝트+Cloud Billing 필수, 무과금은 90일 Express Mode 한정 |
| SLA | 없음 (약관에 SLA 문구 부재) | 있음 — `generateContent`/`streamGenerateContent` 월간 가동률 SLO 99.5%, 미달 시 10~50% 크레딧 |
| 실측 지연시간(latency) | ⚠️ 더 빠름 (아래 4.4절 참고) | 상대적으로 느림 |
| 프리뷰 모델 접근 | 즉시 접근 가능한 경우 많음 | allowlist 별도 승인 필요할 수 있음 |
| 할인 프로그램 | 없음 | EDP(Enterprise Discount Program), Provisioned Throughput 약정 할인 적용 가능 |

확신도: 표 전체 ✅ **[Confirmed]** (2개 이상 독립 출처 교차 확인).

### 1.2 인증 방식 상세

```
[AI Studio]                         [Vertex AI]
x-goog-api-key: API_KEY             OAuth2 access token (~1시간 TTL)
   │                                    │
   └─ 발급자 식별 없음                    └─ Service Account 또는 ADC로 발급
      (2026-09부터 이 방식 거부됨,             │
       서비스 계정 결합 키만 허용)              └─ 스코프: cloud-platform
                                              역할: roles/aiplatform.user
```

- AI Studio: "Standard API keys don't identify a caller." vs "Authorization keys are bound directly to a Google Cloud service account." — [ai.google.dev/gemini-api/docs/api-key](https://ai.google.dev/gemini-api/docs/api-key)
- Vertex AI: "Always specify the `https://www.googleapis.com/auth/cloud-platform` scope... it's pretty much the only scope available." 서비스 계정 또는 ADC 신원에 `roles/aiplatform.user` 역할 필요.

### 1.3 모델 가용성에 대한 주의 (❓ Uncertain 구간 포함)

2026년 8월 기준 Gemini 3 계열은 3 → 3.1 → 3.5 → 3.6 → 3.7로 수개월 새 빠르게 버전업되고 있습니다. AI Studio 목록에는 `gemini-3.1-pro-preview` 등 프리뷰 라벨이 붙은 모델이 있는 반면, 일부 3차 가격 추적 사이트는 이미 "Gemini 3 Pro"를 GA(정식 출시) 가격으로 취급하는 등 **표기가 완전히 일치하지 않습니다.** 이 문서에 적은 특정 모델 ID를 코드에 하드코딩하지 말고, **구현 시점에 `ai.google.dev/gemini-api/docs/models` 공식 목록을 반드시 재확인**하세요.

실무에서 실제로 발생한 사례(⚠️ 중요): AI Studio에서 쓰던 프리뷰 이미지 모델(`gemini-3-pro-image-preview` 등)을 Vertex AI에서 그대로 호출했더니 `"Publisher Model ... was not found"` 오류가 발생했습니다. **프리뷰 모델은 Vertex AI 쪽에서 별도 allowlist 승인이 필요할 수 있습니다.** GA 모델(`gemini-2.5-flash` 등)은 문제없이 작동했습니다. 🟡 [Likely] — [Google 개발자 포럼 실사례](https://discuss.ai.google.dev/t/migrating-from-gemini-api-to-vertex-enterprise-agent-platform/144841)

---

## 2. SDK 마이그레이션

### 2.1 SDK 계보 정리

```
google-generativeai (구, google.generativeai)
   └─ ✅ [Confirmed] Deprecated. GitHub 저장소가
      "google-gemini/deprecated-generative-ai-python"으로 개명·archive됨
      원문: "All support for this repository ended permanently
             on November 30, 2025."
      (⚠️ 다른 2차 자료는 "2025-08-31 지원 종료"로도 언급 — 원문 직접 인용이
       확보된 "2025-11-30"을 신뢰 가능한 값으로 채택, 8월 31일 표기는
       [Uncertain]으로 남김. 최신 계약/공지는 Google 채널로 재확인 권장)
   │
   ▼ (기계적 치환은 아니고 코드 재작성 필요 — breaking rewrite)
   │
google-genai (신, unified SDK, `from google import genai`)
   └─ ✅ [Confirmed] "Gemini Developer API"와 "Gemini Enterprise
      Agent Platform(구 Vertex AI)"을 모두 지원하는 통합 SDK
      pip install google-genai (최신 2.18.1, Python >= 3.10 필요)

google-cloud-aiplatform (vertexai 네임스페이스)
   └─ ✅ [Confirmed] 패키지 전체가 아니라 생성형 AI 서브모듈만 폐기
      (vertexai.generative_models, language_models, vision_models,
       tuning, caching) — 2025-06-24 폐기 예고, 2026-06-24 실제 제거
      나머지 모듈(파이프라인, 피처스토어 등 MLOps 기능)은 계속 사용 권장
      ⚠️ 실무 파손 사례: "from vertexai.generative_models import
         GenerativeModel" 를 쓰던 서비스가 제거일 이후 ImportError로
         실제 중단됨 (byteiota 블로그 실사례, 🟡 Likely)
```

**Python 최소 버전**: `google-genai`는 Python 3.10 이상 필요 (PyPI + GitHub `pyproject.toml` 완전 일치, ✅ Confirmed). `requires-python = ">=3.10"`.

### 2.2 코드 전환: Before/After

구(舊) SDK → 신(新) 통합 SDK로 옮길 때 핵심 아키텍처 변화는 "모델 객체를 직접 만드는 절차형 방식"에서 "중앙 `Client` 객체를 거치는 방식"으로의 전환입니다.

```python
# 구(舊) — google.generativeai
import google.generativeai as genai
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content("...")
```

```python
# 신(新) — google-genai, Gemini Developer API 모드
from google import genai
client = genai.Client(api_key="GEMINI_API_KEY")
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="...",
)
```

```python
# 신(新) — google-genai, Vertex AI(Gemini Enterprise Agent Platform) 모드
from google import genai
client = genai.Client(
    enterprise=True,          # ⚠️ 아래 2.3절 참고 — 신규 권장 파라미터명
    project="your-gcp-project-id",
    location="us-central1",   # 또는 "global"
)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="...",
)
```

**전환 코드 요약표**:

| 항목 | 구 SDK | 신 SDK |
|---|---|---|
| 진입점 | `genai.configure()` + `GenerativeModel` | `genai.Client()` 단일 객체 |
| 콘텐츠 생성 | `model.generate_content(...)` | `client.models.generate_content(model=.., contents=..)` |
| 채팅 세션 | `model.start_chat()` | `client.chats.create()` |
| 스트리밍 | `generate_content(..., stream=True)` | `client.models.generate_content_stream(...)` |
| 함수 호출 | 명시적 활성화 필요 | 자동 함수 호출(AFC)이 기본값 |
| 안전설정 카테고리 | 예: `'HATE'` | `'HARM_CATEGORY_HATE_SPEECH'` 등 정식 명칭 |
| 설정 전달 | 개별 파라미터 인라인 | `types.GenerateContentConfig` 객체로 통합 |

⚠️ **하위호환성 층위 구분** (실무에서 헷갈리기 쉬운 지점):
- **층위 A**: `google-generativeai`(구) → `google-genai`(신) — **하위호환 아님**, 코드 재작성 필요.
- **층위 B**: `google-genai` 내부의 `vertexai=True`(구 파라미터) ↔ `enterprise=True`(신 파라미터) — **하위호환 유지됨**, 기존 코드 그대로 동작.

### 2.3 ⚠️ 예상과 다른 발견: `vertexai=True` → `enterprise=True`

조사 요청 시 가정했던 `genai.Client(vertexai=True, ...)` 파라미터는 **지금도 동작하지만 현재는 "레거시 별칭"**입니다. 2026-05-21 릴리즈(v2.6.0)부터 공식 예제가 `enterprise=True`로 전면 교체됐습니다 (Vertex AI → Gemini Enterprise Agent Platform 리브랜딩과 맞물린 변화). ✅ **[Confirmed]**, SDK 소스코드(`client.py`) 직접 확인:

> "`enterprise` (bool): Indicates whether the client should use the Gemini Enterprise Agent Platform endpoints (previously Vertex AI API)... `vertexai` (bool): Legacy flag for `enterprise`. When `enterprise` and `vertexai` are both set, and they have conflicting values, a `ValueError` will be raised."

환경변수도 마찬가지입니다:

| 구 환경변수 (레거시, 여전히 동작) | 신 환경변수 (신규 권장) |
|---|---|
| `GOOGLE_GENAI_USE_VERTEXAI` | `GOOGLE_GENAI_USE_ENTERPRISE` |
| `GOOGLE_CLOUD_PROJECT` (동일) | `GOOGLE_CLOUD_PROJECT` |
| `GOOGLE_CLOUD_LOCATION` (동일) | `GOOGLE_CLOUD_LOCATION` |

소스코드(`_api_client.py`)를 직접 읽어 확인한 우선순위 로직: 둘 다 설정되고 값이 다르면 `GOOGLE_GENAI_USE_ENTERPRISE`가 우선하며 경고(warning)가 출력됩니다. **파라미터 레벨 충돌은 예외(`ValueError`)를, 환경변수 레벨 충돌은 경고(warning) 후 계속 진행**으로 처리 방식이 다르니 유의하세요.

### 2.4 향후 Breaking Change 예고

`google-genai` README 경고 원문:

> "We are changing AFC(Automatic Function Calling) behavior in the next major version... To avoid unexpected updates, pin the SDK version to `< 3.0.0`."

**실무 권장**: `requirements.txt`에 `google-genai<3.0.0`으로 버전을 고정하세요.

---

## 3. AI Agent 개발 프레임워크

### 3.1 전체 지형도

```
                Gemini Enterprise Agent Platform (구 Vertex AI)
                                    │
        ┌─────────────────────────┼─────────────────────────┐
        │                          │                          │
   [빌드 단계]                [상호운용 표준]              [배포/운영 단계]
        │                          │                          │
   ┌────┴─────┐           ┌────────┴────────┐          ┌──────┴──────┐
   │   ADK    │           │  A2A Protocol    │          │Agent Runtime │
   │(오픈소스, │           │ (에이전트↔에이전트│          │(구 Agent    │
   │ 코드 우선)│           │  통신/발견 표준) │          │ Engine)     │
   │          │           │                  │          │완전관리형   │
   │Agent     │           │  MCP             │          │실행 런타임   │
   │Studio    │           │ (에이전트↔도구/   │          └─────────────┘
   │(low-code,│           │  데이터 연결 표준)│
   │구 Agent  │           └──────────────────┘
   │Builder)  │
   └──────────┘
```

각 도구의 역할을 명확히 구분하면:

| 도구 | 성격 | 대상 | ADK/타 프레임워크와의 관계 |
|---|---|---|---|
| **ADK (Agent Development Kit)** | 코드 우선 오픈소스 프레임워크, Apache 2.0 | 개발자 | Agent Studio/Agent Runtime의 "엔진" 역할 |
| **Agent Studio** (구 Agent Builder) | 콘솔 기반 low-code UI | 개발자(빠른 프로토타입) | ADK로 만든 것을 등록하거나, 콘솔에서 직접 생성 |
| **Agent Runtime** (구 Agent Engine, 구 Reasoning Engine) | 완전관리형 배포·운영 런타임 | 개발자/운영팀 | ADK/LangChain/LangGraph 등으로 만든 에이전트를 프로덕션 규모로 실행 |
| **Gemini Enterprise** (구 Agentspace) | no-code 엔터프라이즈 검색+에이전트 앱 | 비개발 지식근로자 | Agent Runtime에 배포된 에이전트를 최종 사용자에게 노출 |

### 3.2 ADK 기본 사용법

```bash
pip install google-adk
```

```python
from google.adk import Agent
from google.adk.tools import google_search

agent = Agent(
    name="researcher",
    model="gemini-flash-latest",
    instruction="당신은 사용자의 질문을 철저히 조사해 답하는 리서치 에이전트입니다.",
    tools=[google_search],
)
```

- 라이선스: Apache 2.0 (오픈소스) ✅ [Confirmed]
- 언어 지원: Python, Go, Java, TypeScript, Kotlin ✅ [Confirmed]
- ADK로 개발 → 단일 명령으로 Agent Runtime에 배포 가능 ✅ [Confirmed]

### 3.3 Agent Runtime이 지원하는 프레임워크

| 프레임워크 | 지원 여부 |
|---|---|
| ADK | ✅ 지원 |
| LangChain | ✅ 지원 |
| LangGraph | ✅ 지원 (전용 배포 가이드 존재) |
| LlamaIndex | ✅ 지원 |
| AG2 | ✅ 지원 |
| CrewAI | ❓ **[Uncertain]** — 2025년 자료(Google Cloud 공식 블로그 포함)는 명시하나, 2026년 리브랜딩 이후 최신 공식 문서에는 명시적으로 나열되지 않음. 실제 배포 전 최신 문서에서 재확인 필요 |

### 3.4 Function Calling — Gemini Developer API와 Vertex AI의 API 형태 차이

```
[Gemini Developer API]  (ai.google.dev, 개인 개발자/AI Studio용)
   Interactions API (client.interactions.create)
      └─ 2026-06 GA, 신규 프로젝트에 권장               ✅ Confirmed
   generateContent API (레거시, 계속 지원)               ✅ Confirmed

[Vertex AI / Gemini Enterprise Agent Platform]
   google-genai SDK (generate_content / chats.create)
      └─ 2026-08 현재 프로덕션 표준 패턴                  ✅ Confirmed
   Interactions API
      └─ 아직 Vertex AI 쪽에는 없음
         Google 엔지니어 공식 답변: "No, the Interaction
         API is currently not available in Vertex AI."    ✅ Confirmed
```

**실무 함의**: Gemini Developer API 쪽 최신 기능(Interactions API)을 Vertex AI에서 그대로 쓸 수 없는 시차가 존재합니다. 함수 호출은 아래 4.2절의 `google-genai` 패턴으로 구현하는 것이 현재 유일한 프로덕션 경로입니다.

### 3.5 Model Context Protocol (MCP) 연동

ADK는 MCP를 **클라이언트**(외부 MCP 서버의 도구 사용)와 **서버**(ADK 도구를 MCP로 노출) 양방향으로 지원합니다. ✅ [Confirmed]

```python
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters
import os

filesystem_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem",
                  os.path.abspath("./data")],
        ),
    ),
    # tool_filter=['list_directory', 'read_file'],  # 선택: 노출 도구 제한
)

agent = Agent(
    name="file_agent",
    model="gemini-flash-latest",
    instruction="파일시스템에서 요청한 정보를 찾아 답합니다.",
    tools=[filesystem_mcp],
)
```

### 3.6 LangChain / LangGraph 연동 — ⚠️ 진행 중인 전환

```bash
# 레거시 (여전히 동작하지만 공식 경고 배너 있음, 신규 프로젝트 비권장)
pip install -qU langchain-google-vertexai
```
```python
from langchain_google_vertexai import ChatVertexAI

llm = ChatVertexAI(model="gemini-2.5-flash", temperature=0, max_retries=6)
```

> "As of langchain-google-vertexai 3.2.0, certain classes are deprecated in favor of equivalents in langchain-google-genai 4.0.0, which uses the consolidated google-genai SDK." — ✅ [Confirmed]

**신규 프로젝트는 `langchain-google-genai`(통합 SDK 기반) 채택을 권장**하는 방향으로 이동 중이나, enterprise(Vertex) 모드의 정확한 초기화 코드는 이번 조사에서 원문으로 직접 확보하지 못했습니다 — ⚪ **[Unverified]**, 채택 전 최신 `langchain-google-genai` 공식 문서 확인 필요.

이는 2.3절의 SDK 파라미터 리브랜딩(`vertexai=True`→`enterprise=True`)과 같은 흐름입니다 — Google이 SDK를 `google-genai`로 통합하면서 LangChain 쪽도 Vertex 전용 클래스에서 통합 클래스로 옮겨가는 중입니다.

### 3.7 A2A(Agent2Agent) Protocol과의 관계

MCP와 A2A는 경쟁 관계가 아니라 **같은 스택에서 서로 다른 구간을 담당하는 상보적 표준**입니다:

```
에이전트 A ──[A2A: 에이전트 간 통신/발견]──▶ 에이전트 B
    │                                          │
    └──[MCP: 에이전트→도구/데이터]──▶ 도구/DB   └──[MCP]──▶ 도구/DB
```

- ADK는 A2A를 네이티브로 지원합니다: "Google released native support for A2A in Agent Development Kit (ADK)... making it easy to build A2A agents if already using ADK." ✅ [Confirmed]
- A2A는 2025년 6월 Linux Foundation에 기증되어 오픈 거버넌스 체제로 운영됩니다. 🟡 [Likely]
- 참고: 이 vault의 [[a2a-protocol-agent-to-agent-deep-dive]]에 A2A 자체에 대한 별도 Deep Dive가 있습니다.

---

## 4. 엔터프라이즈 보안·비용·관측성 Best Practice

### 4.1 인증/권한 Best Practice

**IAM 역할 최소권한 원칙**: `roles/aiplatform.admin`은 생성·삭제·배포·관리를 모두 포함하는 광범위한 역할이므로 프로덕션 실행 서비스 계정에는 부여하지 않는 것이 권장됩니다. 예측(추론) 전용 워크로드에는 `roles/aiplatform.user`, 더 좁히려면 `aiplatform.endpoints.predict` 권한만 담은 커스텀 역할을 사용하세요.

| 역할 ID | 성격 |
|---|---|
| `roles/aiplatform.admin` | 전체 리소스 완전 접근 — 프로덕션 실행 계정엔 비권장 |
| `roles/aiplatform.user` | 예측 요청 등 사용자 수준 접근 |
| `roles/aiplatform.viewer` | 읽기 전용 |
| `roles/aiplatform.tuningServiceAgent` | 모델 튜닝 작업용 (CMEK 설정 시 필요) |

**Workload Identity Federation (WIF, 워크로드 아이덴티티 연동)**: 서비스 계정 키 파일 없이 인증하는 방식.

```
[온프레미스/AWS/GitHub Actions 등 외부 워크로드]
        │  IdP(OIDC/SAML)가 발급한 단기 자격증명 제시
        ▼
[Google Cloud STS (Security Token Service)]
        │  검증 후 연합 토큰 발급 (OAuth 2.0 token exchange 규격)
        ▼
[GCP 서비스 계정 임퍼소네이션(impersonation)]
        │
        ▼
[Vertex AI 호출]
```

- **GKE**: Kubernetes 서비스 계정(KSA)을 GCP 서비스 계정(GSA)에 매핑, 메타데이터 서버로 자동 토큰 교환.
- **Cloud Run/GCE**: WIF 별도 설정 없이 "연결된(attached) 서비스 계정"만으로 키리스 인증 기본 제공.
- **외부(AWS/on-prem/GitHub Actions)**: workload identity pool + provider 구성 필요.

**ADC(Application Default Credentials) 탐색 순서**: ① `GOOGLE_APPLICATION_CREDENTIALS` 환경변수 → ② `gcloud auth application-default login`으로 만든 로컬 자격증명 파일 → ③ 메타데이터 서버가 반환하는 연결된 서비스 계정. **"프로덕션에서는 ③(연결된 서비스 계정)이 가장 권장되는 방식"**이며, 탐색 순서가 권장 순위와 같지 않다는 점에 유의하세요.

### 4.2 엔터프라이즈 보안 기능

| 기능 | 지원 여부 및 제약 | 확신도 |
|---|---|---|
| VPC-SC (VPC Service Controls) | 지원. 단, Vector Search/커스텀 훈련/Pipelines/프라이빗 엔드포인트는 추가 네트워크 구성 필요 | 🟡 Likely |
| CMEK (Customer-Managed Encryption Keys) | 지원하나 **US/EU 멀티리전 API 한정, `global` 리전은 미지원** | ✅ Confirmed |
| Private Endpoint / PSC | VPC Network Peering 기반 프라이빗 엔드포인트(GA) + PSC 기반 전용 프라이빗 엔드포인트, 두 경로 공존 | 🟡 Likely |
| 감사 로깅 | Admin Activity 로그는 항상 켜짐(비활성화 불가), **Data Access 로그(=프롬프트 호출 메타데이터)는 기본 꺼짐**, 별도 활성화 필요 | 🟡 Likely |
| 컴플라이언스 인증 | HIPAA, FedRAMP, ISO 27001/27017/27018/27701, SOC 1/2/3, PCI DSS, BSI C5:2020 | ✅ Confirmed |

⚠️ **감사 로그 관련 흔한 오해**: "요청/응답을 감사 로그가 자동 캡처한다"고 가정하면 안 됩니다. Data Access 로그에 담기는 건 **메타데이터(누가/언제/어떤 모델 호출)**이지 프롬프트·응답 본문이 아닙니다. 프롬프트 본문 자체를 캡처하려면 별도의 "Request-Response Logging"(BigQuery로 샘플링 저장)을 활성화해야 합니다.

⚠️ **HIPAA 관련 흔한 오해**: 소비자용 Gemini 앱과 AI Studio(무료 개발자 플레이그라운드)는 HIPAA 워크플로에 **사용 불가**합니다. HIPAA 준수는 "적격 GCP 프로젝트 + BAA(Business Associate Agreement) 체결 + 올바른 설정"이 전제조건입니다. 🟡 [Likely] — 법적 판단이 필요하면 Google 1차 문서 또는 담당 세일즈팀 재확인 권장.

### 4.3 비용 최적화

| 기법 | 효과 | 비고 |
|---|---|---|
| Implicit Caching(암묵적 캐싱) | 캐시된 토큰 90% 할인 | 모든 GCP 프로젝트에 기본 활성화, 별도 설정 불필요 |
| Explicit Caching(명시적 캐싱) | Gemini 2.5 계열 90%, 2.0 계열 75% 할인 | API로 수동 생성·관리, 저장 기간별 스토리지 비용 별도 발생 |
| Batch Prediction API | 실시간 대비 **50% 할인**, 24시간 내 결과 반환 | ETL, 주간 리포트, 대량 문서 처리 등 비실시간 워크로드에 적합 |
| Provisioned Throughput (PT) | 고정 요금으로 처리량 예약, 트래픽 급증 시 지연 제거 | GSU(Generative AI Scale Unit)·burndown rate 기반 과금, 트래픽이 예측 가능하고 지속적으로 높을 때만 비용 효율적 |

**실무 비용 절감 사례** 🟡 [Likely]: AI Studio는 GCP 표준 청구·계약 구조 밖에 있어 EDP(Enterprise Discount Program)와 PT 할인이 적용되지 않습니다. 한 팀은 Vertex AI로 전환하며 EDP(10%)+PT(1년 약정 시 24%)를 합쳐 **총 34% 비용 절감**을 달성했다는 실제 사례가 있습니다 ([GitHub 이슈 #6935](https://github.com/BasedHardware/omi/issues/6935)).

**예상 밖 청구 요인**:
- **Thinking token(추론 토큰)**: Gemini 3.x 계열의 내부 추론 과정도 output 토큰 요율로 과금됩니다 (예: 답변 500토큰 + 추론 4,000토큰 = 총 4,500토큰 과금). 어려운 문제가 아니면 thinking 레벨을 낮춰 비용을 통제하세요.
- **200K 토큰 임계값**: Pro 모델은 프롬프트가 200,000 토큰을 넘으면 입력 가격이 **점진적이 아니라 계단식으로 2배**가 됩니다. RAG(Retrieval-Augmented Generation) 파이프라인이 긴 문서를 조용히 끌어와 이 임계값을 넘길 수 있으니 프롬프트 길이 모니터링이 필요합니다.

### 4.4 관측성(Observability)

**Cloud Trace/Logging 연동**: Agent Runtime(구 Agent Engine)은 모델 호출·도구 실행·의사결정 지점을 아우르는 통합 트레이스를 제공하며, Cloud Trace(시각화)와 Cloud Logging(검색 가능한 구조화 로그)에 연동됩니다.

**ADK의 OpenTelemetry 계측**: ✅ [Confirmed], 공식 문서 원문 직접 확인.

> "The ADK framework includes OpenTelemetry instrumentation that collects telemetry from agent's key actions." Tracing은 `opentelemetry-exporter-otlp-proto-grpc`가 OTLP(OpenTelemetry Protocol) API로, Logging은 `opentelemetry-exporter-gcp-logging`이 Cloud Logging API로 전송합니다.

**Request-Response Logging**: 프롬프트/응답 본문 샘플을 BigQuery에 저장 — 엔드포인트에서 별도 활성화 필요, Terraform이라면 `google_vertex_ai_endpoint` 리소스의 `predict_request_response_logging_config` 블록으로 설정합니다.

---

## 5. 실무 마이그레이션 시 주의사항 (Gotcha)

### 5.1 실측 지연시간(Latency) 비교 — ⚠️ 통념과 반대되는 결과

독립 벤치마킹 서비스([Artificial Analysis](https://artificialanalysis.ai/models/gemini-2-5-flash/providers))가 Gemini 2.5 Flash 기준으로 측정한 결과, **AI Studio가 Vertex AI보다 일관되게 더 빠릅니다.** ✅ [Confirmed] (다수 모델에서 반복 확인된 패턴).

| 지표 | AI Studio | Vertex AI |
|---|---|---|
| 첫 토큰까지 시간(TTFT) | 0.48초 | 0.57초 |
| 출력 속도 (tokens/sec) | 226.0 | 184.5 |
| 500토큰 응답 전체 소요 | 2.93초 | 3.71초 |

가격은 두 플랫폼이 동일하므로 이 차이가 비용 때문은 아닙니다. **"엔터프라이즈용이니 더 빠를 것"이라는 가정은 틀릴 수 있습니다.** 다만 이는 특정 시점 스냅샷 벤치마크이므로, latency에 민감한 실시간 서비스는 전환 전 반드시 자체 워크로드로 A/B 벤치마크를 돌려보세요.

### 5.2 리전 선택의 함정

| 실수 유형 | 실제 발생 결과 |
|---|---|
| 리전에 모델 별칭 그대로 사용 | 특정 리전에서 별칭이 작동하지 않고 정확한 버전 문자열 필요 |
| 신규 프리뷰 모델을 리전 지정 엔드포인트로 호출 | 일부 프리뷰 모델은 `global` 리전에서만 사용 가능 |
| 데이터 레지던시 요구로 리전 고정 | 2026년 7월 1일부터 non-global(리전 지정) 엔드포인트가 global 대비 **약 10% 추가 요금** |
| compute와 Vertex 엔드포인트가 다른 리전 | latency 증가 |

**트레이드오프**: global 엔드포인트는 latency·가용성이 좋지만 처리 리전을 통제할 수 없어 데이터 레지던시 요구사항과 충돌할 수 있습니다.

### 5.3 인증 키 관리 — 구조적 리스크

- AI Studio 키는 기본값이 **무제한(unrestricted)** — IP/도메인 제한 없이, 공개 저장소·클라이언트 번들 등에 유출되면 누구나 사용 가능합니다.
- Vertex AI 서비스 계정 키(JSON 파일)는 **장기 유효 크리덴셜**이라 유출 시 서비스 계정을 그대로 사칭(impersonate)할 수 있고, API 키처럼 IP/도메인 제한을 걸 수 없습니다.
- **권장 대응**: 키 발급 즉시 IP/도메인 제한, Secret Manager 사용, 커스텀(비-default) 서비스 계정 사용, 예산 알림(budget alert) 설정. 가능하면 서비스 계정 키 파일 대신 4.1절의 WIF를 사용하세요.

### 5.4 Quota — "429 에러" 실사례

한 실무 사례에서, AI Studio 무료 할당량 초과로 `"429 Your billing account has exceeded its monthly spending cap"` 에러가 실제 프로덕션 서비스(LINE 챗봇)를 막았고, 이것이 Vertex AI 마이그레이션의 직접적 계기가 됐습니다. Vertex AI의 DSQ 방식도 무한한 것은 아니라서, 리전 내 전체 고객이 용량을 나눠 쓰다 소진되면 `"429 Vertex AI is overloaded"`가 발생할 수 있습니다 — 예측 가능한 서비스 수준이 필요하면 4.3절의 Provisioned Throughput을 고려하세요.

Google 직원(Gemini API 담당)의 공식 답변: **"무료 티어는 불안정하며, 실제 애플리케이션에 의존해서는 안 된다."** ✅ [Confirmed] — 무료 티어 기반 데모/사이드 프로젝트도 갑작스러운 축소에 대비한 폴백이 필요합니다.

### 5.5 2025~2026년 정책 변경 타임라인

| 시점 | 변경 내용 | 확신도 |
|---|---|---|
| 2025-06-24 | 구 Vertex AI 생성형 AI 모듈(`vertexai.generative_models` 등) 폐기 예고 | ✅ Confirmed |
| 2025-11-30 | `google-generativeai` 저장소 지원 완전 종료 | ✅ Confirmed |
| 2025-10-09 | Agentspace → Gemini Enterprise 리브랜딩 | 🟡 Likely |
| 2026-04-01 | Gemini Pro 계열이 무료 티어에서 제외 (Flash/Flash-Lite만 무료 유지) | ✅ Confirmed |
| 2026-04-22 | Vertex AI 전체 → Gemini Enterprise Agent Platform 리브랜딩 | ✅ Confirmed |
| 2026-06-24 | 구 Vertex AI 생성형 AI 모듈 실제 제거 (이미 발생) | ✅ Confirmed |
| 2026-07-01 | non-global(리전 지정) 엔드포인트에 약 10% 프리미엄 요금 적용 | ✅ Confirmed |
| **2026-09** | **AI Studio 표준 API 키(익명 키) 전면 거부** | ✅ Confirmed — 상단 "가장 먼저 알아야 할 것" 참고 |

---

## 6. 언제 무엇을 쓸 것인가 — 결정 프레임워크

```
                     [ 프로토타입 / 빠른 검증 ]
                              │
                              ▼
              ┌───────────────────────────────┐
              │   AI Studio (Gemini Dev API)   │
              │  - API 키 하나로 즉시 시작       │
              │  - latency 실측상 더 빠름        │
              │  - 단, 무료 티어는 공식적으로     │
              │    "불안정, 프로덕션 신뢰 금지"   │
              └───────────────┬───────────────┘
                              │  검증 완료, 다음 중 하나라도
                              │  해당되면 전환 검토
                              ▼
              ┌───────────────────────────────┐
              │        Vertex AI               │
              │  - 감사 가능성/거버넌스 요구      │
              │  - VPC-SC/CMEK/데이터 레지던시   │
              │  - SLA 필요                     │
              │  - EDP/PT 약정 할인 대상 트래픽   │
              │  - ADK/Agent Runtime 기반        │
              │    멀티에이전트 운영              │
              └───────────────────────────────┘
```

실무 블로그 원문: "If speed to value and simple pipelines are the priority, Gemini wins on simplicity. If the goal is auditable deployments, strict access controls, and enterprise-grade governance across teams, Vertex AI is preferable." 🟡 [Likely]

**팀 상황에 대한 권장**: 질문에서 "AI Agent 개발"이 목적이라고 하셨으므로, 프로덕션 배포·멀티에이전트 오케스트레이션·엔터프라이즈 거버넌스가 필요하다면 Vertex AI(Gemini Enterprise Agent Platform) + ADK 조합이 Google의 de facto standard입니다. 다만 **latency가 실제로 더 느릴 수 있다는 점(5.1절)과 2026-09 API 키 정책 변경(상단 참고)은 전환 계획에 반드시 반영**하세요.

---

## 7. Python 코드 예제 모음

### 7.1 설치 및 기본 초기화

```bash
pip install "google-genai<3.0.0"   # 2.4절 참고: 향후 breaking change 예고로 버전 고정 권장
```

```python
from google import genai

# ── Gemini Developer API (AI Studio) 모드 ──
client_devapi = genai.Client(api_key="GEMINI_API_KEY")

# ── Vertex AI / Gemini Enterprise Agent Platform 모드 ──
client_enterprise = genai.Client(
    enterprise=True,           # 레거시: vertexai=True 도 여전히 동작 (2.3절)
    project="your-gcp-project-id",
    location="us-central1",    # 또는 "global"
)
```

### 7.2 환경변수로 전환 (코드 무수정)

```bash
export GOOGLE_GENAI_USE_ENTERPRISE=true
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export GOOGLE_CLOUD_LOCATION="global"
```
```python
from google import genai
client = genai.Client()  # 환경변수에서 자동으로 모드 결정
```

### 7.3 서비스 계정 자격증명 명시적 전달

```python
from google import genai
from google.oauth2.service_account import Credentials

scopes = ["https://www.googleapis.com/auth/cloud-platform"]
credentials = Credentials.from_service_account_file(
    "path/to/service-account-key.json", scopes=scopes
)

client = genai.Client(
    enterprise=True,
    project="your-gcp-project-id",
    location="us-central1",
    credentials=credentials,
)
```

> ⚠️ 5.3절 참고: 가능하면 JSON 키 파일보다 Workload Identity Federation(4.1절)을 우선 검토하세요. 키 파일을 쓴다면 Secret Manager에 보관하고 절대 코드/이미지에 포함하지 마세요.

### 7.4 기본 콘텐츠 생성

```python
response = client.models.generate_content(
    model="gemini-2.5-flash",   # 구현 시점에 최신 모델 ID 재확인 (1.3절)
    contents="Vertex AI와 Gemini API의 차이를 한 문장으로 요약해줘",
)
print(response.text)
```

### 7.5 스트리밍

```python
for chunk in client.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents="스트리밍 응답 테스트를 생성해줘",
):
    print(chunk.text, end="", flush=True)
```

### 7.6 멀티턴 채팅

```python
chat = client.chats.create(model="gemini-2.5-flash")
response1 = chat.send_message("안녕, 나는 재영이야.")
response2 = chat.send_message("내 이름이 뭐라고 했지?")
print(response2.text)
```

### 7.7 함수 호출(Function Calling) — 자동(AFC) 방식

`google-genai`는 자동 함수 호출(AFC, Automatic Function Calling)이 기본값입니다. 파이썬 함수를 직접 tool로 전달하면 SDK가 호출·실행·재전달을 대신 처리합니다.

```python
from google.genai import types

def get_weather(city: str) -> dict:
    """주어진 도시의 현재 날씨를 반환합니다."""
    return {"city": city, "condition": "맑음", "temp_c": 27}

config = types.GenerateContentConfig(tools=[get_weather])
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="서울 날씨 알려줘",
    config=config,
)
print(response.text)  # AFC가 자동으로 get_weather()를 호출하고 결과를 반영
```

### 7.8 함수 호출 — 수동 방식 (세밀한 제어가 필요할 때)

```python
from google.genai import types

weather_tool = types.Tool(function_declarations=[
    types.FunctionDeclaration(
        name="get_weather",
        description="주어진 도시의 현재 날씨를 조회합니다.",
        parameters={
            "type": "OBJECT",
            "properties": {"city": {"type": "STRING", "description": "도시 이름"}},
            "required": ["city"],
        },
    )
])

chat = client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(tools=[weather_tool]),
)
response = chat.send_message("서울 날씨 어때?")

if response.function_calls:
    call = response.function_calls[0]
    result = get_weather(**call.args)
    response = chat.send_message(
        types.Part.from_function_response(name=call.name, response=result)
    )
print(response.text)
```

### 7.9 ADK 기반 Agent + MCP 도구 연동

```bash
pip install google-adk
```

```python
from google.adk import Agent
from google.adk.tools import google_search
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters
import os

filesystem_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem",
                  os.path.abspath("./data")],
        ),
    ),
)

agent = Agent(
    name="researcher",
    model="gemini-flash-latest",
    instruction=(
        "당신은 사용자의 질문을 철저히 조사해 답하는 리서치 에이전트입니다. "
        "필요하면 웹 검색과 로컬 파일시스템 도구를 사용하세요."
    ),
    tools=[google_search, filesystem_mcp],
)
```

### 7.10 LangChain 연동 (레거시 패턴, 3.6절 주의사항 참고)

```bash
pip install -qU langchain-google-vertexai
```
```python
from langchain_google_vertexai import ChatVertexAI

llm = ChatVertexAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_retries=6,
)
```

> ⚠️ 위 `langchain-google-vertexai`는 공식적으로 마이그레이션이 안내되고 있는 레거시 패턴입니다(3.6절). 신규 프로젝트라면 `langchain-google-genai` 최신 문서를 먼저 확인하세요.

---

## 8. 마이그레이션 체크리스트

1. **인증 전환**: API 키 → 서비스 계정/ADC. 가능하면 JSON 키 대신 Workload Identity Federation.
2. **SDK 전환**: `google-generativeai` 잔여 import를 전체 코드베이스에서 검색해 제거 (배포 자체가 실패하는 사례 있음, 5절 참고). `vertexai.generative_models` 등 구 Vertex AI SDK 사용 코드도 함께 점검(2026-06-24부로 이미 제거됨).
3. **리전 결정**: 데이터 레지던시 요구 여부 확인 → global vs 리전 지정 엔드포인트 선택 (비용 10% 차이, 5.2절).
4. **Quota/PT 검토**: 트래픽이 예측 가능하고 지속적으로 높다면 Provisioned Throughput 사전 구매 검토.
5. **프리뷰 모델 의존성 점검**: AI Studio에서 쓰던 프리뷰 모델이 Vertex AI allowlist 밖이면 접근 신청 리드타임 확보.
6. **비용 실측**: EDP/PT 적용 전후 비교, thinking token/200K 임계값 등 예상 밖 청구 요인 사전 점검(4.3절).
7. **관측성 설정**: Cloud Audit Logs(Data Access), Request-Response Logging, ADK OpenTelemetry 계측을 각각 별도로 활성화(4.4절 — 자동으로 켜지지 않음).
8. **Latency 실측**: 전환 전 자체 워크로드로 AI Studio 대비 A/B 벤치마크 (5.1절 — 반드시 더 빠르다는 보장 없음).
9. **API 키 정책 대응**: 2026년 9월 표준 키 거부 이전에 서비스 계정 결합 키 또는 Vertex AI 인증으로 전환 완료.

---

## ⚔️ 확인되지 않았거나 모순이 남은 항목 (투명성 고지)

| 항목 | 내용 |
|---|---|
| `google-generativeai` 지원 종료일 | GitHub 저장소 원문은 "2025-11-30"을 명시 인용(✅ Confirmed). 일부 2차 자료는 "2025-08-31"도 언급하나 해당 날짜의 직접 출처는 확보하지 못함 — 이 문서는 2025-11-30을 채택 |
| CrewAI가 Agent Runtime에서 계속 지원되는지 | 2025년 자료는 명시하나 2026년 최신 공식 문서 요약에는 미확인. 실제 채택 전 최신 문서 재확인 필요 |
| `langchain-google-genai`의 enterprise 모드 정확한 초기화 코드 | 원문 확보 실패. 채택 전 최신 공식 문서 확인 필요 |
| LangGraph 에이전트를 Agent Runtime에 배포하는 정확한 코드(`agent_engines.create` 등) | 원문 추출 실패, 배포 직전 별도 확인 필요 |
| Reddit/Hacker News 원문 커뮤니티 논의 | 검색엔진이 실제 스레드 대신 공식문서/SEO 블로그를 반복 반환해 직접 확보 실패. Google 공식 개발자 포럼(discuss.ai.google.dev) 실사용자 스레드로 대체함 — 완전한 대체는 아님 |
| Vertex AI 전체 리전 목록, 가격 페이지 원문 | 대상 페이지가 대형 SPA(단일 페이지 애플리케이션)라 WebFetch가 본문 대신 내비게이션만 반환하는 경우가 반복됨. 3차 집계 사이트와 WebSearch 스니펫으로 교차검증했으나 확신도를 낮춰 표기 |

---

## 📎 출처 목록 (핵심)

**공식 문서**
- [ai.google.dev/gemini-api/docs/api-key](https://ai.google.dev/gemini-api/docs/api-key) — API 키 정책 (2026-09 변경 공지)
- [ai.google.dev/gemini-api/docs/migrate](https://ai.google.dev/gemini-api/docs/migrate) — SDK 마이그레이션 가이드
- [ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models) — 모델 목록
- [ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing) / [rate-limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [ai.google.dev/gemini-api/terms](https://ai.google.dev/gemini-api/terms) — 데이터 사용 정책
- [cloud.google.com/blog/.../introducing-gemini-enterprise-agent-platform](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform) — 리브랜딩 공식 발표
- [docs.cloud.google.com/vertex-ai/generative-ai/docs/deprecations/genai-vertexai-sdk](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/deprecations/genai-vertexai-sdk) — 구 SDK 폐기 공지
- [docs.cloud.google.com/iam/docs/workload-identity-federation](https://docs.cloud.google.com/iam/docs/workload-identity-federation)
- [docs.cloud.google.com/docs/authentication/application-default-credentials](https://docs.cloud.google.com/docs/authentication/application-default-credentials)
- [docs.cloud.google.com/gemini/enterprise/docs/compliance-security-controls](https://docs.cloud.google.com/gemini/enterprise/docs/compliance-security-controls)
- [developers.googleblog.com/.../scale-your-ai-workloads-batch-mode-gemini-api](https://developers.googleblog.com/en/scale-your-ai-workloads-batch-mode-gemini-api/) — Batch Mode 50% 할인
- [docs.cloud.google.com/stackdriver/docs/instrumentation/ai-agent-adk](https://docs.cloud.google.com/stackdriver/docs/instrumentation/ai-agent-adk) — ADK OpenTelemetry
- [developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) — A2A 발표

**GitHub / PyPI**
- [github.com/googleapis/python-genai](https://github.com/googleapis/python-genai) — 통합 SDK 소스
- [github.com/google-gemini/deprecated-generative-ai-python](https://github.com/google-gemini/deprecated-generative-ai-python) — 구 SDK 폐기 공지
- [github.com/google/adk-python](https://github.com/google/adk-python), [adk.dev](https://adk.dev/)
- [github.com/GoogleCloudPlatform/generative-ai](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/function-calling/intro_function_calling.ipynb) — function calling 공식 노트북

**실무/커뮤니티 (교차검증용)**
- [dev.to — LINE 챗봇 마이그레이션 실사례](https://dev.to/gde/gcp-in-action-migrating-a-line-bot-from-ai-studio-to-vertex-ai-to-solve-429-errors-47jo)
- [GitHub 이슈 #6935 — 비용 절감 34% 사례](https://github.com/BasedHardware/omi/issues/6935)
- [Artificial Analysis — 독립 latency 벤치마크](https://artificialanalysis.ai/models/gemini-2-5-flash/providers)
- [discuss.ai.google.dev](https://discuss.ai.google.dev/) — Google 공식 개발자 포럼 다수 스레드

---

## 관련 노트

- [[a2a-protocol-agent-to-agent-deep-dive]] — A2A(Agent2Agent) Protocol 자체에 대한 심층 분석
- [[gemini-api-vs-vertex-ai-response-quality-factcheck]] — 같은 모델 ID 호출 시 응답 품질 차이에 관한 7개 주장 다관점 Fact-Check
- [[genai-rag-agent-llm-workflow-concepts]] — GenAI/Agent 핵심 개념 전반
- [[multi-agent-orchestration-concrete-scenarios]] — Multi-Agent Orchestration 시나리오
