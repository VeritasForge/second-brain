# Den Wiki Log

> 추가 전용 (append-only). LLM이 자동 관리합니다.

## [2026-04-23] create | SSH vs SSM Session Manager Deep Dive
- created: [[ssh-vs-ssm-session-manager]] — SSH vs SSM 프로토콜 차이, TOFU/PKI 신뢰 모델, MITM 공격, 공격 표면, SSM 통신 구조(폴링/WebSocket), 셸 릴레이 메커니즘, SSM Agent 기본 정보

## [2026-04-23] update | AWS IAM Role — Q&A 검증 반영 (Instance Profile, IMDS, SessionToken 등)
- updated: [[04-aws-iam-role-concept-explainer]] — Q&A 9건 병합: Role 생성 방법, Instance Profile/External ID 상세, AKIA/ASIA 공식 미공개 명시, SessionToken opaque 토큰 정정, IMDS 동작 정정 (EC2 서비스가 STS 호출), Execution Role/Task Role 공식 용어 명시, 같은 계정 Default Deny 설명, Role 선택 가이드 해설. Sources 10→16건

## [2026-04-23] update | AWS IAM Role — STS 상세, CLI 인증 방식, FAQ 보충
- updated: [[04-aws-iam-role-concept-explainer]] — STS API 상세, Action vs ARN 접두사 차이, Lambda+SQS 시나리오, 로컬 CLI에서 Role 사용법 (SSO/Profile Chaining), Organizations 불필요 오해 교정

## [2026-04-23] restructure | AWS IAM 시리즈 번호 체계 + 허브 페이지
- created: [[00-aws-iam-study-guide]] — AWS IAM 학습 가이드 (시리즈 허브 페이지)
- restructured: 01~06 번호 접두어 추가, 읽기 순서 및 레벨별 추천 경로 안내

## [2026-04-22] create | AWS IAM 개념 시리즈 (6개 문��)
- created: [[aws-iam-user-concept-explainer]] — AWS IAM User 8관점 분석
- created: [[aws-iam-group-concept-explainer]] — AWS IAM Group 8관점 분석
- created: [[aws-iam-policy-concept-explainer]] — AWS IAM Policy 8관점 분석
- created: [[aws-iam-role-concept-explainer]] — AWS IAM Role 8관점 분석
- created: [[aws-iam-concept-explainer]] — AWS IAM 전체 개념 8관점 분석
- created: [[aws-iam-architecture-and-integration]] — AWS IAM 4요소 유기적 결합 Deep Research

## [2026-04-22] create | Connection Pool Eviction 전략 Deep Research
- created: [[connection-pool-eviction-lazy-idle]] — Lazy vs Idle/Proactive Eviction, 타이머 리셋 동작, 라이브러리별 비교

## [2026-04-22] create | HTTP Connection Pool, Keep-Alive, Long Polling (2개 문서)
- created: [[python-requests-connection-pool-keepalive]] — Python requests Connection Pool, Keep-Alive, Stale Connection, Timeout 설계
- created: [[long-polling-http-realtime-communication]] — Long Polling: HTTP 실시간 통신의 이해 (Short Polling, SSE, WebSocket 비교)

## [2026-04-21] create | gRPC Concept Deep Dive (Go 중심, rl-verify 검증 완료)
- created: [[grpc-concept-deep-dive]] — gRPC 8관점 분석 + Go 코드 예시 + 수렴 검증 반영

## [2026-04-21] create | Git Tag/Plumbing/Reflog + Shell Heredoc (4개 문서 일괄)
- created: [[git-tag-annotated-lightweight]] — Git Tag 완전 가이드 (Annotated vs Lightweight, GPG, push, 삭제)
- created: [[git-cat-file-for-each-ref]] — Git 내부 명령어 가이드 (cat-file, for-each-ref)
- created: [[git-reflog-recovery-guide]] — Git Reflog 개념과 실수 복구 활용법
- created: [[shell-command-substitution-heredoc]] — Shell Command Substitution + Here Document 패턴 가이드

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
