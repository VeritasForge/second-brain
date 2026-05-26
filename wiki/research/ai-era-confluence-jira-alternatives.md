---
tags: [confluence-alternatives, jira-alternatives, docs-as-code, ai-native-tools]
created: 2026-05-25
---

# 🤖 AI 시대 Confluence/JIRA 대체 — 조사·검증 종합 (도입 & 기여 가이드)

> **TL;DR**: ① 마크다운이 AI에 유리하다는 전제는 *대체로* 맞지만 흔한 수치는 과장됨. ② Confluence/JIRA를 마크다운·git·AI 네이티브로 대체하는 도구는 **이미 다수 존재** → 직접 만들 필요 없음. ③ 목적(Atlassian 탈출 + 회사 도입 + OSS 기여 + 학습)에 가장 정합적인 단일 경로는 **Forgejo(또는 Gitea) 도입 + MCP 서버 기여**. ④ AGPL(Plane·Docmost)은 회사 법무 확인 전까지 보류.

---

## 1️⃣ 출발 질문과 전제 검증 — "마크다운이 AI에 유리한가?"

질문: *"AI 시대엔 마크다운이 AI가 이해하기 좋은 언어다. Confluence/JIRA를 마크다운으로 대체한 툴이 있나? 없으면 만들려고 한다."*

전제부터 검증한 결과:

| 주장 | 검증 결과 | 확신도 |
| --- | --- | :---: |
| 마크다운이 HTML보다 토큰 효율적 (Cloudflare 80% 감소) | 수치 실재하나 **단일 블로그 1개 표본 + 기준선이 raw HTML(짚인형)**. 실무 정제 텍스트와는 격차 축소 | 🟡 [Likely] |
| 토큰 절감 = AI가 더 잘 이해 | ❌ **비약** (비용↔이해도는 다른 축, 통제 실험 없음) | ⚪ [Refuted] |
| llms.txt 채택 1년새 1,835% 증가 | ❌ **1차 출처 추적 실패** → 인용 금지 | ⚪ [Refuted] |

> 💡 **12살 비유**: 마크다운은 "택배에서 포장재를 뺀 편지"라 AI가 싸고 빠르게 읽습니다(맞음). 하지만 "싸게 읽는다 ≠ 더 정확히 이해한다". 표·의존성 같은 구조는 순수 텍스트에서 오히려 잃을 수 있어, 똑똑한 도구는 **마크다운 + DB 하이브리드**(예: Beads의 SQLite)를 씁니다. → "AI 친화"는 선택의 *한 축*이지 절대 기준이 아니며, 실무에선 **MCP/에이전트 지원 여부**로 구체화해야 합니다.

---

## 2️⃣ 대체재 지형 (위키 / 이슈 / 통합)

```
                Confluence (위키)        JIRA (이슈)          둘 다 (통합)
              ┌──────────────────┬──────────────────┬──────────────────────────┐
  성숙·기성   │ Wiki.js BookStack │  GitHub Issues   │ GitLab, Gitea, Forgejo,  │
              │ Outline  Docmost  │                  │ Fossil  (AI는 부착형)     │
              ├──────────────────┼──────────────────┼──────────────────────────┤
  AI-네이티브 │ (Karpathy식       │ Backlog.md(5.6k★)│ Plane(49k★,MCP 128tools) │
  신흥        │  LLM wiki 등장중) │ Beads(24k★)      │ Huly(26k★, Hulia AI)     │
              └──────────────────┴──────────────────┴──────────────────────────┘
```

---

## 3️⃣ 핵심 결론 1 — 대체재는 이미 존재한다 (원 조사 "빈 공간" 주장 정정)

원 조사는 "마크다운+AI 네이티브 통합 제품은 빈 공간"이라 결론냈으나, 검증에서 **부분 반증**됐습니다.

- ⚠️ **"위키+이슈+마크다운 통합"은 이미 존재**: **Fossil**(VCS+위키+티켓을 단일 바이너리, 공통 MD 인터프리터), **GitLab/Gitea/Forgejo**(MD 위키+MD 이슈+git).
- 남은 좁은 틈은 *"풀위키 + 풀이슈 + 순수MD + AI 네이티브"* **4박자 동시충족**뿐이고, 그조차 **Plane/Huly/Backlog.md가 빠르게 메우는 중**.

✅ **결론: 직접 빌드는 정당화되지 않습니다.** 통합의 90%는 *같은 git repo에 위키 폴더 + 이슈 폴더*로 공짜이고, 남는 빈틈은 해자가 없습니다.

---

## 4️⃣ 목적 정렬 — 빌드가 아니라 "도입 + 기여"

실제 목적:

> *"만드는 게 목적이 아니다. 대체할 게 있으면 → 학습해서 **회사에 도입** + **contributor로 활동**. 없으면 → 그때 만든다."* + 회사 현재 스택 = **Atlassian(Confluence/JIRA), 탈출 희망**.

```
대체할 도구가 있는가?
   ├─ YES (← 검증: 다수 존재) → 학습 + 회사 도입 + 기여  ✅ 여기
   └─ NO                      → 직접 빌드 (발동 안 함)
```

---

## 5️⃣ 후보 도구 심층 비교 (gh 실측, 2026-05)

| 도구 | ★ | 통합(위키+이슈) | AI 네이티브 | 셀프호스트 | 기여 친화 | 라이선스 |
| --- | ---: | :---: | :---: | :---: | :---: | --- |
| **Forgejo** | (Codeberg) | ⭕ +git | ❌(MCP 서드파티) | 🟢 단일 바이너리 | 🟢 비영리·GFI 있음 | GPL-3.0 |
| **Gitea** | 55.8k | ⭕ +git | ❌ | 🟢 단일 바이너리 | 🟢 개방 | MIT |
| **GitLab CE** | (자체) | ⭕ +CI | ⚠️ Duo **유료** | 🔴 무거움 | 🟡 | MIT(CE)/EE 혼재 |
| **Plane** | 49.6k | ⭕(위키 약함) | 🟢 **MCP 128 tools** | 🔴 10+ 컨테이너 | 🔴 **GFI 0**, top-3=45% | AGPL-3.0 |
| **Huly** | 26k | ⭕ +채팅 | ⚠️ Hulia 초기베타 | 🔴 **14 서비스** | 🔴 코어팀 독점 | EPL-2.0 |
| **Docmost** | 20.3k | ❌ 위키만(Confluence import) | 🟡 MCP(서드파티) | 🟡 | 🟡 CLA 필수 | AGPL+EE |
| **Backlog.md** | 5.6k | 절반(이슈+경량docs) | 🟢 **MCP 코어 내장** | 🟢 외부 DB X | 🟢 진입 쉬움 | MIT |

**검증된 핵심 사실**: Plane MCP = **128 tools/20 cat**(매우 강력), SSO 유료, good first issue **0**. Backlog.md는 MCP 코어 내장(#633 오픈)이나 **MrLesk 98.5% 솔로**(버스팩터 1). Huly **14개 서비스**(CockroachDB/Elasticsearch/MinIO/Redpanda)·AI는 영상 전사 수준.

> 🔑 **냉정한 사실**: **어떤 무료 도구도 "통합 + 강한 AI + 관대한 라이선스" 3박자를 다 주지 못합니다.** GitLab=AI 유료, Plane=AGPL+이슈편중, Huly=14서비스+기여폐쇄.

---

## 6️⃣ 라이선스 리스크 (회사 도입 결정 요인, 1차 출처 검증)

회사 AGPL 정책이 **미확인**이므로 이게 후보를 가릅니다.

| 순위 | 대상 | 라이선스 | 리스크 | 핵심 |
| :---: | --- | --- | :---: | --- |
| 🟢 1 | GitLab CE / Gitea | MIT | 낮음 | permissive. 단 GitLab은 `ee/` proprietary 혼재 → CE-only 빌드 확인 |
| 🟢 1 | Forgejo | GPL-3.0 | 낮음 | 사내 도입 자유 |
| 🟡 2 | Huly | EPL-2.0 | 중간 | **network 조항 없음**(SaaS 안전), file-level weak copyleft → AGPL보다 관대 |
| 🔴 3 | Plane / Docmost | AGPL-3.0 | 높음 | §13 network 조항 + **Google 등 대기업 공식 전면 금지**. Docmost는 +EE 유료+CLA |

> ⚠️ **AGPL §13**: 트리거 = *수정* AND *네트워크 사용자* 동시. 미수정 self-host는 미발동이나, "users" 범위가 회색지대 → **법무 검토 필수**.

---

## 7️⃣ 최종 추천 (정정본) — Forgejo 도입 + MCP 기여

> 💡 **협동조합 마트 비유**: 큰 마트(Plane/Huly)는 진열대를 못 바꾸고, 솔로 가게(Backlog.md)는 주인이 떠나면 닫힙니다. **Forgejo는 주민이 함께 운영하는 협동조합** — 물건(위키+이슈+git) 다 있고, 내가 새 매대(AI/MCP)를 직접 만들어 넣을 수 있습니다.

### 🥇 1순위: Forgejo (또는 Gitea)

| 이유 | 설명 |
| --- | --- |
| 통합 단일 도구 | 위키(Confluence)+이슈(JIRA)+git을 한 데이터모델에 → "통합" 욕구 충족 |
| permissive | GPL/MIT → **AGPL 법무 블로커 회피** |
| 기여=복리 | 비영리 거버넌스, GFI 운영, 외부 PR 머지 → **도입한 그 도구에 기여 = 운영지식=코드지식 복리** |
| AI 공백=기여 기회 | 네이티브 AI 없음 → **"Forgejo용 MCP 서버" 기여**가 곧 AI-era 학습 + 도입 도구 강화 (관심사와 정확히 일치) |
| 경량 | 단일 Go 바이너리 (Plane 10+/Huly 14서비스 대비 압도적) |

⚠️ **트레이드오프**: Forgejo 위키는 git+MD지만 **Confluence만큼 화려하진 않음**(매크로·템플릿 없음). AI는 "지금"이 아니라 "당신이 기여해 채우는" 형태.

### 대안 (우선순위가 다르면)

| 조건 | 추천 |
| --- | --- |
| 즉시 강한 AI 최우선 + **AGPL 법무 통과** | **Plane** (128 MCP tools, Jira importer). 위키 약함 |
| Confluence급 위키가 절대 요건 | Plane + **Docmost**(Confluence import) — *위키가 일급 시민인 조직*에만 (2개 운영은 과설계 주의) |
| 가장 안전·성숙 | **GitLab CE** (MIT, Jira importer, 통합) — 단 AI 유료 |
| 순수 학습용 기여(회사 무관) | Backlog.md — 단 솔로 메인테이너라 회사 의존 금지 |

---

## 8️⃣ 액션 플랜 (순서 중요)

1. **🔴 법무에 AGPL 정책 확인** (병렬) → 통과 시 AI 강한 Plane도 후보 부활.
2. **Forgejo 파일럿**: 단일 바이너리 셀프호스트 → Confluence 위키 1개 + JIRA 이슈 일부 이전해 감 잡기.
3. **첫 기여**: `good first issue` 1개로 워크플로우 익히기 + CONTRIBUTING 정독.
4. **🎯 핵심 기여(AI-era)**: Forgejo 코어에 **MCP 서버 RFC/구현** 제안 (현재 서드파티만 존재 = 빈틈). "도입 도구 강화 + AI 학습 + OSS 기여"를 한 번에.

---

## 9️⃣ 두 차례 검증이 바로잡은 것 (정정 이력)

| 단계 | 원안 | 정정 |
| --- | --- | --- |
| 1차 검증 | "통합형은 빈 공간" | Fossil/GitLab/Gitea 존재 → **부분 반증** |
| 1차 검증 | "토큰 80% → AI 친화" | 단일 사례·상관/인과 혼동 |
| 1차 검증 | Markplane 등 "폭발" | Markplane 169★(소규모), llms.txt 1835% 출처불명 |
| 2차 검증 | 도입=Plane+Docmost(2개) | **과설계**(운영 2배+AI 컨텍스트 분절) → 통합 단일 도구 |
| 2차 검증 | 기여=Backlog.md | **학습 비전이 + 버스팩터 1** → 도입 도구에 기여(복리) |
| 2차 검증 | GitLab "곁다리" | **정식 평가 누락**(alternative blindness) → 후보 승격 |
| 2차 검증 | AGPL "self-host OK" | **회사 정책 게이트 과소평가**(Google 금지) → 법무 우선 |
| 사실 정정 | Plane 기여자 "top 4-5 ~80%" | 실제 **top-3=45%** |

---

## 🔟 Sources & 확신도

- ✅ [Cloudflare — Markdown for Agents](https://blog.cloudflare.com/markdown-for-agents/) · [AGPL §13](https://www.gnu.org/licenses/agpl-3.0.txt) · [Google AGPL 금지](https://opensource.google/documentation/reference/using/agpl-policy) · [EPL-2.0](https://opensource.org/license/epl-2-0)
- ✅ [Forgejo Contributor Guide](https://forgejo.org/docs/v15.0/contributor/) · [Gitea](https://github.com/go-gitea/gitea) · [GitLab LICENSE](https://gitlab.com/gitlab-org/gitlab/-/raw/master/LICENSE)
- ✅ [Plane](https://github.com/makeplane/plane) · [Plane MCP(128 tools)](https://github.com/makeplane/plane-mcp-server) · [Huly](https://github.com/hcengineering/platform) · [Docmost](https://github.com/docmost/docmost) · [Backlog.md](https://github.com/MrLesk/Backlog.md)
- ⭐ [Fossil — Why All-in-One](https://www2.fossil-scm.org/fossil/doc/trunk/www/whyallinone.md)

**확신도**: ✅ Confirmed 다수(gh·1차출처 직접 확인) · 🟡 Likely(토큰 효율, GitLab AI 품질) · 🔄 Synthesized(정정 추천) · ❓ Uncertain(AGPL 법무·Confluence급 위키 요건 = 조직 의사결정) · ⚪ Refuted(토큰→이해도 인과, llms.txt 1835%)

**검증**: rl-verify 2회 — deep-research → 1차 검증(원 조사) → 도구 심층 비교 → 2차 검증(추가 조사) → 정정 추천.
