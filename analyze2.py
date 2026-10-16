import sys; sys.path.insert(0, sys.argv[2]); from core import *
from scipy.stats import spearmanr
D = sys.argv[1]; g, nm = load(D)
W2, W1 = wmat(g, "2026-06-30"), wmat(g, "2026-03-31")
N = len(W2); d = (W2 > 0).sum(axis=0)
print("Q2: funds", N, "issuers", W2.shape[1], "| held by >=8 funds:", (d >= 8).sum(), "| held by exactly 1:", (d == 1).sum())
print(pd.DataFrame({"n": nm[d.index], "df": d}).sort_values("df", ascending=False).head(10).to_string())
raw, idf, nid = sim(W2, "raw"), sim(W2, "idf"), sim(W2, "noidf")
pr, pi = pairs(raw), pairs(idf)
print("\nraw top5:\n", pr.head(5).to_string(index=False)); print("\nIDF top12:\n", pi.head(12).to_string(index=False))
m = pr.merge(pi, on=["a","b"], suffixes=("_r","_i")); m["rr"] = m.s_r.rank(ascending=False); m["ri"] = m.s_i.rank(ascending=False)
print("Spearman:", round(spearmanr(m.s_r, m.s_i)[0], 3))
for a, b in [("Bridgewater","Point72"),("Point72","Soros"),("Maverick","Point72"),("Coatue","Tiger Global")]:
    r = m[((m.a==a)&(m.b==b))|((m.a==b)&(m.b==a))].iloc[0]; print(a, b, "raw", int(r.s_r), "rank", int(r.rr), "| idf", round(r.s_i,3), "rank", int(r.ri))
# strength / max sim
arr = np.array(idf.to_numpy(), copy=True); np.fill_diagonal(arr, 0); S = pd.DataFrame(arr, idf.index, idf.columns)
ex = {f: W2.loc[f, d[d == 1].index].sum() for f in W2.index}
tab = pd.DataFrame({"n_hold": (W2 > 0).sum(axis=1), "top10w": W2.apply(lambda r: r.nlargest(10).sum(), axis=1), "excl_w": pd.Series(ex), "max_sim": S.max(axis=1), "nearest": S.idxmax(axis=1), "strength": S.sum(axis=1)}).round(3)
print(tab.sort_values("max_sim", ascending=False).to_string())
for cut in (0.05, 0.10, 0.15):
    G, cc = comps(idf, cut); big = [c for c in cc if len(c) > 1]
    print(f"\ncut {cut}: edges {G.number_of_edges()}, connected nodes {sum(len(c) for c in big)}, isolates {sum(1 for c in cc if len(c)==1)}"); print([c for c in big])
print("\n-- Q1 vs Q2 --"); idf1 = sim(W1, "idf"); p1 = pairs(idf1); print("Q1 top8:\n", p1.head(8).to_string(index=False))
t1 = set(map(frozenset, p1.head(15)[["a","b"]].values)); t2 = set(map(frozenset, pi.head(15)[["a","b"]].values)); print("top15 overlap Q1/Q2:", len(t1 & t2))
mm = p1.merge(pi, on=["a","b"]); print("Spearman Q1 vs Q2 pair sims:", round(spearmanr(mm.s_x, mm.s_y)[0], 3))
print("\n-- hubs dropped (held by >=8 funds) --"); Wd = wmat(g, "2026-06-30", drop_df_ge=8); pd_ = pairs(sim(Wd, "idf")); print(Wd.shape[1], "issuers left"); print(pd_.head(8).to_string(index=False))
print("\n-- no-IDF weight cosine top5 --"); print(pairs(nid).head(5).to_string(index=False))
# shared stocks Coatue-Tiger-Appaloosa
def shared(a, b, k=6):
    s = W2.loc[[a, b]].T; s = s[(s > 0).all(axis=1)]; s["m"] = s.min(axis=1); return [(nm[i], round(float(s.loc[i, a]*100),1), round(float(s.loc[i, b]*100),1)) for i in s.sort_values("m", ascending=False).index[:k]], len(s)
print("\nCoatue-Tiger shared:", shared("Coatue","Tiger Global")); print("Appaloosa-Coatue shared:", shared("Appaloosa","Coatue")); print("Berkshire-DailyJournal:", shared("Berkshire","Daily Journal"))
