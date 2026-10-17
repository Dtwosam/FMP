# DEC-1496 — Bound run inventories in direct and JSON offline CI review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1741, exact parent `fa8c61e32ded7b6a9504925579439e8963bfb164`. Adds **10 synthetic unittest methods**, for **2,209 proposed source-defined tests**.

Source maps already carry bounded text/file entry contracts, but in-memory offline evidence input also holds an uncapped top-level `runs` list and four run-ID-indexed dictionaries for job data, checkout observations, raw logs and digest receipts. A direct caller can construct large collections without crossing the separate raw JSON text-length bound. Enforce at most 4,096 top-level run entries and 8,192 entries for each run-indexed map **before sorting/decoding or nested review**; retain strict decimal signed-64-bit key checks and all original source consistency rules. The schema value must be an actual `str`, not a subclass with surprising behavior.

Ten tests cover exact plain schema and subclass rejection, over/exact run collection, every run-indexed map, precedence before bad ID keys and stdin safe diagnostics. These measures prevent unbounded synthetic input processing but do not authenticate the GitHub data provider, establish independent OS protections, or grant annual execution authority.

Own PR-associated Phase 3 and full historical/general CI on exact commit, and independent qualified review, required. DEC-650/#820 protected-original OS no-write and DEC-651/#821/#779 exclusive immutable 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No annual dispatch/retry, protected originals/archive/artifacts, installed workflow/security changes, merge, deployment or trading.
