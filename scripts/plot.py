"""Plot the climate change impact of the chain per item for each case (from results/chain.csv).

    python scripts/plot.py [--results results] [--out results/chain.png]
"""
import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ITEMS = {"electricity_and_water_g_per_km": "Electricity and water", "compression_g_per_km": "Compression",
         "electrolyser_stacks_g_per_km": "Electrolyser stacks", "tank_g_per_km": "Tank", "fuel_cell_stacks_g_per_km": "Fuel cell stacks"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    df = pd.read_csv(Path(a.results) / "chain.csv").set_index("case")
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    bottom = pd.Series(0.0, index=df.index)
    colors = ["#4C72B0", "#8C8C8C", "#55A868", "#C9A227", "#C44E52"]
    for (col, lab), c in zip(ITEMS.items(), colors):
        ax.bar(df.index, df[col], bottom=bottom, label=lab, color=c)
        bottom += df[col]
    for i, (case, r) in enumerate(df.iterrows()):
        ax.text(i, r["total_g_per_km"] + 1, f"{r['total_g_per_km']:.1f}" + ("" if case == "no_ageing" else f"\n(+{r['rise_pct']:.1f} %)"),
                ha="center", va="bottom", fontsize=8.5)
    ax.set_ylabel("g CO$_2$-eq per km")
    ax.set_ylim(0, bottom.max() * 1.2)
    ax.legend(fontsize=8, ncol=2, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    out = Path(a.out) if a.out else Path(a.results) / "chain.png"
    fig.savefig(out, dpi=200)
    print("written to", out)


if __name__ == "__main__":
    main()
