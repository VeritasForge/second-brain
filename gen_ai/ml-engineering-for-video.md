# Q1. 온프레미스 환경에서 GPU 기반 AI 영상 처리 플랫폼을 처음부터 설계한다고 가정합니다. 전체 아키텍처를 어떻게 구성하시겠습니까?

**학습 포인트**: 온프레미스 GPU 기반 AI 영상 처리 플랫폼 아키텍처 설계

#### 모범답변

**핵심 요약**: 4개 레이어(인프라 → 플랫폼 → 애플리케이션 → 인터페이스)로 분리하고, 각 레이어를 독립적으로 확장 가능하게 설계합니다.

```
┌─────────────────────────────────────────────────────────┐
│  📡 Interface Layer                                      │
│  REST API / gRPC / Web Dashboard                         │
├─────────────────────────────────────────────────────────┤
│  ⚙️ Application Layer                                    │
│  Job Manager │ Workflow Engine │ Result Handler           │
│  (작업 접수)   (DAG 오케스트레이션)  (결과 전달)          │
├─────────────────────────────────────────────────────────┤
│  🔧 Platform Layer                                       │
│  Container Orchestration (K8s) │ GPU Scheduler            │
│  Model Registry │ Monitoring │ Auth/RBAC                  │
├─────────────────────────────────────────────────────────┤
│  💾 Infrastructure Layer                                  │
│  GPU Servers │ High-Speed Network │ Distributed Storage   │
│  (L40S+A100 이원화) (25-100GbE/RoCE)   (BeeGFS/NFS)     │
└─────────────────────────────────────────────────────────┘
```

**상세 설명**:

**1) Infrastructure Layer**
- **GPU 서버**: 용도별 GPU 이원화 전략을 권장합니다.
  - **추론 전용 노드**: **NVIDIA L40S** — NVENC/NVDEC 각 3기 내장으로 영상 디코딩→AI 추론→영상 인코딩 올인원 파이프라인 가능. H100 대비 Video AI TCO 우수. 48GB GDDR6.
  - **멀티테넌트 격리가 필요한 노드**: **NVIDIA A100 80GB** — MIG(Multi-Instance GPU)를 지원하여 하드웨어 레벨 GPU 파티셔닝 가능. 고객 간 GPU 격리가 필수인 경우 선택.
  - **참고**: L40S는 MIG를 지원하지 않으므로, GPU 공유가 필요하면 NVIDIA MPS(Multi-Process Service) 또는 시간 분할(Time-slicing) 방식을 사용.
- **네트워크**: GPU 서버 간 통신은 25/100GbE. 스토리지 접근은 별도 네트워크 분리 (Storage Network). 초기에는 RoCEv2로 시작하고, 규모 확장 시 InfiniBand으로 전환.
- **스토리지**: Hot/Warm/Cold 3-tier 구성. Hot(NVMe SSD) → 현재 처리 중인 영상. Warm(HDD RAID) → 최근 완료 작업. Cold(테이프/오브젝트) → 아카이브.

**2) Platform Layer**
- **Kubernetes** 기반 컨테이너 오케스트레이션 (NVIDIA GPU Operator 포함)
- **GPU 스케줄러**: GPU 모델에 따라 MIG(A100) 또는 MPS/Time-slicing(L40S)으로 파티셔닝하여 다중 작업 동시 처리
- **Model Registry**: MLflow 또는 자체 구축하여 모델 버전 관리
- **모니터링**: NVIDIA DCGM + Prometheus + Grafana로 GPU 사용률, 온도, 메모리 실시간 모니터링

**3) Application Layer**
- **Job Manager**: 고객 요청을 접수하고 작업 큐(Redis/RabbitMQ)에 등록
- **Workflow Engine**: Temporal 또는 Argo Workflows로 DAG 기반 워크플로우 실행 (영상 분할 → 전처리 → AI 추론 → 후처리 → 합성)
- **Result Handler**: 완료된 결과물을 고객별 스토리지로 전달, 알림 발송

**4) Interface Layer**
- REST API / gRPC로 외부 시스템 연동
- 웹 대시보드로 작업 상태 모니터링, 결과 미리보기

**핵심 설계 원칙**:
- **Stateless 서비스**: 모든 애플리케이션 서비스는 Stateless로 설계하여 수평 확장 가능
- **데이터 지역성**: GPU 서버와 Hot 스토리지를 물리적으로 가깝게 배치하여 I/O 병목 최소화
- **장애 격리**: 고객별 namespace 분리, GPU 장애 시 자동 재스케줄링

> **출처**: [NVIDIA AI Enterprise Reference Architecture](https://docs.nvidia.com/ai-enterprise/planning-resource/reference-architecture-for-multi-tenant-clouds/latest/workload-isolation.html), [Databricks AI Infrastructure Best Practices](https://www.databricks.com/blog/ai-infrastructure-essential-components-and-best-practices), [Deloitte AI Infrastructure Reckoning 2026](https://www.deloitte.com/us/en/insights/topics/technology-management/tech-trends/2026/ai-infrastructure-compute-strategy.html)

**예상 꼬리질문**:
- "Hot/Cold 스토리지 간 데이터 이동 정책은 어떻게 설계하시겠습니까?"
- "이 아키텍처에서 단일 장애점(SPOF)은 어디이며, 어떻게 해결하시겠습니까?"

---

#### 📝 Q1 심화 학습 노트: 아키텍처 키워드 개념 정리

##### 플랫폼의 본질: ML 모델을 호출하는 시스템

이 플랫폼은 AI 모델 개발이 아닌 **AI 추론(Inference) 서빙 시스템**이다. AI 연구팀이 CVPR SOTA 초해상화 모델을 개발(Training)하면, ML 엔지니어는 완성된 모델을 받아서 GPU 위에 올리고 효율적으로 추론을 수행하는 **인프라/플랫폼을 설계·운영**한다.

```python
# 극도로 단순화한 구조
video = receive_upload("movie_1080p.mp4")        # 고객 업로드
frames = ffmpeg.extract_frames(video)             # 프레임 분할
for batch in chunk(frames, batch_size=16):
    upscaled = model.inference(batch)             # GPU에서 추론 ⭐
    save(upscaled)
result = ffmpeg.merge_frames(upscaled_frames, audio)  # 영상 합성
```

ML 엔지니어가 고민하는 것은 `model.inference(batch)` 한 줄이 아니라, **그 주변의 모든 것**: 프레임을 GPU 메모리에 효율적으로 올리는 법, batch_size 최적화, 수천 개 동시 요청 스케줄링, GPU 장애 복구, 고객 간 데이터 격리.

FastAPI + Celery 경험으로 비유하면:
- FastAPI = Interface Layer (API 요청 접수)
- Celery Worker = GPU에서 모델 돌리는 워커
- RabbitMQ/Redis = 작업 큐
- 차이점: Celery worker가 CPU 대신 **GPU**를 쓰고, 작업이 ms가 아닌 **분~시간** 단위

##### 🆕 영상 파일 기초 개념

###### 컨테이너 (Container) vs 코덱 (Codec)

컨테이너 = 여러 종류의 데이터를 하나의 파일에 담는 포장 상자. 코덱 = 상자 안의 내용물을 압축하는 방식.

```
🎁 선물 상자 (컨테이너 = MP4 파일)
├── 🎥 영상 (비디오 스트림: H.264로 압축)
├── 🔊 음성 (오디오 스트림: AAC로 압축)
├── 📝 자막 (SRT 텍스트)
└── 🏷️ 메타데이터 (제목, 길이, 해상도)

컨테이너 (상자)     코덱 (압축 방식)
    MP4        ──→  비디오: H.264, H.265, AV1
                    오디오: AAC, MP3, Opus
```

| 컨테이너 | 확장자 | 특징 |
|----------|--------|------|
| **MP4** | `.mp4` | 가장 보편적. 웹/모바일 호환성 최고 |
| **MKV** | `.mkv` | 자막/다중 오디오 트랙 지원에 강함 |
| **MOV** | `.mov` | Apple. ProRes 코덱 주로 사용 |
| **MPEG-TS** | `.ts` | 방송/스트리밍용 (HLS 기반) |

###### H.264 코덱 — 프레임 간 차이만 저장하여 압축

H.264(AVC) = 가장 널리 쓰이는 영상 압축 코덱. 프레임 간 차이만 저장하여 대폭 압축.

```
원본: 3장 모두 "집+나무" 동일, 소년만 다름 → 매번 전체 그리기 = 낭비!

H.264:
  1장(I-frame): 🏠+🧒+🌳 ← 전체 그림 (키프레임, 독립 디코딩 가능)
  2장(P-frame): "1장 + 소년 손 올림" ← 차이만 기록 (이전 참조)
  3장(B-frame): "1장+3장 참조" ← 양방향 차이 (가장 작지만 복잡)
```

```
영상 타임라인:  I --- P --- P --- B --- P --- I --- P --- P
                │                              │
                └── GOP (Group of Pictures) ──┘
```

💡 **I-frame = 세그먼트 분할의 기준점**. I-frame만 독립 디코딩 가능하므로, 시간 구간 분할 시 반드시 I-frame 경계에서 잘라야 함. → "프레임 레벨 vs 세그먼트 레벨 분할" 섹션 참조.

| 코덱 | 다른 이름 | 1분 1080p 용량 |
|------|----------|---------------|
| **H.264** | AVC | ~150MB |
| **H.265** | HEVC | ~75MB (2x 효율) |
| **AV1** | - | ~60MB (2.5~3x) |

###### Demux / Mux — 스트림 분리와 합성

```
demux (de-multiplex): MP4 → 비디오 스트림(H.264) + 오디오 스트림(AAC) + 자막
mux (multiplex): 비디오 + 오디오 + 자막 → MP4
```

AI 업스케일링에서 demux하는 이유: AI 모델은 프레임(이미지)만 처리하므로 오디오가 불필요. 오디오는 따로 보관했다가 추론 완료 후 mux로 다시 합침.

###### FFmpeg — 영상 처리의 만능 오픈소스 도구

FFmpeg = demux, decode, encode, mux, 포맷 변환, 프레임 추출 등 모든 영상 처리의 기본 도구.

```bash
# 포맷 변환
ffmpeg -i input.mov output.mp4

# 프레임 추출 (AI 전처리용)
ffmpeg -i input.mp4 frame_%04d.png

# L40S NVENC 하드웨어 인코딩 (17배 빠름!)
ffmpeg -hwaccel cuda -i input.mp4 -c:v h264_nvenc output.mp4

# 프레임 합성 + 오디오 머지 (AI 후처리용)
ffmpeg -i frame_%04d.png -i audio.aac -c:v h264_nvenc output_4k.mp4
```

| 도구 | 역할 |
|------|------|
| **ffmpeg** | 메인. 변환/인코딩/디코딩 |
| **ffprobe** | 미디어 파일 정보 조회 |
| **ffplay** | 간단한 미디어 플레이어 |

📌 Meta: 하루 수십억 번 FFmpeg 실행, 10억 건+ 비디오 업로드 처리.

###### CUDA와 CUDA 커널

**CUDA** = NVIDIA가 만든 "GPU로 범용 계산을 시키는 프로그래밍 플랫폼".

```
🧠 CPU = 대학교수 4명 (복잡한 계산 가능, 하지만 4명뿐)
🏭 GPU CUDA Cores = 초등학생 10,000명 (단순 계산만, 하지만 10,000명 동시!)
→ AI 추론(행렬 곱셈) = 단순 덧셈+곱셈의 대량 반복 → GPU 압도적
```

**CUDA 커널** = GPU 스레드 수천 개가 동시에 실행하는 함수:

```c
__global__ void normalize(float* pixels, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) pixels[i] /= 255.0f;  // 정규화
}
normalize<<<blocks, threads>>>(gpu_pixels, total_pixels);
// ↑ "10,000명에게 동시에 작업 시작!"
```

###### GPU 내부 구성요소 — 역할 분담

```
NVIDIA GPU
├── CUDA Cores (범용 연산) ← CUDA 커널 실행. AI 추론, 정규화 등
├── Tensor Cores (AI 특화) ← FP16/INT8 행렬 곱셈 가속
├── NVDEC (디코딩 전용 칩) ← H.264 → raw 프레임. CUDA와 별개 하드웨어
└── NVENC (인코딩 전용 칩) ← raw 프레임 → H.265. CUDA와 별개 하드웨어
```

⚠️ **CUDA cores로 디코딩은 실용적이지 않다.** 디코딩/인코딩은 NVDEC/NVENC 전용 칩 또는 CPU 소프트웨어가 담당.

##### A. GPU 하드웨어 기초

###### NVIDIA 데이터센터 GPU 라인업

```
NVIDIA GPU 라인업 (데이터센터용, 2024-2025 기준):

🏢 데이터센터용 (서버에 꽂는 것):
  ├─ H100 / H200    → AI 학습(Training) 최강. 가장 비쌈 ($25K+)
  ├─ A100            → AI 학습/추론 범용. H100 이전 세대 (2020)
  ├─ L40S            → AI 추론 + 영상 처리 특화. 가성비 좋음
  ├─ A10G / L4       → 가벼운 추론용. 클라우드에서 많이 씀
  └─ B100 / B200     → 최신 Blackwell 세대 (2025~)

세대 순서: A100(Ampere, 2020) → H100(Hopper, 2022) → B100/B200(Blackwell, 2024)
```

게이밍 GPU(RTX 4090)와 데이터센터 GPU(L40S)는 물리적 형태도 다르다. 게이밍은 팬 달린 카드로 PC 케이스에 꽂고, 데이터센터용은 팬 없는 납작한 보드로 서버 랙에 장착하여 서버 자체 냉각 시스템을 사용한다.

###### GPU 서버 구성: 서버 1대에 GPU 여러 개

```
일반 PC: GPU 1~2개 (게이밍)

GPU 서버 (데이터센터용, 예: NVIDIA DGX A100):
┌─────────────────────────────────────────────┐
│  CPU: 2개 (AMD EPYC 또는 Intel Xeon)         │
│  RAM: 512GB ~ 1TB~2TB (시스템 메모리)         │
│  GPU: 8개 (A100 80GB × 8 = 640GB VRAM!)     │
│  NVLink: GPU끼리 초고속 연결                  │
│  SSD: 여러 개 (NVMe)                         │
│                                               │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐                    │
│  │GPU│ │GPU│ │GPU│ │GPU│                    │
│  │ 0 │ │ 1 │ │ 2 │ │ 3 │                    │
│  └───┘ └───┘ └───┘ └───┘                    │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐                    │
│  │GPU│ │GPU│ │GPU│ │GPU│                    │
│  │ 4 │ │ 5 │ │ 6 │ │ 7 │                    │
│  └───┘ └───┘ └───┘ └───┘                    │
└─────────────────────────────────────────────┘
```

서버 1대에 GPU가 8개이므로, "서버에 빈 GPU 있나?"라는 표현이 나오는 것이다. GPU 0~3번은 사용 중이고 4~7번은 비어있을 수 있다.

###### GPU 메모리 (VRAM) — CPU의 RAM과 완전히 별개

GPU에는 자체 전용 메모리가 물리적으로 내장되어 있다:

```
🖥️ 서버 내부 구조:

  CPU ←── 고속 버스 ──→ RAM (시스템 메모리, DDR5)
  GPU ←── 고속 버스 ──→ VRAM (GPU 전용 메모리, GPU 카드에 납땜)
  CPU ←── PCIe ──→ GPU  (둘 사이 통신은 상대적으로 느림)
```

| GPU | VRAM | VRAM 종류 | 용도 |
|-----|------|-----------|------|
| RTX 4090 (게이밍) | 24GB | GDDR6X | 게임, 개인 AI |
| **L40S** | **48GB** | **GDDR6** | AI 추론 + 영상 |
| **A100** | **40GB 또는 80GB** | **HBM2e** | AI 학습/추론 |
| H100 | 80GB | HBM3 | AI 학습 최강 |

AI 추론 시 VRAM에 올라가야 하는 것들: AI 모델 가중치(~2-4GB), 입력 프레임 데이터, 중간 계산 결과(활성화 맵), 출력 데이터. VRAM 부족 시 OOM 에러로 처리 불가.

###### NVENC / NVDEC — GPU 내장 영상 인코딩/디코딩 전용 칩

```
NVENC = NVIDIA Video ENCoder (영상 압축 전용 칩)
NVDEC = NVIDIA Video DECoder (영상 해제 전용 칩)
```

| GPU | NVENC (인코딩) | NVDEC (디코딩) |
|-----|---------------|---------------|
| L40S | **3개** | **3개** |
| A100 | **0개** | **1개** (제한적) |
| H100 SXM | 0개 | 0개 |

영상 업스케일링 파이프라인에서의 차이:

```
L40S: NVDEC(500+fps) → GPU 메모리 내에서 AI 추론 → NVENC(500+fps)
      ↑ 모든게 GPU 안에서 끝남! CPU 개입 없음!

A100: CPU or NVDEC(제한적) → AI 추론 → CPU에서 인코딩(30fps) ⚠️
      ↑ 인코딩이 CPU 병목!
```

A100이 아무리 AI 연산이 빨라도, NVENC 0개라 인코딩을 CPU로 해야 하면 전체 파이프라인이 느려진다. **이것이 영상 처리에서 L40S가 A100보다 유리한 핵심 이유.**

##### B. L40S + A100 이원화 전략

###### 이원화 판단 기준

| 상황 | 선택 | 이유 |
|------|------|------|
| 일반 고객의 영상 업스케일링 | L40S | 성능 충분 + NVENC/NVDEC로 효율적 |
| 디즈니급 대형 고객 (보안 필수) | A100 MIG | GPU 메모리까지 물리적 격리 필요 |
| 극장용 4K 리마스터 (대용량) | A100 80GB | 80GB VRAM이 필요한 경우 |

순수 연산 능력만 보면 L40S FP16 362 TFLOPS > A100 312 TFLOPS. L40S만으로 영상 AI 서비스 전부 처리 가능하며, A100은 MIG(보안 격리)나 80GB 대용량 VRAM이 필요한 특수 케이스에 사용.

###### MIG (Multi-Instance GPU) — 하드웨어 레벨 GPU 분할

MIG = Multi-Instance GPU. A100/H100에서 GPU의 연산 유닛(GPC)과 메모리를 **하드웨어 레벨에서 분할**하여 각각 독립된 미니 GPU처럼 동작하게 하는 기술.

GPU를 여러 사람이 공유하는 3가지 방법 비교:

```
1️⃣ Time-slicing (시분할) = 원룸 + 시간대별 공유
   한 번에 한 명만 GPU 전체를 씀. 메모리 잔류 가능 → 보안 취약

2️⃣ MPS (Multi-Process Service) = 셰어하우스
   A와 B가 동시에 GPU를 씀. 메모리 공유 → 한쪽 OOM 시 전체 죽음

3️⃣ MIG (Multi-Instance GPU) = 아파트 🏢
   GPU를 물리적 벽으로 나눔. 각 파티션이 독립된 GPU처럼 동작
   ✅ 메모리 접근 물리적 차단 ✅ 장애 격리
```

A100 내부 구조: 총 8개 GPC (Graphics Processing Cluster), 각 GPC 안에 SM 16개, 각 SM 안에 CUDA 코어 64개 = 총 약 6,912 CUDA 코어. MIG는 이 GPC들과 메모리 컨트롤러를 그룹으로 묶어 분리한다.

```
MIG로 쪼갠 A100 (예: 3g.40gb + 4g.40gb):

┌────────────────────────────────────────────────┐
│  A100 GPU                                       │
│  ┌──────────────────┐ ┌─────────────────────┐   │
│  │ Instance 0       │ │ Instance 1          │   │
│  │ (3g.40gb)        │ │ (4g.40gb)           │   │
│  │ GPC: 3개         │ │ GPC: 4개            │   │
│  │ VRAM: 40GB       │ │ VRAM: 40GB          │   │
│  │ ← 디즈니 전용    │ │ ← KBS 전용          │   │
│  │ 🔒 하드웨어 벽!  │ │ 🔒 하드웨어 벽!     │   │
│  └──────────────────┘ └─────────────────────┘   │
│        ↑ 서로의 메모리에 절대 접근 불가 ↑         │
└────────────────────────────────────────────────┘
```

###### 하드웨어 레벨 격리 vs 소프트웨어 격리

```
소프트웨어 격리 = 칸막이 (규칙으로 정함, 버그 있으면 뚫릴 수 있음)
하드웨어 격리 = 콘크리트 벽 (물리적으로 불가능, 소프트웨어 취약점으로도 뚫을 수 없음)
```

###### MIG 보안 격리의 진짜 이유: GPU 메모리 잔류

GPU VRAM은 작업이 끝나도 **자동으로 지워지지 않는다**. MIG 없이 GPU를 공유하면 이전 고객(디즈니)의 미공개 영화 프레임이 VRAM에 잔류하고, 다음 고객(KBS)의 악의적 코드가 VRAM을 스캔하면 미공개 콘텐츠가 유출될 수 있다.

현실적 위험도 평가:
- 🟢 **낮음**: 외부 해커가 GPU VRAM을 직접 읽는 공격 (매우 어려움)
- 🟡 **중간**: 내부자 또는 버그에 의한 우발적 접근 (소프트웨어 버그에 가까움)
- 🔴 **높음**: 계약/컴플라이언스 요구 — 디즈니 같은 대형 고객이 계약서에 "물리적 격리 환경" 명시 가능

**대안**: 작업 완료 후 VRAM zeroing(`cuda_memset(0)`)으로 잔류 데이터 제거. 기술적으로 충분하나, 대형 고객의 컴플라이언스 요구에는 MIG가 필요할 수 있음.

###### 실무 판단: L40S 단일 구성의 합리성

스타트업 규모에서는 L40S 단일 구성이 현실적이다:
- ✅ 영상 처리에 최적 (NVENC/NVDEC 3/3)
- ✅ A100보다 저렴 (약 $7K vs $15K+)
- ✅ 운영 복잡도 낮음 (MIG 관리 불필요)
- ✅ VRAM zeroing으로 보안 충분 (대부분의 경우)
- ⚠️ 단점: MIG 없으므로 초대형 고객 계약 시 불리할 수 있음

**핵심 포인트**: "L40S만으로 구성하겠다"라고 답하면서 "대형 고객의 컴플라이언스 요구에 대비해 A100 MIG 옵션은 인지하고 있다"라고 덧붙이면 현실적 판단력 + 확장 가능한 사고를 동시에 보여줄 수 있다.

##### C. 네트워크: 25-100GbE / RoCE

###### 25GbE 대역폭 계산 (Step by Step)

```
기본 단위:
  bit (비트) = 0 또는 1 하나 → 네트워크 속도 단위 (소문자 b)
  Byte (바이트) = bit 8개 묶음 → 파일 크기 단위 (대문자 B)
  1 Byte = 8 bits

25GbE = 초당 25 Gigabit = 25,000,000,000 bit/s

Byte로 변환:
  25,000,000,000 bit/s ÷ 8 = 3,125,000,000 Byte/s = 3.125 GB/s

비교표:
  1 GbE  = 1 ÷ 8 = 0.125 GB/s = 125 MB/s
  10 GbE = 10 ÷ 8 = 1.25 GB/s
  25 GbE = 25 ÷ 8 = 3.125 GB/s  ← 스타트업 초기
  100 GbE = 100 ÷ 8 = 12.5 GB/s ← 확장 시
```

실제로는 패킷 헤더 오버헤드로 이론값의 ~80-95%: 약 2.5~3.0 GB/s.

###### 왜 25GbE로 충분한가?

GPU는 데이터를 "잠깐 읽고 오래 계산"하므로 네트워크 사용 시간이 짧다:

```
GPU 서버 1대가 6GB 청크를 처리하는 시간:
  Step A: 스토리지에서 읽기 = 6GB ÷ 3.1GB/s ≈ 2초
  Step B: AI 추론 (GPU 연산) = ~300초 (5분) ← 네트워크 안 씀!
  Step C: 결과물 저장 = 24GB ÷ 3.1GB/s ≈ 8초

  네트워크 사용 비율: (2+8) / 310 ≈ 3.2%
  → 네트워크는 전체 시간의 3%만 사용! 25GbE로 충분
```

###### RoCE (RDMA over Converged Ethernet)

RoCE = RDMA over **Converged** Ethernet. CPU 커널을 거치지 않고 메모리끼리 직접 통신하여 CPU 병목 없이 고속 전송.

필요 인프라:
- RDMA 지원 NIC (네트워크카드): NVIDIA ConnectX-6/7 등 ($500~$2,000/장)
- DCB 지원 네트워크 스위치: PFC(Priority Flow Control) 설정으로 패킷 손실 방지
- 특별한 메인보드 불필요 (PCIe 슬롯에 NIC 장착)

영상 AI 환경에서 RoCE의 주 용도: GPU 서버 ↔ 스토리지 서버 간 대용량 영상 파일 고속 전송 (GPU 서버 간 직접 통신은 거의 불필요).

##### D. 분산 스토리지: BeeGFS / NFS / MinIO

###### NFS vs BeeGFS 비교

```
NFS: 1대 서버 + 파일 통째로 저장 + 순차 접근
     장점: 간단 / 단점: 병목, 장애 시 전체 마비

BeeGFS: N대 서버 + 파일 쪼개서 분산(스트라이핑) + 병렬 접근
        장점: 고성능, 장애 대응, 확장성 / 단점: 설치 복잡도
```

###### BeeGFS Buddy Mirror: 미리 복제해둔 것을 쓰는 방식

"죽은 후에 복제"하는 게 아니라 **"평소에 항상 2벌씩 저장"**:

```
파일 쓸 때 (정상 상태):
  서버1: 조각1(100GB) ←→ 서버2: 조각1 복제본(100GB)  ← Buddy 쌍
  서버3: 조각2(100GB) ←→ 서버4: 조각2 복제본(100GB)  ← Buddy 쌍

서버1이 죽었을 때:
  서버2의 복제본이 이미 있음 → 자동으로 Primary 승격 → 서비스 지속

서버1 복구 후:
  BeeGFS가 자동으로 서버1에 데이터 재복제 (self-healing)

대가: 스토리지 용량 2배 필요 (100TB 데이터 → 200TB)
```

###### BeeGFS 메타데이터 서버 분리

메타데이터 = 파일 이름, 크기, 생성 시간, 권한, **스트라이핑 정보**(몇 바이트로 쪼개져서 어떤 서버에 분리되어 있는지), **Buddy 쌍 정보**(복제본 위치).

BeeGFS는 메타데이터 서버를 스토리지 서버와 분리 가능:
- 메타데이터서버: "이 파일 어디에 있어?" 응답 (빠름, 작은 데이터)
- 스토리지서버: 실제 데이터 저장/읽기 (대용량)

BeeGFS는 순수 소프트웨어로, 일반 리눅스 서버에 설치하면 동작. 구성요소: Management Server, Metadata Server, Storage Server, Client.

###### MinIO — 온프레미스 S3

리눅스에 바이너리 설치하여 S3 호환 API(HTTP)로 오브젝트를 저장하는 소프트웨어. AWS S3 SDK/CLI(`boto3`, `aws s3 cp`)를 엔드포인트만 변경하여 그대로 사용 가능. 이 아키텍처에서 Cold(아카이브) 스토리지로 사용.

```
AWS 비유:
├─ BeeGFS ≈ FSx for Lustre (파일시스템, POSIX 호환, 고성능 컴퓨팅용)
├─ MinIO ≈ S3 (오브젝트 스토리지, HTTP API, 아카이브용)
└─ 예시: Hot/Warm = BeeGFS, Cold = MinIO
```

###### 선택 기준

| GPU 서버 규모 | 추천 스토리지 | 이유 |
|--------------|-------------|------|
| 1~3대, 단일 고객 | NFS | 간단, 충분 |
| **4대+, 멀티테넌트** | **BeeGFS** | 병렬 I/O, 장애 복구, 확장성 ← **추천** |
| 50대+ | Lustre | EB급 확장성 |

###### 🆕 BeeGFS Meta Buddy Mirror — 메타데이터 서버 이중화

스토리지 Buddy Mirror가 "실제 데이터"를 복제하는 것처럼, **Meta Buddy Mirror**는 "메타데이터(파일 위치/속성 정보)"를 복제한다.

```
비유: 도서관 책장 2벌 복사(Storage Buddy) + 카탈로그 2벌 복사(Meta Buddy)
→ 카탈로그(메타데이터)가 사라지면 책은 있어도 찾을 수 없으므로 서비스 불가!

Meta Server 1 (Primary) ←→ Meta Server 2 (Mirror)
  쓰기 시 양쪽 동시 기록 → Server 1 장애 시 Server 2 자동 승격
```

| 구분 | 이중화 대상 | 시점 |
|------|-----------|------|
| Storage Buddy Mirror | 실제 영상 데이터 | Phase 1부터 (데이터 유실 치명적) |
| **Meta Buddy Mirror** | 파일 위치/속성 정보 | **Phase 2 (8→16대)** (부하 증가 시) |

Phase 1에서 메타데이터 서버 1대로 충분한 이유: 메타데이터는 용량이 작고(GB 단위) 장애 시 재시작으로 복구 가능. 확장 시(16대+) 동시 접근 부하와 다운타임 불허 요건으로 이중화 필수.

##### E. Kubernetes (K8s) 구성요소 상세

###### K8s 전체 구조

```
┌─────────────────────────────────────────────────────┐
│  Control Plane (관리동) — K8s의 두뇌                   │
│  ┌──────────────┐  ┌──────────────┐                  │
│  │ API Server   │  │ Scheduler    │                  │
│  │ (접수 창구)   │  │ (배치 담당자) │                  │
│  └──────────────┘  └──────────────┘                  │
│  ┌──────────────┐  ┌──────────────┐                  │
│  │ etcd         │  │ Controller   │                  │
│  │ (데이터베이스)│  │ Manager      │                  │
│  │ (모든 상태   │  │ (상태 감시+  │                  │
│  │  저장)       │  │  자동 복구)  │                  │
│  └──────────────┘  └──────────────┘                  │
├──────────────────────────────────────────────────────┤
│  Worker Nodes (작업동) — 실제 일하는 서버들             │
│  ┌─── Node 1 (GPU서버1) ───┐  ┌─── Node 2 ────────┐  │
│  │ kubelet (현장 관리자)    │  │ kubelet            │  │
│  │ kube-proxy (네트워크)    │  │ kube-proxy         │  │
│  │ ┌─Pod A──┐ ┌─Pod B──┐  │  │ ┌─Pod C──┐         │  │
│  │ │Triton  │ │Triton  │  │  │ │Triton  │         │  │
│  │ │GPU:0   │ │GPU:1   │  │  │ │GPU:0   │         │  │
│  │ └────────┘ └────────┘  │  │ └────────┘          │  │
│  └─────────────────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

###### Control Plane 구성요소

Control Plane = K8s가 동작하기 위한 핵심 구성. 보통 별도 서버 1~3대에 설치 (GPU 불필요). AWS EKS에서는 AWS가 관리.

**kubectl**: K8s용 CLI 도구. 사용자가 터미널에서 `kubectl` 명령어를 입력하면 API Server가 받아서 처리:
```bash
$ kubectl get pods              # 돌아가는 Pod 목록 조회
$ kubectl get nodes             # 서버(Node) 목록 조회
$ kubectl apply -f triton.yaml  # 설정대로 Pod 생성
$ kubectl delete pod triton-1   # Pod 삭제
$ kubectl logs triton-1         # Pod 로그 조회
```

**API Server**: 모든 명령의 진입점. kubectl이 보내는 HTTP 요청을 받아서 처리.

**Scheduler**: 새 Pod를 어떤 Node에 올릴지 결정. 2단계 로직:
1. 필터링: GPU 부족/메모리 부족/다운된 Node 제외
2. 점수 매기기: 자원 균형, 데이터 지역성 등으로 최적 Node 선택

설정 방법 (Pod yaml):
```yaml
# 특정 GPU 타입이 있는 Node에만 올리기
spec:
  nodeSelector:
    gpu-type: "l40s"

# 더 세밀한 제어 (affinity)
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: customer
            operator: In
            values: ["disney"]
```

**Controller Manager**: "원하는 상태"와 "현재 상태"를 비교해서 **직접 행동**하는 자동화 시스템. DataDog/NewRelic(보고만 하는 모니터링)과 달리 직접 복구까지 수행:
- Deployment Controller: "Triton Pod 3개 항상 유지" → Pod 죽으면 자동 재생성
- Node Controller: Node 응답 없음 → "Node 다운" 판정 → Pod 재스케줄링
- Job Controller: 일회성 작업 완료/실패 시 정리/재시도

K8s 대시보드: Controller Manager 자체에는 없지만, Kubernetes Dashboard(공식), Lens(데스크톱 앱), Rancher(관리 플랫폼), Grafana+Prometheus(메트릭 대시보드) 등을 사용.

**etcd**: K8s 클러스터의 모든 상태 정보를 저장하는 분산 키-값 데이터베이스.

###### Worker Nodes 구성요소

Worker Node = 실제 일하는 서버. AWS에서는 EC2 인스턴스, 온프레미스에서는 물리 GPU 서버.

**kubelet**: 각 Worker Node의 에이전트. Control Plane으로부터 "이 Pod를 올려라" 명령을 받아 컨테이너를 실행하고 상태를 관리하며 보고. FastAPI의 uvicorn(프로세스 매니저)과 유사.

**kube-proxy**: 각 Worker Node의 네트워크 담당. Pod의 IP가 생성/삭제마다 바뀌는 문제를 해결하기 위해 K8s "Service"(고정 주소) → 실제 Pod로의 트래픽 전달을 관리. nginx 리버스 프록시의 upstream 자동 업데이트와 유사.

###### Pod 상세

- 90% 이상은 **1 Pod = 1 Container**
- Pod 1개에 Container N개 = "사이드카 패턴": 메인 컨테이너 + 보조 컨테이너(로그 수집 Fluentd, 네트워크 프록시 Envoy 등)
- Container Runtime: containerd(현재 기본), CRI-O 등. Docker 이미지 호환.

###### Node 구성 예시

GPU 서버 1대 (CPU 2개 + GPU 8개) = K8s Node 1개:
```
Node (GPU 서버)
├─ Pod A: Triton 서버 (GPU 0번 사용) ← AI 추론
├─ Pod B: Triton 서버 (GPU 1번 사용) ← AI 추론
├─ Pod C: FFmpeg 워커 (GPU 2번의 NVENC 사용) ← 영상 인코딩
├─ Pod D: 전처리 워커 (CPU만 사용) ← 프레임 분할/정규화
└─ GPU 3~7: 비어있음 (새 작업 대기)
```

- **FFmpeg 워커**: 영상/오디오 변환 오픈소스 도구를 실행하는 컨테이너. 영상 디코딩(프레임 분리), 인코딩(프레임→영상 합성), 포맷 변환, 오디오 머지 등 수행.
- **전처리 워커**: AI 추론 전에 데이터를 준비하는 컨테이너. 프레임 분할, 리사이즈, 정규화(픽셀값 0-255→0-1), 배치 구성 등. GPU 불필요 → CPU만 사용하여 GPU 자원 절약.

###### Namespace — 논리적 분리 단위

Namespace = K8s 클러스터 안에서의 논리적 파티션. 같은 Node(서버) 위에 다른 Namespace의 Pod가 공존 가능:

```
Node1: [disney-triton-1] [kbs-triton-1] [disney-ffmpeg-1]
Node2: [disney-triton-2] [kbs-triton-2] [kbs-ffmpeg-1]
Node3: [disney-triton-3] [kbs-triton-3]
→ 디즈니 Pod가 3개 Node에 분산! Node1 죽어도 나머지에서 계속 동작
```

한 Node에 특정 고객 Pod를 몰아넣지 않는 이유: Node 다운 시 해당 고객 서비스 전체 장애. 여러 Node에 분산하여 가용성 확보.

Namespace의 목적:
1. 접근 분리: kubectl로 해당 Namespace만 볼 수 있는 권한
2. 리소스 제한: ResourceQuota를 Namespace 단위로 적용
3. 네트워크 격리: NetworkPolicy로 Namespace 간 통신 차단
4. 이름 충돌 방지: `disney/triton-pod`와 `kbs/triton-pod` 공존 가능
5. 관리 편의: `kubectl delete namespace disney` = 디즈니 관련 전체 리소스 삭제

###### ResourceQuota — Namespace에 붙이는 자원 제한

Namespace = "방"(공간 분리), ResourceQuota = "방에 붙인 규칙표"(자원 제한). Namespace 없이 ResourceQuota만 쓸 수 없다.

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: disney-quota
  namespace: disney          # 이 Namespace에 적용
spec:
  hard:
    nvidia.com/gpu: "2"     # GPU 최대 2개
    cpu: "8"                # CPU 최대 8코어
    memory: "32Gi"          # 메모리 최대 32GB
```

멀티테넌트에서의 실제 배치 (서버를 고객별로 고정하지 않음):
```
모든 서버(1~8)는 공유 풀. 어떤 고객의 Pod든 어떤 서버에든 올라갈 수 있음.
ResourceQuota로 "최대 사용량"만 제한.

설정: 디즈니 GPU 최대 12개 / KBS GPU 최대 12개 (전체 64개)

KBS 폭주 시:
  서버1: [디즈니Pod] [디즈니Pod] [KBSPod] [KBSPod] [KBSPod] ...
  서버2: [KBSPod] [KBSPod] [KBSPod] [KBSPod] ...
  → KBS가 최대 12개 GPU까지 사용 (한도 내)
  → 디즈니 Pod는 영향 없이 계속 동작
```

K8s Scheduler가 각 Node의 GPU 사용 현황을 추적하고, 새 Pod를 빈 GPU 있는 Node에 **자동** 배치한다.

###### NVIDIA GPU Operator

K8s는 원래 CPU/메모리만 관리 가능. GPU Operator를 설치하면 GPU 드라이버, CUDA 라이브러리를 자동 설치하고, K8s에 "이 Node에 GPU N개 있음"을 등록하여 Pod에 GPU를 선언적으로 할당/해제할 수 있게 된다.

###### K8s를 쓰는 이유: 단순 배포 편의 이상

K8s 없이 16대 GPU 서버(128 GPU)를 운영하면: SSH로 16대 각각 접속해 배포, 장애 감지/재시작 로직 직접 구축, GPU 사용 현황 수동 추적, 멀티테넌트 격리 수동 관리, 모델 업데이트 16대 반복.

K8s = **배포 + 자동 장애복구 + GPU 리소스 최적 배치 + 멀티테넌트 격리 + 무중단 업데이트를 통합한 "분산 시스템 운영체제"**.

###### HPA (Horizontal Pod Autoscaler): 온프레미스에서의 오토스케일링

```
클라우드: 요청 증가 → 서버 자체를 새로 만듦 (EC2 추가)
온프레미스: 요청 증가 → 기존 서버 안에서 Pod(컨테이너)를 더 띄움
           물리 서버는 그대로! 빈 GPU가 있는 한 Pod 추가 가능

예시 (GPU 서버 4대, 각 8GPU = 32개):
  평상시: Triton Pod 8개 = GPU 8/32개 사용
  폭주 시: HPA가 Pod 24개로 확장 = GPU 24/32개 사용
  야간: HPA가 Pod 4개로 축소 = GPU 4/32개 사용
```

온프레미스 유휴 자원 관리: 피크(78% 활용) vs 야간(16% 활용)으로 평균 ~50%. 완전한 낭비를 줄이는 방법: 야간 배치 작업(P2) 활용, 유휴 GPU로 모델 학습, 단계적 서버 증설.

###### Pod 생명주기: 상주 Pod vs Job

영상 처리 워크로드에서 두 가지 방식 모두 유효:

```
방식 1: 상주 Pod (uvicorn worker 스타일)
  Triton Pod 8개 항상 실행 → 요청 오면 처리 → Pod 유지
  ✅ 모델 로딩 반복 없음 ✅ 즉시 응답
  ❌ GPU 항상 점유 (작업 없어도)

방식 2: Job Pod (배치 작업 스타일)
  작업 들어오면 Pod 생성 → 처리 → 종료 → GPU 반환
  ✅ 유휴 시 GPU 반환 (다른 작업 활용)
  ❌ Pod 시작 + 모델 로딩 시간 (30초~수분, 영상 30분 처리 대비 무시 가능)
```

uvicorn worker 비유: Triton Pod을 상주시키고 요청을 라우팅하는 방식은 완전히 유효한 아키텍처.

| GPU 규모 | 추천 방식 | 이유 |
|----------|---------|------|
| **4~8대** | **상주 (Deployment)** | 단순, 관리 쉬움 ← **소규모 추천** |
| 16대+ | Job 또는 혼합 | GPU 활용률 최적화 |
| 100대+ | 정교한 스케줄러 필수 | Netflix/Meta급 |

###### 🆕 K8s Ingress / Egress — 두 가지 맥락

K8s에서 "Ingress/Egress"는 두 가지 완전히 다른 곳에서 쓰인다:

**① Ingress 리소스** = 클러스터의 "정문" (외부→내부 HTTP 라우팅)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
spec:
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /upload
        backend:
          service: { name: upload-svc, port: { number: 8080 } }
  tls:
  - hosts: [api.example.com]
    secretName: app-tls-cert
```

Ingress 리소스 = 안내판(규칙), **Ingress Controller**(NGINX 등) = 안내하는 경비원(실행). 온프레미스에서는 NGINX Ingress Controller이 자연스러운 선택.

**② NetworkPolicy Ingress/Egress** = Pod 레벨 "방화벽"

```yaml
# 디즈니 Triton Pod: disney namespace에서만 접근 허용, 인터넷 차단
spec:
  podSelector: { matchLabels: { app: triton } }
  policyTypes: [Ingress, Egress]
  ingress:
  - from:
    - namespaceSelector: { matchLabels: { tenant: disney } }
  egress:
  - to:
    - namespaceSelector: { matchLabels: { tenant: disney } }
  - to:
    - ipBlock: { cidr: 10.0.50.0/24 }  # BeeGFS만 허용
```

- Ingress 규칙: "이 Pod에 누가 접근할 수 있나" (교실 입장 규칙)
- Egress 규칙: "이 Pod가 어디에 접근할 수 있나" (교실 외출 규칙)
- 멀티테넌트 격리: disney Pod가 kbs Pod에 접근 불가 → 미공개 영상 유출 방지

**③ Egress Fee** = 클라우드 비용 맥락 (NetworkPolicy와 별개)

데이터가 클라우드 밖으로 나갈 때 부과되는 요금. AWS egress 1PB 시 $50,000+/월 → 영상 AI 스타트업이 온프레미스를 선택하는 이유 중 하나.

| 개념 | 역할 | 활용 예시 |
|------|------|------------|
| Ingress Resource | 외부→내부 HTTP 라우팅 | API/대시보드 접근 |
| Ingress Controller | Ingress 규칙 실행 엔진 | NGINX Ingress |
| NetworkPolicy Ingress | Pod 들어오는 트래픽 제어 | 테넌트 간 격리 |
| NetworkPolicy Egress | Pod 나가는 트래픽 제어 | 데이터 유출 방지 |
| Egress Fee | 클라우드 아웃바운드 비용 | 온프레미스 선택 이유 |

###### 🆕 NVIDIA Triton Inference Server 상세

**Triton** = AI 모델 서빙 전용 서버. 모델 파일만 올려두면 HTTP/gRPC API 자동 생성 + Dynamic Batching + GPU 관리.

| 항목 | FastAPI | Triton |
|------|---------|--------|
| 용도 | 범용 웹 API | ML 모델 서빙 전용 |
| API | 직접 코딩 | **모델 올리면 자동 생성** |
| GPU 관리 | 직접 `cuda:0` | 설정 기반 자동 할당 |
| 배칭 | 직접 구현 | Dynamic Batching 내장 |
| 프레임워크 | PyTorch만 | PyTorch + TF + ONNX + TensorRT |

```
모델 폴더 구조:
model_repository/
└── super_resolution/
    ├── config.pbtxt
    └── 1/model.plan

서버 시작: $ tritonserver --model-repository=/models
→ 자동 생성 API:
  POST /v2/models/super_resolution/infer
  GET  /v2/models/super_resolution
```

**GPU 관리 = K8s + Triton 2단계 구조**:
- 1단계 (K8s): 스케줄러 + NVIDIA Device Plugin이 "Pod A에 GPU 0번 배정"
- 2단계 (Triton): config.pbtxt의 `instance_group`에서 할당된 GPU 내 모델 인스턴스 관리

```protobuf
instance_group [
  { count: 2, kind: KIND_GPU, gpus: [0, 1] }
]
```

⚠️ Triton은 "놀고 있는 GPU를 자동 탐지"하는 것이 아니라 **설정 기반 할당**. 빈 GPU 탐지와 할당은 K8s 스케줄러의 역할.

##### F. 왜 온프레미스인가? AWS와의 비용 비교

```
☁️ AWS (p4d.24xlarge, A100 8개 × 4대):
  월: 4 × $32.77/hr × 24h × 30d = $94,454 (약 1.2억원/월)
  연: 약 14.4억원
  + 영상 데이터 전송 비용 (egress fee): 1PB 시 $50,000+/월

🏠 온프레미스:
  초기 구매: ~$600K (약 8억원, 1회성)
  월 운영 (전기/냉각/관리): ~$5K (약 650만원/월)
  연 운영: 약 0.8억원

  손익분기: 약 8~12개월
```

영상 AI 스타트업의 온프레미스 선택 이유:
1. **💰 비용**: 24시간 GPU 가동 워크로드에서 압도적으로 저렴
2. **📦 데이터 전송 비용**: 영상 1편 50~500GB, AWS egress fee 월 수천만원
3. **🔒 보안**: "우리 서버에서 처리" = 영업 시 유리
4. **⚡ 성능 예측 가능성**: 고객에게 처리 시간 보장 가능

##### 🆕 G. 프레임 레벨 vs 세그먼트 레벨 분할 + 제로카피 파이프라인

###### 두 가지 분산 처리 접근법

```
방식 A: 프레임 레벨 분할
  전체 디코딩(NVDEC/CPU) → raw 프레임 → CPU에서 청킹/정규화 → 각 GPU로
  ❌ 제로카피 깨짐 (GPU→CPU→GPU 왕복)
  ✅ 해상도별 배치 그룹핑, 세밀한 제어

방식 B: 세그먼트 레벨 분할
  H.264 스트림을 I-frame 기준으로 시간 구간 분할 → 각 GPU에 segment 배분
  각 GPU: NVDEC → CUDA 전처리(정규화) → AI 추론 → NVENC
  ✅ 제로카피 유지 (GPU 내부에서 전부 처리)
  ⚠️ I-frame 경계 필수, 세밀한 프레임 제어 제한적
```

```
세그먼트 레벨 분할 (L40S 제로카피):

FFmpeg (CPU): demux + H.264 세그먼트 분할 (I-frame 기준)
       ↓              ↓              ↓
  GPU 0 (L40S)   GPU 1 (L40S)   GPU 2 (L40S)
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │ NVDEC    │  │ NVDEC    │  │ NVDEC    │
  │→ CUDA    │  │→ CUDA    │  │→ CUDA    │ ← 정규화(GPU 내)
  │  정규화  │  │  정규화  │  │  정규화  │
  │→ AI추론  │  │→ AI추론  │  │→ AI추론  │
  │→ NVENC   │  │→ NVENC   │  │→ NVENC   │
  └──────────┘  └──────────┘  └──────────┘
       ↓              ↓              ↓
FFmpeg (CPU): 세그먼트 concat + 오디오 머지 → 최종 MP4
```

###### 제로카피의 조건과 한계

| 항목 | 프레임 레벨 (A) | 세그먼트 레벨 (B) |
|------|----------------|-------------------|
| 분할 시점 | 디코딩 후 | 디코딩 전 |
| 전처리 위치 | CPU 워커 | GPU CUDA 커널 |
| 제로카피 | ❌ | ✅ |
| 적합 GPU | A100 (NVENC 없음) | **L40S** (NVENC/NVDEC 내장) |

⚠️ **A100은 NVENC 0개**이므로 인코딩을 CPU로 해야 → 제로카피 파이프라인 자체가 불가능 → 프레임 레벨 분할이 자연스러운 선택.

💡 정규화(`pixel/255.0`)는 간단한 CUDA 커널로 GPU 내에서 수행 가능. CPU로 빼면 제로카피가 깨진다.

###### L40S에서 FFmpeg 워커 분리 여부

L40S 사용 시 별도 FFmpeg GPU 워커 Pod는 **불필요**:
- FFmpeg 소프트웨어 자체: ✅ 여전히 필요 (demux/mux/오디오)
- FFmpeg "CPU 인코딩": ❌ 불필요 (NVENC이 대체)
- 별도 FFmpeg GPU 워커 Pod: ❌ 불필요 (Triton Pod에 통합)

예외: 고객마다 다른 인코딩 옵션, 인코딩만 폭주, A100 사용 시 → 분리 유리

**핵심 문장**: "L40S에서는 H.264 세그먼트 레벨 분할 후 각 GPU가 NVDEC→CUDA 전처리→AI 추론→NVENC을 제로카피로 일괄 처리합니다. CPU는 demux/세그먼트 분할과 최종 concat/mux만 담당합니다."

###### 🆕 오디오 향상 파이프라인 (확장)

비디오만 4K로 올리는 게 아니라 오디오 품질도 함께 높인다면, 병렬 분기 파이프라인:

```
MP4 → demux
  ├── 🎥 비디오 → [Video AI: 업스케일링] → 4K 프레임들 ─┐
  └── 🔊 오디오 → [Audio AI: 음질 향상] → 고품질 오디오 ─┤→ mux → 최종 MP4
```

| 오디오 AI 작업 | 모델 예시 | 설명 |
|---------------|----------|------|
| 노이즈 제거 | DeepFilterNet, DTLN | 배경 소음 제거 |
| 업샘플링 | AudioSR, NVSR | 16kHz → 48kHz |
| 음성 분리 | Demucs (Meta) | 보컬/악기 분리 |
| 공간 오디오 | - | 스테레오 → 서라운드 |

오디오 AI 모델은 비디오보다 훨씬 가볍다 (파라미터 1/10 이하). 같은 GPU에서 MPS로 동시 실행 가능.

##### 🆕 H. RBAC — 역할 기반 접근 제어

```
RBAC = Role-Based Access Control = 역할(Role)에 따라 접근(Access)을 제어(Control)
```

비유: 🏢 회사 출입카드 시스템. "사람"이 아니라 "역할(직급)"에 권한을 부여. 김사원이 팀장으로 승진하면 카드만 바꾸면 됨.

영상 AI 플랫폼 RBAC (3단계):

| 역할 | 할 수 있는 것 | 대상 |
|------|-------------|------|
| **Admin** | 모든 것 (사용자 관리, 시스템 설정, GPU 할당) | 플랫폼팀 리드 |
| **Operator** | 작업 실행, 모니터링, 로그 조회 | 운영 담당자 |
| **Viewer** | 작업 상태 조회, 결과물 다운로드 | 고객사 |

K8s에서의 RBAC 예시:

```yaml
kind: Role
metadata:
  namespace: disney
  name: disney-viewer
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]  # 조회만 가능
---
kind: RoleBinding
metadata:
  namespace: disney
subjects:
- kind: User
  name: disney-user
roleRef:
  kind: Role
  name: disney-viewer
```

##### 🆕 I. Model Registry(MLflow)와 Triton의 관계

###### Triton = 폴더에서 모델 로드

```
/models/
├── super_resolution/
│   ├── 1/model.plan        ← 버전 1
│   ├── 2/model.plan        ← 버전 2
│   └── config.pbtxt        ← 모델 설정
```

Triton은 Model Registry 없이도 동작한다. 폴더에 모델 파일만 있으면 됨.

###### MLflow = 모델의 이력 관리

비유: MLflow = 📚 도서관 카탈로그 (어떤 책이 있는지, 저자, 판번 관리), Triton Model Repository = 📖 책꽂이 (실제 책이 꽂혀있는 곳).

MLflow가 필요한 시점: 모델 여러 개 + 자주 업데이트 + AI 연구팀이 모델 전달 + 롤백 필요.

K8s에 배포하면: MLflow Pod(replica:2, stateless) + PostgreSQL(메타데이터) + MinIO(모델 파일).

###### Git vs MLflow vs DVC 비교

| | Git + CI/CD | DVC | MLflow |
|---|---|---|---|
| 모델 파일 저장 | ❌ 100MB 제한 | ✅ 외부 스토리지 + .dvc 포인터 | ✅ S3/MinIO |
| 실험 비교 | ❌ | 🟡 제한적 | ✅ 웹 UI |
| 인프라 부담 | ✅ 없음 | ✅ 낮음 | ❌ 서버 운영 |
| 적합한 경우 | 모델 1-2개 | Git 워크플로우 유지 + 대용량 | 실험 활발, 팀 협업 |

##### 🆕 J. 모델 배포 파이프라인 (안전한 방식)

```
AI팀이 MLflow에서 "Production" 태그
    │
    ▼ (Webhook 또는 수동 트리거)
배포 서비스
    ├── 1. staging dir에 다운로드
    │      mlflow.artifacts.download_artifacts(dst_path="/models/.staging/...")
    ├── 2. 체크섬 검증
    ├── 3. config.pbtxt 생성 (MLflow↔Triton 구조 변환)
    ├── 4. atomic rename으로 model repository에 배치
    │      mv /models/.staging/super_resolution/3 /models/super_resolution/3
    └── 5. Triton explicit load API 호출
           POST /v2/repository/models/super_resolution/load
```

BeeGFS 공유 스토리지이므로, 파일 1번만 넣으면 모든 Triton Pod에서 접근 가능.

⚠️ **프로덕션 주의사항** (수렴 검증 확인):
- **poll 모드 비권장**: Triton 공식 문서에서 프로덕션 비권장. **explicit 모드 + load API** 사용
- **partial write 방지**: staging dir → atomic rename 패턴 필수
- **디렉토리 구조 불일치**: MLflow artifact 구조 ≠ Triton 구조. config.pbtxt 생성 + 버전 폴더 매핑 필요
- **MLflow stages deprecated**: MLflow 2.9+에서 stages→aliases/tags 전환 중

##### 🆕 K. 모델 롤백 전략

청크 분할 + 체크포인팅으로 롤백 비용 최소화:

```
롤백 시:
├── 청크 1-2: ✅ v2로 완료 → 유지
├── 청크 3: ❌ v3 처리 중 → 버리고 v2로 재처리
└── 청크 4+: ⏳ v2로 처리
```

⚠️ **주의사항**: load/unload 시 수 초~수십 초 다운타임 발생. multi-version 로드로 최소화. 청크 경계에서 화질 불연속 가능성 있으므로 확인 필요.

##### 🆕 L. 워크플로우 엔진 선택

###### 현 규모(GPU 4-8대, 팀 3-5명): Celery + Redis 권장

수렴 검증 결과, Temporal은 이 규모에서 과잉. 워크플로우가 선형(분기 없음)이고 중간 복구는 DB 컬럼+if문으로 충분.

| | Celery + Redis | Temporal |
|---|---|---|
| 상태 관리 | DB 테이블 1개 | Temporal Server 내장 |
| 중간 복구 | `current_step` 기반 재개 | 워크플로우 리플레이 |
| 운영 컴포넌트 | 2개 (Redis, worker) | 3-4개 (Server, DB, ES 등) |
| 적합 규모 | GPU 4-8대 | 동시 워크플로우 수백+ |

Temporal 정당화 조건: 동시 워크플로우 수백 개+, 조건부 경로 3개 이상, 전담 인력 확보.

**핵심 답변 포인트**: "Temporal을 검토했지만, 현 규모에서는 운영 비용 대비 이점이 부족합니다. 파이프라인이 복잡해지면 재검토합니다."

###### Temporal 동작 원리 (참고)

```python
# FastAPI에서 워크플로우 시작
handle = await temporal_client.start_workflow(UpscaleWorkflow.run, args=[video_id])

# workflow.py — "무엇을 할지" (순서)
async def run(self, video_id):
    await execute_activity(validate_video, video_id)
    chunks = await execute_activity(split_frames, video_id)
    for chunk in chunks:
        await execute_activity(ai_inference, chunk)  # Triton 호출은 activity 안에서
    await execute_activity(merge_frames, results)

# activities.py — "어떻게 할지" (Triton gRPC 호출)
async def ai_inference(chunk):
    result = triton_client.infer(model_name="super_resolution", inputs=[inputs])
```

비유: workflow.py = 🍳 레시피, activities.py = 실제 요리, Triton = 프라이팬.

##### 🆕 M. Pod 구성

###### Sidecar 패턴 (현 규모 권장)

수렴 검증 결과, CPU Worker와 Triton의 독립 스케일링 이점이 미미. Sidecar로 같은 Pod에 배치하는 것이 더 단순.

```
Pod (GPU 노드 1개당 1 Pod):
├── Container 1: Worker (전처리/후처리 + Triton 호출)
└── Container 2: Triton Server (GPU 추론)
    └── 통신: localhost:8001 (gRPC) — 네트워크 홉 제거
```

| 항목 | 분리 구조 | Sidecar (권장) |
|------|-----------|---------------|
| 네트워크 | Pod간 gRPC | localhost |
| 스케일링 | 2개 HPA | 1개 HPA |
| 장애 전파 | Worker가 죽은 Triton에 계속 요청 | 함께 재시작 |

분리 정당화 조건: Triton을 중앙 추론 플랫폼으로 공유, GPU 50대+.

###### 전체 Pod 목록

| Pod | 역할 | GPU? | replica |
|-----|------|------|---------|
| FastAPI | API 접수 | ❌ | 2 |
| Worker + Triton (Sidecar) | 전처리/추론/후처리 | ✅ | 8 |
| MLflow | 모델 관리 | ❌ | 2 |
| PostgreSQL | 메타데이터 | ❌ | 2 (이중화) |
| MinIO | 모델/영상 파일 | ❌ | 3 |
| Prometheus + Grafana + DCGM | 모니터링 | ❌ | 1+1+1 |
| Ingress Controller | 외부 트래픽 | ❌ | 2 |

##### 🆕 N. 수렴 검증 — 수렴 검증 수정 포인트

5개 Agent(RESEARCHER, CONTRARIAN, ARCHITECT, SIMPLIFIER, EVALUATOR)에 의한 수렴 검증 결과:

| 기존 답변 | 수정 방향 |
|-----------|----------|
| Triton poll 모드로 자동 감지 | **explicit 모드 + load API** |
| download_artifacts로 직접 다운로드 | **staging dir → atomic rename** |
| Temporal로 워크플로우 관리 | **현 규모에서는 Celery + Redis** |
| CPU Worker와 Triton 분리 | **Sidecar 패턴** |
| Triton에 HTTP 요청 | **gRPC 사용** |
| 모니터링 언급 없음 | **Prometheus + Grafana + DCGM 필수** |

**관통 원칙**: "설계 결정은 현재 규모의 실제 문제를 기준으로 합니다. 미래 규모의 가상 문제가 아닙니다. 단, 전환 경로는 항상 열어둡니다."

---

### Q2. Docker 기반으로 AI 추론 서비스를 운영할 때, Kubernetes와 Docker Compose 중 어떤 것을 선택하시겠습니까?

**학습 포인트**: Docker/Kubernetes 기반 운영

#### 모범답변

**핵심 요약**: 현재 규모(GPU 서버 4-8대)에서는 Kubernetes를 선택합니다. 다만, 초기 MVP 단계에서는 Docker Compose로 빠르게 시작하고 점진적으로 마이그레이션하는 전략이 현실적입니다.

| 비교 기준 | Docker Compose | Kubernetes |
|-----------|---------------|------------|
| 설정 복잡도 | ⭐ 낮음 | ⭐⭐⭐ 높음 |
| GPU 스케줄링 | ❌ 수동 | ✅ NVIDIA GPU Operator |
| 자동 복구 | ❌ 없음 | ✅ Pod 자동 재시작 |
| 수평 확장 | ❌ 어려움 | ✅ HPA/VPA |
| 멀티테넌트 | ❌ 미지원 | ✅ Namespace 격리 |
| 롤링 업데이트 | ❌ 수동 | ✅ 자동 |
| 학습 곡선 | 낮음 | 높음 |
| 적합 규모 | 1-2대 | 3대+ |

**Kubernetes 선택 근거**:
1. **GPU 리소스 관리**: NVIDIA GPU Operator + Device Plugin으로 GPU를 K8s 리소스로 선언적 관리. MIG 파티셔닝도 K8s 레벨에서 지원.
2. **멀티테넌트 필수**: 고객 단위 데이터 격리가 핵심 업무. K8s Namespace + NetworkPolicy로 자연스럽게 구현.
3. **자동 장애 복구**: GPU 서버 장애 시 Pod 자동 재스케줄링. 영상 처리는 장시간 작업이므로 중단 없는 운영 중요.
4. **온프레미스 K8s 배포**: kubeadm 또는 RKE2(Rancher)로 배어메탈에 직접 설치. 클라우드 의존성 없음.

**마이그레이션 전략** (스타트업 현실 반영):
```
Phase 1 (MVP, 1-2개월): Docker Compose로 빠른 프로토타이핑
Phase 2 (검증 후): K8s 클러스터 구축 (kubeadm/RKE2)
Phase 3 (운영 안정화): GPU Operator, 모니터링, 자동 스케줄링 추가
```

> **출처**: [NVIDIA GPU Operator Documentation](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/overview.html), [vCluster Multi-tenant GPU](https://www.vcluster.com/blog/isolating-workloads-multitenant-gpu-cluster)

**예상 꼬리질문**:
- "K8s 없이 GPU 스케줄링을 구현해야 한다면 어떻게 하시겠습니까?"
- "온프레미스 K8s에서 etcd 백업/복구 전략은?"

---

#### 📝 Q2 심화 학습 노트: 꼬리질문 답변 + 개념 정리

##### A. K8s 없이 GPU 스케줄링 — RabbitMQ + Celery 접근법

###### 기본 아이디어

GPU 서버 1대에 GPU 8개가 있다면, **worker를 8개 띄우고 GPU 처리가 필요한 큐를 바라보게 하면 자연스럽게 GPU 스케줄링이 된다.** RabbitMQ가 라운드로빈으로 작업을 자동 분배하고, 각 worker는 `CUDA_VISIBLE_DEVICES`로 자기 GPU만 사용한다.

```bash
# GPU 8개 서버에서 worker 8개를 하나의 큐에 연결
CUDA_VISIBLE_DEVICES=0 celery -A app worker -Q gpu_tasks -c 1 -n worker0@%h
CUDA_VISIBLE_DEVICES=1 celery -A app worker -Q gpu_tasks -c 1 -n worker1@%h
CUDA_VISIBLE_DEVICES=2 celery -A app worker -Q gpu_tasks -c 1 -n worker2@%h
# ... (8개)
```

비유: 🍔 햄버거 가게에 주문 창구 1개 + 요리사 8명. 주문이 들어오면 **놀고 있는 요리사가 알아서 가져감**.

###### Celery 실행 옵션 breakdown

```bash
CUDA_VISIBLE_DEVICES=0 celery -A app worker -Q gpu_tasks -c 1 -n worker0@%h
```

| 부분 | 의미 | 비유 |
|------|------|------|
| `CUDA_VISIBLE_DEVICES=0` | 이 프로세스는 GPU 0번만 보인다 (나머지 GPU는 숨김) | 🙈 "눈가리개" — 요리사가 자기 화구만 볼 수 있게 |
| `celery` | Celery 프로그램 실행 | - |
| `-A app` | `app`이라는 Python 모듈에서 Celery 앱 설정을 불러옴 | 📋 "업무 매뉴얼 위치" |
| `worker` | Celery의 worker 모드로 실행 (큐에서 작업을 가져와 처리) | 👷 "요리사 역할로 출근" |
| `-Q gpu_tasks` | `gpu_tasks` 큐만 바라봄 | 📬 "이 우체통에서만 편지 가져감" |
| `-c 1` | concurrency = 1 (동시에 1개 작업만 처리) | ☝️ "한 번에 하나만" |
| `-n worker0@%h` | worker 이름 지정 (`%h`는 호스트명 자동 삽입) | 🏷️ "이름표 달기" |

**`-c 1`이 중요한 이유**: GPU는 한 작업이 VRAM 대부분을 점유한다. `-c 2`로 설정하면 두 작업이 동시에 VRAM을 요구하여 OOM(Out of Memory) 에러 발생.

```
-c 2: 작업A(VRAM 40GB) + 작업B("나도 필요해!") → 💥 OOM!
-c 1: 작업A(완료→반환) → 작업B(시작) → ✅ 정상
```

비유: 🛁 욕조에 물 가득 채워서 쓰는 중인데, 다른 사람이 또 물 틀면 넘침 → 한 번에 한 명만!

###### 요구사항에 따른 큐 확장

기본은 **단일 큐 + 다중 worker**. 요구사항이 생기면 큐를 늘리면 된다. 전부 같은 "큐 + worker" 패턴의 연장선이다.

```
Case 1: GPU 동일 스펙, 격리 불필요
  → gpu_tasks 큐 1개 + worker 8개 ✅

Case 2: GPU 스펙 섞임 (L40S + A100)
  → l40s_tasks 큐 + a100_tasks 큐 (2개)
  → L40S worker 4개, A100 worker 4개
  → 여전히 "큐 + worker" 패턴 ✅

Case 3: 고객 격리
  → disney_tasks 큐 + kbs_tasks 큐
  → 전용 worker 배정
  → 여전히 같은 패턴 ✅
```

###### K8s와의 비교

| 항목 | RabbitMQ + Celery | K8s |
|------|-------------------|-----|
| 설정 복잡도 | ✅ 낮음 (이미 아는 스택) | ❌ 높음 |
| GPU 할당 | ✅ CUDA_VISIBLE_DEVICES + 큐 | ✅ GPU Operator 자동 |
| 자동 복구 | ❌ supervisord/systemd 수동 | ✅ Pod 자동 재시작 |
| 멀티테넌트 | 🟡 큐 분리로 가능 | ✅ Namespace 격리 |
| MIG 관리 | ❌ 직접 구현 필요 | ✅ GPU Operator 지원 |
| 적합 규모 | 1-4대 | 4대+ |

###### nvidia-smi — GPU의 "작업관리자"

```
nvidia-smi = NVIDIA System Management Interface
```

컴퓨터에서 작업관리자를 열면 CPU 사용률, 메모리 사용량이 보이듯, **nvidia-smi는 GPU 버전의 작업관리자**다.

```bash
$ nvidia-smi
+-------------------------------------------+
| GPU  Name        | Temp | GPU-Util | Memory     |
|-------------------------------------------+
|  0   L40S        |  65C |    85%   | 40GB/48GB  |  ← 바쁨
|  1   L40S        |  45C |     0%   |  2GB/48GB  |  ← 놀고 있음
|  2   L40S        |  90C |    99%   | 47GB/48GB  |  ← 과열! 위험!
|  3   L40S        |  50C |    30%   | 10GB/48GB  |  ← 여유
+-------------------------------------------+
```

**기본적인 작업 배분(스케줄링)에는 nvidia-smi가 필요 없다.** RabbitMQ + Celery worker만으로 작업 배분은 완벽하게 동작한다.

nvidia-smi가 필요해지는 **추가** 상황들:
- GPU 온도 90도 초과 → 작업 보내면 안 됨 (하드웨어 보호)
- GPU 메모리 누수 → worker가 죽지 않았는데 VRAM이 꽉 참
- GPU 하드웨어 에러 → Xid 에러 감지해서 해당 GPU 제외

즉, nvidia-smi 기반 모니터링은 **"스케줄링"이 아니라 "모니터링/안전장치"**. 프로덕션에서는 권장하지만, 처음부터 필수는 아니다.

###### 핵심 답변 포인트

> "RabbitMQ + Celery worker로 기본 스케줄링을 구현합니다. GPU별 worker를 띄우고 단일 큐에서 경쟁 소비하면 자연스러운 스케줄링이 됩니다. GPU 스펙이 다르거나 고객 격리가 필요하면 큐를 분리합니다. 다만, 서버 4대 이상 또는 MIG 파티셔닝이 필요해지면 K8s 마이그레이션을 권장합니다."

##### B. etcd 백업/복구 전략

###### etcd란?

> "etcd: K8s 클러스터의 **모든 상태 정보**를 저장하는 분산 키-값 데이터베이스"

"설정"뿐 아니라 **K8s의 모든 것**이 저장된다:

```
etcd에 저장되는 것들:
├── Pod 목록과 상태 (어떤 Pod가 어디서 돌고 있는지)
├── Deployment 설정 (Pod 몇 개 유지할지)
├── Service 정보 (네트워크 라우팅 규칙)
├── ConfigMap / Secret (앱 설정값, 비밀번호)
├── Namespace, RBAC 권한 정보
└── 모든 K8s 오브젝트의 현재 상태
```

비유: 🧠 etcd = **K8s의 뇌(기억 장치)**. 공장 관리 시스템의 모든 기록이 담긴 장부. 이 장부가 없어지면 공장 전체 마비.

###### 백업/복구 방법

핵심 도구: `etcdctl` (백업) + `etcdutl` (복구, v3.5+)

**스냅샷 백업**:

```bash
# etcd의 현재 상태를 파일 하나로 "사진 찍기"
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-snapshot-$(date +%Y%m%d).db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
```

비유: 📸 게임 세이브 파일 만들기. "지금 이 순간의 K8s 상태"를 파일로 저장.

**자동화 (CronJob)**:

```bash
# 매시간 자동 백업 + 외부 스토리지로 복사
0 * * * * /usr/local/bin/etcdctl snapshot save /backup/etcd-$(date +\%Y\%m\%d-\%H).db && \
          rsync /backup/ backup-server:/etcd-backups/
```

**복구 (재난 발생 시)**:

```bash
# 1. kube-apiserver 중지
# 2. 스냅샷에서 복구
etcdutl snapshot restore /backup/etcd-snapshot-20260325.db \
  --data-dir=/var/lib/etcd-restored

# 3. etcd 데이터 디렉토리 교체
mv /var/lib/etcd /var/lib/etcd-old
mv /var/lib/etcd-restored /var/lib/etcd

# 4. etcd + kube-apiserver 재시작
```

비유: 🎮 게임 세이브 불러오기. "어제 저녁 상태"로 되돌리기.

주의사항 (2025+ best practice):
- `etcdctl snapshot restore`는 v3.5부터 deprecated → `etcdutl` 사용 권장
- 멀티노드 클러스터: 리더 노드에서 백업, 모든 노드에서 동시 복구
- 백업 파일은 반드시 클러스터 외부(다른 서버, S3 등)에 저장
- 주기적으로 테스트 복구 실행하여 백업 무결성 검증

> **출처**: [Kubernetes 공식 - etcd 운영](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/), [DevOpsCube - etcd 백업 튜토리얼](https://devopscube.com/backup-etcd-restore-kubernetes/), [etcd 공식 - Disaster Recovery](https://etcd.io/docs/v3.5/op-guide/recovery/)

###### 이중화(HA) ≠ 백업 — 목적이 다르다

3노드 이중화하면 자연스럽게 백업되는 것 아닌가? **부분적으로 맞지만 치명적인 차이가 있다.**

```
🔑 이중화(HA) = 집 열쇠를 3개 만듦
   → 1개 잃어버려도 나머지 2개로 집에 들어갈 수 있음 ✅
   → 하지만 "집 자체가 불타면" 열쇠 3개 다 쓸모없음 ❌

📐 백업 = 집 설계도를 은행 금고에 보관
   → 집이 전소해도 설계도로 다시 지을 수 있음 ✅
```

이중화가 백업을 대체하지 못하는 시나리오:

| 시나리오 | 이중화(3노드) | 백업 |
|----------|-------------|------|
| **노드 1대 장애** | ✅ 나머지 2대가 서비스 지속 | 불필요 |
| **실수로 `kubectl delete ns production`** | ❌ **3노드 모두에 즉시 동기화** → 3개 다 삭제됨! | ✅ 스냅샷에서 복구 |
| **etcd 데이터 손상 (버그/디스크)** | ❌ Raft 합의로 **손상 데이터가 3노드에 전파** | ✅ 손상 전 스냅샷으로 복구 |
| **전체 클러스터 장애 (정전/네트워크)** | ❌ 3노드 모두 다운 | ✅ 외부 백업에서 복구 |

Redis Cluster도 같은 문제가 있다:

```
Redis Cluster 3노드:
  ✅ 노드 1대 죽어도 나머지가 처리 → 가용성(Availability)
  ❌ FLUSHALL 실행하면 3노드 모두 데이터 삭제 → 복구 불가
  ❌ 그래서 Redis도 RDB/AOF 백업이 별도로 필요!
```

etcd 데이터가 `/var/lib/etcd`에 파일로 저장되지만, 쓰기 중인 파일을 그냥 `cp`하면 **일관성 없는 상태**가 복사될 수 있다. `etcdctl snapshot save`는 etcd에게 "일관된 시점의 스냅샷"을 요청하여 **일관성 보장된 백업**을 생성한다.

비유: 📝 일기장을 쓰고 있는 도중에 복사기로 복사하면 "쓰다 만 페이지"가 복사돼. `snapshot save`는 "깨끗한 상태에서 복사"하는 것.

**정리**: 이중화는 가용성(Availability), 백업은 내구성(Durability). 목적이 다르므로 둘 다 필요.

```
                    이중화 (3노드)         백업 (스냅샷)
보호 대상:          노드 장애              데이터 장애
보호 범위:          1-2대 죽어도 서비스 지속  실수/손상/전체 장애 복구
비유:              열쇠 여러 개             설계도 금고 보관
Redis 대응:        Redis Sentinel/Cluster   RDB/AOF 백업
목적:              가용성(Availability)     내구성(Durability)
```

---

### Q3. 수천 개의 영상 업스케일링 작업이 동시에 요청될 때, GPU 리소스를 효율적으로 스케줄링하는 시스템을 어떻게 설계하시겠습니까?

**학습 포인트**: AI 추론 워크플로우 및 작업 스케줄링 구조 설계

#### 모범답변

**핵심 요약**: 다단계 큐 시스템 + 우선순위 기반 GPU 스케줄러를 조합합니다. GPU 파티셔닝은 A100 사용 시 MIG, L40S 사용 시 MPS/Time-slicing으로 구분합니다.

```
┌─────────────────────────────────────────────────────────┐
│  고객 요청 (REST API)                                     │
│       │                                                   │
│       ▼                                                   │
│  ┌──────────────┐                                         │
│  │ Job Manager  │ → 작업 분류 + 우선순위 할당              │
│  └──────┬───────┘                                         │
│         │                                                  │
│         ▼                                                  │
│  ┌──────────────────────────────────────┐                  │
│  │      Multi-Level Priority Queue       │                 │
│  │  ┌─────────┐ ┌─────────┐ ┌────────┐ │                 │
│  │  │ P0:긴급  │ │ P1:일반  │ │P2:배치 │ │                 │
│  │  │ (실시간) │ │ (당일)   │ │(야간)  │ │                 │
│  │  └─────────┘ └─────────┘ └────────┘ │                 │
│  └──────────────────┬───────────────────┘                  │
│                      │                                     │
│                      ▼                                     │
│  ┌──────────────────────────────────────┐                  │
│  │         GPU Scheduler                 │                 │
│  │  ┌────────┐  ┌────────┐  ┌────────┐ │                 │
│  │  │GPU 0   │  │GPU 1   │  │GPU 2   │ │                 │
│  │  │MIG 3g  │  │MIG 7g  │  │MIG 7g  │ │                 │
│  │  │+MIG 4g │  │(대작업) │  │(대작업) │ │                 │
│  │  └────────┘  └────────┘  └────────┘ │                 │
│  └──────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

**1) 작업 분류 및 우선순위**:
- **P0 (긴급)**: 고객이 급히 필요한 작업. 즉시 GPU 할당. Preemption 가능.
- **P1 (일반)**: 당일 처리 필요. FIFO + 공정 스케줄링.
- **P2 (배치)**: 야간/주말 처리 가능. 빈 GPU 슬롯 활용.

**2) GPU 파티셔닝 (NVIDIA MIG)**:
- A100 80GB를 MIG로 분할: 예) 3g.40gb + 4g.40gb (소형+중형 작업 동시 처리)
- 영상 해상도별 GPU 요구량이 다름: SD→HD(작음) vs HD→4K(큼) vs 극장용 4K 리마스터(매우 큼)
- 작업 크기에 맞는 MIG 프로파일 자동 매칭

**3) 큐 시스템 구현**:
- **Redis Streams** 또는 **RabbitMQ**: 작업 큐 (내구성, 재시도 지원)
- **Dead Letter Queue**: 3회 실패 시 DLQ로 이동, 관리자 알림
- **Back-pressure**: GPU가 모두 사용 중일 때 새 작업 수용 제한 (429 Too Many Requests)

**4) 공정 스케줄링 (Fair Scheduling)**:
- 고객별 GPU 할당량 (quota) 설정
- Weighted Fair Queue: 프리미엄 고객에게 높은 가중치
- 한 고객이 모든 GPU를 독점하지 않도록 Max-share 제한

**5) 모니터링 및 자동 조정**:
- GPU 사용률 80% 이상 지속 → 알림 + 자동 P2 작업 지연
- GPU 사용률 30% 이하 → MIG 재구성 검토 알림

> **출처**: [MDPI GPU Scheduling Survey 2025](https://www.mdpi.com/1999-4893/18/7/385), [ACM Deep Learning Workload Scheduling Survey](https://dl.acm.org/doi/full/10.1145/3638757), [NVIDIA MIG Documentation](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/)

**예상 꼬리질문**:
- "Preemption이 발생하면 진행 중이던 영상 처리 작업은 어떻게 되나요? 체크포인팅 전략은?"
- "GPU 장애로 작업이 실패했을 때 자동 복구 메커니즘은?"

---

#### 📝 Q3/Q5 통합 심화 학습 노트: 스토리지 역할 분담, 큐 설계, 알림 체계, 보안

##### A. 스토리지 역할 분담: MinIO(외부) vs BeeGFS(내부)

BeeGFS는 POSIX 파일시스템 → HTTP API 없음 → **pre-signed URL 미지원.** 이건 역할 분담이 아니라 **구조적 제약.**

```
MinIO (S3 호환) = 🚪 현관문 (외부 클라이언트 소통, pre-signed URL)
BeeGFS (POSIX)  = 🏭 내부 창고 (GPU 서버 고속 I/O)
```

| | MinIO | BeeGFS |
|---|---|---|
| 프로토콜 | HTTP/S3 | POSIX (mount) |
| 외부 접근 | ✅ | ❌ 내부 전용 |
| pre-signed URL | ✅ | ❌ |
| 용도 | 업로드/다운로드, Cold 아카이브 | GPU 처리 중 고속 I/O |

MinIO가 느린 진짜 이유: "HTTP라서"가 아니라 **"개별 오브젝트 접근 패턴"**. 벌크 읽기면 HTTP여도 빠를 수 있음.

##### B. BeeGFS 병렬 I/O — 왜 빠른가

BeeGFS는 파일을 **청크 단위(수백KB~수MB)**로 여러 서버에 분산 저장(스트라이핑). Worker가 `read()` 하면 커널 모듈이 투명하게 병렬 수신:

```
NFS (서버 1대):   50GB / 1개 디스크+네트워크 = ~1GB/s
BeeGFS (서버 4대): 50GB / 4개 동시 전송     = ~3-10GB/s (구성 의존적)
```

특히 **8대 GPU 서버가 동시에 읽을 때** NFS 1대 vs BeeGFS 4대의 차이가 극명.

⚠️ **BeeGFS 스트라이핑 ≠ 영상 프레임 chunking:**
- 스트라이핑 재조립 → 커널이 투명 처리 (비용 없음)
- 영상 프레임 재조립 → FFmpeg 인코딩 필요 (CPU 비용 있음)

##### C. Cold 스토리지 분리 이유

**핵심은 비용** (엔터프라이즈 NVMe ~$100/TB vs HDD ~$15/TB). 1년 ~1.2PB 기준 약 1.3억원 절약.

부차적 이유: BeeGFS에 파일 수억 개 쌓이면 메타데이터 서버 부하 → ls/find 느려짐 + GPU I/O 영향. MinIO는 lifecycle policy, versioning 등 아카이브 기능 내장.

##### D. Q3 설계 수정 — 앱 레벨 vs 인프라 레벨 스케줄링

Q3 원문에서 "GPU Scheduler"가 큐에서 작업을 직접 가져가는 것처럼 그려져 있었으나, K8s GPU Scheduler(NVIDIA Device Plugin)는 **"Pod를 어떤 Node에 배치할지"** 결정하는 것이지 앱 큐에서 작업을 꺼내는 것이 아님.

```
앱 레벨 스케줄링:    "어떤 작업을 먼저?" → Priority Queue + Consumer Worker
인프라 레벨 스케줄링: "이 Pod를 어떤 Node에?" → K8s Scheduler (배포 시 1번)
```

수정된 흐름:

```
고객 → FastAPI (접수 + 즉시 응답) → Priority Queue (P0/P1/P2)
  → Celery Worker (큐에서 꺼내서 워크플로우 실행) → Triton (GPU 추론)
```

큐 구조는 **단일 선택**: Celery만(현 규모) 또는 Temporal만(확장 시). 둘을 섞으면 큐가 두 겹.

##### E. 영상 업로드/다운로드 — Pre-signed URL

```python
# 업로드: MinIO presigned PUT URL
url = minio_client.presigned_put_object("raw-videos", f"{video_id}/original.mp4", expires=timedelta(hours=2))

# 다운로드: MinIO presigned GET URL (처리 완료 시)
url = minio_client.presigned_get_object("completed-videos", f"{job_id}/output_4k.mp4", expires=timedelta(hours=24))
```

업로드/다운로드 모두 FastAPI 서버를 거치지 않음 (서버 부담 없음). 완성 영상은 BeeGFS → MinIO로 복사 후 URL 생성.

##### F. 알림 체계 — SSE + Webhook + 이메일

| | SSE | Webhook | 이메일 |
|---|---|---|---|
| 받는 주체 | 사람 (브라우저) | 기계 (고객 서버) | 사람 (메일함) |
| 연결 필요 | ✅ 브라우저 열림 | ❌ | ❌ |
| 용도 | 실시간 진행률 | B2B 완료 콜백 | 완료 알림 (가장 넓은 도달 범위) |

**SSE 이벤트 유실 방지 — Last-Event-ID**: SSE 스펙 내장 기능. 브라우저가 재연결 시 Last-Event-ID 헤더를 자동 전달 → 서버가 이벤트를 DB/Redis에 저장 + 해당 ID 이후부터 재전송. job_id별 관리.

**Webhook = HTTP Callback**: 우리 서버가 고객 서버에 POST. 재시도 정책(지수 백오프) + 최대 횟수 초과 시 Dead Letter Queue 필요.

##### G. Webhook 보안 — X-API-Key vs HMAC

```
X-API-Key:  "너 누구야?" (인증만)
HMAC:       "너 누구야?" + "내용 안 바뀌었지?" (인증 + 무결성)
```

HMAC = Hash-based Message Authentication Code = 메시지 + 비밀 키 → 단방향 해시. 비밀 키를 아는 사람만 만들 수 있고, 해시에서 원본/키 복원 불가.

| | X-API-Key + HTTPS | HMAC |
|---|---|---|
| 발신자 확인 | ✅ | ✅ |
| 내용 변조 감지 | ❌ | ✅ |
| 적합한 경우 | 대부분 충분 | 대형 고객 계약, 금융/의료 |

현실적 판단: X-API-Key + HTTPS가 기본, HMAC은 고객 보안 요구사항에 따라 추가.

##### H. 수렴 검증 — 수렴 검증 수정 포인트

| 기존 답변 | 수정 방향 |
|-----------|----------|
| "17만 프레임 MinIO 86분 vs BeeGFS 4분" | **"전제에 따라 33-86분 범위. GPU prefetch로 체감 차이 줄어듦"** |
| "다시 붙이는 비용 없다" | **스트라이핑에만 해당.** 영상 재조립은 인코딩 필요 |
| BeeGFS "바이트 단위" 분산 | **"청크 단위(수백KB~수MB)"** |
| "이메일: 항상 도달" | **"가장 넓은 도달 범위"** (스팸 필터 등 미도달 가능) |
| FCM "서버가 토큰 해제" | **개발자가 수동 구현 필요** (자동 아님) |

---

### Q4. AI 추론 파이프라인에서 동적 배칭(Dynamic Batching)이란 무엇이며, 영상 업스케일링 작업에서 이를 어떻게 구현하시겠습니까?

**학습 포인트**: AI 추론 워크플로우 설계

#### 모범답변

**핵심 요약**: Dynamic batching은 고정 배치 크기 대신, 시간 윈도우 내 도착한 요청을 유동적으로 묶어 GPU 활용률을 극대화하는 기법입니다.

```
Static Batching:          Dynamic Batching:
┌──────────────────┐     ┌──────────────────┐
│ batch=4 고정      │     │ window=100ms     │
│ ████ → GPU       │     │ ██ → GPU (2개)   │  ← 즉시 처리
│ (빈 슬롯 대기)    │     │ ████ → GPU (4개) │  ← 바쁜 시간
│ ████ → GPU       │     │ █ → GPU (1개)    │  ← 한가한 시간
└──────────────────┘     └──────────────────┘
```

**영상 업스케일링에서의 특수성**:

영상 업스케일링은 일반 추론과 다른 특성이 있습니다:

| 특성 | 일반 AI 추론 (텍스트/이미지) | 영상 업스케일링 |
|------|---------------------------|----------------|
| 입력 크기 | 균일 (토큰/고정 이미지) | 가변 (SD 480p ~ HD 1080p) |
| 처리 시간 | ms 단위 | 분~시간 단위 (프레임별) |
| 배칭 단위 | 요청 단위 | **프레임 단위** |
| VRAM 사용 | 예측 가능 | 해상도에 비례하여 가변 |

**구현 전략**:

1. **프레임 레벨 Dynamic Batching**:
   - 영상을 개별 프레임으로 분할 (FFmpeg)
   - 동일 해상도 프레임끼리 배치 그룹핑
   - GPU VRAM 한도 내에서 최대 배치 크기 동적 결정
   ```
   VRAM 예산 산출 (모델 파라미터 + 활성화 맵 + I/O 버퍼 포함):
   - 모델 가중치: ~2-4GB (FP16 SR 모델 기준)
   - 480p 프레임당 활성화 메모리: ~1-2GB → batch=16~24 가능
   - 1080p 프레임당 활성화 메모리: ~4-8GB → batch=4~8 가능
   ※ 정확한 수치는 프로파일링 필수 (nvidia-smi, torch.cuda.memory_summary)
   ※ L40S 48GB / A100 80GB에 따라 최대 batch 크기 달라짐
   ```

2. **NVIDIA Triton Inference Server 활용**:
   - Triton의 Dynamic Batcher 설정:
     ```
     dynamic_batching {
       preferred_batch_size: [4, 8, 16]
       max_queue_delay_microseconds: 100000  # 100ms
     }
     ```
   - 다양한 해상도 입력을 처리하기 위해 패딩 + 마스킹 전략

3. **해상도별 모델 인스턴스 분리**:
   ```
   GPU 0: SD→HD 모델 인스턴스 (작은 VRAM, 빠른 처리)
   GPU 1: HD→4K 모델 인스턴스 (큰 VRAM, 느린 처리)
   ```

4. **TensorRT 최적화**:
   - FP16 정밀도 변환으로 VRAM 50% 절감 + 처리 속도 2-3x 향상
   - Layer fusion, kernel auto-tuning 적용

> **출처**: [BentoML Dynamic Batching Guide](https://bentoml.com/llm/inference-optimization/static-dynamic-continuous-batching), [Baseten Continuous vs Dynamic Batching](https://www.baseten.co/blog/continuous-vs-dynamic-batching-for-ai-inference/), [RunPod CV Pipeline Optimization](https://www.runpod.io/articles/guides/computer-vision-pipeline-optimization-accelerating-image-processing-workflows-with-gpu-computing)

**예상 꼬리질문**:
- "배치 크기가 커지면 레이턴시가 증가합니다. 처리량(throughput)과 레이턴시(latency) 사이 최적점을 어떻게 찾으시겠습니까?"
- "TensorRT의 FP16 변환이 영상 품질에 미치는 영향을 어떻게 측정하시겠습니까?"

---

### Q5. TB~PB 규모의 영상 데이터를 처리하는 파이프라인을 설계할 때, 인제스트(ingestion)부터 최종 딜리버리(delivery)까지의 전체 흐름을 설명해주세요.

**학습 포인트**: TB~PB 확장을 고려한 대용량 영상 데이터 파이프라인 설계

#### 모범답변

**핵심 요약**: 5단계 파이프라인 (Ingest → Validate → Process → Deliver → Archive)을 DAG 기반 워크플로우로 오케스트레이션합니다.

```
┌────────────────────────────────────────────────────────────┐
│              영상 데이터 처리 파이프라인                      │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  1. INGEST         2. VALIDATE       3. PROCESS             │
│  ┌──────────┐     ┌──────────┐     ┌──────────────────┐    │
│  │고객 업로드│ ──→ │무결성 검증│ ──→ │ 전처리 (FFmpeg)   │    │
│  │(SFTP/API) │     │포맷/코덱  │     │ ↓                 │    │
│  │           │     │메타데이터 │     │ 프레임 분할        │    │
│  └──────────┘     └──────────┘     │ ↓                 │    │
│                                      │ AI 추론 (GPU)     │    │
│                                      │ ↓                 │    │
│                                      │ 프레임 합성        │    │
│                                      │ ↓                 │    │
│                                      │ 후처리 (인코딩)    │    │
│                                      └──────────────────┘    │
│                                              │               │
│  5. ARCHIVE        4. DELIVER                │               │
│  ┌──────────┐     ┌──────────┐     ◄────────┘               │
│  │Cold 스토리│ ◄── │고객 전달  │                              │
│  │지로 이동  │     │(다운로드/ │                              │
│  │(30일 후)  │     │ 스트리밍) │                              │
│  └──────────┘     └──────────┘                               │
└────────────────────────────────────────────────────────────┘
```

**각 단계 상세**:

**1) Ingest (인제스트)**:
- 고객이 SFTP 또는 REST API(Presigned URL)로 원본 영상 업로드
- 대용량 파일 전송: **Aspera** 또는 **rclone**으로 고속 전송 (TCP 대비 10-100x)
- 업로드 완료 시 메시지 큐(Kafka)에 이벤트 발행
- 메타데이터 DB(PostgreSQL)에 작업 레코드 생성

**2) Validate (검증)**:
- FFprobe로 코덱, 해상도, 프레임레이트, 길이 확인
- 체크섬(SHA-256) 무결성 검증
- 지원 포맷 확인: ProRes, H.264, H.265, DNxHR
- 실패 시 → 고객에게 알림 + 재업로드 요청

**3) Process (처리)**:
```
원본 영상 (2시간, 1080p, ~50GB)
    │
    ▼ FFmpeg: 프레임 추출
    │ (약 172,800 프레임 @ 24fps)
    │
    ▼ 청크 분할 (1,000 프레임씩)
    │ → 173개 청크로 분할
    │
    ▼ GPU 클러스터에 분산 할당
    │ (각 청크를 별도 GPU 작업으로)
    │
    ▼ AI Super-Resolution 추론
    │ (1080p → 4K 업스케일링)
    │
    ▼ 프레임 합성 + 오디오 머지
    │
    ▼ 최종 인코딩 (H.265/ProRes 4K)
```

- **워크플로우 오케스트레이션**: Temporal 선택 (Airflow 대비 장시간 작업에 강점, 영상 처리는 수시간 소요)
- **청크 단위 체크포인팅**: 각 청크 완료 시 상태 저장 → 장애 시 마지막 청크부터 재시작
- **병렬도 조절**: GPU 가용량에 따라 동적으로 병렬 청크 수 조절

**4) Deliver (전달)**:
- 완료 알림 (Webhook/이메일)
- 고객별 격리된 스토리지 경로에서 다운로드
- 프리뷰 스트리밍 (HLS/DASH) 제공

**5) Archive (아카이브)**:
- 처리 완료 후 30일간 Hot 스토리지 유지
- 이후 Cold 스토리지로 자동 이동 (lifecycle policy)
- 메타데이터는 영구 보존

**스토리지 용량 계산 예시**:
```
영화 1편 (2시간, 4K ProRes): ~500GB
월 100편 처리 시: 원본 50TB + 결과물 50TB = ~100TB/월
1년: ~1.2PB (아카이브 포함)
```

> **출처**: [fal.ai Generative Media Performance](https://fal.ai/learn/devs/gen-ai-performance-optimization), [JISEM Real-Time Video Processing with AI](https://jisem-journal.com/index.php/journal/article/view/6540)

**예상 꼬리질문**:
- "청크 분할 시 프레임 간 temporal consistency를 어떻게 보장하시겠습니까?"
- "파이프라인 중간에 고객이 작업을 취소하면 어떻게 처리하시겠습니까?"

---

### Q6. 온프레미스 환경에서 대용량 영상 데이터를 위한 스토리지 아키텍처를 설계할 때, 어떤 분산 파일시스템을 선택하시겠습니까?

**학습 포인트**: 대용량 데이터 + 확장 전략

#### 모범답변

**핵심 요약**: BeeGFS를 기본 선택으로 권장하되, 규모에 따라 Lustre로 전환을 고려합니다.

| 비교 기준 | BeeGFS | Lustre | Ceph |
|-----------|--------|--------|------|
| **설치/관리** | ✅ 쉬움 | ❌ 복잡 | ❌ 매우 복잡 |
| **순차 I/O** | ✅ 우수 | ✅ 최고 | 🟡 보통 |
| **랜덤 I/O** | 🟡 보통 | 🟡 보통 | ✅ 우수 |
| **확장성** | PB급 | EB급 | EB급 |
| **POSIX 호환** | ✅ 완전 | ✅ 완전 | ✅ 완전 |
| **자동 복구** | ✅ Buddy Mirror | 🟡 수동 | ✅ 자동 |
| **학습 곡선** | 낮음 | 높음 | 높음 |
| **적합 규모** | 10-100TB+ | PB+ | PB+ |
| **커뮤니티** | 중간 | 대규모 (HPC) | 대규모 |

**BeeGFS 선택 근거 (현재 규모)**:
1. **설치/관리 용이성**: 스타트업에서 전담 스토리지 팀 없이도 운영 가능. 초기 소규모 팀 감안.
2. **POSIX 호환**: AI 프레임워크(PyTorch, TensorRT)가 일반 파일 접근으로 데이터를 읽을 수 있음.
3. **파일 스트라이핑**: 대용량 영상 파일을 여러 스토리지 서버에 자동 분산하여 I/O 병렬화.
4. **Buddy Mirroring**: 스토리지 서버 장애 시 자동 복제본으로 서비스 지속 + 자동 self-healing.

**스토리지 아키텍처 (3-Tier)**:
```
┌─────────────────────────────────────────┐
│  Hot Tier (NVMe SSD)                     │
│  • 현재 처리 중인 영상                     │
│  • BeeGFS on NVMe (10-50TB)              │
│  • (참고: GDS는 Lustre/WekaFS에서 지원)   │
├─────────────────────────────────────────┤
│  Warm Tier (HDD RAID)                    │
│  • 최근 30일 완료 작업                     │
│  • BeeGFS on HDD (100TB-1PB)            │
├─────────────────────────────────────────┤
│  Cold Tier (오브젝트/테이프)              │
│  • 아카이브 (MinIO S3-compatible)         │
│  • 30일 이후 자동 이동                     │
└─────────────────────────────────────────┘
```

**Lustre 전환 시점**: 동시 처리 클라이언트 50+대 또는 총 스토리지 500TB+ 도달 시 검토.

> **출처**: [VAST Data Parallel vs Distributed FS](https://www.vastdata.com/blog/parallel-vs-distributed-file-systems-for-hpc), [ACM Lustre Survey 2025](https://dl.acm.org/doi/10.1145/3736583), [BeeGFS at Pomona College HPC](https://ritg.pomona.edu/hpc/beegfs-hpc-storage/)

**예상 꼬리질문**:
- "GPU Direct Storage란 무엇이며, 영상 처리 성능에 어떤 영향을 미칩니까?"
- "스토리지 서버 2대가 동시에 장애나면 BeeGFS Buddy Mirroring으로 어떻게 대응합니까?"

---

### Q7. 여러 콘텐츠 제작사가 동일한 온프레미스 플랫폼을 사용할 때, 고객 간 데이터 격리를 어떻게 보장하시겠습니까?

**학습 포인트**: 고객 단위 데이터 격리 및 보안 아키텍처 설계

#### 모범답변

**핵심 요약**: 3계층 격리(네트워크 + 스토리지 + GPU) + RBAC으로 종합적인 멀티테넌트 보안을 구현합니다.

```
┌─────────────────────────────────────────────────────────┐
│  멀티테넌트 격리 아키텍처                                  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │ Tenant A (방송사) │  │ Tenant B (제작사) │               │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │               │
│  │ │ K8s NS: a   │ │  │ │ K8s NS: b   │ │               │
│  │ │ VLAN: 100   │ │  │ │ VLAN: 200   │ │               │
│  │ │ Path: /a/   │ │  │ │ Path: /b/   │ │               │
│  │ │ GPU: MIG-0  │ │  │ │ GPU: MIG-1  │ │               │
│  │ └─────────────┘ │  │ └─────────────┘ │               │
│  └─────────────────┘  └─────────────────┘                │
│           │                    │                          │
│           ▼                    ▼                          │
│  ┌──────────────────────────────────────┐                 │
│  │     공유 인프라 (물리 서버)            │                │
│  │     + NetworkPolicy + RBAC           │                │
│  │     + Audit Logging                  │                │
│  └──────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────┘
```

**1) 네트워크 격리**:
- **Kubernetes NetworkPolicy**: 테넌트 간 Pod 통신 완전 차단
- **VLAN 분리**: 물리 네트워크 레벨에서 테넌트별 VLAN 할당
- **Ingress 격리**: 테넌트별 API 엔드포인트 분리 또는 API Gateway에서 테넌트 라우팅

**2) 스토리지 격리**:
- **디렉토리 기반 격리**: `/data/{tenant_id}/` 하위에 모든 데이터 저장
- **Linux 권한**: 각 테넌트에 별도 UID/GID 할당, chmod/chown으로 접근 제한
- **암호화**: 저장 시 AES-256 암호화 (at-rest encryption). 테넌트별 별도 암호화 키 (key-per-tenant).
- **삭제 정책**: 고객 이탈 시 데이터 완전 삭제 (crypto-shredding)

**3) GPU 리소스 격리** (GPU 모델에 따라 전략 분기):
- **A100/H100 사용 시 → NVIDIA MIG**: 물리적 GPU를 하드웨어 레벨에서 분리. MIG 파티션 간 메모리 접근 불가. 가장 강력한 격리.
- **L40S 사용 시 → NVIDIA MPS 또는 전용 GPU 할당**: L40S는 MIG 미지원이므로, 보안 민감 고객에게는 전용 GPU(dedicated node) 할당. 일반 고객은 MPS로 GPU 공유.
- **K8s ResourceQuota**: 테넌트별 GPU 할당량 제한

**4) 인증/인가**:
- **RBAC (Role-Based Access Control)**: Admin / Operator / Viewer 3단계 역할
- **API Key + JWT**: 테넌트 식별 및 인증
- **Audit Logging**: 모든 데이터 접근/조작 기록 (who, when, what)

**5) 영상 특화 보안**:
- **DRM 연동**: 고객 요청 시 Widevine/FairPlay DRM 적용
- **워터마킹**: 프리뷰 영상에 비가시 워터마크 삽입 (유출 추적용)
- **전송 암호화**: TLS 1.3 필수

> **출처**: [Introl Multi-tenant GPU Security 2025](https://introl.com/blog/multi-tenant-gpu-security-isolation-strategies-shared-infrastructure-2025), [vCluster GPU Isolation Best Practices](https://www.vcluster.com/blog/isolating-workloads-multitenant-gpu-cluster), [NVIDIA Reference Architecture for Multi-Tenant Clouds](https://docs.nvidia.com/ai-enterprise/planning-resource/reference-architecture-for-multi-tenant-clouds/latest/workload-isolation.html)

**예상 꼬리질문**:
- "MIG 없이 GPU 격리를 구현해야 한다면 어떤 대안이 있습니까?"
- "Audit log의 저장과 분석 파이프라인은 어떻게 설계하시겠습니까?"

---

### Q8. 3-5명의 백엔드 개발팀을 리딩하면서 코드 품질을 유지하기 위한 전략을 설명해주세요. 특히 스타트업 환경에서 속도와 품질의 균형을 어떻게 잡으시겠습니까?

**학습 포인트**: 백엔드 개발팀 기술 리딩 및 코드 리뷰

#### 모범답변

**핵심 요약**: "필수 자동화 + 경량 코드 리뷰 + 주간 기술 싱크"의 3축 전략으로, 스타트업 속도를 유지하면서 치명적 품질 문제를 방지합니다.

**1) 필수 자동화 (투자 대비 효과 최대)**:
```
커밋 → Pre-commit hooks (lint, format)
PR → CI 파이프라인:
     ├─ 유닛 테스트 (필수 통과)
     ├─ 타입 체크 (mypy/pyright)
     ├─ Docker 빌드 테스트
     └─ 보안 스캔 (trivy - 컨테이너 취약점)
```
- 자동화할 것: 포맷팅, 린팅, 타입 체크, 보안 스캔
- 사람이 할 것: 아키텍처 판단, 비즈니스 로직 검증, 엣지 케이스 리뷰

**2) 경량 코드 리뷰 프로세스**:
- **Small PR 원칙**: 300줄 이하. 큰 변경은 분할.
- **리뷰어 1명 필수**: 리드인 본인이 항상 리뷰하되, 팀원 간 교차 리뷰도 병행
- **48시간 SLA**: 48시간 내 리뷰 완료. 긴급 시 Slack으로 요청.
- **리뷰 레벨 구분**:
  - 🟢 Nit: 스타일 제안 (무시 가능)
  - 🟡 Suggestion: 개선 권장 (다음 PR에서 가능)
  - 🔴 Blocker: 반드시 수정 (머지 차단)

**3) 주간 기술 싱크 (30분)**:
- 월요일: 이번 주 기술 의사결정 공유
- 금요일: 이번 주 기술 부채 기록 (Tech Debt Backlog에 추가)
- 격주: 팀원 1명이 기술 공유 발표 (20분)

**스타트업 속도와 품질의 균형**:
```
  품질 ◄────────────────────────────────► 속도
       │                              │
       │  "기반 인프라 코드"            │  "프로토타입/실험"
       │  엄격한 리뷰 + 테스트 필수     │  빠른 리뷰 + TODO 허용
       │  (데이터 파이프라인, 보안)      │  (내부 도구, 대시보드)
```
- **Critical Path** (데이터 파이프라인, GPU 스케줄러, 보안): 엄격한 리뷰 + 통합 테스트 필수
- **Non-Critical Path** (어드민 도구, 내부 대시보드): 빠른 리뷰 + 나중에 리팩토링

**예상 꼬리질문**:
- "팀원이 코드 리뷰 피드백에 동의하지 않을 때 어떻게 해결하시겠습니까?"
- "기술 부채를 언제 갚을지 어떻게 우선순위를 정하시겠습니까?"

---

### Q9. 현재 GPU 서버 4대로 운영 중인 플랫폼이 고객 증가로 16대까지 확장해야 합니다. 수직 확장과 수평 확장 각각의 전략과 trade-off를 설명해주세요.

**학습 포인트**: GPU 및 스토리지 인프라 확장 전략 수립

#### 모범답변

**핵심 요약**: GPU 인프라에서는 **수평 확장(Scale-out)을 기본 전략**으로, 수직 확장(Scale-up)은 GPU 세대 교체 시에만 적용합니다.

| 비교 기준 | 수직 확장 (Scale-up) | 수평 확장 (Scale-out) |
|-----------|---------------------|----------------------|
| 방법 | GPU를 더 강력한 모델로 교체 (A100→H100) | 동일 GPU 서버를 추가 |
| 비용 | ⭐⭐⭐ 높음 (H100 $25K+/장) | ⭐⭐ 중간 (점진적 투자) |
| 다운타임 | 교체 시 서버 중단 필요 | 무중단 추가 가능 |
| 복잡도 | 낮음 (소프트웨어 변경 최소) | 높음 (분산 시스템 설계 필요) |
| 확장 한계 | GPU 1대의 물리적 한계 | 이론적 무한 |
| 적합 시나리오 | 단일 작업 성능 향상 | 동시 처리량 증가 |

**수평 확장 전략 (4대 → 16대)**:

```
Phase 1 (4→8대): 기존 네트워크 활용
  ├─ 동일 스펙 GPU 서버 4대 추가
  ├─ K8s 클러스터에 노드 추가 (kubectl join)
  ├─ BeeGFS 스토리지 서버 1대 추가
  └─ 네트워크: 기존 25GbE 스위치 포트 여유분 활용

Phase 2 (8→16대): 네트워크/스토리지 병목 해결
  ├─ Spine-Leaf 네트워크 토폴로지로 전환
  ├─ 스토리지 네트워크 분리 (Dedicated Storage Network)
  ├─ BeeGFS 메타데이터 서버 이중화
  └─ 모니터링 인프라 강화 (Prometheus HA)
```

**핵심 병목 포인트**:
1. **네트워크**: 8대 이상에서 단일 스위치 한계. Spine-Leaf 필수.
2. **스토리지 I/O**: GPU 16대가 동시에 영상 읽기 → 스토리지 throughput이 GPU 처리 속도를 따라가야 함
3. **스케줄러 부하**: 작업 수 증가 → 스케줄러 자체의 성능 테스트 필요
4. **전력/냉각**: GPU 서버 1대당 ~3-6kW. 16대 = 48-96kW. 전용 UPS + 냉각 시스템 검토.

**용량 계획 (Capacity Planning)**:
```
현재 (L40S 2대 + A100 2대):
  동시 처리: ~8-12 영상 (MPS/MIG 활용)
  월 처리량: ~150-200편

목표 (L40S 12대 + A100 4대):
  동시 처리: ~40-50 영상
  월 처리량: ~500-600편 (선형 확장이 아닌 실효 70-80% 반영)
  스토리지: Hot 200TB + Warm 1PB 필요
```

**예상 꼬리질문**:
- "16대 이후에도 계속 확장해야 한다면, 클라우드 하이브리드를 고려하시겠습니까?"
- "GPU 서버 추가 시 기존 서비스 무중단을 어떻게 보장하시겠습니까?"

---

### Q10. AI 영상 처리 플랫폼에서 장애가 발생했을 때, 어떤 모니터링 시스템과 장애 대응 프로세스를 구축하시겠습니까?

**학습 포인트**: 기술 로드맵 + 운영 역량

#### 모범답변

**핵심 요약**: NVIDIA DCGM + Prometheus + Grafana + PagerDuty로 3단계 모니터링 체계를 구축합니다.

```
┌──────────────────────────────────────────────────────┐
│              모니터링 아키텍처                          │
├──────────────────────────────────────────────────────┤
│                                                        │
│  ┌────────────────┐  ┌────────────────┐               │
│  │ GPU Metrics     │  │ System Metrics  │              │
│  │ (DCGM Exporter) │  │ (Node Exporter) │             │
│  └───────┬────────┘  └───────┬────────┘              │
│          │                    │                        │
│          ▼                    ▼                        │
│  ┌──────────────────────────────────┐                 │
│  │        Prometheus (수집/저장)      │                │
│  └──────────────┬───────────────────┘                 │
│                  │                                     │
│          ┌───────┴───────┐                             │
│          ▼               ▼                             │
│  ┌──────────────┐ ┌──────────────┐                    │
│  │ Grafana       │ │ Alertmanager │                   │
│  │ (대시보드)     │ │ → PagerDuty  │                  │
│  └──────────────┘ │ → Slack      │                   │
│                    └──────────────┘                    │
└──────────────────────────────────────────────────────┘
```

**모니터링 메트릭 3계층**:

| 계층 | 메트릭 | 임계값 | 알림 |
|------|--------|--------|------|
| **GPU** | GPU 사용률, VRAM 사용률, 온도, ECC 에러, Power | 온도>85°C, ECC>0, VRAM>95% | 🔴 즉시 |
| **시스템** | CPU, 메모리, 디스크 I/O, 네트워크 | 디스크>90%, 메모리>95% | 🟡 경고 |
| **애플리케이션** | 작업 큐 길이, 처리 시간, 실패율, API 레이턴시 | 실패율>5%, 큐>1000 | 🟡 경고 |

**GPU 특화 장애 탐지**:
1. **GPU Xid Error**: DCGM이 Xid 에러 감지 → 즉시 해당 GPU에서 작업 drain → 재시작 시도
2. **GPU Thermal Throttling**: 온도 기반 throttling 감지 → 해당 GPU 워크로드 감소
3. **GPU 메모리 누수**: VRAM 사용량 지속 증가 패턴 감지 → 컨테이너 재시작
4. **NVLink/PCIe 에러**: 통신 에러 증가 → 하드웨어 점검 알림

**장애 대응 프로세스 (Runbook)**:
```
Level 1 (자동 복구):
  GPU 작업 실패 → 자동 재시도 (최대 3회)
  Pod 크래시 → K8s 자동 재시작
  스토리지 서버 1대 장애 → BeeGFS Buddy Mirror 자동 전환

Level 2 (수동 개입):
  GPU 하드웨어 장애 → 해당 노드 K8s에서 cordon → 작업 재스케줄링 → 하드웨어 교체
  스토리지 2대 동시 장애 → 백업에서 복구

Level 3 (에스컬레이션):
  전체 클러스터 장애 → 대표/CTO 에스컬레이션 → 고객 커뮤니케이션
```

**데이터 보호**:
- **작업 체크포인팅**: 영상 처리 진행 상태를 주기적으로 저장. 장애 복구 시 마지막 체크포인트부터 재시작.
- **메타데이터 백업**: PostgreSQL → 일일 백업 + WAL 아카이빙 (PITR 가능)
- **설정 백업**: K8s 매니페스트, 스토리지 설정 → GitOps (Argo CD)

> **출처**: [NVIDIA DCGM Documentation](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/), [LogicMonitor AI Workload Infrastructure](https://www.logicmonitor.com/blog/ai-workload-infrastructure)

**예상 꼬리질문**:
- "Prometheus의 저장 용량이 부족해지면 어떻게 하시겠습니까? (Thanos/Mimir)"
- "고객에게 장애 상황을 어떻게 커뮤니케이션하시겠습니까?"

---

---

---

## 📚 Sources

1. [NVIDIA AI Enterprise Reference Architecture](https://docs.nvidia.com/ai-enterprise/planning-resource/reference-architecture-for-multi-tenant-clouds/latest/workload-isolation.html) — 멀티테넌트
2. [Introl - Multi-tenant GPU Security 2025](https://introl.com/blog/multi-tenant-gpu-security-isolation-strategies-shared-infrastructure-2025) — GPU 보안
3. [vCluster - GPU Isolation Best Practices](https://www.vcluster.com/blog/isolating-workloads-multitenant-gpu-cluster) — K8s 멀티테넌트
4. [MDPI - GPU Scheduling Survey 2025](https://www.mdpi.com/1999-4893/18/7/385) — GPU 스케줄링
5. [ACM - Deep Learning Workload Scheduling](https://dl.acm.org/doi/full/10.1145/3638757) — 워크로드 스케줄링
6. [BentoML - Batching Guide](https://bentoml.com/llm/inference-optimization/static-dynamic-continuous-batching) — Dynamic Batching
7. [VAST Data - Parallel vs Distributed FS](https://www.vastdata.com/blog/parallel-vs-distributed-file-systems-for-hpc) — 스토리지
8. [Deloitte - AI Infrastructure 2026](https://www.deloitte.com/us/en/insights/topics/technology-management/tech-trends/2026/ai-infrastructure-compute-strategy.html) — 인프라 전략
9. [Databricks - AI Infrastructure Best Practices](https://www.databricks.com/blog/ai-infrastructure-essential-components-and-best-practices) — 인프라 설계

---

## 📖 Appendix: Concept Deep Dive 핵심 인사이트

> 4개 concept-explainer 에이전트가 각각 WebSearch 7회+ WebFetch 3회+ 수행하여 도출한 핵심 포인트

### A. GPU 기반 AI 추론 파이프라인

**차별화할 수 있는 핵심 수치:**
- Triton Dynamic Batching 적용 시: throughput 73 → 272 inferences/sec (약 **3.7x 향상**) — [NVIDIA Triton Optimization Guide](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/optimization.html)
- GPU 전체 파이프라인(NVDEC→추론→NVENC) 시 CPU 대비 **10~100x 성능 향상** — [RunPod](https://www.runpod.io/articles/guides/computer-vision-pipeline-optimization-accelerating-image-processing-workflows-with-gpu-computing)
- FP16 양자화: VRAM 50% 절감 + ~2x 속도. INT8: VRAM 75% 절감 + ~3x 속도 (calibration 필요)

**Anti-Pattern (알아두면 좋은 것):**
- CPU-GPU 메모리 핑퐁: PCIe ~32GB/s가 병목. 전체 파이프라인을 GPU 메모리 내에서 유지해야 함
- 고정 배치 크기: 요청 적을 때 무한 대기 → Dynamic Batching 필수
- MPS에서 프로덕션 운영: 메모리 격리 없음 → 한 프로세스 OOM 시 전체 죽음

**2025-2026 트렌드:**
- NVIDIA Dynamo: Triton 차세대, 분산 추론 + disaggregated serving 지원
- LithOS (CMU): GPU를 OS 레벨에서 관리하여 MPS 활용률 + MIG 격리 동시 달성

### B. 온프레미스 GPU 인프라 아키텍처

**L40S가 Video AI에 최적인 이유 (핵심 포인트):**

| GPU | NVENC | NVDEC | 이유 |
|-----|-------|-------|------|
| H100 SXM | 0 | 0 | Training 전용, 영상 처리에 비효율 |
| A100 | 0 | 1 | 디코딩만 가능, 인코딩은 CPU 필요 |
| **L40S** | **3** | **3** | 영상 디코딩→AI 추론→영상 인코딩 올인원 |

→ "AI 추론 중심 Video AI 플랫폼에는 H100보다 L40S가 TCO 관점에서 우수합니다" 라고 답변하면 깊은 이해를 어필 가능

**온프레미스 TCO 손익분기:**
- GPU 활용률 70-80% 이상 지속 시, **8-18개월** 내 클라우드 대비 손익분기 — [Lenovo TCO 2025](https://lenovopress.lenovo.com/lp2225-on-premise-vs-cloud-generative-ai-total-cost-of-ownership)
- 영상 데이터 egress fee만으로도 상당한 추가 비용 → 온프레미스 유리

**전력/냉각 핵심 수치:**
- GPU 서버 1대 (8x H100): ~10.2kW / 랙 4대: ~40kW
- 50kW 이상: 액체 냉각(Direct-to-Chip) 필수
- PUE 목표: < 1.3 (Air: 1.4-1.6, Liquid: <1.2)

### C. 대용량 영상 데이터 파이프라인

**인용할 수 있는 업계 레퍼런스:**
- Netflix: 매주 약 **2 PB** 미디어 데이터 생성. Chunk 기반 분산 인코딩으로 수 시간 → 수 분 단축
- Meta: 하루 **수십억 번** FFmpeg 실행, **10억 건+** 비디오 업로드 처리
- Netflix AV1: 전체 스트리밍의 ~30%, AVC/HEVC 대비 대역폭 1/3 절감, 버퍼링 45% 감소

**핵심 숫자 (용량 계산 대비):**
- 1분 4K ProRes: ~6 GB
- 1분 1080p H.264: ~150 MB / H.265: ~75 MB / AV1: ~60 MB
- NVENC HW 인코딩: ~500+ fps (1080p) vs SW FFmpeg: ~30 fps

**워크플로우 오케스트레이터 선택:**
- Temporal: 장기 실행 워크플로우에 강점 (영상 처리는 수시간 소요)
- Argo Workflows: K8s 네이티브 GPU 병렬 처리에 최적
- 최적 조합: Temporal(상태 관리) + Argo(GPU 병렬 처리)

### D. 멀티테넌트 데이터 격리

**Bridge 모델이 Video AI에 최적인 이유 (핵심 답변):**
- 영상/GPU는 **Silo** (보안 + 성능 격리) → 미공개 영상 유출 방지
- 메타데이터/인증/빌링은 **Pool** (비용 + 운영 효율)
- 테넌트 티어(Free/Pro/Enterprise)에 따라 유연하게 격리 수준 조절

**Crypto-shredding (차별화 포인트):**
- 테넌트 해지 시 TB 단위 영상 데이터를 물리 삭제하는 것은 비현실적
- 대신 **per-tenant 암호화 키를 파기** → 데이터가 의미 없는 바이트가 됨
- 규정 준수(GDPR Right to Erasure) 충족

**GPU 메모리 보안 (잘 모르는 사람이 많은 포인트):**
- GPU 메모리는 워크로드 전환 시 **자동 초기화되지 않음**
- 이전 테넌트의 모델 가중치/영상 데이터가 잔류 가능
- 반드시 **세션 간 GPU memory zeroing** 구현 필요
- H100/Blackwell은 Confidential Computing (AES-GCM 256) 지원