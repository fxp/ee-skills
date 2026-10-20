"""Validate catalog/*.yaml (rules) and catalog/verifiers.yaml against docs/SCHEMA.md.

Usage: validate.py [FILE ...] [--check-urls] [--verifiers]
Exit code 1 if any error. Warnings never fail the run.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

DOMAINS = {
    "general": "GEN", "power": "PWR", "low_power": "LPW", "rf": "RF", "audio": "AUD",
    "analog": "ANA", "high_speed": "HSD", "emc_esd": "EMC", "hv_safety": "HVS",
    "thermal": "THM", "dfm": "DFM",
}
STAGES = {
    "architecture": "ARC", "library": "LIB", "schematic": "SCH", "netlist": "NET",
    "stackup": "STK", "floorplan": "FLR", "placement": "PLC", "routing": "RTE",
    "plane_pour": "PLN", "manufacturing": "MFG", "verification": "VER",
}
SEVERITY = {"must", "should", "consider"}
CONFIDENCE = {"high", "medium", "low"}
METHODS = {
    "erc", "drc", "netlist_diff", "bom_check", "geometry_script", "spice", "tline_calc",
    "em_sim", "si_sim", "pi_sim", "thermal_sim", "emc_precompliance", "bench", "review",
}
AUTOMATABLE = {"full", "partial", "manual"}
SOURCE_KINDS = {"standard", "datasheet", "app_note", "vendor_guide", "textbook", "paper", "tool_doc", "blog", "forum"}
OPS = {"<=", ">=", "<", ">", "==", "range", "minimize", "maximize", "qualitative"}
VER_STATUS = {"installed", "bundled", "not_installed", "cloud"}
ID_RE = re.compile(r"^([A-Z]+)-([A-Z]+)-(\d{3})$")
REQUIRED = ["id", "title", "domain", "stage", "severity", "rule", "rationale", "verify", "sources", "confidence"]
KNOWN = set(REQUIRED) | {"applies_to", "parameters", "conflicts", "tags"}


def check_rule(r, where, errs, warns):
    def e(msg): errs.append(f"{where}: {msg}")
    def w(msg): warns.append(f"{where}: {msg}")

    if not isinstance(r, dict):
        e("not a mapping")
        return None
    for k in REQUIRED:
        if k not in r or r[k] in (None, "", []):
            e(f"missing/empty '{k}'")
    for k in r:
        if k not in KNOWN:
            e(f"unknown field '{k}'")
    rid = r.get("id")
    where = f"{where} [{rid}]"
    dom, stg = r.get("domain"), r.get("stage")
    if dom not in DOMAINS: e(f"bad domain {dom!r}")
    if stg not in STAGES: e(f"bad stage {stg!r}")
    if isinstance(rid, str):
        m = ID_RE.match(rid)
        if not m: e("id must look like PWR-PLC-001")
        else:
            if dom in DOMAINS and m.group(1) != DOMAINS[dom]: e(f"id prefix {m.group(1)} != {DOMAINS[dom]} for domain {dom}")
            if stg in STAGES and m.group(2) != STAGES[stg]: e(f"id stage {m.group(2)} != {STAGES[stg]} for stage {stg}")
    if r.get("severity") not in SEVERITY: e(f"bad severity {r.get('severity')!r}")
    if r.get("confidence") not in CONFIDENCE: e(f"bad confidence {r.get('confidence')!r}")
    if isinstance(r.get("title"), str) and len(r["title"]) > 60: w("title longer than 60 chars")
    for k in ("rule", "rationale"):
        if isinstance(r.get(k), str) and len(r[k]) < 15: w(f"'{k}' very short")

    v = r.get("verify")
    if isinstance(v, list):
        for i, x in enumerate(v):
            if not isinstance(x, dict): e(f"verify[{i}] not a mapping"); continue
            if x.get("method") not in METHODS: e(f"verify[{i}].method bad {x.get('method')!r}")
            if x.get("automatable") not in AUTOMATABLE: e(f"verify[{i}].automatable bad {x.get('automatable')!r}")
            for k in ("tool", "check"):
                if not x.get(k): e(f"verify[{i}] missing '{k}'")
    elif v is not None:
        e("verify must be a list")

    s = r.get("sources")
    has_url = False
    if isinstance(s, list):
        for i, x in enumerate(s):
            if not isinstance(x, dict): e(f"sources[{i}] not a mapping"); continue
            if not x.get("title"): e(f"sources[{i}] missing title")
            if x.get("kind") not in SOURCE_KINDS: e(f"sources[{i}].kind bad {x.get('kind')!r}")
            if x.get("url"):
                has_url = True
                if not str(x["url"]).startswith("http"): e(f"sources[{i}].url not http(s)")
            elif not x.get("ref"): e(f"sources[{i}] needs url or ref")
    elif s is not None:
        e("sources must be a list")
    if r.get("confidence") == "high" and isinstance(s, list) and not has_url:
        w("confidence high but no source has a url (ok for standards/books, double-check)")

    p = r.get("parameters")
    if p is not None:
        if not isinstance(p, list): e("parameters must be a list")
        else:
            for i, x in enumerate(p):
                if not isinstance(x, dict): e(f"parameters[{i}] not a mapping"); continue
                if not x.get("name"): e(f"parameters[{i}] missing name")
                op = x.get("op")
                if op not in OPS: e(f"parameters[{i}].op bad {op!r}")
                val = x.get("value")
                if op == "range" and not (isinstance(val, list) and len(val) == 2): e(f"parameters[{i}] range needs [lo, hi]")
                if op in {"<=", ">=", "<", ">", "=="} and not isinstance(val, (int, float)): e(f"parameters[{i}] needs numeric value for op {op}")
                if isinstance(val, (int, float)) and not x.get("unit"): w(f"parameters[{i}] numeric value without unit")
    for k in ("applies_to", "tags"):
        if r.get(k) is not None and not (isinstance(r[k], list) and all(isinstance(t, str) for t in r[k])):
            e(f"{k} must be a list of strings")
    return rid


def check_verifier(r, where, errs, warns):
    if not isinstance(r, dict):
        errs.append(f"{where}: not a mapping"); return None
    for k in ("id", "name", "methods", "status", "can_check"):
        if not r.get(k):
            errs.append(f"{where}: missing '{k}'")
    for m in r.get("methods") or []:
        if m not in METHODS: errs.append(f"{where}: bad method {m!r}")
    if r.get("status") not in VER_STATUS: errs.append(f"{where}: bad status {r.get('status')!r}")
    return r.get("id")


def check_urls(urls):
    import concurrent.futures as cf
    import httpx

    def probe(u):
        try:
            with httpx.Client(follow_redirects=True, timeout=20, headers={"User-Agent": "Mozilla/5.0"}) as c:
                r = c.get(u)
                return u, r.status_code
        except Exception as ex:  # noqa: BLE001
            return u, type(ex).__name__

    bad = []
    with cf.ThreadPoolExecutor(12) as ex:
        for u, st in ex.map(probe, sorted(urls)):
            if not (isinstance(st, int) and st < 400):
                bad.append((u, st))
    return bad


def main(argv):
    do_urls = "--check-urls" in argv
    files = [a for a in argv if not a.startswith("--")]
    paths = [Path(f) for f in files] if files else sorted((ROOT / "catalog").glob("*.yaml"))
    errs, warns, seen, urls, n = [], [], {}, set(), 0
    for p in paths:
        if not p.is_absolute() and not p.exists() and (ROOT / p).exists():
            p = ROOT / p
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception as ex:  # noqa: BLE001
            errs.append(f"{p}: YAML error: {ex}"); continue
        if not isinstance(data, list):
            errs.append(f"{p}: top level must be a list"); continue
        for i, r in enumerate(data):
            where = f"{p.name}#{i}"
            rid = check_verifier(r, where, errs, warns) if p.name == "verifiers.yaml" else check_rule(r, where, errs, warns)
            n += 1
            if rid:
                if rid in seen: errs.append(f"{where}: duplicate id {rid} (also in {seen[rid]})")
                seen[rid] = p.name
            if isinstance(r, dict):
                for s in r.get("sources") or []:
                    if isinstance(s, dict) and s.get("url"): urls.add(s["url"])
    for m in warns: print("WARN ", m)
    for m in errs: print("ERROR", m)
    print(f"{n} records in {len(paths)} files, {len(urls)} distinct source urls, {len(errs)} errors, {len(warns)} warnings")
    if do_urls:
        bad = check_urls(urls)
        for u, st in bad: print(f"URL   {st}  {u}")
        print(f"url probe: {len(urls) - len(bad)} ok, {len(bad)} not ok (403/429 may just be bot blocking)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
