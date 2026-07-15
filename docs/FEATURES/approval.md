# 기능 명세: 주문 승인/거절

## 대상
- `RESERVED` 상태의 주문만 승인/거절 대상이 된다. 그 외 상태의 주문에 승인/거절을 시도하면 오류 처리한다.

## 승인
1. 대상 주문의 시료 재고와 주문 수량을 비교한다.
2. 재고가 주문 수량 이상(경계값 포함, `재고 >= 수량`)이면: 재고에서 주문 수량만큼 즉시 차감하고
   주문 상태를 `CONFIRMED`로 전환한다.
3. 재고가 주문 수량 미만이면: 부족분(`수량 - 재고`)과 주문 수량을 생산 큐에 등록하고
   주문 상태를 `PRODUCING`으로 전환한다. 이 시점에는 재고를 차감하지 않는다.

## 거절
- 주문 상태를 `REJECTED`로 전환한다. 재고/생산 큐에는 영향을 주지 않는다.

## 구현 위치
- `app/controllers/approval_controller.py` (`ApprovalController`)
- `app/repositories/production_queue_repository.py`
- 관련 설계 문서: [`docs/design/phase4.md`](../design/phase4.md)
