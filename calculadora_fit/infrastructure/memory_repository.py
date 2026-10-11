from calculadora_fit.domain.repositories import PlanRecord, PlanRepository


class InMemoryPlanRepository(PlanRepository):
    def __init__(self) -> None:
        self._records: list[PlanRecord] = []

    def save(self, record: PlanRecord) -> None:
        self._records.append(record)

    def list_all(self) -> list[PlanRecord]:
        return list(self._records)
