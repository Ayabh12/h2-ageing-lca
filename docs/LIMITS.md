# Limits and validity domain

**English** | [Français](LIMITS.fr.md)

What the model does not know, the effect on the results, and what is done.

**What the results are:** the rise of the impact due to ageing, with and without ageing, for each component and for the chain. Three cases **bracket** ageing; they **do not predict** the exact lifetime of these stacks.

## 1. Data

| Limit | Effect | What is done | Where |
|---|---|---|---|
| No degradation rate published for the Nel MC250 and Mirai II stacks | lifetime unknown | three cases bracket it; your value is entered in one line | [METHOD](METHOD.md#the-three-ageing-cases); [GUIDE](GUIDE.md), example 2 |
| Pessimistic constants from laboratory cells, more stressed (3 A/cm² for the electrolyser) | pessimistic case probably too severe | used as an upper bracket; each constant tested against another published value | `semi_empirical_constants.py`; [GUIDE](GUIDE.md), example 5 |
| Semi-empirical laws extrapolated beyond the tests (×2.9 fuel cell, ×8.5 electrolyser) | shape of the curve not measured at old age | three crossover laws compared: same number of stacks | `fuel_cell_tests.py` |
| Fuel cell crossover measured over 1 000 h only | hydrogen consumption at old age uncertain | linear, exponential and constant laws compared | `fuel_cell_tests.py`; [GUIDE](GUIDE.md), section 3.2 |
| No published law for the tank permeation | effect bracketed, not modelled | from 6 to 46 mL/h/L (UN R134 limit): less than 1 g CO2-eq/km | [METHOD](METHOD.md), sections 4 and 7 |
| Fuel cell area (297 cm²) estimated; electrolyser cells (200) and area (1 500 cm²) chosen | they fix the current density | justified; can be changed | [METHOD](METHOD.md), sections 2.5 and 3.1 |
| 3.64 g of hydrogen not explained on the trip (gap between the hydrogen measured at the tank, 0.196 kg, and that computed from the current, 0.192 kg) | origin unknown | kept constant, as a loss current | [METHOD](METHOD.md), section 2.2; `src/h2ageing/pemfc.py` |

## 2. Operating conditions

| Limit | Effect | What is done | Where |
|---|---|---|---|
| One trip (2 033 s, 20.32 km) replayed over the whole life; one 4-hour wind profile repeated | another use would change the consumption | files can be replaced; mean speed tested (48 instead of 36 km/h) | [GUIDE](GUIDE.md), section 3.5; `fuel_cell_tests.py` |
| Constant temperatures (80 °C electrolyser, 70 °C fuel cell) | changes not modelled | tested on the electrolyser with published 60 °C ratios: chain rise +34.5 and +34.9 % instead of +35.0 % | `semi_empirical_constants.py`; [GUIDE](GUIDE.md), example 5 |
| Start-ups, shutdowns and idle periods not modelled | degradation from shutdowns not counted | not tested; a faster linear rate can represent it | [GUIDE](GUIDE.md), section 3.2 |

## 3. Scope and method

| Limit | What it means | Where |
|---|---|---|
| Stacks and tank only | auxiliaries, station except compression, rest of the vehicle, transport and end of life outside the system | [METHOD](METHOD.md), section 1 |
| Inventories from the literature, scaled (Mori 2023, Lundberg 2019, Benitez 2021) | with the original values, central rise from +22.9 to +28.2 % instead of +31.1 %, same number of stacks | [inventories](../data/inventories/README.md); redo it with your own fabrication file ([GUIDE](GUIDE.md), section 3.4) |
| ecoinvent not distributed | results run without a licence; recomputing a fabrication needs one | [GUIDE](GUIDE.md), section 3.4 |
| Linear model (optimistic, central) | sees neither the crossover rise nor the fast early loss of the anode | [METHOD](METHOD.md), sections 2.4 and 3.3 |
| Sensitivity, not uncertainty | inputs are bracketed and ranked, without probability: too few published data | [METHOD](METHOD.md), section 6 |

## 4. Validity domain

| | Examples |
|---|---|
| **Usable directly** (change a value, [GUIDE](GUIDE.md) section 3) | electricity, lifetimes and ageing constants, mileage, electrolyser hours, compression, fabrication impact, stack counting |
| **Usable after adapting the data** (code unchanged) | another PEM stack (refit the curves, `fit_pemfc.py`, `fit_pemwe.py`); another trip or profile; another PEM vehicle (bus, truck: replace the DOE lifetimes); another tank; another inventory (ecoinvent licence) |
| **Outside the domain** (new equations needed) | another technology (alkaline, SOEC, AEM, SOFC); another storage (liquid, hydrides); auxiliaries; transport, distribution, recycling; other ageing (membrane rupture, cold starts, varying temperatures); electricity changing over 15 years; total vehicle footprint |
