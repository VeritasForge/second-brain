---
type: concept
origin: ingest
confidence: high
date_created: 2026-04-09
tags: [rag, retrieval, llm, gen-ai]
---
# RAG (Retrieval-Augmented Generation)

## 한 줄 정의
외부 문서에서 관련 정보를 쿼리 시점에 검색하여 LLM 응답에 포함하는 패턴.

## 핵심 메커니즘
- 사용자 질문 → 임베딩 벡터로 변환 → 벡터 DB에서 유사 문서 검색 → LLM 컨텍스트에 삽입 → 답변 생성
- 매 질문마다 검색을 반복하므로 지식이 축적되지 않음

## 장점과 한계
| 장점 | 한계 |
|------|------|
| 설정이 간단 (문서 업로드만) | 매번 처음부터 재검색 |
| 최신 데이터 즉시 반영 | 여러 문서 종합이 필요한 질문에 약함 |
| 환각 위험 낮음 (원본 직접 참조) | 지식이 축적되지 않음 |

## 관련 페이지
- [[llm-wiki-pattern]] — 대안 패턴
- [[rag-vs-llm-wiki]] — 비교 분석
- [[genai-rag-agent-llm-workflow-concepts]] — 기존 레거시 RAG 노트

## 출처
- [[karpathy-llm-wiki]]
