# Den Wiki Log

> 추가 전용 (append-only). LLM이 자동 관리합니다.

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
