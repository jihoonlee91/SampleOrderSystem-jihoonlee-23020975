# CLAUDE.md

이 파일은 Claude Code가 이 리포지토리에서 작업할 때 참고하는 지침을 담는다.
개인과제의 5대 주안점(문서 관리 / Harness / Test / Clean Code / Commit 이력)에 맞춰 정리한다.

## 기술 스택

- Python 3, 표준 라이브러리 위주 (외부 의존성 최소화)
- 데이터 영속성: JSON 파일 (PoC `DataPersistence-jihoonlee-23020975`의 `JsonStore` 설계를 계승)
- 테스트: `pytest`

## 실행 / 테스트

```
pip install -r requirements.txt  # pytest 설치 (최초 1회, 테스트 실행 시에만 필요)
python main.py           # 콘솔 앱 실행 (표준 라이브러리만 사용, 설치 불필요)
python -m pytest tests/  # 전체 테스트 실행
python scripts/verify.py # Verify Harness (Test Verify -> Compliance Verify)
```

## 1. 문서 관리

- `docs/PRD.md`: 전체 요구사항(거시적, 기술적 내용 없음)
- `docs/PLAN.md`: Phase별 개발 계획 및 진행 상황(거시적 계획, 체크박스로 진행 추적)
- `docs/design/phaseN.md` (+ [인덱스](docs/design/README.md)): Phase별 상세 설계 문서(세부 계획).
  사람이 승인한 원본을 그대로 유지하며, 구현 중 발생한 편차는 문서를 고치지 않고 `docs/REPORT.md`에 기록한다.
- `docs/FEATURES/*.md`: 기능 단위 상세 명세(입력값/검증 규칙/경계값). PRD의 기능 요구사항 절에서 링크한다.
- `docs/REPORT.md`: Phase별 AI 작업 보고서(요청/해석/변경 요약/TDD 기록/체크리스트/변경 파일 목록)
- `README.md`: 실행 방법, 기능 목록, 프로젝트 구조, 문서 링크를 항상 최신 상태로 유지한다.

## 2. Harness 도입

Phase 4부터 커밋 전 `python scripts/verify.py`(Verify Harness)를 실행한다.
1. Test Verify: pytest 전체 스위트 실행, 실패 시 즉시 중단(Compliance Verify로 진행하지 않음)
2. Compliance Verify: 설계 문서 범위 준수 / PLAN 체크리스트 충족 / E2E 수동 검증 / 작업 보고서 작성 여부를
   사람이 최종 확인

## 3. Test

- 콘솔 I/O에 의존하지 않는 Controller 메서드 단위로 pytest 작성 (View는 별도 수동 E2E 검증으로 분리)
- 각 Phase마다 TDD 사이클(RED: 실패 테스트 작성 및 실패 확인 → GREEN: 최소 구현 후 통과 → REVIEW: 리팩토링/체크)을 따른다
- 회귀(Regression): 새 Phase 작업 후 반드시 전체 테스트 스위트를 재실행하여 기존 기능이 깨지지 않았는지 확인한다

## 4. Clean Code

- Model은 순수 데이터만 가지며 로직을 갖지 않는다.
- Repository는 CRUD/조회만 담당하고 도메인 규칙(승인 분기, 생산 계산 등)을 갖지 않는다.
- Controller가 도메인 규칙을 담당하며, View나 Repository의 구체적 구현에 의존하지 않는다.
- View는 입출력만 담당하고 비즈니스 로직을 포함하지 않는다.

## 5. Commit 이력

- 각 Phase 완료 시 하나의 커밋으로 정리하고, 커밋 메시지에 어떤 Phase/설계 문서를 따랐는지, TDD/Verify 결과를 남긴다.
- 커밋 메시지 말미에 `Reviewed-by: jihoonlee91`로 사람 검토 완료를 표시한다(코드를 만든 AI가 아니라
  검토·승인한 사람이 최종 책임을 진다는 원칙을 반영).

## 개발 절차 (Phase 7부터 적용)

1. AI가 `docs/design/phaseN.md` 설계 문서를 작성하여 제시한다.
2. 사람이 설계 문서를 검토하고, 필요 시 수정을 요청한다(기대치 확보).
3. 승인된 설계 문서를 기반으로만 TDD(RED→GREEN) 구현을 진행한다.
4. Verify Harness 통과 후 사람이 콘솔 E2E 검증 및 최종 리뷰.
5. 작업 보고서(`docs/REPORT.md`) 작성 후 커밋.

## 도메인 규칙 (변경 가능성 낮은 핵심 규칙만 기록)

- 주문 상태는 `RESERVED → (REJECTED | CONFIRMED | PRODUCING → CONFIRMED) → RELEASE` 순으로만 전이한다.
- 승인 시 재고가 주문 수량 미만이면, **그 시점의 재고 전량을 즉시 소진(0으로 차감)**하고 생산
  큐에 부족분을 등록한다. 재고를 즉시 소진하지 않으면 같은 시료의 여러 대기 주문이 동일한 재고를
  중복으로 계산해 재고가 음수가 되는 버그가 발생한다(발견 경위: docs/REPORT.md "동시 승인 재고
  이중 계산 버그" 참고). 이 불변식을 깨지 않도록 주의한다.
- 실 생산량 = `ceil(부족분 / 수율)`, 총 생산 시간 = `평균 생산시간 * 실 생산량`.
  생산 완료 시 재고 반영 = `실 생산량 - 부족분`(반올림 잉여만 재고로 편입).
- 생산 큐는 FIFO(선입선출)로 처리하며, 시료가 섞여 있어도 등록 순서를 그대로 지킨다.
- REJECTED 상태는 모니터링 집계에서 제외한다.
- 시료 등록 시 수율은 `(0, 1]`, 평균 생산시간은 `> 0`, 재고는 `>= 0`이어야 한다(수율 0은
  생산 단계에서 `ZeroDivisionError`로 이어지므로 반드시 차단).

## 알려진 범위 밖 한계 (Out of Scope)

- `JsonStore`의 read-modify-write는 파일 락이 없다. 단일 프로세스(콘솔 앱 1개 실행) 환경을
  가정하며, 여러 프로세스가 동시에 같은 데이터 파일에 쓰는 상황(진짜 멀티프로세스 동시성)은
  지원하지 않는다. 이번에 고친 "재고 이중 계산 버그"는 같은 프로세스 내 순차 승인 호출 사이의
  논리 버그였고, 파일 락 부재로 인한 진짜 동시 쓰기 충돌과는 별개다.
