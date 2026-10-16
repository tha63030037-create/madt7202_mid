import json, sys, time, os, urllib.request
import xml.etree.ElementTree as ET
import os
UA = os.environ["SEC_UA"]  # e.g. "Your Name your@email.com" (SEC requires a contact in the User-Agent)
RES = json.load(open(sys.argv[1])); OUT = sys.argv[2]
DROP = {"1037389","1423053","1273087","1056288","1544598","1812000","1336528","1649339","1079114","1006438"}
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()
rows = []; log = []
for cik, v in RES.items():
    if cik in DROP or len(v["acc"]) < 2: continue
    for period, acc in sorted(v["acc"].items()):
        nd = acc.replace("-", "")
        try:
            idx = json.loads(get(f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{nd}/index.json")); time.sleep(0.25)
            cands = [i["name"] for i in idx["directory"]["item"] if i["name"].lower().endswith(".xml") and i["name"] != "primary_doc.xml"]
            done = False
            for name in cands:
                raw = get(f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{nd}/{name}"); time.sleep(0.25)
                root = ET.fromstring(raw)
                if not root.tag.lower().endswith("informationtable"): continue
                d = os.path.join(OUT, f"{cik}_{period}"); os.makedirs(d, exist_ok=True)
                open(os.path.join(d, "infotable.xml"), "wb").write(raw)
                n = 0
                for it in root:
                    g = lambda t: (it.find(".//{*}" + t).text if it.find(".//{*}" + t) is not None else None)
                    rows.append([cik, v["name"], period, g("nameOfIssuer"), g("cusip"), g("value"), g("sshPrnamt"), g("putCall") or ""])
                    n += 1
                log.append((cik, v["name"], period, acc, n)); print(cik, v["name"], period, n, flush=True); done = True; break
            if not done: print(cik, period, "NO INFOTABLE", cands, flush=True)
        except Exception as e:
            print(cik, period, "ERR", e, flush=True)
import csv
with open(os.path.join(OUT, "holdings_raw.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["cik","fund","period","issuer","cusip","value","shares","putcall"]); w.writerows(rows)
json.dump(log, open(os.path.join(OUT, "fetch_log.json"), "w"))
print("rows", len(rows))
