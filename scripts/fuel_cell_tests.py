"""Additional tests on the mechanistic fuel cell model (pessimistic case).

For the configured pessimistic cell (and a second cell, cell B of Colombo et al. 2023, for comparison):
  * crossover law beyond the 1000 h test: linear (default), exponential, constant;
  * an extra end-of-life criterion on the membrane: the stack also ends its life when the crossover
    reaches a threshold (10, 15 = DOE, 20 mA/cm2), whichever comes first;
  * a mean speed of 48 km/h instead of the measured 36 km/h (fewer operating hours).

Writes results/fuel_cell_tests.json and prints a table.

    python scripts/fuel_cell_tests.py
"""
import sys, json
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from h2ageing import load_config, with_values
from h2ageing.chain import Chain
from h2ageing.impacts import CLIMATE

base = load_config()
C = base["cases"]["pessimistic"]["fuel_cell"]
B = dict(C, ecsa_at_1000h=0.65, voltage_loss_at_1p8_A_cm2_1000h_V=0.027, crossover_factor_1000h=1.4)

def run(cell, law="linear", membrane=None, speed=None):
    cfg = with_values(base, **{"fuel_cell.crossover_law": law})
    ch = Chain(cfg); fc = ch.fc
    p = fc.parameters(cell)
    if speed:
        ch.L_fc_h = ch.km_total / speed
    if membrane is not None:
        orig = fc.end_of_life
        def eol(pp, max_h=60000.0):
            tv = orig(pp, max_h)
            g = lambda t: float(fc.crossover(t, pp) - membrane)
            tm = brentq(g, 0, max_h) if g(max_h) > 0 else np.inf
            return min(tv, tm)
        fc.end_of_life = eol
    ref = ch.fuel_cell_reference(); r = ch.fuel_cell_alone(p)
    s0 = ch.imp.single_score(ref["tot"]); s1 = ch.imp.single_score(r["tot"])
    te = r["eol_h"]
    te_, a, m = fc.life_table(p)
    # H2 per trip at EoL vs new, and crossover share in that rise
    rise_trip = 100 * (m[-1] / m[0] - 1)
    gap_cross = (fc.crossover(te, p) - fc.x0) * fc.A
    cur0, _ = fc.currents(0.0, p); curE, _ = fc.currents(te, p)
    dI_v = np.nansum((curE - cur0) * fc.dt); dI_x = gap_cross * np.sum(fc.active * fc.dt)
    share = 100 * dI_x / (dI_v + dI_x)
    return {"eol_h": te, "stacks": r["n"], "rise_climate": 100 * (r["tot"][CLIMATE] / ref["tot"][CLIMATE] - 1),
            "rise_score": 100 * (s1 / s0 - 1), "crossover_eol_mA": 1e3 * float(fc.crossover(te, p)),
            "h2_trip_eol_pct": rise_trip, "crossover_share_pct": share, "h2_km_mean_pct": r["h2_mean_rise_pct"]}

out = {}
for nm, cell in [("C", C), ("B", B)]:
    for law in ["linear", "exponential", "constant"]:
        out[f"{nm}_{law}"] = run(cell, law)
for law in ["linear", "exponential"]:
    for th in [0.010, 0.015, 0.020]:
        out[f"C_{law}_mem{int(th*1e3)}"] = run(C, law, membrane=th)
out["B_exponential_mem15"] = run(B, "exponential", membrane=0.015)
out["C_speed48"] = run(C, "linear", speed=48.0)
for k, v in out.items():
    print(f"{k:24s}", {a: round(float(b), 2) for a, b in v.items()})
(ROOT / "results").mkdir(exist_ok=True)
json.dump(out, open(ROOT / "results" / "fuel_cell_tests.json", "w"), indent=1, default=float)
