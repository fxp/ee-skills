"""One-command rule checking: catalog rules -> drc_rule + geometry checkers -> results.json / results.md.

    python run.py --board X.kicad_pcb --design design/my_board.yaml                     # both checkers, results in ./ee-results/<today>/
    python run.py --board X.kicad_pcb --design D.yaml --pro X.kicad_pro --out some/dir
    python run.py --board X.kicad_pcb --design D.yaml --rules DFM-PLC-003,DFM-STK-001 --checkers geometry

The input board is COPIED into a private work directory under checkers/_work/ (never opened for writing, never
via /tmp); KiCad runs against the copy with private config/documents dirs.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from checkers import common as C          # noqa: E402
from checkers import drc_rule as D        # noqa: E402
from checkers import geometry as GE       # noqa: E402



def export_geometry(board: Path, out: Path, workdir: Path) -> Path:
    cp = C.run([C.KPY, "-I", HERE / "export_geometry.py", board, out], env=C.kicad_env(workdir), timeout=300)
    if not out.exists():
        raise RuntimeError(f"geometry export failed rc={cp.returncode}: {cp.stderr[-400:]}")
    return out


def run_all(board: Path, pro: Path, design: Path, workdir: Path, checkers: list[str], rules: list[str] | None, workers: int) -> dict:
    t0 = time.time()
    board_copy, pro_copy = C.copy_board(board, pro, workdir / "board")
    version = C.kicad_version()
    results = []
    geo_path = None
    if "drc_rule" in checkers:
        ctx = D.make_ctx(board_copy, pro_copy, workdir)
        results += D.check_all(ctx, rules, workers=workers)
    if "geometry" in checkers:
        geo_path = export_geometry(board_copy, workdir / "geometry.json", workdir)
        gctx = GE.make_ctx(geo_path, board_copy, design, version)
        results += GE.check_all(gctx, rules)
    for rid in (rules or []):
        if rid not in D.load_bindings() and rid not in GE.load_bindings():
            h = C.catalog_head(rid) if rid in C.load_catalog() else {"severity": "", "title": ""}
            results.append(C.Result(rule_id=rid, checker="-", status="skipped", severity=h["severity"], title=h["title"],
                                    note="no drc_rule / geometry binding for this rule id"))
    order = {"fail": 0, "error": 1, "pass": 2, "skipped": 3}
    counts = {s: sum(1 for r in results if r.status == s) for s in ("pass", "fail", "error", "skipped")}
    cat = C.load_catalog()
    full = lambda m: {i for i, r in cat.items() if any(v["method"] == m and v["automatable"] == "full" for v in r["verify"])}  # noqa: E731
    coverage = {"drc_full_in_catalog": len(full("drc")), "drc_wired": len(D.load_bindings()), "geometry_script_full_in_catalog": len(full("geometry_script")),
                "geometry_wired": len(GE.load_bindings())}
    return {
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "source_board": str(board), "source_board_sha256": C.sha256_file(board), "run_copy": C.rel(board_copy),
        "kicad_version": version, "catalog_rules": len(C.load_catalog()), "checkers": checkers,
        "design_file": C.rel(design),
        "geometry_json_sha256": C.sha256_file(geo_path) if geo_path else None, "duration_s": round(time.time() - t0, 1), "counts": counts, "coverage": coverage,
        "results": [r.as_json() for r in sorted(results, key=lambda r: (order.get(r.status, 9), r.checker, r.rule_id))],
    }


def short(v, n=90) -> str:
    s = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
    return s if len(s) <= n else s[: n - 1] + "…"


def _scalar(v):
    if isinstance(v, float):
        return round(v, 3)
    if isinstance(v, (list, dict)):
        return "…"
    return v


def measured_summary(r: dict) -> str:
    out = []
    for k, m in (r.get("measured") or {}).items():
        if r["checker"] == "drc_rule" and isinstance(m, dict) and "violations" in m:
            ext = m.get("observed_extreme")
            out.append(f"{k}={ext if ext is not None else '-'}" + (f" ({m['violations']} viol)" if m["violations"] else ""))
        elif isinstance(m, dict):
            out.append(f"{k}={_scalar(m.get('measured'))}")
        else:
            out.append(f"{k}={_scalar(m)}")
    return "; ".join(out)


def threshold_summary(r: dict) -> str:
    th = r.get("threshold")
    out = []
    for t in (th if isinstance(th, list) else [th]):
        if not t or not t.get("op"):
            continue
        src = t.get("source")
        tag = f"({t.get('source_param')})" if src == "catalog" else ("(design file)" if src == "design_yaml" else "(rule text)")
        op = ("NOT " if t.get("negated") else "") + t["op"]
        out.append(f"{t.get('key', '')} {op} {_scalar(t.get('value'))} {t.get('unit') or ''} {tag}".replace("  ", " ").strip())
    return "; ".join(out)


def write_md(report: dict, path: Path) -> None:
    c = report["counts"]
    lines = [f"# 规则检查结果 {report['generated'][:10]}", "",
             f"被测板：`{report['source_board']}`"
             f"（sha256 `{report['source_board_sha256'][:12]}…`，只用拷贝）· KiCad {report['kicad_version']} · 检查器 {', '.join(report['checkers'])} · 用时 {report['duration_s']} s",
             "", f"**{len(report['results'])} 条规则：{c['pass']} 通过 · {c['fail']} 不通过 · {c['error']} 出错 · {c['skipped']} 跳过。** "
             "阈值列括号里是来源：目录 `parameters` 的名字 / `design file`（目录写“项目设定”的阈值，来自 --design 指定的设计文件）/ `rule text`（只在目录规则或 verify.check 文字里有、`parameters` 里没有数字）。"
             "DRC 行的“实测”是探测所得的最接近值（观测到的最小/最大），违规数在括号里。", "",
             "| 规则 | 检查器 | 级别 | 结果 | 实测 | 阈值 | 证据 |", "|---|---|---|---|---|---|---|"]
    for r in report["results"]:
        ev = "；".join(e.get("message", "") for e in r.get("evidence", [])[:2]) or (r.get("note") or "")
        lines.append(f"| {r['rule_id']} | {r['checker']} | {r['severity']} | **{r['status']}** | {short(measured_summary(r), 140)} | {short(threshold_summary(r), 140)} | {short(ev, 160)} |")
    lines.append("")
    path.write_text("\n".join(lines).replace("|  |", "| |"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", type=Path, required=True, help=".kicad_pcb to check (copied, never modified)")
    ap.add_argument("--pro", type=Path, default=None, help=".kicad_pro holding the net classes (default: <board>.kicad_pro)")
    ap.add_argument("--design", type=Path, required=True, help="board facts the geometry checks need; start from design/template.yaml")
    ap.add_argument("--out", type=Path, default=None, help="results dir (default ./ee-results/<today>)")
    ap.add_argument("--checkers", default="drc_rule,geometry")
    ap.add_argument("--rules", default=None, help="comma-separated rule ids (default: every bound rule)")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--keep-work", action="store_true", help="keep the run's work directory (board copy, per-rule DRC dirs, geometry.json)")
    ap.add_argument("--strict", action="store_true", help="exit 1 when any rule fails (default: exit 1 only on tool errors)")
    a = ap.parse_args(argv)
    if not C.kicad_available():
        C.die(f"KiCad not found at {C.KICAD_APP}")
    pro = a.pro or a.board.with_suffix(".kicad_pro")
    if not pro.exists():
        C.die(f"no .kicad_pro at {pro}; pass --pro (net classes and DRC severities live there)")
    out = a.out or (Path.cwd() / "ee-results" / dt.date.today().isoformat())
    out.mkdir(parents=True, exist_ok=True)
    workdir = C.ensure_work() / ("run-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S"))
    workdir.mkdir(parents=True, exist_ok=True)
    rules = a.rules.split(",") if a.rules else None
    report = run_all(a.board.resolve(), pro.resolve(), a.design.resolve(), workdir, a.checkers.split(","), rules, a.workers)
    (out / "results.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    write_md(report, out / "results.md")
    if not a.keep_work:
        shutil.rmtree(workdir, ignore_errors=True)
    c = report["counts"]
    print(f"{len(report['results'])} rules: {c['pass']} pass, {c['fail']} fail, {c['error']} error, {c['skipped']} skipped -> {out}")
    return 1 if (c["error"] or (a.strict and c["fail"])) else 0


if __name__ == "__main__":
    raise SystemExit(main())
