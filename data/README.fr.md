# Données

[English](README.md) | **Français**

## measurements/

| Fichier | Contenu | Origine |
|---|---|---|
| `mirai2_fuel_cell_signals.csv` | Pile de la Toyota Mirai II, tous les enregistrements à 1 s : temps (s), vitesse du véhicule (km/h), courant du stack (A), tension du stack (V), niveau du réservoir (%). Le temps repart de zéro à chaque enregistrement. | Mesures sur route et à l'arrêt sur une Toyota Mirai II. Utilisées pour ajuster la courbe de polarisation. |
| `mirai2_fuel_cell_trip.csv` | Trajet sur route mesuré, utilisé pour le bilan d'hydrogène : temps (s), courant (A), tension (V) ; 2 033 s, 20,32 km, 0,196 kg d'hydrogène (réservoir de 56,0 % à 52,5 % de 5,6 kg). Valeurs manquantes interpolées. | Même campagne de mesures, tirée de la base de données expérimentale d'Ali Alhakim. |
| `nel_mc250_wind_profile.xlsx` | Électrolyseur PEM Nel MC250 (1,25 MW) alimenté selon un profil éolien, 4 h à 1 s (feuille `Profil_1s_source`), avec l'inventaire de la phase d'usage qui en est tiré (autres feuilles). | Construit à partir du jeu de données public du NLR « Public Reference Data for Megawatt-Scale Hydrogen Electrolysis », essai « wind-GE1.5MW 0.65-200 ». |

## parameters/

| Fichier | Écrit par | Contenu |
|---|---|---|
| `pemfc_fit.json` | `scripts/fit_pemfc.py` | pile : paramètres de polarisation ajustés, qualité de l'ajustement, et courbe mesurée utilisée pour l'ajustement |
| `pemwe_fit.json` | `scripts/fit_pemwe.py` | électrolyseur : paramètres de polarisation ajustés, qualité de l'ajustement, grandeurs du profil mesuré, et test de la pente de Tafel |

Les deux fichiers sont réécrits par leur script, qui redonne les valeurs fournies. Un guide de chaque entrée est donné plus bas, dans [Lire les fichiers de paramètres](#lire-les-fichiers-de-paramètres).

## impacts/ (résultats caractérisés, EF 3.1, ecoinvent 3.11 cut-off)

Aucune donnée ecoinvent n'est incluse. Ces fichiers contiennent seulement des résultats caractérisés, calculés dans Brightway / Activity Browser par les auteurs.

| Fichier | Contenu |
|---|---|
| `electricity_per_kWh.csv` | impact d'1 kWh : `residual_mix_FR` (« electricity, medium voltage, residual mix, FR », 79,6 g CO2-éq/kWh, référence), `average_mix_FR`, `nuclear_FR`, `wind_FR`, `photovoltaic` (toiture de 3 kWc, CdTe) |
| `water_per_kg.csv` | impact d'1 kg d'eau déionisée |
| `fabrication_per_unit.csv` | impact d'un stack de pile (128 kW), d'un stack d'électrolyseur (1,25 MW) et d'un réservoir de type IV |
| `ef31_normalisation_weighting.csv` | facteurs de normalisation (par personne) et de pondération d'EF 3.1 |

## inventories/ (premier plan)

| Fichier | Contenu | Source |
|---|---|---|
| `fuel_cell_stack_128kW.csv` | matériaux et électricité de fabrication du stack de pile, avec l'activité ecoinvent 3.11 utilisée pour chaque flux | Mori et al. 2023 (stack de 48 kW), mis à l'échelle par 128/48 |
| `electrolyser_stack_1p25MW.csv` | matériaux et électricité d'assemblage du stack d'électrolyseur | Lundberg 2019 (par MW de stack), mis à l'échelle de 1,25 MW ; iridium compté seulement comme flux de ressource |
| `tank_type_IV.csv` | masses de matériaux et énergie de fabrication du réservoir (flux ecoinvent donnés par leur code Brightway) | Benitez et al. 2021 (5,6 kg, 700 bar) |

L'impact du réservoir dans la configuration par défaut, 2 332 kg CO2-éq, se compose de 2 075 kg pour les matériaux et 257 kg pour l'énergie de fabrication (338,64 kWh d'électricité haute tension, marché mondial, et 43,2 kWh de cogénération au gaz naturel). Mettez une ligne de la colonne `included_in_shipped_impact` à `no` pour l'exclure quand vous reconstruisez le réservoir.

## Licences

Données produites pour ce travail : CC BY 4.0 (voir `LICENSE-DATA.md`). Les données du NLR gardent les conditions de leur éditeur. Les données ecoinvent ne sont pas redistribuées ; des résultats caractérisés sont donnés pour la reproductibilité.

## Lire les fichiers de paramètres

Cette section explique les deux fichiers de `parameters/` pour des lecteurs qui ne sont pas spécialistes d'électrochimie.

### Ce qui est ajusté, et pourquoi

Un stack est un empilement de cellules. La tension d'une cellule dépend du courant qui la traverse : cette relation est la **courbe de polarisation**. Elle part d'une tension théorique (la tension réversible), puis s'en écarte à cause de trois types de pertes :

- **les pertes d'activation** : l'énergie nécessaire pour faire démarrer la réaction à l'électrode ; elles augmentent avec le logarithme du courant ;
- **les pertes ohmiques** : la résistance électrique de la membrane, des contacts et des couches ; elles sont proportionnelles au courant ;
- **les pertes de transport** : à fort courant, les gaz et l'eau n'arrivent plus ou ne repartent plus assez vite de l'électrode.

Dans un électrolyseur, les pertes *s'ajoutent* à la tension réversible (il faut plus d'électricité) ; dans une pile, elles *se retranchent* (elle produit moins d'électricité).

Le modèle de polarisation a quelques paramètres inconnus. **Ajuster** veut dire choisir leurs valeurs pour que le modèle reproduise le plus fidèlement possible la tension mesurée (moindres carrés bornés). Chaque paramètre est gardé dans une plage qui encadre des valeurs publiées ([docs/METHOD.fr.md](../docs/METHOD.fr.md)). Ces valeurs ajustées décrivent les stacks **à l'état de référence, c'est-à-dire l'état mesuré** ; le vieillissement leur est ensuite appliqué.

### `pemfc_fit.json` (pile, Toyota Mirai II)

| Entrée | En clair | Valeur | Unité |
|---|---|---|---|
| `i0c_A_cm2` | facilité avec laquelle la réaction de l'oxygène démarre à la cathode (densité de courant d'échange) ; plus elle est élevée, plus la perte d'activation est faible | 1,52e-6 | A/cm² |
| `R0_ohm_cm2` | résistance électrique d'une cellule, par cm² de surface active | 0,0462 | Ω·cm² |
| `Bc_V` | ampleur de la perte de transport à fort courant | 0,026 | V |
| `ilim_A_cm2` | densité de courant limite : le courant auquel le transport des gaz bloquerait la réaction | 2,30 | A/cm² |
| `RMSE_mV_per_cell` | écart moyen entre le modèle et la mesure, par cellule (racine de l'erreur quadratique moyenne) ; plus il est petit, mieux c'est | 1,99 | mV |
| `R2` | part de la variation de la tension mesurée expliquée par le modèle (1 = parfait) | 0,9989 | – |
| `starts`, `starts_reaching_minimum` | l'ajustement est lancé à partir de 200 valeurs initiales tirées au hasard ; les 200 atteignent le même résultat, donc le résultat ne dépend pas du point de départ | 200 / 200 | – |
| `median_points` | la courbe de polarisation mesurée utilisée pour l'ajustement (18 points), voir ci-dessous | – | – |

Chaque entrée de `median_points` est une classe de courant, construite à partir des parties stables des 12 enregistrements sur route :

| Champ | Signification |
|---|---|
| `I` | courant du stack (A) |
| `U` | tension médiane du stack mesurée à ce courant (V) |
| `n` | nombre de points mesurés (1 par seconde) dans cette classe |
| `n_rec` | nombre d'enregistrements, sur 12, qui contiennent cette classe |

Exemple : `{"I": 33.2, "U": 282.25, "n": 326, "n_rec": 11}` signifie qu'à 33,2 A, la tension médiane du stack est de 282,25 V, à partir de 326 secondes mesurées dans 11 enregistrements différents. Utiliser des médianes sur de nombreuses secondes et de nombreux enregistrements supprime le bruit des mesures isolées.

### `pemwe_fit.json` (électrolyseur, Nel MC250, à 80 °C)

Modèle ajusté :

| Entrée | En clair | Valeur | Unité |
|---|---|---|---|
| `T_K` | température du modèle (80 °C) | 353,15 | K |
| `Erev` | tension réversible d'une cellule à cette température : le minimum théorique | 1,182 | V |
| `b_tafel` | pente de Tafel : vitesse à laquelle la perte d'activation augmente avec le courant (fixée d'après la littérature, voir `fits_pente`) | 0,046 | V par décade |
| `alpha_a` | coefficient de transfert de l'anode, calculé à partir de la pente de Tafel | 0,76 | – |
| `i0a` | facilité avec laquelle la réaction de l'oxygène démarre à l'anode (densité de courant d'échange) | 9,36e-10 | A/cm² |
| `R0` | résistance électrique d'une cellule, par cm² | 0,216 | Ω·cm² |
| `Bc` | ampleur de la perte de transport ; elle tombe à zéro, car la courbe mesurée ne montre aucune perte de transport jusqu'à 2 A/cm² | ≈ 0 | V |
| `ilim` | densité de courant limite, fixée au-dessus du courant mesuré le plus fort ; sans perte de transport, elle n'a pas d'effet | 3,0 | A/cm² |
| `RMSE_mV`, `R2` | qualité de l'ajustement sur les 14 400 points du profil (voir le tableau de la pile) | 3,97 ; 0,9993 | mV ; – |

Grandeurs du profil mesuré de 4 heures (état de référence) :

| Entrée | En clair | Valeur | Unité |
|---|---|---|---|
| `E0` | électricité consommée par le stack sur le profil | 2 841 | kWh |
| `H20` | hydrogène produit sur le profil | 52,93 | kg |
| `SEC0` | électricité par kg d'hydrogène (`E0 / H20`), la grandeur clé pour l'ACV | 53,68 | kWh/kg |
| `etaF0` | rendement faradique : part du courant qui produit vraiment de l'hydrogène (le reste est perdu à travers la membrane) | 0,977 | – |
| `j_ref` | densité de courant moyenne sur le profil ; la fin de vie est vérifiée à ce courant | 1,20 | A/cm² |
| `Vref0` | tension de cellule à `j_ref` | 1,860 | V |
| `Vmean0` | tension de cellule moyenne sur le profil | 1,855 | V |
| `W0`, `Wj` | poids utilisés pour mettre à jour l'énergie du profil quand le stack vieillit : `E(t) = E0 + ΔV × W0 + ΔR × Wj`, pour une hausse de tension uniforme ΔV et une hausse de résistance ΔR | 1 470 ; 2 237 | kWh/V ; kWh/(Ω·cm²) |
| `decomposition_jref_mV` | où va la tension au-dessus d'`Erev` à `j_ref` : 419 mV de perte d'activation, 259 mV de perte ohmique, 0 de perte de transport (1,182 + 0,419 + 0,259 = 1,860 V) | – | mV |

Test de la pente de Tafel (`fits_pente`) : le modèle est ajusté trois fois, avec la pente de Tafel fixée à 46 mV par décade (valeur retenue, Padgett et al. 2025) et à 43,3 et 49 mV par décade (valeurs extrêmes mesurées par Padgett et al. 2023). Pour chaque ajustement : `b (mV/déc)` la pente, `alpha_a`, `i0a`, `Rtot` et `Bc` les paramètres ajustés, `RMSE_mV` et `MAE_mV` les écarts moyens (quadratique et absolu), `R2` la qualité.

| Pente de Tafel | i0a (A/cm²) | Rtot (Ω·cm²) | RMSE (mV) |
|---|---|---|---|
| 43,3 mV/déc | 2,9e-10 | 0,217 | 3,99 |
| 46 mV/déc (retenue) | 9,4e-10 | 0,216 | 3,97 |
| 49 mV/déc | 3,0e-9 | 0,214 | 3,95 |

Les trois ajustements sont aussi bons les uns que les autres : le profil mesuré ne permet pas de dire quelle pente est la bonne, donc la pente est prise dans la littérature au lieu d'être ajustée. Quand la pente change, `i0a` change pour compenser, et la résistance bouge à peine.
