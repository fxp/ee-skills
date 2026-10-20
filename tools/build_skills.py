"""Generate the eleven domain skills (skills/ee-<domain>/) and the copied references of the workflow skills from catalog/*.yaml.

For every domain:  skills/<skill>/SKILL.md            (generated: scope, how to use, stage counts, must-level rules)
                   skills/<skill>/references/rules-index.md   one line per rule, grouped by stage
                   skills/<skill>/references/rules.md         full rule text (grep it by rule ID, do not read it whole)
The three workflow skills (ee-design-review, ee-pcb-verify, ee-catalog-maintain) are hand-written; only their
references/ copies of docs/ files are refreshed here.

Usage: python tools/build_skills.py        (run tools/validate.py first; output is deterministic)
"""
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_docs as B  # noqa: E402

REPO = B.REPO
SKILLS = REPO / "skills"

# key -> (English title, description, related skills)
META = {
    "general": (
        "General mixed-signal MCU board",
        "Sourced best-practice rules for the whole flow of an ordinary mixed-signal MCU board: requirements and part choice, "
        "symbol/footprint libraries, schematic, netlist and net classes, stackup, floorplan, placement, routing, planes and "
        "copper pours, sign-off. Use first for any PCB design or review, for decoupling, crystal, reset/boot-pin, return-path "
        "and grounding questions. 通用 PCB 设计与评审、原理图检查、去耦、晶振、回流路径、地平面、叠层、布局布线、铺铜。",
        ["ee-power", "ee-emc-esd", "ee-dfm", "ee-design-review", "ee-pcb-verify"],
    ),
    "power": (
        "Power conversion and power stages",
        "Sourced best-practice rules for power circuits: buck/boost/flyback layout (hot loop, switch node, feedback routing), "
        "LDO selection and thermal limits (AMS1117-class), motor drivers and MOSFET switching, high-current copper (IPC-2152), "
        "reverse-polarity/fuse/TVS input protection, PDN and decoupling. Use when designing or reviewing any supply, LDO, DC-DC, "
        "motor or battery-charger circuit. 电源、开关电源布局、LDO、电机驱动、大电流走线、输入保护、去耦。",
        ["ee-thermal", "ee-emc-esd", "ee-low-power", "ee-general-pcb", "ee-pcb-verify"],
    ),
    "low_power": (
        "Low power and battery-powered design",
        "Sourced best-practice rules for low-power and battery/IoT designs: sleep-current budgets, leakage paths (pull-ups, dividers, "
        "ESD diodes, level shifters), load switches and power gating, quiescent-current regulator choice, Wi-Fi/BLE burst loads vs "
        "battery resistance, nA-level measurement. Use for battery-life, deep-sleep, leakage or brown-out questions. "
        "低功耗、电池供电、睡眠电流预算、漏电、负载开关、掉电。",
        ["ee-power", "ee-rf", "ee-general-pcb", "ee-pcb-verify"],
    ),
    "rf": (
        "RF and antennas",
        "Sourced best-practice rules for RF and antenna circuits on PCBs: 2.4 GHz module and chip/PCB antenna keep-outs, pi matching "
        "networks, controlled-impedance microstrip/CPWG, via fencing and RF grounding, shielding, TX/RX isolation, tuning and "
        "verification with a VNA or S-parameter simulation. Use for Wi-Fi/BLE/LoRa/GNSS boards, antenna clearance, 50-ohm routing. "
        "射频、天线净空、阻抗匹配、50 欧姆走线、过孔屏蔽、VNA 调试。",
        ["ee-high-speed", "ee-emc-esd", "ee-general-pcb", "ee-pcb-verify"],
    ),
    "audio": (
        "Audio circuits",
        "Sourced best-practice rules for audio circuits: codec/ADC/DAC signal chains, AC-coupling capacitor dielectric and distortion, "
        "op-amp stability with capacitive loads, ground partitioning and return currents, Class-D output filters and layout, I2S "
        "clocking, THD+N/SNR verification. Use for microphone, line-in, headphone and speaker-amplifier designs. "
        "音频、编解码器、D 类功放、耦合电容、接地、THD+N。",
        ["ee-analog", "ee-power", "ee-emc-esd", "ee-general-pcb"],
    ),
    "analog": (
        "Precision analog and sensor front-ends",
        "Sourced best-practice rules for precision/low-noise analog: error and noise budgets, op-amp stability, ADC drivers and "
        "anti-alias filters, reference routing, bridge/load-cell front-ends (HX711-class), shunt current sensing with Kelvin "
        "connections (INA199-class), guard rings and leakage, AGND/DGND. Use for sensor, ADC, current-sense or instrumentation "
        "circuits. 精密模拟、传感器前端、ADC、分流检流、开尔文连接、保护环、低噪声。",
        ["ee-audio", "ee-power", "ee-general-pcb", "ee-pcb-verify"],
    ),
    "high_speed": (
        "High-speed digital",
        "Sourced best-practice rules for high-speed digital interfaces: USB, Ethernet (RMII/RGMII), DDR, LVDS, MIPI, PCIe, SPI/I2C on "
        "long wires; controlled impedance and stackup, differential-pair coupling and skew, length matching, return paths and via "
        "transitions, termination, crosstalk, SI simulation. Use for any interface faster than a few tens of MHz or with sub-ns "
        "edges. 高速数字、差分对、阻抗控制、等长、端接、串扰、USB、以太网、DDR。",
        ["ee-rf", "ee-emc-esd", "ee-general-pcb", "ee-pcb-verify"],
    ),
    "emc_esd": (
        "EMC, ESD and surge",
        "Sourced best-practice rules for EMC/ESD/surge: loop-area and return-path control, edge-rate and clock handling, I/O filtering "
        "(ferrites, common-mode chokes), shield and chassis ground, TVS selection and placement, IEC 61000-4-2/-4/-5 immunity, "
        "motor/relay noise suppression, pre-compliance checks. Use whenever a board has external connectors, cables, motors or "
        "radios. EMC、ESD、浪涌、TVS、滤波、屏蔽、预兼容测试。",
        ["ee-general-pcb", "ee-hv-safety", "ee-power", "ee-high-speed"],
    ),
    "hv_safety": (
        "High voltage, isolation and safety spacing",
        "Sourced best-practice rules for high-voltage and isolation: creepage and clearance per IEC 60664-1/62368-1/IPC-2221, basic vs "
        "reinforced insulation, isolation-barrier layout, slots and cutouts, optocoupler/isolator/transformer/Y-capacitor placement, "
        "mains-side spacing and fusing, hipot testing. Use for anything above SELV or with galvanic isolation. "
        "高压、隔离、爬电距离、电气间隙、安规、光耦、Y 电容。",
        ["ee-emc-esd", "ee-power", "ee-dfm"],
    ),
    "thermal": (
        "Thermal design",
        "Sourced best-practice rules for PCB thermal design: theta-JA/JC/psi-JT and junction-temperature budgets, copper spreading for "
        "SOT-223/DPAK parts, thermal vias and exposed-pad land patterns, hot-part placement, trace temperature rise (IPC-2152), "
        "MOSFET and LDO dissipation, thermal verification. Use when a part dissipates more than a few hundred mW or temperature is "
        "a risk. 热设计、结温、散热铜皮、热过孔、温升。",
        ["ee-power", "ee-dfm", "ee-pcb-verify"],
    ),
    "dfm": (
        "Manufacturability, assembly and test (JLCPCB-oriented)",
        "Sourced best-practice rules for DFM/DFA/DFT: fab limits (trace/space, drill, annular ring, mask, silkscreen), JLCPCB "
        "capabilities and quirks, panelisation, fiducials and tooling holes, pick-and-place spacing, BOM/CPL conventions and rotation "
        "offsets, stencil and via-in-pad, test points, Gerber hygiene. Use before ordering PCBs or SMT assembly. "
        "可制造性、嘉立创 JLC、MARK 点、工艺边、贴片、BOM/CPL、测试点、出图检查。",
        ["ee-general-pcb", "ee-thermal", "ee-design-review", "ee-pcb-verify"],
    ),
}

STAGE_HINT = {
    "architecture": "需求、器件选型、降额、电源预算",
    "library": "符号 / 封装 / 3D 库质量",
    "schematic": "原理图设计与绘制",
    "netlist": "网表、网络类、约束、原理图↔PCB 一致性",
    "stackup": "叠层、阻抗、板级设计规则",
    "floorplan": "分区、功能块、接口位置",
    "placement": "器件布局",
    "routing": "布线、过孔、回流路径",
    "plane_pour": "平面、铺铜、缝合过孔",
    "manufacturing": "出图、板厂 / 贴片工艺、测试点",
    "verification": "签核：ERC / DRC / 仿真 / 实测",
}


def best_verify(r):
    v = min(r["verify"], key=lambda x: B.AUTO_ORDER[x["automatable"]])
    return f"{v['method']}({v['automatable']})"


def oneline(text, n):
    t = " ".join(str(text).split())
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


def rules_index(rules, key):
    name = next(n for d, n, _ in B.DOMAINS if d == key)
    rs = [r for r in rules if r["domain"] == key]
    o = [f"# {name} — 规则索引", "", f"{len(rs)} 条。⚠ = 来源之间有分歧。全文见 `rules.md`，用 `grep -n \"<规则ID>\" rules.md` 定位。", ""]
    for sk, sn in B.STAGES:
        srs = B.sort_rules([r for r in rs if r["stage"] == sk])
        if not srs:
            continue
        o += [f"## {sn}（{sk}）", "", "| ID | 标题 | 级别 | 可信度 | 最强验证 |", "|---|---|---|---|---|"]
        for r in srs:
            flag = " ⚠" if r.get("conflicts") else ""
            o.append(f"| {r['id']} | {r['title'].replace('|', '/')}{flag} | {r['severity']} | {r['confidence']} | {best_verify(r)} |")
        o.append("")
    return "\n".join(o)


def skill_md(rules, key):
    name_en, desc, related = META[key]
    zh, kind = next((n, k) for d, n, k in B.DOMAINS if d == key)
    skill = B.SKILL[key]
    rs = [r for r in rules if r["domain"] == key]
    sev = Counter(r["severity"] for r in rs)
    stages = Counter(r["stage"] for r in rs)
    must = [r for r in B.sort_rules(rs) if r["severity"] == "must"]
    full = sum(1 for r in rs if any(v["automatable"] == "full" for v in r["verify"]))
    conf = sum(1 for r in rs if r.get("conflicts"))
    o = [
        "---", f"name: {skill}", f"description: {json.dumps(desc, ensure_ascii=False)}", "---", "",
        f"# {zh}（{name_en}）",
        "",
        f"规则库里本领域共 **{len(rs)}** 条（must {sev['must']} · should {sev['should']} · consider {sev['consider']}）。"
        f"每条规则带量化参数、验证方式、来源和可信度；其中 {full} 条至少有一种验证方式可完全自动化，{conf} 条的来源之间有分歧（已写明）。",
        "",
        "## 怎么用",
        "",
        "1. **定位环节**：先看下面「环节分布」，挑你正在做的环节（设计前期看 architecture / schematic，布局看 floorplan / placement，出板前看 manufacturing / verification）。",
        f"2. **查索引**：`references/rules-index.md` 一行一条（ID · 标题 · 级别 · 可信度 · 最强验证）。按环节标题或关键词 `grep`，不要整份读。",
        "3. **读详情**：`grep -n \"<规则ID>\" references/rules.md` 找到位置，只读那一块（规则、依据、参数、验证、来源、来源分歧）。",
        "4. **应用并报告**：结论里写规则 ID、级别、可信度和你看到的证据（器件位号、网络名、实测数值）。有「来源分歧」的规则要把各方观点讲出来，别只报其中一个。",
        "5. **数值要回原文**：规则里的数字来自调研者读到的来源，审计里带数值的高可信度规则仍有约 5–10% 有瑕疵；`medium` / `low` 的数值只当参考。要把数值写成硬性门禁或 DRC 规则前，打开规则里的来源核对一次。",
        "6. **能自动验证的交给 `ee-pcb-verify`**：规则 `verify` 里 `automatable: full` 的检查（DRC 自定义规则、pcbnew 几何、网表对比、SPICE）不要靠肉眼估，用它跑；`bench` / `review` 方式的写进待办清单。",
        "7. 不适用就写 N/A 并说明原因，不要为了凑条数硬套规则。",
        "",
        "## 环节分布",
        "",
        "| 环节 | 条数 | 关注什么 |", "|---|---|---|",
    ]
    for sk, sn in B.STAGES:
        if stages[sk]:
            o.append(f"| {sn}（{sk}） | {stages[sk]} | {STAGE_HINT[sk]} |")
    o += ["", f"## 必须遵守的规则（must，{len(must)} 条）", "",
          "违反会导致功能失效、认证不过或板厂拒收。完整依据与验证见 `references/rules.md`。", "",
          "| ID | 环节 | 标题 | 规则 |", "|---|---|---|---|"]
    for r in must:
        o.append(f"| {r['id']} | {B.STG_NAME[r['stage']]} | {r['title'].replace('|', '/')} | {oneline(r['rule'], 110).replace('|', '/')} |")
    if not must:
        o.append("| — | — | 本领域没有 must 级规则 | — |")
    o += ["", "## 相关 skill", ""]
    for rel in related:
        o.append(f"- `{rel}`")
    o += ["", "## 局限", "",
          "* 规则文字是中文，术语、器件名、标准号保留英文；来源链接在规则里，本机打不开的链接清单见仓库 `docs/URL_CHECK.md`。",
          "* 规则是调研汇总，不是标准本身；与你的器件数据手册冲突时，以数据手册和板厂当前的公开页面为准。",
          "* `tags: [cat-feeder]` 表示规则适用于开源示例板 fxp/cat-feeder，对你的板不一定相关。", ""]
    return "\n".join(o)


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def coverage_matrix(rules):
    cd = Counter(r["domain"] for r in rules)
    mat = Counter((r["domain"], r["stage"]) for r in rules)
    o = ["# 领域 × 环节 覆盖矩阵", "", "每格是该领域在该环节的规则条数；空格 = 没有收录（不等于不需要）。", "",
         "| 领域（skill） | " + " | ".join(sn for _, sn in B.STAGES) + " | 合计 |", "|---|" + "---|" * (len(B.STAGES) + 1)]
    for dk, dn, _ in B.DOMAINS:
        o.append(f"| {dn}（`{B.SKILL[dk]}`） | " + " | ".join(str(mat[(dk, sk)] or "") for sk, _ in B.STAGES) + f" | **{cd[dk]}** |")
    return "\n".join(o) + "\n"


def main():
    rules, _ = B.load()
    if not rules:
        print("no rules found")
        return 1
    for key in META:
        skill = B.SKILL[key]
        write(SKILLS / skill / "SKILL.md", skill_md(rules, key))
        write(SKILLS / skill / "references" / "rules-index.md", rules_index(rules, key))
        write(SKILLS / skill / "references" / "rules.md", B.domain_reference(rules, key))
    # copies the workflow skills carry so each skill directory is self-contained
    copies = {
        SKILLS / "ee-pcb-verify" / "references" / "toolchain.md": REPO / "docs" / "VERIFICATION_TOOLCHAIN.md",
        SKILLS / "ee-pcb-verify" / "references" / "verifiers.yaml": REPO / "catalog" / "verifiers.yaml",
        SKILLS / "ee-catalog-maintain" / "references" / "schema.md": REPO / "docs" / "SCHEMA.md",
        SKILLS / "ee-catalog-maintain" / "references" / "research-brief.md": REPO / "docs" / "RESEARCH_BRIEF.md",
    }
    for dst, src in copies.items():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    write(SKILLS / "ee-design-review" / "references" / "coverage-matrix.md", coverage_matrix(rules))
    print(f"built {len(META)} domain skills for {len(rules)} rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
