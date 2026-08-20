---
tags: [distributed-tracing, correlation-id, datadog, apm, logging]
created: 2026-08-20
---

# dd.trace_id vs correlation_id

## 1. 겹치는 부분은 진짜다 — 인정하고 시작

`dd.trace_id`가 end-to-end로 잘 전파(propagation)되고 있다면, "이 실행 하나를 추적한다"는 목적에서는 `correlation_id`와 하는 일이 **사실상 같다.** 오히려 `dd.trace_id` 쪽이 로그 줄만 이어주는 `correlation_id`보다 상위호환이다 — 각 구간의 소요 시간, 실패 지점까지 타이밍 그래프(waterfall)로 보여주니까. 그러니 "한 번의 실행을 추적"하는 목적만 놓고 보면, `correlation_id`를 따로 만드는 건 **중복 투자**가 맞다.

## 2. 그런데 겹치지 않는 지점이 셋 있다 — 트레이스의 구조적 한계

```
trace(dd.trace_id) 의 생명주기 :  하나의 실행이 "지금 이 순간" 시작해서 앞으로 전파되는 것만 묶는다
                                   (과거로 거슬러 올라가지 못하고, 전파가 끊기면 거기서 트레이스도 끊긴다)

     이번 스캔 tick ──▶ [cycle_loop 실행] ──▶ dd.trace_id = A  (여기서 새로 시작)
                              │
                              ▼ 실패, 메시지 삭제
                        다음 tick 기다림
                              │
                              ▼
     다음 스캔 tick ──▶ [cycle_loop 실행] ──▶ dd.trace_id = B  (또 새로 시작, A 와 인과관계 없음)

     → A 와 B 를 "같은 채널의 같은 문제"로 묶어주는 트레이스는 존재하지 않는다
     → 이걸 묶는 건 트레이싱의 일이 아니라 우리 도메인 지식(channel_id+biz_date)의 일이다
```

세 가지 구조적 한계:

| 한계                       | 왜 트레이스가 못 하나                                                                                                                                                       | correlation_id가 메꾸는 방식                                          |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------- |
| ① 시간을 못 거슬러 올라간다   | 트레이스는 "지금 시작해서 앞으로 전파"만 가능. 여러 메시지를 묶어 한 번에 처리하는 배치성 작업(예: cycle_loop)이 다루는 메시지들은 서로 다른 과거 시점에 각자 별도로 들어온 것들이라, 지금 시작하는 트레이스가 그 과거들을 하나로 묶을 방법이 없다 | `channel_id`+`biz_date`처럼 DB에 이미 저장된 도메인 값으로 묶는다(트레이스가 아니라 쿼리) |
| ② 재시도가 트레이스를 끊는다  | 큐 기반 재시도가 완전히 새 메시지·새 실행으로 이루어지면 트레이스도 새로 시작(위 다이어그램 A→B). 실패한 시도와 재시도가 인과적으로 안 이어짐                                                                              | `correlation_id`를 "이번 시도"가 아니라 "이 업무 단위"로 정의하면 여러 트레이스에 걸쳐 같은 값 유지 가능 |
| ③ 큐(SQS/SNS)를 건너면 전파가 저절로 안 된다 | Datadog 자체 문서·이슈로 확인됨 — SQS/SNS는 특수 처리(메시지 속성에 트레이스 정보를 실어야 함)가 필요하고, 언어별로 지원 범위가 다르며 SNS→SQS 팬아웃 같은 조합은 별도 이슈로 계속 보고되는 중 ([dd-trace-java #3411](https://github.com/DataDog/dd-trace-java/issues/3411), [dd-trace-js #1280](https://github.com/DataDog/dd-trace-js/issues/1280)) | 우리 필드는 메시지 본문(payload)에 직접 실어 보내므로 트레이싱 설정과 무관하게 항상 전파됨 |

## 3. 정리 — "역할 분담"이 정확한 표현이다

```
                    ┌───────────────── 하나의 실행(공짜 아님, APM 계측 필요) ─────────────────┐
                    │   dd.trace_id : 이번 HTTP 호출이 내부적으로 뭘 했는지, 어디서 얼마나       │
                    │                 걸렸는지 — "현미경"                                       │
                    └──────────────────────────────────────────────────────────────────────────┘

┌────────────────────────── 여러 실행에 걸친 하나의 업무(재시도·시간차 포함) ──────────────────────────┐
│   correlation_id : 이 메시지/이 사이클이 시간이 걸리더라도, 몇 번을 실패하고 재시도하더라도            │
│                     "결국 같은 건"이라는 것 — "책갈피"                                                 │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**결론**: 완전히 다른 개념이 아니라 **책임 범위가 다른 상하위 관계**에 가깝다. `dd.trace_id`는 실행 1건 안쪽을 현미경으로 보여주고, `correlation_id`는 그 실행들을 시간·재시도를 넘어 하나의 업무로 묶어준다. 둘 다 있으면 "이 업무(`correlation_id=X`)가 실패했는데, 그중 이번 시도(`dd.trace_id=B`)는 정확히 어디서 느려졌지?"처럼 서로를 보완해서 쓴다 — 하나가 다른 하나를 대체하지 못한다.

APM이 잘 계측된 단일 실행 안에서는 실제로 중복이고, 그 중복을 감수할 가치가 있는 지점은 딱 "재시도·시간차·큐 경계를 넘어야 하는 곳"뿐이다.

## 배경 — Datadog 예약 속성 확인 (충돌 여부)

`correlation_id`라는 이름 자체는 Datadog과 충돌하지 않는다 (공식 문서로 확인):

| 구분 | 실제 필드명 |
|---|---|
| Datadog Log Management의 예약 속성(전체 6개, 다른 이름은 예약 아님) | `host`, `source`, `status`, `service`, `trace_id`, `message` |
| Datadog APM(`ddtrace` 라이브러리)이 로그에 자동 주입하는 필드 | `dd.env`, `dd.service`, `dd.version`, `dd.trace_id`, `dd.span_id` |

- [Attributes and Aliasing](https://docs.datadoghq.com/logs/log_configuration/attributes_naming_convention/)
- [Connect Logs and Traces (Python)](https://docs.datadoghq.com/tracing/other_telemetry/connect_logs_and_traces/python/)

지켜야 할 규칙은 하나: 필드명을 접두사 없는 `trace_id`로 짓지 말 것. `correlation_id`는 이 예약어와 겹치지 않는다.

## 관련
- [[dd-trace-id-vs-correlation-id]] 관련 배경: tax-agent 저장소의 `consult-task-engine`/`consult-task-orchestrator` 로깅에 correlation_id 도입 검토 (Jira AOTA-114)
