# 04 — Scoring and Ranking

Inputs: `02-ideas.md` (10 ideas) and `03-data-verification.md`.

**Rubrics.** The two rubrics are used exactly as given. Total = Data score + Speed score. Ties are broken by Data score, then by Speed score. No other criteria were added.

**How the data score was applied.** Each score is read off the Phase 3 statuses:
- 5: every input "verified" with nothing to clean.
- 4: every input "verified", but at least one needs free registration, an API key or a login, or minor cleaning (PDF, ZIP, geocoding).
- 3: one input "unverified", or coarser than needed.
- 2: a key input "unverified".
- 1: a key input "unavailable".

**Speed scores** follow the steps each idea's pipeline requires.

**Ties that remain.** Several ideas tie on all three keys: total, data score and speed score. They share a rank (shown as "1=", "4=" and so on) and are listed in idea-number order. The rules supply no further tie-breaker, and none was invented.

## Ranked table

| Rank | Idea | Data score | Speed score | Total | One-line justification |
|---|---|---|---|---|---|
| 1= | 2. Rice-shed methane footprint | 4 | 3 | 7 | All inputs verified: KOSIS si/gun rice tables, national per capita consumption, MOIS population, IPCC Vol. 4 factors. Only a possible VWorld login is needed. One lightweight LP plus Monte Carlo. |
| 1= | 3. Electricity-shed GHG footprint | 4 | 3 | 7 | All inputs verified, but the KEPCO si/gun/gu Excel needs a free login and EPSIS units lack coordinates (they must be geocoded by name). LP plus Monte Carlo. |
| 1= | 5. Municipal solid waste "waste-shed" | 4 | 3 | 7 | The 2024 national waste release (229 si/gun/gu, with facility throughput tables) and IPCC Vol. 5 are verified. The result-table ZIP has not been opened, so some cleaning is expected. LP plus Monte Carlo. |
| 4= | 4. Air-pollutant footprint of electricity | 3 | 3 | 6 | CleanSYS facility Excel/CSV, EPSIS and KEPCO are verified, but the CAPSS export at si/gun/gu level is unverified. LP plus Monte Carlo, plus matching facilities to plant units. |
| 4= | 10. Cattle-manure nitrogen-shed | 3 | 3 | 6 | Cattle numbers by si/gun/gu, cropland area by si/gun and IPCC Vol. 4 Ch. 10 are verified. Crop N requirement rates are unverified. LP plus Monte Carlo. |
| 6= | 6. Food-waste treatment footprint | 2 | 3 | 5 | Food-waste rows by si/gun/gu are verified, but the key national food-waste facility list (type, capacity) is unverified; only provincial or city files exist. LP plus Monte Carlo. |
| 6= | 8. Commuting carbon from census OD | 2 | 3 | 5 | The 2020 si/gun/gu OD and mode tables are verified, but the key mode-specific gCO2/pkm factors are unverified. Tabulation, distances and Monte Carlo. |
| 8= | 1. Carbon hoofprint of Korean si/gun/gu | 2 | 2 | 4 | Key intensity inputs are unverified: the GIR regional ZIP breakdown, slaughter data below sido, and pig/poultry numbers. Building the KNHANES food-code crosswalk, the PDF balance sheet, LP and Monte Carlo means several heavy cleaning steps. |
| 8= | 7. Embodied cement carbon of construction | 2 | 2 | 4 | Cement plant production and location, a key input, are unverified (cement.or.kr unreachable), and so is the per-m² coefficient. The permit file has 6,151,376 rows. |
| 10 | 9. Energy footprint of tap-water supply | 1 | 1 | 2 | National waterworks statistics and plant kWh/m³ are unavailable (only city files were found), so city files would have to be compiled by hand. |

## Full ranked list

### Rank 1= — Idea 2: Rice-shed Methane Footprint of Korean Cities (Total 7; Data 4, Speed 3)
- **Procedures:** P1, P2, P3, P4, P5, P6.
- **Data evidence (Phase 3 rows for Idea 2):**
  - KOSIS DT_1ET0034 and DT_1ET0033 are verified. Rows at si/gun level, such as 수원시, are visible, covering 1965–2025.
  - "1인당 연간 양곡소비량" is verified (national level).
  - S-POP is verified: CSV downloads without login.
  - Paddy CH4 factors are verified through IPCC 2006 Vol. 4 (S-IPCC4). The rice table in the GIR NID PDF is unverified, but the IPCC default replaces it.
  - S-BND SHP is verified; VWorld may need a login.
- **Why 4, not 5:** a possible free VWorld login, and KOSIS tables need light reshaping.
- **Speed evidence:** the data are small: rice-producing si/gun rows, and 250 consuming units (the row count of the S-BND boundary file). One balanced transport LP and a lightweight Monte Carlo over sourcing and factors. Score 3 under "optimization or Monte Carlo needed, still lightweight".

### Rank 1= — Idea 3: Consumption-Based Electricity GHG Footprint ("Electricity-shed") (Total 7; Data 4, Speed 3)
- **Procedures:** P1, P2, P3, P4, P5, P6, P7.
- **Data evidence:**
  - S-KEPCO is verified: si/gun/gu option, Excel download, login required.
  - S-EPSIS is verified: EXCEL/CSV generation by unit, 2002–2025. Units are located only by sido and plant name.
  - S-GHGDISC is verified (Excel).
  - S-EF is verified: 0.4173 tCO2eq/MWh for 2023.
  - S-BND is verified.
- **Why 4:** a free KEPCO login is required, and geocoding plants by name is minor cleaning.
- **Speed evidence:** an LP between about 250 demand nodes and the EPSIS generating units, plus a Monte Carlo over the sourcing matrix. Score 3.

### Rank 1= — Idea 5: Municipal Solid Waste "Waste-shed" Carbon Footprint (Total 7; Data 4, Speed 3)
- **Procedures:** P1, P2, P3, P4, P5, P6.
- **Data evidence:**
  - S-WASTE is verified: the 2024 release covers 229 si/gun/gu and includes public incineration and landfill facility tables with throughput.
  - The incinerator API 15164842 is verified (free key).
  - S-IPCC5, S-POP and S-BND are verified.
- **Why 4:** the result-table ZIP was not opened, so multi-sheet cleaning is expected; the API key is free.
- **Speed evidence:** an LP from 229 generating si/gun/gu to the public facilities listed in the release (the incinerator API describes about 300 incinerators nationwide), plus a Monte Carlo on composition and FOD parameters. Score 3.

### Rank 4= — Idea 4: Air-Pollutant Footprint of Electricity Use (Total 6; Data 3, Speed 3)
- **Procedures:** P1, P3, P4, P5, P6, P7.
- **Data evidence:**
  - CleanSYS statAnnual is verified: facility-level annual kg/yr with 소재지, Excel/CSV.
  - S-EPSIS and S-KEPCO are verified.
  - CAPSS is **unverified at si/gun/gu**. Its Excel export is confirmed only for sido, although the query tool offers si/gun/gu. That is one input unverified, so the score is 3.
- **Speed evidence:** the same LP as Idea 3, plus name-matching TMS facilities to EPSIS units and a Monte Carlo. Score 3.

### Rank 4= — Idea 10: Cattle-Manure Nitrogen-shed (Total 6; Data 3, Speed 3)
- **Procedures:** P1, P3, P4, P5, P6.
- **Data evidence:**
  - KOSIS DT_1EO251 is verified: cattle by si/gun/gu, quarterly 2021–2026. The data.go.kr 15147310 한우 CSV by si/gun is also verified.
  - "시군별 논밭별 경지면적" is verified.
  - S-IPCC4 Ch. 10 is verified.
  - RDA crop N requirement rates are **unverified**. That is one input, so the score is 3.
  - Pig and poultry data at si/gun/gu are unverified. They are optional here and noted as a risk.
- **Speed evidence:** a surplus/deficit tabulation, one transport LP and a Monte Carlo on excretion factors. Score 3.

### Rank 6= — Idea 6: Food-Waste Treatment Footprint (Total 5; Data 2, Speed 3)
- **Procedures:** P1, P2, P3, P4, P5, P6.
- **Data evidence:**
  - Food-waste rows by si/gun/gu in S-WASTE are verified.
  - The national food-waste facility list with treatment type and capacity is **unverified**. data.go.kr holds only 경상남도 (15054866), 광주 (15119083) and Daegu files, and it is unconfirmed whether S-WASTE's "공공기타" table covers food-waste plants by type. This is the key supply-side input, so the score is 2.
- **Speed evidence:** an LP plus a Monte Carlo on small data. Score 3.

### Rank 6= — Idea 8: Commuting Carbon Footprint from Census OD (Total 5; Data 2, Speed 3)
- **Procedures:** P2, P3, P4, P5, P6, P7.
- **Data evidence:**
  - The 2020 si/gun/gu OD and the mode-by-residence tables on KOSIS are verified. They are separate tables, not cross-tabulated.
  - S-BND and S-KEPCO are verified.
  - Mode-specific gCO2/pkm is **unverified**: the MOLIT page failed and the PDF opened had no factors. This is a key input, so the score is 2.
- **Speed evidence:** OD tabulation, centroid distances and a lightweight Monte Carlo on distance and factors. No optimization is needed, but the Monte Carlo is part of the design. Score 3.

### Rank 8= — Idea 1: The Carbon Hoofprint of Korean Si/Gun/Gu (Total 4; Data 2, Speed 2)
- **Procedures:** P1, P2, P3, P4, P5, P6, P7.
- **Data evidence:**
  - Verified: KNHANES (registration and pledge), S-POP, the slaughterhouse API (key), the Food Balance Sheet PDF, cattle numbers by si/gun/gu, S-KEPCO and S-BND.
  - **Unverified:** the agriculture breakdown inside the GIR regional ZIP, which is the key per-location intensity input. Also the mtrace slaughter data, which is sido-only and has no download format shown, and pig/poultry numbers below sido.
  - A key input is unverified, so the score is 2.
- **Speed evidence:** several heavy cleaning steps:
  - building a Korean food-code → beef/pork/chicken crosswalk from KNHANES dietary files (the paper relied on USDA FICRCD, Methods p. 9);
  - extracting the 360-page balance-sheet PDF;
  - unpacking a 59.6 MB inventory ZIP;
  - then the LP and Monte Carlo.
  - Score 2.

### Rank 8= — Idea 7: Embodied Cement Carbon of New Construction (Total 4; Data 2, Speed 2)
- **Procedures:** P1, P2, P3, P4, P5, P6.
- **Data evidence:**
  - Building permits (15044695) are verified as a free XLSX, and S-GHGDISC is verified.
  - Cement plant locations and production are **unverified**: cement.or.kr gave a TLS error and browser navigation failed.
  - The per-m² cement coefficient is **unverified**.
  - A key input is unverified, so the score is 2.
- **Speed evidence:** a 6,151,376-row permit download that needs address parsing, plus plant geocoding, before the LP. That is a large download plus heavy cleaning, so the score is 2.

### Rank 10 — Idea 9: Energy Footprint of Tap-Water Supply (Total 2; Data 1, Speed 1)
- **Procedures:** P1, P2, P3, P4, P5.
- **Data evidence:**
  - National waterworks statistics and plant electricity use are **unavailable** from the sources checked. waternow.go.kr returned an error page or redirected to an app intro, and data.go.kr "상수도통계" lists city files only (e.g. Namyangju 3074156). The national dataset 15149349 is sewage, not water supply.
  - A key input is unavailable, so the score is 1.
- **Speed evidence:** the only route is compiling dozens of city files by hand, which breaks the "no manual data collection" constraint for a national study. Score 1.
