"""Recompute the fabrication impacts from the foreground inventories (needs ecoinvent).

ecoinvent is licensed, so this repository only ships the characterised results
(data/impacts/fabrication_per_unit.csv). If you hold an ecoinvent 3.11 cut-off licence,
this script rebuilds the two stacks and the tank from
data/inventories/*.csv in your own Brightway project, computes the 16 EF 3.1 categories
and writes a new fabrication file. Change any amount in the CSV files first to test your
own inventory.

Requirements: bw2data and bw2calc (Brightway 2.5), a project with the databases
"ecoinvent-3.11-cutoff" and its biosphere, and the EF v3.1 methods imported with ecoinvent.

    python scripts/build_fabrication_brightway.py --project my_project \
        --out data/impacts/fabrication_per_unit_custom.csv

Then point ``fabrication.file`` of your configuration to the new file.

Note: this script was written for this repository and has not been run by its author
(no ecoinvent licence on the machine that built the repository). The impacts shipped in
data/impacts were computed with Activity Browser on the same inventories. Check the
climate change result of the default inventories against the shipped file (3 698, 39 509
and 2 332 kg CO2-eq) before using your own values.
"""
import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# substrings that identify each EF 3.1 category in the Brightway method names
EF31 = {"acidification": "acidification", "climate_change": "climate change", "ecotoxicity_freshwater": "ecotoxicity: freshwater",
        "particulate_matter": "particulate matter", "eutrophication_freshwater": "eutrophication: freshwater",
        "eutrophication_marine": "eutrophication: marine", "eutrophication_terrestrial": "eutrophication: terrestrial",
        "human_toxicity_cancer": "human toxicity: carcinogenic", "ozone_depletion": "ozone depletion",
        "resource_use_fossils": "energy resources", "resource_use_minerals_metals": "material resources",
        "water_use": "water use", "land_use": "land use", "ionising_radiation": "ionising radiation",
        "photochemical_ozone_formation": "photochemical oxidant", "human_toxicity_non_cancer": "human toxicity: non-carcinogenic"}


def pick_method(bd, key):
    cands = [m for m in bd.methods if "EF v3.1" in " ".join(m) and EF31[key] in " ".join(m).lower()
             and "inorganics" not in " ".join(m) and "organics" not in " ".join(m).replace("inorganics", "")
             and "no LT" not in " ".join(m)]
    if not cands:
        raise LookupError(f"no EF v3.1 method found for {key}")
    return sorted(cands, key=len)[0]


def find(bd, db, row):
    if row["database"] == "biosphere3" or row["type"] == "biosphere":
        bio = [d for d in bd.databases if "biosphere" in d][0]
        hits = [a for a in bd.Database(bio) if a["name"] == row["exchange_name"]]
        cat = tuple(str(row.get("categories", "")).split("::")) if row.get("categories") else None
        hits = [a for a in hits if cat is None or tuple(a.get("categories", ())) == cat] or hits
        return hits[0]
    hits = [a for a in bd.Database(db) if a["name"] == row["exchange_name"] and a["location"] == row["location"]
            and a.get("reference product") == row["reference_product"]]
    if len(hits) != 1:
        raise LookupError(f"{len(hits)} matches for {row['exchange_name']} / {row['location']} / {row['reference_product']}")
    return hits[0]


def build(bd, inv: pd.DataFrame, top: str, db_name: str, eco: str):
    """Create a foreground database from an inventory table, return the top activity."""
    if db_name in bd.databases:
        del bd.databases[db_name]
    fg = bd.Database(db_name)
    fg.register()
    acts = {}
    for name in inv.foreground_activity.unique():
        acts[name] = fg.new_activity(code=name, name=name, unit="unit", location="GLO")
        acts[name].save()
        acts[name].new_exchange(input=acts[name], amount=1, type="production").save()
    for _, r in inv.iterrows():
        if r["database"] == eco or r["type"] == "biosphere":
            inp = find(bd, eco, r)
        else:
            inp = acts[r["exchange_name"]]
        acts[r["foreground_activity"]].new_exchange(input=inp, amount=float(r["amount"]), type=r["type"]).save()
    return acts[top]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--ecoinvent", default="ecoinvent-3.11-cutoff")
    ap.add_argument("--out", default=str(ROOT / "data/impacts/fabrication_per_unit_custom.csv"))
    a = ap.parse_args()
    import bw2calc as bc
    import bw2data as bd

    bd.projects.set_current(a.project)
    items = {"fuel_cell_stack_128kW": ("fuel_cell_stack_128kW.csv", "fabrication"),
             "electrolyser_stack_1p25MW": ("electrolyser_stack_1p25MW.csv", "peml")}
    res = {}
    for col, (f, top) in items.items():
        inv = pd.read_csv(ROOT / "data/inventories" / f).fillna("")
        act = build(bd, inv, top, f"h2ageing_{col}", a.ecoinvent)
        res[col] = {}
        for key in EF31:
            lca = bc.LCA({act: 1}, pick_method(bd, key))
            lca.lci()
            lca.lcia()
            res[col][key] = lca.score
        print(col, "climate change:", round(res[col]["climate_change"], 1))
    # tank: flows identified by their ecoinvent code; rows marked "no" are left out.
    tank = pd.read_csv(ROOT / "data/inventories/tank_type_IV.csv")
    tank = tank[tank["included_in_shipped_impact"] == "yes"]
    demand = {}
    for _, r in tank.iterrows():
        act = bd.get_activity((r["database"], r["ecoinvent_code"]))
        demand[act] = demand.get(act, 0) + float(r["amount"])
    res["tank_type_IV"] = {}
    for key in EF31:
        lca = bc.LCA(demand, pick_method(bd, key))
        lca.lci()
        lca.lcia()
        res["tank_type_IV"][key] = lca.score
    print("tank_type_IV climate change:", round(res["tank_type_IV"]["climate_change"], 1))
    out = pd.DataFrame(res)
    out.index.name = "category"
    out.reset_index().to_csv(a.out, index=False, float_format="%.10g")
    print("written to", a.out)


if __name__ == "__main__":
    main()
