# 기능 명세: 출고 처리

## 대상
- `CONFIRMED` 상태 주문만 출고 대상 목록에 표시된다.

## 동작
- 출고 실행 시 대상 주문 상태를 `RELEASE`로 전환한다.
- `CONFIRMED`가 아닌 주문(RESERVED/PRODUCING/REJECTED/RELEASE)에 출고를 시도하면 오류 처리한다
  (이미 출고된 주문의 중복 출고도 방지됨).
- 출고는 재고에 영향을 주지 않는다(재고 차감은 승인/생산 단계에서 이미 처리됨).

## 구현 위치
- `app/controllers/release_controller.py` (`ReleaseController`)
- `app/controllers/errors.py`: `InvalidOrderStateError` (ApprovalController와 공유)
- 관련 설계 문서: [`docs/design/phase7.md`](../design/phase7.md)
