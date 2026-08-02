# Synthesis domain model

## Conventions

- IDs are opaque, stable, locally generated values.
- Times are UTC instants; display localization is presentation-only.
- Revisions and audit records are immutable and append-only while their project exists.
- `pageIndex` is zero-based extraction order. `pageLabel` is the independent displayed
  label printed or encoded by the document.
- Status vocabularies are closed enums, not free text.
- A complete, confirmed project deletion may purge the project's records and content.

## Project, paper, and extraction

### `Project`

```text
projectId, name, createdAt, deletedAt?
```

### `Paper`

```text
paperId, projectId, pdfObjectId, pdfHash, importParametersDigest,
currentExtractionVersionId?, createdAt
```

`pdfHash` is `sha256(pdfBytes)`. `pdfObjectId` resolves through the local content store and
is never an absolute path.

### `ExtractionVersion`

```text
extractionVersionId, paperId, parserName, parserVersion, ocrProfile,
sourcePdfHash, createdAt, status
```

`status = running | succeeded | failed | cancelled`. A parser upgrade creates a new
version and never rewrites an old text layer.

### `TextLayerPage`

```text
extractionVersionId, pageIndex, pageLabel, text, pageTextChecksum,
ocrStatus, renderedPageObjectId, renderedPageDigest
```

`ocrStatus = notRequired | applied | failed`. After offsets and the checksum are created,
`text` is immutable and is not Unicode-normalized.

### `SourceSpan`

```text
sourceSpanId, extractionVersionId, pageIndex, pageLabel,
pageTextChecksum, startOffset, endOffset, exactText
```

Offsets are half-open Unicode code-point offsets. A valid span satisfies exactly:

```text
sha256(UTF8(page.text)) == sourceSpan.pageTextChecksum
sliceByUnicodeCodePoint(page.text, startOffset, endOffset)
    == sourceSpan.exactText
```

It also requires the same extraction version, `pageIndex`, and `pageLabel` as the page.
JavaScript `String.slice()` is not a Unicode code-point implementation and cannot be used
for this check.

## Suggestions and human review

### `Suggestion`

```text
suggestionId, projectId, kind, origin, originalText,
sourceSpanIds[], extractionVersionIds[], createdAt
```

`kind = studyFinding | comparisonCandidate | gapCandidate | researchQuestionCandidate`.
`origin = localRule | microsoftAnalysis`. V1 has no local-generative origin. Suggestions
are immutable advice and never constitute acceptance.

### `ReviewSession`

```text
reviewSessionId, projectId, startedAt, endedAt?
```

### `ReviewInspection`

```text
reviewInspectionId, reviewSessionId, suggestionId, sourceSpanId,
extractionVersionId, pageIndex, pageTextChecksum,
renderedPageDigest, presentationDigest, presentedAt, confirmedAt
```

Each record covers one suggestion and one source span only. Creation requires the
companion to verify the span, serve the matching rendered page and extraction version,
hash the canonical descriptor of the page/span/suggestion presentation, and receive a
distinct researcher confirmation while that exact item is displayed. It is evidence of
presentation and explicit confirmation, not proof of attention or agreement.

An accepting decision references a current-session inspection for every source span it
uses. A record for a different suggestion, span, extraction version, checksum, or session
cannot satisfy the rule.

### `ReviewDecision`

```text
reviewDecisionId, suggestionId, sequence, supersedesDecisionId?, decision,
reviewedText?, reviewInspectionIds[], createdAt
```

`decision = accepted | rejected`. Sequence starts at 1 and increases by exactly one per
suggestion. Sequence 1 has no superseded decision; every later decision points to the
current prior decision. The companion appends this using one SQLite transaction and
returns `409 Conflict` for a stale head or sequence. `reviewedText` never changes the
suggestion or its provenance span.

### `StudyFindingRevision`

```text
studyFindingRevisionId, studyFindingId, projectId, paperId,
reviewDecisionId, reviewedText, sourceSpanIds[], sequence, createdAt
```

A finding derives from one accepted suggestion and one `paperId`. A new human decision
creates a new revision; it does not rewrite prior evidence.

## Synthesis

### `EvidenceLink`

```text
evidenceLinkId, synthesisClaimRevisionId, studyFindingRevisionId, role
```

`role = supports | contradicts | boundaryCondition | methodQualification`.

### `SynthesisClaimRevision`

```text
synthesisClaimRevisionId, synthesisClaimId, projectId, sequence,
claimText, status, evidenceLinks[], approvedAt?, supersedesRevisionId?
```

`status = draft | approved | superseded`. Only a researcher can approve. Every approved
revision must reference accepted finding revisions from at least two distinct `paperId`
values. There is no single-study exception: a one-paper observation remains a
`StudyFindingRevision`.

### `ComparisonRevision`

```text
comparisonRevisionId, projectId, dimension, rows[], sourceFindingRevisionIds[],
status, createdAt
```

Rows trace every value to accepted finding revisions. `status = draft | approved |
superseded`; approval is human.

### `ResearchQuestionRevision`

```text
researchQuestionRevisionId, projectId, questionText,
sourceClaimRevisionIds[], status, sequence, createdAt
```

`status = draft | approved | superseded`.

## Corpus-bounded gap analysis

### `LocalEmbeddingProfile`

```text
profileId, modelId, upstreamRevision, modelObjectDigest, tokenizerObjectDigest,
runtimeName, runtimeVersion, dimensions
```

V1 `modelId` is `sentence-transformers/all-MiniLM-L6-v2`. All artifacts are packaged and
verified offline before indexing. This is an embedding profile, not a generative model.

### `CorpusSnapshotPaperRevision`

```text
paperId, extractionVersionId, indexRevisionId, eligibilityStatus, reason?
```

`eligibilityStatus = included | excluded | failed`.

### `CorpusSnapshot`

```text
corpusSnapshotId, projectId, paperRevisions[], embeddingProfileId,
indexSchemaVersion, query, filters, createdAt
```

The snapshot is immutable and records every paper considered, including exclusions and
failures.

### `GapTestRevision`

```text
gapTestRevisionId, projectId, corpusSnapshotId, query, matches[],
status, conclusionText?, createdAt
```

`status = queued | running | corpusSearched | researcherSubstantiated | rejected | failed |
cancelled`. A successful local search reaches only `corpusSearched`. Only a researcher can
append the substantiated or rejected revision. The conclusion is scoped to its snapshot,
not the wider literature.

## Microsoft AI operations

### Closed vocabularies

```text
AiOperationType = analysis | research
AiOperationStatus = prepared | consented | running | succeeded |
                    failed | cancelled | unavailable
```

Validation is an Analysis purpose, not a third v1 operation. `unavailable` means the
configured resource, deployment, tool, credential, quota, or network capability was not
available before a usable result. `failed` means an attempted operation did not produce a
valid result. Local workflows do not depend on either operation.

### `AnalysisRequest`

```text
analysisPurpose, instruction, selectedMaterial[], selectedSourceMetadata[],
requestedOutputSchemaVersion
```

`analysisPurpose = critique | compare | validateInterpretation | suggestQuestion`.
Selected material is text or excerpts the researcher explicitly chose. Source metadata is
limited to displayed non-path fields.

### `ResearchRequest`

```text
query, selectedContext[], permittedDomains[]?, requestedOutputSchemaVersion
```

The only v1 tool is `web_search`. User location is omitted unless a future design adds it
to the preview and consent contract.

### `AiDisclosurePreview`

```text
operationId, operationType, canonicalRequestBytes, payloadDigest,
disclosedFields[], endpoint, deploymentName, baseModel, modelVersion, toolSelection[],
inputLimit, outputTokenLimit, responseByteLimit, timeoutSeconds,
costNotice, retentionNotice, externalProcessingNotice, expiresAt, disclosureVersion
```

`payloadDigest = sha256(canonicalRequestBytes)`. The bytes are the exact planned HTTP body,
serialized with RFC 8785 JSON canonicalization, and include `store: false`. The preview
renders those bytes field-for-field before consent.

### `AiConsentRecord`

```text
aiConsentId, operationId, operationType, payloadDigest, endpoint,
deploymentName, baseModel, modelVersion, toolSelection[], disclosureVersion,
consentedAt, expiresAt, consumedAt?
```

Consent is single-use and cannot be transferred. Any payload, endpoint, model, tool,
notice, or expiry change requires a new preview and consent.

### `AiOperationEvent` and projection

```text
aiOperationEventId, operationId, sequence, status, reasonCode?, occurredAt
```

Events are append-only and deterministically project the current `AiOperationStatus`.
Sequence increases by one. A remote attempt can occur only during the transition from
`consented` to `running`, after atomically consuming consent.

### `AnalysisResult`

```text
operationId, schemaVersion, adviceItems[], limitations[], usage,
responseDigest, recordedAt
```

### `ResearchResult` and `ResearchDiscovery`

```text
ResearchResult: operationId, schemaVersion, discoveries[], limitations[], usage,
                responseDigest, recordedAt
ResearchDiscovery: researchDiscoveryId, operationId, title, url,
                   citedPassage?, advisorySummary, citationMetadata
```

Both result types are advisory and locally schema-validated. A discovery is not a paper,
source span, finding, evidence link, gap conclusion, or artifact source. Its cited source
must be acquired by the researcher, imported into the local corpus, and reviewed normally
before it supports accepted evidence.

## Artifacts and Word insertion

### `ArtifactSourceRevision`

```text
sourceType, sourceRevisionId
```

`sourceType = studyFinding | synthesisClaim | comparison | researchQuestion |
gapConclusion`. The referenced revision must be accepted or approved, in the same project,
and valid for insertion.

### `ArtifactSnapshot`

```text
artifactSnapshotId, projectId, artifactType, sourceRevisions[],
payloadObjectId, payloadDigest, createdAt
```

`sourceRevisions` is a nonempty `ArtifactSourceRevision[]`. A snapshot and its payload are
immutable.

### `ArtifactStalenessProjection`

```text
artifactSnapshotId, isStale, supersededSourceRevisions[], calculatedAt
```

Staleness is derived from current approved heads or from append-only source-revision
events. It never mutates the snapshot or previously inserted Word content.

### `ArtifactInsertion`

```text
artifactInsertionId, projectId, artifactSnapshotId, idempotencyKey,
contentControlTag, contentControlId?, documentLinkId, insertedAt
```

The record is appended only after `context.sync()` succeeds. The idempotency key and
content-control tag reconcile ambiguous local recording failures without reinsertion.

## Import idempotency

An import key is scoped to a project and bound to `pdfHash` plus the canonical import
parameters digest. Identical replay returns the original `paperId` and `jobId`. Reusing
the same key with different PDF bytes or parameters returns `409 Conflict`; it never
silently deduplicates or starts a second job.
