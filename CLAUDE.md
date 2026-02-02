# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an **Obsidian knowledge vault** ("Den") for personal study notes, primarily covering Generative AI and software development topics. It is not a software project — there are no build, lint, or test commands.

## Vault Structure

```
Den/
├── gen_ai/          # Generative AI notes (RAG, agents, LLM, transformers)
├── develop/         # Software development notes
├── .obsidian/       # Obsidian settings and plugins (terminal plugin enabled)
└── .claude/         # Claude Code commands and settings
```

## Custom Commands

- `/wrap` — Analyzes the vault and updates README.md + CLAUDE.md to reflect current state. Run after adding/modifying notes.
- `/commit` — Updates CLAUDE.md "Recent Changes", commits with Conventional Commits format, and pushes. Always includes `Co-Authored-By` trailer.

Typical workflow after note changes: `/wrap` → `/commit`

## Commit Conventions

Uses Conventional Commits with vault-specific scopes:
- Types: `feat`, `fix`, `docs`, `refactor`, `chore`
- Scopes: `gen-ai`, `develop`, `docs`, `config`, `vault`
- Example: `feat(gen-ai): add RAG agent workflow concepts note`

## Document Separation Rules

- **README.md**: User-facing only (vault intro, topic list, usage guide)
- **CLAUDE.md**: AI context only (vault structure, content categories, recent changes)
- No duplication between the two documents
- CLAUDE.md references README.md via `@README.md` at top for user info
- Target: keep CLAUDE.md under 200 lines

## Content Categories

### gen_ai/
- RAG, agent workflows, LLM pipeline concepts
- Token systems, transformer architecture deep dives

### develop/
- Software development topics (currently empty, reserved for future notes)

## Recent Changes
- Docs: Add CLAUDE.md and README.md for vault documentation
- Initial vault setup with gen_ai notes and Obsidian configuration
