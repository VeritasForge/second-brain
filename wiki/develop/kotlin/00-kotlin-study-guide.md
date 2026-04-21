---
created: 2026-04-21
source: claude-code
tags: [kotlin, spring, study-guide, index, learning-path]
---

# 📖 Kotlin+Spring 학습 가이드 — 시리즈 허브

> 💡 **한줄 요약**: Kotlin 언어 + Spring Framework를 체계적으로 학습하기 위한 8개 문서 시리즈 + 기존 Spring Deep Dive/면접 Q&A의 진입점.
>
> 📅 **기준**: Kotlin 2.1+ / Spring Boot 3.x (2025)

---

## 📚 전체 문서 목록

### 학습 시리즈

| # | 문서 | 핵심 내용 |
|---|------|----------|
| 01 | [[01-kotlin-philosophy-and-differentiation]] | JetBrains 기원, 핵심 가치 4개, 4개 언어 비교 |
| 02 | [[02-kotlin-architecture-and-runtime]] | K2 컴파일러, JVM, GC, 코루틴 런타임, Spring Boot 시작 |
| 03 | [[03-kotlin-basic-syntax]] | null safety, data/sealed class, when, extension |
| 04 | [[04-kotlin-advanced-syntax-and-patterns]] | 코루틴, Spring DI/AOP, 제네릭, DSL, scope function |
| 05 | [[05-kotlin-developer-essentials-by-seniority]] | Junior→Staff (Kotlin+Spring 이중 트랙) |
| 06 | [[06-kotlin-testing-patterns]] | JUnit5, MockK, Spring test slices, 코루틴 테스트 |
| 07 | [[07-kotlin-project-structure-and-tooling]] | Gradle KTS, ktlint/detekt, Jib, CI/CD |

### 기존 Deep Dive / 면접 문서

| 문서 | 위치 | 내용 |
|------|------|------|
| [[kotlin-spring]] | interview-prep/ | Staff Engineer 면접 Q&A (26문항) |
| [[kotlin-vs-go]] | develop/ | Kotlin vs Go 언어 선택 가이드 |
| [[spring-aop-complete-guide]] | develop/ | Spring AOP 완전 가이드 |
| [[spring-di-bean-test-deep-dive]] | develop/ | Spring DI/Bean/테스트 Deep Dive |
| [[spring-di-deep-dive-followup-q1-q11]] | develop/ | Spring DI 심화 Q&A (11문항) |
| [[coroutine-gmp-vthread]] | performance/ | 코루틴/goroutine/VThread 비교 |
| [[gc-g1-zgc]] | performance/ | G1/ZGC/Go GC/Python RC 비교 |

---

## 🎯 페르소나별 학습 경로

### 🟢 Kotlin 입문자 (Java 경험 있음)
```
01 철학 → 03 기본 문법(§2 null safety) → 04 고급(§6 scope function)
→ 07 프로젝트 구조 → 05 Junior 레벨
```

### 🔄 Go → Kotlin 전환자
```
01 철학(§6 전환 가이드) → 03 기본 문법(§2 null safety, §6 OOP)
→ 04 고급(§1 코루틴 vs goroutine) → 02 아키텍처(§2 JVM vs Go runtime)
```

### 🎯 면접 준비자
```
05 필수 지식(해당 레벨) → 02 아키텍처(§3 코루틴, §4 Spring 시작)
→ 04 고급(§1-3) → [[kotlin-spring]] (26문항)
```
