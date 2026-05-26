---
tags: [engineering-taste, software-engineering, judgment, paul-graham, ai-era, career]
created: 2026-05-26
---

# "Taste" — 엔지니어가 말하는 그 단어의 정체

## 📋 한 줄 요약

엔지니어링에서 **taste(테이스트)**는 "취향" 같은 **주관적 선호가 아니라**, **불확실한 상황에서 트레이드오프를 가려내는 훈련된 판단력**을 뜻합니다. 코드를 *짤 줄 아는 것*(skill)과 무엇이 좋은 코드/제품인지 *알아보는 것*(taste)은 별개이며, AI가 "짜는 일"을 대신하면서 이 *알아보는 능력*이 핵심 차별화 요소로 급부상했습니다. ✅ [Confirmed]

> 관련 노트: [[ai-native-engineer-role]] — AI Native Engineer 직군의 1번 핵심 역량이 "Product & Outcome Taste"

---

## 🍷 왜 하필 "맛(taste)"이라는 단어일까?

> 🧒 12살 비유
> **요리 평론가**를 생각해보세요. 요리를 직접 못 만들어도(=기술 실력 없음) **"이 음식이 왜 훌륭한지"는 정확히 짚어내는 사람**이 있죠. 반대로 칼질은 빠른데(=기술 실력 좋음) 손님이 뭘 원하는지 모르는 요리사도 있고요.
> 엔지니어링의 "taste"가 바로 이 **요리 평론가의 혀** — *직접 만드는 능력과 별개로, 무엇이 좋은지 알아보는 감각*입니다.

Sean Goedecke가 이 구분을 정확히 못박습니다:

> 💬 *"Technical taste is different from technical skill. You can be technically strong but have bad taste."*
> (기술적 taste는 기술 실력과 다르다. 기술적으로 뛰어나면서도 taste가 나쁠 수 있다.)

---

## 📜 계보: 이 단어는 어디서 왔나

```
1995 ───────────── 2002 ───────────── 2025~2026
Steve Jobs        Paul Graham         Andrej Karpathy
"무취향 비판"      "취향=훈련됨"        "AI 시대 = taste 시대"
   │                  │                     │
   ▼                  ▼                     ▼
독창성·문화        주관 아닌 판단력      구현이 싸지니
부재 = no taste    (학습 가능)          판단이 차별화
```

### 1️⃣ Steve Jobs (1995) — 대중화의 시작

마이크로소프트를 두고 한 유명한 말:

> 💬 *"The only problem with Microsoft is they just have no taste. They have absolutely no taste."*

핵심은 — Jobs가 말한 taste는 **겉멋(심미적 세련됨)이 아니었다**는 점입니다. 그는 "그들은 **독창적 아이디어를 생각하지 않고, 제품에 문화를 담지 않는다**"는 뜻이라고 부연했습니다. 즉 **독창성·비전·사려 깊은 설계 철학**을 가리킨 거죠. ✅ [Confirmed] (1995 Cringely 인터뷰, PBS "Triumph of the Nerds")

### 2️⃣ Paul Graham "Taste for Makers" (2002) — 이론적 정초

엔지니어/메이커 사이에서 "taste"를 진지한 개념으로 만든 결정적 에세이입니다. 그의 핵심 주장은 **"taste는 주관적이다"라는 통념을 정면 반박**한 것:

> 💬 *"Saying that taste is just personal preference is a good way to prevent disputes. The trouble is, it's not true."*
> (취향이 그저 개인 선호라고 말하는 건 논쟁을 피하는 좋은 방법이다. 문제는, 그게 사실이 아니라는 것.)

그의 논리가 영리합니다 🧠 — *만약 taste가 순수 주관이라면, 디자이너가 경력을 쌓으며 취향이 "나아지는" 현상을 설명할 수 없다*. 취향이 향상된다는 건, 더 나은 취향이 **객관적으로 존재**하고 **훈련으로 다가갈 수 있다**는 뜻입니다. 그리고 좋은 디자인의 원칙을 제시:

| 원칙              | 원문                                                  |
| ----------------- | ----------------------------------------------------- |
| 단순함            | *"Good design is simple."*                            |
| **올바른 문제 해결** | *"Good design solves the right problem."*             |
| 암시적            | *"Good design is suggestive."*                        |
| 재설계            | *"Good design is redesign."* (한 번에 맞추는 일은 드물다) |

✅ [Confirmed] (paulgraham.com 원문 직접 확인)

### 3️⃣ Karpathy & AI 시대 (2025~2026) — 급부상

여기가 **"요즘 부쩍 많이 보인다"고 느끼는 이유**입니다. Karpathy가 "vibe coding"(2025) → "agentic engineering"(2026)으로 정리한 흐름에서, 가치가 **위로 이동(moves up)**합니다:

```
       [ 가치가 어디에 있는가 ]

  과거           →           AI 시대
  ────                       ────
  syntax 숙련                무엇을 만들지 판단 (taste)
  디버깅 속도        ⬆️      에이전트 감독·검증
  프레임워크 암기            시스템 설계
  (구현 = 비쌈)              (구현 = 싸짐)
```

> 💬 Karpathy 관점: *"가치가 syntax·구현에서 판단·taste·감독으로 위로 이동한다. 모델이 구현을 떠맡으면서 개발자는 editor·reviewer·system designer가 된다."*

OfferZen이 이걸 한 문장으로 압축합니다:

> 💬 *"When speed is cheap, judgement becomes the differentiator."*
> (속도가 싸지면, 판단이 차별화 요소가 된다.)

✅ [Confirmed] (Karpathy 발언 다수 출처 + OfferZen)

---

## 🎯 그래서 엔지니어링에서 "taste"의 작동 정의는?

여러 출처가 수렴하는 정의입니다:

> **Taste = 불확실성 속에서 트레이드오프를 가려내는, 장기 비용·위험을 줄이는 규율 있는 판단**
> *(disciplined judgment about tradeoffs under uncertainty that reduces long-term cost and risk)*

왜 *트레이드오프*가 핵심이냐면 — Sean Goedecke의 말처럼:

> 💬 *"Almost every decision in software engineering is a tradeoff."*

`map/filter` vs `for` 루프, 추상화를 지금 넣을까 말까, 이 에러를 던질까 삼킬까... **정답이 하나가 아닌 갈림길**에서 "이 프로젝트엔 이게 맞다"를 고르는 감각이 taste입니다. 그래서 그는 taste를 *"현재 프로젝트에 맞는 엔지니어링 가치관을 채택하는 능력"*이라 정의하고, **bad taste = 상황에 안 맞는 가치관을 고집하는 "고장난 나침반(broken compass)"**이라 표현합니다.

---

## 🔗 "Product Taste" vs "Outcome Taste"

AI Native Engineer 채용 역량(Augment Code)에 등장하는 **"Product & Outcome Taste"**를 분해하면:

- **Product taste** = "사용자가 *진짜* 원하는 게 뭔지" 알아보는 감각
- **Outcome taste** = "코드를 짰다"가 아니라 "*올바른 결과*를 냈다"를 판별하는 감각

*"가장 영향력 있는 엔지니어는 가장 많은 코드를 작성하는 사람이 아니라, 팀이 **올바른 문제**를 풀게 하는 사람"* — 이게 Paul Graham의 *"solves the right problem"* 원칙과 정확히 같은 뿌리입니다. 🌳

---

## ⚠️ Edge Cases & 주의점

| 관점                       | 내용                                                                                                              |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **"taste"가 면죄부가 될 위험** | "내 taste로는 이게 맞아"가 근거 없는 고집의 변명이 될 수 있음. Antonio Agudo는 *"Tests, Not Vibes"*라며 **taste도 검증 가능한 근거로 뒷받침**돼야 한다고 반박 ❓ |
| **"Taste Is Not a Moat" 반론** | Shrivu Shankar는 AI가 평균적 taste도 학습하면 *taste만으론 차별화가 안 된다*고 주장. taste 만능론에 대한 건강한 반대 시각 ❓ [Uncertain — 논쟁 중] |
| **버즈워드화 경계**        | "taste"가 채용 공고의 유행어로 남용되면 의미가 희석됨                                                              |

---

## 🌱 taste는 어떻게 기르나? (성장 관점)

Paul Graham의 핵심 메시지가 곧 답입니다 — **taste는 타고나는 게 아니라 훈련된다**:

1. **많이 보기**: 좋은 코드베이스·좋은 제품을 의식적으로 분석 (요리 평론가가 맛집을 다니듯)
2. **트레이드오프를 말로 표현**: "왜 A 대신 B를 골랐나"를 매번 언어화 → 직관을 명시적 판단으로
3. **재설계 반복**: *"Good design is redesign"* — 1차 결과를 비판하고 다시 만드는 훈련
4. **사용자/맥락 이해**: 코드 너머의 사용자·비즈니스·팀 역학을 아는 것이 outcome taste의 토대

> 💡 백엔드 배경(Python/FastAPI/Celery)이라면, "이 동시성 문제를 Celery로 풀까 / async로 풀까 / 큐를 둘까"를 매번 **이유와 함께 기록**하는 것 자체가 taste 훈련입니다. 트레이드오프 비교 노트(GMP, GC, connection pool 등)가 곧 taste의 증거 자산이 됩니다.

---

## 📎 Sources

1. [Taste for Makers — Paul Graham (2002)](https://paulgraham.com/taste.html) — 1차 자료 (원문 확인)
2. [What is "good taste" in software engineering? — Sean Goedecke](https://www.seangoedecke.com/taste/) — 1차 자료 (원문 확인)
3. [Steve Jobs on Microsoft: "They just have no taste" — Computerworld](https://www.computerworld.com/article/1484493/steve-jobs-on-microsoft-they-just-have-no-taste.html) — 1차 인용 (1995 Cringely 인터뷰)
4. [Why "Engineering Taste" Is Becoming a Critical Skill — OfferZen](https://www.offerzen.com/blog/ai-fluency-engineering-teams) — 기술 블로그
5. [What Do Engineers Mean When We Say "Taste"? — Dave Griffith](https://davegriffith.substack.com/p/what-do-engineers-mean-when-we-say) — 기술 블로그
6. [Good Taste in Software Engineering: Tests, Not Vibes — Antonio Agudo](https://antonioagudo.com/blog/good-taste-in-software-design/) — 기술 블로그 (반론)
7. [Taste Is Not a Moat — Shrivu Shankar](https://blog.sshh.io/p/taste-is-not-a-moat) — 기술 블로그 (반론)
8. [From Vibe Coding to Agentic Engineering: Karpathy's Vision](https://aiagentssimplified.substack.com/p/from-vibe-coding-to-agentic-engineering) — 기술 블로그

---

## 📊 Research Metadata

- 검색 쿼리 수: 4 (일반 4)
- 수집 출처 수: 8 (원문 확인 2건: Paul Graham, Sean Goedecke)
- 출처 유형 분포: 1차 자료 3, 기술 블로그 5
- 확신도 분포: ✅ Confirmed 4, ❓ Uncertain 2 (taste 만능론 논쟁)
- 원문 직접 인용: 9건
