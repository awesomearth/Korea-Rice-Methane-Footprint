"""Attach geometry to the 252 consuming and 156 producing units (shared by Phases 4, 6, 8).

Geometry: geoBoundaries KOR ADM2 (approved substitute for S-BND, 00-scope.md (e)), plus one
OpenStreetMap patch for 영광군, which is absent from geoBoundaries (228 of 229 polygons).
Names are joined through the SGIS Korean<->English si/gun/gu table; duplicated romanized
names (e.g. six "Jung-gu") are resolved by province, using the majority province of
already-identified neighbouring polygons.
"""
import json
import os
import re

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import shape
from shapely.ops import unary_union

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
R = lambda *a: os.path.join(ROOT, *a)
CRS = 5179
EARTH_R_KM = 6371.0088  # IUGG mean Earth radius
# ISO 3166-2:KR province codes (geoBoundaries ADM1 shapeISO) -> MOIS 2025 sido code prefix
ISO2MOIS = {"11": "11", "26": "26", "27": "27", "28": "28", "29": "29", "30": "30", "31": "31", "50": "36",
            "41": "41", "42": "51", "43": "43", "44": "44", "45": "52", "46": "46", "47": "47", "48": "48",
            "49": "50"}
# KOSIS DT_1ET0034 sido code -> MOIS sido code (names checked in kosis_sido_map)
KOSIS2MOIS = {"11": "11", "21": "26", "22": "27", "23": "28", "24": "29", "25": "30", "26": "31", "29": "36",
              "31": "41", "32": "51", "33": "43", "34": "44", "35": "52", "36": "46", "37": "47", "38": "48",
              "39": "50"}
SIDO_ALIAS = {"강원도": "51", "전라북도": "52", "제주도": "50"}


def key(x):
    x = re.sub(r"\[.*?\]", "", str(x)).strip().lower()
    x = re.sub(r"[\s\-]", "", x)
    return re.sub(r"(si|gun|gu|city)$", "", x)


def sido_codes():
    pop = pd.read_csv(R("data/raw/pop/mois_bjd_pop_20251231.csv"), encoding="cp949", dtype=str,
                      usecols=["법정동코드", "시도명"])
    m = dict(zip(pop["시도명"], pop["법정동코드"].str[:2]))
    m.update(SIDO_ALIAS)
    return m


def sgis_cities(s2c):
    sg = pd.read_csv(R("data/raw/aux/sgis_sgg_english.csv"), encoding="cp949")
    sg["sido"] = sg["시도명"].map(s2c)
    assert sg["sido"].notna().all()
    sg["city_ko"] = sg["시군구명"].str.split().str[0]
    sg["city_en"] = sg["시군구영문"].str.split().str[-1]
    sej = sg["시도명"].str.startswith("세종")
    sg.loc[sej, "city_ko"], sg.loc[sej, "city_en"] = "세종시", "Sejong City"
    c = sg.drop_duplicates(["sido", "city_ko"])[["sido", "city_ko", "city_en"]].reset_index(drop=True)
    c["key"] = c["city_en"].map(key)
    return c


def boundary_polygons():
    """Return polygons (EPSG:5179) with sido, city_ko, city_en, source, match_method."""
    s2c = sido_codes()
    cities = sgis_cities(s2c)
    g = gpd.read_file(R("data/raw/boundary/gb/geoBoundaries-KOR-ADM2.shp")).to_crs(CRS)
    g["source"] = "geoBoundaries KOR ADM2 (2020)"
    a1 = gpd.read_file(R("data/raw/boundary/gb1/geoBoundaries-KOR-ADM1.shp")).to_crs(CRS)
    a1 = a1.rename(columns={"shapeISO": "iso1"})[["iso1", "geometry"]]
    # OSM patch for 영광군 (absent from geoBoundaries): clip the maritime OSM boundary to land
    # (ADM1 land polygons) and remove overlap with existing ADM2 polygons.
    osm = json.load(open(R("data/raw/boundary/osm/yeonggwang_nominatim.json"), encoding="utf-8"))[0]
    y = gpd.GeoSeries([shape(osm["geojson"])], crs=4326).to_crs(CRS).iloc[0]
    y = y.intersection(unary_union(a1.geometry)).difference(unary_union(g.geometry))
    g = pd.concat([g, gpd.GeoDataFrame({"shapeName": ["Yeonggwang-gun"], "shapeID": [f"OSM-relation-{osm['osm_id']}"],
                                        "source": ["OpenStreetMap relation %s (ODbL), land-clipped" % osm["osm_id"]]},
                                       geometry=[y], crs=CRS)], ignore_index=True)
    g["key"] = g["shapeName"].map(key)
    rp = g.copy()
    rp["geometry"] = g.representative_point()
    j = gpd.sjoin(rp[["geometry"]], a1, how="left", predicate="within")
    j = j[~j.index.duplicated()]
    miss = j["iso1"].isna()
    if miss.any():
        nn = gpd.sjoin_nearest(rp.loc[miss, ["geometry"]], a1)
        nn = nn[~nn.index.duplicated()]
        j.loc[miss, "iso1"] = nn["iso1"]
    g["sido_adm1"] = j["iso1"].str[3:].map(ISO2MOIS)
    g["sido"], g["city_ko"], g["city_en"], g["match_method"] = None, None, None, None
    taken = set()

    def assign(i, c, how):
        g.loc[i, ["sido", "city_ko", "city_en", "match_method"]] = [c.sido, c.city_ko, c.city_en, how]
        taken.add((c.sido, c.city_ko))

    # A: romanized name unique among SGIS cities
    for i, r in g.iterrows():
        cand = cities[cities.key == r.key]
        if len(cand) == 1:
            assign(i, cand.iloc[0], "unique name")
    # B: duplicates resolved by majority province of identified touching neighbours (iterate)
    for _ in range(10):
        changed = False
        for i, r in g[g.city_ko.isna()].iterrows():
            cand = cities[(cities.key == r.key) & ~cities.apply(lambda c: (c.sido, c.city_ko) in taken, axis=1)]
            if cand.empty:
                continue
            nb = g[(g.index != i) & g.city_ko.notna() & (g.distance(r.geometry) < 200)]
            votes = nb["sido"].value_counts()
            best = [s for s in votes.index if s in set(cand.sido)]
            if best:
                assign(i, cand[cand.sido == best[0]].iloc[0], f"duplicate name; neighbours' province ({votes[best[0]]} of {len(nb)})")
                changed = True
        if not changed:
            break
    # C: anything left, fall back to the ADM1 province of the representative point
    for i, r in g[g.city_ko.isna()].iterrows():
        cand = cities[(cities.key == r.key) & (cities.sido == r.sido_adm1)]
        cand = cand[~cand.apply(lambda c: (c.sido, c.city_ko) in taken, axis=1)]
        if len(cand) == 1:
            assign(i, cand.iloc[0], "duplicate name; ADM1 province")
    unmatched_cities = cities[~cities.apply(lambda c: (c.sido, c.city_ko) in taken, axis=1)]
    return g, cities, unmatched_cities


def centroid_lonlat(geoms):
    c = gpd.GeoSeries(geoms, crs=CRS).centroid.to_crs(4326)
    return np.c_[c.x.values, c.y.values]


def haversine(a, b):
    """a: (n,2) lon/lat, b: (m,2) lon/lat -> (n,m) km."""
    lon1, lat1 = np.radians(a[:, 0])[:, None], np.radians(a[:, 1])[:, None]
    lon2, lat2 = np.radians(b[:, 0])[None, :], np.radians(b[:, 1])[None, :]
    h = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * EARTH_R_KM * np.arcsin(np.sqrt(h))


def attach_units():
    """Crosswalk consuming and producing units to polygons; return (cons, prod, polys, crosswalk)."""
    polys, cities, unmatched_cities = boundary_polygons()
    s2c = sido_codes()
    d = pd.read_csv(R("data/processed/demand.csv"), dtype={"admin_code": str})
    s = pd.read_csv(R("data/processed/supply_intensity.csv"), dtype={"admin_code": str})
    pop = pd.read_csv(R("data/raw/pop/mois_bjd_pop_20251231.csv"), encoding="cp949", dtype=str,
                      usecols=["법정동코드", "시도명", "시군구명"]).drop_duplicates(subset=None)
    pop["admin_code"] = pop["법정동코드"].str[:5]
    nm = pop.drop_duplicates("admin_code").set_index("admin_code")
    pidx = {(r.sido, r.city_ko): i for i, r in polys[polys.city_ko.notna()].iterrows()}
    rows = []
    cons_poly = []
    for r in d.itertuples():
        sido = r.admin_code[:2]
        sgg = nm.loc[r.admin_code, "시군구명"] if isinstance(nm.loc[r.admin_code, "시군구명"], str) else ""
        city = "세종시" if sido == "36" else sgg.split()[0]
        i = pidx.get((sido, city))
        how = "parent city polygon (일반구)" if (" " in sgg) else "own polygon"
        rows.append(dict(side="consumer", unit_code=r.admin_code, unit_name=r.name, sido=sido, city_ko=city,
                         shapeName=polys.loc[i, "shapeName"] if i is not None else None,
                         shapeID=polys.loc[i, "shapeID"] if i is not None else None,
                         method=how if i is not None else None,
                         status="matched" if i is not None else "UNMATCHED",
                         reason="" if i is not None else f"no polygon for ({sido}, {city})"))
        cons_poly.append(i)
    prod_geom = []
    for r in s.itertuples():
        if len(r.admin_code) == 2:  # metropolitan/special city reported as a whole
            sido = KOSIS2MOIS[r.admin_code]
            idx = list(polys.index[polys.sido == sido])
            geom = unary_union(polys.loc[idx, "geometry"]) if idx else None
            rows.append(dict(side="producer", unit_code=r.admin_code, unit_name=r.name, sido=sido, city_ko="(all)",
                             shapeName="; ".join(polys.loc[idx, "shapeName"]),
                             shapeID="; ".join(polys.loc[idx, "shapeID"]),
                             method=f"union of {len(idx)} polygons assigned to sido {sido}",
                             status="matched" if idx else "UNMATCHED", reason="" if idx else "no polygons"))
        else:
            sido = KOSIS2MOIS[r.admin_code[:2]]
            city = r.name.split()[-1]
            i = pidx.get((sido, city))
            geom = polys.loc[i, "geometry"] if i is not None else None
            rows.append(dict(side="producer", unit_code=r.admin_code, unit_name=r.name, sido=sido, city_ko=city,
                             shapeName=polys.loc[i, "shapeName"] if i is not None else None,
                             shapeID=polys.loc[i, "shapeID"] if i is not None else None,
                             method="own polygon" if i is not None else None,
                             status="matched" if i is not None else "UNMATCHED",
                             reason="" if i is not None else f"no polygon for ({sido}, {city})"))
        prod_geom.append(geom)
    cw = pd.DataFrame(rows)
    cons_ll = centroid_lonlat([polys.loc[i, "geometry"] if i is not None else None for i in cons_poly])
    prod_ll = centroid_lonlat(prod_geom)
    cw["centroid_lon"] = np.r_[cons_ll[:, 0], prod_ll[:, 0]]
    cw["centroid_lat"] = np.r_[cons_ll[:, 1], prod_ll[:, 1]]
    d["poly_idx"] = cons_poly
    return d, s, polys, cw, cons_ll, prod_ll, unmatched_cities, prod_geom
