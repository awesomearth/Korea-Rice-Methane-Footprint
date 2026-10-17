"""Phase 1 - acquire the five Idea 2 inputs into data/raw/ and write 01-data-inventory.md.

Run from output/05-rice-shed/:  python code/phase1_acquire.py [--force]
Existing files are kept unless --force is given; the inventory is always rewritten
from what is on disk.
"""
import datetime as dt
import json
import os
import re
import sys

import pandas as pd
import requests
from pypdf import PdfReader

sys.path.insert(0, os.path.dirname(__file__))
import datagokr_dl  # noqa: E402
import kosis_dl  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(ROOT, "data", "raw")
FORCE = "--force" in sys.argv
UA = {"User-Agent": "Mozilla/5.0"}
YEARS = ["2023", "2024", "2025"]

IPCC_URL = "https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/4_Volume4/V4_05_Ch5_Cropland.pdf"
NID_PAGE = "http://www.gir.go.kr/home/board/read.do?menuId=36&boardId=90&boardMasterId=2"
POP_PK, POP_DETAIL = "15099158", "uddi:4ade01ad-f26b-4809-b1a1-c0f4af2bb099"  # version _20251231
BND_DGK = "https://www.data.go.kr/data/15125064/fileData.do"
BND_VW = "https://www.vworld.kr/dtmk/dtmk_ntads_s002.do?dsId=30015"
# Approved substitute for S-BND (study owner decision, 2026-10-17) and auxiliary crosswalk inputs
GB_API = "https://www.geoboundaries.org/api/current/gbOpen/KOR/{lvl}/"
SGIS_PK, SGIS_DETAIL = "15135856", "uddi:a954fa2b-22e1-4a56-9347-9f16fbcd34c7"  # SGIS 시군구경계영문 (names)


def p(*a):
    return os.path.join(RAW, *a)


def need(path):
    return FORCE or not os.path.exists(path) or os.path.getsize(path) == 0


def get_kosis():
    os.makedirs(p("kosis"), exist_ok=True)
    for tbl in ["DT_1ET0034", "DT_1ET0033", "DT_1ED0001"]:
        out = p("kosis", f"{tbl}.csv")
        if need(out):
            kosis_dl.download("101", tbl, out, YEARS)


def get_pop():
    os.makedirs(p("pop"), exist_ok=True)
    out = p("pop", "mois_bjd_pop_20251231.csv")
    if need(out):
        datagokr_dl.download(POP_PK, POP_DETAIL, out)


def get_ipcc():
    os.makedirs(p("ipcc"), exist_ok=True)
    out = p("ipcc", "V4_05_Ch5_Cropland.pdf")
    if need(out):
        r = requests.get(IPCC_URL, headers=UA, timeout=300)
        r.raise_for_status()
        open(out, "wb").write(r.content)


def get_nid():
    os.makedirs(p("gir"), exist_ok=True)
    out = p("gir", "NID2025_ko.pdf")
    if not need(out):
        return
    s = requests.Session()
    s.headers.update(UA)
    h = s.get(NID_PAGE, timeout=60).text
    link = re.search(r'href="(/home/file/readDownloadFile\.do\?[^"]+)"', h).group(1).replace("&amp;", "&")
    r = s.get("http://www.gir.go.kr" + link, headers={"Referer": NID_PAGE}, timeout=600)
    r.raise_for_status()
    open(out, "wb").write(r.content)
    json.dump({"page": NID_PAGE, "download_url": "http://www.gir.go.kr" + link},
              open(out + ".meta.json", "w"), indent=1)


def check_boundary():
    """Record why the S-BND SHP could not be fetched (no login is attempted)."""
    os.makedirs(p("boundary"), exist_ok=True)
    s = requests.Session()
    s.headers.update(UA)
    dgk = s.get(BND_DGK, timeout=60).text
    vw = s.get(BND_VW, timeout=60).text
    ev = {
        "checked": dt.date.today().isoformat(),
        "datagokr_page": BND_DGK,
        "datagokr_has_portal_file": "fn_fileDataDown(" in dgk,
        "datagokr_provision": (re.search(r"기관자체에서 다운로드[^<]*", dgk) or [None])[0],
        "vworld_page": BND_VW,
        "vworld_lists_file": "BND_SIGUNGU_PG.zip" in vw,
        "vworld_download_gated": 'loginYn == "N"' in vw and "로그인 후" in vw,
    }
    json.dump(ev, open(p("boundary", "BLOCKED_evidence.json"), "w"), ensure_ascii=False, indent=1)
    return ev


def get_geoboundaries():
    import zipfile
    for lvl, sub in [("ADM2", "gb"), ("ADM1", "gb1")]:
        meta_p = p("boundary", f"geoBoundaries-KOR-{lvl}.api.json")
        zip_p = p("boundary", f"geoBoundaries-KOR-{lvl}-all.zip")
        if need(zip_p):
            meta = requests.get(GB_API.format(lvl=lvl), headers=UA, timeout=60).json()
            json.dump(meta, open(meta_p, "w"), indent=1)
            r = requests.get(meta["staticDownloadLink"], headers=UA, timeout=600)
            r.raise_for_status()
            open(zip_p, "wb").write(r.content)
        zipfile.ZipFile(zip_p).extractall(p("boundary", sub))


FAO_URL = "https://www.fao.org/4/mb060e/mb060e.pdf"


def get_fao():
    """FAO (2011) Global food losses and food waste - Annex 4 waste shares (Phase 7, scenario S2)."""
    os.makedirs(p("fao"), exist_ok=True)
    out = p("fao", "FAO2011_global_food_losses_mb060e.pdf")
    if need(out):
        r = requests.get(FAO_URL, headers=UA, timeout=300)
        r.raise_for_status()
        open(out, "wb").write(r.content)


def get_sgis_names():
    os.makedirs(p("aux"), exist_ok=True)
    out = p("aux", "sgis_sgg_english.csv")
    if need(out):
        datagokr_dl.download(SGIS_PK, SGIS_DETAIL, out)


def kosis_rows(path):
    d = pd.read_csv(path, encoding="utf-8-sig", header=None, skiprows=2, dtype=str)
    m = json.load(open(path + ".meta.json", encoding="utf-8"))
    return len(d), m


def main():
    get_kosis()
    get_pop()
    get_ipcc()
    get_nid()
    bnd = check_boundary()
    get_geoboundaries()
    get_sgis_names()
    get_fao()
    today = dt.date.today().isoformat()
    rows = []

    def add(inp, path, nrows, years, unit, url, date=today):
        full = os.path.join(ROOT, path)
        size = os.path.getsize(full) if os.path.exists(full) else 0
        rows.append([inp, f"`{path}`", f"{size:,}", nrows, years, unit, url, date])

    for tbl, inp in [("DT_1ET0034", "1. Rice production (논벼 생산량, 정곡 92.9%): area ha, yield kg/10a, production t"),
                     ("DT_1ET0033", "1. Paddy rice cultivated area (논벼 재배면적), ha and share"),
                     ("DT_1ED0001", "2. Per capita annual grain consumption (1인당 연간 양곡소비량), kg")]:
        n, m = kosis_rows(p("kosis", f"{tbl}.csv"))
        unit = "national (곡류별 × 용도별)" if tbl == "DT_1ED0001" else "sido + si/gun (metropolitan cities as one unit)"
        add(f"{inp} [{tbl}]", f"data/raw/kosis/{tbl}.csv", f"{n} data rows",
            f"{', '.join(m['years'])} downloaded (table covers{m['containPeriod']})", unit, m["source_page"])
    pop = pd.read_csv(p("pop", "mois_bjd_pop_20251231.csv"), encoding="cp949", dtype=str)
    add("3. Resident population by 법정동, sex, single-year age (MOIS), version _20251231",
        "data/raw/pop/mois_bjd_pop_20251231.csv", f"{len(pop):,} rows",
        f"reference date {pop['기준연월'].iloc[0]}", "법정동 (aggregates to 252 si/gun/gu codes)",
        "https://www.data.go.kr/data/15099158/fileData.do (주기성 과거 데이터 → _20251231)")
    add("4a. Paddy CH4 factors: 2006 IPCC Guidelines Vol. 4 Ch. 5 (Eq. 5.1–5.3, Tables 5.11–5.14)",
        "data/raw/ipcc/V4_05_Ch5_Cropland.pdf", f"{len(PdfReader(p('ipcc', 'V4_05_Ch5_Cropland.pdf')).pages)} pages",
        "2006 (rice section pp. 5.44–5.53)", "coefficients (default)", IPCC_URL)
    add("4b. GIR 2025 국가 온실가스 인벤토리 보고서 (NID), rice section 5.4 (opened)",
        "data/raw/gir/NID2025_ko.pdf", f"{len(PdfReader(p('gir', 'NID2025_ko.pdf')).pages)} pages",
        "inventory years 1990–2023", "coefficients (national, Tier 2)", NID_PAGE)
    rows.append(["5. Si/gun/gu census boundary SHP (S-BND, BND_SIGUNGU_PG.zip)", "**BLOCKED** — no file",
                 "0", "—", "—", "si/gun/gu", f"{BND_VW} ; mirror {BND_DGK}", bnd["checked"]])

    import geopandas as gpd
    for lvl, sub, label, unit in [
            ("ADM2", "gb", "5′. **Approved substitute for S-BND**: geoBoundaries gbOpen KOR ADM2 (CC BY 3.0; source citypopulation.de)",
             "si/gun/gu, local-government level (no 일반구)"),
            ("ADM1", "gb1", "5″. Auxiliary: geoBoundaries gbOpen KOR ADM1 (Public Domain; Natural Earth), to locate ADM2 polygons by province",
             "sido")]:
        meta = json.load(open(p("boundary", f"geoBoundaries-KOR-{lvl}.api.json")))
        shp = f"data/raw/boundary/{sub}/geoBoundaries-KOR-{lvl}.shp"
        n = len(gpd.read_file(os.path.join(ROOT, shp)))
        add(label, shp, f"{n} polygons (metadata admUnitCount {meta['admUnitCount']})",
            f"boundaryYear {meta['boundaryYearRepresented']}", unit, meta["staticDownloadLink"],
            dt.date.fromtimestamp(os.path.getmtime(p("boundary", f"geoBoundaries-KOR-{lvl}-all.zip"))).isoformat())
    sg = pd.read_csv(p("aux", "sgis_sgg_english.csv"), encoding="cp949")
    add("Aux. 국가데이터처_SGIS_시군구경계영문 (Korean↔English si/gun/gu names; name crosswalk only)",
        "data/raw/aux/sgis_sgg_english.csv", f"{len(sg)} rows", "reference year 2023 (version _20240710)",
        "si/gun/gu incl. 일반구", "https://www.data.go.kr/data/15135856/fileData.do",
        dt.date.fromtimestamp(os.path.getmtime(p("aux", "sgis_sgg_english.csv"))).isoformat())

    fao = p("fao", "FAO2011_global_food_losses_mb060e.pdf")
    add("Aux. FAO (2011) Global food losses and food waste, Annex 4 waste shares (scenario S2 only)",
        "data/raw/fao/FAO2011_global_food_losses_mb060e.pdf", f"{len(PdfReader(fao).pages)} pages",
        "2011 (FBS 2007 basis)", "regional (Industrialized Asia)", FAO_URL,
        dt.date.fromtimestamp(os.path.getmtime(fao)).isoformat())

    hdr = "| Input | Local path | Bytes | Rows / pages | Year coverage | Spatial unit | Retrieval URL | Retrieval date |"
    lines = [hdr, "|" + "---|" * 8] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    md = open(os.path.join(ROOT, "code", "templates", "01-data-inventory.md.tmpl"), encoding="utf-8").read()
    md = md.replace("{{TABLE}}", "\n".join(lines)).replace("{{BND_EVIDENCE}}",
                                                            json.dumps(bnd, ensure_ascii=False, indent=1))
    open(os.path.join(ROOT, "01-data-inventory.md"), "w", encoding="utf-8").write(md)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
