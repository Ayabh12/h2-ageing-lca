"""Fit the polarisation curve of the fuel cell stack on the road measurements.

Method:
  1. split the signal file into recordings (time resets to zero) and keep the driving ones;
  2. keep quasi-steady points: current >= 30 A and less than 10 % change from the previous second;
  3. bin the current on a geometric grid (30 to 610 A) and take the median voltage of each bin
     (bins with at least 5 points from at least 2 recordings);
  4. fit  V = E_rev - RT/(alpha_c F) ln(j/i0c) - R j + Bc ln(1 - j/ilim)  by bounded least squares
     (trust region reflective) with 200 random starts (seed 1); keep the lowest cost.

The result is printed and written to data/parameters/pemfc_fit.json. Copy the four values
into ``fuel_cell.polarisation`` of your configuration to use them.

    python scripts/fit_pemfc.py [--signals data/measurements/mirai2_fuel_cell_signals.csv]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from h2ageing import load_config  # noqa: E402

R = 8.314462618
F = 96485.33212


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None)
    ap.add_argument("--signals", default=str(ROOT / "data/measurements/mirai2_fuel_cell_signals.csv"))
    ap.add_argument("--starts", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    fc = load_config(a.config)["fuel_cell"]
    T, alpha, N, A = fc["temperature_K"], fc["alpha_c"], fc["n_cells"], fc["active_area_cm2"]
    E_rev = 1.229 - 0.85e-3 * (T - 298.15)

    sig = pd.read_csv(a.signals).rename(columns={"time_s": "t", "speed_kmh": "v", "current_A": "I", "voltage_V": "U", "h2_level_pct": "H2"})
    sig["rec"] = np.r_[0, np.cumsum(np.diff(sig.t.to_numpy()) < 0)]
    info = sig.groupby("rec").agg(v_max=("v", "max"))
    driving = info.index[info.v_max > 0].tolist()
    drv = sig[sig.rec.isin(driving)].copy()

    def steady(g, tol=0.10):
        I = g.I.to_numpy()
        ok = np.zeros(len(I), bool)
        ok[1:] = np.abs(I[1:] - I[:-1]) / np.maximum(I[1:], 1.0) < tol
        return pd.Series(ok, index=g.index)

    drv["steady"] = drv.groupby("rec", group_keys=False).apply(steady)
    pts = drv[(drv.I >= 30.0) & drv.steady]
    edges = np.unique(np.round(np.geomspace(30.0, 610, 19)))
    g = pts.groupby(pd.cut(pts.I, edges), observed=True).agg(I=("I", "median"), U=("U", "median"), n=("U", "size"), n_rec=("rec", "nunique"))
    pol = g[(g.n >= 5) & (g.n_rec >= 2)].reset_index(drop=True)

    # bounds (log10 i0c, R, Bc, ilim) enclosing published values: i0c Vetter & Schumacher 2019 and Colombo et al. 2023;
    # R Colombo et al. 2023; Bc Almodfer et al. 2022; ilim Bielefeld et al. 2024 (lower bound above the measured maximum)
    lo = np.array([-12, 0, 0, 2.03])
    hi = np.array([-1, 0.3, 0.3, 6])
    jj, vv = pol.I.to_numpy() / A, pol.U.to_numpy() / N

    def V(j, th):
        l, Rt, Bc, il = th
        return E_rev - R * T / (alpha * F) * np.log(j / 10 ** l) - j * Rt + Bc * np.log(1 - j / il)

    rng = np.random.default_rng(a.seed)
    best, costs = None, []
    for _ in range(a.starts):
        s = least_squares(lambda x: V(jj, x) - vv, rng.uniform(lo, hi), bounds=(lo, hi), max_nfev=5000)
        costs.append(s.cost)
        if best is None or s.cost < best.cost:
            best = s
    th = best.x
    e = best.fun
    out = {"i0c_A_cm2": 10 ** th[0], "R0_ohm_cm2": th[1], "Bc_V": th[2], "ilim_A_cm2": th[3],
           "RMSE_mV_per_cell": 1e3 * float(np.sqrt(np.mean(e ** 2))),
           "R2": float(1 - np.sum(e ** 2) / np.sum((vv - vv.mean()) ** 2)),
           "starts_reaching_minimum": int(np.sum(np.array(costs) <= best.cost * 1.001)), "starts": a.starts,
           "median_points": pol.to_dict(orient="records")}
    dest = ROOT / "data/parameters/pemfc_fit.json"
    json.dump(out, open(dest, "w", encoding="utf-8"), indent=1, default=float)
    print(f"{len(pts)} quasi-steady points, {len(pol)} bins")
    for k in ["i0c_A_cm2", "R0_ohm_cm2", "Bc_V", "ilim_A_cm2", "RMSE_mV_per_cell", "R2"]:
        print(f"{k:18s} {out[k]:.10g}")
    print(f"{out['starts_reaching_minimum']}/{a.starts} starts reach the minimum ; written to {dest}")


if __name__ == "__main__":
    main()
