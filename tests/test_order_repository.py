import os
import tempfile

from app.repositories.order_repository import OrderRepository
from app.models.order import OrderStatus


def _repo():
    tmp_dir = tempfile.mkdtemp()
    return OrderRepository(os.path.join(tmp_dir, "orders.json"))


def test_create_order_defaults_to_reserved_and_auto_numbers():
    repo = _repo()

    order = repo.create("S-001", "삼성전자 파운드리", 200)

    assert order["status"] == OrderStatus.RESERVED.value
    assert order["order_id"] == "ORD-0001"

    second = repo.create("S-002", "SK하이닉스", 100)
    assert second["order_id"] == "ORD-0002"


def test_update_status_changes_only_target_order():
    repo = _repo()
    repo.create("S-001", "삼성전자 파운드리", 200)
    repo.create("S-002", "SK하이닉스", 100)

    repo.update_status("ORD-0001", OrderStatus.CONFIRMED.value)

    assert repo.read("ORD-0001")["status"] == OrderStatus.CONFIRMED.value
    assert repo.read("ORD-0002")["status"] == OrderStatus.RESERVED.value


def test_find_by_status_filters_correctly():
    repo = _repo()
    repo.create("S-001", "삼성전자 파운드리", 200)
    repo.create("S-002", "SK하이닉스", 100)
    repo.update_status("ORD-0001", OrderStatus.CONFIRMED.value)

    reserved = repo.find_by_status(OrderStatus.RESERVED.value)
    confirmed = repo.find_by_status(OrderStatus.CONFIRMED.value)

    assert len(reserved) == 1
    assert reserved[0]["order_id"] == "ORD-0002"
    assert len(confirmed) == 1
    assert confirmed[0]["order_id"] == "ORD-0001"
