---
created: 2026-02-03
source: claude-code
tags:
  - security
  - nginx
  - web-security
  - audit
---

# 2차 보안성 검토 결과 - 용인 AITRICS 솔루션

부적합 항목 3건에 대한 분석 및 조치 방법 정리.

---

## 1. 정보누출 - nginx 버전 정보 노출

**매우 흔한 보안 점검 항목이다.** 응답 헤더에 `Server: nginx/1.26.1`이 그대로 노출되고 있다. 공격자가 nginx 버전을 알면 해당 버전의 알려진 취약점(CVE)을 바로 찾아서 공격할 수 있기 때문에 숨기라는 것이다.

**nginx 설정에서 바로 할 수 있다.** `nginx.conf`의 `http` 블록에 한 줄 추가하면 된다:

```nginx
http {
    server_tokens off;  # "nginx/1.26.1" → "nginx" 로 변경됨
}
```

이렇게 하면 `Server: nginx`만 나온다. 버전 정보는 사라지지만 "nginx"라는 문자열은 남는다.

완전히 제거하거나 다른 값으로 바꾸려면 `ngx_http_headers_more_module`을 사용해야 한다:

```nginx
# 완전히 제거
more_clear_headers Server;

# 또는 다른 값으로 변경
more_set_headers "Server: WebServer";
```

`server_tokens off;`만으로 충분히 통과할 가능성이 높다. 검토 결과에서도 "버전 정보 노출 : 삭제 필요"라고 했으니까.

---

## 2. 불충분한 인증 절차

검토 결과에서 구체적으로 지적하는 내용:

> **별도 인증 없이 설정 페이지(`/settings/account`) 접근이 가능하여, 다수 정보 삭제 & 변경 가능**

로그인한 사용자가 **설정 페이지(내 계정, 병원 정보 관리, 멤버 관리, 알람기준 설정 등)에 들어갈 때 추가 인증 없이 바로 접근해서 정보를 수정/삭제할 수 있다**는 것이 문제다.

**요구사항**: 설정 페이지 접근 시 다음 중 하나를 구현:

- **비밀번호 재입력** (가장 일반적) - 설정 페이지 진입 시 현재 비밀번호를 다시 한번 입력받음
- **2차 간편인증** - OTP, PIN 등

예를 들어, GitHub에서 비밀번호 변경하거나 2FA 설정 바꿀 때 비밀번호를 다시 입력하는 것과 같은 패턴이다. 은행 앱에서 설정 들어갈 때 PIN을 다시 입력하는 것도 같은 맥락이다.

**구현 방향**:

- `/settings/*` 경로 접근 시 서버 사이드에서 "최근 N분 이내에 비밀번호 재인증을 했는가"를 확인
- 안 했으면 비밀번호 재입력 화면으로 리다이렉트
- 재인증 후 일정 시간(예: 15분) 동안은 추가 인증 없이 설정 페이지 사용 가능

---

## 3. 데이터 평문 전송 - 취약한 Cipher Suite 비활성화

**SSL/TLS를 새로 적용하라는 게 아니다. API 응답 암호화도 아니다.**

이미 HTTPS를 쓰고 있지만, **취약한 Cipher Suite를 비활성화하라**는 것이다. 지적된 두 개의 cipher suite:

- `TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384`
- `TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA`

둘 다 **CBC 모드**를 사용하는 cipher suite다. CBC 모드는 BEAST, Lucky13, POODLE 등의 공격에 취약한 것으로 알려져 있어서 비활성화가 권장된다.

**nginx에서 조치 방법** - `nginx.conf`에서 `ssl_ciphers` 설정을 수정:

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305';
ssl_prefer_server_ciphers on;
```

핵심은 **GCM이나 CHACHA20 계열만 허용하고, CBC 계열을 모두 제외**하는 것이다. 설정 변경 후 `nginx -t`로 검증하고 reload하면 된다.

---

## 부록: Cipher Suite란?

Cipher Suite는 HTTPS 통신할 때 클라이언트(브라우저)와 서버가 **"어떤 암호화 방식을 쓸지" 합의하는 조합**이다.

지적받은 이름을 분해하면:

```
TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384
│    │      │        │    │    │    └── 무결성 검증 알고리즘 (SHA384)
│    │      │        │    │    └────── 암호화 운영 모드 (CBC) ← 이게 문제
│    │      │        │    └─────────── 키 길이 (256bit)
│    │      │        └────────────────  암호화 알고리즘 (AES)
│    │      └───────────────────────── 인증 방식 (RSA)
│    └──────────────────────────────── 키 교환 방식 (ECDHE)
└───────────────────────────────────── 프로토콜 (TLS)
```

브라우저가 서버에 접속할 때 "나는 이런 cipher suite들을 지원해"라고 목록을 보내고, 서버가 그 중 하나를 골라서 "이걸로 하자"고 응답한다. 이걸 TLS Handshake라고 한다.

**문제가 되는 이유**: CBC 모드는 오래된 암호화 운영 방식이라 알려진 공격 기법들이 있다. 그래서 보안 검토에서 CBC 대신 **GCM 모드**를 쓰라는 것이다:

```
TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384  ← GCM이라 안전
TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384  ← CBC라 취약
```

서버(nginx)가 CBC 계열 cipher suite를 목록에서 빼버리면, 브라우저는 자동으로 GCM 같은 안전한 걸로 연결한다. 최신 브라우저들은 전부 GCM을 지원하기 때문에 호환성 문제도 없다.

---

## 요약

| 항목                 | 조치 대상      | 난이도 |
| -------------------- | ------------- | ------ |
| 정보누출             | nginx 설정    | 낮음   |
| 불충분한 인증 절차   | 애플리케이션  | 중간   |
| 데이터 평문 전송     | nginx 설정    | 낮음   |
