# Phase 7 설계: 출고 처리 (사용자 승인 완료)

## 목표

`CONFIRMED` 상태 주문 목록을 표시하고, 특정 주문에 대해 출고를 실행하여 `RELEASE`로 전환한다.

## 아키텍처

```
app/controllers/release_controller.py
```

## 동작 규칙

- `list_confirmed()`: `CONFIRMED` 상태 주문만 반환 (RESERVED/PRODUCING/REJECTED/RELEASE는 노출하지 않음)
- `release(order_id)`:
  - 대상 주문이 `CONFIRMED` 상태가 아니면 `InvalidOrderStateError` 발생(승인/거절과 동일한 예외 패턴 재사용 여부는
    검토 필요 - 아래 [검토 필요 사항] 참고)
  - 정상 조건이면 상태를 `RELEASE`로 전환
- 출고는 재고에 영향을 주지 않는다(재고 차감은 Phase 4/5에서 이미 처리됨. 출고는 상태 전환만 수행).

## 테스트 케이스 (예정)

1. CONFIRMED 주문만 `list_confirmed()`에 노출되는지 (RESERVED/PRODUCING 주문은 제외)
2. CONFIRMED 주문 출고 시 RELEASE로 전환되는지
3. CONFIRMED가 아닌 주문(RESERVED, PRODUCING, REJECTED, RELEASE) 출고 시도 시 예외 발생하는지
4. 이미 RELEASE된 주문을 재출고 시도 시 예외 발생하는지 (중복 출고 방지)

## 결정 사항 (사용자 승인 완료)

1. **예외 클래스 공통화**: `InvalidOrderStateError`를 `app/controllers/errors.py`로 분리한다.
   `ApprovalController`와 `ReleaseController`가 모두 이 모듈을 참조하도록 리팩토링한다
   (Approval 쪽 기존 코드도 함께 수정, 회귀 테스트로 기존 동작 불변 확인).
2. **메뉴 번호**: 메인 메뉴 "6. 출고 처리"를 그대로 사용한다.

## out of scope

- 출고 이후 배송/물류 처리 (본 프로젝트 범위 밖)
