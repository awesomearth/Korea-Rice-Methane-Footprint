# Rice-shed Methane Footprint of Korean Cities

A spatial footprint study that applies the "carbon hoofprint" method of Goldstein et al. (2025, *Nature Climate Change* 15, 1190–1197, [doi:10.1038/s41558-025-02450-7](https://doi.org/10.1038/s41558-025-02450-7)) to South Korea. The study traces the paddy-rice methane (CH4) embodied in each si/gun/gu's household rice consumption back to the places where the rice is grown. Presentation built with Claude Code. 

## Headline results (2025)

- National paddy CH4: **6,371 kt CO2e**, an average of 1.80 kg CO2e per kg of milled rice. Intensity ranges from 1.57 to 2.11 across producing units.
- Household rice-shed footprint of the 252 consuming units: **4,903 kt CO2e**. The demand-weighted mean sourcing distance is 55.6 km.
- Per capita footprint: **96.9 ± 5.7 kg CO2e/person/yr** (range 84.6–113.9). Units supplied by low-yield southwestern producers sit above the national average; most of Seoul sits below it.
- Scenarios: intermittent drainage −8.2%, halving household waste −10.9%, both −18.2%.
- Monte Carlo (1,000 draws): combined MAPE 46%, dominated by IPCC factor ranges; sourcing-only MAPE 2.6%.

The full write-up, with methods, limitations and a source for every number, is in [`output/05-rice-shed/09-report.md`](output/05-rice-shed/09-report.md).

## Repository layout

```
output/
├── 01-method-summary.md      Summary of the source paper's method
├── 02-ideas.md               Ten candidate Korean applications
├── 03-data-verification.md   Data availability check for each idea
├── 04-ranking.md             Scoring; Idea 2 (rice-shed) selected
└── 05-rice-shed/
    ├── 00-scope.md … 09-report.md   One document per phase
    ├── code/                 Pipeline scripts (phase1 … phase10) and requirements.txt
    ├── data/raw/             Downloaded inputs and factor-table transcriptions
    ├── data/processed/       Pipeline outputs (CSV, JSON, NPZ)
    ├── figures/              Four maps (PNG)
    └── presentation/         Interactive web presentation (index.html)
```

## Reproducing the analysis

Requires Python 3.12 and internet access. Run from `output/05-rice-shed/`:

```bash
python3 -m venv .venv && .venv/bin/pip install -r code/requirements.txt
.venv/bin/python -I code/phase1_acquire.py
.venv/bin/python -I code/phase2_demand.py
.venv/bin/python -I code/phase3_supply_intensity.py
.venv/bin/python -I code/phase4_flows.py
.venv/bin/python -I code/phase5_footprint.py
.venv/bin/python -I code/phase6_uncertainty.py   # ~6 min, seed 20251231
.venv/bin/python -I code/phase7_scenarios.py
.venv/bin/python -I code/phase8_figures.py
.venv/bin/python -I code/phase9_report.py
.venv/bin/python -I code/phase10_webdata.py      # presentation/data/bundle.json
```

**Run `phase1_acquire.py` first.** Three things are left out of this repository, and phase 1 restores them:
- the IPCC, GIR NID and FAO PDFs, which it downloads from their publishers;
- the extracted geoBoundaries shapefiles, which it unpacks from the zips in `data/raw/boundary/`.

Phases 3 and 7 check the transcribed factor tables against pages of those PDFs. More detail is in [`output/05-rice-shed/code/README.md`](output/05-rice-shed/code/README.md).

To view the presentation locally:

```bash
python3 -m http.server 8000 --directory output/05-rice-shed/presentation
```

Then open http://localhost:8000.

## Data sources

| Input | Source |
|---|---|
| Rice production and paddy area by si/gun (DT_1ET0034, DT_1ET0033) | KOSIS, Statistics Korea |
| Per capita grain consumption (DT_1ED0001) | KOSIS, Statistics Korea |
| Resident population by 법정동, 2025-12-31 | Ministry of the Interior and Safety, via data.go.kr |
| Paddy CH4 method and default factors | 2006 IPCC Guidelines, Vol. 4 Ch. 5 |
| Korean Tier 2 factors and management mix | GIR, National Inventory Report 2025 |
| Si/gun/gu boundaries | geoBoundaries gbOpen KOR ADM2 (CC BY 3.0) and ADM1 (Public Domain) |
| 영광군 boundary patch | © OpenStreetMap contributors (ODbL) |
| Korean–English unit names | SGIS, via data.go.kr |
| Household waste share (scenario S2) | FAO (2011), *Global food losses and food waste* |

The source paper's PDF is not included. Read it at the DOI above.

## License

Copyright © 2026 awesomearth. **All rights reserved.** See [LICENSE](LICENSE). Third-party data in `data/raw/` and the derived boundary layer keep their original licenses, as listed in LICENSE.
