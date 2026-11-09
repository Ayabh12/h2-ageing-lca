# h2-ageing-lca

**How much does stack ageing change the life cycle assessment of a hydrogen mobility chain?**

This repository contains the models, data and code of a life cycle assessment (LCA) that accounts for the ageing of the stacks of a hydrogen chain.

The chain studied:

```
wind electricity -> PEM electrolyser (Nel MC250, 1.25 MW) -> compression (700 bar) -> type IV tank -> PEM fuel cell (Toyota Mirai II)
```

Ageing acts through two routes, computed separately:

1. **over-consumption**: the electrolyser needs more electricity per kg of hydrogen, the fuel cell more hydrogen per km;
2. **replacement**: a worn stack (10 % voltage change, DOE criterion) is replaced by a new one that must be manufactured.

Everything is parameterised. **Change a quantity, an inventory, an ageing rate or a model, run one command, and get the new results.**

## Quick start

```bash
git clone <this repository>
cd h2-ageing-lca
pip install -r requirements.txt
python scripts/run.py                 # default configuration (about 3 s)
python tests/test_reference_results.py
```

Default results (climate change, EF 3.1, ecoinvent 3.11 cut-off, French residual mix 79.6 g CO2-eq/kWh, 200 000 km over 15 years):

| | No ageing | Optimistic | Central | Pessimistic |
|---|---|---|---|---|
| Fuel cell stacks over 15 years | 1 | 1 | 2 | 2 |
| Electrolyser stacks over 15 years | 1 | 2 | 3 | 3 |
| Electrolyser alone (kg CO2-eq/kg H2) | 4.31 | 4.53 (+5.1 %) | 4.57 (+5.9 %) | 4.66 (+8.2 %) |
| Tank alone (g CO2-eq/km) | 11.89 | 11.89 (0.0 %) | 12.04 (+1.3 %) | 12.64 (+6.4 %) |
| Fuel cell alone (g CO2-eq/km) | 61.9 | 63.4 (+2.4 %) | 82.2 (+32.8 %) | 83.4 (+34.6 %) |
| Whole chain (g CO2-eq/km) | 74.1 | 77.8 (+5.0 %) | 97.2 (+31.1 %) | 100.1 (+35.0 %) |
| Whole chain, stacks counted prorata | 74.1 | +4.6 % | +14.7 % | +32.8 % |

Compression: 2.8 kWh/kg, 0.223 kg CO2-eq per kg of hydrogen; it does not age. Tank: fabrication 11.66 g CO2-eq/km plus the hydrogen lost by permeation. Residual mix data: AIB statistics, 2024.

The three cases: **optimistic** = linear model with the DOE targets; **central** = linear model with the DOE status; **pessimistic** = mechanistic model with constants from laboratory cells. See [docs/METHOD.md](docs/METHOD.md).

## Use your own values

All inputs are in [config/default.yaml](config/default.yaml), each with its source. Two ways to change them:

```bash
# one value from the command line
python scripts/run.py --set usage.compression_kWh_per_kg=3.0
python scripts/run.py --set usage.electricity_electrolyser=wind_FR
python scripts/run.py --set cases.central.fuel_cell.hours_to_end_of_life=6000
python scripts/run.py --set horizon.vehicle_km_total=250000 --set usage.stack_counting=prorata

# or a whole scenario: copy the file, edit it, run it
cp config/default.yaml config/my_case.yaml
python scripts/run.py --config config/my_case.yaml --out results/my_case
python scripts/plot.py --results results/my_case
```

From Python:

```python
import sys; sys.path.insert(0, "src")
from h2ageing import load_config, with_values, run

cfg = with_values(load_config(), **{"usage.compression_kWh_per_kg": 3.0})
res = run(cfg)
print(res["chain"])
```

What you can change, and where, is listed in [docs/CUSTOMISE.md](docs/CUSTOMISE.md): usage quantities, electricity source, horizon, hours of the electrolyser, ageing rates and constants, stack counting, fabrication impacts, inventories, measurements and the models themselves.

## Repository layout

```
config/default.yaml        all parameters, with sources
src/h2ageing/              the models
    pemfc.py               fuel cell: polarisation, ageing (linear and mechanistic), trip at constant power
    pemwe.py               electrolyser: profile, ageing (linear and mechanistic)
    tank.py                permeation of the type IV tank
    impacts.py             EF 3.1 impact data and single score
    chain.py               LCA of each converter and of the whole chain
    run.py                 runs all cases, builds the result tables
scripts/
    run.py                 command line: run a configuration, write CSV tables
    plot.py                bar chart of the chain per item
    threshold.py           impact versus stack lifetime, with the predictions of each ageing model
    sobol.py               global sensitivity analysis (Sobol indices) of the chain
    fuel_cell_tests.py     mechanistic fuel cell: crossover law, membrane criterion, mean speed
    fit_pemfc.py           fit the fuel cell polarisation curve on the road measurements
    fit_pemwe.py           fit the electrolyser model on the wind profile
    build_fabrication_brightway.py   recompute fabrication impacts from the inventories (needs ecoinvent)
data/                      measurements, fitted parameters, impacts, inventories (see data/README.md)
tests/                     the default configuration gives the reference results
notebooks/                 the original research notebooks (French), see notebooks/README.md
docs/                      method and customisation guide
```

## Data and ecoinvent

No ecoinvent dataset is distributed. `data/impacts` contains characterised EF 3.1 results only (impact of 1 kWh, of 1 kg of water, of one manufactured stack or tank). The foreground inventories (masses and energy of each stack, with the name of the ecoinvent activity used) are in `data/inventories`. With your own ecoinvent licence, `scripts/build_fabrication_brightway.py` recomputes the fabrication impacts after you change any amount. Details and sources: [data/README.md](data/README.md).

## Limits

The models describe the stacks only: auxiliaries (balance of plant), the refuelling station apart from compression, the rest of the vehicle and end of life are outside the system. No degradation rate has been measured on the stacks studied: the linear cases use rates declared by the DOE, and the pessimistic case uses constants from laboratory cells, which are more stressed than commercial stacks. The fuel cell result changes by steps with the number of stacks. See docs/METHOD.md.

## How to cite

See [CITATION.cff](CITATION.cff). Please cite this repository when you use the code or the data.

## Licence

Code: MIT ([LICENSE](LICENSE)). Data and documentation: CC BY 4.0 ([LICENSE-DATA.md](LICENSE-DATA.md)). Third-party sources keep their own terms (see data/README.md).
