import { createClient } from "npm:@supabase/supabase-js@2";
import { createRemoteJWKSet, jwtVerify } from "npm:jose@5";
import {
  assertTrustedGithubAuditClaims,
  validateAuditRequest,
} from "./validation.ts";

const BUCKET = "fmp-raw";
const AUDIENCE = "fmp-supabase-raw-audit";
const GITHUB_ISSUER = "https://token.actions.githubusercontent.com";
const GITHUB_JWKS = createRemoteJWKSet(
  new URL("https://token.actions.githubusercontent.com/.well-known/jwks"),
);
const MAX_REQUEST_BYTES = 50_000;
const DOWNLOAD_CONCURRENCY = 10;

type AuditObject = {
  path: string;
  kind: "manifest" | "raw";
  sha256: string;
  size_bytes: number;
  manifest_json?: Record<string, unknown> | null;
  manifest_parse_error?: boolean;
};

async function sha256Hex(bytes: Uint8Array): Promise<string> {
  const digestInput = bytes.buffer.slice(
    bytes.byteOffset,
    bytes.byteOffset + bytes.byteLength,
  ) as ArrayBuffer;
  const digest = await crypto.subtle.digest("SHA-256", digestInput);
  return [...new Uint8Array(digest)]
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

function parseManifest(bytes: Uint8Array): Record<string, unknown> | null {
  try {
    const parsed = JSON.parse(new TextDecoder().decode(bytes));
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      return parsed as Record<string, unknown>;
    }
  } catch {
    // Final verifier reports malformed manifest JSON as provenance failure.
  }
  return null;
}

async function authenticate(req: Request): Promise<void> {
  const auth = req.headers.get("authorization") ?? "";
  if (!auth.startsWith("Bearer ")) {
    throw new Error("missing OIDC token");
  }
  const token = auth.slice("Bearer ".length);
  const { payload } = await jwtVerify(token, GITHUB_JWKS, {
    issuer: GITHUB_ISSUER,
    audience: AUDIENCE,
  });
  assertTrustedGithubAuditClaims(payload as Record<string, unknown>);
}

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") {
    return Response.json({ error: "method_not_allowed" }, { status: 405 });
  }

  try {
    await authenticate(req);
  } catch (error) {
    console.error(error);
    return Response.json({ error: "unauthorized" }, { status: 401 });
  }

  let paths: string[];
  try {
    const body = new Uint8Array(await req.arrayBuffer());
    if (body.length === 0 || body.length > MAX_REQUEST_BYTES) {
      return Response.json({ error: "invalid_body_size" }, { status: 400 });
    }
    paths = validateAuditRequest(
      JSON.parse(new TextDecoder().decode(body)) as unknown,
    );
  } catch (error) {
    console.error(error);
    return Response.json({ error: "invalid_audit_request" }, { status: 400 });
  }

  try {
    const secretKeys = JSON.parse(
      Deno.env.get("SUPABASE_SECRET_KEYS") ?? "{}",
    );
    const secretKey = secretKeys.default;
    if (!secretKey) {
      throw new Error("missing Supabase secret key");
    }
    const supabase = createClient(Deno.env.get("SUPABASE_URL")!, secretKey);

    const inspectObject = async (path: string): Promise<AuditObject> => {
      const { data, error } = await supabase.storage
        .from(BUCKET)
        .download(path, {}, { cache: "no-store" });
      if (error || !data) {
        throw new Error(`storage download failed for ${path}`);
      }

      const bytes = new Uint8Array(await data.arrayBuffer());
      const item: AuditObject = {
        path,
        kind: path.endsWith(".json") ? "manifest" : "raw",
        sha256: await sha256Hex(bytes),
        size_bytes: bytes.length,
      };
      if (item.kind === "manifest") {
        const manifest = parseManifest(bytes);
        item.manifest_json = manifest;
        item.manifest_parse_error = manifest === null;
      }
      return item;
    };

    const objects: AuditObject[] = [];
    for (let offset = 0; offset < paths.length; offset += DOWNLOAD_CONCURRENCY) {
      const batch = paths.slice(offset, offset + DOWNLOAD_CONCURRENCY);
      objects.push(...await Promise.all(batch.map(inspectObject)));
    }

    return Response.json({
      status: "audited",
      count: objects.length,
      objects,
    });
  } catch (error) {
    console.error(error);
    return Response.json({ error: "storage_audit_failed" }, { status: 502 });
  }
});
