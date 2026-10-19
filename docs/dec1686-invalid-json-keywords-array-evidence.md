# DEC-1686 — Malformed JSON keywords inside array-contained evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1932 at `3c3783decb5ada6d973bb170f7799e506c578f6c`.

Adds **37 methods** (**4,975 proposed source-defined total**): six invalid unquoted literal tokens at each of six representative array-contained dictionary locations (runs, compare.files, jobs_by_run, phase3 scenario, full-tree entry, merge parent), plus a clean synthetic control. A unique synthetic quoted marker is substituted with the malformed literal only after JSON serializing a deep-copied fixture. Unmodified clean input remains consistent; corrupted text is refused at strict JSON grammar ingress via both text and stdin, without a raw-path echo, changed authority flag, or accidental acceptance as a normal Boolean/null.

Own exact-head Phase 3/full historical-general CI and qualified independent review required. Only tests/docs and caller-supplied synthetic evidence. No production/parser/resource/workflow/security updates, protected originals/archive/artifacts, annual run/dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
