# Method

This page summarises what the code computes and why. Each value of `config/default.yaml` gives its source.

## 1. Functional units and system

| Assessment | Functional unit | What ages |
|---|---|---|
| Fuel cell alone | 1 km driven | fuel cell stack only; it receives hydrogen from the studied electrolyser at its reference state (no ageing, stack fabrication excluded), compressed: 4.503 kg CO2-eq/kg |
| Electrolyser alone | 1 kg of hydrogen produced | electrolyser stack |
| Whole chain | 1 km driven | electrolyser, tank (permeation) and fuel cell together |

Horizon: 15 years, 200 000 km (`horizon`). Electricity: French residual mix by default (79.6 g CO2-eq/kWh), the mix of a grid-connected electrolyser that buys no guarantees of origin; the measured wind profile only gives the electricity used per kg of hydrogen and its change with age, not the origin of the electricity. Each assessment compares the chain with ageing to the same chain without ageing (same profile, electricity, horizon, boundaries and inventories, one stack of each converter). Inside the system: electricity and water of the electrolyser, compression electricity, manufacture of the stacks and of the tank, hydrogen lost by permeation. Outside: auxiliaries, station apart from compression, rest of the vehicle, transport, end of life.

## 2. Fuel cell (`src/h2ageing/pemfc.py`)

**Polarisation.** The full cell voltage contains the activation and transport losses of both electrodes and the ohmic loss. Only the losses of the oxygen electrode are kept (the cathode for the fuel cell, the anode for the electrolyser), for two reasons: the hydrogen reaction has an exchange current several orders of magnitude higher on platinum in acid medium (Durst et al. 2014), so its loss is small and nearly proportional to the current, hence included in R; and the activation losses of the two electrodes both vary as ln j, so a single voltage-current curve cannot separate them. The fuel cell cell voltage is:

V(j, t) = E_rev(T) − RT/(α_c F) · ln( j / (i0c · S(t)) ) − R(t) · j + B_c · ln(1 − j / i_lim)

E_rev(T) = 1.229 − 0.85·10⁻³ (T − 298.15). The four parameters i0c, R0, B_c and i_lim are fitted on quasi-steady points of the road measurements (`scripts/fit_pemfc.py`), by bounded least squares. Bounds and the published values they enclose: log10 i0c from −12 to −1 (Vetter & Schumacher 2019; Colombo et al. 2023); R0 from 0 to 0.3 Ω cm² (Colombo et al. 2023); B_c from 0 to 0.3 V (Almodfer et al. 2022); i_lim from 2.03 to 6 A/cm² (Bielefeld et al. 2024), the lower bound just above the highest measured current density.

**Hydrogen balance.** The measured trip (time, current, voltage, 2 033 s, 20.32 km) is replayed at each age at constant power: the current that delivers the measured power is found by bisection (40 iterations), with a point-by-point anchoring factor so that the model gives the measured current at age zero. The hydrogen consumed is Faraday's law plus a loss current: the gap between the measured hydrogen (0.196 kg) and Faraday's law is kept constant; the rise of the crossover is added to it.

**Ageing, mechanistic model** (pessimistic case):
- platinum surface: dS/dt = −k S² exp(ω S) (Verducci et al.), k chosen so that S(1000 h) equals the value measured by Colombo et al. (2023). k is found by inverting the tabulated integral g(S) = ∫_S^1 exp(−ω s)/s² ds (trapezoidal rule, 6 000 points);
- transport resistance: R(t) = R0 + r t (written R0 (1 + k_R t) in the code, with k_R = r / R0), where r = [ΔV(1.8 A/cm², 1000 h) − RT/(α_c F) ln(1/S_1000)] / 1.8 / 1000: the voltage loss measured at high current, minus the part already due to the platinum loss;
- crossover: 2 mA/cm² at age zero, multiplied by the factor measured in 1000 h (linear law by default; exponential and constant laws available).

**Ageing, linear model** (optimistic and central cases): V(t) = V(0) − μ t, with μ = 10 % of the cell voltage at 300 A divided by the published hours to end of life (8 000 h DOE target, 4 100 h DOE best fleet). The crossover stays constant.

**End of life**: age at which the stack voltage at 300 A has lost 10 % (DOE), found with Brent's method between 0 and 60 000 h.

## 3. Electrolyser (`src/h2ageing/pemwe.py`)

**New state** (fitted by `scripts/fit_pemwe.py` on the 4 h wind profile, 1 s steps):

V(j) = E_rev(T) + RT/(2 α_a F) · ln(j / i0a) + R j − B_c · ln(1 − j / i_lim)

α_a is fixed by the Tafel slope of Padgett et al. (46 mV/dec at 80 °C); i0a, R and B_c are fitted (bounded least squares, trust region reflective, 50 starts, seed 180). Bounds and the published values they enclose: i0a from 10⁻¹⁴ to 10⁻¹ A/cm² (Marefatjouikilevaee et al. 2023); R from 0 to 1 Ω cm² (Weiß et al. 2019; Padgett et al. 2025; Fouda-Onana et al. 2016); B_c from 0 to 1 V (Almodfer et al. 2022). The model is written at 80 °C, the temperature of the tests that give the ageing constants. The profile gives E0 = 2 841 kWh, 52.93 kg of hydrogen and SEC0 = 53.68 kWh/kg.

**Ageing, mechanistic model** (pessimistic case, Padgett et al. 2025 and Chandesris et al. 2015):
- anode activity f_A(t) = f_min + (1 − f_min) exp(−t/τ), giving a voltage rise b/ln(10) · ln(1/f_A);
- resistance R(t) = R0 + (HFR drift + catalyst-layer drift)/j_test · t;
- Faraday efficiency from the membrane thinning: e/e0 = 1 − 0.5 t / t50.

**Ageing, linear model**: constant drift μ per cell (2.3 µV/h DOE 2026 target, 4.8 µV/h DOE 2022 status).

The energy over the profile is updated to first order: E(t) = E0 + ΔV_uniform · W0 + ΔR · W_j, with W0 = Σ E_step / V0 and W_j = Σ E_step · j / V0. SEC(t) = E(t) / H2(t).

**End of life**: +10 % voltage at the mean current density of the profile (Brent's method, 0 to 400 000 h).

## 4. Tank (`src/h2ageing/tank.py`)

Permeation (mL/h/L at 55 °C, full tank) grows linearly from P0 to P15 over the 15-year certification: 6 → 6, 6 → 14 and 6 → 46 (UN R134 limit) in the three cases. Hydrogen lost per km = P · V · ρ · 8 760 / (km per year).

Tank alone, per km (`tank.csv`): fabrication of one tank / 200 000 km, plus the mean hydrogen lost, valued as delivered hydrogen at the reference state (electrolysis and compression).

## 5. LCA (`src/h2ageing/chain.py`, `impacts.py`)

Each stack restarts from new when it is replaced. Number of stacks: n = ⌈L / t_EoL⌉ (integer, default) or max(1, L / t_EoL) (prorata: the share of stack life used, at least the first stack).

- Fuel cell alone, per km: m0 · h̄ · I_H2,ref + n · F_stack / L_km, where h̄ is the mean hydrogen consumption over the horizon relative to new (trapezoidal rule on the ages), and I_H2,ref the impact of 1 kg of hydrogen from a new electrolyser, compressed.
- Electrolyser alone, per kg: SEC̄ · I_kWh + I_water + n · F_stack / H2_produced, with energy and hydrogen integrated over the horizon (20 001 points).
- Whole chain, per km: the hydrogen consumed (fuel cell at its age) plus the hydrogen lost (tank at its age) is produced by the electrolyser at its age, then compressed; integrated over 15 years (80 points per year). Electrolyser stacks are shared with the rest of the production: the vehicle carries the fraction of hydrogen it uses.

Impacts: EF 3.1, 16 categories. Single score: Σ (impact / normalisation factor × weighting factor).

## 6. Sensitivity analyses

| Test | Question | Script |
|---|---|---|
| Electricity source | does the conclusion hold with a cleaner electricity? | `run.py --set usage.electricity_electrolyser=...` |
| Electrolyser hours per year | does the chosen 6 000 h/yr matter? Published full-load hours are converted to hours at the measured profile by dividing by its mean load (710/1 250 = 0.568) | `run.py --set usage.electrolyser_hours_per_year=...` |
| Stack counting | what if the last stack has a second life? | `run.py --set usage.stack_counting=prorata` |
| Lifetime threshold | from which lifetime is one stack enough? | `threshold.py` |
| Crossover law | does the unknown shape of the crossover growth change the result? | `fuel_cell_tests.py` |
| Mechanistic constants | which laboratory constant changes the result most? | `mechanistic_constants.py` |
| Global (Sobol) | which of eight inputs, varying together, explains the result? | `sobol.py` |

## 7. Main limits

The complete list, with the effect of each limit and how it is tested, is in [LIMITS.md](LIMITS.md).

- No degradation rate has been measured on the stacks studied.
- Laboratory constants (pessimistic case) are measured on more stressed cells than commercial stacks; the mechanistic laws are extrapolated beyond the duration of the tests.
- The linear model sees neither the rise of the fuel cell crossover nor the fast loss of anode activity.
- The fuel cell result changes by steps with the number of stacks: any end of life between half the horizon and the horizon gives two stacks.
- Inventories are taken from the literature and scaled (Mori et al. 2023, Lundberg 2019, Benitez et al. 2021); auxiliaries are excluded.

## References for the model structure and the fit bounds

- Almodfer R. et al. (2022). Improving parameter estimation of fuel cell using honey badger optimization algorithm. Frontiers in Energy Research 10, 875332 (Table 2 corrected in 13, 1588458, 2025).
- Bielefeld N.M. et al. (2024). A one-dimensional computational model to identify operating conditions and cathode flow channel dimensions for a PEM fuel cell. Hydrogen 5, 624–643. doi:10.3390/hydrogen5030033
- Colombo E. et al. (2023). PEMFC performance decay during real-world automotive operation. Journal of Power Sources 553, 232246.
- Durst J. et al. (2014). New insights into the electrochemical hydrogen oxidation and evolution reaction mechanism. Energy & Environmental Science 7, 2255–2260.
- Fouda-Onana F. et al. (2016). Investigation on the degradation of MEAs for PEM water electrolysers part I. International Journal of Hydrogen Energy 41, 16627–16636.
- Marefatjouikilevaee H., Auger F., Olivier J.-C. (2023). Static and dynamic electrical models of PEM electrolysers: a comprehensive review. Energies 16, 6503. doi:10.3390/en16186503
- Padgett E. et al. (2025). Quantifying sources of voltage decay in long-term durability testing for PEM water electrolysis. Journal of The Electrochemical Society 172, 054508.
- Vetter R., Schumacher J.O. (2019). Experimental parameter uncertainty in PEM fuel cell modeling. Part I. Journal of Power Sources 438, 227018.
- Weiß A. et al. (2019). Impact of intermittent operation on lifetime and performance of a PEM water electrolyzer. Journal of The Electrochemical Society 166, F487–F497.
