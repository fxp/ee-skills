"""netlist_diff: schematic (kicad-cli sch export netlist --format kicadxml) vs PCB pad nets (pcb_nets.py dump). stdlib only.
usage: netlist_diff.py sch.xml pcb_nets.json ; exit 1 on any difference. Nets are compared as pin SETS (names normalised: leading '/' stripped),
so renamed nets don't matter, wrong connections do."""
import json, sys, xml.etree.ElementTree as ET
sch = ET.parse(sys.argv[1]).getroot()
s_nets, s_parts = {}, {}
for c in sch.iter("comp"):
    v = c.findtext("value") or ""
    s_parts[c.get("ref")] = v
for n in sch.iter("net"):
    pins = frozenset(f'{x.get("ref")}.{x.get("pin")}' for x in n.iter("node"))
    if len(pins) > 0:
        s_nets[pins] = n.get("name").lstrip("/")
pcb = json.load(open(sys.argv[2]))
p_nets = {frozenset(v): k.lstrip("/") for k, v in pcb["nets"].items()}
rep = {"missing_in_pcb": [], "extra_in_pcb": [], "value_mismatch": [], "net_only_in_sch": [], "net_only_in_pcb": []}
for r, v in s_parts.items():
    if r.startswith("#"): continue
    if r not in pcb["parts"]: rep["missing_in_pcb"].append(r)
    elif pcb["parts"][r]["value"] != v: rep["value_mismatch"].append(f'{r}: sch={v} pcb={pcb["parts"][r]["value"]}')
rep["extra_in_pcb"] = sorted(r for r in pcb["parts"] if r not in s_parts and not r.startswith(("H", "FID")))
# a PCB net may omit pins that have no pad net (NC) -> compare only pins present on both sides
common = {p for pins in s_nets for p in pins if p.split(".")[0] in pcb["parts"]}
s_set = {frozenset(p for p in pins if p in common): nm for pins, nm in s_nets.items() if any(p in common for p in pins)}
for pins, nm in s_set.items():
    if pins not in p_nets: rep["net_only_in_sch"].append(f"{nm}: {sorted(pins)}")
for pins, nm in p_nets.items():
    if pins not in s_set: rep["net_only_in_pcb"].append(f"{nm}: {sorted(pins)}")
print(json.dumps({k: v for k, v in rep.items()}, indent=1))
sys.exit(1 if any(rep.values()) else 0)
