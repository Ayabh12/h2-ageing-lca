# Use and adapt the model

**English** | [Français](GUIDE.fr.md)

This page gathers everything needed to use the model: install and run it, change a value, the list of everything that can be changed, then, at the end, worked examples with their results. You only write what you change: the end-of-life search, the stack counting and the LCA are recomputed automatically.

Examples ready to run in Jupyter: [`examples/adapt_the_model.ipynb`](../examples/adapt_the_model.ipynb) and [`examples/check_and_examples.ipynb`](../examples/check_and_examples.ipynb).

1. [Install and run](#1-install-and-run)
2. [Change a value](#2-change-a-value)
3. [Everything that can be changed](#3-everything-that-can-be-changed)
4. [Check and share](#4-check-and-share)
5. [Worked examples](#5-worked-examples)

---

## 1. Install and run

Setup, once (Python 3.10 or later):

```bash
git clone https://github.com/Ayabh12/h2-ageing-lca
cd h2-ageing-lca
pip install -r requirements.txt
```

In Python or Jupyter, from the folder that contains `h2-ageing-lca`:

```python
import sys
sys.path.insert(0, "h2-ageing-lca/src")
from h2ageing import load_config, with_values, run

cfg = load_config()          # every input, read from config/default.yaml
```

```python
ref = run(cfg)
ref["chain"][["case", "total_g_per_km", "rise_pct"]].round(1)
```

| case | g CO2-eq/km | rise (%) |
|---|---|---|
| no_ageing | 74.1 | 0.0 |
| optimistic | 77.8 | 5.0 |
| central | 97.2 | 31.1 |
| pessimistic | 100.1 | 35.0 |

`run` returns a dictionary of tables: `life` (end of life and stacks), `fuel_cell`, `electrolyser`, `tank`, `chain` and `categories` (16 EF 3.1 categories). From the command line: `python scripts/run.py`.

To write the tables to a folder and draw the figures:

```bash
python scripts/run.py --out results
python scripts/plot.py --results results
```

The tables written to the output folder (`--out`) are:

| File | Content |
|---|---|
| `life.csv` | end of life and number of stacks of each converter, mean over-consumption |
| `electrolyser.csv` | electrolyser alone, climate change per kg of hydrogen |
| `tank.csv` | tank alone, per km: fabrication, hydrogen lost by permeation, total, rise |
| `fuel_cell.csv` | fuel cell alone, climate change per km: use, fabrication, total, rise, single score |
| `chain.csv` | whole chain per km, by item, rise and single score |
| `categories.csv` | the 16 EF 3.1 categories: share of fabrication and rise of each case |


### Repository layout

```
config/default.yaml        all inputs, each with its source (units in the key names)
src/h2ageing/              the models (Python package)
    pemfc.py               fuel cell: polarisation, ageing (linear and semi-empirical), trip at constant power
    pemwe.py               electrolyser: operating profile, ageing (linear and semi-empirical)
    tank.py                permeation of the type IV tank
    impacts.py             EF 3.1 impact data and single score
    chain.py               LCA of each component and of the whole chain
    run.py                 runs all cases, builds the result tables
scripts/                   command-line tools (list in docs/GUIDE.md)
data/
    measurements/          fuel cell road measurements, electrolyser wind profile
    parameters/            fitted polarisation parameters
    inventories/           foreground inventories (masses, energy, ecoinvent activity names)
    impacts/               characterised impacts (per kWh, per kg of water, per stack or tank)
tests/                     reference results and the tests that check them
notebooks/                 original research notebooks (French)
docs/                      method, user guide with examples, limits
examples/                  Jupyter notebooks: use and adapt the model in six levels; checks and examples with and without ecoinvent
```

### Reproduce every result

| Result | Command | Time |
|---|---|---|
| Three cases: end of life, stacks, each component, whole chain, 16 categories | `python scripts/run.py --out results` | ~2 s |
| Check against the reference values | `python tests/test_reference_results.py` (also run automatically on every push) | ~10 s |
| Bar chart of the chain by item (after `run.py`) | `python scripts/plot.py --results results` | ~2 s |
| Electricity sources, electrolyser hours, stack counting | `run.py` with `--set` (see the [worked examples](#5-worked-examples)) | ~2 s each |
| Impact versus stack lifetime (steps and thresholds) | `python scripts/threshold.py --out results` | ~30 s |
| Crossover law of the semi-empirical fuel cell model, mean speed | `python scripts/fuel_cell_tests.py` | ~10 s |
| Effect of each semi-empirical constant (published alternative values) | `python scripts/semi_empirical_constants.py` | ~5 s |
| Global sensitivity (Sobol indices, 10 240 runs) | `python scripts/sobol.py --out results` | ~15 min (2 cores) |
| Polarisation fits (they rewrite `data/parameters/` and give back the shipped parameters) | `python scripts/fit_pemfc.py`, `python scripts/fit_pemwe.py` | ~5 s each |
| Fabrication impacts from the inventories | `python scripts/build_fabrication_brightway.py --project <name>` (needs ecoinvent) | – |

The original research notebooks (in French, outputs included) are in [notebooks/](../notebooks/README.md); they give the same results with more figures.

## 2. Change a value

Three ways, as you prefer; the file `config/default.yaml` is never changed:

- **From the command line**: `python scripts/run.py --set key=value` (one `--set` per value).
- **In Python**: `with_values` returns a copy of the configuration with your values.

  ```python
  r = run(with_values(cfg, **{"cases.central.fuel_cell.hours_to_end_of_life": 5000.0}))
  ```
- **In a file**: copy `config/default.yaml`, change the values, and run `python scripts/run.py --config config/my_case.yaml` (see example 6).

All keys are listed in section 3.

## 3. Everything that can be changed

### 3.1 Usage quantities

| What | Key | Example |
|---|---|---|
| Compression energy | `usage.compression_kWh_per_kg` | `--set usage.compression_kWh_per_kg=3.2` |
| Water per kg of hydrogen | `usage.water_kg_per_kg_h2` | `--set usage.water_kg_per_kg_h2=9` |
| Electricity of the electrolyser | `usage.electricity_electrolyser` | `residual_mix_FR`, `average_mix_FR`, `nuclear_FR`, `wind_FR`, `photovoltaic` |
| Electricity of the compression | `usage.electricity_compression` | the same five sources as for the electrolyser, chosen separately (default `residual_mix_FR`) |
| Hours of the electrolyser per year | `usage.electrolyser_hours_per_year` | `--set usage.electrolyser_hours_per_year=7392` |
| Stack counting | `usage.stack_counting` | `integer` or `prorata` |
| Distance and horizon | `horizon.vehicle_km_total`, `horizon.years` | `--set horizon.vehicle_km_total=250000` |

To add another electricity source, add a column to `data/impacts/electricity_per_kWh.csv` (impact of 1 kWh in the 16 categories) and use its name.

### 3.2 Ageing

Each case of `cases` chooses a model for each converter.

**Linear model** (published rates):

```yaml
fuel_cell:
  model: linear
  hours_to_end_of_life: 6000          # hours until 10 % voltage loss
electrolyser:
  model: linear
  rate_uV_per_h_per_cell: 3.0
```

**Semi-empirical model** (laboratory constants):

```yaml
fuel_cell:
  model: semi_empirical
  ecsa_at_1000h: 0.67
  omega: 3.6
  voltage_loss_at_1p8_A_cm2_1000h_V: 0.045
  crossover_factor_1000h: 2.6
electrolyser:
  model: semi_empirical
  anode_activity_final: 0.1118
  anode_decay_time_h: 1000
  hfr_drift_V_per_h_at_test: 7.0e-6
  catalyst_layer_drift_V_per_h_at_test: 3.4e-6
  test_current_density_A_cm2: 3.0
  membrane_half_thickness_time_h: 80700
```

You can add a case (any name) or remove one; each case also gives the tank permeation `[P0, P15]` in mL/h/L. Other options: `fuel_cell.crossover_law` (`linear`, `exponential`, `constant`), the end-of-life criteria `fuel_cell.end_of_life_voltage_loss` and `electrolyser.end_of_life_voltage_rise`.

Constants of the semi-empirical model (keys under `cases.pessimistic.`):

| Constant | Key |
|---|---|
| Fuel cell: platinum surface after 1 000 h | `fuel_cell.ecsa_at_1000h` |
| Fuel cell: shape of the platinum law | `fuel_cell.omega` |
| Fuel cell: voltage loss at 1.8 A/cm² after 1 000 h | `fuel_cell.voltage_loss_at_1p8_A_cm2_1000h_V` |
| Fuel cell: crossover factor after 1 000 h | `fuel_cell.crossover_factor_1000h` |
| Electrolyser: final anode activity and its time constant | `electrolyser.anode_activity_final`, `electrolyser.anode_decay_time_h` |
| Electrolyser: resistance drifts and test current density | `electrolyser.hfr_drift_V_per_h_at_test`, `electrolyser.catalyst_layer_drift_V_per_h_at_test`, `electrolyser.test_current_density_A_cm2` |
| Electrolyser: membrane thinning | `electrolyser.membrane_half_thickness_time_h` |

The source of each reference value is given next to it in `config/default.yaml`. `scripts/semi_empirical_constants.py` changes them one at a time to other published values.

### 3.3 Another ageing law

| Law | Function to replace | Arguments (age `t` in hours, parameters `p`) |
|---|---|---|
| Fuel cell platinum surface | `pemfc.FuelCell.ecsa` | `t`, `p` |
| Fuel cell resistance | `pemfc.FuelCell.resistance` | `t`, `p` |
| Fuel cell crossover | `pemfc.FuelCell.crossover` | `t`, `p` |
| Electrolyser ageing (voltage, resistance, Faraday efficiency) | `pemwe.Electrolyser.state` | `t`, `p` |
| Tank permeation | `tank.Tank.permeation` | `t_years` (years), `p` |

The models are plain Python classes:

- `FuelCell.cell_voltage(I, t, p)` and `FuelCell.crossover(t, p)` in `src/h2ageing/pemfc.py`;
- `Electrolyser.state(t, p)` in `src/h2ageing/pemwe.py`;
- `Tank.permeation(t, p)` in `src/h2ageing/tank.py`.

To try another ageing law, change these functions (or add a new `model:` value in `parameters()`; see example 7). Everything downstream (end of life, number of stacks, LCA) uses them unchanged. Run `python tests/test_reference_results.py` before your change to check your installation, and expect the tests to fail after it: they compare with the reference results of the default configuration.

### 3.4 Fabrication

**Without an ecoinvent licence.** The model then uses impacts already computed with ecoinvent 3.11 (in `data/impacts`, for the 16 EF 3.1 categories): the impact of **1 kWh** of electricity for each of the five sources, of **1 kg** of deionised water, and of the **fabrication of one unit** of each component (one fuel cell stack, one electrolyser stack, one tank). The model computes the quantities (kWh, kg of water, number of stacks) and multiplies them by these impacts. All quantities can therefore be changed, but not the content of a fabrication inventory.

To use your own fabrication impact, edit `data/impacts/fabrication_per_unit.csv` (impact of one fuel cell stack, one electrolyser stack and one tank in the 16 categories), or add a column and point `fabrication.fuel_cell_stack`, `fabrication.electrolyser_stack` or `fabrication.tank` to it. A stack of another size can be represented with `electrolyser.stack_inventory_scale`.

**With an ecoinvent licence:**

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
5. **Change an inventory**: in `data/inventories/*.csv`, change an amount, the ecoinvent activity or its location, or set `included` to `no` to leave a row out (columns explained in [data/inventories/README.md](../data/inventories/README.md)).
6. **Recompute**: run step 3 again with another output file.
7. **Use the new impacts in the model**: `python scripts/run.py --set fabrication.file=results/<file>.csv --out results/<name>`.

If the script stops with "0 matches" or "2 matches", the ecoinvent activity named in the inventory was not found, or not found once: check its name, location and reference product in your ecoinvent database. If the download fails, check that your ecoinvent account gives access to version 3.11.

All these steps, with the check of the 16 categories and examples with and without a licence, including examples that change a constant, a law or the model of a case, then the 16 impact categories and the sensitivity (electricity source, lifetime threshold, Sobol) (expected values given), are ready to run in Jupyter: [examples/check_and_examples.ipynb](../examples/check_and_examples.ipynb).

### 3.5 Measurements, equipment and data

| You have | Replace | Then |
|---|---|---|
| polarisation measurements of another fuel cell or electrolyser | the files in `data/measurements/` | `python scripts/fit_pemfc.py` or `fit_pemwe.py` |
| another fabrication inventory | the amounts in `data/inventories/` | `python scripts/build_fabrication_brightway.py` (needs ecoinvent) |
| impacts from another database or method | the files in `data/impacts/` | nothing: they are read directly |
| another electricity source | a new column in `data/impacts/electricity_per_kWh.csv` | use its name in `usage.electricity_electrolyser` |

- Another fuel cell or trip: replace `data/measurements/mirai2_fuel_cell_trip.csv` (columns `time_s`, `current_A`, `voltage_V`), give its distance and measured hydrogen (`fuel_cell.trip_distance_km`, `fuel_cell.trip_h2_measured_kg`), the number of cells and the active area, and refit the polarisation curve with `scripts/fit_pemfc.py` on your signals.
- Another electrolyser or profile: run `scripts/fit_pemwe.py --profile <file> --n-cells ... --area-cm2 ...`; it writes the parameter file read by the model (`electrolyser.params_file`).

### 3.6 Lifetime threshold and global sensitivity

```bash
python scripts/threshold.py --out results    # impact versus stack lifetime, model predictions placed on it
python scripts/sobol.py --out results        # Sobol indices of the chain (about 15 min on 2 cores)
```

`threshold.py` varies the stack lifetime with the linear model and places each configured case on the curve. It also separates the two effects of the choice of ageing model: the predicted end of life, and the shape of the trajectory at equal end of life (linear model set to the end of life of the semi-empirical model).

`semi_empirical_constants.py` changes each constant of the semi-empirical model alone to another published value and ranks their effect; edit `VARIANTS` to test your own values.

`fuel_cell_tests.py` (`python scripts/fuel_cell_tests.py`) tests the semi-empirical fuel cell model: crossover law, an extra membrane end-of-life criterion (crossover threshold) and the mean speed.

`sobol.py` reads the factors and their ranges in `global_sensitivity` of the configuration. Change a range, add or remove a factor among those listed, or change `samples`.

## 4. Check and share

- **Check.** `python tests/test_reference_results.py` checks that the default configuration still gives the reference results. Run it before changing the code; after a change of a law, it is expected to fail, since the results change.
- **Ask a question or report an error.** Open an *Issue* on GitHub (tab *Issues*, *New issue*). Questions and answers stay public, so the next user finds them.
- **Keep your own version online.** Click *Fork* on GitHub: you get your own copy of the repository, which you can modify freely. It shows "forked from Ayabh12/h2-ageing-lca".
- **Propose an improvement.** From your fork, open a *Pull request*. The changes are reviewed before being merged; new measured degradation data for commercial stacks are especially welcome.

Nobody can change this repository without the agreement of its owner: forks and local copies are independent.

---

## 5. Worked examples

Each example asks a question, gives the command that answers it, and shows the result obtained with the shipped data (climate change, whole chain, g CO2-eq/km). All commands run in a few seconds, without ecoinvent. Change the values to answer your own question.

The reference results, for comparison:

| | No ageing | Optimistic | Central | Pessimistic |
|---|---|---|---|---|
| Whole chain (g CO2-eq/km) | 74.12 | 77.84 (+5.0 %) | 97.15 (+31.1 %) | 100.06 (+35.0 %) |

### 1. What if the electrolyser runs on wind electricity?

**Why ask:** the reference uses the French residual mix, the most carbon-intensive source tested. A project with a wind power purchase agreement would use another source.

```bash
python scripts/run.py --set usage.electricity_electrolyser=wind_FR
```

| | No ageing | Optimistic | Central | Pessimistic |
|---|---|---|---|---|
| Whole chain (g CO2-eq/km) | 41.22 | 42.32 (+2.7 %) | 61.27 (+48.6 %) | 61.97 (+50.3 %) |

**What it shows:** the chain emits much less, but the relative effect of ageing is larger. The replacement stacks add the same impact whatever the electricity, and they weigh more when the rest is cleaner. Available sources: `residual_mix_FR`, `average_mix_FR`, `nuclear_FR`, `wind_FR`, `photovoltaic`; add your own as a column of `data/impacts/electricity_per_kWh.csv`.

### 2. What if my fuel cell stack lasts longer?

**Why ask:** the central case uses 4 100 h to end of life (best DOE fleet, 2006–2016). A newer stack may last longer.

```bash
python scripts/run.py --set cases.central.fuel_cell.hours_to_end_of_life=6000
```

| | Central (reference, 4 100 h) | Central with 6 000 h |
|---|---|---|
| Fuel cell stacks | 2 | 1 |
| Whole chain (g CO2-eq/km) | 97.15 (+31.1 %) | 78.88 (+6.4 %) |

**What it shows:** above the horizon of 5 554 operating hours, a single stack is enough, and the rise falls from +31 % to +6 %. Example 4 gives the exact thresholds.

### 3. What if the vehicle drives less?

**Why ask:** 200 000 km is the Toyota target for the Mirai II stack; a vehicle may be scrapped earlier.

```bash
python scripts/run.py --set horizon.vehicle_km_total=150000
```

| | No ageing | Optimistic | Central | Pessimistic |
|---|---|---|---|---|
| Whole chain (g CO2-eq/km) | 84.25 | 87.56 (+3.9 %) | 113.87 (+35.2 %) | 116.23 (+38.0 %) |

**What it shows:** fabrication is spread over fewer kilometres, so every value rises, and so does the weight of the replacement stack.

### 4. How long must a fuel cell stack last to avoid a replacement?

**Why ask:** for a manufacturer or a fleet operator, the useful question is the threshold, not the exact lifetime.

**The idea.** Over its life (200 000 km), the vehicle uses its fuel cell for 5 554 hours: this is the horizon. The number of stacks needed depends only on how long one stack lasts compared with this horizon:

- a stack that lasts **more than 5 554 h** lasts the whole life of the vehicle: **1 stack**;
- a stack that lasts **between 2 777 h (half the horizon) and 5 554 h** fails before the end and needs one replacement: **2 stacks**;
- a stack that lasts **between 1 851 h (a third of the horizon) and 2 777 h** needs two replacements: **3 stacks**.

```bash
python scripts/threshold.py --out results
```

It computes the impact for every stack lifetime from 1 500 to 12 000 h (`results/threshold_fuel_cell.csv`) and places the three cases with respect to the thresholds (`results/model_choice.csv`). Results with the shipped data:

| Stack lifetime | Fuel cell stacks | Whole chain rise |
|---|---|---|
| 1 851 to 2 777 h | 3 | about +56 % |
| 2 777 to 5 554 h | 2 | about +31 % |
| more than 5 554 h | 1 | about +6 % |

**What it shows:** the result moves by steps. A stack that lasts 4 100 h and one that lasts 5 000 h both need a replacement, so they give almost the same result (+31.1 % and +31.4 %). A stack that goes from 5 500 to 5 600 h crosses the threshold: one stack is enough, and the rise falls from about +31 % to about +7 %. Gaining a few hundred hours is useless unless it crosses a threshold; for this vehicle, the target is to exceed 5 554 h.

### 5. What if I use my own ageing constants?

**Why ask:** the pessimistic case uses constants measured on laboratory cells. You may have other measurements.

```bash
python scripts/semi_empirical_constants.py
```

It changes each constant of the semi-empirical model alone, to another published value, and prints the end of life, stacks and rise. Output with the shipped data:

| Constant changed | Fuel cell end of life ; stacks | Chain rise |
|---|---|---|
| none (pessimistic reference) | 2 895 h ; 2 | +35.0 % |
| fuel cell high-current loss 27 mV instead of 45 mV | 5 652 h ; 1 | +12.8 % |
| fuel cell crossover factor 1.4 instead of 2.6 | 2 895 h ; 2 | +33.2 % |
| fuel cell platinum surface 0.65 instead of 0.67 | 2 909 h ; 2 | +35.0 % |
| electrolyser HFR drift 0 | 2 895 h ; 2 | +34.6 % |

**What it shows:** one constant, the fuel cell voltage loss at high current, decides the number of stacks; it is the one to measure first. Edit the `VARIANTS` list at the top of the script to test your own values, or set any constant directly, for example:

```bash
python scripts/run.py --set cases.pessimistic.fuel_cell.voltage_loss_at_1p8_A_cm2_1000h_V=0.035
```

### 6. Describe your own case in a configuration file

**Example: a manufacturer whose fuel cell stack lasts 7 000 h and whose electrolyser runs on wind electricity.** Copy the configuration, change the two values, and keep the source of each change in a comment:

```bash
cp config/default.yaml config/my_case.yaml
```

```yaml
# config/my_case.yaml
usage:
  electricity_electrolyser: wind_FR        # wind power purchase agreement
cases:
  central:
    fuel_cell:
      model: linear
      hours_to_end_of_life: 7000           # our own endurance test
```

```bash
python scripts/run.py --config config/my_case.yaml
```

Central case: one stack is enough, 42.7 g CO2-eq/km, and the rise due to ageing falls to +3.7 % (instead of +31.1 % in the reference). The file `my_case.yaml` documents the case completely: anyone can rerun it and get the same result.

### 7. Test another ageing law

**Example: a modeller who thinks that the fuel cell resistance grows as the square root of time, not linearly.** They write their law, plug it in place of the original one, and put the original back afterwards:

```python
import numpy as np
from h2ageing import pemfc

original_law = pemfc.FuelCell.resistance

def my_resistance(self, t, p):
    """Resistance growing as the square root of time; same value as the linear law at 1 000 h."""
    t = np.asarray(t, float)
    return self.R0 * (1 + p.get("k_R", 0.0) * 1000 * np.sqrt(t / 1000))

pemfc.FuelCell.resistance = my_resistance
r = run(cfg)
pemfc.FuelCell.resistance = original_law
```

Pessimistic case: with this law, the resistance grows more slowly after the 1 000 h of the test; the end of life moves to 6 370 h, one stack is enough, and the chain rise is +13.0 %. Only the law was written; the voltage at every age, the end of life, the hydrogen consumption, the number of stacks and the LCA are recomputed.

### 8. Which inputs matter most, all together?

**Why ask:** the examples above change one input at a time. The global sensitivity analysis changes eight inputs together and ranks them.

**What a Sobol analysis is.** It varies all the inputs together, many times (10 240 runs), and measures which share of the variation of the result each input explains. Its total index goes from 0 (the input does not matter) to 1 (the input explains all the variation, alone or together with the others).


```bash
python scripts/sobol.py --out results      # about 15 min on 2 cores
```

**What it shows:** the absolute impact depends mostly on the electricity source (total Sobol index 0.78); the rise due to ageing depends almost only on the fuel cell stack lifetime (0.94). The factors and their ranges are in `global_sensitivity` of `config/default.yaml`.

### 9. What if the last stack gets a second life?

**Why ask:** the reference counts every started stack as a whole stack (`integer`). If the remaining life of the last stack is used elsewhere, only the share of life used should be counted (`prorata`).

```bash
python scripts/run.py --set usage.stack_counting=prorata
```

| | Optimistic | Central | Pessimistic |
|---|---|---|---|
| Rise, integer counting (reference) | +5.0 % | +31.1 % | +35.0 % |
| Rise, prorata counting | +4.6 % | +14.7 % | +32.8 % |

**What it shows:** only the central case changes much, because its second fuel cell stack is used at 35 % only before the end of the horizon. Prorata is a lower bound: it assumes a second-life route that does not exist today for these stacks.
