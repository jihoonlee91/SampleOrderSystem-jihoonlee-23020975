import unicodedata


def _char_width(ch: str) -> int:
    return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1


def display_width(text: str) -> int:
    """터미널에서 실제로 차지하는 표시 너비를 계산한다 (한글/전각 문자는 2칸)."""
    return sum(_char_width(ch) for ch in text)


def visual_ljust(text: str, width: int) -> str:
    """len() 대신 표시 너비 기준으로 왼쪽 정렬 패딩한다 (한글 포함 표 정렬용)."""
    pad = max(0, width - display_width(text))
    return text + " " * pad


def join_columns(*columns: tuple[str, int]) -> str:
    """(텍스트, 목표폭) 쌍들을 이어붙이되, 텍스트가 목표폭을 넘어가도 다음 컬럼과
    최소 1칸은 항상 띄운다 (컬럼 충돌 방지)."""
    parts = []
    for text, width in columns:
        if display_width(text) >= width:
            parts.append(text + " ")
        else:
            parts.append(visual_ljust(text, width))
    return "".join(parts)


def summarize_dashboard(samples: list[dict], orders: list[dict], queue: list[dict]) -> dict:
    """메인 메뉴 상단에 표시할 시스템 현황 요약을 계산한다 (순수 함수, 단위 테스트 가능)."""
    return {
        "sample_count": len(samples),
        "total_stock": sum(s["stock"] for s in samples),
        "order_count": len(orders),
        "queue_count": len(queue),
    }


def stock_bar(stock: int, capacity: int = 200, width: int = 10) -> str:
    """재고 잔여율을 텍스트 막대로 표현한다 (순수 함수, 단위 테스트 가능)."""
    ratio = min(1.0, stock / capacity) if capacity > 0 else 0.0
    filled = round(ratio * width)
    bar = "#" * filled + "." * (width - filled)
    percent = round(ratio * 100)
    return f"[{bar}] {percent}%"


class ConsoleView:
    """모든 콘솔 입출력을 전담한다. 비즈니스 로직을 갖지 않는다."""

    def show_main_menu(self, summary: dict) -> None:
        print("=" * 60)
        print(" 반도체 시료 생산주문관리 시스템")
        print("=" * 60)
        print(
            f" 시스템 현황  등록 시료 {summary['sample_count']}종  "
            f"총 재고 {summary['total_stock']}ea  전체 주문 {summary['order_count']}건  "
            f"생산라인 {summary['queue_count']}건 대기"
        )
        print("-" * 60)
        print("[1] 시료 관리   [2] 시료 주문   [3] 주문 승인/거절")
        print("[4] 모니터링    [5] 생산 라인   [6] 출고 처리   [0] 종료")

    def show_sample_menu(self) -> None:
        print("-" * 60)
        print(" [시료 관리]")
        print("[1] 시료 등록   [2] 시료 목록   [3] 시료 검색   [0] 뒤로")

    def show_approval_menu(self) -> None:
        print("-" * 60)
        print(" [주문 승인/거절]")
        print("[1] 승인   [2] 거절   [0] 뒤로")

    def show_monitoring_menu(self) -> None:
        print("-" * 60)
        print(" [모니터링]")
        print("[1] 주문량 확인   [2] 재고량 확인   [0] 뒤로")

    def show_order_counts(self, counts: dict) -> None:
        print("[상태별 주문 현황] (REJECTED 제외)")
        for status, count in counts.items():
            print(f"  {visual_ljust(status, 12)}{count}건")

    def show_stock_status(self, statuses: list[dict]) -> None:
        if not statuses:
            print("등록된 시료가 없습니다.")
            return
        print(join_columns(("ID", 8), ("이름", 22), ("재고", 8), ("상태", 8)) + "잔여율")
        for s in statuses:
            print(
                join_columns(
                    (s["sample_id"], 8), (s["name"], 22),
                    (str(s["stock"]), 8), (s["status"], 8),
                )
                + stock_bar(s["stock"])
            )

    def show_production_menu(self) -> None:
        print("-" * 60)
        print(" [생산 라인]")
        print("[1] 다음 항목 생산 처리   [2] 대기열 조회   [0] 뒤로")

    def show_production_queue(self, queue: list[dict]) -> None:
        if not queue:
            print("생산 대기 중인 항목이 없습니다.")
            return
        print(join_columns(("순서", 6), ("주문번호", 16), ("시료ID", 8), ("부족분", 8)) + "주문수량")
        for i, entry in enumerate(queue, start=1):
            print(
                join_columns(
                    (str(i), 6), (entry["order_id"], 16),
                    (entry["sample_id"], 8), (str(entry["shortage"]), 8),
                )
                + str(entry["quantity"])
            )

    def show_release_menu(self) -> None:
        print("-" * 60)
        print(" [출고 처리]")
        print("[1] 출고 실행   [0] 뒤로")

    def show_production_result(self, result: dict) -> None:
        print(
            f"생산 완료 - 주문 {result['order_id']} / 시료 {result['sample_id']} / "
            f"부족분 {result['shortage']} -> 실생산량 {result['actual_quantity']} "
            f"(예상 소요 {result['total_time']:.2f}분)"
        )

    def prompt(self, message: str) -> str:
        return input(f"{message} > ").strip()

    def show_message(self, message: str) -> None:
        print(message)

    def show_orders(self, orders: list[dict]) -> None:
        if not orders:
            print("등록된 주문이 없습니다.")
            return
        print(join_columns(("주문번호", 16), ("시료ID", 8), ("고객명", 20), ("수량", 8)) + "상태")
        for o in orders:
            print(
                join_columns(
                    (o["order_id"], 16), (o["sample_id"], 8),
                    (o["customer"], 20), (str(o["quantity"]), 8),
                )
                + f"[{o['status']}]"
            )

    def show_samples(self, samples: list[dict]) -> None:
        if not samples:
            print("등록된 시료가 없습니다.")
            return
        print(join_columns(("ID", 8), ("이름", 22), ("평균생산시간", 14), ("수율", 8)) + "재고")
        for s in samples:
            print(
                join_columns(
                    (s["sample_id"], 8), (s["name"], 22),
                    (str(s["avg_process_time"]), 14), (str(s["yield_rate"]), 8),
                )
                + str(s["stock"])
            )
