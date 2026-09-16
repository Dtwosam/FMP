from pathlib import Path

path = Path("src/fmp/shadow/review_compiler.py")
text = path.read_text(encoding="utf-8")
wrong = '''        _validate_segment(\n            segment,\n            code_commit=code_commit,\n            qualification_fingerprint=qualification_fingerprint,\n            provider_closures=provider_closures,\n        )\n'''
right = '''        _validate_segment(\n            segment,\n            code_commit=code_commit,\n            qualification_fingerprint=qualification_fingerprint,\n        )\n'''
if wrong not in text:
    raise SystemExit("accidental _validate_segment closure argument not found")
text = text.replace(wrong, right, 1)
call = '''        aggregate = _compile_segments(\n            segment_dirs,\n            registration=registration,\n            code_commit=code_commit,\n            qualification_fingerprint=qualification_fingerprint,\n        )\n'''
fixed = '''        aggregate = _compile_segments(\n            segment_dirs,\n            registration=registration,\n            code_commit=code_commit,\n            qualification_fingerprint=qualification_fingerprint,\n            provider_closures=provider_closures,\n        )\n'''
if call not in text:
    raise SystemExit("_compile_segments review call not found")
text = text.replace(call, fixed, 1)
path.write_text(text, encoding="utf-8")
