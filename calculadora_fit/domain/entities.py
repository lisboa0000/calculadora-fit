"""Entidades e regras de negócio. Esta camada não depende de nada externo."""
from dataclasses import dataclass
from enum import Enum


class Sex(Enum):
    MALE = "masculino"
    FEMALE = "feminino"


class ActivityLevel(Enum):
    SEDENTARY = 1.2
    LIGHT = 1.375
    MODERATE = 1.55
    INTENSE = 1.725
    ATHLETE = 1.9


class Goal(Enum):
    LOSE = "emagrecer"
    MAINTAIN = "manter"
    GAIN = "ganhar massa"


@dataclass(frozen=True)
class Profile:
    sex: Sex
    age: int
    weight_kg: float
    height_cm: float
    activity: ActivityLevel
    goal: Goal

    def __post_init__(self) -> None:
        if not 14 <= self.age <= 100:
            raise ValueError("A idade deve estar entre 14 e 100 anos.")
        if not 30 <= self.weight_kg <= 300:
            raise ValueError("O peso deve estar entre 30 e 300 kg.")
        if not 120 <= self.height_cm <= 250:
            raise ValueError("A altura deve estar entre 120 e 250 cm.")


@dataclass(frozen=True)
class Macros:
    protein_g: int
    fat_g: int
    carbs_g: int


@dataclass(frozen=True)
class NutritionPlan:
    bmi: float
    bmi_category: str
    bmr: float
    tdee: float
    target_calories: int
    macros: Macros
