---
tags: [verification, corrections, jvm, go, epoll, hikaricp]
created: 2026-04-15
---

# 검증 결과 요약 — 기술 내용 정정 사항

---

## 1. CRITICAL (수정 완료) — 4건

| 원래 주장                                | 정정                                                                   |
| ---------------------------------------- | ---------------------------------------------------------------------- |
| Kotlin Dispatcher 글로벌 큐 1개          | **per-Worker 로컬 큐 + Work-Stealing 하이브리드** (Go GMP 영감)        |
| Virtual Thread 구조화된 동시성 없다      | **StructuredTaskScope가 Preview로 존재** (JDK 25 6th Preview)          |
| IOCP가 DMA로 유저 버퍼에 직접 쓴다        | **DMA는 NIC→커널 버퍼**. IOCP는 Proactor 패턴                         |
| epoll 2복사 vs IOCP 1복사               | **둘 다 1회 복사 동일**. Reactor vs Proactor 모델 차이                 |

## 2. HIGH (수정 완료) — 6건

| 원래 주장                             | 정정                                                      |
| ------------------------------------- | --------------------------------------------------------- |
| Dispatchers.IO 최대 64개 한계        | 기본값이며 설정/elasticity로 확장 가능                    |
| Spring MVC 코루틴 미지원             | suspend 함수 지원됨, WebFlux 전용만 미지원                |
| Go 10ms마다 선점                     | 10ms threshold + SIGURG + safe-point                      |
| epoll O(1)                           | epoll_wait O(1) + 반환 O(k) + 등록 O(log n)              |
| Java NIO = Level Trigger             | 기본 LT이나 Netty는 ET. 구현에 따라 다름                 |
| 성능 수치 (50K/100K/80K)            | IO-bound에서는 런타임 간 차이 미미. 구체 수치 제시 위험   |

## 3. 추가 검증에서 발견된 수정사항

| 원래 주장                                                 | 정정                                                                |
| --------------------------------------------------------- | ------------------------------------------------------------------- |
| Pool sizing 공식이 HikariCP의 것                         | **PostgreSQL 프로젝트 유래**, HikariCP wiki가 인용                  |
| G1이 Concurrent Marking에서 dirty card Write Barrier 사용 | **SATB Write Barrier**가 핵심. dirty card는 Remembered Set용 별개   |
| ZGC Load Barrier가 모든 object read에서 발동             | heap reference load 시만 발동. JIT 제거. throughput 1~5% 감소       |
| HikariCP keepalive-time 기본 30초, SELECT 1 사용         | 기본 **0 (비활성)**. `Connection.isValid()` (JDBC4). SELECT 1 아님  |
| DB 서버는 커넥션 풀을 관리하지 않는다                    | Oracle DRCP는 서버 프로세스 풀링으로 예외                           |
| Go 할당자가 tcmalloc 기반                                | tcmalloc에서 **영감을 받은** 독자적 할당자                          |
