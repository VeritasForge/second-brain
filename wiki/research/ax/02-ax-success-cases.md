# AX 성공 사례 — 카테고리 분리 분석

> 📅 작성일: 2026-05-20 · 사례 KPI는 시점·기업 발표 의존적이므로 6~12개월 후 재검토 권장
> 🔖 시리즈: AX 리서치 2/3 — `[[01-ax-concept-vs-dx]]` · `[[03-ax-process-framework]]`
> 🧪 분류 기준: 본 노트는 `[[01-ax-concept-vs-dx#6-회색지대-분류-부록표-8-케이스]]` 부록표 8개 케이스에 따라 모든 측정 수치에 `[Self-Reported]` 또는 `[Independently-Audited]` 라벨 부착.

## Executive Summary

본 노트는 AX(AI Transformation) 사례 4개를 plan v3의 카테고리 분리에 따라 분석한다:

| 카테고리 | 사례 | 산업 | Deep dive |
|---------|------|------|-----------|
| **(b) 외부 AI 도입** primary | JPMorgan LLM Suite (2024) | 금융 서비스 | ✅ 6요소 전수 |
| **(b) 외부 AI 도입** primary | Maersk AI 물류 | 해운·물류 | 5요소 + 임팩트 1줄 |
| **(c) 인하우스 AI 역량 구축** primary | Siemens Industrial Copilot | 산업 자동화 SW | 5요소 + 임팩트 1줄 |
| **(a) AI 벤더 도그푸딩** (선택 추가) | Microsoft Copilot 사내 전환 | 소프트웨어·클라우드 | 5요소 + 임팩트 1줄 |

### 핵심 패턴 (Task 4의 framework 작성 시 활용)
1. **"외부 LLM + 내재화 플랫폼"** 하이브리드가 대규모 금융·엔터프라이즈 표준 패턴 (JPMorgan)
2. **"도메인 IP는 자체, 모델 컴퓨팅은 외부"** Hybrid(c) 패턴이 제조업 AI에서 우세 (Siemens)
3. **Pilot의 "Happy path 편향"** — 모든 사례에서 unhappy/exception 케이스가 scale-up 장벽 (Maersk unhappy flow / Siemens 데이터 거부 고객 / JPMorgan 프론트오피스 규제 지연)
4. **측정 가능성 격차** — (b) 외부 도입은 시간·비용 정량 KPI 적극 공개, (c) 인하우스는 "역량 내재화" 지표 위주
5. **거버넌스 성숙도 ∝ 규제 강도** — 금융(JPMorgan) > 제조(Siemens) > 물류(Maersk) 순

### 측정 신뢰도 주의

본 노트의 KPI 수치 대부분이 `[Self-Reported]`다. 회색지대 부록표 적용 결과, 컨설팅·기업 공저·분석가가 vendor 데이터를 인용한 경우 모두 `[Self-Reported]`로 분류. **수치 자체가 검증 불가**라는 점을 명심하고, **패턴·접근법**에서 학습 가치를 추출하는 것이 vault 학습 목적에 맞다.

---

## 사례 비교표

| 항목 | JPMorgan LLM Suite | Maersk AI 물류 | Siemens Industrial Copilot | Microsoft Copilot 내부 |
|------|---|---|---|---|
| **카테고리** | (b) primary | (b) primary | (c) primary | (a) primary |
| **출시 시점** | 2024 여름 | 2023~2024 본격 | 2024-07 정식 출시 | 2023~2024 단계 배포 |
| **산업** | 금융 서비스 | 해운·물류 | 산업 자동화 SW | 소프트웨어·클라우드 |
| **규모** | 직원 230,000명 | 선박 450+ / 100,000 고객 / 130개국 | DI 사업부 70,000명 + 고객 100+ | 직원 ~220,000명 |
| **AI 접근법** | 멀티 LLM 허브 (RAG + 권한 필터) | 예측 유지보수 + GenAI 서비스 + 경로 최적화 | PLC 코드 자동 생성 + 시각화 (RAG) | M365 통합 LLM + GitHub Copilot |
| **핵심 결과** | 8개월 200,000명 온보딩, 주 3~6시간/인 절감 | 가동 중단 30%↓, $300M 절감 (집계) | 시각화 30초 (이전 수 시간), 코드 20%만 수정 | 매출/판매자 9.4%↑ |
| **주요 실패** | 프론트오피스 초기 배포 지연 | unhappy flow 설계 실패 → 재설계 | 데이터 민감 고객 → 온프레미스 경로 추가 | 초기 기능 기초적 수준 |
| **엔지니어링 핵심** | OpenAI+Anthropic 다중 + Azure+Snowflake+AWS | Azure AI + IoT 450척 + LSTM/RF 예측 | Azure OpenAI + TIA Portal + 온프레미스 이중 | M365 네이티브 + GitHub Copilot |
| **Primary 카테고리** | (b) | (b) | (c) | (a) |
| **Secondary** | — | — | (b) — 일부 모델 외부 Azure OpenAI | — |
| **독립 출처 1건+** | ✅ Tearsheet, CIO.com | ✅ Deloitte, devsdata.com | ✅ Automation World | ✅ Microsoft Research 부분 |

---

## 1. JPMorgan LLM Suite (deep dive — 6요소 전수, 카테고리 (b) primary)

### (1) 출발점·문제정의

JPMorgan Chase는 230,000명 이상의 직원이 매일 방대한 리서치·분석 워크플로우를 수행하지만, 내부 문서 접근성과 정보 합성 속도가 성장 병목이었다. 투자 뱅커들이 earnings 트랜스크립트를 수동 분석하거나, 자산관리사들이 고객별 포트폴리오 문서를 일일이 탐색하는 등 반복 지적 노동이 고부가 업무 시간을 잠식했다. 2024년 여름 LLM Suite를 출시한 직접 동기. `[Self-Reported]`

- 출처: JPMorgan Chase 공식 블로그, "LLM Suite Wins American Banker Innovation Award" (2025)
  - URL: https://www.jpmorganchase.com/about/technology/blog/llmsuite-ab-award

> 🔍 **COiN vs LLM Suite 분리** (rl-verify R6 반영):
>
> | 항목 | COiN | LLM Suite |
> |------|------|-----------|
> | 출시 연도 | 2017 (CoE 2016 설립) | 2024 여름 |
> | 시스템 유형 | 특수 목적 ML (NLP + 패턴 인식) | 범용 생성형 AI 플랫폼 |
> | 대상 도메인 | 계약서·법무 문서 분석 | 전 직군 지식 허브 |
> | 모델 기술 | NLP + 이미지 인식 + 비지도 ML | LLM (OpenAI + Anthropic) |
> | 운영 환경 | 사내 Gaia 클라우드 | Azure + Snowflake + AWS |
> | 사용자 규모 | 법무·뱅킹 팀 한정 | 200,000명+ 전 직군 |
> | 결과 | 연 36만 법무 시간 절감 | 주 3~6시간/인 절감 |
>
> 두 시스템은 **기술 세대·도메인·사용자 모두 다른 독립 시스템**이다. 사례 인용 시 혼동 금지.

### (2) 핵심 결정 — 거버넌스·예산·조직

글로벌 CIO **Lori Beer**가 전략 방향을 총괄, Chief Analytics Officer **Derek Waldron**이 LLM Suite 개발을 주도. 2024~2025년 AI 투자 총액 **$18B** 기술 예산 중 핵심 이니셔티브로 배정. AI/ML 및 Data Analytics 리더십(**Katie Hainsey**)이 Digital·Marketing·Operations 전체를 커버.

**이중 구조**:
- 5,000명 데이터 사이언티스트가 SageMaker를 활용하는 분산 모델 개발
- LLM Suite는 200,000+ 일반 사용자 대상의 평면적 액세스 레이어

`[Self-Reported]` · 출처: Tearsheet, "JPMorgan Chase's GenAI Implementation: 450 Use Cases and Lessons Learned" — https://tearsheet.co/artificial-intelligence/jpmorgan-chases-gen-ai-implementation-450-use-cases-and-lessons-learned/ `[Independently-Audited]` (자체 인터뷰 기반 저널리즘)

### (3) 실행 프로세스 — Pilot → Scale → Embed

- **2024 여름**: 출시 → 파일럿 없는 **광속 전사 배포 전략**
- **8개월 내**: 200,000명 온보딩
- **현재 (2025)**: 450건 이상의 agentic AI 유스케이스가 소비자 뱅킹·투자 관리·자산 관리에 배포 중, **1,000건 확장 계획**
- **확장 결정**: 테스트·통제 그룹 A/B 방식으로 "incremental benefit 측정" 후 진행
- **모델 업데이트 사이클**: 8주 고정 — golden dataset 평가 → 5~10% 프로덕션 트래픽 카나리 배포 → 전체 롤아웃

`[Self-Reported]` · 출처: The Data Letter, "AI Infrastructure Engineering Driving JPMorgan" — https://www.thedataletter.com/p/ai-infrastructure-engineering-driving `[Analyst]`

### (4) 측정 결과

| 지표 | 수치 | 출처 | 회색지대 라벨 |
|------|------|------|---------------|
| LLM Suite 온보딩 사용자 | 200,000명 (8개월) | JPMC 공식 블로그 | `[Self-Reported]` |
| 주 절약 시간 | 3~6시간/직원 | JPMC 공식 블로그 | `[Self-Reported]` |
| 투자 뱅커 리서치 자동화 | 40% | The Data Letter | `[Self-Reported]` |
| 포트폴리오 매니저 리서치 시간 단축 | 최대 83% | The Data Letter | `[Self-Reported]` |
| 자산관리사 정보검색 속도 | 95% 향상 | The Data Letter | `[Self-Reported]` |
| 코딩 어시스턴트 생산성 | 10~20% | Tearsheet | `[Self-Reported]` |
| AI 전체 연간 비즈니스 가치 추정 | $1.5~2B | aibmag 분석 | `[Self-Reported]` (분석가 추정) |
| 루틴 워크플로우 시간 단축 | 30~40% | aibmag 분석 | `[Self-Reported]` |
| 총 agentic AI 유스케이스 | 450건+ (1,000건 확장 계획) | Tearsheet 인터뷰 | `[Self-Reported]` |

> ⚠️ 수치 신뢰도: 모두 `[Self-Reported]`. JPMorgan 자체 KPI 측정으로, 회색지대 부록표 케이스 1 (vendor·기업 1차 자료)에 해당. 독립 감사 미존재.

### (5) 실패·재조정

공개 실패 사례는 거의 없다. 다만 Tearsheet 인터뷰에서:
- **프론트 오피스 배포는 규제·고객 데이터 보호를 이유로 신중하게 후행 배포**했다고 언급
- 초기 전사 공개 롤아웃이 백오피스·분석 직군에 집중된 것은 **규제 위험 우회 전략**이었음을 시사
- **사용자 행동 변화** ("기대치와 질문 패턴이 AI 사용 증가와 함께 진화")에 대한 데이터 준비도 문제도 지속적 도전으로 언급

`[Self-Reported]` · 출처: Tearsheet 인터뷰 (위 URL)

### (6) ⭐ 엔지니어링 임팩트 (Deep Dive — 핵심 섹션)

#### 6.1 모델 아키텍처 및 벤더 선택

**모델-agnostic 다중 벤더 전략**:
- **OpenAI** (GPT 계열) + **Anthropic** (Claude 계열)을 단일 인터페이스로 관리
- **벤더 락인 방지를 명시적 설계 목표**로 채택
- 업데이트 사이클은 8주 고정, 모델 교체 시 golden dataset 기반 **regression 평가 먼저 수행**
- 특정 모델 버전은 비공개

`[Self-Reported]` · 출처: The Data Letter (위 URL)

#### 6.2 모델 서빙 인프라

**3-스택 클라우드 분산**:

| 레이어 | 클라우드 | 역할 |
|--------|---------|------|
| **LLM 서빙** | Microsoft Azure | 탄성 확장·보안 스토리지·실시간 컴퓨팅 |
| **데이터 플랫폼** | Snowflake | 전사 데이터 (exabyte 급) 관리 |
| **데이터 사이언스 개발** | AWS SageMaker | 5,000명 데이터 사이언티스트 모델 개발 |
| **데이터 변환·ETL** | AWS Glue | 데이터 자산 관리 |
| **결제 인프라** | AWS EC2 | 결제 처리 |

**Resilience**: 3개 리전 중 **2개 장애 시에도 고객 영향 없는** 아키텍처 (multi-region active-active redundancy).

`[Self-Reported]` · 출처: CIO.com, "JPMorgan Chase Builds Ambitious AI Foundation on AWS" — https://www.cio.com/article/3616622/jpmorgan-chase-builds-ambitious-ai-foundation-on-aws.html `[Independently-Audited]`

#### 6.3 RAG 인프라 및 파인튜닝 접근법

**RAG 기반으로 사내 정책·문서에 모델을 접지(grounding)**:
- 수백만 건 내부 문서를 **벡터 DB로 의미 검색**
- 핵심 보안 메커니즘: 검색 결과를 AI 컨텍스트로 전달하기 전에 **직원 권한 필터링** 적용
  - 투자 뱅커 → 소매 고객 데이터 접근 불가
  - 자산관리사 → 트레이딩 데스크 데이터 접근 불가
  - 양방향 격리 강제
- **파인튜닝 여부는 공개되지 않음** (대부분 RAG 위주로 추정)
- 현재 **AWS Bedrock도 파인튜닝 모델 접근용으로 탐색 중** (CIO 인터뷰 언급)

`[Self-Reported]` · 출처: The Data Letter, CIO.com

#### 6.4 Evals Harness

- **"Golden dataset"** 방식 채택 — 큐레이션된 Q&A 쌍 세트로 각 모델 업데이트 평가
- **카나리 배포** (5~10% 프로덕션 트래픽)로 실제 사용 패턴 검증 후 전체 롤아웃
- 토큰 소비량을 **사람·부서·애플리케이션 단위로 모니터링** → 월간 비즈니스 단위 재무 보고에 활용 (cost attribution)

`[Self-Reported]`

#### 6.5 거버넌스 도구 / Red Team / 안전 검토

**Firmwide CDO 산하 AI Model Risk Management Framework** (2024 도입):

| 거버넌스 요소 | 설명 |
|--------------|------|
| **규제 정렬** | EU AI Act + NIST AI RMF + 내부 기준 |
| **통합 검토** | 법무·컴플라이언스·사이버보안·데이터 윤리 팀이 모든 AI 이니셔티브에 통합 |
| **기술 가드레일** | RAG 패턴 + 역할 기반 접근제어 + 프롬프트 인젝션·데이터 누출·아웃풋 필터 |
| **3대 의무** | 설명 가능성(explainability)·감사 가능성(auditability)·추적 가능성(traceability) |
| **스테이지별 검증** | 각 스테이지(개발·테스트·배포)별 모델 리스크·컴플라이언스·보안 계측 |
| **Red Team** | 존재 언급은 있으나 구체 절차 미공개 |

`[Self-Reported]` · 출처: gend.co, "Leveraging AI for Strategic Data Insights at JPMorgan" — https://www.gend.co/blog/leveraging-ai-strategic-data-insights-jpmorgan `[Analyst]`

#### 6.6 데이터 거버넌스 (규제 준수)

- **Firmwide CDO 산하 데이터 품질 기준 + 접근 패턴 관리**
- **투자 뱅킹 ↔ 소매 뱅킹 데이터 완전 격리** (Chinese Wall 강제)
- SEC·연준 등 금융 규제 프레임워크와 정렬
- "**고객 데이터 보호는 항상 1순위**" (CEO Jamie Dimon 인용)
- AI 유스케이스 전에 **데이터 준비도(data readiness) 우선 확인 원칙**

`[Self-Reported]`

#### 6.7 조직 변화 — 백엔드 엔지니어 관점

**기존 구조 내 역할 강화 방식** (신설 부서 없음):

| 역할 | 규모 |
|------|------|
| 데이터 사이언티스트 (SageMaker) | 5,000명 |
| LLM Suite 사용자 (전 직군) | 200,000명+ |
| AI Platform Team 신설 | ❌ 명시 없음 |

**거버넌스 트라이앵글**: Firmwide CDO + CIO (Lori Beer) + CAO (Derek Waldron) — 중앙 조율. 별도 AI 부서 신설 대신 **기존 조직의 AI 역량 강화 전략**.

> 💡 **백엔드 엔지니어 관점 인사이트**:
> - "외부 LLM API + 내부 RAG + 권한 필터링 + Evals + Governance"의 5-레이어 구조가 대규모 금융 표준 패턴
> - **데이터 readiness가 AI 유스케이스의 선행 조건** — 데이터 카탈로그·접근제어·품질 게이트가 AI 도입의 첫 작업
> - **벤더 락인 회피**를 명시적 설계 목표로 → 추상화 레이어(adapter pattern)로 모델 교체 가능
> - Cost attribution을 위한 토큰 모니터링 → AI 비용을 부서·앱 단위로 추적하는 게 운영 표준

---

## 2. Maersk AI 물류 (5요소 + 임팩트 1줄, 카테고리 (b) primary)

### (1) 출발점·문제정의

세계 최대 컨테이너 해운사 Maersk는 선박 450척 이상, 130개국 100,000+ 고객, 연간 3B 건 이상 비즈니스 이벤트를 처리하는 초복잡 물류 네트워크를 보유. 두 가지 핵심 문제:
- **선박 예상치 못한 고장**: 가동 중단 비용 + 탄소 배출
- **"unhappy flow"**: 전체 주문의 80~90%가 예외 처리(problem-solving)로 흘러 운영자 분석 시간 잠식

전통 AI/ML 실험에서 GenAI로 급속 전환을 2023~2024년에 단행. `[Self-Reported]`

- 출처: Deloitte, "Digital Transformation Reshapes Maersk" — https://www.deloitte.com/dk/en/services/consulting/perspectives/digital-transformation-reshapes-maersk-from-shipping-giant-to-global-logistics-integrator.html `[Independently-Audited]`

### (2) 핵심 결정

- CFO **Patrick Jany**가 "**여러 개의 소규모 실용적 구현**"을 단일 솔루션 탐색보다 우선하는 전략 원칙 공식화
- ELT(Executive Leadership Team) 분기 기술 리뷰 + **"Gemba walk"**(현장 직접 관찰) 방식
- 구체 AI 예산은 미공개
- 13개 물류 오퍼링 전반에 걸친 조율된 자원 배분이 핵심 거버넌스 과제

`[Self-Reported]` · 출처: Deloitte (위 URL)

### (3) 실행 프로세스 — 3-Phase

| Phase | 내용 | 상태 |
|-------|------|------|
| **1** | 인수 기업 레거시 시스템 통합, 단일 디지털 플랫폼 구축 | 완료 |
| **2** | 130개국 고객 서비스 전반에 AI 역량 배포 | 진행 중 |
| **3** | 통합 고객 경험 스케일 | 시작 |

**Maersk Tankers 사례** (외부 용역 — 독립 자료):
- 시니어 데이터 사이언티스트 3명 + 풀스택 개발자 1명, 6개월 sprint
- **의사결정 속도 3일 → 8시간 단축**을 파일럿 성공 지표로 확인 후 확장

`[Self-Reported + Third-Party Independent]` · 출처: devsdata.com, "Maersk Tankers AI Data Science" — https://devsdata.com/case-studies/ai-data-science-maersk-tankers-maritime-logistics/

### (4) 측정 결과

| 지표 | 수치 | 출처 | 회색지대 라벨 |
|------|------|------|---------------|
| 예측 유지보수 선박 가동 중단 감소 | 30% | 업계 분석 집계 | `[Self-Reported]` (집계) |
| 연간 비용 절감 | $300M+ | 업계 분석 | `[Self-Reported]` |
| 탄소 배출 감소 | 연 1.5M 톤 | 업계 분석 | `[Self-Reported]` |
| 항로 최적화 연료 절감 | 5~10%/항해 | 업계 분석 | `[Self-Reported]` |
| 의사결정 속도 | 3일 → 8시간 | devsdata.com | `[Independently-Audited]` (제3자) |
| AI 고객 서비스 처리 | 수천 건/일 | Deloitte 분석 | `[Independently-Audited]` |
| 시장 적응 시간 | 수개월 → 수주 | Maersk 공식 | `[Self-Reported]` |
| SAP 마이그레이션 | 500대 서버, petabyte, 6개월 | Microsoft 사례연구 | `[Self-Reported]` (vendor) |

> ⚠️ **$300M 절감 수치 주의**: 다수 분석 사이트에서 동일하게 인용되지만 **Maersk 공식 IR이나 독립 감사를 통해 직접 확인된 수치가 아님**. `[Uncertain — convergent but Self-Reported origin]`. 사례 활용 시 출처 명시 필수.

### (5) 실패·재조정

- **"unhappy flow" 문제가 대표적 설계 실패**: 전통 자동화 시스템이 예외 케이스를 처리하지 못해 운영자 부담이 오히려 증가
- 해결책: "**real-world 프로세스를 반영하는 시스템 설계**"로 전환
- **마스터 데이터 품질과 프로세스 분석**을 AI 도입 이전 선행 조건으로 명시
- **13개 사업 단위 간 데이터 의미론 불일치**와 조직 소유권 파편화가 파일럿 → 스케일 전환의 주요 장벽

`[Self-Reported + Independent: Deloitte 분석]`

### (6) 엔지니어링 임팩트 (요약)

Azure 기반 SAP 플랫폼 (500서버 petabyte 6개월) + Microsoft Azure AI 항로 최적화 + **LSTM/RandomForest 시계열 예측 모델** (엔진 고장 30일 전 예측, 85~95% 정확도) + OneWireless IoT 플랫폼 + ZEDEDA 엣지 컴퓨팅 + Plotly Dash/Power BI/Looker 시각화. GenAI 스택은 Azure OpenAI 기반 추정이나 공식 확인 미완료 `[Uncertain]`.

---

## 3. Siemens Industrial Copilot (5요소 + 임팩트 1줄, 카테고리 (c) primary, secondary (b))

### (1) 출발점·문제정의

Siemens Digital Industries (직원 70,000명)는 제조 자동화 SW 시장에서 **기술 숙련 인력 부족 구조적 위기**에 직면. PLC(Programmable Logic Controller) 코드 작성, TIA Portal 프로젝트 구성, 기계 시각화 생성 등 반복적이지만 전문 지식이 필요한 엔지니어링 작업이 인력 병목. 고객사(제조 기업) 역시 동일 문제로 Siemens 플랫폼 도입 주저. `[Self-Reported]`

- 출처: Siemens 공식 프레스 릴리즈 (Hermes Award 2025) — https://press.siemens.com/global/en/pressrelease/bringing-generative-ai-industry-siemens-industrial-copilot-wins-hermes-award-2025

### (2) 핵심 결정

- Siemens Digital Industries CEO **Cedrik Neike** + Factory Automation CEO **Rainer Brehm** 공동 주도
- **Microsoft와 전략적 파트너십** (Azure OpenAI Service 기반)
- **Siemens Xcelerator 오픈 플랫폼**에 통합하여 고객 접근성 확보
- **데이터 주권(data sovereignty) 보장**을 명시적 설계 원칙 → 민감 산업 고객을 위한 **온프레미스 배포 옵션** (SIMATIC IPC 1047E + NVIDIA AI Enterprise)

`[Self-Reported]` · 출처: Microsoft Source, "Siemens and Microsoft Scale Industrial AI" — https://news.microsoft.com/source/2024/10/24/siemens-and-microsoft-scale-industrial-ai/

### (3) 실행 프로세스

- **2024-07 정식 출시 전**: 고객 인터뷰 → 파일럿 단계 지속적 피드백 수집 반복 방법론
- **Siemens 자체 Erlangen 전자 공장에서 내부 도그푸딩** (납땜 기계 에러 코드 자연어 번역·해결책 제시)
- 이후 **Schaeffler, thyssenkrupp Automation Engineering 등 100개+ 고객사로 확장**
- **thyssenkrupp**: 2025년 초부터 **전 제품 라인 글로벌 롤아웃**
- **2025 Hannover Messe** 에서 **Hermes Award 수상**으로 업계 공신력 확보

`[Self-Reported + Independently-Audited]` · 출처: Microsoft Source EMEA, "How AI Is Helping Siemens and thyssenkrupp Bridge Skilling Gaps" — https://news.microsoft.com/source/emea/features/how-ai-is-helping-siemens-and-thyssenkrupp-bridge-skilling-gaps-in-manufacturing/

### (4) 측정 결과

| 지표 | 수치 | 출처 | 회색지대 라벨 |
|------|------|------|---------------|
| 패널 시각화 생성 시간 | 30초 (이전 수 시간) | Siemens/MS 공동 발표 | `[Self-Reported]` |
| PLC 코드 수동 수정 비율 | 20% (나머지 자동 생성) | Siemens/MS 공동 발표 | `[Self-Reported]` |
| 고객 수 (2024년 말 기준) | 100개+ 기업 | Siemens 공식 | `[Self-Reported]` |
| 접근 가능 엔지니어링 SW 사용자 | 120,000명 | Siemens/MS 공동 발표 | `[Self-Reported]` |
| 기계 가동 중단 감소 | "dramatic" | Erlangen 공장 사례 | `[Self-Reported]` (수치 미공개) |

> ⚠️ Siemens 공식 자료에 **독립 감사 수치 없음**. 모든 수치 `[Self-Reported]`. 회색지대 부록표 케이스 1 (공저 PR).

### (5) 실패·재조정

공개된 실패 사례 없음. 단, 고객 피드백 수집 과정에서:
- **"데이터 민감 도메인" 고객 일부가 파인튜닝을 위한 데이터 제공 거부**
- 이를 수용하여 **RAG 기반(파인튜닝 없는) 경로** + **온프레미스 배포 경로**를 병행 제공하는 유연한 아키텍처로 재설계

이것이 유일하게 확인된 조정. `[Self-Reported]`

- 출처: Siemens 블로그 팟캐스트 트랜스크립트 — https://blogs.sw.siemens.com/thought-leadership/going-beyond-automation-with-the-industrial-copilot-part-2-transcript/

### (6) 엔지니어링 임팩트 (요약)

**Microsoft Azure OpenAI Service 기반 클라우드 경로** + **SIMATIC IPC 1047E + NVIDIA AI Enterprise 기반 온프레미스 경로** 이중화. Siemens TIA Portal 네이티브 통합으로 SCL 코드 자동 생성 → 즉시 PLC에 주입. 데이터 주권 요구 고객은 인터넷 연결 없이 공장 내 로컬 처리. **RAG 접근법으로 도메인 데이터 없이도 빠른 가치 제공** — 파인튜닝 회피 전략. `[Self-Reported]`

> 💡 **카테고리 secondary (b) 표기 이유**: Siemens는 자체 도메인 IP(TIA Portal, PLC 생태계)는 (c) 인하우스이지만, LLM 자체는 Azure OpenAI에 의존 → hybrid. plan v3 카테고리 hybrid 허용 규칙에 따라 primary (c), secondary (b)로 표기.

---

## 4. Microsoft Copilot 사내 전환 (5요소 + 임팩트 1줄, 카테고리 (a) — 선택 추가)

### (1) 출발점·문제정의

Microsoft는 "**세계 최초 대규모 글로벌 기업으로서 AI를 전사 스케일에 적용**"이라는 자기 정의 아래, M365 Copilot의 내부 배포를 **제품 신뢰성 입증 + 실사용 데이터 수집** 이중 목적으로 추진. `[Self-Reported]`

### (2) 핵심 결정

- **엔지니어·지원팀·전략 직군** 얼리 어답터 프로그램 → 법무·HR·마케팅·세일즈 순차 확장
- **역할 기반(role-based) 스킬링 활동** + Microsoft Viva를 통한 사용량·NSAT 집계

`[Self-Reported]`

### (3) 실행 프로세스

- **월간 활성 사용률 90%+ 유지**
- **Power Hour 세션**, Get Engaged 워크숍, 다국어 지원
- **Bowler scorecard 방식 월간 운영 리뷰** (6개 측정 영역: 매출·생산성·보안·직원 경험·품질·비용)

`[Self-Reported]` · 출처: Microsoft InsideTrack — https://www.microsoft.com/insidetrack/blog/measuring-the-impact-of-microsoft-365-copilot-and-ai-at-microsoft/

### (4) 측정 결과

| 지표 | 수치 | 출처 | 회색지대 라벨 |
|------|------|------|---------------|
| 내부 세일즈 매출/판매자 증가 | 9.4% | Microsoft InsideTrack | `[Self-Reported]` |
| 고사용자 성약률 증가 | 20% | Microsoft InsideTrack | `[Self-Reported]` |
| 포춘 500 기업 Copilot 사용 비율 | 60% | Electroiq 통계 집계 | `[Self-Reported]` (분석가 집계) |
| 생산성 향상 (특정 작업) | 최대 70% | 외부 연구 인용 | `[Independently-Audited]` 부분 포함 |
| 소통 명확성 개선 보고 직원 | 62% | 외부 연구 | `[Self-Reported]` |

### (5) 실패·재조정

- 초기 **Copilot 경험이 "아직 기초적(basic)"** 이었다고 내부 인정
- 구체 실패 사례 공개 없음

`[Self-Reported]`

### (6) 엔지니어링 임팩트 (요약)

**M365 생태계** (Teams, Word, Excel, Outlook) **네이티브 통합** + **GitHub Copilot 별도 경로** (코드 품질·보안 주요 지표). 내부 측정은 Microsoft Viva 집계 데이터로 수행. 카테고리 (a) 벤더 자기 도그푸딩 특성상 **내부 API 접근권·무제한 컴퓨팅·도구-제품 일치성**의 특수 조건 — 일반 기업 적용성은 제한적. `[Self-Reported]`

---

## 5. 카테고리 패턴 일관성 평가 (Task 4 framework induced 패턴 후보)

본 노트의 4개 사례를 카테고리 (b)/(c)/(a)로 분리한 결과 **induced 패턴 5건**을 추출했다. 이는 Task 4의 6단계 프레임워크 작성 시 *induced 사례 ID 또는 imported URL 의무* 규칙에 따라 활용한다.

### Induced Pattern 1: "외부 LLM + 내재화 플랫폼" 하이브리드 아키텍처

- **사례**: JPMorgan (OpenAI/Anthropic 외부 + Azure/Snowflake/AWS 내재화 플랫폼)
- **일반화**: 대규모 금융·엔터프라이즈는 단순 SaaS 구독이 아닌 **5-레이어 구조** (외부 LLM + 추상화 어댑터 + RAG + 권한 필터 + 거버넌스)로 수렴
- **Task 4 활용**: 6단계 ⑤ 스케일링 단계의 표준 아키텍처 참조

### Induced Pattern 2: "도메인 IP는 자체, 모델 컴퓨팅은 외부" Hybrid(c)

- **사례**: Siemens (TIA Portal 자체 + Azure OpenAI 외부) → primary (c), secondary (b)
- **일반화**: 제조업 AI는 도메인 지식 자체가 핵심 자산. LLM 자체보다 **도메인 통합·접근제어**가 차별화 포인트
- **Task 4 활용**: 카테고리 (c) 인하우스 역량은 "모델 self-build"보다 "도메인 IP self-build + 모델 외부"가 현실적

### Induced Pattern 3: Pilot의 "Happy Path 편향"

- **사례**:
  - Maersk: "unhappy flow" 80~90% 예외 케이스 미처리
  - Siemens: 데이터 민감 고객 거부 → 온프레미스 경로 추가
  - JPMorgan: 프론트오피스 규제 우회로 후행 배포
- **일반화**: 파일럿은 Happy path 위주로 설계 → 이례 케이스가 scale-up 장벽
- **Task 4 활용**: 6단계 ④ 파일럿 실행 단계에 **"예외 케이스 사전 카탈로그"** 의무화 필요

### Induced Pattern 4: 측정 가능성의 카테고리 격차

- **사례**:
  - (b) 외부 도입: JPMorgan 주 3~6시간/인 + Maersk 30% 가동 중단 감소 등 **시간·비용 정량 KPI 적극 공개**
  - (c) 인하우스 구축: Siemens "30초 시각화 생성"은 일부 정량, "dramatic" 가동 중단 감소는 정성적
- **일반화**: 인하우스 구축 기업은 **"기술 역량 내재화" 지표** (생산성 대신 차별화 시간)가 더 적합
- **Task 4 활용**: 6단계 ⑥ 측정·KPI를 카테고리별로 분리 — (b)는 ROI 중심, (c)는 역량 내재화 중심

### Induced Pattern 5: 거버넌스 성숙도 ∝ 규제 강도

- **사례**:
  - 금융 (JPMorgan): Firmwide AI Model Risk Framework + EU AI Act/NIST 정렬 + 3대 의무 (explainability·auditability·traceability)
  - 제조 (Siemens): Hermes Award 수상 수준 거버넌스, 단 명문화된 framework 공개 적음
  - 물류 (Maersk): 거버넌스 정보 공개 미흡 — Gemba walk 같은 비공식 메커니즘 위주
- **일반화**: **규제 환경이 AI 거버넌스 성숙도를 강제하는 핵심 변수**
- **Task 4 활용**: 6단계 ④ 파일럿 거버넌스 sub-bullet에 **규제 환경별 권장 가버넌스 수준** 분기 제시

---

## 6. 회색지대 분류 부록표 (재참조)

본 노트의 모든 측정 수치는 `[[01-ax-concept-vs-dx#6-회색지대-분류-부록표-8-케이스]]` 의 8 케이스 분류를 따른다. 핵심 적용 결과:

| 회색지대 적용 사례 | 분류 |
|---------------|------|
| Siemens/Microsoft **공동 발표** (Microsoft Source 기사) | `[Self-Reported]` (케이스 1) |
| Tearsheet **자체 인터뷰** (JPMorgan 임원) | `[Independently-Audited]` (케이스 8) |
| Deloitte **독립 분석** (Maersk 디지털 전환) | `[Independently-Audited]` (케이스 6) |
| **The Data Letter** (vendor 비공개 데이터 기반 분석가 리포트) | `[Self-Reported]` (케이스 2) |
| **Microsoft 고객 스토리** (Maersk SAP) | `[Self-Reported]` (케이스 1 — vendor 발신) |
| devsdata.com **제3자 외주팀 보고** (Maersk Tankers) | `[Independently-Audited]` 에 준함 (케이스 8과 유사) |
| **CIO.com 자체 취재** (JPMorgan AWS 인프라) | `[Independently-Audited]` (케이스 8) |

---

## 출처 (Sources)

| 라벨 | 출처 |
|------|------|
| `[Independently-Audited]` | Tearsheet, "JPMorgan Chase's GenAI Implementation: 450 Use Cases and Lessons Learned". https://tearsheet.co/artificial-intelligence/jpmorgan-chases-gen-ai-implementation-450-use-cases-and-lessons-learned/ |
| `[Independently-Audited]` | CIO.com, "JPMorgan Chase Builds Ambitious AI Foundation on AWS". https://www.cio.com/article/3616622/jpmorgan-chase-builds-ambitious-ai-foundation-on-aws.html |
| `[Independently-Audited]` | Deloitte, "Digital Transformation Reshapes Maersk". https://www.deloitte.com/dk/en/services/consulting/perspectives/digital-transformation-reshapes-maersk-from-shipping-giant-to-global-logistics-integrator.html |
| `[Independently-Audited]` | Automation World, "thyssenkrupp Adopts Siemens Industrial Copilot". https://www.automationworld.com/factory/digital-transformation/news/55248289/thyssenkrupp-adopts-siemens-industrial-copilot |
| `[Self-Reported]` | JPMorgan Chase 공식 블로그, "LLM Suite AB Award". https://www.jpmorganchase.com/about/technology/blog/llmsuite-ab-award |
| `[Self-Reported]` (Analyst) | The Data Letter, "AI Infrastructure Engineering Driving JPMorgan". https://www.thedataletter.com/p/ai-infrastructure-engineering-driving |
| `[Self-Reported]` (Analyst) | gend.co, "Leveraging AI for Strategic Data Insights at JPMorgan". https://www.gend.co/blog/leveraging-ai-strategic-data-insights-jpmorgan |
| `[Self-Reported]` (Joint PR) | Microsoft Source, "Siemens and Microsoft Scale Industrial AI" (2024-10-24). https://news.microsoft.com/source/2024/10/24/siemens-and-microsoft-scale-industrial-ai/ |
| `[Self-Reported]` | Siemens 공식 프레스, "Bringing Generative AI to Industry — Hermes Award 2025". https://press.siemens.com/global/en/pressrelease/bringing-generative-ai-industry-siemens-industrial-copilot-wins-hermes-award-2025 |
| `[Self-Reported]` | Siemens 블로그 트랜스크립트, "Going Beyond Automation with the Industrial Copilot Part 2". https://blogs.sw.siemens.com/thought-leadership/going-beyond-automation-with-the-industrial-copilot-part-2-transcript/ |
| `[Self-Reported]` (Vendor) | Microsoft 고객 스토리, "Maersk SAP on Azure". https://www.microsoft.com/en/customers/story/26271-maersk-sap-on-azure |
| `[Third-Party Independent]` | devsdata.com, "Maersk Tankers AI Data Science Case Study". https://devsdata.com/case-studies/ai-data-science-maersk-tankers-maritime-logistics/ |
| `[Self-Reported]` | Microsoft InsideTrack, "Measuring the Impact of Microsoft 365 Copilot". https://www.microsoft.com/insidetrack/blog/measuring-the-impact-of-microsoft-365-copilot-and-ai-at-microsoft/ |
| `[Self-Reported]` | Microsoft Source EMEA, "How AI is Helping Siemens and thyssenkrupp Bridge Skilling Gaps". https://news.microsoft.com/source/emea/features/how-ai-is-helping-siemens-and-thyssenkrupp-bridge-skilling-gaps-in-manufacturing/ |

**구조적 적대적 출처 충족 여부**: ✅ 4건 `[Independently-Audited]` (저널리즘 자체취재 + 컨설팅 독립 분석) — 노트당 1건+ 의무 충족.

---

> 🔖 다음 노트: `[[03-ax-process-framework]]` — 본 사례 4개에서 도출한 **induced 패턴 5건**과 컨설팅 문헌 imported 단계를 결합하여 **6단계 framework**을 합성. 백엔드 엔지니어 관점 횡단 부록 포함.
