---
tags: [rag, vector-search, managed-search, opensearch, vespa, cloud-comparison]
created: 2026-10-14
---

# 관리형 RAG 검색 서비스 비교: Vertex AI Search(현 Agent Search)와 대안들

> 기준일: 2026-10-14
> 범위: 한국어 노무 상담 에이전트가 법령 정보를 외부 RAG 검색 서비스(Vertex AI Search)에서 가져오는 구조를 출발점으로 삼았습니다. 같은 역할을 하는 관리형 검색 서비스와 검색 엔진(OpenSearch, Vespa 포함)을 하나의 기준으로 비교합니다.
> 검증: 문서에 담긴 사실 주장 91개를 서비스별 원문으로 다시 확인했습니다. 근거를 찾지 못한 주장은 주장마다 서로 다른 방법으로 최대 5회까지 다시 시도했습니다.

## 목차

0. 용어집과 확신도 범례
1. 검증 결과 요약
2. 출발점: 법령 상담 에이전트는 법령 정보를 어디서 가져오는가
3. 핵심 개념
   - 3.1 코퍼스
   - 3.2 RAG의 세 단계와 검색(Retrieval) 단계의 위치
   - 3.3 검색 단계를 이루는 다섯 단계 파이프라인
4. Vertex AI Search(현 Agent Search)와 데이터 스토어
5. 비슷한 서비스의 지형: 세 가지 유형
6. 비교표
   - 6.1 다섯 단계별 관리 범위
   - 6.2 과금 구조
   - 6.3 한국어 법령 문서 관점
7. 서비스별 상세
8. 시장 평가
9. 실전 예제: OpenSearch로 조문 단위 한국어 검색 구성하기
10. 주의점, 남은 모순, 조사의 한계
11. 정리
12. 출처

---

## 0. 용어집과 확신도 범례

| 용어 | 뜻 |
| --- | --- |
| RAG (Retrieval-Augmented Generation) | 문서를 검색해서 찾은 내용을 LLM 입력에 근거로 붙여 답변을 생성하는 방식 |
| 코퍼스 (corpus) | 검색이나 분석의 대상으로 모아 둔 문서 묶음 전체 |
| chunk | 검색하기 좋게 문서를 잘게 나눈 조각 |
| embedding | 텍스트의 의미를 숫자 벡터로 바꾼 것. 벡터끼리의 거리로 의미 유사도를 잰다 |
| BYO embedding (Bring Your Own) | 서비스가 만든 embedding 대신 사용자가 직접 만든 벡터를 넣어 쓰는 것 |
| BM25 | 대표적인 키워드 검색 점수 방식 |
| hybrid search | 키워드 검색 결과와 벡터(의미) 검색 결과를 합쳐 순위를 매기는 검색 |
| RRF (Reciprocal Rank Fusion) | 여러 검색 결과를 점수가 아니라 순위를 기준으로 합치는 방식 |
| reranking | 1차 검색으로 뽑은 후보를 더 정밀한 모델로 다시 정렬하는 단계 |
| cross-encoder | 질문과 문서를 한 번에 넣어 관련도를 직접 계산하는 모델. reranking에 주로 쓴다 |
| 형태소 분석 | "근로기준법에서"를 "근로기준법 + 에서"처럼 의미 단위로 나누는 처리. 한국어 키워드 검색 품질을 좌우한다 |
| nori | Lucene 계열 엔진(Elasticsearch, OpenSearch, Vespa의 Lucene linguistics)에서 쓰는 한국어 형태소 분석기 |
| bigram | 형태소 분석 없이 두 글자씩 잘라 색인하는 방식. "근로기준법"을 "근로/로기/기준/준법"으로 자른다 |
| ACL (Access Control List) | 문서 단위 접근 권한 목록 |
| MCP (Model Context Protocol) | LLM 에이전트가 외부 도구를 호출할 때 쓰는 표준 프로토콜 |
| GA (General Availability) | 정식 출시 |
| SU / CU / OCU / VCU | 용량·연산 과금 단위. SU와 CU는 Azure AI Search, OCU는 OpenSearch Serverless, VCU는 Elastic Serverless |
| SKU | 클라우드 청구서에 찍히는 개별 과금 항목 |

**확신도 범례.** 표와 본문 전체에서 이 표기를 씁니다.

| 표기 | 등급 | 판정 기준 |
| --- | --- | --- |
| ✅ | Confirmed-독립 | 서로 다른 조직(또는 저자)이 낸 출처 2개 이상의 원문에서 직접 확인함. 같은 벤더의 문서·블로그·보도자료는 개수와 관계없이 출처 1개로 셈 |
| ☑️ | Confirmed-1차 2종 | 같은 벤더 자료지만 종류가 다른 1차 자료 2종에서 각각 확인함. 예: 산문 문서와 API 스펙, 문서와 소스 코드, 가격 페이지와 SKU 카탈로그. 벤더 고유 기능처럼 독립 출처가 원리상 드문 주장에만 쓴다 |
| 🟡 | Likely | 신뢰할 만한 출처 1개의 원문만 확인함 |
| 🔄 | Synthesized | 여러 출처를 조합해서 낸 결론 |
| ❓ | Uncertain | 출처끼리 모순되거나 근거가 제한적임 |
| ⚪ | Unverified | 검증 가능한 출처를 찾지 못함 |
| 🧪 | 실측 | 로컬 환경에서 직접 실행해서 확인함 |

---

## 1. 검증 결과 요약

### 1.1 묶음별 결과

| 묶음 | 주장 수 | ✅ / ☑️ (부분 포함) | 🟡 유지 | ❓ / ⚪ 남음 | ✏️ 정정 |
| --- | --- | --- | --- | --- | --- |
| Google Agent Search, Gemini API File Search | 17 | 13 | 3 | 1 (🔄 추론 1) | 2 (비용 추정, File Search 과금) |
| AWS Bedrock Knowledge Bases, Kendra | 16 | 9 | 2 | 2 | 4 (`userContext` 동작, ACL 범위, 커넥터 제한, embedding 기본값) |
| OpenSearch | 11 | 9 | 0 | 2 (부분) | 4 (fork 계기, nori 탑재 형태, agentic memory, MCP 지원 범위) |
| Vespa | 10 | 5 (+정정 후 확인 3) | 1 | 1 (부분) | 3 (Azure zone, 가격 출처, remote embedder) |
| Azure, Elastic, OpenAI, Cohere, Pinecone, Vectara | 29 | 23 | 4 | 2 | 4 (Azure Basic 가격, jina 언어 수, OpenAI ranker, Cohere 날짜) |
| 시장·애널리스트·커뮤니티 평가 | 8 | 5 (부분 포함) | 1 | 0 | 2 (Gartner Leader 수, 비용 추정 원출처) |

### 1.2 검증 방법

```text
  1회차  공식 문서 원문 열기 (WebFetch, curl)
    │  Confirmed가 안 되면
  2회차  종류가 다른 1차 자료: API 스펙(googleapis discovery, botocore, OpenAPI),
    │    SDK 타입 정의, GitHub 소스, 가격 API(AWS Price List, Azure Retail Prices, Google SKU 카탈로그)
  3회차  독립된 3자 출처 (실사용 블로그, 기술 기사; 영어·한국어·일본어)
  4회차  봇 차단·JavaScript 페이지는 Playwright 브라우저로 열기
  5회차  web.archive.org 아카이브, 커뮤니티(Reddit 웹 검색, Hacker News API, 벤더 포럼)
  +     예제 코드는 로컬 OpenSearch 3.9.0 Docker에서 직접 실행 (🧪)
```

### 1.3 결론을 바꾼 주요 정정

| 주제 | 처음 주장 | 검증 후 |
| --- | --- | --- |
| Agent Search 비용 예시 | 월 10만 쿼리에 $400~600 | Standard **$135**, Enterprise **$360**. 원출처 블로그가 현재 가격표에 없는 단가로 계산했다 ✅ |
| Bedrock `userContext` 누락 | 사용자별 필터링이 조용히 건너뛰어진다 | **반대로 동작한다.** ACL을 켠 데이터 소스는 0건을 반환한다(fail closed) ✅ |
| OpenSearch 관리형 nori | 기본 탑재 | 관리형 도메인에서는 **선택형 plugin**이다(연결하면 blue/green 배포가 일어남). Serverless에는 기본 탑재 ☑️ |
| OpenSearch 예제 코드 | 문법 확인 필요 | 문법은 맞다. 다만 **조문이 100개를 넘으면 101번째부터 마지막 chunk 하나에 몰린다** 🧪 |
| Gartner MQ Leader | 3곳 | **6곳**이다 ✅ |
| Forrester Wave 대형 3사 | 포함 여부 모름 | Google Cloud는 Strong Performer, Microsoft와 AWS는 Contender. 다만 회사 단위 평가다 🟡 |

---

## 2. 출발점: 법령 상담 에이전트는 법령 정보를 어디서 가져오는가

이 비교의 출발점은 흔한 구조 하나입니다. 한국어 노무 상담 에이전트가 법령 정보를 직접 가져오지 않고, MCP 도구로 외부 RAG 서버를 호출하면 그 RAG 서버가 Vertex AI Search(현 Agent Search)로 검색을 수행하는 구조입니다. 에이전트 코드에는 law.go.kr 같은 법령 API를 직접 호출하는 부분이 없습니다.

```text
  LLM 에이전트 (상담 애플리케이션)
        │  ① MCP 도구 호출: 예) retrieve_rag_context
        ▼
  MCP 서버 (지식 검색용)
        │  ② 법률 코퍼스 검색 (에이전트와 별도로 운영되는 RAG 서버)
        ▼
  Vertex AI Search 데이터 스토어
        │  ③ 결과: 조각 id, 법령명, 조문 제목, 인용 정보 …
        ▼
  에이전트가 결과를 정규화 → 답변 작성 시 근거로 인용
```

| 구간 | 하는 일 |
| --- | --- |
| ① 도구 호출 | 에이전트가 검색 도구를 MCP로 호출한다. 검색 provider는 설정상 `vertex_ai_search` 같은 라벨로 구분된다 |
| ② 검색 | RAG 서버가 데이터 스토어에 질의를 보낸다. 데이터 스토어에 무엇이 들어 있는지는 RAG 서버 쪽이 결정한다 |
| ③ 결과 정규화 | 응답을 검색 근거와 인용 정보로 바꿔 답변에 붙인다. 조각마다 `vertex-source:<hex>` 같은 id가 붙는다 |
| ③ 민감정보 처리 | 법령 검색 결과는 "공개 법률 코퍼스"로 보고 민감정보 스크리닝을 건너뛰도록 설계하는 경우가 많다 |

코드에 `vertex_ai_search` 같은 라벨이 남아 있는 것은 자연스러운 일입니다. 2026-04-22에 바뀐 것은 문서상 제품 이름뿐이고, 콘솔 화면은 지금도 "Vertex AI Search and AI Applications", API는 Discovery Engine 이름을 그대로 쓰기 때문입니다 ✅.

**이런 구조에서 따로 확인해야 하는 것**

- 원천 데이터: 설계 문서가 국가법령정보 Open API(open.law.go.kr), 국가법령정보센터(law.go.kr), 고용노동부 행정해석과 질의회시집을 공식 출처로 권장하더라도, RAG 서버가 실제로 이 출처들을 수집해 데이터 스토어에 넣는지는 RAG 서버 쪽 코드에서 따로 확인해야 합니다.
- 서버 배치: 검색 도구가 어느 MCP 서버에서 제공되는지는 배포 설정에 따라 달라질 수 있습니다.
- 리전: 데이터 스토어의 리전(global, us, eu 중 어디인지)은 에이전트 코드에 나오지 않는 경우가 많습니다.

---

## 3. 핵심 개념

### 3.1 코퍼스

코퍼스(corpus)는 **검색이나 분석의 대상으로 모아 둔 문서 묶음 전체**입니다. 말뭉치를 뜻하는 라틴어에서 왔고, 검색 분야에서는 "대상 문서 집합"이라는 뜻으로 굳어졌습니다. "법률 코퍼스"는 RAG 서버가 검색할 수 있도록 미리 모아서 색인해 둔 법령·해석 문서 전체를 가리킵니다.

```text
  원천 문서들                         코퍼스 (색인된 문서 묶음)            검색
  ─────────────                      ──────────────────────────         ──────
  근로기준법 조문      ┐
  최저임금법 시행령    ├─ 수집·분할 ─▶  Agent Search 데이터 스토어    ◀─ 검색 도구 호출
  고용노동부 질의회시  ┘    ·색인         (조각마다 id, 법령명, 조문 제목)      "연차수당 계산 기준?"
                                                                           → 관련 조각 몇 개 반환
```

- **수집**: 원천 문서를 가져옵니다.
- **분할·색인**: 문서를 조각(chunk)으로 나누고, 조각마다 id와 메타데이터를 붙입니다. `vertex-source:<hex>` 같은 값이 바로 이런 조각의 id입니다.
- **검색**: 질문이 들어오면 코퍼스 안에서 관련 조각만 찾아 돌려줍니다.

이 구조에서 두 가지 결론이 나옵니다.

1. **코퍼스에 없는 문서는 검색 결과에도 나올 수 없습니다.** 예를 들어 2026년에 개정된 시행령이 코퍼스에 반영되지 않았다면, 검색이 아무리 정교해도 옛 조문만 돌아옵니다. 그래서 "법령 정보를 어디서 가져오는가"라는 질문은 결국 "이 코퍼스를 무엇으로 채웠는가"라는 질문이 됩니다.
2. 법령 검색 결과의 민감정보 스크리닝을 건너뛰는 근거도 코퍼스의 성격에 있습니다. 공개 법령만 모은 집합이므로 고객 개인정보가 섞일 일이 없다고 전제한 것입니다.

### 3.2 RAG의 세 단계와 검색(Retrieval) 단계의 위치

RAG는 "검색 → 프롬프트에 붙이기 → LLM이 답변 생성"의 세 단계로 이루어집니다. **데이터 스토어는 RAG 시스템 전체가 아니라 그중 검색(Retrieval) 부분만 맡습니다.** 위 구조에서는 이 세 단계를 서로 다른 구성 요소가 나눠 맡습니다.

```text
  R  Retrieval (검색)        A  Augmented (보강)               G  Generation (생성)
  ───────────────────       ──────────────────────────       ─────────────────────
  Agent Search              RAG 서버 → 에이전트                에이전트의 LLM
  데이터 스토어               검색 결과를 정리해 도구 결과로       도구 결과를 근거로
  "관련 조각 찾기"            돌려주고, LLM 컨텍스트에 들어감      상담 답변을 작성
```

| 단계 | 담당 |
| --- | --- |
| R 검색 | Agent Search 데이터 스토어 |
| A 보강 | RAG 서버(MCP 검색 도구)와 에이전트의 결과 정규화 |
| G 생성 | 에이전트의 LLM(답변 작성과 인용 처리) |

**판단 기준**: 어떤 구성 요소를 "RAG 시스템"이라고 부를 수 있는지는 **답변을 생성하는 LLM까지 포함하는지**로 판단합니다. 데이터 스토어는 질문을 받으면 관련 조각만 돌려주고 답변 문장은 만들지 않으므로 검색 엔진에 해당합니다.

- Agent Search에도 검색 결과를 요약한 답변을 생성하는 `answer` 메서드가 있습니다 ☑️. 하지만 이 구조에서는 결과를 조각과 인용 id로 받아 에이전트의 LLM이 직접 답변을 씁니다. 따라서 데이터 스토어는 검색 역할로만 쓰입니다.
- 코드에 `legal_rag_runtime`, `retrieve_rag_context`처럼 "rag"가 붙은 이름이 많더라도, 이 이름들은 "RAG 파이프라인에서 검색을 맡는 부분"이라는 뜻이고, 그 도구 하나가 RAG 전체라는 뜻은 아닙니다.

### 3.3 검색 단계를 이루는 다섯 단계 파이프라인

검색(Retrieval) 단계를 직접 구현하려면 다섯 단계를 거쳐야 합니다.

```text
  문서 → [1 chunking] → [2 embedding] → [3 저장·색인] → [4 검색] → [5 reranking] → LLM
```

| 단계 | 하는 일 | 직접 구현할 때 쓰는 도구 예시 |
| --- | --- | --- |
| 1. chunking | 문서를 검색 단위 조각으로 자른다 | LangChain text splitter |
| 2. embedding | 조각을 벡터로 바꾼다 | OpenAI, bge 같은 embedding 모델 |
| 3. 저장·색인 | 벡터와 원문을 색인해 저장한다 | pgvector, Pinecone 같은 벡터 DB |
| 4. 검색 | 질의와 비슷한 조각을 찾는다. 키워드 검색과 벡터 검색을 섞으면 hybrid | ANN 검색과 키워드 검색 병합 |
| 5. reranking | 후보를 정밀 모델로 다시 정렬한다 | Cohere Rerank, cross-encoder |

관리형 서비스는 이 다섯 단계를 묶어서 제공합니다. 개발자는 문서를 넣고 검색 API를 호출하기만 하면 됩니다. 이때 얻는 것과 잃는 것은 다음과 같습니다.

| 구분 | 내용 | 예시 |
| --- | --- | --- |
| ✅ 얻는 것 | 파이프라인을 만들고 운영하는 비용이 크게 줄어든다 | 법령이 개정되면 문서를 다시 import하는 것으로 끝난다. 재색인과 embedding 재계산을 직접 관리하지 않아도 된다 |
| ❌ 잃는 것 | 내부 동작이 잘 보이지 않는다 | "근로기준법 제60조가 왜 검색되지 않았나"를 조사한다고 하자. 직접 구현했다면 chunk 경계와 유사도 점수를 바로 열어 볼 수 있다. 관리형에서는 노출된 설정과 결과만 보고 추정해야 한다 |
| ⚠️ 법령 문서의 특수성 | 자동 chunking이 조문 중간을 자를 수 있다 | 실무에서는 import하기 전에 조문 하나를 문서 하나로 미리 쪼개서 넣는 방식을 자주 쓴다 |

이 trade-off는 여러 독립 출처가 같은 취지로 설명합니다 ✅. Google codelab은 "out of the box RAG가 빨리 시작하게 해 주고, DIY API가 더 많은 투명성과 통제를 준다"고 썼습니다. Atlan은 "Knowledge Bases는 며칠, 직접 만든 RAG는 몇 주에서 몇 달"이 걸린다고 비교했습니다. 다만 **"관리형은 chunking을 통제할 수 없다"는 말은 틀렸습니다.** Bedrock, OpenAI, Agent Search 모두 chunking 옵션을 제공하므로 "덜 통제한다"까지만 맞습니다 ✅. "prompt 구성을 덜 통제한다"는 말은 검색과 답변 생성을 한 번에 하는 retrieve-and-generate 방식에만 해당합니다. 검색 결과만 받는 방식(2절 구조가 쓰는 방식)에서는 prompt를 직접 구성합니다 🟡.

---

## 4. Vertex AI Search(현 Agent Search)와 데이터 스토어

**이름 변경** ✅: 2026-04-22에 Vertex AI는 "Gemini Enterprise Agent Platform"으로 바뀌었고, Vertex AI Search는 "Agent Search"로 바뀌었습니다. 공식 release notes와 독립 출처 2곳(일본 Google Cloud 파트너사 G-gen의 Next '26 현장 리포트, Let's Data Science 기사)이 일치합니다. 다만 바뀐 범위는 **문서 세트**입니다. 콘솔 UI와 API(Discovery Engine)는 옛 이름을 그대로 씁니다.

**데이터 스토어(data store)**는 이 서비스 안에서 검색 대상 문서를 담아 두는 저장소이자 색인 단위입니다. 코퍼스를 Google Cloud 안에 실제로 만들어 둔 형태라고 보면 됩니다.

```text
  Google Cloud 프로젝트
   └─ Agent Search (구 Vertex AI Search)
       ├─ 데이터 스토어 A  (예: 법령·행정해석 문서)   ← 문서 저장 + 자동 parsing·chunking·embedding·색인
       ├─ 데이터 스토어 B  (예: 내부 상담 사례)
       └─ 검색 앱(app / engine)  ── 하나 이상의 데이터 스토어를 묶어 검색 API로 노출
                    ▲
                    │ 검색 요청 ("연차수당 계산 기준")
              RAG 서버 (검색 도구를 제공하는 MCP 서버)
```

**문서 투입 방식** ☑️ (문서와 API 스펙 `ImportDocumentsRequest`로 확인)

| 방식 | 예시 |
| --- | --- |
| Cloud Storage 가져오기 | PDF, HTML, JSONL로 정리한 법령 문서를 버킷에 올린 뒤 가져온다 |
| BigQuery 테이블 | 조문을 행 단위로 정리한 테이블 |
| 웹사이트 | 지정한 도메인의 공개 페이지. 단, **Enterprise 기능이 켜진 앱**에만 붙일 수 있다 |
| 그 밖의 소스 | Google Drive, Cloud SQL, Spanner, Firestore, AlloyDB, Bigtable |

**확인된 세부 사항**

| 항목 | 내용 | 확신도 |
| --- | --- | --- |
| chunking | layout parser가 파싱하고 `layoutBasedChunkingConfig`가 자른다. chunk 크기는 100~500 token이고 기본값은 500. `includeAncestorHeadings`(기본값 false)를 켜면 장·절 제목을 chunk에 함께 넣는다 | ☑️ 문서 + API 스펙 |
| chunk 설정 변경 | **데이터 스토어를 만든 뒤에는 바꿀 수 없다.** 문서에 "can't be changed"로 적혀 있고, API 스펙에도 `chunking_config`가 immutable로 되어 있다. parsing 설정은 바꿀 수 있다 | ☑️ |
| 검색 방식 | 키워드와 의미 검색을 결합한 hybrid 검색. API 스펙에 BM25 `keyword_similarity_score`와 `semantic_similarity_score`가 있다 | ☑️ |
| BYO embedding | Preview 단계이고 1~768차원만 된다. structured 데이터와, 메타데이터가 있는 unstructured 데이터에만 쓸 수 있다 | 🟡 문서만 |
| Ranking API | 별도로 과금된다(1,000건당 $1.00, 쿼리 1건당 문서 최대 100개) | ☑️ 가격 페이지 + SKU |
| 요약 답변 | `answer` 메서드와 `summarySpec`이 있다 | ☑️ |
| 한국어 | ko-KR을 Search, Answers, Ranking API, Grounded generation 모두에서 지원한다. 헬스케어 검색은 2026-05-15부로 제품 전체가 deprecated됐다 | 🟡 문서 언어표만 |
| 리전 | `global`, `us`, `eu`만 있고 **한국 리전은 없다.** 문서에 "multi-region API는 global API와 결과가 같지 않을 수 있다"고 명시되어 있다 | ☑️ 문서 + API 스펙 |
| 관련 제품 | RAG Engine(구 Vertex AI RAG Engine)이 같은 플랫폼에 있다 ✅. Agent Retrieval은 구 Vector Search 2.0이다 🟡 | ✅ / 🟡 |

---

## 5. 비슷한 서비스의 지형: 세 가지 유형

Agent Search와 비슷한 역할을 하는 서비스와 엔진은 **"다섯 단계 중 얼마나 많이 맡기고, 얼마나 많이 직접 설정하는가"**를 기준으로 세 유형으로 나뉩니다 🔄.

```text
  맡기는 범위가 넓음 ◀────────────────────────────────────────────▶ 직접 설정하는 범위가 넓음

  [A] 완전 관리형 RAG 검색          [B] 검색 엔진형                       [C] 부품형
  문서를 넣고 API만 호출             엔진 안에서 다섯 단계를 구성하되       특정 단계만 제공
                                   사용자가 파이프라인을 설정
  ─────────────────────           ──────────────────────────────       ──────────────
  Google Agent Search              Azure AI Search                      Cohere
  Bedrock Managed KB               Elastic                              (Embed, Rerank)
  OpenAI File Search               OpenSearch
  Gemini API File Search           Vespa
  Pinecone Assistant
  Vectara
  (Amazon Kendra: 신규 고객 불가)
```

| 유형 | 특징 | 적합한 상황 |
| --- | --- | --- |
| A. 완전 관리형 | 운영 부담이 가장 적다. 대신 chunking과 검색 전략을 덜 통제하고, 결과가 왜 그렇게 나왔는지 보기 어렵다 | 빨리 시작해야 하고 검색 품질을 세밀하게 튜닝할 필요가 크지 않을 때 |
| B. 검색 엔진형 | 형태소 분석기, chunk 규칙, 점수 합산 방식, reranking까지 직접 정한다. 그만큼 설계와 운영 부담이 크다 | 한국어 키워드 정확도나 조문 단위 제어처럼 검색 품질을 세밀하게 다뤄야 할 때 |
| C. 부품형 | embedding이나 reranking 한 단계만 API로 제공한다 | 다른 유형의 파이프라인에 품질 좋은 단계 하나를 끼워 넣을 때 |

**B 유형 안의 계보**

- **OpenSearch의 출발** ✅
  - 2021-01-14: Elastic이 7.11부터 SSPL과 Elastic License의 이중 라이선스로 바꾼다고 발표했습니다.
  - 2021-01-21: AWS가 "지난주 Elastic의 발표"를 직접 언급하면서 7.10 기반 Apache 2.0 fork를 만들겠다고 발표했습니다.
  - 2021-04-12: Elasticsearch 7.10.2를 바탕으로 한 OpenSearch 프로젝트가 공개됐습니다.
  - 2024-09-16: Linux Foundation 산하 OpenSearch Software Foundation으로 이관됐습니다.
- Elastic과 OpenSearch는 이런 계보 때문에 API와 운영 방식이 비슷하고, 둘 다 nori를 씁니다.
- **Vespa** ✅: Yahoo가 내부 검색과 추천에 쓰던 엔진입니다. 2017년에 오픈소스로 공개했고, 2023-10-04에 Vespa.ai라는 별도 회사로 분리했습니다. Yahoo는 지분과 이사회 1석을 가진 최대 고객으로 남았습니다.
- **B 유형 엔진은 A 유형 서비스의 내부 부품으로도 쓰입니다.** 예를 들어 기존 방식 Bedrock Knowledge Bases는 vector store로 OpenSearch Serverless를 고를 수 있습니다.

**2025~2026년 지형 변화**: 2024~2025년에 나온 비교 자료는 이름과 구성이 낡았다고 보고 읽어야 합니다.

| 시점 | 변화 | 확신도 |
| --- | --- | --- |
| 2025-10-14 | OpenSearch 3.3에서 agentic search와 agentic memory가 GA | ✅ |
| 2025-11-06 | Gemini API File Search 출시 | ✅ |
| 2025-11-25 | Amazon OpenSearch Service에서 agentic search 제공 시작 | ✅ |
| 2026-02-16 | Vespa Kubernetes Operator 출시(enterprise 전용) | ☑️ |
| 2026-04-22 | Vertex AI Search가 Agent Search로 이름 변경(문서 기준) | ✅ |
| 2026-05-15 | Agent Search 헬스케어 검색 deprecated | 🟡 |
| 2026-05-27 | Vespa coding agent용 skills 공개(Elasticsearch 이관 skill 포함) | ☑️ |
| 2026-05-28 | OpenSearch Serverless NextGen collection GA | ☑️ |
| 2026-06-17 | AWS Bedrock Managed Knowledge Base GA | ✅ |
| 2026-06-30 / 07-30 | Amazon Kendra 유지보수 모드 진입, 07-30부터 신규 고객 불가 | ✅ |
| 2026-08-05 | OpenSearch 3.8: 기본 agent 4종 모두 MCP 지원, gRPC streaming | ☑️ |
| 2026-08-26 | OpenAI Assistants API 종료. File Search는 Responses API로 사용 | ✅ |
| 2026-08-31 | Pinecone에서 cohere-rerank-3.5 요청을 rerank-4-fast로 자동 연결 | ✅ |
| 2026-09-13 | Azure AI Search Serverless(preview) 과금 시작 | ☑️ |
| 2026-09-30 | 기존 방식 Bedrock KB에서 Confluence·SharePoint·Salesforce·Web Crawler 커넥터 신규 생성 중단 | 🟡 |
| 2026-09-30 | Cohere Embed 5 출시(Bedrock은 출시 채널에 없음) | ✅ |

---

## 6. 비교표

### 6.1 다섯 단계별 관리 범위

기호: **●** 완전 관리 또는 핵심 기능, **◐** 관리되지만 사용자가 설정·조정 가능, **○** 사용자가 직접 구성, **?** 확인 못 함. 확신도 기호는 0절 범례를 따릅니다.

| 유형 | 서비스 | 1. Chunking | 2. Embedding | 3. 저장·색인 | 4. 검색 | 5. Reranking |
| --- | --- | --- | --- | --- | --- | --- |
| A | **Google Agent Search** | ◐ 100~500 token(기본 500), 상위 제목 포함 옵션, 생성 후 변경 불가 ☑️ | ● 기본 제공. BYO는 Preview, 768차원 이하 🟡 | ● | hybrid(BM25 + semantic) ☑️ | ● Ranking API(별도 과금) ☑️ |
| A | **Bedrock Managed KB** | ◐ 기본은 300 token에 overlap 20% / fixed / 없음. semantic 불가, parser 선택 불가 ✅. hierarchical 지원 여부는 AWS 문서끼리 다름 ❓. 설정 단위는 데이터 소스이고, 연결 후에는 변경 불가 🟡 | ● **기본값은 서비스가 관리하는 모델(모델 선택 불필요)** ✅. 직접 고르면 Titan V2, Cohere v3·v4, Nova(1024차원 🟡)와 TwelveLabs Marengo(멀티모달) | ● AWS 관리형 저장소만(외부 vector DB 불가) ✅ | 항상 hybrid, semantic 단독 모드 없음 ✅ | ● MANAGED / CUSTOM / NONE. embedding을 직접 고르면 관리형 reranker는 못 씀 ✅ |
| A | Bedrock KB (기존 방식) | ◐ 위 방식 + semantic chunking | ◐ 모델 선택 | ○ OpenSearch Serverless, Aurora PostgreSQL Serverless, Neptune Analytics, S3 Vectors 중 선택 🟡 | semantic / hybrid 선택 | ◐ rerank 모델 선택 |
| A | Amazon Kendra | ● | ● | ● | 키워드 / semantic / hybrid | ● (2026-07-30부터 신규 고객 불가 ✅) |
| A | **OpenAI File Search** | ◐ 기본 800 token, overlap 400, 범위 100~4096 ☑️ | ● 모델 비공개 | ● vector store | hybrid. RRF 가중치(`embedding_weight`/`text_weight`) 조정 ☑️ | ● `ranker`(허용 값이 API마다 다름), `score_threshold` ☑️ |
| A | **Gemini API File Search** | ◐ `max_tokens_per_chunk`, `max_overlap_tokens`. 단위는 공백으로 나눈 단어 수 ☑️ | ◐ 텍스트는 gemini-embedding-001, 이미지·멀티모달은 -2 🟡 | ● | **semantic만. hybrid 옵션 없음** ☑️ | ? |
| A | **Pinecone Assistant** | ● ☑️ | ● ☑️ | ● ☑️ | ? | ? |
| A | **Vectara** | ◐ 기본은 문장 단위. section 경계를 넘지 않음. `CoreDocument`로 미리 자른 chunk 업로드 ☑️ | ● Boomerang ✅ | ● | hybrid(`lexical_interpolation` 0.0~1.0) ☑️ | ● Multilingual Reranker v1(100개 이상 언어) |
| B | **Azure AI Search** | ○ Text Split skill 등으로 직접 구성 | ○ Azure OpenAI, Foundry, custom skill 연결 | ● (용량은 직접 정함) | BM25 / 벡터 / hybrid(RRF) | ◐ semantic ranker(유료 옵션, 다국어 모델 🟡) |
| B | **Elastic** (`semantic_text`) | ◐ 자동 chunking. **기본 전략은 `sentence`**, `word`(120단어, overlap 40) 등은 `chunking_settings`로 선택 ☑️ | ◐ inference endpoint 선택. 지정하지 않으면 업그레이드 때 기본 모델이 바뀔 수 있다고 경고 ☑️ | ● / ○ (Serverless / Hosted) | BM25 + 벡터 hybrid | ◐ 외부·내장 rerank 연결 |
| B | **OpenSearch** | ◐ `text_chunking` ingest processor(2.13+). `fixed_token_length`, `fixed_char_length`, `delimiter` ✅. 기본 `max_chunk_limit`은 100 🧪 | ◐ ML Commons에 local 모델을 올리거나 remote connector(Bedrock, OpenAI, Cohere, SageMaker, Vertex AI)로 연결 ✅ | ● k-NN 벡터 색인 + 역색인 | hybrid query(2.11+), min_max 정규화 또는 RRF ✅. 3.3부터 agentic search ✅ | ◐ rerank processor(2.12+). `ml_opensearch`는 OpenSearch가 제공하는 cross-encoder를 클러스터 안에서 사용, `by_field`는 2.18+ ☑️. late interaction(ColBERT 등) 재정렬은 3.3+이고 `ml_inference` processor를 씀 ☑️ |
| B | **Vespa** | ◐ indexing language의 `chunk`(8.520+). `sentence`, `fixed-length`, 직접 만든 chunker | ◐ 엔진 안 ONNX embedder(HF, ColBERT, SPLADE) 또는 remote embedder(OpenAI·Mistral은 8.678+, Voyage). **endpoint 변경 가능** ☑️ | ● tensor field + HNSW + 역색인. 문서 하나에 chunk별 벡터 | 한 YQL 쿼리에서 `weakAnd`(키워드), `nearestNeighbor`(벡터), filter를 함께 사용 ☑️ | ● first/second/global-phase를 엔진 안에서 정의 ☑️ |
| C | **Cohere** | ? | ● Embed(Embed 5는 2026-09-30 출시 ✅) | ◐ Compass(Compass Cloud는 private beta ✅) | ? | ● Rerank v4.0 pro·fast, multilingual ✅ |

**B 유형 안에서 OpenSearch와 Vespa는 성격이 다릅니다** ☑️

- **OpenSearch는 reranking을 "검색 뒤에 붙이는 처리 단계"로 다룹니다.** search pipeline에 rerank processor를 끼워 넣는 구조입니다.
- **Vespa는 ranking 자체를 엔진의 중심 기능으로 다룹니다.**
  - first-phase: 가벼운 점수로 후보를 넓게 뽑습니다.
  - second-phase: **content node마다** 상위 100건(기본값)을 다시 계산합니다.
  - global-phase: stateless container에서 schema마다 전체 상위 100건(기본값, `rerank-count`로 조정)을 cross-encoder로 재정렬합니다.
  - 공식 문서는 global-phase가 "ONNX 추론에 최적화"되어 있고 "대표 용도가 cross-encoder 재정렬"이라고 명시합니다. 이 기본값 100은 소스 코드(`GlobalPhaseSetup.java`, `indexproperties.cpp`)에서도 확인됩니다.
- Vespa는 8.530부터 **layered ranking**을 지원합니다 ☑️. 문서 단위로 후보를 고른 뒤 그 안의 chunk 단위로 다시 점수를 매기고, `select-elements-by`로 가장 좋은 chunk만 돌려줄 수 있습니다. 예를 들어 "근로기준법" 문서를 고른 뒤 그 안에서 제60조 chunk만 돌려주는 식입니다.

### 6.2 과금 구조

금액은 참고용이고, 구조를 중심으로 봅니다.

| 유형 | 서비스 | 과금 구조 | 최소 비용 | 확신도 |
| --- | --- | --- | --- | --- |
| A | Agent Search | **General**: 쿼리 1,000건당 Standard $1.50 / Enterprise $4.00, 원본 데이터 GiB당 월 $5.00. 월 1만 쿼리와 10GiB까지 무료. **Configurable**: 월 구독(QPM + 저장량)과 add-on 종량. Layout Parser는 1,000건당 $10, Ranking은 1,000건당 $1 | General: 없음. Configurable: 최소 1,000 QPM + 50GB 🟡 | ☑️ 가격 페이지 + SKU |
| A | Bedrock Managed KB | 원본 데이터 GB당 월 $5, Retrieve 1,000건당 $1. Agentic Retrieve는 1,000건당 $4 추가. 관리형 parsing·embedding·rerank는 $0 | 없음 | ✅ |
| A | Bedrock KB (기존 방식) | 고른 vector store 요금 + embedding·rerank 모델 요금 | OpenSearch Serverless를 쓰면 아래 OpenSearch 행 참조 | 🔄 |
| A | Kendra | index를 만든 시점부터 지울 때까지 시간당 과금. 쿼리가 없어도 과금됨 | 있음 | ✅ |
| A | OpenAI File Search | vector store 저장은 1GB까지 무료, 이후 GB당 하루 $0.10. 도구 호출은 1,000회당 $2.50(Responses API에만 적용) | 없음 | ☑️ |
| A | Gemini File Search | 색인할 때 embedding 100만 token당 $0.15. 저장과 쿼리 시 embedding은 무료. **단, 검색된 문서 token은 모델의 일반 입력 token으로 과금됨** | 없음 | ☑️ |
| A | Pinecone Assistant | 플랜별 월 최소액 Starter $0 / Builder $20(정액, 한도를 넘으면 과금 대신 차단) / Standard $50 / Enterprise $500. ingestion unit당 $0.0005, context token 100만 개당 $5, GB당 월 $3 | 플랜별 | ☑️ |
| A | Vectara | 연간 계약: SaaS $100K~, VPC $250K~, On-prem $500K~. 2022년 무료 Growth 플랜 → 2024년 월 $100 → 2025-08~09 사이 연 $100K로 바뀜 | $100K/년 | ✅ |
| B | Azure AI Search | **Dedicated**: SU(replica × partition)마다 시간당 고정 요금, 쿼리당 과금 없음 ☑️. Basic은 $0.101/SU·시간 = **$73.73/SU·월**(Korea Central 포함) ☑️. **Serverless(preview)**: CU 시간당 + GB당 월 요금, 2026-09-13부터 과금 ☑️. semantic ranker, agentic retrieval, AI enrichment, vectorizer는 별도 | Dedicated는 일시 정지가 안 되고 **삭제해야 과금이 멈춤** ☑️. 같은 등급에서 용량을 2배로 늘리면 비용은 2배를 넘는다 🟡 | ☑️ |
| B | Elastic Serverless | Ingest·Search·ML VCU-hour + GB당 저장 + Inference Service 토큰 | 명시된 최소액은 없다. 다만 baseline 검색 자원이 늘 유지되고, 유휴 시간에도 낮은 요율로 과금된다 | ☑️ |
| B | **OpenSearch (Amazon 관리형)** | Service: 인스턴스 시간당. Serverless: indexing·search OCU 시간당 + 저장량 | **Classic**: 계정의 첫 collection 기준으로 최소 2 OCU. us-east-1에서 $0.24 × 2 × 730h = **$350.40/월**, 이중화를 끄면 $175.20 ✅. **서울은 $0.293/OCU-h라 약 $428/월** ☑️. vector search collection은 search·time series collection과 OCU를 공유하지 않으므로 둘 다 쓰면 하한이 2배 ☑️. **NextGen**: 최소 OCU 0, 10분간 요청이 없으면 연산 과금 중단, 저장 비용은 계속 ☑️ | ✅ / ☑️ |
| B | **Vespa Cloud** | 할당한 리소스에 시간당 과금. 시작 단가는 Basic $0.10/vCPU-h, $0.01/GB 메모리-h, $0.0004/GB 디스크-h. Commercial $0.145 / $0.0145 / $0.0005(24/7 지원 포함). Enterprise $0.18 / $0.018 / $0.0007. Startup $0.05 / $0.005 / $0.0002(dev zone 전용). 단가는 사용량이 늘면 최대 50%까지 선형으로 내려가고, 연간 약정 시 15% 할인 | Enterprise는 월 $20,000 최소. quota 상한은 Trial 시간당 $2, 그 밖의 플랜 시간당 $10 | 🟡 (공식 가격 계산기 원문. apis.io는 공식 페이지를 옮겨 적은 것이라 독립 출처가 아님) |
| C | Cohere | Rerank는 search unit(쿼리 1건, 문서 최대 100개) 단위 🟡. Model Vault는 인스턴스당 시간 과금 ☑️. Compass와 North는 영업 문의 | 확인 못 함 | 🟡 / ☑️ |

**과금 구조의 두 계열** 🔄

- **사용한 만큼 내는 계열**(Agent Search General, Bedrock Managed KB, OpenAI, Gemini, OpenSearch NextGen): 트래픽이 적거나 들쭉날쭉할 때 유리합니다.
- **용량을 잡아 두고 내는 계열**(Azure Dedicated, OpenSearch Classic, Vespa Cloud, Kendra): 쿼리가 없어도 비용이 나갑니다. 대신 트래픽이 많고 일정하면 쿼리당 단가가 낮아질 수 있습니다.

**계산 예시: Agent Search에서 월 10만 쿼리** ✅ (공식 SKU 계산과 독립 출처 Digital Applied의 계산이 일치)

| 구성 | 계산 | 월 비용 |
| --- | --- | --- |
| Standard | (100,000 − 무료 10,000) / 1,000 × $1.50 | **$135** |
| Enterprise | 90 × $4.00 | **$360** |
| Enterprise + Advanced Generative Answers | $360 + 100 × $4.00 | **약 $760** |

"월 10만 쿼리에 $400~600"이라는 수치가 블로그에 돌고 있습니다. 원출처는 CloudZero이고, costbench는 이를 그대로 옮겨 인용했습니다. 이 수치의 바탕이 된 Standard $4.00 / Advanced $6.00 단가는 현재 가격표에 없으므로, 이 수치는 쓰지 않습니다.

### 6.3 한국어 법령 문서 관점

법령처럼 조문 단위 구조가 중요한 한국어 문서에서는 다음 세 가지가 판단을 좌우합니다 🔄.

```text
  ① 한국어 형태소 분석  →  "근로기준법에서"처럼 조사가 붙은 말을 키워드 검색이 제대로 찾는가
  ② 미리 자른 chunk 투입 →  조문 하나를 chunk 하나로 넣을 수 있는가
  ③ 한국 리전           →  데이터와 질의가 국내에 머무는가 (저장과 처리를 나눠서 본다)
```

| 유형 | 서비스 | ① 형태소 분석 | 한국어 embedding / rerank | ③ 한국 리전 | ② 조문 단위 제어 |
| --- | --- | --- | --- | --- | --- |
| A | Agent Search | 확인 못 함 | ko-KR 공식 지원 🟡 | ❌ global/us/eu만 ☑️ | 장·절 제목 포함 옵션, 최대 500 token, 생성 후 변경 불가 |
| A | Bedrock Managed KB | 확인 못 함 | 기본은 관리형 모델. 직접 고르면 Cohere v3·v4 | ❌ 서울 없음(us-east-1, us-west-2, eu-west-1/2, eu-central-1, ap-northeast-1, ap-southeast-2, GovCloud) ☑️ | "no chunking" 옵션 ✅ |
| A | Bedrock KB (기존 방식) | OpenSearch Serverless를 고르면 nori가 기본 탑재됨 ☑️. 다만 KB의 hybrid 검색이 nori 분석기를 쓰는지는 ⚪ | 서울 단일 리전 embedding은 **Titan V2뿐**. Cohere Embed v4는 Global cross-region inference로만 사용 가능, Cohere Multilingual은 서울에 없음 ☑️ | ✅ 서울 사용 가능 ☑️ | "no chunking" + 조문별로 나눈 파일 |
| A | OpenAI File Search | 확인 못 함 | 언어 목록 비공개 | ⚠️ 한국 data residency는 **저장만 국내, 처리는 해외** ✅. File Search 처리는 미국·EU에서만 🟡 | chunk 크기만 지정 |
| A | Gemini File Search | 확인 못 함 | 언어 목록 비공개 | 확인 못 함 | chunk 크기만 지정. semantic 검색만 제공 |
| A | Pinecone Assistant | 확인 못 함 | 확인 못 함 | 확인 못 함 | 확인 못 함 |
| A | Vectara | 확인 못 함 | reranker는 100개 이상 언어를 지원한다고만 하고 한국어 명시는 없음 ⚪ | 확인 못 함(VPC·on-prem 배포 가능) | section 경계 유지, `CoreDocument` 업로드 ☑️ |
| B | Azure AI Search | ✅ `ko.microsoft`, `ko.lucene` ☑️ (문서, REST 스펙, SDK enum) | semantic ranker는 다국어 모델이라고만 명시. 한국어 품질 언급 없음 🟡 | ✅ Korea Central(AI enrichment, agentic retrieval, semantic ranker, AZ). Korea South는 agentic retrieval과 semantic ranker만 🟡 | custom skill 또는 직접 push로 완전 제어 |
| B | Elastic | ✅ nori 공식 plugin, 사전은 mecab-ko-dic ✅ (Elastic 문서 + Apache Lucene 빌드 소스) | jina-embeddings-v3를 EIS로 제공. 튜닝 대상 30개 언어(기반 모델은 100개)에 한국어 포함 ☑️ | ✅ **Hosted**: AWS 서울, GCP 서울 ☑️. ❌ **Serverless**: 한국 리전 없음 ☑️ | 완전 제어 |
| B | **OpenSearch** | ✅ nori. **관리형 도메인은 선택형 plugin**이라 패키지를 연결해야 함(연결 시 blue/green 배포) ☑️. **Serverless는 기본 탑재** ☑️. **오픈소스 기본 배포판에는 없음** 🧪. 인라인 사용자 사전(`user_dictionary_rules`)은 오픈소스에서 동작 🧪, Serverless에서는 ⚪ | 외부 모델 연결 방식이라 모델 선택에 달림 | ✅ Service, Serverless, Ingestion 모두 서울(ap-northeast-2) 엔드포인트 있음 ☑️ | `delimiter` chunking 또는 미리 자른 문서 투입 (9절 주의점 참고) |
| B | **Vespa** | ⚠️ **기본은 형태소 분석이 아님.** 기본 OpenNLP linguistics에는 한국어가 없고, Lucene linguistics는 한국어를 "지원"한다고 적었지만 소스상 기본값은 `CJKAnalyzer`(bigram) ✅. nori는 Maven 의존성으로 추가할 수 있고 공식 `simple-korean` 예제가 있음 ☑️ | embedder 선택에 달림 | ❌ Vespa Cloud에는 한국 zone 없음. 아시아태평양은 도쿄와 뭄바이(`aps1` = ap-south-1 ✅)뿐 ☑️. 직접 설치하면 가능 | 직접 만든 chunker 또는 미리 자른 문서 투입 |
| C | Cohere | 해당 없음 | Rerank v4는 multilingual ✅. 한국어 명시는 Cohere가 직접 쓴 AWS Marketplace 문구뿐 🟡 | 확인 못 함 | 해당 없음 |

**이 표에서 읽히는 결론** 🔄

- 형태소 분석과 한국 리전을 **둘 다 공식 자료로 확인한 곳은 B 유형의 세 곳**입니다.
  - Azure AI Search(Korea Central)
  - Elastic(Hosted만, Serverless는 제외)
  - OpenSearch(관리형 도메인은 plugin 연결 필요, Serverless는 기본 탑재)
- A 유형 중에서는 **기존 방식 Bedrock KB에 OpenSearch Serverless를 붙인 조합**만 서울 리전과 nori 기본 탑재가 함께 확인됩니다. 다만 KB의 검색이 nori 분석기를 실제로 쓰는지는 확인하지 못했습니다.
- Agent Search와 Bedrock Managed KB는 한국어를 다루지만 한국 리전이 없습니다.
- 한국 리전을 볼 때는 "저장"과 "처리"를 나눠서 봐야 합니다. OpenAI의 한국 data residency가 대표적인 예로, 데이터는 국내에 저장되지만 추론 처리는 해외에서 일어날 수 있습니다.

**bigram 방식이 왜 문제인가**: Vespa 기본값처럼 두 글자씩 자르면 "근로기준법"이 "근로", "로기", "기준", "준법"으로 색인됩니다. 이 상태에서 "기준"을 검색하면 "근로기준법"과 관계없는 "판단 기준" 문서도 함께 걸립니다. 형태소 분석이 없어도 검색은 되지만, 관련 없는 결과가 섞이기 쉽습니다.

**Vespa에서 nori를 쓰는 방법** ☑️ (공식 sample-apps `examples/lucene-linguistics/simple-korean`, 2025-07-02 추가)

1. `pom.xml`에 `lucene-analysis-nori` 의존성을 추가합니다.
2. `services.xml`의 `LuceneLinguistics` 설정에서 `ko` 키에 tokenizer `korean`을 지정합니다.
3. Maven으로 container plugin bundle을 빌드해 배포합니다.

Vespa Cloud에서 이 방식을 쓸 수 있을 가능성은 높습니다 🟡. 문서에 cloud 제한 태그가 없고, 일반적인 Java bundle 배포 방식이기 때문입니다. 하지만 "제약 없이 쓸 수 있다"고 명시한 문장은 찾지 못했습니다 ⚪.

---

## 7. 서비스별 상세

### 7.1 A 유형: 완전 관리형

**Google Agent Search** (구 Vertex AI Search)

- 2절 구조에서 쓰는 서비스입니다. 세부 사항은 4절을 참고하세요.
- Configurable 요금제로 만든 데이터 스토어는 Configurable 앱에서만 쓸 수 있습니다. General 요금제 앱은 Configurable 데이터 스토어에 연결하지 못합니다. 이 점이 lock-in 요소가 됩니다 🟡(가격 페이지와 설정 문서 두 곳).
- Gemini Enterprise 앱용 데이터 스토어는 General 요금제로 만들어야 합니다.

**Amazon Bedrock Managed Knowledge Base** (2026-06-17 GA)

- 다섯 단계를 모두 맡긴다는 점에서 Agent Search와 가장 가까운 형태입니다.
- AWS 문서 세 곳이 기존 방식보다 Managed KB를 권장합니다 🟡.
- agentic retrieval(`AgenticRetrieveStream`)과 AgentCore Gateway 연동을 지원합니다 ✅/☑️. GovCloud에서는 둘 다 쓸 수 없습니다.
- **문서 단위 접근 권한(ACL)은 Managed KB의 기능입니다** ✅. 다만 Web Crawler 커넥터는 권한 모델이 없어서 ACL을 켤 수 없습니다.
- **`userContext`를 빠뜨리면 결과가 0건입니다** ✅. ACL을 켠 데이터 소스는 아무것도 반환하지 않고, ACL이 없는 데이터 소스만 정상 결과를 냅니다. 실패하면 막는 쪽(fail closed)으로 동작한다는 점이 AWS 문서와 Classmethod 실측에서 일치했습니다.
- 메타데이터 필터에서 `startsWith`와 `stringContains`는 지원하지 않습니다.

**Amazon Bedrock Knowledge Bases (기존 방식)**

- chunking과 embedding은 Bedrock이 맡고, 저장과 검색은 사용자가 고른 vector store가 맡습니다.

```text
  Bedrock KB (기존 방식)
    ├─ chunking·embedding  : Bedrock이 담당
    └─ 저장·검색           : 사용자가 고른 vector store
                             (OpenSearch Serverless / Aurora PostgreSQL Serverless /
                              Neptune Analytics / S3 Vectors)
```

- Quick create 선택지는 위 4개이고, 현재 KB 생성 문서는 어느 것도 기본값으로 표시하지 않습니다 🟡. 반면 다른 AWS 문서(2025 ML 블로그, FSx 가이드)는 S3 Vectors를 "recommended"로 표기합니다.
- Confluence, SharePoint, Salesforce, Web Crawler를 데이터 소스로 쓰면 vector store는 OpenSearch Serverless만 고를 수 있습니다 🟡. **2026-09-30부터는 기존 방식 KB에서 이 네 커넥터를 새로 만들 수 없습니다.** 이미 만든 커넥터는 계속 동작합니다.
- **문서 단위 ACL이 없습니다.** 동기화한 데이터는 `bedrock:Retrieve` 권한이 있는 누구나 조회할 수 있습니다 🟡.
- **KB를 지워도 vector store는 지워지지 않습니다** ✅. AWS 사용자 가이드와 독립 블로그 cloudburn이 일치합니다. 다만 AWS 공식 배지가 붙은 re:Post 글 1건이 반대로 말하고 있으니, 실제 계정에서 한 번 확인하는 편이 안전합니다.
- 2026-05에 나온 OpenSearch Serverless NextGen collection(하한 비용 없음)은 **아직 KB Retrieve API와 호환되지 않습니다** 🟡(AWS ML 블로그 2026-09-17). Quick create가 Classic과 NextGen 중 무엇을 만드는지는 문서에 없습니다 ❓.

**Amazon Kendra**

- 2026-07-30부터 신규 고객을 받지 않으므로 새로 고를 대상이 아닙니다 ✅.
- Bedrock Managed KB로 옮기면 Query Suggestions, Faceted Search, Custom Synonyms, Spell Checking, Incremental Learning, Document Enrichment를 따로 구현해야 합니다 ☑️. AWS 마이그레이션 문서와 botocore API 대조로 확인했습니다.

**OpenAI File Search**

- Responses API로만 씁니다(Assistants API는 2026-08-26 종료 ✅).
- `ranker`에 넣을 수 있는 값이 API마다 다릅니다 ☑️.

| API | 허용 값 |
| --- | --- |
| Assistants file_search | `auto`, `default_2024_08_21` |
| Responses API file_search | `auto`, `default-2024-11-15` |
| vector store search | `none`, `auto`, `default-2024-11-15` |

- 가이드 문서에 적힌 `default-2024-08-21`(하이픈)은 위 어느 값과도 정확히 일치하지 않습니다.
- 어떤 chunk가 쓰였는지 보이지 않는다는 불만이 2024년 포럼에 있었습니다 ✅. 지금은 `include` 파라미터(`file_search_call.results`)로 검색 결과를 함께 받을 수 있습니다 ☑️.

**Gemini API File Search / Pinecone Assistant / Vectara**

- 6.1~6.3절의 표를 참고하세요.
- Vectara는 미리 자른 문서를 문서 색인 API의 `CoreDocument` 방식으로 넣습니다. 이 방식은 자동 분할을 건너뜁니다.

### 7.2 B 유형: 검색 엔진형

**Azure AI Search**

- 거의 모든 단계를 직접 조정할 수 있고, 한국어 분석기와 Korea Central 리전이 확인됩니다.
- 관련 제품인 Foundry IQ가 있습니다 ☑️. Foundry IQ의 agentic retrieval 사용량은 Azure AI Search 항목으로 과금됩니다.

**Elastic**

- `semantic_text` 필드 하나로 chunking, embedding, 저장을 자동 처리하면서, 필요하면 각 단계를 직접 조정할 수도 있습니다.
- nori 공식 plugin이 있고, 서울 리전은 Hosted에만 있습니다.

**OpenSearch**

- Elasticsearch 7.10.2에서 갈라진 엔진이라 Elastic과 사용법이 비슷합니다(5절 참고).
- 관리형으로는 Amazon OpenSearch Service(provisioned domain)와 OpenSearch Serverless가 있습니다. Serverless는 2026년에 **Classic과 NextGen 두 세대**로 나뉘었습니다(API enum `CLASSIC`, `NEXTGEN` ☑️).
- Serverless 제약 사항 ☑️ (AWS 문서와 botocore API 모델로 확인)

| 항목 | 내용 |
| --- | --- |
| collection 유형 | Time series, Search, Vector search. 만든 뒤에는 바꿀 수 없음(Update API에 `type` 필드가 없음) |
| NextGen 지원 유형 | Search와 Vector search만 |
| k-NN index | Search, Time series 유형에서는 쓸 수 없음. 벡터 검색이 필요하면 Vector search 유형을 골라야 함 |
| 저장 | Search, Vector search 유형은 모든 데이터를 hot storage에 둔다 |
| refresh | Search, Time series 유형은 약 10초. Vector search 유형은 문서에 명시 없음 |
| plugin | custom plugin 미지원 |
| NextGen ingest pipeline | 지원하지 않음(AWS Migration Assistant 문서 🟡). chunking은 클라이언트나 OpenSearch Ingestion에서 처리해야 함 |
| NextGen 첫 요청 지연 | 0 OCU에서 깨어날 때 개발자 가이드 기준 10~30초. AWS 블로그는 약 10초로 적음 ❓ |

- 2025~2026년 주요 신기능

| 기능 | 시점 | 확신도 |
| --- | --- | --- |
| Agentic search GA. LLM 기반 QueryPlanningTool이 자연어를 검색 DSL로 바꾸고, 외부 MCP 서버에 연결 가능 | 오픈소스 3.3(2025-10-14), Amazon 관리형은 2025-11-25 | ✅ |
| Agentic memory GA | 오픈소스 3.3. **Amazon 관리형에서 언제부터 제공되는지는 근거 없음** | ✅ / ⚪ |
| 기본 agent 4종(conversational, plan_execute_and_reflect, flow, conversational_flow) 모두 MCP 지원, MCP list-tools API, gRPC streaming | 3.8(2026-08-05) | ☑️ |
| Serverless NextGen과 scale-to-zero | 2026-05-28 | ☑️ |

**Vespa**

- 키워드, 벡터, 구조화된 필드를 한 쿼리에서 함께 다루고, 다단계 ranking을 엔진 안에서 정의하는 것이 핵심입니다(6.1절).
- 관리형은 Vespa Cloud입니다 ☑️.
  - prod zone은 AWS(미국, 유럽, 아시아태평양)와 GCP(미국, europe-west3)에 있습니다.
  - Azure는 **prod zone만 없습니다.** dev zone(`azure-eastus-az1`)과 Enclave(고객 클라우드 계정 안에 Vespa Cloud가 관리하는 배포)는 Azure를 지원합니다.
  - 한국 zone은 없습니다.
- remote embedder는 기본 설정에서 외부 업체 API(api.openai.com, api.mistral.ai, api.voyageai.com)로 텍스트를 보냅니다 ☑️. `endpoint`를 바꿀 수 있고, OpenAI embedder는 OpenAI 호환 API라면 자체 호스팅 서버도 쓸 수 있습니다. 데이터 보관 지역에 관한 서술은 문서에 없습니다.
- 2025~2026년 주요 신기능

| 기능 | 시점 | 확신도 |
| --- | --- | --- |
| 엔진 내장 chunking(8.520), layered ranking(8.530) | 2025-06 | ☑️ |
| Voyage 4 비대칭 구성: 문서는 API로, 쿼리는 로컬 소형 모델(voyage-4-nano)로 처리. Voyage 4 계열은 embedding 공간을 공유함 | 2026-05 | ✅ (Vespa, Voyage AI 모델 카드, MongoDB) |
| coding agent용 Vespa skills(Elasticsearch 이관 포함) | 2026-05-27 | ☑️ |
| Kubernetes Operator(enterprise 전용) | 2026-02-16 | ☑️ |

### 7.3 C 유형: 부품형

**Cohere**

- Embed와 Rerank를 API로 제공합니다.
- Compass(전처리·검색)와 North(업무 플랫폼)는 가격이 공개되어 있지 않습니다. Compass Cloud는 private beta입니다 ✅.
- Rerank 3.5는 Cohere 자체 API와 Model Vault에서 여전히 제공됩니다. Pinecone이 호스팅하는 rerank-3.5만 2026-07-01에 deprecated되었고, 08-31부터 rerank-4-fast로 자동 연결됩니다 ✅.
- Cohere 모델은 Bedrock, OpenSearch(remote connector) 같은 다른 유형의 파이프라인에 부품으로 들어갑니다.

---

## 8. 시장 평가

### 8.1 애널리스트 평가

| 보고서 | 발행 | 관련 서비스의 위치 | 확신도 |
| --- | --- | --- | --- |
| **Forrester Wave: Cognitive Search Platforms, Q4 2025** (14개사, 21개 기준) | 2025-10-03 | Leaders: Kore.ai, Mindbreeze, **Elastic** ✅ / Strong Performers: Sinequa, Coveo, Lucidworks, **Google Cloud**, Moveworks, Glean / Contenders: OpenText, SearchUnify, **Microsoft**, **Amazon Web Services**, Algolia | 목록은 ✅ (Forrester 아카이브 목차 + 벤더 4곳 발표). Google·Microsoft·AWS 등급은 🟡 (Forrester 단독) |
| **IDC MarketScape: WW General-Purpose Knowledge Discovery Software 2025** | 2025-11 | **Elastic: Leader** ✅, **Google: Leader** 🟡. Microsoft와 AWS는 평가 대상이 아님 | ✅ / 🟡 |
| **GigaOm Radar for Vector Databases v3** (17개사) | 2025-11 | **Vespa.ai: Leader(최고 평가)**, **OpenSearch: Leader** ✅. AWS·Google·Microsoft는 평가됐지만 Leader가 아님. Elastic은 대상에 없음 | ✅ |
| **Gartner MQ for Search & Product Discovery 2025** (15개사) | 2025-06-24 | Leaders 6곳: Algolia, Bloomreach, Constructor, Coveo, **Google**, Netcore Unbxd. 커머스 검색 중심이라 이 비교와는 거리가 있음. 2026판도 이미 나와 있음 | ✅ |
| Gartner Market Guide for Enterprise AI Search | 2025-09-15 | 순위가 없는 시장 개관 보고서 | ☑️ (존재만) |
| Gartner Insight Engines MQ 후속판 | — | 2025~2026판을 찾지 못함 | ❓ |
| Azure AI Search나 Bedrock KB를 **제품 단위**로 평가한 보고서 | — | 찾지 못함 | ⚪ |

해석할 때 주의할 점이 두 가지 있습니다.

- Forrester 목차에는 회사 이름만 나옵니다. 그래서 "Azure AI Search가 Contender", "Bedrock KB가 Contender"처럼 제품 이름을 붙이면 근거를 넘어섭니다.
- "Leader"는 애널리스트의 가치 판단이지, 실제로 얼마나 많이 쓰이는지를 말해 주지 않습니다.

### 8.2 개발자 커뮤니티 평가

아래는 Reddit(웹 검색을 브라우저로 직접 연 결과), Hacker News API, 벤더 포럼에서 원문을 확인한 의견입니다. **"이런 의견이 있다"는 사실은 Confirmed이지만, 대부분 개인 한 명의 경험담이라 대표성은 없습니다.**

| 서비스 | 칭찬 | 불만 |
| --- | --- | --- |
| Bedrock KB | "it works pretty well and is cost effective"(HN, 2025-02), "the simplest implementation on the Market"(HN, 2025-10) | "a black box — you can't control chunking"(r/Rag, 2026-03). 다만 현재 공식 문서상 chunking 옵션은 있음. "Just don't use the OpenSearch serverless store it's $$$"(HN, 2023-12) |
| Agent Search | "usually the winner in every AB test I've seen"(HN, 2026-09, 커머스 검색 제품 기준) | "Indexing is a nightmare … anywhere from a minute to never for same document"(r/googlecloud, 2026-02), "the latency hasn't been great (Google especially slow)"(r/Rag, 2026-04) |
| Azure AI Search | "azure cosmos db + azure ai search Pretty good"(r/Rag, 2026-07) | "Vectorizing the content and syncing daily gets kinda expensive"(r/AZURE, 2026-03). Microsoft가 내장 Indexer 대신 직접 만들라고 권했다는 경험담도 있음 |
| OpenAI File Search | — | 최대 결과 수 파라미터가 오래 동작하지 않았다는 불만, "control the retrieval layer yourself"라는 조언(OpenAI 포럼, 2025) |
| OpenSearch | 필터와 facet을 함께 쓸 거라면 OpenSearch나 Elastic이 낫다는 의견(r/Rag, 2025-08) | "great but we're not 'full production' yet"(HN, 2025-05) |
| Vespa | ranking 깊이를 3배 이상 늘려 결과 관련성이 좋아졌다는 사례(Vinted 엔지니어링 블로그, 2024-09) ✅. "slightly better than Elasticsearch, especially in search relevancy"(PeerSpot) | "the learning curve was high"(HN, 2024-04), "considerable learning curve", "lack of documentation", "A UI would be nice"(PeerSpot 리뷰 3건). Elasticsearch만큼 동의어를 다루지 못한다는 지적도 있음 |

**개인 벤치마크 1건** (HN, 2026-05, 문서 81개와 질문 50개로 측정했다는 게시글)

| 서비스 | 점수 |
| --- | --- |
| Azure AI Search | 84.0 |
| Vertex AI RAG Engine | 82.6 |
| Bedrock KB | 82.5 |
| OpenAI File Search | 78.5 |

- 작성자는 "네 서비스 모두 답할 수 없는 질문에서 hallucination을 일으켰다"고 적었습니다.
- 표본이 작고 측정 방법을 검증하지 않았으므로 참고용으로만 봐야 합니다.
- 여기서 Vertex는 Agent Search가 아니라 RAG Engine입니다.

### 8.3 서비스별 주요 비판 정리

| 유형 | 서비스 | 공식 자료로 확인된 약점 |
| --- | --- | --- |
| A | Agent Search | 한국 리전 없음, multi-region 결과가 global과 다를 수 있음, chunk 설정 변경 불가 ☑️. BYO embedding은 Preview이고, Configurable 데이터 스토어는 lock-in 🟡 |
| A | Bedrock Managed KB | 외부 vector store 불가, 서울 리전 없음, 메타데이터 필터 일부 미지원 |
| A | Bedrock 기존 방식 | 문서 단위 ACL 없음, 커넥터 신규 생성 중단, KB를 지워도 vector store가 남음, OpenSearch Serverless Classic 하한 비용 |
| A | Gemini File Search | 공식 문서와 API 스펙에 keyword·hybrid 옵션이 없음 ☑️. 그래서 "제5조"처럼 조문 번호를 정확히 찾는 검색에 약할 수 있음 🔄(실측하지 않은 추론) |
| A | OpenAI File Search | 처리 리전이 미국·EU뿐, ranker 값이 API마다 달라 혼동하기 쉬움 |
| A | Vectara | 최소 연 $100K로 진입 장벽이 높음 ✅ |
| B | Azure AI Search | 일시 정지가 안 됨, 용량 증설 시 비용이 비선형으로 늚. 초기 구성 난이도는 리뷰마다 "쉽다"와 "어렵다"가 엇갈림 ❓ |
| B | OpenSearch | Classic Serverless 하한 비용(서울 약 $428/월). Elasticsearch 계열이라 운영 튜닝 부담(merge policy, JVM heap)을 물려받는다는 평가(벤더 블로그 2곳, 의견) ✅ |
| B | Vespa | 학습 곡선, 문서 부족, 관리 UI 없음(리뷰 의견) 🟡. 한국 zone 없음, 한국어는 nori를 직접 빌드해야 함 ☑️ |

---

## 9. 실전 예제: OpenSearch로 조문 단위 한국어 검색 구성하기

B 유형 엔진을 쓰면 "nori 형태소 분석 + 조문 단위 chunk + 키워드 검색"을 직접 설계하게 됩니다. 아래 예제는 **오픈소스 OpenSearch 3.9.0에서 실제로 실행해 확인했습니다** 🧪. 문법 근거는 OpenSearch 문서와 소스 코드(`DelimiterChunker.java`, `NoriTokenizerFactory.java`)입니다 ☑️.

**사전 준비: 배포판마다 다릅니다**

| 배포판 | text_chunking | nori | 준비 작업 |
| --- | --- | --- | --- |
| 오픈소스 기본 배포판 | 2.13+에서 사용 가능 ✅ | **들어 있지 않음** 🧪 | `bin/opensearch-plugin install analysis-nori` 후 재시작 |
| Amazon OpenSearch Service | neural search plugin은 있지만 processor 이름을 명시한 AWS 문서는 없음 🟡 | 선택형 plugin ☑️ | 콘솔 Packages 탭에서 analysis-nori 연결(blue/green 배포가 일어남) |
| Serverless Classic | ⚪ | 기본 탑재 ☑️ | — |
| Serverless NextGen | ingest pipeline 미지원 🟡 | 기본 탑재 ☑️ | chunking은 클라이언트나 OpenSearch Ingestion에서 처리 |

nori를 설치하지 않은 채 아래 예제를 실행하면 `Custom Analyzer [korean] failed to find tokenizer under name [nori_tokenizer]` 오류(400)가 납니다 🧪.

**1단계: 조문 경계로 자르는 ingest pipeline**

법령 원문에서 조문과 조문 사이를 빈 줄(`\n\n`)로 구분해 두었다고 가정합니다.

```http
PUT _ingest/pipeline/law-article-chunking
{
  "description": "조문 경계(빈 줄)로 법령 본문을 chunk로 나눈다",
  "processors": [
    {
      "text_chunking": {
        "algorithm": {
          "delimiter": { "delimiter": "\n\n", "max_chunk_limit": -1 }
        },
        "field_map": { "body": "body_chunks" }
      }
    }
  ]
}
```

**2단계: nori 분석기를 쓰는 index**

```http
PUT law-corpus
{
  "settings": {
    "index": { "default_pipeline": "law-article-chunking" },
    "analysis": {
      "analyzer": {
        "korean": {
          "type": "custom",
          "tokenizer": "nori_tokenizer",
          "filter": ["nori_part_of_speech", "nori_readingform", "lowercase"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "law_name":      { "type": "keyword" },
      "article_no":    { "type": "keyword" },
      "article_title": { "type": "text", "analyzer": "korean" },
      "body":          { "type": "text", "analyzer": "korean" },
      "body_chunks":   { "type": "text", "analyzer": "korean" }
    }
  }
}
```

**3단계: 문서 넣기와 검색**

```http
POST law-corpus/_doc
{
  "law_name": "근로기준법",
  "article_no": "제60조",
  "article_title": "연차 유급휴가",
  "body": "① 사용자는 1년간 80퍼센트 이상 출근한 근로자에게 15일의 유급휴가를 주어야 한다.\n\n② 사용자는 계속하여 근로한 기간이 1년 미만인 근로자 ..."
}

GET law-corpus/_search
{
  "query": {
    "bool": {
      "must":   { "match": { "body_chunks": "연차휴가 발생 요건" } },
      "filter": { "term":  { "law_name": "근로기준법" } }
    }
  }
}
```

**이 예제에서 봐야 할 지점**

| 지점 | 정상 케이스 | 실패·예외 케이스 |
| --- | --- | --- |
| `max_chunk_limit` | `-1`이면 조문 수만큼 chunk가 생긴다 🧪 | **이 값을 빼면 기본값 100이 적용된다.** 조문 150개짜리 문서를 넣었을 때 chunk가 100개만 생겼고, 101~150조가 마지막 chunk 하나(661자)에 합쳐졌다 🧪. 오류 없이 결과만 나빠지므로 특히 위험하다. 근로기준법처럼 조문이 100개를 넘는 법령에서 실제로 생길 수 있다 |
| nori 분석 | "근로조건의 기준"이 "근로 / 조건 / 의 / 기준"으로 나뉜다 🧪. `nori_part_of_speech` 필터를 쓰면 조사 "의"가 걸러진다 | 사용자 사전이 없으면 "통상임금" 같은 법률 복합어를 엉뚱하게 나눌 수 있다. 인라인 규칙 `user_dictionary_rules`를 쓰면 "근로기준법"이 토큰 하나로 나온다 🧪(오픈소스 기준). Serverless에서 같은 설정이 되는지는 ⚪ |
| chunk 결과 | 각 chunk가 `text` 배열로 저장되고 `match` 검색으로 찾힌다 🧪 | chunk 끝에 구분자 `\n\n`가 남는다(소스상 구분자까지 포함해 자름). 또 배열로 저장하면 **문서 단위로** 일치 여부가 판정되므로 어떤 조문 chunk가 걸렸는지 알 수 없다. RAG처럼 조각 단위 인용이 필요하면 nested 필드를 쓰거나 chunk마다 별도 문서로 넣어야 한다 |
| 조문 경계 | 원문이 조문 사이만 빈 줄로 구분하면 조문 하나가 chunk 하나가 된다 | 항(①, ②) 사이에도 빈 줄이 있으면 항 단위로 잘린다. 조문 하나를 문서 하나로 미리 나눠 넣는 편이 경계를 더 확실히 지킨다 |
| `law_name` 필터 | `keyword` 필드라 "근로기준법"을 정확히 걸러낸다 | "근로기준법 시행령"은 다른 값이라 걸리지 않는다. 시행령까지 묶으려면 상위 법령명 필드를 따로 둬야 한다 |
| 벡터·hybrid 검색 | 이 예제는 키워드 검색만 한다 | 의미 검색을 더하려면 `text_embedding` processor로 embedding 필드를 추가하고, `hybrid` query와 점수 합산 search pipeline을 구성해야 한다. Serverless라면 collection 유형을 Vector search로 만들어야 한다 |

---

## 10. 주의점, 남은 모순, 조사의 한계

### 10.1 주의점

- **검색 질의문의 국외 이전**
  - Agent Search에는 한국 리전이 없고 ☑️, OpenAI File Search는 한국 data residency를 써도 처리는 해외에서 합니다 ✅.
  - RAG 서버가 고객 질문으로 검색 질의문을 만들 때 고객 정보(예: 직원 이름과 급여)가 섞이면, 그 질의문이 국외 리전으로 나갈 수 있습니다.
  - 법령 검색 결과의 민감정보 스크리닝을 건너뛰도록 설계했다면 더욱 그렇습니다. 질의문이 어떻게 만들어지고 어디로 가는지는 RAG 서버 쪽에서 확인해야 합니다.
- **chunk 설정은 되돌릴 수 없습니다.** Agent Search는 데이터 스토어를 만든 뒤 chunk 설정을 바꿀 수 없고 ☑️, Bedrock Managed KB는 데이터 소스를 연결한 뒤 바꿀 수 없습니다 🟡. 조문 단위 전략을 바꾸려면 데이터 스토어나 데이터 소스를 새로 만들어야 합니다.
- **오류 없이 결과만 나빠지는 경우가 있습니다.**
  - OpenSearch `text_chunking`의 `max_chunk_limit` 기본값 100 🧪
  - Bedrock에서 `userContext`를 빠뜨린 경우 ✅. 이때는 결과가 0건이 되므로 "검색 결과 없음"으로 오인하기 쉽습니다.
- **"지원"이라는 말의 뜻을 확인해야 합니다.** Vespa 문서는 한국어를 지원 언어로 적었지만, 실제 기본 처리는 bigram입니다 ✅. 문서에 "Korean 지원"이 있어도 형태소 분석을 뜻하는지 따로 확인해야 합니다.
- **한국어 검색 품질은 별개의 문제입니다.** 형태소 분석기를 지원한다는 사실과 실제 법령 검색 품질은 다릅니다. 한국어 법령 검색 품질을 서비스끼리 비교한 자료는 찾지 못했습니다. 판단하려면 법령 몇십 건으로 직접 비교해 봐야 합니다.

### 10.2 아직 남은 모순

| 쟁점 | 출처 A | 출처 B | 상태 |
| --- | --- | --- | --- |
| Bedrock Managed KB의 hierarchical chunking | Kendra 마이그레이션 문서: 지원 | Managed KB 생성·비교 문서, Classmethod: 선택지에 없음 | ❓ 미해결 |
| Managed KB의 기본 chunking | AWS 문서: 300 token 고정 크기 | Classmethod: 관리형 embedding이면 chunking도 자동 최적화 | ❓ 미해결 |
| KB 삭제 시 vector store | AWS 사용자 가이드, cloudburn: 남는다 | AWS 공식 배지가 붙은 re:Post 기사: Bedrock이 만든 store는 함께 지워진다 | 가이드 쪽을 채택했지만 실제 계정 확인 권장 |
| OpenSearch NextGen 첫 요청 지연 | 개발자 가이드: 10~30초 | AWS 블로그 2편: 약 10초 | ❓ |
| nori 최소 버전(Amazon Service) | AWS plugin 표: 1.3 | AWS 한국 기술 블로그: 1.0 이상 | ❓ |
| Azure Serverless의 Korea Central | Retail Prices API: 요금 있음(2026-10-01 시행) | 리전 문서 표: Serverless 칸 비어 있음 | ❓ |
| Agent Search Advanced Generative Answers 단가 | 가격 페이지: +$4.00/1,000 | SKU 카탈로그: $10.00/1,000 항목도 있음 | ❓ |
| Managed KB `chunkingStrategy` 예시 값 | 데이터 소스 문서: `"DEFAULT"` | botocore enum: DEFAULT 없음 | ❓ |
| Cohere rerank-v3.5 용도 | 모델 개요: 영어 문서용 | Rerank 페이지: 영어 외 언어도 잘함 | ❓ |
| IDC MarketScape 2025 Leader | Mindbreeze, Algolia 자체 발표: Leader | IDC 발췌 PDF: 두 회사는 "Major players" | ❓ |
| jina-embeddings-v3 언어 수 | Elastic 블로그: 32개 | 같은 글의 실제 나열과 모델 카드: 30개 | 모델 카드(30개)를 채택 |

### 10.3 조사의 한계

- **도구 장애**: 일부 MCP 서버(GitHub, AWS 가격)가 연결이나 의존성 문제로 동작하지 않았습니다. 대신 `gh` CLI, raw.githubusercontent.com, 공개 AWS Price List 파일, Azure Retail Prices API를 썼습니다.
- **요약 모델의 누락**: WebFetch는 원문을 요약 모델에 통과시킨 뒤 돌려줍니다. 이번 검증에서는 요약 모델이 원문에 있는 문단을 "없다"고 보고한 사례가 1건 있었습니다(aicoolies 리뷰). 그래서 핵심 주장은 curl이나 Playwright로 원문을 다시 열어 확인했습니다.
- **사라지는 근거**: Forrester 라이브 페이지에서는 보고서 목차가 더 이상 보이지 않아 2025-11-15 아카이브에 의존했습니다. 이전 조사에서 근거로 썼던 집계 사이트(Spotlight)는 도메인이 사라졌습니다.
- **조사하지 않은 범위**: 한국어 법령 검색 품질을 직접 측정하지 않았습니다. OpenSearch 예제는 오픈소스에서만 실행했고, Amazon 관리형과 Serverless에서는 실행하지 않았습니다.
- **Vespa 버전 태그**: `v8.530.*` 태그가 GitHub에 없어서, layered ranking 버전은 블로그 표기와 커밋 범위(8.526.15~8.533.16)로 판정했습니다.
- **확인하지 않은 최신판**: Gartner MQ for Search & Product Discovery 2026판(12개사 평가)이 이미 나와 있지만 내용은 확인하지 않았습니다.

---

## 11. 정리

1. **법령 상담 에이전트의 법령 정보 경로**: 에이전트 → MCP 검색 도구 → 별도로 운영되는 RAG 서버 → Agent Search(구 Vertex AI Search) 데이터 스토어. 코퍼스를 무엇으로 채웠는지는 RAG 서버 쪽에서 확인해야 합니다.
2. **데이터 스토어의 역할**: RAG 전체가 아니라 검색(Retrieval) 단계를 맡습니다. 그 안의 다섯 단계(chunking, embedding, 저장·색인, 검색, reranking)를 관리형으로 묶어 제공하며, 검색은 BM25와 semantic을 결합한 hybrid 방식입니다 ☑️.
3. **대안은 세 유형으로 나뉩니다.**

| 유형 | 대표 | 한 줄 요약 |
| --- | --- | --- |
| A. 완전 관리형 | Agent Search, Bedrock Managed KB, OpenAI·Gemini File Search, Pinecone Assistant, Vectara | 빠르고 편하지만 내부가 덜 보이고 덜 조정된다 |
| B. 검색 엔진형 | Azure AI Search, Elastic, OpenSearch, Vespa | 다섯 단계를 엔진 안에서 조립한다. 한국어 처리와 조문 단위 제어가 가능하지만 설계·운영 부담이 크다 |
| C. 부품형 | Cohere | embedding이나 reranking 한 단계를 다른 파이프라인에 끼워 넣는다 |

4. **한국어 법령 검색 기준**: 형태소 분석과 한국 리전을 공식 자료로 함께 확인한 곳은 Azure AI Search, Elastic Hosted, OpenSearch입니다. Agent Search, Bedrock Managed KB, Elastic Serverless, Vespa Cloud는 한국 리전이 없습니다. OpenAI는 저장만 국내이고 처리는 해외입니다.
5. **B 유형 안에서의 선택**
   - 애널리스트 평가: OpenSearch와 Vespa는 GigaOm Vector DB Radar에서 Leader였고 ✅, Elastic은 Forrester와 IDC에서 Leader였습니다 ✅.
   - 운영 관점: 이미 Elasticsearch 계열 인프라나 AWS를 쓰고 있다면 OpenSearch나 Elastic, ranking 품질에 엔지니어링 투자를 할 수 있다면 Vespa가 후보가 됩니다. 이 운영 관점은 3자 리뷰와 Vinted 사례에 근거한 것이라 🟡입니다.
6. **비용 감각**: Agent Search로 월 10만 쿼리를 처리하면 Standard 기준 약 $135입니다 ✅. OpenSearch Serverless Classic은 쿼리가 없어도 서울 기준 약 $428/월이 나갑니다 ☑️.
7. **2025~2026년 변화**: Vertex AI Search는 Agent Search로 이름이 바뀌었습니다. Kendra는 신규 고객을 받지 않고, Bedrock Managed KB와 OpenSearch Serverless NextGen이 새로 나왔으며, 기존 방식 Bedrock KB의 일부 커넥터는 신규 생성이 막혔습니다. 2024~2025년 비교 자료는 낡았다고 보고 읽어야 합니다.

---

## 12. 출처

**Google**

- [Agent Search release notes](https://docs.cloud.google.com/generative-ai-app-builder/docs/release-notes) · [Agent Platform release notes(이름 변경표)](https://docs.cloud.google.com/gemini-enterprise-agent-platform/release-notes)
- [Agent Search 가격](https://cloud.google.com/generative-ai-app-builder/pricing?hl=en) · [Configurable pricing 설정](https://docs.cloud.google.com/generative-ai-app-builder/docs/enable-configurable-pricing) · Google Cloud SKU 카탈로그(cloud.google.com/skus)
- [Parse and chunk documents](https://docs.cloud.google.com/generative-ai-app-builder/docs/parse-chunk-documents) · [Bring embeddings](https://docs.cloud.google.com/generative-ai-app-builder/docs/bring-embeddings) · [Languages & locales](https://docs.cloud.google.com/generative-ai-app-builder/docs/languages-locales) · [Locations](https://docs.cloud.google.com/generative-ai-app-builder/docs/locations)
- [About generic search(hybrid)](https://docs.cloud.google.com/generative-ai-app-builder/docs/about-generic-search) · [Answer method](https://docs.cloud.google.com/generative-ai-app-builder/docs/answer) · [Create data store](https://docs.cloud.google.com/generative-ai-app-builder/docs/create-data-store-es)
- [Agent Retrieval(구 Vector Search 2.0)](https://docs.cloud.google.com/vertex-ai/docs/vector-search-2/overview) · Discovery Engine API 스펙(`discoveryengine.googleapis.com/$discovery/rest`)
- [Gemini File Search](https://ai.google.dev/gemini-api/docs/file-search) · [Gemini API 가격](https://ai.google.dev/gemini-api/docs/pricing) · [File Search 출시 블로그](https://blog.google/technology/developers/file-search-gemini-api/) · `googleapis/python-genai` `types.py`
- [Build Google-quality RAG codelab](https://codelabs.developers.google.com/build-google-quality-rag)

**AWS**

- [Managed KB 수집 설정](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-customize-ingestion.html) · [Managed KB vs 기존 방식](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-build-managed.html) · [Managed KB 리전](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-regions.html) · [Managed KB ACL](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-acl.html) · [ACL 검색](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-retrieve-acl.html) · [Retrieve 테스트](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-retrieve.html) · [Gateway target](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-gateway-target.html)
- [KB 생성](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-create.html) · [KB 지원 모델·리전](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-supported.html) · [Bedrock chunking](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking.html) · [KB 삭제](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-delete.html) · [Web Crawler 커넥터](https://docs.aws.amazon.com/bedrock/latest/userguide/webcrawl-data-source-connector.html)
- [Bedrock 가격](https://aws.amazon.com/bedrock/pricing/) · [Managed KB GA 공지](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-bedrock-managed-knowledge-base/) · [Vector store 선택 블로그(2026-09)](https://aws.amazon.com/blogs/machine-learning/selecting-a-vector-store-for-amazon-bedrock-knowledge-bases/) · [S3 Vectors 블로그(2025-07)](https://aws.amazon.com/blogs/machine-learning/building-cost-effective-rag-applications-with-amazon-bedrock-knowledge-bases-and-amazon-s3-vectors/)
- [What is Kendra](https://docs.aws.amazon.com/kendra/latest/dg/what-is-kendra.html) · [Kendra availability change](https://docs.aws.amazon.com/kendra/latest/dg/kendra-availability-change.html) · [Kendra 가격](https://aws.amazon.com/kendra/pricing/)
- [Stepping up for a truly open source Elasticsearch(2021-01)](https://aws.amazon.com/blogs/opensource/stepping-up-for-a-truly-open-source-elasticsearch/) · [Introducing OpenSearch(2021-04)](https://aws.amazon.com/blogs/opensource/introducing-opensearch/)
- [Serverless 개요](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-overview.html) · [Serverless 지원 plugin](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-genref.html) · [Service 지원 plugin](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/supported-plugins.html) · [Serverless scaling](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-scaling.html) · [Scale to zero](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-scale-to-zero.html) · [엔드포인트·리전](https://docs.aws.amazon.com/general/latest/gr/opensearch-service.html) · [OpenSearch 가격](https://aws.amazon.com/opensearch-service/pricing/)
- [Agentic search 공지](https://aws.amazon.com/about-aws/whats-new/2025/11/opensearch-service-agentic-search/) · [Nori 등 언어 분석기 공지(2023-10)](https://aws.amazon.com/about-aws/whats-new/2023/10/amazon-opensearch-four-language-analyzers/)
- [AWS 가용 영역 ID](https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-availability-zones.html) · AWS Price List 공개 파일(AmazonES, AmazonKendra, Bedrock) · `boto/botocore` service-2.json, endpoints.json

**Microsoft**

- [언어 분석기](https://learn.microsoft.com/en-us/azure/search/index-add-language-analyzers) · [비용 관리](https://learn.microsoft.com/en-gb/azure/search/search-sku-manage-costs) · [리전](https://learn.microsoft.com/en-us/azure/search/search-region-support) · [semantic ranking 개요](https://learn.microsoft.com/en-us/azure/search/semantic-search-overview) · [Foundry IQ](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/what-is-foundry-iq) · [가격](https://azure.microsoft.com/en-us/pricing/details/search/)
- Azure Retail Prices API(`prices.azure.com/api/retail/prices`) · `Azure/azure-rest-api-specs` `models-service.tsp` · `Azure/azure-sdk-for-python` `_enums.py`

**OpenAI / Cohere / Pinecone / Vectara**

- [OpenAI file search](https://developers.openai.com/api/docs/guides/tools-file-search) · [retrieval](https://developers.openai.com/api/docs/guides/retrieval) · [deprecations](https://developers.openai.com/api/docs/deprecations) · OpenAI data residency 가이드(your-data) · `openai/openai-python` · `openai/openai-openapi`
- [Cohere rerank](https://docs.cohere.com/v2/docs/rerank) · [Cohere 가격](https://cohere.com/pricing) · [Model Vault 가격](https://docs.cohere.com/docs/model-vault/standard/pricing) · [Compass](https://cohere.com/compass) · Cohere Embed 5 changelog(2026-09-30)
- [Pinecone Assistant 가격](https://docs.pinecone.io/guides/assistant/pricing-and-limits) · [Assistant 개요](https://docs.pinecone.io/guides/assistant/overview)
- [Vectara 가격](https://www.vectara.com/pricing) · [chunking](https://docs.vectara.com/docs/build/chunking-strategies) · [multilingual reranker](https://docs.vectara.com/docs/search-and-retrieval/rerankers/vectara-multi-lingual-reranker) · web.archive.org Vectara 가격 스냅숏(2022-12, 2024-12, 2025-08, 2025-09)

**Elastic / Apache Lucene / Jina**

- [semantic_text](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/semantic-text) · [Serverless 가격](https://www.elastic.co/pricing/serverless-search) · [Hosted 리전](https://www.elastic.co/docs/reference/cloud/cloud-hosted/regions) · [nori 블로그](https://www.elastic.co/blog/nori-the-official-elasticsearch-plugin-for-korean-language-analysis) · [jina-embeddings-v3 on EIS](https://www.elastic.co/search-labs/kr/blog/jina-embeddings-v3-elastic-inference-service)
- `elastic/elasticsearch` `WordBoundaryChunkingSettings.java` · Apache Lucene `lucene/analysis/nori/build.gradle` · Hugging Face jina-embeddings-v3 모델 카드

**OpenSearch 프로젝트 / Linux Foundation**

- [text_chunking processor](https://docs.opensearch.org/latest/ingest-pipelines/processors/text-chunking/) · [rerank processor](https://docs.opensearch.org/latest/search-plugins/search-pipelines/rerank-processor/) · [hybrid search](https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/index/) · [remote models](https://docs.opensearch.org/latest/ml-commons-plugin/remote-models/index/) · [What's new in 3.8](https://opensearch.org/blog/whats-new-in-opensearch-3-8/)
- `opensearch-project/OpenSearch`, `neural-search`(`RerankType.java`, `DelimiterChunker.java`), `ml-commons`, `k-NN`, `opensearch-build`, `documentation-website` 저장소의 release notes와 소스
- [OpenSearch Software Foundation 출범](https://www.linuxfoundation.org/press/linux-foundation-announces-opensearch-software-foundation-to-foster-open-collaboration-in-search-and-analytics)
- [Elastic 라이선스 변경 공지(2021-01)](https://www.elastic.co/blog/licensing-change)

**Vespa / Yahoo**

- [Yahoo의 Vespa 분사 보도자료](https://www.yahooinc.com/press/yahoo-spins-out-vespa-its-enterprise-ai-scaling-engine-as-an-independent-company)
- [phased ranking](https://docs.vespa.ai/en/ranking/phased-ranking.html) · [embedding](https://docs.vespa.ai/en/rag/embedding.html) · [chunking reference](https://docs.vespa.ai/en/reference/rag/chunking.html) · [working with chunks](https://docs.vespa.ai/en/rag/working-with-chunks.html) · [Lucene linguistics](https://docs.vespa.ai/en/linguistics/lucene-linguistics.html) · [hybrid search 튜토리얼](https://docs.vespa.ai/en/learn/tutorials/hybrid-search.html) · [quota](https://docs.vespa.ai/en/cloud/quota.html) · [가격 계산기](https://cloud.vespa.ai/price-calculator)
- [Layered ranking 블로그(2025-06-30)](https://blog.vespa.ai/) · [2025-06 뉴스레터](https://blog.vespa.ai/vespa-newsletter-june-2025/) · [2026-05 뉴스레터](https://blog.vespa.ai/vespa-newsletter-may-2026/)
- `vespa-engine/vespa`(`GlobalPhaseSetup.java`, `ProfileAnalyzersImporter.java`, embedder `.def`), `vespa-engine/documentation`(zone 표), `vespa-engine/sample-apps`(`simple-korean`, `rag-blueprint`), `vespa-engine/skills`, `vespa-cloud/terraform-aws-enclave`
- Hugging Face `voyageai/voyage-4-nano` 모델 카드 · MongoDB Voyage 4 제품 업데이트

**애널리스트**

- [Forrester Wave: Cognitive Search Platforms Q4 2025](https://www.forrester.com/report/the-forrester-wave-tm-cognitive-search-platforms-q4-2025/RES186654) · [2025-11-15 아카이브(목차)](http://web.archive.org/web/20251115142847/https://www.forrester.com/report/the-forrester-wave-tm-cognitive-search-platforms-q4-2025/RES186654)
- [Mindbreeze 발표](https://www.mindbreeze.com/news/independent-research-firm-names-mindbreeze-a-leader-in-the-cognitive-search-platforms) · [Kore.ai 발표](https://kore.ai/ai-research-reports/kore-ai-leader-forrester-wave-cognitive-search-q4-2025) · [Elastic 발표](https://www.elastic.co/blog/forrester-leader-cognitive-search-platforms-2025) · [Moveworks 발표](https://www.moveworks.com/us/en/resources/blog/moveworks-in-forrester-wave-for-cognitive-search-platform)
- [Gartner MQ Search & Product Discovery 2025](https://www.gartner.com/en/documents/6633334) · [Coveo 발표](https://www.coveo.com/blog/coveo-gartner-magic-quadrant-2025/) · Algolia, Google, Bloomreach, Netcore, Constructor 발표
- [Gartner Market Guide for Enterprise AI Search](https://www.gartner.com/en/documents/6952766)
- [IDC MarketScape 2025](https://my.idc.com/getdoc.jsp?containerId=US53011225) · [IDC 발췌(Elastic 배포)](https://www.elastic.co/pdf/idc-marketscape-worldwide-general-purpose-knowledge-discovery-software-2025.pdf)
- [GigaOm Vector DB Radar v3 보도(Blocks & Files)](https://blocksandfiles.com/2025/11/27/gigaom-vector-databases/)

**3자 출처: 보도, 블로그, 리뷰**

- [G-gen Next '26 리포트](https://blog.g-gen.co.jp/entry/next-26-keynote-day-1) · [Let's Data Science](https://letsdatascience.com/news/google-launches-gemini-enterprise-agent-platform-b2a6d446) · [GCP Study Hub](https://gcpstudyhub.com/blog/vertex-ai-replaced-by-gemini-enterprise-agent-platform) · [The Decoder](https://the-decoder.com/googles-gemini-api-now-supports-file-search-with-custom-data/)
- [Classmethod: Managed KB Agentic Retrieval](https://dev.classmethod.jp/articles/bedrock-managed-knowledge-base-retrieve-agentic-retrieval/) · [Classmethod: Managed KB ACL](https://dev.classmethod.jp/en/articles/20260914-amazon-mkb-s3-acl-with-quick/) · [Classmethod: NextGen GA](https://dev.classmethod.jp/en/articles/20260531-amazon-opensearch-service-nxgn-ga/)
- [cloudburn(OpenSearch)](https://cloudburn.io/blog/amazon-opensearch-pricing) · [bigdataboutique](https://bigdataboutique.com/) · [Binadox(Kendra)](https://www.binadox.com/?p=14819) · [re:Post 기사](https://repost.aws/articles/ARO2JXBG6cQZObXj0TZJ4gjg/) · [re:Post 질문](https://repost.aws/questions/QUVPl-znFxTuWTzU5ryqM0pQ/bedrock-opensearch-serverless-collection-unpredictable-search-ocu-costs)
- [CloudZero](https://www.cloudzero.com/blog/google-vertex-ai-pricing/) · [costbench](https://www.costbench.com/software/rag-pipelines/vertex-ai-search/hidden-costs/) · Digital Applied 가격 비교(2026-10-02) · [Atlan](https://atlan.com/know/ai-agent/aws/bedrock-managed-knowledge-base-vs-custom-rag-pipeline/)
- [DevClass 2021-04](https://devclass.com/2021/04/13/aws-debuts-opensearch-project-in-latest-round-of-elastic-licence-spat/) · [The New Stack](https://thenewstack.io/opensearch-3-3s-new-ai-agents-now-generally-available-for-developers/) · [SiliconANGLE(Vespa 분사)](https://siliconangle.com/2023/10/04/yahoo-spins-off-ai-scaling-engine-vespa-independent-company/) · [TechCrunch](https://techcrunch.com/2023/11/01/yahoo-spin-out-vespa-lands-31m-investment-from-blossom)
- [Vinted: Goodbye Elasticsearch, Hello Vespa](https://vinted.engineering/2024/09/05/goodbye-elasticsearch-hello-vespa/) · [PeerSpot(Vespa)](https://www.peerspot.com/landing/product-report-vespa) · [aicoolies(Vespa)](https://aicoolies.com/reviews/vespa-review) · Last9, Redis 비교 블로그
- [VentureBeat(Boomerang, 2023)](https://venturebeat.com/) · usagepricing.com(Vectara) · Unite.ai(Compass Cloud) · RuntimeWire(Embed 5) · Digital Today(OpenAI 한국 data residency, 2026-09-09) · dev.to(Assistants API 종료)

**커뮤니티** (원문 확인, 개인 의견)

- Reddit: [r/Rag 1f6pwt8](https://www.reddit.com/r/Rag/comments/1f6pwt8/) · [r/Rag 1s1c90j](https://www.reddit.com/r/Rag/comments/1s1c90j/) · [r/googlecloud 1quxh8k](https://www.reddit.com/r/googlecloud/comments/1quxh8k/) · [r/Rag 1synetk](https://www.reddit.com/r/Rag/comments/1synetk/) · [r/Rag 1usfkpd](https://www.reddit.com/r/Rag/comments/1usfkpd/) · [r/AZURE 1s4gjkd](https://www.reddit.com/r/AZURE/comments/1s4gjkd/) · [r/Rag 1mqp4qs](https://www.reddit.com/r/Rag/comments/1mqp4qs/)
- Hacker News items: 42956376, 45647032, 38766709, 49649464, 48102522, 43918805, 39945474
- OpenAI 포럼: [1313288](https://community.openai.com/t/1313288) · [1344113](https://community.openai.com/t/1344113) · [chunking 질문(2024)](https://community.openai.com/t/what-is-the-chunking-strategy-used-by-the-assistant/480086)
