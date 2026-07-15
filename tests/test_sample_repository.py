import os
import tempfile

from app.repositories.sample_repository import SampleRepository


def _repo():
    tmp_dir = tempfile.mkdtemp()
    return SampleRepository(os.path.join(tmp_dir, "samples.json"))


def test_create_and_read_sample():
    repo = _repo()
    repo.create("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)

    sample = repo.read("S-001")

    assert sample["sample_id"] == "S-001"
    assert sample["name"] == "실리콘 웨이퍼-8인치"
    assert sample["avg_process_time"] == 0.5
    assert sample["yield_rate"] == 0.92
    assert sample["stock"] == 480


def test_read_all_returns_every_sample():
    repo = _repo()
    repo.create("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)
    repo.create("S-002", "GaN 에피택셜-4인치", 0.3, 0.78, 220)

    samples = repo.read_all()

    assert len(samples) == 2


def test_adjust_stock_increases_and_decreases():
    repo = _repo()
    repo.create("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 100)

    repo.adjust_stock("S-001", 50)
    assert repo.read("S-001")["stock"] == 150

    repo.adjust_stock("S-001", -30)
    assert repo.read("S-001")["stock"] == 120


def test_search_by_name_keyword():
    repo = _repo()
    repo.create("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)
    repo.create("S-002", "GaN 에피택셜-4인치", 0.3, 0.78, 220)

    results = repo.search_by_name("웨이퍼")

    assert len(results) == 1
    assert results[0]["sample_id"] == "S-001"


def test_adjust_stock_returns_false_for_missing_sample():
    repo = _repo()

    assert repo.adjust_stock("S-NOPE", 10) is False
