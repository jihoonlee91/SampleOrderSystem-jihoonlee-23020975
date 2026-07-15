"""
Safety Test (안전성 테스트)

정상적인 사용 시나리오가 아닌, 잘못되거나 극단적인 입력값을 넣었을 때
시스템이 안전하게(예외를 명확히 발생시키며) 방어하는지 검증한다.
아래 테스트들은 실제 코드 공격(수동 스크립트 실행)으로 먼저 문제를 발견한 뒤 작성되었다.
"""
import os
import tempfile

import pytest

from app.controllers.sample_controller import SampleController, InvalidSampleDataError
from app.repositories.sample_repository import SampleRepository


def _controller():
    tmp_dir = tempfile.mkdtemp()
    repo = SampleRepository(os.path.join(tmp_dir, "samples.json"))
    return SampleController(repo)


def test_register_with_zero_yield_rate_raises_error():
    """yield_rate=0이면 생산 단계에서 ZeroDivisionError로 이어지므로 등록 자체를 막는다."""
    controller = _controller()

    with pytest.raises(InvalidSampleDataError):
        controller.register("S-999", "위험시료", 0.5, 0.0, 10)


def test_register_with_yield_rate_above_one_raises_error():
    controller = _controller()

    with pytest.raises(InvalidSampleDataError):
        controller.register("S-B", "B", 0.5, 1.5, 10)


def test_register_with_negative_yield_rate_raises_error():
    controller = _controller()

    with pytest.raises(InvalidSampleDataError):
        controller.register("S-B", "B", 0.5, -0.1, 10)


def test_register_with_negative_avg_process_time_raises_error():
    controller = _controller()

    with pytest.raises(InvalidSampleDataError):
        controller.register("S-C", "C", -5, 0.9, 10)


def test_register_with_zero_avg_process_time_raises_error():
    controller = _controller()

    with pytest.raises(InvalidSampleDataError):
        controller.register("S-C", "C", 0, 0.9, 10)


def test_register_with_negative_stock_raises_error():
    controller = _controller()

    with pytest.raises(InvalidSampleDataError):
        controller.register("S-A", "A", 0.5, 0.9, -100)


def test_register_with_valid_boundary_values_succeeds():
    """경계값(yield_rate=1, stock=0)은 정상 등록되어야 한다 (과도한 제약 금지)."""
    controller = _controller()

    sample = controller.register("S-OK", "정상시료", 0.1, 1.0, 0)

    assert sample["yield_rate"] == 1.0
    assert sample["stock"] == 0


def test_search_with_empty_keyword_returns_all_samples():
    """빈 문자열 검색은 모든 시료를 반환한다 (모든 이름에 '' 포함되므로 정상 동작)."""
    controller = _controller()
    controller.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)
    controller.register("S-002", "GaN 에피택셜-4인치", 0.3, 0.78, 220)

    results = controller.search("")

    assert len(results) == 2
