# Phase 3 설계: 시료 주문(예약)

## 목표

고객이 원하는 시료 ID/고객명/수량을 입력받아 RESERVED 상태의 주문을 생성하는 기능을 구현한다.

## 아키텍처

```
app/controllers/order_controller.py   # 주문 예약/조회, 존재하지 않는 시료 검증
```

`OrderController`는 `SampleController`를 참조하여 주문 대상 시료가 실제로 존재하는지 확인한다
(시료 등록 여부는 SampleController의 책임 영역이므로 직접 Repository를 건드리지 않는다).

## 테스트 케이스

1. 존재하는 시료로 주문 시 RESERVED 상태, 자동 채번된 order_id로 생성되는지
2. 존재하지 않는 시료 ID로 주문 시 예외 발생하는지 (SampleNotFoundError)
3. 수량이 0 이하인 경우 예외 발생하는지 (InvalidQuantityError)
4. 여러 건 주문 시 order_id가 순차 채번되는지

## out of scope

- 주문 승인/거절 (Phase 4)
