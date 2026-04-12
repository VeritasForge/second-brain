# Den Wiki Log

> 추가 전용 (append-only). LLM이 자동 관리합니다.

## [2026-04-13] restructure | LLM Wiki 레이어 제거, old_wiki → wiki rename
- wiki/ (concepts, entities, sources, synthesis, moc, WIKI-SCHEMA.md) 삭제
- old_wiki/ → wiki/ rename (git mv)
- scripts/batch-ingest.sh, wiki-lint.sh 삭제
- .claude/skills/ingest.md, wiki-lint.md 삭제
- save_obsi.md: wiki/ 직접 저장으로 변경
- CLAUDE.md, index.md 재구성

## [2026-04-09] ingest | SSO Concept Explainer
- source: [[raw/sources/2026-04-09-sso-concept-explainer]]
- created: [[sso-concept-explainer-src]], [[sso]], [[oidc]], [[saml]], [[keycloak]], [[auth0]], [[okta]], [[security-auth]]

## [2026-04-09] ingest | Karpathy LLM Wiki Gist
- source: [[raw/articles/karpathy-llm-wiki]]
- created: [[karpathy-llm-wiki]], [[llm-wiki-pattern]], [[rag]], [[obsidian]], [[rag-vs-llm-wiki]], [[knowledge-management]]

## [2026-04-09] create | LLM Wiki 구조 초기화
- created: index.md, log.md
- updated: CLAUDE.md (위키 운영 스키마 추가)
