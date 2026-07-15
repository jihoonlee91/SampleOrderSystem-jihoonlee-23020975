from dataclasses import dataclass


@dataclass
class Sample:
    sample_id: str
    name: str
    avg_process_time: float
    yield_rate: float
    stock: int = 0

    def to_dict(self) -> dict:
        return {
            "sample_id": self.sample_id,
            "name": self.name,
            "avg_process_time": self.avg_process_time,
            "yield_rate": self.yield_rate,
            "stock": self.stock,
        }

    @staticmethod
    def from_dict(data: dict) -> "Sample":
        return Sample(
            sample_id=data["sample_id"],
            name=data["name"],
            avg_process_time=data["avg_process_time"],
            yield_rate=data["yield_rate"],
            stock=data.get("stock", 0),
        )
