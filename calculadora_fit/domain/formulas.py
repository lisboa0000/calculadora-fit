"""Padrão Strategy: cada fórmula de metabolismo basal é uma estratégia.

Para suportar uma nova fórmula, basta criar uma classe com `name` e `bmr`
e registrá-la em `FORMULAS` (Open/Closed).
"""
from typing import Protocol

from calculadora_fit.domain.entities import Profile, Sex


class BMRFormula(Protocol):
    name: str

    def bmr(self, profile: Profile) -> float: ...


class MifflinStJeor:
    name = "mifflin"

    def bmr(self, profile: Profile) -> float:
        base = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age
        return base + (5 if profile.sex is Sex.MALE else -161)


class HarrisBenedict:
    """Versão revisada (Roza e Shizgal, 1984)."""

    name = "harris"

    def bmr(self, profile: Profile) -> float:
        w, h, a = profile.weight_kg, profile.height_cm, profile.age
        if profile.sex is Sex.MALE:
            return 88.362 + 13.397 * w + 4.799 * h - 5.677 * a
        return 447.593 + 9.247 * w + 3.098 * h - 4.330 * a


FORMULAS: dict[str, BMRFormula] = {
    f.name: f for f in (MifflinStJeor(), HarrisBenedict())
}
