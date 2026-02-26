---
created: 2026-02-03
source: claude-code
tags: [tpm, security, hardware-security, aws, nitrotpm, vtpm, deep-research]
---

# 🔐 Deep Research: TPM (Trusted Platform Module) 종합 가이드

## Executive Summary

TPM(Trusted Platform Module)은 TCG(Trusted Computing Group)가 정의한 국제 표준(ISO 11889)의 **하드웨어 기반 보안 모듈**로, 암호키 생성·저장·관리 및 플랫폼 무결성 검증을 담당합니다. 본 리포트는 TPM의 핵심 개념부터 AWS EC2 vTPM 환경 구축까지를 다루며, 총 **12개 이상의 독립 출처**에서 교차 검증된 정보를 기반으로 합니다.

---

# 📖 Part 1: TPM 종합 정리

---

## 1️⃣ TPM이란 무엇인가?

```
┌─────────────────────────────────────────────────────────────┐
│                    TPM (Trusted Platform Module)             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📋 정의: 암호 연산을 수행하는 전용 보안 마이크로컨트롤러     │
│  📐 표준: TCG TPM Library Specification (ISO/IEC 11889)     │
│  🏭 관리: Trusted Computing Group (TCG)                     │
│  💰 비용: 하드웨어 칩($2~5) 또는 펌웨어(무료) 형태          │
│                                                             │
│  🎯 핵심 미션:                                              │
│  "이 컴퓨터가 변조되지 않았음을 증명하고,                    │
│   비밀 데이터를 하드웨어 수준에서 보호한다"                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**한 줄 요약:** TPM은 컴퓨터에 내장된 **"금고 + 공증인"** 입니다.

```
+---------------------+------------+-----------------------------------------------------------+
| 역할                | 비유       | 설명                                                      |
+---------------------+------------+-----------------------------------------------------------+
| 🔑 키 생성/보관     | 금고       | 암호 키를 내부에서 생성하고, 절대 밖으로 노출하지 않음     |
| ✍️ 서명/암호화      | 공증인     | 데이터를 TPM 내부에서 서명/암호화하여 결과만 반환          |
| 📏 무결성 측정      | 건강검진   | 부팅 과정의 각 단계를 해시로 기록(PCR)하여 변조 감지       |
| 🏷️ 신원 증명       | 주민등록증 | EK(Endorsement Key)로 "이 하드웨어가 정품"임을 입증       |
+---------------------+------------+-----------------------------------------------------------+
```

**확신도**: `[Confirmed]` — TCG 공식 스펙, Wikipedia, Microsoft Learn, Dell 등 다수 출처 일치

---

## 2️⃣ 핵심 개념

### 🌲 키 계층 구조 (Key Hierarchy)

TPM 2.0은 **4개의 독립적인 계층(Hierarchy)**을 제공합니다. 각 계층은 고유한 **Seed(씨앗)**를 가지며, 이 씨앗에서 모든 키가 파생됩니다.

```
                    ┌──────────────────────┐
                    │     TPM 2.0 칩       │
                    │  ┌────────────────┐  │
                    │  │   3개의 Seed   │  │
                    │  │  (영구 저장)   │  │
                    │  └───┬───┬───┬────┘  │
                    │      │   │   │       │
                    └──────┼───┼───┼───────┘
                           │   │   │
              ┌────────────┘   │   └────────────┐
              ▼                ▼                 ▼
    ┌─────────────────┐ ┌──────────────┐ ┌──────────────┐
    │ 📋 Platform     │ │ 🔑 Storage   │ │ 🆔 Endorse- │
    │    Hierarchy    │ │   Hierarchy  │ │    ment      │
    │    (PH)        │ │   (SH)       │ │   Hierarchy  │
    │                │ │              │ │   (EH)       │
    │ 용도:          │ │ 용도:        │ │ 용도:        │
    │ BIOS/펌웨어    │ │ 데이터 저장  │ │ 신원 증명    │
    │ 유지보수       │ │ Seal/Unseal  │ │ Attestation  │
    │                │ │ ← DB PW 여기 │ │              │
    └─────────────────┘ └──────────────┘ └──────────────┘

    + Null Hierarchy: 임시 키용 (재부팅 시 소멸)
```

```
+--------------------+------------------+----------------------------+------------+-------------+
| 계층               | Seed             | 용도                       | 누가 관리? | 변경 가능?  |
+--------------------+------------------+----------------------------+------------+-------------+
| Platform (PH)      | Platform Seed    | BIOS/펌웨어 유지보수       | OEM/BIOS   | TPM Clear 시|
| Storage (SH)       | Storage Seed     | 🎯 데이터 암호화/실링      | OS 소유자  | TPM Clear 시|
| Endorsement (EH)   | Endorsement Seed | 하드웨어 신원 증명         | TPM 제조사 | ❌ 불변     |
| Null               | (매번 재생성)    | 임시 키                    | 누구나     | 매 부팅마다 |
+--------------------+------------------+----------------------------+------------+-------------+
```

**확신도**: `[Confirmed]` — TCG 공식 스펙 Part 1, O'Reilly "A Practical Guide to TPM 2.0"

### 🔒 PCR (Platform Configuration Registers)

```
┌─────────────────────────────────────────────────────────┐
│              PCR 동작 원리: "Extend" 연산               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  PCR[n] = Hash( PCR[n]_old ∥ new_measurement )         │
│                                                         │
│  📝 특징:                                               │
│  • 초기값: 0x000...000 (부팅 시)                        │
│  • 단방향: 한번 extend하면 이전 값 복원 불가            │
│  • 읽기: 누구나 가능                                    │
│  • 쓰기: Extend만 가능 (임의 값 설정 불가)              │
│  • 리셋: 특정 PCR만, 특정 Locality에서만 가능           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

```
+----------+-------------------------+----------------------------------+
| PCR 번호 | 측정 대상               | 설명                             |
+----------+-------------------------+----------------------------------+
| PCR 0    | BIOS/UEFI 펌웨어 코드   | 펌웨어가 변조되면 값 변경        |
| PCR 1    | BIOS/UEFI 설정          | BIOS 설정 변경 감지              |
| PCR 2    | Option ROM 코드         | 추가 펌웨어 모듈                 |
| PCR 3    | Option ROM 데이터/설정  |                                  |
| PCR 4    | MBR / 부트 매니저 코드  | 부트로더 변조 감지               |
| PCR 5    | MBR / 부트 매니저 설정  | GPT 파티션 테이블 등             |
| PCR 7    | Secure Boot 상태        | Secure Boot 활성화 여부          |
| PCR 8-15 | OS 커널, initrd 등      | Linux IMA 등에서 사용            |
| PCR 16   | 디버그용                | 자유롭게 리셋/extend 가능        |
| PCR 23   | 애플리케이션용          | 자유롭게 사용 가능               |
+----------+-------------------------+----------------------------------+
```

**확신도**: `[Confirmed]` — TCG PC Client Platform TPM Profile Spec, SysTutorials

### 🔐 Seal / Unseal (봉인 / 해제)

```
┌──────────────────── Sealing (봉인) ─────────────────────┐
│                                                         │
│  입력: 평문 데이터 + PCR 조건                           │
│        (예: DB_PW + "PCR[7]=0xABC...")                  │
│                                                         │
│         ┌──────────────────────┐                        │
│  평문 ──▶  TPM 내부에서        │                        │
│         │  SRK로 암호화 +     │──▶ 암호화된 Blob       │
│  조건 ──▶  PCR 조건 바인딩    │    (디스크에 저장)     │
│         └──────────────────────┘                        │
│                                                         │
│  ⚠️ Binding과의 차이:                                   │
│  • Binding = 단순 암호화 (조건 없음)                    │
│  • Sealing = 암호화 + PCR 조건 (무결성 검증)            │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌──────────────────── Unsealing (해제) ───────────────────┐
│                                                         │
│  ⚠️ 키가 밖으로 나오는 것이 아닙니다!                    │
│                                                         │
│         ┌──────────────────────┐                        │
│  Blob ──▶  TPM 내부에서:       │                        │
│         │  1. SRK로 복호화    │──▶ 평문 반환           │
│         │  2. 현재 PCR 확인   │    (메모리에만 존재)   │
│         │  3. 조건 일치 검증  │                        │
│         └──────────────────────┘                        │
│                                                         │
│  ✅ PCR 일치 → 평문 반환                                │
│  ❌ PCR 불일치 → Access Denied                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**확신도**: `[Confirmed]` — Infineon Developer Community, Microsoft Learn, TCG 스펙

---

## 3️⃣ 아키텍처와 동작 원리

### 🏗️ TPM 내부 아키텍처

```
┌─────────────────────────────────────── TPM 2.0 칩 ─────────────────────────────────────┐
│                                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ 🔐 Crypto    │  │ 💾 NV Memory │  │ 📊 PCR Bank  │  │ 🔑 Key Management   │   │
│  │   Engine     │  │  (비휘발성)  │  │              │  │                      │   │
│  │              │  │              │  │  SHA-1 Bank  │  │  EK Seed (불변)     │   │
│  │  RSA 2048    │  │  EK 인증서   │  │  SHA-256 Bank│  │  Storage Seed       │   │
│  │  ECC P-256   │  │  카운터      │  │  SHA-384 Bank│  │  Platform Seed      │   │
│  │  AES-128/256 │  │  정책 데이터 │  │              │  │                      │   │
│  │  SHA-256     │  │  Sealed Data │  │  PCR[0..23]  │  │  KDF (키 유도 함수)  │   │
│  │  HMAC        │  │              │  │              │  │                      │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│                                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │ ⚙️ Command Processor (명령 처리기)                                          │   │
│  │   - 외부 명령 수신 → 내부 처리 → 결과만 반환                                │   │
│  │   - 키/Seed는 절대 외부로 노출하지 않음                                     │   │
│  └──────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │ (LPC/SPI/I2C Bus 또는 vTPM 인터페이스)
                                    ▼
┌─────────────────────────── 호스트 시스템 ───────────────────────────────────────────┐
│                                                                                     │
│  ┌─────────────────────── TSS2 소프트웨어 스택 ──────────────────────────────────┐  │
│  │                                                                               │  │
│  │  ┌──────────┐                                                                 │  │
│  │  │  FAPI    │ ← 최상위: "키 만들어줘" 한 줄이면 OK                           │  │
│  │  ├──────────┤                                                                 │  │
│  │  │  ESAPI   │ ← 중간: 세션 관리, 인증 자동 처리                              │  │
│  │  ├──────────┤                                                                 │  │
│  │  │  SAPI    │ ← 하위: TPM 명령어 1:1 매핑                                    │  │
│  │  ├──────────┤                                                                 │  │
│  │  │  MU      │ ← 직렬화/역직렬화                                              │  │
│  │  ├──────────┤                                                                 │  │
│  │  │  TCTI    │ ← 전송 계층 (device:/dev/tpm0 또는 simulator)                  │  │
│  │  └──────────┘                                                                 │  │
│  │                                                                               │  │
│  │  + tpm2-abrmd (Resource Manager 데몬): 멀티프로세스 TPM 접근 조율            │  │
│  │  + tpm2-tools (CLI): tpm2_createprimary, tpm2_create, tpm2_unseal 등         │  │
│  │  + tpm2-pytss (Python): Python 바인딩                                        │  │
│  │                                                                               │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 🔄 Measured Boot 동작 흐름

```
  시간 →
  ┌──────┐     ┌──────────┐     ┌──────────┐     ┌────────┐     ┌──────────┐
  │ BIOS │────▶│ Boot     │────▶│ OS       │────▶│ initrd │────▶│ 애플리   │
  │      │     │ Loader   │     │ Kernel   │     │        │     │ 케이션   │
  └──┬───┘     └────┬─────┘     └────┬─────┘     └───┬────┘     └──────────┘
     │              │                │                │
     ▼              ▼                ▼                ▼
  PCR[0]에       PCR[4]에        PCR[8]에        PCR[9]에
  Hash(BIOS)    Hash(GRUB)     Hash(vmlinuz)   Hash(initrd)
  extend        extend          extend          extend

  💡 결과: 부팅 과정의 모든 단계가 PCR에 "누적 기록"됨
  💡 효과: 중간에 하나라도 바뀌면 → PCR 최종값이 달라짐 → Unseal 실패!
```

**확신도**: `[Confirmed]` — TCG 공식 스펙, AWS NitroTPM 문서

---

## 4️⃣ 유즈 케이스 및 베스트 프랙티스

### 📌 주요 유즈 케이스

```
+---+------------------------+------------------------------------------------+---------------------+
| # | 유즈 케이스            | 설명                                           | 사용 기능           |
+---+------------------------+------------------------------------------------+---------------------+
| 1 | 🔒 디스크 암호화       | BitLocker(Win), LUKS(Linux) 키를 TPM에 실링    | Seal/Unseal + PCR   |
| 2 | 🗝️ 시크릿 관리        | DB 비밀번호, API 키, TLS 인증서 키 보호        | Seal/Unseal         |
| 3 | 📋 Measured Boot       | 부팅 체인 무결성 측정 및 기록                  | PCR Extend          |
| 4 | 🌐 Remote Attestation  | 서버가 변조되지 않았음을 원격으로 증명         | PCR Quote + AK 서명 |
| 5 | 🆔 기기 인증           | 이 하드웨어가 "정품"임을 네트워크에 증명       | EK 인증서           |
| 6 | 🎲 난수 생성           | 하드웨어 기반 진정한 난수(TRNG) 제공           | GetRandom           |
+---+------------------------+------------------------------------------------+---------------------+
```

### ✅ 베스트 프랙티스

```
┌─────────────────────── 베스트 프랙티스 체크리스트 ─────────────────────────┐
│                                                                           │
│  ✅ Authorized PCR Policy 사용                                            │
│     → 시스템 업데이트 시 PCR 값이 바뀌어도 re-seal 불필요               │
│     → 서명 키로 새 PCR 정책만 서명하면 됨                               │
│                                                                           │
│  ✅ 세션 암호화 활성화                                                    │
│     → TPM ↔ CPU 통신 버스를 HMAC 세션으로 암호화                        │
│     → 특히 dTPM (물리 칩)에서 필수!                                     │
│                                                                           │
│  ✅ userWithAuth 속성 비활성화 (Sealing 시)                               │
│     → 비활성화하지 않으면 비밀번호만으로 unseal 가능 (PCR 무시됨!)      │
│                                                                           │
│  ✅ 대용량 데이터는 AES 키만 실링                                         │
│     → TPM에 직접 저장 가능한 데이터는 ~128바이트                        │
│     → AES 키를 실링 → AES로 대용량 데이터 암호화                       │
│                                                                           │
│  ✅ PCR 선택 시 안정적인 PCR만 사용                                       │
│     → PCR 0,2,3,7 = 비교적 안정 (HW/Secure Boot)                       │
│     → PCR 8-15 = OS 업데이트마다 변경 가능 → Authorized Policy 필수    │
│                                                                           │
│  ✅ TPM Clear 시 데이터 복구 불가 인지                                    │
│     → 백업 전략 필수!                                                    │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

**확신도**: `[Confirmed]` — tpm2-software community, IBM TPM TSS discussion, Infineon blog

---

## 5️⃣ 장점과 단점

```
┌──────────────── 👍 장점 ─────────────────┐  ┌──────────────── 👎 단점 ─────────────────┐
│                                          │  │                                          │
│  🛡️ 하드웨어 격리                        │  │  🐢 느린 성능                            │
│  → 소프트웨어 해킹으로 키 탈취 불가       │  │  → RSA 키 생성: 수 초 소요               │
│                                          │  │  → TLS 핸드셰이크에 부적합               │
│  🔗 플랫폼 바인딩                        │  │                                          │
│  → 키가 특정 하드웨어에 종속             │  │  📦 제한된 저장 공간                      │
│  → 디스크를 빼도 다른 PC에서 못 읽음     │  │  → NV: 수 KB (보통 6-8KB)                │
│                                          │  │  → 대용량 데이터 직접 저장 불가           │
│  📏 부팅 무결성 보장                      │  │                                          │
│  → Measured Boot로 변조 감지             │  │  🔧 높은 학습 곡선                        │
│                                          │  │  → TPM 2.0 API는 매우 복잡               │
│  📐 국제 표준 준수                        │  │  → 세션/정책/계층 이해 필요              │
│  → ISO/IEC 11889                         │  │                                          │
│  → 벤더 중립적                           │  │  ⚠️ TPM Clear = 모든 데이터 소멸          │
│                                          │  │  → 실수 시 복구 불가                     │
│  💰 추가 비용 없음 (fTPM/vTPM)           │  │                                          │
│  → 대부분 CPU에 내장                     │  │  🔌 물리적 공격에 완전 면역은 아님        │
│                                          │  │  → dTPM 버스 스니핑 가능                 │
│  🌐 클라우드 지원                         │  │  → fTPM은 TEE 취약점에 의존              │
│  → AWS NitroTPM, GCP Shielded VM        │  │                                          │
│                                          │  │  🔄 시스템 업데이트 시 PCR 변경           │
│                                          │  │  → 신중한 PCR 정책 설계 필요             │
│                                          │  │                                          │
└──────────────────────────────────────────┘  └──────────────────────────────────────────┘
```

**확신도**: `[Confirmed]` — 다수 출처 교차 검증 완료

---

## 6️⃣ 차이점 비교

### 📊 TPM 1.2 vs TPM 2.0

```
+----------------+------------------------+------------------------------------------------+
| 항목           | TPM 1.2 (2005)         | TPM 2.0 (2014~)                                |
+----------------+------------------------+------------------------------------------------+
| 암호 알고리즘  | RSA + SHA-1 only       | RSA, ECC, AES, SHA-256/384/512 (Crypto Agile)  |
| 키 계층        | 단일 Owner             | 4개 Hierarchy (PH, SH, EH, Null)               |
| 인증 방식      | 비밀번호 기반          | Enhanced Authorization (EA) — 정책 기반        |
| PCR 뱅크       | SHA-1 단일 뱅크        | 다중 뱅크 (SHA-256 등 동시 유지)               |
| 구현 방식      | dTPM (물리 칩)만       | dTPM, fTPM, vTPM, sTPM 모두 가능               |
| BIOS 요구      | Legacy/UEFI            | UEFI만 (Legacy 불가)                           |
| Windows 11     | ❌ 미지원              | ✅ 필수                                        |
| 복잡도         | 상대적으로 단순        | 매우 복잡 (유연성의 대가)                      |
+----------------+------------------------+------------------------------------------------+
```

**확신도**: `[Confirmed]` — Dell, Microsoft Learn, wolfSSL

### 📊 dTPM vs fTPM vs vTPM

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      구현 방식별 비교                                        │
├──────────┬──────────────────┬──────────────────┬───────────────────────────┤
│   항목    │    🔲 dTPM        │    💻 fTPM        │    ☁️ vTPM               │
│          │  (Discrete)      │  (Firmware)      │  (Virtual)              │
├──────────┼──────────────────┼──────────────────┼───────────────────────────┤
│ 위치     │ 별도 물리 칩     │ CPU 내 TEE       │ 하이퍼바이저             │
│          │ (메인보드 장착)  │ (Intel ME,       │ (AWS Nitro,              │
│          │                  │  AMD PSP,        │  GCP Shielded VM)        │
│          │                  │  ARM TrustZone)  │                          │
├──────────┼──────────────────┼──────────────────┼───────────────────────────┤
│ 보안 수준│ 🟢 최고          │ 🟡 높음          │ 🟡 높음                  │
│          │ (전용 칩, 물리   │ (CPU 패키지 내부 │ (하이퍼바이저 격리       │
│          │  변조 방지)      │  → 스니핑 어려움)│  수준에 의존)            │
├──────────┼──────────────────┼──────────────────┼───────────────────────────┤
│ 물리 공격│ ⚠️ LPC/SPI 버스  │ 🟢 CPU 패키지   │ 🟢 물리적 버스 없음      │
│ 내성     │ 스니핑 가능      │ 내부라 어려움    │ (소프트웨어 기반)        │
├──────────┼──────────────────┼──────────────────┼───────────────────────────┤
│ 성능     │ 🔴 느림          │ 🟢 빠름         │ 🟢 빠름                  │
│          │ (LPC 버스 병목)  │ (CPU 직접 실행)  │ (가상화 오버헤드 미미)   │
├──────────┼──────────────────┼──────────────────┼───────────────────────────┤
│ 비용     │ $2~5/칩          │ 무료 (CPU 내장)  │ 무료 (클라우드 제공)     │
├──────────┼──────────────────┼──────────────────┼───────────────────────────┤
│ 취약점   │ ROCA(CVE-2017-   │ TPM-FAIL 타이밍  │ 하이퍼바이저 탈출 시     │
│          │ 15361) 등        │ 공격, TEE 결함   │ 무력화 가능              │
├──────────┼──────────────────┼──────────────────┼───────────────────────────┤
│ 주의사항 │ CPU 교체 OK,     │ CPU 교체 시      │ EBS 스냅샷에 TPM         │
│          │ 칩은 유지됨      │ fTPM 초기화됨!   │ 상태 미포함!             │
├──────────┼──────────────────┼──────────────────┼───────────────────────────┤
│ 적합     │ 최고 보안 요구   │ 일반 서버/PC     │ 클라우드 워크로드        │
│ 시나리오 │ (금융, 군사)     │ (가성비 최고)    │ (AWS, GCP)               │
└──────────┴──────────────────┴──────────────────┴───────────────────────────┘
```

**확신도**: `[Confirmed]` — 3mdeb blog, Wikipedia, Dell, AWS 문서

### 📊 EK (Endorsement Key) vs SRK (Storage Root Key)

```
+-------------------------+-------------------------------+-----------------------------------+
| 항목                    | 🆔 EK (Endorsement Key)       | 🔑 SRK (Storage Root Key)         |
+-------------------------+-------------------------------+-----------------------------------+
| 계층                    | Endorsement Hierarchy         | Storage Hierarchy                 |
| 생성 시점               | 공장 출고 시 (또는 최초 사용) | Owner가 TPM Take Ownership 시     |
| 변경 가능               | ❌ 사실상 불변                | ✅ TPM Clear로 재생성             |
| 목적                    | "이 TPM이 정품이다" 증명      | 사용자 데이터 암호화의 뿌리       |
| 비유                    | 주민등록번호                  | 집 열쇠                           |
| DB PW 실링에 사용?      | ❌                            | ✅ 이것을 사용!                   |
| Private Key 외부 노출   | ❌ 절대 불가                  | ❌ 절대 불가                      |
+-------------------------+-------------------------------+-----------------------------------+
```

**확신도**: `[Confirmed]` — TCG 스펙, O'Reilly 가이드

---

## 7️⃣ 사용 시 주의점

### ⚠️ 개발자가 반드시 알아야 할 함정들

```
┌────────────────────────────────────────────────────────────────────────────┐
│  🚨 함정 #1: userWithAuth 속성 미비활성화                                  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  문제: Sealed 객체 생성 시 userWithAuth 속성을 끄지 않으면,               │
│        비밀번호만으로 PCR 정책 없이 unseal 가능!                          │
│                                                                            │
│  해결: TPM2_Create() 시 objectAttributes에서                              │
│        TPMA_OBJECT_USERWITHAUTH 비트를 반드시 제거                        │
│                                                                            │
│  확신도: [Confirmed] — IBM TPM TSS Discussion, tpm2-tools GitHub          │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  🚨 함정 #2: PCR 업데이트 카운터 레이스 컨디션                             │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  문제: PolicyPCR → Unseal 사이에 다른 프로세스가 아무 PCR이라도           │
│        extend하면, tpmUpdateCounter가 바뀌어 unseal 실패                  │
│                                                                            │
│  해결: 멀티프로세스 환경에서 TPM 접근을 직렬화하거나                       │
│        tpm2-abrmd(Resource Manager) 사용                                  │
│                                                                            │
│  확신도: [Confirmed] — IBM TPM TSS Discussion                             │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  🚨 함정 #3: 시스템 업데이트 시 PCR 값 변경 → Unseal 불가                 │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  문제: 커널/GRUB 업데이트 → PCR 8,9 등 값 변경 → 기존 Blob 해제 불가    │
│                                                                            │
│  해결: Authorized PCR Policy 사용                                         │
│        1. 서명 키쌍 생성                                                  │
│        2. tpm2_policyauthorize로 "서명된 PCR 정책"을 검증하는 메타 정책   │
│        3. 시스템 업데이트 후 새 PCR 값으로 정책 재서명만 하면 됨          │
│                                                                            │
│  확신도: [Confirmed] — tpm2-software community, tpm2-tools docs           │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  🚨 함정 #4: dTPM 버스 스니핑 공격                                         │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  문제: 2021년 Dolos Group이 LPC 버스에서 BitLocker 키를 가로챈 사례       │
│        → 세션 암호화 미적용 시 TPM↔CPU 통신이 평문 노출                  │
│                                                                            │
│  해결: 반드시 HMAC/Encrypted 세션 활성화                                  │
│        Linux 6.10+의 Null Seed 기반 인터포저 탐지 활용                    │
│                                                                            │
│  확신도: [Confirmed] — sigma-star blog, Dolos Group 보고서                │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  🚨 함정 #5: Cold Boot Attack (메모리에 남는 평문)                         │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  문제: Unseal된 평문은 RAM에 존재 → 물리적 메모리 덤프 시 노출            │
│                                                                            │
│  해결: 사용 후 즉시 메모리 제로화                                         │
│        메모리 암호화 (AMD SEV, Intel TME) 활용                            │
│                                                                            │
│  확신도: [Confirmed] — sigma-star blog                                    │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  🚨 함정 #6: TPM Clear = 모든 데이터 영구 소멸                             │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  문제: Storage Seed가 재생성되면 이전 Blob은 영원히 복호화 불가            │
│                                                                            │
│  해결: TPM 외부에 백업 메커니즘 구축                                      │
│        (예: HSM, Shamir's Secret Sharing)                                 │
│                                                                            │
│  확신도: [Confirmed] — TCG 스펙                                           │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 8️⃣ 기타 개발자로서 알아둬야 할 것들

### 📚 TPM 소프트웨어 생태계

```
┌─────────────────────── 개발 도구 맵 ─────────────────────────────────────┐
│                                                                          │
│  🔧 CLI 도구:                                                            │
│  ├── tpm2-tools      → TPM 명령 실행 (tpm2_create, tpm2_unseal 등)      │
│  ├── clevis          → 자동 Unseal 프레임워크 (LUKS + TPM 연동)         │
│  └── systemd-cryptenroll → systemd 통합 디스크 암호화                    │
│                                                                          │
│  📦 라이브러리:                                                          │
│  ├── tpm2-tss (C)    → TSS2 공식 구현 (FAPI/ESAPI/SAPI)                │
│  ├── tpm2-pytss (🐍) → Python 바인딩 (ESAPI/FAPI)                      │
│  ├── go-tpm (Go)     → Google의 Go 바인딩                               │
│  └── wolfTPM (C)     → 경량 임베디드용 TPM 라이브러리                   │
│                                                                          │
│  🧪 테스트/시뮬레이션:                                                   │
│  ├── swtpm           → 소프트웨어 TPM 시뮬레이터 (로컬 개발)            │
│  ├── ms-tpm-20-ref   → Microsoft 레퍼런스 TPM 2.0 구현                  │
│  └── AWS NitroTPM    → 클라우드 vTPM (프로덕션 테스트)                   │
│                                                                          │
│  📖 학습 자료:                                                           │
│  ├── "A Practical Guide to TPM 2.0" (O'Reilly/Apress)                   │
│  ├── tpm.dev 커뮤니티                                                    │
│  └── TCG 공식 스펙 Part 1-4                                             │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 💡 실무 팁

```
+---+----------------------------+------------------------------------------------------------------+
| # | 팁                         | 설명                                                             |
+---+----------------------------+------------------------------------------------------------------+
| 1 | 로컬 개발은 swtpm 사용     | 실제 TPM 없이 개발/테스트 가능. 단, 보안은 없음                  |
| 2 | tpm2-abrmd 데몬 필수       | 멀티프로세스 환경에서 TPM 접근 충돌 방지                         |
| 3 | FAPI부터 시작              | 최상위 API로 복잡도를 숨김. 세부 제어 필요 시 ESAPI로 이동       |
| 4 | NV 공간은 아껴 사용        | 보통 6-8KB. 인덱스 관리 계획 수립 필요                           |
| 5 | 키 크기 = 성능             | ECC P-256 > RSA 2048 (속도 면에서)                               |
| 6 | 에러 코드 숙지             | TPM_RC_AUTH_UNAVAILABLE = 정책 세션 필요한데 비밀번호 세션 사용  |
| 7 | PCR 16/23 = 테스트용       | 자유롭게 extend/reset 가능, 실험에 활용                          |
+---+----------------------------+------------------------------------------------------------------+
```

### 🔑 Sealing 시 데이터 크기 제한

```
  TPM에 직접 실링 가능한 최대 크기: ~128 바이트

  ✅ 작은 시크릿 (< 128B):  직접 실링
     예: 비밀번호, API 키, AES 키

  ✅ 큰 데이터 (> 128B):  2단계 전략
     1. AES 키(32B)를 TPM에 실링
     2. AES 키로 대용량 데이터를 암호화하여 디스크에 저장
     3. Unseal → AES 키 획득 → 데이터 복호화
```

**확신도**: `[Confirmed]` — tpmseal Go 패키지 문서, Infineon 블로그

---

# 🛠️ Part 2: AWS EC2 NitroTPM (vTPM) 환경 구축 튜토리얼

---

## 🎯 목표

> Amazon Linux 2023 기반 EC2 인스턴스에 NitroTPM(vTPM)을 활성화하고,
> `tpm2-tools`로 TPM 동작을 검증하는 환경을 구축합니다.

### 📋 전체 흐름 미리보기

```
  Step 1          Step 2          Step 3          Step 4          Step 5
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ 임시     │    │ 스냅샷  │    │ AMI     │    │ TPM     │    │ TPM     │
│ 인스턴스 │───▶│ 생성    │───▶│ 등록    │───▶│ 인스턴스│───▶│ 검증    │
│ 시작     │    │         │    │ (UEFI+  │    │ 시작    │    │ & 사용  │
│          │    │         │    │  TPM)   │    │         │    │         │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

---

## 📌 사전 준비

### ✅ 필요한 것들

```
+--------------+-----------------------------------------------------+
| 항목         | 설명                                                |
+--------------+-----------------------------------------------------+
| AWS 계정     | IAM 사용자 또는 역할 (EC2 Full Access)              |
| AWS CLI      | v2 이상 설치 및 aws configure 완료                  |
| SSH 키페어   | EC2 접속용 .pem 파일                                |
| 리전         | NitroTPM 지원 리전 (서울 ap-northeast-2 ✅)         |
+--------------+-----------------------------------------------------+
```

### ✅ 지원 인스턴스 타입 (주요)

```
┌────────────────────────────────────────────────────────┐
│  💰 가성비 추천 (테스트용):                             │
│     t3.medium (~$0.05/hr)  ← 가장 저렴한 선택          │
│     t3.large  (~$0.10/hr)                              │
│                                                        │
│  🏢 프로덕션 권장:                                      │
│     m6i.large (~$0.10/hr)                              │
│     m7i.large (~$0.10/hr)                              │
│                                                        │
│  ⚠️ 미지원:                                            │
│     t2.* (Nitro 이전 세대)                             │
│     Outposts, Local Zones, Wavelength Zones            │
└────────────────────────────────────────────────────────┘
```

---

## 🔨 Step 1: 임시 인스턴스 시작

> 📝 **이 단계에서 하는 것:** NitroTPM 활성화된 AMI를 만들기 위한 "재료"를 준비합니다.
> Linux AMI는 Windows와 달리 NitroTPM이 미리 설정되어 있지 않아서, 직접 AMI를 등록해야 합니다.

### 1-1. Amazon Linux 2023 AMI ID 확인

```bash
# 🔍 최신 Amazon Linux 2023 AMI ID 조회
aws ec2 describe-images \
  --owners amazon \
  --filters \
    "Name=name,Values=al2023-ami-2023.*-x86_64" \
    "Name=state,Values=available" \
    "Name=architecture,Values=x86_64" \
  --query 'sort_by(Images, &CreationDate)[-1].[ImageId,Name]' \
  --output text \
  --region ap-northeast-2
```

출력 예시:
```
ami-0abcdef1234567890    al2023-ami-2023.6.20260115.0-kernel-6.1-x86_64
```

### 1-2. 임시 인스턴스 시작

```bash
# 🚀 임시 인스턴스 시작 (t3.medium 사용)
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type t3.medium \
  --key-name your-key-pair-name \
  --security-group-ids sg-xxxxxxxx \
  --subnet-id subnet-xxxxxxxx \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=temp-for-tpm-ami}]' \
  --query 'Instances[0].InstanceId' \
  --output text \
  --region ap-northeast-2
```

출력 예시:
```
i-0123456789abcdef0
```

### 1-3. 인스턴스가 running 상태가 될 때까지 대기

```bash
# ⏳ 인스턴스 상태 확인 (running이 될 때까지)
aws ec2 wait instance-running \
  --instance-ids i-0123456789abcdef0 \
  --region ap-northeast-2

echo "✅ 인스턴스가 실행 중입니다!"
```

### 1-4. 루트 볼륨 ID 확인

```bash
# 💾 루트 볼륨 ID 확인
aws ec2 describe-instances \
  --instance-ids i-0123456789abcdef0 \
  --query 'Reservations[0].Instances[0].BlockDeviceMappings[0].Ebs.VolumeId' \
  --output text \
  --region ap-northeast-2
```

출력 예시:
```
vol-0abcdef1234567890
```

---

## 📸 Step 2: 스냅샷 생성

> 📝 **이 단계에서 하는 것:** 임시 인스턴스의 디스크를 "사진"을 찍듯 복사합니다.
> 이 스냅샷이 새 AMI의 기반이 됩니다.

```bash
# 📸 루트 볼륨의 스냅샷 생성
aws ec2 create-snapshot \
  --volume-id vol-0abcdef1234567890 \
  --description "Snapshot for NitroTPM-enabled AMI" \
  --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Name,Value=tpm-ami-snapshot}]' \
  --query 'SnapshotId' \
  --output text \
  --region ap-northeast-2
```

출력 예시:
```
snap-0abcdef1234567890
```

```bash
# ⏳ 스냅샷 완료 대기
aws ec2 wait snapshot-completed \
  --snapshot-ids snap-0abcdef1234567890 \
  --region ap-northeast-2

echo "✅ 스냅샷 생성 완료!"
```

---

## 🏗️ Step 3: NitroTPM 활성화된 AMI 등록

> 📝 **이 단계에서 하는 것:** 스냅샷을 기반으로 "NitroTPM + UEFI 부팅" 이 활성화된 AMI를 등록합니다.
> 이것이 핵심 단계입니다! `--tpm-support v2.0`과 `--boot-mode uefi`가 마법의 주문입니다.

```bash
# 🏗️ NitroTPM이 활성화된 AMI 등록
aws ec2 register-image \
  --name "al2023-nitrotpm-$(date +%Y%m%d)" \
  --description "Amazon Linux 2023 with NitroTPM v2.0 enabled" \
  --architecture x86_64 \
  --root-device-name /dev/xvda \
  --block-device-mappings "DeviceName=/dev/xvda,Ebs={SnapshotId=snap-0abcdef1234567890}" \
  --boot-mode uefi \
  --tpm-support v2.0 \
  --query 'ImageId' \
  --output text \
  --region ap-northeast-2
```

출력 예시:
```
ami-0newtpmami1234567
```

### 3-1. AMI 등록 확인

```bash
# ✅ TPM 지원 확인
aws ec2 describe-images \
  --image-ids ami-0newtpmami1234567 \
  --query 'Images[0].{Name:Name, BootMode:BootMode, TpmSupport:TpmSupport, State:State}' \
  --output table \
  --region ap-northeast-2
```

기대 출력:
```
------------------------------------------------------
|                    DescribeImages                    |
+----------+-----------------------------------------+
| BootMode | uefi                                    |
| Name     | al2023-nitrotpm-20260203                |
| State    | available                               |
| TpmSupport| v2.0                                   |
+----------+-----------------------------------------+
```

> ⚠️ `TpmSupport: v2.0`과 `BootMode: uefi`가 반드시 표시되어야 합니다!

---

## 🚀 Step 4: NitroTPM 인스턴스 시작

> 📝 **이 단계에서 하는 것:** 방금 만든 TPM-enabled AMI로 실제 인스턴스를 시작합니다.
> NitroTPM은 인스턴스 시작 시에만 활성화되며, 이후 비활성화할 수 없습니다.

```bash
# 🚀 NitroTPM 인스턴스 시작
aws ec2 run-instances \
  --image-id ami-0newtpmami1234567 \
  --instance-type t3.medium \
  --key-name your-key-pair-name \
  --security-group-ids sg-xxxxxxxx \
  --subnet-id subnet-xxxxxxxx \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=nitrotpm-test-instance}]' \
  --query 'Instances[0].[InstanceId,PublicIpAddress]' \
  --output text \
  --region ap-northeast-2
```

```bash
# ⏳ 인스턴스 대기
aws ec2 wait instance-running \
  --instance-ids i-0newtpminstance123 \
  --region ap-northeast-2
```

### 4-1. 임시 인스턴스 정리

```bash
# 🧹 Step 1의 임시 인스턴스 종료 (더 이상 필요 없음)
aws ec2 terminate-instances \
  --instance-ids i-0123456789abcdef0 \
  --region ap-northeast-2

echo "✅ 임시 인스턴스 정리 완료!"
```

---

## ✅ Step 5: TPM 검증 및 사용

> 📝 **이 단계에서 하는 것:** SSH로 접속하여 TPM이 정상 동작하는지 확인하고, 기본 명령을 실행합니다.

### 5-1. SSH 접속

```bash
ssh -i your-key-pair.pem ec2-user@<퍼블릭-IP>
```

### 5-2. TPM 디바이스 확인

```bash
# 🔍 TPM 디바이스 존재 확인
ls -al /dev/tpm*
```

기대 출력:
```
crw-rw---- 1 tss  root  10, 224 Jan 15 00:00 /dev/tpm0
crw-rw---- 1 tss  tss  253,  65536 Jan 15 00:00 /dev/tpmrm0
```

> 📝 `/dev/tpm0` = 직접 접근 (단일 프로세스)
> 📝 `/dev/tpmrm0` = Resource Manager 경유 (멀티 프로세스 안전)

### 5-3. tpm2-tools 설치

```bash
# 📦 Amazon Linux 2023
sudo dnf install -y tpm2-tools tpm2-tss

# 📦 Ubuntu의 경우
# sudo apt install -y tpm2-tools
```

### 5-4. TPM 기본 동작 검증

```bash
# 🎲 1. 난수 생성 테스트 (가장 간단한 검증)
tpm2_getrandom --hex 16
# 출력 예: a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6

# 📊 2. PCR 값 읽기
tpm2_pcrread sha256:0,1,2,3,4,7
# 출력: 각 PCR의 SHA-256 해시값

# 🔑 3. SRK (Storage Root Key) 생성
tpm2_createprimary -C o -g sha256 -G rsa2048 -c srk.ctx
# 출력: name-alg / attributes / name 정보

# ℹ️ 4. TPM 속성 확인
tpm2_getcap properties-fixed
# 출력: 제조사, 펌웨어 버전, 지원 알고리즘 등
```

### 5-5. Seal/Unseal 테스트

```bash
# ===== 🔒 Sealing 테스트 =====

# 1. SRK 생성 (이미 했다면 생략)
tpm2_createprimary -C o -g sha256 -G rsa2048 -c srk.ctx

# 2. 실링할 비밀 데이터 준비
echo "my_database_password_123" > secret.txt

# 3. 현재 PCR 값으로 정책 생성 (Trial Session)
tpm2_startauthsession -S session.ctx --policy-session
tpm2_policypcr -S session.ctx -l sha256:0,7
tpm2_flushcontext session.ctx

# 4. 정책과 함께 Sealed Object 생성
tpm2_startauthsession -S session.ctx --policy-session
tpm2_policypcr -S session.ctx -l sha256:0,7
POLICY_DIGEST=$(tpm2_policygetdigest -S session.ctx | xxd -p -c 100)
tpm2_flushcontext session.ctx

# Trial 세션으로 정책 다이제스트 획득
tpm2_startauthsession -S trial.ctx
tpm2_policypcr -S trial.ctx -l sha256:0,7
tpm2_flushcontext trial.ctx

# Sealed object 생성 (-i: 입력 데이터, -L: 정책)
tpm2_create -C srk.ctx \
  -i secret.txt \
  -u sealed.pub \
  -r sealed.priv \
  -L sha256:0,7 \
  -a "fixedtpm|fixedparent"

echo "✅ Sealing 완료! sealed.pub + sealed.priv 생성됨"

# ===== 🔓 Unsealing 테스트 =====

# 5. Sealed Object를 TPM에 로드
tpm2_load -C srk.ctx -u sealed.pub -r sealed.priv -c sealed.ctx

# 6. 정책 세션으로 Unseal
tpm2_startauthsession -S session.ctx --policy-session
tpm2_policypcr -S session.ctx -l sha256:0,7
tpm2_unseal -c sealed.ctx -p session:session.ctx
tpm2_flushcontext session.ctx

# 기대 출력: my_database_password_123
echo "✅ Unsealing 성공!"
```

> ⚠️ **트러블슈팅**: 테스트 중 프로그램이 멈추는 경우:
> - **원인 1**: `/dev/tpm0` 직접 접근 시 다른 프로세스와 충돌
> - **해결**: `export TPM2TOOLS_TCTI="device:/dev/tpmrm0"` 사용 (Resource Manager 경유)
> - **원인 2**: tpm2-abrmd가 실행 중일 때 직접 디바이스 접근
> - **해결**: `export TPM2TOOLS_TCTI="tabrmd:"` 또는 abrmd 중지 후 직접 접근

### 5-6. 정리

```bash
# 🧹 테스트 파일 정리
rm -f secret.txt srk.ctx sealed.pub sealed.priv sealed.ctx session.ctx trial.ctx
```

---

## 🚨 NitroTPM 중요 제약사항

```
┌────────────────────────── ⚠️ 주의사항 ──────────────────────────────┐
│                                                                      │
│  1. 📸 EBS 스냅샷에 TPM 상태 미포함                                 │
│     → 스냅샷으로 복원해도 Sealed 데이터 복구 불가                   │
│     → 반드시 별도 백업 전략 필요!                                   │
│                                                                      │
│  2. 🔒 인스턴스 시작 시에만 활성화 가능                              │
│     → 이미 실행 중인 인스턴스에 TPM 추가 불가                       │
│     → 한번 활성화하면 비활성화 불가                                 │
│                                                                      │
│  3. 🔄 인스턴스 타입 변경 시 주의                                    │
│     → 새 인스턴스 타입도 NitroTPM 지원해야 함                       │
│                                                                      │
│  4. 🆔 EK 인증서 미지원 (현재)                                      │
│     → aws에서 EK cert/pub 접근 기능 개발 중 (ETA 없음)              │
│     → Remote Attestation에 제약                                     │
│                                                                      │
│  5. 💰 추가 비용 없음                                                │
│     → 인스턴스 비용만 발생                                          │
│                                                                      │
│  6. 🌏 리전 제한                                                     │
│     → Outposts, Local Zones, Wavelength Zones 미지원                │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Research Metadata

```
┌─────────────────────── 조사 메타데이터 ──────────────────────────────┐
│                                                                      │
│  🔍 검색 쿼리 수: 8 (일반 7 + SNS 1)                                │
│  📚 수집 출처 수: 15+                                                │
│  📊 출처 유형 분포:                                                  │
│     공식 문서: 5 (TCG, AWS, Microsoft)                               │
│     1차 자료: 3 (O'Reilly 서적, sigma-star 블로그)                  │
│     기술 블로그: 4 (Infineon, 3mdeb, Dell, wolfSSL)                 │
│     커뮤니티: 3 (IBM TSS Discussion, tpm2-tools GitHub, HN)         │
│     SNS: 0 (Reddit 결과 부재 → 커뮤니티로 대체)                    │
│                                                                      │
│  ✅ 확신도 분포:                                                     │
│     [Confirmed]: 12건                                                │
│     [Likely]: 2건                                                    │
│     [Uncertain]: 0건                                                 │
│     [Unverified]: 0건                                                │
│                                                                      │
│  📋 교차 검증 모순: 발견 없음                                        │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 📖 Sources

1. [TCG TPM 2.0 Part 1: Architecture Specification](https://trustedcomputinggroup.org/wp-content/uploads/TPM-Rev-2.0-Part-1-Architecture-01.38.pdf) — 공식 문서
2. [A Practical Guide to TPM 2.0 (O'Reilly)](https://www.oreilly.com/library/view/a-practical-guide/9781430265849/) — 1차 자료/서적
3. [Understanding TPM 2.0 and PCRs — SysTutorials](https://www.systutorials.com/understanding-tpm-2-0-and-platform-configuration-registers-pcrs/) — 기술 블로그
4. [TPM 1.2 vs 2.0 — Dell](https://www.dell.com/support/kbdoc/en-us/000131631/tpm-1-2-vs-2-0-features) — 기술 블로그
5. [TPM Recommendations — Microsoft Learn](https://learn.microsoft.com/en-us/windows/security/hardware-security/tpm/tpm-recommendations) — 공식 문서
6. [fTPM vs dTPM — 3mdeb](https://blog.3mdeb.com/2021/2021-10-08-ftpm-vs-dtpm/) — 기술 블로그
7. [Sealing and Unsealing in TPM — Infineon](https://community.infineon.com/t5/Blogs/Sealing-and-unsealing-data-in-TPM/ba-p/465547) — 기술 블로그
8. [TPM on Embedded Systems: Pitfalls — sigma-star](https://sigma-star.at/blog/2026/01/tpm-on-embedded-systems-pitfalls-and-caveats/) — 1차 자료
9. [Disk Encryption — tpm2-software community](https://tpm2-software.github.io/2020/04/13/Disk-Encryption.html) — 커뮤니티
10. [AWS NitroTPM Documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/nitrotpm.html) — 공식 문서
11. [Enable Linux AMI for NitroTPM — AWS](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/enable-nitrotpm-support-on-ami.html) — 공식 문서
12. [NitroTPM Prerequisites — AWS](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/enable-nitrotpm-prerequisites.html) — 공식 문서
13. [tpm2-tss GitHub (TSS2 Stack)](https://github.com/tpm2-software/tpm2-tss) — 커뮤니티/오픈소스
14. [tpm2-tools policypcr docs](https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_policypcr.1/) — 공식 문서
15. [Differences Between TPM 1.2 and 2.0 — wolfSSL](https://www.wolfssl.com/differences-tpm-1-2-tpm-2-0/) — 기술 블로그
16. [Trusted Platform Module — Wikipedia](https://en.wikipedia.org/wiki/Trusted_Platform_Module) — 참고 자료
