# Den Wiki Log

> 추가 전용 (append-only). LLM이 자동 관리합니다.

## [2026-06-01] create | PostgreSQL RLS (Row-Level Security) Concept Deep Dive
- created: [[postgresql-row-level-security]] — concept-explainer 8섹션 리포트. PostgreSQL 9.5(2016) 도입 RLS를 deep-research(7쿼리/14출처)로 정리. (1) **정의**: 모든 쿼리에 자동으로 "보이지 않는 `WHERE` 절"을 주입해 행 단위 접근을 DB 엔진 차원에서 강제 — 정책은 **테이블에 묶임(쿼리 아님)**, default-deny. (2) **핵심 구성**: `ENABLE ROW LEVEL SECURITY`(스위치) + `CREATE POLICY`의 `USING`(읽기 필터) vs `WITH CHECK`(쓰기 검증) + `TO role` — `WITH CHECK` 생략 시 `USING` 자동 복사, 둘이 다르면 "못 보는데 INSERT 되는" 구멍. (3) **동작**: 쿼리 플래너가 사용자 WHERE보다 **먼저** 정책 주입. 기본/멀티테넌트 SQL 예시 2종. (4) **멀티테넌트 베스트 프랙티스**: 테넌트별 DB 유저 ❌ → **런타임 변수 + 트랜잭션 내 `SET LOCAL`**(`SET` 금지 — 커넥션 풀에서 다음 사용자가 컨텍스트 상속 → 테넌트 누수), 모든 테넌트 테이블에 RLS, 정책 컬럼 인덱싱, 통합 테스트. (5) **장단점**: ✅ DB 강제·코드 단순화·단일 진실·Defense in Depth / ❌ 성능 오버헤드·디버깅 난이도·정책 code drift(pg_policies에 살아 Git 추적 누락)·ABAC 등 복잡 권한 한계. (6) **vs App-Level 인가**: RLS는 접근 경로 무관 강제(누수 위험 ↓)·복잡 로직 약함·디버깅 어려움 vs 앱 인가는 유연·누수 위험 ↑ → **정답은 "둘 다"**(Supabase 권고, RLS=최후 방어선). (7) **🚨 함정**: ① 테이블 소유자 접속 시 RLS **우회**(→ `FORCE ROW LEVEL SECURITY` 필수, 실무 1순위 사고) ② `SET` vs `SET LOCAL` ③ `BYPASSRLS`/superuser 절대 금지 ④ `WITH CHECK` 오설계 ⑤ VIEW는 기본 SECURITY DEFINER로 우회(PG15 `security_invoker=true`). Anti-pattern: 행마다 함수 호출(N행=N콜)·non-LEAKPROOF 함수(인덱스 차단·풀스캔)·rate limit 부재(쿼리 자체는 계속 실행 → CPU 낭비). **성능 최적화 SELECT wrapper**: STABLE SECURITY DEFINER 함수를 `IN (SELECT fn())`로 감싸 쿼리당 1회 평가(~450ms→~45ms, 10x). (8) 도구: Supabase/PostGREST/Bytebase. 출처: PostgreSQL 공식 docs, Supabase, AWS, Crunchy Data, Bytebase, PlanetScale(비판적 관점), SupaExplorer, The Nile. develop/database. 관련: [[advisory-lock-vs-for-update-vs-redlock]].

## [2026-06-01] create | 동시성 제어: Advisory Lock · FOR UPDATE · Redlock
- created: [[advisory-lock-vs-for-update-vs-redlock]] — PostgreSQL advisory lock(권고 잠금: "내가 정한 키"에 거는 자율 잠금으로 COUNT-then-INSERT race 직렬화, 다중 키는 정렬 획득으로 deadlock 방지)을 `SELECT FOR UPDATE`(존재하는 행만 잠금) 및 Redis Redlock(분산 락, TTL 기반·Kleppmann 안전성 논쟁/fencing token 필요)과 비교. 핵심 구분: ① FOR UPDATE와는 **"아직 없는 것을 잠글 수 있는가"**(advisory는 미존재 엔티티·INSERT race 직렬화 가능) ② Redlock과는 **"락-데이터 거리"**(advisory는 DB·트랜잭션과 밀착, Redlock은 별도 Redis로 분리되어 불일치 위험). 동시성 정확성의 최후 보장은 락이 아니라 **DB unique constraint**(강제적 차단). 출처: PostgreSQL 공식 docs, Kleppmann "How to do distributed locking". develop/database.

## [2026-06-01] update | Set-Cookie 노트 위치 이동 + rl-verify 검증 반영
- restructured: [[http-cookie-security-concept-explainer]] — 위치 `develop/network/` → **`develop/fe/`** 이동(index.md 섹션 갱신).
- updated: [[http-cookie-security-concept-explainer]] — rl-verify Tier 3 수렴 검증(2 iteration, 5관점: ce-web-researcher/ce-security-sentinel/ce-best-practices-researcher/ce-adversarial-document-reviewer/convergence-evaluator) 결과 **14건 정정 반영**. High: (F2) Google third-party 발표 2024.7 폐지철회/2025.4 prompt철회·현행유지 시간순 정정 — "user choice 전환" 과대해석 교정, (F4) 토큰 "XSS·CSRF 양쪽 방어"→"완화(제거 아님)"+메모리 access token도 XSS 런타임 탈취 명시, (F8) BFF/Token-Handler가 IETF/OWASP 1순위·하이브리드는 차선으로 균형, (F14) Domain 미지정=host-only가 가장 안전(명시 시 서브도메인 확대 역효과), (F18) first-party "무영향" 안일 보강(정책 휘발성·Safari ITP first-party 만료 단축·GDPR 동의의무). Med: (F1) Firefox 미지정 시 None 기본값(Bugzilla #1617609), (F6) refresh token rotation/재사용 탐지, (F7) __Host- "쿠키 덮어쓰기 방어"로 한정+host-only라 SSO 공유 불가, (F9) CHIPS Baseline 2025(Chrome114+/FF141+/Safari18.4+)+Partitioned Secure 필수, (F11) Lax는 cross-site POST 복귀(PG/OAuth form_post)에 미전송, (F13) localhost Secure 예외는 브라우저 구현 한정, (F15) 레거시 브라우저 None→Strict 오인, (F16) localStorage CSRF없음에 "XSS 무방비→종합위험 큼" 각주. Low: (F3) HttpOnly IE6→IE6 SP1. 기각: (F10) SameSite 표 "자기모순" 주장은 REFUTED(표 정확). Sources 8→13건(Bugzilla/OWASP Session Cheat Sheet/IETF draft-oauth-browser-based-apps/MDN Partitioned/OneTrust 추가). 검증 리포트: docs/demiurge/rl-verify/http-cookie-security/report.md.

## [2026-05-31] create | Set-Cookie & 쿠키 보안 속성 Concept Deep Dive
- created: [[http-cookie-security-concept-explainer]] — `Set-Cookie` 응답 헤더와 쿠키 보안 속성(HttpOnly/Secure/SameSite/Domain/Path/Max-Age·Expires)을 concept-explainer 8섹션으로 정리. 핵심: (1) **HttpOnly**=JS `document.cookie` 차단으로 XSS 토큰 탈취 방어(단 JS-initiated fetch엔 여전히 첨부) (2) **Secure**=HTTPS 전용(localhost 예외) (3) **SameSite** Strict/Lax/None 3값 비교 + 브라우저 기본값(Chrome/Edge/Opera는 미지정 시 Lax, Chrome 80~2020.2 / **Firefox·Safari는 미적용** → 항상 명시 권장) (4) **공격↔방어 매핑**: XSS↔HttpOnly, CSRF↔SameSite+CSRF토큰(SameSite는 토큰 대체 ❌, defense in depth) (5) **localStorage vs HttpOnly Cookie** 토큰 저장 트레이드오프 + 2025 하이브리드 합의(access=메모리, refresh=HttpOnly Secure 쿠키) (6) `__Host-`/`__Secure-` 접두사, CHIPS(`Partitioned`), Max-Age>Expires 우선순위 (7) **third-party cookie**: Google 2024.7 폐지 철회 → 2025.4 user choice 모델(first-party 세션 쿠키 무영향). 기존 [[oauth2-concept-explainer]]·[[sso-oauth-comparison-and-architecture]]·HTTP 시리즈와 cross-link. 출처 8건(MDN, web.dev, OWASP, PortSwigger, Microsoft Learn, Privacy Sandbox 등).

## [2026-05-30] create | API Rate Limiting 실무 가이드 (slowapi vs nginx)
- created: [[api-rate-limiting-practical-guide]] — FastAPI/Starlette 기반 백엔드의 rate limiting을 앱 레이어(slowapi)와 인프라 레이어(nginx)로 나눠 정리한 실무 가이드. 3회 iteration 수렴 검증(rl-verify Tier 3) 결과 반영: (1) **C14 P0 안티패턴** `key_func=lambda r: get_user_plan(r)` 정정 — 모든 동일 plan 유저가 단일 버킷 공유 + DoS amplification 보안 결함, `key_func`=식별자/`limit string`=정책 분리 원칙 명시 (2) **멀티워커 N배 정확도** — "정확히 N배" → balls-into-bins로 ~3.4-3.6× (N=4), keep-alive sticky 시 1× 수렴 (3) **nginx JWT 옵션 축소 정정** — Lua/OpenResty 필수 ❌ → njs(공식) + auth_request + nginx-plus + OpenResty 4가지 (4) **"Defense in Depth 정석" 단정 제거** — OWASP API4도 레이어 처방 안 함 (5) **"10만 RPS 신화" 정정** — 진짜 L7 DDoS면 nginx도 무력, CDN/Shield 영역 (6) **Retry-After 의미론 정정** — slowapi는 모든 응답에 주입(RFC와 다름) (7) **응답 헤더 app config 커스터마이즈** (RATELIMIT_HEADER_*). 5가지 핵심 시나리오(외부 API 비용/DB 자원/봇/ATO/SaaS 차등), 8가지 안티패턴, 6단계 의사결정 가이드, 11개 1차 출처 포함. 검증 출처: docs/demiurge/rl-verify/slowapi-vs-nginx-ratelimit/report.md (CONFIRMED 8 / PARTIAL 3 / REFUTED 4 / CONTESTED 0).

## [2026-05-28] create | Rate-Limit 설계 & 클라이언트 IP 추출 종합
- created: [[rate-limit-and-client-ip]] — 회원가입 OTP 선검증에 적용할 rate-limit 정책(재전송 쿨다운 60초·이메일당 일 한도 10~20통·IP /64 한도·Resend 응답 fallback·timing equalization) + 클라이언트 IP 추출(TCP 소켓 vs HTTP 헤더, XFF 위조 가능성·CWE-348, "오른쪽에서 신뢰 hop N번째" 규칙, 호스팅 검증 헤더 — **Vercel `x-real-ip` 우선** (`@vercel/functions` SDK 일치), **Cloudflare `TRUST_CLOUDFLARE` 환경변수 게이트**, IPv6 /64 prefix·IPv4-mapped 정규화, Next.js 16 base-server.js XFF socket fallback 함정) 종합 정리. brainstorming 토론과 rl-verify 다관점 검증(ce-web-researcher/adversarial-document-reviewer/security-sentinel/feasibility-reviewer)으로 정정된 결론 반영 — 초안의 "이메일당 한도 제거 가능"은 NIST §5.2.2와 충돌해 REFUTED → 일 한도 복원, "Vercel `x-vercel-forwarded-for` 우선"은 공식 SDK 코드 확인으로 `x-real-ip`로 정정. 보강 헬퍼 함수 `lib/get-client-ip.ts` 패턴 포함 (`ipaddr.js@1.9.1` 이미 transitive 설치 — 추가 의존성 0). Sources 13건(RFC 7239/4291/4862, MDN, NIST 800-63B, OWASP Auth/API Top10, CWE-348, Cloudflare WAF/CF-Connecting-IP, Vercel docs, in-tree Next.js base-server.js:511 + @vercel/functions headers.js:36).

## [2026-05-28] create | aria-activedescendant vs Roving Focus 키보드 네비게이션 패턴
- created: [[aria-activedescendant-vs-roving-focus]] — WAI-ARIA 공식 속성 aria-activedescendant(DOM focus 고정 + 시각 하이라이트) vs Roving Focus/Roving Tabindex(실제 DOM focus 이동) 두 패턴 비교. activeIndex 용어 설명(React 관용 변수명), tabindex 동적 관리 원리, 구현 코드 스케치

## [2026-05-27] create+update | AI Native Engineer 발표용 조사·보강 (brainstorming→plan→4조사관 실행)
- created: [[ai-native-engineer-talk-outline]] — 개발자 청중 20-30분 교육 발표 골격. 8슬롯(훅→정의→실제업무★→자격요건→도구→냉정한현실→자가진단→Q&A), 콘텐츠 22분+Q&A 5-8분 재배분. 각 슬롯 [메시지/근거(노트 링크)/출처/화면/전달팁]. 자가진단 10항목. 벤더/비-벤더 출처 규칙 + Q&A 핵심 반론 5개(재브랜딩/일자리/도구/신입진입/19% 역설).
- updated: [[ai-native-engineer-role]] — 4-조사관 병렬 deep-research 결과 통합 보강. (1) §1 정의에 **인접 용어 4형제 지도**(Vibe Coder/AI Native/Agentic/AI Engineer, 책임구조 축, Karpathy 출처) (2) §4 업무에 **실제 워크플로 루프**(spec→agent→verify, Harper Reed/Addy Osmani/Sakasegawa — 비-벤더 독립 실무자 수렴 강조, "70/30" 같은 미측정 수치 배제) (3) §5에 **해외 실제 JD 3건**(Libra/Ramp/Legion $140-220K) 추가 → 국내외 1차 공고 6건, 공통요건은 "표본6·경향" 명시(비율% 금지) (4) **§7 도구 생태계 지도 신규**(Claude Code/Cursor/Copilot/Codex/Augment/Windsurf + MCP/하네스5계층, 벤더 벤치마크 라벨 필수) (5) §⚖️ 비-벤더 검증 대폭 보강: METR 후속(머지가능 PR 0%, 고품질OSS 한정)·2026-02 재참여자+18%(선택편향)·Stanford -20%(전체) vs -16%(AI노출직무) 분리+금리/팬데믹 교란·MIT 95% zero-value(기업ROI≠개인코딩)·Gartner Hype Cycle 재브랜딩 비판(단 [미결]) (6) 자가진단 부록 10항목. **검증**: T2 ce-adversarial-document-reviewer(P0 3건: 미근거 수치·선택편향·벤더라벨 + P1 5건 전량 반영) → T6 ce-doc-review(coherence+feasibility, P0 2건 "숙련"표본불일치·시간예산초과 + P1 4건 반영). 출처 21→다수 비-벤더 추가(METR arXiv·Stanford DEL·BLS·MIT). spec/plan: ~/.claude/plans/2026-05-27-ai-native-engineer-research-{design,plan}.md.

## [2026-05-27] update | AI Native Engineer 노트 비-벤더 검증 + 출처 편향 보정
- updated: [[ai-native-engineer-role]] — 사용자 비판("Augment Code 6가지 빼면 건질 게 없다")을 비-벤더 deep-research로 검증·반영. (1) **편향 진단**: 정의·역량론 핵심 1차 출처(Howdy/Augment Code/Agentic Engineering Jobs)가 모두 AI 코딩 생태계 이해당사자 = "독립 출처"가 아닌 "벤더 합창" → 확신도 과대 태깅 식별 (2) **새 섹션 "⚖️ 비-벤더 독립 검증/회의론"**: METR RCT(독립 평가기관 — 경험 개발자 AI 사용 시 19% 슬로우다운, 본인은 20% 빨라졌다 착각, arXiv 2507.09089, 단 과잉일반화 금지 경고) + Stanford 노동시장(22-25세 개발자 고용 ~20%↓, 인턴십 30%↓, 신입 경력요구 1-2년→2-5년) + 구조신호(LinkedIn AI스킬 JD 8%→42%, BLS 22%→15%) + 용어 hype 회의(Julio Pessan) (3) **Contradictions 갱신**: "모순 없음"→표로 [생산성: 벤더 "압도적 빠름" vs METR 19% 느림 = 조건부] [독립성: "합의" vs 벤더 합창]. **종합 판정**: 라벨·역량론은 벤더 거품, 그러나 노동시장 재편은 비-벤더가 입증하는 실재. 직군 가치는 "속도"가 아니라 "판단"(→[[engineering-taste-concept]]) (4) **확신도 정직화**: 정의·6대 역량·Agent Wrangler [Confirmed]→[Likely](서술적 사실은 유지, 규범적 주장만 하향), 한국시장·직군비교는 비-벤더 1차라 [Confirmed] 유지. 분포 ✅2/🟡6/❓2. Sources 14→21(METR/Stanford/IMF 등 비-벤더 7건 추가). Executive Summary에 균형 blockquote 추가.

## [2026-05-26] create | "Taste" 엔지니어링 심미안/판단력의 정체
- created: [[engineering-taste-concept]] — [[ai-native-engineer-role]]의 "Product & Outcome Taste" 역량에서 출발한 "taste" 개념 deep-research. (1) **정의**: taste = "취향(주관적 선호)"이 아니라 "불확실성 속 트레이드오프를 가려내는 훈련된 판단력(disciplined judgment about tradeoffs)". 코드 짜는 능력(skill) ≠ 무엇이 좋은지 알아보는 능력(taste) — "요리 평론가의 혀" 비유 (2) **계보 3단계**: ① Steve Jobs 1995 "Microsoft has no taste"(겉멋 아닌 독창성·문화 부재 비판, Cringely 인터뷰) ② Paul Graham "Taste for Makers" 2002(통념 반박 "taste is just personal preference... it's not true", 취향은 객관적·학습가능, 좋은 디자인 4원칙: simple/solves the right problem/suggestive/redesign) ③ Karpathy 2025-26 vibe coding→agentic engineering(가치가 syntax·구현→판단·taste·감독으로 "moves up") (3) **작동 정의**: Sean Goedecke "almost every decision in software engineering is a tradeoff", bad taste="고장난 나침반(broken compass)", OfferZen "when speed is cheap, judgement becomes the differentiator" (4) **product vs outcome taste 분해**: product=사용자가 진짜 원하는 것 / outcome=올바른 결과를 냈는지 — Graham "solves the right problem"과 동일 뿌리 (5) **반론(Edge)**: Antonio Agudo "Tests, Not Vibes"(taste도 검증 근거 필요) / Shrivu Shankar "Taste Is Not a Moat"(AI가 평균 taste 학습하면 차별화 안 됨) [Uncertain] (6) **훈련법**: 많이 보기/트레이드오프 언어화/재설계 반복/맥락 이해. 원문 직접 확인 2건(paulgraham.com, seangoedecke.com), 8 출처, ✅Confirmed 4/❓Uncertain 2. develop 카테고리.

## [2026-05-26] update | AI Native Engineer 노트 3️⃣ 6대 역량 상세 보충
- updated: [[ai-native-engineer-role]] — 6대 역량이 이름+한 줄 질문뿐이라 Augment Code 원문(WebFetch 1회 재확인)으로 상세 확장. 각 역량(Product & Outcome Taste / System & Architectural Judgment / Agent Leverage / Communication & Collaboration / Ownership & Leadership / Learning Velocity & Experimental Mindset)에 **의미 + 원문 인용구 + ✅좋은 신호/❌나쁜 신호** 추가. 핵심 인용 6종("가장 영향력 있는 엔지니어는 가장 많은 코드를 작성하는 사람이 아니다"/""작동한다"는 쉽다, "프로덕션에서 계속 작동"은 어렵다"/"Like delegation — 보고서가 빠르고 자신감 있게 틀림"/"가장 빠른 팀은 가장 빠르게 명확성에 도달하는 팀"/"소유권=팀과 결과 사이 모든 장애물 제거"/"실험은 한 단계가 아니다, 지금이 곧 일이다"). **🎤 면접 평가 신호 3가지**(모호한 문제 명확화/아키텍처 위험 사전 인식/AI 작업 지시·검증) + **🧭 4가지 채용 프로필**(Systems/Product/Applied AI/Early Professional — 역량 가중치 차이) 추가. 백엔드 배경→Systems Engineer 프로필 매핑 가이드. 원문 직접 인용 5→18건+.

## [2026-05-26] update | AI Native Engineer 노트에 Augment Code 회사 설명 보충
- updated: [[ai-native-engineer-role]] — 3️⃣ 6대 역량 섹션에 `> 💡 Augment Code란?` blockquote 추가 (Context Engine 시맨틱 검색·"도서관 사서" 비유·타겟 200-500명 조직·2026 신제품 Intent/Context Engine MCP·ISO 42001 최초 인증·"대장장이가 쓴 검술 채용 기준" 출처 신뢰도 + 자사 홍보 편향 주의). Sources 11→14 (공식 사이트/SiliconANGLE/VS Code Marketplace), Metadata 갱신. Quick Research(WebSearch 1회) 기반.

## [2026-05-26] create | AI Native Engineer 직군 완전 해부
- created: [[ai-native-engineer-role]] — AI Native Engineer 직군 deep-research 3-phase 결과. (1) **정의**: "AI 코딩 에이전트(Claude Code/Cursor/Codex)를 핵심 인프라로 오케스트레이션하여 소프트웨어를 빌드하는 직군" — 3개 독립 출처(Howdy/Augment Code/Agentic Engineering Jobs) [Confirmed]. 모델을 만드는 ML Engineer도, 모델 호출해 앱 만드는 AI Engineer도 아닌 "에이전트 부대를 지휘하는 설계자(architect & editor)" (2) **병목 역전**: "코드 생성은 순식간, 인간의 판단이 새 병목" / "from craftsperson to architect — from typing to thinking" (3) **3-direction 비교**: ML Engineer(모델 생성·수학)/AI Engineer(API 호출·RAG)/AI Native Engineer(에이전트 오케스트레이션·CLAUDE.md·검증 인프라) — 7차원 매트릭스 (4) **Augment Code 6대 역량**: Product Taste / System Judgment / Agent Leverage("위임과 같음 — 다만 보고서가 매우 빠르고 자신감 있게 틀림") / Communication / Ownership / Learning Velocity (5) **Agent Wrangler 5대 업무**: Task Decomposition / Context Curation(CLAUDE.md/ADR) / Harness Design(CI gate/타입체크) / Verification Ownership(라인 리뷰가 아닌 의도 일치도) / Intervention(plausible-but-wrong 감지) (6) **한국 시장**: 무신사 2026-01-16 4년 만의 주니어 대규모 공채(6개월 인턴 전환형·이력서 없는 간편 지원·CTO 전준희) / 그루우 상시 1-7년 "Claude Code, Codex, opencode 경험" + **"컨텍스트 엔지니어링과 하네스 엔지니어링의 경계를 이해"**(글로벌 정의와 거의 동일 표현) / GroupBy·Sionic AI 추가 (7) **연봉**: 미국 AI Engineer 중위 $150-165K base, 시니어 토탈 $200-312K, AI Native 프리미엄 일반 대비 +20-30% [Likely·IIT Kharagpur 단일 출처] / 인도 신입 ₹10-18 LPA (8) **Edge Cases**: 마케팅 용어 vs 실질 직군 / 신입 온보딩 "보일러플레이트→에이전트 코드 평가" 전환 / AI 도구 의존 리스크 / 프리미엄 지속성 [Uncertain] / 포트폴리오 평가법 = 프로덕션 배포+컨텍스트 파일+프로세스 변화 (9) **커리어 권장**: 단기 사이드 프로젝트 CLAUDE.md 포트폴리오 / 중기 팀 단위 워크플로우 개선 사례 / 장기 Den vault Claude Code 4-scope·Trivy 노트 활용. 출처 11건 (1차 자료 5 + 기술 블로그 6), 원문 직접 인용 5건, ✅Confirmed 5/🟡Likely 1/❓Uncertain 1.

## [2026-05-25] create | AI 시대 Confluence/JIRA 대체 도구 조사·검증 종합
- created: [[ai-era-confluence-jira-alternatives]] — AI 시대 Confluence/JIRA를 마크다운·git·AI 네이티브로 대체하는 도구 조사 + rl-verify 2회 검증 종합. (1) **전제 검증**: 마크다운 AI 친화는 대체로 맞으나 Cloudflare "토큰 80% 감소"는 단일 표본·raw HTML 기준(과장), 토큰절감≠이해도(상관/인과 혼동), llms.txt 1835% 출처불명(Refuted) (2) **대체재 지형**: 위키(Wiki.js/BookStack/Outline/Docmost)·이슈(Backlog.md/Beads/GitHub Issues)·통합(GitLab/Gitea/Forgejo/Fossil/Plane/Huly) — "빈 공간" 주장 부분 반증(Fossil이 위키+이슈+VCS 통합 전례) (3) **목적 정렬**: 빌드 아님, Atlassian 탈출+회사 도입+OSS 기여+학습 (4) **도구 비교(gh 실측)**: Plane(49.6k★, MCP 128tools, AGPL, SSO유료, GFI 0), Huly(26k★, 14서비스, EPL-2.0, AI베타), Forgejo(통합·GPL·비영리·경량), Backlog.md(MCP 코어내장, MrLesk 98.5% 솔로=버스팩터1) (5) **라이선스 리스크**: GitLab CE/Gitea(MIT)<Forgejo(GPL)<Huly(EPL, network조항 없어 SaaS안전)<Plane/Docmost(AGPL, Google 등 대기업 전면금지) (6) **정정 추천**: 분리전략(Plane+Docmost) 과설계 → **Forgejo(또는 Gitea) 통합 도입 + "Forgejo용 MCP 서버" 기여**가 통합·permissive·기여복리·AI학습을 한 우물로 충족. AI 공백=기여 기회로 전환 (7) **검증이 바로잡은 것**: 빈공간 부분반증/토큰 인과오류/Markplane 169★/GitLab 평가누락(alternative blindness)/AGPL 회사정책 게이트/Backlog.md 학습 비전이·버스팩터1. 액션: 법무 AGPL 확인→Forgejo 파일럿→GFI 첫기여→MCP RFC. Sources: Cloudflare, AGPL/EPL 1차출처, Google AGPL금지정책, gh api 실측

## [2026-05-22] create | Vercel 스킬 3종 + 워크플로우 연계 가이드
- created: [[vercel-skills-and-workflow-integration]] — Vercel 공식 Claude Code 스킬 3개 카탈로그 + Superpowers/Plan Mode 워크플로우 연계 방법. (1) **Part 1 스킬 3종**: ① `vercel-react-best-practices` (69 룰, 8 카테고리: async/bundle/server/client/rerender/rendering/js/advanced — React/Next.js 성능 안티패턴 방지, 웹 프로젝트 최우선) ② `vercel-composition-patterns` (4 카테고리: architecture/state/patterns/react19 — boolean prop 폭증 방지, compound components, React 19 use/no forwardRef) ③ `vercel-react-native-skills` (8 카테고리: list-performance/animation/navigation/ui/state/rendering/monorepo/configuration — Expo/RN 전용, 웹 프로젝트 무관) (2) **Part 2 워크플로우 연계**: 🅰️ Superpowers 3단계 — brainstorming(룰을 옵션으로 제시: "use client 패턴 vs Server Component 권장")/writing-plans⭐(룰을 사양으로 — 플랜 전 invoke + Task별 "적용 룰" 라벨 + Self-Review 시 룰 기준 점검)/executing-plans(ce-code-review에게 "Vercel best-practices 기준 audit" 명시). 🅱️ Plan Mode 5-Phase — CLAUDE.md 5번 "Skill Discovery" 섹션이 핵심 연결점 + Phase별(Explore/Plan agent/Final Plan/ExitPlan) 끼워넣기 (3) **비유**: Vercel 스킬 = "건축 시방서", brainstorming = 컨셉 스케치(시방서 안 봐도 가능), writing-plans = 구조 도면(시방서 절대 필요), executing-plans = 공사, Plan Mode = "약식 도면 + 즉시 시공" (4) **추천 3중 안전망**: ①작업 시작 시 스택별 스킬 invoke ②플랜 Task에 "적용 룰" 라벨 ③완료 후 code-review에 audit 의뢰 (5) **자동화 강화**: CLAUDE.md 매핑 강화 / settings.json PreToolUse hook / Plan 템플릿 강화 (6) **핵심 통찰**: "룰북이 있어도 펴지 않으면 의미 없다" — 스킬은 자동 강제력이 약하므로 플랜 단계에서 명시적 매핑이 핵심. CLAUDE.md "Skill Discovery" 섹션이 그 안전망.

## [2026-05-22] create | React Transition (useTransition / startTransition) 개념 정리
- created: [[react-transition]] — React 18 Transition API 개념 설명. 상태 업데이트 우선순위 2종(긴급/비긴급) 구분, startTransition으로 폴링 업데이트를 non-blocking 처리, useTransition의 isPending 활용법, 편의점 계산대 비유, React 18 async 제약 주의사항

## [2026-05-22] create | Next.js 페이지 성능과 SWR/Server Component 개념 정리
- created: [[nextjs-performance-and-swr-concepts]] — Next.js App Router(React 19) 환경 페이지 전환 속도 저하 원인 분석 + FE 초보용 핵심 개념 5섹션 정리. (1) **핵심 문제 3가지**: ① `"use client"` 남용 — 햄버거 셀프 조립 비유, JS 다운로드→실행→fetch→렌더 waterfall ② "마운트 후 fetch Waterfall" 시간순 시퀀스 (50→300→500→501→1000→1050ms vs Server Component 0→500ms) ③ "SWR 미사용" — 단골 카페 비유, 매 페이지 이동마다 캐시 부재 재요청 (2) **SWR 심화**: 라이브러리(Vercel/swr.vercel.app) + 전략(RFC 5861 stale-while-revalidate) 두 의미, 4단계 사이클(즉시 표시→백그라운드 fetch→캐시 비교→리렌더), 우유 사오기 비유, 자동 기능 5종(dedupe/revalidateOnFocus/revalidateOnReconnect/자동 재시도/mutate) (3) **캐시 위치**: 브라우저 메모리 JS Map, F5/탭닫기로 사라짐, 5계층 캐시 매트릭스(SWR/HTTP/Service Worker/Redis/CDN) — "책상 위 메모 vs 책장 vs 사서가 외운 정보" 비유 (4) **Single-Threaded인데 어떻게 Background Fetch**: JS 엔진(V8) 메인 스레드 1개 + 브라우저(C++) multi-thread(네트워크/타이머/렌더링/Disk I/O), 1인 피자집 비유(셰프=메인스레드, 오븐=네트워크 스레드, "띵!"=callback, 할일목록=Task Queue, 셰프 확인=Event Loop), fetch 0ms 위임→다른 코드 계속→300ms 응답→Task Queue→302ms 콜백 실행, "non-blocking I/O" + async/await도 syntax sugar, 진짜 멀티스레드는 Web Worker/Service Worker/SharedArrayBuffer (5) **Server Component vs SWR 관계**: "절반은 맞고 절반은 아님" — 첫 페이지 로드는 RSC 충분, 그러나 5가지 상황(데이터 변경/같은 데이터 여러 곳/백그라운드 자동 갱신/Optimistic UI/페이지 재방문)에서 SWR 필요, 식당+미니바 비유("첫 상차림"=RSC vs "식사 중 운영"=SWR), 7시나리오 매트릭스, 2 패턴(Server-First 공식 권장 vs Hybrid 현실) (6) **처방 매트릭스**: Streak SQL 단일화(`async-parallel` ~30x)/SWR 도입(`client-swr-dedup`)/Server Component 전환(`server-parallel-fetching`)/Suspense 경계(`async-suspense-boundaries`) (7) **부록**: Vercel react-best-practices 69개 룰 8 카테고리(async/bundle/server/client/rerender/rendering/js/advanced) 개요 + 문서 개념↔룰 매핑 5건 + `client-swr-dedup` Incorrect/Correct 원문 코드. Sources: SWR 공식(swr.vercel.app), RFC 5861, Vercel react-best-practices 스킬 룰 파일

## [2026-05-22] create | Two Pointer Read/Write 패턴 완벽 가이드
- created: [[two-pointer-read-write-pattern]] — read/write 두 포인터 in-place 필터링 패턴 8섹션 정리. (1) 핵심 정의: read(스캔, 항상 전진) + write(유효 원소 자리, 조건 시 전진), `read ≥ write` 불변량으로 덮어써도 안전 (2) 12살 비유: 사진첩 정리 — read=손가락, write=새 앨범 다음 페이지 (3) 일반화 코드 구조 + 3가지 구성요소 (4) `move_zeroes([0,1,0,3,12])` 단계별 ASCII 시각화 (5) **불변량**: `nums[0:write]`=확정 유효, `nums[write:read]`=스킵됨, `nums[read:]`=미탐색 — "불변량 먼저" 사고법 (6) 패턴 식별 신호 5종 (in-place 제거/중복 제거/끝으로 이동/순서 유지 필터링/O(1) 공간) (7) LeetCode 매핑 6선: 26 Remove Dup / 27 Remove Element / 80 Remove Dup II / 283 Move Zeroes / 905 Sort by Parity / 1089 Duplicate Zeros (8) 변형 A swap (원본 보존, 283/905) vs B overwrite (버려도 됨, 26/27/80) (9) 자주 하는 실수 3건: read 조건부 전진, write 덮어쓰고 원본 손실, write +=1 누락/중복 (10) 다른 two-pointer 비교 매트릭스: read/write vs left/right(수렴) vs fast/slow(속도차) vs sliding window(구간) — 암기 팁 4종 (11) 연습 문제 LeetCode 27 빈칸 채우기 (12) 다음 확인: 역방향 read/write (88/1089), 다중 조건 (80), 불변량 작성 훈련. 관련 풀이: `da_python/src/leetcode/move_zeroes_283.py`

## [2026-05-21] create | Dutch National Flag (DNF) Concept Deep Dive
- created: [[dutch-national-flag]] — concept-explainer 8섹션 리포트 + 포인터 초기값 Q&A 통합. (1) Dijkstra 1976, 3-way partitioning, in-place + O(1) 공간 + 1-pass 알고리즘 정의·역사 (2) 핵심 개념: low/mid/high 3-포인터 + 불변 조건(invariant) — `[0,low)`=0확정, `[low,mid)`=1확정, `(high,n-1]`=2확정, `[mid,high]`=미검사 영역 (3) 분기 다이어그램 + Python 구현 + 복잡도 증명 스케치 (미확인 영역 매 스텝 1씩 감소) (4) **3️⃣-A 포인터 초기값 Deep Dive** (사용자 질문 통합): L=0/H=n-1 은 "값이 있는 자리"가 아니라 "영역의 경계선", M=0 은 "배열 크기 1" 때문이 아니라 "검사 안 한 영역의 시작점" — 책장 비유(L칸=다음 빨간책 자리/H칸=다음 파란책 자리/M=지금 보는 책), n=1 케이스 추적, 사고 프레임(초기값은 어떤 invariant를 처음부터 만족시키나로 정한다) (5) 유즈 케이스: LeetCode 75 + 3-way QuickSort(Bentley-McIlroy) + Pivot equal-key 처리 + 카테고리 데이터 in-place 그룹화 (6) 비교 매트릭스 4종: DNF vs Counting Sort vs 2-pointer Partition(Lomuto/Hoare) vs Bentley-McIlroy 3-way — 패스 수/공간/안정성/카테고리 수 차이 (7) 흔한 실수 5건: `mid < high`로 마지막 칸 누락, `2` 분기에서 `mid++` 동시 호출, `0` 분기 `mid++` 누락, `high = n` off-by-one, invariant 없는 즉흥 코딩 (8) 학습 리소스: Sedgewick & Wayne *Algorithms 4e* / Dijkstra *A Discipline of Programming* / Bentley-McIlroy 1993 / David Gries Cornell 2018 강의노트 / LeetCode #905·#922 일반화 연습 (9) 트렌드: pdqsort (Pattern-defeating QS, Rust/C++ 표준) + Branchless variants. Sources 9 (Wikipedia, Princeton algs4, Baeldung, GeeksforGeeks, Dev.to, OpenGenus, arXiv 2106.05123, Medium). 관련 풀이: `da_python/src/leetcode/sort_colors_75.py`

## [2026-05-20] create | AX(AI Transformation) Deep Research 3-노트 시리즈
- created: [[01-ax-concept-vs-dx]] — AX 개념·DX 관계·falsification gate(양론 병기)·배경(시장/정책/산업 도입률). 16 출처(`[Independently-Audited]` 7건 + `[Self-Reported]` 9건). 회색지대 분류 8 케이스 부록표 신설. **사실 정정**: ① "AX"는 **Korean-Japanese coinage** 확인 (영문은 "AI Transformation" 풀네임) ② McKinsey 70~80% 실패율 → **RAND 2024 RRA2680-1** 정정 ③ Acemoglu **단독** (Restrepo 미포함), "Simple Macroeconomics of AI" NBER w32487 (2024-04, TFP 0.53~0.66%). Falsification gate 평가: (i) 학계 회의론 "AX≠DX 구분 불가" 명시 X = 불충족 + (ii) 컨설팅 정의 90%+ DX 중복 = 모호 → **양론 병기 채택**.
- created: [[02-ax-success-cases]] — 4 사례 카테고리 분리: (b) JPMorgan LLM Suite + Maersk AI 물류, (c) Siemens Industrial Copilot, (a) Microsoft Copilot 사내 전환. **JPMorgan deep dive** (6요소 전수): OpenAI+Anthropic 다중 벤더 + Azure/Snowflake/AWS 3-스택 + RAG+권한 필터 + 8주 모델 업데이트 사이클 + Firmwide CDO AI Model Risk Framework + COiN(2016)≠LLM Suite(2024) 분리. **Induced 패턴 5건 추출** (Task 4 framework용): ① 5-레이어 하이브리드 아키텍처 ② 도메인 IP self-build + 모델 외부 ③ Pilot Happy path 편향 ④ 측정 가능성 카테고리 격차 ⑤ 거버넌스 ∝ 규제 강도. 15 출처(`[Independently-Audited]` 4건).
- created: [[03-ax-process-framework]] — **6단계 framework** (① 진단 ② 비전 ③ 우선순위 ④ 파일럿+CoE ⑤ 스케일링+Responsible AI ⑥ 측정·KPI) — induced 사례 ID + imported 출처 URL 부착. 컨설팅 5사 비교표 (McKinsey/BCG/Deloitte/Accenture/Gartner). **백엔드 엔지니어 횡단 부록** (framework 외 별도 H2): DevOps→MLOps→LLMOps→AI Platform Engineer 진화 + 5 레이어 기술 스택 (vLLM/pgvector/RAGAS/Langfuse/NIST RMF) + 30/60/90일 학습 로드맵 + AX 인터뷰 framing. **Anti-Pattern**: RAND 5대 실패 원인 + Acemoglu/Evans/Marcus 외부 비판 3각 + 컨설팅 자인 신호 (McKinsey 6%·BCG 5%·MIT SMR 40%·HAI 사건 56.4%↑). 19 출처(`[Independently-Audited]` 7건).
- **plan validation**: v1→v2→v3 3차 정제. document-review 5 페르소나 14건 → 5건 v2 반영(B/C/D/G/H+I). rl-verify 4 페르소나 20건 → P1 7건 + P2/P3 best judgment v3 반영. plan 파일: `~/.claude/plans/ax-kind-rabbit.md`, 검증 산출물: `~/.claude/rl-verify/ax-plan-verify/`. Memory 저장: [[reference_skill_mapping_deep_research]] + [[reference_ax_term_status]] (회색지대 8케이스 부록표 포함).

## [2026-05-16] update | 홍길동 design doc v2 + v3 갱신 (document-review + rl-verify 합의)
- updated: [[hong-gildong-service-design]] — v2 (6 페르소나 document-review 반영) + v3 (rl-verify Iteration 1 사실 검증). **v2 변경**: §0 Phase 0 + Kill Criteria 신설 / MVP 카테고리 7→4 축소 / GlobaLeaks·K-MHaS·entity_links·Impact Report·3위원회 Phase 2 deferral / 실 운영비 ₩5,900-11,630K/월 보강 / §7.4 SLAPP·SLA·신고 폭주 / §7.5 정치 중립 모순 처리 / §8 보안 11항목 / §9 v1 결정 vs v2+ 유보 매트릭스 / §10 KPI 사이드카. **v3 사실 정정 8건**: ① 대법원 2007다8333 → 2008다53812 (2009.4.16. 전합) 사건 번호 정정 ② 공직선거법 250조 처벌 구조 (1항 5년·3,000만 / 2항 7년·500-3,000만 / 4항 딥페이크 5,000만) 분리 ③ Fly.io 가격 (2GB $20→$11, 1GB $10→$6) 초당 과금 ④ Cloudflare R2 "외부 클라우드 egress $0.09" 삭제 (R2 egress 전방향 무료) ⑤ 공익신고자 보호법 "498개" 표기 제거 (471개 내외) ⑥ ProPublica "$45-50M (2025)" → "$64.3M (2024)" ⑦ 헌재 결정 병합 번호 2018헌바330 병기 ⑧ 위법성 조각 판결 사건번호 2022도13425 명기. **v3 부분 수정**: 정통망법 70조 2항 자격정지 10년 추가 / 44조의2 "즉시 발동" → "판단 어려움 전제 선택적 발동" / 2022다284513 인용 맥락 주의 / 뉴스타파 ~3.7만 명 [Uncertain] / iOS PWA opt-in 10x + delivery 3x 구분 / 한국 데스크톱 40-50% [Likely] / App Store 거부율 25% 명시. **v3 아키텍처 Issues**: Fan-out 1K/10K 근거 부재 → §4.1-2 read fan-out 기본 / Phase 2 big bang → 2a(데이터)/2b(품질)/2c(인프라) 서브페이즈 분해 + 2-4주 stabilization gap. 6 페르소나 document-review + 4 agent rl-verify = 10 관점 검증 완료. 잔여 v4 권고 7건 (observability/legal_log standby/R2 1h→15분/Fly portability 등).
- created: [[docs/demiurge/rl-verify/hong-gildong-design/plan.md]] + [[docs/demiurge/rl-verify/hong-gildong-design/report.md]] — Tier 3 수렴 검증 산출물

## [2026-05-16] create | 홍길동(Hong Gildong) 부조리 폭로 SNS 종합 디자인 v1
- created: [[hong-gildong-service-design]] — 4개 ce-web-researcher 병렬 리서치 합성: (1) 글로벌 ICIJ($6.4M)/ProPublica($45-50M)/OCCRP Aleph/I Paid A Bribe/GlobaLeaks vs 한국 뉴스타파(3.7만 후원)/청와대 국민청원(정권교체 후 트래픽 -99.3%)/디시·네이트판 비교, (2) 한국 법 4대 리스크 (사실적시 명예훼손 형법 307조 1항 2021헌마1113 합헌 + 정통망법 70조 + 임시조치 §44조의2 30일차단 + SLAPP 반-SLAPP법 부재 + 공직선거법 250조), 위법성조각 형법 310조 + 대법원 2007다8333 운영자 책임 3요건 + 2024.1.4. 인터넷운영자 판례, (3) 7카테고리 택소노미 (TI 5분류 × ACFE Fraud Tree × 권익위 교차 도출: 공직권한 남용/금품향응/예산횡령/재무부정/이해충돌/사법방해/구조적 포획) + ICIJ 4노드 그래프 데이터 모델 + Santa Clara Principles 2.0 + IFCN + K-MHaS 한국어 분류기, (4) 익명(GlobaLeaks Tor)/실명(SNS) 채널 아키텍처 분리 + "So What?" 권익위·언론사 연계 파이프라인, (5) Web-first PWA 권장 (한국 데스크톱 ~48% + App Store Guideline 1.1.1 UGC 폭로 앱 리스크 + iOS 푸시 10-15x↓), Next.js + Postgres(recursive CTE 지식그래프) + Redis + Meilisearch + Cloudflare R2(zero egress) + BullMQ + Fly.io 스택 월 $87-100, (6) 수익모델 복합형 70% 시민후원 + 20% 데이터/API 라이선스(OCCRP Aleph) + 10% 그랜트 + 광고/정부지원/암호화폐 단독 회피, (7) 12-24개월 3-Phase 로드맵 + 정치중립 헌장 + SLAPP 대응 + 콘텐츠위원회·시민자문위원회·법무자문단. 출처 16건. 본 v1은 document-review + rl-verify 검증 대기.

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
