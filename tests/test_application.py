from pathlib import Path

import pytest

from calculadora_fit.application.use_cases import GeneratePlan, ListHistory
from calculadora_fit.domain.entities import ActivityLevel, Goal, Profile, Sex
from calculadora_fit.domain.formulas import FORMULAS
from calculadora_fit.infrastructure.json_repository import JsonPlanRepository
from calculadora_fit.infrastructure.memory_repository import InMemoryPlanRepository


@pytest.fixture
def profile() -> Profile:
    return Profile(
        sex=Sex.MALE,
        age=30,
        weight_kg=80,
        height_cm=180,
        activity=ActivityLevel.MODERATE,
        goal=Goal.MAINTAIN,
    )


def test_generate_plan_returns_expected_numbers(profile):
    plan = GeneratePlan(FORMULAS, InMemoryPlanRepository()).execute(profile)

    assert plan.bmr == 1780
    assert plan.tdee == 2759
    assert plan.target_calories == 2759
    assert plan.bmi_category == "peso normal"


def test_generate_plan_saves_to_history(profile):
    repository = InMemoryPlanRepository()
    GeneratePlan(FORMULAS, repository).execute(profile, "harris")

    history = ListHistory(repository).execute()

    assert len(history) == 1
    assert history[0].formula == "harris"


def test_unknown_formula_is_rejected(profile):
    use_case = GeneratePlan(FORMULAS, InMemoryPlanRepository())
    with pytest.raises(ValueError, match="desconhecida"):
        use_case.execute(profile, "inexistente")


def test_json_repository_round_trip(tmp_path: Path, profile):
    repository = JsonPlanRepository(tmp_path / "history.json")
    plan = GeneratePlan(FORMULAS, repository).execute(profile)

    [record] = repository.list_all()

    assert record.profile == profile
    assert record.plan == plan


def test_json_repository_starts_empty(tmp_path: Path):
    assert JsonPlanRepository(tmp_path / "missing.json").list_all() == []
