"""Static checks that need no KiCad: the catalog is valid, the generated views are current, skills are well formed,
and every checker binding points at a real catalog rule and parameter."""
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_catalog_validates():
    import validate

    assert validate.main([]) == 0
    assert validate.main([str(ROOT / "catalog" / "verifiers.yaml")]) == 0


def _snapshot():
    import hashlib

    h = {}
    for base in ("docs", "skills"):
        for f in sorted((ROOT / base).rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts and "_work" not in f.parts:
                h[str(f.relative_to(ROOT))] = hashlib.sha256(f.read_bytes()).hexdigest()
    return h


def test_generated_docs_and_skills_are_current():
    """Re-running the generators must not change any file under docs/ or skills/ (run `python3 tools/build_docs.py && python3 tools/build_skills.py` after catalog edits)."""
    before = _snapshot()
    for tool in ("build_docs.py", "build_skills.py"):
        subprocess.run([sys.executable, str(ROOT / "tools" / tool)], check=True, cwd=ROOT, capture_output=True)
    after = _snapshot()
    stale = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    assert not stale, f"generated files were stale (now regenerated): {stale[:10]}"


def _skills():
    return sorted((ROOT / "skills").glob("*/SKILL.md"))


def test_skills_have_valid_frontmatter():
    assert len(_skills()) >= 14
    for p in _skills():
        m = re.match(r"---\n(.*?)\n---\n", p.read_text(encoding="utf-8"), re.S)
        assert m, f"{p}: no frontmatter"
        fm = yaml.safe_load(m.group(1))
        assert fm["name"] == p.parent.name, p
        assert 40 < len(fm["description"]) <= 1024, (p, len(fm["description"]))
        assert set(fm) <= {"name", "description", "license", "allowed-tools", "metadata"}, (p, set(fm))


def test_every_domain_has_a_skill():
    import validate

    names = {p.parent.name for p in _skills()}
    for dom in validate.DOMAINS:
        assert "ee-" + dom.replace("_", "-") in names or dom == "general" and "ee-general-pcb" in names, dom


def test_bindings_reference_real_catalog_rules_and_params():
    from checkers import common as C
    from checkers import drc_rule as D
    from checkers import geometry as GE

    cat = C.load_catalog()
    assert len(cat) > 500
    for rid, b in D.load_bindings().items():
        assert rid in cat, rid
        names = {p["name"] for p in cat[rid].get("parameters") or []}
        for sub in b.get("rules") or []:
            if sub.get("param"):
                assert sub["param"] in names, (rid, sub["param"])
    for rid in GE.load_bindings():
        assert rid in cat, rid


def test_rules_helper_and_topic_index():
    helper = ROOT / "skills" / "ee-design-review" / "scripts" / "rules.py"
    shown = subprocess.run([sys.executable, str(helper), "show", "PWR-ARC-002", "THM-ARC-002"], capture_output=True, text=True, check=True).stdout
    assert "# PWR-ARC-002" in shown and "# THM-ARC-002" in shown and "**规则**" in shown
    found = subprocess.run([sys.executable, str(helper), "find", "AMS1117"], capture_output=True, text=True, check=True).stdout
    assert "PWR-ARC-002" in found and "topic-index" in found
    missing = subprocess.run([sys.executable, str(helper), "show", "XXX-YYY-999"], capture_output=True, text=True, check=True).stdout
    assert "not found" in missing
    topics = (ROOT / "skills" / "ee-design-review" / "references" / "topic-index.md").read_text(encoding="utf-8")
    assert "**AMS1117**" in topics and "**INA199**" in topics
