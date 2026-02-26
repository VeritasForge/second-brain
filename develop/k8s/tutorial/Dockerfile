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
