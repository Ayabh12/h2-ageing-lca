"""Run all cases of a configuration and build the result tables."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .chain import Chain
from .impacts import CLIMATE


def pct(a, b):
    return 100.0 * (a / b - 1.0)


def run(cfg: dict) -> dict[str, pd.DataFrame]:
    ch = Chain(cfg)
    imp = ch.imp
    cases = cfg["cases"]
    fc_ref, we_ref = ch.fuel_cell_reference(), ch.electrolyser_reference()
    chain_ref = ch.chain_reference()

    life, fc_rows, we_rows, chain_rows, cat_rows, parts_rows = [], [], [], [], [], []
    fc_res, we_res, ch_res = {}, {}, {}
    for name, case in cases.items():
        pf = ch.fc.parameters(case["fuel_cell"])
        pw = ch.we.parameters(case["electrolyser"])
        fc_res[name] = f = ch.fuel_cell_alone(pf)
        we_res[name] = w = ch.electrolyser_alone(pw)
        ch_res[name] = c = ch.chain(pf, pw, case["tank_permeation_mL_h_L"])
        life.append({"case": name, "fuel_cell_model": case["fuel_cell"]["model"], "fuel_cell_end_of_life_h": f["eol_h"],
                     "fuel_cell_stacks": f["n"], "electrolyser_model": case["electrolyser"]["model"],
                     "electrolyser_end_of_life_h": w["eol_h"], "electrolyser_stacks": w["n"],
                     "h2_per_km_mean_rise_pct": f["h2_mean_rise_pct"], "sec_mean_rise_pct": w["sec_mean_rise_pct"]})

    def fc_row(name, r):
        return {"case": name, "use_g_per_km": 1e3 * r["use"][CLIMATE], "fabrication_g_per_km": 1e3 * r["fab"][CLIMATE],
                "total_g_per_km": 1e3 * r["tot"][CLIMATE], "rise_pct": pct(r["tot"][CLIMATE], fc_ref["tot"][CLIMATE]),
                "single_score_uPt_per_km": 1e6 * imp.single_score(r["tot"])}

    def we_row(name, r):
        return {"case": name, "use_kg_per_kg": r["use"][CLIMATE], "fabrication_kg_per_kg": r["fab"][CLIMATE],
                "total_kg_per_kg": r["tot"][CLIMATE], "rise_pct": pct(r["tot"][CLIMATE], we_ref["tot"][CLIMATE]),
                "single_score_uPt_per_kg": 1e6 * imp.single_score(r["tot"])}

    fc_rows = [fc_row("no_ageing", fc_ref)] + [fc_row(n, r) for n, r in fc_res.items()]
    we_rows = [we_row("no_ageing", we_ref)] + [we_row(n, r) for n, r in we_res.items()]
    for name, r in [("no_ageing", chain_ref)] + list(ch_res.items()):
        row = {"case": name}
        row.update({f"{k}_g_per_km": 1e3 * v[CLIMATE] for k, v in r["parts"].items()})
        row["total_g_per_km"] = 1e3 * r["total"][CLIMATE]
        row["rise_pct"] = pct(r["total"][CLIMATE], chain_ref["total"][CLIMATE])
        row["single_score_uPt_per_km"] = 1e6 * imp.single_score(r["total"])
        row["single_score_rise_pct"] = pct(imp.single_score(r["total"]), imp.single_score(chain_ref["total"]))
        chain_rows.append(row)
    for cat in imp.categories:
        row = {"category": cat, "unit": imp.ef.loc[cat, "unit"],
               "fuel_cell_fabrication_share_pct": 100 * fc_ref["fab"][cat] / fc_ref["tot"][cat],
               "electrolyser_fabrication_share_pct": 100 * we_ref["fab"][cat] / we_ref["tot"][cat],
               "chain_no_ageing_per_km": chain_ref["total"][cat]}
        for name in cases:
            row[f"fuel_cell_rise_pct_{name}"] = pct(fc_res[name]["tot"][cat], fc_ref["tot"][cat])
            row[f"electrolyser_rise_pct_{name}"] = pct(we_res[name]["tot"][cat], we_ref["tot"][cat])
            row[f"chain_rise_pct_{name}"] = pct(ch_res[name]["total"][cat], chain_ref["total"][cat])
        cat_rows.append(row)
    # tank alone, per km: fabrication (one tank per certification period) and hydrogen lost by permeation,
    # valued as delivered hydrogen at the reference state
    t = np.linspace(0.0, ch.L, 15001)
    n_tanks = float(ch.tank.n_tanks(ch.L))
    tank_fab = 1e3 * n_tanks * imp.tank[CLIMATE] / ch.km_total
    tank_rows = []
    for name, perm in [("no_ageing", (cases[next(iter(cases))]["tank_permeation_mL_h_L"][0],) * 2)] + \
            [(n_, tuple(c_["tank_permeation_mL_h_L"])) for n_, c_ in cases.items()]:
        lost = ch.tank.loss_per_km(t, perm, ch.km_year).mean()
        tank_rows.append({"case": name, "permeation_P0_mL_h_L": perm[0], "permeation_P15_mL_h_L": perm[1], "tanks": n_tanks,
                          "h2_lost_mg_per_km": 1e6 * lost, "fabrication_g_per_km": tank_fab,
                          "h2_lost_g_per_km": 1e3 * lost * ch.ikg_ref[CLIMATE], "total_g_per_km": tank_fab + 1e3 * lost * ch.ikg_ref[CLIMATE]})
    tank_df = pd.DataFrame(tank_rows)
    tank_df["rise_pct"] = 100 * (tank_df.total_g_per_km / tank_df.total_g_per_km.iloc[0] - 1)
    return {"life": pd.DataFrame(life), "tank": tank_df, "fuel_cell": pd.DataFrame(fc_rows), "electrolyser": pd.DataFrame(we_rows),
            "chain": pd.DataFrame(chain_rows), "categories": pd.DataFrame(cat_rows)}
