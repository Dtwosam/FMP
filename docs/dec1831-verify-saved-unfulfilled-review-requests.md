# DEC-1831 — Strict offline verification of saved compact reviewer requests

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent child of PR #2077 `c2ee195efdfbd4c85cb892157974166855b7ef12`.

The Phase8A seven-source script already emits full `json`, canonical human `markdown` and compact `requests` outputs, and DEC-1828 verifies a saved *full* JSON report. Independent reviewers also need to reject forged saved *compact* request files. The new `--verify-requests FILE` mode uses the same 1 MiB bounded no-follow file reader, strict JSON duplicate-key/NaN/Infinity rejection and complete canonical JSON equality with a **freshly rebuilt** pinned compact request packet. Merely retaining or recalculating the parent's digest does not authenticate a forged signoff.

A valid input remains permanently BLOCKED and exits 3, echoing the freshly validated compact packet. Invalid proof rows, unknown fields, malformed JSON and symlinked/oversized inputs fail with exit 2 and **no stdout**. Mixed verification modes or source override paths are explicitly prohibited, as is Markdown formatting of the compact verified request.

Five new source-defined tests (**6,691 cumulative proposed**) verify an unchanged packet, a forged reviewer signoff, nested duplicate/nonfinite JSON, file boundaries and controlled CLI behavior. These are local review-document consistency checks, not independent admin/runner OS proofs, real signatures or an authorization. All eight external proofs and #779/#820/#821 remain MISSING; protected 2023/run385/attempt1, installed workflow/ref/ruleset changes, broker/demo/live orders, money and profitability remain blocked. Own exact-head Phase3/full regression CI and qualified independent review required.
