import copy
import json
import os
from typing import Any


class JsonStore:
    """단일 JSON 파일을 dict 레코드 리스트로 다루는 범용 저장소.

    파일은 최초 1회만 읽어 인메모리 캐시에 보관하고, 이후 조회는 캐시를 사용한다.
    쓰기(insert/update/delete)는 기본적으로 캐시를 갱신한 뒤 즉시 파일에 반영하여 영속성을
    유지한다. `flush=False`를 넘기면 캐시만 갱신하고 디스크 반영은 `flush()` 호출 시점으로
    미룰 수 있다(대량 쓰기 시 성능 개선용, 기본 동작은 변경되지 않는다).
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            self._write([])
        self._cache: list[dict[str, Any]] = self._read_from_disk()
        self._dirty = False

    def _read_from_disk(self) -> list[dict[str, Any]]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, records: list[dict[str, Any]]) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    def find_all(self) -> list[dict[str, Any]]:
        return copy.deepcopy(self._cache)

    def find_by_id(self, id_field: str, id_value: str) -> dict[str, Any] | None:
        for record in self._cache:
            if record.get(id_field) == id_value:
                return copy.deepcopy(record)
        return None

    def find_by_field(self, field: str, value: Any) -> list[dict[str, Any]]:
        return [copy.deepcopy(r) for r in self._cache if r.get(field) == value]

    def insert(self, record: dict[str, Any], flush: bool = True) -> None:
        self._cache.append(copy.deepcopy(record))
        self._mark_dirty(flush)

    def update(self, id_field: str, id_value: str, updates: dict[str, Any],
               flush: bool = True) -> bool:
        for record in self._cache:
            if record.get(id_field) == id_value:
                record.update(updates)
                self._mark_dirty(flush)
                return True
        return False

    def delete(self, id_field: str, id_value: str, flush: bool = True) -> bool:
        filtered = [r for r in self._cache if r.get(id_field) != id_value]
        if len(filtered) == len(self._cache):
            return False
        self._cache = filtered
        self._mark_dirty(flush)
        return True

    def _mark_dirty(self, flush: bool) -> None:
        self._dirty = True
        if flush:
            self.flush()

    def flush(self) -> None:
        if self._dirty:
            self._write(self._cache)
            self._dirty = False
