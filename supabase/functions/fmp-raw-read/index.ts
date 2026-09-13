import { createClient } from "npm:@supabase/supabase-js@2.116.0";
import { createRemoteJWKSet, jwtVerify } from "npm:jose@5.10.0";
import { assertTrustedGithubReadClaims, deriveReadPaths, READ_PROTOCOL, validateManifestForRead, validateReadRequest } from "./validation.ts";

const BUCKET = "fmp-raw";
const AUDIENCE = "fmp-supabase-raw-read";
const GITHUB_ISSUER = "https://token.actions.githubusercontent.com";
const GITHUB_JWKS = createRemoteJWKSet(new URL("https://token.actions.githubusercontent.com/.well-known/jwks"));
const MAX_REQUEST_BYTES = 4096;

async function authenticate(req: Request): Promise<void> {
  const auth = req.headers.get("authorization") ?? "";
  if (!auth.startsWith("Bearer ")) throw new Error("missing OIDC token");
  const { payload } = await jwtVerify(auth.slice(7), GITHUB_JWKS, { issuer: GITHUB_ISSUER, audience: AUDIENCE });
  assertTrustedGithubReadClaims(payload as Record<string, unknown>);
}

async function sha256Hex(bytes: Uint8Array): Promise<string> {
  const input = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer;
  const digest = await crypto.subtle.digest("SHA-256", input);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function fail(error: string, status: number): Response {
  return Response.json({ error }, { status, headers: { "Cache-Control": "no-store" } });
}

Deno.serve(async (req: Request) => {
  if (req.method !== "GET" && req.method !== "POST") return fail("method_not_allowed", 405);
  try { await authenticate(req); } catch (error) { console.error(error); return fail("unauthorized", 401); }
  if (req.method === "GET") return Response.json({ status: "ready", protocol: READ_PROTOCOL }, { headers: { "Cache-Control": "no-store" } });

  let readRequest;
  try {
    const body = new Uint8Array(await req.arrayBuffer());
    if (body.length === 0 || body.length > MAX_REQUEST_BYTES) return fail("invalid_body_size", 400);
    readRequest = validateReadRequest(JSON.parse(new TextDecoder().decode(body)) as unknown);
  } catch (error) { console.error(error); return fail("invalid_read_request", 400); }

  try {
    const secretKeys = JSON.parse(Deno.env.get("SUPABASE_SECRET_KEYS") ?? "{}");
    const secretKey = secretKeys.default;
    if (!secretKey) throw new Error("missing Supabase secret key");
    const supabase = createClient(Deno.env.get("SUPABASE_URL")!, secretKey);
    const paths = deriveReadPaths(readRequest);

    const { data: manifestBlob, error: manifestError } = await supabase.storage.from(BUCKET).download(paths.manifestPath, {}, { cache: "no-store" });
    if (manifestError || !manifestBlob) throw new Error("manifest download failed");
    let manifestJson: unknown;
    try { manifestJson = JSON.parse(new TextDecoder().decode(new Uint8Array(await manifestBlob.arrayBuffer()))); }
    catch { throw new Error("manifest JSON malformed"); }
    const manifest = validateManifestForRead(readRequest, manifestJson);

    if (manifest.status === "not_found") {
      return Response.json({ status: "not_found", protocol: READ_PROTOCOL, pair: readRequest.pair, side: readRequest.side, date_utc: readRequest.date_utc }, { status: 404, headers: { "Cache-Control": "no-store" } });
    }

    const { data: rawBlob, error: rawError } = await supabase.storage.from(BUCKET).download(paths.rawPath, {}, { cache: "no-store" });
    if (rawError || !rawBlob) throw new Error("raw download failed");
    const raw = new Uint8Array(await rawBlob.arrayBuffer());
    if (raw.length !== manifest.compressedSizeBytes) throw new Error("raw size mismatch");
    if (await sha256Hex(raw) !== manifest.sha256) throw new Error("raw SHA-256 mismatch");

    return new Response(raw, { status: 200, headers: {
      "Content-Type": "application/octet-stream", "Cache-Control": "no-store",
      "X-FMP-Protocol": READ_PROTOCOL, "X-FMP-Pair": readRequest.pair,
      "X-FMP-Side": readRequest.side, "X-FMP-Date-UTC": readRequest.date_utc,
      "X-FMP-SHA256": manifest.sha256, "X-FMP-Size-Bytes": String(manifest.compressedSizeBytes),
      "X-FMP-Manifest-Status": "complete",
    }});
  } catch (error) { console.error(error); return fail("storage_read_failed", 502); }
});
