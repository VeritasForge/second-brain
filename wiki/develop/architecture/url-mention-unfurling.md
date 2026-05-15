---
tags: [url-mention, unfurling, open-graph, link-preview, python, ssrf, favicon]
created: 2026-05-15
updated: 2026-05-15
---

# 📖 URL Mention (URL Unfurling) — Concept Deep Dive

> 💡 **한줄 요약**: 메시지/문서에 붙여넣은 URL을 시스템이 자동으로 감지해서 제목·설명·이미지가 담긴 **미리보기 카드**로 펼쳐주는 기능 (= "Unfurling" = "두루마리 펴기").

> 🍱 **현실 비유 (12세 가정)**: 친구가 카톡에 유튜브 링크를 보내면 영상 썸네일이랑 제목이 자동으로 뜨죠? 그게 바로 **URL Mention/Unfurling**입니다. 마치 종이비행기(URL)에 그림책 표지(미리보기)를 자동으로 붙여주는 우체부와 같아요.

---

## 1️⃣ 무엇인가? (What is it?)

**URL Mention** (또는 **URL Unfurling**, **Link Preview**) 은 사용자가 입력한 텍스트 속의 URL을 **자동 감지**하고, 해당 페이지의 메타데이터를 가져와 **풍부한 미리보기 카드** (rich preview card) 로 렌더링하는 기능입니다.

- **탄생 배경**: 2010년 Facebook이 **Open Graph Protocol** (OGP) 을 발표하면서 표준화됨. 이후 **Slack**이 "**Unfurling**" (두루마리를 펼친다) 이라는 용어를 대중화시킴.
- **해결한 문제**: 텍스트 링크만 봐서는 어떤 콘텐츠인지 알 수 없는 문제 → 클릭 전에 미리보기를 제공하여 사용자 경험과 클릭률을 동시에 개선.
- **사용처**: Slack, Discord, X(Twitter), Facebook, LinkedIn, iMessage, Notion, Obsidian, KakaoTalk, Microsoft Teams 등 거의 모든 메시징/협업 플랫폼.

> 📌 **핵심 키워드**: `Unfurling`, `Open Graph Protocol (OGP)`, `Twitter Card`, `oEmbed`, `Link Preview`, `Metadata Extraction`, `Rich Preview Card`

---

## 2️⃣ 핵심 개념 (Core Concepts)

URL Mention 시스템은 크게 **3개 레이어**로 구성됩니다.

```
┌────────────────────────────────────────────────────────┐
│              URL Mention 핵심 구성 요소                │
├────────────────────────────────────────────────────────┤
│                                                        │
│   ┌──────────────────┐                                 │
│   │  ① Detector      │   "이 텍스트에 URL이 있나?"     │
│   │  (URL 감지기)     │   regex / linkify              │
│   └────────┬─────────┘                                 │
│            ▼                                           │
│   ┌──────────────────┐                                 │
│   │  ② Fetcher       │   "그 URL을 서버에서 GET"       │
│   │  (HTTP 수집기)    │   timeout, size-limit, SSRF가드 │
│   └────────┬─────────┘                                 │
│            ▼                                           │
│   ┌──────────────────┐                                 │
│   │  ③ Parser        │   "HTML 메타태그 뽑아내기"      │
│   │  (메타데이터 추출) │   OGP → Twitter → HTML         │
│   └──────────────────┘                                 │
│                                                        │
└────────────────────────────────────────────────────────┘
```

| 구성 요소     | 역할                       | 기술 예시                                |
| ------------- | -------------------------- | ---------------------------------------- |
| **Detector**  | 텍스트에서 URL 패턴 추출   | `linkify-it`, `re.findall`, Markdown autolink |
| **Fetcher**   | 서버사이드 HTTP GET        | `requests`, `httpx`, `aiohttp`           |
| **Parser**    | HTML 파싱 + 메타 추출      | `BeautifulSoup`, `lxml`, `metadata_parser` |
| **Cache**     | 같은 URL 중복 호출 방지    | Redis, Memcached, in-memory LRU          |
| **Renderer**  | 카드 UI 출력               | React, HTML 템플릿, Slack Block Kit      |

### 🏷️ 메타데이터 우선순위 (Fallback Chain)

대부분 플랫폼은 아래 **우선순위**로 메타데이터를 탐색합니다.

```
   1순위: Open Graph (OGP)     ┐
            og:title             │
            og:description       │  Facebook 주도 표준
            og:image             │
            og:url               │
                                 ┘
   2순위: Twitter Card           ┐
            twitter:title         │
            twitter:description    │  X (Twitter) 표준
            twitter:image          │
                                  ┘
   3순위: 표준 HTML <head>       ┐
            <title>               │  최후의 보루
            <meta name="desc..."> │
                                  ┘
   4순위: oEmbed Endpoint       ┐
            JSON 응답 (YouTube 등) │  Rich Embed
                                  ┘
```

> 💡 **🔖 Favicon은 별도 추출**: 위 4가지 메타는 카드의 **제목·설명·대표 이미지**를 결정하지만, **카드 왼쪽 상단의 작은 사이트 로고**(예: Slack 카드의 16~32px 아이콘)는 별도 경로로 가져옵니다. HTML `<head>`의 `<link rel="icon" href="...">` 또는 `<link rel="shortcut icon">` 태그를 파싱하거나, 관례적으로 `/favicon.ico` 경로를 직접 시도합니다. 메타 fallback chain과는 **독립된 다섯 번째 추출 단계**로 이해하면 됩니다. (자세한 내용은 본문 끝의 🔖 Appendix 참조)

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

### 🏗️ 전체 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│                    URL Mention 전체 흐름                      │
└──────────────────────────────────────────────────────────────┘

     ┌─────────┐                            ┌──────────────┐
     │  User   │  "https://example.com"     │ External Web │
     │ (Chat)  │      메시지 입력             │   (Origin)   │
     └────┬────┘                            └──────┬───────┘
          │ ① 메시지 전송                          ▲
          ▼                                       │
     ┌──────────────┐                              │ ④ HTML 응답
     │  Chat Server │  ② link_shared 이벤트         │   (32KB~)
     │  (Slack 등)  │ ────────────────────►        │
     └────┬─────────┘                              │
          │                                        │
          │ ③ Unfurl Worker가 URL GET 요청          │
          ▼                                        │
     ┌──────────────┐                              │
     │ Unfurl Worker│ ─────────────────────────────┘
     │  (백그라운드) │
     │  ┌────────┐  │
     │  │ Cache  │  │  ⑤ 캐시 hit 시 즉시 반환
     │  └────────┘  │
     │  ┌────────┐  │
     │  │ Parser │  │  ⑥ HTML → OGP 메타 추출
     │  └────────┘  │
     │  ┌────────┐  │
     │  │ SSRF   │  │  ⑦ 보안 검사 (사설 IP 차단)
     │  │ Guard  │  │
     │  └────────┘  │
     └──────┬───────┘
            │ ⑧ Preview Card 데이터 (JSON)
            ▼
     ┌──────────────┐
     │   Chat UI    │  ⑨ 사용자에게 카드 렌더링
     │  (Rendering) │
     └──────────────┘
```

### 🔄 동작 흐름 (Step by Step)

1. **URL 감지**: 클라이언트 또는 서버가 메시지 텍스트에서 URL 패턴을 추출 (Slack은 최대 5개까지 처리).
2. **이벤트 발행**: 서버는 `link_shared` 같은 비동기 이벤트를 큐(Queue)에 발행 → 메시지 전송은 즉시 완료 (UX 우선).
3. **캐시 조회**: 같은 URL이 최근 N분 내에 처리됐다면 캐시된 결과 사용 (Slack은 보통 수 시간 ~ 1일 캐싱).
4. **HTTP GET**: 캐시 미스 시 `User-Agent: Slackbot 1.0` 같은 식별자로 GET 요청 (Slack은 32KB까지만, Facebook 512KB, Twitter 1MB, LinkedIn 3MB).
5. **HTML 파싱**: 응답 본문에서 `<head>` 영역의 `<meta>` 태그를 파싱.
6. **메타 우선순위 적용**: OGP → Twitter Card → 표준 HTML 순서로 탐색.
7. **oEmbed 보강 (선택)**: YouTube, Vimeo, Twitter 같은 등록된 provider면 oEmbed 엔드포인트 호출.
8. **SSRF 가드**: 사설 IP (10.x, 172.16~31.x, 192.168.x), 링크-로컬 (169.254.x), 메타데이터 서버 (169.254.169.254) 차단.
9. **카드 렌더링**: 추출된 데이터를 카드 UI로 변환 → 사용자에게 표시.

### 💻 Open Graph 태그 예시

```html
<head>
  <!-- 1순위: OGP -->
  <meta property="og:title"       content="우리 서비스 소개" />
  <meta property="og:description" content="가장 빠른 채팅 앱입니다" />
  <meta property="og:image"       content="https://cdn.example.com/og.png" />
  <meta property="og:url"         content="https://example.com/about" />
  <meta property="og:type"        content="website" />

  <!-- 2순위: Twitter Card -->
  <meta name="twitter:card"  content="summary_large_image" />
  <meta name="twitter:title" content="우리 서비스 소개" />

  <!-- 3순위: HTML 표준 -->
  <title>우리 서비스 소개</title>
  <meta name="description" content="가장 빠른 채팅 앱입니다" />
</head>
```

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| #   | 유즈 케이스               | 설명                                     | 적합한 이유                |
| --- | ------------------------- | ---------------------------------------- | -------------------------- |
| 1   | 💬 **채팅 메시지 미리보기** | Slack/Discord에서 링크를 카드로 변환     | 클릭률↑, 컨텍스트 공유↑    |
| 2   | 📝 **노트 앱 임베드**       | Notion/Obsidian의 "Web Bookmark" 블록    | 외부 자료 큐레이션         |
| 3   | 🐦 **SNS 공유 카드**        | 트위터/페이스북 공유 시 카드 표시        | 콘텐츠 클릭 유도           |
| 4   | 📧 **이메일 클라이언트**     | Gmail/Outlook의 링크 미리보기            | 피싱 방지 + UX             |
| 5   | 🛒 **e커머스 봇**           | 상품 URL → 가격/이미지 카드              | 거래 컨텍스트 강화         |

### ✅ 베스트 프랙티스

1. **비동기 처리**: Unfurl 작업은 **반드시 백그라운드 워커**로. 메시지 전송 응답을 막지 마세요.
2. **HTTP 응답 크기 제한**: 32KB ~ 1MB 정도로 잘라서 다운로드 (`Range` 헤더 또는 stream 중 끊기). 악성 거대 파일 방어.
3. **타임아웃**: HTTP 요청에 **3~5초** 타임아웃 설정 (응답 지연으로 워커 점유 방지).
4. **캐싱 필수**: URL → 메타데이터 매핑을 Redis 등에 **최소 30분 ~ 24시간** 캐싱. 동일 URL 폭증 대비.
5. **User-Agent 명시**: `MyApp-LinkPreview/1.0 (+https://myapp.com/bot)` 처럼 식별 가능하게. robots.txt도 존중.
6. **이미지 크기 검증**: 50px 미만은 아이콘일 가능성, 3:1 초과 비율은 미리보기 부적합.
7. **HTTPS 강제**: HTTP만 응답하는 사이트도 HTTPS로 우선 시도.
8. **사용자 옵트아웃 제공**: 일부 사용자는 프라이버시 이유로 미리보기를 끄고 싶어함.

### 🏢 실제 적용 사례

- **Slack**: `Slackbot 1.0` UA로 32KB 다운로드 → OGP 파싱 → 자체 캐시 (자세히: [Slack Developer Docs](https://docs.slack.dev/messaging/unfurling-links-in-messages/))
- **Reddit**: 자회사 **Embedly**에 위임 — 거의 모든 사이트에 대한 메타데이터 추출 SaaS
- **Discord**: 디스코드 봇이 직접 fetch + OGP/oEmbed 파싱, 짧은 캐시
- **iMessage (Apple)**: **클라이언트 사이드** unfurl (디바이스가 직접 요청) — 프라이버시 우선이지만 SSRF 책임이 OS로 이동

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분    | 항목                  | 설명                                                  |
| ------- | --------------------- | ----------------------------------------------------- |
| ✅ 장점 | **UX 향상**           | 클릭 전에 콘텐츠 미리보기 가능 → 의사결정 시간 단축   |
| ✅ 장점 | **클릭률↑ (CTR)**     | 시각적 카드가 텍스트 링크보다 2~3배 높은 CTR          |
| ✅ 장점 | **컨텍스트 공유**     | "이 링크 봐" 한 마디로 무슨 내용인지 즉시 전달        |
| ✅ 장점 | **피싱 식별 단서**    | 표시된 도메인/제목과 실제 URL 불일치 시 의심 가능     |
| ❌ 단점 | **SSRF 공격 표면**    | 서버가 임의 URL을 fetch → 내부망 정찰 위험            |
| ❌ 단점 | **인프라 비용**       | 워커, 캐시, 네트워크 비용. 대규모는 무시 못 함        |
| ❌ 단점 | **프라이버시 누출**   | 비공개 링크 (예: Google Docs 공유) 가 서버에 노출     |
| ❌ 단점 | **지연/실패**         | 외부 사이트 응답 지연 → 카드 표시 누락/지연           |

### ⚖️ Trade-off 분석

```
   풍부한 미리보기      ◄────────────►   서버 부하/공격 표면
   (서버사이드)                          (SSRF, 비용)

   프라이버시 우선     ◄────────────►   디바이스 배터리/대역폭
   (클라이언트사이드)                    (모바일에서 불리)

   실시간성           ◄────────────►   캐시 일관성
   (즉시 fetch)                        (TTL 만료 정책 복잡)
```

---

## 6️⃣ 차이점 비교 (Comparison)

URL Mention을 구현하는 **3가지 표준/접근**을 비교합니다.

### 📊 비교 매트릭스

| 비교 기준              | **Open Graph (OGP)**      | **Twitter Card**          | **oEmbed**                       |
| ---------------------- | ------------------------- | ------------------------- | -------------------------------- |
| **주도 주체**          | Facebook (2010)           | X (Twitter)               | OpenEmbed 컨소시엄               |
| **데이터 형식**        | HTML `<meta>` 태그        | HTML `<meta>` 태그        | JSON/XML 응답                    |
| **반환 내용**          | 메타데이터 (텍스트+이미지 URL) | 메타데이터                | **임베드 가능한 HTML**           |
| **추출 방식**          | 페이지 HTML 파싱          | 페이지 HTML 파싱          | 별도 endpoint 호출               |
| **인터랙티브 임베드**  | ❌ 정적 카드만             | ❌ 정적 카드만             | ✅ 영상 재생 등 가능              |
| **구현 난이도**        | 🟢 매우 쉬움              | 🟢 쉬움                   | 🟡 중간 (provider 등록 필요)     |
| **적합한 경우**        | 일반 웹페이지             | 트위터 공유 최적화        | 동영상, 트윗 등 풍부한 임베드    |

### 🔍 핵심 차이 요약

```
   Open Graph                  Twitter Card                 oEmbed
   ──────────────────    vs    ──────────────────    vs    ──────────────────
   HTML 메타태그 파싱           HTML 메타태그 파싱            JSON API 호출
   정적 텍스트+이미지           정적 텍스트+이미지            <iframe> 등 동적 HTML
   범용 (모든 사이트)           트위터 카드 특화              사전 등록된 provider만
   1순위 폴백 표준              2순위 폴백                    YouTube, Vimeo, X
```

### 🤔 언제 무엇을 선택?

- **Open Graph (OGP)를 선택하세요** → 가장 범용적, **반드시 1순위로 구현**할 표준. 모든 메이저 플랫폼이 지원.
- **Twitter Card를 선택하세요** → OGP 외 보조용. OGP가 없을 때 폴백, 또는 트위터 전용 풍부 카드 (`summary_large_image`).
- **oEmbed를 선택하세요** → 동영상 재생, 트윗 인터랙티브 표시 같이 **iframe 임베드**가 필요할 때. provider 목록에 있는 도메인일 때만.

> 💡 **현실적인 답**: 셋 다 구현하세요. OGP를 기본으로 하되, oEmbed provider 화이트리스트가 있으면 우선 시도, 둘 다 실패하면 Twitter Card → HTML 표준 순으로 폴백.

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| #   | 실수                     | 왜 문제인가                                              | 올바른 접근                              |
| --- | ------------------------ | -------------------------------------------------------- | ---------------------------------------- |
| 1   | **SSRF 검증 누락**       | `http://169.254.169.254` (AWS 메타데이터) 로 자격증명 탈취 | 사설 IP/링크-로컬 차단 + DNS 재검증      |
| 2   | **응답 크기 무제한**     | 100GB 응답 시도 → 메모리 폭주                            | `stream=True` + chunk 누적 한도          |
| 3   | **동기 fetch**           | 메시지 응답이 외부 사이트 응답에 종속                    | 비동기 큐 + 백그라운드 워커              |
| 4   | **무한 리다이렉트**      | 악성 사이트가 무한 302 → 워커 점유                       | `max_redirects=5` 명시                   |
| 5   | **HTML 인코딩 무시**     | EUC-KR 페이지에서 한글 깨짐                              | `chardet`/`charset_normalizer`로 감지    |
| 6   | **캐시 부재**            | 동일 URL 폭증 시 외부 사이트 DDoS                        | URL → 메타 Redis 캐싱                    |
| 7   | **XSS 미처리**           | `og:title` 그대로 HTML 출력 시 스크립트 실행             | 출력 시 HTML escape                      |
| 8   | **favicon 상대 경로 미변환** | `<link rel="icon" href="/icon.png">` 그대로 저장 → 카드 렌더링 시 도메인 누락으로 404 | `urljoin(base_url, favicon_href)`로 절대 URL 변환 |

### 🚫 Anti-Patterns

1. **❌ 사용자 입력 URL을 검증 없이 fetch**: SSRF 1순위 공격 벡터. 반드시 **allowlist 도메인** 또는 **IP 검증** 필요.
2. **❌ 메시지 전송 응답에 unfurl 결과 포함**: 외부 사이트가 느리면 메시지 자체가 늦어짐. 비동기로 후속 패치.
3. **❌ 동일 URL에 매번 fetch**: 캐시 없이 운영하면 인기 링크 하나로 외부 사이트와 자기 워커 둘 다 죽음.

### 🔒 보안/성능 고려사항

- 🔐 **SSRF 방어 5계명**:
  1. URL을 **정규화 (canonicalize)** 후 **호스트 → IP 해석** 하여 검사
  2. **사설 대역 차단**: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `169.254.0.0/16`, `::1`, `fc00::/7`
  3. **DNS 재바인딩 방어**: 매 redirect hop마다 재해석
  4. **egress 방화벽**: unfurl 워커 컨테이너의 outbound는 default-deny + allowlist
  5. **응답 헤더 검사**: `Content-Type`이 `text/html` 또는 `application/xml`이 아니면 거부
- ⚡ **성능**: 대규모 트래픽은 **fetcher 노드 격리** (메인 서비스와 분리된 풀), **Circuit Breaker** (CB) 적용하여 느린 사이트가 워커 풀을 고갈시키지 못하게.
- 🔏 **프라이버시**: 비공개 URL (예: 만료 토큰 포함) 노출 가능성 → 옵트아웃 옵션 제공.

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit) — **Python 구현**

### 📚 학습 리소스

| 유형          | 이름                                                                                                                                                                                       | 설명                                       |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------ |
| 📖 공식 사양  | [The Open Graph protocol](https://ogp.me/)                                                                                                                                                 | OGP 1.1 공식 명세                          |
| 📖 공식 사양  | [oEmbed.com](https://oembed.com/)                                                                                                                                                          | oEmbed 1.0 명세 + provider 리스트          |
| 📖 공식 문서  | [Slack Unfurling Docs](https://docs.slack.dev/messaging/unfurling-links-in-messages/)                                                                                                      | Slack의 unfurl 구현 가이드                 |
| 📘 보안 가이드 | [OWASP SSRF Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)                                                          | SSRF 방어 패턴                             |
| 📺 블로그     | [Slack Platform Blog — Unfurling](https://medium.com/slack-developer-blog/everything-you-ever-wanted-to-know-about-unfurling-but-were-afraid-to-ask-or-how-to-make-your-e64b4bb9254)       | Slack 엔지니어의 unfurl 설계 회고          |

### 🛠️ Python 관련 라이브러리

| 라이브러리              | 용도                              | 비고                  |
| ----------------------- | --------------------------------- | --------------------- |
| `requests` / `httpx`    | HTTP 클라이언트                   | 표준                  |
| `beautifulsoup4`        | HTML 파싱                         | 표준                  |
| `lxml`                  | 더 빠른 파서                      | 보조                  |
| [`linkpreview`](https://pypi.org/project/linkpreview/) | URL → 미리보기 추출 라이브러리    | 간편                  |
| [`metadata_parser`](https://github.com/jvanasco/metadata_parser) | 프로덕션 검증된 메타 파서         | 대규모                |
| `charset-normalizer`    | 인코딩 자동 감지                  | 한글 사이트           |
| `ipaddress`             | SSRF용 IP 검증 (표준 라이브러리)  | 보안                  |

---

### 💻 Python 구현 예제

#### 🔧 예제 1: 가장 간단한 형태 (BeautifulSoup으로 직접 추출)

```python
"""url_preview_minimal.py
가장 단순한 URL Mention 구현.
프로덕션에서는 SSRF 가드 + 캐시 + 비동기 처리 필요.
"""
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


@dataclass
class LinkPreview:
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    site_name: Optional[str] = None


def _meta(soup: BeautifulSoup, *, attr: str, key: str) -> Optional[str]:
    tag = soup.find("meta", attrs={attr: key})
    return tag.get("content") if tag and tag.get("content") else None


def fetch_link_preview(url: str, *, timeout: float = 5.0) -> LinkPreview:
    headers = {
        "User-Agent": "MyApp-LinkPreview/1.0 (+https://myapp.com/bot)",
        "Accept": "text/html,application/xhtml+xml",
    }
    resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    title = (
        _meta(soup, attr="property", key="og:title")
        or _meta(soup, attr="name", key="twitter:title")
        or (soup.title.string.strip() if soup.title and soup.title.string else None)
    )
    description = (
        _meta(soup, attr="property", key="og:description")
        or _meta(soup, attr="name", key="twitter:description")
        or _meta(soup, attr="name", key="description")
    )
    image = (
        _meta(soup, attr="property", key="og:image")
        or _meta(soup, attr="name", key="twitter:image")
    )
    if image:
        image = urljoin(resp.url, image)  # 상대경로 → 절대경로

    site_name = _meta(soup, attr="property", key="og:site_name")

    return LinkPreview(
        url=resp.url,
        title=title,
        description=description,
        image=image,
        site_name=site_name,
    )


if __name__ == "__main__":
    preview = fetch_link_preview("https://www.python.org/")
    print(preview)
```

---

#### 🔒 예제 2: SSRF 가드 + 응답 크기 제한 + 인코딩 감지 (프로덕션 권장)

```python
"""url_preview_safe.py
프로덕션용 URL 미리보기 — SSRF 방어, 크기 제한, 인코딩 자동 감지.
"""
import ipaddress
import socket
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from charset_normalizer import from_bytes

MAX_BYTES = 512 * 1024          # 최대 512KB만 받음
CONNECT_TIMEOUT = 3.0
READ_TIMEOUT = 5.0
ALLOWED_SCHEMES = {"http", "https"}
MAX_REDIRECTS = 5


class UnsafeURLError(Exception):
    """SSRF 위험 URL"""


@dataclass
class LinkPreview:
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    site_name: Optional[str] = None
    favicon: Optional[str] = None


# ─────────────────────────────────────────────────────────────
# SSRF 가드: 호스트를 IP로 해석한 뒤 사설/예약 대역인지 검사
# ─────────────────────────────────────────────────────────────
def _resolve_safe_ip(hostname: str) -> str:
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as e:
        raise UnsafeURLError(f"DNS 해석 실패: {hostname}") from e

    for family, _, _, _, sockaddr in infos:
        ip_str = sockaddr[0]
        ip_obj = ipaddress.ip_address(ip_str)
        # 사설/링크로컬/루프백/멀티캐스트/예약/메타데이터 차단
        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_multicast
            or ip_obj.is_reserved
            or ip_obj.is_unspecified
        ):
            raise UnsafeURLError(f"차단된 IP 대역: {ip_str} ({hostname})")
        # AWS/GCP 메타데이터 서버 명시 차단
        if ip_str == "169.254.169.254":
            raise UnsafeURLError("클라우드 메타데이터 서버 접근 차단")
    return infos[0][4][0]


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise UnsafeURLError(f"허용되지 않은 scheme: {parsed.scheme}")
    if not parsed.hostname:
        raise UnsafeURLError("호스트 없음")
    _resolve_safe_ip(parsed.hostname)


# ─────────────────────────────────────────────────────────────
# 본문은 stream으로 읽고 한도 초과 시 중단
# ─────────────────────────────────────────────────────────────
def _safe_get(url: str) -> requests.Response:
    headers = {
        "User-Agent": "MyApp-LinkPreview/1.0 (+https://myapp.com/bot)",
        "Accept": "text/html,application/xhtml+xml",
    }
    session = requests.Session()
    session.max_redirects = MAX_REDIRECTS

    # 매 redirect hop마다 다시 검증 (DNS Rebinding 방어)
    resp = session.get(
        url,
        headers=headers,
        timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
        stream=True,
        allow_redirects=False,
    )
    hops = 0
    while resp.is_redirect or resp.is_permanent_redirect:
        hops += 1
        if hops > MAX_REDIRECTS:
            raise UnsafeURLError("리다이렉트 너무 많음")
        next_url = urljoin(resp.url, resp.headers["Location"])
        _validate_url(next_url)
        resp = session.get(
            next_url,
            headers=headers,
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            stream=True,
            allow_redirects=False,
        )

    ctype = resp.headers.get("Content-Type", "").lower()
    if not any(t in ctype for t in ("text/html", "application/xhtml", "application/xml")):
        raise UnsafeURLError(f"HTML 아님: {ctype}")

    # 크기 제한 stream
    buffer = bytearray()
    for chunk in resp.iter_content(chunk_size=8192):
        buffer.extend(chunk)
        if len(buffer) >= MAX_BYTES:
            break
    resp._content = bytes(buffer)  # type: ignore[attr-defined]
    return resp


# ─────────────────────────────────────────────────────────────
# 메타데이터 추출 (OGP → Twitter → HTML 표준 폴백)
# ─────────────────────────────────────────────────────────────
def _meta(soup: BeautifulSoup, *, attr: str, key: str) -> Optional[str]:
    tag = soup.find("meta", attrs={attr: key})
    if tag and tag.get("content"):
        return tag["content"].strip()
    return None


def _decode(resp: requests.Response) -> str:
    raw = resp.content
    # charset-normalizer로 인코딩 자동 감지 (EUC-KR 한글 페이지 대응)
    result = from_bytes(raw).best()
    return str(result) if result else raw.decode("utf-8", errors="replace")


def fetch_link_preview(url: str) -> LinkPreview:
    _validate_url(url)
    resp = _safe_get(url)
    html = _decode(resp)
    soup = BeautifulSoup(html, "html.parser")

    title = (
        _meta(soup, attr="property", key="og:title")
        or _meta(soup, attr="name", key="twitter:title")
        or (soup.title.string.strip() if soup.title and soup.title.string else None)
    )
    description = (
        _meta(soup, attr="property", key="og:description")
        or _meta(soup, attr="name", key="twitter:description")
        or _meta(soup, attr="name", key="description")
    )
    image = (
        _meta(soup, attr="property", key="og:image")
        or _meta(soup, attr="name", key="twitter:image")
    )
    if image:
        image = urljoin(resp.url, image)

    site_name = _meta(soup, attr="property", key="og:site_name")

    # ─ Favicon 추출 (메타와 별개) ─
    # OGP/Twitter Card 어디에도 favicon은 없음 → <link rel="icon"> 직접 탐색.
    # rel은 "icon" / "shortcut icon" / "apple-touch-icon" 등 다양 → 부분일치로 감지.
    favicon_tag = soup.find("link", rel=lambda v: v and "icon" in v.lower())
    favicon = urljoin(resp.url, favicon_tag["href"]) if favicon_tag and favicon_tag.get("href") else None

    return LinkPreview(
        url=resp.url,
        title=title,
        description=description,
        image=image,
        site_name=site_name,
        favicon=favicon,
    )


if __name__ == "__main__":
    try:
        print(fetch_link_preview("https://www.python.org/"))
        # SSRF 시뮬레이션 — 차단되어야 함
        print(fetch_link_preview("http://169.254.169.254/latest/meta-data/"))
    except UnsafeURLError as e:
        print(f"❌ 차단됨: {e}")
```

---

#### 🚀 예제 3: 비동기 + 캐싱 (대규모 채팅 서버 시나리오)

```python
"""url_preview_async.py
async + Redis 캐싱 — 채팅 서버용 unfurl 워커.
"""
import asyncio
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from typing import Optional

import httpx
import redis.asyncio as redis
from bs4 import BeautifulSoup

URL_REGEX = re.compile(r"https?://[^\s<>\"']+")
CACHE_TTL_SEC = 60 * 60 * 6   # 6시간


@dataclass
class LinkPreview:
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None


def detect_urls(text: str, max_n: int = 5) -> list[str]:
    """메시지 텍스트에서 URL을 최대 N개 감지 (Slack은 5)."""
    return URL_REGEX.findall(text)[:max_n]


def _cache_key(url: str) -> str:
    return "linkpreview:" + hashlib.sha256(url.encode()).hexdigest()


async def _parse(client: httpx.AsyncClient, url: str) -> LinkPreview:
    headers = {"User-Agent": "MyApp-LinkPreview/1.0"}
    resp = await client.get(url, headers=headers, timeout=5.0, follow_redirects=True)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    def meta(attr: str, key: str) -> Optional[str]:
        t = soup.find("meta", attrs={attr: key})
        return t["content"].strip() if t and t.get("content") else None

    return LinkPreview(
        url=str(resp.url),
        title=meta("property", "og:title") or (soup.title.string if soup.title else None),
        description=meta("property", "og:description") or meta("name", "description"),
        image=meta("property", "og:image"),
    )


async def fetch_preview(
    client: httpx.AsyncClient,
    cache: redis.Redis,
    url: str,
) -> LinkPreview:
    key = _cache_key(url)

    # ─ 캐시 hit ─
    cached = await cache.get(key)
    if cached:
        return LinkPreview(**json.loads(cached))

    # ─ 캐시 miss → 외부 fetch ─
    preview = await _parse(client, url)

    # 결과 캐싱 (음성 캐싱: 실패 시에도 짧게 캐싱 권장)
    await cache.set(key, json.dumps(asdict(preview)), ex=CACHE_TTL_SEC)
    return preview


async def unfurl_message(text: str) -> list[LinkPreview]:
    """메시지의 모든 URL을 병렬로 unfurl."""
    urls = detect_urls(text)
    if not urls:
        return []

    cache = redis.Redis(host="localhost", port=6379, decode_responses=True)
    async with httpx.AsyncClient(http2=True) as client:
        results = await asyncio.gather(
            *(fetch_preview(client, cache, u) for u in urls),
            return_exceptions=True,
        )
    return [r for r in results if isinstance(r, LinkPreview)]


if __name__ == "__main__":
    msg = "이 두 사이트 봐줘 https://python.org 그리고 https://fastapi.tiangolo.com"
    previews = asyncio.run(unfurl_message(msg))
    for p in previews:
        print(p)
```

> ⚠️ 위 비동기 예제도 프로덕션에서는 **예제 2의 SSRF 가드와 응답 크기 제한**을 결합해 사용해야 합니다 (간결성을 위해 생략).

---

#### 📦 예제 4: 기성 라이브러리 사용 (linkpreview)

```python
"""url_preview_lib.py
직접 만들지 않고 검증된 라이브러리 사용."""
from linkpreview import link_preview

preview = link_preview("https://www.python.org/")
print(preview.title)        # Welcome to Python.org
print(preview.description)
print(preview.image)
print(preview.site_name)
print(preview.absolute_image)
```

---

### 🔮 트렌드 & 전망

- 🤖 **AI 요약 카드**: 단순 메타데이터를 넘어 LLM이 페이지를 읽어 **요약**을 카드에 표시 (Notion AI, Arc Browser).
- 🧱 **Slack Block Kit / Adaptive Cards**: 정적 카드 → 버튼·폼이 있는 **인터랙티브 카드**로 진화.
- 🔐 **프라이버시 우선 unfurl**: iMessage처럼 **클라이언트 사이드**로 이동하는 흐름 (Signal 등).
- 🌐 **Fediverse 표준화**: Mastodon, Bluesky 등이 OGP 호환하면서 표준 위치가 더 공고해짐.
- 🚧 **Agent 시대의 새 표준**: AI 에이전트가 URL 콘텐츠를 읽기 위해 OGP보다 풍부한 **structured data (JSON-LD)** 가 더 중요해지는 추세.
- 🌗 **다크모드 대응 favicon**: SVG favicon + `prefers-color-scheme` 미디어 쿼리 또는 PWA `manifest.json`의 `theme_color`로 카드 배경/아이콘이 시스템 테마 따라 자동 전환되는 흐름. 모바일 메신저 카드 UI에서 점점 표준화 중.

### 💬 커뮤니티 인사이트

- "Reddit은 자체 처리하지 않고 자회사 **Embedly**에 위임한다 — 굳이 직접 만들 필요 없으면 SaaS 검토" — DEV Community
- "iMessage의 클라이언트 사이드 unfurl은 프라이버시는 좋지만, 일부 사이트의 분석 트래커에 모든 수신자 디바이스가 노출되는 문제가 있다" — 9to5Mac 보안 연구
- "프로덕션에서 가장 자주 터지는 버그는 **상대 경로 og:image**를 절대 URL로 변환 안 한 케이스" — Andrej Gajdos 블로그

---

## 📎 Sources

1. [Slack — Unfurling links in messages](https://docs.slack.dev/messaging/unfurling-links-in-messages/) — 공식 문서
2. [Slack Platform Blog — Everything about unfurling](https://medium.com/slack-developer-blog/everything-you-ever-wanted-to-know-about-unfurling-but-were-afraid-to-ask-or-how-to-make-your-e64b4bb9254) — 엔지니어 블로그
3. [URL Unfurling: How Slack, Discord and Twitter Generate Link Previews](https://dev.to/eatyou_eatyou_d79d27e5622/url-unfurling-how-slack-discord-and-twitter-generate-link-previews-5hgb) — 기술 블로그
4. [The Open Graph protocol — ogp.me](https://ogp.me/) — 공식 사양
5. [oEmbed.com](https://oembed.com/) — 공식 사양
6. [OWASP — SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) — 보안 가이드
7. [PortSwigger — SSRF Web Security Academy](https://portswigger.net/web-security/ssrf) — 보안 학습
8. [linkpreview — PyPI](https://pypi.org/project/linkpreview/) — Python 라이브러리
9. [metadata_parser — GitHub](https://github.com/jvanasco/metadata_parser) — Python 라이브러리
10. [Generating Website Previews with Python — bytescrum](https://blog.bytescrum.com/generating-website-previews-with-python-a-step-by-step-guide) — Python 튜토리얼
11. [How to Create a Link Preview (Definitive Guide) — Andrej Gajdos](https://andrejgajdos.com/how-to-create-a-link-preview/) — 종합 가이드
12. [9to5Mac — Link preview privacy research](https://9to5mac.com/2020/10/26/researchers-demonstrate-how-link-previews-in-apps-can-expose-data-from-users/) — 프라이버시 연구
13. [RealFaviconGenerator](https://realfavicongenerator.net/) — Favicon 멀티 사이즈 생성 도구
14. [MDN — `<link rel="icon">` 사양](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link) — favicon HTML 사양

---

## 🔖 Appendix: Favicon — URL Mention 카드의 사이트 로고

URL Mention 카드 왼쪽 상단의 작은 아이콘이 어디서 오는지, 발행자(콘텐츠 작성자) 입장에서 어떻게 만들어야 하는지를 정리합니다.

### A-1. Favicon이란?

> **Favicon** = **Fav**orites + **icon** 합성어. **Microsoft Internet Explorer 5** (1999) 에서 처음 도입. 사이트의 "이름표 스티커" 역할.

#### 🍱 현실 비유

학교 사물함 100개가 줄지어 있어도 본인 이름표 스티커로 자기 사물함을 찾듯, 브라우저 탭 100개가 열려있어도 favicon만 보면 어느 사이트인지 즉시 알 수 있습니다.

#### 📍 favicon이 등장하는 곳

```
┌──────────────────────────────────────────────────────────┐
│   🔖 Favicon이 등장하는 6곳                              │
├──────────────────────────────────────────────────────────┤
│  ① 브라우저 탭             [🐍 Python.org × ]            │
│  ② 북마크/즐겨찾기          ⭐ 🐍 Welcome to Python      │
│  ③ 주소창 (일부 브라우저)   🐍 https://python.org        │
│  ④ 검색 결과                🐍 python.org                │
│  ⑤ 홈 화면 추가 (모바일)    [📱 앱 아이콘처럼]           │
│  ⑥ URL Mention 카드 로고    💬 Slack/Discord/노션 카드   │ ← 이 문서의 관심사
└──────────────────────────────────────────────────────────┘
```

### A-2. favicon.jpg 인가? — 아니요

가장 흔한 건 `.ico`, 현대 표준은 `.png`/`.svg`. **JPG는 권장하지 않습니다**.

| 확장자        | 지원 여부        | 추천도   | 이유                                                  |
| ------------- | ---------------- | -------- | ----------------------------------------------------- |
| `.ico`        | ✅ 모든 브라우저 | ⭐⭐⭐⭐   | 전통 표준, 한 파일에 여러 해상도 (16/32/48px) 담음    |
| `.png`        | ✅ 모든 브라우저 | ⭐⭐⭐⭐⭐ | **현대 표준**, 투명 배경 지원, 가벼움                 |
| `.svg`        | ✅ 모던 브라우저 | ⭐⭐⭐⭐⭐ | 벡터 → 무한 확대, 다크모드 대응 가능                  |
| `.gif`        | ✅ 가능          | ⭐⭐       | 애니메이션 가능하지만 지저분, 거의 안 씀              |
| `.jpg/.jpeg`  | ⚠️ 가능하지만    | ❌       | **투명 배경 불가** → 흰색/검은색 배경이 떡 됨         |

> 💡 16~48px 작은 사이즈에서 JPG는 **압축 노이즈가 보기 흉**하고 **투명 배경**도 안 됩니다. PNG/ICO/SVG 중 선택하세요.

### A-3. HTML에서 발행하는 방법

#### 방법 1: 관례 (Convention) — 가장 간단

홈페이지 루트에 `/favicon.ico` 파일만 두면 브라우저가 자동으로 `GET https://yoursite.com/favicon.ico` 요청.

#### 방법 2: HTML `<link>` 태그 — **권장**

```html
<head>
  <!-- 🌟 기본 favicon -->
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png" />
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16.png" />

  <!-- 🍎 iOS 홈 화면 추가용 (touch icon) -->
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />

  <!-- 🤖 Android Chrome용 -->
  <link rel="manifest" href="/site.webmanifest" />

  <!-- 🌗 SVG + 다크모드 대응 (옵션) -->
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
</head>
```

### A-4. 권장 사이즈 매트릭스

| 사이즈     | 용도                              |
| ---------- | --------------------------------- |
| 16×16      | 브라우저 탭 (Windows)             |
| 32×32      | 브라우저 탭 (고해상도/macOS)      |
| 48×48      | Windows 작업표시줄                |
| 180×180    | iOS 홈 화면 (`apple-touch-icon`)  |
| 192×192    | Android Chrome (PWA)              |
| 512×512    | 스플래시 스크린, PWA              |

> 🛠️ 실무에서는 [RealFaviconGenerator](https://realfavicongenerator.net/) 같은 도구에 PNG 한 장 올리면 위 사이즈를 **한 번에 생성**해줍니다.

### A-5. 발행자 측 흔한 함정

본문 7️⃣의 함정 #8(추출 측 함정)과 별개로, **사이트 발행자**가 자주 겪는 함정:

| 함정                       | 증상                                | 해결                                                          |
| -------------------------- | ----------------------------------- | ------------------------------------------------------------- |
| **브라우저 캐시**          | favicon 바꿔도 옛날 게 보임         | 강제 새로고침 (Ctrl+Shift+R) 또는 파일명 버저닝 (`favicon-v2.png`) |
| **HTTP/HTTPS 혼용**        | HTTPS 페이지에서 HTTP favicon 차단  | 항상 HTTPS 절대 URL 또는 `//cdn.example.com` 프로토콜 상대    |
| **iOS만 touch icon 없음**  | 홈 화면 추가 시 회색 박스           | `apple-touch-icon.png` (180×180) 별도 추가                    |
| **상대 경로 카드 깨짐**    | unfurl 카드에서 아이콘 404          | 서버 응답 `<link rel="icon" href="...">`를 절대 경로로 변환   |

### A-6. URL Mention 카드 입장에서의 favicon

| 관점                                  | 역할                                                                                  |
| ------------------------------------- | ------------------------------------------------------------------------------------- |
| **사이트 발행자**                     | `<link rel="icon">`로 favicon을 노출 → 미리보기 카드에 자기 브랜드 노출 가능          |
| **카드 추출자** (이 문서의 unfurl 코드) | HTML 파싱 시 `<link rel="...icon...">` 탐색 + `urljoin`으로 절대 URL 변환             |
| **카드 렌더러**                       | 카드 UI에 16~32px 작은 아이콘으로 표시 (대표 이미지 og:image와는 별개)                |

### A-7. 더 알아볼 만한 것들

- 🌗 **다크모드 대응 favicon**: SVG + `prefers-color-scheme` 미디어 쿼리
- 📱 **PWA `manifest.json`**: 홈 화면 아이콘, 스플래시, 테마 색상 통합 관리
- 🔍 **검색 SEO**: Google 검색 결과에 favicon 노출 → 클릭률 영향 (Google은 `apple-touch-icon` 우선 사용)
- 🛡️ **보안**: favicon 해시로 사이트 fingerprinting 추적 가능 (Shodan favicon hash search)

---

## 🎯 핵심 정리 (TL;DR)

| 항목             | 한 줄 정리                                                       |
| ---------------- | ---------------------------------------------------------------- |
| **무엇**         | URL을 자동 감지 → 메타데이터 추출 → 미리보기 카드                |
| **표준**         | OGP (1순위) > Twitter Card > HTML `<title>/<meta>` > oEmbed      |
| **흐름**         | Detect → Fetch → Parse → Cache → Render (비동기 필수)            |
| **위험**         | SSRF, 거대 응답, 무한 redirect, 인코딩 문제                      |
| **Python 스택**  | `httpx` + `BeautifulSoup` + `redis` + `ipaddress` (SSRF)         |
| **빠른 시작**    | `pip install linkpreview` 후 `link_preview(url)` 한 줄           |

> 📌 **추천 다음 단계**: 예제 2 (SSRF-safe 동기) → 예제 3 (async + 캐싱) 순서로 따라 만들어보세요. 본인 서비스에 붙일 때는 **응답 크기 제한**과 **사설 IP 차단**만큼은 절대 빼지 마세요. 이 두 가지가 신문 1면감 사고를 막아주는 안전벨트입니다.
