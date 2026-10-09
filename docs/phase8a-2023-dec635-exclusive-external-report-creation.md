# DEC-635 — Exclusive creation for four offline 2023 audit CLI reports

**Draft stacked fix; NOT a dispatch, annual run, merge approval or trading gate.** Based on the unmerged exact head of DEC-628 / PR #797, not on `main`. The parent PR's independent review and merge sequence are unchanged.

## Failure mode

The DEC-628 audit CLIs reject checkout-local output and reject an *already existing* conflicting external report. However, the read/write sequence was:

```python
if target.exists(): ...
target.write_text(content, encoding="utf-8")
```

A second process could create a conflicting external report **after** the existence check and **before** `write_text`; `write_text` could then truncate the second process's report. The local checkout SHA-256 inventory and existing-report idempotency tests do not cover this race.

## Proposed narrow change

A package-local, pure Python helper `annual_pattern_catalogue_2023_external_report_create.py` uses `Path.open('x', encoding='utf-8')` to create a new external **leaf file exclusively**. If the leaf exists before the check or appears during creation, identical content is treated idempotently without rewriting; conflicting, unreadable or dangling-symlink output fails closed. It is called by four assessment scripts: DEC-612 main-lock readiness; DEC-615 immutable-tag feasibility; DEC-616 tag-ruleset static review; DEC-617 tag-ref guard rehearsal. Each CLI retains its own `Path(__file__).resolve().parents[1]` checkout boundary validation, immutable offline model checks, and `sys.dont_write_bytecode=True` initialization. The helper resides in `src/fmp/discovery` because the existing DEC-628 subprocess tests copy that full package, but may stage only the four selected scripts.

Dedicated seven-method regressions exercise new external creation, identical report no-rewrite, pre-existing conflict rejection, **deterministic competing-file creation during exclusive open**, identical competing-file behavior, dangling symlink protection, and unchanged SHA-256/mtime of a hard-linked checkout inode. Existing DEC-628 focused tests should remain green under the staged package model. GitHub CI is still required to validate the actual branch.

## Residual limits

This is a **leaf-file no-clobber improvement**, not a lock on arbitrary destination parent directories, defense against hostile symlink/path replacement during resolution or write, or a guarantee of fully atomic/durable publication. Partial file creation is possible if writing is interrupted. The CLI still cannot dispatch the annual workflow, consume or retry run385, read protected historical data, merge a pull request, or trade. Independent code review and all immutable-ref controls remain required. See issue #779.
