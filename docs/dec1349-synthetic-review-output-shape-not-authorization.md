# DEC-1349 — Source-only synthetic diagnostic output contract is stable and nonauthorizing

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit child of #1572 DEC-1348 at `e97ccea5d7d5570faae647dbe3600c8b99bff9eb`, **957 proposed distinct source-defined tests** (+4). The classifier is a pure in-memory negative helper, not the protected run385 gate.

Four tests pin the exact **12-key report schema**, the eight authority flags all having the identity `False`, persistent `BLOCKED` gate-state labels, and `STATIC_BLOCKERS` as the ordered prefix of every diagnostic. Two checks require deterministic encoding through Python's standard-library JSON serialization and verify that arbitrary alleged independent reviewer metadata and protected ref approvals in **otherwise ignored** fields cannot change diagnostic output or leak fabricated PUBLIC canary text.

**The report schema is a diagnostic, not a permission API.** A stable JSON report does not authenticate a protected filesystem object, OS policy deployment, GitHub server-side workflow SHA, immutable ref, annual inventory or reviewer signature. A caller can always supply self-reported values; the only safe outcome of this uninstalled source-only function is denial. The tests do not access annual evidence, production, broker or any network endpoint.

Every original exact head requires independently completed successful Phase3 AND full historical CI plus qualified independent security review. Earlier failed SHAs remain failed. Protected independent no-write DEC-650/#820 and exclusive immutable annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No annual protected source/evidence, run/test/retry/rerun/dispatch, workflow/ruleset installation, production/trading, mergers or promotions.
