# DEC-1346 — Non-authorizing reviewer hardening and protected annual gate acceptance ledger

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of #1569 DEC-1345 at `3ec01ad3590673a7422cfaec8811a6415823d0c2`, **944 source-defined tests unchanged**. This is review documentation for FMP Phase 8A under governing annual discovery DEC-469 / DEC-268; it **does not authorize annual history access, research execution, Strategy V1 synthesis, promotion, brokers or trading**.

## Scope, lineage and inspectable coverage

| Exact draft | Changed source-only surface | Inspectable regression requirement |
| --- | --- | --- |
| #1564 DEC-1340 | Unsupported local Landlock ABI probe feasibility note | Query returned ENOSYS in development container; **no kernel policy installed, no protected denial proven**. Support must be independently re-established in the actual future test host |
| #1565 DEC-1341 | `scripts/dec1330_synthetic_annual_gate_proof_nonauthorizing.py`, +5 tests | SHA strings lacking exactly 40 lowercase ASCII hex chars raise an additional malformed-shape diagnostic; **well-formed matching SHA text is still unauthenticated self-report** |
| #1566 DEC-1342 | Same inert reviewer, +4 tests | Any untrusted caller-supplied gate/permission field, including false values, is explicitly flagged; response permissions and DEC gates remain immutable **BLOCKED/False** |
| #1567 DEC-1343 | Same inert reviewer, +4 tests | Missing/unknown annual outcome, caller-reported success and terminal retry/failed/ambiguous outcomes are classified separately, but **never authorize** a run |
| #1568 DEC-1344 | New regression-only test, +4 methods | Synthetic fabricated PUBLIC canaries in alleged tokens, proof signatures, SHA/workflow fields and Unicode metadata do not appear in classifier output; no real credentials used |
| #1569 DEC-1345 | New source-only separation regression, +3 methods | `.github/workflows/*.yml/.yaml`, `src/**/*.py`, and `pyproject.toml` have **no references to the inert synthetic reviewer**; no live installed workflow verification is implied |
| #1570 DEC-1346 | This documentation-only review ledger | No new executable tests, no runtime or access-policy modifications |

All PRs are independent **strict one-commit children** of their predecessor draft. Each exact SHA needs separately completed successful Phase3 and full historical regression suites; a Phase3 pass alone is not green. Historical failed original SHAs remain FAILED, including earlier source-only test expectation defects; forward-only replacements do not erase that classification. Passing source-only tests do **not** satisfy qualified independent review.

## What this work actually establishes

The `assess_synthetic_claims` model is a deliberately **inert diagnostic**. It does not retrieve, read, or authenticate a GitHub ref/SHA, hosted reviewer signature, protected annual storage, raw market-data manifest, protected evidence inventory, or annual workflow. Even purported signed evidence and a matching SHA can be syntactically checked only. Every packet is permanently `SOURCE_ONLY_SYNTHETIC_NONAUTHORITATIVE`, `status=BLOCKED`, with no protected evidence access, no run385 action, no promotion and no trading. The new source-code quarantine regression is a useful early warning if anyone later tries to call this model from a GitHub Actions YAML or the production package; it is **not proof of server-side installed workflow immutability** or total source absence outside scanned paths.

The repo's mandatory `AGENTS.md` states Phase 8A must not be skipped. The governing research method is **annual discovery-first pattern catalogues** under DEC-469 / DEC-268, not a particular representation, strategy, or simulation; research output and execution authorization are separate questions. No annual study, actual catalogue, market-data read, backtest, shadow/demo activity or Strategy V1 synthesis was performed in this batch.

## Independent decisions that a human security administrator still must resolve

| Real gate | Independent evidence owner must supply | Current status |
| --- | --- | --- |
| DEC-650/#820 — protected original OS no-write | Actual protected original filesystem/storage object identity and alias inventory; independently installed policy and enforcement authority; bypass analysis for inherited O_RDWR, MAP_SHARED, alternate procfd/mount/namespace and privilege paths; pre-access and continuous policy lifetime; disposable same-policy destructive denial probes and independent original-byte/identity witness | **BLOCKED: no installed independently authenticated protected-source policy** |
| DEC-651/#821/#779 — exclusive immutable run385 admission | Independently enforceable no-bypass immutable ref/workflow/resolved SHA identity before any job checkout/install/evidence access across all three relevant jobs; external reviewed expected identity not supplied by untrusted runner; fresh independent run385 attempt1 slot inventory; separate signed one-shot action after all proofs, terminal no retry/attempt2 on ambiguity | **BLOCKED: no administrator lock, installed admission or independent one-shot authorization** |
| Qualified independent source and control review | Review each exact new source SHA, required CI suites, actual external policy deployment, requested access scope and runner/protected-data identity before considering any future action | **OUTSTANDING — neither CI nor this ledger signs that proof** |

A local disposable PUBLIC memfd seal, generated original+parent inotify observation, a synthetic test packet, an ENOSYS capability probe or a repository-document SHA **cannot be substituted for either actual protected gate**. We do not use, relax or mutate protected annual workflows/rulesets to compensate. No independent approval has been issued; all protected authorities remain false.

**Explicit exclusions:** never run/retry/rerun/dispatch the protected 2023 annual workflow; never read or change protected annual source/evidence; do not install/change production CI workflows, ref permissions or administrator security controls, merge/promote draft code, synthesize Strategy V1, place demo or live orders, trade or touch broker state.
