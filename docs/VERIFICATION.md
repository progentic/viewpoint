# Verification strategy

## Evidence standard

Verification is layered. Pure domain tests establish rules. Adapter and contract tests
establish mechanics. Signed-package tests establish installation behavior. Real supported
Word Desktop tests establish host feasibility. Mocks cannot prove deployment, local Transport Layer Security (TLS),
cookies, Fetch Metadata, Office content delivery network (CDN) loading, or WebView behavior.

Every release evidence bundle records the platform and component versions. It records
certificate, contract, dependency, model, and Azure profile identifiers. It also records
Coordinated Universal Time (UTC), the test result, and redacted logs. No evidence
text, prompt, application programming interface (API) key, local path, or document content appears in logs.

Use one of these labels for every test result:

- Observed
- Verified
- Inferred
- Assumed
- Not tested
- Blocked
- Failed
- Passed
- Passed with limitations

An observation records the measured behavior. An inference records only the bounded
conclusion that the observation supports.

## 1. Architecture and dependency boundaries

Static rules fail when:

- Domain modules import FastAPI, SQLite, filesystem, Portable Document Format (PDF), optical character recognition (OCR), or Open Neural Network Exchange (ONNX)
- Domain modules import Office.js, HTTP, or a Microsoft software development kit (SDK)
- Task pane code imports Node APIs, credentials, Azure SDKs, bundled Office.js, or a general-purpose external HTTP client
- A general-purpose HTTP client exists outside `MicrosoftAiGateway` and approved platform plumbing
- Policy coordinators contain raw serialization, Structured Query Language (SQL), path, HTTP, Office, or hashing mechanics
- Hand-maintained TypeScript mirrors duplicate OpenAPI types
- An ambiguous model label or legacy validation-only adapter name appears in production sources

Review functions over 20 lines and modules over 400 lines as prompts, not automatic
failures. Functions that coordinate and implement lower-level mechanics fail review under
the Single Level of Abstraction rule.

## 2. Phase 1 production-feasibility matrix

Test on current supported, organization-managed Word Desktop installations:

| Scenario | Windows | macOS | Required evidence |
| :--- | :---: | :---: | :--- |
| Admin-deployed Extensible Markup Language (XML) manifest appears | Yes | Yes | Admin record and Word catalog capture |
| Signed local companion installs/starts | Yes | Yes | Package/install/startup logs |
| Loopback task pane loads | WebView2 | WKWebView | Origin, webview, Office build |
| `Office.onReady()` and `WordApi 1.3` | Yes | Yes | Runtime capability result |
| Session + cross-site request forgery (CSRF) bootstrap | Yes | Yes | Cookie/Fetch Metadata matrix |
| `/health` generated-client round trip | Yes | Yes | Request/result and OpenAPI digest |
| Web/mobile runtime rejection | Yes | Yes | Screen if assets load. Fail-closed load evidence otherwise |
| Certificate rotation/rollback/repair | Yes | Yes | Before/after fingerprints |
| Uninstall trust/startup cleanup | Yes | Yes | Operating-system trust and process inspection |

Also prove that a development sideload can support engineering work. Label that evidence
“development only.” The phase fails if the production candidate needs an insecure or
development-only exception. Examples include warning bypass, shared trust, origin
changes, JavaScript secrets, and manual certificate acceptance.

Phase 2 platform-neutral work can start after the conditional Phase 1 gate passes. Real
Windows Word Desktop remains mandatory before Windows release support. Architecture and
product owners must select a supported alternative if the real Windows host fails.

## 3. Loopback TLS and request security

Package/integration tests prove:

- Each clean install creates different root and leaf keys and fingerprints
- The leaf subject alternative name contains only `localhost`, without wildcard or external names
- Keys have least-privilege access-control lists and the task pane process cannot export them
- Only the selected loopback addresses listen
- If another process owns port `4179`, companion startup fails closed
- The hostname, port, and certificate origin remain stable across restart and repair
- Renewal is atomic and rollback restores the prior valid pair
- The companion refuses revoked material
- Uninstall removes trust, keys, and startup state
- Reject a `Host` mismatch and an absent or invalid `Origin` where required
- Reject disallowed Fetch Metadata and cross-site requests
- Reject stale or missing sessions, missing or wrong CSRF values, replay, and expiry before a use case
- The cookie always has these attributes: `Secure; HttpOnly; SameSite=Strict`
- The cross-site request forgery (CSRF) token is distinct and session-bound
- Cross-origin resource sharing is exact-origin
- The content security policy disallows unexpected sources
- API and evidence responses are non-cacheable
- No durable per-install secret appears in HyperText Markup Language (HTML), JavaScript, source maps, or browser storage
- No durable secret appears in the manifest, bootstrap JavaScript Object Notation (JSON), or API responses

Record actual initial-navigation and fetch headers for WebView2 and WKWebView. The guard
policy must match only proved behavior and must not weaken ordinary-browser attack tests.

Run these bootstrap classification checks:

- Accept an exact `Origin` with all remaining controls.
- Reject an unexpected `Origin`.
- Accept a missing `Origin` with the verified embedded-host profile.
- Reject a missing `Origin` with incorrect Fetch Metadata.
- Reject an ordinary browser request with a missing `Origin`.
- Reject an incorrect Host.
- Reject a non-loopback peer.
- Reject an incorrect method.
- Reject an incorrect content type.
- Reject replayed bootstrap material.
- Reject a missing session.
- Reject a missing CSRF token.
- Reject an invalid CSRF token.

Run these hostile-browser checks:

- Attempt a foreign-webpage bootstrap.
- Attempt a cross-site form submission.
- Attempt a cross-site fetch.
- Attempt a cross-origin preflight.
- Attempt a simple browser navigation to the bootstrap route.
- Attempt a missing-Origin request without the complete profile.

Run these lifecycle checks:

- Restart Word and establish a new session.
- Restart the companion and reconnect.
- Run repair two times.
- Uninstall and confirm cleanup.
- Occupy port `4179` and confirm fail-closed startup.

These tests do not require resistance to an arbitrary same-user native client. Such a
client can forge raw Hypertext Transfer Protocol (HTTP) headers and is outside the v1
browser-origin boundary.

## 4. Local-only and path controls

Run the companion/domain local suite with network denied. Imports, extraction, OCR,
embeddings, review, synthesis, gaps, artifacts, and export remain usable without Azure.
Real Word integration permits the required Office.js production-CDN fetch but denies
application research data on that request. Capture socket and Domain Name System (DNS)
attempts. Fail the test if application research data leaves through an unapproved route
or host.

Verify:

- Runtime model downloads, remote embeddings, telemetry, crash uploads, update checks, cloud stores, and hidden external calls do not occur
- Office.js is requested only from Microsoft's production CDN
- No research payload is attached to the Office.js uniform resource locator (URL), headers, or body
- Domain records contain opaque IDs and never absolute paths
- Reject traversal and encoded traversal
- Reject symbolic-link or junction escape and case-folding surprises
- Reject hardlink attacks, oversized files, and unsafe archives
- Export and restore preserve hashes and relationships
- Complete project deletion purges
  SQLite plus unreferenced content only after explicit confirmation.

Word's own Microsoft 365 traffic is outside the add-in egress assertion. Evidence must not
attribute that traffic to the add-in or claim that the add-in controls it.

## 5. OpenAPI and generated client

Run these contract checks:

- Generate OpenAPI 3.1 twice from a clean tree and compare byte-for-byte.
- Generate TypeScript types/client, regenerate, and fail on a dirty diff.
- Run positive/negative round trips for every route and closed enum.
- Verify unknown properties and over-bound payloads are rejected.
- Prove one generated-client `/health` call from each real Phase 1 task pane.
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

- Repeated identical text at different offsets
- Emoji represented by surrogate pairs in JavaScript
- Combining-character sequences and canonically similar but byte-different text
- Extracted ligature characters and expanded glyph text
- OCR output and an OCR failure
- Zero-based `pageIndex` that differs from printed `pageLabel`
- Empty spans, boundary spans, and multi-byte UTF-8
- The same PDF through two parser versions with distinct immutable extraction versions

Prove no normalization occurs after checksum/offset generation. Demonstrate that substring
search and JavaScript `String.slice()` fail at least one fixture, while
`sliceByUnicodeCodePoint` selects the exact span. Parser upgrades never silently retarget
old suggestions or inspections.

## 8. Review authority and ordering

Run these review-authority checks:

- Reject acceptance without `ReviewInspection` for every used span.
- Reject an inspection from another suggestion, span, extraction version, checksum, or
  review session, or with a different rendered-page/presentation digest.
- Verify the page and exact version are presented before explicit confirmation can append
  the single-item inspection.
- Verify that inspection proves only presentation and confirmation.
- Reject a dwell-time, focus, or attention inference during acceptance.
- Reject bulk decisions and artificial intelligence (AI) or local-worker attempts to write review state.
- Append sequence 1 without `supersedesDecisionId`.
- Require each later sequence to point to the current head.
- Race two decisions against one head: one succeeds and one receives `409 Conflict`.
- Preserve immutable original text and record edits only as `reviewedText`.
- Prove that item deletion cannot erase the audit trail.
- Prove that confirmed whole-project deletion can purge the audit trail.

## 9. Synthesis, gaps, and embeddings

Run these synthesis and gap checks:

- Reject approval of a `SynthesisClaimRevision` with zero or one distinct `paperId`, even
  if it has multiple findings.
- Accept only two-or-more-paper claims with valid typed `EvidenceLink` records.
- Keep one-paper boundary observations as `StudyFindingRevision`.
- Trace every approved comparison cell to accepted finding revisions.
- Freeze every eligible/ineligible/failed paper revision in a `CorpusSnapshot`.
- Permit successful gap search to reach only `corpusSearched`.
- Reject worker or AI attempts to substantiate or reject the gap.
- Verify corpus-bounded wording in the user interface (UI) and artifacts.
- Verify the packaged `all-MiniLM-L6-v2` model, tokenizer, runtime, license, revision, and SHA-256 before indexing.
- Deny runtime download and all embedding network calls.
- Scan packages/configuration for a local generative model and fail v1 if one is present or
  claimed.

## 10. AI contract tests common to both operations

Use a local fake transport for exhaustive tests and a separately provisioned Azure test
resource for redacted capability evidence. The fake must not relax production host rules
outside the test composition root.

For both `analysis` and `research`:

- Render the full canonical request bytes.
- Verify that the user-interface bytes equal the transport bytes.
- Verify RFC 8785 deterministic serialization and `sha256(canonicalRequestBytes)`.
- Bind consent to all disclosed operation, payload, endpoint, model, tool, notice, and expiry fields.
- Change each bound field independently and prove that execution is refused.
- Consume consent atomically once.
- Reject replay and concurrent execution.
- Allow only the exact configured `{resource-name}.openai.azure.com` resource host.
- Require verified TLS and the `/openai/v1/responses?api-version=v1` path.
- Reject redirects, DNS mismatches, host mismatches, and invalid certificates.
- Reject unexpected output types, truncated JSON, unknown properties, and schema violations.
- Reject oversized input, oversized output, token overruns, and timeouts.
- Set HTTP environment-proxy inheritance to false.
- Prove that hostile `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` values cannot redirect traffic.
- Set automatic retries to zero.
- Prove that a timeout or 5xx response creates one recorded attempt.
- Require `store: false`.
- Reject `previous_response_id`, conversations, files, vector stores, and file search.
- Reject Assistants, batches, stored responses, background mode, and code interpreter.
- Reject Model Context Protocol (MCP), context management, prompt-cache controls, and encrypted-reasoning carryover.
- Reject every undeclared tool or remote state feature.
- Verify that local audit records contain disclosed fields, digests, status, safe reason, validated result, and usage.
- Verify that local audit records contain no credential.
- Exercise `prepared`, `consented`, `running`, `succeeded`, `failed`, `cancelled`, and `unavailable`.
- Prove that local flows work when AI is unconfigured, offline, unauthorized, quota-limited, deployment-retired, tool-disabled, or unavailable.

Cancellation before execution consumes no remote attempt. Cancellation after send is
best-effort. If remote completion cannot stop, the record must not deny processing of the
sent payload.

## 11. Analysis-specific AI tests

Run these Analysis checks:

- Permit only the selected instruction, text/excerpts, and displayed metadata.
- Reject raw PDF bytes, page images, paths, SQLite/index content, unrelated findings,
  credentials, or undisclosed Word content.
- Require zero tools and strict `analysis_result_v1` structured output.
- Show Analysis-specific selected fields, cost basis, external processing, `store: false`,
  possible abuse monitoring, and single-attempt notice before consent.
- Verify advice cannot append inspection/decision, approve claims/questions/comparisons,
  change gaps, create insertable artifacts by itself, or call Word.

## 12. Research-specific AI tests

Run these Research checks:

- Permit only the approved query and optional selected context.
- Require exactly `web_search`, a completed `web_search_call`, strict
  `research_result_v1`, valid citation annotations, and reconciled source URLs.
- Require a distinct Research consent even when identical context was approved for
  Analysis.
- Display the query, context, tool, cost notice, and external processing before consent.
- Display Microsoft's Data Protection Addendum (DPA) and geographic-boundary warning before consent.
- Reject `web_search_preview`, deep/background research, arbitrary tools, remote files,
  and location disclosure not present in preview.
- Persist outputs only as `ResearchDiscovery`.
- Reject use of a discovery URL, citation, or summary as evidence or an artifact source.
- Prove that only a newly imported and reviewed cited source can become accepted evidence.

## 13. Artifacts and Word transactions

Run these artifact and Word checks:

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
- Prove that document settings call `settings.set()`.
- Complete settings persistence after a successful `saveAsync()` callback outside `Word.run()`.
- Reject evidence, paths, credentials, or payload content in settings.

## 14. Office.js production checks

Run these Office.js checks:

- Inspect task pane HTML to require the production CDN script in `<head>`.
- Fail if Office.js is bundled or loaded from a preview/local substitute in production.
- Fail on preview type packages.
- Treat `WordApi 1.3` as baseline and require explicit runtime checks for every newer
  stable member.
- Run insertion, document-link, unsupported-host, restart, and reconnect smoke tests in
  real Word Desktop on the Windows/macOS support matrix.

## 15. Documentation consistency gate

Before each implementation phase, scan all eight planning documents for:

- Legacy validation-only adapter names or route names
- The old page checksum name
- Singular artifact-source language
- Ambiguous model labels or local-generative claims
- AI operations or statuses outside the closed vocabularies
- Production claims based only on sideloading or unproved loopback behavior
- A claim that `saveAsync()` runs inside `Word.run()`
- “Zero retention,” single-study synthesis exceptions, mutable snapshots, or discoveries treated as evidence

Any match is resolved before that phase's gate passes.
