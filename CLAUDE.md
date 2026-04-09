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
│   └── assets/      # 이미지, 첨부파일
├── wiki/            # LLM 관리 위키 — 규칙은 wiki/WIKI-SCHEMA.md 참조
├── old_wiki/        # 기존 노트 (수정 금지, shortest-path wikilink로 참조)
├── index.md         # 전체 위키 카탈로그 (LLM 자동 관리)
├── log.md           # 시간순 작업 이력 (append-only)
└── CLAUDE.md        # wiki/WIKI-SCHEMA.md 참조
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
- **security/**: Nginx audit, TPM, OAuth, SSO, financial API security
- **career/**: job analysis, interview Q&A
- **mac-os/**: macOS configuration

## Wiki 운영

wiki 관련 작업 시 반드시 `wiki/WIKI-SCHEMA.md`를 먼저 읽어라. 이 파일에 frontmatter 규격, 태그 규칙, wikilink 규칙, 워크플로가 정의되어 있다.

새 세션 시작 시 `log.md`의 최근 5-10개 항목을 확인하여 직전 작업 맥락을 파악한다.
