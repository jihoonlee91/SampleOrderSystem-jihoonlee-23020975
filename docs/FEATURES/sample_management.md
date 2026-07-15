# 기능 명세: 시료 관리

## 시료 등록
- 입력: 시료 ID(문자열, 고유), 이름, 평균 생산시간(분, 실수), 수율(0~1 실수), 초기 재고(정수, 생략 시 0)
- 이미 존재하는 시료 ID로 등록 시 오류 처리(등록 거부, 기존 데이터 보존)
- 성공 시 등록 완료 메시지 표시

## 시료 조회
- 등록된 모든 시료를 ID/이름/평균생산시간/수율/현재 재고와 함께 목록으로 표시
- 등록된 시료가 없으면 안내 메시지 표시

## 시료 검색
- 이름에 포함된 키워드로 검색 (부분 일치)
- 검색 결과가 없으면 빈 목록으로 처리(안내 메시지 표시)

## 구현 위치
- `app/controllers/sample_controller.py` (`SampleController`)
- `app/repositories/sample_repository.py`
- 관련 설계 문서: [`docs/design/phase1.md`](../design/phase1.md), [`docs/design/phase2.md`](../design/phase2.md)
