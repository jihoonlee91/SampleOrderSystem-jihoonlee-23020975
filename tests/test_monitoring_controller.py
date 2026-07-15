import os
import tempfile

from app.controllers.sample_controller import SampleController
from app.controllers.order_controller import OrderController
from app.controllers.approval_controller import ApprovalController
from app.controllers.monitoring_controller import MonitoringController
from app.repositories.sample_repository import SampleRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.production_queue_repository import ProductionQueueRepository


def _setup():
    tmp_dir = tempfile.mkdtemp()
    sample_repo = SampleRepository(os.path.join(tmp_dir, "samples.json"))
    order_repo = OrderRepository(os.path.join(tmp_dir, "orders.json"))
    queue_repo = ProductionQueueRepository(os.path.join(tmp_dir, "queue.json"))

    sample_controller = SampleController(sample_repo)
    order_controller = OrderController(order_repo, sample_controller)
    approval_controller = ApprovalController(order_repo, sample_controller, queue_repo)
    monitoring_controller = MonitoringController(order_repo, sample_controller)
    return sample_controller, order_controller, approval_controller, monitoring_controller


def test_order_counts_exclude_rejected():
    sample_controller, order_controller, approval_controller, monitoring_controller = _setup()
    sample_controller.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 1000)

    o1 = order_controller.reserve("S-001", "고객A", 10)
    o2 = order_controller.reserve("S-001", "고객B", 10)
    o3 = order_controller.reserve("S-001", "고객C", 10)
    approval_controller.approve(o1["order_id"])  # CONFIRMED (재고 충분)
    approval_controller.reject(o2["order_id"])   # REJECTED
    # o3는 RESERVED로 유지

    counts = monitoring_controller.order_counts()

    assert counts["RESERVED"] == 1
    assert counts["CONFIRMED"] == 1
    assert counts["PRODUCING"] == 0
    assert counts["RELEASE"] == 0
    assert "REJECTED" not in counts


def test_stock_status_classifies_correctly():
    sample_controller, _, _, monitoring_controller = _setup()
    sample_controller.register("S-001", "고갈시료", 0.5, 0.9, 0)
    sample_controller.register("S-002", "부족시료", 0.5, 0.9, 50)
    sample_controller.register("S-003", "여유시료", 0.5, 0.9, 100)

    statuses = {s["sample_id"]: s["status"] for s in monitoring_controller.stock_status()}

    assert statuses["S-001"] == "고갈"
    assert statuses["S-002"] == "부족"
    assert statuses["S-003"] == "여유"


def test_stock_status_empty_when_no_samples():
    _, _, _, monitoring_controller = _setup()

    assert monitoring_controller.stock_status() == []
