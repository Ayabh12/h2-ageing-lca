# Use your own values

Every input sits in a YAML configuration (`config/default.yaml`). Change a value with `--set key=value`, or copy the file and edit it. Then run:

```bash
python scripts/run.py --config config/my_case.yaml --out results/my_case
python scripts/plot.py --results results/my_case
```

The tables written to the output folder are:

| File | Content |
|---|---|
| `life.csv` | end of life and number of stacks of each converter, mean over-consumption |
| `electrolyser.csv` | electrolyser alone, climate change per kg of hydrogen |
| `tank.csv` | tank alone, per km: fabrication, hydrogen lost by permeation, total, rise |
| `fuel_cell.csv` | fuel cell alone, climate change per km: use, fabrication, total, rise, single score |
| `chain.csv` | whole chain per km, by item, rise and single score |
| `categories.csv` | the 16 EF 3.1 categories: share of fabrication and rise of each case |

## 1. Usage quantities

| What | Key | Example |
|---|---|---|
| Compression energy | `usage.compression_kWh_per_kg` | `--set usage.compression_kWh_per_kg=3.2` |
| Water per kg of hydrogen | `usage.water_kg_per_kg_h2` | `--set usage.water_kg_per_kg_h2=9` |
| Electricity of the electrolyser | `usage.electricity_electrolyser` | `residual_mix_FR`, `average_mix_FR`, `nuclear_FR`, `wind_FR`, `photovoltaic` |
| Electricity of the compression | `usage.electricity_compression` | same choices |
| Hours of the electrolyser per year | `usage.electrolyser_hours_per_year` | `--set usage.electrolyser_hours_per_year=7392` |
| Stack counting | `usage.stack_counting` | `integer` or `prorata` |
| Distance and horizon | `horizon.vehicle_km_total`, `horizon.years` | `--set horizon.vehicle_km_total=250000` |

To add another electricity source, add a column to `data/impacts/electricity_per_kWh.csv` (impact of 1 kWh in the 16 categories) and use its name.

## 2. Ageing

Each case of `cases` chooses a model for each converter.

**Linear model** (published rates):

```yaml
fuel_cell:
  model: linear
  hours_to_end_of_life: 6000          # hours until 10 % voltage loss
electrolyser:
  model: linear
  rate_uV_per_h_per_cell: 3.0
```

**Mechanistic model** (laboratory constants):

```yaml
fuel_cell:
  model: mechanistic
  ecsa_at_1000h: 0.67
  omega: 3.6
  voltage_loss_at_1p8_A_cm2_1000h_V: 0.045
  crossover_factor_1000h: 2.6
electrolyser:
  model: mechanistic
  anode_activity_final: 0.1118
  anode_decay_time_h: 1000
  hfr_drift_V_per_h_at_test: 7.0e-6
  catalyst_layer_drift_V_per_h_at_test: 3.4e-6
  test_current_density_A_cm2: 3.0
  membrane_half_thickness_time_h: 80700
```

You can add a case (any name) or remove one; each case also gives the tank permeation `[P0, P15]` in mL/h/L. Other options: `fuel_cell.crossover_law` (`linear`, `exponential`, `constant`), the end-of-life criteria `fuel_cell.end_of_life_voltage_loss` and `electrolyser.end_of_life_voltage_rise`.

## 3. Fabrication

**Without ecoinvent**: edit `data/impacts/fabrication_per_unit.csv` (impact of one fuel cell stack, one electrolyser stack and one tank in the 16 categories), or add a column and point `fabrication.fuel_cell_stack`, `fabrication.electrolyser_stack` or `fabrication.tank` to it. A stack of another size can be represented with `electrolyser.stack_inventory_scale`.

**With ecoinvent**: change the amounts in `data/inventories/*.csv` and run `scripts/build_fabrication_brightway.py --project <your project>`; it writes a new fabrication file that you point to with `fabrication.file`.

## 4. Measurements and fitted models

- Another fuel cell or trip: replace `data/measurements/mirai2_fuel_cell_trip.csv` (columns `time_s`, `current_A`, `voltage_V`), give its distance and measured hydrogen (`fuel_cell.trip_distance_km`, `fuel_cell.trip_h2_measured_kg`), the number of cells and the active area, and refit the polarisation curve with `scripts/fit_pemfc.py` on your signals.
- Another electrolyser or profile: run `scripts/fit_pemwe.py --profile <file> --n-cells ... --area-cm2 ...`; it writes the parameter file read by the model (`electrolyser.params_file`).

## 5. Lifetime threshold and global sensitivity

```bash
python scripts/threshold.py --out results    # impact versus stack lifetime, model predictions placed on it
python scripts/sobol.py --out results        # Sobol indices of the chain (about 15 min on 2 cores)
```

`threshold.py` varies the stack lifetime with the linear model and places each configured case on the curve. It also separates the two effects of the choice of ageing model: the predicted end of life, and the shape of the trajectory at equal end of life (linear model set to the end of life of the mechanistic model).

`mechanistic_constants.py` changes each constant of the mechanistic model alone to another published value and ranks their effect; edit `VARIANTS` to test your own values.

`fuel_cell_tests.py` (`python scripts/fuel_cell_tests.py`) tests the mechanistic fuel cell model: crossover law, an extra membrane end-of-life criterion (crossover threshold) and the mean speed.

`sobol.py` reads the factors and their ranges in `global_sensitivity` of the configuration. Change a range, add or remove a factor among those listed, or change `samples`.

## 6. The models themselves

The models are plain Python classes:

- `FuelCell.cell_voltage(I, t, p)` and `FuelCell.crossover(t, p)` in `src/h2ageing/pemfc.py`;
- `Electrolyser.state(t, p)` in `src/h2ageing/pemwe.py`;
- `Tank.permeation(t, p)` in `src/h2ageing/tank.py`.

To try another ageing law, change these functions (or add a new `model:` value in `parameters()`). Everything downstream (end of life, number of stacks, LCA) uses them unchanged. Run `python tests/test_reference_results.py` before your change to check your installation, and expect the tests to fail after it: they compare with the reference results of the default configuration.
