"""Generate the human-readable views from catalog/*.yaml (single source of truth).

Writes (all overwritten):
  docs/INDEX.md                 matrix, coverage, per-board list
  docs/VERIFICATION_BACKLOG.md  rules grouped by verification method + tool availability
  docs/by-stage/<stage>.md      process view, grouped by domain (compact)

Usage: build_docs.py            (run validate.py first)
"""
from collections import Counter, defaultdict
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs"

DOMAINS = [  # (key, 中文名, 垂直/横向)
    ("general", "通用 / 数模混合 MCU 板", "垂直"),
    ("power", "电源与功率", "垂直"),
    ("low_power", "低功耗 / 电池", "垂直"),
    ("rf", "射频与天线", "垂直"),
    ("audio", "音频", "垂直"),
    ("analog", "精密模拟 / 传感器前端", "垂直"),
    ("high_speed", "高速数字", "垂直"),
    ("emc_esd", "EMC / ESD / 浪涌", "横向"),
    ("hv_safety", "高压 / 隔离 / 安规", "横向"),
    ("thermal", "热设计", "横向"),
    ("dfm", "可制造 / 可装配 / 可测试", "横向"),
]
STAGES = [
    ("architecture", "架构与选型"), ("library", "符号封装库"), ("schematic", "原理图"),
    ("netlist", "网表与约束"), ("stackup", "叠层与规则"), ("floorplan", "分区规划"),
    ("placement", "器件布局"), ("routing", "布线"), ("plane_pour", "平面与铺铜"),
    ("manufacturing", "出图与制造"), ("verification", "签核验证"),
]
METHODS = [
    ("erc", "原理图 ERC"), ("drc", "PCB DRC / 自定义规则"), ("netlist_diff", "网表一致性"),
    ("bom_check", "BOM / 器件参数检查"), ("geometry_script", "几何脚本 (pcbnew)"),
    ("spice", "SPICE 仿真"), ("tline_calc", "传输线 / 载流计算"), ("em_sim", "电磁仿真"),
    ("si_sim", "信号完整性仿真"), ("pi_sim", "电源完整性仿真"), ("thermal_sim", "热仿真"),
    ("emc_precompliance", "EMC 预兼容"), ("bench", "实物测量"), ("review", "人工评审"),
]
SKILL = {  # domain key -> skill directory under skills/
    "general": "ee-general-pcb", "power": "ee-power", "low_power": "ee-low-power", "rf": "ee-rf", "audio": "ee-audio",
    "analog": "ee-analog", "high_speed": "ee-high-speed", "emc_esd": "ee-emc-esd", "hv_safety": "ee-hv-safety",
    "thermal": "ee-thermal", "dfm": "ee-dfm",
}
DOM_NAME = {k: n for k, n, _ in DOMAINS}
STG_NAME = dict(STAGES)
METH_NAME = dict(METHODS)
SEV_ORDER = {"must": 0, "should": 1, "consider": 2}
AUTO_ORDER = {"full": 0, "partial": 1, "manual": 2}


def load():
    rules, verifiers = [], []
    for p in sorted((REPO / "catalog").glob("*.yaml")):
        if p.name == "verifiers.yaml":
            continue
        rules += yaml.safe_load(p.read_text(encoding="utf-8")) or []
    vp = REPO / "catalog" / "verifiers.yaml"
    if vp.exists():
        verifiers = yaml.safe_load(vp.read_text(encoding="utf-8")) or []
    return rules, verifiers


def fmt_param(p):
    v = p.get("value")
    if p["op"] == "range" and isinstance(v, list):
        s = f"{v[0]} … {v[1]}"
    elif p["op"] in ("minimize", "maximize", "qualitative"):
        s = p["op"] if v is None else f"{p['op']} {v}"
    else:
        s = f"{p['op']} {v}"
    u = p.get("unit")
    return f"{s} {u}".strip() if u else s


def render_rule(r):
    o = [f'<a id="{r["id"]}"></a>', f'#### {r["id"]} · {r["title"]}']
    meta = [f"`{r['severity']}`", f"可信度 `{r['confidence']}`"]
    if r.get("applies_to"): meta.append("适用: " + ", ".join(r["applies_to"]))
    if r.get("tags"): meta.append("标签: " + ", ".join(r["tags"]))
    o += [" · ".join(meta), "", f"**规则** {r['rule'].strip()}", "", f"**依据** {r['rationale'].strip()}", ""]
    if r.get("parameters"):
        o += ["| 参数 | 判据 | 备注 |", "|---|---|---|"]
        for p in r["parameters"]:
            o.append(f"| `{p['name']}` | {fmt_param(p)} | {(p.get('note') or '').replace('|', '/')} |")
        o.append("")
    o.append("**验证**")
    for v in r["verify"]:
        o.append(f"- `{v['method']}`（{v['automatable']}）· {v['tool'].strip()} — {v['check'].strip()}")
    o.append("")
    if r.get("conflicts"):
        o += [f"**来源分歧** {r['conflicts'].strip()}", ""]
    o.append("**来源**")
    for s in r["sources"]:
        label = f"[{s['title']}]({s['url']})" if s.get("url") else f"{s['title']}（{s.get('ref', '')}）"
        extra = ", ".join(x for x in (s.get("publisher"), s["kind"], s.get("section")) if x)
        o.append(f"- {label} — {extra}")
    o.append("")
    return "\n".join(o)


def sort_rules(rs):
    return sorted(rs, key=lambda r: (SEV_ORDER[r["severity"]], r["id"]))


def domain_reference(rules, key):
    """Full rule text of one domain, grouped by stage: skills/<skill>/references/rules.md."""
    name, kind = next((n, k) for d, n, k in DOMAINS if d == key)
    rs = [r for r in rules if r["domain"] == key]
    o = [f"# {name}（{key}）— 规则全文", "", f"{kind}领域 · {len(rs)} 条规则 · 由 `catalog/*.yaml` 生成，请改 YAML 不要改本文件。"
         "用 `grep -n \"<规则ID>\" rules.md` 定位单条，不要整份读。", ""]
    c = Counter(r["stage"] for r in rs)
    o.append("环节分布：" + "，".join(f"{STG_NAME[st]} {c[st]}" for st, _ in STAGES if c[st]))
    o.append("")
    for sk, sn in STAGES:
        srs = sort_rules([r for r in rs if r["stage"] == sk])
        if not srs:
            continue
        o += [f"## {sn}（{sk}）", ""]
        o += [render_rule(r) for r in srs]
    return "\n".join(o) + "\n"


def rule_link(r, up):
    """Link to a rule's full text from a file `up` directories below docs/ (0 = docs/, 1 = docs/by-stage/)."""
    return f"{'../' * (up + 1)}skills/{SKILL[r['domain']]}/references/rules.md#{r['id']}"


def by_stage(rules):
    out = OUT / "by-stage"
    out.mkdir(exist_ok=True)
    for sk, sn in STAGES:
        rs = [r for r in rules if r["stage"] == sk]
        if not rs:
            continue
        o = [f"# {sn}（{sk}）", "", f"{len(rs)} 条规则 · 由 `catalog/*.yaml` 生成。详情见各领域文件。", ""]
        for dk, dn, _ in DOMAINS:
            drs = sort_rules([r for r in rs if r["domain"] == dk])
            if not drs:
                continue
            o += [f"## {dn}", "", "| ID | 规则 | 级别 | 可信度 | 最强验证 |", "|---|---|---|---|---|"]
            for r in drs:
                best = min(r["verify"], key=lambda v: AUTO_ORDER[v["automatable"]])
                o.append(f"| [{r['id']}]({rule_link(r, 1)}) | {r['title']} | {r['severity']} | {r['confidence']} | {best['method']} ({best['automatable']}) |")
            o.append("")
        (out / f"{sk}.md").write_text("\n".join(o), encoding="utf-8")


def by_board(rules):
    out = OUT / "by-board"
    out.mkdir(exist_ok=True)
    cf = [r for r in rules if "cat-feeder" in (r.get("tags") or [])]
    o = ["# 示例板（猫咪喂食器）— 相关规则清单", "",
         f"{len(cf)} 条，按级别（must → should → consider）再按领域排序。由 `catalog/*.yaml` 生成。", ""]
    for sev in ("must", "should", "consider"):
        srs = [r for r in cf if r["severity"] == sev]
        if not srs:
            continue
        o += [f"## {sev}（{len(srs)}）", "", "| ID | 规则 | 环节 | 可信度 | 最强验证 |", "|---|---|---|---|---|"]
        for dk, _, _ in DOMAINS:
            for r in sorted((x for x in srs if x["domain"] == dk), key=lambda x: x["id"]):
                best = min(r["verify"], key=lambda v: AUTO_ORDER[v["automatable"]])
                flag = " ⚠" if r.get("conflicts") else ""
                o.append(f"| [{r['id']}]({rule_link(r, 1)}) | {r['title']}{flag} | {STG_NAME[r['stage']]} | {r['confidence']} | {best['method']} ({best['automatable']}) |")
        o.append("")
    o.append("⚠ = 来源之间有分歧，详情见规则里的「来源分歧」。")
    (out / "cat-feeder.md").write_text("\n".join(o) + "\n", encoding="utf-8")


def index(rules, verifiers):
    n = len(rules)
    cd = Counter(r["domain"] for r in rules)
    mat = Counter((r["domain"], r["stage"]) for r in rules)
    o = ["# 电路设计最佳实践库 — 索引", "",
         f"共 **{n}** 条规则，{len({u['url'] for r in rules for u in r['sources'] if u.get('url')})} 个不同的来源 URL。本文件由 `tools/build_docs.py` 从 `catalog/*.yaml` 生成。", ""]
    o += ["## 领域 × 环节", "", "| 领域 | " + " | ".join(sn for _, sn in STAGES) + " | 合计 |", "|---|" + "---|" * (len(STAGES) + 1)]
    for dk, dn, kind in DOMAINS:
        if not cd[dk]:
            continue
        cells = [str(mat[(dk, sk)] or "") for sk, _ in STAGES]
        o.append(f"| [{dn}](../skills/{SKILL[dk]}/SKILL.md)（{kind}） | " + " | ".join(cells) + f" | **{cd[dk]}** |")
    tot = [str(sum(mat[(dk, sk)] for dk, _, _ in DOMAINS) or "") for sk, _ in STAGES]
    o += ["| **合计** | " + " | ".join(tot) + f" | **{n}** |", ""]
    o += ["按环节看：" + "　".join(f"[{sn}](by-stage/{sk}.md)" for sk, sn in STAGES if any(r['stage'] == sk for r in rules)), ""]

    sev, conf = Counter(r["severity"] for r in rules), Counter(r["confidence"] for r in rules)
    o += ["## 级别与可信度", "", "| | high | medium | low | 合计 |", "|---|---|---|---|---|"]
    for s in ("must", "should", "consider"):
        row = [sum(1 for r in rules if r["severity"] == s and r["confidence"] == c) for c in ("high", "medium", "low")]
        o.append(f"| {s} | " + " | ".join(map(str, row)) + f" | {sev[s]} |")
    o += ["", f"含 `conflicts`（来源有分歧）的规则：{sum(1 for r in rules if r.get('conflicts'))} 条。", ""]

    o += ["## 验证覆盖", "", "每条规则可有多种验证方式；下表按方式统计规则条数（同一规则在多行重复计入）。", "",
          "| 验证方式 | full | partial | manual | 规则数 |", "|---|---|---|---|---|"]
    for mk, mn in METHODS:
        c = Counter()
        ids = set()
        for r in rules:
            for v in r["verify"]:
                if v["method"] == mk:
                    c[v["automatable"]] += 1
                    ids.add(r["id"])
        if ids:
            o.append(f"| `{mk}` {mn} | {c['full']} | {c['partial']} | {c['manual']} | {len(ids)} |")
    full_any = sum(1 for r in rules if any(v["automatable"] == "full" for v in r["verify"]))
    o += ["", f"至少有一种验证方式可 **完全自动化** 的规则：{full_any} / {n}（{100 * full_any // max(n, 1)}%）。", ""]
    o += ["| 领域 | 规则数 | 含完全自动化验证 | 仅人工 / 实测 |", "|---|---|---|---|"]
    for dk, dn, _ in DOMAINS:
        rs = [r for r in rules if r["domain"] == dk]
        if not rs:
            continue
        f = sum(1 for r in rs if any(v["automatable"] == "full" for v in r["verify"]))
        m = sum(1 for r in rs if all(v["automatable"] == "manual" for v in r["verify"]))
        o.append(f"| {dn} | {len(rs)} | {f} | {m} |")
    o.append("")

    cf = [r for r in rules if "cat-feeder" in (r.get("tags") or [])]
    o += [f"## 与示例板（猫咪喂食器）相关（{len(cf)} 条，其中 must {sum(1 for r in cf if r['severity'] == 'must')} 条）", "",
          "标签 `cat-feeder` 表示规则适用于开源示例板 [fxp/cat-feeder](https://github.com/fxp/cat-feeder)（ESP32-C3 模块、电机 MOSFET、INA199 检流、AMS1117 LDO、HX711、2 层板、JLC 贴片）的某个电路，范围较宽。[by-board/cat-feeder.md](by-board/cat-feeder.md) 演示怎样为一块具体的板筛出规则并按优先级排序。", "",
          "| 领域 | 相关条数 | 其中 must |", "|---|---|---|"]
    for dk, dn, _ in DOMAINS:
        drs = [r for r in cf if r["domain"] == dk]
        if drs:
            o.append(f"| {dn} | {len(drs)} | {sum(1 for r in drs if r['severity'] == 'must')} |")
    o += ["", "## 文件", "",
          "* [`catalog/*.yaml`](../catalog/) — 规则本体（唯一事实来源），格式见 [SCHEMA.md](SCHEMA.md)",
          "* [`catalog/verifiers.yaml`](../catalog/verifiers.yaml) — 验证工具目录；[VERIFICATION_TOOLCHAIN.md](VERIFICATION_TOOLCHAIN.md) — 本机已验证的命令与差距",
          "* [VERIFICATION_BACKLOG.md](VERIFICATION_BACKLOG.md) — 规则按验证方式分组的待办（下一步仿真 / EDA 校验的工作包）",
          "* [`skills/`](../skills/) — 按领域生成的 skill（每个含规则索引与全文）；`by-stage/`、`by-board/` — 按环节、按板子的阅读视图",
          "* [RESEARCH_BRIEF.md](RESEARCH_BRIEF.md) — 调研方法与质量要求"]
    (OUT / "INDEX.md").write_text("\n".join(o) + "\n", encoding="utf-8")


def backlog(rules, verifiers):
    vmeth = defaultdict(list)
    for v in verifiers:
        for m in v["methods"]:
            vmeth[m].append(v)
    o = ["# 验证待办 — 规则按验证方式分组", "",
         "由 `build_docs.py` 生成。每个方法列出：本机可用的工具（来自 `verifiers.yaml`）、可完全自动化的规则（带检查说明）、可部分自动化的规则（只列 ID，检查说明在规则详情里）。下一步按方法建立检查器，每个检查器输出 `rule id → pass/fail/evidence`。", ""]
    for mk, mn in METHODS:
        hits = [(r, v) for r in rules for v in r["verify"] if v["method"] == mk]
        if not hits:
            continue
        cnt = Counter(v["automatable"] for _, v in hits)
        o += [f"## `{mk}` — {mn}", "", f"full {cnt['full']} · partial {cnt['partial']} · manual {cnt['manual']}", ""]
        tools = vmeth.get(mk, [])
        o.append("可用工具：" + ("；".join(f"{t['name']}（{t['status']}）" for t in tools) if tools else "（`verifiers.yaml` 里还没有登记）"))
        o.append("")
        key = lambda x: (SEV_ORDER[x[0]["severity"]], x[0]["id"])
        full = sorted([(r, v) for r, v in hits if v["automatable"] == "full"], key=key)
        if full:
            o += [f"### 可完全自动化（{len(full)}）", "", "| ID | 规则 | 级别 | 检查 |", "|---|---|---|---|"]
            for r, v in full:
                chk = v["check"].strip().replace("|", "/").replace("\n", " ")
                if len(chk) > 220:
                    chk = chk[:220].rstrip() + "…"
                o.append(f"| [{r['id']}]({rule_link(r, 0)}) | {r['title']} | {r['severity']} | {chk} |")
            o.append("")
        part = sorted([(r, v) for r, v in hits if v["automatable"] == "partial"], key=key)
        if part:
            o += [f"### 可部分自动化（{len(part)}）", "", "、".join(f"[{r['id']}]({rule_link(r, 0)})" for r, _ in part), ""]
        man = [r for r, v in hits if v["automatable"] == "manual"]
        if man:
            o += [f"### 人工 / 实测（{len(man)}）", "", "见各规则详情；此处不列。", ""]
    (OUT / "VERIFICATION_BACKLOG.md").write_text("\n".join(o), encoding="utf-8")


def main():
    rules, verifiers = load()
    if not rules:
        print("no rules found"); return 1
    by_stage(rules)
    by_board(rules)
    index(rules, verifiers)
    backlog(rules, verifiers)
    print(f"built views for {len(rules)} rules, {len(verifiers)} verifiers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
