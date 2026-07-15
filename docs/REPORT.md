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
