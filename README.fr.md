# h2-ageing-lca

[English](README.md) | **Français**

**De combien le vieillissement des stacks change-t-il l'analyse du cycle de vie d'une chaîne de mobilité hydrogène ?**

[![tests](https://github.com/Ayabh12/h2-ageing-lca/actions/workflows/tests.yml/badge.svg)](https://github.com/Ayabh12/h2-ageing-lca/actions/workflows/tests.yml)
Code : MIT · Données : CC BY 4.0

Ce dépôt contient les modèles, les données et le code d'une analyse du cycle de vie (ACV) qui tient compte du vieillissement des stacks électrochimiques d'une chaîne hydrogène : un électrolyseur PEM, la compression, un réservoir de type IV et une pile à combustible PEM. Chaque résultat se recalcule avec une seule commande, et chaque valeur d'entrée se change dans un seul fichier de configuration.

---

## Sommaire

1. [Pourquoi c'est important](#1-pourquoi-cest-important)
2. [Ce que fait le code](#2-ce-que-fait-le-code)
3. [Qui peut l'utiliser, et pour quoi](#3-qui-peut-lutiliser-et-pour-quoi)
4. [Démarrage rapide](#4-démarrage-rapide)
5. [L'utiliser et l'adapter : six niveaux, avec exemples](#5-lutiliser-et-ladapter--six-niveaux-avec-exemples)
6. [Reproduire chaque résultat](#6-reproduire-chaque-résultat)
7. [Organisation du dépôt](#7-organisation-du-dépôt)
8. [Données et ecoinvent](#8-données-et-ecoinvent)
9. [Limites](#9-limites)
10. [Résultats principaux](#10-résultats-principaux)
11. [Citer, licence, contact](#11-citer-licence-contact)

Documentation complémentaire : [méthode](docs/METHOD.fr.md) · [utiliser et adapter le modèle](docs/ADAPT.fr.md) · [exemples commentés](docs/USE_CASES.fr.md) · [changer une valeur d'entrée](docs/CUSTOMISE.fr.md) · [limites et domaine de validité](docs/LIMITS.fr.md) · [données](data/README.fr.md) · [notebooks de recherche](notebooks/README.fr.md)

---

## 1. Pourquoi c'est important

La plupart des ACV de la mobilité hydrogène traitent l'électrolyseur et la pile à combustible comme s'ils ne vieillissaient jamais : le même rendement pendant 15 ans et un seul stack. En réalité, un stack perd en performance avec l'usage et doit être remplacé en fin de vie. Ignorer ce phénomène sous-estime l'impact, mais on ne savait pas de combien.

Ce dépôt répond à deux questions :

- **De combien ?** La hausse de l'impact due au vieillissement, pour chaque composant seul et pour la chaîne complète.
- **Par quelle voie ?** Le vieillissement agit de deux façons, calculées séparément :
  1. **la surconsommation** : un électrolyseur vieilli consomme plus d'électricité par kg d'hydrogène, et une pile vieillie plus d'hydrogène par km ;
  2. **le remplacement** : un stack en fin de vie (variation de tension de 10 %, critère du DOE) est remplacé par un neuf, qu'il faut fabriquer.

## 2. Ce que fait le code

```
source d'électricité -> électrolyseur PEM -> compression -> réservoir type IV -> pile PEM
(au choix)              Nel MC250, 1,25 MW   700 bar        142,2 L             Toyota Mirai II
```

1. **Performance de référence tirée de mesures.** Un modèle de polarisation est ajusté sur un profil de fonctionnement éolien mesuré d'un électrolyseur Nel MC250 (données publiques du NLR) et sur des mesures sur route de la pile d'une Toyota Mirai II. Le profil éolien décrit *comment* l'électrolyseur fonctionne ; il ne fixe pas l'origine de l'électricité, qui est une entrée séparée (mix résiduel français par défaut).
2. **Vieillissement dans trois cas.** Optimiste et central : modèle linéaire, avec des vitesses publiées par le DOE américain. Pessimiste : modèle semi-empirique, avec des constantes mesurées sur des cellules de laboratoire (perte de surface de platine, hausse de la résistance, crossover, activité de l'anode, amincissement de la membrane). Il est dit semi-empirique car sa structure est physique, chaque mécanisme de dégradation agissant sur un terme de l'équation de polarisation, alors que ses lois d'évolution dans le temps sont ajustées sur des mesures de laboratoire. La perméation du réservoir augmente sur 15 ans.
3. **Fin de vie et nombre de stacks.** Un stack atteint sa fin de vie quand sa tension a varié de 10 % par rapport à l'état neuf (critère du DOE) : pour la pile, une perte de tension de 10 % à 300 A ; pour l'électrolyseur, une hausse de tension de 10 % à la densité de courant moyenne du profil. Le modèle cherche l'âge auquel chaque stack atteint ce critère, puis compte les stacks nécessaires sur 15 ans.
4. **ACV.** Les flux de la phase d'usage et la fabrication des stacks et du réservoir sont combinés avec des impacts caractérisés (ecoinvent 3.11 cut-off, EF 3.1, 16 catégories). La fabrication est comptée du berceau à la porte de l'usine : extraction des ressources, transformation des matériaux, énergie et transports de ces étapes, et électricité de l'usine ; la fin de vie n'est pas comptée ([ce que comprend chaque impact](docs/METHOD.fr.md#ce-que-comprend-chaque-impact)). Les résultats sont donnés pour chaque composant seul et pour la chaîne complète, avec et sans vieillissement.

La méthode complète, avec chaque équation et sa source, est dans [docs/METHOD.fr.md](docs/METHOD.fr.md).

## 3. Qui peut l'utiliser, et pour quoi

| Vous êtes | Ce que vous pouvez faire | Par où commencer |
|---|---|---|
| **Praticien de l'ACV** | Ajouter le vieillissement à une ACV de la mobilité hydrogène ; tester votre propre mix électrique, horizon, inventaire ou règle de comptage des stacks | [docs/USE_CASES.fr.md](docs/USE_CASES.fr.md), exemples 1 à 4 |
| **Ingénieur ou constructeur** | Voir ce que vaut, en CO2-éq, un stack qui dure plus longtemps ou qui se dégrade moins vite ; trouver la durée de vie qui évite un remplacement | `scripts/threshold.py`, exemple 5 |
| **Chercheur sur la dégradation** | Brancher vos propres constantes ou votre propre loi de vieillissement et voir l'effet sur l'ACV, sans réécrire l'ACV | [docs/ADAPT.fr.md](docs/ADAPT.fr.md), niveaux 4 et 5 |
| **Étudiant** | Lire un petit modèle complet d'ACV avec vieillissement, le lancer et le modifier pas à pas | [docs/METHOD.fr.md](docs/METHOD.fr.md), puis les notebooks |

Pourquoi partir de ce dépôt plutôt que de zéro : les modèles de vieillissement, la recherche de la fin de vie, le comptage des stacks et l'ACV sont déjà reliés, donc changer une entrée met à jour automatiquement tout ce qui en dépend ; et chaque entrée est reliée à sa source dans un seul fichier.

## 4. Démarrage rapide

Prérequis : Python 3.10 ou plus récent, et Git (ou téléchargez le dépôt en ZIP : bouton vert **Code**, **Download ZIP**). Aucune licence ecoinvent n'est nécessaire pour lancer le modèle.

**Dans un terminal** (Anaconda Prompt, PowerShell, terminal macOS ou Linux) :

```bash
git clone https://github.com/Ayabh12/h2-ageing-lca
cd h2-ageing-lca
pip install -r requirements.txt
python scripts/run.py                    # configuration par défaut, environ 2 s
python tests/test_reference_results.py   # 8 tests : la configuration par défaut redonne les résultats de référence
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

Dans Jupyter, `!` lance une commande du terminal, `%cd` entre dans un dossier, et `{sys.executable}` désigne le Python du notebook. Si le dossier existe déjà, lancez seulement `import sys` puis `%cd h2-ageing-lca-main`. Un notebook prêt à lancer est aussi dans [examples/adapt_the_model.fr.ipynb](examples/adapt_the_model.fr.ipynb).

`scripts/run.py` affiche les tableaux de résultats de la [section 10](#10-résultats-principaux) et les écrit en fichiers CSV (`--out <dossier>`). Pour changer une valeur depuis le terminal (dans Jupyter, remplacez `python` par `!{sys.executable}`) :

```bash
python scripts/run.py --set usage.electricity_electrolyser=wind_FR
python scripts/run.py --set cases.central.fuel_cell.hours_to_end_of_life=6000
```

ou copiez `config/default.yaml`, modifiez-le, et lancez `python scripts/run.py --config config/mon_cas.yaml`. Depuis Python ou Jupyter, une fois dans le dossier du dépôt, `h2-ageing-lca` ou `h2-ageing-lca-main` (le dossier `src` doit être visible depuis l'endroit où le code tourne) :

```python
import sys; sys.path.insert(0, "src")
from h2ageing import load_config, with_values, run

cfg = with_values(load_config(), **{"usage.electricity_electrolyser": "wind_FR"})
print(run(cfg)["chain"])
```

## 5. L'utiliser et l'adapter : six niveaux, avec exemples

Chacun peut utiliser le modèle pour sa propre question sans le réécrire : on ne change que ce qui diffère dans son cas, et la fin de vie, le nombre de stacks et l'ACV sont recalculés. Exemples avec les données fournies (changement climatique, chaîne complète, cas central sauf mention contraire) :

| Niveau | Exemple de question | Ce que vous écrivez | Réponse |
|---|---|---|---|
| 1. Reproduire | « Est-ce que je retrouve les valeurs publiées ? » | `run(load_config())` | 74,1 g/km sans vieillissement, +31,1 % avec vieillissement |
| 2. Poser une question | « Et si mon stack de pile dure 5 000 h ? » | `with_values(cfg, **{"cases.central.fuel_cell.hours_to_end_of_life": 5000.0})` | toujours 2 stacks, +31,4 % : un seul stack suffit seulement au-delà de 5 554 h |
| 3. Votre propre cas | « Mon stack dure 7 000 h et mon électrolyseur fonctionne à l'électricité éolienne » | une copie de `config/default.yaml` avec deux valeurs changées | 1 stack, 42,7 g/km, +3,7 % |
| 4. Vos propres constantes | « J'ai mesuré 27 mV de perte à fort courant, pas 45 mV » (cas pessimiste) | une clé du modèle semi-empirique | fin de vie 5 652 h au lieu de 2 895 h, +12,8 % au lieu de +35,0 % |
| 5. Votre propre loi | « La résistance augmente comme la racine carrée du temps » (cas pessimiste) | une fonction Python de quatre lignes | fin de vie 6 370 h, 1 stack, +13,0 % |
| 6. Vos propres données | « J'ai des mesures ou un inventaire d'un autre stack » | les fichiers de `data/` | réajuster ou reconstruire, puis lancer |

```python
import sys; sys.path.insert(0, "src")
from h2ageing import load_config, with_values, run

cfg = load_config()
r = run(with_values(cfg, **{"cases.central.fuel_cell.hours_to_end_of_life": 5000.0}))   # niveau 2
print(r["chain"][["case", "total_g_per_km", "rise_pct"]])
```

Le code de chaque niveau, expliqué : [docs/ADAPT.fr.md](docs/ADAPT.fr.md). Le même, prêt à lancer dans Jupyter : [examples/adapt_the_model.fr.ipynb](examples/adapt_the_model.fr.ipynb). Pour poser une question, ouvrez une *Issue* ; pour garder votre propre version en ligne, faites un *Fork* du dépôt ; pour proposer une amélioration, ouvrez une *Pull request* depuis votre fork.

## 6. Reproduire chaque résultat

| Résultat | Commande | Durée |
|---|---|---|
| Trois cas : fin de vie, stacks, chaque composant, chaîne complète, 16 catégories | `python scripts/run.py --out results` | ~2 s |
| Vérification par rapport aux valeurs de référence | `python tests/test_reference_results.py` (lancé aussi automatiquement à chaque envoi) | ~10 s |
| Diagramme en barres de la chaîne par poste (après `run.py`) | `python scripts/plot.py --results results` | ~2 s |
| Sources d'électricité, heures de l'électrolyseur, comptage des stacks | `run.py` avec `--set` (voir [docs/USE_CASES.fr.md](docs/USE_CASES.fr.md)) | ~2 s chacun |
| Impact en fonction de la durée de vie du stack (paliers et seuils) | `python scripts/threshold.py --out results` | ~30 s |
| Loi de crossover du modèle semi-empirique de la pile, vitesse moyenne | `python scripts/fuel_cell_tests.py` | ~10 s |
| Effet de chaque constante semi-empirique (autres valeurs publiées) | `python scripts/semi_empirical_constants.py` | ~5 s |
| Sensibilité globale (indices de Sobol, 10 240 calculs) | `python scripts/sobol.py --out results` | ~15 min (2 cœurs) |
| Ajustements de polarisation (ils réécrivent `data/parameters/` et redonnent les paramètres fournis) | `python scripts/fit_pemfc.py`, `python scripts/fit_pemwe.py` | ~5 s chacun |
| Impacts de fabrication à partir des inventaires | `python scripts/build_fabrication_brightway.py --project <nom>` (nécessite ecoinvent) | – |

Les notebooks de recherche d'origine (en français, sorties comprises) sont dans [notebooks/](notebooks/README.fr.md) ; ils donnent les mêmes résultats, avec plus de figures.

## 7. Organisation du dépôt

```
config/default.yaml        toutes les entrées, chacune avec sa source (unités dans le nom des clés)
src/h2ageing/              les modèles (paquet Python)
    pemfc.py               pile : polarisation, vieillissement (linéaire et semi-empirique), trajet à puissance imposée
    pemwe.py               électrolyseur : profil de fonctionnement, vieillissement (linéaire et semi-empirique)
    tank.py                perméation du réservoir de type IV
    impacts.py             données d'impact EF 3.1 et score unique
    chain.py               ACV de chaque composant et de la chaîne complète
    run.py                 lance tous les cas, construit les tableaux de résultats
scripts/                   outils en ligne de commande (voir section 5)
data/
    measurements/          mesures sur route de la pile, profil éolien de l'électrolyseur
    parameters/            paramètres de polarisation ajustés
    inventories/           inventaires de premier plan (masses, énergie, noms des activités ecoinvent)
    impacts/               impacts caractérisés (par kWh, par kg d'eau, par stack ou réservoir)
tests/                     résultats de référence et tests qui les vérifient
notebooks/                 notebooks de recherche d'origine (en français)
docs/                      méthode, utilisation et adaptation, exemples, personnalisation, limites
examples/                  notebook Jupyter : utiliser et adapter le modèle en six niveaux
```

## 8. Données et ecoinvent

Aucune donnée ecoinvent n'est distribuée, conformément à sa licence. `data/impacts` ne contient que des résultats caractérisés (impact d'1 kWh, d'1 kg d'eau, d'un stack ou d'un réservoir fabriqué), ce qui suffit pour obtenir tous les résultats. Les inventaires de premier plan, avec l'activité ecoinvent utilisée pour chaque flux, sont dans `data/inventories` ; avec votre propre licence ecoinvent, `scripts/build_fabrication_brightway.py` recalcule les impacts de fabrication après que vous avez changé une quantité. Sources et licences de chaque fichier : [data/README.fr.md](data/README.fr.md).

## 9. Limites

Le modèle dit clairement ce qu'il ne sait pas ; les limites principales sont ci-dessous, et [docs/LIMITS.fr.md](docs/LIMITS.fr.md) donne chacune avec son effet sur les résultats et la façon de la tester.

- **Aucune vitesse de dégradation n'est publiée pour les deux stacks étudiés.** Les trois cas encadrent le vieillissement avec des valeurs publiées pour d'autres équipements ; ils ne prédisent pas le vieillissement exact de ces stacks.
- **Les constantes pessimistes viennent de cellules de laboratoire**, plus sollicitées que des stacks commerciaux, et les lois semi-empiriques sont extrapolées au-delà de la durée des essais.
- **Un seul trajet et un seul profil éolien pour la phase d'usage.** La courbe de polarisation de la pile est ajustée sur les 12 enregistrements sur route, mais la consommation d'hydrogène sur la vie du véhicule est simulée en rejouant, à chaque âge, un seul trajet mesuré (type WLTP, 2 033 s, 20,32 km) ; l'électrolyseur rejoue un profil éolien de 4 heures. Les températures sont constantes.
- **Périmètre : stacks et réservoir seulement.** Les auxiliaires, la station hors compression, le reste du véhicule et la fin de vie sont hors du système.

## 10. Résultats principaux

Ces résultats découlent de la méthode de la [section 2](#2-ce-que-fait-le-code) (détails dans [docs/METHOD.fr.md](docs/METHOD.fr.md)) et sont valables dans les limites de la [section 9](#9-limites). « Sans vieillissement » désigne la même chaîne avec des stacks qui ne vieillissent jamais : un stack de chaque convertisseur, des performances constantes.

Configuration par défaut : changement climatique (EF 3.1), mix résiduel français (79,6 g CO2-éq/kWh, données AIB 2024), 200 000 km en 15 ans.

| | Sans vieillissement | Optimiste | Central | Pessimiste |
|---|---|---|---|---|
| Stacks de pile sur 15 ans | 1 | 1 | 2 | 2 |
| Stacks d'électrolyseur sur 15 ans | 1 | 2 | 3 | 3 |
| Électrolyseur seul (kg CO2-éq/kg H2) | 4,31 | 4,53 (+5,1 %) | 4,57 (+5,9 %) | 4,66 (+8,2 %) |
| Réservoir seul (g CO2-éq/km) | 11,89 | 11,89 (0,0 %) | 12,04 (+1,3 %) | 12,64 (+6,4 %) |
| Pile seule (g CO2-éq/km) | 61,9 | 63,4 (+2,4 %) | 82,2 (+32,8 %) | 83,4 (+34,6 %) |
| **Chaîne complète (g CO2-éq/km)** | **74,1** | **77,8 (+5,0 %)** | **97,2 (+31,1 %)** | **100,1 (+35,0 %)** |

La hausse due au vieillissement, séparée selon ses deux voies. Chaque ligne donne la part de la hausse due à une voie, en % de l'impact sans vieillissement ; les deux lignes s'additionnent pour donner la hausse totale (à 0,1 près, à cause des arrondis).

| Composant | Voie | Optimiste | Central | Pessimiste |
|---|---|---|---|---|
| Électrolyseur seul | surconsommation (plus d'électricité et d'eau par kg) | +4,3 % | +4,3 % | +6,6 % |
| | remplacement (stacks en plus) | +0,8 % | +1,5 % | +1,5 % |
| | **les deux** | **+5,1 %** | **+5,9 %** | **+8,2 %** |
| Réservoir seul | surconsommation (hydrogène perdu par perméation) | 0,0 % | +1,3 % | +6,4 % |
| | remplacement (un seul réservoir dans tous les cas) | 0,0 % | 0,0 % | 0,0 % |
| | **les deux** | **0,0 %** | **+1,3 %** | **+6,4 %** |
| Pile seule | surconsommation (plus d'hydrogène par km) | +2,4 % | +2,9 % | +4,8 % |
| | remplacement (stack en plus) | 0,0 % | +29,9 % | +29,9 % |
| | **les deux** | **+2,4 %** | **+32,8 %** | **+34,6 %** |
| Chaîne complète | surconsommation (électricité, eau et compression) | +4,6 % | +5,2 % | +9,1 % |
| | remplacement (stacks de pile et d'électrolyseur) | +0,5 % | +25,9 % | +25,9 % |
| | **les deux** | **+5,0 %** | **+31,1 %** | **+35,0 %** |

Ce que montrent ces chiffres :

- **La pile est dominée par le remplacement.** Un stack de pile est réparti sur les 200 000 km d'un seul véhicule ; un second stack ajoute 18,5 g CO2-éq/km, soit 30 % de l'impact de la pile sans vieillissement (61,9 g/km). Dans le cas central, 91 % de la hausse de la pile vient du stack en plus.
- **L'électrolyseur est dominé par la surconsommation.** Un stack d'électrolyseur est réparti sur environ 1,19 million de kg d'hydrogène et pèse 0,8 % de l'impact d'1 kg ; l'électricité en plus compte davantage.
- **Le résultat évolue par paliers.** Toute fin de vie de la pile comprise entre la moitié de l'horizon et l'horizon donne deux stacks ; la durée de vie exacte compte peu à l'intérieur d'un palier et beaucoup à ses bords.
- **La durée de vie de la pile est l'entrée clé.** Dans l'analyse de sensibilité globale, elle explique presque toute la variation de la hausse (indice de Sobol total 0,94).
- **Une électricité plus propre fait peser davantage le vieillissement, en valeur relative.** Les stacks de remplacement ajoutent le même impact quelle que soit l'électricité ; avec l'électricité éolienne, la hausse de la chaîne dans le cas central est de +48,6 % au lieu de +31,1 %.

## 11. Citer, licence, contact

- **Citer :** voir [CITATION.cff](CITATION.cff) (GitHub affiche un bouton « Cite this repository »).
- **Licence :** code sous licence MIT ([LICENSE](LICENSE)) ; données et documentation sous CC BY 4.0 ([LICENSE-DATA.md](LICENSE-DATA.md)). Les sources tierces gardent leurs propres conditions ([data/README.fr.md](data/README.fr.md)).
- **Questions, erreurs ou nouvelles données :** ouvrez une *Issue* sur GitHub. Les données de dégradation mesurées sur des stacks commerciaux sont particulièrement bienvenues, car elles remplaceraient les cas d'encadrement par une mesure.
