import json
import os
import tempfile

from app.repositories.json_store import JsonStore


def _store():
    tmp_dir = tempfile.mkdtemp()
    return JsonStore(os.path.join(tmp_dir, "data.json")), tmp_dir


def test_find_all_uses_cache_not_reread_from_disk():
    """캐시 생성 이후 파일을 외부에서 직접 변조해도, find_all() 결과는 캐시를 반영한다
    (매 호출마다 디스크를 다시 읽지 않는다는 것을 증명)."""
    store, tmp_dir = _store()
    store.insert({"id": "A", "value": 1})

    # 외부에서 파일을 직접 변조 (다른 프로세스가 손댄 상황을 흉내냄)
    path = store.file_path
    with open(path, "w", encoding="utf-8") as f:
        json.dump([{"id": "TAMPERED", "value": 999}], f)

    # 캐시를 쓰므로 방금 insert한 결과가 그대로 유지된다 (외부 변조가 즉시 반영되지 않음)
    assert store.find_all() == [{"id": "A", "value": 1}]


def test_returned_records_are_copies_not_live_cache_references():
    """find_all()로 받은 dict를 호출자가 직접 수정해도 내부 캐시는 오염되지 않는다."""
    store, _ = _store()
    store.insert({"id": "A", "value": 1})

    records = store.find_all()
    records[0]["value"] = 9999  # 호출자가 반환값을 직접 변경

    assert store.find_all()[0]["value"] == 1


def test_update_and_insert_still_persist_to_disk():
    """캐싱을 도입해도 쓰기 동작은 여전히 즉시 디스크에 반영되어야 한다(영속성 계약 유지)."""
    store, tmp_dir = _store()
    store.insert({"id": "A", "value": 1})
    store.update("id", "A", {"value": 2})

    # 새 인스턴스(프로세스 재시작을 흉내냄)로 다시 읽어도 반영되어 있어야 한다
    reloaded = JsonStore(store.file_path)
    assert reloaded.find_all() == [{"id": "A", "value": 2}]
