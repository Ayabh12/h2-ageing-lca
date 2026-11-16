# Méthode

[English](METHOD.md) | **Français**

Cette page résume ce que calcule le code, et pourquoi. Chaque valeur de `config/default.yaml` est accompagnée de sa source.

## 1. Unités fonctionnelles et système

| Évaluation | Unité fonctionnelle | Ce qui vieillit |
|---|---|---|
| Pile seule | 1 km parcouru | le stack de pile seulement ; elle reçoit l'hydrogène de l'électrolyseur étudié à son état de référence (sans vieillissement, fabrication du stack exclue), comprimé : 4,503 kg CO2-éq/kg |
| Électrolyseur seul | 1 kg d'hydrogène produit | le stack d'électrolyseur |
| Chaîne complète | 1 km parcouru | électrolyseur, réservoir (perméation) et pile ensemble |

Horizon : 15 ans, 200 000 km (`horizon`). Électricité : mix résiduel français par défaut (79,6 g CO2-éq/kWh), le mix d'un électrolyseur raccordé au réseau qui n'achète pas de garanties d'origine ; le profil éolien mesuré donne seulement l'électricité consommée par kg d'hydrogène et son évolution avec l'âge, pas l'origine de l'électricité. Chaque évaluation compare la chaîne avec vieillissement à la même chaîne sans vieillissement (même profil, même électricité, même horizon, mêmes frontières et mêmes inventaires, un stack de chaque convertisseur). Dans le système : électricité et eau de l'électrolyseur, électricité de compression, fabrication des stacks et du réservoir, hydrogène perdu par perméation. Hors du système : auxiliaires, station hors compression, reste du véhicule, transports, fin de vie.

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

## 2. Pile à combustible (`src/h2ageing/pemfc.py`)

**Polarisation.** La tension complète d'une cellule contient les pertes d'activation et de transport des deux électrodes, et la perte ohmique. Seules les pertes de l'électrode à oxygène sont gardées (la cathode pour la pile, l'anode pour l'électrolyseur), pour deux raisons : la réaction de l'hydrogène a, sur platine en milieu acide, un courant d'échange plus élevé de plusieurs ordres de grandeur (Durst et al. 2014), donc sa perte est faible et presque proportionnelle au courant, et elle est comprise dans R ; et les pertes d'activation des deux électrodes varient toutes deux en ln j, donc une seule courbe tension-courant ne permet pas de les séparer. La tension d'une cellule de pile s'écrit :

V(j, t) = E_rev(T) − RT/(α_c F) · ln( j / (i0c · S(t)) ) − R(t) · j + B_c · ln(1 − j / i_lim)

E_rev(T) = 1,229 − 0,85·10⁻³ (T − 298,15). Les quatre paramètres i0c, R0, B_c et i_lim sont ajustés sur des points quasi stationnaires des mesures sur route (`scripts/fit_pemfc.py`), par moindres carrés bornés. Bornes, et valeurs publiées qu'elles encadrent : log10 i0c de −12 à −1 (Vetter & Schumacher 2019 ; Colombo et al. 2023) ; R0 de 0 à 0,3 Ω cm² (Colombo et al. 2023) ; B_c de 0 à 0,3 V (Almodfer et al. 2022) ; i_lim de 2,03 à 6 A/cm² (Bielefeld et al. 2024), la borne basse étant juste au-dessus de la plus forte densité de courant mesurée.

**Bilan d'hydrogène.** Le trajet mesuré (temps, courant, tension, 2 033 s, 20,32 km) est rejoué à chaque âge à puissance imposée : le courant qui fournit la puissance mesurée est trouvé par dichotomie (40 itérations), avec un facteur d'ancrage point par point pour que le modèle redonne le courant mesuré à l'âge zéro. L'hydrogène consommé suit la loi de Faraday, plus un courant de perte : l'écart entre l'hydrogène mesuré (0,196 kg) et la loi de Faraday est gardé constant ; la hausse du crossover s'y ajoute.

**Vieillissement, modèle semi-empirique** (cas pessimiste) : sa structure est physique, chaque mécanisme de dégradation agissant sur un terme de l'équation de polarisation ; ses lois d'évolution dans le temps sont ajustées sur des mesures de laboratoire, d'où le nom « semi-empirique ».
- surface de platine : dS/dt = −k S² exp(ω S) (Verducci et al.), k choisi pour que S(1000 h) soit égal à la valeur mesurée par Colombo et al. (2023). k est trouvé en inversant l'intégrale tabulée g(S) = ∫_S^1 exp(−ω s)/s² ds (méthode des trapèzes, 6 000 points) ;
- résistance de transport : R(t) = R0 + r t (écrite R0 (1 + k_R t) dans le code, avec k_R = r / R0), où r = [ΔV(1,8 A/cm², 1000 h) − RT/(α_c F) ln(1/S_1000)] / 1,8 / 1000 : la perte de tension mesurée à fort courant, moins la part déjà due à la perte de platine ;
- crossover : 2 mA/cm² à l'âge zéro, multiplié par le facteur mesuré en 1000 h (loi linéaire par défaut ; lois exponentielle et constante disponibles).

**Vieillissement, modèle linéaire** (cas optimiste et central) : V(t) = V(0) − μ t, avec μ = 10 % de la tension de cellule à 300 A, divisés par la durée de vie publiée (8 000 h, objectif du DOE ; 4 100 h, meilleure flotte du DOE). Le crossover reste constant.

**Fin de vie** : âge auquel la tension du stack à 300 A a perdu 10 % (DOE), trouvé par la méthode de Brent entre 0 et 60 000 h.

## 3. Électrolyseur (`src/h2ageing/pemwe.py`)

**État neuf** (ajusté par `scripts/fit_pemwe.py` sur le profil éolien de 4 h, pas de 1 s) :

V(j) = E_rev(T) + RT/(2 α_a F) · ln(j / i0a) + R j − B_c · ln(1 − j / i_lim)

α_a est fixé par la pente de Tafel de Padgett et al. (46 mV/décade à 80 °C) ; i0a, R et B_c sont ajustés (moindres carrés bornés, méthode *trust region reflective*, 50 points de départ, graine 180). Bornes, et valeurs publiées qu'elles encadrent : i0a de 10⁻¹⁴ à 10⁻¹ A/cm² (Marefatjouikilevaee et al. 2023) ; R de 0 à 1 Ω cm² (Weiß et al. 2019 ; Padgett et al. 2025 ; Fouda-Onana et al. 2016) ; B_c de 0 à 1 V (Almodfer et al. 2022). Le modèle est écrit à 80 °C, la température des essais qui donnent les constantes de vieillissement. Le profil donne E0 = 2 841 kWh, 52,93 kg d'hydrogène et SEC0 = 53,68 kWh/kg.

**Vieillissement, modèle semi-empirique** (cas pessimiste, Padgett et al. 2025 et Chandesris et al. 2015) :
- activité de l'anode f_A(t) = f_min + (1 − f_min) exp(−t/τ), qui donne une hausse de tension b/ln(10) · ln(1/f_A) ;
- résistance R(t) = R0 + (dérive de la HFR + dérive de la couche catalytique)/j_test · t ;
- rendement faradique, à partir de l'amincissement de la membrane : e/e0 = 1 − 0,5 t / t50.

**Vieillissement, modèle linéaire** : dérive constante μ par cellule (2,3 µV/h, objectif 2026 du DOE ; 4,8 µV/h, statut 2022 du DOE).

L'énergie sur le profil est mise à jour au premier ordre : E(t) = E0 + ΔV_uniforme · W0 + ΔR · W_j, avec W0 = Σ E_pas / V0 et W_j = Σ E_pas · j / V0. SEC(t) = E(t) / H2(t).

**Fin de vie** : tension en hausse de 10 % à la densité de courant moyenne du profil (méthode de Brent, de 0 à 400 000 h).

## 4. Réservoir (`src/h2ageing/tank.py`)

La perméation (mL/h/L à 55 °C, réservoir plein) augmente linéairement de P0 à P15 sur les 15 ans de la certification : 6 → 6, 6 → 14 et 6 → 46 (limite du règlement UN R134) dans les trois cas. Hydrogène perdu par km = P · V · ρ · 8 760 / (km par an).

Réservoir seul, par km (`tank.csv`) : fabrication d'un réservoir / 200 000 km, plus l'hydrogène perdu en moyenne, compté comme de l'hydrogène livré à l'état de référence (électrolyse et compression).

## 5. ACV (`src/h2ageing/chain.py`, `impacts.py`)

Chaque stack repart de l'état neuf quand il est remplacé. Nombre de stacks : n = ⌈L / t_FdV⌉ (entier, par défaut) ou max(1, L / t_FdV) (au prorata : la part de vie du stack utilisée, avec au moins le premier stack).

- Pile seule, par km : m0 · h̄ · I_H2,réf + n · F_stack / L_km, où h̄ est la consommation moyenne d'hydrogène sur l'horizon rapportée à l'état neuf (méthode des trapèzes sur les âges), et I_H2,réf l'impact d'1 kg d'hydrogène produit par un électrolyseur neuf, puis comprimé.
- Électrolyseur seul, par kg : SEC̄ · I_kWh + I_eau + n · F_stack / H2_produit, avec l'énergie et l'hydrogène intégrés sur l'horizon (20 001 points).
- Chaîne complète, par km : l'hydrogène consommé (pile à son âge) plus l'hydrogène perdu (réservoir à son âge) est produit par l'électrolyseur à son âge, puis comprimé ; intégration sur 15 ans (80 points par an). Les stacks d'électrolyseur sont partagés avec le reste de la production : le véhicule porte la part de l'hydrogène qu'il utilise.

Impacts : EF 3.1, 16 catégories. Score unique : Σ (impact / facteur de normalisation × facteur de pondération).

## 6. Analyses de sensibilité

| Test | Question | Script |
|---|---|---|
| Source d'électricité | la conclusion tient-elle avec une électricité plus propre ? | `run.py --set usage.electricity_electrolyser=...` |
| Heures de l'électrolyseur par an | les 6 000 h/an choisies comptent-elles ? Les heures publiées à pleine charge sont converties en heures au profil mesuré en les divisant par sa charge moyenne (710/1 250 = 0,568) | `run.py --set usage.electrolyser_hours_per_year=...` |
| Comptage des stacks | et si le dernier stack avait une seconde vie ? | `run.py --set usage.stack_counting=prorata` |
| Seuil de durée de vie | à partir de quelle durée de vie un seul stack suffit-il ? | `threshold.py` |
| Loi de crossover | la forme inconnue de la hausse du crossover change-t-elle le résultat ? | `fuel_cell_tests.py` |
| Constantes semi-empiriques | quelle constante de laboratoire change le plus le résultat ? | `semi_empirical_constants.py` |
| Globale (Sobol) | laquelle des huit entrées, variant ensemble, explique le résultat ? | `sobol.py` |

## 7. Limites principales

La liste complète, avec l'effet de chaque limite et la façon de la tester, est dans [LIMITS.fr.md](LIMITS.fr.md).

- Aucune vitesse de dégradation n'a été mesurée sur les stacks étudiés.
- Les constantes de laboratoire (cas pessimiste) sont mesurées sur des cellules plus sollicitées que des stacks commerciaux ; les lois semi-empiriques sont extrapolées au-delà de la durée des essais.
- Le modèle linéaire ne voit ni la hausse du crossover de la pile, ni la perte rapide d'activité de l'anode.
- Le résultat de la pile évolue par paliers avec le nombre de stacks : toute fin de vie comprise entre la moitié de l'horizon et l'horizon donne deux stacks.
- Les inventaires sont pris dans la littérature et mis à l'échelle (Mori et al. 2023, Lundberg 2019, Benitez et al. 2021) ; les auxiliaires sont exclus.

## Références pour la structure du modèle et les bornes d'ajustement

- Almodfer R. et al. (2022). Improving parameter estimation of fuel cell using honey badger optimization algorithm. Frontiers in Energy Research 10, 875332 (Table 2 corrected in 13, 1588458, 2025).
- Bielefeld N.M. et al. (2024). A one-dimensional computational model to identify operating conditions and cathode flow channel dimensions for a PEM fuel cell. Hydrogen 5, 624–643. doi:10.3390/hydrogen5030033
- Colombo E. et al. (2023). PEMFC performance decay during real-world automotive operation. Journal of Power Sources 553, 232246.
- Durst J. et al. (2014). New insights into the electrochemical hydrogen oxidation and evolution reaction mechanism. Energy & Environmental Science 7, 2255–2260.
- Fouda-Onana F. et al. (2016). Investigation on the degradation of MEAs for PEM water electrolysers part I. International Journal of Hydrogen Energy 41, 16627–16636.
- Marefatjouikilevaee H., Auger F., Olivier J.-C. (2023). Static and dynamic electrical models of PEM electrolysers: a comprehensive review. Energies 16, 6503. doi:10.3390/en16186503
- Padgett E. et al. (2025). Quantifying sources of voltage decay in long-term durability testing for PEM water electrolysis. Journal of The Electrochemical Society 172, 054508.
- Vetter R., Schumacher J.O. (2019). Experimental parameter uncertainty in PEM fuel cell modeling. Part I. Journal of Power Sources 438, 227018.
- Weiß A. et al. (2019). Impact of intermittent operation on lifetime and performance of a PEM water electrolyzer. Journal of The Electrochemical Society 166, F487–F497.
