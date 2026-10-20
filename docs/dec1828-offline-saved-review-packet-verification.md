# DEC-1828 — Strict offline verification of a saved BLOCKED review packet

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent child of PR #2074 at `2a6344124c90f98e3d594aced0519a8e45ab56af`.

An exported seven-source review packet could previously be read by a human but not reliably revalidated by the offline tooling. A new `--verify-report FILE` mode opens a **bounded regular file without following symlinks**, strictly rejects duplicate JSON members and nonstandard NaN/Infinity, canonicalizes the complete saved packet with `allow_nan=False`, verifies the local SHA-256 request fingerprint and compares the entire result byte-for-byte in canonical JSON with **fresh pinned offline source** evidence. The mode prohibits overriding evidence inputs at the same time.

Recomputation of a SHA-256 alone is **not authentication**; a malicious editor can rehash a forged claim, so even a correctly rehashed packet is rejected unless its full content exactly matches a fresh build from frozen inputs. No current GitHub/admin or OS review is performed and no separately signed human evidence is collected.

Five new adversarial tests (6,677 cumulative proposed source-defined methods) cover unchanged BLOCKED packets, correctly rehashed forged approvals, duplicate/NaN/nonfinite JSON, symlinked file rejection and both CLI outcomes. Valid input still exits nonzero **3** with BLOCKED, invalid exits **2 without stdout**. No installed workflow/ruleset/ref/runner mutation, protected annual 2023/run385/attempt1 dispatch or data read, broker/demo/live order, money or profitability claim. External #779/#820/#821 and eight independent proofs remain MISSING/BLOCKED. Exact-head Phase3/full regression CI and independent qualified review required.
