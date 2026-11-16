# Utiliser vos propres valeurs

[English](CUSTOMISE.md) | **Français**

Cette page liste chaque entrée que vous pouvez changer et l'endroit où elle se trouve. Pour des exemples prêts à lancer, avec leurs résultats, voir [USE_CASES.fr.md](USE_CASES.fr.md).

Toutes les entrées sont dans une configuration YAML (`config/default.yaml`). Changez une valeur avec `--set clé=valeur`, ou copiez le fichier et modifiez-le. Puis lancez :

```bash
python scripts/run.py --config config/mon_cas.yaml --out results/mon_cas
python scripts/plot.py --results results/mon_cas
```

Les tableaux écrits dans le dossier de sortie sont :

| Fichier | Contenu |
|---|---|
| `life.csv` | fin de vie et nombre de stacks de chaque convertisseur, surconsommation moyenne |
| `electrolyser.csv` | électrolyseur seul, changement climatique par kg d'hydrogène |
| `tank.csv` | réservoir seul, par km : fabrication, hydrogène perdu par perméation, total, hausse |
| `fuel_cell.csv` | pile seule, changement climatique par km : usage, fabrication, total, hausse, score unique |
| `chain.csv` | chaîne complète par km, par poste, hausse et score unique |
| `categories.csv` | les 16 catégories EF 3.1 : part de la fabrication et hausse de chaque cas |

## 1. Quantités d'usage

| Quoi | Clé | Exemple |
|---|---|---|
| Énergie de compression | `usage.compression_kWh_per_kg` | `--set usage.compression_kWh_per_kg=3.2` |
| Eau par kg d'hydrogène | `usage.water_kg_per_kg_h2` | `--set usage.water_kg_per_kg_h2=9` |
| Électricité de l'électrolyseur | `usage.electricity_electrolyser` | `residual_mix_FR`, `average_mix_FR`, `nuclear_FR`, `wind_FR`, `photovoltaic` |
| Électricité de la compression | `usage.electricity_compression` | mêmes choix |
| Heures de l'électrolyseur par an | `usage.electrolyser_hours_per_year` | `--set usage.electrolyser_hours_per_year=7392` |
| Comptage des stacks | `usage.stack_counting` | `integer` (entier) ou `prorata` |
| Distance et horizon | `horizon.vehicle_km_total`, `horizon.years` | `--set horizon.vehicle_km_total=250000` |

Pour ajouter une autre source d'électricité, ajoutez une colonne à `data/impacts/electricity_per_kWh.csv` (impact d'1 kWh dans les 16 catégories) et utilisez son nom.

## 2. Vieillissement

Chaque cas de `cases` choisit un modèle pour chaque convertisseur.

**Modèle linéaire** (vitesses publiées) :

```yaml
fuel_cell:
  model: linear
  hours_to_end_of_life: 6000          # heures jusqu'à 10 % de perte de tension
electrolyser:
  model: linear
  rate_uV_per_h_per_cell: 3.0
```

**Modèle semi-empirique** (constantes de laboratoire) :

```yaml
fuel_cell:
  model: semi_empirical
  ecsa_at_1000h: 0.67
  omega: 3.6
  voltage_loss_at_1p8_A_cm2_1000h_V: 0.045
  crossover_factor_1000h: 2.6
electrolyser:
  model: semi_empirical
  anode_activity_final: 0.1118
  anode_decay_time_h: 1000
  hfr_drift_V_per_h_at_test: 7.0e-6
  catalyst_layer_drift_V_per_h_at_test: 3.4e-6
  test_current_density_A_cm2: 3.0
  membrane_half_thickness_time_h: 80700
```

Vous pouvez ajouter un cas (avec n'importe quel nom) ou en retirer un ; chaque cas donne aussi la perméation du réservoir `[P0, P15]` en mL/h/L. Autres options : `fuel_cell.crossover_law` (`linear`, `exponential`, `constant`), et les critères de fin de vie `fuel_cell.end_of_life_voltage_loss` et `electrolyser.end_of_life_voltage_rise`.

## 3. Fabrication

**Sans ecoinvent** : modifiez `data/impacts/fabrication_per_unit.csv` (impact d'un stack de pile, d'un stack d'électrolyseur et d'un réservoir dans les 16 catégories), ou ajoutez une colonne et faites-y pointer `fabrication.fuel_cell_stack`, `fabrication.electrolyser_stack` ou `fabrication.tank`. Un stack d'une autre taille peut être représenté avec `electrolyser.stack_inventory_scale`.

**Avec ecoinvent** : changez les quantités dans `data/inventories/*.csv` et lancez `scripts/build_fabrication_brightway.py --project <votre projet>` ; il écrit un nouveau fichier de fabrication, que vous indiquez avec `fabrication.file`.

## 4. Mesures et modèles ajustés

- Une autre pile ou un autre trajet : remplacez `data/measurements/mirai2_fuel_cell_trip.csv` (colonnes `time_s`, `current_A`, `voltage_V`), donnez sa distance et l'hydrogène mesuré (`fuel_cell.trip_distance_km`, `fuel_cell.trip_h2_measured_kg`), le nombre de cellules et la surface active, et réajustez la courbe de polarisation avec `scripts/fit_pemfc.py` sur vos signaux.
- Un autre électrolyseur ou un autre profil : lancez `scripts/fit_pemwe.py --profile <fichier> --n-cells ... --area-cm2 ...` ; il écrit le fichier de paramètres lu par le modèle (`electrolyser.params_file`).

## 5. Seuil de durée de vie et sensibilité globale

```bash
python scripts/threshold.py --out results    # impact en fonction de la durée de vie du stack, prédictions des modèles placées dessus
python scripts/sobol.py --out results        # indices de Sobol de la chaîne (environ 15 min sur 2 cœurs)
```

`threshold.py` fait varier la durée de vie du stack avec le modèle linéaire et place chaque cas configuré sur la courbe. Il sépare aussi les deux effets du choix du modèle de vieillissement : la fin de vie prédite, et la forme de la trajectoire à fin de vie égale (modèle linéaire réglé sur la fin de vie du modèle semi-empirique).

`semi_empirical_constants.py` change chaque constante du modèle semi-empirique seule, vers une autre valeur publiée, et classe leurs effets ; modifiez `VARIANTS` pour tester vos propres valeurs.

`fuel_cell_tests.py` (`python scripts/fuel_cell_tests.py`) teste le modèle semi-empirique de la pile : loi de crossover, un critère de fin de vie supplémentaire pour la membrane (seuil de crossover) et la vitesse moyenne.

`sobol.py` lit les facteurs et leurs plages dans `global_sensitivity` de la configuration. Changez une plage, ajoutez ou retirez un facteur parmi ceux de la liste, ou changez `samples`.

## 6. Les modèles eux-mêmes

Les modèles sont de simples classes Python :

- `FuelCell.cell_voltage(I, t, p)` et `FuelCell.crossover(t, p)` dans `src/h2ageing/pemfc.py` ;
- `Electrolyser.state(t, p)` dans `src/h2ageing/pemwe.py` ;
- `Tank.permeation(t, p)` dans `src/h2ageing/tank.py`.

Pour essayer une autre loi de vieillissement, changez ces fonctions (ou ajoutez une nouvelle valeur `model:` dans `parameters()`). Tout ce qui suit (fin de vie, nombre de stacks, ACV) les utilise sans modification. Lancez `python tests/test_reference_results.py` avant votre changement pour vérifier votre installation, et attendez-vous à ce que les tests échouent après : ils comparent avec les résultats de référence de la configuration par défaut.
