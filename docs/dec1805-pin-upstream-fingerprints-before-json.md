# DEC-1805 — Pin all six historical source fingerprints before JSON output

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2051, SHA `4837443d17ede62ec661ec3823f4569741046f7d`.

The consolidated Markdown renderer compared the five documentary SHA-256 hashes, historical workflow Git blob SHA-1 and workflow byte SHA-256 against frozen source constants, but the compiler had not done the same before producing **JSON**. A drifted upstream reporter could therefore advertise a fabricated source hash, observed `main` ref or fixture-only status in a machine-readable BLOCKED handoff. The underlying source readers still have their own pins; this closes the reporting boundary and cannot authenticate current GitHub or runtime state.

Both formats now require the entire ordered five-source digest mapping to equal the frozen `PINNED_SOURCE_SHA256`, the published stale main SHA/date to equal reviewed constants, both historical workflow fingerprints to match the independently pinned SHA-1/SHA-256 values, and the historical **not current installed workflow** flag to remain exact True. Unexpected upstream claims fail with controlled `InvalidHandoff` before output.

Four adversarial tests cover documentary digest substitution, forged stale-ref/date claims, historical workflow hash or fixture-status tampering and clean failure of JSON/Markdown CLI (exit 2, no stdout). Normal BLOCKED reporting remains exit 3. **6,612 cumulative proposed source-defined test methods**.

Nothing reads protected annual data or modifies current GitHub ref, workflow, ruleset, runner or broker; no 2023/run385/attempt1 dispatch, shadow/demo/live trading, money or profit claim. External #779/#820/#821 and the eight independently attested proof packages remain MISSING/BLOCKED. Exact-head Phase3/full regression CI and qualified human review required.
