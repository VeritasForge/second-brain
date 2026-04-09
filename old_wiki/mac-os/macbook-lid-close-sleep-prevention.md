---
created: 2026-02-09
source: claude-code
tags:
  - macos
  - sleep-prevention
  - system-config
---

## macOS 맥북 덮개 닫힘 시 슬립 방지 설정 가이드

### 1. 개요

macOS는 맥북 덮개(lid)를 닫으면 하드웨어 레벨에서 슬립 모드에 진입한다. 이는 과열 방지 및 배터리 보호를 위한 기본 동작이다. 터미널 작업, CI/CD, Claude Code 등 장시간 프로세스를 실행 중일 때 덮개를 닫아도 작업을 유지하려면 시스템 레벨 설정이 필요하다.

### 2. 슬립 방지 방법 비교

| 방법                       | 화면 꺼짐 방지 | 덮개 닫힘 슬립 방지 | 충전기 필요      | 비고                                        |
| -------------------------- | -------------- | -------------------- | ---------------- | ------------------------------------------- |
| **Caffeine 앱**            | O              | X                    | -                | GUI 앱은 lid close 이벤트를 오버라이드 불가  |
| **`caffeinate` 명령어**    | O              | 불확실               | -                | macOS 버전에 따라 동작 상이                  |
| **`pmset disablesleep 1`** | -              | **O**                | O (`-c` 옵션)    | 시스템 레벨, 가장 확실한 방법                |
| **클램셸 모드**            | -              | O                    | O                | 외부 모니터 + 키보드 + 마우스 필수           |

### 3. pmset disablesleep 사용법

#### 3.1 슬립 비활성화 (덮개 닫아도 실행 유지)

```bash
sudo pmset -c disablesleep 1
```

- `-c`: 충전(charger) 상태에서만 적용
- 충전기가 반드시 연결되어 있어야 동작

#### 3.2 슬립 다시 활성화 (원래대로 복원)

```bash
sudo pmset -c disablesleep 0
```

#### 3.3 현재 상태 확인

```bash
pmset -g
```

출력 예시:

```
 sleep          1 (sleep prevented by caffeinate, powerd)
 displaysleep   2 (display sleep prevented by Caffeine)
```

- `disablesleep` 항목이 출력에 **없으면**: 기본값(0), 슬립 활성화 상태
- `disablesleep 1`이 **있으면**: 슬립 비활성화 상태

#### 3.4 추가 확인 명령어

```bash
# 전원 프로파일별 전체 설정 확인
pmset -g custom

# 현재 슬립을 막고 있는 프로세스 확인
pmset -g assertions
```

### 4. pmset 주요 항목 레퍼런스

| 항목             | 기본값 | 설명                                          |
| ---------------- | ------ | --------------------------------------------- |
| `sleep`          | 1      | 시스템 슬립까지 대기 시간(분). 0 = 슬립 안 함 |
| `displaysleep`   | 2      | 디스플레이 꺼짐까지 대기 시간(분)             |
| `disksleep`      | 10     | 디스크 슬립까지 대기 시간(분)                 |
| `disablesleep`   | 0      | 1로 설정 시 덮개 닫힘 슬립 방지               |
| `standby`        | 1      | 슬립 후 딥 슬립(하이버네이트) 전환 여부       |
| `hibernatemode`  | 3      | 0: 슬립만, 3: RAM+디스크, 25: 디스크만        |
| `powernap`       | 1      | 슬립 중 백그라운드 업데이트 허용              |
| `ttyskeepawake`  | 1      | 터미널 세션 활성 시 슬립 방지                 |
| `womp`           | 0      | Wake on LAN                                   |
| `tcpkeepalive`   | 1      | 슬립 중 TCP 연결 유지                         |
| `lowpowermode`   | 0      | 저전력 모드                                   |

### 5. 옵션 플래그

| 플래그 | 적용 범위                       |
| ------ | ------------------------------- |
| `-a`   | 모든 전원 상태 (배터리 + 충전)  |
| `-b`   | 배터리 전원일 때만              |
| `-c`   | 충전기 연결 시에만              |

### 6. 주의사항

- **과열 위험**: 덮개를 닫으면 통풍이 제한된다. 장시간 사용 시 맥북 스탠드 등으로 공기 순환을 확보할 것
- **화면 잔상**: 키보드와 디스플레이가 밀착된 상태로 오래 두면 화면에 잔상이 남을 수 있음
- **충전기 필수**: `-c` 옵션은 충전기 연결 상태에서만 동작. 배터리 전원에서는 덮개 닫으면 무조건 슬립
- **작업 완료 후 복원**: `disablesleep 1` 상태를 방치하면 의도치 않은 배터리 소모와 과열이 발생할 수 있으므로 반드시 `disablesleep 0`으로 복원

### 7. 권장 워크플로우

```bash
# 1. 충전기 연결

# 2. 슬립 비활성화
sudo pmset -c disablesleep 1

# 3. 설정 확인
pmset -g | grep disablesleep

# 4. 장시간 작업 실행 (예: Claude Code)
claude

# 5. 덮개 닫기 → 작업 계속 진행됨

# 6. 작업 완료 후 복원
sudo pmset -c disablesleep 0
```
