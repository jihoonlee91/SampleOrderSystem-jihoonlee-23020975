import os
import tempfile

import pytest

from app.controllers.sample_controller import SampleController
from app.controllers.order_controller import (
    OrderController,
    SampleNotFoundError,
    InvalidQuantityError,
)
from app.repositories.sample_repository import SampleRepository
from app.repositories.order_repository import OrderRepository
from app.models.order import OrderStatus


def _setup():
    tmp_dir = tempfile.mkdtemp()
    sample_repo = SampleRepository(os.path.join(tmp_dir, "samples.json"))
    order_repo = OrderRepository(os.path.join(tmp_dir, "orders.json"))
    sample_controller = SampleController(sample_repo)
    order_controller = OrderController(order_repo, sample_controller)
    return sample_controller, order_controller


def test_reserve_order_for_existing_sample():
    sample_controller, order_controller = _setup()
    sample_controller.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)

    order = order_controller.reserve("S-001", "삼성전자 파운드리", 200)

    assert order["order_id"] == "ORD-0001"
    assert order["status"] == OrderStatus.RESERVED.value
    assert order["quantity"] == 200


def test_reserve_order_for_missing_sample_raises_error():
    _, order_controller = _setup()

    with pytest.raises(SampleNotFoundError):
        order_controller.reserve("S-999", "삼성전자 파운드리", 200)


def test_reserve_order_with_non_positive_quantity_raises_error():
    sample_controller, order_controller = _setup()
    sample_controller.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)

    with pytest.raises(InvalidQuantityError):
        order_controller.reserve("S-001", "삼성전자 파운드리", 0)


def test_multiple_reservations_auto_number_sequentially():
    sample_controller, order_controller = _setup()
    sample_controller.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)

    first = order_controller.reserve("S-001", "삼성전자 파운드리", 200)
    second = order_controller.reserve("S-001", "SK하이닉스", 100)

    assert first["order_id"] == "ORD-0001"
    assert second["order_id"] == "ORD-0002"


def test_list_all_returns_every_order():
    sample_controller, order_controller = _setup()
    sample_controller.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)
    order_controller.reserve("S-001", "고객A", 10)
    order_controller.reserve("S-001", "고객B", 20)

    assert len(order_controller.list_all()) == 2
