---
tags: [aws, vpc, networking, ecs, lambda]
created: 2026-08-07
---

# 📖 AWS VPC 네트워킹 아키텍처 — Public/Private Subnet부터 메시징 브로커 패턴까지

> 💡 **한줄 요약**: VPC(Virtual Private Cloud, 가상 사설 클라우드) 안에서 인터넷과의 관계는 "누가 먼저 연결을 시작하는가"로 결정되며, ECS(Elastic Container Service) Hello World API, VPC 연결 방식(Peering/Transit Gateway), Lambda VPC 모드, SNS(Simple Notification Service) 메시징까지 — 이 대화에서 다룬 모든 사례가 결국 **"Public Subnet의 진입점을 거치지 않으면 아무것도 Private Subnet 안으로 들어올 수 없다"**는 하나의 원칙으로 귀결된다.

---

## 1. VPC 기초 — Public Subnet과 Private Subnet

### 1.1 정의

- **VPC**: AWS 클라우드 안에 논리적으로 격리된 나만의 가상 네트워크. IP 대역(CIDR, Classless Inter-Domain Routing), 서브넷, 라우팅, 게이트웨이를 직접 설계할 수 있습니다.
- **Public Subnet**: 라우팅 테이블에 `0.0.0.0/0 → IGW(Internet Gateway, 인터넷 게이트웨이)` 라우트가 있는 서브넷. 여기 배치된 리소스는 (Public IP가 있다면) 인터넷과 직접 양방향 통신이 가능합니다.
- **Private Subnet**: IGW로 가는 직접 라우트가 없는 서브넷. 인터넷에서 먼저 접속을 시작할 수 없고, 내부에서 나가는 아웃바운드는 NAT Gateway(Network Address Translation Gateway, 네트워크 주소 변환 게이트웨이)를 거쳐야 합니다.

AWS 공식 설명: *"공개 서브넷에는 웹 서버를, 비공개 서브넷에는 DB 서버를 두는 멀티티어(multi-tier) 구성을 추천한다"* [[AWS Networking Essentials]](https://aws.amazon.com/getting-started/aws-networking-essentials/) — 인터넷에 노출될 필요가 없는 리소스를 물리적으로 격리하는 것이 핵심입니다.

> 📌 **핵심 키워드**: `VPC`, `Public Subnet`, `Private Subnet`, `IGW`, `NAT Gateway`

### 1.2 핵심 구성 요소

| 구성 요소 | 역할 | 설명 |
| --- | --- | --- |
| **IGW** (Internet Gateway) | Public Subnet의 인터넷 관문 | AWS가 관리하는 수평 확장형 게이트웨이. VPC ↔ 인터넷 양방향 통신 허용 |
| **NAT Gateway** | Private Subnet의 아웃바운드 전용 통로 | Private → 인터넷 방향 요청만 허용, 인터넷이 먼저 연결을 시작할 수 없음 |
| **Route Table** | 서브넷 트래픽 방향 결정 | Public: `0.0.0.0/0 → igw-xxx` / Private: `0.0.0.0/0 → nat-xxx` |
| **Security Group (SG)** | 인스턴스·ENI(Elastic Network Interface, 가상 네트워크 인터페이스) 단위 방화벽 | Stateful(상태 추적), 허용 규칙만 정의(default deny) |
| **NACL** (Network ACL) | 서브넷 단위 방화벽 | Stateless — 인바운드/아웃바운드 규칙을 각각 명시해야 함 |
| **AZ** (Availability Zone, 가용 영역) | 물리적으로 분리된 데이터센터 묶음 | 서브넷은 하나의 AZ에 귀속. 고가용성을 위해 최소 2개 AZ 사용 권장 |

- Public/Private을 가르는 것은 물리적 위치가 아니라 **라우팅 테이블에 IGW 라우트가 있는지 여부** 하나뿐입니다.
- Private Subnet은 **inbound(들어오는 연결)만 막히고, outbound(나가는 연결)는 NAT Gateway나 VPC Endpoint를 통해 자유롭게 허용**됩니다 — 이 구분이 이 문서 전체를 관통하는 핵심 원칙입니다.

---

## 2. ECS(Elastic Container Service) 기반 Hello World API 아키텍처

### 2.1 전체 아키텍처

```
                          🌐 Internet
                              │
                    ┌─────────▼─────────┐
                    │  Internet Gateway   │
                    └─────────┬─────────┘
   ┌──────────────────────────┼──────────────────────────┐
   │                    VPC (10.0.0.0/16)                  │
   │  ── AZ-a ──────────────┐   ┌────────── AZ-b ──────    │
   │  Public Subnet          │   │  Public Subnet          │
   │  ┌────┐    ┌─────────┐  │   │  ┌────┐   ┌─────────┐   │
   │  │ ALB │    │ NAT GW  │  │   │  │ ALB │   │ NAT GW  │   │
   │  └──┬─┘    └────┬────┘  │   │  └──┬─┘   └────┬────┘   │
   │─────┼───────────┼───────┤   │─────┼──────────┼────────│
   │  Private Subnet  │        │   │  Private Subnet │        │
   │  ┌──▼─────────┐  │        │   │  ┌──▼─────────┐  │        │
   │  │ ECS Fargate│◄─┘(egress)│   │  │ ECS Fargate│◄─┘        │
   │  │ Task:8080  │           │   │  │ Task:8080  │           │
   │  │"Hello World"│          │   │  │"Hello World"│          │
   │  └────────────┘           │   │  └────────────┘           │
   └────────────────────────────────────────────────────────────┘
              │ (VPC Endpoint 권장 — NAT 비용 절감, 4장에서 상세 설명)
       ┌──────▼──────────┐
       │ ECR / CloudWatch │
       │ Logs / Secrets   │
       └──────────────────┘
```

핵심은 **ECS 태스크(컨테이너)를 Private Subnet에 두고, 인터넷에 노출되는 것은 ALB(Application Load Balancer)뿐**이라는 점입니다. AWS 공식 블로그도 이 패턴을 표준으로 설명합니다: *"ALB는 Public Subnet에, Fargate 태스크는 Private Subnet에 두어 컨테이너를 인터넷으로부터 안전하게 격리한다."* [[Task Networking in AWS Fargate]](https://aws.amazon.com/blogs/compute/task-networking-in-aws-fargate/)

### 2.2 동작 흐름

1. **클라이언트 요청**: 클라이언트가 ALB의 DNS(Domain Name System) 이름으로 HTTPS 요청을 보냄
2. **ALB 수신**: ALB는 **Public Subnet**(두 AZ에 걸쳐 배치)에서 요청을 받고 TLS(Transport Layer Security) 종료
3. **Target Group 전달**: ALB가 Target Group을 통해 **Private Subnet**의 ECS Fargate 태스크로 트래픽 전달
4. **컨테이너 처리**: 컨테이너가 요청을 처리하고 `{"message": "Hello World"}` 같은 응답 반환
5. **아웃바운드가 필요할 때**: 태스크가 이미지를 ECR(Elastic Container Registry)에서 받거나 로그를 CloudWatch로 보낼 때는 NAT Gateway(또는 VPC Endpoint) 경유
6. **응답 반환**: ALB를 거쳐 클라이언트로 응답 전달

**최소 권한 Security Group 체인**:
```
Internet(0.0.0.0/0) --443--> ALB SG --8080--> ECS Task SG
```

### 2.3 유즈 케이스 & 베스트 프랙티스

| # | 유즈 케이스 | 설명 | 적합한 이유 |
| --- | --- | --- | --- |
| 1 | 멀티티어 웹 서비스 | ALB(Public) + API 서버(Private) + DB(Private/Isolated) | 계층별 격리로 공격 표면 최소화 |
| 2 | 서버리스 컨테이너 API | ECS Fargate로 서버 관리 없이 Hello World API 운영 | Fargate는 EC2 인스턴스 관리가 필요 없는 서버리스 컨테이너 실행 환경 |
| 3 | 내부 마이크로서비스 통신 | Internal ALB를 Private Subnet에 두고 서비스 간 통신 | 인터넷 노출 없이 서비스-투-서비스 연결 |

**베스트 프랙티스**:
1. **컨테이너는 항상 Private Subnet**: 인터넷에 직접 노출되는 리소스는 ALB/NAT Gateway로 최소화
2. **AZ 최소 2개 이상 이중화**: NAT Gateway·ALB를 AZ마다 하나씩 두어 하나의 AZ 장애가 전체 서비스를 멈추지 않게 함
3. **VPC Endpoint로 NAT 비용 절감**: ECR, S3, CloudWatch Logs, Secrets Manager 등 AWS 서비스 트래픽은 NAT Gateway 대신 Interface/Gateway VPC Endpoint로 우회 가능 → *(단, 무조건 대체되는 건 아님 — 4장에서 정확한 조건을 다룬다)*
4. **Security Group은 항상 "출처 SG" 참조**: IP 대역보다 다른 SG를 소스로 지정하면 인스턴스가 바뀌어도 규칙을 안 고쳐도 됨

AWS 공식 CDK(Cloud Development Kit) 샘플들이 "Public Subnet(ALB) + Private Subnet(Fargate)" 패턴을 기본 템플릿으로 제공 — 스타트업/엔터프라이즈 모두의 표준 웹 API 아키텍처입니다.

### 2.4 장점과 단점

| 구분 | 항목 | 설명 |
| --- | --- | --- |
| ✅ 장점 | 보안 강화 | Private Subnet의 컨테이너는 인터넷에서 직접 접근 불가 |
| ✅ 장점 | 계층적 방어 | ALB → SG → NACL 다중 방어선 구성 가능 |
| ❌ 단점 | 추가 비용 | NAT Gateway는 시간당 요금 + 처리 GB당 요금 발생 |
| ❌ 단점 | 디버깅 난이도 | Private 리소스는 직접 접속이 안 되어 Bastion Host나 SSM(Systems Manager) Session Manager 필요 |

### 2.5 Public Subnet vs Private Subnet 비교

| 비교 기준 | Public Subnet | Private Subnet |
| --- | --- | --- |
| 인터넷 인바운드 | 가능 (IGW 라우트 있음) | 불가능 |
| 인터넷 아웃바운드 | 직접 가능 | NAT GW 경유만 가능 |
| 대표 리소스 | ALB, NAT GW, Bastion Host | ECS Task, RDS(Relational Database Service), Lambda(VPC 모드 — 5장 참고) |
| 보안 노출 | 높음 | 낮음 |

**언제 무엇을 선택?**
- **Public Subnet** → ALB, NAT Gateway처럼 인터넷과 직접 통신해야 하는 "관문" 리소스
- **Private Subnet** → 애플리케이션 서버, DB처럼 인터넷에서 직접 접근할 이유가 없는 "업무 로직" 리소스

### 2.6 사용 시 주의점

| # | 실수 | 왜 문제인가 | 올바른 접근 |
| --- | --- | --- | --- |
| 1 | NAT Gateway를 AZ 1개에만 배치 | 그 AZ 장애 시 다른 AZ의 Private 리소스도 아웃바운드 불가 (SPOF, Single Point of Failure) | AZ마다 NAT Gateway 하나씩 배치 |
| 2 | ECS Task를 Public Subnet에 두고 Public IP 자동 할당 | 컨테이너가 불필요하게 인터넷에 직접 노출됨 | Task는 Private Subnet + ALB 뒤에 배치 |
| 3 | NACL을 SG처럼 한쪽만 설정 | NACL은 stateless라 인바운드·아웃바운드를 각각 명시해야 응답 트래픽이 통과함 | 인바운드/아웃바운드 규칙 모두 작성 |

### 2.7 개발자가 알아둬야 할 것들

| 유형 | 이름 | 설명 |
| --- | --- | --- |
| 📖 공식 문서 | AWS Networking Essentials | Public/Private Subnet 표준 시나리오 설명 |
| 📖 공식 문서 | ECS Developer Guide – Task Networking in Fargate | ALB+Fargate 아키텍처의 공식 설계 근거 |
| 🛠️ 도구 | AWS CDK `ecs_patterns.ApplicationLoadBalancedFargateService` | 이 아키텍처 전체를 몇 줄의 코드로 생성 |

---

## 3. VPC 연결 방식 — VPC Peering과 Transit Gateway(TGW)

### 3.1 정의

- **VPC Peering (2014년 출시)**: 두 VPC 사이의 네트워킹 연결로, 서로 같은 네트워크에 있는 것처럼 프라이빗 IP로 통신할 수 있게 해줍니다. 같은 계정/다른 계정, 같은 리전/다른 리전(inter-region) 모두 지원됩니다. [[AWS Whitepaper: VPC peering]](https://docs.aws.amazon.com/whitepapers/latest/aws-vpc-connectivity-options/vpc-peering.html)
- **Transit Gateway (TGW, 2018년 출시)**: 여러 VPC와 온프레미스 네트워크(VPN, Direct Connect)를 연결하는 리전 단위 관리형 라우팅 허브. "클라우드 라우터" 역할을 합니다.

> 📌 **핵심 키워드**: `VPC Peering`, `Transit Gateway(TGW)`, `Transitive Routing(전이적 라우팅)`, `Hub-and-Spoke`

### 3.2 핵심 개념

| 구성 요소 | 역할 | 설명 |
| --- | --- | --- |
| Peering Connection | VPC 간 1:1 연결 객체 | 각 VPC의 라우팅 테이블에 서로를 가리키는 라우트 추가 필요 |
| **Non-transitive routing** (비전이적 라우팅) | Peering의 핵심 제약 | A↔B, A↔C가 연결돼 있어도 B↔C는 자동으로 통신 안 됨 |
| TGW Attachment | VPC/VPN/Direct Connect를 TGW에 연결하는 지점 | 각 연결이 하나의 attachment |
| TGW Route Table | TGW 내부 라우팅 규칙 | attachment 간 전이적 라우팅과 라우팅 도메인 분리 지원 |

### 3.3 아키텍처

**VPC Peering — Full Mesh (완전 연결망)**
```
   VPC-A ─────── VPC-B
     │  ╲       ╱  │
     │   ╲     ╱   │
     │    ╲   ╱    │
     │    ╱   ╲    │
     │   ╱     ╲   │
     │  ╱       ╲  │
   VPC-D ─────── VPC-C
```
VPC 4개를 모두 서로 통신시키려면 **6개의 Peering Connection**이 필요합니다 (`n(n-1)/2 = 4×3/2 = 6`). VPC가 100개면 **4,950개**가 필요합니다. [[AWS Whitepaper]](https://docs.aws.amazon.com/whitepapers/latest/building-scalable-secure-multi-vpc-network-infrastructure/vpc-peering.html)

**Transit Gateway — Hub-and-Spoke (허브-스포크)**
```
        VPC-A          VPC-B
           \             /
            \           /
          ┌───────────────┐
          │ Transit Gateway│──── 온프레미스 (VPN / Direct Connect)
          └───────────────┘
            /           \
           /             \
        VPC-C          VPC-D
```
VPC가 몇 개든 **TGW에 1개씩만 연결(attachment)**하면 되고, TGW 라우트 테이블이 나머지 전달을 처리합니다.

### 3.4 유즈 케이스 & 베스트 프랙티스

| # | 유즈 케이스 | 설명 | 적합한 이유 |
| --- | --- | --- | --- |
| 1 | 소수 VPC 간 고성능 연결 (Peering) | VPC 2~3개 사이의 대용량/저지연 트래픽 | 중간 허브 없이 직접 연결이라 지연·비용 최소 |
| 2 | 대규모 멀티 VPC 조직 (TGW) | 수십~수천 개 VPC, 여러 계정을 아우르는 네트워크 | 허브 하나로 관리 단순화, 최대 5,000 VPC attachment 지원 |
| 3 | 온프레미스 하이브리드 연결 (TGW) | Direct Connect/VPN을 여러 VPC와 동시 공유 | VPC마다 별도 연결 없이 TGW 하나로 공유 |
| 4 | 중앙 공유 서비스 VPC 접근 | 여러 VPC가 공통 서비스(로깅, 보안 검사) VPC에 접근 | Peering과 TGW를 **함께** 쓰는 것도 AWS가 권장하는 패턴 |

### 3.5 장단점 및 비교 매트릭스

| 비교 기준 | VPC Peering | Transit Gateway |
| --- | --- | --- |
| 연결 방식 | 1:1 point-to-point | 중앙 허브(hub-and-spoke) |
| 전이적 라우팅 | ❌ 미지원 (직접 연결만 통신 가능) | ✅ 지원 |
| 확장성 | VPC 많아지면 관리 복잡 (n(n-1)/2) | VPC 최대 5,000개까지 단일 TGW로 관리 |
| 온프레미스 연결 | VPC마다 개별 VPN/Direct Connect 필요 | TGW 하나로 여러 VPC가 공유 |
| 비용 | 대체로 무료(같은 AZ 내) | attachment당 시간 요금 + GB당 처리 요금 |

```
단순함/무료(Peering)   ◄──────── Trade-off ────────►   확장성/중앙관리(TGW)
```

### 3.6 왜 "VPC 10개 미만"에서만 Peering을 권장하는가 (심화)

AWS 공식 백서: *"VPC peering은 연결할 VPC 개수가 10개 미만일 때(개별 연결을 하나하나 관리할 수 있는 수준일 때) 가장 적합하다."* [[AWS Whitepaper]](https://docs.aws.amazon.com/whitepapers/latest/building-scalable-secure-multi-vpc-network-infrastructure/vpc-peering.html)

**이유**: Peering은 **모든 쌍(pair)마다 개별 연결 + 양쪽 라우팅 테이블 수정 + Security Group 설정**이 필요해 연결 수가 `n(n-1)/2`로 제곱에 가깝게 증가합니다.

| VPC 개수 (n) | 필요한 Peering 연결 수 | 관리 난이도 |
| --- | --- | --- |
| 4개 | 6개 | 쉬움 |
| 10개 | 45개 | 아직 관리 가능 |
| 50개 | 1,225개 | 매우 어려움 |
| 100개 | 4,950개 | 실질적으로 불가능 |

기술적 한도도 존재합니다: VPC당 활성 Peering 연결 수는 기본 50, 최대 125까지 상향 가능. [[VPC peering connection quotas]](https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-connection-quotas.html) 즉 125라는 하드 리밋에 닿기 전에도, **VPC가 10~20개만 넘어가도 라우팅 테이블·SG를 쌍마다 손으로 관리하는 운영 부담이 기술적 한도보다 먼저 병목**이 됩니다.

**결론**: Peering = 1:1 point-to-point + 비전이적(non-transitive) → VPC가 늘어날수록 연결 수가 **제곱으로 증가**. TGW = 허브 앤 스포크 + 전이적 라우팅 → VPC가 늘어나도 연결 수가 **선형으로(1개씩만)** 증가. 그래서 규모가 커지면 TGW로 전환하는 것이 정답입니다.

### 3.7 사용 시 주의점

| # | 실수 | 왜 문제인가 | 올바른 접근 |
| --- | --- | --- | --- |
| 1 | "A-B, A-C Peering이 있으면 B-C도 통신될 것"이라 착각 | Peering은 비전이적 — B-A-C 경유 통신은 애초에 불가능 | B-C가 통신해야 하면 별도 Peering 필요, 또는 TGW로 전환 |
| 2 | CIDR이 겹치는 VPC를 Peering 시도 | 주 IPv4 CIDR이 겹치면 Peering 자체가 생성되지 않음 | VPC 설계 초기에 CIDR을 서로 겹치지 않게 계획 |
| 3 | Peering만으로 온프레미스 연결까지 우회하려 시도 | Peering된 VPC를 거쳐 상대방의 온프레미스 연결(VPN 등)에는 접근 불가 | 온프레미스 공유가 필요하면 TGW 사용 |

### 3.8 개발자가 알아둬야 할 것들

- AWS Cloud WAN: TGW보다 상위 레벨에서 여러 리전의 네트워크를 정책 기반으로 통합 관리하는 서비스
- 참고 요금(2026년 상반기, 리전·시점에 따라 달라질 수 있어 [공식 요금 페이지](https://aws.amazon.com/transit-gateway/pricing/) 재확인 권장): TGW는 attachment당 약 $0.05/시간 + 처리 데이터 $0.02/GB

---

## 4. VPC Endpoint로 NAT을 완전히 대체할 수 있는가

**결론: 조건부로만 가능합니다.** VPC Endpoint(가상 프라이빗 접속점)는 "AWS 서비스로 가는 트래픽"만 대체하고, "AWS 서비스가 아닌 임의의 인터넷 목적지"는 여전히 NAT Gateway가 필요합니다.

### 4.1 두 가지 Endpoint 유형

| 구분 | Gateway Endpoint | Interface Endpoint (AWS PrivateLink 기반) |
| --- | --- | --- |
| 지원 대상 | **S3, DynamoDB 딱 2개뿐** | ECR, CloudWatch Logs, Secrets Manager, SSM 등 **140개 이상** AWS 서비스 |
| 동작 방식 | 라우팅 테이블에 prefix list 추가 (ENI 없음) | 서브넷에 ENI 생성 |
| 비용 | **무료** | **유료** — AZ당 시간당 요금 + 처리 데이터 GB당 요금 |
| 온프레미스 접근 | 불가 | Direct Connect/VPN으로 가능 |

[[Gateway endpoints 공식 문서]](https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html) · [[Choosing VPC Endpoint Strategy for S3]](https://aws.amazon.com/blogs/architecture/choosing-your-vpc-endpoint-strategy-for-amazon-s3/)

> ⚠️ Interface Endpoint도 공짜가 아니므로, "NAT 대신 무조건 저렴"이 아니라 **트래픽량과 서비스 개수에 따른 비용 트레이드오프**로 판단해야 합니다.

### 4.2 2장의 ECS Hello World 시나리오에 대입하면

```
ECS Fargate Task 가 나가야 하는 곳
├── ECR (이미지 pull)         → Interface Endpoint 2개 필요
│                               (com.amazonaws.<region>.ecr.api,
│                                com.amazonaws.<region>.ecr.dkr)
│                               + 이미지 레이어는 S3에 저장되므로
│                               S3 Gateway Endpoint도 같이 필요
├── CloudWatch Logs (로그 전송) → Interface Endpoint
├── Secrets Manager (비밀값)   → Interface Endpoint
└── 외부 결제 API, 날씨 API 등
    AWS가 아닌 서드파티 서비스   → ❌ Endpoint 없음 → NAT Gateway 필수
```

### 4.3 NAT을 완전히 제거할 수 있는 조건

| 시나리오 | NAT 제거 가능? |
| --- | --- |
| 오직 AWS 서비스(ECR, S3, CloudWatch, Secrets Manager 등)만 호출 | ✅ 가능 — 필요한 Endpoint를 다 만들면 NAT 0개도 가능 |
| 외부 SaaS(Software as a Service, 예: Stripe, OpenAI API) 호출이 하나라도 있음 | ❌ 불가능 — 그 트래픽만큼은 NAT 경유 필요 |
| pip/npm 등 퍼블릭 패키지 레지스트리 접근 | ❌ 불가능 (CodeArtifact 등으로 AWS 내부화하면 가능) |

즉 "AWS 서비스 트래픽 비중이 크고 외부 인터넷 호출이 거의 없는 워크로드"만 NAT을 완전히 없앨 수 있고, 그 외에는 **NAT + Endpoint를 병행**하는 게 현실적인 구성입니다.

---

## 5. Lambda의 VPC 모드 — 정확한 모델과 오해 정정

이 부분은 흔히 오해가 생기는 지점입니다. AWS 공식 블로그: *"Lambda 함수는 항상 Lambda 서비스가 소유한 VPC 안에서 실행된다... 기본적으로 VPC를 구성하지 않으면 Lambda는 퍼블릭 인터넷에 접근할 수 있다. VPC로 접근을 구성하면 더 이상 그렇지 않다."* [[Operating Lambda: Application design – Part 3]](https://aws.amazon.com/blogs/compute/operating-lambda-application-design-part-3/)

### 5.1 두 가지 모드

```
┌─────────────────────────────────────────────────────────────┐
│  [기본 모드] VPC 구성을 안 한 Lambda (VPC 미연결)                │
│                                                               │
│   Lambda 함수 실행환경                                          │
│   (AWS 소유 관리형 VPC 안에서 실행 — 고객 눈에는 안 보임)          │
│         │                                                     │
│         ├──────► 🌐 퍼블릭 인터넷 (직접 접근 가능)                │
│         └──────► AWS 서비스 API (직접 접근 가능)                 │
│                                                               │
│   ❌ 고객 VPC 안의 리소스(Private Subnet의 RDS 등)는 접근 불가!    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  [VPC 모드] 고객이 명시적으로 VPC 구성을 설정한 Lambda            │
│                                                               │
│   Lambda 함수 실행환경                                          │
│   (여전히 AWS 관리형 VPC 안에서 실행됨 — 컴퓨트 자체는 안 옮김)     │
│         │                                                     │
│         │ Hyperplane ENI로 고객 VPC 서브넷에 cross-attach       │
│         ▼                                                     │
│   고객 VPC 의 Private Subnet 안 ENI                             │
│         │                                                     │
│         ├──────► ✅ 같은 VPC의 RDS/ElastiCache 등 (이제 접근 가능) │
│         └──────► ❌ 인터넷 직접 접근 불가! (이제 Private Subnet    │
│                     라우팅 규칙을 그대로 따르기 때문)              │
│                     → NAT Gateway 또는 VPC Endpoint 있어야       │
│                        인터넷/AWS API 다시 접근 가능              │
└─────────────────────────────────────────────────────────────┘
```

[[Giving Lambda functions access to VPC resources]](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html) · [[Announcing improved VPC networking for Lambda]](https://aws.amazon.com/blogs/compute/announcing-improved-vpc-networking-for-aws-lambda-functions/)

### 5.2 정리 — VPC 모드 = private subnet infra 통신용

"VPC 모드 = private subnet infra 통신용"이라는 이해는 **정답**입니다. RDS, ElastiCache, 내부 ALB처럼 **고객 VPC의 Private Subnet에만 존재하는 리소스**에 접근해야 할 때만 VPC 모드를 켭니다. 그 외(S3, DynamoDB, 외부 API 호출만 하는 함수)는 VPC 모드를 켤 이유가 없고, 오히려 콜드 스타트 지연·ENI 할당 이슈(계정당 소프트 리밋 350개)가 생기니 **"필요할 때만 켜라"**가 공식 권장사항입니다.

### 5.3 트리거 축과 네트워크 축은 독립적 — 흔한 오해 정정

**"API Gateway로 요청 받는 서비스 = 기본(Non-VPC) 모드"라고 단정하면 안 됩니다.** Lambda 설계에는 서로 무관한 두 개의 축이 있습니다:

| 축 | 질문 | 선택지 |
| --- | --- | --- |
| **트리거** (무엇이 Lambda를 호출하는가) | 요청이 어떻게 들어오는가? | API Gateway, ALB, S3 이벤트, SQS, EventBridge... |
| **네트워크 모드** (Lambda가 어디로 나가는가) | 이 함수가 Private VPC 리소스에 접근해야 하는가? | 기본 모드(Non-VPC) vs VPC 모드 |

두 축이 독립적이라 4가지 조합이 전부 실제로 존재합니다.

| | API Gateway 트리거 | 비(非)-API Gateway 트리거 |
| --- | --- | --- |
| **기본 모드 (Non-VPC)** | 외부 날씨 API만 호출하는 조회용 API | S3 업로드 이미지를 리사이즈해서 다시 S3에 저장 (S3 이벤트 트리거) |
| **VPC 모드** | 고객 요청을 받아 **Private RDS**를 조회하는 API ← *사실 이게 실무에서 제일 흔한 패턴* | SQS 메시지를 받아 Private RDS에 저장하는 배치 처리 |

**정확한 판단 기준**은 "API Gateway를 쓰는가"가 아니라, **"이 함수의 로직이 고객 VPC의 Private Subnet 안 리소스(RDS, ElastiCache, 내부 ALB 등)에 접근해야 하는가"** 하나입니다.

```
질문: 이 Lambda 함수가 내 VPC의 Private Subnet 리소스에 접근하는가?
   │
   ├─ NO  → 기본 모드로 충분 (DynamoDB, S3, 외부 API 등은
   │         VPC 밖에서도 직접 호출 가능) → VPC 모드를 켤 이유 없음
   │
   └─ YES → VPC 모드 필수 (RDS, ElastiCache, 내부 ALB 등)
             → 이후 Private Subnet 규칙 그대로 적용
                (인터넷 필요하면 NAT/Endpoint도 같이 필요)
```

---

## 6. SQS·SNS는 VPC 모드가 있는가

**결론: 없습니다.** SQS(Simple Queue Service)와 SNS는 "VPC 모드"라는 개념 자체가 없습니다.

### 6.1 "VPC 모드"와 "VPC Endpoint"는 서로 다른 개념

핵심 구분: **누가 어느 방향으로 VPC 경계를 넘는가**가 다릅니다.

| | Lambda **VPC 모드** | SQS/SNS **VPC Endpoint** |
| --- | --- | --- |
| 누가 움직이는가 | **컴퓨트(Lambda)가** 고객 VPC 안으로 ENI를 만들어 **들어감** | 서비스는 그대로 밖에 있고, **VPC 안의 클라이언트**가 privately 접근할 **문(door)만** 생김 |
| 목적 | Lambda가 VPC **안의** 리소스(RDS 등)에 접근하기 위해 | VPC **안의** 무언가(Lambda, EC2, ECS)가 SQS/SNS라는 **완전관리형 서비스**에 인터넷 없이 접근하기 위해 |
| 서비스 자체 위치 | (해당 없음) | 항상 VPC 밖의 AWS 관리형 영역 — 원래부터 안 바뀜 |

```
Lambda VPC 모드                        SQS/SNS VPC Endpoint
──────────────────                     ──────────────────────
Lambda(컴퓨트) ──ENI로──▶ 고객 VPC        고객 VPC 안의 무언가
                (들어감)                 (Lambda, EC2...)
                                              │
                                              ▼ (Endpoint 통해 privately)
                                        SQS / SNS (원래 위치 그대로,
                                                    VPC 밖)
```

- SNS: *"AWS PrivateLink를 통해 VPC Endpoint를 지원하며, 인터넷을 거치지 않고 SNS 토픽에 프라이빗하게 메시지를 발행할 수 있다"* [[Amazon SNS Documentation]](https://aws.amazon.com/documentation-overview/sns/)
- SQS: *"인터페이스 VPC 엔드포인트를 정의하면 인터넷 게이트웨이, NAT, VPN 연결 없이도 SQS로 안정적이고 확장 가능한 연결을 제공한다"* [[Internetwork traffic privacy in Amazon SQS]](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-internetwork-traffic-privacy.html)

### 6.2 일반화 — 어떤 서비스가 "VPC 모드"를 가지는가

| 특징 | 예시 서비스 | VPC 모드 유무 |
| --- | --- | --- |
| 컴퓨트/DB가 실제로 서브넷에 ENI를 만들어야 동작 | Lambda(옵션), RDS, ElastiCache, ECS/EC2, Redshift | ✅ VPC 모드/네트워킹 구성 있음 |
| API 호출만으로 쓰는 완전관리형 서비스 | SQS, SNS, S3, DynamoDB, Secrets Manager, ECR | ❌ VPC 모드 없음 — **VPC Endpoint(접근용 문)만** 존재 |

"VPC 모드가 있다"는 건 그 서비스의 **컴퓨트 자체가 당신의 VPC 안으로 들어올 수 있는가**를 뜻하고, SQS/SNS처럼 순수 API 기반 관리형 서비스는 애초에 들어올 실체(컴퓨트)가 없어서 그 개념이 적용되지 않습니다.

---

## 7. SNS의 Private Subnet 전달 — 이론과 실제 사례 검증

### 7.1 SNS는 private HTTP(S) 엔드포인트로 직접 push할 수 없다 (공식 제약)

> *"Amazon SNS does not currently support private HTTP(S) endpoints."* — SNS가 HTTP/HTTPS 구독자에게 알림을 보낼 때는 **퍼블릭 인터넷을 통해 실제 HTTP POST 요청**을 보냅니다. 대상이 퍼블릭에서 도달 불가능하면 구독 등록 자체가 `"Unreachable Endpoint"` 에러로 실패합니다. [[SNS 공식 문서]](https://docs.aws.amazon.com/sns/latest/dg/sns-http-https-endpoint-as-subscriber.html) [[트러블슈팅 가이드]](https://repost.aws/knowledge-center/sns-topic-https-endpoints-notification)

**"발행(Publish)"과 "전달(Delivery)" 방향을 구분해야 합니다** — 6장의 VPC Endpoint는 **발행 방향**(VPC 안 → SNS)이고, 이건 **전달 방향**(SNS → 구독자)이라 완전히 다른 문제입니다.

```
① 발행 방향 (Publish) — VPC Endpoint로 해결되는 부분
   Private Subnet 안의 Lambda/EC2 ──(Interface Endpoint)──▶ SNS
   (인터넷 없이 SNS에 메시지를 "보내는" 건 가능)

② 전달 방향 (Delivery) — 지금 다루는 부분, VPC Endpoint와 무관
   SNS ──(퍼블릭 인터넷 HTTP POST)──✕──▶ Private Subnet 안의 HTTP 서버
   (SNS가 구독자에게 메시지를 "밀어넣는" 건 대상이 Private면 불가능)
```

### 7.2 그런데 Lambda·SQS 구독은 왜 문제없이 되는가

구독 유형별로 실제 전달 메커니즘이 다릅니다.

| 구독 유형 | 실제 전달 방식 | Private Subnet 대상 가능 여부 |
| --- | --- | --- |
| **HTTP/HTTPS** | SNS가 대상 URL로 진짜 네트워크 홉(HTTP POST)을 만듦 | ❌ 불가능 — 퍼블릭 도달 가능해야 함 |
| **Lambda** | SNS가 Lambda **Invoke API**를 호출(AWS 내부 control-plane 호출) | ✅ 가능 — 네트워크 라우팅이 아니라 API 호출이라 문제 없음 |
| **SQS** | SNS가 SQS **SendMessage API**를 호출(AWS 내부 control-plane 호출) | ✅ 가능 — 마찬가지로 API 호출 |

Lambda/SQS 구독이 잘 되는 이유는 SNS가 그쪽으로 "네트워크 연결"을 만드는 게 아니라 **AWS 내부 API를 호출**하는 것이기 때문입니다. Lambda가 VPC 모드인지 아닌지는 이 호출 성공 여부와 무관합니다.

### 7.3 Private Subnet에 정말 전달하고 싶다면 — Lambda 브릿지 패턴

AWS가 공식적으로 제시하는 방법은 **Lambda VPC 모드를 다리로 쓰는 것**입니다.

```
SNS ──(Invoke API, 문제없음)──▶ Lambda(VPC 모드, 대상과 같은 서브넷)
                                        │
                                        └──(VPC 내부 네트워크로 직접 HTTP 호출)──▶
                                                    Private Subnet 안의 서버
```

절차 (AWS 공식 가이드 요약):
1. 대상 Private 엔드포인트와 **같은 VPC·서브넷**에 Lambda 함수를 생성하고 VPC 모드로 구성
2. 대상의 Security Group 인바운드 규칙에 이 Lambda의 Security Group을 허용 소스로 추가
3. Lambda 코드에서 SNS 이벤트를 받아 그 안의 메시지를 대상 Private 엔드포인트로 직접 HTTP 요청 전달
4. 이 Lambda를 SNS 토픽에 구독자로 등록

[[SNS에 Private HTTP/HTTPS 엔드포인트 구독하는 방법(공식)]](https://repost.aws/knowledge-center/sns-subscribe-private-http-endpoint)

### 7.4 실제 사례로 검증 — "MS 간 통신 브로커로 SNS를 썼는데, 서비스가 private subnet에 있었다"

이 원칙을 실제 2022~23년 경험과 대조해본 결과를 정리합니다.

**1차 가설 — SNS → SQS Fan-out(당겨오기 방식)**: MS(Microservice, 마이크로서비스) 간 통신에 SNS를 브로커로 쓰는 가장 표준적인 AWS 레퍼런스 아키텍처는 SNS에 각 서비스의 SQS 큐를 구독시키고, 각 서비스는 자기 큐를 폴링(polling)하는 방식입니다.

```
                         SNS Topic (브로커)
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        SQS Queue-A     SQS Queue-B     SQS Queue-C
     (Service-A 소유)  (Service-B 소유)  (Service-C 소유)
              ▲               ▲               ▲
              │ ReceiveMessage(폴링, 나가는 방향)  │
      Service-A         Service-B         Service-C
   (Private Subnet)   (Private Subnet)  (Private Subnet)
```

여기서 서비스는 SNS/SQS로부터 "밀어넣어지는(push)" 게 아니라, 자기가 먼저 SQS로 나가서 메시지를 당겨오는(pull) 구조라 Private Subnet의 "outbound는 자유롭다"는 원칙과 맞아떨어집니다.

**실제 확인 — 중간에 SQS가 없었음**: 하지만 이번 사례는 "SNS → Service-A, Service-B" 직결 구조로, 중간에 SQS가 없었던 것으로 확인되었습니다. 이 경우 남는 후보는 다음과 같았습니다.

| 후보 | 구조 | Private Subnet 기억과 충돌 여부 |
| --- | --- | --- |
| ① 서비스 앞에 퍼블릭 진입점(ALB/NLB)이 있었음 | SNS → ALB/NLB(Public Subnet) → 실제 컴퓨트(Private Subnet) | 충돌 없음 — **실제로 이것이 정답으로 확인됨** |
| ② Service-A/B가 실은 Lambda였음 | SNS → Lambda Invoke API (7.2절 방식) | 충돌 없음 |
| ③ "Private Subnet"에 실제로는 IGW 라우트가 있었음 | 사실상 Public Subnet과 동일하게 동작 | 개념적 명명 차이 |

**최종 확인된 구조 (① 확정)**:

```
        🌐 Internet (SNS)
              │
    ┌─────────▼─────────┐
    │  ALB/NLB(Network    │  ← Public Subnet
    │  Load Balancer)     │     (여기가 SNS의 실제 HTTP 타겟,
    │  (SNS 발신 IP만 허용) │      SNS는 이 IP 대역만 허용하도록
    └─────────┬─────────┘     보안그룹에서 제한 가능
              │ (내부 전달)
    ┌─────────▼─────────┐
    │  Service-A/B 실제 로직 │  ← Private Subnet
    │  (ECS/EC2)          │     (여기가 "우리 서비스"라고 부르던 곳)
    └────────────────────┘
```

SNS가 HTTP POST를 실제로 때린 대상은 서비스 앞단의 ALB/NLB였고, 이 로드밸런서는 IGW로 가는 라우트가 있는 Public Subnet에 있어야 SNS가 도달할 수 있는 대신, 보안그룹으로 "AWS가 공개하는 SNS 발신 IP 대역만 허용"([[AWS IP ranges 문서]](https://docs.aws.amazon.com/general/latest/gr/aws-ip-ranges.html))하도록 잠가두면 다른 곳에서는 못 두드리고 SNS만 두드릴 수 있는, 사실상 사설처럼 느껴지는 퍼블릭 엔드포인트가 됩니다. 실제 업무 로직(컴퓨트)이 있는 곳은 분명히 Private Subnet이었으므로 기억이 틀린 게 아니라, "서비스"라고 부르는 범위에 로드밸런서가 포함되는지 여부의 관점 차이였던 것입니다.

---

## 8. 전체 정리 — 관통하는 하나의 원칙

이 대화 전체를 관통하는 원칙은 하나였습니다.

> **인터넷(또는 SNS)이 먼저 연결을 시작(inbound)하려면 반드시 Public Subnet의 무언가(ALB/NLB/API Gateway)를 거쳐야 하고, Private Subnet의 실제 컴퓨트는 그 뒤에서 "받는" 게 아니라 로드밸런서로부터 "전달"받는다.**

- 2장 ECS Hello World 아키텍처에서 ALB가 한 역할
- 5장 Lambda VPC 모드에서 "Private 엔드포인트로 못 들어가서 Lambda를 다리로 써야 했던" 이유
- 7장 SNS→ALB→Service 구조

전부 같은 원칙의 다른 사례였던 셈입니다.

---

## 📎 Sources

1. [AWS Networking Essentials](https://aws.amazon.com/getting-started/aws-networking-essentials/)
2. [NAT gateway use cases](https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateway-scenarios.html)
3. [Task Networking in AWS Fargate](https://aws.amazon.com/blogs/compute/task-networking-in-aws-fargate/)
4. [AWS Whitepaper: VPC peering](https://docs.aws.amazon.com/whitepapers/latest/aws-vpc-connectivity-options/vpc-peering.html)
5. [Building Scalable Secure Multi-VPC Network Infrastructure](https://docs.aws.amazon.com/whitepapers/latest/building-scalable-secure-multi-vpc-network-infrastructure/vpc-peering.html)
6. [VPC peering connection quotas](https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-connection-quotas.html)
7. [Communicating across VPCs and AWS Regions](https://docs.aws.amazon.com/prescriptive-guidance/latest/secure-outbound-network-traffic/vpc-region-communication.html)
8. [Designing hyperscale Amazon VPC networks](https://aws.amazon.com/blogs/networking-and-content-delivery/designing-hyperscale-amazon-vpc-networks/)
9. [AWS Transit Gateway Pricing](https://aws.amazon.com/transit-gateway/pricing/)
10. [Gateway endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html)
11. [Choosing Your VPC Endpoint Strategy for Amazon S3](https://aws.amazon.com/blogs/architecture/choosing-your-vpc-endpoint-strategy-for-amazon-s3/)
12. [Operating Lambda: Application design – Part 3](https://aws.amazon.com/blogs/compute/operating-lambda-application-design-part-3/)
13. [Giving Lambda functions access to resources in an Amazon VPC](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html)
14. [Announcing improved VPC networking for AWS Lambda functions](https://aws.amazon.com/blogs/compute/announcing-improved-vpc-networking-for-aws-lambda-functions/)
15. [Amazon SNS Documentation — Message privacy](https://aws.amazon.com/documentation-overview/sns/)
16. [Internetwork traffic privacy in Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-internetwork-traffic-privacy.html)
17. [Fanout Amazon SNS notifications to HTTPS endpoints](https://docs.aws.amazon.com/sns/latest/dg/sns-http-https-endpoint-as-subscriber.html)
18. [How do I subscribe a private HTTP or HTTPS endpoint to my Amazon SNS topic?](https://repost.aws/knowledge-center/sns-subscribe-private-http-endpoint)
19. [AWS IP address ranges](https://docs.aws.amazon.com/general/latest/gr/aws-ip-ranges.html)
