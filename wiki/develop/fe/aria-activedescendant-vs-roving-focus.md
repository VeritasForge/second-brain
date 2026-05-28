---
tags: [accessibility, aria, keyboard-navigation, focus-management]
created: 2026-05-28
---

## 1. `aria-activedescendant` — 진짜 HTML 표준 속성

### 정의

WAI-ARIA (Web Accessibility Initiative - Accessible Rich Internet Applications) 명세에 정의된 **공식 HTML 어트리뷰트**입니다. React 용어가 아니라 브라우저/스크린리더가 직접 읽는 표준입니다.

### 🎯 핵심 개념: "나는 여기 있는데, 활성 항목은 저기야"

```
[input 요소] ← DOM focus 실제로 여기 있음
    |
    | aria-activedescendant="item-2"  ← 브라우저/스크린리더에게 알려줌
    ↓
[dropdown]
  [item-1] id="item-1"
  [item-2] id="item-2"  ← "활성" 항목 (시각적 하이라이트만)
  [item-3] id="item-3"
```

### 실제 HTML 예시

```html
<input
  role="combobox"
  aria-activedescendant="item-2"
  aria-expanded="true"
/>

<ul role="listbox">
  <li id="item-1" role="option">삼성전자</li>
  <li id="item-2" role="option" aria-selected="true">애플</li>
  <li id="item-3" role="option">구글</li>
</ul>
```

스크린리더는 `aria-activedescendant`를 보고 "현재 활성 항목은 '애플'입니다"라고 읽어줍니다.

---

### `activeIndex`는 뭔가요?

이건 React 용어가 **아니고**, 어디에도 표준으로 정의된 건 없습니다. 단순히 개발자들이 관용적으로 쓰는 **상태 변수 이름**입니다.

```tsx
const [activeIndex, setActiveIndex] = useState(-1);

// 방향키 누를 때마다 숫자가 바뀜: -1 → 0 → 1 → 2 ...
// 이 숫자로 어떤 항목을 하이라이트할지 결정
```

> 🏠 비유: **TV 리모컨의 채널 번호**같은 거예요. 채널 번호(activeIndex)는 머릿속(state)에서만 바뀌고, TV 화면(dropdown)에는 해당 채널만 강조돼서 보이는 거죠. TV 리모컨 자체가 TV로 이동하진 않아요.

---

## 2. Roving Focus (= Roving Tabindex) — 접근성 전문가들이 쓰는 진짜 용어

### 정의

[WAI-ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/#kbd_roving_tabindex)에 공식 명시된 **키보드 네비게이션 패턴**입니다. "Roving tabindex"라고도 부릅니다.

### 🔑 핵심: tabindex가 "떠돌아다닌다(roving)"

`tabindex` 속성이 현재 활성 항목에만 `0`으로 설정되고, 나머지는 `-1`로 바뀌면서 **실제 DOM focus가 항목들 사이를 이동**하는 패턴입니다.

```
[방향키 ↓ 누르기 전]                [방향키 ↓ 누른 후]

input [tabindex=0, focused]          input [tabindex=-1]
  ↓                                    ↓
dropdown:                            dropdown:
  item-1 [tabindex=-1]                 item-1 [tabindex=0, focused] ← focus 이동!
  item-2 [tabindex=-1]                 item-2 [tabindex=-1]
  item-3 [tabindex=-1]                 item-3 [tabindex=-1]
```

### 두 방식 비교표

| 구분                 | aria-activedescendant           | Roving Focus                      |
| -------------------- | ------------------------------- | --------------------------------- |
| **DOM focus 위치**   | 항상 input에 고정               | 실제로 항목으로 이동              |
| **시각 하이라이트** | activeIndex로 CSS만 변경        | `:focus` CSS pseudo-class 활용 가능 |
| **스크린리더**       | aria-activedescendant 속성으로 알림 | 실제 focus 이동으로 자연스럽게 읽음 |
| **구현 복잡도**      | 낮음                            | 높음 (tabindex 동적 관리 필요)    |
| **사용자 체감**      | 커서가 input에 남아있음         | 커서가 실제로 항목으로 감         |

### 🏠 비유

- **aria-activedescendant** = 집에 가만히 앉아서 "저 식당 2번 메뉴 주세요"라고 전화하는 것. 몸(focus)은 집에 있고, 식당(dropdown)에는 번호(aria-activedescendant)만 전달됨.
- **Roving Focus** = 직접 식당에 가서(focus 이동) 메뉴판 앞에 서서 손가락으로 짚는 것. 몸이 실제로 이동함.

### Roving Focus 구현 원리 (코드 스케치)

```tsx
function handleKeyDown(e: KeyboardEvent) {
  if (e.key === 'ArrowDown') {
    const nextIndex = currentIndex + 1;

    // 핵심: 실제 DOM 요소에 focus() 호출
    itemRefs[nextIndex].current?.focus();

    // tabindex도 함께 이동 (roving)
    itemRefs[currentIndex].current?.setAttribute('tabindex', '-1');
    itemRefs[nextIndex].current?.setAttribute('tabindex', '0');
  }
}
```

---

## 정리

```
사용자가 원하는 것:
  "방향키 → dropdown 항목으로 focus 이동"
      ↓
  = Roving Focus 방식

현재 구현:
  "방향키 → input focus 유지 + 시각 하이라이트만 변경"
      ↓
  = aria-activedescendant 방식
```

두 방식 모두 접근성 관점에서 유효하지만, 사용자가 원하는 "직접 이동하는 느낌"은 Roving Focus가 더 자연스럽습니다. 다만 구현 시 `itemRefs` 배열 관리, focus trap (dropdown 벗어날 때 input으로 복귀), `Escape` 키 처리 등을 추가로 고려해야 합니다.
