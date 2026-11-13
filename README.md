# h2-ageing-lca

**How much does stack ageing change the life cycle assessment of a hydrogen mobility chain?**

[![tests](https://github.com/Ayabh12/h2-ageing-lca/actions/workflows/tests.yml/badge.svg)](https://github.com/Ayabh12/h2-ageing-lca/actions/workflows/tests.yml)
Code: MIT · Data: CC BY 4.0

This repository contains the models, data and code of a life cycle assessment (LCA) that accounts for the ageing of the electrochemical stacks of a hydrogen chain: a PEM electrolyser, compression, a type IV tank and a PEM fuel cell. Every result can be recomputed with one command, and every input can be changed in one configuration file.

---

## Contents

1. [Why this matters](#1-why-this-matters)
2. [What the code does](#2-what-the-code-does)
3. [Main results](#3-main-results)
4. [Who can use it, and for what](#4-who-can-use-it-and-for-what)
5. [Quick start](#5-quick-start)
6. [Use and adapt it: six levels, with examples](#6-use-and-adapt-it-six-levels-with-examples)
7. [Reproduce every result](#7-reproduce-every-result)
8. [Repository layout](#8-repository-layout)
9. [Data and ecoinvent](#9-data-and-ecoinvent)
10. [Limits](#10-limits)
11. [Cite, licence, contact](#11-cite-licence-contact)

Further documentation: [method](docs/METHOD.md) · [use and adapt the model](docs/ADAPT.md) · [worked examples](docs/USE_CASES.md) · [change any input](docs/CUSTOMISE.md) · [limits and validity domain](docs/LIMITS.md) · [data](data/README.md) · [research notebooks](notebooks/README.md)

---

## 1. Why this matters

Most LCAs of hydrogen mobility treat the electrolyser and the fuel cell as if they never aged: the same efficiency for 15 years and a single stack. In reality, a stack loses performance with use and must be replaced at the end of its life. Ignoring this underestimates the impact, but by how much was not known.

This repository answers two questions:

- **How much?** The rise of the impact due to ageing, for each component alone and for the whole chain.
- **Through which route?** Ageing acts in two ways, computed separately:
  1. **over-consumption**: an aged electrolyser needs more electricity per kg of hydrogen, an aged fuel cell more hydrogen per km;
  2. **replacement**: a stack at end of life (10 % voltage change, DOE criterion) is replaced by a new one, which must be manufactured.

## 2. What the code does

```
electricity source -> PEM electrolyser -> compression -> type IV tank -> PEM fuel cell
(configurable)        Nel MC250, 1.25 MW   700 bar        142.2 L         Toyota Mirai II
```

1. **Reference performance from measurements.** A polarisation model is fitted on a measured wind-driven operating profile of a Nel MC250 electrolyser (public NLR data) and on road measurements of a Toyota Mirai II fuel cell. The wind profile describes *how* the electrolyser operates; it does not fix the origin of the electricity, which is a separate input (French residual mix by default).
2. **Ageing in three cases.** Optimistic and central: linear model with rates published by the US DOE. Pessimistic: mechanistic model with constants measured on laboratory cells (platinum surface loss, resistance growth, crossover, anode activity, membrane thinning). The tank permeation grows over 15 years.
3. **End of life and number of stacks.** The model finds the age at which each stack reaches the DOE criterion, then counts the stacks needed over 15 years.
4. **LCA.** Use-phase flows and fabrication of the stacks and tank are combined with characterised impacts (ecoinvent 3.11 cut-off, EF 3.1, 16 categories). Results are given for each component alone and for the whole chain, with and without ageing.

The full method, with every equation and its source, is in [docs/METHOD.md](docs/METHOD.md).

## 3. Main results

Default configuration: climate change (EF 3.1), French residual mix (79.6 g CO2-eq/kWh, AIB 2024 data), 200 000 km over 15 years.

| | No ageing | Optimistic | Central | Pessimistic |
|---|---|---|---|---|
| Fuel cell stacks over 15 years | 1 | 1 | 2 | 2 |
| Electrolyser stacks over 15 years | 1 | 2 | 3 | 3 |
| Electrolyser alone (kg CO2-eq/kg H2) | 4.31 | 4.53 (+5.1 %) | 4.57 (+5.9 %) | 4.66 (+8.2 %) |
| Tank alone (g CO2-eq/km) | 11.89 | 11.89 (0.0 %) | 12.04 (+1.3 %) | 12.64 (+6.4 %) |
| Fuel cell alone (g CO2-eq/km) | 61.9 | 63.4 (+2.4 %) | 82.2 (+32.8 %) | 83.4 (+34.6 %) |
| **Whole chain (g CO2-eq/km)** | **74.1** | **77.8 (+5.0 %)** | **97.2 (+31.1 %)** | **100.1 (+35.0 %)** |

What these numbers show:

- **The fuel cell is dominated by replacement.** One fuel cell stack is spread over the 200 000 km of a single vehicle; a second stack adds about 30 points. In the central case, 91 % of the fuel cell rise comes from the extra stack.
- **The electrolyser is dominated by over-consumption.** One electrolyser stack is spread over about 1.19 million kg of hydrogen and weighs 0.8 % of the impact of 1 kg; the extra electricity matters more.
- **The result moves by steps.** Any fuel cell end of life between half the horizon and the horizon gives two stacks; the exact lifetime matters little inside a step and a lot at its edges.
- **The fuel cell lifetime is the key input.** In the global sensitivity analysis, it explains almost all the variation of the rise (total Sobol index 0.94).
- **Cleaner electricity makes ageing weigh more, in relative terms.** The replacement stacks add the same impact whatever the electricity; with wind electricity, the chain rise in the central case is +48.6 % instead of +31.1 %.

## 4. Who can use it, and for what

| You are | What you can do | Where to start |
|---|---|---|
| **LCA practitioner** | Add ageing to an LCA of hydrogen mobility; test your own electricity mix, horizon, inventories or stack counting rule | [docs/USE_CASES.md](docs/USE_CASES.md), examples 1–4 |
| **Engineer or manufacturer** | See what a longer stack lifetime or a slower degradation rate is worth in CO2-eq; find the lifetime threshold that removes one replacement | `scripts/threshold.py`, example 5 |
| **Researcher on degradation** | Plug in your own ageing constants or ageing law and see the effect on the LCA, without rewriting the LCA | [docs/ADAPT.md](docs/ADAPT.md), levels 4 and 5 |
| **Student** | Read a complete, small LCA model with ageing, run it, and modify it step by step | [docs/METHOD.md](docs/METHOD.md), then the notebooks |

Why use this repository rather than start from scratch: the ageing models, the end-of-life search, the stack counting and the LCA are already linked, so changing one input automatically updates everything downstream; and every input is traced to a source in a single file.

## 5. Quick start

Requirements: Python 3.10 or later. No ecoinvent licence is needed to run the model.

```bash
git clone https://github.com/Ayabh12/h2-ageing-lca
cd h2-ageing-lca
pip install -r requirements.txt
python scripts/run.py                    # default configuration, about 2 s
python tests/test_reference_results.py   # 8 tests: the default configuration gives the reference results
```

`scripts/run.py` prints the tables above and writes them as CSV files (`--out <folder>`). Change one value from the command line:

```bash
python scripts/run.py --set usage.electricity_electrolyser=wind_FR
python scripts/run.py --set cases.central.fuel_cell.hours_to_end_of_life=6000
```

or copy `config/default.yaml`, edit it, and run `python scripts/run.py --config config/my_case.yaml`. From Python:

```python
import sys; sys.path.insert(0, "src")
from h2ageing import load_config, with_values, run

cfg = with_values(load_config(), **{"usage.electricity_electrolyser": "wind_FR"})
print(run(cfg)["chain"])
```

## 6. Use and adapt it: six levels, with examples

Anyone can use the model for their own question without rewriting it: you change only what differs in your case, and the end of life, the number of stacks and the LCA are recomputed. Examples with the shipped data (climate change, whole chain, central case unless stated):

| Level | Example question | What you write | Answer |
|---|---|---|---|
| 1. Reproduce | "Do I get the published values?" | `run(load_config())` | 74.1 g/km without ageing, +31.1 % with ageing |
| 2. Ask a question | "What if my fuel cell stack lasts 5 000 h?" | `with_values(cfg, **{"cases.central.fuel_cell.hours_to_end_of_life": 5000.0})` | still 2 stacks, +31.4 %: one stack is enough only above 5 554 h |
| 3. Your own case | "My stack lasts 7 000 h and my electrolyser runs on wind electricity" | a copy of `config/default.yaml` with two values changed | 1 stack, 42.7 g/km, +3.7 % |
| 4. Your own constants | "I measured 27 mV of loss at high current, not 45 mV" (pessimistic case) | one key of the mechanistic model | end of life 5 652 h instead of 2 895 h, +12.8 % instead of +35.0 % |
| 5. Your own law | "The resistance grows as the square root of time" (pessimistic case) | one Python function of four lines | end of life 6 370 h, 1 stack, +13.0 % |
| 6. Your own data | "I have measurements or an inventory of another stack" | the files in `data/` | refit or rebuild, then run |

```python
import sys; sys.path.insert(0, "src")
from h2ageing import load_config, with_values, run

cfg = load_config()
r = run(with_values(cfg, **{"cases.central.fuel_cell.hours_to_end_of_life": 5000.0}))   # level 2
print(r["chain"][["case", "total_g_per_km", "rise_pct"]])
```

The code of every level, explained: [docs/ADAPT.md](docs/ADAPT.md). The same, ready to run in Jupyter: [examples/adapt_the_model.ipynb](examples/adapt_the_model.ipynb). To ask a question, open an *Issue*; to keep your own version online, *Fork* the repository; to propose an improvement, open a *Pull request* from your fork.

## 7. Reproduce every result

| Result | Command | Time |
|---|---|---|
| Three cases: end of life, stacks, each component, whole chain, 16 categories | `python scripts/run.py --out results` | ~2 s |
| Check against the reference values | `python tests/test_reference_results.py` (also run automatically on every push) | ~10 s |
| Bar chart of the chain by item (after `run.py`) | `python scripts/plot.py --results results` | ~2 s |
| Electricity sources, electrolyser hours, stack counting | `run.py` with `--set` (see [docs/USE_CASES.md](docs/USE_CASES.md)) | ~2 s each |
| Impact versus stack lifetime (steps and thresholds) | `python scripts/threshold.py --out results` | ~30 s |
| Crossover law of the mechanistic fuel cell model, mean speed | `python scripts/fuel_cell_tests.py` | ~10 s |
| Effect of each mechanistic constant (published alternative values) | `python scripts/mechanistic_constants.py` | ~5 s |
| Global sensitivity (Sobol indices, 10 240 runs) | `python scripts/sobol.py --out results` | ~15 min (2 cores) |
| Polarisation fits (they rewrite `data/parameters/` and give back the shipped parameters) | `python scripts/fit_pemfc.py`, `python scripts/fit_pemwe.py` | ~5 s each |
| Fabrication impacts from the inventories | `python scripts/build_fabrication_brightway.py --project <name>` (needs ecoinvent) | – |

The original research notebooks (in French, outputs included) are in [notebooks/](notebooks/README.md); they give the same results with more figures.

## 8. Repository layout

```
config/default.yaml        all inputs, each with its source (units in the key names)
src/h2ageing/              the models (Python package)
    pemfc.py               fuel cell: polarisation, ageing (linear and mechanistic), trip at constant power
    pemwe.py               electrolyser: operating profile, ageing (linear and mechanistic)
    tank.py                permeation of the type IV tank
    impacts.py             EF 3.1 impact data and single score
    chain.py               LCA of each component and of the whole chain
    run.py                 runs all cases, builds the result tables
scripts/                   command-line tools (see section 6)
data/
    measurements/          fuel cell road measurements, electrolyser wind profile
    parameters/            fitted polarisation parameters
    inventories/           foreground inventories (masses, energy, ecoinvent activity names)
    impacts/               characterised impacts (per kWh, per kg of water, per stack or tank)
tests/                     reference results and the tests that check them
notebooks/                 original research notebooks (French)
docs/                      method, use and adaptation, worked examples, customisation, limits
examples/                  Jupyter notebook: use and adapt the model in six levels
```

## 9. Data and ecoinvent

No ecoinvent dataset is distributed, in line with its licence. `data/impacts` contains characterised results only (impact of 1 kWh, of 1 kg of water, of one manufactured stack or tank), which is enough to run every result. The foreground inventories, with the ecoinvent activity used for each flow, are in `data/inventories`; with your own ecoinvent licence, `scripts/build_fabrication_brightway.py` recomputes the fabrication impacts after you change any amount. Sources and licences of each file: [data/README.md](data/README.md).

## 10. Limits

The model is transparent about what it does not know; the main limits are below, and [docs/LIMITS.md](docs/LIMITS.md) gives each one with its effect on the results and how to test it.

- **No degradation rate is published for the two stacks studied.** The three cases bracket ageing with published values for other equipment; they are not a prediction of these exact stacks.
- **The pessimistic constants come from laboratory cells**, more stressed than commercial stacks, and the mechanistic laws are extrapolated beyond the duration of the tests.
- **One driving pattern and one wind profile for the use phase.** The fuel cell polarisation curve is fitted on all 12 road recordings, but the hydrogen consumption over the vehicle life is simulated by replaying one measured trip (WLTP-type, 2 033 s, 20.32 km) at every age; the electrolyser replays one 4-hour wind profile. Temperatures are constant.
- **Scope: stacks and tank only.** Auxiliaries (balance of plant), the station apart from compression, the rest of the vehicle and end of life are outside the system.
- **The result moves by steps** with the number of fuel cell stacks; the stack counting rule (integer or prorata) matters in the central case.

## 11. Cite, licence, contact

- **Cite:** see [CITATION.cff](CITATION.cff) (GitHub shows a "Cite this repository" button).
- **Licence:** code under MIT ([LICENSE](LICENSE)); data and documentation under CC BY 4.0 ([LICENSE-DATA.md](LICENSE-DATA.md)). Third-party sources keep their own terms ([data/README.md](data/README.md)).
- **Questions, errors or new data:** please open an issue on GitHub. Contributions of measured degradation data for commercial stacks are especially welcome, since they would replace the bracketing cases by a measurement.

---

### En bref (français)

**Pourquoi c'est important.** La plupart des ACV de la mobilité hydrogène traitent l'électrolyseur et la pile à combustible comme s'ils ne vieillissaient jamais : le même rendement pendant 15 ans et un seul stack. En réalité, un stack perd en performance avec l'usage et doit être remplacé en fin de vie. Ignorer ce phénomène sous-estime l'impact, mais on ne savait pas de combien.

Ce dépôt répond à deux questions :

- **De combien ?** La hausse de l'impact due au vieillissement, pour chaque composant seul et pour la chaîne complète.
- **Par quelle voie ?** Le vieillissement agit de deux façons, calculées séparément :
  1. **la surconsommation** : un électrolyseur vieilli consomme plus d'électricité par kg d'hydrogène, et une pile vieillie plus d'hydrogène par km ;
  2. **le remplacement** : un stack en fin de vie (10 % de variation de tension, critère du DOE) est remplacé par un neuf, qu'il faut fabriquer.

**Le dépôt.** Ce dépôt calcule l'effet du vieillissement des stacks sur l'analyse du cycle de vie d'une chaîne hydrogène (électrolyseur PEM, compression, réservoir de type IV, pile à combustible PEM). Le vieillissement agit par deux voies, calculées séparément : la surconsommation et le remplacement des stacks. Une commande (`python scripts/run.py`) redonne tous les résultats ; toutes les valeurs d'entrée, avec leur source, sont dans `config/default.yaml` et peuvent être changées. Les notebooks de recherche d'origine, en français, sont dans `notebooks/`.
