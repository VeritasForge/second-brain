---
created: 2026-04-21
source: claude-code
tags: [kotlin, spring-boot, gradle, project-structure, docker, ci-cd, ktlint, detekt]
---

# 📖 Kotlin 프로젝트 구조와 도구 — Spring Boot 현업 셋업

> 💡 **한줄 요약**: Kotlin+Spring Boot 프로젝트는 Controller/Service/Repository 계층 + Gradle Kotlin DSL을 기본으로, ktlint/detekt(린트) + Jib(Docker) + GitHub Actions CI를 조합하면 엔터프라이즈 수준의 개발 환경을 구축할 수 있다.
>
> 📌 **핵심 키워드**: Gradle KTS, multi-module, ktlint, detekt, Jib, layered JAR, GraalVM
> 📅 **기준**: Kotlin 2.1+ / Spring Boot 3.x (2025)

---

## 1️⃣ Spring Boot 프로젝트 레이아웃

```
myproject/
├── build.gradle.kts           ← 루트 빌드 스크립트
├── settings.gradle.kts        ← 멀티 모듈 설정
├── gradle/
│   └── libs.versions.toml     ← Version Catalog
│
├── app/                       ← 실행 모듈
│   └── src/main/kotlin/
│       └── com/myapp/
│           ├── MyApplication.kt
│           ├── api/            ← Controller (HTTP 진입점)
│           ├── service/        ← 비즈니스 로직
│           ├── repository/     ← DB 접근
│           ├── domain/         ← 도메인 모델 (entity, VO)
│           └── config/         ← Spring 설정
│
├── core/                      ← 공유 도메인/유틸 모듈
│   └── src/main/kotlin/
│
└── infra/                     ← 인프라 모듈 (DB, 외부 API)
    └── src/main/kotlin/
```

### Version Catalog

```toml
# gradle/libs.versions.toml
[versions]
kotlin = "2.1.0"
spring-boot = "3.3.0"
coroutines = "1.9.0"
mockk = "1.13.12"

[libraries]
spring-boot-starter-web = { module = "org.springframework.boot:spring-boot-starter-web" }
coroutines-core = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core", version.ref = "coroutines" }
mockk = { module = "io.mockk:mockk", version.ref = "mockk" }
```

### 🔄 Go와 비교

| 개념 | Kotlin/Spring | Go |
|------|-------------|-----|
| 진입점 | `@SpringBootApplication` class | `cmd/*/main.go` |
| 계층 구조 | api/service/repository | handler/service/repository (관습) |
| 비공개 모듈 | `internal` 가시성 | `internal/` 디렉터리 |
| 의존성 | `libs.versions.toml` | `go.mod` |

---

## 2️⃣ Gradle Kotlin DSL

```kotlin
// build.gradle.kts
plugins {
    kotlin("jvm") version libs.versions.kotlin
    kotlin("plugin.spring") version libs.versions.kotlin
    id("org.springframework.boot") version libs.versions.spring.boot
}

kotlin {
    jvmToolchain(21)  // JDK 21 타겟
    compilerOptions {
        freeCompilerArgs.addAll("-Xjsr305=strict")  // null 어노테이션 엄격 처리
    }
}

tasks.test {
    useJUnitPlatform()
}
```

---

## 3️⃣ 린팅 — ktlint + detekt

### ktlint (포매팅)

```kotlin
// build.gradle.kts
plugins {
    id("org.jlleitschuh.gradle.ktlint") version "12.1.0"
}

ktlint {
    version.set("1.3.0")
    android.set(false)
}
```

### detekt (정적 분석)

```yaml
# detekt.yml
complexity:
  LongMethod:
    threshold: 30
  ComplexCondition:
    threshold: 4
style:
  MagicNumber:
    active: true
    ignoreNumbers: ['-1', '0', '1', '2']
```

| 도구 | 역할 | Go 대응 |
|------|------|--------|
| **ktlint** | 포매팅 (Kotlin 스타일 가이드 기반) | gofmt |
| **detekt** | 정적 분석 (복잡도, 코드 스멜) | golangci-lint |

---

## 4️⃣ Docker 배포

### Jib (Docker 없이 이미지 빌드)

```kotlin
// build.gradle.kts
plugins {
    id("com.google.cloud.tools.jib") version "3.4.0"
}

jib {
    from { image = "eclipse-temurin:21-jre-alpine" }
    to { image = "myregistry/myapp:${version}" }
    container {
        jvmFlags = listOf("-Xms512m", "-Xmx1024m", "-XX:+UseZGC")
        ports = listOf("8080")
    }
}
```

```bash
# Docker 데몬 없이 이미지 빌드!
./gradlew jibDockerBuild
```

### Layered JAR (Docker multi-stage 대안)

```dockerfile
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY build/libs/myapp-0.1.0.jar app.jar
# Spring Boot layered JAR: 의존성 캐싱 최적화
RUN java -Djarmode=layertools -jar app.jar extract

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=0 /app/dependencies/ ./
COPY --from=0 /app/spring-boot-loader/ ./
COPY --from=0 /app/snapshot-dependencies/ ./
COPY --from=0 /app/application/ ./
ENTRYPOINT ["java", "org.springframework.boot.loader.launch.JarLauncher"]
```

### GraalVM Native Image

```bash
./gradlew nativeCompile
# → 50ms 시작, ~80MB 바이너리, Docker scratch 가능
```

| 방식 | 이미지 크기 | 시작 시간 | 빌드 시간 |
|------|-----------|---------|---------|
| FAT JAR | ~300MB | 2-5s | 빠름 |
| Jib (JRE alpine) | ~200MB | 2-5s | 빠름 |
| Layered JAR | ~200MB (캐시 효율) | 2-5s | 빠름 |
| **GraalVM Native** | ~100MB | **~50ms** | 느림 (수 분) |

---

## 5️⃣ CI/CD 파이프라인

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 21
      - uses: gradle/actions/setup-gradle@v4

      - run: ./gradlew ktlintCheck
      - run: ./gradlew detekt
      - run: ./gradlew test
      - run: ./gradlew bootJar

      - uses: actions/upload-artifact@v4
        with:
          name: jar
          path: app/build/libs/*.jar
```

---

## 6️⃣ 관측성 (Observability)

### Spring Boot Actuator

```kotlin
// application.yml
management:
  endpoints:
    web:
      exposure:
        include: health,metrics,prometheus
  endpoint:
    health:
      show-details: when_authorized
```

| 도구 | 역할 | Go 대응 |
|------|------|--------|
| Actuator `/health` | 헬스 체크 | 커스텀 핸들러 |
| Actuator `/metrics` | Micrometer 메트릭 | `expvar` / Prometheus client |
| Actuator `/prometheus` | Prometheus 메트릭 | promhttp |
| Spring Boot Admin | 대시보드 | 없음 (Grafana 직접) |

---

## 📎 출처

1. [Spring Boot Gradle Plugin](https://docs.spring.io/spring-boot/gradle-plugin/) — Gradle 플러그인
2. [Jib Documentation](https://github.com/GoogleContainerTools/jib) — Docker 없이 이미지 빌드
3. [detekt Documentation](https://detekt.dev/) — 정적 분석
4. [GraalVM Spring Support](https://docs.spring.io/spring-boot/reference/packaging/native-image/) — Native Image

---

> 📌 **이전 문서**: [[06-kotlin-testing-patterns]]
> 📌 **관련**: [[02-kotlin-architecture-and-runtime]] §5 (배포)
