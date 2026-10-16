import json, sys, time, urllib.request
import os
UA = os.environ["SEC_UA"]  # e.g. "Your Name your@email.com" (SEC requires a contact in the User-Agent)
OUT = sys.argv[1]
CIKS = [1067983,1350694,1336528,1649339,1656456,1040273,1167483,1135730,1037389,1423053,1029160,1536411,1061768,1079114,921669,1061165,1103804,934639,1603466,1747057,1791786,1345471,783412,1056831,1549575,1112520,1709323,1166559,1105838,1273087,1056288,1544598,1006438,1812000]
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()
res = {}
for c in CIKS:
    try:
        d = json.loads(get(f"https://data.sec.gov/submissions/CIK{c:010d}.json"))
        r = d["filings"]["recent"]
        found = {}
        for i, f in enumerate(r["form"]):
            if f == "13F-HR" and r["reportDate"][i] in ("2026-06-30", "2026-03-31"):
                found.setdefault(r["reportDate"][i], r["accessionNumber"][i])
        res[c] = {"name": d["name"], "acc": found}
        print(c, d["name"], found, flush=True)
    except Exception as e:
        print(c, "ERR", e, flush=True)
    time.sleep(0.25)
json.dump(res, open(OUT, "w"), indent=1)
