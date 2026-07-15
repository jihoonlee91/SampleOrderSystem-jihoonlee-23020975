import os
import tempfile

from app.repositories.sample_repository import SampleRepository
from app.repositories.order_repository import OrderRepository


def test_sample_data_persists_across_new_repository_instances():
    tmp_dir = tempfile.mkdtemp()
    path = os.path.join(tmp_dir, "samples.json")

    first = SampleRepository(path)
    first.create("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)

    # 새 인스턴스 생성 = 프로세스 재시작을 흉내낸다.
    second = SampleRepository(path)
    assert second.read("S-001")["stock"] == 480


def test_order_data_persists_across_new_repository_instances():
    tmp_dir = tempfile.mkdtemp()
    path = os.path.join(tmp_dir, "orders.json")

    first = OrderRepository(path)
    first.create("S-001", "삼성전자 파운드리", 200)

    second = OrderRepository(path)
    assert len(second.read_all()) == 1
    assert second.read_all()[0]["order_id"] == "ORD-0001"
