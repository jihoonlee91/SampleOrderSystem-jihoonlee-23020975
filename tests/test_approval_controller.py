import os
import tempfile

import pytest

from app.controllers.sample_controller import SampleController
from app.controllers.order_controller import OrderController
from app.controllers.approval_controller import ApprovalController, InvalidOrderStateError
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
    return sample_controller, order_controller, approval_controller


def test_approve_with_sufficient_stock_confirms_and_deducts_stock():
    sample_controller, order_controller, approval_controller = _setup()
    sample_controller.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)
    order = order_controller.reserve("S-001", "삼성전자 파운드리", 200)

    approval_controller.approve(order["order_id"])

    updated_order = order_controller.repository.read(order["order_id"])
    assert updated_order["status"] == OrderStatus.CONFIRMED.value
    assert sample_controller.get("S-001")["stock"] == 280


def test_approve_with_insufficient_stock_enqueues_and_sets_producing():
    sample_controller, order_controller, approval_controller = _setup()
    sample_controller.register("S-003", "SiC 파워기판-6인치", 0.8, 0.92, 30)
    order = order_controller.reserve("S-003", "삼성전자 파운드리", 200)

    approval_controller.approve(order["order_id"])

    updated_order = order_controller.repository.read(order["order_id"])
    assert updated_order["status"] == OrderStatus.PRODUCING.value
    # 재고 부족 시에는 아직 재고를 차감하지 않는다 (생산 완료 후 Phase 5에서 처리)
    assert sample_controller.get("S-003")["stock"] == 30

    queue_entries = approval_controller.queue_repository.find_all()
    assert len(queue_entries) == 1
    assert queue_entries[0]["order_id"] == order["order_id"]
    assert queue_entries[0]["shortage"] == 170


def test_approve_with_stock_exactly_equal_to_quantity_confirms():
    sample_controller, order_controller, approval_controller = _setup()
    sample_controller.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 200)
    order = order_controller.reserve("S-001", "삼성전자 파운드리", 200)

    approval_controller.approve(order["order_id"])

    updated_order = order_controller.repository.read(order["order_id"])
    assert updated_order["status"] == OrderStatus.CONFIRMED.value
    assert sample_controller.get("S-001")["stock"] == 0


def test_reject_sets_rejected_and_does_not_touch_stock():
    sample_controller, order_controller, approval_controller = _setup()
    sample_controller.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)
    order = order_controller.reserve("S-001", "삼성전자 파운드리", 200)

    approval_controller.reject(order["order_id"])

    updated_order = order_controller.repository.read(order["order_id"])
    assert updated_order["status"] == OrderStatus.REJECTED.value
    assert sample_controller.get("S-001")["stock"] == 480


def test_approve_non_reserved_order_raises_error():
    sample_controller, order_controller, approval_controller = _setup()
    sample_controller.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)
    order = order_controller.reserve("S-001", "삼성전자 파운드리", 200)
    approval_controller.approve(order["order_id"])

    with pytest.raises(InvalidOrderStateError):
        approval_controller.approve(order["order_id"])
