# Limits and validity domain

**English** | [Français](LIMITS.fr.md)

What the model does not know, the effect on the results, and what is done.

**What the results are:** the rise of the impact due to ageing, with and without ageing, for each component and for the chain. Three cases **bracket** ageing; they **do not predict** the exact lifetime of these stacks.

## 1. Data

| Limit | Effect | What is done |
|---|---|---|
| No degradation rate published for the Nel MC250 and Mirai II stacks | lifetime unknown | three cases bracket it; your value is entered in one line ([GUIDE](GUIDE.md), example 2) |
| Pessimistic constants from laboratory cells, more stressed (3 A/cm² for the electrolyser) | pessimistic case probably too severe | used as an upper bracket; each constant tested against another published value (`semi_empirical_constants.py`) |
| Semi-empirical laws extrapolated beyond the tests (×2.9 fuel cell, ×8.5 electrolyser) | shape of the curve not measured at old age | three crossover laws compared: same number of stacks (`fuel_cell_tests.py`) |
| Fuel cell crossover measured over 1 000 h only | hydrogen consumption at old age uncertain | linear, exponential and constant laws compared |
| No published law for the tank permeation | effect bracketed, not modelled | from 6 to 46 mL/h/L (UN R134 limit): less than 1 g CO2-eq/km |
| Fuel cell area (297 cm²) estimated; electrolyser cells (200) and area (1 500 cm²) chosen | they fix the current density | justified in `config/default.yaml`; can be changed |
| 3.64 g of measured hydrogen not explained by the current on the trip | origin unknown | kept constant, as a loss current |

## 2. Operating conditions

| Limit | Effect | What is done |
|---|---|---|
| One trip (2 033 s, 20.32 km) replayed over the whole life; one 4-hour wind profile repeated | another use would change the consumption | files can be replaced ([GUIDE](GUIDE.md), section 3.5); mean speed tested (48 instead of 36 km/h) |
| Constant temperatures (80 °C electrolyser, 70 °C fuel cell) | changes not modelled | published 60 °C ratios can be tested on the electrolyser |
| Start-ups, shutdowns and idle periods not modelled | degradation from shutdowns not counted | a faster linear rate can represent it |

## 3. Scope and method

| Limit | What it means |
|---|---|
| Stacks and tank only | auxiliaries, station except compression, rest of the vehicle, transport and end of life outside the system |
| Compression does not age | 2.8 kWh/kg in all cases |
| Inventories from the literature, scaled (Mori 2023, Lundberg 2019, Benitez 2021) | with the original values, central rise from +22.9 to +28.2 % instead of +31.1 %, same number of stacks |
| ecoinvent not distributed | results run without a licence; recomputing a fabrication needs one |
| Linear model (optimistic, central) | sees neither the crossover rise nor the fast early loss of the anode |
| Sensitivity, not uncertainty | inputs are bracketed and ranked, without probability: too few published data |

## 4. Validity domain

| | Examples |
|---|---|
| **Usable directly** (change a value, [GUIDE](GUIDE.md) section 3) | electricity, lifetimes and ageing constants, mileage, electrolyser hours, compression, fabrication impact, stack counting |
| **Usable after adapting the data** (code unchanged) | another PEM stack (refit the curves, `fit_pemfc.py`, `fit_pemwe.py`); another trip or profile; another PEM vehicle (bus, truck: replace the DOE lifetimes); another tank; another inventory (ecoinvent licence) |
| **Outside the domain** (new equations needed) | another technology (alkaline, SOEC, AEM, SOFC); another storage (liquid, hydrides); auxiliaries; transport, distribution, recycling; other ageing (compression, membrane rupture, cold starts, varying temperatures); electricity changing over 15 years; total vehicle footprint |
