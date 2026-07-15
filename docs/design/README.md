# 설계 문서 인덱스

각 Phase의 상세 설계 문서 목록이다. 전체 진행 상황은 [`docs/PLAN.md`](../PLAN.md), 요구사항 원본은
[`docs/PRD.md`](../PRD.md), Phase별 작업 이력은 [`docs/REPORT.md`](../REPORT.md)를 참고한다.

| Phase | 문서 | 내용 | 상태 |
|---|---|---|---|
| 1 | [phase1.md](phase1.md) | 프로젝트 스캐폴드 + 데이터 영속성 계층 (Sample/Order 모델, JsonStore Repository) | 완료 |
| 2 | [phase2.md](phase2.md) | 메인 메뉴 + 시료 관리 (등록/조회/검색) | 완료 |
| 3 | [phase3.md](phase3.md) | 시료 주문(예약) | 완료 |
| 4 | [phase4.md](phase4.md) | 주문 승인/거절 (재고 비교 분기, 생산 큐 등록) | 완료 |
| 5 | [phase5.md](phase5.md) | 생산 라인 (FIFO 큐 처리, 실생산량/생산시간 계산) | 완료 |
| 6 | [phase6.md](phase6.md) | 모니터링 (주문량/재고량 확인) | 완료 |
| 7 | phase7.md (예정) | 출고 처리 | 설계 검토 중 |
| 8 | - | 통합 마감 (설계 문서 없이 전체 회귀/정리로 진행) | 예정 |

## 설계 문서 작성 규칙

- 각 문서는 "목표 → 아키텍처 → (필요 시 계산/동작 규칙) → 테스트 케이스 → out of scope" 순서로 통일한다.
- 실제 구현 중 설계와 달라진 부분이 발생하면, 해당 Phase 문서를 직접 수정하지 않고
  `docs/REPORT.md`의 해당 Phase 섹션에 "TDD 사이클 기록"으로 편차와 사유를 남긴다
  (설계 문서는 사람이 승인한 원본을 그대로 유지하여 의사결정 이력을 보존하기 위함).
