---
name: ee-catalog-maintain
description: Add, fix, audit or extend the sourced EE best-practice rule catalog (catalog/*.yaml) - write a rule with quantified parameters and verify methods, validate it, regenerate the domain skills and docs, check source URLs, and audit numbers against their sources. Use when the user wants to add a best practice, correct a rule, research a new domain, or check that catalog numbers are real. 维护最佳实践规则库：新增规则、核对来源、校验与重新生成。
---

# Maintaining the rule catalog

The catalog is the single source of truth: `catalog/*.yaml` (rules) and `catalog/verifiers.yaml` (tools). Everything under `skills/ee-<domain>/`, `docs/INDEX.md`, `docs/by-stage/`, `docs/by-board/` and `docs/VERIFICATION_BACKLOG.md` is generated: **never edit those by hand**.

Read `references/schema.md` for the fields and enums, `references/research-brief.md` for the research method and quality bar.

## Add or change a rule

1. Find the right file (`catalog/<domain>.yaml`; `general` is split into `general_process.yaml` for architecture/library/schematic/netlist/verification and `general_layout.yaml` for stackup/floorplan/placement/routing/plane_pour).
2. ID = `<DOM>-<STG>-<NNN>`: next free number for that domain and stage (`grep -c "id: PWR-PLC" catalog/power.yaml`). IDs are never reused or renumbered; deprecate by editing the rule.
3. Write it in Chinese with English terms/part names/standard numbers. One rule = one checkable statement. Required: title, rule, rationale, `verify` (≥ 1, concrete enough that someone else can implement it: what is measured, from where to where, pass criterion), `sources` (≥ 1), `confidence`.
4. Numbers go in `parameters` **only if you read them in the cited source**; otherwise put the figure in a `note`, and use `confidence: medium|low`.
5. When sources disagree, write `conflicts` (both positions + your trade-off). Do not silently pick one.
6. Validate and rebuild:

```bash
python3 tools/validate.py                 # schema, ID/domain/stage consistency, duplicate IDs
python3 tools/build_docs.py && python3 tools/build_skills.py
python3 -m pytest -q                      # includes "generated files are current"
```

## Source rules

* Prefer standards and vendor application notes/datasheets/layout guides; then textbooks; then EDA/fab vendor docs; then blogs/forums (never as the only source for a `must`).
* **Never invent a URL, section number or value.** Textbooks and paid standards without a link need a `ref` (title, edition, section).
* Paraphrase; do not paste long passages.
* PDFs often come back as binary from fetch tools: extract text (`pdftotext -layout`) and grep the number; if it is an image-only scan, read the rendered page.

## Audit numbers (do this before trusting or gating on a figure)

Sample rules with `confidence: high` and a numeric `parameters` entry; for each, open the cited source and confirm: the number, unit and condition; the section; that the source supports the rule sentence. Verdicts: CONFIRMED / PARTIAL / NOT_FOUND / CONTRADICTED / UNVERIFIED. Fix clear errors in place (correct the value only if the source gives it; otherwise drop the parameter and lower `confidence`). The 2026-10 audit of all 531 rules found about 83% right as written and the rest defective in some way (usually a mis-cited section or table, a missing condition, a neighbouring number from the same source, or a paraphrase that drifted; a few wrong values); none fabricated. Results and open items are in `docs/AUDIT.md`: add yours there.

## URLs

```bash
python3 tools/validate.py --check-urls          # probes every source URL
python3 tools/retry_urls.py <saved-output>      # re-probe failures with curl and a browser UA
```

403/429/timeouts are often bot blocking, not dead links. A 404 is real: find the current URL or a mirror, confirm it is the same document, replace it everywhere, and regenerate `docs/URL_CHECK.md` by hand-editing the summary.

## Adding a whole domain or verifier

New domain: add the key to `DOMAINS`/`STAGES` mapping in `tools/validate.py` and `tools/build_docs.py`, a `META` entry in `tools/build_skills.py`, then write the catalog file. New verifier: add to `catalog/verifiers.yaml` (fields in the schema) and mark `VERIFIED <date>` only for things you actually ran.
