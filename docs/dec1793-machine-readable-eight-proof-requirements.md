# DEC-1793 — Machine-readable missing-proof acceptance criteria in blocked handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2039 at `01b755050939fe518d10ce6773055293390726fe`.

DEC-1792 made the human Markdown security-review packet actionable by displaying the exact acceptance criteria for all eight MISSING independent administrator/security proofs. The JSON output, however, still listed only the proof ID, owner role and missing status. An operator integrating the JSON with a separate reviewer tracker could lose the requirements or accidentally substitute a different checklist.

DEC-1793 adds `independent_proof_acceptance_criteria`, a strictly ordered JSON dictionary keyed by the eight existing frozen proof IDs and populated directly from the same source-only `PROOF_ACCEPTANCE_CRITERIA`. The human Markdown renderer now uses that exact map after source-bound canonical comparison, so machine and human formats always describe the same outstanding external actions. This change adds **no new approval schema**, cannot ingest proof or status claims, and never transitions any proof to PASS. All eight status fields remain MISSING and both formats remain strictly BLOCKED (exit 3).

Adds 4 tests (**6576 cumulative proposed source-defined**) for exact machine/human agreement, unknown approval field rejection and no trading/annual authority. Protected 2023/run385/attempt1 is still blocked; actual admin no-bypass, inherited rulesets, real runner OS, source and one-shot inventory witnesses remain unverified (#779/#820/#821). No protected market reads, GitHub workflow/ref/ruleset/branch mutations, broker/demo/live orders, live money or trading. Exact-head Phase3/full historical-general CI and independent qualified review required.
