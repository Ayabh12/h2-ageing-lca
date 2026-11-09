"""The default configuration must give the reference results.

Run with ``pytest`` or simply ``python tests/test_reference_results.py``.
Tolerance: 0.05 % on absolute values, 0.05 point on percentage rises.
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from h2ageing import load_config, run, with_values  # noqa: E402

REF = json.load(open(ROOT / "tests" / "reference_results.json", encoding="utf-8"))
CFG = load_config()
_RES = {}


def res():
    if "default" not in _RES:
        _RES["default"] = run(CFG)
    return _RES["default"]


def close_rel(a, b, tol=5e-4):
    assert math.isclose(a, b, rel_tol=tol), f"{a} != {b}"


def close_pt(a, b, tol=0.05):
    assert abs(a - b) <= tol, f"{a} != {b} (points)"


def row(df, case):
    return df.set_index("case").loc[case]


def test_end_of_life_and_stacks():
    life = res()["life"].set_index("case")
    for case, r in REF["fuel_cell"].items():
        close_rel(life.loc[case, "fuel_cell_end_of_life_h"], r["eol_h"], 1e-3)
        assert life.loc[case, "fuel_cell_stacks"] == r["stacks"]


def test_fuel_cell_alone():
    df = res()["fuel_cell"]
    close_rel(row(df, "no_ageing")["total_g_per_km"], REF["fuel_cell_no_ageing_g_per_km"])
    for case, r in REF["fuel_cell"].items():
        close_rel(row(df, case)["total_g_per_km"], r["total_g_per_km"])
        close_pt(row(df, case)["rise_pct"], r["rise_pct"])


def test_tank_alone():
    df = res()["tank"]
    for case, r in REF["tank"].items():
        close_rel(row(df, case)["total_g_per_km"], r["total_g_per_km"])
        close_pt(row(df, case)["rise_pct"], r["rise_pct"])


def test_electrolyser_alone():
    df = res()["electrolyser"]
    close_rel(row(df, "no_ageing")["total_kg_per_kg"], REF["electrolyser_no_ageing_kg_per_kg"])
    for case, r in REF["electrolyser"].items():
        close_rel(row(df, case)["total_kg_per_kg"], r["total_kg_per_kg"])
        close_pt(row(df, case)["rise_pct"], r["rise_pct"])


def test_chain():
    df = res()["chain"]
    close_rel(row(df, "no_ageing")["total_g_per_km"], REF["chain_no_ageing_g_per_km"])
    close_rel(row(df, "no_ageing")["single_score_uPt_per_km"], REF["chain_no_ageing_score_uPt"])
    for case, r in REF["chain"].items():
        close_rel(row(df, case)["total_g_per_km"], r["total_g_per_km"])
        close_pt(row(df, case)["rise_pct"], r["rise_pct"])
        close_pt(row(df, case)["single_score_rise_pct"], r["score_rise_pct"])


def test_categories_central():
    df = res()["categories"].set_index("category")
    for cat, r in REF["categories_central"].items():
        close_pt(df.loc[cat, "fuel_cell_rise_pct_central"], r["fuel_cell_rise_pct"])
        close_pt(df.loc[cat, "electrolyser_rise_pct_central"], r["electrolyser_rise_pct"])
        close_pt(df.loc[cat, "chain_rise_pct_central"], r["chain_rise_pct"])


def test_electricity_sources():
    for source, r in REF["electricity"].items():
        out = run(with_values(CFG, **{"usage.electricity_electrolyser": source}))
        ch = out["chain"].set_index("case")
        close_rel(ch.loc["no_ageing", "total_g_per_km"], r["chain_no_ageing_g_per_km"])
        for case, v in r["chain_rise_pct"].items():
            close_pt(ch.loc[case, "rise_pct"], v)
        close_pt(out["electrolyser"].set_index("case").loc["central", "rise_pct"], r["electrolyser_rise_pct_central"])


def test_electrolyser_hours():
    for r in REF["electrolyser_hours"].values():
        out = run(with_values(CFG, **{"usage.electrolyser_hours_per_year": r["hours_per_year"]}))
        ch = out["chain"].set_index("case")
        life = out["life"].set_index("case")
        for case, v in r["chain_rise_pct"].items():
            close_pt(ch.loc[case, "rise_pct"], v)
            assert life.loc[case, "electrolyser_stacks"] == r["electrolyser_stacks"][case]


if __name__ == "__main__":
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for t in tests:
        t()
        print("ok ", t.__name__)
    print(f"{len(tests)} tests passed")
