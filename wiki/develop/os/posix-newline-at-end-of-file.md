---
tags: [posix, linux, newline, unix, text-file, develop]
created: 2026-04-21
---

# POSIX 파일 끝 Newline 원칙

## 📌 핵심: POSIX 표준의 "텍스트 파일" 정의

POSIX (Portable Operating System Interface) 표준에서 **텍스트 파일의 "줄(line)"**을 이렇게 정의합니다:

> **"A sequence of zero or more non-newline characters plus a terminating newline character."**
> (0개 이상의 문자 + **끝에 반드시 newline(`\n`)**으로 구성)

## 🏠 현실 세계 비유

줄 = 기차 칸이라고 생각해봐:

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│  1번 칸  │──│  2번 칸  │──│  3번 칸  │──🔚 (종착역 표시)
└──────────┘  └──────────┘  └──────────┘
   줄 1 \n      줄 2 \n      줄 3 \n
```

각 기차 칸(줄)은 **연결부(`\n`)**가 있어야 "완성된 칸"이야. 마지막 칸도 마찬가지! 연결부 없는 칸은 "불완전한 칸"으로 취급돼.

## 🔍 왜 이런 원칙이 있을까?

| 이유               | 설명                                                                             |
| ------------------ | -------------------------------------------------------------------------------- |
| **도구 호환성**    | `cat`, `wc`, `grep`, `diff` 등 UNIX 도구들이 `\n`을 줄 구분자(terminator)로 사용 |
| **파일 합치기**    | `cat file1 file2` 할 때, file1 끝에 `\n`이 없으면 file2의 첫 줄과 붙어버림      |
| **diff/git**       | 마지막 newline 없으면 `\ No newline at end of file` 경고 표시                    |
| **쉘 스크립트**    | `while read line` 패턴에서 마지막 줄을 놓칠 수 있음                              |

## 📊 구체적 예시

```bash
# ❌ newline 없는 파일
$ printf "hello" > no_newline.txt
$ cat no_newline.txt
hello$                    # ← 프롬프트($)가 같은 줄에 붙음!

# ✅ newline 있는 파일
$ printf "hello\n" > with_newline.txt
$ cat with_newline.txt
hello
$                         # ← 깔끔하게 다음 줄에 프롬프트
```

```bash
# 파일 합치기 문제
$ printf "aaa" > a.txt
$ printf "bbb\n" > b.txt
$ cat a.txt b.txt
aaabbb                    # ← aaa와 bbb가 붙어버림! 😱
```

## ⚠️ 주의할 점

| 구분                   | 설명                                                                           |
| ---------------------- | ------------------------------------------------------------------------------ |
| **텍스트 파일만 해당** | 바이너리 파일(이미지, 실행파일 등)은 해당 없음                                 |
| **"원칙"이지 "강제"는 아님** | newline 없어도 파일이 깨지진 않지만, 도구 동작이 예상과 달라질 수 있음    |
| **에디터 자동 처리**   | Vim/Neovim, VS Code 등 대부분의 에디터가 저장 시 자동으로 마지막 newline 추가  |

## 🔗 Neovim에서의 관련 설정

참고로 Neovim에서는 `options.lua`에서 이걸 제어할 수 있어:

```lua
vim.opt.fixendofline = true   -- 기본값: 저장 시 마지막 newline 자동 추가
vim.opt.endofline = true      -- 기본값: 파일 끝에 EOL 존재
```

## 💡 정리

> **POSIX 텍스트 파일 = 모든 줄이 `\n`으로 끝나는 파일**
>
> 마지막 줄도 예외 없이 `\n`으로 끝나야 "완전한 텍스트 파일"

이건 리눅스만의 규칙이 아니라 **UNIX 계열 전체**(macOS 포함)의 공통 원칙이에요. Windows는 줄바꿈이 `\r\n`(CRLF)이라 조금 다르지만, "마지막에 줄바꿈이 있어야 한다"는 개념 자체는 동일합니다.
