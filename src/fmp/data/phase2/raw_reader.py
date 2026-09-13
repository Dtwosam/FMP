from __future__ import annotations

import hashlib
from pathlib import Path

from fmp.data.manifest import load_manifest, validate_manifest_for_key
from fmp.data.types import RawChunkKey


class RawReadError(RuntimeError):
    pass


class LocalRawChunkReader:
    def __init__(self, root: Path) -> None:
        self._root = Path(root)

    def read(self, key: RawChunkKey) -> bytes | None:
        raw_path = self._root / "raw" / key.relative_raw_path
        manifest_path = self._root / "manifests" / key.relative_manifest_path
        if not manifest_path.exists():
            raise RawReadError(f"missing Phase 1 manifest: {manifest_path}")

        try:
            manifest = load_manifest(manifest_path)
        except (OSError, ValueError) as exc:
            raise RawReadError(f"invalid Phase 1 manifest: {manifest_path}") from exc
        validated = validate_manifest_for_key(key, manifest)
        if validated is None:
            raise RawReadError(f"Phase 1 manifest failed validation: {manifest_path}")

        if validated.status == "not_found":
            if raw_path.exists():
                raise RawReadError(f"raw object present beside not_found manifest: {raw_path}")
            return None

        if validated.status != "complete":
            raise RawReadError(f"unsupported Phase 1 manifest status for local raw read: {validated.status}")
        if not raw_path.exists():
            raise RawReadError(f"missing Phase 1 raw object: {raw_path}")

        body = raw_path.read_bytes()
        if validated.compressed_size_bytes != len(body):
            raise RawReadError(f"Phase 1 raw size mismatch: {raw_path}")
        if validated.sha256 != hashlib.sha256(body).hexdigest():
            raise RawReadError(f"Phase 1 raw checksum mismatch: {raw_path}")
        return body
