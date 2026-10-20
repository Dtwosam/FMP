# DEC-1802 — Exact integer types for historical runtime and matrix scope

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2048, `d82fb9456b5ca358f0eb1090893f57c5866733e7`.

The consolidated JSON compiler's historical workflow checks previously used Python numeric equality for `job_count == 3`, matrix cell counts `==18` and `==9`, and the job runtime gate positions were later checked only by Markdown's canonical comparison. This could allow upstream producer numeric aliases such as `3.0`, `18.0` or `4.0` into machine-readable JSON despite source-only fixture values being integers.

The compiler now checks exact `int` types for every historical job-count/matrix-count/runtime-gate-index before building either format, alongside plain-dictionary upstream nested shapes. It preserves the existing values and blocked scope; this cannot attest the current installed runner, GitHub controls, any protected data, the actual historical run inventory or external execution permissions.

Four new adversarial test methods (6,604 proposed source-defined cumulative): float job counts, float matrix counts, float gate positions and both CLI formats rejecting numeric aliases (exit 2, empty stdout). Valid reports remain BLOCKED exit 3. No annual 2023/run385/attempt1 action, main/ref/workflow/security/ruleset changes, broker/demo/live order, real-money trading or economic claim. All independent proof packages and #779/#820/#821 still MISSING/BLOCKED. Exact-head Phase3/full CI and qualified review required.
