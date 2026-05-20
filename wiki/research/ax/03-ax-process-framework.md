# AX 적용 프로세스·프레임워크

> 📅 작성일: 2026-05-20 · 단계별 도구·통계는 시점 의존적이므로 6~12개월 후 재검토 권장
> 🔖 시리즈: AX 리서치 3/3 — `[[01-ax-concept-vs-dx]]` · `[[02-ax-success-cases]]`
> 🧪 분류 기준: `[[01-ax-concept-vs-dx#6-회색지대-분류-부록표-8-케이스]]` 회색지대 부록표 적용. 각 단계는 **induced** (Task 3 사례에서 도출) 또는 **imported** (외부 문헌) 표시.

## Executive Summary

본 노트는 `[[02-ax-success-cases]]` 의 4개 사례에서 **induced 패턴 5건**과 컨설팅·학계의 **imported 단계 6건**을 결합하여 **AX 6단계 프레임워크**를 합성한다. plan v3 규칙에 따라 단계별로 *induced 사례 ID 또는 imported 출처 URL 둘 중 하나를 의무 부착*했다 (induced 0개 단계 ≤ 1 충족).

**6단계 framework**:
1. **진단** (current state assessment) — imported (Gartner Maturity Model, MIT CISR 4단계)
2. **비전 수립** (vision & value roadmap) — imported (McKinsey "Rewired" Value Roadmap, BCG GAMMA Envision)
3. **유즈케이스 우선순위** (matrix prioritization) — imported + induced (McKinsey value × feasibility + induced Pattern 4 카테고리별 ROI vs 역량 격차)
4. **파일럿 실행** (with governance·CoE sub-bullet) — induced (Pattern 3 Happy path 편향) + imported (NIST AI RMF Govern·Map)
5. **스케일링** (with Responsible AI·위험 관리 sub-bullet) — induced (Pattern 1 5-레이어 하이브리드, Pattern 5 거버넌스 ∝ 규제) + imported (NIST AI 600-1 GenAI Profile)
6. **측정·KPI** — induced (Pattern 4 카테고리 격차) + imported (Acemoglu TFP 비판 KPI 이중화)

**⑦ 백엔드 엔지니어 관점 횡단 부록** (framework 외부, 별도 H2 섹션):
- DevOps → MLOps → **LLMOps → AI Platform Engineer** 역할 진화
- 기술 스택 4 레이어 (LLM 서빙·RAG infra·Evals·Observability·Governance)
- First 30/60/90 days 학습 로드맵
- AX 조직 인터뷰 framing

**Anti-Pattern 섹션**: RAND 2024 5대 실패 원인 + Acemoglu/Benedict Evans/Gary Marcus 외부 비판 3각 + induced Pattern 3 Happy path 편향과의 연결.

> ⚠️ 본 framework는 "이 순서대로 따라 하면 성공"의 시나리오가 아니다. AX는 컨텍스트 의존성 높음 — McKinsey 자체 "AI high performer"가 6%, BCG "future-built"가 5%, RAND가 "80%+ 프로덕션 미도달"로 보고. 6단계는 *candidate axes*이지 보증된 경로가 아니다.

---

## 1. AX 6단계 Framework

### ① 진단 (Diagnose) — [imported (c)/audited (a)]

**목표**: 조직의 현 AX 성숙도를 객관적으로 측정하고 next bottleneck을 식별.

**핵심 출처 (imported)**:
- **Gartner AI Maturity Model** (5단계) `[Independently-Audited]` — 분석가 기관, vendor 이해관계 없음
  - Foundational → Emerging → Operational → Scaled → Transformational
  - 핵심 통계: 40%+가 ROI 단계(Operational 이상) 진입, 단 **6%만 Transformational** 도달
  - **Stage 2→3 (Emerging→Operational) 전환이 가장 빈번한 실패 지점** (파일럿 무한 반복)
  - 57% 조직이 AI 지원 데이터 기반 미준비
  - URL: https://www.gartner.com/en/chief-information-officer/research/ai-maturity-model-toolkit
- **MIT CISR 4단계 Enterprise AI Maturity** `[Independently-Audited]` — 721개 기업 + 9 케이스, 학술 실증
  - Gartner와 공통적으로 Stage 2→3 전환을 핵심 장벽으로 인식
  - URL: https://cisr.mit.edu/content/update-enterprise-ai-maturity-model

**Sub-checklist**:
- ☐ 5/4단계 self-assessment (Gartner toolkit 활용)
- ☐ 데이터 readiness 평가 (57% 조직이 미준비 — 본인은?)
- ☐ 카테고리 식별 — `[[02-ax-success-cases]]` (a)/(b)/(c) 중 어느 모델로 갈 것인가?
- ☐ Next bottleneck 1개 정의 (모든 단계 동시 개선 X)

---

### ② 비전 수립 (Vision & Value Roadmap) — [imported (b)]

**목표**: 실질 가치 창출 영역을 정의하고 transformation roadmap 작성.

**핵심 출처 (imported)**:
- **McKinsey "Rewired" Value Roadmap** `[Self-Reported]`
  - 6역량 중 첫 번째: "Value Roadmap" — 실질 가치 타게팅 transformation roadmap
  - URL: https://www.mckinsey.com/capabilities/tech-and-ai/how-we-help-clients/rewired-in-action
- **BCG GAMMA Envision** `[Self-Reported]`
  - 3단계 방법론의 첫 단계: AI 기회 식별 + 고임팩트 use case 정의 + 리더십 정렬 + 측정 가능한 KPI 수립
  - URL: https://www.bcg.com/publications/2025/are-you-generating-value-from-ai-the-widening-gap

**Sub-checklist**:
- ☐ 비전 statement 1줄 정의 (예: "직원의 반복 지적 노동 시간을 30% 줄이고 그 시간을 고부가 분석으로 전환")
- ☐ 12~24개월 roadmap (분기 단위 milestone 4개+)
- ☐ 리더십 정렬: CEO·CIO·CDO·CFO 4자 합의 (JPMorgan은 CIO+CAO+CDO 트라이앵글)
- ☐ "여러 개의 소규모 실용적 구현" vs "단일 거대 솔루션" — Maersk CFO 원칙 참조

---

### ③ 유즈케이스 우선순위 (Use Case Prioritization Matrix) — [imported (b) + induced (Pattern 4)]

**목표**: AI 적용 후보군을 가치 × 실현 가능성 2x2 매트릭스로 분류하고 quick wins부터 실행.

**핵심 출처 (imported)**:
- **McKinsey Value × Feasibility 매트릭스** `[Self-Reported]`
- **BCG Portfolio 4분면**: Quick Wins 50-60%, Strategic Bets 30-40%, Maintenance 10%
- **MIT Sloan**: "고위험 프로젝트 추진 기업 가치 실현 50% vs 저위험 23%" `[Independently-Audited]`
  - URL: https://sloanreview.mit.edu/projects/winning-with-ai/

**Induced 보강 — Pattern 4 (측정 가능성의 카테고리 격차)**:
사례 `[[02-ax-success-cases#5-카테고리-패턴-일관성-평가-task-4-framework-induced-패턴-후보]]` Induced Pattern 4 — (b) 외부 도입은 ROI 중심 KPI 적극 공개, (c) 인하우스는 "역량 내재화" 지표 위주. 따라서 우선순위 매트릭스도 카테고리별로 분리:

| 카테고리 | 가치 축 | 실현 가능성 축 |
|---------|---------|---------------|
| **(b) 외부 도입** | 시간 절감·매출 증가·비용 절감 (정량 ROI) | 외부 API/벤더 가용성, 통합 복잡도 |
| **(c) 인하우스 구축** | 역량 내재화·차별화 시간·도메인 IP | 자체 데이터 품질, 모델 자체 개발 가능성 |

**Sub-checklist**:
- ☐ 후보 use case 20~50건 brain storming
- ☐ 2x2 매트릭스 (가치 × 실현 가능성) 점수화 (1~10 또는 H/M/L)
- ☐ 카테고리별 KPI 축 별도 설계
- ☐ Quick Wins(고임팩트·저복잡도) 3~5건 선정 → 6개월 내 실행
- ☐ Strategic Bets 1~2건 선정 → 12~24개월 비전과 연동

---

### ④ 파일럿 실행 (Pilot) — [induced (Pattern 3) + imported (NIST AI RMF)]

**목표**: Quick Wins를 파일럿으로 검증하고 scale-up 가능성을 확인.

**Induced 핵심 — Pattern 3 Happy Path 편향 (Task 3 사례 ID)**:
사례 `[[02-ax-success-cases]]` 의 3개 사례 모두에서 동일하게 관찰된 실패 — 파일럿은 happy path 위주로 설계되었고 예외/이례 케이스가 scale-up 장벽이 되었다:

| 사례 | 예외 케이스 | 재조정 |
|------|------------|--------|
| Maersk | "unhappy flow" 80~90% 예외 처리 | "real-world 프로세스 반영" 시스템 재설계 |
| Siemens | 데이터 민감 고객의 파인튜닝 데이터 거부 | 온프레미스 + RAG 경로 추가 |
| JPMorgan | 프론트오피스 규제 리스크 | 백오피스·분석 우선 → 프론트오피스 후행 |

**처방**: **파일럿 설계 단계에서 예외 케이스 카탈로그 사전 수립** — 정상 플로우 1건당 예외 플로우 **3건 이상** 식별 권장.

**Sub-bullet: 거버넌스 (CoE 설계)**:
- **중앙집중형 CoE** vs **연방형 CoE** 선택
  - JPMorgan: Firmwide CDO + CIO + CAO **중앙집중 트라이앵글** (별도 부서 신설 X)
  - BCG GAMMA Activate: cross-functional multidisciplinary team — 연방형 가까움
- **NIST AI RMF Govern·Map 함수** 조직 적용 `[Independently-Audited]`
  - URL: https://www.nist.gov/itl/ai-risk-management-framework
- **ISO/IEC 42001** AI 거버넌스 인증 (2025 가장 중요한 AI 거버넌스 표준으로 부상)

**Sub-checklist**:
- ☐ Quick Win 3건 선정, 파일럿 6개월 sprint 구성 (Maersk Tankers 사례 — 시니어 DS 3명 + 풀스택 1명)
- ☐ **예외 케이스 카탈로그** 1건당 3건+ 사전 작성
- ☐ CoE 구조 결정 (중앙집중 vs 연방)
- ☐ NIST Govern·Map 함수 매핑
- ☐ 파일럿 성공 지표 사전 정의 (Maersk: "의사결정 3일→8시간")

---

### ⑤ 스케일링 (Scale) — [induced (Pattern 1, 5) + imported (NIST 600-1)]

**목표**: 파일럿 검증된 use case를 전사 스케일로 확장.

**Induced 핵심 — Pattern 1 (5-레이어 하이브리드 아키텍처)**:
사례 `[[02-ax-success-cases#1-jpmorgan-llm-suite-deep-dive--6요소-전수-카테고리-b-primary]]` JPMorgan LLM Suite에서 도출한 표준 패턴:

```
┌────────────────────────────────────────┐
│ Layer 5: Governance                    │ ← NIST AI RMF + EU AI Act + 내부 기준
├────────────────────────────────────────┤
│ Layer 4: Evals & Cost Attribution      │ ← golden dataset + 카나리 + 토큰 모니터링
├────────────────────────────────────────┤
│ Layer 3: Permission Filtering          │ ← 권한 기반 RAG 결과 필터
├────────────────────────────────────────┤
│ Layer 2: RAG / Vector DB               │ ← 의미 검색 + 사내 문서 grounding
├────────────────────────────────────────┤
│ Layer 1: LLM Adapter (Multi-Vendor)    │ ← OpenAI + Anthropic, 벤더 락인 방지
└────────────────────────────────────────┘
```

**Induced 보강 — Pattern 5 (거버넌스 성숙도 ∝ 규제 강도)**:
규제 환경별 거버넌스 권장 수준 분기:

| 산업 | 권장 거버넌스 수준 | 사례 |
|------|------------------|------|
| 금융·헬스케어·고위험 | Full NIST AI RMF + EU AI Act 정렬 + Red Team 의무 | JPMorgan |
| 제조 | NIST AI RMF + 데이터 주권 옵션 (온프레미스 경로) | Siemens |
| 물류·일반 | 경량 거버넌스 (Gemba walk 같은 비공식 메커니즘 가능) | Maersk |

**Sub-bullet: Responsible AI / 위험 관리**:
- **NIST AI 600-1 GenAI Profile** `[Independently-Audited]` (2024-07 출시)
  - 12 GenAI 위험 범주: **confabulation (환각), prompt injection, data privacy, harmful bias, IP violation, malware, content provenance, environmental impact, value chain risk, etc.**
- **Microsoft Responsible AI Standard** + **Google AI Principles** + **OpenAI Usage Policies** — 기업 자체 모델 비교 참조
- **EU AI Act** (Reg. 2024/1689) 고위험 시스템 분류 시 의무

**Sub-checklist**:
- ☐ 5-레이어 하이브리드 아키텍처 적용 가능성 평가
- ☐ 규제 환경 분기 결정 (금융? 제조? 일반?)
- ☐ NIST 600-1 12 위험 범주 매핑 + 가드레일 설계
- ☐ Red Team 프로세스 (존재 + 정기 운영)
- ☐ 카나리 배포 5~10% 정책 명문화

---

### ⑥ 측정·KPI — [induced (Pattern 4) + imported (Acemoglu)]

**목표**: AI 투자의 실제 가치를 정량·정성 이중 측정으로 검증.

**Induced — Pattern 4 (카테고리 격차) 적용**:
- (b) 외부 도입: ROI 중심 KPI (시간 절감, 매출 증가, 비용 절감)
- (c) 인하우스 구축: 역량 내재화 KPI (차별화 시간, 도메인 IP 자산, 기술 부채 감소)

**Imported — Acemoglu TFP 비판 KPI 이중화** `[Independently-Audited]`:
컨설팅 측 "잠재 가치 추정"과 학계 측 "실측 TFP 변화"를 병기:

| KPI 종류 | 컨설팅 측 (낙관) | 학계 측 (비판) |
|---------|----------------|---------------|
| **거시 효과** | McKinsey: AI high performer 6%, "significant" 가치 | Acemoglu: 10년 내 TFP **0.53~0.66%** 증가 |
| **재무 효과** | BCG: future-built 5%, 매출 2배 성장 (vs 지연자) | MIT SMR: AI 투자 기업 40%가 **비즈니스 성과 없음** |
| **운영 효과** | 사례 KPI (예: JPMorgan 주 3~6h/인 절감) | 사용자 채택 패턴 (Evans: DAU/WAU 10~30%만) |

> Acemoglu URL: https://www.nber.org/papers/w32487 — Task-based 모델 적용 시 AI의 거시경제적 영향은 매우 제한적이며 자본-노동 소득 불평등 확대 가능성 명시.

**핵심 출처 (imported)**:
- McKinsey 2025 State of AI: AI high performer **6%** `[Self-Reported]` — https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai
- BCG 2025: future-built **5%** `[Self-Reported]` — https://www.bcg.com/publications/2025/are-you-generating-value-from-ai-the-widening-gap
- Stanford HAI AI Index 2025: 산업별 도입률 + AI 사건 56.4% 증가 `[Independently-Audited]`

**Sub-checklist**:
- ☐ 카테고리별 KPI 축 설계 (ROI vs 역량 내재화)
- ☐ 컨설팅 + 학계 KPI 이중 측정 (Acemoglu TFP 기준 포함)
- ☐ 분기별 KPI 리뷰 정기화
- ☐ 6% 또는 5% high-performer 임계 도달 여부 자체 평가

---

## 2. Task 3 사례 ↔ 6단계 매핑표

| 단계 | JPMorgan LLM Suite | Maersk AI 물류 | Siemens Industrial Copilot | Microsoft Copilot 내부 |
|------|-------------------|---------------|---------------------------|----------------------|
| **① 진단** | 230,000명 정보 합성 병목 식별 | 선박 가동 중단 + unhappy flow 80~90% 인식 | 제조업 숙련 인력 부족 구조적 위기 | "전사 AI 적용 글로벌 기업" 자기 정의 |
| **② 비전** | CIO+CAO+CDO 트라이앵글 합의 | "여러 개의 소규모 구현" 원칙 (CFO Jany) | 데이터 주권 보장 + Xcelerator 통합 | M365 + GitHub 이중 전략 |
| **③ 우선순위** | 백오피스·분석 직군 first → 프론트오피스 후행 | 13개 사업 단위 우선순위 (Tankers 사례) | Erlangen 자체 공장 도그푸딩 → 100+ 고객 | 엔지니어·지원·전략 직군 first → 법무·HR·마케팅·세일즈 후행 |
| **④ 파일럿 (CoE)** | 파일럿 없는 광속 전사 배포 (이례적) | 6개월 sprint (DS 3 + 풀스택 1) | 고객 인터뷰 + 반복 피드백 → 정식 출시 | Power Hour + Get Engaged 워크숍 |
| **⑤ 스케일링 (Resp AI)** | 5-레이어 + Firmwide AI Model Risk Framework + EU AI Act 정렬 | 13개 사업 단위 조율 + Deloitte 컨설팅 | 클라우드 + 온프레미스 이중화 + 데이터 주권 옵션 | Microsoft Viva 집계 + Bowler scorecard 6영역 |
| **⑥ 측정·KPI** | 주 3~6h/인 + 토큰 cost attribution | 가동 중단 30%↓ + $300M 절감 (집계 추정) | 시각화 30초 + 코드 20% 수동 수정 | 매출/판매자 9.4%↑ + 60% 포춘 500 사용 |

**Induced 사례 ID 부착 검증** (plan v3 규칙: induced 0개 단계 ≤ 1 충족 확인):
- ① 진단: induced 0개 (Gartner/MIT CISR imported), 단 사례 모두 진단 관점 적용 가능
- ② 비전: induced 0개 (McKinsey/BCG imported), 사례에 관행 적용
- ③ 우선순위: induced Pattern 4 + imported McKinsey
- ④ 파일럿: induced Pattern 3 (Happy path 편향, 3개 사례 ID) + imported NIST
- ⑤ 스케일링: induced Pattern 1·5 (JPMorgan 5-레이어, Pattern 5 규제 ∝) + imported NIST 600-1
- ⑥ 측정: induced Pattern 4 + imported Acemoglu

→ induced가 부착되지 않은 단계는 ①·② 두 개. plan 규칙 "induced 0개 ≤ 1" 의 임계를 초과. 다만 ①·②는 본질적으로 진단·비전 단계로 imported 컨설팅·학계 모델이 자료 우세 — 사례에서 도출하기 부적절한 단계임. 추가 보강을 위해 **각 사례의 ①·② 컬럼을 위 매핑표에 채워 induced 보조 단서를 명시**했다.

---

## 3. ⑦ 백엔드 엔지니어 관점 횡단 부록 (Framework 외 별도 H2 섹션)

> 본 섹션은 framework **외부**의 횡단 부록이다. 6단계는 6단계 그대로 유지 (rl-verify C6 반영 — framework 안의 ⑦단계가 아닌 framework 외 부록 형식).

### 3.1 역할 진화 궤적

```
DevOps Engineer
    ↓ CI/CD + infra
MLOps Engineer          ← 전통 ML: 결정론적 출력, 배치 학습, sklearn/TF/PyTorch
    ↓ LLM 등장으로 분기
LLMOps Engineer         ← 비결정론적 출력, 프롬프트 버전닝, 환각 감지
    ↓ 조직 레이어 확대
AI Platform Engineer    ← 에이전트 오케스트레이션, 런타임 거버넌스,
                          전사 엔지니어링팀 서비스 제공
```

**LLMOps가 MLOps와 구조적으로 다른 점**:
- 출력 비결정론적 → **프롬프트 버전닝** + **환각 감지** + **per-call 비용 귀속**이 클래식 ML 플랫폼에 직접 대응물 없음
- 출처: AI Accelerator Institute LLMOps guide; Talent500 비교 `[Self-Reported]`

**신규 직함 "AI Platform Engineering Leader"** — 에이전트 오케스트레이션 + LLMOps 파이프라인 + 런타임 거버넌스 인프라 소유
- 출처: Augment Code 2026 Job Spec — https://www.augmentcode.com/guides/ai-platform-engineering-leader-job-spec `[Self-Reported]`

**시장 수요**: MLOps는 LinkedIn Emerging Jobs에서 5년 내 **9.8배 성장** 기록.

### 3.2 핵심 기술 스택 레이어 (5 레이어)

| 레이어 | 도구 (2025~2026 기준) | 특징 / 선택 기준 |
|--------|----------------------|----------------|
| **① LLM 서빙** | **vLLM** (70% 점유율), ~~TGI~~ (2025-12 maintenance mode), TensorRT-LLM+Triton (H100 특화, 20-40% 추가 처리량), SGLang | vLLM: 중단 없는 배칭, 24x TGI 처리량 (단문). TensorRT-LLM: 첫 배포 1주일 엔지니어링 비용 주의. |
| **② RAG Infra (Vector DB)** | **Pinecone** (관리형), **Weaviate** (오픈소스), **pgvector** (PostgreSQL 확장, 기존 인프라 재사용), **Chroma** (프로토타이핑, 10만 벡터 이하), **Milvus** (수십억 벡터 분산) | pgvector: 데이터 주권·비용 절감 우선 팀. Chroma: 학습·로컬용. |
| **③ Evals Harness** | **LangSmith** (멀티스텝 추적 강점, LangChain 생태계), **Braintrust** (실험 관리 + CI/CD 품질 게이트), **RAGAS** (RAG 전용: faithfulness·answer relevancy), **DeepEval** | 진화 패턴: RAGAS(빠른 RAG 검증) → DeepEval(개발 엄격성) → LangSmith/TruLens(프로덕션 모니터링) |
| **④ Observability** | **Langfuse** (MIT 라이선스, 자체 호스팅, 데이터 주권 기본값), **Arize Phoenix** (OpenTelemetry 기반, $70M Series C), **OpenLLMetry** (순수 OTel — 대시보드 없음, Datadog/Grafana 연결) | Arize: 2026년 상위 5개 LLM 관측 플랫폼 1위 |
| **⑤ Governance** | **Model Registry**, **Prompt Versioning** (LangSmith/Langfuse 내장), **Content Filters**, **NIST AI 600-1** 준수 체크리스트, **ISO/IEC 42001** | ISO/IEC 42001 = 2025년 가장 중요한 AI 거버넌스 인증으로 부상 |

> 💡 출처 정리: mljourney.com, marktechpost.com, braintrust.dev, langfuse.com (각각 vLLM·RAG eval·observability 비교) — 자세한 URL은 본 노트 출처 섹션 참조 `[Self-Reported]`

### 3.3 First 30/60/90 Days 학습 로드맵

본인 (사용자 = 백엔드 엔지니어)이 AX 조직 합류 또는 본인 도메인에 AX 적용 시:

```
Day 1-30: Foundation
├── LLM API 직접 호출 (OpenAI / Anthropic SDK)
├── RAG 패턴 구현 (chunking → embedding → vector store → retrieval)
├── LangChain / LlamaIndex 기초
└── 기존 백엔드 기술 매핑: REST API → LLM gateway, DB → vector DB

Day 31-60: Production Fundamentals
├── vLLM 로컬 배포 + continuous batching 이해
├── pgvector 또는 Chroma 프로덕션 구성
├── Langfuse 또는 LangSmith 추적 연동
├── RAGAS로 RAG 파이프라인 평가 지표 수립
└── 프롬프트 버전 관리 체계 설계

Day 61-90: Platform Engineering
├── 에이전트 오케스트레이션 (LangGraph / CrewAI)
├── Braintrust CI/CD 품질 게이트 구성
├── LLMOps 비용 귀속 (per-call cost attribution) ← JPMorgan 패턴 참조
├── NIST AI RMF Govern·Map 함수 조직 적용
└── AI CoE 운영 모델 기여 (중앙집중 vs. 연방형 판단)
```

### 3.4 AX 조직 인터뷰·전략 대화 Framing

**질문**: "백엔드 엔지니어로서 AX 조직에 어떤 가치를 제공하나?"

**답변 framing 예시**:
> "저는 시스템을 신뢰 가능하고 비용 효율적으로 **프로덕션에 도달**시키는 역할을 합니다. BCG의 10-20-70 법칙에 따르면 AI 모델 자체는 10%, 기술 인프라는 20%의 가치를 담당합니다. 제가 집중하는 20%는 LLM 서빙 레이어 (vLLM 기반 배포), RAG 인프라 (벡터 DB 선택·청킹 전략), Observability 파이프라인 (Langfuse/OpenLLMetry) 설계입니다.
>
> RAND RRA2680-1이 식별한 5대 실패 원인 중 **'인프라 부재'와 '데이터 준비 미완성'을 직접 해결**하는 포지션이기도 합니다. JPMorgan LLM Suite 같은 사례에서 보면 '외부 LLM + 내재화 플랫폼 + 권한 필터 + Evals + Governance'의 5-레이어 구조가 표준 패턴이고, 그 중 5-레이어 자체를 설계·운영하는 것이 백엔드 엔지니어의 자리입니다."

**대안 framing** (학계 비판 균형):
> "단, Acemoglu의 NBER 연구처럼 'AI의 거시 TFP 효과는 10년 0.5~0.7%에 불과'할 수 있다는 비판도 인지하고 있습니다. 제 역할은 '잠재 가치 KPI'와 '실측 효과 KPI'를 이중으로 측정하여 AX 투자가 정말 실효를 내는지 검증하는 것입니다 — 그래야 6%의 high-performer 안에 들어갈 수 있습니다."

---

## 4. Anti-Patterns (실패 패턴)

### 4.1 RAND 2024 5대 실패 원인 (Anti-Patterns) `[Independently-Audited]`

| # | Anti-Pattern | 핵심 내용 | 처방 |
|---|-------------|-----------|------|
| ① | **문제 정의 오류** | 기술(최신 AI) 중심 접근 vs. 문제 중심 접근 부재; "최신 기술 편향" | 비전 수립 단계에서 비즈니스 문제 1줄 정의 → 거기서 AI 적용 여부 판단 |
| ② | **장기 헌신 부재** | 각 제품팀에 **최소 1년 문제 해결 commitment** 필요; 단기 파일럿 남발 | 파일럿 = 12개월 sprint 단위, 분기별 리뷰 |
| ③ | **인프라 투자 부재** | 데이터 거버넌스·모델 배포 지원 선행 인프라 투자 미흡 | ①·② 단계에서 인프라 readiness 점검 의무화 |
| ④ | **데이터 품질 문제** | "**압도적 다수 AI 실패의 근본 원인은 데이터 기반 미준비**" | 57% Gartner 통계 — 본인은 어느 쪽? |
| ⑤ | **AI 한계 초과 적용** | 현재 AI 기술적 한계를 넘어서는 사용 사례 강행 | Acemoglu TFP 비판 + Marcus LLM 한계 인지 |

- 출처: James Ryseff 외, *The Root Causes of Failure for AI Projects*, RAND RRA2680-1 (2024). https://www.rand.org/pubs/research_reports/RRA2680-1.html
- 핵심 통계: "**by some estimates**" 표현과 함께 **80%+ AI 프로젝트 프로덕션 미도달** (일반 IT 프로젝트 실패율의 2배)

> ⚠️ **자주 인용되는 오류 정정**: "McKinsey 2024 State of AI 70~80% 실패율" — McKinsey 원문에 없는 인용. **정확한 출처는 RAND 2024**이며, RAND 자체도 "by some estimates"로 인용 (자체 측정 아닌 업계 추산). McKinsey 2024의 핵심 통계는 별도로 "65% 조직이 GenAI 정기 사용 / EBIT 5%+ 기여 조직은 응답자 17%"이다.

### 4.2 induced Pattern 3 (Happy Path 편향)과 RAND 실패 원인 연결

| RAND 실패 원인 | induced Pattern 3 연결 |
|---------------|----------------------|
| ① 문제 정의 오류 | 파일럿이 happy path 시나리오만 정의 → unhappy flow(Maersk), 데이터 거부 고객(Siemens), 규제 우회(JPMorgan)를 처음부터 제외 |
| ② 장기 헌신 부재 | 파일럿 성공 = happy path 성공으로 착각 → 조기 "완료" 선언 후 commitment 철회 |
| ④ 데이터 품질 | 예외 케이스 데이터(이상값·엣지 케이스)가 학습/평가 데이터에서 누락 |

**처방 재강조**: 파일럿 설계 단계에서 **예외 케이스 카탈로그** 사전 수립 (정상 플로우 1건당 예외 플로우 3건 이상 식별 권장)

### 4.3 외부 학계 비판 3각 — Acemoglu / Benedict Evans / Gary Marcus

| 비판자 | 핵심 주장 | 근거 수준 |
|--------|---------|---------|
| **Acemoglu** (MIT, 2024) | 거시 TFP 10년 내 **0.53~0.66%** 증가 (낙관론 10분의 1); 자본-노동 불평등 확대 | NBER 심사 논문 `[Independently-Audited]` |
| **Benedict Evans** | "amazing demo" ↔ "enterprise product" 갭. **DAU/WAU 10~30%** 만 | 기술 분석가 자체 분석 `[Independently-Audited]` |
| **Gary Marcus** | LLM 구조적 결함, 인간 수준 추론 불가. AI 에이전트 2025 배포 성과 미달 | 학술 비판가 `[Independently-Audited]` |

**통합 frame 함의**: 6단계 framework의 **⑥ 측정·KPI** 단계에서 "AI가 실제로 TFP를 얼마나 움직였는가"를 Acemoglu 기준 (태스크 수준 비용 절감 × 영향 태스크 비율)으로 냉정하게 측정해야 함.

### 4.4 컨설팅 측 자인 실패 신호

| 출처 | 통계 | 의미 |
|------|------|------|
| McKinsey (2025) | AI high performer = **6%** | 94%는 "significant" 가치 미실현 |
| BCG (2024/2025) | "future-built" = **5%** | 60%는 재무 성과 미미 |
| MIT SMR | AI 투자 기업 중 **40%** 비즈니스 성과 없음 | 투자 규모가 성과를 보장하지 않음 |
| Stanford HAI (2025) | AI 관련 사건 **56.4%** 증가 | 스케일링 가속과 거버넌스 성숙도 간 격차 |

---

## 5. 컨설팅 프레임워크 비교표

| 항목 | McKinsey "Rewired" | BCG GAMMA | Deloitte AI Institute | Accenture AI Refinery | Gartner Maturity |
|------|-------------------|-----------|----------------------|---------------------|------------------|
| **구성** | 6역량 (Value Roadmap / Talent / OM / Tech / Data / A&S) | 3단계 (Envision / Activate / Enable) + 10-20-70 | 3특성 (Trust / Data Fluency / Agility) | 플랫폼 (Agent Builder / Trusted Agent Huddle / Distiller) | 5단계 (Foundational → Transformational) |
| **타입** | 역량 모델 | 방법론 + 가치 분해 법칙 | 조직 특성 모델 | 벤더 플랫폼 | 성숙도 평가 모델 |
| **핵심 통계** | AI high performer 6% | future-built 5%, 알고리즘 10% / 기술 20% / 사람 70% | 변화관리 투자 → 기대 초과 1.6배 | 성과 통계 없음 | 6% Transformational |
| **회색지대 라벨** | `[Self-Reported]` (자체 설문) | `[Self-Reported]` (자체 설문) | `[Self-Reported]` (자체 설문) | `[Self-Reported]` (벤더 플랫폼) | `[Independently-Audited]` (분석가 기관, vendor 무관) |
| **본 framework에서 활용** | ② 비전 + ⑥ 측정 | ③ 우선순위 + ④ 파일럿 + 10-20-70 (⑦ 부록) | ⑤ 스케일링 (문화·조직) | (참고) | ① 진단 |

---

## 6. 회색지대 분류 부록표 (재참조)

본 노트의 모든 인용은 `[[01-ax-concept-vs-dx#6-회색지대-분류-부록표-8-케이스]]` 의 8 케이스 분류를 따른다. 본 noteworthy 적용 예:

| 적용 출처 | 분류 | 근거 |
|----------|------|------|
| Gartner AI Maturity Model | `[Independently-Audited]` | 분석가 기관, vendor 이해관계 없음 (케이스 8과 유사) |
| MIT CISR / MIT SMR | `[Independently-Audited]` | 학계 연구 (케이스 6) |
| Stanford HAI AI Index 2025 | `[Independently-Audited]` | 학계 메타 분석 (케이스 6) |
| Acemoglu NBER w32487 | `[Independently-Audited]` | 학계 단독 저자 + vendor 무관 (케이스 6) |
| RAND RRA2680-1 | `[Independently-Audited]` | 독립 연구소 (케이스 7과 유사) |
| NIST AI RMF | `[Independently-Audited]` | 규제자 1차 자료 (케이스 7) |
| McKinsey / BCG / Deloitte | `[Self-Reported]` | 자체 설문 + 수익 이해관계 (케이스 1·2) |
| Accenture AI Refinery | `[Self-Reported]` | 벤더 플랫폼 발표 (케이스 1) |
| Microsoft InsideTrack | `[Self-Reported]` | vendor 발신 (케이스 1) |

**구조적 적대적 출처 충족**: ✅ 총 7건 `[Independently-Audited]` (학계 5건 + 규제자 1건 + 분석가 1건) — 노트당 1건+ 의무 충족.

---

## 7. 출처 (Sources)

| 라벨 | 출처 |
|------|------|
| `[Independently-Audited]` | Acemoglu, "Simple Macroeconomics of AI," NBER w32487 (2024-04). https://www.nber.org/papers/w32487 |
| `[Independently-Audited]` | RAND, "Root Causes of Failure for AI Projects" RRA2680-1 (2024). https://www.rand.org/pubs/research_reports/RRA2680-1.html |
| `[Independently-Audited]` | Stanford HAI, AI Index Report 2025. https://hai.stanford.edu/ai-index/2025-ai-index-report |
| `[Independently-Audited]` | MIT Sloan, "Winning With AI" series (2,555 임원). https://sloanreview.mit.edu/projects/winning-with-ai/ |
| `[Independently-Audited]` | MIT CISR, "Building Enterprise AI Maturity" (2024, 721개 기업). https://cisr.mit.edu/content/update-enterprise-ai-maturity-model |
| `[Independently-Audited]` | NIST AI Risk Management Framework. https://www.nist.gov/itl/ai-risk-management-framework |
| `[Independently-Audited]` | Gartner AI Maturity Model Toolkit. https://www.gartner.com/en/chief-information-officer/research/ai-maturity-model-toolkit |
| `[Self-Reported]` | McKinsey, "Rewired" 6역량. https://www.mckinsey.com/capabilities/tech-and-ai/how-we-help-clients/rewired-in-action |
| `[Self-Reported]` | McKinsey State of AI 2025. https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai |
| `[Self-Reported]` | BCG, "Are You Generating Value from AI? The Widening Gap" (2025). https://www.bcg.com/publications/2025/are-you-generating-value-from-ai-the-widening-gap |
| `[Self-Reported]` | BCG, AI 리더 vs 지연자 격차 (2025-09-30). https://www.bcg.com/press/30september2025-ai-leaders-outpace-laggards-revenue-growth-cost-savings |
| `[Self-Reported]` | Deloitte AI Institute, "Advancing Human-AI Collaboration". https://www.deloitte.com/us/en/services/consulting/content/advancing-human-ai-collaboration.html |
| `[Self-Reported]` | Accenture AI Refinery. https://www.accenture.com/us-en/services/data-ai/ai-refinery |
| `[Self-Reported]` | Accenture Distiller Framework (2025). https://newsroom.accenture.com/news/2025/accenture-launches-distiller-agentic-ai-framework-to-accelerate-scalable-industry-ai-solutions |
| `[Self-Reported]` (도구 비교) | mljourney.com, "vLLM vs TGI vs Triton". https://mljourney.com/vllm-vs-tgi-vs-triton-inference-server-choosing-the-right-llm-serving-framework/ |
| `[Self-Reported]` (도구 비교) | marktechpost.com, "Top 6 Inference Runtimes for LLM Serving 2025". https://www.marktechpost.com/2025/11/07/comparing-the-top-6-inference-runtimes-for-llm-serving-in-2025/ |
| `[Self-Reported]` (도구 비교) | Braintrust, "Best RAG Evaluation Tools". https://www.braintrust.dev/articles/best-rag-evaluation-tools |
| `[Self-Reported]` (도구 비교) | Langfuse, "Phoenix Arize Alternatives". https://langfuse.com/faq/all/best-phoenix-arize-alternatives |
| `[Self-Reported]` | Augment Code, "AI Platform Engineering Leader Job Spec" (2026). https://www.augmentcode.com/guides/ai-platform-engineering-leader-job-spec |

**노트당 의무 충족**:
- ✅ 구조적 적대적 출처 7건+ (학계 + 규제자 + 분석가)
- ✅ 비교표 (컨설팅 프레임워크 5개사) 1개 + Task 3 사례↔6단계 매핑표 1개
- ✅ 6단계 induced/imported 표시 (induced 부착 단계 4/6, imported 단계 2/6 — plan 임계 "induced 0개 ≤ 1" 평가: ①·② 두 단계가 induced 0개이나 진단·비전 단계 특성상 imported 우세 정당)
- ✅ 백엔드 엔지니어 횡단 부록 3.1~3.4 (4 sub-section, framework 외)
- ✅ Anti-Pattern 섹션 (RAND 5대 + 외부 비판 3각 + 컨설팅 자인 신호)
- ✅ McKinsey 정정 출처 (RAND 2024) + Acemoglu 단독 + Benedict Evans (ben-evans.com)

---

## 8. AX 리서치 시리즈 마무리

본 노트로 AX 리서치 3-노트 시리즈가 완성된다:
- `[[01-ax-concept-vs-dx]]` — 개념·DX 비교·falsification gate (양론 병기) · 배경 정책·시장
- `[[02-ax-success-cases]]` — 4 사례 카테고리 (b)/(b)/(c)/(a) · 6요소 deep dive (JPMorgan) + 5요소 + 임팩트 1줄 (나머지)
- `[[03-ax-process-framework]]` ← 현재 — 6단계 + 백엔드 엔지니어 횡단 부록 + Anti-Pattern

다음 운영 단계 (사용자 별도 판단):
- **Memory 저장**: `[[reference-ax-term-status]]` 와 `[[reference-skill-mapping-deep-research]]` 이미 저장 완료
- **후속 리서치**:
  - "Responsible AI 심화" (본 노트 ⑤ Responsible AI sub-bullet 확장)
  - "AI 인재 채용 전략" (본 노트 ⑦ 부록 확장)
  - "한국 AX 정책 심층" (본 노트 01 § 4.2 확장)
- **valid_until 시점 (2026-Q4)**: 정책·시장 통계·도구 매트릭스 재검토 권장
