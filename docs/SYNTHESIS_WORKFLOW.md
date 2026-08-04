# Synthesis workflows

## Actors

The workflows use these actors:

- **Researcher:** Local operating-system user and sole review and approval authority
- **Word task pane:** Presentation and Word mutation client
- **Local companion:** Authoritative application programming interface (API), persistence, consent coordinator, and job
  supervisor
- **Local workers:** Extraction, optical character recognition (OCR), local embedding/indexing, deterministic analysis,
  and consented remote-operation execution
- **MicrosoftAiGateway:** Only application-data egress adapter for `analysis` and
  `research`
- **Word Desktop:** Supported Windows/macOS destination for approved snapshots

## 1. Deploy, install, and open

The deployment sequence is:

1. A Microsoft 365 administrator deploys the Extensible Markup Language (XML) add-in-only manifest through the
   organization-approved Microsoft path.
2. Device management installs the separately signed local companion package.
3. The installer creates installation-unique certificate and key material.
4. The installer protects this material with operating-system facilities.
5. The installer reserves the stable origin and registers startup and repair.
6. Word Desktop loads the task pane from the HTTPS loopback origin.
7. The task pane waits for `Office.onReady()`.
8. The task pane confirms Word Desktop on Windows or macOS.
9. The task pane checks `WordApi 1.3`.
10. The task pane calls the bootstrap route.
11. The companion classifies the bootstrap request.
12. The companion accepts the exact `Origin` or the verified missing-`Origin` embedded-host profile.
13. The companion creates the session cookie.
14. The companion returns the session-bound cross-site request forgery (CSRF) token.
15. The generated client calls `/health`.

The XML manifest cannot enforce operating-system support. If local assets load on an
unsupported host, the task pane shows an unsupported-host screen. The screen has no
feature user interface (UI). A
missing or unhealthy companion prevents the loopback load. A custom screen cannot appear
before that load. Phase 1 records the real Office error. Development sideloading is not a
production installation route.

The production sequence remains conditional on the complete Windows and macOS release
matrix. The conditional Phase 1 gate permits platform-neutral Phase 2 work. It does not
establish Windows release support.

## 2. Create or link a project

The project-link sequence is:

1. The researcher creates or chooses a project in local SQLite.
2. The task pane invokes the Office Common API settings adapter.
3. The adapter sets only `projectId` and document-link schema version.
4. The link becomes durable only when the `saveAsync()` callback reports success.
5. Reopening resolves the opaque project identifier through the local companion.

`saveAsync()` is not inside `Word.run()`. Moving a Word document to another machine does
not move the project. Export and import form a separate local operation. Word can independently
sync that document through Microsoft 365 services, outside the add-in's control.

## 3. Import and index papers locally

The local-import sequence is:

1. The researcher selects local Portable Document Format (PDF) files.
2. The task pane submits each file over loopback with an `Idempotency-Key` and canonical import
   parameters.
3. The companion verifies PDF bounds and computes `sha256(pdfBytes)`.
4. The companion stores the content object.
5. The companion atomically creates a paper and queued job.
6. The companion returns `202 Accepted` with `paperId` and `jobId`.
7. A worker creates an immutable extraction version.
8. The worker uses OCR only when needed.
9. The worker renders page previews and records `pageIndex` and `pageLabel`.
10. The worker creates local embeddings and indexes.
11. Deterministic rules can create immutable suggestions.
12. The task pane displays persisted progress and fetches the successful projection.

V1 runs no local generative model.

An identical idempotency replay returns the original IDs. The same key with different PDF
bytes or parameters returns `409 Conflict`. Jobs resume from checkpoints. Retry and cancel
are explicit, and there is no hidden retry or second parse request.

## 4. Inspect and decide one suggestion

The single-item review sequence is:

1. The queue loads immutable suggestions and the current ordered decision projection.
2. The researcher opens one suggestion and one source span.
3. The companion verifies:

   ```text
   sha256(UTF8(page.text)) == sourceSpan.pageTextChecksum
   sliceByUnicodeCodePoint(page.text, startOffset, endOffset)
       == sourceSpan.exactText
   ```

4. The task pane presents the matching local page, extraction version, page values,
   highlighted span, and original suggestion text.
5. The researcher explicitly confirms that exact presentation.
6. The companion appends one `ReviewInspection` with the required presentation and session bindings.
7. Acceptance or rejection appends the next `ReviewDecision`, with
   `supersedesDecisionId`, monotonic sequence, referenced inspections, and optional
   `reviewedText`.

Every accepted span needs a current-session inspection. A stale decision head returns
`409 Conflict`. There is no bulk/automatic acceptance. The inspection is evidence of
presentation and confirmation, not proof of attention or correctness.

The inspection binds to the suggestion, span, extraction version, checksum, page digest,
presentation digest, and review session.

## 5. Request optional Microsoft Analysis

Analysis can critique, compare, validate an interpretation, or suggest a research question
using only material the researcher selects.

The Analysis sequence is:

1. The researcher chooses the Analysis purpose, instruction, and exact local excerpts.
2. The companion builds the stable Azure OpenAI Responses API v1 body.
3. The body uses no tools, sets `store: false`, applies hard bounds, and uses strict `analysis_result_v1` JSON Schema.
4. The companion serializes the body with RFC 8785 and computes SHA-256.
5. The companion records `prepared`.
6. The task pane renders the exact canonical payload.
7. The task pane shows the endpoint, deployment, model, version, zero tools, and bounds.
8. The task pane shows cost, persistence, abuse-monitoring, and single-attempt notices.
9. Explicit confirmation appends one-use consent bound to every disclosed property and
   moves the operation to `consented`.
10. Execution atomically consumes consent.
11. The companion records `running`.
12. `MicrosoftAiGateway` makes exactly one bounded request.
13. The companion validates response size, output items, and strict schema.
14. The companion records
   `succeeded`, `failed`, `cancelled`, or `unavailable`.
15. The task pane shows advice beside—not in place of—the human review flow.

Any payload, endpoint, model, tool, notice, or expiration change requires a new preview
and consent. A timeout is not retried automatically. Analysis cannot write a decision or
approve any domain object.

## 6. Request optional Microsoft Research

Research is a separate operation with a separate consent screen.

The Research sequence is:

1. The researcher writes a query and optionally chooses exact context excerpts.
2. The companion builds an Azure Responses API v1 body.
3. The body sets `store: false` and uses exactly one `web_search` tool.
4. The body applies Research bounds and uses strict `research_result_v1` JSON Schema.
5. The companion canonicalizes and digests the body.
6. The companion records `prepared`.
7. The task pane renders the exact query and context.
8. The task pane identifies the tool, Azure resource, model, and applicable cost basis.
9. The task pane states that Microsoft's Data Protection Addendum (DPA) does not cover this search data.
10. The task pane states that processing can cross the selected compliance or geographic boundary.
11. The companion records and consumes consent for one attempt as in Analysis.
12. The gateway requires a completed web-search call.
13. The gateway validates sources, citations, and the strict result schema.
14. The companion appends the terminal status and local `ResearchResult`.
15. Each cited item becomes only a `ResearchDiscovery`.

To use a discovery as evidence, the researcher obtains its source, imports it as a local
paper, and completes the normal provenance/inspection/decision workflow. A discovery can
never automatically support a finding, synthesis claim, gap conclusion, or artifact.

## 7. Build and approve synthesis

The synthesis sequence is:

1. Accepted decisions create or revise single-paper `StudyFindingRevision` records.
2. The researcher selects findings from multiple papers and assigns typed evidence roles.
3. Local comparison logic can propose rows or claim wording without approving it.
4. The researcher edits and approves a `SynthesisClaimRevision`.
5. The companion rejects approval unless evidence resolves to at least two distinct
   `paperId` values.

A single-study boundary condition stays a `StudyFindingRevision`. Analysis advice can be
visible during drafting but never supplies acceptance or approval.

## 8. Test a corpus-bounded gap

The gap-test sequence is:

1. The researcher defines a query and filters.
2. The companion freezes every considered paper, extraction, and index revision in a `CorpusSnapshot`.
3. The snapshot includes exclusions and failures.
4. The companion pins the local embedding profile.
5. A local worker searches the entire eligible snapshot and records matches.
6. Success moves the gap only to `corpusSearched`.
7. The researcher is permitted to append `researcherSubstantiated` or `rejected`, with explicitly
   corpus-bounded wording.

Microsoft Research can discover candidates for future import, but its remote result
cannot change a gap-test state or expand an existing immutable snapshot.

## 9. Freeze and insert an artifact

The artifact sequence is:

1. The researcher selects accepted/approved revisions.
2. The companion verifies project ownership and creates an immutable
   `ArtifactSnapshot` with a nonempty typed `ArtifactSourceRevision[]` and payload digest.
3. The task pane loads that exact snapshot.
4. One Word adapter opens `Word.run()`.
5. The adapter queues the complete insertion batch and content control.
6. The adapter performs one `context.sync()` outside the insertion loops.
7. Only after sync succeeds does the task pane record `ArtifactInsertion` through the
   companion.
8. If local recording is ambiguous, the content-control tag and idempotency key reconcile
   the insertion without duplicating Word content.

Later evidence revisions do not mutate the snapshot or document. A derived staleness
projection identifies superseded sources and lets the researcher create a new snapshot.

## 10. Export, delete, repair, or uninstall

The lifecycle rules are:

- Export and restore include SQLite plus all referenced content objects, with integrity
  checks and no machine-specific paths.
- Project deletion names the loss of local content and audit history.
- Project deletion requires explicit confirmation.
- A transaction or recoverable job purges both stores.
- Repair revalidates the stable port, startup entry, binaries, trust chain, and keys.
- Repair revalidates managed-manifest availability without changing the origin or deleting projects.
- Uninstall stops the companion.
- Uninstall removes startup entries, certificate trust, leaf and root keys, and reserved integration state.
- Deleting user projects is a separate explicit choice.
- Uninstall evidence records what the process preserved and removed.
