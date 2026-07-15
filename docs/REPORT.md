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
