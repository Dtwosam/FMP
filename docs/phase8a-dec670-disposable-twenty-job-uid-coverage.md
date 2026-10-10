# DEC-670 — Rehearse exact 20 synthetic separate-UID job identities

**SOURCE-ONLY / DRAFT / NEVER MERGE / NEVER authorization.**

This is a source-only composition test stacked on DEC-669 draft #840. It calls the disposable root-only Linux UID-split permission witness for **20 independent generated temporary fixtures**, matching the job-type topology in the current DEC-650 annual isolation contract: one synthetic preflight, 18 synthetic cells and one synthetic freeze. It does **not** execute any actual annual job or read an annual artifact.

The six-digit matrices and real workflow jobs are NOT started; the 18 cell identities are only labels annual_cell:01 through annual_cell:18. Each invocation generates only public fake checkout and external report bytes, drops the subprocess to UID/GID 65534, clears groups and capabilities, asserts kernel permission denials, and checks the fake sources and reports unchanged.

The composition refuses to treat one clean preflight as coverage for the other 19. The aggregator requires exactly the 20 known job names, a full set of expected permission/identity checks for **each** job, both authorization fields explicitly false, no findings or missing/inconclusive checks, and status LOCAL_DISPOSABLE_WITNESS_UNVERIFIED. Any missing, unexpected or malformed job, blocked OS test, hidden skip or true authorization claim returns BLOCKED. Even 20 consistent synthetic results produce only LOCAL_DISPOSABLE_WITNESS_UNVERIFIED and exit 3, never a security PASS.

Normal CLI is inert, BLOCKED exit 2:

    python -B scripts/dec670_disposable_20_job_uid_coverage.py

Opt-in local disposable Linux root host only:

    python -B scripts/dec670_disposable_20_job_uid_coverage.py --execute-disposable-20

The source defines **11 regression tests**, with one manual opt-in OS composition skipped by default. On a disposable local Linux root container the real 20-iteration composition returned covered_synthetic_jobs=20, no findings and deliberately exit 3, not an approval.

## What remains blocked

This run uses **the same tiny fake child 20 times**, not actual preflight/cell/freeze runtimes or their workflow commands, data, capabilities, network, mounted aliases, descriptors or process tree. The verdict rests partly on the disposable child self-report; there is no independently authenticated runner OS observation, no trusted external GitHub artifact uploader/receipt, no live race-hardening of all 20 jobs and no security approval. Source regressions and completed GitHub CI do not substitute for real DEC-650 #820 acceptance.

DEC-651 #821 and issue #779 require a separate exclusive immutable source and one-shot server-controlled dispatch admission boundary, which is still BLOCKED. The 2023 annual run385 must remain unconsumed. No original #796–800 draft approvals can be inferred from this test.

No merge/ready promotion, production workflow changes, protected data access, GitHub permissions/ref/ruleset/runner changes, annual dispatch/test/retry, strategy promotion or broker/trading action is authorized.
