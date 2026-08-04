# Phase 1.5 real-host feasibility matrix

Test date: **2026-08-02 EDT**. Only `PASS`, `FAIL`, `BLOCKED`, `N/A`, and
`PASS — LIMITED` are used. A runner result is never treated as Word Desktop evidence.

## Environments

| Field | macOS real host | Windows CI runner | Windows real host |
| :--- | :--- | :--- | :--- |
| OS | macOS 26.5.2 (25F84), arm64 | Intended `windows-2025`; no run | Unavailable |
| Word | 16.109.3 (16.109.26053122) | N/A | Unavailable |
| Update channel | Unknown | N/A | Unavailable |
| Installation | Unsigned feasibility scripts/development sideload | Intended isolated temporary lifecycle | Unavailable |
| Policy context | Login Keychain, user trust dialog, TCC/Finder, LaunchAgents, WKWebView | Unknown; no run | Unknown |

## Matrix

| Operation | macOS real host | Windows CI runner | Windows real host | Evidence or limitation |
| :--- | :---: | :---: | :---: | :--- |
| Fresh companion installation | BLOCKED | BLOCKED | BLOCKED | Final-origin sequence did not run; final workflow did not run; no Windows host. |
| Certificate creation | PASS | BLOCKED | BLOCKED | Unique final `DNS:localhost` certificate/key tests passed on Mac only. |
| Certificate trust | BLOCKED | BLOCKED | BLOCKED | macOS auth boundary observed but final trust not installed; Windows unrun. |
| Stable hostname resolution | PASS | BLOCKED | BLOCKED | Mac normal resolver returned only `127.0.0.1`/`::1`; Windows unrun. |
| Manifest installation or registration | BLOCKED | BLOCKED | BLOCKED | Final-origin manifest not installed; Windows lifecycle unrun. |
| Word launch | BLOCKED | N/A | BLOCKED | Unsaved Mac document prohibited restart; a runner is not a Word host. |
| Add-in discoverable in Word | BLOCKED | N/A | BLOCKED | Not observed on either real host. |
| Task pane opens | BLOCKED | N/A | BLOCKED | Not observed on either real host. |
| Stable HTTPS origin loads | BLOCKED | N/A | BLOCKED | Direct probe passes, but no real task pane. |
| Office.js initializes | BLOCKED | N/A | BLOCKED | Static/unit checks only. |
| Word host confirmed | BLOCKED | N/A | BLOCKED | Runtime host gate not observed in Word. |
| `WordApi 1.3` confirmed | BLOCKED | N/A | BLOCKED | Unit capability gate only. |
| Bootstrap succeeds | BLOCKED | BLOCKED | BLOCKED | Local protocol passed; final Windows run and real hosts did not. |
| Session established | BLOCKED | BLOCKED | BLOCKED | Same limitation as bootstrap. |
| Generated client `/health` | BLOCKED | BLOCKED | BLOCKED | Protocol PASS is not installed-origin or Word evidence. |
| Predictable startup | BLOCKED | BLOCKED | BLOCKED | Final LaunchAgent and Scheduled Task lifecycles unproved. |
| Repair | BLOCKED | BLOCKED | BLOCKED | No final-origin Mac repair; Windows job unrun. |
| Uninstall | BLOCKED | BLOCKED | BLOCKED | Partial Mac failure cleanup passed, not a full final install; Windows unrun. |
| Credential cleanup | BLOCKED | BLOCKED | BLOCKED | Partial Mac cleanup only; Windows unrun. |
| Certificate cleanup | BLOCKED | BLOCKED | BLOCKED | Partial Mac cleanup only; Windows unrun. |
| No undocumented installer download | BLOCKED | BLOCKED | BLOCKED | Static scan passes, but full observed install/Word windows are incomplete. |
| Network observations complete | BLOCKED | BLOCKED | BLOCKED | No final real Word capture and no Windows run/host. |

## Interpretation

The final stable-hostname correction passes normal resolution on macOS. It has not been
validated in Word WKWebView, and the remaining matrix prevents conditional closure.

## Continuation matrix — current result

This matrix supersedes the unavailable macOS-host result above while preserving it as run
history.

| Operation | macOS real host | Windows CI runner | Windows real host | Current evidence or limitation |
| :--- | :---: | :---: | :---: | :--- |
| Fresh companion installation | PASS | BLOCKED | BLOCKED | Corrected runtime staged and started on Mac; no Windows run/host. |
| Certificate creation and trust | PASS | BLOCKED | BLOCKED | Per-install `DNS:localhost` chain trusted normally on Mac. |
| Stable hostname resolution | PASS | BLOCKED | BLOCKED | Only loopback addresses on Mac. |
| Manifest installation | PASS | BLOCKED | BLOCKED | One active Mac development manifest; Windows unrun. |
| Word launch | PASS | N/A | BLOCKED | Blank unsaved Mac test document only. |
| Add-in discoverable | PASS | N/A | BLOCKED | Ribbon → Add-ins → Developer Add-ins. |
| Task pane opens | PASS | N/A | BLOCKED | Correct title and final local URL, no certificate warning. |
| Production Office.js initializes | PASS | N/A | BLOCKED | React connection step reached after `Office.onReady()`. |
| Word host confirmed | PASS | N/A | BLOCKED | Unsupported-host state not rendered. |
| `WordApi 1.3` confirmed | PASS | N/A | BLOCKED | Missing-capability state not rendered. |
| Bootstrap succeeds | **FAIL** | BLOCKED | BLOCKED | Mac WKWebView omitted mandatory Origin; strict 403. |
| Session established | **FAIL** | BLOCKED | BLOCKED | Bootstrap failure prevented session creation. |
| Generated client `/health` from Word | **FAIL** | BLOCKED | BLOCKED | Not called after failed bootstrap. |
| Installed generated-client `/health` | PASS | BLOCKED | BLOCKED | Exact-source Mac installed-origin test passed outside Word. |
| Predictable restart | BLOCKED | BLOCKED | BLOCKED | Post-pass restart sequence was not authorized by the failed initial sequence. |
| Two repair acceptance passes | BLOCKED | BLOCKED | BLOCKED | Diagnostic repairs are not acceptance passes. |
| Full uninstall | PASS | BLOCKED | BLOCKED | All Mac active/private state removed; Windows unrun. |
| Credential/certificate cleanup | PASS | BLOCKED | BLOCKED | Login/system relevant cert counts zero; credential absent. |
| Add-in absent after uninstall | PASS | N/A | BLOCKED | Fresh Word launch no longer listed it. |
| No undocumented installer download | PASS | BLOCKED | BLOCKED | Observed/static Mac installer result; Windows unrun. |
| Network observations complete | BLOCKED | BLOCKED | BLOCKED | Mac session/restart/repair windows incomplete; no Windows evidence. |

macOS real-host verification is **FAIL**, not merely unavailable. Overall Phase 1 remains
**BLOCKED**.
