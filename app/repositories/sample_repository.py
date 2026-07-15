from app.repositories.json_store import JsonStore


class SampleRepository:
    """시료(Sample) 데이터에 대한 CRUD 및 재고 조정을 담당한다."""

    def __init__(self, file_path: str = "data/samples.json"):
        self.store = JsonStore(file_path)

    def create(self, sample_id: str, name: str, avg_process_time: float,
               yield_rate: float, stock: int = 0) -> dict:
        record = {
            "sample_id": sample_id,
            "name": name,
            "avg_process_time": avg_process_time,
            "yield_rate": yield_rate,
            "stock": stock,
        }
        self.store.insert(record)
        return record

    def read_all(self) -> list[dict]:
        return self.store.find_all()

    def read(self, sample_id: str) -> dict | None:
        return self.store.find_by_id("sample_id", sample_id)

    def search_by_name(self, keyword: str) -> list[dict]:
        return [s for s in self.read_all() if keyword in s["name"]]

    def adjust_stock(self, sample_id: str, delta: int) -> bool:
        sample = self.read(sample_id)
        if sample is None:
            return False
        new_stock = sample["stock"] + delta
        return self.store.update("sample_id", sample_id, {"stock": new_stock})
