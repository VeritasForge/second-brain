# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an **Obsidian knowledge vault** ("Den") for personal study notes, primarily covering Generative AI and software development topics. It is not a software project — there are no build, lint, or test commands.

## Vault Structure

```
Den/
├── raw/             # 원본 자료 (불변, LLM 읽기 전용)
│   ├── articles/    # 웹 클리핑
│   ├── papers/      # 논문, PDF
│   ├── transcripts/ # 팟캐스트, 영상 스크립트
│   ├── sources/     # /save_obsi 원본 보관
│   └── assets/      # 이미지, 첨부파일
├── wiki/            # 모든 노트 (자유 형식)
│   ├── security/
│   ├── gen_ai/
│   ├── develop/
│   ├── ai-engineering/
│   ├── algorithm/
│   ├── career/
│   ├── research/
│   └── mac-os/
├── index.md         # 전체 문서 카탈로그
├── log.md           # 시간순 변경 이력 (append-only)
└── CLAUDE.md
```

## Custom Commands

- `/wrap` — Analyzes the vault and updates README.md + CLAUDE.md to reflect current state. Run after adding/modifying notes.
- `/commit` — Updates CLAUDE.md "Recent Changes", commits with Conventional Commits format, and pushes. Always includes `Co-Authored-By` trailer.

Typical workflow after note changes: `/wrap` → `/commit`

## Commit Conventions

Uses Conventional Commits with vault-specific scopes:
- Types: `feat`, `fix`, `docs`, `refactor`, `chore`
- Scopes: `gen-ai`, `develop`, `algorithm`, `research`, `security`, `mac-os`, `docs`, `config`, `vault`
- Example: `feat(gen-ai): add RAG agent workflow concepts note`

## Document Separation Rules

- **README.md**: User-facing only (vault intro, topic list, usage guide)
- **CLAUDE.md**: AI context only (vault structure, content categories, recent changes)
- No duplication between the two documents
- CLAUDE.md references README.md via `@README.md` at top for user info
- Target: keep CLAUDE.md under 200 lines

## Content Categories

- **gen_ai/**: RAG, agent workflows, LLM pipeline, transformer architecture, multi-agent orchestration
- **ai-engineering/**: Claude Code hooks, Ralph Loop, Ouroboros, superpowers integration
- **develop/**: git, database, frontend (fe/), claude-code, k8s, os, slack, python, go, architecture, performance
- **algorithm/**: coding test strategies, backtracking, bit manipulation
- **research/**: market research, industry analysis, deep research reports
- **security/**: AWS IAM (User, Group, Policy, Role), Nginx audit, TPM, OAuth, SSO, financial API security
- **career/**: job analysis, interview Q&A
- **mac-os/**: macOS configuration

## Vault 운영

문서는 자유 형식으로 wiki/ 하위 카테고리에 저장한다. raw/는 원본 소스(PDF, 웹 스크랩 등) 보관용이며 LLM은 읽기만 한다.

### index.md (문서 카탈로그)
- wiki/ 전체 문서 목록을 카테고리별로 관리
- **읽기**: 사용자가 문서를 찾거나, 관련 노트를 탐색할 때 먼저 index.md를 읽어 위치를 파악
- **쓰기**: 문서를 추가/삭제/이동할 때 반드시 index.md도 함께 갱신
- 형식: `- [[파일명]] — 한줄 설명` (카테고리 섹션 내 알파벳순)
- **경로 규칙**: 섹션 헤더가 곧 wiki/ 하위 경로. 예: `### develop/claude-code` 섹션의 `[[foo]]` → `wiki/develop/claude-code/foo.md`

### log.md (변경 이력)
- 문서 변경사항을 시간순으로 기록 (append-only, 최신이 위)
- **읽기**: 새 세션 시작 시 최근 5-10개 항목을 읽어 직전 작업 맥락을 파악
- **쓰기**: 문서를 추가/수정/삭제할 때 맨 위에 항목 추가
- 형식: `## [YYYY-MM-DD] action | 제목` (action: create, update, delete, restructure)
- 하위에 `- created: [[파일명]]` 또는 `- updated: [[파일명]]` 등 상세 기록
