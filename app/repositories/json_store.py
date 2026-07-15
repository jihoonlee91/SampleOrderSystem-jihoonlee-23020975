import json
import os
from typing import Any


class JsonStore:
    """단일 JSON 파일을 dict 레코드 리스트로 다루는 범용 저장소."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            self._write([])

    def _read(self) -> list[dict[str, Any]]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, records: list[dict[str, Any]]) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    def find_all(self) -> list[dict[str, Any]]:
        return self._read()

    def find_by_id(self, id_field: str, id_value: str) -> dict[str, Any] | None:
        for record in self._read():
            if record.get(id_field) == id_value:
                return record
        return None

    def find_by_field(self, field: str, value: Any) -> list[dict[str, Any]]:
        return [r for r in self._read() if r.get(field) == value]

    def insert(self, record: dict[str, Any]) -> None:
        records = self._read()
        records.append(record)
        self._write(records)

    def update(self, id_field: str, id_value: str, updates: dict[str, Any]) -> bool:
        records = self._read()
        for record in records:
            if record.get(id_field) == id_value:
                record.update(updates)
                self._write(records)
                return True
        return False

    def delete(self, id_field: str, id_value: str) -> bool:
        records = self._read()
        filtered = [r for r in records if r.get(id_field) != id_value]
        if len(filtered) == len(records):
            return False
        self._write(filtered)
        return True
