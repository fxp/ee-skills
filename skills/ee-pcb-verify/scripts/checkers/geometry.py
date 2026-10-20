"""``geometry`` checker: catalog rule id -> function over ``geometry.json`` (+ the board design file) -> pass/fail + evidence.

A generalised placement audit: nothing here names a reference designator. Which pads, nets and keep-outs a
rule applies to comes from ``design/<board>.yaml``; thresholds come from the catalog parameter named in
``bindings/geometry.yaml`` (or, where the catalog says "project-set", from ``project_thresholds`` in the design file,
and the result carries that provenance in ``threshold.source``).
"""
from __future__ import annotations

import math
import re
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import common as C
from . import geom_lib as G


# ------------------------------------------------------------------ context + output
@dataclass
class GCtx:
    board: G.Board
    design: dict
    geometry_sha: str
    design_sha: str
    board_sha: str
    kicad_version: str

    def thr_from(self, rule: dict, spec) -> C.Threshold:
        """spec: 'param_name' | {param, op?, scale?} | {design: key} | {rule: ID, param: name}"""
        if isinstance(spec, str):
            return C.resolve_threshold(rule, spec)
        if "design" in spec:
            d = self.design["project_thresholds"][spec["design"]]
            return C.Threshold(op=d["op"], value=d["value"], unit=d["unit"], source="design_yaml", source_param=spec["design"], note=d["source"])
        if "rule" in spec:
            return C.resolve_threshold(C.load_catalog()[spec["rule"]], spec["param"], scale=spec.get("scale", 1.0), op=spec.get("op"))
        if "text" in spec:
            return C.manual_threshold(spec.get("op", "=="), spec.get("value", 0), spec.get("unit", "count"), "rule_text", spec["text"])
        return C.resolve_threshold(rule, spec["param"], scale=spec.get("scale", 1.0), op=spec.get("op"))


class Out:
    def __init__(self):
        self.subs: list[dict] = []
        self.evidence: list[dict] = []
        self.not_evaluated: list[str] = []

    def add(self, key: str, measured, thr: C.Threshold | None, ok: bool | None = None, negate: bool = False, **extra):
        if ok is None:
            ok = (not thr.holds(measured)) if negate else thr.holds(measured)
            if negate:
                extra["interpretation"] = f"catalog op '{thr.op}' is the alarm level: pass iff measured is NOT {thr.op} {thr.value}"
        tj = thr.as_json() if thr else None
        if tj and negate:
            tj["negated"] = True        # the catalog op is the alarm level; the check passes when it does NOT hold
        self.subs.append({"key": key, "measured": measured, "threshold": tj, "ok": bool(ok), **extra})

    def ev(self, **kw):
        self.evidence.append(kw)


def rnd(x, n=3):
    return None if x is None else round(float(x), n)


# ------------------------------------------------------------------ small selectors
def is_fiducial(f: dict) -> bool:
    return f["ref"].startswith("FID") or f["value"].lower() == "fiducial" or any((p.get("prop") or "").startswith("fiducial") for p in f["pads"])


def is_testpoint(f: dict) -> bool:
    return f["ref"].startswith("TP") or any(p.get("prop") == "testpoint" for p in f["pads"])


FARAD = {"pF": 1e-12, "nF": 1e-9, "uF": 1e-6, "F": 1.0}


def to_farad(thr: "C.Threshold") -> float:
    return thr.value * FARAD[thr.unit]


def pad_center(p):
    return tuple(p["pos"])


def pad_label(p):
    return f"{p['ref']}.{p['num']}"


def cap_value_f(value: str) -> float | None:
    m = re.fullmatch(r"\s*([0-9]*\.?[0-9]+)\s*([pnuµm]?)F?\s*", value)
    if not m:
        return None
    return float(m.group(1)) * {"p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "m": 1e-3, "": 1.0}[m.group(2)]


def polys_contain(polys: list[dict], pt) -> bool:
    for pl in polys:
        bb = pl.get("_bb") or pl.setdefault("_bb", G.bbox_of(pl["outline"]))
        if bb[0] <= pt[0] <= bb[2] and bb[1] <= pt[1] <= bb[3] and G.point_in_poly(pt, pl["outline"]) \
                and not any(G.point_in_poly(pt, h) for h in pl["holes"]):
            return True
    return False


def poly_area(poly) -> float:
    a = np.asarray(poly, dtype=float)
    return abs(float(np.dot(a[:, 0], np.roll(a[:, 1], -1)) - np.dot(a[:, 1], np.roll(a[:, 0], -1)))) / 2


def track_copper_poly(t: dict):
    return G.stadium_poly(t["start"], t["end"], t["width"])


# ------------------------------------------------------------------ checks
CHECKS = {}


def check(fn):
    CHECKS[fn.__name__] = fn
    return fn


@check
def smd_pad_edge_distance(ctx: GCtx, rule: dict, P: dict, o: Out):
    """DFM-FLR-006: SMD pad (non-fiducial) to Edge.Cuts, and the fiducial clearance zone to Edge.Cuts."""
    b = ctx.board
    worst = []
    for p in b.all_pads():
        f = b.parts[p["ref"]]
        if p["attr"] != "smd" or is_fiducial(f) or not p["poly"]:
            continue
        worst.append((b.edge_dist_poly(p["poly"]), pad_label(p)))
    worst.sort()
    o.add("smd_pads", rnd(worst[0][0]) if worst else None, P["pad"], ok=(worst[0][0] >= P["pad"].value - 1e-9) if worst else True,
          worst_pad=worst[0][1] if worst else None, n_pads=len(worst))
    for d, lab in worst:
        if d < P["pad"].value - 1e-9:
            o.ev(refs=[lab.split(".")[0]], pad=lab, distance_mm=rnd(d), message=f"SMD pad {lab} is {d:.3f} mm from the board edge")
    R = P["fiducial_zone_diameter"].value / 2
    fz = []
    for ref, f in b.parts.items():
        if is_fiducial(f):
            fz.append((b.edge_dist_point(f["pos"]) - R, ref))
    fz.sort()
    o.add("fiducial_clearance_zone", rnd(fz[0][0]) if fz else None, P["fiducial"], ok=(fz[0][0] >= P["fiducial"].value - 1e-9) if fz else True,
          zone_radius_mm=R, worst_fiducial=fz[0][1] if fz else None, n_fiducials=len(fz))
    for d, ref in fz:
        if d < P["fiducial"].value - 1e-9:
            o.ev(refs=[ref], distance_mm=rnd(d), message=f"fiducial {ref} clearance zone is {d:.3f} mm from the board edge")


@check
def fiducials(ctx: GCtx, rule: dict, P: dict, o: Out):
    """DFM-PLC-003: count, copper diameter, mask opening, copper-free circle, edge clearance, asymmetry."""
    b = ctx.board
    fids = [f for f in b.parts.values() if is_fiducial(f) and f["side"] == "F"]
    o.add("count", len(fids), P["count"])
    dias, openings, free, edge, others_info = [], [], [], [], []
    R = P["free"].value / 2
    for f in fids:
        pad = f["pads"][0]
        dias.append(pad["size"][0])
        m = pad["mask_margin"] if pad.get("mask_margin") is not None else b.g.get("mask_expansion_mm", 0.0)
        openings.append(pad["size"][0] + 2 * m)
        c = tuple(f["pos"])
        side = "F.Cu" if f["side"] == "F" else "B.Cu"
        cand, other = [], []   # (clearance from the fiducial centre to the copper, description); same layer decides, other layers are informational
        for t in b.tracks:
            (cand if t["layer"] == side else other).append((G.point_seg_dist(c, t["start"], t["end"]) - t["width"] / 2, f"track {t['net']} on {t['layer']}"))
        for v in b.vias:
            cand.append((math.dist(c, v["pos"]) - v["diameter"] / 2, f"via {v['net']}"))
        for p in b.all_pads():
            if p["ref"] != f["ref"] and p["poly"] and side[0] in p["copper"]:
                cand.append((G.point_poly_dist(c, p["poly"]), f"pad {pad_label(p)}"))
        for pl in b.fill_polys(side):
            cand.append((0.0 if polys_contain([pl], c) else min(G.point_seg_dist(c, s_[0], s_[1]) for s_ in G.edges_of(pl["outline"])), f"{pl['net']} pour on {side}"))
        dmin, what = min(cand)
        if other:
            others_info.append((f["ref"],) + min(other))
        free.append((dmin, f["ref"], what))
        edge.append((b.edge_dist_point(c) - R, f["ref"]))
    o.add("copper_diameter", sorted(set(dias)), P["diameter"], ok=all(abs(d - P["diameter"].value) < 1e-6 for d in dias) if dias else False)
    o.add("mask_opening_diameter", rnd(min(openings)) if openings else None, P["opening"], ok=all(x >= P["opening"].value - 1e-9 for x in openings) if openings else False)
    fm = min(free) if free else (None, None, None)
    o.add("copper_free_radius_mm", rnd(fm[0]), C.manual_threshold(">=", R, "mm", "catalog", f"{P['free'].source_param} / 2 = {R} mm (diameter {P['free'].value} mm), copper on the fiducial's own layer (the mask opening and the camera view are on that face)"),
          ok=(fm[0] >= R - 1e-9) if free else False, nearest_fiducial=fm[1], nearest_object=fm[2],
          other_layer_nearest=[{"fiducial": r, "mm": rnd(d), "object": w} for r, d, w in others_info if d < R])
    for d, r, what in free:
        if d < R - 1e-9:
            o.ev(refs=[r], message=f"{what} is {d:.3f} mm from the centre of {r} (needs >= {R} mm copper-free)")
    em = min(edge) if edge else (None, None)
    o.add("edge_clearance_mm", rnd(em[0]), P["edge"], ok=(em[0] >= P["edge"].value - 1e-9) if edge else False, worst_fiducial=em[1])
    if len(fids) >= 3:
        cs = [tuple(f["pos"]) for f in fids]
        ds = sorted(math.dist(cs[i], cs[j]) for i in range(len(cs)) for j in range(i + 1, len(cs)))
        tol = ctx.design["fiducial_distance_tolerance_mm"]
        gap = min(ds[i + 1] - ds[i] for i in range(len(ds) - 1))
        o.add("pairwise_distance_min_gap_mm", rnd(gap), C.manual_threshold(">", tol, "mm", "design_yaml", "numerical tolerance for 'distances differ'"), ok=gap > tol,
              distances=[rnd(d, 2) for d in ds])
    else:
        o.add("pairwise_distance_min_gap_mm", None, None, ok=len(fids) >= 2, note="asymmetry needs >= 3 fiducials")
    o.not_evaluated.append("silkscreen/text inside the 2.0 mm circle (silk is not in geometry.json; DFM rules on silk run in the drc_rule checker)")


@check
def test_points(ctx: GCtx, rule: dict, P: dict, o: Out):
    """DFM-MFG-009."""
    b = ctx.board
    tps = [f for f in b.parts.values() if is_testpoint(f)]
    power = set(ctx.design["nets"]["power"]) | set(ctx.design["nets"]["ground"])
    bad = []
    for f in tps:
        for p in f["pads"]:
            need = P["power"] if p["net"] in power else P["signal"]
            d = min(p["size"])
            if d < need.value - 1e-9:
                bad.append((pad_label(dict(p, ref=f["ref"])), d, need.value))
    dmin = min((min(p["size"]) for f in tps for p in f["pads"]), default=None)
    o.add("pad_diameter_mm", rnd(dmin), P["signal"], ok=not bad, n_test_points=len(tps), failing=[f"{a}: {d} < {n}" for a, d, n in bad])
    pitch = [math.dist(a["pos"], c["pos"]) for i, a in enumerate(tps) for c in tps[i + 1:]]
    o.add("center_pitch_mm", rnd(min(pitch)) if pitch else None, P["pitch"], ok=(min(pitch) >= P["pitch"].value - 1e-9) if pitch else True,
          note=None if pitch else "single test point: nothing to compare")
    body = []
    for f in tps:
        for p in f["pads"]:
            for ref, g in b.parts.items():
                if ref == f["ref"] or is_testpoint(g):
                    continue
                for cy in b.courtyard_polys(ref):
                    body.append((G.poly_poly_dist(p["poly"], cy), f["ref"], ref))
    body.sort()
    o.add("to_component_body_mm", rnd(body[0][0]) if body else None, P["body"], ok=(body[0][0] >= P["body"].value - 1e-9) if body else True,
          nearest=f"{body[0][1]}->{body[0][2]}" if body else None)
    edge = sorted((b.edge_dist_poly(p["poly"]), f["ref"]) for f in tps for p in f["pads"])
    o.add("to_board_edge_mm", rnd(edge[0][0]) if edge else None, P["edge"], ok=(edge[0][0] >= P["edge"].value - 1e-9) if edge else True,
          nearest=edge[0][1] if edge else None)
    o.add("same_side", sorted({f["side"] for f in tps}), None, ok=len({f["side"] for f in tps}) <= 1)
    o.not_evaluated += ["tp_to_tall_component (no component heights in the board file)", "solder-mask opening over the pad and silk over the pad"]
    for a, d, n in bad:
        o.ev(refs=[a.split(".")[0]], message=f"test point pad {a} is {d} mm, needs >= {n} mm")


@check
def via_in_smd_pad(ctx: GCtx, rule: dict, P: dict, o: Out):
    """DFM-RTE-002: no via centre inside an SMD pad (heat-sink pads allowed)."""
    b = ctx.board
    hits = []
    for v in b.vias:
        for p in b.all_pads():
            if p["attr"] == "smd" and p["prop"] != "heatsink" and p["poly"] and G.point_in_poly(v["pos"], p["poly"]):
                hits.append((v, p))
    o.add("vias_in_smd_pads", len(hits), P["zero"], n_vias=len(b.vias))
    for v, p in hits:
        o.ev(refs=[p["ref"]], nets=[v["net"]], pos_mm=v["pos"], message=f"via on {v['net']} sits inside SMD pad {pad_label(p)}")


@check
def copper_edge_distance(ctx: GCtx, rule: dict, P: dict, o: Out):
    """GEN-FLR-007: outline closed + every copper object >= limit from Edge.Cuts."""
    b = ctx.board
    out = b.outline
    o.add("outline_closed", bool(out["closed"]), None, ok=out["closed"], loops=out["n_loops"])
    if not out["closed"]:
        return
    items = []
    for t in b.tracks:
        items.append((G.seg_seg_min(G.edges_of([t["start"], t["end"]], closed=False), out["edges"]) - t["width"] / 2, f"track {t['net']}", t["start"]))
    for v in b.vias:
        items.append((b.edge_dist_point(v["pos"]) - v["diameter"] / 2, f"via {v['net']}", v["pos"]))
    for p in b.all_pads():
        if p["copper"] and p["poly"]:
            items.append((b.edge_dist_poly(p["poly"]), f"pad {pad_label(p)}", p["pos"]))
    for layer in ("F.Cu", "B.Cu"):
        for pl in b.fill_polys(layer):
            items.append((G.seg_seg_min(G.edges_of(pl["outline"]), out["edges"]), f"zone fill {pl['net']} {layer}", pl["outline"][0]))
    items.sort(key=lambda x: x[0])
    o.add("min_copper_to_edge_mm", rnd(items[0][0]), P["limit"], nearest=items[0][1])
    for d, lab, pos in items:
        if d < P["limit"].value - 1e-9:
            o.ev(message=f"{lab} is {d:.3f} mm from the board edge", pos_mm=pos, distance_mm=rnd(d))


@check
def supply_trace_widths(ctx: GCtx, rule: dict, P: dict, o: Out):
    """GEN-RTE-006 / PWR-RTE-008: Espressif minimum widths on the 3V3 supply."""
    b = ctx.board
    sp = ctx.design["supply_paths"]["main_3v3"]
    path = b.graph(sp["net"]).path(tuple(sp["from"]), tuple(sp["to"]))
    if path is None:
        o.add("main_3v3_path_width_mm", None, P["main"], ok=False, note=f"no copper path {sp['from']} -> {sp['to']} on {sp['net']}")
    else:
        o.add("main_3v3_path_width_mm", rnd(path["min_width_mm"]), P["main"], path_length_mm=rnd(path["length_mm"]), segments=path["segments"])
        if not P["main"].holds(path["min_width_mm"]):
            for i in path["track_ids"]:
                t = b.graph(sp["net"]).tracks[i]
                if t["width"] < P["main"].value - 1e-9:
                    o.ev(nets=[sp["net"]], pos_mm=t["start"], width_mm=t["width"], message=f"{sp['net']} segment {t['width']} mm wide on the main supply path")
    to = tuple(sp["to"])
    pad = b.pad(*to)
    g = b.graph(sp["net"])
    w = [t["width"] for t in g.tracks if any(G.point_in_poly(e, pad["poly"]) or G.point_poly_dist(e, pad["poly"]) <= 5e-3 for e in (t["start"], t["end"]))]
    o.add("supply_pin_entry_width_mm", rnd(min(w)) if w else None, P["pin"], ok=(min(w) >= P["pin"].value - 1e-9) if w else False,
          pad=f"{to[0]}.{to[1]}", tracks_at_pad=len(w))
    other = [(t["width"], n) for n in ctx.design["nets"]["power_other_than_3v3"] for t in b.net_tracks(n)]
    o.add("other_power_nets_min_width_mm", rnd(min(other)[0]) if other else None, P["other"], ok=(min(other)[0] >= P["other"].value - 1e-9) if other else True,
          nets=ctx.design["nets"]["power_other_than_3v3"])
    for w_, n in other:
        if w_ < P["other"].value - 1e-9:
            o.ev(nets=[n], width_mm=w_, message=f"{n} segment {w_} mm wide")
            break


@check
def fast_net_length(ctx: GCtx, rule: dict, P: dict, o: Out):
    """GEN-RTE-015 / EMC-RTE-005: total routed length of each fast net against a limit."""
    b = ctx.board
    negate = P.get("_negate", False)
    lens = {n: sum(t["length"] for t in b.net_tracks(n)) for n in ctx.design["nets"]["fast"]}
    worst = max(lens.items(), key=lambda kv: kv[1])
    o.add("max_fast_net_length_mm", rnd(worst[1]), P["limit"], negate=negate, worst_net=worst[0], per_net_mm={k: rnd(v, 1) for k, v in lens.items()})
    for n, l in lens.items():
        bad = P["limit"].holds(l) if negate else not P["limit"].holds(l)
        if bad:
            o.ev(nets=[n], length_mm=rnd(l), message=f"{n} is {l:.1f} mm long")


@check
def esd_entry(ctx: GCtx, rule: dict, P: dict, o: Out):
    """EMC-PLC-001 / EMC-RTE-003 / GEN-PLC-009: connector -> TVS -> IC path shape."""
    b = ctx.board
    rows = []
    for e in ctx.design["esd"]:
        g = b.graph(e["net"])
        conn, tvs, ic = tuple(e["connector"]), tuple(e["tvs"]), tuple(e["ic"])
        d1p, d4p, mp = g.path(conn, tvs), g.path(tvs, ic), g.path(conn, ic)
        row = {"net": e["net"], "connector": "%s.%s" % conn, "tvs": "%s.%s" % tvs, "ic": "%s.%s" % ic}
        if d1p is None or d4p is None:
            row["error"] = "no copper path (tracks/vias) between the parts"
        else:
            d1, d4 = d1p["length_mm"], d4p["length_mm"]
            row.update(d1_mm=rnd(d1), d4_mm=rnd(d4), ratio_d4_over_d1=rnd(d4 / d1) if d1 else None, vias_connector_to_tvs=d1p["vias"],
                       max_corner_deg=d1p["max_corner_deg"], stub_mm=rnd(max(0.0, (d1 + d4 - mp["length_mm"]) / 2)) if mp else None)
        rows.append(row)
    ok_paths = [r for r in rows if "error" not in r]
    bad_paths = [r for r in rows if "error" in r]
    for key, spec in P.items():
        if key.startswith("_"):
            continue
        thr = spec
        if key == "ratio":
            vals = [r["ratio_d4_over_d1"] for r in ok_paths if r["ratio_d4_over_d1"] is not None]
            o.add("tvs_to_ic_over_tvs_to_connector", rnd(min(vals)) if vals else None, thr, ok=bool(vals) and not bad_paths and all(thr.holds(v) for v in vals), per_net=rows)
            for r in rows:
                if "error" in r or not thr.holds(r["ratio_d4_over_d1"]):
                    o.ev(nets=[r["net"]], message=f"{r['net']}: d1 (connector->TVS) {r.get('d1_mm')} mm, d4 (TVS->IC) {r.get('d4_mm')} mm", **{k: r.get(k) for k in ("d1_mm", "d4_mm")})
        elif key == "vias":
            vals = [r["vias_connector_to_tvs"] for r in ok_paths]
            o.add("vias_connector_to_tvs", max(vals) if vals else None, thr, ok=bool(vals) and not bad_paths and all(thr.holds(v) for v in vals))
            for r in ok_paths:
                if not thr.holds(r["vias_connector_to_tvs"]):
                    o.ev(nets=[r["net"]], message=f"{r['net']}: {r['vias_connector_to_tvs']} via(s) between {r['connector']} and {r['tvs']}")
        elif key == "stub":
            vals = [r["stub_mm"] for r in ok_paths if r["stub_mm"] is not None]
            o.add("tvs_stub_length_mm", max(vals) if vals else None, thr, ok=bool(vals) and all(thr.holds(v) for v in vals))
        elif key == "corner":
            vals = [r["max_corner_deg"] for r in ok_paths]
            o.add("max_corner_deg_connector_to_tvs", max(vals) if vals else None, thr, ok=bool(vals) and all(thr.holds(v) for v in vals))
        elif key == "d1":
            vals = [r["d1_mm"] for r in ok_paths]
            o.add("connector_to_tvs_mm", max(vals) if vals else None, thr, ok=bool(vals) and all(thr.holds(v) for v in vals))
        elif key == "far_ratio":
            vals = [r["ratio_d4_over_d1"] for r in ok_paths if r["ratio_d4_over_d1"] is not None]
            o.add("ic_side_over_connector_side", rnd(min(vals)) if vals else None, thr, ok=bool(vals) and all(thr.holds(v) for v in vals))
    for r in bad_paths:
        o.ev(nets=[r["net"]], message=f"{r['net']}: {r['error']}")


@check
def decap_proximity(ctx: GCtx, rule: dict, P: dict, o: Out):
    """GEN-PLC-002 / ANA-PLC-002 / EMC-PLC-003: nearest matching capacitor to each IC supply pin."""
    b = ctx.board
    dsg = ctx.design["decoupling"]
    target = to_farad(P["cap_value"]) if "cap_value" in P else dsg["cap_value_f"]
    grounds = set(ctx.design["nets"]["ground"])
    rows = []
    for e in dsg["pins"]:
        if P.get("_ics") and e["ic"] not in P["_ics"]:
            continue
        ic = b.pad(e["ic"], e["pin"])
        cands = []
        for ref, f in b.parts.items():
            if not ref.startswith("C") or f["dnp"]:
                continue
            val = cap_value_f(f["value"])
            if val is None or abs(val - target) > 1e-12 + 0.05 * target:
                continue
            pw = [p for p in f["pads"] if p["net"] == e["net"]]
            gd = [p for p in f["pads"] if p["net"] in grounds]
            if pw and gd:
                cands.append((math.dist(pw[0]["pos"], ic["pos"]), ref, dict(pw[0], ref=ref)))
        row = {"ic_pin": f"{e['ic']}.{e['pin']}", "net": e["net"], "role": e.get("role"), "capacitors_considered": len(cands)}
        if not cands:
            row["error"] = f"no {target * 1e9:g} nF capacitor with one pad on {e['net']} and one on ground"
        else:
            cands.sort()
            d, ref, cp = cands[0]
            row.update(cap=ref, center_distance_mm=rnd(d), edge_distance_mm=rnd(G.poly_poly_dist(cp["poly"], ic["poly"])))
            path = b.graph(e["net"]).path((ref, cp["num"]), (e["ic"], e["pin"]))
            if path:
                row.update(path_length_mm=rnd(path["length_mm"]), path_min_width_mm=path["min_width_mm"], path_vias=path["vias"],
                           length_to_width=rnd(path["track_length_mm"] / path["min_width_mm"], 2) if path["min_width_mm"] else None)
            else:
                row["path"] = "no track path (connected through a pour or not at all)"
        rows.append(row)
    miss = [r for r in rows if "error" in r]
    have = [r for r in rows if "error" not in r]
    for key, thr in P.items():
        if key.startswith("_") or key == "cap_value":
            continue
        if key == "distance":
            o.add("pin_to_cap_center_distance_mm", rnd(max((r["center_distance_mm"] for r in have), default=None)), thr,
                  ok=not miss and all(thr.holds(r["center_distance_mm"]) for r in have), per_pin=rows)
            for r in rows:
                if "error" in r:
                    o.ev(refs=[r["ic_pin"].split(".")[0]], message=f"{r['ic_pin']}: {r['error']}")
                elif not thr.holds(r["center_distance_mm"]):
                    o.ev(refs=[r["cap"], r["ic_pin"].split(".")[0]], nets=[r["net"]],
                         message=f"{r['cap']} is {r['center_distance_mm']} mm (pad centres; {r['edge_distance_mm']} mm edge to edge) from {r['ic_pin']}")
        elif key == "ratio":
            vals = [r["length_to_width"] for r in have if r.get("length_to_width") is not None]
            o.add("trace_length_to_width", rnd(max(vals), 2) if vals else None, thr, ok=not miss and len(vals) == len(have) and all(thr.holds(v) for v in vals))
        elif key == "no_via":
            vals = [r.get("path_vias") for r in have if r.get("path_vias") is not None]
            o.add("vias_between_cap_and_pin", max(vals) if vals else None, thr, ok=not miss and bool(vals) and all(thr.holds(v) for v in vals))
    o.not_evaluated.append("ground-pad return distance and ground via count next to the capacitor (not exported per pad)")


@check
def antenna_keepout(ctx: GCtx, rule: dict, P: dict, o: Out):
    """GEN-PLN-009 / RF-FLR-002: nothing but the antenna module intrudes into the keep-out rectangle on any copper layer."""
    b = ctx.board
    x0, y0, x1, y1 = ctx.design["antenna_keepout"]["rect_mm"]
    rect = G.rect_poly(x0, y0, x1, y1)
    exempt = set(ctx.design["antenna_keepout"]["exempt_refs"])
    rb = (x0, y0, x1, y1)
    hits = []
    for t in b.tracks:
        if G.poly_poly_dist(track_copper_poly(t), rect) == 0.0:
            hits.append(("track", t["net"], t["layer"], t["start"]))
    for v in b.vias:
        if G.point_poly_dist(v["pos"], rect) <= v["diameter"] / 2:
            hits.append(("via", v["net"], "F/B", v["pos"]))
    holes = set()
    for p in b.all_pads():
        if p["ref"] in exempt or not p["poly"] or not p["copper"]:
            continue
        if G.poly_poly_dist(p["poly"], rect) == 0.0:
            if p["attr"] == "npth":      # unplated mounting / locating hole: a screw or standoff goes here (RF-FLR-002 'no screws')
                holes.add(p["ref"])
                hits.append(("mounting hole", "", p["ref"], p["pos"]))
            else:
                hits.append(("pad", p["net"], p["ref"], p["pos"]))
    for ref, f in b.parts.items():
        if ref in exempt or ref in holes:
            continue
        for cy in b.courtyard_polys(ref):
            if G.poly_poly_dist(cy, rect) == 0.0:
                hits.append(("courtyard", "", ref, f["pos"]))
    for layer in ("F.Cu", "B.Cu"):
        for pl in b.fill_polys(layer):
            if G.bbox_overlap(G.bbox_of(pl["outline"]), rb) and G.poly_poly_dist(pl["outline"], rect) == 0.0:
                # outline overlap is necessary but not sufficient: look for fill inside the rectangle
                inside = any(polys_contain([pl], pt) for pt in _grid(rb, 1.0))
                if inside:
                    hits.append(("zone fill", pl["net"], layer, pl["outline"][0]))
    o.add("objects_in_keepout", len(hits), P["zero"], rect_mm=[x0, y0, x1, y1], exempt=sorted(exempt))
    for kind, net, where, pos in hits[:12]:
        o.ev(refs=[where] if kind in ("pad", "courtyard", "mounting hole") else [], nets=[net] if net else [], pos_mm=pos,
             message=f"{kind} {net or ''} {where} inside the antenna keep-out".replace("  ", " "))


def _grid(bb, step):
    xs = np.arange(bb[0] + step / 2, bb[2], step)
    ys = np.arange(bb[1] + step / 2, bb[3], step)
    return [(float(x), float(y)) for x in xs for y in ys]


@check
def zone_orphans(ctx: GCtx, rule: dict, P: dict, o: Out):
    """GEN-PLN-007: every filled copper island contains at least one same-net pad, via or track end."""
    b = ctx.board
    orphans = []
    total = 0
    for layer in ("F.Cu", "B.Cu"):
        for pl in b.fill_polys(layer):
            total += 1
            net = pl["net"]
            pts = [p["pos"] for p in b.all_pads() if p["net"] == net and layer[0] in p["copper"]]
            pts += [v["pos"] for v in b.vias if v["net"] == net]
            pts += [e for t in b.tracks if t["net"] == net and t["layer"] == layer for e in (t["start"], t["end"])]
            if not any(polys_contain([pl], pt) for pt in pts):
                orphans.append((layer, net, round(poly_area(pl["outline"]), 2), pl["outline"][0]))
    o.add("orphan_copper_islands", len(orphans), P["zero"], islands_total=total)
    for layer, net, area, pos in orphans[:12]:
        o.ev(nets=[net], pos_mm=pos, message=f"{layer} {net} island of {area} mm2 has no pad/via/track of its net")


@check
def ground_fill_connections(ctx: GCtx, rule: dict, P: dict, o: Out):
    """GEN-PLN-004 / EMC-PLN-001: each sizeable GND fill region is tied to the other layer by >= N vias / through-hole pads."""
    b = ctx.board
    minarea = P["min_area"].value
    gnd = set(ctx.design["nets"]["ground"])
    rows = []
    for layer in ("F.Cu", "B.Cu"):
        for pl in b.fill_polys(layer):
            if pl["net"] not in gnd:
                continue
            area = poly_area(pl["outline"]) - sum(poly_area(h) for h in pl["holes"])
            if area < minarea:
                continue
            n = sum(1 for v in b.vias if v["net"] == pl["net"] and polys_contain([pl], v["pos"]))
            n += sum(1 for p in b.all_pads() if p["net"] == pl["net"] and len(p["copper"]) == 2 and polys_contain([pl], p["pos"]))
            rows.append((n, layer, round(area, 1), pl["outline"][0]))
    rows.sort()
    o.add("min_connection_points_per_region", rows[0][0] if rows else None, P["points"], ok=bool(rows) and all(P["points"].holds(r[0]) for r in rows),
          regions_checked=len(rows), min_region_area_mm2=minarea)
    for n, layer, area, pos in rows:
        if not P["points"].holds(n):
            o.ev(nets=sorted(gnd), pos_mm=pos, message=f"{layer} GND region of {area} mm2 has {n} via/through-hole connection(s) to the other layer")


@check
def return_path(ctx: GCtx, rule: dict, P: dict, o: Out):
    """GEN-RTE-002 / EMC-RTE-001: signal segments run over GND copper on the opposite layer (2-layer board)."""
    b = ctx.board
    mode = P["_mode"]
    gnd = set(ctx.design["nets"]["ground"])
    power = set(ctx.design["nets"]["power"])
    other = {"F.Cu": "B.Cu", "B.Cu": "F.Cu"}
    fills = {l: b.fill_polys(l, net="GND") for l in ("F.Cu", "B.Cu")}
    nets = set(ctx.design["nets"]["fast"]) if mode == "fast" else {n for n in b.nets if n not in gnd and n not in power}
    bad, n_seg, n_samples, n_unc = [], 0, 0, 0
    for t in b.tracks:
        if t["net"] not in nets or t["layer"] not in other:
            continue
        n_seg += 1
        L = math.dist(t["start"], t["end"])
        k = max(1, int(L / 0.5))
        pts = [(t["start"][0] + (t["end"][0] - t["start"][0]) * i / k, t["start"][1] + (t["end"][1] - t["start"][1]) * i / k) for i in range(k + 1)]
        if mode == "midpoint":
            pts = [pts[len(pts) // 2]] if L > 0 else pts[:1]
        unc = [p for p in pts if not polys_contain(fills[other[t["layer"]]], p)]
        n_samples += len(pts)
        n_unc += len(unc)
        if unc:
            bad.append((t["net"], t["layer"], t["start"], len(unc), len(pts)))
    if mode == "fast":
        cov = 100.0 * (1 - n_unc / n_samples) if n_samples else 100.0
        o.add("fast_net_gnd_coverage_pct", rnd(cov, 2), P["coverage"], samples=n_samples, segments=n_seg)
    else:
        o.add("segments_over_reference_gap", len(bad), P["zero"], segments_checked=n_seg)
    for net, layer, pos, u, n in bad[:12]:
        o.ev(nets=[net], pos_mm=pos, message=f"{net} segment on {layer}: {u}/{n} sample(s) have no GND copper on the other layer")


@check
def trace_current_width(ctx: GCtx, rule: dict, P: dict, o: Out):
    """PWR-RTE-005 / GEN-STK-007: narrowest segment of each rated net vs the width the current needs."""
    b = ctx.board
    cur = ctx.design["currents_a"]
    rows = []
    for net, amps in cur.items():
        ts = b.net_tracks(net)
        if not ts:
            continue
        w = min(t["width"] for t in ts)
        if "per_amp" in P:
            need = P["per_amp"].value * amps
        else:
            k, dT, oz = P["k"].value, ctx.design["design_temp_rise_c"], ctx.design["copper_oz"]
            area_mil2 = (amps / (k * dT ** 0.44)) ** (1 / 0.725)
            need = area_mil2 / (1.378 * oz) * 0.0254
        rows.append((w - need, net, w, need, amps))
    rows.sort()
    src = P["per_amp"] if "per_amp" in P else P["k"]
    how = (f"{src.source_param} = {src.catalog_value} {src.catalog_unit} x rated current" if "per_amp" in P else
           f"IPC-2221 external with {src.source_param} = {src.value}, rise {ctx.design['design_temp_rise_c']} C, {ctx.design['copper_oz']} oz")
    thr = C.Threshold(op=">=", value=0.0, unit="mm", source="catalog", source_param=src.source_param,
                      note=f"narrowest segment minus the width the current needs ({how})")
    o.add("narrowest_margin_mm", rnd(rows[0][0]) if rows else None, thr, ok=bool(rows) and rows[0][0] >= -1e-9,
          per_net={n: {"min_width_mm": w, "required_mm": rnd(need), "current_a": a} for _, n, w, need, a in rows})
    for margin, net, w, need, a in rows:
        if margin < -1e-9:
            o.ev(nets=[net], message=f"{net}: narrowest segment {w} mm, {need:.3f} mm needed for {a} A")


@check
def shunt_kelvin(ctx: GCtx, rule: dict, P: dict, o: Out):
    """PWR-RTE-007 / ANA-RTE-001: sense lines leave the shunt's sense pads, not its force pads."""
    b = ctx.board
    s = ctx.design["shunt"]
    gp, gn = b.graph(s["net_pos"]), b.graph(s["net_neg"])
    comp = gp.components()
    sense = gp.pad_key(s["ref"], s["sense_pos"])
    force = gp.pad_key(s["ref"], s["force_pos"])
    power = gp.pad_key(*s["power_pad"])
    amp = gp.pad_key(s["amp"], s["amp_pos"])
    cs = comp.get(sense[0]) if sense and sense[0] in comp else None
    cf = comp.get(force[0]) if force and force[0] in comp else None
    cp = comp.get(power[0]) if power and power[0] in comp else None
    ca = comp.get(amp[0]) if amp and amp[0] in comp else None
    kelvin = cs is not None and ca == cs and cf != cs and cp != cs
    o.add("kelvin_connection", kelvin, C.manual_threshold("==", True, "bool", "rule_text",
                                                          "the amplifier input is wired to the shunt SENSE pad by copper that is not shared with the force pad / switch source"),
          ok=kelvin, sense_to_amp=ca == cs, sense_shares_copper_with_force_pad=cf == cs, sense_shares_copper_with_switch=cp == cs)
    if not kelvin:
        o.ev(refs=[s["ref"], s["amp"]], nets=[s["net_pos"]], message=f"{s['net_pos']}: sense pad {s['ref']}.{s['sense_pos']} and force pad {s['ref']}.{s['force_pos']} are in "
             + ("the same copper cluster" if cf == cs else "different clusters") + f"; amplifier pin {'is' if ca == cs else 'is NOT'} on the sense pad's copper")
    if "mismatch" in P:
        pp = gp.path((s["ref"], s["sense_pos"]), (s["amp"], s["amp_pos"]))
        pn = gn.path((s["ref"], s["sense_neg"]), (s["amp"], s["amp_neg"]))
        if pp and pn:
            lp, ln = pp["track_length_mm"], pn["track_length_mm"]
            pct = abs(lp - ln) / max(lp, ln) * 100
            o.add("sense_length_mismatch_pct", rnd(pct, 1), P["mismatch"], len_pos_mm=rnd(lp), len_neg_mm=rnd(ln),
                  width_pos_mm=pp["min_width_mm"], width_neg_mm=pn["min_width_mm"], layers_pos=pp["layers"], layers_neg=pn["layers"])
            if not P["mismatch"].holds(pct):
                o.ev(refs=[s["ref"], s["amp"]], nets=[s["net_pos"], s["net_neg"]], message=f"sense lines {lp:.2f} mm ({s['net_pos']}) vs {ln:.2f} mm ({s['net_neg']}): {pct:.0f}% apart")
        else:
            o.add("sense_length_mismatch_pct", None, P["mismatch"], ok=False, note="no copper path from a sense pad to the amplifier input")


@check
def entry_bulk_capacitor(ctx: GCtx, rule: dict, P: dict, o: Out):
    """GEN-PLC-005: a >= 10 uF capacitor on the power entry net close to the entry connector pad."""
    b = ctx.board
    pe = ctx.design["power_entry"]
    ent = b.pad(*pe["connector_pad"])
    cands = []
    for ref, f in b.parts.items():
        if not ref.startswith("C") or f["dnp"]:
            continue
        v = cap_value_f(f["value"])
        if v is None or v < to_farad(P["value"]) - 1e-12:
            continue
        for p in f["pads"]:
            if p["net"] in pe["nets"]:
                cands.append((math.dist(p["pos"], ent["pos"]), ref, p["net"], v))
    cands.sort()
    o.add("nearest_bulk_cap_distance_mm", rnd(cands[0][0]) if cands else None, P["distance"], ok=bool(cands) and P["distance"].holds(cands[0][0]),
          capacitor=cands[0][1] if cands else None, capacitance_f=cands[0][3] if cands else None, entry_pad=f"{pe['connector_pad'][0]}.{pe['connector_pad'][1]}")
    if not cands or not P["distance"].holds(cands[0][0]):
        o.ev(refs=[pe["connector_pad"][0]] + ([cands[0][1]] if cands else []), message=(f"nearest >= 10 uF capacitor on {pe['nets']} is {cands[0][1]}, {cands[0][0]:.1f} mm from {pe['connector_pad'][0]}.{pe['connector_pad'][1]}" if cands
                                                                                     else "no >= 10 uF capacitor on the entry nets"))


@check
def two_terminal_symmetry(ctx: GCtx, rule: dict, P: dict, o: Out):
    """DFM-LIB-002: the two pads of a chip part have equal size and sit symmetrically about the footprint origin."""
    b = ctx.board
    tol = P["tol"].value
    rows = []
    for ref, f in b.parts.items():
        if not f["attr_smd"] or len(f["pads"]) != 2 or is_fiducial(f) or is_testpoint(f):
            continue
        a, c = f["pads"]
        if a["num"] == c["num"]:
            continue
        mid = ((a["pos"][0] + c["pos"][0]) / 2, (a["pos"][1] + c["pos"][1]) / 2)
        off = math.dist(mid, f["pos"])
        dsz = max(abs(a["size"][0] - c["size"][0]), abs(a["size"][1] - c["size"][1]))
        rows.append((max(off, dsz), ref, off, dsz))
    rows.sort(reverse=True)
    o.add("max_asymmetry_mm", rnd(rows[0][0], 4) if rows else None, P["tol"], ok=(rows[0][0] <= tol + 1e-9) if rows else True, parts_checked=len(rows),
          worst=rows[0][1] if rows else None)
    for m, ref, off, dsz in rows:
        if m > tol + 1e-9:
            o.ev(refs=[ref], message=f"{ref}: pad centre offset {off:.4f} mm, size difference {dsz:.4f} mm")


# ------------------------------------------------------------------ driver
def load_bindings() -> dict:
    return C.load_yaml(C.HERE / "bindings" / "geometry.yaml")


def check_rule(rule_id: str, ctx: GCtx, bindings: dict | None = None) -> C.Result:
    bindings = bindings or load_bindings()
    bind = bindings[rule_id]
    cat = C.load_catalog()[rule_id]
    t0 = time.time()
    base = dict(rule_id=rule_id, checker="geometry", severity=cat["severity"], title=cat["title"], method="geometry_script", automatable=C.verify_automatable(rule_id, "geometry_script"), method_check=C.verify_check_text(rule_id, "geometry_script"))
    inputs = {"board_sha256": ctx.board_sha, "geometry_json_sha256": ctx.geometry_sha, "design_sha256": ctx.design_sha}
    tool = {"name": "geometry.py + export_geometry.py (pcbnew)", "version": ctx.kicad_version, "function": bind["fn"]}
    try:
        P = {}
        for k, spec in (bind.get("params") or {}).items():
            P[k] = ctx.thr_from(cat, spec)
        for k, v in (bind.get("flags") or {}).items():
            P["_" + k] = v
        o = Out()
        CHECKS[bind["fn"]](ctx, cat, P, o)
    except Exception as e:  # noqa: BLE001 - checker bugs / missing design roles must surface as 'error', never as a verdict
        import traceback
        return C.Result(status="error", note=f"{type(e).__name__}: {e} | {traceback.format_exc().splitlines()[-3].strip()}", tool=tool, inputs=inputs, **base)
    failed = [s["key"] for s in o.subs if not s["ok"]]
    summary = []   # one line per failing sub-check, so a failure always says what was measured against what (even when no object-level evidence exists)
    for s_ in o.subs:
        if not s_["ok"]:
            t_ = s_["threshold"]
            summary.append({"sub_check": s_["key"], "message": f"{s_['key']}: measured {s_['measured']}"
                            + (f" vs {t_['op']} {t_['value']} {t_.get('unit') or ''}".rstrip() if t_ else "") + (f" ({s_['note']})" if s_.get("note") else "")})
    o.evidence = summary + o.evidence
    measured = {s["key"]: {k: v for k, v in s.items() if k not in ("key", "threshold", "ok")} for s in o.subs}
    for s in o.subs:
        measured[s["key"]]["ok"] = s["ok"]
    thr = [dict(s["threshold"], key=s["key"]) if s["threshold"] else {"key": s["key"]} for s in o.subs]
    note = ("failing: " + ", ".join(failed)) if failed else ""
    if o.not_evaluated:
        note = (note + " | " if note else "") + "not evaluated: " + "; ".join(o.not_evaluated)
    return C.Result(status="fail" if failed else "pass", measured=measured, threshold=thr if len(thr) > 1 else thr[0], evidence=o.evidence[:20], tool=tool,
                    inputs=inputs, duration_s=round(time.time() - t0, 3), note=note, **base)


def make_ctx(geometry_json: Path, board_path: Path, design_path: Path, kicad_version: str) -> GCtx:
    return GCtx(board=G.Board.load(geometry_json), design=C.load_yaml(design_path), geometry_sha=C.sha256_file(geometry_json),
                design_sha=C.sha256_file(design_path), board_sha=C.sha256_file(board_path), kicad_version=kicad_version)


def check_all(ctx: GCtx, rule_ids: list[str] | None = None) -> list[C.Result]:
    bindings = load_bindings()
    return [check_rule(r, ctx, bindings) for r in (rule_ids or list(bindings)) if r in bindings]
