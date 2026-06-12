---
tags: [shell, fish, cli, directory, posix]
created: 2026-06-12
---

# 쉘에서 `-`로 시작하는 디렉토리 탐색 문제

## 🔍 문제 상황

Claude Code는 프로젝트 경로를 `~/.claude/projects/` 아래에 **슬래시를 대시(`-`)로 인코딩**하여 저장한다.

```
실제 프로젝트 경로: /home/user/workspace/my-project
저장 디렉토리명:    -home-user-workspace-my-project
```

이 디렉토리로 이동하려 할 때 에러가 발생한다:

```bash
❯ cd -home-user-workspace-my-project
cd: -home-user-workspace-my-project: unknown option
```

## 🎯 원인

쉘이 `-`로 시작하는 문자열을 **경로가 아닌 옵션 플래그**로 해석하기 때문이다.

| 입력                      | 쉘의 해석                              |
| ------------------------- | -------------------------------------- |
| `cd -dirname`             | `-dirname`을 옵션 플래그로 파싱 → 에러 |
| `cd /absolute/path`       | `/`로 시작하므로 절대 경로로 인식 → 정상 |

## ✅ 해결 방법

### 방법 1: `./` 접두사 (권장)

```bash
cd ./-home-user-workspace-my-project
```

`./`가 있으면 쉘이 **상대 경로**로 인식하여 옵션 파싱을 건너뛴다.

### 방법 2: `--` 옵션 종료 선언

```bash
cd -- -home-user-workspace-my-project
```

### 방법 3: 원본 프로젝트 경로로 직접 이동

```bash
cd ~/workspace/my-project
```

---

## 📖 `--` 의 의미

POSIX 표준에서 정의된 관례로, `--` 이후에 오는 모든 인자를 **옵션이 아닌 순수한 인자(경로, 파일명 등)로만 해석**하라는 신호다.

```
명령어 [옵션들] -- [순수 인자들]
```

### 동작 원리

```bash
cd -foo       # 쉘이 "-foo"를 옵션으로 파싱 시도 → 에러
cd -- -foo    # "--" 이후라서 "-foo"를 경로로 취급 → 정상
```

### 다른 명령어에서의 활용

```bash
# 파일명이 "-rf"인 파일 삭제
rm -- -rf

# 파일명이 "--help"인 파일 읽기
cat -- --help

# 패턴이 "-"로 시작하는 grep
grep -- -pattern file.txt
```

**한 줄 요약:** `--`는 "지금부터 옵션 파싱 끝, 이후는 모두 인자"라고 쉘에게 선언하는 것이다.
