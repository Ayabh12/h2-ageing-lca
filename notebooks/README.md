# Research notebooks (French)

These are the original research notebooks of this work, kept as they were run (outputs included). The Python package in `src/h2ageing` gives the same results from a configuration file and is easier to modify; these notebooks keep the full detail, the figures and the additional sensitivity analyses.

Prepare the inputs once, then run the notebooks in this folder:

```bash
cd notebooks
python prepare_inputs.py
jupyter lab
```

| Notebook | Content |
|---|---|
| `Fitting_polarisation_Mirai_II` | fuel cell polarisation curve: quasi-steady points, median curve, multistart fit, bootstrap, cross-validation by recording |
| `AB_vieillissement_PEMWE` | electrolyser: fit on the wind profile, ageing trajectories, end of life; writes `pemwe_parametres.json` |
| `AB_vieillissement_PEMFC` | fuel cell: ageing laws, end of life, hydrogen per trip with age, crossover laws |
| `AB_vieillissement_trois_cas` | **reference results**: three cases, end of life, each converter, chain, 16 categories, sensitivity (electricity, constants, hours); checks them against the reference values |
| `AB_vieillissement_fabrication` | fabrication inventories and chain over the vehicle life |
| `AB_vieillissement_couplage` | coupling of the three components over time |
| `AB_vieillissement_normalisation` | EF 3.1 normalisation, weighting, single score by item, Monte Carlo |
| `AB_vieillissement_ACV_sensibilite` | additional sensitivity analyses |
| `AB_vieillissement_comparaison_modeles` | linear versus mechanistic models, validation against Toyota tests |

`medium.xlsx`, `nuc.xlsx`, `wind.xlsx` and `pv.xlsx` are the impacts of 1 kWh exported from Activity Browser (characterised results only).

Note on names: in `AB_vieillissement_PEMWE`, the scenarios called *Optimiste*, *Moyen* and *Pessimiste* are three variants of the anode-activity loss in the mechanistic electrolyser model (final activity 0.49, 0.30 and 0.112), explored during the research. Only the last one is used in the results, as the pessimistic case. The three cases of the results (optimistic, central, pessimistic) are defined in `config/default.yaml` and computed in `AB_vieillissement_trois_cas`.
