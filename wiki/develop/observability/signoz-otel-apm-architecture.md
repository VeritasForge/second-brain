---
tags: [opentelemetry, signoz, observability, apm, kubernetes, python]
created: 2026-10-02
---

# SigNoz와 OpenTelemetry로 구성하는 Python 서비스 APM 아키텍처

## 목차

1. 용어집
2. 전체 그림: 앱에서 SigNoz 화면까지
3. 텔레메트리 신호 세 가지: Trace(Span), Metric, Log
   - 3.1 Span
   - 3.2 Metric
   - 3.3 같은 사건의 두 가지 표현
4. OpenTelemetry 패키지 구성: API, SDK, Exporter, 계측 패키지, 자동 로더
   - 4.1 다섯 종류의 패키지
   - 4.2 SDK 내부: Provider ⊃ Processor ⊃ Exporter
   - 4.3 API만 있으면 아무 일도 하지 않는다 (no-op)
5. 전송과 저장: OTLP, OTel Collector, ClickHouse
   - 5.1 OTLP
   - 5.2 OTel Collector와 Datadog Agent 비교
   - 5.3 직접 전송과 Agent 경유
   - 5.4 ClickHouse
6. 자동 계측의 동작 원리
   - 6.1 시작: `sitecustomize`
   - 6.2 `initialize()`: SDK 조립과 계측 패키지 실행
   - 6.3 entry point로 계측 패키지 찾기
   - 6.4 함수 바꿔치기: httpx, asyncpg, FastAPI
   - 6.5 직접 돌려 보기
7. 쿠버네티스에서 Operator로 계측 주입하기
   - 7.1 Operator란
   - 7.2 Operator가 파드에 하는 일
   - 7.3 파드가 뜨는 순서
   - 7.4 재현: OTel이 없는 앱 환경에 주입 흉내 내기
   - 7.5 이 구조에서 나오는 결과
   - 7.6 Operator 방식과 직접 설치 방식
8. 자동 계측이 닿는 곳과 닿지 않는 곳
   - 8.1 라이브러리별 판정
   - 8.2 큐(SQS) 관련 관측은 세 가지로 나뉜다
   - 8.3 LLM 호출 관측과 LLM 관측 도구의 역할 분담
   - 8.4 직접 span·metric을 쓸 때
9. 같은 프로세스의 다른 OTel 사용자와 충돌: LLM 관측 도구 사례
10. SigNoz에서 보이는 것과 만들어야 하는 것
    - 10.1 자동으로 생기는 Services(APM) 화면
    - 10.2 워커 서비스의 함정: 진입점 span
    - 10.3 Breakdown(구간별 시간 분석)
    - 10.4 클라우드 지표(CloudWatch)는 별도 수집 경로
    - 10.5 대시보드 직접 구성과 JSON 보관
11. 알람과 권한
    - 11.1 알림 채널과 알람 규칙
    - 11.2 알람 규칙의 종류
    - 11.3 UI 관리와 코드 관리
    - 11.4 역할과 수정 권한
12. 운영 설계 원칙
    - 12.1 P50·P90·P99를 함께 보는 이유
    - 12.2 Apdex가 맞지 않는 서비스
    - 12.3 샘플링
    - 12.4 cardinality
    - 12.5 알람 임계값과 판정 창
13. 역할 분담: 개발 팀과 플랫폼 팀
14. 주의점
15. 정리

---

## 1. 용어집

| 용어                                         | 뜻                                                                                                   |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **APM** (Application Performance Monitoring) | 애플리케이션의 요청량, 에러, 지연을 관측하는 일                                                      |
| **OTel** (OpenTelemetry)                     | 텔레메트리(trace, metric, log)를 만들고 보내는 방법을 정한 공개 표준과 그 구현 라이브러리            |
| **SigNoz**                                   | OTel 데이터를 받아 저장하고 화면·알람을 제공하는 오픈소스 관측 백엔드. 자체 호스팅과 Cloud 판이 있음 |
| **span**                                     | 작업 한 구간의 기록(시작·끝 시각, 이름, 속성)                                                        |
| **trace**                                    | 부모-자식으로 이어진 span의 묶음. 요청 하나의 전체 경로                                              |
| **metric**                                   | 측정값을 기간별로 미리 집계한 숫자                                                                   |
| **RED**                                      | Rate(요청량), Errors(에러율), Duration(지연). 서비스 상태를 보는 기본 지표 세 가지                   |
| **OTLP** (OpenTelemetry Protocol)            | 텔레메트리를 주고받는 OTel 표준 전송 규격                                                            |
| **OTel Collector**                           | 텔레메트리를 받아 가공·중계하는 별도 프로세스                                                        |
| **ClickHouse**                               | 열(column) 단위로 저장하는 분석용 데이터베이스. SigNoz의 저장소                                      |
| **Instrumentation (계측)**                   | 코드에 텔레메트리를 남기도록 만드는 일                                                               |
| **자동 계측 (auto-instrumentation)**         | 앱 코드를 고치지 않고 라이브러리 함수를 바꿔치기해서 텔레메트리를 남기는 방식                        |
| **monkey patching**                          | 실행 중에 모듈의 함수·클래스를 다른 것으로 바꿔 끼우는 기법                                          |
| **Operator**                                 | 쿠버네티스에 추가 설치해서, 사람이 하던 반복 작업을 대신하는 프로그램                                |
| **annotation**                               | 쿠버네티스 리소스에 붙이는 "키: 값" 메모. 그 키를 아는 프로그램이 읽고 행동함                        |
| **CR / CRD** (Custom Resource / Definition)  | Operator가 쿠버네티스에 새로 추가하는 리소스 종류와 그 인스턴스                                      |
| **init container**                           | 앱 컨테이너보다 먼저 실행되고 끝나는 준비용 컨테이너                                                 |
| **노드 / 파드 / 클러스터**                   | 서버 한 대 / 앱 컨테이너가 도는 단위 / 서버 여러 대의 묶음                                           |
| **샘플링**                                   | 텔레메트리의 일부만 골라 저장하는 것                                                                 |
| **cardinality**                              | metric 속성 값 조합의 개수. 커지면 시계열 수가 폭발함                                                |
| **Apdex**                                    | 응답 시간을 사용자 만족도 점수(0~1)로 바꾼 지표                                                      |
| **P50·P90·P99**                              | 요청을 소요 시간순으로 세웠을 때 50·90·99번째 백분위 값                                              |

---

## 2. 전체 그림: 앱에서 SigNoz 화면까지

```
┌─ 앱 클러스터 ────────────────────────────────────────────┐
│ ┌─ 파드 (Python 프로세스 하나) ──────────────────┐       │
│ │ 우리 코드 / 자동 계측(httpx·FastAPI·asyncpg)   │       │
│ │      │               │               │         │       │
│ │    Tracer          Meter           Logger      │       │
│ │      ▼               ▼               ▼         │       │
│ │ TracerProvider  MeterProvider  LoggerProvider  │       │
│ │      └───────── OTLP Exporter ───────┘         │       │
│ │                      │                         │       │
│ └──────────────────────┬─────────────────────────┘       │
│                        │ OTLP/HTTP (4318)                │
│                        │                                 │
│                        │     stdout·stderr 로그          │
│                        │       └─▶ 노드 로그 수집 agent  │
│                        │                  │ 로그         │
└────────────────────────┬──────────────────┬──────────────┘
                         │                  │      AWS CloudWatch (SQS·RDS 지표)
                         │                  │         │ 별도 수집 경로(10.4절)
┌─ 관측 클러스터 ────────┬──────────────────┬─────────┬────┐
│                        ▼                  ▼         ▼    │
│   ┌──────────────────────────────────────────────────┐   │
│   │ OTel Collector (SigNoz판): 받기·가공·중계        │   │
│   └─────────────────────┬────────────────────────────┘   │
│                         ▼                                │
│                ClickHouse (저장)                         │
│                         ▲ 읽기                           │
│                query-service (조회)                      │
│                         ▲                                │
│                SigNoz 화면·알람 ──▶ Slack                │
└──────────────────────────────────────────────────────────┘
```

이 문서는 이 그림의 각 구간을 차례로 설명합니다.

- 앱 안에서 무엇이 텔레메트리를 만드는가: 3·4·6절
- 그 부품이 어떻게 파드에 들어오는가: 7절
- 어디로 어떻게 보내고 저장하는가: 5절
- 무엇이 자동으로 보이고 무엇을 만들어야 하는가: 8·10절
- 알람과 운영: 11·12절

---

## 3. 텔레메트리 신호 세 가지: Trace(Span), Metric, Log

**span은 "요청 한 건이 어디를 거쳐 얼마나 걸렸는지"를 남기는 개별 기록이고, metric은 "그런 일이 몇 번, 얼마나 자주, 얼마나 오래 걸렸는지"를 미리 집계해 둔 숫자입니다.** 같은 사건도 span으로 남기면 "이 요청이 왜 느렸나"를 파고들 수 있고, metric으로 남기면 "요즘 전체적으로 느려졌나"를 싸게 볼 수 있습니다.

| 신호                         | 한 건의 모양                        | 답하는 질문                           | 비용                         |
| ---------------------------- | ----------------------------------- | ------------------------------------- | ---------------------------- |
| 🧵 **Trace (span들의 묶음)** | 요청 하나의 호출 경로와 구간별 시간 | "**이** 요청은 왜 느렸나?"            | 요청 수에 비례해 큼          |
| 📊 **Metric**                | 시간대별로 집계된 숫자              | "**전체적으로** 얼마나, 얼마나 자주?" | 요청 수와 거의 무관하게 작음 |
| 📝 **Log**                   | 사건 한 줄과 필드                   | "그때 **무슨 일**이 있었나?"          | 줄 수에 비례                 |

### 3.1 Span

span 하나가 담는 것은 다음과 같습니다.

| 필드             | 뜻                                                                              | 예시                            |
| ---------------- | ------------------------------------------------------------------------------- | ------------------------------- |
| `trace_id`       | 이 span이 속한 요청 전체의 ID. 서비스를 넘어가도 같음                           | `4bf92f35…`                     |
| `span_id`        | 이 구간 자체의 ID                                                               | `00f067aa…`                     |
| `parent_span_id` | 나를 부른 구간의 ID. 없으면 루트 span                                           |                                 |
| `name`           | 구간 이름                                                                       | `POST /process`                 |
| `kind`           | 역할: SERVER(요청을 받음), CLIENT(요청을 보냄), INTERNAL, PRODUCER/CONSUMER(큐) | `CLIENT`                        |
| 시작·끝 시각     | 둘의 차이가 소요 시간                                                           | 1.8초                           |
| `attributes`     | 키-값 부가 정보                                                                 | `http.response.status_code=503` |
| `status`         | 성공(OK·UNSET)인지 실패(ERROR)인지                                              | `ERROR`                         |
| `events`         | 구간 도중의 시점 기록. 예외가 대표적                                            | `exception`                     |

**trace 한 건의 예시.** 큐 소비 워커가 내부 API 서버를 부르고, API 서버가 LLM을 세 번 부르는 경우입니다.

```
trace_id = 4bf9…   (한 요청 전체)
│
├─ [worker] POST http://api-server/process          CLIENT   0.0s ─────────────────── 9.2s
│   └─ [api-server] POST /process                    SERVER    0.1s ───────────────── 9.1s
│        ├─ [api-server] pipeline.run                INTERNAL   0.1s ──────────────── 9.0s
│        │    ├─ POST https://…/generateContent      CLIENT      0.2s ──── 3.1s       ← LLM 1번째
│        │    ├─ POST https://…/generateContent      CLIENT             3.2s ── 5.9s  ← LLM 2번째
│        │    └─ POST https://…/generateContent      CLIENT                   6.0s ─ 8.9s
│        └─ (응답 직렬화)
└─ [worker] INSERT … (asyncpg)                       CLIENT                            9.3s
```

이 한 장만 보면 "9초 중 LLM 세 번이 약 8.5초를 썼다"를 바로 알 수 있습니다. 로그만으로는 서비스 세 곳의 줄을 시각으로 맞춰 봐야 알 수 있는 내용입니다.

**서비스를 넘어 이어지는 원리 (context propagation).**

```
 worker (CLIENT span 생성)                          api-server
   httpx 요청 헤더에 자동으로 실음:
   traceparent: 00-4bf92f35…-00f067aa…-01  ───────▶ FastAPI 계측이 헤더를 읽음
                  └ trace_id ┘ └ 부모 span_id ┘     → 같은 trace_id로 SERVER span 생성
```

HTTP는 헤더가 있어서 자동 계측이 알아서 이어 줍니다. 반면 **큐 메시지에는 누가 이 값을 실어 주지 않으면** trace가 끊깁니다(8.2절).

### 3.2 Metric

**metric은 측정값을 앱 안에서 미리 집계해 두었다가, 일정 주기로 숫자만 내보내는 신호**입니다. 요청 1만 건이 들어와도 레코드 1만 개를 보내지 않습니다. "지난 60초 동안 1만 건, 그중 503이 12건, 지연 분포는 이러함"이라는 요약 몇 개만 보냅니다(내보내기 주기의 기본값 60초는 확인 필요).

**계기(instrument)의 종류** (OTel 공식 문서 기준):

| 계기                              | 공식 정의 요지                                                                   | 예시                                    |
| --------------------------------- | -------------------------------------------------------------------------------- | --------------------------------------- |
| **Counter**                       | 누적되며 **올라가기만** 하는 값 (자동차 주행 거리계)                             | 작업 결과별 건수, 메시지 누락 건수      |
| **UpDownCounter**                 | 누적되지만 **내려가기도** 하는 값 (예: 큐 길이)                                  | 현재 동시 실행 중인 작업 수             |
| **Gauge**                         | 읽는 **그 순간의 현재 값** (연료 게이지)                                         | 진행 중 요청 수, 스레드풀 크기          |
| **Histogram**                     | 값의 **분포**를 앱 쪽에서 집계 (예: 요청 지연)                                   | API 지연, 외부 호출 지연                |
| **Asynchronous(Observable) 계열** | 위와 같지만, 코드가 값을 밀어 넣지 않고 **내보낼 때마다 콜백으로 한 번 읽어 감** | 이미 변수에 있는 값을 읽기만 하면 될 때 |

**SDK 안의 metric 구성 요소:**

| 구성 요소           | 역할                                                                           |
| ------------------- | ------------------------------------------------------------------------------ |
| **MeterProvider**   | Meter를 만드는 공장. 앱 기동 시 한 번 초기화                                   |
| **Meter**           | 계기(Counter, Histogram 등)를 만듦. 보통 모듈마다 하나                         |
| **Aggregation**     | 측정값 여러 개를 한 기간의 통계로 합침                                         |
| **View**            | 어떤 계기를 내보낼지, 어떤 속성만 남길지, 히스토그램 구간을 어떻게 나눌지 조정 |
| **Metric Exporter** | 집계 결과를 OTLP로 Collector에 보냄                                            |

### 3.3 같은 사건의 두 가지 표현

API 호출 한 건이 503으로 끝났다고 해 보겠습니다.

```
 사건: worker → api-server POST /process, 0.02초, 503

 Span 으로 남기면                          Metric 으로 남기면
 ┌────────────────────────────────┐        ┌────────────────────────────────────┐
 │ trace_id=…  span_id=…          │        │ http.client 지연 히스토그램        │
 │ name=POST /process             │        │   {server=api-server, status=503}  │
 │ duration=0.02s                 │        │   0~0.05초 구간 카운트 += 1        │
 │ status_code=503  status=ERROR  │        │ (주기마다 구간별 누적값만 전송)    │
 │ 부모: 작업 처리 span           │        └────────────────────────────────────┘
 └────────────────────────────────┘
 → "이 작업이 왜 실패했나"                 → "지난 1시간 503 비율이 몇 %인가"
```

| 구분           | Span                             | Metric                |
| -------------- | -------------------------------- | --------------------- |
| 단위           | 사건 하나                        | 기간별 집계           |
| 세부 정보      | 풍부함 (속성, 부모 관계, 예외)   | 적음 (정해 둔 속성만) |
| 저장·전송 비용 | 요청 수에 비례                   | 거의 일정             |
| 샘플링         | 비용 때문에 자주 함              | 하지 않음. 전부 셈    |
| 알람           | 샘플링되면 수치가 왜곡될 수 있음 | ✅ 적합               |
| 잘하는 것      | 원인 추적, 병목 구간 찾기        | 추세, SLO, 용량 계획  |

같은 사건을 span(고유 ID를 달아 개별 추적)과 metric(닫힌 값 집합만 달아 집계)으로 **동시에** 남기는 것이 일반적인 패턴입니다(코드는 8.4절).

---

## 4. OpenTelemetry 패키지 구성: API, SDK, Exporter, 계측 패키지, 자동 로더

흔한 오해가 두 가지 있습니다.

1. **TracerProvider, MeterProvider, LoggerProvider가 OTLP Exporter인 것은 아닙니다.** Provider는 "기록을 받아 관리하는 쪽"이고, OTLP Exporter는 그 아래에 붙는 "밖으로 보내는 부품" 중 하나입니다.
2. **SDK만 설치한다고 자동 계측이 되지는 않습니다.** 자동 계측은 라이브러리별 **계측 패키지**가 하고, 파이썬이 시작할 때 이 패키지들을 찾아 실행해 주는 **자동 로더**가 따로 있습니다.

### 4.1 다섯 종류의 패키지

```
 ┌──────────────────────────── 파이썬 프로세스 하나 ─────────────────────────────┐
 │  ⑤ 자동 로더 (opentelemetry-instrumentation + distro)                         │
 │     파이썬 시작 시 실행 → ③ SDK 조립 + ④ 계측 패키지들 실행                   │
 │            │                                │                                 │
 │            ▼                                ▼                                 │
 │  ④ 계측 패키지 (instrumentation-httpx, -fastapi, -asyncpg …)                  │
 │     httpx·FastAPI·asyncpg 함수를 바꿔치기 → 호출될 때마다 ① API로 span 생성   │
 │            │                                                                  │
 │            ▼                                                                  │
 │  ① API (opentelemetry-api)  ← 우리 코드가 직접 span을 만들 때도 여기를 씀     │
 │            │                                                                  │
 │            ▼                                                                  │
 │  ③ SDK (opentelemetry-sdk)                                                    │
 │     TracerProvider ─▶ BatchSpanProcessor ─▶ ② Exporter ───────────────────────┼─▶ Collector
 │     MeterProvider  ─▶ PeriodicExportingMetricReader ─▶ ② Exporter             │
 │     LoggerProvider ─▶ BatchLogRecordProcessor ─▶ ② Exporter                   │
 └───────────────────────────────────────────────────────────────────────────────┘
   ② Exporter 의 종류: OTLP Exporter(Collector로 보냄), Console Exporter(터미널에 찍음) 등
```

| 패키지                                                     | 역할                                                                 | 비유                                        |
| ---------------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------- |
| ① `opentelemetry-api`                                      | span·metric을 **기록하는 함수 모음**. 혼자서는 아무것도 하지 않음    | 편지지와 펜                                 |
| ③ `opentelemetry-sdk`                                      | 기록을 받아 **모으고, 묶고, 내보낼 곳에 넘김** (Provider, Processor) | 우체국 창구                                 |
| ② `opentelemetry-exporter-otlp-*`                          | **실제로 네트워크로 보냄** (OTLP 형식)                               | 배달 트럭                                   |
| ④ `opentelemetry-instrumentation-<라이브러리>`             | 특정 라이브러리 함수를 바꿔치기해 **자동으로 span을 씀**             | 대신 편지를 써 주는 대필가                  |
| ⑤ `opentelemetry-instrumentation` + `opentelemetry-distro` | 시작할 때 ③을 조립하고 ④를 모두 실행                                 | 아침에 창구를 열고 대필가를 배치하는 관리자 |

### 4.2 SDK 내부: Provider ⊃ Processor ⊃ Exporter

자동 로더가 SDK를 조립하는 실제 코드입니다(`opentelemetry/sdk/_configuration/__init__.py`, SDK 1.45.0).

```python
def _init_tracing(exporters, ..., sampler=None, resource=None, ...):
    provider = TracerProvider(            # Provider: span 을 받아 관리
        sampler=sampler,
        resource=resource,                #   service.name 같은 공통 정보
    )
    set_tracer_provider(provider)         # 전역으로 등록 → API 가 이걸 찾아 씀

    export_processor = export_span_processor or BatchSpanProcessor
    for _, exporter_class in exporters.items():
        # Provider 에 Processor 를 붙이고, Processor 안에 Exporter 를 넣는다
        provider.add_span_processor(export_processor(exporter_class(**exporter_args)))
```

```
 TracerProvider
   └─ BatchSpanProcessor        (span 을 메모리에 모았다가 묶어서 넘김)
        └─ OTLPSpanExporter     (OTLP/HTTP 로 Collector 에 보냄)
```

어떤 Exporter를 쓸지는 환경변수가 정합니다. distro의 기본값은 다음과 같습니다(`opentelemetry/distro/__init__.py`, 0.66b0).

```python
os.environ.setdefault(OTEL_TRACES_EXPORTER, "otlp")
os.environ.setdefault(OTEL_METRICS_EXPORTER, "otlp")
os.environ.setdefault(OTEL_LOGS_EXPORTER, "otlp")
os.environ.setdefault(OTEL_EXPORTER_OTLP_PROTOCOL, "grpc")   # ← distro 의 기본은 gRPC
```

SDK가 프로세스 안에서 하는 일은 다음과 같습니다.

```
 ┌─────────────────────── 앱 파드 (Python 프로세스 하나) ───────────────────────┐
 │  우리 코드: with tracer.start_as_current_span("job.run"):                    │
 │     ▼                                                                        │
 │  TracerProvider ── span 끝남 ──▶ BatchSpanProcessor                          │
 │                                   │ 메모리 큐에 쌓아 둠                      │
 │                                   │ 백그라운드 스레드가 몇 초마다 묶음 전송  │
 │                                   ▼                                          │
 │                                OTLP Exporter ────────────────────────────────┼──▶ Collector
 └──────────────────────────────────────────────────────────────────────────────┘
```

- span을 기록하는 호출은 **메모리에 레코드를 만드는 일**뿐이라 빠릅니다. 네트워크 전송은 백그라운드 스레드가 따로 합니다.
- 프로세스가 갑자기 죽으면 **아직 보내지 못한 span은 사라집니다.**
- 전송이 실패하면 SDK가 몇 번 재시도하고, 그래도 안 되면 버립니다. 앱 자체는 실패하지 않습니다.

### 4.3 API만 있으면 아무 일도 하지 않는다 (no-op)

OTel API는 SDK가 등록되기 전까지 **아무 일도 하지 않도록(no-op)** 설계되어 있습니다.

```
 우리 코드 ── tracer.start_as_current_span() ──▶ OTel API
                                                   │
                         SDK(TracerProvider + Exporter)가 등록돼 있나?
                         ├─ 아니요 → NonRecordingSpan: 기록도 전송도 안 함 (no-op)
                         └─ 예     → span 기록 → OTLP Exporter → Collector
                                          ↑
                          이 부분은 코드가 아니라 배포 설정이 채운다
                          (Operator 주입, 또는 SDK 초기화 + 엔드포인트 환경변수)
```

SDK 없이 실행해 보면 이렇습니다.

```python
from opentelemetry import trace, metrics

s = trace.get_tracer("x").start_span("a")
print("span:", type(s).__name__, "recording=", s.is_recording())
print("provider:", type(trace.get_tracer_provider()).__name__,
      "| meter provider:", type(metrics.get_meter_provider()).__name__)
```

```
span: NonRecordingSpan recording= False
provider: ProxyTracerProvider | meter provider: _ProxyMeterProvider
```

그래서 **코드에 span을 먼저 넣어 두는 것은 안전합니다.** 계측이 켜지기 전까지는 조용히 아무 일도 하지 않고, 계측을 켜면 같은 코드가 진짜 span을 만듭니다.

---

## 5. 전송과 저장: OTLP, OTel Collector, ClickHouse

### 5.1 OTLP

**OTLP는 텔레메트리 데이터를 주고받을 때 쓰는 OTel 표준 전송 규격입니다.** "어떤 모양으로 담아서, 어떤 통로로 보내는가"를 정해 둔 약속이고, 비유하면 **규격 봉투**입니다. 보내는 쪽과 받는 쪽이 같은 규격을 쓰므로 제조사가 달라도 주고받을 수 있습니다.

```
 [앱 SDK] ──OTLP──▶ [OTel Collector] ──OTLP──▶ [다른 Collector 또는 백엔드]
```

| 항목         | 내용                                                                                               |
| ------------ | -------------------------------------------------------------------------------------------------- |
| 담는 방식    | Protocol Buffers(protobuf: 바이너리 직렬화 형식)로 인코딩                                          |
| 통로 두 가지 | **gRPC** (보통 4317 포트), **HTTP** (보통 4318 포트, 경로 `/v1/traces`, `/v1/metrics`, `/v1/logs`) |

**Datadog과 비교하면:** Datadog은 라이브러리와 Agent 사이에 전용 형식을 씁니다. OTLP는 공개 표준이라서, 앱 코드를 바꾸지 않고 받는 쪽만 다른 제품으로 갈아끼울 수 있습니다.

### 5.2 OTel Collector와 Datadog Agent 비교

**SigNoz의 수집기는 OTel Collector를 SigNoz 저장소(ClickHouse)에 맞게 조정한 배포판입니다.** 받는 방식(OTLP)은 표준 Collector와 같습니다.

```
 [앱 SDK] ──OTLP──▶ [SigNoz OTel Collector] ──▶ [ClickHouse] ◀── [query-service] ◀── SigNoz 화면
                     = OTel Collector의 SigNoz판   (저장)            (조회)
```

Datadog과 1:1로 맞추면 다음과 같습니다. **OTel SDK는 Datadog Agent가 아니라 Datadog의 트레이싱 라이브러리(`ddtrace`)에 해당하고, Agent 역할은 OTel Collector가 맡습니다.**

```
 ┌───────────── Datadog ─────────────┐        ┌───────── OTel + SigNoz ──────────┐
 │ [앱 프로세스]                     │        │ [앱 프로세스]                    │
 │   우리 코드                       │        │   우리 코드                      │
 │     ▼                             │        │     ▼                            │
 │   ddtrace (tracer + 버퍼 + 전송)  │   ⇔    │   OTel API → OTel SDK            │
 │     │ localhost                   │        │     │ OTLP/HTTP                  │
 │     ▼                             │        │     ▼                            │
 │ [노드 데몬] Datadog Agent         │   ⇔    │ [수집기] OTel Collector          │
 │     │ (배치·샘플링·태그 보강)     │        │     │ (배치·샘플링·속성 가공)    │
 │     ▼                             │        │     ▼                            │
 │ [SaaS] Datadog 백엔드             │   ⇔    │ [백엔드] SigNoz (저장소 + 화면)  │
 └───────────────────────────────────┘        └──────────────────────────────────┘
```

| 역할                        | Datadog                   | OTel + SigNoz      | 어디서 도나        |
| --------------------------- | ------------------------- | ------------------ | ------------------ |
| 기록 인터페이스             | `ddtrace` API             | OTel API           | 앱 프로세스 안     |
| 모으고, 버퍼에 담고, 보내기 | `ddtrace`의 tracer·writer | **OTel SDK**       | **앱 프로세스 안** |
| 중계·가공                   | **Datadog Agent**         | **OTel Collector** | 별도 프로세스      |
| 저장·조회·화면              | Datadog SaaS              | SigNoz             | 관측 클러스터      |

### 5.3 직접 전송과 Agent 경유

OTel에서는 두 구조를 모두 쓸 수 있습니다.

```
 직접 전송                                         Agent 경유 (Datadog과 같은 구조)
 [앱 파드: OTel SDK]                               [앱 파드: OTel SDK]
      │ OTLP/HTTP (네트워크를 건넘)                     │ 같은 노드 (가까움)
      ▼                                                 ▼
 관측 클러스터의 OTel Collector                    [같은 노드: OTel Collector (DaemonSet)]
      ▼                                                 ▼
 SigNoz                                            관측 클러스터의 OTel Collector → SigNoz
```

| 방식           | 장점                                                                             | 단점                                                                                                     |
| -------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **직접 전송**  | 구성이 단순함. 노드마다 띄울 것이 없음                                           | 네트워크가 끊기면 SDK의 작은 메모리 버퍼만으로 버팀. 파드·노드 정보(k8s 메타데이터)를 중앙에서 붙여야 함 |
| **Agent 경유** | 앱은 가까운 곳으로 보내므로 빠르고 안정적. Agent가 버퍼링·재시도·메타데이터 보강 | 노드마다 데몬을 운영해야 함                                                                              |

노드 비유로 다시 풀면, Agent 경유는 **층마다 우편 담당자가 있어 사무실(파드)은 건네기만 하면 되는** 구조이고, 직접 전송은 **사무실이 옆 건물(관측 클러스터)의 우편 센터까지 직접 가져가는** 구조입니다. 어느 쪽이 틀린 것은 아니며, 어느 구조를 쓰는지는 계측 설정의 exporter 주소가 같은 노드를 가리키는지, 원격 주소를 가리키는지로 알 수 있습니다.

참고로 SigNoz의 `k8s-infra` 차트는 노드마다 뜨는 OTel Collector를 설치해 파드 로그와 노드·쿠버네티스 지표를 모읍니다. 이 agent가 앱의 OTLP까지 받도록 해서 Agent 경유 구조로 쓸 수 있는지는 구성에 따라 다릅니다(확인 필요).

### 5.4 ClickHouse

**ClickHouse는 대량의 데이터를 빠르게 집계하는 데 특화된 오픈소스 데이터베이스입니다.** SigNoz는 span, metric, log를 모두 ClickHouse에 저장하고, 화면의 그래프와 검색은 ClickHouse에 질의해서 그립니다. 핵심은 **열 단위 저장**입니다.

```
 span 표:  | 시각 | 서비스 | 엔드포인트 | 상태 | 소요 시간 | trace_id | … (컬럼 수십 개)

 행 단위 저장 (PostgreSQL 등)              열 단위 저장 (ClickHouse)
 [시각,서비스,엔드포인트,상태,시간,…]      [시각, 시각, 시각, …]
 [시각,서비스,엔드포인트,상태,시간,…]      [서비스, 서비스, 서비스, …]
 [시각,서비스,엔드포인트,상태,시간,…]      [소요 시간, 소요 시간, …]   ← 이 열만 읽으면 됨

 질문: "지난 1시간 api-server 의 P99 지연은?"
 → 행 저장: 모든 행을 통째로 읽어야 함     → 열 저장: '서비스'와 '소요 시간' 열만 읽음
```

| 텔레메트리의 성격                        | ClickHouse가 잘 맞는 이유                              |
| ---------------------------------------- | ------------------------------------------------------ |
| 초당 수천~수만 건이 계속 쌓임            | 대량 추가(append)에 최적화                             |
| 한 번 쌓이면 거의 고치지 않음            | 수정·삭제가 드물다는 전제로 설계                       |
| "몇 건, 평균, P99" 같은 집계를 주로 물음 | 필요한 열만 읽고, 같은 열의 비슷한 값끼리 압축이 잘 됨 |

**개발자 관점에서 중요한 점:** span 속성과 로그에 무엇을 싣느냐가 곧 ClickHouse에 무엇이 저장되느냐입니다. 민감한 원문이 속성에 실리면 그대로 저장됩니다(9·14절).

---

## 6. 자동 계측의 동작 원리

**자동 계측의 실체는 "원래 함수를 span을 여는 함수로 바꿔치기(monkey patching)"하는 것입니다.** 이 절의 코드는 `opentelemetry-instrumentation` 0.66b0, `opentelemetry-sdk` 1.45.0을 설치해 확인한 실제 소스입니다.

### 6.1 시작: `sitecustomize`

파이썬은 시작할 때 `sys.path`에서 **`sitecustomize`라는 이름의 모듈을 찾으면 자동으로 import**합니다. 우리 코드보다 먼저 실행됩니다. OTel은 이 규칙을 이용합니다. 실제 파일은 두 줄입니다.

```python
# opentelemetry/instrumentation/auto_instrumentation/sitecustomize.py
from opentelemetry.instrumentation.auto_instrumentation import initialize

initialize()
```

이 폴더를 `PYTHONPATH`에 넣는 방법은 두 가지입니다.

- **`opentelemetry-instrument` 명령:** `opentelemetry-instrument python app.py`처럼 앱을 감싸서 실행하면 이 폴더를 `PYTHONPATH`에 넣고 앱을 띄웁니다.
- **쿠버네티스 Operator:** 파드에 파일을 복사해 두고 `PYTHONPATH`를 설정합니다(7절).

### 6.2 `initialize()`: SDK 조립과 계측 패키지 실행

```python
# opentelemetry/instrumentation/auto_instrumentation/__init__.py (_initialize)
distro = _load_distro()           # distro 찾기 (기본 설정값 담당)
distro.configure()
_load_configurators()             # ← 4.2절의 _init_tracing 등이 여기서 돈다 (SDK 조립)
_load_instrumentors(distro)       # ← 설치된 계측 패키지를 전부 찾아 실행
```

### 6.3 entry point로 계측 패키지 찾기

계측 패키지는 설치될 때 **"나는 `opentelemetry_instrumentor` 그룹에 속한다"**고 패키지 메타데이터(`entry_points.txt`)에 등록합니다.

```ini
[opentelemetry_instrumentor]
httpx = opentelemetry.instrumentation.httpx:HTTPXClientInstrumentor

[opentelemetry_instrumentor]
fastapi = opentelemetry.instrumentation.fastapi:FastAPIInstrumentor

[opentelemetry_instrumentor]
asyncpg = opentelemetry.instrumentation.asyncpg:AsyncPGInstrumentor
```

로더는 이 그룹을 훑어서 하나씩 실행합니다(`_load.py`).

```python
for entry_point in entry_points(group="opentelemetry_instrumentor"):
    if entry_point.name in package_to_exclude:      # OTEL_PYTHON_DISABLED_INSTRUMENTATIONS 로 끌 수 있음
        continue
    try:
        ...
        distro.load_instrumentor(entry_point, skip_dep_check=True)   # → Instrumentor().instrument()
    except ModuleNotFoundError as exc:
        # 대상 라이브러리가 설치돼 있지 않으면 조용히 건너뜀
        _logger.debug("Skipping instrumentation %s: %s", entry_point.name, exc.msg)
        continue
    except ImportError:
        # Operator 주입 환경에서 바이너리 확장이 필요한 계측이 파이썬 버전·libc 차이로
        # 못 올라오면, 전체를 실패시키지 않고 그 계측 하나만 건너뜀
        _logger.exception("Importing of %s failed, skipping it", entry_point.name)
        continue
```

그래서 계측 패키지가 50개 넘게 깔려 있어도 **앱에 설치된 라이브러리에 해당하는 것만** 실제로 적용됩니다.

### 6.4 함수 바꿔치기: httpx, asyncpg, FastAPI

**httpx:** 요청을 실제로 보내는 메서드를 감쌉니다.

```python
def _instrument(self, **kwargs):
    ...
    wrap_function_wrapper(                       # wrapt 라이브러리의 바꿔치기 함수
        "httpx",
        "HTTPTransport.handle_request",          # 동기 클라이언트
        partial(self._handle_request_wrapper, tracer=tracer, ...),
    )
    wrap_function_wrapper(
        "httpx",
        "AsyncHTTPTransport.handle_async_request",   # 비동기 클라이언트
        partial(self._handle_async_request_wrapper, tracer=tracer, ...),
    )
```

감싼 함수 안에서는 span을 열고, 요청 헤더에 `traceparent`를 넣고(`inject(_headers)`), 원래 함수를 부른 뒤 응답 코드를 기록합니다.

```python
with self._tracer.start_as_current_span(span_name, kind=SpanKind.CLIENT, attributes=span_attributes) as span:
    ...
    response = await self._transport.handle_async_request(*args, **kwargs)   # 원래 함수 호출
```

원리만 단순화하면 이런 모양입니다(개념 코드).

```python
원래_send = httpx.AsyncClient.send

async def 감싼_send(self, request, **kwargs):
    with tracer.start_as_current_span(f"{request.method}", kind=SpanKind.CLIENT) as span:
        span.set_attribute("http.request.method", request.method)
        inject(request.headers)              # traceparent 헤더 → 받는 서버가 같은 trace로 이음
        response = await 원래_send(self, request, **kwargs)
        span.set_attribute("http.response.status_code", response.status_code)
        return response

httpx.AsyncClient.send = 감싼_send          # 파이썬 시작 시 한 번 바꿔치기
```

**asyncpg:** 쿼리를 실행하는 메서드 다섯 개를 감쌉니다.

```python
for method in [
    "Connection.execute",
    "Connection.executemany",
    "Connection.fetch",
    "Connection.fetchval",
    "Connection.fetchrow",
]:
    wrapt.wrap_function_wrapper("asyncpg.connection", method, self._do_execute)

async def _do_execute(self, func, instance, args, kwargs):
    name = args[0] ...                          # SQL 문장의 첫 단어 (SELECT, INSERT …) → span 이름
    span_attributes = _hydrate_span_from_args(
        instance,
        args[0],                                 # SQL 문장
        args[1:] if self.capture_parameters else None,   # 바인딩 값: 기본값 False 라 안 남김
        ...
    )
    with self._tracer.start_as_current_span(name, kind=SpanKind.CLIENT, attributes=span_attributes) as span:
        try:
            result = await func(*args, **kwargs)   # 원래 쿼리 실행
        except Exception as exc:
            exception = exc
            raise
        finally:
            if span.is_recording() and exception is not None:
                span.set_status(Status(StatusCode.ERROR))   # 실패하면 span 을 ERROR 로
    return result
```

`capture_parameters`의 기본값은 `False`입니다(`__init__(self, capture_parameters=False)`). 기본 설정에서는 SQL 바인딩 값이 span에 남지 않습니다.

**FastAPI:** 함수가 아니라 **`FastAPI` 클래스 자체를 바꿔치기**합니다.

```python
def _instrument(self, **kwargs):
    self._original_fastapi = fastapi.FastAPI
    fastapi.FastAPI = _InstrumentedFastAPI      # 계측된 하위 클래스로 교체

class _InstrumentedFastAPI(fastapi.FastAPI):
    ...                                          # 앱을 만들 때 OpenTelemetryMiddleware(ASGI)를 끼움
```

이 교체는 `sitecustomize`에서, 즉 **앱 코드가 `from fastapi import FastAPI`를 하기 전에** 일어납니다. 그래서 앱이 `FastAPI(...)`를 부르면 사실은 계측된 클래스가 만들어지고, 요청이 들어올 때마다 미들웨어가 SERVER span을 엽니다.

### 6.5 직접 돌려 보기

평범하게 `httpx.AsyncClient`로 요청 하나를 보내는 스크립트입니다.

```python
# demo.py
import asyncio, httpx

print("handle_async_request =", type(httpx.AsyncHTTPTransport.handle_async_request).__name__)

async def main():
    async with httpx.AsyncClient() as client:   # 앱 코드는 평소처럼 호출만 한다
        r = await client.get("http://127.0.0.1:8765/")
        print("status =", r.status_code)

asyncio.run(main())
```

```bash
uv venv -p 3.14 otel-demo
VIRTUAL_ENV=$PWD/otel-demo uv pip install httpx \
  opentelemetry-distro opentelemetry-exporter-otlp-proto-http opentelemetry-instrumentation-httpx
otel-demo/bin/python -m http.server 8765 &

# A. 그냥 실행
otel-demo/bin/python demo.py

# B. 자동 계측으로 실행 (Exporter 를 console 로)
OTEL_SERVICE_NAME=demo OTEL_TRACES_EXPORTER=console \
OTEL_METRICS_EXPORTER=none OTEL_LOGS_EXPORTER=none \
  otel-demo/bin/opentelemetry-instrument otel-demo/bin/python demo.py
```

**A 결과**

```
handle_async_request = function
status = 200
```

**B 결과**

```
handle_async_request = BoundFunctionWrapper      ← 같은 메서드가 감싼 함수로 바뀌어 있음
status = 200
{
    "name": "GET",
    "kind": "SpanKind.CLIENT",
    "parent_id": null,
    "attributes": {
        "http.method": "GET",
        "http.url": "http://127.0.0.1:8765/",
        "http.status_code": 200
    },
    "resource": { "attributes": { "service.name": "demo" } }
}
```

스크립트 코드는 한 줄도 바뀌지 않았는데, B에서는 메서드가 `BoundFunctionWrapper`(wrapt가 감싼 함수)로 바뀌어 있고 요청 하나에 span 하나가 자동으로 생겼습니다.

---

## 7. 쿠버네티스에서 Operator로 계측 주입하기

**Operator가 파드에서 하는 일은 6절의 `opentelemetry-instrument` 명령이 하는 일을 쿠버네티스 방식으로 대신하는 것입니다.** 정확히는 OTel 패키지 묶음을 **파일로 파드에 복사**하고, 파이썬이 시작할 때 그 안의 **`sitecustomize`를 먼저 찾도록 `PYTHONPATH`를 설정**하는 두 가지만 합니다. SDK 조립과 함수 바꿔치기는 6절과 똑같이 파이썬 프로세스 안에서 일어납니다.

### 7.1 Operator란

**Operator는 쿠버네티스 기본 구성품이 아니라, 필요한 쪽이 클러스터에 추가로 설치하는 프로그램**입니다. "Operator"는 원래 특정 제품 이름이 아니라 "사람 운영자(operator)가 하던 반복 작업을 프로그램이 대신하게" 쿠버네티스를 확장하는 방식을 부르는 이름이고, OpenTelemetry Operator는 그 방식으로 만든 제품입니다. 보통 helm으로 **클러스터마다 한 번** 설치하고, 설치에는 cluster-admin 권한이 필요합니다.

| 구분                     | 예시                                                   | 누가 넣나              |
| ------------------------ | ------------------------------------------------------ | ---------------------- |
| k8s 기본 구성품          | API 서버, 스케줄러, Deployment, Service                | 쿠버네티스에 원래 있음 |
| **Operator** (추가 설치) | OpenTelemetry Operator, cert-manager, 각종 DB Operator | 필요한 쪽이 설치       |

OpenTelemetry Operator가 클러스터에 더하는 것은 두 가지입니다.

```
 OpenTelemetry Operator 설치
   ├─ ① 새 리소스 종류: Instrumentation (CRD)
   │     └ "SDK를 넣을 때 쓸 설정" (보낼 주소, 샘플링, 전파 방식 등). 네임스페이스마다 하나
   │
   └─ ② 파드 생성 가로채기 (mutating webhook)
         └ 파드가 만들어지기 직전에 쿠버네티스가 Operator에게 먼저 보여 줌
           → Operator가 파드 설계도를 고쳐서 돌려줌
```

서비스 쪽에서 할 일은 Deployment에 **annotation 한 줄**을 다는 것입니다.

```yaml
# Deployment (일부)
spec:
  template:
    metadata:
      annotations:
        instrumentation.opentelemetry.io/inject-python: "default"
        #  └ OpenTelemetry Operator만 알아듣는 키      └ 같은 네임스페이스의 "default" Instrumentation 을 써라
    spec:
      containers:
        - name: api-server
          env:
            - name: OTEL_SERVICE_NAME
              value: api-server
```

Instrumentation 리소스의 예시입니다.

```yaml
apiVersion: opentelemetry.io/v1alpha1
kind: Instrumentation
metadata:
  name: default
  namespace: my-namespace          # 대상 파드와 같은 네임스페이스여야 함
spec:
  exporter:
    endpoint: https://otlp.observability.example.internal   # Collector 주소 (SDK가 /v1/traces 등을 붙임)
  propagators:
    - tracecontext
    - baggage
  sampler:
    type: parentbased_traceidratio
    argument: "1.0"                # 전량 수집
  resource:
    resourceAttributes:
      deployment.environment: dev
  python:
    env:
      - name: OTEL_EXPORTER_OTLP_PROTOCOL
        value: http/protobuf
```

### 7.2 Operator가 파드에 하는 일

아래 값은 OTel Operator 소스(`internal/instrumentation/python.go`, main 브랜치)에서 확인한 것입니다.

| Operator가 파드에 하는 일                                                                                                                            | 6절의 어느 부분인가                                                                    |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **init container 추가**: 명령 `cp -r /autoinstrumentation/. /otel-auto-instrumentation-python`                                                       | 4.1절의 패키지 ①~⑤를 **설치(복사)**하는 단계. 이미지에서 `pip install`하는 것을 대신함 |
| **emptyDir 볼륨 추가** (마운트 경로 `/otel-auto-instrumentation-python`)                                                                             | 복사한 패키지를 앱 컨테이너가 볼 수 있게 하는 통로                                     |
| **`PYTHONPATH` 설정**: `fmt.Sprintf("%s:%s:%s", pythonPathPrefix, 기존값, pythonPathSuffix)`                                                         | 6.1절: 파이썬이 `sitecustomize`와 SDK를 찾게 하는 단계                                 |
| ┗ 접두: `/otel-auto-instrumentation-python/opentelemetry/instrumentation/auto_instrumentation`                                                       | `sitecustomize.py`가 있는 폴더 → 시작 시 `initialize()` 실행                           |
| ┗ 접미: `/otel-auto-instrumentation-python`                                                                                                          | SDK·Exporter·계측 패키지가 있는 폴더                                                   |
| **기본 환경변수**: `OTEL_TRACES_EXPORTER=otlp`, `OTEL_METRICS_EXPORTER=otlp`, `OTEL_LOGS_EXPORTER=otlp`, `OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf` | 4.2절: SDK가 어떤 Exporter를 붙일지 정하는 값                                          |
| **Instrumentation 값 주입**: 보낼 주소, 샘플링, 환경 이름                                                                                            | Exporter의 목적지와 TracerProvider의 sampler·resource                                  |

Operator의 Python 이미지는 OTel 패키지 묶음을 `/autoinstrumentation`(glibc용)과 `/autoinstrumentation-musl`(Alpine용)에 담은 `busybox` 이미지입니다. 묶음에 들어 있는 exporter는 `otlp_proto_http`뿐이라서, 전송 방식을 gRPC로 지정하면 `Requested component 'otlp_proto_grpc' not found` 오류로 초기화에 실패할 수 있습니다.

```
 ┌─────────── Operator 몫 (파드가 뜨기 전) ────────────┐   ┌────────── 파이썬 몫 (프로세스 안) ──────────┐
 │ 패키지 파일 복사 + PYTHONPATH + OTEL_* 환경변수     │──▶│ sitecustomize → initialize()                │
 │ = "pip install" 과 "opentelemetry-instrument" 대행  │   │   ├ SDK 조립 (Provider·Processor·Exporter)  │
 └─────────────────────────────────────────────────────┘   │   └ 계측 패키지 실행 (함수 바꿔치기)        │
                                                           └─────────────────────────────────────────────┘
```

### 7.3 파드가 뜨는 순서

```
 ① GitOps 도구가 Deployment 를 적용 (annotation: inject-python: "default")
        │
 ② 쿠버네티스가 파드를 만들려 함 → Operator webhook 이 가로채서 파드 설계도를 고침
        ├─ volumes:        emptyDir
        ├─ initContainers: Operator 의 Python 이미지
        │                  command: cp -r /autoinstrumentation/. /otel-auto-instrumentation-python
        └─ 앱 컨테이너 env: PYTHONPATH, OTEL_* (기본값 + Instrumentation 값)
        │
 ③ init container 실행 → 패키지 묶음을 공유 볼륨에 복사하고 종료
        │      /otel-auto-instrumentation-python/
        │        ├─ opentelemetry/instrumentation/auto_instrumentation/sitecustomize.py   (⑤ 자동 로더)
        │        ├─ opentelemetry/instrumentation/httpx/ … asyncpg/ … fastapi/ …          (④ 계측 패키지)
        │        ├─ opentelemetry/sdk/                                                    (③ SDK)
        │        ├─ opentelemetry/exporter/otlp/…                                         (② Exporter)
        │        └─ opentelemetry/trace/, metrics/ …                                      (① API)
        │
 ④ 앱 컨테이너 실행: Dockerfile 의 CMD 그대로 (바꾼 것 없음)
        │
        ├─ 파이썬 시작 → sys.path 에서 sitecustomize 발견 → initialize()        ← 6.1·6.2절
        │     ├─ _load_configurators(): OTEL_* 를 읽어 TracerProvider + OTLP Exporter 조립
        │     └─ _load_instrumentors(): httpx·asyncpg·fastapi 바꿔치기          ← 6.3·6.4절
        │
        └─ 앱 코드 실행 → 평소처럼 httpx·FastAPI 사용 → span 이 저절로 생김 → Collector 로 전송
```

`sitecustomize` 방식이라서 **Dockerfile의 `CMD`를 `opentelemetry-instrument …`로 바꿀 필요가 없습니다.**

**annotation이 있어도 계측되지 않는 경우:** 클러스터에 Operator가 없거나, 같은 네임스페이스에 참조한 Instrumentation(`default`)이 없으면 파드는 **에러 없이 계측 없이** 뜹니다. 조용히 빠진 채로 모를 수 있으므로, 새 클러스터·환경에 적용할 때는 Operator와 Instrumentation이 있는지 먼저 확인해야 합니다.

### 7.4 재현: OTel이 없는 앱 환경에 주입 흉내 내기

**httpx만 설치하고 OTel 패키지는 하나도 없는 venv**(앱 이미지 역할)에 Operator가 하는 일을 손으로 똑같이 했습니다.

```bash
# 앱 이미지 역할: OTel 이 전혀 없는 환경
uv venv -p 3.14 app-image && VIRTUAL_ENV=$PWD/app-image uv pip install httpx

# init container 역할: Operator 이미지의 내용물(OTel 패키지 묶음)을 공유 폴더로 복사
cp -r autoinstr-image/. otel-auto-instrumentation-python

# Operator 가 넣는 PYTHONPATH 와 환경변수 (기존 PYTHONPATH 는 비어 있음)
M=$PWD/otel-auto-instrumentation-python
export PYTHONPATH="$M/opentelemetry/instrumentation/auto_instrumentation::$M"
export OTEL_SERVICE_NAME=demo-service OTEL_TRACES_EXPORTER=console OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
export OTEL_METRICS_EXPORTER=none OTEL_LOGS_EXPORTER=none

# 평범한 python 으로 실행 (opentelemetry-instrument 없이)
app-image/bin/python demo.py
```

```
앱 venv 의 OTel 패키지 수: 0
sitecustomize 위치 = otel-auto-instrumentation-python/opentelemetry/instrumentation/auto_instrumentation/sitecustomize.py
handle_async_request = BoundFunctionWrapper     ← 바꿔치기 됨
status = 200
    "name": "GET",
    "kind": "SpanKind.CLIENT",
        "http.url": "http://127.0.0.1:8765/",
        "http.status_code": 200
            "service.name": "demo-service",
```

앱 venv에는 OTel 패키지가 0개인데도 `PYTHONPATH`가 가리키는 폴더의 `sitecustomize`가 실행되어 span이 생겼습니다. 파드에서 일어나는 일이 이것입니다.

### 7.5 이 구조에서 나오는 결과

**① 앱 이미지에는 OTel이 없어도 됩니다.** SDK, Exporter, 계측 패키지가 모두 바깥 폴더에서 옵니다. 앱 코드로 span을 직접 쓸 때도 pyproject에는 가벼운 `opentelemetry-api`만 넣으면 됩니다(7.6절).

**② Operator가 넣은 패키지가 앱 패키지보다 먼저 로드됩니다.** 재현 환경의 `sys.path` 순서입니다.

```
   otel-auto-instrumentation-python/opentelemetry/instrumentation/auto_instrumentation    ← PYTHONPATH 접두
   (현재 폴더)                                                                            ← 빈 기존 PYTHONPATH
   otel-auto-instrumentation-python                                                       ← PYTHONPATH 접미
   …/lib/python3.14 (표준 라이브러리)
   app-image/lib/python3.14/site-packages                                                 ← 앱 venv (맨 뒤)
SDK 로드 위치 = otel-auto-instrumentation-python/opentelemetry/sdk/trace/__init__.py
```

`PYTHONPATH`의 폴더는 항상 앱 venv(`site-packages`)보다 앞에 옵니다. 그래서 **같은 패키지가 양쪽에 있으면 Operator 쪽이 이깁니다.** 예를 들어 앱이 다른 라이브러리(LLM 관측 도구 등)를 통해 `opentelemetry-sdk` 1.44.0을 끌어왔어도, 파드에서는 Operator의 1.45.0이 로드됩니다. 이 경우 그 라이브러리가 더 새 SDK와 호환되는지가 확인할 지점입니다. 앱 pyproject에 `opentelemetry-api`를 넣을 때 **버전 상한을 좁게 고정하지 않는** 편이 안전한 이유도 이것입니다. 기존 `PYTHONPATH`가 비어 있으면 가운데 빈 칸이 "현재 폴더"로 해석된다는 점도 참고할 만합니다.

**③ 설정은 Instrumentation에서 오고, 코드에서 오지 않습니다.** 보낼 주소, 샘플링, 환경 이름이 모두 환경변수로 들어오므로, **보낼 곳이나 샘플링을 바꿔도 앱을 다시 빌드할 필요가 없습니다.** Instrumentation을 고치고 파드를 다시 띄우면 됩니다.

### 7.6 Operator 방식과 직접 설치 방식

| 구분          | A. Operator 방식 (권장)                           | B. 직접 설치 방식                  |
| ------------- | ------------------------------------------------- | ---------------------------------- |
| 앱 pyproject  | `opentelemetry-api`만                             | api + sdk + exporter + 계측 패키지 |
| 앱 코드       | SDK 초기화 코드 없음                              | SDK 초기화 코드 작성               |
| annotation    | **유지**                                          | **제거**                           |
| 이미지 재빌드 | 설정 변경 시 불필요                               | 계측 변경 시 필요                  |
| 전제          | 클러스터에 Operator와 Instrumentation이 있어야 함 | 없음                               |

**두 방식을 섞으면 안 됩니다.** pyproject에 SDK를 넣고 앱에서 초기화하면서 annotation도 남겨 두면 SDK가 두 번 초기화됩니다. OTel API 소스의 동작은 이렇습니다.

```python
# opentelemetry/trace/__init__.py
def set_tracer_provider(tracer_provider: TracerProvider) -> None:
    """Sets the current global :class:`~.TracerProvider` object.

    This can only be done once, a warning will be logged if any further attempt
    is made.
    """
    ...
    logger.warning("Overriding of current TracerProvider is not allowed")
```

Operator가 먼저 등록하므로, 앱에서 만든 SDK 설정은 **경고 한 줄만 남기고 무시됩니다.** 파드 안에 SDK가 두 벌 있어 어느 버전이 로드될지도 헷갈리게 됩니다.

---

## 8. 자동 계측이 닿는 곳과 닿지 않는 곳

### 8.1 라이브러리별 판정

Operator Python 이미지의 `requirements.txt`(main 브랜치)에 들어 있는 계측 패키지와 대조한 결과입니다. 묶음에는 `asyncpg`, `botocore`, `boto3sqs`, `fastapi`, `httpx`, `logging`, `sqlalchemy`, `system-metrics` 등 약 50개가 들어 있습니다.

| 라이브러리                                | 묶음에 계측 패키지가 있나 | 결과                                                                                                                                                                      |
| ----------------------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `httpx`                                   | ✅                        | 외부 API 호출 span 자동 생성                                                                                                                                              |
| `FastAPI`                                 | ✅                        | 요청 수신 span 자동 생성                                                                                                                                                  |
| `asyncpg`, `SQLAlchemy`                   | ✅                        | DB 쿼리 span 자동 생성                                                                                                                                                    |
| `aioboto3`/`aiobotocore` (비동기 AWS SDK) | ❌                        | `botocore` 계측은 `BaseClient._make_api_call`을 감싸지만, `aiobotocore`의 `AioBaseClient`는 이 메서드를 `async def _make_api_call`로 **덮어쓰기** 때문에 패치가 닿지 않음 |
| `google-genai` (LLM SDK)                  | ❌                        | 전용 span은 없고, SDK 내부의 httpx 호출 span만 생김                                                                                                                       |

### 8.2 큐(SQS) 관련 관측은 세 가지로 나뉜다

"SQS"라는 이름이 붙은 관측 대상은 서로 다른 세 가지입니다.

| 구분        | ① 큐 지표                                                  | ② SQS API 호출 span                                    | ③ 큐를 건너 trace 잇기                                                    |
| ----------- | ---------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------- |
| 누가 재나   | **AWS**가 큐 쪽에서                                        | **앱**이 호출하는 쪽에서                               | 생산자와 소비자 양쪽                                                      |
| 예시        | 가장 오래된 메시지 나이, 대기 건수, 전송·수신·삭제 수      | "`ReceiveMessage`에 20초 걸림", "`DeleteMessage` 실패" | 생산자가 보낸 메시지부터 소비자 처리까지 trace 하나로                     |
| 어디에 있나 | CloudWatch `AWS/SQS`                                       | 앱 프로세스 안                                         | 메시지 속성                                                               |
| 코드 필요?  | ❌ 불필요. **수집 경로 구축**(인프라 작업)만 필요 (10.4절) | ✅ 필요 (비동기 SDK는 자동 계측 대상 아님)             | ✅ 필요 (생산자가 `traceparent`를 메시지 속성에 싣고, 소비자가 꺼내야 함) |

여기에 하나가 더 있습니다. **④ 메시지 한 건을 처리한 전체 과정**(소비 워커의 "작업 한 번")을 묶는 span입니다. 처리 시작 지점에 span 하나를 열면, 그 안에서 자동으로 생기는 httpx·DB span이 **한 묶음으로** 보입니다. 몇 줄이면 되고 효과가 커서 코드 작업의 1순위입니다(10.2절).

```
 ④ 처리 span만 추가 (소비자 레포만 수정)
    trace A: [producer] POST … → SQS 발행             ← 따로 끊긴 trace
    trace B: [worker] job.run ─┬─ SELECT …            ← 처리 과정은 한 묶음으로 보임
                               ├─ POST /process → [api-server] …
                               └─ POST external-api

 ③ 큐를 건너 잇기 (생산자 레포도 수정)
    trace A: [producer] POST … → SQS 발행 ─ ─ ─ ▶ [worker] job.run ─┬─ …
                                   (메시지 속성의 traceparent 로 연결)
```

권장 순서는 ①(인프라) → ④(몇 줄) → 필요할 때 ②·③입니다. 큐 대기 지연의 **전체 추세**는 ①의 Age 지표로 이미 볼 수 있으므로, ③은 요청 단위로 봐야 할 때 검토합니다. SQS 지표 각각의 의미와 해석은 [[sqs-cloudwatch-metrics-guide]]에서 다룹니다.

### 8.3 LLM 호출 관측과 LLM 관측 도구의 역할 분담

| 보고 싶은 것                             | 코드 필요?                       | 이유                                                                   |
| ---------------------------------------- | -------------------------------- | ---------------------------------------------------------------------- |
| LLM 호출 한 번의 지연, 상태 코드, 실패율 | ❌                               | LLM SDK가 내부에서 httpx로 호출하면 httpx 자동 계측이 HTTP span을 만듦 |
| 그 호출이 파이프라인의 어느 단계였나     | ✅ (조금)                        | HTTP span에는 URL만 있음. 단계마다 span을 열거나 속성을 달아야 함      |
| 모델 이름, 토큰 사용량                   | ✅ 또는 **LLM 관측 도구로 대신** | Langfuse 같은 LLM 관측 도구가 이미 기록하고 있다면 그쪽에서 봄         |

| 도구                            | 맡는 질문                                      | 예시                                                       |
| ------------------------------- | ---------------------------------------------- | ---------------------------------------------------------- |
| **LLM 관측 도구 (Langfuse 등)** | LLM 품질: 프롬프트, 응답, 토큰, 버전별 비교    | "프롬프트를 바꾼 뒤 결과가 달라졌나?"                      |
| **SigNoz**                      | 운영: 지연, 실패율, 포화, 다른 서비스와의 연결 | "API 서버가 느린 게 LLM 때문인가, 스레드풀 포화 때문인가?" |

OTel에는 LLM SDK 전용 계측 패키지가 따로 있을 수 있지만 Operator 묶음에는 들어 있지 않습니다. 쓴다면 **프롬프트 원문을 span에 싣지 않도록 막을 수 있는지** 먼저 확인해야 합니다(확인 필요).

### 8.4 직접 span·metric을 쓸 때

자동 계측이 TracerProvider와 MeterProvider를 이미 만들어 두므로, 앱 코드는 **API만 불러서** 씁니다. 소비 워커의 작업 처리를 예로 든 코드입니다.

```python
import time
from datetime import UTC, datetime

from opentelemetry import metrics, trace

tracer = trace.get_tracer("myapp.worker")
meter = metrics.get_meter("myapp.worker")

# Counter: 결과별 건수 — 속성 값은 몇 개로 닫혀 있어야 한다 (cardinality)
job_outcomes = meter.create_counter("job.outcomes", unit="{job}", description="작업 결과별 건수")
# Histogram: 소요 시간 분포
job_duration = meter.create_histogram("job.duration", unit="s", description="작업 한 번의 소요 시간")

running: set = set()
# Observable Gauge: 내보낼 때마다 콜백이 현재 값을 읽어 간다
meter.create_observable_gauge(
    "job.in_flight",
    callbacks=[lambda _options: [metrics.Observation(len(running))]],
    description="동시 실행 중인 작업 수",
)


async def run_one(target_id: int, handler) -> None:
    # 루트 span 하나 — 안에서 일어나는 httpx·asyncpg span 이 전부 이 아래 자식으로 붙는다
    with tracer.start_as_current_span("job.run") as span:
        span.set_attribute("target.id", target_id)   # span 에는 고유값을 달아도 된다
        start = time.perf_counter()
        result = "ok"
        try:
            await handler(target_id, datetime.now(UTC))
        except TimeoutError:
            result = "budget_exceeded"
            raise
        except Exception:
            result = "failed"
            raise
        finally:
            # metric 에는 닫힌 값 집합만 — target_id 는 싣지 않는다
            job_outcomes.add(1, {"result": result})
            job_duration.record(time.perf_counter() - start, {"result": result})
```

**나중에 span을 추가하면 정보가 덧붙습니다.** 새 span은 같은 trace 안에서 부모가 되고, 자동으로 생기던 span이 그 아래 자식으로 붙습니다. 이미 만든 대시보드를 다시 만들 필요는 없습니다.

```
 자동 계측만                            처리 span 추가 후
 trace A: SELECT …                      trace: job.run (9.2s)    ← 새로 생김
 trace B: POST /process → api-server …    ├─ SELECT …            (0.1s)
 trace C: POST external-api               ├─ POST /process → api-server … (8.5s)
 trace D: INSERT …                        ├─ POST external-api   (0.3s)
 (따로따로 흩어짐)                        └─ INSERT …            (0.1s)
```

---

## 9. 같은 프로세스의 다른 OTel 사용자와 충돌: LLM 관측 도구 사례

Langfuse처럼 **OTel 위에서 만든 라이브러리**는 프로세스의 전역 TracerProvider를 함께 씁니다. Langfuse 4.15.1 소스(`langfuse/_client/resource_manager.py`)의 동작은 이렇습니다.

```python
default_provider = cast(TracerProvider, otel_trace_api.get_tracer_provider())
if isinstance(default_provider, otel_trace_api.ProxyTracerProvider):
    provider = TracerProvider(...)          # 전역 provider 가 없을 때만 자기 것을 만든다
    otel_trace_api.set_tracer_provider(provider)
else:
    ...                                     # 이미 있으면 그걸 재사용한다
```

이 때문에 두 가지 상황이 생깁니다.

**① 자동 계측을 켠 경우:** 자동 계측이 `sitecustomize`에서 전역 provider를 먼저 등록하므로, Langfuse는 **같은 provider에 자기 processor를 붙입니다.** 그러면 Langfuse span이 두 곳으로 나갑니다.

```
 앱 span ─┬─▶ Langfuse processor (Langfuse span만 골라서) ─▶ Langfuse
          └─▶ Operator OTLP exporter (전부)               ─▶ SigNoz   ← Langfuse span 포함
```

Langfuse span에는 `langfuse.observation.input`·`langfuse.observation.output` 속성이 붙습니다. 루트 span이라면 API 요청 원본 전체가, LLM 호출 span이라면 모델에 보낸 프롬프트와 모델 응답이 들어갑니다. 이 값은 **SigNoz의 로그가 아니라 trace 화면**에서 span을 눌렀을 때 나오는 속성 목록에 보이고, ClickHouse의 trace 테이블에 저장됩니다. 대화 전체가 문자열 하나로 들어가면 span 하나가 커져 저장 용량에도 영향을 줍니다.

**② 자동 계측 없이 앱 코드에 span을 넣은 경우:** Langfuse가 자기 provider를 만들어 전역으로 등록합니다. 이 provider의 기본 필터(`should_export_span`)는 Langfuse span, `gen_ai.*` 속성을 가진 span, 알려진 LLM 계측 span만 내보냅니다. 따라서 **앱이 만든 span은 기록은 되지만 어디로도 가지 않습니다.**

어느 쪽이든 정리하려면 provider를 분리하거나(Langfuse에 전용 provider를 넘김), 수집기에서 해당 속성을 지우는 작업이 필요합니다.

---

## 10. SigNoz에서 보이는 것과 만들어야 하는 것

**절반은 자동이고, 절반은 직접 만들어야 합니다.** span으로 얻는 RED는 SigNoz의 **내장 Services 화면**이 자동으로 보여 주고, 클라우드 지표와 업무 지표는 **대시보드를 직접 구성**해야 합니다.

```
 ┌─ 경로 A: 자동 계측 span (코드 불필요) ───────────────────────────────────────────┐
 │  앱 ──httpx/FastAPI/asyncpg 패치──▶ span ──OTLP──▶ SigNoz ──▶ Services 화면 RED  │
 └──────────────────────────────────────────────────────────────────────────────────┘
 ┌─ 경로 B: 코드로 적는 span·metric (코드 필요) ────────────────────────────────────┐
 │  앱 ──tracer/meter API──▶ 작업 span, 업무 Counter, in_flight Gauge ──▶ SigNoz    │
 └──────────────────────────────────────────────────────────────────────────────────┘
 ┌─ 경로 C: 클라우드 지표 (앱 코드와 무관, 인프라 설정 필요) ───────────────────────┐
 │  SQS·RDS ──(AWS가 직접 측정)──▶ CloudWatch ──?──▶ SigNoz                         │
 │                                              └ 이 화살표를 따로 놓아야 함        │
 └──────────────────────────────────────────────────────────────────────────────────┘
```

"SigNoz가 span에서 metric을 만든다"는 말은 **경로 A와 B에만** 해당합니다.

### 10.1 자동으로 생기는 Services(APM) 화면

SigNoz 문서에 따르면 `service.name`이 붙은 span이 들어오면 그 서비스가 Services 목록에 자동으로 올라갑니다. RED는 서비스의 **진입점 span(sub-root span)**으로 계산합니다(요청량 = 초당 sub-root span 수, 에러율 = error 상태 sub-root span 비율, 지연 = sub-root span 소요 시간의 분위수).

| 화면                             | 보이는 것                                      |
| -------------------------------- | ---------------------------------------------- |
| **Services 목록**                | 서비스별 P99 지연, 에러율, 초당 요청 수, Apdex |
| **서비스 상세 > Key Operations** | 그 서비스가 받는 API·작업별 RED                |
| **External Calls**               | 그 서비스가 밖으로 부른 호출의 RED             |
| **Database Calls**               | DB 쿼리의 RED                                  |

샘플링 비율을 낮추면 span에서 계산한 RED 수치가 영향을 받는지는 SigNoz 문서에 적혀 있지 않습니다(확인 필요).

### 10.2 워커 서비스의 함정: 진입점 span

HTTP 서버는 요청을 받는 SERVER span이 진입점이라 문제가 없습니다. 하지만 **큐를 돌리는 워커**는 진입점이 없어서, 자동 계측만 켜면 DB 쿼리와 httpx 호출 span이 각각 루트로 흩어집니다.

```
 처리 span 없음                          처리 span 있음 (몇 줄 추가)
 worker Key Operations:                  worker Key Operations:
   POST  (httpx)                           job.run        ← 작업 한 번의 RED
   SELECT (asyncpg)                        ingest.handle
   INSERT (asyncpg)                      External Calls: api-server, external-api
   … 뒤섞여 나옴 (확인 필요)             Database Calls: SELECT, INSERT …
```

### 10.3 Breakdown(구간별 시간 분석)

New Relic의 트랜잭션 Breakdown은 "이 API가 평균 9초 걸렸는데 DB 0.5초, 외부 호출 7초, 나머지 1.5초"처럼 **구간 종류별 시간을 집계한 표**입니다.

| 보고 싶은 것                                  | SigNoz에서                                                                                                                 | 자동 계측만으로                                                         |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| **요청 한 건**의 구간별 시간                  | trace 상세 화면에서 span이 시간축으로 펼쳐짐                                                                               | ✅ HTTP 서버는 바로 됨. 워커는 처리 span이 없으면 한 화면에 묶이지 않음 |
| **여러 요청을 집계한** 구간별 시간            | 문서상 **기본 화면은 없음.** trace 쿼리 빌더(필터·집계·Group By)로 span을 호출 대상·DB 여부로 묶어 패널을 직접 만들어야 함 | ⚠️ 패널 구성 필요                                                        |
| 실패 요청의 분해 (응답 코드·작업·호출 대상별) | Services 화면과 trace 쿼리 빌더                                                                                            | ✅                                                                      |

### 10.4 클라우드 지표(CloudWatch)는 별도 수집 경로

SQS·RDS 같은 관리형 서비스의 지표는 span과 무관하게 **AWS CloudWatch**에 있습니다. span을 아무리 잘 적어도 생기지 않습니다. "큐에 대기 중인 메시지가 몇 건인가"는 앱이 알 수 없는 값이기 때문입니다.

- SigNoz의 **One-Click AWS Integration**은 문서상 "This feature is available for SigNoz Cloud users."로, **Cloud 전용**입니다. 자체 호스팅에서는 쓸 수 없습니다(이 기능은 내부적으로 CloudFormation, CloudWatch Metric Streams, Kinesis Firehose를 씁니다).
- 자체 호스팅에서는 경로를 직접 놓아야 합니다.

| 방법                           | 흐름                                                                                | 비고                                                                                                                            |
| ------------------------------ | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Metric Streams (밀어 주기)** | CloudWatch Metric Stream → Kinesis Data Firehose → Collector의 HTTP 수신 엔드포인트 | AWS 문서상 Metric Streams는 **OpenTelemetry 1.0.0** 형식을 지원. Collector가 Firehose 형식을 받는 receiver를 갖췄는지 확인 필요 |
| **폴링 exporter (가져오기)**   | exporter가 CloudWatch API를 주기적으로 조회 → Prometheus 형식 → Collector가 긁어 감 | YACE 같은 도구가 흔히 쓰임 (확인 필요)                                                                                          |

공개 대시보드 템플릿에도 한계가 있습니다. SigNoz 대시보드 레포의 `aws-sqs-prometheus` 템플릿은 `jmal98/sqs-exporter`로 큐 속성을 직접 조회한 값을 쓰며, 지표가 `sqs_approximatenumberofmessages`(Visible), `…delayed`, `…notvisible` **3개뿐**입니다. 가장 중요한 `ApproximateAgeOfOldestMessage`와 전송·수신·삭제 수가 없습니다.

### 10.5 대시보드 직접 구성과 JSON 보관

대시보드는 **이미 SigNoz에 들어와 있는 지표**로만 그릴 수 있습니다. 지표 이름도 수집 경로에 따라 달라지므로 순서가 정해져 있습니다.

```
 ① 수집 경로 결정·구축
      ▼
 ② SigNoz에서 들어온 지표 이름 확인
      ▼
 ③ 대시보드 패널 구성 (Dashboards → New → Add Panel → Query Builder)
      ▼
 ④ 알람 규칙 구성 (대시보드와 별도)
```

UI에서 만든 대시보드는 **JSON으로 내보내고 가져올 수 있습니다.** 실수로 지우거나 고쳐도 되돌릴 수 있도록 JSON을 git에 보관하고, SigNoz API(`POST /api/v1/dashboards`)로 다시 올리는 스크립트를 쓰는 것이 일반적입니다. 내장 Services 화면은 JSON 대상이 아니고, **직접 구성한 대시보드**가 대상입니다.

---

## 11. 알람과 권한

### 11.1 알림 채널과 알람 규칙

SigNoz에서 알림은 **"어디로 보낼지"(채널)**와 **"언제 보낼지"(규칙)**가 분리되어 있습니다. 둘 다 UI에서 관리할 수 있고, 자체 호스팅에서도 같습니다(Slack 채널은 v0.5.0 이상).

```
 ┌─ Notification Channel (어디로) ──┐        ┌─ Alert Rule (언제) ────────┐
 │  이름: myservice-prd             │ ◀───── │ "큐 Age > 700초"           │
 │  종류: Slack                     │  선택  │ "API 503 1건 이상"         │
 │  Webhook: https://hooks.slack…   │ ◀───── │ "error 로그 5분 3건 이상"  │
 └──────────────────────────────────┘        └────────────────────────────┘
        한 채널을 여러 규칙이 함께 씀        규칙이 울리면 → 선택한 채널의 Slack 으로 게시
```

| 대상          | UI 위치 (문서 기준)                                                      | 가능한 작업                                                                                         |
| ------------- | ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| **알림 채널** | `Alerts > Notification Channels` 또는 `Settings > Notification Channels` | 만들기, 고치기. **채널 이름과 종류는 만든 뒤 바꿀 수 없음.** 삭제는 문서에 명시되지 않음(확인 필요) |
| **알람 규칙** | `Alerts` 화면                                                            | 만들기, 고치기, 일시 정지(silence), 삭제                                                            |

Slack 쪽에서는 **Incoming Webhook URL**(`https://hooks.slack.com/services/…`)이 필요합니다. 문서에 따르면 **Slack 앱에서 만든 webhook**이어야 하고 Workflow Builder로 만든 것은 쓸 수 없습니다. Webhook 하나는 Slack 채널 하나에 묶이므로, 환경별로 다른 채널로 받으려면 webhook도 그만큼 필요합니다.

### 11.2 알람 규칙의 종류

| 종류       | 문서 설명 요지                   | 용도 예시                             |
| ---------- | -------------------------------- | ------------------------------------- |
| Metrics    | 지표 쿼리가 임계값을 넘을 때     | 큐 Age, 파드 CPU·메모리·재시작        |
| Logs       | 로그 패턴, 건수, 속성 조건       | 특정 접두어 로그, error·critical 로그 |
| Traces     | span 조건 (P99 지연, 에러 건수)  | API 에러·지연, 503                    |
| Exceptions | 새로 나타나거나 반복되는 예외    |                                       |
| Anomaly    | 지표가 과거 기준선에서 벗어날 때 |                                       |

### 11.3 UI 관리와 코드 관리

문서에 따르면 알람 규칙은 **Terraform**이나 **SigNoz Operator의 쿠버네티스 리소스**로도 선언할 수 있습니다. 운영 팀이 코드로 관리한다면 **UI에서 직접 고친 내용이 다음 배포 때 덮어써질 수 있습니다.** 그래서 알람을 요청할 때 다음을 함께 확인합니다.

- 알람 규칙과 채널을 UI로 관리하는지, 코드로 관리하는지
- 기준값을 조정할 때 UI에서 직접 고쳐도 되는지, 요청 절차가 있는지

### 11.4 역할과 수정 권한

SigNoz 문서(Roles)의 기본 역할입니다.

| 역할              | 문서 설명                                                                                              | 알람·대시보드                |
| ----------------- | ------------------------------------------------------------------------------------------------------ | ---------------------------- |
| **SigNoz-Admin**  | 모든 리소스에 대한 전체 관리 권한                                                                      | 모두 가능 + 사용자·역할 관리 |
| **SigNoz-Editor** | 대시보드, 알람, 파이프라인 같은 관측 리소스를 만들고 고칠 수 있음. 사용자·역할·서비스 계정은 관리 불가 | ✅ 만들기·고치기             |
| **SigNoz-Viewer** | 관측 데이터와 리소스를 읽기만 함                                                                       | ❌ 보기만                    |
| SigNoz-Anonymous  | 공개 공유된 대시보드만. 자동 부여                                                                      | 해당 없음                    |

- **Editor는 조직 전체에 적용될 수 있습니다.** "우리 팀 알람만" 같은 범위 구분이 가능한 **사용자 정의 역할**은 문서상 SigNoz Cloud와 자체 호스팅 **Enterprise** 판에서만 제공되며, 이 기능도 beta입니다. Community 판이라면 Editor를 받으면 다른 팀의 대시보드와 알람도 고칠 수 있게 됩니다.
- 알림 채널 관리 권한이 Editor에 포함되는지는 문서에 명시되어 있지 않습니다(확인 필요).

---

## 12. 운영 설계 원칙

### 12.1 P50·P90·P99를 함께 보는 이유

```
 요청 100건을 빠른 순으로 정렬
 ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▂▂▂▂▂▂▂▃▃▃▅▅▇█
 └──────── 50번째 ────────┘            │    │
          P50 (중앙값)                P90  P99
   "보통 요청은 이 정도"           "10건에 1건" "100건에 1건 (꼬리)"
```

| 지표    | 답하는 질문                  | 움직일 때의 뜻                                                                                                      |
| ------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **P50** | 보통의 요청은 얼마나 걸리나  | P50이 오르면 **전체가 느려진 것**. 배포 후 성능 저하나 하위 서비스 전반의 지연                                      |
| **P90** | 대부분의 요청이 겪는 상한은  | SLO를 "90%의 요청은 X초 안에"로 잡을 때의 기준                                                                      |
| **P99** | 운 나쁜 요청은 얼마나 걸리나 | P50은 그대로인데 P99만 오르면 **일부 요청만** 느린 것. 재시도, 특정 입력, 한 하위 서비스의 간헐적 지연, 대기열 포화 |

평균을 쓰지 않는 이유는 평균이 꼬리를 숨기기 때문입니다. 99건이 1초, 1건이 60초면 평균은 약 1.6초라 괜찮아 보이지만, 그 1건을 겪은 사용자는 1분을 기다렸습니다.

**꼬리가 증폭되는 현상:** 작업 하나가 LLM을 3번 부르고, LLM 호출 한 번이 P99 수준으로 느릴 확률이 1%라면, **셋 중 하나라도 느릴 확률은 약 3%**(1 − 0.99³)입니다. 하위 호출의 P99가 상위 작업에서는 P97 수준으로 올라옵니다. Dean과 Barroso가 "The Tail at Scale"(2013)에서 정리한 현상이며, 하위 호출일수록 P99를 봐야 상위 작업의 지연을 설명할 수 있습니다. 그래서 모든 대상에 P50·P90·P99를 같은 기준으로 둡니다.

### 12.2 Apdex가 맞지 않는 서비스

```
 기준 시간 T (예: 0.5초)
   만족(Satisfied)      : 응답 ≤ T
   참을 만함(Tolerating): T < 응답 ≤ 4T
   불만(Frustrated)     : 응답 > 4T 또는 실패

 Apdex = (만족 건수 + 참을 만함 건수 ÷ 2) ÷ 전체 건수
```

Apdex는 **사람이 화면 앞에서 응답을 기다리는 요청**을 전제로 합니다. 다음과 같은 서비스에는 맞지 않습니다.

| 이유                      | 설명                                                                                                                      |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| 기다리는 사람이 없음      | 배치형·큐 기반 처리는 3초가 9초로 늘어도 그 순간 화면 앞에서 기다리는 사람이 없음                                         |
| 정상 응답이 수 초~수십 초 | LLM을 여러 번 부르면 기본 T(0.5초)로는 모든 요청이 "불만"이 되어 점수가 늘 0 근처. 움직이지 않는 점수는 신호로 쓸 수 없음 |
| 하나의 점수로 뭉개짐      | 느려진 것인지 실패가 늘어난 것인지 구분할 수 없음                                                                         |

이런 서비스는 Apdex를 빼고 **작업별 P50·P90·P99와 에러율**로 판단합니다.

### 12.3 샘플링

**샘플링의 핵심 이유는 비용이고, 앱 속도와는 거의 관계없습니다.**

| 이유           | 설명                                                                                                                                             |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| 저장·처리 비용 | span 수는 요청 수에 비례. 전부 저장하면 ClickHouse 용량과 Collector 처리량이 크게 늘어남                                                         |
| 네트워크       | 전송 트래픽이 줄어듦                                                                                                                             |
| 앱 속도        | 영향이 작음. span 생성은 가볍고 전송은 백그라운드 스레드가 함. 샘플링에서 빠진 요청은 "기록하지 않는 span"이 되어 그 작은 비용마저 줄어드는 정도 |

**요청이 적은 서비스는 전량(100%) 수집이 낫습니다.** 샘플링을 낮추면 드문 실패가 통째로 빠지거나, span으로 계산하는 요청량·에러율이 실제와 달라질 수 있습니다. 계측 설정의 `parentbased_traceidratio` sampler에서 `argument: "1.0"`이 전량 수집입니다.

### 12.4 cardinality

metric에 속성을 붙이면 **속성 값 조합 하나하나가 별도의 시계열**이 됩니다.

| 속성                                 | 값의 종류    | 판정                                   |
| ------------------------------------ | ------------ | -------------------------------------- |
| `result` (ok·failed·timeout·skipped) | 4개          | ✅ 좋음                                |
| `http.response.status_code`          | 수십 개      | ✅ 괜찮음                              |
| 채널·고객 ID                         | 수백 개 이상 | ⚠️ 시계열 폭발. span 속성이나 로그에 둠 |
| 요청 ID, 메시지 ID                   | 무한         | ❌ 절대 금지                           |

"고객별로 보고 싶다"는 요구는 metric이 아니라 **span 속성이나 로그**로 풉니다.

### 12.5 알람 임계값과 판정 창

**임계값의 원칙:** "설계상 정상적으로 도달할 수 있는 최대값"보다 커지면 알립니다. 숫자를 감으로 정하지 않고 코드와 설정에 이미 있는 시간값에서 끌어냅니다. 예를 들면 다음과 같습니다.

- 호출하는 쪽의 타임아웃이 60초면, P99 지연 알람은 그보다 조금 낮은 값(예: 45초)으로 둡니다. 그 값을 넘으면 타임아웃이 곧 시작됩니다.
- 하위 호출 마감이 100초면, P99 알람은 그 75% 수준(예: 75초)으로 둡니다.
- 큐 대기 시간은 재시도 설계(가시성 시간 × 재시도 횟수 + 처리 마감)에서 정상 최대를 계산합니다. 상세한 계산법은 [[sqs-cloudwatch-metrics-guide]]에서 다룹니다.

**구조적으로 0이어야 하는 지표는 1건 즉시 알람이 맞습니다.** 예를 들어 "호출 쪽 동시 요청 최대치 ≤ 서버 처리 한도"로 맞춰 둔 구성에서 서버 포화 응답(503)은 평소에 나올 수 없습니다. 이런 값은 "평소 0%"의 임계를 몇 %로 둘지 근거가 없으므로, 비율 대신 건수로 겁니다.

**판정 창은 알람마다 성격에 맞춥니다.** 처음에는 촘촘하게 두고 운영하면서 푸는 방향을 권합니다.

| 유형                           | 기준                           | 예                                                                                                                       |
| ------------------------------ | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| 구조적으로 0이어야 하는 것     | 1건 즉시                       | 서버 포화 응답, 사람이 봐야 한다고 코드가 표시한 로그, critical 로그, OOMKilled, 재시작, Ready 파드 0, 큐 대기 임계 초과 |
| 실패가 이어지면 기능이 멈춘 것 | 짧은 창의 건수 (예: 5분에 3건) | API 실패, error 로그                                                                                                     |
| 짧은 튐이 정상인 것            | 짧은 연속 조건                 | CPU (예: 3분 연속), P99 지연 (예: 5분)                                                                                   |

몇 가지 근거를 덧붙입니다.

- **트래픽이 적으면 비율 대신 건수를 씁니다.** 5분에 요청 3건 중 1건만 실패해도 33%가 됩니다.
- **메모리는 즉시, CPU는 연속 조건입니다.** 메모리 limit을 넘으면 커널이 프로세스를 강제 종료(OOMKilled)하고, 파이썬 프로세스는 늘어난 메모리를 잘 돌려주지 않아 90%에 닿으면 곧 종료될 가능성이 큽니다. 반면 CPU limit을 넘으면 종료되지 않고 **느려지며(throttling)**, 파싱 같은 작업으로 잠깐 튀는 일이 정상적으로 자주 생깁니다.
- **readiness probe가 없는 워커의 Ready 파드 수는 "컨테이너가 떠 있다"는 뜻입니다.** probe가 없으면 쿠버네티스는 성공으로 간주하므로, 크래시 반복이나 이미지 실패는 잡지만 **프로세스가 멈춘(hang) 경우는 잡지 못합니다.** 이 경우는 큐 대기 시간 알람이 대신 잡습니다.
- **재시도되는 실패도 error로 남는 코드라면,** error 로그 알람을 촘촘하게 잡으면 시작하고 얼마 동안 자주 울릴 수 있습니다. 그것이 "기능이 계속 실패 중"이라는 신호이므로 의도된 결과입니다.

---

## 13. 역할 분담: 개발 팀과 플랫폼 팀

span이 SigNoz에 닿기까지 필요한 것을 층별로 나누면 다음과 같습니다.

```
 ④ SigNoz 백엔드·Collector (관측 클러스터)                       ← 플랫폼 팀
        ▲ OTLP/HTTP
 ③ 네트워크 경로 (앱 클러스터 → 관측 클러스터)                   ← 플랫폼 팀
        ▲
 ② Operator 설치 + Instrumentation (클러스터·네임스페이스당 1회) ← 플랫폼 팀
        ▲
 ①' Deployment annotation·환경변수 (서비스마다)                  ← 배포 매니페스트 소유 팀
        ▲
 ① 코드: 직접 span·metric 기록                                   ← 개발 팀
```

| 층                         | 작업                                                                                                     | 담당                                |
| -------------------------- | -------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| ① 코드                     | 처리 span, 업무 metric, `opentelemetry-api` 의존성, 같은 프로세스의 다른 OTel 사용자와 provider 정리     | 개발 팀                             |
| ①' 서비스 설정             | annotation, `OTEL_SERVICE_NAME`, 헬스체크 경로 제외(`OTEL_PYTHON_EXCLUDED_URLS`, HTTP probe일 때만 필요) | 매니페스트 소유 팀                  |
| ② Operator·Instrumentation | cluster-admin 권한 필요                                                                                  | 플랫폼 팀                           |
| ③ 네트워크                 | 클러스터 간 도달성                                                                                       | 플랫폼 팀                           |
| ④ 백엔드 정책              | 샘플링, 보존 기간, 비용, 속성 가공, 클라우드 지표 수집 경로, 대시보드 JSON 보관 위치                     | 플랫폼 팀 (개발 팀은 요구사항 제시) |

**요청서는 "필요한 것"만 담백하게 씁니다.** 어떤 템플릿이 부족한지, 어느 경로로 수집할지 같은 구현 방법은 플랫폼 팀이 정할 일입니다. 개발 팀이 요청서에 담을 것은 대상 서비스, 보고 싶은 지표와 임계값, 알람 조건, 그리고 확인이 필요한 것(알림 채널 이름 규칙, 알람 수정 권한과 관리 방식)입니다.

**개발 팀이 먼저 할 수 있는 것:**

1. **코드부터 넣기:** API는 no-op이 보장되므로 계측이 준비되기 전에 병합해도 동작이 바뀌지 않습니다.
2. **로컬에서 검증하기:** 앱을 `opentelemetry-instrument`로 띄우고 `OTEL_TRACES_EXPORTER=console`로 두면 span 모양을 터미널에서 확인할 수 있습니다.
3. **개발 환경에서 먼저 켜기:** 화면과 trace 모양을 확인한 뒤 운영 환경에 요청합니다.

---

## 14. 주의점

- **API만으로는 아무것도 가지 않습니다.** SDK와 Exporter가 등록되어야 전송됩니다(4.3절).
- **annotation이 있어도 Operator나 Instrumentation이 없으면 조용히 계측이 빠집니다**(7.3절).
- **SDK를 두 번 초기화하지 않습니다.** Operator 방식과 직접 설치 방식 중 하나만 씁니다(7.6절).
- **Operator 패키지가 앱 패키지보다 먼저 로드됩니다.** 같은 OTel 패키지를 앱도 가지고 있다면 버전 호환을 확인합니다(7.5절).
- **같은 프로세스의 다른 OTel 사용자를 확인합니다.** LLM 관측 도구 같은 라이브러리가 전역 provider를 공유해, 원문이 담긴 속성이 SigNoz로 가거나 앱 span이 어디로도 가지 않을 수 있습니다(9절).
- **로그 수집은 stdout·stderr 전체를 가져갑니다.** 감사 기록처럼 일반 로그와 분리해야 하는 기록을 같은 stderr로 쓰고 있다면 함께 수집됩니다. 로그 줄에 `type` 같은 구분 필드가 있으면 수집 단계에서 걸러내거나 따로 보낼 수 있습니다.
- **DB 쿼리 파라미터:** asyncpg 계측은 기본값에서 바인딩 값을 남기지 않지만(`capture_parameters=False`), 다른 계측이나 설정에서도 그런지 확인합니다.
- **비동기 AWS SDK와 LLM SDK는 자동 계측 대상이 아닙니다**(8.1절).
- **워커 서비스는 처리 span이 있어야 Services 화면이 제대로 나옵니다**(10.2절).
- **클라우드 지표는 별도 수집 경로가 필요하고, 공개 템플릿은 지표가 부족할 수 있습니다**(10.4절).
- **UI에서 고친 알람이 코드 관리로 덮어써질 수 있습니다**(11.3절).
- **metric 속성에 고유 ID를 넣지 않습니다**(12.4절).

---

## 15. 정리

| 질문                             | 답                                                                                              |
| -------------------------------- | ----------------------------------------------------------------------------------------------- |
| span과 metric의 차이는?          | span은 사건 하나의 기록(원인 추적), metric은 기간별 집계(추세·알람) (3절)                       |
| SDK는 어디서 도나?               | **앱 프로세스 안.** Provider ⊃ Processor ⊃ Exporter 구조 (4.2절)                                |
| OTLP Exporter는 Provider인가?    | 아님. Provider 아래 Processor에 들어가는 전송 부품 하나 (4.2절)                                 |
| Datadog Agent에 해당하는 것은?   | **OTel Collector.** SDK는 `ddtrace`에 해당 (5.2절)                                              |
| 자동 계측은 어떻게 동작하나?     | `sitecustomize` → `initialize()` → entry point로 계측 패키지 찾기 → wrapt로 함수 바꿔치기 (6절) |
| Operator는 무엇을 하나?          | 패키지 파일 복사(init container) + `PYTHONPATH`·`OTEL_*` 설정. 나머지는 파이썬이 함 (7절)       |
| 코드로 span을 쓰려면?            | pyproject에 `opentelemetry-api`만 넣고 annotation 유지 (7.6·8.4절)                              |
| 자동으로 안 되는 것은?           | 비동기 AWS SDK, LLM 의미 정보, 큐 건너 trace, 업무 지표, 워커 처리 단위 (8절)                   |
| SigNoz에서 자동으로 보이는 것은? | Services 화면의 RED, External Calls, Database Calls (10.1절)                                    |
| 직접 만들어야 하는 것은?         | 클라우드 지표 수집 경로, 커스텀 대시보드, Breakdown 패널, 알람 규칙 (10·11절)                   |
| 알람은 UI로 관리하나?            | 가능. 채널과 규칙이 분리되고, 코드 관리도 가능하며, 수정에는 Editor 이상 필요 (11절)            |

**기억할 세 가지:**

1. **Operator는 준비만 하고, 계측은 파이썬 프로세스 안에서 일어납니다.** 그래서 앱 코드와 이미지를 바꾸지 않고 켜고 끌 수 있습니다.
2. **자동 계측은 "알려진 라이브러리의 함수 바꿔치기"입니다.** 그 목록 밖(비동기 SDK, 큐 경계, 업무 단위)은 코드나 인프라 작업으로 채웁니다.
3. **SigNoz가 span에서 만드는 RED와, 클라우드가 재는 지표는 서로 다른 경로입니다.** 앞의 것은 계측으로, 뒤의 것은 수집 경로로 해결합니다.

---

## Sources

- [OpenTelemetry Metrics 개념](https://opentelemetry.io/docs/concepts/signals/metrics/)
- [OpenTelemetry Operator: Python 주입 코드 (`internal/instrumentation/python.go`)](https://github.com/open-telemetry/opentelemetry-operator/blob/main/internal/instrumentation/python.go)
- [OpenTelemetry Operator: Python 자동 계측 이미지 (`autoinstrumentation/python`)](https://github.com/open-telemetry/opentelemetry-operator/tree/main/autoinstrumentation/python)
- [SigNoz: Services(APM) 지표](https://signoz.io/docs/userguide/metrics/)
- [SigNoz: Trace Explorer](https://signoz.io/docs/product-features/trace-explorer/)
- [SigNoz: Slack 알림 채널](https://signoz.io/docs/alerts-management/notification-channel/slack/)
- [SigNoz: Alerts](https://signoz.io/docs/alerts/)
- [SigNoz: One-Click AWS Integrations](https://signoz.io/docs/integrations/aws/one-click-aws-integrations/)
- [SigNoz: Roles](https://signoz.io/docs/manage/administrator-guide/iam/roles/)
- [SigNoz Dashboards 레포 (`aws-sqs-prometheus`)](https://github.com/SigNoz/dashboards/tree/main/aws-sqs-prometheus)
- [Amazon CloudWatch Metric Streams](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-metric-streams-formats.html)
- Jeffrey Dean, Luiz André Barroso, "The Tail at Scale", Communications of the ACM, 2013
