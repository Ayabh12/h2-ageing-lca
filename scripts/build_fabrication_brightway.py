"""Recompute the fabrication impacts from the foreground inventories (needs ecoinvent).

ecoinvent is licensed, so this repository only ships the characterised results
(data/impacts/fabrication_per_unit.csv). If you hold an ecoinvent 3.11 cut-off licence,
this script rebuilds the two stacks and the tank from
data/inventories/*.csv in your own Brightway project, computes the 16 EF 3.1 categories
and writes a new fabrication file. Change any amount in the CSV files first to test your
own inventory.

Two ways to use it:

* Without an ecoinvent licence: nothing to do. The impacts in data/impacts are enough to run the
  model and obtain every result; ``--check`` prints the inventories.
* With an ecoinvent licence: the script can download and import ecoinvent 3.11 cut-off into a
  Brightway project with your ecoinvent login, then recompute the fabrication impacts.

Requirements for the second way: Brightway 2.5 (``pip install -r requirements-brightway.txt``)
and an ecoinvent account with a licence for version 3.11. Your login is read from the
environment variables EI_USERNAME and EI_PASSWORD, or asked when the script starts; it is
never written to a file.

    python scripts/build_fabrication_brightway.py --check          # print the inventories, no ecoinvent
    python scripts/build_fabrication_brightway.py --project h2ageing --import-ecoinvent
    python scripts/build_fabrication_brightway.py --project h2ageing \
        --out data/impacts/fabrication_per_unit_custom.csv          # project already contains ecoinvent

Each inventory (data/inventories/*.csv) gives, for one unit of the component, every input
with its amount, the part of the component it belongs to, and the ecoinvent activity it is
linked to (by its code when given, otherwise by name, location and reference product).
Set ``included`` to ``no`` to leave a row out.

Then point ``fabrication.file`` of your configuration to the new file.

Check: with ecoinvent 3.11 cut-off and the default inventories, this script gives the
same climate change impacts as the shipped file, computed with Activity Browser
(3 698.3, 39 509.4 and 2 332.0 kg CO2-eq). Run it once on the default inventories to
check your installation before using your own values.
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
    """EF v3.1 method of one category.

    The category is matched on the start of its own name (the element after "EF v3.1"),
    not anywhere in the method name: "land use" must not pick
    "climate change: land use and land use change". When several names start the same way
    (for example "climate change" and "climate change: biogenic"), the shortest is the
    category itself.
    """
    target = EF31[key]
    cands = []
    for m in bd.methods:
        parts = [str(x) for x in m]
        if "EF v3.1" not in parts:
            continue
        i = parts.index("EF v3.1")
        if i + 1 < len(parts) and parts[i + 1].lower().startswith(target):
            cands.append((len(parts[i + 1]), m))
    if not cands:
        raise LookupError(f"no EF v3.1 method found for {key}")
    return sorted(cands)[0][1]


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
    db = ecoinvent_db(bd, row["database"])
    if row["ecoinvent_code"]:
        return bd.get_activity((db, row["ecoinvent_code"]))
    hits = [a for a in bd.Database(db) if a["name"] == row["ecoinvent_activity"]
            and a["location"] == row["location"] and a.get("reference product") == row["reference_product"]]
    if len(hits) != 1:
        raise LookupError(f"{len(hits)} matches for {row['ecoinvent_activity']} / {row['location']} / {row['reference_product']}")
    return hits[0]


def ecoinvent_db(bd, name):
    """Name of the ecoinvent 3.11 cut-off database in the project (the inventories say ecoinvent-3.11-cutoff)."""
    if name in bd.databases:
        return name
    cands = [d for d in bd.databases if "3.11" in d and "cut" in d.lower() and "biosphere" not in d]
    if len(cands) != 1:
        raise LookupError(f"database {name!r} not found; databases in the project: {list(bd.databases)}")
    return cands[0]


def import_ecoinvent(bd):
    """Download and import ecoinvent 3.11 cut-off (with its biosphere and LCIA methods) with your login."""
    import getpass
    import os

    import bw2io as bi

    if any("3.11" in d and "cut" in d.lower() for d in bd.databases):
        print("ecoinvent 3.11 cut-off is already in the project")
        return
    user = os.environ.get("EI_USERNAME") or input("ecoinvent username: ")
    password = os.environ.get("EI_PASSWORD") or getpass.getpass("ecoinvent password: ")
    print("downloading and importing ecoinvent 3.11 cut-off (this can take several minutes)...")
    bi.import_ecoinvent_release(version="3.11", system_model="cutoff", username=user, password=password)


def read_inventory(name):
    inv = pd.read_csv(ROOT / "data/inventories" / f"{name}.csv", dtype=str).fillna("")
    inv["amount"] = inv["amount"].astype(float)
    return inv[inv["included"] == "yes"]


def build(bd, inv: pd.DataFrame, name: str):
    """One foreground activity (one unit of the component) with every inventory row as an input."""
    db_name = f"h2ageing_{name}"
    if db_name in bd.databases:
        # remove the activities and exchanges of an earlier run (also an interrupted one), then the database
        try:
            bd.Database(db_name).delete(warn=False)
        except TypeError:
            bd.Database(db_name).delete()
        if db_name in bd.databases:
            del bd.databases[db_name]
    fg = bd.Database(db_name)
    fg.register()
    act = fg.new_activity(code=name, name=name, unit="unit", location="GLO", type="process")
    act.save()
    act.new_exchange(input=act, amount=1, type="production").save()
    for _, r in inv.iterrows():
        kind = "biosphere" if r["flow_type"] == "resource" else "technosphere"
        act.new_exchange(input=find(bd, r), amount=float(r["amount"]), type=kind).save()
    # the activity must hold exactly one production of 1 unit and one input per inventory row
    n_inputs = len(list(act.technosphere())) + len(list(act.biosphere()))
    production = sum(e["amount"] for e in act.production())
    if n_inputs != len(inv) or abs(production - 1) > 1e-9:
        raise RuntimeError(f"{name}: {n_inputs} inputs for {len(inv)} inventory rows, production {production}; "
                           f"delete the database {db_name} from the project and run again")
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
    ap.add_argument("--import-ecoinvent", action="store_true",
                    help="download and import ecoinvent 3.11 cut-off with your ecoinvent login (licence needed)")
    a = ap.parse_args()
    if a.check:
        check()
        return
    if not a.project:
        ap.error("--project is required (or use --check)")
    import warnings
    # Brightway notices that do not change the result (solver speed, default activity type);
    # install pypardiso (requirements-brightway.txt) for the fast solver
    warnings.filterwarnings("ignore", message="No fast sparse solver found")
    warnings.filterwarnings("ignore", message=".*has no `type` specified.*")
    import bw2calc as bc
    import bw2data as bd

    bd.projects.set_current(a.project)
    if a.import_ecoinvent:
        import_ecoinvent(bd)
    methods = {key: pick_method(bd, key) for key in EF31}
    print("EF 3.1 methods used:")
    for key, m in methods.items():
        print(f"  {key:32s} {' | '.join(m)}")
    res = {}
    for name in COMPONENTS:
        act = build(bd, read_inventory(name), name)
        res[name] = {}
        # one inventory calculation per component, then the 16 methods on the same inventory
        lca = bc.LCA({act: 1}, methods["climate_change"])
        lca.lci()
        for key in EF31:
            if hasattr(lca, "switch_method"):
                lca.switch_method(methods[key])
                lca.lcia()
            else:  # older bw2calc: one calculation per method
                lca = bc.LCA({act: 1}, methods[key])
                lca.lci()
                lca.lcia()
            res[name][key] = lca.score
        print(name, "climate change:", round(res[name]["climate_change"], 1))
    out = pd.DataFrame(res)
    out.index.name = "category"
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    out.reset_index().to_csv(a.out, index=False, float_format="%.10g")
    print("written to", a.out)


if __name__ == "__main__":
    main()
