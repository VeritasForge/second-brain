---
tags: [ax, case-study, playbook, biotech]
created: 2026-06-02
company: Moderna
category: 바이오테크 · AI-first 문화 전환
valid_until: 2027-Q2
---

# Moderna AX Playbook — HR과 IT를 합친 AI-first 조직

> 📅 작성일 2026-06-02 · 측정치·동향은 시점 의존적, 6~12개월 후 재검토 권장
> 🔖 AX 실천 Playbook 시리즈 · [[00-ax-practice-guide]]

---

## 0. Executive Summary

Moderna는 mRNA 플랫폼 기반 바이오테크 기업(직원 약 5,800명, 2025년 매출 약 30억 달러)으로, 2021년부터 조직 전체를 체계적으로 AI-first 기업으로 전환한 사례다. 핵심 구조는 세 층위로 요약된다.

**기술 레이어**: 10년 AWS 단일 클라우드 선행 → 2023년 자체 챗봇 mChat 2주 내 개발 → 2024년 ChatGPT Enterprise 전사 도입 → 2개월 내 750+ 맞춤 GPT 배포.

**조직 레이어**: 2025년 2월 CIO Brad Miller 퇴임 후 HR과 IT를 "People & Digital Technology" 단일 부서로 통합. Chief People and Digital Technology Officer (CPDTO) Tracey Franklin이 3,000+ AI 에이전트와 5,800명 인력을 단일 보고체계로 관리.

**문화 레이어**: CEO Stéphane Bancel의 "6개월 내 전 직원 AI 채택·숙련도 100%" 공개 목표 → AI 챔피언 네트워크(100명) → 주 2,000명 규모 슬랙 AI 포럼 → 6트랙 AI 아카데미.

주의: 생산성 수치(하루 40~60분 절감 등)는 Moderna·OpenAI 자체 보고 기반이며 제3자 감사 없음. AI 채택이 신약 개발 가속화 등 실제 사업 성과로 이어졌다는 인과는 현재 미입증 상태 ``[Uncertain]`` (재무 수치 공개, 인과관계 미입증).

---

## 1. 출발점 — 왜 AX를 시작했나

### 1-1. 조직 맥락

| 항목 | 내용 |
|------|------|
| 창립 | 2010년 |
| 직원 수 | 2019년 800명 → 2025년 5,800명 (+625%) |
| 본사 | 케임브리지, 매사추세츠 |
| 핵심 사업 | mRNA 플랫폼 기반 백신·치료제 |
| 재무 맥락 | 2024년 매출 약 30억 달러(코로나 특수 종료 후 급감) |

Moderna는 COVID-19 이전부터 "디지털 우선, 데이터 기반" 철학을 표방했다. 백신 특수로 급성장했으나 2023~2024년 수요 급감으로 비용 절감 압박이 커졌고, 이는 AI로 소수 인력이 대규모 조직처럼 성과를 내야 한다는 실존적 필요를 만들었다.

### 1-2. 전략적 동인

**레버리지 필요성**: CEO Bancel은 "수천 명으로 10만 명의 성과를 내야 한다"고 공개 천명. 자원 제약이 전사 AI 채택을 선택이 아닌 생존 조건으로 만들었다 ``[Self-Reported]`` (기업 발표).

**기술 부채 부재**: 경쟁사 대부분이 레거시 인프라와 씨름하는 동안, Moderna는 창사 초기부터 AWS 단일 클라우드를 선택해 10년간 데이터 거버넌스를 성숙시켰다. 이 선행 투자가 AI 도구를 14일 만에 배포하는 속도를 가능하게 했다 ``[Self-Reported]`` (기업 발표).

**규제 환경 인식**: 임상시험 데이터와 FDA 대응 등 고위험 프로세스에 AI를 적용하는 거버넌스 미비는 규제 리스크로 직결된다. Moderna가 GPT 거버넌스를 신중하게 설계한 이유다.

---

## 2. 타임라인 — 어떻게 수행했나

| 시기 | 이벤트 | 핵심 수치·세부 |
|------|--------|--------------|
| 2010년 | Moderna 창립 | AWS 단일 클라우드 철학 도입 |
| 2019년 | 전사 클라우드 표준화 완료 | 멀티클라우드 시도 중단, AWS 단일 베팅 결정 |
| 2021년 12월 | **AI Academy 출범** | Carnegie Mellon University (CMU) 파트너십, 전 직원 AI 기초 교육 의무화 |
| 2022년 초 | AI Academy 1기 교육 시작 | 90분 단기강좌·주간 세미나·다주간 인증 트랙 3종 제공 |
| 2023년 초 | **mChat 개발·배포** | CIO Brad Miller + AI 엔지니어링 책임자 Andrew Giessel, OpenAI API 기반 알파 개발 → 보안 검토 완료 후 전사 배포 (알파~전사 배포: 약 6주) |
| 2023년 | AI Academy 기업 내재화 | CMU 외부 의존 탈피, 6트랙 맞춤 교육 체계로 재설계; mChat 채택률 80% ``[Self-Reported]`` (기업 발표) |
| 2023년 11월 | Moderna 디지털 인베스터 데이 | AI 전략 투자자 공개 설명, Brice Challamel 등 AI 리더십 소개 |
| 2024년 초 | **ChatGPT Enterprise 전사 배포** | mChat·Copilot·ChatGPT Enterprise 비교 평가 후 OpenAI 선택(NPS 우위); ChatGPT Enterprise는 기업 데이터를 OpenAI 학습에 사용 불가 |
| 2024년 (2개월 내) | **750+ GPT 배포** | 초기 500명 온보딩 사용자가 700+ 맞춤 GPT 생성; 법무·연구·제조·상업 전 부문 임베딩 |
| 2024년 4월 | OpenAI 파트너십 공식 확대 | mRNA 연구 가속화 목적 협업 발표 |
| 2024년 | LinkedIn 'Top Companies' 9위 | AI 인력 적응 기준 평가 ``[Independently-Audited]`` (LinkedIn 공식 순위) |
| 2024년 말~2025년 초 | **HR·IT 통합 시작** | Brad Miller CIO 퇴임 검토 |
| 2025년 2월 | **Brad Miller CIO 퇴임** | Tracey Franklin이 IT 책임 흡수, CPDTO 직책 신설 |
| 2025년 중 | 디지털팀 10% 감축 | 약 50명 감원, "digital for business"·"digital core" 기능 재편 |
| 2025년 말 기준 | GPT 3,000+ 운영 | People & Digital Technology 부서가 3,000 AI + 5,800인 통합 관리 |
| 2025년 1월 | **HBS 케이스 625-070 출판** | "Democratizing Artificial Intelligence", Bojinov·Lakhani 외 저술 |

> 출처: OpenAI case study, Fortune (2024.04, 2024.03, 2025.05), Fierce Pharma, CIO.com, UNLEASH, IntuitionLabs ``[Self-Reported]`` (기업 발표) / LinkedIn Top Companies ``[Independently-Audited]`` (LinkedIn 공식 순위)

---

## 3. 조직 변화 — 신설 부서·역할·보고체계

### 3-1. 통합 이전 구조 (2023~2025년 초)

```
CEO Stéphane Bancel
├── CIO Brad Miller          ─── IT·디지털 인프라
│   └── VP AI Products & Platforms: Brice Challamel
│       └── Head of AI Engineering: Andrew Giessel
└── CHRO Tracey Franklin     ─── HR·인재 관리
```

### 3-2. 통합 이후 구조 (2025년 2월~)

```
CEO Stéphane Bancel
└── Chief People & Digital Technology Officer (CPDTO): Tracey Franklin
    ├── People (HR) 기능      ─── 인재·문화·보상·온보딩
    ├── Digital Technology    ─── 인프라·엔지니어링·AI 플랫폼
    └── AI 거버넌스 통합       ─── 3,000+ GPT 관리 + 5,800명 인력
```

### 3-3. 핵심 인물 프로필

**Tracey Franklin (CPDTO)**
- 2019년 Moderna 합류 (당시 직원 800명)
- Merck & Co. 15년 경력: VP HR Chief Talent & Strategy Officer
- 통합 철학: "나는 workforce planning에서 work planning으로 이동했다" — 역할 단위가 아닌 흐름(work flow) 단위로 인간·AI 배치를 설계
- 특기: AI를 활용한 경영진 갈등 예측 모델(GPT로 경영진 성격 프로파일 구성 후 시나리오 시뮬레이션)

**Brice Challamel (전 VP AI Products & Platforms)**
- Moderna 재직 중 ChatGPT Enterprise 도입 설계·실행 주도
- HBS MBA 케이스 및 저서 "AI First: The Playbook for a Future-Proof Business and Brand" 소재
- 2026년 초 OpenAI로 이직, Head of AI Strategy and Adoption 역임 → 핵심 인물의 이탈 리스크 실증

**Brad Miller (전 CIO, 2023~2025년 초)**
- Amazon·Microsoft·Capital One·Mastercard 출신 엔지니어링 원칙 적용
- AWS 단일 클라우드 표준화, mChat 개발 진두지휘
- 2025년 2월 퇴임 → HR+IT 통합의 직접 계기

### 3-4. 통합 의사결정 배경

CIO.com 분석가 Ken Knapton 박사에 따르면 Moderna의 HR·IT 통합은 "대담하고 전례 없는" 결정이나 업계 전반 트렌드는 아님. 성공 조건은 Tracey Franklin이 HR 전문성과 디지털 전환 이해를 동시에 보유한 비전형적 CHRO라는 사실 `[Independently-Audited: CIO.com 독립 분석]`.

통합 배경의 공식적 논리: "인간과 기계 중 누가 각 태스크를 수행해야 최선의 결과를 내는가?"를 단일 리더십이 결정할 수 있어야 한다. 분리된 HR·IT 체계에서는 이 질문 자체를 조직적으로 소유하는 주체가 없다.

---

## 4. 의사결정·거버넌스 — GPT 생성·관리 프로세스

### 4-1. GPT 생성 파이프라인

Moderna는 "민주화(democratize)"와 "거버넌스" 사이의 긴장을 핵심 운영 과제로 인식한다 (HBS 케이스 625-070의 핵심 논제).

**GPT 생성 흐름 (추론 가능한 운영 방식):**

```
아이디어 → AI 챔피언 검토 → 보안·콘텐츠 필터 설정 →
Human-in-the-loop 검증 (임상 관련) → 전사 배포 → 사용 모니터링
```

**임상 관련 GPT 특별 요건:**
- Dose ID GPT: AI 출력물은 임상팀의 인간 주도 검토를 위한 입력으로만 사용, AI가 직접 의사결정하지 않음
- 규제 기관 통보 여부는 2025년 기준 여전히 미결 상태 (HBS 케이스가 이를 열린 질문으로 제시)

**데이터 보안 기반:**
- ChatGPT Enterprise: 기업 데이터를 OpenAI 학습에 활용하지 않음 계약 체결
- HIPAA Business Associate Agreement 이행
- SSO(Single Sign-On) + 감사 로그
- 콘텐츠 필터 + 민감 GPT 대상 검토위원회

### 4-2. 거버넌스 긴장 구조 (HBS 케이스 핵심 논제)

| 민주화 모델 | 중앙화 모델 |
|------------|------------|
| 혁신 속도 최대화 | 위험 통제 강화 |
| 40% 사용자가 직접 GPT 생성 | 전문 팀만 GPT 생성 |
| 부서별 자율성 | 일관성·규정 준수 |
| 환각(hallucination) 리스크 분산 | 규제 리스크 집중 관리 |

**Moderna의 실제 선택**: 현재까지 민주화 모델 유지. 단, 임상·규제 관련 GPT는 Human-in-the-loop 강제화로 절충.

### 4-3. AI 챔피언 네트워크 (거버넌스 인프라)

- 발굴 방식: 전사 AI 프롬프트 콘테스트에서 상위 100명 선발
- 기능: 부서별 AI 복음 전파자 (evangelists) + GPT 품질 검토 1차 게이트
- 지원 구조: 부서별 AI 오피스 아워(office hours) + 월간 AI 앰배서더 쇼케이스

---

## 5. 실행 디테일 — 기술 스택·도구·롤아웃

### 5-1. 기술 스택

| 레이어 | 기술·도구 | 역할 |
|--------|---------|------|
| 클라우드 | AWS (단일 클라우드) | 인프라 기반, 10년 표준화 |
| AI 플랫폼 | ChatGPT Enterprise (OpenAI) | 전사 GenAI 허브 |
| 내부 챗봇 | mChat (OpenAI API 기반) | 초기 내부 인스턴스, 현재 ChatGPT Enterprise로 전환 중 |
| 데이터 플랫폼 | Best-of-breed + Data Mesh | AI 레디 데이터 아키텍처 |
| ML 학습 플랫폼 | Dataiku | AI Applied 교육 트랙에서 활용 |
| 연구 플랫폼 | Benchling (2025년 확장 파트너십) | 실험실 AI 통합 |
| 학습 플랫폼 | ISLE (CMU 개발 인터랙티브 교육 환경) | AI Academy 초기 사용 |
| 협업 | Slack | AI 포럼 (주 활성 사용자 2,000명) |

### 5-2. 부서별 GPT 사례

| 부서 | GPT 이름 | 기능 | 효과 |
|------|---------|------|------|
| 임상개발 | Dose ID | 임상시험 데이터 분석 → 최적 백신 용량 평가, 근거·차트 자동 생성 | 임상팀 검토 시간 단축 (수치 미공개) |
| 법무 | Contract Companion | 계약서 검토·핵심 조항 요약 | 계약 초안 작업 90~95% 시간 절감 ``[Self-Reported]`` (기업 발표) |
| 법무 | Policy Bot | HR·안전 정책 Q&A 자동화 | 법무팀 100% 채택 |
| 규제 | Regulator Response | FDA 대응 초안 작성 | 대응 시간: 수주 → 수분 (내부 주장) ``[Self-Reported]`` (기업 발표) |
| 커뮤니케이션 | Brand GPT | 바이오테크 전문용어를 투자자 언어로 변환 | 분기 실적 발표 등 활용 |
| HR | Ask HR | 성과·경력·복리후생 Q&A → 전문 리소스 라우팅 | 반복 문의 자동화 |
| HR | Benefits Assistant | 연간 복리후생 선택 안내 | 신입 온보딩 연계 |

### 5-3. ChatGPT Enterprise 롤아웃 방법론

1. **평가 단계**: mChat·Microsoft Copilot·ChatGPT Enterprise 3종 비교 (NPS 기준 ChatGPT Enterprise 우위)
2. **파일럿**: 초기 500명 온보딩
3. **확산**: GPT Kickstart Live 필수 교육 → 부서별 오피스 아워 → 챔피언 네트워크 지원
4. **측정**: 주간 활성 사용자·생성 GPT 수·부서별 채택률 추적 (CEO 직보)

### 5-4. AI Academy 6트랙 (2023년 재설계)

| 트랙 | 대상 | 내용 |
|------|------|------|
| AI Awareness | 전 직원 | AI 기초, 윤리 모듈 포함 |
| GPT Kickstart | ChatGPT 사용자 | 기본 활용법 |
| AI Applied | 중급자 | Dataiku 플랫폼 활용 |
| Data Visualization | 데이터 실무자 | 인사이트 추출·시각화 |
| AI Champions | 상위 100명 | GPT 개발·거버넌스 |
| AI for Leaders | 경영진 | 전략적 AI 활용 |

---

## 6. 측정 결과 — 어떻게 성공을 측정했나

### 6-1. 핵심 채택 지표 (측정 방법: ChatGPT Enterprise 플랫폼 내장 분석)

| 지표 | 수치 | 측정 시점 | 라벨 |
|------|------|----------|------|
| ChatGPT Enterprise 전사 채택률 | 80% (mChat 포함) | 2024년 배포 후 | ``[Self-Reported]`` (기업 발표) |
| 법무팀 채택률 | 100% | 2024년 | ``[Self-Reported]`` (기업 발표) |
| 사용자당 주간 대화 수 | 120회 | 2024년 평균 | ``[Self-Reported]`` (기업 발표) |
| GPT 생성 참여율 | 주간 활성 사용자의 40% | 2개월 내 | ``[Self-Reported]`` (기업 발표) |
| 배포된 맞춤 GPT 수 | 750+ (초기) → 3,000+ (2025년) | 단계별 | ``[Self-Reported]`` (기업 발표) |
| Slack AI 포럼 주간 참여자 | 약 2,000명 | 2024년 | ``[Self-Reported]`` (기업 발표) |

### 6-2. AI 교육 지표 (측정 방법: AI Academy 수료 기록 + NPS 설문)

| 지표 | 수치 | 라벨 |
|------|------|------|
| AI Academy 누적 등록 (20개월) | 2,000명+ | ``[Self-Reported]`` (기업 발표) |
| 총 학습 시간 | 14,700시간+ | ``[Self-Reported]`` (기업 발표) |
| 평균 지식 향상률 (교육 전후 비교) | 약 30% | ``[Self-Reported]`` (기업 발표) |
| 2023년 전사 참여율 | 25% | ``[Self-Reported]`` (기업 발표) |
| AI Academy NPS | 71 (50↑ = 긍정) | ``[Self-Reported]`` (기업 발표) |
| LinkedIn Top Companies AI 순위 | 9위 (2024년) | ``[Independently-Audited]`` (LinkedIn 공식 순위) |

### 6-3. 생산성·비용 주장 (측정 방법 미공개, 주의 요망)

| 주장 | 수치 | 라벨 |
|------|------|------|
| Enterprise GPT 사용자 일일 시간 절감 | 40~60분 | ``[Self-Reported]`` (기업 발표) — 측정 방법 미공개 |
| Contract Companion 계약 초안 시간 절감 | 90~95% | ``[Self-Reported]`` (기업 발표) — 단일 발화 인용 |
| 규제 대응 처리 시간 | 수주 → 수분 | ``[Self-Reported]`` (기업 발표) — 검증 불가 |

### 6-4. 비즈니스 성과와의 인과 (현재 미입증)

AI 채택이 mRNA 신약 개발 가속, 임상 성공률 향상, 매출 회복 등 실제 사업 성과로 이어졌다는 인과관계는 현재 공개된 자료에서 입증되지 않는다 ``[Uncertain]`` (재무 수치 공개, 인과관계 미입증).

- 2024년 매출: 약 30억 달러 (전년 대비 급감, 코로나 특수 종료 효과)
- 2025년 R&D 투자: 33~34억 달러 (매출보다 R&D가 더 큼)
- AI가 비용 절감과 파이프라인 가속에 기여했다는 주장: Moderna 자체 주장에 그침

> HBS 케이스(625-070)도 이 거버넌스 딜레마와 리스크를 중심으로 서술하며, AI 도입이 사업 성과로 직결된다는 전제를 검증 과제로 제시한다.

---

## 7. 핵심 실천 교훈 — 따라 할 수 있는 것

### 교훈 1: 클라우드 인프라가 먼저다

**Moderna 사례**: 10년 AWS 단일 클라우드 표준화 → mChat 14일 내 구동 가능.

**따라 할 것**: GenAI 도입 전 데이터 플랫폼·API 접근성·보안 거버넌스를 정비하라. 레거시 인프라 위의 GenAI는 속도가 10배 느리다.

**하지 말 것**: 인프라 미비 상태에서 "AI 우선 도입, 기반은 나중에" 방식으로 접근하지 말 것.

---

### 교훈 2: CEO가 측정 가능한 목표를 공개 선언해야 한다

**Moderna 사례**: Bancel의 "6개월 내 100% 채택·숙련도" 공개 목표 → 조직 전체가 AI를 선택지가 아닌 기본값으로 인식.

**따라 할 것**: AI 채택 목표를 수치·기한으로 공개 설정하고 CEO 직보 대시보드로 주간 추적하라.

**하지 말 것**: "AI를 장려합니다" 같은 방향 제시에 그치지 말 것. 측정 없는 목표는 문화를 바꾸지 못한다.

---

### 교훈 3: 단일 챗봇이 아닌 플랫폼을 배포하라

**Moderna 사례**: ChatGPT Enterprise를 "모든 사람이 GPT를 만드는 플랫폼"으로 포지셔닝. 2개월 내 750+, 2025년에는 3,000+ GPT.

**따라 할 것**: 도구를 배포하되, 사용자가 자신의 업무에 맞는 도구를 직접 만들 수 있는 환경을 제공하라 (플랫폼 사고).

**하지 말 것**: 중앙팀이 모든 GPT를 개발·승인하는 방식은 혁신을 병목화한다.

---

### 교훈 4: 교육은 단일 트랙이 아닌 역할별 커리큘럼으로

**Moderna 사례**: CMU 파트너십으로 시작한 단일 필수 과정 → "효과 없음" 발견 → 6트랙 맞춤 교육으로 재설계. NPS 50 이하 → 71로 개선.

**따라 할 것**: 교육 프로그램 초기 NPS를 측정하고, 역할(관리자/개발자/현업/경영진)별로 분리된 커리큘럼을 운영하라.

**하지 말 것**: AI 교육을 "비용 절감 수단"으로 프레이밍하지 말 것. Tracey Franklin은 이 접근이 직원 참여를 낮춘다고 명시적으로 경고했다.

---

### 교훈 5: 챔피언 네트워크가 바이럴 확산의 핵심이다

**Moderna 사례**: AI 프롬프트 콘테스트 → 상위 100명 식별 → 부서별 챔피언 배치 → 내부 슬랙 포럼 주 2,000명 활성화.

**따라 할 것**: 탑다운 의무화와 바텀업 챔피언 네트워크를 병행하라. 챔피언은 중앙 팀이 지명하는 것이 아니라 사용 데이터로 발굴하라.

---

### 교훈 6: HR+IT 통합은 전제 조건이 충족될 때만 시도하라

**Moderna 사례**: CHRO Tracey Franklin이 HR 전문성 + 디지털 이해를 동시 보유 → 통합이 가능. CIO.com 독립 분석가는 "대부분의 기업은 이 조건을 갖추지 못한다"고 평가.

**따라 할 것**: HR 리더에게 디지털 교육을 먼저 투자하거나, IT와 HR 간 공동 KPI를 설계하는 것부터 시작하라.

**하지 말 것**: Moderna 조직 구조를 그대로 복사하지 말 것. 담당자의 역량 조건 없이 조직 박스만 합치면 두 기능 모두 약화된다.

---

### 교훈 7: 고위험 영역은 민주화가 아닌 Human-in-the-loop로

**Moderna 사례**: Dose ID GPT는 임상팀의 최종 검토를 위한 입력 자료 생성 용도. AI가 용량을 직접 결정하지 않음.

**따라 할 것**: "AI 민주화 영역"과 "AI 지원 + 인간 최종 결정 영역"을 명시적으로 분리하고, 규제·환자 안전·법적 리스크가 있는 영역은 후자로 분류하라.

---

### 경고 사항 (따라 하면 안 되는 것)

| 리스크 | 내용 |
|--------|------|
| **핵심 인물 의존** | Brice Challamel → OpenAI 이직. AI 전략 설계자 이탈 시 실행 공백 발생. 역할이 사람이 아닌 프로세스·거버넌스에 내재화되어야 한다. |
| **인과 과장** | 채택률·사용량 수치가 사업 성과(신약 개발 속도, 매출)와 인과적으로 연결됐다고 주장하지 말 것. Moderna 자신도 이를 입증하지 못했다. |
| **비용 절감 명목의 구조조정** | 디지털팀 10% 감축은 AI 도입이 아닌 매출 급감(비용 10억 달러 절감 목표)에 의한 결정. AI 효율화와 인력 감축을 동일시하면 문화 저항을 초래한다. |

---

## 출처 (Sources)

| # | 출처 | URL | 유형 | 비고 |
|---|------|-----|------|------|
| 1 | OpenAI — Moderna case study | https://openai.com/index/moderna/ | ``[Self-Reported]`` (기업 발표) | ChatGPT Enterprise 배포 수치의 1차 출처; OpenAI는 공급업체 |
| 2 | HBS Case 625-070 "Democratizing Artificial Intelligence" (Bojinov, Lakhani 외, 2025.01) | https://store.hbr.org/product/moderna-democratizing-artificial-intelligence/625070 | `[Self-Reported+Analyst]` | OpenAI 1차 자료 기반 HBS 학술 분석; MBA 정규 케이스로 채택 |
| 3 | Fortune — "Moderna CIO Brad Miller" (2024.04.17) | https://fortune.com/2024/04/17/moderna-cio-brad-miller-covid-drugs-ai-cloud/ | ``[Self-Reported]`` (기업 발표) | Brad Miller 인터뷰, mChat·AWS 결정 세부 |
| 4 | Fortune — "Moderna AI upskilling" (2024.03.18) | https://fortune.com/2024/03/18/moderna-ai-upskilling-program-chro-tracey-franklin/ | ``[Self-Reported]`` (기업 발표) | Tracey Franklin 인터뷰, AI Academy 재설계 세부 |
| 5 | Fortune — "Moderna leader AI conflict" (2025.05.19) | https://fortune.com/2025/05/19/moderna-leader-ai-resolve-conflictexecutive-teamall-before-it-happens/ | ``[Self-Reported]`` (기업 발표) | Franklin의 AI 갈등 예측 모델 활용 사례 |
| 6 | CIO.com — "Moderna's HR-IT merger: Trend or exception" | https://www.cio.com/article/4002321/modernas-hr-it-merger-trend-or-exception-to-the-rule.html | ``[Independently-Audited]`` (LinkedIn 공식 순위) | Ken Knapton 박사(독립 분석가) 비판적 평가 |
| 7 | UNLEASH — "Why Moderna merged HR and IT" | https://www.unleash.ai/artificial-intelligence/why-moderna-merged-hr-and-it-to-better-architect-the-flow-of-work/ | ``[Self-Reported]`` (기업 발표) | Franklin 인터뷰, 통합 철학 상세 |
| 8 | FlexOS — "Moderna Merges HR & IT" | https://www.flexos.work/learn/moderna-merges-hr-it-new-chief-manages-3000-ai-and-5800-humans | ``[Self-Reported]`` (기업 발표) | 3,000 AI + 5,800인 통합 관리 수치 |
| 9 | IntuitionLabs — Moderna AI Adoption Case Study | https://intuitionlabs.ai/articles/moderna-ai-adoption-case-study | ``[Self-Reported]`` (기업 발표) | 타임라인·교육 지표 종합; OpenAI 자료 재가공 |
| 10 | CMU News — "Moderna AI Academy" (2021.12) | https://www.cmu.edu/news/stories/archives/2021/december/moderna-ai-academy.html | ``[Independently-Audited]`` (LinkedIn 공식 순위) | CMU 공식 발표; AI Academy 출범 1차 확인 |
| 11 | PharmExec — "How Moderna is Implementing AI and ChatGPT" (2024.06) | https://www.pharmexec.com/view/moderna-implementing-ai-chatgpt | ``[Self-Reported]`` (기업 발표) | Brice Challamel 인터뷰, Contract Companion 90~95% 절감 주장 |
| 12 | AI Native Foundation — Moderna Case Study 8 | https://ainativefoundation.org/ai-native-case-study-8-moderna/ | ``[Self-Reported]`` (기업 발표) | 주의: "AI 생성 평가, 데이터 미뒷받침"이라고 자체 고지 |

> **면책 고지**: 이 노트는 2026년 6월 기준 공개 자료를 종합한 것이다. 750개·3,000개 GPT, 120회/주 대화 수, 40~95% 절감 수치는 모두 Moderna 또는 OpenAI 자체 보고 기반이며 독립 감사를 거치지 않았다. AI 채택이 임상·사업 성과로 이어졌다는 인과는 미입증 상태다. valid_until 기준(2027-Q2) 이전에 독립 연구·감사 자료가 나올 경우 업데이트 필요.
