# Worked examples

Each example asks a question, gives the command that answers it, and shows the result obtained with the shipped data (climate change, whole chain, g CO2-eq/km). All commands run in a few seconds, without ecoinvent. Change the values to answer your own question.

The reference results, for comparison:

| | No ageing | Optimistic | Central | Pessimistic |
|---|---|---|---|---|
| Whole chain (g CO2-eq/km) | 74.12 | 77.84 (+5.0 %) | 97.15 (+31.1 %) | 100.06 (+35.0 %) |

---

## 1. What if the electrolyser runs on wind electricity?

**Why ask:** the reference uses the French residual mix, the most carbon-intensive source tested. A project with a wind power purchase agreement would use another source.

```bash
python scripts/run.py --set usage.electricity_electrolyser=wind_FR
```

| | No ageing | Optimistic | Central | Pessimistic |
|---|---|---|---|---|
| Whole chain (g CO2-eq/km) | 41.22 | 42.32 (+2.7 %) | 61.27 (+48.6 %) | 61.97 (+50.3 %) |

**What it shows:** the chain emits much less, but the relative effect of ageing is larger. The replacement stacks add the same impact whatever the electricity, and they weigh more when the rest is cleaner. Available sources: `residual_mix_FR`, `average_mix_FR`, `nuclear_FR`, `wind_FR`, `photovoltaic`; add your own as a column of `data/impacts/electricity_per_kWh.csv`.

## 2. What if my fuel cell stack lasts longer?

**Why ask:** the central case uses 4 100 h to end of life (best DOE fleet, 2006–2016). A newer stack may last longer.

```bash
python scripts/run.py --set cases.central.fuel_cell.hours_to_end_of_life=6000
```

| | Central (reference, 4 100 h) | Central with 6 000 h |
|---|---|---|
| Fuel cell stacks | 2 | 1 |
| Whole chain (g CO2-eq/km) | 97.15 (+31.1 %) | 78.88 (+6.4 %) |

**What it shows:** above the horizon of 5 554 operating hours, a single stack is enough, and the rise falls from +31 % to +6 %. Example 5 gives the exact thresholds.

## 3. What if the last stack gets a second life?

**Why ask:** the reference counts every started stack as a whole stack (`integer`). If the remaining life of the last stack is used elsewhere, only the share of life used should be counted (`prorata`).

```bash
python scripts/run.py --set usage.stack_counting=prorata
```

| | Optimistic | Central | Pessimistic |
|---|---|---|---|
| Rise, integer counting (reference) | +5.0 % | +31.1 % | +35.0 % |
| Rise, prorata counting | +4.6 % | +14.7 % | +32.8 % |

**What it shows:** only the central case changes much, because its second fuel cell stack is used at 35 % only before the end of the horizon. Prorata is a lower bound: it assumes a second-life route that does not exist today for these stacks.

## 4. What if the vehicle drives less?

**Why ask:** 200 000 km is the Toyota target for the Mirai II stack; a vehicle may be scrapped earlier.

```bash
python scripts/run.py --set horizon.vehicle_km_total=150000
```

| | No ageing | Optimistic | Central | Pessimistic |
|---|---|---|---|---|
| Whole chain (g CO2-eq/km) | 84.25 | 87.56 (+3.9 %) | 113.87 (+35.2 %) | 116.23 (+38.0 %) |

**What it shows:** fabrication is spread over fewer kilometres, so every value rises, and so does the weight of the replacement stack.

## 5. How long must a fuel cell stack last to avoid a replacement?

**Why ask:** for a manufacturer or a fleet operator, the useful question is the threshold, not the exact lifetime.

```bash
python scripts/threshold.py --out results
```

It writes `results/threshold_fuel_cell.csv` (impact versus stack lifetime, from 1 500 to 12 000 h) and `results/model_choice.csv`. Thresholds found with the shipped data (horizon 5 554 operating hours):

| Stack lifetime | Fuel cell stacks | Whole chain rise |
|---|---|---|
| from 1 851 h | 3 | +56.6 % |
| from 2 777 h (half the horizon) | 2 | +31.6 % |
| from 5 554 h (the horizon) | 1 | +6.7 % |

**What it shows:** the result moves by steps. Gaining a few hundred hours changes nothing inside a step; crossing a threshold removes one stack.

## 6. What if I use my own ageing constants?

**Why ask:** the pessimistic case uses constants measured on laboratory cells. You may have other measurements.

```bash
python scripts/mechanistic_constants.py
```

It changes each constant of the mechanistic model alone, to another published value, and prints the end of life, stacks and rise. Output with the shipped data:

| Constant changed | Fuel cell end of life ; stacks | Chain rise |
|---|---|---|
| none (pessimistic reference) | 2 895 h ; 2 | +35.0 % |
| fuel cell high-current loss 27 mV instead of 45 mV | 5 652 h ; 1 | +12.8 % |
| fuel cell crossover factor 1.4 instead of 2.6 | 2 895 h ; 2 | +33.2 % |
| fuel cell platinum surface 0.65 instead of 0.67 | 2 909 h ; 2 | +35.0 % |
| electrolyser HFR drift 0 | 2 895 h ; 2 | +34.6 % |

**What it shows:** one constant, the fuel cell voltage loss at high current, decides the number of stacks; it is the one to measure first. Edit the `VARIANTS` list at the top of the script to test your own values, or set any constant directly, for example:

```bash
python scripts/run.py --set cases.pessimistic.fuel_cell.voltage_loss_at_1p8_A_cm2_1000h_V=0.035
```

## 7. Which inputs matter most, all together?

**Why ask:** the examples above change one input at a time. The global sensitivity analysis changes eight inputs together and ranks them.

```bash
python scripts/sobol.py --out results      # about 15 min on 2 cores
```

**What it shows:** the absolute impact depends mostly on the electricity source (total Sobol index 0.78); the rise due to ageing depends almost only on the fuel cell stack lifetime (0.94). The factors and their ranges are in `global_sensitivity` of `config/default.yaml`.

---

All the keys you can change, and how to replace a model, a measurement or an inventory: [CUSTOMISE.md](CUSTOMISE.md).
