---
tags: [prioritization, moscow-method, decision-matrix, requirements-engineering, methodology]
created: 2026-07-07
---

# "필수(Blocker)/핵심(Major)/참고(Minor)" 표현과 평가기준 도구

## 📋 Executive Summary

**이 표현 자체는 "버그 트래커 용어를 빌려온 것"이고, 원래는 의사결정 기준 가중치를 위한 표준 용어가 아니다.** 다만 "중요도 3~4단계로 기준을 나눠 채점한다"는 개념 자체는 이미 여러 표준 프레임워크(MoSCoW, RFC 2119)로 확립돼 있고, 그걸 구현하는 실제 도구(Weighted Decision Matrix, 벤더 평가 스코어카드)도 존재한다.

## 🔍 Findings

### 1. "Blocker/Major/Minor"는 버그 트래커(Jira)의 기본 Priority 값

- ✅ **확신도**: Confirmed (Atlassian 커뮤니티 공식 포럼 + 다수 독립 QA 블로그 교차확인)
- Jira의 기본 Priority 필드 값이 정확히 **Blocker > Critical > Major > Minor > Trivial** 순서다.
- "Blocker는 다른 모든 것보다 우선하는 최고 우선순위, Major는 상당한 영향, Minor는 상대적으로 작은 영향"이라는 정의도 QA/버그관리 도메인 고유의 것이다.
- **출처**: [Atlassian Community](https://community.atlassian.com/t5/Jira-questions/According-to-Jira-What-is-Blocker-Critical-Major-Minor-and/qaq-p/668774), [ToolsQA Severity vs Priority](https://www.toolsqa.com/software-testing/severity-vs-priority/)

즉 "의사결정 기준 가중치"라는 다른 목적에, 익숙한 QA/개발 도메인 용어(Blocker/Major/Minor)를 빌려와 재해석해 붙인 사례다. 이 자체는 흔한 일이지만, "가중치 부여"의 원래 표준 용어는 아래 프레임워크들이다.

### 2. 원래 이 개념(기준별 중요도 3~4단계)의 "정식 이름"은 MoSCoW

- ✅ **확신도**: Confirmed (Wikipedia + Agile Business Consortium 공식페이지 + 3개 이상 독립 매체 교차확인)
- **기원**: Dai Clegg가 1994년 Oracle 재직 중 개발 → 이후 DSDM(Dynamic Systems Development Method) 컨소시엄에 기증 → 2002년부터 본격 표준화
- **4단계**: Must Have(필수) / Should Have(중요하지만 필수는 아님) / Could Have(있으면 좋음) / Won't Have(이번엔 안 함)
- 필수/핵심/참고와 거의 1:1 대응된다: **필수≈Must, 핵심≈Should, 참고≈Could** (Won't Have에 대응하는 항목만 없음)
- **출처**: [Agile Business Consortium 공식](https://www.agilebusiness.org/resource/what-is-moscow-prioritization/), [Wikipedia](https://en.wikipedia.org/wiki/MoSCoW_method)

### 3. 기술 표준 문서 작성 분야의 formal한 대응 표현 — RFC 2119

- ✅ **확신도**: Confirmed (IETF 공식 RFC 원문 직접 확인)
- MUST(=필수, 절대적 요구사항) / SHOULD(=권고, 특별한 이유 없이 벗어나면 안 됨) / MAY(=선택, 진짜 옵션)
- IETF가 기술 표준 문서를 쓸 때 "요구사항의 강제성 정도"를 명확히 하기 위해 1997년 공식화한 관행이다.
- **출처**: [RFC 2119 원문 (IETF)](https://datatracker.ietf.org/doc/html/rfc2119)

### 4. "평가 기준에 가중치를 매겨 채점하는" 실제 도구/방법론 — Weighted Decision Matrix

- ✅ **확신도**: Confirmed (Lucid, Asana, 대학 교재(Pressbooks) 등 다수 독립 출처 교차확인)
- 각 기준에 **숫자 가중치**를 매기고, 각 옵션을 기준별로 채점한 뒤 **가중치 × 점수를 곱해 합산**하는 방식이다.
- "항목 | 중요도 | 판정 | 근거 | 비고" 형태의 표는 사실상 이 Weighted Decision Matrix의 **간소화 버전**이다 (3단계 라벨 대신 숫자 가중치를 쓰면 정식 버전이 된다).
- **출처**: [Lucid - Weighted Decision Matrix 소개](https://lucid.co/blog/weighted-decision-matrix), [Pressbooks 프로젝트관리 교재](https://ecampusontario.pressbooks.pub/essentialsofprojectmanagement/chapter/4-3-weighted-decision-matrix/)

### 5. 실제 "도구/템플릿"으로 존재하는 형태 — 벤더/기술 평가 스코어카드

- ✅ **확신도**: Confirmed (Smartsheet, Nvelop 등 복수의 실제 템플릿 제공처 확인)
- Smartsheet는 최대 10개 평가 기준에 가중치를 매겨 대시보드로 시각화하는 완제품 템플릿을 제공한다.
- 이런 스코어카드는 build-vs-buy / 벤더 선정 상황에 특화된 실무 도구다.
- **출처**: [Smartsheet 벤더 스코어카드](https://www.smartsheet.com/content/vendor-scorecards), [Nvelop RFP 스코어카드 템플릿](https://nvelop.ai/resources/templates/rfp-vendor-scorecard)

## 📊 종합 비교

| 프레임워크                       | 단계 수         | 원래 도메인          | 관계                       |
| -------------------------------- | ---------------- | --------------------- | -------------------------- |
| Blocker/Major/Minor (차용 표현)  | 3단계            | 버그 트래커(QA)       | 다른 도메인 용어를 차용   |
| MoSCoW                           | 4단계            | 요구사항 우선순위(애자일) | 가장 가까운 정식 대응 개념 |
| RFC 2119                        | 3단계(+금지형)   | 기술 표준 문서         | 두번째로 가까운 정식 대응  |
| Weighted Decision Matrix         | 자유(숫자 가중치) | 의사결정 이론 전반     | 표의 "정식 확장판"          |
| 벤더 평가 스코어카드              | 자유             | 조달·벤더선정 실무     | 가장 실용적인 완제품 도구   |

💡 **권장**: "필수/핵심/참고"라는 이름을 굳이 바꿀 필요는 없지만(의미는 이미 잘 통함), 다른 사람이 봤을 때 더 낯익게 하려면 **MoSCoW 어휘(Must/Should/Could)**로 라벨을 바꾸거나 "(MoSCoW 기법 응용)"이라고 각주를 다는 것이 좋다. 채점표를 실제로 채울 때는 3단계 라벨보다 **숫자 가중치(예: 필수=×3, 핵심=×2, 참고=×1) × 판정 점수**로 합산하는 Weighted Decision Matrix 방식으로 확장하면, "왜 A가 아니라 B인가"를 숫자로 방어할 수 있다.

## ⚠️ Edge Cases & Caveats

- Kano Model, RICE 스코어링은 검토했으나 **제품 기능의 고객가치 우선순위**용이라 지금 같은 "채택할지 말지"형 의사결정과는 결이 달라 이번 조사에서 제외했다.

## 📎 Sources

1. [Atlassian Community - Jira Priority 정의](https://community.atlassian.com/t5/Jira-questions/According-to-Jira-What-is-Blocker-Critical-Major-Minor-and/qaq-p/668774)
2. [Agile Business Consortium - MoSCoW 공식 설명](https://www.agilebusiness.org/resource/what-is-moscow-prioritization/)
3. [Wikipedia - MoSCoW method](https://en.wikipedia.org/wiki/MoSCoW_method)
4. [RFC 2119 원문 (IETF)](https://datatracker.ietf.org/doc/html/rfc2119)
5. [Lucid - Weighted Decision Matrix](https://lucid.co/blog/weighted-decision-matrix)
6. [Smartsheet - Vendor Scorecard 템플릿](https://www.smartsheet.com/content/vendor-scorecards)

## 배경 (원 대화 맥락)

이 조사는 세무 대리 서비스용 AI 에이전트를 LangGraph에서 Dify로 전환할지 검토하는 Notion 문서("Dify 도입 검토")에서, 평가 기준에 "필수(Blocker)/핵심(Major)/참고(Minor)"라는 3단계 중요도를 부여한 표현을 보고, 이게 일반적 표현인지와 이런 평가를 도와주는 도구가 있는지 확인하기 위해 수행했다.
