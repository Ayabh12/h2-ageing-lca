# Method

**English** | [Français](METHOD.fr.md)

This page summarises what the code computes and why. Each value of `config/default.yaml` gives its source.

**Contents:** [1. Functional units and system](#1-functional-units-and-system) · [2. Fuel cell](#2-fuel-cell) · [3. Electrolyser](#3-electrolyser) · [4. Tank](#4-tank) · [5. LCA](#5-lca) · [6. Sensitivity analyses](#6-sensitivity-analyses) · [7. Main limits](#7-main-limits) · [References](#references-for-the-model-structure-and-the-fit-bounds)

---

## 1. Functional units and system

| Assessment | Functional unit | What ages |
|---|---|---|
| Fuel cell alone | 1 km driven | fuel cell stack only; it receives hydrogen from the studied electrolyser at its reference state (no ageing, stack fabrication excluded), compressed: 4.503 kg CO2-eq/kg |
| Electrolyser alone | 1 kg of hydrogen produced | electrolyser stack |
| Whole chain | 1 km driven | electrolyser, tank (permeation) and fuel cell together |

- **Horizon:** 15 years, 200 000 km (`horizon`).
- **Electricity:** French residual mix by default (79.6 g CO2-eq/kWh), the mix of a grid-connected electrolyser that buys no guarantees of origin. The measured wind profile only gives the electricity used per kg of hydrogen and its change with age, not the origin of the electricity.
- **Comparison:** each assessment compares the chain with ageing to the same chain without ageing (same profile, electricity, horizon, boundaries and inventories, one stack of each converter).
- **Inside the system:** electricity and water of the electrolyser, compression electricity, manufacture of the stacks and of the tank, hydrogen lost by permeation.
- **Outside the system:** auxiliaries, station apart from compression, rest of the vehicle, transport, end of life.

### What each impact includes

The LCA counts two kinds of flows: the **manufacture** of the components that age, and their **use**. Both are counted "cradle to gate": from the extraction of resources to the moment the component leaves the factory, or the kilowatt-hour reaches the electrolyser.

**Manufacture of a stack or of the tank.** The inventory of each component (`data/inventories/`) lists its materials and the electricity used by the factory. Each material is linked to an ecoinvent 3.11 dataset (cut-off model) that carries its whole upstream chain. The impact of one component therefore includes:

| Life-cycle stage | Included | Where it comes from |
|---|---|---|
| Extraction of resources (ores, oil, gas) | yes | ecoinvent datasets of each material |
| Processing of materials (refining, smelting, rolling, chemical synthesis, carbon fibre production) | yes | ecoinvent datasets of each material |
| Energy and transport of these upstream steps, up to the market | yes | ecoinvent datasets of each material |
| Electricity used to manufacture and assemble the component | yes | inventory of the component |
| Transport of the finished component to the vehicle or to the site | no | not described in the source inventories |
| Factory buildings and machines of the component maker | no | not described in the source inventories |
| End of life, recycling, credits for recovered metals | no | cut-off model: no burden and no credit at end of life |

Iridium (electrolyser anode) has no ecoinvent dataset: it is counted as a resource taken from the ground only. Its extraction weighs on resource depletion, but no impact of its processing is counted, in particular on climate change.

**Use.** The impact of 1 kWh of electricity is the ecoinvent dataset of the chosen source: it includes the fuels and their extraction, the power plants and their construction, and the grid with its losses. The impact of 1 kg of deionised water includes its production. Hydrogen lost by permeation is valued as hydrogen that has to be produced and compressed.

**Outside the system.** Auxiliaries (balance of plant), the refuelling station apart from compression, the rest of the vehicle and transport between the links of the chain. They do not change with the age of the stacks.

---

## 2. Fuel cell

Code: `src/h2ageing/pemfc.py`

### 2.1 Polarisation at the reference state

The full cell voltage contains the activation and transport losses of both electrodes and the ohmic loss. Only the losses of the oxygen electrode are kept (the cathode for the fuel cell, the anode for the electrolyser), for two reasons:

1. the hydrogen reaction has an exchange current several orders of magnitude higher on platinum in acid medium (Durst et al. 2014), so its loss is small and nearly proportional to the current, hence included in $`R`$;
2. the activation losses of the two electrodes both vary as $`\ln j`$, so a single voltage–current curve cannot separate them.

The cell voltage of the fuel cell is:

```math
V(j,t) \;=\; E_{\mathrm{rev}}(T) \;-\; \frac{RT}{\alpha_c F}\,\ln\!\left(\frac{j}{i_{0c}\,S(t)}\right) \;-\; R(t)\,j \;+\; B_c\,\ln\!\left(1-\frac{j}{i_{\mathrm{lim}}}\right)
```

```math
E_{\mathrm{rev}}(T) \;=\; 1.229 \;-\; 0.85\times10^{-3}\,(T-298.15)
```

| Symbol | Meaning | Unit |
|---|---|---|
| $`j`$ | current density | A/cm² |
| $`t`$ | age of the stack | h |
| $`T`$ | temperature (70 °C) | K |
| $`\alpha_c`$ | cathode transfer coefficient | – |
| $`i_{0c}`$ | exchange current density of the cathode | A/cm² |
| $`S(t)`$ | relative platinum surface (1 when new) | – |
| $`R(t)`$ | resistance of one cell ($`R_0`$ when new) | Ω·cm² |
| $`B_c`$ | transport loss coefficient | V |
| $`i_{\mathrm{lim}}`$ | limiting current density | A/cm² |

The four parameters $`i_{0c}`$, $`R_0`$, $`B_c`$ and $`i_{\mathrm{lim}}`$ are fitted on quasi-steady points of the road measurements (`scripts/fit_pemfc.py`), by bounded least squares. Bounds, and the published values they enclose:

| Parameter | Bounds | Published values |
|---|---|---|
| $`\log_{10} i_{0c}`$ | −12 to −1 | Vetter & Schumacher 2019; Colombo et al. 2023 |
| $`R_0`$ | 0 to 0.3 Ω·cm² | Colombo et al. 2023 |
| $`B_c`$ | 0 to 0.3 V | Almodfer et al. 2022 |
| $`i_{\mathrm{lim}}`$ | 2.03 to 6 A/cm² (lower bound just above the highest measured current density) | Bielefeld et al. 2024 |

### 2.2 Hydrogen consumed at a given age

The measured trip (time, current, voltage; 2 033 s, 20.32 km) is replayed at each age **at constant power**:

- **Current at each second.** The current that delivers the measured power is found by bisection (40 iterations).
- **Anchoring factor.** A factor, computed second by second, makes the model give exactly the measured current at age zero; the rise in consumption then comes only from ageing.
- **Hydrogen.** The hydrogen consumed is Faraday's law plus a loss current. The gap between the measured hydrogen (0.196 kg) and Faraday's law is kept constant; the rise of the crossover is added to it.

### 2.3 Ageing, semi-empirical model (pessimistic case)

Its structure is physical, each degradation mechanism acting on one term of the polarisation equation; its laws of change with time are fitted on laboratory measurements, hence "semi-empirical".

**Platinum surface** (Verducci et al.):

```math
\frac{dS}{dt} \;=\; -\,k\,S^2\,e^{\omega S}
```

$`k`$ is chosen so that $`S(1000\ \mathrm{h})`$ equals the value measured by Colombo et al. (2023). It is found by inverting the tabulated integral (trapezoidal rule, 6 000 points):

```math
g(S) \;=\; \int_S^1 \frac{e^{-\omega s}}{s^2}\,ds
```

**Transport resistance:**

```math
R(t) \;=\; R_0 + r\,t, \qquad r \;=\; \frac{\Delta V_{1.8,\,1000} \;-\; \dfrac{RT}{\alpha_c F}\,\ln\dfrac{1}{S_{1000}}}{1.8 \times 1000}
```

$`\Delta V_{1.8,\,1000}`$ is the voltage loss measured at 1.8 A/cm² after 1 000 h; the part already due to the platinum loss is subtracted. In the code, $`R(t)`$ is written $`R_0\,(1 + k_R\,t)`$ with $`k_R = r/R_0`$.

**Crossover:** 2 mA/cm² at age zero, multiplied by the factor measured in 1 000 h (linear law by default; exponential and constant laws available).

### 2.4 Ageing, linear model (optimistic and central cases)

```math
V(t) \;=\; V(0) \;-\; \mu\,t, \qquad \mu \;=\; \frac{0.10 \times V_{300\,\mathrm{A}}(0)}{t_{\mathrm{EoL}}}
```

$`t_{\mathrm{EoL}}`$ is the published time to end of life: 8 000 h (DOE target, optimistic) or 4 100 h (DOE best fleet, central). The crossover stays constant.

### 2.5 End of life

Age at which the stack voltage at 300 A has lost 10 % (DOE criterion), found with Brent's method between 0 and 60 000 h.

---

## 3. Electrolyser

Code: `src/h2ageing/pemwe.py`

### 3.1 Polarisation at the reference state

Fitted by `scripts/fit_pemwe.py` on the 4-hour wind profile (1 s steps):

```math
V(j) \;=\; E_{\mathrm{rev}}(T) \;+\; \frac{RT}{2\,\alpha_a F}\,\ln\!\left(\frac{j}{i_{0a}}\right) \;+\; R\,j \;-\; B_c\,\ln\!\left(1-\frac{j}{i_{\mathrm{lim}}}\right)
```

- $`\alpha_a`$ is fixed by the Tafel slope of Padgett et al. (46 mV/decade at 80 °C).
- $`i_{0a}`$, $`R`$ and $`B_c`$ are fitted (bounded least squares, trust region reflective, 50 starts, seed 180).
- The model is written at 80 °C, the temperature of the tests that give the ageing constants.

| Parameter | Bounds | Published values |
|---|---|---|
| $`i_{0a}`$ | $`10^{-14}`$ to $`10^{-1}`$ A/cm² | Marefatjouikilevaee et al. 2023 |
| $`R`$ | 0 to 1 Ω·cm² | Weiß et al. 2019; Padgett et al. 2025; Fouda-Onana et al. 2016 |
| $`B_c`$ | 0 to 1 V | Almodfer et al. 2022 |

On the measured profile, the new stack uses $`E_0`$ = 2 841 kWh and produces 52.93 kg of hydrogen, that is $`\mathrm{SEC}_0`$ = 53.68 kWh/kg.

### 3.2 Ageing, semi-empirical model (pessimistic case)

Constants from Padgett et al. (2025) and Chandesris et al. (2015).

**Anode activity**, and the voltage rise it causes:

```math
f_A(t) \;=\; f_{\min} + (1-f_{\min})\,e^{-t/\tau}, \qquad \Delta V_{\mathrm{act}}(t) \;=\; \frac{b}{\ln 10}\,\ln\frac{1}{f_A(t)}
```

**Resistance:**

```math
R(t) \;=\; R_0 \;+\; \frac{\text{HFR drift} + \text{catalyst-layer drift}}{j_{\mathrm{test}}}\;t
```

**Faraday efficiency**, from the membrane thinning:

```math
\frac{\eta_F(t)}{\eta_{F,0}} \;=\; 1 - 0.5\,\frac{t}{t_{50}}
```

### 3.3 Ageing, linear model (optimistic and central cases)

Constant voltage drift $`\mu`$ per cell: 2.3 µV/h (DOE 2026 target, optimistic) or 4.8 µV/h (DOE 2022 status, central).

### 3.4 Electricity per kg at a given age

The energy over the profile is updated to first order:

```math
E(t) \;=\; E_0 \;+\; \Delta V_{\mathrm{uniform}}\,W_0 \;+\; \Delta R\,W_j, \qquad \mathrm{SEC}(t) \;=\; \frac{E(t)}{H_2(t)}
```

```math
W_0 \;=\; \sum \frac{E_{\mathrm{step}}}{V_0}, \qquad W_j \;=\; \sum \frac{E_{\mathrm{step}}\; j}{V_0}
```

### 3.5 End of life

Voltage rise of 10 % at the mean current density of the profile (Brent's method, 0 to 400 000 h).

---

## 4. Tank

Code: `src/h2ageing/tank.py`

The permeation $`P`$ (mL/h/L at 55 °C, full tank) grows linearly from $`P_0`$ to $`P_{15}`$ over the 15-year certification: 6 → 6, 6 → 14 and 6 → 46 (UN R134 limit) in the three cases.

```math
m_{\mathrm{perm}} \;=\; \frac{P \cdot V \cdot \rho \cdot 8\,760}{\text{km per year}}
```

with $`V`$ the tank volume and $`\rho`$ the hydrogen density.

**Tank alone, per km** (`tank.csv`): fabrication of one tank divided by 200 000 km, plus the mean hydrogen lost, valued as delivered hydrogen at the reference state (electrolysis and compression).

---

## 5. LCA

Code: `src/h2ageing/chain.py`, `impacts.py`

**Number of stacks.** Each stack restarts from new when it is replaced:

```math
n \;=\; \left\lceil \frac{L}{t_{\mathrm{EoL}}} \right\rceil \ \ \text{(integer, default)} \qquad \text{or} \qquad n \;=\; \max\!\left(1,\ \frac{L}{t_{\mathrm{EoL}}}\right) \ \ \text{(prorata)}
```

$`L`$ is the operating time over the horizon; prorata counts the share of stack life used, with at least the first stack.

**Fuel cell alone, per km:**

```math
I_{\mathrm{FC}} \;=\; m_0\,\bar h\,I_{\mathrm{H_2,ref}} \;+\; \frac{n\,F_{\mathrm{stack}}}{L_{\mathrm{km}}}
```

- $`m_0`$: hydrogen per km when new;
- $`\bar h`$: mean hydrogen consumption over the horizon, relative to new (trapezoidal rule on the ages);
- $`I_{\mathrm{H_2,ref}}`$: impact of 1 kg of hydrogen from a new electrolyser, compressed;
- $`F_{\mathrm{stack}}`$: impact of manufacturing one stack; $`L_{\mathrm{km}}`$ = 200 000 km.

**Electrolyser alone, per kg:**

```math
I_{\mathrm{WE}} \;=\; \overline{\mathrm{SEC}}\;I_{\mathrm{kWh}} \;+\; I_{\mathrm{water}} \;+\; \frac{n\,F_{\mathrm{stack}}}{H_{2,\mathrm{produced}}}
```

Energy and hydrogen are integrated over the horizon (20 001 points).

**Whole chain, per km.** The hydrogen consumed (fuel cell at its age) plus the hydrogen lost (tank at its age) is produced by the electrolyser at its age, then compressed; everything is integrated over 15 years (80 points per year). Electrolyser stacks are shared with the rest of the production: the vehicle carries the fraction of hydrogen it uses.

**Impacts:** EF 3.1, 16 categories. Single score:

```math
\text{single score} \;=\; \sum_{\text{categories}} \frac{\text{impact}}{\text{normalisation factor}} \times \text{weighting factor}
```

---

## 6. Sensitivity analyses

**What a Sobol analysis is.** It varies all the inputs together, many times (10 240 runs), and measures which share of the variation of the result each input explains. Its total index goes from 0 (the input does not matter) to 1 (the input explains all the variation, alone or together with the others).

| Test | Question | Script |
|---|---|---|
| Electricity source | does the conclusion hold with a cleaner electricity? | `run.py --set usage.electricity_electrolyser=...` |
| Electrolyser hours per year | does the chosen 6 000 h/yr matter? Published full-load hours are converted to hours at the measured profile by dividing by its mean load (710/1 250 = 0.568) | `run.py --set usage.electrolyser_hours_per_year=...` |
| Stack counting | what if the last stack has a second life? | `run.py --set usage.stack_counting=prorata` |
| Lifetime threshold | from which lifetime is one stack enough? | `threshold.py` |
| Crossover law | does the unknown shape of the crossover growth change the result? | `fuel_cell_tests.py` |
| Semi-empirical constants | which laboratory constant changes the result most? | `semi_empirical_constants.py` |
| Global (Sobol) | which of eight inputs, varying together, explains the result? | `sobol.py` |

---

## 7. Main limits

The complete list, with the effect of each limit and how it is tested, is in [LIMITS.md](LIMITS.md).

- No degradation rate has been measured on the stacks studied.
- Laboratory constants (pessimistic case) are measured on more stressed cells than commercial stacks; the semi-empirical laws are extrapolated beyond the duration of the tests.
- The linear model sees neither the rise of the fuel cell crossover nor the fast loss of anode activity.
- Inventories are taken from the literature and scaled (Mori et al. 2023, Lundberg 2019, Benitez et al. 2021); auxiliaries are excluded.

---

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
