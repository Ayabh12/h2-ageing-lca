# Exemples commentés

[English](USE_CASES.md) | **Français**

Chaque exemple pose une question, donne la commande qui y répond et montre le résultat obtenu avec les données fournies (changement climatique, chaîne complète, g CO2-éq/km). Toutes les commandes tournent en quelques secondes, sans ecoinvent. Changez les valeurs pour répondre à votre propre question.

Les résultats de référence, pour comparaison :

| | Sans vieillissement | Optimiste | Central | Pessimiste |
|---|---|---|---|---|
| Chaîne complète (g CO2-éq/km) | 74,12 | 77,84 (+5,0 %) | 97,15 (+31,1 %) | 100,06 (+35,0 %) |

---

## 1. Et si l'électrolyseur fonctionne à l'électricité éolienne ?

**Pourquoi se poser la question :** la référence utilise le mix résiduel français, la source testée la plus carbonée. Un projet avec un contrat d'achat d'électricité éolienne utiliserait une autre source.

```bash
python scripts/run.py --set usage.electricity_electrolyser=wind_FR
```

| | Sans vieillissement | Optimiste | Central | Pessimiste |
|---|---|---|---|---|
| Chaîne complète (g CO2-éq/km) | 41,22 | 42,32 (+2,7 %) | 61,27 (+48,6 %) | 61,97 (+50,3 %) |

**Ce que ça montre :** la chaîne émet beaucoup moins, mais l'effet relatif du vieillissement est plus grand. Les stacks de remplacement ajoutent le même impact quelle que soit l'électricité, et ils pèsent plus quand le reste est plus propre. Sources disponibles : `residual_mix_FR`, `average_mix_FR`, `nuclear_FR`, `wind_FR`, `photovoltaic` ; ajoutez la vôtre comme une colonne de `data/impacts/electricity_per_kWh.csv`.

## 2. Et si mon stack de pile dure plus longtemps ?

**Pourquoi se poser la question :** le cas central utilise 4 100 h jusqu'à la fin de vie (meilleure flotte du DOE, 2006–2016). Un stack plus récent peut durer plus longtemps.

```bash
python scripts/run.py --set cases.central.fuel_cell.hours_to_end_of_life=6000
```

| | Central (référence, 4 100 h) | Central avec 6 000 h |
|---|---|---|
| Stacks de pile | 2 | 1 |
| Chaîne complète (g CO2-éq/km) | 97,15 (+31,1 %) | 78,88 (+6,4 %) |

**Ce que ça montre :** au-delà de l'horizon de 5 554 heures de fonctionnement, un seul stack suffit, et la hausse passe de +31 % à +6 %. L'exemple 5 donne les seuils exacts.

## 3. Et si le dernier stack a une seconde vie ?

**Pourquoi se poser la question :** la référence compte chaque stack commencé comme un stack entier (`integer`). Si la vie restante du dernier stack est utilisée ailleurs, seule la part de vie utilisée devrait être comptée (`prorata`).

```bash
python scripts/run.py --set usage.stack_counting=prorata
```

| | Optimiste | Central | Pessimiste |
|---|---|---|---|
| Hausse, comptage entier (référence) | +5,0 % | +31,1 % | +35,0 % |
| Hausse, comptage au prorata | +4,6 % | +14,7 % | +32,8 % |

**Ce que ça montre :** seul le cas central change beaucoup, car son second stack de pile n'est utilisé qu'à 35 % avant la fin de l'horizon. Le prorata est une borne basse : il suppose une filière de seconde vie qui n'existe pas aujourd'hui pour ces stacks.

## 4. Et si le véhicule roule moins ?

**Pourquoi se poser la question :** 200 000 km est la cible de Toyota pour le stack de la Mirai II ; un véhicule peut être retiré plus tôt.

```bash
python scripts/run.py --set horizon.vehicle_km_total=150000
```

| | Sans vieillissement | Optimiste | Central | Pessimiste |
|---|---|---|---|---|
| Chaîne complète (g CO2-éq/km) | 84,25 | 87,56 (+3,9 %) | 113,87 (+35,2 %) | 116,23 (+38,0 %) |

**Ce que ça montre :** la fabrication est répartie sur moins de kilomètres, donc toutes les valeurs augmentent, et le poids du stack de remplacement aussi.

## 5. Combien de temps un stack de pile doit-il durer pour éviter un remplacement ?

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
| de 1 851 à 2 777 h | 3 | environ +57 % |
| de 2 777 à 5 554 h | 2 | environ +31 % |
| plus de 5 554 h | 1 | environ +7 % |

**Ce que ça montre :** le résultat évolue par paliers. Un stack qui dure 4 100 h et un stack qui dure 5 000 h demandent tous deux un remplacement, donc ils donnent presque le même résultat (+31,1 % et +31,4 %). Un stack qui passe de 5 500 à 5 600 h franchit le seuil : un seul stack suffit, et la hausse tombe d'environ +31 % à environ +7 %. Gagner quelques centaines d'heures ne sert à rien tant qu'aucun seuil n'est franchi ; pour ce véhicule, l'objectif est de dépasser 5 554 h.

## 6. Et si j'utilise mes propres constantes de vieillissement ?

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

## 7. Quelles entrées comptent le plus, toutes ensemble ?

**Pourquoi se poser la question :** les exemples ci-dessus changent une entrée à la fois. L'analyse de sensibilité globale change huit entrées ensemble et les classe.

**Ce qu'est l'analyse de Sobol.** Elle fait varier toutes les entrées en même temps, un grand nombre de fois (10 240 calculs), et mesure la part de la variation du résultat expliquée par chaque entrée. Son indice total va de 0 (l'entrée ne compte pas) à 1 (l'entrée explique toute la variation, seule ou avec les autres).


```bash
python scripts/sobol.py --out results      # environ 15 min sur 2 cœurs
```

**Ce que ça montre :** l'impact absolu dépend surtout de la source d'électricité (indice de Sobol total 0,78) ; la hausse due au vieillissement dépend presque seulement de la durée de vie du stack de pile (0,94). Les facteurs et leurs plages sont dans `global_sensitivity` de `config/default.yaml`.

---

Pour aller plus loin, jusqu'à remplacer une loi de vieillissement : [ADAPT.fr.md](ADAPT.fr.md). Toutes les clés que vous pouvez changer : [CUSTOMISE.fr.md](CUSTOMISE.fr.md).
