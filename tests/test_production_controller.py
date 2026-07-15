import os
import tempfile
import math

from app.controllers.sample_controller import SampleController
from app.controllers.order_controller import OrderController
from app.controllers.approval_controller import ApprovalController
from app.controllers.production_controller import ProductionController
from app.repositories.sample_repository import SampleRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.production_queue_repository import ProductionQueueRepository
from app.models.order import OrderStatus


def _setup():
    tmp_dir = tempfile.mkdtemp()
    sample_repo = SampleRepository(os.path.join(tmp_dir, "samples.json"))
    order_repo = OrderRepository(os.path.join(tmp_dir, "orders.json"))
    queue_repo = ProductionQueueRepository(os.path.join(tmp_dir, "queue.json"))

    sample_controller = SampleController(sample_repo)
    order_controller = OrderController(order_repo, sample_controller)
    approval_controller = ApprovalController(order_repo, sample_controller, queue_repo)
    production_controller = ProductionController(queue_repo, order_repo, sample_controller)
    return sample_controller, order_controller, approval_controller, production_controller


def test_process_next_calculates_actual_quantity_and_time():
    sample_controller, order_controller, approval_controller, production_controller = _setup()
    sample_controller.register("S-003", "SiC 파워기판-6인치", 0.8, 0.92, 30)
    order = order_controller.reserve("S-003", "삼성전자 파운드리", 200)
    approval_controller.approve(order["order_id"])  # PRODUCING, shortage=170

    result = production_controller.process_next()

    expected_actual = math.ceil(170 / 0.92)
    assert result["actual_quantity"] == expected_actual
    assert result["total_time"] == 0.8 * expected_actual


def test_process_next_confirms_order_and_updates_stock():
    sample_controller, order_controller, approval_controller, production_controller = _setup()
    sample_controller.register("S-003", "SiC 파워기판-6인치", 0.8, 0.92, 30)
    order = order_controller.reserve("S-003", "삼성전자 파운드리", 200)
    approval_controller.approve(order["order_id"])

    production_controller.process_next()

    updated_order = order_controller.repository.read(order["order_id"])
    assert updated_order["status"] == OrderStatus.CONFIRMED.value

    expected_actual = math.ceil(170 / 0.92)
    expected_stock = 30 + expected_actual - 200  # 기존 재고 + 실생산량 - 주문수량(소진)
    assert sample_controller.get("S-003")["stock"] == expected_stock


def test_process_next_returns_none_when_queue_empty():
    _, _, _, production_controller = _setup()

    result = production_controller.process_next()

    assert result is None


def test_list_queue_returns_fifo_order():
    sample_controller, order_controller, approval_controller, production_controller = _setup()
    sample_controller.register("S-003", "SiC 파워기판-6인치", 0.8, 0.92, 0)
    first_order = order_controller.reserve("S-003", "고객A", 100)
    second_order = order_controller.reserve("S-003", "고객B", 50)
    approval_controller.approve(first_order["order_id"])
    approval_controller.approve(second_order["order_id"])

    queue = production_controller.list_queue()

    assert len(queue) == 2
    assert queue[0]["order_id"] == first_order["order_id"]
    assert queue[1]["order_id"] == second_order["order_id"]
