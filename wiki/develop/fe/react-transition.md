---
tags: [react, transition, useTransition]
created: 2026-05-22
---

# React Transition

**React.js** 용어 (React 18에서 도입). Next.js는 React 위에 올라타므로 둘 다에서 사용 가능.

## Transition이란?

### 🏪 12살도 이해하는 비유

편의점 계산대를 생각해보세요.

```
일반 계산대 (기존 방식):
  손님 A가 계산 중 → 다른 손님 전부 대기 → 완료 후 다음 손님

VIP + 일반 이중 계산대 (Transition 방식):
  긴급 손님(VIP) → 즉시 처리
  일반 손님       → 여유 있을 때 처리 (뒤로 밀림)
```

### 코드로 보면

```
React의 상태 업데이트에는 2가지 우선순위가 있음:

긴급(Urgent):   사용자 입력, 클릭, 타이핑
                → 즉시 반영해야 UX가 자연스러움

비긴급(Transition): 검색 결과 목록, 폴링 데이터 업데이트
                    → 약간 늦어도 괜찮음
```

### 실제 동작 차이

```
❌ startTransition 없음 (기존):

  t=0    폴링 발화 → setAccounts(newData)
  t=0    React: "accounts 바뀜! 전부 리렌더 시작!"
  t=0    사용자가 버튼을 눌러도 → 리렌더 완료까지 응답 없음 😤

✅ startTransition 있음:

  t=0    폴링 발화 → startTransition(() => setAccounts(newData))
  t=0    React: "이건 비긴급이야. 긴급한 거 먼저 처리할게."
  t=0    사용자 버튼 클릭 → 즉시 반응 😊
  t=0.X  여유 생기면 accounts 업데이트
```

---

## API

```typescript
// 1. useTransition 훅 (isPending 상태도 제공)
const [isPending, startTransition] = useTransition();

startTransition(() => {
  setAccounts(newData);  // 낮은 우선순위로 처리
});

// isPending: transition 처리 중이면 true
// → 버튼에 미묘한 로딩 표시 등에 활용 가능

// 2. startTransition 함수 (isPending 불필요할 때)
import { startTransition } from 'react';
startTransition(() => setAccounts(newData));
```

---

## 폴링 데이터 업데이트 적용 예시

```typescript
// useAccounts.ts — 폴링 시 setAccounts를 transition으로 감싸기
import { useState, useCallback, useTransition } from 'react';

export function useAccounts(isGuest: boolean) {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [, startTransition] = useTransition();

  const fetchAccounts = useCallback(async () => {
    try {
      if (isGuest) {
        startTransition(() => setAccounts([guestAccount]));
      } else {
        const res = await fetchWithAuth(url);
        if (res.ok) {
          const data = await res.json();
          startTransition(() => setAccounts(data));  // ← 비긴급 처리
        }
      }
    } finally {
      setIsLoading(false);
    }
  }, [isGuest, storeAssets, storeCash]);
}
```

---

## 효과 비교

| 상황                  | 기존                      | startTransition 적용 시       |
| --------------------- | ------------------------- | ----------------------------- |
| 폴링 데이터 도착      | 즉시 전체 리렌더          | 여유 있을 때 리렌더           |
| 리렌더 중 사용자 입력 | 응답 지연 가능            | 즉시 반응                     |
| 체감 깜빡임           | 강함 (배열 통째 교체)     | 약함 (React가 조율)           |
| 에러 처리             | 수동 setIsLoading(false)  | isPending 자동 리셋           |

---

## 주의사항

- React 18에서 `startTransition` 콜백에 **async 직접 사용 불가** (React 19부터 가능)
- 데이터 fetch는 바깥에서 await → 결과를 `startTransition` 안에서 setState
- `isPending`이 필요 없으면 `useTransition` 대신 `import { startTransition } from 'react'` 사용

---

## 참고

- [React 공식 문서: useTransition](https://react.dev/reference/react/useTransition)
- Vercel 베스트 프랙티스 규칙: `rendering-usetransition-loading`, `rerender-transitions`
