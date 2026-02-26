---
created: 2026-02-03
source: claude-code
tags: [tpm, security, pcr, deep-research]
---

## Deep Research: TPM USERWITHAUTH vs PCR 정책 — 현재 tpm.py 보안 수준 분석

---

### Executive Summary

**사용자의 이해 ("TPM = PCR로 이중 보안")는 틀리지 않지만, 현재 tpm.py는 PCR을 전혀 사용하지 않고 있다.**

TPM seal/unseal에는 두 가지 독립적인 인증 경로가 있다:
1. **Password(auth) 기반** — 비밀번호를 알면 unseal (현재 tpm.py가 사용하는 방식)
2. **PCR 정책 기반** — 시스템 부팅 상태가 일치해야 unseal (현재 tpm.py에 미구현)

현재 구현은 "TPM 보안의 절반"만 활용 중이다.

---

### Findings

#### 1. PCR이란 무엇인가 (쉬운 설명)

**PCR (Platform Configuration Registers)** = TPM 칩 안에 있는 **"부팅 기록장"**

서버가 켜질 때 이런 일이 일어난다:

```
[전원 ON]
   ↓
[BIOS/UEFI 로드] → TPM에 기록: "이 BIOS가 로드됨" (PCR[0])
   ↓
[부트로더 로드]  → TPM에 기록: "이 부트로더가 로드됨" (PCR[1])
   ↓
[OS 커널 로드]   → TPM에 기록: "이 커널이 로드됨" (PCR[3])
   ↓
[앱 실행]        → TPM에 기록: "이 앱이 실행됨" (PCR[8-15])
```

각 PCR에는 해시값이 저장되며, **한번 기록되면 덮어쓸 수 없다** (extend만 가능). 서버를 재부팅해야만 초기화된다.

| PCR 인덱스 | 측정 대상 | 변경 시점 |
|---|---|---|
| PCR[0] | BIOS/UEFI 펌웨어 | BIOS 업데이트 시 |
| PCR[1] | 부트로더 (GRUB 등) | 부트로더 업데이트 시 |
| PCR[2-3] | OS 커널, 설정 | OS 업데이트 시 |
| PCR[4-5] | 부팅 드라이버 | 드라이버 변경 시 |
| PCR[7] | Secure Boot 정책 | Secure Boot 설정 변경 시 |
| PCR[8-15] | 런타임 측정 | 앱/서비스 변경 시 |
| PCR[16-23] | 사용자 정의 | 직접 extend 시 |

- **확신도**: `[Confirmed]` — [Microsoft Learn](https://learn.microsoft.com/en-us/windows/security/hardware-security/tpm/switch-pcr-banks-on-tpm-2-0-devices), [SysTutorials](https://www.systutorials.com/understanding-tpm-2-0-and-platform-configuration-registers-pcrs/), [Infineon Blog](https://community.infineon.com/t5/Blogs/Sealing-and-unsealing-data-in-TPM/ba-p/465547) 모두 일치

---

#### 2. TPM Seal/Unseal의 두 가지 인증 경로

TPM 2.0에서 sealed 객체를 unseal하려면, **두 가지 경로** 중 하나를 선택하거나 결합할 수 있다:

```
                    ┌─────────────────────────────────┐
                    │    Sealed Data (TPM 내부)        │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────┴──────────────────┐
                    │         Unseal 요청              │
                    └──────────────┬──────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                                         ▼
   ┌──────────────────┐                    ┌───────────────────┐
   │  경로 A: Password │                    │  경로 B: PCR 정책  │
   │  (auth값 제출)     │                    │  (시스템 상태 검증)  │
   └────────┬─────────┘                    └────────┬──────────┘
            │                                       │
   "비밀번호 맞으면 열림"                    "부팅 상태가 일치하면 열림"
```

**핵심: `USERWITHAUTH` 속성이 어떤 경로를 허용하는지 결정한다.**

| `USERWITHAUTH` 값 | Password로 unseal | PCR 정책으로 unseal | 의미 |
|---|---|---|---|
| **SET** (현재 tpm.py) | ✅ 가능 | ✅ 가능 | password **또는** 정책, 둘 중 하나면 OK |
| **CLEAR** | ❌ 불가 | ✅ 가능 | **오직** 정책만으로 unseal 가능 |

- **확신도**: `[Confirmed]` — [tpm2-tools GitHub #1123](https://github.com/tpm2-software/tpm2-tools/issues/1123), [tpm2-tools 공식 문서](https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_create.1/), [Linux kernel trusted keys patch](https://patchwork.kernel.org/patch/7839331/)

---

#### 3. 현재 tpm.py의 정확한 보안 수준

`tpm.py:308-312`를 보면:

```python
seal_attrs = (
    TPMA_OBJECT.FIXEDTPM        # 이 TPM 칩에 물리적 바인딩
    | TPMA_OBJECT.FIXEDPARENT   # 부모 키(SRK) 변경 불가
    | TPMA_OBJECT.USERWITHAUTH  # ← password로 unseal 허용
)
```

**현재 보호 구조:**

```
보호 레이어 1: FIXEDTPM
   → sealed blob은 이 TPM 칩에서만 unseal 가능
   → 디스크를 다른 서버에 옮기면 unseal 불가 ✅

보호 레이어 2: auth password
   → unseal 시 auth값(비밀번호) 제출 필요
   → auth를 모르면 unseal 불가 ✅

보호 레이어 3: PCR 정책
   → ❌ 미구현 — 시스템 부팅 상태 검증 없음
```

**이것이 의미하는 것 (구체적 공격 시나리오):**

| 공격 시나리오 | PCR 정책 있을 때 | 현재 (PCR 없음) |
|---|---|---|
| 디스크를 다른 서버에 장착 | ❌ 차단 (FIXEDTPM) | ❌ 차단 (FIXEDTPM) |
| 같은 서버에서 USB로 다른 OS 부팅 | ❌ 차단 (PCR 불일치) | **✅ auth 알면 unseal 성공** |
| 같은 서버에서 루트킷에 감염된 OS로 부팅 | ❌ 차단 (PCR 불일치) | **✅ auth 알면 unseal 성공** |
| 같은 서버에서 정상 OS + auth 탈취 | ❌ 차단 (PCR 일치하므로 unseal 가능이긴 함) | ✅ unseal 성공 |
| 메모리 덤프로 auth 탈취 후 같은 서버에서 시도 | 정상 부팅이면 PCR 일치 → unseal 가능 | unseal 가능 |

- **확신도**: `[Confirmed]` — 코드 직접 확인 + [tpm2-software 커뮤니티](https://tpm2-software.github.io/2021/02/17/Protecting-secrets-at-TPM-interface.html), [tpm2-tools #1123](https://github.com/tpm2-software/tpm2-tools/issues/1123)

---

#### 4. "TPM = PCR 이중 보안" — 사용자 이해의 교정

**사용자의 이해**: "TPM을 쓰면 PCR을 통해 이중 보안한다"

**실제**: PCR 정책은 **자동이 아니라 명시적으로 코딩해야** 하며, 현재 tpm.py는 이를 생략했다.

비유로 설명하면:

```
TPM = 금고
auth password = 금고 비밀번호
PCR 정책 = "특정 시간(시스템 상태)에만 열림" 조건

현재 tpm.py:
  "비밀번호만 맞으면 언제든 열리는 금고"

PCR 추가 시:
  "비밀번호도 맞고, 정상 부팅 상태일 때만 열리는 금고"
```

BitLocker 같은 잘 알려진 구현은 PCR을 기본으로 사용하기 때문에 "TPM = PCR 보안"이라는 인식이 있지만, TPM 자체는 PCR을 강제하지 않는다. 개발자가 선택하는 것이다.

- **확신도**: `[Confirmed]` — [VMware TPM Sealing Policies](https://techdocs.broadcom.com/us/en/vmware-cis/vsphere/vsphere/7-0/vsphere-security-7-0/securing-esxi-hosts/securing-the-esxi-configuration/tpm-sealing-policies-overview.html), [Arch Wiki TPM](https://wiki.archlinux.org/title/Trusted_Platform_Module), [Wikipedia TPM](https://en.wikipedia.org/wiki/Trusted_Platform_Module)

---

#### 5. 그래서 현재 tpm.py가 위험한가?

**결론: "위험"이 아니라 "충분히 강하지 않다"가 정확하다.**

현재 보안 수준 평가:

| 보호 요소 | 상태 | 효과 |
|---|---|---|
| `FIXEDTPM` | ✅ 적용됨 | TPM 칩에 물리 바인딩 — 매우 강력 |
| auth password | ✅ 적용됨 | auth를 모르면 unseal 불가 |
| PCR 정책 | ❌ 미적용 | 부팅 무결성 검증 없음 |

**실질적 위험 수준:**
- auth 값이 환경변수(`TPM_AUTH`)에 저장되므로, auth 자체가 `.env` 파일이나 메모리에 존재
- 공격자가 서버에 접근하여 auth를 탈취하면, PCR이 없으므로 어떤 부팅 상태에서든 unseal 가능
- 하지만 FIXEDTPM이므로 **반드시 해당 물리 서버/VM에서만** unseal 가능

**PCR을 추가하면 얻는 이점:**
- 공격자가 auth를 탈취해도, 정상 부팅 상태가 아니면 unseal 불가
- USB/네트워크 부팅으로 다른 OS를 올려서 시크릿 탈취하는 공격을 차단
- Secure Boot + PCR 조합으로 부팅 체인 전체의 무결성 보장

**PCR을 추가하면 생기는 비용:**
- BIOS 업데이트, 커널 업데이트 시 PCR 값이 변경되어 sealed 데이터 접근 불가 → re-seal 필요
- 운영 복잡도 증가 (업데이트 전 unseal → 업데이트 → re-seal 절차)
- PCR brittleness 문제 (TPM 2.0에서는 signed policy로 완화 가능)

- **확신도**: `[Confirmed]` — 여러 출처 교차 검증 완료

---

#### 6. PCR 정책 추가 시 tpm.py 코드 변경 예시 (참고)

현재 ESAPI 레벨에서 PCR 정책을 추가하려면, 대략 이런 형태가 된다:

```python
# 현재 코드 (auth만 사용)
seal_attrs = (
    TPMA_OBJECT.FIXEDTPM
    | TPMA_OBJECT.FIXEDPARENT
    | TPMA_OBJECT.USERWITHAUTH  # ← 이것 때문에 auth만으로 unseal 가능
)

# PCR 정책 강제 시 (USERWITHAUTH 제거 + policy 추가)
seal_attrs = (
    TPMA_OBJECT.FIXEDTPM
    | TPMA_OBJECT.FIXEDPARENT
    # USERWITHAUTH 제거 → policy session만으로 unseal 가능
)
# + PolicyPCR 세션 생성 코드 추가 필요
```

FAPI (Feature API) 레벨에서는 JSON 정책으로 더 간단하게 구현 가능하다:

```json
{
  "type": "POLICYPCR",
  "pcrs": [
    {"pcr": 0, "hashAlg": "TPM2_ALG_SHA256"},
    {"pcr": 7, "hashAlg": "TPM2_ALG_SHA256"}
  ]
}
```

출처: [tpm2-pytss FAPI 문서](https://tpm2-pytss.readthedocs.io/en/latest/fapi.html), [tpm2-pytss Issue #504](https://github.com/tpm2-software/tpm2-pytss/issues/504)

---

### Edge Cases & Caveats

| 상황 | 영향 |
|---|---|
| PCR 정책 사용 시 커널 업데이트 | PCR 값 변경 → sealed 데이터 접근 불가 → 업데이트 전 unseal 필수 |
| PCR 정책 + Auto Scaling (Cloud) | 각 인스턴스마다 PCR 값 다를 수 있음 → signed policy 필요 |
| PCR 정책 + vMotion (On-Premise VMware) | vMotion 후 PCR 값 유지되지만 KMS 검증 필요 |
| `USERWITHAUTH` 제거 + auth도 제거 | PCR 정책만으로 보호 → PCR 만족하면 누구나 unseal 가능 (auth + PCR 조합 권장) |

---

### Contradictions Found

| 주제 | 모순 | 해결 |
|---|---|---|
| "PCR 없이 TPM은 무의미한가?" | 일부 출처는 PCR 필수로 설명, 다른 출처는 auth만으로도 유효하다고 설명 | **해결됨**: 둘 다 맞음. 사용 목적에 따라 다르다. 디스크 암호화 = PCR 필수, 시크릿 관리 = auth만으로도 FIXEDTPM과 조합 시 유의미한 보안 제공 |

---

### 최종 정리: 현재 tpm.py의 보안을 비유로 설명

```
┌──────────────────────────────────────────────────────┐
│                현재 tpm.py의 보안                      │
│                                                        │
│  [서버 A의 TPM 칩] ← FIXEDTPM: 이 칩에서만 열림       │
│       │                                                │
│       ▼                                                │
│  ┌─────────┐                                          │
│  │ 금고     │ ← auth: 비밀번호를 알아야 열림           │
│  │ (sealed) │                                          │
│  │ data     │ ← PCR: ❌ 없음 → 아무 OS에서나 열림     │
│  └─────────┘                                          │
│                                                        │
│  ✅ 장점: 디스크를 떼어가면 못 열음                     │
│  ✅ 장점: 비밀번호 모르면 못 열음                       │
│  ⚠️  한계: 같은 서버에서 USB로 다른 OS 부팅하면        │
│           비밀번호만 알면 열림                          │
└──────────────────────────────────────────────────────┘
```

```
┌──────────────────────────────────────────────────────┐
│           PCR 정책 추가 시 보안 (이상적)               │
│                                                        │
│  [서버 A의 TPM 칩] ← FIXEDTPM: 이 칩에서만 열림       │
│       │                                                │
│       ▼                                                │
│  ┌─────────┐                                          │
│  │ 금고     │ ← auth: 비밀번호를 알아야 열림           │
│  │ (sealed) │                                          │
│  │ data     │ ← PCR: 정상 부팅일 때만 열림 ✅          │
│  └─────────┘                                          │
│                                                        │
│  ✅ 디스크 분리 → 차단                                 │
│  ✅ 비밀번호 모름 → 차단                               │
│  ✅ USB 부팅 등 비정상 부팅 → 차단                     │
│  ⚠️ 커널/BIOS 업데이트 시 re-seal 필요 (운영 비용)    │
└──────────────────────────────────────────────────────┘
```

---

### 권장 사항

현재 VitalCare 서비스 환경에서는:

1. **당장 위험한 것은 아니다** — FIXEDTPM + auth password 조합은 "시크릿 관리" 용도로는 유의미한 보안 수준
2. **PCR 추가는 "보안 강화" 옵션**이지 필수는 아니다 — 특히 컨테이너/클라우드 환경에서는 PCR 운영 부담이 크다
3. **우선순위**: DB_ENCRYPTION_KEY `"some_secret"` 교체 > GitHub PAT revoke > PCR 정책 추가 순서로 진행하는 것이 합리적

---

### Sources

1. [Microsoft Learn — PCR Banks on TPM 2.0](https://learn.microsoft.com/en-us/windows/security/hardware-security/tpm/switch-pcr-banks-on-tpm-2-0-devices) — 공식 문서
2. [SysTutorials — Understanding TPM 2.0 PCRs](https://www.systutorials.com/understanding-tpm-2-0-and-platform-configuration-registers-pcrs/) — 기술 블로그
3. [Infineon — Sealing and Unsealing Data in TPM](https://community.infineon.com/t5/Blogs/Sealing-and-unsealing-data-in-TPM/ba-p/465547) — 1차 자료 (TPM 제조사)
4. [tpm2-tools Issue #1123 — Unsealing despite PCR policy](https://github.com/tpm2-software/tpm2-tools/issues/1123) — 커뮤니티 (USERWITHAUTH 보안 문제)
5. [tpm2-tools — tpm2_create man page](https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_create.1/) — 공식 문서
6. [tpm2-pytss Issue #504 — FAPI sealed object with PCR policy](https://github.com/tpm2-software/tpm2-pytss/issues/504) — 커뮤니티
7. [tpm2-pytss FAPI Documentation](https://tpm2-pytss.readthedocs.io/en/latest/fapi.html) — 공식 문서
8. [VMware TPM Sealing Policies Overview](https://techdocs.broadcom.com/us/en/vmware-cis/vsphere/vsphere/7-0/vsphere-security-7-0/securing-esxi-hosts/securing-the-esxi-configuration/tpm-sealing-policies-overview.html) — 공식 문서
9. [Arch Wiki — Trusted Platform Module](https://wiki.archlinux.org/title/Trusted_Platform_Module) — 커뮤니티
10. [tpm2-software — Protecting Secrets at TPM Interface](https://tpm2-software.github.io/2021/02/17/Protecting-secrets-at-TPM-interface.html) — 1차 자료
11. [Linux Kernel Trusted Keys Patch](https://patchwork.kernel.org/patch/7839331/) — 1차 자료

### Research Metadata
- 검색 쿼리 수: 7 (일반 6 + SNS 1)
- 수집 출처 수: 11
- 출처 유형 분포: 공식 4, 1차 3, 블로그 1, 커뮤니티 3, SNS 0
- 확신도 분포: Confirmed 5, Likely 0, Uncertain 0, Unverified 0
