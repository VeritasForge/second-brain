---
created: 2026-02-20
source: claude-code
tags:
  - slack
  - socket-mode
  - websocket
  - slack-api
  - slack-sticker-bot
---

# 📖 Slack Socket Mode vs HTTP (공개 URL) — Concept Deep Dive

> 💡 **한줄 요약**: Socket Mode는 **WebSocket으로 Slack과 통신**하여 공개 URL 없이 앱을 실행하는 방식이고, HTTP 방식은 **공개 URL에 Slack이 이벤트를 POST**하는 전통적 방식입니다.

---

## 1️⃣ 무엇인가? (What is it?)

Slack 앱이 이벤트(메시지, 슬래시 커맨드, 버튼 클릭 등)를 받는 **두 가지 통신 방식**입니다.

- **HTTP 방식 (공개 URL)**: Slack이 앱의 공개 엔드포인트(`https://your-server.com/slack/events`)로 HTTP POST 요청을 보냄
- **Socket Mode**: 앱이 Slack에 WebSocket 연결을 열고, 그 채널로 이벤트를 수신

Socket Mode는 2020년에 Slack이 도입. 방화벽 뒤에서 개발하는 팀을 위해 만들어졌으며, **공개 URL 없이도 모든 Slack API 기능**을 사용할 수 있게 합니다.

> 📌 **핵심 키워드**: `WebSocket`, `Socket Mode`, `HTTP Request URL`, `Events API`, `방화벽`

---

## 2️⃣ 핵심 개념 (Core Concepts)

```
┌─────────────────────────────────────────────────────┐
│                  두 가지 통신 방식                     │
├────────────────────────┬────────────────────────────┤
│                        │                            │
│   🌐 HTTP 방식          │   🔌 Socket Mode           │
│                        │                            │
│   Slack ──POST──▶ 앱   │   앱 ──WebSocket──▶ Slack  │
│   (Slack이 앱을 호출)    │   (앱이 Slack에 연결)       │
│                        │                            │
│   필요: 공개 URL        │   필요: App-Level Token    │
│   방향: Slack → 앱      │   방향: 앱 → Slack (양방향) │
│   프로토콜: HTTP/HTTPS  │   프로토콜: WebSocket(wss)  │
│                        │                            │
└────────────────────────┴────────────────────────────┘
```

| 구성 요소    | HTTP 방식                    | Socket Mode                              |
| ------------ | ---------------------------- | ---------------------------------------- |
| **연결 주체** | Slack이 앱에 접속             | 앱이 Slack에 접속                        |
| **URL**      | 고정 공개 URL                | 런타임에 생성되는 동적 WebSocket URL     |
| **인증**     | 요청마다 서명 검증 필요      | 사전 인증된 연결 (검증 불필요)           |
| **이벤트 확인** | HTTP 200 응답              | `envelope_id`로 acknowledge              |

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

### 🔌 Socket Mode 동작 흐름

```
┌──────────┐                        ┌──────────────┐
│  Slack   │                        │  Bolt App    │
│  Server  │                        │  (EC2)       │
└────┬─────┘                        └──────┬───────┘
     │                                      │
     │  1. apps.connections.open (HTTP)     │
     │◀─────────────────────────────────────┤ App-Level Token
     │                                      │
     │  2. WebSocket URL 반환               │
     ├─────────────────────────────────────▶│
     │                                      │
     │  3. WebSocket 연결 (wss://...)       │
     │◀════════════════════════════════════▶│ 양방향 연결 수립
     │                                      │
     │  4. 사용자가 /sticker search 입력    │
     │                                      │
     │  5. 이벤트 전송 (WebSocket)          │
     ├─────────────────────────────────────▶│
     │                                      │  6. 처리
     │  7. acknowledge (envelope_id)        │
     │◀─────────────────────────────────────┤
     │                                      │
     │  8. chat.postMessage (HTTP API)      │
     │◀─────────────────────────────────────┤
     │                                      │
```

### 🌐 HTTP 방식 동작 흐름

```
┌──────────┐                        ┌──────────────┐
│  Slack   │                        │  Bolt App    │
│  Server  │                        │  (EC2)       │
└────┬─────┘                        └──────┬───────┘
     │                                      │
     │  1. 사용자가 /sticker search 입력    │
     │                                      │
     │  2. HTTP POST → https://app.com/slack│
     ├─────────────────────────────────────▶│
     │                                      │  3. 서명 검증
     │  4. HTTP 200 (3초 내 응답 필수)      │  4. 처리
     │◀─────────────────────────────────────┤
     │                                      │
     │  5. chat.postMessage (HTTP API)      │
     │◀─────────────────────────────────────┤
     │                                      │
```

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| #   | 유즈 케이스                    | 추천 방식    | 이유                                  |
| --- | ------------------------------ | ------------ | ------------------------------------- |
| 1   | **사내 봇 (우리 스티커 봇)**   | Socket Mode  | EC2에 공개 URL 설정 불필요, 간편      |
| 2   | 로컬 개발/테스트               | Socket Mode  | ngrok 없이 바로 테스트 가능           |
| 3   | 방화벽 뒤 서버                 | Socket Mode  | 아웃바운드 연결만 필요                |
| 4   | Slack Marketplace 앱           | HTTP         | Marketplace 배포 시 HTTP 필수         |
| 5   | 대규모 트래픽 앱               | HTTP         | 로드밸런서 + 수평 확장 가능           |

### ✅ 베스트 프랙티스

1. **단일 워크스페이스 사내 봇 → Socket Mode** 선택
2. Bolt 프레임워크 사용 시 `socketMode: true` 한 줄이면 전환됨
3. Socket Mode에서도 Slack API 호출(chat.postMessage 등)은 HTTP로 나감

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분      | Socket Mode                    | HTTP 방식                         |
| --------- | ------------------------------ | --------------------------------- |
| ✅ 장점   | 공개 URL 불필요                | 수평 확장 가능 (로드밸런서)       |
| ✅ 장점   | 방화벽 뒤에서 동작             | Marketplace 배포 가능             |
| ✅ 장점   | ngrok 없이 로컬 개발           | 단순한 요청-응답 모델             |
| ✅ 장점   | 서명 검증 불필요               | 상태 비저장(stateless)            |
| ❌ 단점   | 수평 확장 어려움               | SSL 인증서 + 도메인 필요          |
| ❌ 단점   | Marketplace 배포 불가          | 3초 내 응답 필수                  |
| ❌ 단점   | WebSocket 연결 관리 필요       | 방화벽 인바운드 규칙 필요         |

### ⚖️ Trade-off

```
간편함    ◄──────── Trade-off ────────►  확장성
Socket    ◄─────────────────────────►  HTTP
설정 0분   ◄─────────────────────────►  도메인+SSL+인바운드 규칙
```

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 비교 매트릭스

| 비교 기준        | Socket Mode        | HTTP                       |
| ---------------- | ------------------ | -------------------------- |
| 공개 URL 필요    | ❌                  | ✅                          |
| SSL 인증서 필요  | ❌                  | ✅                          |
| 방화벽 설정      | 아웃바운드만       | 인바운드 오픈 필요         |
| 설정 난이도      | ⚡ 매우 낮음       | 중간                       |
| 수평 확장        | ⚠️ 어려움          | ✅ 로드밸런서 가능          |
| Marketplace      | ❌ 불가             | ✅ 필수                     |
| 응답 시간 제한   | 없음               | 3초                        |
| Bolt 설정        | `socketMode: true` | Request URL 등록           |

### 🤔 우리 스티커 봇에서는?

- 단일 워크스페이스 → Marketplace 불필요 → **Socket Mode**
- EC2 하나에서 실행 → 수평 확장 불필요 → **Socket Mode**
- Docker Compose → 공개 URL 설정 번거로움 회피 → **Socket Mode**

→ **Socket Mode가 최적**

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수

| #   | 실수                            | 왜 문제인가                            | 올바른 접근                                       |
| --- | ------------------------------- | -------------------------------------- | ------------------------------------------------- |
| 1   | Bot Token으로 Socket Mode 연결 시도 | Socket Mode는 App-Level Token 필요 | `xapp-` 토큰 발급 후 사용                         |
| 2   | acknowledge 누락                | Slack이 이벤트를 재전송 (중복 처리)    | 모든 이벤트에 ack 응답                            |
| 3   | WebSocket 끊김 미처리           | 연결 끊기면 이벤트 수신 불가           | Bolt가 자동 재연결 처리 (걱정 불필요)             |

### 🔒 보안 고려사항

- App-Level Token (`xapp-`)은 환경변수로 관리, 코드에 하드코딩 금지
- Socket Mode라도 Slack API 호출 시 Bot Token (`xoxb-`) 별도 필요

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 🛠️ Bolt에서의 설정

```javascript
const app = new App({
  token: process.env.SLACK_BOT_TOKEN,       // xoxb-
  appToken: process.env.SLACK_APP_TOKEN,    // xapp-
  socketMode: true,                         // 이 한 줄이 전부
});
```

### 📚 학습 리소스

| 유형         | 이름                      | 링크                                                                                         |
| ------------ | ------------------------- | -------------------------------------------------------------------------------------------- |
| 📖 공식 문서 | Socket Mode vs HTTP 비교  | [docs.slack.dev](https://docs.slack.dev/apis/events-api/comparing-http-socket-mode/)         |
| 📖 공식 문서 | Socket Mode 사용법        | [docs.slack.dev](https://docs.slack.dev/apis/events-api/using-socket-mode/)                  |
| 📖 공식 블로그 | Socket to me             | [slack.com/blog](https://slack.com/blog/developers/socket-to-me)                             |

---

## 📎 Sources

1. [Comparing HTTP & Socket Mode](https://docs.slack.dev/apis/events-api/comparing-http-socket-mode/) — 공식 문서
2. [Using Socket Mode](https://docs.slack.dev/apis/events-api/using-socket-mode/) — 공식 문서
3. [Socket to me (Slack Blog)](https://slack.com/blog/developers/socket-to-me) — 공식 블로그
4. [Socket Mode Implementation](https://api.slack.com/apis/connections/socket-implement) — 공식 문서
