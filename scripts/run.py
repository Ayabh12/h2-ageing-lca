"""Run the model for a configuration and write the result tables.

Examples
--------
    python scripts/run.py                                   # default configuration (reference results)
    python scripts/run.py --config config/my_case.yaml --out results/my_case
    python scripts/run.py --set usage.compression_kWh_per_kg=3.0
    python scripts/run.py --set usage.electricity_electrolyser=wind_FR
    python scripts/run.py --set cases.central.fuel_cell.hours_to_end_of_life=6000
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402

from h2ageing import load_config, run  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None, help="YAML configuration (default: config/default.yaml)")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", help="override one value, e.g. usage.compression_kWh_per_kg=3")
    ap.add_argument("--out", default="results", help="output folder for the CSV tables")
    a = ap.parse_args()

    cfg = load_config(a.config, a.set)
    res = run(cfg)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, df in res.items():
        df.to_csv(out / f"{name}.csv", index=False)

    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 20)
    print("\nEnd of life and number of stacks")
    print(res["life"].round(1).to_string(index=False))
    print("\nFuel cell alone, climate change (per km)")
    print(res["fuel_cell"].round(2).to_string(index=False))
    print("\nElectrolyser alone, climate change (per kg H2)")
    print(res["electrolyser"].round(3).to_string(index=False))
    print("\nWhole chain, climate change (g CO2-eq per km)")
    print(res["chain"].round(2).to_string(index=False))
    print(f"\nTables written to {out.resolve()}")


if __name__ == "__main__":
    main()
