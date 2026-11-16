# Utiliser et adapter le modèle

[English](ADAPT.md) | **Français**

Cette page montre comment une autre personne peut utiliser ce modèle pour sa propre question, du simple lancement jusqu'au remplacement d'une loi de vieillissement. Chaque niveau est accompagné d'un exemple et du résultat qu'il donne avec les données fournies. Vous n'écrivez que ce que vous changez : la recherche de la fin de vie, le comptage des stacks et l'ACV sont recalculés automatiquement.

Les mêmes exemples, prêts à lancer dans Jupyter : [`examples/adapt_the_model.fr.ipynb`](../examples/adapt_the_model.fr.ipynb).

| Niveau | Vous voulez… | Vous changez | Utilisateur type |
|---|---|---|---|
| 1 | reproduire les résultats | rien | étudiant, relecteur |
| 2 | poser une question au modèle | une ou quelques entrées, en ligne de commande ou en Python | praticien de l'ACV |
| 3 | décrire votre propre cas | une copie du fichier de configuration | ingénieur, porteur de projet |
| 4 | utiliser vos propres mesures de vieillissement | les constantes des modèles de vieillissement | chercheur sur la dégradation |
| 5 | tester une autre loi de vieillissement | une fonction Python | modélisateur |
| 6 | utiliser vos propres équipements ou inventaires | les fichiers de données | constructeur, praticien de l'ACV |

Installation, une seule fois (Python 3.10 ou plus récent) :

```bash
git clone https://github.com/Ayabh12/h2-ageing-lca
cd h2-ageing-lca
pip install -r requirements.txt
```

En Python ou dans Jupyter, depuis le dossier qui contient `h2-ageing-lca` :

```python
import sys
sys.path.insert(0, "h2-ageing-lca/src")
from h2ageing import load_config, with_values, run

cfg = load_config()          # toutes les entrées, lues dans config/default.yaml
```

---

## Niveau 1 : reproduire les résultats

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

## Niveau 2 : poser une question au modèle

**Exemple : « et si mon stack de pile dure 5 000 h ? »** `with_values` renvoie une copie de la configuration avec les valeurs que vous donnez ; le fichier de configuration n'est pas modifié.

```python
r = run(with_values(cfg, **{"cases.central.fuel_cell.hours_to_end_of_life": 5000.0}))
r["chain"][["case", "total_g_per_km", "rise_pct"]].round(1)
```

Cas central : 2 stacks, 97,4 g CO2-éq/km, +31,4 %. Presque comme avec 4 100 h, car un stack qui dure 5 000 h s'arrête encore avant les 5 554 heures de fonctionnement du véhicule.

**La question suivante, naturelle : « à partir de quelle durée de vie un seul stack suffit-il ? »**

```python
for d in [3000, 4100, 5000, 5554, 6000, 7000]:
    x = run(with_values(cfg, **{"cases.central.fuel_cell.hours_to_end_of_life": float(d)}))
    stacks = x["life"].set_index("case").loc["central", "fuel_cell_stacks"]
    rise = x["chain"].set_index("case").loc["central", "rise_pct"]
    print(f"{d} h -> {stacks:.0f} stack(s), chain rise +{rise:.1f} %")
```

| Durée de vie du stack | Stacks | Hausse de la chaîne |
|---|---|---|
| 3 000 h | 2 | +31,4 % |
| 4 100 h | 2 | +31,1 % |
| 5 000 h | 2 | +31,4 % |
| 5 554 h | 2 | +31,6 % |
| 6 000 h | 1 | +6,4 % |
| 7 000 h | 1 | +6,0 % |

La réponse est un seuil : en dessous de 5 554 h, le résultat bouge à peine ; au-dessus, il tombe de +31,6 % à +6,4 %.

La même chose en ligne de commande : `python scripts/run.py --set cases.central.fuel_cell.hours_to_end_of_life=5000`. D'autres questions de ce type, avec leurs résultats : [USE_CASES.fr.md](USE_CASES.fr.md).

## Niveau 3 : décrire votre propre cas dans un fichier de configuration

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

## Niveau 4 : utiliser vos propres constantes de vieillissement

**Exemple : un chercheur qui a mesuré, sur sa propre cellule, une perte de tension de 27 mV à 1,8 A/cm² après 1 000 h** (au lieu de 45 mV pour la cellule utilisée dans le cas pessimiste) :

```python
r = run(with_values(cfg, **{"cases.pessimistic.fuel_cell.voltage_loss_at_1p8_A_cm2_1000h_V": 0.027}))
r["life"][["case", "fuel_cell_end_of_life_h", "fuel_cell_stacks"]].round(0)
```

Cas pessimiste : la fin de vie passe de 2 895 h à 5 652 h, un seul stack suffit, et la hausse de la chaîne tombe de +35,0 % à +12,8 %.

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

## Niveau 5 : tester une autre loi de vieillissement

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

| Loi | Fonction à remplacer | Arguments (âge `t` en heures, paramètres `p`) |
|---|---|---|
| Surface de platine de la pile | `pemfc.FuelCell.ecsa` | `t`, `p` |
| Résistance de la pile | `pemfc.FuelCell.resistance` | `t`, `p` |
| Crossover de la pile | `pemfc.FuelCell.crossover` | `t`, `p` |
| Vieillissement de l'électrolyseur (tension, résistance, rendement faradique) | `pemwe.Electrolyser.state` | `t`, `p` |
| Perméation du réservoir | `tank.Tank.permeation` | `t_years` (années), `p` |

Pour garder une nouvelle loi définitivement, écrivez-la dans le module et ajoutez une nouvelle valeur `model:` dans `parameters()` ([CUSTOMISE.fr.md](CUSTOMISE.fr.md), section 6).

## Niveau 6 : utiliser vos propres équipements, mesures ou inventaires

| Vous avez | Remplacez | Puis |
|---|---|---|
| des mesures de polarisation d'une autre pile ou d'un autre électrolyseur | les fichiers de `data/measurements/` | `python scripts/fit_pemfc.py` ou `fit_pemwe.py` |
| un autre inventaire de fabrication | les quantités de `data/inventories/` | `python scripts/build_fabrication_brightway.py` (nécessite ecoinvent) |
| des impacts tirés d'une autre base ou d'une autre méthode | les fichiers de `data/impacts/` | rien : ils sont lus directement |
| une autre source d'électricité | une nouvelle colonne dans `data/impacts/electricity_per_kWh.csv` | utilisez son nom dans `usage.electricity_electrolyser` |

Détails pour chaque fichier : [CUSTOMISE.fr.md](CUSTOMISE.fr.md) et [data/README.fr.md](../data/README.fr.md).

---

## Vérifier et partager vos changements

- **Vérifier.** `python tests/test_reference_results.py` vérifie que la configuration par défaut redonne les résultats de référence. Lancez-le avant de changer le code ; après le changement d'une loi, il doit échouer, puisque les résultats changent.
- **Poser une question ou signaler une erreur.** Ouvrez une *Issue* sur GitHub (onglet *Issues*, *New issue*). Questions et réponses restent publiques, donc la personne suivante les trouve.
- **Garder votre propre version en ligne.** Cliquez sur *Fork* sur GitHub : vous obtenez votre propre copie du dépôt, que vous pouvez modifier librement. Elle affiche « forked from Ayabh12/h2-ageing-lca ».
- **Proposer une amélioration.** Depuis votre fork, ouvrez une *Pull request*. Les changements sont relus avant d'être intégrés ; les nouvelles données de dégradation mesurées sur des stacks commerciaux sont particulièrement bienvenues.

Personne ne peut modifier ce dépôt sans l'accord de sa propriétaire : les forks et les copies locales sont indépendants.
