# 기능 명세: 시료 주문(예약)

## 입력
- 시료 ID, 고객명, 주문 수량(정수)

## 검증 규칙
- 존재하지 않는 시료 ID로 주문 시 오류 처리(주문 생성 거부)
- 주문 수량이 0 이하이면 오류 처리(주문 생성 거부)

## 동작
- 위 검증을 통과하면 주문번호(`ORD-0001` 형식, 기존 최대 번호 다음 순번 자동 채번)를 부여하여
  상태 `RESERVED`로 주문을 생성한다.

## 구현 위치
- `app/controllers/order_controller.py` (`OrderController`)
- `app/repositories/order_repository.py`
- 관련 설계 문서: [`docs/design/phase3.md`](../design/phase3.md)
