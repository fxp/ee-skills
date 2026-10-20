# $KPY -I dump_copper.py BOARD OUT.json  : tracks/vias/pads per net (mm) for a resistive-network IR-drop solve
import json, sys, pcbnew
mm = pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
d = {"tracks": [], "vias": [], "pads": [], "thickness_mm": {"F.Cu": 0.035, "B.Cu": 0.035}}
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        d["vias"].append({"net": t.GetNetname(), "x": mm(t.GetPosition().x), "y": mm(t.GetPosition().y), "drill": mm(t.GetDrill())})
    elif t.GetClass() == "PCB_TRACK":
        d["tracks"].append({"net": t.GetNetname(), "layer": t.GetLayerName(), "x1": mm(t.GetStart().x), "y1": mm(t.GetStart().y),
                            "x2": mm(t.GetEnd().x), "y2": mm(t.GetEnd().y), "w": mm(t.GetWidth())})
for f in b.GetFootprints():
    for p in f.Pads():
        d["pads"].append({"ref": f.GetReference(), "num": p.GetNumber(), "net": p.GetNetname(), "x": mm(p.GetPosition().x), "y": mm(p.GetPosition().y),
                          "layer": "F.Cu" if p.IsOnLayer(pcbnew.F_Cu) else "B.Cu", "tht": p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH})
json.dump(d, open(sys.argv[2], "w"))
