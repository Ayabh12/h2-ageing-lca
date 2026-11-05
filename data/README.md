# Data

## measurements/

| File | Content | Origin |
|---|---|---|
| `mirai2_fuel_cell_signals.csv` | Toyota Mirai II fuel cell, all recordings at 1 s: time (s), vehicle speed (km/h), stack current (A), stack voltage (V), tank level (%). Time restarts at zero at each recording. | Road and standstill measurements described in chapter 1 of the thesis. Used to fit the polarisation curve. |
| `mirai2_fuel_cell_trip.csv` | Measured road trip used for the hydrogen balance: time (s), current (A), voltage (V); 2 033 s, 20.32 km, 0.196 kg of hydrogen (tank 56.0 % → 52.5 % of 5.6 kg). Missing values interpolated. | Same measurement campaign, from the experimental database of Ali Alhakim. |
| `nel_mc250_wind_profile.xlsx` | Nel MC250 PEM electrolyser (1.25 MW) driven by a wind profile, 4 h at 1 s (sheet `Profil_1s_source`), with the derived use-phase inventory (other sheets). | Built from the public NLR data set "Public Reference Data for Megawatt-Scale Hydrogen Electrolysis", run "wind-GE1.5MW 0.65-200". |

## parameters/

| File | Written by | Content |
|---|---|---|
| `pemwe_fit.json` | `scripts/fit_pemwe.py` | electrolyser new-state model and profile quantities (E0, H2, SEC0, Faraday efficiency, j_ref, V_ref, W0, W_j) |
| `pemfc_fit.json` | `scripts/fit_pemfc.py` | fuel cell polarisation parameters and the median curve used for the fit |

## impacts/ (characterised results, EF 3.1, ecoinvent 3.11 cut-off)

No ecoinvent dataset is included. These files contain characterised results only, computed in Brightway / Activity Browser by the authors.

| File | Content |
|---|---|
| `electricity_per_kWh.csv` | impact of 1 kWh: `residual_mix_FR` ("electricity, medium voltage, residual mix, FR", 79.6 g CO2-eq/kWh, reference), `average_mix_FR`, `nuclear_FR`, `wind_FR`, `photovoltaic` (3 kWp roof, CdTe) |
| `water_per_kg.csv` | impact of 1 kg of deionised water |
| `fabrication_per_unit.csv` | impact of one fuel cell stack (128 kW), one electrolyser stack (1.25 MW) and one type IV tank |
| `ef31_normalisation_weighting.csv` | EF 3.1 normalisation (per person) and weighting factors |

## inventories/ (foreground)

| File | Content | Source |
|---|---|---|
| `fuel_cell_stack_128kW.csv` | materials and manufacturing electricity of the fuel cell stack, with the ecoinvent 3.11 activity used for each flow | Mori et al. 2023 (48 kW stack), scaled by 128/48 |
| `electrolyser_stack_1p25MW.csv` | materials and assembly electricity of the electrolyser stack | Lundberg 2019 (per MW of stack), scaled to 1.25 MW; iridium counted as a resource flow only |
| `tank_type_IV.csv` | material masses and manufacturing energy of the tank (ecoinvent flows given by their Brightway code) | Benitez et al. 2021 (5.6 kg, 700 bar) |

The tank impact used in the article, 2 332 kg CO2-eq, is 2 075 kg for the materials and 257 kg for the manufacturing energy (338.64 kWh of high-voltage electricity, global market, and 43.2 kWh from natural gas co-generation). Set a row of the column `included_in_shipped_impact` to `no` to leave it out when you rebuild the tank.

## Licences

Data produced for this work: CC BY 4.0 (see `LICENSE-DATA.md`). The NLR data keep the terms of their publisher. ecoinvent data are not redistributed; characterised results are given for reproducibility.
