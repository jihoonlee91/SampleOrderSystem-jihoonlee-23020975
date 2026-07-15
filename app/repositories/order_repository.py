from app.models.order import OrderStatus
from app.repositories.json_store import JsonStore


class OrderRepository:
    """주문(Order) 데이터에 대한 CRUD, 자동 채번, 상태 필터 조회를 담당한다."""

    def __init__(self, file_path: str = "data/orders.json"):
        self.store = JsonStore(file_path)

    def _next_order_id(self) -> str:
        max_seq = 0
        for record in self.store.find_all():
            digits = "".join(ch for ch in record["order_id"] if ch.isdigit())
            if digits:
                max_seq = max(max_seq, int(digits))
        return f"ORD-{max_seq + 1:04d}"

    def create(self, sample_id: str, customer: str, quantity: int) -> dict:
        record = {
            "order_id": self._next_order_id(),
            "sample_id": sample_id,
            "customer": customer,
            "quantity": quantity,
            "status": OrderStatus.RESERVED.value,
        }
        self.store.insert(record)
        return record

    def read_all(self) -> list[dict]:
        return self.store.find_all()

    def read(self, order_id: str) -> dict | None:
        return self.store.find_by_id("order_id", order_id)

    def update_status(self, order_id: str, status: str) -> bool:
        return self.store.update("order_id", order_id, {"status": status})

    def find_by_status(self, status: str) -> list[dict]:
        return self.store.find_by_field("status", status)
