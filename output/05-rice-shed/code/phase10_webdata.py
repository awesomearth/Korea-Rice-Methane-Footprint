"""Phase 10: browser data bundle for the interactive presentation (presentation/).

Reads only Phase 2-8 artifacts and the approved geometry (geo_units.boundary_polygons, i.e.
geoBoundaries KOR ADM2 + the OSM patch for 영광군). Nothing is modelled here: the script joins,
sums, averages and sorts existing values, and copies class breaks from figure_classes.json.

Outputs:
  presentation/data/bundle.json        units, producers, flows, national totals, breaks, sources
  presentation/data/korea-adm2.geo.json  229 polygons, WGS84, simplified for the web
  presentation/index.html              both files embedded between the DATA markers, so the page
                                       needs no fetch() (Chrome blocks fetch on file:// pages)
"""
import json
import os
import re
import sys

import numpy as np
import pandas as pd
import shapely

sys.path.insert(0, os.path.dirname(__file__))
from geo_units import CRS, boundary_polygons, sido_codes  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
R = lambda *a: os.path.join(ROOT, *a)
OUT = R("presentation", "data")
SIMPLIFY_M = 250  # Douglas-Peucker tolerance in EPSG:5179 metres, display only
SIZE_SPLIT = 125_000  # population split used in 06-uncertainty.md


def rd(x, n):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), n)


def english_names():
    """(sido code, 시군구명) -> English unit name, and sido code -> English province name."""
    s2c = sido_codes()
    sg = pd.read_csv(R("data/raw/aux/sgis_sgg_english.csv"), encoding="cp949")
    sg["sido"] = sg["시도명"].map(s2c)
    unit = {(r.sido, r.시군구명): r.시군구영문 for r in sg.itertuples()}
    prov = dict(zip(sg["sido"], sg["시도영문"]))
    return unit, prov


def geometry():
    polys, _, _ = boundary_polygons()
    g = polys.copy()
    g["geometry"] = g.geometry.simplify(SIMPLIFY_M, preserve_topology=True)
    g = g.to_crs(4326)
    g["geometry"] = shapely.orient_polygons(g.geometry.values, exterior_cw=True)  # d3-geo winding

    def rnd(c):
        if isinstance(c[0], (float, int)):
            return [round(c[0], 4), round(c[1], 4)]
        return [rnd(x) for x in c]

    feats = []
    for r in g.itertuples():
        gj = r.geometry.__geo_interface__
        feats.append({"type": "Feature", "id": r.shapeID,
                      "properties": {"en": re.sub(r"\s*\[.*?\]", "", r.shapeName), "ko": r.city_ko, "sido": r.sido},
                      "geometry": {"type": gj["type"], "coordinates": rnd(gj["coordinates"])}})
    return {"type": "FeatureCollection", "features": feats}


def sources_table():
    """Report §2 input table, parsed from 09-report.md."""
    txt = open(R("09-report.md"), encoding="utf-8").read()
    sec = txt.split("## 2. Data and sources")[1].split("## 3.")[0]
    rows = [l for l in sec.splitlines() if l.startswith("| ") and not l.startswith("| Input") and not l.startswith("|---")]
    out = []
    for l in rows:
        c = [x.strip() for x in l.strip("|").split("|")]
        out.append({"input": re.sub(r"\*\*", "", c[0]), "path": c[1].strip("`").replace("**", ""), "years": c[4],
                    "unit": c[5], "url": c[6].split(" ;")[0]})
    return out


def embed_in_page(blocks):
    page = R("presentation", "index.html")
    html = open(page, encoding="utf-8").read()
    start, end = "<!-- DATA:START (written by code/phase10_webdata.py) -->", "<!-- DATA:END -->"
    i, j = html.index(start) + len(start), html.index(end)
    body = "".join(f'\n<script type="application/json" id="{k}">'
                   + json.dumps(v, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>"
                   for k, v in blocks.items())
    with open(page, "w", encoding="utf-8") as f:
        f.write(html[:i] + body + "\n" + html[j:])


def main():
    os.makedirs(OUT, exist_ok=True)
    fp = pd.read_csv(R("data/processed/footprint.csv"), dtype={"admin_code": str})
    sc = pd.read_csv(R("data/processed/scenarios.csv"), dtype={"admin_code": str})
    mc = pd.read_csv(R("data/processed/mc_results.csv"), dtype={"admin_code": str})
    si = pd.read_csv(R("data/processed/supply_intensity.csv"), dtype={"admin_code": str})
    fl = pd.read_csv(R("data/processed/flows.csv"), dtype={"from_code": str, "to_code": str})
    cw = pd.read_csv(R("data/processed/crosswalk.csv"), dtype={"unit_code": str, "sido": str})
    ch4 = json.load(open(R("data/processed/ch4_factors.json"), encoding="utf-8"))
    br = json.load(open(R("data/processed/figure_classes.json"), encoding="utf-8"))
    draws = np.load(R("data/processed/mc_draws_per_capita.npz"), allow_pickle=True)
    unit_en, prov_en = english_names()

    cons = cw[cw.side == "consumer"].set_index("unit_code")
    prod = cw[cw.side == "producer"].set_index("unit_code")
    u = fp.merge(sc[["admin_code", "S1_pct", "S2_pct", "S1S2_pct", "S1_tco2e", "S2_tco2e", "S1S2_tco2e"]], on="admin_code") \
          .merge(mc[["admin_code", "mean", "p5", "p95", "mape", "sourcing_only_p5", "sourcing_only_p95", "sourcing_only_mape"]],
                 on="admin_code")
    assert len(u) == 252

    units = []
    for r in u.itertuples():
        c = cons.loc[r.admin_code]
        sgg = r.name.split(" ", 1)[-1]
        units.append({
            "code": r.admin_code, "ko": r.name, "en": unit_en.get((c.sido, sgg), c.shapeName),
            "sido": c.sido, "poly": c.shapeID, "lon": rd(c.centroid_lon, 4), "lat": rd(c.centroid_lat, 4),
            "pop": int(r.population), "demand_t": rd(r.rice_demand_t, 1),
            "fp_t": rd(r.footprint_tco2e, 1), "natavg_t": rd(r.footprint_natavg_tco2e, 1),
            "pc": rd(r.per_capita_kgco2e, 2), "int": rd(r.sourcing_intensity_kgco2e_per_kg, 4),
            "ratio": rd(r.ratio_spatial_to_natavg, 4), "nsrc": int(r.n_sources), "km": rd(r.mean_sourcing_km, 1),
            "s1": rd(r.S1_pct, 2), "s2": rd(r.S2_pct, 2), "s12": rd(r.S1S2_pct, 2),
            "mc_mean": rd(r.mean, 2), "p5": rd(r.p5, 2), "p95": rd(r.p95, 2), "mape": rd(r.mape, 4),
            "src_p5": rd(r.sourcing_only_p5, 2), "src_p95": rd(r.sourcing_only_p95, 2),
            "src_mape": rd(r.sourcing_only_mape, 4)})

    producers = []
    for r in si.itertuples():
        c = prod.loc[r.admin_code]
        metro = len(r.admin_code) == 2
        name_parts = r.name.split(" ", 1)
        en = prov_en.get(c.sido, r.name) if metro else unit_en.get((c.sido, name_parts[-1]), c.shapeName)
        producers.append({
            "code": r.admin_code, "ko": r.name, "en": en, "sido": c.sido, "metro": metro,
            "polys": str(c.shapeID).split("; "), "lon": rd(c.centroid_lon, 4), "lat": rd(c.centroid_lat, 4),
            "area_ha": rd(r.paddy_area_ha, 1), "prod_t": rd(r.production_t, 1), "yield": rd(r[si.columns.get_loc("yield") + 1], 1),
            "ch4_t": rd(r.ch4_t, 2), "int": rd(r.kgco2e_per_kg, 4)})
    assert len(producers) == 156

    flows = [{"f": r.from_code, "t": r.to_code, "tn": rd(r.tonnes, 1), "km": rd(r.km, 1)} for r in fl.itertuples()]
    assert len(flows) == 408

    # Polygon-level map values, as in phase8_figures.py: Σ footprint / Σ population per polygon
    pg = u.assign(poly=u.admin_code.map(cons.shapeID)).groupby("poly")
    poly_cons = {p: {"pc": rd(g.footprint_tco2e.sum() * 1000 / g.population.sum(), 2),
                     "ratio": rd(g.footprint_tco2e.sum() / g.footprint_natavg_tco2e.sum(), 4),
                     "units": g.admin_code.tolist()} for p, g in pg}
    poly_prod = {pid: p["code"] for p in producers for pid in p["polys"]}

    # National figures
    hh = fl[fl.to_code != "SLACK"]
    slack = fl[fl.to_code == "SLACK"]
    int_by = si.set_index("admin_code").kgco2e_per_kg
    slack_kt = float((slack.tonnes * slack.from_code.map(int_by)).sum() / 1000)
    big = mc.population > SIZE_SPLIT
    k = draws["k"]
    sc_tot = {c: rd(sc[c].sum() / 1000, 4) for c in ["baseline_tco2e", "S1_tco2e", "S2_tco2e", "S1S2_tco2e"]}

    # Household sourcing origin by consuming province (tonnes share of producer province)
    hh_o = hh.assign(to_sido=hh.to_code.str[:2], from_sido=hh.from_code.map(prod.sido))
    origin = {}
    for s, g in hh_o.groupby("to_sido"):
        sh = g.groupby("from_sido").tonnes.sum().sort_values(ascending=False) / g.tonnes.sum()
        origin[s] = [[k_, rd(v, 4)] for k_, v in sh.items()]
    cap = hh_o[hh_o.to_sido.isin(["11", "41"])]  # Seoul + Gyeonggi-do, as in 09-report.md §4
    sh = cap.groupby("from_sido").tonnes.sum().sort_values(ascending=False) / cap.tonnes.sum()
    origin["capital"] = [[k_, rd(v, 4)] for k_, v in sh.items()]
    cap_int = float((cap.tonnes * cap.from_code.map(int_by)).sum() / cap.tonnes.sum())
    reg = []
    for s, g in u.groupby(u.admin_code.str[:2]):
        reg.append({"sido": s, "en": prov_en.get(s, s), "n": int(len(g)), "below": int((g.ratio_spatial_to_natavg < 1).sum()),
                    "median": rd(g.ratio_spatial_to_natavg.median(), 4),
                    "pc_median": rd(g.per_capita_kgco2e.median(), 2)})

    national = {
        "year": 2025, "gwp": ch4["gwp"], "ef_c": ch4["EFc"], "ef_nat": rd(ch4["ef_nat"], 4),
        "t_eff_days": rd(ch4["t_eff_days"], 1), "ch4_t": rd(ch4["national_ch4_t"], 0),
        "paddy_kt": rd(ch4["national_kt_co2e"], 1), "intensity": rd(ch4["national_intensity_kgco2e_per_kg"], 4),
        "production_t": ch4["national_production_t"],
        "household_kt": rd(fp.footprint_tco2e.sum() / 1000, 1), "slack_kt": rd(slack_kt, 1),
        "slack_t": rd(slack.tonnes.sum(), 0), "slack_share": rd(slack.tonnes.sum() / si.production_t.sum(), 5),
        "pop": int(fp.population.sum()), "n_cons": len(fp), "n_prod": len(si), "per_capita_kg": 53.9,
        "pc_mean": rd(fp.per_capita_kgco2e.mean(), 4), "pc_sd": rd(fp.per_capita_kgco2e.std(), 4),
        "pc_min": rd(fp.per_capita_kgco2e.min(), 2), "pc_max": rd(fp.per_capita_kgco2e.max(), 2),
        "pc_popw": rd(fp.footprint_tco2e.sum() * 1000 / fp.population.sum(), 2),
        "pc_natavg": rd(fp.footprint_natavg_tco2e.sum() * 1000 / fp.population.sum(), 2),
        "int_min": rd(si.kgco2e_per_kg.min(), 3), "int_max": rd(si.kgco2e_per_kg.max(), 3),
        "ratio_min": rd(fp.ratio_spatial_to_natavg.min(), 3), "ratio_max": rd(fp.ratio_spatial_to_natavg.max(), 3),
        "ratio_below": int((fp.ratio_spatial_to_natavg < 1).sum()),
        "mean_km": rd((hh.tonnes * hh.km).sum() / hh.tonnes.sum(), 1), "tkm_m": rd((hh.tonnes * hh.km).sum() / 1e6, 1),
        "nsrc_median": int(fp.n_sources.median()), "nsrc_max": int(fp.n_sources.max()),
        "mape": rd(mc.mape.mean(), 4), "mape_big": rd(mc.mape[big].mean(), 4), "mape_small": rd(mc.mape[~big].mean(), 4),
        "src_mape": rd(mc.sourcing_only_mape.mean(), 4), "src_mape_big": rd(mc.sourcing_only_mape[big].mean(), 4),
        "src_mape_small": rd(mc.sourcing_only_mape[~big].mean(), 4), "n_big": int(big.sum()), "n_small": int((~big).sum()),
        "k_mean": rd(k.mean(), 3), "k_p5": rd(np.percentile(k, 5), 3), "k_p95": rd(np.percentile(k, 95), 3),
        "draws": int(k.size), "capital_int": rd(cap_int, 4), "scen": sc_tot}

    bundle = {"national": national, "units": units, "producers": producers, "flows": flows,
              "poly_cons": poly_cons, "poly_prod": poly_prod, "origin": origin, "regions": reg,
              "breaks": {k_: {"min": v["min"], "breaks": v["breaks"], "counts": v["counts"]} for k_, v in br.items()
                         if isinstance(v, dict) and "breaks" in v},
              "sources": sources_table(),
              "provenance": {"generated_by": "code/phase10_webdata.py",
                             "inputs": ["data/processed/footprint.csv", "scenarios.csv", "mc_results.csv",
                                        "supply_intensity.csv", "flows.csv", "crosswalk.csv", "ch4_factors.json",
                                        "figure_classes.json", "mc_draws_per_capita.npz", "09-report.md"]}}
    with open(os.path.join(OUT, "bundle.json"), "w", encoding="utf-8") as f:
        json.dump(bundle, f, ensure_ascii=False, separators=(",", ":"))
    geo = geometry()
    with open(os.path.join(OUT, "korea-adm2.geo.json"), "w", encoding="utf-8") as f:
        json.dump(geo, f, ensure_ascii=False, separators=(",", ":"))

    embed_in_page({"data-bundle": bundle, "data-geo": geo})

    # Checks against 09-report.md / 05-footprint.md / 06-uncertainty.md / 07-scenarios.md
    n = national
    print("polygons", len(geo["features"]), "| units", len(units), "| producers", len(producers), "| flows", len(flows))
    print("household kt", n["household_kt"], "| paddy kt", n["paddy_kt"], "| slack kt", n["slack_kt"], "| slack t", n["slack_t"],
          f"({n['slack_share']:.1%})")
    print("mean km", n["mean_km"], "| t.km (M)", n["tkm_m"], "| sources median/max", n["nsrc_median"], n["nsrc_max"])
    print("pc mean/sd", n["pc_mean"], n["pc_sd"], "| range", n["pc_min"], n["pc_max"], "| ratio", n["ratio_min"], n["ratio_max"])
    print("MAPE", n["mape"], n["mape_big"], n["mape_small"], "| src", n["src_mape"], n["src_mape_big"], n["src_mape_small"])
    print("k", n["k_mean"], n["k_p5"], n["k_p95"], "| scenarios", sc_tot)
    unmapped = [x["code"] for x in units if x["poly"] not in {f["id"] for f in geo["features"]}]
    print("units without polygon:", unmapped)
    for fn in ["bundle.json", "korea-adm2.geo.json"]:
        print(fn, os.path.getsize(os.path.join(OUT, fn)), "bytes")
    assert abs(n["household_kt"] - 4902.9) < 0.05 and abs(n["paddy_kt"] - 6371.2) < 0.05


if __name__ == "__main__":
    main()
