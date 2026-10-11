import pytest

from calculadora_fit.domain import services
from calculadora_fit.domain.entities import ActivityLevel, Goal, Profile, Sex
from calculadora_fit.domain.formulas import FORMULAS, HarrisBenedict, MifflinStJeor


def make_profile(**overrides) -> Profile:
    data = dict(
        sex=Sex.MALE,
        age=30,
        weight_kg=80,
        height_cm=180,
        activity=ActivityLevel.MODERATE,
        goal=Goal.MAINTAIN,
    )
    data.update(overrides)
    return Profile(**data)


def test_mifflin_male():
    assert MifflinStJeor().bmr(make_profile()) == 1780


def test_mifflin_female():
    profile = make_profile(sex=Sex.FEMALE, age=25, weight_kg=60, height_cm=165)
    assert MifflinStJeor().bmr(profile) == 1345.25


def test_harris_male():
    assert HarrisBenedict().bmr(make_profile()) == pytest.approx(1853.632)


def test_formulas_registry_exposes_all_strategies():
    assert set(FORMULAS) == {"mifflin", "harris"}


@pytest.mark.parametrize(
    "bmi, category",
    [
        (17.0, "abaixo do peso"),
        (22.0, "peso normal"),
        (27.5, "sobrepeso"),
        (32.0, "obesidade"),
    ],
)
def test_bmi_classification(bmi, category):
    assert services.classify_bmi(bmi) == category


def test_bmi_calculation():
    assert services.calculate_bmi(80, 180) == 24.7


def test_tdee_uses_activity_factor():
    assert services.calculate_tdee(1780, make_profile()) == pytest.approx(2759)


@pytest.mark.parametrize(
    "goal, expected",
    [(Goal.LOSE, 2345), (Goal.MAINTAIN, 2759), (Goal.GAIN, 3035)],
)
def test_target_calories_by_goal(goal, expected):
    assert services.target_calories(2759, goal) == expected


def test_macros_add_up_to_target_calories():
    profile = make_profile(goal=Goal.GAIN)
    calories = 3035
    macros = services.calculate_macros(calories, profile)
    total = macros.protein_g * 4 + macros.carbs_g * 4 + macros.fat_g * 9
    assert total == pytest.approx(calories, abs=10)


@pytest.mark.parametrize(
    "field, value",
    [("age", 10), ("weight_kg", 10), ("height_cm", 80)],
)
def test_profile_rejects_invalid_values(field, value):
    with pytest.raises(ValueError):
        make_profile(**{field: value})
