"""Phase 4 (P1) - flow reconstruction: balanced transportation LP, 2025.

Inputs : data/processed/demand.csv, data/processed/supply_intensity.csv,
         boundary: geoBoundaries KOR ADM2 (approved S-BND substitute) + OSM 영광군 patch,
         geoBoundaries ADM1 and SGIS name table (crosswalk only)
Outputs: data/processed/flows.csv, data/processed/crosswalk.csv, data/processed/impedance.npz, 04-flows.md
Run from output/05-rice-shed/:  python code/phase4_flows.py

LP: min sum_ij x_ij d_ij  s.t.  sum_j x_ij + x_i,SLACK = P_i  (every producer ships its production)
                                 sum_i x_ij = D_j               (every consumer receives its demand)
                                 x >= 0
SLACK = single sink node "non-household disposition" (supply - household demand), cost 0.
"""
import os
import sys
import time

import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.optimize import linprog

sys.path.insert(0, os.path.dirname(__file__))
import geo_units as G  # noqa: E402

ROOT = G.ROOT
SLACK = "SLACK"


def build_lp(P, D, dist):
    """Equality-constrained transport LP with one zero-cost slack sink column per producer."""
    n, m = dist.shape
    nv = n * (m + 1)
    c = np.zeros(nv)
    c.reshape(n, m + 1)[:, :m] = dist
    rows, cols = [], []
    for i in range(n):  # producer rows
        rows += [i] * (m + 1)
        cols += list(range(i * (m + 1), (i + 1) * (m + 1)))
    for j in range(m):  # consumer rows
        rows += [n + j] * n
        cols += [i * (m + 1) + j for i in range(n)]
    A = sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n + m, nv))
    b = np.r_[P, D]
    return c, A, b


def solve(P, D, dist):
    c, A, b = build_lp(P, D, dist)
    res = linprog(c, A_eq=A, b_eq=b, bounds=(0, None), method="highs")
    x = res.x.reshape(len(P), dist.shape[1] + 1) if res.x is not None else None
    return res, x


def main():
    t0 = time.time()
    d, s, polys, cw, cons_ll, prod_ll, unmatched_cities, _ = G.attach_units()
    cw.to_csv(os.path.join(ROOT, "data/processed/crosswalk.csv"), index=False, encoding="utf-8")
    n_unmatched = int((cw.status != "matched").sum())
    poly_out = polys.drop(columns="geometry").copy()
    poly_out.to_csv(os.path.join(ROOT, "data/processed/boundary_polygons_crosswalk.csv"), index=False, encoding="utf-8")
    dist = G.haversine(prod_ll, cons_ll)  # km, producers x consumers
    np.savez(os.path.join(ROOT, "data/processed/impedance.npz"), dist_km=dist,
             prod_codes=s.admin_code.values, cons_codes=d.admin_code.values, prod_ll=prod_ll, cons_ll=cons_ll)

    P = s.production_t.values.astype(float)
    D = d.rice_demand_t.values.astype(float)
    slack_t = P.sum() - D.sum()
    assert slack_t >= 0, "household demand exceeds supply: an import source node would be needed"
    res, x = solve(P, D, dist)
    status = res.message
    ok_opt = res.status == 0
    row_err = np.max(np.abs(x.sum(1) - P) / P)
    col_err = np.max(np.abs(x[:, :-1].sum(0) - D) / D)
    flows_ij = x[:, :-1]
    tkm = float((flows_ij * dist).sum())
    mean_km = tkm / D.sum()

    recs = []
    ii, jj = np.nonzero(flows_ij > 1e-6)
    for i, j in zip(ii, jj):
        recs.append((s.admin_code.iloc[i], d.admin_code.iloc[j], flows_ij[i, j], dist[i, j]))
    for i in np.nonzero(x[:, -1] > 1e-6)[0]:
        recs.append((s.admin_code.iloc[i], SLACK, x[i, -1], np.nan))
    flows = pd.DataFrame(recs, columns=["from_code", "to_code", "tonnes", "km"])
    flows.to_csv(os.path.join(ROOT, "data/processed/flows.csv"), index=False, encoding="utf-8")

    # rice-sheds of the five largest consuming units
    top5 = d.sort_values("rice_demand_t", ascending=False).head(5)
    sheds = []
    for r in top5.itertuples():
        f = flows[flows.to_code == r.admin_code].sort_values("tonnes", ascending=False)
        src = s.set_index("admin_code").loc[f.from_code.iloc[0], "name"]
        sheds.append((r.admin_code, r.name, r.rice_demand_t, len(f), src, f.tonnes.iloc[0] / f.tonnes.sum(),
                      (f.tonnes * f.km).sum() / f.tonnes.sum()))
    # per-consumer sourcing distance distribution and number of sources
    per_c = flows[flows.to_code != SLACK].groupby("to_code").apply(
        lambda g: pd.Series({"n_src": len(g), "km": (g.tonnes * g.km).sum() / g.tonnes.sum()}), include_groups=False)
    slack_src = flows[flows.to_code == SLACK].merge(s[["admin_code", "name", "production_t"]],
                                                    left_on="from_code", right_on="admin_code")
    slack_src["share_of_prod"] = slack_src.tonnes / slack_src.production_t
    slack_src = slack_src.sort_values("tonnes", ascending=False)
    dup_methods = polys.match_method.value_counts()
    done = ok_opt and row_err <= 1e-6 and col_err <= 1e-6 and n_unmatched == 0
    rt = time.time() - t0

    sh_rows = "\n".join(f"| {a} | {b} | {c:,.0f} | {n} | {src} | {sh:.1%} | {km:.1f} |" for a, b, c, n, src, sh, km in sheds)
    sl_rows = "\n".join(f"| {r.admin_code} | {r.name} | {r.tonnes:,.0f} | {r.share_of_prod:.0%} |"
                        for r in slack_src.head(10).itertuples())
    md = f"""# 04 — Flow Reconstruction (Idea 2, Phase 4 / P1)

Generated by `code/phase4_flows.py` (shared geometry code in `code/geo_units.py`); runtime {rt:.1f} s.
- **Inputs:** `data/processed/demand.csv`, `data/processed/supply_intensity.csv`, and the boundary geometry approved in `00-scope.md` (e).
- **Outputs:** `data/processed/flows.csv`, `data/processed/crosswalk.csv`, `data/processed/impedance.npz`, `data/processed/boundary_polygons_crosswalk.csv`.

**Status history.** This phase was first BLOCKED, because the S-BND boundary needs a VWorld login. It was re-run on 2026-10-17 after the study owner approved geoBoundaries KOR ADM2 as the substitute.

## 1. Joining units to geometry (crosswalk)
The substitute polygons carry romanized names only, with no codes, so the join is by name, in two steps.

**Step 1: polygon → (sido, si/gun/gu)**
- **Unique names.** {dup_methods.get('unique name', 0)} of {len(polys)} polygons have a name that is unique among the SGIS English si/gun/gu names (`data/raw/aux/sgis_sgg_english.csv`), and are matched directly.
- **Duplicated names.** The remaining {len(polys) - dup_methods.get('unique name', 0)} share a romanized name with another unit (Jung-gu ×6, Dong-gu ×6, Seo-gu ×5, Nam-gu ×5, Buk-gu ×4, Gangseo-gu ×2, Goseong-gun ×2). Each is resolved by the **majority province of already-identified neighbouring polygons** (within 200 m), iterated until stable. The per-polygon vote counts are in `boundary_polygons_crosswalk.csv`.
  - The ADM1 province of the representative point was kept only as a fallback; it was needed {int(polys.match_method.str.contains('ADM1').sum())} times. The coarse Natural Earth ADM1 misplaces several metropolitan gu, e.g. Gwangju's gu fall inside Jeollanam-do.
- **Result:** all {len(polys)} polygons are assigned and every SGIS city is matched exactly once (unmatched cities: {len(unmatched_cities)}). The district counts per metropolitan city are correct: Seoul 25, Busan 16, Daegu 9 (including 군위군), Incheon 10, Gwangju 5, Daejeon 5, Ulsan 5.
- **영광군 (Yeonggwang-gun)** is absent from geoBoundaries (228 polygons against `admUnitCount` 229). It was patched from OpenStreetMap relation 7624187 (ODbL; `data/raw/boundary/osm/yeonggwang_nominatim.json`):
  - the maritime OSM boundary was clipped to land (ADM1 polygons) and to the gap between existing polygons, giving 397 km²;
  - its neighbours are Gochang-gun, Jangseong-gun and Hampyeong-gun, as expected.

**Step 2: units → polygons**
- **Consuming units (252):** MOIS code → (sido, city).
  - The **{int((cw.method == 'parent city polygon (일반구)').sum())} 일반구 units** (e.g. 수원시 장안구) take their parent city's polygon, because the substitute has no 일반구 polygons. They share its centroid.
- **Producing units (156):** KOSIS sido code → MOIS sido code (`geo_units.KOSIS2MOIS`), then si/gun name → polygon.
  - The 8 metropolitan/special-city producers use the union of their assigned polygons.

| Crosswalk check | Value |
|---|---|
| Rows in `crosswalk.csv` | {len(cw)} ({int((cw.side == 'consumer').sum())} consumers + {int((cw.side == 'producer').sum())} producers) |
| Unmatched rows | **{n_unmatched}** |

## 2. Impedance
- **Measure:** great-circle (haversine) distance between polygon centroids. Centroids are computed in EPSG:5179 and the distance uses the mean Earth radius 6,371.0088 km (`00-scope.md` (e)).
- **Matrix:** {dist.shape[0]} × {dist.shape[1]} km, saved in `impedance.npz`.
- **Zero distances:** a producer and a consumer that share a polygon (a city producing for itself, or its 일반구) are 0 km apart.

## 3. Transportation LP
- **Problem:** minimize Σ x_ij · d_ij (t·km), subject to:
  - every producer ships its full 2025 production;
  - every consumer receives its full household demand;
  - x ≥ 0.
- **Solver:** `scipy.optimize.linprog(method="highs")`, with {dist.shape[0] * (dist.shape[1] + 1):,} variables and {dist.shape[0] + dist.shape[1]} equality rows.
- **Slack node "non-household disposition" (SLACK).** Supply exceeds household demand, so one sink absorbs the difference at zero cost. It stands for processing, food service, government stocks and stock change, and losses (`00-scope.md` (b)).
  - With cost 0, the LP sends to SLACK the production that is costliest to deliver to households, i.e. production far from demand.

| Result | Value |
|---|---|
| Solver status | **{status}** (status code {res.status}) |
| Objective value | {res.fun:,.0f} t·km |
| Total tonne-km delivered to households | {tkm:,.0f} t·km ({tkm/1e6:,.2f} million t·km) |
| Mean sourcing distance (demand-weighted) | **{mean_km:.1f} km** |
| Median over consuming units of their own mean sourcing distance | {per_c.km.median():.1f} km (range {per_c.km.min():.1f}–{per_c.km.max():.1f}) |
| Source units per consuming unit, median (range) | {per_c.n_src.median():.0f} ({per_c.n_src.min():.0f}–{per_c.n_src.max():.0f}) |
| **Slack node magnitude** | **{x[:, -1].sum():,.1f} t** ({x[:, -1].sum()/P.sum():.1%} of production), from {len(slack_src)} producers |
| Max relative row-sum error (producers) | {row_err:.2e} |
| Max relative column-sum error (consumers) | {col_err:.2e} |
| Non-zero flows (excluding slack) | {int((flows.to_code != SLACK).sum())} |

### Rice-sheds of the five largest consuming units
| admin_code | Consuming unit | Demand (t) | No. of source units | Top source | Share from top source | Mean sourcing km |
|---|---|---|---|---|---|---|
{sh_rows}

### Largest contributors to the slack node
| Producer | Name | Tonnes to SLACK | Share of its production |
|---|---|---|---|
{sl_rows}

## Done criterion
- Solver reports optimality: **{'MET' if ok_opt else 'NOT MET'}**.
- Row and column sums within 1e-6 relative: **{'MET' if max(row_err, col_err) <= 1e-6 else 'NOT MET'}**.
- `crosswalk.csv` has zero unmatched rows: **{'MET' if n_unmatched == 0 else 'NOT MET'}**.

## Caveats
- **Few sources per consumer.** A cost-minimizing LP gives extreme-point solutions: each consumer is served by very few sources, and nearby producers serve their own demand first. Real sourcing through government stocks and RPC brokerage is more mixed (Idea 2's stated risk; see Phase 6 for alternative mass-balanced sourcings).
- **Shared distances for 일반구.** All gu of one city share one centroid, so they have identical distance rows.
- **Metropolitan producer centroids.** A metropolitan producer's centroid is the centroid of the whole city, not of its paddy area.
"""
    open(os.path.join(ROOT, "04-flows.md"), "w", encoding="utf-8").write(md)
    print(f"status={status} obj={res.fun:.1f} tkm={tkm:.1f} mean_km={mean_km:.2f} slack={x[:, -1].sum():.1f} "
          f"row_err={row_err:.1e} col_err={col_err:.1e} unmatched={n_unmatched} done={done} t={rt:.1f}s")
    if not done:
        sys.exit(2)


if __name__ == "__main__":
    main()
