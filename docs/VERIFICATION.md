# Verification strategy

## Evidence standard

Verification is layered. Pure domain tests establish rules; adapter/contract tests
establish mechanics; signed-package tests establish installation behavior; real supported
Word Desktop tests establish host feasibility. Mocks cannot prove deployment, local TLS,
cookies, Fetch Metadata, Office CDN loading, or WebView behavior.

Every release evidence bundle records OS/Office builds, webview version, manifest version,
companion/package version, certificate fingerprints, OpenAPI digest, dependency/model
digests, Azure profile identifiers, UTC time, test result, and redacted logs. No evidence
text, prompt, API key, local path, or document content appears in logs.

## 1. Architecture and dependency boundaries

Static rules fail when:

- domain modules import FastAPI, SQLite, filesystem, PDF/OCR/ONNX, Office.js, HTTP, or a
  Microsoft SDK;
- task-pane code imports Node APIs, credentials, Azure SDKs, Office.js as a bundle, or a
  general-purpose external HTTP client;
- a general-purpose HTTP client exists outside `MicrosoftAiGateway` and explicitly
  approved platform plumbing;
- policy coordinators contain raw serialization, SQL, path, HTTP, Office, or hashing
  mechanics;
- hand-maintained TypeScript mirrors duplicate OpenAPI types;
- an ambiguous model label or legacy validation-only adapter/route name appears in
  production sources.

Review functions over 20 lines and modules over 400 lines as prompts, not automatic
failures. Functions that coordinate and implement lower-level mechanics fail review under
the Single Level of Abstraction rule.

## 2. Phase 1 production-feasibility matrix

Test on current supported, organization-managed Word Desktop installations:

| Scenario | Windows | macOS | Required evidence |
| :--- | :---: | :---: | :--- |
| Admin-deployed XML manifest appears | Yes | Yes | Admin record and Word catalog capture |
| Signed companion installs/starts | Yes | Yes | Package/install/startup logs |
| Loopback task pane loads | WebView2 | WKWebView | Origin, webview, Office build |
| `Office.onReady()` and `WordApi 1.3` | Yes | Yes | Runtime capability result |
| Session + CSRF bootstrap | Yes | Yes | Cookie/Fetch Metadata matrix |
| `/health` generated-client round trip | Yes | Yes | Request/result and OpenAPI digest |
| Web/mobile runtime rejection | Yes | Yes | Screen if assets load; fail-closed load evidence otherwise |
| Certificate rotation/rollback/repair | Yes | Yes | Before/after fingerprints |
| Uninstall trust/startup cleanup | Yes | Yes | OS trust and process inspection |

Also prove a development sideload can support engineering work, but label that evidence
“development only.” The phase fails if the production candidate needs sideloading, browser
warning bypass, shared trust material, a changing origin, a JavaScript installation
secret, or manual certificate acceptance. No Phase 2 feature work starts after such a
failure; architecture/product owners must select a supported alternative or stop v1.

## 3. Loopback TLS and request security

Package/integration tests prove:

- each clean install creates different root/leaf keys and fingerprints;
- the leaf SAN contains only `word-researcher.localhost`, without wildcard/external names;
- keys have least-privilege ACLs and cannot be exported by the task-pane process;
- only the selected loopback addresses are listening and port `4179` fails closed on a
  conflicting owner;
- hostname, port, and certificate origin stay stable across restart and repair;
- renewal is atomic, rollback restores the prior valid pair, revoked material is refused,
  and uninstall removes trust/keys/startup state;
- `Host` mismatch, absent/invalid Origin where required, disallowed Fetch Metadata,
  cross-site requests, stale/missing session, missing/wrong CSRF, replay, and expired
  session all fail before a use case;
- the cookie is always `Secure; HttpOnly; SameSite=Strict`; the CSRF token is distinct and
  session-bound;
- CORS is exact-origin, CSP disallows unexpected sources, and API/evidence responses are
  non-cacheable;
- no durable per-install secret is present in HTML, JavaScript, source maps, browser
  storage, manifest, bootstrap JSON, or API responses.

Record actual initial-navigation and fetch headers for WebView2 and WKWebView. The guard
policy must match only proved behavior and must not weaken ordinary-browser attack tests.

## 4. Local-only and path controls

Run the companion/domain local suite with network denied. Imports, extraction, OCR,
embeddings, review, synthesis, gaps, artifacts, and export remain usable without Azure.
Real Word integration permits the required Office.js production-CDN fetch but denies
application research data on that request. Capture socket/DNS attempts and fail on
application-data egress outside a consented gateway test to the exact configured host.

Verify:

- runtime model downloads, remote embeddings, telemetry, crash uploads, update checks,
  cloud queues/stores, and hidden external calls do not occur;
- Office.js is requested only from Microsoft's production CDN and no research payload is
  attached to its URL, headers, or body;
- domain records contain opaque IDs and never absolute paths;
- traversal, encoded traversal, symlink/junction escape, case-folding surprises, hardlink
  attacks, oversized files, and unsafe archives fail closed;
- export/restore preserve hashes and relationships, and complete project deletion purges
  SQLite plus unreferenced content only after explicit confirmation.

Word's own OneDrive/SharePoint/connected-experience traffic is outside the add-in egress
assertion and is documented rather than falsely attributed to or controlled by the app.

## 5. OpenAPI and generated client

- Generate OpenAPI 3.1 twice from a clean tree and compare byte-for-byte.
- Generate TypeScript types/client, regenerate, and fail on a dirty diff.
- Run positive/negative round trips for every route and closed enum.
- Verify unknown properties and over-bound payloads are rejected.
- Prove a minimal real task-pane-generated-client `/health` call in both Phase 1 hosts.
- Confirm safe errors expose opaque IDs/codes but no paths, excerpts, prompts, SQL, or
  stack traces.

## 6. Imports, jobs, and persistence

Test valid, malformed, encrypted, image-only, mixed-text, oversized, and high-page-count
PDFs. Verify extraction/OCR/index stages persist checkpoints and do not block the API event
loop. Kill companion and worker at each checkpoint and prove deterministic recovery.

Idempotency cases:

| Replay | Expected result |
| :--- | :--- |
| Same project, key, PDF bytes, parameters | Original `paperId`/`jobId` |
| Same key, different PDF bytes | `409 Conflict` |
| Same key, different import parameters | `409 Conflict` |
| Explicit retry after retryable failure | New recorded attempt, same logical job |

Cancellation is cooperative and terminal when acknowledged. No failure, timeout, restart,
or polling action creates an undisclosed retry.

## 7. Provenance fixtures

For every fixture, validate the SHA-256 of raw UTF-8 page text and half-open Unicode
code-point slice. Include:

- repeated identical text at different offsets;
- emoji represented by surrogate pairs in JavaScript;
- combining-character sequences and canonically similar but byte-different text;
- extracted ligature characters versus expanded glyph text;
- OCR output and an OCR failure;
- zero-based `pageIndex` differing from printed `pageLabel`;
- empty/boundary spans and multi-byte UTF-8;
- the same PDF through two parser versions with distinct immutable extraction versions.

Prove no normalization occurs after checksum/offset generation. Demonstrate that substring
search and JavaScript `String.slice()` fail at least one fixture, while
`sliceByUnicodeCodePoint` selects the exact span. Parser upgrades never silently retarget
old suggestions or inspections.

## 8. Review authority and ordering

- Reject acceptance without `ReviewInspection` for every used span.
- Reject an inspection from another suggestion, span, extraction version, checksum, or
  review session, or with a different rendered-page/presentation digest.
- Verify the page and exact version are presented before explicit confirmation can append
  the single-item inspection.
- Verify inspection proves only presentation/confirmation; no dwell-time, focus, or
  attention inference affects acceptance.
- Reject bulk decisions and AI/local-worker attempts to write review state.
- Append sequence 1 without `supersedesDecisionId`; require each later sequence to point
  to the current head.
- Race two decisions against one head: one succeeds and one receives `409 Conflict`.
- Preserve immutable original text and record edits only as `reviewedText`.
- Prove item deletion cannot erase the audit trail; prove confirmed whole-project deletion
  can purge it.

## 9. Synthesis, gaps, and embeddings

- Reject approval of a `SynthesisClaimRevision` with zero or one distinct `paperId`, even
  if it has multiple findings.
- Accept only two-or-more-paper claims with valid typed `EvidenceLink` records.
- Keep one-paper boundary observations as `StudyFindingRevision`.
- Trace every approved comparison cell to accepted finding revisions.
- Freeze every eligible/ineligible/failed paper revision in a `CorpusSnapshot`.
- Permit successful gap search to reach only `corpusSearched`; reject worker/AI attempts
  to substantiate or reject it.
- Verify corpus-bounded wording in UI and artifacts.
- Verify the packaged `all-MiniLM-L6-v2` model/tokenizer/runtime license, revision, and
  SHA-256 before indexing; deny runtime download and all embedding network calls.
- Scan packages/configuration for a local generative model and fail v1 if one is present or
  claimed.

## 10. AI contract tests common to both operations

Use a local fake transport for exhaustive tests and a separately provisioned Azure test
resource for redacted capability evidence. The fake must not relax production host rules
outside the test composition root.

For both `analysis` and `research`:

- render the exact full canonical request bytes and verify the UI bytes equal transport
  bytes;
- verify RFC 8785 deterministic serialization and `sha256(canonicalRequestBytes)`;
- bind consent to operation/type, digest, exact endpoint, deployment/base model/version,
  tools, disclosure version, notices, and expiry;
- change each bound field independently and prove execution is refused;
- consume consent atomically once and reject replay/concurrent execution;
- allow only the exact configured `{resource-name}.openai.azure.com` resource host,
  verified TLS, and
  `/openai/v1/responses?api-version=v1` path;
- reject redirects, DNS/host mismatches, invalid certificates, unexpected output types,
  oversize input/output, token overruns, timeouts, truncated JSON, unknown properties, and
  schema violations;
- set HTTP environment-proxy inheritance false and prove hostile `HTTP_PROXY`,
  `HTTPS_PROXY`, and `NO_PROXY` values do not redirect traffic;
- set automatic retries to zero and prove a timeout/5xx creates one recorded attempt;
- require `store: false` and reject `previous_response_id`, conversations, files, vector
  stores, file search, Assistants, batches, stored responses, background mode, code
  interpreter, MCP, context management, prompt-cache controls, encrypted-reasoning
  carryover, and any undeclared tool/state;
- verify local audit records contain disclosed fields, digests, status, safe reason,
  validated result/usage, and no credential;
- exercise all statuses: `prepared`, `consented`, `running`, `succeeded`, `failed`,
  `cancelled`, and `unavailable`;
- prove all local flows still work when unconfigured, offline, unauthorized, quota-limited,
  deployment-retired, tool-disabled, or unavailable.

Cancellation before execution consumes no remote attempt. Cancellation after send is
best-effort: if remote completion cannot be stopped, the record must not falsely assert
that Microsoft did not process the already sent payload.

## 11. Analysis-specific AI tests

- Permit only the selected instruction, text/excerpts, and displayed metadata.
- Reject raw PDF bytes, page images, paths, SQLite/index content, unrelated findings,
  credentials, or undisclosed Word content.
- Require zero tools and strict `analysis_result_v1` structured output.
- Show Analysis-specific selected fields, cost basis, external processing, `store: false`,
  possible abuse monitoring, and single-attempt notice before consent.
- Verify advice cannot append inspection/decision, approve claims/questions/comparisons,
  change gaps, create insertable artifacts by itself, or call Word.

## 12. Research-specific AI tests

- Permit only the approved query and optional selected context.
- Require exactly `web_search`, a completed `web_search_call`, strict
  `research_result_v1`, valid citation annotations, and reconciled source URLs.
- Require a distinct Research consent even when identical context was approved for
  Analysis.
- Display the query, context, tool, token/tool cost notice, external processing, and
  Microsoft's DPA/geographic-boundary warning before consent.
- Reject `web_search_preview`, deep/background research, arbitrary tools, remote files,
  and location disclosure not present in preview.
- Persist outputs only as `ResearchDiscovery`; reject attempts to use a discovery URL,
  citation, or summary directly in a finding, evidence link, gap conclusion, or artifact.
- Prove that only a newly imported and reviewed cited source can become accepted evidence.

## 13. Artifacts and Word transactions

- Reject an empty, singular untyped, cross-project, unaccepted, or unapproved artifact
  source reference.
- Freeze nonempty typed `ArtifactSourceRevision[]` and verify payload digest.
- Derive staleness after source supersession without changing snapshot bytes or inserted
  content.
- Inspect Office command traces to prove one `Word.run()`, no `context.sync()` inside
  insertion loops, and insertion recording only after successful sync.
- Inject sync failure and prove no local insertion record is written.
- Inject failure after sync but before local record, then reconcile by content-control tag
  and idempotency key without duplicate insertion.
- Prove document settings call `settings.set()` and complete on successful `saveAsync()`
  callback outside `Word.run()`; reject evidence, paths, credentials, or payload content
  in settings.

## 14. Office.js production checks

- Inspect task-pane HTML to require the production CDN script in `<head>`.
- Fail if Office.js is bundled or loaded from a preview/local substitute in production.
- Fail on preview type packages.
- Treat `WordApi 1.3` as baseline and require explicit runtime checks for every newer
  stable member.
- Run insertion, document-link, unsupported-host, restart, and reconnect smoke tests in
  real Word Desktop on the Windows/macOS support matrix.

## 15. Documentation consistency gate

Before each implementation phase, scan all eight planning documents for:

- legacy validation-only adapter/route names, the old page checksum name, singular
  artifact-source language, ambiguous model labels, or local-generative claims;
- AI operations/statuses not in the closed vocabularies;
- production claims based only on sideloading or unproved loopback behavior;
- a claim that `saveAsync()` runs inside `Word.run()`;
- “zero retention,” single-study synthesis exceptions, mutable snapshots, or research
  discoveries treated as evidence.

Any match is resolved before that phase's gate passes.
