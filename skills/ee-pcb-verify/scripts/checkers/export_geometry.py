"""Export a KiCad board to ``geometry.json`` (mm, KiCad board coordinates, y down).

Runs under KiCad's bundled Python 3.9 because ``pcbnew`` only imports there:

    KPY -I export_geometry.py BOARD.kicad_pcb OUT.json

All pcbnew coupling in the checker stack is confined to this file and ``seed_defects.py``; the geometry checkers read
the JSON in the repo's Python 3.14. The board is opened read-only (never saved).
"""
import hashlib
import json
import os
import sys

import pcbnew

mm = pcbnew.ToMM
MAX_ERR = 5000  # nm; polygonisation tolerance for rounded pad ends


def pt(v):
    return [round(mm(v.x), 4), round(mm(v.y), 4)]


def chain(ch):
    return [[round(mm(ch.CPoint(i).x), 4), round(mm(ch.CPoint(i).y), 4)] for i in range(ch.PointCount())]


def poly_set(ps):
    """SHAPE_POLY_SET -> list of {outline, holes}."""
    out = []
    for i in range(ps.OutlineCount()):
        out.append({"outline": chain(ps.Outline(i)), "holes": [chain(ps.Hole(i, h)) for h in range(ps.HoleCount(i))]})
    return out


def bbox(bb):
    return [round(mm(bb.GetLeft()), 4), round(mm(bb.GetTop()), 4), round(mm(bb.GetRight()), 4), round(mm(bb.GetBottom()), 4)]


PAD_SHAPES = {
    pcbnew.PAD_SHAPE_CIRCLE: "circle", pcbnew.PAD_SHAPE_RECT: "rect", pcbnew.PAD_SHAPE_OVAL: "oval",
    pcbnew.PAD_SHAPE_TRAPEZOID: "trapezoid", pcbnew.PAD_SHAPE_ROUNDRECT: "roundrect", pcbnew.PAD_SHAPE_CUSTOM: "custom",
}
PAD_ATTRS = {
    pcbnew.PAD_ATTRIB_PTH: "pth", pcbnew.PAD_ATTRIB_SMD: "smd", pcbnew.PAD_ATTRIB_CONN: "conn", pcbnew.PAD_ATTRIB_NPTH: "npth",
}
PAD_PROPS = {
    pcbnew.PAD_PROP_NONE: None, pcbnew.PAD_PROP_BGA: "bga", pcbnew.PAD_PROP_FIDUCIAL_GLBL: "fiducial_global",
    pcbnew.PAD_PROP_FIDUCIAL_LOCAL: "fiducial_local", pcbnew.PAD_PROP_TESTPOINT: "testpoint", pcbnew.PAD_PROP_HEATSINK: "heatsink",
    pcbnew.PAD_PROP_CASTELLATED: "castellated", pcbnew.PAD_PROP_MECHANICAL: "mechanical", pcbnew.PAD_PROP_PRESSFIT: "pressfit",
}


def side(layer):
    return "F" if layer == pcbnew.F_Cu else "B"


def export_pad(fp, p):
    on_f, on_b = p.IsOnLayer(pcbnew.F_Cu), p.IsOnLayer(pcbnew.B_Cu)
    layer = pcbnew.F_Cu if on_f else pcbnew.B_Cu
    ps = pcbnew.SHAPE_POLY_SET()
    p.TransformShapeToPolygon(ps, layer, 0, MAX_ERR, pcbnew.ERROR_INSIDE)
    polys = poly_set(ps)
    drill = p.GetDrillSize()
    return {
        "num": p.GetNumber(), "net": p.GetNetname(), "pos": pt(p.GetPosition()), "size": [round(mm(p.GetSizeX()), 4), round(mm(p.GetSizeY()), 4)],
        "shape": PAD_SHAPES.get(p.GetShape(), str(p.GetShape())), "attr": PAD_ATTRS.get(p.GetAttribute(), str(p.GetAttribute())),
        "prop": PAD_PROPS.get(p.GetProperty(), str(p.GetProperty())), "angle": round(p.GetOrientationDegrees(), 3),
        "side": side(layer), "copper": ([ "F" ] if on_f else []) + ([ "B" ] if on_b else []),
        "drill": [round(mm(drill.x), 4), round(mm(drill.y), 4)] if drill.x else None, "pin_name": p.GetPinFunction() or p.GetName(),
        "poly": polys[0]["outline"] if polys else [], "bbox": bbox(p.GetBoundingBox()),
        "mask_margin": (round(mm(p.GetLocalSolderMaskMargin()), 4) if p.GetLocalSolderMaskMargin() is not None else None),  # None = board default
    }


def export_fp(fp):
    layer = fp.GetLayer()
    d = {
        "ref": fp.GetReference(), "value": fp.GetValue(), "fpid": str(fp.GetFPID().GetUniStringLibId()), "side": side(layer),
        "pos": pt(fp.GetPosition()), "angle": round(fp.GetOrientationDegrees(), 3), "dnp": bool(fp.IsDNP()),
        "attr_smd": bool(fp.GetAttributes() & pcbnew.FP_SMD), "attr_tht": bool(fp.GetAttributes() & pcbnew.FP_THROUGH_HOLE),
        "exclude_from_bom": bool(fp.GetAttributes() & pcbnew.FP_EXCLUDE_FROM_BOM), "board_only": bool(fp.GetAttributes() & pcbnew.FP_BOARD_ONLY),
        "allow_missing_courtyard": bool(fp.AllowMissingCourtyard()), "fields": {f.GetName(): f.GetText() for f in fp.GetFields()},
        "bbox": bbox(fp.GetBoundingBox(False)),
    }
    crt = fp.GetCourtyard(pcbnew.F_CrtYd if layer == pcbnew.F_Cu else pcbnew.B_CrtYd)
    d["courtyard"] = poly_set(crt)
    d["courtyard_bbox"] = bbox(crt.BBox()) if crt.OutlineCount() else None
    d["pads"] = [export_pad(fp, p) for p in fp.Pads()]
    return d


def export(path):
    b = pcbnew.LoadBoard(path)
    nets = {}
    for name, ni in b.GetNetInfo().NetsByName().items():
        name = str(name)
        if name:
            nets[name] = {"netclass": ni.GetNetClassName()}
    tracks, vias = [], []
    for t in b.GetTracks():
        cls = t.GetClass()
        if cls == "PCB_VIA":
            lay = b.GetLayerName(t.TopLayer()), b.GetLayerName(t.BottomLayer())
            vias.append({"net": t.GetNetname(), "pos": pt(t.GetPosition()), "diameter": round(mm(t.GetWidth(pcbnew.F_Cu)), 4),
                         "drill": round(mm(t.GetDrill()), 4), "layers": list(lay), "type": str(t.GetViaType())})
        else:
            tr = {"net": t.GetNetname(), "layer": t.GetLayerName(), "start": pt(t.GetStart()), "end": pt(t.GetEnd()),
                  "width": round(mm(t.GetWidth()), 4), "length": round(mm(t.GetLength()), 4), "kind": "arc" if cls == "PCB_ARC" else "line"}
            if cls == "PCB_ARC":
                tr["mid"] = pt(t.GetMid())
            tracks.append(tr)
    zones = []
    for z in b.Zones():
        layers = [b.GetLayerName(l) for l in z.GetLayerSet().Seq()]
        zd = {"name": z.GetZoneName(), "net": z.GetNetname(), "layers": layers, "rule_area": bool(z.GetIsRuleArea()),
              "priority": z.GetAssignedPriority(), "outline": poly_set(z.Outline()), "min_thickness": round(mm(z.GetMinThickness()), 4)}
        if z.GetIsRuleArea():
            zd["keepout"] = {"tracks": bool(z.GetDoNotAllowTracks()), "vias": bool(z.GetDoNotAllowVias()),
                             "copper_pour": bool(z.GetDoNotAllowZoneFills()), "pads": bool(z.GetDoNotAllowPads()),
                             "footprints": bool(z.GetDoNotAllowFootprints())}
        else:
            zd["filled"] = {b.GetLayerName(l): {"area_mm2": round(z.GetFilledArea() / 1e12, 3), "polys": poly_set(z.GetFilledPolysList(l))}
                            for l in z.GetLayerSet().Seq() if z.HasFilledPolysForLayer(l)} if hasattr(z, "HasFilledPolysForLayer") else {}
        zones.append(zd)
    outline = []
    for g in b.GetDrawings():
        if g.GetLayer() == pcbnew.Edge_Cuts:
            s = {"shape": g.GetShapeStr()}
            if g.GetShape() == pcbnew.SHAPE_T_SEGMENT:
                s.update(start=pt(g.GetStart()), end=pt(g.GetEnd()))
            elif g.GetShape() == pcbnew.SHAPE_T_ARC:
                s.update(start=pt(g.GetStart()), end=pt(g.GetEnd()), mid=pt(g.GetArcMid()))
            elif g.GetShape() == pcbnew.SHAPE_T_CIRCLE:
                s.update(center=pt(g.GetCenter()), radius=round(mm(g.GetRadius()), 4))
            elif g.GetShape() == pcbnew.SHAPE_T_RECT:
                s.update(start=pt(g.GetStart()), end=pt(g.GetEnd()))
            else:
                s["polygon"] = poly_set(g.GetPolyShape())
            outline.append(s)
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    return {
        "schema": 1, "source": os.path.basename(path), "source_sha256": sha, "kicad_version": pcbnew.Version(), "units": "mm",
        "origin": "KiCad board coordinates (y down)", "board_bbox": bbox(b.GetBoardEdgesBoundingBox()), "edge_cuts": outline,
        "copper_layers": b.GetCopperLayerCount(), "mask_expansion_mm": round(mm(b.GetDesignSettings().m_SolderMaskExpansion), 4), "board_thickness_mm": round(mm(b.GetDesignSettings().GetBoardThickness()), 3),
        "nets": nets, "footprints": [export_fp(f) for f in b.GetFootprints()], "tracks": tracks, "vias": vias, "zones": zones,
    }


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    data = export(src)
    with open(dst, "w") as fh:
        json.dump(data, fh, separators=(",", ":"))
    print(f"geometry.json: {len(data['footprints'])} footprints, {len(data['tracks'])} tracks, {len(data['vias'])} vias, {len(data['zones'])} zones")
