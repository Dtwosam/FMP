const EXPECTED = {
  repository: "Dtwosam/FMP",
  repository_id: "1342321016",
  repository_owner_id: "42391449",
  ref: "refs/heads/main",
  runner_environment: "github-hosted",
  workflow_ref:
    "Dtwosam/FMP/.github/workflows/phase1-full-acquisition.yml@refs/heads/main",
} as const;

const ALLOWED_EVENTS = new Set(["push", "workflow_dispatch"]);

export function assertTrustedGithubClaims(
  claims: Record<string, unknown>,
): true {
  for (const [key, expected] of Object.entries(EXPECTED)) {
    if (claims[key] !== expected) {
      throw new Error(`untrusted GitHub ${key}`);
    }
  }
  if (!ALLOWED_EVENTS.has(String(claims.event_name ?? ""))) {
    throw new Error("untrusted GitHub event_name");
  }
  return true;
}

export function manifestsEquivalent(
  first: Record<string, unknown>,
  retry: Record<string, unknown>,
): boolean {
  const canonical = (manifest: Record<string, unknown>): string =>
    JSON.stringify(
      Object.entries(manifest)
        .filter(([key]) => key !== "retrieved_at_utc")
        .sort(([left], [right]) => left.localeCompare(right)),
    );
  return canonical(first) === canonical(retry);
}

const RAW_RE = /^raw\/dukascopy\/v1\/(EURUSD|GBPUSD|USDJPY)\/(\d{4})\/(0[0-9]|1[01])\/([0-2][0-9]|3[01])\/(BID|ASK)_candles_min_1\.bi5$/;
const MANIFEST_RE = /^manifests\/dukascopy\/v1\/(EURUSD|GBPUSD|USDJPY)\/(\d{4})\/(0[0-9]|1[01])\/([0-2][0-9]|3[01])\/(BID|ASK)_candles_min_1\.json$/;

export function validateObjectPath(path: string): true {
  if (!RAW_RE.test(path) && !MANIFEST_RE.test(path)) {
    throw new Error("invalid FMP storage object path");
  }
  return true;
}


export type ManifestStorageInvariant =
  | {
    status: "complete";
    rawPath: string;
    sha256: string;
    sizeBytes: number;
  }
  | {
    status: "not_found";
    rawPath: string;
  };

function rawPathForManifest(manifestPath: string): string {
  const match = MANIFEST_RE.exec(manifestPath);
  if (!match) {
    throw new Error("manifest path is not canonical");
  }
  const [, pair, year, month, day, side] = match;
  return `raw/dukascopy/v1/${pair}/${year}/${month}/${day}/${side}_candles_min_1.bi5`;
}

export function manifestStorageInvariant(
  manifestPath: string,
  manifest: Record<string, unknown>,
): ManifestStorageInvariant {
  const status = manifest.status;
  const rawPath = rawPathForManifest(manifestPath);

  if (status === "not_found") {
    return { status: "not_found", rawPath };
  }

  if (status === "complete") {
    const sha256 = manifest.sha256;
    const sizeBytes = manifest.compressed_size_bytes;
    if (
      typeof sha256 !== "string" ||
      !/^[0-9a-f]{64}$/.test(sha256) ||
      typeof sizeBytes !== "number" ||
      !Number.isInteger(sizeBytes) ||
      sizeBytes <= 0
    ) {
      throw new Error("complete manifest raw metadata is invalid");
    }
    return {
      status: "complete",
      rawPath,
      sha256,
      sizeBytes,
    };
  }

  throw new Error("manifest status is invalid");
}

export function rawPathForNotFoundManifest(
  manifestPath: string,
  manifest: Record<string, unknown>,
): string | null {
  if (manifest.status !== "not_found") return null;
  return manifestStorageInvariant(manifestPath, manifest).rawPath;
}

export function isStorageObjectNotFound(error: unknown): boolean {
  if (!error || typeof error !== "object") return false;
  const item = error as Record<string, unknown>;
  const status = String(
    item.status ?? item.statusCode ?? item.httpStatusCode ?? "",
  );
  const code = String(item.error ?? item.code ?? "");
  return status === "404" &&
    new Set(["NoSuchKey", "NotFound", "not_found"]).has(code);
}
