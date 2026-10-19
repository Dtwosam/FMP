# DEC-1763 — Frozen source bytes for offline security-review packets

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit source-only child of PR #2009 at `c1d0e24e920ce1f8798c119485a9341cda6520e0`.

Previous DEC-1752–1762 checks validated important semantic flags and printed SHA-256s, but the hashes were recomputed from the same untrusted source files and never compared against independently frozen values. A wording-only, label or provenance amendment could therefore pass validation and acquire a normal-looking BLOCKED handoff with an unreviewed hash.

DEC-1763 pins **five exact SHA-256 values** of existing source-only packets in the reporter; it verifies those values after the semantic guards, so semantic mutation controls retain their meaning and byte provenance is checked independently before any report is emitted. A changed byte—even if the critical BLOCKED fields and evidence-gate wording stay identical—now fails closed with status **2**, a BLOCKED error and no stdout. An unchanged, validated BLOCKED packet still yields status **3**, never 0.

This code-pinned hash is a *review-bound source identity check*, not independent administrative attestation, signature, present-time GitHub protection, source-of-truth promotion, runner OS proof or executable annual authority. Intentional changes to these five packets need new qualified code/evidence review and refreshed pins; the helper does not automatically accept replacement bytes.

Adds **7** focused adversarial tests (**6417 cumulative proposed source-defined**) including editorial-only mutations on all five packets and CLI no-output refusal. No real GitHub security/ruleset changes, protected annual data access, workflow dispatch/retry, Strategy V1 evidence, broker/demo/live orders or trading. Issues #779, #820 and #821 remain BLOCKED. Exact-head Phase 3/full historical-general CI and qualified independent review required.
