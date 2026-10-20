---
name: ee-pcb-verify
description: Verify a KiCad design headlessly and automatically - ERC, DRC with custom .kicad_dru rules, schematic-vs-PCB netlist diff, BOM export, pcbnew geometry checks, ngspice simulation through KiCad's bundled libngspice - plus a rule-checking harness that maps catalog rule IDs to pass/fail/evidence JSON. Use for "run DRC/ERC from the CLI", "check my board against best practices", "write a custom DRC rule", "headless KiCad", "measure decap/shunt/antenna distances", "simulate with ngspice", KiCad 自动化校验、自定义 DRC 规则、几何检查、仿真。
---

# Automated EE verification (KiCad 10)

Turns the catalog's `verify` entries into runnable checks. Tested on macOS arm64 with KiCad 10.0.6; Linux/Windows need `KCLI`, `KPY` (and `NGSPICE_LIB`) set by hand and are untested. Everything below was actually run; unverified items say so in `references/toolchain.md`.

## Ground rules

1. **Work on copies.** Never run write-capable commands (`--refill-zones --save-board`, `pcbnew.SaveBoard`) on a board KiCad may have open. Copy only `.kicad_pcb`, `.kicad_pro`, `.kicad_sch`, `*-lib-table`; never `~*.lck` or `_autosave-*`. The harness does this for you.
2. **Private KiCad config:** `export KICAD_CONFIG_HOME=<dir> KICAD_DOCUMENTS_HOME=<dir>` so the CLI does not touch your KiCad settings or stall scanning `~/Documents` (macOS TCC).
3. Do not use `/tmp` for scratch that has to outlive a step; use a work directory inside the project (`work/` is git-ignored here).
4. A tool error is **not** a verdict. Report `error` and fix the check; never turn it into pass or fail.

## Quick commands (all verified)

```bash
KCLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3   # Python 3.9 with pcbnew
$KCLI sch erc --format json --severity-all --units mm -o erc.json board.kicad_sch
$KCLI pcb drc --format json --severity-all --all-track-errors --units mm -o drc.json board.kicad_pcb     # reads board.kicad_dru + board.kicad_pro next to it
$KCLI pcb drc --schematic-parity --format json --severity-all -o parity.json board.kicad_pcb              # noisy baseline: compare with a clean run
$KCLI sch export netlist --format kicadxml -o net.xml board.kicad_sch
$KCLI sch export bom --fields 'Reference,Value,Footprint,${QUANTITY}' --labels 'Refs,Value,Footprint,Qty' -o bom.csv board.kicad_sch
$KPY -I scripts/lib/pcb_nets.py board.kicad_pcb nets.json && python3 scripts/lib/netlist_diff.py net.xml nets.json     # exit 1 on any pin-set difference
```

## The rule-checking harness

```bash
python3 scripts/checkers/run.py --board board.kicad_pcb --design design/my_board.yaml            # pro defaults to board.kicad_pro; results -> ./ee-results/<date>/
python3 scripts/checkers/run.py --board B --design D --rules DFM-PLC-003,GEN-STK-005 --checkers geometry,drc_rule
python3 scripts/checkers/coverage.py                                                              # which automatable catalog rules are NOT wired, and why
```

(Paths are relative to this skill's directory. It finds the catalog by walking up to `catalog/`, or `$EE_CATALOG_DIR`.)

* Two checkers. **`drc_rule`** writes one `.kicad_dru` rule file per catalog rule (thresholds read from the catalog `parameters`, never hard-coded), runs `kicad-cli pcb drc` once per rule, plus a **canary** rule so a syntax error that makes KiCad silently drop every custom rule is detected. **`geometry`** exports the board once to `geometry.json` (inside KiCad's Python) and evaluates pure-Python checks: pad-pair distances, keep-outs, copper-path length and width, loop proxies.
* `design/template.yaml` holds the board facts a `.kicad_pcb` cannot say (which nets are power/fast, which IC pins need which decoupling cap, the antenna keep-out rectangle, the shunt pads). Copy and edit it; a rule whose role is missing reports `error`, not pass.
* Result per rule: `{rule_id, checker, severity, status: pass|fail|error|skipped, measured, threshold (+source), evidence, tool, inputs sha256}`. `not evaluated` notes list what the check could not see (silk, component heights, mask openings); treat those as unknown.
* Wired rules are a first slice (about 40). `bindings/*.yaml` explain how to add one; `scripts/checkers/README.md` has the recipe and the seeded-defect test method (break a copy of the board with pcbnew, require pass→fail).

## Custom DRC rules: the pitfalls that cost hours

* **A syntax error in `.kicad_dru` is silently ignored** (exit code 0). Always include a canary rule that must fire.
* Same-type constraints with overlapping conditions mask each other (last wins): one rule per DRC run, or mutually exclusive conditions.
* The DRC JSON has no numeric field for the measured value: parse `actual` out of the description string; to read the nearest/worst value, run again with a loosened threshold ("probe").
* Default-ignored checks (`missing_courtyard` etc.) need enabling in `.kicad_pro` `rule_severities`; netclasses and `hasNetclass()` need the `.kicad_pro` next to the board.
* `A.Value` never matched in 10.0.6; use `getField('Value')`. `track_angle` takes a bare number.
* DRC coordinates are KiCad board coordinates; ERC JSON coordinates are 1/100 of schematic mm.
* `kicad-cli` cannot run simulations; `pcb_calculator` and the IPC API need the GUI.

## Simulation (SPICE)

KiCad ships `libngspice`; `scripts/lib/ngspice_ctypes.py` drives it from any Python through ctypes (transient, AC, noise, `.meas`, temperature sweeps), checked against analytic values. `scripts/lib/example_rc.py` is the smoke test. `ngSpice_Init` is process-global: use separate processes for parallel runs. There are no IC models bundled; AMS1117/INA199-class parts need vendor models. `scripts/lib/tline_formulas.py` (IPC-2221 trace width, microstrip Z0) and `scripts/lib/irdrop.py` (+ `dump_copper.py`, track-only IR drop) are prototypes with the accuracy caveats in `references/toolchain.md`.

## Mapping catalog `verify.method` → tool

`erc`, `drc`, `netlist_diff`, `bom_check`, `geometry_script`, `spice`, `tline_calc` have working paths above; `em_sim`, `si_sim`, `pi_sim`, `thermal_sim` need tools that are not installed on the reference machine (openEMS, Elmer, …), and `bench`, `emc_precompliance`, `review` are manual. `references/verifiers.yaml` lists every tool with status, invocation, what it can check and its limits; `references/toolchain.md` has the measured commands and the recommended harness architecture.

## Reporting

Report fail/error with the evidence field (reference designators, measured vs threshold). Say which rules were not wired or not evaluated. Do not claim a board is "verified" beyond the rules actually run.
