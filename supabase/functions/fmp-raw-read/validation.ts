export const READ_PROTOCOL = "fmp-raw-read-v1";

const EXPECTED = {
  repository: "Dtwosam/FMP",
  repository_id: "1342321016",
  repository_owner_id: "42391449",
  ref: "refs/heads/main",
  event_name: "workflow_dispatch",
  runner_environment: "github-hosted",
  workflow_ref:
    "Dtwosam/FMP/.github/workflows/phase2-cloud-golden.yml@refs/heads/main",
} as const;

const PAIRS = new Set(["EURUSD", "GBPUSD", "USDJPY"]);
const SIDES = new Set(["BID", "ASK"]);
const START_MS = Date.UTC(2015, 0, 1);
const END_EXCLUSIVE_MS = Date.UTC(2026, 7, 21);
const SHA_RE = /^[0-9a-f]{64}$/;
const REQUIRED_MANIFEST_FIELDS = new Set([
  "manifest_version", "retrieval_method", "source", "source_url", "pair",
  "side", "date_utc", "granularity", "source_format", "record_size_bytes",
  "month_indexing", "status", "http_status", "sha256",
  "compressed_size_bytes", "records", "retrieved_at_utc",
]);

export type ReadRequest = {
  pair: "EURUSD" | "GBPUSD" | "USDJPY";
  side: "BID" | "ASK";
  date_utc: string;
};

export type ValidatedManifest =
  | { status: "complete"; sha256: string; compressedSizeBytes: number; records: number }
  | { status: "not_found" };

export function assertTrustedGithubReadClaims(claims: Record<string, unknown>): true {
  for (const [key, expected] of Object.entries(EXPECTED)) {
    if (claims[key] !== expected) throw new Error(`untrusted GitHub ${key}`);
  }
  return true;
}

function parseDate(value: string): { year: number; month: number; day: number; timestamp: number } {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (!match) throw new Error("date_utc must be YYYY-MM-DD");
  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const timestamp = Date.UTC(year, month - 1, day);
  const parsed = new Date(timestamp);
  if (
    parsed.getUTCFullYear() !== year || parsed.getUTCMonth() !== month - 1 ||
    parsed.getUTCDate() !== day || timestamp < START_MS || timestamp >= END_EXCLUSIVE_MS
  ) throw new Error("date_utc outside frozen snapshot");
  return { year, month, day, timestamp };
}

export function validateReadRequest(payload: unknown): ReadRequest {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    throw new Error("read request root must be an object");
  }
  const record = payload as Record<string, unknown>;
  const keys = Object.keys(record).sort();
  if (keys.join(",") !== "date_utc,pair,side") {
    throw new Error("read request must contain exactly pair, side, date_utc");
  }
  if (typeof record.pair !== "string" || !PAIRS.has(record.pair)) throw new Error("invalid pair");
  if (typeof record.side !== "string" || !SIDES.has(record.side)) throw new Error("invalid side");
  if (typeof record.date_utc !== "string") throw new Error("invalid date_utc");
  parseDate(record.date_utc);
  return record as ReadRequest;
}

export function deriveReadPaths(request: ReadRequest): { manifestPath: string; rawPath: string } {
  const { year, month, day } = parseDate(request.date_utc);
  const zero = month - 1;
  const prefix = `dukascopy/v1/${request.pair}/${year.toString().padStart(4, "0")}/${zero.toString().padStart(2, "0")}/${day.toString().padStart(2, "0")}`;
  return {
    manifestPath: `manifests/${prefix}/${request.side}_candles_min_1.json`,
    rawPath: `raw/${prefix}/${request.side}_candles_min_1.bi5`,
  };
}

function validUtcTimestamp(value: unknown): boolean {
  if (typeof value !== "string" || !value.endsWith("Z")) return false;
  const time = Date.parse(value);
  return Number.isFinite(time);
}

function exactFieldSet(record: Record<string, unknown>): boolean {
  const keys = Object.keys(record);
  return keys.length === REQUIRED_MANIFEST_FIELDS.size && keys.every((key) => REQUIRED_MANIFEST_FIELDS.has(key));
}

export function validateManifestForRead(request: ReadRequest, manifest: unknown): ValidatedManifest {
  if (!manifest || typeof manifest !== "object" || Array.isArray(manifest)) throw new Error("manifest must be an object");
  const record = manifest as Record<string, unknown>;
  if (!exactFieldSet(record)) throw new Error("manifest field set mismatch");
  if (typeof record.manifest_version !== "number" || !Number.isInteger(record.manifest_version) || record.manifest_version !== 1) throw new Error("invalid manifest_version");

  const { year, month, day } = parseDate(request.date_utc);
  const sourceUrl = `https://datafeed.dukascopy.com/datafeed/${request.pair}/${year.toString().padStart(4, "0")}/${(month - 1).toString().padStart(2, "0")}/${day.toString().padStart(2, "0")}/${request.side}_candles_min_1.bi5`;
  const fixed: Record<string, unknown> = {
    retrieval_method: "dukascopy-public-daily-m1-bi5-v1",
    source: "dukascopy",
    source_url: sourceUrl,
    pair: request.pair,
    side: request.side,
    date_utc: request.date_utc,
    granularity: "1m",
    source_format: "bi5-lzma-daily-candles",
    record_size_bytes: 24,
    month_indexing: "zero_based_in_source_url",
  };
  for (const [key, expected] of Object.entries(fixed)) {
    if (record[key] !== expected) throw new Error(`manifest ${key} mismatch`);
  }
  if (!validUtcTimestamp(record.retrieved_at_utc)) throw new Error("invalid retrieved_at_utc");

  if (record.status === "complete") {
    if (typeof record.http_status !== "number" || !Number.isInteger(record.http_status) || record.http_status < 200 || record.http_status >= 300) throw new Error("invalid complete http_status");
    if (typeof record.sha256 !== "string" || !SHA_RE.test(record.sha256)) throw new Error("invalid complete sha256");
    if (typeof record.compressed_size_bytes !== "number" || !Number.isInteger(record.compressed_size_bytes) || record.compressed_size_bytes <= 0) throw new Error("invalid complete size");
    if (typeof record.records !== "number" || !Number.isInteger(record.records) || record.records < 1 || record.records > 1440) throw new Error("invalid complete records");
    return { status: "complete", sha256: record.sha256, compressedSizeBytes: record.compressed_size_bytes, records: record.records };
  }
  if (record.status === "not_found") {
    if (record.http_status !== 404 || record.sha256 !== null || record.compressed_size_bytes !== null || record.records !== null) throw new Error("invalid not_found contract");
    return { status: "not_found" };
  }
  throw new Error("unsupported manifest status");
}
