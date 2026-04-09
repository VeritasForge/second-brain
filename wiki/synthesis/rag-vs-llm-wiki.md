---
type: synthesis
origin: ingest
confidence: high
date_created: 2026-04-09
tags: [comparison, rag, llm-wiki, knowledge-management]
---
# RAG vs LLM Wiki 패턴 비교

## 비교 축
| 기준 | RAG | LLM Wiki |
|------|-----|----------|
| 지식 축적 | X (매번 재검색) | O (영구 축적) |
| 초기 비용 | 낮음 (업로드만) | 높음 (구조 설계 필요) |
| 유지보수 | 없음 | LLM이 자동 수행 |
| 다문서 종합 | 약함 (매번 재조합) | 강함 (이미 종합됨) |
| 환각 위험 | 낮음 (원본 직접 참조) | 중간 (confidence 필드로 완화) |
| 확장성 | 임베딩 DB 필요 | index.md → 검색 엔진으로 점진 확장 |
| 상호 참조 | 없음 | 자동 유지 (wikilink) |

## 결론
- RAG는 "검색 시점" 패턴, LLM Wiki는 "축적 시점" 패턴
- 빠른 질의 응답에는 RAG가 유리하지만, 장기적 지식 구축에는 LLM Wiki가 우위
- 두 패턴은 배타적이지 않음: 위키가 커지면 위키 내부 검색에 RAG 기법(벡터 검색) 적용 가능

## 관련 페이지
- [[rag]]
- [[llm-wiki-pattern]]

## 출처
- [[karpathy-llm-wiki]]
