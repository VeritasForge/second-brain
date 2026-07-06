---
tags: [pwa, service-worker, web-push, cache-storage, twa, webapk]
created: 2026-07-06
---

# PWA(Progressive Web App) 아키텍처 정리

> 💡 **한줄 요약**: PWA는 웹 애플리케이션 그대로이지만, **Service Worker**(백그라운드에서 웹페이지와 별개로 동작하는 스크립트)와 **Web App Manifest**(설치 가능성을 정의하는 JSON)를 통해 OS 알림·오프라인·설치라는 네이티브 앱 경험을 흉내 낸다.

---

## 1️⃣ PWA란 무엇인가 — 3대 기둥

PWA를 구성하는 기본 요소는 3가지다.

| 기둥 | 역할 | 없으면? |
| --- | --- | --- |
| **HTTPS** | 통신 암호화, Service Worker 등록의 전제조건 | Service Worker 자체를 등록 불가 |
| **Web App Manifest** | 아이콘·이름·"홈 화면에 추가" 설치 정보를 담은 JSON | 설치는 안 되지만 웹사이트로는 동작 |
| **Service Worker** | 오프라인 캐싱, 백그라운드 동기화, 푸시 알림 수신 | 앱이 닫히면 아무것도 못 함 — "그냥 웹사이트"가 됨 |

이 중 **탭이 닫혀 있어도 뭔가를 할 수 있게** 해주는 유일한 요소가 Service Worker다.

---

## 2️⃣ Service Worker — PWA의 핵심 실행 모델

### 2.1 정체: "모듈/인스턴스"가 아니라 브라우저가 관리하는 백그라운드 스레드

Service Worker는 `new`로 인스턴스를 만드는 게 아니라, `navigator.serviceWorker.register('/sw.js')`로 브라우저에게 "이 스크립트를 백그라운드에서 관리해줘"라고 **등록**만 한다. 브라우저가 라이프사이클을 대신 관리한다:

```
개발자 관점                          브라우저 관점
──────────────                     ────────────────────
register('/sw.js')  ──────────►    "이 origin의 백그라운드 워커로
                                     이 스크립트를 등록해라"

push 이벤트 도착      ──────────►    잠들어있던 워커를 깨워서
                                     이벤트 핸들러 실행 후 다시 재움
```

다만 "origin당 하나만 존재하고 여러 탭이 공유한다"는 점에서는 싱글턴과 비슷한 감각이 맞다. 실제로 "인스턴스 핸들"에 가까운 건 `ServiceWorkerRegistration`(등록된 Service Worker를 가리키는 참조 객체)이다.

| 이름 | 정체 | "인스턴스"에 해당하는가? |
| --- | --- | --- |
| Service Worker 스크립트 자체 | origin당 보통 1개만 활성화 (싱글턴에 가까움) | 개념적으로는 "인스턴스 하나"처럼 동작 |
| `ServiceWorkerRegistration` | 등록된 Service Worker를 가리키는 참조 객체 | 이게 오히려 "인스턴스 핸들"에 더 가까움 |
| `ServiceWorkerContainer` (`navigator.serviceWorker`) | 페이지에서 Service Worker 시스템에 접근하는 진입점 | "모듈의 진입점" 느낌 |

### 2.2 Origin과 Scope — 등록 경계

**Origin**은 **프로토콜 + 호스트(도메인) + 포트**의 조합이다. 경로는 origin에 포함되지 않는다.

```
https://example.com:443/path/to/page
└──┬──┘ └────┬─────┘ └┬┘
 프로토콜    호스트    포트
```

| URL | example.com:443과 같은 origin? |
| --- | --- |
| `https://example.com/other-page` | ✅ 같음 (경로는 무관) |
| `http://example.com` | ❌ 다름 (프로토콜이 다름) |
| `https://www.example.com` | ❌ 다름 (서브도메인도 다른 호스트) |
| `https://example.com:8443` | ❌ 다름 (포트가 다름) |

브라우저의 **Same-Origin Policy(동일 출처 정책)** — "다른 origin의 데이터는 서로 못 건드린다" — 때문에 Service Worker도 origin당 등록된다. `evil.com`이 `bank.com`의 요청을 가로챌 수 있다면 심각한 보안 문제가 되기 때문이다.

다만 같은 origin 안에서도 등록 범위를 경로 단위로 더 좁힐 수 있는데, 이걸 **scope**라 부른다.

```
origin: https://example.com          ← 보안 격리 경계
   │
   ├── scope: /            ← 사이트 전체를 가로채는 SW
   └── scope: /app/        ← /app/ 하위만 가로채는 별도 SW
```

```javascript
navigator.serviceWorker.register("/sw.js");                          // 기본: origin 전체
navigator.serviceWorker.register("/app/sw.js", { scope: "/app/" });  // scope로 범위 축소
```

| 개념 | 무엇을 결정하나 | 넘어설 수 있나? |
| --- | --- | --- |
| **origin** | 아예 다른 사이트인지 아닌지 (보안 격리 경계) | 절대 불가 |
| **scope** | 같은 origin 안에서 어느 경로까지 관장하는지 | 개발자가 register 시 조정 가능 |

### 2.3 이벤트 기반 라이프사이클 — "브라우저 닫아도 코드가 계속 동작한다"는 오해

Service Worker는 "등록해두면 코드가 계속 살아서 돈다"가 아니라, **특정 이벤트가 올 때만 잠깐 깨어나서 그 이벤트 하나만 처리하고 다시 종료되는 모델**이다.

```
❌ 오해:                              ✅ 실제:
┌────────────────┐                 ┌────────────────┐
│ Service Worker   │                 │ Service Worker   │
│  (계속 실행 중)   │                 │  (대부분 종료 상태) │
│  타이머 돌고...   │                 │       │          │
└────────────────┘                 │  push 이벤트 도착  │
  브라우저 닫아도                    │       ▼          │
  이 상태가 유지됨 (X)               │  잠깐 깨어남      │
                                    │  showNotification │
                                    │  실행 → 다시 종료   │
                                    └────────────────┘
```

브라우저를 켜놓은 상태에서도 이벤트가 없으면 약 30초 안에 브라우저가 강제로 Service Worker를 종료시킨다 (메모리 절약).

"브라우저가 닫혀 있어도 알림이 뜬다"는 건, 코드가 계속 도는 게 아니라 **OS/브라우저 벤더의 Push Service가 브라우저를 대신 깨워주는 구조**다.

```
┌──────────────┐   push 메시지 도착    ┌───────────────────┐
│  Push Service  │ ──────────────────► │  OS/브라우저의       │
│ (구글/모질라 등) │                     │  백그라운드 대기 프로세스│
└──────────────┘                       └─────────┬─────────┘
                                                  │ 이때만 브라우저를
                                                  ▼ 잠깐 살리거나 깨움
                                        Service Worker의
                                        push 이벤트 핸들러만 실행
                                        → showNotification() → 종료
```

이 지원 정도는 플랫폼마다 다르다.

| 플랫폼 | 브라우저 완전히 종료해도 push 오나? | 왜 그런가 |
| --- | --- | --- |
| **Android** | ✅ 대부분 됨 (앱을 스와이프로 지워도) | OS 레벨에서 FCM이 깊게 통합되어 브라우저가 죽어도 OS가 대신 깨워줌 |
| **Windows/macOS 데스크톱** | ⚠️ 조건부 | "백그라운드 앱 계속 실행" 옵션이 켜져 있어야 함. 꺼져 있고 프로세스가 완전 종료되면 다음에 열 때까지 지연되거나 TTL 만료 시 소실 |
| **iOS** | ❌ 매우 제한적 | 홈 화면에 설치된 PWA 상태에서만 동작, Android만큼 지속성이 강하지 않음 |

> **정확한 표현**: "Service Worker에 등록해둔 **특정 이벤트 핸들러**(push, notificationclick 등)는, 그 이벤트가 실제로 발생하는 순간에만 OS/Push Service가 브라우저를 깨워서 잠깐 실행시켜준다" — Push처럼 외부에서 트리거해주는 것만 가능하고, 스스로 계속 뭔가를 능동적으로 수행하는 상시 실행은 불가능하다.

### 2.4 업데이트 라이프사이클 (실무에서 가장 많이 삽질하는 지점)

```
문제: 새 버전을 배포했는데, 유저 화면에는 옛 버전이 계속 보임
        │
        ▼
원인: 브라우저는 새 sw.js를 감지해도 바로 교체하지 않고
     "waiting" 상태로 대기시킴 (열려있는 탭이 있으면 활성화 안 함)

┌──────────┐   새 배포    ┌──────────┐   모든 탭 닫힘   ┌──────────┐
│ 기존 SW    │ ─────────► │ 새 SW       │ ───────────►  │ 새 SW       │
│ (activated)│  감지됨     │ (waiting)  │  (또는 새로고침) │ (activated)│
└──────────┘             └──────────┘                └──────────┘
```

기본적으로는 사용자가 **탭을 전부 닫아야만** 새 Service Worker가 활성화된다. 즉시 반영하려면 `self.skipWaiting()`(대기 없이 바로 교체) + `clients.claim()`(이미 열린 탭도 즉시 새 SW가 관리)을 조합해야 한다.

---

## 3️⃣ 설치 가능성(Installability)과 플랫폼별 배포 메커니즘

### 3.1 설치 가능 판단 조건

브라우저가 임의로 판단하는 게 아니라, 아래 조건을 **모두** 충족해야 `beforeinstallprompt` 이벤트가 발생한다. ([MDN](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable), [web.dev](https://web.dev/articles/install-criteria))

| 조건 | 내용 |
| --- | --- |
| **HTTPS** | `https://` 또는 `localhost`/`127.0.0.1`에서만 서빙 |
| **Web App Manifest** | `name`, `icons`(192px+512px), `start_url`, `display: standalone` 등을 정의한 JSON을 `<link rel="manifest">`로 연결 |
| **사용자 상호작용** | 사용자가 페이지를 최소 한 번 클릭/탭한 적이 있어야 함 |

> ⚠️ **의외의 사실**: Service Worker는 설치 가능 조건에 **필수가 아니다.** MDN 원문: "많은 PWA가 오프라인 경험을 위해 Service Worker를 쓰지만, 이게 설치 조건은 아니다." 설치 가능성과 Service Worker는 서로 독립적인 기능이다.

### 3.2 "설치"의 진짜 의미: 네이티브 컴파일이 아니라 브라우저의 위장/포장

```
❌ 오해: PWA 설치 = 네이티브 앱처럼 컴파일된 실행 파일을 다운로드

✅ 실제: PWA "설치" = 브라우저가 이미 갖고 있는 렌더링 엔진을
         OS 레벨의 아이콘/셸로 감싸서 "앱처럼 보이게" 만드는 것
         → 플랫폼마다 그 "감싸는 방식"이 완전히 다름
```

```
                    ┌─────────────────────────────┐
                    │   동일한 Web App Manifest    │
                    └──────────────┬──────────────┘
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌──────────────┐          ┌──────────────────┐         ┌──────────────────┐
│   Android      │          │   데스크톱          │         │   iOS              │
│  (WebAPK)      │          │  (Chrome/Edge)     │         │  (Web Clip)         │
└──────────────┘          └──────────────────┘         └──────────────────┘
```

**📱 Android — WebAPK (서버가 진짜 APK를 대신 만들어줌)**
- Chrome이 manifest 정보를 Google의 **WebAPK minting server**로 전송 → 서버가 실제 Android APK를 컴파일 → Play Store가 서명 → 조용히 설치.
- WebView가 아니라 **"사용자가 사이트를 추가한 그 Chrome 인스턴스에서 그대로 열린다"**([web.dev](https://web.dev/articles/webapks)).
- 트리거는 브라우저 방문 + 설치 승인뿐이고, 나머지(서버 컴파일, Play Store 서명, 조용한 설치)는 전부 사용자에게 숨겨진 자동화다. **Play Store 앱을 열지도, 파일을 다운로드하지도 않는다.**

**🖥️ 데스크톱 (Chrome/Edge) — 런처 하드링크**
- 새로 다운로드되는 실행파일은 없다. Chrome이 이미 설치 디렉토리에 가진 **`chrome_pwa_launcher.exe`**를 사용자 프로필 폴더 안에 하드링크(또는 복사)하고 이름만 그 PWA 이름으로 바꾼다.
- 데스크톱에는 이 런처를 가리키는 **바로가기**만 생성된다.
- 더블클릭하면 이 런처가 **`chrome_proxy.exe`**를 그 PWA의 app id + 프로필로 실행 — "새 앱"이 아니라 "이미 설치된 Chrome을 그 사이트 전용 창 모드로 여는 것".
- manifest에 파일 확장자 연결을 정의해두면 Windows 레지스트리에도 등록됨. ([Chromium 공식 문서](https://chromium.googlesource.com/chromium/src/+/HEAD/docs/windows_pwa_integration.md))

**🍎 iOS — Web Clip (네이티브 패키징 자체가 없음)**
- iOS는 `beforeinstallprompt`를 지원하지 않는다 — Safari가 이 스펙을 구현하지 않아서, 설치는 항상 "공유 → 홈 화면에 추가"를 수동으로 눌러야만 가능하다.
- 생성되는 건 **Web Clip**이라는 Property List(plist) **XML 파일 한 장**뿐. 실제 패키지는 전혀 생성되지 않는다.
- 실행하면 일반 Safari 인스턴스가 아니라 **"Web.app"**이라는 별도의 최소 컨테이너에서 열린다.
- 같은 PWA를 여러 번 "홈 화면에 추가"하면 iOS는 매번 **독립된 저장공간을 가진 다른 앱**으로 취급한다.

| 기준 | Android (WebAPK) | 데스크톱 (Chrome/Edge) | iOS (Web Clip) |
| --- | --- | --- | --- |
| 실제 생성물 | 서버가 컴파일한 진짜 APK | 런처 하드링크 + 바로가기 | plist XML 파일 |
| 렌더링 엔진 | 설치된 Chrome 그대로 사용 | 설치된 Chrome/Edge 그대로 사용 | Safari 엔진(WebKit) 기반 Web.app |
| 설치 프롬프트 | `beforeinstallprompt` 자동 배너 | `beforeinstallprompt` 자동 배너 | 없음 (수동 "홈 화면에 추가") |

### 3.3 TWA(Trusted Web Activity) vs WebAPK — 서로 다른 배포 경로

TWA는 개발자가 Play Store에 "정식 앱"으로 올리고 싶을 때 쓰는 **별도** 경로다. Custom Tabs 기반이며, 리소스를 APK 안에 미리 담지 않고 Service Worker가 온라인으로 계속 서빙한다.

Android 공식 문서 원문: "호스트 앱은 TWA에서 실행되는 웹 콘텐츠나 쿠키, localStorage 같은 웹 상태에 직접 접근할 수 없다. 대신 URL의 쿼리 파라미터나 intent URI로만 데이터를 주고받을 수 있다."

| WebAPK | TWA |
| --- | --- |
| **브라우저가 자동으로** 처리 (개발자 개입 없음) | **개발자가 직접** 빌드 도구(Bubblewrap/PWABuilder)로 패키징해서 제출 |
| 사용자는 웹사이트 방문 → 홈 화면 추가만 하면 끝 | 사용자는 **일반 앱처럼 Play Store에서 검색해 다운로드** |
| Google 서버가 실시간 컴파일 | 개발자가 사전에 빌드, Google 심사(Play Console) 거침 |
| "설치"가 웹사이트 방문의 부산물 | "게시"가 개발자의 별도 배포 작업 |

```
TWA 게시 흐름:
① 개발자가 Bubblewrap/PWABuilder로 wrapper APK/AAB 직접 빌드
② Google Play Console에 일반 네이티브 앱처럼 업로드
③ Google 앱 심사 통과
④ 정식 게시 → 사용자는 Play Store에서 검색해 일반적으로 다운로드
```

---

## 4️⃣ 웹 푸시 알림 (시스템 알럿)

### 4.1 핵심 구성요소

```
┌───────────────────────────────────────────────────────┐
│              시스템 알럿을 구성하는 3개의 축              │
├───────────────────────────────────────────────────────┤
│  ⚙️ Service Worker  — push 이벤트를 "받는 귀"           │
│  📡 Push API        — 서버↔Push Service↔클라이언트 배달 채널│
│  🔔 Notification API — 받은 메시지를 OS 알림창으로 그림    │
└───────────────────────────────────────────────────────┘
```

| 구성 요소 | 역할 |
| --- | --- |
| **Service Worker** | 탭이 닫혀 있어도 브라우저가 계속 띄워두는 스크립트, push 이벤트 리스너를 등록해둠 |
| **Push API** | `PushManager.subscribe()`로 구독을 만들고, 서버가 그 endpoint로 메시지를 보낼 수 있게 함 |
| **Push Service** | 브라우저 벤더의 중계 서버 (Chrome은 FCM, Firefox/Safari는 자체 서비스) — **내 서버가 아니라 브라우저 회사가 운영하는 중계소** |
| **Notification API** | `ServiceWorkerRegistration.showNotification()`으로 실제 OS 네이티브 알림 UI를 그림 |
| **VAPID 키** | 내 서버가 구독의 주인임을 Push Service에 증명하는 공개키/개인키 쌍 |

### 4.2 아키텍처 흐름

```
┌────────────┐   ①구독요청    ┌──────────────────┐
│  브라우저    │ ───────────► │  Push Service      │
└─────┬──────┘  ②endpoint 발급 └─────────▲──────────┘
      │③subscription 정보 전송            │④VAPID로 서명된 push 전송
      ▼                                  │
┌────────────┐                          │
│  내 백엔드   │──────────────────────────┘
└────────────┘
      ▼ (Push Service가 기기로 전달)
┌────────────────────┐
│ Service Worker      │ ⑤'push' 이벤트 수신 ⑥showNotification() 호출
└─────────┬───────────┘
          ▼
   🔔 OS 네이티브 알림창
```

**클라이언트 코드 (구독 + 등록)**
```javascript
async function subscribeToPush() {
  const registration = await navigator.serviceWorker.register("/sw.js");
  const permission = await Notification.requestPermission();
  if (permission !== "granted") return;

  const vapidPublicKey = await fetch("/vapidPublicKey").then(r => r.text());
  const subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true, // 모든 알림을 사용자에게 반드시 보여줘야 함 (필수 true)
    applicationServerKey: urlBase64ToUint8Array(vapidPublicKey),
  });

  await fetch("/api/subscribe", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(subscription),
  });
}
```

**Service Worker 코드 (알림 수신 및 표시)**
```javascript
self.addEventListener("push", (event) => {
  const data = event.data ? event.data.json() : { title: "알림", body: "" };
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: "/icon-192.png",
      data: { url: data.url },
    })
  );
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(clients.openWindow(event.notification.data.url || "/"));
});
```

**서버 코드 (Node.js, `web-push` 라이브러리)**
```bash
npm install web-push
npx web-push generate-vapid-keys
```
```javascript
import webpush from "web-push";
webpush.setVapidDetails("mailto:you@example.com", process.env.VAPID_PUBLIC_KEY, process.env.VAPID_PRIVATE_KEY);

async function sendNotification(subscription, payload) {
  try {
    await webpush.sendNotification(subscription, JSON.stringify(payload));
  } catch (err) {
    if (err.statusCode === 410) await deleteSubscriptionFromDB(subscription); // 만료 구독 즉시 정리
  }
}
```

### 4.3 베스트 프랙티스와 주의점

| # | 실수 | 왜 문제인가 | 올바른 접근 |
| --- | --- | --- | --- |
| 1 | 첫 방문 즉시 권한 팝업 | 맥락 없이 뜬 팝업은 **90%가 거부/무시됨** (Chrome Dev Summit 데이터) | 혜택이 명확해지는 순간(결제 완료 등)에 요청 |
| 2 | `userVisibleOnly: false` 시도 | 대부분 브라우저가 silent push를 금지해 구독 실패 | 항상 `true`로 설정 |
| 3 | 실패한 구독 방치 | 410 Gone 응답 무시 시 죽은 구독에 계속 발송 시도 | 실패 시 즉시 DB에서 구독 삭제 |
| 4 | iOS를 일반 웹처럼 취급 | Safari 탭에서는 권한 요청 자체가 실패 | "홈 화면에 추가"로 설치된 상태인지 먼저 확인 |

| 구분 | 항목 |
| --- | --- |
| ✅ 장점 | 앱스토어 불필요, 크로스 플랫폼 1회 구현, 종단간 암호화, 무료 인프라 |
| ❌ 단점 | 낮은 도달률(웹 푸시 평균 약 33% vs 네이티브 95%+), iOS 제약이 큼, 리치 미디어 제한 |

**더블 권한 패턴(Double Permission Pattern)**: 브라우저 네이티브 팝업 전에, 먼저 커스텀 UI로 "왜 알림이 필요한지" 설명하고 동의한 사용자에게만 실제 브라우저 권한 팝업을 띄우는 방식.

---

## 5️⃣ 데이터 저장과 캐싱

### 5.1 저장소 비교 — Cache Storage, localStorage, sessionStorage, IndexedDB

가장 근본적인 차이는 **"무엇을" 저장하는가**다.

```
localStorage / sessionStorage           Cache Storage (Cache API)
┌─────────────────────┐                ┌─────────────────────┐
│  문자열 키-값 저장소     │                │  HTTP 요청↔응답 짝 저장소 │
│  "theme" → "dark"    │                │  Request("/api/x")   │
│                      │                │    ↔ Response(JSON)  │
└─────────────────────┘                └─────────────────────┘
```

두 번째 근본 차이는 **어디서 접근 가능한가**다.

| | localStorage / sessionStorage | Cache Storage |
| --- | --- | --- |
| 동작 방식 | **동기(synchronous)** — 즉시 값 반환 | **비동기(async)** — Promise 반환 |
| Service Worker에서 접근 가능? | ❌ 불가능 | ✅ 가능 (오히려 Service Worker가 주 사용자) |

**왜 Service Worker에서 localStorage를 못 쓰나?** 브라우저는 워커 스레드에서 메인 스레드를 블로킹할 수 있는 **동기 API를 금지**한다. localStorage는 동기 API라서 Service Worker 안에는 애초에 존재하지 않는다.

전체 비교:

| 저장소 | 동기/비동기 | Service Worker 접근 | 데이터 형태 | 유지 기간 | 용도 |
| --- | --- | --- | --- | --- | --- |
| **localStorage** | 동기 | ❌ | 문자열 키-값 | 영구 (수동 삭제 전까지) | 사용자 설정, 간단한 토큰 |
| **sessionStorage** | 동기 | ❌ | 문자열 키-값 | 탭 닫으면 삭제 | 탭 한정 임시 상태 |
| **Cache Storage** | 비동기 | ✅ | Request↔Response 쌍 | 명시적 삭제 또는 브라우저 용량 정리 전까지 | 네트워크 요청/응답 캐싱 |
| **IndexedDB** | 비동기 | ✅ | 구조화된 객체/대용량 | 명시적 삭제 또는 브라우저 용량 정리 전까지 | 오프라인 폼 데이터, 로컬 DB |

```javascript
// sw.js — Cache Storage 사용 예시
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open("app-shell-v1").then((cache) => cache.addAll(["/", "/styles.css", "/app.js"]))
  );
});
self.addEventListener("fetch", (event) => {
  event.respondWith(caches.match(event.request).then((cached) => cached || fetch(event.request)));
});
```

### 5.2 물리적 저장 위치 — 서버가 아니라 사용자 기기, origin별로 격리

```
┌─────────────────────────────────────────────┐
│              사용자의 컴퓨터/폰                    │
│  ┌─────────────────────────────────────────┐  │
│  │           브라우저 (Chrome 등)               │  │
│  │  ┌───────────────────────────────────┐  │  │
│  │  │   origin별로 격리된 저장 공간          │  │  │
│  │  │  https://example.com 전용:           │  │  │
│  │  │   - localStorage / sessionStorage    │  │  │
│  │  │   - Cache Storage / IndexedDB        │  │  │
│  │  └───────────────────────────────────┘  │  │
│  └─────────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
        ▲  서버로 자동 전송되지 않음
```

Chrome 기준 예시 디렉토리 구조:

```
~/.../Chrome/Default/
├── Local Storage/leveldb/                        ← localStorage
├── Session Storage/                              ← sessionStorage
├── IndexedDB/https_example.com_0.indexeddb.leveldb/  ← origin별 폴더
└── Service Worker/CacheStorage/<해시값 폴더>/        ← Cache Storage
```

실무적 의미:

| 의미 | 설명 |
| --- | --- |
| **기기 종속적** | 다른 기기에서 같은 사이트 접속해도 데이터가 따라오지 않음 (브라우저 동기화 별도 설정 없는 한) |
| **사용자가 지울 수 있음** | "인터넷 사용 기록 삭제"에서 함께 삭제됨 |
| **용량 제한** | 브라우저가 origin별 할당량(quota)을 관리, 공간 부족 시 임의로 오래된 데이터 삭제 가능 |

### 5.3 캐싱 전략

| 전략 | 동작 | 적합한 데이터 |
| --- | --- | --- |
| **Cache First** | 캐시에 있으면 그거 쓰고, 없으면 네트워크 | 아이콘, 폰트, 정적 자산 |
| **Network First** | 네트워크 먼저 시도, 실패하면 캐시 | 실시간성이 중요한 API 응답 |
| **Stale-While-Revalidate** | 캐시를 즉시 보여주고, 백그라운드로 네트워크에서 갱신 | 자주 안 바뀌지만 최신성도 필요한 데이터 |

### 5.4 App Shell 패턴

첫 로딩 시 **레이아웃 뼈대(헤더/네비게이션/기본 CSS)**만 캐시에서 즉시 그리고, **콘텐츠는 그 다음에** 네트워크/캐시로 채우는 아키텍처 패턴. 이게 있어야 "오프라인에서도 앱 자체는 뜨는데 콘텐츠만 못 불러온다" 같은 경험이 가능해진다.

---

## 6️⃣ TWA vs React Native/Flutter — 왜 여전히 네이티브 프레임워크를 쓰는가

### 이유 1: TWA는 iOS에 존재하지 않음

```
        Android              iOS
TWA:  │  ✅ 지원   │       │  ❌ 대응 기술 없음 │
React Native/Flutter: │  ✅ 지원   │   │  ✅ 지원   │
```

Apple App Store Review Guideline **4.2.2가 "web clippings(웹 클리핑)"을 명시적으로 차단**한다.

### 이유 2: TWA는 웹 콘텐츠와 네이티브 기능 사이에 진짜 다리가 없음

```
┌─────────────────────┐         ┌─────────────────────┐
│   TWA 안의 웹 콘텐츠    │  ⇆(매우 제한적)  │   Android 네이티브 앱    │
│  (Chrome이 그대로 렌더링) │   URL 파라미터/    │  (블루투스, 카메라 등)     │
└─────────────────────┘   Intent URI만    └─────────────────────┘
        vs.
┌─────────────────────┐         ┌─────────────────────┐
│  React Native/Flutter  │ ⇆(양방향 브리지)  │   네이티브 API 전체       │
│      코드            │  Platform Channel  │  (진짜 Bluetooth LE,     │
└─────────────────────┘   / Bridge         │   NFC, 센서, 백그라운드)   │
                                            └─────────────────────┘
```

| 기준 | TWA | React Native | Flutter |
| --- | --- | --- | --- |
| iOS 지원 | ❌ 존재하지 않음 | ✅ 지원 | ✅ 지원 |
| 렌더링 엔진 | 사용자 기기의 Chrome | 네이티브 UI 컴포넌트 | 자체 렌더링 엔진(Skia), 네이티브급 속도 |
| 네이티브 API 접근 | URL 파라미터/Intent뿐, 직접 브리지 없음 | JS↔네이티브 브리지 | Platform Channel |
| 적합한 상황 | 이미 있는 웹/PWA를 Android에만 빠르게 노출 | iOS+Android 동시에, 하나의 코드베이스로 진짜 앱 경험 | 위와 동일 + 고성능 UI/애니메이션이 중요할 때 |

PWA/TWA는 **NFC, 지문 인식, 정교한 카메라 제어 같은 최신 하드웨어 기능을 아직 웹 표준이 지원하지 않아서** 쓸 수 없다 — TWA를 잘 만들어도 해결 안 되는 웹 플랫폼 자체의 한계다.

> **정리**: "TWA로 쉽게 만든다"는 건 원래부터 "Android 전용, 웹 API 한계 안에서"라는 전제가 깔린 선택지다. React Native/Flutter는 그 전제 자체를 깨고 싶을 때(iOS도 필요, 네이티브 하드웨어 기능 필요, 진짜 네이티브급 성능 필요) 쓴다.

---

## 7️⃣ PWA/TWA를 언제 쓰는가 — 흔한 오해 정정

"웹페이지 닫혀도 백그라운드 처리가 필요할 때 쓴다"는 **범위가 너무 좁다.** 실제로는 여러 이유가 동시에 걸리는 경우가 훨씬 많다.

```
PWA를 선택하는 실제 이유들
┌────────────────────────────────────────────────┐
│  💰 앱스토어 없이 배포        (심사/수수료 회피)   │
│  📱 iOS+Android+데스크톱      (코드 1개로 커버)   │
│  🔍 검색엔진에 그대로 노출     (여전히 웹사이트라서) │
│  📴 오프라인에서도 일부 동작   (캐싱)              │
│  🔔 웹페이지 닫혀도 알림 수신  (Service Worker)   │
│                              ↑ 이건 전체 중 "하나의 기능"일 뿐 │
└────────────────────────────────────────────────┘
```

| 목적 | PWA가 해결하는 방식 | 백그라운드 처리와 관계 |
| --- | --- | --- |
| 앱스토어 심사/수수료 회피 | 웹사이트를 그대로 설치 가능하게 함 | 무관 |
| 여러 플랫폼 동시 지원 | 코드 1벌로 웹+앱 경험 제공 | 무관 |
| SEO/검색 노출 유지 | 여전히 인덱싱되는 웹페이지 | 무관 |
| 느린 네트워크에서도 동작 | Service Worker 캐싱 | 무관 |
| 앱이 닫혀도 알림 받기 | Service Worker push 이벤트 | 이게 그 기능 |

**TWA는 이 목록에서도 더 좁다** — TWA는 "이미 있는 PWA를 Android Play Store에 정식 앱처럼 올리기 위한 배포 방법"일 뿐이며, 백그라운드 처리 능력을 TWA가 추가로 주는 건 없다. 그 능력은 이미 PWA(Service Worker) 단계에서 결정된 것이고, TWA는 그걸 그대로 Play Store 껍데기에 넣어주는 역할만 한다.

---

## 8️⃣ 아직 다루지 않은 것 (알아두면 좋은 나머지 조각)

| 항목 | 설명 |
| --- | --- |
| **Background Sync API** | Push(서버→클라이언트)와 반대로, 클라이언트가 오프라인에서 시도한 작업(폼 제출 등)을 온라인이 되는 순간 자동 재시도해주는 기능 |
| **Project Fugu APIs** | PWA의 네이티브 API 한계를 좁히려는 실험적 웹 API 그룹 — File System Access API, Web Share API, Badging API, Contact Picker 등. Chrome이 주도 |
| **Manifest 세부 필드** | display modes(standalone/fullscreen/minimal-ui/browser), shortcuts, screenshots 등 install UI를 풍부하게 만드는 필드 |
| **Lighthouse PWA 감사** | 실무에서 설치 가능성/성능/오프라인 지원 여부를 체크리스트로 검증하는 도구 |

---

## 📎 Sources (대화 중 인용된 주요 출처)

1. [Making PWAs installable - MDN](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable)
2. [What does it take to be installable? - web.dev](https://web.dev/articles/install-criteria)
3. [WebAPKs on Android - web.dev](https://web.dev/articles/webapks)
4. [Chromium Windows PWA Integration - chromium.googlesource.com](https://chromium.googlesource.com/chromium/src/+/HEAD/docs/windows_pwa_integration.md)
5. [Overview of Trusted Web Activities - Android Developers](https://developer.android.com/develop/ui/views/layout/webapps/trusted-web-activities)
6. [PWA Add to Home Screen: The Magic Behind It - gomage.com](https://www.gomage.com/blog/pwa-add-to-home-screen/)
7. [Do Progressive Web Apps Work on iOS? - Mobiloud](https://www.mobiloud.com/blog/progressive-web-apps-ios)
8. [Can You Publish a PWA to the App Store and Google Play? - Mobiloud](https://www.mobiloud.com/blog/publishing-pwa-app-store)
9. [Native vs. Cross-Platform for Bluetooth LE - novelbits.io](https://novelbits.io/native-vs-cross-platform-bluetooth-low-energy-mobile-app-platforms/)
10. [PWA Re-engageable Notifications - MDN](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Tutorials/js13kGames/Re-engageable_Notifications_Push)
11. [Push API - W3C 스펙](https://www.w3.org/TR/push-api/)
