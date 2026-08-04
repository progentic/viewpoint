# Phase 1 exit decision

## Project discontinuation — 2026-08-04

The project is **DISCONTINUED**. The selected Word add-in and native companion
architecture did not pass the cross-platform session feasibility gate within the
available budget. Phase 1 remains blocked. Phase 2 did not start. Preserve this
repository for reference and do not spend additional project funds on the current
architecture.

The following records preserve the earlier feasibility decisions and evidence.

## BLOCKED

Phase 1 does not pass and is not conditionally closed.

## Decision basis

- Phase 0 contracts and owner-acceptance artifact are coherent.
- The unreliable `word-researcher.localhost` candidate was replaced consistently with
  `https://localhost:4179`; normal macOS resolution now returns only loopback addresses.
- Locked installation, lint, type checks, unit tests, build, deterministic contracts,
  manifest validation, protocol transport, direct HTTPS bind/certificate, security scan,
  and action-pin checks pass locally.
- macOS real Word remains incomplete because an unsaved user document prevented the
  required safe full quit/restart. Final installed trust, task-pane navigation, Office.js,
  `WordApi 1.3`, session, health, restart, repair, uninstall, and network capture are not
  proved.
- Windows noninteractive CI remains incomplete because final source is not committed or
  pushed and commit/push authorization was not provided.
- Windows real Word Desktop remains unavailable.

The conditional-closure rule requires complete macOS real Word evidence, passing Windows
runner validation, a final commit, and passing CI against that commit. Those conditions are
not met.

## Smallest concrete remaining set

1. Save or close the active Word document outside this task, then fully quit Word.
2. Run final-origin macOS fresh install and approve the visible per-user trust prompt.
3. Execute the exact production-origin generated-client test and the complete real Word,
   restart, two-repair, uninstall, and sanitized network sequence.
4. Explicitly authorize a baseline/final commit and push, then run all three GitHub jobs
   against that exact revision and resolve any Windows runner defect.
5. Execute the deferred real Windows Word matrix before any beta, release, or cross-platform
   readiness claim.

Phase 2 is not authorized under the conditional-closure exception because Phase 1.5 is
blocked. No roadmap gate was weakened or rewritten.

## Continuation decision — 2026-08-02 EDT

The earlier unsaved-document blocker was cleared and the complete initial macOS host path
was attempted. The current decision remains:

## BLOCKED

Current basis:

- macOS fresh install, trusted localhost TLS, manifest discovery, task-pane opening,
  production Office.js, `Office.onReady()`, Word Desktop/macOS, and `WordApi 1.3` passed.
- The exact-source installed generated client passed bootstrap/session/authenticated
  `/health` outside Word.
- Real Word's bootstrap fetch omitted `Origin` while supplying same-origin/cors/empty Fetch
  Metadata. Exact authority and loopback checks passed first.
- ROADMAP.md requires exact Origin enforcement. The companion correctly returned 403; no
  local session formed and Word did not complete authenticated `/health`.
- Restart and two repair acceptance follow a passing initial Word sequence, so they remain
  blocked. Diagnostic repairs are not substituted.
- Full uninstall passed and removed all active/private state.
- Final source remains uncommitted and unpushed; Windows GitHub-hosted CI has not run against
  it; real Windows Word remains unavailable.

The immediate Phase 1 blocker is no longer “run the Mac test.” It is a confirmed Word
WKWebView/security-contract incompatibility. The smallest next action is a formal Phase 0
security and Office-platform review that either proves a different bootstrap preserving the
exact Origin invariant or explicitly changes that contract and repeats all affected gates.
Silently accepting a missing Origin is prohibited.

Phase 7 distribution work remains separate: signing, notarization, managed deployment,
upgrade/rollback, and certificate lifecycle hardening are not the cause of this Phase 1
failure.
