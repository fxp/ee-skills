"""``drc_rule`` checker: catalog rule id -> custom ``.kicad_dru`` rule(s) -> ``kicad-cli pcb drc`` -> pass/fail + evidence.

One catalog rule = one DRC run in its own directory (so KiCad's "last rule of a constraint type wins" masking cannot hide
a rule behind another), run in parallel. Every run carries a canary rule: if a syntax error makes KiCad silently drop the
whole ``.kicad_dru`` the canary never shows up and the rule is reported ``error``, never ``pass``.

Each rule gets a second *probe* run with the threshold widened so the closest approach is reported even when the rule
passes (``measured``/margin), and so a sub-rule whose condition matches nothing is visible.
"""
from __future__ import annotations

import json
import re
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from . import common as C

CANARY_NAME = "__canary__"
CANARY = (f'(rule "{CANARY_NAME}" (severity warning) (condition "A.Type == \'Footprint\'")'
          ' (constraint assertion "A.Reference == \'__never__\'"))')
RE_REF = re.compile(r"(?:\bof|\bFootprint|\bfield of)\s+([A-Za-z]+[0-9]+)\b")
RE_NET = re.compile(r"\[([^\]]*)\]")
PER_OBJECT_PROBE_MM = 50.0


@dataclass
class Sub:
    name: str
    key: str
    constraint: str
    bound: str | None
    threshold: C.Threshold | None
    condition: str | None
    layer: str | None
    arg: str | None
    shape: str
    note: str | None

    def dru(self, probe: bool) -> str:
        parts = [f'(rule "{self.name}"']
        if self.layer:
            parts.append(f'(layer "{self.layer}")')
        if self.condition:
            parts.append(f'(condition "{self.condition}")')
        if self.constraint == "disallow":
            parts.append(f"(constraint disallow {self.arg})")
        else:
            parts.append(f"(constraint {self.constraint} ({self.bound} {C.mm_fmt(self.probe_value() if probe else self.threshold.value)}))")
        return " ".join(parts) + ")"

    def probe_value(self) -> float:
        v = self.threshold.value
        if self.bound == "max":
            return 0.001
        return PER_OBJECT_PROBE_MM if self.shape == "per_object" else v * 3 + 0.5


def load_bindings() -> dict:
    return C.load_yaml(C.HERE / "bindings" / "drc.yaml")


def build_subs(rule_id: str, binding: dict) -> list[Sub]:
    cat = C.load_catalog()[rule_id]
    subs = []
    for r in binding.get("rules", []):
        thr = None
        if r.get("param"):
            thr = C.resolve_threshold(cat, r["param"], scale=r.get("scale", 1.0), op=">=" if r["bound"] == "min" else "<=")
        elif r.get("threshold_text"):
            thr = C.manual_threshold("==", 0, "count", "rule_text", r["threshold_text"])
        subs.append(Sub(name=f"{rule_id}/{r['key']}", key=r["key"], constraint=r["constraint"], bound=r.get("bound"), threshold=thr,
                        condition=r.get("condition"), layer=r.get("layer"), arg=r.get("arg"), shape=r.get("shape", "per_object"), note=r.get("note")))
    return subs


def drc_once(workdir: Path, board: Path, pro: Path, rules_text: str, patch_pro: dict | None = None, timeout: int = 240) -> tuple[dict, str, str]:
    """Run kicad-cli DRC in ``workdir`` on copies of board/pro with the given rule text; return (report, dru_sha, pro_sha)."""
    workdir.mkdir(parents=True, exist_ok=True)
    b = workdir / board.name
    shutil.copyfile(board, b)
    p = workdir / (board.stem + ".kicad_pro")
    if patch_pro:
        data = json.loads(pro.read_text())
        rs = data.setdefault("board", {}).setdefault("design_settings", {}).setdefault("rule_severities", {})
        rs.update(patch_pro)
        p.write_text(json.dumps(data, indent=2))
    else:
        shutil.copyfile(pro, p)
    dru_text = "(version 1)\n" + CANARY + "\n" + rules_text + "\n"
    (workdir / (board.stem + ".kicad_dru")).write_text(dru_text)
    out = workdir / "drc.json"
    out.unlink(missing_ok=True)
    cp = C.run([C.KCLI, "pcb", "drc", "--format", "json", "--severity-all", "--all-track-errors", "--units", "mm", "-o", out, b],
               env=C.kicad_env(workdir), timeout=timeout)
    if not out.exists():
        raise RuntimeError(f"kicad-cli pcb drc failed rc={cp.returncode}: {(cp.stderr or cp.stdout)[-300:]}")
    return json.loads(out.read_text()), C.sha256_text(dru_text), C.sha256_file(p)


def footprint_count(board: Path) -> int:
    return len(re.findall(r'^\t\(footprint "', board.read_text(), flags=re.M))


def canary_hits(report: dict) -> int:
    return sum(1 for v in report["violations"] if f"rule '{CANARY_NAME}'" in v["description"])


def violations_for(report: dict, name: str) -> list[dict]:
    out = []
    for v in report["violations"]:
        m = C.RE_RULE.search(v["description"])
        if m and m.group(1) == name:
            a = C.RE_ACTUAL.search(v["description"])
            items = v.get("items", [])
            refs = sorted({r for i in items for r in RE_REF.findall(i["description"])})
            nets = sorted({n for i in items for n in RE_NET.findall(i["description"]) if n})
            out.append({"actual": float(a.group(1)) if a else None, "type": v["type"], "severity": v["severity"], "refs": refs, "nets": nets,
                        "pos_mm": [items[0]["pos"]["x"], items[0]["pos"]["y"]] if items else None,
                        "message": v["description"], "items": [i["description"] for i in items]})
    return out


def label(x: dict, msg: str) -> str:
    who = ", ".join(x["refs"] + [f"net {n}" for n in x["nets"]])
    return f"{who}: {msg}" if who else msg


def check_custom(rule_id: str, binding: dict, ctx: "Ctx") -> C.Result:
    cat = C.load_catalog()[rule_id]
    subs = build_subs(rule_id, binding)
    t0 = time.time()
    wd = ctx.workdir / "drc" / rule_id
    base = dict(rule_id=rule_id, checker="drc_rule", severity=cat["severity"], title=cat["title"], method="drc", automatable=C.verify_automatable(rule_id, "drc"), method_check=C.verify_check_text(rule_id, "drc"))
    rules_text = "\n".join(s.dru(False) for s in subs)
    rep, dru_sha, pro_sha = drc_once(wd / "verdict", ctx.board, ctx.pro, rules_text)
    hits = canary_hits(rep)
    inputs = {"board_sha256": ctx.board_sha, "dru_sha256": dru_sha, "kicad_pro_sha256": pro_sha}
    tool = {"name": "kicad-cli pcb drc", "version": ctx.kicad_version, "canary": hits > 0, "canary_hits": hits, "expected_footprints": ctx.n_footprints}
    thr = [dict(s.threshold.as_json(), key=s.key, constraint=s.constraint) for s in subs]
    if hits == 0:
        bad = locate_bad_sub(rule_id, subs, ctx, wd)
        return C.Result(status="error", threshold=thr, tool=tool, inputs=inputs, duration_s=round(time.time() - t0, 2),
                        note="canary absent: KiCad dropped the whole custom rule file (syntax error) so no verdict is trustworthy"
                             + (f"; offending sub-rule: {bad}" if bad else ""), **base)
    probe_text = "\n".join(s.dru(True) for s in subs if s.constraint != "disallow")
    prep = drc_once(wd / "probe", ctx.board, ctx.pro, probe_text)[0] if probe_text else None
    if prep is not None and canary_hits(prep) == 0:
        return C.Result(status="error", threshold=thr, tool=tool, inputs=inputs, duration_s=round(time.time() - t0, 2),
                        note="canary absent in the probe run", **base)
    measured, evidence, failed = {}, [], []
    for s in subs:
        v = violations_for(rep, s.name)
        m = {"violations": len(v)}
        if s.constraint == "disallow":
            m["threshold"] = 0
        else:
            m["threshold"] = s.threshold.value
            pv = violations_for(prep, s.name) if prep is not None else []
            acts = [x["actual"] for x in pv if x["actual"] is not None]
            if acts:
                ext = min(acts) if s.bound == "min" else max(acts)
                m["observed_extreme"] = ext
                m["margin"] = round(ext - s.threshold.value, 4) if s.bound == "min" else round(s.threshold.value - ext, 4)
            else:
                m["observed_extreme"] = None
                m["note"] = "no object within the probe window (condition matched nothing, or every object is far beyond the threshold)"
            m["objects_in_probe_window"] = len(pv)
        measured[s.key] = m
        if v:
            failed.append(s.key)
            v.sort(key=lambda x: (x["actual"] if x["actual"] is not None else 0), reverse=(s.bound == "max"))
            evidence += [{"sub_rule": s.key, **{k: x[k] for k in ("refs", "nets", "pos_mm", "actual")}, "message": label(x, x["message"])} for x in v[:6]]
    return C.Result(status="fail" if failed else "pass", measured=measured, threshold=thr if len(thr) > 1 else thr[0], evidence=evidence[:20],
                    tool=tool, inputs=inputs, duration_s=round(time.time() - t0, 2),
                    note=("failing sub-rules: " + ", ".join(failed)) if failed else "", **base)


def locate_bad_sub(rule_id: str, subs: list[Sub], ctx: "Ctx", wd: Path) -> str | None:
    if len(subs) < 2:
        return subs[0].name if subs else None
    for s in subs:
        try:
            rep = drc_once(wd / f"bisect_{s.key}", ctx.board, ctx.pro, s.dru(False))[0]
        except RuntimeError:
            return s.name
        if canary_hits(rep) == 0:
            return s.name
    return None


def check_builtin(rule_id: str, binding: dict, ctx: "Ctx") -> C.Result:
    cat = C.load_catalog()[rule_id]
    b = binding["builtin"]
    t0 = time.time()
    base = dict(rule_id=rule_id, checker="drc_rule", severity=cat["severity"], title=cat["title"], method="drc", automatable=C.verify_automatable(rule_id, "drc"), method_check=C.verify_check_text(rule_id, "drc"))
    patch = {k: "error" for k in b.get("enable", [])} or None
    rep, dru_sha, pro_sha = drc_once(ctx.workdir / "drc" / rule_id / "verdict", ctx.board, ctx.pro, "", patch_pro=patch)
    hits = canary_hits(rep)
    tool = {"name": "kicad-cli pcb drc (built-in checks)", "version": ctx.kicad_version, "canary": hits > 0, "canary_hits": hits}
    inputs = {"board_sha256": ctx.board_sha, "dru_sha256": dru_sha, "kicad_pro_sha256": pro_sha}
    thr = C.manual_threshold("==", 0, "count", "rule_text", b["threshold_text"]).as_json()
    if hits == 0:
        return C.Result(status="error", threshold=thr, tool=tool, inputs=inputs, duration_s=round(time.time() - t0, 2),
                        note="canary absent: the harness could not load custom rules", **base)
    measured, evidence = {}, []
    for t in b.get("types", []):
        vs = [v for v in rep["violations"] if v["type"] == t]
        measured[t] = len(vs)
        for v in vs[:6]:
            items = v.get("items", [])
            ev = {"type": t, "refs": sorted({r for i in items for r in RE_REF.findall(i["description"])}),
                  "nets": sorted({n for i in items for n in RE_NET.findall(i["description"]) if n}),
                  "pos_mm": [items[0]["pos"]["x"], items[0]["pos"]["y"]] if items else None}
            evidence.append(dict(ev, message=label(ev, v["description"])))
    if b.get("unconnected"):
        un = rep.get("unconnected_items", [])
        measured["unconnected_items"] = len(un)
        for v in un[:6]:
            items = v.get("items", [])
            evidence.append({"type": "unconnected_items", "refs": [], "nets": sorted({n for i in items for n in RE_NET.findall(i["description"]) if n}),
                             "pos_mm": [items[0]["pos"]["x"], items[0]["pos"]["y"]] if items else None, "message": v.get("description", "")})
    total = sum(measured.values())
    return C.Result(status="fail" if total else "pass", measured=measured, threshold=thr, evidence=evidence[:20], tool=tool, inputs=inputs,
                    duration_s=round(time.time() - t0, 2), **base)


@dataclass
class Ctx:
    board: Path          # the run's private copy
    pro: Path
    workdir: Path
    kicad_version: str
    board_sha: str
    n_footprints: int


def make_ctx(board: Path, pro: Path, workdir: Path) -> Ctx:
    return Ctx(board=board, pro=pro, workdir=workdir, kicad_version=C.kicad_version(), board_sha=C.sha256_file(board), n_footprints=footprint_count(board))


def check_rule(rule_id: str, ctx: Ctx, bindings: dict | None = None) -> C.Result:
    bindings = bindings or load_bindings()
    b = bindings[rule_id]
    try:
        return check_builtin(rule_id, b, ctx) if "builtin" in b else check_custom(rule_id, b, ctx)
    except Exception as e:  # noqa: BLE001 - any tooling failure must surface as 'error', never as a verdict
        return C.error_result(rule_id, "drc_rule", f"{type(e).__name__}: {e}", tool={"name": "kicad-cli pcb drc", "version": ctx.kicad_version},
                              inputs={"board_sha256": ctx.board_sha})


def check_all(ctx: Ctx, rule_ids: list[str] | None = None, workers: int = 6) -> list[C.Result]:
    bindings = load_bindings()
    ids = [r for r in (rule_ids or list(bindings)) if r in bindings]
    with ThreadPoolExecutor(max_workers=workers) as ex:  # each worker only waits on a kicad-cli subprocess
        res = list(ex.map(lambda r: check_rule(r, ctx, bindings), ids))
    return res
