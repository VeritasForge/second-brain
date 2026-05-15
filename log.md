# Den Wiki Log

> 추가 전용 (append-only). LLM이 자동 관리합니다.

## [2026-05-15] update | URL Mention 문서 — Favicon 섹션 보강
- updated: [[url-mention-unfurling]] — favicon 관련 내용 6가지 위치에 병합. (1) 2️⃣ 핵심 개념 fallback chain 다음에 💡 보충 박스 추가 (favicon은 메타 우선순위와 별개의 5번째 추출 단계 = `<link rel="icon">` 직접 탐색), (2) 7️⃣ 흔한 실수 테이블 #8행 추가 (favicon 상대 경로 미변환 → urljoin 필수), (3) 8️⃣ 예제 2의 favicon_tag 코드에 인라인 주석 보강 (OGP/Twitter Card에 favicon 없음, "icon"/"shortcut icon"/"apple-touch-icon" 부분일치 감지), (4) 🔮 트렌드 항목 추가 (다크모드 대응 SVG favicon + prefers-color-scheme + PWA theme_color), (5) **🔖 Appendix: Favicon — URL Mention 카드의 사이트 로고** 부록 신설 7개 하위 섹션: A-1 정의(IE5 1999, "이름표 스티커" 비유, 등장 6곳) / A-2 포맷 비교 매트릭스 5종(.ico/.png/.svg/.gif/.jpg, JPG 비권장 이유=투명 배경 불가+압축 노이즈) / A-3 HTML 발행 방법 2가지(/favicon.ico convention vs <link> 명시 + apple-touch-icon + manifest) / A-4 권장 사이즈 매트릭스(16/32/48/180/192/512) / A-5 발행자 측 흔한 함정 4가지(캐시/HTTP-HTTPS/iOS touch icon/상대 경로) / A-6 발행자·추출자·렌더러 3관점 역할 분리 / A-7 더 알아볼 것(다크모드/PWA/SEO/Shodan fingerprint), (6) Sources 2건 추가(RealFaviconGenerator, MDN link rel=icon 사양 → 12→14건). frontmatter tags에 favicon 추가, updated 필드 추가

## [2026-05-15] create | URL Mention (URL Unfurling) Concept Deep Dive + Python 구현
- created: [[url-mention-unfurling]] — concept-explainer 8섹션 리포트. (1) URL Mention = 텍스트 속 URL 자동 감지 → 메타데이터 추출 → 미리보기 카드 렌더링. Facebook OGP 2010 → Slack "Unfurling" 용어 대중화, (2) 3-레이어 구조 (Detector/Fetcher/Parser) + Cache + Renderer, (3) 메타 우선순위 폴백 체인: Open Graph → Twitter Card → HTML `<title>/<meta>` → oEmbed, (4) Slack 32KB / Facebook 512KB / Twitter 1MB / LinkedIn 3MB 다운로드 한도, (5) OGP vs Twitter Card vs oEmbed 비교 매트릭스 (정적 메타 vs 인터랙티브 iframe 임베드), (6) SSRF 5계명: URL 정규화 → IP 해석 검사, 사설 대역 차단(10/8, 172.16/12, 192.168/16, 127/8, 169.254/16, fc00::/7), DNS Rebinding 방어(매 hop 재해석), egress default-deny, Content-Type 검증, (7) AWS 메타데이터 서버(169.254.169.254) 명시 차단 패턴, (8) Python 구현 4종: ① BeautifulSoup 최소판 ② SSRF-safe 동기판(ipaddress + socket.getaddrinfo + stream chunk 누적 한도 + charset-normalizer) ③ async + Redis 캐싱(httpx + 병렬 unfurl + URL detect regex max 5) ④ linkpreview 라이브러리 한 줄, (9) iMessage 클라이언트 사이드 unfurl 프라이버시 트레이드오프 + Reddit Embedly 위임 사례, (10) Anti-pattern 3대(검증 없는 fetch / 동기 메시지 응답 결합 / 캐시 부재). Sources 12 (Slack 공식, ogp.me, oembed.com, OWASP SSRF Cheat Sheet, PortSwigger, linkpreview/metadata_parser PyPI, 9to5Mac 보안 리서치)

## [2026-05-13] create | Claude Code 컨텍스트 자산 4-Scope 모델 (CLAUDE.md/Rules/Skills 로딩 메커니즘)
- created: [[claude-context-assets-4-scope-model]] — 3차 수렴 검증 결과 정리. (1) 4-Scope 모델: Always-on(CLAUDE.md+paths 없는 rule) / Pattern-gated(paths 있는 rule) / On-demand(skills/agents) / Enforcement(hooks/permissions), (2) 사실 오류 5건 정정 (override→concatenate, AGENTS.md 자동 인식 안 됨, 8단계→5계층+동시 로드, Rules ↔ nested 직교 관계, 사람용/AI용 이분법→3분법+공유 카테고리), (3) 통합 자산 매트릭스 14종(README/CLAUDE.md/nested CLAUDE.md/.claude/rules/.claude/skills/.claude/agents/.claude/commands(레거시)/output-styles/hooks/.claudeignore/.worktreeinclude/.mcp.json/AGENTS.md), (4) Skills vs Rules 결정 주체 차이: Skills=LLM 주도(description 보고 자율 호출) vs Rules=런타임 주도(paths 매칭 자동 주입, frontmatter는 LLM 미노출), (5) Rules 컨텍스트 잔존 모델: 매칭 시 message history 누적 → compaction 시 제거 → 다시 매칭 시 재로드 → "시간 지연 로드"이지 "영구 제외" 아님, (6) 진짜 토큰 절약 수단 3가지(.claudeignore, Skills disable-model-invocation, root CLAUDE.md 200줄 이하), (7) Nested CLAUDE.md 생존 7가지 이유(하위 호환성/근접성/계층 누적/거버넌스 분산/도구 호환/Git blame/폴더 진입 UX), (8) 의사결정 가이드 4축(팀 규모/규제 강도/도구 다양성/변경 빈도) + Hook 트리거 신호 + 단일 팀→보안 규제 마이그레이션 4단계. UNVERIFIED 3건(중복 로드/`/clear` 동작/frontmatter LLM 노출 여부). Sources 7건 모두 docs.claude.com 공식

## [2026-05-13] update | Trivy 자동 보안 패치 운영 — 6시간 빈도 디테일 후속 검증 추가
- updated: [[trivy-auto-patch-cron-vs-ci-design]] — §4 환경 사실 5→8개 확장 (E-6 macOS 캐시 경로 `~/Library/Caches/trivy/`, E-7 Trivy 0.69+ 기본 OCI 타깃 `mirror.gcr.io/aquasec/trivy-db:2`, E-8 NextUpdate TTL=24h). §8 보완 #1 옆 후속 참조 💡 추가. §10 회고 "권고를 한 번 더 깨러 가기" 메타 교훈 추가. §11 신규 섹션 "6시간 빈도를 어떻게 운영할 것인가" 추가 (7개 하위 절): 처음 권고한 metadata.json UpdatedAt 폴링 3계층 패턴이 두 번째 rl-verify로 사실 오류 4건 + 설계 결함(NextUpdate TTL 24h라 폴링 무의미, "정각 회피 마진"은 공식 권고 아님, 안전망 cron은 폴링과 race) 드러남 → Random jitter(Google SRE Book Ch.24, thundering herd 방지, `sleep $((RANDOM % 600))`) SRE 표준 도입 → Healthchecks.io는 over-engineering 인정(부재 감지 dead-man switch 본질이지만 우리 케이스엔 Slack webhook으로 충분) → 최종 단순화 코드 1줄로 수렴(6h cron + random jitter + Slack webhook + 환경변수 4개). §11-7 처음 vs 최종 비교표 8개 항목. 출처 추가: Google SRE Book Ch.24, AWS Exponential Backoff and Jitter, Trivy 소스코드 (pkg/db/db.go, pkg/metadata/metadata.go, cron.yml), Healthchecks.io, trivy-action 2026-03 공급망 사고

## [2026-05-13] create | Trivy 자동 보안 패치 운영 모델 — Cron 배치 vs CI 트리거
- created: [[trivy-auto-patch-cron-vs-ci-design]] — 모노레포(Go/Python/Kotlin) 의존성 취약점 자동 패치 워크플로우를 5개 검증 관점(CONTRARIAN/SecOps/DevOps/Researcher/Simplifier)으로 교차 검증. 옵션 A(Cron 배치 매시간 → trunk 별도 보안 PR) vs 옵션 B(CI 시점 PR 브랜치 자동 패치) 비교. 발견사항 9개(D-1~D-9): D-1 Dependabot/Renovate 산업 표준은 default branch 전용 → 옵션 A 정렬 / D-2 옵션 B는 branch protection enforce_admins+race+2024 Confused Deputy/Merge Conflict Tango/Branch Merge Shuffle 공격 벡터 / D-3 매시간은 Trivy DB 6h 빌드 주기 대비 75% over-polling / D-4 release/* 미커버 구조적 갭 / D-5 0-day는 GHSA T+2h+Trivy DB T+9h+cron T+1h = 최악 24h+ → CISA KEV feed fast-path 필요 / D-6 CI Trivy non-blocking + workflow_run 이미지 스캔 → PR 게이트 전제 부정확. 위협 모델 매트릭스 T1~T5(옵션 A 10/15 vs B 7/15), 운용 리스크 10항목 비교(33/40 vs 20/40 vs 31/40). 최종 권고: 옵션 A 유지 + 4계층 보완(빈도 6h, KEV fast-path, release/* 커버리지, GH Actions cron 이중화). CVSS SLA 표(CISA BOD 22-01 14일, NIST SP 800-40r4 15일, UK SS-033 7일, PCI 30일, OWASP SAMM 24~72h). 메타 교훈: CONTRARIAN 의무화, 환경 사실 선확인, 산업 표준 닻

## [2026-05-13] create | 동시통역 (Simultaneous Interpretation) 서비스 Deep Research
- created: [[simultaneous-interpretation-service]] — deep-research 3-phase 결과. (1) 표준 Cascaded 파이프라인 (ASR→NMT→TTS) 아키텍처 + Silero VAD 16kHz/32ms chunk 사양, (2) TTS가 RTF의 62% 차지 → streaming TTS 적용 시 4200ms→475ms 단축 (Deepgram 검증), (3) 총 latency 목표 500ms(대화)/2-3s(강의), (4) Meta SeamlessM4T v2 + EMMA (Efficient Monotonic Multihead Attention) E2E 아키텍처 + UnitY2 framework (arXiv 2312.05187), (5) Cascaded vs E2E BLEU 비교 (many-to-many 21.6 vs 15.8, into-English 22.0 vs 26.6), (6) 한국어 SOV↔SVO 어순 이슈 + CWMT(Chunk-wise Monotonic Translation) 해결 전략 (arXiv 2404.12299), (7) Samsung Galaxy AI Live Translate 18+ 언어 (Korean 포함, dialer+WhatsApp/KakaoTalk) vs iOS 26 Live Translation (한국어 미지원, ES/PT/DE/FR만), (8) 컴포넌트 벤더 매트릭스 (Deepgram Nova-3 200-300ms / Cartesia Sonic 3 <200ms / ElevenLabs Turbo v3 300-400ms), (9) 한국어 production stack 권고 [Synthesized]: Deepgram/Whisper KR + LLM MT(register prompt) + Cartesia/ElevenLabs streaming TTS. Sources 11 (arXiv 4, 공식 3, 기술 블로그 4). 확신도 분포: ✅Confirmed 13 / 🟡Likely 9 / 🔄Synthesized 3 / ❓Uncertain 1

## [2026-05-08] create | Python + EventBridge + Lambda + AWS Batch 스택 조사
- created: [[aws-eventbridge-lambda-batch-stack]] — deep-research 3-phase 결과. EventBridge Scheduler vs Rules 매트릭스 (IANA TZ/one-time/DLQ/계정당 수백만 한도), Lambda → Batch 트리거 3경로 (boto3.submit_job / Step Functions submitJob.sync / EventBridge → Batch 직접), IaC 5종 비교 (CDK/SAM/Serverless/Terraform/CFN), Fargate(500 launches/min) vs EC2 Spot 권장 매트릭스, Lambda Python 3.13/3.14 런타임 (Deprecation 2029-06-30), Powertools v3.21+ Pydantic 통합, X-Ray maintenance(2026-02-25) → ADOT 권장, EventBridge DLQ 자가치유 패턴, GitHub Actions OIDC, 의사결정 트리(STACK A 미니멀/B 표준/C 워크플로우). Sources 13 (AWS 공식 9, primary 1, blog 3)

## [2026-05-08] create | Git Ref 버전/자연 정렬 가이드
- created: [[git-ref-version-sort-guide]] — 5섹션 정리. (1) 자연 정렬 vs 사전식 정렬 비교 + GNU sort -V/ls -v/git --sort=v:refname/Python natsort/JS localeCompare 도구 매트릭스, (2) `--sort=v:refname` 문법 분해 (v: 접두어 = version 정렬, refname = 정렬 대상) + git sort 키 표 (refname/v:refname/creatordate/committerdate/taggerdate), (3) refname의 컨텍스트별 의미 (refs/tags vs refs/heads vs refs/remotes), (4) er-* 태그 오름/내림차순/최신 추출 실전 예시, (5) macOS BSD sort 한계, SemVer prerelease 정렬 한계, refname:short 별칭, 전체 경로 정렬 주의

## [2026-05-06] create | Bloom Filter Concept Deep Dive
- created: [[bloom-filter]] — concept-explainer 8섹션 리포트. Burton Bloom 1970, m·k·n·p 수식 (k* = (m/n)·ln2, m = -n·ln(p)/(ln2)², 1% FPR ≈ 9.6 bit/원소), Insert/Query ASCII 흐름, Cassandra/RocksDB/Redis/Bitcoin SPV 유즈케이스, Cuckoo/HyperLogLog/Count-Min Sketch 비교 매트릭스, Cloudflare 메모리 무작위 접근 함정, Learned Bloom Filter 트렌드. Sources 12 (Wikipedia, Cloudflare, Redis, AWS, InfoQ, Berkeley CS170 등)

## [2026-05-01] create | Kotlin Coroutine vs Java Thread/Virtual Thread Deep Dive
- created: [[kotlin-coroutine-vs-java-thread-vthread]] — concept-explainer 8섹션 + 면접 Q&A 10선. JEP 444/491/505 반영 (JDK 24 synchronized pinning 해소, JDK 25 Structured Concurrency 5th Preview), CPS 변환·상태머신, mount/unmount, Dispatchers.IO work-stealing, 메모리/컨텍스트 스위치 비용 3-way 매트릭스, 선택 결정 트리, 안티패턴 8개, JFR 모니터링 가이드. Sources 15+ (공식 JEP 3, Oracle/JetBrains 공식, Inside Java, Rock the JVM, Medium 벤치마크)

## [2026-04-28] create | HTTP 프로토콜 시리즈 (1.1/2/3·QUIC)
- created: [[http1-1-concept-explainer]] — HTTP/1.1 8관점 분석 (persistent connection, pipelining, chunked, caching, RFC 9110~9112)
- created: [[http2-concept-explainer]] — HTTP/2 8관점 분석 (binary frame, multiplexing, HPACK, server push deprecated, Rapid Reset CVE-2023-44487)
- created: [[http1-1-problems-and-http2-evolution]] — HTTP/1.1 6대 문제 → HTTP/2 해결 매핑, 도메인 샤딩 안티패턴, 103 Early Hints
- created: [[why-http1-1-still-dominates]] — HTTP/1.1 잔존 8가지 이유 (CDN edge↔origin, L4 LB, 기업망, 디버깅, REST 생태계)
- created: [[http2-perspective-grpc-and-ecosystem]] — HTTP/2 관점 gRPC 매핑표 (Stream/HEADERS/Trailers/Flow control), APNs, Web Push, K8s API, Envoy xDS
- created: [[http3-quic-concept-explainer]] — HTTP/3 + QUIC 8관점 분석 (UDP+TLS1.3, 0-RTT, connection migration, QPACK, Multipath/MASQUE)
- created: [[http-protocol-interview-qa]] — 면접 Q&A 33문항 (기본/함정/성능/시스템디자인/HTTP3 카테고리)

## [2026-04-24] create | Computer-Use MCP Server Deep Dive
- created: [[computer-use-mcp-server]] — Claude Code 빌트인 MCP 서버로 macOS GUI 앱 직접 조작 (스크린샷, 클릭, 타이핑), 동작 원리, 보안 모델, 4가지 도구 비교

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
