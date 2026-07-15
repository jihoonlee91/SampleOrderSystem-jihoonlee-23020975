# Phase 1 설계: 프로젝트 스캐폴드 + 데이터 영속성 계층

## 목표

애플리케이션의 데이터 기반이 되는 Sample/Order 모델과 JSON 기반 영속성 계층을 구축한다.
아직 콘솔 UI는 없으며, pytest로 Repository 레이어를 직접 검증한다.

## 아키텍처

```
app/
  models/
    sample.py      # Sample dataclass
    order.py       # Order dataclass, OrderStatus enum
  repositories/
    json_store.py       # 범용 JSON CRUD 저장소 (PoC DataPersistence 계승)
    sample_repository.py
    order_repository.py
data/
  samples.json     # 최초 실행 시 자동 생성
  orders.json
tests/
  test_sample_repository.py
  test_order_repository.py
  test_persistence.py   # 프로세스 재시작 후 데이터 유지 검증
```

## 도메인 모델

- `Sample`: sample_id, name, avg_process_time(float), yield_rate(float), stock(int)
- `Order`: order_id, sample_id, customer, quantity(int), status(OrderStatus)
- `OrderStatus`: RESERVED, REJECTED, PRODUCING, CONFIRMED, RELEASE

## Repository 책임

- `SampleRepository`: create/read_all/read/update/delete, `stock` 증감 편의 메서드(`adjust_stock`) 제공
- `OrderRepository`: create(자동 채번)/read_all/read/update_status, 상태 필터 조회(`find_by_status`) 제공

## 테스트 케이스 (RED 우선 작성 대상)

1. `test_gutter...` 류가 아니라 도메인에 맞춰: 시료 생성 후 재조회 시 동일 데이터 반환
2. 재고 조정(adjust_stock) 후 값 반영 확인
3. 주문 생성 시 상태가 RESERVED로 초기화되고 order_id가 자동 채번되는지
4. 상태 필터 조회(find_by_status)가 정확한 주문만 반환하는지
5. 별도 프로세스(재실행)로 데이터가 유지되는지 (파일 기반이므로 새 Repository 인스턴스 생성 후 조회로 대체 검증)

## out of scope

- 콘솔 메뉴/입출력 (Phase 2 이후)
- 주문 상태 전이 로직(승인/거절/생산/출고) — 이번 Phase는 저장소 CRUD만 다룸
