# Architecture

## Purpose and scope

This document defines the production target for a provenance-first research assistant for
Microsoft Word Desktop on Windows and macOS. `INVARIANTS.md` is normative.

“Local-only” applies to application-data processing and transmission performed by this
add-in and its local companion. The product has no hosted application infrastructure. Microsoft Word
can independently synchronize a document through OneDrive or SharePoint. Word can also
use Microsoft 365 connected experiences. The add-in cannot prevent or characterize those
host-controlled transmissions. Office.js loads from Microsoft's production content delivery network (CDN) and
must never receive an application research payload. Microsoft documents
[Word AutoSave](https://support.microsoft.com/en-us/onedrive/turn-on-autosave-in-microsoft-365-apps)
for files in OneDrive and SharePoint. Microsoft also documents
[content processing by connected experiences](https://learn.microsoft.com/en-us/microsoft-365-apps/privacy/connected-experiences-content).

## Deployment decision and open production gate

The selected v1 candidate is **managed organizational deployment**:

1. A Microsoft 365 administrator deploys the Extensible Markup Language (XML) manifest through the approved organizational route.
2. Device management deploys a signed platform package for the per-user companion.
3. The manifest points its task pane URL at the installer-owned HTTPS loopback origin.

Microsoft documents Integrated Apps and app catalogs as supported deployment routes.
Microsoft provides these deployment sources:

- [Runtime and catalog requirements](https://learn.microsoft.com/en-us/office/dev/add-ins/concepts/requirements-for-running-office-add-ins)
- [Production publication options](https://learn.microsoft.com/en-us/office/dev/add-ins/publish/publish)
- [Centralized Deployment](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-deployment-of-add-ins?view=o365-worldwide)

Sideloading is limited to development and testing, not the v1 production plan
([Microsoft sideloading guidance](https://learn.microsoft.com/en-us/office/dev/add-ins/testing/sideload-office-add-ins-for-testing)).

Official documentation does not establish that an administratively deployed manifest
can reliably use a per-device HTTPS loopback source on both Word Desktop webviews. This
combination is not a production guarantee. The conditional Phase 1 gate permits
platform-neutral Phase 2 work after the macOS host, hostile-browser, and Windows
noninteractive checks pass. Real Windows Word Desktop remains a mandatory pre-release
test. This route also assumes an eligible managed Microsoft 365 organization. Personal
or unmanaged distribution is outside v1 unless the product selects a separately
supported path.

The XML manifest cannot restrict an add-in by operating system. When task pane assets
load, they check the runtime platform and requirement set. They show a nonfunctional
unsupported-host screen on Word for the web, mobile, or non-Word hosts. A device without
the local companion cannot load those local assets. The failed origin connection stops
the load. Phase 1 must document the actual Office error. It must not promise a custom
screen that cannot load. Microsoft explicitly requires runtime platform
checks for this case
([requirement configuration](https://learn.microsoft.com/en-us/office/dev/add-ins/develop/understand-requirement-configuration)).

## System boundary

In this document, artificial intelligence (AI) means the two optional Microsoft advisory operations.

```text
[ Microsoft Word Desktop ]
  [ Task pane: React + TypeScript + Office.js ]
             |
             | trusted same-origin HTTPS loopback /api/v1
             v
[ Local companion: FastAPI ]
  session guard, use cases, OpenAPI, static task pane assets, job supervision
       |                    |                    |
       v                    v                    v
[ SQLite ]        [ Local content store ]  [ Local workers ]
 authoritative      PDFs, previews, index    extraction, OCR, embeddings
 metadata/review                               and queued AI operations
                                                   |
                                                   | disclosed, one-use consent only
                                                   v
                                         [ MicrosoftAiGateway ]
                                                   |
                                                   v
                    [ Azure OpenAI Responses API in Microsoft Foundry ]
```

`MicrosoftAiGateway` is the only component permitted to send application research data off-device. Analysis and
Research remain optional. Every local workflow works without Azure configuration.

## Process ownership

### Word task pane

The task pane owns presentation and Word mutation. It renders locally served page
previews, captures explicit review confirmation and decisions, displays the exact AI
disclosure preview, and inserts immutable artifact snapshots.

It does not parse PDFs, access the filesystem, hold credentials, call Azure directly, or
infer durable state from React. Browser storage is nonauthoritative and contains no
evidence, secrets, or paths.

### Local companion

The companion owns static assets, session enforcement, and application programming interface (API) coordination.
It also owns OpenAPI publication, SQLite transactions, content-store paths, durable jobs,
and the AI consent state machine. FastAPI's deterministic OpenAPI 3.1 document is the loopback contract.
The generator produces the TypeScript types and client from this contract.

### Local workers

Workers own Portable Document Format (PDF) validation, hashing, and versioned extraction.
They own optical character recognition (OCR), page rendering, structure analysis, and local indexing.
They also own deterministic suggestion rules and consented AI operation execution. V1 has
no local generative suggestion model.

Jobs and checkpoints are persisted in SQLite. A crashed worker can be replaced without
losing queued work. V1 uses no remote queue, Redis, or cloud worker.

### Authoritative local storage

SQLite is authoritative for project, paper, job, extraction, suggestion, inspection, and
decision records. It also owns synthesis, gap, AI, artifact, and insertion records.

The content store holds PDF bytes by SHA-256, rendered pages, the packaged local index,
and immutable artifact payloads beneath the per-user application-data directory.
Platform adapters resolve paths. Temporary work uses an operating-system-created private directory.
Export, backup, restore, and complete project deletion cover both stores.

Suggestions, inspections, decisions, claim revisions, and AI records are append-only
while a project exists. Complete user-requested project deletion can purge that project's
records and content, including its audit history, after confirmation.

## Local embedding decision

V1 uses `sentence-transformers/all-MiniLM-L6-v2` solely to create local embeddings. The
Phase 2 package must include an offline Open Neural Network Exchange (ONNX) artifact and tokenizer.
It must include an approved license record, upstream revision, and SHA-256 digests. Import/indexing cannot start until
those exact artifacts are pinned and verified. Runtime download and remote embedding APIs
are forbidden. V1 packages no local generative model.

## Loopback trust model

The stable origin is `https://localhost:4179`. Phase 1.5 rejected the earlier
`word-researcher.localhost` candidate because normal macOS and Node resolution returned
`EAI_NONAME`. A direct Server Name Indication (SNI) connection could not repair that defect. The selected hostname
resolves only to operating-system loopback addresses without installer-owned mappings.
Phase 1 must still prove the exact origin in real WebView2 and WKWebView hosts. A hostname
or port change invalidates the evidence.

The installer must complete these actions:

- Generate a unique local root certificate and server certificate for each installation.
- Use no shared certificate or private key.
- Constrain the leaf subject alternative name (SAN) to `DNS:localhost`.
- Use no wildcard or external name.
- Bind listeners only to `127.0.0.1` and, if proved, `::1`.
- Protect private keys with operating-system facilities.
- Limit access-control lists (ACLs) to the companion and installer.
- Reserve port `4179`.
- If an unexpected process owns the port, fail closed.
- Do not fall back to another origin.
- Support expiry monitoring, renewal, atomic rotation, rollback, revocation, repair, and uninstall cleanup.
- Remove leaf and root trust and keys during uninstall.

The companion must enforce these controls:

- Reject a `Host` value that does not match the exact origin.
- Reject an unexpected `Origin` value.
- Classify each bootstrap request before session creation.
- Accept an absent `Origin` only on the bootstrap route.
- Require the exact verified embedded-host profile for that exception.
- Enforce the verified `Sec-Fetch-Site`, mode, and destination tuple.
- Use a short-lived `Secure`, `HttpOnly`, `SameSite=Strict` session cookie.
- Require a separate session-bound cross-site request forgery (CSRF) token for every mutation.
- Rotate the session on startup and reconnection.
- Apply restrictive cross-origin resource sharing (CORS), content security policy (CSP), and cache headers.
- Reject path traversal and symbolic-link escape.
- Do not expose a per-install secret or certificate private key to task pane JavaScript.

The bootstrap authorization model is a verified embedded-host profile. The companion
accepts an exact `Origin` only after all other bootstrap controls pass. The companion
accepts a missing `Origin` only when every verified macOS Word request property matches.
The accepted properties are exact Host, loopback peer, HTTPS scheme, method, path, media
type, and Fetch Metadata. A missing field does not match an expected value.

This model protects the browser-origin boundary. It protects against remote network
clients, ordinary foreign webpages, cross-site request forgery, and invalid local
sessions. It does not cryptographically authenticate Word as a client. The local
operating-system user account is the v1 trust boundary.

A same-user native process can forge the complete local request context. A malicious
browser extension or compromised user profile can also imitate the task pane. These
threats are outside the v1 browser-origin boundary. The product makes no Word-attestation,
same-user malware-resistance, perfect-isolation, or unbypassable-authorization claim.

The task pane receives only short-lived bootstrap and session-bound CSRF material. The
manifest and task pane contain no durable installation secret. The design prioritizes
usable offline operation and ordinary web-origin protection over Word attestation.

Microsoft documents WebView2 on current Windows Office and WKWebView on Mac Office
([Office add-in browsers](https://learn.microsoft.com/en-us/office/dev/add-ins/concepts/browsers-used-by-office-web-add-ins)). Mocks are insufficient evidence.

## Loopback API responsibilities

The following paths fix ownership. OpenAPI fixes exact payload spelling:

- `GET /api/v1/health` reports companion, schema, database, worker, certificate, and
  embedding-package readiness.
- `POST /api/v1/projects` creates a local project.
- `POST /api/v1/projects/{projectId}/papers` stores and enqueues an import.
- This route returns `202 Accepted` and requires `Idempotency-Key`.
- `GET /api/v1/jobs/{jobId}`, `POST .../cancel`, and `POST .../retry` expose durable job
  progress and explicit transitions.
- `GET /api/v1/papers/{paperId}/result` returns the extraction projection.
- `GET /api/v1/papers/{paperId}/pages/{pageIndex}/preview` streams one local page.
- `GET /api/v1/projects/{projectId}/suggestions` returns immutable suggestions.
- `POST /api/v1/suggestions/{suggestionId}/review-inspections` confirms presentation of
  one exact source span in one review session.
- `POST /api/v1/suggestions/{suggestionId}/review-decisions` appends an ordered human
  decision.
- `POST /api/v1/projects/{projectId}/ai/analysis/previews` prepares an Analysis payload.
- `POST /api/v1/projects/{projectId}/ai/research/previews` prepares a Research payload.
- `POST /api/v1/ai-operations/{operationId}/consents` records one-use consent for the
  unchanged digest and execution profile.
- `POST /api/v1/ai-operations/{operationId}/execute` consumes consent and enqueues exactly
  one remote attempt.
- `GET /api/v1/ai-operations/{operationId}` returns the local operation projection.
- If execution is incomplete, `POST /api/v1/ai-operations/{operationId}/cancel` records cancellation.
- Remote cancellation is best-effort.
- The companion must report the remote cancellation result accurately.
- Synthesis, comparison, gap-test, artifact-snapshot, and insertion routes use the typed
  entities in `SYNTHESIS_DOMAIN_MODEL.md`.

A replay of an import idempotency key returns the original identifiers only when the
project, PDF bytes, and request parameters are identical. The same key with different
bytes or parameters returns `409 Conflict`. Mutations are locally authorized and audited.

## Microsoft AI production API

The exact external service is **Azure OpenAI in Microsoft Foundry, Responses API v1**:

```text
POST https://{resource-name}.openai.azure.com/openai/v1/responses?api-version=v1
```

This is the stable `v1` API. It is not a consumer Copilot API or a preview endpoint.
Microsoft defines this interface in the
[Responses REST reference](https://learn.microsoft.com/en-us/rest/api/microsoft-foundry/azureopenai/responses).
The user or organization must separately provision an Azure subscription, Azure OpenAI
resource, quota, billing, and deployments. The v1 baseline uses an API key from the
operating-system credential store. Microsoft Entra bearer authentication is a supported
future alternative. It requires a separate local sign-in and token-lifecycle design.

The selected model profile is `gpt-5`, model version `2025-08-07`, with separate local
deployment names for Analysis and Research. Release configuration pins the Azure resource
host, deployment name, expected base model/version, region/deployment type, and capability
probe result. A model retirement or deployment change invalidates the profile and requires
new verification. Silent routing is forbidden. Microsoft lists that version as generally available (GA) in its
[model retirement schedule](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirement-schedule).
Microsoft's structured-output support list explicitly includes this model/version
([structured outputs](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs)).

Analysis sends `store: false`, no tools, selected text/excerpts only, and a strict JSON
Schema in `text.format`. Research sends `store: false`, the approved query and optional
selected context, exactly `tools: [{"type":"web_search"}]`, and its strict result schema.
Microsoft documents `web_search` as the supported Responses API tool. The older
`web_search_preview` form is not selected
([web search guidance](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/web-search)).
Deep Research is excluded because its long-running/background behavior conflicts with the
v1 bounded, single-request, nonpersistent contract.

## Remote-processing contract

Every operation follows this state machine:

```text
prepared -> consented -> running -> succeeded
    |           |          |-----> failed
    |           |          |-----> cancelled
    |           |          |-----> unavailable
    |           |---------> cancelled
    |---------------------> cancelled
```

Preparation creates operation-specific request data, a local field-by-field disclosure,
and the exact HTTP body using RFC 8785 JavaScript Object Notation (JSON) canonicalization. The digest is
`sha256(canonicalRequestBytes)`. The preview displays the exact canonical payload. It also
explains the endpoint, model, tool, disclosed fields, bounds, cost basis, and retention.
It explains external processing and the applicable Research geography warning.

Consent is one-use and bound to operation identifier and type, payload digest, exact endpoint, model
deployment/base version, tool selection, disclosure version, and expiration. Execute
recreates the bytes and refuses any mismatch. The gateway sends those exact bytes once.
A timeout or ambiguous failure is `failed`. The gateway never retries it automatically.
Trying again requires a new preview, digest, and consent.

The HTTP adapter allows only the configured exact
`{resource-name}.openai.azure.com` resource host. It rejects redirects and disables
environment-proxy inheritance. It uses verified TLS. It enforces operation-specific
input, output-token, response-byte, and timeout limits. It sends no
paths, credentials in content, raw PDFs, database/index data, unrelated findings, or
undisclosed Word content. It validates HTTP shape, output item types, tool use, citations,
and the strict local JSON Schema before recording `succeeded`.

Both operations set `store: false`. They prohibit `previous_response_id`, conversations,
remote files, vector stores, file search, Assistants, batches, and stored responses. They
also prohibit background mode, context management, and prompt-cache controls. They prohibit
encrypted-reasoning carryover, code interpreter, Model Context Protocol (MCP), and other caller-managed remote state. Microsoft says Responses are
otherwise retained for 30 days and describes abuse-monitoring review of flagged prompts
and completions. The product therefore says **nonpersistent Responses request**, never
“zero retention.” These Microsoft sources define the applicable behavior:

- [Responses data behavior](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/responses)
- [Privacy and abuse monitoring](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy)

Research has a separate consent screen. Microsoft states that Grounding with Bing Search
incurs tool costs. Microsoft states that its Data Protection Addendum does not cover this
data. Microsoft also states that processing can cross the selected compliance or
geographic boundary. Those facts appear before every
Research consent. Research results are local `ResearchDiscovery` records. A cited source
must be imported and reviewed through normal provenance before it can support evidence.

## Paper job lifecycle

`POST /papers` atomically creates the paper record and runnable local job:

```text
queued -> running -> succeeded
          |    |
          |    -> failed -> queued (explicit retry attempt)
          -> cancelling -> cancelled
```

Failure records contain stable safe codes, stage, attempt, and retry eligibility. There is
no second parse command and no hidden retry.

## Office.js boundaries

Task pane HyperText Markup Language (HTML) loads the production Office.js script in
`<head>`. The required script URL is
`https://appsforoffice.microsoft.com/lib/1/hosted/office.js`. This follows Microsoft's
[Office.js guidance](https://learn.microsoft.com/en-us/office/dev/add-ins/develop/understand-the-javascript-api-for-office).
`WordApi 1.3` is the stable baseline. Newer stable members require runtime capability
checks ([requirement-set guidance](https://learn.microsoft.com/en-us/office/dev/add-ins/develop/office-versions-and-requirement-sets)).

Word application-object mutations execute inside `Word.run()` and finish only after
`context.sync()` succeeds. Commands are batched outside loops. Document settings use the
Office Common API `settings.set()` and are durable only after a successful `saveAsync()`
callback, outside `Word.run()`. An insertion record is appended after Word sync succeeds
and is reconciled by content-control tag plus idempotency key.
