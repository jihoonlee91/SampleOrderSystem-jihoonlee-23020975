from app.views.console_view import ConsoleView
from app.controllers.sample_controller import SampleController, DuplicateSampleError
from app.controllers.order_controller import (
    OrderController,
    SampleNotFoundError,
    InvalidQuantityError,
)
from app.repositories.sample_repository import SampleRepository
from app.repositories.order_repository import OrderRepository


class MainController:
    """메인 메뉴 루프를 담당하며 하위 Controller에 처리를 위임한다."""

    def __init__(self) -> None:
        self.view = ConsoleView()
        self.sample_controller = SampleController(SampleRepository())
        self.order_controller = OrderController(OrderRepository(), self.sample_controller)

    def run(self) -> None:
        actions = {
            "1": self._sample_menu,
            "2": self._reserve_order,
        }
        while True:
            self.view.show_main_menu()
            choice = self.view.prompt("선택")
            if choice == "0":
                self.view.show_message("종료합니다.")
                break
            action = actions.get(choice)
            if action is None:
                self.view.show_message("아직 지원하지 않거나 잘못된 선택입니다.")
                continue
            action()

    def _sample_menu(self) -> None:
        while True:
            self.view.show_sample_menu()
            choice = self.view.prompt("선택")
            if choice == "0":
                return
            elif choice == "1":
                self._register_sample()
            elif choice == "2":
                self.view.show_samples(self.sample_controller.list_all())
            elif choice == "3":
                keyword = self.view.prompt("검색어")
                self.view.show_samples(self.sample_controller.search(keyword))
            else:
                self.view.show_message("잘못된 선택입니다.")

    def _register_sample(self) -> None:
        try:
            sample_id = self.view.prompt("시료 ID")
            name = self.view.prompt("시료명")
            avg_time = float(self.view.prompt("평균 생산시간(분)"))
            yield_rate = float(self.view.prompt("수율(0~1)"))
            stock = int(self.view.prompt("초기 재고") or 0)
            self.sample_controller.register(sample_id, name, avg_time, yield_rate, stock)
            self.view.show_message(f"시료 '{name}' 등록 완료.")
        except DuplicateSampleError as e:
            self.view.show_message(str(e))
        except ValueError:
            self.view.show_message("입력 값이 올바르지 않습니다.")

    def _reserve_order(self) -> None:
        try:
            sample_id = self.view.prompt("시료 ID")
            customer = self.view.prompt("고객명")
            quantity = int(self.view.prompt("주문 수량"))
            order = self.order_controller.reserve(sample_id, customer, quantity)
            self.view.show_message(
                f"주문 '{order['order_id']}' 접수 완료. (상태: {order['status']})"
            )
        except (SampleNotFoundError, InvalidQuantityError) as e:
            self.view.show_message(str(e))
        except ValueError:
            self.view.show_message("입력 값이 올바르지 않습니다.")
