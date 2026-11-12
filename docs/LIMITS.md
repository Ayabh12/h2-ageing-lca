# Limits and validity domain

This page lists what the model does not know or does not include, the effect on the results, and how each limit is tested or could be lifted. It is meant to help you judge when the results apply to your own case.

## What the results are, and are not

- They are **the effect of ageing on the LCA of this chain**: the rise of the impact between the same chain with and without ageing, for each component and for the whole chain.
- They **bracket** ageing with three cases built from published values; they are **not a prediction** of the lifetime of these exact stacks.
- They are computed with characterised impacts from ecoinvent 3.11 (cut-off) and EF 3.1. Climate change is the main indicator; the 16 EF 3.1 categories and the single score are also computed.

## Limits of the data

| Limit | Effect on the results | How it is handled |
|---|---|---|
| No degradation rate is published for the Nel MC250 stack nor for the Toyota Mirai II stack | The lifetime of the stacks is not known exactly | Three cases bracket it: DOE target (optimistic), DOE status or fleet value (central), laboratory constants (pessimistic). Your own value can be entered in one line (USE_CASES.md, example 2) |
| The pessimistic constants come from laboratory cells, more stressed than commercial stacks (for example 3 A/cm² constant for the electrolyser) | The pessimistic case is likely above the degradation of an industrial stack | It is used as an upper bracket only; each constant is tested against another published value (`scripts/mechanistic_constants.py`) |
| The mechanistic laws are extrapolated beyond the duration of the tests (2.9 times for the fuel cell, 8.5 times for the electrolyser) | The shape of the curve after the tests is not measured | Three crossover laws are compared (`scripts/fuel_cell_tests.py`); the number of stacks does not change |
| The fuel cell crossover is measured over 1 000 h only; published tests show a sudden rise after 500–800 h that no continuous law predicts | The hydrogen consumption at old age is uncertain | Linear, exponential and constant laws are compared |
| No ageing law is published for the tank permeation | The tank effect is bracketed, not modelled from a law | From no rise up to the regulatory limit (46 mL/h/L): less than 1 g CO2-eq/km in all cases |
| The fuel cell active area (297 cm²) is estimated in the literature; the electrolyser cell number (200) and area (1 500 cm²) are not published and are chosen | They fix the current density used by the ageing laws | Each choice is justified in `config/default.yaml` and `data/parameters/`; they can be changed and the models refitted |
| The hydrogen measured on the fuel cell trip exceeds by 3.64 g the hydrogen explained by the current | Its origin is unknown | It is kept constant over time, as a loss current |

## Limits of the operating conditions

| Limit | Effect | How to lift it |
|---|---|---|
| One measured road trip (2 033 s, 20.32 km) and one 4-hour wind profile, repeated at every age | Other driving or wind patterns age the stacks differently | Replace the measurement files and refit (CUSTOMISE.md, section 4) |
| Constant temperatures (80 °C electrolyser, 70 °C fuel cell), those of the tests that give the ageing constants | Temperature changes are not modelled | Published 60 °C ratios can be applied to the electrolyser constants (`scripts/mechanistic_constants.py`) |
| The ageing follows the operating hours; start-ups, shutdowns and idle periods are not modelled separately | Shutdowns at open-circuit potential, known to worsen electrolyser degradation, are not included | Use a faster rate in the linear model to represent them |

## Limits of the scope

- **Stacks and tank only.** Auxiliaries (balance of plant), the refuelling station apart from compression, the rest of the vehicle, transport, end of life and recycling are outside the system: they are not affected by the ageing mechanisms studied.
- **Compression does not age:** 2.8 kWh per kg in all cases.
- **Inventories from the literature, scaled:** fuel cell stack from Mori et al. (2023, 48 kW scaled to 128 kW), electrolyser stack from Lundberg (2019, per MW), tank from Benitez et al. (2021). With the values published by these sources instead of ours, the central chain rise goes from +31.1 % to between +22.9 % and +28.2 %, with the same number of stacks.
- **ecoinvent is not distributed.** All results run from the characterised impacts shipped in `data/impacts`; rebuilding the fabrication impacts after changing an inventory needs your own ecoinvent licence.

## Limits of the method

- **Steps.** The number of stacks is an integer, so the fuel cell result moves by steps: any end of life between half the horizon and the horizon gives two stacks. Near a threshold, a small change of lifetime changes the result a lot (USE_CASES.md, example 5).
- **Stack counting.** By default, every started stack is counted as a whole stack. Counting the share of life used (prorata) is a lower bound that assumes a second life; it mostly changes the central case (+14.7 % instead of +31.1 %).
- **The linear model** (optimistic and central cases) sees neither the rise of the fuel cell crossover nor the fast early loss of the electrolyser anode activity; the mechanistic model does.
- **The sensitivity analyses are not an uncertainty analysis.** They bracket and rank the inputs; they do not give a probability for the result, because the published ageing data are too few to build probability distributions without inventing them.

## Validity domain

The results apply directly to a chain close to the one studied: grid-connected PEM electrolysis at MW scale, 700 bar compression, type IV tank, PEM fuel cell in a passenger car, over 15 years. For another equipment, the structure of the model still applies, but the polarisation models should be refitted on its own measurements and its own ageing data should be entered.
