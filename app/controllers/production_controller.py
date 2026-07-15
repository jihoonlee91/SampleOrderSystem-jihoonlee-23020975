import math

from app.controllers.sample_controller import SampleController
from app.repositories.order_repository import OrderRepository
from app.repositories.production_queue_repository import ProductionQueueRepository
from app.models.order import OrderStatus


class ProductionController:
    """생산 큐(FIFO)를 처리하여 부족분을 생산하고 주문을 CONFIRMED로 전환한다."""

    def __init__(self, queue_repository: ProductionQueueRepository,
                 order_repository: OrderRepository, sample_controller: SampleController):
        self.queue_repository = queue_repository
        self.order_repository = order_repository
        self.sample_controller = sample_controller

    def list_queue(self) -> list[dict]:
        return self.queue_repository.find_all()

    def process_next(self) -> dict | None:
        entry = self.queue_repository.dequeue_front()
        if entry is None:
            return None

        sample = self.sample_controller.get(entry["sample_id"])
        shortage = entry["shortage"]
        actual_quantity = math.ceil(shortage / sample["yield_rate"])
        total_time = sample["avg_process_time"] * actual_quantity

        # 생산된 만큼 재고에 더하고, 주문 수량 전체를 출고 대기로 확정(소진)한다.
        # 순증감 = 실 생산량 - 주문 수량 (기존 재고 중 이미 확보된 부분 + 신규 생산분 - 주문 소진량)
        self.sample_controller.repository.adjust_stock(
            entry["sample_id"], actual_quantity - entry["quantity"]
        )
        self.order_repository.update_status(entry["order_id"], OrderStatus.CONFIRMED.value)

        return {
            "order_id": entry["order_id"],
            "sample_id": entry["sample_id"],
            "shortage": shortage,
            "actual_quantity": actual_quantity,
            "total_time": total_time,
        }
