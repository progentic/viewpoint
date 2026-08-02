# Architecture

## Purpose and scope

This document defines the production target for a provenance-first research assistant for
Microsoft Word Desktop on Windows and macOS. `INVARIANTS.md` is normative.

“Local-only” applies to application-data processing and transmission performed by this
add-in and its companion. The product has no hosted application backend. Microsoft Word
can independently synchronize a document through OneDrive or SharePoint and can use
Microsoft 365 connected experiences; the add-in cannot prevent or characterize those
host-controlled transmissions. Office.js is loaded from Microsoft's production CDN and
must never receive an application research payload. Microsoft documents Word AutoSave for
files in OneDrive/SharePoint
([AutoSave support](https://support.microsoft.com/en-us/onedrive/turn-on-autosave-in-microsoft-365-apps))
and content processing by Microsoft 365 connected experiences
([connected experiences](https://learn.microsoft.com/en-us/microsoft-365-apps/privacy/connected-experiences-content)).

## Deployment decision and open production gate

The selected v1 candidate is **managed organizational deployment**:

1. A Microsoft 365 administrator deploys the XML add-in-only manifest through Integrated
   Apps/Centralized Deployment (or an approved organizational app catalog).
2. Device management deploys a separately signed Windows installer or macOS package for
   the per-user companion, certificate material, startup registration, repair, and
   uninstall.
3. The manifest points its task-pane URL at the installer-owned HTTPS loopback origin.

Microsoft documents Integrated Apps or an app catalog as supported ways to make an XML
task-pane add-in available, and distinguishes publication from development sideloading:
[runtime and catalog requirements](https://learn.microsoft.com/en-us/office/dev/add-ins/concepts/requirements-for-running-office-add-ins),
[production publication options](https://learn.microsoft.com/en-us/office/dev/add-ins/publish/publish), and
[Centralized Deployment](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-deployment-of-add-ins?view=o365-worldwide).
Sideloading is limited to development and testing, not the v1 production plan
([Microsoft sideloading guidance](https://learn.microsoft.com/en-us/office/dev/add-ins/testing/sideload-office-add-ins-for-testing)).

Official documentation does not establish that an administratively deployed manifest
may reliably use a per-device HTTPS loopback source on both Word Desktop webviews. This
combination is therefore a **Phase 1 hard feasibility gate**, not a production guarantee.
No feature implementation proceeds until real supported Windows and macOS Word Desktop
environments prove deployment, startup, trust, repair, and removal. This route also
assumes an eligible managed Microsoft 365 organization; personal/unmanaged distribution
is outside v1 unless a separately supported path is selected.

The XML manifest cannot restrict an add-in by operating system. When task-pane assets
load, they perform a runtime platform and requirement-set check and show a nonfunctional
unsupported-host screen on Word for the web, mobile, or non-Word hosts. A device without
the local companion cannot load those local assets and is rejected by the origin
connection failure; Phase 1 must document the actual Office error experience rather than
promise a custom screen that cannot load. Microsoft explicitly requires runtime platform
checks for this case
([requirement configuration](https://learn.microsoft.com/en-us/office/dev/add-ins/develop/understand-requirement-configuration)).

## System boundary

```text
[ Microsoft Word Desktop ]
  [ Task pane: React + TypeScript + Office.js ]
             |
             | trusted same-origin HTTPS loopback /api/v1
             v
[ Local companion: FastAPI ]
  session guard, use cases, OpenAPI, static task-pane assets, job supervision
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

Only `MicrosoftAiGateway` may send application research data off-device. Analysis and
Research remain optional; every local workflow works without Azure configuration.

## Process ownership

### Word task pane

The task pane owns presentation and Word mutation. It renders locally served page
previews, captures explicit review confirmation and decisions, displays the exact AI
disclosure preview, and inserts immutable artifact snapshots.

It does not parse PDFs, access the filesystem, hold credentials, call Azure directly, or
infer durable state from React. Browser storage is nonauthoritative and contains no
evidence, secrets, or paths.

### Local companion

The companion owns static assets, session enforcement, API coordination, OpenAPI
publication, SQLite transactions, content-store paths, durable jobs, and the AI consent
state machine. FastAPI's deterministic OpenAPI 3.1 document is the loopback contract;
TypeScript types and the client are generated from it.

### Local workers

Workers own PDF validation, hashing, versioned extraction, OCR, rendered page creation,
structure analysis, local embeddings/indexing, deterministic suggestion rules, and
execution of consented AI operations. V1 has no local generative suggestion model.

Jobs and checkpoints are persisted in SQLite. A crashed worker can be replaced without
losing queued work. V1 uses no remote queue, Redis, or cloud worker.

### Authoritative local storage

SQLite is authoritative for projects, papers, jobs, extraction versions, suggestions,
review inspections, review decisions, synthesis claims, corpus snapshots, gap tests, AI
disclosures/consents/results, artifact snapshots, and insertion records.

The content store holds PDF bytes by SHA-256, rendered pages, the packaged local index,
and immutable artifact payloads beneath the OS per-user application-data directory.
Platform adapters resolve paths. Temporary work uses an OS-created private directory.
Export, backup, restore, and complete project deletion cover both stores.

Suggestions, inspections, decisions, claim revisions, and AI records are append-only
while a project exists. Complete user-requested project deletion may purge that project's
records and content, including its audit history, after confirmation.

## Local embedding decision

V1 uses `sentence-transformers/all-MiniLM-L6-v2` solely to create local embeddings. The
Phase 2 package must include an offline ONNX artifact and tokenizer, an approved license
record, the upstream revision, and SHA-256 digests. Import/indexing cannot start until
those exact artifacts are pinned and verified. Runtime download and remote embedding APIs
are forbidden. V1 packages no local generative model.

## Loopback trust model

The proposed stable origin is `https://word-researcher.localhost:4179`. Phase 1 must prove
the exact origin in real WebView2 and WKWebView hosts; changing hostname or port invalidates
the evidence.

The installer must:

- generate a unique per-install local root and server certificate; use no shared
  certificate or private key;
- constrain the leaf SAN to `DNS:word-researcher.localhost`, with no wildcard or external
  name, and bind listeners only to `127.0.0.1` and, if proved, `::1`;
- protect private keys with OS facilities and ACLs limited to the companion/installer;
- reserve port `4179`, fail closed on an unexpected owner, and never fall back to another
  origin;
- support expiry monitoring, renewal, atomic rotation with rollback, compromise
  revocation, repair, and removal of leaf/root trust and keys on uninstall.

The companion must:

- reject any `Host` other than the exact origin and reject unexpected `Origin`;
- enforce observed Fetch Metadata (`Sec-Fetch-Site`, mode, and destination) according to
  the WebView2/WKWebView matrix proved in Phase 1;
- use a short-lived `Secure`, `HttpOnly`, `SameSite=Strict` session cookie and a separate,
  session-bound CSRF token for every mutation;
- rotate the session on startup/reconnect, apply restrictive CORS/CSP/cache headers, and
  reject path traversal and symlink escape;
- never expose a per-install secret or certificate private key to task-pane JavaScript.

An ordinary page load must not silently establish an authenticated API session. The exact
Word-to-companion bootstrap mechanism remains a Phase 1 spike: evidence must show how the
real webviews establish the HttpOnly session without placing a durable per-install secret
in JavaScript or the manifest. A short-lived CSRF token may be available to the task pane;
it is not the installation credential. Loopback is not production-ready until this works.

Microsoft documents WebView2 on current Windows Office and WKWebView on Mac Office
([Office add-in browsers](https://learn.microsoft.com/en-us/office/dev/add-ins/concepts/browsers-used-by-office-web-add-ins)); mocks are insufficient evidence.

## Loopback API responsibilities

The following paths fix ownership; OpenAPI fixes exact payload spelling:

- `GET /api/v1/health` reports companion, schema, database, worker, certificate, and
  embedding-package readiness.
- `POST /api/v1/projects` creates a local project.
- `POST /api/v1/projects/{projectId}/papers` stores and enqueues an import and returns
  `202 Accepted`; `Idempotency-Key` is required.
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
- `POST /api/v1/ai-operations/{operationId}/cancel` records cancellation if execution has
  not completed; remote cancellation is best-effort and never misreported.
- synthesis, comparison, gap-test, artifact-snapshot, and insertion routes use the typed
  entities in `SYNTHESIS_DOMAIN_MODEL.md`.

A replay of an import idempotency key returns the original identifiers only when the
project, PDF bytes, and request parameters are identical. The same key with different
bytes or parameters returns `409 Conflict`. Mutations are locally authorized and audited.

## Microsoft AI production API

The exact external service is **Azure OpenAI in Microsoft Foundry, Responses API v1**:

```text
POST https://{resource-name}.openai.azure.com/openai/v1/responses?api-version=v1
```

This is the stable `v1` API, not a consumer Copilot API and not a preview endpoint
([Microsoft REST reference](https://learn.microsoft.com/en-us/rest/api/microsoft-foundry/azureopenai/responses)).
The user or organization must separately provision an Azure subscription, Azure OpenAI
resource, quota, billing, and deployments. The v1 baseline uses an API key from the OS
credential store; Microsoft Entra bearer authentication is a supported future alternative
but requires its own local sign-in and token-lifecycle design.

The selected model profile is `gpt-5`, model version `2025-08-07`, with separate local
deployment names for Analysis and Research. Release configuration pins the Azure resource
host, deployment name, expected base model/version, region/deployment type, and capability
probe result. A model retirement or deployment change invalidates the profile and requires
new verification; silent routing is forbidden. Microsoft lists that version as GA in its
[model retirement schedule](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirement-schedule).
Microsoft's structured-output support list explicitly includes this model/version
([structured outputs](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs)).

Analysis sends `store: false`, no tools, selected text/excerpts only, and a strict JSON
Schema in `text.format`. Research sends `store: false`, the approved query and optional
selected context, exactly `tools: [{"type":"web_search"}]`, and its strict result schema.
Microsoft documents `web_search` as the supported Responses API tool; the older
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
and the exact HTTP body using RFC 8785 JSON canonicalization. The digest is
`sha256(canonicalRequestBytes)`. The preview displays the exact canonical payload and
separately explains the endpoint, deployment/base model, selected tool, disclosed fields,
bounds, estimated cost basis, retention/external-processing behavior, and applicable
Research geography/compliance warning.

Consent is one-use and bound to operation ID/type, payload digest, exact endpoint, model
deployment/base version, tool selection, disclosure version, and expiration. Execute
recreates the bytes and refuses any mismatch. The gateway sends those exact bytes once.
A timeout or ambiguous failure is `failed`; it is never retried automatically. Trying
again requires a new preview, digest, and consent.

The HTTP adapter allows only the configured exact
`{resource-name}.openai.azure.com` resource host,
rejects redirects, disables environment-proxy inheritance, uses verified TLS, and enforces
operation-specific input, output-token, response-byte, and timeout limits. It sends no
paths, credentials in content, raw PDFs, database/index data, unrelated findings, or
undisclosed Word content. It validates HTTP shape, output item types, tool use, citations,
and the strict local JSON Schema before recording `succeeded`.

Both operations set `store: false` and prohibit `previous_response_id`, conversations,
remote files, vector stores, file search, Assistants, batches, stored responses, background
mode, context management, prompt-cache controls, encrypted-reasoning carryover, code
interpreter, MCP, and any other caller-managed remote state. Microsoft says Responses are
otherwise retained for 30 days and describes abuse-monitoring review of flagged prompts
and completions. The product therefore says **nonpersistent Responses request**, never
“zero retention” ([Responses data behavior](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/responses),
[privacy and abuse monitoring](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy)).

Research has a separate consent screen. Microsoft states that Grounding with Bing Search
incurs tool costs, is not covered by the Microsoft Data Protection Addendum, and can move
data outside the selected compliance/geographic boundary. Those facts appear before every
Research consent. Research results are local `ResearchDiscovery` records; a cited source
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

Task-pane HTML loads `https://appsforoffice.microsoft.com/lib/1/hosted/office.js` in
`<head>` as required by Microsoft's
[Office.js guidance](https://learn.microsoft.com/en-us/office/dev/add-ins/develop/understand-the-javascript-api-for-office).
`WordApi 1.3` is the stable baseline; newer stable members require runtime capability
checks ([requirement-set guidance](https://learn.microsoft.com/en-us/office/dev/add-ins/develop/office-versions-and-requirement-sets)).

Word application-object mutations execute inside `Word.run()` and finish only after
`context.sync()` succeeds. Commands are batched outside loops. Document settings use the
Office Common API `settings.set()` and are durable only after a successful `saveAsync()`
callback, outside `Word.run()`. An insertion record is appended after Word sync succeeds
and is reconciled by content-control tag plus idempotency key.
