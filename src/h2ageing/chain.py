"""Life cycle assessment of each converter alone and of the whole chain.

Functional units
  * fuel cell alone:    1 km driven   (hydrogen consumed x impact of 1 kg of reference hydrogen + stacks / km)
  * electrolyser alone: 1 kg H2 produced (mean electricity x impact of 1 kWh + water + stacks / kg)
  * whole chain:        1 km driven   (electrolyser, compression, tank and fuel cell ageing together)

Each stack restarts from new when it is replaced. Means over the horizon use the
trapezoidal rule. Stack counts are integer by default: n = ceil(L / t_EoL).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .impacts import ImpactData
from .pemfc import FuelCell
from .pemwe import Electrolyser
from .tank import Tank


def _trapz(y, x, axis=-1):
    f = getattr(np, "trapezoid", None) or np.trapz
    return f(y, x, axis=axis)


class Chain:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.imp = ImpactData(cfg)
        self.fc = FuelCell(cfg)
        self.we = Electrolyser(cfg)
        self.tank = Tank(cfg)
        h = cfg["horizon"]
        self.L = float(h["years"])
        self.km_total = float(h["vehicle_km_total"])
        self.km_year = self.km_total / self.L
        self.fc_hours_year = self.km_year / self.fc.distance_km * self.fc.duration_h
        self.L_fc_h = self.L * self.fc_hours_year
        self.we_hours_year = float(cfg["usage"]["electrolyser_hours_per_year"])
        self.L_we_h = self.L * self.we_hours_year
        self.integer = cfg["usage"]["stack_counting"] == "integer"
        self.s_we = cfg["electrolyser"]["stack_inventory_scale"]
        self.cats = self.imp.categories
        self.m0 = self.fc.h2_per_km_measured                     # kg H2 / km, measured trip
        self.ikg_ref = self.imp.h2_delivered(self.we.SEC0)       # 1 kg of reference hydrogen, compressed

    def n_stacks(self, horizon, life):
        """Integer: n = ceil(L / t_EoL). Prorata: n = L / t_EoL, at least one stack (the first one is always built)."""
        return np.ceil(horizon / life - 1e-9) if self.integer else max(1.0, horizon / life)

    # ------------------------------------------------------------------ fuel cell alone (per km)
    def fuel_cell_reference(self):
        use = self.m0 * self.ikg_ref
        fab = self.imp.fuel_cell_stack / self.km_total
        return {"use": use, "fab": fab, "tot": use + fab, "n": 1}

    def fuel_cell_alone(self, p):
        te, a, mtab = self.fc.life_table(p)
        ratio = mtab / mtab[0]
        g = np.linspace(0, self.L_fc_h, 1601)
        hm = float(_trapz(np.interp(np.mod(g, te), a, ratio), g) / self.L_fc_h)
        n = self.n_stacks(self.L_fc_h, te)
        use = self.m0 * hm * self.ikg_ref
        fab = n * self.imp.fuel_cell_stack / self.km_total
        return {"use": use, "fab": fab, "tot": use + fab, "n": n, "eol_h": te, "h2_mean_rise_pct": 100 * (hm - 1)}

    # ------------------------------------------------------------------ electrolyser alone (per kg)
    def electrolyser_reference(self):
        use = self.imp.h2_produced(self.we.SEC0)
        h2 = self.L_we_h / self.we.profile_h * self.we.H20
        fab = self.s_we * self.imp.electrolyser_stack / h2
        return {"use": use, "fab": fab, "tot": use + fab, "n": 1}

    def electrolyser_alone(self, p):
        te = self.we.end_of_life(p)
        g = np.linspace(0, self.L_we_h, 20001)
        q = self.we.state(np.mod(g, te), p)
        e_tot = _trapz(np.asarray(q["Energy"], float), g) / self.we.profile_h
        h_tot = _trapz(np.asarray(q["H2"], float), g) / self.we.profile_h
        sec = e_tot / h_tot
        n = self.n_stacks(self.L_we_h, te)
        use = self.imp.h2_produced(sec)
        fab = self.s_we * n * self.imp.electrolyser_stack / h_tot
        return {"use": use, "fab": fab, "tot": use + fab, "n": n, "eol_h": te, "sec_mean_rise_pct": 100 * (sec / self.we.SEC0 - 1)}

    # ------------------------------------------------------------------ whole chain (per km)
    def chain_reference(self, permeation=(6.0, 6.0)):
        t = np.linspace(0, self.L, int(self.L * 80) + 1)
        mp = self.tank.loss_per_km(t, (permeation[0], permeation[0]), self.km_year)
        mt = self.m0 + mp
        mbar = _trapz(mt, t) / self.L
        h2_ref = self.we.H20 / self.we.profile_h * self.we_hours_year * self.L
        parts = {"electricity_and_water": mbar * self.imp.h2_produced(self.we.SEC0),
                 "compression": mbar * self.imp.compression,
                 "fuel_cell_stacks": self.imp.fuel_cell_stack / self.km_total,
                 "tank": self.tank.n_tanks(self.L) * self.imp.tank / self.km_total,
                 "electrolyser_stacks": mbar * self.s_we * self.imp.electrolyser_stack / h2_ref}
        return {"parts": parts, "total": sum(parts.values())}

    def chain(self, pf, pw, permeation, npa=80):
        te_fc, a, mtab = self.fc.life_table(pf)
        te_we, b, sectab, _ = self.we.life_table(pw)
        t = np.linspace(0, self.L, int(self.L * npa) + 1)
        m = np.interp(np.mod(t * self.fc_hours_year, te_fc), a, mtab)
        mp = self.tank.loss_per_km(t, permeation, self.km_year)
        mt = m + mp
        sec = np.interp(np.mod(t * self.we_hours_year, te_we), b, sectab)
        kwh = self.imp.kwh_electrolyser.to_numpy()
        prod = sec[:, None] * kwh + self.imp.water.to_numpy()
        elec_water = _trapz(mt[:, None] * prod, t, axis=0) / self.L
        mbar = _trapz(mt, t) / self.L
        km_stack = te_fc / self.fc_hours_year * self.km_year
        nfc = self.n_stacks(self.km_total, km_stack)
        nwe = self.n_stacks(self.L_we_h, te_we)
        h2_hor = self.we.h2_over(pw, self.L_we_h)
        parts = {"electricity_and_water": pd.Series(elec_water, index=self.cats),
                 "compression": mbar * self.imp.compression,
                 "fuel_cell_stacks": nfc * self.imp.fuel_cell_stack / self.km_total,
                 "tank": self.tank.n_tanks(self.L) * self.imp.tank / self.km_total,
                 "electrolyser_stacks": mbar * self.s_we * nwe * self.imp.electrolyser_stack / h2_hor}
        return {"parts": parts, "total": sum(parts.values()), "n_fc": nfc, "n_we": nwe,
                "h2_produced_g_per_km": 1e3 * mbar}
