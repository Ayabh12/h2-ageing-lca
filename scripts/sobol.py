"""Global sensitivity analysis (Sobol indices) of the climate change impact of the whole chain.

Factors and ranges: ``global_sensitivity`` in the configuration. Continuous factors are uniform
between their two bounds; the electricity source is discrete and equiprobable.

Outputs (climate change):
  * chain impact with ageing (g CO2-eq/km);
  * rise due to ageing (%), relative to the chain without ageing computed with the same factors.

Method: Saltelli sampling (two scrambled Sobol matrices A and B, plus the k matrices A_B^(i)),
first-order index with the Saltelli 2010 estimator, total index with the Jansen estimator,
95 % confidence intervals by bootstrap. N (k + 2) model runs.

    python scripts/sobol.py [--config ...] [--samples 1024] [--out results]
"""
import argparse
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import qmc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from h2ageing import load_config  # noqa: E402
from h2ageing.chain import Chain  # noqa: E402
from h2ageing.impacts import CLIMATE  # noqa: E402

_CH = None
_CFG = None


def _init(cfg):
    global _CH, _CFG
    _CFG = cfg
    _CH = Chain(cfg)


def factor_values(u, factors):
    """Map a row of [0,1) numbers to factor values."""
    out = {}
    for x, (name, rng) in zip(u, factors.items()):
        if isinstance(rng[0], str):
            out[name] = rng[min(int(x * len(rng)), len(rng) - 1)]
        else:
            out[name] = rng[0] + x * (rng[1] - rng[0])
    return out


def evaluate(v):
    ch, imp = _CH, _CH.imp
    base = _CFG
    imp.kwh_electrolyser = imp.electricity_source(v.get("electricity_electrolyser", base["usage"]["electricity_electrolyser"]))
    imp.compression = v.get("compression_kWh_per_kg", base["usage"]["compression_kWh_per_kg"]) * imp.kwh_compression
    if "fuel_cell_stack_kg_CO2" in v:
        imp.fuel_cell_stack = imp.fuel_cell_stack.copy()
        imp.fuel_cell_stack[CLIMATE] = v["fuel_cell_stack_kg_CO2"]
    if "tank_kg_CO2" in v:
        imp.tank = imp.tank.copy()
        imp.tank[CLIMATE] = v["tank_kg_CO2"]
    ch.ikg_ref = imp.h2_delivered(ch.we.SEC0)
    ch.we_hours_year = v.get("electrolyser_hours_per_year", base["usage"]["electrolyser_hours_per_year"])
    ch.L_we_h = ch.L * ch.we_hours_year
    central = base["cases"]["central"]   # values used for factors left out of the analysis
    pf = {"mu_lin": ch.fc.eol_frac * ch.fc.U0 / ch.fc.N / v.get("fuel_cell_lifetime_h", central["fuel_cell"]["hours_to_end_of_life"])}
    pw = {"mu_lin": v.get("electrolyser_drift_uV_per_h", central["electrolyser"]["rate_uV_per_h_per_cell"]) * 1e-6}
    perm = (6.0, v.get("tank_permeation_end_mL_h_L", central["tank_permeation_mL_h_L"][1]))
    aged = 1e3 * ch.chain(pf, pw, perm)["total"][CLIMATE]
    ref = 1e3 * ch.chain_reference((6.0, 6.0))["total"][CLIMATE]
    ch.fc._tab.clear()
    ch.we._tab.clear()
    return aged, 100 * (aged / ref - 1)


def _eval_row(args):
    u, factors = args
    return evaluate(factor_values(u, factors))


def indices(fA, fB, fAB, rng=None):
    var = np.var(np.r_[fA, fB], ddof=1)
    S1 = np.mean(fB[:, None] * (fAB - fA[:, None]), axis=0) / var
    ST = 0.5 * np.mean((fA[:, None] - fAB) ** 2, axis=0) / var
    return S1, ST


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None)
    ap.add_argument("--samples", type=int, default=None)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    cfg = load_config(a.config)
    gs = cfg["global_sensitivity"]
    factors = gs["factors"]
    k = len(factors)
    N = a.samples or gs["samples"]
    base = qmc.Sobol(d=2 * k, scramble=True, seed=gs["seed"]).random(N)
    A, B = base[:, :k], base[:, k:]
    rows = [A, B] + [np.where(np.arange(k) == i, B, A) for i in range(k)]
    X = np.vstack(rows)
    t0 = time.time()
    with Pool(a.workers, initializer=_init, initargs=(cfg,)) as pool:
        Y = np.array(pool.map(_eval_row, [(u, factors) for u in X], chunksize=16))
    print(f"{len(X)} runs in {time.time() - t0:.0f} s")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    vals = pd.DataFrame([factor_values(u, factors) for u in X])
    vals["chain_g_per_km"], vals["rise_pct"] = Y[:, 0], Y[:, 1]
    vals.to_csv(out / "sobol_runs.csv", index=False)

    rng = np.random.default_rng(gs["seed"])
    res = []
    for j, yname in enumerate(["chain_g_per_km", "rise_pct"]):
        y = Y[:, j]
        fA, fB = y[:N], y[N:2 * N]
        fAB = np.stack([y[(2 + i) * N:(3 + i) * N] for i in range(k)], axis=1)
        S1, ST = indices(fA, fB, fAB)
        bs1, bst = [], []
        for _ in range(gs["bootstrap"]):
            idx = rng.integers(0, N, N)
            s1, st = indices(fA[idx], fB[idx], fAB[idx])
            bs1.append(s1)
            bst.append(st)
        bs1, bst = np.array(bs1), np.array(bst)
        for i, name in enumerate(factors):
            res.append({"output": yname, "factor": name, "S1": S1[i], "S1_low": np.percentile(bs1[:, i], 2.5), "S1_high": np.percentile(bs1[:, i], 97.5),
                        "ST": ST[i], "ST_low": np.percentile(bst[:, i], 2.5), "ST_high": np.percentile(bst[:, i], 97.5)})
        print(f"\n{yname}: mean {y[:2 * N].mean():.2f}, 5-95 % [{np.percentile(y[:2 * N], 5):.2f}, {np.percentile(y[:2 * N], 95):.2f}], sum S1 = {S1.sum():.3f}")
    df = pd.DataFrame(res)
    df.to_csv(out / "sobol_indices.csv", index=False)
    print(df.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
