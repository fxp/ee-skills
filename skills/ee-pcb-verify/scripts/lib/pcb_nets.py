# runs under KiCad's bundled python:  $KPY -I pcb_nets.py BOARD.kicad_pcb OUT.json
import json, sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
out = {"parts": {}, "nets": {}}
for f in b.GetFootprints():
    out["parts"][f.GetReference()] = {"value": f.GetValue(), "fpid": str(f.GetFPID().GetUniStringLibId())}
    for p in f.Pads():
        n = p.GetNetname()
        if n:
            out["nets"].setdefault(n, []).append(f"{f.GetReference()}.{p.GetNumber()}")
json.dump(out, open(sys.argv[2], "w"), indent=1, sort_keys=True)
