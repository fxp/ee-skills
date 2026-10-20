# Design review report template

```markdown
# Design review — <board name> <revision>   (<date>)

**Reviewed:** <files / screenshots / spec> · **Fab/assembly target:** <e.g. JLCPCB 2-layer + SMT> · **Domains applied:** <ee-... list>
**Verified by tools:** <ERC/DRC/parity/ee-pcb-verify run/simulations — or "none">

## Summary
<3–5 lines: ready to order? number of must-level fails / unknowns, the one or two things that matter most>

## Findings (must first)
| # | Rule | Sev | Stage | Status | Evidence | Fix | Verify with |
|---|---|---|---|---|---|---|---|
| 1 | PWR-ARC-002 | must | architecture | fail | AMS1117 SOT-223, 5 V→3.3 V at 0.35 A: P=0.6 W, θJA 150 °C/W → Tj≈129 °C at 40 °C ambient | larger copper / lower-θ part / buck | bom_check + thermal estimate |
| … |

## Disagreeing sources (conflicts)
<for each reported rule that carries `conflicts`: the two positions, the trade-off the rule recommends, and what you chose for this board and why>

## Unknown (no evidence available)
<rule ID — what data is needed to decide>

## N/A
<rule ID — reason>

## Assumptions
<supply voltages, currents, ambient, loads, anything you inferred>

## Suggested next checks
<automatable rules still to run with ee-pcb-verify; bench measurements; simulations>
```

Severity words: `must` = failure, non-compliance or fab rejection if violated; `should` = strong recommendation, deviate only with a reason; `consider` = depends on context.
