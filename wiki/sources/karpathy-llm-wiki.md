---
type: source
origin: ingest
confidence: high
source_path: "[[raw/articles/karpathy-llm-wiki]]"
date_created: 2026-04-09
tags: [knowledge-management, llm, wiki, obsidian]
---
# Karpathy의 LLM Wiki 패턴

## 핵심 주장
- RAG는 매 질문마다 원시 문서에서 정보를 재검색하므로 지식이 축적되지 않음
- LLM Wiki는 구조화된 마크다운 위키를 점진적으로 구축하여 지식을 영구 축적
- 3계층 아키텍처: Raw Sources(불변 원본) → Wiki(LLM 관리) → Schema(운영 규칙)
- 유지보수 부담을 LLM이 흡수하므로 위키가 지속적으로 유지됨
- 인간의 역할은 자료 선별, 방향 제시, 좋은 질문 — LLM은 그 외 모든 것

## 주요 인사이트
- index.md + log.md 이중 탐색 구조로 임베딩 기반 RAG 인프라 없이도 중간 규모(~100 소스, 수백 페이지)에서 효과적
- 정기적 lint 점검으로 모순, 고립 페이지, 누락된 상호 참조를 발견하여 위키 건강 유지
- 바네바 부시의 Memex(1945)와 정신적으로 관련 — 능동적으로 관리되는 개인 지식 저장소

## 인용할 만한 구절
> "위키는 유지보수 비용이 거의 들지 않기 때문에 지속적으로 유지 관리됩니다."
> "Obsidian은 IDE이고, LLM은 프로그래머이며, 위키는 코드베이스입니다."

## 관련 페이지
- [[llm-wiki-pattern]]
- [[rag]]
- [[obsidian]]
- [[rag-vs-llm-wiki]]
- [[knowledge-management]]
