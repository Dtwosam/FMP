# DEC-1791 — Canonical six-source equality for human security handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2037, SHA `8a2d7c519e3aedb82062539eb980cedaece96aef`.

The DEC-1782 offline six-source human review already checks pinned input bytes, all missing administrator/security proofs, BLOCKED execution flags, and every pre-gate command payload against its inert historical workflow fixture. This patch closes a remaining *presentation boundary*: a caller could pass a dictionary with unknown root metadata, missing schema, self-asserted approval fields, or other data the formatter did not explicitly check. That object could still produce an official-looking Markdown report.

The updated validator re-generates the complete **source-bound canonical BLOCKED report** from the exact reviewed local files and compares strict, sorted JSON serialization of the entire caller's report with the canonical result (nonfinite numbers are rejected). This rejects extra/missing/renamed fields, numeric aliases of booleans, altered nested values and fictitious permission metadata. No runtime GitHub, credentials, protected data, broker, real installed workflow or admin/OS/one-shot inventory is consulted. Canonical comparison is evidence-integrity validation only, never external attestation.

Adds **6** focused tests (**6568 proposed source-defined methods**). Valid offline BLOCKED reports still exit code 3, invalid files exit 2 without stdout, and all one-shot 2023/run385/attempt1 and trading permissions stay false. Issues #779/#820/#821 remain independently blocked. Exact-head Phase3/full historical-general CI and qualified review required.
