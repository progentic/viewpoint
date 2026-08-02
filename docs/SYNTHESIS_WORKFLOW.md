# Synthesis workflows

## Actors

- **Researcher:** local OS user, sole review and approval authority.
- **Word task pane:** presentation and Word mutation client.
- **Local companion:** authoritative API, persistence, consent coordinator, and job
  supervisor.
- **Local workers:** extraction, OCR, local embedding/indexing, deterministic analysis,
  and consented remote-operation execution.
- **MicrosoftAiGateway:** only application-data egress adapter; supports `analysis` and
  `research`.
- **Word Desktop:** supported Windows/macOS destination for approved snapshots.

## 1. Deploy, install, and open

1. A Microsoft 365 administrator deploys the XML add-in-only manifest through the
   organization-approved Microsoft path.
2. Device management installs the separately signed local companion package.
3. The installer creates installation-unique loopback certificate/key material, protects
   it with OS facilities, reserves the stable origin, and registers startup/repair.
4. Word Desktop loads the task pane from the HTTPS loopback origin.
5. The pane waits for `Office.onReady()`, confirms Word Desktop on Windows or macOS,
   checks `WordApi 1.3`, establishes the proved local session, and calls `/health`.

The XML manifest cannot enforce OS support. If local assets load, web, mobile, non-Word,
and inadequate requirement sets receive an unsupported-host screen with no feature UI. A
missing/unhealthy companion rejects the loopback load before a custom screen is possible;
Phase 1 records the real Office error experience. Development sideloading is not a
production installation route.

The production sequence remains conditional on Phase 1 proof of managed manifest plus
per-device loopback in real WebView2 and WKWebView. Until then it is a candidate workflow,
not a support claim.

## 2. Create or link a project

1. The researcher creates or chooses a project in local SQLite.
2. The task pane invokes the Office Common API settings adapter.
3. The adapter sets only `projectId` and document-link schema version.
4. The link becomes durable only when the `saveAsync()` callback reports success.
5. Reopening resolves the opaque project ID through the local companion.

`saveAsync()` is not inside `Word.run()`. Moving a Word document to another machine does
not move the project; export/import is a separate local operation. Word may independently
sync that document through Microsoft 365 services, outside the add-in's control.

## 3. Import and index papers locally

1. The researcher selects local PDF files.
2. The pane submits each file over loopback with an `Idempotency-Key` and canonical import
   parameters.
3. The companion verifies PDF bounds, computes `sha256(pdfBytes)`, stores the content
   object, and atomically creates a paper plus queued job.
4. It returns `202 Accepted` with `paperId` and `jobId`.
5. A worker creates an immutable extraction version, OCRs only when needed, renders page
   previews, records `pageIndex` and `pageLabel`, and creates local embeddings/indexes.
6. Deterministic rules may create immutable suggestions; v1 runs no local generative
   model.
7. The pane displays persisted progress and fetches the successful projection.

An identical idempotency replay returns the original IDs. The same key with different PDF
bytes or parameters returns `409 Conflict`. Jobs resume from checkpoints; retry and cancel
are explicit, and there is no hidden retry or second parse request.

## 4. Inspect and decide one suggestion

1. The queue loads immutable suggestions and the current ordered decision projection.
2. The researcher opens one suggestion and one source span.
3. The companion verifies:

   ```text
   sha256(UTF8(page.text)) == sourceSpan.pageTextChecksum
   sliceByUnicodeCodePoint(page.text, startOffset, endOffset)
       == sourceSpan.exactText
   ```

4. The pane presents the matching locally rendered page, exact extraction version, page
   index/label, highlighted span, and original suggestion text.
5. The researcher explicitly confirms that exact presentation.
6. The companion appends one `ReviewInspection` bound to the suggestion, span,
   extraction version, checksum, rendered-page digest, canonical presentation digest, and
   review session.
7. Accept or reject appends the next `ReviewDecision`, with
   `supersedesDecisionId`, monotonic sequence, referenced inspections, and optional
   `reviewedText`.

Every accepted span needs a current-session inspection. A stale decision head returns
`409 Conflict`. There is no bulk/automatic acceptance. The inspection is evidence of
presentation and confirmation, not proof of attention or correctness.

## 5. Request optional Microsoft Analysis

Analysis can critique, compare, validate an interpretation, or suggest a research question
using only material the researcher selects.

1. The researcher chooses the Analysis purpose, instruction, and exact local excerpts.
2. The companion builds the stable Azure OpenAI Responses API v1 body with no tools,
   `store: false`, hard bounds, and strict `analysis_result_v1` JSON Schema.
3. It serializes the body with RFC 8785, computes SHA-256, and records `prepared`.
4. The pane renders the exact canonical payload and separately shows endpoint,
   deployment/base model and version, zero tools, bounds, cost basis, nonpersistent-request
   notice, possible abuse monitoring, and single-attempt rule.
5. Explicit confirmation appends one-use consent bound to every disclosed property and
   moves the operation to `consented`.
6. Execute atomically consumes consent, records `running`, and lets
   `MicrosoftAiGateway` make exactly one bounded request.
7. The companion validates response size, output items, and strict schema, then records
   `succeeded`, `failed`, `cancelled`, or `unavailable`.
8. The pane shows advice beside—not in place of—the human review flow.

Any payload, endpoint, model, tool, notice, or expiration change requires a new preview
and consent. A timeout is not retried automatically. Analysis cannot write a decision or
approve any domain object.

## 6. Request optional Microsoft Research

Research is a separate operation with a separate consent screen.

1. The researcher writes a query and optionally chooses exact context excerpts.
2. The companion builds an Azure Responses API v1 body with `store: false`, the one
   `web_search` tool, strict `research_result_v1` schema, and Research bounds.
3. It canonicalizes, digests, records `prepared`, and renders the exact query/context.
4. The screen identifies the tool and Azure resource/model, estimates the applicable
   token/tool cost basis, and prominently states that Grounding with Bing Search is not
   covered by Microsoft's DPA for this data and can process it outside the selected
   compliance/geographic boundary.
5. Researcher consent is recorded and consumed for one attempt exactly as in Analysis.
6. The gateway requires a completed web-search call, validates sources/citations and the
   strict result schema, then appends the terminal status and local `ResearchResult`.
7. Each cited item becomes only a `ResearchDiscovery`.

To use a discovery as evidence, the researcher obtains its source, imports it as a local
paper, and completes the normal provenance/inspection/decision workflow. A discovery can
never automatically support a finding, synthesis claim, gap conclusion, or artifact.

## 7. Build and approve synthesis

1. Accepted decisions create or revise single-paper `StudyFindingRevision` records.
2. The researcher selects findings from multiple papers and assigns typed evidence roles.
3. Local comparison logic may propose rows or claim wording without approving it.
4. The researcher edits and approves a `SynthesisClaimRevision`.
5. The companion rejects approval unless evidence resolves to at least two distinct
   `paperId` values.

A single-study boundary condition stays a `StudyFindingRevision`. Analysis advice may be
visible during drafting but never supplies acceptance or approval.

## 8. Test a corpus-bounded gap

1. The researcher defines a query and filters.
2. The companion freezes a `CorpusSnapshot` of every considered paper/extraction/index
   revision, including exclusions and failures, and pins the local embedding profile.
3. A local worker searches the entire eligible snapshot and records matches.
4. Success moves the gap only to `corpusSearched`.
5. The researcher may append `researcherSubstantiated` or `rejected`, with explicitly
   corpus-bounded wording.

Microsoft Research can discover candidates for future import, but its remote result
cannot change a gap-test state or expand an existing immutable snapshot.

## 9. Freeze and insert an artifact

1. The researcher selects accepted/approved revisions.
2. The companion verifies project ownership and creates an immutable
   `ArtifactSnapshot` with a nonempty typed `ArtifactSourceRevision[]` and payload digest.
3. The pane loads that exact snapshot.
4. One Word adapter opens `Word.run()`, queues the complete insertion batch and content
   control, then performs one `context.sync()` outside the insertion loops.
5. Only after sync succeeds does the pane record `ArtifactInsertion` through the
   companion.
6. If local recording is ambiguous, the content-control tag and idempotency key reconcile
   the insertion without duplicating Word content.

Later evidence revisions do not mutate the snapshot or document. A derived staleness
projection identifies superseded sources and lets the researcher create a new snapshot.

## 10. Export, delete, repair, or uninstall

- Export and restore include SQLite plus all referenced content objects, with integrity
  checks and no machine-specific paths.
- Project deletion names the loss of local content and audit history, requires explicit
  confirmation, and purges both stores transactionally or through a recoverable recorded
  job.
- Repair revalidates the stable port, startup entry, binaries, trust chain, keys, and
  managed-manifest availability without silently rotating origin or deleting projects.
- Uninstall stops the companion and removes startup entries, certificate trust, leaf/root
  keys, and reserved integration state. Deleting user projects is a separate explicit
  choice; the uninstall evidence records what was preserved and what was removed.
