"""Seeded-defect tests for the drc_rule and geometry checkers.

A copy of a reference board is broken one way at a time with pcbnew (move a part, delete a footprint, change a net,
...). For each (defect, rule) pair the rule must PASS on the good board and FAIL on the defect board; a checker that
silently stops checking (a dropped .kicad_dru, an empty selector) fails these tests. All files live under
skills/ee-pcb-verify/scripts/checkers/_work/ (never /tmp, never the original board).

The defects in seed_defects.py are written for the author's ESP32-C3 cat-feeder reference board (refs C7, U1, J2, nets
TXD/SCK ...), which is not published yet, so the tests run only when you point them at it:

    EE_TEST_BOARD=/path/cat_feeder_rev_c.kicad_pcb EE_TEST_PRO=/path/x.kicad_pro EE_TEST_DESIGN=/path/design.yaml pytest tests/test_checkers_seeded.py

To reuse the method for your own board, adapt seed_defects.py and FLIPS below.
"""
from __future__ import annotations

import copy
import json
import os
import shutil
import uuid
from pathlib import Path

import pytest
import yaml

from checkers import common as C
from checkers import drc_rule as D
from checkers import geometry as GE
from checkers import run as R

pytestmark = pytest.mark.kicad_bp

_ENV = {k: os.environ.get(k) for k in ("EE_TEST_BOARD", "EE_TEST_PRO", "EE_TEST_DESIGN")}
if not all(_ENV.values()):
    pytest.skip("set EE_TEST_BOARD, EE_TEST_PRO, EE_TEST_DESIGN to run the seeded-defect tests (reference board not published)", allow_module_level=True)
SRC_BOARD = Path(_ENV["EE_TEST_BOARD"])
SRC_PRO = Path(_ENV["EE_TEST_PRO"])
SRC_DESIGN = Path(_ENV["EE_TEST_DESIGN"])
HERE = Path(__file__).resolve()

# (defect, checker, rule) : the rule passes on the good board and fails on the defect
FLIPS = [
    ("thin_track", "drc_rule", "DFM-STK-001"), ("thin_track", "drc_rule", "GEN-STK-005"),
    ("thin_track", "geometry", "PWR-RTE-005"), ("thin_track", "geometry", "GEN-STK-007"),
    ("small_drill_via", "drc_rule", "DFM-STK-002"), ("small_drill_via", "drc_rule", "GEN-STK-005"),
    ("part_over_edge", "drc_rule", "GEN-FLR-007"), ("part_over_edge", "drc_rule", "DFM-PLN-001"),
    ("part_over_edge", "geometry", "GEN-FLR-007"), ("part_over_edge", "geometry", "DFM-FLR-006"),
    ("bottom_footprint", "drc_rule", "GEN-STK-004"),
    ("net_short", "drc_rule", "GEN-NET-007"),
    ("delete_track_txd", "drc_rule", "GEN-NET-007"), ("delete_track_txd", "geometry", "EMC-PLC-001"),
    ("decap_c7_far", "geometry", "ANA-PLC-002"),
    ("fiducials_deleted", "geometry", "DFM-PLC-003"),
    ("smd_near_edge", "geometry", "DFM-FLR-006"),
    ("via_in_pad", "geometry", "DFM-RTE-002"),
    ("antenna_track", "geometry", "GEN-PLN-009"), ("antenna_track", "geometry", "RF-FLR-002"),
    ("long_sck", "geometry", "GEN-RTE-015"),
]
# rules that must keep passing on a defect (the two checkers are complementary, not redundant)
STAYS_PASS = [("smd_near_edge", "drc_rule", "DFM-PLN-001"), ("smd_near_edge", "drc_rule", "GEN-FLR-007")]


class World:
    def __init__(self, root: Path):
        self.root = root
        self.good_dir = root / "good"
        self.board, self.pro = C.copy_board(SRC_BOARD, SRC_PRO, self.good_dir)
        env = C.kicad_env(root)
        cp = C.run([C.KPY, "-I", C.HERE / "seed_defects.py", self.board, root / "seeds"], env=env, timeout=300)
        assert cp.returncode == 0, cp.stderr[-500:]
        self.seeds = {k: Path(v) for k, v in json.loads(cp.stdout.strip().splitlines()[-1]).items()}
        self.version = C.kicad_version()
        # the shipped design file exempts nothing; the antenna test also exempts the two mounting holes that sit in the strip on the real board
        d = C.load_yaml(SRC_DESIGN)
        self.design = SRC_DESIGN
        d2 = copy.deepcopy(d)
        d2["antenna_keepout"]["exempt_refs"] = sorted(set(d2["antenna_keepout"]["exempt_refs"]) | {"H1", "H2"})
        self.design_antenna = root / "design_h_exempt.yaml"
        self.design_antenna.write_text(yaml.safe_dump(d2))
        self._cache: dict = {}

    def board_for(self, defect: str | None) -> tuple[Path, Path]:
        if defect is None:
            return self.board, self.pro
        b = self.seeds[defect]
        return b, b.with_suffix(".kicad_pro")

    def result(self, defect: str | None, checker: str, rule: str):
        key = (defect, checker, rule)
        if key not in self._cache:
            b, pro = self.board_for(defect)
            tag = defect or "good"
            wd = self.root / "runs" / f"{tag}-{checker}"
            if checker == "drc_rule":
                ctx = D.make_ctx(b, pro, wd)
                self._cache[key] = D.check_rule(rule, ctx)
            else:
                geo = wd / "geometry.json"
                wd.mkdir(parents=True, exist_ok=True)
                if not geo.exists():
                    R.export_geometry(b, geo, wd)
                design = self.design_antenna if rule in ("GEN-PLN-009", "RF-FLR-002") else self.design
                ctx = GE.make_ctx(geo, b, design, self.version)
                self._cache[key] = GE.check_rule(rule, ctx)
        return self._cache[key]


@pytest.fixture(scope="module")
def world():
    root = C.ensure_work() / f"pytest-{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True)
    w = World(root)
    yield w
    shutil.rmtree(root, ignore_errors=True)


@pytest.mark.parametrize("defect,checker,rule", FLIPS, ids=[f"{d}:{r}:{c[:3]}" for d, c, r in FLIPS])
def test_rule_flips_on_seeded_defect(world, defect, checker, rule):
    good = world.result(None, checker, rule)
    bad = world.result(defect, checker, rule)
    assert good.status == "pass", f"{rule} should pass on the good board: {good.note} {good.measured}"
    assert bad.status == "fail", f"{rule} should fail on '{defect}': {bad.status} {bad.note} {bad.measured}"
    assert bad.evidence, "a failing rule must say what failed"
    assert bad.threshold and bad.inputs.get("board_sha256") and bad.tool.get("version")
    assert good.inputs["board_sha256"] != bad.inputs["board_sha256"]


@pytest.mark.parametrize("defect,checker,rule", STAYS_PASS)
def test_other_checker_unaffected(world, defect, checker, rule):
    assert world.result(defect, checker, rule).status == "pass"


def test_bad_rule_file_is_error_not_pass(world):
    """A syntax error makes KiCad drop the whole .kicad_dru and report nothing: the canary must turn that into 'error'."""
    bindings = {"DFM-STK-001": {"rules": [{"key": "bad", "constraint": "no_such_constraint", "bound": "min", "param": "min_trace_width_2layer_1oz", "shape": "per_object"}]}}
    ctx = D.make_ctx(world.board, world.pro, world.root / "canary")
    r = D.check_rule("DFM-STK-001", ctx, bindings)
    assert r.status == "error" and "canary" in r.note
    assert r.tool["canary"] is False


def test_thresholds_come_from_the_catalog(world, monkeypatch):
    """Change a catalog parameter and the verdict follows: 0.25 mm tracks pass a 0.1 mm floor and fail a 0.5 mm floor."""
    cat = copy.deepcopy(C.load_catalog())
    for p in cat["DFM-STK-001"]["parameters"]:
        if p["name"] == "min_trace_width_2layer_1oz":
            p["value"] = 0.5
    monkeypatch.setattr(C, "_CATALOG", cat)
    ctx = D.make_ctx(world.board, world.pro, world.root / "thr")
    r = D.check_rule("DFM-STK-001", ctx)
    assert r.status == "fail"
    assert r.measured["track_width"]["threshold"] == 0.5
    assert r.threshold[0]["source"] == "catalog" and r.threshold[0]["source_param"] == "min_trace_width_2layer_1oz"


def test_every_bound_rule_is_marked_full_in_the_catalog():
    cat = C.load_catalog()
    for rid in D.load_bindings():
        assert C.verify_automatable(rid, "drc") == "full", rid
    for rid in GE.load_bindings():
        assert C.verify_automatable(rid, "geometry_script") == "full", rid
    assert len(D.load_bindings()) >= 10 and len(GE.load_bindings()) >= 10
    assert set(D.load_bindings()) | set(GE.load_bindings()) <= set(cat)


def test_good_board_geometry_matches_drc_fromto(world):
    """The copper-path length agrees with KiCad's own fromTo() length (toolchain doc: C4-1 -> U1-1 = 9.6631 mm)."""
    geo = world.root / "good-geometry" / "geometry.json"
    geo.parent.mkdir(parents=True, exist_ok=True)
    R.export_geometry(world.board, geo, geo.parent)
    from checkers import geom_lib as G
    path = G.Board.load(geo).graph("+3V3").path(("C4", "1"), ("U1", "1"))
    assert abs(path["track_length_mm"] - 9.6631) < 0.01
