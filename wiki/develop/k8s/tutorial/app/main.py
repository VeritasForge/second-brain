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
