# Phase 4 설계: 주문 승인/거절

## 목표

RESERVED 주문 목록을 표시하고, 특정 주문을 승인(재고 비교 후 CONFIRMED/PRODUCING 분기 및 생산 큐 등록) 또는
거절(REJECTED)하는 기능을 구현한다.

## 아키텍처

```
app/repositories/production_queue_repository.py  # 생산 큐(FIFO) 저장소, 실제 생산 처리는 Phase 5
app/controllers/approval_controller.py           # 승인/거절 로직
```

## 승인 로직

1. 대상 주문의 시료 재고(`SampleController.get(sample_id)["stock"]`)와 주문 수량을 비교한다.
2. 재고가 주문 수량 이상이면: 재고를 즉시 차감하고 주문 상태를 CONFIRMED로 전환한다.
3. 재고가 주문 수량 미만이면: 생산 큐에 `{order_id, sample_id, shortage(부족분)}`를 등록하고
   주문 상태를 PRODUCING으로 전환한다. 이때 재고는 아직 차감하지 않는다(생산 완료 시 Phase 5에서 처리).
4. 거절 시: 주문 상태를 REJECTED로 전환한다. 재고/생산 큐에는 영향 없음.

## 경계값 처리

- 재고 == 주문 수량인 경우 "충분"으로 간주하여 CONFIRMED 처리 (요구사항: 재고 부족 시에만 생산).
- 이미 RESERVED가 아닌 주문(중복 승인/거절 시도)은 `InvalidOrderStateError`를 발생시킨다.

## 테스트 케이스

1. 재고 충분 → CONFIRMED 전환 및 재고 차감 확인
2. 재고 부족 → PRODUCING 전환, 생산 큐에 부족분 등록 확인, 재고는 아직 차감되지 않음
3. 재고 == 주문 수량 (경계값) → CONFIRMED 처리 확인
4. 거절 시 REJECTED 전환, 재고 불변 확인
5. RESERVED가 아닌 주문 승인/거절 시도 시 예외 발생

## out of scope

- 생산 큐 실제 처리(생산 진행, PRODUCING→CONFIRMED 완료 전환)는 Phase 5에서 다룬다.
