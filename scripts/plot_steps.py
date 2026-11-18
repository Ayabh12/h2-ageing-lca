"""Figure: rise of the chain as a function of the fuel cell stack lifetime, with the three cases.

The rise moves in steps, because the number of stacks is a whole number.

The curve varies only the fuel cell stack lifetime (linear model); the electrolyser and the
tank keep the values of the central case. The points are the three ageing cases.

    python scripts/plot_steps.py --lang fr --out docs/figures/steps.fr.png
"""
import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from h2ageing import load_config, run  # noqa: E402
from h2ageing.chain import Chain  # noqa: E402

CC = "climate_change"
TEXT = {
    "fr": dict(
        x="Durée de vie d'un stack de pile (h)", y1="Hausse de la chaîne\ndue au vieillissement (%)",
        y2="dont surconsommation (%)", stacks="{n} stack{s}",
        half="2 777 h : moitié de l'horizon\n(en dessous : 3 stacks)", horizon="5 554 h : la pile fonctionne\n5 554 h sur 200 000 km",
        cases={"pessimistic": ("pessimiste", "2 895 h : fin de vie calculée\npar le modèle semi-empirique"),
               "central": ("central", "4 100 h : état actuel\nmesuré par le DOE"),
               "optimistic": ("optimiste", "8 000 h : objectif\ndu DOE")},
        over="La surconsommation varie peu et sans à-coup ;\nce sont les remplacements qui font les marches.", dec=","),
    "en": dict(
        x="Lifetime of one fuel cell stack (h)", y1="Rise of the chain\ndue to ageing (%)",
        y2="of which\nover-consumption (%)", stacks="{n} stack{s}",
        half="2 777 h: half the horizon\n(below: 3 stacks)", horizon="5 554 h: the fuel cell runs\n5 554 h over 200 000 km",
        cases={"pessimistic": ("pessimistic", "2 895 h: end of life computed\nby the semi-empirical model"),
               "central": ("central", "4 100 h: current status\nmeasured by the DOE"),
               "optimistic": ("optimistic", "8 000 h: DOE\ntarget")},
        over="Over-consumption varies little and smoothly;\nreplacements make the steps.", dec="."),
}


def curves(cfg):
    ch = Chain(cfg)
    C = cfg["cases"]
    pw = ch.we.parameters(C["central"]["electrolyser"])
    perm = C["central"]["tank_permeation_mL_h_L"]
    ref = ch.chain_reference()
    rt = ref["total"][CC]
    use_ref = ref["parts"]["electricity_and_water"][CC] + ref["parts"]["compression"][CC]
    L = ch.L_fc_h
    h = np.unique(np.r_[np.linspace(1900, 9000, 400), [L / k * (1 + s * 1e-6) for k in (2, 3) for s in (-1, 1)], L * (1 - 1e-6), L * (1 + 1e-6)])
    rise, over = [], []
    for x in h:
        c = ch.chain({"mu_lin": ch.fc.eol_frac * ch.fc.U0 / ch.fc.N / x}, pw, perm)
        use = c["parts"]["electricity_and_water"][CC] + c["parts"]["compression"][CC]
        rise.append(100 * (c["total"][CC] / rt - 1))
        over.append(100 * (use - use_ref) / rt)
    return h, np.array(rise), np.array(over), L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None)
    ap.add_argument("--lang", choices=["en", "fr"], default="en")
    ap.add_argument("--font", default=None, help="font family, e.g. Inter")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    t = TEXT[a.lang]
    if a.font:
        plt.rcParams["font.family"] = a.font
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    cfg = load_config(a.config)
    h, rise, over, L = curves(cfg)
    res = run(cfg)
    chain = res["chain"].set_index("case")
    life = res["life"].set_index("case")

    fig, ax = plt.subplots(figsize=(8, 4.6))
    cols = {3: "#f6e0e0", 2: "#fcecd6", 1: "#e3f0e3"}
    for n in (3, 2, 1):
        lo, hi = max(L / n, 1900), (L / (n - 1) if n > 1 else 9000)
        ax.axvspan(lo, min(hi, 9000), color=cols[n], lw=0)
        ax.text((lo + min(hi, 9000)) / 2, 70, t["stacks"].format(n=n, s="s" if n > 1 else ""),
                ha="center", fontsize=10, weight="bold", color="0.3")
    ax.step(h, rise, where="post", color="#3b6ea5", lw=2)
    for x, lab in [(L / 2, t["half"]), (L, t["horizon"])]:
        ax.axvline(x, color="firebrick", ls="--", lw=1)
        ax.text(x + 60, 62, lab, color="firebrick", fontsize=7.5, va="center")
    place = {"pessimistic": (3000, 42, "left"), "central": (4170, 26, "left"), "optimistic": (8000, 11, "center")}
    for case, (tx, ty, ha) in place.items():
        x = life.loc[case, "fuel_cell_end_of_life_h"]
        y = chain.loc[case, "rise_pct"]
        name, why = t["cases"][case]
        ax.vlines(x, 0, y, color="0.25", ls=":", lw=1)
        ax.plot(x, y, "o", color="k", ms=6, zorder=5)
        head = (f"{name} : +{y:.1f} %".replace(".", ",")) if a.lang == "fr" else f"{name}: +{y:.1f} %"
        ax.annotate(head + "\n" + (why.replace("\n", " ") if case == "optimistic" else why), (x, y),
                    xytext=(tx, ty), textcoords="data", ha=ha, va="top" if case == "central" else "bottom", fontsize=7.8,
                    arrowprops=dict(arrowstyle="-", color="0.4", lw=0.6) if case == "pessimistic" else None)
    ax.set_xlim(1900, 9000)
    ax.set_ylim(0, 75)
    ax.set_ylabel(t["y1"])
    ax.set_xlabel(t["x"])
    fig.tight_layout()
    out = Path(a.out or f"results/steps.{a.lang}.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200)
    print("written to", out)


if __name__ == "__main__":
    main()
