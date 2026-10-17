# 02 — Candidate Ideas for South Korea

Input: `01-method-summary.md`. Procedure codes:

| Code | Procedure (from paper) |
|---|---|
| **P1** | Flow reconstruction with a mass-balanced supply–demand model and optimization (transport LP) |
| **P2** | Consumption estimated from survey or demographic data, allocated from admin units to cities |
| **P3** | Spatially explicit footprint or intensity, with per-location intensities rather than a national average |
| **P4** | Hotspot mapping of inter-city or inter-regional variation |
| **P5** | Scenario testing of demand-side or supply-side interventions |
| **P6** | Uncertainty analysis (Monte Carlo) |
| **P7** | Comparison against a reference quantity |

**Domains** (at most 2 ideas each; numbers are idea numbers): food–livestock: Idea 1 · food–crops: Idea 2 · electricity: Ideas 3, 4 · waste: Ideas 5, 6 · construction materials: Idea 7 · transport: Idea 8 · water: Idea 9 · agri-environment / nutrients: Idea 10.

**About the dataset names.** The input names below were tightened after the Phase 3 checks. Some were renamed to the exact dataset title found, some agencies were renamed (Statistics Korea → 국가데이터처; Ministry of Environment → 기후에너지환경부), and two weak sources were swapped for verified alternatives: the KAPE slaughter source in Idea 1 became mtrace.go.kr, and Idea 2's emission factors now include IPCC Vol. 4 Ch. 5. Idea 10 was added after Phase 3 as a buffer, built only from sources checked in that phase.

**What the checks found is not decided here.** Each input's verified, unverified or unavailable status is recorded in `03-data-verification.md`. Ideas 7 and 9 have key inputs that turned out unverified or unavailable. They are kept so that Phase 4 can score them, and Idea 10 keeps the count of data-viable ideas at 8 or more.

---

## Idea 1: The Carbon Hoofprint of Korean Si/Gun/Gu (Beef, Pork, Chicken)
- **Research question:** How much do per capita GHG footprints of meat consumption differ across Korean si/gun/gu once meat is traced from slaughterhouse regions with different production intensities, rather than using one national intensity?
- **Study area and spatial unit:** All si/gun/gu (consumption); sido slaughterhouse regions (supply and intensity).
- **Paper procedures reused:** P1, P2, P3, P4, P5, P6, P7
- **Required inputs:**
  1. KNHANES raw data (국민건강영양조사 원시자료, dietary intake) — Korea Disease Control and Prevention Agency (KDCA)
  2. Resident population by 법정동, sex and age (지역별(법정동) 성별 연령별 주민등록 인구수) — Ministry of the Interior and Safety (MOIS), via data.go.kr
  3. Slaughter heads by slaughterhouse region (도축장지역(시도)별 도축두수) — Korea Institute for Animal Products Quality Evaluation (KAPE, 축산물품질평가원), 축산유통 통계누리 (mtrace.go.kr)
  4. Slaughterhouse licensing records (동물_도축업 조회서비스) — MOIS, via data.go.kr
  5. Regional GHG inventory 2010–2023 (지역 온실가스 인벤토리), agriculture sector — Greenhouse Gas Inventory and Research Center (GIR)
  6. Livestock numbers by si/gun/gu (가축동향조사: 축종별 시군구별 농장수 및 마리수) — 국가데이터처, via KOSIS
  7. Food Balance Sheet 2023 (식품수급표) — Korea Rural Economic Institute (KREI)
  8. Electricity use by contract type and si/gun/gu, household use (계약종별 전력사용량, 주택용) — KEPCO Power Data Open Portal
  9. Si/gun/gu census boundary SHP ((센서스경계)시군구경계) — Ministry of Land, Infrastructure and Transport (MOLIT), via data.go.kr / VWorld
- **Output artifact:** Choropleths of per capita footprint and intensity, a sido→si/gun/gu meat-flow map, a scenario bar chart (waste halving, beef→pork/chicken swap, meatless day), a Monte Carlo error table, a ratio map of footprint to household-electricity CO2, and a short paper-style report.
- **Free-account or API-key requirement:** Yes:
  - KNHANES: pledge and user registration.
  - data.go.kr API key for slaughterhouse records.
  - KEPCO portal login for the Excel download.
  - Possibly a VWorld login for the boundary file.
- **Main risk:** Production intensity is available only at sido level, and pig and poultry numbers were not found below sido. Most of the paper's within-meatshed variation would be lost, and a Korean food-code→meat crosswalk must be built by hand.

## Idea 2: Rice-shed Methane Footprint of Korean Cities
- **Research question:** Where is the paddy CH4 embodied in each si/gun/gu's rice consumption emitted, and how much does yield-driven variation in per-kg intensity change urban rice footprints?
- **Study area and spatial unit:** All si/gun/gu, for both production (si/gun) and consumption (si/gun/gu).
- **Paper procedures reused:** P1, P2, P3, P4, P5, P6
- **Required inputs:**
  1. Rice production and paddy area by si/gun (시군별 논벼 생산량, DT_1ET0034; 시군별 논벼 재배면적, DT_1ET0033) — 국가데이터처, via KOSIS
  2. Per capita annual grain/rice consumption (1인당 연간 양곡소비량, 양곡소비량조사) — 국가데이터처, via KOSIS
  3. Resident population by 법정동, sex and age — MOIS, via data.go.kr
  4. Paddy CH4 emission factors: 2006 IPCC Guidelines Vol. 4, Ch. 5 (IPCC-TFI), with the national value from the 2025 국가 온실가스 인벤토리 보고서 (GIR) where available
  5. Si/gun/gu census boundary SHP — MOLIT, via data.go.kr / VWorld
- **Output artifact:** A producer→consumer flow map, a per-kg intensity map, a per capita footprint choropleth, Monte Carlo bands, and a scenario table (intermittent-drainage adoption; halving household rice waste).
- **Free-account or API-key requirement:** Optional. KOSIS tables download without a key (a free KOSIS key is needed only for the API); VWorld may need a free login.
- **Main risk:** Rice is traded nationally through government stocks and RPC (rice processing complex) brokerage. Distance-minimizing flows may therefore misrepresent real sourcing, and yield-scaled intensity reflects only the yield term of CH4 variation.

## Idea 3: Consumption-Based Electricity GHG Footprint of Si/Gun/Gu ("Electricity-shed")
- **Research question:** If each si/gun/gu's electricity demand is matched to generating units by a distance-minimizing transport model, how do consumption-based emissions and intensity vary across cities compared with the national grid factor?
- **Study area and spatial unit:** All si/gun/gu (demand); generating units (supply).
- **Paper procedures reused:** P1, P2, P3, P4, P5, P6, P7
- **Required inputs:**
  1. Electricity use by contract type and si/gun/gu (계약종별 전력사용량) — KEPCO Power Data Open Portal
  2. Generation and capacity by generating unit (발전기별 발전량; 발전기 현황) — Korea Power Exchange (KPX), EPSIS
  3. GHG statement disclosure by company/site (온실가스 명세서 주요정보) — GIR
  4. National grid emission factor (전력배출계수, 2023) — 기후에너지환경부 / GIR
  5. Si/gun/gu census boundary SHP — MOLIT, via data.go.kr / VWorld
- **Output artifact:** A unit→si/gun/gu flow map, per capita consumption-based CO2 choropleths, a map of the ratio to the national-factor estimate, a coal-phase-out scenario chart, and a Monte Carlo MAPE table.
- **Free-account or API-key requirement:** Yes. A KEPCO portal login is needed for the Excel download; VWorld may need a free login.
- **Main risk:** Electricity is pooled on one national grid, so distance-based "sourcing" is a modelling construct. Plants also lack coordinates and must be geocoded by name.

## Idea 4: Air-Pollutant Footprint of Electricity Use (NOx/SOx/dust)
- **Research question:** Which si/gun/gu host the stack emissions that serve other cities' electricity use, and how does each city's "imported" pollution compare with the pollution emitted within its own boundary?
- **Study area and spatial unit:** All si/gun/gu; TMS-monitored facilities.
- **Paper procedures reused:** P1, P3, P4, P5, P6, P7
- **Required inputs:**
  1. Stack TMS annual emissions by facility (굴뚝자동측정기기 연간 배출량) — Korea Environment Corporation (한국환경공단), CleanSYS
  2. Generation by generating unit — KPX, EPSIS
  3. Electricity use by si/gun/gu — KEPCO Power Data Open Portal
  4. Air-pollutant emissions by si/gun/gu (CAPSS 배출량 통합검색) — National Air Emission Inventory and Research Center (국가미세먼지정보센터)
  5. Si/gun/gu census boundary SHP — MOLIT, via data.go.kr / VWorld
- **Output artifact:** A pollution-shed flow map, a ratio map of imported to local emissions, and a coal-to-LNG scenario chart.
- **Free-account or API-key requirement:** Yes. A KEPCO portal login is needed; VWorld may need a free login.
- **Main risk:** TMS facility names must be matched to EPSIS units by hand, and the export format of CAPSS at si/gun/gu level is unconfirmed.

## Idea 5: Municipal Solid Waste "Waste-shed" Carbon Footprint
- **Research question:** How do the GHG emissions of treating each si/gun/gu's household waste vary with the incinerators and landfills that receive it, and how much would recycling gains and the capital-region direct-landfill ban change them?
- **Study area and spatial unit:** All si/gun/gu (229 surveyed units, generation side); public treatment facilities.
- **Paper procedures reused:** P1, P2, P3, P4, P5, P6
- **Required inputs:**
  1. 2024 전국 폐기물 발생 및 처리현황, household-waste generation and treatment by si/gun/gu (결과표) — 기후에너지환경부 / Korea Environment Corporation, via the Resource Circulation Information System (recycling-info.or.kr)
  2. Treatment-facility tables in the same release (공공소각, 공공매립, with throughput), plus the incinerator facility API (폐기물처분부담금 소각시설정보) — Korea Environment Corporation
  3. 2006 IPCC Guidelines Vol. 5 (Waste): fossil-carbon fractions, FOD parameters — IPCC-TFI
  4. Resident population by 법정동 — MOIS, via data.go.kr
  5. Si/gun/gu census boundary SHP — MOLIT, via data.go.kr / VWorld
- **Output artifact:** A per capita waste-GHG choropleth, a facility catchment and flow map, scenario and Monte Carlo tables.
- **Free-account or API-key requirement:** Optional. The data.go.kr API key is free; VWorld may need a free login.
- **Main risk:** The result tables come as a multi-sheet ZIP with HWP/PDF companions, so cleaning may be slower than expected. Inter-municipal waste contracts also break distance-based allocation.

## Idea 6: Food-Waste Treatment Footprint of Si/Gun/Gu
- **Research question:** How do per capita food-waste GHGs vary across si/gun/gu depending on whether the receiving facility makes feed, compost or biogas, and what is gained by halving food waste?
- **Study area and spatial unit:** All si/gun/gu; food-waste treatment facilities.
- **Paper procedures reused:** P1, P2, P3, P4, P5, P6
- **Required inputs:**
  1. 2024 전국 폐기물 발생 및 처리현황, food-waste separate-collection rows (음식물류분리배출) by si/gun/gu — 기후에너지환경부 / Korea Environment Corporation (recycling-info.or.kr)
  2. National food-waste treatment facility list with type and capacity (음식물류폐기물 처리시설 설치·운영 현황) — 기후에너지환경부
  3. 2006 IPCC Guidelines Vol. 5, Ch. 4 (biological treatment) — IPCC-TFI
  4. Resident population by 법정동 — MOIS, via data.go.kr
  5. Si/gun/gu census boundary SHP — MOLIT, via data.go.kr / VWorld
- **Output artifact:** A per-tonne and per capita footprint choropleth, a facility-type flow map, and a waste-halving scenario.
- **Free-account or API-key requirement:** No (expected); VWorld may need a free login.
- **Main risk:** No national food-waste facility list was found online; only provincial or city files exist.

## Idea 7: Embodied Cement Carbon of New Construction by Si/Gun/Gu
- **Research question:** How much cement CO2 is embodied in each si/gun/gu's new floor area, traced to specific cement plants with plant-specific intensities?
- **Study area and spatial unit:** All si/gun/gu (demand); cement plants (supply).
- **Paper procedures reused:** P1, P2, P3, P4, P5, P6
- **Required inputs:**
  1. Building permit records with floor area (건축인허가 기본개요) — MOLIT, via data.go.kr / 건축HUB
  2. Cement plant locations and production — Korea Cement Association (한국시멘트협회)
  3. GHG statement disclosure for cement companies — GIR
  4. Cement intensity per m² floor area — published Korean LCA literature
  5. Si/gun/gu census boundary SHP — MOLIT, via data.go.kr / VWorld
- **Output artifact:** A plant→si/gun/gu flow map, an embodied-CO2 choropleth, and a blended-cement scenario chart.
- **Free-account or API-key requirement:** No (expected); VWorld may need a free login.
- **Main risk:** Plant-level production and a per-m² cement coefficient could not be found openly. The permit file also has over 6 million rows.

## Idea 8: Commuting Carbon Footprint from Census Origin–Destination Flows
- **Research question:** How do per-worker commuting GHG footprints vary by si/gun/gu of residence, and how much would a car-to-rail modal shift cut hotspot emissions?
- **Study area and spatial unit:** All si/gun/gu (OD matrix).
- **Paper procedures reused:** P2, P3, P4, P5, P6, P7
- **Required inputs:**
  1. 2020 census: commuting population by residence × destination si/gun/gu (현 거주지별/통근통학지별 통근통학 인구-시군구) — 국가데이터처, via KOSIS
  2. 2020 census: commuting population by travel mode, by si/gun/gu of residence (성별/연령별/이용 교통수단별 통근통학 인구-시군구) — 국가데이터처, via KOSIS
  3. Si/gun/gu census boundary SHP, used for centroid distances — MOLIT, via data.go.kr / VWorld
  4. Mode-specific emission factors (gCO2/pkm) — MOLIT / Korean transport literature
  5. Electricity use by si/gun/gu, household use (reference quantity) — KEPCO Power Data Open Portal
- **Output artifact:** An OD flow map, a per-worker CO2 choropleth, a modal-shift scenario chart, and a ratio map of commuting CO2 to household-electricity CO2.
- **Free-account or API-key requirement:** Yes. A KEPCO portal login is needed for the reference quantity; VWorld may need a free login.
- **Main risk:** Mode is not cross-tabulated with destination, so each origin's mode shares must be applied to all its destinations. A citable open Korean gCO2/pkm source was not confirmed.

## Idea 9: Energy Footprint of Tap-Water Supply ("Water-shed" of Cities)
- **Research question:** How does the electricity embodied in each si/gun/gu's tap water vary with the treatment plants (local versus multi-regional) that supply it?
- **Study area and spatial unit:** All si/gun/gu; water treatment plants (정수장).
- **Paper procedures reused:** P1, P2, P3, P4, P5
- **Required inputs:**
  1. National waterworks statistics (상수도통계): supply by si/gun/gu, plant capacity — 기후에너지환경부 (국가상수도정보시스템)
  2. Electricity use per treatment plant (kWh/m³) — 기후에너지환경부 / K-water
  3. National grid emission factor — 기후에너지환경부 / GIR
  4. Resident population by 법정동 — MOIS, via data.go.kr
  5. Si/gun/gu census boundary SHP — MOLIT, via data.go.kr / VWorld
- **Output artifact:** A plant-catchment flow map, kWh/m³ and per capita CO2 choropleths, and a leakage-reduction scenario.
- **Free-account or API-key requirement:** No (expected).
- **Main risk:** The national waterworks statistics and plant electricity data could not be found as open files; only city-level files exist.

## Idea 10: Cattle-Manure Nitrogen-shed: Matching Manure Surplus to Cropland Demand
- **Research question:** Which si/gun/gu generate cattle-manure nitrogen beyond what their own cropland can absorb, and what is the minimum-distance redistribution of that surplus to deficit si/gun/gu?
- **Study area and spatial unit:** All si/gun/gu (manure supply); si/gun (cropland demand).
- **Paper procedures reused:** P1, P3, P4, P5, P6
- **Required inputs:**
  1. Cattle numbers by si/gun/gu (축종별 시군구별 농장수 및 마리수, DT_1EO251) — 국가데이터처, via KOSIS; plus 전국 시군별 한우 사육규모 현황 — 가축위생방역지원본부, via data.go.kr
  2. Manure N excretion and management-loss factors: 2006 IPCC Guidelines Vol. 4, Ch. 10 — IPCC-TFI
  3. Paddy and upland area by si/gun (시군별 논밭별 경지면적) — 국가데이터처, via KOSIS
  4. Crop N requirement rates (작물별 비료사용처방기준) — Rural Development Administration (RDA)
  5. Si/gun/gu census boundary SHP — MOLIT, via data.go.kr / VWorld
- **Output artifact:** A manure-N surplus/deficit choropleth (kg N/ha), an LP redistribution flow map with total tonne-km, a herd-reduction / manure-processing scenario table, and Monte Carlo bands on the excretion factors.
- **Free-account or API-key requirement:** No (expected); VWorld may need a free login.
- **Main risk:** Pig and poultry numbers were not found below sido and are the larger manure sources, so a cattle-only analysis understates surpluses. Crop N rates were not located in Phase 3.
