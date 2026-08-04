# Phase 1.5 closure task

Authorized: **2026-08-02 EDT**

## Objective

Close every Phase 1 feasibility item supported by the available macOS environment and add
honestly limited Windows noninteractive validation. Phase 1.5 must not implement Phase 2.

## Required outcomes

1. Verify normal resolution, trusted HTTPS, the generated client, and the protected session
   at `https://localhost:4179`.
2. Complete the fresh-install through uninstall sequence in real macOS Word Desktop without
   changing or closing unsaved user content.
3. Separate protocol transport, HTTPS bind/certificate, production-origin, real Word,
   Windows runner, and real Windows Word evidence.
4. Add deterministic Windows installer plans, dry-run validation, platform adapter tests,
   and a supported Windows GitHub Actions job.
5. Expand session, request-boundary, cache, redirect, and secret-leakage verification.
6. Verify locked dependencies, deterministic OpenAPI/client output, manifest correctness,
   full-SHA Actions, architecture boundaries, and final artifact hashes.
7. Record Phase 0 owner acceptance and produce the complete Phase 1.5 evidence set.

## Decision rule

- `PASS` requires both real Word Desktop platforms.
- `CONDITIONALLY CLOSED` requires complete macOS real Word evidence, passing Windows runner
  validation, and only real Windows Word acceptance remaining.
- `BLOCKED` applies if macOS real Word, stable origin, deterministic verification, or
  Windows runner validation is incomplete or fails.

The original two-platform Phase 1 exit gate remains unchanged. No runner, direct-SNI probe,
or substituted transport may be reported as real Word evidence.

## Authorization boundary

This task authorizes local Phase 1.5 source, test, installer, workflow, and evidence changes.
It does not independently authorize a commit, push, pull request, tag, release, signing,
notarization, publication, or Phase 2 implementation.
