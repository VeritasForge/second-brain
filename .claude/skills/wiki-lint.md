---
name: wiki-lint
description: wiki 전체의 건강 상태를 점검하고 수정 가능한 항목을 자동 수정하는 LLM Wiki lint 스킬
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# /wiki-lint — LLM Wiki Lint

wiki 전체의 건강 상태를 점검하고, 수정 가능한 항목을 자동 수정하며, 리포트를 생성합니다.

**Usage:**
- `/wiki-lint` — 전체 점검 + 자동 수정 + 리포트 생성
- `/wiki-lint --dry-run` — 점검만 수행, 수정하지 않음

```
Parse the user's input from: $ARGUMENTS

## Step 0: WIKI-SCHEMA.md 로드 (필수)

반드시 Read 도구로 `wiki/WIKI-SCHEMA.md`를 읽는다.
이 파일은 자동 로딩되지 않으므로 명시적 Read가 필수.
스키마를 읽지 않으면 이후 모든 작업을 중단한다.

## Step 1: --dry-run 플래그 확인

- $ARGUMENTS에 `--dry-run`이 포함되어 있으면: 점검만 수행, 수정하지 않음
- 없으면: 점검 + 자동 수정

## Step 2: wiki/ 전체 파일 스캔

Glob으로 `wiki/**/*.md`를 스캔하여 모든 wiki 페이지 목록을 수집한다.
각 페이지의 frontmatter와 본문을 Read로 읽는다.

## Step 3: 점검 항목 실행

아래 7가지 항목을 순서대로 점검한다. 각 항목의 결과를 issues 목록에 기록.

### 3-1. 페이지 간 모순 점검

같은 주제를 다루는 페이지들에서 상충하는 주장이 있는지 확인한다.
- 같은 태그를 가진 페이지들을 그룹화
- 핵심 주장/정의가 서로 다른 경우 모순으로 기록
- severity: warning

### 3-2. 오래된 주장 점검 (stale)

`date_created` 또는 `date_updated`로부터 6개월 이상 경과한 페이지를 식별한다.
- 오늘 날짜 기준으로 계산
- 해당 페이지의 frontmatter에 `status: stale` 표시 (--dry-run이 아닌 경우)
- severity: info

### 3-3. 고립 페이지 점검 (orphan)

inbound link가 0개인 페이지를 식별한다.
- 전체 wiki 페이지에서 wikilink를 추출
- 어떤 페이지에서도 참조되지 않는 페이지 = 고립
- index.md에서의 참조는 제외 (index는 카탈로그이므로)
- moc 페이지는 허브이므로 inbound 0이어도 고립으로 간주하지 않음
- severity: warning

### 3-4. 빨간 링크 점검 (dangling reference)

wikilink가 가리키는 파일이 실제로 존재하지 않는 경우를 식별한다.
- `[[파일명]]` 형태의 모든 wikilink를 추출
- 해당 파일명.md가 vault 어디에도 없으면 빨간 링크
- severity: error

### 3-5. 누락된 상호 참조 점검

A 페이지가 B를 참조하지만, B의 `## 관련 페이지`에 A가 없는 경우를 식별한다.
- 양방향 참조가 WIKI-SCHEMA.md 규칙이므로 누락은 수정 대상
- --dry-run이 아닌 경우: B의 `## 관련 페이지`에 A를 자동 추가
- severity: warning

### 3-6. index.md 불일치 점검

index.md의 Wiki 페이지 목록과 실제 wiki/ 파일을 대조한다.
- wiki/에 있지만 index.md에 없는 파일 → 누락
- index.md에 있지만 wiki/에 없는 항목 → 유령 항목
- --dry-run이 아닌 경우: index.md를 자동 수정
- severity: error

### 3-7. confidence: low 페이지 검증

confidence: low인 페이지를 식별하고, 출처가 추가되었는지 확인한다.
- 출처 URL이 3개 이상 → confidence를 medium 또는 high로 승격 가능
- --dry-run이 아닌 경우: 승격 가능한 페이지의 confidence를 자동 업데이트
- severity: info

## Step 4: 리포트 생성

점검 결과를 `wiki/reports/lint-report-YYYY-MM-DD.md`에 저장한다.

리포트 형식:
```markdown
---
type: report
origin: lint
date_created: YYYY-MM-DD
tags: [wiki-maintenance, lint]
---
# Wiki Lint Report — YYYY-MM-DD

## 요약
- 전체 페이지: N개
- 이슈 발견: N개 (error: N, warning: N, info: N)
- 자동 수정: N개 (--dry-run이면 "0개 (dry-run 모드)")

## Error
(error 항목 나열)

## Warning
(warning 항목 나열)

## Info
(info 항목 나열)

## 자동 수정 내역
(수정한 내용 나열, --dry-run이면 "수정 없음")
```

## Step 5: index.md + log.md 갱신

- index.md의 Reports 섹션에 새 리포트 추가
- log.md에 lint 항목 추가:

```markdown
## [YYYY-MM-DD] lint | Wiki 건강 점검
- report: [[lint-report-YYYY-MM-DD]]
- issues: error N, warning N, info N
- fixed: N개 자동 수정
```

## Step 6: 결과 보고

사용자에게 점검 결과 요약을 보고한다:
- 전체 페이지 수
- 발견된 이슈 수 (severity별)
- 자동 수정된 항목 수
- 리포트 파일 경로
```
