# K8s Hello World 실무형 튜토리얼

> **대상**: Kubernetes를 처음 접하거나 개념만 알고 직접 해본 적 없는 백엔드 개발자
> **소요시간**: 약 2~3시간 (Part 1: 30분, Part 2: 45분, Part 3: 45분)
> **사전 요구사항**: macOS, Docker Desktop 설치 완료, 터미널 사용 경험
> **학습 목표**:
> 1. Minikube + Helm으로 FastAPI 앱을 K8s에 배포할 수 있다
> 2. Pod, Service, Ingress 등 핵심 리소스의 역할과 관계를 이해한다
> 3. Health Probe, Graceful Shutdown, Rolling Update 등 실무 패턴을 직접 실험한다

---

## 목차

- [Part 1: 일단 돌린다](#part-1-일단-돌린다)
  - [Step 1-1: 환경 준비](#step-1-1-환경-준비)
  - [Step 1-2: FastAPI 앱 작성](#step-1-2-fastapi-앱-작성)
  - [Step 1-3: Docker 이미지 빌드](#step-1-3-docker-이미지-빌드)
  - [Step 1-4: Helm 차트로 배포](#step-1-4-helm-차트로-배포)
  - [Step 1-5: 동작 확인](#step-1-5-동작-확인)
- [Part 2: 방금 뭘 한 거지? — K8s 아키텍처 해부](#part-2-방금-뭘-한-거지--k8s-아키텍처-해부)
  - [Step 2-1: K8s 전체 아키텍처](#step-2-1-k8s-전체-아키텍처)
  - [Step 2-2: 리소스 계층 — 우리가 만든 것들을 역추적](#step-2-2-리소스-계층--우리가-만든-것들을-역추적)
  - [Step 2-3: 요청이 Hello World에 도달하기까지](#step-2-3-요청이-hello-world에-도달하기까지)
  - [Step 2-4: Helm이 해준 것](#step-2-4-helm이-해준-것)
  - [Step 2-5: kubectl로 까보기](#step-2-5-kubectl로-까보기)
- [Part 3: 실무처럼 만들기](#part-3-실무처럼-만들기)
  - [Step 3-1: ConfigMap으로 설정 변경](#step-3-1-configmap으로-설정-변경)
  - [Step 3-2: Health Probe 동작 실험](#step-3-2-health-probe-동작-실험)
  - [Step 3-3: Resource 관리](#step-3-3-resource-관리)
  - [Step 3-4: Graceful Shutdown 이해](#step-3-4-graceful-shutdown-이해)
  - [Step 3-5: Rolling Update 무중단 배포](#step-3-5-rolling-update-무중단-배포)
- [정리 및 다음 단계](#정리-및-다음-단계)

---

# Part 1: 일단 돌린다

> 이해는 나중에. 먼저 K8s 위에서 Hello World가 돌아가는 것을 눈으로 확인하자.

---

## Step 1-1: 환경 준비

### 도구 설치 (macOS Homebrew 기준)

```bash
# Minikube — 내 노트북에서 돌아가는 1인용 K8s 클러스터
brew install minikube

# Helm — K8s 배포 패키지 매니저 (apt-get/brew의 K8s 버전이라고 생각하면 된다)
brew install helm

# kubectl — K8s 클러스터와 대화하는 CLI (minikube 설치 시 보통 함께 설치됨)
brew install kubectl
```

각 도구를 한 줄로 정리하면:

| 도구 | 한 줄 설명 |
|------|-----------|
| **Minikube** | 로컬 머신에 가상 K8s 클러스터를 만들어주는 도구 |
| **Helm** | K8s 리소스를 패키지(차트)로 묶어서 한 번에 배포/관리하는 도구 |
| **kubectl** | K8s 클러스터에 명령을 내리는 CLI (모든 K8s 작업의 출발점) |

### Minikube 클러스터 시작

```bash
minikube start --driver=docker --cpus=2 --memory=4096
```

- `--driver=docker`: Docker 위에서 K8s를 실행한다 (가장 안정적인 옵션)
- `--cpus=2`: CPU 2코어 할당
- `--memory=4096`: 메모리 4GB 할당 (Ingress 등 addon 포함 시 4GB 권장)

### 필수 애드온 활성화

```bash
# Ingress Controller — 외부 HTTP 요청을 클러스터 내부로 라우팅
minikube addons enable ingress

# Metrics Server — kubectl top 명령으로 CPU/메모리 사용량 확인
minikube addons enable metrics-server
```

### 설치 확인

```bash
kubectl cluster-info
# 출력 예시:
# Kubernetes control plane is running at https://192.168.49.2:8443
# CoreDNS is running at https://192.168.49.2:8443/api/v1/namespaces/...

helm version
# 출력 예시:
# version.BuildInfo{Version:"v3.x.x", ...}

kubectl get nodes
# 출력 예시:
# NAME       STATUS   ROLES           AGE   VERSION
# minikube   Ready    control-plane   1m    v1.28.x
```

### /etc/hosts 설정

우리 앱에 `hello.local` 도메인으로 접근하기 위해 hosts 파일에 등록한다.

```bash
echo "$(minikube ip) hello.local" | sudo tee -a /etc/hosts
```

> **Apple Silicon (M1/M2/M3) 참고**: `minikube ip`가 `127.0.0.1`을 반환하는 경우가 있다.
> 이 경우 별도 터미널에서 `minikube tunnel`을 실행해야 Ingress가 정상 동작한다.
> 그리고 `/etc/hosts`에는 `127.0.0.1 hello.local`을 등록한다.

---

## Step 1-2: FastAPI 앱 작성

### 디렉토리 구조 생성

```bash
mkdir -p k8s-hello-world/app
cd k8s-hello-world
```

### requirements.txt

```bash
# 파일: app/requirements.txt
```

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
```

- **FastAPI**: 파이썬 비동기 웹 프레임워크 (타입 힌트 기반, 자동 API 문서)
- **Uvicorn**: ASGI 서버 (FastAPI를 실행하는 엔진)

### main.py

```bash
# 파일: app/main.py
```

```python
"""
FastAPI Hello World - Kubernetes 튜토리얼용 애플리케이션

K8s의 핵심 개념을 실습하기 위한 간단한 웹 서버:
- Liveness / Readiness Probe
- Graceful Shutdown (SIGTERM 처리)
- 환경 변수 주입 (ConfigMap, Downward API)
- 구조화된 JSON 로깅
"""

import asyncio
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# ──────────────────────────────────────────────
# 환경 변수 설정 (K8s ConfigMap / Downward API로 주입)
# ──────────────────────────────────────────────
APP_ENV = os.environ.get("APP_ENV", "local")          # 실행 환경 (local, dev, staging, prod)
APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")  # 앱 버전 (이미지 태그와 맞추면 편리)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "info")        # 로그 레벨
POD_NAME = os.environ.get("POD_NAME", "unknown")      # K8s Downward API로 주입되는 파드 이름


# ──────────────────────────────────────────────
# JSON 로깅 포맷터 (외부 라이브러리 없이 구현)
# ──────────────────────────────────────────────
class JsonFormatter(logging.Formatter):
    """
    로그를 JSON 형태로 출력하는 커스텀 포맷터.

    K8s 환경에서는 stdout으로 출력된 JSON 로그를
    Fluentd, Filebeat 등의 로그 수집기가 파싱할 수 있다.
    (12-Factor App: Factor 11 - Logs as event streams)
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "pod": POD_NAME,
        }
        # 예외 정보가 있으면 포함
        if record.exc_info and record.exc_info[0] is not None:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)


# 로거 설정: stdout으로만 출력 (컨테이너 로깅 표준)
logger = logging.getLogger("app")
logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logger.handlers = [handler]  # 기존 핸들러 제거 후 JSON 핸들러만 사용


# ──────────────────────────────────────────────
# 애플리케이션 상태 (Readiness / Shutdown 플래그)
# ──────────────────────────────────────────────
app_state = {
    "ready": True,       # Readiness Probe 응답 제어 (False면 503)
    "shutting_down": False,  # Graceful Shutdown 진행 중 여부
}


# ──────────────────────────────────────────────
# SIGTERM 핸들러 (Graceful Shutdown)
# ──────────────────────────────────────────────
def handle_sigterm(signum, frame):
    """
    K8s가 파드를 종료할 때 SIGTERM을 보낸다.
    이 핸들러에서:
    1. Readiness를 False로 전환 → 새 트래픽 수신 중단
    2. 진행 중인 요청이 완료될 시간을 확보

    K8s terminationGracePeriodSeconds (기본 30초) 내에
    종료되지 않으면 SIGKILL이 전송된다.
    """
    logger.info("Received SIGTERM, starting graceful shutdown...")
    app_state["shutting_down"] = True
    app_state["ready"] = False  # Readiness Probe 실패 → 새 트래픽 차단


# SIGTERM 시그널 등록
signal.signal(signal.SIGTERM, handle_sigterm)


# ──────────────────────────────────────────────
# FastAPI 앱 생성
# ──────────────────────────────────────────────
app = FastAPI(
    title="K8s Tutorial App",
    description="Kubernetes 튜토리얼용 FastAPI Hello World",
    version=APP_VERSION,
)


# ──────────────────────────────────────────────
# 라이프사이클 이벤트
# ──────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    """앱 시작 시 초기화 로그 출력"""
    logger.info(
        f"Application started: env={APP_ENV}, version={APP_VERSION}, pod={POD_NAME}"
    )


@app.on_event("shutdown")
async def on_shutdown():
    """
    앱 종료 시 리소스 정리.
    실제 프로젝트에서는 DB 커넥션 풀, 메시지 큐 연결 등을 정리한다.
    """
    logger.info("Cleaning up resources...")
    # 여기에 DB 커넥션 종료, 캐시 플러시 등 정리 로직 추가
    logger.info("Shutdown complete")


# ──────────────────────────────────────────────
# 엔드포인트 정의
# ──────────────────────────────────────────────

@app.get("/")
async def root():
    """
    메인 엔드포인트 - Hello World 응답.
    버전 정보를 함께 반환하여 Rolling Update 시 확인 가능.
    """
    logger.info("Hello World requested")
    return {"message": "Hello World", "version": APP_VERSION}


@app.get("/health/live")
async def liveness():
    """
    Liveness Probe 엔드포인트.

    K8s가 주기적으로 호출하여 컨테이너가 살아있는지 확인한다.
    실패 시 컨테이너를 재시작한다.

    여기서는 단순히 200을 반환하지만, 실제로는
    데드락 감지, 메모리 누수 체크 등을 추가할 수 있다.
    """
    return {"status": "ok"}


@app.get("/health/ready")
async def readiness():
    """
    Readiness Probe 엔드포인트.

    K8s가 주기적으로 호출하여 트래픽을 받을 준비가 되었는지 확인한다.
    실패 시 Service의 Endpoints에서 제거되어 새 트래픽을 받지 않는다.

    - 정상: 200 OK
    - 비정상 (toggle off 또는 shutdown 중): 503 Service Unavailable
    """
    if not app_state["ready"]:
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "shutting_down": app_state["shutting_down"]},
        )
    return {"status": "ok"}


@app.post("/admin/toggle-ready")
async def toggle_ready():
    """
    Readiness 상태를 수동으로 토글하는 관리 엔드포인트.

    테스트 시나리오:
    1. POST /admin/toggle-ready → ready=False
    2. kubectl get endpoints 로 파드가 빠지는 것 확인
    3. POST /admin/toggle-ready → ready=True
    4. 파드가 다시 Endpoints에 포함되는 것 확인
    """
    app_state["ready"] = not app_state["ready"]
    new_state = "ready" if app_state["ready"] else "not ready"
    logger.info(f"Readiness toggled: {new_state}")
    return {"ready": app_state["ready"]}


@app.get("/slow")
async def slow_response(seconds: int = 5):
    """
    의도적으로 느린 응답을 생성하는 엔드포인트.

    Graceful Shutdown 테스트용:
    1. curl로 /slow?seconds=30 요청 시작
    2. 다른 터미널에서 kubectl delete pod 실행
    3. 요청이 정상 완료되는지 확인 (terminationGracePeriodSeconds 이내)

    최대 60초로 제한하여 과도한 요청 방지.
    """
    # 최대 60초 제한
    capped_seconds = min(seconds, 60)
    logger.info(f"Slow endpoint called: sleeping for {capped_seconds}s")

    # asyncio.sleep을 사용하여 이벤트 루프를 블로킹하지 않음
    await asyncio.sleep(capped_seconds)

    return {
        "message": f"Responded after {capped_seconds} seconds",
        "requested_seconds": seconds,
        "actual_seconds": capped_seconds,
    }


@app.get("/info")
async def info():
    """
    앱 메타데이터 반환 엔드포인트.

    K8s에서 주입된 환경 변수들을 확인할 수 있다:
    - APP_ENV: ConfigMap으로 주입
    - APP_VERSION: 이미지 태그 또는 ConfigMap
    - LOG_LEVEL: ConfigMap으로 주입
    - POD_NAME: Downward API (metadata.name)
    """
    return {
        "app_env": APP_ENV,
        "app_version": APP_VERSION,
        "log_level": LOG_LEVEL,
        "pod_name": POD_NAME,
    }
```

### 엔드포인트 요약

| 엔드포인트 | 메서드 | 목적 |
|-----------|--------|------|
| `/` | GET | Hello World 응답 + 버전 확인 |
| `/health/live` | GET | Liveness Probe (살아있니?) |
| `/health/ready` | GET | Readiness Probe (트래픽 받을 수 있니?) |
| `/admin/toggle-ready` | POST | Readiness 수동 토글 (실험용) |
| `/slow?seconds=N` | GET | 느린 응답 (Graceful Shutdown 테스트용) |
| `/info` | GET | 환경 변수 확인 (ConfigMap/Downward API) |

> **왜 이렇게?**
>
> - **JSON 로깅**: K8s에서는 로그가 stdout으로 나가고, Fluentd/Filebeat 같은 수집기가 파싱한다. JSON 형식이면 자동 파싱이 가능해서 검색/필터링이 쉽다. 파일에 직접 쓰면? 컨테이너가 죽으면 로그도 사라진다.
> - **Health Endpoint 분리 (`/health/live` vs `/health/ready`)**: K8s가 "이 컨테이너 재시작할까?" (liveness)와 "이 컨테이너에 트래픽 보내도 될까?" (readiness)를 각각 판단하기 위해 필요하다. 하나로 합치면 세밀한 제어가 불가능하다.
> - **SIGTERM 핸들링**: K8s가 Pod를 종료할 때 SIGTERM을 보낸다. 이것을 잡아서 "지금 처리 중인 요청은 마저 처리하고, 새 요청은 거부" 하는 것이 graceful shutdown이다. 안 하면? 사용자가 500 에러를 본다.

### 로컬 테스트

K8s에 올리기 전에 로컬에서 먼저 확인하자.

```bash
cd k8s-hello-world

# 가상환경 생성 및 의존성 설치
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt

# 앱 실행
uvicorn app.main:app --host 0.0.0.0 --port 8080

# 다른 터미널에서 확인
curl http://localhost:8080/
# {"message":"Hello World","version":"1.0.0"}

curl http://localhost:8080/health/live
# {"status":"ok"}

curl http://localhost:8080/info
# {"app_env":"local","app_version":"1.0.0","log_level":"info","pod_name":"unknown"}
```

확인이 끝나면 `Ctrl+C`로 서버를 종료한다.

---

## Step 1-3: Docker 이미지 빌드

### .dockerignore

```bash
# 파일: .dockerignore
```

```
__pycache__
*.pyc
.git
.gitignore
*.md
.env
helm/
.venv/
```

Docker 빌드 시 불필요한 파일을 제외한다. `.gitignore`와 비슷한 역할이다.
특히 `.venv/`나 `helm/`을 포함시키면 이미지 크기가 불필요하게 커진다.

### Dockerfile

```bash
# 파일: Dockerfile
```

```dockerfile
# ============================================================
# Stage 1: Builder
# 멀티스테이지 빌드 — 빌드 도구와 캐시를 최종 이미지에서 제거하여
# 이미지 크기를 대폭 줄인다 (보통 50~70% 감소).
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# requirements.txt만 먼저 복사하여 Docker 레이어 캐시를 활용한다.
# 소스코드가 바뀌어도 의존성이 동일하면 pip install을 다시 실행하지 않는다.
COPY app/requirements.txt .

# --no-cache-dir: pip 캐시를 저장하지 않아 이미지 크기를 줄인다.
# --prefix=/install: 설치 결과물을 별도 경로에 격리하여 런타임 스테이지로 깔끔하게 복사할 수 있다.
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================================
# Stage 2: Runtime
# 빌드 도구 없이 실행에 필요한 것만 포함하는 최종 이미지.
# ============================================================
FROM python:3.12-slim

# 비root 사용자 생성 — 컨테이너가 탈취되더라도 호스트 시스템에 대한
# 권한 상승(privilege escalation)을 방지하기 위한 보안 조치.
# -r: 시스템 계정, -s /sbin/nologin: 셸 로그인 차단.
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Builder 스테이지에서 설치한 Python 패키지만 복사한다.
# 빌드 도구(gcc, pip 캐시 등)는 빌더에 남아 최종 이미지에 포함되지 않는다.
COPY --from=builder /install /usr/local

# 애플리케이션 소스코드 복사
COPY app/ .

# 비root 사용자로 전환 — 이 시점 이후 모든 명령은 appuser 권한으로 실행된다.
# K8s에서도 runAsNonRoot: true 설정과 함께 사용하면 이중 보안이 된다.
USER appuser

# 컨테이너가 수신하는 포트를 문서화한다.
# 실제 포트 바인딩은 docker run -p 또는 K8s Service에서 설정한다.
EXPOSE 8080

# 헬스체크 — K8s livenessProbe/readinessProbe와 별개로,
# Docker 자체적으로도 컨테이너 상태를 모니터링할 수 있게 한다.
# curl을 설치하지 않고 Python 표준 라이브러리만으로 HTTP 체크를 수행한다.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health/live')" || exit 1

# exec form(JSON 배열)을 사용해야 uvicorn이 PID 1로 직접 실행된다.
# shell form(문자열)을 쓰면 /bin/sh가 PID 1이 되어 SIGTERM이
# uvicorn에 전달되지 않아 graceful shutdown이 불가능하다.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "info"]
```

> **왜 이렇게?**
>
> - **Multi-stage Build**: Stage 1(builder)에서 pip install을 수행하고, Stage 2(runtime)에서는 설치 결과물만 복사한다. 빌드 도구(gcc, pip 캐시)를 최종 이미지에서 제거하여 크기를 50~70% 줄일 수 있다.
> - **Non-root User**: `appuser`라는 권한 없는 사용자로 실행한다. 컨테이너가 해킹당해도 호스트 시스템의 root 권한을 탈취할 수 없다. 자물쇠를 하나 더 거는 것과 같다.
> - **Exec Form CMD**: `CMD ["uvicorn", ...]` (JSON 배열)을 쓰면 uvicorn이 PID 1로 실행된다. `CMD uvicorn ...` (문자열)을 쓰면 `/bin/sh`가 PID 1이 되어 K8s의 SIGTERM이 uvicorn에 전달되지 않는다. Graceful shutdown의 핵심!

### Minikube Docker 환경으로 빌드

Minikube 내부에는 자체 Docker 데몬이 있다. 로컬 Docker로 빌드하면 이미지를 Minikube에 별도로 전송해야 하지만, Minikube Docker 데몬을 직접 사용하면 빌드 결과가 바로 Minikube에 저장된다.

```bash
# Minikube 내부 Docker 데몬을 현재 셸에서 사용하도록 환경 변수 설정
eval $(minikube docker-env)

# 이미지 빌드
docker build -t hello-world:1.0.0 .

# 빌드 확인
docker images | grep hello-world
# 출력 예시:
# hello-world   1.0.0   abc123def456   5 seconds ago   158MB
```

> **비유**: `eval $(minikube docker-env)`는 "이번 대화는 Minikube한테 직접 하겠어"라고 선언하는 것이다. 원래 내 노트북의 Docker한테 말하던 것을, Minikube 안에 있는 Docker한테 직접 말하는 것으로 전환된다.

---

## Step 1-4: Helm 차트로 배포

### Helm 차트 구조

```
helm/hello-world/
├── Chart.yaml          # 차트 메타데이터 (이름, 버전)
├── values.yaml         # 기본 설정값 (배포 환경에 따라 오버라이드)
└── templates/          # K8s 리소스 템플릿
    ├── _helpers.tpl    # 공통 템플릿 함수 (이름, 레이블 생성)
    ├── namespace.yaml  # 네임스페이스
    ├── configmap.yaml  # 환경변수 설정
    ├── deployment.yaml # Pod 배포 정의 (핵심!)
    ├── service.yaml    # 네트워크 접근 경로
    └── ingress.yaml    # 외부 HTTP 라우팅
```

지금은 "이런 파일들이 있구나" 정도로만 보자. 각 파일의 상세한 역할은 Part 2에서 해부한다.

### Chart.yaml

```yaml
apiVersion: v2
name: hello-world
description: K8s Hello World Tutorial - FastAPI App
type: application
version: 0.1.0
appVersion: "1.0.0"
```

### values.yaml (전체 — 모든 설정의 중앙 관리 파일)

```yaml
# ============================================================
# Hello World Helm Chart - 기본 설정값
# ============================================================
# 이 파일은 Helm 차트의 모든 설정 가능한 값을 정의합니다.
# helm install 또는 helm upgrade 시 --set 또는 -f 플래그로
# 이 값들을 오버라이드할 수 있습니다.
# ============================================================

# ------------------------------------------------------------
# 레플리카 수 (Pod 복제본 개수)
# ------------------------------------------------------------
# 가용성을 위해 최소 2개 이상 권장합니다.
# HPA(Horizontal Pod Autoscaler)를 사용할 경우 이 값은
# 초기값으로만 동작합니다.
replicaCount: 2

# ------------------------------------------------------------
# 컨테이너 이미지 설정
# ------------------------------------------------------------
# repository: 이미지 이름 (레지스트리 포함 가능, 예: ghcr.io/myorg/hello-world)
# tag: 이미지 태그 (버전). Chart의 appVersion과 맞추는 것을 권장합니다.
# pullPolicy: 이미지 풀 정책
#   - Always: 항상 레지스트리에서 새로 pull
#   - IfNotPresent: 로컬에 없을 때만 pull (권장)
#   - Never: 로컬 이미지만 사용
image:
  repository: hello-world
  tag: "1.0.0"
  pullPolicy: IfNotPresent

# ------------------------------------------------------------
# 네임스페이스 설정
# ------------------------------------------------------------
# 리소스가 배포될 Kubernetes 네임스페이스입니다.
# 네임스페이스가 없으면 차트가 자동으로 생성합니다.
namespace: hello

# ------------------------------------------------------------
# 서비스 설정
# ------------------------------------------------------------
# type: 서비스 타입
#   - ClusterIP: 클러스터 내부에서만 접근 가능 (기본값)
#   - NodePort: 노드의 고정 포트로 외부 접근 허용
#   - LoadBalancer: 클라우드 제공자의 로드밸런서 사용
# port: 서비스가 노출하는 포트 (클라이언트가 접근하는 포트)
# targetPort: 컨테이너 내부에서 앱이 리스닝하는 포트
service:
  type: ClusterIP
  port: 80
  targetPort: 8080

# ------------------------------------------------------------
# 인그레스 설정
# ------------------------------------------------------------
# 클러스터 외부에서 HTTP(S)로 접근할 수 있도록 라우팅 규칙을 정의합니다.
# enabled: false로 설정하면 인그레스 리소스가 생성되지 않습니다.
# className: 사용할 Ingress Controller (nginx, traefik 등)
# host: 라우팅할 도메인 (로컬 테스트 시 /etc/hosts에 등록 필요)
ingress:
  enabled: true
  className: nginx
  host: hello.local

# ------------------------------------------------------------
# 리소스 제한 설정
# ------------------------------------------------------------
# requests: Pod 스케줄링 시 보장받는 최소 리소스
# limits: Pod가 사용할 수 있는 최대 리소스
#
# CPU 단위: 1000m = 1 CPU 코어
# 메모리 단위: Mi (메비바이트), Gi (기비바이트)
#
# requests와 limits의 차이가 클수록 노드 과잉 할당 위험이 있으므로
# 적절한 비율(보통 1:2 ~ 1:3)을 유지하는 것이 좋습니다.
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 250m
    memory: 256Mi

# ------------------------------------------------------------
# 헬스체크 프로브 설정
# ------------------------------------------------------------
# liveness: 컨테이너가 살아있는지 확인합니다.
#   실패 시 kubelet이 컨테이너를 재시작합니다.
#   initialDelaySeconds: 앱 기동 시간을 고려하여 충분히 설정합니다.
#
# readiness: 컨테이너가 트래픽을 받을 준비가 되었는지 확인합니다.
#   실패 시 Service 엔드포인트에서 제외됩니다. (재시작 X)
#   initialDelaySeconds: liveness보다 짧게 설정하여 빠르게 트래픽을 받습니다.
probes:
  liveness:
    path: /health/live
    initialDelaySeconds: 10
    periodSeconds: 10
    failureThreshold: 3
  readiness:
    path: /health/ready
    initialDelaySeconds: 5
    periodSeconds: 5
    failureThreshold: 3

# ------------------------------------------------------------
# Graceful Shutdown 설정
# ------------------------------------------------------------
# terminationGracePeriodSeconds:
#   SIGTERM 수신 후 SIGKILL까지의 유예 시간(초)입니다.
#   앱이 진행 중인 요청을 모두 처리할 수 있는 충분한 시간을 줍니다.
#
# preStopSleepSeconds:
#   preStop hook에서 sleep하는 시간(초)입니다.
#   Kubernetes가 Service 엔드포인트를 업데이트하는 동안
#   기존 요청이 유실되지 않도록 잠시 대기합니다.
#   (iptables/IPVS 규칙 전파 시간을 고려한 값)
#
# 주의: preStopSleepSeconds < terminationGracePeriodSeconds 여야 합니다.
gracefulShutdown:
  terminationGracePeriodSeconds: 45
  preStopSleepSeconds: 10

# ------------------------------------------------------------
# 애플리케이션 환경 설정
# ------------------------------------------------------------
# ConfigMap으로 주입되는 환경변수 값들입니다.
# appEnv: 실행 환경 (development, staging, production)
# logLevel: 로그 레벨 (debug, info, warning, error)
config:
  appEnv: production
  logLevel: info

# ------------------------------------------------------------
# 앱 버전
# ------------------------------------------------------------
# ConfigMap의 APP_VERSION에 사용됩니다.
# 이미지 태그와 별도로 관리할 수 있습니다.
app:
  version: "1.0.0"
```

### 배포 실행

```bash
# Helm 차트로 배포 (릴리즈 이름: hello)
helm install hello ./helm/hello-world
```

출력 예시:
```
NAME: hello
LAST DEPLOYED: ...
NAMESPACE: default
STATUS: deployed
REVISION: 1
```

### Pod 상태 확인

```bash
kubectl get all -n hello
```

출력 예시:
```
NAME                                    READY   STATUS    RESTARTS   AGE
pod/hello-hello-world-xxxxxxxxx-xxxxx   1/1     Running   0          30s
pod/hello-hello-world-xxxxxxxxx-yyyyy   1/1     Running   0          30s

NAME                        TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
service/hello-hello-world   ClusterIP   10.96.xxx.xxx   <none>        80/TCP    30s

NAME                                READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/hello-hello-world   2/2     2            2           30s
```

STATUS가 `Running`이 아니라 `ContainerCreating`이나 `ImagePullBackOff`라면 잠시 기다리거나 Troubleshooting을 참고하자.

---

## Step 1-5: 동작 확인

### API 호출 테스트

```bash
# Hello World 확인
curl http://hello.local/
# {"message":"Hello World","version":"1.0.0"}

# Liveness Probe 확인
curl http://hello.local/health/live
# {"status":"ok"}

# Readiness Probe 확인
curl http://hello.local/health/ready
# {"status":"ok"}

# 앱 메타정보 확인 (K8s 환경변수 주입 확인)
curl http://hello.local/info
# {"app_env":"production","app_version":"1.0.0","log_level":"info","pod_name":"hello-hello-world-xxxxxxxxx-xxxxx"}
```

브라우저에서 `http://hello.local/`을 열어도 JSON 응답을 볼 수 있다.
`http://hello.local/docs`로 가면 FastAPI의 자동 생성 API 문서(Swagger UI)도 확인 가능하다.

### Troubleshooting

**Pod이 안 뜰 때:**

```bash
# Pod 상태 상세 확인 — Events 섹션에 원인이 나온다
kubectl describe pod -l app.kubernetes.io/name=hello-world -n hello
```

자주 나오는 에러:

| STATUS | 원인 | 해결 |
|--------|------|------|
| `ImagePullBackOff` | 이미지를 찾을 수 없음 | `eval $(minikube docker-env)` 후 다시 빌드 |
| `CrashLoopBackOff` | 앱이 시작 직후 crash | `kubectl logs <pod-name> -n hello` 로 에러 로그 확인 |
| `Pending` | 리소스 부족 | `minikube start`에서 CPU/메모리 늘리기 |

**Ingress가 안 될 때:**

```bash
# /etc/hosts 확인
cat /etc/hosts | grep hello

# Ingress Controller가 돌고 있는지 확인
kubectl get pods -n ingress-nginx

# Apple Silicon이라면 tunnel 실행 (별도 터미널에서 계속 실행)
minikube tunnel
```

> **Part 1 체크포인트**: `curl http://hello.local/`에서 `{"message":"Hello World","version":"1.0.0"}`이 보이면 성공이다. K8s 위에서 앱이 돌아가고 있다!

---

# Part 2: 방금 뭘 한 거지? — K8s 아키텍처 해부

> Part 1에서 우리는 helm install 한 줄로 앱을 배포했다. 이제 그 한 줄 뒤에서 무슨 일이 일어났는지 뜯어보자.

---

## Step 2-1: K8s 전체 아키텍처

### 클러스터 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                        K8s Cluster                              │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   Control Plane (두뇌)                     │  │
│  │                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │  │
│  │  │  API Server   │  │    etcd      │  │   Scheduler    │  │  │
│  │  │  (접수 창구)   │  │ (기록 장부)   │  │ (배치 담당자)  │  │  │
│  │  │              │  │              │  │                │  │  │
│  │  │ 모든 요청이    │  │ 클러스터의    │  │ "이 Pod는     │  │  │
│  │  │ 여기를 통과    │  │ 모든 상태를   │  │  어느 Node에   │  │  │
│  │  │              │  │ key-value로   │  │  놓을까?"      │  │  │
│  │  │              │  │ 저장          │  │                │  │  │
│  │  └──────────────┘  └──────────────┘  └────────────────┘  │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │              Controller Manager (감시자)              │  │  │
│  │  │                                                     │  │  │
│  │  │  "원하는 상태(desired) vs 현재 상태(current)"         │  │  │
│  │  │  차이가 있으면 자동으로 맞춘다                         │  │  │
│  │  │  예: replica=2인데 Pod 1개만 있으면 → 1개 더 생성    │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   Worker Node (일꾼)                       │  │
│  │                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │  │
│  │  │   kubelet     │  │  kube-proxy  │  │   Pod  Pod     │  │  │
│  │  │ (현장 관리자)  │  │  (교환원)     │  │   Pod  Pod     │  │  │
│  │  │              │  │              │  │                │  │  │
│  │  │ Pod를 실제로  │  │ 네트워크     │  │  실제 앱이     │  │  │
│  │  │ 실행하고      │  │ 규칙을 관리   │  │  돌아가는 곳   │  │  │
│  │  │ 모니터링      │  │ (iptables)   │  │                │  │  │
│  │  └──────────────┘  └──────────────┘  └────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

> **비유**: K8s 클러스터는 레스토랑과 비슷하다.
> - **API Server** = 접수 창구. 손님(사용자)의 모든 주문이 여기로 온다.
> - **etcd** = 주문 기록장. "테이블 3번에 파스타 2개" 같은 모든 상태가 여기 적혀있다.
> - **Scheduler** = 홀 매니저. "이 주문은 2번 셰프한테 보내자" 결정.
> - **Controller Manager** = 감독관. "파스타 2개 주문인데 지금 1개만 나왔네? 1개 더 만들어" 감시.
> - **kubelet** = 각 주방의 셰프. 실제로 요리(컨테이너)를 만든다.
> - **kube-proxy** = 서빙 직원. 완성된 요리를 올바른 테이블로 전달한다.

Minikube에서는 이 모든 것이 **하나의 Node**에 들어있다. 실제 운영 환경에서는 Control Plane과 Worker Node가 분리되어 있다.

### Part 1에서 `helm install`했을 때 일어난 일

```
당신                    Helm              API Server         etcd          Scheduler       kubelet
  │                      │                    │                │               │              │
  │  helm install hello  │                    │                │               │              │
  │─────────────────────>│                    │                │               │              │
  │                      │                    │                │               │              │
  │                      │ YAML 템플릿 렌더링  │                │               │              │
  │                      │ (values + template │                │               │              │
  │                      │  → 완성된 YAML)     │                │               │              │
  │                      │                    │                │               │              │
  │                      │ POST /apis/...     │                │               │              │
  │                      │───────────────────>│                │               │              │
  │                      │                    │                │               │              │
  │                      │                    │  상태 저장      │               │              │
  │                      │                    │───────────────>│               │              │
  │                      │                    │                │               │              │
  │                      │                    │  "Pod 2개 필요" │               │              │
  │                      │                    │──────────────────────────────>│              │
  │                      │                    │                │               │              │
  │                      │                    │                │   "Node에 배치"│              │
  │                      │                    │                │               │─────────────>│
  │                      │                    │                │               │              │
  │                      │                    │                │               │  컨테이너 실행│
  │                      │                    │                │               │  이미지 pull  │
  │                      │                    │                │               │  프로세스 시작│
```

1. Helm이 `values.yaml`과 `templates/`를 조합하여 완성된 YAML을 생성한다.
2. 완성된 YAML을 API Server에 전송한다.
3. API Server가 etcd에 "원하는 상태(desired state)"를 저장한다.
4. Controller Manager가 "Deployment 생성됨 → ReplicaSet 필요" 판단하여 ReplicaSet을 생성한다.
5. Scheduler가 "이 Pod는 minikube 노드에 배치" 결정한다.
6. kubelet이 컨테이너를 실행한다.

---

## Step 2-2: 리소스 계층 — 우리가 만든 것들을 역추적

### Deployment → ReplicaSet → Pod → Container

```
┌──────────────────────────────────────────────────────────────┐
│  Deployment (hello-hello-world)                              │
│  "Pod 2개를 항상 유지해라"                                     │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  ReplicaSet (hello-hello-world-5f7b9c8d4)              │  │
│  │  "현재 버전의 Pod 2개를 관리"                              │  │
│  │                                                        │  │
│  │  ┌──────────────────────┐  ┌──────────────────────┐   │  │
│  │  │  Pod (..d4-abc12)     │  │  Pod (..d4-def34)     │   │  │
│  │  │                      │  │                      │   │  │
│  │  │  ┌────────────────┐  │  │  ┌────────────────┐  │   │  │
│  │  │  │  Container     │  │  │  │  Container     │  │   │  │
│  │  │  │  hello-world   │  │  │  │  hello-world   │  │   │  │
│  │  │  │  :1.0.0        │  │  │  │  :1.0.0        │  │   │  │
│  │  │  └────────────────┘  │  │  └────────────────┘  │   │  │
│  │  └──────────────────────┘  └──────────────────────┘   │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

| 리소스 | 비유 | 역할 |
|--------|------|------|
| **Deployment** | 공장장 | "이 앱을 2개 돌려라, 업데이트는 이렇게 해라" 정책 설정 |
| **ReplicaSet** | 현장 조장 | "현재 버전의 Pod를 N개 유지" 실행 담당 (직접 다룰 일 거의 없음) |
| **Pod** | 작업대 | 컨테이너가 실행되는 최소 단위. IP를 갖고, 볼륨을 공유 |
| **Container** | 작업자 | 실제 앱 프로세스 (우리의 FastAPI 서버) |

> **비유**: Deployment는 "피자 2판을 항상 진열대에 올려놔"라는 지시서다. ReplicaSet은 "지금 마르게리타 v1을 2판 만들어서 올려놔"라는 구체적 실행. Pod는 피자가 놓이는 접시. Container는 접시 위의 실제 피자다.

### Service → Endpoints → Pod

```
┌──────────────────────────────────────────────┐
│  Service (hello-hello-world)                  │
│  Type: ClusterIP                              │
│  IP: 10.96.xxx.xxx:80                         │
│                                               │
│  selector:                                    │
│    app.kubernetes.io/name: hello-world        │
│    app.kubernetes.io/instance: hello          │
│         │                                     │
│         │ 레이블이 일치하는 Pod을 자동 발견       │
│         ▼                                     │
│  ┌──────────────────────────────────────────┐ │
│  │  Endpoints                               │ │
│  │  10.244.0.5:8080  ──── Pod 1             │ │
│  │  10.244.0.6:8080  ──── Pod 2             │ │
│  └──────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

| 리소스 | 비유 | 역할 |
|--------|------|------|
| **Service** | 대표 전화번호 | 변하지 않는 IP/포트를 제공. Pod이 죽고 새로 생겨도 Service IP는 그대로 |
| **Endpoints** | 내선 번호 목록 | Service 뒤에 있는 실제 Pod IP 목록 (자동 관리됨) |

### 직접 확인해보자

```bash
kubectl get deployment,rs,pod -n hello
```

출력 예시:
```
NAME                                READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/hello-hello-world   2/2     2            2           5m

NAME                                          DESIRED   CURRENT   READY   AGE
replicaset.apps/hello-hello-world-5f7b9c8d4   2         2         2       5m

NAME                                    READY   STATUS    RESTARTS   AGE
pod/hello-hello-world-5f7b9c8d4-abc12   1/1     Running   0          5m
pod/hello-hello-world-5f7b9c8d4-def34   1/1     Running   0          5m
```

이름을 잘 보면 계층 구조가 보인다:
- `hello-hello-world` (Deployment)
- `hello-hello-world-5f7b9c8d4` (ReplicaSet — Deployment 이름 + 해시)
- `hello-hello-world-5f7b9c8d4-abc12` (Pod — ReplicaSet 이름 + 해시)

---

## Step 2-3: 요청이 Hello World에 도달하기까지

```
┌───────────┐     ┌─────────────────────┐     ┌───────────────────┐
│  브라우저   │     │  Ingress Controller  │     │     Service       │
│ / curl     │     │     (NGINX)          │     │ hello-hello-world │
│            │     │                     │     │                   │
│ hello.local│────>│ Host: hello.local   │────>│ ClusterIP:80     │
│            │     │ Path: /             │     │                   │
└───────────┘     └─────────────────────┘     └─────────┬─────────┘
                                                        │
                                                        │ kube-proxy가
                                                        │ iptables 규칙으로
                                                        │ Pod 중 하나를 선택
                                                        ▼
                                              ┌───────────────────┐
                                              │       Pod         │
                                              │  10.244.0.5:8080  │
                                              │                   │
                                              │  ┌─────────────┐  │
                                              │  │  uvicorn     │  │
                                              │  │  FastAPI     │  │
                                              │  │  main:app    │  │
                                              │  └─────────────┘  │
                                              └───────────────────┘
```

단계별로 따라가보자:

1. **브라우저/curl** → `hello.local`로 HTTP 요청을 보낸다.
2. **/etc/hosts** → `hello.local`이 Minikube IP로 해석된다.
3. **Ingress Controller (NGINX)** → Host 헤더(`hello.local`)를 보고, 우리가 정의한 Ingress 규칙에 따라 `hello-hello-world` Service로 전달한다.
4. **Service** → ClusterIP를 통해 요청을 받는다. Service는 직접 트래픽을 처리하지 않고, kube-proxy가 설정한 iptables 규칙이 실제 라우팅을 수행한다.
5. **kube-proxy (iptables)** → Endpoints에 등록된 Pod 중 하나를 랜덤(또는 라운드로빈)으로 선택한다.
6. **Pod** → 선택된 Pod의 8080 포트로 요청이 도착한다.
7. **uvicorn/FastAPI** → 요청을 처리하고 JSON 응답을 반환한다.

> **비유**: 대기업 고객센터를 생각해보자.
> - **Ingress** = 대표 전화번호 (1588-xxxx). 전화를 걸면 여기로 간다.
> - **Service** = ARS 시스템. "상담 연결을 원하시면 1번을 누르세요"
> - **kube-proxy** = 자동 분배 시스템. "현재 대기 중인 상담원에게 연결합니다"
> - **Pod** = 실제 상담원. 전화를 받아서 답변한다.

---

## Step 2-4: Helm이 해준 것

### 수동 배포 vs Helm 비교

Helm 없이 직접 배포한다면?

```bash
# 수동 배포 — 파일 하나하나 직접 적용
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# 삭제할 때도 하나하나...
kubectl delete -f ingress.yaml
kubectl delete -f service.yaml
kubectl delete -f deployment.yaml
kubectl delete -f configmap.yaml
kubectl delete -f namespace.yaml
```

Helm을 쓰면:

```bash
# 설치
helm install hello ./helm/hello-world

# 삭제
helm uninstall hello

# 업그레이드
helm upgrade hello ./helm/hello-world --set image.tag=2.0.0

# 롤백
helm rollback hello 1
```

| 항목 | 수동 (`kubectl apply`) | Helm |
|------|----------------------|------|
| 배포 | 파일 순서 직접 관리 | `helm install` 한 줄 |
| 삭제 | 역순으로 하나씩 삭제 | `helm uninstall` 한 줄 |
| 버전 관리 | 없음 (git에 의존) | `helm history`로 릴리즈 이력 추적 |
| 롤백 | YAML 수동 되돌리기 | `helm rollback` 한 줄 |
| 환경별 설정 | 파일 복사 또는 kustomize | `values-dev.yaml`, `values-prod.yaml` |
| 템플릿 | 불가 (하드코딩) | Go template으로 변수화 |

### Helm이 렌더링한 실제 YAML 확인

```bash
helm template hello ./helm/hello-world
```

이 명령은 `values.yaml` + `templates/`를 조합하여 **실제로 K8s에 적용될 최종 YAML**을 출력한다. 디버깅할 때 매우 유용하다.

### Helm 릴리즈 관리

```bash
# 현재 설치된 릴리즈 목록
helm list -A
# NAME    NAMESPACE   REVISION   STATUS     CHART              APP VERSION
# hello   default     1          deployed   hello-world-0.1.0  1.0.0

# 릴리즈 이력 (업그레이드/롤백 기록)
helm history hello
# REVISION   STATUS     CHART              APP VERSION   DESCRIPTION
# 1          deployed   hello-world-0.1.0  1.0.0         Install complete
```

### values.yaml의 역할

`values.yaml`은 Helm 차트의 **설정 변수 모음**이다. 같은 차트를 다른 환경에 배포할 때 이 파일만 바꾸면 된다.

```
동일한 templates/ ──┬── values.yaml          → 기본값
                    ├── values-dev.yaml      → 개발 환경 (replica=1, resources 작게)
                    ├── values-staging.yaml  → 스테이징 (replica=2, 운영과 동일 설정)
                    └── values-prod.yaml     → 운영 (replica=3, resources 크게)
```

---

## Step 2-5: kubectl로 까보기

이제 kubectl 명령으로 클러스터 내부를 실제로 들여다보자.

### 1. 전체 리소스 조회

```bash
kubectl get all -n hello
```

`-n hello`는 "hello 네임스페이스에서"라는 뜻이다. 네임스페이스는 K8s 리소스를 논리적으로 격리하는 폴더 같은 것이다.

### 2. Pod 상세 정보 (Events 섹션 중점)

```bash
# Pod 이름 확인
kubectl get pods -n hello

# 상세 정보 조회 (Pod 이름을 복사해서 넣기)
kubectl describe pod <pod-name> -n hello
```

출력 중 **Events** 섹션을 주목하자:

```
Events:
  Type    Reason     Age   From               Message
  ----    ------     ----  ----               -------
  Normal  Scheduled  5m    default-scheduler  Successfully assigned hello/hello-hello-world-... to minikube
  Normal  Pulled     5m    kubelet            Container image "hello-world:1.0.0" already present on machine
  Normal  Created    5m    kubelet            Created container hello-world
  Normal  Started    5m    kubelet            Started container hello-world
```

이벤트가 시간 순서대로 Pod의 라이프사이클을 보여준다:
1. Scheduler가 Node에 배치 (`Scheduled`)
2. kubelet이 이미지를 확인 (`Pulled`)
3. 컨테이너 생성 (`Created`)
4. 컨테이너 시작 (`Started`)

### 3. 앱 로그 확인

```bash
kubectl logs <pod-name> -n hello
```

출력 예시 (JSON 형태의 구조화된 로그):
```json
{"timestamp":"2026-02-26T10:00:00.000000+00:00","level":"INFO","message":"Application started: env=production, version=1.0.0, pod=hello-hello-world-...","logger":"app","pod":"hello-hello-world-..."}
```

실시간 로그를 보려면 `-f` (follow) 플래그를 추가한다:
```bash
kubectl logs -f <pod-name> -n hello
```

### 4. 컨테이너 내부 진입

```bash
kubectl exec -it <pod-name> -n hello -- sh
```

컨테이너 안에서 실행할 수 있다:
```bash
# 환경 변수 확인
env | grep APP
# APP_ENV=production
# APP_VERSION=1.0.0

# 프로세스 확인
ps aux
# PID   USER     COMMAND
# 1     appuser  uvicorn main:app --host 0.0.0.0 --port 8080 ...

# 나가기
exit
```

### 5. Endpoints 확인

```bash
kubectl get endpoints -n hello
```

출력 예시:
```
NAME                ENDPOINTS                         AGE
hello-hello-world   10.244.0.5:8080,10.244.0.6:8080   10m
```

Service 뒤에 있는 실제 Pod IP:Port 목록이다. Pod가 죽거나 Readiness 실패하면 여기서 자동으로 빠진다.

### 6. CPU/메모리 사용량 (metrics-server 필요)

```bash
kubectl top pod -n hello
```

출력 예시:
```
NAME                                    CPU(cores)   MEMORY(bytes)
hello-hello-world-5f7b9c8d4-abc12       1m           45Mi
hello-hello-world-5f7b9c8d4-def34       1m           43Mi
```

> metrics-server가 아직 데이터를 수집하지 못했다면 잠시 기다렸다가 다시 실행하자.

---

# Part 3: 실무처럼 만들기

> Part 1에서 돌렸고, Part 2에서 이해했다. 이제 실무에서 쓰는 패턴을 하나씩 실험해보자.

---

## Step 3-1: ConfigMap으로 설정 변경

### 12-Factor App: Factor 3 — 설정을 코드에서 분리하라

앱의 설정(환경, 로그 레벨, DB 주소 등)은 코드에 하드코딩하지 않고, **환경 변수**로 주입한다. K8s에서는 **ConfigMap**이 이 역할을 한다.

우리 차트의 ConfigMap을 다시 보자:

```yaml
# helm/hello-world/templates/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "hello-world.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "hello-world.labels" . | nindent 4 }}
data:
  APP_ENV: {{ .Values.config.appEnv | quote }}
  APP_VERSION: {{ .Values.app.version | quote }}
  LOG_LEVEL: {{ .Values.config.logLevel | quote }}
```

`values.yaml`의 `config.appEnv`, `config.logLevel`, `app.version` 값이 ConfigMap에 들어가고, Deployment의 `envFrom`을 통해 Pod에 환경 변수로 주입된다.

### 실습: LOG_LEVEL을 debug로 변경

```bash
# Helm upgrade로 설정 변경
helm upgrade hello ./helm/hello-world --set config.logLevel=debug
```

```bash
# Pod가 재시작되는지 확인 (ConfigMap 변경 시 Pod 재생성됨)
kubectl get pods -n hello -w
# 새 Pod가 생성되고 기존 Pod가 종료되는 것을 볼 수 있다
# (Ctrl+C로 watch 종료)

# 변경 확인
curl http://hello.local/info
# {"app_env":"production","app_version":"1.0.0","log_level":"debug","pod_name":"hello-hello-world-..."}
```

`log_level`이 `"debug"`로 바뀐 것을 확인할 수 있다.

> **주의**: ConfigMap이 변경되면 기존 Pod에는 자동 반영되지 않는다. Pod를 재시작해야 새 설정을 읽는다.
> `helm upgrade`는 Deployment spec이 바뀌면 자동으로 Rolling Update를 수행한다.

### 실무에서는: 환경별 values 파일

```bash
# 개발 환경
helm upgrade hello ./helm/hello-world -f values-dev.yaml

# 운영 환경
helm upgrade hello ./helm/hello-world -f values-prod.yaml
```

```yaml
# values-dev.yaml
replicaCount: 1
config:
  appEnv: development
  logLevel: debug
resources:
  requests:
    cpu: 50m
    memory: 64Mi
  limits:
    cpu: 100m
    memory: 128Mi
```

```yaml
# values-prod.yaml
replicaCount: 3
config:
  appEnv: production
  logLevel: warning
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

---

## Step 3-2: Health Probe 동작 실험

### Liveness vs Readiness 차이

```
                    ┌─────────────────────────────────────┐
                    │         kubelet (Health Check)       │
                    │                                     │
                    │  Liveness Probe                      │
                    │  "살아있니?"                          │
                    │  → 실패 시: 컨테이너 재시작 (kill)     │
                    │  → 용도: 데드락, 무한루프 감지         │
                    │                                     │
                    │  Readiness Probe                     │
                    │  "준비됐니?"                          │
                    │  → 실패 시: 트래픽 차단 (재시작 X)     │
                    │  → 용도: DB 연결 대기, 초기화 진행 중  │
                    └─────────────────────────────────────┘
```

핵심 차이:

| | Liveness | Readiness |
|--|----------|-----------|
| 질문 | "살아있니?" | "일할 준비됐니?" |
| 실패 시 | 컨테이너 **재시작** (kill → restart) | Endpoints에서 **제거** (트래픽 차단) |
| 비유 | 심장 박동 체크 | 출근 체크 |
| 검사 대상 | 앱 프로세스 자체 | 앱 + 의존성 (DB, 캐시 등) |

### 실습: Readiness 끄기

우리 앱에는 Readiness를 수동으로 토글하는 `/admin/toggle-ready` 엔드포인트가 있다. 이것을 이용해서 Readiness Probe가 실패하면 무슨 일이 일어나는지 실험하자.

**Step 1**: 현재 Endpoints 확인

```bash
kubectl get endpoints hello-hello-world -n hello
# NAME                ENDPOINTS                         AGE
# hello-hello-world   10.244.0.5:8080,10.244.0.6:8080   15m
# → 2개의 Pod IP가 등록되어 있다
```

**Step 2**: Readiness 토글 (하나의 Pod를 "not ready"로 만들기)

```bash
curl -X POST http://hello.local/admin/toggle-ready
# {"ready":false}
```

**Step 3**: 15초 기다린다 (failureThreshold=3 x periodSeconds=5 = 15초)

K8s는 Readiness Probe가 3번 연속 실패해야 Pod를 Endpoints에서 제거한다.

```bash
# 15초 후 Endpoints 다시 확인
kubectl get endpoints hello-hello-world -n hello
# NAME                ENDPOINTS         AGE
# hello-hello-world   10.244.0.6:8080   16m
# → Pod 하나의 IP가 사라졌다!
```

**Step 4**: 이 상태에서 요청을 보내보자

```bash
curl http://hello.local/
# {"message":"Hello World","version":"1.0.0"}
# → 다른 Pod가 응답한다! (replica=2이므로)
```

Pod가 2개이기 때문에 하나가 "not ready"가 되어도 나머지 하나가 요청을 처리한다. 만약 Pod가 1개뿐이었다면 502 에러가 발생했을 것이다.

**Step 5**: Readiness 복구

```bash
curl -X POST http://hello.local/admin/toggle-ready
# {"ready":true}

# 잠시 후 Endpoints 확인 — Pod가 다시 등록된다
kubectl get endpoints hello-hello-world -n hello
# NAME                ENDPOINTS                         AGE
# hello-hello-world   10.244.0.5:8080,10.244.0.6:8080   17m
# → 2개로 복구!
```

> **주의**: Readiness Probe가 실패해도 Pod는 **재시작되지 않는다**. 단지 트래픽을 받지 않을 뿐이다. Liveness Probe가 실패해야 재시작된다.

### 실무에서는

```python
# Readiness에 DB 연결 체크 추가
@app.get("/health/ready")
async def readiness():
    # DB 연결 확인
    if not db_pool.is_connected():
        return JSONResponse(status_code=503, content={"status": "db not connected"})
    # 캐시 연결 확인
    if not redis_client.ping():
        return JSONResponse(status_code=503, content={"status": "cache not connected"})
    return {"status": "ok"}

# Liveness에 데드락 감지 추가
@app.get("/health/live")
async def liveness():
    # 이벤트 루프가 응답하는지 자체 확인
    # (데드락 상태면 이 엔드포인트 자체가 응답하지 못함)
    return {"status": "ok"}
```

---

## Step 3-3: Resource 관리

### requests vs limits

```
┌──────────────────────────────────────────────────┐
│  Node의 전체 리소스: CPU 2000m, Memory 4Gi       │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │  Pod A                                     │  │
│  │  requests: cpu=100m, memory=128Mi          │  │
│  │  limits:   cpu=250m, memory=256Mi          │  │
│  │                                            │  │
│  │  ■■■■■□□□□□□□□  (현재 실제 사용량: 50m)    │  │
│  │  ├─────┤        requests (보장 영역)        │  │
│  │  ├───────────┤  limits (최대 한계)          │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │  Pod B                                     │  │
│  │  requests: cpu=100m, memory=128Mi          │  │
│  │  limits:   cpu=250m, memory=256Mi          │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  남은 리소스: CPU 1800m, Memory 3.75Gi           │
└──────────────────────────────────────────────────┘
```

| | requests | limits |
|--|----------|--------|
| 비유 | 최소 보장 좌석 (비행기 예약) | 절대 넘을 수 없는 한계 (짐 무게 제한) |
| 역할 | Scheduler가 "이 Pod를 어디에 배치할까?" 결정 시 사용 | 실행 중 이 이상 사용하면 제한(CPU) 또는 종료(Memory) |
| CPU 초과 시 | - | **쓰로틀링** (느려지지만 죽지는 않음) |
| Memory 초과 시 | - | **OOMKilled** (강제 종료!) |

### values.yaml에서의 위치

```yaml
# values.yaml
resources:
  requests:
    cpu: 100m       # 0.1 CPU 코어 보장
    memory: 128Mi   # 128MB 메모리 보장
  limits:
    cpu: 250m       # 최대 0.25 CPU 코어
    memory: 256Mi   # 최대 256MB 메모리
```

### 단위 설명

**CPU**:
- `1000m` = 1 CPU 코어
- `100m` = 0.1 코어 (코어의 10%)
- `250m` = 0.25 코어 (코어의 25%)

**Memory**:
- `Mi` = 메비바이트 (1Mi = 1,048,576 bytes)
- `Gi` = 기비바이트 (1Gi = 1,073,741,824 bytes)
- `128Mi` = 약 134MB

### 실제 사용량 확인

```bash
# Pod별 사용량
kubectl top pod -n hello
# NAME                                    CPU(cores)   MEMORY(bytes)
# hello-hello-world-5f7b9c8d4-abc12       1m           45Mi
# hello-hello-world-5f7b9c8d4-def34       1m           43Mi

# Node 전체 할당 가능 리소스 확인
kubectl describe node minikube | grep -A 5 "Allocatable"
# Allocatable:
#   cpu:                2
#   memory:             3956Mi
#   ...
```

> **비유**: requests/limits는 통신사 데이터 요금제와 비슷하다.
> - **requests** = 기본 데이터 (5GB 보장). 이만큼은 반드시 쓸 수 있다.
> - **limits** = 데이터 상한 (10GB). 여기까지 쓸 수 있지만, 넘으면 속도 제한(CPU) 또는 사용 중단(Memory).
> - requests가 너무 크면? 노드에 Pod를 적게 배치하게 되어 자원 낭비.
> - limits가 너무 크면? 여러 Pod가 동시에 리소스를 쓰면 노드가 과부하.

---

## Step 3-4: Graceful Shutdown 이해

Graceful Shutdown은 "앱을 종료할 때 처리 중인 요청은 마저 끝내고, 새 요청은 거부하는 것"이다.

### Pod 종료 라이프사이클

```
API Server: "이 Pod를 삭제해라"
    │
    │ (동시에 2가지가 발생!)
    │
    ├─────────────────────────┐
    │                         │
    ▼                         ▼
kubelet                   EndpointSlice Controller
    │                         │
    ▼                         ▼
1. preStop hook 실행       Endpoints에서 Pod IP 제거
   (sleep 10초)            ↓
    │                     kube-proxy가 iptables 규칙 갱신
    │                     (이 과정에 지연이 있다!)
    │
    ▼
2. SIGTERM 전송
    │
    ▼
3. FastAPI graceful shutdown
   - app_state["ready"] = False
   - app_state["shutting_down"] = True
   - 새 요청: Readiness 503 반환
   - 진행 중 요청: 완료 대기
    │
    ▼
4. 앱 종료 (또는 대기 중...)
    │
    ▼
5. terminationGracePeriodSeconds (45초) 만료 시
    │
    ▼
6. SIGKILL (강제 종료 — 앱이 뭘 하고 있든 즉시 kill)
```

### 왜 preStop hook이 필요한가?

핵심 문제: **SIGTERM 전송**과 **Endpoints에서 Pod 제거**가 **동시에** 발생한다.

```
시간 →  0초         1초         5초         10초
        │           │           │           │
SIGTERM ─┤           │           │           │
         │           │           │           │
Endpoints ─┤          │           │           │
제거 시작   │          │           │           │
            │   kube-proxy       │           │
            │   iptables 갱신 중  │           │
            │   (아직 이전 규칙!) │           │
            │                    │  갱신 완료 │
            │                    │           │
```

SIGTERM을 받자마자 앱이 종료해버리면, kube-proxy가 iptables를 갱신하기 **전에** 앱이 죽어버린다. 그 사이에 들어오는 요청은 **502 에러**를 맞는다.

해결책: **preStop hook에서 sleep을 걸어서** kube-proxy가 iptables를 갱신할 시간을 벌어준다.

```yaml
# deployment.yaml에서
lifecycle:
  preStop:
    exec:
      command:
        - /bin/sh
        - -c
        - sleep 10     # ← 10초 대기: iptables 갱신 시간 확보
```

### 종료 예산 정렬 (Termination Budget)

```
terminationGracePeriodSeconds (45초)
├── preStop sleep (10초)
├── 앱 shutdown 시간 (최대 30초: 진행 중 요청 완료 + 리소스 정리)
└── buffer (5초: 안전 여유분)

공식: termination(45) >= preStop(10) + app_shutdown(30) + buffer(5)
```

- `terminationGracePeriodSeconds`가 너무 짧으면? 앱이 요청 처리를 마치기 전에 SIGKILL로 강제 종료.
- `preStopSleepSeconds`가 너무 짧으면? iptables 갱신 전에 SIGTERM이 와서 502 발생.
- 둘 다 너무 길면? Pod 교체가 느려져서 배포 시간 증가.

### main.py의 SIGTERM 핸들러 동작

```python
def handle_sigterm(signum, frame):
    logger.info("Received SIGTERM, starting graceful shutdown...")
    app_state["shutting_down"] = True
    app_state["ready"] = False  # → Readiness Probe 503 → 새 트래픽 차단
```

이 핸들러가 하는 일:
1. `shutting_down = True` → 앱 내부에서 "종료 중"임을 인식
2. `ready = False` → Readiness Probe가 503을 반환하여 K8s가 이 Pod에 더 이상 트래픽을 보내지 않음

그리고 uvicorn이 SIGTERM을 받으면 FastAPI의 `on_shutdown` 이벤트가 실행되어 리소스를 정리한다.

### deployment.yaml의 관련 설정

```yaml
spec:
  terminationGracePeriodSeconds: 45    # SIGTERM → SIGKILL까지 45초
  containers:
    - lifecycle:
        preStop:
          exec:
            command:
              - /bin/sh
              - -c
              - sleep 10               # iptables 갱신 대기 10초
```

---

## Step 3-5: Rolling Update 무중단 배포

### Rolling Update 전략

우리 deployment.yaml에는 다음 설정이 있다:

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1         # 기존 replicas 수 대비 1개까지 추가 생성 가능
    maxUnavailable: 0   # 항상 모든 replicas가 사용 가능해야 함
```

이 설정의 의미:

```
replicas=2, maxSurge=1, maxUnavailable=0

초기 상태:  [v1 Pod A] [v1 Pod B]              (2개 Running)

Step 1:     [v1 Pod A] [v1 Pod B] [v2 Pod C]   (v2 1개 추가 생성, 총 3개)
            maxSurge=1이므로 최대 3개(2+1)까지 허용

Step 2:     [v1 Pod A] [v1 Pod B] [v2 Pod C]   (v2 Pod C가 Ready 될 때까지 대기)
                                   ~~~~~~~~
                                   Readiness 확인 중...

Step 3:     [v1 Pod A]            [v2 Pod C]   (v2 Ready → v1 Pod B 종료)
            maxUnavailable=0이므로 항상 2개 이상 Ready 유지

Step 4:     [v1 Pod A] [v2 Pod C] [v2 Pod D]   (v2 1개 더 추가)

Step 5:                [v2 Pod C] [v2 Pod D]   (v1 Pod A 종료, 완료!)
```

`maxUnavailable: 0`이 핵심이다. 이 설정 덕분에 항상 최소 2개의 Pod가 Running 상태를 유지하여 **502/503 에러 없이** 업데이트가 진행된다.

### 실습: v1 → v2 배포

**Step 1**: 앱 코드 수정

`app/main.py`에서 Hello World 메시지를 변경한다:

```python
# 변경 전
return {"message": "Hello World", "version": APP_VERSION}

# 변경 후
return {"message": "Hello World v2", "version": APP_VERSION}
```

**Step 2**: 새 이미지 빌드

```bash
# Minikube Docker 환경인지 확인 (이전에 eval 했다면 새 터미널에서는 다시 필요)
eval $(minikube docker-env)

# v2 이미지 빌드
docker build -t hello-world:2.0.0 .
```

**Step 3**: 별도 터미널에서 반복 요청 시작

```bash
# 새 터미널 열고 (이 터미널에서 502/503이 발생하는지 관찰)
while true; do curl -s http://hello.local/ && echo; sleep 0.5; done
```

출력이 계속 반복된다:
```
{"message":"Hello World","version":"1.0.0"}
{"message":"Hello World","version":"1.0.0"}
{"message":"Hello World","version":"1.0.0"}
...
```

**Step 4**: 배포 (원래 터미널에서)

```bash
helm upgrade hello ./helm/hello-world --set image.tag=2.0.0 --set app.version=2.0.0
```

**Step 5**: 관찰

반복 요청 터미널을 보면:
```
{"message":"Hello World","version":"1.0.0"}
{"message":"Hello World","version":"1.0.0"}
{"message":"Hello World v2","version":"2.0.0"}    ← 여기서 v2로 전환!
{"message":"Hello World v2","version":"2.0.0"}
{"message":"Hello World v2","version":"2.0.0"}
```

**502/503 에러 없이** v1에서 v2로 자연스럽게 전환되는 것을 확인할 수 있다.

원래 터미널에서 롤아웃 상태와 Pod 변화를 확인한다:

```bash
# 롤아웃 진행 상황
kubectl rollout status deployment/hello-hello-world -n hello
# Waiting for deployment "hello-hello-world" rollout to finish: 1 old replicas are pending termination...
# deployment "hello-hello-world" successfully rolled out

# Pod 변화 실시간 확인 (별도 터미널)
kubectl get pods -n hello -w
# NAME                                    READY   STATUS              RESTARTS   AGE
# hello-hello-world-5f7b9c8d4-abc12       1/1     Running             0          20m
# hello-hello-world-5f7b9c8d4-def34       1/1     Running             0          20m
# hello-hello-world-7a8b9c0d1-ghi56       0/1     ContainerCreating   0          2s    ← 새 Pod
# hello-hello-world-7a8b9c0d1-ghi56       1/1     Running             0          5s    ← Ready!
# hello-hello-world-5f7b9c8d4-abc12       1/1     Terminating         0          20m   ← 구 Pod 종료 시작
# ...
```

반복 요청 터미널은 `Ctrl+C`로 종료한다.

### 롤백

문제가 발생했다면 이전 버전으로 되돌릴 수 있다:

```bash
# 현재 릴리즈 이력 확인
helm history hello
# REVISION   STATUS       CHART              APP VERSION   DESCRIPTION
# 1          superseded   hello-world-0.1.0  1.0.0         Install complete
# 2          deployed     hello-world-0.1.0  1.0.0         Upgrade complete

# 이전 버전으로 롤백
helm rollback hello 1

# 확인
curl http://hello.local/
# {"message":"Hello World","version":"1.0.0"}
# → v1으로 돌아왔다!
```

---

# 정리 및 다음 단계

## 리소스 정리

```bash
# Helm 릴리즈 삭제 (모든 K8s 리소스 삭제)
helm uninstall hello

# Minikube 중지
minikube stop

# Minikube 완전 삭제 (디스크 공간 회수)
minikube delete
```

## 이 튜토리얼에서 배운 것 체크리스트

- [ ] Minikube + Helm으로 K8s 클러스터를 만들고 앱을 배포할 수 있다
- [ ] Pod, Deployment, Service, Ingress의 역할과 관계를 설명할 수 있다
- [ ] `kubectl get`, `describe`, `logs`, `exec`으로 클러스터 내부를 조사할 수 있다
- [ ] ConfigMap으로 앱 설정을 코드 변경 없이 바꿀 수 있다
- [ ] Liveness Probe와 Readiness Probe의 차이를 설명하고, 실패 시 동작을 예측할 수 있다
- [ ] requests/limits의 차이를 이해하고, 적절한 값을 설정할 수 있다
- [ ] Graceful Shutdown의 필요성과 preStop hook의 역할을 설명할 수 있다
- [ ] Rolling Update로 무중단 배포를 수행하고, 문제 시 롤백할 수 있다
- [ ] Helm의 values.yaml을 수정하여 환경별 설정을 관리할 수 있다
- [ ] 요청이 브라우저에서 Pod까지 도달하는 전체 경로를 설명할 수 있다

## 다음 단계

이 튜토리얼에서 다루지 않은 실무 필수 주제들:

| 주제 | 설명 | 왜 필요한가 |
|------|------|------------|
| **HPA** (Horizontal Pod Autoscaler) | CPU/메모리 사용량에 따라 Pod 수 자동 조절 | 트래픽 변화에 자동 대응 |
| **PDB** (PodDisruptionBudget) | Node 유지보수 시에도 최소 Pod 수 보장 | 가용성 보장 |
| **NetworkPolicy** | Pod 간 네트워크 통신 제어 | 보안 (최소 권한 원칙) |
| **Secret** | 비밀번호, API 키 등 민감 정보 관리 | ConfigMap은 평문이므로 Secret 필요 |
| **PV/PVC** (Persistent Volume) | Pod가 죽어도 유지되는 저장소 | DB, 파일 저장 |
| **Prometheus + Grafana** | 메트릭 수집 및 시각화 | 모니터링/알림 |
| **ArgoCD** | Git 기반 자동 배포 (GitOps) | CI/CD 파이프라인 |
| **Namespace + RBAC** | 팀/환경별 리소스 격리 + 접근 제어 | 멀티 팀 운영 |
