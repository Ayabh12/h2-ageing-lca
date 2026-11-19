# Limites et domaine de validité

[English](LIMITS.md) | **Français**

Cette page liste ce que le modèle ne sait pas ou ne comprend pas, l'effet sur les résultats, et la façon dont chaque limite est testée ou pourrait être levée. Elle vous aide à juger quand les résultats s'appliquent à votre propre cas.

## Ce que sont les résultats, et ce qu'ils ne sont pas

- Ils sont **l'effet du vieillissement sur l'ACV de cette chaîne** : la hausse de l'impact entre la même chaîne avec et sans vieillissement, pour chaque composant et pour la chaîne complète.
- Ils **encadrent** le vieillissement avec trois cas construits à partir de valeurs publiées ; ils **ne prédisent pas** la durée de vie exacte de ces stacks.
- Ils sont calculés avec des impacts caractérisés tirés d'ecoinvent 3.11 (cut-off) et d'EF 3.1. Le changement climatique est l'indicateur principal ; les 16 catégories EF 3.1 et le score unique sont aussi calculés.

## Limites des données

| Limite | Effet sur les résultats | Comment elle est traitée |
|---|---|---|
| Aucune vitesse de dégradation n'est publiée pour le stack du Nel MC250 ni pour celui de la Toyota Mirai II | La durée de vie des stacks n'est pas connue exactement | Trois cas l'encadrent : objectif du DOE (optimiste), statut ou valeur de flotte du DOE (central), constantes de laboratoire (pessimiste). Votre propre valeur se saisit en une ligne (GUIDE.fr.md, exemple 2) |
| Les constantes pessimistes viennent de cellules de laboratoire, plus sollicitées que des stacks commerciaux (par exemple 3 A/cm² constants pour l'électrolyseur) | Le cas pessimiste est probablement au-dessus de la dégradation d'un stack industriel | Il sert seulement de borne haute ; chaque constante est testée contre une autre valeur publiée (`scripts/semi_empirical_constants.py`) |
| Les lois semi-empiriques sont extrapolées au-delà de la durée des essais (2,9 fois pour la pile, 8,5 fois pour l'électrolyseur) | La forme de la courbe après les essais n'est pas mesurée | Trois lois de crossover sont comparées (`scripts/fuel_cell_tests.py`) ; le nombre de stacks ne change pas |
| Le crossover de la pile n'est mesuré que sur 1 000 h ; des essais publiés montrent une hausse brutale après 500 à 800 h, qu'aucune loi continue ne prédit | La consommation d'hydrogène en fin de vie est incertaine | Des lois linéaire, exponentielle et constante sont comparées |
| Aucune loi de vieillissement n'est publiée pour la perméation du réservoir | L'effet du réservoir est encadré, pas modélisé par une loi | De l'absence de hausse jusqu'à la limite réglementaire (46 mL/h/L) : moins d'1 g CO2-éq/km dans tous les cas |
| La surface active de la pile (297 cm²) est estimée dans la littérature ; le nombre de cellules (200) et la surface (1 500 cm²) de l'électrolyseur ne sont pas publiés et sont choisis | Ils fixent la densité de courant utilisée par les lois de vieillissement | Chaque choix est justifié dans `config/default.yaml` et `data/parameters/` ; ils peuvent être changés et les modèles réajustés |
| L'hydrogène mesuré sur le trajet de la pile dépasse de 3,64 g l'hydrogène expliqué par le courant | Son origine est inconnue | Il est gardé constant dans le temps, comme un courant de perte |

## Limites des conditions de fonctionnement

| Limite | Effet | Comment la lever |
|---|---|---|
| Pile : la courbe de polarisation est ajustée sur les 12 enregistrements sur route, mais la phase d'usage rejoue à chaque âge un seul trajet mesuré (type WLTP, 2 033 s, 20,32 km), comme si toute la vie du véhicule suivait ce trajet. Électrolyseur : un profil éolien de 4 heures, répété | Un autre trajet ou un autre profil éolien donnerait une autre consommation, et peut-être une autre vitesse de vieillissement | Remplacer le fichier du trajet ou du profil (GUIDE.fr.md, section 3.5) ; la vitesse moyenne du trajet est testée (48 au lieu de 36 km/h : `scripts/fuel_cell_tests.py`) |
| Températures constantes (80 °C pour l'électrolyseur, 70 °C pour la pile), celles des essais qui donnent les constantes de vieillissement | Les variations de température ne sont pas modélisées | Des rapports publiés à 60 °C peuvent être appliqués aux constantes de l'électrolyseur (`scripts/semi_empirical_constants.py`) |
| Le vieillissement suit les heures de fonctionnement ; démarrages, arrêts et périodes d'attente ne sont pas modélisés à part | Les arrêts au potentiel de circuit ouvert, connus pour aggraver la dégradation de l'électrolyseur, ne sont pas inclus | Utiliser une vitesse plus forte dans le modèle linéaire pour les représenter |

## Limites du périmètre

- **Stacks et réservoir seulement.** Les auxiliaires, la station de distribution hors compression, le reste du véhicule, les transports, la fin de vie et le recyclage sont hors du système : ils ne sont pas touchés par les mécanismes de vieillissement étudiés.
- **La compression ne vieillit pas :** 2,8 kWh par kg dans tous les cas.
- **Inventaires tirés de la littérature et mis à l'échelle :** stack de pile d'après Mori et al. (2023, 48 kW mis à l'échelle de 128 kW), stack d'électrolyseur d'après Lundberg (2019, par MW), réservoir d'après Benitez et al. (2021). Avec les valeurs publiées par ces sources au lieu des nôtres, la hausse de la chaîne dans le cas central passe de +31,1 % à une valeur entre +22,9 % et +28,2 %, avec le même nombre de stacks.
- **ecoinvent n'est pas distribué.** Tous les résultats tournent à partir des impacts caractérisés fournis dans `data/impacts` ; reconstruire les impacts de fabrication après avoir changé un inventaire nécessite votre propre licence ecoinvent.

## Limites de la méthode

- **Le modèle linéaire** (cas optimiste et central) ne voit ni la hausse du crossover de la pile, ni la perte rapide, en début de vie, de l'activité de l'anode de l'électrolyseur ; le modèle semi-empirique les voit.
- **Les analyses de sensibilité ne sont pas une analyse d'incertitude.** Elles encadrent et classent les entrées ; elles ne donnent pas de probabilité pour le résultat, car les données de vieillissement publiées sont trop peu nombreuses pour construire des distributions de probabilité sans les inventer.

## Domaine de validité

Le modèle répond à une question précise : **de combien le vieillissement des stacks change l'ACV d'une chaîne hydrogène PEM**. Selon ce que vous changez, il s'applique directement, après adaptation des données, ou pas du tout.

**1. Utilisable directement, en changeant une valeur** (section 3 du [guide](GUIDE.fr.md)) :

- une autre source d'électricité (une des cinq fournies, ou une nouvelle si vous avez son impact par kWh) ;
- une autre durée de vie ou vitesse de dégradation des stacks, d'autres constantes de vieillissement ;
- un autre kilométrage, un autre horizon, d'autres heures de fonctionnement de l'électrolyseur ;
- une autre énergie de compression, un autre impact de fabrication, une autre règle de comptage des stacks.

**2. Utilisable après adaptation des données, sans changer le code :**

- **un autre stack PEM** (électrolyseur ou pile) : réajuster les courbes de polarisation sur ses propres mesures (`scripts/fit_pemfc.py`, `scripts/fit_pemwe.py`), donner son nombre de cellules, sa surface active et ses propres données de vieillissement ;
- **un autre trajet ou un autre profil de fonctionnement** : remplacer les fichiers de mesures ;
- **un autre véhicule à pile PEM** (bus, camion) : donner son trajet mesuré, son stack et son kilométrage ; les durées de vie du DOE, établies pour des voitures, ne s'appliquent alors plus et doivent être remplacées ;
- **un autre réservoir** (autre type ou autre volume) : donner son inventaire et sa perméation ;
- **un autre inventaire de fabrication** : avec une licence ecoinvent.

**3. Hors du domaine : le modèle ne fournit pas de résultat valable** et il faudrait écrire de nouvelles équations :

- **une autre technologie** : électrolyse alcaline, à oxyde solide (SOEC) ou à membrane échangeuse d'anions (AEM), pile à oxyde solide (SOFC). Les courbes de polarisation et les lois de vieillissement sont propres au PEM (platine, membrane, iridium) ;
- **un autre mode de stockage** : hydrogène liquide, hydrures, transport par canalisation ;
- **des auxiliaires** : compresseur d'air, humidificateur, refroidissement, électronique de puissance, équipements de l'électrolyseur hors stack. Ni leur consommation, ni leur fabrication, ni leur vieillissement ne sont modélisés ; en ajouter un demande de nouvelles équations, pas seulement une donnée ;
- **des étapes hors périmètre** : transport et distribution de l'hydrogène, station hors compression, fin de vie et recyclage des stacks (platine, iridium) ;
- **d'autres formes de vieillissement** : vieillissement de la compression, défaillances brutales (rupture de membrane), effet propre des démarrages et des arrêts, températures variables, démarrages à froid ;
- **une électricité qui change au fil des 15 ans** : le modèle utilise une même source sur tout l'horizon ;
- **l'empreinte totale d'un véhicule** : seuls les stacks, le réservoir et la production d'hydrogène sont comptés. Le résultat mesure l'effet du vieillissement, pas l'impact complet du véhicule.
