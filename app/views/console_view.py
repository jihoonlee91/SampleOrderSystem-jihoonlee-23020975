class ConsoleView:
    """모든 콘솔 입출력을 전담한다. 비즈니스 로직을 갖지 않는다."""

    def show_main_menu(self) -> None:
        print("=" * 60)
        print(" 반도체 시료 생산주문관리 시스템")
        print("=" * 60)
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
            print(f"  {status:<12}{count}건")

    def show_stock_status(self, statuses: list[dict]) -> None:
        if not statuses:
            print("등록된 시료가 없습니다.")
            return
        print(f"{'ID':<8}{'이름':<20}{'재고':<8}{'상태'}")
        for s in statuses:
            print(f"{s['sample_id']:<8}{s['name']:<20}{s['stock']:<8}{s['status']}")

    def show_production_menu(self) -> None:
        print("-" * 60)
        print(" [생산 라인]")
        print("[1] 다음 항목 생산 처리   [2] 대기열 조회   [0] 뒤로")

    def show_production_queue(self, queue: list[dict]) -> None:
        if not queue:
            print("생산 대기 중인 항목이 없습니다.")
            return
        print(f"{'순서':<6}{'주문번호':<14}{'시료ID':<8}{'부족분':<8}{'주문수량'}")
        for i, entry in enumerate(queue, start=1):
            print(
                f"{i:<6}{entry['order_id']:<14}{entry['sample_id']:<8}"
                f"{entry['shortage']:<8}{entry['quantity']}"
            )

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
        print(f"{'주문번호':<14}{'시료ID':<8}{'고객명':<16}{'수량':<8}{'상태'}")
        for o in orders:
            print(
                f"{o['order_id']:<14}{o['sample_id']:<8}"
                f"{o['customer']:<16}{o['quantity']:<8}{o['status']}"
            )

    def show_samples(self, samples: list[dict]) -> None:
        if not samples:
            print("등록된 시료가 없습니다.")
            return
        print(f"{'ID':<8}{'이름':<20}{'평균생산시간':<14}{'수율':<8}{'재고':<8}")
        for s in samples:
            print(
                f"{s['sample_id']:<8}{s['name']:<20}"
                f"{s['avg_process_time']:<14}{s['yield_rate']:<8}{s['stock']:<8}"
            )
