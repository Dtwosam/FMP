# DEC-626 — Uninstalled precheckout GitHub Actions job-level if preview

**Status: SOURCE ONLY / FABRICATED IDENTITY / NOT INSTALLED / NO DISPATCH OR TRADING AUTHORIZATION.**

## Why job-level admission matters

In the current installed `.github/workflows/phase8a-annual-pattern-catalogue.yml`, all three jobs (`annual_preflight`, `annual_cell`, `annual_freeze`) run `actions/checkout@v6` **before** their existing main-only `workflow_dispatch` shell guards. DEC-624 showed three required future layers: job-level admission before checkout, exact independent SHA/ref identity check before setup/pip, and a recheck before historical/evidence network calls. DEC-625 showed why the expected identity cannot be derived from the same runner's `GITHUB_SHA` or `GITHUB_REF`.

DEC-626 is an **actual GitHub expression string-shape preview** using only a deliberately unapproved fixed manifest fixture. It does **not** create a real `jobs.<job>.if` field, add a workflow file, or make the active workflow tag-compatible. A future reviewer can examine an example expression for all three jobs rather than relying solely on fabricated step-name labels.

The identical candidate expressions require:
- `github.event_name == 'workflow_dispatch'`, exact repository name, `github.ref_type == 'tag'`, and the fixed unapproved candidate ref.
- `github.sha` and `github.workflow_sha` equal a separately specified SHA fixture; `github.workflow` and `github.workflow_ref` equal the reviewed name/path@ref.
- `inputs.annual_segment_label == '2023'`, `inputs.previous_annual_freeze_run_id == '37663157285'`, `github.run_number == 385`, and `github.run_attempt == 1`.

All values come from the source-pinned DEC-625 **in-memory unapproved fixture**; no GitHub environment value becomes its own approved comparison target. The report retains every proposed expression as **text in JSON**, not as YAML. Exact-string checking and 24 missing/late/weakened/self-attested/injected-variable cases verify only the shape of the proposed string—not its actual GitHub Actions runtime semantics.

```sh
PYTHONPATH=src python scripts/phase8a_annual_pattern_catalogue_2023_precheckout_job_if_preview.py assess --out /tmp/dec626-precheckout-job-if.json
```

The CLI has only `assess`, writes only outside the checkout, and does not call GitHub. It pins installed annual workflow Git blob `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1` and unchanged installed 2023 runtime blob `cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191`. Rehashed report forgeries and boolean/int substitutions cannot grant authority.

## Design limitations and next independent checks

A GitHub **job-level** `if` is evaluated before job steps, **not before GitHub itself loads or parses the workflow definition**. A job-level `if` therefore cannot alone eliminate workflow-definition provenance risk. Exact self-consistency does not establish that a tag is immutable, nondeletable, or unretargetable; does not authenticate an external approved SHA; and does not prove continuous admin no-bypass enforcement during workflow dispatch. Nor can a static expression replace runtime checks before pip/install and evidence access.

Do **not** copy these unapproved SHA/ref fixtures to an active workflow or treat passing tests as permission. The real next gate is an independently authenticated reviewed exact identity manifest, continuous administrator-enforced tag immutability/no-bypass, a separately reviewed and tested **installed** workflow plus 2023 runtime authorization amendment, renewed workflow run inventory and a distinct one-shot action decision. Under issue #779, run 385, attempt 2, run 386+, future-year runs, historical artifact downloads, strategy promotion, broker mutation, demo/live or real-money trading are not authorized.
