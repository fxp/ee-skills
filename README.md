# ee-skills

**Electronics-design skills for Claude Code, backed by a sourced rule catalog and a KiCad verification harness.**
**面向 Claude Code 的电子设计 skills：531 条有出处的最佳实践规则 + KiCad 自动验证。**

[![ci](https://github.com/fxp/ee-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/fxp/ee-skills/actions/workflows/ci.yml)

Best practices for every stage of circuit design (architecture, library, schematic, netlist, stackup, floorplan, placement, routing, planes, manufacturing, sign-off) and for each vertical (RF, power, low-power, audio, precision analog, high-speed, EMC/ESD, HV safety, thermal, DFM), collected from standards, vendor application notes, textbooks and fab documentation. Each rule is **atomic, quantified where its source quantifies it, and checkable**: it says what to measure, how, and which tool can do it, so the same catalog drives design reviews today and automated ERC/DRC/geometry/SPICE checks.

> Rule text is in **Chinese** (part names, standards and technical terms stay in English); skill descriptions are bilingual so they trigger from either language. Sources are linked from every rule.

## Skills

| Skill | Use it when |
|---|---|
| [`ee-design-review`](skills/ee-design-review/SKILL.md) | reviewing a schematic / PCB / spec: picks the domains, walks the stages, reports findings with rule IDs and evidence |
| [`ee-pcb-verify`](skills/ee-pcb-verify/SKILL.md) | running ERC, DRC (custom `.kicad_dru` rules), netlist diff, geometry checks and ngspice headlessly; maps catalog rules to pass/fail JSON |
| [`ee-catalog-maintain`](skills/ee-catalog-maintain/SKILL.md) | adding / auditing rules, checking sources, regenerating the skills |
| [`ee-general-pcb`](skills/ee-general-pcb/SKILL.md) | any MCU board: libraries, schematic, netlist, stackup, placement, routing, planes (103 rules) |
| [`ee-power`](skills/ee-power/SKILL.md) | buck/boost/LDO, motor drivers, high current, input protection (54) |
| [`ee-low-power`](skills/ee-low-power/SKILL.md) | battery / deep-sleep budgets, leakage, load switches (40) |
| [`ee-rf`](skills/ee-rf/SKILL.md) | antennas, matching, controlled-impedance RF, keep-outs (45) |
| [`ee-audio`](skills/ee-audio/SKILL.md) | codecs, Class-D, AC coupling, grounding (43) |
| [`ee-analog`](skills/ee-analog/SKILL.md) | ADC/sensor front-ends, shunt current sensing, guard rings (46) |
| [`ee-high-speed`](skills/ee-high-speed/SKILL.md) | USB, Ethernet, DDR, LVDS, differential pairs, SI (52) |
| [`ee-emc-esd`](skills/ee-emc-esd/SKILL.md) | EMC, ESD/TVS, surge, filtering (46) |
| [`ee-hv-safety`](skills/ee-hv-safety/SKILL.md) | creepage/clearance, isolation barriers (23) |
| [`ee-thermal`](skills/ee-thermal/SKILL.md) | junction temperature, copper spreading, thermal vias (28) |
| [`ee-dfm`](skills/ee-dfm/SKILL.md) | fab/assembly limits (JLCPCB-oriented), fiducials, BOM/CPL, test points (51) |

Coverage per domain and stage: [docs/INDEX.md](docs/INDEX.md). Per-stage views: [docs/by-stage/](docs/by-stage/). Which rules can be automated and with what: [docs/VERIFICATION_BACKLOG.md](docs/VERIFICATION_BACKLOG.md).

## Install

As a Claude Code plugin (all 14 skills):

```
/plugin marketplace add fxp/ee-skills
/plugin install ee-skills@ee-skills
```

Or copy individual skills: `git clone https://github.com/fxp/ee-skills && cp -r ee-skills/skills/ee-rf ~/.claude/skills/`. The domain skills and `ee-design-review` are self-contained. `ee-pcb-verify` needs the catalog next to it (installed as a plugin it is found automatically); with a bare copy set `EE_CATALOG_DIR=/path/to/ee-skills/catalog`.

Example prompts: "review this schematic against the best practices", "what are the antenna keep-out rules for a 2.4 GHz module", "check my board for decoupling distance and board-edge clearance", "add a rule about …".

## How far to trust it

* Every rule carries `confidence`: `high` = the researcher read the standard / vendor note itself; `medium` = secondary source or search summary only; `low` = single community source or rule of thumb. 141 rules record **disagreements between sources** (2- vs 4-layer, split vs solid ground, fuse vs TVS order, 20H rule, …) instead of picking a side.
* **Audited, not guaranteed.** A random sample of 36 high-confidence numeric rules: 33 confirmed, 3 with defects (a neighbouring number taken from the same source, a mis-scaled example, a rule sentence that drifted); no number was fabricated. `analog` and `dfm` were then re-audited rule by rule. The other domains were only sampled, so expect **~5–10%** of numeric high-confidence rules to have a similar flaw: **open the source before turning a number into a gate.** See [`ee-catalog-maintain`](skills/ee-catalog-maintain/SKILL.md) for the audit method.
* 39 source links could not be opened from the author's machine (bot blocking, network); see [docs/URL_CHECK.md](docs/URL_CHECK.md). That does not mean they are dead.
* Known gaps (no readable source found, so not included): connector current ratings, MLCC piezo/voltage-coefficient effects, DDR4/LPDDR, the IEC 60664-1 clearance table, CISPR/FCC limits, Li-ion capacity vs temperature.
* JLCPCB numbers come from jlcpcb.com pages; domestic jlc.com pricing and some limits differ, and JLC's own pages contradict each other in places (recorded in `conflicts`).
* The catalog summarises sources; it is **not** a substitute for the standard, the datasheet, or your fab's current rules, and nothing here is legal/safety certification advice.

## Verification

`ee-pcb-verify` ships a first slice of the harness: `drc_rule` (generates a custom DRC rule per catalog rule, with a canary that detects KiCad silently ignoring a broken `.kicad_dru`) and `geometry` (pad-pair distances, keep-outs, copper-path length/width), 42 rules wired so far, with seeded-defect tests that require pass on a good board and fail on a broken copy. Thresholds always come from the catalog, never from code. Tested on **macOS arm64, KiCad 10.0.6**; the seeded-defect tests need a reference board that is not published, so CI runs only the static checks. Details: [docs/VERIFICATION_TOOLCHAIN.md](docs/VERIFICATION_TOOLCHAIN.md) (commands that were actually run, pitfalls, architecture) and [catalog/verifiers.yaml](catalog/verifiers.yaml).

## Repository layout

```
catalog/            rules (*.yaml) and verifiers.yaml — the single source of truth
skills/             3 hand-written workflow skills + 11 generated domain skills (references/ inside each)
tools/              validate.py, build_docs.py, build_skills.py, retry_urls.py
docs/               SCHEMA, research brief, toolchain notes, generated INDEX / by-stage / by-board / backlog
tests/              static tests (CI) + seeded-defect tests (need KiCad + a reference board)
```

Edit `catalog/*.yaml` only, then `python tools/validate.py && python tools/build_docs.py && python tools/build_skills.py`. CI fails if generated files are stale.

## 中文简介

按设计环节（架构选型、库、原理图、网表、叠层、分区、布局、布线、铺铜、制造、签核）和垂直领域（射频、电源、低功耗、音频、精密模拟、高速数字、EMC/ESD、安规、热、可制造性）整理的最佳实践，共 531 条，每条带量化参数、来源、可信度和**可执行的验证方式**，为后续的仿真和 EDA 校验准备。`ee-design-review` 做评审，`ee-pcb-verify` 在 KiCad 上无头跑 ERC / DRC / 几何检查 / ngspice，11 个领域 skill 各带本领域规则的索引和全文。规则数值来自调研时读到的来源，抽样审计仍发现约 5–10% 的瑕疵，把数值写成硬性门禁前请回原文核对。示例板是开源的 [fxp/cat-feeder](https://github.com/fxp/cat-feeder)（ESP32-C3 自动猫粮机）。

## License

MIT (code, tooling and the catalog text). The catalog paraphrases and links third-party sources; their content remains the property of their publishers.
