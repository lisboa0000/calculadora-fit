"""Porta de saída: o domínio define o contrato, a infraestrutura implementa."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from calculadora_fit.domain.entities import NutritionPlan, Profile


@dataclass(frozen=True)
class PlanRecord:
    created_at: datetime
    formula: str
    profile: Profile
    plan: NutritionPlan


class PlanRepository(ABC):
    @abstractmethod
    def save(self, record: PlanRecord) -> None: ...

    @abstractmethod
    def list_all(self) -> list[PlanRecord]: ...
