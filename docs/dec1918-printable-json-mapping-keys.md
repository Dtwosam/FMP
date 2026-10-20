# DEC-1918 — Preserve canonical JSON evidence mapping keys

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2166 `ab7a5b8b3b1b6c056b454b357998847c4094f7bb`.

The Phase3 deterministic serializer previously converted `Mapping` keys with `str(key)` before JSON serialization. This could silently conflate distinct source keys such as integer `1` and string `"1"`, damaging claimed run/economic evidence provenance. Require ordinary `dict` or immutable `MappingProxyType`, and ordinary printable string keys, including Unicode. Existing empty-string keys and valid nested Unicode identity data continue to round-trip; invalid aliases, control/surrogate keys and hostile user-defined mappings fail before output I/O under the prior artifact preflight.

Three synthetic source-defined regression methods cover key collisions, control/surrogate denial without filesystem creation, and valid nested multilingual mapping roundtrip. **6,916 cumulative proposed methods**; own exact-commit Phase3/full historical-general CI and independent evidence review required. This is source-only protection, not approved provenance, real OS runner isolation or economic performance evidence.

Phase8A #779/#820/#821 remain OPEN/BLOCKED; eight independent administrator/ref/installed early workflow/runner OS/DEC609-610 provenance/fresh inventory/human permission proof packages missing. Protected 2023/run385/attempt1 and later annual research, Strategy V1, shadow/demo/live broker funds and installed GitHub controls remain BLOCKED. No research dispatch, trade or capital movement.
