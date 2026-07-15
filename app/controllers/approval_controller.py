from app.controllers.sample_controller import SampleController
from app.controllers.errors import InvalidOrderStateError
from app.repositories.order_repository import OrderRepository
from app.repositories.production_queue_repository import ProductionQueueRepository
from app.models.order import OrderStatus


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
            # 현재 재고 전량을 이 주문에 즉시 소진 처리한다. 그래야 같은 시료에 대해
            # 재고 부족 상태로 대기 중인 다른 주문이 이미 소진된 재고를 중복으로
            # 계산하지 않는다(동시 승인 시 재고 이중 계산 방지).
            if sample["stock"] > 0:
                self.sample_controller.repository.adjust_stock(order["sample_id"], -sample["stock"])
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
