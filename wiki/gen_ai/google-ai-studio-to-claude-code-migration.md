---
created: 2026-02-24
source: claude-code
tags:
  - google-ai-studio
  - claude-code
  - cursor
  - vibe-coding
  - migration
  - deep-research
---

# Deep Research: Google AI Studio -> Export -> Claude Code/Cursor 고도화 워크플로우

## Executive Summary

Google AI Studio에서 앱을 만들고 -> GitHub/ZIP으로 Export -> Claude Code, Cursor 등 AI 코딩 도구에서 고도화하는 워크플로우는 **이미 확립된 패턴**입니다. 다만 "AI Studio -> Claude Code로 직접 마이그레이션"에 대한 전용 튜토리얼은 아직 없고, **"AI Studio -> GitHub -> 외부 IDE"** 패턴이 사실상의 표준 워크플로우입니다.

---

## Findings

### 1. 확립된 워크플로우: AI Studio -> GitHub -> 외부 IDE

이 워크플로우는 여러 독립 가이드에서 동일하게 설명됩니다:

```
Step 1: AI Studio에서 자연어로 앱 설명 -> 앱 자동 생성
Step 2: AI Studio 내에서 반복 수정 (채팅 + UI 어노테이션)
Step 3: "Export to GitHub" 클릭 -> 자동 레포지토리 생성
Step 4: Cursor/VS Code/Claude Code에서 git clone
Step 5: npm install && npm run dev 로 로컬 실행
Step 6: AI 코딩 도구로 고도화 작업 시작
```

- **확신도**: [Confirmed]
- **출처**: [The Complete Guide to Building with Google AI Studio](https://marily.substack.com/p/the-complete-guide-to-building-with) (Marily Nika, Substack), [Kasun Sameera 배포 가이드](https://www.kasunsameera.com/how-i-deploy-apps-with-google-ai-studio-full-tutorial-git-hub-tips), [Google 공식문서](https://ai.google.dev/gemini-api/docs/aistudio-build-mode)
- **근거**: Marily Nika의 가이드에서 "Click Export to GitHub and continue in VS Code, Cursor, or similar IDEs"라고 명시. Kasun의 가이드에서 GitHub OAuth 연동 + 로컬 개발 절차 상세 기술

### 2. AI Studio에서 만든 실제 앱 예시 (Export 가능)

Marily Nika의 가이드에서 AI Studio Build 모드로 만든 3가지 실제 앱 사례:

| 앱 이름                         | 설명                                           | 사용 기능                 |
| ------------------------------- | ---------------------------------------------- | ------------------------- |
| **음성 제어 Task Manager**      | "치과 내일 2시" 말하면 AI가 파싱 -> 날짜별 정리 | Live API (음성)           |
| **경쟁사 인텔리전스 대시보드**  | 경쟁사 웹사이트 모니터링 -> 가격/업데이트 추적  | Google Search grounding   |
| **화이트보드->액션 아이템**     | 회의 화이트보드 사진 업로드 -> 액션 아이템 추출  | 이미지 분석 + Sheets 연동 |

이 앱들 모두 **Export to GitHub -> 외부 IDE에서 고도화** 가능한 구조입니다.

- **확신도**: [Confirmed]
- **출처**: [Marily Nika 가이드](https://marily.substack.com/p/the-complete-guide-to-building-with)
- **근거**: 원문에서 앱 3개의 구체적 기능/사용 기술을 직접 확인

### 3. Export 후 고도화 시 해야 할 작업들

Marily Nika의 가이드와 Kasun의 가이드를 종합하면, Export 후 외부 IDE에서 할 수 있는 고도화 작업:

| 고도화 항목            | 설명                                | 도구              |
| ---------------------- | ----------------------------------- | ----------------- |
| **데이터 영속성 추가** | Firestore, Supabase 등 DB 연동     | Claude Code/Cursor |
| **이메일 서비스 연동** | SendGrid, Gmail API 통합            | Claude Code/Cursor |
| **스케줄링**           | Cloud Scheduler로 자동화 작업 설정  | Claude Code/Cursor |
| **API 프로바이더 교체** | Gemini -> Claude API 로 LLM 교체   | Claude Code        |
| **인증/권한**          | OAuth, JWT 등 사용자 인증 추가      | Claude Code/Cursor |
| **환경변수 관리**      | API 키 서버사이드 보안 처리         | Claude Code/Cursor |
| **테스트 추가**        | Unit/E2E 테스트 작성                | Claude Code        |

- **확신도**: [Synthesized]
- **출처**: [Marily Nika 가이드](https://marily.substack.com/p/the-complete-guide-to-building-with) + [Kasun 가이드](https://www.kasunsameera.com/how-i-deploy-apps-with-google-ai-studio-full-tutorial-git-hub-tips) 종합
- **근거**: Marily는 "Firestore, SendGrid, Cloud Scheduler" 추가를 명시. Kasun은 "환경변수, 보안, README" 작성을 권장

### 4. Claude Code에서 고도화하는 구체적 시나리오

AI Studio에서 Export한 React + Node.js 프로젝트를 Claude Code에서 고도화하는 흐름:

```bash
# Step 1: GitHub에서 클론
git clone https://github.com/your-repo/ai-studio-app.git
cd ai-studio-app

# Step 2: 의존성 설치
npm install

# Step 3: Claude Code 실행
claude

# Step 4: Claude Code에서 고도화 지시 예시
> "geminiService.ts의 Gemini API 호출을 Anthropic Claude API로 교체해줘"
> "Supabase로 사용자 데이터 영속성을 추가해줘"
> "Jest로 API 호출 유닛 테스트를 작성해줘"
> "다크모드 토글 기능을 추가해줘"
```

- **확신도**: [Synthesized]
- **출처**: 앞서 확인한 AI Studio Export 구조(공식문서) + Claude Code 사용법(Anthropic 문서) 종합
- **근거**: Export 코드 구조가 표준 React + Node.js이므로, Claude Code에서 즉시 작업 가능한 구조임이 논리적으로 성립

### 5. Cursor를 사용한 고도화 사례

Vibe Coding 가이드(natively.dev)에서 설명하는 구체적 워크플로우:

```
1. AI Studio에서 프로젝트 -> GitHub Push
2. Cursor에서 Cmd+Shift+P -> Git: Clone -> 레포 URL 붙여넣기
3. Cursor에서 Copilot 또는 Composer를 사용해 추가 기능 구현
   - 커스텀 기능 추가
   - 고급 애니메이션
   - 서드파티 API 연동
```

- **확신도**: [Likely]
- **출처**: [Vibe Coding with Cursor, Copilot & Claude - IDE Tools Guide 2026](https://natively.dev/articles/vibe-coding-ide-tools)
- **근거**: 워크플로우 설명이 구체적이지만, 실제 완성된 앱의 스크린샷/코드 예시는 미확인

---

## 배경: Google AI Studio 목업을 Claude로 가져오기

### Export 방식 3가지

| 방법             | 설명                                                               |
| ---------------- | ------------------------------------------------------------------ |
| **ZIP 다운로드** | 우측 상단 Download -> "Download as ZIP" -> 로컬에서 npm install    |
| **GitHub Push**  | 우측 상단 GitHub 아이콘 -> OAuth 인증 -> 기존/신규 레포에 Push     |
| **Get Code**     | "Get Code" 버튼 -> Python/JavaScript/REST API 코드 스니펫 복사     |

### Export된 코드 구조

Export된 프로젝트의 핵심 파일은 `geminiService.ts` (또는 동등한 API 호출 파일):

```typescript
// 원본 (Gemini)
import { GoogleGenerativeAI } from "@google/generative-ai";
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
```

이 부분을 Claude SDK로 교체:

```typescript
// 변경 후 (Claude)
import Anthropic from "@anthropic-ai/sdk";
const client = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY,
});
```

### 프롬프트 호환성

| 항목               | Gemini                  | Claude                                     |
| ------------------ | ----------------------- | ------------------------------------------ |
| **시스템 프롬프트** | `systemInstruction`     | `system` 파라미터 (Messages API)           |
| **멀티턴**         | `contents` 배열         | `messages` 배열 (role: user/assistant)     |
| **응답 형식**      | `generationConfig`      | `max_tokens`, `temperature` 등 별도 파라미터 |
| **도구/함수 호출** | `functionDeclarations`  | `tools` (다른 스키마 형식)                  |

### 선택 가능한 프레임워크 (2026년 2월 기준)

| 영역           | 선택 가능 옵션   | 기본값      |
| -------------- | ---------------- | ----------- |
| **프론트엔드** | React, Angular   | React       |
| **백엔드**     | Node.js          | Node.js     |
| **언어**       | TypeScript/JS    | TypeScript  |

---

## Edge Cases & Caveats

- **GitHub 연동은 새 프로젝트만 가능**: "The integration works only on new projects" -- 기존 앱에는 소급 적용 불가. ZIP 다운로드는 제약 없음
- **API 키 보안**: Export 후 API 키가 클라이언트 코드에 남아있을 수 있으므로, 반드시 서버사이드로 이동 필요
- **AI Studio 전용 기능 손실**: AI Studio 내의 "AI Chips" (Nano Banana 이미지 생성, Google Search grounding 등)는 Export 후 별도 API 연동 필요
- **도구/함수 호출(Function Calling)**: Gemini의 `functionDeclarations` 스키마와 Claude의 `tools` 스키마가 다르므로 수동 변환 필요
- **멀티모달 입력**: 이미지/비디오 처리 방식이 다를 수 있음
- **스트리밍 응답**: Gemini의 `generateContentStream`과 Claude의 streaming 방식이 다름

## Contradictions Found

- N/A -- 출처 간 모순 미발견

---

## Sources

1. [Google AI Studio Build Mode 공식문서](https://ai.google.dev/gemini-api/docs/aistudio-build-mode) -- 공식 문서
2. [The Complete Guide to Building with Google AI Studio](https://marily.substack.com/p/the-complete-guide-to-building-with) (Marily Nika) -- 기술 블로그
3. [Deploying Apps with Google AI Studio](https://www.kasunsameera.com/how-i-deploy-apps-with-google-ai-studio-full-tutorial-git-hub-tips) (Kasun Sameera) -- 기술 블로그
4. [Vibe Coding with Google AI Studio](https://designwithai.substack.com/p/vibe-coding-with-google-ai-studio) -- 기술 블로그
5. [Google AI Studio Build Mode: A Free Alternative to Cursor & Claude](https://www.aifire.co/p/google-ai-studio-build-mode-a-free-alternative-to-cursor-claude) -- 기술 블로그
6. [Introducing vibe coding in Google AI Studio](https://blog.google/innovation-and-ai/technology/developers-tools/introducing-vibe-coding-in-google-ai-studio/) -- Google 공식 블로그
7. [Vibe Coding IDE Tools Guide 2026](https://natively.dev/articles/vibe-coding-ide-tools) -- 기술 블로그
8. [Apiyi - Export Code Guide](https://help.apiyi.com/en/google-ai-studio-deploy-app-export-code-guide-en.html) -- 기술 블로그
9. [Anthropic SDK npm](https://www.npmjs.com/package/@anthropic-ai/sdk) -- 공식 문서
10. [Claude Prompt Improver](https://claude.com/blog/prompt-improver) -- 공식 블로그
11. [AI SDK Anthropic Provider](https://ai-sdk.dev/providers/ai-sdk-providers/anthropic) -- 기술 문서

## Research Metadata

- 검색 쿼리 수: 13 (일반 11 + SNS 2)
- 수집 출처 수: 11
- 출처 유형 분포: 공식 4, 1차 0, 블로그 7, 커뮤니티 0, SNS 0
- 확신도 분포: Confirmed 5, Likely 3, Synthesized 2, Uncertain 0, Unverified 0
- WebFetch 원문 확인: 7건 완료
- **한계**: "AI Studio -> Claude Code"만을 다룬 전용 튜토리얼은 발견하지 못함. 대부분 "AI Studio -> GitHub -> Cursor/VS Code" 패턴으로 설명되며, Claude Code는 동일 워크플로우에서 Cursor 자리를 대체하는 형태
