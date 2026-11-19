"""Run the model for a configuration and write the result tables.

Examples
--------
    python scripts/run.py                                   # default configuration (reference results)
    python scripts/run.py --config config/my_case.yaml --out results/my_case
    python scripts/run.py --set usage.compression_kWh_per_kg=3.0
    python scripts/run.py --set usage.electricity_electrolyser=wind_FR
    python scripts/run.py --set cases.central.fuel_cell.hours_to_end_of_life=6000

Compare with earlier results (a folder written by a previous run):
    python scripts/run.py --out results/reference
    python scripts/run.py --set cases.central.fuel_cell.hours_to_end_of_life=6000 \
                          --out results/fc6000 --compare results/reference
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
    ap.add_argument("--compare", default=None, metavar="FOLDER",
                    help="folder of earlier results (from --out) to compare with")
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
    print("\nElectrolyser alone, climate change (per kg H2)")
    print(res["electrolyser"].round(3).to_string(index=False))
    print("\nTank alone, climate change (per km)")
    print(res["tank"].round(2).to_string(index=False))
    print("\nFuel cell alone, climate change (per km)")
    print(res["fuel_cell"].round(2).to_string(index=False))
    print("\nWhole chain, climate change (g CO2-eq per km)")
    print(res["chain"].round(2).to_string(index=False))
    print(f"\nTables written to {out.resolve()}")

    if a.compare:
        compare(res, Path(a.compare))


def compare(res, ref_dir):
    """Print the earlier results, the new ones and the difference, case by case."""
    if not (ref_dir / "chain.csv").exists():
        sys.exit(f"--compare: no chain.csv in {ref_dir}; write it first with --out {ref_dir}")
    life_ref = pd.read_csv(ref_dir / "life.csv")
    cols = ["case", "fuel_cell_stacks", "electrolyser_stacks"]
    life = life_ref[cols].merge(res["life"][cols], on="case", suffixes=("_before", "_now"))
    print(f"\nComparison with {ref_dir}: number of stacks")
    print(life.astype({c: int for c in life.columns if c != "case"}).to_string(index=False))

    for name, title in [("chain", "Whole chain"), ("fuel_cell", "Fuel cell alone"), ("tank", "Tank alone")]:
        before = pd.read_csv(ref_dir / f"{name}.csv")[["case", "total_g_per_km", "rise_pct"]]
        now = res[name][["case", "total_g_per_km", "rise_pct"]]
        t = before.merge(now, on="case", suffixes=("_before", "_now"))
        t["change_g_per_km"] = t["total_g_per_km_now"] - t["total_g_per_km_before"]
        t["change_pct"] = 100 * t["change_g_per_km"] / t["total_g_per_km_before"]
        print(f"\nComparison with {ref_dir}: {title}, climate change (g CO2-eq per km)")
        num = t.columns[1:]
        t[num] = t[num].round(2) + 0.0          # + 0.0 turns -0.0 into 0.0
        print(t.to_string(index=False))


if __name__ == "__main__":
    main()
