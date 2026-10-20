# DEC-1799 — Test offline six-source compilation under denied side-effect APIs

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit source-only child of #2045 at `ebf9931a3df50d78a00a476044214c2604fc8b3d`.

The offline six-source Phase8A BLOCKED handoff declares that it does not dispatch workflows, spawn broker activity, access the network or modify local source evidence. Existing tests checked the `no_external_actions_performed` result field, which is a **claim**, not a direct process-level negative control.

Add four source-only adversarial execution-boundary tests that fail if the compiler invokes `subprocess.Popen` or opens a network `socket.socket`, and fail on attempts to open any local file with write/create/truncate/append flags through `os.open`. The guarded build must still read existing reviewed source inputs and produce a permanently BLOCKED report. Both CLI formats must return the normal nonzero blocked status **3** with process and socket APIs denied.

These are narrow Python-process regression guards, **not** sandbox enforcement, an installed GitHub Actions runner/OS witness, an external network monitor, broker attestation, or proof of permission. They must never be treated as satisfying any of the eight independent external MISSING proof packages. Four test methods (6,596 cumulative proposed source-defined).

No source-of-truth decision, historical research, protected 2023/run385 attempt1, installed runner/ref/workflow/ruleset, broker, demo/live trading or money used. #779/#820/#821 remain BLOCKED. Exact-head Phase3 and full regression CI plus qualified independent review required.
