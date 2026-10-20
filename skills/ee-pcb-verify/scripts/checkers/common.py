"""Shared plumbing for the rule checkers: catalog access, threshold resolution, KiCad tool paths, result objects.

Thresholds are never written in checker code. A binding names a catalog ``parameters[].name`` and ``resolve_threshold``
returns the catalog's ``op / value / unit`` (converted to mm where the unit is a length). The few rules whose catalog
entry has no number (the ``verify.check`` text says "project-set, empirical") take the value from the board design file
and the result says so in ``threshold.source``.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent


def _find_catalog() -> Path:
    """$EE_CATALOG_DIR, else the nearest ancestor of this file that holds catalog/*.yaml (a repo checkout or an installed plugin)."""
    env = os.environ.get("EE_CATALOG_DIR")
    if env:
        return Path(env).expanduser().resolve()
    for p in HERE.parents:
        if (p / "catalog").is_dir() and any((p / "catalog").glob("*.yaml")):
            return p / "catalog"
    raise FileNotFoundError("rule catalog not found: clone https://github.com/fxp/ee-skills or set EE_CATALOG_DIR to its catalog/ directory")


CATALOG_DIR = _find_catalog()
REPO = CATALOG_DIR.parent


def rel(p: Path) -> str:
    """Path relative to the repo when inside it, else absolute."""
    p = Path(p)
    try:
        return str(p.resolve().relative_to(REPO))
    except ValueError:
        return str(p)

WORK = HERE / "_work"      # private scratch space (board copies, per-rule DRC dirs, seeded defects); git-ignored, never /tmp
KICAD_APP = Path(os.environ.get("EE_KICAD_APP", "/Applications/KiCad/KiCad.app"))   # macOS tested; elsewhere set KCLI and KPY
KCLI = Path(os.environ.get("KCLI", KICAD_APP / "Contents/MacOS/kicad-cli"))
KPY = Path(os.environ.get("KPY", KICAD_APP / "Contents/Frameworks/Python.framework/Versions/Current/bin/python3"))

LENGTH_TO_MM = {"mm": 1.0, "mil": 0.0254, "inch": 25.4, "in": 25.4, "um": 0.001, "µm": 0.001}
OPS = {
    "<=": lambda m, v: m <= v + 1e-9, ">=": lambda m, v: m >= v - 1e-9, "<": lambda m, v: m < v, ">": lambda m, v: m > v,
    "==": lambda m, v: abs(m - v) <= 1e-6 + 1e-6 * abs(v),
}


def ensure_work() -> Path:
    WORK.mkdir(exist_ok=True)
    (WORK / ".gitignore").write_text("*\n!.gitignore\n")
    return WORK


def kicad_available() -> bool:
    return KCLI.exists() and KPY.exists()


def kicad_version() -> str:
    try:
        r = subprocess.run([str(KPY), "-I", "-c", "import pcbnew;print(pcbnew.Version())"], capture_output=True, text=True, timeout=60)
        return r.stdout.strip().splitlines()[-1]
    except Exception:  # noqa: BLE001
        return "unknown"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(Path(path).read_bytes())
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def kicad_env(workdir: Path) -> dict[str, str]:
    """Private config/documents dirs so kicad-cli never touches ~/Library/Preferences/kicad or scans ~/Documents."""
    cfg, docs = workdir / "_cfg", workdir / "_docs"
    cfg.mkdir(parents=True, exist_ok=True)
    docs.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, KICAD_CONFIG_HOME=str(cfg), KICAD_DOCUMENTS_HOME=str(docs))
    share = KICAD_APP / "Contents/SharedSupport"
    env.setdefault("KICAD10_SYMBOL_DIR", str(share / "symbols"))
    env.setdefault("KICAD10_FOOTPRINT_DIR", str(share / "footprints"))
    return env


# ---------------------------------------------------------------- catalog
_CATALOG: dict[str, dict] | None = None


def load_catalog() -> dict[str, dict]:
    global _CATALOG
    if _CATALOG is None:
        rules: dict[str, dict] = {}
        for f in sorted(CATALOG_DIR.glob("*.yaml")):
            if f.name == "verifiers.yaml":
                continue
            for r in yaml.safe_load(f.read_text()):
                rules[r["id"]] = r
        _CATALOG = rules
    return _CATALOG


def load_yaml(path: Path):
    return yaml.safe_load(Path(path).read_text())


def catalog_param(rule: dict, name: str) -> dict:
    for p in rule.get("parameters") or []:
        if p.get("name") == name:
            return p
    raise KeyError(f"{rule['id']}: catalog has no parameter {name!r}")


def to_mm(value: float, unit: str | None) -> float:
    if unit in LENGTH_TO_MM:
        return value * LENGTH_TO_MM[unit]
    if unit in (None, "", "-"):
        return value
    raise ValueError(f"cannot convert unit {unit!r} to mm")


@dataclass
class Threshold:
    op: str
    value: float | list
    unit: str | None
    source: str                    # "catalog" | "design_yaml" | "rule_text"
    source_param: str | None = None
    note: str | None = None
    catalog_value: float | list | None = None   # value as written in the catalog, before unit conversion
    catalog_unit: str | None = None
    scale: float = 1.0                           # binding-level multiplier applied after unit conversion

    def as_json(self) -> dict:
        d = {"op": self.op, "value": self.value, "unit": self.unit, "source": self.source, "source_param": self.source_param}
        if (self.catalog_unit and self.catalog_unit != self.unit) or self.scale != 1.0:
            d["catalog_value"], d["catalog_unit"] = self.catalog_value, self.catalog_unit
        if self.scale != 1.0:
            d["scale"] = self.scale
        if self.note:
            d["note"] = self.note
        return d

    def holds(self, measured: float) -> bool:
        if self.op == "range":
            lo, hi = self.value
            return lo - 1e-9 <= measured <= hi + 1e-9
        return OPS[self.op](measured, self.value)


def resolve_threshold(rule: dict, param: str, scale: float = 1.0, to_length_mm: bool = True, op: str | None = None) -> Threshold:
    p = catalog_param(rule, param)
    if p.get("value") is None:
        raise ValueError(f"{rule['id']}.{param} has no numeric value in the catalog")
    unit = p.get("unit")
    raw = p["value"]
    if to_length_mm and isinstance(unit, str) and unit.endswith(" per A") and unit[:-6] in LENGTH_TO_MM:   # e.g. "mil per A"
        f = LENGTH_TO_MM[unit[:-6]] * scale
        conv = [x * f for x in raw] if isinstance(raw, list) else raw * f
        return Threshold(op=op or p["op"], value=conv, unit="mm per A", source="catalog", source_param=param, note=(p.get("note") or None),
                         catalog_value=raw, catalog_unit=unit, scale=scale)
    if to_length_mm and unit in LENGTH_TO_MM:
        conv = [to_mm(x, unit) * scale for x in raw] if isinstance(raw, list) else to_mm(raw, unit) * scale
        out_unit = "mm"
    else:
        conv = [x * scale for x in raw] if isinstance(raw, list) else raw * scale
        out_unit = unit
    return Threshold(op=op or p["op"], value=conv, unit=out_unit, source="catalog", source_param=param, note=(p.get("note") or None),
                     catalog_value=raw, catalog_unit=unit, scale=scale)


def manual_threshold(op: str, value, unit: str, source: str, note: str) -> Threshold:
    return Threshold(op=op, value=value, unit=unit, source=source, note=note)


# ---------------------------------------------------------------- results
@dataclass
class Result:
    rule_id: str
    checker: str
    status: str                    # pass | fail | error | skipped
    severity: str = ""
    title: str = ""
    method: str = ""               # catalog verify.method this checker implements (drc | geometry_script)
    automatable: str = ""          # catalog verify.automatable for that method (the harness only claims results for 'full')
    method_check: str = ""         # the catalog verify.check text this implements
    measured: dict = field(default_factory=dict)
    threshold: dict | list | None = None
    evidence: list = field(default_factory=list)
    tool: dict = field(default_factory=dict)
    inputs: dict = field(default_factory=dict)
    duration_s: float = 0.0
    note: str = ""

    def as_json(self) -> dict:
        d = dict(self.__dict__)
        if not d["note"]:
            d.pop("note")
        return d


def catalog_head(rule_id: str) -> dict:
    r = load_catalog()[rule_id]
    return {"severity": r["severity"], "title": r["title"]}


def verify_check_text(rule_id: str, method: str) -> str:
    for v in load_catalog()[rule_id]["verify"]:
        if v["method"] == method:
            return v["check"]
    return ""


def verify_automatable(rule_id: str, method: str) -> str:
    for v in load_catalog()[rule_id]["verify"]:
        if v["method"] == method:
            return v["automatable"]
    return "none"


def error_result(rule_id: str, checker: str, msg: str, **kw) -> Result:
    h = catalog_head(rule_id)
    return Result(rule_id=rule_id, checker=checker, status="error", severity=h["severity"], title=h["title"], note=msg, **kw)


def run(cmd: list[str], env: dict | None = None, timeout: int = 240, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True, env=env, timeout=timeout, cwd=cwd)


def copy_board(board: Path, pro: Path | None, dest: Path) -> tuple[Path, Path | None]:
    """Copy .kicad_pcb (+ .kicad_pro) into ``dest`` and return the copies. Never opens the source for writing."""
    dest.mkdir(parents=True, exist_ok=True)
    text = board.read_bytes()
    if not text.rstrip().endswith(b")"):
        raise RuntimeError(f"{board} does not end with ')': KiCad may be mid-save; copy again in a moment")
    b2 = dest / board.name
    b2.write_bytes(text)
    p2 = None
    if pro is not None:
        p2 = dest / (board.stem + ".kicad_pro")
        shutil.copyfile(pro, p2)
    return b2, p2


def mm_fmt(v: float) -> str:
    return f"{v:.4f}mm"


def js(obj) -> str:
    return json.dumps(obj, indent=1, ensure_ascii=False, default=str)


def die(msg: str):
    print(msg, file=sys.stderr)
    raise SystemExit(2)


RE_ACTUAL = re.compile(r"actual\s+(-?[0-9.]+)")
RE_RULE = re.compile(r"rule '([^']+)'")
