# DEC-1419 — October 16 annual matrix source regression CI incident and forward remediation

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Documentation-only strict one-commit child of #1642 DEC-1418 at 25e4cabb682ce89585c27144ea53ef9045771708. No source-defined test methods added: **1,438 proposed methods** remain in the unmerged draft lineage. No annual code, workflow, runner, repository settings or trading functionality changes.

## Exact-head original CI evidence, immutable failures

The newly introduced DEC-1410 reviewer in #1634 incorrectly matched matrix field names using ASCII lowercase letters and underscore only: [a-z_]+. The installed annual source has feature_zip_sha256 and outcome_zip_sha256. Their digits caused rows_from_checked_in_text to raise ValueError: unknown matrix row source syntax on the canonical, unchanged source.

- PR #1634, SHA a5aac96eee5fd0625b073a5683823be391abf5da, historical/general run 38960720448: **FAILURE**, 6,269 tests, 9 failures, 2 errors, 702 skips; Phase 3: success.
- PR #1635, SHA fa84ce6adcbd32e2aa0ee750582030f25c588e5c, historical/general run 38961149723: **FAILURE**, 6,283 tests, 9 failures, 2 errors, 702 skips; Phase 3: success.
- PR #1636, SHA 99aff63f729e850d3281b5341fc4ef08ac89f629, historical/general run 38961445605: **FAILURE**, 6,292 tests, 9 failures, 2 errors, 702 skips; Phase 3: success.

These are three separate **failed exact commits**, not transient statuses and not permissions to rerun protected research. GitHub job logs show the same matrix test class in all three. Phase 3 did not include the failing historical test path and cannot substitute for the historical/general suite.

## Forward-only remediation and review boundary

#1637 DEC-1413 corrects the field regex to [a-z0-9_]+ and adds five positive/negative regression methods. #1638 DEC-1414 pins nine reviewed feature/outcome ID/digest literal tuples (not fetched artifact bytes). #1639 DEC-1415 rejects changed matrix container, extra axes and strategy keys. #1640 DEC-1416 adds manual-event-trigger inventory checks. #1641 DEC-1417 examines inline alternate automatic triggers; its incomplete manual-key scalar comparison is forward-corrected by #1642 DEC-1418. Original failed PR heads #1634–#1636 remain immutable and must **never** be rewritten as green after a descendant passes.

At this incident packet's creation, the corrective lineage's full historical CI remained pending. Record an individual exact-head Phase3 + full historical result for each draft before saying it is fully verified, and retain **independent qualified review** separately. Proposed source-defined method counts and historical suite runtime test executions measure different things.

## External security gates not repaired by test CI

Actual OS-enforced immutability of the protected original including aliases, inherited descriptors, children and uploader (DEC-650/#820) remains **BLOCKED**. Immutable, exclusive GitHub server-side ref/SHA approval and one-shot 2023 annual run385/attempt1 allocation (DEC-651/#821/#779) remains **BLOCKED**. The unchanged installed workflow checks a mutable main-ref context inside jobs; main protected=false and repository rulesets=0 at the last read-only snapshot. Source-only method checks, token read scopes or 18-cell artifact ID literals cannot prove those controls.

**Hold:** no protected-data access, annual dispatch/retry, GitHub workflow/ruleset/branch mutation, merge, Strategy V1 promotion, Phase 8B, broker operation or trading.
