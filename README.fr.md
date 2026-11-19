# h2-ageing-lca

[English](README.md) | **Français**

**De combien le vieillissement des stacks change-t-il l'analyse du cycle de vie d'une chaîne de mobilité hydrogène ?**

[![tests](https://github.com/Ayabh12/h2-ageing-lca/actions/workflows/tests.yml/badge.svg)](https://github.com/Ayabh12/h2-ageing-lca/actions/workflows/tests.yml)
Code : MIT · Données : CC BY 4.0

Ce dépôt contient les modèles, les données et le code d'une analyse du cycle de vie (ACV) qui tient compte du vieillissement des stacks électrochimiques d'une chaîne hydrogène : un électrolyseur PEM, la compression, un réservoir de type IV et une pile à combustible PEM. Chaque résultat se recalcule avec une seule commande, et chaque valeur d'entrée se change dans un seul fichier de configuration.

---

## Sommaire

1. [Pourquoi c'est important](#1-pourquoi-cest-important)
2. [Qui peut l'utiliser, et pour quoi](#2-qui-peut-lutiliser-et-pour-quoi)
3. [Ce que fait le code](#3-ce-que-fait-le-code)
4. [Démarrage rapide, sans et avec licence ecoinvent](#4-démarrage-rapide-sans-et-avec-licence-ecoinvent)
5. [Organisation du dépôt et documentation](#5-organisation-du-dépôt-et-documentation)
6. [Résultats principaux](#6-résultats-principaux)
7. [Citer, licence, contact](#7-citer-licence-contact)

---

## 1. Pourquoi c'est important

La plupart des ACV de la mobilité hydrogène traitent l'électrolyseur et la pile à combustible comme s'ils ne vieillissaient jamais : le même rendement pendant 15 ans et un seul stack. En réalité, un stack perd en performance avec l'usage et doit être remplacé en fin de vie. Ignorer ce phénomène sous-estime l'impact, mais on ne savait pas de combien.

Ce dépôt répond à deux questions :

- **De combien ?** La hausse de l'impact due au vieillissement, pour chaque composant seul et pour la chaîne complète.
- **Par quelle voie ?** Le vieillissement agit à deux niveaux :
  1. **La surconsommation** : la pile vieillie consomme plus d'hydrogène par km, l'électrolyseur plus d'électricité par kg, et le réservoir perd plus d'hydrogène.
  2. **Le remplacement** : un stack est remplacé quand sa tension a varié de 10 % (critère du DOE) ; chaque stack neuf ajoute son impact de fabrication.

**Le résultat en bref.** Sur la vie du véhicule (15 ans, 200 000 km), le vieillissement des stacks augmente l'impact de la chaîne sur le changement climatique, par rapport à la même chaîne sans vieillissement, de **+5,0 %** (cas optimiste, objectifs du DOE), **+31,1 %** (cas central, état actuel mesuré par le DOE) et **+35,0 %** (cas pessimiste, modèle semi-empirique et constantes de laboratoire).

**Ce que ce dépôt apporte**

- **Une méthode prête à l'emploi.** Les modèles de vieillissement, la recherche de la fin de vie, le comptage des stacks et l'ACV sont déjà reliés entre eux, et chaque équation est documentée avec sa source ([docs/METHOD.fr.md](docs/METHOD.fr.md)).
- **N'importe quelle valeur ou n'importe quel inventaire se change sans réécrire le code.** Les valeurs d'entrée sont dans un seul fichier de configuration, les inventaires de fabrication dans des tableaux CSV ; après un changement, la fin de vie, le nombre de stacks et l'impact sont recalculés automatiquement.
- **Des modèles construits sur des mesures réelles** : une pile de Toyota Mirai II enregistrée sur route, et un électrolyseur Nel MC250 qui suit un profil de production éolienne (données publiques du NLR).
- **Utilisable sans licence ecoinvent**, et complet avec une licence : les deux façons de faire sont décrites pas à pas ([section 4](#4-démarrage-rapide-sans-et-avec-licence-ecoinvent)).
- **Des résultats contrôlés automatiquement** : des tests vérifient les résultats à chaque modification du dépôt.
- **Ouvert et bilingue** : chaque page existe en français et en anglais, et n'importe qui peut reproduire les résultats ou tester son propre cas.

## 2. Qui peut l'utiliser, et pour quoi

| Vous êtes | Ce que vous pouvez faire | Par où commencer |
|---|---|---|
| **Praticien de l'ACV** | Ajouter le vieillissement à une ACV de la mobilité hydrogène ; tester votre propre mix électrique, horizon, inventaire ou règle de comptage des stacks | [docs/GUIDE.fr.md](docs/GUIDE.fr.md#5-exemples-commentés), exemples 1 à 3 et 9 |
| **Ingénieur ou constructeur** | Voir ce que vaut, en CO2-éq, un stack qui dure plus longtemps ou qui se dégrade moins vite ; trouver la durée de vie qui évite un remplacement | `scripts/threshold.py`, exemple 4 |
| **Chercheur sur la dégradation** | Brancher vos propres constantes ou votre propre loi de vieillissement et voir l'effet sur l'ACV, sans réécrire l'ACV | [docs/GUIDE.fr.md](docs/GUIDE.fr.md#5-exemples-commentés), exemples 5 et 7 |
| **Étudiant** | Lire un petit modèle complet d'ACV avec vieillissement, le lancer et le modifier pas à pas | [docs/METHOD.fr.md](docs/METHOD.fr.md), puis les notebooks |

## 3. Ce que fait le code

```mermaid
flowchart TB
    subgraph E["Entrées · config/default.yaml et data/"]
        direction LR
        e1["Mesures<br/>profil éolien du Nel MC250<br/>trajets sur route de la Mirai II"]
        e2["Trois cas de vieillissement<br/>optimiste · central · pessimiste"]
        e3["Inventaires de fabrication<br/>stacks et réservoir"]
        e4["Impacts caractérisés<br/>ecoinvent 3.11 · EF 3.1"]
        e1 ~~~ e2 ~~~ e3 ~~~ e4
    end

    subgraph C["La chaîne étudiée · reliée par le kg d'hydrogène"]
        direction LR
        c1["Électricité<br/>au choix"] -->|"kWh par kg H₂"| c2["Électrolyseur PEM<br/>Nel MC250, 1,25 MW"] -->|"kg H₂"| c3["Compression<br/>700 bar"] -->|"kg H₂"| c4["Réservoir type IV<br/>142,2 L"] -->|"kg H₂"| c5["Pile PEM<br/>Toyota Mirai II"] -->|"kg H₂ par km"| c6(["1 km parcouru"])
    end

    subgraph M["Ce que calcule le code · ★ apport de ce travail"]
        direction LR
        m1["1 · Performance<br/>de référence"] --> m2["★ 2 · Vieillissement<br/>sur 15 ans, trois cas"] --> m3["★ 3 · Fin de vie<br/>et nombre de stacks"] --> m4["★ 4 · ACV du vieillissement<br/>surconsommation + remplacement"]
    end

    subgraph R["Résultats"]
        direction LR
        r1["Chaque composant<br/>et la chaîne complète"]
        r2["★ Hausse due au vieillissement<br/>avec / sans, 16 catégories EF 3.1"]
        r3["Tests de sensibilité"]
        r1 ~~~ r2 ~~~ r3
    end

    E --> C --> M --> R

    classDef inp fill:#e8f0fa,stroke:#3b6ea5,color:#1d2b3a
    classDef chain fill:#fdf1dc,stroke:#c9892b,color:#3a2a10
    classDef code fill:#ece6f6,stroke:#6c4fa3,color:#2a1d40
    classDef res fill:#e3f1e3,stroke:#3d8b3d,color:#163016
    class e1,e2,e3,e4 inp
    class c1,c2,c3,c4,c5,c6 chain
    class m1,m2,m3,m4 code
    class r1,r2,r3 res
    style E fill:#ffffff,stroke:#3b6ea5
    style C fill:#ffffff,stroke:#c9892b
    style M fill:#ffffff,stroke:#6c4fa3
    style R fill:#ffffff,stroke:#3d8b3d
    classDef key fill:#fde3e1,stroke:#c0392b,stroke-width:3px,color:#4a1410,font-weight:bold
    class m2,m3,m4,r2 key
```

**Lecture du schéma, étape par étape :**

1. **Performance de référence** : à partir des mesures, le code ajuste une courbe de polarisation de l'électrolyseur et de la pile à l'état neuf.
2. **Vieillissement** : à partir de cette performance de référence, il fait vieillir chaque stack sur 15 ans selon le cas choisi ; la tension de la pile baisse, celle de l'électrolyseur monte.
3. **Fin de vie et nombre de stacks** : à partir de cette tension, il trouve l'âge où elle a varié de 10 %, puis le nombre de stacks nécessaires sur 15 ans.
4. **Flux de la chaîne** : à partir de la même tension, il calcule l'électricité par kg d'hydrogène et l'hydrogène par km ; leur hausse est la surconsommation.
5. **ACV** : il multiplie ces flux et le nombre de stacks par les impacts caractérisés, ce qui donne l'impact de la surconsommation et celui du remplacement.
6. **Résultats** : la hausse due au vieillissement, pour chaque composant et pour la chaîne, dans les 16 catégories EF 3.1.

Les cases marquées ★ sont l'apport de ce travail. Le détail de chaque étape est dans [docs/METHOD.fr.md](docs/METHOD.fr.md).

### Les trois cas de vieillissement

| | Optimiste | Central | Pessimiste |
|---|---|---|---|
| Modèle | linéaire | linéaire | semi-empirique |
| Pile | 8 000 h jusqu'à la fin de vie (objectif du DOE) | 4 100 h (meilleure flotte suivie par le DOE, 2006–2016) | constantes de laboratoire (Colombo et al. 2023) : fin de vie à 2 895 h |
| Électrolyseur | 2,3 µV/h par cellule (objectif 2026 du DOE) | 4,8 µV/h (statut 2022 du DOE) | constantes de laboratoire (Padgett et al. 2025 ; Chandesris et al. 2015) |
| Perméation du réservoir (mL/h/L, de 0 à 15 ans) | 6 → 6 | 6 → 14 | 6 → 46 (limite UN R134) |
| Ce qu'il représente | ce que vise la technologie | l'état actuel des systèmes réels | une borne haute, sur des cellules plus sollicitées que des stacks commerciaux |

Les trois cas sont toujours donnés côte à côte ; le cas central est mis en avant parce qu'il repose sur des systèmes réels. Les valeurs et leurs sources sont dans `config/default.yaml`, les équations dans [docs/METHOD.fr.md](docs/METHOD.fr.md).

## 4. Démarrage rapide, sans et avec licence ecoinvent

| | Sans licence ecoinvent | Avec une licence ecoinvent |
|---|---|---|
| **Ce que vous pouvez changer** | toutes les entrées du modèle : durées de vie et constantes de vieillissement, lois de vieillissement, kilométrage, heures de l'électrolyseur, compression, règle de comptage des stacks, source d'électricité (parmi les cinq fournies, ou une nouvelle si vous avez son impact par kWh) ; et l'**impact de fabrication** d'un stack ou du réservoir, en donnant directement votre propre valeur | tout ce qui est possible sans licence, et en plus le **contenu des inventaires de fabrication** : quantités de matériaux et d'énergie, données ecoinvent reliées, lieu de fabrication ; l'impact est alors recalculé |
| **Ce que vous ne pouvez pas changer** | tout ce qui demande de recalculer un impact à partir d'ecoinvent : changer une quantité de matériau ou d'énergie dans un inventaire de fabrication, ajouter ou retirer un flux, relier une autre donnée ecoinvent, changer le lieu de fabrication, calculer l'impact d'un nouveau composant, ou celui d'une nouvelle source d'électricité | les données ecoinvent elles-mêmes (les procédés d'arrière-plan), que le dépôt utilise sans les modifier |
| Ce qui est utilisé | `data/impacts` : résultats caractérisés seulement (impact d'1 kWh, d'1 kg d'eau, d'un stack ou d'un réservoir fabriqué) | votre propre ecoinvent 3.11 cut-off, importé dans Brightway avec votre identifiant ecoinvent |
| Ce qu'il faut installer | `requirements.txt` | `requirements.txt` et `requirements-brightway.txt` |

### Installation

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

Dans Jupyter, `!` lance une commande du terminal, `%cd` entre dans un dossier, et `{sys.executable}` désigne le Python du notebook. Si le dossier existe déjà, lancez seulement `import sys` puis `%cd h2-ageing-lca-main`. Un notebook prêt à lancer est aussi dans [examples/adapt_the_model.fr.ipynb](examples/adapt_the_model.fr.ipynb).

**Ensuite :**

- **sans licence**, changez une valeur ou un cas : [docs/GUIDE.fr.md](docs/GUIDE.fr.md), sections 2 et 3 ;
- **avec une licence**, recalculez les impacts de fabrication avec Brightway (identifiant ecoinvent, import, vérification) : [docs/GUIDE.fr.md](docs/GUIDE.fr.md#34-fabrication), section 3.4.

## 5. Organisation du dépôt et documentation

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

| Document | Ce qu'on y trouve |
|---|---|
| [docs/METHOD.fr.md](docs/METHOD.fr.md) | chaque équation et sa source, l'ACV, la sensibilité, les résultats détaillés |
| [docs/GUIDE.fr.md](docs/GUIDE.fr.md) | installer, changer une valeur, tout ce qui se change, reproduire chaque résultat, exemples commentés |
| [docs/LIMITS.fr.md](docs/LIMITS.fr.md) | les limites, leur effet et le domaine de validité |
| [data/README.fr.md](data/README.fr.md) | les sources et licences de chaque fichier de données |
| [data/inventories/README.fr.md](data/inventories/README.fr.md) | les inventaires de fabrication et leurs données ecoinvent |
| [examples/](examples/) | notebooks Jupyter prêts à lancer |
| [notebooks/](notebooks/README.fr.md) | notebooks de recherche d'origine |

## 6. Résultats principaux

Configuration par défaut : changement climatique (EF 3.1), mix résiduel français (79,6 g CO2-éq/kWh, données AIB 2024), 200 000 km en 15 ans. « Sans vieillissement » : la même chaîne avec des stacks qui ne vieillissent jamais. Chaque valeur comprend l'usage et la fabrication.

| | Sans vieillissement | Optimiste | Central | Pessimiste |
|---|---|---|---|---|
| Stacks de pile sur 15 ans | 1 | 1 | 2 | 2 |
| Stacks d'électrolyseur sur 15 ans | 1 | 2 | 3 | 3 |
| Électrolyseur seul (kg CO2-éq/kg H2) | 4,31 | 4,53 (+5,1 %) | 4,57 (+5,9 %) | 4,66 (+8,2 %) |
| Réservoir seul (g CO2-éq/km) | 11,89 | 11,89 (0,0 %) | 12,04 (+1,3 %) | 12,64 (+6,4 %) |
| Pile seule (g CO2-éq/km) | 61,9 | 63,4 (+2,4 %) | 82,2 (+32,8 %) | 83,4 (+34,6 %) |
| **Chaîne complète (g CO2-éq/km)** | **74,1** | **77,8 (+5,0 %)** | **97,2 (+31,1 %)** | **100,1 (+35,0 %)** |

- **La pile est dominée par le remplacement** : dans le cas central, 91 % de sa hausse vient du second stack.
- **L'électrolyseur est dominé par la surconsommation** : un stack est réparti sur 1,19 million de kg d'hydrogène, l'électricité en plus pèse davantage.

Décomposition détaillée (usage et fabrication, deux voies par composant) et explication de chaque point : [docs/METHOD.fr.md](docs/METHOD.fr.md#7-résultats-détaillés). Limites et domaine de validité : [docs/LIMITS.fr.md](docs/LIMITS.fr.md).

## 7. Citer, licence, contact

- **Citer :** voir [CITATION.cff](CITATION.cff) (GitHub affiche un bouton « Cite this repository »).
- **Licence :** code sous licence MIT ([LICENSE](LICENSE)) ; données et documentation sous CC BY 4.0 ([LICENSE-DATA.md](LICENSE-DATA.md)). Les sources tierces gardent leurs propres conditions ([data/README.fr.md](data/README.fr.md)).
- **Questions, erreurs ou nouvelles données :** ouvrez une *Issue* sur GitHub. Les données de dégradation mesurées sur des stacks commerciaux sont particulièrement bienvenues, car elles remplaceraient les cas d'encadrement par une mesure.
