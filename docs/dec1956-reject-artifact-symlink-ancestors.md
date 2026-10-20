# DEC-1956 — Reject linked ancestors of read-only artifact root

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source/tests/docs child of #2204 at `2ab5e6802259aac29304affbca4c06981ba16095`.

The read-only artifact verifier already rejects a symlink at the output-directory leaf and uses no-follow descriptors when opening the manifest and fixed evidence files. It could still follow a symlink in a parent directory (for example `linked-parent/artifacts`) and verify a different directory from the intended root. Before accessing the manifest, check the lexical absolute output-directory path and every parent component for an existing symlink; refuse any linked ancestor. Preserve direct-directory paths.

Two synthetic methods exercise linked absolute and relative parent paths while a normal direct target continues to verify. **6,992 cumulative proposed source-defined test methods**. Exact-head Phase3/full historical-general CI and qualified independent filesystem review required. Lexical symlink checks are non-atomic and do **not** protect against adversarial concurrent parent swaps, bind mounts or privileged runner compromise. Source-only checks are not OS sandbox proofs, independently authenticated historical data or investment performance.

Historic #2178–#2191 and #2198 full-suite failure records remain failed. Phase8A #779/#820/#821 and eight independent external proof packages MISSING; accepted catalogue ends 2022/run384, protected 2023/run385/attempt1, future annual discovery, Strategy V1 economics, shadow/demo/live brokers/capital and installed GitHub refs/workflows/rulesets/runners blocked. No protected dispatch, trades or money.
