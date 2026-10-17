# 00 — Scope: Locked Analysis Parameters (Idea 2, Phase 0)

**Inputs read:** `04-ranking.md` (Rank 1=, Idea 2 block), `02-ideas.md` (Idea 2; P1–P7), `03-data-verification.md` (Idea 2 rows; S-POP, S-BND, S-KOSIS, S-IPCC4), `01-method-summary.md` (§3 steps A–E, §4, §5).

**Procedures in scope:** P1, P2, P3, P4, P5, P6 (`04-ranking.md`). P7 is not part of Idea 2.

**Year availability and unit counts.** The years available, and the unit counts in (b), were read from the raw files once they were on disk (`01-data-inventory.md`; Phase 0 was finalized after that inventory was written). Each choice below cites the file it rests on.

---

## (a) Analysis year — **2025**

| Source | Latest year present | Evidence |
|---|---|---|
| KOSIS DT_1ET0034 (rice production by si/gun) | 2025 | covers 1965–2025; renewal 2025-11-13 (`data/raw/kosis/DT_1ET0034.csv.meta.json`) |
| KOSIS DT_1ET0033 (paddy area by si/gun) | 2026 | covers 1975–2026 |
| KOSIS DT_1ED0001 (1인당 연간 양곡소비량) | 2025 | covers 1963–2025; renewal 2026-02-02 |
| S-POP (data.go.kr 15099158) | monthly to 2026-09 | the version `_20251231` exists among the 56 past versions |

- **Chosen:** 2025. It is the latest year present in all three of rice production, per capita consumption and population.
  - Population is the **2025-12-31** resident registration count, the year-end figure. The production and consumption figures are 2025 annual totals.
- **Rejected:**
  - 2026: no production or consumption figures yet.
  - 2024: complete, but one year older with no offsetting gain.
  - Mid-year population (`_20250630`): resident registration annual statistics are conventionally reported at 31 December, so using the same reference point keeps the demand side comparable with other year-end KOSIS series.

## (b) Spatial units

### Consuming units — **252 si/gun/gu**
- **Definition:** the first 5 digits (시군구 code) of the 10-digit 법정동코드 in `data/raw/pop/mois_bjd_pop_20251231.csv`.
  - This keeps autonomous gu (e.g. 종로구 11110) and the non-autonomous gu of large cities (e.g. 수원시 장안구 41111) as separate units. 세종특별자치시 (36110) is one unit.
- **Count:** 252 codes, all with population > 0, totalling 51,117,378 residents.
- **Source:** S-POP, version `_20251231`.
- **Rejected:** the 250-row S-BND unit list (vintage differs from the 2025-12-31 code list, and the file is blocked; see (e) for the approved geometry substitute). The 226 local-government (기초자치단체) level was also rejected: it would merge the gu of large cities, which the population file distinguishes.

### Producing units — **156 units with 2025 production > 0**
- **Definition:** the lowest-level rows of `data/raw/kosis/DT_1ET0034.csv` for 2025:
  - **148 si/gun** in the provinces (149 si/gun rows; 군위군 37310 reports "-" for 2024–2025 because it moved to 대구광역시 on 2023-07-01 and is now inside 대구's figure);
  - **8 metropolitan/special cities** that KOSIS reports only as a whole (소계): 서울, 부산, 대구, 인천, 광주, 대전, 울산, 세종.
- **Source:** KOSIS DT_1ET0034, 2025 column.
- **Rejected:** forcing producers onto the 252 consuming units. KOSIS gives no gu-level rice data for the metropolitan cities, and splitting them would invent a disaggregation.

### Supply–demand balance
2025 national production (3,539,195 t, DT_1ET0034) is larger than household demand. Household demand is per capita household consumption × population (Phase 2). The difference covers processing, food service, government stocks and stock change, and losses. Phase 4 will absorb it with **one explicit slack sink node, "non-household disposition"**, rather than inflating demand.

## (c) Mass unit — **tonnes of milled rice (정곡)**

- **Production.** DT_1ET0034 is titled **"시군별 논벼 생산량(정곡, 92.9%)"**: production is already expressed as polished rice (정곡) at a 92.9% milling rate (KOSIS table title, `DT_1ET0034.csv.meta.json`). Its yield item (10a당 생산량, kg) is on the same 정곡 basis; t/ha = (kg/10a) ÷ 100.
- **Consumption.** DT_1ED0001 item "10 쌀 / 00 계 / 전가구" is kg of rice per person per year: **53.9 kg in 2025**. This is rice as consumed by households, i.e. milled rice.
- **Conversion applied: 1:1.** Both quantities are already on a milled-rice basis, so no paddy↔milled factor is applied by this study. The only conversion involved is the 92.9% 정곡 rate, and KOSIS has already applied it to production.
  - **Caveat:** DT_1ED0001 does not state its basis explicitly. Reading "쌀" as milled rice is an interpretation, and it is recorded here.
- **CH4 is unaffected by this choice.** CH4 is computed per hectare (IPCC Eq. 5.1). The mass unit only enters as the denominator of per-kg intensity.
- **Rejected:** a paddy (조곡) basis. It would need a paddy→milled ratio that is not in the input set, and it would not change the per-hectare CH4.

## (d) CH4 GWP — **28 (100-year)**

- **Value:** 1 t CH4 = 28 t CO2e.
- **Source:** GIR, 2025 국가 온실가스 인벤토리 보고서 (NID), **표 1-9 "온실가스별 지구온난화지수(GWP)"** (report p. 1-26; PDF p. 67): "메탄 CH4 28". The NID front matter (PDF p. 2) states that national statistics follow the 2006 IPCC Guidelines and the GWPs of the IPCC Fifth Assessment Report (AR5), per MPGs para. 37.
  - File: `data/raw/gir/NID2025_ko.pdf`.
- **Why this value:** using the same GWP as the national inventory keeps the results comparable with the NID rice total (6,879 kt CO2e in 2023, 표 5-24).
- **Rejected:**
  - AR6 values (27.0 non-fossil / 29.8 fossil): not used by the Korean inventory.
  - AR4 (25) and SAR (21): superseded under the Paris Agreement transparency framework.

## (e) LP impedance — **great-circle distance between unit centroids**

- **Measure:** haversine distance (km) between the centroids of each producing unit and each consuming unit.
  - Centroids are computed on the boundary polygons in a projected CRS (EPSG:5179, Korea 2000 / Unified CS), then converted to WGS84 for the haversine.
  - A metropolitan producing unit's centroid is the centroid of the union of its gu/gun polygons.
- **Rejected:** road distance. It needs a road network and a routing engine, which are not in Idea 2's input set. Straight-line impedance is the option `01-method-summary.md` §5 names as portable for the transport LP.

### Geometry source — amended 2026-10-17 (study owner decision)
- **Originally locked:** S-BND (`국토교통부_(센서스경계)시군구경계`). It is **BLOCKED** behind a VWorld login, and data.go.kr has no mirror with geometry (`01-data-inventory.md`).
- **Approved substitute:** **geoBoundaries gbOpen KOR ADM2**.
  - boundaryYear 2020; 228 polygons; CC BY 3.0; source citypopulation.de.
  - File: `data/raw/boundary/gb/geoBoundaries-KOR-ADM2.shp`.
- **Patch for a missing unit — 영광군 (Yeonggwang-gun, 전라남도).** geoBoundaries has 228 polygons against 229 units in its own `admUnitCount`; 영광군 is the one missing. Without it, 영광군's rice production and population could not be placed, and the mass balance would break. Its polygon was taken from **OpenStreetMap relation 7624187** (Nominatim, ODbL 1.0, no login; `data/raw/boundary/osm/yeonggwang_nominatim.json`).
  - The OSM boundary extends into the sea (2,105 km²), so it was clipped to land (ADM1 polygons) and to the gap between existing polygons, giving 397 km².
  - Its neighbours are Gochang-gun, Jangseong-gun and Hampyeong-gun, as expected.
  - Details: `04-flows.md` §1. This patch extends the approved substitution and is flagged here for the study owner.
- **Auxiliary inputs used only to join names to polygons:**
  - geoBoundaries KOR ADM1 (Public Domain), to assign each polygon to a province;
  - SGIS 시군구경계영문 (data.go.kr 15135856), for official Korean↔English names.
- **Consequences for (b):** the 252 consuming and 156 producing units are unchanged. Geometry is attached to them as follows:
  - Each **일반구** consuming unit (e.g. 수원시 장안구) uses its **parent city's polygon and centroid**, because the substitute has no 일반구 polygons. All gu of one city therefore share the same distances.
  - Each **metropolitan producing unit** (서울 … 세종) uses the union of the polygons the crosswalk assigns to that city.
  - 군위군's polygon is assigned to 대구 (transfer of 2023-07-01).
  - Maps (Phase 8) are drawn at the polygon level: 일반구 values are aggregated to the parent city (Σ footprint / Σ population).
- **Rejected alternatives:**
  - GADM: its licence is not open for redistribution.
  - Remembered or hand-typed coordinates: not allowed by the no-invented-numbers constraint.
