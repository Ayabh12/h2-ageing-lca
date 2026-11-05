"""PEM fuel cell model (Toyota Mirai II stack) and its ageing.

Polarisation (cell voltage, cathode only)::

    V = E_rev - RT/(alpha_c F) ln( j / (i0c f_A(t)) ) - R(t) j + Bc ln(1 - j/ilim)

Ageing, mechanistic model (pessimistic case):
  * platinum surface f_A(t): dS/dt = -k S^2 exp(omega S) (Verducci et al.), k set so
    that S(1000 h) equals the measured value (Colombo et al. 2023);
  * apparent resistance R(t) = R0 (1 + k_R t), k_R from the voltage loss at 1.8 A/cm2
    minus its kinetic part;
  * hydrogen crossover from 2 mA/cm2, multiplied by the measured factor in 1000 h
    (linear, exponential or constant law). It only enters the hydrogen balance.

Ageing, linear model (optimistic and central cases): V(t) = V(0) - mu t, with
mu = 10 % of the reference cell voltage divided by the published hours to end of life.

The stack is driven over the measured road trip at constant power: at each age the
current that delivers the measured power is found by bisection. End of life is the
age at which the voltage at the reference current has lost 10 % (Brent's method).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import brentq, minimize_scalar

from .config import resolve

R = 8.314462618
F = 96485.33212
M_H2 = 2.01588e-3
J_LOW, J_HIGH, T_TEST = 0.08, 1.8, 1000.0


class FuelCell:
    def __init__(self, cfg: dict):
        c = cfg["fuel_cell"]
        self.cfg = c
        trip = pd.read_csv(resolve(c["trip_file"]))
        self.t = trip["time_s"].to_numpy(float)
        self.I_exp = trip["current_A"].to_numpy(float)
        self.U_exp = trip["voltage_V"].to_numpy(float)
        self.dt = np.diff(self.t, append=self.t[-1] + np.median(np.diff(self.t)))
        self.active = self.I_exp > 0
        self.P_dem = self.I_exp * self.U_exp
        self.distance_km = c["trip_distance_km"]
        self.duration_h = (self.t[-1] - self.t[0]) / 3600.0
        self.N = c["n_cells"]
        self.A = c["active_area_cm2"]
        self.T = c["temperature_K"]
        self.alpha = c["alpha_c"]
        self.E = 1.229 - 0.85e-3 * (self.T - 298.15)
        p = c["polarisation"]
        self.i0c, self.R0, self.Bc, self.ilim = p["i0c_A_cm2"], p["R0_ohm_cm2"], p["Bc_V"], p["ilim_A_cm2"]
        self.h2_measured = c["trip_h2_measured_kg"]
        self.x0 = c["crossover_initial_A_cm2"]
        self.law = c["crossover_law"]
        self.niter = c["current_bisection_iterations"]
        self.I_ref = c["reference_current_A"]
        self.eol_frac = c["end_of_life_voltage_loss"]
        # Hydrogen not explained by Faraday's law over the trip: constant equivalent current
        t_act = float(np.sum(self.dt[self.active]))
        q = float(np.sum(self.I_exp * self.dt))
        self.cross0 = (2 * F * self.h2_measured / (self.N * M_H2) - q) / (self.A * t_act)
        self._tab = {}
        self.U0 = float(self.stack_voltage(self.I_ref, 0.0, {}))
        # point-by-point anchoring: at age zero the model reproduces the measured current
        u_mod0 = self.stack_voltage(np.maximum(self.I_exp, 0.1), 0.0, {})
        self.anchor = np.ones_like(self.I_exp)
        self.anchor[self.active] = self.U_exp[self.active] / u_mod0[self.active]
        self.I_dom = 0.995 * self.ilim * self.A
        self.h2_per_km_measured = self.h2_measured / self.distance_km

    # ------------------------------------------------------------------ parameters
    def parameters(self, case: dict) -> dict:
        """Turn a case of the configuration into model parameters."""
        if case["model"] == "linear":
            u0_cell = self.U0 / self.N
            return {"mu_lin": self.eol_frac * u0_cell / case["hours_to_end_of_life"]}
        if case["model"] == "mechanistic":
            S = case["ecsa_at_1000h"]
            dv_kin = R * self.T / (self.alpha * F) * np.log(1.0 / S)
            r_app = (case["voltage_loss_at_1p8_A_cm2_1000h_V"] - dv_kin) / J_HIGH / T_TEST
            return {"S1000": S, "omega": case["omega"], "k_R": r_app / self.R0,
                    "k_mem": np.log(case["crossover_factor_1000h"]) / T_TEST}
        raise ValueError(f"unknown fuel cell model {case['model']!r}")

    # ------------------------------------------------------------------ ageing laws
    @staticmethod
    def _ecsa_table(omega):
        S = np.linspace(1.0, 0.02, 6000)
        f = np.exp(-omega * S) / S ** 2
        g = np.concatenate([[0.0], np.cumsum(0.5 * (f[1:] + f[:-1]) * (S[:-1] - S[1:]))])  # g(S) = int_S^1 exp(-w s)/s^2 ds
        return S, g

    def ecsa(self, t, p):
        if "S1000" not in p or p["S1000"] >= 1:
            return np.ones_like(np.asarray(t, float))
        S, g = self._ecsa_table(p["omega"])
        k = float(np.interp(p["S1000"], S[::-1], g[::-1])) / T_TEST
        return np.interp(k * np.asarray(t, float), g, S)

    def resistance(self, t, p):
        return self.R0 * (1 + p.get("k_R", 0.0) * np.asarray(t, float))

    def crossover(self, t, p):
        """Crossover current density (A/cm2), from x0 at age zero."""
        t = np.asarray(t, float)
        if "mu_lin" in p or "k_mem" not in p:
            return self.x0 + 0 * t
        if self.law == "exponential":
            return self.x0 * np.exp(p["k_mem"] * t)
        if self.law == "linear":
            return self.x0 * (1 + (np.exp(p["k_mem"] * T_TEST) - 1) * t / T_TEST)
        if self.law == "constant":
            return self.x0 + 0 * t
        raise ValueError(self.law)

    def h2_loss_current(self, t, p):
        """Measured gap (constant) plus the rise of the crossover."""
        return self.cross0 + self.crossover(t, p) - self.x0

    # ------------------------------------------------------------------ voltage
    def cell_voltage(self, I, t, p):
        j = np.maximum(np.asarray(I, float) / self.A, 1e-12)
        if "mu_lin" in p:
            return self.cell_voltage(I, 0.0, {}) - p["mu_lin"] * np.asarray(t, float)
        fa = self.ecsa(t, p)
        return (self.E - R * self.T / (self.alpha * F) * np.log(j / (self.i0c * fa))
                - j * self.resistance(t, p) + self.Bc * np.log(1 - j / self.ilim))

    def stack_voltage(self, I, t, p):
        return self.N * self.cell_voltage(I, t, p)

    def end_of_life(self, p, max_h=60000.0):
        target = (1 - self.eol_frac) * self.U0
        g = lambda t: float(self.stack_voltage(self.I_ref, t, p) - target)
        return brentq(g, 0, max_h) if g(max_h) <= 0 else np.nan

    # ------------------------------------------------------------------ trip at a given age
    def currents(self, t, p):
        ip = float(minimize_scalar(lambda x: -float(x * self.stack_voltage(x, t, p)),
                                   bounds=(0.1, self.I_dom), method="bounded").x)
        lo = np.zeros_like(self.I_exp) + 1e-9
        hi = np.zeros_like(self.I_exp) + ip
        feasible = (~self.active) | (self.P_dem <= self.anchor * ip * self.stack_voltage(ip, t, p) * (1 + 1e-10))
        for _ in range(self.niter):
            mid = (lo + hi) / 2
            low = self.anchor * mid * self.stack_voltage(mid, t, p) < self.P_dem
            lo = np.where(low, mid, lo)
            hi = np.where(low, hi, mid)
        cur = (lo + hi) / 2
        cur[~self.active] = 0
        cur[~feasible] = np.nan
        return cur, feasible

    def h2_trip(self, t, p):
        """Hydrogen consumed over the trip at age t (kg)."""
        cur, _ = self.currents(t, p)
        total = cur + self.A * self.h2_loss_current(t, p) * self.active
        return float(np.nansum(self.N * M_H2 * total / (2 * F) * self.dt))

    def life_table(self, p):
        """(end of life, ages, hydrogen per km at each age)."""
        key = tuple(sorted(p.items()))
        if key not in self._tab:
            te = self.end_of_life(p)
            a = np.linspace(0, te, self.cfg["ages_per_life"])
            self._tab[key] = (te, a, np.array([self.h2_trip(x, p) for x in a]) / self.distance_km)
        return self._tab[key]
