# Use and adapt the model

This page shows how someone else can use this model for their own question, from simply running it to replacing an ageing law. Each level comes with an example and the result it gives with the shipped data. You only write what you change: the end-of-life search, the stack counting and the LCA are recomputed automatically.

The same examples, ready to run in Jupyter: [`examples/adapt_the_model.ipynb`](../examples/adapt_the_model.ipynb).

| Level | You want to… | You change | Typical user |
|---|---|---|---|
| 1 | reproduce the results | nothing | student, reviewer |
| 2 | ask the model a question | one or a few inputs, from the command line or Python | LCA practitioner |
| 3 | describe your own case | a copy of the configuration file | engineer, project developer |
| 4 | use your own ageing measurements | the constants of the ageing models | degradation researcher |
| 5 | test another ageing law | one Python function | modeller |
| 6 | use your own equipment or inventories | the data files | manufacturer, LCA practitioner |

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

---

## Level 1: reproduce the results

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

## Level 2: ask the model a question

**Example: "what if my fuel cell stack lasts 5 000 h?"** `with_values` returns a copy of the configuration with the values you give; the configuration file is not modified.

```python
r = run(with_values(cfg, **{"cases.central.fuel_cell.hours_to_end_of_life": 5000.0}))
r["chain"][["case", "total_g_per_km", "rise_pct"]].round(1)
```

Central case: 2 stacks, 97.4 g CO2-eq/km, +31.4 %. Almost the same as with 4 100 h, because a stack that lasts 5 000 h still stops before the 5 554 operating hours of the vehicle.

**The natural next question: "from which lifetime is one stack enough?"**

```python
for d in [3000, 4100, 5000, 5554, 6000, 7000]:
    x = run(with_values(cfg, **{"cases.central.fuel_cell.hours_to_end_of_life": float(d)}))
    stacks = x["life"].set_index("case").loc["central", "fuel_cell_stacks"]
    rise = x["chain"].set_index("case").loc["central", "rise_pct"]
    print(f"{d} h -> {stacks:.0f} stack(s), chain rise +{rise:.1f} %")
```

| Stack lifetime | Stacks | Chain rise |
|---|---|---|
| 3 000 h | 2 | +31.4 % |
| 4 100 h | 2 | +31.1 % |
| 5 000 h | 2 | +31.4 % |
| 5 554 h | 2 | +31.6 % |
| 6 000 h | 1 | +6.4 % |
| 7 000 h | 1 | +6.0 % |

The answer is a threshold: below 5 554 h the result barely moves; above it, it falls by 25 points.

The same from the command line: `python scripts/run.py --set cases.central.fuel_cell.hours_to_end_of_life=5000`. More questions of this kind, with their results: [USE_CASES.md](USE_CASES.md).

## Level 3: describe your own case in a configuration file

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

## Level 4: use your own ageing constants

**Example: a researcher who measured, on their own cell, a voltage loss of 27 mV at 1.8 A/cm² after 1 000 h** (instead of 45 mV for the cell used in the pessimistic case):

```python
r = run(with_values(cfg, **{"cases.pessimistic.fuel_cell.voltage_loss_at_1p8_A_cm2_1000h_V": 0.027}))
r["life"][["case", "fuel_cell_end_of_life_h", "fuel_cell_stacks"]].round(0)
```

Pessimistic case: the end of life goes from 2 895 h to 5 652 h, one stack is enough, and the chain rise falls from +35.0 % to +12.8 %.

Constants of the mechanistic model (keys under `cases.pessimistic.`):

| Constant | Key |
|---|---|
| Fuel cell: platinum surface after 1 000 h | `fuel_cell.ecsa_at_1000h` |
| Fuel cell: shape of the platinum law | `fuel_cell.omega` |
| Fuel cell: voltage loss at 1.8 A/cm² after 1 000 h | `fuel_cell.voltage_loss_at_1p8_A_cm2_1000h_V` |
| Fuel cell: crossover factor after 1 000 h | `fuel_cell.crossover_factor_1000h` |
| Electrolyser: final anode activity and its time constant | `electrolyser.anode_activity_final`, `electrolyser.anode_decay_time_h` |
| Electrolyser: resistance drifts and test current density | `electrolyser.hfr_drift_V_per_h_at_test`, `electrolyser.catalyst_layer_drift_V_per_h_at_test`, `electrolyser.test_current_density_A_cm2` |
| Electrolyser: membrane thinning | `electrolyser.membrane_half_thickness_time_h` |

The source of each reference value is given next to it in `config/default.yaml`. `scripts/mechanistic_constants.py` changes them one at a time to other published values.

## Level 5: test another ageing law

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

| Law | Function to replace | Arguments (age `t` in hours, parameters `p`) |
|---|---|---|
| Fuel cell platinum surface | `pemfc.FuelCell.ecsa` | `t`, `p` |
| Fuel cell resistance | `pemfc.FuelCell.resistance` | `t`, `p` |
| Fuel cell crossover | `pemfc.FuelCell.crossover` | `t`, `p` |
| Electrolyser ageing (voltage, resistance, Faraday efficiency) | `pemwe.Electrolyser.state` | `t`, `p` |
| Tank permeation | `tank.Tank.permeation` | `t_years` (years), `p` |

To keep a new law for good, write it in the module and add a new `model:` value in `parameters()` ([CUSTOMISE.md](CUSTOMISE.md), section 6).

## Level 6: use your own equipment, measurements or inventories

| You have | Replace | Then |
|---|---|---|
| polarisation measurements of another fuel cell or electrolyser | the files in `data/measurements/` | `python scripts/fit_pemfc.py` or `fit_pemwe.py` |
| another fabrication inventory | the amounts in `data/inventories/` | `python scripts/build_fabrication_brightway.py` (needs ecoinvent) |
| impacts from another database or method | the files in `data/impacts/` | nothing: they are read directly |
| another electricity source | a new column in `data/impacts/electricity_per_kWh.csv` | use its name in `usage.electricity_electrolyser` |

Details for each file: [CUSTOMISE.md](CUSTOMISE.md) and [data/README.md](../data/README.md).

---

## Checking and sharing your changes

- **Check.** `python tests/test_reference_results.py` checks that the default configuration still gives the reference results. Run it before changing the code; after a change of a law, it is expected to fail, since the results change.
- **Ask a question or report an error.** Open an *Issue* on GitHub (tab *Issues*, *New issue*). Questions and answers stay public, so the next user finds them.
- **Keep your own version online.** Click *Fork* on GitHub: you get your own copy of the repository, which you can modify freely. It shows "forked from Ayabh12/h2-ageing-lca".
- **Propose an improvement.** From your fork, open a *Pull request*. The changes are reviewed before being merged; new measured degradation data for commercial stacks are especially welcome.

Nobody can change this repository without the agreement of its owner: forks and local copies are independent.
