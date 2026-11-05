"""Type IV tank: hydrogen permeation, linear in age from P0 to P15 (mL/h/L, 55 C, full tank)."""
from __future__ import annotations

import numpy as np


class Tank:
    def __init__(self, cfg: dict):
        c = cfg["tank"]
        self.V = c["volume_L"]
        self.rho = c["h2_density_kg_per_NmL"]
        self.life = c["certification_years"]

    def permeation(self, t_years, p):
        p0, p1 = p
        t = np.asarray(t_years, float)
        tt = np.mod(t, self.life)
        tt = np.where((tt == 0) & (t > 0), self.life, tt)   # end of certification included
        return p0 + (p1 - p0) * tt / self.life

    def loss_per_km(self, t_years, p, km_per_year):
        """Hydrogen lost by permeation, kg per km driven."""
        return self.permeation(t_years, p) * self.V * self.rho * 8760.0 / km_per_year

    def n_tanks(self, years):
        return np.ceil(years / self.life - 1e-9)
