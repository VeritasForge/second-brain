---
name: save_obsi
description: 직전 대화 결과를 Obsidian vault의 raw/sources/에 마크다운 파일로 저장합니다.
allowed-tools: Bash, Write, Read, Glob
---

# Save to Obsidian Vault (raw/sources/)

직전 대화에서 출력된 결과를 `raw/sources/`에 마크다운 파일로 저장합니다.
LLM Wiki 패턴에 따라 raw/sources/에 저장한 후, /ingest로 wiki 통합 여부를 확인합니다.

**Usage:**
- `/save_obsi` — 직전 대화 결과를 raw/sources/에 저장
- `/save_obsi <slug>` — 지정된 slug로 파일명 생성

```
Parse the user's input from: $ARGUMENTS

## Step 1: Vault Root 결정

Vault root는 `~/den/Den`으로 고정.
`~`를 사용자 홈 디렉토리로 확장.

## Step 2: Determine File Name

Look at the conversation history BEFORE this command was invoked.
Analyze the most recent substantive output (the last assistant response before this command).

파일명 형식: `<YYYY-MM-DD>-<slug>.md`

- $ARGUMENTS에 slug가 주어지면 그것을 사용
- 없으면 대화 내용에서 자동 생성:
  - Use the main topic or subject as the slug
  - Use lowercase with hyphens for spaces (kebab-case)
  - Keep slug under 50 characters
  - Examples: `2026-04-09-clean-architecture-overview.md`, `2026-04-09-jwt-authentication-flow.md`

## Step 3: Prepare Content

Take the most recent substantive assistant output and format it as a clean markdown file.

Add YAML front matter at the top (raw 원본이므로 태그 불필요 — /ingest 시 LLM이 자동 부여):

---
created: <current date in YYYY-MM-DD format>
source: claude-code
---

Then include the full content of the last assistant response with the following formatting rules applied:

### 3-1. Table Formatting (CRITICAL)

Tables MUST be valid, well-formed markdown tables for Obsidian to render them correctly. Apply these rules:

1. **Every table MUST have a header separator row**: `| --- | --- |` immediately after the header row. If missing, add it.
2. **Column alignment**: Pad every cell with spaces so that `|` delimiters in each column are vertically aligned. This ensures Obsidian's live preview renders correctly.
3. **Pipe escaping**: If cell content contains a literal `|` character, escape it as `\|`.
4. **No trailing/leading whitespace issues**: Each row must start and end with `|`.
5. **Empty cells**: Use a single space ` ` inside empty cells, never leave them completely empty (`||`).

6. **Nested content in cells**: If a cell contains inline code, bold, or links, preserve them but ensure the pipe alignment still holds.
7. **Wide tables**: If a table has many columns, still maintain alignment. Do not break a single table row across multiple lines.

### 3-2. Other Markdown Formatting

- Preserve all headings, code blocks, lists, bold, italic, links, and blockquotes as-is.
- Ensure code blocks use triple backticks with language identifiers when available.
- Ensure there is a blank line before and after headings, code blocks, tables, and blockquotes for proper Obsidian rendering.
- Horizontal rules: use `---` on its own line with blank lines before and after.

## Step 4: Ensure Directory Exists

Create the target directory if it doesn't exist:
  mkdir -p <vault_root>/raw/sources

## Step 5: Check Duplicate & Save File

저장 경로: `<vault_root>/raw/sources/<YYYY-MM-DD>-<slug>.md`

BEFORE writing, check if a file with the same name already exists.

Use Bash to check:
  ls "<vault_root>/raw/sources/<filename>" 2>/dev/null

- If the file does NOT exist: save as-is.
- If the file ALREADY exists: append an incrementing numeric suffix to the base name.
  - Try `-2`, then `-3`, `-4`, ... until a non-existing name is found.

CRITICAL: NEVER overwrite an existing file. Always verify before writing.

## Step 6: Report & Ingest 확인

Report the result:

**Saved:** <filename>
**Path:** <full_file_path>
**Size:** <file size in human-readable format>

저장 완료 후 사용자에게 확인:

```
/ingest로 wiki에 통합할까요? (y/n)
```

- y: `/ingest <저장된_파일_경로>` 실행을 안내
- n: 저장만 완료하고 종료
```
