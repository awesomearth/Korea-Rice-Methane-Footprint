"""Phase 6 (P6) - Monte Carlo over sourcing and CH4 factors, 1,000 draws.

Inputs : Phase 4 LP (data/processed/impedance.npz, demand.csv, supply_intensity.csv),
         Phase 3 factors (data/processed/ch4_factors.json; IPCC ranges in ipcc2006_v4c5_rice_factors.csv),
         Phase 5 baseline (data/processed/footprint.csv) for the error metrics
Outputs: data/processed/mc_results.csv, data/processed/mc_draws_per_capita.npz, 06-uncertainty.md
Run from output/05-rice-shed/:  python code/phase6_uncertainty.py
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from phase4_flows import solve  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
R = lambda *a: os.path.join(ROOT, *a)
N_DRAWS = 1000
SIGMA_LN = 0.5          # sourcing perturbation: d_ij * LogNormal(0, SIGMA_LN), study design choice
SENS_SIGMAS = (0.25, 1.0)
N_SENS = 200
SEED = 20251231
POP_SPLIT = 125_000     # paper's city-size threshold (01-method-summary.md §4)

# NID water-regime classes -> IPCC Table 5.12/5.13 rows whose relative error range is applied
SFW_IPCC = {"SFw_CF": "SFw_CF", "SFw_1x_lt1wk": "SFw_single", "SFw_1x_1to2wk": "SFw_single", "SFw_2x": "SFw_multiple"}


def split_normal(rng, mean, lo, hi, size=None):
    """IPCC p. 5.52: ranges 'are defined as the standard deviation about the mean'. Asymmetric ranges are
    treated as a two-piece normal: sd_low = mean - lo below the mean, sd_high = hi - mean above it."""
    z = rng.standard_normal(size)
    v = np.where(z < 0, mean + z * (mean - lo), mean + z * (hi - mean))
    return np.maximum(v, 1e-6)


def factor_multiplier(rng, fac, ipcc):
    """One draw of EF_nat / EF_nat_baseline using IPCC relative ranges on the NID factors."""
    rel = lambda k: split_normal(rng, 1.0, ipcc[k]["low"] / ipcc[k]["value"], ipcc[k]["high"] / ipcc[k]["value"])
    m_efc = rel("EFc")
    m_sfw = {c: rel(SFW_IPCC[c]) for c in SFW_IPCC}
    m_sfp = {c: rel(c) for c in ("SFp_lt180", "SFp_gt180", "SFp_fl30")}
    e = split_normal(rng, ipcc["SFo_exponent"]["value"], ipcc["SFo_exponent"]["low"], ipcc["SFo_exponent"]["high"])
    e0 = ipcc["SFo_exponent"]["value"]
    nid = fac["nid_factors"]
    sfo = {"none": 1.0,
           "straw": nid["SFo_straw"] ** (e / e0),   # (1 + ROA*CFOA)^e with (1+ROA*CFOA) implied by NID SFo at e0
           "green": nid["SFo_green"] ** (e / e0)}
    num = 0.0
    den = 0.0
    for u in fac["sub_units"]:
        ef = nid["EFc"] * m_efc * nid[u["sfw"]] * m_sfw[u["sfw"]] * nid[u["sfp"]] * m_sfp[u["sfp"]] * sfo[u["om"]]
        num += ef * u["area_ha"]
        den += u["area_ha"]
    return (num / den) / fac["ef_nat"]


def per_capita_from_flows(x, I, pop):
    return (x[:, :-1] * I[:, None]).sum(0) * 1000 / pop


def main():
    t0 = time.time()
    z = np.load(R("data/processed/impedance.npz"), allow_pickle=True)
    s = pd.read_csv(R("data/processed/supply_intensity.csv"), dtype={"admin_code": str})
    d = pd.read_csv(R("data/processed/demand.csv"), dtype={"admin_code": str})
    base = pd.read_csv(R("data/processed/footprint.csv"), dtype={"admin_code": str})
    fac = json.load(open(R("data/processed/ch4_factors.json")))
    ipcc = fac["ipcc_factors"]
    assert list(z["prod_codes"]) == list(s.admin_code) and list(z["cons_codes"]) == list(d.admin_code)
    dist, P, D = z["dist_km"], s.production_t.values.astype(float), d.rice_demand_t.values.astype(float)
    I, pop = s.kgco2e_per_kg.values, d.population.values.astype(float)
    f0 = base.set_index("admin_code").loc[d.admin_code, "per_capita_kgco2e"].values
    rng = np.random.default_rng(SEED)

    pc_src = np.empty((N_DRAWS, len(D)))
    k = np.empty(N_DRAWS)
    n_fail = 0
    for t in range(N_DRAWS):
        res, x = solve(P, D, dist * rng.lognormal(0.0, SIGMA_LN, dist.shape))
        if res.status != 0:
            n_fail += 1
            pc_src[t] = np.nan
        else:
            pc_src[t] = per_capita_from_flows(x, I, pop)
        k[t] = factor_multiplier(rng, fac, ipcc)
    pc = pc_src * k[:, None]
    runtime_main = time.time() - t0

    sens = {}
    for sg in SENS_SIGMAS:
        r2 = np.random.default_rng(SEED + int(sg * 100))
        arr = np.array([per_capita_from_flows(solve(P, D, dist * r2.lognormal(0, sg, dist.shape))[1], I, pop)
                        for _ in range(N_SENS)])
        sens[sg] = float(np.mean(np.abs(arr - f0) / f0))
    runtime = time.time() - t0

    ape = np.abs(pc - f0) / f0
    ape_src = np.abs(pc_src - f0) / f0
    mape_u = np.nanmean(ape, axis=0)
    mape_src_u = np.nanmean(ape_src, axis=0)
    big = pop > POP_SPLIT
    out = pd.DataFrame({"admin_code": d.admin_code, "name": d.name, "population": d.population,
                        "baseline_per_capita": f0,
                        "mean": np.nanmean(pc, 0), "sd": np.nanstd(pc, 0, ddof=1),
                        "p5": np.nanpercentile(pc, 5, 0), "p95": np.nanpercentile(pc, 95, 0),
                        "mape": mape_u,
                        "sourcing_only_mean": np.nanmean(pc_src, 0), "sourcing_only_sd": np.nanstd(pc_src, 0, ddof=1),
                        "sourcing_only_p5": np.nanpercentile(pc_src, 5, 0),
                        "sourcing_only_p95": np.nanpercentile(pc_src, 95, 0),
                        "sourcing_only_mape": mape_src_u})
    out["width_p5_p95"] = out.p95 - out.p5
    out["sourcing_only_width"] = out.sourcing_only_p95 - out.sourcing_only_p5
    out.to_csv(R("data/processed/mc_results.csv"), index=False, encoding="utf-8")
    np.savez_compressed(R("data/processed/mc_draws_per_capita.npz"), combined=pc, sourcing_only=pc_src, k=k,
                        codes=d.admin_code.values)

    mape_all, mape_src = float(np.nanmean(mape_u)), float(np.nanmean(mape_src_u))
    k_mape = float(np.mean(np.abs(k - 1)))
    complete = n_fail == 0 and out[["p5", "p95"]].notna().all().all()
    w = out.sort_values("width_p5_p95", ascending=False).head(10)
    ws = out.sort_values("sourcing_only_width", ascending=False).head(10)
    row = lambda r: (f"| {r.admin_code} | {r.name} | {r.population:,} | {r.baseline_per_capita:.1f} | {r.mean:.1f} | "
                     f"{r.p5:.1f} | {r.p95:.1f} | {r.width_p5_p95:.1f} |")
    rows_ = lambda r: (f"| {r.admin_code} | {r.name} | {r.population:,} | {r.baseline_per_capita:.1f} | "
                       f"{r.sourcing_only_p5:.1f} | {r.sourcing_only_p95:.1f} | {r.sourcing_only_width:.1f} | {r.sourcing_only_mape:.1%} |")
    md = f"""# 06 — Uncertainty (Idea 2, Phase 6 / P6)

Generated by `code/phase6_uncertainty.py`.
- **Inputs:** the Phase 4 LP (`impedance.npz`, `demand.csv`, `supply_intensity.csv`), the Phase 3 factors (`ch4_factors.json`) and the Phase 5 baseline (`footprint.csv`).
- **Outputs:** `data/processed/mc_results.csv` (per unit: mean, sd, p5, p95, MAPE; plus sourcing-only columns) and `data/processed/mc_draws_per_capita.npz` (all draws).

**Draws completed: {N_DRAWS - n_fail} of {N_DRAWS}** (LP failures: {n_fail}); seed {SEED}. **Runtime: {runtime_main:.0f} s** for the 1,000-draw run, {runtime:.0f} s including the sensitivity runs.

## Design
Each draw combines two independent perturbations.

**(a) Sourcing.** Every producer→consumer distance is multiplied by an independent LogNormal(0, σ = {SIGMA_LN}) factor, and the balanced LP of Phase 4 is re-solved.
- Every re-solve is mass-balanced: each producer ships its full output, each consumer receives its full demand, and the slack is unchanged.
- The randomized impedance gives alternative cost-plausible sourcing patterns. This stands in for the paper's sourcing Monte Carlo (`01-method-summary.md` §4).
- σ is a **study design choice**, not a sourced value. A sensitivity on it is reported below.
- Zero distances (self-supply within a polygon) stay zero under multiplicative noise.

**(b) CH4 factors.** Relative multipliers are drawn from the IPCC 2006 Vol. 4 Ch. 5 uncertainty ranges and applied to the Korean (NID) factors:
- EFc: Table 5.11, p. 5.49;
- SFw: Table 5.12, p. 5.49. NID continuous → IPCC continuous; NID 1× aeration → IPCC single aeration; NID ≥ 2× → IPCC multiple aeration;
- SFp: Table 5.13, p. 5.50;
- the SFo exponent, 0.54–0.64: Eq. 5.3, p. 5.50. Straw and green-manure SFo are rescaled as SFo^(e/0.59).

IPCC p. 5.52 states that the ranges "are defined as the standard deviation about the mean". Each asymmetric range is therefore sampled as a two-piece normal (sd_low = mean − low, sd_high = high − mean), truncated at > 0. One multiplier is drawn per factor class per draw. The national EF_nat is recomputed over the 36 NID sub-units, and t_eff (activity data) is held at its Phase 3 value. Every producing unit shares EF_nat, so the factor draw scales all intensities by a common multiplier k.

**Metric.** MAPE_j = mean over draws of |f_jd − f_j0| / f_j0, where f_j0 is the Phase 5 baseline per capita footprint. "MAPE across units" is the unweighted mean of MAPE_j.

## Results
| Metric | Combined (sourcing + factors) | Sourcing only (k = 1) |
|---|---|---|
| **MAPE across all {len(out)} units** | **{mape_all:.1%}** | **{mape_src:.1%}** |
| MAPE, units with population > 125,000 (n = {int(big.sum())}) | {float(np.nanmean(mape_u[big])):.1%} | {float(np.nanmean(mape_src_u[big])):.1%} |
| MAPE, units with population ≤ 125,000 (n = {int((~big).sum())}) | {float(np.nanmean(mape_u[~big])):.1%} | {float(np.nanmean(mape_src_u[~big])):.1%} |
| Median unit p5–p95 width (kg CO2e/person) | {out.width_p5_p95.median():.1f} | {out.sourcing_only_width.median():.1f} |
| National factor multiplier k: mean, p5–p95 | {k.mean():.3f}, {np.percentile(k, 5):.3f}–{np.percentile(k, 95):.3f} (mean \\|k−1\\| = {k_mape:.1%}) | — |

**Sensitivity of the sourcing-only MAPE to σ** ({N_SENS} draws each): σ = 0.25 → {sens[0.25]:.1%}; σ = {SIGMA_LN} → {mape_src:.1%} (main run); σ = 1.0 → {sens[1.0]:.1%}.

**Interpretation**
- **Factor uncertainty dominates.** The IPCC baseline-EF range (−38% / +69% relative) moves every unit together. It drives the combined MAPE, but it does not change the ranking of units.
- **Sourcing uncertainty is what decides between-unit differences.** It is much smaller, and it is {'larger' if np.nanmean(mape_src_u[big]) > np.nanmean(mape_src_u[~big]) else 'smaller'} for units above 125,000 people ({float(np.nanmean(mape_src_u[big])):.1%} vs {float(np.nanmean(mape_src_u[~big])):.1%}). Large urban units import from several distant producers whose ranking shifts under perturbed costs. Many small rural units supply themselves from their own polygon at 0 km, which multiplicative noise cannot displace ({int((base.set_index('admin_code').loc[d.admin_code, 'mean_sourcing_km'].values[~big] == 0).sum())} of {int((~big).sum())} small units have a 0 km baseline sourcing distance). This is the opposite of the paper's pattern of lower error in large cities.

### 10 widest p5–p95 intervals (combined, kg CO2e per person)
| admin_code | Unit | Population | Baseline | MC mean | p5 | p95 | Width |
|---|---|---|---|---|---|---|---|
{chr(10).join(row(r) for r in w.itertuples())}

### 10 widest sourcing-only intervals
| admin_code | Unit | Population | Baseline | p5 | p95 | Width | Sourcing MAPE |
|---|---|---|---|---|---|---|---|
{chr(10).join(rows_(r) for r in ws.itertuples())}

## Done criterion
- 1,000 draws completed, with draw count and runtime stated: **{'MET' if n_fail == 0 else 'NOT MET'}** ({N_DRAWS - n_fail} draws, {runtime_main:.0f} s).
- Every unit has a p5/p95 band: **{'MET' if complete else 'NOT MET'}** ({int(out[['p5', 'p95']].notna().all(axis=1).sum())} of {len(out)}).
"""
    open(R("06-uncertainty.md"), "w", encoding="utf-8").write(md)
    print(f"draws={N_DRAWS - n_fail} fail={n_fail} mape={mape_all:.4f} mape_src={mape_src:.4f} "
          f"big={np.nanmean(mape_u[big]):.4f}/{np.nanmean(mape_src_u[big]):.4f} small={np.nanmean(mape_u[~big]):.4f}/"
          f"{np.nanmean(mape_src_u[~big]):.4f} k={k.mean():.3f} sens={sens} t_main={runtime_main:.0f}s t={runtime:.0f}s")


if __name__ == "__main__":
    main()
