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

const MANIFEST_FIELDS = [
  "manifest_version",
  "retrieval_method",
  "source",
  "source_url",
  "pair",
  "side",
  "date_utc",
  "granularity",
  "source_format",
  "record_size_bytes",
  "month_indexing",
  "status",
  "http_status",
  "sha256",
  "compressed_size_bytes",
  "records",
  "retrieved_at_utc",
].sort();

export function validateManifestForStorage(
  manifestPath: string,
  manifest: Record<string, unknown>,
): true {
  const keys = Object.keys(manifest).sort();
  if (
    keys.length !== MANIFEST_FIELDS.length ||
    keys.some((key, index) => key !== MANIFEST_FIELDS[index])
  ) {
    throw new Error("manifest fields are not canonical");
  }

  const match = MANIFEST_RE.exec(manifestPath);
  if (!match) {
    throw new Error("manifest identity path is not canonical");
  }
  const [, pair, yearText, sourceMonthText, dayText, side] = match;
  const year = Number(yearText);
  const sourceMonth = Number(sourceMonthText);
  const day = Number(dayText);
  const calendarMonth = sourceMonth + 1;
  const date = new Date(Date.UTC(year, sourceMonth, day));
  if (
    date.getUTCFullYear() !== year ||
    date.getUTCMonth() !== sourceMonth ||
    date.getUTCDate() !== day
  ) {
    throw new Error("manifest identity date is invalid");
  }

  const dateUtc = `${yearText}-${String(calendarMonth).padStart(2, "0")}-${dayText}`;
  const sourceUrl =
    `https://datafeed.dukascopy.com/datafeed/${pair}/${yearText}/` +
    `${sourceMonthText}/${dayText}/${side}_candles_min_1.bi5`;
  const fixed: Record<string, unknown> = {
    manifest_version: 1,
    retrieval_method: "dukascopy-public-daily-m1-bi5-v1",
    source: "dukascopy",
    source_url: sourceUrl,
    pair,
    side,
    date_utc: dateUtc,
    granularity: "1m",
    source_format: "bi5-lzma-daily-candles",
    record_size_bytes: 24,
    month_indexing: "zero_based_in_source_url",
  };
  for (const [field, expected] of Object.entries(fixed)) {
    if (manifest[field] !== expected) {
      throw new Error(`manifest identity mismatch for ${field}`);
    }
  }

  const retrievedAt = manifest.retrieved_at_utc;
  if (
    typeof retrievedAt !== "string" ||
    !/(?:Z|[+-]\d{2}:\d{2})$/.test(retrievedAt) ||
    !Number.isFinite(Date.parse(retrievedAt))
  ) {
    throw new Error("manifest retrieved_at_utc must be timezone-aware");
  }

  if (manifest.status === "complete") {
    if (
      typeof manifest.http_status !== "number" ||
      !Number.isInteger(manifest.http_status) ||
      manifest.http_status < 200 ||
      manifest.http_status >= 300 ||
      typeof manifest.sha256 !== "string" ||
      !/^[0-9a-f]{64}$/.test(manifest.sha256) ||
      typeof manifest.compressed_size_bytes !== "number" ||
      !Number.isInteger(manifest.compressed_size_bytes) ||
      manifest.compressed_size_bytes <= 0 ||
      typeof manifest.records !== "number" ||
      !Number.isInteger(manifest.records) ||
      manifest.records < 1 ||
      manifest.records > 1440
    ) {
      throw new Error("complete manifest metadata is invalid");
    }
    return true;
  }

  if (manifest.status === "not_found") {
    if (
      manifest.http_status !== 404 ||
      manifest.sha256 !== null ||
      manifest.compressed_size_bytes !== null ||
      manifest.records !== null
    ) {
      throw new Error("not_found manifest metadata is invalid");
    }
    return true;
  }

  throw new Error("manifest status is invalid");
}

const FROZEN_START_MS = Date.UTC(2015, 0, 1);
const FROZEN_END_EXCLUSIVE_MS = Date.UTC(2026, 7, 21);

function validateFrozenPathDate(match: RegExpExecArray): void {
  const year = Number(match[2]);
  const sourceMonth = Number(match[3]);
  const day = Number(match[4]);
  const value = new Date(Date.UTC(year, sourceMonth, day));

  if (
    value.getUTCFullYear() !== year ||
    value.getUTCMonth() !== sourceMonth ||
    value.getUTCDate() !== day
  ) {
    throw new Error("FMP storage object path has invalid calendar date");
  }

  const timestamp = value.getTime();
  if (
    timestamp < FROZEN_START_MS ||
    timestamp >= FROZEN_END_EXCLUSIVE_MS
  ) {
    throw new Error("FMP storage object path is outside frozen Phase 1 snapshot");
  }
}

export function validateObjectPath(path: string): true {
  const match = RAW_RE.exec(path) ?? MANIFEST_RE.exec(path);
  if (!match) {
    throw new Error("invalid FMP storage object path");
  }
  validateFrozenPathDate(match);
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
