# Méthode

[English](METHOD.md) | **Français**

Cette page résume ce que calcule le code, et pourquoi. Chaque valeur de `config/default.yaml` est accompagnée de sa source.

**Sommaire :** [1. Unités fonctionnelles et système](#1-unités-fonctionnelles-et-système) · [2. Pile à combustible](#2-pile-à-combustible) · [3. Électrolyseur](#3-électrolyseur) · [4. Réservoir](#4-réservoir) · [5. ACV](#5-acv) · [6. Analyses de sensibilité](#6-analyses-de-sensibilité) · [7. Résultats détaillés](#7-résultats-détaillés) · [Références](#références-pour-la-structure-du-modèle-et-les-bornes-dajustement)

---

## 1. Unités fonctionnelles et système

| Évaluation | Unité fonctionnelle | Ce qui vieillit |
|---|---|---|
| Pile seule | 1 km parcouru | le stack de pile seulement ; elle reçoit l'hydrogène de l'électrolyseur étudié à son état de référence (sans vieillissement, fabrication du stack exclue), comprimé : 4,503 kg CO2-éq/kg |
| Électrolyseur seul | 1 kg d'hydrogène produit | le stack d'électrolyseur |
| Chaîne complète | 1 km parcouru | électrolyseur, réservoir (perméation) et pile ensemble |

- **Horizon :** 15 ans, 200 000 km (`horizon`).
- **Électricité :** mix résiduel français par défaut (79,6 g CO2-éq/kWh), le mix d'un électrolyseur raccordé au réseau qui n'achète pas de garanties d'origine. Le profil éolien mesuré donne seulement l'électricité consommée par kg d'hydrogène et son évolution avec l'âge, pas l'origine de l'électricité.
- **Comparaison :** chaque évaluation compare la chaîne avec vieillissement à la même chaîne sans vieillissement (même profil, même électricité, même horizon, mêmes frontières et mêmes inventaires, un stack de chaque convertisseur).
- **Dans le système :** électricité et eau de l'électrolyseur, électricité de compression, fabrication des stacks et du réservoir, hydrogène perdu par perméation.
- **Hors du système :** auxiliaires, station hors compression, reste du véhicule, transports, fin de vie.

### Ce que comprend chaque impact

L'ACV compte deux types de flux : la **fabrication** des composants qui vieillissent, et leur **usage**. Les deux sont comptés « du berceau à la porte » : de l'extraction des ressources jusqu'au moment où le composant sort de l'usine, ou où le kilowattheure arrive à l'électrolyseur.

**Fabrication d'un stack ou du réservoir.** L'inventaire de chaque composant (`data/inventories/`) liste ses matériaux et l'électricité consommée par l'usine. Chaque matériau est relié à une donnée ecoinvent 3.11 (modèle cut-off) qui porte toute sa chaîne amont. L'impact d'un composant comprend donc :

| Étape du cycle de vie | Comptée | D'où elle vient |
|---|---|---|
| Extraction des ressources (minerais, pétrole, gaz) | oui | données ecoinvent de chaque matériau |
| Transformation des matériaux (raffinage, fusion, laminage, synthèse chimique, production de la fibre de carbone) | oui | données ecoinvent de chaque matériau |
| Énergie et transports de ces étapes amont, jusqu'au marché | oui | données ecoinvent de chaque matériau |
| Électricité de fabrication et d'assemblage du composant | oui | inventaire du composant |
| Transport du composant fini jusqu'au véhicule ou au site | non | non décrit dans les inventaires sources |
| Bâtiments et machines de l'usine du fabricant | non | non décrits dans les inventaires sources |
| Fin de vie, recyclage, crédits pour les métaux récupérés | non | modèle cut-off : ni charge ni crédit en fin de vie |

L'iridium (anode de l'électrolyseur) n'a pas de donnée ecoinvent : il est compté seulement comme ressource prélevée dans le sol. Son extraction pèse sur l'épuisement des ressources, mais aucun impact de sa transformation n'est compté, en particulier sur le changement climatique.

**Usage.** L'impact d'1 kWh d'électricité est la donnée ecoinvent de la source choisie : il comprend les combustibles et leur extraction, les centrales et leur construction, et le réseau avec ses pertes. L'impact d'1 kg d'eau déionisée comprend sa production. L'hydrogène perdu par perméation est compté comme de l'hydrogène qu'il faut produire et comprimer.

**Hors du système.** Les auxiliaires, la station de distribution hors compression, le reste du véhicule et les transports entre les maillons de la chaîne. Ils ne changent pas avec l'âge des stacks.

---

### Les trois cas de vieillissement

| | Optimiste | Central | Pessimiste |
|---|---|---|---|
| Modèle | linéaire | linéaire | semi-empirique |
| Pile | 8 000 h jusqu'à la fin de vie (objectif du DOE) | 4 100 h (meilleure flotte suivie par le DOE, 2006–2016) | constantes de laboratoire (Colombo et al. 2023) : fin de vie à 2 895 h |
| Électrolyseur | 2,3 µV/h par cellule (objectif 2026 du DOE) | 4,8 µV/h (statut 2022 du DOE) | constantes de laboratoire (Padgett et al. 2025 ; Chandesris et al. 2015) |
| Perméation du réservoir (mL/h/L, de 0 à 15 ans) | 6 → 6 | 6 → 14 | 6 → 46 (limite UN R134) |
| Ce qu'il représente | ce que vise la technologie | l'état actuel des systèmes réels | une borne haute, sur des cellules plus sollicitées que des stacks commerciaux |

Les trois cas sont toujours donnés côte à côte ; le cas central est mis en avant parce qu'il repose sur des systèmes réels. Les valeurs et leurs sources sont dans `config/default.yaml`, les équations dans les sections 2 à 4 ci-dessous.

## 2. Pile à combustible

Code : `src/h2ageing/pemfc.py`

### 2.1 Polarisation à l'état de référence

La tension complète d'une cellule contient les pertes d'activation et de transport des deux électrodes, et la perte ohmique. Seules les pertes de l'électrode à oxygène sont gardées (la cathode pour la pile, l'anode pour l'électrolyseur), pour deux raisons :

1. la réaction de l'hydrogène a, sur platine en milieu acide, un courant d'échange plus élevé de plusieurs ordres de grandeur (Durst et al. 2014), donc sa perte est faible et presque proportionnelle au courant, et elle est comprise dans $`R`$ ;
2. les pertes d'activation des deux électrodes varient toutes deux en $`\ln j`$, donc une seule courbe tension–courant ne permet pas de les séparer.

La tension d'une cellule de pile s'écrit :

```math
V(j,t) \;=\; E_{\mathrm{rev}}(T) \;-\; \frac{RT}{\alpha_c F}\,\ln\!\left(\frac{j}{i_{0c}\,S(t)}\right) \;-\; R(t)\,j \;+\; B_c\,\ln\!\left(1-\frac{j}{i_{\mathrm{lim}}}\right)
```

```math
E_{\mathrm{rev}}(T) \;=\; 1{,}229 \;-\; 0{,}85\times10^{-3}\,(T-298{,}15)
```

| Symbole | Signification | Unité |
|---|---|---|
| $`j`$ | densité de courant | A/cm² |
| $`t`$ | âge du stack | h |
| $`T`$ | température (70 °C) | K |
| $`\alpha_c`$ | coefficient de transfert de la cathode | – |
| $`i_{0c}`$ | densité de courant d'échange de la cathode | A/cm² |
| $`S(t)`$ | surface de platine relative (1 à l'état neuf) | – |
| $`R(t)`$ | résistance d'une cellule ($`R_0`$ à l'état neuf) | Ω·cm² |
| $`B_c`$ | coefficient de la perte de transport | V |
| $`i_{\mathrm{lim}}`$ | densité de courant limite | A/cm² |

Les quatre paramètres $`i_{0c}`$, $`R_0`$, $`B_c`$ et $`i_{\mathrm{lim}}`$ sont ajustés sur des points quasi stationnaires des mesures sur route (`scripts/fit_pemfc.py`), par moindres carrés bornés. Bornes, et valeurs publiées qu'elles encadrent :

| Paramètre | Bornes | Valeurs publiées |
|---|---|---|
| $`\log_{10} i_{0c}`$ | de −12 à −1 | Vetter & Schumacher 2019 ; Colombo et al. 2023 |
| $`R_0`$ | de 0 à 0,3 Ω·cm² | Colombo et al. 2023 |
| $`B_c`$ | de 0 à 0,3 V | Almodfer et al. 2022 |
| $`i_{\mathrm{lim}}`$ | de 2,03 à 6 A/cm² (borne basse juste au-dessus de la plus forte densité de courant mesurée) | Bielefeld et al. 2024 |

### 2.2 Hydrogène consommé à un âge donné

Le trajet mesuré (temps, courant, tension ; 2 033 s, 20,32 km) est rejoué à chaque âge **à puissance imposée** :

- **Courant à chaque seconde.** Le courant qui fournit la puissance mesurée est trouvé par dichotomie (40 itérations).
- **Facteur d'ancrage.** La courbe de polarisation ajustée ne redonne pas exactement la tension mesurée à chaque seconde. À chaque seconde, le facteur vaut tension mesurée ÷ tension du modèle neuf ; il corrige le modèle pour qu'à l'âge zéro il redonne exactement le courant et l'hydrogène mesurés. Le même facteur est gardé à tous les âges : l'écart entre l'âge zéro et un âge donné ne vient donc que du vieillissement, pas de l'erreur d'ajustement.
- **Hydrogène.** L'hydrogène consommé suit la loi de Faraday, plus un courant de perte. L'écart entre l'hydrogène mesuré (0,196 kg) et la loi de Faraday est gardé constant ; la hausse du crossover s'y ajoute.

### 2.3 Vieillissement, modèle semi-empirique (cas pessimiste)

Sa structure est physique, chaque mécanisme de dégradation agissant sur un terme de l'équation de polarisation ; ses lois d'évolution dans le temps sont ajustées sur des mesures de laboratoire, d'où le nom « semi-empirique ».

**Surface de platine** (Verducci et al.) :

```math
\frac{dS}{dt} \;=\; -\,k\,S^2\,e^{\omega S}
```

$`k`$ est choisi pour que $`S(1000\ \mathrm{h})`$ soit égal à la valeur mesurée par Colombo et al. (2023). Il est trouvé en inversant l'intégrale tabulée (méthode des trapèzes, 6 000 points) :

```math
g(S) \;=\; \int_S^1 \frac{e^{-\omega s}}{s^2}\,ds
```

**Résistance de transport :**

```math
R(t) \;=\; R_0 + r\,t, \qquad r \;=\; \frac{\Delta V_{1{,}8,\,1000} \;-\; \dfrac{RT}{\alpha_c F}\,\ln\dfrac{1}{S_{1000}}}{1{,}8 \times 1000}
```

$`\Delta V_{1{,}8,\,1000}`$ est la perte de tension mesurée à 1,8 A/cm² après 1 000 h ; la part déjà due à la perte de platine est retranchée. Dans le code, $`R(t)`$ est écrite $`R_0\,(1 + k_R\,t)`$, avec $`k_R = r/R_0`$.

**Crossover :** 2 mA/cm² à l'âge zéro, multiplié par le facteur mesuré en 1 000 h (loi linéaire par défaut ; lois exponentielle et constante disponibles).

### 2.4 Vieillissement, modèle linéaire (cas optimiste et central)

```math
V(t) \;=\; V(0) \;-\; \mu\,t, \qquad \mu \;=\; \frac{0{,}10 \times V_{300\,\mathrm{A}}(0)}{t_{\mathrm{FdV}}}
```

$`t_{\mathrm{FdV}}`$ est la durée de vie publiée : 8 000 h (objectif du DOE, optimiste) ou 4 100 h (meilleure flotte du DOE, central). Le crossover reste constant.

### 2.5 Fin de vie

Âge auquel la tension du stack à 300 A a perdu 10 % (critère du DOE), trouvé par la méthode de Brent entre 0 et 60 000 h. Le DOE mesure cette perte entre 1,0 et 1,5 A/cm² (objectifs techniques du DOE pour les composants de pile PEM, 2017) ; avec 297 cm² de surface active, 300 A correspondent à 1,01 A/cm². À ce courant, la tension de cellule de référence est de 0,7324 V ; la fin de vie est atteinte à 0,6592 V.

---

## 3. Électrolyseur

Code : `src/h2ageing/pemwe.py`

### 3.1 Polarisation à l'état de référence

Ajustée par `scripts/fit_pemwe.py` sur le profil éolien de 4 heures (pas de 1 s) :

```math
V(j) \;=\; E_{\mathrm{rev}}(T) \;+\; \frac{RT}{2\,\alpha_a F}\,\ln\!\left(\frac{j}{i_{0a}}\right) \;+\; R\,j \;-\; B_c\,\ln\!\left(1-\frac{j}{i_{\mathrm{lim}}}\right)
```

- $`\alpha_a`$ est fixé par la pente de Tafel de Padgett et al. (46 mV/décade à 80 °C).
- $`i_{0a}`$, $`R`$ et $`B_c`$ sont ajustés (moindres carrés bornés, méthode *trust region reflective*, 50 points de départ, graine 180).
- Le modèle est écrit à 80 °C, la température des essais qui donnent les constantes de vieillissement.

| Paramètre | Bornes | Valeurs publiées |
|---|---|---|
| $`i_{0a}`$ | de $`10^{-14}`$ à $`10^{-1}`$ A/cm² | Marefatjouikilevaee et al. 2023 |
| $`R`$ | de 0 à 1 Ω·cm² | Weiß et al. 2019 ; Padgett et al. 2025 ; Fouda-Onana et al. 2016 |
| $`B_c`$ | de 0 à 1 V | Almodfer et al. 2022 |

**Nombre de cellules et surface.** Ni l'un ni l'autre n'est publié. La loi de Faraday ne fixe que le produit $`\eta_F N`$ : la fiche Nel (246 Nm³/h à 3 000 A) donne 196, nos mesures 195. Le nombre de cellules vaut donc au moins 196 ; 200 est retenu (premier nombre rond au-dessus), d'où $`\eta_F`$ = 97,7 %. La surface, 1 500 cm², est choisie pour que le courant maximal (3 000 A) corresponde à 2 A/cm², densité à laquelle le DOE donne l'état de l'art de la durabilité des stacks PEM. Les deux se changent avec `scripts/fit_pemwe.py --n-cells --area-cm2`.

Sur le profil mesuré, le stack neuf consomme $`E_0`$ = 2 841 kWh et produit 52,93 kg d'hydrogène, soit $`\mathrm{SEC}_0`$ = 53,68 kWh/kg.

### 3.2 Vieillissement, modèle semi-empirique (cas pessimiste)

Constantes de Padgett et al. (2025) et Chandesris et al. (2015).

**Activité de l'anode**, et la hausse de tension qu'elle provoque :

```math
f_A(t) \;=\; f_{\min} + (1-f_{\min})\,e^{-t/\tau}, \qquad \Delta V_{\mathrm{act}}(t) \;=\; \frac{b}{\ln 10}\,\ln\frac{1}{f_A(t)}
```

**Résistance :**

```math
R(t) \;=\; R_0 \;+\; \frac{\text{dérive de la HFR} + \text{dérive de la couche catalytique}}{j_{\mathrm{essai}}}\;t
```

**Rendement faradique**, à partir de l'amincissement de la membrane :

```math
\frac{\eta_F(t)}{\eta_{F,0}} \;=\; 1 - 0{,}5\,\frac{t}{t_{50}}
```

### 3.3 Vieillissement, modèle linéaire (cas optimiste et central)

Dérive de tension constante $`\mu`$ par cellule : 2,3 µV/h (objectif 2026 du DOE, optimiste) ou 4,8 µV/h (statut 2022 du DOE, central).

### 3.4 Électricité par kg à un âge donné

L'énergie sur le profil est mise à jour au premier ordre :

```math
E(t) \;=\; E_0 \;+\; \Delta V_{\mathrm{uniforme}}\,W_0 \;+\; \Delta R\,W_j, \qquad \mathrm{SEC}(t) \;=\; \frac{E(t)}{H_2(t)}
```

```math
W_0 \;=\; \sum \frac{E_{\mathrm{pas}}}{V_0}, \qquad W_j \;=\; \sum \frac{E_{\mathrm{pas}}\; j}{V_0}
```

### 3.5 Fin de vie

Hausse de tension de 10 % à la densité de courant moyenne du profil (méthode de Brent, de 0 à 400 000 h).

---

## 4. Réservoir

Code : `src/h2ageing/tank.py`

La perméation $`P`$ (mL/h/L à 55 °C, réservoir plein) augmente linéairement de $`P_0`$ à $`P_{15}`$ sur les 15 ans de la certification : 6 → 6, 6 → 14 et 6 → 46 dans les trois cas. Les valeurs viennent de Dixon et Smutny (2022, NHTSA) : 5,86 et 14,38 mL/h/L mesurés sur deux réservoirs de type IV (arrondis à 6 et 14), et 46 mL/h/L, la limite réglementaire (GTR 13, repris dans le règlement UN R134).

```math
m_{\mathrm{perm}} \;=\; \frac{P \cdot V \cdot \rho \cdot 8\,760}{\text{km par an}}
```

avec $`V`$ le volume du réservoir et $`\rho`$ la masse volumique de l'hydrogène.

**Réservoir seul, par km** (`tank.csv`) : fabrication d'un réservoir divisée par 200 000 km, plus l'hydrogène perdu en moyenne, compté comme de l'hydrogène livré à l'état de référence (électrolyse et compression).

---

## 5. ACV

Code : `src/h2ageing/chain.py`, `impacts.py`

**Nombre de stacks.** Chaque stack repart de l'état neuf quand il est remplacé :

```math
n \;=\; \left\lceil \frac{L}{t_{\mathrm{FdV}}} \right\rceil \ \ \text{(entier, par défaut)} \qquad \text{ou} \qquad n \;=\; \max\!\left(1,\ \frac{L}{t_{\mathrm{FdV}}}\right) \ \ \text{(prorata)}
```

$`L`$ est la durée de fonctionnement sur l'horizon ; le prorata compte la part de vie du stack utilisée, avec au moins le premier stack.

**Pile seule, par km :**

```math
I_{\text{PàC}} \;=\; m_0\,\bar h\,I_{\mathrm{H_2},\,\text{réf}} \;+\; \frac{n\,F_{\mathrm{stack}}}{L_{\mathrm{km}}}
```

- $`m_0`$ : hydrogène par km à l'état neuf ;
- $`\bar h`$ : consommation moyenne d'hydrogène sur l'horizon, rapportée à l'état neuf (méthode des trapèzes sur les âges) ;
- $`I_{\mathrm{H_2},\,\text{réf}}`$ : impact d'1 kg d'hydrogène produit par un électrolyseur neuf, puis comprimé ;
- $`F_{\mathrm{stack}}`$ : impact de la fabrication d'un stack ; $`L_{\mathrm{km}}`$ = 200 000 km.

**Électrolyseur seul, par kg :**

```math
I_{\mathrm{EL}} \;=\; \overline{\mathrm{SEC}}\;I_{\mathrm{kWh}} \;+\; I_{\mathrm{eau}} \;+\; \frac{n\,F_{\mathrm{stack}}}{H_{2,\mathrm{produit}}}
```

L'énergie et l'hydrogène sont intégrés sur l'horizon (20 001 points).

**Chaîne complète, par km.** L'hydrogène consommé (pile à son âge) plus l'hydrogène perdu (réservoir à son âge) est produit par l'électrolyseur à son âge, puis comprimé ; le tout est intégré sur 15 ans (80 points par an). Les stacks d'électrolyseur sont partagés avec le reste de la production : le véhicule porte la part de l'hydrogène qu'il utilise.

**Impacts :** EF 3.1, 16 catégories. Score unique :

```math
\text{score unique} \;=\; \sum_{\text{catégories}} \frac{\text{impact}}{\text{facteur de normalisation}} \times \text{facteur de pondération}
```

---

## 6. Analyses de sensibilité

Chaque test change une entrée (ou plusieurs) et regarde si le résultat change.

| Ce qu'on change | Question | Script |
|---|---|---|
| La source d'électricité | Le résultat tient-il avec une électricité plus propre ? | `run.py --set usage.electricity_electrolyser=...` |
| Les heures de l'électrolyseur par an | Le résultat change-t-il si l'électrolyseur fonctionne plus ou moins que 6 000 h par an ? | `run.py --set usage.electrolyser_hours_per_year=...` |
| Le comptage des stacks | Et si le dernier stack avait une seconde vie ? | `run.py --set usage.stack_counting=prorata` |
| La durée de vie de la pile | À partir de quelle durée de vie un seul stack suffit-il ? | `threshold.py` |
| La loi de crossover | Sa forme change-t-elle le résultat ? | `fuel_cell_tests.py` |
| Les constantes de laboratoire | Laquelle compte le plus ? | `semi_empirical_constants.py` |
| Huit entrées à la fois (Sobol) | Laquelle explique le plus le résultat ? | `sobol.py` |

**Heures de l'électrolyseur.** Les heures publiées sont à pleine charge ; elles sont converties en heures au profil mesuré en les divisant par sa charge moyenne (710/1 250 = 0,568).

**Ce qu'est l'analyse de Sobol.** Elle fait varier toutes les entrées en même temps, un grand nombre de fois (10 240 calculs), et mesure la part de la variation du résultat expliquée par chaque entrée. Son indice total va de 0 (l'entrée ne compte pas) à 1 (l'entrée explique toute la variation, seule ou avec les autres).

---

## 7. Résultats détaillés

Configuration par défaut (changement climatique, chaîne complète, 200 000 km en 15 ans). Tableau principal : [README](../README.fr.md#6-résultats-principaux).

Chaque valeur est un total : **usage et fabrication**. Pour la chaîne complète, en g CO2-éq/km (valeurs arrondies) :

| | Sans vieillissement | Optimiste | Central | Pessimiste |
|---|---|---|---|---|
| Usage : électricité et eau de l'électrolyse | 41,5 | 44,8 | 45,2 | 48,0 |
| Usage : compression | 2,2 | 2,2 | 2,3 | 2,4 |
| Fabrication : stacks de pile | 18,5 | 18,5 | 37,0 | 37,0 |
| Fabrication : réservoir | 11,7 | 11,7 | 11,7 | 11,7 |
| Fabrication : stacks d'électrolyseur | 0,3 | 0,7 | 1,0 | 1,1 |
| **Total** | **74,1** | **77,8** | **97,2** | **100,1** |

L'hydrogène perdu par perméation est compté dans l'usage, comme de l'hydrogène à produire en plus.

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
| Chaîne complète | surconsommation (électricité, eau et compression) | +4,5 % | +5,2 % | +9,1 % |
| | remplacement (stacks de pile et d'électrolyseur) | +0,5 % | +25,9 % | +25,9 % |
| | **les deux** | **+5,0 %** | **+31,1 %** | **+35,0 %** |

Ce que montrent ces chiffres :

- **La pile est dominée par le remplacement.** Un stack de pile est réparti sur les 200 000 km d'un seul véhicule ; un second stack ajoute 18,5 g CO2-éq/km, soit 30 % de l'impact de la pile sans vieillissement (61,9 g/km). Dans le cas central, 91 % de la hausse de la pile vient du stack en plus.
- **L'électrolyseur est dominé par la surconsommation.** En 15 ans, l'électrolyseur fonctionne 90 000 h et produit environ 1,19 million de kg d'hydrogène. La fabrication d'un stack (39 509 kg CO2-éq) est répartie sur tout cet hydrogène : 0,033 kg CO2-éq/kg, soit 0,8 % de l'impact d'1 kg (4,31). Dans le cas central, les stacks en plus ajoutent 0,07 kg CO2-éq/kg, mais l'électricité en plus en ajoute 0,19 : la surconsommation pèse près de trois fois plus que le remplacement.
- **Le résultat avance par paliers, car le nombre de stacks est entier.** La pile fonctionne 5 554 h sur 200 000 km : au-dessus, 1 stack suffit (+6 %) ; entre 2 777 et 5 554 h, il en faut 2 (+31 %). Ce qui compte est de franchir le seuil de 5 554 h, pas de gagner quelques heures.
- **La durée de vie de la pile est l'entrée clé.** L'analyse de sensibilité globale (méthode de Sobol) fait varier les huit entrées incertaines en même temps et mesure la part de la variation du résultat due à chacune : son indice total va de 0 (l'entrée ne compte pas) à 1 (elle explique tout). La durée de vie de la pile explique presque toute la variation de la hausse (indice de Sobol total 0,94 ; méthode dans [section 6](#6-analyses-de-sensibilité), résultats dans [GUIDE.fr.md](GUIDE.fr.md#8-quelles-entrées-comptent-le-plus-toutes-ensemble-)).

Les limites, leur effet et le domaine de validité sont dans [LIMITS.fr.md](LIMITS.fr.md).

---

## Références pour la structure du modèle et les bornes d'ajustement

- Almodfer R. et al. (2022). Improving parameter estimation of fuel cell using honey badger optimization algorithm. Frontiers in Energy Research 10, 875332 (Table 2 corrected in 13, 1588458, 2025).
- Bielefeld N.M. et al. (2024). A one-dimensional computational model to identify operating conditions and cathode flow channel dimensions for a PEM fuel cell. Hydrogen 5, 624–643. doi:10.3390/hydrogen5030033
- Colombo E. et al. (2023). PEMFC performance decay during real-world automotive operation. Journal of Power Sources 553, 232246.
- Dixon M., Smutny T. (2022). Hydrogen Container Performance Testing. NHTSA, U.S. Department of Transportation, report DOT HS 812 988. rosap.ntl.bts.gov/view/dot/62645
- Durst J. et al. (2014). New insights into the electrochemical hydrogen oxidation and evolution reaction mechanism. Energy & Environmental Science 7, 2255–2260.
- Fouda-Onana F. et al. (2016). Investigation on the degradation of MEAs for PEM water electrolysers part I. International Journal of Hydrogen Energy 41, 16627–16636.
- Marefatjouikilevaee H., Auger F., Olivier J.-C. (2023). Static and dynamic electrical models of PEM electrolysers: a comprehensive review. Energies 16, 6503. doi:10.3390/en16186503
- Padgett E. et al. (2025). Quantifying sources of voltage decay in long-term durability testing for PEM water electrolysis. Journal of The Electrochemical Society 172, 054508.
- Vetter R., Schumacher J.O. (2019). Experimental parameter uncertainty in PEM fuel cell modeling. Part I. Journal of Power Sources 438, 227018.
- Weiß A. et al. (2019). Impact of intermittent operation on lifetime and performance of a PEM water electrolyzer. Journal of The Electrochemical Society 166, F487–F497.
