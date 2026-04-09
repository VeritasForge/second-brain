---
name: ingest
description: 외부 소스를 raw/에 저장하고 wiki 페이지를 생성/업데이트하는 LLM Wiki ingest 스킬
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
---

# /ingest — LLM Wiki Ingest

외부 소스를 raw/에 저장하고, wiki 페이지를 생성/업데이트하며, index.md + log.md를 갱신합니다.

**Usage:**
- `/ingest <파일경로>` — 단일 파일 interactive ingest
- `/ingest <파일경로1> <파일경로2> ...` — 복수 파일 interactive ingest
- `/ingest --auto <파일경로>` — non-interactive (사용자 확인 skip)
- `/ingest --auto <파일경로1> <파일경로2> ...` — non-interactive 복수 파일 병렬 처리

```
Parse the user's input from: $ARGUMENTS

## Step 0: WIKI-SCHEMA.md 로드 (필수 — 모든 모드 공통)

반드시 Read 도구로 `wiki/WIKI-SCHEMA.md`를 읽는다.
이 파일은 자동 로딩되지 않으므로 명시적 Read가 필수.
스키마를 읽지 않으면 이후 모든 작업을 중단한다.

## Step 1: 인자 파싱

$ARGUMENTS 문자열을 파싱한다.

### --auto 플래그 감지
- $ARGUMENTS 문자열의 시작 부분이 `--auto`로 시작하는지 확인
- `--auto`가 있으면: non-interactive 모드 (사용자 확인 단계를 모두 skip)
- `--auto`가 없으면: interactive 모드 (각 단계에서 사용자 확인)

### 파일 경로 파싱
- `--auto` 제거 후 나머지를 공백으로 split하여 파일 경로 목록 추출
- 파일 경로가 1개면 → 단일 파일 워크플로
- 파일 경로가 2개 이상이면 → 복수 파일 워크플로

## Step 2: 분기 — 단일 vs 복수

### A. 단일 파일 워크플로

#### A-1. 소스를 raw/ 하위에 저장

파일 내용을 분석하여 적절한 하위 디렉토리를 결정:
- `raw/articles/` — 블로그 글, gist, 아티클
- `raw/papers/` — 학술 논문, 기술 리포트
- `raw/transcripts/` — 강연, 영상 트랜스크립트

파일이 이미 raw/ 안에 있으면 이 단계를 skip.

**interactive 모드**: 분류 결과를 사용자에게 보여주고 확인 요청.
**--auto 모드**: 분류를 자동 결정하고 판단 근거를 기록.
  예: "→ raw/articles/ 분류 — URL 도메인이 blog, 텍스트 형식이 아티클"

#### A-2. wiki/sources/ 요약 카드 생성

raw 원본을 읽고 wiki/sources/ 에 요약 카드를 생성한다.

Frontmatter 규격 (WIKI-SCHEMA.md 준수):
```yaml
---
type: source
origin: ingest
confidence: <high|medium|low>
source_path: "[[raw/articles/파일명]]"
date_created: YYYY-MM-DD
tags: [tag1, tag2]
---
```

**주의사항:**
- `source_path`만 full path 사용 (`"[[raw/articles/파일명]]"`) — raw와 wiki 파일명이 동일할 수 있으므로
- 그 외 모든 wikilink는 shortest-path 사용 (`[[파일명]]`)
- confidence 판단 기준:
  - high: 3개 이상 출처로 교차검증 가능
  - medium: 1-2개 출처
  - low: 미검증 또는 단일 주장

**interactive 모드**: 요약 카드 내용을 사용자에게 보여주고 확인.
**--auto 모드**: 자동 생성. confidence 판단 근거를 기록.
  예: "confidence: medium 설정 — 출처 URL 2개 확인, 교차검증 미완료"

#### A-3. 관련 wiki 페이지 업데이트/생성

소스에서 추출한 핵심 개념, 엔티티, 비교 분석을 식별한다.

1. **기존 페이지 확인**: index.md를 읽어 관련 기존 페이지가 있는지 확인
2. **기존 페이지 업데이트**: 관련 내용이 있으면 해당 페이지에 새 정보 추가 + `## 관련 페이지` 섹션에 wikilink 추가
3. **새 페이지 생성**: 기존에 없는 개념/엔티티는 새 페이지 생성
   - wiki/concepts/ — 단일 개념 심층 설명
   - wiki/entities/ — 기술/도구/인물/조직 정의
   - wiki/synthesis/ — 비교, 종합, 분석 리포트

모든 페이지는 WIKI-SCHEMA.md의 frontmatter 규격을 준수.
모든 wikilink는 shortest-path: `[[rag]]`, `[[obsidian]]` (경로 없이 파일명만).
모든 페이지에 `## 관련 페이지` 섹션 필수.

**interactive 모드**: 생성/업데이트할 페이지 목록을 보여주고 사용자 확인.
**--auto 모드**: 자동 결정. 각 페이지의 생성/업데이트 이유를 기록.

#### A-4. index.md 갱신

index.md의 Wiki 페이지 섹션에 새로 생성된 페이지를 추가한다.
각 항목은 `- [[파일명]] — 한 줄 요약` 형태 (shortest-path wikilink).
해당 유형(Sources, Entities, Concepts, Synthesis, MOC)의 섹션에 알파벳순으로 삽입.

#### A-5. log.md에 항목 추가

log.md 끝에 ingest 항목을 추가한다.

형식:
```markdown
## [YYYY-MM-DD] ingest | <소스 제목>
- source: [[raw/<type>/<파일명>]]
- created: [[페이지1]], [[페이지2]], ...
- updated: [[기존페이지1]], ... (업데이트한 경우)
```

#### A-6. 변경 요약 보고

최종 결과를 사용자에게 보고한다:
- raw/ 저장 위치
- 생성된 wiki 페이지 목록
- 업데이트된 wiki 페이지 목록
- index.md, log.md 갱신 여부

### B. 복수 파일 워크플로

1. 파일 경로 목록을 파싱한다.
2. 각 파일에 대해 Agent 도구를 사용하여 독립적인 subagent로 dispatch한다.
   - 각 subagent에게 단일 파일 워크플로(A-1 ~ A-6)를 수행하도록 지시
   - subagent 프롬프트에 WIKI-SCHEMA.md 규칙 요약을 포함
   - --auto 모드 여부를 subagent에 전달
3. 모든 subagent 완료 후 결과를 집계한다.
4. 전체 성공/실패 요약을 보고한다:
   - 성공: N개 파일 처리 완료
   - 실패: 파일명 + 오류 원인 목록
5. index.md, log.md는 subagent들이 각각 갱신하므로, 최종적으로 중복/정렬 정리를 수행한다.

## 규칙 요약

1. wiki/WIKI-SCHEMA.md를 먼저 Read한다 (Step 0)
2. source_path만 full path (`"[[raw/articles/파일명]]"`), 나머지는 shortest-path (`[[파일명]]`)
3. 모든 wiki 페이지에 `## 관련 페이지` 섹션 필수
4. frontmatter의 confidence 필드에 판단 근거 기록 (--auto 모드)
5. --auto 모드에서 skip한 모든 판단 지점에 선택 이유를 기록
6. 태그는 flat하게 사용 (계층 없음), 최소 2개
7. 파일명 유일성 유지 (wiki/와 old_wiki/에 같은 이름 금지)
```
