import os
import tempfile

from app.repositories.json_store import JsonStore


def _store():
    tmp_dir = tempfile.mkdtemp()
    return JsonStore(os.path.join(tmp_dir, "data.json"))


def test_update_returns_false_when_id_not_found():
    store = _store()
    store.insert({"id": "A", "value": 1})

    assert store.update("id", "MISSING", {"value": 2}) is False


def test_delete_returns_false_when_id_not_found():
    store = _store()
    store.insert({"id": "A", "value": 1})

    assert store.delete("id", "MISSING") is False
    assert len(store.find_all()) == 1


def test_delete_removes_matching_record():
    store = _store()
    store.insert({"id": "A", "value": 1})
    store.insert({"id": "B", "value": 2})

    assert store.delete("id", "A") is True
    remaining = store.find_all()
    assert len(remaining) == 1
    assert remaining[0]["id"] == "B"
