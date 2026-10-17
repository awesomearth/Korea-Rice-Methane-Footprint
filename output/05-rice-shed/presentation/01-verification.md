# 01 — Verification (presentation, Phase 3)

Checked on the local preview of `presentation/index.html` (Python static server, 2026-10-17). The page reads every number from `data/bundle.json`, which `code/phase10_webdata.py` builds. Its built-in check prints the totals below and asserts the two national totals.

## Number trace

| Shown value | Slide | bundle.json key | Built from (file → column/section) | Report value |
|---|---|---|---|---|
| 6,371.2 kt CO₂e | 1, 2 | `national.paddy_kt` | `ch4_factors.json` → national_kt_co2e | 6,371.2 (§4) |
| 4,902.9 kt CO₂e | 1, 3, 8 | `national.household_kt`, `scen.baseline_tco2e` | `footprint.csv` → Σ footprint_tco2e | 4,902.9 (§4) |
| 96.9 kg CO₂e/person (mean), ± 5.7 | 1, 5 | `pc_mean`, `pc_sd` | `footprint.csv` → per_capita_kgco2e | 96.9 ± 5.7 (§4) |
| 95.9 population-weighted | 5 | `pc_popw` | `footprint.csv` → Σ footprint / Σ population | 95.9 (`05-footprint.md`) |
| 55.6 km, 153.3 M t·km | 1, 3 | `mean_km`, `tkm_m` | `flows.csv` household rows → Σ t·km / Σ t | 55.6 km, 153.3 M (§4) |
| 156 producers, 252 consumers, 51,117,378 residents | 1, 2, 3 | `n_prod`, `n_cons`, `pop` | `supply_intensity.csv`, `footprint.csv` | same (§3) |
| 2,755,227 t household demand | 3 | Σ `units[].demand_t` | `footprint.csv` → rice_demand_t | 2,755,227 (§3) |
| EF_nat 2.4493, t_eff 137.1 d, GWP 28 | 3, 10 | `ef_nat`, `t_eff_days`, `gwp` | `ch4_factors.json` | same (§3) |
| 22.2% to non-household, 1,468.2 kt | 3 | `slack_share`, `slack_kt` | `flows.csv` SLACK rows × `supply_intensity.csv` | 22.2%, 1,468.2 (§3, §4) |
| 1.570–2.113 kg/kg; national 1.800; "up to 35%" | 4 | `int_min`, `int_max`, `intensity` | `supply_intensity.csv` → kgco2e_per_kg; 35% = max/min − 1 (1.35) | 1.570–2.113, max/min 1.35 (§4) |
| 3,539,195 t produced | 4 | `production_t` | `ch4_factors.json` → national_production_t | 3,539,195 (`00-scope.md`) |
| 84.6–113.9 kg CO₂e/person | 5 | `pc_min`, `pc_max` | `footprint.csv` | 84.6–113.9 (§4) |
| Median 1 source, max 9 | 6, 10 | `nsrc_median`, `nsrc_max` | `footprint.csv` → n_sources | 1, 9 (§4) |
| Namyangju 9 sources, 86.0 km; Songpa 4 sources, 86.1 km | 6 | `units[].nsrc`, `units[].km` | `footprint.csv` | same (`08-figures.md` fig3) |
| Ratio 0.872–1.174; "up to 17%" | 7 | `ratio_min`, `ratio_max` | `footprint.csv` → ratio_spatial_to_natavg; 17% = 1.174 − 1 | 0.872–1.174 (§4) |
| Seoul 24 of 25 below 1; Jeollanam-do median 1.086 | 7 | `regions[]` | `footprint.csv` grouped by province | same (§4) |
| Seoul + Gyeonggi origin: Chungnam 33%, Gyeonggi 30%, Gyeongbuk 13%, Jeonbuk 11%; intensity 1.738 | 7 | `origin.capital`, `capital_int` | `flows.csv` household rows to sido 11/41 | same (§4) |
| 4,502.6 / 4,367.6 / 4,011.0 kt; −8.17 / −10.92 / −18.19% | 3, 8 | `scen.*` | `scenarios.csv` → Σ S1/S2/S1S2_tco2e | same (§6) |
| Unit ranges: all −8.17%; −19.08% to +0.89%; −25.69% to −7.35% | 8 | `units[].s1/s2/s12` | `scenarios.csv` → *_pct | same (§6) |
| 11.0% continuously flooded area; waste 20% → 10% | 8 | text constant | `07-scenarios.md` table | same (§6) |
| MAPE 46.2% / 46.4% / 45.9%; sourcing 2.6% / 3.8% / 1.1%; n = 144 / 108 | 2, 3, 9 | `mape*`, `src_mape*`, `n_big`, `n_small` | `mc_results.csv` → mape, sourcing_only_mape | same (§5) |
| k p5–p95 0.37–2.33 | 9 | `k_p5`, `k_p95` | `mc_draws_per_capita.npz` → k | 0.370–2.333 (§5) |
| Paper: 3,531 areas, 3,143 counties, 329 Mt, r = 0.99 / −0.04, 26.5% MAPE | 2, 9 | text constants | `01-method-summary.md` §1, §4 | — |
| Map classes: fig1 30/63/54/58/24; fig4 3/74/78/59/15; 229 polygons | 5, 7 | `breaks.*`, `poly_cons` | `figure_classes.json` | counts match on the rendered maps |

The intensity map colours polygons, so its rendered polygon counts (27/48/100/38/11, plus 5 with no rice) differ from fig2's counts per producing unit (27/39/49/34/7). Metropolitan producers colour all of their districts. The legend shows fig2's counts and says "n = producing units".

**Not shown, because no artifact holds them:** observed inter-regional rice trade, regional per capita consumption, water regime by si/gun (`00-content-plan.md`, Not available).

## Text budget

Body prose counted: ledes, caveats, card text, the visible method-step text and the switch labels. Captions and the sources table are excluded.

| Section | Prose words | Bullets (max words) | Result |
|---|---|---|---|
| top | 20 | 0 | pass |
| question | 46 | 0 | pass |
| method | 32 | 0 | pass |
| intensity | 23 | 3 (7) | pass |
| footprint | 20 | 2 (7) | pass |
| ricesheds | 32 | 4 (6) | pass |
| ratio | 20 | 3 (6) | pass |
| scenarios | 53 | 0 | pass |
| uncertainty | 15 | 2 (8) | pass |
| limits | 55 | 0 | pass |
| sources | 0 | 0 | pass |

## Rendering checks

- **Console:** no errors on load or during interaction.
- **Desktop, 1440×900, dark and light:** all 11 sections render, and every map draws 229 polygons.
- **Interactions tested:**
  - footprint search (finds "Songpa"), and column sort (sorting by population puts Hwaseong-si first);
  - rice-shed dropdown and chips (Songpa-gu: 4 sources, 4 lines; the map zooms to the rice-shed);
  - scenario switches (all four states match `scenarios.csv`);
  - uncertainty toggle (y-axis rescales from about 80–120 to 0–270);
  - method steps (click and arrow keys);
  - keyboard section navigation.
- **Phone, 375×812:** the page does not scroll sideways (scrollWidth = clientWidth = 375). The section label in the top bar is hidden below 480 px.
- **Resting states:** the first render draws everything without waiting for an animation (hero flows, rice-shed zoom, scenario and uncertainty charts), so thumbnails and background tabs show finished visuals.
