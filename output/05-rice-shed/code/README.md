# Idea 2 rice-shed — reproduction

Run from `output/05-rice-shed/`, in order:

```bash
python3 -m venv .venv && .venv/bin/pip install -r code/requirements.txt
.venv/bin/python -I code/phase1_acquire.py          # raw inputs -> 01-data-inventory.md (add --force to re-download)
.venv/bin/python -I code/phase2_demand.py           # demand.csv, 02-demand.md
.venv/bin/python -I code/phase3_supply_intensity.py # supply_intensity.csv, ch4_factors.json, 03-supply-intensity.md
.venv/bin/python -I code/phase4_flows.py            # crosswalk.csv, impedance.npz, flows.csv, 04-flows.md
.venv/bin/python -I code/phase5_footprint.py        # footprint.csv, 05-footprint.md
.venv/bin/python -I code/phase6_uncertainty.py      # mc_results.csv, 06-uncertainty.md (~6 min, seed 20251231)
.venv/bin/python -I code/phase7_scenarios.py        # scenarios.csv, 07-scenarios.md
.venv/bin/python -I code/phase8_figures.py          # figures/*.png, 08-figures.md
.venv/bin/python -I code/phase9_report.py           # 09-report.md
```

- `kosis_dl.py` and `datagokr_dl.py` are keyless downloaders. `geo_units.py` attaches geometry: geoBoundaries ADM2, the approved substitute for the login-gated S-BND, plus an OSM patch for 영광군.
- `data/raw/gir/nid2025_rice_*.csv`, `data/raw/ipcc/ipcc2006_v4c5_rice_factors.csv` and `data/raw/fao/fao2011_cereal_waste.csv` are transcriptions of factor tables. Phases 3 and 7 check each value against its cited PDF page.
- Phase 0 (`00-scope.md`) is a design document and has no script.
