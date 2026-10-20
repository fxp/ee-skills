#!/usr/bin/env python3
"""Look rules up across the sibling domain skills without reading whole files.

    python3 rules.py find AMS1117 ldo thermal      # index rows matching ANY keyword, best matches first
    python3 rules.py show PWR-ARC-002 THM-ARC-002  # full text of rules (rule, rationale, parameters, verify, sources)
    python3 rules.py show --all-must ee-rf         # the must-level rule IDs of one domain skill

Looks for skills/ee-*/references/{rules-index.md,rules.md} next to this skill (a plugin install or a repo checkout).
"""
import re
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
ANCHOR = re.compile(r'<a id="([A-Z]+-[A-Z]+-\d{3})"></a>')


def domain_dirs():
    return sorted(p for p in SKILLS.glob("ee-*/") if (p / "references" / "rules.md").exists())


def cmd_find(words):
    words = [w.lower() for w in words]
    hits = []
    for d in domain_dirs():
        for ref in ("rules-index.md",):
            for line in (d / "references" / ref).read_text(encoding="utf-8").splitlines():
                if not line.startswith("| ") or line.startswith("| ID"):
                    continue
                low = line.lower()
                score = sum(w in low for w in words)
                if score:
                    hits.append((-score, d.name, line))
    topic = SKILLS / "ee-design-review" / "references" / "topic-index.md"
    if topic.exists():
        for line in topic.read_text(encoding="utf-8").splitlines():
            if line.startswith("- **") and any(w in line.lower() for w in words):
                hits.append((-sum(w in line.lower() for w in words) + 0.5, "topic-index", line))
    for _, skill, line in sorted(hits, key=lambda h: (h[0], h[1], h[2]))[:60]:
        print(f"[{skill}] {line}")
    if not hits:
        print("no match; try another keyword or read references/topic-index.md")


def cmd_show(ids):
    for rid in ids:
        found = False
        for d in domain_dirs():
            text = (d / "references" / "rules.md").read_text(encoding="utf-8")
            m = re.search(rf'<a id="{re.escape(rid)}"></a>', text)
            if not m:
                continue
            nxt = ANCHOR.search(text, m.end())
            heading = re.search(r"(?m)^## .*$", text[m.end():nxt.start() if nxt else len(text)])
            end = nxt.start() if nxt else len(text)
            if heading:  # the block ends at the next stage heading too
                end = min(end, m.end() + heading.start())
            print(f"# {rid}  ({d.name})\n{text[m.end():end].strip()}\n")
            found = True
            break
        if not found:
            print(f"# {rid}: not found in {SKILLS}\n")


def cmd_musts(skill):
    d = SKILLS / skill
    for line in (d / "SKILL.md").read_text(encoding="utf-8").splitlines():
        if re.match(r"\| [A-Z]+-[A-Z]+-\d{3} \|", line):
            print(line)


def main(argv):
    if len(argv) < 2 or argv[0] not in ("find", "show"):
        print(__doc__)
        return 2
    if argv[0] == "find":
        cmd_find(argv[1:])
    elif argv[1] == "--all-must" and len(argv) == 3:
        cmd_musts(argv[2])
    else:
        cmd_show(argv[1:])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
