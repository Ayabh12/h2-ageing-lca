# Inventaires de fabrication

[English](README.md) | **Français**

Chaque fichier liste ce qu'il faut pour fabriquer **une unité** d'un composant : un stack de pile, un stack d'électrolyseur ou un réservoir. Chaque ligne est une entrée : un matériau, une énergie ou une ressource, avec sa quantité et la donnée ecoinvent 3.11 (cut-off) à laquelle elle est reliée. L'impact du composant est la somme des impacts de ces entrées, chacune comptée de l'extraction des ressources jusqu'au marché ([ce que comprend chaque impact](../../docs/METHOD.fr.md#ce-que-comprend-chaque-impact)).

Colonnes des fichiers CSV :

| Colonne | Signification |
|---|---|
| `part` | partie du composant à laquelle appartient l'entrée (quand la source la donne) |
| `input` | matériau, énergie ou ressource, en clair |
| `amount`, `unit` | quantité pour une unité du composant |
| `flow_type` | `material` (matériau), `energy` (énergie), `processing` (transformation d'un matériau, comme le tréfilage) ou `resource` (prélevée directement dans la nature) |
| `ecoinvent_activity`, `reference_product`, `location`, `database` | la donnée ecoinvent reliée à l'entrée |
| `ecoinvent_code` | code de la donnée ecoinvent, quand il sert à l'identifier |
| `biosphere_category` | pour une ressource, sa catégorie dans la base biosphère |
| `included` | `yes` ou `no` : mettez `no` pour retirer une ligne quand l'impact est reconstruit |
| `source` | d'où vient la quantité |

Pour afficher les trois inventaires (sans licence) : `python scripts/build_fabrication_brightway.py --check`. Pour recalculer les impacts après avoir changé une quantité, avec votre propre licence ecoinvent : `pip install -r requirements-brightway.txt`, puis `python scripts/build_fabrication_brightway.py --project h2ageing --import-ecoinvent` ; le script demande votre identifiant et votre mot de passe ecoinvent, importe ecoinvent 3.11 cut-off dans Brightway et écrit un nouveau fichier d'impacts. Avec les inventaires tels que fournis, il redonne les mêmes impacts qu'Activity Browser dans les 16 catégories EF 3.1 (écart inférieur à 0,01 % ; changement climatique : 3 698,3, 39 509,4 et 2 332,0 kg CO2-éq) : lancez-le une fois ainsi pour vérifier votre installation.

La dernière colonne de chaque tableau donne la donnée ecoinvent 3.11 cut-off reliée à l'entrée. Pour le réservoir, l'activité est identifiée par son code ecoinvent, donné en entier dans le fichier CSV.

---

## Inventaire du stack de pile (128 kW)

`fuel_cell_stack_128kW.csv` · Source : Mori et al. 2023 (stack de 48 kW), mis à l'échelle par 128/48. La source donne les matériaux du stack entier, sans leur répartition par partie.

| Partie | Entrée | Quantité | Unité | Flux ecoinvent 3.11 cut-off utilisé |
|---|---|---|---|---|
| Matériaux du stack | Acier inoxydable (acier au chrome 18/8) | 59,87 | kg | `market for steel, chromium steel 18/8, hot rolled` |
| | Fibre de verre | 10,1 | kg | `market for glass fibre` |
| | Acier faiblement allié | 7,52 | kg | `steel production, low-alloyed, hot rolled` |
| | Polytéréphtalate d'éthylène (PET) | 4,85 | kg | `polyethylene terephthalate production, granulate, amorphous` |
| | Silicone | 3,36 | kg | `market for silicone product` |
| | Acrylonitrile | 3,33 | kg | `market for acrylonitrile` |
| | Cuivre | 2,53 | kg | `market for copper, cathode` |
| | Eau déionisée | 1,31 | kg | `market for water, deionised` |
| | Alcool éthoxylé (AE11) | 0,587 | kg | `market for ethoxylated alcohol (AE11)` |
| | Tétrafluoroéthylène | 0,384 | kg | `market for tetrafluoroethylene` |
| | Noir de carbone | 0,104 | kg | `market for carbon black` |
| | Platine | 0,069 | kg | `market for platinum` |
| | Tréfilage du cuivre (transformation des 2,53 kg de cuivre) | 2,53 | kg | `market for wire drawing, copper` |
| Énergie de fabrication | Électricité, mix résiduel français, haute tension | 1 096 | kWh | `electricity, high voltage, residual mix` |
| **Total** | **matériaux** | **94,0** | **kg** | |
| | **énergie** | **1 096** | **kWh** | |

Impact d'un stack sur le changement climatique : 3 698 kg CO2-éq.

## Inventaire du stack d'électrolyseur (1,25 MW)

`electrolyser_stack_1p25MW.csv` · Source : Lundberg 2019 (par MW de stack), mis à l'échelle de 1,25 MW.

| Partie | Entrée | Quantité | Unité | Flux ecoinvent 3.11 cut-off utilisé |
|---|---|---|---|---|
| Plaques bipolaires | Titane | 660 | kg | `market for titanium` |
| Enveloppe externe | Acier inoxydable (acier au chrome 18/8) | 125 | kg | `steel production, electric, chromium steel 18/8` |
| Collecteurs de courant | Aluminium, alliage corroyé | 33,75 | kg | `market for aluminium, wrought alloy` |
| | Cuivre | 5,625 | kg | `market for copper, cathode` |
| Membrane | Tétrafluoroéthylène | 20 | kg | `market for tetrafluoroethylene` |
| Électrodes | Charbon actif, granulé | 11,25 | kg | `activated carbon production, granular from hard coal` |
| | Iridium (ressource, voir plus bas) | 0,9375 | kg | `Iridium` · biosphère, *natural resource::in ground* |
| | Platine | 0,09375 | kg | `market for platinum` |
| Énergie d'assemblage | Électricité, mix résiduel français, moyenne tension | 6 700 | kWh | `electricity, medium voltage, residual mix` |
| **Total** | **matériaux et ressources** | **856,7** | **kg** | |
| | **énergie** | **6 700** | **kWh** | |

Impact d'un stack sur le changement climatique : 39 509 kg CO2-éq. L'iridium n'a pas de donnée ecoinvent : il est compté comme une ressource prélevée dans le sol, donc son extraction pèse sur l'épuisement des ressources, mais aucun impact de sa transformation n'est compté.

## Inventaire du réservoir d'hydrogène (type IV, 5,6 kg, 700 bar)

`tank_type_IV.csv` · Source : Benitez et al. 2021.

| Partie | Entrée | Quantité | Unité | Flux ecoinvent 3.11 cut-off utilisé |
|---|---|---|---|---|
| Coque composite | Fibre de carbone | 76 | kg | carbon fibre (code `9ad06220…`) |
| | Résine époxy | 26 | kg | epoxy resin (code `52da7875…`) |
| Liner (enveloppe intérieure) | Polyéthylène haute densité | 7,5 | kg | high-density polyethylene (liner) (code `1cbbd15b…`) |
| Énergie de fabrication | Électricité, haute tension, marché mondial | 338,64 | kWh | electricity, high voltage, market group for electricity, high voltage (code `8a929576…`) |
| | Électricité, basse tension, cogénération au gaz naturel | 43,2 | kWh | electricity, low voltage, from heat and power co-generation, natural gas (code `1f3b8a35…`) |
| **Total** | **matériaux** | **109,5** | **kg** | |
| | **énergie** | **381,84** | **kWh** | |

Impact d'un réservoir sur le changement climatique : 2 332 kg CO2-éq, dont 2 075 kg pour les matériaux et 257 kg pour l'énergie de fabrication.
