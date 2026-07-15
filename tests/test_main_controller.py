import builtins

import pytest

from app.controllers.main_controller import MainController


def _run_with_inputs(monkeypatch, tmp_path, inputs):
    """MainController를 tmp_path를 작업 디렉터리로 하여 실행하고, 주어진 입력을 순서대로
    건네준다. 실제 프로덕션 코드는 건드리지 않고 builtins.input과 cwd만 테스트용으로
    monkeypatch한다."""
    monkeypatch.chdir(tmp_path)
    queue = list(inputs)

    def fake_input(prompt=""):
        return queue.pop(0)

    monkeypatch.setattr(builtins, "input", fake_input)
    MainController().run()


def test_exit_immediately(monkeypatch, tmp_path, capsys):
    _run_with_inputs(monkeypatch, tmp_path, ["0"])
    out = capsys.readouterr().out
    assert "종료합니다." in out


def test_invalid_main_menu_choice_shows_message(monkeypatch, tmp_path, capsys):
    _run_with_inputs(monkeypatch, tmp_path, ["9", "0"])
    out = capsys.readouterr().out
    assert "아직 지원하지 않거나 잘못된 선택입니다." in out


def test_register_sample_then_list_via_menu(monkeypatch, tmp_path, capsys):
    _run_with_inputs(
        monkeypatch,
        tmp_path,
        [
            "1",  # 시료 관리
            "1",  # 시료 등록
            "S-001", "웨이퍼", "0.5", "0.9", "10",
            "2",  # 시료 목록
            "0",  # 뒤로
            "0",  # 종료
        ],
    )
    out = capsys.readouterr().out
    assert "등록 완료" in out
    assert "S-001" in out


def test_register_sample_with_invalid_number_shows_value_error_message(monkeypatch, tmp_path, capsys):
    _run_with_inputs(
        monkeypatch,
        tmp_path,
        [
            "1", "1",
            "S-001", "웨이퍼", "abc", "0.9", "10",  # avg_time에 숫자가 아닌 값
            "0", "0",
        ],
    )
    out = capsys.readouterr().out
    assert "입력 값이 올바르지 않습니다." in out


def test_reserve_order_for_unknown_sample_shows_error(monkeypatch, tmp_path, capsys):
    _run_with_inputs(
        monkeypatch,
        tmp_path,
        ["2", "S-NOPE", "고객사", "5", "0"],
    )
    out = capsys.readouterr().out
    assert "S-NOPE" in out


def test_sample_search_and_invalid_submenu_choice(monkeypatch, tmp_path, capsys):
    _run_with_inputs(
        monkeypatch,
        tmp_path,
        ["1", "1", "S-001", "웨이퍼", "0.5", "0.9", "10", "3", "웨이퍼", "9", "0", "0"],
    )
    out = capsys.readouterr().out
    assert "S-001" in out
    assert "잘못된 선택입니다." in out


def test_register_duplicate_sample_shows_error(monkeypatch, tmp_path, capsys):
    _run_with_inputs(
        monkeypatch,
        tmp_path,
        [
            "1", "1", "S-001", "웨이퍼", "0.5", "0.9", "10",
            "1", "S-001", "웨이퍼2", "0.5", "0.9", "10",
            "0", "0",
        ],
    )
    out = capsys.readouterr().out
    assert "이미 존재하는" in out


def test_reserve_order_with_invalid_quantity_input_shows_value_error(monkeypatch, tmp_path, capsys):
    _run_with_inputs(monkeypatch, tmp_path, ["2", "S-001", "고객사", "abc", "0"])
    out = capsys.readouterr().out
    assert "입력 값이 올바르지 않습니다." in out


def test_approval_reject_and_invalid_choice(monkeypatch, tmp_path, capsys):
    _run_with_inputs(
        monkeypatch,
        tmp_path,
        [
            "1", "1", "S-001", "웨이퍼", "0.5", "0.9", "10", "0",
            "2", "S-001", "고객사", "5",
            "3", "2", "ORD-0001",  # 거절
            "9",  # 잘못된 선택
            "0", "0",
        ],
    )
    out = capsys.readouterr().out
    assert "거절 완료" in out
    assert "잘못된 선택입니다." in out


def test_approval_on_unknown_order_shows_invalid_state_error(monkeypatch, tmp_path, capsys):
    _run_with_inputs(monkeypatch, tmp_path, ["3", "1", "ORD-NOPE", "0", "0"])
    out = capsys.readouterr().out
    assert "RESERVED 상태의 주문이 아닙니다" in out


def test_release_on_unknown_order_shows_invalid_state_error(monkeypatch, tmp_path, capsys):
    _run_with_inputs(monkeypatch, tmp_path, ["6", "1", "ORD-NOPE", "9", "0", "0"])
    out = capsys.readouterr().out
    assert "CONFIRMED" in out or "출고" in out
    assert "잘못된 선택입니다." in out


def test_production_menu_no_queue_and_invalid_choice(monkeypatch, tmp_path, capsys):
    _run_with_inputs(monkeypatch, tmp_path, ["5", "1", "2", "9", "0", "0"])
    out = capsys.readouterr().out
    assert "생산 대기 중인 항목이 없습니다." in out
    assert "잘못된 선택입니다." in out


def test_monitoring_menu_invalid_choice(monkeypatch, tmp_path, capsys):
    _run_with_inputs(monkeypatch, tmp_path, ["4", "9", "0", "0"])
    out = capsys.readouterr().out
    assert "잘못된 선택입니다." in out


def test_full_flow_reserve_approve_produce_release(monkeypatch, tmp_path, capsys):
    _run_with_inputs(
        monkeypatch,
        tmp_path,
        [
            "1", "1", "S-001", "웨이퍼", "0.5", "0.9", "0",  # 재고 0으로 등록
            "0",  # 시료관리 뒤로
            "2", "S-001", "고객사", "10",  # 주문 예약 (재고 부족 예정)
            "3",  # 승인/거절 메뉴
            "1", "ORD-0001",  # 첫 주문 승인 -> 재고부족 -> PRODUCING
            "0",  # 승인메뉴 뒤로
            "5",  # 생산 라인
            "1",  # 다음 항목 생산 처리
            "0",  # 생산메뉴 뒤로
            "6",  # 출고 처리
            "1", "ORD-0001",  # 출고
            "0",  # 출고메뉴 뒤로
            "4",  # 모니터링
            "1",  # 주문량 확인
            "2",  # 재고량 확인
            "0",  # 모니터링 뒤로
            "0",  # 종료
        ],
    )
    out = capsys.readouterr().out
    assert "PRODUCING" in out
    assert "생산 완료" in out
    assert "출고 완료" in out
