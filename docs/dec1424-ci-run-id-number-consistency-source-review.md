# DEC-1424 — Require unique CI run IDs and valid run numbers

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit synthetic test/docs child #1647 DEC-1423 at 249e46ab580361d04595db52136f3aab3b771768; five new methods, **1,481 proposed source-defined methods**.

A pair of caller-supplied full GitHub workflow run records can pass per-name, per-path and per-SHA source checks yet claim the same numeric run ID for both required suites. Since the two workflows are distinct, those run IDs cannot legitimately be identical. This forward-only audit now rejects duplicate positive IDs across required workflows and requires positive integer run_number values for each (rejecting missing, zero and Python bool values). Exact workflow path/id, PR event, SHA, completed-success, first-attempt checks from DEC-1423 remain unchanged. These additions are pure offline consistency assertions, not an independently trusted provenance chain.

Five focused test methods added to the 27 existing; **all 32 focused methods passed locally** before PR creation. The actual repository full historical/general CI and Phase3 at this exact head still must pass separately, with qualified independent review. GitHub REST records must be obtained separately and authenticated; no API is called by these tests.

DEC-650/#820 actual OS-protected original no-write and DEC-651/#821/#779 immutable exclusive 2023 run385/attempt1 server admission remain BLOCKED. No protected sources, archive download, annual execution/retry, real workflow/branch/ruleset/permission mutation, merge, promotion or trading.
