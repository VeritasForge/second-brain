---
tags: [ghostty, terminal, font-config, macos, dotfiles, claude-code]
created: 2026-07-12
---

# Ghostty 터미널 폰트 설정

## 결론

Claude Code CLI (Command Line Interface, 명령줄 인터페이스) 자체에는 폰트를 지정하는 설정이 없다. 폰트는 Claude Code가 아니라, Claude Code를 실행하는 **터미널 에뮬레이터** — 여기서는 Ghostty — 가 담당한다.

Ghostty는 설정 파일이 **키-값 텍스트 형식**이라 JSON/YAML 문법 없이 간단하다.

## 1. 설정 파일 열기

| 방법 A (GUI 단축키) | 방법 B (직접 편집) |
|---|---|
| `Cmd + ,` (없으면 자동 생성) | `~/.config/ghostty/config` 텍스트 에디터로 열기 |

> ⚠️ macOS 주의사항: 과거 버전에서 만들어진 `~/Library/Application Support/com.mitchellh.ghostty/config` 파일이 남아있으면 `Cmd+,`가 그쪽을 열 수 있다. 폰트를 바꿔도 적용 안 되면 이 파일을 지우고 `~/.config/ghostty/config`만 남길 것.

## 2. 폰트 설정 추가

```
font-family = JetBrains Mono
font-size = 14
```

- `font-family`는 **줄을 반복해서 여러 개 지정**하면 fallback(대체) 폰트로 동작한다 — 첫 번째 폰트에 없는 문자는 다음 줄 폰트로 자동 대체된다.

```
font-family = JetBrains Mono
font-family = Apple Color Emoji
```

- 따옴표는 선택사항: `font-family = "JetBrains Mono"` 도 동일하게 동작.

## 3. 설치된 폰트 이름 확인

```bash
ghostty +list-fonts
```

정확한 폰트 이름(패밀리명)을 확인한 뒤 그대로 `font-family` 값에 넣는다.

## 4. 적용하기

파일 저장 후 **`Cmd + Shift + ,`** 로 실시간 리로드된다 (터미널을 껐다 켤 필요 없음). 단, 이미 수동으로 폰트 크기를 조절한 적 있는 탭은 그 조절값을 유지한다.

## 추가 팁

| 상황 | 해결책 |
|---|---|
| Claude Code의 아이콘/박스 문자가 깨짐 | 일반 폰트가 아니라 **Nerd Font**(글리프 포함 폰트, 예: `JetBrainsMono Nerd Font`)로 지정 |
| 설정 파일 없이 한 번만 테스트하고 싶음 | `ghostty --font-family="JetBrains Mono"` 처럼 CLI 플래그로 임시 실행 |
| 고해상도(Retina) 디스플레이에서 폰트가 애매하게 보임 | `font-size`에 소수점(예: `13.5`) 지정 가능 — 1pt=2px 환경에서 홀수 픽셀 크기 조정용 |

## 참고

- [Option Reference - Configuration](https://ghostty.org/docs/config/reference)
- [Configuration](https://ghostty.org/docs/config)
- [macOS: Ghostty should open the user defined config file from settings menu · ghostty-org/ghostty · Discussion #5516](https://github.com/ghostty-org/ghostty/discussions/5516)
