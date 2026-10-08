# DEC-623 — Inert three-job pre-evidence identity gate placement audit

**Status: SOURCE-ONLY, UNINSTALLED, NO DISPATCH OR TRADING AUTHORIZATION.** Depends on DEC-622 merged main `4060419eb2d3172da8d403b5ae7a0ac725d2ebb7`. Issue #779 remains open.

## Existing protected workflow topology

The pinned installed annual workflow `.github/workflows/phase8a-annual-pattern-catalogue.yml` Git blob `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1` still requires `refs/heads/main` in all three jobs and has no tag-ref identity gate.

**Concrete ordering gap:** `annual_preflight` runs **Fetch exact accepted EXP-044 source snapshots** (GitHub API run/artifact *metadata* queries) **before** its **Require separately authorized annual catalogue execution** step. `annual_cell` and `annual_freeze` run **Recheck separately authorized annual catalogue execution** before their respective artifact download steps. This is a placement concern for the *future* proposed exact tag/commit/workflow-ref identity check; it is not a claim that protected historical artifact bytes were downloaded before the current gate.

A correct future live amendment needs an authenticated exact `GITHUB_REF`, `GITHUB_REF_TYPE`, `GITHUB_SHA`, `GITHUB_WORKFLOW_REF`, repository, workflow, year, run 385/attempt 1 and 2022 predecessor binding **before any GitHub evidence API call or artifact download in any of the three jobs**. A predicate in an unrelated Python module will not enforce that ordering by itself.

## What this offline source-only audit does

The auditor pins the unmodified workflow source by Git blob and verifies the original job guard order. It extracts the exact three job step-name lists, records the current preflight ordering exception, and inserts a **fabricated step label** immediately after runtime installation in in-memory step-name lists. The fabricated label contains no executable command, produces no workflow YAML, and cannot be installed.

Synthetic tests check that this label precedes each known first evidence-access step. For each job, missing, late, and duplicated gates must all fail: **9 adverse placement scenarios**. They also reject malformed step lists, invented jobs, field-type confusion, and re-fingerprinted authorization flags.

An assess-only CLI may write a canonical JSON report outside the checkout:

```sh
PYTHONPATH=src python scripts/phase8a_annual_pattern_catalogue_2023_preaccess_identity_gate_topology_audit.py assess --out /tmp/dec623-preaccess-topology.json
```

The validator reconstructs all report bytes from the pinned installed workflow. Positive *synthetic* step ordering says nothing about real tag immutability, authenticated GitHub context, source approval, sufficient permissions, repository rulesets, actual runtime wiring, artifact provenance, or dispatch safety.

## Live gates still blocked

No current annual workflow, 2023 runtime authorization, tag, repository branch protection, or ruleset is edited. Nothing calls GitHub or reads historical artifacts from this audit. The report forces installed/amended/authenticated/authorized/executed/retry/broker/trading claims to false, with `dispatch_blocked=true`.

Before any real 2023 run 385: independently obtain continuous administrator-enforced no-bypass non-retargetable ref evidence, separately approve and review the actual **three-job workflow amendment plus 2023 runtime binding**, verify pre-access wiring and unchanged annual run inventory, and obtain a distinct one-shot action approval. An ambiguous request remains terminal: no attempt 2, replacement dispatch or run 386+ by default. No future-year research, Phase 8B, strategy promotion, broker operation, demo/live order or real-money trading is authorized.
