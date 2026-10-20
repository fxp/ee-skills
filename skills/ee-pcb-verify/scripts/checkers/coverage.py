"""Render <out>/NOT_AUTOMATED.md: which automatable:full rules the checkers do not cover, and why.

    python coverage.py [--out DIR] [--results DIR]
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from checkers import common as C  # noqa: E402
from checkers import drc_rule as D  # noqa: E402
from checkers import geometry as GE  # noqa: E402

CATS = {
    "needs_project_setup": "能写，但板子/项目里没有可选对象（网络类、分区、角色表）",
    "needs_other_artifact": "要检查的是 Gerber / 钻孔 / CPL / 库文件，不是 .kicad_pcb（另一个检查器）",
    "needs_data": "数据不在板文件或工具输出里（元件高度、阻焊网宽、库表）",
    "empirical_threshold": "目录写“项目设定 / 经验值”，仓库里也没有定数",
    "not_applicable": "这块板上没有这类电路",
    "not_done": "现有积木就能做，本次没做",
    "manual": "需要人决定 / 同意",
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path.cwd() / "ee-results" / dt.date.today().isoformat())
    ap.add_argument("--results", type=Path, default=None, help="results dir holding results.json (default: --out)")
    a = ap.parse_args(argv)
    cat = C.load_catalog()
    reasons = C.load_yaml(C.HERE / "bindings" / "not_wired.yaml")
    wired = {"drc": set(D.load_bindings()), "geometry_script": set(GE.load_bindings())}
    key = {"drc": "drc", "geometry_script": "geometry_script"}
    lines = [f"# 没有被检查器覆盖的可自动化规则 {dt.date.today().isoformat()}", "",
             "目录里 `verify.method = drc | geometry_script` 且 `automatable: full` 的规则，减去已接入 `drc_rule` / `geometry` 的。"
             "带 `cat-feeder` 标签的逐条写原因（`bindings/not_wired.yaml`），其余只按领域计数。", ""]
    total = collections.Counter()
    for m in ("drc", "geometry_script"):
        full = [i for i, r in cat.items() if any(v["method"] == m and v["automatable"] == "full" for v in r["verify"])]
        un = [i for i in full if i not in wired[m]]
        cf = [i for i in un if "cat-feeder" in (cat[i].get("tags") or [])]
        other = [i for i in un if i not in cf]
        total[m] = (len(full), len(full) - len(un), len(cf), len(other))
        lines += [f"## `{m}`：目录 {len(full)} 条 full，已接入 {len(full) - len(un)}，未接入 {len(un)}（cat-feeder 标签 {len(cf)}，其它 {len(other)}）", "",
                  "| 规则 | 级别 | 类别 | 原因 |", "|---|---|---|---|"]
        for i in sorted(cf):
            r = reasons.get(m if m == "drc" else "geometry_script", {}).get(i)
            lines.append(f"| {i} {cat[i]['title']} | {cat[i]['severity']} | {r['cat'] if r else '**未标注**'} | {r['why'] if r else ''} |")
        by_dom = collections.Counter(cat[i]["domain"] for i in other)
        lines += ["", "其它（没有 cat-feeder 标签）按领域：" + "，".join(f"{d} {n}" for d, n in sorted(by_dom.items())) + "。"
                  "这些是音频 / 高速 / 射频 / 高压 / 通用规则，多数针对这块板上没有的电路（Class-D、DDR、以太网、隔离……）。", ""]
    cnt = collections.Counter(reasons.get("drc", {}).get(i, {}).get("cat") for i in reasons.get("drc", {})) + collections.Counter(
        reasons.get("geometry_script", {}).get(i, {}).get("cat") for i in reasons.get("geometry_script", {}))
    lines += ["## 类别说明与计数（cat-feeder 标签的未接入规则）", "", "| 类别 | 条数 | 含义 |", "|---|---|---|"]
    for k, v in CATS.items():
        lines.append(f"| {k} | {cnt.get(k, 0)} | {v} |")
    res_dir = a.results or a.out
    if (res_dir / "results.json").exists():
        rep = json.loads((res_dir / "results.json").read_text())
        notes = collections.Counter()
        for r in rep["results"]:
            if "not evaluated:" in (r.get("note") or ""):
                for part in r["note"].split("not evaluated:")[1].split(";"):
                    notes[(r["rule_id"], part.strip())] += 1
        lines += ["", "## 已接入但有一部分没评估的规则（`note` 里的 `not evaluated`）", "", "| 规则 | 没评估的部分 |", "|---|---|"]
        for (rid, txt), _ in sorted(notes.items()):
            lines.append(f"| {rid} | {txt} |")
    lines += ["", "## 目录里不是 full 的规则", "",
              "`partial` / `manual` 的 DRC 与 geometry_script，以及 `spice` `bom_check` `netlist_diff` `erc` `em_sim` `thermal_sim` `bench` `review` 等方法，不在这一步的范围内"
              "（VERIFICATION_TOOLCHAIN §3.4 第 3、4 步及之后）。"]
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "NOT_AUTOMATED.md").write_text("\n".join(lines) + "\n")
    print(f"wrote {a.out / 'NOT_AUTOMATED.md'}")
    missing = [i for m in ("drc", "geometry_script") for i, r in cat.items()
               if "cat-feeder" in (r.get("tags") or []) and any(v["method"] == m and v["automatable"] == "full" for v in r["verify"])
               and i not in wired[m] and i not in reasons.get(m, {})]
    if missing:
        print("rules without a reason in not_wired.yaml:", missing)
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
