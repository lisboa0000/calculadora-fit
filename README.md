# Calculadora Fit

[![Tests](https://github.com/lisboa0000/calculadora-fit/actions/workflows/tests.yml/badge.svg)](https://github.com/lisboa0000/calculadora-fit/actions/workflows/tests.yml)

Calculadora de IMC, metabolismo basal, gasto calórico diário e macronutrientes, em Python, via linha de comando.

O objetivo do projeto é **mostrar como organizo código**: Clean Architecture, princípios SOLID e padrões de projeto aplicados a um problema pequeno e fácil de entender. Este README explica as decisões.

> Os cálculos são estimativas educativas e não substituem a orientação de um nutricionista.

## Como usar

Requer Python 3.10 ou superior. Não tem dependências de execução.

```bash
python -m calculadora_fit calcular --sexo m --idade 30 --peso 80 --altura 180 --atividade moderado --objetivo ganhar
python -m calculadora_fit calcular --sexo f --idade 25 --peso 60 --altura 165 --formula harris
python -m calculadora_fit historico
```

Exemplo de saída:

```
IMC: 24.7 (peso normal)
Metabolismo basal: 1780 kcal
Gasto diário total: 2759 kcal
Meta para 'ganhar': 3035 kcal
Macros: 144 g proteína | 426 g carbo | 84 g gordura
```

## Testes

```bash
pip install -r requirements-dev.txt
pytest
```

## Estrutura

```
calculadora_fit/
  domain/          # regras de negócio: entidades, fórmulas, cálculos, contrato do repositório
  application/     # casos de uso (GeneratePlan, ListHistory)
  infrastructure/  # repositórios concretos (JSON em disco e em memória)
  interface/       # CLI
tests/
```

A dependência aponta sempre para dentro: `interface` e `infrastructure` conhecem o `domain`, e o `domain` não conhece ninguém. O `domain` não importa `json`, `argparse` nem nenhum detalhe de I/O.

## Decisões de projeto

### Clean Architecture: o domínio não depende de nada

As fórmulas e as regras de macros ficam em `domain/`, sem I/O. Isso permite testar tudo sem arquivo, sem terminal e sem banco. Trocar a CLI por uma API ou o JSON por um banco de dados não muda nenhuma regra de negócio.

### Strategy: fórmulas de metabolismo intercambiáveis

Mifflin-St Jeor e Harris-Benedict calculam o metabolismo basal de formas diferentes. Cada uma é uma classe com o mesmo contrato (`BMRFormula`) e fica registrada em `FORMULAS`. O usuário escolhe com `--formula`, e o caso de uso não tem `if` por fórmula. Código em `domain/formulas.py`.

### Repository: o histórico é um detalhe

`PlanRepository` é um contrato definido no domínio. `JsonPlanRepository` grava em disco e `InMemoryPlanRepository` é usado nos testes. O caso de uso só conhece a abstração. Código em `domain/repositories.py` e `infrastructure/`.

### SOLID, com o código onde cada princípio aparece

| Princípio | Onde |
|---|---|
| **S**: responsabilidade única | `services.py` só calcula, `json_repository.py` só persiste, `cli.py` só traduz entrada e saída |
| **O**: aberto/fechado | Adicionar uma fórmula nova é criar uma classe e registrá-la em `FORMULAS`, sem alterar o caso de uso |
| **L**: substituição de Liskov | `JsonPlanRepository` e `InMemoryPlanRepository` são trocáveis, e os testes de `GeneratePlan` rodam com os dois |
| **I**: segregação de interfaces | `BMRFormula` tem um único método, e `PlanRepository` só `save` e `list_all` |
| **D**: inversão de dependência | `GeneratePlan` recebe as fórmulas e o repositório pelo construtor e depende só de abstrações |

### Objetos de valor imutáveis e validação na entidade

`Profile`, `Macros` e `NutritionPlan` são `dataclass(frozen=True)`. `Profile` valida a si mesmo (idade, peso e altura em faixas plausíveis), então não existe um perfil inválido circulando pelo sistema.

## Regras de cálculo

- **IMC:** peso / altura², classificado pela OMS para adultos.
- **Metabolismo basal:** Mifflin-St Jeor (padrão) ou Harris-Benedict revisada.
- **Gasto diário total:** metabolismo basal × fator de atividade (1,2 a 1,9).
- **Meta calórica:** gasto total × 0,85 (emagrecer), × 1,0 (manter) ou × 1,10 (ganhar massa).
- **Macros:** proteína por kg de peso (2,0 / 1,6 / 1,8 g conforme o objetivo), gordura em 25% das calorias e carboidratos com o restante.

Os percentuais e os fatores são simplificações para fins didáticos e estão em constantes nomeadas em `domain/services.py`, fáceis de ajustar.

## O que ficou de fora de propósito

- **Sem framework e sem banco de dados.** O projeto é pequeno e o objetivo é a arquitetura, não a infraestrutura.
- **Sem interface web.** Uma API ou um front-end seriam um novo adaptador de entrada, sem mudar `domain/` nem `application/`.
- **Sem controle de versão do formato do JSON.** Para um histórico local simples isso não compensa. Num caso real, o próximo passo seria versionar o esquema.

## Próximos passos

- Exportar o histórico para CSV.
- Acompanhar a evolução do peso ao longo do tempo.
- Adicionar uma fórmula baseada em massa magra (Katch-McArdle) como uma nova estratégia.
