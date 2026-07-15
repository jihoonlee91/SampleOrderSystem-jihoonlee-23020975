from app.controllers.sample_controller import SampleController
from app.repositories.order_repository import OrderRepository


class SampleNotFoundError(Exception):
    """존재하지 않는 시료 ID로 주문을 시도할 때 발생한다."""


class InvalidQuantityError(Exception):
    """주문 수량이 0 이하일 때 발생한다."""


class OrderController:
    """주문 예약/조회를 담당한다."""

    def __init__(self, repository: OrderRepository, sample_controller: SampleController):
        self.repository = repository
        self.sample_controller = sample_controller

    def reserve(self, sample_id: str, customer: str, quantity: int) -> dict:
        if self.sample_controller.get(sample_id) is None:
            raise SampleNotFoundError(f"존재하지 않는 시료 ID입니다: {sample_id}")
        if quantity <= 0:
            raise InvalidQuantityError("주문 수량은 1 이상이어야 합니다.")
        return self.repository.create(sample_id, customer, quantity)

    def list_all(self) -> list[dict]:
        return self.repository.read_all()
