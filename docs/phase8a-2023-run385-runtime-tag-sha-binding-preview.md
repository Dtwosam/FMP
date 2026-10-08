# DEC-622 — Inert 2023 runtime tag, workflow-ref and SHA binding contract

**Status:** source-only synthetic test contract, not installed as a 2023 runtime gate, not an annual workflow amendment, and **not authorization** to create a tag or dispatch research run 385.

## Why this change is necessary

DEC-619 established the check-then-dispatch race on mutable `main`; DEC-620 demonstrated why untrusted "no bypass" claims are not an administrator lock; DEC-621 modeled why an ambiguous HTTP response cannot be retried. The remaining immutable-tag execution option also needs an **explicit proposed ref/commit binding** at runtime.

The installed `.github/workflows/phase8a-annual-pattern-catalogue.yml` (Git blob `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1`) requires `GITHUB_REF=refs/heads/main` in preflight, all 18 cells and freeze. The installed `src/fmp/discovery/annual_pattern_catalogue_2023_runtime_authorization.py` (Git blob `cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191`) checks the supplied code commit **format**, year, run number, attempt and predecessor. It does not authenticate or compare the **exact** dispatched tag ref and GitHub's resolved SHA against a separately reviewed immutable ref/commit tuple.

DEC-622 adds an **uninstalled**, source-pinned negative-test design for that missing ref/SHA identity condition. Nothing is wired into the active annual dispatcher, annual workflow or historical research runtime.

## Hypothetical identity tuple

The exact-match rehearsal requires all of the following at once:

- `GITHUB_EVENT_NAME=workflow_dispatch`, `GITHUB_REF_TYPE=tag`, and `GITHUB_REF` equal to the reviewed exact ref.
- `GITHUB_SHA` strictly equal to the separately reviewed code commit, not just a well-formed SHA.
- `GITHUB_REPOSITORY=Dtwosam/FMP`, `GITHUB_WORKFLOW=phase8a-annual-pattern-catalogue`, and `GITHUB_WORKFLOW_REF` equal to `Dtwosam/FMP/.github/workflows/phase8a-annual-pattern-catalogue.yml@<exact tag ref>`.
- `annual_segment_label=2023`, `GITHUB_RUN_NUMBER=385`, `GITHUB_RUN_ATTEMPT=1` and previous 2022 freeze run id `37663157285`.

Tests include the positive **synthetic** tuple and 22 negative cases: wrong branch/tag/workflow path/repository, ref type, SHA, case, event, year, run number, attempt, predecessor, boolean-integer confusion, absent fields and injected authority fields.

**The only positive fixture is deliberately non-authoritative**:
```text
refs/tags/fmp/phase8a/2023/run385/dec622-unapproved-fixture
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```
No real tag is created, discovered, verified or approved. A passing synthetic predicate proves only that the inert string-comparison design discriminates the defined sample cases. It provides **no proof that an actual tag is immutable**. Administrator-enforced, no-bypass, non-deletable and non-retargetable tag restrictions must be independently authenticated for the entire server-side dispatch window; an exact workflow/runtime amendment needs separate review and approval.

## Read-only local preview

```sh
PYTHONPATH=src python scripts/phase8a_annual_pattern_catalogue_2023_runtime_tag_sha_binding_preview.py assess --out /tmp/dec622-tag-sha-binding-preview.json
```

The only CLI command is `assess`. It writes the JSON preview **outside** the checkout, refuses conflicting outputs, performs no GitHub/API/network calls, and cannot write or install an active workflow or runtime gate.

The report is regenerated from the **exact pinned existing annual workflow and 2023 runtime sources**; its verifier compares the complete canonical JSON payload, including booleans and integers, rejecting a rehashed forged authorization, scenario or source fingerprint. Every report forces `installed_runtime_ref_sha_binding=false`, `installed_workflow_tag_ref_binding=false`, `authoritative_immutable_tag_proven=false`, `annual_workflow_dispatch_authorized=false`, `annual_run385_action_authorized=false`, `retry_authorized=false`, `trading_authorized=false` and `dispatch_blocked=true`.

## Remaining release blockers

Issue #779 remains OPEN. A real tag path still requires independently authenticated administrator ruleset/ref evidence, an **approved executable three-job workflow amendment**, an **approved 2023 runtime SHA/ref binding** applied *before historical reads*, new security review and CI of the actual installation, fresh run-385 inventory, and a distinct tightly scoped one-shot dispatch decision. A pure predicate cannot make GitHub dispatch a protected ref nor recover the single run number if dispatch fails. Main-exclusive-lock remains an alternative, similarly requiring continuous authenticated no-bypass exclusivity.

No attempt 2, run 386+, 2024+ research, cross-year comparison, strategy synthesis/promotion, Phase 8B, broker mutation, demo/live order, real-money activity or trading is authorized by DEC-622.
