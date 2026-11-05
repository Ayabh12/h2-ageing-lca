"""Copy the measurement files of ../data into this folder, with the names the notebooks expect.

    cd notebooks
    python prepare_inputs.py

Run the notebooks in this order: Fitting_polarisation_Mirai_II, AB_vieillissement_PEMWE,
AB_vieillissement_PEMFC, then AB_vieillissement_trois_cas (reference results) and the others.
"""
import shutil
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"

sig = pd.read_csv(DATA / "measurements/mirai2_fuel_cell_signals.csv")
sig.columns = ["Temps (s)", "Vitesse (km/h)", "Courant FC (A)", "Tension FC (V)", "Niveau hydrogène restant (%)"]
sig.to_excel(HERE / "signaux_fuel_cell_1.xlsx", index=False)

trip = pd.read_csv(DATA / "measurements/mirai2_fuel_cell_trip.csv")
trip.columns = ["Temps (s)", "Courant FC (A)", "Tension FC (V)"]
trip.to_excel(HERE / "mirai2_fuel_cell_trip.xlsx", sheet_name="wltp", index=False)

shutil.copy(DATA / "measurements/nel_mc250_wind_profile.xlsx", HERE / "profil_electrolyseur_ACV_duree_vie (2).xlsx")
shutil.copy(DATA / "parameters/pemwe_fit.json", HERE / "pemwe_parametres.json")
print("inputs ready in", HERE)
