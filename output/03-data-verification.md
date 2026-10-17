# 03 — Data Verification

**Checked:** 2026-10-17. Input: `02-ideas.md`.

**How each source was checked.** Each source was first located with WebSearch. Each candidate page was then fetched in one of two ways:
- WebFetch, through fetch agents, for server-rendered pages.
- The built-in browser, for JavaScript-only portals: KOSIS, KNHANES, CleanSYS, EPSIS, KEPCO, recycling-info, VWorld, mtrace and data.go.kr search.

Each URL was tried at most twice. Failures are recorded below and were not retried further.

**Status definitions**
- **verified**: a URL in the table was actually fetched in this phase, and it showed four things: the dataset exists, it is free, it can be downloaded in a machine-readable form, and its spatial unit is as stated. Notes record any caveats, such as a login, an API key, or a file format not opened.
- **unverified**: the page could not be loaded, or the page did not show one of those four facts (existence, free access, format, or resolution).
- **unavailable**: the sources checked show no free national dataset at the required resolution.

**Renamed agencies.** Several names changed during 2025–26; the table uses the names now shown on the sites.
- Statistics Korea now appears as **국가데이터처** (mods.go.kr).
- The Ministry of Environment now appears as **기후에너지환경부** (mcee.go.kr).

Shared inputs, such as population and boundaries, get one row per idea that uses them so that each idea's inputs are complete. Their evidence is the same in every row.

## Shared-source evidence (referenced in the table)

| Ref | Source | URL fetched | What was confirmed on the page |
|---|---|---|---|
| S-POP | MOIS resident population by 법정동, sex and single-year age | https://www.data.go.kr/data/15099158/fileData.do | Free; CSV downloads without login. 법정동 rows carry 시도/시군구 names, so they aggregate to si/gun/gu. Monthly; reference month 2026-09, 18,627 rows. The API version (15108074) needs an auto-approved key. |
| S-BND | Si/gun/gu boundary SHP, "국토교통부_(센서스경계)시군구경계" | https://www.data.go.kr/data/15125064/fileData.do → https://www.vworld.kr/dtmk/dtmk_ntads_s002.do?dsId=30015 | Free (비용부과 무료; 이용허락범위 제한 없음). SHP, 250 rows, nationwide, updated yearly. Downloaded through VWorld, whose site marks some menus as login-only; whether this download needs a free login was not confirmed. |
| S-KOSIS | KOSIS table access and Open API | https://kosis.kr/openapi/introduce/introduce_01List.do ; https://kosis.kr/openapi/community/community_0401List.do | Free. A free member key is auto-approved and valid for 2 years. Formats: JSON/XLS/XML/SDMX. Each table page shows a "다운로드" button (seen on DT_1ET0034). |
| S-EF | National grid emission factor | https://www.kukinews.com/article/view/kuk202512180131 ; http://www.gir.go.kr/home/board/read.do?menuId=36&boardId=86&boardMasterId=2 | The 2023 factor, 0.4173 tCO2eq/MWh, is reported in the news article. The GIR post attaches the official factor file as .hwpx/.pdf; the file itself was not opened. |
| S-KEPCO | KEPCO Power Data Open Portal, 계약종별 전력사용량 | https://bigdata.kepco.co.kr/cmsmain.do?scode=S01&pcode=000166 | Area choices go down to "전체(시 / 군 / 구)", and contract types include 주택용 (household). The page script calls the download "엑셀다운로드" (Excel) and shows the alert "자료에 대한 다운로드는 로그인 이후 가능합니다", so a **free login is required**. Updated monthly. |
| S-EPSIS | EPSIS generation by generating unit (발전기별 발전량) and unit list | https://epsis.kpx.or.kr/epsisnew/selectEkgeGepGbpGrid.do?menuId=060105 ; https://epsis.kpx.or.kr/epsisnew/selectEkpoBcrGrid.do?menuId=020901 | Free, EXCEL/CSV buttons, years 2002–2025. Generation can be filtered by 발전원 and company. The page notes that some small and renewable units are missing. The unit list can be filtered by 지역별 (17 sido). No coordinates are given. |
| S-GHGDISC | GIR GHG statement disclosure (명세서 주요정보) | http://www.gir.go.kr/home/index.do?menuId=37 | Free "엑셀 다운로드". Covers 2011–2025 (1,173 records for 2025). Per company, with some designated at site (사업장) level: emissions in tCO2eq and energy in TJ. No addresses or coordinates. |
| S-IPCC5 | 2006 IPCC Guidelines Vol. 5 (Waste) | https://www.ipcc-nggip.iges.or.jp/public/2006gl/vol5.html | Free per-chapter PDFs plus IPCC_Waste_Model.xls. |
| S-IPCC4 | 2006 IPCC Guidelines Vol. 4 (AFOLU) | https://www.ipcc-nggip.iges.or.jp/public/2006gl/vol4.html | Free chapter list incl. Ch. 5 Cropland and Ch. 10 Livestock & Manure (and Ch. 11 Managed soils) |
| S-WASTE | 전국 폐기물 발생 및 처리현황 (2024) | https://www.recycling-info.or.kr/rrs/stat/envStatDetail.do?bbsId=BBSMSTR_000000000002&nttId=1596&s_nttSj=KEC005 | Free downloads: summary PDF, full PDF, HWP, and "결과표.zip" (18.6 MB, result tables). The survey covers "전국 17개 시도 및 229개 시군구". Contents include household-waste generation and treatment, food-waste separate collection (음식물류분리배출), and treatment-facility tables (공공소각, 공공매립, 공공기타 with throughput). File types inside the ZIP were not opened. |

## Verification table

| Idea | Input | Source URL | Free? | Format | Spatial resolution | Status |
|---|---|---|---|---|---|---|
| 1 | KNHANES raw data (incl. dietary intake) | https://knhanes.kdca.go.kr/knhanes/main.do (raw-data menu and 2026-07-31 notice) | Yes. Download after signing the 이행서약서 and 보안서약서; a 사용자등록 login is shown | SAS / SPSS | Individual microdata (national sample). Whether the 24-h recall file is part of the download set was not confirmed on the page | verified (free registration/pledge) |
| 1 | Resident population by si/gun/gu, age, sex | S-POP | Yes | CSV | 법정동 → si/gun/gu | verified |
| 1 | Slaughter volumes by slaughterhouse region | https://mtrace.go.kr/stats/ (축산유통 통계누리, KAPE) | Yes (public viewer) | Table viewer; download format not shown on fetched page | Slaughterhouse region = **sido** (table "도축장지역(시도)별 소의 품종별 성별도축두수"). Also lists region-to-region cattle movement counts. The KAPE data.go.kr APIs 15056898/15000577 give per-animal or national data only | unverified (format; sido only) |
| 1 | Slaughterhouse locations (도축업 인허가) | https://www.data.go.kr/data/15155105/openapi.do | Yes. Free API key, auto-approved | JSON/XML API | Facility, with address; coordinates in EPSG:5174. Species field not stated | verified (free API key) |
| 1 | Regional (sido) GHG inventory, agriculture | http://www.gir.go.kr/home/board/read.do?menuId=36&boardId=89&boardMasterId=2 | Yes | ZIP (59.6 MB, "2025 지역 온실가스 통계.zip"); contents not opened | Sido stated in post; agriculture/livestock breakdown inside not confirmed | unverified |
| 1 | Livestock numbers by si/gun/gu | KOSIS DT_1EO251 https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1EO251 ; https://www.data.go.kr/data/15147310/fileData.do | Yes | KOSIS download / CSV | Cattle (한육우, 한우, 육우, 젖소) by 시군구, quarterly 2021–2026. The 한우 CSV is by 시군. **Pigs and chickens at si/gun/gu not found**: the KOSIS search "돼지 시군구별 사육" returned 0 results | verified for cattle; pigs/chickens unverified |
| 1 | Food Balance Sheet 2023 | https://repository.krei.re.kr/bitstream/2018.oak/31894/1/E05-2024.pdf | Yes | PDF (360 pp.); text extractable, including meat supply rows (e.g. "Pig Meat" with production and imports) | National | verified (PDF table cleaning) |
| 1 | Household electricity by si/gun/gu (reference) | S-KEPCO | Yes (free login) | Excel | si/gun/gu, 주택용 separable | verified (free login) |
| 1 | Si/gun/gu boundary | S-BND | Yes | SHP | si/gun/gu | verified (VWorld login may be needed) |
| 2 | Rice production and paddy area by si/gun | KOSIS DT_1ET0034 https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1ET0034 ; DT_1ET0033 (paddy area), found via https://kosis.kr/search/search.do?query=논벼+시군별 | Yes | KOSIS download / Open API (S-KOSIS) | si/gun, e.g. 수원시 rows seen. Fields: area (ha), yield per 10a, production. 1965–2025 | verified |
| 2 | Per capita rice consumption | KOSIS "1인당 연간 양곡소비량" (양곡소비량조사, 1963–2025), found via https://kosis.kr/search/search.do?query=1인당+양곡소비량 | Yes | KOSIS download | National | verified |
| 2 | Population by si/gun/gu | S-POP | Yes | CSV | si/gun/gu | verified |
| 2 | Paddy CH4 emission factors | GIR NID 2025 http://www.gir.go.kr/home/board/read.do?menuId=36&boardId=90&boardMasterId=2 ; IPCC 2006 Vol.4 Ch.5 (S-IPCC4) | Yes | PDF (NID, 11 MB, not opened); IPCC chapter PDF | Coefficients (national / default) | verified (IPCC default available); NID rice table unverified |
| 2 | Si/gun/gu boundary | S-BND | Yes | SHP | si/gun/gu | verified |
| 3 | Electricity use by si/gun/gu and contract type | S-KEPCO | Yes (free login) | Excel | si/gun/gu | verified (free login) |
| 3 | Power plant / unit list, capacity, fuel, generation | S-EPSIS | Yes | EXCEL/CSV | Generating unit; location only as sido and plant name, **no coordinates** | verified (geocoding by plant name needed) |
| 3 | Plant/company GHG emissions | S-GHGDISC | Yes | Excel | Company, some site-level; no address | verified |
| 3 | National grid emission factor | S-EF | Yes | News text; GIR .hwpx/.pdf | National | verified |
| 3 | Si/gun/gu boundary | S-BND | Yes | SHP | si/gun/gu | verified |
| 4 | Stack TMS annual emissions per facility | https://cleansys.or.kr/statAnnual.do | Yes | "Excel Down" / "CSV Down" | Facility (사업장), with 소재지. Annual dust, SOx, NOx, HCl, HF, NH3 and CO (kg/yr) | verified |
| 4 | Power plant list and generation | S-EPSIS | Yes | EXCEL/CSV | Unit; sido | verified |
| 4 | Electricity use by si/gun/gu | S-KEPCO | Yes (free login) | Excel | si/gun/gu | verified (free login) |
| 4 | CAPSS air-pollutant emissions by si/gun/gu | https://www.air.go.kr/capss/emission/search.do?menuId=33 ; sido Excel link /capss/emission/download.do?emissionType=sido&exmnYear=2023 | Yes | Excel confirmed for **sido**; export format at si/gun/gu not shown | Query tool offers 전국/시도/시군구, 1999–2023 | unverified (si/gun/gu export format) |
| 4 | Si/gun/gu boundary | S-BND | Yes | SHP | si/gun/gu | verified |
| 5 | Household waste generation and treatment by si/gun/gu | S-WASTE | Yes | PDF/HWP + ZIP of result tables | 229 si/gun/gu (KOSIS DT_106N_29_2020005 is sido only) | verified (ZIP contents not opened) |
| 5 | Treatment facility inventory (incinerators, landfills) | S-WASTE facility tables ; https://www.data.go.kr/data/15164842/openapi.do (incinerators) | Yes. API: free key, auto-approval for development, reviewed approval (심의승인) for production | ZIP tables; JSON/XML API | Facility, with address (incinerators: about 300 nationwide, 2010–present). No national landfill file with capacity on data.go.kr (NIER API 15058301 has location but no capacity) | verified (facility throughput via S-WASTE; API key optional) |
| 5 | IPCC waste-sector default factors | S-IPCC5 | Yes | PDF/XLS | Coefficients | verified |
| 5 | Population by si/gun/gu | S-POP | Yes | CSV | si/gun/gu | verified |
| 5 | Si/gun/gu boundary | S-BND | Yes | SHP | si/gun/gu | verified |
| 6 | Food waste (음식물류) by si/gun/gu | S-WASTE (food-waste separate-collection rows named in the 2026-01-06 and 2026-10-13 revision notes) | Yes | PDF/HWP + ZIP | si/gun/gu | verified (ZIP contents not opened) |
| 6 | National food-waste treatment facility list with type and capacity | data.go.kr search (27 results), https://www.data.go.kr/data/15054866/fileData.do (경상남도 only) ; https://data.go.kr/catalog/15157567/openapi.json (Daegu only) | Yes (regional files) | CSV / XML | Province or city only; no national list on data.go.kr. Whether S-WASTE's "공공기타" table covers food-waste plants by type was not confirmed | unverified (key input) |
| 6 | Biological-treatment emission factors | S-IPCC5 (Ch. 4) | Yes | PDF | Coefficients | verified |
| 6 | Population by si/gun/gu | S-POP | Yes | CSV | si/gun/gu | verified |
| 6 | Si/gun/gu boundary | S-BND | Yes | SHP | si/gun/gu | verified |
| 7 | Building permits / starts floor area | https://www.data.go.kr/data/15044695/fileData.do (건축인허가 기본개요, via https://www.hub.go.kr) ; https://www.index.go.kr/unify/idx-info.do?idxCd=1224 (sido XLSX) | Yes | XLSX, **6,151,376 rows** (record level with address) | Permit record → aggregable to si/gun/gu; official summary tables are sido only | verified (large download) |
| 7 | Cement plant locations and production | https://www.cement.or.kr | — | — | — | unverified (WebFetch: "certificate has expired"; browser navigation failed) |
| 7 | Cement company/site GHG emissions | S-GHGDISC | Yes | Excel | Company / some sites | verified |
| 7 | Cement intensity per m² floor area | https://www.koreascience.kr/article/JAKO201321356458054.page (only search hit; gives no per-m² value) | Yes | — | — | unverified |
| 7 | Si/gun/gu boundary | S-BND | Yes | SHP | si/gun/gu | verified |
| 8 | Commuting OD by si/gun/gu (2020 census) | KOSIS "현 거주지별/통근통학지별 통근통학 인구(12세 이상)-시군구" (2020), found via https://kosis.kr/search/search.do?query=통근통학지별+시군구 | Yes | KOSIS download (S-KOSIS) | si/gun/gu × si/gun/gu | verified |
| 8 | Travel mode by si/gun/gu | KOSIS "성별/연령별/이용 교통 수단별 통근 통학 인구(12세 이상)-시군구" (2020), found via https://kosis.kr/search/search.do?query=통근통학+교통수단+시군구 | Yes | KOSIS download | si/gun/gu of residence. Mode is **not** cross-tabulated with destination | verified (separate tables) |
| 8 | Mode-specific emission factors (gCO2/pkm) | https://molit.go.kr/USR/policyTarget/m_24066/dtl.jsp?idx=89 (failed: too many redirects) ; https://www.koreascience.or.kr/article/JAKO202014264111162.pdf (opened; perception study, no factors) | — | — | — | unverified (key input) |
| 8 | Household electricity by si/gun/gu (reference) | S-KEPCO | Yes (free login) | Excel | si/gun/gu | verified (free login) |
| 8 | Si/gun/gu boundary | S-BND | Yes | SHP | si/gun/gu | verified |
| 9 | National waterworks statistics: supply by si/gun/gu, plant capacity | https://www.waternow.go.kr/ (redirects to app intro); https://www.waternow.go.kr/web/sswdStatTotal ("페이지를 찾을 수 없습니다") ; data.go.kr search "상수도통계" (only city files, e.g. https://www.data.go.kr/data/3074156/fileData.do) | — | — | City-level only (Seoul, Namyangju, Daejeon, Gyeonggi, etc.) | unavailable (no national file found) |
| 9 | Plant electricity use (kWh/m³) | Same sources; https://www.data.go.kr/catalog/15149349/fileData.json is sewage/wastewater, not water supply | — | — | — | unavailable |
| 9 | Grid emission factor | S-EF | Yes | — | National | verified |
| 9 | Population by si/gun/gu | S-POP | Yes | CSV | si/gun/gu | verified |
| 9 | Si/gun/gu boundary | S-BND | Yes | SHP | si/gun/gu | verified |
| 10 | Cattle numbers by si/gun/gu | KOSIS DT_1EO251 ; https://www.data.go.kr/data/15147310/fileData.do | Yes | KOSIS download / CSV | si/gun/gu (cattle) | verified |
| 10 | Pig and poultry numbers by si/gun/gu | KOSIS search https://kosis.kr/search/search.do?query=돼지+시군구별+사육 (0 results) | — | — | Not found below sido | unverified (optional input) |
| 10 | Manure N excretion factors | S-IPCC4 (Ch. 10) | Yes | PDF | Coefficients | verified |
| 10 | Cropland (paddy/upland) area by si/gun | KOSIS "시군별 논밭별 경지면적" (농업면적조사, 1975–2025), found via https://kosis.kr/search/search.do?query=시군별+경지면적 ; DT_1ET0033 | Yes | KOSIS download | si/gun | verified |
| 10 | Crop N requirement rates (작물별 비료사용처방기준), RDA | Not located in this phase | — | — | — | unverified |
| 10 | Si/gun/gu boundary | S-BND | Yes | SHP | si/gun/gu | verified |

## Failures and notes
- `https://www.gir.go.kr` returned an empty page twice. `http://www.gir.go.kr/home/main.do` worked, and the GIR rows above use it.
- `data.go.kr/dcat/metadata/15130913`, `/15156737` and `/15140211` timed out twice and were not retried.
- `https://www.cement.or.kr`: WebFetch failed with a TLS certificate error, and browser navigation also failed.
- `https://stat.molit.go.kr` loaded, but its search returned no usable result.
- `https://koreascience.kr/article/CFKO201132164226619.pdf` triggered a file-download dialog in the browser pane and was not opened. The search snippet citing a 2001 MOLIT car value of 150.7 gCO2/pkm therefore remains **unverified**.
- KOSIS rice, livestock, commuting and waste tables were read in the browser. The "다운로드" button was seen, but no file was actually downloaded in this phase.
- Several data.go.kr links from the search engine turned out to be different datasets from what their titles suggested:
  - 15065266 is national hourly demand.
  - 15119635 is Jeju plants only.
  - 15147320 and 15147319 are laboratory pigs and mini-pigs.
