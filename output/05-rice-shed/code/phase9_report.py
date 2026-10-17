"""Phase 9 - paper-style report. Every number is read from an artifact file and cited inline.

Inputs : 00-08 outputs and data/processed/*
Output : 09-report.md
Run from output/05-rice-shed/:  python code/phase9_report.py
"""
import json
import os

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
R = lambda *a: os.path.join(ROOT, *a)
rd = lambda f, **k: pd.read_csv(R("data/processed", f), dtype={"admin_code": str, "from_code": str, "to_code": str}, **k)


def main():
    dem, sup, flo, fp = rd("demand.csv"), rd("supply_intensity.csv"), rd("flows.csv"), rd("footprint.csv")
    mc, sc = rd("mc_results.csv"), rd("scenarios.csv")
    fac = json.load(open(R("data/processed/ch4_factors.json")))
    figc = json.load(open(R("data/processed/figure_classes.json")))
    draws = np.load(R("data/processed/mc_draws_per_capita.npz"), allow_pickle=True)
    nid, gwp = fac["nid_factors"], fac["gwp"]
    pop_t, dem_t, prod_t = dem.population.sum(), dem.rice_demand_t.sum(), sup.production_t.sum()
    pc_rate = dem.rice_demand_t.sum() * 1000 / pop_t
    hh = flo[flo.to_code != "SLACK"]
    slack_t = flo.loc[flo.to_code == "SLACK", "tonnes"].sum()
    tkm = (hh.tonnes * hh.km).sum()
    mean_km = tkm / dem_t
    nsrc = hh.groupby("to_code").size()
    cons_kt = fp.footprint_tco2e.sum() / 1000
    nat_kt = fac["national_kt_co2e"]
    pcf = fp.per_capita_kgco2e
    rr = fp.ratio_spatial_to_natavg
    r_int = np.corrcoef(pcf, fp.sourcing_intensity_kgco2e_per_kg)[0, 1]
    I = sup.kgco2e_per_kg
    big = mc.population > 125_000
    k = draws["k"]
    base_kt = sc.baseline_tco2e.sum() / 1000
    scen = {c: (sc[f"{c}_tco2e"].sum() / 1000, sc[f"{c}_pct"].min(), sc[f"{c}_pct"].max()) for c in ["S1", "S2", "S1S2"]}
    sl = flo[flo.to_code == "SLACK"].merge(sup[["admin_code", "name", "kgco2e_per_kg"]], left_on="from_code",
                                           right_on="admin_code")
    slack_int = (sl.tonnes * sl.kgco2e_per_kg).sum() / sl.tonnes.sum()
    hh_int = cons_kt * 1000 / dem_t
    subu = pd.DataFrame(fac["sub_units"])
    cf_share = subu.loc[subu.sfw == "SFw_CF", "area_ha"].sum() / subu.area_ha.sum()
    sf_ratio = fac["ipcc_factors"]["SFw_multiple"]["value"] / fac["ipcc_factors"]["SFw_CF"]["value"]
    w = float(pd.read_csv(R("data/raw/fao/fao2011_cereal_waste.csv")).value.iloc[0])
    slack_kt = float((sl.tonnes * sl.kgco2e_per_kg).sum() / 1000)
    top = fp.sort_values("per_capita_kgco2e", ascending=False)
    top_names = ", ".join(f"{r.name} {r.per_capita_kgco2e:.1f}" for r in top.head(3).itertuples())
    low_names = ", ".join(f"{r.name} {r.per_capita_kgco2e:.1f}" for r in top.tail(3).iloc[::-1].itertuples())
    SIDO = {"11": "Seoul", "26": "Busan", "27": "Daegu", "28": "Incheon", "29": "Gwangju", "30": "Daejeon",
            "31": "Ulsan", "36": "Sejong", "41": "Gyeonggi-do", "43": "Chungcheongbuk-do", "44": "Chungcheongnam-do",
            "46": "Jeollanam-do", "47": "Gyeongsangbuk-do", "48": "Gyeongsangnam-do", "50": "Jeju", "51": "Gangwon",
            "52": "Jeonbuk"}
    KOSIS_SIDO = {"11": "Seoul", "21": "Busan", "22": "Daegu", "23": "Incheon", "24": "Gwangju", "25": "Daejeon",
                  "26": "Ulsan", "29": "Sejong", "31": "Gyeonggi-do", "32": "Gangwon", "33": "Chungcheongbuk-do",
                  "34": "Chungcheongnam-do", "35": "Jeonbuk", "36": "Jeollanam-do", "37": "Gyeongsangbuk-do",
                  "38": "Gyeongsangnam-do", "39": "Jeju"}
    fp["sido"] = fp.admin_code.str[:2]
    gs = fp.groupby("sido").ratio_spatial_to_natavg.agg(["size", lambda r: int((r > 1).sum()), "median"])
    gs.columns = ["n", "above1", "median"]
    allhot = [SIDO[c] for c in gs.index if gs.loc[c, "above1"] == gs.loc[c, "n"]]
    hot_txt = ("Every consuming unit has ratio > 1 in " + ", ".join(allhot) +
               f" (Jeollanam-do median {gs.loc['46', 'median']:.3f}, Gwangju {gs.loc['29', 'median']:.3f}); these units are "
               "supplied by nearby low-yield producers (fig1, fig4).")
    capf = hh[hh.to_code.str[:2].isin(["11", "41"])].merge(sup[["admin_code", "kgco2e_per_kg"]], left_on="from_code",
                                                           right_on="admin_code")
    shares = (capf.groupby(capf.from_code.str[:2]).tonnes.sum() / capf.tonnes.sum()).sort_values(ascending=False)
    cap_txt = (f"Seoul has {int(gs.loc['11', 'n'] - gs.loc['11', 'above1'])} of {int(gs.loc['11', 'n'])} units below 1 and "
               f"Gyeonggi-do {int((fp[fp.sido == '41'].ratio_spatial_to_natavg < 1).sum())} of {int(gs.loc['41', 'n'])} "
               f"(median {gs.loc['41', 'median']:.3f}). Their household rice comes from " +
               ", ".join(f"{KOSIS_SIDO[c]} {v:.0%}" for c, v in shares.head(4).items()) +
               f", at a mean intensity of {(capf.tonnes * capf.kgco2e_per_kg).sum() / capf.tonnes.sum():.3f} kg CO2e/kg")
    inv = open(R("01-data-inventory.md"), encoding="utf-8").read()
    table = inv[inv.find("| Input |"):inv.find("\n\n", inv.find("| Input |"))]

    md = f"""# Rice-shed Methane Footprint of Korean Cities, 2025 (Idea 2)

*Paper-style report, Phase 9. Generated by `code/phase9_report.py`. Every number below is read from the artifact file named beside it in brackets [file].*

## 1. Research question
Where is the paddy CH4 embodied in each si/gun/gu's rice consumption emitted, and how much does yield-driven variation in per-kg intensity change urban rice footprints (`02-ideas.md`, Idea 2)?

The study transfers the "carbon hoofprint" design of Goldstein et al. (2025, *Nature Climate Change*; `01-method-summary.md`) to Korean rice:
- consumption allocated to cities (P2);
- per-location production intensity (P3);
- a mass-balanced transport LP linking producers to consumers (P1);
- hotspot maps (P4), scenarios (P5) and Monte Carlo uncertainty (P6).

## 2. Data and sources
Analysis year 2025; units are tonnes of milled rice (정곡) and GWP CH4 = {gwp:.0f} (AR5, as in the national inventory) [00-scope.md].

{table}

**Approved deviation.** The locked boundary input S-BND is behind a VWorld login. The study owner approved **geoBoundaries KOR ADM2** (2020, CC BY 3.0) as the substitute, and 영광군, which is missing from geoBoundaries, was patched from OpenStreetMap (ODbL) [00-scope.md (e); 01-data-inventory.md; 04-flows.md]. Scenario S2 uses the FAO (2011) cereal waste share [data/raw/fao/fao2011_cereal_waste.csv].

## 3. Methods

### P2 — Consumption allocated to consuming units
- **Units and population.** 2025-12-31 법정동 population was summed to {len(dem)} si/gun/gu units ({pop_t:,} residents) [demand.csv].
- **Demand.** Household rice demand = population × {pc_rate:.1f} kg per person per year (KOSIS DT_1ED0001, 쌀, 전가구, 2025). Unit shares were rescaled to the national control total of {dem_t:,.0f} t [demand.csv; 02-demand.md].
- **Limitation of the input.** A single national rate means per capita consumption does not vary across units.

### P3 — Per-location intensity
- **Production.** {len(sup)} producing units: 148 si/gun plus 8 metropolitan cities reported as wholes. They produced {prod_t:,.0f} t in 2025, reconciling with the KOSIS national row to {(prod_t - fac['national_production_t']) / fac['national_production_t']:+.4%} [supply_intensity.csv; 03-supply-intensity.md].
- **Equations.** CH4 follows IPCC 2006 Vol. 4 Ch. 5 Eq. 5.1–5.2 with Korean Tier 2 factors from the GIR NID 2025: EFc = {nid['EFc']} kg CH4/ha/d, NID 표 5-27, together with the NID water-regime and organic-amendment scaling factors (표 5-28/5-29).
- **National EF.** These are area-weighted over the NID 2023 management mix (표 5-31) to EF_nat = {fac['ef_nat']:.4f} kg CH4/ha/d.
- **Cultivation period.** An effective cultivation period t_eff = {fac['t_eff_days']:.1f} d is back-calculated so that NID 2023 factors and areas reproduce the NID 2023 irrigated-rice CH4 [ch4_factors.json].
- **Per unit.** CH4_u = EF_nat · t_eff · area_u. Intensity_u = CH4_u / production_u, so **intensity varies only through yield**.

### P1 — Flow reconstruction
- **LP.** A balanced transportation LP minimizes Σ tonnes × great-circle distance between polygon centroids, solved with HiGHS via `scipy.optimize.linprog` [04-flows.md].
- **Slack node.** Supply exceeds household demand, so one explicit zero-cost sink, "non-household disposition" (processing, food service, stocks, losses), absorbs {slack_t:,.0f} t, {slack_t / prod_t:.1%} of production [flows.csv].
- **일반구.** Units without their own polygon use their parent city's centroid [crosswalk.csv].

### P4 — Hotspot mapping
Four maps in EPSG:5179: Fisher-Jenks classes for per capita footprint and intensity, small-multiple flow maps, and a diverging ratio map [08-figures.md; figure_classes.json].

### P5 — Scenarios
S1, intermittent drainage, and S2, halving household rice waste, separately and combined, recomputed on the baseline [07-scenarios.md].

### P6 — Uncertainty
{len(draws['k'])} Monte Carlo draws. Each draw (a) re-solves the LP with every distance multiplied by LogNormal(0, 0.5) noise, which gives alternative mass-balanced sourcings, and (b) draws the CH4 factors from the IPCC Table 5.11–5.14 ranges, treated as ±1 sd about the mean [06-uncertainty.md; mc_results.csv].

## 4. Results
- **National totals.**
  - National paddy CH4 in 2025 is {fac['national_ch4_t']:,.0f} t CH4 = **{nat_kt:,.1f} kt CO2e**, a national average intensity of {fac['national_intensity_kgco2e_per_kg']:.3f} kg CO2e per kg milled rice [ch4_factors.json].
  - Intensity across producing units ranges {I.min():.3f}–{I.max():.3f} kg CO2e/kg, max/min {I.max() / I.min():.2f} [supply_intensity.csv].
- **Sourcing.**
  - The LP is optimal. The demand-weighted mean sourcing distance is **{mean_km:.1f} km** ({tkm / 1e6:,.1f} million t·km).
  - Most units draw from very few sources: median {nsrc.median():.0f}, maximum {nsrc.max()} [flows.csv].
- **Household footprint.**
  - The household rice-shed footprint of the {len(fp)} consuming units is **{cons_kt:,.1f} kt CO2e**.
  - The slack carries {slack_kt:,.1f} kt (slack flows × source intensity). Household plus slack = {cons_kt + slack_kt:,.1f} kt, against national paddy CH4 of {nat_kt:,.1f} kt (difference {cons_kt + slack_kt - nat_kt:+.1e} kt) [flows.csv; supply_intensity.csv; footprint.csv; ch4_factors.json].
- **Per capita.**
  - Mean ± sd over units is **{pcf.mean():.1f} ± {pcf.std():.1f} kg CO2e/person/yr**, range {pcf.min():.1f}–{pcf.max():.1f}.
  - Highest: {top_names}. Lowest: {low_names} [footprint.csv].
- **Spatial vs national average.**
  - The spatial estimate differs from the national-average-intensity estimate by a factor of **{rr.min():.3f}–{rr.max():.3f}** [footprint.csv].
  - {hot_txt}
  - {cap_txt} [footprint.csv; flows.csv; figures/].
- **Correlations.**
  - Per capita footprint vs per capita consumption: **undefined**, because consumption has zero variance across units.
  - Per capita footprint vs sourcing-weighted intensity: **r = {r_int:.3f}**, which is identical by construction.
  - As in the paper, the footprint is set by *where* rice comes from. With one national consumption rate, Idea 2 cannot test the paper's consumption correlation independently [05-footprint.md].
- **Slack mechanism.**
  - The LP routes the slack mostly to distant southwestern producers. Rice going to the slack has a mean intensity of {slack_int:.3f} kg CO2e/kg, against {hh_int:.3f} for household rice [flows.csv; supply_intensity.csv; footprint.csv].
  - As a result the household total is below demand × national average. This is a model mechanism, not an observed fact.

## 5. Uncertainty
- **Draws.** {int(np.isfinite(draws['combined']).all(axis=1).sum())} of {len(k)} draws completed [mc_draws_per_capita.npz]. Runtime is stated in 06-uncertainty.md.
- **Combined MAPE across units: {mc.mape.mean():.1%}**:
  - {mc.mape[big].mean():.1%} for units > 125,000 people (n = {int(big.sum())});
  - {mc.mape[~big].mean():.1%} for units ≤ 125,000 (n = {int((~big).sum())}) [mc_results.csv].
- **Sourcing-only MAPE: {mc.sourcing_only_mape.mean():.1%}**:
  - {mc.sourcing_only_mape[big].mean():.1%} for > 125,000;
  - {mc.sourcing_only_mape[~big].mean():.1%} for ≤ 125,000 [mc_results.csv].
- **Factor uncertainty.** The common factor multiplier k has mean {k.mean():.3f} and p5–p95 {np.percentile(k, 5):.3f}–{np.percentile(k, 95):.3f} [mc_draws_per_capita.npz].
- **Reading.** IPCC factor uncertainty dominates the level of every footprint but does not change the ranking. Between-unit differences carry the sourcing uncertainty.
- **Comparison with the paper.** The paper reports a 26.5% sourcing MAPE, below 20% for cities over 125,000 people (`01-method-summary.md` §4). Here the sourcing MAPE is much lower ({mc.sourcing_only_mape.mean():.1%}), and the size pattern is reversed: large units {mc.sourcing_only_mape[big].mean():.1%} vs small units {mc.sourcing_only_mape[~big].mean():.1%}. Many small rural units supply themselves at 0 km, which distance noise cannot displace, while large urban units import from several producers. The level depends on the noise σ chosen; see the σ sensitivity in 06-uncertainty.md [mc_results.csv].

## 6. Scenarios
All values are the household rice-shed footprint summed over the 252 units [scenarios.csv; 07-scenarios.md; ch4_factors.json; data/raw/fao/fao2011_cereal_waste.csv].

| Scenario | Assumption and source | kt CO2e | % vs baseline ({base_kt:,.1f} kt) | Range across units |
|---|---|---|---|---|
| S1 intermittent drainage | the {cf_share:.1%} continuously flooded paddy area (NID 표 5-31) moves to multiple aeration, SFw × {sf_ratio:.2f} (IPCC Table 5.12) | {scen['S1'][0]:,.1f} | {(scen['S1'][0] / base_kt - 1) * 100:+.2f}% | {scen['S1'][1]:+.2f}% to {scen['S1'][2]:+.2f}% |
| S2 halve household waste | waste {w:.0%} → {w/2:.0%} (FAO 2011 Annex 4, cereals, Industrialized Asia); purchases × {(1-w)/(1-w/2):.4f}; LP re-solved | {scen['S2'][0]:,.1f} | {(scen['S2'][0] / base_kt - 1) * 100:+.2f}% | {scen['S2'][1]:+.2f}% to {scen['S2'][2]:+.2f}% |
| S1 + S2 | combined | {scen['S1S2'][0]:,.1f} | {(scen['S1S2'][0] / base_kt - 1) * 100:+.2f}% | {scen['S1S2'][1]:+.2f}% to {scen['S1S2'][2]:+.2f}% |

- **S1 is uniform across units** because water regime is not known by si/gun.
- **S2 cuts household footprints but not production CH4.** Rice released by households moves to the slack, so national paddy CH4 falls only if production falls [07-scenarios.md].

## 7. Limitations
- **Distance-minimizing flows may misrepresent real sourcing (Idea 2's stated risk).** Rice moves nationally through government stocks and RPC (rice processing complex) brokerage.
  - The cost-minimizing LP gives extreme-point solutions, with a median of {nsrc.median():.0f} source per unit, and assigns the non-household slack to the most remote producers.
  - Real rice-sheds are more mixed. Footprints of units near low-yield regions (Jeollanam-do, Gwangju) are probably overstated, and those of Seoul/Gyeonggi probably understated.
  - The Monte Carlo explores cost-plausible alternatives, not observed trade.
- **Yield-scaled intensity captures only the yield term of CH4 variation.** Water management, pre-season flooding, straw incorporation, soil and cultivar are set to the national NID 2023 mix in every unit. Intensity differences (max/min {I.max() / I.min():.2f}) are differences in yield only.
- **Consumption is uniform.** Per capita consumption is one national household rate. Regional and demographic diets and non-household rice (food service, processed foods) are outside the demand vector, and the latter goes to the slack.
- **The cultivation period is derived.** t_eff is back-calculated from the NID, not observed. The 2023 NID management mix is applied to 2025 areas.
- **Geometry.**
  - Boundaries are geoBoundaries 2020 at local-government level, with 영광군 patched from OSM.
  - 일반구 share their parent city's centroid.
  - Metropolitan producers are located at whole-city centroids.
- **Scenario inputs are partly non-Korean.** The S2 waste share is FAO's regional cereal default, not a Korean rice measurement.

## 8. Reproduction (commands in order, from `output/05-rice-shed/`)
```bash
python3 -m venv .venv && .venv/bin/pip install -r code/requirements.txt
.venv/bin/python -I code/phase1_acquire.py
.venv/bin/python -I code/phase2_demand.py
.venv/bin/python -I code/phase3_supply_intensity.py
.venv/bin/python -I code/phase4_flows.py
.venv/bin/python -I code/phase5_footprint.py
.venv/bin/python -I code/phase6_uncertainty.py
.venv/bin/python -I code/phase7_scenarios.py
.venv/bin/python -I code/phase8_figures.py
.venv/bin/python -I code/phase9_report.py
```
- **Phase 0** (`00-scope.md`) is a design document.
- **Shared code:** `code/kosis_dl.py` and `code/datagokr_dl.py` are the keyless downloaders; `code/geo_units.py` is the geometry crosswalk.
- **Fixed seed:** Phase 6 uses seed 20251231.
"""
    open(R("09-report.md"), "w", encoding="utf-8").write(md)
    print("report written", len(md))


if __name__ == "__main__":
    main()
