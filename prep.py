import pandas as pd, numpy as np, re, sys
D = sys.argv[1]
df = pd.read_csv(f"{D}/raw/holdings_raw.csv", dtype={"cusip": str, "cik": str})
n0 = len(df)
df = df[df.putcall.isna()].copy(); n_opt = n0 - len(df)
df["value"] = pd.to_numeric(df.value, errors="coerce"); df["shares"] = pd.to_numeric(df.shares, errors="coerce")
# unit fix: some filers report value in $ thousands -> detect with implied price
fix = []
for (f, p), g in df.groupby(["fund", "period"]):
    px = (g.value / g.shares.replace(0, np.nan)).median()
    if px < 2: df.loc[g.index, "value"] *= 1000; fix.append((f, p, round(px, 3)))
print("unit-fixed filings:", fix)
etf = re.compile(r"ISHARES|SPDR|SELECT SECTOR|VANECK|VANGUARD (WORLD|INDEX|INTL|TAX|SCOTTSDALE|MALVERN)|\bETF\b|INVESCO QQQ|PROSHARES|DBX|WISDOMTREE (TR|FD)|ROUNDHILL|AMPLIFY|GSCI|SILVER TR|GOLD TR|BITCOIN TR|GRAYSCALE|DIREXION|GLOBAL X", re.I)
isetf = df.issuer.fillna("").str.contains(etf)
print("ETF rows dropped:", isetf.sum()); df = df[~isetf]
df["cusip"] = df.cusip.str.upper().str.strip()
df = df.groupby(["fund", "period", "cusip"], as_index=False).agg(value=("value", "sum"), issuer=("issuer", "first"))
df["w"] = df.value / df.groupby(["fund", "period"]).value.transform("sum")
names = df.groupby("cusip").issuer.agg(lambda s: s.str.upper().mode().iloc[0])
df["issuer"] = df.cusip.map(names)
df.to_csv(f"{D}/holdings_clean.csv", index=False)
print("options dropped:", n_opt, "| clean rows:", len(df), "| funds:", df.fund.nunique(), "| unique cusips:", df.cusip.nunique())
print(df.groupby(["fund", "period"]).size().unstack().to_string())
