---
created: 2026-04-01
source: claude-code
tags: [claude-code, hook, plugin, lifecycle]
---

# Claude Code Hook System

## 1. Hook이란?

Claude Code의 **생명주기 특정 시점에 자동 실행되는 사용자 정의 핸들러**. LLM이 "할까 말까" 판단하는 게 아니라 **무조건 결정론적으로 실행**된다.

💡 **비유**: 자동차의 **안전 센서** 시스템. 에어백(Hook) = 충돌(이벤트) 시 운전자 의지와 상관없이 무조건 작동. Claude(운전자)가 "에어백 안 터뜨릴게"라고 결정할 수 없다.

---

## 2. Hook 이벤트 (25개)

> 📌 공식 문서 기준 25개 이벤트 확인 (rl-verify 검증 완료)

```
[세션 시작]                [작업 중]                    [세션 종료]
┌────────────┐      ┌─────────────────┐          ┌──────────────┐
│SessionStart│      │ PreToolUse      │          │ Stop         │
│            │  →   │ PostToolUse     │   →      │ SessionEnd   │
│            │      │ UserPromptSubmit│          │              │
└────────────┘      └─────────────────┘          └──────────────┘
```

| 단계     | 이벤트                          | 설명                         |
| -------- | ------------------------------- | ---------------------------- |
| 시작     | `SessionStart`                  | 세션 시작/재개 시            |
| 시작     | `InstructionsLoaded`            | CLAUDE.md 등 로딩 시         |
| 시작     | `UserPromptSubmit`              | 사용자 프롬프트 제출 시      |
| 작업 중  | `PreToolUse`                    | 도구 실행 **전** (차단 가능) |
| 작업 중  | `PermissionRequest`             | 권한 다이얼로그 시           |
| 작업 중  | `PostToolUse`                   | 도구 실행 **후**             |
| 작업 중  | `PostToolUseFailure`            | 도구 실행 실패 후            |
| 작업 중  | `SubagentStart/Stop`            | 서브에이전트 시작/종료       |
| 작업 중  | `TaskCreated/Completed`         | 태스크 생성/완료             |
| 종료     | **`Stop`**                      | Claude 응답 완료 시          |
| 종료     | `StopFailure`                   | API 에러로 턴 종료 시        |
| 종료     | `TeammateIdle`                  | 팀 에이전트 유휴 시          |
| 종료     | `PreCompact/PostCompact`        | 컨텍스트 압축 전/후          |
| 종료     | `SessionEnd`                    | 세션 종료 시                 |
| 비동기   | `Notification`                  | 알림 발생 시                 |
| 비동기   | `ConfigChange`                  | 설정 파일 외부 변경 시       |
| 비동기   | `CwdChanged`                    | 작업 디렉토리 변경 시        |
| 비동기   | `FileChanged`                   | 감시 파일 변경 시            |
| 비동기   | `WorktreeCreate/Remove`         | 워크트리 생성/제거 시        |
| 비동기   | `Elicitation/ElicitationResult` | MCP 서버 사용자 입력 요청/응답 |

---

## 3. Hook의 입출력 모델

```
Claude Code 이벤트 발생
    │
    ▼
[Hook 스크립트에 JSON을 stdin으로 전달]
    │  {
    │    "session_id": "abc123",
    │    "cwd": "/workspace",
    │    "hook_event_name": "Stop",
    │    "last_assistant_message": "작업 완료했습니다..."
    │  }
    │
    ▼
[Hook 스크립트 실행]
    │
    ├─ exit 0            → ✅ 허용 (진행)
    ├─ exit 2 + stderr   → ❌ 차단 (stderr가 Claude에게 피드백)
    └─ stdout JSON       → 구조화된 결정 전달
       {"decision":"block","reason":"이유"}
```

> Stop 이벤트에서 exit 2 = "종료를 차단" = Claude가 계속 작업 (검증 완료)

💡 **비유**: **학교 알림장 시스템**. 선생님(Claude Code)이 알림장(JSON)을 학생(Hook)에게 줌 → 부모님(스크립트 로직) 확인 → 도장(exit 0) = 통과, 빨간 X(exit 2) = 차단.

---

## 4. Hook 핸들러 타입 (4가지)과 토큰 사용

> ✅ 토큰 사용 구분 검증 완료

| Hook 타입     | Claude 토큰 사용 | 설명                                      |
| ------------- | :--------------: | ----------------------------------------- |
| **command**   |        ❌        | 셸 스크립트 실행. Claude API 호출 없음     |
| **http**      |        ❌        | 외부 HTTP 엔드포인트 호출. Claude와 무관   |
| **prompt**    |        ✅        | Claude에게 단일턴 질문. Claude 토큰 소모   |
| **agent**     |        ✅        | Claude 서브에이전트 (다중턴). 토큰 소모    |

💡 **비유**: command/http = **자비로 출장** (회사 경비 안 씀), prompt/agent = **회사 법인카드로 출장** (Claude 토큰 사용).

---

## 5. Hook 설정 — 4개 출처 (+1)

> ✅ 4개 스코프 검증 완료 (엔터프라이즈 Managed 스코프 추가로 총 5개)

| 출처      | 파일 경로                        | 용도                                |
| --------- | -------------------------------- | ----------------------------------- |
| 글로벌    | `~/.claude/settings.json`        | 모든 프로젝트에 적용 (직접 설정)    |
| 프로젝트  | `.claude/settings.json`          | 해당 프로젝트만 (팀 공유)           |
| 로컬      | `.claude/settings.local.json`    | 내 머신만 (gitignore)               |
| 플러그인  | `plugin/hooks/hooks.json`        | 플러그인이 자동 등록                |
| (Managed) | 엔터프라이즈 정책                | 관리자 설정                         |

설정 예시:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{
          "type": "command",
          "command": "prettier --write",
          "timeout": 30
        }]
      }
    ]
  }
}
```

---

## 6. 플러그인 Hook 발견 방법

> 📌 `installed_plugins.json`은 실제 존재하지만 **공식 문서에 미기재된 구현 상세**이다. 내부 구현이므로 버전 간 변경 가능성이 있다.

```
[1] ~/.claude/plugins/installed_plugins.json  ← ⚠️ 미문서화 구현 상세
    "어떤 플러그인이 설치되어 있는가?"
         │
         ▼
[2] ~/.claude/settings.json → enabledPlugins
    "이 플러그인이 활성화되어 있는가?"
         │
         ▼
[3] 해당 플러그인의 hooks/hooks.json
    "이 플러그인이 어떤 훅을 등록했는가?"
```

공식 문서에서는 플러그인 활성화 시 해당 플러그인의 hooks가 자동으로 사용 가능해진다고만 설명한다.

💡 **비유**: **회사 출입카드 시스템**.
1. **인사팀 명부** = 누가 등록돼 있는지
2. **출입 권한 설정** (`enabledPlugins`) = 누구에게 카드 활성화했는지
3. **각 부서의 보안 규칙** (`hooks.json`) = 각 부서가 어떤 이벤트에 반응할지

이벤트 발생 시 해당 이벤트에 등록된 모든 훅이 실행되며, **하나라도 block이면 전체 차단**된다.
