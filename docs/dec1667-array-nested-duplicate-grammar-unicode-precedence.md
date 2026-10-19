# DEC-1667 — Array-nested duplicate JSON keys outrank Unicode surrogate failures

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent, one-commit tests/docs child of #1913 at `ac0c4e88b3be1a7c8b84ec247dbb627e41b2187d`. Adds 25 regression methods (**4,237 proposed source-defined tests**).

This matrix deliberately creates two defects inside one nested dictionary **under an array**: a Unicode-decoded duplicate child member and an unpaired UTF-16 surrogate in an additional key or value. Six previously verified evidence paths (runs, jobs, PR comparison files, Phase 3 scenarios, full Git-tree entries, merge parents) are crossed with the Unicode fault location (key/value) and textual placement (before/after the duplicate), yielding 24 negative cases plus one clean control.

Permissive `json.loads` produces a dictionary still containing unpaired Unicode. Strict bounded JSON/text and stdin review must refuse the **earlier grammar defect** with exactly `BUNDLE_JSON_GRAMMAR_UNREVIEWED`, rather than expose a Unicode or downstream category-evidence diagnostic. The test construction walks an explicit path without global substitutions.

Each case verifies the source-only clean fixture is unchanged, safe verdict field inventory, no sample source-path echo, and false independent-original OS proof, exclusive server dispatch proof, and annual-run authorization. Own exact-head Phase 3/full historical-general CI and qualified independent review required. No production/parser/resources/workflow/security changes, protected original/archive/artifact reads, annual dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
