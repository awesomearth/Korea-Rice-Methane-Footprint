"""Phase 3 (P3) - rice production by producing unit and per-location CH4 intensity, 2025.

Inputs : data/raw/kosis/DT_1ET0034.csv, data/raw/kosis/DT_1ET0033.csv,
         data/raw/gir/NID2025_ko.pdf (+ transcriptions nid2025_rice_factors.csv, nid2025_rice_area_2023.csv),
         data/raw/ipcc/V4_05_Ch5_Cropland.pdf (+ transcription ipcc2006_v4c5_rice_factors.csv)
Outputs: data/processed/supply_intensity.csv, data/processed/ch4_factors.json, 03-supply-intensity.md
Run from output/05-rice-shed/:  python code/phase3_supply_intensity.py

Method (IPCC 2006 Vol.4 Ch.5 Eq. 5.1, 5.2; Korean Tier 2 factors from the GIR NID 2025):
  EF_i  = EFc * SFw * SFp * SFo                     (Eq. 5.2; NID 표 5-26..5-29)
  EF_nat = sum_i EF_i A_i / sum_i A_i                (NID 2023 irrigated-area mix, 표 5-31)
  t_eff  = CH4_irrigated_2023 / sum_i EF_i A_i       (back-calculated from NID 표 5-24; see md)
  CH4_u  = EF_nat * t_eff * A_u                       (Eq. 5.1 per producing unit, 2025 KOSIS area)
  I_u    = CH4_u / P_u = EF_nat * t_eff / Y_u         (kg CH4 per kg milled rice)
"""
import json
import os
import re

import numpy as np
import pandas as pd
from pypdf import PdfReader

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
YEAR = "2025"
METRO = ["11", "21", "22", "23", "24", "25", "26", "29"]  # KOSIS sido codes reported only as a whole


def norm(s):
    return re.sub(r"[\s‧･·\-–]", "", s)


def verify_transcription(pdf, rows, page_col, label_col):
    """Every transcribed value must appear on the cited PDF page (whitespace-insensitive)."""
    reader = PdfReader(pdf)
    cache, bad = {}, []
    for _, r in rows.iterrows():
        pg = int(r[page_col])
        if pg not in cache:
            cache[pg] = norm(reader.pages[pg - 1].extract_text() or "")
        v = r["value"]
        sv = f"{v:g}" if isinstance(v, float) else str(v)
        cands = {sv, f"{float(v):.2f}", f"{float(v):,.0f}", f"{float(v):.1f}"}
        if not any(norm(c) in cache[pg] for c in cands):
            bad.append((r["key"], sv, pg))
    return bad


def read_kosis(tbl):
    raw = pd.read_csv(os.path.join(ROOT, f"data/raw/kosis/{tbl}.csv"), encoding="utf-8-sig", header=None, dtype=str)
    years, items = raw.iloc[0], raw.iloc[1]
    body = raw.iloc[2:].reset_index(drop=True)
    return years, items, body


def production_table():
    years, items, b = read_kosis("DT_1ET0034")
    col = {it.split()[0]: i for i, (y, it) in enumerate(zip(years, items)) if str(y).startswith(f"Y{YEAR}")}
    df = pd.DataFrame({
        "sido": b[0], "unit": b[1],
        "paddy_area_ha": pd.to_numeric(b[col["T10"]], errors="coerce"),
        "yield_kg_10a": pd.to_numeric(b[col["T20"]], errors="coerce"),
        "production_t": pd.to_numeric(b[col["T30"]], errors="coerce")})
    df["sido_code"] = df["sido"].str.split().str[0]
    nat = df[(df.sido_code == "00")].iloc[0]
    si = df[(df.unit != "소계") & (df.sido_code != "00")].copy()
    si["admin_code"] = si["unit"].str.split().str[0]
    si["name"] = si["sido"].str.split(n=1).str[1] + " " + si["unit"].str.split(n=1).str[1]
    me = df[(df.unit == "소계") & df.sido_code.isin(METRO)].copy()
    me["admin_code"] = me["sido_code"]
    me["name"] = me["sido"].str.split(n=1).str[1]
    units = pd.concat([me, si])
    return nat, units, si


def area_table_33():
    years, items, b = read_kosis("DT_1ET0033")
    c = [i for i, (y, it) in enumerate(zip(years, items)) if str(y).startswith(f"Y{YEAR}") and it.startswith("T10")][0]
    nat = b[b[0].str.startswith("00 ")]
    return float(nat.iloc[0, c])


def main():
    nidf = pd.read_csv(os.path.join(ROOT, "data/raw/gir/nid2025_rice_factors.csv"))
    ipf = pd.read_csv(os.path.join(ROOT, "data/raw/ipcc/ipcc2006_v4c5_rice_factors.csv"))
    area = pd.read_csv(os.path.join(ROOT, "data/raw/gir/nid2025_rice_area_2023.csv"))
    bad_nid = verify_transcription(os.path.join(ROOT, "data/raw/gir/NID2025_ko.pdf"), nidf, "pdf_page", "quoted_label")
    ipf_pages = ipf.assign(pdf_page=ipf["ipcc_page"].map(lambda s: int(str(s).split(".")[1])))
    bad_ipcc = verify_transcription(os.path.join(ROOT, "data/raw/ipcc/V4_05_Ch5_Cropland.pdf"), ipf_pages,
                                    "pdf_page", "quoted_label")
    # NID 표 5-31 area check (PDF p. 289): totals 413.7 (none) and 731.8 (all)
    f = dict(zip(nidf.key, nidf.value))

    # --- adjusted daily EF per NID sub-unit (Eq. 5.2) and national area-weighted EF
    rows = []
    for r in area.itertuples():
        for om, a in [("none", r.area_none_kha), ("straw", r.area_straw_kha), ("green", r.area_green_kha)]:
            sfo = {"none": 1.0, "straw": f["SFo_straw"], "green": f["SFo_green"]}[om]
            ef = f["EFc"] * f[r.sfw_class] * f[r.sfp_class] * sfo
            rows.append(dict(sfw=r.sfw_class, sfp=r.sfp_class, om=om, area_ha=a * 1000, ef=ef))
    sub = pd.DataFrame(rows)
    sum_efa = float((sub.ef * sub.area_ha).sum())  # kg CH4 / day
    a_tot = float(sub.area_ha.sum())
    ef_nat = sum_efa / a_tot
    ch4_irr_2023_kg = f["CH4_irrigated_2023"] * 1e6 / f["GWP_CH4"]  # kt CO2e -> kg CH4
    t_eff = ch4_irr_2023_kg / sum_efa  # days
    gwp = f["GWP_CH4"]

    # --- production and per-location intensity
    nat, units, si = production_table()
    units = units[units.production_t > 0].copy()
    units["yield_t_ha"] = units["yield_kg_10a"] / 100.0
    units["yield_implied_t_ha"] = units["production_t"] / units["paddy_area_ha"]
    units["ch4_t"] = ef_nat * t_eff * units["paddy_area_ha"] / 1000.0
    units["kgch4_per_kg"] = units["ch4_t"] / units["production_t"]
    units["kgco2e_per_kg"] = units["kgch4_per_kg"] * gwp
    out = units[["admin_code", "name", "paddy_area_ha", "production_t", "yield_kg_10a", "ch4_t", "kgco2e_per_kg",
                 "kgch4_per_kg", "yield_implied_t_ha"]].rename(columns={"yield_kg_10a": "yield"})
    out.to_csv(os.path.join(ROOT, "data/processed/supply_intensity.csv"), index=False, encoding="utf-8")

    sum_prod = float(out.production_t.sum())
    nat_prod = float(nat.production_t)
    recon = (sum_prod - nat_prod) / nat_prod
    sum_area = float(out.paddy_area_ha.sum())
    area33 = area_table_33()
    ch4_nat_t = float(out.ch4_t.sum())
    ch4_nat_kt_co2e = ch4_nat_t * gwp / 1000.0
    nat_int = ch4_nat_t / nat_prod * gwp
    q = out.kgco2e_per_kg
    imin, imed, imax = q.min(), q.median(), q.max()
    lo, hi = out.loc[q.idxmin()], out.loc[q.idxmax()]

    # Tier 1 IPCC default sensitivity (not used downstream): same NID area mix, IPCC default factors.
    ip = dict(zip(ipf.key, ipf.value))
    map_w = {"SFw_CF": "SFw_CF", "SFw_1x_lt1wk": "SFw_single", "SFw_1x_1to2wk": "SFw_single", "SFw_2x": "SFw_multiple"}
    t1 = {}
    for timing, cf in [("straw shortly before", ip["CFOA_straw_short"]), ("straw long before", ip["CFOA_straw_long"])]:
        sfo_s = (1 + f["ROA_straw"] * cf) ** ip["SFo_exponent"]
        sfo_g = (1 + f["ROA_green"] * ip["CFOA_green"]) ** ip["SFo_exponent"]
        e = sub.apply(lambda r: ip["EFc"] * ip[map_w[r.sfw]] * ip[r.sfp] *
                      {"none": 1.0, "straw": sfo_s, "green": sfo_g}[r.om], axis=1)
        efn = float((e * sub.area_ha).sum() / a_tot)
        t1[timing] = dict(ef_nat=efn, sfo_straw=sfo_s, intensity_nat=efn * t_eff * float(out.paddy_area_ha.sum()) /
                          1000 / nat_prod * gwp)

    factors = dict(EFc=f["EFc"], ef_nat=ef_nat, t_eff_days=t_eff, gwp=gwp, area_nid_ha=a_tot, sum_efa_kg_day=sum_efa,
                   ch4_irr_2023_kg=ch4_irr_2023_kg, national_ch4_t=ch4_nat_t, national_kt_co2e=ch4_nat_kt_co2e,
                   national_intensity_kgco2e_per_kg=nat_int, national_production_t=nat_prod,
                   sub_units=sub.to_dict("records"), tier1_sensitivity=t1,
                   nid_factors=f, ipcc_factors=ipf.set_index("key")[["value", "low", "high"]].to_dict("index"))
    json.dump(factors, open(os.path.join(ROOT, "data/processed/ch4_factors.json"), "w"), indent=1, ensure_ascii=False)

    # check NID 표 5-26 rounded EFs against recomputed values
    t526 = {("SFw_CF", "SFp_lt180", "none"): 2.32, ("SFw_CF", "SFp_lt180", "straw"): 5.80,
            ("SFw_2x", "SFp_lt180", "none"): 1.14, ("SFw_2x", "SFp_fl30", "straw"): 3.10,
            ("SFw_1x_1to2wk", "SFp_gt180", "green"): 1.28}
    t526_ok = all(abs(sub[(sub.sfw == k[0]) & (sub.sfp == k[1]) & (sub.om == k[2])].ef.iloc[0] - v) < 0.006
                  for k, v in t526.items())

    dev = out["yield_implied_t_ha"] * 100 / out["yield"] - 1
    done = abs(recon) <= 0.01 and not bad_nid and not bad_ipcc
    top = out.sort_values("kgco2e_per_kg")
    row = lambda r: (f"| {r['admin_code']} | {r['name']} | {r.paddy_area_ha:,.0f} | {r.production_t:,.0f} | "
                     f"{r['yield']:.0f} | {r.ch4_t:,.1f} | {r.kgco2e_per_kg:.4f} |")
    th = "| admin_code | name | paddy_area_ha | production_t | yield (kg/10a) | ch4_t | kgco2e_per_kg |\n|---|---|---|---|---|---|---|"
    md = f"""# 03 — Supply Side and Per-location Intensity (Idea 2, Phase 3 / P3)

Generated by `code/phase3_supply_intensity.py`.
- **Inputs:** `data/raw/kosis/DT_1ET0034.csv` and `DT_1ET0033.csv` (2025 column); the NID 2025 rice section (`data/raw/gir/NID2025_ko.pdf`); IPCC 2006 Vol. 4 Ch. 5 (`data/raw/ipcc/V4_05_Ch5_Cropland.pdf`).
- **Outputs:** `data/processed/supply_intensity.csv`, `data/processed/ch4_factors.json`.

## Producing units and reconciliation
| Check | Value |
|---|---|
| Producing units with 2025 production > 0 | {len(out)} ({int(out.admin_code.isin(METRO).sum())} metropolitan/special cities + {int((~out.admin_code.isin(METRO)).sum())} si/gun) |
| Σ unit production, 2025 | {sum_prod:,.0f} t milled rice |
| KOSIS national row (전국), 2025 | {nat_prod:,.0f} t |
| Relative difference | {recon:+.4%} |
| Σ unit paddy area vs DT_1ET0034 national | {sum_area:,.0f} ha vs {float(nat.paddy_area_ha):,.0f} ha |
| DT_1ET0033 national paddy area, 2025 (cross-check) | {area33:,.0f} ha |

## CH4 method
- **Equation.** IPCC 2006 Vol. 4 Ch. 5 **Eq. 5.1** (p. 5.45): CH4 = Σ EF_i · t_i · A_i · 10⁻⁶. The adjusted daily factor is **Eq. 5.2** (p. 5.48): EF_i = EFc · SFw · SFp · SFo.
- **Factors.** Tier 2 Korean factors from the GIR NID 2025, which applies the same IPCC equations (NID PDF p. 285 cites "2006 IPCC GL, Vol.4, Ch.5, Equation 5.1 / 5.2"). The IPCC defaults (Tier 1) are recorded below; they supply the uncertainty ranges for Phase 6 and a sensitivity.
- **National mean EF.** Water regime and organic amendment are not published by si/gun, so every producing unit gets the **national area-weighted EF_nat**. It is built from the NID 2023 irrigated-area mix (12 water-regime cells × 3 amendment classes, NID 표 5-31, PDF p. 289).
- **Cultivation period.** The NID gives no explicit day count. An **effective cultivation period t_eff** is therefore back-calculated so that the NID's own 2023 factors and areas reproduce the NID's 2023 irrigated-rice CH4:
  t_eff = (6,869 kt CO2e ÷ 28) ÷ Σ EF_i·A_i.
  This is a derived quantity, not an observed season length.
- **Per-unit CH4 and intensity.** CH4_u = EF_nat · t_eff · A_u, using 2025 KOSIS paddy area. Intensity_u = CH4_u / P_u = EF_nat · t_eff / Yield_u.
  **Only yield varies across units**, which is Idea 2's stated design ("yield-scaled intensity").

### Factor table
| Symbol | Value | Source | Page |
|---|---|---|---|
| Eq. 5.1 (emissions) | Σ EF·t·A·10⁻⁶ | IPCC 2006 V4 Ch5 | p. 5.45 |
| Eq. 5.2 (adjusted EF) | EFc·SFw·SFp·SFo | IPCC 2006 V4 Ch5 | p. 5.48 |
| EFc (Korea) | {f['EFc']} kg CH4/ha/d | NID 표 5-27 | report p. 5-29 (PDF p. 286) |
| SFp, non-flooded pre-season < 180 d / > 180 d / flooded ≥ 30 d | {f['SFp_lt180']} / {f['SFp_gt180']} / {f['SFp_fl30']} | NID 표 5-28 | p. 5-30 (PDF p. 287) |
| SFw, continuous / 1× < 1 wk / 1× 1–2 wk / ≥ 2× | {f['SFw_CF']} / {f['SFw_1x_lt1wk']} / {f['SFw_1x_1to2wk']} / {f['SFw_2x']} | NID 표 5-28 | p. 5-30 (PDF p. 287) |
| SFo, straw (6 Mg/ha) / green manure (0.0685 Mg/ha) | {f['SFo_straw']} / {f['SFo_green']} | NID 표 5-29 | p. 5-30 (PDF p. 287) |
| Area mix by water regime × amendment, 2023 (731.8 kha) | 36 cells | NID 표 5-31 | p. 5-32 (PDF p. 289) |
| Irrigated-rice CH4, 2023 | {f['CH4_irrigated_2023']:,.0f} kt CO2e | NID 표 5-24 | p. 5-27 (PDF p. 284) |
| GWP CH4 | {gwp:.0f} | NID 표 1-9 | p. 1-26 (PDF p. 67) |
| **EF_nat (derived)** | **{ef_nat:.4f} kg CH4/ha/d** | Σ EF_i A_i / Σ A_i over NID 표 5-31 | computed |
| **t_eff (derived)** | **{t_eff:.1f} days** | NID 표 5-24 ÷ (Σ EF_i A_i) | computed |
| IPCC default EFc (range) | {ip['EFc']} ({ipf.set_index('key').loc['EFc','low']}–{ipf.set_index('key').loc['EFc','high']}) kg CH4/ha/d | IPCC Table 5.11 | p. 5.49 |
| IPCC SFw: continuous / single aeration / multiple aeration (ranges) | 1 (0.79–1.26) / 0.60 (0.46–0.80) / 0.52 (0.41–0.66) | IPCC Table 5.12 | p. 5.49 |
| IPCC SFp: < 180 d / > 180 d / flooded > 30 d (ranges) | 1 (0.88–1.14) / 0.68 (0.58–0.80) / 1.90 (1.65–2.18) | IPCC Table 5.13 | p. 5.50 |
| IPCC SFo exponent (range) | 0.59 (0.54–0.64) | IPCC Eq. 5.3 text | p. 5.50 |
| IPCC CFOA: straw short / straw long / green manure (ranges) | 1 (0.97–1.04) / 0.29 (0.20–0.40) / 0.50 (0.30–0.60) | IPCC Table 5.14 | p. 5.51 |

**Transcription check.** Every value in `data/raw/gir/nid2025_rice_factors.csv` and `data/raw/ipcc/ipcc2006_v4c5_rice_factors.csv` was searched for on its cited PDF page.
- Not found: NID {bad_nid if bad_nid else 'none'}; IPCC {bad_ipcc if bad_ipcc else 'none'}.
- Recomputed EF_i vs the rounded NID 표 5-26 entries (5 spot checks, ±0.005): **{'match' if t526_ok else 'MISMATCH'}**.

## Results (2025)
| Quantity | Value |
|---|---|
| National paddy CH4 (Σ units) | **{ch4_nat_t:,.0f} t CH4 = {ch4_nat_kt_co2e:,.1f} kt CO2e** |
| For comparison: NID 2023 rice total (표 5-24; 2023 area, 3-yr-average activity data) | {f['CH4_rice_total_2023']:,.0f} kt CO2e |
| National average intensity (Σ CH4 · GWP / national production) | {nat_int:.4f} kg CO2e / kg milled rice |
| Intensity min / median / max | {imin:.4f} / {imed:.4f} / {imax:.4f} kg CO2e/kg |
| **Ratio max / min** | **{imax/imin:.3f}** |
| Lowest-intensity unit | {lo['name']} ({lo['admin_code']}): yield {lo['yield']:.0f} kg/10a |
| Highest-intensity unit | {hi['name']} ({hi['admin_code']}): yield {hi['yield']:.0f} kg/10a |

**Lowest 5 and highest 5 intensities**

{th}
{chr(10).join(row(r) for _, r in top.head(5).iterrows())}
{chr(10).join(row(r) for _, r in top.tail(5).iterrows())}

**Yield field.** KOSIS publishes 10a당 생산량 as an integer; several small Gyeonggi cities share the same published value (485 kg/10a). Production ÷ area (`yield_implied_t_ha` in the CSV) differs from the published yield by more than 1% in {int((dev.abs() > 0.01).sum())} units, all with ≤ {int(out.loc[dev.abs() > 0.01, 'paddy_area_ha'].max())} ha of paddy, where rounding of the integer area dominates (maximum {float(dev.abs().max()):.1%}). The median deviation is {float(dev.abs().median()):.2%}. Intensity is computed as CH4 / production, so it is consistent with published production.

**Tier 1 sensitivity (not used downstream).** This uses the IPCC default factors on the same NID area mapping:
- 1× aeration → "single aeration"; ≥ 2× → "multiple aeration";
- SFo from IPCC Eq. 5.3 with the NID application rates.

The straw timing is not reported in the NID, so two bounds are shown:
""" + "\n".join(f"- {k}: EF_nat = {v['ef_nat']:.3f} kg CH4/ha/d, national intensity = {v['intensity_nat']:.4f} kg CO2e/kg"
                for k, v in t1.items()) + f"""

The Korean Tier 2 national intensity ({nat_int:.4f}) is used throughout.

## Done criterion
- National production reconciles with the KOSIS national figure within 1%: **{'MET' if abs(recon) <= 0.01 else 'NOT MET'}** ({recon:+.4%}).
- Every factor carries a page citation, and all transcribed values were found on their cited pages: **{'MET' if not bad_nid and not bad_ipcc else 'NOT MET'}**.

## Limitations specific to this phase
- **Only the yield term varies.** Water regime, pre-season flooding and organic amendment use the national 2023 mix in every unit, so per-kg intensity varies only through yield. Idea 2's stated risk applies here.
- **Year mismatch in the area mix.** The 2023 NID mix (3-year-average activity data, 2021–2023) is applied to 2025 areas.
- **t_eff is back-calculated.** It absorbs any difference between the NID's activity-data definition (논벼 + 맥류 double-cropped area) and KOSIS 논벼 area.
- **Rainfed paddies get the irrigated mix.** Rainfed paddies (2.7 kha in the NID, 0.4% of rice area; 10 kt CO2e) are treated with the irrigated mix.
"""
    open(os.path.join(ROOT, "03-supply-intensity.md"), "w", encoding="utf-8").write(md)
    print(f"units={len(out)} recon={recon:+.5f} ef_nat={ef_nat:.4f} t_eff={t_eff:.2f} ch4_kt_co2e={ch4_nat_kt_co2e:.1f} "
          f"int min/med/max={imin:.4f}/{imed:.4f}/{imax:.4f} ratio={imax/imin:.3f} bad_nid={bad_nid} bad_ipcc={bad_ipcc} "
          f"t526={t526_ok} done={done}")


if __name__ == "__main__":
    main()
