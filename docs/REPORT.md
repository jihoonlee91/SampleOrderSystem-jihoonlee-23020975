# AI 작업 보고서

## Phase 1: 프로젝트 스캐폴드 + 데이터 영속성 계층

### 요청 받은 작업
docs/PLAN.md의 Phase 1 항목 구현: Sample/Order 모델과 JSON 기반 Repository 계층 구축, pytest로 CRUD/영속성 검증.

### 해석
PoC(DataPersistence-jihoonlee-23020975)의 JsonStore 설계를 계승하되, 도메인에 맞는 `adjust_stock`(재고 증감),
`search_by_name`(시료 검색), `find_by_status`(주문 상태 필터), 자동 채번(`_next_order_id`)을 Repository에 추가.

### 변경 요약
- `app/models/sample.py`, `app/models/order.py`: 순수 데이터 모델
- `app/repositories/json_store.py`: 범용 JSON CRUD 저장소
- `app/repositories/sample_repository.py`, `order_repository.py`: 도메인 전용 Repository
- `tests/`: Repository 및 영속성에 대한 9개 pytest 테스트

### TDD 사이클 기록
- RED: 모듈 부재로 3개 테스트 파일 collection error 확인
- GREEN: 모델/Repository 구현 후 9개 테스트 전부 PASS
- REVIEW: 계층 간 책임 분리(Model=데이터, Repository=CRUD) 확인, 리팩토링 필요사항 없음

### 요청사항 충족 여부 체크리스트
- [x] Sample/Order 모델 정의
- [x] JSON 기반 CRUD 저장소 구현
- [x] 프로세스 재시작(신규 Repository 인스턴스) 후 데이터 유지 검증
- [x] pytest 전체 PASS (9/9)

### 변경된 파일 목록
- `app/__init__.py`, `app/models/__init__.py`, `app/repositories/__init__.py` (신규)
- `app/models/sample.py`, `app/models/order.py` (신규)
- `app/repositories/json_store.py`, `sample_repository.py`, `order_repository.py` (신규)
- `tests/__init__.py`, `test_sample_repository.py`, `test_order_repository.py`, `test_persistence.py` (신규)
- `.gitignore` (신규)

## Phase 2: 메인 메뉴 + 시료 관리

### 요청 받은 작업
docs/PLAN.md의 Phase 2 항목 구현: 콘솔 메인 메뉴 뼈대, 시료 등록/조회/검색 기능.

### 해석
콘솔 입출력 자체는 자동 테스트 가치가 낮다고 판단하여, `SampleController`를 View에 의존하지 않는 순수
파라미터 기반 메서드로 설계해 pytest로 검증하고, 실제 입출력 흐름(View/MainController)은 사람이 직접
콘솔에서 실행하여 확인하는 방식(E2E 수동 검증)으로 역할을 분리함.

### 변경 요약
- `app/controllers/sample_controller.py`: 등록(중복 방지 포함)/조회/검색
- `app/views/console_view.py`: 메뉴 표시, 입력 프롬프트, 시료 목록 출력 (로직 없음)
- `app/controllers/main_controller.py`: 메인 메뉴 루프 + 시료 관리 서브메뉴
- `main.py`: 진입점

### TDD 사이클 기록
- RED: `app.controllers` 모듈 부재로 collection error 확인
- GREEN: `SampleController` 구현 후 4개 테스트 PASS
- REVIEW: 콘솔로 등록→목록→검색 시나리오 직접 실행하여 정상 동작 확인, 전체 회귀 테스트 13/13 PASS

### 요청사항 충족 여부 체크리스트
- [x] 메인 메뉴 및 시료 관리 서브메뉴 구현
- [x] 시료 등록 (중복 ID 방지)
- [x] 시료 목록 조회 (재고 수량 포함)
- [x] 이름 키워드 검색
- [x] pytest 전체 PASS (13/13), 콘솔 실행 E2E 검증 완료

### 변경된 파일 목록
- `app/controllers/__init__.py`, `app/views/__init__.py` (신규)
- `app/controllers/sample_controller.py`, `main_controller.py` (신규)
- `app/views/console_view.py` (신규)
- `main.py` (신규)
- `tests/test_sample_controller.py` (신규)

## Phase 3: 시료 주문(예약)

### 요청 받은 작업
docs/PLAN.md의 Phase 3 항목 구현: 시료 ID/고객명/수량을 입력받아 RESERVED 상태 주문을 생성.

### 해석
주문 대상 시료의 존재 여부 검증은 `OrderController`가 `SampleController.get()`을 통해 확인하도록 하여,
Repository 계층을 직접 넘나들지 않고 Controller 간 협력으로 참조 무결성을 지키도록 설계함.

### 변경 요약
- `app/controllers/order_controller.py`: 주문 예약(존재하지 않는 시료/수량 0 이하 검증 포함), 목록 조회
- `app/views/console_view.py`: `show_orders` 추가
- `app/controllers/main_controller.py`: 메인 메뉴에 "2. 시료 주문" 연결

### TDD 사이클 기록
- RED: `order_controller` 모듈 부재로 collection error 확인
- GREEN: `OrderController` 구현 후 4개 테스트 PASS
- REVIEW: 콘솔에서 정상 주문/존재하지 않는 시료 주문 시나리오 실행 확인, 전체 회귀 테스트 17/17 PASS

### 요청사항 충족 여부 체크리스트
- [x] 시료 ID/고객명/수량 입력받아 주문 생성
- [x] 생성 시점 상태 RESERVED
- [x] 존재하지 않는 시료 주문 시 명확한 오류 처리
- [x] pytest 전체 PASS (17/17), 콘솔 실행 E2E 검증 완료

### 변경된 파일 목록
- `app/controllers/order_controller.py` (신규)
- `app/views/console_view.py`, `app/controllers/main_controller.py` (수정)
- `tests/test_order_controller.py` (신규)

## Phase 4: 주문 승인/거절

### 요청 받은 작업
docs/PLAN.md의 Phase 4 항목 구현: RESERVED 주문 목록 표시, 승인 시 재고 비교 기반 CONFIRMED/PRODUCING 분기 및
생산 큐 등록, 거절 시 REJECTED 전환.

### 해석
"재고가 충분하면 즉시 CONFIRMED, 부족하면 생산 라인 등록 후 PRODUCING"이라는 PRD 요구사항을 그대로 구현하되,
경계값(재고 == 주문 수량)은 "충분"으로 해석함(PRD상 "재고 부족 시에만 생산"이므로 동일한 경우는 충분으로 처리).
재고 부족 시에는 실제 생산이 완료되기 전이므로 재고를 미리 차감하지 않고, 생산 큐에 부족분만 등록함(Phase 5에서
생산 완료 처리 시 재고 반영 예정).

### 변경 요약
- `app/repositories/production_queue_repository.py`: 생산 큐 FIFO 저장소(enqueue/find_all/dequeue_front)
- `app/controllers/approval_controller.py`: 승인/거절 로직, RESERVED 상태 검증
- `app/views/console_view.py`: 승인/거절 서브메뉴 표시 추가
- `app/controllers/main_controller.py`: "3. 주문 승인/거절" 메뉴 연결

### TDD 사이클 기록
- RED: `approval_controller` 모듈 부재로 collection error 확인
- GREEN: `ApprovalController`, `ProductionQueueRepository` 구현 후 5개 테스트 PASS
- REVIEW: Verify Harness(`scripts/verify.py`) 실행 - Test Verify 22/22 PASS, Compliance Verify 체크리스트로
  설계 문서 범위 준수 확인. 콘솔에서 재고 충분/부족 두 시나리오 모두 실행하여 CONFIRMED/PRODUCING 분기 확인.

### 요청사항 충족 여부 체크리스트
- [x] RESERVED 주문 목록 표시
- [x] 재고 충분 시 즉시 CONFIRMED 전환 및 재고 차감
- [x] 재고 부족 시 생산 큐 등록 및 PRODUCING 전환
- [x] 거절 시 REJECTED 전환
- [x] Verify Harness(pytest 22/22 + Compliance 체크) 통과, 콘솔 E2E 검증 완료

### 변경된 파일 목록
- `app/repositories/production_queue_repository.py` (신규)
- `app/controllers/approval_controller.py` (신규)
- `app/views/console_view.py`, `app/controllers/main_controller.py` (수정)
- `tests/test_approval_controller.py` (신규)

## Phase 5: 생산 라인

### 요청 받은 작업
docs/PLAN.md의 Phase 5 항목 구현: 생산 큐 FIFO 처리, 실 생산량/생산 시간 계산, 생산 완료 시
PRODUCING→CONFIRMED 전환 및 재고 반영, 생산 현황/대기열 조회.

### 해석
큐 항목에 "부족분(shortage)"뿐 아니라 "주문 수량(quantity)"도 함께 저장하도록 Phase 4의
`ProductionQueueRepository.enqueue` 시그니처를 확장함(작업 중 발견 — 최초 설계에는 shortage만 저장했으나,
생산 완료 후 최종 재고 = 기존재고 + 실생산량 - 주문수량으로 계산해야 정확함을 테스트 작성 중 확인하여 즉시 반영).

### 변경 요약
- `app/repositories/production_queue_repository.py`: `enqueue`에 `quantity` 파라미터 추가 (Phase 4 코드 수정)
- `app/controllers/approval_controller.py`: enqueue 호출 시 quantity 함께 전달 (Phase 4 코드 수정)
- `app/controllers/production_controller.py`: FIFO 처리, 실생산량(ceil)/생산시간 계산, 재고 반영, CONFIRMED 전환
- `app/views/console_view.py`, `main_controller.py`: 생산 라인 메뉴("5") 연결

### TDD 사이클 기록
- RED: `production_controller` 모듈 부재로 collection error 확인
- GREEN: 최초 구현 시 재고 계산식이 실제 요구와 달라 테스트 기대값과 불일치 발견 → 계산식을
  `actual_quantity - shortage`에서 `actual_quantity - quantity`(전체 주문 수량 기준)로 수정하여 통과시킴
- REVIEW: Verify Harness 실행 - Test Verify 26/26 PASS. 콘솔 실행으로 재고 30 → 생산 후 15로
  정확히 반영되는 것을 실측 확인 (30 + ceil(170/0.92) - 200 = 15)

### 요청사항 충족 여부 체크리스트
- [x] 실 생산량 = ceil(부족분 / 수율) 계산
- [x] 총 생산 시간 = 평균 생산시간 * 실 생산량 계산
- [x] 생산 완료 시 PRODUCING → CONFIRMED 전환 및 재고 반영
- [x] FIFO 순서로 대기열 처리
- [x] 대기열 조회 기능
- [x] Verify Harness(pytest 26/26 + Compliance 체크) 통과, 콘솔 E2E 검증 완료

### 변경된 파일 목록
- `app/controllers/production_controller.py` (신규)
- `app/repositories/production_queue_repository.py`, `app/controllers/approval_controller.py` (수정)
- `app/views/console_view.py`, `app/controllers/main_controller.py` (수정)
- `tests/test_production_controller.py` (신규)

## Phase 6: 모니터링

### 요청 받은 작업
docs/PLAN.md의 Phase 6 항목 구현: 상태별 주문 수(REJECTED 제외) 및 시료별 재고 상태(여유/부족/고갈) 조회.

### 해석
재고 상태 임계값(여유≥100, 부족 1~99, 고갈 0)은 PoC `DataMonitor-jihoonlee-23020975`에서 사용한 기준을
그대로 계승함. PRD에는 구체적 수치가 명시되어 있지 않아 PoC 단계에서 검증된 기준을 재사용하는 것이
일관성 있다고 판단함.

### 변경 요약
- `app/controllers/monitoring_controller.py`: 상태별 주문 집계(REJECTED 제외), 재고 상태 분류
- `app/views/console_view.py`, `main_controller.py`: 모니터링 메뉴("4") 연결

### TDD 사이클 기록
- RED: `monitoring_controller` 모듈 부재로 collection error 확인
- GREEN: 구현 후 3개 테스트 PASS
- REVIEW: Verify Harness 실행 - Test Verify 29/29 PASS. 콘솔에서 주문량/재고량 조회 화면 직접 확인.
  사용자 검토 결과 재고 임계값/집계 방식 수정 없이 그대로 승인됨.

### 요청사항 충족 여부 체크리스트
- [x] 상태별 주문 수 조회 (REJECTED 제외)
- [x] 시료별 재고 상태(여유/부족/고갈) 조회
- [x] Verify Harness(pytest 29/29 + Compliance 체크) 통과, 콘솔 E2E 검증 완료, 사용자 승인 완료

### 변경된 파일 목록
- `app/controllers/monitoring_controller.py` (신규)
- `app/views/console_view.py`, `app/controllers/main_controller.py` (수정)
- `tests/test_monitoring_controller.py` (신규)
