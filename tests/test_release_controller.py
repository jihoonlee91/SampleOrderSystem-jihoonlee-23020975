import os
import tempfile

import pytest

from app.controllers.sample_controller import SampleController
from app.controllers.order_controller import OrderController
from app.controllers.approval_controller import ApprovalController
from app.controllers.release_controller import ReleaseController
from app.controllers.errors import InvalidOrderStateError
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
    release_controller = ReleaseController(order_repo)
    return sample_controller, order_controller, approval_controller, release_controller


def test_list_confirmed_only_returns_confirmed_orders():
    sample_controller, order_controller, approval_controller, release_controller = _setup()
    sample_controller.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)
    confirmed_order = order_controller.reserve("S-001", "고객A", 100)
    reserved_order = order_controller.reserve("S-001", "고객B", 50)
    approval_controller.approve(confirmed_order["order_id"])

    confirmed_list = release_controller.list_confirmed()

    assert len(confirmed_list) == 1
    assert confirmed_list[0]["order_id"] == confirmed_order["order_id"]


def test_release_confirmed_order_sets_release_status():
    sample_controller, order_controller, approval_controller, release_controller = _setup()
    sample_controller.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)
    order = order_controller.reserve("S-001", "고객A", 100)
    approval_controller.approve(order["order_id"])

    released = release_controller.release(order["order_id"])

    assert released["status"] == OrderStatus.RELEASE.value


def test_release_non_confirmed_order_raises_error():
    sample_controller, order_controller, approval_controller, release_controller = _setup()
    sample_controller.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)
    order = order_controller.reserve("S-001", "고객A", 100)  # still RESERVED

    with pytest.raises(InvalidOrderStateError):
        release_controller.release(order["order_id"])


def test_release_already_released_order_raises_error():
    sample_controller, order_controller, approval_controller, release_controller = _setup()
    sample_controller.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)
    order = order_controller.reserve("S-001", "고객A", 100)
    approval_controller.approve(order["order_id"])
    release_controller.release(order["order_id"])

    with pytest.raises(InvalidOrderStateError):
        release_controller.release(order["order_id"])


def test_release_producing_order_raises_error():
    """재고 부족으로 아직 생산 중인(PRODUCING) 주문은 출고할 수 없다."""
    sample_controller, order_controller, approval_controller, release_controller = _setup()
    sample_controller.register("S-003", "SiC 파워기판-6인치", 0.8, 0.92, 10)
    order = order_controller.reserve("S-003", "고객A", 100)
    approval_controller.approve(order["order_id"])  # 재고 부족 -> PRODUCING

    with pytest.raises(InvalidOrderStateError):
        release_controller.release(order["order_id"])


def test_release_rejected_order_raises_error():
    sample_controller, order_controller, approval_controller, release_controller = _setup()
    sample_controller.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)
    order = order_controller.reserve("S-001", "고객A", 100)
    approval_controller.reject(order["order_id"])

    with pytest.raises(InvalidOrderStateError):
        release_controller.release(order["order_id"])
