# Utiliser et adapter le modèle

[English](GUIDE.md) | **Français**

Cette page rassemble tout ce qu'il faut pour utiliser le modèle : l'installer et le lancer, changer une valeur, la liste de tout ce que l'on peut changer, puis, à la fin, des exemples commentés avec leurs résultats. Vous n'écrivez que ce que vous changez : la recherche de la fin de vie, le comptage des stacks et l'ACV sont recalculés automatiquement.

Des exemples prêts à lancer dans Jupyter : [`examples/adapt_the_model.fr.ipynb`](../examples/adapt_the_model.fr.ipynb) et [`examples/check_and_examples.fr.ipynb`](../examples/check_and_examples.fr.ipynb).

1. [Installer et lancer](#1-installer-et-lancer)
2. [Changer une valeur](#2-changer-une-valeur)
3. [Tout ce que l'on peut changer](#3-tout-ce-que-lon-peut-changer)
4. [Vérifier et partager](#4-vérifier-et-partager)
5. [Exemples commentés](#5-exemples-commentés)

---

## 1. Installer et lancer

Prérequis : Python 3.10 ou plus récent, et Git (ou téléchargez le dépôt en ZIP : bouton vert **Code**, **Download ZIP**).

**Dans un terminal** (Anaconda Prompt, PowerShell, terminal macOS ou Linux) :

```bash
git clone https://github.com/Ayabh12/h2-ageing-lca
cd h2-ageing-lca
pip install -r requirements.txt
python scripts/run.py                    # configuration par défaut, environ 2 s
python tests/test_reference_results.py   # 13 tests : la configuration par défaut redonne les résultats de référence
```

**Dans Jupyter**, cette méthode marche partout, avec ou sans Git installé. Copiez ces deux cellules dans un nouveau notebook :

```python
# cellule 1 : télécharger le dépôt (sans Git) et installer, une seule fois
import sys, urllib.request, zipfile
urllib.request.urlretrieve("https://github.com/Ayabh12/h2-ageing-lca/archive/refs/heads/main.zip", "h2-ageing-lca.zip")
zipfile.ZipFile("h2-ageing-lca.zip").extractall(".")
%cd h2-ageing-lca-main
!{sys.executable} -m pip install -r requirements.txt
```

```python
# cellule 2 : lancer le modèle, puis vérifier les résultats de référence
!{sys.executable} scripts/run.py
!{sys.executable} tests/test_reference_results.py
```

Dans Jupyter, `!` lance une commande du terminal, `%cd` entre dans un dossier, et `{sys.executable}` désigne le Python du notebook. Si le dossier existe déjà, lancez seulement `import sys` puis `%cd h2-ageing-lca-main`. Un notebook prêt à lancer est aussi dans [examples/adapt_the_model.fr.ipynb](../examples/adapt_the_model.fr.ipynb).

En Python ou dans Jupyter, depuis le dossier qui contient `h2-ageing-lca` :

```python
import sys
sys.path.insert(0, "h2-ageing-lca/src")
from h2ageing import load_config, with_values, run

cfg = load_config()          # toutes les entrées, lues dans config/default.yaml
```

```python
ref = run(cfg)
ref["chain"][["case", "total_g_per_km", "rise_pct"]].round(1)
```

| cas | g CO2-éq/km | hausse (%) |
|---|---|---|
| no_ageing (sans vieillissement) | 74,1 | 0,0 |
| optimistic (optimiste) | 77,8 | 5,0 |
| central | 97,2 | 31,1 |
| pessimistic (pessimiste) | 100,1 | 35,0 |

`run` renvoie un dictionnaire de tableaux : `life` (fin de vie et stacks), `fuel_cell`, `electrolyser`, `tank`, `chain` et `categories` (16 catégories EF 3.1). En ligne de commande : `python scripts/run.py`.

Pour écrire les tableaux dans un dossier et tracer les figures :

```bash
python scripts/run.py --out results
python scripts/plot.py --results results
```

Les tableaux écrits dans le dossier de sortie (`--out`) sont :

| Fichier | Contenu |
|---|---|
| `life.csv` | fin de vie et nombre de stacks de chaque convertisseur, surconsommation moyenne |
| `electrolyser.csv` | électrolyseur seul, changement climatique par kg d'hydrogène |
| `tank.csv` | réservoir seul, par km : fabrication, hydrogène perdu par perméation, total, hausse |
| `fuel_cell.csv` | pile seule, changement climatique par km : usage, fabrication, total, hausse, score unique |
| `chain.csv` | chaîne complète par km, par poste, hausse et score unique |
| `categories.csv` | les 16 catégories EF 3.1 : part de la fabrication et hausse de chaque cas |


### Organisation du dépôt

```
config/default.yaml        toutes les entrées, chacune avec sa source (unités dans le nom des clés)
src/h2ageing/              les modèles (paquet Python)
    pemfc.py               pile : polarisation, vieillissement (linéaire et semi-empirique), trajet à puissance imposée
    pemwe.py               électrolyseur : profil de fonctionnement, vieillissement (linéaire et semi-empirique)
    tank.py                perméation du réservoir de type IV
    impacts.py             données d'impact EF 3.1 et score unique
    chain.py               ACV de chaque composant et de la chaîne complète
    run.py                 lance tous les cas, construit les tableaux de résultats
scripts/                   outils en ligne de commande (liste dans docs/GUIDE.fr.md)
data/
    measurements/          mesures sur route de la pile, profil éolien de l'électrolyseur
    parameters/            paramètres de polarisation ajustés
    inventories/           inventaires de premier plan (masses, énergie, noms des activités ecoinvent)
    impacts/               impacts caractérisés (par kWh, par kg d'eau, par stack ou réservoir)
tests/                     résultats de référence et tests qui les vérifient
notebooks/                 notebooks de recherche d'origine (en français)
docs/                      méthode, guide d'utilisation avec exemples, limites
examples/                  notebooks Jupyter : utiliser et adapter le modèle en six niveaux ; vérifications et exemples avec et sans ecoinvent
```

### Reproduire chaque résultat

| Résultat | Commande | Durée |
|---|---|---|
| Trois cas : fin de vie, stacks, chaque composant, chaîne complète, 16 catégories | `python scripts/run.py --out results` | ~2 s |
| Vérification par rapport aux valeurs de référence | `python tests/test_reference_results.py` (lancé aussi automatiquement à chaque envoi) | ~10 s |
| Diagramme en barres de la chaîne par poste (après `run.py`) | `python scripts/plot.py --results results` | ~2 s |
| Sources d'électricité, heures de l'électrolyseur, comptage des stacks | `run.py` avec `--set` (voir les [exemples commentés](#5-exemples-commentés)) | ~2 s chacun |
| Impact en fonction de la durée de vie du stack (paliers et seuils) | `python scripts/threshold.py --out results` | ~30 s |
| Loi de crossover du modèle semi-empirique de la pile, vitesse moyenne | `python scripts/fuel_cell_tests.py` | ~10 s |
| Effet de chaque constante semi-empirique (autres valeurs publiées) | `python scripts/semi_empirical_constants.py` | ~5 s |
| Sensibilité globale (indices de Sobol, 10 240 calculs) | `python scripts/sobol.py --out results` | ~15 min (2 cœurs) |
| Ajustements de polarisation (ils réécrivent `data/parameters/` et redonnent les paramètres fournis) | `python scripts/fit_pemfc.py`, `python scripts/fit_pemwe.py` | ~5 s chacun |
| Impacts de fabrication à partir des inventaires | `python scripts/build_fabrication_brightway.py --project <nom>` (nécessite ecoinvent) | – |

Les notebooks de recherche d'origine (en français, sorties comprises) sont dans [notebooks/](../notebooks/README.fr.md) ; ils donnent les mêmes résultats, avec plus de figures.

## 2. Changer une valeur

Trois façons, au choix ; le fichier `config/default.yaml` n'est jamais modifié :

- **En ligne de commande** : `python scripts/run.py --set clé=valeur` (un `--set` par valeur).
- **En Python** : `with_values` renvoie une copie de la configuration avec vos valeurs.

  ```python
  r = run(with_values(cfg, **{"cases.central.fuel_cell.hours_to_end_of_life": 5000.0}))
  ```
- **Dans un fichier** : copiez `config/default.yaml`, changez les valeurs, et lancez `python scripts/run.py --config config/mon_cas.yaml` (voir l'exemple 6).

Toutes les clés sont listées dans la section 3.

## 3. Tout ce que l'on peut changer

### 3.1 Quantités d'usage

| Quoi | Clé | Exemple |
|---|---|---|
| Énergie de compression | `usage.compression_kWh_per_kg` | `--set usage.compression_kWh_per_kg=3.2` |
| Eau par kg d'hydrogène | `usage.water_kg_per_kg_h2` | `--set usage.water_kg_per_kg_h2=9` |
| Électricité de l'électrolyseur | `usage.electricity_electrolyser` | `residual_mix_FR`, `average_mix_FR`, `nuclear_FR`, `wind_FR`, `photovoltaic` |
| Électricité de la compression | `usage.electricity_compression` | les mêmes cinq sources que pour l'électrolyseur, choisies séparément (par défaut `residual_mix_FR`) |
| Heures de l'électrolyseur par an | `usage.electrolyser_hours_per_year` | `--set usage.electrolyser_hours_per_year=7392` |
| Comptage des stacks | `usage.stack_counting` | `integer` (entier) ou `prorata` |
| Distance et horizon | `horizon.vehicle_km_total`, `horizon.years` | `--set horizon.vehicle_km_total=250000` |

Pour ajouter une autre source d'électricité, ajoutez une colonne à `data/impacts/electricity_per_kWh.csv` (impact d'1 kWh dans les 16 catégories) et utilisez son nom.

### 3.2 Vieillissement

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

Constantes du modèle semi-empirique (clés sous `cases.pessimistic.`) :

| Constante | Clé |
|---|---|
| Pile : surface de platine après 1 000 h | `fuel_cell.ecsa_at_1000h` |
| Pile : forme de la loi du platine | `fuel_cell.omega` |
| Pile : perte de tension à 1,8 A/cm² après 1 000 h | `fuel_cell.voltage_loss_at_1p8_A_cm2_1000h_V` |
| Pile : facteur de crossover après 1 000 h | `fuel_cell.crossover_factor_1000h` |
| Électrolyseur : activité finale de l'anode et sa constante de temps | `electrolyser.anode_activity_final`, `electrolyser.anode_decay_time_h` |
| Électrolyseur : dérives de résistance et densité de courant de l'essai | `electrolyser.hfr_drift_V_per_h_at_test`, `electrolyser.catalyst_layer_drift_V_per_h_at_test`, `electrolyser.test_current_density_A_cm2` |
| Électrolyseur : amincissement de la membrane | `electrolyser.membrane_half_thickness_time_h` |

La source de chaque valeur de référence est donnée à côté d'elle dans `config/default.yaml`. `scripts/semi_empirical_constants.py` les change une par une vers d'autres valeurs publiées.

### 3.3 Une autre loi de vieillissement

| Loi | Fonction à remplacer | Arguments (âge `t` en heures, paramètres `p`) |
|---|---|---|
| Surface de platine de la pile | `pemfc.FuelCell.ecsa` | `t`, `p` |
| Résistance de la pile | `pemfc.FuelCell.resistance` | `t`, `p` |
| Crossover de la pile | `pemfc.FuelCell.crossover` | `t`, `p` |
| Vieillissement de l'électrolyseur (tension, résistance, rendement faradique) | `pemwe.Electrolyser.state` | `t`, `p` |
| Perméation du réservoir | `tank.Tank.permeation` | `t_years` (années), `p` |

Les modèles sont de simples classes Python :

- `FuelCell.cell_voltage(I, t, p)` et `FuelCell.crossover(t, p)` dans `src/h2ageing/pemfc.py` ;
- `Electrolyser.state(t, p)` dans `src/h2ageing/pemwe.py` ;
- `Tank.permeation(t, p)` dans `src/h2ageing/tank.py`.

Pour essayer une autre loi de vieillissement, changez ces fonctions (ou ajoutez une nouvelle valeur `model:` dans `parameters()` ; voir l'exemple 7). Tout ce qui suit (fin de vie, nombre de stacks, ACV) les utilise sans modification. Lancez `python tests/test_reference_results.py` avant votre changement pour vérifier votre installation, et attendez-vous à ce que les tests échouent après : ils comparent avec les résultats de référence de la configuration par défaut.

### 3.4 Fabrication

**Sans licence ecoinvent.** Le modèle utilise alors des impacts déjà calculés avec ecoinvent 3.11 (dans `data/impacts`, pour les 16 catégories EF 3.1) : l'impact d'**1 kWh** d'électricité pour chacune des cinq sources, d'**1 kg** d'eau déionisée, et de la **fabrication d'une unité** de chaque composant (un stack de pile, un stack d'électrolyseur, un réservoir). Le modèle calcule les quantités (kWh, kg d'eau, nombre de stacks) et les multiplie par ces impacts. On peut donc changer toutes les quantités, mais pas le contenu d'un inventaire de fabrication.

Pour utiliser votre propre impact de fabrication, modifiez `data/impacts/fabrication_per_unit.csv` (impact d'un stack de pile, d'un stack d'électrolyseur et d'un réservoir dans les 16 catégories), ou ajoutez une colonne et faites-y pointer `fabrication.fuel_cell_stack`, `fabrication.electrolyser_stack` ou `fabrication.tank`. Un stack d'une autre taille peut être représenté avec `electrolyser.stack_inventory_scale`.

**Avec une licence ecoinvent :**

1. **Installer Brightway** (une fois) : `pip install -U -r requirements-brightway.txt`.
2. **Donner votre identifiant ecoinvent.** Deux façons :
   - laisser le script le demander : il demande votre identifiant, puis votre mot de passe (le mot de passe ne s'affiche pas pendant la saisie) ;
   - ou le définir avant, dans deux variables d'environnement, `EI_USERNAME` et `EI_PASSWORD` : dans un terminal Windows `set EI_USERNAME=...`, sous macOS ou Linux `export EI_USERNAME=...` (de même pour `EI_PASSWORD`) ; dans Jupyter, `os.environ["EI_USERNAME"] = input()` et `os.environ["EI_PASSWORD"] = getpass.getpass()`.

   L'identifiant peut être le vôtre ou celui d'une licence partagée par votre établissement, si ses conditions le permettent. Il est seulement envoyé à ecoinvent pour télécharger la base et n'est jamais écrit dans un fichier. Ne mettez jamais d'identifiant dans ce dépôt ni dans une cellule de notebook que vous partagez : les licences ecoinvent sont personnelles ou propres à un établissement.
3. **Importer ecoinvent et recalculer les impacts** : `python scripts/build_fabrication_brightway.py --project <projet> --import-ecoinvent --out results/<fichier>.csv`. La première fois, ecoinvent 3.11 cut-off, sa biosphère et ses méthodes d'impact sont téléchargés et importés dans le projet Brightway `<projet>` ; cela prend d'environ 20 minutes à moins d'une heure. Les fois suivantes, le script trouve ecoinvent dans le projet et ne fait que recalculer (environ une minute). Il affiche les 16 méthodes EF 3.1 utilisées, puis l'impact de chaque composant sur le changement climatique.
4. **Vérifier votre installation** (une fois) : lancez l'étape 3 sur les inventaires tels que fournis, puis comparez le fichier écrit avec les impacts fournis, en pourcentage :

   ```python
   import pandas as pd
   nouveau = pd.read_csv("results/<fichier>.csv").set_index("category")
   fourni = pd.read_csv("data/impacts/fabrication_per_unit.csv").set_index("category")
   ((nouveau - fourni) / fourni * 100).round(2)
   ```

   Toutes les valeurs doivent être à 0 (ou −0, un arrondi) : avec ecoinvent 3.11 cut-off, l'écart avec les impacts fournis (calculés avec Activity Browser) est inférieur à 0,01 % dans les 16 catégories et pour les trois composants.
5. **Changer un inventaire** : dans `data/inventories/*.csv`, changez une quantité, l'activité ecoinvent ou sa localisation, ou mettez `included` à `no` pour retirer une ligne (colonnes expliquées dans [data/inventories/README.fr.md](../data/inventories/README.fr.md)).
6. **Recalculer** : relancez l'étape 3 avec un autre fichier de sortie.
7. **Utiliser les nouveaux impacts dans le modèle** : `python scripts/run.py --set fabrication.file=results/<fichier>.csv --out results/<nom>`.

Si le script s'arrête avec « 0 matches » ou « 2 matches », l'activité ecoinvent nommée dans l'inventaire n'a pas été trouvée, ou pas une seule fois : vérifiez son nom, sa localisation et son produit de référence dans votre base ecoinvent. Si le téléchargement échoue, vérifiez que votre compte ecoinvent donne accès à la version 3.11.

Toutes ces étapes, avec la vérification des 16 catégories et des exemples avec et sans licence, dont des exemples qui changent une constante, une loi ou le modèle d'un cas, puis les 16 catégories d'impact et la sensibilité (source d'électricité, seuil de durée de vie, Sobol) (valeurs attendues indiquées), sont prêtes à lancer dans Jupyter : [examples/check_and_examples.fr.ipynb](../examples/check_and_examples.fr.ipynb).

### 3.5 Mesures, équipements et données

| Vous avez | Remplacez | Puis |
|---|---|---|
| des mesures de polarisation d'une autre pile ou d'un autre électrolyseur | les fichiers de `data/measurements/` | `python scripts/fit_pemfc.py` ou `fit_pemwe.py` |
| un autre inventaire de fabrication | les quantités de `data/inventories/` | `python scripts/build_fabrication_brightway.py` (nécessite ecoinvent) |
| des impacts tirés d'une autre base ou d'une autre méthode | les fichiers de `data/impacts/` | rien : ils sont lus directement |
| une autre source d'électricité | une nouvelle colonne dans `data/impacts/electricity_per_kWh.csv` | utilisez son nom dans `usage.electricity_electrolyser` |

- Une autre pile ou un autre trajet : remplacez `data/measurements/mirai2_fuel_cell_trip.csv` (colonnes `time_s`, `current_A`, `voltage_V`), donnez sa distance et l'hydrogène mesuré (`fuel_cell.trip_distance_km`, `fuel_cell.trip_h2_measured_kg`), le nombre de cellules et la surface active, et réajustez la courbe de polarisation avec `scripts/fit_pemfc.py` sur vos signaux.
- Un autre électrolyseur ou un autre profil : lancez `scripts/fit_pemwe.py --profile <fichier> --n-cells ... --area-cm2 ...` ; il écrit le fichier de paramètres lu par le modèle (`electrolyser.params_file`).

### 3.6 Seuil de durée de vie et sensibilité globale

```bash
python scripts/threshold.py --out results    # impact en fonction de la durée de vie du stack, prédictions des modèles placées dessus
python scripts/sobol.py --out results        # indices de Sobol de la chaîne (environ 15 min sur 2 cœurs)
```

`threshold.py` fait varier la durée de vie du stack avec le modèle linéaire et place chaque cas configuré sur la courbe. Il sépare aussi les deux effets du choix du modèle de vieillissement : la fin de vie prédite, et la forme de la trajectoire à fin de vie égale (modèle linéaire réglé sur la fin de vie du modèle semi-empirique).

`semi_empirical_constants.py` change chaque constante du modèle semi-empirique seule, vers une autre valeur publiée, et classe leurs effets ; modifiez `VARIANTS` pour tester vos propres valeurs.

`fuel_cell_tests.py` (`python scripts/fuel_cell_tests.py`) teste le modèle semi-empirique de la pile : loi de crossover, un critère de fin de vie supplémentaire pour la membrane (seuil de crossover) et la vitesse moyenne.

`sobol.py` lit les facteurs et leurs plages dans `global_sensitivity` de la configuration. Changez une plage, ajoutez ou retirez un facteur parmi ceux de la liste, ou changez `samples`.

## 4. Vérifier et partager

- **Vérifier.** `python tests/test_reference_results.py` vérifie que la configuration par défaut redonne les résultats de référence. Lancez-le avant de changer le code ; après le changement d'une loi, il doit échouer, puisque les résultats changent.
- **Poser une question ou signaler une erreur.** Ouvrez une *Issue* sur GitHub (onglet *Issues*, *New issue*). Questions et réponses restent publiques, donc la personne suivante les trouve.
- **Garder votre propre version en ligne.** Cliquez sur *Fork* sur GitHub : vous obtenez votre propre copie du dépôt, que vous pouvez modifier librement. Elle affiche « forked from Ayabh12/h2-ageing-lca ».
- **Proposer une amélioration.** Depuis votre fork, ouvrez une *Pull request*. Les changements sont relus avant d'être intégrés ; les nouvelles données de dégradation mesurées sur des stacks commerciaux sont particulièrement bienvenues.

Personne ne peut modifier ce dépôt sans l'accord de sa propriétaire : les forks et les copies locales sont indépendants.

---

## 5. Exemples commentés

Chaque exemple pose une question, donne la commande qui y répond et montre le résultat obtenu avec les données fournies (changement climatique, chaîne complète, g CO2-éq/km). Toutes les commandes tournent en quelques secondes, sans ecoinvent. Changez les valeurs pour répondre à votre propre question.

Les résultats de référence, pour comparaison :

| | Sans vieillissement | Optimiste | Central | Pessimiste |
|---|---|---|---|---|
| Chaîne complète (g CO2-éq/km) | 74,12 | 77,84 (+5,0 %) | 97,15 (+31,1 %) | 100,06 (+35,0 %) |

### 1. Et si l'électrolyseur fonctionne à l'électricité éolienne ?

**Pourquoi se poser la question :** la référence utilise le mix résiduel français, la source testée la plus carbonée. Un projet avec un contrat d'achat d'électricité éolienne utiliserait une autre source.

```bash
python scripts/run.py --set usage.electricity_electrolyser=wind_FR
```

| | Sans vieillissement | Optimiste | Central | Pessimiste |
|---|---|---|---|---|
| Chaîne complète (g CO2-éq/km) | 41,22 | 42,32 (+2,7 %) | 61,27 (+48,6 %) | 61,97 (+50,3 %) |

**Ce que ça montre :** la chaîne émet beaucoup moins, mais l'effet relatif du vieillissement est plus grand. Les stacks de remplacement ajoutent le même impact quelle que soit l'électricité, et ils pèsent plus quand le reste est plus propre. Sources disponibles : `residual_mix_FR`, `average_mix_FR`, `nuclear_FR`, `wind_FR`, `photovoltaic` ; ajoutez la vôtre comme une colonne de `data/impacts/electricity_per_kWh.csv`.

### 2. Et si mon stack de pile dure plus longtemps ?

**Pourquoi se poser la question :** le cas central utilise 4 100 h jusqu'à la fin de vie (meilleure flotte du DOE, 2006–2016). Un stack plus récent peut durer plus longtemps.

```bash
python scripts/run.py --set cases.central.fuel_cell.hours_to_end_of_life=6000
```

| | Central (référence, 4 100 h) | Central avec 6 000 h |
|---|---|---|
| Stacks de pile | 2 | 1 |
| Chaîne complète (g CO2-éq/km) | 97,15 (+31,1 %) | 78,88 (+6,4 %) |

**Ce que ça montre :** au-delà de l'horizon de 5 554 heures de fonctionnement, un seul stack suffit, et la hausse passe de +31 % à +6 %. L'exemple 4 donne les seuils exacts.

### 3. Et si le véhicule roule moins ?

**Pourquoi se poser la question :** 200 000 km est la cible de Toyota pour le stack de la Mirai II ; un véhicule peut être retiré plus tôt.

```bash
python scripts/run.py --set horizon.vehicle_km_total=150000
```

| | Sans vieillissement | Optimiste | Central | Pessimiste |
|---|---|---|---|---|
| Chaîne complète (g CO2-éq/km) | 84,25 | 87,56 (+3,9 %) | 113,87 (+35,2 %) | 116,23 (+38,0 %) |

**Ce que ça montre :** la fabrication est répartie sur moins de kilomètres, donc toutes les valeurs augmentent, et le poids du stack de remplacement aussi.

### 4. Combien de temps un stack de pile doit-il durer pour éviter un remplacement ?

**Pourquoi se poser la question :** pour un constructeur ou un gestionnaire de flotte, la question utile est le seuil, pas la durée de vie exacte.

**L'idée.** Sur sa vie (200 000 km), le véhicule fait fonctionner sa pile pendant 5 554 heures : c'est l'horizon. Le nombre de stacks nécessaires dépend seulement de la durée de vie d'un stack comparée à cet horizon :

- un stack qui dure **plus de 5 554 h** tient toute la vie du véhicule : **1 stack** ;
- un stack qui dure **entre 2 777 h (la moitié de l'horizon) et 5 554 h** s'arrête avant la fin et demande un remplacement : **2 stacks** ;
- un stack qui dure **entre 1 851 h (le tiers de l'horizon) et 2 777 h** demande deux remplacements : **3 stacks**.

```bash
python scripts/threshold.py --out results
```

Le script calcule l'impact pour chaque durée de vie de 1 500 à 12 000 h (`results/threshold_fuel_cell.csv`) et place les trois cas par rapport aux seuils (`results/model_choice.csv`). Résultats avec les données fournies :

| Durée de vie du stack | Stacks de pile | Hausse de la chaîne |
|---|---|---|
| de 1 851 à 2 777 h | 3 | environ +56 % |
| de 2 777 à 5 554 h | 2 | environ +31 % |
| plus de 5 554 h | 1 | environ +6 % |

**Ce que ça montre :** le résultat évolue par paliers. Un stack qui dure 4 100 h et un stack qui dure 5 000 h demandent tous deux un remplacement, donc ils donnent presque le même résultat (+31,1 % et +31,4 %). Un stack qui passe de 5 500 à 5 600 h franchit le seuil : un seul stack suffit, et la hausse tombe d'environ +31 % à environ +7 %. Gagner quelques centaines d'heures ne sert à rien tant qu'aucun seuil n'est franchi ; pour ce véhicule, l'objectif est de dépasser 5 554 h.

### 5. Et si j'utilise mes propres constantes de vieillissement ?

**Pourquoi se poser la question :** le cas pessimiste utilise des constantes mesurées sur des cellules de laboratoire. Vous avez peut-être d'autres mesures.

```bash
python scripts/semi_empirical_constants.py
```

Le script change chaque constante du modèle semi-empirique seule, vers une autre valeur publiée, et affiche la fin de vie, les stacks et la hausse. Sortie avec les données fournies :

| Constante changée | Fin de vie de la pile ; stacks | Hausse de la chaîne |
|---|---|---|
| aucune (référence pessimiste) | 2 895 h ; 2 | +35,0 % |
| perte de la pile à fort courant : 27 mV au lieu de 45 mV | 5 652 h ; 1 | +12,8 % |
| facteur de crossover de la pile : 1,4 au lieu de 2,6 | 2 895 h ; 2 | +33,2 % |
| surface de platine de la pile : 0,65 au lieu de 0,67 | 2 909 h ; 2 | +35,0 % |
| dérive de la HFR de l'électrolyseur : 0 | 2 895 h ; 2 | +34,6 % |

**Ce que ça montre :** une seule constante, la perte de tension de la pile à fort courant, décide du nombre de stacks ; c'est celle à mesurer en premier. Modifiez la liste `VARIANTS` en haut du script pour tester vos propres valeurs, ou donnez directement une constante, par exemple :

```bash
python scripts/run.py --set cases.pessimistic.fuel_cell.voltage_loss_at_1p8_A_cm2_1000h_V=0.035
```

### 6. Décrire son propre cas dans un fichier de configuration

**Exemple : un constructeur dont le stack de pile dure 7 000 h et dont l'électrolyseur fonctionne à l'électricité éolienne.** Copiez la configuration, changez les deux valeurs, et gardez la source de chaque changement dans un commentaire :

```bash
cp config/default.yaml config/mon_cas.yaml
```

```yaml
# config/mon_cas.yaml
usage:
  electricity_electrolyser: wind_FR        # contrat d'achat d'électricité éolienne
cases:
  central:
    fuel_cell:
      model: linear
      hours_to_end_of_life: 7000           # notre propre essai d'endurance
```

```bash
python scripts/run.py --config config/mon_cas.yaml
```

Cas central : un seul stack suffit, 42,7 g CO2-éq/km, et la hausse due au vieillissement tombe à +3,7 % (au lieu de +31,1 % dans la référence). Le fichier `mon_cas.yaml` documente entièrement le cas : n'importe qui peut le relancer et obtenir le même résultat.

### 7. Tester une autre loi de vieillissement

**Exemple : un modélisateur qui pense que la résistance de la pile augmente comme la racine carrée du temps, et non linéairement.** Il écrit sa loi, la branche à la place de la loi d'origine, puis remet l'originale :

```python
import numpy as np
from h2ageing import pemfc

original_law = pemfc.FuelCell.resistance

def my_resistance(self, t, p):
    """Résistance en racine carrée du temps ; même valeur que la loi linéaire à 1 000 h."""
    t = np.asarray(t, float)
    return self.R0 * (1 + p.get("k_R", 0.0) * 1000 * np.sqrt(t / 1000))

pemfc.FuelCell.resistance = my_resistance
r = run(cfg)
pemfc.FuelCell.resistance = original_law
```

Cas pessimiste : avec cette loi, la résistance augmente plus lentement après les 1 000 h de l'essai ; la fin de vie passe à 6 370 h, un seul stack suffit, et la hausse de la chaîne vaut +13,0 %. Seule la loi a été écrite ; la tension à chaque âge, la fin de vie, la consommation d'hydrogène, le nombre de stacks et l'ACV sont recalculés.

### 8. Quelles entrées comptent le plus, toutes ensemble ?

**Pourquoi se poser la question :** les exemples ci-dessus changent une entrée à la fois. L'analyse de sensibilité globale change huit entrées ensemble et les classe.

**Ce qu'est l'analyse de Sobol.** Elle fait varier toutes les entrées en même temps, un grand nombre de fois (10 240 calculs), et mesure la part de la variation du résultat expliquée par chaque entrée. Son indice total va de 0 (l'entrée ne compte pas) à 1 (l'entrée explique toute la variation, seule ou avec les autres).


```bash
python scripts/sobol.py --out results      # environ 15 min sur 2 cœurs
```

**Ce que ça montre :** l'impact absolu dépend surtout de la source d'électricité (indice de Sobol total 0,78) ; la hausse due au vieillissement dépend presque seulement de la durée de vie du stack de pile (0,94). Les facteurs et leurs plages sont dans `global_sensitivity` de `config/default.yaml`.

### 9. Et si le dernier stack a une seconde vie ?

**Pourquoi se poser la question :** la référence compte chaque stack commencé comme un stack entier (`integer`). Si la vie restante du dernier stack est utilisée ailleurs, seule la part de vie utilisée devrait être comptée (`prorata`).

```bash
python scripts/run.py --set usage.stack_counting=prorata
```

| | Optimiste | Central | Pessimiste |
|---|---|---|---|
| Hausse, comptage entier (référence) | +5,0 % | +31,1 % | +35,0 % |
| Hausse, comptage au prorata | +4,6 % | +14,7 % | +32,8 % |

**Ce que ça montre :** seul le cas central change beaucoup, car son second stack de pile n'est utilisé qu'à 35 % avant la fin de l'horizon. Le prorata est une borne basse : il suppose une filière de seconde vie qui n'existe pas aujourd'hui pour ces stacks.
