# Coding style

## Goal

Minimize cognitive load through explicit ownership, narrow interfaces, and the Single
Level of Abstraction rule. `INVARIANTS.md` is normative; code that makes an invariant
unenforceable is incorrect even when it is locally convenient.

## Single Level of Abstraction

Every function operates at one level:

- **Policy / coordination** reads like a use-case summary and calls domain operations.
- **Domain logic** makes one business decision without raw framework or storage calls.
- **Implementation / infrastructure** performs serialization, hashing, SQL, filesystem,
  OS credential, Office.js, PDF, embedding-runtime, or Microsoft API mechanics.

Callers appear physically above callees in step-down order. A policy function contains no
raw API calls, SQL, regex, string slicing, path construction, magic number, or complex
boolean expression. Functions should usually fit within 20 lines with nesting depth two.
A name that needs “and” is a signal to split responsibilities.

## Stable boundaries

Use narrow interfaces for these volatile capabilities:

- generated loopback client;
- SQLite unit of work and local content store;
- durable job runner, PDF extractor, OCR engine, and local embedding index;
- `MicrosoftAiGateway` with separate `analysis` and `research` request types;
- clock, identifier generator, canonical serializer, and digest service;
- OS credential store, platform paths, installer, certificate manager, and startup manager;
- Word application-object adapter and Office Common API settings adapter.

Domain code depends on these capabilities, never on FastAPI, SQLite, Office.js, an HTTP
client, or a Microsoft SDK. Avoid speculative factories and catch-all `utils` modules.

V1 packages no local generative model. Use `localEmbeddingModel` only for the pinned,
offline embedding dependency and never as a synonym for generation or Microsoft AI.

## Module size

Split by responsibility before a file becomes difficult to understand. Treat 400 lines
as a review prompt. Files above 800 executable lines require an architecture
justification. Generated clients are exempt and live in an explicitly generated folder.

## TypeScript task pane

- Enable `strict`; forbid `any` and unchecked non-null assertions.
- Give exported functions explicit return types.
- Let React coordinate presentation; place loopback and Word mechanics in adapters.
- Use the generated OpenAPI client and same-origin `/api/v1` routes.
- Load Office.js globally from Microsoft's production CDN in the HTML `<head>`; never
  import or bundle it and never use preview Office.js or preview type packages.
- Keep Word application-object mutations in a Word adapter, within `Word.run()`, and
  finish them with a batched `context.sync()` outside insertion loops.
- Keep document-settings operations in a separate Office Common API adapter. Call
  `Office.context.document.settings.set()` and consider persistence complete only after
  the `saveAsync()` callback succeeds. Do not put this operation inside `Word.run()`.
- Use stable `WordApi 1.3` as the baseline. Guard any newer stable API with an explicit
  capability check.
- Do not use Node built-ins, filesystem APIs, credentials, or Microsoft AI SDKs.
- Do not call external application APIs. Only the companion owns Microsoft AI egress.
- Return structured errors with opaque local IDs and safe reason codes, without evidence
  text or local paths.

Example policy coordinator:

```ts
export async function insertApprovedArtifact(
  artifactSnapshotId: ArtifactSnapshotId,
): Promise<void> {
  const snapshot = await loadInsertableSnapshot(artifactSnapshotId)
  const receipt = await insertSnapshotIntoWord(snapshot)
  await recordArtifactInsertion(receipt)
}
```

Loading, command batching, synchronization, and receipt serialization belong to lower
layers. `recordArtifactInsertion` is called only after Word synchronization succeeds.

## Python local companion

- Use Python 3.12+, Pydantic v2, and type hints for public functions.
- Let routers authenticate the local session, parse one request, invoke one use case, and
  map one result.
- Let application services coordinate domain operations and transaction boundaries.
- Keep domain modules free of FastAPI, SQLite, PDF, filesystem, embedding, Microsoft SDK,
  and HTTP imports.
- Run extraction, OCR, indexing, and remote AI work in supervised workers, never on the
  FastAPI event loop.
- Persist a job and its runnable state atomically in SQLite.
- Store opaque object IDs, never absolute paths, in domain records.
- Resolve application-data and temporary locations through platform adapters.

All outbound application-data networking is implemented in `MicrosoftAiGateway`. A
static dependency rule rejects general-purpose HTTP clients elsewhere, except the
loopback server framework and an installer-only update capability if one is separately
designed and documented later.

## Microsoft AI adapter

Keep policy, operation logic, and HTTP mechanics separate:

```py
async def execute_ai_operation(operation_id: AiOperationId) -> AiOperationResult:
    operation = load_consumable_operation(operation_id)
    request = prepare_disclosed_request(operation)
    result = await invoke_microsoft_ai(request)
    return record_validated_result(operation, result)
```

- `load_consumable_operation` enforces state and one-use consent.
- `prepare_disclosed_request` recreates the canonical bytes and verifies their digest.
- `invoke_microsoft_ai` owns TLS, exact-host validation, redirect rejection, proxy
  disabling, bounds, timeout, and the single network attempt.
- `record_validated_result` validates the strict schema and appends the local outcome.

Do not share a generic “send prompt” method with callers. Analysis and Research have
different input schemas, notices, result schemas, and tool policies.

## Provenance text handling

Use Unicode code-point offsets. JavaScript `String.slice()` operates on UTF-16 code units
and is not a code-point slicer. Keep code-point slicing in a named, tested low-level
function shared through the loopback contract. Do not normalize extracted text after its
offsets and `pageTextChecksum` are produced.

## Platform adapters

Windows and macOS implementations may differ for installation, startup, certificate
provisioning, application-data paths, Keychain/Credential Manager, signing, repair, and
uninstall. A composition root selects one adapter. OS checks do not appear throughout
domain logic.

## Naming

- Use verbs: `submitPaper`, `confirmReviewInspection`, `prepareAiAnalysis`.
- Use question forms for booleans: `isLoopbackHost`, `isSourceSpanExact`.
- Use the same domain names in both stacks: `StudyFinding`, `ReviewInspection`,
  `SynthesisClaim`, `ArtifactSourceRevision`.
- Distinguish `pageIndex` from `pageLabel`, inspection from attention, advice from
  acceptance, and local embeddings from remote generation.
- Use `analysis` and `research` consistently; validation is an Analysis purpose, not a
  third v1 operation.

## Comments and constants

Names and layers explain what code does. Comments explain why a security rule, domain
constraint, or Word workaround exists and link to the invariant or official source.
Extract policy constants from coordinators and keep them in typed configuration.

## Testing style

- Domain tests require no framework, filesystem, Word, or network.
- Contract tests exercise deterministic OpenAPI and canonical request bytes.
- Adapter tests cover SQLite, path and symlink defense, worker recovery, credentials,
  certificate lifecycle, Microsoft AI failures, and Word batching.
- Network tests deny all application-data egress except a consented `MicrosoftAiGateway`
  operation to its exact configured Azure OpenAI host.
- Real Word Desktop tests on supported Windows and macOS complement Office mocks.
