# Phase 11 설계: 점수 개선 3종 (CI 자동화 / JsonStore 쓰기 성능 / View 계층 테스트 보강)

## 배경

"최종 결과물이 몇 점짜리인가"에 대한 자체 평가에서 아래 3가지 감점 요인이 지적됨. 사용자가
"CI + 성능 + View 테스트 보강까지 전부" 진행을 승인함(AskUserQuestion).

## 1. CI 자동화

- `.github/workflows/test.yml` 추가: `push`/`pull_request` 시 Python 3 환경에서
  `pip install -r requirements.txt` 후 `python -m pytest tests/` 실행.
- 기존 `scripts/verify.py`(로컬 Harness)는 그대로 유지한다. CI는 "Test Verify" 단계를
  원격에서도 강제하는 추가 안전망이며, Compliance Verify(사람 최종 확인)를 대체하지 않는다.

## 2. JsonStore 쓰기 성능 개선

- 배경: Phase 10에서 읽기는 캐싱했으나 `insert`/`update`/`delete`는 매 호출마다 파일 전체를
  재직렬화(O(n) write)하여 1000건 규모에서 병목이 남아있었음(당시 사용자가 "여기까지만, 문서화"로
  결정 → 이번에 마저 해결하기로 재결정).
- 설계: "dirty flag + 명시적 flush" 방식을 채택한다.
  - `insert`/`update`/`delete`는 캐시만 갱신하고 `self._dirty = True`로 표시, 즉시 디스크에
    쓰지 않는다.
  - `flush()` 메서드를 추가해 dirty일 때만 디스크에 쓰고 플래그를 내린다.
  - **데이터 유실 방지가 최우선이므로**, 각 Repository의 도메인 메서드(`create`, `update_status`,
    `adjust_stock` 등)가 매 호출 끝에 `flush()`를 호출하도록 하여 "매 변경 후 즉시 영속화"라는
    기존 계약(동작 관찰 가능한 범위)은 그대로 유지한다. 즉, 겉보기 동작은 Phase 10과 동일하되,
    내부적으로 여러 필드를 한 레코드 안에서 갱신할 때(예: `update()`가 여러 필드를 한 번에 바꾸는
    경우) 중복 flush를 줄이는 구조로 정리한다.
  - 실질적 성능 개선은 주로 반복 `insert`(스트레스 테스트의 대량 생성) 구간에서, 호출자가
    `flush=False`를 넘겨 배치 처리 후 마지막에 한 번만 `flush()`하는 옵션을 추가로 제공한다.
    앱의 실제 콘솔 흐름(1건씩 승인/등록)은 매번 flush하므로 동작 변화가 없다.
- out of scope: 트랜잭션/롤백, 파일 락 기반 멀티프로세스 동시성(기존과 동일하게 범위 밖).

## 3. View 계층 테스트 보강

- 대상: `app/controllers/main_controller.py`의 `run()` 및 하위 메뉴 분기(`_sample_menu`,
  `_approval_menu` 등)의 입력값 → 분기 로직.
- 방법: `MainController`는 생성자에서 리포지토리를 직접 생성하므로(파일 경로 `data/*.json` 고정),
  테스트는 `tmp_path`로 작업 디렉터리를 옮긴 뒤(`monkeypatch.chdir`) `builtins.input`을
  순차 응답 큐로 monkeypatch하고 `capsys`로 출력만 확인한다. 프로덕션 코드는 변경하지 않는다
  (테스트만 추가, Clean Code 원칙상 테스트를 위한 의존성 주입 리팩토링은 이번 범위에서 제외 —
  기존 계층 구조로도 충분히 테스트 가능하다고 판단).
- 커버 대상: 메인 메뉴 종료(`0`), 잘못된 선택, 시료 등록 성공/검증 오류, 주문 예약, 승인/거절
  분기, 모니터링 메뉴, 생산 메뉴, 출고 메뉴 각 서브메뉴의 정상/오류 경로 최소 1개씩.

## 테스트 전략 (공통)

- 기존 73개 테스트가 모두 그대로 통과해야 한다(회귀 없음).
- JsonStore 변경은 `test_json_store.py`, `test_json_store_cache.py`에 flush 관련 케이스를
  추가하고, 기존 "매 insert/update/delete 후 즉시 디스크 반영" 계약을 검증하는 기존 테스트는
  그대로 통과해야 한다(flush=True 기본값이므로).
- CI 워크플로우는 로컬에서 `act` 등으로 직접 실행 검증하기 어려우므로, YAML 문법과 커맨드가
  로컬 `scripts/verify.py`의 Test Verify 단계와 동일한 커맨드(`pip install -r requirements.txt`,
  `pytest tests/`)를 쓰는지로 리뷰한다.

## out of scope

- View의 실제 콘솔 출력 포맷(`show_*` 메서드들의 문자열 정렬 등)은 Phase 9에서 이미 단위
  테스트(`test_console_view_helpers.py`, `test_display_width.py`)로 커버되어 있으므로 중복 작성하지 않는다.
