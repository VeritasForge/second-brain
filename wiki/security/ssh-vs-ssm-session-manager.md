---
tags: [security, aws, ssm, ssh, network, protocol]
created: 2026-04-23
---

# SSH vs SSM Session Manager — 프로토콜, 아키텍처, 통신 구조 Deep Dive

---

## 1. 기초 개념: MITM 공격이란?

**MITM (Man-In-The-Middle)** = 통신하는 두 당사자 사이에 해커가 끼어들어 데이터를 엿보거나 변조하는 공격.

```
정상 통신:
  철수 📞 ──────────────────────────── 📞 영희
       "내일 3시에 카페에서 만나자"
       → 영희가 정확히 들음 ✅

MITM 공격:
  철수 📞 ────► 🕵️ 해커 ────► 📞 영희
       "내일 3시에        "내일 3시에
        카페에서 만나자"    PC방에서 만나자" ← 변조!
       
  📌 철수는 영희와 직접 통화한다고 생각
  📌 영희도 철수에게 직접 듣는다고 생각
  📌 둘 다 해커가 중간에 있는 걸 모름
```

네트워크에서의 동작:

```
  User ──► 🕵️ 해커 ──► Server
       암호화1     암호화2

  ① User에게: "나 Server야" (가짜 인증서/키 제시)
  ② Server에게: "나 User야" (정상 접속)
  ③ 해커는 중간에서 모든 내용을 읽고/수정 가능
```

---

## 2. 신뢰 모델: TOFU vs PKI

"이 서버가 진짜 맞아?"를 확인하는 두 가지 방식이다.

### TOFU (Trust On First Use) — SSH가 사용

**비유**: 전학생 첫날 얼굴 기억하기

```
첫날: "너 김철수지?" → "응!" → 얼굴 기억 📸
다음날: (같은 얼굴) → "김철수 맞네" ✅
어느 날: (다른 얼굴) → "너 누구야?! 🚨" ← 경고!

📌 문제: 첫날에 가짜 김철수가 왔으면? → 모르고 기억해버림 😱
```

실제 SSH 동작:

```
$ ssh user@server.com
The authenticity of host 'server.com' can't be established.
ED25519 key fingerprint is: SHA256:AbCdEf1234567890...
Are you sure you want to continue? (yes/no)    ← "Trust On FIRST Use"
→ yes → ~/.ssh/known_hosts에 저장
→ 이후 지문 불일치 시 🚨 WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!
```

### PKI (Public Key Infrastructure) — HTTPS가 사용

**비유**: 학교 교무실이 발급한 학생증 확인하기

```
첫날: "학생증 보여줘" → 교무실 도장 확인 🏫 → 진짜네 ✅
📌 장점: 첫날에도 가짜 구별 가능 (교무실 도장이 없으면 거부)
📌 약점: 교무실이 해킹당하면? → 가짜 학생증 발급 가능 😱
```

실제 HTTPS 동작:

```
① 서버가 인증서 제시 → "나는 naver.com이야"
② 브라우저 검증:
   ├── 발급 CA? → DigiCert
   ├── 브라우저에 미리 설치된 Root CA 목록에 DigiCert 있음? → ✅
   ├── 인증서 유효기간? → ✅ 유효
   ├── 도메인 일치? → ✅ naver.com
   └── 서명 위조 안 됨? → ✅
③ 모두 통과 → 🔒 자물쇠 + 접속
```

### MITM 방어 능력 비교

| 시나리오              | TOFU (SSH)                       | PKI (HTTPS)                                                     |
| --------------------- | -------------------------------- | --------------------------------------------------------------- |
| **첫 접속 공격**      | ⚠️ 취약 (검증 수단 없음)         | ✅ CA 인증서로 방어                                              |
| **이후 접속 공격**    | ✅ 안전 (지문 비교)               | ✅ 안전 (인증서 검증)                                            |
| **CA/인증기관 해킹**  | 해당 없음                        | ⚠️ 가짜 인증서 발급 가능 (실제 사례: 2011 DigiNotar 해킹)       |
| **사용자가 경고 무시** | ⚠️ 취약                          | ⚠️ 취약                                                         |
| **중앙 기관 의존**    | ❌ 불필요 (탈중앙)                | ✅ CA 필요                                                       |

---

## 3. SSH vs HTTPS 프로토콜 차이

### SSH는 TLS를 사용하지 않는다

SSH는 RFC 4253에서 정의한 **자체 암호화 프로토콜(SSH Transport Protocol)**을 사용한다. HTTPS는 **HTTP + TLS**의 조합이다. 둘 다 AES, ChaCha20 같은 암호화 알고리즘을 "사용"할 수 있지만, 프로토콜 자체는 완전히 다르다.

```
SSH  = 전용 보안 택배 시스템 (자체 규칙으로 포장·배송)
TLS  = 범용 보안 포장 서비스 (누구든 이 포장을 쓸 수 있음)
HTTPS = 일반 편지(HTTP)를 TLS 포장으로 감싼 것
```

| 비교 기준           | SSH                                        | HTTPS (HTTP + TLS)                         |
| ------------------- | ------------------------------------------ | ------------------------------------------ |
| **암호화 프로토콜** | SSH Transport Protocol (자체)              | TLS 1.2/1.3                                |
| **암호화 알고리즘** | AES, ChaCha20 등                           | AES, ChaCha20 등                           |
| **키 교환**         | Diffie-Hellman (자체 구현)                  | Diffie-Hellman (TLS 내장)                   |
| **인증 방식**       | 공개키, 비밀번호                            | 인증서 (CA 기반)                            |
| **신뢰 모델**       | TOFU                                       | PKI                                        |
| **기본 포트**       | 22                                         | 443                                        |
| **방화벽 친화성**   | ⚠️ 포트 22 (종종 차단)                     | ✅ 포트 443 (거의 차단 안 됨)               |

### 암호화 강도는 동일, 차이는 네트워크 아키텍처

**HTTPS가 보안상 더 좋은가?** — 암호화 강도 자체는 거의 동일하다. 차이는 "네트워크 보안 모델"에서 나온다:

- SSH: 포트 22를 인바운드로 열어야 함 → 공격 표면 존재
- HTTPS(SSM 맥락): 아웃바운드만 사용 가능 → 인바운드 포트 0개 가능

---

## 4. 공격 표면(Attack Surface)이란?

**공격 표면 = 해커가 침입을 시도할 수 있는 모든 "문과 창문"**

```
집 A: 현관문 + 뒷문 + 창문 5개 → 공격 표면 7개 ⚠️
집 B: 현관문 1개 (방탄유리)    → 공격 표면 1개 ✅
```

### "포트 22든 443이든 열려있으면 공격 가능한 거 아니야?"

맞다! 하지만 **"어디에 열려있느냐"**와 **"뒤에서 뭐가 듣고 있느냐"**가 핵심이다.

```
SSH (포트 22 오픈):
  해커 ──── 포트 22 ────► [네 EC2의 sshd]
  → 공격 대상: 네가 직접 관리하는 서버
  → Brute Force, SSH 취약점, Key 탈취 가능

SSM (EC2에 포트 0개):
  해커 ──── ??? ────► [네 EC2] ← 포트가 없음! 문이 없는 집
  해커 ──── 443 ────► [AWS SSM 서비스 엔드포인트]
  → 공격 대상: AWS가 24/7 관리하는 서비스
  → IAM 인증 없으면 무조건 거부
```

| 공격 표면 항목        | SSH (Bastion)          | SSM                   |
| --------------------- | ---------------------- | --------------------- |
| **EC2 인바운드 포트** | 22번 오픈 ⚠️           | 0개 ✅                |
| **포트 스캔 가능**    | ✅ 발견됨              | ❌ 발견 불가           |
| **Brute Force**       | ✅ 가능                | ❌ IAM 인증만          |
| **서비스 관리**       | 직접 관리              | AWS 관리              |

---

## 5. SSM Session Manager vs Bastion Server

### 핵심 차이: 직접 연결 vs 중개자 경유

```
SSH:   User ──────────────────► EC2        (클라이언트-서버 직접 연결)
SSM:   User ──► AWS SSM 서비스 ◄── EC2     (중개자 경유, 브로커)
```

이 **"중개자가 있다/없다"**에서 모든 차이가 파생된다:

| 특성                   | SSH (직접 연결)                       | SSM (중개자 경유)                        |
| ---------------------- | ------------------------------------- | ---------------------------------------- |
| **인바운드 포트**      | 22번 오픈 필수 ⚠️                     | **0개** ✅                                |
| **SSH Key 관리**       | 생성/분배/회수/교체 필요              | **불필요** (IAM으로 제어)                |
| **점프 서버**          | 별도 EC2 운영 필요 💰                 | **불필요** (AWS 관리형)                   |
| **접근 제어**          | SSH Key 보유 여부                     | **IAM Policy** (중앙 관리)               |
| **접근 로그**          | 별도 설정 필요                        | **CloudTrail 자동 기록**                 |
| **세션 녹화**          | 별도 도구 필요                        | **S3/CloudWatch에 자동 저장**            |
| **퇴사자 접근 차단**   | SSH Key 회수 (누락 위험)              | **IAM 권한 제거로 즉시 차단**            |
| **비용**               | Bastion EC2 비용                      | 무료                                     |

---

## 6. SSM이 인바운드 포트 없이 동작하는 원리

```
┌────────────────────────────────────────────────────────────────┐
│                    SSM Session Manager 통신 구조                │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  [Private EC2]                        [AWS SSM 서비스]          │
│  │                                    │                        │
│  │ ① SSM Agent 시작 시:               │                        │
│  │   아웃바운드 HTTPS(443)로           │                        │
│  │   SSM 서비스에 연결 ──────────────► │                        │
│  │   "나 i-xxxx야, 명령 기다릴게"      │                        │
│  │                                    │                        │
│  │ ② ~20초마다 폴링:                  │                        │
│  │   "새 명령 있어?" ────────────────► │                        │
│  │   (항상 Agent가 먼저 나감)          │                        │
│  │                                    │   [개발자 PC]           │
│  │                                    │   │                    │
│  │                                    │   │ ③ aws ssm          │
│  │                                    │   │   start-session    │
│  │                                    │ ◄─┘   --target i-xxxx │
│  │                                    │   (아웃바운드 HTTPS)    │
│  │                                    │                        │
│  │ ④ SSM 서비스가 Agent에 전달:        │                        │
│  │ ◄──────── "세션 시작해"             │                        │
│  │   (기존 아웃바운드 연결로 응답)      │                        │
│  │                                    │                        │
│  │ ⑤ WebSocket 채널 수립              │                        │
│  │ ◄────── 양방향 통신 ──────────────► │ ◄────────► 개발자 PC   │
│  │                                    │                        │
│  │ 📌 EC2 Security Group:             │                        │
│  │   인바운드: 없음! 🎉               │                        │
│  │   아웃바운드: 443 → SSM 엔드포인트  │                        │
└────────────────────────────────────────────────────────────────┘
```

**비유**: 📞 전화 vs 💬 카카오톡

- **SSH** = 직접 전화 — 상대방이 전화기를 켜놓고 있어야 함 (인바운드 포트 오픈)
- **SSM** = 카카오톡 — 카톡 앱이 카카오 서버에 "나 온라인이야" 하고 먼저 연결 (아웃바운드). 인바운드 불필요

### "아웃바운드 연결인데 어떻게 응답을 받아?"

TCP 연결이 한번 맺어지면 **양방향 통신이 가능**하다. AWS Security Group은 **stateful**이다:

> *"Security groups are stateful — if you send a request from your instance, the response traffic for that request is allowed to flow in regardless of inbound security group rules."* — AWS 공식 문서

- **인바운드 포트를 여는 것** = "외부에서 새로운 연결을 시작할 수 있게 허용"
- **아웃바운드로 나간 연결** = "내가 시작한 연결의 응답은 자동으로 돌아옴"

---

## 7. SSM의 셸 실행 방식 — 에뮬레이션이 아니라 릴레이

### rl-verify 검증으로 확인된 정정사항

SSM Agent 소스코드([shell_unix.go](https://github.com/aws/amazon-ssm-agent/blob/b9654b268afcb7e70a9cc6c6d9b7d2a676f5b468/agent/session/plugins/shell/shell_unix.go)) 검증 결과, SSM Agent는 `github.com/kr/pty` 패키지로 **실제 PTY(pseudo-terminal)를 할당**하고 `exec.Command("sh")`로 **실제 셸을 실행**한다. sshd와 **동일한 메커니즘**이다.

```
SSH:  User ←── SSH 프로토콜 ──► sshd    ──► PTY ──► bash
SSM:  User ←── WebSocket ──► SSM 서비스 ←── WebSocket ──► SSM Agent ──► PTY ──► bash
                                                                          ↑
                                                              이 부분은 sshd와 동일!
```

| 항목               | SSH                              | SSM Session Manager                      |
| ------------------ | -------------------------------- | ---------------------------------------- |
| **셸 실행 주체**   | sshd 데몬                        | SSM Agent                                |
| **PTY 할당**       | sshd가 로컬 PTY 할당             | Agent가 로컬 PTY 할당 (**동일**)          |
| **입출력 전달**    | SSH 프로토콜 (직통)              | WebSocket 릴레이 (중계)                   |
| **네트워크 경로**  | User → EC2 (직접 SSH 기준 1홉)  | User → SSM → EC2 (2홉)                  |
| **지연(Latency)**  | 낮음 (직통)                      | 약간 높음 (중계 경유)                     |

- **에뮬레이션** (가짜 셸을 흉내냄) ❌ 부정확
- **릴레이/중계** (진짜 셸의 입출력을 WebSocket으로 전달) ✅ 정확

**비유**: 🎮

- **SSH** = 게임 컨트롤러를 TV에 **직접 유선 연결**
- **SSM** = 클라우드 게임 (GeForce NOW) — 게임은 서버에서 **실제로 돌아가고**, 입력/화면만 스트리밍

---

## 8. SSM Agent 기본 정보

### SSM = AWS Systems Manager

```
이름 변천사:
1. Amazon Simple Systems Manager (SSM)    ← 최초 이름
2. Amazon EC2 Systems Manager (SSM)       ← 중간 이름
3. AWS Systems Manager                    ← 현재 이름 (약자 SSM은 유지)
```

Session Manager는 SSM의 여러 기능 중 하나 (Run Command, Parameter Store, Patch Manager 등 포함).

### SSM Agent 설치 위치

관리 대상 **EC2 인스턴스 내부**에 설치되는 백그라운드 데몬이다.

| AMI                                               | SSM Agent 사전 설치 |
| ------------------------------------------------- | ------------------- |
| Amazon Linux (1, 2, 2023)                         | ✅                  |
| Ubuntu Server (16.04+, 2018-06-27 이후 AMI)       | ✅                  |
| Windows Server (AWS 공식 AMI 기준)                 | ✅                  |
| 기타 AMI                                           | 수동 설치 필요      |

> ⚠️ 사전 설치된 AMI라도 Agent 실행 상태와 IAM Role(Instance Profile) 연결을 확인할 것.

### 통신 메커니즘

- 평상시: 약 **20초마다 SSM 서비스에 폴링** (HTTPS 443 아웃바운드)
- Session Manager 세션 시: **WebSocket 채널 수립** (Amazon Message Gateway Service, `ssmmessages` 엔드포인트)
- MGS(WebSocket) 우선, 불가능하면 MDS(Message Delivery Service)로 폴백하는 **하이브리드 방식**

---

## 📎 Sources

1. [RFC 4253 - SSH Transport Layer Protocol](https://www.rfc-editor.org/rfc/rfc4253) — SSH 프로토콜 공식 표준
2. [Trust on First Use - Wikipedia](https://en.wikipedia.org/wiki/Trust_on_first_use) — TOFU 개념
3. [Man-in-the-middle attack - Wikipedia](https://en.wikipedia.org/wiki/Man-in-the-middle_attack) — MITM 공격
4. [AWS SSM Session Manager Docs](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html) — 공식 문서
5. [SSM Agent shell package - Go Docs](https://pkg.go.dev/github.com/aws/amazon-ssm-agent/agent/session/shell) — PTY 할당 확인
6. [shell_unix.go - GitHub](https://github.com/aws/amazon-ssm-agent/blob/b9654b268afcb7e70a9cc6c6d9b7d2a676f5b468/agent/session/plugins/shell/shell_unix.go) — SSM Agent 소스코드
7. [AWS Security Groups (Stateful) - AWS VPC Docs](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html) — Stateful 방화벽
8. [Systems Manager service name history - AWS Docs](https://docs.aws.amazon.com/systems-manager/latest/userguide/service-naming-history.html) — SSM 이름 변천
9. [Find AMIs with SSM Agent preinstalled - AWS Docs](https://docs.aws.amazon.com/systems-manager/latest/userguide/ami-preinstalled-agent.html) — Agent 사전 설치 AMI
10. [Improved SSM latency - AWS Blog](https://aws.amazon.com/blogs/mt/improved-web-application-load-time-with-aws-systems-manager-port-forwarding-sessions/) — 지연 개선
11. [TOFU MITM vulnerability - USENIX](https://www.usenix.org/legacy/events/usenix08/tech/full_papers/wendlandt/wendlandt_html/index.html) — TOFU 보안 분석
12. [PKI MITM and CA compromise](https://murshedsk135.medium.com/man-in-the-middle-attack-certificates-pki-and-asymmetric-key-establishment-a-comprehensive-991d6fda274b) — CA 해킹 시나리오
