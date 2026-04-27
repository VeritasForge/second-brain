---
tags: [claude-code, mcp, computer-use, gui-automation, macos, research-preview]
created: 2026-04-24
---

# 📖 Computer-Use MCP Server (Claude Code) — Concept Deep Dive

> 💡 **한줄 요약**: Claude Code에 내장된 MCP 서버로, Claude가 macOS 화면을 보고 마우스 클릭·키보드 입력·스크린샷을 수행하여 GUI 앱을 직접 조작할 수 있게 해주는 기능이다.

---

## 1️⃣ 무엇인가? (What is it?)

**Computer-Use MCP Server**는 Claude Code에 **빌트인**으로 탑재된 MCP (Model Context Protocol) 서버로, Claude가 사용자의 **macOS 데스크톱을 직접 제어**할 수 있게 해주는 기능이다.

- **공식 정의**: Claude Code CLI에서 `computer-use`라는 이름의 내장 MCP 서버로, Claude가 앱을 열고, 화면을 보고(스크린샷), 클릭/타이핑/스크롤하여 사용자가 하듯이 작업할 수 있다 ([Claude Code 공식 문서](https://code.claude.com/docs/en/computer-use))
- **탄생 배경**: Anthropic이 2024년 10월 Claude 3.5 Sonnet에서 처음 Computer Use를 소개했고, 2026년 3~4월에 Claude Code CLI에 **research preview**로 확장됨
- **해결하는 문제**: CLI나 API가 없는 **GUI 전용 도구** (Xcode, iOS Simulator, 디자인 툴, 시스템 설정 등)를 터미널 세션 안에서 직접 조작해야 할 때 사용

> 📌 **핵심 키워드**: `MCP Server`, `Computer Use`, `GUI Automation`, `Screen Control`, `macOS`, `Research Preview`

---

## 2️⃣ 핵심 개념 (Core Concepts)

Computer-Use MCP Server를 구성하는 핵심 요소를 이해하면, "Claude가 어떻게 내 컴퓨터를 쓰는지"가 명확해진다.

```
┌─────────────────────────────────────────────────────────┐
│              🖥️  Computer-Use MCP Server 구조            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐    MCP Protocol    ┌───────────────┐  │
│  │  Claude Code  │◄────────────────►│  computer-use  │  │
│  │  (MCP Client) │   JSON-RPC 2.0   │  (MCP Server)  │  │
│  └──────┬───────┘                   └───────┬───────┘  │
│         │                                    │          │
│         │  요청: "앱 열어, 클릭해"             │          │
│         │                                    ▼          │
│         │                          ┌─────────────────┐  │
│         │                          │  macOS APIs     │  │
│         │                          │  ┌───────────┐  │  │
│         │                          │  │Accessibility│  │  │
│         │                          │  ├───────────┤  │  │
│         │                          │  │Screen Rec. │  │  │
│         │                          │  └───────────┘  │  │
│         │                          └────────┬────────┘  │
│         │                                   ▼           │
│         │                          ┌─────────────────┐  │
│         ◄──────── 스크린샷 반환 ────│  사용자 데스크톱  │  │
│                                    └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

| 구성 요소            | 역할          | 설명                                                                               |
| -------------------- | ------------- | ---------------------------------------------------------------------------------- |
| 🔌 MCP Client       | 요청자        | Claude Code가 MCP 클라이언트로 동작하여 computer-use 서버에 작업을 요청             |
| 🖥️ computer-use Server | 실행자     | 빌트인 MCP 서버. macOS Accessibility/Screen Recording API를 통해 실제 화면 조작     |
| 📸 스크린샷 엔진      | 시각 피드백   | 화면을 캡처하여 다운스케일 후 Claude에게 전달. Retina 디스플레이 자동 대응           |
| 🔒 앱별 승인 시스템   | 보안 게이트   | 세션마다 사용자가 앱별로 접근 허용/거부를 결정                                      |
| 🔐 머신 잠금 (Lock)   | 동시성 제어   | 한 번에 하나의 Claude 세션만 컴퓨터를 제어 가능                                    |

- **MCP (Model Context Protocol)**: Anthropic이 2024년 11월에 발표한 **오픈 프로토콜**. AI 모델이 외부 도구/데이터에 연결하는 표준 방식. JSON-RPC 2.0 기반 ([Wikipedia](https://en.wikipedia.org/wiki/Model_Context_Protocol))
- **빌트인 서버**: 별도 설치 없이 Claude Code에 이미 포함되어 있음. `/mcp` 명령으로 활성화만 하면 됨

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

```
┌──────────────────────────────────────────────────────────────────┐
│                    동작 흐름 (Data Flow)                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  사용자 프롬프트                                                  │
│  "Swift 앱 빌드하고 실행해서 모든 버튼 테스트해줘"                   │
│       │                                                          │
│       ▼                                                          │
│  ┌──────────────────────────────────────┐                        │
│  │  Claude: 도구 선택 우선순위 판단      │                        │
│  │  1. MCP 서버 있으면? → MCP 사용       │                        │
│  │  2. Shell 명령이면? → Bash 사용       │                        │
│  │  3. 웹 작업이면? → Chrome 사용        │                        │
│  │  4. 그 외 GUI? → ⭐ Computer Use     │                        │
│  └──────────┬───────────────────────────┘                        │
│             │ (4번 선택됨)                                        │
│             ▼                                                    │
│  ┌──────────────────────────────────────┐                        │
│  │  Step 1: 머신 잠금 획득               │                        │
│  │  → macOS 알림: "Claude is using..."   │                        │
│  │  → 다른 앱 숨김 처리                   │                        │
│  └──────────┬───────────────────────────┘                        │
│             ▼                                                    │
│  ┌──────────────────────────────────────┐                        │
│  │  Step 2: 앱 승인 요청 (세션별)         │                        │
│  │  → 터미널에 승인 프롬프트 표시          │                        │
│  │  → "Allow for this session" / "Deny" │                        │
│  └──────────┬───────────────────────────┘                        │
│             ▼                                                    │
│  ┌──────────────────────────────────────┐     ┌───────────────┐  │
│  │  Step 3: GUI 조작 루프                │────►│  스크린샷 촬영  │  │
│  │  → 클릭, 타이핑, 스크롤               │◄────│  (다운스케일)   │  │
│  │  → 스크린샷으로 결과 확인              │     └───────────────┘  │
│  │  → 다음 액션 결정                     │                        │
│  └──────────┬───────────────────────────┘                        │
│             ▼                                                    │
│  ┌──────────────────────────────────────┐                        │
│  │  Step 4: 완료 및 잠금 해제            │                        │
│  │  → 숨긴 앱 복원                       │                        │
│  │  → 결과를 대화에 보고                  │                        │
│  └──────────────────────────────────────┘                        │
│                                                                  │
│  ⏹️ 언제든 Esc 키로 즉시 중단 가능                                │
└──────────────────────────────────────────────────────────────────┘
```

### 🔄 동작 흐름 (Step by Step)

1. **Step 1 — 도구 선택**: Claude는 가장 정밀한 도구부터 시도한다. MCP 서버 → Bash → Chrome → Computer Use 순서로, **Computer Use는 다른 방법이 없을 때 최후의 수단**으로 사용됨
2. **Step 2 — 머신 잠금**: machine-wide lock을 획득. 다른 Claude 세션이 이미 사용 중이면 실패함
3. **Step 3 — 앱 숨김**: 승인된 앱만 화면에 남기고 나머지 앱은 숨김. 터미널 윈도우는 **항상 보이지만 스크린샷에서 제외**
4. **Step 4 — GUI 조작 루프**: 스크린샷 촬영 → 화면 분석 → 액션 결정 → 클릭/타이핑 → 다시 스크린샷… 반복
5. **Step 5 — 완료**: 작업 끝나면 잠금 해제, 숨긴 앱 복원, 결과 보고

### 📸 스크린샷 다운스케일

```
16인치 MacBook Pro Retina:
원본: 3456 × 2234  →  다운스케일: ~1372 × 887
                        (종횡비 유지, 자동 처리)
```

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| #   | 유즈 케이스               | 설명                                                         | 적합한 이유                                       |
| --- | ------------------------- | ------------------------------------------------------------ | ------------------------------------------------- |
| 1   | 🍎 네이티브 앱 빌드 & 검증 | Swift 앱 빌드 → 실행 → UI 클릭 → 스크린샷                    | CLI에서 빌드 후 GUI 검증까지 한 세션에서 완료      |
| 2   | 🧪 E2E UI 테스팅          | Electron/macOS 앱의 온보딩 플로우를 직접 클릭하여 테스트      | Playwright 설정 없이 즉석 테스트 가능              |
| 3   | 🐛 레이아웃 버그 디버깅    | 윈도우 리사이즈 → 버그 재현 → 스크린샷 → CSS 수정 → 확인     | 시각적 버그를 Claude가 직접 "보고" 수정            |
| 4   | 📱 iOS Simulator 조작     | 시뮬레이터에서 앱 실행, 탭 이동, 로딩 시간 확인               | XCTest 작성 없이 수동 테스트를 자동화              |
| 5   | 🎨 GUI 전용 도구 조작     | 디자인 툴, 하드웨어 제어판 등 API 없는 도구                   | CLI/API가 없는 도구의 유일한 자동화 방법           |

### ✅ 베스트 프랙티스

1. **구체적으로 지시하라**: "빌드 → 실행 → Preferences 열기 → 슬라이더 조작 → 스크린샷"처럼 단계별로 명시
2. **가능하면 다른 도구를 우선 사용하라**: Computer Use는 가장 느린 도구. MCP/Bash/Chrome으로 가능하면 그것을 쓰자
3. **Esc 키를 기억하라**: 예상치 못한 동작 시 Esc로 즉시 중단 가능

### 🏢 실제 적용 사례

- **macOS 메뉴바 앱 개발**: Claude가 Swift 코드 작성 → xcodebuild → 앱 실행 → 모든 컨트롤 클릭 검증
- **iOS 시뮬레이터 테스트**: 온보딩 화면 탭 이동하며 로딩 시간 체크

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분     | 항목                          | 설명                                                   |
| -------- | ----------------------------- | ------------------------------------------------------ |
| ✅ 장점  | **코드 → GUI 검증 원스톱**    | 코드 작성과 시각적 검증을 한 세션에서 완료              |
| ✅ 장점  | **테스트 인프라 불필요**       | Playwright, XCTest 등 설정 없이 즉석 UI 테스트 가능    |
| ✅ 장점  | **API 없는 도구도 자동화**    | GUI만 있는 도구를 프로그래밍적으로 제어                 |
| ✅ 장점  | **빌트인이라 설치 불필요**    | `/mcp`에서 활성화만 하면 바로 사용                      |
| ✅ 장점  | **강력한 보안 모델**          | 앱별 승인, 머신 잠금, 터미널 스크린샷 제외              |
| ❌ 단점  | **macOS 전용**                | Linux/Windows CLI에서 사용 불가 (Windows는 Desktop 앱에서만) |
| ❌ 단점  | **느림**                      | 스크린샷 촬영·분석·액션 루프라 Bash/MCP보다 훨씬 느림  |
| ❌ 단점  | **Pro/Max 플랜 필요**         | Team/Enterprise 플랜에서는 사용 불가                   |
| ❌ 단점  | **Research Preview**          | 아직 안정 릴리즈가 아니며, 예상치 못한 동작 가능       |
| ❌ 단점  | **샌드박스 아님**             | Bash 도구와 달리 실제 데스크톱에서 실행되어 위험 가능성 있음 |

### ⚖️ Trade-off 분석

```
자동화 범위  ◄──────── Trade-off ────────►  실행 속도
(GUI까지 가능)                               (스크린샷 루프로 느림)

보안 통제    ◄──────── Trade-off ────────►  편의성
(앱별 승인)                                  (매 세션 승인 필요)

범용성       ◄──────── Trade-off ────────►  플랫폼 지원
(모든 GUI 앱)                                (macOS만 CLI 지원)
```

---

## 6️⃣ 차이점 비교 (Comparison)

Claude Code에서 **외부 시스템과 상호작용하는 4가지 방식**을 비교한다.

### 📊 비교 매트릭스

| 비교 기준   | 🖥️ Computer Use          | 🔧 Bash Tool         | 🌐 Chrome (Claude in Chrome) | 🔌 Custom MCP Server     |
| ----------- | ------------------------- | -------------------- | ---------------------------- | ------------------------- |
| 핵심 목적   | GUI 앱 직접 조작          | Shell 명령 실행      | 브라우저 웹페이지 조작        | 구조화된 API/도구 연결     |
| 속도        | ⚡ 느림 (스크린샷 루프)   | ⚡⚡⚡ 빠름          | ⚡⚡ 보통                    | ⚡⚡⚡ 빠름               |
| 정밀도      | 보통 (시각 기반)          | 높음 (정확한 출력)   | 보통                         | 높음 (구조화된 응답)       |
| 적용 범위   | 모든 GUI 앱              | CLI 있는 도구        | 웹 앱만                      | 서버 구현된 도구만         |
| 보안        | 앱별 승인, 잠금           | 샌드박스 가능        | 브라우저 샌드박스             | 서버별 권한                |
| 우선순위    | 4번째 (최후 수단)         | 2번째                | 3번째                        | 1번째 (최우선)             |
| 플랫폼      | macOS만                   | 모든 OS              | 모든 OS                      | 모든 OS                    |

### 🔍 핵심 차이 요약

```
Computer Use                    Bash Tool
──────────────────    vs    ──────────────────
GUI 앱 직접 조작               텍스트 기반 명령 실행
스크린샷으로 "봄"               stdout으로 "읽음"
느리지만 범용적                빠르지만 CLI 필요
실제 데스크톱에서 실행          샌드박스 가능

Computer Use                    Custom MCP Server
──────────────────    vs    ──────────────────
범용 (아무 앱이나)              특정 서비스 전용
느린 시각 루프                  빠른 구조화된 호출
설정 거의 없음                  서버 구현/설치 필요
정밀도 낮음                     정밀도 높음
```

### 🤔 언제 무엇을 선택?

- **Computer Use** → CLI/API가 없는 **네이티브 GUI 앱**을 조작해야 할 때
- **Bash** → 빌드, 테스트, 파일 조작 등 **shell로 해결되는 모든 것**
- **Chrome** → **웹 앱**을 브라우저에서 테스트해야 할 때
- **Custom MCP** → GitHub, Slack, DB 등 **구조화된 API**가 있는 서비스

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| #   | 실수                                       | 왜 문제인가                           | 올바른 접근                                                       |
| --- | ------------------------------------------ | ------------------------------------- | ----------------------------------------------------------------- |
| 1   | Bash로 되는 작업에 Computer Use 사용       | 불필요하게 느리고 토큰 소모 큼        | Claude가 자동으로 우선순위를 판단하지만, 프롬프트에 "터미널에서 해줘"라고 명시 가능 |
| 2   | 고해상도에서 작은 UI 요소 클릭 기대         | 다운스케일 후 글자가 너무 작아 인식 불가 | 앱 내에서 글자 크기를 키우거나 윈도우를 확대                       |
| 3   | 여러 Claude 세션에서 동시 사용 시도         | 머신 잠금으로 하나만 가능             | 이전 세션 종료 후 사용                                            |
| 4   | 민감한 앱 무분별 승인                       | 터미널 승인 = shell 접근 수준         | 경고 메시지를 반드시 읽고 필요한 앱만 승인                         |

### 🚫 Anti-Patterns

1. **"모든 것을 Computer Use로"**: Computer Use는 최후의 수단. API, CLI, MCP가 있으면 그것부터 쓰자
2. **비대화형 모드 (`-p` 플래그)에서 사용 시도**: Computer Use는 대화형 세션에서만 동작. CI/CD 파이프라인에서는 사용 불가

### 🔒 보안/성능 고려사항

- **보안**: Bash 도구와 달리 **샌드박스가 아님**. 실제 데스크톱에서 실행되므로, 화면에 표시된 악성 텍스트(prompt injection)가 Claude에게 영향을 줄 수 있음. 다만 터미널은 스크린샷에서 제외되고, Esc 키 이벤트는 소비되어 prompt injection으로 다이얼로그를 닫을 수 없음
- **성능**: 매 액션마다 스크린샷 촬영 → 모델 전송 → 분석 루프를 돌므로, **토큰 소모가 매우 큼**. Pro 플랜의 사용량 제한에 빠르게 도달할 수 있음
- **앱 티어**: 브라우저/트레이딩 앱은 **view-only**, 터미널/IDE는 **click-only**, 나머지는 **full control** — 카테고리별로 제어 수준이 다름

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형      | 이름                        | 링크/설명                                                                                          |
| --------- | --------------------------- | -------------------------------------------------------------------------------------------------- |
| 📖 공식 문서 | Claude Code Computer Use | [code.claude.com/docs/en/computer-use](https://code.claude.com/docs/en/computer-use)               |
| 📖 공식 가이드 | Computer Use 안전 가이드 | [support.claude.com/en/articles/14128542](https://support.claude.com/en/articles/14128542)         |
| 📖 MCP 문서 | Model Context Protocol    | [modelcontextprotocol.io](https://modelcontextprotocol.io/docs/develop/connect-local-servers)      |
| 📘 블로그  | MCP로 코드 실행             | [anthropic.com/engineering/code-execution-with-mcp](https://www.anthropic.com/engineering/code-execution-with-mcp) |

### 🛠️ 관련 도구 & 대안

| 도구/라이브러리                                                           | 플랫폼          | 용도                                                          |
| ------------------------------------------------------------------------- | --------------- | ------------------------------------------------------------- |
| Claude in Chrome                                                          | 모든 OS         | 브라우저 기반 웹 앱 자동화 (Computer Use 대신 웹 작업에 사용)  |
| Claude Desktop Computer Use                                               | macOS + Windows | 데스크톱 앱에서 GUI 설정으로 Computer Use 사용                |
| [domdomegg/computer-use-mcp](https://github.com/domdomegg/computer-use-mcp) | 크로스 플랫폼   | 커뮤니티 제작 오픈소스 Computer Use MCP (비공식)               |
| Browser Use MCP                                                           | 모든 OS         | 브라우저 자동화 특화 MCP 서버                                 |

### 🔮 트렌드 & 전망

- **Opus 4.7의 3x 비전 해상도 향상**으로 Computer Use의 UI 인식 정확도가 대폭 개선됨 ([AI Tool Analysis](https://aitoolanalysis.com/claude-code/))
- **MCP 생태계 9,000+ 플러그인** 확장 중 — Computer Use가 필요한 경우가 점점 줄어들 수 있음 (전용 MCP 서버가 대체)
- Windows CLI 지원은 아직 미정이나, Desktop 앱에서는 이미 Windows 지원 중

### 💬 커뮤니티 인사이트

- 개발자들은 Computer Use의 **코드 품질은 높이 평가** (67% blind test 승률)하지만, **토큰 소모가 큰 점**을 주요 단점으로 지적 ([Reddit 개발자 조사](https://dev.to/_46ea277e677b888e0cd13/claude-code-vs-codex-2026-what-500-reddit-developers-really-think-31pb))
- "Build → Launch → Click → Screenshot" 워크플로우가 **네이티브 앱 개발자에게 특히 유용**하다는 평가
- Computer Use를 포함한 full MCP 지원이 **Codex 대비 Claude Code의 킬러 피처**로 평가됨

---

## 📎 Sources

1. [Claude Code 공식 문서 - Computer Use](https://code.claude.com/docs/en/computer-use) — 공식 문서
2. [Wikipedia - Model Context Protocol](https://en.wikipedia.org/wiki/Model_Context_Protocol) — 백과사전
3. [Anthropic - Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) — 공식 블로그
4. [Claude Code vs Codex 2026 - Reddit Developer Survey](https://dev.to/_46ea277e677b888e0cd13/claude-code-vs-codex-2026-what-500-reddit-developers-really-think-31pb) — 커뮤니티
5. [Claude Code Opus 4.7 Review](https://aitoolanalysis.com/claude-code/) — 블로그
6. [Builder.io - Claude Code MCP Servers Guide](https://www.builder.io/blog/claude-code-mcp-servers) — 블로그
7. [domdomegg/computer-use-mcp (GitHub)](https://github.com/domdomegg/computer-use-mcp) — 오픈소스
8. [Computer Use Safety Guide](https://support.claude.com/en/articles/14128542) — 공식 가이드

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 6
> - 수집 출처 수: 8
> - 출처 유형: 공식 2, 블로그 3, 커뮤니티 2, 오픈소스 1

---

### 🎯 12살을 위한 비유로 정리!

Computer-Use MCP Server를 **리모컨**에 비유하면:

- **Bash 도구** = 전화기로 주문하기 (텍스트로 명령) 📞
- **MCP 서버** = 전용 리모컨 (TV 리모컨, 에어컨 리모컨 등 각각 하나씩) 🎮
- **Computer Use** = **로봇 팔**이 직접 화면 앞에 앉아서 마우스를 잡고 클릭하는 것 🤖👆

로봇 팔(Computer Use)은 어떤 앱이든 조작할 수 있지만, 전화(Bash)보다 느리고, 전용 리모컨(MCP)보다 정확하지 않다. 그래서 **전화나 리모컨으로 안 되는 것만** 로봇 팔을 쓰는 것!
