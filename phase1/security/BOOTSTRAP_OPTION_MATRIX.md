# Bootstrap option matrix

## Decision status

Date: 2026-08-04 EDT.

The selected v1 model is `VERIFIED EMBEDDED-HOST PROFILE`. Word-specific cryptographic
attestation is not required. The project rejects the mutual Transport Layer Security
(mTLS) spike.

## Evaluation constraints

An acceptable v1 bootstrap option must meet these constraints:

- Operate fully offline after installation
- Require no Microsoft Entra or Office single sign-on (SSO)
- Expose no durable installation secret to JavaScript
- Reject ordinary cross-site requests
- Require exact local request context
- Issue a short-lived session and separate cross-site request forgery (CSRF) token
- Preserve the stable HTTPS loopback origin
- Support restart, repair, and uninstall

The v1 option does not need to distinguish Word from an arbitrary same-user native
process. The local operating-system user account is the trust boundary.

## Option comparison

| Option | Offline | No JavaScript secret | Foreign-web protection | Word attestation | Status | Decision reason |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| Exact `Origin` only | Yes | Yes | Strong when present | No | REJECTED | Real macOS Word omits `Origin` |
| Accept every missing `Origin` | Yes | Yes | No | No | REJECTED | Missing `Origin` alone is not sufficient |
| Verified embedded-host profile | Yes | Yes | Yes, for the browser-origin boundary | No | SELECTED FOR V1 | Matches real Word and rejects incomplete or foreign profiles |
| Durable bearer in JavaScript or manifest | Yes | No | Conditional | No | PROHIBITED | Client assets expose the bearer |
| Microsoft Entra or Office SSO | No | No | Yes | Tenant identity only | PROHIBITED | Bootstrap must operate offline |
| Mutual TLS client certificate | Potentially | Potentially | Potentially | Potentially | REJECTED | Complexity is disproportionate and Office support is unproved |

## Selected option

The policy accepts one of two origin classifications:

1. Accept an exact `Origin` after every remaining control passes.
2. Accept an absent `Origin` only when every verified embedded-host property matches.

The policy rejects every present nonexact `Origin`. The policy does not normalize an
alternate loopback hostname, port, scheme, path, method, or media type into a match.

The missing-`Origin` exception applies only to the bootstrap endpoint. Later mutation
routes keep session, CSRF, Host, Origin-when-present, Fetch Metadata, method, and media
type checks.

## Residual risk

A same-user native process can forge the complete request context. A malicious browser
extension or compromised user profile can also imitate the local task pane. These
threats are outside the v1 browser-origin boundary.

An ordinary foreign webpage cannot set the complete verified Fetch Metadata profile.
The browser also cannot read the companion response through CORS. SameSite cookies,
one-use bootstrap material, session-bound CSRF, exact Host, and loopback binding provide
additional protection.

## Rejected mTLS spike

The project does not continue the mTLS spike. The option has no proved WebView2 or
WKWebView client-certificate behavior. It also adds certificate selection, private-key
policy, repair, rotation, and browser-profile isolation requirements that v1 does not
need.

## Verification requirement

The selected option must pass these groups:

- Exact and unexpected Origin cases
- Complete and incomplete missing-Origin cases
- Host, peer, scheme, method, path, content-type, and Fetch Metadata cases
- Foreign fetch, form, preflight, simple request, and navigation cases
- Session expiry, rotation, CSRF, replay, and cache cases
- Real macOS Word, restart, repair, and uninstall cases
- Windows noninteractive validation

Real Windows Word Desktop remains a mandatory pre-release test.
