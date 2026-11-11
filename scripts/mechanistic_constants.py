"""Effect of each constant of the mechanistic ageing model (pessimistic case), changed alone.

Each constant goes from its default value to another published value, the others staying fixed:
  fuel cell (Colombo et al. 2023, cell B instead of cell C):
    * high-current voltage loss after 1000 h (sets the transport resistance growth r): 45 -> 27 mV
    * crossover factor after 1000 h: 2.6 -> 1.4
    * platinum surface after 1000 h (sets k): 0.67 -> 0.65
  electrolyser:
    * HFR drift set to 0, as measured under dynamic load or at 1.5 A/cm2 (Padgett et al. 2025, table I)
    * resistance drifts x 0.59, ratio measured between 60 and 80 C (Frensch et al. 2018)
    * membrane thinning rate x 0.57, ratio measured between 60 and 80 C (Frensch et al. 2019)

Writes results/mechanistic_constants.json and prints a table. Edit VARIANTS to test other values.

    python scripts/mechanistic_constants.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from h2ageing import load_config, with_values  # noqa: E402
from h2ageing.chain import Chain  # noqa: E402
from h2ageing.impacts import CLIMATE  # noqa: E402

P = "cases.pessimistic."
VARIANTS = [
    ("reference", {}),
    ("electrolyser: HFR drift = 0", {P + "electrolyser.hfr_drift_V_per_h_at_test": 0.0}),
    ("electrolyser: resistance drifts x 0.59 (60 C)", {P + "electrolyser.hfr_drift_V_per_h_at_test": 7.0e-6 * 0.59,
                                                      P + "electrolyser.catalyst_layer_drift_V_per_h_at_test": 3.4e-6 * 0.59}),
    ("electrolyser: membrane thinning x 0.57 (60 C)", {P + "electrolyser.membrane_half_thickness_time_h": 80700 / 0.57}),
    ("fuel cell: platinum surface 0.65", {P + "fuel_cell.ecsa_at_1000h": 0.65}),
    ("fuel cell: high-current loss 27 mV", {P + "fuel_cell.voltage_loss_at_1p8_A_cm2_1000h_V": 0.027}),
    ("fuel cell: crossover factor 1.4", {P + "fuel_cell.crossover_factor_1000h": 1.4}),
]


def main():
    base = load_config()
    out = {}
    for name, kv in VARIANTS:
        cfg = with_values(base, **kv)
        ch = Chain(cfg)
        c = cfg["cases"]["pessimistic"]
        pf, pw = ch.fc.parameters(c["fuel_cell"]), ch.we.parameters(c["electrolyser"])
        f, w = ch.fuel_cell_alone(pf), ch.electrolyser_alone(pw)
        fr, wr = ch.fuel_cell_reference()["tot"][CLIMATE], ch.electrolyser_reference()["tot"][CLIMATE]
        cr = ch.chain_reference()["total"][CLIMATE]
        cc = ch.chain(pf, pw, tuple(c["tank_permeation_mL_h_L"]))["total"][CLIMATE]
        out[name] = {"fuel_cell_eol_h": float(f["eol_h"]), "fuel_cell_stacks": float(f["n"]), "fuel_cell_rise_pct": 100 * (f["tot"][CLIMATE] / fr - 1),
                     "electrolyser_eol_h": float(w["eol_h"]), "electrolyser_stacks": float(w["n"]), "electrolyser_rise_pct": 100 * (w["tot"][CLIMATE] / wr - 1),
                     "chain_rise_pct": 100 * (cc / cr - 1)}
        o = out[name]
        print(f"{name:48s} FC {o['fuel_cell_eol_h']:7.0f} h {o['fuel_cell_stacks']:.0f} {o['fuel_cell_rise_pct']:+6.1f} % | "
              f"WE {o['electrolyser_eol_h']:7.0f} h {o['electrolyser_stacks']:.0f} {o['electrolyser_rise_pct']:+5.1f} % | chain {o['chain_rise_pct']:+5.1f} %")
    (ROOT / "results").mkdir(exist_ok=True)
    json.dump(out, open(ROOT / "results" / "mechanistic_constants.json", "w"), indent=1)


if __name__ == "__main__":
    main()
