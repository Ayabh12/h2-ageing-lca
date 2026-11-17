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


def test_fuel_cell_lifetime_6000h():
    """Central fuel cell at 6 000 h instead of 4 100 h: one stack instead of two (threshold 5 554 h)."""
    out = run(with_values(CFG, **{"cases.central.fuel_cell.hours_to_end_of_life": 6000}))
    assert out["life"].set_index("case").loc["central", "fuel_cell_stacks"] == 1
    ch = out["chain"].set_index("case")
    close_rel(ch.loc["central", "total_g_per_km"], 78.882177)
    close_pt(ch.loc["central", "rise_pct"], 6.42)


def test_own_fabrication_file():
    """A fabrication file of your own (here: fuel cell stack 30 % lower in climate change) is used by the model."""
    import tempfile

    import pandas as pd

    fab = pd.read_csv(ROOT / "data/impacts/fabrication_per_unit.csv").set_index("category")
    fab.loc["climate_change", "fuel_cell_stack_128kW"] *= 0.7
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "my_fabrication.csv"
        fab.to_csv(path)
        out = run(with_values(CFG, **{"fabrication.file": str(path)}))
    ch = out["chain"].set_index("case")
    close_rel(ch.loc["no_ageing", "total_g_per_km"], 68.575087)
    close_rel(ch.loc["central", "total_g_per_km"], 86.057652)
    close_pt(ch.loc["central", "rise_pct"], 25.49)


def test_semi_empirical_constant():
    """Pessimistic fuel cell: high-current voltage loss 27 mV instead of 45 mV (value of another cell)."""
    cfg = load_config()
    cfg["cases"]["pessimistic"]["fuel_cell"]["voltage_loss_at_1p8_A_cm2_1000h_V"] = 0.027
    out = run(cfg)
    life = out["life"].set_index("case").loc["pessimistic"]
    close_rel(life["fuel_cell_end_of_life_h"], 5652.435)
    assert life["fuel_cell_stacks"] == 1
    close_pt(out["chain"].set_index("case").loc["pessimistic", "rise_pct"], 12.82)


def test_crossover_law_exponential():
    """Exponential crossover law instead of linear: same end of life, slightly higher over-consumption."""
    cfg = load_config()
    cfg["fuel_cell"]["crossover_law"] = "exponential"
    out = run(cfg)
    close_rel(out["life"].set_index("case").loc["pessimistic", "fuel_cell_end_of_life_h"], 2894.516)
    close_pt(out["chain"].set_index("case").loc["pessimistic", "rise_pct"], 36.93)


def test_linear_model_same_end_of_life():
    """Pessimistic fuel cell with the linear model set to the same end of life: only the shape changes."""
    cfg = load_config()
    cfg["cases"]["pessimistic"]["fuel_cell"] = {"model": "linear", "hours_to_end_of_life": 2895}
    out = run(cfg)
    assert out["life"].set_index("case").loc["pessimistic", "fuel_cell_stacks"] == 2
    close_pt(out["chain"].set_index("case").loc["pessimistic", "rise_pct"], 33.74)


if __name__ == "__main__":
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for t in tests:
        t()
        print("ok ", t.__name__)
    print(f"{len(tests)} tests passed")
