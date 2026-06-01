# 📖 Set-Cookie & 쿠키 보안 속성 — Concept Deep Dive

> 💡 **한줄 요약**: `Set-Cookie`는 서버가 브라우저에 상태(세션·토큰)를 저장시키는 HTTP 응답 헤더이고, `HttpOnly`·`Secure`·`SameSite` 같은 **속성(attribute)** 이 그 쿠키를 "누가·언제·어떻게" 다룰 수 있는지를 정해 XSS·CSRF·MITM 공격을 막는 안전장치다.

> 🧭 **관련 노트**: [[oauth2-concept-explainer]] · [[sso-oauth-comparison-and-architecture]] · [[http1-1-concept-explainer]] · [[http2-concept-explainer]]

---

## 1️⃣ 무엇인가? (What is it?)

**쿠키(Cookie)** 는 HTTP가 **무상태(stateless)** 프로토콜이라는 한계를 메우기 위해 등장한 "작은 메모지"다. 서버는 응답에 `Set-Cookie` 헤더를 실어 브라우저에게 "이 값을 적어뒀다가 다음에 올 때 보여줘"라고 부탁하고, 브라우저는 이후 같은 사이트로 가는 요청마다 `Cookie` 헤더에 그 값을 자동으로 담아 보낸다.

- **공식 정의**: `Set-Cookie` HTTP 응답 헤더는 서버에서 사용자 에이전트(브라우저)로 쿠키를 전송하여 저장하게 한다 ([MDN: Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)).
- **표준**: [RFC 6265](https://datatracker.ietf.org/doc/html/rfc6265) (HTTP State Management Mechanism), 그리고 보안 강화를 다루는 후속 초안 RFC 6265bis.
- **탄생 배경**: 1994년 Netscape의 Lou Montulli가 장바구니 상태를 기억시키려 고안. 처음엔 "값을 저장"하는 기능만 있었지만, 이 값이 **세션 ID·인증 토큰**을 담게 되면서 "어떻게 안전하게 다룰지"가 핵심 문제가 되었고 → `HttpOnly`(2002, IE6 SP1)·`Secure`·`SameSite`(2016~) 속성이 차례로 추가됐다.

> 📌 **핵심 키워드**: `Set-Cookie`, `attribute`, `HttpOnly`, `Secure`, `SameSite`, `세션 관리`

> 🍪 **12살용 비유**: 쿠키는 놀이공원 입장 후 손목에 채워주는 **종이 팔찌**다. `Set-Cookie`는 직원이 팔찌를 채워주는 행위, 속성들은 팔찌에 적힌 규칙("물에 젖으면 안 됨"=Secure, "본인만 보여줄 수 있음"=HttpOnly, "옆 놀이공원에선 안 통함"=SameSite)이다.

---

## 2️⃣ 핵심 개념 (Core Concepts)

쿠키 하나는 `이름=값` 뒤에 **세미콜론으로 구분된 속성들**이 붙는 구조다. 속성은 크게 ① **스코프(범위)를 정하는 것**과 ② **보안을 정하는 것**, ③ **수명을 정하는 것** 세 갈래로 나뉜다.

```
Set-Cookie: sessionId=abc123; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600
            └──────┬──────┘  └──┬───┘ └─┬──┘ └────┬─────┘ └─┬─┘ └────┬─────┘
              이름=값          보안     보안    보안       스코프    수명
```

┌──────────────────────────────────────────────────────────┐
│             쿠키 속성 3대 분류 (ASCII)                      │
├──────────────────────────────────────────────────────────┤
│   🔒 보안(Security)    📍 스코프(Scope)   ⏰ 수명(Lifetime)  │
│   ├ HttpOnly           ├ Domain          ├ Max-Age         │
│   ├ Secure             └ Path            └ Expires         │
│   └ SameSite                            (둘 다 없으면        │
│                                          = Session Cookie)  │
└──────────────────────────────────────────────────────────┘

| 속성 | 분류 | 역할 | 한 줄 설명 |
|------|------|------|-----------|
| `HttpOnly` | 🔒 보안 | XSS 방어 | JavaScript의 `document.cookie` 접근 차단 |
| `Secure` | 🔒 보안 | MITM 방어 | HTTPS 연결에서만 전송 (localhost는 대부분 브라우저가 예외 처리 — 사설 IP·기타 http 호스트는 예외 아님) |
| `SameSite` | 🔒 보안 | CSRF 방어 | 교차 사이트 요청 시 전송 여부 제어 |
| `Domain` | 📍 스코프 | 전송 대상 호스트 | 어떤 도메인/서브도메인에 보낼지 |
| `Path` | 📍 스코프 | 전송 대상 경로 | 어떤 URL 경로에 보낼지 |
| `Max-Age` | ⏰ 수명 | 상대 만료 | 지금부터 N초 뒤 만료 (우선순위 높음) |
| `Expires` | ⏰ 수명 | 절대 만료 | 특정 GMT 시각에 만료 |

> 📌 **우선순위 규칙**: `Max-Age`와 `Expires`가 함께 있으면 **`Max-Age`가 이긴다**. 둘 다 없으면 브라우저를 닫을 때 사라지는 **세션 쿠키(Session Cookie)** 가 된다.

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

### 🔄 동작 흐름 (Step by Step)

```
┌─────────┐                                      ┌─────────┐
│ Browser │                                      │ Server  │
└────┬────┘                                      └────┬────┘
     │  1. POST /login (id, pw)                       │
     │ ─────────────────────────────────────────────▶│
     │                                                │ 2. 인증 성공
     │                                                │    세션 생성
     │  3. 200 OK                                     │
     │     Set-Cookie: sid=abc; HttpOnly;             │
     │                 Secure; SameSite=Lax           │
     │ ◀─────────────────────────────────────────────│
     │  4. 쿠키 저장소(jar)에 보관                      │
     │     (JS는 HttpOnly라 못 읽음)                    │
     │                                                │
     │  5. GET /dashboard                             │
     │     Cookie: sid=abc   ← 자동 첨부               │
     │ ─────────────────────────────────────────────▶│
     │                                                │ 6. sid 검증 → 사용자 식별
     │  7. 200 OK (개인화 페이지)                       │
     │ ◀─────────────────────────────────────────────│
```

1. **Step 1**: 브라우저가 로그인 요청을 보냄
2. **Step 2**: 서버가 인증 후 세션을 만들고 세션 ID를 발급
3. **Step 3**: `Set-Cookie` 헤더로 세션 ID + 보안 속성을 응답에 실음
4. **Step 4**: 브라우저가 쿠키 저장소(cookie jar)에 저장. **`HttpOnly`라서 JS는 못 읽음**
5. **Step 5~6**: 이후 같은 사이트 요청마다 브라우저가 `Cookie` 헤더를 **자동 첨부** → 서버가 사용자 식별
6. **핵심**: 개발자가 코드로 쿠키를 붙이지 않아도 **브라우저가 자동으로** 첨부한다. 바로 이 "자동성"이 편리함이자 동시에 CSRF (Cross-Site Request Forgery)의 빌미가 된다.

### 💻 서버 응답 예시

```http
HTTP/1.1 200 OK
Content-Type: text/html
Set-Cookie: sessionId=9f2k...; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600
Set-Cookie: theme=dark; Path=/; Max-Age=31536000
```

> ⚙️ **중요**: 한 응답에 **여러 개의 `Set-Cookie` 헤더**를 둘 수 있다(쿠키 1개당 1줄). 반면 브라우저가 보내는 `Cookie` 요청 헤더는 모든 쿠키를 세미콜론으로 묶어 **한 줄**로 보낸다.

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| # | 유즈 케이스 | 권장 속성 조합 | 적합한 이유 |
|---|------------|--------------|------------|
| 1 | 세션 ID / 인증 토큰 | `HttpOnly; Secure; SameSite=Lax` | JS 탈취 차단 + HTTPS 전용 + CSRF 완화 |
| 2 | Refresh Token | `HttpOnly; Secure; SameSite=Strict; Path=/auth/refresh` | 최고 보안 + 갱신 엔드포인트로 스코프 한정 |
| 3 | UI 테마·언어 설정 | (속성 최소, `HttpOnly` 불필요) | 민감하지 않고 JS가 읽어야 함 |
| 4 | 결제·은행 등 고보안 세션 | `HttpOnly; Secure; SameSite=Strict` | 교차 사이트 유입 완전 차단 |

### ✅ 베스트 프랙티스

1. **민감 쿠키엔 항상 `HttpOnly; Secure` 세트로**: 세션·인증 토큰은 예외 없이.
2. **기본은 `SameSite=Lax`, 고보안은 `Strict`**: 단, **외부 PG(결제 게이트웨이)의 cross-site `POST` 리다이렉트 복귀**나 **OAuth `response_mode=form_post` 콜백**처럼 *top-level cross-site POST*로 돌아오는 흐름에서는 Lax 쿠키가 **전송되지 않아 세션이 끊긴다**(Lax는 top-level GET 네비게이션에만 전송). 이런 경로는 별도 처리(예: 해당 콜백만 `None; Secure`)가 필요.
3. **`__Host-` 접두사 활용**: 쿠키 이름을 `__Host-sid`로 시작하면 브라우저가 `Secure` + `Path=/` + `Domain` 미지정을 **강제** → 서브도메인이 상위 도메인 쿠키를 **덮어쓰는 공격(cookie overwrite)** 방어 ([MDN: Cookie prefixes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies#cookie_prefixes)). ⚠️ 단 `__Host-`는 `Domain` 미지정(host-only)이라 **서브도메인 간 쿠키 공유가 불가** → `auth.example.com`↔`app.example.com` 공유가 필요한 SSO 쿠키엔 부적합하므로 `__Secure-`를 고려.
4. **수명은 짧게 + refresh token은 회전(rotation)**: access token 쿠키는 분 단위, refresh token만 길게 두되 **쓸 때마다 새로 발급(rotation)하고 이전 토큰 재사용을 탐지(reuse detection)**해 유출 시 무효화한다 — 회전 없이 길게 두면 한 번 새면 영구 악용된다.
5. **토큰 저장: BFF가 1순위, 하이브리드는 차선**: IETF `draft-ietf-oauth-browser-based-apps`·OWASP는 **BFF(Backend-for-Frontend)/Token-Handler 패턴**(토큰을 브라우저에 두지 않고 백엔드 프록시가 보관)을 보안 1순위로 권고한다. 백엔드 프록시를 둘 수 없을 때의 차선책이 **하이브리드** — short-lived **access token은 메모리(JS 변수)**, long-lived **refresh token은 HttpOnly Secure 쿠키**다. 단 이건 XSS·CSRF 위험을 **완화할 뿐 제거하지 못한다**: XSS가 발생하면 메모리의 access token도 런타임에 읽히거나 refresh 쿠키로 새 토큰을 재발급받아 세션 라이딩이 가능하다(HttpOnly는 *읽기*만 막지 *사용*은 못 막음). 근본 방어는 XSS 자체 차단(CSP·출력 인코딩)이다 ([OWASP Session Mgmt Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html), [Wisp: Token Storage](https://www.wisp.blog/blog/understanding-token-storage-local-storage-vs-httponly-cookies)).

### 🏢 실제 적용 사례

- **OAuth 2.0 / SSO 세션**: 인가 서버가 발급한 세션을 `HttpOnly; Secure` 쿠키로 보관 → [[oauth2-concept-explainer]], [[sso-oauth-comparison-and-architecture]] 참고.
- **Google / Microsoft 로그인**: SameSite 변경(Chrome 80)에 맞춰 third-party 인증 쿠키에 `SameSite=None; Secure` 명시 ([Microsoft Learn](https://learn.microsoft.com/en-us/entra/identity-platform/howto-handle-samesite-cookie-changes-chrome-browser)).

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ 장점 | 자동 전송 | 브라우저가 매 요청에 자동 첨부 → 구현 단순 |
| ✅ 장점 | `HttpOnly` XSS 방어 | JS로 토큰을 못 읽으므로 스크립트 주입돼도 탈취 어려움 |
| ✅ 장점 | 표준·범용 | 모든 브라우저·서버가 RFC 6265 지원 |
| ❌ 단점 | CSRF 노출 | 자동 전송 특성 탓에 위조 요청에 쿠키가 딸려감 → `SameSite`/토큰 필요 |
| ❌ 단점 | 용량 제한 | 쿠키당 약 4KB, 도메인당 개수 제한 |
| ❌ 단점 | 매 요청 오버헤드 | 모든 요청에 실려 헤더 크기 증가 |

### ⚖️ Trade-off 분석

```
편의성(자동전송)  ◄──────── Trade-off ────────►  CSRF 위험
XSS 안전(HttpOnly) ◄──────── Trade-off ────────►  JS 접근 불가(클라 로직 제약)
보안 강함(Strict)  ◄──────── Trade-off ────────►  UX 깨짐(외부 유입 시 로그아웃처럼 보임)
```

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 SameSite 3값 비교

| 비교 기준 | `Strict` | `Lax` | `None` |
|-----------|----------|-------|--------|
| 같은 사이트 요청 | ✅ 전송 | ✅ 전송 | ✅ 전송 |
| 교차 사이트 GET (링크 클릭) | ❌ 차단 | ✅ 전송 | ✅ 전송 |
| 교차 사이트 POST / iframe / img | ❌ 차단 | ❌ 차단 | ✅ 전송 |
| `Secure` 필수 여부 | 선택 | 선택 | **필수** |
| CSRF 방어력 | 가장 강함 | 강함(실용 기본) | 없음 |
| 대표 용도 | 은행·결제 | 일반 로그인 세션 | 외부 임베드·third-party |

> 📌 **브라우저 기본값(2025~2026)**: SameSite를 **명시하지 않으면** Chrome·Edge·Opera는 `Lax`로 취급(Chrome 80, 2020.2부터). 단 **Firefox·Safari는 이 "미지정→Lax" 기본값을 적용하지 않으며, 특히 Firefox는 미지정 시 `None`으로 처리(= 가장 느슨·위험)**한다(Bugzilla #1617609). → 브라우저별 기본값이 갈리므로 **항상 명시**하는 게 안전 ([web.dev: SameSite](https://web.dev/articles/samesite-cookies-explained)).

### 📊 토큰 저장: HttpOnly Cookie vs localStorage

| 비교 기준 | 🍪 HttpOnly Cookie | 🗄️ localStorage |
|-----------|-------------------|-----------------|
| XSS 시 토큰 탈취 | **방어됨** (JS 접근 불가) | ❌ 즉시 탈취 가능 |
| CSRF 노출 | ⚠️ 노출(SameSite/토큰으로 완화) | ✅ 없음(수동 첨부) — 단 **XSS엔 무방비라 종합 위험은 더 큼** |
| 전송 방식 | 자동 첨부 | JS가 `Authorization` 헤더에 수동 첨부 |
| 용량 | ~4KB | 5~10MB |
| 구현 난이도 | 서버 설정 필요 | 매우 간단 |

### 🔍 공격↔방어 매핑 (핵심)

```
XSS (Cross-Site Scripting)        CSRF (Cross-Site Request Forgery)
─────────────────────────         ──────────────────────────────────
스크립트 주입 → 쿠키 읽기?     vs   위조 페이지 → 자동 쿠키 전송?
        ▼                                  ▼
  🛡️ HttpOnly 로 차단              🛡️ SameSite + CSRF 토큰으로 차단
```

### 🤔 언제 무엇을 선택?

- **`SameSite=Strict`** → 상태 변경이 잦고 외부 유입이 거의 없는 고보안(관리자·결제).
- **`SameSite=Lax`** → 대부분의 일반 로그인 세션(기본 권장).
- **`SameSite=None; Secure`** → 광고·결제 위젯 등 third-party 컨텍스트에서 쿠키가 필요할 때만.
- **localStorage** → 민감하지 않은 캐시·UI 상태에만. **토큰 저장 금지**.

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|------|-----------|------------|
| 1 | JWT를 localStorage에 저장 | XSS 한 번이면 토큰 전체 탈취 | HttpOnly Secure 쿠키 + access는 메모리 |
| 2 | `SameSite` 미지정 후 Lax 가정 | Firefox는 미지정 시 `None`(가장 위험), Safari도 Lax 기본 미적용 | 항상 명시적으로 설정 |
| 3 | `SameSite=Strict`만 믿고 CSRF 토큰 생략 | Strict도 우회 기법 존재, 일부 흐름 비호환 | **defense in depth**: 토큰 병행 |
| 4 | `Secure` 없이 `SameSite=None` | 브라우저가 쿠키를 **거부** | `None`은 반드시 `Secure` 동반 |
| 5 | 레거시 브라우저에 `SameSite=None` 의존 | 구형 Safari/iOS12 등은 `None`을 **미인식 → `Strict`처럼 차단** (third-party 흐름 통째로 깨짐) | User-Agent 분기 또는 이중 쿠키 발급 |

### 🚫 Anti-Patterns

1. **"HttpOnly면 무조건 안전" 착각**: `HttpOnly`는 XSS의 *탈취*는 막지만, 주입된 스크립트가 **사용자를 가장해 요청을 보내는** 것(예: fetch로 송금 API 호출)은 못 막는다. HttpOnly 쿠키도 JS가 일으킨 요청엔 그대로 실린다 ([MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)).
2. **"SameSite가 CSRF를 완전 해결" 착각**: SameSite는 *부분* 방어다. OWASP·PortSwigger 모두 **CSRF 토큰을 대체하지 말고 함께 쓰라**고 권고 ([OWASP: SameSite](https://owasp.org/www-community/SameSite), [PortSwigger](https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions)).

### 🔒 보안/성능 고려사항

- **`__Host-` / `__Secure-` 접두사**로 다운그레이드·고정 공격 차단.
- **Domain은 *생략*해야 가장 좁고 안전**: `Domain`을 **미지정하면 host-only**(발급한 그 호스트에만 전송)로 가장 안전하다. 반대로 `Domain=example.com`처럼 **지정하면 그 도메인 + 모든 서브도메인**에 전송된다 → 좁히려는 의도로 Domain을 명시하면 오히려 노출이 **확대**된다(흔한 역효과). `Domain=.example.com`은 한 서브도메인 XSS가 전체로 번지는 통로가 된다. **요약: 좁히려면 Domain을 쓰지 마라.**
- **CHIPS (`Partitioned`)**: third-party 쿠키를 top-level 사이트별로 격리하는 속성. third-party cookie 제한 환경에서 임베드 위젯 세션 유지에 사용. **2025-12부터 MDN Baseline("Newly available") — Chrome 114+/Firefox 141+/Safari 18.4+로 주요 브라우저 범용 지원**(caniuse ≈84%). `Partitioned`는 **`Secure` 필수**이며 `__Host-` 접두사 병용이 권장된다(예: `Set-Cookie: __Host-w=…; SameSite=None; Secure; Partitioned`) ([MDN: Partitioned cookies](https://developer.mozilla.org/en-US/docs/Web/Privacy/Guides/Privacy_sandbox/Partitioned_cookies)).
- ⚡ **성능**: 쿠키는 매 요청에 실리므로, 정적 자원 도메인(CDN)에는 쿠키를 두지 말 것(cookieless domain).

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|------|------|----------|
| 📖 공식 표준 | RFC 6265 | [HTTP State Management](https://datatracker.ietf.org/doc/html/rfc6265) |
| 📖 공식 문서 | MDN Set-Cookie | [Reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie) |
| 📘 가이드 | web.dev SameSite | [SameSite cookies explained](https://web.dev/articles/samesite-cookies-explained) |
| 🔒 보안 | OWASP SameSite | [www-community/SameSite](https://owasp.org/www-community/SameSite) |

### 🛠️ 관련 도구 & 설정 위치

| 도구/프레임워크 | 설정 방법 |
|---------------|----------|
| Express (Node) | `res.cookie('sid', v, { httpOnly: true, secure: true, sameSite: 'lax' })` |
| FastAPI (Python) | `response.set_cookie(key, value, httponly=True, secure=True, samesite='lax')` |
| Nginx | `proxy_cookie_flags ~ secure httponly samesite=lax;` |
| DevTools | Application → Cookies 탭에서 속성 확인 |

### 🔮 트렌드 & 전망

- **Third-party cookie**: Google의 입장은 두 번에 걸쳐 바뀌었다 — **2024년 7월 22일** Chrome의 third-party cookie *단계적 폐지 계획을 철회*했고, **2025년 4월 29일** 새로 도입하려던 *별도 동의 프롬프트(standalone prompt) 계획마저 철회*하고 기존 Chrome 프라이버시 설정을 현행 유지하기로 확정했다(즉 "새 user-choice 모델로 전환"이 아니라 "현상 유지"). Privacy Sandbox API는 유지 ([OneTrust 요약](https://www.onetrust.com/blog/google-drops-plans-for-third-party-cookie-choice-prompt-in-chrome/)).
  - → 영향받는 건 광고·추적용 third-party 쿠키이고 **first-party 세션 쿠키는 직접 영향이 없다**. ⚠️ 단 "first-party면 안심"은 안일하다: ① 이 정책은 **2020→2024→2025로 반복 번복**돼 시점 의존적이고, ② **Safari ITP·Firefox**는 JS(`document.cookie`)로 설정한 first-party 쿠키도 **만료를 7일/24시간으로 단축**하며, ③ 인증·기능 외 쿠키는 **GDPR/ePrivacy상 동의(consent) 의무**가 별도로 있다(기술적으로 동작함 ≠ 법적으로 써도 됨).
- **`Partitioned` (CHIPS)**: third-party 제한 시대의 표준 메커니즘으로, 2025-12 **Baseline 도달**(주요 브라우저 범용 지원). "실험"이 아니라 실사용 단계.
- **passkey·토큰 in 메모리** 등 "쿠키 의존도 낮추기" 흐름과 공존.

### 💬 커뮤니티 인사이트

- 실무 합의(2025): "**무조건 localStorage 금지, 무조건 쿠키**"가 아니라 — *access token은 메모리, refresh token은 HttpOnly 쿠키*가 XSS·CSRF를 동시에 줄이는 가장 균형 잡힌 패턴이라는 의견이 다수 ([DEV Community](https://dev.to/cotter/localstorage-vs-cookies-all-you-need-to-know-about-storing-jwt-tokens-securely-in-the-front-end-15id)).

---

## 📎 Sources

1. [MDN — Set-Cookie header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie) — 공식 문서
2. [web.dev — SameSite cookies explained](https://web.dev/articles/samesite-cookies-explained) — 공식 가이드
3. [OWASP — SameSite](https://owasp.org/www-community/SameSite) — 보안 커뮤니티
4. [PortSwigger — Bypassing SameSite restrictions](https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions) — 보안 연구
5. [Microsoft Learn — Handle SameSite cookie changes in Chrome](https://learn.microsoft.com/en-us/entra/identity-platform/howto-handle-samesite-cookie-changes-chrome-browser) — 공식 문서
6. [Wisp — Token Storage: localStorage vs HttpOnly Cookies](https://www.wisp.blog/blog/understanding-token-storage-local-storage-vs-httponly-cookies) — 기술 블로그
7. [DEV Community — LocalStorage vs Cookies for JWT](https://dev.to/cotter/localstorage-vs-cookies-all-you-need-to-know-about-storing-jwt-tokens-securely-in-the-front-end-15id) — 커뮤니티
8. [Privacy Sandbox — Cookie attributes / countdown](https://privacysandbox.google.com/cookies/basics/cookie-attributes) — 공식 문서
9. [MDN — Partitioned cookies (CHIPS)](https://developer.mozilla.org/en-US/docs/Web/Privacy/Guides/Privacy_sandbox/Partitioned_cookies) — 공식 문서
10. [OWASP — Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) — 보안 표준
11. [IETF — OAuth 2.0 for Browser-Based Apps (draft)](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps) — 표준 초안 (BFF 1순위 근거)
12. [Bugzilla #1617609 — Firefox SameSite=Lax default](https://bugzilla.mozilla.org/show_bug.cgi?id=1617609) — 브라우저 트래커
13. [OneTrust — Google drops third-party cookie prompt (2025-04)](https://www.onetrust.com/blog/google-drops-plans-for-third-party-cookie-choice-prompt-in-chrome/) — 업계 분석

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 4 (작성) + rl-verify 5-관점 검증(2 iteration)
> - 수집 출처 수: 13 (인용 기준)
> - 출처 유형: 공식/표준 8, 블로그 3, 커뮤니티 2
> - 작성일: 2026-05-31 / **rl-verify 검증 반영: 2026-06-01** (Tier 3, 14건 정정 — 검증 리포트: `docs/demiurge/rl-verify/http-cookie-security/report.md`)
