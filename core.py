import pandas as pd, numpy as np, itertools, warnings
warnings.filterwarnings("ignore")
SHORT = {"BERKSHIRE HATHAWAY INC":"Berkshire","Bridgewater Associates, LP":"Bridgewater","Appaloosa LP":"Appaloosa","Third Point LLC":"Third Point","TIGER GLOBAL MANAGEMENT LLC":"Tiger Global","COATUE MANAGEMENT LLC":"Coatue","SOROS FUND MANAGEMENT LLC":"Soros","Duquesne Family Office LLC":"Duquesne","BAUPOST GROUP LLC/MA":"Baupost","ICAHN CARL C":"Icahn","LONE PINE CAPITAL LLC":"Lone Pine","VIKING GLOBAL INVESTORS LP":"Viking","MAVERICK CAPITAL LTD":"Maverick","Point72 Asset Management, L.P.":"Point72","D1 Capital Partners L.P.":"D1","Elliott Investment Management L.P.":"Elliott","TRIAN FUND MANAGEMENT, L.P.":"Trian","DAILY JOURNAL CORP":"Daily Journal","FAIRHOLME CAPITAL MANAGEMENT LLC":"Fairholme","Dalal Street, LLC":"Dalal St","AKRE CAPITAL MANAGEMENT LLC":"Akre","Himalaya Capital Management LLC":"Himalaya","GATES FOUNDATION TRUST":"Gates Fdn","ROBOTTI ROBERT":"Robotti"}
def load(D):
    df = pd.read_csv(f"{D}/holdings_clean.csv", dtype={"cusip": str})
    df["f"] = df.fund.map(SHORT); df["iss"] = df.cusip.str[:6]
    nm = df.groupby("iss").issuer.agg(lambda s: s.mode().iloc[0])
    g = df.groupby(["f", "period", "iss"], as_index=False).value.sum()
    g["w"] = g.value / g.groupby(["f", "period"]).value.transform("sum")
    return g, nm
def wmat(g, p, drop_df_ge=None):
    W = g[g.period == p].pivot_table(index="f", columns="iss", values="w", fill_value=0.0)
    if drop_df_ge:
        keep = (W > 0).sum(axis=0) < drop_df_ge; W = W.loc[:, keep]
    return W
def sim(W, mode="idf"):
    B = (W > 0).astype(float); N = len(W); d = B.sum(axis=0).values
    if mode == "raw": return pd.DataFrame(B.values @ B.values.T, W.index, W.index)
    wt = np.log(N / d) if mode == "idf" else np.ones(W.shape[1])
    X = W.values * wt; X = X / np.linalg.norm(X, axis=1, keepdims=True).clip(1e-12)
    return pd.DataFrame(X @ X.T, W.index, W.index)
def pairs(M):
    r = [(a, b, M.loc[a, b]) for a, b in itertools.combinations(M.index, 2)]
    return pd.DataFrame(r, columns=["a", "b", "s"]).sort_values("s", ascending=False).reset_index(drop=True)
def edges(M, cut):
    p = pairs(M); return p[p.s >= cut]
def comps(M, cut):
    import networkx as nx
    G = nx.Graph(); G.add_nodes_from(M.index); G.add_edges_from([(a, b) for a, b, s in edges(M, cut).itertuples(index=False)])
    return G, [sorted(c) for c in nx.connected_components(G)]
