# DEC-1829 — Saved-packet no-follow, size and immutable-input boundaries

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2075 at `41836694aae27f8be1dfcc1ba4c54bfa1b05fa80`.

The offline `--verify-report` reader must not accept a symlink in an ancestor directory, oversized/noncanonical JSON or mixed source overrides. The unchanged fail-closed no-follow regular-file reader enforces parent and leaf symlink checks and a 1 MiB source-document bound. New tests exercise an actual parent-directory symlink and an oversized saved packet, alongside nonobject/numeric-alias inputs.

Before this change, CLI verification with a conflicting `--docs-root`, `--workflow` or `--worksheet` invoked argparse's process-level `SystemExit`, which is difficult for embedding tools to interpret as a controlled, no-output invalid-evidence result. This branch changes that path to **return 2 with empty stdout** and a BLOCKED stderr explanation, without reading the disputed source. A further test confirms the verifier leaves saved bytes unchanged across its three output choices.

Five adversarial tests (6,682 cumulative proposed source-defined). Valid saved packets remain BLOCKED, exit 3; invalid packets and mixed evidence inputs fail exit 2. These are local file-integrity tests, **not real runner OS/admin permission**, independent one-shot inventory, or approval. #779/#820/#821 and eight external proof packages remain MISSING. No protected 2023/run385/attempt1, GitHub installed workflow/ref/ruleset mutation, broker/demo/live order or real money. Own exact-head CI and qualified review required.
