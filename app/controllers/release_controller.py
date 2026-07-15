from app.controllers.errors import InvalidOrderStateError
from app.repositories.order_repository import OrderRepository
from app.models.order import OrderStatus


class ReleaseController:
    """CONFIRMED 주문에 대한 출고 처리를 담당한다."""

    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def list_confirmed(self) -> list[dict]:
        return self.order_repository.find_by_status(OrderStatus.CONFIRMED.value)

    def release(self, order_id: str) -> dict:
        order = self.order_repository.read(order_id)
        if order is None or order["status"] != OrderStatus.CONFIRMED.value:
            raise InvalidOrderStateError(f"CONFIRMED 상태의 주문이 아닙니다: {order_id}")
        self.order_repository.update_status(order_id, OrderStatus.RELEASE.value)
        return self.order_repository.read(order_id)
