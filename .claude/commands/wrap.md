# /wrap - Update Project Documentation

작업 완료 후 프로젝트 문서(README.md, CLAUDE.md)를 현재 Vault 상태에 맞게 업데이트합니다.

## Usage

```
/wrap              # 현재 Vault 분석 후 문서 업데이트
/wrap --check      # 문서와 Vault의 일치 여부만 확인 (업데이트 없음)
```

## Document Structure

이 프로젝트는 다음과 같은 문서 구조를 따릅니다:

- **README.md**: 사용자용 문서 (Vault 소개, 주제 목록, 사용법)
- **CLAUDE.md**: AI용 컨텍스트 (Vault 구조, 콘텐츠 카테고리, 최근 변경사항)
  - `@README.md`로 사용자 정보 참조
  - **중복 금지**: 사용자 정보는 README.md에만, AI 컨텍스트는 CLAUDE.md에만

## Workflow

1. **Analyze Vault**: 현재 디렉토리 구조 및 마크다운 파일 분석
2. **Read Documents**: README.md, CLAUDE.md 읽기
3. **Detect Changes**: 문서와 Vault 간 불일치 탐지
4. **Update Documents**: 변경사항 반영
5. **Report**: 업데이트 내역 보고

## Steps

### Step 1: Analyze Vault

현재 Vault의 구조를 분석합니다.

```bash
# Vault 전체 구조
tree -L 2

# 각 카테고리별 노트 수
find gen_ai -name "*.md" | wc -l
find develop -name "*.md" | wc -l

# 최근 추가/수정된 노트
git log --oneline -10
```

**분석 대상:**
- 디렉토리 구조 변경 (새 카테고리, 삭제된 카테고리)
- 새로운 노트 추가 또는 삭제
- 주제 범위 변화 (새 토픽 영역)
- Obsidian 설정 변경

### Step 2: Read Current Documents

기존 문서를 읽고 내용을 파악합니다.

```bash
# 사용자용 문서
cat README.md

# AI용 컨텍스트
cat CLAUDE.md
```

### Step 3: Detect Changes

문서와 Vault 간 불일치를 탐지합니다.

**체크리스트:**

#### README.md (User-Facing)
- [ ] Vault 소개: 설명이 현재 상태를 반영하는가?
- [ ] 주제 목록: 새 카테고리가 추가되었는가?
- [ ] 노트 수: 전체 노트 수가 최신인가?
- [ ] 사용법: Obsidian 사용 가이드가 최신인가?

#### CLAUDE.md (AI Context)
- [ ] @README.md import: 상단에 올바르게 참조하는가?
- [ ] Vault 구조: 디렉토리 구조가 최신인가?
- [ ] 콘텐츠 카테고리: 각 카테고리별 설명이 정확한가?
- [ ] 노트 목록: 각 카테고리별 노트 목록이 최신인가?
- [ ] Recent Changes: 최신 변경사항이 추가되었는가?
- [ ] 중복 체크: README.md와 내용이 중복되지 않는가?

### Step 4: Update Documents

탐지된 변경사항에 따라 문서를 업데이트합니다.

#### README.md Update Rules

**수정 대상:**
- Vault 소개 (범위가 변경된 경우)
- 주제 목록 (새 카테고리 추가 시)
- 노트 수 통계 (변경 시)

**수정하지 않음:**
- 프로젝트 목적 (변경되지 않는 한)

#### CLAUDE.md Update Rules

**수정 대상:**
```markdown
## Vault Structure (구조 변경 시)
- 디렉토리 트리 업데이트
- 카테고리별 노트 수 업데이트

## Content Categories (카테고리 변경 시)
- 새 카테고리 추가
- 카테고리별 노트 목록 업데이트

## Recent Changes (최상단에 추가)
- [New Entry]: [Description]
```

**수정하지 않음:**
- @README.md import (항상 유지)
- AI 작업 가이드라인 (프로세스 변경 시만)

**절대 추가하지 말 것:**
- 사용법 안내 (README.md에만)
- Vault 소개 (README.md에만)

### Step 5: Report Changes

업데이트 결과를 보고합니다.

```markdown
## Documentation Update Report

### README.md
Updated:
- 주제 목록: Added "develop" category
- 노트 수: 2 → 5

No changes needed

### CLAUDE.md
Updated:
- Vault Structure: Added develop/ directory
- Content Categories: Updated gen_ai note list
- Recent Changes: Added latest entries

No changes needed

### Summary
- 2 files updated
- 3 sections modified
- 0 inconsistencies remaining
```

## Update Guidelines

### Language
- **README.md**: 영어로 작성
- **CLAUDE.md**: 기존 언어 유지 (한국어/영어 혼용)

### Tone
- **README.md**: 사용자 친화적, 명확한 설명
- **CLAUDE.md**: 기술적, 구조적, AI가 이해하기 쉽게

### Format
- 기존 문서의 마크다운 형식 유지
- 섹션 구조 유지
- 코드 블록 스타일 일관성 유지

### Anti-Patterns

**Don't:**
- 같은 내용을 두 문서에 중복 작성
- README.md에 AI 전용 컨텍스트 추가 (Vault 구조 상세, 카테고리 분류 기준)
- CLAUDE.md에 사용자 정보 추가 (사용법, Vault 소개)
- @README.md import 제거하거나 수정
- 기존 섹션 구조를 크게 변경
- 문서에 없던 새 섹션을 임의로 추가

**Do:**
- CLAUDE.md 상단에 @README.md import 유지
- 사용자 정보(소개, 사용법)는 README.md에만
- AI 컨텍스트(구조, 카테고리, 노트 목록)는 CLAUDE.md에만
- 기존 형식과 톤 유지
- 명확하고 간결하게
- 변경사항만 업데이트 (불필요한 수정 지양)
- CLAUDE.md는 간결하게 유지 (200줄 이하 목표)

## Check Mode

`--check` 플래그를 사용하면 업데이트 없이 일치 여부만 확인합니다.

```bash
/wrap --check
```

**Output:**
```markdown
## Documentation Check Report

### README.md
Inconsistencies found:
- 주제 목록: "develop" category not documented
- 노트 수: Documented 2, actual 5

Consistent sections:
- Vault 소개
- 사용법

### CLAUDE.md
Inconsistencies found:
- Vault Structure: New directory "develop/" not documented
- Content Categories: 3 new notes not listed

Consistent sections:
- Recent Changes

### Action Required
Run `/wrap` to update documents automatically.
```

## Integration with Other Commands

`/wrap`은 다음 명령어들과 함께 사용됩니다:

```bash
# 노트 작업 → 문서 업데이트 → 커밋
# (노트 작성/수정)
/wrap
/commit
```

## Notes

- 문서 업데이트는 Vault 변경 후 수행해야 합니다
- `/wrap` 없이 `/commit`하면 경고 메시지가 표시될 수 있습니다
- 문서는 항상 현재 Vault 상태를 반영해야 합니다
- CLAUDE.md는 간결하게 유지 (200줄 이하 목표)
