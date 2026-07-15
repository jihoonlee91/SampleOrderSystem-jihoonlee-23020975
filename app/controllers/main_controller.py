from app.views.console_view import ConsoleView
from app.controllers.sample_controller import SampleController, DuplicateSampleError
from app.controllers.order_controller import (
    OrderController,
    SampleNotFoundError,
    InvalidQuantityError,
)
from app.controllers.approval_controller import ApprovalController
from app.controllers.production_controller import ProductionController
from app.controllers.monitoring_controller import MonitoringController
from app.controllers.release_controller import ReleaseController
from app.controllers.errors import InvalidOrderStateError
from app.repositories.sample_repository import SampleRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.production_queue_repository import ProductionQueueRepository


class MainController:
    """메인 메뉴 루프를 담당하며 하위 Controller에 처리를 위임한다."""

    def __init__(self) -> None:
        self.view = ConsoleView()
        self.sample_controller = SampleController(SampleRepository())
        order_repository = OrderRepository()
        queue_repository = ProductionQueueRepository()
        self.order_controller = OrderController(order_repository, self.sample_controller)
        self.approval_controller = ApprovalController(
            order_repository, self.sample_controller, queue_repository
        )
        self.production_controller = ProductionController(
            queue_repository, order_repository, self.sample_controller
        )
        self.monitoring_controller = MonitoringController(order_repository, self.sample_controller)
        self.release_controller = ReleaseController(order_repository)

    def run(self) -> None:
        actions = {
            "1": self._sample_menu,
            "2": self._reserve_order,
            "3": self._approval_menu,
            "4": self._monitoring_menu,
            "5": self._production_menu,
            "6": self._release_menu,
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

    def _approval_menu(self) -> None:
        while True:
            self.view.show_approval_menu()
            reserved = self.approval_controller.list_reserved()
            self.view.show_orders(reserved)
            choice = self.view.prompt("선택")
            if choice == "0":
                return
            elif choice in ("1", "2"):
                order_id = self.view.prompt("주문번호")
                try:
                    if choice == "1":
                        order = self.approval_controller.approve(order_id)
                        self.view.show_message(f"승인 완료. 상태: {order['status']}")
                    else:
                        order = self.approval_controller.reject(order_id)
                        self.view.show_message(f"거절 완료. 상태: {order['status']}")
                except InvalidOrderStateError as e:
                    self.view.show_message(str(e))
            else:
                self.view.show_message("잘못된 선택입니다.")

    def _monitoring_menu(self) -> None:
        while True:
            self.view.show_monitoring_menu()
            choice = self.view.prompt("선택")
            if choice == "0":
                return
            elif choice == "1":
                self.view.show_order_counts(self.monitoring_controller.order_counts())
            elif choice == "2":
                self.view.show_stock_status(self.monitoring_controller.stock_status())
            else:
                self.view.show_message("잘못된 선택입니다.")

    def _release_menu(self) -> None:
        while True:
            self.view.show_release_menu()
            confirmed = self.release_controller.list_confirmed()
            self.view.show_orders(confirmed)
            choice = self.view.prompt("선택")
            if choice == "0":
                return
            elif choice == "1":
                order_id = self.view.prompt("주문번호")
                try:
                    order = self.release_controller.release(order_id)
                    self.view.show_message(f"출고 완료. 상태: {order['status']}")
                except InvalidOrderStateError as e:
                    self.view.show_message(str(e))
            else:
                self.view.show_message("잘못된 선택입니다.")

    def _production_menu(self) -> None:
        while True:
            self.view.show_production_menu()
            choice = self.view.prompt("선택")
            if choice == "0":
                return
            elif choice == "1":
                result = self.production_controller.process_next()
                if result is None:
                    self.view.show_message("생산 대기 중인 항목이 없습니다.")
                else:
                    self.view.show_production_result(result)
            elif choice == "2":
                self.view.show_production_queue(self.production_controller.list_queue())
            else:
                self.view.show_message("잘못된 선택입니다.")
