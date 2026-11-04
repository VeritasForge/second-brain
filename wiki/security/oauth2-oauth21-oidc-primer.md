---
tags: [security, oauth, oauth2, oauth21, oidc, openid-connect, pkce, jwt, authorization, authentication, primer]
created: 2026-11-03
---

# OAuth 2.0·2.1과 OpenID Connect 입문: 두 서비스 간 계정 연동으로 배우기

> **이 문서 한 줄 요약**: OAuth는 "비밀번호를 넘기지 않고 권한만 빌려주는" 표준이고, OpenID Connect는 그 위에 "로그인한 사람이 누구인지"를 알려 주는 층을 얹은 표준이다. 이 문서는 두 표준을 처음 접하는 개발자가 실제 서비스 연동(클라이언트 앱에 외부 AI 에이전트 서비스를 붙이는 작업)을 따라가며 개념, 흐름, 보안 원리를 익히도록 쓴 입문서다.

## 이 문서를 읽는 법

**대상 독자**: OAuth라는 말은 들어 봤지만 직접 연동해 본 적은 없는 주니어 개발자.

**예시 상황**: 이 문서는 하나의 실제 연동을 계속 예로 든다.

- **클라이언트 앱**: 자체 회원과 로그인을 가진 앱 서비스다.
- **IdP 서비스**: 계정과 AI 에이전트 기능을 함께 제공하는 서비스. 자체 회원 가입·로그인 서버인 **인증 서버**를 가지고 있다.
- **하려는 일**: 클라이언트 앱 안에 IdP 서비스 메뉴를 넣고, 앱 사용자가 IdP 서비스 계정과 연결한 뒤 앱 안에서 그 서비스의 기능을 쓰게 한다.

**읽는 순서**: 1장부터 순서대로 읽으면 개념이 쌓이도록 배치했다. 보안은 두 군데서 다룬다. 개념을 배우는 장 안에서 그 개념과 관련된 공격을 🛡️ 표시로 함께 보고, 15장에서 OAuth를 노리는 공격 전체를 한 지도로 모은다. 14장(확장 표준)은 입문 중요도 표시를 보고 ★ 항목은 처음엔 건너뛰어도 된다. 부록 A는 표준 연표, 부록 B는 AWS 기준 IP 교환 설명이다. 실제 연동 사례만 보고 싶다면 16장으로 바로 가도 되지만, 그 장은 앞 장의 개념을 참조한다.

**표기**: 예시 값(`c-5d1e0b`, `user@example.com` 등)은 모두 설명을 위해 지어낸 값이다. 표준 문서의 규범 강도는 원어를 그대로 쓴다. MUST는 "반드시", SHOULD는 "특별한 이유가 없으면", MAY는 "선택"이라는 뜻이다.

## 목차

- [[#1. 용어집|1. 용어집]]
- [[#2. OAuth가 풀려는 문제|2. OAuth가 풀려는 문제]]
    - [[#2.1 비밀번호를 넘기지 않고 권한만 빌려주기|2.1 비밀번호를 넘기지 않고 권한만 빌려주기]]
    - [[#2.2 인증과 인가|2.2 인증과 인가]]
    - [[#2.3 OAuth가 아닌 것, OAuth와 헷갈리는 것|2.3 OAuth가 아닌 것, OAuth와 헷갈리는 것]]
    - [[#2.4 버전 흐름 한눈에 보기|2.4 버전 흐름 한눈에 보기]]
- [[#3. 등장인물과 관계|3. 등장인물과 관계]]
    - [[#3.1 OAuth의 네 역할|3.1 OAuth의 네 역할]]
    - [[#3.2 이번 연동은 양방향이다|3.2 이번 연동은 양방향이다]]
    - [[#3.3 클라이언트 유형별로 맞는 흐름|3.3 클라이언트 유형별로 맞는 흐름]]
- [[#4. 사전 등록: 클라이언트 등록 카드|4. 사전 등록: 클라이언트 등록 카드]]
    - [[#4.1 등록 카드에 들어가는 것|4.1 등록 카드에 들어가는 것]]
    - [[#4.2 client_id와 client_secret|4.2 client_id와 client_secret]]
    - [[#4.3 클라이언트 인증 방식: client_secret_basic|4.3 클라이언트 인증 방식: client_secret_basic]]
    - [[#4.4 redirect_uri|4.4 redirect_uri]]
    - [[#4.5 방화벽(IP 허용)과 클라이언트 등록은 무엇이 다른가|4.5 방화벽(IP 허용)과 클라이언트 등록은 무엇이 다른가]]
    - [[#4.6 동적 클라이언트 등록 (RFC 7591)|4.6 동적 클라이언트 등록 (RFC 7591)]]
- [[#5. 엔드포인트 지도|5. 엔드포인트 지도]]
    - [[#5.1 authorize와 token을 나누는 이유|5.1 authorize와 token을 나누는 이유]]
    - [[#5.2 "webview를 요청하는 API"는 따로 없다|5.2 "webview를 요청하는 API"는 따로 없다]]
    - [[#5.3 scope: 위임하는 권한의 범위|5.3 scope: 위임하는 권한의 범위]]
- [[#6. grant_type: 무엇을 근거로 토큰을 받는가|6. grant_type: 무엇을 근거로 토큰을 받는가]]
    - [[#6.1 grant_type은 왜 필요한가|6.1 grant_type은 왜 필요한가]]
    - [[#6.2 세 가지 grant와 각각이 증명하는 것|6.2 세 가지 grant와 각각이 증명하는 것]]
    - [[#6.3 grant_type별 파라미터와 응답|6.3 grant_type별 파라미터와 응답]]
    - [[#6.4 오류 응답|6.4 오류 응답]]
    - [[#6.5 "파라미터가 많을수록 안전하다"는 오해|6.5 "파라미터가 많을수록 안전하다"는 오해]]
    - [[#6.6 "client credentials"는 두 가지 뜻이다|6.6 "client credentials"는 두 가지 뜻이다]]
    - [[#6.7 OAuth 2.1에서 남은 것과 사라진 것|6.7 OAuth 2.1에서 남은 것과 사라진 것]]
- [[#7. Authorization Code + PKCE 흐름 따라가기|7. Authorization Code + PKCE 흐름 따라가기]]
    - [[#7.1 전체 시퀀스|7.1 전체 시퀀스]]
    - [[#7.2 state: 로그인 요청과 응답을 짝짓는 번호표|7.2 state: 로그인 요청과 응답을 짝짓는 번호표]]
    - [[#7.3 PKCE: code를 가로채도 쓸 수 없게|7.3 PKCE: code를 가로채도 쓸 수 없게]]
    - [[#7.4 302 redirect는 왜 등장하나|7.4 302 redirect는 왜 등장하나]]
    - [[#7.5 callback 처리 순서|7.5 callback 처리 순서]]
    - [[#7.6 authorize 단계의 오류 응답|7.6 authorize 단계의 오류 응답]]
    - [[#7.7 결과를 돌려받는 방식: response_type과 response_mode|7.7 결과를 돌려받는 방식: response_type과 response_mode]]
    - [[#7.8 동의(consent) 화면|7.8 동의(consent) 화면]]
- [[#8. 토큰: access·refresh·id|8. 토큰: access·refresh·id]]
    - [[#8.1 세 토큰은 같은 응답에 함께 오지만 독자가 다르다|8.1 세 토큰은 같은 응답에 함께 오지만 독자가 다르다]]
    - [[#8.2 유효 시간은 누가 정하나|8.2 유효 시간은 누가 정하나]]
    - [[#8.3 refresh_token grant: 근거와 목적|8.3 refresh_token grant: 근거와 목적]]
    - [[#8.4 refresh token rotation과 탈취 탐지|8.4 refresh token rotation과 탈취 탐지]]
    - [[#8.5 refresh token이 증명하는 것과 증명하지 못하는 것|8.5 refresh token이 증명하는 것과 증명하지 못하는 것]]
    - [[#8.6 access token 사용법 (RFC 6750)|8.6 access token 사용법 (RFC 6750)]]
    - [[#8.7 토큰 수명 설계|8.7 토큰 수명 설계]]
    - [[#8.8 토큰 폐기 (RFC 7009)|8.8 토큰 폐기 (RFC 7009)]]
    - [[#8.9 클라이언트가 토큰을 보관할 때|8.9 클라이언트가 토큰을 보관할 때]]
    - [[#8.10 bearer 토큰과 발신자 제한 토큰|8.10 bearer 토큰과 발신자 제한 토큰]]
- [[#9. OpenID Connect|9. OpenID Connect]]
    - [[#9.1 OAuth와의 관계|9.1 OAuth와의 관계]]
    - [[#9.2 id_token|9.2 id_token]]
    - [[#9.3 sub와 회원 저장|9.3 sub와 회원 저장]]
    - [[#9.4 nonce|9.4 nonce]]
    - [[#9.5 scope: OIDC scope와 API scope|9.5 scope: OIDC scope와 API scope]]
    - [[#9.6 discovery|9.6 discovery]]
    - [[#9.7 JWKS|9.7 JWKS]]
    - [[#9.8 userinfo|9.8 userinfo]]
    - [[#9.9 id_token 검증은 꼭 필요한가|9.9 id_token 검증은 꼭 필요한가]]
    - [[#9.10 소셜 로그인과 같은 구조|9.10 소셜 로그인과 같은 구조]]
    - [[#9.11 로그인 세션, 토큰, 로그아웃|9.11 로그인 세션, 토큰, 로그아웃]]
    - [[#9.12 로그인 동작을 조절하는 요청 파라미터|9.12 로그인 동작을 조절하는 요청 파라미터]]
- [[#10. access token을 받는 쪽의 검증|10. access token을 받는 쪽의 검증]]
    - [[#10.1 검증 순서|10.1 검증 순서]]
    - [[#10.2 서명 방식에 따라 검증하는 쪽이 필요한 것|10.2 서명 방식에 따라 검증하는 쪽이 필요한 것]]
    - [[#10.3 API 앞단(gateway)과 내부 서비스의 역할 분담|10.3 API 앞단(gateway)과 내부 서비스의 역할 분담]]
    - [[#10.4 id_token을 access token처럼 쓰면 안 되는 이유|10.4 id_token을 access token처럼 쓰면 안 되는 이유]]
    - [[#10.5 access token이 JWT인지부터 확인한다|10.5 access token이 JWT인지부터 확인한다]]
    - [[#10.6 audience 제한과 scope 설계|10.6 audience 제한과 scope 설계]]
- [[#11. TLS: 통로를 지키는 것과 지키지 못하는 것|11. TLS: 통로를 지키는 것과 지키지 못하는 것]]
    - [[#11.1 TLS가 보장하는 세 가지|11.1 TLS가 보장하는 세 가지]]
    - [[#11.2 연결을 맺는 과정 (TLS 1.3 핸드셰이크, 단순화)|11.2 연결을 맺는 과정 (TLS 1.3 핸드셰이크, 단순화)]]
    - [[#11.3 OAuth에서 TLS가 지키는 구간|11.3 OAuth에서 TLS가 지키는 구간]]
    - [[#11.4 mTLS와의 차이|11.4 mTLS와의 차이]]
    - [[#11.5 TLS가 지키지 못하는 것|11.5 TLS가 지키지 못하는 것]]
- [[#12. 네이티브 앱(모바일·데스크톱·CLI)에서 로그인 화면 띄우기|12. 네이티브 앱(모바일·데스크톱·CLI)에서 로그인 화면 띄우기]]
    - [[#12.1 세 가지 그릇|12.1 세 가지 그릇]]
    - [[#12.2 웹뷰에서 호스트 앱이 할 수 있는 것|12.2 웹뷰에서 호스트 앱이 할 수 있는 것]]
    - [[#12.3 iframe은 왜 막히나|12.3 iframe은 왜 막히나]]
    - [[#12.4 앱으로 돌아오기: Universal Links·App Links와 custom scheme|12.4 앱으로 돌아오기: Universal Links·App Links와 custom scheme]]
    - [[#12.5 돌아오기 처리에서 흔한 실수|12.5 돌아오기 처리에서 흔한 실수]]
    - [[#12.6 데스크톱·CLI 앱: loopback redirect|12.6 데스크톱·CLI 앱: loopback redirect]]
    - [[#12.7 채팅 화면 전체를 웹뷰로 띄우는 구조와 비교|12.7 채팅 화면 전체를 웹뷰로 띄우는 구조와 비교]]
- [[#13. 브라우저 앱(SPA)과 BFF 패턴|13. 브라우저 앱(SPA)과 BFF 패턴]]
    - [[#13.1 SPA가 어려운 이유|13.1 SPA가 어려운 이유]]
    - [[#13.2 먼저 알아 둘 웹 보안 기초|13.2 먼저 알아 둘 웹 보안 기초]]
    - [[#13.3 세 가지 구조|13.3 세 가지 구조]]
    - [[#13.4 XSS가 토큰에 하는 일|13.4 XSS가 토큰에 하는 일]]
    - [[#13.5 토큰 저장 위치 비교 (브라우저에 둘 수밖에 없을 때)|13.5 토큰 저장 위치 비교 (브라우저에 둘 수밖에 없을 때)]]
    - [[#13.6 BFF를 만들 때 지킬 것|13.6 BFF를 만들 때 지킬 것]]
    - [[#13.7 SPA가 직접 OAuth 클라이언트가 될 때|13.7 SPA가 직접 OAuth 클라이언트가 될 때]]
    - [[#13.8 이 연동에서 보이는 BFF의 모습|13.8 이 연동에서 보이는 BFF의 모습]]
- [[#14. 더 알아 둘 확장 표준|14. 더 알아 둘 확장 표준]]
    - [[#14.1 문제별 확장 표준 지도|14.1 문제별 확장 표준 지도]]
    - [[#14.2 PAR: 요청을 미리 서버로 보내기 (RFC 9126)|14.2 PAR: 요청을 미리 서버로 보내기 (RFC 9126)]]
    - [[#14.3 JAR: 요청을 서명된 JWT로 보내기 (RFC 9101)|14.3 JAR: 요청을 서명된 JWT로 보내기 (RFC 9101)]]
    - [[#14.4 RAR: 세밀한 권한 요청 (RFC 9396)|14.4 RAR: 세밀한 권한 요청 (RFC 9396)]]
    - [[#14.5 Device Authorization Grant: 입력이 불편한 기기 (RFC 8628)|14.5 Device Authorization Grant: 입력이 불편한 기기 (RFC 8628)]]
    - [[#14.6 Token Exchange: 사용자 대신 다른 서비스 부르기 (RFC 8693)|14.6 Token Exchange: 사용자 대신 다른 서비스 부르기 (RFC 8693)]]
    - [[#14.7 private_key_jwt: secret 없이 클라이언트 인증 (RFC 7523)|14.7 private_key_jwt: secret 없이 클라이언트 인증 (RFC 7523)]]
    - [[#14.8 CIBA: 다른 기기에서 승인받기 (OpenID)|14.8 CIBA: 다른 기기에서 승인받기 (OpenID)]]
    - [[#14.9 Step-up 인증: 더 강한 로그인 요구하기 (RFC 9470)|14.9 Step-up 인증: 더 강한 로그인 요구하기 (RFC 9470)]]
    - [[#14.10 Protected Resource Metadata (RFC 9728)|14.10 Protected Resource Metadata (RFC 9728)]]
- [[#15. 보안: 공격과 방어|15. 보안: 공격과 방어]]
    - [[#15.1 이 장을 읽는 법|15.1 이 장을 읽는 법]]
    - [[#15.2 공격자는 무엇을 할 수 있다고 가정하나|15.2 공격자는 무엇을 할 수 있다고 가정하나]]
    - [[#15.3 공격 지도|15.3 공격 지도]]
    - [[#15.4 리다이렉트 경로를 노리는 공격|15.4 리다이렉트 경로를 노리는 공격]]
    - [[#15.5 code·토큰을 끼워 넣는 공격|15.5 code·토큰을 끼워 넣는 공격]]
    - [[#15.6 훔친 토큰을 쓰는 공격|15.6 훔친 토큰을 쓰는 공격]]
    - [[#15.7 신원을 혼동시키는 공격|15.7 신원을 혼동시키는 공격]]
    - [[#15.8 JWT 검증 함정|15.8 JWT 검증 함정]]
    - [[#15.9 화면과 브라우저를 노리는 공격|15.9 화면과 브라우저를 노리는 공격]]
    - [[#15.10 TLS 종료 프록시의 헤더 위조|15.10 TLS 종료 프록시의 헤더 위조]]
    - [[#15.11 추측 공격과 값의 강도|15.11 추측 공격과 값의 강도]]
    - [[#15.12 쓰지 말아야 할 방식|15.12 쓰지 말아야 할 방식]]
    - [[#15.13 방어 장치와 막는 공격 한눈에 보기|15.13 방어 장치와 막는 공격 한눈에 보기]]
- [[#16. 사례: 클라이언트 앱 × IdP 서비스 연동|16. 사례: 클라이언트 앱 × IdP 서비스 연동]]
    - [[#16.1 처음 가정한 구조와 실제 구조의 차이|16.1 처음 가정한 구조와 실제 구조의 차이]]
    - [[#16.2 구조 한눈에|16.2 구조 한눈에]]
    - [[#16.3 진입: 메뉴를 누를 때마다|16.3 진입: 메뉴를 누를 때마다]]
    - [[#16.4 계정 연결: 최초 1회|16.4 계정 연결: 최초 1회]]
    - [[#16.5 서비스 화면: iframe + 클라이언트 앱 서버 중계|16.5 서비스 화면: iframe + 클라이언트 앱 서버 중계]]
    - [[#16.6 토큰 갱신|16.6 토큰 갱신]]
    - [[#16.7 IdP 서비스 → 클라이언트 앱 API|16.7 IdP 서비스 → 클라이언트 앱 API]]
    - [[#16.8 partner-user-id와 신뢰 구조|16.8 partner-user-id와 신뢰 구조]]
    - [[#16.9 연결 해제·탈퇴: 미정|16.9 연결 해제·탈퇴: 미정]]
    - [[#16.10 CI와 동일인 식별|16.10 CI와 동일인 식별]]
    - [[#16.11 토큰 규격이 바뀐 이력|16.11 토큰 규격이 바뀐 이력]]
    - [[#16.12 구현 때 남는 일과 별도로 정할 항목|16.12 구현 때 남는 일과 별도로 정할 항목]]
- [[#17. OAuth 2.1: 무엇이 달라졌나|17. OAuth 2.1: 무엇이 달라졌나]]
    - [[#17.1 2.0 대비 변화|17.1 2.0 대비 변화]]
    - [[#17.2 IdP 인증 서버 대조|17.2 IdP 인증 서버 대조]]
- [[#18. 정리: 한 장 체크리스트|18. 정리: 한 장 체크리스트]]
    - [[#18.1 클라이언트(토큰을 받아 쓰는 쪽)를 만들 때|18.1 클라이언트(토큰을 받아 쓰는 쪽)를 만들 때]]
    - [[#18.2 인증 서버를 만들 때|18.2 인증 서버를 만들 때]]
    - [[#18.3 API(리소스 서버)를 만들 때|18.3 API(리소스 서버)를 만들 때]]
- [[#부록 A. OAuth 표준 연표|부록 A. OAuth 표준 연표]]
- [[#부록 B. IP 교환: 어디의 IP인가 (AWS 기준)|부록 B. IP 교환: 어디의 IP인가 (AWS 기준)]]

---

## 1. 용어집

처음 보는 용어가 나오면 이 표로 돌아온다. 자세한 설명은 오른쪽 절에 있다.

| 용어 | 한 줄 정의 | 자세히 |
|---|---|---|
| OAuth 2.0 | 비밀번호 대신 토큰으로 권한을 위임하는 표준. RFC 6749 | 2장 |
| OAuth 2.1 | 2.0 이후 보안 권고를 합치고 위험한 방식을 뺀 정리판. 2026년 11월 현재 IETF 초안(17판)이며 RFC로 확정되지 않았다 | 17장 |
| OIDC (OpenID Connect) | OAuth 위에 "누가 로그인했나"를 얹은 표준 | 9장 |
| 인증 (Authentication) | 당신이 누구인지 확인하는 것 | 2장 |
| 인가 (Authorization) | 당신이 무엇을 할 수 있는지 정하는 것 | 2장 |
| 클라이언트 (client) | 사용자 대신 토큰을 받아 쓰는 프로그램. 예: 클라이언트 앱 서버 | 3장 |
| 인증 서버 (Authorization Server) | 로그인을 받고 토큰을 발급하는 서버. 예: IdP 서비스의 로그인 서버 | 3장 |
| 리소스 서버 (Resource Server) | 토큰을 받고 실제 기능을 제공하는 API 서버. 예: IdP 서비스의 API | 3장 |
| RP / IdP | OIDC 용어. RP(Relying Party)는 남의 인증을 믿고 쓰는 쪽, IdP(Identity Provider)는 신원을 확인해 주는 쪽 | 9.10절 |
| client_id | 클라이언트의 공개 이름표 | 4.2절 |
| client_secret | 이름표가 진짜임을 증명하는 비밀번호 | 4.2절 |
| confidential client | client_secret 같은 비밀을 안전하게 보관할 수 있는 클라이언트. 예: 클라이언트 앱 서버 | 4.2절 |
| public client | 비밀을 보관할 수 없는 클라이언트. 앱 설치 파일이나 JS 번들에 넣은 비밀은 누구나 꺼낼 수 있다. 예: 모바일 앱, SPA | 4.2절 |
| front-channel / back-channel | 사용자 브라우저를 거치는 구간 / 서버끼리 직접 통신하는 구간 | 5.1절 |
| redirect_uri | 로그인 결과를 돌려보낼 클라이언트 주소 | 4.4절 |
| scope | 위임받으려는 권한의 범위 | 5.3절 |
| grant_type | token 엔드포인트에 "무엇을 근거로 토큰을 받는지" 알리는 값 | 6장 |
| authorization code | 로그인 직후 받는 일회용 교환권 | 7장 |
| access token | API를 호출할 때 내미는 출입증 | 8장 |
| refresh token | access token을 다시 받기 위한 증서 | 8장 |
| id_token | 로그인한 사람이 누구인지 담은 서명된 신분증 | 9.2절 |
| JWT (JSON Web Token) | 서명이 붙은 JSON 토큰 형식. `헤더.본문.서명` 세 덩어리 | 9.2절 |
| JWKS (JSON Web Key Set) | 토큰 서명을 검증할 공개키 목록 | 9.7절 |
| discovery | 인증 서버가 자기 주소와 규칙을 공개한 JSON 문서 | 9.6절 |
| PKCE | code를 가로채도 쓸 수 없게 묶는 장치. "픽시"로 읽음 | 7.3절 |
| state | 로그인 요청과 응답을 짝짓는 난수. CSRF 방지 | 7.2절 |
| nonce | 로그인 요청과 id_token을 짝짓는 난수. 재사용 방지 | 9.4절 |
| CSRF (Cross-Site Request Forgery) | 사용자가 의도하지 않은 요청을 다른 사이트가 대신 보내게 만드는 공격. OAuth에서는 callback을 노리는 것과 쿠키 인증 API를 노리는 것 두 가지가 있다 | 7.2절, 13.2절 |
| TLS (Transport Layer Security) | 통신을 암호화하고 서버를 인증하는 규약. HTTPS의 S | 11장 |
| mTLS (mutual TLS) | 클라이언트도 인증서를 내미는 TLS | 11장 |
| 웹뷰 (WebView) | 앱 안에 끼워 넣은 브라우저 화면 | 12장 |
| CI (연계정보) | 서로 다른 서비스에서 같은 사람인지 확인하는 국내 본인확인 식별값 | 16.10절 |
| bearer token | 가진 사람이 곧 주인인 토큰. 지금 대부분의 access token | 8.10절 |
| 발신자 제한 토큰 (sender-constrained) | 특정 클라이언트의 키가 있어야만 쓸 수 있게 묶은 토큰 | 8.10절, 15.6.2 |
| DPoP | 요청마다 비밀키 서명을 붙여 토큰을 키에 묶는 표준 (RFC 9449) | 15.6.2 |
| audience (`aud`) | 이 토큰을 받기로 정해진 대상. access token에서는 API | 10.6절 |
| introspection | 리소스 서버가 인증 서버에 토큰이 유효한지 묻는 API (RFC 7662) | 10.5절 |
| revocation | 토큰을 무효로 해 달라고 인증 서버에 요청하는 API (RFC 7009) | 8.8절 |
| consent (동의) | 사용자가 클라이언트에 권한을 위임하는 화면과 행위 | 7.8절 |
| response_mode | 인가 결과를 URL 쿼리·fragment·POST 본문 중 어디로 돌려받을지 | 7.7절 |
| SPA | 화면 대부분이 브라우저 JavaScript로 돌아가는 웹앱 | 13장 |
| XSS (Cross-Site Scripting) | 페이지에 악성 스크립트를 심어 그 페이지의 권한으로 실행시키는 공격 | 13.4절 |
| BFF (Backend for Frontend) | 브라우저 대신 토큰을 서버에 보관하고 중계하는 구조 | 13.3절 |
| origin / site | origin은 scheme+호스트+포트, site는 scheme+등록 가능한 도메인. 브라우저 보안 경계의 두 단위 | 13.2절 |
| CORS | 다른 origin의 JS가 API 응답을 읽어도 되는지 서버가 알려 주는 규칙 | 13.2절 |
| open redirector | 쿼리로 받은 아무 주소로 브라우저를 보내 주는 기능 | 15.4.2 |
| mix-up | 클라이언트가 응답을 어느 인증 서버가 줬는지 착각하게 만드는 공격 | 15.5.5 |
| PAR / JAR / RAR | authorize 요청을 미리 서버로 보내기 / 서명해 보내기 / 세밀한 권한 표현 | 14장 |
| Token Exchange | 받은 토큰을 다른 대상용 토큰으로 바꾸는 표준 (RFC 8693) | 14.6 |
| loopback redirect | 데스크톱·CLI 앱이 자기 컴퓨터의 임시 서버(127.0.0.1)로 로그인 결과를 받는 방식 | 12.6절 |
| RFC / BCP / IETF | 인터넷 표준 문서 / 그중 "모범 사례" 분류 / 표준을 만드는 기구 | 2.4절, 부록 A |

---

## 2. OAuth가 풀려는 문제

### 2.1 비밀번호를 넘기지 않고 권한만 빌려주기

앱 사용자가 클라이언트 앱 안에서 IdP 서비스의 기능을 쓰려면, 클라이언트 앱이 "이 사람은 IdP 서비스 회원 12345이고, 서비스 API를 써도 된다"는 것을 IdP 서비스에게 증명해야 한다. 가장 단순한 방법은 이것이다.

```
❌ 가장 단순하지만 나쁜 방법
사용자 ── IdP 서비스 이메일·비밀번호 ──► 클라이언트 앱 ──► 클라이언트 앱 서버가 보관
                                               │
                                               └─► IdP 서비스에 매번 비밀번호로 로그인
```

이 방법은 세 가지 문제를 만든다.

| 문제 | 무슨 일이 생기나 |
|---|---|
| 비밀번호 유출 범위 | 클라이언트 앱 서버가 털리면 IdP 서비스 계정이 통째로 넘어간다 |
| 권한을 좁힐 수 없음 | 비밀번호는 "모든 것을 할 수 있는 열쇠"라서, 서비스 이용만 허락하고 결제는 막는 식의 제한이 불가능하다 |
| 회수할 수 없음 | 클라이언트 앱 연결만 끊고 싶어도, 비밀번호를 바꾸는 것 말고 방법이 없다. 바꾸면 다른 곳의 로그인도 모두 끊긴다 |

OAuth는 이 문제를 **토큰**으로 푼다.

```
✅ OAuth 방식
사용자 ── IdP 서비스 비밀번호 ──► IdP 서비스(IdP 인증 서버)에만 입력
                                  │
                                  └─► 클라이언트 앱에게 "서비스 이용만 할 수 있는, 기한이 있는 토큰"을 발급
클라이언트 앱 서버 ── 토큰 ──► IdP 서비스 API
```

- 비밀번호는 **IdP 서비스에만** 입력된다.
- 클라이언트 앱은 **범위(scope)와 기한이 정해진 토큰**만 받는다.
- 연결을 끊으려면 **그 토큰만** 무효화하면 된다.

### 2.2 인증과 인가

두 단어는 비슷해 보이지만 묻는 질문이 다르다.

| | 인증 (Authentication) | 인가 (Authorization) |
|---|---|---|
| 묻는 질문 | 당신은 누구인가? | 당신은 무엇을 할 수 있는가? |
| 결과물 | "이 사람은 회원 12345다" | "이 토큰으로 서비스 API를 쓸 수 있다" |
| 담당 표준 | OpenID Connect | OAuth |
| 대표 토큰 | id_token | access token |

OAuth 자체는 **인가** 표준이다. "누가 로그인했는가"를 표준 방식으로 알려 주는 일은 OAuth 위에 얹은 OpenID Connect가 맡는다. 실무에서 "OAuth 로그인"이라고 부르는 것은 대부분 OAuth + OIDC 조합이다(9장).

### 2.3 OAuth가 아닌 것, OAuth와 헷갈리는 것

OAuth를 처음 배울 때 비슷한 말들과 섞이기 쉽다. 각각이 무엇을 하는지 구분해 두면 이후 장이 훨씬 쉽게 읽힌다.

| 이름 | 정체 | OAuth와의 관계 |
|---|---|---|
| **API key** | 앱(또는 개발자 계정)을 식별하는 고정 문자열. 오래 살고, 사용자 위임 개념이 없다 | OAuth access token은 **사용자가 위임한, 범위와 기한이 정해진** 토큰이다. API key로는 "이 사용자가 이 앱에 이것만 허락했다"를 표현할 수 없다 |
| **세션 쿠키** | 브라우저와 **자기 서버** 사이의 로그인 상태 | OAuth는 **서로 다른 회사·서비스** 사이의 위임이다. OAuth로 로그인한 뒤에도 클라이언트는 보통 자기 세션 쿠키를 따로 만든다(7.5절 8번, 9.11절) |
| **JWT** | 서명이 붙은 JSON 토큰 **형식** | OAuth의 토큰은 JWT일 수도, 아무 의미 없는 문자열(불투명 토큰)일 수도 있다. "JWT를 쓴다 = OAuth를 쓴다"가 아니다 |
| **OpenID Connect** | OAuth 위에 "누가 로그인했나"를 얹은 표준 | 9장 |
| **SSO** (Single Sign-On) | 한 번 로그인으로 여러 서비스를 쓰는 **사용자 경험** | SSO를 구현하는 수단이 OIDC나 SAML이다 |
| **SAML** | XML 기반의 기업용 SSO 표준. 브라우저 POST로 서명된 XML을 주고받는다 | OIDC가 같은 문제를 JSON·REST로 푼다. 자세한 비교는 [[sso-oauth-comparison-and-architecture]] |
| **OAuth 1.0** | 2007년 커뮤니티 사양으로 시작해 2010년 RFC 5849(정보 제공용 RFC)로 정리됐다. 요청마다 서명을 만들어야 했다 | 2.0은 서명 대신 TLS에 기대고 bearer token을 쓰는 방식으로 단순해졌다. 서로 호환되지 않는다. [[oauth1-concept-explainer]] |

**OAuth가 필요 없는 경우도 있다.** 같은 회사의 웹 프론트와 백엔드가 같은 도메인에서 돌아간다면, 로그인 상태는 평범한 세션 쿠키로 충분하다. 브라우저 앱 모범 사례(RFC 10017 7.1절)도 "단순한 앱이 세션 관리를 대신하려고 OAuth를 들여와 쓸데없이 복잡해지는 경우가 너무 많다"고 지적한다. OAuth가 값을 하는 때는 **서로 다른 주체 사이에서 권한을 위임할 때**다. 다른 회사의 앱이 우리 API를 쓰거나(클라이언트 앱 × IdP 서비스), 우리 앱이 다른 회사의 계정으로 로그인하거나(카카오 로그인), 여러 서비스가 로그인을 한 곳(인증 서버)에 모을 때다.

### 2.4 버전 흐름 한눈에 보기

```
2012          2013~2023                         2025-01         2026-08          2026-10
OAuth 2.0 ──► 쓰면서 드러난 문제를 확장 표준이 ──► 보안 모범 사례 ──► 브라우저 앱 ───► OAuth 2.1 초안 17판
(RFC 6749)    하나씩 메움 (PKCE, 네이티브 앱,      (RFC 9700)       모범 사례        (아직 RFC 아님)
              JWT access token, DPoP …)                           (RFC 10017)
```

RFC는 IETF(Internet Engineering Task Force, 인터넷 표준을 만드는 기구)가 번호를 붙여 발행하는 문서이고, BCP(Best Current Practice)는 그중 "현재 모범 사례"로 분류된 문서다.

"OAuth"는 문서 하나가 아니라 **표준 가족**이다. 2.0 본체가 나온 뒤 10여 년 동안 쌓인 보완 표준과 보안 교훈을 하나로 합치는 작업이 OAuth 2.1이다. 초안 17판 10절은 합치는 대상을 이렇게 밝힌다.

```
RFC 6749 (2.0 본체) ─────┐
RFC 6750 (Bearer) ──────┤
RFC 7636 (PKCE) ────────┤
RFC 8252 (네이티브 앱) ───┼──► OAuth 2.1  (implicit·password 제외, PKCE 기본, 보안 권고 반영)
RFC 9700 (보안 BCP) ─────┤
RFC 10017 (브라우저 앱) ──┘
```

그래서 2.1을 이해하는 가장 빠른 길은 "2.0 + 그 뒤 10여 년의 보안 교훈"으로 보는 것이다. 바뀐 점은 17장에서, 연도별 표준 목록은 부록 A에서 정리한다. 지금은 RFC 번호를 외울 필요가 없다. 본문에서 필요할 때마다 그 번호가 무엇인지 함께 적는다.

---

## 3. 등장인물과 관계

### 3.1 OAuth의 네 역할

```
          ┌──────────────────────────┐
          │  Resource Owner (사용자)    │  자기 데이터·권한의 주인
          └─────┬───────────────▲────┘
       ① 로그인·동의│               │
                ▼               │
┌──────────────────────┐        │        ┌──────────────────────────┐
│ Authorization Server │ ② 토큰 발급 ──►  │ Client                    │
│ (인증 서버, 예: IdP 서비스)│◄── 토큰 요청 ───│ (클라이언트, 예: 앱 서버)    │
└──────────────────────┘                 └────────────┬─────────────┘
                                                      │ ③ 토큰을 내밀고 API 호출
                                                      ▼
                                         ┌──────────────────────────┐
                                         │ Resource Server           │
                                         │ (리소스 서버, 예: IdP 서비스 API)│
                                         └──────────────────────────┘
```

| 역할 | 하는 일 | 클라이언트 앱 × IdP 서비스 연동에서 |
|---|---|---|
| Resource Owner | 권한을 위임하는 사람 | 클라이언트 앱 사용자이자 IdP 서비스 회원 |
| Client | 사용자 대신 토큰을 받아 쓰는 프로그램 | 클라이언트 앱 서버 |
| Authorization Server | 로그인을 받고 토큰을 발급 | IdP 인증 서버 |
| Resource Server | 토큰을 검증하고 기능을 제공 | IdP 서비스 웹·Agent API |

인증 서버와 리소스 서버는 같은 회사(IdP 서비스)가 운영하는 경우가 많지만, 역할은 분리된다. 인증 서버는 토큰을 **발급**하고, 서비스 API는 토큰을 **검증**한다.

### 3.2 이번 연동은 양방향이다

이 연동에는 OAuth 관계가 두 개 있다. 처음 보면 가장 헷갈리는 지점이다.

```
[관계 A] 계정 연결과 서비스 이용            [관계 B] IdP 서비스가 클라이언트 앱 기능을 호출
  클라이언트:  클라이언트 앱 서버            클라이언트:  IdP 서비스 서버
  인증 서버:   IdP 서비스의 인증 서버         인증 서버:   클라이언트 앱 제휴사 API의 토큰 발급기
  리소스 서버: IdP 서비스의 서비스 API        리소스 서버: 클라이언트 앱 제휴사 API
  사용자:     있음 (로그인함)                사용자:     없음 (서버끼리)
  grant_type: authorization_code          grant_type: client_credentials
              + refresh_token
```

같은 회사가 한 관계에서는 인증 서버이고, 다른 관계에서는 클라이언트다. 그래서 "우리 client_secret"이라는 말이 두 가지 뜻이 될 수 있다. 이 문서에서는 관계 A의 것을 "인증 서버에 등록된 클라이언트 앱", 관계 B의 것을 "클라이언트 앱에 등록된 IdP 서비스 클라이언트"라고 구분해 부른다.

### 3.3 클라이언트 유형별로 맞는 흐름

어떤 클라이언트를 만드느냐에 따라 쓸 흐름과 지킬 것이 정해진다. 처음 설계할 때 이 나무부터 따라간다. 처음 읽을 때는 큰 그림만 보고, 각 장을 읽은 뒤 다시 돌아와 보면 잎마다 무슨 뜻인지 보인다. 표의 confidential은 비밀(secret)을 안전하게 보관할 수 있는 클라이언트, public은 그럴 수 없는 클라이언트라는 뜻이다(4.2절).

```
사용자가 흐름에 끼는가?
 ├─ 아니오 (서버가 자기 일을 함) ──────────────────► client_credentials (6.2절)
 └─ 예 (사용자를 대신함)
     ├─ 기기에 브라우저가 없거나 입력이 불편한가? (스마트 TV, 브라우저 없는 서버 터미널) ─► Device Authorization Grant (14.5)
     └─ 아니오
         ├─ 서버가 있는 웹앱 ─────────► authorization code + PKCE, confidential client (7장)
         ├─ 브라우저 앱 (SPA) ─────────► authorization code + PKCE, 가능하면 BFF 구조 (13장)
         └─ 모바일·데스크톱·CLI 앱 ────► authorization code + PKCE, public client,
                                         시스템 브라우저로 로그인 (12장. CLI는 loopback, 12.6절)

받은 토큰으로 다른 서비스를 사용자 대신 불러야 하는가? ──► Token Exchange (14.6)
```

| 클라이언트 | 예 | 클라이언트 종류 | 토큰을 어디에 두나 | 로그인 결과를 받는 방법 |
|---|---|---|---|---|
| 서버 웹앱 | 클라이언트 앱 서버, 일반 웹서비스 | confidential | 서버 세션·DB | 서버의 https 콜백 |
| 브라우저 앱 | React SPA | public (BFF를 두면 BFF가 confidential) | BFF 서버. BFF가 없을 때만 브라우저 메모리(13.5절) | https 콜백 |
| 네이티브 앱 | iOS·Android·데스크톱 앱 | public | OS 보안 저장소 (iOS Keychain, Android는 Keystore 키로 암호화해 저장) | https 앱 링크, loopback 주소, 앱 전용 scheme |
| 서버 간 | 배치 작업, IdP 서비스 → 클라이언트 앱 호출 | confidential | 서버 메모리 캐시 | 없음 (사용자 없음) |
| 입력 제약 기기 | 스마트 TV, 브라우저 없는 서버 터미널(SSH 접속 등) | 보통 public | 기기 저장소 | 없음 (폴링) |

**네이티브 앱이 로그인 결과를 받는 세 가지 방법** (RFC 8252 7절)

| 방법 | 예 | 특징 |
|---|---|---|
| https 앱 링크 | `https://app.example.com/oauth/cb` | 도메인 소유를 증명해야 OS가 앱으로 넘긴다. 가장 안전 (12.4절) |
| loopback 주소 | `http://127.0.0.1:51004/cb` | 데스크톱 앱이 잠깐 로컬 서버를 열어 받는다. 포트는 실행할 때마다 바뀌어도 된다 |
| 앱 전용 scheme | `com.example.app:/oauth/cb` | 자기가 소유한 도메인을 거꾸로 쓴 이름이어야 한다(MUST, RFC 8252 7.1절). 그래도 다른 앱이 같은 scheme을 등록해 결과를 가로챌 수 있어 세 방법 중 가장 약하다 |

어느 방법을 쓰든 네이티브 앱은 public client이므로 PKCE가 필수다(RFC 8252 8.1절). 결과가 가로채이더라도 PKCE 원본값이 없으면 토큰으로 바꿀 수 없다. IdP 인증 서버는 앱 전용 scheme을 redirect_uri로 받지 않으므로, 클라이언트 앱은 서버의 https 주소로 콜백을 받는다.

---

## 4. 사전 등록: 클라이언트 등록 카드

OAuth 연동은 코드를 쓰기 전에 **서로를 등록하는 일**부터 시작한다. 인증 서버는 "이 앱이 누구이고, 어떻게 자기를 증명하고, 무엇을 요청할 수 있고, 결과를 어디로 받는가"를 미리 알고 있어야 한다. 이 정보를 이 문서에서는 **클라이언트 등록 카드**라고 부른다.

### 4.1 등록 카드에 들어가는 것

관계가 두 개이므로 카드도 두 장이다.

```
[카드 A] IdP 인증 서버에 등록된 "클라이언트 앱"            [카드 B] 클라이언트 앱 제휴사 API에 등록된 "idp-client"
  용도: 계정 연결 (사용자 로그인)            용도: IdP 서비스 서버가 클라이언트 앱 API 호출
  발급: IdP 서비스(IdP 인증 서버)                     발급: 클라이언트 앱
```

**카드 A: IdP 인증 서버에 등록된 클라이언트 앱**

| 항목 | 값 | 의미 |
|---|---|---|
| client_id | IdP 서비스가 발급 | "나는 클라이언트 앱이다"라는 이름표. 공개돼도 되는 값 |
| client_secret | IdP 서비스가 발급 | 이름표가 진짜임을 증명하는 비밀번호. 클라이언트 앱 서버에만 보관 |
| 클라이언트 인증 방식 | `client_secret_basic` | 토큰을 요청할 때 위 두 값을 어떻게 보내는지 (4.3절) |
| redirect_uri | 환경별 3개 (local·dev·stg) | 로그인 결과를 돌려받을 클라이언트 앱 서버 주소 (4.4절) |
| 허용 grant_type | `authorization_code`, `refresh_token` | 이 클라이언트가 쓸 수 있는 토큰 발급 방식 (6장) |
| scope | `openid email` | 클라이언트 앱이 요청할 수 있는 권한의 범위 (5.3절, 9.5절) |
| PKCE | S256 필수 | code 가로채기 방지 장치를 반드시 쓰라는 설정 (7.3절) |
| 토큰 수명 | access 60분, refresh 14일 (rotation) | 이 클라이언트에게 발급할 토큰 규칙 (8장) |
| post_logout_redirect_uri | 선택 | 로그아웃 후 돌아갈 주소 (구현할 때만) |

**카드 B: 클라이언트 앱 제휴사 API에 등록된 IdP 서비스 클라이언트**

| 항목 | 값 |
|---|---|
| client_id | `idp-client` (모든 환경 동일) |
| client_secret | 환경별로 클라이언트 앱이 발급 |
| 클라이언트 인증 방식 | `client_secret_basic` 권장 |
| 허용 grant_type | `client_credentials` |
| scope | 제휴사별 등록 범위 |
| redirect_uri | **없음** |

카드 B에는 redirect_uri가 없다. 사용자가 끼지 않고 서버끼리 바로 토큰을 주고받는 방식이라, 결과를 브라우저로 돌려보낼 일이 없기 때문이다(6.2절).

### 4.2 client_id와 client_secret

**client_id는 "어느 앱인가"를 밝히는 공개 이름표이고, client_secret은 "그 이름표가 진짜다"를 증명하는 비밀번호다.** 사람으로 치면 아이디와 비밀번호인데, 주인이 사람이 아니라 **서버 프로그램**이라는 점이 다르다.

| | client_id | client_secret |
|---|---|---|
| 비유 | 아이디 | 비밀번호 |
| 공개해도 되나 | ✅ authorize URL에 그대로 노출된다 | ❌ 서버 비밀 저장소에만 둔다 |
| 어디에 등장하나 | authorize 요청(브라우저), token 요청, id_token의 `aud` | token 요청(서버 대 서버)에만 |
| 누가 만드나 | 인증 서버가 등록할 때 발급 | 인증 서버가 등록할 때 발급 |
| 바뀌나 | 거의 바뀌지 않는다 | 유출이 의심되거나 주기적으로 교체한다 |

**client_id가 노출돼도 괜찮은 이유**: 공격자가 클라이언트 앱의 client_id로 authorize를 시작해도, code는 **등록된 클라이언트 앱의 redirect_uri로만** 가고, 그 code를 토큰으로 바꾸려면 **secret과 PKCE 원본값**이 필요하다. client_id 하나로는 아무것도 얻을 수 없다.

**secret은 왜 상대방에게 받아야 하나**: 토큰을 발급하는 인증 서버가 그 값을 알고 있어야 대조할 수 있으므로, 인증 서버 쪽이 만들어 건네는 것이 표준이다. IdP 인증 서버에 등록된 클라이언트 앱의 secret은 IdP 서비스가 만들어 주었고, 클라이언트 앱에 등록된 IdP 서비스의 secret은 클라이언트 앱이 만들어 주었다.

이 방식에는 **비밀을 양쪽이 모두 들고 있다**는 약점이 있다. 전달 과정에서 새거나, 인증 서버의 DB에서 샐 수 있다. 비밀을 공유하지 않는 대안이 있다.

| 방식 | 비밀은 누가 가지나 | 인증 서버에 주는 것 |
|---|---|---|
| `client_secret_basic` / `client_secret_post` | 양쪽 모두 | secret 원본 |
| `private_key_jwt` | 클라이언트만 | **공개키만** (또는 JWKS 주소) |
| `tls_client_auth` (mTLS) | 클라이언트만 | 인증서 정보 |

`private_key_jwt`에서는 클라이언트가 키 쌍을 직접 만들고, 토큰을 요청할 때마다 비밀키로 서명한 짧은 JWT를 보낸다. 인증 서버는 공개키로 검증만 한다. 비밀이 전달되는 일 자체가 없다.

#### confidential client와 public client

secret을 안전하게 가질 수 있느냐로 클라이언트를 두 종류로 나눈다.

| 종류 | 예 | secret | 대신 의지하는 것 |
|---|---|---|---|
| **confidential** | 클라이언트 앱 백엔드, IdP 서비스 서버 | ✅ 서버에 안전하게 보관 가능 | secret + PKCE |
| **public** | 모바일 앱, 브라우저에서만 도는 SPA(Single Page Application, 13장) | ❌ 앱 안에 넣으면 누구나 꺼낼 수 있다 | PKCE만 |

클라이언트 앱이 아니라 **클라이언트 앱 서버**가 토큰을 받게 한 것은 이 구분 때문이다. 앱 설치 파일에 넣은 secret은 디컴파일로 꺼낼 수 있어서 비밀이 아니다.

#### secret을 관리할 때 지킬 것

- **환경마다 다른 secret을 쓴다.** dev의 secret이 새도 prd는 안전해야 한다.
- **비밀 저장소에만 둔다.** AWS라면 Secrets Manager나 SSM Parameter Store(SecureString)에 넣고, 애플리케이션이 기동할 때 읽는다. 소스 코드, 커밋된 `.env`, 로그, 메신저에 남기지 않는다.
- **교체 절차를 미리 정한다.** 한 번에 바꾸면 그 사이 요청이 실패한다. 그래서 인증 서버가 **잠시 두 secret을 동시에 허용**하는 기간을 두고, 클라이언트가 새 값으로 바꾼 뒤 옛 값을 지운다.
- **메신저로 받은 secret은 받은 즉시 비밀 저장소로 옮기고 메시지를 지운다.** 운영 환경 secret은 메신저가 아닌 경로(일회용 비밀 공유 링크 등)로 주고받는다.

### 4.3 클라이언트 인증 방식: client_secret_basic

**token 엔드포인트에 요청할 때 client_id와 secret을 HTTP `Authorization` 헤더에 Basic 인증 형식으로 넣는 방식**이다. 방식 자체는 RFC 6749 2.3.1절에 정의돼 있고, `client_secret_basic`이라는 이름은 동적 클라이언트 등록 표준(RFC 7591)과 OIDC Core가 이 방식에 붙인 것이다.

**만드는 법**

```
1) client_id와 secret을 각각 URL 인코딩       idp-client  /  s3cr+t   →  s3cr%2Bt
2) 콜론으로 이어 붙임                          idp-client:s3cr%2Bt
3) Base64 인코딩                              aWRwLWNsaWVudDpzM2NyJTJCdA==
4) 헤더에 넣음                                Authorization: Basic aWRwLWNsaWVudDpzM2NyJTJCdA==
```

**실제 요청** (IdP 서비스 서버가 클라이언트 앱 제휴사 API에 client_credentials 토큰을 요청하는 경우, 카드 B)

```http
POST /oauth/token HTTP/1.1
Host: stg-partner.client.example
Authorization: Basic aWRwLWNsaWVudDpzM2NyJTJCdA==
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
```

curl의 `-u 'id:secret'` 옵션은 Base64 헤더를 만들어 주지만 **1단계의 URL 인코딩은 하지 않는다.** `curl -u 'idp-client:s3cr+t'`가 보내는 헤더는 `Basic aWRwLWNsaWVudDpzM2NyK3Q=`로, 위의 값과 다르다. secret에 `+`, `/`, `=` 같은 문자가 있으면 `-u 'idp-client:s3cr%2Bt'`처럼 미리 인코딩한 값을 넣는다.

**`client_secret_post`와의 차이**

| | basic | post |
|---|---|---|
| secret 위치 | `Authorization` 헤더 | 요청 본문(`client_id=…&client_secret=…`) |
| OAuth 2.0 (RFC 6749) | secret을 발급한 인증 서버는 **반드시 지원(MUST)** | **권장하지 않음(NOT RECOMMENDED).** Basic을 못 쓰는 클라이언트용 |
| OAuth 2.1 (초안 17판) | 지원은 **선택(MAY)** | 인증 서버가 **반드시 지원(MUST)** |
| 로그에 남을 위험 | 헤더는 보통 마스킹된다 | 본문을 로깅하는 미들웨어가 있으면 그대로 남는다 |

**2.1 초안에서 우선순위가 뒤집힌 이유**: 아래 "주의할 점"의 URL 인코딩 단계를 구현마다 다르게 처리해서, Basic 방식이 실제로는 상호운용 문제를 많이 일으켰기 때문이다. 2.1 초안이 그 경험을 반영해 본문 방식을 필수로 바꿨다.

IdP 인증 서버는 basic만 받고, post로 보내면 `401 invalid_client`로 거부한다. 이 동작은 OAuth 2.0 기준으로는 문제가 없지만, OAuth 2.1 초안 기준으로는 "본문 방식을 반드시 지원"하라는 규칙과 맞지 않는다(17장).

**주의할 점 두 가지**

- **Base64는 암호화가 아니다.** 누구나 되돌릴 수 있는 인코딩이므로 반드시 HTTPS(TLS) 위에서만 보낸다(11장).
- **1단계의 URL 인코딩을 빠뜨리는 구현이 많다.** secret에 `+`, `/`, `=` 같은 문자가 있으면 라이브러리마다 인코딩 여부가 달라서 `401 invalid_client`가 난다.

### 4.4 redirect_uri

**redirect_uri는 "로그인 결과(authorization code)를 돌려보낼 클라이언트 주소"다.** 이 주소를 미리 등록해 두는 이유는 공격자가 자기 주소로 code를 빼돌리지 못하게 막기 위해서다.

#### 정상 흐름에서의 역할: 로그인 결과의 반송 주소

```
클라이언트 앱 서버 ── "이 사용자 로그인시켜 줘, 끝나면 여기로 보내 줘"
             redirect_uri = https://stg-app.client.example/authorize/oauth2/code/idp
                 │
                 ▼
IdP 인증 서버 ── 사용자 로그인 완료 ── 브라우저(웹뷰)에게 302 응답:
        "https://stg-app.client.example/authorize/oauth2/code/idp?code=c-5d1e&state=…로 가라"
                 │
                 ▼
브라우저 → 클라이언트 앱 서버 도착 → 클라이언트 앱 서버가 code를 들고 IdP 인증 서버에 토큰 요청
```

IdP 인증 서버는 로그인이 끝난 사용자의 브라우저를 클라이언트 앱으로 돌려보내야 하는데, 브라우저에게 "어디로 가라"고 알려 줄 주소가 redirect_uri다. 이때 URL에 일회용 authorization code가 함께 실린다.

#### 🛡️ 공격: redirect_uri 조작으로 code 가로채기

**공격 원리**: 인증 서버가 요청에 들어온 redirect_uri를 검사 없이 따른다면, 공격자는 자기 서버 주소를 넣은 로그인 링크를 피해자에게 보낸다. 피해자는 진짜 IdP 서비스 로그인 화면을 보고 안심하고 로그인한다. 그러면 code가 공격자 서버로 간다.

```
공격자가 만든 링크:
  IdP 인증 서버 /authorize?client_id=client-app&redirect_uri=https://evil.example/steal …
        │
피해자가 클릭 → 평소처럼 IdP 서비스 로그인 (화면은 진짜 IdP 인증 서버)
        │
IdP 인증 서버 → 302 → https://evil.example/steal?code=…   ← code가 공격자에게 감
```

**방어**: IdP 인증 서버는 **등록된 redirect_uri와 한 글자라도 다르면 리다이렉트하지 않고 자기 화면에 오류를 띄운다.**

**방어 원리**: code가 갈 수 있는 목적지를 등록 시점에 고정하면, 요청을 조작해도 목적지를 바꿀 수 없다. 오류를 redirect로 돌려보내지 않고 IdP 인증 서버 화면에 띄우는 것도 같은 이유다. 검증되지 않은 주소로는 어떤 응답도 보내지 않는다.

그래서 "끝의 `/`와 포트까지 그대로 등록한다". 실제 연동에서도 클라이언트 앱이 처음 보낸 주소(`/authorize/code/oauth2/idp`)가 틀려서 `/authorize/oauth2/code/idp`로 다시 등록했다. 경로 순서가 바뀐 것만으로 로그인이 실패하는 구조다.

#### 토큰 교환 때 한 번 더 대조한다

클라이언트 앱 서버가 code를 토큰으로 바꿀 때도 같은 redirect_uri를 다시 보낸다. IdP 인증 서버는 "authorize 때 쓴 주소와 지금 보낸 주소가 같은가"를 확인하고, 다르면 `invalid_request`로 거부한다(RFC 6749 5.2절은 이 경우의 오류 코드를 `invalid_grant`로 정하지만, IdP 인증 서버 구현은 `invalid_request`를 돌려준다). OAuth 2.0(RFC 6749 4.1.3절)은 authorize 요청에 redirect_uri를 넣었다면 token 요청에도 같은 값을 넣고, 서버가 둘이 같은지 확인하도록 정한다.

OAuth 2.1 초안은 이 파라미터를 token 요청에서 **없앴다**. PKCE(7.3절)가 "다른 곳에서 얻은 code를 끼워 넣는" 공격을 이미 막으므로, redirect_uri를 다시 보내는 것이 더 이상 쓸모가 없다는 이유다. 다만 2.0 클라이언트와 2.1 클라이언트를 함께 받는 인증 서버는, 이 값이 들어오면 받아들이고 2.0 규칙대로 검사해야 한다.

#### localhost 주소가 등록돼도 동작하는 이유

| 등록된 주소 | 용도 |
|---|---|
| `http://localhost:8080/authorize/oauth2/code/idp` | 클라이언트 앱 개발자 PC에서 테스트 |
| `https://dev-app.client.example/authorize/oauth2/code/idp` | 클라이언트 앱 dev 서버 |
| `https://stg-app.client.example/authorize/oauth2/code/idp` | 클라이언트 앱 stg 서버 |

IdP 인증 서버가 그 주소에 접속하는 것이 아니라 **브라우저에게 "거기로 가라"고 말할 뿐**이기 때문이다. 브라우저가 자기 PC의 8080 포트로 돌아가면 된다. 공인 IP나 방화벽 설정이 필요 없다.

### 4.5 방화벽(IP 허용)과 클라이언트 등록은 무엇이 다른가

방화벽과 클라이언트 등록은 막는 대상이 다르다. 방화벽은 "**어느 IP에서** 온 요청인가"를 보고, 클라이언트 등록은 "**어느 앱이 무엇을** 요청하는가"를 본다. 그리고 OAuth에는 **방화벽으로 막을 수 없는 구간**이 있다.

```
[구간 1] 사용자 브라우저(웹뷰) ──► IdP 인증 서버 /oauth/authorize/      ← 전 세계 어느 IP에서든 와야 함
[구간 2] 클라이언트 앱 서버            ──► IdP 인증 서버 /oauth/token/          ← 서버 간. IP 제한 가능
[구간 3] IdP 인증 서버가 브라우저에 302 ──► redirect_uri                ← 방화벽이 관여할 수 없는 "응답 내용"
```

- **구간 1**: 사용자는 집, 회사, LTE 등 어디서든 로그인하므로 IP로 거를 수 없다. `/authorize`는 인터넷 전체에 열려 있어야 한다.
- **구간 3**: 4.4절의 code 탈취 공격이 일어나는 곳이다. 공격은 "IdP 인증 서버가 어디로 302를 보내느냐"를 조작하는 것이라 방화벽은 관여할 수 없다. 등록된 redirect_uri 대조만 이 공격을 막는다.
- **구간 2**: IP 제한이 가능하지만 IP만으로는 부족하다. 클라우드에서는 같은 IP 대역을 여러 서비스가 나눠 쓰고, 클라이언트 앱 내부의 다른 시스템도 같은 IP에서 나온다. client_id와 secret은 "IP가 맞다"를 넘어 "**정확히 이 연동용 클라이언트 앱 서버다**"까지 증명한다.

그래서 둘은 서로를 대체하지 않고 겹쳐 쓴다. 연동 규격도 dev·stg에서는 IP 등록과 클라이언트 인증을 **둘 다** 요구한다.

서버 간 구간의 IP 허용을 실제로 설정할 때 "어느 IP를 주고받는가"는 부록 B에서 AWS 기준으로 설명한다.

### 4.6 동적 클라이언트 등록 (RFC 7591)

지금까지 본 등록 카드는 사람이 메신저와 문서로 주고받았다. 클라이언트가 많거나, 미리 짝지을 수 없는 개방형 생태계에서는 **클라이언트가 API로 스스로 등록**한다.

```http
POST /register
Content-Type: application/json

{
  "client_name": "Example Tax Helper",
  "redirect_uris": ["https://helper.example.com/oauth/cb"],
  "grant_types": ["authorization_code", "refresh_token"],
  "token_endpoint_auth_method": "private_key_jwt",
  "jwks_uri": "https://helper.example.com/.well-known/jwks.json"
}
```

```json
HTTP/1.1 201 Created
Content-Type: application/json

{
  "client_id": "s6BhdRkqt3",
  "client_id_issued_at": 1793000000,
  "client_name": "Example Tax Helper",
  "redirect_uris": ["https://helper.example.com/oauth/cb"],
  "grant_types": ["authorization_code", "refresh_token"],
  "token_endpoint_auth_method": "private_key_jwt",
  "jwks_uri": "https://helper.example.com/.well-known/jwks.json"
}
```

응답에는 서버가 정한 값(`client_id` 등)과 함께 등록된 메타데이터가 전부 들어온다(RFC 7591 3.2.1절, MUST).

**보안 주의**: 누구나 클라이언트를 만들 수 있다는 것은 **공격자도** 만들 수 있다는 뜻이다. 동적 등록은 여러 공격의 출발점이 된다.

| 공격자가 동적 등록으로 하는 일 | 자세히 |
|---|---|
| 자기 인증 서버를 클라이언트에 붙여 mix-up을 일으킴 | 15.5.5 |
| redirect URI를 피싱 사이트로 두고, 진짜 인증 서버 링크를 피싱에 씀 | 15.4.2 |
| 자기 client_id를 사용자 ID와 같은 값으로 골라 사용자인 척함 | 15.7.1 |
| 그럴듯한 이름으로 등록해 동의 화면에서 사용자를 속임 | 7.8절 |

방어는 공격마다 자리가 다르다.

| 공격 | 누가 막나 | 어떻게 |
|---|---|---|
| mix-up | 클라이언트 | 공격자 인증 서버에 동적으로 등록되는 쪽은 클라이언트다. 인가 응답의 `iss`를 대조한다(7.5절, 15.5.5) |
| 인증 서버를 피싱 중계기로 쓰기 | 인증 서버 | 동적 등록 클라이언트의 redirect URI로는 자동 이동하지 않고, 이동 전에 사용자를 먼저 인증한다(15.4.2) |
| client_id로 사용자 사칭 | 인증 서버 | client_id는 서버가 정한다. 클라이언트가 고르게 하지 않는다(15.7.1) |
| 그럴듯한 이름으로 속이기 | 인증 서버 | 등록 메타데이터는 클라이언트가 스스로 주장한 값으로 취급하고(RFC 7591 5절, MUST), 동의 화면에 "확인되지 않은 앱" 경고를 띄운다(7.8절) |

공통으로, 아무나 등록하지 못하게 사전에 발급한 등록용 토큰(initial access token)을 요구할 수 있다.

---

## 5. 엔드포인트 지도

OAuth와 OIDC의 인증 서버는 몇 개의 정해진 주소(엔드포인트)를 가진다. IdP 인증 서버 스테이징 기준으로 정리하면 이렇다.

| 엔드포인트 | IdP 인증 서버 주소 (스테이징) | 형태 | 누가 부르나 | 용도 |
|---|---|---|---|---|
| authorize | `/oauth/authorize/` | **HTML 페이지** | 사용자의 브라우저(웹뷰) | 로그인·동의 화면, code 발급 |
| token | `/oauth/token/` | JSON API | 클라이언트 서버 | code·refresh_token 등을 토큰으로 교환 |
| discovery | `/.well-known/openid-configuration` | JSON | 클라이언트 라이브러리 | 나머지 주소와 지원 규칙 공개 (9.6절) |
| JWKS | `/.well-known/jwks.json` | JSON | 토큰을 검증하는 모든 쪽 | 서명 검증용 공개키 (9.7절) |
| userinfo | discovery에 기재 | JSON API | 클라이언트 서버 | access token으로 사용자 정보 조회 (9.8절) |
| logout | `/oauth/logout/` | HTML 리다이렉트 | 사용자의 브라우저 | 로그아웃 후 등록된 주소로 복귀 (선택) |

### 5.1 authorize와 token을 나누는 이유

```
            ┌────────── front-channel (브라우저를 거침) ──────────┐
사용자 브라우저 ──► authorize ──► 로그인·동의 ──► 302 redirect_uri?code=…
            └──────────────────────────────────────────────────┘
                                                         │ code만 노출
            ┌────────── back-channel (서버끼리) ──────────────────┐
클라이언트 서버 ──► token (code + secret + PKCE 원본) ──► 토큰들
            └──────────────────────────────────────────────────┘
```

- **authorize는 로그인과 동의를 받는, 사람이 거치는 엔드포인트다.** 그래서 인터넷 전체에 열려 있어야 하고, IP로 막을 수 없다. 결과는 **토큰이 아니라 code**다. 브라우저 URL에는 노출돼도 덜 위험한 일회용 값만 싣는다.
- **token은 브라우저가 아니라 서버가 직접 호출한다.** 그래서 client_secret을 실어 보낼 수 있고, IP 제한도 걸 수 있다.

**사용자 기기를 거치는 구간(front-channel)과 서버끼리의 구간(back-channel)을 분리하는 것**이 OAuth 설계의 뼈대다. 사람의 동의는 브라우저에서 받고, 비밀이 오가는 교환은 서버끼리만 한다.

**공격자는 front-channel에서 더 많은 것을 할 수 있다.** 브라우저를 거치는 구간은 사용자 기기, 브라우저 확장 프로그램, 프록시 로그, 같은 기기의 다른 앱처럼 클라이언트와 인증 서버가 통제할 수 없는 곳을 지난다. 그래서 OAuth의 보안 장치 대부분(redirect_uri 대조, state, PKCE, `iss`)이 front-channel에 몰려 있다. 이 문서는 공격자가 다음을 할 수 있다고 가정하고 🛡️ 표시가 붙은 공격들을 설명한다. 자세한 분류는 15.2절에 있다.

| 공격자 | 할 수 있는 것 |
|---|---|
| 웹 공격자 | 자기 사이트와 **자기 인증 서버·리소스 서버**를 운영하고, 사용자를 아무 링크로 유인하고, 정상 인증 서버에 자기 클라이언트를 등록한다 |
| 네트워크 공격자 | TLS로 보호되지 않은 통신을 엿보고 바꾼다 |
| 응답·요청 열람자 | 브라우저 URL(인가 요청·응답)을 로그·히스토리 등으로 읽는다 |
| 토큰 탈취자 | 어떤 경로로든 access token 하나를 손에 넣었다 |

### 5.2 "webview를 요청하는 API"는 따로 없다

클라이언트 앱은 IdP 인증 서버에 JSON 요청을 보내 로그인 화면을 받아 오는 것이 아니다. **IdP 인증 서버의 authorize 주소(URL)를 만들어서 브라우저로 그 주소를 연다.** 브라우저가 일반 GET 요청을 보내고, IdP 인증 서버는 HTML 로그인 페이지를 돌려준다. IdP 인증 서버 쪽에는 "로그인 화면을 내려 주는 API"가 따로 있는 것이 아니라, **브라우저가 열 수 있는 로그인 페이지 주소 하나**가 있을 뿐이다. JSON API 호출은 그 뒤 클라이언트 서버가 token 엔드포인트를 부를 때 처음 등장한다.

### 5.3 scope: 위임하는 권한의 범위

**scope는 클라이언트가 사용자에게 위임받으려는 권한의 범위**다. authorize 요청의 `scope` 파라미터에 공백으로 구분한 문자열로 넣는다. 사용자가 동의 화면(7.8절)에서 승인하고 인증 서버가 허락한 만큼만 토큰에 담긴다.

```
클라이언트 요청      scope=service:read service:write offline_access
                          │
사용자 동의 화면      "서비스 읽기 ✓   서비스 쓰기 ✗   오프라인 접근 ✓"
                          │
인증 서버 판단        + 이 클라이언트에 허용된 범위인가? (등록 카드, 4.1절)
                          ▼
토큰 응답            "scope": "service:read offline_access"    ← 요청보다 좁아질 수 있다
```

| 규칙 | 근거 |
|---|---|
| 인증 서버는 요청한 scope를 전부 또는 일부 무시할 수 있다 | RFC 6749 3.3절 |
| 발급한 scope가 요청과 다르면, 토큰 응답에 `scope`를 반드시 넣는다 | RFC 6749 3.3절 (MUST) |
| OAuth 자체는 scope 값을 하나도 정하지 않는다. 값은 각 서비스가 정의한다 | OAuth 2.1 초안 1.4.1절 |
| refresh 때는 처음 위임받은 범위를 넘을 수 없다 | RFC 6749 6절 (8.5절) |
| 등록 범위를 벗어난 scope는 빼고 발급하거나 `invalid_scope`로 거부한다. 어느 쪽인지는 인증 서버가 정한다(IdP 인증 서버는 거부, 9.5절) | RFC 6749 3.3절 |
| scope를 생략하면 인증 서버가 미리 정한 기본값으로 처리하거나 `invalid_scope`로 거부한다(MUST). 기본값은 문서로 공개하는 것이 권장된다(SHOULD) | RFC 6749 3.3절, OAuth 2.1 초안 1.4.1절 |

**클라이언트가 할 일**: 토큰 응답의 `scope`를 확인한다. 요청한 권한이 빠져 있다면 그 기능을 끄거나 사용자에게 다시 동의를 구한다. "요청했으니 받았겠지"라고 가정하면, API를 부를 때 `403 insufficient_scope`(8.6절)를 만나고서야 알게 된다.

scope 값에는 두 종류가 있다. OIDC가 정의한 `openid`·`email` 같은 **사용자 정보 scope**(9.5절)와, 서비스가 정의한 `service` 같은 **API scope**다. API scope를 어떻게 설계할지는 10.6절에서 다룬다.

---

## 6. grant_type: 무엇을 근거로 토큰을 받는가

### 6.1 grant_type은 왜 필요한가

grant_type은 **token 엔드포인트에 "무엇을 근거로 토큰을 달라는 것인지" 알리는 값**이다. RFC 6749는 grant 방식마다 이 파라미터를 필수(REQUIRED)로 정하고, OAuth 2.1 초안도 그대로 유지한다.

필요한 이유는 **token 엔드포인트가 하나뿐이기 때문**이다. 토큰을 받는 방식은 여러 가지인데 주소는 `/oauth/token/` 하나다. 요청마다 방식을 알려 줘야 인증 서버가 어떤 값을 확인하고 어떤 토큰을 줄지 정할 수 있다.

```
POST /oauth/token/
  grant_type = ?
      │
      ├─ authorization_code  → code, redirect_uri, code_verifier가 있는가?
      │                         code가 유효시간 안이고 처음 쓰는가? PKCE가 맞는가?
      │                         → 사용자 토큰 + refresh_token + id_token
      │
      ├─ refresh_token       → refresh_token이 유효한가? 이미 쓴 값은 아닌가?
      │                         → 새 토큰 세트
      │
      └─ client_credentials  → 클라이언트 인증만 확인
                                → 클라이언트 자신의 토큰 (refresh 없음)
```

grant_type이 없으면 인증 서버는 본문의 값들을 보고 방식을 추측해야 한다. 추측에 기대는 보안 규칙은 틀리기 쉬우므로, 표준이 이 값을 명시하도록 정했다.

grant_type은 두 가지 역할을 더 한다.

- **클라이언트별 허용 방식 제한**: 인증 서버는 등록 카드에 "이 클라이언트가 쓸 수 있는 grant_type"을 적어 둔다. 예를 들어 클라이언트 앱의 secret이 새더라도 IdP 인증 서버가 클라이언트 앱에 `client_credentials`를 허용하지 않았다면, 공격자는 사용자 로그인 없이 토큰을 받을 수 없다. 허용되지 않은 방식으로 요청하면 `unauthorized_client` 오류가 난다.
- **확장**: 새 발급 방식이 표준에 추가될 때도 grant_type 값을 하나 더 정의하는 식으로 늘어난다(6.7절).

### 6.2 세 가지 grant와 각각이 증명하는 것

grant_type 이름은 **"무엇을 근거로 내미는가"**를 가리킨다. 세 방식 모두 목적은 access token이다.

| grant_type | 이름이 가리키는 것 = 내미는 근거 | 클라이언트 증명 | 사용자 위임 증명 | 사용자가 지금 있나 | 결과 토큰의 권한 |
|---|---|---|---|---|---|
| `client_credentials` | 클라이언트 자격 증명 | ✅ id·secret | ❌ 위임 없음 | ❌ | 클라이언트 자신의 권한 |
| `authorization_code` | 로그인 직후 받은 code | ✅ id·secret | ✅ **방금** 로그인해서 받은 code | ✅ | 그 사용자 한 명의 권한 |
| `refresh_token` | 예전에 받은 refresh token | ✅ id·secret | ✅ **예전** 위임의 증서 | ❌ 없어도 됨 | 처음 위임받은 범위 이내 |

#### client_credentials: 서버 자신의 출입증

사용자가 전혀 끼지 않는 방식이다. 서버가 자기 client_id와 secret만 내밀고 토큰을 받는다.

```
IdP 서비스 서버 ── POST https://stg-partner.client.example/oauth/token
                 Authorization: Basic base64(idp:secret)
                 grant_type=client_credentials
              ◄── { "access_token": "eyJ…", "token_type": "Bearer", "expires_in": 1800 }
```

refresh_token이 없는 이유는 간단하다. refresh_token은 "사용자에게 다시 로그인시키지 않으려고" 있는 것인데, client_credentials에는 로그인할 사용자가 애초에 없다. 만료되면 secret으로 다시 받으면 된다. RFC 6749 4.4.3절도 이 응답에 refresh token을 넣지 않는 것을 원칙(SHOULD NOT)으로 정한다. 요청마다 새로 받지 말고, 만료 1~2분 전까지 메모리에 캐시해 재사용한다.

이 방식은 **confidential client만 쓸 수 있다(MUST).** RFC 6749 4.4절부터 있던 규칙이고 OAuth 2.1 초안도 그대로 유지한다. secret을 안전하게 보관할 수 없는 앱이 이 방식을 쓰면, 앱에서 꺼낸 secret 하나로 누구든 그 앱의 권한을 얻기 때문이다.

#### authorization_code: 사용자가 방금 위임한 권한

사용자가 로그인하고 받은 일회용 code를 내민다. 결과 토큰은 그 사용자의 권한을 담는다. 흐름 전체는 7장에서 따라간다.

#### refresh_token: 예전 위임을 이어 쓰기

refresh_token은 authorization_code 때 사용자가 한 위임을 **보관해 둔 증서**다. 사용자를 다시 로그인시키지 않고도 그 위임을 이어 쓰게 해 준다. 자세한 동작은 8.3~8.5절에서 다룬다.

### 6.3 grant_type별 파라미터와 응답

같은 `POST /oauth/token/`이지만 grant_type마다 함께 보내야 하는 파라미터와 돌아오는 응답이 다르다. 공통으로 들어가는 것은 grant_type과 클라이언트 인증(Basic 헤더)뿐이다.

| 파라미터 | `authorization_code` | `refresh_token` | `client_credentials` |
|---|---|---|---|
| `grant_type` | ✅ | ✅ | ✅ |
| 클라이언트 인증 (Basic 헤더) | ✅ | ✅ | ✅ |
| `code` | ✅ 로그인 후 받은 일회용 값 | | |
| `redirect_uri` | ✅ authorize 때와 같은 값 | | |
| `code_verifier` | ✅ PKCE 원본 값 | | |
| `refresh_token` | | ✅ | |
| `scope` | | 선택 (기존보다 좁힐 때만) | 선택 (생략하면 인증 서버의 기본값. 등록 범위 전부를 주는 서버가 많다) |

**요청 세 가지**

```http
# ① authorization_code: 클라이언트 앱 서버 → IdP 인증 서버, 계정 연결 시
POST /oauth/token/
Authorization: Basic base64(client_app_id:secret)

grant_type=authorization_code
&code=c-5d1e0b
&redirect_uri=https://stg-app.client.example/authorize/oauth2/code/idp
&code_verifier=dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk
```

```http
# ② refresh_token: 클라이언트 앱 서버 → IdP 인증 서버, access token 만료 시
POST /oauth/token/
Authorization: Basic base64(client_app_id:secret)

grant_type=refresh_token
&refresh_token=rt-9c2e…
```

```http
# ③ client_credentials: IdP 서비스 서버 → 클라이언트 앱 제휴사 API
POST /oauth/token
Authorization: Basic base64(idp:secret)

grant_type=client_credentials
```

**응답에 들어오는 것**

| 응답 필드 | ① authorization_code | ② refresh_token | ③ client_credentials |
|---|---|---|---|
| `access_token` | ✅ | ✅ 새 값 | ✅ |
| `refresh_token` | ✅ | ✅ 새 값 (IdP 인증 서버는 rotation) | ❌ |
| `id_token` | ✅ (`openid` scope라서) | ✅ (IdP 인증 서버의 동작. 표준상 선택) | ❌ |

①과 ②에는 사용자가 있으므로 id_token과 refresh_token이 나오고, ③에는 사용자가 없으므로 access token만 나온다. "사용자가 끼느냐"의 차이가 응답 모양에 그대로 드러난다.

### 6.4 오류 응답

인증 서버는 grant_type을 먼저 보고, 그 방식의 필수 파라미터가 다 있는지 검사한다.

| 상황 | 오류 |
|---|---|
| code_verifier를 빠뜨리거나 redirect_uri가 authorize 때와 다름 | `400 invalid_request` (IdP 인증 서버 기준. RFC 6749 5.2절은 redirect_uri 불일치를 `invalid_grant`로 정한다) |
| code가 유효시간을 넘겼거나 이미 씀, refresh_token이 만료됐거나 이미 씀 | `400 invalid_grant` |
| 이 클라이언트에 허용되지 않은 grant_type | `400 unauthorized_client` |
| 허용되지 않은 scope 요청 | `400 invalid_scope` |
| 클라이언트 인증 실패 (secret 오류, Basic이 아닌 방식) | `401 invalid_client` |

오류 코드는 인증 서버 구현마다 조금씩 다르다. 클라이언트는 오류 코드 하나에 기대어 분기하지 말고 `error_description`까지 로그로 남긴다.

`401 invalid_client`는 파라미터 문제가 아니라 **클라이언트 인증 단계**에서 실패했다는 뜻이다. 확인 순서는 이렇다.

1. 그 환경용 secret이 맞는지 (다른 환경 값과 섞이지 않았는지)
2. secret 앞뒤에 공백이나 줄바꿈이 붙지 않았는지 (메신저에서 복사할 때 흔하다)
3. Basic 헤더를 만들 때 id와 secret을 URL 인코딩했는지
4. Basic 헤더로 보냈는지 (본문으로 보내지 않았는지)

연결 시간 초과는 성격이 다르다. 인증 이전에 네트워크가 닿지 않은 것이므로 방화벽 허용부터 확인한다.

### 6.5 "파라미터가 많을수록 안전하다"는 오해

client_credentials → authorization_code로 갈수록 보내는 파라미터가 많아지니 보안이 강해진다고 생각하기 쉽다. **그렇지 않다. grant_type마다 증명하는 대상이 다르고, 파라미터가 많은 것은 그만큼 위험한 경로를 거치기 때문이다.**

```
client_credentials:
  서버 ──────────(TLS)──────────► 인증 서버
  통로가 서버 대 서버 하나뿐. 중간에 끼어들 곳이 없음

authorization_code:
  서버 → 브라우저 → 인증 서버 → 브라우저 → 서버 → 인증 서버
         ▲ 사용자 기기    ▲ 302로 code가 URL에 실림
         통제할 수 없는 구간이 여러 번 끼어 있음
```

authorization_code의 추가 파라미터는 **통제할 수 없는 구간에서 생기는 공격을 하나씩 막는 장치**다.

| 파라미터 | 막는 공격 | 자세히 |
|---|---|---|
| `redirect_uri` 대조 | code를 공격자 주소로 빼돌리기 | 4.4절 |
| `state` | 공격자의 로그인 결과를 피해자 세션에 끼워 넣기 (CSRF) | 7.2절 |
| `code_verifier` (PKCE) | URL에서 새어 나간 code를 공격자가 대신 교환하기 | 7.3절 |
| code의 짧은 수명·1회 사용 | 가로챈 code를 나중에 재사용하기 | 7.1절 |

client_credentials에는 이런 구간이 없으니 이 장치들도 필요 없다.

**오히려 반대인 경우**: 토큰이 샜을 때의 피해를 비교하면 순서가 뒤집힌다.

| 샌 것 | 공격자가 할 수 있는 것 |
|---|---|
| 클라이언트 앱이 가진 사용자 access token 1개 | **그 사용자 한 명**의 서비스 이용에 최대 60분 접근 |
| IdP 서비스 서버의 클라이언트 앱용 secret | 토큰을 마음대로 다시 받고, 사용자 지정 헤더만 바꿔 가며 **연결된 모든 사용자** 건으로 클라이언트 앱 API 호출 (16.8절) |

보안의 강도는 "어느 grant_type이 더 강한가"로 비교하지 않는다. **상황에 맞는 grant_type을 골랐는가, 그 방식의 약점을 막았는가**로 판단한다.

- **사용자를 대신해** 무언가를 하려면 authorization_code를 쓴다. 브라우저 구간의 공격은 PKCE·state·redirect_uri로 막는다.
- **서버 자신의 일**을 하려면 client_credentials를 쓴다. secret 관리, IP 제한, 좁은 scope로 막는다.

### 6.6 "client credentials"는 두 가지 뜻이다

같은 말이 두 가지 뜻으로 쓰여서 헷갈린다.

- **client credentials (일반 명사)**: 클라이언트를 식별하고 증명하는 자격 증명 자체. 곧 client_id와 client_secret의 묶음이다.
- **`client_credentials` (grant_type 값)**: 위 자격 증명**만** 내밀어서 토큰을 받는 발급 방식의 이름이다.

```
client credentials (자격 증명)  =  client_id  +  client_secret
        │
        │ 이 자격 증명은 모든 grant_type에서 "클라이언트 인증"에 쓰인다
        ▼
┌──────────────────────┬────────────────────────────────────────────────┐
│ grant_type           │ 토큰을 받기 위해 내미는 것                          │
├──────────────────────┼────────────────────────────────────────────────┤
│ authorization_code   │ client credentials  +  사용자가 로그인해서 받은 code │
│ refresh_token        │ client credentials  +  refresh_token            │
│ client_credentials   │ client credentials  만                          │
└──────────────────────┴────────────────────────────────────────────────┘
```

### 6.7 OAuth 2.1에서 남은 것과 사라진 것

| grant | OAuth 2.0 (RFC 6749) | OAuth 2.1 | 비고 |
|---|---|---|---|
| `authorization_code` | ✅ | ✅ **PKCE 필수** | 2.0에서는 PKCE가 별도 표준(RFC 7636)이었다 |
| `refresh_token` | ✅ | ✅ | public client는 rotation 또는 토큰을 발신자에 묶는 방식 필수 |
| `client_credentials` | ✅ | ✅ | |
| `password` | ✅ | ❌ **삭제** | 클라이언트가 사용자 비밀번호를 직접 받는 방식 |
| implicit (`response_type=token`) | ✅ | ❌ **삭제** | 토큰을 URL에 실어 바로 넘기는 방식. grant_type이 아니라 response_type으로 지정 |

**확장 grant**: 2.1도 "절대 URI 형태의 grant_type 값을 다른 표준에서 정의할 수 있다"는 규칙을 유지한다(RFC 6749 4.5절). 절대 URI가 꼭 https 주소일 필요는 없고, 아래처럼 `urn:` 형태가 흔하다.

| grant_type 값 | 표준 | 용도 |
|---|---|---|
| `urn:ietf:params:oauth:grant-type:device_code` | RFC 8628 | TV처럼 입력이 불편하거나 브라우저가 없는 기기 로그인 |
| `urn:ietf:params:oauth:grant-type:token-exchange` | RFC 8693 | 받은 토큰을 다른 대상용 토큰으로 교환 |
| `urn:ietf:params:oauth:grant-type:jwt-bearer` | RFC 7523 | 서명된 JWT를 근거로 토큰 발급 |
| `urn:openid:params:grant-type:ciba` | OpenID CIBA (Client-Initiated Backchannel Authentication) | 사용자 기기로 승인 요청을 보내는 분리형 인증 |

device_code, token-exchange, ciba가 어떻게 동작하는지는 14장(14.5, 14.6, 14.8)에서 그림과 함께 설명한다. `jwt-bearer` grant는 이 문서에서 따로 다루지 않는다. 14.7의 private_key_jwt도 RFC 7523을 쓰지만, 그것은 토큰을 받는 근거(grant)가 아니라 **클라이언트 인증** 방식이다. 값도 `urn:ietf:params:oauth:client-assertion-type:jwt-bearer`로 다르니, `grant-type`과 `client-assertion-type`을 구분해서 읽는다.

---

## 7. Authorization Code + PKCE 흐름 따라가기

사용자가 클라이언트 앱에서 IdP 서비스 계정을 연결하는 과정을 처음부터 끝까지 따라간다.

### 7.1 전체 시퀀스

```
클라이언트 앱 서버                         브라우저(웹뷰)                         IdP 인증 서버
   │ 0. discovery 문서를 읽어 주소·규칙을 알아 둠 (시작 시 1회, 캐시) ────────►│
   │                                                                    │
   │ 1. state·nonce·code_verifier 생성, 세션에 저장                        │
   │    code_challenge = BASE64URL(SHA256(code_verifier))                │
   ├──302──────────────►│                                               │
   │                    │ 2. GET /oauth/authorize/?                     │
   │                    │     response_type=code                        │
   │                    │     &client_id=…&redirect_uri=…               │
   │                    │     &scope=openid email                       │
   │                    │     &state=…&nonce=…                          │
   │                    │     &code_challenge=…&code_challenge_method=S256
   │                    ├──────────────────────────────────────────────►│
   │                    │ 3. 로그인 화면 (이미 로그인돼 있으면 생략)          │
   │                    │◄──────────────────────────────────────────────┤
   │                    │ 4. 사용자 로그인 ─────────────────────────────►│
   │                    │                                 5. code 발급,  │
   │                    │                                    code ↔ challenge 저장
   │                    │◄── 6. 302 redirect_uri?code=…&state=…&iss=… ──┤
   │◄───────────────────┤                                               │
   │ 7. callback 처리: state 대조 → error 확인 → iss 대조                    │
   │ 8. POST /oauth/token/                                               │
   │    grant_type=authorization_code, code, redirect_uri, code_verifier │
   │    Authorization: Basic …                                           │
   ├────────────────────────────────────────────────────────────────────►│
   │                                          9. verifier 해시 == challenge?
   │◄─── 10. access_token + refresh_token + id_token ────────────────────┤
   │ 11. id_token 검증(JWKS), nonce 대조, (iss, sub)로 회원 연결, 세션 생성   │
```

IdP 인증 서버가 정한 code 규칙: **60초 안에 한 번만** 쓸 수 있다. 표준(RFC 6749 4.1.2절)의 규칙은 셋으로 나뉜다.

| 누구에게 | 규칙 | 강도 |
|---|---|---|
| 인증 서버 | code는 발급 직후 곧 만료되게 한다. 최대 10분을 권장 | MUST / RECOMMENDED |
| 클라이언트 | 같은 code를 두 번 쓰지 않는다 | MUST NOT |
| 인증 서버 | 두 번째 사용은 거부하고, 가능하면 그 code로 이미 발급한 토큰까지 폐기한다 | MUST / SHOULD |

마지막 줄이 중요하다. code가 두 번 쓰였다는 것은 **누군가 가로챘다는 신호**이므로, 먼저 발급된 토큰도 공격자 손에 있을 수 있다고 보고 함께 무효로 만든다.

### 7.2 state: 로그인 요청과 응답을 짝짓는 번호표

**state는 클라이언트가 로그인 요청마다 새로 만드는 난수**다. authorize 요청에 실어 보내면 IdP 인증 서버가 결과와 함께 그대로 돌려주고, 클라이언트는 자기 세션에 저장한 값과 같은지 대조한다. OAuth 표준에서 state는 **클라이언트를 위한 값**이다. 인증 서버는 해석하지 않고 받은 그대로 돌려줄 의무만 있다.

#### 🛡️ 공격: 로그인 CSRF (공격자의 계정에 피해자를 로그인시키기)

**공격 원리**:

```
① 공격자가 자기 계정으로 로그인 흐름을 시작하고, 마지막 redirect 직전에 멈춘다
   → 손에 쥔 것: https://client.example…/callback?code=<공격자의 code>
② 이 URL을 링크 클릭이나 페이지 이동으로 피해자 브라우저가 열게 만든다
   (세션 쿠키가 SameSite=Lax면 이미지 같은 하위 요청에는 쿠키가 실리지 않으므로, 공격자는 최상위 이동을 쓴다)
③ state 검사가 없으면 클라이언트 앱 서버는 이 code를 피해자 세션에서 교환한다
④ 피해자는 자기도 모르게 "공격자의 IdP 서비스 계정"과 연결된다
⑤ 피해자가 서비스에 입력한 개인정보가 공격자 계정에 쌓인다
```

**방어**: 로그인을 시작할 때 state를 만들어 **피해자 자신의 세션**에 저장하고, callback에서 쿼리의 state와 세션의 state가 같은지 대조한다. 다르거나 세션에 없으면 400으로 끝낸다.

**방어 원리**: 공격자는 피해자의 세션에 무엇이 저장됐는지 알 수 없다. 공격자가 가진 callback URL에는 **공격자 세션의 state**가 들어 있으므로, 피해자 세션 값과 맞지 않아 거부된다. "이 응답은 내가 시작한 요청의 응답인가"를 확인하는 것이다.

**state를 만드는 법**: 암호학적 난수 16바이트 이상을 base64url로 인코딩한다(22자 이상. 예: Python `secrets.token_urlsafe(16)`). 로그인할 때마다 새로 만들고, 한 번 쓰면 버린다.

**흔한 착각**: state 파라미터를 넣기만 하면 안전하다고 생각하기 쉽다. RFC 6749 10.12절이 요구하는 것은 **사용자 브라우저의 세션에 묶인, 추측할 수 없는 값을 돌아온 뒤 대조하는 절차**다(클라이언트는 CSRF 방어를 반드시 구현해야 하고, 그 값을 실어 나르는 수단으로 state를 쓰는 것이 권장된다). 무작위 값을 보내 놓고 세션과 대조하지 않으면 아무것도 막지 못한다.

**OAuth 2.1 초안의 대안**: 인증 서버가 PKCE를 지원한다는 것을 확인한 클라이언트는 PKCE가 주는 CSRF 방어에 기대도 된다. OIDC 흐름에서는 nonce 검증(9.4절)도 CSRF 방어가 된다. 공격자의 code는 공격자 세션의 verifier·nonce와 묶여 있어서, 피해자 세션에서 교환하거나 검증하면 실패하기 때문이다. 그래도 state를 함께 쓰는 것이 가장 단순하고 확실하다.

### 7.3 PKCE: code를 가로채도 쓸 수 없게

**PKCE(Proof Key for Code Exchange, RFC 7636)는 authorize 요청을 보낸 바로 그 클라이언트만 code를 토큰으로 바꿀 수 있게 묶는 장치**다.

```
[1] 클라이언트가 비밀 원본을 만든다
      code_verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"   ← 아무에게도 안 보여 줌

[2] 해시해서 authorize 요청에 싣는다 (브라우저 URL에 노출돼도 됨)
      code_challenge = base64url(SHA256(code_verifier))
                     = "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
      code_challenge_method = S256
      → IdP 인증 서버가 이 code와 challenge를 짝지어 기억

[3] token 요청 때 원본을 보낸다 (서버 대 서버)
      code=…&code_verifier=dBjftJeZ…
      → IdP 인증 서버: SHA256(받은 verifier) == 기억한 challenge ? 토큰 발급 : invalid_grant
```

위 verifier와 challenge 값은 RFC 7636 부록 B의 공식 예시 짝이다. 직접 구현했다면 이 짝으로 검산할 수 있다.

#### 🛡️ 공격: authorization code 가로채기

**공격 원리**: code는 브라우저 URL로 오간다. 그래서 다음 경로로 샐 수 있다.

- 모바일에서 같은 custom scheme(`clientapp://…`)을 등록한 악성 앱이 redirect를 대신 받는다. OS가 URL을 보고 앱을 골라 넘겨주는 방식(Android의 intent 등)에서 생기는 일이다(12.4절).
- 프록시·서버 로그, 브라우저 히스토리에 URL이 남는다.

PKCE가 없으면 가로챈 code만으로 토큰 요청이 가능하다. public client(앱)라면 secret도 없으니 code 하나로 끝이다.

**방어**: code를 발급할 때 challenge를 함께 저장하고, 토큰 교환 때 원본 verifier를 요구한다.

**방어 원리**: 공격자는 code와 (URL에 노출된) challenge는 가질 수 있지만, **원본 verifier는 클라이언트(클라이언트 앱 서버)의 세션에만 있고, 브라우저 URL에는 실리지 않는다.** SHA-256은 해시값으로 원본을 거꾸로 계산할 수 없으므로(역상 저항성), challenge를 알아도 verifier를 만들 수 없다.

#### S256과 plain

| 방식 | challenge | 평가 |
|---|---|---|
| `S256` | SHA-256 해시 | 권장. URL에 challenge가 새도 verifier를 알 수 없다 |
| `plain` | verifier 그대로 | URL에 노출되면 그대로 verifier가 샌다. 해시 계산이 불가능한 환경용 예외 |

IdP 인증 서버는 S256만 허용한다. 없거나 S256이 아니면 `invalid_request`다.

#### ⚠️ 함정: `code_challenge_method`를 빠뜨리면 plain이 된다

RFC 7636 4.3절은 `code_challenge_method`를 생략하면 **기본값을 plain**으로 정한다. S256으로 해시한 challenge를 보내면서 method를 빠뜨리면, 서버는 그 해시값을 verifier 원본으로 취급한다. 그 뒤 token 요청에 진짜 verifier를 보내면 값이 맞지 않아 실패한다. 반대로 plain을 받아 주는 서버라면, URL에 노출된 challenge가 곧 verifier가 되어 PKCE가 무력해진다. **항상 `code_challenge_method=S256`을 함께 보낸다.**

**plain을 써도 되는 조건(RFC 7636)**: 기술적인 이유로 S256을 쓸 수 없고, 동시에 서버가 plain을 지원한다는 것을 별도 설정으로 알고 있을 때만이다. 또 S256을 시도했다가 plain으로 내려가는 것은 금지(MUST NOT)다. S256이 실패했다면 서버가 고장 났거나, 중간에서 누군가 방식을 낮추려는 공격(다운그레이드)을 하고 있다는 뜻이기 때문이다. **OAuth 2.1 초안은 plain을 아예 금지했다.**

#### 왜 SHA-256인가

PKCE가 해시에 요구하는 성질은 세 가지다.

| 성질 | 의미 | PKCE에서의 역할 |
|---|---|---|
| 역상 저항성 | 해시값만 보고 원본을 찾을 수 없음 | challenge가 새도 verifier를 알아낼 수 없음 |
| 제2 역상 저항성 | 같은 해시값을 내는 다른 원본을 만들 수 없음 | 다른 verifier로 같은 challenge를 맞출 수 없음 |
| 결정성 | 같은 입력이면 항상 같은 출력 | IdP 인증 서버가 나중에 받은 verifier를 해시해 대조할 수 있음 |

| 다른 후보 | 쓰지 않는 이유 |
|---|---|
| MD5, SHA-1 | 충돌 저항성이 깨져 새 보안 설계에서는 쓰지 않는다. PKCE가 기대는 역상 저항성이 당장 깨진 것은 아니지만, 약점이 드러난 해시를 새 표준에 넣을 이유가 없다 |
| SHA-512, SHA3 | 안전하지만 과하다. 256비트로 충분하고, 방식이 하나로 고정돼야 서로 다른 구현이 맞물린다 |
| bcrypt, Argon2 (일부러 느린 해시) | **필요 없다.** 사람이 고른 비밀번호는 경우의 수가 적어 하나씩 넣어 보는 공격(무차별 대입)이 통하므로 느린 해시가 필요하다. verifier는 32바이트 암호학적 난수라 경우의 수가 2^256이고, 수십 초만 쓰고 버린다 |

그 밖에 모든 언어의 표준 라이브러리와 브라우저(Web Crypto), 모바일 OS에 내장돼 있고, 32바이트를 base64url로 바꾸면 43자라 URL에 넣기 알맞다. id_token 서명 방식 RS256도 "RSA 서명 + SHA-256"이라 한 연동 안에서 해시가 통일된다.

#### secret이 있는데 왜 PKCE가 또 필요한가

원래 PKCE는 secret을 보관할 수 없는 모바일 앱(public client)을 위해 만들었다. 그런데 secret이 있는 서버 클라이언트에서도 둘은 막는 것이 다르다. **secret은 "이 클라이언트가 맞다"를, PKCE는 "이 로그인 요청을 시작한 바로 그 세션이 맞다"를 증명한다.**

예를 들어 공격자가 다른 경로로 피해자의 code를 얻어, **공격자 자신의 브라우저 세션**으로 정상 클라이언트의 callback에 그 code를 넣는다고 하자. 정상 클라이언트는 자기 secret으로 토큰을 받아 주므로 secret은 이 공격을 막지 못한다. PKCE가 있으면 공격자 세션에 저장된 verifier가 그 code의 challenge와 맞지 않아 실패한다. 이 공격을 **authorization code injection**이라고 부른다.

그래서 OAuth 2.1 초안은 authorization code 흐름에서 PKCE를 필수로 한다. 예외는 하나뿐이고 두 조건을 **모두** 만족해야 한다. 클라이언트가 confidential client이고, 인증 서버가 그 클라이언트가 OIDC nonce를 올바로 구현했다고 합리적으로 확신할 수 있을 때다. 그 경우에도 PKCE를 쓰는 것이 권장된다. IdP 인증 서버는 예외 없이 클라이언트 앱 서버에 S256을 필수로 걸어 두었다.

#### code_verifier 만드는 법

| 값 | 만드는 법 | 쓰는 곳 |
|---|---|---|
| state | 난수 16바이트 이상을 base64url 인코딩 (22자 이상) | authorize에 보내고, callback에서 세션 값과 비교 |
| nonce | state와 같은 방법으로 별도 값 | authorize에 보내고, id_token의 nonce와 비교 (9.4절) |
| code_verifier | 난수 32바이트를 base64url 인코딩하고 끝의 `=` 제거 → 43자. 허용 문자 영문·숫자·`-._~`, 길이 43~128자 | 세션에 보관했다가 토큰 요청에 보냄 |
| code_challenge | base64url(SHA-256(code_verifier)), 끝의 `=` 제거 → 43자 | authorize에 `code_challenge_method=S256`과 함께 |

셋 다 **암호학적 난수 생성기**로 만들고, 한 번 쓰면 버린다. 대부분의 OIDC 라이브러리가 만들고 저장하고 비교하는 것까지 대신해 준다.

### 7.4 302 redirect는 왜 등장하나

흐름 그림의 6번에서 IdP 인증 서버가 갑자기 redirect를 보내는 것처럼 보이지만, 실제로는 **사용자가 로그인 버튼을 누른 그 요청에 대한 응답**이다.

```
브라우저(웹뷰)                      IdP 인증 서버 (와 내부 서비스)
  │ POST /login (이메일·비밀번호) ────►│
  │                                   │ 비밀번호 확인 → 회원 12345
  │      (브라우저는 응답을 기다리는 중)   │ (필요하면 서버끼리 추가 처리)
  │                                   │ 일회용 code 발급, code ↔ (12345, challenge) 저장
  │◄── 302 Location: https://…/callback?code=c-5d1e&state=st-8f2c&iss=… ──┤
  │ 브라우저가 Location을 따라 클라이언트로 이동
```

authorize는 처음부터 **브라우저가 페이지를 이동하는 방식**으로 시작됐다. 클라이언트 서버가 IdP 인증 서버 API를 호출한 것이 아니라, 사용자의 브라우저를 IdP 인증 서버 페이지로 보낸 것이다. 그러니 끝날 때도 **사용자의 브라우저를 다시 클라이언트로 보내야** 흐름이 닫힌다.

```
② 클라이언트 → 브라우저: "IdP 인증 서버로 가라"   (302)      ← 열기
⑥ IdP 인증 서버 → 브라우저: "클라이언트로 돌아가라" (302)    ← 닫기, 결과(code)를 실어서
```

### 7.5 callback 처리 순서

브라우저가 IdP 인증 서버에서 돌아올 때 클라이언트 서버가 실행하는 핸들러다. **보안 검사가 모두 여기에 있으므로 순서를 지킨다.**

| 순서 | 할 일 | 실패하면 |
|---|---|---|
| 1 | 세션에 저장해 둔 state를 꺼내고 지운다 | 없으면 진행 중인 로그인이 없는 것 → 400 |
| 2 | 쿼리의 state가 세션 값과 같은지 본다 | 다르면 400 |
| 3 | 쿼리에 `error`가 있으면 여기서 끝낸다. RFC 9207은 오류 응답에도 iss를 넣으라고 하지만 IdP 인증 서버는 일부 오류 응답에서 iss를 빼므로, 이 단계에서는 iss를 보지 않는다. 오류가 정말 그 인증 서버에서 왔다고 가정할 수 없으니 오류 내용을 화면에 그대로 믿고 쓰지 않는다 | 사용자에게 다시 로그인 안내 |
| 4 | 쿼리의 `iss`가 issuer와 같은지 본다. 성공 응답에는 항상 들어 있다 | 없거나 다르면 400 |
| 5 | 백엔드에서 token 주소로 code와 code_verifier를 보낸다 (Basic 인증) | 오류 코드는 6.4절 |
| 6 | 받은 id_token을 검증한다: JWKS 공개키로 서명, iss·aud(자기 client_id)·exp·nonce 비교 | 400 |
| 7 | (iss, sub)로 회원을 찾거나 새로 만든다. sub는 문자열 그대로 | — |
| 8 | 로그인 세션을 새로 만든다. 로그인 전에 쓰던 세션 ID는 버리고 다시 발급한다 | — |

4번의 `iss` 검사는 응답이 **로그인 요청을 보낸 바로 그 인증 서버에서 왔는지** 확인하는 것이다(RFC 9207). 클라이언트가 인증 서버를 둘 이상 쓸 때(예: 카카오와 IdP 서비스 로그인을 모두 지원), 공격자가 한 서버의 응답을 다른 서버의 것으로 착각하게 만드는 **mix-up 공격**을 막는다. RFC 9207을 지원하는 클라이언트는 응답에 iss가 있으면 반드시 비교하고, 지원한다고 알려진 서버의 응답에 iss가 없으면 거부해야 한다. OAuth 2.1 초안은 인가 응답의 iss를 필수로 바꿨다.

8번은 로그인 전 세션 ID를 공격자가 미리 심어 두는 공격(세션 고정)을 막는다. 4번(iss 대조)은 아래 예제의 authlib를 포함해 많은 라이브러리가 검사하지 않으므로 직접 넣는다. 3번은 authlib도 예외로 처리하지만 state 확인보다 먼저 하므로, 위 순서를 지키려고 직접 넣었다.

**세션 쿠키의 SameSite 주의**: callback은 IdP 인증 서버에서 클라이언트로 돌아오는 **다른 사이트 간 이동**이다. 로그인 진행에 쓰는 세션 쿠키를 `SameSite=Strict`로 두면 이 이동에 쿠키가 실리지 않아 state를 대조할 수 없다. 그래서 이 쿠키는 `SameSite=Lax`로 둔다(결과를 URL 쿼리로 받을 때. form_post로 받는다면 7.7절).

**받은 값은 모두 외부 입력이다**: OAuth 2.1 초안 7.12절은 인증 서버와 클라이언트가 받은 파라미터(특히 access token, state, redirect_uri)를 **악의적일 수 있는 외부 입력**으로 다루라고 정한다(MUST). 예를 들어 state에 "로그인 후 돌아갈 주소"를 담고 callback에서 그 주소로 그대로 이동시키면, 클라이언트가 open redirector(15.4.2)가 된다. 돌아갈 주소는 허용 목록과 대조한 뒤에만 쓴다.

**오류일 때 돌아오는 주소의 두 모양**

```
# 요청값이 틀린 경우. IdP 인증 서버는 iss를 넣지 않는다 (RFC 9207은 오류 응답에도 iss를 요구).
https://…/callback?error=invalid_scope&state=st-8f2c1a

# 인증 서버가 로그인을 끝내지 못한 경우. iss가 있다.
https://…/callback?error=access_denied&state=st-8f2c1a&iss=https%3A%2F%2Fauth.stg.idp.example
```

단, client_id나 redirect_uri가 틀린 요청은 callback으로 돌아오지 않는다(7.6절).

**참고: Python으로 쓴 callback 골격** (authlib 사용, 위 순서 번호와 대응)

```python
@app.get("/oauth/callback")
async def callback(request: Request):
    q = request.query_params
    state = q.get("state", "")
    state_key = f"_state_idp_{state}"           # authlib가 세션에 저장하는 키

    # 1·2 세션의 state와 비교
    if not state or state_key not in request.session:
        return error_page("state 불일치", 400)

    # 3 error면 종료 (iss는 보지 않음)
    if "error" in q:
        request.session.pop(state_key, None)
        return error_page(f"로그인 실패: {q['error']}")

    # 4 iss 비교
    if q.get("iss") != ISSUER:
        request.session.pop(state_key, None)
        return error_page("iss 불일치", 400)

    # 5·6 토큰 요청(Basic) + id_token 검증(서명·iss·aud·exp·nonce)은 authlib가 처리
    metadata = await oauth.idp.load_server_metadata()
    metadata["id_token_signing_alg_values_supported"] = ["RS256"]   # RS256만 허용
    token = await oauth.idp.authorize_access_token(request)
    claims = dict(token["userinfo"])                 # 검증을 마친 id_token 본문

    # 7 (iss, sub)로 회원 연결
    member = find_or_create_member(claims["iss"], str(claims["sub"]))

    # 8 로그인 전 세션 내용 폐기 (Starlette 세션은 서명 쿠키라 별도 세션 ID가 없다)
    request.session.clear()
    request.session["member"] = member
    return RedirectResponse("/", status_code=302)
```

서버에 세션을 저장하는 프레임워크에서는 내용 비우기(`clear`)만으로는 세션 ID가 그대로 남는다. 세션 고정을 막으려면 ID를 새로 만드는 함수(Django `request.session.cycle_key()`, Express `req.session.regenerate()`)를 쓴다.

### 7.6 authorize 단계의 오류 응답

authorize 단계의 오류는 **돌려보내도 안전한지**에 따라 두 갈래로 처리된다.

```
authorize 요청 도착
  │
  ├─ client_id가 없거나 틀림, 또는 redirect_uri가 등록값과 다름
  │    → 인증 서버 자기 화면에 오류 표시. 리다이렉트하지 않는다 (MUST NOT)
  │      (검증되지 않은 주소로 보내면 open redirector가 된다, 15.4.2)
  │
  └─ 그 밖의 오류
       → 등록된 redirect_uri로 302
         ?error=…&error_description=…&state=<보낸 값>&iss=…
```

**OAuth 오류 코드** (RFC 6749 4.1.2.1)

| error | 뜻 | 클라이언트가 할 일 |
|---|---|---|
| `invalid_request` | 필수 파라미터 누락, 중복, 형식 오류 (PKCE 누락도 여기) | 구현 버그. 로그 남기고 수정 |
| `unauthorized_client` | 이 클라이언트는 이 방식으로 요청할 수 없음 | 등록 설정 확인 |
| `access_denied` | 사용자가 거부했거나 인증 서버가 거절 | 사용자에게 다시 시도 안내 |
| `unsupported_response_type` | 지원하지 않는 response_type | 설정 확인 |
| `invalid_scope` | 잘못되었거나 허용되지 않은 scope | 요청 scope 확인 |
| `server_error` | 인증 서버 내부 오류 | 잠시 뒤 재시도 |
| `temporarily_unavailable` | 과부하·점검 | 잠시 뒤 재시도 |

**OIDC가 더하는 오류** (OIDC Core 3.1.2.6, 주요한 것만). 넷 다 주로 `prompt=none`(9.12절)으로 화면 없이 요청했는데 화면이 필요할 때 온다. 받으면 `prompt=none` 없이 다시 요청한다.

| error | 뜻 |
|---|---|
| `login_required` | 로그인 화면이 필요함 |
| `interaction_required` | 로그인 외의 사용자 상호작용이 필요함 |
| `consent_required` | 동의 화면이 필요함 |
| `account_selection_required` | 계정 선택 화면이 필요함 |

7.5절 callback 처리의 3번이 받는 오류가 이것이다. token 엔드포인트의 오류는 6.4절에 있다. 두 엔드포인트의 차이는 **전달 방식**이다. authorize 오류는 브라우저 리다이렉트로, token 오류는 HTTP 응답 본문(JSON)으로 온다.

### 7.7 결과를 돌려받는 방식: response_type과 response_mode

지금까지 따라간 흐름은 code를 **URL 쿼리**로 돌려받았다. authorize 요청에는 결과를 **무엇으로**, **어떻게** 돌려받을지 정하는 파라미터가 둘 있다. OAuth 2.1 본문이 정의하는 값은 `code` 하나뿐이다(다른 표준이 정의하는 확장 값은 허용된다). 나머지는 옛 코드나 OIDC 제공자 문서를 읽을 때 알아보는 용도로 보면 된다.

**response_type: 무엇을 받나**

| 값 | 받는 것 | 상태 |
|---|---|---|
| `code` | authorization code | ✅ 표준. OAuth 2.1 본문이 정의하는 유일한 값 |
| `token` | access token (implicit) | ❌ OAuth 2.1에서 삭제 (15.12) |
| `id_token` | id_token만 (OIDC implicit) | ⚠️ OIDC 정의. 토큰을 URL로 받는 계열 |
| `code id_token` 등 | code와 id_token을 함께 (OIDC hybrid) | ⚠️ OIDC가 정의한 확장. 특수 용도 |

**response_mode: 어떻게 돌려받나**

```
[query]      302 Location: https://client.example/cb?code=…&state=…        ← code 흐름의 기본값
[fragment]   302 Location: https://client.example/cb#access_token=…        ← implicit의 기본값
                         (# 뒤는 서버로 전송되지 않고 브라우저 JS만 읽음)
[form_post]  200 OK + 자동 제출 HTML 폼
             <form method="post" action="https://client.example/cb">
               <input type="hidden" name="code" value="…">
               <input type="hidden" name="state" value="…">
             </form><script>document.forms[0].submit()</script>
             → 결과가 URL이 아니라 POST 본문으로 감
```

`form_post`(OAuth 2.0 Form Post Response Mode)는 code가 **URL에 남지 않게** 해서 브라우저 히스토리·Referer 유출(15.4.3, 15.4.4)을 줄인다. 대신 주의할 점이 있다. 인증 서버 도메인에서 클라이언트로 **다른 사이트 간 POST**가 일어나므로, 클라이언트 세션 쿠키가 `SameSite=Lax`이면 이 POST에 쿠키가 실리지 않는다. 그러면 콜백에서 state를 세션과 대조할 수 없다. form_post를 쓴다면 state·nonce·code_verifier를 담는 **로그인 진행용 쿠키만** 따로 두고 `SameSite=None; Secure; HttpOnly`로 설정한다. 이 쿠키는 다른 사이트에서 온 POST에도 실린다. 그래도 공격자는 쿠키 안의 state 값을 모르므로 7.2절의 대조가 그대로 CSRF를 막는다. 수명은 몇 분으로 짧게 두고 callback 처리 직후 지운다. 로그인 뒤의 일반 세션 쿠키는 Lax(또는 Strict)를 유지한다.

### 7.8 동의(consent) 화면

로그인 다음에 인증 서버가 보여 주는 "이 앱이 다음 권한을 요청합니다" 화면이 동의 화면이다. OAuth에서 **사용자가 권한을 위임하는 순간**이 바로 이 화면이다.

```
┌────────────────────────────────────────────┐
│  [로고] Example Tax Helper                   │  ← 클라이언트 이름·로고 (등록 정보)
│  등록 조직: Example Inc. (확인됨)              │  ← 누가 만든 앱인지
│  helper.example.com 으로 돌아갑니다            │  ← 어디로 돌아가는지
│                                            │
│  다음 권한을 허용하시겠습니까?                   │
│   ✓ 이메일 주소 보기          (email)          │  ← scope를 사람의 말로
│   ✓ 서비스 이용 내역 읽기            (service:read)   │
│   ✓ 오프라인 접근 유지         (offline_access) │  ← refresh token, 기간 표시
│                                            │
│  로그인 계정: user@example.com  [계정 변경]     │
│                                            │
│        [ 거부 ]              [ 허용 ]          │  ← 거부하면 error=access_denied
└────────────────────────────────────────────┘
```

OAuth 2.1 초안은 동의 화면에 **클라이언트가 누구인지, 어떤 scope를 얼마 동안 요청하는지**를 보여 주라고 권한다(초안 7.3절·7.9절, SHOULD).

- **같은 회사의 앱(first-party)**은 동의 화면을 생략하는 경우가 많다. "내 서비스가 내 서비스에 권한을 달라"는 것이라 의미가 적기 때문이다.
- 한 번 동의하면 인증 서버가 기억해서 다음부터 묻지 않는 구현이 흔하다. 다시 묻게 하려면 OIDC의 `prompt=consent`를 붙인다(9.12절). 순수 OAuth에는 이런 표준 파라미터가 없다.
- 이 연동 사례에서는 동의가 두 곳에서 나뉜다. 클라이언트 앱 화면의 "클라이언트 앱 → IdP 서비스 제3자 제공 동의"와, IdP 서비스 화면의 약관·개인정보 동의다(16.4절).

#### ⚠️ 함정: 기억한 동의로 자동 승인할 때

"한 번 동의했으면 다음부터 화면 없이 통과"는 편하지만 조건이 있다. **public client는 client_id만으로 누구인지 증명할 수 없다.** 그래도 code는 등록된 redirect_uri로만 가므로(4.2절), 가짜 앱이 같은 client_id로 요청하는 것만으로는 code를 받지 못한다. 문제는 **가짜 앱이 그 redirect_uri로 오는 결과를 가로챌 수 있을 때**다. 예를 들어 네이티브 앱이 custom scheme(`com.example.app:/cb`)을 쓰면, 같은 scheme을 등록한 악성 앱이 결과를 받을 수 있다(12.4절). 이때 인증 서버가 기억한 동의로 화면 없이 code를 내주면, 사용자는 아무것도 보지 못한 채 악성 앱이 토큰을 얻는다. 이 경우 PKCE도 막지 못한다. 악성 앱이 흐름을 처음부터 직접 시작했으므로 verifier도 악성 앱의 것이기 때문이다. 동의 화면을 다시 띄우면 적어도 사용자가 "내가 지금 이 앱에 로그인하려는 것이 맞나"를 판단할 기회가 생긴다.

그래서 OAuth 2.1 초안 7.3절은 인증 서버가 **클라이언트를 인증하지 않았거나 같은 클라이언트라는 다른 보장이 없으면, 반복된 요청을 사용자 상호작용 없이 자동 처리하지 말라**고 한다(SHOULD NOT). 네이티브 앱이라면 이전에 같은 client_id를 승인했더라도 처음 요청처럼 다루는 것이 권장된다(초안 7.3.1절, SHOULD). 반대로 https 앱 링크처럼 OS가 앱의 신원을 보장하는 redirect는 신원 증명으로 받아들여도 된다(RFC 8252 8.6절, MAY).

#### 🛡️ 공격: 동의 피싱 (consent phishing)

🎯 **노리는 것**: 비밀번호를 훔치지 않고, 사용자가 **스스로** 공격자 앱에 넓은 권한을 주게 만드는 것.

🧨 **공격 원리**

```
① 공격자가 인증 서버에 그럴듯한 이름으로 클라이언트를 등록 ("보안 업데이트 도우미")
② 피해자의 자원을 노린 scope로 authorize URL을 만들어 피싱 메시지로 보냄
③ 피해자는 진짜 로그인 화면에서 진짜 비밀번호와 2단계 인증으로 로그인
④ 동의 화면에서 "메일 읽기, 오프라인 접근"을 허용
⑤ 공격자 앱이 정상 흐름으로 토큰을 받음. 비밀번호는 한 번도 공격자에게 가지 않음
```

OAuth 2.1 초안 7.9절은 이 공격을 직접 다루며, **피싱에 강한 인증 수단(패스키 같은 것)도 동의 피싱은 막지 못한다**고 강조한다. 사용자가 **진짜로** 로그인하고 **진짜로** 동의했기 때문이다. "진짜 도메인이면 안전하다"는 직관이 여기서 깨진다.

🛡️ **방어**

| 누가 | 무엇을 |
|---|---|
| 인증 서버 | 동의 화면에 클라이언트 이름, 등록한 조직, 요청 scope를 분명히 표시 (SHOULD). 검증되지 않은 앱 경고 |
| 인증 서버 | 위험한 scope는 관리자가 승인한 앱만 요청 가능하게 제한 |
| 인증 서버 | 신뢰하지 않는 redirect URI로는 자동 이동하지 않음 (15.4.2) |
| 인증 서버 | 사용자와 관리자가 **연결된 앱 목록을 보고 권한을 철회**할 수 있게 함 (SHOULD, 8.8절) |

💡 **방어 원리**: 패스키처럼 **도메인에 묶인 인증**은 "가짜 도메인의 화면"을 걸러 내는 장치다. 동의 피싱은 진짜 도메인의 진짜 화면에서 진짜 동의를 받으므로 이 방어가 통하지 않는다. 그래서 방어는 **동의하는 순간에 클라이언트를 믿을 만한지 판단할 정보**를 사용자에게 주고, **나중에 철회할 수단**을 두는 쪽으로 간다.

#### 🛡️ 공격: 클릭재킹 (clickjacking)

**공격 원리**: 공격자 페이지가 투명한 iframe으로 로그인·동의 화면을 겹쳐 놓고, 그 위에 "경품 받기" 같은 버튼을 그린다. 사용자는 경품 버튼을 누른다고 생각하지만 실제로는 아래에 깔린 동의 버튼을 누른다.

```
사용자 눈에 보이는 화면              실제 겹쳐 있는 구조
┌────────────────────┐          ┌────────────────────┐ ← 공격자 페이지
│   🎁 경품 받기       │          │   🎁 경품 받기       │
│   [ 클릭하세요 ]     │          │ ┌────────────────┐ │
│                    │          │ │ [동의하고 연결] │ │ ← 투명한 iframe (opacity:0)
└────────────────────┘          │ └────────────────┘ │    버튼 위치를 맞춰 둠
                                └────────────────────┘
```

**방어**: 인증 서버가 응답 헤더 `Content-Security-Policy: frame-ancestors 'none'`(또는 옛 방식의 `X-Frame-Options: DENY`)를 보내 프레임 삽입 자체를 막는다.

**방어 원리**: 브라우저가 "이 페이지는 다른 페이지 안에 들어갈 수 없다"는 지시를 지키므로, 공격자는 로그인 화면을 자기 페이지 안에 겹쳐 놓을 수 없다.

RFC 9700은 인증 서버의 클릭재킹 방지를 MUST로, CSP 레벨 2 이상 사용을 SHOULD로 정한다. 로그인·동의 화면뿐 아니라 오류 화면처럼 사용자를 인증·인가하는 모든 화면에 건다.

---

## 8. 토큰: access·refresh·id

### 8.1 세 토큰은 같은 응답에 함께 오지만 독자가 다르다

id_token, access token, refresh token은 모두 **`POST /oauth/token/`의 응답 한 번에 함께** 들어온다.

```json
{
  "access_token":  "at-5f1c…",        ← API 호출용 (IdP 인증 서버: 60분)
  "token_type":    "Bearer",
  "expires_in":    3600,
  "refresh_token": "rt-9c2e…",        ← 갱신용 (IdP 인증 서버: 마지막 사용 후 14일)
  "scope":         "openid email",
  "id_token":      "eyJhbGciOiJSUzI1NiIs…"   ← 신원 확인용
}
```

| 토큰 | 누가 읽나 | 언제 쓰나 | 비유 |
|---|---|---|---|
| `id_token` | **클라이언트(클라이언트 앱 서버)가 직접** 검증하고 읽음 | 받자마자 한 번. 서명·nonce 검증 후 `sub`로 회원 연결 | 신분증 사본 |
| `access_token` | **리소스 서버(IdP 서비스 API)**가 검증 | API를 호출할 때마다 `Authorization: Bearer`로 제시 | 출입증 |
| `refresh_token` | **인증 서버**만 읽음 | access token이 만료되면 제시 | 출입증 재발급 신청서 |

**authorize 단계에서 토큰을 받지 않는 이유**: authorize는 브라우저 URL로 결과를 돌려주므로 일회용 code만 싣는다. 토큰을 URL로 받던 implicit 방식은 URL이 로그와 히스토리에 남기 쉬워서 OAuth 2.1에서 삭제됐다. 지금은 **모든 토큰을 token 엔드포인트에서 서버끼리 받는 것**이 표준 흐름이다.

### 8.2 유효 시간은 누가 정하나

**access token의 유효 시간은 grant_type이 정하는 것이 아니라, 토큰을 발급하는 인증 서버가 자기 정책으로 정한다.** OAuth 표준은 시간을 정하지 않는다. 응답에 `expires_in`(초)을 담아 "몇 초 뒤 만료된다"를 알려 주라고만 정한다.

```
① authorization_code  ── 발급자: IdP 인증 서버              → access 60분
② refresh_token       ── 발급자: IdP 인증 서버              → access 60분
③ client_credentials  ── 발급자: 클라이언트 앱 제휴사 API    → access 30분
```

60분과 30분이 다른 이유는 grant_type이 달라서가 아니라 **발급한 서버가 달라서**다.

| 짧게 하면 | 길게 하면 |
|---|---|
| 토큰이 새도 피해 시간이 짧다 | 토큰이 새면 오래 악용된다 |
| 자주 다시 받아야 해서 인증 서버 부하가 늘어난다 | 재발급이 드물어 부하가 줄어든다 |

균형점을 정하는 핵심 기준은 **"어떻게 다시 받을 수 있느냐"**다.

- **클라이언트 앱이 30분으로 짧게 둔 것은 다시 받기가 쉬워서다.** client_credentials는 secret만 있으면 언제든 새 토큰을 받을 수 있다.
- **IdP 인증 서버가 60분 + refresh 14일인 것은 사용자가 끼기 때문이다.** 사용자가 끼는 토큰은 만료될 때마다 다시 로그인시킬 수 없으니, access는 적당히 짧게 두고 refresh token으로 다시 받는 길을 열어 준다.

### 8.3 refresh_token grant: 근거와 목적

`grant_type=refresh_token`은 **"refresh token을 내밀어서 새 access token을 받는" 방식**이다. 이름의 refresh_token은 **내미는 근거**를 가리킨다. 받으려는 대상이 refresh token이라는 뜻이 아니다.

```
POST /oauth/token/
  grant_type=refresh_token
  refresh_token=rt-AAA          ← 내미는 것 (근거)
        │
        ▼
  응답
    access_token=at-새값         ← 받으려는 것 (목적)
    refresh_token=rt-BBB         ← rotation 정책일 때만 새로 나옴
    id_token=…                   ← 인증 서버에 따라 다름 (IdP 인증 서버는 줌)
```

### 8.4 refresh token rotation과 탈취 탐지

| | rotation 없음 | rotation 있음 (IdP 인증 서버의 설정) |
|---|---|---|
| 갱신 응답 | 새 access token만 | 새 access token + **새 refresh token** |
| 이전 refresh token | 만료 전까지 계속 쓸 수 있음 | **즉시 무효.** 다시 쓰면 `invalid_grant` |
| 클라이언트가 할 일 | 처음 받은 값을 계속 보관 | 갱신할 때마다 새 값으로 **바꿔 저장** |

```
계정 연결     → at-1(60분) + rt-A(14일)
60분 후 갱신  → rt-A 제출 → at-2 + rt-B    (rt-A는 이제 무효)
60분 후 갱신  → rt-B 제출 → at-3 + rt-C    (rt-B는 이제 무효)
…
14일간 갱신 없음 → 마지막 rt 만료 → 계정 연결부터 다시
```

"마지막 사용 후 14일"이라는 규칙도 rotation 덕분에 성립한다. 사용자가 꾸준히 쓰면 연결이 계속 유지된다.

**표준의 규칙**: RFC 6749 6절은 인증 서버가 갱신 때 새 refresh token을 줄 수 있고(MAY), 그러면 클라이언트는 옛 값을 버리고 새 값으로 바꿔야 한다(MUST)고 정한다. OAuth 2.1 초안은 한 걸음 더 나간다. **public client의 refresh token은 rotation을 하거나, 토큰을 특정 클라이언트 인스턴스에 암호학적으로 묶어야(sender-constrained) 한다.** 앱 안에 저장된 refresh token은 서버에 저장된 것보다 훔치기 쉽기 때문이다.

#### 🛡️ 공격: refresh token 탈취 후 재사용

**공격 원리**: refresh token은 수명이 길다. 공격자가 하나를 훔치면, 사용자가 다시 로그인하지 않아도 계속 새 access token을 받을 수 있다.

**방어**: rotation. 갱신할 때마다 새 refresh token을 주고, 이전 값은 무효로 만든다.

**방어 원리**: 정상 클라이언트와 공격자가 **같은 refresh token**을 갖게 되므로, 둘 중 하나가 먼저 쓰면 다른 쪽이 쓸 때 "이미 쓴 값"이 된다. 인증 서버는 이 재사용을 보고 탈취를 알아챈다.

```
공격자가 rt-B를 훔침
  ├─ 공격자가 먼저 갱신 → rt-B 소모, 공격자가 rt-C를 받음
  └─ 정상 클라이언트 앱 서버가 rt-B로 갱신 → 이미 쓴 값이라 invalid_grant
        → 인증 서버는 "같은 rt가 두 번 쓰였다 = 탈취"로 판단하고
          그 연결의 토큰 전체를 무효화할 수 있다
```

**같은 이유로 생기는 운영상 주의점**: 클라이언트 서버가 실수로 **같은 refresh token으로 갱신을 동시에 두 번** 보내면, 공격이 아닌데도 한쪽이 `invalid_grant`를 받는다. 인증 서버가 재사용 감지 시 토큰 전체를 무효화하도록 구현돼 있다면 사용자 연결까지 끊긴다. 그래서 **같은 사용자의 갱신 요청은 한 번에 하나씩** 보내도록 클라이언트에서 직렬화한다.

### 8.5 refresh token이 증명하는 것과 증명하지 못하는 것

`grant_type=refresh_token`이 증명하는 것은 **"나는 이 클라이언트이고, 이 사용자가 예전에 나에게 위임한 권한이 아직 살아 있다"**다. 사용자가 **지금** 그 자리에 있다는 것은 증명하지 않는다.

```
[처음] 사용자 로그인 → code → authorization_code 교환
         → "이 사용자가 클라이언트 앱에 위임함"을 IdP 인증 서버가 기록
         → 그 기록을 가리키는 증서 = refresh token

[이후] 클라이언트 앱 서버 혼자서 refresh token 제출
         → IdP 인증 서버: "이 증서의 위임이 아직 유효한가?" 확인
         → 새 access token
```

**IdP 인증 서버가 갱신 요청에서 확인하는 것**

1. **클라이언트 인증**: Basic 헤더의 client_id·secret이 맞는가
2. **증서의 주인**: 이 refresh token이 **바로 그 클라이언트에게** 발급된 것인가. 클라이언트 앱에 발급된 refresh token을 다른 클라이언트가 내밀면 거부한다
3. **증서의 상태**: 14일 안인가, 이미 쓴 값은 아닌가, 사용자가 연결을 해제하지 않았는가
4. **권한 범위**: 요청한 scope가 처음 위임받은 범위를 넘지 않는가. 줄이는 것은 되지만 늘릴 수는 없다. scope를 생략하면 처음 위임받은 범위로 간주한다(RFC 6749 6절)

2번 덕분에 **refresh token만 훔쳐서는 쓸 수 없고, 그 클라이언트의 secret까지 있어야 한다.** confidential client의 refresh token은 사용자 기기에 저장되는 refresh token보다 탈취 위험이 훨씬 낮다.

**"사용자가 지금 있지 않다"가 뜻하는 것**: refresh token으로 받은 토큰은, 사용자가 14일 전에 마지막으로 왔더라도 똑같이 유효하다. 그래서 **본인 확인이 다시 필요한 작업**(되돌리기 어려운 제출, 결제 등)에는 그대로 믿으면 안 된다. 그때는 사용자에게 다시 로그인시키는 절차(authorize에 `prompt=login`을 붙이거나 별도 본인인증)를 거친다. id_token의 `auth_time`(사용자가 실제로 로그인한 시각)을 보면 위임이 언제 이뤄졌는지 구분할 수 있다.

**갱신 때 받은 id_token의 규칙 (OIDC Core 12.2절)**: 갱신 응답에는 id_token이 없을 수도 있다(IdP 인증 서버는 준다). 들어 있다면 다음을 지켜야 한다.

| claim | 갱신 때 받은 id_token에서 |
|---|---|
| `iss`, `sub`, `aud` | 처음 로그인 때와 **같아야 한다** |
| `iat` | 새로 발급한 시각 |
| `auth_time` | **처음 로그인한 시각 그대로** (새 발급 시각이 아님) |
| `nonce` | 넣지 않는 것이 원칙. 있다면 처음 값과 같아야 한다 |

그래서 갱신이 아무리 이어져도 `auth_time`을 보면 "사용자가 실제로 마지막에 로그인한 때"를 알 수 있다.

### 8.6 access token 사용법 (RFC 6750)

클라이언트가 리소스 서버에 access token을 보내는 방법은 세 가지가 정의돼 있다.

| 방법 | 예 | 상태 |
|---|---|---|
| `Authorization` 헤더 | `Authorization: Bearer at-5f1c…` | ✅ 표준 방법 |
| POST 본문 | `access_token=at-5f1c…` (form 인코딩, 조건 있음) | ⚠️ 헤더를 못 쓸 때만 |
| URL 쿼리 | `GET /api?access_token=at-5f1c…` | ❌ RFC 6750은 SHOULD NOT, RFC 9700은 MUST NOT, OAuth 2.1 초안은 삭제 |

**리소스 서버의 오류 응답**: 실패하면 `WWW-Authenticate` 헤더로 이유를 알린다.

```http
# 토큰 없이 호출: 오류 코드 없이 인증 방식만 알림
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer realm="idp-client"

# 토큰이 만료·위조·폐기됨
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer realm="idp-client", error="invalid_token", error_description="The access token expired"

# 토큰은 유효하지만 권한(scope) 부족
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer realm="idp-client", error="insufficient_scope", scope="service"
```

| error | 상태 코드 | 클라이언트가 할 일 |
|---|---|---|
| (없음) | 401 | 토큰을 붙여 다시 요청 |
| `invalid_request` | 400 | 요청 형식 수정 |
| `invalid_token` | 401 | refresh token으로 **한 번** 갱신 후 재시도. 또 실패하면 다시 로그인 |
| `insufficient_scope` | 403 | 재시도해도 소용없음. 더 넓은 scope로 다시 인가받아야 함 |

발신자 제한 토큰 중 DPoP(15.6.2)를 쓰면 인증 방식 이름이 `Bearer` 대신 `DPoP`가 된다(`Authorization: DPoP at-…`). mTLS에 묶은 토큰(RFC 8705)은 헤더가 그대로 `Bearer`이고, 묶임 확인은 TLS 연결의 클라이언트 인증서로 한다.

### 8.7 토큰 수명 설계

| 토큰 | 흔한 수명 | 이유 |
|---|---|---|
| authorization code | 수십 초 ~ 10분 (IdP 인증 서버: 60초) | 곧바로 교환하므로 길 이유가 없다. 표준은 최대 10분 권장 |
| access token | 수 분 ~ 1시간 (IdP 인증 서버: 60분) | 유출되면 만료까지 막을 수 없는 경우가 많다(JWT). 짧을수록 피해가 작다 |
| refresh token | 수일 ~ 수개월 | 사용자가 다시 로그인하지 않아도 되는 기간 |
| id_token | 수 분 ~ 1시간 (제공자마다 다르다) | 받자마자 한 번 검증하고 쓰는 용도. 수명이 길어도 이 값으로 로그인 상태를 유지하지 않는다 |

refresh token의 만료는 두 가지 방식을 조합한다.

```
[비활성 만료 (sliding)]  마지막 사용 후 N일이 지나면 만료     ← IdP 인증 서버: 마지막 사용 후 14일
  사용 ●──────●───●─────────●──── … 계속 쓰면 계속 연장
                                  └── 14일 동안 안 쓰면 만료

[절대 만료 (absolute)]   처음 로그인 후 M일이 지나면 무조건 만료
  로그인 ●═══════════════════════════════════╳ M일
          쓰든 안 쓰든 이 시점에 다시 로그인
```

비활성 만료만 있으면, 훔친 refresh token은 공격자가 계속 쓰는 한 **끝없이** 살아 있다. rotation의 재사용 탐지(8.4절)는 정상 클라이언트가 옛 토큰을 다시 내밀 때에야 작동한다. 사용자가 앱을 그만 써서 정상 클라이언트가 더 이상 갱신하지 않으면 탐지도 일어나지 않는다. 그래서 민감한 서비스는 절대 만료를 함께 둔다. 표준의 규칙은 이렇다.

| 규칙 | 근거 |
|---|---|
| 일정 기간 쓰지 않은 refresh token은 만료 | RFC 9700 4.14.2 (SHOULD) |
| 비밀번호 변경, 인증 서버 로그아웃 같은 보안 이벤트 때 폐기 가능 | RFC 9700 4.14.2 (MAY) |

IdP 인증 서버는 비활성 만료(14일)를 쓰고 있다. 절대 만료가 있는지는 확인 필요다. 브라우저 앱(SPA)의 refresh token에는 더 엄격한 규칙이 붙는다(13.7절).

### 8.8 토큰 폐기 (RFC 7009)

사용자가 연결을 끊거나, 로그아웃하거나, 토큰 유출이 의심될 때 클라이언트가 **인증 서버에 "이 토큰을 무효로 해 달라"**고 요청한다.

```http
POST /revoke
Authorization: Basic base64(client_id:secret)
Content-Type: application/x-www-form-urlencoded

token=rt-9c2e…&token_type_hint=refresh_token

→ HTTP/1.1 200 OK
```

- **토큰이 이미 무효여도 200을 돌려준다.** 클라이언트가 그 오류로 할 수 있는 일이 없고, 토큰을 무효로 만든다는 목적은 이미 이뤄졌기 때문이다(RFC 7009 2.2절). 다만 다른 클라이언트에게 발급된 토큰을 폐기하려 하면 인증 서버는 거부하고 오류를 돌려준다(RFC 7009 2.1절).
- `token_type_hint`는 인증 서버가 토큰을 빨리 찾도록 돕는 힌트일 뿐, 틀려도 된다.
- refresh token을 폐기하면, 인증 서버는 같은 위임에서 나온 access token도 함께 무효로 하는 것이 권장된다(SHOULD).

**JWT access token은 폐기해도 바로 멈추지 않을 수 있다.**

```
[불투명 토큰]  리소스 서버가 매 요청 introspection으로 인증 서버에 물어봄
               → 폐기 즉시 active:false → 바로 거부

[JWT 토큰]    리소스 서버가 서명과 exp만 보고 스스로 판단 (인증 서버에 묻지 않음)
               → 폐기돼도 exp까지는 통과할 수 있음
               → 그래서 access token 수명을 짧게 둔다 (8.7절)
```

이 연동의 연결 해제(16.9절)가 확정되면, IdP 인증 서버가 할 일이 바로 이 폐기다.

**사용자 쪽에서 끊는 길도 있어야 한다.** 2.1절에서 OAuth의 장점으로 "연결을 끊으려면 그 토큰만 무효화하면 된다"를 들었다. 그 약속이 지켜지려면 클라이언트가 폐기를 요청하는 길뿐 아니라, **사용자가 인증 서버에서 직접 "연결된 앱" 목록을 보고 끊는 화면**이 필요하다. OAuth 2.1 초안 7.9절도 인증 서버가 사용자와 관리자에게 이 기능을 주라고 권한다(SHOULD).

```
IdP 인증 서버 계정 설정 > 연결된 앱
┌──────────────────────────────────────────────┐
│ 클라이언트 앱            연결일 2026-11-01  권한: 이메일, 서비스 │  [연결 끊기]  → 그 위임의 토큰 전체 폐기
│ Example Helper  연결일 2026-09-12  권한: 서비스 읽기  │  [연결 끊기]
└──────────────────────────────────────────────┘
```

### 8.9 클라이언트가 토큰을 보관할 때

클라이언트 서버는 연결된 **모든 사용자**의 refresh token을 오래 쌓아 둔다. 클라이언트 앱 서버가 IdP 서비스 refresh token을 14일씩 보관하는 것처럼. 그래서 이 저장소 하나가 털리면 **그 사이트의 모든 사용자 토큰이 한꺼번에** 샌다(RFC 6819 4.1.2절).

| 규칙 | 근거 |
|---|---|
| access·refresh token은 전송 중에도 저장 중에도 기밀로 다룬다 | RFC 6749 10.3·10.4절 (MUST) |
| DB에 저장할 때 암호화한다. 암호화 키는 KMS 같은 별도 관리 시스템에 둔다 | 해석: 위 규칙의 구현 |
| client_secret과 토큰을 **같은 저장소에 두지 않는다** | 해석: 8.5절에서 "refresh token만으로는 못 쓰고 secret이 함께 있어야 한다"고 했다. 둘이 한 곳에 있으면 한 번에 둘 다 샌다 |
| 토큰을 로그·에러 리포트·분석 이벤트에 남기지 않는다 | 해석 |
| 연결 해제·탈퇴 때 저장한 토큰을 지우고 인증 서버에 폐기를 요청한다 | 8.8절 |
| **값의 길이를 가정하지 않는다.** 토큰 컬럼을 `VARCHAR(255)`처럼 짧게 잡지 않는다 | OAuth 2.1 초안 1.7.1절 (MUST NOT assume). JWT 형식 토큰은 1KB를 넘기 쉽다 |

길이 문제는 증상이 원인과 멀리 나타나서 찾기 어렵다. 토큰이 DB에 잘려 저장되면, 나중에 갱신할 때 "가끔 `invalid_grant`"로만 보인다.

**인증 서버 쪽의 짝 규칙**: 토큰이나 자격 증명이 담긴 응답에는 `Cache-Control: no-store`를 넣는다(RFC 6749 5.1절, OAuth 2.1 초안 3.2.3절, MUST). 프록시나 브라우저가 토큰 응답을 캐시해 두었다가 다른 사람에게 내주는 일을 막는다.

| 클라이언트 종류 | 토큰을 둘 곳 |
|---|---|
| 서버 | 암호화한 DB, 서버 메모리 캐시 |
| 네이티브 앱 | OS 보안 저장소 (iOS Keychain, Android Keystore로 암호화) |
| 브라우저 앱 | 가능하면 브라우저에 두지 않는다 (13장) |

### 8.10 bearer 토큰과 발신자 제한 토큰

지금까지 본 access token은 모두 **bearer token**이다. bearer는 "소지자"라는 뜻으로, **가진 사람이 곧 주인**이다. 버스 승차권처럼 누가 내밀든 통과한다. 그래서 지금까지의 방어는 대부분 "토큰이 새지 않게"에 집중했다.

**발신자 제한(sender-constrained) 토큰**은 접근이 다르다. 토큰을 특정 클라이언트의 **키**에 묶어서, 토큰과 함께 "그 키를 지금 가지고 있다"는 증명을 내야만 통과시킨다. 새더라도 키가 없으면 쓸 수 없다.

```
bearer token                          발신자 제한 토큰
┌────────────────────┐                ┌────────────────────────────────────┐
│ 토큰만 있으면 통과    │                │ 토큰 + "이 키의 주인이다"라는 증명    │
│ (승차권)            │                │ (이름이 적힌 탑승권 + 신분증)          │
└────────────────────┘                └────────────────────────────────────┘
훔친 사람도 사용 가능                      키가 없으면 사용 불가
```

표준 방식은 mTLS 인증서에 묶는 RFC 8705(10.3절)와, 요청마다 비밀키 서명을 붙이는 DPoP(RFC 9449)다. OAuth 2.1 초안은 서론(1.4.3절)에서 발신자 제한을 권하고, public client의 refresh token에는 rotation 아니면 발신자 제한을 요구한다(8.4절). 동작 원리와 두 방식의 비교는 보안 장의 15.6.2에서 자세히 다룬다.

---

## 9. OpenID Connect

### 9.1 OAuth와의 관계

```
┌───────────────────────────────────────────────┐
│ OpenID Connect (OIDC)                          │  "누가 로그인했나" (인증)
│   id_token, sub, nonce, discovery, userinfo     │
│ ┌───────────────────────────────────────────┐ │
│ │ OAuth 2.0 / 2.1                            │ │  "무엇을 할 수 있나" (인가)
│ │   authorize, token, grant_type, PKCE, scope │ │
│ └───────────────────────────────────────────┘ │
└───────────────────────────────────────────────┘
```

**OIDC는 OAuth 위에서만 동작한다.** OIDC 표준(OpenID Connect Core 1.0)은 스스로를 OAuth 2.0 위에 얹은 신원 확인 층으로 정의하고, authorize·token 엔드포인트, authorization code, 클라이언트 인증을 모두 OAuth의 것을 그대로 쓴다. 그래서 OAuth 없이 OIDC만 있는 구조는 성립하지 않는다.

| 조합 | 성립하나 | 예 |
|---|---|---|
| OAuth만 (OIDC 없음) | ✅ | IdP 서비스 → 클라이언트 앱의 client_credentials. 사용자가 없으니 신원 확인 층이 필요 없다 |
| OAuth + OIDC, 둘 다 사용 | ✅ | 이 장의 연동 사례. id_token으로 누구인지 알고, access token으로 서비스 API 호출 |
| OAuth 흐름 위에서 id_token만 사용 | ✅ | 이 연동의 최초 설계. "access token은 쓸 일이 없다"고 했던 단계 (16.11절) |
| OAuth 없이 OIDC만 | ❌ | OIDC에는 독자적인 전송 방식이 없다 |

OIDC로 동작하게 만드는 스위치는 scope의 `openid`다. 이 값이 없으면 id_token이 나오지 않고 순수 OAuth로 동작한다.

### 9.2 id_token

**사용자가 누구이고 언제 어떻게 로그인했는지를 담아, 인증 서버가 서명해서 발급하는 신분증**이다. 형식은 JWT다.

```
eyJhbGciOiJSUzI1NiIsImtpZCI6ImsxIn0 . eyJpc3MiOiJodHRwczovL2dhdGUu… . SflKxwRJSMeKKF2QT4fwpM…
└──────── 헤더 (base64url) ────────┘   └──────── 본문 (base64url) ───────┘   └──── 서명 ────┘
  {"alg":"RS256","kid":"k1"}
```

```json
{
  "iss": "https://auth.stg.idp.example",   // 누가 발급했나
  "sub": "12345",                          // 누구인가 (회원 식별자)
  "aud": "client-app-id",                 // 누구에게 주는 것인가 (받는 client_id)
  "exp": 1793000300,                       // 언제 만료되나
  "iat": 1793000000,                       // 언제 발급했나
  "auth_time": 1793000000,                 // 사용자가 실제로 로그인한 시각
  "nonce": "n-7f3a91",                     // 이 로그인 요청과 짝지을 값
  "email": "user@example.com",
  "email_verified": true
}
```

헤더와 본문은 base64url **인코딩**일 뿐 암호화가 아니다. 누구나 풀어서 읽을 수 있다. 위조를 막는 것은 세 번째 덩어리인 **서명**이다.

**access token과의 차이가 핵심이다.**

| | id_token | access token |
|---|---|---|
| 읽는 쪽 | **클라이언트(클라이언트 앱)** | **리소스 서버(IdP 서비스 API)** |
| 용도 | "로그인한 사람이 누구인가" 확인 | "이 요청을 허락해도 되는가" 확인 |
| `aud` | 클라이언트의 client_id | 리소스 서버 |
| API 호출에 쓰나 | ❌ 쓰면 안 된다 (10.4절) | ✅ |

### 9.3 sub와 회원 저장

**sub(subject)는 발급자(`iss`) 안에서 사용자를 유일하게 가리키는 식별자**다. IdP 인증 서버에서는 IdP 서비스 회원 식별자이고, 예시로는 `"12345"`다.

- **바뀌지 않는다.** 이메일은 사용자가 바꿀 수 있지만 `sub`는 그대로다. 그래서 회원을 찾는 열쇠로 `sub`를 쓴다.
- **`iss`와 짝으로만 유일하다.** 다른 인증 서버의 `"12345"`는 다른 사람이다. 그래서 `(iss, sub)` 짝으로 저장한다.
- **숫자처럼 보여도 문자열이다.** 숫자로 바꿔 저장하면 앞자리 0이 사라지거나 형식이 바뀌어 매칭이 깨질 수 있다.

**권장 테이블 구조**

```
users                                  user_identities  (로그인 수단 연결표)
┌──────────┬──────────────────┐        ┌──────────┬────────────────────────────┬──────────┬──────────────────┐
│ id (PK)  │ email (프로필용)   │        │ user_id  │ iss                        │ sub      │ email_at_link    │
├──────────┼──────────────────┤        ├──────────┼────────────────────────────┼──────────┼──────────────────┤
│ 101      │ a@example.com    │◄───────┤ 101      │ https://kauth.kakao.com    │ 98765432 │ a@example.com    │
│          │                  │◄───────┤ 101      │ https://accounts.google.com│ 1170…    │ a@gmail.com      │
└──────────┴──────────────────┘        └──────────┴────────────────────────────┴──────────┴──────────────────┘
                                         UNIQUE (iss, sub)
```

- 로그인할 때마다 `(iss, sub)`로 `user_identities`를 찾고, 찾으면 그 `user_id`로 로그인시킨다.
- 한 회원이 여러 로그인 수단을 가질 수 있다.

#### 🛡️ 공격: 이메일로 기존 계정에 자동 연결해서 계정 탈취

**공격 원리**:

```
기존 회원: a@example.com (이메일·비밀번호로 가입)
공격자:    어떤 IdP에서 자기 계정의 이메일을 a@example.com으로 설정 (인증하지 않은 채)
           → 그 IdP로 로그인 → 서비스가 email로 기존 회원을 찾아 자동 연결
           → 공격자가 기존 회원 계정으로 로그인됨
```

**방어**: email을 식별 키로 쓰지 않는다. email로 기존 회원과 연결하는 것은 **처음 연결할 때 한 번만**, 두 조건을 지킬 때만 한다.

- id_token의 `email_verified`가 `true`인지 확인한다. **이 claim이 없으면 미인증으로 취급한다.** 예를 들어 카카오 id_token에는 `email_verified`가 없다. 그럴 때는 제공자의 별도 API가 주는 인증 여부를 쓰거나, 아래 두 번째 절차만으로 연결한다.
- 자동으로 합치지 않고, 기존 계정으로 **한 번 더 로그인하게 해서** 본인임을 확인한 뒤 연결한다. 연결한 뒤로는 `(iss, sub)`로만 찾는다.

**방어 원리**: 이메일은 IdP가 "이 사람이 이 주소를 소유했다"고 보장할 때만 의미가 있다. 보장 여부(`email_verified`)를 확인하고, 그래도 남는 위험은 **기존 계정의 비밀번호를 아는 사람만 연결할 수 있게** 해서 없앤다.

### 9.4 nonce

**클라이언트가 로그인 요청마다 새로 만드는 일회용 난수**다. authorize 요청에 넣으면 인증 서버가 그 값을 id_token 안에 그대로 넣어 돌려주고, 클라이언트는 자기가 보낸 값과 같은지 대조한다.

OIDC Core가 밝힌 목적은 두 가지다. **클라이언트의 세션과 id_token을 묶는 것**, 그리고 그 결과로 **재사용(replay) 공격을 완화하는 것**이다. authorization code 흐름에서 nonce는 선택(OPTIONAL)이지만, 토큰을 URL로 받던 implicit 흐름에서는 필수였다. 선택이라도 넣는 편이 좋다. OAuth 2.1 초안은 OIDC 흐름의 nonce 검증을 CSRF 방어 수단으로도 인정하고, PKCE 생략 예외의 조건으로도 쓴다(7.2절, 7.3절).

#### 🛡️ 공격: id_token 재사용(replay)

**공격 원리**: 공격자가 예전에 가로챈 (서명이 유효한) id_token을 다른 로그인 응답에 끼워 넣는다. 서명은 진짜이므로 서명 검증만 하는 클라이언트는 속는다.

**방어**: 로그인마다 새 nonce를 만들어 세션에 저장하고, 받은 id_token의 `nonce`와 대조한다.

**방어 원리**: 예전 id_token에는 **예전 로그인의 nonce**가 들어 있다. 서명 때문에 공격자는 nonce만 바꿔 넣을 수도 없다. 그래서 "이 신분증은 지금 이 로그인을 위해 발급된 것인가"를 확인할 수 있다.

state와 비슷해 보이지만 지키는 대상이 다르다.

| | state | nonce |
|---|---|---|
| 소속 | OAuth | OIDC |
| 어디로 돌아오나 | redirect URL 쿼리 | id_token 안 |
| 막는 것 | 남의 로그인 결과를 내 세션에 끼워 넣기 (CSRF) | 예전 id_token을 다시 쓰기 |

### 9.5 scope: OIDC scope와 API scope

scope의 기본 규칙은 5.3절에서 봤다. OIDC를 쓰면 한 `scope` 파라미터 안에 두 종류의 값이 섞여 들어간다.

```
scope=openid email service
      ─────┬────  ──┬───
           │        └─ 서비스가 직접 정의한 scope → "어떤 API를 부를 수 있나"
           └────────── OIDC가 정의한 scope      → "사용자 정보 중 무엇을 받을 수 있나"
```

| 종류 | 예 | 정의한 곳 | 결정하는 것 |
|---|---|---|---|
| OIDC scope | `openid`, `email`, `profile`, `phone`, `address`, `offline_access` | OIDC 표준 | id_token 발급 여부, 어떤 사용자 정보(claim)를 내줄지 |
| API scope | `service`, `read:history` 같은 것 | 각 서비스 | access token으로 어떤 API를 호출할 수 있는지 |

| OIDC scope | 결과 |
|---|---|
| `openid` | id_token 발급. `sub` 포함. 이 값이 없으면 OIDC가 아니라 순수 OAuth로 동작 |
| `email` | `email`, `email_verified` |
| `profile` | `name`, `nickname`, `picture`, `birthdate` 등 |
| `phone` | `phone_number`, `phone_number_verified` |
| `offline_access` | refresh token 요청 |

**클라이언트 등록에 허용된 범위를 넘을 수 없다.** 클라이언트 앱은 `openid email`만 허용돼 있어서, 다른 값을 요청하면 `invalid_scope`가 난다.

**OIDC scope는 id_token만의 문제가 아니다.** OIDC Core 5.4절은 `profile`, `email`, `address`, `phone` scope로 요청한 정보를, access token이 발급되는 흐름에서는 **userinfo에서 돌려준다**고 정한다. access token 없이 id_token만 받는 흐름에서는 id_token에 담는다. 실제로는 code 흐름에서도 id_token에 바로 담아 주는 인증 서버가 많다.

또 이 scope로 요청한 정보는 **자발적 제공 항목(Voluntary Claim)**이다. 사용자가 동의 화면에서 거부하거나 인증 서버가 생략하면 오지 않을 수 있으므로, 코드는 값이 없는 경우를 처리해야 한다. 특정 정보를 id_token에 반드시 담아 달라고 요구하려면 `claims` 요청 파라미터(OIDC Core 5.5절)를 쓴다.

```
scope=openid email 로 요청했을 때

[방식 A] id_token에 바로 담음           ← IdP 인증 서버의 방식
  id_token = { sub, email, email_verified, … }

[방식 B] id_token에는 sub만, 나머지는 userinfo로
  id_token = { sub, … }
  GET /userinfo  Bearer access_token  →  { sub, email, email_verified }
```

토큰 응답의 `scope` 필드는 **access token에 부여된 범위 전체**를 뜻한다. 그래서 OIDC scope와 API scope가 모두 여기에 기록된다.

### 9.6 discovery

**인증 서버가 자기 주소와 지원 규칙을 JSON 한 장으로 공개하는 문서**다. 주소는 `{issuer}/.well-known/openid-configuration`으로 정해져 있다.

```json
{
  "issuer": "https://auth.stg.idp.example",
  "authorization_endpoint": "https://auth.stg.idp.example/oauth/authorize/",
  "token_endpoint": "https://auth.stg.idp.example/oauth/token/",
  "jwks_uri": "https://auth.stg.idp.example/.well-known/jwks.json",
  "userinfo_endpoint": "…",
  "end_session_endpoint": "https://auth.stg.idp.example/oauth/logout/",
  "scopes_supported": ["openid", "email"],
  "response_types_supported": ["code"],
  "grant_types_supported": ["authorization_code", "refresh_token"],
  "code_challenge_methods_supported": ["S256"],
  "id_token_signing_alg_values_supported": ["RS256"]
}
```

(값은 IdP 인증 서버 연동 가이드에서 확인된 주소와 규칙을 바탕으로 쓴 예시다. 실제 응답 전체는 확인하지 않았다.)

```
클라이언트 앱 서버 (또는 IdP 서비스 API)
   │ ① 설정에는 issuer 하나만 있음: https://auth.stg.idp.example
   ├─► GET /.well-known/openid-configuration
   │◄── { issuer, authorization_endpoint, token_endpoint, jwks_uri, … }
   │ ② 응답의 issuer가 내가 설정한 issuer와 같은지 확인
   ├─► GET jwks_uri
   │◄── { keys: [ … ] }
   │ ③ 둘 다 캐시. 이후 토큰 검증은 IdP 인증 서버 호출 없이 처리
```

- **두 주소 모두 인증 없이 누구나 열 수 있다.** 주소, 지원 규칙, 공개키뿐이라 공개해도 안전하다.
- **매 요청마다 부르지 않는다.** 라이브러리가 처음 필요할 때 받아 일정 시간 캐시하고(예: PyJWKClient의 JWKS 캐시 기본 5분), 모르는 `kid`를 만나면 다시 받는다. IdP 인증 서버가 잠시 느려져도 이미 캐시한 쪽의 검증은 계속 동작한다.
- **②의 issuer 대조가 중요하다.** 응답의 `issuer`가 문서를 받아 온 주소의 issuer와 정확히 같지 않으면, 그 문서의 내용을 **쓰면 안 된다**(RFC 8414 3.3절, MUST NOT). 다른 인증 서버의 문서에 속아 엉뚱한 공개키를 믿게 되는 것을 막는다. 이 대조를 하지 않는 라이브러리도 있다(예: authlib). 설정에 issuer를 고정해 두면 위험은 작지만, 여러 인증 서버를 다룬다면 직접 대조한다.
- **OAuth 전용 메타데이터 경로도 있다.** OIDC가 아닌 순수 OAuth 인증 서버는 RFC 8414의 `/.well-known/oauth-authorization-server`를 쓴다. issuer에 경로가 붙어 있으면 위치가 다르다. RFC 8414는 경로 **앞에** 끼워 넣고(`https://example.com/.well-known/oauth-authorization-server/issuer1`), OIDC Discovery는 issuer **뒤에** 붙인다(`https://example.com/issuer1/.well-known/openid-configuration`).
- 클라이언트 라이브러리에 issuer 하나만 넣으면 나머지 주소를 스스로 알아낸다. 그래서 IdP 인증 서버 연동 가이드에서 클라이언트 앱에 넣으라고 한 설정은 7개뿐이었다.

```bash
# 직접 확인
curl -s https://auth.stg.idp.example/.well-known/openid-configuration | jq
curl -s "$(curl -s https://auth.stg.idp.example/.well-known/openid-configuration | jq -r .jwks_uri)" | jq
```

### 9.7 JWKS

**JWKS(JSON Web Key Set)는 인증 서버가 토큰 서명을 검증할 공개키 목록을 JSON으로 공개한 것**이다. RFC 7517에 형식이 정의돼 있다.

```json
{
  "keys": [
    { "kty": "RSA", "use": "sig", "alg": "RS256", "kid": "2026-10-key",
      "n": "0vx7agoebGcQSuu...", "e": "AQAB" },
    { "kty": "RSA", "use": "sig", "alg": "RS256", "kid": "2026-07-key",
      "n": "...", "e": "AQAB" }
  ]
}
```

| 필드 | 의미 |
|---|---|
| `kty` | 키 종류 (RSA, EC 등) |
| `use` | 용도 (`sig` = 서명 검증) |
| `alg` | 서명 알고리즘 |
| `kid` | 키 식별자. 토큰 헤더의 `kid`와 맞춰 고른다 |
| `n`, `e` | RSA 공개키 자체 (modulus, exponent) |

```
IdP 인증 서버가 발급한 JWT
  header : { "alg": "RS256", "kid": "2026-10-key" }
                    │ ① header의 kid를 읽음
                    ▼
캐시한 JWKS에서 kid == "2026-10-key"인 키를 찾음
                    │ ② 그 공개키로 signature 검증
                    ▼
            통과해야 payload를 믿음
```

- **비밀키는 IdP 인증 서버 밖으로 나가지 않는다.** 검증하는 쪽이 아무리 늘어도 서명을 만들 수 있는 것은 IdP 인증 서버뿐이다.
- **키 교체(rotation)가 자연스럽다.** IdP 인증 서버가 새 `kid`로 서명을 시작하면, 검증하는 쪽은 모르는 `kid`를 만났을 때 JWKS를 다시 받는다. 옛 키는 기존 토큰이 만료될 때까지 목록에 남겨 둔다.
- 비밀키가 없으므로 이 파일은 공개돼도 안전하다. Google, Apple, Kakao 등 큰 인증 서버가 모두 공개해 두고 있다.

**라이브러리가 다 해 준다**

| 언어 | 라이브러리 예 |
|---|---|
| Python | `PyJWT`의 `PyJWKClient` |
| Node.js | `jose`의 `createRemoteJWKSet` |
| Java / Kotlin | Spring Security `NimbusJwtDecoder.withJwkSetUri(...)` |
| Go | `lestrrat-go/jwx`, `MicahParks/keyfunc` |

### 9.8 userinfo

**access token을 내밀면 사용자 정보를 JSON으로 돌려주는 OIDC 표준 API**다.

```http
GET /userinfo
Authorization: Bearer <access_token>

→ { "sub": "12345", "email": "user@example.com", "email_verified": true }
```

id_token에 다 담기 어려운 정보나, 로그인 이후 바뀌었을 수 있는 최신 정보를 가져올 때 쓴다. IdP 인증 서버 연동에서는 필요한 값이 id_token에 다 있어서 userinfo를 부를 필요가 없다.

### 9.9 id_token 검증은 꼭 필요한가

**id_token을 받는 것 자체는 필요하고, 검증 중 일부는 이 흐름에서 생략이 허용된다.**

**클라이언트가 sub를 알아야 하는 이유** (클라이언트 앱 예)

| 쓰는 곳 | 왜 sub가 필요한가 |
|---|---|
| 클라이언트 앱의 연결표 | "클라이언트 앱 사용자 ↔ IdP 서비스 회원 12345"를 저장해야 연결 여부에 답할 수 있다 |
| IdP 서비스 → 클라이언트 앱 API 호출 | IdP 서비스가 회원 12345를 지정하면 클라이언트 앱이 이 표로 자기 사용자를 찾는다 |
| 재연결 판단 | 같은 클라이언트 앱 사용자가 다른 IdP 서비스 계정으로 로그인했는지 알아챌 수 있다 |

access token만으로는 이것을 알 수 없다. access token은 리소스 서버가 읽는 토큰이라 클라이언트가 해석해서는 안 되고, 형식이 JWT인지도 보장되지 않는다.

**id_token 없이 하는 방법과 비교**

| 방법 | 동작 | 평가 |
|---|---|---|
| **id_token** | token 응답에 서명된 신원 정보 포함 | 표준. 추가 호출 없음. 라이브러리가 검증까지 처리 |
| access token + userinfo | 토큰을 받은 뒤 `/userinfo`를 한 번 더 호출 | 표준. 왕복 1회 추가. 단 "누가 로그인했나"의 판단은 id_token의 `aud`로 해야 안전하다 |
| 비표준 사용자 API | access token으로 직접 만든 `/me` 같은 API를 불러 사용자 확인 | ⚠️ OIDC 라이브러리를 못 쓰고, **토큰 바꿔치기 공격**에 열린다. 클라이언트는 받은 access token이 "자기에게 발급된 것"인지 확인할 수단이 없기 때문이다(15.7.2) |

**생략이 허용되는 부분**: OIDC Core 3.1.3.7절은 id_token을 **클라이언트와 token 엔드포인트의 직접 통신으로 받았다면**, 발급자를 확인하기 위한 서명 검사 대신 TLS 서버 인증을 써도 된다(MAY)고 정한다. 그 밖의 경로로 받은 id_token은 서명 검증이 필수(MUST)다.

| 검증 항목 | code 흐름(token 엔드포인트에서 직접 받음) | 이유 |
|---|---|---|
| 서명 (JWKS) | 선택. 발급자 확인을 TLS로 갈음할 수 있음 | TLS가 응답이 IdP 인증 서버에서 왔음을 이미 보장 (11장) |
| `iss` | **필수** | 다른 인증 서버의 토큰과 섞이지 않게 |
| `aud` = 자기 client_id | **필수** | 다른 클라이언트용 토큰을 받지 않게 |
| `exp` | **필수** | 만료된 토큰을 받지 않게 |
| `nonce` | **필수** (요청에 넣었다면) | 예전 응답 재사용 방지 |

그래도 서명 검증은 포함하는 편이 좋다. 대부분의 라이브러리가 자동으로 하므로 비용이 거의 없고, 나중에 id_token을 다른 경로로 전달받는 구조 변경에도 안전하다.

### 9.10 소셜 로그인과 같은 구조

클라이언트 앱과 IdP 인증 서버의 관계는, 어떤 서비스가 카카오 로그인을 붙일 때 그 서비스와 카카오의 관계와 똑같다.

```
[카카오 로그인을 붙인 서비스]              [클라이언트 앱 × IdP 서비스]
  서비스      = client (RP)              클라이언트 앱  = client (RP)
  카카오      = 인증 서버 (IdP)           IdP 서비스 = 인증 서버 (IdP)
  카카오 회원  = 로그인하는 사람            IdP 서비스 회원 = 로그인하는 사람
  카카오 id_token의 sub = 카카오 회원번호    IdP 인증 서버 id_token의 sub = IdP 서비스 회원 식별자
```

RP(Relying Party)는 남의 인증을 믿고 쓰는 쪽, IdP(Identity Provider)는 신원을 확인해 주는 쪽이다. 그래서 IdP 인증 서버 연동 가이드의 제목이 "IdP 서비스로 로그인"이고, 클라이언트 앱 입장에서 IdP 서비스는 카카오 같은 로그인 수단 하나가 된다.

**국내 소셜 로그인에서 알아 둘 점**

- **카카오**는 OIDC를 지원하므로 `openid` scope로 id_token을 받을 수 있다. email은 사용자가 동의 화면에서 제공에 동의했을 때만 들어오고, 앱 설정에서 해당 동의 항목을 켜 둬야 한다. 카카오 id_token에는 `email_verified` claim이 없다(9.3절).
- **네이버 로그인**도 OIDC를 지원한다(discovery: `https://nid.naver.com/.well-known/openid-configuration`). 다만 id_token에는 기본 claim만 있고 email 같은 프로필은 없어서, 프로필은 access token으로 기존 프로필 API를 불러 받는다. 또 `sub`가 앱마다 다른 값(pairwise)이다. 원칙은 같다. `(iss, sub)`로 회원을 찾는다.

### 9.11 로그인 세션, 토큰, 로그아웃

OAuth·OIDC로 로그인하면 **세 가지 상태**가 따로 생긴다. 로그아웃이 헷갈리는 이유는 이 셋이 서로 독립이기 때문이다.

```
사용자 브라우저
 ├─ ① 클라이언트 세션   클라이언트 앱 서버의 세션 쿠키              "클라이언트 앱에 로그인돼 있다"
 ├─ ② 인증 서버 세션    IdP 인증 서버 도메인의 로그인 쿠키             "IdP 인증 서버에 로그인돼 있다"
 │                     (다음 authorize 때 로그인 화면 생략)
 └─ (브라우저 밖) ③ 토큰  클라이언트 앱 서버가 보관한 access·refresh token  "클라이언트 앱이 IdP 서비스 API를 쓸 수 있다"
```

| 무엇을 하면 | ① 클라이언트 세션 | ② 인증 서버 세션 | ③ 토큰 |
|---|---|---|---|
| 클라이언트에서만 로그아웃 | 끝남 | **남음** → 다음 로그인 때 화면 없이 통과 | **남음** |
| 인증 서버 로그아웃 (RP-Initiated Logout) | 클라이언트가 별도로 지워야 함 | 끝남 | 보통 남음. 인증 서버 정책에 따라 함께 폐기될 수 있다(8.7절) |
| 토큰 폐기 (8.8절) | 그대로 | 그대로 | 끝남 |
| 완전한 연결 해제 | 지움 | 필요하면 로그아웃 | **폐기** |

**RP-Initiated Logout (OpenID Connect)**: 클라이언트가 사용자 브라우저를 인증 서버의 로그아웃 주소로 보낸다.

```
클라이언트 서버: 자기 세션 삭제 + 같은 응답에서
  302 → https://auth.stg.idp.example/oauth/logout/
        ?id_token_hint=<받았던 id_token>&post_logout_redirect_uri=https://…/logged-out&state=lo-3b9e
        (client_id도 함께 보낼 수 있다. IdP 인증 서버 연동 가이드는 client_id를 필수로 요구)
브라우저 → IdP 인증 서버: 브라우저가 들고 간 IdP 인증 서버 쿠키로 누구를 로그아웃할지 찾음 → 세션 종료
IdP 인증 서버 → 302 → https://…/logged-out?state=lo-3b9e
```

`id_token_hint`는 권장(RECOMMENDED) 파라미터다. 빠뜨리면 인증 서버는 사용자에게 "정말 로그아웃할까요?"를 반드시 묻고(MUST), 다른 확인 수단이 없으면 post_logout_redirect_uri로 돌려보내지 않는다(MUST NOT). post_logout_redirect_uri는 미리 등록한 값과 정확히 같아야 한다. 로그아웃 뒤 화면이 인증 서버에 멈춰 있다면 이 두 가지부터 확인한다.

**서버에서 로그아웃 주소를 직접 호출하면 안 된다.** 인증 서버는 **브라우저가 들고 오는 쿠키**로 누구를 로그아웃할지 찾기 때문이다.

**Back-Channel Logout (OpenID Connect)**: 반대 방향이다. 인증 서버 세션이 끝나면(사용자 로그아웃, 관리자의 강제 종료 등. 어떤 사건에 보낼지는 인증 서버가 정한다), 인증 서버가 **브라우저를 거치지 않고** 각 클라이언트의 등록된 주소로 로그아웃 토큰을 POST한다.

```
IdP 인증 서버 ── POST https://client.example/backchannel-logout
        logout_token=<서명된 JWT: iss, aud, iat, exp, jti, sub와 sid 중 하나 이상,
                      events: {"http://schemas.openid.net/event/backchannel-logout": {}}>
클라이언트 앱 ── id_token처럼 서명·iss·aud·iat·exp 검증, events 확인, nonce가 없는지 확인
     ── 해당 사용자(sub)나 세션(sid)의 클라이언트 세션 삭제
```

`sid`는 인증 서버의 로그인 세션 식별자다. 인증 서버가 id_token에 `sid`를 넣어 줬다면, 클라이언트는 그 값을 자기 세션과 함께 저장해 두었다가 로그아웃 토큰의 `sid`와 맞춰 본다. 브라우저가 닫혀 있어도 전파된다는 것이 장점이다. 브라우저 iframe으로 각 클라이언트를 불러 로그아웃시키는 front-channel 방식도 있지만, Safari나 앱 웹뷰처럼 서드파티 쿠키를 기본으로 막는 환경에서는 동작하지 않는다.

### 9.12 로그인 동작을 조절하는 요청 파라미터

OIDC는 authorize 요청에 "어떻게 로그인시킬지"를 조절하는 파라미터를 정의한다(OIDC Core 3.1.2.1절).

| 파라미터 | 뜻 | 쓰임 |
|---|---|---|
| `prompt=none` | 어떤 화면도 띄우지 말 것. 이미 로그인·동의돼 있으면 바로 결과, 아니면 오류 (`login_required`, `interaction_required` 등) | 화면 없이 로그인 상태만 확인할 때. IdP 인증 서버는 지원하지 않아 항상 `login_required` |
| `prompt=login` | 이미 로그인돼 있어도 다시 로그인시킬 것 | 민감한 작업 전 재인증 (8.5절) |
| `prompt=consent` | 기억한 동의가 있어도 다시 동의를 받을 것 | scope가 바뀌었을 때 (7.8절) |
| `prompt=select_account` | 계정 선택 화면을 보여 줄 것 | 여러 계정을 쓰는 사용자 |
| `max_age=초` | 마지막 로그인 후 이 시간이 지났으면 다시 로그인시킬 것. 보내면 id_token에 `auth_time`이 반드시 들어간다. `max_age=0`은 `prompt=login`과 같다 | "최근 5분 안에 로그인한 사용자만" 같은 조건 |
| `login_hint` | 로그인할 계정의 힌트(이메일 등) | 로그인 화면에 계정을 미리 채움 |
| `id_token_hint` | 예전에 받은 id_token | 지금 로그인한 사용자가 그 사람인지 확인 |
| `acr_values` | 원하는 인증 수준 (예: 2단계 인증). 인증 서버가 따르지 않을 수 있는 **요청**이므로, 받은 토큰의 `acr`을 반드시 확인한다 | Step-up 인증 (14.9) |

`prompt=none`은 다른 값과 함께 쓸 수 없다. 함께 쓰면 오류다.

---

## 10. access token을 받는 쪽의 검증

### 10.1 검증 순서

리소스 서버(IdP 서비스 API)는 요청마다 access token을 검증한다. **"까서 본다"는 서명 검증을 먼저 하고 나서 본다는 뜻이어야 한다.** 서명 검증 없이 본문만 읽으면, 누구나 `"scope": "service"`를 넣은 가짜 토큰을 만들어 통과할 수 있다.

```
요청: Authorization: Bearer eyJ…
  │
  ⓪ typ          헤더의 typ == "at+jwt"     ← id_token 등 다른 종류의 JWT 차단 (10.4절)
  ① 서명 검증     JWKS 공개키 (kid로 선택), 알고리즘은 RS256만 허용
  ② iss          == https://auth.stg.idp.example
  ③ aud          == IdP 서비스 API         ← 다른 서비스용 토큰이 흘러오는 것 차단
  ④ exp          만료 전인가
  ⑤ scope        필요한 권한이 있는가
  │   ⓪~④ 실패: 401 invalid_token  /  ⑤ 실패: 403 insufficient_scope
  ▼
  sub를 꺼내 사용자 식별 → 처리
```

JWT 형식의 access token 표준(RFC 9068)은 리소스 서버가 ⓪~④를 반드시 검사하도록 정한다. 토큰에는 `iss`, `exp`, `aud`, `sub`, `client_id`, `iat`, `jti` 일곱 claim이 반드시 들어 있다. `scope` claim은 요청에 scope가 있었을 때 넣는 것이 권장(SHOULD)되며, 값은 공백으로 구분한 문자열이다(RFC 8693 4.2절의 정의를 따른다).

```python
import jwt
from jwt import PyJWKClient

ISSUER = "https://auth.stg.idp.example"
AUDIENCE = "idp-service-api"          # 예시 값. 실제 aud는 인증 서버 설정을 따른다
jwks = PyJWKClient(f"{ISSUER}/.well-known/jwks.json")   # 키 캐시 내장

def verify_access_token(token: str, required_scope: str) -> str:
    header = jwt.get_unverified_header(token)
    if header.get("typ") not in ("at+jwt", "application/at+jwt"):   # ⓪
        raise Unauthorized("invalid_token")
    key = jwks.get_signing_key_from_jwt(token)     # 헤더의 kid로 키 선택
    claims = jwt.decode(
        token, key.key,
        algorithms=["RS256"],                      # ① 허용 알고리즘을 고정
        issuer=ISSUER,                             # ②
        audience=AUDIENCE,                         # ③
        options={"require": ["exp", "iss", "aud", "sub"]},   # ④ 없으면 거부
        leeway=30,                                 # 서버 간 시계 오차 허용(초). 몇 분 이상 잡지 않는다
    )                                              # ④ exp는 있으면 자동 검사. require가 없으면 exp 없는 토큰이 통과
    scopes = claims.get("scope", "").split()       # ⑤ 공백으로 구분한 문자열
    if required_scope not in scopes:
        raise Forbidden("insufficient_scope")      # 403
    return claims["sub"]
```

`leeway`는 RFC 7519가 허용하는 시계 오차 여유다(보통 몇 분 이하). 서버 시계가 몇 초 어긋나 막 발급된 토큰이 거부되는 일을 막는다. 크게 잡을수록 만료된 토큰을 오래 받아 주므로 짧게 둔다. `audience`, `issuer`, `algorithms`를 라이브러리 설정값으로 넣으면 검증 코드가 거의 남지 않는다. 실패했을 때 돌려줄 응답 형식은 8.6절에 있다. `Unauthorized`, `Forbidden`은 사용하는 웹 프레임워크의 401·403 예외로 바꿔 쓴다. ⓪의 typ 검사는 인증 서버가 RFC 9068 형식으로 발급할 때만 켠다. IdP 인증 서버 access token의 실제 형식은 10.5절의 방법으로 먼저 확인한다.

### 10.2 서명 방식에 따라 검증하는 쪽이 필요한 것

| 인증 서버의 방식 | 검증하는 쪽이 필요한 것 | 평가 |
|---|---|---|
| 비대칭 서명 (RS256·ES256·EdDSA) + JWKS | 공개키 (JWKS에서 자동 수신) | **권장** |
| 대칭 서명 (HS256, 공유 비밀) | 인증 서버와 **같은 비밀** | 비권장. 비밀을 가진 모든 검증자가 토큰을 **위조**할 수도 있게 된다. 검증자가 늘수록 유출면이 커진다 |
| 불투명 토큰 (JWT 아님) | 키 불필요. 요청마다 인증 서버의 introspection 엔드포인트 호출 | 가능하지만 인증 서버가 요청 경로에 들어온다 |

#### 🛡️ 공격: 알고리즘 혼동으로 서명 위조

**공격 원리**: 검증 코드가 토큰 헤더의 `alg`를 그대로 믿는다고 하자. 공격자는 헤더를 `"alg": "HS256"`으로 바꾸고, **공개돼 있는 RS256 공개키**를 HS256의 비밀키처럼 써서 서명을 만든다. 검증 코드가 "HS256이니 이 키로 HMAC 검증"을 하면 통과한다. 비슷한 변종으로 `"alg": "none"`(서명 없음)을 넣어 검증을 건너뛰게 하는 공격도 있다.

OIDC에서는 한 가지가 더 있다. OIDC Core 10.1절은 HS256 같은 대칭 서명의 키로 **client_secret을 UTF-8로 표현한 바이트열**을 쓰도록 정한다. 그래서 인증 서버가 HS256 id_token을 허용하면, 그 client_secret을 아는 쪽(클라이언트 자신이나 secret을 훔친 사람)이 id_token을 만들 수 있게 된다. 같은 절은 public client가 대칭 서명을 쓰는 것을 금지(MUST NOT)한다.

**방어**: 검증하는 쪽이 **허용 알고리즘을 직접 고정**한다(`algorithms=["RS256"]`). 인증 서버도 쓰지 않는 알고리즘은 discovery에 광고하지 않는다.

**방어 원리**: 무엇으로 검증할지를 **공격자가 만든 값(토큰 헤더)이 아니라 검증하는 쪽의 설정**이 정하게 하면, 헤더를 바꿔도 검증 방식이 바뀌지 않는다.

### 10.3 API 앞단(gateway)과 내부 서비스의 역할 분담

IdP 서비스 쪽 구성은 이렇게 잡았다. **인증 서버**는 로그인과 토큰 발급을, **gateway**는 API 앞단을, **코어 서비스**는 요청을 처리하는 Orchestrator 서비스를 맡는다. 코어 서비스는 클라이언트 앱 말고 다른 채널에서도 쓰여야 하므로, 채널과 무관하게 만든다.

#### IdP 인증 서버는 요청 경로에 서 있지 않다

```
                 ┌──────────── 토큰 발급 시(가끔) ────────────┐
클라이언트 앱 서버 ───────┼─► 인증 서버 (IdP 서비스)                           │
   │             │     클라이언트 인증, 사용자 로그인, 토큰 발급   │
   │             │     → token(JWT): sub, aud, client_id, exp  │
   │             └────────────────────────────────────────────┘
   │  ┌──────────── 매 요청(자주) ─────────────────────────────┐
   └──┼─► gateway 또는 서비스의 인증 미들웨어                     │
      │     JWKS로 서명·exp·aud 확인, client_id == 클라이언트 앱 확인     │
      │     → 통과 시 사용자 id만 내부 컨텍스트로                   │
      └─────────────────────── IdP 인증 서버 호출 없음 ──────────────────┘
```

- 채팅 메시지마다 IdP 인증 서버를 거치면 IdP 인증 서버가 **단일 병목이자 단일 장애점**이 된다.
- "토큰을 발급·폐기한다"와 "트래픽을 라우팅하고 검사한다"를 한 서비스에 넣으면 둘 다 바꾸기 어려워진다.
- JWT를 쓰면 검증에 네트워크 호출이 필요 없다. 대신 **폐기가 바로 반영되지 않는다.** refresh token을 폐기해도 이미 발급된 access token은 남은 수명(IdP 인증 서버 기준 최대 60분) 동안 통과한다. 이 공백을 줄이려면 수명을 짧게 두고, 즉시 차단이 꼭 필요하면 introspection(인증 서버에 토큰이 지금 유효한지 묻는 API, RFC 7662) 조회나 폐기 목록을 앞단에 둔다(8.8절).

#### 요청에 실린 두 가지 신원

| 신원 | 질문 | 확인 수단 |
|---|---|---|
| 호출자 신원 | 이 요청이 정말 클라이언트 앱 서버에서 왔는가 | 토큰의 `client_id` claim(이 토큰을 받은 클라이언트, RFC 9068 필수 claim), 선택적으로 mTLS. id_token에서는 같은 역할을 `azp`(authorized party) claim이 한다. IdP 인증 서버의 access token이 RFC 9068 형식이 아니고 클라이언트를 `azp`에 담는다면 그 claim을 대신 본다(형식은 10.5절 방법으로 확인) |
| 사용자 신원 | 어느 IdP 서비스 회원의 요청인가 | 토큰의 `sub` |

**클라이언트 앱의 사용자 인증 토큰은 IdP 서비스로 넘어오지 않는다.** 클라이언트 앱의 로그인은 클라이언트 앱 백엔드 안에서 소비되고 끝난다. IdP 서비스가 확인하는 것은 **IdP 서비스가 발급하거나 등록한** 자격 증명뿐이다.

**호출자에게 토큰을 묶기(sender-constrained)**: 토큰이 유출돼 다른 서버가 쓰는 경우까지 막으려면, 클라이언트 앱 서버와 IdP 서비스 앞단 사이를 mTLS로 연결하고, IdP 인증 서버가 토큰을 발급할 때 클라이언트 앱 인증서의 SHA-256 지문을 토큰에 넣는다. 정확히는 `cnf`(confirmation) claim 안의 `x5t#S256` 항목이다. `cnf` claim은 RFC 7800이, `x5t#S256` 항목은 RFC 8705가 정의한다. 앞단은 "지금 TLS 연결의 인증서 지문 == 토큰의 `cnf.x5t#S256`"을 확인한다. 검사는 TLS가 끝나는 곳에서 한다. AWS에서 흔한 구성처럼 ALB가 TLS를 끝낸다면, ALB의 mTLS 기능을 켜고 뒤의 gateway는 ALB가 넘겨준 인증서 헤더로 `cnf`와 대조한다. 이때 그 헤더를 외부 요청이 직접 넣지 못하게 막아야 한다(15.10).

```json
"cnf": { "x5t#S256": "bwcK0esc3ACC3DB2Y5_lESsXE8o9ltc05O89jdN-dg2" }
```

#### gateway에서만 검사하면 되나, 내부 서비스도 해야 하나

| 확인 항목 | gateway | 코어 서비스 | 이유 |
|---|---|---|---|
| 토큰 서명·만료·발급자·대상(`aud`) | ✅ | ✅ **다시** (아래 방식 중 택 1) | 위조된 신원이 들어오는 것을 막는 마지막 선 |
| 호출자 확인 (`client_id`, mTLS, `cnf`) | ✅ | ❌ | 채널 지식. 코어 서비스는 채널을 몰라야 한다 |
| 호출량 제한, 차단 목록 | ✅ | ❌ | 트래픽 정책은 앞단의 일 |
| 인가 (이 사용자가 이 사례 파일·대화를 볼 수 있는가) | ❌ 못 한다 | ✅ **반드시** | 데이터 소유 관계는 코어 서비스만 안다 |

코어 서비스의 재검증은 **gateway를 우회해서 들어온 요청을 거르는 것**이다. gateway가 `X-User-Id: user-123` 같은 헤더만 붙여 넘기고 코어 서비스가 그 헤더를 그대로 믿으면, 코어 서비스에 직접 닿을 수 있는 누구든 헤더 한 줄로 아무 사용자가 될 수 있다. 막는 방식은 셋 중 하나다.

1. **원본 JWT를 그대로 전달하고 코어 서비스가 같은 JWKS로 다시 검증** (권장). 공개키가 캐시돼 있어 비용이 아주 작고, 새 인프라가 필요 없다.
2. **gateway가 내부용 토큰을 새로 서명해 전달**하고 코어 서비스가 gateway의 공개키로 검증. 외부 토큰 형식이 바뀌어도 코어 서비스가 영향을 받지 않지만, gateway에 서명 키가 생긴다.
3. **네트워크 격리만으로 보장**: 코어 서비스가 gateway에서만 도달 가능한 사설망에 있고 둘 사이를 mTLS로 묶는다. 격리가 유지되는지가 설정에 달려 있어서 1번과 함께 쓰는 편이 안전하다.

#### 토큰을 하위로 흘려보내지 않는다

코어 서비스는 검증을 통과한 뒤 **토큰을 버리고** `sub`와 채널 id만 내부 컨텍스트에 둔다. 하위 Agent나 내부 서비스를 부를 때는 사용자 토큰을 그대로 넘기지(passthrough) 않고, 서비스 자신의 신원으로 호출하면서 사용자 id를 매개변수로 넘긴다. 사용자 명의의 외부 자격 증명이 필요한 작업은 별도 설계(token exchange 또는 사용자가 직접 승인하는 단계)가 필요하다.

### 10.4 id_token을 access token처럼 쓰면 안 되는 이유

```
✅ Authorization: Bearer <access_token>   → 리소스 서버가 검증 후 처리
❌ Authorization: Bearer <id_token>       → 거부해야 함
```

#### 🛡️ 공격: 토큰 종류 혼동

**공격 원리**: 두 토큰 모두 IdP 인증 서버가 RS256으로 서명한 JWT라면, 서명만 검증하는 API는 id_token도 통과시킨다. id_token은 클라이언트에게 주는 신분증이라 클라이언트 쪽 로그·화면·저장소 등 노출되는 경로가 더 많다. 그것으로 API까지 부를 수 있게 되면 피해가 커진다.

**방어**: 두 겹으로 막는다.

- `aud` 검사: id_token의 `aud`는 클라이언트의 client_id이고, access token의 `aud`는 리소스 서버여야 한다.
- `typ` 검사: RFC 9068 형식의 access token은 헤더 `typ`이 `at+jwt`다. 이 형식을 쓰는 리소스 서버는 typ이 `at+jwt`(또는 `application/at+jwt`)가 아닌 토큰을 반드시 거부한다(RFC 9068 4절). id_token의 typ은 보통 `JWT`이므로 여기서 걸러진다.

**방어 원리**: "이 토큰은 누구에게 주려고 발급됐나"를 확인하면, 다른 용도로 발급된 토큰이 진짜 서명을 가졌더라도 거부할 수 있다.

### 10.5 access token이 JWT인지부터 확인한다

access token을 "깔" 수 있으려면 JWT 형식이어야 한다. id_token은 반드시 JWT지만 access token의 형식은 인증 서버가 정한다. 실제 토큰 하나를 받아 점(`.`)으로 나뉜 세 덩어리인지 보면 바로 알 수 있다.

| 형식 | 리소스 서버가 scope를 확인하는 방법 |
|---|---|
| JWT | JWKS 공개키로 서명 검증 후 claim 확인. 인증 서버 호출 없음 |
| 불투명 문자열 | 까 볼 내용이 없다. 요청마다 introspection 엔드포인트(RFC 7662)에 물어본다 |

introspection 응답에서 필수 항목은 `active`(true/false) 하나뿐이다. 만료됐거나, 존재하지 않거나, 조회 권한이 없는 경우가 모두 똑같이 `active: false`로 온다. 인증 서버가 비활성 토큰에 대해 이유를 알려 주지 않도록 권장되기 때문에, false만 보고 원인을 구분할 수는 없다.

```http
POST /introspect
Authorization: Basic base64(resource_server_id:secret)
Content-Type: application/x-www-form-urlencoded

token=at-5f1c…

→ { "active": true, "scope": "openid email", "client_id": "…", "sub": "12345", "exp": 1793003600 }
→ { "active": false }
```

**JWT access token에 개인정보를 넣지 않는다.** JWT 본문은 base64url 인코딩일 뿐이라(9.2절) 토큰을 가진 클라이언트도 내용을 읽을 수 있다. RFC 9068 6절은 클라이언트가 access token 내용을 들여다보지 말라고 하면서도(MUST NOT), 인증 서버 운영자는 그 내용이 클라이언트에게 보인다는 점을 고려하라고 한다. 그래서 이름·전화번호·CI 같은 개인정보는 access token에 넣지 않는다. 꼭 필요하면 토큰을 암호화하거나 불투명 토큰을 쓰고, 리소스 서버가 introspection으로 받게 한다.

### 10.6 audience 제한과 scope 설계

#### 토큰을 특정 API 전용으로: audience와 Resource Indicators

인증 서버 하나가 여러 API(서비스 API, 결제 API, 관리자 API)의 토큰을 발급한다고 하자. 서비스 API용 토큰이 결제 API에서도 통하면, 서비스 API의 로그가 새는 순간 결제까지 위험해진다(15.6.1). 그래서 토큰은 **어느 API용인지(audience, `aud`)**가 정해져 있어야 하고, 각 API는 자기 앞으로 발급된 토큰만 받는다.

클라이언트가 "이 API용 토큰을 달라"고 인증 서버에 알리는 표준이 **Resource Indicators**(RFC 8707)의 `resource` 파라미터다.

```
authorize 요청: …&scope=service&resource=https://service-api.idp.example
token 요청:     …&resource=https://service-api.idp.example
                              │
                              ▼
          access token: { "aud": "https://service-api.idp.example", "scope": "service", … }
          → 결제 API에 내밀면 aud가 달라서 거부
          (인증 서버가 허용하지 않는 resource를 요청하면 invalid_target 오류)
```

```
            ┌─────────────── 같은 사용자, 같은 클라이언트 ───────────────┐
토큰 1  aud=service-api, scope=service        ─► 서비스 API ✅   결제 API ❌
토큰 2  aud=payment-api, scope=payment:read   ─► 서비스 API ❌   결제 API ✅
```

#### scope 설계 원칙

| 원칙 | 예 | 이유 |
|---|---|---|
| 최소 권한 | 서비스 이용만 하는 클라이언트에 `service`만 | RFC 9700 2.3: 권한은 필요한 최소로 (SHOULD) |
| 자원:행위 형태로 이름 짓기 | `service:read`, `service:write`, `filing:submit` | 읽기와 쓰기, 되돌리기 어려운 행위를 나눌 수 있다 |
| 위험한 행위는 별도 scope | `claim:submit`은 따로 두고 재인증과 묶음(14.9) | 일상 토큰이 새도 위험 행위는 못 한다 |
| scope에 사용자 ID·데이터 ID를 넣지 않음 | ❌ `service:user-12345` | scope는 "종류의 권한"이다. 어떤 데이터의 주인인지는 리소스 서버가 판단(10.3절의 인가) |
| OIDC scope와 섞어 생각하지 않기 | `email`은 사용자 정보 권한, `service`는 API 권한 | 9.5절 |

**scope와 audience는 함께 쓴다.** audience는 "**어느 API**용인가", scope는 "그 API 안에서 **무엇을** 할 수 있나"다. 그리고 둘 다 통과해도 "이 사용자가 **이 데이터**의 주인인가"는 리소스 서버가 따로 확인해야 한다.

```
요청: GET /cases/987  Authorization: Bearer <토큰>
  ① aud == 서비스 API?                 (토큰이 이 API용인가)
  ② scope ⊇ service:read?            (이 종류의 일을 할 권한이 있나)
  ③ 사례 987의 주인 == 토큰의 sub?     (이 데이터에 대한 권한이 있나)  ← 토큰만으로는 알 수 없음
```

---

## 11. TLS: 통로를 지키는 것과 지키지 못하는 것

TLS(Transport Layer Security)는 **두 컴퓨터가 주고받는 데이터를 암호화하고, 상대가 진짜 그 서버인지 확인해 주는 보안 통신 규약**이다. 주소가 `https://`로 시작하면 그 연결이 TLS 위에서 이뤄진다는 뜻이다. HTTPS는 "HTTP를 TLS로 감싼 것"이다. 예전 이름은 SSL이다. SSL은 보안 결함으로 모두 폐기됐지만 "SSL 인증서" 같은 말이 관습적으로 남아 있다. 지금 쓰는 버전은 TLS 1.2와 1.3이다.

### 11.1 TLS가 보장하는 세 가지

| 보장 | 의미 | 없으면 생기는 일 |
|---|---|---|
| **기밀성** (암호화) | 중간에서 엿봐도 내용을 읽을 수 없다 | 카페 와이파이에서 client_secret, 토큰이 그대로 보인다 |
| **무결성** | 중간에서 내용을 바꾸면 들킨다 | 응답의 id_token을 공격자가 바꿔치기한다 |
| **서버 인증** | 접속한 상대가 진짜 그 도메인의 주인이다 | `auth.stg.idp.example`인 척하는 가짜 서버에 secret을 보낸다 |

### 11.2 연결을 맺는 과정 (TLS 1.3 핸드셰이크, 단순화)

```
클라이언트 앱 서버                                                   auth.stg.idp.example
   │ ① "TLS로 통신하자" + 지원 암호 방식 + 키 교환 재료 ────────────►│
   │ ② "좋아" + 서버 쪽 키 교환 재료 ◄──────────────────────────────┤
   │    → 양쪽이 같은 세션 키를 계산. 이후 메시지는 모두 암호화
   │ ③ 서버가 보냄 (이미 암호화된 상태)                                │
   │    · 인증서: 도메인 = auth.stg.idp.example, 공개키, 인증기관(CA) 서명
   │    · 지금까지의 대화 내용에 대해 "인증서 비밀키로 만든 서명"
   │ ④ 클라이언트 확인
   │    · 신뢰하는 CA가 인증서에 서명했나? (OS·런타임에 내장된 CA 목록)
   │    · 도메인이 내가 접속하려는 주소와 같나? 만료 전인가?
   │    · ③의 서명이 인증서 속 공개키로 검증되나?   ← 비밀키를 가진 진짜 주인인가
   │    → 하나라도 틀리면 연결 중단
   │◄═══════════════ 이후 모든 데이터 암호화 ═══════════════════════►│
   │   POST /oauth/token/  Authorization: Basic …                   │
```

④가 핵심이다. 인증서는 **신뢰할 수 있는 인증기관(CA, Certificate Authority)**이 "이 공개키의 주인은 auth.stg.idp.example이다"라고 서명해 준 증명서다. 그런데 **인증서 자체는 공개 정보**라서, 진짜 서버에 한 번 접속하면 누구나 받아 갈 수 있고 가짜 서버도 그것을 그대로 내밀 수 있다. 가짜 서버를 거르는 것은 ③의 **서명**이다. 그 서명은 인증서의 비밀키로만 만들 수 있으므로, 비밀키가 없는 가짜 서버는 ④에서 걸러진다(RFC 8446 4.4.3절의 CertificateVerify 메시지).

| 무엇이 | 무엇을 보증하나 |
|---|---|
| CA의 서명 (인증서 안) | "이 공개키의 주인은 이 도메인이다" |
| 서버의 서명 (③) | "지금 대화하는 상대가 그 공개키의 주인이다" |

중간자가 ①②의 키 교환 재료를 자기 것으로 바꿔치기하면 어떻게 될까. ③의 서명 대상인 "지금까지의 대화 내용"에는 ①②의 키 교환 재료가 들어 있다. 그래서 바꿔치기한 대화에 대해서는 진짜 서버의 서명을 얻을 수 없다. 바꾸지 않고 그대로 전달만 하면, 중간자는 세션 키를 계산할 수 없어 내용을 읽지 못한다.

TLS 1.2는 메시지 순서가 조금 다르지만 "비밀키를 가졌다는 것을 증명해야 통과한다"는 원리는 같다. 9.9절에서 "TLS 서버 인증으로 서명 검증을 갈음할 수 있다"고 한 것이 이 세 번째 보장이다.

### 11.3 OAuth에서 TLS가 지키는 구간

| 구간 | TLS가 지키는 것 |
|---|---|
| 클라이언트 앱 서버 → IdP 인증 서버 `/oauth/token/` | client_secret(Basic 헤더), code, verifier, 받은 토큰 |
| 웹뷰 → IdP 인증 서버 로그인 화면 | 사용자 이메일·비밀번호 |
| IdP 서비스 서버 → 클라이언트 앱 제휴사 API | IdP 서비스의 client_secret, client_credentials 토큰 |
| 클라이언트 앱 서버 → IdP 서비스 API | access token, 서비스 이용 내용 |

4.3절에서 "Base64는 암호화가 아니므로 HTTPS 위에서만 보낸다"고 한 것도 TLS가 이 구간들을 암호화하기 때문이다.

### 11.4 mTLS와의 차이

일반 TLS는 **서버만** 인증서를 내밀고 클라이언트는 인증하지 않는다. **mTLS(mutual TLS)**는 클라이언트도 인증서를 내밀어 **양쪽이 서로를 인증**한다. client_secret 대신 클라이언트 인증서로 "나는 클라이언트 앱 서버다"를 증명하는 방식(`tls_client_auth`, 4.2절)과, 토큰을 인증서에 묶는 방식(`cnf`, 10.3절)이 mTLS를 쓴다.

### 11.5 TLS가 지키지 못하는 것

TLS는 **통로**를 지킨다. 통로 양 끝에서 일어나는 일은 지키지 못한다.

```
[클라이언트 앱 프로세스]                                     [IdP 인증 서버]
  웹뷰가 화면에 그린 로그인 폼 ◄═══ TLS로 암호화된 통로 ═══► 로그인 처리
   ▲ 여기서는 이미 복호화된 평문            ▲ 여기서도 평문 (서버 로그 등)
```

- 받은 쪽 서버가 로그에 토큰을 찍으면, TLS와 무관하게 샌다.
- 연결의 한쪽 끝이 **다른 회사 앱 안의 웹뷰**라면, 웹뷰가 복호화해 화면에 그린 내용에 그 앱이 접근할 수 있다(12.2절).

---

## 12. 네이티브 앱(모바일·데스크톱·CLI)에서 로그인 화면 띄우기

클라이언트가 네이티브 앱일 때, IdP 인증 서버 로그인 화면을 **어떤 그릇에 담아 보여 주느냐**가 보안을 크게 좌우한다.

### 12.1 세 가지 그릇

```
[A] 시스템 브라우저 시트          [B] 웹뷰 최상위 문서            [C] 웹뷰 안의 iframe
┌───────────────────────┐      ┌───────────────────────┐      ┌───────────────────────┐
│ OS 브라우저 프로세스      │      │ 호스트 앱 프로세스        │      │ 호스트 앱 프로세스        │
│ ┌───────────────────┐ │      │ ┌───────────────────┐ │      │ ┌───────────────────┐ │
│ │ IdP 인증 서버 로그인 화면    │ │      │ │ IdP 인증 서버 로그인 화면    │ │      │ │ 호스트 페이지        │ │
│ │                   │ │      │ │ (주소가 IdP 인증 서버로 이동)│ │      │ │ ┌───────────────┐ │ │
│ └───────────────────┘ │      │ └───────────────────┘ │      │ │ │ IdP 인증 서버 로그인    │ │ │
│ 호스트 앱은 안을 못 봄    │      │ 호스트 앱이 띄운 웹뷰     │      │ │ └───────────────┘ │ │
└───────────────────────┘      └───────────────────────┘      │ └───────────────────┘ │
                                                             └───────────────────────┘
표준이 권하는 방식               연동 규격이 정한 방식             IdP 인증 서버가 거부
```

| | A. 시스템 브라우저 | B. 웹뷰 최상위 | C. 웹뷰 안 iframe |
|---|---|---|---|
| 누가 화면을 그리나 | OS 브라우저 | 호스트 앱의 웹뷰 | 호스트 앱 웹뷰, 그 안의 프레임 |
| 주소창의 도메인 | IdP 인증 서버 (사용자에게 보임) | IdP 인증 서버 (보통 사용자에게 안 보임) | 호스트 도메인 그대로 |
| 호스트 앱이 입력을 볼 수 있나 | ❌ | ⚠️ 기술적으로 가능 | ⚠️ 가능 |
| 쿠키·세션 | 시스템 브라우저와 공유(iOS는 만료 시각이 있는 쿠키만). 이미 로그인했으면 바로 통과할 수 있음 | 앱 전용 저장소. 자주 재로그인 | 서드파티 쿠키로 취급돼 깨지기 쉬움 |
| Google 로그인 | 동작 | 차단됨 | 차단됨 |

**A의 구현 이름**: iOS는 `ASWebAuthenticationSession`, Android는 Custom Tabs다. 둘 다 앱 안에서 시트처럼 뜨지만, iOS는 Safari 쪽 별도 프로세스가, Android는 사용자의 기본 브라우저 앱(Chrome, 삼성 인터넷 등)이 그린다. 어느 쪽이든 호스트 앱 프로세스 밖이다.

**"웹뷰 최상위 화면"은 시스템 브라우저가 아니다.** 앱이 직접 띄운 웹뷰가 화면 전체로 IdP 인증 서버 페이지를 여는 것이다. 규격이 "iframe 아님"이라고 구분한 것은 B와 C의 차이다.

### 12.2 웹뷰에서 호스트 앱이 할 수 있는 것

```
호스트 앱 프로세스
┌──────────────────────────────────────────────────────┐
│  호스트 앱 코드                                          │
│    │ ① 페이지에 JS 주입 (Android evaluateJavascript,     │
│    │    iOS WKUserScript)                              │
│    │    → document.querySelector('input[type=password]').value 읽기
│    │ ② 쿠키 저장소 접근 (CookieManager / WKHTTPCookieStore)│
│    │    → IdP 인증 서버 로그인 세션 쿠키 읽기                       │
│    │ ③ 페이지 이동 감시 → redirect URL의 code 읽기         │
│    ▼                                                   │
│  ┌─ 웹뷰 ──────────────────────────────┐               │
│  │  IdP 인증 서버 로그인 화면 (TLS로 받아 복호화된 상태) │               │
│  │  [ 이메일    ] [ 비밀번호 ] [로그인]     │               │
│  └────────────────────────────────────┘               │
└──────────────────────────────────────────────────────┘
        ▲ TLS는 여기(네트워크 구간)까지만 보호
```

#### 🛡️ 공격: 내장 웹뷰를 통한 자격 증명 탈취

**공격 원리**: 웹뷰는 호스트 앱 프로세스 안에서 돌아가는 브라우저다. 앱 코드나, 앱에 포함된 제3자 SDK(분석·광고 등)는 웹뷰 페이지에 스크립트를 넣어 입력 중인 이메일·비밀번호를 읽거나, 쿠키 저장소에서 IdP 인증 서버 로그인 세션을 꺼낼 수 있다. TLS는 이미 복호화된 화면 안의 값을 지키지 못한다. 세 번째(code)는 원래 클라이언트가 받을 값이라 문제가 아니다. 문제는 **비밀번호가 이 연동 밖에서도 쓰이는 값**이라는 점이다. 사용자는 IdP 서비스 웹에 직접 로그인할 때도 같은 비밀번호를 쓰고, 다른 서비스와 같은 비밀번호를 쓰는 사용자도 많다.

**표준의 방어**: OAuth 모바일 앱 표준(RFC 8252)은 네이티브 앱이 OAuth 인증 요청에 **앱 내장 브라우저(embedded user-agent)를 쓰면 안 되고(MUST NOT), 외부 브라우저를 써야 한다(MUST)**고 정한다(RFC 8252 8.12절·4절). RFC 8252는 웹뷰를 내장 브라우저의 흔한 구현으로 설명한다. 인증 서버가 내장 브라우저에서 온 요청을 탐지해 막는 것도 허용(MAY)한다. Google이 웹뷰 로그인을 막는 것이 그 예다.

**방어 원리**: 시스템 브라우저는 OS가 관리하는 **별도 프로세스**라서, 호스트 앱이 그 안의 DOM(브라우저가 페이지를 다루는 객체 구조)이나 쿠키에 접근할 수 없다. 호스트 앱이 받는 것은 마지막 콜백 URL 하나뿐이다. "호스트 앱을 믿느냐"의 문제를 "호스트 앱이 볼 수 없는 구조"로 바꾼다.

**위험의 현실적 평가**

| 고려 요소 | 판단 |
|---|---|
| 호스트 앱이 악의적으로 읽을 가능성 | 계약 관계의 대형 파트너라면 낮다. 그렇게 하면 법적 책임이 크다 |
| 호스트 앱이 침해되거나, 앱에 붙은 제3자 SDK가 웹뷰에 스크립트를 넣을 가능성 | **낮지 않다** |
| 감사·인증 관점 | "제휴사 앱이 우리 회원 비밀번호에 접근할 수 없다"고 말할 수 없다. 개인정보 처리방침과 보안 심사에서 설명이 필요해진다 |

이 문제는 "파트너를 믿느냐"보다 **"비밀번호가 호스트 앱을 거칠 수 있는 구조를 받아들이느냐"**의 문제다. 대응 선택지는 보통 세 가지다. 시스템 브라우저로 바꾸도록 협의하기, 웹뷰 채널에서는 비밀번호 대신 이메일 일회용 코드처럼 재사용할 수 없는 값으로 로그인하게 하기, 계약·규격에 스크립트 주입과 쿠키 접근 금지를 명시하기다. 이 연동 사례에서 어느 쪽을 택할지는 별도로 정해야 한다(16.12절).

참고로 **PC 브라우저로 들어오는 사용자는 이 문제가 없다.** 그 경우 "웹뷰 최상위"는 일반 브라우저의 최상위 탭이라 시스템 브라우저와 같다. 문제는 모바일 앱의 내장 웹뷰에 한정된다.

#### 🛡️ 공격: 가짜 브라우저와 로그인 페이지 피싱

🎯 **노리는 것**: 사용자 비밀번호.

🧨 **공격 원리**: OAuth는 사용자에게 "앱을 쓰다가 다른 화면으로 넘어가 비밀번호를 입력하는" 습관을 들인다. 공격자는 바로 그 습관을 노린다. OAuth 2.1 초안 7.8절과 8.5절이 다루는 모양은 세 가지다.

```
① 가짜 로그인 페이지      진짜와 똑같이 꾸민 페이지로 유인해 비밀번호를 받음
② 시스템 브라우저 흉내     네이티브 앱이 내장 웹뷰에 가짜 주소 표시줄까지 그려 넣어
                         시스템 브라우저 시트처럼 보이게 함 (12.2의 탈취와 결합)
③ 기본 브라우저 바꿔치기   악성 앱이 기기의 기본 브라우저로 설정돼,
                         다른 앱이 연 "시스템 브라우저" 자체가 악성 앱이 됨
```

🛡️ **방어**

- 인증 서버는 **피싱에 강한 인증 수단**(패스키·WebAuthn)을 제공한다.
- 앱은 진짜 시스템 브라우저를 쓰고, 사용자가 주소를 확인할 수 있게 한다.
- 사용자 교육: 로그인 화면의 주소를 확인하는 습관.

💡 **방어 원리**: 비밀번호는 어디에 입력되는지 스스로 알지 못한다. 가짜 화면에 넣어도 똑같이 쓸 수 있다. 패스키는 브라우저가 **실제 접속한 도메인**을 넣어 서명하므로, ①처럼 가짜 도메인에서는 진짜 도메인용 인증이 만들어지지 않는다. ②처럼 앱의 웹뷰가 진짜 IdP 인증 서버 주소를 여는 경우에는, 진짜 외부 브라우저에서만 쓸 수 있는 인증 수단을 요구하는 것이 방어가 된다(OAuth 2.1 초안 8.5.2절). 다만 패스키가 지키는 것은 **자격 증명**뿐이다. ②·③처럼 공격자가 브라우저 자체를 쥐고 있으면, 로그인이 끝난 뒤의 세션 쿠키와 code는 여전히 가져갈 수 있다(위의 내장 웹뷰 탈취). 또 동의 피싱(7.8절)은 **진짜 도메인**에서 일어나므로 패스키로도 막지 못한다.

### 12.3 iframe은 왜 막히나

IdP 인증 서버 로그인 화면은 iframe 삽입을 거부하도록 만들어져 있다. 이유는 두 가지다.

첫째는 **클릭재킹** 방지다. 인증 서버의 로그인·동의 화면을 다른 페이지 안에 몰래 겹쳐 놓는 공격이라, 동의 화면과 함께 7.8절에서 자세히 다룬다. IdP 인증 서버는 프레임 삽입 자체를 막는다.

**두 번째 이유는 쿠키다.** iframe 안의 IdP 인증 서버는 상위 페이지(`client.example`)와 **사이트**(등록 가능한 도메인)가 다르므로 IdP 인증 서버 쿠키가 **서드파티 쿠키**가 된다. Android WebView(Android 5.0 이상을 대상으로 하는 앱)와 iOS WKWebView(iOS 14 이상)는 서드파티 쿠키를 기본으로 막는다. 그래서 클라이언트 앱 웹뷰 안의 iframe에서는 IdP 인증 서버 로그인 세션이나 state 확인이 깨진다. Safari도 기본으로 막고, Firefox는 사이트마다 쿠키 저장소를 따로 나눈다. 데스크톱 Chrome은 2026년 현재 기본 허용이지만 사용자가 끌 수 있으므로, 브라우저에서도 iframe 로그인에 기대지 않는다.

그래서 이 연동은 서비스 화면은 iframe으로 보여 주되, **로그인만큼은 웹뷰 전체를 IdP 인증 서버로 이동시켰다가** 끝나면 redirect_uri로 돌아오는 구조가 됐다.

```
클라이언트 앱 웹뷰
  ① app.client.example/… (클라이언트 앱 화면)
  ② 최상위 문서를 IdP 인증 서버 /oauth/authorize/ 로 이동   ← 이때 화면 전체가 IdP 인증 서버 로그인
  ③ 로그인 완료 → 302 → app.client.example/authorize/oauth2/code/idp
  ④ 다시 클라이언트 앱 화면 → 서비스 iframe 로드
```

### 12.4 앱으로 돌아오기: Universal Links·App Links와 custom scheme

시스템 브라우저로 로그인했다면, 콜백 URL이 **앱으로** 돌아와야 한다. 받는 방식은 두 OS가 다르다. iOS는 `ASWebAuthenticationSession`이 콜백 URL을 **직접 가로채** 앱에 넘기고 시트를 닫는다. Android는 OS가 App Links 선언을 보고 "이 주소는 이 앱 것"이라고 판단해 앱을 연다.

| 역할 | iOS | Android |
|---|---|---|
| 브라우저 시트 | `ASWebAuthenticationSession` (Safari 엔진) | Custom Tabs (기본 브라우저 엔진) |
| https 콜백을 앱이 받는 방식 | 세션이 콜백을 직접 가로챈다. https 콜백은 iOS 17.4 이상에서 `.https(host:path:)`로 지정하고, 그 host를 앱의 associated domain으로 등록(도메인의 `apple-app-site-association` 파일). 17.4 미만은 custom scheme만 | App Links: 도메인의 `assetlinks.json` 파일로 "이 주소는 이 앱 것"이라고 선언 |
| 콜백 URL을 앱에 전달 | 세션의 completion handler 호출, 시트 자동 닫힘 | 콜백 Activity를 Intent로 실행 (시트는 앱이 정리) |

#### 🛡️ 공격: custom scheme 가로채기

**공격 원리**: custom scheme(`clientapp://cb/idp` 같은 것)은 여러 앱이 같은 이름을 등록할 수 있다. 그래서 **OS가 URL을 보고 앱을 골라 넘겨주는 방식**(Android의 intent, iOS에서 Safari가 여는 딥링크)에서는 어느 앱이 받을지 정해지지 않고(RFC 8252 8.1절), 같은 scheme을 등록한 악성 앱이 code를 받을 수 있다. 반면 iOS의 `ASWebAuthenticationSession`은 세션이 콜백을 직접 가로채므로, 같은 scheme을 등록한 앱이 있어도 호출한 앱만 받는다.

**방어**: https 기반의 Universal Links·App Links로 콜백을 받는다. 그리고 PKCE를 쓴다(7.3절).

**방어 원리**: https 링크는 **도메인 주인이 자기 도메인에 올린 파일로 "이 앱만 이 주소를 연다"고 선언**해야 OS가 앱으로 넘긴다. 악성 앱은 그 도메인에 파일을 올릴 수 없다. 혹시 code가 새더라도 PKCE 원본값이 없으면 토큰으로 바꿀 수 없다.

IdP 인증 서버는 앱 전용 scheme(`clientapp://…` 같은 형태)을 redirect_uri로 등록하지 않는다. 앱에서도 콜백은 클라이언트 서버의 https 주소로 받는다.

**앱 쪽 코드는 이 정도다.**

```swift
// iOS 17.4 이상: https 콜백을 직접 지정할 수 있다
let session = ASWebAuthenticationSession(
    url: authorizeURL,                                   // 클라이언트 서버가 만들어 준 authorize URL
    callback: .https(host: "client.example", path: "/cb/idp")
) { callbackURL, error in
    // https://client.example/cb/idp?code=abc&state=… 가 들어옴
    guard let url = callbackURL,
          let items = URLComponents(url: url, resolvingAgainstBaseURL: false)?.queryItems
    else { return }                                       // error가 canceledLogin이면 사용자가 닫은 것
    let code  = items.first { $0.name == "code" }?.value
    let state = items.first { $0.name == "state" }?.value
    backend.completeLink(code: code, state: state)        // 서버로 넘겨 토큰 교환
}
session.presentationContextProvider = self
session.start()                                           // 시트가 올라옴
```

iOS 17.4보다 낮은 버전의 `ASWebAuthenticationSession`은 custom scheme 콜백(`callbackURLScheme: "clientapp"`)만 받는다. 그래서 낮은 버전까지 지원하려면, 인증 서버의 redirect_uri는 https 서버 주소로 두고 그 서버가 처리를 마친 뒤 앱의 scheme으로 한 번 더 이동시키는 식의 우회가 필요하다(지원 OS 범위는 앱 팀과 확인 필요).

```kotlin
// Android
CustomTabsIntent.Builder().build()
    .launchUrl(activity, authorizeUri)        // 시트가 올라옴
// App Link로 등록된 https://client.example/cb/idp 가 열리면
// 해당 Activity의 onNewIntent에서 code, state를 읽어 서버로 보냄
```

### 12.5 돌아오기 처리에서 흔한 실수

| 실수 | 증상 | 대응 |
|---|---|---|
| Android Custom Tab이 뒤로 가기 스택에 남음 | 로그인 후 뒤로 가기를 누르면 로그인 페이지가 다시 나타남 | 콜백 Activity를 `singleTask`로 두거나 `FLAG_ACTIVITY_CLEAR_TOP`으로 띄운다 |
| 사용자가 시트를 그냥 닫은 경우를 처리 안 함 | 앱이 로딩 상태로 멈춤 | iOS는 `canceledLogin` 오류, Android는 콜백 없이 복귀. "연결 안 됨" 상태로 처리하고 다시 시작할 수 있게 한다 |
| 콜백 URL이 등록값과 글자 단위로 다름 | IdP 인증 서버 화면에 오류가 뜨고 돌아오지 않음 | 환경별 주소를 모두 등록. 끝의 `/`, 포트, http/https까지 일치 |
| 인증 서버가 실패를 콜백으로 안 돌려보냄 | 시트가 닫히지 않아 사용자가 갇힌 것처럼 보임 | 인증 서버는 실패·취소도 `error` 파라미터를 붙여 콜백으로 302 |

**iOS는 기본 모드에서 시트를 열기 전에 시스템 확인창을 한 번 띄운다**("…이(가) 로그인하기 위해 example.com을 사용하려고 합니다"). Safari와 쿠키를 공유하기 때문에 묻는 것이다. `prefersEphemeralWebBrowserSession = true`(비공개 세션)로 열면 확인창이 뜨지 않지만, Safari와 쿠키를 공유하지 않아 이미 로그인한 사용자도 다시 로그인해야 한다. 어느 쪽을 쓸지 디자인 검토 때 함께 정한다. Android Custom Tabs는 확인창 없이 바로 열린다.

### 12.6 데스크톱·CLI 앱: loopback redirect

데스크톱 앱이나 CLI 도구는 https 앱 링크로 결과를 받기 어렵다. 이때는 앱이 **자기 컴퓨터에서 잠깐 작은 웹 서버를 열고** 그 주소로 결과를 받는다(RFC 8252 7.3절, OAuth 2.1 초안 8.4.2절).

```
CLI 도구                          시스템 브라우저                       인증 서버
  │ ① 비어 있는 포트를 골라                │                                │
  │    http://127.0.0.1:51004/callback 에서 대기 (이 컴퓨터 안에서만 열림)    │
  │ ② 브라우저로 authorize 열기 ─────────►│ redirect_uri=http://127.0.0.1:51004/callback
  │                                     │ + state + PKCE ──────────────►│
  │                                     │ ③ 로그인·동의                    │
  │                                     │◄── 302 http://127.0.0.1:51004/callback?code=…&state=…
  │◄──── ④ 브라우저가 로컬 서버로 요청 ─────┤                                │
  │    code 꺼냄, 브라우저에 "로그인 완료. 창을 닫아도 됩니다" 표시, 로컬 서버 종료  │
  │ ⑤ POST /token (code + code_verifier) ─────────────────────────────►│
  │◄─────────────────────────────────── 토큰 ───────────────────────────┤
```

| 규칙 | 근거 |
|---|---|
| `localhost`라는 이름 대신 `127.0.0.1`(또는 `[::1]`) IP를 쓴다. 이름은 다른 주소로 풀릴 수 있다 | RFC 8252 8.3절 (localhost NOT RECOMMENDED) |
| 인증 서버는 loopback 주소의 **포트만** 달라도 받아 준다. 나머지는 정확히 일치 | RFC 8252 7.3절, OAuth 2.1 초안 2.3.1절 |
| http를 허용하는 것은 loopback 주소뿐이다 | RFC 9700 2.6절 |
| 로컬 서버는 loopback 인터페이스에만 열고, 인가 요청을 시작할 때 열었다가 응답을 받으면 바로 닫는다 | RFC 8252 8.3절, OAuth 2.1 초안 8.5.4절 (SHOULD). 같은 네트워크의 다른 기기가 끼어들지 못하게 |
| public client이므로 PKCE 필수 | 7.3절 |

브라우저조차 띄울 수 없는 서버 터미널이라면 Device Authorization Grant(14.5)를 쓴다.

### 12.7 채팅 화면 전체를 웹뷰로 띄우는 구조와 비교

로그인만이 아니라 **서비스 화면 전체**를 호스트 앱의 웹뷰로 띄우면, 인증 연동 자체가 사라진다. 호스트 앱은 IdP 서비스 토큰을 받지도 저장하지도 않는다. 대신 호스트 앱이 신경 쓸 것이 "토큰 관리"에서 "웹뷰 환경 보장"으로 바뀐다.

| 항목 | IdP 서비스 (웹 앱 + 백엔드) | 호스트 앱 |
|---|---|---|
| 로그인·세션 | 전부 IdP 서비스 소관 | 관여 없음 |
| 세션 유지 | HttpOnly(스크립트 접근 차단)·Secure(HTTPS에서만 전송)·SameSite(다른 사이트 요청에 쿠키를 싣는 범위) 쿠키, 만료 정책 | 웹뷰 저장소를 영구로 설정. 비영구면 앱을 껐다 켤 때마다 로그인 |
| 소셜 로그인 | 리다이렉트 흐름 구현 | 외부 IdP 로그인은 웹뷰에서 막히는 경우가 있어, 시스템 브라우저로 열었다 돌아오는 처리가 필요 |
| 파일 첨부 | `<input type="file">` | Android WebView는 호스트 앱이 file chooser를 구현해야 동작 |
| 로그아웃 | IdP 서비스 화면의 로그아웃 | 호스트 계정 전환 시에도 IdP 서비스 웹뷰 세션은 기기에 남음 |
| 푸시 알림 | 웹뷰는 못 받음 | 호스트 푸시를 빌리면 사용자 식별 연동이 다시 필요 |
| JS bridge (웹뷰의 JS가 앱의 네이티브 함수를 부르는 통로) | — | 노출한다면 IdP 서비스 도메인만 허용 |

---

## 13. 브라우저 앱(SPA)과 BFF 패턴

React·Vue처럼 화면 대부분이 브라우저의 JavaScript로 돌아가는 앱을 **SPA**(Single Page Application)라고 한다. SPA는 OAuth 클라이언트로서 가장 다루기 까다롭다. 이 장은 2026년 8월 발행된 브라우저 앱 OAuth 모범 사례 **RFC 10017**(BCP 212, 모바일 앱의 RFC 8252와 같은 묶음)을 따른다.

### 13.1 SPA가 어려운 이유

| 문제 | 무슨 뜻인가 |
|---|---|
| 비밀을 둘 곳이 없다 | JS 번들은 누구나 내려받아 읽을 수 있다. client_secret을 넣으면 공개된 것과 같다. 그래서 SPA는 public client다 |
| XSS에 노출된다 | 페이지에 악성 스크립트가 한 줄이라도 들어오면(XSS, Cross-Site Scripting), 그 스크립트는 앱과 **같은 권한**으로 돈다. 앱이 읽을 수 있는 토큰은 공격자도 읽는다 |
| 브라우저 저장소는 모두 같은 origin에 열려 있다 | localStorage, sessionStorage는 같은 origin의 모든 스크립트가 읽는다 |

### 13.2 먼저 알아 둘 웹 보안 기초

브라우저 앱의 보안은 브라우저가 지키는 몇 가지 경계 위에 서 있다. 이 장을 읽기 전에 네 가지를 짚는다.

**① origin과 site는 다르다**

| 개념 | 무엇으로 정해지나 | 예 |
|---|---|---|
| origin | scheme + 호스트 + 포트 | `https://auth.idp.example.com:443` |
| site | scheme + 등록 가능한 도메인 (eTLD+1) | `https://example.com` |

eTLD(공개 접미사)는 `com`, `kr`, `co.kr`처럼 누구나 그 아래에 도메인을 등록할 수 있는 부분이다. eTLD+1은 그 바로 아래 한 칸까지다. 예: `auth.idp.example.com`의 site는 `example.com`, `www.example.co.kr`의 site는 `example.co.kr`.

```
https://auth.idp.example.com   vs  https://www.idp.example.com   → origin 다름, site 같음 (같은 example.com)
https://www.idp.example.com    vs  https://app.client.example.com     → origin도 site도 다름
http://www.idp.example.com     vs  https://www.idp.example.com   → scheme이 달라 origin도 site도 다름
```

브라우저는 **origin** 단위로 JS를 격리한다(same-origin policy). origin A의 JS는 origin B의 응답이나 저장소(localStorage 등)를 읽지 못한다. 반면 쿠키의 `SameSite`와 "서드파티 쿠키"는 **site** 단위로 판단한다. 같은 회사의 하위 도메인끼리는 같은 site라서, 한 하위 도메인이 뚫리면 다른 하위 도메인으로 가는 요청에 쿠키가 실릴 수 있다.

**② 쿠키 속성**

| 속성 | 뜻 |
|---|---|
| `Secure` | HTTPS 요청에만 실린다 |
| `HttpOnly` | JS(`document.cookie`)가 읽을 수 없다. XSS가 쿠키 값을 훔치는 것을 막는다 |
| `SameSite=Strict` | 같은 site에서 시작한 요청에만 실린다. 다른 사이트의 링크를 눌러 들어와도 안 실린다 |
| `SameSite=Lax` | 같은 site 요청, 그리고 다른 사이트에서 온 **최상위 이동 중 GET**(링크 클릭 등)에 실린다. 다른 사이트에서 보낸 폼 POST, 이미지·iframe·fetch 같은 하위 요청에는 안 실린다 |
| `SameSite=None` | 다른 사이트에서 시작한 요청에도 실린다. `Secure`가 함께 있어야 한다. 단 브라우저의 서드파티 쿠키 차단(12.3절)이 켜져 있으면 다른 사이트 안의 iframe 등에서는 여전히 막힌다 |
| `Domain`, `Path` | 쿠키가 실릴 도메인과 경로 범위. `Domain`을 생략하면 그 호스트에만 실린다 |
| `__Host-` 이름 접두어 | 브라우저가 `Secure`, `Path=/`, `Domain` 없음을 강제한다 |

**③ CORS (Cross-Origin Resource Sharing)**

origin A의 JS가 origin B의 API를 부를 때, B가 응답에 `Access-Control-Allow-Origin`으로 A를 허락해야 JS가 응답을 읽는다. 요청 모양에 따라 순서가 다르다. 커스텀 헤더를 붙이거나 `Content-Type`이 `application/json`처럼 폼 전송이 쓰지 않는 값이면, 브라우저가 먼저 `OPTIONS` 요청(preflight)으로 허락을 받고, 허락이 없으면 본 요청을 아예 보내지 않는다. 반대로 GET이나 폼 전송과 같은 모양(`Content-Type`이 `application/x-www-form-urlencoded`, `multipart/form-data`, `text/plain`)인 요청은 preflight 없이 바로 간다. 이때는 **응답은 못 읽어도 서버 쪽 동작은 일어날 수 있다.** 본문이 JSON이어도 `Content-Type: text/plain`으로 보내면 preflight가 생기지 않으므로, "JSON API라서 CSRF에 안전하다"고 가정하지 않는다. CORS는 "읽기"를 막는 장치이지 "요청 자체"를 막는 장치가 아니다. 그래서 RFC 10017은 BFF가 CORS를 CSRF 방어로 쓸 때 모든 요청에 커스텀 헤더를 요구하라고 한다(SHOULD, 6.1.3.3.2절).

**④ CSRF는 두 가지가 있다**

| | OAuth redirect CSRF | 일반 웹 CSRF |
|---|---|---|
| 노리는 곳 | 클라이언트의 callback 주소 | 쿠키로 인증하는 API (BFF 등) |
| 공격 | 공격자의 code를 피해자 세션에 끼워 넣음 | 피해자 브라우저가 쿠키를 실어 상태 변경 요청을 보내게 함 |
| 방어 | state, PKCE, nonce (7.2절) | SameSite 쿠키, CSRF 토큰, 커스텀 헤더 + CORS (13.6절) |

이 장에서 말하는 CSRF는 주로 두 번째다.

### 13.3 세 가지 구조

RFC 10017은 SPA가 OAuth를 쓰는 구조를 세 가지로 나누고, 보안이 강한 순서로 설명한다.

```
[구조 1] BFF (Backend for Frontend)                      ← 가장 권장
 브라우저(SPA JS) ──쿠키(HttpOnly)──► BFF (같은 origin의 서버) ──access token──► 리소스 서버
                                       │  ▲
                                       ▼  │ code + PKCE + client 인증 (confidential client)
                                     인증 서버
 토큰은 전부 BFF 서버에. 브라우저에는 세션 쿠키만.

[구조 2] Token-Mediating Backend
 브라우저(SPA JS) ──access token──────────────────────────────────────► 리소스 서버
        ▲ access token만 내려받음
 백엔드 ── code 교환, refresh token 보관 (confidential client) ──► 인증 서버
 access token은 브라우저에, refresh token은 서버에.

[구조 3] Browser-based OAuth Client
 브라우저(SPA JS) ── code + PKCE ──► 인증 서버
        └── access token ─────────────────────────────────────────────► 리소스 서버
 모든 토큰이 브라우저에. public client.
```

| | BFF | Token-Mediating Backend | Browser-based Client |
|---|---|---|---|
| access token 위치 | 서버 | **브라우저** | 브라우저 |
| refresh token 위치 | 서버 | 서버 | 브라우저 |
| 클라이언트 종류 | confidential | confidential | public |
| XSS가 토큰을 훔칠 수 있나 | ❌ (브라우저에 없음) | access token은 가능 | 둘 다 가능 |
| 리소스 서버 호출 경로 | BFF가 중계 | 브라우저가 직접 | 브라우저가 직접 |
| RFC 10017의 평가 | 업무용·민감·개인정보를 다루는 앱에 **강력 권장** | BFF보다 약하지만 브라우저 단독보다 낫다. 택하기 전에 BFF가 가능한지 먼저 검토하라고 강하게 권함 | 업무용·민감·개인정보를 다루는 앱에는 **권장하지 않음** |

### 13.4 XSS가 토큰에 하는 일

SPA 보안 논의는 대개 "토큰을 어디에 저장하느냐"로 흐른다. RFC 10017은 그보다 **XSS 공격자가 무엇을 할 수 있느냐**부터 보라고 한다(RFC 10017 5.1절). 시나리오가 넷이다.

```
[시나리오 1] 단발 탈취
  악성 스크립트 → 저장소에서 access/refresh token 읽기 → 공격자 서버로 전송
  → 막는 방법: 토큰을 스크립트가 못 읽는 곳에 두기

[시나리오 2] 지속 탈취
  악성 스크립트가 계속 살아 있으면서 갱신될 때마다 최신 토큰을 빼냄
  refresh rotation도 소용없음: 공격자가 앱의 토큰을 지우거나 사용자가 앱을 닫기를 기다리면
  앱이 그 refresh token을 다시 쓰지 않으므로 재사용이 일어나지 않아 탐지되지 않음

[시나리오 3] 새 흐름 실행  ← 가장 중요
  악성 스크립트가 저장소를 건드리지 않고, 숨긴 iframe으로 직접 authorize → code → token 흐름을 돌림
  사용자가 이미 인증 서버에 로그인돼 있으면 화면 없이 새 토큰 세트를 받음
  인증 서버 입장에서는 정상 앱의 흐름과 구별할 수 없음

[시나리오 4] 사용자 브라우저를 통한 요청 중계
  토큰을 훔치지 않고, 사용자 브라우저에서 앱처럼 API를 직접 부름 (쿠키·토큰은 앱이 알아서 붙임)
  사용자가 페이지를 열어 둔 동안만 가능
```

시나리오 3에서 악성 스크립트는 redirect_uri가 앱과 같은 origin이라는 점을 이용해, iframe의 주소를 읽어 code를 꺼낸다(RFC 10017 5.1.3절). 인증 서버가 iframe 삽입을 막아도(12.3절의 IdP 인증 서버처럼) 공격자는 팝업 창으로 같은 흐름을 돌릴 수 있어서, iframe 차단은 근본 대책이 아니다(RFC 10017 6.3.4.2.3절).

**시나리오 3이 핵심이다.** 토큰을 아무리 잘 숨겨도, 브라우저 안에서 OAuth 클라이언트 노릇을 하는 코드가 장악되면 공격자는 **새 토큰을 직접 받아 간다.** 저장 위치를 바꾸는 것으로는 막을 수 없다. 그래서 BFF가 권장된다. BFF 구조에서는 토큰 교환에 서버의 client 인증이 필요하므로, 브라우저의 악성 스크립트가 흐름을 돌려도 토큰을 받을 수 없다. 남는 것은 시나리오 4, 곧 **사용자 브라우저가 열려 있는 동안 BFF를 통해 요청을 보내는 것**뿐이다. 이것은 OAuth와 무관하게 XSS가 원래 할 수 있는 일이라서, 콘텐츠 보안 정책(CSP)이나 입력값 처리 같은 일반적인 XSS 방어로 막는다.

| 시나리오 | 저장 위치를 숨기면 | BFF로 바꾸면 |
|---|---|---|
| 1 단발 탈취 | 일부 막음 | 막음 (브라우저에 토큰 없음) |
| 2 지속 탈취 | 일부 막음 | 막음 |
| 3 새 흐름 실행 | 못 막음 | 막음 (토큰 교환에 서버의 client 인증 필요) |
| 4 요청 중계 | 못 막음 | 못 막음 (XSS 자체를 막아야 함) |

### 13.5 토큰 저장 위치 비교 (브라우저에 둘 수밖에 없을 때)

| 저장 위치 | 노출 정도 | 특징 |
|---|---|---|
| JS 메모리 (변수, 클로저) | 같은 실행 환경의 스크립트가 접근할 수 있음 | 새로고침하면 사라짐 |
| Web Worker | 메인 스레드 스크립트가 직접 못 읽음. 상대적으로 격리됨 | 구현이 복잡 |
| sessionStorage | 같은 origin·같은 탭의 스크립트가 읽음 | 탭을 닫으면 사라짐 |
| localStorage | 같은 origin의 **모든** 스크립트가 읽음 | 오래 남고 모든 탭이 공유 |
| JS로 쓴 쿠키 | 같은 origin 스크립트가 읽고, 요청마다 서버로 따라감 | RFC 10017: NOT RECOMMENDED |

**흔한 오해 바로잡기**: RFC 10017에 "localStorage에 저장하면 안 된다(MUST NOT)"는 금지 문장은 없다. 문서가 말하는 것은 두 가지다. localStorage는 같은 origin에서 도는 악성 스크립트가 그대로 읽을 수 있다. 그리고 **어떤 저장 위치도 악성 코드가 앱 안에서 실행될 때의 토큰 유출을 완전히 막지 못한다.** 저장 위치는 노출 정도를 줄이는 문제이고, 근본 해결은 구조(BFF)다.

### 13.6 BFF를 만들 때 지킬 것

BFF는 브라우저와 **세션 쿠키**로 대화한다. 그 쿠키가 곧 사용자 권한이므로 규칙이 엄격하다(RFC 10017 6.1.3).

| 규칙 | 강도 | 이유 |
|---|---|---|
| `Secure` | MUST | HTTPS로만 전송 |
| `HttpOnly` | MUST | JS가 읽을 수 없게 (XSS 단발 탈취 차단) |
| `SameSite=Strict` | SHOULD | 다른 사이트에서 시작한 요청에 쿠키가 따라가지 않게. 이 규칙은 로그인 뒤의 **BFF 세션 쿠키**에 대한 것이다. 인증 서버가 다른 사이트라면 인증 서버에서 BFF 콜백으로 돌아오는 이동에는 Strict 쿠키가 실리지 않으므로, 로그인 진행 중의 state·code_verifier는 7.5절처럼 `SameSite=Lax`인 별도 쿠키나 서버 저장소에 둔다 |
| `Path=/` | SHOULD | |
| `Domain` 속성 생략 | SHOULD NOT set | 하위 도메인으로 쿠키가 퍼지지 않게 |
| `__Host-Http-` 같은 이름 접두어 | SHOULD | 브라우저가 Secure·Path=/·Domain 없음을 강제하고, HTTP로 설정된 쿠키임을 표시 |
| CSRF 방어 | MUST | 쿠키 기반 인증은 원래 일반 웹 CSRF(13.2절 ④)에 노출됨. 같은 site의 다른 하위 도메인에서 오는 요청은 SameSite로 막히지 않으므로 CSRF 토큰이나 커스텀 헤더 + CORS를 함께 쓴다 |

```http
Set-Cookie: __Host-Http-session=8f3c…; Secure; HttpOnly; SameSite=Strict; Path=/
```

### 13.7 SPA가 직접 OAuth 클라이언트가 될 때

BFF를 둘 수 없어 구조 3을 택한다면 최소한 이것을 지킨다.

| 무엇을 | 강도 | 근거 |
|---|---|---|
| authorization code + PKCE 사용 | MUST | RFC 10017 6.3.2.1(PKCE), 7.2(code 사용) |
| implicit 사용 금지 | MUST NOT | RFC 10017 7.2 |
| client_secret을 앱에 넣지 않음. 인증 서버도 요구하지 않음 | MUST NOT | RFC 10017 6.3.3.1 |
| refresh token은 rotation 또는 발신자 제한 | MUST (인증 서버) | RFC 10017 6.3.2.3 |
| refresh token에 최대 수명 또는 비활성 만료를 두고, rotation으로 새로 준 토큰이 처음 토큰의 수명을 넘지 않게 | MUST (인증 서버) | RFC 10017 6.3.2.3 |
| 가능하면 DPoP로 토큰을 브라우저 키에 묶음 (15.6.2). 이미 받은 토큰을 빼 가는 시나리오 1·2는 줄지만, 새 흐름 실행(시나리오 3)은 막지 못한다(RFC 10017 6.3.4.2.2절) | 선택 | |

인증 서버 쪽 설정도 관련된다. 브라우저 JS가 token 엔드포인트를 직접 부르므로, 인증 서버는 token 엔드포인트(그리고 앱이 직접 부르는 discovery·JWKS·폐기 엔드포인트 등)에 CORS를 지원한다. RFC 9700 2.6절은 이를 허용(MAY)하고, RFC 10017 6.3.3.4절은 브라우저 단독 클라이언트를 지원한다면 인증 서버와 리소스 서버가 필요한 CORS 헤더를 보내야 한다(MUST)고 한다. 반면 **authorize 엔드포인트는 CORS를 지원하면 안 된다(MUST NOT, RFC 9700 2.6).** authorize는 JS가 호출하는 API가 아니라 브라우저가 **이동**하는 페이지이기 때문이다.

### 13.8 이 연동에서 보이는 BFF의 모습

이 연동 사례의 서비스 화면(16.5절)은 구조상 BFF와 닮았다. 클라이언트 앱 서버가 IdP 서비스 토큰을 서버에 보관하고, 사용자 기기의 웹뷰에는 클라이언트 앱 세션만 두며, 요청마다 토큰을 붙여 중계한다. IdP 서비스 토큰은 사용자 기기로 내려가지 않는다. 그래서 클라이언트 앱 웹뷰 안의 스크립트가 장악되더라도 **IdP 서비스 토큰 자체를 훔치기는 어렵다.** 대신 그 경우에도 "브라우저가 열려 있는 동안 중계를 통해 요청을 보내는 것"은 가능하다는 BFF의 한계도 그대로 갖는다.

---

## 14. 더 알아 둘 확장 표준

OAuth 2.0 본체(RFC 6749)가 다루지 않는 문제를 푸는 확장 표준이 많다. 입문 단계에서 모두 구현할 필요는 없다. 다만 **어떤 문제가 생겼을 때 어떤 표준을 찾아야 하는지**는 알아 두면 좋다.

입문 중요도는 이렇게 읽는다. ★★★는 지금 바로 알아야 하는 것, ★★는 해당 상황이 오면 바로 찾아볼 것, ★는 이름만 알아 두고 처음엔 건너뛰어도 되는 것이다. 각 절의 그림은 "무엇을 해결하는지"를 보이는 용도라서, 세부 파라미터를 외울 필요는 없다.

### 14.1 문제별 확장 표준 지도

| 이런 문제가 생기면 | 찾아볼 표준 | 입문 중요도 | 절 |
|---|---|---|---|
| authorize URL의 파라미터가 길고, 브라우저를 거치며 바뀔까 걱정된다 | PAR (RFC 9126) | ★★ | 14.2 |
| authorize 요청 내용을 서명해서 위·변조를 막고 싶다 | JAR (RFC 9101) | ★ | 14.3 |
| scope 문자열로는 "이 계좌에서 이 금액만" 같은 세밀한 권한을 표현할 수 없다 | RAR (RFC 9396) | ★ | 14.4 |
| 스마트 TV나 브라우저 없는 서버 터미널처럼, 브라우저가 없거나 입력이 불편한 기기에서 로그인해야 한다 | Device Authorization Grant (RFC 8628) | ★★ | 14.5 |
| 받은 토큰으로 다른 서비스를 사용자 대신 불러야 한다 | Token Exchange (RFC 8693) | ★★ | 14.6 |
| client_secret을 공유하지 않고 클라이언트를 인증하고 싶다 | private_key_jwt (RFC 7523) | ★★ | 14.7 |
| 사용 중인 기기가 아니라 사용자 휴대폰으로 승인을 받고 싶다 | CIBA (OpenID) | ★ | 14.8 |
| 민감한 API에서 "방금 다시 로그인한 사용자"만 받고 싶다 | Step-up (RFC 9470) | ★ | 14.9 |
| 클라이언트가 리소스 서버만 알고 어느 인증 서버로 가야 할지 모른다 | Protected Resource Metadata (RFC 9728) | ★ | 14.10 |
| 토큰을 훔쳐도 못 쓰게 하고 싶다 | DPoP (RFC 9449), mTLS (RFC 8705) | ★★★ | 15.6.2 |
| 토큰을 특정 API 전용으로 만들고 싶다 | Resource Indicators (RFC 8707) | ★★ | 10.6절 |
| 클라이언트를 사람 손 없이 등록하고 싶다 | Dynamic Client Registration (RFC 7591) | ★ | 4.6절 |
| 연결 해제·유출 의심 때 토큰을 무효화하고 싶다 | Revocation (RFC 7009) | ★★★ | 8.8절 |

### 14.2 PAR: 요청을 미리 서버로 보내기 (RFC 9126)

**문제**: 일반 authorize 요청은 모든 파라미터를 URL에 싣고 브라우저를 거친다. 브라우저를 지나는 동안 바뀔 수 있고(무결성 없음), 누가 보냈는지 확인할 수 없으며(출처 인증 없음), 파라미터가 많으면 URL이 너무 길어진다.

**해결**: 클라이언트가 파라미터 전체를 **서버끼리 먼저** 인증 서버에 보내고, 받은 짧은 참조값만 브라우저로 넘긴다.

```
클라이언트 서버                                   인증 서버
  │ ① POST /par  (client 인증 + 모든 authorize 파라미터) ─►│
  │◄── 201 { "request_uri": "urn:ietf:params:oauth:request_uri:6esc…", "expires_in": 60 }
  │
  │ ② 브라우저를 이동시킴
  │    GET /authorize?client_id=…&request_uri=urn:ietf:params:oauth:request_uri:6esc…
  │                                   ③ 인증 서버는 ①에서 받은 내용으로 처리
```

**얻는 것**: 브라우저에는 의미 없는 참조값만 지나가므로 요청을 바꿀 수 없다. 사용자를 화면에 보내기 **전에** 클라이언트 인증을 끝낼 수 있다. redirect_uri 검사도 인증된 요청 기준으로 할 수 있다(RFC 9700 4.1.3은 PAR·JAR과 client 인증이 함께 쓰이면 redirect URI 추가 검사를 생략해도 된다고 한다).

### 14.3 JAR: 요청을 서명된 JWT로 보내기 (RFC 9101)

authorize 파라미터를 **서명된 JWT(Request Object)** 하나에 담아 `request` 파라미터로 보내거나, 그 JWT가 있는 주소를 `request_uri`로 보낸다. 인증 서버는 서명을 검증해 "이 요청은 정말 그 클라이언트가 만들었고 중간에 바뀌지 않았다"를 확인한다. PAR과 함께 쓰는 경우가 많고, 금융권 보안 프로필(FAPI)에서 자주 요구된다.

### 14.4 RAR: 세밀한 권한 요청 (RFC 9396)

scope는 `read`, `payment` 같은 짧은 문자열이라 "**이 계좌에서 123.50유로를 이 수취인에게**" 같은 권한을 표현하기 어렵다. RAR은 `authorization_details`라는 JSON 배열로 권한을 구조적으로 표현한다.

```json
"authorization_details": [
  {
    "type": "payment_initiation",
    "actions": ["initiate"],
    "locations": ["https://bank.example/payments"],
    "instructedAmount": { "currency": "EUR", "amount": "123.50" },
    "creditorName": "Merchant A",
    "creditorAccount": { "iban": "DE02100100109307118603" }
  }
]
```

동의 화면에 "Merchant A에게 123.50 EUR 송금"처럼 구체적으로 보여 줄 수 있다. 인증 서버는 승인된 `authorization_details`를 access token(또는 introspection 응답)에 담고, 리소스 서버가 요청이 그 범위 안인지 확인한다(RFC 9396 9절). "한 번만" 같은 횟수 제한은 RAR이 정하지 않으므로 API나 인증 서버 정책으로 따로 구현한다. 신고·제출 업무 서비스로 옮기면 "특정 연도 귀속분 신고서 1건 제출" 같은 권한 표현에 어울린다.

### 14.5 Device Authorization Grant: 입력이 불편한 기기 (RFC 8628)

스마트 TV나 브라우저 없는 서버 터미널처럼 브라우저가 없거나 입력이 불편한 기기는, **다른 기기(휴대폰)의 브라우저**로 로그인을 대신 처리한다.

```
TV(기기)                              인증 서버                         사용자 휴대폰
  │ ① POST /device_authorization ────►│                                  │
  │◄── device_code, user_code="WDJB-MJHT",                               │
  │    verification_uri="https://example.com/device", interval=5         │
  │ ② 화면에 표시: "example.com/device 에서 WDJB-MJHT 입력"                │
  │                                   │◄── ③ 주소 접속, 코드 입력, 로그인·동의 ┤
  │ ④ 5초마다 폴링                      │                                  │
  │   POST /token grant_type=urn:ietf:params:oauth:grant-type:device_code │
  │               &device_code=…  ───►│                                  │
  │◄── authorization_pending (아직)    │                                  │
  │◄── slow_down (너무 자주 → 간격 5초 늘리기)                              │
  │◄── 토큰 (사용자가 승인함)  /  access_denied  /  expired_token          │
```

**보안 주의**: 공격자가 자기 user_code를 피해자에게 보내 "이 코드를 입력하라"고 속이면, 피해자의 승인이 공격자 기기로 간다. 그래서 인증 서버의 코드 입력 화면은 **어떤 기기·클라이언트가 권한을 요청하는지**를 분명히 보여 줘야 한다.

### 14.6 Token Exchange: 사용자 대신 다른 서비스 부르기 (RFC 8693)

10.3절에서 "사용자 토큰을 하위 서비스로 그대로 넘기지 않는다"고 했다. 그러면 하위 서비스가 **사용자의 권한**으로 동작해야 할 때는 어떻게 하나. 받은 토큰을 인증 서버에 내고, **그 하위 서비스 전용의 새 토큰**으로 바꿔 받는다.

```
사용자 ──토큰 A (aud=core-service)──► 코어 서비스
                                     │ POST /token
                                     │   grant_type=urn:ietf:params:oauth:grant-type:token-exchange
                                     │   subject_token=<토큰 A>
                                     │   subject_token_type=urn:ietf:params:oauth:token-type:access_token
                                     │   audience=tax-filing-service
                                     │   (위임이라면 actor_token=<코어 서비스 자신의 토큰>
                                     │    &actor_token_type=urn:ietf:params:oauth:token-type:access_token)
                                     ▼
                                  인증 서버 ── 토큰 B (aud=tax-filing-service, 좁은 scope) ──►
코어 서비스 ──토큰 B──► 신고 서비스
```

| 방식 | 토큰 B에 담기는 것 | 의미 |
|---|---|---|
| 사칭 (impersonation) | `sub` = 사용자 | 하위 서비스는 사용자가 직접 부른 것처럼 본다 |
| 위임 (delegation) | `sub` = 사용자, `act` = 코어 서비스 | "코어 서비스가 사용자를 대신해" 부른 것이 기록된다 |

`actor_token`을 보내면 `actor_token_type`도 반드시 함께 보낸다(RFC 8693 2.1절, REQUIRED). 위임 방식 토큰의 `act` claim은 이 값을 근거로 채워진다.

**얻는 것**: 토큰 A는 코어 서비스에서 멈추고 하위 서비스로 내려가지 않는다. 하위로 가는 토큰 B는 `aud=filing-service`로 묶여 있어, 신고 서비스에서 새더라도 코어 서비스나 다른 서비스에서는 쓸 수 없다. 하위 서비스마다 필요한 최소 권한만 준다. 위임 방식이면 감사 기록에 "누가 누구를 대신했는지"가 남는다. AI 에이전트가 사용자 대신 여러 도구를 부르는 구조에서 특히 유용하다.

### 14.7 private_key_jwt: secret 없이 클라이언트 인증 (RFC 7523)

4.2절에서 본 대안이다. 클라이언트는 키 쌍을 만들어 공개키만 인증 서버에 등록하고, token 요청마다 비밀키로 서명한 짧은 JWT를 낸다.

```http
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&code=…&code_verifier=…
&client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer
&client_assertion=eyJhbGciOiJSUzI1NiIsImtpZCI6ImNsaWVudC1rZXktMSJ9.…
```

```json
{
  "iss": "client-app-id",           // 클라이언트 자신
  "sub": "client-app-id",           // 클라이언트 자신
  "aud": "https://auth.stg.idp.example",              // 인증 서버의 issuer 식별자 하나만 (배열 X)
  "jti": "b8f3…",                    // 재사용 방지용 고유 ID
  "exp": 1793000060                  // 아주 짧게
}
```

`aud`에는 token 엔드포인트 주소가 아니라 **인증 서버의 issuer 식별자**(discovery 문서의 `issuer` 값) 하나만 넣는다. RFC 7523은 token 엔드포인트 주소도 허용했지만, aud 값이 모호한 점을 노려 한 인증 서버로 보낸 assertion을 다른 인증 서버에서 재사용하는 공격(audience injection)이 2025년에 알려졌다. 그래서 개정판(draft-ietf-oauth-rfc7523bis, RFC 발행 대기)은 issuer만 허용하고 token 엔드포인트 주소를 금지한다(MUST NOT). 인증 서버도 aud가 자기 issuer 하나가 아니면 거부해야 한다. 개정판은 헤더에 `"typ": "client-authentication+jwt"`를 넣는 방식도 새로 정의한다.

**얻는 것**: 인증 서버는 공개키만 저장하므로 DB가 털려도 클라이언트를 사칭할 수 없다. 비밀이 메신저로 오갈 일도 없다. RFC 9700은 이런 비대칭 방식의 클라이언트 인증을 권장한다(RECOMMENDED).

### 14.8 CIBA: 다른 기기에서 승인받기 (OpenID)

**Client-Initiated Backchannel Authentication**. 사용자가 쓰는 기기에서 로그인 화면을 띄우지 않고, 사용자의 **다른 기기(휴대폰 앱)**로 승인 요청을 보낸다. 콜센터 상담원이 고객 대신 처리할 때, 매장 단말기에서 결제할 때처럼 "사용하는 기기"와 "인증하는 기기"가 다른 상황을 위한 것이다.

```
클라이언트(콜센터 시스템)                 인증 서버                         사용자 휴대폰 앱
  │ ① POST /bc-authorize (client 인증)   │                                  │
  │    scope=openid, login_hint=회원 식별자,│                                  │
  │    binding_message="A7"                                                 │
  │◄── auth_req_id, expires_in, interval│ ② 푸시 ─────────────────────────►│
  │                                    │      "A7: 경정청구 제출을 승인하시겠습니까?"
  │                                    │◄── ③ 사용자가 생체 인증 후 승인 ───┤
  │ ④ 폴링 (또는 인증 서버가 알려 줌)     │                                  │
  │   grant_type=urn:openid:params:grant-type:ciba&auth_req_id=… ─►│        │
  │◄── 토큰                             │                                  │
```

`binding_message`는 클라이언트 화면과 휴대폰 화면에 같은 짧은 문구를 보여 줘서, 사용자가 "지금 내가 요청한 것"을 승인하는지 확인하게 한다. 되돌리기 어려운 작업에 사용자 본인 승인을 받는 수단으로 검토할 만하다. `binding_message`는 짧고 제한된 문자로 쓰라고 권하므로(SHOULD), 한글 문구를 쓰려면 인증 서버가 받아 주는지 먼저 확인한다.

### 14.9 Step-up 인증: 더 강한 로그인 요구하기 (RFC 9470)

8.5절에서 refresh token으로 받은 토큰은 "사용자가 지금 있다"를 증명하지 않는다고 했다. 민감한 API는 리소스 서버가 클라이언트에게 "**더 최근의, 더 강한 인증이 필요하다**"고 알려 줄 수 있다.

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer error="insufficient_user_authentication",
  error_description="A different authentication level is required",
  acr_values="urn:example:mfa", max_age="300"
```

클라이언트는 이 응답을 받으면 authorize 요청에 `acr_values`(요구하는 인증 수준)와 `max_age`(최대 경과 시간, 초)를 실어 사용자를 다시 인증시키고, 새 토큰으로 재시도한다. 리소스 서버는 토큰의 `acr`, `auth_time`을 보고 판단한다.

### 14.10 Protected Resource Metadata (RFC 9728)

9.6절의 discovery가 **인증 서버**의 정보를 공개한다면, 이 표준은 **리소스 서버**의 정보를 공개한다. 경로는 `/.well-known/oauth-protected-resource`다.

```json
{
  "resource": "https://api.idp.example",
  "authorization_servers": ["https://auth.stg.idp.example"],
  "scopes_supported": ["service"],
  "bearer_methods_supported": ["header"]
}
```

리소스 서버는 토큰 없이 들어온 요청에 401과 함께 `WWW-Authenticate: Bearer resource_metadata="https://api.idp.example/.well-known/oauth-protected-resource"`를 돌려줄 수 있다. 그러면 클라이언트는 **리소스 서버 주소만 알고 시작해도** 어느 인증 서버에서 어떤 scope로 토큰을 받아야 하는지 스스로 알아낸다. 클라이언트와 서버가 미리 짝지어 설정되지 않는 개방형 생태계에서 쓰인다. 대표 사용처는 AI 에이전트가 외부 도구 서버에 연결하는 규격인 MCP(Model Context Protocol)다. MCP 인가 규격은 MCP 서버에 이 표준(RFC 9728)을, MCP 클라이언트에 Resource Indicators(10.6절)를 필수(MUST)로 요구한다. 클라이언트 등록 방식은 판마다 바뀌었다. 2025-06-18판은 동적 클라이언트 등록(4.6절)을 권장(SHOULD)했고, 2026-11 현재 최신판(2026-07-28)은 클라이언트 정보를 https 주소의 JSON 문서로 공개하는 방식(Client ID Metadata Documents)을 권장(SHOULD)하면서 동적 등록은 하위 호환용(MAY, deprecated)으로 낮췄다.

(위 JSON의 리소스 주소와 scope는 설명을 위한 예시다.)

---

## 15. 보안: 공격과 방어

앞 장들에서 개념을 배울 때 공격을 몇 개 함께 봤다. 이 장은 OAuth를 노리는 공격 전체를 한곳에 모은 **공격 지도**다. 중심 기준은 OAuth 보안 모범 사례 표준인 **RFC 9700**(BCP 240, 2025년 1월)이다. 다만 RFC 9700은 "예전 위협 모델 문서(RFC 6819)에 이미 있는 공격은 다시 싣지 않는다"고 스스로 밝히므로, RFC 6819의 기본 위협과 **OAuth 2.1 초안 7장**의 보안 절(동의 피싱, 추측 공격, 피싱, 입력값 검증, 클라이언트 사칭)도 함께 다룬다. JWT 검증 함정은 **RFC 8725**(JWT 모범 사례), 브라우저 앱은 **RFC 10017**(2026년 8월)을 따른다.

### 15.1 이 장을 읽는 법

공격 하나를 항상 같은 순서로 설명한다.

| 표시 | 무엇을 쓰나 |
|---|---|
| 🎯 노리는 것 | 공격자가 최종적으로 얻으려는 것 |
| 🧨 공격 원리 | 공격자가 무엇을 어떻게 조작하는지, 단계별로 |
| 🛡️ 방어 | 무엇을 해야 하는지, 표준의 규범 강도와 함께 |
| 💡 방어 원리 | 그 방어가 **왜** 통하는지 |

이미 앞 장에서 자세히 다룬 공격은 15.3절의 공격 지도 표에 한 줄로 요약하고 그 절을 가리킨다. 같은 설명을 두 번 쓰지 않기 위해서다.

### 15.2 공격자는 무엇을 할 수 있다고 가정하나

RFC 9700은 공격자를 능력에 따라 다섯 종류로 나눈다. 방어를 설계할 때 "어떤 공격자를 상대로 하는가"를 먼저 정해야, 방어가 충분한지 판단할 수 있다.

```
                 ┌──────────────────── 인터넷 ─────────────────────┐
 사용자 브라우저 ◄─┼──► 클라이언트 ◄──► 인증 서버 ◄──► 리소스 서버   │
        ▲        │        ▲                                ▲      │
   [웹 공격자]     │   [네트워크 공격자]                  [토큰 탈취자] │
   자기 사이트로    │   TLS 밖의 통신을                     토큰 하나를   │
   사용자를 유인    │   엿보고 바꿈                        손에 넣음     │
        │        └─────────────────────────────────────────────────┘
        ▼
 [응답 열람자]  인가 응답(code가 실린 URL)을 읽을 수 있음
 [요청 열람자]  인가 요청(authorize URL)을 읽을 수 있음
```

| 평이한 이름 | 할 수 있는 것 | 예 |
|---|---|---|
| 웹 공격자 | 자기 웹사이트와 **자기 인증 서버·리소스 서버**를 운영하고, 정상 인증 서버에 자기 클라이언트를 등록하고, 사용자를 아무 URL로 유인한다. 자기에게 오지 않은 메시지는 못 읽는다 | 피싱 링크를 뿌리는 사람 |
| 네트워크 공격자 | 네트워크를 장악해 엿보고 바꾼다. TLS로 보호된 것은 못 읽는다 | 공용 와이파이 운영자 |
| 응답 열람자 | 인가 응답(code가 실린 URL)을 읽을 수 있다. 바꾸지는 못한다 | 프록시 로그, 브라우저 히스토리, 같은 scheme을 등록한 악성 앱 |
| 요청 열람자 | 인가 요청(authorize URL)을 읽을 수 있다 | 같은 경로 |
| 토큰 탈취자 | access token을 손에 넣었다 | 침해된 리소스 서버, 잘못된 설정으로 토큰을 받은 가짜 서버 |

뒤의 세 공격자는 보통 앞의 둘과 함께 움직인다. 그리고 **공격자 자신이 정상 사용자일 수도 있다.** 공격자는 자기 계정과 자기 브라우저로 정상 흐름을 진행하면서, 중간에 값을 바꿔치기할 수 있다.

### 15.3 공격 지도

OAuth 흐름 위에 공격이 노리는 지점을 표시하면 이렇다.

```
 ① authorize 요청        ② 로그인·동의           ③ 302 응답(code)         ④ token 요청          ⑤ API 호출
 브라우저 ──────────► 인증 서버 ──────────► 브라우저 ──────────► 클라이언트 ──────────► 인증 서버 ─ 토큰 ─► 리소스 서버
    │                    │                    │                    │                     │                │
    ├ PKCE 다운그레이드    ├ 클릭재킹            ├ redirect URI 조작   ├ code 끼워 넣기       ├ refresh 탈취     ├ 훔친 토큰 사용
    ├ mix-up 시작         ├ 307 redirect       ├ Referer 유출        ├ CSRF               ├ 클라이언트 사칭   ├ 가짜 리소스 서버
    └ 요청 변조           ├ 내장 웹뷰           ├ 히스토리 유출       ├ access token 끼워넣기│                  ├ 토큰 종류 혼동
                         └ 동의 피싱           ├ open redirector    └ mix-up 완성        │                  ├ JWT 검증 함정
                                              ├ custom scheme 가로채기                   │                  └ 프록시 헤더 위조
                                              └ postMessage 유출                         │
```

| 공격 | 노리는 것 | 핵심 방어 | 자세히 |
|---|---|---|---|
| redirect URI 조작 (등록값과 다른 주소로 보내기) | code | 등록값과 정확히 일치할 때만 리다이렉트 | 4.4절 |
| redirect URI 검증 부족 (와일드카드·부분 일치) | code, 토큰 | 정확한 문자열 일치 | 15.4.1 |
| open redirector | code, 토큰, 피싱 | open redirector를 두지 않기 | 15.4.2 |
| Referer 헤더 유출 | code, state | 콜백 페이지에 외부 자원 금지, Referrer-Policy | 15.4.3 |
| 브라우저 히스토리 유출 | code, 토큰 | code 일회용, 토큰을 URL에 싣지 않기 | 15.4.4 |
| 307 redirect | 사용자 비밀번호 | 303 사용 | 15.4.5 |
| code 가로채기 | code → 토큰 | PKCE | 7.3절 |
| authorization code injection | 피해자 계정을 공격자 세션에 연결 | PKCE (또는 OIDC nonce) | 15.5.1 |
| access token injection | 같음 | implicit 쓰지 않기 | 15.5.2 |
| 로그인 CSRF | 피해자를 공격자 계정에 연결 | state 대조, PKCE, nonce | 7.2절, 15.5.3 |
| PKCE 다운그레이드 | PKCE 무력화 | challenge 없이 발급한 code에 verifier가 오면 거부 | 15.5.4 |
| mix-up | 다른 인증 서버의 code·토큰 | `iss` 대조 | 15.5.5 |
| 가짜·침해된 리소스 서버 | access token | audience 제한, 발신자 제한 | 15.6.1 |
| 훔친 access token 사용 | 사용자 권한 | 발신자 제한 토큰(mTLS, DPoP) | 15.6.2 |
| refresh token 탈취 | 장기 권한 | rotation, 재사용 탐지, 발신자 제한 | 8.4절, 15.6.3 |
| 클라이언트의 사용자 사칭 | 사용자 리소스 | client_id와 사용자 ID 공간 분리 | 15.7.1 |
| 토큰 종류 혼동 (id_token을 API에) | API 접근 | `aud`, `typ` 검사 | 10.4절 |
| 이메일 기반 자동 연결 | 기존 계정 탈취 | `(iss, sub)`로 식별, 기존 계정 재인증 | 9.3절 |
| id_token 재사용 | 로그인 위조 | nonce | 9.4절 |
| JWT 알고리즘 혼동·`none` | 토큰 위조 | 허용 알고리즘 고정 | 10.2절, 15.8 |
| JWT 약한 키·`kid`·`jku` 악용 | 토큰 위조, 서버 내부 요청 | 강한 키, 값 검증, 주소 허용 목록 | 15.8 |
| 클릭재킹 | 동의·비밀번호 | `frame-ancestors` | 7.8절 |
| 내장 웹뷰 | 비밀번호, 세션 쿠키 | 시스템 브라우저 | 12.2절 |
| custom scheme 가로채기 | code | https 링크 + PKCE | 12.4절 |
| postMessage 흐름 공격 | code, 토큰 | origin 정확히 비교 | 15.9.1 |
| XSS로 토큰 탈취 (브라우저 앱) | 토큰 | BFF로 토큰을 브라우저 밖에 | 13장 |
| TLS 종료 프록시 헤더 위조 | 접근 제어 우회 | 외부 헤더 제거, 내부 구간 보호 | 15.10 |
| 서버 자격 증명 유출·사용자 지정값 조작 | 모든 연결 사용자 | secret 보관, 사용자 값은 검증된 토큰에서 | 16.8절 |
| 동의 피싱 | 사용자의 정상 동의 | 동의 화면에 클라이언트 정보 명시, 철회 수단 | 7.8절 |
| 기억한 동의로 자동 승인 악용 | 사용자 모르게 code 발급 | 클라이언트를 인증하지 못하면 자동 승인하지 않음 | 7.8절 |
| OAuth를 로그인으로 쓸 때의 토큰 바꿔치기 | 피해자 계정으로 로그인 | access token이 아니라 id_token의 `aud`로 로그인 판단 | 15.7.2 |
| 추측 공격 | code, refresh token 등 | 값의 무작위성 2^128 이상, 시도 횟수 제한 | 15.11 |
| 가짜 브라우저·로그인 페이지 피싱 | 비밀번호 | 시스템 브라우저, 피싱에 강한 인증 수단 | 12.2절 |
| 받은 파라미터를 그대로 믿기 (state에 담은 주소로 이동 등) | open redirect 등 | 모든 파라미터를 외부 입력으로 검증 | 7.5절 |
| 클라이언트 저장소 유출 | 모든 사용자의 refresh token | 암호화 저장, secret과 분리 | 8.9절 |

---

### 15.4 리다이렉트 경로를 노리는 공격

code와 토큰은 브라우저 URL을 거쳐 이동한다. URL은 생각보다 많은 곳에 남고 새어 나간다. 이 절의 공격은 모두 그 성질을 노린다.

#### 15.4.1 redirect URI 검증 부족

🎯 **노리는 것**: code나 access token을 공격자 서버로 받는 것.

🧨 **공격 원리**: 일부 인증 서버는 정확한 주소 대신 **패턴(와일드카드)** 등록을 허용한다. 패턴은 사람이 생각한 것보다 넓게 해석되기 쉽다.

```
[변형 1] 와일드카드를 "아무 문자"로 해석
  등록 패턴:  https://*.somesite.example/*
  의도:       somesite.example의 하위 도메인만
  실제 통과:  https://attacker.example/.somesite.example     ← 앞부분이 공격자 도메인

  ① 공격자가 피해자를 자기 페이지로 유인
  ② 자기 페이지에서 "정상 client_id + 조작한 redirect_uri"로 authorize 요청을 보냄
  ③ 패턴 매칭 통과 → 피해자는 진짜 인증 서버 화면이라 안심하고 로그인
  ④ code가 attacker.example로 감

[변형 2] 와일드카드를 올바르게 해석해도 뚫리는 경우
  등록 패턴:  https://*.somesite.example/*   ("somesite.example 아래 아무 호스트")
  공격자가 somesite.example의 하위 도메인 하나를 손에 넣음
  (예: 지운 서비스의 DNS 레코드가 남아 있어 남이 그 이름을 가져가는 경우)
  → 그 하위 도메인으로 code가 감
```

public client의 code라면 공격자가 바로 토큰으로 바꾼다. confidential client라면 secret이 없어 바로 바꾸지는 못한다. 15.5.1의 code injection으로 정상 클라이언트에게 대신 바꾸게 할 수 있지만, 인증 서버가 token 요청의 redirect_uri를 authorize 때 값과 대조하면(RFC 6749 4.1.3절) 공격자 주소로 발급된 code라서 걸린다(RFC 9700 4.5.2절). 그 대조가 없는 OAuth 2.1 환경에서는 PKCE가 막는다.

🛡️ **방어** (RFC 9700)

| 누가 | 무엇을 | 강도 |
|---|---|---|
| 인증 서버 | 등록된 주소와 **정확한 문자열 일치**로 비교. 예외는 네이티브 앱의 loopback 주소(127.0.0.1, [::1])에서 포트 번호뿐 (12.6절) | MUST |
| 클라이언트 | redirect URI가 있는 서버에 open redirector를 두지 않음 | MUST NOT |
| 클라이언트 | 토큰을 인가 응답으로 받는 방식(implicit) 대신 code 방식 사용 | SHOULD |

💡 **방어 원리**: 패턴은 아무리 좁혀도 "공격자가 끼워 넣을 남는 자리"가 생긴다. RFC 9700도 패턴은 아주 좁아도 우회되지만 **정확한 일치는 우회되지 않는다**고 직접 적는다. 등록된 문자열 하나와 글자 단위로 같아야 하므로, 다른 도메인이나 꼬리 파라미터를 붙일 틈이 없다.

#### 15.4.2 open redirector

**open redirector**는 쿼리 파라미터로 받은 아무 주소로 브라우저를 보내 주는 기능이다. 로그인 후 원래 보던 페이지로 돌려보내는 `?next=` 같은 기능이 흔한 예다.

🎯 **노리는 것**: code·토큰 유출, 또는 믿을 만한 도메인을 앞세운 피싱.

🧨 **공격 원리 1: 클라이언트의 open redirector**

```
등록 패턴: https://client.example/cb?*     (쿼리는 아무거나 허용하는 느슨한 등록)
클라이언트에 open redirector가 있음: /cb?redirect_to=<URL> → 그 URL로 303

① 공격자가 redirect_uri = https://client.example/cb?redirect_to=https://attacker.example 로
   implicit(response_type=token) 요청을 만듦
② 인증 서버: 패턴 일치 → 303 Location: https://client.example/cb?redirect_to=…#access_token=…
③ 클라이언트의 redirector: 303 Location: https://attacker.example/   (fragment 없음)
④ 브라우저: 리다이렉트 대상에 fragment가 없으면 원래 fragment를 다시 붙이는 규칙에 따라
   https://attacker.example/#access_token=… 로 이동
⑤ 공격자 페이지가 fragment에서 access token을 꺼냄
```

이 공격은 패턴 등록이 아무리 좁아도 통한다. 정확한 일치 비교에서만 막힌다.

🧨 **공격 원리 2: 인증 서버를 피싱 중계기로 쓰기**

공격자가 동적 등록(4.6절)으로 자기 클라이언트를 만들고, redirect URI를 피싱 사이트로 둔다. 그리고 피해자에게 **진짜 인증 서버 도메인**의 링크를 보낸다.

```
https://auth.example/oauth/authorize?client_id=<공격자 클라이언트>&redirect_uri=https://phish.example&…

경로 A: 일부러 잘못된 scope를 넣음 → 인증 서버가 오류를 redirect_uri로 보냄 → 피싱 사이트 도착
경로 B: 사용자가 이상하다고 느껴 "거부" → 인증 서버가 access_denied를 redirect_uri로 보냄 → 피싱 사이트 도착
경로 C: prompt=none(화면 없는 로그인) → 인증 서버가 자동으로 redirect → 피싱 사이트 도착
```

피해자는 믿을 만한 인증 서버 주소를 눌렀는데 결국 공격자 사이트에 도착한다. 메일 필터나 링크 미리보기도 정상 도메인만 본다.

🛡️ **방어**

| 누가 | 무엇을 | 강도 |
|---|---|---|
| 클라이언트·인증 서버 | 쿼리로 받은 아무 주소로 보내는 기능을 노출하지 않음 | MUST NOT (RFC 9700 2.1) |
| 클라이언트 | 리다이렉트는 허용 목록에 있는 주소로만 | 권고 |
| 인증 서버 | client_id와 redirect_uri 조합이 틀리면 자동 리다이렉트하지 않음 | MUST (RFC 6749 4.1.2.1) |
| 인증 서버 | 리다이렉트 전에 **먼저 사용자를 인증** | MUST (RFC 9700 4.11.2) |
| 인증 서버 | 신뢰하는 redirect URI일 때만 자동 리다이렉트. 아니면 사용자에게 알리고 판단을 맡김 | SHOULD / MAY |

💡 **방어 원리**: open redirector는 "신뢰받는 도메인"과 "아무 목적지"를 이어 주는 다리다. 다리를 없애면 신뢰를 빌려 쓸 수 없다. 인증 서버가 먼저 로그인을 요구하면, 익명 사용자를 링크 한 번으로 피싱 사이트에 보내는 대량 공격이 어려워진다.

#### 15.4.3 Referer 헤더로 code·state 유출

🎯 **노리는 것**: 콜백 URL에 실린 code와 state.

🧨 **공격 원리**: 브라우저는 다른 페이지로 이동하거나 외부 자원(이미지, 광고 iframe)을 불러올 때, 지금 페이지의 URL을 `Referer` 헤더에 실어 보낸다.

```
① 브라우저가 https://client.example/cb?code=c-5d1e&state=st-8f2c 에 도착
② 이 콜백 페이지가 외부 광고 이미지를 불러오거나, 사용자가 외부 링크를 누름
③ 외부 서버로 가는 요청:
     GET /ad.png
     Referer: https://client.example/cb?code=c-5d1e&state=st-8f2c   ← URL 전체가 실림
④ 외부 서버(또는 공격자)가 code와 state를 얻음
```

state를 얻으면 그 state로 CSRF 방어가 무력해지고, code를 얻으면 15.5.1의 code injection으로 이어진다. 인증 서버의 authorize 페이지에 외부 자원이 있으면 같은 방식으로 state가 샌다.

🛡️ **방어** (RFC 9700 4.2.4)

| 무엇을 | 강도 |
|---|---|
| 인가 응답을 받는 콜백 페이지와 authorize 페이지에 제3자 자원·외부 링크를 두지 않음 | SHOULD NOT |
| `Referrer-Policy: no-referrer` 헤더로 Referer 자체를 보내지 않게 함 | 권고 |
| code를 PKCE나 confidential client에 묶음 | 권고 |
| code는 첫 사용 후 무효화, 두 번째 시도 시 기발급 토큰 폐기 | MUST / SHOULD |
| state는 첫 사용 후 무효화 | SHOULD |
| 콜백을 처리한 뒤 code가 없는 URL로 한 번 더 이동 | 해석: 일반적인 구현 습관 |

💡 **방어 원리**: 두 겹이다. Referrer-Policy와 외부 자원 금지는 **URL이 밖으로 나가는 경로 자체를 끊는다.** PKCE, 일회용 code·state는 **새더라도 쓸 수 없게** 만든다. 유출을 완전히 막을 수 없다고 가정하고 두 번째 겹을 둔다.

#### 15.4.4 브라우저 히스토리로 유출

🎯 **노리는 것**: 히스토리에 남은 code나 access token.

🧨 **공격 원리**: 브라우저는 방문한 URL을 히스토리에 저장한다. 공용 PC나 기기에 접근할 수 있는 공격자는 히스토리에서 `…/cb?code=…`나 `…?access_token=…`를 찾아 다시 쓴다. 웹사이트가 편의를 위해 `/profile?access_token=…`처럼 토큰을 URL에 넣으면 그대로 남는다.

🛡️ **방어**

| 무엇을 | 강도 |
|---|---|
| access token을 URL 쿼리 파라미터로 보내지 않음 | MUST NOT (RFC 9700 4.3.2) |
| code는 일회용으로, PKCE에 묶음 | MUST / 권고 |
| 인가 응답을 URL 대신 POST 본문으로 받는 form_post 응답 방식 사용 (7.7절) | 선택 |

💡 **방어 원리**: 히스토리는 "방문한 URL"만 기록한다. 토큰을 `Authorization` 헤더나 POST 본문으로 옮기면 히스토리에 남을 것이 없다. code는 기본 응답 방식(query)에서는 URL에 남지만, 일회용이고 PKCE에 묶여 있어 남아도 다시 쓸 수 없다. form_post를 쓰면 URL에 남지도 않는다.

#### 15.4.5 307 redirect로 비밀번호 유출

🎯 **노리는 것**: 사용자가 인증 서버 로그인 폼에 입력한 아이디·비밀번호.

🧨 **공격 원리**: 인증 서버가 로그인 폼(POST)을 처리한 뒤 **307**로 리다이렉트하면, HTTP 규칙상 브라우저는 **같은 POST 요청을 본문 그대로** 다음 주소로 다시 보낸다.

```
브라우저 ──POST /login  (email=…&password=…)──────────────▶ 인증 서버
브라우저 ◀──307 Location: https://client.example/cb?code=…── 인증 서버
브라우저 ──POST https://client.example/cb  (email=…&password=… 본문 그대로!)──▶ 클라이언트
```

악성 클라이언트라면 이 비밀번호로 인증 서버에 사용자인 척 로그인할 수 있다.

🛡️ **방어**: 사용자 자격 증명이 담긴 요청을 리다이렉트할 때 **307을 쓰지 않는다(MUST NOT). HTTP 리다이렉트를 쓴다면 303을 쓴다(SHOULD).** (RFC 9700 4.12)

💡 **방어 원리**: HTTP 표준에서 **303만이 "POST를 GET으로 바꿔서 이동하라"를 확실히 강제**한다. GET으로 바뀌면 폼 본문이 떨어져 나간다. 흔히 쓰는 302도 브라우저가 POST를 유지할 여지가 있다(실제로는 대부분의 브라우저가 307에서만 본문을 유지한다).

---

### 15.5 code·토큰을 끼워 넣는 공격

이 절의 공격은 무언가를 훔치는 것에서 끝나지 않는다. 훔친 것을 **자기 세션에 끼워 넣거나, 남의 세션에 공격자 것을 끼워 넣어** 신원을 뒤섞는다.

#### 15.5.1 authorization code injection

🎯 **노리는 것**: 훔친 피해자의 code를 정상 클라이언트에 대신 교환시켜, **공격자의 클라이언트 세션을 피해자 계정에 연결**하는 것.

🧨 **공격 원리**: confidential client는 secret이 있어야 code를 바꿀 수 있다. 공격자에게 secret이 없으니, 정상 클라이언트가 대신 바꾸게 만든다.

```
공격자 브라우저              정상 클라이언트                 인증 서버
  │ ① (다른 경로로 피해자의 code_V 확보: Referer, 프록시 로그, 히스토리, custom scheme 가로채기 등.
  │    모두 정상 redirect_uri로 발급된 code)
  │ ② 자기 기기에서 정상 로그인 흐름 시작 ─────►│                         │
  │◄────────────────────── 302 authorize ──────┤                         │
  │ ─────────────────────────────────────────────────────────────────►│
  │◄──── 302 /cb?code=code_A (공격자 자신의 code) ──────────────────────┤
  │ ③ 브라우저 개발자 도구로 code_A를 code_V로 바꿔치기
  │ ── /cb?code=code_V ──────────────────────►│                         │
  │                                           │ ④ 자기 secret으로 교환 ──►│
  │                                           │◄── ⑤ 피해자의 토큰 ──────┤
  │ ⑥ 공격자의 클라이언트 세션 = 피해자 계정       │                         │
```

공격자는 네트워크를 장악할 필요도 없다. 응답이 **자기 기기를 지나가므로** 아무 도구로나 바꿀 수 있다.

**기존 검사로 못 막는 이유**: ④에서 클라이언트는 정상 secret으로 인증하고, code는 그 클라이언트에게 발급된 것이며, redirect_uri도 맞다. 모든 검사가 통과한다. secret을 비대칭 키(private_key_jwt)로 바꿔도 마찬가지다. 인증하는 것은 정상 클라이언트이기 때문이다. 단, code_V를 redirect_uri 조작(15.4.1)으로 얻었다면 이야기가 다르다. 그 code는 공격자 주소로 발급됐으므로, 정상 클라이언트가 token 요청에 자기 redirect_uri를 실으면 인증 서버가 authorize 때 값과 달라 거부한다(RFC 6749 4.1.3절, RFC 9700 4.5.2절). OAuth 2.1 초안은 token 요청의 redirect_uri를 없앴으므로(17.1절), 그 환경에서는 이 대조에 기대지 말고 PKCE로 막는다.

🛡️ **방어** (RFC 9700 2.1.1)

| 클라이언트 종류 | 무엇을 | 강도 |
|---|---|---|
| public client | PKCE | MUST |
| confidential client | PKCE | RECOMMENDED |
| confidential OIDC client | PKCE 대신 nonce도 가능. 단 token 엔드포인트에서 받은 id_token의 nonce를 검증하고, 검증이 끝나기 전에는 받은 토큰을 하나도 쓰지 않음 | MAY (조건 MUST) |
| 공통 | challenge·nonce는 거래마다 새 값이고, 그 거래를 시작한 브라우저에 묶여야 함 | MUST |

💡 **방어 원리**: secret은 "**같은 클라이언트**"만 증명하고 "**같은 거래**"는 증명하지 못한다. PKCE는 code를 그 code를 요청한 거래의 challenge에 묶는다.

```
code_V  ── 묶여 있음 ──► 피해자 세션의 challenge = SHA256(verifier_V)
공격자 세션에서 교환할 때 클라이언트가 보내는 것 = verifier_A (공격자 세션 값)
인증 서버: SHA256(verifier_A) ≠ challenge_V  →  invalid_grant
```

**한계**: 공격자가 피해자의 authorize 요청 안의 challenge나 nonce를 **자기 세션의 값으로 바꿔치기**할 수 있다면 이 방어도 뚫린다. 공격이 복잡해 현실성은 낮지만, 그래서 15.4의 유출 경로를 막는 노력도 함께 해야 한다.

#### 15.5.2 access token injection

🎯 **노리는 것**: 다른 경로로 얻은 피해자의 access token을 정상 클라이언트에 끼워 넣어, 그 클라이언트에서 피해자로 행세하는 것.

🧨 **공격 원리**: implicit 방식에서는 access token이 **브라우저를 거쳐** 클라이언트에 전달된다. 공격자는 자기 기기에서 정상 흐름을 시작하고, 돌아오는 응답의 access token만 훔친 토큰으로 바꾼다. state는 공격자 세션의 정상 값이라 CSRF 검사도 통과한다.

🛡️ **방어**: **implicit을 쓰지 않는다.** RFC 9700은 인가 응답으로 access token을 받는 방식을 쓰지 말라고 권하고(SHOULD NOT), OAuth 2.1 초안은 implicit을 아예 삭제했다. OIDC에서는 id_token의 `at_hash`(access token의 해시)로 완화할 수 있다.

같은 계열의 공격이 implicit이 사라진 지금도 다른 모양으로 살아 있다. 백엔드가 앱에서 받은 access token으로 사용자를 로그인시키는 구조에서 일어나는 **토큰 바꿔치기**다(15.7.2).

💡 **방어 원리**: 순수 OAuth의 implicit에서는 토큰이 **거래와 아무 연결 없이** 발급되므로 끼워 넣기를 탐지할 방법이 없다. code 방식에서는 access token이 브라우저를 거치지 않고 클라이언트가 token 엔드포인트에서 직접 받으므로, 바꿔치기할 지점 자체가 사라진다. `at_hash`는 서명된 id_token 안에 "이 access token과 짝"이라고 적어 두므로, 공격자는 access token만 바꿀 수 없다.

#### 15.5.3 CSRF: state와 PKCE의 차이

기본 원리는 7.2절에서 다뤘다. 여기서는 **어느 방어가 더 강한지**만 짚는다.

| 방어 | 막는 조건 | 응답을 읽을 수 있는 공격자(15.2)에게 |
|---|---|---|
| state | 공격자가 피해자 세션의 state를 모를 때 | ⚠️ state는 응답 URL에 그대로 실려 새어 나갈 수 있음 |
| OIDC nonce | 공격자가 피해자 세션의 nonce를 모를 때 | ⚠️ id_token이 **인가 응답에 함께 실리는** 방식(`response_type=code id_token` 등)이면, 응답에서 nonce를 꺼내 새 요청에 써서 같은 nonce의 id_token을 만들 수 있음. 기본 code 흐름(id_token은 token 응답에만 옴)에서는 응답 URL로 새지 않음 |
| PKCE | 공격자가 피해자 세션의 verifier를 모를 때 | ✅ verifier는 authorize 요청에도 응답에도 실리지 않고 token 요청으로만 감 |

그래서 RFC 9700은 **인증 서버가 PKCE를 지원한다는 것을 확인한 클라이언트는 PKCE의 CSRF 방어에 기대도 된다(MAY)**고 한다. 다만 인증 서버가 PKCE를 **강제하지 않으면** 15.5.4의 다운그레이드로 이 방어가 열린다. state를 함께 쓰면 두 겹이 된다.

state에 "로그인 후 돌아갈 페이지" 같은 애플리케이션 정보를 담는다면, 변조와 바꿔치기를 막아야 한다(MUST). 브라우저 세션에 묶거나 서명·암호화한다.

#### 15.5.4 PKCE 다운그레이드

🎯 **노리는 것**: PKCE를 꺼서 CSRF·code injection 방어를 무력화하는 것.

🧨 **공격 원리**: 전제는 두 가지다. ① 인증 서버가 "요청에 `code_challenge`가 있으면 PKCE를 적용하고, 없으면 적용하지 않는다". ② 클라이언트가 CSRF 방어를 PKCE에만 맡기고 state를 쓰지 않거나 제대로 검사하지 않는다.

```
피해자 브라우저                       정상 클라이언트                    인증 서버
  │ ① 피해자가 로그인 시작, 클라이언트는 verifier=abc를 피해자 세션에 저장
  │
공격자 브라우저
  │ ② 공격자도 자기 기기에서 로그인 시작. 클라이언트가 만든 authorize URL에서
  │    code_challenge 파라미터를 통째로 지워 버림
  │ ────────────────────────────────────────────────────────────────►│
  │                                     ③ challenge가 없으니 PKCE 없이 code_X 발급
  │ ④ 피해자 브라우저가 /cb?code=code_X 를 열게 유도
  │
피해자 브라우저 ── /cb?code=code_X ──►│ ⑤ verifier=abc와 함께 교환 요청 ───►│
                                    │                     ⑥ code_X엔 challenge가 없음
                                    │                        → verifier를 보지 않고 발급
                                    │◄──── 공격자 계정의 토큰 ──────────────┤
  피해자 세션이 공격자 계정에 연결됨 (CSRF의 변형)
```

🛡️ **방어**: 인증 서버는 **authorize 요청에 `code_challenge`가 없었던 code로 token 요청이 왔는데 `code_verifier`가 들어 있으면 거부해야 한다(MUST, RFC 9700 4.8.2).** PKCE를 모든 요청에 강제하는 인증 서버(IdP 인증 서버처럼)는 이 방어를 자동으로 갖는다.

💡 **방어 원리**: 정상 클라이언트는 항상 PKCE를 쓰므로 token 요청에 verifier를 싣는다. 그런데 공격자가 challenge를 지운 code에는 challenge가 없다. **"verifier는 왔는데 challenge는 없었다"는 모순 자체가 공격의 흔적**이다.

#### 15.5.5 mix-up

🎯 **노리는 것**: 정직한 인증 서버가 발급한 code나 토큰을, 클라이언트가 **공격자의 인증 서버로 보내게** 만드는 것.

**조건**: 클라이언트가 인증 서버를 둘 이상 쓰고(예: "카카오로 로그인"과 "IdP 서비스로 로그인"을 모두 지원), 그중 하나를 공격자가 통제한다. 클라이언트가 동적 등록으로 공격자의 인증 서버에도 등록됐거나(공격자가 그렇게 유도), 연동한 인증 서버 하나가 침해된 경우다. **인증 서버를 하나만 쓰는 클라이언트에게는 해당하지 않는다.**

🧨 **공격 원리**

```
사용자 브라우저          클라이언트                공격자 인증 서버(A)         정직한 인증 서버(H)
  │ ① "A로 로그인" 클릭 ►│ ② 세션에 "A로 보냄" 저장   │                         │
  │◄─ 302 A/authorize ───┤                         │                         │
  │ ─────────────────────────────────────────────►│ ③ client_id를 H용으로 바꿔  │
  │◄─ 303 H/authorize?client_id=<H에 등록된 클라이언트 id> ──┤  H로 즉시 보냄     │
  │ ──────────────────────────────────────────────────────────────────────►│
  │                                                  ④ 사용자는 H 화면을 보고 로그인
  │◄─────────────────── /cb?code=code_H ──────────────────────────────────────┤
  │ ── code_H ──────────►│ ⑤ 세션에는 "A로 보냄" → A가 준 code라고 믿음
  │                      │ ── A의 token 엔드포인트로 code_H 전송 ─►│ ⑥ 공격자가 H의 code 획득
```

모든 인증 서버에 **같은 redirect URI**를 쓰면, 클라이언트는 돌아온 응답이 어느 서버에서 왔는지 구분할 수 없다. 그 틈을 노린다.

🛡️ **방어** (RFC 9700 4.4.2, RFC 9207)

| 무엇을 | 강도 |
|---|---|
| 인증 서버를 둘 이상 쓰는 클라이언트는 mix-up 방어를 갖춤 | MUST |
| 요청마다 "어느 issuer로 보냈는지"를 저장하고 사용자 브라우저에 묶음 | MUST |
| 인가 응답의 `iss`를 저장한 issuer와 비교하고, 다르면 중단 | MUST (방어 1) |
| `iss`를 쓸 수 없으면 issuer마다 다른 redirect URI를 쓰고, 응답이 온 주소로 판별 | 최후 수단 (SHOULD only if) |

💡 **방어 원리**: 공격의 핵심은 클라이언트가 "응답이 어디서 왔는지 모른다"는 점이다. 응답에 `iss`가 붙으면 ⑤에서 "나는 A에 보냈는데 응답은 H가 줬다"를 알아채고 code를 어디에도 보내지 않는다. 인증 서버 **URL**만 저장해서는 부족하다. 공격자는 정직한 서버의 authorize 주소를 자기 것인 척 선언하고 token 주소만 자기 것으로 둘 수 있기 때문이다. 그래서 authorize와 token 엔드포인트 묶음을 대표하는 **issuer 식별자**를 비교한다.

---

### 15.6 훔친 토큰을 쓰는 공격

앞 절들이 "토큰이 새지 않게"를 다뤘다면, 이 절은 **"새더라도 쓸모없게"**를 다룬다. 유출을 완벽히 막을 수 없다는 가정에서 출발하는 두 번째 방어선이다.

#### 15.6.1 bearer 토큰의 근본 약점과 가짜 리소스 서버

8.10절에서 본 대로 지금 대부분의 access token은 **bearer token**이라서, **가진 사람이 곧 주인**이다.

🧨 **공격 원리: 가짜 리소스 서버로 토큰 모으기**

```
① 공격자가 표준 API(메일, 캘린더, 오픈뱅킹 등)를 흉내 내는 가짜 리소스 서버를 차림
② 사용자나 관리자가 설정 화면에서 리소스 서버 주소를 입력하는 구조의 클라이언트에
   공격자 서버 주소를 넣게 유도
③ 클라이언트가 정상 access token을 공격자 서버로 보냄
④ 공격자가 그 토큰으로 진짜 리소스 서버를 호출
```

리소스 서버가 침해되거나 로그 파일만 새도 같은 결과가 난다. 그 서버에 들어온 토큰들이 **다른 서버에서도 유효하다면** 피해가 번진다.

🛡️ **방어** (RFC 9700 4.9, 4.10)

| 무엇을 | 강도 |
|---|---|
| access token의 audience를 특정 리소스 서버로 제한 (10.6절) | SHOULD |
| 리소스 서버는 자기 앞으로 발급되지 않은 토큰을 거부 | MUST |
| access token을 발신자에 묶음 (15.6.2) | SHOULD |
| 리소스 서버는 토큰을 비밀처럼 다루고 평문으로 저장·전송하지 않음 | MUST |

💡 **방어 원리**: audience가 "IdP 서비스 API"로 묶여 있으면, 가짜 서버가 받은 토큰을 다른 서버에 내밀어도 "내 것이 아니다"로 거부된다. 발신자 제한이 있으면 토큰 문자열만으로는 아무 데서도 못 쓴다.

#### 15.6.2 발신자 제한 토큰: mTLS와 DPoP

**발신자 제한 토큰**의 개념은 8.10절에서 봤다. 토큰을 특정 클라이언트의 **키**에 묶어, 토큰과 함께 "그 키를 지금 가지고 있다"는 증명을 내야만 통과시킨다. 여기서는 표준 방식 두 가지가 실제로 어떻게 동작하는지 본다.

**① mTLS 인증서 묶기 (RFC 8705)**: 10.3절에서 본 방식이다. 클라이언트가 mTLS로 연결하면, 인증 서버는 토큰에 그 인증서의 지문(`cnf.x5t#S256`)을 넣는다. 리소스 서버는 지금 TLS 연결의 인증서 지문과 비교한다. **서버끼리의 연동**에 잘 맞는다.

**② DPoP (RFC 9449, Demonstrating Proof of Possession)**: TLS가 아니라 **애플리케이션 계층**에서 증명한다. 클라이언트가 키 쌍을 만들고, 요청마다 비밀키로 서명한 짧은 JWT(**DPoP proof**)를 `DPoP` 헤더에 붙인다. 인증서가 필요 없어서 **모바일 앱이나 브라우저 앱 같은 public client**에도 쓸 수 있다.

```
클라이언트 (키 쌍 보유)                   인증 서버                        리소스 서버
  │ ① token 요청                          │                               │
  │    DPoP: <proof: 내 공개키 + 서명>  ──►│ ② 토큰에 공개키 지문을 넣음        │
  │◄─── access_token (cnf.jkt = 지문), token_type: DPoP                    │
  │                                                                       │
  │ ③ API 호출                                                             │
  │    Authorization: DPoP <access_token>                                 │
  │    DPoP: <새 proof: 이 요청의 메서드·URL·시각·토큰 해시, 비밀키로 서명> ──►│
  │                                                ④ proof 서명을 공개키로 검증,
  │                                                   그 공개키의 지문 == 토큰의 cnf.jkt?
  │                                                   메서드·URL이 지금 요청과 같은가?
  │                                                   ath == 함께 온 access token의 SHA-256 해시?
  │                                                   iat가 허용 시간 범위 안인가? 같은 proof(jti)를 재사용하지 않았나?
```

DPoP proof JWT의 주요 항목(RFC 9449):

| 위치 | 항목 | 의미 |
|---|---|---|
| 헤더 | `typ: dpop+jwt` | DPoP proof임을 표시 |
| 헤더 | `alg` | 서명 알고리즘. 비대칭 서명만 허용, `none` 금지 |
| 헤더 | `jwk` | 서명 검증에 쓸 공개키 |
| 본문 | `htm`, `htu` | 이 proof가 쓰일 HTTP 메서드와 URL(쿼리·fragment 제외) |
| 본문 | `nonce` | 서버가 `DPoP-Nonce` 헤더로 준 값(서버가 요구할 때). 미리 만든 proof를 무력화한다 |
| 본문 | `iat`, `jti` | 만든 시각과 고유 ID (재사용 방지) |
| 본문 | `ath` | 함께 보내는 access token의 해시 (리소스 서버 호출 시) |

| | mTLS (RFC 8705) | DPoP (RFC 9449) |
|---|---|---|
| 증명 위치 | TLS 연결 | HTTP 헤더 (애플리케이션) |
| 필요한 것 | 클라이언트 인증서, 그리고 TLS가 끝나는 지점(앞단 LB 등)에서 인증서를 확인해 뒤로 안전하게 넘기는 구성(10.3절, 15.10) | 키 쌍만 |
| 잘 맞는 곳 | 서버 간 연동, 금융권 | 모바일·브라우저 앱, 인증서를 다루거나 넘기기 어려운 구조 |
| refresh token도 묶나 | 가능 | 가능 (public client의 refresh 보호 수단) |

🧨 **이 방어의 한계**: 공격자가 클라이언트 안에서 코드를 실행할 수 있으면(브라우저 앱의 XSS, 클라이언트 소프트웨어 침해) DPoP의 보장은 사라진다(RFC 9449 11.4절). 키를 하드웨어 보안 모듈, OS 키 저장소, 브라우저의 추출 불가(non-extractable) 키에 두어 꺼내지 못하게 해도 길이 셋 남는다. ① 클라이언트가 켜져 있는 동안 그 키로 원하는 요청의 proof를 만들게 한다. ② `iat`를 미래 시각으로 잡은 proof를 미리 잔뜩 만들어 토큰과 함께 빼 간다. 그러면 클라이언트가 꺼진 뒤에도 쓸 수 있다(RFC 9449 11.2절). ③ 숨긴 iframe으로 새 authorization code 흐름을 돌려, **공격자 자신의 키**에 묶인 새 토큰을 받는다(RFC 9449 11.4절, RFC 10017 5.1.3절). ②는 서버가 `DPoP-Nonce` 헤더로 주는 예측할 수 없는 nonce를 proof에 넣게 하면 막힌다. 미리 만든 proof에는 아직 받지 않은 nonce를 넣을 수 없기 때문이다. nonce를 쓰지 않는다면 DPoP access token의 수명을 길게 두지 않는다(SHOULD NOT, RFC 9449 11.2절). ①과 ③은 DPoP로 막을 수 없고, 코드 실행 자체를 막아야 한다. 그래서 브라우저 앱에서 DPoP는 BFF(13장)를 대신하지 못한다.

💡 **방어 원리**: bearer token의 약점은 "문자열 하나가 곧 권한"이라는 데 있다. 발신자 제한은 권한을 **문자열 + 비밀키**의 조합으로 바꾼다. 비밀키는 네트워크로 전송되지 않으므로, 로그·프록시·가짜 서버 어디에서 토큰이 새도 키는 새지 않는다. 증명에 메서드·URL·시각·고유 ID가 들어가 있어서, 지나간 증명을 다시 쓰는 것도 막힌다.

#### 15.6.3 refresh token 보호

기본 원리는 8.4절(rotation과 재사용 탐지)에서 다뤘다. RFC 9700 4.14가 더하는 규칙을 정리한다.

| 누가 | 무엇을 | 강도 |
|---|---|---|
| 인증 서버 | 클라이언트마다 refresh token을 줄지 위험 평가로 결정 | MUST |
| 인증 서버 | refresh token을 사용자가 동의한 scope와 리소스 서버에 묶음 | MUST |
| 인증 서버 | public client의 refresh token은 발신자 제한 또는 rotation | MUST |
| 인증 서버 | rotation 재사용을 탐지하면, 누가 범인인지 모르므로 **현재 유효한 refresh token을 폐기** | rotation의 정의 |
| 인증 서버 | 비밀번호 변경, 인증 서버 로그아웃 같은 보안 이벤트 때 자동 폐기 | MAY |
| 인증 서버 | 일정 기간 쓰지 않은 refresh token은 만료 | SHOULD |

```
시점   정상 클라이언트          공격자               인증 서버
t0     RT1 보유               RT1 탈취             RT1 유효
t1     RT1 → AT2, RT2                            RT1 무효, RT2 유효 (RT1→RT2 관계 기억)
t2                            RT1 제출 ──────────► "무효화된 RT1 재사용!"
                                                  누가 범인인지 모름 → RT2까지 폐기
t3     RT2 제출 → 거부                            정상 클라이언트도 다시 로그인해야 함
```

순서가 반대여도(공격자가 먼저 쓰면) 정상 클라이언트의 제출이 재사용으로 탐지되어 공격자가 받은 토큰이 폐기된다. 대가는 정상 사용자도 다시 로그인해야 한다는 것이다.

🧨 **rotation의 한계 (브라우저 앱)**: XSS가 계속 살아 있으면 rotation으로도 탈취가 탐지되지 않는다. 원리는 13.4절 시나리오 2에서 봤다(RFC 10017 5.1.2절). 그래서 브라우저 앱은 rotation만으로 부족하고, 13장의 BFF 구조가 권장된다.

---

### 15.7 신원을 혼동시키는 공격

#### 15.7.1 클라이언트가 사용자인 척하기

🎯 **노리는 것**: 클라이언트 자신의 토큰으로 **사용자 리소스**에 접근하는 것.

🧨 **공격 원리**: JWT access token(RFC 9068)의 `sub`는 사용자가 위임한 토큰이면 **사용자 ID**, client_credentials 토큰이면 **클라이언트 ID**다. 둘이 같은 문자열 공간을 쓰면 혼동이 생긴다.

```
① 공격 클라이언트가 동적 등록 때 client_id를 "12345"(관리자 회원의 sub와 같은 값)로 고름
② client_credentials로 토큰 발급 → sub = "12345"
③ 리소스 서버: "sub = 12345 → 회원 12345의 권한"으로 판단 → 관리자 리소스에 접근
```

🛡️ **방어** (RFC 9700 4.15): 클라이언트 ID와 사용자 ID가 같은 공간을 쓴다면, 인증 서버는 클라이언트가 자기 client_id를 정하지 못하게 한다(SHOULD NOT allow). 피할 수 없다면 리소스 서버가 두 종류의 토큰을 구분할 수단을 준다(MUST).

💡 **방어 원리**: 혼동은 "같은 이름표가 두 종류의 주인을 가리킬 수 있다"에서 생긴다. 이름표 공간을 나누거나(예: 사용자 ID는 숫자, 클라이언트 ID는 `client:` 접두어), 토큰에 "사용자 위임 토큰인지"를 명시하면 섞일 수 없다. 리소스 서버 쪽에서는 사용자 리소스 API가 **사용자 위임 토큰만** 받도록, 예를 들어 grant 종류나 scope로 거르면 된다.

#### 15.7.2 OAuth를 로그인으로 쓸 때의 토큰 바꿔치기

🎯 **노리는 것**: 다른 앱에서 얻은 피해자의 access token을 우리 백엔드에 내밀어, **피해자 계정으로 로그인**하는 것.

🧨 **공격 원리**: 소셜 로그인을 붙인 모바일 앱에서 흔한 구조가 있다. 앱이 제공자 SDK로 access token을 받아 백엔드에 넘기고, 백엔드는 그 토큰으로 제공자의 사용자 정보 API(`/me` 같은 것)를 불러 나온 ID로 회원을 로그인시킨다.

```
[정상]
우리 앱 ──(제공자 로그인)──► access token ──► 우리 백엔드 ──► 제공자 /me ──► "회원 A" → 로그인

[공격]
① 공격자가 같은 제공자에 붙은 자기 앱(예: 무료 운세 앱)을 운영
② 피해자가 그 앱에 제공자 계정으로 로그인 → 공격자가 "피해자의 access token"을 가짐
③ 공격자가 그 토큰을 우리 백엔드의 로그인 API에 직접 보냄
④ 우리 백엔드 ──► 제공자 /me ──► "피해자"  →  공격자가 피해자 계정으로 로그인됨
```

핵심은 **access token에는 "어느 클라이언트에게 발급됐는지"를 클라이언트가 확인할 수단이 없다**는 점이다. RFC 6749 10.3절도 리소스 서버가 "이 토큰이 그것을 내민 클라이언트에게 발급된 것"인지 확인하는 방법을 정하지 않는다고 밝힌다. `/me`는 토큰이 유효하기만 하면 그 사람의 정보를 돌려준다. RFC 6819 4.4.2.6절이 이 위협을 "Token Substitution (OAuth Login)"으로 정리한다.

🛡️ **방어**

- 로그인 판단에는 **access token이 아니라 id_token을 쓰고, `aud`가 우리 client_id인지 검증**한다(9.2절, 9.9절). id_token은 "누구에게 발급했는지"를 서명해 담고 있다.
- id_token을 쓸 수 없는 제공자라면, 제공자가 "이 토큰이 어느 앱에 발급됐는지" 알려 주는 API로 우리 앱의 토큰인지 확인한다(제공자마다 API가 달라 문서 확인 필요).
- 백엔드 로그인 API가 앱에서 받은 토큰을 그대로 믿는 구조 자체를 피한다. 가능하면 백엔드가 직접 authorization code 흐름의 클라이언트가 된다.

💡 **방어 원리**: 로그인에 필요한 증거는 "이 사람이 인증됐다"가 아니라 "**이 사람이 우리에게** 인증됐다"다. access token은 리소스 서버에 내미는 출입증이라 받는 사람이 누구든 같은 모양이다. id_token은 `aud`에 받을 클라이언트를 박아 서명하므로, 다른 앱이 받은 id_token은 우리 검증에서 걸러진다(RFC 6819도 대책으로 "클라이언트에 대한 audience 제한을 지원하는 OpenID Connect 같은 프로토콜"을 든다).

#### 15.7.3 이미 다룬 신원 혼동 공격

| 공격 | 핵심 | 자세히 |
|---|---|---|
| id_token을 access token으로 사용 | `aud`, `typ` 검사 | 10.4절 |
| 이메일 기반 자동 계정 연결 | `(iss, sub)`로 식별, `email_verified` 확인, 기존 계정 재인증 | 9.3절 |
| 사용자 지정값(`partner-user-id`) 조작 | 사용자 값은 검증된 토큰에서만 | 16.8절 |

---

### 15.8 JWT 검증 함정

JWT는 서명을 검증해야만 의미가 있다. 그런데 검증 코드의 작은 실수가 서명 자체를 무력화한다. RFC 8725(JWT 모범 사례)가 정리한 함정이다.

| 함정 | 공격 원리 | 방어 | 강도 |
|---|---|---|---|
| `alg: none` 수용 | 공격자가 헤더를 `none`으로 바꾸면, 헤더를 믿는 라이브러리는 서명 검사 없이 통과시킨다 | 검증하는 쪽이 허용 알고리즘 목록을 지정하고 그 밖은 쓰지 않음. OAuth JWT access token은 `none` 금지 | MUST (RFC 8725 3.1), MUST NOT (RFC 9068) |
| RS256 → HS256 혼동 | 10.2절 참조. 공개된 RSA 공개키를 HMAC 비밀키로 써서 서명을 만든다 | 키 하나는 알고리즘 하나에만 쓰고, 검증 때 그 짝을 확인 | MUST (RFC 8725 3.1) |
| 약한 HS256 키 | 사람이 기억할 만한 문자열을 HMAC 키로 쓰면, 토큰 하나를 얻은 공격자가 오프라인에서 사전 대입으로 키를 찾는다 | 사람이 기억할 수 있는 비밀번호를 HMAC 키로 직접 쓰지 않음 | MUST NOT (RFC 8725 3.5) |
| `kid` 주입 | 키를 찾을 때 `kid` 값을 SQL이나 LDAP 조회에 그대로 넣으면 주입 공격이 된다 | `kid`를 검증·정제한 뒤 사용 | 권고 (RFC 8725 3.10) |
| `jku`·`x5u` 추종 | 헤더가 가리키는 아무 URL에서 키를 받아 오면, 공격자가 자기 키 주소를 넣어 위조 토큰을 통과시키거나, 서버가 내부망 주소를 호출하게 만든다(SSRF) | 키 주소는 설정(discovery의 `jwks_uri`)에서만 가져오거나 허용 목록과 대조 | SHOULD (RFC 8725 3.10) |
| 발급자와 키 불일치 | `iss`는 A인데 B의 키로 서명된 토큰을 받는다 | 서명 키가 그 `iss`의 것인지 확인 | MUST (RFC 8725 3.8) |
| `aud` 미검사 | 같은 발급자가 다른 서비스용으로 준 토큰을 받는다 (토큰 바꿔치기) | 자기 앞으로 발급된 토큰만 받음 | MUST (RFC 8725 3.9, RFC 9068 4) |
| 종류가 다른 JWT 혼동 | id_token, access token, logout token처럼 모양이 비슷한 JWT를 서로 바꿔 낸다 | 종류마다 검증 규칙이 서로를 거부하도록 설계 (`typ` 등) | MUST (RFC 8725 3.12) |

**공통 원리**: JWT의 헤더와 본문은 **공격자가 만든 값**일 수 있다. 그래서 "무엇으로 어떻게 검증할지"(알고리즘, 키를 가져올 주소, 믿을 발급자, 대상)는 **검증하는 쪽의 설정**이 정한다. 서명 검증 전의 헤더 값은 설정이 이미 허용한 범위 안에서 고르는 데만 쓴다. 예를 들어 `kid`로 **설정된 JWKS 안의** 키 하나를 고르거나, `typ`이 기대값과 다르면 일찍 거부하는 것(10.1절 ⓪)은 괜찮다. `alg` 값에 따라 검증 함수를 바꾸거나 `jku`가 가리키는 주소에서 키를 받아 오는 것은 안 된다.

```
❌ 위험한 순서                              ✅ 안전한 순서
토큰 헤더 읽기 → alg대로 검증 함수 선택       설정에 고정: alg=RS256, jwks_uri, iss, aud
          → jku 주소에서 키 받기               → 헤더의 kid로 "설정된 JWKS 안에서만" 키 선택
          → 검증                               → 고정된 alg로 서명 검증
                                              → iss·aud·exp 확인 (typ은 10.1절처럼 맨 앞에서 걸러도 된다)
```

---

### 15.9 화면과 브라우저를 노리는 공격

#### 15.9.1 postMessage 흐름 공격

일부 구현은 인가 응답을 HTTP 리다이렉트 대신 **팝업 창과 부모 창 사이의 `postMessage`**로 전달한다. 화면 이동 없이 팝업으로 로그인하는 SPA에서 흔하다.

🎯 **노리는 것**: 팝업에서 부모 창으로 넘어가는 code·토큰, 또는 클라이언트에 가짜 응답을 끼워 넣는 것.

🧨 **공격 원리**

| 실수 | 결과 |
|---|---|
| 인증 서버가 `postMessage(응답, "*")`처럼 **아무 origin에나** 보냄 | 공격자가 통제하는 창이 code·state를 읽음 |
| 인증 서버가 받는 쪽 origin을 등록값과 대조하지 않고, 요청에 들어온 origin으로 보냄 | 15.4.1과 같은 유출 |
| 클라이언트가 메시지를 받을 때 **보낸 쪽 origin을 확인하지 않음** | 공격자가 가짜 인가 응답을 끼워 넣음 (CSRF의 변형) |

🛡️ **방어** (RFC 9700 4.17)

```js
// 인증 서버(보내는 쪽): 정확한 클라이언트 origin을 지정한다. "*" 금지(MUST NOT)
window.opener.postMessage(
  { code: "c-5d1e", state: "st-8f2c" },
  "https://client.example"
);

// 클라이언트(받는 쪽): 보낸 쪽 origin을 정확히 비교한다(MUST)
window.addEventListener("message", (e) => {
  if (e.origin !== "https://auth.stg.idp.example") return;   // 정확한 문자열 비교
  handleAuthResponse(e.data.code, e.data.state);            // 이후 state 대조 등은 리다이렉트 방식과 동일
});
```

리다이렉트 방식에 적용하던 모든 보호(정확한 주소 비교, state, PKCE 등)를 postMessage 방식에도 똑같이 적용한다(MUST).

💡 **방어 원리**: `postMessage`의 두 번째 인자에 정확한 origin을 주면, **브라우저가** 그 origin이 아닌 창에는 메시지를 전달하지 않는다. 받는 쪽의 `e.origin`은 브라우저가 채우는 값이라 공격자가 위조할 수 없다. 이 두 값의 정확한 비교가 리다이렉트 방식의 "정확한 redirect URI 비교"에 해당한다.

#### 15.9.2 이미 다룬 화면·브라우저 공격

| 공격 | 핵심 | 자세히 |
|---|---|---|
| 클릭재킹 | 인증 서버가 `frame-ancestors`로 프레임 삽입 금지. RFC 9700은 클릭재킹 방지를 MUST, CSP 레벨 2 이상 사용을 SHOULD로 정함 | 7.8절 |
| 내장 웹뷰 | 네이티브 앱은 외부 브라우저 사용 (RFC 8252 MUST) | 12.2절 |
| custom scheme 가로채기 | https 링크(Universal Links·App Links) + PKCE | 12.4절 |
| XSS로 토큰 탈취 | 브라우저에 토큰을 두지 않는 BFF 구조 | 13장 |

---

### 15.10 TLS 종료 프록시의 헤더 위조

10.3절의 gateway처럼, TLS를 앞단 프록시에서 끝내고 뒤의 애플리케이션 서버에는 **HTTP 헤더로 정보를 넘기는** 구조가 흔하다. 원래 요청자의 IP(`X-Forwarded-For`), mTLS로 확인한 클라이언트 인증서(`X-Client-Cert` 같은 헤더), 검증한 사용자 ID 같은 값이다.

🎯 **노리는 것**: 애플리케이션 서버의 IP 제한이나 클라이언트 인증을 우회하는 것.

🧨 **공격 원리**

```
공격자 ── GET /api   X-Forwarded-For: 10.0.0.5   (허용된 내부 IP를 직접 적어 보냄) ──► 프록시
프록시 ── 외부 헤더를 지우지 않고 자기 값을 뒤에 덧붙임
          X-Forwarded-For: 10.0.0.5, 203.0.113.9 ──► 애플리케이션 서버
애플리케이션 서버: 첫 번째 값만 보고 "내부 IP네" → 허용
```

같은 원리로, 공격자가 "인증서 헤더"나 "사용자 ID 헤더"를 직접 넣어 보내면 다른 클라이언트나 사용자인 척할 수 있다. 프록시를 건너뛰고 내부망에서 애플리케이션 서버에 직접 닿을 수 있다면 더 쉽다.

🛡️ **방어** (RFC 9700 4.13)

| 무엇을 | 강도 |
|---|---|
| 프록시는 들어오는 요청에서 보안 관련 헤더를 **지우고 자기가 새로 씀** | MUST |
| 프록시와 애플리케이션 서버 사이의 구간을 엿보기·주입·재전송으로부터 보호 | MUST |

💡 **방어 원리**: 애플리케이션 서버는 "이 헤더는 프록시가 붙였다"고 믿는다. 프록시가 외부에서 온 같은 이름의 헤더를 지우고 자기 값만 쓰면, 그 믿음이 실제로 참이 된다. 내부 구간을 보호하면 프록시를 우회해 위조 헤더를 직접 넣는 경로도 막힌다. 10.3절에서 "내부 서비스도 원본 JWT를 다시 검증하라"고 한 것도 같은 이유다. 헤더 한 줄을 믿는 대신 서명된 토큰을 믿는다.

---

### 15.11 추측 공격과 값의 강도

🎯 **노리는 것**: authorization code, refresh token, 불투명 access token처럼 **값 자체가 권한인 것**을 맞혀서 쓰는 것.

🧨 **공격 원리**: 인증 서버가 code를 `1001`, `1002`처럼 순서대로 만들거나 짧은 난수로 만들면, 공격자는 token 엔드포인트에 값을 바꿔 가며 계속 요청한다. 하나라도 맞으면 남의 토큰을 받는다. 클라이언트의 state·nonce·verifier가 약해도 마찬가지로 CSRF·PKCE 방어가 무너진다.

🛡️ **방어**

| 무엇을 | 근거 |
|---|---|
| 공격자가 토큰·자격 증명을 한 번에 맞힐 확률을 2^-128 이하로 (2^-160 이하 권장) | OAuth 2.1 초안 7.7절 (MUST / SHOULD), RFC 6749 10.10절 |
| 암호학적 난수 생성기로 만든다 (Python `secrets`, Java `SecureRandom`, Node `crypto.randomBytes`) | 해석 |
| token 엔드포인트의 실패 요청 횟수를 제한한다 | 해석 |
| code는 짧은 수명·일회용 (7.1절) | RFC 6749 4.1.2절 |

**흔한 실수**: UUID v4를 토큰으로 쓰는 것. UUID v4는 무작위 비트가 122개라 2^-128 기준에 못 미친다. `random.random()`처럼 암호용이 아닌 난수 함수로 만드는 것도 예측될 수 있어 위험하다.

💡 **방어 원리**: 2^128은 약 3.4 × 10^38이다. 초당 1조 번 시도해도 모두 해 보려면 10^19년 넘게 걸린다. 값이 충분히 길고 예측할 수 없으면 "맞히기"는 현실적인 공격이 아니게 된다. 여기에 시도 횟수 제한과 짧은 수명이 더해지면 확률은 더 떨어진다. 7.3절의 state(16바이트 = 128비트 이상)와 code_verifier(32바이트 = 256비트) 규칙도 같은 기준에서 나온다.

### 15.12 쓰지 말아야 할 방식

| 방식 | 무엇이 문제인가 | 표준의 입장 |
|---|---|---|
| implicit (`response_type=token`) | access token이 URL(fragment)로 브라우저를 거쳐 전달되어 유출(15.4)과 끼워 넣기(15.5.2)에 노출된다. 발신자 제한도 걸 수 없다 | RFC 9700: SHOULD NOT. RFC 10017(브라우저 앱): MUST NOT. OAuth 2.1 초안: 삭제 |
| password (ROPC) | 클라이언트가 사용자 비밀번호를 직접 받는다. 착한 클라이언트라도 비밀번호가 새는 곳이 늘고, 사용자가 "아무 앱에나 비밀번호를 넣는" 습관을 들인다. 2단계 인증, WebAuthn(패스키)과도 맞지 않는다 | RFC 9700: MUST NOT. OAuth 2.1 초안: 삭제 |
| URL 쿼리로 access token 보내기 | 로그·히스토리·Referer로 샌다 | RFC 9700: MUST NOT |
| PKCE plain | challenge가 곧 verifier라 요청 URL만 보면 verifier를 안다 | RFC 9700: S256 SHOULD. OAuth 2.1 초안: 삭제 |
| SPA·앱에 client_secret 넣어 배포 | 설치 파일을 열면 누구나 secret을 꺼낸다. secret이 아무것도 증명하지 못한다 | RFC 10017: 인증 서버는 브라우저 앱에 공유 secret을 요구하면 안 됨(MUST NOT), 요구하더라도 public client로 취급(MUST) |

### 15.13 방어 장치와 막는 공격 한눈에 보기

어떤 방어 장치가 어떤 공격을 막는지 거꾸로 정리하면, 장치 하나를 빼먹었을 때 무엇이 열리는지 보인다.

| 방어 장치 | 막는 공격 | 담당 |
|---|---|---|
| redirect URI 정확 일치 | redirect 조작, 검증 부족, open redirector와의 결합, (mix-up 탐지 보조) | 인증 서버 |
| state (세션에 묶은 일회용 값) | CSRF, (PKCE 다운그레이드 보조) | 클라이언트 |
| PKCE S256 | code 가로채기, code injection, CSRF | 클라이언트 + 인증 서버 |
| challenge 없는 code의 verifier 거부 | PKCE 다운그레이드 | 인증 서버 |
| nonce | id_token 재사용, (confidential OIDC client의 code injection, CSRF) | 클라이언트 |
| 인가 응답의 `iss` 대조 | mix-up | 클라이언트 |
| code 일회용·짧은 수명 | code 재사용, 히스토리·Referer 유출 피해 축소 | 인증 서버 |
| Referrer-Policy, 콜백 페이지의 외부 자원 금지 | Referer 유출 | 클라이언트 + 인증 서버 |
| 303 리다이렉트 | 307 비밀번호 유출 | 인증 서버 |
| `frame-ancestors` | 클릭재킹 | 인증 서버 |
| 시스템 브라우저, https 앱 링크 | 내장 웹뷰 탈취, custom scheme 가로채기 | 네이티브 앱 |
| `aud` 검사 | 가짜·침해된 리소스 서버의 토큰 재사용, 토큰 종류 혼동 | 리소스 서버 |
| `typ` 검사 | id_token 등 다른 JWT 혼동 | 리소스 서버 |
| 허용 알고리즘 고정 | `alg: none`, RS256→HS256 혼동 | 토큰을 검증하는 모든 쪽 |
| 발신자 제한 (mTLS, DPoP) | 훔친 access·refresh token 사용 | 인증 서버 + 리소스 서버 |
| refresh rotation + 재사용 탐지 | refresh token 탈취 | 인증 서버 |
| `(iss, sub)` 식별 + 기존 계정 재인증 | 이메일 기반 계정 탈취 | 클라이언트 |
| 프록시의 헤더 정제 + 내부 구간 보호 + 내부 재검증 | 헤더 위조 | 앞단·내부 서비스 |
| BFF | 브라우저 XSS로 토큰 탈취 | 브라우저 앱 |
| 동의 화면의 클라이언트 정보 표시 + 연결 앱 철회 화면 | 동의 피싱 | 인증 서버 |
| 클라이언트 미인증 시 자동 승인 금지 | 기억한 동의 악용 | 인증 서버 |
| id_token의 `aud`로 로그인 판단 | OAuth 로그인 토큰 바꿔치기 | 클라이언트 백엔드 |
| 2^128 이상의 무작위성 + 시도 제한 | 추측 공격 | 인증 서버 + 클라이언트 |
| 받은 파라미터를 외부 입력으로 검증 | open redirect, 주입 | 인증 서버 + 클라이언트 |
| 토큰 암호화 저장, secret과 분리 | 클라이언트 저장소 유출 | 클라이언트 |

---

## 16. 사례: 클라이언트 앱 × IdP 서비스 연동

이 장은 앞 장의 개념이 하나의 연동 사례에서 어떻게 조합되는지 보여 준다. 두 서비스가 정한 구조와, 구현 때 남는 결정 사항을 정리했다.

### 16.1 처음 가정한 구조와 실제 구조의 차이

설계 초기에는 "클라이언트 앱 네이티브 채팅 화면 → 앱 백엔드 → IdP 서비스 API gateway → 코어 서비스"를 가정했다. 실제 구조는 달랐다.

| 항목 | 처음 가정 | 실제 구조 |
|---|---|---|
| 서비스 화면 | 클라이언트 앱 네이티브 화면 | **클라이언트 앱 웹뷰가 IdP 서비스 웹을 iframe으로 감싸고, 클라이언트 앱 서버가 IdP 서비스 토큰을 붙여 중계** |
| 로그인 화면 | 시스템 브라우저 시트 | **클라이언트 앱 웹뷰 최상위 화면** (12.1절 B) |
| IdP 서비스 → 클라이언트 앱 호출 | 없음 | **있음.** client_credentials로 클라이언트 앱 제휴사 API 호출 |
| access token 용도 | 서비스 API 호출 | 처음엔 "로그인 확인용으로만 쓰고 버림" → 이후 "웹뷰 중계와 Agent API에 계속 사용"으로 변경 (16.11절) |

### 16.2 구조 한눈에

| 구분 | 방식 | 클라이언트 → 서버 |
|---|---|---|
| ① 계정 연결 | OAuth 2.0 Authorization Code + PKCE(S256) | 클라이언트 앱 → IdP 인증 서버 |
| ② IdP 서비스 → 클라이언트 앱 API 호출 | OAuth 2.0 Client Credentials | IdP 서비스 서버 → 클라이언트 앱 제휴사 API |
| ③ 서비스 화면 | 클라이언트 앱 웹뷰가 IdP 서비스 웹을 iframe으로 감쌈. 클라이언트 앱 서버가 IdP 서비스 토큰을 붙여 전달 | 클라이언트 앱 서버 → IdP 서비스 웹 |

```
┌───────── 클라이언트 앱 영역 ─────────┐      ┌─────────── IdP 서비스 영역 ───────────┐
│ 사용자 기기 (앱 웹뷰)                │      │ 인증 서버                              │
│ 클라이언트 앱 서버                   │      │   OAuth/OIDC 인증 서버, 가입·로그인 화면 │
│   화면, IdP 서비스 토큰 보관·중계     │      │ IdP 서비스 서버                         │
│ 제휴사 API                          │      │   회원 연결 처리, 서비스 웹·Agent API    │
│   relay/info, IdP 서비스가 부르는 API │      │                                       │
└─────────────────────────────────────┘      └───────────────────────────────────────┘
```

| 단계 | 언제 | 핵심 |
|---|---|---|
| 사전 등록 | 개발 전 1회 | 서로의 클라이언트 정보, redirect_uri, IP 교환 (4장, 부록 B) |
| 진입 | 메뉴를 누를 때마다 | 이용 제한 확인 → 연결 여부 조회 |
| 계정 연결 | 최초 1회 | 연결 동의 → 인증 서버 로그인·가입 → 앱 사용자 조회 → 토큰 발급 |
| 서비스 화면 | 매번 | 클라이언트 앱 웹뷰 iframe, 클라이언트 앱 서버가 IdP 서비스 토큰을 붙여 중계 |
| 토큰 갱신 | access 만료 시 | 클라이언트 앱 서버가 refresh token으로 갱신 |
| IdP 서비스 → 클라이언트 앱 API | 필요할 때 | client_credentials 토큰 + `partner-user-id` |
| 연결 해제·탈퇴 | 사용자가 끊을 때 | 규격 회신 대기 |

### 16.3 진입: 메뉴를 누를 때마다

```
사용자 ── 클라이언트 앱에서 IdP 서비스 메뉴 클릭 (클라이언트 앱 로그인 상태)
   │
   ├─ 이용 제한 대상인가? (만 14세 미만)
   │    └─ 예 → "14세 이상만 이용 가능" 안내 후 클라이언트 앱으로 복귀
   │
   └─ 클라이언트 앱 웹뷰 → GET {client}/relay/api/v1/links/idp
        ├─ 200 연결됨  → 서비스 화면
        └─ 404 미연결  → 계정 연결
```

이 단계는 전부 클라이언트 앱 안에서 끝나고 IdP 서비스는 관여하지 않는다.

### 16.4 계정 연결: 최초 1회

```
사용자(웹뷰)     클라이언트 앱 서버    인증 서버            IdP 서비스 서버      제휴사 API
  │                │                   │                      │                    │
  │ ① 서비스 연결 이용 동의 (클라이언트 앱 화면)                    │                    │
  │   제3자 제공: 클라이언트 앱 → IdP 서비스, 항목 = 서비스 ID · 인증토큰│                │
  ├───────────────►│                   │                      │                    │
  │                │ ② state·nonce·code_verifier 생성, 세션 저장  │                    │
  │◄───────────────┤ 302 → IdP 인증 서버 /oauth/authorize/ (웹뷰 최상위 화면, iframe 아님)       │
  ├───────────────────────────────────►│                      │                    │
  │ ③ IdP 서비스 화면                       │                      │                    │
  │   · 약관 · 만 14세 이상 확인 · 개인정보 수집·이용 동의          │                    │
  │   · 신규: 이메일·비밀번호 입력 → 이메일 인증 → 계정 생성         │                    │
  │   · 기존 회원: 로그인                 │                      │                    │
  ├───────────────────────────────────►│                      │                    │
  │                │                   │ ④ state 전달 (IdP 인증 서버 내부 방식) ───►│          │
  │                │                   │                      │ ⑤ 클라이언트 앱용 토큰 확보 (대개 캐시)
  │                │                   │                      │ ⑥ GET /api/relay/info?state=…
  │                │                   │                      │    Bearer <IdP 서비스의 client_credentials 토큰>
  │                │                   │                      ├───────────────────►│
  │                │                   │                      │◄── sub(앱 사용자 ID), exp
  │                │                   │                      │ ⑦ 연결 기록 저장     │
  │◄───────────────────────────────────┤ ⑧ 302 → redirect_uri?code&state&iss     │
  ├───────────────►│ ⑨ callback 처리 (7.5절 순서)                 │                    │
  │                ├──────────────────►│ ⑩ POST /oauth/token/ (code, code_verifier, Basic)
  │                │◄──────────────────┤  access(60분) · refresh(14일) · id_token(RS256)
  │                │ ⑪ id_token 검증, (iss, sub)로 IdP 서비스 회원 저장, 토큰은 서버에만 보관
  │◄───────────────┤ ⑫ 연결 완료 → 서비스 화면                     │                    │
```

**단계별로 지킬 것**

- **②~⑧은 웹뷰 최상위 화면에서 진행한다.** IdP 인증 서버 로그인 화면은 iframe 삽입을 허용하지 않는다(12.3절).
- **③의 동의는 IdP 서비스 화면에서 받는다.** 동의 항목은 이용약관, 만 14세 이상 확인, 개인정보 수집·이용(이메일·비밀번호·서비스 이용 대화, 가명처리 후 품질 개선과 학습에 활용), 마케팅 수신(선택)이다. 이름·전화번호·CI는 받지 않는다.
- **⑩의 authorization code는 60초 안에 한 번만 쓴다.** 클라이언트 인증은 `client_secret_basic`만 허용한다.
- **⑪의 회원 식별은 `(iss, sub)`로 한다.**

#### state를 번호표로 재활용하는 확장

OAuth 표준에서 state는 클라이언트를 위한 값이고, 인증 서버는 해석하지 않는다(7.2절). 이 연동 규격은 여기에 하나를 더 얹었다.

```
GET {클라이언트 앱 제휴사 API}/api/relay/info?state=st-8f2c
Authorization: Bearer <IdP 서비스의 client_credentials 토큰>
→ { "sub": "앱 사용자 ID", "exp": … }
```

클라이언트 앱은 state를 만들 때 "이 state는 어느 클라이언트 앱 사용자의 연결 요청인가"를 자기 서버에 기록해 둔다. 제휴사가 **그 state를 들고 와서 물으면 해당 클라이언트 앱 사용자를 알려 준다.** 클라이언트 전용이던 state를 **연결 요청 번호표**로 재활용한 것이다.

- state는 발급 후 **10분 안에만** 조회된다. 만료됐거나 다른 제휴사의 state면 404다.
- 이 확장 때문에 OAuth에서는 의미 없던 state를 **IdP 인증 서버가 읽고 보관하고 넘겨야** 하는 일이 생겼다. 이 부분은 OAuth 표준 밖이라 표준에 답이 없고, IdP 서비스 내부에서 정해야 한다(16.12절).
- 번호표가 된 state는 성격이 바뀐다. 원래는 URL에 노출돼도 괜찮은 값이었지만, 이제는 클라이언트 앱 사용자 식별자를 조회할 수 있는 열쇠다. 조회에 IdP 서비스의 client_credentials 토큰이 필요하고 10분 뒤 만료되므로 위험은 제한돼 있지만, **로그에 state 값을 남기지 않는다.**

#### ⑤와 ⑥은 한 번의 호출이 아니다

⑤의 토큰은 사용자와 무관한 "IdP 서비스 서버의 출입증"이라서, 한 번 받으면 30분 동안 모든 사용자의 연결 요청에 재사용한다. 실제로 매 연결마다 일어나는 것은 ⑥이다.

#### relay/info로 앱 사용자 ID를 받아야 하는 이유

클라이언트 앱 → IdP 서비스 요청은 IdP 서비스 토큰으로 오고, IdP 서비스 → 클라이언트 앱 요청은 `partner-user-id`에 IdP 서비스 회원 ID를 넣는다. 둘 다 앱 사용자 ID 없이도 동작한다. 그래도 필요한 이유는 세 가지다.

1. **동의받은 정보의 전달 통로다.** 클라이언트 앱 동의 화면에서 사용자가 동의한 "클라이언트 앱 → IdP 서비스 제3자 제공" 항목이 서비스 ID다. relay/info는 그 동의에 따라 정보를 넘겨받는 API다.
2. **연결 해제·탈퇴 처리에 필요하다.** 클라이언트 앱이 해제를 어떤 식별자로 알려 올지는 미정이다. 앱 사용자 ID로 알려 온다면 IdP 서비스 쪽에 그 값이 있어야 해당 회원을 찾아 데이터를 지울 수 있다.
3. **신규 가입과 기존 회원 연결을 구분하는 용도로 설계된 API다.** CI를 받는 제휴사는 이 응답의 CI로 기존 회원을 찾는다. IdP 서비스는 CI를 받지 않으므로 이 용도로는 쓰지 않고, 사용자가 직접 로그인하는 것으로 대신한다(16.10절).

#### ⑦ 연결 기록에 남기는 것

| 항목 | 예 | 용도 |
|---|---|---|
| IdP 서비스 회원 ID | `12345` | IdP 서비스 쪽 주인 |
| 제휴사 | `client-app` (client_id) | 제휴사가 늘어날 때 구분 |
| 제휴사 사용자 ID | relay/info의 sub | 해제 통지 처리, 삭제 의무 이행 |
| 연결 시각, 상태 | 연결 시각, `active` | 해제 시 `revoked`로 변경 |
| 동의 이력 | 약관·만 14세·개인정보 동의 버전과 시각 | IdP 서비스 화면에서 받은 동의의 증빙 |

이 기록은 **code를 발급하기 전에** 끝나야 한다. code가 나간 뒤에 기록에 실패하면 클라이언트 앱은 연결 완료로 알고 IdP 서비스는 연결 정보가 없는 상태가 된다.

### 16.5 서비스 화면: iframe + 클라이언트 앱 서버 중계

```
클라이언트 앱 웹뷰
  └─ <iframe src="https://app.client.example/web/relay/idp/">
        │ ① 요청 (사용자 기기 → 클라이언트 앱 서버, 클라이언트 앱 로그인 상태)
        ▼
     클라이언트 앱 서버
        │ ② 보관 중인 IdP 서비스 access token을 붙여 전달 (헤더 형식은 아직 정해지지 않음)
        ▼
     IdP 서비스 웹 / Agent API
        │ ③ 토큰 검증 (IdP 인증 서버 JWKS) → sub로 IdP 서비스 회원 식별 → 요청 처리
        ▼
     응답 → 클라이언트 앱 서버 → iframe
```

- **IdP 서비스 토큰은 클라이언트 앱 서버에만 있고 사용자 기기로 내려가지 않는다.** 연동 규격에 명시돼 있다.
- 연동 규격은 CORS(다른 출처의 JS가 API를 부를 수 있는지 정하는 규칙)·CSRF 허용 출처에 환경별 클라이언트 앱 서버 주소를 넣어 달라고 요구한다.
- 클라이언트 앱 쪽 개인정보 처리는 웹뷰에서 하는 최소 범위뿐이라서, 대화 내용 속 개인정보의 가명처리는 IdP 서비스의 Agent 설계에서 따로 다뤄야 한다.

### 16.6 토큰 갱신

```
클라이언트 앱 서버 ── POST IdP 인증 서버 /oauth/token/   (Basic client_id:client_secret)
              grant_type=refresh_token&refresh_token=rt-…
          ◄── 200: access·refresh·id_token 모두 새 값 (rotation)
              400 invalid_grant: 만료·재사용·연결 해제 → 계정 연결부터 다시
              401 invalid_client: secret 오류
```

refresh token은 마지막으로 사용한 뒤 14일 동안 유효하다. 사용자가 14일 넘게 들어오지 않으면 연결을 다시 해야 한다. rotation이므로 클라이언트 앱 서버는 같은 사용자의 갱신 요청을 한 번에 하나씩 보내야 한다(8.4절).

### 16.7 IdP 서비스 → 클라이언트 앱 API

```
IdP 서비스 서버 ── POST {partner.client.example}/oauth/token   (Basic idp:secret, client_credentials)
             ◄── access_token (JWT RS256, 30분, refresh 없음 → 만료 전까지 재사용)
IdP 서비스 서버 ── {METHOD} {partner.client.example}/api/{영역}/…
                 Authorization: Bearer <token>
                 partner-user-id: <IdP 서비스 회원 식별자>   ← 클라이언트 앱이 연결된 사용자로 변환
```

| 오류 | 의미 |
|---|---|
| 401 | 인증 실패나 토큰 만료 |
| 403 | 필요한 scope가 없거나, `partner-user-id`에 연결된 사용자가 없음 |
| 404 | 등록되지 않은 경로나 만료된 state |

### 16.8 partner-user-id와 신뢰 구조

client_credentials 토큰에는 "어느 사용자 건으로 왔는지"가 들어 있지 않다. 그래서 매 요청마다 **`partner-user-id` 헤더에 IdP 서비스 회원 식별자를 적어 대상 사용자를 따로 알린다.** 이름이 "partner-user-id"인 이유는 클라이언트 앱 입장에서 IdP 서비스가 partner(제휴사)이기 때문이다. 클라이언트 앱 사용자 ID가 아니라 **IdP 서비스 쪽 ID**를 보내고, 클라이언트 앱이 연결 표로 바꿔 준다.

```
[계정 연결 때 클라이언트 앱이 저장해 둔 표]
  클라이언트 앱 사용자           IdP 서비스 회원 식별자 (iss, sub)
  app-user-8f3c   ↔   (https://auth.stg.idp.example, "12345")

[IdP 서비스 → 클라이언트 앱 API 호출]
  Authorization: Bearer eyJ…              ← "나는 IdP 서비스 서버다"
  partner-user-id: 12345                  ← "IdP 서비스 회원 12345 건이다"
                  │
                  ▼
  클라이언트 앱: 표에서 12345 → app-user-8f3c 로 변환해서 처리. 연결된 사용자가 없으면 403
```

#### 🛡️ 공격: 서버 자격 증명 유출 또는 사용자 지정값 조작

**공격 원리**: 토큰은 "IdP 서비스 서버"만 증명하고, 사용자는 IdP 서비스가 헤더에 적은 대로 믿는다. 그래서 두 가지 경로로 다른 사용자 건을 건드릴 수 있다.

- IdP 서비스 서버의 클라이언트 앱용 secret이나 토큰이 새면, 공격자는 헤더 값만 바꿔 가며 **연결된 모든 사용자** 건으로 클라이언트 앱 API를 부를 수 있다. 사용자별 토큰이 아니라서 피해가 한 사람으로 한정되지 않는다.
- Agent가 도구로 클라이언트 앱 API를 부르는 구조에서, 회원 ID를 사용자 입력이나 LLM 출력에서 가져오면 **프롬프트 인젝션**으로 다른 회원 ID를 넣게 만들 수 있다.

**방어**

- secret은 비밀 저장소에만 둔다. 로그, 소스, 메신저에 남기지 않는다.
- `partner-user-id`는 반드시 **지금 검증된 요청의 사용자**, 즉 앞단에서 토큰을 검증하고 얻은 `sub`에서 꺼낸다. 메시지 내용이나 LLM 출력에서 가져오지 않는다.
- 어떤 Agent·도구가 클라이언트 앱 API를 부를 수 있는지 제한한다. client_credentials 토큰을 Agent 런타임 전체가 공유하지 않게 한다.

**방어 원리**: 사용자를 지정하는 값의 **출처를 신뢰 경계 안(검증된 토큰)으로 고정**하면, 신뢰할 수 없는 입력(사용자 메시지, LLM 출력)이 그 값을 바꿀 수 없다.

### 16.9 연결 해제·탈퇴: 미정

| 항목 | 상태 |
|---|---|
| 클라이언트 앱 → IdP 서비스 해제 통지 API 규격 | 아직 정해지지 않음 |
| 해제 시 IdP 서비스가 할 일 (제안) | 클라이언트 앱에서 받은 서비스 ID·토큰과 앱 채널 대화를 삭제하거나 익명처리하고, IdP 서비스 계정은 유지 |
| 클라이언트 앱 측 조건 | 계정 유지는 가능해 보이나, 연결 시 필수 동의에 관련 문구를 넣어야 하고 법무 검토가 필요 |
| 해제 안내 문구 | "모두 삭제" 같은 문구가 계정 유지 방식과 맞는지 확인 필요 |
| 인증 서버 쪽 | 해제가 확정되면 해당 refresh token을 폐기한다(8.8절). 폐기된 뒤 갱신하면 `invalid_grant`. 단 이미 발급된 access token은 남은 수명(최대 60분) 동안 유효하므로, 해제 즉시 차단이 필요하면 서비스 API 쪽에 연결 상태 확인을 둔다 |

### 16.10 CI와 동일인 식별

CI는 **연계정보(Connecting Information)**다. 주민등록번호를 대신해 **서로 다른 서비스에서 같은 사람인지 확인하는 데 쓰는 개인 식별값**이고, 휴대폰 본인인증이나 아이핀 같은 본인확인 절차를 거치면 본인확인기관이 발급한다.

```
주민등록번호 ──► 본인확인기관이 공통 비밀키로 일방향 암호화 ──► CI (88바이트 문자열)
```

- 같은 사람이면 어느 서비스에서 받든 같은 값이 나오므로, 두 서비스가 CI를 비교하면 동일인인지 알 수 있다.
- CI에서 주민등록번호를 되돌려 낼 수는 없다.
- 비슷한 값으로 **DI(중복가입확인정보)**가 있다. 서비스마다 다른 값이 나오므로 한 서비스 안에서 중복 가입을 막는 데만 쓴다.

```
[CI가 있는 제휴사]
클라이언트 앱 사용자의 CI ──► 제휴사 회원 DB에서 같은 CI 검색
                     ├─ 있음 → "연결 가능한 계정을 찾았어요" → 바로 연결
                     └─ 없음 → 제휴사 가입·로그인 화면

[IdP 서비스: CI 없음]
CI 조회 단계를 건너뜀 ──► 바로 IdP 서비스 가입·로그인 화면
                         (기존 회원이면 이메일·비밀번호로 로그인해 직접 연결)
```

IdP 서비스는 가입할 때 이메일 인증만 하고 본인인증을 하지 않아 CI가 없다. 그래서 CI 조회 단계는 생략하고, 클라이언트 앱에서 CI를 받지 않으며, 동일인 확인은 사용자의 로그인에 맡긴다. 나중에 실명 확인이 필요한 기능(예: 신고서 제출)을 열면 그때 본인인증과 고유식별정보 별도 동의가 필요해질 가능성이 크다.

### 16.11 토큰 규격이 바뀐 이력

| 시점 | access token | refresh token | 클라이언트 앱이 토큰을 쓰는 용도 |
|---|---|---|---|
| 초기 연동 가이드 | 5분 | 없음 | 쓸 일 없음. id_token의 `sub`만 저장하고 로그인 상태는 클라이언트 앱 자체 세션으로 유지 |
| 변경 후 | 60분 | 마지막 사용 후 14일, rotation | iframe 웹뷰 중계와 Agent API 호출에 계속 사용 |

처음 설계는 "OAuth 흐름 위에서 id_token만 쓰는" 로그인 연동이었다(9.1절). 클라이언트 앱 개발팀이 "연동 유지를 위해 access token을 웹뷰 중계와 Agent API에 쓰겠다"고 하면서, OAuth의 권한 위임까지 본래 의미대로 쓰는 구조가 됐다.

### 16.12 구현 때 남는 일과 별도로 정할 항목

**구현 전에 확인할 일**

1. IdP 서비스 → 클라이언트 앱 토큰 발급 경로를 환경별로 점검한다(연결 시간 초과, `401 invalid_client` 같은 오류). 계정 연결의 relay/info 조회가 여기에 달려 있다.
2. 서비스 화면에서 클라이언트 앱이 IdP 서비스 토큰을 어떤 형식으로 붙이는지 확정한다.
3. 운영 환경의 redirect_uri, 클라이언트 정보, CORS 허용 출처를 교환한다.
4. 연결 해제 통지 API 규격과 법무 검토 결과를 확정한다.
5. 연동 가이드의 토큰 규격을 변경 내용에 맞게 갱신한다.

**별도로 정할 항목** (이 문서에서는 결정하지 않는다)

| 항목 | 관련 절 |
|---|---|
| 서비스 API용 scope 분리와 access token의 `aud` 검사 | 9.5절, 10.1절 |
| IdP 인증 서버 discovery의 서명 알고리즘 광고 정리, OAuth 2.1 준수 확인 | 10.2절, 17장 |
| relay/info 호출 주체와 state 처리, 실패 시 동작 | 16.4절 |
| 연결표의 1:1 여부, 해제 통지 식별자 | 16.4절, 16.9절 |
| 클라이언트 앱 웹뷰 로그인의 비밀번호 노출 구조 | 12.2절 |

---

## 17. OAuth 2.1: 무엇이 달라졌나

OAuth 2.1은 새 기능을 더한 버전이 아니다. 2.0(2012년) 이후 나온 보안 권고(PKCE, 보안 모범 사례 RFC 9700 등)를 하나로 합치고 위험한 방식을 뺀 **정리판**이다. 그래서 grant_type이 오히려 줄었다(6.7절).

**상태 (2026-11-03 기준)**

| 항목 | 내용 |
|---|---|
| 최신판 | `draft-ietf-oauth-v2-1-17` (2026-10-31) |
| RFC 여부 | **아니다.** 작업 그룹 문서 단계이고, IETF 승인 기구(IESG)에 제출하는 목표 시점이 2026년 12월이다 |
| 승인되면 | RFC 6749(OAuth 2.0)와 RFC 6750(Bearer token 사용법)을 대체한다 |

그래서 이 장의 2.1 내용은 **"초안 17판 기준이며 RFC 발행 전에 바뀔 수 있다"**는 단서를 달고 읽어야 한다. 다만 PKCE 필수, implicit·password 삭제 같은 핵심은 초안 내내 유지돼 왔다.

### 17.1 2.0 대비 변화

| 항목 | OAuth 2.0 | OAuth 2.1 초안 17판 | 왜 바꿨나 | 자세히 |
|---|---|---|---|---|
| PKCE | 별도 표준(RFC 7636), 사실상 public client용 | authorization code 흐름에 **필수**. 예외는 confidential client이면서 OIDC nonce 구현이 확실할 때뿐 | code 가로채기·끼워 넣기 방지 | 7.3절 |
| PKCE plain | 조건부 허용 | **금지** | challenge 노출이 곧 verifier 노출 | 7.3절 |
| implicit | 허용 | **삭제** | 토큰이 URL로 노출됨. RFC 9700도 쓰지 말라고 권고(SHOULD NOT) | 6.7절, 8.1절 |
| password (ROPC, Resource Owner Password Credentials) | 허용 | **삭제** | 클라이언트가 사용자 비밀번호를 직접 받음. RFC 9700은 금지(MUST NOT) | 2.1절, 6.7절 |
| redirect_uri 비교 | 전체 등록을 권장하되 일부 등록도 허용 | 전체 등록, **정확한 문자열 일치**. loopback 주소(127.0.0.1)의 포트만 예외 | 부분 일치를 노린 code 탈취 | 4.4절 |
| token 요청의 redirect_uri | authorize에 넣었으면 필수 | **제거** | PKCE가 같은 공격을 막음 | 4.4절 |
| 클라이언트 인증 | Basic 지원 MUST, 본문 방식 비권장 | 본문 방식 지원 MUST, Basic은 MAY | Basic의 URL 인코딩 상호운용 문제 | 4.3절 |
| 인가 응답의 `iss` | 없음 (RFC 9207로 추가) | **필수** | mix-up 공격 방지 | 7.5절 |
| access token을 URL 쿼리로 보내기 | 정의돼 있으나 권장하지 않음(RFC 6750) | **금지**. 리소스 서버도 쿼리의 토큰을 무시해야 함 | 로그·히스토리·Referer로 유출 | 15.4.4, 15.12 |
| public client의 refresh token | 규칙 없음 | rotation 또는 sender-constrained **필수** | 탈취 탐지 | 8.4절 |
| client_credentials | confidential client만 (RFC 6749 4.4절, MUST) | 같음 (2.1 초안 4.2절) | 바뀐 것 없음. 2.0부터 secret을 보관할 수 없는 앱은 쓸 수 없었다 | 6.2절 |

loopback 포트 예외는 데스크톱 앱처럼 `http://127.0.0.1:{임의 포트}/callback`으로 결과를 받는 네이티브 앱을 위한 것이다. 앱이 실행될 때마다 비어 있는 포트를 고르므로 포트까지 고정해 등록할 수 없다.

### 17.2 IdP 인증 서버 대조

| 2.1 초안 요구사항 | IdP 인증 서버 (연동 가이드 기준) | 판정 |
|---|---|---|
| authorization code에 PKCE 필수 | S256 필수. 없거나 S256이 아니면 `invalid_request` | ✅ |
| PKCE plain 금지 | S256만 허용 | ✅ |
| redirect_uri 정확히 일치 | 끝의 `/`와 포트까지 글자 단위 대조 | ✅ |
| 인가 응답에 `iss` 필수 (오류 응답 포함) | 성공 응답에는 항상 포함. 요청값 오류 응답에는 넣지 않음(연동 가이드 예시) | ⚠️ RFC 9207과 2.1 초안은 오류 응답에도 요구 |
| code 일회용·짧은 수명 | 60초, 1회 | ✅ |
| refresh token 재사용 방지 | rotation 적용 | ✅ (클라이언트 앱은 confidential client라 필수는 아님) |
| token 요청의 redirect_uri | 받으면 authorize 때 값과 대조 | ✅ 2.0·2.1 클라이언트를 함께 받는 서버의 규칙과 맞음 |
| 클라이언트 인증: 본문 방식 지원 필수 | **Basic만 허용, 본문 방식은 401** | ⚠️ 2.0 기준으로는 정상, 2.1 초안 기준으로는 불일치 |
| implicit 삭제 | 가이드에 언급 없음 | ❓ discovery로 확인 |
| password 삭제 | 가이드에 언급 없음 | ❓ discovery로 확인 |
| access token을 URL 쿼리로 받지 않음 | 가이드에 언급 없음 | ❓ 리소스 서버 구현 확인 |

⚠️ 두 항목(본문 방식 클라이언트 인증, 오류 응답의 iss)은 2.0 기준으로는 문제가 아니지만, 2.1 초안을 따르려면 바꿔야 한다. 어떻게 할지는 별도 논의 예정이다(16.12절). 남은 ❓ 중 앞의 둘은 discovery 문서 한 번 조회로 확인할 수 있다.

```bash
curl -s https://auth.stg.idp.example/.well-known/openid-configuration | jq '{
  response_types_supported,               # "code" 말고 다른 값(token, id_token, 또는 이를 포함한 조합)이 있으면 토큰을 URL로 내주는 방식이 열려 있음
  grant_types_supported,                  # "password"가 있으면 password 방식 허용
  code_challenge_methods_supported,       # "plain"이 있으면 PKCE plain 허용
  token_endpoint_auth_methods_supported,  # "client_secret_post"가 없으면 2.1 초안의 본문 방식 미지원
  id_token_signing_alg_values_supported
}'
```

대외 문서에는 확정되지 않은 "OAuth 2.1 준수"보다 **"OAuth 2.0(RFC 6749) + PKCE(RFC 7636) + 보안 모범 사례(RFC 9700) + 발급자 식별(RFC 9207) + OIDC Core"**처럼 확정된 표준 이름으로 적는 편이 정확하다.

---

## 18. 정리: 한 장 체크리스트

각 항목 끝의 번호는 자세한 설명이 있는 절이다.

### 18.1 클라이언트(토큰을 받아 쓰는 쪽)를 만들 때

- [ ] secret은 서버 비밀 저장소에만 두고, 앱·소스·로그에 남기지 않는다 (4.2)
- [ ] 클라이언트 유형에 맞는 흐름을 고른다. 사용자가 끼면 authorization code + PKCE (3.3)
- [ ] authorize 요청마다 state·nonce·code_verifier를 암호학적 난수로 새로 만들고 세션에 저장한다 (7.2, 7.3)
- [ ] PKCE는 S256으로 보내고, `code_challenge_method=S256`을 반드시 함께 보낸다. 생략하면 plain으로 처리된다 (7.3)
- [ ] callback에서 state → error → iss 순서로 검사하고, 받은 파라미터는 모두 외부 입력으로 다룬다 (7.5)
- [ ] 로그인 진행용 세션 쿠키는 `SameSite=Lax`로 두고, 로그인 후 세션 ID를 새로 발급한다 (7.5)
- [ ] 토큰 응답의 `scope`를 확인하고, 빠진 권한을 처리한다 (5.3)
- [ ] id_token은 iss·aud·exp·nonce를 검증하고, 서명 알고리즘을 고정한다 (9.9)
- [ ] 로그인 판단은 access token이 아니라 id_token의 `aud`로 한다 (15.7.2)
- [ ] 회원은 `(iss, sub)`로 저장하고, email은 식별 키로 쓰지 않는다. `email_verified`가 없으면 미인증으로 본다 (9.3)
- [ ] 토큰은 암호화해 저장하고 secret과 다른 곳에 둔다. 컬럼 길이를 짧게 가정하지 않는다 (8.9)
- [ ] refresh token은 rotation에 맞춰 바꿔 저장하고, 같은 사용자의 갱신은 직렬화한다 (8.4)
- [ ] 연결 해제·탈퇴 때 토큰을 지우고 폐기를 요청한다 (8.8)
- [ ] 모바일 앱은 로그인을 시스템 브라우저로 열고 https 앱 링크로 받는다. 데스크톱·CLI는 `127.0.0.1` loopback으로 받는다 (12.4, 12.6)
- [ ] 브라우저 앱은 가능하면 BFF로 토큰을 서버에 둔다 (13.3)

### 18.2 인증 서버를 만들 때

- [ ] redirect_uri는 등록값과 정확히 일치할 때만 리다이렉트하고, 불일치는 자기 화면에 오류를 띄운다 (4.4, 7.6)
- [ ] code는 짧게(수십 초~수 분), 한 번만 쓰게 한다. 두 번째 사용 때는 그 code로 발급한 토큰도 폐기한다 (7.1)
- [ ] PKCE S256을 필수로 하고 plain을 받지 않는다. challenge 없이 발급한 code에 verifier가 오면 거부한다 (7.3, 15.5.4)
- [ ] code·토큰은 2^128 이상의 무작위성으로 만들고, token 엔드포인트의 시도 횟수를 제한한다 (15.11)
- [ ] 인가 응답에는 성공·오류 모두 `iss`를 넣는다 (7.5, 17.2)
- [ ] 로그인 폼 처리 뒤 리다이렉트에 307을 쓰지 않는다 (15.4.5)
- [ ] 토큰이 담긴 응답에 `Cache-Control: no-store`를 넣는다 (8.9)
- [ ] 로그인·동의·오류 화면에 `frame-ancestors 'none'`을 건다 (7.8)
- [ ] 동의 화면에 클라이언트 이름·등록 조직·scope를 보여 주고, 인증하지 못한 클라이언트는 자동 승인하지 않는다 (7.8)
- [ ] 사용자가 연결된 앱을 보고 끊는 화면과 폐기 엔드포인트를 둔다 (8.8)
- [ ] refresh token에 비활성 만료와 절대 만료를 두고, public client는 rotation이나 발신자 제한을 쓴다 (8.4, 8.7)
- [ ] 쓰지 않는 grant(implicit, password)와 서명 알고리즘은 discovery에서 빼고 실제로도 막는다 (15.12, 17.2)
- [ ] 2.1 초안을 따르려면 token 엔드포인트가 본문 방식 클라이언트 인증(`client_secret_post`)도 받는다 (4.3)
- [ ] 실패·취소도 `error`를 붙여 콜백으로 돌려보낸다 (7.6)

### 18.3 API(리소스 서버)를 만들 때

- [ ] access token은 typ → 서명 → iss → aud → exp → scope 순서로 검증하고, 시계 오차 여유(leeway)는 짧게 둔다 (10.1)
- [ ] 허용 알고리즘을 설정으로 고정하고, 키 주소는 설정의 JWKS에서만 가져온다 (10.2, 15.8)
- [ ] id_token은 받지 않는다 (`aud`, `typ`로 구분) (10.4)
- [ ] URL 쿼리로 온 access token은 무시한다 (8.6)
- [ ] 실패 응답은 `WWW-Authenticate`로 이유를 알린다 (401 `invalid_token`, 403 `insufficient_scope`) (8.6)
- [ ] 앞단에서 검증해도 내부 서비스는 원본 토큰을 가볍게 재검증하고, 프록시는 외부에서 온 보안 헤더를 지운다 (10.3, 15.10)
- [ ] 인가(데이터 소유 확인)는 데이터를 가진 서비스가 한다 (10.6)
- [ ] 사용자 토큰을 하위 서비스로 그대로 넘기지 않는다. 필요하면 Token Exchange (10.3, 14.6)
- [ ] JWT access token에 개인정보를 넣지 않는다 (10.5)
- [ ] 사용자 위임 토큰과 client_credentials 토큰을 구분한다 (15.7.1)
---

## 부록 A. OAuth 표준 연표

2.4절에서 본 버전 흐름을 연도별 표준 목록으로 펼친 것이다. 본문에서 RFC 번호를 만났을 때 그 표준이 언제, 어떤 맥락에서 나왔는지 찾아보는 용도로 쓴다.

```
2007-12  OAuth 1.0 (커뮤니티 사양)
2010-04  RFC 5849  OAuth 1.0
2012-10  RFC 6749  OAuth 2.0 본체          RFC 6750  Bearer token 사용법
2013     RFC 6819  위협 모델               RFC 7009  토큰 폐기
2014     OpenID Connect Core 1.0           ← 로그인(신원) 층
2015     RFC 7519  JWT    RFC 7591 동적 등록    RFC 7636 PKCE    RFC 7662 introspection
2017-10  RFC 8252  네이티브 앱 모범 사례
2018-06  RFC 8414  인증 서버 메타데이터
2019-08  RFC 8628  Device grant
2020     RFC 8693 Token Exchange   RFC 8705 mTLS   RFC 8707 Resource Indicators   RFC 8725 JWT 모범 사례
2021     RFC 9101 JAR   RFC 9126 PAR   RFC 9068 JWT access token
2022-03  RFC 9207  인가 응답의 iss
2023     RFC 9396 RAR   RFC 9449 DPoP   RFC 9470 Step-up
2025-01  RFC 9700  OAuth 2.0 보안 모범 사례 (BCP 240)
2025-04  RFC 9728  리소스 서버 메타데이터
2026-08  RFC 10017 브라우저 앱 모범 사례 (BCP 212)
2026-10  OAuth 2.1 초안 17판  (RFC 아님)
```

---

## 부록 B. IP 교환: 어디의 IP인가 (AWS 기준)

이 부록은 OAuth 자체가 아니라, 연동할 때 함께 정하게 되는 네트워크 설정을 다룬다. 4.5절에서 본 것처럼 IP 허용은 클라이언트 등록을 대체하지 못하지만, 서버 간 구간에서는 둘을 함께 쓴다.

교환하는 IP는 **"요청이 출발할 때 상대방 눈에 보이는 출발지(송신) IP"**다. 방향이 둘이라서 각각 누구의 IP인지가 다르다.

```
[방향 1] IdP 서비스 서버 ──► 클라이언트 앱 제휴사 API
          IdP 서비스가 클라이언트 앱에 전달한 IP = IdP 서비스 서버의 송신 IP
          클라이언트 앱이 자기 방화벽에 허용 (dev·stg만 IP 제한)

[방향 2] 클라이언트 앱 서버 ──► IdP 서비스 (IdP 인증 서버 /oauth/token/, 서비스 웹·API)
          클라이언트 앱이 문서로 알려 준 IP = 클라이언트 앱 서버의 송신 IP 대역
          IdP 서비스가 자기 방화벽에 허용 (선택)
```

### AWS에서 송신 IP는 실제로 무엇인가

```
[private subnet]                [public subnet]                       인터넷
  ECS / EC2 (10.0.x.x) ──► NAT Gateway (Elastic IP) ──► Internet Gateway ──► 클라이언트 앱
                                     ▲
                       클라이언트 앱이 보는 출발지 IP = 이 Elastic IP
```

ECS·EC2는 AWS의 컨테이너·가상 서버 서비스이고, Elastic IP는 계정에 고정으로 할당되는 공인 IPv4 주소다.

- **Internet Gateway에는 IP가 없다.** IGW는 VPC와 인터넷을 잇는 통로일 뿐이고, 공인 IP를 가진 자원의 사설 IP와 공인 IP를 1:1로 바꿔 주는 역할만 한다.
- **서버가 private subnet에 있으면**(일반적 구성) 밖으로 나가는 요청은 NAT Gateway를 거친다. 상대방이 보는 출발지는 **NAT Gateway의 Elastic IP**다.
- **서버가 public subnet에서 공인 IP를 직접 가지면** 그 인스턴스의 공인 IP가 출발지다. 자동으로 할당된 공인 IP는 인스턴스를 중지했다 켜기만 해도 바뀌므로 허용 목록 용도로는 부적합하다. 고정하려면 Elastic IP를 붙인다.
- **NAT Gateway는 AZ(가용 영역)마다 하나씩 두는 방식(zonal)이 오래 쓰여 왔다.** 다만 지금은 여러 AZ를 하나로 처리하는 regional NAT Gateway도 있고, NAT 하나에 IP를 여러 개(최대 8개) 붙일 수도 있다. 그래서 IP 개수만으로 구성을 추정하지 말고 인프라 설정을 확인한다. 상대에게 송신 IP를 알려 줬다면, NAT의 IP가 자동으로 늘거나 바뀌지 않게 고정한다(regional NAT는 수동 모드).

### LB의 IP는 왜 교환 대상이 아닌가

- **ALB(Application Load Balancer)는 고정 IP를 주지 않는다.** 트래픽에 따라 노드가 늘고 줄며 IP가 바뀐다. 그래서 ALB는 반드시 **도메인**으로 가리킨다.
- LB가 관여하는 방향은 **들어오는 요청(방향 2)**뿐이다. IdP 서비스 서버가 클라이언트 앱을 부를 때(방향 1)는 LB를 거치지 않는다.

상대방이 "우리 쪽으로 들어갈 때 목적지 IP가 고정이냐"고 물으면 앞단 구성에 따라 답이 다르다.

| IdP 서비스 앞단 구성 | 줄 수 있는 답 |
|---|---|
| ALB (일반적) | 도메인만. "고정 IP 아님" |
| NLB + Elastic IP | AZ별 고정 IP |
| Global Accelerator | 고정 Anycast IP 2개 (Anycast: 같은 IP를 여러 위치에서 알려 가장 가까운 곳으로 보내는 방식) |
| ALB + IPAM 풀 | 직접 가져온 IP 대역에서 ALB의 공인 IP를 받아, 그 대역을 알려 줄 수 있음 |

### 상대 IP로 우리 앞단을 막을 때: 경로별로 다르게

| IdP 서비스 경로 | 누가 호출하나 | 클라이언트 앱 IP로 제한 |
|---|---|---|
| IdP 인증 서버 `/oauth/authorize/`, 로그인·가입 화면 | **사용자 웹뷰** (사용자 IP) | ❌ 막으면 로그인 불가 |
| IdP 인증 서버 `/oauth/token/` | 클라이언트 앱 서버 | ✅ 가능 |
| IdP 인증 서버 `/.well-known/jwks.json` | 클라이언트 앱 서버 등 | 공개 정보라 굳이 막지 않음 |
| 서비스 웹·API (클라이언트 앱 서버가 중계) | 클라이언트 앱 서버 | ✅ 가능 (중계 방식 확인 후) |

그래서 Security Group처럼 IP 단위로 통째로 막는 방법은 IdP 인증 서버에 쓸 수 없다. AWS WAF의 IP set(WAF 규칙에서 쓰는 IP 주소 목록) 규칙을 **경로 조건과 함께** 거는 방식이 맞다. WAF는 ALB에는 붙지만 NLB에는 붙지 않으므로, 고정 IP 때문에 NLB를 쓴다면 NLB 뒤에 ALB를 두고 거기에 WAF를 건다.

---

## 출처

**표준 문서** (2026-11-03 원문 확인)

- RFC 6749 The OAuth 2.0 Authorization Framework (2012)
- RFC 6750 The OAuth 2.0 Authorization Framework: Bearer Token Usage
- RFC 7517 JSON Web Key (JWK)
- RFC 7591 OAuth 2.0 Dynamic Client Registration Protocol (`client_secret_basic` 이름 정의)
- RFC 7636 Proof Key for Code Exchange (PKCE)
- RFC 7662 OAuth 2.0 Token Introspection
- RFC 7800 Proof-of-Possession Key Semantics for JWTs (`cnf` claim)
- RFC 8252 OAuth 2.0 for Native Apps (BCP 212)
- RFC 8414 OAuth 2.0 Authorization Server Metadata
- RFC 8693 OAuth 2.0 Token Exchange (`scope` claim 형식)
- RFC 8705 OAuth 2.0 Mutual-TLS Client Authentication and Certificate-Bound Access Tokens
- RFC 9068 JWT Profile for OAuth 2.0 Access Tokens
- RFC 9207 OAuth 2.0 Authorization Server Issuer Identification
- RFC 9700 Best Current Practice for OAuth 2.0 Security (BCP 240, 2025년 1월)
- RFC 6819 OAuth 2.0 Threat Model and Security Considerations
- RFC 7009 OAuth 2.0 Token Revocation
- RFC 7519 JSON Web Token (JWT)
- RFC 7523 JWT Profile for OAuth 2.0 Client Authentication and Authorization Grants
- RFC 8446 The Transport Layer Security (TLS) Protocol Version 1.3
- RFC 8628 OAuth 2.0 Device Authorization Grant
- RFC 8707 Resource Indicators for OAuth 2.0
- RFC 8725 JSON Web Token Best Current Practices (BCP 225)
- RFC 9101 JWT-Secured Authorization Request (JAR)
- RFC 9126 OAuth 2.0 Pushed Authorization Requests (PAR)
- RFC 9396 OAuth 2.0 Rich Authorization Requests (RAR)
- RFC 9449 OAuth 2.0 Demonstrating Proof of Possession (DPoP)
- RFC 9470 OAuth 2.0 Step Up Authentication Challenge Protocol
- RFC 9728 OAuth 2.0 Protected Resource Metadata
- RFC 10017 OAuth 2.0 for Browser-Based Applications (BCP 212, 2026년 8월)
- OpenID Connect Discovery 1.0, RP-Initiated Logout 1.0, Back-Channel Logout 1.0, CIBA Core 1.0
- OAuth 2.0 Form Post Response Mode (OpenID Foundation)

**벤더·구현 문서** (리뷰에서 확인)

- Apple `ASWebAuthenticationSession`, `Callback.https(host:path:)` (iOS 17.4+)
- Android `CookieManager`, WebKit 블로그(WKWebView ITP 기본값)
- AWS VPC NAT Gateway(regional·zonal), ALB mTLS·IPAM 풀
- PyJWT API 문서, authlib·Django 세션 소스
- 카카오·네이버 OIDC discovery 문서 (2026-11-03 조회)
- OpenID Connect Core 1.0 incorporating errata set 2 (2023-12-15)
- draft-ietf-oauth-v2-1-17 The OAuth 2.1 Authorization Framework (2026-10-31, 초안)

**연동 자료 (내부)**

- 제휴 연동 규격 (사례 작성에 쓴 비공개 문서)
- 인증 서버 로그인 연동 가이드 (스테이징 기준, 비공개)
- refresh token 안내 문서 (비공개)
- 가입·계정 연결·보안 팔로업 문서 (비공개)
- 제휴사 회원 연동 구성 기획안 (비공개)

**관련 노트**

- [[oauth2-concept-explainer]]: OAuth 2.0 개념 요약
- [[oauth1-concept-explainer]]: OAuth 1.0
- [[sso-oauth-comparison-and-architecture]]: SSO와 OAuth 비교
- [[sso-concept-explainer]]: SSO
