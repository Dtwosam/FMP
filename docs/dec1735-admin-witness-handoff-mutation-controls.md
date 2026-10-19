# DEC-1735 — Adversarial tests of administrator handoff refusal

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit exact-parent tests/docs child of #1981 at `d3048ee1ce2f8266f1b15360efe18b80bfbdd343`.

Adds **24 source-defined methods** (**6019 proposed total**). The earlier DEC-1721 handoff captures ten independently required DEC-613 human-proof identifiers, four DEC-620 continuity intervals, six enforcement claims, exact 2023/run385/attempt1 identity and explicit `BLOCKED` release disposition. This draft now executes **its actual existing guard methods** against in-memory forged handoff text to prove unsafe edits do not silently pass:

- Ten independent tests flip one blank `[ ]` proof item into a falsely checked `[x]`; the real DEC-613 checklist assertion must reject each, instead of treating a document-edit as genuine administrator authentication.
- Four tests remove each named continuity-interval bullet shape and six remove named enforcement-claim bullet shapes; original guards must detect missing requested observations.
- Additional tests forge `release_status=AUTHORIZED`, insert an executable `gh workflow run` instruction, and replace one-shot run385 **attempt 1** with attempt 2; all must fail original tests.
- A pristine control runs all twelve original handoff source checks.

All changes are source-only and in memory. The assertions protect the **human-review request document**, not the *substance, freshness, authorship or independence* of external administrator evidence. A checked checkbox in a future *new, separately reviewed evidence artifact* cannot itself authorize an annual run; all actual admin bypass/enforcement, privileged runner isolation, workflow amendments and one-shot decisions remain separate mandatory gates.

No main/tag/ruleset mutation, installed workflow changes, protected annual dataset or workflow run385 dispatch, retries, historical economic calculation, broker/demo/live order or real-money trading. External issue #779, DEC-650/#820 and DEC-651/#821 remain **BLOCKED**. Own exact-head Phase 3/full historical-general CI and qualified independent review required.
