"""Impact data (EF 3.1, 16 categories) and single score.

No ecoinvent inventory is distributed. The files in ``data/impacts`` contain
characterised results only: the impact of one kWh of electricity, of one kg of
deionised water and of one unit of each manufactured component.
"""
from __future__ import annotations

import pandas as pd

from .config import resolve

CLIMATE = "climate_change"


class ImpactData:
    def __init__(self, cfg: dict):
        imp = cfg["impacts"]
        self.ef = pd.read_csv(resolve(imp["ef31_file"])).set_index("category")
        self.categories = list(self.ef.index)
        self.electricity = pd.read_csv(resolve(imp["electricity_file"])).set_index("category").reindex(self.categories)
        water = pd.read_csv(resolve(imp["water_file"])).set_index("category").reindex(self.categories)
        self.water_per_kg = water.iloc[:, 0]
        fab = pd.read_csv(resolve(cfg["fabrication"]["file"])).set_index("category").reindex(self.categories)
        f = cfg["fabrication"]
        self.fuel_cell_stack = fab[f["fuel_cell_stack"]]
        self.electrolyser_stack = fab[f["electrolyser_stack"]]
        self.tank = fab[f["tank"]]
        u = cfg["usage"]
        self.kwh_electrolyser = self.electricity_source(u["electricity_electrolyser"])
        self.kwh_compression = self.electricity_source(u["electricity_compression"])
        self.water = u["water_kg_per_kg_h2"] * self.water_per_kg            # per kg H2 produced
        self.compression = u["compression_kWh_per_kg"] * self.kwh_compression  # per kg H2 delivered

    def electricity_source(self, name: str) -> pd.Series:
        if name not in self.electricity.columns:
            raise KeyError(f"electricity source {name!r} not in {list(self.electricity.columns)}")
        return self.electricity[name]

    def h2_produced(self, sec_kwh_per_kg: float) -> pd.Series:
        """Use-phase impact of 1 kg of hydrogen produced (electricity + water)."""
        return sec_kwh_per_kg * self.kwh_electrolyser + self.water

    def h2_delivered(self, sec_kwh_per_kg: float) -> pd.Series:
        """Use-phase impact of 1 kg of hydrogen produced and compressed."""
        return self.h2_produced(sec_kwh_per_kg) + self.compression

    def single_score(self, s: pd.Series) -> float:
        """EF 3.1 single score (Pt): sum of normalised and weighted results."""
        s = s.reindex(self.categories)
        return float((s / self.ef["normalisation_factor_per_person"] * self.ef["weighting_factor_pct"] / 100).sum())
