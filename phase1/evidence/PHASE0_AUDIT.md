# Phase 0 precondition audit

Audit date: **2026-08-02 EDT**.

The eight planning documents named by `docs/ROADMAP.md` were read completely before Phase
1.5 implementation. `PHASE0_OWNER_ACCEPTANCE.md` records the project-owner role and accepted
scope.

| Contract area | Result | Consistent terms |
| :--- | :--- | :--- |
| Local owners | PASS | Word add-in owns Office UI; companion owns local state and workers; only `MicrosoftAiGateway` owns later application-data egress. |
| Network boundary | PASS | No hosted application backend; companion is loopback-only; production Office.js is an identified Microsoft platform asset. |
| State names and endpoints | PASS | Final stable origin `https://localhost:4179`; versioned `GET /api/v1/health`; no Phase 2 state. |
| Provenance chain | PASS | Later evidence remains paper/revision/finding/link based; Phase 1 creates none of those entities. |
| Office.js baseline | PASS | Production Office.js CDN, Word Desktop runtime gate, and `WordApi 1.3`. |

## Phase 1.5 origin correction

The original contracts named `https://word-researcher.localhost:4179`. Normal macOS
`getaddrinfo`, `dscacheutil`, and Node resolution returned `EAI_NONAME`/`ENOTFOUND` without
an `/etc/hosts` entry. Direct-SNI evidence therefore did not prove the selected origin.

The Phase 1.5 task explicitly permits one consistent replacement when the original name is
unreliable. The final contracts, settings, certificate SAN policy, manifest, authority
checks, CSP/CORS assumptions, installers, tests, and evidence now name only
`https://localhost:4179`. The normal resolver returned `127.0.0.1` and `::1`, both loopback;
no installer-owned mapping exists. Real Word trust and navigation remain a Phase 1 gate.

## Result

No Phase 0 ownership, network, endpoint, provenance, or Office baseline contradiction
prevents a coherent Phase 1 implementation. Phase 0 contract consistency passes; this does
not satisfy the later real-host feasibility gate.
