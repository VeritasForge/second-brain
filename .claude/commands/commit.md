# /commit - Complete and Push Changes

작업을 마무리하고 변경사항을 커밋 및 푸시합니다.

## Usage

```
/commit              # 현재 세션의 모든 변경사항을 커밋 및 푸시
/commit [message]    # 커스텀 메시지로 커밋 및 푸시
```

## Workflow

작업 마무리 시 다음 단계를 자동으로 수행합니다:

1. **Context Update**: `CLAUDE.md`의 "Recent Changes" 업데이트
2. **Pre-Commit Checks**: 비밀 정보 확인, CLAUDE.md 업데이트 확인
3. **Status Check**: 변경된 파일 확인 (`git status`, `git diff HEAD`)
4. **Commit Message**: Conventional Commits 규칙에 따라 메시지 생성
5. **Commit**: 변경사항 스테이징 및 커밋
6. **Push**: 원격 저장소로 푸시
7. **Report**: 결과 보고

## Steps

### Step 1: Update CLAUDE.md (MANDATORY)

현재 세션에서 수행한 작업을 분석하고 `CLAUDE.md`의 "Recent Changes" 섹션을 업데이트합니다.

```bash
# CLAUDE.md 읽기
cat CLAUDE.md

# "Recent Changes" 섹션 업데이트
# - 새로운 변경사항을 맨 위에 추가
# - 간결하고 명확한 항목으로 작성
# - 형식: "- [Category]: [Brief description]"
```

**Update 예시:**
```markdown
## Recent Changes
- Note: Add RAG agent workflow concepts note
- Note: Add transformer architecture deep dive
- Config: Update Obsidian workspace settings
- Vault: Reorganize gen_ai directory structure
```

### Step 2: Pre-Commit Checks

커밋 전 다음 항목을 확인합니다:

- [ ] 비밀 정보 없음 (하드코딩된 API 키 등)
- [ ] CLAUDE.md 업데이트 완료

### Step 3: Check Status

변경된 파일을 확인합니다.

```bash
# 변경 파일 확인
git status

# 변경 내용 상세 확인
git diff HEAD
```

### Step 4: Generate Commit Message

Conventional Commits 규칙에 따라 커밋 메시지를 생성합니다.

**Format:**
```
<type>(<scope>): <subject>

[optional body]

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

**Types:**
- `feat`: 새로운 노트/콘텐츠
- `fix`: 오류 수정
- `docs`: 문서 변경 (README, CLAUDE.md)
- `refactor`: 구조 변경 (노트 이동, 재분류)
- `chore`: 설정, 유지보수

**Scopes (Den):**
- `gen-ai`: Generative AI 관련 노트
- `develop`: 개발 관련 노트
- `docs`: 일반 문서 (README, CLAUDE.md)
- `config`: Obsidian/프로젝트 설정
- `vault`: Vault 구조 변경

**Example Messages:**
```bash
# New note
feat(gen-ai): add RAG agent workflow concepts note

- Cover RAG pipeline architecture
- Include agent orchestration patterns
- Add LLM workflow comparison

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

# Fix
fix(gen-ai): correct transformer attention mechanism description

Fixed inaccurate description of multi-head attention
in the transformer architecture note.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

# Docs
docs(docs): update CLAUDE.md with new vault structure

Added develop/ category and updated note counts.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

# Restructure
refactor(vault): reorganize gen_ai notes into subcategories

Moved LLM-specific notes into gen_ai/llm/ subdirectory.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

### Step 5: Commit

변경사항을 스테이징하고 커밋합니다.

```bash
# 모든 변경사항 스테이징 (또는 특정 파일만)
git add .

# HEREDOC을 사용한 커밋 (포맷팅 보장)
git commit -m "$(cat <<'EOF'
feat(gen-ai): add RAG agent workflow concepts note

- Cover RAG pipeline architecture
- Include agent orchestration patterns

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

### Step 6: Push

원격 저장소로 푸시합니다.

```bash
# 현재 브랜치를 원격으로 푸시
git push

# 새 브랜치의 경우 upstream 설정
git push -u origin <branch-name>
```

### Step 7: Report

사용자에게 결과를 보고합니다.

```markdown
Changes successfully committed and pushed!

**Commit:** feat(gen-ai): add RAG agent workflow concepts note
**Branch:** main
**Files Changed:** 3 files (+150, -5)

**Summary:**
- CLAUDE.md updated
- 3 files committed
- Pushed to origin/main
```

## Edge Cases

### No Changes to Commit

```
No changes to commit. Working tree is clean.
```

### Push Conflict

```
Push rejected. Remote has changes.

Suggested action:
git pull --rebase
git push
```

### Uncommitted Changes in CLAUDE.md

CLAUDE.md 업데이트를 잊은 경우:

```
CLAUDE.md not updated. Please update "Recent Changes" section first.
```

## References

- `CLAUDE.md` - AI 컨텍스트
- `README.md` - 사용자 문서

## Example Session

```bash
User: /commit
```
