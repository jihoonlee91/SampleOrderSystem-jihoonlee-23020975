"""
동시성/중복 재고 계산 버그 재현 테스트

같은 시료에 대해 재고 부족 주문이 2건 이상 대기 중일 때, 각 주문의 부족분이 동일한
"승인 시점 재고"를 기준으로 중복 계산되어 최종 재고가 음수가 되는 문제를 검증한다.
(사용자 승인 하에 발견 및 수정 - docs/REPORT.md 참고)
"""
import math
import os
import tempfile

from app.controllers.sample_controller import SampleController
from app.controllers.order_controller import OrderController
from app.controllers.approval_controller import ApprovalController
from app.controllers.production_controller import ProductionController
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
    production_controller = ProductionController(queue_repo, order_repo, sample_controller)
    return sample_controller, order_controller, approval_controller, production_controller


def test_two_concurrent_insufficient_orders_never_produce_negative_stock():
    sample_controller, order_controller, approval_controller, production_controller = _setup()
    sample_controller.register("S-003", "SiC 파워기판-6인치", 0.8, 0.92, 30)

    order_a = order_controller.reserve("S-003", "고객A", 200)
    order_b = order_controller.reserve("S-003", "고객B", 100)
    approval_controller.approve(order_a["order_id"])
    approval_controller.approve(order_b["order_id"])

    production_controller.process_next()
    production_controller.process_next()

    assert sample_controller.get("S-003")["stock"] >= 0


def test_two_concurrent_insufficient_orders_final_stock_is_exact():
    sample_controller, order_controller, approval_controller, production_controller = _setup()
    sample_controller.register("S-003", "SiC 파워기판-6인치", 0.8, 0.92, 30)

    order_a = order_controller.reserve("S-003", "고객A", 200)
    order_b = order_controller.reserve("S-003", "고객B", 100)
    approval_controller.approve(order_a["order_id"])  # shortage=170 (재고 30 기준)
    approval_controller.approve(order_b["order_id"])  # 재고가 이미 소진 처리되어 shortage=100

    production_controller.process_next()  # A: actual=ceil(170/0.92)=185
    production_controller.process_next()  # B: actual=ceil(100/0.92)=109

    actual_a = math.ceil(170 / 0.92)
    actual_b = math.ceil(100 / 0.92)
    # 두 주문 모두 정확히 필요한 만큼만 생산되고, 남는 잉여(반올림 초과분)만 재고로 남는다.
    expected_stock = (actual_a - 170) + (actual_b - 100)
    assert sample_controller.get("S-003")["stock"] == expected_stock


def test_three_concurrent_insufficient_orders_never_produce_negative_stock():
    """독립 검증(SubAgent)에서 제안된 3건 이상 동시 대기 시나리오를 정식 회귀 테스트로 고정한다."""
    sample_controller, order_controller, approval_controller, production_controller = _setup()
    sample_controller.register("S-003", "SiC 파워기판-6인치", 0.8, 0.92, 30)

    orders = [
        order_controller.reserve("S-003", f"고객{i}", quantity)
        for i, quantity in enumerate([200, 100, 50])
    ]
    for order in orders:
        approval_controller.approve(order["order_id"])

    while production_controller.process_next() is not None:
        pass

    assert sample_controller.get("S-003")["stock"] >= 0


def test_mixed_sample_queue_preserves_fifo_order_and_avoids_negative_stock():
    """서로 다른 시료 주문이 큐에 섞여 있어도 등록 순서(FIFO)가 유지되고 재고가 음수가 되지 않는다."""
    sample_controller, order_controller, approval_controller, production_controller = _setup()
    sample_controller.register("S-A", "시료A", 0.5, 0.9, 10)
    sample_controller.register("S-B", "시료B", 0.5, 0.9, 10)

    order_1 = order_controller.reserve("S-A", "고객1", 100)
    order_2 = order_controller.reserve("S-B", "고객2", 100)
    order_3 = order_controller.reserve("S-A", "고객3", 50)
    approval_controller.approve(order_1["order_id"])
    approval_controller.approve(order_2["order_id"])
    approval_controller.approve(order_3["order_id"])

    queue_order = [entry["order_id"] for entry in production_controller.list_queue()]
    assert queue_order == [order_1["order_id"], order_2["order_id"], order_3["order_id"]]

    while production_controller.process_next() is not None:
        pass

    assert sample_controller.get("S-A")["stock"] >= 0
    assert sample_controller.get("S-B")["stock"] >= 0
