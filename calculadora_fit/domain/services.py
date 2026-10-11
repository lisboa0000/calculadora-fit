"""Regras puras de cálculo, sem I/O."""
from calculadora_fit.domain.entities import Goal, Macros, Profile

CALORIE_ADJUSTMENT = {Goal.LOSE: 0.85, Goal.MAINTAIN: 1.0, Goal.GAIN: 1.10}
PROTEIN_G_PER_KG = {Goal.LOSE: 2.0, Goal.MAINTAIN: 1.6, Goal.GAIN: 1.8}
FAT_SHARE_OF_CALORIES = 0.25

KCAL_PER_G_PROTEIN = 4
KCAL_PER_G_CARBS = 4
KCAL_PER_G_FAT = 9


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    return round(weight_kg / (height_cm / 100) ** 2, 1)


def classify_bmi(bmi: float) -> str:
    """Classificação da OMS para adultos."""
    if bmi < 18.5:
        return "abaixo do peso"
    if bmi < 25:
        return "peso normal"
    if bmi < 30:
        return "sobrepeso"
    return "obesidade"


def calculate_tdee(bmr: float, profile: Profile) -> float:
    return bmr * profile.activity.value


def target_calories(tdee: float, goal: Goal) -> int:
    return round(tdee * CALORIE_ADJUSTMENT[goal])


def calculate_macros(calories: int, profile: Profile) -> Macros:
    protein = round(profile.weight_kg * PROTEIN_G_PER_KG[profile.goal])
    fat = round(calories * FAT_SHARE_OF_CALORIES / KCAL_PER_G_FAT)
    remaining = calories - protein * KCAL_PER_G_PROTEIN - fat * KCAL_PER_G_FAT
    carbs = max(0, round(remaining / KCAL_PER_G_CARBS))
    return Macros(protein_g=protein, fat_g=fat, carbs_g=carbs)
