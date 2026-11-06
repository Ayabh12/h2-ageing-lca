"""Impact as a function of the stack lifetime, with the predictions of each ageing model placed on it.

For each converter, the lifetime of the stack (hours to the 10 % criterion) is varied with the
linear model; the results of the configured cases (and of the mechanistic variants) are added
as points. Writes results/threshold_fuel_cell.csv, results/threshold_electrolyser.csv,
results/model_choice.csv and results/threshold.pdf.

    python scripts/threshold.py [--config ...] [--out results]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from h2ageing import load_config  # noqa: E402
from h2ageing.chain import Chain  # noqa: E402
from h2ageing.impacts import CLIMATE  # noqa: E402


def fc_curve(ch, hours, pw, perm):
    rows = []
    ref = 1e3 * ch.fuel_cell_reference()["tot"][CLIMATE]
    cref = 1e3 * ch.chain_reference()["total"][CLIMATE]
    for h in hours:
        p = {"mu_lin": ch.fc.eol_frac * ch.fc.U0 / ch.fc.N / h}
        r = ch.fuel_cell_alone(p)
        c = ch.chain(p, pw, perm)
        rows.append({"lifetime_h": h, "stacks": r["n"], "use_g_per_km": 1e3 * r["use"][CLIMATE], "fabrication_g_per_km": 1e3 * r["fab"][CLIMATE],
                     "total_g_per_km": 1e3 * r["tot"][CLIMATE], "rise_pct": 100 * (1e3 * r["tot"][CLIMATE] / ref - 1),
                     "chain_g_per_km": 1e3 * c["total"][CLIMATE], "chain_rise_pct": 100 * (1e3 * c["total"][CLIMATE] / cref - 1)})
    return pd.DataFrame(rows)


def we_curve(ch, hours):
    rows = []
    ref = ch.electrolyser_reference()["tot"][CLIMATE]
    for h in hours:
        p = {"mu_lin": ch.we.eol_frac * ch.we.Vref0 / h}
        r = ch.electrolyser_alone(p)
        rows.append({"lifetime_h": h, "stacks": r["n"], "use_kg_per_kg": r["use"][CLIMATE], "fabrication_kg_per_kg": r["fab"][CLIMATE],
                     "total_kg_per_kg": r["tot"][CLIMATE], "rise_pct": 100 * (r["tot"][CLIMATE] / ref - 1)})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None)
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    cfg = load_config(a.config)
    ch = Chain(cfg)
    C = cfg["cases"]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    pf = {k: ch.fc.parameters(C[k]["fuel_cell"]) for k in C}
    pw = {k: ch.we.parameters(C[k]["electrolyser"]) for k in C}
    central_pw, central_perm = pw.get("central", next(iter(pw.values()))), C.get("central", next(iter(C.values())))["tank_permeation_mL_h_L"]

    # ---------- curves (linear model, lifetime varied)
    L = ch.L_fc_h
    hfc = np.unique(np.r_[np.linspace(1500, 12000, 211), [L / 3 * (1 - 1e-6), L / 3 * (1 + 1e-6), L / 2 * (1 - 1e-6), L / 2 * (1 + 1e-6), L * (1 - 1e-6), L * (1 + 1e-6)]])
    fcc = fc_curve(ch, hfc, central_pw, central_perm)
    fcc.to_csv(out / "threshold_fuel_cell.csv", index=False)
    Lw = ch.L_we_h
    hwe = np.unique(np.r_[np.linspace(15000, 120000, 211), [Lw / k * (1 + s * 1e-6) for k in (2, 3, 4, 5) for s in (-1, 1)]])
    wec = we_curve(ch, hwe)
    wec.to_csv(out / "threshold_electrolyser.csv", index=False)

    # ---------- model predictions and the two effects of the model choice
    fr = 1e3 * ch.fuel_cell_reference()["tot"][CLIMATE]
    wr = ch.electrolyser_reference()["tot"][CLIMATE]
    rows = []
    for k in C:
        f = ch.fuel_cell_alone(pf[k])
        rows.append({"converter": "fuel_cell", "case": k, "model": C[k]["fuel_cell"]["model"], "variant": "", "eol_h": f["eol_h"], "stacks": f["n"],
                     "use": 1e3 * f["use"][CLIMATE], "fabrication": 1e3 * f["fab"][CLIMATE], "total": 1e3 * f["tot"][CLIMATE], "rise_pct": 100 * (1e3 * f["tot"][CLIMATE] / fr - 1)})
        w = ch.electrolyser_alone(pw[k])
        rows.append({"converter": "electrolyser", "case": k, "model": C[k]["electrolyser"]["model"], "variant": "", "eol_h": w["eol_h"], "stacks": w["n"],
                     "use": w["use"][CLIMATE], "fabrication": w["fab"][CLIMATE], "total": w["tot"][CLIMATE], "rise_pct": 100 * (w["tot"][CLIMATE] / wr - 1)})
    mech = [k for k in C if C[k]["fuel_cell"]["model"] == "mechanistic"]
    if mech:
        k = mech[0]
        base = pf[k]
        variants = {"Pt surface loss +20 %": {**base, "S1000": 1 - (1 - base["S1000"]) * 1.2},
                    "resistance growth +20 %": {**base, "k_R": base["k_R"] * 1.2},
                    "Pt surface loss -20 %": {**base, "S1000": 1 - (1 - base["S1000"]) * 0.8},
                    "resistance growth -20 %": {**base, "k_R": base["k_R"] * 0.8}}
        same = {"mu_lin": ch.fc.eol_frac * ch.fc.U0 / ch.fc.N / ch.fc.end_of_life(base)}
        variants["linear model, same end of life"] = same
        for name, p in variants.items():
            f = ch.fuel_cell_alone(p)
            rows.append({"converter": "fuel_cell", "case": k, "model": "linear" if "mu_lin" in p else "mechanistic", "variant": name, "eol_h": f["eol_h"], "stacks": f["n"],
                         "use": 1e3 * f["use"][CLIMATE], "fabrication": 1e3 * f["fab"][CLIMATE], "total": 1e3 * f["tot"][CLIMATE], "rise_pct": 100 * (1e3 * f["tot"][CLIMATE] / fr - 1)})
        for law in ("exponential", "constant"):
            from h2ageing import with_values
            ch2 = Chain(with_values(cfg, **{"fuel_cell.crossover_law": law}))
            f = ch2.fuel_cell_alone(ch2.fc.parameters(C[k]["fuel_cell"]))
            rows.append({"converter": "fuel_cell", "case": k, "model": "mechanistic", "variant": f"crossover law {law}", "eol_h": f["eol_h"], "stacks": f["n"],
                         "use": 1e3 * f["use"][CLIMATE], "fabrication": 1e3 * f["fab"][CLIMATE], "total": 1e3 * f["tot"][CLIMATE], "rise_pct": 100 * (1e3 * f["tot"][CLIMATE] / fr - 1)})
    mech_w = [k for k in C if C[k]["electrolyser"]["model"] == "mechanistic"]
    if mech_w:
        k = mech_w[0]
        same = {"mu_lin": ch.we.eol_frac * ch.we.Vref0 / ch.we.end_of_life(pw[k])}
        w = ch.electrolyser_alone(same)
        rows.append({"converter": "electrolyser", "case": k, "model": "linear", "variant": "linear model, same end of life", "eol_h": w["eol_h"], "stacks": w["n"],
                     "use": w["use"][CLIMATE], "fabrication": w["fab"][CLIMATE], "total": w["tot"][CLIMATE], "rise_pct": 100 * (w["tot"][CLIMATE] / wr - 1)})
    pts = pd.DataFrame(rows)
    pts.to_csv(out / "model_choice.csv", index=False)
    print(pts.round(3).to_string(index=False))
    print(f"\nfuel cell operating hours over the horizon: {L:.0f} h ; electrolyser: {Lw:.0f} h")


if __name__ == "__main__":
    main()
