from app.repositories.sample_repository import SampleRepository


class DuplicateSampleError(Exception):
    """이미 존재하는 sample_id로 등록을 시도할 때 발생한다."""


class InvalidSampleDataError(Exception):
    """시료 등록 값이 유효 범위를 벗어날 때 발생한다."""


class SampleController:
    """시료 등록/조회/검색을 담당한다. View에 의존하지 않아 단위 테스트가 가능하다."""

    def __init__(self, repository: SampleRepository):
        self.repository = repository

    def register(self, sample_id: str, name: str, avg_process_time: float,
                 yield_rate: float, stock: int = 0) -> dict:
        if self.repository.read(sample_id) is not None:
            raise DuplicateSampleError(f"이미 존재하는 시료 ID입니다: {sample_id}")
        self._validate(avg_process_time, yield_rate, stock)
        return self.repository.create(sample_id, name, avg_process_time, yield_rate, stock)

    @staticmethod
    def _validate(avg_process_time: float, yield_rate: float, stock: int) -> None:
        if not (0 < yield_rate <= 1):
            raise InvalidSampleDataError("수율(yield_rate)은 0보다 크고 1 이하여야 합니다.")
        if avg_process_time <= 0:
            raise InvalidSampleDataError("평균 생산시간은 0보다 커야 합니다.")
        if stock < 0:
            raise InvalidSampleDataError("재고는 0 이상이어야 합니다.")

    def list_all(self) -> list[dict]:
        return self.repository.read_all()

    def search(self, keyword: str) -> list[dict]:
        return self.repository.search_by_name(keyword)

    def get(self, sample_id: str) -> dict | None:
        return self.repository.read(sample_id)
