import {
  assertEquals,
  assertThrows,
} from "jsr:@std/assert@1";
import {
  assertTrustedGithubClaims,
  isStorageObjectNotFound,
  manifestStorageInvariant,
  manifestsEquivalent,
  rawPathForNotFoundManifest,
  validateObjectPath,
} from "./validation.ts";

const trustedClaims = {
  iss: "https://token.actions.githubusercontent.com",
  aud: "fmp-supabase-raw-ingest",
  repository: "Dtwosam/FMP",
  repository_id: "1342321016",
  repository_owner_id: "42391449",
  ref: "refs/heads/main",
  event_name: "workflow_dispatch",
  runner_environment: "github-hosted",
  workflow_ref:
    "Dtwosam/FMP/.github/workflows/phase1-full-acquisition.yml@refs/heads/main",
};

Deno.test("accepts trusted workflow-dispatch identity", () => {
  assertEquals(assertTrustedGithubClaims(trustedClaims), true);
});

Deno.test("accepts trusted main-branch push identity for cloud smoke", () => {
  assertEquals(assertTrustedGithubClaims({ ...trustedClaims, event_name: "push" }), true);
});

Deno.test("rejects other event types", () => {
  assertThrows(() => assertTrustedGithubClaims({ ...trustedClaims, event_name: "schedule" }), Error, "event_name");
});

Deno.test("rejects a token from another repository", () => {
  assertThrows(() => assertTrustedGithubClaims({ ...trustedClaims, repository: "attacker/FMP" }), Error, "repository");
});

Deno.test("rejects a token from a different workflow", () => {
  assertThrows(
    () => assertTrustedGithubClaims({ ...trustedClaims, workflow_ref: "Dtwosam/FMP/.github/workflows/tests.yml@refs/heads/main" }),
    Error,
    "workflow",
  );
});

Deno.test("accepts canonical raw and manifest object paths", () => {
  assertEquals(validateObjectPath("raw/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.bi5"), true);
  assertEquals(validateObjectPath("manifests/dukascopy/v1/USDJPY/2024/00/02/ASK_candles_min_1.json"), true);
});

Deno.test("rejects path traversal and non-V1 objects", () => {
  for (const path of [
    "../secret",
    "raw/dukascopy/v1/EURUSD/2024/00/02/evil.exe",
    "raw/dukascopy/v1/XAUUSD/2024/00/02/BID_candles_min_1.bi5",
    "raw/dukascopy/v2/EURUSD/2024/00/02/BID_candles_min_1.bi5",
  ]) {
    assertThrows(() => validateObjectPath(path), Error);
  }
});

Deno.test("manifest retries may differ only by retrieval timestamp", () => {
  const first = {
    pair: "EURUSD",
    side: "BID",
    status: "complete",
    sha256: "abc",
    records: 1440,
    retrieved_at_utc: "2026-08-22T01:00:00Z",
  };
  const retry = { ...first, retrieved_at_utc: "2026-08-22T02:00:00Z" };
  assertEquals(manifestsEquivalent(first, retry), true);
});

Deno.test("manifest retry rejects substantive differences", () => {
  const first = {
    pair: "EURUSD",
    side: "BID",
    status: "complete",
    sha256: "abc",
    records: 1440,
    retrieved_at_utc: "2026-08-22T01:00:00Z",
  };
  assertEquals(manifestsEquivalent(first, { ...first, sha256: "changed" }), false);
  assertEquals(manifestsEquivalent(first, { ...first, records: 1439 }), false);
  assertEquals(manifestsEquivalent(first, { ...first, extra: "field" }), false);
});


Deno.test("not_found manifest maps to canonical raw counterpart", () => {
  const manifestPath =
    "manifests/dukascopy/v1/USDJPY/2022/11/17/BID_candles_min_1.json";
  const rawPath = rawPathForNotFoundManifest(manifestPath, {
    status: "not_found",
  });
  assertEquals(
    rawPath,
    "raw/dukascopy/v1/USDJPY/2022/11/17/BID_candles_min_1.bi5",
  );
});

Deno.test("complete manifest does not request raw counterpart absence check", () => {
  assertEquals(
    rawPathForNotFoundManifest(
      "manifests/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.json",
      { status: "complete" },
    ),
    null,
  );
});

Deno.test("storage missing-key errors are distinguished from other 404s", () => {
  assertEquals(
    isStorageObjectNotFound({ statusCode: "404", error: "NoSuchKey" }),
    true,
  );
  assertEquals(
    isStorageObjectNotFound({ status: 404, error: "NotFound" }),
    true,
  );
  assertEquals(
    isStorageObjectNotFound({ statusCode: "404", code: "not_found" }),
    true,
  );
  assertEquals(
    isStorageObjectNotFound({ statusCode: "404", error: "NoSuchBucket" }),
    false,
  );
  assertEquals(
    isStorageObjectNotFound({ statusCode: "500", error: "InternalError" }),
    false,
  );
});


Deno.test("complete manifest requires canonical raw expectation", () => {
  const invariant = manifestStorageInvariant(
    "manifests/dukascopy/v1/GBPUSD/2020/05/01/BID_candles_min_1.json",
    {
      status: "complete",
      sha256: "a".repeat(64),
      compressed_size_bytes: 321,
    },
  );
  assertEquals(invariant, {
    status: "complete",
    rawPath: "raw/dukascopy/v1/GBPUSD/2020/05/01/BID_candles_min_1.bi5",
    sha256: "a".repeat(64),
    sizeBytes: 321,
  });
});

Deno.test("complete manifest rejects missing or invalid raw metadata", () => {
  const path =
    "manifests/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.json";
  for (const manifest of [
    { status: "complete", compressed_size_bytes: 123 },
    { status: "complete", sha256: "not-a-sha", compressed_size_bytes: 123 },
    { status: "complete", sha256: "a".repeat(64), compressed_size_bytes: 0 },
    { status: "complete", sha256: "a".repeat(64), compressed_size_bytes: 12.5 },
  ]) {
    assertThrows(
      () => manifestStorageInvariant(path, manifest),
      Error,
      "complete manifest",
    );
  }
});

Deno.test("manifest storage invariant rejects unknown status", () => {
  assertThrows(
    () =>
      manifestStorageInvariant(
        "manifests/dukascopy/v1/USDJPY/2024/00/02/ASK_candles_min_1.json",
        { status: "mystery" },
      ),
    Error,
    "status",
  );
});
