---
created: 2026-04-01
source: claude-code
tags: [claude-code, codex, openai, code-review, plugin, architecture]
---

# Codex Plugin for Claude Code — 종합 분석 (검증 완료)

> **검증 상태**: rl-verify Tier 2 수렴 검증 완료 (2026-04-01)
> **검증 방법**: CONTRARIAN (소스코드 대조 8건) + ARCHITECT (Hook 시스템 6건) + 수렴 2회전
> **결과**: 13개 항목 중 11건 CONFIRMED, 2건 경미한 수정 반영
> **관련 문서**: [[claude-code-hook-system]] — Hook System 배경 지식

---

## 1. 배경 지식: .mjs 확장자와 JavaScript 모듈 시스템

### 1.1 .mjs란?

| 확장자 | 의미                        | 모듈 시스템                  |
| ------ | --------------------------- | ---------------------------- |
| `.js`  | 일반 JavaScript             | 설정에 따라 다름             |
| `.mjs` | **M**odule **J**ava**S**cript | ESM (`import/export`)        |
| `.cjs` | **C**ommonJS **J**ava**S**cript | CommonJS (`require/exports`) |

Node.js는 파일 확장자를 보고 어떤 모듈 시스템으로 해석할지 결정한다. `.mjs`를 쓰면 `package.json`에 `"type": "module"` 없이도 ESM으로 동작한다.

💡 **비유**: 편지 봉투 색깔. 흰 봉투(.js) = 안을 봐야 앎, 파란 봉투(.mjs) = 무조건 ESM, 빨간 봉투(.cjs) = 무조건 CommonJS.

### 1.2 역사적 맥락: Babel+Webpack에서 네이티브 ESM으로

```
[2015] ES6(ES2015) 발표 — import/export 문법 표준화
   │  하지만 Node.js/브라우저가 아직 미지원
   ▼
[2015~2019] Babel + Webpack 시대
   import/export → Babel이 require로 변환 → Webpack이 번들링
   ▼
[2019] Node.js 12+에서 ESM 네이티브 지원
   변환 없이 import/export 직접 사용 가능!
   방법 1: .mjs 확장자 → 자동 ESM 인식
   방법 2: package.json에 "type": "module"
```

.mjs는 Webpack을 자동으로 해주는 게 **아니다**. Node.js에게 "이 파일은 ESM으로 해석해"라고 알려주는 확장자일 뿐이며, Webpack이 하던 변환 자체가 더 이상 필요 없어진 것이다.

### 1.3 CommonJS vs ES Modules

| 관점            | CommonJS (CJS)                  | ES Modules (ESM)                       |
| --------------- | ------------------------------- | -------------------------------------- |
| **탄생**        | 2009년, Node.js가 만듦          | 2015년, **ES6 표준**으로 제정          |
| **문법**        | `require()` / `module.exports`  | `import` / `export`                    |
| **로딩**        | **동기** — 파일 읽을 때까지 대기 | **비동기** — 미리 분석 후 로딩          |
| **실행 시점**   | require() 호출 시 바로 실행      | 모든 import 분석 완료 후 실행          |
| **동적 로딩**   | `require(변수)` 가능            | `import(변수)` 별도 문법               |
| **Tree-shaking** | ❌ 불가능                       | ✅ 가능 (정적 분석으로 안 쓰는 코드 제거) |
| **Top-level await** | ❌ 불가                     | ✅ 가능                                |
| **`__dirname`** | ✅ 사용 가능                    | ❌ 없음 (`import.meta.url` 사용)       |
| **JSON import** | `require('./data.json')` 가능   | `assert { type: "json" }` 필요         |
| **표준 여부**   | ❌ Node.js만의 규약             | ✅ ECMA-262 공식 표준 (ES6+)           |

💡 **비유**: CommonJS = 지역 방언(그 지역 Node.js에서만 통함), ESM = 표준어(어디서나 통함).

가장 실용적인 차이는 Tree-shaking:

```javascript
// CommonJS - 번들러가 뭐가 쓰이는지 모름
const lodash = require('lodash'); // 전체 lodash가 번들에 포함 (큼!)

// ESM - 번들러가 정확히 뭐가 쓰이는지 앎
import { debounce } from 'lodash'; // debounce만 번들에 포함 (작음!)
```

---

## 2. 플러그인 개요

| 항목         | 내용                                                                 |
| ------------ | -------------------------------------------------------------------- |
| **소스**     | github.com/openai/codex-plugin-cc                                    |
| **저자**     | OpenAI                                                               |
| **버전**     | 1.0.2 (2026-03-31 설치)                                             |
| **라이선스** | Apache 2.0                                                           |
| **요구사항** | ChatGPT 구독(Free 포함) 또는 OpenAI API 키, Node.js >= 18.18        |
| **목적**     | Codex CLI를 Claude Code 안에서 직접 사용 — 코드 리뷰, 태스크 위임, 적대적 리뷰 |

### 로컬 설치 경로

| 경로                                                    | 역할                     |
| ------------------------------------------------------- | ------------------------ |
| `~/.claude/plugins/cache/openai-codex/codex/1.0.2/`     | 설치된 플러그인 (캐시)   |
| `~/.claude/plugins/marketplaces/openai-codex/`           | 마켓플레이스 소스         |
| `~/.claude/plugins/data/codex-openai-codex/`             | 플러그인 데이터           |

---

## 3. 아키텍처

### 3.1 전체 구조

> ✅ **검증 완료**: app-server.mjs:189에서 `spawn("codex", ["app-server"])` 확인

```
[내 맥북]                                    [OpenAI 클라우드]
┌─────────────────────────┐                 ┌──────────────┐
│ codex app-server        │ ── HTTPS ──→    │ GPT 모델 API │
│ (로컬 프로세스)          │ ← 응답 ────    │ (실제 LLM)   │
└─────────────────────────┘                 └──────────────┘
     ↑
     │ Unix 소켓 (로컬 통신)
     │
┌─────────────────────────┐
│ Broker (교통 정리)       │
└─────────────────────────┘
     ↑
     │
┌────┴────────────────────┐
│ codex-companion (플러그인) │
│ - 포그라운드 명령         │
│ - 백그라운드 작업 워커     │
└─────────────────────────┘
```

`codex app-server`는 **내 컴퓨터에서 실행되는 로컬 프로세스**이고, 이 프로세스가 **OpenAI API를 호출**하여 실제 GPT 모델의 추론을 받아온다.

💡 **비유**: **은행 ATM 기계**. `codex app-server` = 내 동네 ATM(로컬), OpenAI 서버 = 은행 본점(클라우드).

### 3.2 사용된 패턴: Broker + Sidecar 조합

> 📌 "Companion-Broker 패턴"은 코드 구조를 보고 붙인 **설명적 레이블**. POSA, GoF 패턴 카탈로그에 등재된 공식 이름이 아니다.

**1) Broker 패턴** (POSA Vol.1 등재)

```
[클라이언트 A] ──┐
[클라이언트 B] ──┼──→ [Broker] ──→ [서버]
[클라이언트 C] ──┘
```

💡 **비유**: **부동산 중개인** — 여러 구매자가 직접 집주인에게 가지 않고 중개인을 통해 소통.

**2) Sidecar/Companion 패턴** (클라우드 네이티브 패턴)

```
[메인 프로세스: Claude Code] ←──→ [사이드카: codex-companion.mjs]
```

💡 **비유**: **오토바이 사이드카** — 오토바이(Claude)에 옆칸(Codex companion)을 달아 추가 짐을 실음.

### 3.3 JSON-RPC / Unix 소켓 / 멀티플렉싱

| 용어          | 의미                                               | 비유                     |
| ------------- | -------------------------------------------------- | ------------------------ |
| **Unix 소켓** | 같은 컴퓨터 안의 프로그램끼리 대화하는 통로          | 같은 건물 안의 내선 전화 |
| **JSON-RPC**  | JSON으로 "함수를 호출해줘"라고 요청하는 프로토콜     | 내선 전화의 대화 언어    |
| **브로커**    | 여러 발신자의 전화를 받아 한 수신자에게 연결          | 전화 교환원              |

JSON-RPC 예시:

```json
{"jsonrpc": "2.0", "method": "add", "params": [2, 3], "id": 1}
{"jsonrpc": "2.0", "result": 5, "id": 1}
```

멀티플렉싱:

```
❌ 멀티플렉싱 없이:
[포그라운드 리뷰] ──→ [Codex 서버 1]
[백그라운드 작업] ──→ [Codex 서버 2]  ← 서버 2개 필요!

✅ 멀티플렉싱 있음:
[포그라운드 리뷰] ──┐
                    ├──→ [브로커] ──→ [Codex 서버 1개]
[백그라운드 작업] ──┘
```

### 3.4 병렬 실행 제약과 BROKER_BUSY

> ✅ **검증 완료**: app-server-broker.mjs:69-71, 173-182

```javascript
// 단 1개의 활성 스트림만 허용
let activeStreamSocket = null;

// 바쁘면 즉시 에러 반환 (큐 아님)
send(socket, {
  id: message.id,
  error: buildJsonRpcError(BROKER_BUSY_RPC_CODE, "Shared Codex broker is busy.")
});
```

| 관점                | Claude Code                     | Codex (이 플러그인)               |
| ------------------- | ------------------------------- | --------------------------------- |
| **서브에이전트 병렬** | ✅ 여러 Agent 동시 실행 가능    | ❌ 브로커가 1개 스트림만 허용     |
| **바쁠 때**         | -                               | BROKER_BUSY 즉시 거절 (큐 없음)  |

---

## 4. 슬래시 커맨드 (7개)

### 4.1 커맨드 일람

| 커맨드                     | 기능                     | 주요 옵션                                                          |
| -------------------------- | ------------------------ | ------------------------------------------------------------------ |
| `/codex:setup`             | 설치/인증, 리뷰 게이트   | `--enable-review-gate`, `--disable-review-gate`                    |
| `/codex:review`            | 읽기 전용 코드 리뷰      | `--base <ref>`, `--wait`, `--background`                           |
| `/codex:adversarial-review` | 적대적 리뷰             | `--base <ref>`, `--wait`, `--background`, 포커스 텍스트            |
| `/codex:rescue`            | Codex에게 태스크 위임    | `--model`, `--effort`, `--resume`, `--fresh`, `--background`, `--write` |
| `/codex:status`            | 작업 상태 조회           | `--wait`, `--all`, 작업 ID                                        |
| `/codex:result`            | 완료 작업 결과 조회      | 작업 ID                                                           |
| `/codex:cancel`            | 백그라운드 작업 취소      | 작업 ID                                                           |

### 4.2 /codex:status 필드

| Field           | 의미                          | 값 예시                                     |
| --------------- | ----------------------------- | ------------------------------------------- |
| **Runtime**     | Codex 앱서버 연결 방식        | `direct startup` = 첫 명령 시 on-demand     |
| **Review gate** | Claude 종료 시 Codex 자동 리뷰 | `disabled` / `enabled`                      |
| **Jobs**        | 세션 내 작업 목록             | `None recorded yet` / 테이블                |

### 4.3 공통 옵션 상세

#### --base

> ✅ **검증 완료**: git.mjs:74-130 resolveReviewTarget

```
/codex:review --base abc123  → abc123부터 HEAD까지 diff 리뷰

옵션 미지정 시 (auto):
워킹 트리 dirty? ──→ YES → 워킹 트리 diff
                     NO  → 기본 브랜치(main/master)와의 diff
```

#### --wait / --background

| 옵션           | 동작                                     | 비유                     |
| -------------- | ---------------------------------------- | ------------------------ |
| (기본값)       | 포그라운드 실행, 결과까지 대기            | 카운터 앞에서 바로 받음  |
| `--wait`       | 백그라운드 + 2초마다 폴링 (최대 4분)      | 나오면 가져다 드릴게요   |
| `--background` | 분리된 워커, 즉시 job ID 반환             | 세탁기 돌려놓고 다른 일  |

### 4.4 /codex:review vs Claude 자체 리뷰

| 관점         | Claude Code 리뷰       | /codex:review                                |
| ------------ | ---------------------- | -------------------------------------------- |
| **수행자**   | Claude (Anthropic)     | Codex (OpenAI GPT)                           |
| **핵심 가치** | 같은 AI의 시각        | **다른 AI의 시각** ("세컨드 오피니언")        |
| **출력**     | 자유 형식              | JSON 스키마 (verdict, findings[], severity)   |

### 4.5 /codex:adversarial-review

| 관점       | /codex:review | /codex:adversarial-review                                |
| ---------- | ------------- | -------------------------------------------------------- |
| **태도**   | 중립적        | **적대적** — "안 괜찮은 이유를 찾아라"                    |
| **포커스** | ❌ 불가       | ✅ 가능 ("인증 부분 집중")                                |
| **공격 표면** | 일반적     | auth, 데이터 손실, race condition, 롤백, 스키마 드리프트  |

### 4.6 /codex:rescue

| 옵션                    | 의미                           |
| ----------------------- | ------------------------------ |
| `--write`               | Codex가 파일 직접 수정 (기본값) |
| `--model spark`         | gpt-5.3-codex-spark 사용       |
| `--effort high`         | 추론 노력 수준 (none~xhigh)    |
| `--resume` / `--fresh`  | 이전 작업 이어서 / 새로 시작    |
| `--background`          | 백그라운드 실행                 |

> ✅ **검증 완료**: `spark` → `gpt-5.3-codex-spark` (codex-companion.mjs:70)

### 4.7 /codex:result, /codex:cancel

`--background`와 직접 연관된 보조 커맨드:

```
/codex:review --background    → "Job ID: review-abc123"
/codex:status                 → 진행 상태 확인
/codex:result review-abc123   → 결과 조회
/codex:cancel review-abc123   → 작업 취소
```

💡 **비유**: **배달 앱**. background = 주문, status = 추적, result = 수령, cancel = 취소.

---

## 5. 리뷰 게이트 (Review Gate)

> Hook System의 상세 내용은 [[claude-code-hook-system]] 참조

### 5.1 동작 원리

> ✅ **검증 완료**: hooks.json:32에서 Stop 훅 timeout 900(15분) 확인

```
Claude 작업 완료 → Stop 이벤트
    │
    ▼
stop-review-gate-hook.mjs (command 타입, timeout: 900초)
    │
    ├─ config.stopReviewGate OFF → exit 0 → Claude 정상 종료
    │
    └─ config.stopReviewGate ON
         │
         ▼
    codex-companion.mjs task → Codex 앱서버 → Claude 마지막 응답 리뷰
         │
         ├─ "ALLOW:..." → exit 0 → Claude 종료 ✅
         └─ "BLOCK:..." → {"decision":"block","reason":"..."} → Claude 재작업 🔄
```

### 5.2 Fail-Closed 전략

> ✅ **검증 완료**: stop-review-gate-hook.mjs:69-139 모든 분기 확인

| 상황                                   | 결과       |
| -------------------------------------- | ---------- |
| ETIMEDOUT (15분 초과)                  | **block**  |
| exit status ≠ 0 (BROKER_BUSY 포함)     | **block**  |
| 유효하지 않은 JSON                     | **block**  |
| rawOutput 비어있음                     | **block**  |
| 첫 줄 `BLOCK:`                         | **block**  |
| 예상치 못한 응답                       | **block**  |
| 첫 줄 **`ALLOW:`**                     | ✅ **유일한 통과** |

💡 **비유**: **공항 보안 검색대**. 고장, 바쁨, 결과 못 읽음 → 모두 통과 불가. "OK"일 때만 통과. 보안 용어로 **"Fail-Closed"**.

### 5.3 토큰 소모 구조

```
Stop 훅 발동
    │
    ▼
stop-review-gate-hook.mjs  ← command 타입 (Claude 토큰 ❌)
    │
    ▼
codex-companion.mjs task   ← OpenAI API (OpenAI 토큰 ✅)
    │
    └─ BLOCK → Claude 재작업 ← Claude 토큰 ✅
```

⚠️ 피드백 루프가 수렴하지 않으면 Claude + OpenAI **양쪽 토큰이 동시에** 급증한다.

---

## 6. 내부 스킬 (3개, 사용자 호출 불가)

### 6.1 codex-cli-runtime

rescue 서브에이전트가 `codex-companion.mjs task`를 호출하는 **계약(contract)**. 핵심: **"포워더이지 오케스트레이터가 아님"**.

```
사용자: "이 버그 고쳐줘"
    ▼
[codex-rescue] ← 해석/직접 풀기 안 함
    ▼
node codex-companion.mjs task "이 버그 고쳐줘"
    ▼
[Codex 실행] → stdout → 그대로 반환 (요약/분석 없음)
```

### 6.2 codex-result-handling

- verdict/summary/findings 구조 보존, 심각도별 정렬
- **자동 수정 적용 금지** (반드시 사용자 확인)
- 실패 시 정직 보고 (대체 답변 생성 금지)

### 6.3 gpt-5-4-prompting

"Codex를 협력자가 아닌 운영자처럼 프롬프트하라."

| 참조 파일                     | 내용                                          |
| ----------------------------- | --------------------------------------------- |
| `prompt-blocks.md`            | 재사용 XML 프롬프트 블록 14개                  |
| `codex-prompt-recipes.md`     | 5가지 레시피 (진단, 수정, 리뷰, 연구, 패칭)    |
| `codex-prompt-antipatterns.md` | 피해야 할 안티패턴                             |

---

## 7. 에이전트: codex-rescue

> ✅ **검증 완료**: agents/codex-rescue.md:4에서 `tools: Bash` 확인

| 항목       | 내용                                                  |
| ---------- | ----------------------------------------------------- |
| **도구**   | Bash만                                                |
| **스킬**   | codex-cli-runtime, gpt-5-4-prompting                  |
| **역할**   | **Thin forwarding wrapper** — Claude 막힘 시 Codex 위임 |

**"Claude가 막혔다"**: 같은 실수 반복, 컨텍스트 부족, 다른 관점 필요, 복잡한 디버깅.

💡 **비유**: 수학 문제를 풀다 막혔을 때 옆자리 친구에게 "이거 좀 봐줘".

**"Thin forwarding wrapper"**: 소프트웨어 엔지니어링 표준 용어. 자체 로직 없이 요청을 그대로 전달하는 최소한의 코드. 반대는 "thick wrapper" 또는 "smart proxy".

---

## 8. 훅 (3개)

> ✅ **검증 완료**: hooks.json에서 확인. Hook System 상세는 [[claude-code-hook-system]] 참조

| 훅             | 타임아웃  | 역할                                |
| -------------- | --------- | ----------------------------------- |
| `SessionStart` | 5초       | 세션 ID 환경변수 설정               |
| `SessionEnd`   | 5초       | 브로커 종료, 고아 작업 정리          |
| `Stop`         | **15분**  | Codex가 Claude 턴 리뷰 (ALLOW/BLOCK) |

---

## 9. 리뷰 출력 스키마

```json
{
  "verdict": "approve | needs-attention",
  "summary": "리뷰 요약",
  "findings": [{
    "severity": "critical|high|medium|low",
    "title": "제목", "body": "설명",
    "file": "경로", "line_start": 10, "line_end": 20,
    "confidence": 0.85, "recommendation": "제안"
  }],
  "next_steps": ["다음 단계"]
}
```

---

## 10. 고유 워크플로우 (4가지)

| #  | 워크플로우          | 설명                                                        |
| -- | ------------------- | ----------------------------------------------------------- |
| 1  | **코드 리뷰**       | 변경사항 → Codex 리뷰 → 구조화 JSON → 심각도별 표시 → 결정  |
| 2  | **Rescue 위임**     | Claude 막힘 → codex-rescue 자동 발동 → Codex → 결과 반환    |
| 3  | **Stop Review Gate** | Claude 완료 → Stop 훅 → Codex 리뷰 → ALLOW/BLOCK 루프      |
| 4  | **백그라운드 관리**  | `--background` → job ID → status/result/cancel              |

---

## 11. 설계 원칙 요약

1. **엄격한 관심사 분리**: rescue 에이전트는 순수 포워딩만 (검사/풀기/후속 작업 금지)
2. **자동 수정 금지**: 리뷰 결과는 반드시 사용자 승인 후 적용
3. **선제적 위임**: Claude가 막히면 사용자 요청 없이 rescue 자동 발동 가능
4. **세션 범위 관리**: 모든 작업이 세션 ID에 바인딩, 종료 시 자동 정리
5. **Fail-Closed**: Review gate 에러 시 무조건 차단, ALLOW만 통과
6. **BROKER_BUSY 즉시 거절**: 큐 없이 바로 실패 응답
7. **Hook System 활용**: Claude Code의 결정론적 프레임워크로 플러그인 동작 보장

---

## 부록: 수렴 검증 결과

| #  | 항목                         | 판정           | 근거                             |
| -- | ---------------------------- | -------------- | -------------------------------- |
| 1  | BROKER_BUSY 즉시 거절        | ✅ CONFIRMED   | app-server-broker.mjs:173-182    |
| 2  | resolveReviewTarget auto     | ✅ CONFIRMED   | git.mjs:74-130                   |
| 3  | Fail-Closed 전략             | ✅ CONFIRMED   | stop-review-gate-hook.mjs:69-139 |
| 4  | 단일 스트림 강제             | ✅ CONFIRMED   | app-server-broker.mjs:69-71      |
| 5  | spark → gpt-5.3-codex-spark  | ✅ CONFIRMED   | codex-companion.mjs:70           |
| 6  | app-server 로컬 spawn        | ✅ CONFIRMED   | app-server.mjs:189               |
| 7  | Stop 훅 900s 타임아웃        | ✅ CONFIRMED   | hooks.json:32                    |
| 8  | rescue Bash only             | ✅ CONFIRMED   | codex-rescue.md:4                |
| 9  | Hook 이벤트 수               | 🔧 **수정됨** | 24개 → **25개** (공식 문서 기준)  |
| 10 | 토큰 사용 구분               | ✅ CONFIRMED   | 공식 문서 일치                   |
| 11 | Stop 훅 exit 코드            | ✅ CONFIRMED   | exit 2 = 종료 차단               |
| 12 | 4개 설정 스코프              | ✅ CONFIRMED   | +Managed(엔터프라이즈)           |
| 13 | 플러그인 발견 체인           | 🔧 **주석 추가** | installed_plugins.json 미문서화 |
