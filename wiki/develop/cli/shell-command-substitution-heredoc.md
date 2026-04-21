---
tags: [shell, bash, cli, heredoc]
created: 2026-04-21
---

# 🧅 Shell Command Substitution + Here Document 패턴 가이드

셸에서 여러 줄 텍스트를 안전하게 하나의 문자열 인자로 전달하는 패턴을 분해합니다.

---

## 전체 구조

```bash
git tag -a v1.2.0 -m "$(cat <<'EOF'
Release v1.2.0

주요 변경사항:
- 사용자 인증 기능 추가
EOF
)"
```

바깥에서 안쪽으로 하나씩 벗겨볼게요 🧅

---

## Layer 1: `"$( ... )"` — Command Substitution (명령 치환)

```bash
"$( 명령어 )"
```

- `$()` 안의 명령을 **실행하고, 그 출력을 문자열로 치환**
- 쌍따옴표 `""`로 감싸서 결과를 하나의 문자열로 유지

> 🎒 비유: **"이 봉투 안의 편지를 꺼내서 여기에 붙여넣어줘"**

```bash
echo "오늘은 $(date)입니다"
# → "오늘은 Mon Apr 21 10:00:00 KST 2026입니다"
```

---

## Layer 2: `cat` — 표준입력을 그대로 출력

- `cat`은 입력받은 것을 **그대로 출력**하는 명령
- Here Document에서 받은 텍스트를 그대로 내보내는 역할

---

## Layer 3: `<<'EOF' ... EOF` — Here Document (히어 독)

```bash
<<'EOF'
여기 안에 있는 모든 텍스트는
여러 줄이어도
하나의 입력으로 전달됩니다
EOF
```

- `<<` : "지금부터 여러 줄 텍스트를 입력할게" 라는 시작 신호
- `'EOF'` : 텍스트의 **끝을 알리는 구분자** (어떤 단어든 가능: HEREDOC, END 등)
- `EOF` (마지막) : "여기서 텍스트 끝!" 이라는 종료 신호

> 🎒 비유: 편지를 쓸 때 **"여기서부터"** ~ **"여기까지"** 표시하는 것

---

## `<<'EOF'` vs `<<EOF` — 따옴표 유무 차이

| 시작 구분자             | 변수 치환                    | 예시                                |
| ---------------------- | ---------------------------- | ----------------------------------- |
| `<<EOF` (따옴표 없음)   | ✅ `$변수`가 값으로 치환됨     | `$HOME` → `/Users/cjynim`          |
| `<<'EOF'` (따옴표 있음) | ❌ **있는 그대로** 출력        | `$HOME` → `$HOME`                  |

```bash
# 변수 치환 O
cat <<EOF
홈 디렉토리: $HOME
EOF
# → 홈 디렉토리: /Users/cjynim

# 변수 치환 X (있는 그대로)
cat <<'EOF'
홈 디렉토리: $HOME
EOF
# → 홈 디렉토리: $HOME
```

---

## 전체 조립 흐름

```
git tag -a v1.2.0 -m "$(cat <<'EOF'
Release v1.2.0
주요 변경사항:
- 사용자 인증 기능 추가
EOF
)"

실행 순서:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 1: <<'EOF' ... EOF
        → 여러 줄 텍스트를 cat에 전달

Step 2: cat이 받아서 그대로 출력
        → "Release v1.2.0\n주요 변경사항:\n- 사용자 인증 기능 추가"

Step 3: $() 가 cat의 출력을 캡처
        → 문자열로 치환

Step 4: "" 로 감싸져서 -m 의 인자로 전달
        → git tag -a v1.2.0 -m "Release v1.2.0
           주요 변경사항:
           - 사용자 인증 기능 추가"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 왜 이 패턴을 쓰나?

```bash
# ❌ 줄바꿈이 제대로 처리 안 될 수 있음
git tag -a v1.2.0 -m "Release v1.2.0
주요 변경사항..."     # 셸에 따라 동작이 다름

# ✅ Here Document로 깔끔하게 여러 줄 전달
git tag -a v1.2.0 -m "$(cat <<'EOF'
Release v1.2.0

주요 변경사항:
- 사용자 인증 기능 추가
EOF
)"
```

**장점:**
- 여러 줄 텍스트를 **안전하게** 하나의 인자로 전달
- `<<'EOF'`를 쓰면 **변수 치환 없이** 있는 그대로 전달 (의도치 않은 치환 방지)
- **어떤 셸에서든** 일관되게 동작

---

## 실무 활용 예시

### git commit 메시지

```bash
git commit -m "$(cat <<'EOF'
feat: 사용자 인증 기능 추가

- OAuth 2.0 기반 로그인 구현
- JWT 토큰 관리 추가
- 세션 만료 처리 구현

Closes #123
EOF
)"
```

### 멀티라인 변수 할당

```bash
SQL_QUERY="$(cat <<'EOF'
SELECT u.name, u.email
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.created_at > '2026-01-01'
ORDER BY u.name
EOF
)"
```

> 📌 git tag에서의 활용 예시는 [[git-tag-annotated-lightweight]] 참조

---

## 관련 패턴: `<<<` (Here String)

```bash
# Here Document의 한 줄 버전
grep "error" <<< "$LOG_OUTPUT"
```

| 패턴             | 용도                  |
| ---------------- | --------------------- |
| `<<EOF ... EOF`  | 여러 줄 텍스트 전달    |
| `<<<`            | 한 줄 문자열 전달      |
| `< file`         | 파일 내용 전달         |

---

## 핵심 정리

1. `"$(cat <<'EOF' ... EOF)"`는 **Here Document + cat + Command Substitution**의 조합
2. `<<'EOF'`(따옴표 있음)는 변수 치환 없이 있는 그대로 전달
3. `<<EOF`(따옴표 없음)는 `$변수`가 값으로 치환됨
4. 여러 줄 텍스트를 안전하게 하나의 문자열 인자로 전달할 때 사용
5. git commit/tag 메시지, SQL 쿼리, 설정 파일 생성 등에 널리 활용

> 📌 관련 문서: [[git-tag-annotated-lightweight]], [[glob-pattern-matching-deep-dive]], [[file-search-find-rg-grep]]
