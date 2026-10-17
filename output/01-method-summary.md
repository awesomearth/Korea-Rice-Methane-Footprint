# 01 — Method Summary

**Paper:** Goldstein, B. P., Pelton, R. E. O., Gounaridis, D., Schmitt, J., Springer, N. & Newell, J. P. "The carbon hoofprint of cities is shaped by geography and production in the livestock supply chain." *Nature Climate Change* 15, 1190–1197 (Nov 2025). doi:10.1038/s41558-025-02450-7.

**Source used:** the local PDF `s41558-025-02450-7.pdf` (18 pages). Text was extracted from pp. 1–15 (main text pp. 1190–1197, Methods, Extended Data Figs. 1–3). Pages 16–18 have no extractable text and were not used. The Supplementary Information (Supplementary Notes 1–6, Supplementary Tables 1–8, Supplementary Figs. 1–9) is **not in the PDF**. Where the paper sends the reader there, this summary says so and does not guess what it contains.

Citation shorthand: "p. 1190" = journal page. "Methods: *subsection*" = Methods subsection heading (PDF pp. 9–11). "Fig. N" / "ED Fig. N" = main / Extended Data figure.

---

## 1. Research question and headline findings

**Research question.** What GHG emissions are embodied in the beef, chicken and pork consumed in each US city (the "carbon hoofprint")? Where in the rural supply chain (feed, livestock, processing) do those emissions occur? How much do differences in production geography, rather than in diet, explain differences between cities? (Abstract, p. 1190; p. 1191 col. 1.)

**Headline findings**
- Scope: 3,531 census-defined urban areas, linked to 3,143 feed-, livestock- and poultry-producing counties. Covers 93% of the US population (p. 1191).
- Residents of US cities consume 11.1 Mt of meat a year: 4.6 Mt chicken, 3.7 Mt beef and 2.7 Mt pork (Results, p. 1191; ED Fig. 1a).
- The total hoofprint is **329 MtCO2e**. That is more than the territorial CO2 of the UK (305 Mt) or Italy (313 Mt), and on par with US at-home fossil-fuel combustion (334 Mt) (Abstract; p. 1191).
- The per capita hoofprint is 1,093 ± 237 kgCO2e. It ranges from 500 (Houghton, MI) to 1,731 kgCO2e (Richmond, MO), while per capita consumption is nearly uniform at 78.6 ± 1.87 kg (p. 1192; Fig. 1a).
- Consumption is a poor proxy for the hoofprint (r = −0.04). The carbon intensity of the meat a city sources is what drives its hoofprint (r = 0.99). Using national-average intensities would therefore over- or under-estimate city footprints (p. 1192; Fig. 2a).
- Beef accounts for 73 ± 7% of the hoofprint, with a range of 41–87% across cities (p. 1192; Fig. 2b). Intensity varies across cities by a factor of 4.3 for beef, 4.9 for chicken and 15 for pork (p. 1194; Fig. 4a).
- Meatsheds are large. Los Angeles beef passes through 10 processing counties, which draw on 469 livestock counties, which draw on 828 feed counties (p. 1192; Fig. 3). Mean beef distances for the 20 largest cities are 920 ± 630 km from processing to city, 420 ± 150 km from feedlot to processing, and 430 ± 230 km from feed to animal (p. 1193).
- The hoofprint equals 43% of city GHGs from at-home fuel and electricity. The ratio exceeds 50% for 60 million people (p. 1194; Fig. 5a).
- Demand-side scenarios cut the hoofprint by 14–51%. Production-side silvopasture cuts it by about 6% (pp. 1195–1196; Fig. 5b; ED Figs. 2–3).
- Uncertainty: the meatshed Monte Carlo gives a mean absolute percentage error (MAPE) of 26% across cities (Fig. 1 caption; Methods: *Limitations and uncertainty analysis*).

## 2. Data inputs (type, resolution, source category)

| Input | Type | Spatial / temporal resolution | Source category | Citation in paper |
|---|---|---|---|---|
| NHANES dietary recall (5 iterations, n = 51,623) | Individual survey microdata, survey weights | National sample, demographic strata | Federal health survey (CDC) | Methods: *Meat consumption estimates*; ref. 50 |
| FICRCD (food code → retail commodity, g per 100 g) | Conversion table, ~10,000 food codes | Non-spatial | Federal agriculture (USDA) | Methods: *Meat consumption estimates*; ref. 51 |
| Census / ACS demographics (population by race, household income vs poverty line) | Demographic counts | Census tract (73,057 tracts), 2017 | Federal statistics (Census Bureau) | Methods: *Meat consumption estimates*; ref. 55 |
| USDA Census of Agriculture 2017 and other FoodS3 inputs (crop output, livestock, processors) | Production statistics | County | Federal agriculture (USDA) | Methods: *Meat consumption estimates*; *Data availability* |
| Livestock slaughter, animal mass, dressing weights (≈61% beef, ≈75% pork/chicken) | Production statistics | State-specific factors, national totals | USDA Livestock Slaughter Summary | Methods: *County supply of meat*; ref. 58 |
| National domestic carcass-weight supply (≈12 Mt beef, 9.5 Mt pork, 15.5 Mt chicken), imports, stocks | National balance sheet | National, annual | USDA ERS | Methods: *County domestic meat demand*; ref. 59 |
| Loss factors (processing, retail, consumer) | Coefficients (0.63/0.59/0.61 kg purchased per kg carcass) | National | USDA ERS / Buzby et al. | Methods: *Total loss-adjusted meat consumption*; ref. 60; Suppl. Table 8 (not in PDF) |
| Spatially explicit LCA inventories (fertilizer N, N2O, tillage, irrigation, land-use change, manure systems, enteric, grid) | Emission factors and practice data | County / facility | USDA, EPA, USGS, national labs, LCA databases | Methods: *Spatial carbon hoofprint*; refs 31, 56, 57, 61 |
| Import origins and intensities | Trade shares, country intensities | Country | USDA GATS, FAOSTAT | Methods: *Spatial carbon hoofprint*; refs 62–63 |
| Transport impedance (rail, road, waterway) | Network cost proxy | County to county | FoodS3 internal | Methods: *Limitations and uncertainty analysis* |
| Urban areas and county population shares | Boundaries | Census urban areas (TIGER 2017) | Census Bureau | Methods: *Spatial carbon hoofprint*; *Data availability* |
| CoolClimate household energy CO2 | Modelled per-household emissions | ZIP code, 2013 | Academic (UC Berkeley) | Methods: *Residential energy use*; ref. 64 |
| FAF5 freight flows (validation only) | Commodity-group freight | FAF zones | Oak Ridge National Laboratory | Methods: *Limitations and uncertainty analysis* |

## 3. Modelling steps in order

**Step A — Consumption (demand)** (Methods: *Meat consumption estimates*)
1. Link NHANES food codes to FICRCD and disaggregate meals into grams of beef, chicken and pork per capita per day, using the survey package in R.
2. Build 8 consumption profiles per meat: 4 race/ethnicity groups × 2 income classes, split at 200% of the federal poverty line.
3. Apply the profiles to tract-level population by race and income class, then sum tracts to counties (73,057 tracts).
4. Correct for NHANES under-reporting and embedded losses. Keep only each county's *share* of national consumption, then scale those shares to the national domestic chilled-carcass weight (Methods: *County domestic meat demand*).

**Step B — Supply** (Methods: *County supply of meat*)
5. Estimate county meat supply as animals processed × state-specific slaughter mass × dressing weight. Scale it to the national carcass total and add imports plus net stock change (imports ≈10% of beef, 4% of pork, 0.3% of chicken).

**Step C — Supply chain / flow reconstruction** (Methods: *Enhancing the FoodS3 model*)
6. FoodS3 is mass-balanced. It distributes total crop supply (corn, wheat, soy, alfalfa, silage) to downstream demand nodes (livestock, dairy, ethanol, crushers, millers). It then distributes by-products to livestock and moves animals to primary processors.
7. The new link is a **linear optimization** that minimizes total impedance from processing counties to consuming counties for each meat type. Supply and demand are balanced nationally. The output is a meatshed per consuming county.

**Step D — Intensity** (Methods: *Spatial carbon hoofprint*)
8. A spatially explicit LCA gives a unique cradle-to-processing-gate intensity (kgCO2e per kg boneless meat) for each processing facility. It covers feed, livestock and processing practices, uses IPCC AR5 GWPs with climate-carbon feedbacks, and allocates emissions economically: 71% of burdens to beef, 65% to pork, 91% to chicken. Import intensities are added. Transport from processing to the consumer is excluded to avoid double counting with city inventories.
9. Loss-adjust the purchased versus consumed quantities. 1 kg carcass yields 0.63/0.59/0.61 kg purchased and 0.50/0.42/0.52 kg eaten for beef/pork/chicken (Methods: *Total loss-adjusted meat consumption*).

**Step E — Allocation to cities** (Methods: *Spatial carbon hoofprint*)
10. County emissions = Σ over processors (flow × intensity of that processor).
11. Allocate county emissions to urban areas by the fraction of county population that lives in each urban area. Sum over counties for each city, then divide by meat purchased to get the city's intensity. Per capita and total hoofprints are mapped with Jenks classes (Figs. 1, 4; ED Fig. 1).

**Step F — Hotspots and reference comparison**
12. Map intercity variation, the shares of beef, chicken and pork, stage contributions, and meatshed linkages (Figs. 1–4).
13. Compare per capita hoofprint with per capita household-energy CO2. CoolClimate ZIP-code values × households are summed to urban areas, and the ratio is mapped (Methods: *Residential energy use*; Fig. 5a).

## 4. Scenario and uncertainty procedures

**Demand-side scenarios** (Methods: *Scenarios*; Fig. 5b; ED Fig. 2)
- S1: halve retail and consumer edible waste. Edible losses fall to 15.1% beef, 13.8% chicken, 18.9% pork, cutting the intensity per kg delivered by 18.5% / 23.4% / 16.0%. Result: −16%.
- S2: replace 50% of beef mass with pork and chicken equally. Beef goes from 26.9 to 13.4 kg, pork from 19.5 to 25.9 kg, chicken from 32.2 to 38.2 kg. Result: −28 to −33% across the beef-swap scenarios (p. 1195).
- S3: replace 50% of beef with chicken. Result: −33% (Fig. 5b).
- S4: "meatless Monday", with consumption × 6/7. Result: −14%.
- Combined scenarios: −37 to −43% without S4 and −51% with it, i.e. 329 → 160 MtCO2e (p. 1195; Fig. 5b). ED Fig. 2b shows that the reduction varies by city.

**Supply-side scenario**
- Beef silvopasture: −6% nationally, more in some cities. ED Fig. 3b maps the ratio of the supply-side reduction to the demand-side reduction (p. 1195 *Future work*; ED Fig. 3; method in ref. 31).

**Uncertainty** (Methods: *Limitations and uncertainty analysis*)
- **Sourcing (meatshed) Monte Carlo:** 1,000,000 mass-balanced alternative sourcing scenarios per city. MAPE is 26.5% across cities and falls below 20% for cities over 125,000 people (Suppl. Note 4 and Suppl. Fig. 1, not in PDF).
- **Consumption Monte Carlo:** 100 draws per city, varying each demographic group's consumption within NHANES ranges. MAPE is 0.02–5% per city and under 1% overall (Suppl. Note 5 and Suppl. Fig. 7, not in PDF). Standard errors of the consumption estimates are 1–10% (Methods: *Meat consumption estimates*).
- **LCA inventory uncertainty:** acknowledged but not quantified (Methods p. 10–11; Suppl. Note 6).
- **Validation:** consistency with FAF5 and with stakeholder or proprietary sourcing data, checked qualitatively (Methods p. 10).
- **Stated limitations:** sourcing assumes pure cost minimization and ignores contracts and brands. Consumption profiles are national averages per demographic group and miss regional cuisines (Methods pp. 9–10). The scenarios ignore export rebound (p. 1195 *Future work*).

## 5. Transferable components

| Component | US-specific dependency | Portability to South Korea | Paper basis |
|---|---|---|---|
| Survey-based per capita consumption profiles by demographic group | NHANES + FICRCD; race/ethnicity × income strata | **Portable in structure.** Needs a national dietary or expenditure survey with microdata. Korea's strata would be age/sex/income/region, since race is not a meaningful Korean stratum. A food-code → commodity crosswalk must be rebuilt. | Methods: *Meat consumption estimates* |
| Apply profiles to small-area demographics, aggregate to admin units | Census tracts + ACS income-by-race | **Portable.** Any population-by-age/sex table at si/gun/gu or eup/myeon/dong works. | Methods: *Meat consumption estimates* |
| Scale bottom-up demand to a national balance sheet (fixes under-reporting) | USDA ERS supply-and-disposition data | **Portable.** Any national supply balance (e.g. a food balance sheet) can be the control total. | Methods: *County domestic meat demand* |
| Mass-balanced supply estimate per producing unit | USDA slaughter and agriculture census | **Portable** where unit-level production or processing statistics exist. | Methods: *County supply of meat* |
| Transport LP minimizing impedance between supply and demand nodes | FoodS3 rail/road/waterway impedance | **Highly portable.** A balanced transportation problem can be solved with free solvers (scipy/PuLP), using straight-line or road distance as the impedance. | Methods: *Enhancing FoodS3*; *Limitations* |
| Facility- or location-specific intensity (not national average) | FoodS3 spatial LCA built on USDA/EPA/USGS practice data | **Partly portable.** The full LCA is US-built, but the *principle* transfers. Simpler per-location intensities (e.g. per-plant emission factors, yield-scaled factors) can be built from open data. | Methods: *Spatial carbon hoofprint* |
| Population-share allocation from admin units to cities | Census urban areas straddling counties | **Portable.** In Korea, si/gun/gu are themselves the city units. Allocation to eup/myeon/dong or urban clusters uses population shares the same way. | Methods: *Spatial carbon hoofprint* |
| Loss and waste coefficients | USDA ERS loss-adjusted data | **Portable** if national loss factors exist, otherwise FAO defaults. | Methods: *Total loss-adjusted meat consumption* |
| Scenario arithmetic (waste halving, substitution, ×6/7) | None | **Fully portable.** Pure recomputation on the baseline. | Methods: *Scenarios* |
| Monte Carlo over sourcing and consumption | None (method) | **Fully portable.** Can be scaled down to about 1,000 draws for speed. | Methods: *Limitations and uncertainty analysis* |
| Reference-quantity comparison | CoolClimate ZIP-level household energy | **Portable** if a sub-national household energy or emissions dataset exists. | Methods: *Residential energy use* |
| Jenks hotspot maps, quadrant (consumption vs footprint) analysis | None | **Fully portable** | Figs. 1, 2a, 4, 5a |

**Bottom line:** two components are the hard-to-port core: the US-specific spatial LCA inventories (FoodS3) and the NHANES-to-FICRCD food crosswalk. Everything else is generic: demographic allocation, the mass balance, the transport LP, scenario arithmetic, Monte Carlo, hotspot mapping and the reference ratio. That generic part can be rebuilt with open data and scripts.
