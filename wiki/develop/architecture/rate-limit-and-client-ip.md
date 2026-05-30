---
tags: [rate-limit, security, otp, email-verification, web-security, ip-extraction]
created: 2026-05-28
---

# Rate-Limit 설계 & 클라이언트 IP 추출 — 종합 정리

> 회원가입 OTP 선검증에 적용할 rate-limit 정책과 그 기반이 되는 클라이언트 IP 추출 방법을 종합 정리한다. 검증 과정에서 정정된 결론을 반영한 최종 형태.

## 📋 Executive Summary

- **rate-limit은 보안이 1차 목적**, Resend 한도 보호는 부수 효과. 두 종류(입력 시도 제한 / 발송 제한)로 나뉜다.
- 초안의 "단순화 정책"(이메일당 시간·일 한도 제거)은 후속 검증에서 반박됨. NIST §5.2.2와 충돌하고, 60초 쿨다운만으로는 시간당 60통 = 메일함 DoS·sender reputation 공격에 정확히 충분한 페이로드. → **이메일당 일 한도 10~20통 복원**.
- 클라이언트 IP 추출은 TCP 소켓이 아니라 HTTP 헤더로 받되, **위조 가능**하므로 신뢰 프록시 모델 필수.
- 정확한 추출 규칙은 "가장 왼쪽"이 아니라 **"오른쪽에서 신뢰 hop 개수번째"**.
- 호스팅 검증 헤더 우선순위 정정: **Vercel은 `x-real-ip`** (공식 SDK가 사용. `x-vercel-forwarded-for` 아님), **Cloudflare는 `TRUST_CLOUDFLARE` 환경변수 게이트 필수**.

---

## 🛡️ Rate-Limit 정책

### 두 종류로 나뉘는 rate-limit

```
┌─────────────────────────────────────────────────────────────┐
│ ① 입력 시도 제한 (3회)   — "코드를 몇 번 맞춰볼 수 있나"     │
│ ② 발송 제한               — "코드를 몇 번 보낼 수 있나"      │
│     ├─ 재전송 쿨다운 60초                                    │
│     ├─ 이메일당 일 한도 (검증 후 복원)                        │
│     └─ IP /64당 한도                                         │
└─────────────────────────────────────────────────────────────┘
```

| 종류                | 값                                            | 1차 목적                                                       | 부수 효과                       |
| ------------------- | --------------------------------------------- | -------------------------------------------------------------- | ------------------------------- |
| 입력 시도 제한      | 3회 실패 시 코드 무효화                       | 🔐 코드 추측(brute-force) 차단                                  | —                               |
| 재전송 쿨다운       | 60초                                          | 🔐 메일 폭탄·brute-force 사이클 차단                            | 사용자 실수 방지                |
| 이메일당 일 한도    | **10~20통**                                   | 🔐 표적 메일함 DoS·sender reputation 보호 (NIST §5.2.2)          | Resend 일 100통 한도 보호       |
| IP /64당 한도       | 운영 데이터 기반 조정 (참고치 시간당 10~20)   | 🔐 이메일 바꿔가며 우회 차단                                    | —                               |

### 입력 시도 제한 — "코드 맞추기 3회"

> 🎮 비유: 휴대폰 잠금 화면. 비밀번호 3번 틀리면 잠겨버리는 거예요.

**🟢 정상 시나리오 (A씨가 코드를 헷갈림)**

```
시각      행동                              서버 상태(pending_signups)
─────────────────────────────────────────────────────────────────────
14:00:00  POST /signup/start                attempts=0, otp_hash=H("482917")
          → "코드 발송됨" (메일에 482917)

14:00:30  POST /signup/verify {code:"482971"}  ← 78↔97 오타
          서버: attempts++ → attempts=1
          → 응답 401 "코드가 올바르지 않습니다 (2회 남음)"

14:00:45  POST /signup/verify {code:"482917"}  ← 정정
          서버: timingSafeEqual(H(코드), otp_hash) ✅
          → 응답 200, users INSERT, pending_signups DELETE → 자동 로그인
```

**🔴 공격 시나리오 (공격자가 brute-force)**

```
공격자: 6자리 숫자 = 100만 조합. 한 번에 하나씩 찍어보자.

14:00:00  POST /signup/verify {code:"000001"}   attempts=1, 401
14:00:01  POST /signup/verify {code:"000002"}   attempts=2, 401
14:00:02  POST /signup/verify {code:"000003"}   attempts=3
          → 서버: pending_signups DELETE (코드 무효화!)
          → 응답 401 "코드가 만료되었습니다"

→ 새 코드를 받으려면 발송 rate-limit에 막힘 (분당 1통)
→ 100만 조합 시도하려면 며칠 + 매번 메일 발송 → 사실상 불가능
```

> ⚠️ 시도 카운터는 **이메일 단위 글로벌 누적**: 코드 재발급해도 안 리셋. 그래야 "코드 무효화 → 재전송 → 다시 3회 → 무한 반복" 우회를 차단.

### 재전송 쿨다운 60초 — 필요성

**이유 1: 메일 폭탄(이메일 abuse) 차단 — 피해자 보호**

```
공격자가 victim@example.com을 가입 폼에 입력
   │
   ├─ 쿨다운 없으면: 1초에 100번 호출 → victim 메일함에 인증코드 100통 💣
   │
   └─ 60초 쿨다운: 분당 최대 1통 → 폭탄 효과 사실상 사라짐 ✅
```

이건 **Resend 한도와 무관**: Resend 입장에선 정상 발송이라 알림이 안 옴. 피해자는 우리 서비스 사용자가 아닌 제3자라 더 위험.

**이유 2: brute-force 시도 사이클 차단**

```
입력 시도 제한(3회)이 있어도 쿨다운 없으면:
  ┌─ 코드 받음 → 3번 틀림 → 코드 무효화
  ├─ 즉시 재전송 → 새 코드 → 또 3번 틀림 → 무효화
  └─ ... 무한 반복

쿨다운 60초: 분당 3번 시도 → 100만 조합 brute-force = ~5,500시간 → 사실상 불가능 ✅
```

**이유 3 (부수): 사용자 실수 — "메일이 안 와요" 연타**

> 🎮 비유: 휴대폰 잠금 화면이 "3번 틀리면 30초 잠금"이잖아요? 그 30초가 바로 쿨다운이에요.

**표준 부합성**: NIST/OWASP 공식 수치 미명시이나 업계 관행(Auth0 30s, **Supabase 60s**, GitHub 60s, Stripe 60s)에 부합.

### 이메일당 일 한도 — 검증 후 복원

> ⚠️ **초안 정정 사항.** 처음엔 "60초 쿨다운 = 시간당 60통 상한이 자연 강제되므로 이메일당 시간·일 한도 제거 가능"이라 했으나, 후속 검증에서 반박됨.

**왜 60초 쿨다운만으로 부족한가**:

```
공격자의 목표가 "정상 사용자 1명의 메일함을 쓰레기로 만드는 것"이라면 시간당 60통이면 충분:

- 표적 victim@example.com에 60초마다 1통 = 시간당 60통 OTP 메일
- 24시간 = 1,440통/일
- 메일함 DoS, sender reputation 손상, Resend 100통/일 한도 16분 만에 소진
```

**NIST SP 800-63B §5.2.2**: 계정당 10 attempts/30일 절대 상한 요구. 일 한도 없으면 위반 위험.

→ **이메일당 일 한도 10~20통 유지**. DB 카운터 1개로 해결.

### IP 한도 — NAT 균형점

> ⚠️ **수치 권고에 공식 1차 출처 없음**. 업계 관행이고 컨텍스트에 따라 다름.

**균형점의 어려움**:

- 너무 빡빡: CGNAT(T-Mobile/Verizon)·대학교 기숙사·회사망에서 정상 사용자 차단
- 너무 느슨: 봇넷/VPN으로 IP 분산하면 무력화

→ IP 한도는 **2차 휴리스틱**이고, 1차는 이메일 단위 한도. 운영 데이터 기반으로 조정.

### Resend 응답 fallback

```
정상 발송   → 200 "인증 코드를 보냈습니다"
한도 초과   → 200 "인증 코드를 보냈습니다"  (사용자엔 같게, 내부 모니터링 알림은 따로)
쿨다운     → 200 (동일 — enumeration 방어)
```

**보강 사항**:

- **Soft threshold 사전 경보**: 한도 80% 도달 시 관리자 알림 (60통 발송 시점). 소진 *전* 대응 시간 확보.
- **timing equalization**: 모든 응답이 동일 latency를 가지도록 `await sleep(jitter)` 또는 고정 지연. timing-based enumeration 차단.
- **Resend bounce/complaint webhook**: 동일 이메일 반복 발송 시 sender reputation 손상 방어 (도메인 SPF/DKIM 영향).

---

## 🌐 클라이언트 IP 추출

### TCP 소켓 IP vs HTTP 헤더

```
사용자(1.2.3.4)
   │
   ▼
[CDN/Proxy 5.5.5.5]     ◀── 우리 서버가 "TCP 소켓에서 보는 peer IP" = 5.5.5.5
   │                         (사용자의 진짜 IP가 아님!)
   ▼
[LB 7.7.7.7]
   │
   ▼
[API Gateway 8.8.8.8]
   │
   ▼
[API Server]   ← 직전 hop(8.8.8.8)만 TCP로 보임. 사용자 1.2.3.4는 HTTP 헤더로 받음
```

> 🎮 비유: 택배가 여러 물류센터를 거치면 마지막 박스의 발송지는 마지막 물류센터 주소예요. "진짜 보낸 사람"은 운송장 안의 별도 메모(HTTP 헤더)에 적혀 와요.

**RFC 7239 §5.2 원문 확인**: *"The last proxy's IP address, and optionally a port number, are, however, readily available as the remote IP address at the transport layer."*

### IP를 운반하는 표준 헤더

| 헤더                            | 형식                                        | 누가 설정             |
| ------------------------------- | ------------------------------------------- | --------------------- |
| **X-Forwarded-For** (XFF)       | `client, proxy1, proxy2` — 콤마로 누적      | de facto 표준         |
| **X-Real-IP**                   | 단일 IP                                     | nginx 등              |
| **Forwarded** (RFC 7239)        | `for=1.2.3.4;by=5.5.5.5`                    | 공식 표준             |
| **벤더 전용**                   | `CF-Connecting-IP`, `x-vercel-forwarded-for` 등 | 해당 인프라      |

### XFF append 규칙

각 hop이 "자기가 본 TCP 소스 IP"를 append하며 **자기 IP는 안 적음**:

```
사용자(1.2.3.4) → 요청 보냄 (헤더 없음)
   │
   ▼
[CDN 5.5.5.5]     append:  X-Forwarded-For: 1.2.3.4
   │
   ▼
[LB 7.7.7.7]      append:  X-Forwarded-For: 1.2.3.4, 5.5.5.5
   │
   ▼
[Gateway 8.8.8.8] append:  X-Forwarded-For: 1.2.3.4, 5.5.5.5, 7.7.7.7
   │
   ▼
[우리 서버]  XFF 헤더: [1.2.3.4, 5.5.5.5, 7.7.7.7]  ← 3개 (Gateway IP는 없음)
            Gateway(8.8.8.8) IP는 TCP 소스로만 보임
```

> 🎮 비유: 마지막 물류센터는 자기 주소를 운송장에 안 적어요. **상자 도착 그 자체**가 자기를 가리키니까.

> ⚠️ **Next.js 16 함정**: `next/dist/server/base-server.js:511`가 XFF가 비어있으면 `socket.remoteAddress`(=직전 hop IP)로 자동 채움. Coolify+Traefik이 forward 설정 안 했을 때 "Traefik IP가 XFF에 들어가는" 케이스 발생.

### XFF는 클라이언트가 위조 가능

**핵심 함정**: HTTP 헤더는 누구든 임의로 보낼 수 있다.

```
악의적 사용자가 직접 요청:
  curl -H "X-Forwarded-For: 1.2.3.4" https://our-api.com/signup/start

우리 서버가 그냥 XFF 가장 왼쪽을 신뢰하면?
  → 가짜 IP 1.2.3.4에 카운트
  → 공격자는 매 요청마다 다른 가짜 IP → rate-limit 우회 💥
```

**RFC 7239 §7.1**: *"A malicious or compromised client could craft messages with fake 'Forwarded' header fields. Recipients SHOULD validate or sanitize the field."* → CWE-348 매핑.

### 정확한 추출 규칙: "오른쪽에서 신뢰 프록시 N번째"

신뢰 프록시 3개(CDN, LB, Gateway)면 **오른쪽에서 3번째**가 진짜 클라이언트.

| 시나리오 | XFF                                              | 길이 | 가장 왼쪽   | **오른쪽 3번째**  |
| -------- | ------------------------------------------------ | ---- | ----------- | ----------------- |
| 정상     | `[1.2.3.4, 5.5.5.5, 7.7.7.7]`                    | 3    | 1.2.3.4 ✓   | 1.2.3.4 ✓         |
| 공격     | `[9.9.9.9, 1.2.3.4, 5.5.5.5, 7.7.7.7]`           | 4    | 9.9.9.9 ✗   | **1.2.3.4 ✓**     |

```
오른쪽 1번째 = 우리 직전 hop(Gateway)이 본 TCP 소스 = LB 7.7.7.7
오른쪽 2번째 = LB가 본 TCP 소스 = CDN 5.5.5.5
오른쪽 3번째 = CDN이 본 TCP 소스 = 진짜 클라이언트 1.2.3.4 ★
오른쪽 4번째 이상 = 클라이언트가 위조한 부분 → 무시
```

**MDN 원문**: *"The X-Forwarded-For IP list is searched from the rightmost by that count minus one."*

### 호스팅 검증 헤더 (정정된 우선순위)

> ⚠️ **초안 정정**: 처음엔 "Vercel `x-vercel-forwarded-for` 우선"이라 했으나, Vercel 공식 SDK(`@vercel/functions@3.6.1`)는 **`x-real-ip`를 사용**함이 코드 인용으로 확정.

```
1순위: Vercel  → x-real-ip (공식 SDK가 사용하는 진입점)
       Cloudflare → CF-Connecting-IP (단, Cloudflare를 실제 앞에 둘 때만)

2순위: X-Forwarded-For + TRUSTED_PROXY_HOPS 환경변수로 정확한 위치 추출

3순위: x-real-ip (마지막 fallback)
```

> ⚠️ **CF-Connecting-IP는 환경 게이트 필수**: Cloudflare를 안 쓰는 환경에서 그 헤더를 신뢰하면 누구나 헤더에 IP 박아 보내서 우회 가능. → `TRUST_CLOUDFLARE` 환경변수로 명시 게이트.

### IPv6 — /64 prefix 매칭

IPv6는 한 사용자가 `/64` prefix 안에서 수많은 주소를 가질 수 있어, rate-limit 키를 **`/64`로 묶어** 카운트해야 우회 방지.

- RFC 4291/4862: /64는 SLAAC의 실질적 단위
- Cloudflare 실제 구현: /64 수준 차단
- Let's Encrypt: /48 추가 묶음 (병행 검토 가치)

**IPv4-mapped IPv6 함정**:

- Node에서 `::ffff:1.2.3.4`는 IPv6로 인식됨
- dual-stack 서버에서 IPv4 클라이언트가 `::ffff:` 형태로 들어오면 /64 매칭이 어긋남
- → `ipaddr.process()`로 정규화 의무화

> 📦 **`ipaddr.js@1.9.1`이 이미 transitive로 설치돼 있음** — 추가 의존성 없이 사용 가능.

### NAT/공유 IP 함정

- **NAT (Network Address Translation)**: 모바일 캐리어·회사망에서 여러 사용자가 같은 IP 공유 → IP 한도를 너무 낮게 잡으면 정상 사용자 차단
- **VPN/Tor**: 의도적 우회 가능 → IP rate-limit만으로 절대 방어 안 됨
- → CAPTCHA fallback이 임계 초과 시 보조

> 🎮 비유: 한 가족이 한 인터넷 회선을 같이 쓰면(NAT) IP가 같아요. "이 IP에서 1시간에 1번만" 같은 강한 제한은 가족 중 1명만 통과시키니 너무 빡빡.

### 보강된 헬퍼 함수 (정정 반영)

```typescript
// lib/get-client-ip.ts
import ipaddr from 'ipaddr.js'; // 이미 설치됨

export function getClientIp(req: { headers: Headers }): string | null {
  // 1) Cloudflare는 env로 명시 게이트 (안 쓰면 위조 위험)
  if (process.env.TRUST_CLOUDFLARE === 'true') {
    const cf = req.headers.get('cf-connecting-ip');
    if (cf) return normalize(cf);
  }

  // 2) Vercel: 공식 SDK와 일치 — x-real-ip 우선 (정정됨)
  if (process.env.VERCEL === '1') {
    const xr = req.headers.get('x-real-ip');
    if (xr) return normalize(xr);
  }

  // 3) Self-host: XFF "오른쪽에서 N번째"
  const xff = req.headers.get('x-forwarded-for');
  if (xff) {
    const chain = xff.split(',').map(s => s.trim()).filter(Boolean);
    const idx = chain.length - Number(process.env.TRUSTED_PROXY_HOPS ?? 1);
    if (idx >= 0) return normalize(chain[idx]);
  }

  // 4) 마지막 fallback
  const xr2 = req.headers.get('x-real-ip');
  return xr2 ? normalize(xr2) : null;
}

function normalize(ip: string) {
  try {
    return ipaddr.process(ip).toString(); // IPv4-mapped 정규화
  } catch { return null; }
}

export function rateLimitKey(ip: string): string {
  const parsed = ipaddr.parse(ip);
  if (parsed.kind() === 'ipv6') {
    // /64 prefix로 묶기
    const bytes = parsed.toByteArray().slice(0, 8);
    return 'v6:' + bytes.map(b => b.toString(16).padStart(2,'0')).join('');
  }
  return 'v4:' + parsed.toString();
}
```

---

## 📎 Sources

1. [RFC 7239 — Forwarded HTTP Extension](https://datatracker.ietf.org/doc/html/rfc7239) — §5.2 last proxy IP, §7.1 spoofing 경고
2. [MDN — X-Forwarded-For](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Forwarded-For) — "from the rightmost by that count minus one"
3. [Vercel Request Headers](https://vercel.com/docs/headers/request-headers) — `x-real-ip` 검증 헤더
4. [Cloudflare HTTP Headers](https://developers.cloudflare.com/fundamentals/reference/http-headers/) — CF-Connecting-IP
5. [NIST SP 800-63B §5.2.2](https://pages.nist.gov/800-63-3/sp800-63b.html#throttle) — 계정당 시도 제한
6. [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) — multi-tier rate limiting
7. [OWASP API Security Top 10 — API4:2023](https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/) — IP 단독 한계
8. [CWE-348 — Use of Less Trusted Source](https://cwe.mitre.org/data/definitions/348.html) — XFF 위조 매핑
9. [RFC 4291](https://tools.ietf.org/html/rfc4291) / [RFC 4862](https://datatracker.ietf.org/doc/html/rfc4862) — IPv6 /64 구조
10. [Cloudflare WAF Rate Limiting Best Practices](https://developers.cloudflare.com/waf/rate-limiting-rules/best-practices/) — credential stuffing 예시
11. [adam-p — IPv6 rate-limiting](https://adam-p.ca/blog/2022/02/ipv6-rate-limiting/) — Cloudflare /64, Let's Encrypt /48 실측
12. (in-tree) `node_modules/next/dist/server/base-server.js:511` — Next.js 16 XFF socket fallback
13. (in-tree) `@vercel/functions@3.6.1 headers.js:36` — `IP_HEADER_NAME = "x-real-ip"`
