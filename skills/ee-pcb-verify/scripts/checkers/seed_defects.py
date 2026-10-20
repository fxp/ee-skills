"""Make seeded-defect copies of a board (runs under KiCad's bundled Python, like export_geometry.py).

    KPY -I seed_defects.py GOOD.kicad_pcb OUTDIR

For every defect a fresh load of GOOD is broken in one specific way and saved as OUTDIR/<name>/<stem>.kicad_pcb; the
mapping name -> path is printed as JSON. The tests assert that the rules that pass on GOOD fail on the matching defect.
Only copies are written; GOOD is opened read-only.
"""
import json
import math
import os
import shutil
import sys

import pcbnew

FromMM = pcbnew.FromMM
V = lambda x, y: pcbnew.VECTOR2I(FromMM(x), FromMM(y))  # noqa: E731


def fp(b, ref):
    f = b.FindFootprintByReference(ref)
    assert f is not None, ref
    return f


def move(b, ref, dx=0.0, dy=0.0, to=None):
    f = fp(b, ref)
    p = f.GetPosition()
    f.SetPosition(V(to[0], to[1]) if to else pcbnew.VECTOR2I(p.x + FromMM(dx), p.y + FromMM(dy)))


def add_track(b, net, layer, p0, p1, width):
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(V(*p0))
    t.SetEnd(V(*p1))
    t.SetWidth(FromMM(width))
    t.SetLayer(layer)
    t.SetNet(b.FindNet(net))
    b.Add(t)
    return t


def add_via(b, net, pos, drill, dia):
    v = pcbnew.PCB_VIA(b)
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetPosition(V(*pos))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetDrill(FromMM(drill))
    v.SetWidth(FromMM(dia))
    v.SetNet(b.FindNet(net))
    b.Add(v)
    return v


def free_spot(b, margin=3.0):
    """A board location at least ``margin`` mm from every pad, track and via (for an isolated seeded via)."""
    pts = [(pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)) for f in b.GetFootprints() for p in f.Pads()]
    pts += [(pcbnew.ToMM(t.GetStart().x), pcbnew.ToMM(t.GetStart().y)) for t in b.GetTracks()]
    pts += [(pcbnew.ToMM(t.GetEnd().x), pcbnew.ToMM(t.GetEnd().y)) for t in b.GetTracks()]
    bb = b.GetBoardEdgesBoundingBox()
    x0, y0, x1, y1 = (pcbnew.ToMM(v) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom()))
    best = None
    y = y0 + 20
    while y < y1 - 6:
        x = x0 + 6
        while x < x1 - 6:
            d = min(math.hypot(x - px, y - py) for px, py in pts)
            if best is None or d > best[0]:
                best = (d, x, y)
            x += 1.0
        y += 1.0
    assert best[0] >= margin, f"no free spot (best {best})"
    return best[1], best[2]


def d_decap_c7_far(b):
    move(b, "C7", dy=8.0)                      # INA199 bypass capacitor 8 mm further from U3.3


def d_fiducials_deleted(b):
    for r in ("FID1", "FID2"):
        b.Remove(fp(b, r))                     # leaves one fiducial


def d_smd_near_edge(b):
    move(b, "SW1", dx=-1.0)                    # pad 3.35 mm -> 2.35 mm from the edge: under the 3 mm assembly margin, over the 0.2 mm copper-to-edge floor


def d_part_over_edge(b):
    move(b, "SW3", dx=-3.2)                    # pad 0.15 mm from the edge: under the 0.2 mm copper-to-edge floor


def d_thin_track(b):
    for t in b.GetTracks():
        if t.GetClass() == "PCB_TRACK" and t.GetNetname() == "MOTOR_N":
            t.SetWidth(FromMM(0.08))           # motor-return segment far below both the fab limit and the current-derived width
            return
    raise AssertionError("no MOTOR_N track")


def d_small_drill_via(b):
    x, y = free_spot(b)
    add_via(b, "GND", (x, y), 0.10, 0.35)      # 0.10 mm drill: under the 0.15 mm fab minimum


def d_via_in_pad(b):
    pad = fp(b, "C8").FindPadByNumber("1")
    p = pad.GetPosition()
    add_via(b, pad.GetNetname(), (pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)), 0.3, 0.6)   # via-in-pad on an SMD pad (same net, so no short)


def d_bottom_footprint(b):
    f = fp(b, "R9")
    f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)


def d_net_short(b):
    fp(b, "C5").FindPadByNumber("1").SetNet(b.FindNet("GND"))   # pad of the EN capacitor re-netted to GND: tracks of EN now touch a GND pad


def d_delete_track_txd(b):
    tracks = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK" and t.GetNetname() == "TXD"]
    a = fp(b, "J2").FindPadByNumber("2").GetPosition()
    c = fp(b, "D5").FindPadByNumber("1").GetPosition()
    mx, my = (a.x + c.x) / 2, (a.y + c.y) / 2
    t = min(tracks, key=lambda t: math.hypot((t.GetStart().x + t.GetEnd().x) / 2 - mx, (t.GetStart().y + t.GetEnd().y) / 2 - my))
    b.Remove(t)                                 # a segment half-way along the J2.2 -> D5.1 copper: opens the TXD connector-to-TVS path


def d_antenna_track(b):
    add_track(b, "SCK", pcbnew.F_Cu, (70.0, 58.0), (90.0, 58.0), 0.25)     # 20 mm of signal in the antenna keep-out (y < 64)


def d_long_sck(b):
    add_track(b, "SCK", pcbnew.F_Cu, (52.0, 101.0), (114.0, 101.0), 0.25)  # +62 mm of routed length on the HX711 clock net


DEFECTS = {
    "decap_c7_far": d_decap_c7_far, "fiducials_deleted": d_fiducials_deleted, "smd_near_edge": d_smd_near_edge, "part_over_edge": d_part_over_edge,
    "thin_track": d_thin_track, "small_drill_via": d_small_drill_via, "via_in_pad": d_via_in_pad, "bottom_footprint": d_bottom_footprint,
    "net_short": d_net_short, "delete_track_txd": d_delete_track_txd, "antenna_track": d_antenna_track, "long_sck": d_long_sck,
}

def make_one(good: str, outdir: str, name: str) -> str:
    pro = os.path.splitext(good)[0] + ".kicad_pro"
    d = os.path.join(outdir, name)
    os.makedirs(d, exist_ok=True)
    b = pcbnew.LoadBoard(good)
    DEFECTS[name](b)
    dst = os.path.join(d, os.path.basename(good))
    pcbnew.SaveBoard(dst, b)
    if os.path.exists(pro):
        shutil.copyfile(pro, os.path.join(d, os.path.basename(pro)))
    return dst


if __name__ == "__main__":
    good, outdir = sys.argv[1], sys.argv[2]
    if len(sys.argv) > 3:                       # one defect per process: removing a footprint leaves pcbnew's SWIG layer unable to load the next board
        print(make_one(good, outdir, sys.argv[3]))
    else:
        import subprocess
        out = {}
        for name in DEFECTS:
            r = subprocess.run([sys.executable, "-I", __file__, good, outdir, name], capture_output=True, text=True)
            if r.returncode:
                raise SystemExit(f"{name}: {r.stderr[-400:]}")
            out[name] = r.stdout.strip().splitlines()[-1]
        print(json.dumps(out))
