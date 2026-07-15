from app.views.console_view import display_width, visual_ljust, join_columns


def test_display_width_counts_ascii_as_one():
    assert display_width("ID") == 2
    assert display_width("S-001") == 5


def test_display_width_counts_korean_as_two():
    # 한글 2글자 = 터미널에서 4칸 너비
    assert display_width("웨이퍼") == 6


def test_display_width_mixed_ascii_and_korean():
    assert display_width("S-001웨이퍼") == 5 + 6


def test_visual_ljust_pads_ascii_by_character_count():
    assert visual_ljust("ID", 8) == "ID" + " " * 6


def test_visual_ljust_pads_korean_by_display_width():
    # "웨이퍼"는 표시 너비 6이므로 폭 10 맞추려면 공백 4칸만 추가
    assert visual_ljust("웨이퍼", 10) == "웨이퍼" + " " * 4


def test_visual_ljust_does_not_truncate_when_text_exceeds_width():
    assert visual_ljust("아주긴이름입니다", 4) == "아주긴이름입니다"


def test_join_columns_pads_normal_case():
    assert join_columns(("ID", 8), ("이름", 6)) == "ID      " + "이름  "


def test_join_columns_guarantees_at_least_one_space_when_overflow():
    """컬럼 텍스트가 지정 폭을 초과해도, 다음 컬럼과 최소 1칸은 항상 띄운다."""
    result = join_columns(("삼성전자 파운드리", 16), ("200", 8))
    assert result.startswith("삼성전자 파운드리 200")
