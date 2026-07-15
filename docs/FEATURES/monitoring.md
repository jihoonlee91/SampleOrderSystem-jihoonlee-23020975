# 기능 명세: 모니터링

## 주문량 확인
- `RESERVED`/`CONFIRMED`/`PRODUCING`/`RELEASE` 상태별 주문 건수를 표시한다.
- `REJECTED`는 유효한 주문이 아니므로 집계에서 제외한다.

## 재고량 확인
- 등록된 모든 시료의 현재 재고와 상태를 표시한다.
- 재고 상태 판정 기준: 고갈(재고==0) / 부족(1~99) / 여유(100 이상)

## 구현 위치
- `app/controllers/monitoring_controller.py` (`MonitoringController`)
- 관련 설계 문서: [`docs/design/phase6.md`](../design/phase6.md)
