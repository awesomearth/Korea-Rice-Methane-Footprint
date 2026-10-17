"""Phase 8 (P4) - hotspot maps, 300 dpi PNG.

Inputs : data/processed/footprint.csv, supply_intensity.csv, flows.csv, boundary geometry (geo_units.py)
Outputs: figures/fig1-per-capita-footprint.png, fig2-intensity.png, fig3-riceshed-flows.png,
         fig4-ratio-to-national-average.png, data/processed/figure_classes.json, 08-figures.md
Run from output/05-rice-shed/:  python code/phase8_figures.py
"""
import json
import os
import sys

import mapclassify
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
import geo_units as G  # noqa: E402

ROOT = G.ROOT
R = lambda *a: os.path.join(ROOT, *a)
FIG = R("figures")
SURF, INK, MUTED, EDGE = "#fcfcfb", "#1f1f1e", "#6b6b68", "#ffffff"
BLUE = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]          # sequential (reference palette blue)
ORANGE = ["#fbd9c8", "#f5a37f", "#eb6834", "#b94a1f", "#7a2e10"]        # sequential, second context (orange)
DIVERGING = ["#1c5cab", "#86b6ef", "#f0efec", "#f19c9b", "#c23434"]     # blue <-> gray <-> red
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7, "axes.edgecolor": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF})


def classed(ax, gdf, col, breaks, colors, fmt):
    """Fill polygons by class (breaks are upper bounds); return legend handles."""
    idx = np.searchsorted(breaks, gdf[col].values, side="left")
    idx = np.clip(idx, 0, len(colors) - 1)
    gdf.assign(_c=[colors[i] for i in idx]).plot(ax=ax, color=gdf.assign(_c=[colors[i] for i in idx])["_c"],
                                                 edgecolor=EDGE, linewidth=0.15)
    lows = [gdf[col].min()] + list(breaks[:-1])
    return [Patch(facecolor=c, edgecolor="none", label=f"{fmt(lo)} – {fmt(hi)}") for c, lo, hi in zip(colors, lows, breaks)]


def frame(ax, title, sub):
    ax.set_axis_off()
    ax.set_title(title, loc="left", fontsize=9, color=INK, fontweight="bold", pad=14)
    ax.text(0, 1.005, sub, transform=ax.transAxes, fontsize=6.5, color=MUTED, va="bottom")


def caption(fig, text):
    fig.text(0.02, 0.012, text, fontsize=5.5, color=MUTED, ha="left", va="bottom", wrap=True)


def main():
    os.makedirs(FIG, exist_ok=True)
    d, s, polys, cw, cons_ll, prod_ll, _, prod_geom = G.attach_units()
    fp = pd.read_csv(R("data/processed/footprint.csv"), dtype={"admin_code": str})
    flows = pd.read_csv(R("data/processed/flows.csv"), dtype={"from_code": str, "to_code": str})
    assert list(fp.admin_code) == list(d.admin_code)
    fp["poly_idx"] = d["poly_idx"].values
    agg = fp.groupby("poly_idx").agg(footprint=("footprint_tco2e", "sum"), pop=("population", "sum"),
                                     natavg=("footprint_natavg_tco2e", "sum"), n_units=("admin_code", "size"))
    agg["per_capita"] = agg.footprint * 1000 / agg["pop"]
    agg["ratio"] = agg.footprint / agg.natavg
    P = polys.join(agg, how="left")
    assert P.per_capita.notna().all()
    classes = {}
    nat_int = json.load(open(R("data/processed/ch4_factors.json")))["national_intensity_kgco2e_per_kg"]

    # ---- fig1 per capita footprint (Fisher-Jenks, k=5)
    fj = mapclassify.FisherJenks(P.per_capita.values, k=5)
    classes["fig1"] = dict(variable="per capita household rice-shed CH4 footprint, kg CO2e/person/yr",
                           method="Fisher-Jenks (exact Jenks natural breaks), k=5",
                           breaks=[round(float(b), 2) for b in fj.bins], min=round(float(P.per_capita.min()), 2),
                           counts=[int(c) for c in fj.counts])
    fig, ax = plt.subplots(figsize=(4.3, 5.4))
    h = classed(ax, P, "per_capita", fj.bins, BLUE, lambda v: f"{v:.1f}")
    frame(ax, "Per capita rice-shed CH4 footprint, 2025", "kg CO2e per person per year (household rice)")
    ax.legend(handles=h, loc="lower right", frameon=False, title="kg CO2e / person", title_fontsize=6.5, fontsize=6)
    caption(fig, "Source: data/processed/footprint.csv (252 units; non-autonomous gu aggregated to parent city as Σ footprint / Σ population). "
                 "Classes: Fisher-Jenks k=5. Projection: EPSG:5179. Boundaries: geoBoundaries KOR ADM2 (CC BY 3.0) + OSM (Yeonggwang).")
    fig.savefig(os.path.join(FIG, "fig1-per-capita-footprint.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    # ---- fig2 producer intensity (Fisher-Jenks, k=5)
    Q = polys.copy()
    Q["intensity"] = np.nan
    for (r, code) in zip(s.itertuples(), s.admin_code):
        if len(code) == 2:
            Q.loc[Q.sido == G.KOSIS2MOIS[code], "intensity"] = r.kgco2e_per_kg
        else:
            row = cw[(cw.side == "producer") & (cw.unit_code == code)].iloc[0]
            Q.loc[Q.shapeID == row.shapeID, "intensity"] = r.kgco2e_per_kg
    Qn = Q[Q.intensity.notna()]
    fj2 = mapclassify.FisherJenks(s.kgco2e_per_kg.values, k=5)
    classes["fig2"] = dict(variable="CH4 intensity of producing units, kg CO2e per kg milled rice",
                           method="Fisher-Jenks k=5 on the 156 producing units",
                           breaks=[round(float(b), 4) for b in fj2.bins], min=round(float(s.kgco2e_per_kg.min()), 4),
                           counts=[int(c) for c in fj2.counts], polygons_without_producer=int(Q.intensity.isna().sum()),
                           polygons_without_producer_names=Q.loc[Q.intensity.isna(), "shapeName"].tolist())
    fig, ax = plt.subplots(figsize=(4.3, 5.4))
    h = classed(ax, Qn, "intensity", fj2.bins, ORANGE, lambda v: f"{v:.3f}")
    if Q.intensity.isna().any():
        Q[Q.intensity.isna()].plot(ax=ax, color="#e6e5e1", edgecolor=EDGE, linewidth=0.15)
        h.append(Patch(facecolor="#e6e5e1", label="no KOSIS rice row"))
    frame(ax, "CH4 intensity of rice by producing unit, 2025", "kg CO2e per kg milled rice (varies with yield only)")
    ax.legend(handles=h, loc="lower right", frameon=False, title="kg CO2e / kg", title_fontsize=6.5, fontsize=6)
    caption(fig, "Source: data/processed/supply_intensity.csv (156 producing units; metropolitan cities are one unit and share one value "
                 "across their gu). Classes: Fisher-Jenks k=5. Projection: EPSG:5179.")
    fig.savefig(os.path.join(FIG, "fig2-intensity.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    # ---- fig3 rice-shed flows for the five largest consuming units (small multiples)
    top = d.sort_values("rice_demand_t", ascending=False).head(5)
    from shapely.geometry import LineString, Point
    import geopandas as gpd
    pc = gpd.GeoSeries(gpd.points_from_xy(prod_ll[:, 0], prod_ll[:, 1]), crs=4326).to_crs(G.CRS)
    cc = gpd.GeoSeries(gpd.points_from_xy(cons_ll[:, 0], cons_ll[:, 1]), crs=4326).to_crs(G.CRS)
    pidx = {c: i for i, c in enumerate(s.admin_code)}
    cidx = {c: i for i, c in enumerate(d.admin_code)}
    sg = pd.read_csv(R("data/raw/aux/sgis_sgg_english.csv"), encoding="cp949")
    sido_en = dict(zip(sg["시도명"].map(G.sido_codes()), sg["시도영문"]))
    # common zoom: all source and consumer geometries of the five units, padded 25 km
    zoom = [prod_geom[pidx[c]] for c in flows[flows.to_code.isin(top.admin_code)].from_code] + \
           [polys.loc[d.poly_idx.iloc[cidx[c]], "geometry"] for c in top.admin_code]
    zx0, zy0, zx1, zy1 = gpd.GeoSeries(zoom, crs=G.CRS).total_bounds
    pad = 25000
    fig, axg = plt.subplots(2, 3, figsize=(7.2, 5.0))
    axes = axg.ravel()[:5]
    axg.ravel()[5].set_axis_off()
    tmax = flows[flows.to_code.isin(top.admin_code)].tonnes.max()
    names_en = polys.set_index(polys.index)["city_en"]
    fig3_rows = []
    for ax, r in zip(axes, top.itertuples()):
        polys.plot(ax=ax, color="#ecebe7", edgecolor=EDGE, linewidth=0.1)
        f = flows[flows.to_code == r.admin_code]
        src_geoms = [prod_geom[pidx[c]] for c in f.from_code]
        gpd.GeoSeries(src_geoms, crs=G.CRS).plot(ax=ax, color=ORANGE[1], edgecolor=EDGE, linewidth=0.1)
        gpd.GeoSeries([polys.loc[d.poly_idx.iloc[cidx[r.admin_code]], "geometry"]], crs=G.CRS).boundary.plot(
            ax=ax, color=INK, linewidth=0.6)
        for fr in f.itertuples():
            a, b = pc.iloc[pidx[fr.from_code]], cc.iloc[cidx[r.admin_code]]
            lw = 0.6 + 2.6 * fr.tonnes / tmax
            if a.distance(b) < 1:
                ax.plot(b.x, b.y, "o", ms=3 + 4 * fr.tonnes / tmax, color=BLUE[3], mec=SURF, mew=0.6)
            else:
                ax.plot([a.x, b.x], [a.y, b.y], color=BLUE[3], lw=lw, solid_capstyle="round", alpha=0.9)
        ax.plot(cc.iloc[cidx[r.admin_code]].x, cc.iloc[cidx[r.admin_code]].y, "o", ms=2.5, color=INK)
        km = (f.tonnes * f.km).sum() / f.tonnes.sum()
        en = names_en.loc[d.poly_idx.iloc[cidx[r.admin_code]]]
        ax.set_xlim(zx0 - pad, zx1 + pad)
        ax.set_ylim(zy0 - pad, zy1 + pad)
        ax.set_axis_off()
        ax.set_title(f"{sido_en[r.admin_code[:2]]} {en} ({r.admin_code})\n"
                     f"{r.rice_demand_t:,.0f} t · {len(f)} source(s) · mean {km:.0f} km",
                     fontsize=6.5, color=INK, loc="left")
        fig3_rows.append(dict(admin_code=r.admin_code, label=en, demand_t=round(r.rice_demand_t, 1), n_sources=len(f),
                              mean_km=round(km, 1)))
    fig.suptitle("Rice-sheds of the five largest consuming units (LP flows, 2025)", x=0.02, y=0.99, ha="left", fontsize=9,
                 fontweight="bold", color=INK)
    axg.ravel()[5].text(0.0, 0.9, "How to read\n\n• line: producer centroid → consumer\n  centroid, width ∝ tonnes\n"
                        "• blue dot: supply from the consumer's\n  own polygon (0 km)\n• orange: source units\n"
                        "• black outline: consumer polygon\n• all panels share one extent",
                        transform=axg.ravel()[5].transAxes, fontsize=6.5, color=MUTED, va="top")
    caption(fig, "Source: data/processed/flows.csv (LP solution) with data/processed/demand.csv and supply_intensity.csv. "
                 "No classification (flows drawn individually; width linear in tonnes, max "
                 f"{tmax:,.0f} t). Projection: EPSG:5179.")
    fig.savefig(os.path.join(FIG, "fig3-riceshed-flows.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    classes["fig3"] = dict(variable="LP flows (t) to the five largest consuming units", method="none (individual flows)",
                           panels=fig3_rows, max_flow_t=round(float(tmax), 1))

    # ---- fig4 ratio spatial / national-average (manual diverging classes around 1)
    br = np.array([0.90, 0.97, 1.03, 1.10, max(1.10001, float(P.ratio.max()))])
    classes["fig4"] = dict(variable="ratio of spatial footprint to national-average-intensity footprint",
                           method="manual diverging classes centred on 1.0 (neutral class 0.97–1.03)",
                           breaks=[round(float(b), 3) for b in br], min=round(float(P.ratio.min()), 3),
                           counts=[int(c) for c in np.bincount(np.clip(np.searchsorted(br, P.ratio.values), 0, 4),
                                                               minlength=5)])
    fig, ax = plt.subplots(figsize=(4.3, 5.4))
    h = classed(ax, P, "ratio", br, DIVERGING, lambda v: f"{v:.2f}")
    frame(ax, "Spatial footprint ÷ national-average footprint", f"> 1: sources rice dirtier than the national mean ({nat_int:.3f} kg CO2e/kg)")
    ax.legend(handles=h, loc="lower right", frameon=False, title="ratio", title_fontsize=6.5, fontsize=6)
    caption(fig, "Source: data/processed/footprint.csv (ratio_spatial_to_natavg; non-autonomous gu aggregated to parent city). "
                 "Classes: manual, diverging around 1.0. Projection: EPSG:5179.")
    fig.savefig(os.path.join(FIG, "fig4-ratio-to-national-average.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    json.dump(classes, open(R("data/processed/figure_classes.json"), "w"), indent=1, ensure_ascii=False)
    sizes = {f: os.path.getsize(os.path.join(FIG, f)) for f in sorted(os.listdir(FIG)) if f.endswith(".png")}
    br_txt = lambda c: " | ".join(f"{lo} – {hi} (n={n})" for lo, hi, n in
                                  zip([c["min"]] + c["breaks"][:-1], c["breaks"], c["counts"]))
    md = f"""# 08 — Figures (Idea 2, Phase 8 / P4)

Generated by `code/phase8_figures.py`. All maps are in **EPSG:5179** (Korea 2000 / Unified CS) and saved as 300 dpi PNG in `figures/`. Class breaks are also stored in `data/processed/figure_classes.json`.
- **Base geometry:** geoBoundaries KOR ADM2 (CC BY 3.0, citypopulation.de) plus the OSM patch for 영광군 (ODbL), as approved in `00-scope.md` (e).
- **Polygon level:** maps are drawn per polygon (229), so 일반구 consuming units are aggregated to their parent city (Σ footprint / Σ population).
- **Colour:** sequential maps use single-hue ramps (blue for consumers, orange for producers). fig4 uses a blue–gray–red diverging scheme with a neutral class around 1. fig3 is a set of small multiples in one hue: a 5-hue categorical palette failed the all-pairs colour-vision and normal-vision checks for a map.

| File | Bytes |
|---|---|
""" + "\n".join(f"| `figures/{k}` | {v:,} |" for k, v in sizes.items()) + f"""

## fig1-per-capita-footprint.png
- **Variable:** {classes['fig1']['variable']}.
- **Data file:** `data/processed/footprint.csv` (`footprint_tco2e`, `population`).
- **Classification:** {classes['fig1']['method']}. Breaks (min – upper bound, count of polygons): {br_txt(classes['fig1'])}.
- **Caption:** *Per capita household rice-shed CH4 footprint by si/gun/gu, 2025 (kg CO2e/person/yr). Source: data/processed/footprint.csv; Fisher-Jenks k=5; EPSG:5179.*

## fig2-intensity.png
- **Variable:** {classes['fig2']['variable']}.
- **Data file:** `data/processed/supply_intensity.csv` (`kgco2e_per_kg`).
- **Classification:** {classes['fig2']['method']}. Breaks (count of producing units): {br_txt(classes['fig2'])}. Polygons with no producer row: {classes['fig2']['polygons_without_producer']} ({", ".join(classes['fig2']['polygons_without_producer_names'])}; these have no row in KOSIS DT_1ET0034, i.e. no reported paddy rice).
- **Note:** metropolitan producing units colour all their gu with one value.
- **Caption:** *CH4 intensity of rice by producing unit, 2025 (kg CO2e per kg milled rice). Source: data/processed/supply_intensity.csv; Fisher-Jenks k=5; EPSG:5179.*

## fig3-riceshed-flows.png
- **Variable:** {classes['fig3']['variable']}.
- **Data file:** `data/processed/flows.csv`, with `demand.csv` and `supply_intensity.csv` for names and centroids.
- **Classification:** none. Each flow is drawn individually; line width is linear in tonnes (max {classes['fig3']['max_flow_t']:,} t), and a dot marks supply from the consumer's own polygon (0 km).
- **Panels:** """ + "; ".join(f"{p['label']} ({p['admin_code']}): {p['n_sources']} source(s), mean {p['mean_km']} km" for p in fig3_rows) + f""".
- **Caption:** *Rice-sheds of the five largest consuming units under the distance-minimizing LP, 2025. Source: data/processed/flows.csv; no classification; EPSG:5179.*

## fig4-ratio-to-national-average.png
- **Variable:** {classes['fig4']['variable']}.
- **Data file:** `data/processed/footprint.csv` (`footprint_tco2e`, `footprint_natavg_tco2e`).
- **Classification:** {classes['fig4']['method']}. Breaks (count of polygons): {br_txt(classes['fig4'])}.
- **Caption:** *Ratio of the spatially explicit footprint to the national-average-intensity footprint, 2025. Source: data/processed/footprint.csv; manual diverging classes around 1.0; EPSG:5179.*

## Done criterion
All four PNGs exist and are non-empty, and each has a caption stating its source file and classification: **{'MET' if len(sizes) == 4 and min(sizes.values()) > 0 else 'NOT MET'}**.
"""
    open(R("08-figures.md"), "w", encoding="utf-8").write(md)
    print(sizes, json.dumps({k: v.get("breaks") for k, v in classes.items()}))


if __name__ == "__main__":
    main()
