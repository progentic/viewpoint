# Invariants

These rules are normative. SQLite constraints, domain services, loopback guards, adapter
boundaries, packaging checks, and automated tests enforce them. A task pane check alone
never establishes an invariant. If another document conflicts with this file, the other
document must change.

## 1. Application research data is local by default

The add-in and local companion have no hosted application infrastructure, telemetry collector, remote database,
remote object store, cloud queue, or remote index. Application research data stays on the
device by default. This data includes Portable Document Format (PDF) files, text, pages,
and embeddings. It also includes indexes, SQLite, artifacts, and Word content. One
Microsoft artificial intelligence (AI) operation can send only the exact approved
payload.

This promise covers only transmissions performed by the add-in and companion. Word can
independently use OneDrive, SharePoint, AutoSave, or connected experiences. Office.js is a
required production content delivery network (CDN) dependency and carries no application research payload.

## 2. SQLite and the content store are authoritative

SQLite owns metadata, jobs, review state, AI audit records, synthesis state, snapshots,
and insertion records. The content store owns addressed local bytes. React state, browser
storage, Word settings, and worker memory are never authoritative.

Opaque content IDs, not absolute paths, cross domain boundaries. Export, backup, restore,
and deletion cover both authoritative stores.

## 3. Audit records are append-only within a live project

Suggestions, `ReviewInspection`, `ReviewDecision`, claim revisions, AI disclosure/
consent/events/results, and artifact snapshots are immutable and append-only while a
project exists. A complete, explicitly confirmed project deletion can purge the project,
its content, and its audit history. User-interface (UI) deletion of one item cannot rewrite history.

## 4. The companion is hardened for loopback access

The companion binds only to approved loopback addresses at the installer-owned stable
origin. It rejects unexpected `Host`, `Origin`, Fetch Metadata, session, and cross-site request forgery (CSRF) values.
The bootstrap endpoint can accept an absent `Origin` only for a real Word Desktop
embedded-host profile that Phase 1 verified. An unexpected `Origin` always fails.
Every mutation requires a short-lived `Secure`, `HttpOnly`, `SameSite=Strict` session
cookie plus a separate session-bound CSRF token.

The product does not cryptographically authenticate Word as a client. The local
operating-system user account is the v1 trust boundary. A same-user native process,
malicious browser extension, or compromised user profile can imitate local request
context. These threats are outside the v1 browser-origin boundary.

Each installation has unique certificate/key material constrained to the loopback
hostname. Private keys and durable installation credentials are operating-system-protected and never
enter SQLite, logs, the manifest, browser storage, or task pane JavaScript. Renewal,
rotation, rollback, revocation, repair, and uninstall cleanup are required behaviors.

## 5. Production support requires real cross-platform evidence

Development sideloading is not production distribution. V1's candidate production route
is administrator deployment of the Extensible Markup Language (XML) manifest plus separately managed installation of
the companion. The product must not claim production readiness before Phase 1 passes.
Phase 1 must prove the manifest source, trust, bootstrap, webview behavior, repair, and
uninstall on both supported platforms before release. Phase 2 platform-neutral work can
start after the conditional Phase 1 gate in `ROADMAP.md` passes. Windows release support
remains provisional until the real Windows Word Desktop matrix passes.

The manifest does not enforce an operating-system restriction. The task pane rejects Word
on the web, mobile, non-Word hosts, missing companions, and hosts lacking the baseline.

## 6. Provenance resolves to exact immutable extraction text

Every accepted `StudyFindingRevision` resolves:

```text
StudyFindingRevision -> ReviewDecision -> Suggestion -> SourceSpan
    -> TextLayerPage -> ExtractionVersion -> Paper.pdfHash
```

`pageIndex` is zero-based and separate from displayed `pageLabel`. Portable Document Format (PDF) hash, extraction
version, parser and optical character recognition (OCR) identity, page values, offsets, exact text, and
`pageTextChecksum` are required. A valid span satisfies:

```text
sha256(UTF8(page.text)) == sourceSpan.pageTextChecksum
sliceByUnicodeCodePoint(page.text, startOffset, endOffset)
    == sourceSpan.exactText
```

Extraction text is not Unicode-normalized after offsets and checksum are generated.
Substring search and JavaScript `String.slice()` do not prove a span.

## 7. Confirmed presentation precedes acceptance

Acceptance is single-item and human-only. Before an accepting `ReviewDecision`, the
application presents the exact rendered page, source span, checksum, and extraction
version, and the researcher explicitly confirms that presentation. One
`ReviewInspection` records one suggestion/span/session combination. Every accepted span
requires a matching current-session inspection bound to the rendered-page and canonical
presentation digests.

This record proves presentation and confirmation, not attention, comprehension, or truth.
Bulk acceptance and automatic acceptance are forbidden.

## 8. Review decisions are deterministically ordered

`ReviewDecision.sequence` starts at 1 and increases by one for its suggestion. The first
has no `supersedesDecisionId`. Each later decision points to the current prior decision.
The append and head check are atomic. A stale predecessor or sequence returns
`409 Conflict`.

Original suggestion text remains immutable. Human edits live in `reviewedText`. Source
spans are never rewritten to make edited prose appear verbatim.

## 9. Microsoft AI has two narrow advisory operations

`MicrosoftAiGateway` is the only component permitted to send application data off-device. V1 operation types are
`analysis` and `research`. Validation is an Analysis purpose. Their shared status
vocabulary is:

```text
prepared | consented | running | succeeded | failed | cancelled | unavailable
```

Analysis receives only explicitly selected text/excerpts and disclosed metadata. Research
receives only its approved query and optional selected context. Neither receives raw PDFs,
SQLite/index data, local paths, credentials, unrelated findings, or undisclosed Word
content.

AI cannot accept evidence or write an inspection or decision. AI cannot approve a
synthesis claim or decide a gap. AI cannot create an insertable artifact without review.
AI cannot mutate Word.
Local workflows remain available when AI is not configured or unavailable.

## 10. Every remote attempt consumes exact one-use consent

Before every Analysis or Research attempt, the application locally renders the exact
canonical request body and computes `sha256(canonicalRequestBytes)`. One-use consent is
bound to operation/type, digest, exact endpoint, deployment/base model and version, tool
selection, disclosure version, notices, and expiry. Execution recreates the bytes and
rejects any mismatch.

The gateway permits only the configured exact Azure OpenAI host. It rejects redirects and
disables environment-proxy inheritance. It verifies Transport Layer Security (TLS) and
enforces all configured bounds. It makes one attempt and validates structured output
locally. A retry requires a new preview and consent. Local storage records disclosed
fields and the result or failure.

## 11. Remote processing is nonpersistent, not “zero retention”

Every Azure OpenAI Responses API request sets `store: false`. V1 forbids response chaining,
conversations, remote files, vector stores, file search, Assistants, and batches. It also
forbids stored responses, background mode, code interpreter, Model Context Protocol (MCP),
and other remote state.
Context management, prompt-cache control fields, and encrypted-reasoning carryover are
also forbidden.

Every consent says Microsoft can process prompts and completions for abuse monitoring under
the resource's applicable configuration. The product never promises zero retention.
Research consent separately discloses web-search tool cost, external processing, and
Microsoft's stated Data Protection Addendum (DPA) and geographic/compliance-boundary limitations.

## 12. Research discoveries are not evidence

An Azure `web_search` result becomes only a local `ResearchDiscovery`. Before a discovery
supports a finding or claim, the researcher must acquire its cited source. The researcher
must import and review the source through the normal provenance workflow. A uniform resource locator (URL) or model
summary alone cannot become evidence.

## 13. Synthesis is multi-paper

A `StudyFindingRevision` belongs to one `paperId`. Every approved
`SynthesisClaimRevision` references accepted findings from at least two distinct
`paperId` values through typed `EvidenceLink` records. There is no single-study exception.
A one-paper boundary observation remains a finding.

Only a researcher approves a claim, comparison, research question, or gap conclusion.

## 14. Gap conclusions are corpus-bounded

A gap test searches every eligible, successfully indexed revision recorded in one
immutable `CorpusSnapshot`. The snapshot also records exclusions and failures. The snapshot pins
query, filters, `LocalEmbeddingProfile`, index version, and time.

Successful search reaches only `corpusSearched`. The researcher is the only actor
permitted to append `researcherSubstantiated` or `rejected`. Product language never equates a local corpus
search with proof about the wider literature.

## 15. V1 embeds locally and does not generate locally

V1 packages a pinned offline `sentence-transformers/all-MiniLM-L6-v2` Open Neural Network Exchange (ONNX) model and
tokenizer for embeddings only. Their upstream revision, license, and SHA-256 digests are
recorded and verified before import/indexing. Runtime model download and remote embedding
calls are forbidden. V1 packages no local generative model and makes no local-generative
suggestion claim.

## 16. Paper imports are idempotent and recoverable

`POST /papers` atomically creates and enqueues one local job, returning `202 Accepted`
with `paperId` and `jobId`. A project-scoped idempotency key is bound to the PDF hash and
canonical import parameters. Identical replay returns the original IDs. The same key with
different bytes or parameters returns `409 Conflict`.

Jobs and checkpoints survive restart. Retry and cancel are explicit recorded transitions. No
hidden retry or second parse-start endpoint exists.

## 17. Artifact snapshots are immutable and plural-sourced

Every `ArtifactSnapshot.sourceRevisions` is a nonempty typed
`ArtifactSourceRevision[]` referring to accepted/approved revisions in the same project.
Snapshots and inserted Word content never change. Staleness is a derived projection or an
append-only event, not a mutable snapshot field.

## 18. Office operations respect separate transaction models

Every Word application-object mutation runs inside `Word.run()` and completes through a
batched `context.sync()` outside insertion loops. An `ArtifactInsertion` is recorded only
after sync succeeds and is reconciled with content-control tag plus idempotency key.

Document settings use the Office Common API, contain only `projectId` and schema version,
and are durable only after a successful `saveAsync()` callback outside `Word.run()`.
Evidence, credentials, local paths, and artifact content are forbidden in settings.

## 19. Production Office.js is stable and capability-gated

Task pane HyperText Markup Language (HTML) loads Office.js from Microsoft's production CDN in `<head>` and does not
bundle it. Stable `WordApi 1.3` is the baseline. Preview CDN URLs, preview type packages,
and unguarded use of newer APIs fail verification.

## 20. OpenAPI is the loopback contract

Pydantic models produce deterministic OpenAPI 3.1. TypeScript loopback types and the
client are generated from it. Hand-maintained cross-stack mirrors are forbidden. A
regeneration dirty diff fails verification.
