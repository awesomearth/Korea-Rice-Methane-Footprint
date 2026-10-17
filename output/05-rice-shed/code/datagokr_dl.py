"""Download a data.go.kr file-data version (current or a periodic past version) without login.

Replays the portal's own download flow: POST /tcs/dss/selectFileDataDownload.do returns the
attachment id, then /cmm/cmm/fileDownload.do serves the file.

Usage: python datagokr_dl.py PUBLIC_DATA_PK PUBLIC_DATA_DETAIL_PK OUT_FILE
  PUBLIC_DATA_PK         e.g. 15099158
  PUBLIC_DATA_DETAIL_PK  the version's uddi:... id (data-public-pk on the past-data row)
"""
import json
import sys

import requests

BASE = "https://www.data.go.kr"


def download(pk, detail_pk, out, detail_sn="1"):
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0"
    page = f"{BASE}/data/{pk}/fileData.do"
    s.get(page, timeout=60)
    r = s.post(f"{BASE}/tcs/dss/selectFileDataDownload.do",
               data={"publicDataDetailPk": detail_pk, "publicDataPk": pk, "atchFileId": "",
                     "fileDetailSn": detail_sn, "publicDataTyCode": "PR0051"},
               headers={"Referer": page, "X-Requested-With": "XMLHttpRequest"}, timeout=60)
    r.raise_for_status()
    j = r.json() if r.text.strip().startswith("{") else json.loads(r.text)
    if not j.get("status"):
        raise RuntimeError(f"portal refused: {j}")
    info = j["dataSetFileDetailInfo"]
    url = (f"{BASE}/cmm/cmm/fileDownload.do?atchFileId={j['atchFileId']}"
           f"&fileDetailSn={j['fileDetailSn']}&insertDataPrcus=N")
    f = s.get(url, headers={"Referer": page}, timeout=600)
    f.raise_for_status()
    with open(out, "wb") as fh:
        fh.write(f.content)
    meta = {"publicDataPk": pk, "publicDataDetailPk": detail_pk, "dataNm": info.get("dataNm"),
            "download_url": url, "page": page, "bytes": len(f.content),
            "content_disposition": f.headers.get("Content-Disposition")}
    with open(out + ".meta.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=1)
    return meta


if __name__ == "__main__":
    print(json.dumps(download(*sys.argv[1:4]), ensure_ascii=False, indent=1))
