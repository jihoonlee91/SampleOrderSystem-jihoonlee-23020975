from dataclasses import dataclass
from enum import Enum


class OrderStatus(str, Enum):
    RESERVED = "RESERVED"
    REJECTED = "REJECTED"
    PRODUCING = "PRODUCING"
    CONFIRMED = "CONFIRMED"
    RELEASE = "RELEASE"


@dataclass
class Order:
    order_id: str
    sample_id: str
    customer: str
    quantity: int
    status: OrderStatus = OrderStatus.RESERVED

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "sample_id": self.sample_id,
            "customer": self.customer,
            "quantity": self.quantity,
            "status": self.status.value,
        }

    @staticmethod
    def from_dict(data: dict) -> "Order":
        return Order(
            order_id=data["order_id"],
            sample_id=data["sample_id"],
            customer=data["customer"],
            quantity=data["quantity"],
            status=OrderStatus(data.get("status", "RESERVED")),
        )
