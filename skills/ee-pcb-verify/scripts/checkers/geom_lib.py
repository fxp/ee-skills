"""Pure-Python/numpy geometry for the ``geometry`` checker. Reads ``geometry.json`` (see export_geometry.py); no pcbnew.

Units are mm in KiCad board coordinates (y grows downward). Nothing here knows about a particular board or rule.
"""
from __future__ import annotations

import heapq
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

EPS = 1e-6


# ------------------------------------------------------------------ primitives
def edges_of(poly: list, closed: bool = True) -> np.ndarray:
    """(n,2,2) array of the segments of a polygon / polyline."""
    p = np.asarray(poly, dtype=float)
    if len(p) < 2:
        return np.zeros((0, 2, 2))
    q = np.roll(p, -1, axis=0) if closed else p[1:]
    return np.stack([p if closed else p[:-1], q], axis=1)


def seg_seg_min(A: np.ndarray, B: np.ndarray) -> float:
    """Minimum distance between two sets of segments ((n,2,2) and (m,2,2)); 0 if any pair intersects."""
    if len(A) == 0 or len(B) == 0:
        return math.inf
    a0, a1 = A[:, None, 0, :], A[:, None, 1, :]
    b0, b1 = B[None, :, 0, :], B[None, :, 1, :]

    def pt_seg(p, s0, s1):
        d = s1 - s0
        l2 = np.maximum((d * d).sum(-1), 1e-18)
        t = np.clip(((p - s0) * d).sum(-1) / l2, 0.0, 1.0)
        return np.linalg.norm(p - (s0 + t[..., None] * d), axis=-1)

    best = np.minimum.reduce([pt_seg(a0, b0, b1), pt_seg(a1, b0, b1), pt_seg(b0, a0, a1), pt_seg(b1, a0, a1)])

    def cross(o, p, q):
        return (p[..., 0] - o[..., 0]) * (q[..., 1] - o[..., 1]) - (p[..., 1] - o[..., 1]) * (q[..., 0] - o[..., 0])

    inter = (cross(a0, a1, b0) * cross(a0, a1, b1) < 0) & (cross(b0, b1, a0) * cross(b0, b1, a1) < 0)
    best = np.where(inter, 0.0, best)
    return float(best.min())


def poly_poly_dist(P: list, Q: list) -> float:
    """Distance between two simple polygons (0 when they overlap or one contains the other)."""
    d = seg_seg_min(edges_of(P), edges_of(Q))
    if d == 0.0:
        return 0.0
    if point_in_poly(P[0], Q) or point_in_poly(Q[0], P):
        return 0.0
    return d


def point_in_poly(pt, poly) -> bool:
    x, y = pt
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-18) + xi:
            inside = not inside
        j = i
    return inside


def point_seg_dist(p, a, b) -> float:
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy
    t = 0.0 if l2 < 1e-18 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / l2))
    return math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy))


def point_poly_dist(pt, poly) -> float:
    """0 inside the polygon, else distance to its boundary."""
    if point_in_poly(pt, poly):
        return 0.0
    e = edges_of(poly)
    return min(point_seg_dist(pt, s[0], s[1]) for s in e)


def bbox_of(poly) -> tuple:
    a = np.asarray(poly, dtype=float)
    return float(a[:, 0].min()), float(a[:, 1].min()), float(a[:, 0].max()), float(a[:, 1].max())


def bbox_overlap(a, b, pad=0.0) -> bool:
    return not (a[2] + pad < b[0] or b[2] + pad < a[0] or a[3] + pad < b[1] or b[3] + pad < a[1])


def rect_poly(x0, y0, x1, y1) -> list:
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def stadium_poly(a, b, width, n=8) -> list:
    """Outline of a track segment: capsule of diameter ``width`` around a-b."""
    ax, ay = a
    bx, by = b
    ang = math.atan2(by - ay, bx - ax)
    r = width / 2
    pts = []
    for k in range(n + 1):  # cap around b
        t = ang - math.pi / 2 + math.pi * k / n
        pts.append([bx + r * math.cos(t), by + r * math.sin(t)])
    for k in range(n + 1):  # cap around a
        t = ang + math.pi / 2 + math.pi * k / n
        pts.append([ax + r * math.cos(t), ay + r * math.sin(t)])
    return pts


def circle_poly(c, r, n=24) -> list:
    return [[c[0] + r * math.cos(2 * math.pi * k / n), c[1] + r * math.sin(2 * math.pi * k / n)] for k in range(n)]


def arc_points(start, mid, end, max_step_deg=4.0) -> list:
    """Sample a 3-point arc into a polyline (inclusive of start and end)."""
    (x1, y1), (x2, y2), (x3, y3) = start, mid, end
    d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    if abs(d) < 1e-12:
        return [list(start), list(end)]
    ux = ((x1**2 + y1**2) * (y2 - y3) + (x2**2 + y2**2) * (y3 - y1) + (x3**2 + y3**2) * (y1 - y2)) / d
    uy = ((x1**2 + y1**2) * (x3 - x2) + (x2**2 + y2**2) * (x1 - x3) + (x3**2 + y3**2) * (x2 - x1)) / d
    r = math.hypot(x1 - ux, y1 - uy)
    a1, a2, a3 = (math.atan2(y - uy, x - ux) for y, x in ((y1, x1), (y2, x2), (y3, x3)))

    def norm(a):
        while a < 0:
            a += 2 * math.pi
        return a % (2 * math.pi)

    ccw = norm(a2 - a1) < norm(a3 - a1)
    sweep = norm(a3 - a1) if ccw else -norm(a1 - a3)
    n = max(2, int(abs(math.degrees(sweep)) / max_step_deg))
    return [[ux + r * math.cos(a1 + sweep * k / n), uy + r * math.sin(a1 + sweep * k / n)] for k in range(n + 1)]


def polyline_len(pts) -> float:
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))


# ------------------------------------------------------------------ board model
class Board:
    def __init__(self, g: dict):
        self.g = g
        self.parts: dict[str, dict] = {f["ref"]: f for f in g["footprints"]}
        self.tracks = g["tracks"]
        self.vias = g["vias"]
        self.zones = g["zones"]
        self.nets = g["nets"]
        self._outline = None
        self._graphs: dict[str, NetGraph] = {}

    @classmethod
    def load(cls, path: Path) -> "Board":
        return cls(json.loads(Path(path).read_text()))

    # ---- pads
    def pads(self, ref: str, num: str | None = None) -> list[dict]:
        out = []
        for p in self.parts[ref]["pads"]:
            if num is None or p["num"] == str(num):
                out.append(dict(p, ref=ref))
        return out

    def pad(self, ref: str, num: str) -> dict:
        ps = self.pads(ref, num)
        if not ps:
            raise KeyError(f"pad {ref}.{num} not found")
        return ps[0]

    def all_pads(self):
        for ref, f in self.parts.items():
            for p in f["pads"]:
                yield dict(p, ref=ref)

    def has_pad(self, ref: str, num: str) -> bool:
        return ref in self.parts and bool(self.pads(ref, num))

    # ---- outline
    @property
    def outline(self) -> dict:
        if self._outline is None:
            self._outline = build_outline(self.g["edge_cuts"])
        return self._outline

    def edge_dist_poly(self, poly) -> float:
        return seg_seg_min(edges_of(poly), self.outline["edges"])

    def edge_dist_point(self, pt) -> float:
        return min(point_seg_dist(pt, s[0], s[1]) for s in self.outline["edges"])

    def graph(self, net: str) -> "NetGraph":
        if net not in self._graphs:
            self._graphs[net] = NetGraph(self, net)
        return self._graphs[net]

    def net_tracks(self, net: str, layer: str | None = None) -> list[dict]:
        return [t for t in self.tracks if t["net"] == net and (layer is None or t["layer"] == layer)]

    def net_vias(self, net: str) -> list[dict]:
        return [v for v in self.vias if v["net"] == net]

    def fill_polys(self, layer: str, net: str | None = None) -> list[dict]:
        """Filled copper polygons ({outline, holes, net}) of all zones on ``layer`` (optionally one net)."""
        out = []
        for z in self.zones:
            if z["rule_area"] or (net is not None and z["net"] != net):
                continue
            f = z.get("filled", {}).get(layer)
            if f:
                out += [dict(p, net=z["net"], zone=z.get("name", "")) for p in f["polys"]]
        return out

    def courtyard_polys(self, ref: str) -> list[list]:
        return [c["outline"] for c in self.parts[ref]["courtyard"]]

    def part_bbox(self, ref: str):
        f = self.parts[ref]
        return f["courtyard_bbox"] or f["bbox"]


def build_outline(edge_cuts: list) -> dict:
    """Chain Edge.Cuts items into loops; returns segment array, loop count and whether everything closed."""
    pieces = []
    for s in edge_cuts:
        if s["shape"] == "Line" or s["shape"] == "Rect":
            if s["shape"] == "Rect":
                (x0, y0), (x1, y1) = s["start"], s["end"]
                pieces.append([[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]])
            else:
                pieces.append([list(s["start"]), list(s["end"])])
        elif s["shape"] == "Arc":
            pieces.append(arc_points(s["start"], s["mid"], s["end"]))
        elif s["shape"] == "Circle":
            pieces.append(circle_poly(s["center"], s["radius"]) + [circle_poly(s["center"], s["radius"])[0]])
        else:
            for poly in s.get("polygon", []):
                o = poly["outline"]
                pieces.append(o + [o[0]])
    # chain pieces by endpoints
    tol = 1e-3
    remaining = [p for p in pieces]
    loops = []
    while remaining:
        cur = remaining.pop(0)
        grew = True
        while grew:
            grew = False
            for i, p in enumerate(remaining):
                for cand in (p, p[::-1]):
                    if math.dist(cur[-1], cand[0]) < tol:
                        cur = cur + cand[1:]
                        remaining.pop(i)
                        grew = True
                        break
                if grew:
                    break
        loops.append(cur)
    closed = all(math.dist(l[0], l[-1]) < tol for l in loops) and len(loops) >= 1
    segs = np.concatenate([edges_of(l, closed=False) for l in loops]) if loops else np.zeros((0, 2, 2))
    return {"edges": segs, "loops": loops, "closed": closed, "n_loops": len(loops)}


# ------------------------------------------------------------------ connectivity
class NetGraph:
    """Copper connectivity of one net from tracks + vias + pad contact (zone fills are NOT included).

    Nodes are points (x, y, layer) rounded to 1 um, ``('pad', ref, num, k)`` for pads. Edges carry kind/length/width/layer.
    """

    def __init__(self, board: Board, net: str):
        self.net = net
        self.adj: dict = defaultdict(list)
        self.tracks = board.net_tracks(net)
        self.vias = board.net_vias(net)

        def key(p, layer):
            return (round(p[0], 3), round(p[1], 3), layer)

        def link(a, b, kind, length=0.0, width=None, layer=None, tid=None):
            e = {"kind": kind, "len": length, "width": width, "layer": layer, "tid": tid}
            self.adj[a].append((b, dict(e, a=a, b=b)))
            self.adj[b].append((a, dict(e, a=b, b=a)))

        ends = []
        for i, t in enumerate(self.tracks):
            a, b = key(t["start"], t["layer"]), key(t["end"], t["layer"])
            link(a, b, "track", t["length"], t["width"], t["layer"], i)
            ends += [(a, t["start"], t["layer"], i), (b, t["end"], t["layer"], i)]
        via_nodes = []
        for v in self.vias:
            top, bot = v["layers"]
            a, b = key(v["pos"], top), key(v["pos"], bot)
            link(a, b, "via")
            via_nodes += [(a, v["pos"], v["diameter"] / 2, top), (b, v["pos"], v["diameter"] / 2, bot)]
        # a track end inside a via annulus / T-junction onto another segment of the same net+layer
        for node, pt, layer, tid in ends:
            for vn, vp, r, vl in via_nodes:
                if vl == layer and vn != node and math.dist(pt, vp) <= r + 1e-3:
                    link(node, vn, "contact")
            for j, t in enumerate(self.tracks):
                if j == tid or t["layer"] != layer:
                    continue
                if node in (key(t["start"], layer), key(t["end"], layer)):
                    continue
                if point_seg_dist(pt, t["start"], t["end"]) <= 5e-3 + 0.0:
                    link(node, key(t["start"], layer), "track", math.dist(pt, t["start"]), t["width"], layer, j)
                    link(node, key(t["end"], layer), "track", math.dist(pt, t["end"]), t["width"], layer, j)
        # pads
        self.pad_nodes: dict = {}
        for p in board.all_pads():
            if p["net"] != net:
                continue
            k = ("pad", p["ref"], p["num"], len([n for n in self.pad_nodes if n[1:3] == (p["ref"], p["num"])]))
            self.pad_nodes[k] = p
            layers = [{"F": "F.Cu", "B": "B.Cu"}[c] for c in p["copper"]]
            poly = p["poly"] or circle_poly(p["pos"], 0.05)
            bb = bbox_of(poly)
            for node, pt, layer, tid in ends:
                if layer in layers and bb[0] - 5e-3 <= pt[0] <= bb[2] + 5e-3 and bb[1] - 5e-3 <= pt[1] <= bb[3] + 5e-3 \
                        and (point_in_poly(pt, poly) or point_poly_dist(pt, poly) <= 5e-3):
                    link(k, node, "pad", math.dist(p["pos"], pt))
            for vn, vp, r, vl in via_nodes:
                if vl in layers and point_in_poly(vp, poly):
                    link(k, vn, "pad", math.dist(p["pos"], vp))
            if len(layers) == 2:  # through-hole pads join both layers at the pad centre
                link(key(p["pos"], layers[0]), key(p["pos"], layers[1]), "via")
                link(k, key(p["pos"], layers[0]), "pad")
                link(k, key(p["pos"], layers[1]), "pad")

    def pad_key(self, ref: str, num: str):
        return [k for k in self.pad_nodes if k[1] == ref and k[2] == str(num)]

    def path(self, a, b) -> dict | None:
        """Shortest copper path (by track length) between pad a=(ref,num) and pad b; None when not connected by tracks/vias."""
        ka, kb = self.pad_key(*a), self.pad_key(*b)
        if not ka or not kb:
            return None
        dist = {k: 0.0 for k in ka}
        prev: dict = {}
        pq = [(0.0, i, k) for i, k in enumerate(ka)]
        heapq.heapify(pq)
        seen = set()
        goal = None
        c = len(pq)
        while pq:
            d, _, u = heapq.heappop(pq)
            if u in seen:
                continue
            seen.add(u)
            if u in kb:
                goal = u
                break
            for v, e in self.adj[u]:
                nd = d + e["len"] + 1e-9
                if nd < dist.get(v, math.inf):
                    dist[v] = nd
                    prev[v] = (u, e)
                    c += 1
                    heapq.heappush(pq, (nd, c, v))
        if goal is None:
            return None
        edges = []
        u = goal
        while u in prev:
            u, e = prev[u]
            edges.append(e)
        edges.reverse()
        return summarize_path(edges, self.tracks)

    def components(self) -> dict:
        """Connected components over all nodes; returns {node: component id}."""
        comp = {}
        cid = 0
        for s in list(self.adj):
            if s in comp:
                continue
            stack = [s]
            comp[s] = cid
            while stack:
                u = stack.pop()
                for v, _ in self.adj[u]:
                    if v not in comp:
                        comp[v] = cid
                        stack.append(v)
            cid += 1
        return comp

    def pad_component(self, ref: str, num: str):
        comp = self.components()
        ks = self.pad_key(ref, num)
        return comp.get(ks[0]) if ks and ks[0] in comp else None


def summarize_path(edges: list, tracks: list) -> dict:
    tr = [e for e in edges if e["kind"] == "track"]
    length = sum(e["len"] for e in tr)
    contact = sum(e["len"] for e in edges if e["kind"] == "pad")
    widths = [e["width"] for e in tr]
    vias = sum(1 for e in edges if e["kind"] == "via" and e["a"][2] != e["b"][2])
    corners = []
    prev_dir = None
    for e in tr:
        t = tracks[e["tid"]]
        # direction from a->b as traversed
        a, b = e["a"], e["b"]
        d = (b[0] - a[0], b[1] - a[1])
        if math.hypot(*d) < 1e-9:
            continue
        if prev_dir is not None:
            dot = (d[0] * prev_dir[0] + d[1] * prev_dir[1]) / (math.hypot(*d) * math.hypot(*prev_dir))
            corners.append(round(math.degrees(math.acos(max(-1.0, min(1.0, dot)))), 2))
        prev_dir = d
    return {"length_mm": round(length + contact, 4), "track_length_mm": round(length, 4), "min_width_mm": min(widths) if widths else None, "vias": vias, "corners_deg": corners,
            "max_corner_deg": max(corners) if corners else 0.0, "segments": len(tr), "layers": sorted({e["layer"] for e in tr if e["layer"]}),
            "track_ids": [e["tid"] for e in tr]}
