# Limites et domaine de validité

[English](LIMITS.md) | **Français**

Ce que le modèle ne sait pas, l'effet sur les résultats, et ce qui est fait.

**Ce que sont les résultats :** la hausse de l'impact due au vieillissement, avec et sans vieillissement, pour chaque composant et pour la chaîne. Trois cas **encadrent** le vieillissement ; ils **ne prédisent pas** la durée de vie exacte de ces stacks.

## 1. Données

| Limite | Effet | Ce qui est fait | Où |
|---|---|---|---|
| Aucune vitesse de dégradation publiée pour les stacks du Nel MC250 et de la Mirai II | durée de vie inconnue | trois cas l'encadrent ; votre valeur se saisit en une ligne | [METHOD](METHOD.fr.md#les-trois-cas-de-vieillissement) ; [GUIDE](GUIDE.fr.md), exemple 2 |
| Constantes pessimistes issues de cellules de laboratoire, plus sollicitées (3 A/cm² pour l'électrolyseur) | cas pessimiste probablement trop sévère | utilisé comme borne haute ; chaque constante testée contre une autre valeur publiée | `semi_empirical_constants.py` ; [GUIDE](GUIDE.fr.md), exemple 5 |
| Lois semi-empiriques extrapolées au-delà des essais (×2,9 pile, ×8,5 électrolyseur) | forme de la courbe non mesurée en fin de vie | trois lois de crossover comparées : même nombre de stacks | `fuel_cell_tests.py` |
| Crossover de la pile mesuré sur 1 000 h seulement | consommation d'hydrogène en fin de vie incertaine | lois linéaire, exponentielle et constante comparées | `fuel_cell_tests.py` ; [GUIDE](GUIDE.fr.md), section 3.2 |
| Aucune loi publiée pour la perméation du réservoir | effet encadré, pas modélisé | de 6 à 46 mL/h/L (limite UN R134) : moins d'1 g CO2-éq/km | [METHOD](METHOD.fr.md), sections 4 et 7 |
| Surface de la pile (297 cm²) estimée ; cellules (200) et surface (1 500 cm²) de l'électrolyseur choisies | fixent la densité de courant | justifiées ; modifiables | [METHOD](METHOD.fr.md), sections 2.5 et 3.1 |
| 3,64 g d'hydrogène non expliqués sur le trajet (écart entre l'hydrogène mesuré au réservoir, 0,196 kg, et celui calculé à partir du courant, 0,192 kg) | origine inconnue | gardé constant, comme un courant de perte | [METHOD](METHOD.fr.md), section 2.2 ; `src/h2ageing/pemfc.py` |

## 2. Conditions de fonctionnement

| Limite | Effet | Ce qui est fait | Où |
|---|---|---|---|
| Un seul trajet (2 033 s, 20,32 km) rejoué toute la vie ; un seul profil éolien de 4 h répété | un autre usage changerait la consommation | fichiers remplaçables ; vitesse moyenne testée (48 au lieu de 36 km/h) | [GUIDE](GUIDE.fr.md), section 3.5 ; `fuel_cell_tests.py` |
| Températures constantes (80 °C électrolyseur, 70 °C pile) | variations non modélisées | testé sur l'électrolyseur avec des rapports publiés à 60 °C : hausse de la chaîne +34,5 et +34,9 % au lieu de +35,0 % | `semi_empirical_constants.py` ; [GUIDE](GUIDE.fr.md), exemple 5 |
| Démarrages, arrêts et attentes non modélisés | dégradation des arrêts non comptée | non testé ; une vitesse linéaire plus forte peut la représenter | [GUIDE](GUIDE.fr.md), section 3.2 |

## 3. Périmètre et méthode

| Limite | Ce que cela veut dire | Où |
|---|---|---|
| Stacks et réservoir seulement | auxiliaires, station hors compression, reste du véhicule, transports et fin de vie hors système | [METHOD](METHOD.fr.md), section 1 |
| Inventaires tirés de la littérature et mis à l'échelle (Mori 2023, Lundberg 2019, Benitez 2021) | avec les valeurs d'origine, hausse centrale de +22,9 à +28,2 % au lieu de +31,1 %, même nombre de stacks | [inventaires](../data/inventories/README.fr.md) ; se refait avec votre fichier de fabrication ([GUIDE](GUIDE.fr.md), section 3.4) |
| ecoinvent non distribué | les résultats tournent sans licence ; recalculer une fabrication en demande une | [GUIDE](GUIDE.fr.md), section 3.4 |
| Modèle linéaire (optimiste, central) | ne voit ni la hausse du crossover ni la perte rapide de l'anode en début de vie | [METHOD](METHOD.fr.md), sections 2.4 et 3.3 |
| Sensibilité, pas incertitude | les entrées sont encadrées et classées, sans probabilité : trop peu de données publiées | [METHOD](METHOD.fr.md), section 6 |

## 4. Domaine de validité

| | Exemples |
|---|---|
| **Utilisable directement** (changer une valeur, [GUIDE](GUIDE.fr.md) section 3) | électricité, durées de vie et constantes de vieillissement, kilométrage, heures de l'électrolyseur, compression, impact de fabrication, comptage des stacks |
| **Utilisable après adaptation des données** (sans toucher au code) | autre stack PEM (réajuster les courbes, `fit_pemfc.py`, `fit_pemwe.py`) ; autre trajet ou profil ; autre véhicule PEM (bus, camion : remplacer les durées de vie DOE) ; autre réservoir ; autre inventaire (licence ecoinvent) |
| **Hors domaine** (nouvelles équations nécessaires) | autre technologie (alcalin, SOEC, AEM, SOFC) ; autre stockage (liquide, hydrures) ; auxiliaires ; transport, distribution, recyclage ; autres vieillissements (rupture de membrane, démarrages à froid, températures variables) ; électricité qui change sur 15 ans ; empreinte totale du véhicule |
