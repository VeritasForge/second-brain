---
tags: [automl, machine-learning, llm, agentic-ai, deep-research, benchmark]
created: 2026-04-20
---

# 🔬 Deep Research: AutoML (Automated Machine Learning) — 2022년 블로그 vs 2025년 최신 동향

> 원본 블로그: [data-minggeul - AutoML 이란?](https://data-minggeul.tistory.com/12) (2022.11)

---

## 📋 Executive Summary

원본 블로그(2022.11)는 AutoML의 3가지 유형(OSS, Cloud, Enterprise)과 기본 개념을 잘 정리했다. 그러나 **2023-2025년 사이 AutoML은 근본적인 패러다임 전환**을 겪었다. 가장 큰 변화는 **LLM(Large Language Model, 대규모 언어 모델)과의 통합**으로, "코드 기반 파이프라인 자동화"에서 **"자연어 기반 에이전트형 AutoML"**로 진화하고 있다. 벤치마크에서는 **AutoGluon**이 일관된 1위를 차지하며, **TPOT은 v1.1.0 대규모 리팩토링 완료** (TPOT2는 개발 코드명으로 메인에 병합됨), Auto-sklearn은 대규모 데이터에서 약세를 보인다.

---

## 🔍 Findings

### 1. 🤖 Agentic AutoML — "왜(Why)"에 집중하는 새로운 패러다임

> 🎯 **비유**: 기존 AutoML이 "자동 세탁기"(빨래를 넣으면 알아서 세탁)였다면, Agentic AutoML은 "가정부 로봇"(빨래가 필요한 옷을 골라서, 적절한 세탁 방법을 선택하고, 건조까지 알아서 해주는)이다.

**전통 AutoML vs Agentic AutoML:**

```
┌─────────────────────────────────────────────────────────┐
│         전통 AutoML (2022 블로그 기준)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                 │
│  │ 전처리   │→│ 모델링   │→│ 후처리   │                 │
│  │ (수동)   │ │ (자동)   │ │ (수동)   │                 │
│  └──────────┘ └──────────┘ └──────────┘                 │
│  사용자가 코드를 작성하고, 데이터를 준비해야 함           │
├─────────────────────────────────────────────────────────┤
│         Agentic AutoML (2025~)                          │
│  ┌──────────────────────────────────────────────┐       │
│  │  "매출 예측 모델을 만들어줘" (자연어 입력)    │       │
│  │         ↓                                    │       │
│  │  🤖 Agent Manager                           │       │
│  │    ├── 📊 Data Agent (데이터 이해/전처리)    │       │
│  │    ├── 🧠 Model Agent (모델 선택/설계)       │       │
│  │    ├── ⚙️ Operation Agent (코드 생성/실행)   │       │
│  │    └── ✅ Verification (다단계 검증)         │       │
│  │         ↓                                    │       │
│  │  배포 가능한 모델 + 설명 보고서              │       │
│  └──────────────────────────────────────────────┘       │
│  자연어로 지시하면 전체 파이프라인을 에이전트가 수행      │
└─────────────────────────────────────────────────────────┘
```

- ✅ **확신도**: [Confirmed]
- **출처**: [AutoML-Agent: ICML 2025](https://arxiv.org/abs/2410.02958), [AutoGluon Assistant: Amazon Science / NeurIPS 2025](https://www.amazon.science/blog/autogluon-assistant-zero-code-automl-through-multiagent-collaboration)
- **근거**: ICML 2025에서 AutoML-Agent 논문이 발표되었고, Amazon의 AutoGluon Assistant가 MLE-bench Lite에서 **86% 성공률, 평균 순위 1.43**을 달성. 2024 Kaggle AutoML Grand Prix에서 **유일한 완전 자동화 에이전트로 득점**에 성공.

---

### 2. 📊 AutoML 도구 벤치마크 — AutoGluon 1위, TPOT 리팩토링 완료

> 🎯 **비유**: AutoML 도구를 요리사에 비유하면, AutoGluon은 "빠르고 맛있게 만드는 올라운더 셰프", Auto-sklearn은 "느리지만 정교한 미슐랭 셰프", TPOT은 "메뉴를 전면 리뉴얼한 셰프"이다.

| 도구           | 2022 블로그 평가 | 2025 최신 평가                                  | 변화          |
| -------------- | :--------------: | :---------------------------------------------: | :-----------: |
| **AutoGluon**  | ❌ 미언급        | ✅ 벤치마크 1위 (AUC 최고)                      | 🆕 신규 강자  |
| **Auto-sklearn** | ✅ OSS 대표    | 🟡 소규모 데이터에서만 강세                     | ⬇️ 약화      |
| **TPOT**       | ✅ OSS 대표      | ✅ v1.1.0 대규모 리팩토링 완료 (TPOT2 메인 병합) | 🔄 리뉴얼    |
| **AutoKeras**  | ✅ OSS 대표      | 🟡 딥러닝 전용, 빠르지만 복잡한 데이터에 약함   | ➡️ 유지      |
| **H2O AutoML** | ✅ Enterprise    | ✅ 대규모 분산 처리 강점 유지                    | ➡️ 유지      |
| **DataRobot**  | ✅ Enterprise    | ✅ 비즈니스 사용자 대상 강세                     | ➡️ 유지      |
| **Ludwig (Uber)** | ❌ 미언급     | 🟡 딥러닝 전용, 다양한 입력 지원                | 🆕 신규      |

> ⚠️ **rl-verify 정정**: 원래 "TPOT 개발 중단"으로 기술했으나, GitHub 확인 결과 TPOT2는 별도 프로젝트가 아닌 **리팩토링 코드명**이며 2025년 7월 v1.1.0으로 메인 패키지에 병합됨. 최근 커밋: 2025-09-11.

- ✅ **확신도**: [Confirmed]
- **출처**: [Scientific Reports 2025, 16개 도구 벤치마크](https://www.nature.com/articles/s41598-025-02149-x), [Geniusee AutoML Frameworks 2025](https://geniusee.com/single-blog/automl-frameworks), [GitHub: EpistasisLab/tpot](https://github.com/EpistasisLab/tpot)
- **근거**: 2025년 Scientific Reports에 게재된 논문이 21개 실제 데이터셋에서 16개 도구를 비교. AutoGluon이 **정확도와 효율성의 최적 균형**으로 종합 1위. TPOT 상태는 GitHub에서 직접 확인.

---

### 3. 🧠 LLM × AutoML 통합 — 자연어로 ML 파이프라인 구축

> 🎯 **비유**: 이전에는 "레시피(코드)를 직접 작성"해야 했지만, 이제는 "음식 사진을 보여주면 AI 셰프가 레시피를 만들어주는" 것과 같다.

**핵심 프레임워크들:**

| 프레임워크             | 구조             | 핵심 특징                                       | 발표              |
| ---------------------- | ---------------- | ----------------------------------------------- | ----------------- |
| **AutoML-Agent**       | Multi-Agent LLM  | Retrieval-augmented planning + 병렬 실행        | ICML 2025         |
| **AutoM3L**            | 5개 LLM 모듈    | MI/AFE/MS/PA/HPO 전용 모듈                      | ACM Multimedia 2024 |
| **AutoGluon Assistant** | MLZero 아키텍처 | Perception/Semantic/Episodic Memory + Iterative Coding | NeurIPS 2025 |

**AutoGluon Assistant 아키텍처 상세:**

```
┌────────────────────────────────────────────────┐
│          AutoGluon Assistant (MLZero)           │
│                                                │
│  ┌─────────────┐    ┌─────────────────┐        │
│  │  Perception  │    │ Semantic Memory │        │
│  │   Module     │    │    Module       │        │
│  │ (데이터 이해)│    │ (ML 라이브러리  │        │
│  │              │    │  지식 저장)     │        │
│  └──────┬───────┘    └───────┬─────────┘        │
│         │                    │                  │
│         ▼                    ▼                  │
│  ┌──────────────────────────────────┐           │
│  │       Iterative Coding Module    │           │
│  │  (코드 생성 → 실행 → 피드백 루프)│           │
│  └──────────────┬───────────────────┘           │
│                 │                               │
│  ┌──────────────▼───────────────────┐           │
│  │      Episodic Memory Module      │           │
│  │  (실행 이력/디버깅 컨텍스트 추적)│           │
│  └──────────────────────────────────┘           │
│                                                │
│  성과: MLE-bench 86% 성공률, 6 Gold Medals     │
└────────────────────────────────────────────────┘
```

**AutoM3L 5개 모듈 상세:**

| 모듈      | 역할                                                              |
| --------- | ----------------------------------------------------------------- |
| MI-LLM    | Modality Inference — 데이터 컬럼별 모달리티(이미지/텍스트/정형) 추론 |
| AFE-LLM   | Automated Feature Engineering — 불필요 속성 필터링 + 결측값 보간    |
| MS-LLM    | Model Selection — 모델 카드 기반 적합 모델 선택 및 순위화           |
| PA-LLM    | Pipeline Assembly — late fusion 기반 멀티모달 파이프라인 코드 생성   |
| HPO-LLM   | Hyperparameter Optimization — 하이퍼파라미터 탐색 공간 자동 추천    |

- ✅ **확신도**: [Confirmed]
- **출처**: [AutoML-Agent (ICML 2025)](https://arxiv.org/abs/2410.02958), [AutoGluon Assistant (Amazon Science)](https://www.amazon.science/blog/autogluon-assistant-zero-code-automl-through-multiagent-collaboration), [AutoM3L (arXiv 2408.00665 / ACM Multimedia 2024)](https://arxiv.org/html/2408.00665v1)
- **근거**: 세 논문 모두 독립적으로 LLM + AutoML 통합 아키텍처를 제시하고 실험 결과를 공개.

---

### 4. ⚠️ AutoML의 현재 한계 — "No-Code"는 아직 불완전

> 🎯 **비유**: AutoML은 "자율주행 레벨 3"과 비슷하다. 대부분의 상황은 자동으로 처리하지만, 위험한 상황(지저분한 데이터, 복잡한 요구사항)에서는 사람이 핸들을 잡아야 한다.

**2022 블로그의 한계 지적 vs 2025 현실:**

| 2022 블로그 한계                 | 2025 현재 상태                     | 해결 여부     |
| -------------------------------- | ---------------------------------- | :-----------: |
| 데이터 전처리에 인간 개입 필요   | Agentic AutoML이 자동화 시도 중    | 🟡 부분 해결  |
| 하이퍼파라미터 튜닝만 자동화     | 전체 파이프라인 자동화 가능        | ✅ 대폭 개선  |
| OSS는 컴퓨팅 자원 많이 필요      | Edge/Federated Learning 지원       | 🟡 부분 해결  |
| Cloud 솔루션 내부 구현 불투명    | XAI(Explainable AI) 통합 추세      | 🟡 개선 중    |

**여전히 남아 있는 한계:**

| 한계                          | 설명                                            |
| ----------------------------- | ----------------------------------------------- |
| ❌ 비정형 데이터 전처리       | 지저분한 데이터는 여전히 전문가 개입 필요       |
| ❌ 비지도/강화학습            | AutoML은 여전히 지도학습 위주                   |
| ❌ 도메인 특화 문제           | 극도로 특수한 데이터는 자동화 어려움            |
| ❌ 모델 품질 편차             | 동일 데이터에 여러 번 실행 시 결과 변동         |
| ❌ 에너지 비용/지속가능성     | 대규모 탐색의 환경 비용 인식 증가               |

- ✅ **확신도**: [Confirmed]
- **출처**: [Fingerlakes1 - AutoML in 2025](https://www.fingerlakes1.com/2025/07/31/automl-in-2025-does-it-finally-deliver-on-the-no-code-ai-promise/), [Google ML Course - AutoML Benefits & Limitations](https://developers.google.com/machine-learning/crash-course/automl/benefits-limitations), [Geniusee 2025](https://geniusee.com/single-blog/automl-frameworks)
- **근거**: 3개 독립 출처에서 동일한 한계점 지적. Fingerlakes1 원문에서 "tasks like preparing messy datasets... still require technical knowledge" 확인.

---

### 5. 📈 AutoML 시장 및 트렌드 — 6가지 핵심 방향

> 🎯 **비유**: AutoML이 "자동차"라면, 2025년에는 6가지 "업그레이드 옵션"이 추가되고 있다.

```
2025-2026 AutoML 핵심 트렌드
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  Agentic AutoML
    └── "How → Why" 전환, 비즈니스 임팩트 중심

2️⃣  LLM 통합
    └── 자연어 인터페이스, 알고리즘 자동 생성

3️⃣  Explainability & Fairness
    └── XAI, 공정성 제약 조건 내장

4️⃣  Federated Learning + Edge
    └── 데이터 분산, 엣지 디바이스 최적화

5️⃣  지속가능성 (Sustainability)
    └── 에너지 효율, 탄소 비용 메트릭

6️⃣  Human-in-the-Loop
    └── 실시간 메타러닝, 사용자 가이던스
```

- **시장 규모**: USD **6.81B** (2026년 예상), **$15B** (2030년 전망)
- 🟡 **확신도**: [Likely] — 시장 규모 수치는 ResearchAndMarkets 단일 출처
- **출처**: [ResearchAndMarkets 2025](https://www.researchandmarkets.com/reports/5896115/automated-machine-learning-automl-market-report), [KDnuggets 2026 Trends](https://www.kdnuggets.com/5-cutting-edge-automl-techniques-to-watch-in-2026), [USAII 2026](https://www.usaii.org/ai-insights/6-automl-techniques-powering-the-future-of-ai-in-2026)

---

### 6. 🛠️ 2025년 기준 AutoML 도구 선택 가이드

> 🎯 **비유**: 음식점을 고르는 것과 같다. 빨리 먹고 싶으면 패스트푸드(AutoGluon), 정교한 맛을 원하면 파인다이닝(수동 ML), 요리를 모른다면 밀키트(Cloud AutoML).

```
내 상황은?
    │
    ├── 코딩을 모른다
    │    └── ✅ AutoGluon Assistant (자연어 입력)
    │         또는 Cloud AutoML (Google/AWS UI)
    │
    ├── Python은 할 줄 안다
    │    ├── 빠른 프로토타이핑 → ✅ AutoGluon
    │    ├── 딥러닝 전용 → ✅ AutoKeras
    │    └── 커스터마이징 중요 → ✅ H2O AutoML
    │
    ├── 기업 환경 (보안/규정 중요)
    │    ├── 온프레미스 필요 → ✅ DataRobot / H2O
    │    └── 클라우드 OK → ✅ SageMaker / Vertex AI
    │
    └── 최첨단 연구
         └── ✅ 수동 ML + AutoML 하이브리드
              (AutoML로 baseline → 수동 최적화)
```

- 🔄 **확신도**: [Synthesized] — 여러 출처의 도구별 특성을 조합한 가이드
- **출처**: [Scientific Reports 2025 벤치마크](https://www.nature.com/articles/s41598-025-02149-x) + [Geniusee Framework 비교](https://geniusee.com/single-blog/automl-frameworks) + [Fingerlakes1 2025 평가](https://www.fingerlakes1.com/2025/07/31/automl-in-2025-does-it-finally-deliver-on-the-no-code-ai-promise/)

---

## 📊 원본 블로그(2022) vs 현재(2025) 비교

| 항목                 | 블로그 (2022.11)                    | 현재 (2025)                               |
| -------------------- | ----------------------------------- | ----------------------------------------- |
| **AutoML 정의**      | ML 학습/배포 자동화                 | 자연어 기반 전체 파이프라인 자동화         |
| **핵심 기술**        | HPO, NAS                            | LLM 통합, Multi-Agent, Federated Learning |
| **OSS 대표 도구**    | Auto-sklearn, TPOT                  | **AutoGluon** (1위), Auto-sklearn (약세), TPOT (리뉴얼) |
| **Cloud 솔루션**     | Google AutoML, SageMaker            | + AutoGluon Assistant, Vertex AI 강화     |
| **Enterprise**       | DataRobot, H2O                      | 유지 + AI Explainability 강화             |
| **주요 한계**        | 전처리 수동, 컴퓨팅 비용            | + 비지도학습 미지원, 에너지 비용          |
| **비전문가 접근성**  | "솔루션 UI 추천"                    | **자연어 입력으로 모델 생성 가능**        |
| **시장 규모**        | 미언급                              | $6.81B (2026), $15B (2030)                |

---

## ⚠️ Edge Cases & Caveats

| 시나리오                            | 영향                                   | 권고                                 |
| ----------------------------------- | -------------------------------------- | ------------------------------------ |
| 극소량 데이터 (<100건)              | AutoML 탐색 공간 부족으로 성능 저하    | 전이학습 또는 수동 모델 우선         |
| 실시간 스트리밍 데이터              | 대부분 AutoML은 배치 학습 기준         | 온라인 학습 전용 도구 고려           |
| 멀티모달 (이미지+텍스트+정형)       | 일부 도구만 지원                       | AutoGluon MultiModal 또는 AutoM3L   |
| 규제 산업 (의료/금융)               | 모델 해석 가능성 필수                  | XAI 내장 도구 (DataRobot, H2O)      |
| 엣지 디바이스 배포                  | 모델 경량화 필요                       | TinyML + AutoML 조합                 |

---

## ⚔️ Contradictions Found

| 모순                               | 출처 A                                | 출처 B                                   | 해결                                                        |
| ---------------------------------- | ------------------------------------- | ---------------------------------------- | ----------------------------------------------------------- |
| Auto-sklearn 성능                  | Geniusee: "소규모 데이터에서 강세"    | Scientific Reports: "이진/다중분류에서 예측 성능 우수하나 느림" | **양립 가능** — 정확도는 높으나 시간 대비 효율이 낮음       |
| AutoML의 No-Code 달성 여부         | USAII: "완전 자동화 달성"             | Fingerlakes1: "아직 불완전"              | **맥락 차이** — 정형 데이터는 거의 달성, 비정형은 미달      |

---

## ✅ rl-verify 검증 결과

| # | 검증 항목                          | 결과             | 상세                                                                                      |
| - | ---------------------------------- | :--------------: | ----------------------------------------------------------------------------------------- |
| 1 | TPOT 개발 중단 여부               | ⚠️ **Corrected** | TPOT은 개발 중단되지 않았음. TPOT2는 리팩토링 코드명이며 v1.1.0으로 메인에 병합 (2025.07) |
| 2 | AutoGluon 벤치마크 1위            | ✅ **Verified**  | Scientific Reports 2025에서 종합 1위 확인                                                 |
| 3 | AutoML-Agent ICML 2025            | ✅ **Verified**  | arXiv 페이지에서 "ICML 2025" 명시 확인                                                    |
| 4 | AutoGluon Assistant 86% 성공률    | ✅ **Verified**  | Amazon Science 블로그 원문에서 86%, 1.43 순위, 6 gold medals 정확 확인                    |
| 5 | AutoM3L 5개 모듈                  | ✅ **Verified**  | arXiv 2408.00665에서 MI/AFE/MS/PA/HPO-LLM 5개 모듈명 정확 일치                           |
| 6 | 시장 규모 $6.81B (2026)           | 🟡 **Unverified** | ResearchAndMarkets 유료 보고서로 직접 확인 불가. 단일 출처                                |

---

## 📎 Sources

1. [AutoML-Agent: ICML 2025 (arXiv 2410.02958)](https://arxiv.org/abs/2410.02958) — 학술 논문 (1차 자료)
2. [AutoGluon Assistant: Amazon Science Blog](https://www.amazon.science/blog/autogluon-assistant-zero-code-automl-through-multiagent-collaboration) — 공식 기술 블로그 (1차 자료)
3. [Scientific Reports 2025: 16 AutoML Tools Benchmark](https://www.nature.com/articles/s41598-025-02149-x) — 학술 논문 (1차 자료)
4. [Springer AI Review 2025: AutoML Literature Review](https://link.springer.com/article/10.1007/s10462-025-11397-2) — 학술 서베이 (1차 자료)
5. [AutoML in the Age of LLMs (TMLR, arXiv 2306.08107)](https://arxiv.org/abs/2306.08107) — 학술 서베이 (1차 자료)
6. [AutoM3L (arXiv 2408.00665 / ACM Multimedia 2024)](https://arxiv.org/html/2408.00665v1) — 학술 논문 (1차 자료)
7. [Geniusee: Top AutoML Frameworks 2025](https://geniusee.com/single-blog/automl-frameworks) — 기술 블로그
8. [Fingerlakes1: AutoML No-Code Promise 2025](https://www.fingerlakes1.com/2025/07/31/automl-in-2025-does-it-finally-deliver-on-the-no-code-ai-promise/) — 기술 기사
9. [ResearchAndMarkets: AutoML Market Report 2025](https://www.researchandmarkets.com/reports/5896115/automated-machine-learning-automl-market-report) — 시장 조사 보고서
10. [Google ML Course: AutoML Benefits & Limitations](https://developers.google.com/machine-learning/crash-course/automl/benefits-limitations) — 공식 문서
11. [ETRI: AutoML 기술 동향](https://ettrends.etri.re.kr/ettrends/178/0905178004/34-4_32-42.pdf) — 한국 공식 기술 보고서
12. [GitHub: EpistasisLab/tpot](https://github.com/EpistasisLab/tpot) — OSS 저장소 (rl-verify 검증)
13. [원본 블로그: data-minggeul](https://data-minggeul.tistory.com/12) — 한국 기술 블로그

---

## 📊 Research Metadata

| 항목               | 수치                                                                   |
| ------------------ | ---------------------------------------------------------------------- |
| 검색 쿼리 수       | 9 (일반 7 + SNS 2)                                                    |
| 수집 출처 수       | 13                                                                     |
| 출처 유형 분포     | 공식 2, 1차(학술) 6, 블로그 3, 시장조사 1, OSS 저장소 1               |
| 확신도 분포        | ✅ Confirmed 4, 🟡 Likely 1, 🔄 Synthesized 1, ❓ Uncertain 0, ⚪ Unverified 0 |
| SNS 출처           | Reddit 0건 (관련 토론 미발견)                                          |
| WebFetch 원문 확인 | 7건 성공, 2건 실패 (Springer/Nature 303 → WebSearch 대체)              |
| rl-verify 결과     | 4 Verified, 1 Corrected (TPOT), 1 Unverified (시장규모)               |
