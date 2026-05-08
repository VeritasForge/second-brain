---
tags: [git, sort, version-sort, refname, natural-sort]
created: 2026-05-08
---

# Git Ref 정렬 완벽 가이드 — 자연 정렬과 `v:refname`

## 🎯 한눈에 보기

git에서 태그/브랜치를 사람이 보기 자연스러운 순서로 정렬하려면 **자연 정렬(Natural Sort)** 을 사용해야 한다. git은 `--sort=v:refname` 옵션으로 이를 지원한다.

```fish
# 가장 최신 er-* 태그 1개 출력
git tag -l "er-*" --sort=-v:refname | head -n 1
```

---

## 1️⃣ 배경: 자연 정렬이란?

### 한 줄 요약

**사람이 보기에 자연스러운 순서**로 숫자를 정렬하는 방식. 컴퓨터의 기본 정렬(사전식)과 다르다.

### 사전식 vs 자연 정렬 비교

같은 파일 목록을 두 방식으로 정렬해보면:

| 원본    | 사전식 정렬 (`sort`) | 자연 정렬 (`sort -V`) |
| ------- | -------------------- | --------------------- |
| file1   | file1                | file1                 |
| file2   | file10 ❌            | file2 ✅              |
| file10  | file11 ❌            | file10 ✅             |
| file11  | file2 ❌             | file11 ✅             |

### 왜 이런 차이가 생길까?

#### 사전식 정렬 (기본)

컴퓨터는 문자열을 **한 글자씩 왼쪽부터** 비교한다. 마치 영어사전처럼.

```
"file10"  vs  "file2"
 ↓             ↓
'1' (코드 49) < '2' (코드 50)
```

→ `file10`이 `file2`보다 먼저 옴 ❌

#### 자연 정렬 (`-V` 또는 Version sort)

숫자가 나오면 **숫자 덩어리 전체를 하나의 수**로 인식해서 비교한다.

```
"file10"  vs  "file2"
 ↓             ↓
숫자 10 > 숫자 2
```

→ `file2`가 `file10`보다 먼저 옴 ✅

### 🌍 현실 세계 비유: 책장에 책 정리하기 📚

- **사전식**: "1권, 10권, 11권, 2권, 3권..." (도서관 사서가 글자 순서로만 정렬)
- **자연 정렬**: "1권, 2권, 3권, 10권, 11권..." (사람이 책 번호 보고 정렬)

후자가 자연스럽다. 그래서 "자연(Natural)" 정렬이다.

### 자연 정렬 옵션 정리

| 도구          | 옵션                                            | 설명                       |
| ------------- | ----------------------------------------------- | -------------------------- |
| GNU `sort`    | `-V`, `--version-sort`                          | 자연/버전 정렬             |
| `ls`          | `-v`                                            | 자연 정렬로 파일 나열      |
| `git tag`     | `--sort=v:refname`                              | 버전 정렬                  |
| Python        | `natsort` 라이브러리                            | `pip install natsort`      |
| JavaScript    | `localeCompare(b, undefined, {numeric: true})`  | 내장 자연 비교             |

---

## 2️⃣ Git의 `v:refname` 정렬 문법

### 분해해서 보기

```
--sort=v:refname
        ↑ ↑
        │ └─ refname: 정렬 대상 (태그/브랜치 이름)
        └─── v: version 정렬 모드 (자연 정렬)
```

### 옵션별 동작 비교

| 옵션                  | 의미                                 | 결과                       |
| --------------------- | ------------------------------------ | -------------------------- |
| `--sort=refname`      | 이름을 **사전식**으로 정렬           | `1.0`, `1.10`, `1.2` ❌    |
| `--sort=v:refname`    | 이름을 **버전(자연)식**으로 정렬     | `1.0`, `1.2`, `1.10` ✅    |
| `--sort=-v:refname`   | 버전 정렬 + **내림차순** (`-` 접두어) | `1.10`, `1.2`, `1.0`       |

> **참고**: `v:refname`과 `version:refname`은 완전히 동일하다. `v:`가 짧은 별칭이다.

### git이 지원하는 다른 sort 키들

```fish
git tag --sort=<key>
```

| 키                                     | 정렬 기준                       |
| -------------------------------------- | ------------------------------- |
| `refname`                              | 태그 이름 (사전식)              |
| `v:refname` 또는 `version:refname`     | 태그 이름 (버전식) ⭐           |
| `creatordate`                          | 태그 생성 날짜                  |
| `committerdate`                        | 커밋 날짜                       |
| `taggerdate`                           | annotated tag 생성 날짜         |

> 모든 키 앞에 `-`를 붙이면 내림차순이 된다. (예: `-creatordate` = 최신 날짜순)

---

## 3️⃣ `refname`의 정체: 컨텍스트별 의미

`refname`은 **"reference name (참조 이름)"** 의 줄임말로, 사용하는 명령어에 따라 가리키는 대상이 달라진다.

### git의 "ref" 개념

git에서 **ref(reference)**는 커밋을 가리키는 이름표다. 크게 3가지가 있다.

| ref 종류      | 실제 경로                       | 명령어            |
| ------------- | ------------------------------- | ----------------- |
| 태그          | `refs/tags/<이름>`              | `git tag`         |
| 로컬 브랜치   | `refs/heads/<이름>`             | `git branch`      |
| 원격 브랜치   | `refs/remotes/<원격>/<이름>`    | `git branch -r`   |

### 🌍 비유: 도서관의 분류 시스템 📚

`refname`은 **"책장 라벨"**이라고 생각하면 된다.

- **소설 코너**(`git tag`)에서 라벨을 보면 → 소설 제목
- **잡지 코너**(`git branch`)에서 라벨을 보면 → 잡지 이름
- **신문 코너**(`git branch -r`)에서 라벨을 보면 → 신문 이름

같은 "라벨"이라는 단어지만, 어느 코너에 있느냐에 따라 의미가 달라진다.

### 명령어별 동작

```fish
# 태그 정렬 → refs/tags/ 아래의 이름들을 버전 정렬
git tag --sort=v:refname

# 로컬 브랜치 정렬 → refs/heads/ 아래의 이름들을 버전 정렬
git branch --sort=v:refname

# 원격 브랜치 정렬 → refs/remotes/ 아래의 이름들을 버전 정렬
git branch -r --sort=v:refname

# 모든 ref 한 번에 (고급)
git for-each-ref --sort=v:refname
```

### 핵심 정리 다이어그램

```
"refname" = 컨텍스트에 따른 ref의 이름
            ↓
  ┌─────────┼──────────┐
  ↓         ↓          ↓
git tag  git branch  git branch -r
  ↓         ↓          ↓
태그명   로컬브랜치명  원격브랜치명
```

---

## 4️⃣ 실전: git tag 정렬 시나리오

### 시나리오: `er-*` 태그 정렬

#### 오름차순 (기본)

```fish
git tag -l | grep -E "^er-" | sort -V
```

#### 내림차순

```fish
# 방법 1: sort -Vr 사용
git tag -l | grep -E "^er-" | sort -Vr

# 방법 2: git의 내장 옵션 사용 (권장)
git tag -l "er-*" --sort=-v:refname
```

#### 가장 최신 버전만 추출

```fish
# 방법 1: 오름차순 + tail
git tag -l | grep -E "^er-" | sort -V | tail -n 1

# 방법 2: 내림차순 + head
git tag -l | grep -E "^er-" | sort -Vr | head -n 1

# 방법 3: git 내장 옵션 사용 (권장)
git tag -l "er-*" --sort=-v:refname | head -n 1
```

### 왜 git tag에서 자연 정렬이 중요한가

버전 태그는 보통 이렇게 생겼다:

```
er-1.0.0
er-1.2.0
er-1.10.0
er-1.11.0
er-2.0.0
```

`sort`만 쓰면 (사전식):

```
er-1.0.0
er-1.10.0  ← 1.2.0보다 먼저 와버림 ❌
er-1.11.0
er-1.2.0
er-2.0.0
```

`sort -V` 쓰면 (자연 정렬):

```
er-1.0.0
er-1.2.0   ✅
er-1.10.0  ✅
er-1.11.0
er-2.0.0
```

### 날짜 기준 정렬

```fish
# 가장 최근에 만든 태그 1개 (날짜 기준)
git tag --sort=-creatordate | head -n 1
```

---

## 5️⃣ 주의사항 및 팁

### macOS의 `sort` 주의점

macOS의 `sort`는 BSD 버전이라 `-V` 지원이 GNU만큼 완벽하지 않을 수 있다. Homebrew의 `coreutils`를 설치하면 `gsort -V`로 GNU 버전을 쓸 수 있다.

### 시맨틱 버저닝(SemVer) 한계

시맨틱 버저닝(`MAJOR.MINOR.PATCH`)은 자연 정렬과 궁합이 좋다. 단, `1.0.0-rc1` 같은 prerelease 태그는 SemVer 규칙대로는 `1.0.0`보다 작아야 하지만, `sort -V`는 이걸 정확히 처리하지 못할 수 있다.

### `refname:short` 별칭

짧은 이름(`refs/tags/v1.0` → `v1.0`)으로 정렬하고 싶을 때 `refname:short`를 쓸 수 있지만, 결과는 거의 같다.

### `refname` 전체 경로 정렬 주의

`refname`은 전체 경로 기준으로 정렬한다. 만약 `refs/tags/v1.0`과 `refs/heads/v1.0`을 함께 정렬한다면 알파벳 순으로 `heads`가 먼저 온다. 하지만 `git tag`나 `git branch`는 이미 한 종류만 보여주므로 신경 쓸 일은 거의 없다.
