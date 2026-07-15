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

## Phase 7: 출고 처리

### 요청 받은 작업
docs/PLAN.md의 Phase 7 항목 구현: CONFIRMED 주문 목록 표시 및 출고 실행(RELEASE 전환).

### 사람 검토 사항 (설계 단계에서 확인받음)
설계 문서(docs/design/phase7.md) 작성 시 2가지를 사전에 질의하여 승인받음:
1. `InvalidOrderStateError`를 `app/controllers/errors.py` 공통 모듈로 분리 (승인됨, 별도 리팩토링 커밋으로 선행 처리)
2. 출고 메뉴 번호는 기존 "6번" 유지 (승인됨)

### 변경 요약
- `app/controllers/errors.py`: `InvalidOrderStateError` 공통 모듈 (선행 리팩토링 커밋)
- `app/controllers/approval_controller.py`: 공통 예외 모듈 참조로 수정 (선행 리팩토링 커밋)
- `app/controllers/release_controller.py`: CONFIRMED 조회/출고 실행
- `app/views/console_view.py`, `main_controller.py`: "6. 출고 처리" 메뉴 연결

### TDD 사이클 기록
- (선행) 리팩토링: errors.py 분리 후 회귀 테스트 29/29 PASS 확인, 별도 커밋
- RED: `release_controller` 모듈 부재로 collection error 확인
- GREEN: `ReleaseController` 구현 후 4개 테스트 PASS
- REVIEW: Verify Harness 실행 - Test Verify 33/33 PASS. 콘솔에서 승인→출고 흐름 E2E 검증 완료.

### 요청사항 충족 여부 체크리스트
- [x] CONFIRMED 주문만 출고 대상 목록에 노출
- [x] 출고 실행 시 RELEASE로 전환
- [x] CONFIRMED가 아닌 주문(중복 출고 포함) 출고 시도 시 오류 처리
- [x] Verify Harness(pytest 33/33 + Compliance 체크) 통과, 콘솔 E2E 검증 완료
- [x] 설계 문서 사전 승인 절차 준수(errors.py 분리, 메뉴 번호 확정)

### 변경된 파일 목록
- `app/controllers/errors.py` (신규)
- `app/controllers/approval_controller.py` (수정 - import 경로 변경)
- `app/controllers/release_controller.py` (신규)
- `app/views/console_view.py`, `app/controllers/main_controller.py` (수정)
- `tests/test_release_controller.py` (신규)

## Phase 8: 통합 마감

### 요청 받은 작업
docs/PLAN.md의 Phase 8 항목 구현: 전체 메뉴 연결 점검, 회귀 테스트 전체 재실행, README 정리,
더미 데이터 시나리오로 E2E 수동 검증.

### 점검 결과
1. **회귀 테스트**: pytest 33/33 PASS
2. **전체 생애주기 E2E**: 시료 등록(2건) → 주문(3건) → 승인(재고충분 1건→CONFIRMED, 재고부족
   1건→PRODUCING) + 거절(1건→REJECTED) → 모니터링(REJECTED 제외 집계 확인) → 생산 처리
   (실생산량/시간 계산 확인) → 출고(RELEASE 전환) → 모니터링 재확인(RELEASE 건수 갱신 확인)까지
   전 과정을 콘솔에서 직접 실행하여 검증
3. **Clean Code 점검**:
   - Model(순수 데이터)/Repository(CRUD)/Controller(도메인 규칙)/View(입출력) 계층 분리 규칙 위반 없음
   - `InvalidOrderStateError`가 `app/controllers/errors.py`에 단일 정의되어 3곳에서 일관되게 참조됨
   - grep으로 미사용 코드/import 없음을 확인
   - View의 `show_*` 메서드들은 각각 다른 데이터 구조를 출력하므로 무리한 공통 추상화를 하지 않음(Rule of Three 미해당)
4. **문서 정합성**: PRD.md ↔ FEATURES/*.md ↔ design/phaseN.md ↔ REPORT.md ↔ 실제 코드 간 기능 목록 일치 확인
5. **README.md**: 실행 방법/기능 목록/예시 UI 화면/프로젝트 구조/문서 링크/개발 프로세스를 최신 상태로 갱신 완료

### 요청사항 충족 여부 체크리스트
- [x] 전체 메뉴(1~6번) 연결 및 동작 확인
- [x] 전체 회귀 테스트 PASS (33/33)
- [x] README 최종 정리
- [x] 더미 시나리오 기반 E2E 수동 검증 완료
- [x] Clean Code 점검 완료 (계층 분리, 예외 공통화, 미사용 코드 없음)

### 변경된 파일 목록
- `docs/PLAN.md`, `docs/REPORT.md` (수정, Phase 8 반영)

## 추가 보강: Safety(공격적) 테스트

### 배경
사용자 요청으로 정상 시나리오가 아닌 공격적 입력값 테스트를 진행함. 강의자료(Day2-1)의
"AI로 Correctness를 넘어서 안전성 테스트(Safety Testing) 진행" 원칙에 따라, 실제 스크립트로
직접 공격을 시도한 뒤 발견된 문제를 사용자 승인을 받아 수정함.

### 발견한 문제 (수동 공격 스크립트로 확인)
1. **[심각] `yield_rate=0`으로 시료 등록 시, 생산 처리 단계(`ProductionController.process_next`)에서
   `ceil(shortage / yield_rate)` 계산 중 `ZeroDivisionError`로 애플리케이션이 크래시됨.**
2. 음수 재고(stock=-100)로 등록이 허용됨 (데이터 무결성 위반)
3. 수율이 1을 초과(yield_rate=1.5)해도 등록이 허용됨
4. 평균 생산시간이 음수/0이어도 등록이 허용됨

### 사람 검토 및 결정
발견한 4가지 문제를 모두 보고하고, "전체 검증 추가" vs "ZeroDivisionError만 우선 차단" 중
선택을 요청 → **전체 검증 추가**로 결정됨.

### 변경 요약
- `app/controllers/sample_controller.py`: `InvalidSampleDataError` 추가, `register()`에
  `_validate()` 호출 추가 (수율 0<x<=1, 생산시간>0, 재고>=0)
- `app/controllers/main_controller.py`: `InvalidSampleDataError` 예외 처리 연결
- `tests/test_sample_safety.py`: 8개 안전성 테스트 추가 (경계값 정상 케이스 포함)

### TDD/Safety 사이클 기록
- 공격: 수동 스크립트로 4가지 위험 입력 실행 → ZeroDivisionError 크래시 및 무검증 등록 확인
- RED: `InvalidSampleDataError` 미정의로 collection error 확인
- GREEN: 검증 로직 추가 후 8개 신규 테스트 + 기존 33개 테스트 합계 41/41 PASS
- REVIEW: 콘솔에서 동일 공격(수율 0) 재시도 → 크래시 없이 명확한 오류 메시지로 방어됨을 확인.
  Verify Harness(pytest 41/41 + Compliance 체크) 통과.

### 요청사항 충족 여부 체크리스트
- [x] 수율 0으로 인한 ZeroDivisionError 완전 차단
- [x] 음수 재고/수율 범위 초과/음수 생산시간 등록 차단
- [x] 경계값(수율=1, 재고=0)은 정상 등록 허용 (과도한 제약 없음)
- [x] 콘솔 E2E로 실제 크래시 재현 불가 확인

### 변경된 파일 목록
- `app/controllers/sample_controller.py`, `app/controllers/main_controller.py` (수정)
- `tests/test_sample_safety.py` (신규)
- `docs/FEATURES/sample_management.md` (수정)

## 추가 보강: 동시 승인 재고 이중 계산 버그 수정

### 배경
사용자 요청으로 "더 깊게" 코드를 추론하며 점검하던 중, 같은 시료에 대해 재고 부족 주문이
2건 이상 대기할 때의 시나리오를 수동 스크립트로 시뮬레이션하여 발견함.

### 발견한 문제
같은 시료에 재고 부족 주문 A(200개), B(100개)가 순서대로 승인되면(재고 30):
- 두 승인 모두 "재고 부족 시 재고 미차감"이라는 기존 설계 때문에 **둘 다 동일한 기존재고(30)를
  기준으로 독립적으로 부족분을 계산**(A: 170, B: 70)
- 실제로는 재고 30을 어느 한 주문만 가져갈 수 있는데, 두 주문 모두 이 30을 "내 몫"으로 계산에
  포함시켜 총 생산량이 실제 필요량보다 30 적게 계산됨
- 생산 완료 후 재고가 **-8**로 음수가 되는 실제 버그 확인(재현 스크립트로 검증)

### 사람 검토 및 결정
문제와 원인, 해결 방안("승인 시점에 기존 재고를 즉시 0으로 소진 처리")을 보고하고 승인받음.

### 변경 요약
- `app/controllers/approval_controller.py`: 재고 부족 분기에서 기존 재고 전량을 즉시 소진(0으로 차감)
- `app/controllers/production_controller.py`: 재고 반영식을 `실생산량 - 주문수량`에서
  `실생산량 - 부족분`으로 변경 (승인 시 이미 재고가 소진되었으므로 부족분만 채우면 됨)
- `tests/test_production_concurrency.py`: 동시 주문 재현 테스트 2건 추가
- `tests/test_approval_controller.py`: 재고 부족 시 최종 재고 기대값을 30→0으로 수정
  (설계 변경에 따른 정상적인 테스트 갱신)

### TDD/버그 수정 사이클 기록
- 원인 분석: 수동 스크립트로 -8 재현 확인
- RED: `test_production_concurrency.py` 작성, -8 vs 24 기대값 불일치로 실패 확인
- GREEN: 승인/생산 로직 수정 후 43/43 PASS (기존 단일 주문 테스트는 수식 동치로 무수정 통과,
  Phase4의 재고 미차감 검증 테스트만 새 설계에 맞게 갱신)
- REVIEW: 콘솔에서 동일 동시 주문 시나리오 재현 → 재고 24로 정상 확인(음수 없음).
  Verify Harness(pytest 43/43 + Compliance 체크) 통과.

### 요청사항 충족 여부 체크리스트
- [x] 동시 재고 부족 주문 2건 이상 처리 시 재고 음수 발생하지 않음
- [x] 단일 주문 시나리오 결과는 기존과 동일(회귀 없음)
- [x] 콘솔 E2E로 실제 재현 및 수정 확인
- [x] docs/FEATURES/approval.md, production_line.md 최신 동작 반영

### 변경된 파일 목록
- `app/controllers/approval_controller.py`, `app/controllers/production_controller.py` (수정)
- `tests/test_production_concurrency.py` (신규)
- `tests/test_approval_controller.py` (수정)
- `docs/FEATURES/approval.md`, `docs/FEATURES/production_line.md` (수정)

## Phase 9: UI 고도화

### 요청 받은 작업
사용자 요청으로 콘솔 UI를 과제 명세 예시 화면 수준으로 고도화. 설계 문서(docs/design/phase9_ui.md)
작성 후 잔여율 기준치(200ea)와 주문 집계 범위(REJECTED 포함) 2가지를 질의하여 사용자 승인 받음.

### 변경 요약
- `app/views/console_view.py`: `summarize_dashboard()`, `stock_bar()` 순수 함수 추가(단위 테스트 가능),
  메인 메뉴에 시스템 현황 요약 표시, 재고 조회에 잔여율 막대 추가, 주문 상태를 `[STATUS]` 형태로 통일
- `app/controllers/main_controller.py`: 메인 메뉴 표시 시 요약 데이터 조립하여 전달

### TDD 사이클 기록
- RED: `summarize_dashboard`/`stock_bar` 부재로 collection error 확인
- GREEN: 구현 후 5개 신규 테스트 PASS, 전체 48/48 PASS (회귀 없음)
- REVIEW: 콘솔에서 시료 등록→주문→거절→모니터링까지 실행하여 시스템 현황 요약과 잔여율 막대가
  올바르게 갱신되는 것을 확인

### 요청사항 충족 여부 체크리스트
- [x] 메인 메뉴에 시스템 현황 요약(등록 시료/총 재고/전체 주문/생산 대기) 표시
- [x] 재고 조회에 잔여율 막대 표시
- [x] 주문 상태 표기 통일(`[STATUS]`)
- [x] Verify Harness 통과, 콘솔 E2E 검증 완료

### 변경된 파일 목록
- `app/views/console_view.py`, `app/controllers/main_controller.py` (수정)
- `tests/test_console_view_helpers.py` (신규)

## 추가 보강: 독립 SubAgent 검증 및 후속 조치

### 배경
강의자료(Day1, Ch.10 "AE 관점에서 SubAgent 사용 방안")에 따라, Human Review 이전에
독립적인 Verify SubAgent를 통해 재고 이중 계산 버그 수정의 정확성과 잔여 결함을 점검함.

### SubAgent 감사 결과
1. **재고 이중 계산 버그 수정: 정확함** (코드 추적으로 재검증, 이중계산 재발 없음)
2. 진짜 멀티프로세스 동시성(파일 락 없음)은 미대응 — 단일 프로세스 가정이므로 범위 밖으로 문서화 필요
3. 테스트 공백: 대기 주문 3건 이상, `release()`를 PRODUCING/REJECTED 상태에 시도하는 케이스 누락
4. 죽은 코드: `Sample`/`Order` 데이터클래스의 `to_dict`/`from_dict`가 미사용
   (직접 추가 조사 결과, `to_dict`/`from_dict`뿐 아니라 `Sample`/`Order` 데이터클래스 자체가
   어디서도 임포트되지 않는 완전한 죽은 코드였음 — `OrderStatus` enum만 실제로 사용됨)

### 사람 검토 및 결정
죽은 코드 처리 방식(삭제 vs Repository에서 실제 연결)을 질의 → **삭제**로 결정.

### 변경 요약
- `app/models/sample.py` 삭제 (미사용)
- `app/models/order.py`: `Order` 데이터클래스 제거, `OrderStatus` enum만 유지
- `tests/test_production_concurrency.py`: 3건 이상 동시 대기, 시료 혼합 FIFO 정식 회귀 테스트 추가
- `tests/test_release_controller.py`: PRODUCING/REJECTED 상태 출고 시도 테스트 추가(중복 assert 정리)
- `CLAUDE.md`: 멀티프로세스 동시성 미대응을 "범위 밖 한계"로 명시

### 검증 사이클 기록
- 수동 스크립트로 3건 동시 대기, 시료 혼합 FIFO 시나리오 재현 → 모두 정상(음수 없음, FIFO 순서 보장)
- 죽은 코드 삭제 전 grep으로 전체 코드베이스에서 미사용 확인
- 회귀 테스트 52/52 PASS (신규 6개 포함)
- 콘솔 E2E로 최종 정상 동작 확인

### 요청사항 충족 여부 체크리스트
- [x] 독립 SubAgent를 통한 재고 버그 수정 검증 완료
- [x] 3건 이상 동시 대기 시나리오 정식 회귀 테스트로 고정
- [x] release() 상태 검증 테스트 보강(PRODUCING/REJECTED)
- [x] 죽은 코드 제거(사용자 승인)
- [x] 멀티프로세스 동시성 한계 문서화
- [x] Verify Harness(pytest 52/52 + Compliance 체크) 통과

### 변경된 파일 목록
- `app/models/sample.py` (삭제)
- `app/models/order.py` (수정 - Order 데이터클래스 제거)
- `tests/test_production_concurrency.py`, `tests/test_release_controller.py` (수정)
- `CLAUDE.md` (수정)

## 추가 보강: 공백 ID 검증 + 한글 표 정렬(cosmetic) 수정

### 배경
사용자 요청으로 특수문자/빈 값 공격 테스트를 추가로 수행하던 중, 빈 문자열/공백만 있는
시료 ID·이름이 등록되는 데이터 무결성 문제를 발견함. 또한 README 예시 UI의 표 정렬이
한글 때문에 깨져 있다는 지적을 받아, 실제 콘솔 출력 정렬 로직 자체를 점검함.

### 발견한 문제
1. `SampleController.register()`가 빈 문자열(`""`)이나 공백만 있는 `sample_id`/`name`을
   그대로 등록해버림(재현 스크립트로 확인).
2. Python의 `f"{text:<N}"`는 문자 "개수" 기준으로 패딩하는데, 한글은 터미널에서 2칸을
   차지하므로 한글이 섞인 표가 실제 터미널에서 삐뚤어짐.
3. 위 1차 수정(`visual_ljust`, 표시 너비 기준 패딩)만으로는, 컬럼 폭보다 긴 텍스트(예:
   "삼성전자 파운드리"가 16칸 폭을 초과)가 들어오면 다음 컬럼과 공백 없이 붙어버리는
   2차 문제가 남아있음을 실제 실행(E2E)에서 재발견함(`파운드리200`처럼 표시).

### 사람 검토 및 결정
빈 ID/이름 차단 여부, join_columns의 "최소 1칸 보장" 방식을 순서대로 질의하여 승인받음.

### 변경 요약
- `app/controllers/sample_controller.py`: `_validate()`에 sample_id/name의 공백 전용 값 차단 추가
- `app/views/console_view.py`: `display_width()`(East Asian Width 기반 표시 너비 계산),
  `visual_ljust()`(표시 너비 기준 패딩), `join_columns()`(컬럼 폭 초과 시에도 최소 1칸
  공백 보장) 추가. 모든 표 출력(`show_samples`, `show_orders`, `show_stock_status`,
  `show_production_queue`)을 `join_columns` 기반으로 교체.
- README.md의 예시 UI 화면을 정렬이 올바른 실제 실행 결과로 갱신, 중복된 모니터링 섹션 정리.

### TDD 사이클 기록
- RED: `display_width`/`visual_ljust`/`join_columns`/공백 검증 부재로 각각 실패 확인
- GREEN: 구현 후 신규 12개 테스트 PASS, 전체 64/64 PASS
- REVIEW: 콘솔에서 긴 고객명("삼성전자 파운드리") 포함 표를 직접 실행하여 컬럼 충돌이
  사라지고 한글 정렬이 올바른 것을 확인

### 요청사항 충족 여부 체크리스트
- [x] 빈 문자열/공백 전용 시료 ID·이름 등록 차단
- [x] 한글 포함 표 정렬이 표시 너비 기준으로 정확히 계산됨
- [x] 컬럼 폭을 초과하는 텍스트도 다음 컬럼과 최소 1칸 공백 보장
- [x] README 예시 화면을 정렬이 올바른 실제 출력으로 갱신
- [x] 전체 64/64 PASS, 콘솔 E2E 검증 완료

### 변경된 파일 목록
- `app/controllers/sample_controller.py` (수정)
- `app/views/console_view.py` (수정)
- `tests/test_sample_safety.py`, `tests/test_display_width.py` (수정/신규)
- `README.md` (수정)

## 추가 보강: 클린 클론 스모크 테스트 + 커버리지 측정

### 배경
사용자 제안으로 "실제 채점 환경"을 흉내내기 위해 `/tmp`에 5개 리포지토리를 새로 `git clone`하여
아무 로컬 상태도 없는 상태에서 실행/테스트가 되는지 확인함.

### 발견한 문제
- `requirements.txt`가 없어, pytest가 전역 설치되지 않은 환경에서는 `python -m pytest`가
  실패할 수 있음(이 환경은 pytest가 이미 있어 통과했지만 이는 우연). `main.py` 실행 자체는
  표준 라이브러리만 사용하므로 영향 없음.

### 변경 요약
- `requirements.txt` 추가(`pytest>=7.0`), README/CLAUDE.md에 설치 안내 추가
- `pip install -r requirements.txt` 포함한 완전 클린 클론 시나리오로 재검증 완료(5개 리포 전부)
- `coverage` 도구로 측정한 결과, View(콘솔 출력) 계층을 제외한 Model/Repository/Controller
  전체가 100% 커버리지였으나, 위임 메서드(`list_reserved`, `list_all`)와 방어적 분기
  (`JsonStore.update/delete`의 "찾지 못함" 경로, `SampleRepository.adjust_stock`의 존재하지
  않는 sample_id 처리)가 테스트되지 않아 6개 테스트 추가
- `.gitignore`에 커버리지 산출물(`.coverage`, `htmlcov/`) 추가

### 검증 사이클 기록
- 5개 리포 전부 `/tmp`에 clone → 실행/테스트 exit 0 확인 (요구사항 파일 추가 전/후 비교)
- 커버리지 측정: 추가 전 83%(View 포함) → 핵심 로직(Model/Repository/Controller) 100% 확인
- 전체 회귀 테스트 70/70 PASS

### 요청사항 충족 여부 체크리스트
- [x] 클린 클론 스모크 테스트로 실제 배포/채점 환경 시뮬레이션
- [x] requirements.txt 추가로 의존성 명세 완비
- [x] 핵심 로직 100% 테스트 커버리지 확보
- [x] 5개 리포 전부 클린 클론 검증 완료

### 변경된 파일 목록
- `requirements.txt` (신규)
- `README.md`, `CLAUDE.md`, `.gitignore` (수정)
- `tests/test_approval_controller.py`, `test_order_controller.py`, `test_sample_repository.py` (수정)
- `tests/test_json_store.py` (신규)
