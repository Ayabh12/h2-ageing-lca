# Fabrication inventories

**English** | [Français](README.fr.md)

Each file lists what is needed to manufacture **one unit** of a component: one fuel cell stack, one electrolyser stack or one tank. Every row is one input: a material, an energy or a resource, with its amount and the ecoinvent 3.11 dataset (cut-off) it is linked to. The impact of the component is the sum of the impacts of these inputs, each counted from the extraction of resources to the market ([what each impact includes](../../docs/METHOD.md#what-each-impact-includes)).

Columns of the CSV files:

| Column | Meaning |
|---|---|
| `part` | part of the component the input belongs to (when the source gives it) |
| `input` | material, energy or resource, in plain words |
| `amount`, `unit` | quantity for one unit of the component |
| `flow_type` | `material`, `energy`, `processing` (a transformation of a material, such as wire drawing) or `resource` (taken directly from nature) |
| `ecoinvent_activity`, `reference_product`, `location`, `database` | the ecoinvent dataset linked to the input |
| `ecoinvent_code` | code of the ecoinvent dataset, when it is used to identify it |
| `biosphere_category` | for a resource, its category in the biosphere database |
| `included` | `yes` or `no`: set `no` to leave a row out when rebuilding the impact |
| `source` | where the amount comes from |

To print the three inventories: `python scripts/build_fabrication_brightway.py --check`. To rebuild the impacts after changing an amount (needs ecoinvent): `python scripts/build_fabrication_brightway.py --project <your project>`.

---

## Inventory of the fuel cell stack (128 kW)

`fuel_cell_stack_128kW.csv` · Source: Mori et al. 2023 (48 kW stack), scaled by 128/48. The source gives the materials of the whole stack, not their split by part.

| Part | Input | Amount | Unit |
|---|---|---|---|
| Stack materials | Stainless steel (chromium steel 18/8) | 59.87 | kg |
| | Glass fibre | 10.1 | kg |
| | Low-alloyed steel | 7.52 | kg |
| | Polyethylene terephthalate (PET) | 4.85 | kg |
| | Silicone | 3.36 | kg |
| | Acrylonitrile | 3.33 | kg |
| | Copper | 2.53 | kg |
| | Deionised water | 1.31 | kg |
| | Ethoxylated alcohol (AE11) | 0.587 | kg |
| | Tetrafluoroethylene | 0.384 | kg |
| | Carbon black | 0.104 | kg |
| | Platinum | 0.069 | kg |
| | Copper wire drawing (processing of the 2.53 kg of copper) | 2.53 | kg |
| Manufacturing energy | Electricity, French residual mix, high voltage | 1 096 | kWh |
| **Total** | **materials** | **94.0** | **kg** |
| | **energy** | **1 096** | **kWh** |

Climate change impact of one stack: 3 698 kg CO2-eq.

## Inventory of the electrolyser stack (1.25 MW)

`electrolyser_stack_1p25MW.csv` · Source: Lundberg 2019 (per MW of stack), scaled to 1.25 MW.

| Part | Input | Amount | Unit |
|---|---|---|---|
| Bipolar plates | Titanium | 660 | kg |
| Outer casing | Stainless steel (chromium steel 18/8) | 125 | kg |
| Current collectors | Aluminium, wrought alloy | 33.75 | kg |
| | Copper | 5.625 | kg |
| Membrane | Tetrafluoroethylene | 20 | kg |
| Electrodes | Activated carbon, granular | 11.25 | kg |
| | Iridium (resource, see below) | 0.9375 | kg |
| | Platinum | 0.09375 | kg |
| Assembly energy | Electricity, French residual mix, medium voltage | 6 700 | kWh |
| **Total** | **materials and resources** | **856.7** | **kg** |
| | **energy** | **6 700** | **kWh** |

Climate change impact of one stack: 39 509 kg CO2-eq. Iridium has no ecoinvent dataset: it is counted as a resource taken from the ground, so its extraction weighs on resource depletion but no impact of its processing is counted.

## Inventory of the hydrogen tank (type IV, 5.6 kg, 700 bar)

`tank_type_IV.csv` · Source: Benitez et al. 2021.

| Part | Input | Amount | Unit |
|---|---|---|---|
| Composite shell | Carbon fibre | 76 | kg |
| | Epoxy resin | 26 | kg |
| Liner | High-density polyethylene | 7.5 | kg |
| Manufacturing energy | Electricity, high voltage, global market | 338.64 | kWh |
| | Electricity, low voltage, natural gas heat and power co-generation | 43.2 | kWh |
| **Total** | **materials** | **109.5** | **kg** |
| | **energy** | **381.84** | **kWh** |

Climate change impact of one tank: 2 332 kg CO2-eq, of which 2 075 kg for the materials and 257 kg for the manufacturing energy.
