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


def test_generated_docs_and_skills_are_current(tmp_path):
    """Re-running the generators must not change tracked files (run `python tools/build_docs.py && python tools/build_skills.py`)."""
    for tool in ("build_docs.py", "build_skills.py"):
        subprocess.run([sys.executable, str(ROOT / "tools" / tool)], check=True, cwd=ROOT, capture_output=True)
    diff = subprocess.run(["git", "status", "--porcelain", "docs", "skills"], cwd=ROOT, capture_output=True, text=True).stdout
    if not (ROOT / ".git").exists():
        pytest.skip("not a git checkout")
    assert not [l for l in diff.splitlines() if l.startswith(" M")], f"generated files are stale:\n{diff}"


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
