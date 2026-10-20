"""Track-only DC resistance between two pads of a net (copper zones ignored => upper bound for pour nets). Needs numpy+scipy (uv env)."""
import json, math, sys
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spl
RHO = 1.68e-8  # ohm*m copper at 20C
d = json.load(open(sys.argv[1])); net, a, b = sys.argv[2], sys.argv[3], sys.argv[4]; amps = float(sys.argv[5])
key = lambda x, y, l: (round(x, 3), round(y, 3), l)
idx, edges = {}, []
def node(k): return idx.setdefault(k, len(idx))
for t in d["tracks"]:
    if t["net"] != net: continue
    L = math.hypot(t["x2"] - t["x1"], t["y2"] - t["y1"]) * 1e-3
    R = RHO * L / (t["w"] * 1e-3 * d["thickness_mm"][t["layer"]] * 1e-3)
    edges.append((node(key(t["x1"], t["y1"], t["layer"])), node(key(t["x2"], t["y2"], t["layer"])), R))
for v in d["vias"]:
    if v["net"] != net: continue
    ka, kb = key(v["x"], v["y"], "F.Cu"), key(v["x"], v["y"], "B.Cu")
    edges.append((node(ka), node(kb), 0.5e-3))  # ~0.5 mOhm barrel (rough placeholder)
pad = {}
for p in d["pads"]:
    if p["net"] == net:
        pad[f'{p["ref"]}.{p["num"]}'] = key(p["x"], p["y"], p["layer"])
        if p["tht"]: edges.append((node(key(p["x"], p["y"], "F.Cu")), node(key(p["x"], p["y"], "B.Cu")), 0.5e-3))
n = len(idx); G = sp.lil_matrix((n, n))
for i, j, R in edges:
    g = 1 / max(R, 1e-9); G[i, i] += g; G[j, j] += g; G[i, j] -= g; G[j, i] -= g
def snap(k, tol=0.6):  # pad centre -> nearest copper node on the same layer (tracks need not end exactly on the pad centre)
    if k in idx: return idx[k]
    c = min((m for m in idx if m[2] == k[2]), key=lambda m: math.hypot(m[0]-k[0], m[1]-k[1]))
    assert math.hypot(c[0]-k[0], c[1]-k[1]) <= tol, f"pad {k} not within {tol} mm of any {net} copper"
    return idx[c]
ia, ib = snap(pad[a]), snap(pad[b])
I = np.zeros(n); I[ia] = amps; I[ib] = -amps
keep = [k for k in range(n) if k != ib]
v = np.zeros(n); v[keep] = spl.spsolve(G.tocsr()[keep][:, keep].tocsc(), I[keep])
print(f"{net}: {a} -> {b}: R = {v[ia]/amps*1e3:.1f} mOhm, drop at {amps} A = {v[ia]*1e3:.1f} mV  (nodes={n}, segments={len(edges)})")
