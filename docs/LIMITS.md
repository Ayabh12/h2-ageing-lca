# Limits and validity domain

**English** | [Français](LIMITS.fr.md)

This page lists what the model does not know or does not include, the effect on the results, and how each limit is tested or could be lifted. It is meant to help you judge when the results apply to your own case.

## What the results are, and are not

- They are **the effect of ageing on the LCA of this chain**: the rise of the impact between the same chain with and without ageing, for each component and for the whole chain.
- They **bracket** ageing with three cases built from published values; they are **not a prediction** of the lifetime of these exact stacks.
- They are computed with characterised impacts from ecoinvent 3.11 (cut-off) and EF 3.1. Climate change is the main indicator; the 16 EF 3.1 categories and the single score are also computed.

## Limits of the data

| Limit | Effect on the results | How it is handled |
|---|---|---|
| No degradation rate is published for the Nel MC250 stack nor for the Toyota Mirai II stack | The lifetime of the stacks is not known exactly | Three cases bracket it: DOE target (optimistic), DOE status or fleet value (central), laboratory constants (pessimistic). Your own value can be entered in one line (GUIDE.md, example 2) |
| The pessimistic constants come from laboratory cells, more stressed than commercial stacks (for example 3 A/cm² constant for the electrolyser) | The pessimistic case is likely above the degradation of an industrial stack | It is used as an upper bracket only; each constant is tested against another published value (`scripts/semi_empirical_constants.py`) |
| The semi-empirical laws are extrapolated beyond the duration of the tests (2.9 times for the fuel cell, 8.5 times for the electrolyser) | The shape of the curve after the tests is not measured | Three crossover laws are compared (`scripts/fuel_cell_tests.py`); the number of stacks does not change |
| The fuel cell crossover is measured over 1 000 h only; published tests show a sudden rise after 500–800 h that no continuous law predicts | The hydrogen consumption at old age is uncertain | Linear, exponential and constant laws are compared |
| No ageing law is published for the tank permeation | The tank effect is bracketed, not modelled from a law | From no rise up to the regulatory limit (46 mL/h/L): less than 1 g CO2-eq/km in all cases |
| The fuel cell active area (297 cm²) is estimated in the literature; the electrolyser cell number (200) and area (1 500 cm²) are not published and are chosen | They fix the current density used by the ageing laws | Each choice is justified in `config/default.yaml` and `data/parameters/`; they can be changed and the models refitted |
| The hydrogen measured on the fuel cell trip exceeds by 3.64 g the hydrogen explained by the current | Its origin is unknown | It is kept constant over time, as a loss current |

## Limits of the operating conditions

| Limit | Effect | How to lift it |
|---|---|---|
| Fuel cell: the polarisation curve is fitted on all 12 road recordings, but the use phase replays one measured trip (WLTP-type, 2 033 s, 20.32 km) at every age, as if the whole vehicle life followed this trip. Electrolyser: one 4-hour wind profile, repeated | Another driving or wind pattern would give another consumption and possibly another ageing speed | Replace the trip or profile file (GUIDE.md, section 3.5); the mean speed of the trip is tested (48 instead of 36 km/h: `scripts/fuel_cell_tests.py`) |
| Constant temperatures (80 °C electrolyser, 70 °C fuel cell), those of the tests that give the ageing constants | Temperature changes are not modelled | Published 60 °C ratios can be applied to the electrolyser constants (`scripts/semi_empirical_constants.py`) |
| The ageing follows the operating hours; start-ups, shutdowns and idle periods are not modelled separately | Shutdowns at open-circuit potential, known to worsen electrolyser degradation, are not included | Use a faster rate in the linear model to represent them |

## Limits of the scope

- **Stacks and tank only.** Auxiliaries (balance of plant), the refuelling station apart from compression, the rest of the vehicle, transport, end of life and recycling are outside the system: they are not affected by the ageing mechanisms studied.
- **Compression does not age:** 2.8 kWh per kg in all cases.
- **Inventories from the literature, scaled:** fuel cell stack from Mori et al. (2023, 48 kW scaled to 128 kW), electrolyser stack from Lundberg (2019, per MW), tank from Benitez et al. (2021). With the values published by these sources instead of ours, the central chain rise goes from +31.1 % to between +22.9 % and +28.2 %, with the same number of stacks.
- **ecoinvent is not distributed.** All results run from the characterised impacts shipped in `data/impacts`; rebuilding the fabrication impacts after changing an inventory needs your own ecoinvent licence.

## Limits of the method

- **The linear model** (optimistic and central cases) sees neither the rise of the fuel cell crossover nor the fast early loss of the electrolyser anode activity; the semi-empirical model does.
- **The sensitivity analyses are not an uncertainty analysis.** They bracket and rank the inputs; they do not give a probability for the result, because the published ageing data are too few to build probability distributions without inventing them.

## Validity domain

The model answers one precise question: **how much stack ageing changes the LCA of a PEM hydrogen chain**. Depending on what you change, it applies directly, after adapting the data, or not at all.

**1. Usable directly, by changing a value** (section 3 of the [guide](GUIDE.md)):

- another electricity source (one of the five shipped, or a new one if you have its impact per kWh);
- another lifetime or degradation rate of the stacks, other ageing constants;
- another mileage, another horizon, other operating hours of the electrolyser;
- another compression energy, another fabrication impact, another stack counting rule.

**2. Usable after adapting the data, without changing the code:**

- **another PEM stack** (electrolyser or fuel cell): refit the polarisation curves on its own measurements (`scripts/fit_pemfc.py`, `scripts/fit_pemwe.py`), give its number of cells, its active area and its own ageing data;
- **another trip or another operating profile**: replace the measurement files;
- **another PEM fuel cell vehicle** (bus, truck): give its measured trip, its stack and its mileage; the DOE lifetimes, set for cars, then no longer apply and must be replaced;
- **another tank** (another type or volume): give its inventory and its permeation;
- **another fabrication inventory**: with an ecoinvent licence.

**3. Outside the domain: the model gives no valid result**, and new equations would be needed:

- **another technology**: alkaline, solid oxide (SOEC) or anion exchange membrane (AEM) electrolysis, solid oxide fuel cell (SOFC). The polarisation curves and ageing laws are specific to PEM (platinum, membrane, iridium);
- **another storage mode**: liquid hydrogen, hydrides, pipeline transport;
- **auxiliaries**: air compressor, humidifier, cooling, power electronics, electrolyser equipment outside the stack. Neither their consumption, nor their fabrication, nor their ageing is modelled; adding one needs new equations, not only data;
- **steps outside the boundary**: hydrogen transport and distribution, station except compression, end of life and recycling of the stacks (platinum, iridium);
- **other forms of ageing**: ageing of the compression, sudden failures (membrane rupture), the specific effect of starts and stops, varying temperatures, cold starts;
- **electricity that changes over the 15 years**: the model uses one source over the whole horizon;
- **the total footprint of a vehicle**: only the stacks, the tank and hydrogen production are counted. The result measures the effect of ageing, not the full impact of the vehicle.
