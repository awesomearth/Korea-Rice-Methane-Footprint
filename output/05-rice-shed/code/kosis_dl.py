"""Download a KOSIS statistical table as CSV without an API key.

Replays the request the KOSIS table viewer (statHtml) sends when the user clicks
"다운로드 -> CSV": the default item/class selections are read from the table page
(g_jsonStatInfo), a fieldList is built for the requested years, then
/statHtml/downGrid.do returns a temporary file name that /statHtml/downNormal.do serves.

Usage: python kosis_dl.py ORG_ID TBL_ID OUT_CSV [YEAR ...]
With no YEAR, the table's default period is used.
"""
import json
import re
import sys

import requests

BASE = "https://kosis.kr"


def table_info(s, org, tbl):
    url = (f"{BASE}/statHtml/statHtmlContent.do?orgId={org}&tblId={tbl}"
           "&language=ko&vw_cd=MT_ZTITLE&dbUser=NSI.")
    h = s.get(url, timeout=60).text
    m = re.search(r"var g_jsonStatInfo\s*=\s*'(.*?)';\s*\n", h)
    if not m:
        raise RuntimeError("g_jsonStatInfo not found in table page")
    # every input of the viewer's ParamInfo form; the server rejects requests that omit any
    i = h.find('id="ParamInfo"')
    blank = {}
    for t in re.findall(r"<input[^>]*>", h[i:h.find("</form>", i)]):
        n = re.search(r'name="([^"]*)"', t)
        if n and not re.search(r'type="(radio|checkbox)"', t):
            v = re.search(r'value="([^"]*)"', t)
            blank.setdefault(n.group(1), v.group(1) if v else "")
    return url, json.loads(m.group(1)), blank


def download(org, tbl, out, years=None):
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0"
    ref, info, blank = table_info(s, org, tbl)
    pinfo = info["periodInfo"]
    prd_se = info["periodStr"].split("#")[0] or "Y"
    if not years:
        years = pinfo.get("defaultList" + prd_se) or [pinfo.get("defaultEnd" + prd_se)]
    fl = [{"targetId": "PRD", "targetValue": "", "prdValue": f"{prd_se}," + "".join(f"{y}," for y in years) + "@"}]
    for it in info["itemInfo"]["itmList"]:
        fl.append({"targetId": "ITM_ID", "targetValue": it["itmId"], "prdValue": ""})
    n_class_cells = 1
    for ci in info["classInfoList"]:
        codes = [x.split("#")[1] for x in ci["defaultItmList"]]
        # all levels selected (classAllList empty means the default list is the full list)
        allc = [x.split("#")[1] for x in ci.get("classAllList") or []] or codes
        for c in allc:
            fl.append({"targetId": f"OV_L{ci['sn']}_ID", "targetValue": c, "prdValue": ""})
        n_class_cells *= len(allc)
    cells = n_class_cells * len(info["itemInfo"]["itmList"])
    form = dict(blank)
    form.update({
        "orgId": org, "tblId": tbl, "language": "ko", "dbUser": "NSI.", "vwCd": "MT_ZTITLE",
        "statId": info.get("statId", ""), "contextPath": "/statHtml",
        "fieldList": json.dumps(fl, ensure_ascii=False), "periodStr": prd_se,
        "funcPrdSe": prd_se, "isFirst": "N", "doAnal": "N", "pubLog": "4", "usePivot": "N",
        "tableType": "default", "colAxis": "TIME,ITEM", "rowAxis": ",".join(
            ci["classId"] for ci in info["classInfoList"]),
        "itemMultiply": str(cells), "startNum": "1", "endNum": str(cells),
        "expDash": "Y", "smblYn": "Y", "enableLevelExpr": "Y", "prdSort": "asc",
        "dataOpt": "cdko", "view": "csv", "viewKind": "2", "viewSubKind": "2_3", "downGridCsvType": "UTF-8",
        "tblNm": info.get("tblNm", ""), "tblEngNm": info.get("tblEngNm", ""),
        "existStblCmmtKor": info.get("existStblCmmtKor", "N"), "inheritYn": "N",
        "selectType": "", "periodCo": "", "cmmtChk": "Y", "selectAllFlag": "N",
        "classAllArr": json.dumps([{"objVarId": ci["classId"], "ovlSn": str(ci["sn"])}
                                   for ci in info["classInfoList"]]),
        "classSet": json.dumps([{"objVarId": ci["classId"], "ovlSn": str(ci["sn"]), "visible": "true"}
                                for ci in info["classInfoList"]]),
        "defaulPeriodArr": json.dumps({prd_se: [int(y) for y in years]}),
        "defaultItmArr": json.dumps([{"data": [i["itmId"] for i in info["itemInfo"]["itmList"]]}]),
        "orderStr": ",".join([f"OV_L{ci['sn']}_ID" for ci in info["classInfoList"]] + ["TIME", "CHAR_ITM_ID"]),
    })
    hdr = {"Referer": ref, "X-Requested-With": "XMLHttpRequest"}
    # the viewer first renders the grid (html.do); its response carries the logSeq
    # token (element 4) that downGrid.do requires
    view = dict(form, view="table", viewKind="", viewSubKind="", isFirst="Y", logSeq="")
    rh = s.post(f"{BASE}/statHtml/html.do", data=view, headers=hdr, timeout=120)
    rh.raise_for_status()
    jr = rh.json()
    if "result" not in jr:
        raise RuntimeError("html.do: " + json.dumps(jr, ensure_ascii=False)[:400])
    form["logSeq"] = str(jr["result"][4])
    r = s.post(f"{BASE}/statHtml/downGrid.do", data=form, headers=hdr, timeout=120)
    r.raise_for_status()
    fname = r.json()["file"]
    form["file"] = fname
    r2 = s.post(f"{BASE}/statHtml/downNormal.do", data=form, headers={"Referer": ref}, timeout=120)
    r2.raise_for_status()
    if r2.content[:15].lower().startswith(b"<!doctype") or b"<html" in r2.content[:200].lower():
        raise RuntimeError("KOSIS returned HTML instead of CSV")
    with open(out, "wb") as f:
        f.write(r2.content)
    meta = {"orgId": org, "tblId": tbl, "tblNm": info.get("tblNm"), "years": years,
            "containPeriod": info.get("containPeriod"), "renewalDate": info.get("renewalDate"),
            "source_page": f"{BASE}/statHtml/statHtml.do?orgId={org}&tblId={tbl}",
            "items": [(i["itmId"], i["scrKor"], i.get("scrEng")) for i in info["itemInfo"]["itmList"]],
            "bytes": len(r2.content)}
    with open(out + ".meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    return meta


if __name__ == "__main__":
    org, tbl, out = sys.argv[1:4]
    print(json.dumps(download(org, tbl, out, sys.argv[4:] or None), ensure_ascii=False, indent=1))
