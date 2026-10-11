"""Adaptador de entrada (CLI). Monta as dependências e chama os casos de uso."""
import argparse
from pathlib import Path

from calculadora_fit.application.use_cases import GeneratePlan, ListHistory
from calculadora_fit.domain.entities import ActivityLevel, Goal, Profile, Sex
from calculadora_fit.domain.formulas import FORMULAS
from calculadora_fit.infrastructure.json_repository import JsonPlanRepository

HISTORY_FILE = Path.home() / ".calculadora_fit.json"

SEXES = {"m": Sex.MALE, "f": Sex.FEMALE}
ACTIVITIES = {
    "sedentario": ActivityLevel.SEDENTARY,
    "leve": ActivityLevel.LIGHT,
    "moderado": ActivityLevel.MODERATE,
    "intenso": ActivityLevel.INTENSE,
    "atleta": ActivityLevel.ATHLETE,
}
GOALS = {"emagrecer": Goal.LOSE, "manter": Goal.MAINTAIN, "ganhar": Goal.GAIN}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="calculadora-fit",
        description="Calcula IMC, gasto calórico e macros. Uso educativo.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    calc = sub.add_parser("calcular", help="gera um plano nutricional")
    calc.add_argument("--sexo", choices=SEXES, required=True)
    calc.add_argument("--idade", type=int, required=True)
    calc.add_argument("--peso", type=float, required=True, help="em kg")
    calc.add_argument("--altura", type=float, required=True, help="em cm")
    calc.add_argument("--atividade", choices=ACTIVITIES, default="moderado")
    calc.add_argument("--objetivo", choices=GOALS, default="manter")
    calc.add_argument("--formula", choices=sorted(FORMULAS), default="mifflin")

    sub.add_parser("historico", help="lista os planos já calculados")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repository = JsonPlanRepository(HISTORY_FILE)

    if args.command == "historico":
        records = ListHistory(repository).execute()
        if not records:
            print("Nenhum plano salvo ainda.")
        for r in records:
            print(
                f"{r.created_at:%d/%m/%Y %H:%M} | {r.formula} | "
                f"{r.plan.target_calories} kcal | IMC {r.plan.bmi}"
            )
        return 0

    try:
        profile = Profile(
            sex=SEXES[args.sexo],
            age=args.idade,
            weight_kg=args.peso,
            height_cm=args.altura,
            activity=ACTIVITIES[args.atividade],
            goal=GOALS[args.objetivo],
        )
        plan = GeneratePlan(FORMULAS, repository).execute(profile, args.formula)
    except ValueError as error:
        print(f"Erro: {error}")
        return 1

    m = plan.macros
    print(f"IMC: {plan.bmi} ({plan.bmi_category})")
    print(f"Metabolismo basal: {plan.bmr:.0f} kcal")
    print(f"Gasto diário total: {plan.tdee:.0f} kcal")
    print(f"Meta para '{args.objetivo}': {plan.target_calories} kcal")
    print(f"Macros: {m.protein_g} g proteína | {m.carbs_g} g carbo | {m.fat_g} g gordura")
    print("Estimativa educativa, não substitui orientação de nutricionista.")
    return 0
