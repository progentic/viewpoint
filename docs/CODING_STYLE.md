# Coding style

## Goal

Minimize cognitive load through explicit ownership, narrow interfaces, and the Single
Level of Abstraction rule. `INVARIANTS.md` is normative. Code that makes an invariant
unenforceable is incorrect even when it is locally convenient.

## Documentation language

Project documentation uses ASD-STE100 Issue 9 as its primary language standard. Project
terminology and formal technical content are approved technical terms. Security accuracy
and formal meaning take precedence over vocabulary simplification. Markdown follows this
project guide.

The governing reference is ASD-STE100 Issue 9, Part 1, Writing Rules.

Apply this standard to:

- The eight governance documents in `docs/`
- Phase completion reports
- Installer instructions
- Operator procedures
- Security decision records

The standard does not control these formal elements:

- Source code and identifiers
- API paths and protocol names
- JSON, YAML, SQL, and regular expressions
- Error codes and formal schema values
- Product names and vendor names
- Standards citations and direct quotations
- Cryptographic formulas

Classify each section before editing it. A procedural section tells a person or an agent
what to do. A descriptive section explains architecture, policy, state, ownership, or
behavior.

Use these sentence rules:

- Use an imperative command for procedural text.
- Put one instruction in each procedural sentence.
- Keep a procedural sentence within 20 words when practical.
- Put one topic in each descriptive sentence.
- Keep a descriptive sentence within 25 words when practical.
- Use active voice.
- Name the owner of each action.
- Include the subject and the verb.
- Do not use a contraction.
- Do not use a semicolon.
- Put a condition before its command.
- Use the same term for the same object.

Passive voice is permitted in descriptive text only when the agent is unknown or
irrelevant. Do not shorten a sentence when the shorter form changes a security or
technical meaning.

### Project terminology

The following terms are approved technical nouns or technical verbs:

| Approved term | Meaning |
| :--- | :--- |
| Local companion | Installed loopback process that owns the local API and durable coordination |
| Companion | Approved short form for local companion after its first use |
| Task pane | Office add-in user interface that Microsoft Word hosts |
| Application-data directory | Per-user directory that stores mutable local application data |
| Installation directory | Directory that stores installed program files and static assets |
| Content store | Local adapter that stores content-addressed bytes |
| Review inspection | Record of one confirmed presentation for one source span |
| Review decision | Ordered human acceptance or rejection record |
| Suggestion | Immutable advisory item that requires human review |
| Study finding | Accepted single-paper observation |
| Synthesis claim | Researcher-approved statement that uses evidence from multiple papers |
| Source span | Exact range in immutable extraction text |
| Extraction version | Immutable result from one identified extraction process |
| Corpus snapshot | Immutable record of all paper revisions considered by one gap test |
| Artifact snapshot | Immutable payload and its typed source revisions |
| Bootstrap request | Request that starts a protected local session |
| Embedded-host profile | Exact request properties that Phase 1 verified for one Office webview |
| Bootstrap classification | Decision that classifies the bootstrap request origin and profile |
| Bootstrap policy | Typed rules that permit or reject one bootstrap request |
| Browser-origin boundary | V1 protection boundary for remote webpages and browser request contexts |
| Session cookie | Short-lived HTTP-only proof of a protected local session |
| `MicrosoftAiGateway` | Sole adapter for application-data calls to Microsoft artificial intelligence (AI) |

Approved technical verbs include:

- Bootstrap
- Validate
- Canonicalize
- Hash
- Persist
- Reconcile
- Index
- Render
- Install
- Uninstall

Use `local companion` at the first occurrence in a document. Use `companion` after that
definition. Do not use `service`, `daemon`, or `backend` for this component.

These terms have different meanings and are not synonyms:

- Suggestion, advice, and result
- Validation, approval, and acceptance
- Finding, claim, evidence, and discovery
- Installation directory and application-data directory

Define an unfamiliar formal term at its first use. Define an acronym at its first use in
each document. A formal identifier can remain unchanged when prose uses its approved
plain-language term.

Avoid a noun phrase that has more than three words. An official technical term can exceed
this limit. Define a shorter form after the first full occurrence when practical.

### Procedures, lists, and failures

Write a procedure as numbered commands. Use one command in each numbered item. Separate
independent commands into separate items.

Introduce each list with a complete sentence and a colon. Start each item with an
uppercase letter. Use a period only when the item is a complete sentence. Do not end a
list item with a semicolon.

Put a condition before the required action. A failure rule identifies these elements:

- Condition
- Detector
- Required action
- Visible result
- Recorded evidence

### Normative and evidence terms

Use these normative terms consistently:

| Term | Use |
| :--- | :--- |
| Must | Mandatory requirement |
| Must not | Prohibited behavior |
| Should | Recommendation with a permitted exception |
| Can | Capability or possibility |
| Will | Future behavior, not a requirement |

Do not use `may` for a normative requirement. Use `must` or `must not` for an enforceable
rule.

Use these labels for evidence status:

- Observed
- Verified
- Inferred
- Assumed
- Not tested
- Blocked
- Failed
- Passed
- Passed with limitations

An observation states only what the test showed. An inference states the bounded
conclusion that the evidence supports. Do not convert one host result into a universal
platform claim.

Bound each security statement to a named control, scope, and evidence source. Also state
what the control does not protect when that limit is material. Do not use absolute claims
such as `fully secure`, `zero risk`, `cannot be bypassed`, or `guaranteed private`.

### Paragraphs and precedence

Use one topic in each paragraph. Start each descriptive paragraph with its topic. Keep a
paragraph within six sentences when practical.

Apply this precedence order:

1. Preserve security and correctness.
2. Preserve formal schema and protocol terms.
3. Use the project terminology.
4. Apply ASD-STE100 Issue 9.
5. Use general American English.
6. Apply the Markdown conventions in this guide.

### Documentation review checklist

For each governance-document review:

1. Confirm that each section has one purpose.
2. Name the owner of each action.
3. Use normative terms consistently.
4. Use one technical term for each concept.
5. Define each acronym at first use.
6. Put one main idea in each sentence.
7. Start each procedure with an imperative verb.
8. Check the practical sentence limits.
9. Remove semicolons and contractions from prose.
10. Replace ambiguous pronouns with explicit nouns.
11. Separate procedural lists from descriptive lists.
12. Remove unsupported universal claims.
13. Separate evidence from inference.
14. Confirm that formal code and identifiers are unchanged.

## Single Level of Abstraction

Every function operates at one level:

- **Policy / coordination** reads like a use-case summary and calls domain operations.
- **Domain logic** makes one business decision without raw framework or storage calls.
- **Implementation / infrastructure** performs serialization, hashing, storage,
  filesystem, credential, Office.js, Portable Document Format (PDF), embedding-runtime,
  or Microsoft API mechanics.

Callers appear physically above callees in step-down order. A policy function contains no
raw API calls, Structured Query Language (SQL), regex, string slicing, path construction, magic number, or complex
boolean expression. Functions should usually fit within 20 lines with nesting depth two.
A name that needs “and” is a signal to split responsibilities.

## Stable boundaries

Use narrow interfaces for these volatile capabilities:

- Generated loopback client
- SQLite unit of work and local content store
- Durable job runner, PDF extractor, optical character recognition (OCR) engine, and local
  embedding index
- `MicrosoftAiGateway` with separate `analysis` and `research` request types
- Clock, identifier generator, canonical serializer, and digest service
- Operating-system credential store, platform paths, installer, certificate manager, and startup manager
- Word application-object adapter and Office Common API settings adapter

Domain code depends on these capabilities, never on FastAPI, SQLite, Office.js, an HTTP
client, or a Microsoft software development kit (SDK). Avoid speculative factories and catch-all `utils` modules.

V1 packages no local generative model. Use `localEmbeddingModel` only for the pinned,
offline embedding dependency and never as a synonym for generation or Microsoft AI.

## Module size

Split by responsibility before a file becomes difficult to understand. Treat 400 lines
as a review prompt. Files above 800 executable lines require an architecture
justification. Generated clients are exempt and live in an explicitly generated folder.

## TypeScript task pane

Use these task pane rules:

- Enable `strict`.
- Forbid `any` and unchecked non-null assertions.
- Give exported functions explicit return types.
- Let React coordinate presentation.
- Place loopback and Word mechanics in adapters.
- Use the generated OpenAPI client and same-origin `/api/v1` routes.
- Load Office.js globally from Microsoft's production content delivery network (CDN) in
  the HyperText Markup Language (HTML) `<head>`.
- Do not import or bundle Office.js.
- Do not use preview Office.js or preview type packages.
- Keep Word application-object mutations in a Word adapter, within `Word.run()`, and
  finish them with a batched `context.sync()` outside insertion loops.
- Keep document-settings operations in a separate Office Common API adapter.
- Call `Office.context.document.settings.set()`.
- Consider persistence complete only after the `saveAsync()` callback succeeds.
- Do not put a document-settings operation inside `Word.run()`.
- Use stable `WordApi 1.3` as the baseline.
- Guard any newer stable API with an explicit capability check.
- Do not use Node built-ins, filesystem APIs, credentials, or Microsoft AI SDKs.
- Do not call external application APIs.
- Permit only the companion to own Microsoft AI egress.
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

Use these companion rules:

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
static dependency rule rejects general-purpose HTTP clients elsewhere. The rule permits
the loopback framework. It can also permit a separately designed and documented installer
update capability.

## Microsoft AI adapter

Keep policy, operation logic, and HTTP mechanics separate:

```py
async def execute_ai_operation(operation_id: AiOperationId) -> AiOperationResult:
    operation = load_consumable_operation(operation_id)
    request = prepare_disclosed_request(operation)
    result = await invoke_microsoft_ai(request)
    return record_validated_result(operation, result)
```

The low-level functions have these responsibilities:

- `load_consumable_operation` enforces state and one-use consent.
- `prepare_disclosed_request` recreates the canonical bytes and verifies their digest.
- `invoke_microsoft_ai` owns Transport Layer Security (TLS), exact-host validation, redirect rejection, proxy
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

Windows and macOS implementations can differ for installation, startup, certificate
provisioning, application-data paths, Keychain/Credential Manager, signing, repair, and
uninstall. A composition root selects one adapter. Operating-system checks do not appear throughout
domain logic.

## Naming

Use these naming rules:

- Use verbs: `submitPaper`, `confirmReviewInspection`, `prepareAiAnalysis`.
- Use question forms for booleans: `isLoopbackHost`, `isSourceSpanExact`.
- Use the same domain names in both stacks: `StudyFinding`, `ReviewInspection`,
  `SynthesisClaim`, `ArtifactSourceRevision`.
- Distinguish `pageIndex` from `pageLabel`, inspection from attention, advice from
  acceptance, and local embeddings from remote generation.
- Use `analysis` and `research` consistently.
- Treat validation as an Analysis purpose, not a third v1 operation.

## Comments and constants

Names and layers explain what code does. Comments explain why a security rule, domain
constraint, or Word workaround exists and link to the invariant or official source.
Extract policy constants from coordinators and keep them in typed configuration.

## Testing style

Use these testing rules:

- Domain tests require no framework, filesystem, Word, or network.
- Contract tests exercise deterministic OpenAPI and canonical request bytes.
- Adapter tests cover SQLite, path and symlink defense, worker recovery, credentials,
  certificate lifecycle, Microsoft AI failures, and Word batching.
- Network tests deny all application-data egress except a consented `MicrosoftAiGateway`
  operation to its exact configured Azure OpenAI host.
- Real Word Desktop tests on supported Windows and macOS complement Office mocks.
