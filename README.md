# h2-ageing-lca

**English** | [Français](README.fr.md)

**How much does stack ageing change the life cycle assessment of a hydrogen mobility chain?**

[![tests](https://github.com/Ayabh12/h2-ageing-lca/actions/workflows/tests.yml/badge.svg)](https://github.com/Ayabh12/h2-ageing-lca/actions/workflows/tests.yml)
Code: MIT · Data: CC BY 4.0

This repository contains the models, data and code of a life cycle assessment (LCA) that accounts for the ageing of the electrochemical stacks of a hydrogen chain: a PEM electrolyser, compression, a type IV tank and a PEM fuel cell. Every result can be recomputed with one command, and every input can be changed in one configuration file.

---

## Contents

1. [Why this matters](#1-why-this-matters)
2. [Who can use it, and for what](#2-who-can-use-it-and-for-what)
3. [What the code does](#3-what-the-code-does)
4. [Use without and with an ecoinvent licence](#4-use-without-and-with-an-ecoinvent-licence)
5. [Use and adapt it: six levels, with examples](#5-use-and-adapt-it-six-levels-with-examples)
6. [Reproduce every result](#6-reproduce-every-result)
7. [Repository layout](#7-repository-layout)
8. [Data and ecoinvent](#8-data-and-ecoinvent)
9. [Limits](#9-limits)
10. [Main results](#10-main-results)
11. [Cite, licence, contact](#11-cite-licence-contact)

Further documentation: [method](docs/METHOD.md) · [use and adapt the model](docs/ADAPT.md) · [worked examples](docs/USE_CASES.md) · [change any input](docs/CUSTOMISE.md) · [limits and validity domain](docs/LIMITS.md) · [data](data/README.md) · [research notebooks](notebooks/README.md)

---

## 1. Why this matters

Most LCAs of hydrogen mobility treat the electrolyser and the fuel cell as if they never aged: the same efficiency for 15 years and a single stack. In reality, a stack loses performance with use and must be replaced at the end of its life. Ignoring this underestimates the impact, but by how much was not known.

This repository answers two questions:

- **How much?** The rise of the impact due to ageing, for each component alone and for the whole chain.
- **Through which route?** Ageing acts at two levels:
  1. **Over-consumption**: the aged fuel cell uses more hydrogen per km, the electrolyser more electricity per kg, and the tank loses more hydrogen.
  2. **Replacement**: a stack is replaced when its voltage has changed by 10 % (DOE criterion); each new stack adds its fabrication impact.

**The result in short.** Over the vehicle life (15 years, 200 000 km), stack ageing raises the climate change impact of the chain, compared with the same chain without ageing, by:

- **+5.0 %** in the **optimistic** case: linear model, with the DOE targets (fuel cell lifetime, electrolyser degradation rate);
- **+31.1 %** in the **central** case: linear model, with the current status measured by the DOE on real systems;
- **+35.0 %** in the **pessimistic** case: semi-empirical model, more detailed, describing the degradation of the stack materials (fuel cell: loss of platinum active area, rise of the resistance, membrane crossover; electrolyser: loss of anode activity, rise of the resistance, membrane thinning), with constants measured on laboratory cells.

This repository lets anyone recompute this result for their own case.

**What this repository brings**

- **A ready-to-use method.** The ageing models, the end-of-life search, the stack counting and the LCA are already linked, and every equation is documented with its source ([docs/METHOD.md](docs/METHOD.md)).
- **Any value or any inventory can be changed without rewriting the code.** The inputs are in one configuration file, the fabrication inventories in CSV tables; after a change, the end of life, the number of stacks and the impact are recomputed automatically.
- **Models built on real measurements**: a Toyota Mirai II fuel cell recorded on the road, and a Nel MC250 electrolyser following a wind production profile (public NLR data).
- **Usable without an ecoinvent licence**, and complete with one: both ways are described step by step ([section 4](#4-use-without-and-with-an-ecoinvent-licence)).
- **Results checked automatically.** At every change of the repository, GitHub runs 13 tests again. Each one recomputes a result (end of life and number of stacks, each component alone, whole chain, 16 categories, electricity sources, among others) and checks that it is identical to the reference result. The "tests" badge at the top of this page is green when all tests pass; it turns red if a change alters a result.
- **Open and bilingual**: every page exists in English and French, and anyone can reproduce the results or test their own case.

**Try it in one command.** If the fuel cell lasts 6 000 h instead of 4 100 h, one stack lasts the whole vehicle life, and the rise of the central case falls from +31.1 % to +6.4 %:

```bash
python scripts/run.py --set cases.central.fuel_cell.hours_to_end_of_life=6000
```

## 2. Who can use it, and for what

| You are | What you can do | Where to start |
|---|---|---|
| **LCA practitioner** | Add ageing to an LCA of hydrogen mobility; test your own electricity mix, horizon, inventories or stack counting rule | [docs/USE_CASES.md](docs/USE_CASES.md), examples 1–3 and 7 |
| **Engineer or manufacturer** | See what a longer stack lifetime or a slower degradation rate is worth in CO2-eq; find the lifetime threshold that removes one replacement | `scripts/threshold.py`, example 4 |
| **Researcher on degradation** | Plug in your own ageing constants or ageing law and see the effect on the LCA, without rewriting the LCA | [docs/ADAPT.md](docs/ADAPT.md), levels 4 and 5 |
| **Student** | Read a complete, small LCA model with ageing, run it, and modify it step by step | [docs/METHOD.md](docs/METHOD.md), then the notebooks |

## 3. What the code does

```mermaid
flowchart TB
    subgraph E["Inputs · config/default.yaml and data/"]
        direction LR
        e1["Measurements<br/>wind profile of the Nel MC250<br/>road trips of the Mirai II"]
        e2["Three ageing cases<br/>optimistic · central · pessimistic"]
        e3["Fabrication inventories<br/>stacks and tank"]
        e4["Characterised impacts<br/>ecoinvent 3.11 · EF 3.1"]
        e1 ~~~ e2 ~~~ e3 ~~~ e4
    end

    subgraph C["The chain studied"]
        direction LR
        c1["Electricity<br/>configurable"] --> c2["PEM electrolyser<br/>Nel MC250, 1.25 MW"] --> c3["Compression<br/>700 bar"] --> c4["Type IV tank<br/>142.2 L"] --> c5["PEM fuel cell<br/>Toyota Mirai II"] --> c6(["1 km driven"])
    end

    subgraph M["What the code computes · ★ contribution of this work"]
        direction LR
        m1["1 · Reference<br/>performance"] --> m2["★ 2 · Ageing<br/>over 15 years, three cases"] --> m3["★ 3 · End of life<br/>and number of stacks"] --> m4["★ 4 · LCA of ageing<br/>over-consumption + replacement"]
    end

    subgraph R["Results"]
        direction LR
        r1["Each component<br/>and the whole chain"]
        r2["★ Rise due to ageing<br/>with / without, 16 EF 3.1 categories"]
        r3["Sensitivity tests"]
        r1 ~~~ r2 ~~~ r3
    end

    E --> C --> M --> R

    classDef inp fill:#e8f0fa,stroke:#3b6ea5,color:#1d2b3a
    classDef chain fill:#fdf1dc,stroke:#c9892b,color:#3a2a10
    classDef code fill:#ece6f6,stroke:#6c4fa3,color:#2a1d40
    classDef res fill:#e3f1e3,stroke:#3d8b3d,color:#163016
    class e1,e2,e3,e4 inp
    class c1,c2,c3,c4,c5,c6 chain
    class m1,m2,m3,m4 code
    class r1,r2,r3 res
    style E fill:#ffffff,stroke:#3b6ea5
    style C fill:#ffffff,stroke:#c9892b
    style M fill:#ffffff,stroke:#6c4fa3
    style R fill:#ffffff,stroke:#3d8b3d
    classDef key fill:#fde3e1,stroke:#c0392b,stroke-width:3px,color:#4a1410,font-weight:bold
    class m2,m3,m4,r2 key
```

1. **Reference performance.** A polarisation model is fitted on measurements: the wind profile of a Nel MC250 electrolyser (public NLR data) and road trips of a Toyota Mirai II fuel cell. The profile says how the electrolyser operates, not where the electricity comes from, which is chosen separately (French residual mix by default).
2. **Ageing.** Three cases, detailed below. The semi-empirical model has a physical structure (each degradation mechanism acts on one term of the polarisation equation) and laws of change fitted in the laboratory. The tank permeation grows over 15 years.
3. **End of life.** The model finds the age at which the voltage has changed by 10 % (at 300 A for the fuel cell, at the mean current density of the profile for the electrolyser) and counts the stacks needed over 15 years.
4. **LCA.** Use flows and fabrication are combined with characterised impacts (ecoinvent 3.11 cut-off, EF 3.1, 16 categories). Fabrication is counted from cradle to gate; end of life is not ([what each impact includes](docs/METHOD.md#what-each-impact-includes)). Results for each component and for the whole chain, with and without ageing.

### The three ageing cases

No degradation rate is published for the two stacks studied. In the absence of these data, three cases bracket ageing: the DOE target (optimistic), the real state measured by the DOE (central) and laboratory constants (pessimistic).

| | Optimistic | Central | Pessimistic |
|---|---|---|---|
| Model | linear | linear | semi-empirical |
| Fuel cell | 8 000 h to end of life (DOE target) | 4 100 h (best fleet followed by the DOE, 2006–2016) | laboratory constants (Colombo et al. 2023): end of life at 2 895 h |
| Electrolyser | 2.3 µV/h per cell (DOE 2026 target) | 4.8 µV/h (DOE 2022 status) | laboratory constants (Padgett et al. 2025; Chandesris et al. 2015) |
| Tank permeation (mL/h/L, from year 0 to 15) | 6 → 6 | 6 → 14 | 6 → 46 (UN R134 limit) |
| What it represents | what the technology aims for | the current state of real systems | an upper bound, on cells more stressed than commercial stacks |

The examples highlight the central case, because it rests on real systems measured by the DOE; the optimistic and pessimistic cases are bounds, one taken from targets, the other from laboratory cells. The central case is not an average of the other two, and the three cases are always given side by side. The values and their sources are in `cases` of `config/default.yaml`.

The full method, with every equation and its source, is in [docs/METHOD.md](docs/METHOD.md).

## 4. Use without and with an ecoinvent licence

No ecoinvent dataset is distributed, in line with its licence. The model can be used in two ways:

| | Without an ecoinvent licence | With an ecoinvent licence |
|---|---|---|
| What you can do | run the model, change any input and reproduce every result | in addition, change a fabrication inventory and recompute its impact |
| What is used | `data/impacts`: characterised results only (impact of 1 kWh, of 1 kg of water, of one manufactured stack or tank) | your own ecoinvent 3.11 cut-off, imported in Brightway with your ecoinvent login |
| What to install | `requirements.txt` | `requirements.txt` and `requirements-brightway.txt` |

### Installation

Requirements: Python 3.10 or later, and Git (or download the repository as a ZIP: green **Code** button, **Download ZIP**).

**In a terminal** (Anaconda Prompt, PowerShell, macOS or Linux terminal):

```bash
git clone https://github.com/Ayabh12/h2-ageing-lca
cd h2-ageing-lca
pip install -r requirements.txt
python scripts/run.py                    # default configuration, about 2 s
python tests/test_reference_results.py   # 13 tests: the default configuration gives the reference results
```

**In Jupyter**, this method works everywhere, with or without Git installed. Copy these two cells into a new notebook:

```python
# cell 1: download the repository (no Git needed) and install, once
import sys, urllib.request, zipfile
urllib.request.urlretrieve("https://github.com/Ayabh12/h2-ageing-lca/archive/refs/heads/main.zip", "h2-ageing-lca.zip")
zipfile.ZipFile("h2-ageing-lca.zip").extractall(".")
%cd h2-ageing-lca-main
!{sys.executable} -m pip install -r requirements.txt
```

```python
# cell 2: run the model, then check the reference results
!{sys.executable} scripts/run.py
!{sys.executable} tests/test_reference_results.py
```

In Jupyter, `!` runs a terminal command, `%cd` enters a folder, and `{sys.executable}` is the Python of the notebook. If the folder already exists, only run `import sys` and `%cd h2-ageing-lca-main`. A ready-made notebook is also in [examples/adapt_the_model.ipynb](examples/adapt_the_model.ipynb).

In the steps below, write `!{sys.executable}` instead of `python` if you work in Jupyter.

### Without an ecoinvent licence

1. **Run the model**: `python scripts/run.py --out results/<name>`. The tables are written in that folder (list in [docs/CUSTOMISE.md](docs/CUSTOMISE.md)).
2. **Change an input**: add `--set key=value` to the command (one per value), or copy `config/default.yaml`, change it and run with `--config <your file>`. Every key is listed in [docs/CUSTOMISE.md](docs/CUSTOMISE.md).
3. **Use your own fabrication impact**: copy `data/impacts/fabrication_per_unit.csv`, change the values (impact of one unit of each component in the 16 EF 3.1 categories), then run with `--set fabrication.file=<your file>`.

From Python or Jupyter, once inside the repository folder, `h2-ageing-lca` or `h2-ageing-lca-main` (the `src` folder must be visible from where the code runs):

```python
import sys; sys.path.insert(0, "src")
from h2ageing import load_config, with_values, run

cfg = with_values(load_config(), **{"usage.electricity_electrolyser": "wind_FR"})
print(run(cfg)["chain"])
```

### With an ecoinvent licence

1. **Install Brightway** (once): `pip install -U -r requirements-brightway.txt`.
2. **Give your ecoinvent login.** Two ways:
   - let the script ask for it: it asks for your username, then your password (the password is not shown while you type);
   - or set it beforehand in two environment variables, `EI_USERNAME` and `EI_PASSWORD`: in a Windows terminal `set EI_USERNAME=...`, in macOS or Linux `export EI_USERNAME=...` (same for `EI_PASSWORD`); in Jupyter, `os.environ["EI_USERNAME"] = input()` and `os.environ["EI_PASSWORD"] = getpass.getpass()`.

   The login can be your own or that of a licence shared by your institution, if its terms allow it. It is only sent to ecoinvent to download the database and is never written to a file. Never put a login in this repository or in a notebook cell you share: ecoinvent licences are personal or per institution.
3. **Import ecoinvent and recompute the impacts**: `python scripts/build_fabrication_brightway.py --project <project> --import-ecoinvent --out results/<file>.csv`. The first time, ecoinvent 3.11 cut-off, its biosphere and its impact methods are downloaded and imported into the Brightway project `<project>`; this takes from about 20 minutes to under an hour. The next times, the script finds ecoinvent in the project and only recomputes (about one minute). It prints the 16 EF 3.1 methods it uses, then the climate change impact of each component.
4. **Check your installation** (once): run step 3 on the inventories as shipped, then compare the file written with the shipped impacts, in percent:

   ```python
   import pandas as pd
   new = pd.read_csv("results/<file>.csv").set_index("category")
   shipped = pd.read_csv("data/impacts/fabrication_per_unit.csv").set_index("category")
   ((new - shipped) / shipped * 100).round(2)
   ```

   Every value should be 0 (or −0, a rounding): with ecoinvent 3.11 cut-off, the difference with the shipped impacts (computed with Activity Browser) is below 0.01 % in the 16 categories and for the three components.
5. **Change an inventory**: in `data/inventories/*.csv`, change an amount, the ecoinvent activity or its location, or set `included` to `no` to leave a row out (columns explained in [data/inventories/README.md](data/inventories/README.md)).
6. **Recompute**: run step 3 again with another output file.
7. **Use the new impacts in the model**: `python scripts/run.py --set fabrication.file=results/<file>.csv --out results/<name>`.

If the script stops with "0 matches" or "2 matches", the ecoinvent activity named in the inventory was not found, or not found once: check its name, location and reference product in your ecoinvent database. If the download fails, check that your ecoinvent account gives access to version 3.11.

All these steps, with the check of the 16 categories and examples with and without a licence, including examples that change a constant, a law or the model of a case, then the 16 impact categories and the sensitivity (electricity source, lifetime threshold, Sobol) (expected values given), are ready to run in Jupyter: [examples/check_and_examples.ipynb](examples/check_and_examples.ipynb).

## 5. Use and adapt it: six levels, with examples

Anyone can use the model for their own question without rewriting it: you change only what differs in your case, and the end of life, the number of stacks and the LCA are recomputed. Examples with the shipped data (climate change, whole chain, central case unless stated):

| Level | Example question | What you write | Answer |
|---|---|---|---|
| 1. Reproduce | "Do I get the published values?" | `run(load_config())` | 74.1 g/km without ageing, +31.1 % with ageing |
| 2. Ask a question | "What if my fuel cell stack lasts 5 000 h?" | `with_values(cfg, **{"cases.central.fuel_cell.hours_to_end_of_life": 5000.0})` | still 2 stacks, +31.4 %: one stack is enough only above 5 554 h |
| 3. Your own case | "My stack lasts 7 000 h and my electrolyser runs on wind electricity" | a copy of `config/default.yaml` with two values changed | 1 stack, 42.7 g/km, +3.7 % |
| 4. Your own constants | "I measured 27 mV of loss at high current, not 45 mV" (pessimistic case) | one key of the semi-empirical model | end of life 5 652 h instead of 2 895 h, +12.8 % instead of +35.0 % |
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

## 6. Reproduce every result

| Result | Command | Time |
|---|---|---|
| Three cases: end of life, stacks, each component, whole chain, 16 categories | `python scripts/run.py --out results` | ~2 s |
| Check against the reference values | `python tests/test_reference_results.py` (also run automatically on every push) | ~10 s |
| Bar chart of the chain by item (after `run.py`) | `python scripts/plot.py --results results` | ~2 s |
| Electricity sources, electrolyser hours, stack counting | `run.py` with `--set` (see [docs/USE_CASES.md](docs/USE_CASES.md)) | ~2 s each |
| Impact versus stack lifetime (steps and thresholds) | `python scripts/threshold.py --out results` | ~30 s |
| Figure of the steps (after `run.py` and `threshold.py`) | `python scripts/plot_steps.py --results results --lang en` | ~2 s |
| Crossover law of the semi-empirical fuel cell model, mean speed | `python scripts/fuel_cell_tests.py` | ~10 s |
| Effect of each semi-empirical constant (published alternative values) | `python scripts/semi_empirical_constants.py` | ~5 s |
| Global sensitivity (Sobol indices, 10 240 runs) | `python scripts/sobol.py --out results` | ~15 min (2 cores) |
| Polarisation fits (they rewrite `data/parameters/` and give back the shipped parameters) | `python scripts/fit_pemfc.py`, `python scripts/fit_pemwe.py` | ~5 s each |
| Fabrication impacts from the inventories | `python scripts/build_fabrication_brightway.py --project <name>` (needs ecoinvent) | – |

The original research notebooks (in French, outputs included) are in [notebooks/](notebooks/README.md); they give the same results with more figures.

## 7. Repository layout

```
config/default.yaml        all inputs, each with its source (units in the key names)
src/h2ageing/              the models (Python package)
    pemfc.py               fuel cell: polarisation, ageing (linear and semi-empirical), trip at constant power
    pemwe.py               electrolyser: operating profile, ageing (linear and semi-empirical)
    tank.py                permeation of the type IV tank
    impacts.py             EF 3.1 impact data and single score
    chain.py               LCA of each component and of the whole chain
    run.py                 runs all cases, builds the result tables
scripts/                   command-line tools (see section 5)
data/
    measurements/          fuel cell road measurements, electrolyser wind profile
    parameters/            fitted polarisation parameters
    inventories/           foreground inventories (masses, energy, ecoinvent activity names)
    impacts/               characterised impacts (per kWh, per kg of water, per stack or tank)
tests/                     reference results and the tests that check them
notebooks/                 original research notebooks (French)
docs/                      method, use and adaptation, worked examples, customisation, limits
examples/                  Jupyter notebooks: use and adapt the model in six levels; checks and examples with and without ecoinvent
```

## 8. Data and ecoinvent

No ecoinvent dataset is distributed, in line with its licence. The model uses characterised results (`data/impacts`: impact of 1 kWh, of 1 kg of water, of one manufactured stack or tank); ecoinvent is only needed to recompute the fabrication impacts, with your own licence ([section 4](#4-use-without-and-with-an-ecoinvent-licence)). The foreground inventories, with the ecoinvent activity used for each flow, are in `data/inventories`. Sources and licences of each file: [data/README.md](data/README.md).

## 9. Limits

The model is transparent about what it does not know; the main limits are below, and [docs/LIMITS.md](docs/LIMITS.md) gives each one with its effect on the results and how to test it.

- **No degradation rate is published for the two stacks studied.** The three cases bracket ageing with published values for other equipment; they are not a prediction of these exact stacks.
- **The pessimistic constants come from laboratory cells**, more stressed than commercial stacks, and the semi-empirical laws are extrapolated beyond the duration of the tests.
- **One driving pattern and one wind profile for the use phase.** The fuel cell polarisation curve is fitted on all 12 road recordings, but the hydrogen consumption over the vehicle life is simulated by replaying one measured trip (WLTP-type, 2 033 s, 20.32 km) at every age; the electrolyser replays one 4-hour wind profile. Temperatures are constant.
- **Scope: stacks and tank only.** Auxiliaries (balance of plant), the station apart from compression, the rest of the vehicle and end of life are outside the system.

## 10. Main results

These results follow from the method of [section 3](#3-what-the-code-does) (details in [docs/METHOD.md](docs/METHOD.md)) and are valid within the limits of [section 9](#9-limits). "No ageing" is the same chain with stacks that never age: one stack of each converter, constant performance.

Default configuration: climate change (EF 3.1), French residual mix (79.6 g CO2-eq/kWh, AIB 2024 data), 200 000 km over 15 years.

| | No ageing | Optimistic | Central | Pessimistic |
|---|---|---|---|---|
| Fuel cell stacks over 15 years | 1 | 1 | 2 | 2 |
| Electrolyser stacks over 15 years | 1 | 2 | 3 | 3 |
| Electrolyser alone (kg CO2-eq/kg H2) | 4.31 | 4.53 (+5.1 %) | 4.57 (+5.9 %) | 4.66 (+8.2 %) |
| Tank alone (g CO2-eq/km) | 11.89 | 11.89 (0.0 %) | 12.04 (+1.3 %) | 12.64 (+6.4 %) |
| Fuel cell alone (g CO2-eq/km) | 61.9 | 63.4 (+2.4 %) | 82.2 (+32.8 %) | 83.4 (+34.6 %) |
| **Whole chain (g CO2-eq/km)** | **74.1** | **77.8 (+5.0 %)** | **97.2 (+31.1 %)** | **100.1 (+35.0 %)** |

Each value is a total: **use and fabrication**. For the whole chain, in g CO2-eq/km (rounded values):

| | No ageing | Optimistic | Central | Pessimistic |
|---|---|---|---|---|
| Use: electricity and water of electrolysis | 41.5 | 44.8 | 45.2 | 48.0 |
| Use: compression | 2.2 | 2.2 | 2.3 | 2.4 |
| Fabrication: fuel cell stacks | 18.5 | 18.5 | 37.0 | 37.0 |
| Fabrication: tank | 11.7 | 11.7 | 11.7 | 11.7 |
| Fabrication: electrolyser stacks | 0.3 | 0.7 | 1.0 | 1.1 |
| **Total** | **74.1** | **77.8** | **97.2** | **100.1** |

The hydrogen lost by permeation is counted in use, as extra hydrogen to produce.

The rise due to ageing, split into its two routes. Each line gives the part of the rise due to one route, as a % of the impact without ageing; the two lines add up to the total rise (within 0.1 because of rounding).

| Component | Route | Optimistic | Central | Pessimistic |
|---|---|---|---|---|
| Electrolyser alone | over-consumption (more electricity and water per kg) | +4.3 % | +4.3 % | +6.6 % |
| | replacement (extra stacks) | +0.8 % | +1.5 % | +1.5 % |
| | **both** | **+5.1 %** | **+5.9 %** | **+8.2 %** |
| Tank alone | over-consumption (hydrogen lost by permeation) | 0.0 % | +1.3 % | +6.4 % |
| | replacement (one tank in all cases) | 0.0 % | 0.0 % | 0.0 % |
| | **both** | **0.0 %** | **+1.3 %** | **+6.4 %** |
| Fuel cell alone | over-consumption (more hydrogen per km) | +2.4 % | +2.9 % | +4.8 % |
| | replacement (extra stack) | 0.0 % | +29.9 % | +29.9 % |
| | **both** | **+2.4 %** | **+32.8 %** | **+34.6 %** |
| Whole chain | over-consumption (electricity, water and compression) | +4.6 % | +5.2 % | +9.1 % |
| | replacement (fuel cell and electrolyser stacks) | +0.5 % | +25.9 % | +25.9 % |
| | **both** | **+5.0 %** | **+31.1 %** | **+35.0 %** |

What these numbers show:

- **The fuel cell is dominated by replacement.** One fuel cell stack is spread over the 200 000 km of a single vehicle; a second stack adds 18.5 g CO2-eq/km, that is 30 % of the impact of the fuel cell without ageing (61.9 g/km). In the central case, 91 % of the fuel cell rise comes from the extra stack.
- **The electrolyser is dominated by over-consumption.** One electrolyser stack is spread over about 1.19 million kg of hydrogen and weighs 0.8 % of the impact of 1 kg; the extra electricity matters more.
- **The result moves in steps, because the number of stacks is a whole number.** The fuel cell runs 5 554 h over 200 000 km: above that, 1 stack is enough (+6 %); between 2 777 and 5 554 h, 2 are needed (+31 %). What matters is crossing the 5 554 h threshold, not gaining a few hours.

![Rise of the chain as a function of the fuel cell stack lifetime](docs/figures/steps.png)

*Rise of the chain as a function of the lifetime of one fuel cell stack. Curve: only the fuel cell lifetime varies (linear model, other values of the central case); points: the three cases. Figure made by `scripts/plot_steps.py`.*

- **The fuel cell lifetime is the key input.** In the global sensitivity analysis, it explains almost all the variation of the rise (total Sobol index 0.94).

## 11. Cite, licence, contact

- **Cite:** see [CITATION.cff](CITATION.cff) (GitHub shows a "Cite this repository" button).
- **Licence:** code under MIT ([LICENSE](LICENSE)); data and documentation under CC BY 4.0 ([LICENSE-DATA.md](LICENSE-DATA.md)). Third-party sources keep their own terms ([data/README.md](data/README.md)).
- **Questions, errors or new data:** please open an issue on GitHub. Contributions of measured degradation data for commercial stacks are especially welcome, since they would replace the bracketing cases by a measurement.
