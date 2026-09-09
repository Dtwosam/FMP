import {
  assertEquals,
  assertThrows,
} from "jsr:@std/assert@1";
import {
  assertTrustedGithubAuditClaims,
  AUDIT_PROTOCOL,
  validateAuditPaths,
} from "./validation.ts";

const trustedClaims = {
  iss: "https://token.actions.githubusercontent.com",
  aud: "fmp-supabase-raw-audit",
  repository: "Dtwosam/FMP",
  repository_id: "1342321016",
  repository_owner_id: "42391449",
  ref: "refs/heads/main",
  event_name: "workflow_dispatch",
  runner_environment: "github-hosted",
  workflow_ref:
    "Dtwosam/FMP/.github/workflows/phase1-final-cloud-audit.yml@refs/heads/main",
};

Deno.test("audit protocol is pinned for client preflight", () => {
  assertEquals(AUDIT_PROTOCOL, "fmp-raw-audit-v1");
});

Deno.test("accepts trusted manual final-audit workflow identity", () => {
  assertEquals(assertTrustedGithubAuditClaims(trustedClaims), true);
});

Deno.test("rejects push identity even from main", () => {
  assertThrows(
    () => assertTrustedGithubAuditClaims({ ...trustedClaims, event_name: "push" }),
    Error,
    "event_name",
  );
});

Deno.test("rejects another workflow", () => {
  assertThrows(
    () => assertTrustedGithubAuditClaims({
      ...trustedClaims,
      workflow_ref:
        "Dtwosam/FMP/.github/workflows/phase1-full-acquisition.yml@refs/heads/main",
    }),
    Error,
    "workflow",
  );
});

Deno.test("accepts canonical manifest and raw audit paths", () => {
  const paths = [
    "manifests/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.json",
    "raw/dukascopy/v1/USDJPY/2026/07/20/ASK_candles_min_1.bi5",
  ];
  assertEquals(validateAuditPaths(paths), paths);
});

Deno.test("rejects impossible and out-of-snapshot canonical-looking paths", () => {
  for (const path of [
    "raw/dukascopy/v1/EURUSD/2024/01/31/BID_candles_min_1.bi5",
    "manifests/dukascopy/v1/EURUSD/2014/11/31/BID_candles_min_1.json",
    "raw/dukascopy/v1/USDJPY/2026/07/21/ASK_candles_min_1.bi5",
  ]) {
    assertThrows(() => validateAuditPaths([path]), Error, "snapshot");
  }
});

Deno.test("rejects duplicate, invalid, empty, and overlarge audit path batches", () => {
  assertThrows(() => validateAuditPaths([]), Error, "1..100");
  assertThrows(
    () => validateAuditPaths([
      "raw/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.bi5",
      "raw/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.bi5",
    ]),
    Error,
    "duplicate",
  );
  assertThrows(() => validateAuditPaths(["../secret"]), Error, "invalid");
  assertThrows(
    () => validateAuditPaths(
      Array.from(
        { length: 101 },
        (_, i) =>
          `raw/dukascopy/v1/EURUSD/2024/00/${String((i % 28) + 1).padStart(2, "0")}/BID_candles_min_1.bi5#${i}`,
      ),
    ),
    Error,
  );
});
