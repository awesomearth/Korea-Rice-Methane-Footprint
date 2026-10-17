# 00 — Content Plan (presentation, Phase 0)

**Inputs read:** `09-report.md`, `00-scope.md`, `05-footprint.md`, `06-uncertainty.md`, `07-scenarios.md`, `08-figures.md`, `../01-method-summary.md`, headers of `data/processed/*.csv`, `data/processed/ch4_factors.json`, `data/processed/figure_classes.json`.

All slide numbers are read at build time from `presentation/data/bundle.json`, which `code/phase10_webdata.py` assembles from the files below. Values shown here are the ones the bundle must reproduce.

| # | Section | Headline (≤ 12 words) | Visual type | Data file + columns | Source note |
|---|---------|----------------------|-------------|---------------------|-------------|
| 1 | Title | Whose rice, whose methane? Korean cities' paddy CH4 footprint | Metric row (4 tiles) | `ch4_factors.json` (national_kt_co2e); `footprint.csv` (footprint_tco2e, per_capita_kgco2e); `flows.csv` (tonnes, km) | 6,371.2 kt CO2e national paddy CH4 [ch4_factors.json]; 4,902.9 kt household [footprint.csv]; 96.9 kg/person mean [footprint.csv]; 55.6 km mean sourcing [flows.csv] |
| 2 | The question | A US meat method, transferred to Korean rice | Two-column analogy diagram | `../01-method-summary.md` §1, §5 | Goldstein et al. 2025: 3,531 cities, 329 MtCO2e, r = 0.99 with intensity [01-method-summary.md §1] |
| 3 | Method | Six procedures turn population and paddies into footprints | Clickable pipeline (P2→P3→P1→P4→P5→P6) | `09-report.md` §3; `ch4_factors.json` (ef_nat, t_eff_days, gwp) | 252 consumers, 156 producers [demand.csv, supply_intensity.csv]; EF_nat 2.4493; t_eff 137.1 d; GWP 28 [ch4_factors.json] |
| 4 | Where methane is emitted | Low-yield southwestern paddies emit most per kilogram | Choropleth (orange, Jenks k=5) + strip of 156 producers | `supply_intensity.csv` (kgco2e_per_kg, production_t, yield); `figure_classes.json` fig2 | 1.570–2.113 kg CO2e/kg, max/min 1.35 [supply_intensity.csv] |
| 5 | Whose consumption | Per capita footprints span 84.6 to 113.9 kg | Choropleth (blue, Jenks k=5) + searchable ranked table | `footprint.csv` (per_capita_kgco2e, population, n_sources, mean_sourcing_km); `figure_classes.json` fig1 | mean ± sd 96.9 ± 5.7 [footprint.csv] |
| 6 | Rice-sheds | Most units draw on a single nearby source | Flow map with unit picker (default 5 largest) | `flows.csv` (from_code, to_code, tonnes, km); `crosswalk.csv` (centroid_lon/lat) | median 1 source, max 9 [footprint.csv n_sources] |
| 7 | Spatial vs national | National averages misstate local footprints by up to 17% | Diverging choropleth + region contrast bars | `footprint.csv` (ratio_spatial_to_natavg) ; `figure_classes.json` fig4 | 0.872–1.174 [footprint.csv]; Seoul 24 of 25 below 1 [footprint.csv] |
| 8 | Scenarios | Drainage plus less waste cuts household footprint 18% | Toggle (S1, S2) + total bar + per-unit distribution | `scenarios.csv` (baseline/S1/S2/S1S2 tco2e, pct) | 4,502.6 / 4,367.6 / 4,011.0 kt; −8.17 / −10.92 / −18.19% [scenarios.csv] |
| 9 | Uncertainty | Emission factors set the level, sourcing sets the ranking | Paired MAPE bars + p5–p95 interval chart | `mc_results.csv` (mape, sourcing_only_mape, p5, p95); `mc_draws_per_capita.npz` (k) | 46.2% combined, 2.6% sourcing-only; k p5–p95 0.370–2.333 [mc_results.csv, npz] |
| 10 | Limitations | Five caveats bound what these maps can claim | Card grid | `09-report.md` §7 | text only, no new numbers |
| 11 | Sources | Open data, reproducible in nine scripts | Table + attribution list | `09-report.md` §2 table | parsed from report |

## Not available
- Observed inter-regional rice trade (to validate LP flows): not in any artifact. Shown as a caveat, not a number.
- Regional per capita consumption: not in any artifact (single national rate 53.9 kg).
- Water regime by si/gun: not in any artifact; S1 is uniform.
