# Bootstrap authorization decision

## Decision status

| Field | Value |
| :--- | :--- |
| Date | 2026-08-04 EDT |
| Security reviewer | UNASSIGNED — Product Security Owner |
| Office-platform reviewer | UNASSIGNED — Microsoft Office Add-in Platform Owner |
| Architecture approver | UNASSIGNED — Project Architecture Owner |
| Product approver | UNASSIGNED — Product Owner |
| Word-specific cryptographic attestation | NOT REQUIRED FOR V1 |
| Mutual Transport Layer Security (mTLS) spike | REJECTED |
| Bootstrap authorization model | VERIFIED EMBEDDED-HOST PROFILE |
| Same-user native malware | OUT OF SCOPE |
| Offline operation | REQUIRED |
| Microsoft Entra and Office single sign-on (SSO) | PROHIBITED FOR BOOTSTRAP |
| Implementation authorization | APPROVED FOR PHASE 1.6 |
| Phase 1 status before verification | BLOCKED |

This decision supersedes the proposed 2026-08-03 decision. The prior decision required
an mTLS spike and kept the exact-`Origin` guard unchanged. The new decision reduces the
v1 trust boundary and authorizes the narrow Phase 1.6 implementation.

## Product security objective

The local companion protects against remote network clients, ordinary foreign webpages,
cross-site request forgery, invalid local sessions, and unsafe application behavior. It
does not cryptographically authenticate Microsoft Word as the client.

The local operating-system user account is the v1 trust boundary. A same-user native
process, malicious browser extension, or compromised user profile can imitate local
request context. These threats are outside the v1 browser-origin boundary.

The product does not claim Word attestation, same-user malware resistance, perfect
browser isolation, zero risk, or unbypassable local authorization.

## Decision

The bootstrap endpoint uses a verified embedded-host profile. The policy classifies the
request before the companion creates a session.

Use this classification:

```text
Origin present and exact:
    Continue to the remaining bootstrap controls.

Origin present and unexpected:
    Reject.

Origin absent:
    Accept only when the verified Word embedded-host profile passes.
```

Missing `Origin` alone is not sufficient. The accepted profile is a strict conjunction
of observed request properties. An unexpected `Origin` always fails. The exception
applies only to `POST /api/v1/session/bootstrap`.

## Verified macOS Word profile

The real macOS Word test observed this profile:

| Property | Required value |
| :--- | :--- |
| Host | `localhost:4179` |
| Peer | Operating-system loopback |
| Scheme | `https` |
| Method | `POST` |
| Path | `/api/v1/session/bootstrap` |
| `Sec-Fetch-Site` | `same-origin` |
| `Sec-Fetch-Mode` | `cors` |
| `Sec-Fetch-Dest` | `empty` |
| Content type | `application/json` |
| Origin | Absent |

A missing field does not match an expected field. An alternate scheme, port, hostname,
method, path, media type, or Fetch Metadata value fails.

## Required controls

The bootstrap route must require these controls:

- Exact Host
- Loopback peer
- HTTPS at the installed origin
- Exact method and path
- Exact bootstrap media type
- Verified Fetch Metadata tuple
- No redirect
- Non-cacheable response
- Restrictive cross-origin resource sharing (CORS) behavior
- Restrictive content security policy (CSP)
- Short-lived replay-safe bootstrap material
- Safe categorical errors

A successful bootstrap can create only these values:

- One short-lived `Secure`, `HttpOnly`, `SameSite=Strict` session cookie
- One separate session-bound cross-site request forgery (CSRF) token

Every later mutation must require the valid session, valid session-bound CSRF token,
exact Host, valid Origin when present, valid Fetch Metadata, expected method, and expected
content type.

## Offline constraint

> Bootstrap must operate fully offline after installation. It must not require Microsoft
> Entra, Office SSO, tenant identity, or any remote identity service.

Bootstrap must not depend on these systems:

- Microsoft Entra
- Office SSO
- Azure application registration
- Microsoft identity tokens
- Internet availability
- Tenant authentication
- Remote token validation

This constraint does not prohibit optional Phase 5 Azure artificial intelligence (AI)
operations. Those operations remain separate, consented, and unavailable while offline.

## mTLS rejection

The project rejects the mTLS spike because its complexity is disproportionate to the v1
product risk. Office webview support for protected client-certificate selection remains
unproved. The project does not require Word-specific cryptographic attestation for v1.

The project must not continue the mTLS spike as an active Phase 1 design. A future change
to the trust boundary requires a new architecture decision.

## Secret and log restrictions

No durable installation secret can enter these locations:

- Task pane JavaScript
- Browser storage
- Hypertext Markup Language (HTML)
- Manifest content
- Uniform resource locator (URL)
- Log content
- Application programming interface (API) response

Logs can contain only categorical result, policy version, profile identifier, and event
time. Logs must not contain cookies, CSRF values, request bodies, document content,
secret values, local paths, full raw headers, or certificate private material.

## Safe reason codes

The Phase 1.6 bootstrap contract uses these codes:

```text
bootstrap_origin_unexpected
bootstrap_profile_not_allowed
bootstrap_host_invalid
bootstrap_peer_not_loopback
bootstrap_fetch_metadata_invalid
bootstrap_method_invalid
bootstrap_path_invalid
bootstrap_content_type_invalid
bootstrap_replay_rejected
bootstrap_session_failed
```

## Evidence and approval boundary

The implementation must pass policy, browser-origin, session, real macOS Word, restart,
repair, uninstall, network, and Windows noninteractive checks. A GitHub-hosted Windows
runner is not real Windows Word evidence.

Reviewer fields remain `UNASSIGNED` until a person accepts each role. Product scope
approval does not replace the security or Office-platform reviewer.

Evidence anchors are:

- `companion/src/researcher_companion/api/bootstrap_policy.py`
- `companion/src/researcher_companion/api/bootstrap_adapter.py`
- `companion/src/researcher_companion/application/bootstrap.py`
- `companion/src/researcher_companion/session.py`
- `phase1/evidence/MACOS_REAL_WORD_RESULTS.md`
- `docs/INVARIANTS.md`
