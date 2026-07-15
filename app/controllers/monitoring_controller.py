from app.controllers.sample_controller import SampleController
from app.repositories.order_repository import OrderRepository
from app.models.order import OrderStatus

MONITORED_STATUSES = [
    OrderStatus.RESERVED,
    OrderStatus.CONFIRMED,
    OrderStatus.PRODUCING,
    OrderStatus.RELEASE,
]


def _stock_state(stock: int) -> str:
    if stock == 0:
        return "고갈"
    if stock < 100:
        return "부족"
    return "여유"


class MonitoringController:
    """상태별 주문 수(REJECTED 제외)와 시료별 재고 상태를 조회한다."""

    def __init__(self, order_repository: OrderRepository, sample_controller: SampleController):
        self.order_repository = order_repository
        self.sample_controller = sample_controller

    def order_counts(self) -> dict:
        return {
            status.value: len(self.order_repository.find_by_status(status.value))
            for status in MONITORED_STATUSES
        }

    def stock_status(self) -> list[dict]:
        return [
            {**sample, "status": _stock_state(sample["stock"])}
            for sample in self.sample_controller.list_all()
        ]
