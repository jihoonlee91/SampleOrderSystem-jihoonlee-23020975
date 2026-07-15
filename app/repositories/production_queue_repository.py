from app.repositories.json_store import JsonStore


class ProductionQueueRepository:
    """생산 큐(FIFO 대기열) 데이터를 관리한다. 큐 처리 자체는 Phase 5에서 다룬다."""

    def __init__(self, file_path: str = "data/production_queue.json"):
        self.store = JsonStore(file_path)

    def enqueue(self, order_id: str, sample_id: str, shortage: int) -> dict:
        record = {"order_id": order_id, "sample_id": sample_id, "shortage": shortage}
        self.store.insert(record)
        return record

    def find_all(self) -> list[dict]:
        return self.store.find_all()

    def dequeue_front(self) -> dict | None:
        entries = self.store.find_all()
        if not entries:
            return None
        front = entries[0]
        self.store.delete("order_id", front["order_id"])
        return front
