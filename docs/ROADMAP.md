# Implementation roadmap

## Purpose

This roadmap is the dependency-ordered implementation contract. A phase consumes only
evidence produced by earlier exit gates. `INVARIANTS.md` is normative; passing a demo does
not waive an invariant.

This documentation task authorizes no application code, installer, schema, manifest,
migration, test, generated client, package, release, or deployment. Separate approval is
required to begin the Phase 1 feasibility spike.

## Product boundary fixed by Phase 0

- V1 supports managed Windows and macOS Microsoft Word Desktop only.
- The add-in and companion have no hosted application infrastructure.
- “Local-only” describes the add-in/companion, not Word's own OneDrive, SharePoint,
  AutoSave, or connected experiences.
- Optional off-device operations are Azure OpenAI in Microsoft Foundry Responses API v1
  `analysis` and `research`; validation is an Analysis purpose.
- V1 packages one offline embedding model and no local generative model.
- All AI advice is nonauthoritative; web results are discovery records until imported and
  reviewed locally.

## Dependency map

| Phase | Consumes | Proves or delivers for the next phase |
| :--- | :--- | :--- |
| 0. Contract | Product intent and official documentation | One vocabulary, constraints, unresolved spikes |
| 1. Feasibility | Approved Phase 0 contract | Supported host/deployment plus trusted loopback viability |
| 2. Local foundation | Phase 1 evidence | Durable local platform, packaged extraction/OCR/embeddings |
| 3. Import/provenance | Local foundation | Exact versioned paper evidence and local index |
| 4. Human review | Verified provenance | Enforceable inspections, ordered decisions, accepted findings |
| 5. Optional Microsoft AI | Consent infrastructure and reviewed local material | Advisory Analysis and Research/discovery only |
| 6. Synthesis/gaps/questions | Accepted multi-paper evidence and local index | Approved domain revisions |
| 7. Artifacts/Word | Approved revisions and proved Office boundary | Immutable, reconciled Word insertions |
| 8. Hardening/distribution | All prior release evidence | Signed, supportable managed release candidate |

No phase may “borrow” an unproved capability from a later phase.

## Gate vocabulary

- **Exit evidence:** durable artifacts needed to review the phase.
- **Hard gate:** objective pass/fail decision; failure stops dependent work.
- **Blocker owner:** role responsible for resolving or explicitly rejecting the path, not
  a claim that the blocker is already resolved.

---

## Phase 0 — Architecture and product contract

### Goal

Create one implementation-ready planning baseline and make every unsupported production
assumption visible before code is authorized.

### Dependencies

- Product intent: local-first Word Desktop research assistant.
- Current official Microsoft documentation.
- Complete read of all eight repository planning documents and applicable instructions.

### Deliverables

1. Scope the local-only promise to add-in/companion data transmission and disclose Word
   host behavior.
2. Select Azure OpenAI in Microsoft Foundry Responses API v1 at
   `POST https://{resource-name}.openai.azure.com/openai/v1/responses?api-version=v1`.
3. Select `gpt-5` version `2025-08-07`, separate Analysis/Research deployment names,
   strict JSON Schema output, and stable `web_search` for Research.
4. Specify exact-payload disclosure, RFC 8785 bytes, SHA-256, one-use consent, transport
   restrictions, bounds, notices, local audit records, and closed AI statuses.
5. Select managed organizational manifest deployment plus separately managed companion as
   the v1 production candidate; label loopback loading as an unresolved Phase 1 spike.
6. Specify stable loopback origin, certificate lifecycle, session/CSRF requirements, and
   runtime unsupported-host policy.
7. Align domain entities, state transitions, Unicode provenance, inspections, decision
   ordering, two-paper synthesis, artifact sources, immutability, and idempotency.
8. Select `WordApi 1.3`, production Office.js CDN, and separate Word/Common API transaction
   boundaries.
9. Select offline `sentence-transformers/all-MiniLM-L6-v2` embeddings and explicitly
   exclude a v1 local generative model.
10. Make `INVARIANTS.md` normative and align the other seven documents with it.

### Explicit non-goals

- No application code, prototype, manifest, installer, schema, migration, test, generated
  client, dependency package, Azure resource, release, or distribution.
- No claim that Centralized Deployment proves loopback compatibility.
- No personal/unmanaged production distribution promise.
- No consumer Copilot integration, preview API dependency, or Deep Research.

### Exit evidence

- Reviewed diffs for the eight documents only.
- Cross-document scans show one vocabulary and no stale validation-only/local-generative
  contract.
- Every Microsoft production claim has an official link nearby; uncertainty is labeled as
  a spike or blocker.
- Product, architecture, security/privacy, Office platform, and distribution owners record
  approval of the baseline and Phase 1 scope.

### Hard gate

All eight documents agree, the owners accept the disclosed limitations, and no
unsupported behavior is presented as guaranteed. Application code remains unauthorized
until the user separately starts Phase 1.

### Blockers and owners

| Blocker | Owner | Resolution required |
| :--- | :--- | :--- |
| Managed-only v1 may not fit target customers | Product | Accept managed organization scope or select another supported route |
| Loopback task-pane source is not proven by Microsoft docs | Office platform | Carry as Phase 1 hard spike, not a guarantee |
| Word-to-companion session bootstrap is not yet selected | Security + platform | Prove a design without a durable JavaScript/manifest secret |
| Azure subscription/billing and Research terms may be unacceptable | Product + privacy | Keep AI optional; approve or leave disabled |

Microsoft sources: [Responses REST v1](https://learn.microsoft.com/en-us/rest/api/microsoft-foundry/azureopenai/responses),
[web search](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/web-search),
[AI data/privacy](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy),
[Office deployment requirements](https://learn.microsoft.com/en-us/office/dev/add-ins/concepts/requirements-for-running-office-add-ins), and
[runtime platform limitation](https://learn.microsoft.com/en-us/office/dev/add-ins/develop/understand-requirement-configuration).

---

## Phase 1 — Cross-platform feasibility gates

### Goal

Prove the risky host/deployment/trust chain with the smallest disposable vertical spike on
real supported Windows and macOS Word Desktop environments.

### Dependencies

- Approved Phase 0 contract and explicit authorization for spike code/packages.
- Eligible managed Microsoft 365 test tenant and administrator.
- Supported Windows/macOS devices, current Word Desktop, WebView2/WKWebView, signing test
  identities, and packaging tools.

### Deliverables

1. Minimal XML add-in-only manifest deployed through the selected organizational route.
2. Minimal signed companion installers/packages that generate installation-unique local
   root/leaf certificates, protect keys, own
   `https://word-researcher.localhost:4179`, start the companion, repair it, and uninstall
   trust/startup integration.
3. Minimal task-pane HTML loading Office.js from the production CDN in `<head>`.
4. Runtime checks for Word Desktop, Windows/macOS, and `WordApi 1.3`; explicit unsupported
   screens when assets load, plus documented fail-closed Office behavior when the local
   companion cannot serve those assets.
5. Proved session bootstrap with `Secure`, `HttpOnly`, `SameSite=Strict` cookie, separate
   CSRF token, exact Host/Origin/Fetch Metadata enforcement, and no durable per-install
   JavaScript or manifest secret.
6. Minimal `/health` route, deterministic OpenAPI 3.1 generation, generated TypeScript
   client, and real generated-client round trip.
7. Captured WebView2/WKWebView navigation, cookie, origin, fetch, certificate, CSP, and CORS
   behavior.
8. Certificate expiry/renewal/rotation/rollback/revocation, port-conflict, restart,
   repair, and uninstall cleanup exercises.

### Explicit non-goals

- No project, PDF, extraction, database domain, research UI, AI call, synthesis, artifact,
  or Word-content insertion.
- No production branding or broad installer feature set.
- No fallback to HTTP, random ports, shared certificates, manual trust bypass, or
  development sideloading as production evidence.

### Exit evidence

- `VERIFICATION.md` Phase 1 matrix passes on both platforms with exact versions recorded.
- Microsoft 365 admin deployment evidence and separate package evidence are linked.
- The same stable origin survives restart and repair.
- Security traces show rejected cross-site/host/session/CSRF attacks and accepted real-host
  traffic.
- Generated-client `/health` succeeds in both real Word hosts.
- Uninstall removes processes, startup state, trust, leaf/root keys, and integration state;
  repair leaves origin stable.

### Hard gate

**Hard stop:** Phase 2 cannot begin unless production-candidate manifest deployment,
trusted loopback loading, secure session bootstrap, and lifecycle cleanup all pass on both
platforms. If either platform fails, narrow the support policy or select a different
Microsoft-supported architecture and repeat Phase 0/1 review.

### Blockers and owners

| Blocker | Owner | Resolution required |
| :--- | :--- | :--- |
| Central-deployed manifest may reject or mishandle local source URL | Office platform + IT admin | Real tenant/device evidence or supported alternative |
| WebView header/cookie behavior may prevent strict bootstrap | Security + task-pane platform | Observed matrix and threat-reviewed bootstrap |
| Enterprise policy may prohibit installed local trust roots | Distribution + security | Approved certificate strategy or stop loopback design |
| Signed repair/uninstall behavior differs by OS | Platform packaging | Passing platform-specific lifecycle evidence |

Official context: Microsoft documents admin/app-catalog availability for task-pane add-ins
([requirements](https://learn.microsoft.com/en-us/office/dev/add-ins/concepts/requirements-for-running-office-add-ins))
and WebView2/WKWebView hosts
([browsers used by Office](https://learn.microsoft.com/en-us/office/dev/add-ins/concepts/browsers-used-by-office-web-add-ins)); neither link substitutes for the required loopback spike.

---

## Phase 2 — Local foundation

### Goal

Build only the platform-neutral durable substrate after the host architecture is proved.

### Dependencies

- Passed Phase 1 hard gate.
- Approved platform adapter contracts and data-location policy.

### Deliverables

1. SQLite migration runner, foreign-key constraints, unit-of-work boundaries, backup
   primitives, and tested journal mode.
2. Addressed local content store with path/symlink/junction defense, integrity checking,
   private temporary work, and opaque IDs.
3. Windows Credential Manager/macOS Keychain adapters and non-secret reference records.
4. Durable job/event/checkpoint substrate, supervised worker protocol, explicit retry and
   cancellation.
5. Pydantic OpenAPI 3.1 contract, deterministic generation, TypeScript client generation,
   structured safe errors, and dirty-diff gate.
6. Deny-by-default outbound network composition and dependency/static boundary rules.
7. Packaged offline PDF extraction, OCR, rendering, and ONNX Runtime dependencies.
8. Packaged offline `all-MiniLM-L6-v2` model/tokenizer with exact upstream revision,
   license record, runtime version, SHA-256 digests, and startup verification.
9. Local project deletion/export/restore primitives spanning SQLite and content store.

### Explicit non-goals

- No user PDF import workflow, extraction domain records, review, AI, synthesis, gap UI,
  artifact, or Word mutation.
- No runtime dependency/model download or remote embedding.
- No local generative model.

### Exit evidence

- Clean install initializes/migrates/reopens SQLite and content store on both OSes.
- Crash-injection proves atomic durable job/checkpoint recovery.
- Path attack suite and network-denial suite pass.
- OpenAPI/client regenerations are byte-stable and a clean regeneration has no diff.
- Extraction/OCR/embedding binaries, tokenizer, model, licenses, versions, and digests are
  present and verified fully offline.
- Export/restore and confirmed complete deletion pass integrity tests.

### Hard gate

Phase 3 cannot import/index user data until every runtime dependency and embedding artifact
is packaged, pinned, licensed, verified offline, and blocked from network download.

### Blockers and owners

| Blocker | Owner | Resolution required |
| :--- | :--- | :--- |
| Exact ONNX/tokenizer/runtime revisions and license approval | ML platform + legal | Release manifest with digests/licenses |
| SQLite journal behavior on selected OS data paths | Storage | Cross-platform crash/locking evidence |
| Worker supervision differs by platform | Platform | Proved process lifecycle adapter |

---

## Phase 3 — Import, extraction, and provenance

### Goal

Turn local PDFs into immutable, exactly addressable extraction revisions and a local index.

### Dependencies

- Passed Phase 2 foundation gate and verified extraction/OCR/embedding packages.

### Deliverables

1. Project/paper/import records and `POST /projects/{projectId}/papers` returning `202`.
2. Idempotency binding to project, PDF SHA-256, and canonical import-parameter digest;
   `409 Conflict` on key reuse with different bytes/parameters.
3. Versioned PDF validation, extraction, conditional OCR, page rendering, structure
   analysis, local embeddings, and index creation through durable jobs.
4. Immutable `ExtractionVersion`, `TextLayerPage`, and `SourceSpan` records with separate
   zero-based `pageIndex` and `pageLabel`.
5. Exact `pageTextChecksum` and Unicode-code-point slicing without post-offset
   normalization.
6. Deterministic local-rule suggestions only, linked to exact source spans.
7. Page-preview and job/result APIs using generated client types.

### Explicit non-goals

- No acceptance/rejection, bulk review, AI call, synthesis approval, gap conclusion,
  artifact, or Word mutation.
- No local generative suggestion engine.
- No automatic migration of old spans to a new parser version.

### Exit evidence

- Import matrix passes for valid/malformed/encrypted/image-only/mixed/oversize PDFs.
- Kill/restart at every stage proves checkpoint recovery and explicit attempts.
- Idempotency matrix proves exact replay versus both `409` mismatch cases.
- Provenance fixtures cover repeated text, emoji, combining characters, ligatures, OCR,
  page-label differences, boundaries, and parser upgrades.
- All import/index work succeeds with network denied.

### Hard gate

Phase 4 cannot accept evidence until every suggestion resolves through the exact checksum,
code-point slice, extraction version, page, and PDF hash chain.

### Blockers and owners

| Blocker | Owner | Resolution required |
| :--- | :--- | :--- |
| Parser/OCR output cannot preserve deterministic text/offsets | Extraction | Versioned representation and passing fixtures |
| Page labels unavailable for a format | Extraction + product | Preserve explicit unknown label without conflating index |
| Embedding package mismatch | ML platform | Fail indexing and repair package; never download |

---

## Phase 4 — Enforced human review

### Goal

Make local presentation and human authority enforceable, ordered, and auditable one item at
a time.

### Dependencies

- Passed Phase 3 provenance gate.

### Deliverables

1. Review queue/current-decision projections from SQLite.
2. Single-item page/span presentation with revalidation immediately before confirmation.
3. `ReviewSession` and `ReviewInspection` append bound to suggestion, one span, extraction
   version, checksum, rendered-page/presentation digests, and session.
4. `ReviewDecision` append with exact monotonic sequence, `supersedesDecisionId`, atomic
   head compare, optional `reviewedText`, and referenced inspections.
5. Accepted single-paper `StudyFindingRevision` projection.
6. Explicit conflict/reload UI for concurrent or stale decisions.

### Explicit non-goals

- No bulk/automatic acceptance, dwell-time or attention claim, model-written decision,
  synthesis approval, Research discovery acceptance, artifact, or Word mutation.

### Exit evidence

- Every invalid/missing/stale inspection combination is rejected.
- The exact page/extraction/checksum is demonstrably presented before confirmation.
- Concurrent head test produces one append and one `409 Conflict`.
- Original text/spans remain immutable while human edits remain distinct.
- Local-only review functions with network denied and survives restart.

### Hard gate

Phase 5/6 cannot consume “accepted” evidence unless the decision references valid
current-session inspection records and passes deterministic ordering.

### Blockers and owners

| Blocker | Owner | Resolution required |
| :--- | :--- | :--- |
| UI cannot prove exact item/version presentation | Review UX + domain | Bind rendered payload and explicit confirmation to inspection append |
| Concurrent decision semantics unclear | Domain + storage | Transactional head/sequence constraint and `409` contract |

---

## Phase 5 — Optional Microsoft AI Analysis and Research

### Goal

Add the two narrowly consented Azure operations without making any local workflow or
acceptance rule depend on them.

### Dependencies

- Passed Phase 4 review gate.
- Separately provisioned Azure subscription/resource/quota/billing and API key.
- Two deployments pinned to the approved base model/version and Research `web_search`
  enabled.
- Privacy/security/product approval of operation-specific notices.

### Deliverables

1. `MicrosoftAiGateway` as the sole application-data egress adapter.
2. Separate Analysis/Research request and strict result schemas, preview endpoints,
   consent records, execute/cancel/status endpoints, and local results/discoveries.
3. RFC 8785 canonical body bytes, SHA-256, exact preview, one-use consent binding, expiry,
   and atomic consumption.
4. Exact-host allowlist, redirect rejection, verified TLS, environment-proxy disabling,
   single attempt, bounds, safe errors, and structured validation.
5. Azure Responses API v1 with `store: false`; no response chaining or prohibited remote
   state/features.
6. Analysis with no tools and purposes including interpretation validation.
7. Research with exactly stable `web_search`, completed-tool/citation validation, and
   local `ResearchDiscovery` results.
8. Separate cost/retention/external-processing notices, including Research DPA/geographic
   limitations and non-zero-retention wording.
9. Closed statuses everywhere: `prepared | consented | running | succeeded | failed |
   cancelled | unavailable`.

### Explicit non-goals

- No consumer Copilot API, `web_search_preview`, Deep Research, background operation,
  remote files/vector stores, conversation chaining, batch, stored response, Assistants,
  file search, code interpreter, MCP, auto retry, or automatic evidence acceptance.
- No Azure credential in task-pane code or configuration response.
- No AI mutation of Word or authoritative domain approvals.

### Exit evidence

- Common and operation-specific tests in `VERIFICATION.md` pass with fake transport.
- Redacted Azure capability probe confirms stable v1 endpoint, configured deployments,
  strict structured output, and `web_search` on the approved resource/region.
- Byte/digest/consent tests prove transport bytes equal disclosed bytes and one consent
  permits one attempt.
- Host/redirect/proxy/bounds/no-retry/adversarial-response tests pass.
- UI approval captures show complete Analysis and separate Research notices.
- An Azure citation can become only a discovery until its source is imported/reviewed.
- All local workflows pass while Azure is disabled and unavailable.

### Hard gate

Neither operation ships unless its exact configured resource/deployment/model/tool passes
the capability probe and its disclosure is approved. Failure disables that operation; it
does not block the local product. A retired or changed model invalidates the probe.

### Blockers and owners

| Blocker | Owner | Resolution required |
| :--- | :--- | :--- |
| Azure resource/quota/billing unavailable | Customer admin + product | Provision or leave operations disabled |
| Approved model version/tool unavailable in selected region | AI platform | Supported reprovisioning and new disclosed profile |
| Research DPA/geographic limitation unacceptable | Privacy + customer admin | Disable Research; do not weaken notice |
| Abuse-monitoring terms incompatible with selected data | Privacy | Disable AI or obtain an approved contractual/resource configuration |

Microsoft sources: [Responses API](https://learn.microsoft.com/en-us/rest/api/microsoft-foundry/azureopenai/responses),
[structured outputs](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs),
[web search and compliance warning](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/web-search), and
[data/privacy/abuse monitoring](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy).

---

## Phase 6 — Synthesis, gaps, and research questions

### Goal

Build researcher-approved interpretation on accepted local evidence and immutable corpus
snapshots.

### Dependencies

- Passed Phase 4 accepted-evidence gate.
- Phase 3 local index; Phase 5 is optional and never a dependency for approval.

### Deliverables

1. Typed `EvidenceLink` and revisioned comparison/claim/question domain services.
2. Approval rule requiring findings from at least two distinct papers for every
   `SynthesisClaimRevision`.
3. Immutable `CorpusSnapshot` including eligible, excluded, and failed paper revisions,
   query, filters, index version, and `LocalEmbeddingProfile`.
4. Durable gap tests with only `corpusSearched` as automatic success and human-only
   substantiated/rejected transitions.
5. Corpus-bounded language in every gap UI/export.
6. Optional Analysis advice and Research discoveries shown as advisory inputs, never
   accepted evidence.

### Explicit non-goals

- No single-paper synthesis exception, wider-literature gap proof, AI approval, discovery-
  as-evidence shortcut, artifact freeze, or Word mutation.

### Exit evidence

- Two-distinct-paper constraint and typed-link trace tests pass.
- One-paper observations remain findings.
- Corpus snapshot completeness/exclusion/failure tests pass and are reproducible offline.
- Worker/AI attempts to substantiate/reject gaps or approve revisions fail.
- Research questions and comparisons retain revision/source traceability.

### Hard gate

Phase 7 receives only accepted/approved immutable revisions. Drafts, discoveries, advice,
and unsubstantiated gap searches are not insertable sources.

### Blockers and owners

| Blocker | Owner | Resolution required |
| :--- | :--- | :--- |
| Synthesis UI encourages unsupported one-paper claims | Research UX + domain | Enforce finding/claim distinction in service and UI |
| Corpus eligibility cannot be reproduced | Indexing + domain | Immutable complete snapshot and pinned profile |

---

## Phase 7 — Immutable artifacts and Word integration

### Goal

Freeze approved revisions and insert them into Word exactly once with reconciliation.

### Dependencies

- Passed Phase 6 insertable-revision gate.
- Phase 1/Office baseline evidence remains valid for supported Office builds.

### Deliverables

1. `ArtifactSnapshot` with nonempty typed `ArtifactSourceRevision[]`, immutable payload,
   digest, and same-project/approval checks.
2. Derived `ArtifactStalenessProjection` without snapshot mutation.
3. Word adapter using one `Word.run()`, batched commands, and `context.sync()` outside
   insertion loops.
4. Content-control tag/idempotency reconciliation and post-sync-only
   `ArtifactInsertion` append.
5. Separate Office Common API settings adapter with successful `saveAsync()` callback
   outside `Word.run()`.
6. Runtime capability guards for any selected stable API newer than `WordApi 1.3`.

### Explicit non-goals

- No live-linked/mutating inserted content, automatic stale replacement, preview API,
  evidence in document settings, AI Word mutation, or recording before sync.

### Exit evidence

- Source validation, immutability, staleness, sync-failure, and ambiguous-recording tests
  pass.
- Real Word Desktop insertions pass on both Phase 1-supported platforms/builds.
- Command traces prove no sync in insertion loops.
- Document-link settings persist only after successful `saveAsync()` and contain only the
  two allowed fields.

### Hard gate

No release candidate can insert unless post-sync recording and content-control/idempotency
reconciliation prevent duplicates under every injected failure point.

### Blockers and owners

| Blocker | Owner | Resolution required |
| :--- | :--- | :--- |
| Host update invalidates prior Office behavior | Office platform | Rerun real-host matrix or narrow supported builds |
| Reconciliation cannot distinguish successful insert | Word integration | Stable content-control tag/idempotency design |

---

## Phase 8 — Hardening and managed distribution

### Goal

Turn the proved system into a signed, supportable managed release without changing the
architecture contract.

### Dependencies

- All applicable prior hard gates and current support-matrix evidence.
- Organization deployment/signing/release owners and privacy/security approvals.

### Deliverables

1. Signed/notarized production companion packages, SBOM, dependency/model/license
   manifests, vulnerability review, and reproducible build evidence.
2. Final admin-deployable XML manifest and tenant deployment/rollback runbook.
3. Installer upgrade, repair, certificate rotation/rollback/revocation, port ownership,
   startup recovery, uninstall, and optional user-data preservation runbooks.
4. Backup/export/restore/project-deletion support documentation.
5. Privacy/cost/retention notices and Azure provisioning/disablement guide.
6. Real Word Desktop regression matrix, network-egress evidence, recovery/soak tests, and
   OpenAPI/generated-client clean-diff evidence.
7. Support policy naming managed prerequisites, supported OS/Office builds, unsupported
   hosts, known limitations, and incident response.

### Explicit non-goals

- No last-minute hosted service, personal-store promise, silent telemetry/update channel,
  preview API, unsupported platform, shared certificate, automatic AI enablement, or
  architecture bypass for release timing.

### Exit evidence

- Clean managed install/upgrade/repair/rollback/uninstall passes on both platforms.
- Administrator can deploy/remove the manifest and independently deploy/remove companion
  packages according to the runbook.
- All invariant, security, network, recovery, Word, AI-when-enabled, and documentation
  gates pass from signed artifacts.
- Uninstall evidence states exactly what integration/trust was removed and whether local
  projects were preserved or explicitly deleted.
- Release owners sign the support matrix and unresolved-risk register.

### Hard gate

Release only when signed artifacts reproduce all earlier evidence. A failed loopback,
deployment, trust, consent, provenance, review, or Word transaction invariant is a release
stop, not a documented workaround.

### Blockers and owners

| Blocker | Owner | Resolution required |
| :--- | :--- | :--- |
| Signing/notarization or enterprise rollout unavailable | Release + IT | Valid chain and managed deployment proof |
| Office/webview/security policy drift | Office platform + security | Rerun Phase 1 evidence and update support matrix |
| Azure profile retired or terms changed | AI platform + privacy | Reprobe/redisclose or ship affected operation disabled |

## Change-control rules after Phase 0

Return to Phase 0 review and rerun every affected gate when changing:

- hosted/local boundaries, supported hosts, distribution route, loopback origin, session
  bootstrap, certificate model, or Office requirement baseline;
- Azure API family/version, resource host, authentication, model/version/deployment, tool,
  remote state, bounds, canonicalization, consent, retention/cost/compliance notice;
- extraction/OCR/embedding model/runtime/version, Unicode offset convention, provenance
  fields, review authority, synthesis cardinality, gap semantics, or artifact immutability.

No compatibility shim may silently weaken an invariant.
