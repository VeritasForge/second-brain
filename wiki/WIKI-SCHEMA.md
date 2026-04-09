# Wiki Schema — Den Vault 위키 운영 규칙

> 이 파일은 LLM이 wiki/ 작업 시 반드시 참조해야 하는 규칙을 정의합니다.

## 디렉토리 역할
- `raw/` — 원본 자료. LLM은 읽기만 하고 절대 수정하지 않음
- `wiki/` — LLM이 전적으로 관리
- 기존 카테고리 폴더 (gen_ai/, develop/ 등) — 기존 노트. 수정 금지. wiki에서 wikilink로 참조 가능

## 페이지 유형
| 유형 | 경로 | 설명 |
|------|------|------|
| source | wiki/sources/ | raw 원본 1:1 요약 카드 |
| entity | wiki/entities/ | 기술/도구/인물/조직 사전적 정의 |
| concept | wiki/concepts/ | 단일 개념 심층 설명 |
| synthesis | wiki/synthesis/ | 비교, 종합, 분석 리포트 |
| moc | wiki/moc/ | Map of Content (주제 허브) |
| report | wiki/reports/ | 운영 리포트 (lint 점검 등) |

## Frontmatter 필수 필드 (wiki/ 페이지)
- `type`: source | entity | concept | synthesis | moc | report
- `origin`: ingest | deep-research | concept-explainer | manual | lint
- `confidence`: high (3+ 출처 교차검증) | medium (1-2 출처) | low (미검증) — moc, report 제외
- `date_created`: YYYY-MM-DD
- `tags`: [tag1, tag2] — flat 태그, 최소 2개. 마스터 목록은 index.md에서 관리

## 선택 필드
- `source_path`: source 유형만. `"[[raw/...]]"` 형태
- `category`: entity 유형만. tool | person | org | framework | language | service
- `date_updated`: YYYY-MM-DD
- `status`: draft | active | stale | archived

## Wikilink 규칙
- **Obsidian 설정**: `newLinkFormat: shortest` (기본값) — 파일명만으로 링크
- 모든 wiki 페이지에 `## 관련 페이지` 섹션 필수
- shortest-path wikilink: `[[rag]]`, `[[rsc-deep-dive]]` (경로 없이 파일명만)
- 외부 URL: `[제목](https://...)` 마크다운 링크
- 태그 = 분류, wikilink = 연결
- 파일명 유일성 유지 (wiki/와 old_wiki/에 같은 이름 금지)
- **예외**: frontmatter의 `source_path` 필드는 full path 사용 (`"[[raw/articles/파일명]]"`) — raw 원본과 wiki 파일의 이름이 동일할 수 있으므로

## 워크플로
- **Interactive ingest (경로 A)**: raw/ 저장 → wiki/sources/ 요약 카드 → wiki 페이지 생성/업데이트 → index.md + log.md 갱신
- **Interactive ingest (경로 A-2)**: /save_obsi → raw/sources/에 저장 → /ingest로 wiki 통합
- **Interactive ingest (경로 B)**: LLM 생성 노트 → wiki/에 바로 생성 (origin 기록, 출처 URL 기록) → index.md + log.md 갱신
- **Batch ingest**: Cronicle → 브랜치 → Claude Code headless (non-interactive) → PR → 사용자 리뷰
- **Query**: index.md 탐색 → wiki 페이지 읽기 → 답변 → synthesis 저장 시 query+create 2건 기록
- **Lint**: Cronicle 월 1회 → 모순/고립/stale/low confidence 점검 → PR

## index.md / log.md 규칙
- `/ingest` 실행 시 반드시 index.md, log.md 동시 갱신
- log.md 형식: `## [YYYY-MM-DD] action | 제목`
- **log action enum**: `ingest` (소스 수집), `create` (페이지 생성), `update` (페이지 수정), `query` (질의 응답), `lint` (점검)
- query 후 synthesis 저장 시: query 1건 + create 1건 = 2건 기록
- ingest 시: ingest 1건으로 기록 (created 필드에 생성된 페이지 목록 포함). 별도 create 항목 불필요
- 새 세션 시작 시 log.md 최근 5-10개 항목 확인하여 직전 작업 맥락 파악
- index.md 불일치는 `/wiki-lint`가 월 1회 점검

## Query 워크플로 (LLM이 위키에 질문받을 때)
1. index.md 읽기 → 관련 페이지 식별
2. 관련 wiki 페이지 읽기
3. 필요시 기존 노트(old_wiki/)도 참조
4. 더 깊은 근거 필요 시 → sources 페이지의 출처를 따라 raw 원본까지 확인
5. 답변 생성 (인용 포함)
6. 좋은 답변이면 → synthesis 저장 여부 사용자에게 확인
