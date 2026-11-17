"""Figure: rise of the chain as a function of the fuel cell stack lifetime (steps), with the three cases.

Reads results/threshold_fuel_cell.csv (written by scripts/threshold.py) and results/chain.csv and
results/life.csv (written by scripts/run.py --out results).

    python scripts/run.py --out results
    python scripts/threshold.py --out results
    python scripts/plot_steps.py --results results --lang fr --out docs/figures/steps.fr.png
"""
import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

TEXT = {
    "en": dict(x="Lifetime of one fuel cell stack (h)", y="Rise of the chain due to ageing (%)",
               stacks="{n} stack{s}", horizon="5 554 h = fuel cell operation\nover 200 000 km",
               cases={"pessimistic": "pessimistic", "central": "central", "optimistic": "optimistic"}, dec="."),
    "fr": dict(x="Durée de vie d'un stack de pile (h)", y="Hausse de la chaîne due au vieillissement (%)",
               stacks="{n} stack{s}", horizon="5 554 h = fonctionnement de la pile\nsur 200 000 km",
               cases={"pessimistic": "pessimiste", "central": "central", "optimistic": "optimiste"}, dec=","),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--lang", choices=["en", "fr"], default="en")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    t = TEXT[a.lang]
    r = Path(a.results)
    th = pd.read_csv(r / "threshold_fuel_cell.csv")
    th = th[(th.lifetime_h >= 1900) & (th.lifetime_h <= 9000)]
    chain = pd.read_csv(r / "chain.csv").set_index("case")
    life = pd.read_csv(r / "life.csv").set_index("case")

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    colors = {3: "#f3d9d9", 2: "#fbe8cf", 1: "#dcebdc"}
    horizon_h = 5554.47  # fuel cell operating hours over the horizon (threshold.py); steps at horizon / n
    for n in sorted(th.stacks.unique()):
        lo, hi = max(horizon_h / n, th.lifetime_h.min()), min(horizon_h / (n - 1) if n > 1 else 9000, 9000)
        ax.axvspan(lo, hi, color=colors.get(int(n), "#eeeeee"), lw=0)
        ax.text((lo + hi) / 2, 66, t["stacks"].format(n=int(n), s="s" if n > 1 else ""),
                ha="center", va="center", fontsize=10, weight="bold", color="#444444")
    ax.step(th.lifetime_h, th.chain_rise_pct, where="post", color="#3b6ea5", lw=2)
    ax.axvline(5554, color="firebrick", ls="--", lw=1.2)
    ax.text(5554 + 120, 50, t["horizon"], color="firebrick", fontsize=8.5, va="center")
    for case, (dx, dy) in {"pessimistic": (30, 8), "central": (0, -10), "optimistic": (0, 8)}.items():
        x = life.loc[case, "fuel_cell_end_of_life_h"]
        y = chain.loc[case, "rise_pct"]
        ax.plot(x, y, "o", color="black", ms=6, zorder=5)
        lab = f"{t['cases'][case]}\n+{y:.1f} %".replace(".", t["dec"])
        ax.annotate(lab, (x, y), xytext=(dx, dy), textcoords="offset points", ha="left" if dx else "center",
                    va="bottom" if dy > 0 else "top", fontsize=9)
    ax.set_xlim(th.lifetime_h.min(), 9000)
    ax.set_ylim(0, 70)
    ax.set_xlabel(t["x"])
    ax.set_ylabel(t["y"])
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    out = Path(a.out) if a.out else r / f"steps.{a.lang}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200)
    print("written to", out)


if __name__ == "__main__":
    main()
