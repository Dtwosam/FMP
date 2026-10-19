# DEC-1773 — Independently pin Phase7 source Markdown SHA-256 alongside Git blob SHA-1

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent, one-commit source-only child of PR #2019 at `3955a6df1685c40f8c6b92771badd2346107d82e`.

The Phase7 USDJPY 15m Stage2 historical cost replay already verifies the original Git blob SHA-1 `c1d8fe7f71681f2e06b472c77525a4dd800c896f`. This change also pins the **same exact source document bytes** with SHA-256 `afe93d152e52c5a18b003967f97a411f2a1ac60dd54d913920536faa1863bb75`, computed from the published `docs/phase7-walk-forward-evidence.md` on that exact parent lineage. SHA-1 alone is not a suitable sole high-assurance content identity; both must match before any historical results are replayed.

The source-only JSON report now discloses both hashes, while an independent negative test simulates a compromised/misleading SHA-1 check and verifies that an altered document still fails its SHA-256 pin. Ordinary byte edits are rejected as before, and no source file, historical result, immutable Stage2 run, reported profit, selection threshold, or trading assumption changes.

Adds **3** methods (**6468 proposed cumulative**). Source-only retrospective report still exits code **3** even when valid, rejects invalid input with code **2** and no stdout, and does not grant execution. This strengthens **local documentation integrity**, not independent administration, runner OS isolation, live repository ref continuity, accepted Phase8A Strategy V1 economics or broker permissions. Protected 2023/run385/attempt1, issues #779/#820/#821 and all demo/live/real-money trading remain BLOCKED. Exact-head Phase3/full regression CI and independent qualified review required.
