# Den Wiki Log

> 추가 전용 (append-only). LLM이 자동 관리합니다.

## [2026-04-21] create | 파일 검색 도구 가이드 + develop/cli 카테고리 신설
- created: [[file-search-find-rg-grep]] — 파일 검색 도구 가이드 (find, grep, rg)
- moved: [[glob-pattern-matching-deep-dive]] — develop/ → develop/cli/로 이동

## [2026-04-21] create | JS/TS 학습자료 시리즈 (8개 문서)
- created: [[00-js-ts-study-guide]] — JS/TS 학습 가이드 (시리즈 허브)
- created: [[01-js-ts-philosophy-and-differentiation]] — JS/TS 철학과 차별점
- created: [[02-js-ts-architecture-and-runtime]] — JS/TS 아키텍처와 런타임
- created: [[03-js-ts-basic-syntax]] — JS/TS 기본 문법
- created: [[04-js-ts-advanced-syntax-and-patterns]] — JS/TS 고급 문법과 패턴
- created: [[05-js-ts-developer-essentials-by-seniority]] — JS/TS 개발자 필수 지식 (레벨별)
- created: [[06-js-ts-testing-patterns]] — JS/TS 테스팅 패턴
- created: [[07-js-ts-project-structure-and-tooling]] — JS/TS 프로젝트 구조와 도구

## [2026-04-21] create | Kotlin+Spring 학습자료 시리즈 (8개 문서)
- created: [[00-kotlin-study-guide]] — Kotlin+Spring 학습 가이드 (시리즈 허브)
- created: [[01-kotlin-philosophy-and-differentiation]] — Kotlin 철학과 차별점
- created: [[02-kotlin-architecture-and-runtime]] — Kotlin 아키텍처와 런타임
- created: [[03-kotlin-basic-syntax]] — Kotlin 기본 문법
- created: [[04-kotlin-advanced-syntax-and-patterns]] — Kotlin 고급 문법과 패턴
- created: [[05-kotlin-developer-essentials-by-seniority]] — Kotlin 개발자 필수 지식 (레벨별)
- created: [[06-kotlin-testing-patterns]] — Kotlin 테스팅 패턴
- created: [[07-kotlin-project-structure-and-tooling]] — Kotlin 프로젝트 구조와 도구

## [2026-04-21] create | Python 학습자료 시리즈 (8개 문서)
- created: [[00-python-study-guide]] — Python 학습 가이드 (시리즈 허브)
- created: [[01-python-philosophy-and-differentiation]] — Python 철학과 차별점
- created: [[02-python-architecture-and-runtime]] — Python 아키텍처와 런타임
- created: [[03-python-basic-syntax]] — Python 기본 문법
- created: [[04-python-advanced-syntax-and-patterns]] — Python 고급 문법과 패턴
- created: [[05-python-developer-essentials-by-seniority]] — Python 개발자 필수 지식 (레벨별)
- created: [[06-python-testing-patterns]] — Python 테스팅 패턴
- created: [[07-python-project-structure-and-tooling]] — Python 프로젝트 구조와 도구

## [2026-04-21] create | POSIX 파일 끝 Newline 원칙
- created: [[posix-newline-at-end-of-file]]

## [2026-04-21] create | Go 학습자료 시리즈 (8개 문서)
- created: [[00-go-study-guide]] — Go 학습 가이드 (시리즈 허브)
- created: [[01-go-philosophy-and-differentiation]] — Go 철학과 차별점
- created: [[02-go-architecture-and-runtime]] — Go 아키텍처와 런타임
- created: [[03-go-basic-syntax]] — Go 기본 문법
- created: [[04-go-advanced-syntax-and-patterns]] — Go 고급 문법과 패턴
- created: [[05-go-developer-essentials-by-seniority]] — Go 개발자 필수 지식 (레벨별)
- created: [[06-go-testing-patterns]] — Go 테스팅 패턴
- created: [[07-go-project-structure-and-tooling]] — Go 프로젝트 구조와 도구

## [2026-04-20] create | HTTP Status Code 429 & 303 완전 가이드
- created: [[http-status-code-429-303]]

## [2026-04-20] create | AutoML Deep Research 2025
- created: [[automl-deep-research-2025]]

## [2026-04-15] create | 서버 개발 핵심 기술 6편 (Kotlin, 동시성, IO, Spring 튜닝, GC, 검증)
- created: [[kotlin-vs-go]]
- created: [[coroutine-gmp-vthread]]
- created: [[async-io-epoll-pgbouncer]]
- created: [[spring-tuning-hikaricp]]
- created: [[gc-g1-zgc]]
- created: [[verification-corrections-summary]]

## [2026-04-14] create | 선착순 쿠폰 발급 시스템 설계
- created: [[flash-sale-coupon-system]]

## [2026-04-14] create | 캐시 전략 완전 가이드
- created: [[cache-strategy-guide]]

## [2026-04-14] create | MSA SAGA 패턴 완전 가이드
- created: [[msa-saga-pattern-guide]]

## [2026-04-14] create | AWS SNS vs SQS DLQ 비교
- created: [[aws-sns-sqs-dlq-comparison]]

## [2026-04-14] create | Throttling, Kill Switch, Blameless RCA 기술 피드백
- created: [[throttling-kill-switch-blameless-rca]]

## [2026-04-14] create | Spring AOP 완전 가이드
- created: [[spring-aop-complete-guide]]

## [2026-04-14] create | Spring 핵심 완전 정복 (IoC, DI, Bean, 테스트, TDD)
- created: [[spring-di-bean-test-deep-dive]]

## [2026-04-14] create | SOLID 원칙 완전 정복
- created: [[solid-principles-complete-guide]]

## [2026-04-14] create | SLI, SLO, SLA 서비스 신뢰성 지표 체계
- created: [[sli-slo-sla-guide]]

## [2026-04-13] create | Neovim 버퍼 개념
- created: [[nvim-buffer-concept]]

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
