---
type: concept
origin: ingest
confidence: high
date_created: 2026-04-09
tags: [knowledge-management, llm, wiki]
---
# LLM Wiki 패턴

## 한 줄 정의
LLM이 구조화된 마크다운 위키를 점진적으로 구축하고 유지 관리하여, 쿼리 시점 재검색 대신 지식을 영구 축적하는 패턴.

## 핵심 메커니즘
- 새 소스가 추가되면 LLM이 읽고 → 요약 카드 생성 → 기존 위키 페이지 업데이트 → 상호 참조 추가
- 모순되는 정보 발견 시 기존 페이지에 표시
- index.md로 전체 탐색, log.md로 작업 이력 추적
- 정기 lint 점검으로 위키 건강 유지

## 3계층 아키텍처
| 계층 | 역할 | 관리 주체 | 변경 여부 |
|------|------|----------|----------|
| Raw Sources | 원본 자료 | 인간이 수집 | 불변 |
| Wiki | 구조화된 마크다운 | LLM이 관리 | LLM이 지속 업데이트 |
| Schema | 운영 규칙 (CLAUDE.md) | 인간 + LLM 협업 | 점진적 발전 |

## 장점과 한계
| 장점 | 한계 |
|------|------|
| 지식이 축적됨 (매번 재검색 불필요) | 초기 구조 설계 비용 |
| 상호 참조가 자동 유지됨 | AI 환각이 영구 사실로 고정될 위험 (confidence로 완화) |
| 유지보수를 LLM이 흡수 | 대규모 시 index.md만으로 탐색 한계 (검색 엔진 필요) |

## 관련 페이지
- [[rag]] — 대비 패턴
- [[obsidian]] — 권장 뷰어
- [[karpathy-llm-wiki]] — 원본 출처

## 출처
- [[karpathy-llm-wiki]]
- [Karpathy LLM Wiki Gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
