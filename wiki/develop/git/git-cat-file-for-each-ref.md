---
tags: [git, git-internals, plumbing, cli]
created: 2026-04-21
---

# 🔧 Git 내부 명령어 가이드 — cat-file & for-each-ref

Git의 저수준(plumbing) 명령어로, 내부 객체와 참조를 직접 들여다보는 도구예요.

---

## git cat-file — Git 객체 검사 도구

### 핵심 개념

`git cat-file`은 **Git 내부 저장소(object database)에 저장된 객체의 내용을 들여다보는 명령**이에요.

> 🎒 비유: Git 저장소는 **거대한 창고**라고 생각해봐요. 창고 안에는 여러 종류의 상자(객체)가 있는데, `git cat-file`은 **상자를 열어서 안에 뭐가 들었는지 확인하는 도구**예요.

### Git 객체의 4가지 종류

Git 내부에는 모든 것이 **객체(object)**로 저장돼요:

| 객체 타입  | 역할               | 비유           |
| ---------- | ------------------ | -------------- |
| `blob`     | 파일 내용 저장      | 📄 문서 원본   |
| `tree`     | 디렉토리 구조 저장  | 📁 폴더        |
| `commit`   | 커밋 정보 저장      | 📋 작업 기록서 |
| `tag`      | Annotated Tag 저장  | 🏷️ 이름표     |

### 주요 옵션

| 옵션 | 의미             | 설명                          | 사용 예시                               |
| ---- | ---------------- | ----------------------------- | --------------------------------------- |
| `-t` | **type**         | 객체의 종류 출력               | `git cat-file -t HEAD` → `commit`       |
| `-s` | **size**         | 객체의 크기(바이트) 출력        | `git cat-file -s HEAD` → `245`          |
| `-p` | **pretty-print** | 객체 내용을 보기 좋게 출력      | `git cat-file -p HEAD` → 커밋 상세       |
| `-e` | **exist**        | 객체 존재 여부 확인 (종료코드로) | `git cat-file -e abc123`                |

> ⚠️ `-t`는 "태그(tag)"가 아니라 **"타입(type)"의 약자**예요!

### `-p` 옵션 사용 예시

```bash
# 커밋 객체의 내용 보기
$ git cat-file -p HEAD
tree 8a7b3c...
parent 5d6e7f...
author 홍길동 <hong@example.com> 1713700000 +0900
committer 홍길동 <hong@example.com> 1713700000 +0900

커밋 메시지 내용

# Annotated Tag 객체의 내용 보기
$ git cat-file -p v1.0.0
object 33f857b...
type commit
tag v1.0.0
tagger 홍길동 <hong@example.com> 1713700000 +0900

Release v1.0.0
```

### 동작 흐름

```
git cat-file -t v1.0.0
       │
       ▼
  Git Object DB에서
  v1.0.0이 가리키는
  객체를 찾음
       │
       ▼
  객체의 헤더를 읽음
  (헤더 형식: "type size\0content")
       │
       ▼
  type 부분만 출력
  → "tag" 또는 "commit"
```

### 태그 종류 확인에 활용

```bash
git cat-file -t v1.0.0
# "tag"    → Annotated Tag (tagger 정보 있음)
# "commit" → Lightweight Tag (tagger 정보 없음)
```

> 📌 태그 관련 상세 내용은 [[git-tag-annotated-lightweight]] 참조

---

## git for-each-ref — ref 순회 및 커스텀 포맷

### 핵심 개념

`git for-each-ref`는 **Git의 모든 참조(ref)를 순회하면서 원하는 정보를 뽑아내는 명령**이에요.

> 🎒 비유: 학교 교무실에 **모든 학생의 기록카드**가 있다고 생각해봐요. `git for-each-ref`는 **카드를 한 장씩 넘기면서 원하는 항목만 골라서 정리해주는 비서**예요.

### "ref"란?

Git에서 **ref(참조)**는 특정 커밋을 가리키는 **이름표**예요:

| ref 종류    | 저장 위치        | 예시                           |
| ----------- | ---------------- | ------------------------------ |
| 브랜치      | `refs/heads/`    | `refs/heads/main`              |
| 태그        | `refs/tags/`     | `refs/tags/v1.0.0`            |
| 원격 브랜치 | `refs/remotes/`  | `refs/remotes/origin/main`     |

### 사용법

```bash
# 모든 태그의 이름, 작성자, 날짜를 테이블로 출력
git for-each-ref --format='%(refname:short) | %(taggername) | %(taggerdate:short)' refs/tags/

# 모든 브랜치를 최근 커밋 날짜순으로 정렬
git for-each-ref --sort=-committerdate --format='%(refname:short) %(committerdate:relative)' refs/heads/

# 특정 태그의 tagger만 추출
git for-each-ref --format='%(taggername) %(taggeremail)' refs/tags/v1.0.0
```

### `--format` 주요 필드

| 필드                | 설명                                    |
| ------------------- | --------------------------------------- |
| `%(refname)`        | 전체 ref 이름 (`refs/tags/v1.0.0`)      |
| `%(refname:short)`  | 짧은 이름 (`v1.0.0`)                    |
| `%(objecttype)`     | 객체 타입 (`commit`, `tag`)              |
| `%(taggername)`     | 태그 작성자 이름                          |
| `%(taggeremail)`    | 태그 작성자 이메일                        |
| `%(taggerdate)`     | 태그 생성 날짜                            |
| `%(committerdate)`  | 커밋 날짜                                |
| `%(subject)`        | 메시지 첫 줄                              |

### `git tag -l` vs `git for-each-ref`

| 비교   | `git tag -l`         | `git for-each-ref`                |
| ------ | -------------------- | --------------------------------- |
| 용도   | 태그 이름 나열        | **커스텀 포맷**으로 상세 정보 추출   |
| 유연성 | 낮음                  | 높음 (format 자유 지정)             |
| 정렬   | 제한적                | `--sort` 옵션으로 자유 정렬          |
| 대상   | 태그만                | 브랜치, 태그, 원격 ref 모두          |

---

## 두 명령의 관계

```
git cat-file                    git for-each-ref
   │                               │
   ▼                               ▼
"하나의 객체를                   "여러 ref를 순회하며
 깊이 들여다보기"                 원하는 정보만 추출"
   │                               │
   ▼                               ▼
객체 타입, 크기, 내용 확인       이름, 작성자, 날짜, 정렬
```

- **cat-file**: 특정 객체 하나를 깊이 파고들 때
- **for-each-ref**: 여러 ref를 한눈에 조회하거나 스크립트에서 활용할 때

---

## 핵심 정리

1. `git cat-file`은 Git 내부 객체를 들여다보는 저수준(plumbing) 명령
2. `-t`(type), `-s`(size), `-p`(pretty-print), `-e`(exist) 4개 옵션이 핵심
3. `git for-each-ref`는 모든 ref를 순회하며 커스텀 포맷으로 정보를 추출하는 쿼리 도구
4. `--format` 필드와 `--sort`로 유연한 데이터 추출이 가능
5. 두 명령 모두 일반 사용보다는 **스크립트/자동화/디버깅**에서 주로 활용

> 📌 관련 문서: [[git-tag-annotated-lightweight]], [[git-reflog-recovery-guide]]
