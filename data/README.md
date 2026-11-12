# Data

## measurements/

| File | Content | Origin |
|---|---|---|
| `mirai2_fuel_cell_signals.csv` | Toyota Mirai II fuel cell, all recordings at 1 s: time (s), vehicle speed (km/h), stack current (A), stack voltage (V), tank level (%). Time restarts at zero at each recording. | Road and standstill measurements on a Toyota Mirai II. Used to fit the polarisation curve. |
| `mirai2_fuel_cell_trip.csv` | Measured road trip used for the hydrogen balance: time (s), current (A), voltage (V); 2 033 s, 20.32 km, 0.196 kg of hydrogen (tank 56.0 % → 52.5 % of 5.6 kg). Missing values interpolated. | Same measurement campaign, from the experimental database of Ali Alhakim. |
| `nel_mc250_wind_profile.xlsx` | Nel MC250 PEM electrolyser (1.25 MW) driven by a wind profile, 4 h at 1 s (sheet `Profil_1s_source`), with the derived use-phase inventory (other sheets). | Built from the public NLR data set "Public Reference Data for Megawatt-Scale Hydrogen Electrolysis", run "wind-GE1.5MW 0.65-200". |

## parameters/

| File | Written by | Content |
|---|---|---|
| `pemfc_fit.json` | `scripts/fit_pemfc.py` | fuel cell: fitted polarisation parameters, fit quality, and the measured curve used for the fit |
| `pemwe_fit.json` | `scripts/fit_pemwe.py` | electrolyser: fitted polarisation parameters, fit quality, quantities of the measured profile, and the test of the Tafel slope |

Both files are rewritten by their script, which gives back the shipped values. A guide to every entry is given in [Reading the parameter files](#reading-the-parameter-files) below.

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

The tank impact of the default configuration, 2 332 kg CO2-eq, is 2 075 kg for the materials and 257 kg for the manufacturing energy (338.64 kWh of high-voltage electricity, global market, and 43.2 kWh from natural gas co-generation). Set a row of the column `included_in_shipped_impact` to `no` to leave it out when you rebuild the tank.

## Licences

Data produced for this work: CC BY 4.0 (see `LICENSE-DATA.md`). The NLR data keep the terms of their publisher. ecoinvent data are not redistributed; characterised results are given for reproducibility.

## Reading the parameter files

This section explains the two files of `parameters/` for readers who are not specialists of electrochemistry.

### What is fitted, and why

A stack is a pile of cells. The voltage of a cell depends on the current it carries: this relation is the **polarisation curve**. It starts from a theoretical voltage (the reversible voltage), then moves away from it because of three kinds of losses:

- **activation losses**: the energy needed to make the reaction start at the electrode, which grow with the logarithm of the current;
- **ohmic losses**: the electrical resistance of the membrane, contacts and layers, proportional to the current;
- **transport losses**: at high current, the gases and water cannot reach or leave the electrode fast enough.

In an electrolyser, losses are *added* to the reversible voltage (more electricity is needed); in a fuel cell, they are *subtracted* (less electricity is produced).

The polarisation model has a few unknown parameters. **Fitting** means choosing their values so that the model reproduces the measured voltage as closely as possible (bounded least squares). Each parameter is kept within a range that encloses published values ([docs/METHOD.md](../docs/METHOD.md)). These fitted values describe the stacks **at the reference state, the state measured**; ageing is then applied to them.

### `pemfc_fit.json` (fuel cell, Toyota Mirai II)

| Entry | In plain words | Value | Unit |
|---|---|---|---|
| `i0c_A_cm2` | how easily the oxygen reaction starts at the cathode (exchange current density); the higher, the smaller the activation loss | 1.52e-6 | A/cm² |
| `R0_ohm_cm2` | electrical resistance of one cell, per cm² of active area | 0.0462 | Ω·cm² |
| `Bc_V` | size of the transport loss at high current | 0.026 | V |
| `ilim_A_cm2` | limiting current density: the current at which gas transport would block the reaction | 2.30 | A/cm² |
| `RMSE_mV_per_cell` | average gap between model and measurement, per cell (root mean square error); the smaller, the better | 1.99 | mV |
| `R2` | share of the variation of the measured voltage explained by the model (1 = perfect) | 0.9989 | – |
| `starts`, `starts_reaching_minimum` | the fit is started from 200 random initial values; all 200 reach the same result, so the result does not depend on the starting point | 200 / 200 | – |
| `median_points` | the measured polarisation curve used for the fit (18 points), see below | – | – |

Each entry of `median_points` is one class of current, built from the stable parts of the 12 road recordings:

| Field | Meaning |
|---|---|
| `I` | stack current (A) |
| `U` | median stack voltage measured at this current (V) |
| `n` | number of measured points (1 per second) in this class |
| `n_rec` | number of recordings, out of 12, that contain this class |

Example: `{"I": 33.2, "U": 282.25, "n": 326, "n_rec": 11}` means that at 33.2 A, the median stack voltage is 282.25 V, from 326 measured seconds in 11 different recordings. Using medians of many seconds from many recordings removes the noise of single measurements.

### `pemwe_fit.json` (electrolyser, Nel MC250, at 80 °C)

Fitted model:

| Entry | In plain words | Value | Unit |
|---|---|---|---|
| `T_K` | temperature of the model (80 °C) | 353.15 | K |
| `Erev` | reversible voltage of a cell at this temperature: the theoretical minimum | 1.182 | V |
| `b_tafel` | Tafel slope: how fast the activation loss grows with the current (fixed from the literature, see `fits_pente`) | 0.046 | V per decade |
| `alpha_a` | anode transfer coefficient, computed from the Tafel slope | 0.76 | – |
| `i0a` | how easily the oxygen reaction starts at the anode (exchange current density) | 9.36e-10 | A/cm² |
| `R0` | electrical resistance of one cell, per cm² | 0.216 | Ω·cm² |
| `Bc` | size of the transport loss; it reaches zero, because the measured curve shows no transport loss up to 2 A/cm² | ≈ 0 | V |
| `ilim` | limiting current density, fixed above the highest measured current; without transport loss it has no effect | 3.0 | A/cm² |
| `RMSE_mV`, `R2` | fit quality on the 14 400 points of the profile (see the fuel cell table) | 3.97 ; 0.9993 | mV ; – |

Quantities of the measured 4-hour profile (reference state):

| Entry | In plain words | Value | Unit |
|---|---|---|---|
| `E0` | electricity used by the stack over the profile | 2 841 | kWh |
| `H20` | hydrogen produced over the profile | 52.93 | kg |
| `SEC0` | electricity per kg of hydrogen (`E0 / H20`), the key quantity for the LCA | 53.68 | kWh/kg |
| `etaF0` | Faraday efficiency: share of the current that really produces hydrogen (the rest is lost through the membrane) | 0.977 | – |
| `j_ref` | mean current density over the profile; the end of life is checked at this current | 1.20 | A/cm² |
| `Vref0` | cell voltage at `j_ref` | 1.860 | V |
| `Vmean0` | mean cell voltage over the profile | 1.855 | V |
| `W0`, `Wj` | weights used to update the profile energy when the stack ages: `E(t) = E0 + ΔV × W0 + ΔR × Wj`, for a uniform voltage rise ΔV and a resistance rise ΔR | 1 470 ; 2 237 | kWh/V ; kWh/(Ω·cm²) |
| `decomposition_jref_mV` | where the voltage above `Erev` goes at `j_ref`: 419 mV of activation loss, 259 mV of ohmic loss, 0 of transport loss (1.182 + 0.419 + 0.259 = 1.860 V) | – | mV |

Test of the Tafel slope (`fits_pente`): the model is fitted three times, with the Tafel slope fixed at 46 mV per decade (value kept, Padgett et al. 2025) and at 43.3 and 49 mV per decade (extreme values measured by Padgett et al. 2023). For each fit: `b (mV/déc)` the slope, `alpha_a`, `i0a`, `Rtot` and `Bc` the fitted parameters, `RMSE_mV` and `MAE_mV` the average gaps (root mean square and absolute), `R2` the quality.

| Tafel slope | i0a (A/cm²) | Rtot (Ω·cm²) | RMSE (mV) |
|---|---|---|---|
| 43.3 mV/dec | 2.9e-10 | 0.217 | 3.99 |
| 46 mV/dec (kept) | 9.4e-10 | 0.216 | 3.97 |
| 49 mV/dec | 3.0e-9 | 0.214 | 3.95 |

The three fits are equally good: the measured profile cannot tell which slope is right, so the slope is taken from the literature instead of being fitted. When the slope changes, `i0a` changes to compensate, and the resistance barely moves.

