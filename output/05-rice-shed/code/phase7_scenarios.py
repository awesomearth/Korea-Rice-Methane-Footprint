"""Phase 7 (P5) - scenarios on the Phase 5 baseline.

S1  intermittent drainage: all continuously flooded paddy (NID 2023 표 5-31) moves to multiple aeration,
    applying the IPCC 2006 Table 5.12 water-regime scaling factor (0.52 relative to continuous flooding = 1).
S2  halving household rice waste: FAO (2011) Annex 4 consumption-stage waste for cereals, Industrialized
    Asia = 20%; halved to 10%. Purchases fall to D * (1 - 0.20) / (1 - 0.10) for unchanged rice eaten.
S1+S2 combined.

Inputs : data/processed/footprint.csv (baseline), flows/LP inputs (impedance.npz, demand.csv, supply_intensity.csv),
         data/processed/ch4_factors.json, data/raw/ipcc/ipcc2006_v4c5_rice_factors.csv,
         data/raw/fao/FAO2011_global_food_losses_mb060e.pdf (+ fao2011_cereal_waste.csv transcription)
Outputs: data/processed/scenarios.csv, 07-scenarios.md
Run from output/05-rice-shed/:  python code/phase7_scenarios.py
"""
import json
import os
import re
import sys

import numpy as np
import pandas as pd
from pypdf import PdfReader

sys.path.insert(0, os.path.dirname(__file__))
from phase4_flows import solve  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
R = lambda *a: os.path.join(ROOT, *a)


def fao_waste_share():
    """Read FAO (2011) Annex 4, Industrialized Asia, Cereals, Consumption from the PDF and check the transcription."""
    tr = pd.read_csv(R("data/raw/fao/fao2011_cereal_waste.csv"))
    row = tr.iloc[0]
    txt = PdfReader(R("data/raw/fao/FAO2011_global_food_losses_mb060e.pdf")).pages[int(row.pdf_page) - 1].extract_text()
    block = txt[txt.find("FSC for Industrialized"):]
    m = re.search(r"Cereals\s+(.*?)\n", block)
    vals = re.findall(r"(\d+(?:\.\d+)?)%", m.group(1))
    found = float(vals[-1]) / 100  # last column = Consumption
    assert abs(found - row.value) < 1e-9, (found, row.value)
    return float(row.value), row, m.group(0).strip()


def main():
    fac = json.load(open(R("data/processed/ch4_factors.json")))
    ip = pd.read_csv(R("data/raw/ipcc/ipcc2006_v4c5_rice_factors.csv")).set_index("key")
    base = pd.read_csv(R("data/processed/footprint.csv"), dtype={"admin_code": str})
    z = np.load(R("data/processed/impedance.npz"), allow_pickle=True)
    s = pd.read_csv(R("data/processed/supply_intensity.csv"), dtype={"admin_code": str})
    d = pd.read_csv(R("data/processed/demand.csv"), dtype={"admin_code": str})
    assert list(base.admin_code) == list(d.admin_code)
    dist, P, D, I = z["dist_km"], s.production_t.values.astype(float), d.rice_demand_t.values.astype(float), \
        s.kgco2e_per_kg.values

    # --- S1: EF_nat with continuously flooded sub-units scaled by IPCC SFw(multiple)/SFw(continuous)
    sf_ratio = ip.loc["SFw_multiple", "value"] / ip.loc["SFw_CF", "value"]
    sub = pd.DataFrame(fac["sub_units"])
    cf = sub.sfw == "SFw_CF"
    cf_share = float(sub.loc[cf, "area_ha"].sum() / sub.area_ha.sum())
    ef_s1 = float(((sub.ef * np.where(cf, sf_ratio, 1.0)) * sub.area_ha).sum() / sub.area_ha.sum())
    k1 = ef_s1 / fac["ef_nat"]

    # --- S2: halve household waste, re-solve the LP with reduced household purchases
    w, wrow, wquote = fao_waste_share()
    dem_factor = (1 - w) / (1 - w / 2)
    res, x2 = solve(P, D * dem_factor, dist)
    assert res.status == 0
    f2 = (x2[:, :-1] * I[:, None]).sum(0)  # t CO2e per consuming unit

    f0 = base.footprint_tco2e.values
    sc = pd.DataFrame({"admin_code": base.admin_code, "name": base.name, "population": base.population,
                       "baseline_tco2e": f0, "S1_tco2e": f0 * k1, "S2_tco2e": f2, "S1S2_tco2e": f2 * k1})
    for c in ["S1", "S2", "S1S2"]:
        sc[f"{c}_pct"] = (sc[f"{c}_tco2e"] / sc.baseline_tco2e - 1) * 100
    sc.to_csv(R("data/processed/scenarios.csv"), index=False, encoding="utf-8")

    b_kt = f0.sum() / 1000
    nat_prod_kt = fac["national_kt_co2e"]
    rows = []
    defs = {
        "S1": ("Intermittent drainage", f"all continuously flooded paddy, {cf_share:.1%} of paddy area (NID 2023 표 5-31, "
               f"PDF p. 289), moves to multiple aeration; SFw multiplied by {sf_ratio:.2f} = IPCC Table 5.12 multiple "
               f"aeration 0.52 ÷ continuous 1 (p. 5.49). National EF_nat {fac['ef_nat']:.4f} → {ef_s1:.4f} kg CH4/ha/d."),
        "S2": ("Halve household rice waste", f"household waste share {w:.0%} → {w/2:.0%} (FAO 2011, Annex 4, Industrialized Asia, "
               f"Cereals, Consumption = {w:.0%}; report p. {wrow.report_page}, PDF p. {wrow.pdf_page}). Purchases × "
               f"(1−{w:.2f})/(1−{w/2:.2f}) = {dem_factor:.4f} for unchanged rice eaten; LP re-solved, released rice goes to SLACK."),
        "S1S2": ("Combined", "S1 intensities applied to the S2 flows."),
    }
    for c, (name, assump) in defs.items():
        kt = sc[f"{c}_tco2e"].sum() / 1000
        pct = sc[f"{c}_pct"]
        rows.append(f"| {c}: {name} | {assump} | {kt:,.1f} | {(kt / b_kt - 1) * 100:+.2f}% | {pct.min():+.2f}% to {pct.max():+.2f}% |")
    nat_s1 = nat_prod_kt * k1
    md = f"""# 07 — Scenarios (Idea 2, Phase 7 / P5)

Generated by `code/phase7_scenarios.py`. Output: `data/processed/scenarios.csv` (per unit: footprint and % change under each scenario).

- **Baseline:** Phase 5 (`data/processed/footprint.csv`), the household rice-shed footprint summed over the 252 consuming units: **{b_kt:,.1f} kt CO2e**.
- **Metric:** "National kt CO2e" below is that same household-footprint sum under each scenario.

| Scenario | Assumption (numeric) and source | National kt CO2e | % change vs baseline | Range of % change across units |
|---|---|---|---|---|
| Baseline (Phase 5) | 2025 flows (Phase 4), Tier 2 NID intensities (Phase 3) | {b_kt:,.1f} | — | — |
{chr(10).join(rows)}

**Production-side view.** S1 also lowers national paddy CH4 (production basis) from {nat_prod_kt:,.1f} to {nat_s1:,.1f} kt CO2e ({(k1 - 1) * 100:+.2f}%). S2 lowers household footprints only: the rice no longer bought by households moves to the non-household slack in the LP, so national paddy CH4 falls only if production itself falls (cf. the paper's export-rebound caveat, `01-method-summary.md` §4).

**Why the S1 range across units is zero.** Water regime is set nationally (`03-supply-intensity.md`), so S1 scales every producer's intensity by the same factor ({k1:.4f}). Every unit changes by the same percentage. A spatially targeted drainage scenario would need water-regime data by si/gun, which Idea 2 does not have.

**Why S2 varies across units.** S2 re-solves the LP with smaller demand. Each unit's purchases fall by the same {(1 - dem_factor) * 100:.2f}%, but the LP re-sources, and the released supply comes off the most distant producers first. Units served by high-intensity producers that drop out gain or lose more than the uniform cut.

**Transcription check.** The FAO line read from the PDF by the script is "{wquote}"; the last column (Consumption) equals the transcribed {w:.0%}.

## Assumption notes
- **S2 assumes DT_1ED0001 includes household waste.** It treats the per capita consumption in DT_1ED0001 as household acquisition, including household waste. If the survey already measures rice eaten, S2 would instead lower the waste share on top of it, and the demand change would be reported differently.
- **The FAO share is regional, not Korean.** The 20% is FAO's regional default for cereals in Industrialized Asia (Japan, China, Republic of Korea), not a Korean rice-specific measurement.
- **S1 uses the IPCC default ratio.** S1 applies IPCC's default multiple-aeration factor relative to continuous flooding (0.52), as the scenario specification requires. The NID's own ≥ 2× aeration factor is 0.49 (NID 표 5-28); using it would give a slightly larger reduction.

## Done criterion
- Every scenario row states its numeric assumption and source: **MET**.
- Every scenario is compared with the baseline (% change column): **MET**.
"""
    open(R("07-scenarios.md"), "w", encoding="utf-8").write(md)
    print(f"cf_share={cf_share:.4f} k1={k1:.4f} w={w} dem_factor={dem_factor:.4f} base={b_kt:.1f} "
          f"S1={sc.S1_tco2e.sum()/1000:.1f} S2={sc.S2_tco2e.sum()/1000:.1f} S1S2={sc.S1S2_tco2e.sum()/1000:.1f} "
          f"S2 range {sc.S2_pct.min():.2f}..{sc.S2_pct.max():.2f}")


if __name__ == "__main__":
    main()
