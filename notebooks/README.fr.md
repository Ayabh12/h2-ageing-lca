# Notebooks de recherche (en français)

[English](README.md) | **Français**

Ce sont les notebooks de recherche d'origine de ce travail, conservés tels qu'ils ont été exécutés (sorties comprises). Le paquet Python de `src/h2ageing` donne les mêmes résultats à partir d'un fichier de configuration et est plus facile à modifier ; ces notebooks gardent tout le détail, les figures et les analyses de sensibilité supplémentaires.

Chaque notebook prépare ses propres fichiers d'entrée dans sa première cellule (« 0. Fichiers d'entrée ») : il les prend dans `../data` quand il est lancé dans ce dépôt, ou les télécharge depuis ce dépôt GitHub public quand le notebook est lancé seul (connexion internet nécessaire). Un notebook peut donc être téléchargé et lancé seul. `prepare_inputs.py` fait la même chose pour tous les notebooks à la fois :

```bash
cd notebooks
python prepare_inputs.py
jupyter lab
```

Ordre d'exécution : `Fitting_polarisation_Mirai_II`, `AB_vieillissement_PEMWE`, `AB_vieillissement_PEMFC`, `AB_vieillissement_trois_cas`, puis les autres (certains lisent les fichiers de résultats écrits par les précédents).

| Notebook | Contenu |
|---|---|
| `Fitting_polarisation_Mirai_II` | courbe de polarisation de la pile : points quasi stationnaires, courbe médiane, ajustement à départs multiples, bootstrap, validation croisée par enregistrement |
| `AB_vieillissement_PEMWE` | électrolyseur : ajustement sur le profil éolien, trajectoires de vieillissement, fin de vie ; écrit `pemwe_parametres.json` |
| `AB_vieillissement_PEMFC` | pile : lois de vieillissement, fin de vie, hydrogène par trajet selon l'âge, lois de crossover |
| `AB_vieillissement_trois_cas` | **résultats de référence** : trois cas, fin de vie, chaque convertisseur, chaîne, 16 catégories, sensibilité (électricité, constantes, heures) ; les vérifie par rapport aux valeurs de référence |
| `AB_vieillissement_fabrication` | inventaires de fabrication et chaîne sur la vie du véhicule |
| `AB_vieillissement_couplage` | couplage des trois composants dans le temps |
| `AB_vieillissement_normalisation` | normalisation et pondération EF 3.1, score unique par poste, Monte Carlo |
| `AB_vieillissement_ACV_sensibilite` | analyses de sensibilité supplémentaires |
| `AB_vieillissement_comparaison_modeles` | modèles linéaire et semi-empirique comparés, validation par les essais de Toyota |

`medium.xlsx`, `nuc.xlsx`, `wind.xlsx` et `pv.xlsx` sont les impacts d'1 kWh exportés d'Activity Browser (résultats caractérisés seulement).

Note sur les noms : dans `AB_vieillissement_PEMWE`, les scénarios appelés *Optimiste*, *Moyen* et *Pessimiste* sont trois variantes de la perte d'activité de l'anode dans le modèle semi-empirique de l'électrolyseur (activité finale 0,49, 0,30 et 0,112), explorées pendant la recherche. Seule la dernière est utilisée dans les résultats, comme cas pessimiste. Les trois cas des résultats (optimiste, central, pessimiste) sont définis dans `config/default.yaml` et calculés dans `AB_vieillissement_trois_cas`.
