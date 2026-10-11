"""Casos de uso. Dependem de abstrações, nunca de implementações concretas."""
from datetime import datetime

from calculadora_fit.domain import services
from calculadora_fit.domain.entities import NutritionPlan, Profile
from calculadora_fit.domain.formulas import BMRFormula
from calculadora_fit.domain.repositories import PlanRecord, PlanRepository


class GeneratePlan:
    def __init__(
        self, formulas: dict[str, BMRFormula], repository: PlanRepository
    ) -> None:
        self._formulas = formulas
        self._repository = repository

    def execute(self, profile: Profile, formula_name: str = "mifflin") -> NutritionPlan:
        formula = self._formulas.get(formula_name)
        if formula is None:
            options = ", ".join(sorted(self._formulas))
            raise ValueError(f"Fórmula desconhecida: {formula_name}. Opções: {options}.")

        bmr = formula.bmr(profile)
        tdee = services.calculate_tdee(bmr, profile)
        calories = services.target_calories(tdee, profile.goal)
        bmi = services.calculate_bmi(profile.weight_kg, profile.height_cm)

        plan = NutritionPlan(
            bmi=bmi,
            bmi_category=services.classify_bmi(bmi),
            bmr=round(bmr),
            tdee=round(tdee),
            target_calories=calories,
            macros=services.calculate_macros(calories, profile),
        )
        self._repository.save(PlanRecord(datetime.now(), formula.name, profile, plan))
        return plan


class ListHistory:
    def __init__(self, repository: PlanRepository) -> None:
        self._repository = repository

    def execute(self) -> list[PlanRecord]:
        return self._repository.list_all()
