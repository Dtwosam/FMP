# Phase 8A — EXP-062 Historical Execution Authorization

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY ONE-SHOT RUNTIME AUTHORIZATION / DISPATCH STILL LOCKED  
**Decision:** DEC-312  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-311

## Purpose

DEC-312 is the first EXP-062 transition that allows the already-installed historical
workflow runtime to pass its execution gate, but only for the single future
historical-result attempt already reserved by DEC-307.

DEC-312 does **not** dispatch the workflow and adds no executor.

## Frozen prerequisite

DEC-312 binds the concrete DEC-311 historical-plan proof freeze:

- DEC-311 source blob:
  `e3274118b37066efe2869d554e78e6b68e64b32a`;
- DEC-309 plan-proof run:
  `36403342301`;
- DEC-309 plan-proof head:
  `95c193343a905acd40daf0eea5d27d55fd2537e1`;
- reviewed plan proves zero historical-result attempts and an unconsumed slot.

The older DEC-299 workflow-source execution flag remains false. DEC-312 supersedes
that runtime gate through the public EXP-062 CLI without rewriting DEC-299 or the
active workflow YAML.

## Exact source stack

DEC-312 pins:

- active EXP-062 discovery workflow blob:
  `1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`;
- EXP-062 run-contract blob:
  `d304c8fafcff64f967f6777b1c494819f69d4a03`;
- frozen DEC-299 workflow-source blob:
  `e20ded13de24f99e8ea6cfdc6cb0d1309d984f24`;
- repaired adapter blob:
  `491ba8c92cb6e6e4c715bfb1ecb934b6949e1596`;
- pattern protocol blob:
  `63b3f0121d6a50eb9e8e62ab666d70eb91791621`;
- pattern miner blob:
  `495a67699eb5014e52129f0238a2737049fe38e6`;
- predecessor market-learning adapter blob:
  `978a33554fad7e9d78b002778c4896be0af3333a`;
- range-limited loader blob:
  `df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`;
- runtime requirements blob:
  `1ff32214dee10d877a067e750cd69ffad96d5fe5`;
- activated EXP-062 CLI blob:
  `773784d0770d54b1d3e41fba2057b9314a090034`.

## One-shot runtime identity

The frozen gate proof is workflow run #1 / attempt 1. DEC-312 therefore authorizes
historical discovery execution only when all of these runtime conditions hold:

- `GITHUB_ACTIONS=true`;
- repository: `Dtwosam/FMP`;
- workflow: `phase8a-exp062-discovery`;
- event: `workflow_dispatch`;
- ref: `refs/heads/main`;
- workflow run number: `2`;
- workflow run attempt: `1`;
- runtime `GITHUB_SHA` exactly equals the CLI `--code-commit`;
- runtime run id is positive and is not proof run `36358289723`;
- runtime code commit is not the frozen proof head.

Run #1 is the completed gate proof. Run #3 or later is rejected. Any rerun of run #2
has attempt >1 and is rejected.

## Authorization split

DEC-312 records:

- historical execution source authorized: **true**;
- historical-result slot source authorized: **true**;
- historical discovery execution authorized inside the exact runtime identity:
  **true**;
- discovery-result production authorized inside the exact runtime identity:
  **true**;
- historical-result dispatch authorized: **false**;
- rerun / retry / replacement: **false**.

No repository-hosted dispatcher is added.

## Data boundary

Historical execution remains restricted to:

- 2015-01-01 inclusive;
- 2023-01-01 exclusive.

Reserved robustness data remains closed:

- 2023-01-01 inclusive;
- 2026-08-21 exclusive.

The existing range-limited loader continues to enforce the historical boundary.

## CLI transition

`scripts/phase8a_exp062.py` now imports the DEC-312 execution gate. The gate remains
before any historical feature/outcome read in a cell job and before any cell-result
read in the aggregate job. Preflight evidence records the DEC-312 execution
authorization payload.

DEC-307’s old exact-source builder intentionally detects the activated CLI as a source
supersession; its run-inventory classification remains valid.

## Downstream locks

DEC-312 keeps false:

- workflow/historical-result dispatch;
- rerun / retry / replacement;
- reserved robustness access;
- candidate compilation / promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

A historical result produced under DEC-312 is still research evidence, not a trading
instruction.

## Next gate

After DEC-312 merges green, the next safe gate is a separate **read-only historical
execution operator**. It may expose the one future dispatch command only while the
slot is still empty and current main matches exactly. It must have no execute mode.

A one-shot dispatcher may be considered only after that execution plan is separately
proved and reviewed.
