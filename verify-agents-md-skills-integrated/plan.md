# 수렴 검증 플랜

## 대상
`/Users/cjynim/den/Den/ai-engineering/agents-md-effect-on-known-tech-stacks.md`
— Deep Research 3회 + 수렴 검증 + Q&A 2회를 하나로 통합한 28.4KB 문서

## 이전 검증 이력
이 문서의 **Part 2.3 수렴 검증 결과**(항목 1-8)는 이전 대화에서 이미 수렴 검증(Tier 3, 5관점, 5 iterations)을 거쳤다.
→ 기존 검증 결과: `verify-skill-invocation-agents-md/report.md`

이번 검증은 **통합 과정에서 발생한 왜곡/누락/과장** + **새로 추가된 콘텐츠의 정합성**에 집중한다.

## Tier
Tier 3 — 외부 사실 확인 필요 + 합성 결론 포함 + 기술 의사결정에 영향

## 검증 항목
| # | 항목 | 검증 방법 | 사용 Agent/Skill |
|---|------|----------|-----------------|
| 1 | ETH Zurich 수치 정확성: -0.5%, +4%, -2.7%, +20% 비용 증가 | 원문(arXiv:2602.11988) WebFetch 대조 | RESEARCHER |
| 2 | Vercel 수치 정확성: 53%, 79%, 100%, +47pp, 8KB index | 원문(vercel.com/blog) WebFetch 대조 | RESEARCHER |
| 3 | 통합 과정 왜곡 검사: 기존 검증 report.md의 판정(DEBUNKED, OVERSTATED 등)이 통합 문서에 정확히 반영되었는가? | 기존 report.md vs 통합 문서 비교 | ARCHITECT |
| 4 | Q&A 근거 정합성: Q1-Q8 답변이 원본 리서치/검증 결과와 일치하는가? | 원본 vault 문서 대조 | ARCHITECT |
| 5 | 실무 권장사항 논리적 건전성: 권장사항이 근거에서 논리적으로 도출되는가? (서술적→규범적 비약 없는가?) | 논리 분석 | CONTRARIAN |
| 6 | Augment Code "해롭다" 관점의 정확성: "Your CLAUDE.md Is Making Your Agent Dumber" 원문 확인 | WebFetch 대조 | RESEARCHER |
| 7 | 확신도 태그 적절성: [High], [Medium], [Uncertain] 부여가 근거에 부합하는가? | 교차 검증 | CONTRARIAN + ARCHITECT |
| 8 | 누락 검사: 원본 리서치에 있었으나 통합 과정에서 빠진 중요 정보가 있는가? | 원본 문서 vs 통합 문서 비교 | SIMPLIFIER |

## 검증 관점 및 Agent 할당
| 관점 | 역할 | 사용 Agent/Skill | 필수 여부 |
|------|------|-----------------|----------|
| 출처 정확성 | RESEARCHER | general-purpose + WebFetch | 필수 (Tier 3) |
| 반론 구성 | CONTRARIAN | ouroboros:contrarian | 필수 |
| 구조적 건전성 | ARCHITECT | architecture-strategist | 권장 |
| 누락/과잉 분석 | SIMPLIFIER | ouroboros:simplifier | 권장 |
| 종합 판정 | EVALUATOR | ouroboros:evaluator | 필수 |

## Agent별 상세 프롬프트

### 관점 1: 출처 정확성 (RESEARCHER)
- Agent: general-purpose
- 프롬프트: 다음 주장에 대해 원문(WebFetch)을 직접 확인하고, 통합 문서에서 인용한 수치/표현이 원문과 정확히 일치하는지 대조하라.
  1. ETH Zurich arXiv:2602.11988: SWE-bench Lite에서 LLM 생성 context file -0.5%, AGENTbench에서 사람 작성 +4%, LLM 생성 -2.7%, 비용 +20%
  2. Vercel blog: No docs 53%, Agent Skill 53%, Skill+explicit 79%, AGENTS.md 100%, 8KB index
  3. Augment Code blog: "Your CLAUDE.md Is Making Your Agent Dumber" 기사의 실제 주장 확인
  4. 논문 원문 인용 2건이 원문과 정확히 일치하는지

### 관점 2: 반론 구성 (CONTRARIAN)
- Agent: ouroboros:contrarian
- 프롬프트: 통합 문서의 핵심 결론에 대해 반론을 구성하라:
  - "학습 데이터 포함 여부가 핵심 변수"라는 주장의 약점은?
  - "LLM 생성 context file은 일관되게 성능 저하"가 과도한 일반화인가?
  - 실무 권장사항 중 근거가 부족한 것은?
  - 확신도 태그 중 과대/과소 부여된 것은?

### 관점 3: 구조적 건전성 (ARCHITECT)
- Agent: architecture-strategist
- 프롬프트: 다음을 검토하라:
  - 기존 수렴 검증 report.md의 판정(DEBUNKED, OVERSTATED, CONFIRMED 등 8개)이 통합 문서에 정확히 반영되었는가?
  - Q&A 답변이 원본 리서치 및 검증 결과와 모순되는 부분이 있는가?
  - 서술적 주장에서 규범적 주장으로의 비약이 있는가?

### 관점 4: 누락/과잉 분석 (SIMPLIFIER)
- Agent: ouroboros:simplifier
- 프롬프트: 다음을 검토하라:
  - 원본 리서치 3개(skill-invocation, AI씬반응, 기술스택효과)에 있었으나 통합에서 빠진 중요 정보는?
  - 불필요하게 반복되거나 과잉 기술된 부분은?
  - 더 단순한 구조로 동일한 가치를 전달할 수 있는가?

### EVALUATOR
- Agent: ouroboros:evaluator
- 프롬프트: 위 4개 관점 Agent들의 출력을 종합하여 각 발견사항(8개 항목)에 판정 라벨을 부여하라. 안정 카운터를 초기화하라.

## EVALUATOR 판정 기준
| 라벨 | 조건 |
|------|------|
| CONFIRMED | 다수 agent 동의 + 외부 근거 존재 |
| LIKELY | 다수 agent 동의, 외부 근거 미확인 |
| CONTESTED | Agent 간 의견 분열 (핵심 이견 명시) |
| REFUTED | 다수 agent 반대 또는 외부 근거가 반박 |
| UNGROUNDED | 외부 검증 불가 + 자기 참조만 존재 |

## 안정 카운터 업데이트 규칙
- EVALUATOR 판정이 이전과 동일 → 안정 카운터 +1
- EVALUATOR 판정이 이전과 다름 → 안정 카운터 = 0
- 신규 발견 → 안정 카운터 = 0, "신규" 표시
  + 기존 합의 항목에 영향 시 해당 항목 안정 카운터 리셋
- CONTESTED → 다음 iteration에서 제3 관점 투입
- 이전 발견이 이번에 없음 → "취소 후보", 안정 카운터 = 0

## 수렴 판정 기준
- Tier 3: 모든 발견사항의 안정 카운터 >= 3 (EVALUATOR 판정 3회 연속 동일)
- 새로운 발견 0건
- CONTESTED 항목 0건

## 리포트 갱신 형식

### Iteration별 갱신
| # | 항목 | EVALUATOR 판정 | 신뢰도 | 근거 요약 | 안정 카운터 |
|---|------|---------------|--------|----------|-------------|

### 최종 리포트
#### 확정된 발견사항 (안정 카운터 >= 3)
| # | 심각도 | 내용 | 판정 라벨 | 검증 관점 | 안정 카운터 | 확정 iteration |

#### 취소된 발견사항 (재검증으로 부정됨)
| # | 내용 | 취소 사유 | 취소 관점 | iteration |

#### Orchestration 기록
| 관점 | 역할 | 사용 Agent/Skill | 담당 항목 |

## 완료 기준
- [ ] 모든 발견사항의 안정 카운터 >= 3
- [ ] 새로운 발견 0건
- [ ] CONTESTED 항목 0건

## 하지 말 것
- 검증 대상 문서를 수정하지 마
- 추측으로 수렴했다고 판단하지 마 — 실제 비교 근거 필요
- subagent를 background로 실행하지 마
- 수렴하지 않았는데 COMPLETE를 출력하지 마
