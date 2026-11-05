"""Fit the new-state model of the electrolyser on the measured wind profile.

Method:
  * cell voltage V = E_rev(T) + RT/(2 alpha_a F) ln(j/i0a) + R j - Bc ln(1 - j/ilim);
  * alpha_a is fixed by the Tafel slope measured by Padgett et al. 2025 (46 mV/dec at 80 C);
  * i0a, R and Bc are fitted on the 1 s profile by bounded least squares (trust region
    reflective), 50 random starts (seed 180);
  * the profile gives the reference energy E0, hydrogen H20, SEC0 = E0/H20, the Faraday
    efficiency, the mean current density j_ref and the voltage at j_ref (end-of-life criterion);
  * W0 = sum(E_step / V0) and Wj = sum(E_step j / V0) give the energy change for a uniform
    voltage rise and for a resistance rise (first-order update used by the ageing model).

Writes data/parameters/pemwe_fit.json (read by the model).

    python scripts/fit_pemwe.py [--profile data/measurements/nel_mc250_wind_profile.xlsx]
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
R = 8.314462618
F = 96485.33212
M_H2 = 2.01588e-3


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profile", default=str(ROOT / "data/measurements/nel_mc250_wind_profile.xlsx"))
    ap.add_argument("--n-cells", type=int, default=200)
    ap.add_argument("--area-cm2", type=float, default=1500.0)
    ap.add_argument("--temperature-C", type=float, default=80.0, help="temperature of the model (that of the ageing tests)")
    ap.add_argument("--tafel-mV-dec", type=float, default=46.0, help="Padgett et al. 2025")
    ap.add_argument("--ilim", type=float, default=3.0)
    ap.add_argument("--starts", type=int, default=50)
    ap.add_argument("--seed", type=int, default=180)
    ap.add_argument("--out", default=str(ROOT / "data/parameters/pemwe_fit.json"))
    a = ap.parse_args()

    df = pd.read_excel(a.profile, sheet_name="Profil_1s_source")
    cols = ["t (s)", "Puissance PSU (kW)", "Tension PSU (V)", "Courant PSU (A)", "Débit H2 mesuré (kg/h)", "Énergie élect. par pas (kWh)", "H2 par pas (kg)"]
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    inter = ["Puissance PSU (kW)", "Tension PSU (V)", "Courant PSU (A)", "Débit H2 mesuré (kg/h)"]
    df[inter] = df[inter].interpolate(limit_direction="both")
    df = df.dropna(subset=["t (s)", "Énergie élect. par pas (kWh)", "H2 par pas (kg)"]).copy()

    N, A = a.n_cells, a.area_cm2
    t = df["t (s)"].to_numpy(float)
    dt = np.diff(t, append=t[-1] + np.median(np.diff(t)))
    I = df["Courant PSU (A)"].to_numpy(float)
    U = df["Tension PSU (V)"].to_numpy(float)
    E_step = df["Énergie élect. par pas (kWh)"].to_numpy(float)
    E0 = float(E_step.sum())
    H20 = float(df["H2 par pas (kg)"].sum())
    etaF0 = H20 / (N * M_H2 * float(np.sum(I * dt)) / (2 * F))

    T = a.temperature_C + 273.15
    b = a.tafel_mV_dec / 1e3
    alpha = np.log(10) * R * T / (2 * F * b)
    E_rev = 1.229 - 0.85e-3 * (T - 298.15)
    j_all, v_all = I / A, U / N
    ok = np.isfinite(j_all) & np.isfinite(v_all) & (j_all > 0) & (j_all < a.ilim)
    j, v = j_all[ok], v_all[ok]

    def voltage(jj, th):
        log_i0, Rt, Bc = th
        jj = np.asarray(jj, float)
        return E_rev + R * T / (2 * F * alpha) * np.log(jj / np.exp(log_i0)) + Rt * jj - Bc * np.log1p(-jj / a.ilim)

    lo, hi = np.array([np.log(1e-14), 0, 0]), np.array([np.log(1e-1), 1, 1])
    rng = np.random.default_rng(a.seed)
    best = None
    for _ in range(a.starts):
        s = least_squares(lambda x: voltage(j, x) - v, rng.uniform(lo, hi), bounds=(lo, hi), max_nfev=10000)
        if best is None or np.sum(s.fun ** 2) < np.sum(best.fun ** 2):
            best = s
    th = best.x
    err = voltage(j, th) - v
    j_ref = float(np.mean(j_all))
    V0 = voltage(j_all, th)
    P = {"T_K": T, "b_tafel": b, "alpha_a": alpha, "Erev": E_rev, "i0a": float(np.exp(th[0])), "R0": float(th[1]), "Bc": float(th[2]),
         "ilim": a.ilim, "RMSE_mV": 1e3 * float(np.sqrt(np.mean(err ** 2))), "R2": float(1 - np.sum(err ** 2) / np.sum((v - v.mean()) ** 2)),
         "j_ref": j_ref, "Vref0": float(voltage(j_ref, th)), "Vmean0": float(np.mean(V0)),
         "E0": E0, "H20": H20, "SEC0": E0 / H20, "etaF0": etaF0,
         "W0": float(np.sum(E_step / V0)), "Wj": float(np.sum(E_step * j_all / V0))}
    json.dump(P, open(a.out, "w", encoding="utf-8"), indent=1)
    for k in ["i0a", "R0", "Bc", "RMSE_mV", "R2", "j_ref", "Vref0", "SEC0", "etaF0", "W0", "Wj"]:
        print(f"{k:8s} {P[k]:.10g}")
    print("written to", a.out)


if __name__ == "__main__":
    main()
