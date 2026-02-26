---
created: 2026-02-09
source: manual
tags:
  - git
  - cli
  - branch-diff
---

## 특정 브랜치에 병합 된 티켓 찾기
`git log develop..release-v2-2-1 --format="%s" | grep -oE 'VITALCARES-[0-9]+' | sort -ur`