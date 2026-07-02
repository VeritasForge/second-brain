---
created: 2026-07-01
source: claude-code
tags:
  - claude-code
  - skills
  - environment-variables
  - settings-json
  - best-practices
  - hardcoding-anti-pattern
---

# Claude Code 스킬에서 경로·설정을 환경변수로 빼는 표준 방법

Claude Code 스킬(SKILL.md)에서 vault 경로 같은 값을 하드코딩하지 않고 파라미터화하는 방법을 조사·정리한 노트. `save-obsi` 스킬을 이 방식으로 리팩터링한 사례를 포함한다.

## 핵심 결론

| 질문 | 답변 |
| --- | --- |
| SKILL.md 본문에서 환경변수가 네이티브로 치환되나? | ❌ **아니오**. 마크다운 텍스트의 `$VAR`는 리터럴 문자열로 남는다 (스킬은 실행 스크립트가 아니라 LLM 지시문이므로). |
| 그럼 어떻게 env를 쓰나? | 스킬이 **Bash를 실행해 `$VAR`를 읽게** 해야 한다. |
| 권장 파라미터화 방식은? | **settings.json `env` 블록에 정의 → 스킬이 Bash로 읽기 → 폴백 기본값** 조합. |
| 이게 de facto standard인가? | ✅ **예**. 공식 문서 권장, 하드코딩은 anti-pattern으로 인식됨. |

## 왜 마크다운 텍스트의 `$VAR`는 확장되지 않나

스킬(SKILL.md)은 셸이 실행하는 스크립트가 아니라 **LLM에게 주입되는 지시문(마크다운)**이다. 따라서 본문에 `$OBSIDIAN_VAULT`라고 써도 셸 확장이 일어나지 않고 문자열 그대로 모델에 전달된다. 실제 값으로 쓰려면 모델이 Bash 도구를 호출해 환경변수를 읽어야 한다.

> ⚠️ 신뢰도 메모: `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}` 같은 특수변수 목록도 조사에서 언급됐으나 1차 출처로 완전 확증하지 못했다. **확실히 검증된 경로는 "settings.json `env` → 프로세스 환경변수 주입 → Bash 도구에서 `$VAR`로 읽힘"** 이므로, 이 경로에만 의존하는 설계를 택하는 것이 안전하다.

## 파라미터화 방식 비교

| 방식 | 평가 |
| --- | --- |
| settings.json `env` 블록에 정의 → 스킬이 Bash로 읽음 | ✅ **표준·권장**. 여러 스킬이 공유, 로컬/전역 오버라이드 가능. |
| 스킬 지시문이 매번 env를 읽게만 함 (settings 없이) | ⚠️ 폴백 기본값과 결합하면 유효. env 미설정 시 기본값으로 동작. |
| 스킬 폴더 안 config.json을 Read | ⚠️ 가능하나 비표준, 스킬마다 제각각. |
| slash command 인자(`$ARGUMENTS`)로 전달 | ✅ "이번 호출만 다른 경로"에 적합 (영구 설정용은 아님). |

## 권장 설계 — 환경변수 + 폴백 (backward compatible)

핵심은 **환경변수를 읽되, 없으면 기본값으로 폴백**하는 것. 이러면 settings.json을 안 건드려도 지금처럼 동작하고, 경로를 옮길 때 env만 바꾸면 된다.

```bash
VAULT_ROOT="${OBSIDIAN_VAULT:-$HOME/lab/second-brain}"
if [ ! -d "$VAULT_ROOT" ]; then
  echo "ERROR: Obsidian vault를 찾을 수 없음 → $VAULT_ROOT"
  echo "→ ~/.claude/settings.json 의 env 블록에 OBSIDIAN_VAULT 를 설정하세요."
  exit 1
fi
echo "$VAULT_ROOT"
```

| 상황 | 동작 |
| --- | --- |
| `OBSIDIAN_VAULT` 설정됨 | 그 경로를 vault root로 사용 |
| 미설정 | `~/lab/second-brain`으로 폴백 (설정 없이도 동작) |
| vault 경로 자체가 없음 | 에러 + 안내 출력 후 중단 |

## (선택) settings.json에 영구 오버라이드

```json
{
  "env": {
    "OBSIDIAN_VAULT": "/Users/jaeyoungcho/lab/second-brain"
  }
}
```

> 💡 `env` 값은 Bash 도구로 넘어갈 때 `~` 자동확장이 보장되지 않으니 **절대경로**로 쓴다. (스킬 내부 폴백은 `$HOME`을 쓰므로 안전)

## 참고 출처

- [Claude Code skills documentation](https://code.claude.com/docs/en/skills.md)
- [Claude Code settings](https://code.claude.com/docs/en/settings.md)
- [GitHub issue #22902 — custom skills directory paths via env var](https://github.com/anthropics/claude-code/issues/22902)
- [GitHub issue #33501 — support environment variables in claude settings](https://github.com/anthropics/claude-code/issues/33501)
