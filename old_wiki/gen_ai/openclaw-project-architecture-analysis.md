---
created: 2026-02-09
source: claude-code
tags:
  - project-analysis
  - ai-assistant
  - multi-channel
  - typescript
---

# OpenClaw 프로젝트 분석 보고서

## 1. 프로젝트 개요

**OpenClaw**은 **개인용 AI 어시스턴트 플랫폼**으로, 사용자가 이미 사용하고 있는 다양한 메시징 채널(WhatsApp, Telegram, Slack, Discord, Google Chat, Signal, iMessage, Microsoft Teams, WebChat 등)을 통해 AI 어시스턴트와 상호작용할 수 있게 하는 **멀티채널 AI 게이트웨이**입니다.

- **버전**: 2026.2.6-3
- **라이선스**: MIT
- **런타임**: Node.js >=22
- **패키지 매니저**: pnpm (monorepo)
- **언어**: TypeScript (ESM)

---

## 2. 아키텍처

### 2.1 핵심 아키텍처: Gateway 패턴

```
┌─────────────────────────────────────────────────────────┐
│                    사용자 (User)                          │
│ WhatsApp / Telegram / Slack / Discord / Signal / iMessage │
│ Google Chat / MS Teams / WebChat / Matrix / Zalo / etc.  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Gateway Server                          │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌─────────────┐  │
│  │WebSocket │ │ HTTP API │ │OpenAI  │ │  Channel    │  │
│  │ Server   │ │ (Hono)   │ │compat  │ │  Adapters   │  │
│  └──────────┘ └──────────┘ └────────┘ └─────────────┘  │
│                                                          │
│  ┌───────────────────────────────────────────────────┐   │
│  │         Agent (Pi Embedded Runner)                │   │
│  │  System Prompt = Skills + Hooks + Identity        │   │
│  │  Tools: bash, web, browser, canvas, memory,      │   │
│  │         sessions, image, TTS, message, cron...    │   │
│  │  Multi-model failover (auth profile rotation)     │   │
│  └───────────────────────────────────────────────────┘   │
│                                                          │
│  ┌────────┐ ┌──────────┐ ┌────────┐ ┌──────────────┐   │
│  │Memory  │ │Sessions  │ │ Cron   │ │  Plugins     │   │
│  │(Vector)│ │(Persist) │ │(Sched) │ │ (Extensions) │   │
│  └────────┘ └──────────┘ └────────┘ └──────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Native Apps (Nodes)                         │
│  ┌───────┐ ┌──────┐ ┌─────────┐ ┌──────────────────┐   │
│  │ macOS │ │ iOS  │ │ Android │ │ TUI (Terminal)   │   │
│  └───────┘ └──────┘ └─────────┘ └──────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 2.2 핵심 설계 원칙

1. **Gateway = Control Plane**: Gateway는 제어 평면, 실제 제품은 어시스턴트 자체
2. **Single User**: 개인용 단일 사용자 어시스턴트
3. **Channel Agnostic**: 어떤 채널에서든 동일한 AI 어시스턴트와 대화
4. **Plugin Architecture**: 채널과 기능을 플러그인으로 확장 가능
5. **Multi-Model Failover**: 다양한 AI 모델 지원 + 자동 fallback

---

## 3. 디렉토리 구조

```
openclaw/
├── src/                  # 핵심 소스 코드 (TypeScript)
│   ├── gateway/          # Gateway 서버 (WS + HTTP + Protocol)
│   ├── agents/           # AI Agent 엔진 (Pi Embedded Runner)
│   ├── channels/         # 채널 공통 로직
│   ├── cli/              # CLI 명령어 (Commander.js)
│   ├── commands/         # 명령어 구현체 (onboard, doctor 등)
│   ├── config/           # 설정 시스템 (Zod 스키마)
│   ├── routing/          # 메시지 라우팅
│   ├── sessions/         # 세션 관리
│   ├── memory/           # 벡터 메모리 (sqlite-vec)
│   ├── hooks/            # 훅 시스템 (Gmail 등)
│   ├── cron/             # 스케줄링
│   ├── media/            # 미디어 처리
│   ├── media-understanding/ # 미디어 이해 (vision, audio)
│   ├── browser/          # 브라우저 자동화 (Playwright/CDP)
│   ├── canvas-host/      # Canvas HTML 렌더링
│   ├── tts/              # Text-to-Speech
│   ├── tui/              # Terminal UI 클라이언트
│   ├── acp/              # Agent Client Protocol
│   ├── security/         # 보안 감사/검증
│   ├── plugin-sdk/       # 플러그인 SDK
│   ├── plugins/          # 플러그인 런타임
│   ├── providers/        # AI 제공자 (Copilot, Google, Qwen)
│   ├── wizard/           # 온보딩 위저드
│   ├── pairing/          # 디바이스 페어링
│   ├── infra/            # 인프라 유틸리티
│   ├── telegram/         # Telegram 채널
│   ├── discord/          # Discord 채널
│   ├── slack/            # Slack 채널
│   ├── signal/           # Signal 채널
│   ├── imessage/         # iMessage 채널
│   ├── whatsapp/         # WhatsApp 채널
│   ├── web/              # WebChat 채널
│   └── line/             # LINE 채널
│
├── extensions/           # 확장 플러그인 (34개)
│   ├── matrix/           # Matrix
│   ├── msteams/          # Microsoft Teams
│   ├── googlechat/       # Google Chat
│   ├── bluebubbles/      # BlueBubbles
│   ├── voice-call/       # 음성 통화
│   ├── feishu/           # Feishu/Lark
│   ├── nostr/            # Nostr
│   ├── twitch/           # Twitch
│   └── ...               # 26개 더
│
├── skills/               # 스킬 (SKILL.md, 52개)
│   ├── coding-agent/     # Codex, Claude Code, Pi
│   ├── github/           # GitHub 통합
│   ├── canvas/           # Canvas 스킬
│   ├── spotify-player/   # Spotify
│   └── ...               # 48개 더
│
├── apps/                 # 네이티브 앱
│   ├── macos/            # macOS (SwiftUI, SPM)
│   ├── ios/              # iOS (SwiftUI, XcodeGen)
│   ├── android/          # Android (Kotlin, Gradle)
│   └── shared/           # 공유 Swift 라이브러리
│
├── ui/                   # Web UI (Lit 웹 컴포넌트)
├── packages/             # 호환 shim (clawdbot, moltbot)
├── Swabble/              # Swift SPM 라이브러리
├── docs/                 # 문서 (Mintlify)
└── scripts/              # 빌드/배포 스크립트
```

---

## 4. 핵심 컴포넌트 상세

### 4.1 Gateway Server (`src/gateway/`)

전체 시스템의 **중심 허브**:

| 파일/모듈                  | 역할                          |
| -------------------------- | ----------------------------- |
| `server.ts` / `server.impl.ts` | 메인 서버 구현                |
| `server-chat.ts`           | 채팅 처리                     |
| `server-channels.ts`       | 채널 관리                     |
| `server-plugins.ts`        | 플러그인 호스팅               |
| `server-discovery.ts`      | Bonjour/mDNS 자동 디스커버리  |
| `server-cron.ts`           | Cron 스케줄링                 |
| `server-broadcast.ts`      | 이벤트 브로드캐스트           |
| `openai-http.ts`           | OpenAI 호환 API               |
| `openresponses-http.ts`    | Open Responses API            |
| `client.ts`                | Gateway 클라이언트            |
| `protocol/`                | TypeBox 스키마                |
| `hooks.ts`                 | Gateway 훅                    |
| `auth.ts`                  | 인증                          |

### 4.2 AI Agent 엔진 (`src/agents/`)

프로젝트에서 **가장 큰 모듈** (~300+ 파일):

**핵심 런타임:**

- `pi-embedded-runner.ts`: AI 에이전트 실행 엔진
- `pi-embedded-subscribe.ts`: 응답 스트리밍 구독
- `pi-embedded-helpers.ts`: 에러 처리, 프롬프트 구성
- `pi-embedded-messaging.ts`: 메시징 통합

**모델 관리:**

- `model-catalog.ts`: 모델 카탈로그
- `model-selection.ts`: 모델 선택 로직
- `model-fallback.ts`: 자동 failover
- `model-auth.ts`: 모델 인증
- `auth-profiles.ts`: 인증 프로파일 로테이션
- `models-config.ts`: 모델 설정 (Ollama, Qianfan, Copilot 등)

**도구 (`agents/tools/`):**

- `bash-tools.ts`: 셸 실행 (PTY, 백그라운드)
- `browser-tool.ts`: 브라우저 자동화
- `web-fetch.ts` / `web-search.ts`: 웹 크롤링/검색
- `memory-tool.ts`: 벡터 메모리
- `image-tool.ts`: 이미지 생성
- `canvas-tool.ts`: Canvas 제어
- `tts-tool.ts`: 음성 합성
- `message-tool.ts`: 메시지 발송
- `cron-tool.ts`: 스케줄 작업
- `sessions-spawn-tool.ts`: 서브에이전트 스폰
- 채널별 액션 (discord, slack, telegram, whatsapp)

**기타:**

- `sandbox/`: Docker 샌드박스 관리
- `skills.ts`: 스킬 로딩/관리
- `workspace.ts`: 워크스페이스 설정
- `system-prompt.ts`: 시스템 프롬프트 동적 구성
- `compaction.ts`: 컨텍스트 윈도우 자동 압축
- `subagent-registry.ts`: 서브에이전트 관리

### 4.3 채널 시스템

**코어 채널 (8개, src/ 내장):**

| 채널     | 라이브러리               |
| -------- | ------------------------ |
| WhatsApp | @whiskeysockets/baileys  |
| Telegram | grammy                   |
| Discord  | @buape/carbon            |
| Slack    | @slack/bolt              |
| Signal   | 자체 구현                |
| iMessage | 자체 구현 (macOS 전용)   |
| LINE     | @line/bot-sdk            |
| WebChat  | 자체 구현                |

**확장 채널 (extensions/ 14+ 채널):**

Matrix, MS Teams, Google Chat, BlueBubbles, Zalo, Zalo Personal, Feishu/Lark, Mattermost, Nextcloud Talk, Nostr, Twitch, Tlon 등

### 4.4 메모리 시스템 (`src/memory/`)

| 구성요소               | 설명                                      |
| ---------------------- | ----------------------------------------- |
| `sqlite-vec`           | SQLite 기반 벡터 저장소                   |
| `embeddings.ts`        | 임베딩 생성 (OpenAI, Gemini, Voyage, LLaMA) |
| `hybrid.ts`            | 하이브리드 검색 (벡터 + 텍스트)           |
| `manager.ts`           | 메모리 매니저 (인덱싱, 배치)              |
| `qmd-manager.ts`       | QMD (구조화 메모리 문서) 관리             |
| `sync-session-files.ts` | 세션 히스토리 자동 인덱싱                 |

### 4.5 훅 시스템 (`src/hooks/`)

- Gmail 통합 (이메일 감시/처리)
- 플러그인 훅
- 내부 훅 (봇 동작 제어)
- Soul/Evil 검사 (프롬프트 인젝션 방어)

### 4.6 Cron 시스템 (`src/cron/`)

- 시간 기반 자동 작업 실행
- 격리된 에이전트 컨텍스트에서 실행
- 작업 로깅/히스토리
- 실행 결과 채널 전달

---

## 5. 플러그인/확장 시스템

### 플러그인 SDK 인터페이스 (`src/plugin-sdk/`):

```
ChannelPlugin
├── ChannelAuthAdapter        # 인증 (로그인/로그아웃)
├── ChannelConfigAdapter      # 설정 스키마
├── ChannelMessagingAdapter   # 메시지 수신
├── ChannelOutboundAdapter    # 메시지 발송
├── ChannelStatusAdapter      # 상태 조회
├── ChannelCommandAdapter     # 명령어 처리
├── ChannelDirectoryAdapter   # 연락처 디렉토리
├── ChannelGroupAdapter       # 그룹 관리
├── ChannelPairingAdapter     # 페어링
├── ChannelSecurityAdapter    # 보안 정책
├── ChannelStreamingAdapter   # 스트리밍 응답
├── ChannelThreadingAdapter   # 스레딩
└── ChannelMentionAdapter     # 멘션 처리
```

---

## 6. 네이티브 앱

| 플랫폼  | 구현                    | 빌드                    |
| ------- | ----------------------- | ----------------------- |
| macOS   | Swift + SwiftUI + SPM   | `pnpm mac:package`      |
| iOS     | Swift + SwiftUI + XcodeGen | `pnpm ios:build`     |
| Android | Kotlin + Gradle         | `pnpm android:assemble` |

공유 코드: `apps/shared/OpenClawKit` (Swift, Gateway 프로토콜 모델)

---

## 7. Web UI (`ui/`)

- **Lit** 기반 Web Components
- **Vite** 빌드
- 주요 뷰: 채팅, 채널 관리, 설정, 디바이스 인증
- 마크다운 렌더링, 테마, 도구 스트림 표시

---

## 8. CLI 주요 명령어

| 명령어                   | 설명             |
| ------------------------ | ---------------- |
| `openclaw onboard`       | 온보딩 위저드    |
| `openclaw gateway`       | 게이트웨이 서버  |
| `openclaw agent`         | AI 에이전트 실행 |
| `openclaw message send`  | 메시지 발송      |
| `openclaw channels status` | 채널 상태      |
| `openclaw doctor`        | 문제 진단/수정   |
| `openclaw status`        | 전체 상태        |
| `openclaw tui`           | 터미널 UI        |
| `openclaw browser`       | 브라우저 자동화  |
| `openclaw cron`          | 스케줄 작업      |
| `openclaw models`        | AI 모델 관리     |
| `openclaw plugins`       | 플러그인 관리    |
| `openclaw skills`        | 스킬 관리        |
| `openclaw sandbox`       | 샌드박스 관리    |
| `openclaw daemon`        | 데몬 서비스      |
| `openclaw update`        | 업데이트         |

---

## 9. 주요 기능 요약

| 기능              | 설명                                        |
| ----------------- | ------------------------------------------- |
| 멀티채널 메시징   | 12+ 채널에서 동일한 AI 어시스턴트           |
| 멀티모델 AI       | Anthropic, OpenAI, Google, xAI, MiniMax, Ollama 등 |
| 자동 failover     | 인증 프로파일 자동 로테이션                 |
| 벡터 메모리       | sqlite-vec 기반 장기 기억                   |
| 브라우저 자동화   | Playwright/CDP 기반 웹 자동화               |
| Docker 샌드박스   | 안전한 코드 실행                            |
| Canvas            | 네이티브 앱에 HTML 렌더링                   |
| 음성              | TTS + 음성 인식 (Whisper)                   |
| 스케줄링          | Cron 기반 자동 작업                         |
| 서브에이전트      | 멀티 에이전트 위임                          |
| 스킬 시스템       | SKILL.md 기반 52개 내장 스킬                |
| 플러그인          | 34개 확장 플러그인                          |
| 네이티브 앱       | macOS + iOS + Android                       |
| OpenAI API 호환   | OpenAI API 형식 접근                        |
| ACP               | Agent Client Protocol 지원                  |
| Tailscale         | 네트워크 터널링/디스커버리                  |

---

## 10. 기술 스택

| 영역       | 기술                          |
| ---------- | ----------------------------- |
| 언어       | TypeScript, Swift, Kotlin     |
| 빌드       | tsdown, Vite, XcodeGen, Gradle |
| 테스트     | Vitest + V8 Coverage (70% 기준) |
| 린트       | Oxlint, Oxfmt, SwiftLint     |
| 타입체크   | tsgo (네이티브 TS 체커)       |
| 웹 서버    | Hono (HTTP), ws (WebSocket)   |
| UI         | Lit (Web Components)          |
| AI SDK     | @mariozechner/pi-agent-core   |
| DB         | SQLite (sqlite-vec)           |
| 브라우저   | Playwright-core               |
| 배포       | Fly.io, Docker, npm           |
| 네트워크   | Tailscale, Bonjour/mDNS       |
