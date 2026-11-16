"""Recompute the fabrication impacts from the foreground inventories (needs ecoinvent).

ecoinvent is licensed, so this repository only ships the characterised results
(data/impacts/fabrication_per_unit.csv). If you hold an ecoinvent 3.11 cut-off licence,
this script rebuilds the two stacks and the tank from
data/inventories/*.csv in your own Brightway project, computes the 16 EF 3.1 categories
and writes a new fabrication file. Change any amount in the CSV files first to test your
own inventory.

Requirements: bw2data and bw2calc (Brightway 2.5), a project with the databases
"ecoinvent-3.11-cutoff" and its biosphere, and the EF v3.1 methods imported with ecoinvent.

    python scripts/build_fabrication_brightway.py --check          # print the inventories, no ecoinvent
    python scripts/build_fabrication_brightway.py --project my_project \
        --out data/impacts/fabrication_per_unit_custom.csv

Each inventory (data/inventories/*.csv) gives, for one unit of the component, every input
with its amount, the part of the component it belongs to, and the ecoinvent activity it is
linked to (by its code when given, otherwise by name, location and reference product).
Set ``included`` to ``no`` to leave a row out.

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


def find(bd, row):
    """ecoinvent activity or biosphere flow of one inventory row."""
    if row["flow_type"] == "resource":
        bio = [d for d in bd.databases if "biosphere" in d][0]
        hits = [a for a in bd.Database(bio) if a["name"] == row["ecoinvent_activity"]]
        cat = tuple(row["biosphere_category"].split("::")) if row["biosphere_category"] else None
        hits = [a for a in hits if cat is None or tuple(a.get("categories", ())) == cat] or hits
        if not hits:
            raise LookupError(f"biosphere flow not found: {row['ecoinvent_activity']}")
        return hits[0]
    if row["ecoinvent_code"]:
        return bd.get_activity((row["database"], row["ecoinvent_code"]))
    hits = [a for a in bd.Database(row["database"]) if a["name"] == row["ecoinvent_activity"]
            and a["location"] == row["location"] and a.get("reference product") == row["reference_product"]]
    if len(hits) != 1:
        raise LookupError(f"{len(hits)} matches for {row['ecoinvent_activity']} / {row['location']} / {row['reference_product']}")
    return hits[0]


def read_inventory(name):
    inv = pd.read_csv(ROOT / "data/inventories" / f"{name}.csv", dtype=str).fillna("")
    inv["amount"] = inv["amount"].astype(float)
    return inv[inv["included"] == "yes"]


def build(bd, inv: pd.DataFrame, name: str):
    """One foreground activity (one unit of the component) with every inventory row as an input."""
    db_name = f"h2ageing_{name}"
    if db_name in bd.databases:
        del bd.databases[db_name]
    fg = bd.Database(db_name)
    fg.register()
    act = fg.new_activity(code=name, name=name, unit="unit", location="GLO")
    act.save()
    act.new_exchange(input=act, amount=1, type="production").save()
    for _, r in inv.iterrows():
        kind = "biosphere" if r["flow_type"] == "resource" else "technosphere"
        act.new_exchange(input=find(bd, r), amount=float(r["amount"]), type=kind).save()
    return act


COMPONENTS = ["fuel_cell_stack_128kW", "electrolyser_stack_1p25MW", "tank_type_IV"]


def check():
    """Print each inventory, without ecoinvent."""
    for name in COMPONENTS:
        inv = read_inventory(name)
        print(f"\n{name}")
        print(inv[["part", "input", "amount", "unit", "flow_type"]].to_string(index=False))
        kg = inv[(inv.unit == "kilogram") & (inv.flow_type == "material")].amount.sum()
        kwh = inv[inv.unit == "kilowatt hour"].amount.sum()
        print(f"  materials: {kg:.2f} kg   energy: {kwh:.2f} kWh")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", help="Brightway project with ecoinvent 3.11 cut-off")
    ap.add_argument("--out", default=str(ROOT / "data/impacts/fabrication_per_unit_custom.csv"))
    ap.add_argument("--check", action="store_true", help="only print the inventories (no ecoinvent needed)")
    a = ap.parse_args()
    if a.check:
        check()
        return
    if not a.project:
        ap.error("--project is required (or use --check)")
    import bw2calc as bc
    import bw2data as bd

    bd.projects.set_current(a.project)
    res = {}
    for name in COMPONENTS:
        act = build(bd, read_inventory(name), name)
        res[name] = {}
        for key in EF31:
            lca = bc.LCA({act: 1}, pick_method(bd, key))
            lca.lci()
            lca.lcia()
            res[name][key] = lca.score
        print(name, "climate change:", round(res[name]["climate_change"], 1))
    out = pd.DataFrame(res)
    out.index.name = "category"
    out.reset_index().to_csv(a.out, index=False, float_format="%.10g")
    print("written to", a.out)


if __name__ == "__main__":
    main()
