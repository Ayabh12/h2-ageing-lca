"""PEM electrolyser model (Nel MC250, measured wind profile) and its ageing.

The new-state model (polarisation fitted on the measured profile) is read from
``data/parameters/pemwe_fit.json`` (written by ``scripts/fit_pemwe.py``).

Ageing, mechanistic model (pessimistic case), constants from Padgett et al. 2025 and
Chandesris et al. 2015:
  * anode activity f_A(t) = f_min + (1 - f_min) exp(-t/tau), converted to a voltage
    rise b/ln(10) * ln(1/f_A) with the measured Tafel slope b;
  * resistance R(t) = R0 + dR/dt t, with dR/dt = (HFR + catalyst-layer drift) / j_test;
  * Faraday efficiency from the membrane thinning, e/e0 = 1 - 0.5 t/t50.

Ageing, linear model (optimistic and central cases): constant drift mu (V/h per cell).

Energy over the profile is updated to first order with the weights W0 and Wj of
the fit, so the specific consumption SEC(t) = E(t) / H2(t) is cheap to evaluate.
End of life: +10 % voltage at the mean current density of the profile (Brent's method).
"""
from __future__ import annotations

import json

import numpy as np
from scipy.optimize import brentq

from .config import resolve


class Electrolyser:
    def __init__(self, cfg: dict):
        c = cfg["electrolyser"]
        self.cfg = c
        P = json.load(open(resolve(c["params_file"]), encoding="utf-8"))
        self.R0, self.etaF0 = P["R0"], P["etaF0"]
        self.E0, self.H20 = P["E0"], P["H20"]
        self.SEC0 = self.E0 / self.H20
        self.V0, self.Vref0 = P["Vmean0"], P["Vref0"]
        self.W0, self.Wj, self.j_ref = P["W0"], P["Wj"], P["j_ref"]
        self.b_tafel = P["b_tafel"]
        self.profile_h = c["profile_hours"]
        self.eol_frac = c["end_of_life_voltage_rise"]
        self._tab = {}

    def parameters(self, case: dict) -> dict:
        if case["model"] == "linear":
            return {"mu_lin": case["rate_uV_per_h_per_cell"] * 1e-6}
        if case["model"] == "mechanistic":
            r = (case["hfr_drift_V_per_h_at_test"] + case["catalyst_layer_drift_V_per_h_at_test"]) / case["test_current_density_A_cm2"]
            return {"fA_min": case["anode_activity_final"], "k_cat": 1.0 / case["anode_decay_time_h"],
                    "k_R": r / self.R0, "t50_mem": case["membrane_half_thickness_time_h"]}
        raise ValueError(f"unknown electrolyser model {case['model']!r}")

    def state(self, t, p):
        """State at age t (h): voltages, energy and hydrogen over one profile, SEC."""
        t = np.asarray(t, float)
        if "mu_lin" in p:
            dv = p["mu_lin"] * t
            vm = self.V0 + dv
            en = self.E0 + dv * self.W0
            h = self.H20 + 0 * t
            return {"Vmean": vm, "Vref": self.Vref0 + dv, "Energy": en, "H2": h, "SEC": en / h}
        fa = p["fA_min"] + (1 - p["fA_min"]) * np.exp(-p["k_cat"] * t)
        eta = 1 - (1 - self.etaF0) / (1 - 0.5 * t / p["t50_mem"])
        dv = self.b_tafel / np.log(10) * (-np.log(fa))
        vm = self.V0 + dv + self.R0 * p["k_R"] * t * self.j_ref
        en = self.E0 + dv * self.W0 + self.R0 * p["k_R"] * t * self.Wj
        h = self.H20 * eta / self.etaF0
        return {"fA": fa, "etaF": eta, "Vmean": vm, "Vref": self.Vref0 + (vm - self.V0), "Energy": en, "H2": h, "SEC": en / h}

    def end_of_life(self, p, max_h=400000.0):
        g = lambda t: float(self.state(t, p)["Vref"] - (1 + self.eol_frac) * self.Vref0)
        return brentq(g, 0, max_h) if g(max_h) >= 0 else np.nan

    def life_table(self, p, n=801):
        """(end of life, ages, SEC at each age, hydrogen produced over one stack life)."""
        key = tuple(sorted(p.items()))
        if key not in self._tab:
            te = self.end_of_life(p)
            b = np.linspace(0, te, n)
            q = self.state(b, p)
            f = getattr(np, "trapezoid", None) or np.trapz
            self._tab[key] = (te, b, np.asarray(q["SEC"], float), f(np.asarray(q["H2"], float), b) / self.profile_h)
        return self._tab[key]

    def h2_over(self, p, hours):
        """Hydrogen produced over ``hours`` (kg), successive stacks restarting from new."""
        te, b, sec, h2_life = self.life_table(p)
        nfull = int(hours // te)
        rem = hours - nfull * te
        if rem <= 0:
            return nfull * h2_life
        f = getattr(np, "trapezoid", None) or np.trapz
        x = np.linspace(0, rem, 401)
        return nfull * h2_life + f(np.asarray(self.state(x, p)["H2"], float), x) / self.profile_h
