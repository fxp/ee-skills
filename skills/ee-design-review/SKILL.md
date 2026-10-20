---
name: ee-design-review
description: Review a schematic, PCB layout, netlist or design spec against a sourced catalog of 500+ circuit-design best-practice rules organised by design stage (architecture, schematic, netlist, placement, routing, planes, manufacturing, sign-off) and by vertical (RF, power, low-power, audio, precision analog, high-speed, EMC/ESD, HV safety, thermal, DFM). Use for "review my schematic/PCB", design checklists, "what are the best practices for X", pre-order sign-off. Produces findings with rule IDs, severity, evidence and source confidence. 原理图/PCB 评审、设计检查清单、最佳实践、投板前签核。
---

# EE design review against the rule catalog

This skill is the **router**: it decides which domain skills apply, walks the design stages in order, collects evidence and reports findings. The rules themselves live in the domain skills (`ee-general-pcb`, `ee-power`, `ee-rf`, …); automated checks live in `ee-pcb-verify`.

## 0. What to ask for

Ask for (or locate) what the review is based on; never review from memory of what the board "probably" has:

* schematic (`.kicad_sch` / PDF), PCB (`.kicad_pcb` / Gerber / screenshots), netlist, BOM, the requirements or spec, the stackup and fab/assembly target (e.g. JLCPCB 2-layer + SMT);
* what is already verified (ERC/DRC clean? simulations run?). If the board is KiCad, offer to run `ee-pcb-verify` for the mechanical checks first.

Write down the assumptions you had to make (supply voltages, currents, environment). They go into the report.

## 1. Scope: pick the domains

Always include `ee-general-pcb` and `ee-dfm`. Add the rest from what is on the board:

| If the board has … | add |
|---|---|
| any switching regulator, LDO, motor/relay driver, battery charger, current > ~0.5 A | `ee-power` (+ `ee-thermal` if a part dissipates > ~0.5 W) |
| battery operation, deep sleep, always-on rails | `ee-low-power` |
| antenna, Wi-Fi/BLE/LoRa/GNSS module or discrete RF | `ee-rf` |
| codec, microphone, speaker/headphone amp | `ee-audio` |
| ADC, sensor/bridge front-end, shunt current sense, reference | `ee-analog` |
| USB, Ethernet, DDR, LVDS, MIPI, PCIe, fast clocks | `ee-high-speed` |
| any external connector or cable, motor, or radio (that is: almost always) | `ee-emc-esd` |
| mains, > 50 V AC / 120 V DC, galvanic isolation | `ee-hv-safety` |

`references/coverage-matrix.md` shows how many rules exist per domain and stage; empty cells mean the catalog has nothing there, not that nothing is needed — say so in the report instead of implying a pass.

## 2. Walk the stages in order

Earlier stages are cheaper to fix. For each stage, open the relevant domain skills' `references/rules-index.md` and read the `must` rules first, then `should`.

| Stage | Look at |
|---|---|
| architecture | requirements, part choice, derating, power budget, sequencing |
| library | symbols/footprints match the datasheet; pad↔pin consistency; courtyards |
| schematic | decoupling, pull-ups, strapping/boot pins, reset, protection, unused pins, crystals |
| netlist | net classes, naming, constraints, schematic↔PCB parity |
| stackup | layers, impedance, design rules |
| floorplan | partitioning, connector edge, keep-outs, antenna end |
| placement | decap distance, hot loops, TVS at connector, crystal, thermal neighbours |
| routing | return paths, widths, vias, crosstalk, Kelvin sense, diff pairs |
| plane_pour | ground continuity, stitching, islands, splits |
| manufacturing | fab limits, fiducials, panel, BOM/CPL, test points |
| verification | what was actually run (ERC/DRC/sim/bench) and what was not |

## 3. Judge each rule with evidence

For every rule you apply, record **pass / fail / unknown / N/A** and the evidence: reference designators, net names, measured numbers (distance in mm, width, capacitance, computed junction temperature), or a screenshot region.

* Do the arithmetic the rule asks for (power dissipation, trace width for the current, dropout, budgets). Do not eyeball a number that a script can measure; use `ee-pcb-verify`.
* **No evidence means "unknown", not "pass".**
* A rule that does not apply is **N/A with a reason**.
* Rules with `confidence: medium|low`, or with a `conflicts` entry, are guidance: present the disagreement (both sides, then the rule's recommended trade-off) instead of reporting a hard fail.
* Numbers in the catalog come from sources the researchers read; audits found roughly 5–10% of numeric high-confidence rules had some defect. Before a number becomes a gate that blocks an order, open the rule's source and check it.

## 4. Report

Use `references/review-template.md`. Order: must-level fails first, then should, then unknowns, then N/A. Group by stage. Each finding: rule ID · severity · status · evidence · suggested fix · how to verify the fix (the rule's `verify` entry). End with the assumptions, the unknowns that need data from the user, and what was verified by tools versus by inspection.

## 5. Do not

* Do not cite rules that are not in the catalog as if they were; label anything else as "general practice".
* Do not copy long passages from the sources; the rules already paraphrase them and link them.
* Do not recommend ordering a board with open must-level fails without saying so plainly.
* Do not change the user's design files; propose changes.
