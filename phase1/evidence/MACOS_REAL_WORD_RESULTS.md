# macOS real Word Desktop results

Test date: **2026-08-02 EDT**.

## Environment

| Field | Value |
| :--- | :--- |
| Operating system | macOS 26.5.2 (25F84), arm64 |
| Word | 16.109.3, bundle build 16.109.26053122 |
| Update channel | Unknown; not exposed by inspected local AutoUpdate preference |
| Installation type | `/Applications/Microsoft Word.app`; license/deployment source not inspected |
| Spike type | Unsigned local feasibility scripts and development sideload manifest |
| Final stable URL | `https://localhost:4179/taskpane` |

## Safe preflight and obstruction

Read-only automation reported Word running with one document and one unsaved document. The
document name and contents were not collected. The task requires a full Word quit before
testing and forbids closing or modifying unsaved user content. Word was therefore not quit,
restarted, or manipulated.

Final installer state after cleanup was clean:

- listener: absent;
- LaunchAgent and plist: absent;
- active manifest: absent;
- application-data directory: absent;
- `WordResearcher.Phase1` credential: absent;
- relevant trust certificate: absent; and
- installer-owned hostname mapping: absent.

Normal final-hostname resolution returned `127.0.0.1` and `::1`; both are loopback. The
rejected `word-researcher.localhost` candidate returned `EAI_NONAME`/`ENOTFOUND` and was
removed from every final contract.

## Required sequence

| Step | Result | Evidence or blocker |
| :--- | :--- | :--- |
| Fresh install | BLOCKED | Safe full-quit precondition was not met; final-origin install was not represented as complete. |
| Certificate creation | PASS | Final SAN/uniqueness/key-permission adapter tests passed for `localhost`. |
| User trust | BLOCKED | Earlier trust attempt exposed the required macOS authentication dialog; no final-origin trust was installed. |
| Manifest installation | BLOCKED | Final-origin manifest was not installed after the safe stop. |
| Word launch | BLOCKED | Word was already open with unsaved content and was not restarted. |
| Add-in menu path | BLOCKED | Not reached; no menu path is invented. |
| Task pane opens | BLOCKED | Not reached. |
| Stable URL navigation | BLOCKED | Not reached in Word. |
| Certificate warning absent | BLOCKED | Not observed in WKWebView. |
| Production Office.js | BLOCKED | Static HTML is correct; no real Word request/readiness event was observed. |
| `Office.onReady()` | BLOCKED | Not observed in Word. |
| Word host confirmed | BLOCKED | Not observed in Word. |
| `WordApi 1.3` | BLOCKED | Unit gate passes; real Word result unavailable. |
| Bootstrap/session | BLOCKED | Protocol tests pass; no real task-pane cookie trace exists. |
| Generated client `/health` | BLOCKED | Protocol passes; installed production-origin and real Word calls were not run. |
| Restart behavior | BLOCKED | Safe quit/restart not available. |
| Repair twice | BLOCKED | Not executed for the final origin. |
| Full uninstall | BLOCKED | Partial failure-path cleanup passed, but a complete final-origin installation never existed. |
| Add-in absent after uninstall | BLOCKED | Final Word restart was unavailable. |

## Conclusion

macOS application feasibility is **BLOCKED**. The stable-origin design now passes normal
resolver checks, but it has not survived real Word WKWebView navigation, trust, Office.js,
session, or authenticated health. No user document was modified or closed.

## Continuation run — superseding real-host result

Run date: **2026-08-02 EDT**. The user fully quit Word, so the blocked precondition above was
cleared. Prior blocked evidence is retained; this section is the current result.

### Environment and document safety

- macOS 26.5.2 (25F84), arm64.
- Microsoft Word 16.109.3; bundle build `16.109.26053122`; AppleScript build
  `16.109.531`; update channel unknown.
- Unsigned local feasibility installer and development sideload manifest.
- Only blank, unsaved test documents were created. No text was inserted, no document was
  saved, and no existing document was opened, changed, closed, or overwritten.

### Pre-install, install, and production origin

The clean-state audit found no Word process, companion, port-4179 listener, LaunchAgent,
active manifest, application data, credential, relevant login/system certificate, or
installer hostname mapping. `localhost` resolved only to `127.0.0.1` and `::1`.

Fresh install, user trust, loopback-only listener, certificate hostname/chain, private-key
permissions, Keychain credential, LaunchAgent startup, task-pane assets, and manifest all
passed. Normal `https://localhost:4179/taskpane` returned HTTP 200 without TLS bypass. The
exact-source installed-production test passed bootstrap, cookies, CSRF, session, and the
generated-client `/health` request.

### Actual Word sequence

Exact menu path: **Word ribbon → Add-ins → Developer Add-ins → Word Researcher
Feasibility**. The task pane opened at the manifest's final URL
`https://localhost:4179/taskpane` without a recovery or certificate warning.

The rendered React state proves the startup sequence reached the companion connection
step: production Office.js loaded, `Office.onReady()` resolved, host `Word` and desktop
platform `Mac` passed, and `WordApi 1.3` passed. The generated client then attempted the
bootstrap operation.

The request failed closed before session establishment. Sanitized companion evidence:

```text
request_rejected category=boundary reason=browser_context
origin=missing fetch_site=same-origin fetch_mode=cors fetch_destination=empty
```

Authority and loopback checks execute before browser-context checks, so reaching this
reason also proves exact `Host: localhost:4179` and a loopback client. No cookie, CSRF value,
secret, URL query, document text/name, or user identity was logged. The pane rendered:

```text
Local companion unavailable
The protected local health check could not be completed.
```

### Current matrix

| Step | Result | Current evidence |
| :--- | :---: | :--- |
| Fresh install | PASS | Complete corrected final-origin install. |
| Trusted localhost TLS | PASS | Normal resolution, verified chain and hostname, no warning. |
| Manifest / add-in discoverability | PASS | Developer add-in listed at the exact menu path. |
| Task pane opens | PASS | Persistent 350-point pane titled `Word Researcher Feasibility`. |
| Production Office.js / `Office.onReady()` | PASS | React connection state was reached only after readiness. |
| Word Desktop/macOS host | PASS | Unsupported-host state was not rendered. |
| `WordApi 1.3` | PASS | Missing-capability state was not rendered. |
| Bootstrap | FAIL | Real Word omitted required Origin; strict boundary returned 403. |
| Local session | FAIL | Not established after boundary rejection. |
| Generated-client `/health` from Word | FAIL | Not attempted because bootstrap failed. |
| Restart sequence | BLOCKED | Per task control, it follows only a passing initial Word sequence. |
| Two repair acceptance passes | BLOCKED | Diagnostic repairs are not substituted for post-pass acceptance. |
| Full uninstall | PASS | All active/private state removed. |
| Add-in absent after uninstall | PASS | Fresh Word launch showed no Word Researcher entry. |

### Conclusion

macOS real-host verification is **FAIL**. The installed origin, TLS, Office.js, host, and
capability portions pass, but ROADMAP.md requires exact Origin enforcement and Word's real
WKWebView omitted Origin on the bootstrap fetch. No security check was weakened. A formal
Phase 0/security decision and a newly proved bootstrap design are required before another
Phase 1 run; Phase 2 must not begin.
