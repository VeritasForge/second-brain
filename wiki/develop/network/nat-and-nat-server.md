---
tags: [nat, networking, port-forwarding, cgnat]
created: 2026-06-09
---

# 📖 NAT & NAT Server — Concept Deep Dive (검증 반영판)

> 💡 **한줄 요약**: **NAT**는 IP 패킷의 출발지/목적지 주소(+포트)를 바꿔치기해 적은 공인 IP를 나눠 쓰게 하는 기술이고, **NAT Server**는 그 반대 방향(외부→내부)으로 "공인 IP:포트 → 내부 서버"를 미리 고정 매핑해 **내부 서버를 외부에 공개**하는 기능(= DNAT / 포트포워딩)입니다.

> 🔬 본 노트는 concept-explainer 8섹션 리포트를 rl-verify(Tier 3, 4관점 + 1차 출처 교차검증)로 검증해 P0 1건·P1 2건·P2 7건을 교정한 반영판입니다. 🔧 표시가 검증으로 교정된 부분.

---

## 1️⃣ 무엇인가? (What is it?)

**NAT (Network Address Translation, 네트워크 주소 변환)** 는 라우터/방화벽이 IP 패킷의 **출발지 또는 목적지 IP 주소(와 포트)를 바꿔치기**하는 기술입니다. (어느 필드를 바꾸는지는 방향·종류에 따라 다릅니다 — 3️⃣에서 상세.)

🏢 **현실 비유 — 회사 대표 전화번호** *(비유의 한계는 아래 박스 참고)*

- 직원 300명, 외부 공개 번호는 **대표번호 1개(02-1234-5678)** 뿐.
- 직원은 **내선번호**로 구분되고, 외부 통화 시 모두 대표번호로 나갑니다.
- **대표번호 = 공인 IP**, **내선번호 = 포트**, **교환원 = NAT 장비**.

> 🔧 **F1·비유 보정 — 이 전화 비유의 한계**:
> - "내선번호"는 사설 IP가 아니라 **포트**에 대응합니다(사설 IP는 외부에 절대 노출되지 않는다는 게 NAT의 핵심).
> - 교환원 비유는 **외부→내부(inbound, DNAT)** 설명엔 잘 맞지만, NAT의 주 용도인 **내부→외부(outbound, PAT)** "여럿이 공인 IP 하나로 나가기"는 이 비유로 다 담기지 않습니다.

📜 **탄생 배경**: 1990년대 초 인터넷 급성장으로 **IPv4 주소(2³² ≈ 약 43억 개, 실사용 가능분은 더 적음)** 고갈이 **예측**됐습니다. 🔧 (실제 IANA 풀 소진은 2011년 — 1990년대는 "고갈 위기 경보" 시점이고, 그 경보가 NAT·CIDR·RFC 1918 도입을 이끌었습니다.)

- [RFC 1918](https://datatracker.ietf.org/doc/html/rfc1918): 인터넷에 라우팅되지 않는 **사설 주소 대역** 지정
- 🔧 **F4**: [RFC 2663](https://www.rfc-editor.org/rfc/rfc2663.html) = "NAT **용어·고려사항**"(Basic NAT + NAPT 전체 용어 체계) / [RFC 3022](https://www.rfc-editor.org/rfc/rfc3022.html) = **Traditional NAT 구현 표준**(RFC 1631(1994)을 obsolete)
- 🔧 **F7**: NAT는 IPv4 고갈을 **상당 기간 늦춘 핵심 완화책**이며, de facto가 아니라 **IETF 문서로 정식화된 기술**(RFC 1631→3022, 2663, CGNAT는 RFC 6888)입니다.

> 📌 **핵심 키워드**: `사설 IP(Private IP)`, `공인 IP(Public IP)`, `변환 테이블(Translation Table)`, `포트(Port)`, `5-tuple`

---

## 2️⃣ 핵심 개념 (Core Concepts)

NAT의 3가지 기둥: ① 사설/공인 주소, ② 변환 테이블, ③ 포트.

```
NAT의 3대 핵심 구성 요소
=========================

① 주소 영역(Realm)
     사설(Inside) : 192.168.x.x / 10.x.x.x   →  인터넷엔 못 나감
     공인(Outside): 203.0.113.5               →  전 세계 유일

② 변환 테이블(State)  ← "누가 누구와 통신 중인지" 메모장
     세션 키 = 5-tuple {프로토콜, 출발지IP:포트, 목적지IP:포트}
     192.168.0.10:3344 → 93.184.x.x:443  <-->  203.0.113.5:50001 → 93.184.x.x:443

③ 포트(Port)          ← "내선번호" 역할
     같은 공인 IP라도 포트로 누구 트래픽인지 구분 (PAT의 핵심)
```

| 구성 요소 | 역할 | 설명 |
| --- | --- | --- |
| **사설 IP (RFC 1918)** | 내부 식별 | `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` — 인터넷 라우팅 안 됨 |
| **공인 IP** | 외부 식별 | 전 세계 유일, 인터넷 라우팅 가능 |
| **변환 테이블** | 매핑 기억 | 🔧 **F10**: 키는 단순 IP:포트가 아니라 **5-tuple**. 그래서 같은 PC가 같은 포트로 서로 다른 서버에 동시 접속해도 구분됨 |
| **포트(Port)** | 세션 구분 | 같은 공인 IP를 포트로 다중화 (PAT의 핵심) |

🔑 **상태(state)에 대한 정확한 이해** 🔧 **F2**:

- **PAT/NAPT, Dynamic NAT는 stateful** — 세션별 변환 테이블을 유지합니다(나갈 때 변환+기록, 응답 시 역변환).
- **Static NAT는 stateless** — 사전 구성된 고정 1:1 매핑만 적용하며 세션 상태가 필요 없습니다.
- 즉 "NAT는 본질적으로 상태를 기억한다"는 **동적 NAT(PAT/Dynamic)에 한정**되는 성질입니다.

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

### 🔄 일반 NAT (Outbound / Source NAT) — 내부 → 외부

내부 PC가 외부 웹서버(`93.184.x.x:443`)에 접속하는 흐름입니다.

```
나가는 길 (출발지 IP/포트를 바꿈)
---------------------------------
[내부 PC 192.168.0.10:3344]
        |  ① 첫 패킷 도착 (5-tuple: TCP, 192.168.0.10:3344, 93.184.x.x:443)
        v
[NAT 라우터]  ── ② 세션 신규(NEW) → 변환 테이블 엔트리 생성 ──
        |        192.168.0.10:3344  →  203.0.113.5:50001
        |        + TTL 1 감소(NAT=L3 라우터) + IP/TCP 체크섬 재계산
        |  ③ SRC=203.0.113.5:50001  DST=93.184.x.x:443
        v
[인터넷 서버]
        |  (이후 같은 flow는 룰 재평가 없이 fast-path로 동일 변환)

돌아오는 길 (테이블 역조회로 복원)
----------------------------------
[인터넷 서버]
        |  ④ 응답 DST=203.0.113.5:50001
        v
[NAT 라우터]  ── ⑤ 5-tuple 역방향 매칭으로 세션 식별 ──
        |        203.0.113.5:50001  →  192.168.0.10:3344
        |        + TTL 감소 + 체크섬 재계산
        |  ⑥ DST=192.168.0.10:3344
        v
[내부 PC]  ✅ 도착
```

> 🔧 **F3 (중요)**: 위 예시는 포트까지 바꿉니다(`3344 → 50001`). **포트를 바꾸면 정의상 PAT(NAPT)** 입니다. 순수 Basic Source NAT는 IP만 바꾸고 포트는 보존합니다. 현실의 가정·기업 outbound는 거의 다 이 PAT라 예시는 현실적이지만, "일반 SNAT"와 "PAT"의 경계는 **포트 변환 유무**임을 기억하세요.

> 🔧 **F10 (심화 메커니즘)**: NAT는 주소만 갈아끼우는 게 아닙니다 — ① **IP 헤더 체크섬** 재계산, ② TCP/UDP 의사헤더(pseudo-header)에 IP가 포함되므로 **transport 체크섬도** 재계산(단 UDP 체크섬이 0이면 건드리지 않음, RFC 3022), ③ 포워딩 장비이므로 **TTL 감소**. 테이블 엔트리는 TCP FIN/RST 또는 **타임아웃(aging)** 으로 만료됩니다(무한히 쌓이지 않음).

### 📊 NAT의 3가지 유형 🔧 **F9**

| 유형 | 매핑 | 포트 변환? | 고갈 양상 | 비유 |
| --- | --- | --- | --- | --- |
| **Static NAT** | 1:1 고정 (stateless) | ✕ | 없음 | 임원 전용 직통번호 |
| **Dynamic NAT** | 풀에서 1:1 동적 | ✕ | **풀 < 동시 내부호스트면 고갈** | 공용 회의실 선착순 |
| **PAT / NAPT (Overload)** | N:1 | ○ (포트로 다중화) | 사실상 거의 없음 | 대표번호+내선번호 |

> 🔧 분류 보정: RFC 2663 정식 분류는 **Basic NAT**(주소만) vs **NAPT**(주소+포트)의 2분류이고, 업계에선 **PAT를 Dynamic NAT의 N:1 확장형**으로 봅니다. 위 3분류는 CCNA식 교육용 표준으로 유효하되, "PAT = Dynamic의 확장"임을 알아두면 경계가 또렷해집니다. **Dynamic NAT가 고갈되기 때문에 PAT가 발명**됐습니다.

### 🧭 SNAT vs DNAT — "방향"이 아니라 "필드" 기준

🔧 **F10**: 엄밀히 **SNAT = 출발지 필드 변환, DNAT = 목적지 필드 변환**입니다("나감/들어옴"은 운영적 직관). Linux netfilter에선 **DNAT=PREROUTING(라우팅 전), SNAT=POSTROUTING(라우팅 후)** 훅 위치로 구분합니다.

---

## 🎯 NAT Server (방향이 거꾸로!) — 외부 → 내부

외부 사용자가 **우리 내부 서버에 먼저 접속**하게 하려면? 여기서 **NAT Server**가 등장합니다.

```
외부 사용자가 내부 웹서버에 접속하는 길 (목적지 IP를 바꿈)
---------------------------------------------------------
[외부 사용자 (인터넷)]
        |  ① DST=203.0.113.5:80   (공인 주소로 접속 시도)
        v
[NAT 라우터 = 공개 창구]  ── ② "nat server" 정적 매핑표 조회 ──
        |                    203.0.113.5:80  →  192.168.0.100:80
        |  ③ DST=192.168.0.100:80
        v
[내부 웹서버 192.168.0.100:80]
        |  ④ 응답 (inbound DNAT의 자동 역변환으로 출발지를 공인 IP로 복원)
        v
[외부 사용자]  ✅ 응답 수신
```

> 🔧 **F10 (정밀화)**: ④의 "복원"은 별도 SNAT를 거는 게 아니라 **들어올 때 건 DNAT의 자동 역변환(reverse-DNAT)** 입니다. 단, 이 자동 복원은 내부 서버의 **리턴 경로가 같은 NAT 라우터를 다시 통과**할 때만 성립합니다(비대칭 라우팅이면 깨짐).

⚠️ **용어 주의 (벤더 종속)**: **"NAT Server"는 주로 화웨이(Huawei) VRP 명령어 이름**입니다. 같은 개념(=정적 DNAT/포트포워딩)을 벤더마다 다르게 부릅니다.

| 벤더/맥락 | 명칭 | 본질 |
| --- | --- | --- |
| **Huawei** | `nat server` | Destination NAT |
| Cisco | `ip nat inside source static` (+port) | 동일 (= Static PAT) |
| 가정용 공유기 | **포트 포워딩 / 가상 서버** | 동일 |
| Linux/iptables | **DNAT** (`-j DNAT`) | 동일 |

> 🔧 분류 연결: NAT Server는 분류상 정확히 **Static NAT + 포트 지정 = Static PAT(port forwarding)** 입니다. 참고로 **풀 Static 1:1 NAT도 (ACL 허용 시) 외부 개시 연결을 허용**합니다 — NAT Server의 차별점은 "inbound 가능"이 아니라 **포트 단위 매핑**이라는 점입니다.

💻 **Huawei `nat server` 설정 예시** *(IP는 RFC 5737 문서용 예약 대역 — 실제 환경의 공인 IP로 교체)*:

```bash
# 공인 203.0.113.5:80 으로 들어오는 요청을 → 내부 192.168.0.100:80 으로 전달
nat server protocol tcp global 203.0.113.5 80 inside 192.168.0.100 80

# 포트 변환도 가능 (외부 8080 → 내부 80)
nat server protocol tcp global 203.0.113.5 8080 inside 192.168.0.100 80
```

> ✅ 문법은 Huawei 공식 Command Reference `nat server protocol {tcp|udp} global <addr> <port> inside <addr> [host-port]` 와 일치 확인. 출처: [Huawei NAT Configuration Commands](https://support.huawei.com/enterprise/en/doc/EDOC1000174046/29a820da/nat-configuration-commands)

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스

### 🎯 대표 유즈 케이스

| # | 유즈 케이스 | 어떤 NAT? | 적합 이유 |
| --- | --- | --- | --- |
| 1 | 집/회사 여러 기기 인터넷 공유 | **PAT** | 공인 IP 1개로 수백 대 |
| 2 | 사내 웹서버 외부 공개 | **NAT Server (DNAT)** | 사설 서버를 공인 IP:포트로 노출 |
| 3 | 게임 서버·CCTV·NAS 외부 접속 | **포트 포워딩 = NAT Server** | 특정 포트만 선택 공개 |
| 4 | 사설 IP 충돌 없이 두 회사 망 통합 | **Static NAT** | 겹치는 사설망을 다른 주소로 매핑 |

### ✅ 베스트 프랙티스

1. **NAT Server는 ACL로 출입 통제** — 포트를 여는 순간 공격 표면 발생. 접근 출발지 IP를 제한.
2. **포트 변환 활용** — 외부엔 `8080`, 내부 실제 포트 `80`을 숨겨 자동 스캐닝 완화.
3. **필요한 포트만 최소 개방** — "DMZ 전체 노출" 금지, 서비스 포트만 핀포인트.
4. **로깅 필수** — 사고 추적·법적 요구 대응.

### 🏢 실제 적용

- **가정용 공유기**: PAT로 와이파이 기기 전체가 공인 IP 1개 공유.
- **통신사(ISP)**: **CGNAT**로 여러 가입자가 공인 IP 하나를 또 공유 ([A10 Networks](https://www.a10networks.com/glossary/what-is-carrier-grade-nat-cgn-cgnat/)).

---

## 5️⃣ 장점과 단점

| 구분 | 항목 | 설명 |
| --- | --- | --- |
| ✅ | **IPv4 절약** | 공인 IP 1개로 다수 연결 |
| ✅ | **내부 구조 은닉** | 외부는 공인 IP만 봄 |
| ✅ | **유연한 IP 관리** | ISP 변경 시 사설 IP 유지, 매핑만 수정 |
| ❌ | **End-to-End 단절** | 외부→내부 직접 불가 → P2P·화상통화에 STUN/TURN 필요 |
| ❌ | **상태 부담** | (PAT/Dynamic) 세션 테이블 유지 → 메모리·CPU |
| ❌ | **프로토콜 호환성** | FTP active·SIP 등은 ALG 필요 (단, SIP ALG는 역효과로 비활성화가 나은 경우 많음) |

### ⚖️ Trade-off 🔧 **F8**

```
IPv4 절약 / 내부 은닉   <--- 맞바꿈 --->   End-to-End 연결성 상실 (P2P 곤란)
관리 유연성             <----------->      ALG 의존 · 상태테이블 한계
ASIC면 라인레이트 처리  <----------->      소프트웨어 NAT는 세션 한도가 병목
```

---

## 6️⃣ 차이점 비교 — ⭐ NAT vs NAT Server

| 비교 기준 | 일반 NAT (Source NAT/PAT) | NAT Server (Destination NAT) |
| --- | --- | --- |
| **방향** | 내부 → 외부 (Outbound) | 외부 → 내부 (Inbound) |
| **누가 먼저 연결?** | 내부 기기 | **외부 사용자** |
| **바꾸는 필드** | **출발지(Source)** | **목적지(Destination)** |
| **매핑 생성** | 트래픽 발생 시 **동적** | 관리자가 **사전 정적 등록** |
| **상태성** | stateful | (정적 매핑 자체는) stateless 규칙 |
| **목적** | 내부가 인터넷 사용 | 내부 서버 **공개** |
| **대표 명령** | `nat outbound`, PAT, masquerade | `nat server`, 포트포워딩, DNAT |

```
        일반 NAT (PAT)                  NAT Server (DNAT)
  ----------------------------    ----------------------------
  내부가 먼저 노크 (내부→외부)       외부가 먼저 노크 (외부→내부)
  출발지 IP/포트를 바꿈              목적지 IP/포트를 바꿈
  동적 자동 생성                    사전 고정 등록 (= Static PAT)
  "나가는 문"                       "미리 열어둔 들어오는 문"
```

> 💡 **공존**: 웹서버를 NAT Server로 외부 공개하면서, 그 서버가 외부 결제 API를 호출할 땐 일반 NAT로 나갑니다(서로 다른 세션, conntrack이 독립 추적). 🔧 참고로 **한 패킷에 DNAT+SNAT가 동시에** 걸리는 경우도 있는데 그게 바로 **헤어핀(NAT loopback)** 입니다.

---

## 7️⃣ 사용 시 주의점

### ⚠️ 흔한 실수

| # | 실수 | 왜 문제 | 올바른 접근 |
| --- | --- | --- | --- |
| 1 | "**NAT = 방화벽**" 착각 | NAT는 정책·검사·로깅이 없음 | NAT + 명시적 방화벽 병행 |
| 2 | NAT Server + ACL 미적용 | 전 세계 포트 노출 | 출발지 IP를 ACL 제한 |
| 3 | **헤어핀 미고려** | 내부에서 공인 IP로 내부 서버 접속 실패 | NAT loopback 활성화 |
| 4 | 포트 고갈 오해 | 🔧 아래 F5 참고 | per-목적지 관점으로 이해 |

> 🔧 **F8 (보안 오해 정밀화)**: NAT(특히 PAT)는 **미요청 inbound를 매핑 부재로 차단하는 부수효과**가 있습니다. 하지만 이는 **의도된 보안 정책이 아니라 부산물**이며 — 정책·검사·로깅이 없고 UPnP/NAT-PMP·STUN 홀펀칭·outbound 개시 터널로 우회됩니다. **NAT를 방화벽으로 취급하지 마세요.** ([Internet Society](https://www.internetsociety.org/blog/2015/01/ipv6-security-myth-3-no-ipv6-nat-means-less-security/))

> 🔧 **F5 (포트 ~64K 정밀화)**: ephemeral 포트는 **(프로토콜, 목적지IP, 목적지포트) 튜플당 ~64K**입니다. 따라서 단일 공인 IP도 목적지가 다르면 **64K를 훨씬 넘는 동시 세션**을 처리합니다(CGNAT가 성립하는 이유). 고갈은 "IP당 64K 일괄 상한"이 아니라 **많은 가입자가 같은 목적지(예: 한 CDN 엣지)에 동시 접속**할 때 주로 발생합니다.

### 🔒 핵심 함정: 헤어핀 NAT

- **헤어핀(NAT loopback/reflection)**: 내부에서 **공인 IP로 내부 서버** 접근 시 트래픽이 라우터에서 U턴. 구현은 **DNAT + SNAT를 한 패킷에** 적용해야 성립.
- 🔧 **C1**: **전통적 Cisco IOS `ip nat inside/outside` 방식은 헤어핀 미지원**(inside→inside라 NAT 파이프라인 미통과). NVI(`ip nat enable`)나 NAT-on-a-stick(PBR)로 우회. **단, 헤어핀 지원 여부는 플랫폼·OS 버전마다 다르니** 장비별 확인 필수([networklessons](https://networklessons.com/cisco/ccie-routing-switching/cisco-ios-nat-stick-configuration-example)).

### 🌐 핵심 함정: CGNAT와 100.64.0.0/10

> 🔧 **F1 (P0 교정)**: CGNAT 환경에서 단말의 WAN 측에 붙는 `100.64.0.0/10`은 **RFC 1918 사설 주소가 아니라 [RFC 6598](https://datatracker.ietf.org/doc/html/rfc6598) "Shared Address Space"** 입니다. RFC 1918과 **별도 대역으로 지정된 이유**는 가입자 자기 집 LAN(10.x/192.168.x)과 **충돌하지 않게** 하기 위해서입니다.
>
> - ❌ (기존) "공인 IP가 사설처럼 100.64.x.x로 보이면 CGNAT"
> - ✅ (교정) "단말이 받은 주소가 **RFC 6598 Shared Address Space(100.64.0.0/10)** 이면 CGNAT일 가능성이 높다. **단**, 일부 캐리어는 RFC 1918 대역을 쓰기도 하므로 100.64가 안 보여도 CGNAT일 수 있다(절대 지표 아님)."
> - CGNAT에선 가입자가 고유 공인 IP를 못 받아 **포트포워딩(NAT Server)이 불가**합니다.

---

## 8️⃣ 개발자가 알아둬야 할 것들

### 📚 학습 리소스

| 유형 | 이름 | 링크 |
| --- | --- | --- |
| 📖 표준 | RFC 3022 | [Traditional NAT/NAPT](https://www.rfc-editor.org/rfc/rfc3022) |
| 📖 표준 | RFC 1918 | [사설 IP 대역](https://datatracker.ietf.org/doc/html/rfc1918) |
| 📖 표준 | RFC 6598 | [Shared Address Space(CGNAT)](https://datatracker.ietf.org/doc/html/rfc6598) |
| 📖 벤더 | Huawei NAT Commands | [`nat server` 레퍼런스](https://support.huawei.com/enterprise/en/doc/EDOC1000174046/29a820da/nat-configuration-commands) |
| 📺 심화 | Tailscale: NAT Traversal | [P2P가 NAT를 뚫는 원리](https://tailscale.com/blog/how-nat-traversal-works) |

### 🛠️ 관련 도구

| 도구 | 플랫폼 | 용도 |
| --- | --- | --- |
| `iptables`/`nftables` | Linux | SNAT/DNAT/MASQUERADE, conntrack |
| STUN/TURN/ICE | WebRTC | NAT Traversal |
| ALG | 방화벽 | FTP·SIP 페이로드 IP 보정 |
| UPnP/NAT-PMP/PCP | 공유기 | 동적 포트포워딩 |

### 🔮 트렌드

- **IPv6**(2¹²⁸ ≈ 3.4×10³⁸): NAT 원칙적 불필요. NPTv6는 [RFC 6296(Experimental)](https://datatracker.ietf.org/doc/html/rfc6296)로 정의된 stateless 변환이나 IETF/IAB는 일반 관행으로는 권장하지 않음([RFC 5902](https://www.rfc-editor.org/rfc/rfc5902.html)).
- **현실**: IPv6 보급은 지역·사업자별 편차가 커 점진적이며, NAT(특히 CGNAT)는 당분간 IPv4 환경에서 계속 쓰일 전망.

### 💬 커뮤니티 인사이트

- "포트포워딩 했는데 외부만 되고 내부는 안 돼요" → 십중팔구 **헤어핀(NAT loopback) 미지원**.
- 게임·자가호스팅 단골 좌절: **CGNAT** — 단말이 `100.64.x.x`(RFC 6598)를 받으면 ISP에 공인 IP를 별도 요청해야 함.

---

## 📎 Sources

1. [RFC 1918 — Address Allocation for Private Internets](https://www.rfc-editor.org/rfc/rfc1918.html)
2. [RFC 2663 — IP NAT Terminology and Considerations](https://www.rfc-editor.org/rfc/rfc2663.html)
3. [RFC 3022 — Traditional IP Network Address Translator](https://www.rfc-editor.org/rfc/rfc3022.html)
4. [RFC 6598 — IANA-Reserved IPv4 Prefix for Shared Address Space](https://datatracker.ietf.org/doc/html/rfc6598)
5. [RFC 5902 — IAB Thoughts on IPv6 NAT](https://www.rfc-editor.org/rfc/rfc5902.html)
6. [Huawei — NAT Configuration Commands](https://support.huawei.com/enterprise/en/doc/EDOC1000174046/29a820da/nat-configuration-commands)
7. [Wikipedia — Network Address Translation](https://en.wikipedia.org/wiki/Network_address_translation)
8. [Internet Society — IPv6 Security Myth: No NAT = Less Security](https://www.internetsociety.org/blog/2015/01/ipv6-security-myth-3-no-ipv6-nat-means-less-security/)
9. [NetworkLessons — Cisco IOS NAT-on-a-Stick (Hairpin)](https://networklessons.com/cisco/ccie-routing-switching/cisco-ios-nat-stick-configuration-example)

---

## 🔧 검증으로 교정된 내용 (rl-verify 반영 요약)

| ID | 등급 | 교정 내용 |
| --- | --- | --- |
| **F1** | 🔴 P0 | 100.64.0.0/10 = RFC 6598 Shared Address Space(사설 아님) + 인과/biconditional 교정 |
| **F2** | 🟠 P1 | "NAT=상태 기억" → PAT/Dynamic은 stateful, **Static은 stateless**로 한정 |
| **F3** | 🟠 P1 | SNAT 예시(포트 변환)는 **정확히는 PAT**임을 명시 |
| **F4** | 🟡 P2 | RFC 2663(전체 용어)/3022(1631 obsolete) 관계 정정 |
| **F5** | 🟡 P2 | 포트 ~64K → **per-5-tuple**, 고갈은 동일 목적지 집중 시 |
| **F6** | 🟡 P2 | 근거 없는 별점 평가 → 출처/관점 기반 검증 메타로 대체 |
| **F7** | 🟡 P2 | "20년·사실상 표준" → 실제 고갈(2011)·RFC 표준화로 완화 |
| **F8** | 🟡 P2 | 방화벽 — 부수적 차단효과 인정 + 의도된 보안 아님 |
| **F9** | 🟡 P2 | Dynamic vs PAT 고갈 대비를 표에 명시 |
| **F10** | 🟡 P2 | 5-tuple·체크섬·TTL·conntrack 생명주기·reverse-DNAT·hairpin 심화 |
| **C1** | ⚪ | Cisco 헤어핀 "플랫폼·버전 의존" 단서 추가 |
