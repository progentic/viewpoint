# Phase 1.5 network observations

Observation date: **2026-08-02 EDT**.

No full Word/task-pane packet observation exists for the final origin. The classifications
below separate observed development traffic from static conclusions and blocked runtime
evidence.

## 1. Local companion traffic

- The direct HTTPS bind/certificate test listened only on `127.0.0.1:4179` and completed a
  trusted SNI/authority request for `localhost`.
- The protocol test listened only on `127.0.0.1:4179` and completed bootstrap plus
  authenticated `/api/v1/health` under explicitly labeled substituted HTTP transport.
- The final hostname resolved normally to `127.0.0.1` and `::1`, both loopback. No
  `/etc/hosts` entry or installer-owned mapping existed.
- Boundary tests rejected foreign Host, foreign Origin, absent/invalid Fetch Metadata,
  non-loopback client, missing/invalid/expired/replayed session material, and oversized
  requests.
- No paper, document, research, AI, or user-content route exists in Phase 1.

These observations prove local test transports only. They do not prove final installed
WKWebView behavior.

## 2. Microsoft Office.js platform traffic

The task-pane HTML references production Office.js only at
`https://appsforoffice.microsoft.com/lib/1/hosted/office.js`; architecture verification
confirmed it is in `<head>` and absent from the local bundle. A real Word task pane did not
open, so no final Office.js request was captured. Consequently, no claim is made about the
headers, redirects, or payload of that blocked request.

## 3. Microsoft validation and update traffic

- Manifest validation contacted Microsoft's acceptance service and reported the final
  manifest valid.
- A prior Word launch displayed Microsoft AutoUpdate behavior. It is classified as
  Microsoft platform traffic; it is not attributed to the add-in.

No endpoint-level packet trace was retained for the AutoUpdate event.

## 4. Installer and development dependency traffic

- Static security verification found no general external HTTP client in companion or
  installer source. macOS installer `curl` use is restricted to the exact local task-pane
  URL; Windows installers contain no downloader.
- `npm ci`, npm audit, Python dependency setup, GitHub authentication, and manifest
  validation used external development services before installer execution. These are
  documented development/build operations, not hidden installed-application dependencies.
- The incomplete macOS trust attempt required only an operating-system authentication
  dialog. No insecure fallback or downloaded trust material was used.

## 5. Unexplained traffic

No unexplained application destination was observed, but the observation window did not
include final-origin installation, Word restart, task-pane load, Office.js readiness,
session bootstrap, health, repair, or full uninstall. Therefore “no unexplained runtime
traffic” is **BLOCKED**, not proved.

## Required conclusion

The source and automated test surface keeps application traffic local and documents the
Office.js CDN. The complete installation/Word/session/health network requirement remains
**BLOCKED** until a safe real Word run captures final-origin navigation without user content
or secret values.

## Continuation observations — actual Word host

This section supersedes the earlier unavailable observation window.

### Loopback companion

- Fresh and exact-source final installs listened only on IPv4 `127.0.0.1:4179`.
- Normal `localhost` resolution returned `127.0.0.1` and `::1`; the trusted system client
  selected `127.0.0.1` without direct-IP/SNI substitution.
- Task-pane HTTP, bootstrap attempts, installed generated-client health, safe negative
  probes, repair readiness, and shutdown used the stable loopback origin.
- Missing session returned 401; fake invalid session returned 401; unexpected Origin,
  unexpected Host, and cross-site Fetch Metadata returned 403; an oversized request
  returned 413.
- The real Word bootstrap was rejected with exact authority and loopback already passed,
  `Origin` missing, `Sec-Fetch-Site=same-origin`, `Sec-Fetch-Mode=cors`, and
  `Sec-Fetch-Dest=empty`.

### Microsoft platform traffic

The task pane reached the React connection step, which is possible only after the
production Office.js script loaded and `Office.onReady()` resolved. Word had established
IPv6 TLS sockets to `2603:1036:2401:1::14` and `2603:1036:2405:1::4`; these were classified
as Microsoft Office/platform traffic and were not all attributed to the add-in. The limited
socket snapshot did not retain payloads or establish which address served Office.js.

Microsoft's manifest validation gateway was contacted by the documented development
validator. One initial sandboxed validation attempt failed DNS; the authorized retry
passed. No runtime dependency downloader was invoked.

### Installer, repair, and uninstall

Static verification and observed installer output found no external installer downloader.
The macOS installer used system `curl` only for local readiness. Trust was created locally
and installed through the visible operating-system flow. Repair preserved local trust and
private material. Uninstall removed the listener and later local connection attempts
failed; it made no dependency download.

### Conclusions

- Companion/application data traffic remained on loopback.
- No paper, research, document, AI, or user-payload API exists in Phase 1, so no research
  payload left the device.
- Production Office.js loaded from the only configured external task-pane script URL.
- No undocumented installer dependency was downloaded.
- No unexplained add-in/application destination was observed.

This was endpoint/socket and safe application-log observation, not a retained full packet
capture. Because bootstrap failed and restart/two-repair acceptance did not run, the
complete network matrix remains **BLOCKED**, despite the conclusions above for the observed
steps.
