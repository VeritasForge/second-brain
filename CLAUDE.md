# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an **Obsidian knowledge vault** ("Den") for personal study notes, primarily covering Generative AI and software development topics. It is not a software project — there are no build, lint, or test commands.

## Vault Structure

```
Den/
├── gen_ai/          # Generative AI notes (RAG, agents, LLM, transformers)
├── ai-engineering/  # AI engineering practices (Claude Code, Ralph Loop, hooks)
├── develop/         # Software development (git, database, web, slack, claude-code)
│   ├── git/         # Git workflows and branching strategies
│   ├── database/    # Database concepts (cardinality, SQLite)
│   ├── claude-code/ # Claude Code rules, skill practices
│   └── slack/       # Slack integration patterns
├── algorithm/       # Coding test prep, algorithm patterns
├── research/        # Market research, industry analysis
├── security/        # Security auditing, TPM
├── mac-os/          # macOS tips and configuration
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
- Scopes: `gen-ai`, `develop`, `algorithm`, `research`, `security`, `mac-os`, `docs`, `config`, `vault`
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
- Claude Code internals, multi-agent orchestration
- Evaluator-optimizer patterns, project architecture analysis
- Google AI Studio to Claude Code migration, skills invocation optimization

### ai-engineering/
- Claude Code plugin hooks system deep dive
- Ralph Loop playbook (Korean translation)
- Ralph + Superpowers + Compound integration guide

### develop/
- Git workflows: trunk-based development, rebase, backport, branch diff, rebase --onto
- TBD practice monorepo guide
- Database: cardinality, SQLite deep dive
- Modern web architecture: BFF, SSR, SPA, Vite, SEO, React hydration, Googlebot crawling
- Claude Code: rules vs CLAUDE.md, skill/EDD/TDD best practices
- Slack: Socket Mode vs HTTP comparison
- General: greenfield project concepts

### algorithm/
- Coding test preparation strategies
- Backtracking patterns, subarray/subsequence/subset distinctions

### research/
- Market research and fact-checking reports
- Multi-perspective analysis (kick-quality-focus series)
- Industrial revolution (4th/5th) deep research
- Ralph Loop deep research, kick cafe research detail

### security/
- Nginx security auditing
- TPM architecture and authentication deep dives
- Solo developer financial API security
- TPM UserWithAuth vs PCR deep research

### mac-os/
- macOS system configuration (lid close behavior)

## Recent Changes
- Add develop/: Googlebot crawling mechanism SEO, React hydration SSR deep dive
- Add ai-engineering/: Claude Code hooks, Ralph Loop playbook, superpowers integration
- Add develop/claude-code/: rules vs CLAUDE.md, skill/EDD/TDD practices
- Add develop/database/sqlite/: SQLite deep dive
- Add develop/git/: rebase --onto, TBD monorepo guide
- Add develop/: modern web architecture (BFF/SSR/SPA), Slack Socket Mode
- Add gen_ai/: skills optimization, Google AI Studio migration, core components
- Add security/: solo dev financial API security, TPM UserWithAuth vs PCR
- Add research/: ralph loop deep research, kick cafe detail, industrial revolution
- Add algorithm/, research/, security/, mac-os/ categories with notes
- Add develop/ notes: git workflows, database cardinality, greenfield concept
- Add gen_ai/ notes: Claude Code internals, multi-agent, evaluator-optimizer, project analysis
- Docs: Add CLAUDE.md and README.md for vault documentation
