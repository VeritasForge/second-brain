---
created: 2026-08-05
source: claude-code
tags: [architecture, terraform, iac, devops, hashicorp, opentofu, cloud]
---

# 📖 Terraform — Concept Deep Dive

> 💡 **한줄 요약**: Terraform은 클라우드/온프레미스 인프라를 선언적 설정 파일(HCL)로 정의·버전관리·재사용할 수 있게 해주는 HashiCorp의 IaC(Infrastructure as Code, 코드로 인프라를 정의·관리하는 방식) 도구다.

---

## 무엇인가? (What is it?)

**Terraform**은 클라우드와 온프레미스 리소스를 사람이 읽을 수 있는 설정 파일로 정의하고, 그 정의를 버전관리·재사용·공유할 수 있게 해주는 IaC 도구다. 컴퓨트·스토리지·네트워크 같은 저수준 컴포넌트부터 DNS 레코드나 SaaS 설정 같은 고수준 컴포넌트까지 다룰 수 있다 ([HashiCorp 공식](https://developer.hashicorp.com/terraform/intro)).

- **탄생 배경**: 2012년 Mitchell Hashimoto가 창업한 HashiCorp가 2014년 7월 Terraform을 출시했다. 이전까지 인프라는 콘솔 클릭이나 스크립트로 수동 관리되거나, AWS CloudFormation·Azure ARM Templates처럼 **단일 클라우드 벤더에 종속된 도구**로만 관리할 수 있었다. Terraform은 하나의 선언적 언어로 여러 클라우드 프로바이더를 동시에 다룰 수 있게 한 것이 핵심 혁신이었다.
- **해결하려는 문제**: 수동 인프라 관리("Manual Chaos")를 선언적 코드 기반 관리로 전환하여, 인프라 변경을 리뷰 가능한 코드 변경으로 만드는 것.

> 📌 **핵심 키워드**: `IaC`, `HCL`, `Provider`, `State`, `Declarative`, `Plan/Apply`

---

## 핵심 개념 (Core Concepts)

```
┌───────────────────────────────────────────────────────────┐
│                  Terraform 핵심 구성 요소                   │
├───────────────────────────────────────────────────────────┤
│                                                           │
│   .tf 파일 (HCL)                                          │
│      │  resource, variable, output 선언                  │
│      ▼                                                   │
│   Module (재사용 단위)                                    │
│      │                                                   │
│      ▼                                                   │
│   Terraform Core  ◄────────►  State (JSON, 현재 상태 기록) │
│      │                              ▲                     │
│      ▼                              │ 저장                │
│   Provider (플러그인)                │                     │
│      │                        Backend (S3, HCP Terraform  │
│      ▼                              등, 원격 저장+잠금)     │
│   Cloud API (AWS/GCP/Azure/...)                          │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

| 구성 요소 | 역할 | 설명 |
|-----------|------|------|
| **HCL** (HashiCorp Configuration Language) | 설정 언어 | Terraform 전용 선언적 DSL(Domain-Specific Language, 특정 목적에 특화된 프로그래밍 언어). JSON으로도 표현 가능 |
| **Provider** | API 연동 플러그인 | AWS·Azure·GCP·GitHub·Datadog 등과 통신. Terraform Registry에 수천 개가 등록되어 있음 |
| **Resource** | 관리 대상 | `aws_instance`, `aws_s3_bucket` 등 실제 인프라 객체 단위 |
| **State** | 현재 상태 기록 | 설정과 실제 인프라의 매핑을 담은 JSON. "환경의 source of truth" 역할을 하며, 실시간 반영이 아니라 **마지막으로 Terraform이 수행한 작업의 기록**이다 |
| **Module** | 재사용 단위 | 리소스 묶음을 패키징하여 여러 곳에서 재사용 |
| **Backend** | State 저장소 | local, S3+DynamoDB, HCP Terraform(舊 Terraform Cloud) 등. 원격 backend는 잠금(locking)을 지원해 동시 수정 충돌을 방지 |

### 🔩 Terraform Core ↔ Provider의 관계

**Terraform Core**는 Go로 정적 컴파일된 `terraform` CLI 바이너리 그 자체다. 특정 클라우드 API에 대한 지식은 전혀 없고, 아래 5가지만 책임진다 ([HashiCorp — How Terraform Works](https://developer.hashicorp.com/terraform/plugin/how-terraform-works)).

| Core의 책임 | 설명 |
|---|---|
| 설정 해석 | `.tf`/module 파싱(interpolation 포함) |
| State 관리 | 현재 상태 기록·비교 |
| Resource Graph 구성 | 리소스 간 의존성 순서 계산 |
| Plan 실행 | 계산된 그래프대로 실제 변경 수행 |
| Plugin과 RPC 통신 | Provider에게 "이 리소스를 만들어라" 지시 전달 |

Provider는 Core에 내장된 코드가 아니라 **별도 프로세스로 실행되는 독립 실행파일**이며, 둘은 **RPC(Remote Procedure Call, 원격 프로시저 호출 — 한 프로세스가 다른 프로세스의 함수를 마치 로컬 함수처럼 호출하는 통신 방식)**로 통신한다.

```
terraform (Core) ── RPC 호출("aws_instance 생성") ──▶ Provider 플러그인 (별도 프로세스)
                                                                │
                                                                ▼
                                                          실제 클라우드 API 호출
```

이 분리 구조 덕분에 Core를 건드리지 않고도 Provider만 새로 만들면 새로운 서비스를 지원할 수 있다 — Terraform Registry에 수천 개의 Provider가 존재할 수 있는 이유다.

---

## 3️⃣ 아키텍처와 동작 원리 (Architecture & How it Works)

Terraform CLI는 클라이언트 역할을 하며, `plan`·`apply`·`destroy` 명령으로 인프라 생명주기를 관리한다 ([Spacelift](https://spacelift.io/blog/terraform-architecture)).

### 🔄 동작 흐름 (Step by Step)

1. **`terraform init`**: `.tf` 파일에서 선언된 Provider 플러그인을 다운로드하고, Backend(state 저장소)를 초기화한다.
   > ⚠️ **흔한 오해**: `git init`처럼 코드 skeleton(뼈대)을 생성해주는 명령이 **아니다**. 공식 문서 원문: *"terraform init assumes that the working directory already contains a configuration and will attempt to initialize that configuration."* — `.tf` 파일이 이미 존재한다고 전제하고 그 파일이 요구하는 의존성(Provider·Module)만 채워 넣을 뿐, 코드 자체를 만들어주지는 않는다. 실제로 뼈대 코드를 생성해주는 도구가 필요하다면 AWS CDK의 `cdk init`이나 CDK for Terraform의 `cdktf init`이 이에 해당한다 ([HashiCorp — terraform init 공식 문서](https://developer.hashicorp.com/terraform/cli/commands/init)).
2. **`terraform plan`**: 설정 파일을 파싱하고 현재 state와 비교하여, 목표 상태에 도달하기 위해 필요한 변경사항을 담은 **실행 계획**을 생성한다. 이 단계는 실제 인프라를 변경하지 않는다.
3. **`terraform apply`**: `plan`과 동일한 비교를 다시 수행한 뒤, 승인된 변경사항을 Provider의 API를 통해 의존성 순서대로 실제로 적용하고 state를 갱신한다 ([Educative](https://www.educative.io/answers/terraform-plan-vs-terraform-apply)).
4. **`terraform destroy`**: 역순으로 리소스를 제거한다.

```
.tf (HCL 설정)
   │  terraform init
   ▼
Terraform Core + Provider 플러그인
   │  terraform plan  (state와 비교 → diff만 표시, 변경 없음)
   ▼
실행 계획(Execution Plan)
   │  terraform apply (사용자 승인 후 실행)
   ▼
Provider API 호출 ──► 실제 클라우드 인프라
   │
   ▼
State 갱신 (원격 backend에 저장 + 잠금 해제)
```

State는 로컬에도 저장할 수 있지만, 협업 환경에서는 S3·HCP Terraform 같은 원격 backend에 저장하고 잠금 기능을 함께 사용하는 것이 표준이다.

---

## 4️⃣ 유즈 케이스 & 베스트 프랙티스 (Use Cases & Best Practices)

### 🎯 대표 유즈 케이스

| # | 유즈 케이스 | 설명 | 적합한 이유 |
|---|------------|------|------------|
| 1 | 멀티클라우드 인프라 프로비저닝 | AWS·GCP·Azure를 하나의 워크플로우로 관리 | 프로바이더별 API를 추상화한 통일된 HCL 문법 |
| 2 | CI/CD 파이프라인 내 인프라 자동 배포 | GitHub Actions에서 OIDC(OpenID Connect) Federation으로 임시 자격증명을 발급받아 `terraform apply` 실행 | 장기 Access Key 없이 안전하게 배포 자동화 |
| 3 | 팀 협업을 위한 모듈화된 인프라 코드 | Terraform Registry의 공개 모듈(`terraform-aws-modules/iam` 등) 재사용 | 검증된 모듈로 반복 구현 비용 절감 |

### ✅ 베스트 프랙티스

1. **원격 Backend + 잠금 필수 사용**: state를 S3+DynamoDB, HCP Terraform 등에 저장하고 locking을 활성화해 동시 수정 충돌을 방지한다.
2. **State를 서비스/환경 단위로 분리**: 하나의 거대한 state에 전체 인프라를 몰아넣지 않는다 (섹션 7 참고).
3. **`plan` 리뷰 후 `apply`**: 자동 승인 없이 실행 계획을 사람이 검토하는 프로세스를 둔다.
4. **모듈화 + 변수/출력 활용**: 재사용성과 가독성을 높인다.
5. **콘솔 수동 변경 금지**: 드리프트(drift, 실제 인프라와 state 간 불일치) 발생 시 `terraform import`나 코드 반영으로 동기화한다.

### 🏢 실제 적용 사례

- **GitLab**: 2024년 OpenTofu(후술)를 공개적으로 지지하며 자사 파이프라인에 도입 ([platformengineering.org](https://platformengineering.org/blog/terraform-vs-opentofu-iac-tool)).
- **Gruntwork, Spacelift, Env0, Scalr**: OpenTofu 포크를 공동 주도한 기업들로, 자사 IaC 플랫폼에서 Terraform 대체재로 지원.

---

## 5️⃣ 장점과 단점 (Pros & Cons)

| 구분 | 항목 | 설명 |
|------|------|------|
| ✅ 장점 | 최대 규모의 생태계 | 수천 개의 Provider와 가장 큰 module registry 보유 |
| ✅ 장점 | 멀티클라우드 표준화 | 벤더 종속 없이 하나의 워크플로우로 여러 클라우드를 관리 |
| ✅ 장점 | 변경 사전 검토 | `plan`으로 실제 적용 전 변경사항을 미리 확인 가능 |
| ❌ 단점 | HCL의 표현력 한계 | DSL이라 반복문·조건문 등 범용 프로그래밍 언어 기능이 Pulumi 대비 제한적 |
| ❌ 단점 | State 관리 복잡성 | 파일 유실·동시 수정 충돌·민감정보 평문 노출 등의 운영 리스크 |
| ❌ 단점 | 라이선스 불확실성 | 2023년 BSL(Business Source License) 전환 이후 상업적 사용 제약과 생태계 신뢰 문제가 지속되고 있음 (섹션 6 참고) |

### ⚖️ Trade-off 분석

```
선언적 단순함(HCL)   ◄──────── Trade-off ────────►   프로그래밍 유연성(Pulumi)
멀티클라우드 표준화   ◄──────── Trade-off ────────►   벤더 특화 최적화(AWS CDK가 AWS 단일 배포 속도 우위)
```

---

## 6️⃣ 차이점 비교 (Comparison)

### 📊 비교 매트릭스

| 비교 기준 | Terraform | OpenTofu | Pulumi | AWS CDK |
|-----------|-----------|----------|--------|---------|
| 핵심 목적 | 멀티클라우드 선언적 IaC | Terraform의 오픈소스 포크 | 범용 프로그래밍 언어 기반 IaC | AWS 전용, 프로그래밍 언어 → CloudFormation 변환 |
| 언어 | HCL (DSL) | HCL (Terraform과 동일) | TypeScript/Python/Go/C# 등 | TypeScript/Python/Java/C#/Go |
| 라이선스 | BSL (2023.8~, 4년 후 개별 릴리즈가 MPL로 전환) | MPL 2.0 (완전 오픈소스) | Apache 2.0 | Apache 2.0 |
| 거버넌스 | HashiCorp (2025.2 IBM 인수 완료) | Linux Foundation | Pulumi Corp | AWS |
| 적합한 경우 | 광범위한 생태계·자료가 필요하고 BSL 제약이 문제되지 않을 때 | 라이선스 리스크를 피하고 완전 오픈소스를 유지하고 싶을 때 | 팀이 프로그래밍 언어로 인프라를 작성·테스트하고 싶을 때 | AWS 단일 클라우드에 장기 커밋하며 앱·인프라 코드를 한 언어로 통합하고 싶을 때 |

### 🔍 Terraform ↔ OpenTofu 분기 상세

```
2023-08  HashiCorp, 라이선스 MPL v2.0 → BSL 변경 발표
           │  (자사 상용 제품과 "경쟁적으로" 사용하는 것을 금지하는 조항 포함,
           │   BSL은 개별 릴리즈마다 4년 후 자동으로 MPL로 전환)
           ▼
2023-08  커뮤니티(Gruntwork·Spacelift·Harness·Env0·Scalr 등) 반발
           │  "OpenTF" 결성 → Open Terraform Manifesto 발표
           │  (1개월 내 GitHub 33,000+ stars, 140개 기업·700명 개인 서약)
           ▼
2023-09  상표권 문제로 "OpenTofu"로 개명, Linux Foundation 산하 편입
           │  (Terraform 1.6.x — 마지막 MPL 버전 — 기반으로 포크, CLI 호환성 유지)
           ▼
2024-04  HashiCorp, OpenTofu에 cease-and-desist 통보
           │  (BSL 코드 무단 사용 주장 ↔ OpenTofu는 이전 MPL 버전에서 유래했다고 반박)
           │  → 분쟁은 공개적으로 해결되지 않은 채 지속
           ▼
2025-02-27  IBM, HashiCorp를 $6.4B(주당 $35)에 인수 완료
```

- 위 타임라인은 [Wikipedia — OpenTofu](https://en.wikipedia.org/wiki/OpenTofu), [Spacelift](https://spacelift.io/blog/terraform-license-change), [TechCrunch](https://techcrunch.com/2025/02/27/ibm-closes-6-4b-hashicorp-acquisition/) 등 복수 독립 출처로 교차 확인했다.
- ⚠️ 다만 "IBM 인수 이후 38%의 Terraform 사용자가 대안을 검토/이전 중"이라거나 "OpenTofu가 연 300% 성장, 약 1000만 다운로드"라는 수치는 업계 블로그([yaw.sh](https://yaw.sh/blog/ibm-bought-hashicorp-terraform-users-want-out/), [softwareseni.com](https://www.softwareseni.com/hashicorp-terraform-opentofu-and-the-ibm-acquisition-wild-card-for-infrastructure-as-code/))에서만 발견되며, 조사한 원문 어디에도 설문 방법론·표본 크기·발행 기관이 명시되어 있지 않다. **출처가 불분명한 미검증 수치이므로 의사결정 근거로 사용하지 말 것.**

### 🤔 언제 무엇을 선택?

- **Terraform을 선택하세요** → 이미 광범위한 provider/module 생태계와 커뮤니티 자료가 필요하고, 상업적 재판매·경쟁 서비스가 아니라면 BSL 제약이 실질적 문제가 되지 않는 경우
- **OpenTofu를 선택하세요** → 라이선스 불확실성 자체를 리스크로 보고 완전한 오픈소스를 유지하고 싶은 경우 (Terraform 1.6까지의 문법과 대부분 호환)
- **Pulumi를 선택하세요** → 팀이 이미 익숙한 프로그래밍 언어로 인프라 코드를 작성하고 유닛 테스트를 붙이고 싶은 경우
- **AWS CDK를 선택하세요** → AWS 단일 클라우드에 장기적으로 커밋하며, 애플리케이션 코드와 인프라 코드를 같은 언어·레포에서 관리하고 싶은 경우

---

## 7️⃣ 사용 시 주의점 (Pitfalls & Cautions)

### ⚠️ 흔한 실수 (Common Mistakes)

| # | 실수 | 왜 문제인가 | 올바른 접근 |
|---|------|-----------|------------|
| 1 | State를 로컬 개발자 머신에 저장 | 유실·유출·덮어쓰기 위험 | 원격 backend(S3+DynamoDB, HCP Terraform 등)로 전환 |
| 2 | State 잠금(locking) 미적용 | 동시 `apply` 시 state 손상 가능 | 원격 backend의 locking 기능 활성화 |
| 3 | 콘솔에서 수동 변경("Click-Ops") | state와 실제 인프라 간 드리프트 발생 | `terraform import` 또는 코드 반영으로 동기화, 수동 변경 자체를 지양 |
| 4 | 모놀리식 단일 state에 전체 인프라 몰아넣기 | blast radius 확대, `plan`/`apply` 성능 저하 | 서비스·환경 단위로 state 분리, 모듈화 |
| 5 | 민감정보(비밀번호·키)를 state에 평문 저장 | state 유출 시 그대로 노출 | Vault·Secrets Manager와 연동, `sensitive` 속성 사용 |

가장 흔히 지적되는 "at-scale 안티패턴"은 **하나의 거대한 state 파일**이다. 여러 서비스의 리소스를 모듈 분리 없이 한 설정에 몰아넣으면 state가 비대해져 관리·장애 대응이 어려워진다 ([atmosly.com](https://atmosly.com/knowledge/terraform-and-aws-at-scale-patterns-for-teams-managing-100-resources)).

### 🔒 보안/성능 고려사항

- CI 파이프라인에서는 장기 Access Key 대신 OIDC Federation으로 임시 자격증명을 발급받아 사용한다.
- State 파일에 대한 접근 권한(IAM)을 최소 권한 원칙으로 엄격히 제한한다.

---

## 8️⃣ 개발자가 알아둬야 할 것들 (Developer's Toolkit)

### 📚 학습 리소스

| 유형 | 이름 | 링크/설명 |
|------|------|----------|
| 📖 공식 문서 | HashiCorp Developer | [developer.hashicorp.com/terraform](https://developer.hashicorp.com/terraform) |
| 📖 공식 문서 | Terraform Registry | [registry.terraform.io](https://registry.terraform.io) — Provider/Module 검색 |

### 🛠️ 관련 도구 & 생태계

| 도구 | 용도 |
|------|------|
| **OpenTofu** | Terraform 1.6.x 기반 완전 오픈소스(MPL 2.0) 포크, CLI 호환 |
| **terraform-aws-modules/iam** | AWS IAM 관리용 커뮤니티 모듈 ([Terraform Registry](https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest)) |

### 🔮 트렌드 & 전망

- **IBM 인수 (Confirmed)**: 2025년 2월 27일 IBM이 HashiCorp를 $6.4B(주당 $35)에 인수 완료했다. Terraform과 Vault는 IBM의 자동화 소프트웨어 포트폴리오에 편입되었으며, Ansible(설정관리)과의 통합이 방향성으로 제시되고 있다 ([TechCrunch](https://techcrunch.com/2025/02/27/ibm-closes-6-4b-hashicorp-acquisition/), [SiliconANGLE](https://siliconangle.com/2025/02/27/ibm-completes-6-4b-hashicorp-acquisition-following-regulatory-approvals/)).
- **최신 버전 (Confirmed, GitHub 공식 릴리즈 페이지 직접 확인 — 2026-08-05 기준)**: 안정 버전은 **v1.15.8** (2026-07-08 릴리즈)이며, v1.16.0이 베타(v1.16.0-beta1, 2026-07-23) 단계로 개발 중이다.
- **OpenTofu 성장세**: GitLab의 공개 지지, Spacelift·Scalr 등의 지속 지원으로 채택이 늘고 있다는 정성적 신호는 여러 출처에서 일관되게 나타난다. 다만 구체적 성장률·다운로드 수치는 출처가 불분명해 신뢰하지 말 것 (섹션 6 참고).

### 💬 커뮤니티 인사이트

Reddit 직접 검색은 검색엔진이 dev.to 등 블로그 결과를 우선 반환해 성공하지 못했다. 대신 다수의 실무자 블로그(dev.to)에서 "Terraform은 여전히 생태계 규모로 우위를 유지할 것"이라는 의견과 "라이선스 불확실성 때문에 OpenTofu 전환을 검토한다"는 의견이 공존하는 것으로 나타난다. 이는 개별 커뮤니티 게시물을 직접 확인한 결과가 아니라 블로그의 요약에 근거한 것이므로 참고용으로만 사용할 것.

---

## 📎 Sources

1. [What is Terraform — HashiCorp Developer](https://developer.hashicorp.com/terraform/intro) — 공식 문서 (직접 원문 확인)
2. [Terraform Architecture Overview — Spacelift](https://spacelift.io/blog/terraform-architecture) — 기술 블로그
3. [Terraform plan vs apply — Educative](https://www.educative.io/answers/terraform-plan-vs-terraform-apply) — 기술 블로그
4. [OpenTofu — Wikipedia](https://en.wikipedia.org/wiki/OpenTofu) — 백과사전 (직접 원문 확인)
5. [Terraform License Change (BSL) — Spacelift](https://spacelift.io/blog/terraform-license-change) — 기술 블로그
6. [Terraform vs OpenTofu — platformengineering.org](https://platformengineering.org/blog/terraform-vs-opentofu-iac-tool) — 기술 블로그
7. [IBM closes $6.4B HashiCorp acquisition — TechCrunch](https://techcrunch.com/2025/02/27/ibm-closes-6-4b-hashicorp-acquisition/) — 뉴스
8. [IBM completes $6.4B HashiCorp acquisition — SiliconANGLE](https://siliconangle.com/2025/02/27/ibm-completes-6-4b-hashicorp-acquisition-following-regulatory-approvals/) — 뉴스
9. [IBM Closes HashiCorp Acquisition — GovConWire](https://www.govconwire.com/articles/ibm-closes-hashicorp-acquisition) — 뉴스
10. [IBM Bought HashiCorp and 38% of Terraform Users Want Out — yaw.sh](https://yaw.sh/blog/ibm-bought-hashicorp-terraform-users-want-out/) — 블로그 (수치 출처 불분명, 미검증으로 표시)
11. [HashiCorp Terraform, OpenTofu and the IBM Acquisition Wild Card — softwareseni.com](https://www.softwareseni.com/hashicorp-terraform-opentofu-and-the-ibm-acquisition-wild-card-for-infrastructure-as-code/) — 블로그 (수치 출처 불분명, 미검증으로 표시)
12. [Terraform and AWS at Scale — atmosly.com](https://atmosly.com/knowledge/terraform-and-aws-at-scale-patterns-for-teams-managing-100-resources) — 기술 블로그
13. [Terraform Releases — GitHub hashicorp/terraform](https://github.com/hashicorp/terraform/releases) — 공식 릴리즈 페이지 (직접 원문 확인)
14. [Terraform Enterprise Releases — HashiCorp Developer](https://developer.hashicorp.com/terraform/enterprise/releases) — 공식 문서
15. [How Terraform Works — HashiCorp Developer](https://developer.hashicorp.com/terraform/plugin/how-terraform-works) — 공식 문서 (직접 원문 확인, Terraform Core의 5대 책임과 Provider RPC 통신 근거)
16. [terraform init — HashiCorp Developer](https://developer.hashicorp.com/terraform/cli/commands/init) — 공식 문서 (직접 원문 확인, "이미 설정이 존재한다고 가정" 근거)

---

> 🔬 **Research Metadata**
> - 검색 쿼리 수: 8 (일반 7 + SNS 1)
> - 수집 출처 수: 16
> - 출처 유형: 공식 6(HashiCorp 공식문서·GitHub 릴리즈), 백과사전 1, 뉴스 3, 기술 블로그 6
> - SNS 출처: Reddit 검색 시도했으나 직접 접근 실패 (검색엔진이 dev.to 블로그로 대체 반환) — 한계로 명시
> - 주요 정정 사항: WebSearch AI 요약이 제시한 "Terraform 최신 버전 1.15.2/1.15.4(2026-05)"를 GitHub 공식 릴리즈 페이지 직접 확인으로 "v1.15.8(2026-07-08)"로 정정. "IBM 인수 후 38% 이탈 의향", "OpenTofu 연 300% 성장/1000만 다운로드" 수치는 원문 재확인 결과 출처·방법론 불명으로 판단해 미검증 표시로 하향
> - 후속 보강(같은 세션 Q&A 기반): 섹션 2에 Terraform Core의 5대 책임과 Provider와의 RPC 통신 구조 추가, 섹션 3의 `terraform init` 설명에 "`git init`과 달리 skeleton을 생성하지 않는다"는 흔한 오해 정정 추가
