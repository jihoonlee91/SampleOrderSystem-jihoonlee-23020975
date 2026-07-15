from app.controllers.sample_controller import SampleController
from app.repositories.order_repository import OrderRepository
from app.repositories.production_queue_repository import ProductionQueueRepository
from app.models.order import OrderStatus


class InvalidOrderStateError(Exception):
    """RESERVED가 아닌 주문에 승인/거절을 시도할 때 발생한다."""


class ApprovalController:
    """RESERVED 주문에 대한 승인/거절을 담당한다."""

    def __init__(self, order_repository: OrderRepository, sample_controller: SampleController,
                 queue_repository: ProductionQueueRepository):
        self.order_repository = order_repository
        self.sample_controller = sample_controller
        self.queue_repository = queue_repository

    def list_reserved(self) -> list[dict]:
        return self.order_repository.find_by_status(OrderStatus.RESERVED.value)

    def approve(self, order_id: str) -> dict:
        order = self._require_reserved(order_id)
        sample = self.sample_controller.get(order["sample_id"])
        quantity = order["quantity"]

        if sample["stock"] >= quantity:
            self.sample_controller.repository.adjust_stock(order["sample_id"], -quantity)
            self.order_repository.update_status(order_id, OrderStatus.CONFIRMED.value)
        else:
            shortage = quantity - sample["stock"]
            self.queue_repository.enqueue(order_id, order["sample_id"], shortage, quantity)
            self.order_repository.update_status(order_id, OrderStatus.PRODUCING.value)

        return self.order_repository.read(order_id)

    def reject(self, order_id: str) -> dict:
        self._require_reserved(order_id)
        self.order_repository.update_status(order_id, OrderStatus.REJECTED.value)
        return self.order_repository.read(order_id)

    def _require_reserved(self, order_id: str) -> dict:
        order = self.order_repository.read(order_id)
        if order is None or order["status"] != OrderStatus.RESERVED.value:
            raise InvalidOrderStateError(f"RESERVED 상태의 주문이 아닙니다: {order_id}")
        return order
