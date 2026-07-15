# Phase 6 설계: 모니터링

## 목표

상태별 주문 수(REJECTED 제외)와 시료별 재고 상태(여유/부족/고갈)를 조회하는 기능을 구현한다.

## 아키텍처

```
app/controllers/monitoring_controller.py
```

## 규칙

- 주문량 확인: RESERVED/CONFIRMED/PRODUCING/RELEASE 건수를 집계. REJECTED는 집계에서 제외한다.
- 재고량 확인: 시료별 현재 재고를 표시하고, 상태를 다음 기준으로 판정한다(PoC DataMonitor 기준 계승).
  - 고갈: 재고 == 0
  - 부족: 0 < 재고 < 100
  - 여유: 재고 >= 100

## 테스트 케이스

1. RESERVED 2건, CONFIRMED 1건, REJECTED 3건이 있을 때 REJECTED는 집계에서 제외되고 나머지는 정확히 카운트되는지
2. 재고 0 → "고갈", 1~99 → "부족", 100 이상 → "여유"로 판정되는지
3. 시료가 하나도 없을 때 빈 목록 반환

## out of scope

- 상세 임계값 설정 UI (하드코딩된 기준값 사용)
