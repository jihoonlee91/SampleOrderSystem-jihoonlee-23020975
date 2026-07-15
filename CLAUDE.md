# CLAUDE.md

이 파일은 Claude Code가 이 리포지토리에서 작업할 때 참고하는 규칙을 담는다.

## 기술 스택

- Python 3, 표준 라이브러리 위주 (외부 의존성 최소화)
- 데이터 영속성: JSON 파일 (PoC `DataPersistence-jihoonlee-23020975`의 `JsonStore` 설계를 계승)
- 테스트: `pytest`

## 실행 / 테스트

```
python main.py           # 콘솔 앱 실행
python -m pytest tests/  # 전체 테스트 실행
python scripts/verify.py # Verify Harness (Test Verify -> Compliance Verify)
```

## Verify Harness

Phase 4부터 커밋 전 `python scripts/verify.py`를 실행한다.
1. Test Verify: pytest 전체 스위트 실행, 실패 시 즉시 중단
2. Compliance Verify: 설계 문서/PLAN 체크리스트/E2E 수동 검증/작업 보고서 작성 여부를 사람이 최종 확인

## 문서 구조

- `docs/PRD.md`: 전체 요구사항 (기술적 내용 없음)
- `docs/PLAN.md`: Phase별 개발 계획 및 진행 상황 (개발 중에만 참조, 완료된 Phase는 체크 표시)
- `docs/design/phaseN.md`: Phase별 상세 설계 문서

## 개발 프로세스 원칙

- 각 Phase는 독립적으로 실행 가능한 완성 소프트웨어여야 한다. Phase 완료 시마다 직접 실행하여 검증한 뒤 커밋한다.
- 코드 작성 전 해당 Phase의 설계 문서(`docs/design/phaseN.md`)를 먼저 작성하고 검토를 거친다.
- 매 Phase 완료 후 AI는 작업 보고서(요청 내용/해석/변경 요약/체크리스트/변경 파일 목록)를 제시하고, 사람이 검토 후 커밋한다.

## 도메인 규칙 (변경 가능성 낮은 핵심 규칙만 기록)

- 주문 상태는 `RESERVED → (REJECTED | CONFIRMED | PRODUCING → CONFIRMED) → RELEASE` 순으로만 전이한다.
- 실 생산량 = `ceil(부족분 / 수율)`, 총 생산 시간 = `평균 생산시간 * 실 생산량`.
- 생산 큐는 FIFO(선입선출)로 처리한다.
- REJECTED 상태는 모니터링 집계에서 제외한다.
