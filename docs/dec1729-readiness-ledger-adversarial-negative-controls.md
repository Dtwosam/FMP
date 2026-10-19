# DEC-1729 — Mutational negative controls for Phase 8A source-only ledger

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1975 at `e55fcf0fe6ca4d3c77cee8da963a989fa8341416`.

Adds **35 source-defined methods** (**5,950 proposed total**) that execute the *actual* DEC-1728 source-ledger inventory assertions against deep-copied, deliberately corrupted in-memory inputs. These are negative-control **tests of the tests**, not merely additional static assertions about the unmodified ledger.

- Fourteen separate attempts to flip each named protected annual-run, protected history, rerun, strategy promotion, demo, broker and live authorization flag to `true`. Every one must be rejected by the existing strict-denial assertion.
- Extra or missing authorization flag, extra or missing root field, fabricated allowed action list, or a Boolean masquerading as the action list.
- Falsely upgrading the 2022 historical predecessor into live authorization; falsely claiming the prior unprotected main snapshot is protected or current.
- Both forged `HISTORICALLY_FROZEN` and `promotion_eligible=true` for each blocked 2023, 2024, 2025 and 2026-YTD segment.
- Incorrect run number (386) and Boolean `true` masquerading as attempt 1, plus duplicate member names that become identical after JSON Unicode escape decoding.
- One genuine unmodified control executes all eight original DEC-1728 checks and must pass.

Each test guards the original constant document and does not patch or mutate the verified source fixture, change approval facts or claim independent administrator/runner evidence. Failures must be detected *inside the DEC-1728 assertion*; the tests do not accept a raised error while building the mutant as successful refusal.

The Phase 8A one-shot 2023/run385/attempt1 and issue #779 remain **BLOCKED**; this file cannot create source trust, authority, annual runs or economic edge. Own exact-head Phase 3/full historical-general CI plus independent qualified review required. No parser/production/workflow/security changes, protected artifacts, annual dispatch/retry, tag/main or ruleset mutation, broker, demo, live or trading.
