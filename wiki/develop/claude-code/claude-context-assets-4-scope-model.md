---
tags: [claude-code, claude-md, rules, skills, context-management, token-optimization]
created: 2026-05-13
---

# Claude Code 컨텍스트 자산: README.md / CLAUDE.md / Rules / Skills 완전 정리

> 모든 사실 주장은 [docs.claude.com/docs/en/memory.md](https://code.claude.com/docs/en/memory.md), [context-window.md](https://code.claude.com/docs/en/context-window.md), [skills.md](https://code.claude.com/docs/en/skills.md), [claude-directory.md](https://code.claude.com/docs/en/claude-directory.md) 공식 출처 검증 완료 (3차 수렴 검증).

---

## 1. 배경: 두 가지 흔한 오해

대규모 프로젝트에서 root에 단일 `CLAUDE.md`만 두는 관행이 사라졌는지, 그리고 새로 등장한 `.claude/rules/`가 nested CLAUDE.md를 대체했는지에 대한 혼동이 있습니다. 또 "사람용 vs AI용 이분법"으로 README.md와 CLAUDE.md를 나누는 것도 부정확합니다.

**결론 한 줄**: nested CLAUDE.md는 **deprecated 아니며**, Rules와 **직교(orthogonal) 관계**로 공존합니다. README.md/CLAUDE.md/Rules는 사람/AI 이분법이 아니라 **로드 메커니즘과 거버넌스 단위**로 분류되어야 합니다.

---

## 2. 4-Scope 모델

| Scope            | 메커니즘                                                    | 비유                                          |
| ---------------- | ----------------------------------------------------------- | --------------------------------------------- |
| **Always-on**    | `CLAUDE.md` (root + nested) + paths 없는 rule               | 교실 시간표 (자동 적용)                       |
| **Pattern-gated**| `.claude/rules/*.md` (paths frontmatter)                    | 교과서 펼칠 때 자동으로 끼워지는 포스트잇      |
| **On-demand**    | `.claude/skills/`, `.claude/agents/`                        | 도서관 책 목록에서 필요할 때 빌림             |
| **Enforcement**¹ | `.claude/hooks/`, `settings.json` (permissions)             | 교실 문 앞 보안 검색대                        |

¹ "Enforcement"는 본 문서의 분류 용어. 공식 docs는 permissions/hooks/settings로 분산 기술됨.

> **CLAUDE.md vs Rules**는 "같은 교실의 시간표 vs 자리 배치도" — 둘 다 적용되지만 시간 축 vs 공간 축 (직교).
> **AGENTS.md**는 "여러 학교가 합의한 공용 게시판 양식" — Claude Code가 자동 인식하지 않음, `@import`/symlink/`/init`로 우회.

---

## 3. 흔한 사실 오류 정정

| ❌ 오해                                                    | ✅ 공식 사실                                                                                                  |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| "더 깊은 규칙이 일반 규칙을 **override**한다"             | 모든 파일이 **concatenate**됨. 모순 시 LLM이 임의 판단                                                         |
| "AGENTS.md를 Claude Code도 인식한다"                       | **자동 인식 안 함**. 우회: ① `@AGENTS.md` import, ② symlink, ③ `/init`                                         |
| "메모리 로드 8단계 우선순위"                              | 실제는 **5계층** (Managed → User → Project → Local → Nested). 각 계층 안에서 `CLAUDE.md` + `.claude/rules/`는 **동시 로드** (sequential 아님) |
| "Rules가 nested CLAUDE.md의 상위 호환"                    | **직교(orthogonal)**. paths=공간 매칭, nested=시점 누적                                                       |
| "사람용 vs AI용 이분법"                                    | **3분법 + 공유 카테고리** (사람용 / AI용 / 공유: ADR, CONTRIBUTING)                                            |

---

## 4. 통합 자산 매트릭스 (14종)

| 카테고리              | 파일/경로                                                 | Scope                                       | 거버넌스 단위         |
| --------------------- | --------------------------------------------------------- | ------------------------------------------- | --------------------- |
| 사람용 진입점         | `README.md`                                               | (사람용)                                    | 프로젝트              |
| 사람+AI 공유          | `CONTRIBUTING.md`, `ARCHITECTURE.md`, `docs/adr/`         | CLAUDE.md `@import` 권장                    | 프로젝트              |
| AI 전역 지침          | `CLAUDE.md` (root)                                        | Always-on (launch 시)                       | 프로젝트              |
| AI 디렉토리 한정      | `src/CLAUDE.md` (nested)                                  | Pattern-gated (subdir 파일 read 시)         | 팀/도메인             |
| AI 패턴 한정          | `.claude/rules/*.md` (`paths` 있음)                       | Pattern-gated                               | 토픽                  |
| AI 토픽 모듈          | `.claude/rules/*.md` (paths 없음)                         | Always-on                                   | 토픽                  |
| 호출형 스킬           | `.claude/skills/`                                         | On-demand (description만 launch 로드)       | 토픽                  |
| 호출형 에이전트       | `.claude/agents/`                                         | On-demand                                   | 역할                  |
| Slash commands        | `.claude/commands/`                                       | On-demand (⚠️ 레거시 — skills로 통합 중)    | 워크플로              |
| 응답 형식             | `.claude/output-styles/`                                  | 모드 선택 시                                | 사용자                |
| 자동화 훅             | `.claude/hooks/`, `settings.json`                         | **Enforcement**                             | 보안/규제             |
| 부정형 컨텍스트       | `.gitignore`, `.claudeignore`                             | 파일 탐색 차단                              | 프로젝트              |
| 워크트리 파일 복사    | `.worktreeinclude`                                        | 워크트리 생성 시                            | 프로젝트              |
| MCP 서버 설정         | `.mcp.json` (project), `~/.claude.json` (user)            | 세션 launch                                 | 프로젝트/사용자       |
| Cross-tool 호환       | `AGENTS.md`, `GEMINI.md`, `.cursorrules`                  | Claude Code 자동 미인식                     | 표준                  |

---

## 5. 로딩 메커니즘 정밀 비교

### 5.1 CLAUDE.md 로딩

| 위치                                       | 로딩 시점                                          |
| ------------------------------------------ | -------------------------------------------------- |
| **root `CLAUDE.md`**                       | 세션 launch 시 로드                                |
| **nested `CLAUDE.md`** (예: `src/CLAUDE.md`) | **해당 subdirectory의 파일을 read할 때** 로드      |

> 공식 인용: *"Instead of loading them at launch, they are included when Claude reads files in those subdirectories."*

**중요**: 단순 폴더 진입(`cd`)이 트리거가 아니라 **파일 read 이벤트**가 트리거.

### 5.2 Rules 로딩

| Rule 종류              | 로딩 동작                                                               |
| ---------------------- | ----------------------------------------------------------------------- |
| `paths` **없음**       | launch 시 **frontmatter+body 전체** 로드 (= `.claude/CLAUDE.md`와 동일 우선순위) |
| `paths` **있음**       | body는 매칭 파일 read 시 로드 (on-demand)                                |

### 5.3 Skills vs Rules: 결정 주체의 차이

| 차원                          | Skills                                                          | Rules                                                                     |
| ----------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **누가 매칭/호출 결정?**      | LLM (Claude 자신)                                               | Claude Code **런타임/클라이언트**                                         |
| **frontmatter 노출**          | description이 LLM 컨텍스트에 미리 로드됨 (✅ 공식 명시)         | paths는 런타임 메타데이터로만 처리 (🟡 추론)                              |
| **트리거 조건**               | LLM이 description 보고 "이 스킬이 적합" 판단                    | 파일 접근 경로가 paths 패턴과 매칭 시 자동                                |
| **선택권**                    | LLM이 "안 부를 수도" 있음                                       | 매칭되면 **무조건** 로드 (조건부 의무)                                     |

#### Rules 동작 흐름

```
[세션 launch]
  런타임이 .claude/rules/ 스캔 → paths frontmatter를 메타데이터 인덱스로 구축
  (frontmatter 자체는 LLM 컨텍스트에 안 들어감)

[LLM이 작업 중 src/api/users.ts를 read]
  ↓
  런타임이 가로챔 → 인덱스에서 paths 매칭 검사
  "src/api/**/*.ts" 매칭? → YES
  ↓
  매칭된 rule의 body를 LLM 컨텍스트에 자동 주입
  ↓
  LLM은 "어, 새 지침이 들어왔네" 하고 인지
```

**즉 LLM은 paths를 본 적도 없고, 매칭 결정에 관여하지도 않음.**

---

## 6. 컨텍스트 잔존 모델 — 토큰 절약의 진짜 그림

### 6.1 한 번 로드된 Rule의 운명

| 시점                                  | Rules 컨텍스트 상태                                              |
| ------------------------------------- | ---------------------------------------------------------------- |
| 세션 launch                           | Rule body는 컨텍스트에 없음 (paths 없는 rule만 로드)             |
| 매칭 파일 첫 read                     | Rule body가 message history에 주입됨                              |
| 그 이후 turn들                        | **계속 누적되어 남아있음**                                        |
| **자동 compaction 발생**              | **❌ 제거됨** ("Lost until a matching file is read again")        |
| Compaction 후 다시 매칭 파일 read     | 다시 로드                                                         |

> 공식 인용: *"Path-scoped rules load into message history when their trigger file is read, so compaction summarizes them away with everything else."*

### 6.2 토큰 절약은 "시간 지연 로드"이지 "영구 제외"가 아님

```
[효과적인 시나리오]
  ✅ 세션 초기 launch — paths 없는 rule만 로드되어 시작 부하 ↓
  ✅ 단발성 작업 — 특정 영역만 만지고 끝나는 경우
  ✅ 모노레포 cross-team 격리 — 다른 팀 영역 안 건드리면 그 rule 로드 안 됨

[효과 약한 시나리오]
  ⚠️ 긴 세션 — 시간이 지날수록 만진 파일이 늘어 rule 누적
  ⚠️ 여러 영역 횡단 작업 — 결국 대부분 rule이 로드됨
  ⚠️ 같은 파일 반복 read — 중복 로드 가능성 (UNVERIFIED)
```

### 6.3 진짜 영구 토큰 절약 수단

1. **`.claudeignore` / `.gitignore`** — 부정형 컨텍스트 (파일 탐색 차단)
2. **Skills의 `disable-model-invocation: true`** — description조차 컨텍스트에 안 들어감
3. **root CLAUDE.md를 200줄 이하로 유지** — 가장 안정적인 토큰 절약 전략

> 공식 인용: *"Size: target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence."*

---

## 7. Nested CLAUDE.md 생존 이유 (7가지)

1. **하위 호환성** — 원래 메커니즘
2. **근접성**(편집 위치 인접) — "암묵적 스코프"의 정확한 명명
3. **계층 자동 누적** — 부모 → 자식 inheritance
4. **거버넌스/오너십 분산** — CODEOWNERS와 정렬, 팀이 자기 폴더만 수정
5. **다른 AI 도구 호환성** — Cursor/Aider도 nested 일부 인식, grep 친화적
6. **Git blame 추적성** — 코드와 가이드의 공진화를 같은 폴더에서 추적
7. **폴더 진입 컨텍스트 UX** — `cd services/payment` 같은 자연스러운 신호

⚠️ **단점**: 근접성은 양날의 검 — 위쪽 디렉토리 CLAUDE.md를 모두 확인해야 전체 컨텍스트 파악. Rules의 `paths`는 명시적이라 한눈 파악 가능.

---

## 8. 의사결정 가이드

### 8.1 시그널 → 자산 추천

| 시그널                                          | 추천 자산                                                                                                              |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| 단일 팀 + 단일 저장소                           | Nested CLAUDE.md만으로 충분                                                                                            |
| 모노레포 + 다중 팀                              | root CLAUDE.md(200줄↓) + 팀별 nested + cross-cutting `.claude/rules/` + `claudeMdExcludes`로 무관 팀 차단              |
| **보안/규제** (PCI/HIPAA/GDPR)                  | Rules + CODEOWNERS + **Hook 필수** (텍스트 가이드만으론 부족)                                                          |
| 멀티 AI 도구                                    | `AGENTS.md` 단일 진실 + CLAUDE.md/`.cursor/rules`에서 `@import`                                                        |

### 8.2 Hook이 필요한 신호 (텍스트 가이드 한계)

- 규제 준수 (PCI/HIPAA/GDPR — 우회 가능성 차단 필요)
- 비가역 작업 (DB drop, 프로덕션 배포)
- 비용 발생 작업 (외부 API 호출 비용)
- 시크릿/PII 노출 위험

### 8.3 마이그레이션 패턴 (단일 팀 → 보안/규제)

```
1. CLAUDE.md 200줄 초과 → 토픽별 .claude/rules/*.md로 분리 (paths 없음)
2. 토픽이 특정 영역에만 → paths frontmatter 추가 (토큰 절약 시작)
3. 팀 경계 = 폴더 경계 → 팀별 nested CLAUDE.md 도입
4. 보안/규제 요구 → Hook + CODEOWNERS 추가 (Enforcement 레이어)
```

---

## 9. Nested vs Rules 권장 (공식 입장)

| 사용자 추측                                | 공식 입장                                                                                                              |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| "nested는 하위 호환성으로 남아있되"        | ❌ **deprecated 아님**. 정상 권장 메커니즘                                                                              |
| "rules로 대체 가능"                         | 🟡 **기능적 일부만 맞음** — paths로 nested의 spatial 매칭은 재현 가능, 그러나 거버넌스/Git blame/cross-tool 호환은 nested 고유 |
| "어느 게 권장되나"                          | ✅ **상황별 둘 다 권장**. 강제 마이그레이션 없음                                                                         |

> 공식 인용: *"For larger projects, you can organize instructions into multiple files using the `.claude/rules/` directory... This keeps instructions modular and easier for teams to maintain."*

---

## 10. 핵심 사실 4가지 (모두 공식 CONFIRMED)

1. **`@import`는 토큰 절약 효과 없음** — launch 시 전부 로드. 진짜 절약은 `paths`-scoped rules와 nested CLAUDE.md(subdir 파일 read 시)와 Skills(description만 상주)뿐
2. **CLAUDE.md 200줄 초과 시 adherence 저하** — 공식 명시
3. **`claudeMdExcludes`** — 모든 settings 계층(user/project/local/managed)에서 glob 지원. ⚠️ Managed CLAUDE.md는 제외 불가 (조직 정책 강제)
4. **Skills의 `disable-model-invocation: true`** — description조차 context 로드 안 함 (수동 호출만)

---

## 11. 미해결 항목 (UNVERIFIED)

다음 두 항목은 공식 docs에서 침묵하고 있어 직접 테스트나 GitHub issue 문의가 필요합니다:

- 같은 rule이 여러 매칭 파일에서 read될 때 **중복 로드 여부**
- `/clear` 명령 시 로드된 rule 처리 방식
- Rules의 frontmatter 자체가 LLM 컨텍스트에 노출되는지 (정황상 안 됨, 명시 없음)

---

## Sources

- [How Claude remembers your project (memory.md)](https://code.claude.com/docs/en/memory.md)
- [Explore the context window (context-window.md)](https://code.claude.com/docs/en/context-window.md)
- [Skills (skills.md)](https://code.claude.com/docs/en/skills.md)
- [Explore the .claude directory (claude-directory.md)](https://code.claude.com/docs/en/claude-directory.md)
- [How Claude Code works (how-claude-code-works.md)](https://code.claude.com/docs/en/how-claude-code-works.md)
- [Settings (settings.md)](https://code.claude.com/docs/en/settings.md)
- [Output Styles (output-styles.md)](https://code.claude.com/docs/en/output-styles.md)
