import json
from datetime import datetime
from pathlib import Path

from calculadora_fit.domain.entities import (
    ActivityLevel,
    Goal,
    Macros,
    NutritionPlan,
    Profile,
    Sex,
)
from calculadora_fit.domain.repositories import PlanRecord, PlanRepository


class JsonPlanRepository(PlanRepository):
    def __init__(self, path: Path) -> None:
        self._path = path

    def save(self, record: PlanRecord) -> None:
        data = self._read()
        data.append(self._to_dict(record))
        self._path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def list_all(self) -> list[PlanRecord]:
        return [self._from_dict(item) for item in self._read()]

    def _read(self) -> list[dict]:
        if not self._path.exists():
            return []
        return json.loads(self._path.read_text(encoding="utf-8"))

    @staticmethod
    def _to_dict(record: PlanRecord) -> dict:
        p, plan = record.profile, record.plan
        return {
            "created_at": record.created_at.isoformat(timespec="seconds"),
            "formula": record.formula,
            "profile": {
                "sex": p.sex.name,
                "age": p.age,
                "weight_kg": p.weight_kg,
                "height_cm": p.height_cm,
                "activity": p.activity.name,
                "goal": p.goal.name,
            },
            "plan": {
                "bmi": plan.bmi,
                "bmi_category": plan.bmi_category,
                "bmr": plan.bmr,
                "tdee": plan.tdee,
                "target_calories": plan.target_calories,
                "macros": {
                    "protein_g": plan.macros.protein_g,
                    "fat_g": plan.macros.fat_g,
                    "carbs_g": plan.macros.carbs_g,
                },
            },
        }

    @staticmethod
    def _from_dict(item: dict) -> PlanRecord:
        p, plan = item["profile"], item["plan"]
        return PlanRecord(
            created_at=datetime.fromisoformat(item["created_at"]),
            formula=item["formula"],
            profile=Profile(
                sex=Sex[p["sex"]],
                age=p["age"],
                weight_kg=p["weight_kg"],
                height_cm=p["height_cm"],
                activity=ActivityLevel[p["activity"]],
                goal=Goal[p["goal"]],
            ),
            plan=NutritionPlan(
                bmi=plan["bmi"],
                bmi_category=plan["bmi_category"],
                bmr=plan["bmr"],
                tdee=plan["tdee"],
                target_calories=plan["target_calories"],
                macros=Macros(**plan["macros"]),
            ),
        )
