# Configuration contract and examples

This document describes typed configuration that a later phase will implement. It is not
an installer, secret file, or generated schema. The managed installer for the local
companion writes production configuration. Domain modules receive narrow values from the composition
root and do not import global settings.

## Task pane bootstrap

The companion can expose only non-secret capabilities:

```json
{
  "apiBasePath": "/api/v1",
  "schemaVersion": 1,
  "hostSupport": "supported",
  "analysisAvailable": false,
  "researchAvailable": false
}
```

The task pane uses same-origin `/api/v1`. Bootstrap never includes filesystem paths,
certificate material, per-install secrets, Azure endpoints, deployment names, API keys,
or access tokens.

## Production companion profile

Illustrative typed YAML spelling:

```yaml
configurationVersion: 1

bootstrap:
  policyVersion: 1
  allowMissingOriginProfiles:
    - word-macos-wkwebview
  profiles:
    word-macos-wkwebview:
      host: localhost:4179
      method: POST
      path: /api/v1/session/bootstrap
      secFetchSite: same-origin
      secFetchMode: cors
      secFetchDest: empty
  sessionLifetimeSeconds: 900

loopback:
  hostname: localhost
  port: 4179
  bindAddresses: [127.0.0.1]
  exactOrigin: https://localhost:4179
  certificateReference: researcher-loopback-leaf
  cookie:
    secure: true
    httpOnly: true
    sameSite: Strict
  csrf:
    separateToken: true

localEmbedding:
  modelId: sentence-transformers/all-MiniLM-L6-v2
  upstreamRevision: REQUIRED_PIN_BEFORE_PHASE_3
  runtime: onnxruntime-cpu
  runtimeVersion: REQUIRED_PIN_BEFORE_PHASE_3
  modelObjectSha256: REQUIRED_PIN_BEFORE_PHASE_3
  tokenizerObjectSha256: REQUIRED_PIN_BEFORE_PHASE_3
  runtimeDownloadAllowed: false

microsoftAi:
  enabled: false
  service: azure-openai-in-microsoft-foundry
  apiFamily: responses
  apiVersion: v1
  resourceHost: REQUIRED_EXACT_RESOURCE.openai.azure.com
  responsePath: /openai/v1/responses
  apiVersionQuery: v1
  authentication:
    type: apiKey
    credentialReference: researcher-azure-openai-api-key
  transport:
    allowedExactHosts: [REQUIRED_EXACT_RESOURCE.openai.azure.com]
    followRedirects: false
    trustEnvironmentProxy: false
    automaticRetries: 0
    verifyTls: true
  persistence:
    store: false
    previousResponseIdAllowed: false
    remoteFilesAllowed: false
    vectorStoresAllowed: false
    conversationsAllowed: false
    batchesAllowed: false
    storedResponsesAllowed: false
    backgroundModeAllowed: false
    contextManagementAllowed: false
    promptCacheControlsAllowed: false
    encryptedReasoningCarryoverAllowed: false
    fileSearchAllowed: false
    codeInterpreterAllowed: false
    mcpAllowed: false
  canonicalization:
    format: RFC8785
    digest: SHA-256
  operations:
    analysis:
      enabled: false
      deploymentName: researcher-analysis
      baseModel: gpt-5
      modelVersion: 2025-08-07
      tools: []
      maxSelectedCharacters: 50000
      maxRequestBytes: 131072
      maxOutputTokens: 2000
      maxResponseBytes: 524288
      timeoutSeconds: 60
      outputSchema: analysis_result_v1
    research:
      enabled: false
      deploymentName: researcher-research
      baseModel: gpt-5
      modelVersion: 2025-08-07
      tools: [web_search]
      maxQueryCharacters: 2000
      maxContextCharacters: 20000
      maxRequestBytes: 131072
      maxToolCalls: 5
      maxOutputTokens: 3000
      maxResponseBytes: 1048576
      timeoutSeconds: 120
      outputSchema: research_result_v1
```

`REQUIRED_PIN_BEFORE_PHASE_3` is a release-blocking placeholder, not an instruction to
download at runtime. Phase 2 records the exact packaged artifact revisions, licenses, and
digests before Phase 3 import/indexing begins.

The listener never substitutes `0.0.0.0`, a wildcard hostname, or another free port. IPv6
`::1` is added only if Phase 1 proves identical host, cookie, and certificate behavior.

The `empty` configuration value is the literal Fetch Metadata value. A missing header
does not match this value. The bootstrap policy contains no secret, identity token, or
Word attestation value.

## Azure provisioning contract

Analysis and Research use Azure OpenAI in Microsoft Foundry's stable Responses API:

```text
POST https://{resource-name}.openai.azure.com/openai/v1/responses?api-version=v1
```

The API supports API-key and Microsoft Entra authentication
([Responses REST reference](https://learn.microsoft.com/en-us/rest/api/microsoft-foundry/azureopenai/responses)).
V1 selects an API key stored in Windows Credential Manager or macOS Keychain and sends it
only in the `api-key` header. The supported Entra alternative uses an
`Authorization: Bearer` header. A string change does not enable this alternative. It
requires a separate sign-in, token-cache, scope, expiration, and sign-out flow.

Before enabling either operation, the organization must provide:

- An Azure subscription and billed Azure OpenAI resource
- Quota and a supported region and deployment type
- Two deployments pinned to `gpt-5` version `2025-08-07`
- Local deployment names that can differ
- An enabled `web_search` capability for the Research deployment and subscription
- The exact resource host and API key credential reference
- Product and organizational approval for the retention, abuse-monitoring, cost, and Research compliance notices

The deployment evidence, not a user-editable label, proves the base model/version. A
model, deployment, endpoint, region, tool, or notice change disables the affected
operation until it is reprobed and redisclosed.

## Analysis request body

Analysis uses no tool and receives only material selected in the local user interface (UI). The semantic
body is:

```json
{
  "background": false,
  "input": [
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "<instruction plus exactly selected material and disclosed metadata>"
        }
      ]
    }
  ],
  "max_output_tokens": 2000,
  "model": "researcher-analysis",
  "store": false,
  "stream": false,
  "text": {
    "format": {
      "type": "json_schema",
      "name": "analysis_result_v1",
      "strict": true,
      "schema": "<the locally versioned analysis_result_v1 JSON Schema object>"
    }
  },
  "tools": []
}
```

The real body contains a JavaScript Object Notation (JSON) Schema object, never the placeholder string. The disclosure
screen renders the full field-for-field payload, including that schema, as the exact
RFC 8785 canonical bytes that will be sent. It also renders the SHA-256 digest.

The local `analysis_result_v1` schema allows only:

```text
adviceItems[]: {kind, statement, selectedMaterialReferences[], rationale, confidence}
limitations[]: string
```

Unknown properties, invalid references, missing fields, extra output items, truncated
JSON, and size/token overruns fail the operation. Structured outputs enforce a supplied
JSON Schema rather than only valid JSON
([Microsoft structured-output guidance](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs)).

## Research request body

Research has a separate schema and consent. The semantic body is:

```json
{
  "background": false,
  "include": ["web_search_call.action.sources"],
  "input": [
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "<approved query plus only the optional selected context shown>"
        }
      ]
    }
  ],
  "max_tool_calls": 5,
  "max_output_tokens": 3000,
  "model": "researcher-research",
  "parallel_tool_calls": false,
  "store": false,
  "stream": false,
  "text": {
    "format": {
      "type": "json_schema",
      "name": "research_result_v1",
      "strict": true,
      "schema": "<the locally versioned research_result_v1 JSON Schema object>"
    }
  },
  "tool_choice": "required",
  "tools": [{"type": "web_search"}]
}
```

The local schema allows only:

```text
discoveries[]: {title, url, citedPassage?, advisorySummary}
limitations[]: string
```

The adapter also requires a completed `web_search_call`. It parses output arrays by
`type`, not position. It validates source URLs and citation annotations. It then
reconciles them with the structured discoveries. No tool call or invalid citations means `failed`, not a
tool-free success. Microsoft documents `web_search` and its response/citation form in the
[stable web-search guidance](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/web-search).

## Consent notices

Every Analysis preview states:

- The exact selected text and metadata that leave the device
- The Azure resource host, deployment, model, version, absence of tools, and hard bounds
- The Azure charges that can apply to input and output usage
- The rule that `store: false` does not justify a zero-retention claim
- The applicable abuse monitoring that can process flagged content
- The rule that one confirmation authorizes one attempt without automatic retry

Every Research preview additionally states:

- The exact query and optional selected context
- The use of `web_search` and the possible tool-call charges
- The separate external processing path for Grounding with Bing Search
- Microsoft's statement that its Data Protection Addendum does not apply to this search data
- Microsoft's statement that processing can cross the compliance or geographic boundary

These Research disclosures are required by Microsoft's
[web-search guidance](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/web-search).
Microsoft's data document describes abuse monitoring for flagged prompts and
completions. Therefore, the UI says “nonpersistent request,” never “zero retention.” See
Microsoft's [data, privacy, and security guidance](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy).

## Credential and path policy

The Azure API key and installer bootstrap credential live only in Keychain or Credential
Manager. SQLite stores credential reference names. The companion retrieves the Azure key
only while executing a consumed consent. It never logs or returns the key.

Platform adapters resolve the database file, content directory, temporary directory,
certificate references, and credential references. Persisted domain records contain
opaque IDs and hashes, not user-specific paths.

## Development-only environment example

An eventual `.env.example` can document local development values but cannot contain a
secret and is not production configuration:

```dotenv
LOOPBACK_HOST=localhost
LOOPBACK_PORT=4179
AZURE_OPENAI_RESOURCE_HOST=example-resource.openai.azure.com
AZURE_OPENAI_ANALYSIS_DEPLOYMENT=researcher-analysis
AZURE_OPENAI_RESEARCH_DEPLOYMENT=researcher-research
AZURE_OPENAI_CREDENTIAL_REFERENCE=researcher-azure-openai-api-key
```

The gateway still sets the HTTP client's environment-proxy inheritance to false. Azure AI
remains disabled unless every required value, credential, deployment proof, disclosure
version, and capability probe is valid.
