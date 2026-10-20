"""Shared pytest setup. The seeded-defect tests need KiCad 10 and a reference board; they skip cleanly without them."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "ee-pcb-verify" / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))

import pytest  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "kicad_bp: needs KiCad 10 installed (rule-checker seeded-defect tests)")


def pytest_collection_modifyitems(config, items):
    from checkers import common as C

    if C.kicad_available():
        return
    skip = pytest.mark.skip(reason="KiCad not installed (set EE_KICAD_APP, or KCLI and KPY)")
    for item in items:
        if item.get_closest_marker("kicad_bp"):
            item.add_marker(skip)
