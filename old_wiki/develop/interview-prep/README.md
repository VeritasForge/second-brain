# FAANG Staff/Principal Engineer Interview Prep

> 19년차 시니어 엔지니어의 미국 빅테크 L6/L7 도전을 위한 면접 Q&A 모음

## 개요

| 문서 | 문항 수 | 카테고리 | 프레임워크 |
|------|---------|----------|-----------|
| [Python/FastAPI/SQLAlchemy](python-fastapi-sqlalchemy.md) | 28 | 10 | Python 3.12+, FastAPI 0.115+, Pydantic v2, SQLAlchemy 2.0+ |
| [Golang](golang.md) | 26 | 10 | Go 1.22+ |
| [Kotlin/Spring](kotlin-spring.md) | 26 | 10 | Kotlin 2.0+, Spring Boot 3.3+, Spring Framework 6.1+ |
| [Cross-cutting Staff Engineer](cross-cutting-staff-engineer.md) | 39 | 7 | 폴리글랏 (Python/Go/Kotlin 비교) |
| [AI Software Engineer](ai-software-engineer.md) | 35 | 12 | LLM, RAG, Agent, MLOps, AI Safety |
| **총계** | **154** | **49** | |

## 난이도

모든 문항은 **⭐⭐⭐⭐⭐ (L6/L7)** 난이도입니다.
- 경력 5년 미만이 답할 수 있는 문제 없음
- 60%+ 문항이 실제 프로덕션 시나리오 기반
- 30초 구글링으로 답할 수 없는 깊이

## 답변 구조

모든 Q&A는 6-Step 구조를 따릅니다:

```
🧒 12살 비유        → 직관적 이해
Step 1 — 맥락       → 면접관이 평가하는 것
Step 2 — 핵심 기술   → 정밀한 기술적 답변
Step 3 — 다양한 관점  → 성능/정확성/스케일별 차이
Step 4 — 구체적 예시  → 프로덕션 코드 + 주석
Step 5 — 트레이드오프  → 대안 비교 테이블
Step 6 — 심화 학습    → 성장 경로
🎯 면접관 평가 기준   → L6 PASS / L7 EXCEED / RED FLAG
```

## 스택별 카테고리

### Python/FastAPI/SQLAlchemy (28문항)

| # | Category | Q번호 |
|---|----------|-------|
| 1 | Python Runtime Internals | Q1-Q3 |
| 2 | Async/Concurrency Deep Dive | Q4-Q6 |
| 3 | FastAPI Internals & Production | Q7-Q9 |
| 4 | SQLAlchemy Session & ORM | Q10-Q12 |
| 5 | DB Connection Management | Q13-Q14 |
| 6 | Type System & Metaprogramming | Q15-Q17 |
| 7 | Performance & Profiling | Q18-Q19 |
| 8 | Testing at Scale | Q20-Q21 |
| 9 | Production Debugging | Q22-Q23 |
| 10 | Design Patterns in Python | Q24-Q28 |

### Golang (26문항)

| # | Category | Q번호 |
|---|----------|-------|
| 1 | Goroutine Scheduler (G-M-P) | Q1-Q3 |
| 2 | Memory Model & GC | Q4-Q6 |
| 3 | Channel Patterns | Q7-Q9 |
| 4 | Interface Design | Q10-Q12 |
| 5 | Error Handling | Q13-Q14 |
| 6 | Performance Engineering | Q15-Q17 |
| 7 | sync Primitives | Q18-Q20 |
| 8 | Production Patterns | Q21-Q22 |
| 9 | Testing Strategies | Q23-Q24 |
| 10 | Module System & Build | Q25-Q26 |

### Kotlin/Spring (26문항)

| # | Category | Q번호 |
|---|----------|-------|
| 1 | Coroutines Deep Dive | Q1-Q3 |
| 2 | Flow & Reactive | Q4-Q6 |
| 3 | JVM Internals | Q7-Q9 |
| 4 | Spring DI & Lifecycle | Q10-Q12 |
| 5 | Spring WebFlux & Reactive | Q13-Q14 |
| 6 | Kotlin Language Mastery | Q15-Q17 |
| 7 | Spring Security | Q18-Q19 |
| 8 | Testing in Spring | Q20-Q21 |
| 9 | Spring Boot Operational | Q22-Q23 |
| 10 | Data Access | Q24-Q26 |

### Cross-cutting Staff Engineer (39문항)

| # | Category | Q번호 | 특징 |
|---|----------|-------|------|
| 1 | System Design at Scale | Q1-Q8 | Polyglot Implementation Notes 포함 |
| 2 | Distributed Systems | Q9-Q14 | CAP, Consensus, 분산 트랜잭션 |
| 3 | Database Internals | Q15-Q20 | 스택별 커넥션 풀링 비교 |
| 4 | Networking & Protocols | Q21-Q25 | TCP, HTTP/2-3, gRPC |
| 5 | Observability & SRE | Q26-Q30 | OpenTelemetry, SLO/SLI |
| 6 | Technical Leadership | Q31-Q35 | STAR 포맷 답변 |
| 7 | Security Across Stacks | Q36-Q39 | 3스택 보안 비교 |

### AI Software Engineer (35문항)

| # | Category | Q번호 |
|---|----------|-------|
| 1 | Transformer & LLM Internals | Q1-Q3 |
| 2 | Training & Fine-tuning | Q4-Q6 |
| 3 | LLM Inference & Serving | Q7-Q9 |
| 4 | RAG Architecture | Q10-Q12 |
| 5 | AI Agent & Tool Use | Q13-Q15 |
| 6 | Prompt Engineering & Optimization | Q16-Q18 |
| 7 | Embedding & Vector Search | Q19-Q21 |
| 8 | Evaluation & Testing | Q22-Q24 |
| 9 | MLOps & AI Infrastructure | Q25-Q27 |
| 10 | AI Safety & Guardrails | Q28-Q30 |
| 11 | Data Engineering for AI | Q31-Q32 |
| 12 | AI System Design | Q33-Q35 |

## 학습 플랜 (12주)

| 주차 | 포커스 | 일일 목표 |
|------|--------|----------|
| 1-2 | Python/FastAPI/SQLAlchemy | 2-3문항/일 (Cat 1-5) |
| 3-4 | Python 마무리 + Golang 시작 | 2-3문항/일 (Python Cat 6-10, Go Cat 1-3) |
| 5-6 | Golang | 2-3문항/일 (Cat 4-10) |
| 7-8 | Kotlin/Spring | 2-3문항/일 (Cat 1-6) |
| 9-10 | Kotlin 마무리 + Cross-cutting 시작 | 2-3문항/일 (Kotlin Cat 7-10, Cross Cat 1-3) |
| 11-12 | Cross-cutting + 종합 복습 | 2-3문항/일 (Cross Cat 4-7) + 약점 보강 |

## 사용법

1. **순차 학습**: 각 스택 문서의 카테고리 순서대로 진행
2. **약점 집중**: 자신 없는 카테고리를 먼저 공략
3. **모의 면접**: 질문만 보고 답변 후 정답과 비교
4. **크로스 스택**: 시스템 디자인 문제에서 3개 스택 구현 차이를 설명하는 연습
5. **RED FLAG 체크**: 각 문항의 RED FLAG를 확인하여 실수 방지

## 생성 정보

- 생성일: 2026-03-17
- 생성 방식: Claude Code 병렬 Subagent (스택별 독립 생성 → Cross-cutting 합성)
- 응답 가이드라인: 10가지 원칙 (맥락, 다관점, 단계별, 예시, 대안, 12살 비유 등) 적용
