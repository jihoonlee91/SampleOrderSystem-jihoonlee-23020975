import os
import tempfile

import pytest

from app.controllers.sample_controller import SampleController, DuplicateSampleError
from app.repositories.sample_repository import SampleRepository


def _controller():
    tmp_dir = tempfile.mkdtemp()
    repo = SampleRepository(os.path.join(tmp_dir, "samples.json"))
    return SampleController(repo)


def test_register_then_list_includes_new_sample():
    controller = _controller()

    controller.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)

    samples = controller.list_all()
    assert len(samples) == 1
    assert samples[0]["sample_id"] == "S-001"


def test_register_duplicate_sample_id_raises_error():
    controller = _controller()
    controller.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)

    with pytest.raises(DuplicateSampleError):
        controller.register("S-001", "다른 이름", 0.1, 0.5, 0)


def test_search_returns_only_matching_samples():
    controller = _controller()
    controller.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)
    controller.register("S-002", "GaN 에피택셜-4인치", 0.3, 0.78, 220)

    results = controller.search("웨이퍼")

    assert len(results) == 1
    assert results[0]["sample_id"] == "S-001"


def test_get_sample_returns_none_when_not_found():
    controller = _controller()

    assert controller.get("S-999") is None
