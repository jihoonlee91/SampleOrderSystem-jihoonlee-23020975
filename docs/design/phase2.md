# Phase 2 설계: 메인 메뉴 + 시료 관리

## 목표

콘솔 메인 메뉴 뼈대와 시료 등록/조회/검색 기능을 구현한다.

## 아키텍처

```
app/
  views/
    console_view.py     # 입출력 전담 (표시/프롬프트), 로직 없음
  controllers/
    sample_controller.py  # 시료 등록/조회/검색 - 테스트 가능하도록 순수 파라미터 기반 메서드로 설계
    main_controller.py    # 메뉴 루프, 하위 Controller에 위임
main.py                  # 진입점
```

## 테스트 전략

콘솔 입출력(input/print) 자체는 테스트하기 어렵고 의미가 적으므로, `SampleController`의 핵심 메서드는
View에 의존하지 않고 순수 파라미터(sample_id, name, ...)를 받는 형태로 설계하여 pytest로 직접 검증한다.
`main.py`를 통한 실제 콘솔 동작은 사람이 직접 실행하여 확인한다(E2E 수동 검증).

## 테스트 케이스

1. 시료 등록 후 목록 조회 시 등록한 시료가 포함되는지
2. 이미 존재하는 sample_id로 재등록 시도 시 오류 처리(중복 방지)
3. 이름 키워드 검색 시 일치하는 시료만 반환되는지
4. 존재하지 않는 시료 조회 시 None/빈 결과 반환

## out of scope

- 주문 관련 기능 (Phase 3 이후)
- 실제 콘솔 입력 시나리오 자동화 테스트 (수동 검증으로 대체)
