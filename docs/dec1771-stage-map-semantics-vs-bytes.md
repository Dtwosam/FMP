# DEC-1771 — Separate blocked-stage semantics from source-byte identity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent child of #2017 (head `f096e764264906e1419a10ede8393923f0f87e4d`).

The offline DEC-1752 diagnostic had one unnecessary source policy: `tuple(snap["downstream_gate_state"]) == STAGES` required JSON **object insertion order** to match stage ordering. This confused the 2026-10-19 historical/general CI failure in DEC-1763's adversarial test (later correctly repaired by DEC-1769). JSON objects are *unordered maps by contract* and a different JSON serialization order should not be confused with a completed annual, economic, or trading gate.

This patch introduces `_blocked_stage_map_is_valid` to validate **exactly eight named stages**, each with the strict string `"BLOCKED"`, independent of key insertion order. Omitted/extra stage names, PASS/READY values, non-dicts, Boolean/numeric aliases fail the semantic helper. A reordered or otherwise rewritten source file still **cannot** pass the complete diagnostic: the five pinned SHA-256 source-byte fingerprints reject all unreviewed byte changes, with CLI exit **2**, BLOCKED stderr and no stdout. A valid frozen report remains nonauthorizing exit **3**.

Adds **4** direct semantic and full-CLI regression tests (**6460 proposed source-defined methods cumulative**) and revises DEC-1769's obsolete map-order test expectation. No main branch, GitHub ruleset/workflow/runner, protected 2023 annual run385/attempt1, protected data, broker/demo/live action or StrategyV1 economics is affected. The safety blocker issues #779/#820/#821 remain open, and no SHA equality here is an independent administrator or live-run admission proof. Own exact-head Phase3/full regression CI and separate qualified review required.
